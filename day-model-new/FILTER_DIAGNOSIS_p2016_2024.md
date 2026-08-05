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
| 300ETF | single | 37 | 17 | `[4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, ... (17 clusters)]` | 0.2366 | 4 | 9 | 24 | 11% | 0.59 |
| 500ETF | single | 205 | 84 | `[15, 12, 7, 6, 6, 5, 5, 5, 5, 5, 4, 4, ... (84 clusters)]` | 0.2425 | 0 | 32 | 173 | 0% | 0.79 |
| 159915ETF | single | 120 | 55 | `[6, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, ... (55 clusters)]` | 0.2889 | 0 | 5 | 115 | 0% | 0.91 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=4, TP=24)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| half_ratio | 1.673 | 1.056 | 1.639 | 0.958 | +2.02 | 1.413 | 96% |
| ic_cv | 0.872 | 0.782 | 0.878 | 0.802 | +1.22 | 0.896 | 89% |
| weak_link_cv | 1.106 | 1.368 | 1.106 | 1.106 | -0.85 | 2.084 | 82% |
| n_negative_years | 0.500 | 1.000 | 0.000 | 1.000 | -0.74 | 1.500 | 82% |
| ic_std_across_regimes | 0.050 | 0.055 | 0.050 | 0.055 | -0.57 | 0.073 | 82% |
| recency_ratio | 4.813 | 1.087 | 4.621 | 3.260 | +0.53 | 7.992 | 82% |
| n_negative_regimes | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 82% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0023, Sharpe=-0.5759)
- Admission: Train IC=+0.2524, Deflated=+0.2527, IR=0.86, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.037 | 2017: +0.040 | 2018: +0.154 | 2019: +0.041 | 2020: +0.015 | 2021: +0.191 | 2022: +0.037 | 2023: +0.200 | 2024: +0.042 | 2025: +0.105 | 2026: -0.208
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.160 | 2017: +0.186 | 2018: +0.475 | 2019: +0.255 | 2020: +0.206 | 2021: +0.326 | 2022: +0.202 | 2023: +0.220 | 2024: +0.125 | 2025: +0.154 | 2026: -0.448
- IC CV=0.82, Neg years (linear/tail)=0/0 of 8, Half ratio=1.74, Recency ratio=3.10
- Early IC=+0.0382, Recent IC=+0.1184, 1st-half IC=+0.0644, 2nd-half IC=+0.1117, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.096, Q3_mid=+0.070, Q4=+0.032, Q5_high_vol=+0.169

**`combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=-0.0131, Sharpe=-0.5701)
- Admission: Train IC=+0.1892, Deflated=+0.1892, IR=0.71, Mono=0.76, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.087 | 2016: +0.065 | 2017: -0.025 | 2018: +0.158 | 2019: +0.063 | 2020: -0.011 | 2021: +0.164 | 2022: +0.069 | 2023: +0.192 | 2024: +0.010 | 2025: +0.095 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.097 | 2017: +0.128 | 2018: +0.352 | 2019: +0.151 | 2020: +0.030 | 2021: +0.404 | 2022: +0.227 | 2023: +0.218 | 2024: +0.175 | 2025: +0.194 | 2026: -0.148
- IC CV=0.90, Neg years (linear/tail)=2/0 of 8, Half ratio=1.54, Recency ratio=6.91
- Early IC=+0.0188, Recent IC=+0.1298, 1st-half IC=+0.0700, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.104, Q3_mid=+0.062, Q4=+0.036, Q5_high_vol=+0.196

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0138, Sharpe=-0.3231)
- Admission: Train IC=+0.2116, Deflated=+0.2119, IR=0.83, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.92, Neg years (linear/tail)=0/0 of 8, Half ratio=1.93, Recency ratio=5.15
- Early IC=+0.0224, Recent IC=+0.1153, 1st-half IC=+0.0549, 2nd-half IC=+0.1063, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.091, Q3_mid=+0.035, Q4=+0.029, Q5_high_vol=+0.178

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0018, Sharpe=+0.1999)
- Admission: Train IC=+0.2395, Deflated=+0.2396, IR=0.78, Mono=0.79, p=0.0000, MaxCorr=0.59
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.055 | 2017: +0.003 | 2018: +0.171 | 2019: +0.049 | 2020: +0.002 | 2021: +0.181 | 2022: +0.049 | 2023: +0.189 | 2024: +0.027 | 2025: +0.112 | 2026: -0.185
- Yearly Tail ICs:   2015: +0.041 | 2016: +0.202 | 2017: +0.144 | 2018: +0.377 | 2019: +0.178 | 2020: +0.068 | 2021: +0.365 | 2022: +0.360 | 2023: +0.364 | 2024: +0.065 | 2025: +0.068 | 2026: +0.020
- IC CV=0.85, Neg years (linear/tail)=0/0 of 8, Half ratio=1.48, Recency ratio=4.09
- Early IC=+0.0292, Recent IC=+0.1194, 1st-half IC=+0.0738, 2nd-half IC=+0.1092, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.107, Q3_mid=+0.062, Q4=+0.041, Q5_high_vol=+0.169

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0383, Sharpe=-0.0697)
- Admission: Train IC=+0.2602, Deflated=+0.2602, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.076 | 2017: -0.020 | 2018: +0.231 | 2019: +0.115 | 2020: +0.047 | 2021: +0.178 | 2022: +0.024 | 2023: +0.145 | 2024: +0.049 | 2025: +0.071 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.113 | 2017: +0.064 | 2018: +0.361 | 2019: +0.337 | 2020: +0.163 | 2021: +0.605 | 2022: +0.198 | 2023: +0.147 | 2024: +0.197 | 2025: -0.088 | 2026: +0.292
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.86, Recency ratio=3.04
- Early IC=+0.0280, Recent IC=+0.0850, 1st-half IC=+0.1133, 2nd-half IC=+0.0971, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.058, Q3_mid=+0.098, Q4=+0.061, Q5_high_vol=+0.219

**`combo_min__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0125, Sharpe=-0.4568)
- Admission: Train IC=+0.2167, Deflated=+0.2162, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.082 | 2016: +0.041 | 2017: +0.013 | 2018: +0.223 | 2019: +0.067 | 2020: -0.005 | 2021: +0.179 | 2022: +0.036 | 2023: +0.173 | 2024: -0.004 | 2025: +0.122 | 2026: -0.141
- Yearly Tail ICs:   2015: +0.021 | 2016: +0.086 | 2017: -0.052 | 2018: +0.218 | 2019: +0.300 | 2020: +0.064 | 2021: +0.472 | 2022: +0.317 | 2023: +0.459 | 2024: -0.102 | 2025: +0.110 | 2026: +0.014
- IC CV=0.90, Neg years (linear/tail)=1/1 of 8, Half ratio=1.06, Recency ratio=3.88
- Early IC=+0.0268, Recent IC=+0.1041, 1st-half IC=+0.0910, 2nd-half IC=+0.0961, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.123, Q3_mid=+0.112, Q4=+0.036, Q5_high_vol=+0.147

**`combo_mean__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0123, Sharpe=-0.4689)
- Admission: Train IC=+0.2003, Deflated=+0.2006, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.075 | 2017: +0.044 | 2018: +0.210 | 2019: +0.072 | 2020: -0.038 | 2021: +0.160 | 2022: +0.063 | 2023: +0.180 | 2024: +0.003 | 2025: +0.107 | 2026: -0.124
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.002 | 2017: +0.171 | 2018: +0.416 | 2019: +0.146 | 2020: -0.022 | 2021: +0.326 | 2022: +0.323 | 2023: +0.412 | 2024: +0.065 | 2025: +0.179 | 2026: -0.062
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=0.86, Recency ratio=2.06
- Early IC=+0.0591, Recent IC=+0.1219, 1st-half IC=+0.1076, 2nd-half IC=+0.0927, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.110, Q3_mid=+0.084, Q4=+0.054, Q5_high_vol=+0.141

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0084, Sharpe=-0.0883)
- Admission: Train IC=+0.2468, Deflated=+0.2470, IR=0.64, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.090 | 2017: +0.022 | 2018: +0.184 | 2019: +0.074 | 2020: -0.002 | 2021: +0.132 | 2022: +0.046 | 2023: +0.172 | 2024: +0.054 | 2025: +0.022 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.099 | 2017: +0.155 | 2018: +0.376 | 2019: +0.260 | 2020: +0.079 | 2021: +0.374 | 2022: +0.167 | 2023: +0.386 | 2024: +0.235 | 2025: -0.045 | 2026: -0.015
- IC CV=0.71, Neg years (linear/tail)=1/0 of 8, Half ratio=0.87, Recency ratio=1.96
- Early IC=+0.0557, Recent IC=+0.1089, 1st-half IC=+0.0990, 2nd-half IC=+0.0858, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.081, Q3_mid=+0.062, Q4=+0.059, Q5_high_vol=+0.168

**`combo_rank_max__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0069, Sharpe=-0.3876)
- Admission: Train IC=+0.1743, Deflated=+0.1744, IR=0.69, Mono=0.73, p=0.0008, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.074 | 2017: +0.071 | 2018: +0.189 | 2019: +0.057 | 2020: -0.032 | 2021: +0.165 | 2022: +0.060 | 2023: +0.183 | 2024: +0.008 | 2025: +0.110 | 2026: -0.148
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.156 | 2017: +0.221 | 2018: +0.426 | 2019: +0.146 | 2020: -0.046 | 2021: +0.354 | 2022: +0.215 | 2023: +0.229 | 2024: +0.145 | 2025: +0.176 | 2026: -0.270
- IC CV=0.76, Neg years (linear/tail)=1/1 of 8, Half ratio=0.92, Recency ratio=1.72
- Early IC=+0.0708, Recent IC=+0.1217, 1st-half IC=+0.1005, 2nd-half IC=+0.0925, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.098, Q3_mid=+0.100, Q4=+0.041, Q5_high_vol=+0.128

**`combo_mean__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0067, Sharpe=-0.2911)
- Admission: Train IC=+0.2419, Deflated=+0.2414, IR=0.75, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.080 | 2017: -0.034 | 2018: +0.160 | 2019: +0.073 | 2020: +0.052 | 2021: +0.175 | 2022: +0.015 | 2023: +0.161 | 2024: +0.063 | 2025: +0.057 | 2026: -0.167
- Yearly Tail ICs:   2015: -0.026 | 2016: +0.171 | 2017: +0.150 | 2018: +0.341 | 2019: +0.360 | 2020: +0.126 | 2021: +0.367 | 2022: +0.210 | 2023: +0.247 | 2024: +0.288 | 2025: -0.129 | 2026: -0.337
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.37, Recency ratio=3.88
- Early IC=+0.0226, Recent IC=+0.0878, 1st-half IC=+0.0731, 2nd-half IC=+0.0999, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.089, Q3_mid=+0.069, Q4=+0.037, Q5_high_vol=+0.195

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0057, Sharpe=-0.2202)
- Admission: Train IC=+0.2566, Deflated=+0.2561, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.066 | 2017: -0.007 | 2018: +0.233 | 2019: +0.068 | 2020: +0.019 | 2021: +0.177 | 2022: +0.034 | 2023: +0.161 | 2024: +0.012 | 2025: +0.099 | 2026: -0.144
- Yearly Tail ICs:   2015: +0.026 | 2016: +0.093 | 2017: +0.180 | 2018: +0.274 | 2019: +0.325 | 2020: +0.177 | 2021: +0.406 | 2022: +0.300 | 2023: +0.395 | 2024: -0.065 | 2025: -0.052 | 2026: -0.174
- IC CV=0.85, Neg years (linear/tail)=1/0 of 8, Half ratio=1.03, Recency ratio=3.29
- Early IC=+0.0297, Recent IC=+0.0977, 1st-half IC=+0.0957, 2nd-half IC=+0.0989, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.112, Q3_mid=+0.106, Q4=+0.053, Q5_high_vol=+0.161

**`combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0045, Sharpe=-0.5240)
- Admission: Train IC=+0.2226, Deflated=+0.2227, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.072 | 2017: +0.064 | 2018: +0.200 | 2019: +0.058 | 2020: -0.012 | 2021: +0.169 | 2022: +0.057 | 2023: +0.180 | 2024: +0.011 | 2025: +0.100 | 2026: -0.151
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.029 | 2017: +0.158 | 2018: +0.512 | 2019: +0.200 | 2020: +0.228 | 2021: +0.345 | 2022: +0.234 | 2023: +0.228 | 2024: +0.108 | 2025: +0.190 | 2026: -0.322
- IC CV=0.71, Neg years (linear/tail)=1/1 of 8, Half ratio=0.94, Recency ratio=1.74
- Early IC=+0.0683, Recent IC=+0.1186, 1st-half IC=+0.1027, 2nd-half IC=+0.0962, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.096, Q3_mid=+0.091, Q4=+0.050, Q5_high_vol=+0.144

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0013, Sharpe=-0.3332)
- Admission: Train IC=+0.2168, Deflated=+0.2168, IR=0.76, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.066 | 2017: -0.027 | 2018: +0.119 | 2019: +0.050 | 2020: +0.019 | 2021: +0.177 | 2022: +0.049 | 2023: +0.194 | 2024: +0.030 | 2025: +0.107 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.109 | 2016: +0.229 | 2017: +0.164 | 2018: +0.308 | 2019: +0.144 | 2020: +0.078 | 2021: +0.306 | 2022: +0.241 | 2023: +0.193 | 2024: +0.189 | 2025: +0.172 | 2026: -0.347
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.95, Recency ratio=6.25
- Early IC=+0.0194, Recent IC=+0.1215, 1st-half IC=+0.0574, 2nd-half IC=+0.1121, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.099, Q3_mid=+0.037, Q4=+0.041, Q5_high_vol=+0.191

### 500ETF — `single` Median Features

**`combo_max__net_volume_flow__max_down_ret`** (Lock IC=+0.0913, Sharpe=-0.1427)
- Admission: Train IC=+0.1624, Deflated=+0.1621, IR=0.55, Mono=0.71, p=0.0020, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.079 | 2017: +0.203 | 2018: +0.168 | 2019: +0.102 | 2020: +0.108 | 2021: +0.072 | 2022: +0.071 | 2023: +0.047 | 2024: +0.143 | 2025: +0.132 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.329 | 2016: +0.146 | 2017: +0.165 | 2018: +0.139 | 2019: +0.177 | 2020: -0.003 | 2021: +0.233 | 2022: +0.224 | 2023: +0.309 | 2024: +0.292 | 2025: +0.041 | 2026: -0.122
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.42
- Early IC=+0.1413, Recent IC=+0.0591, 1st-half IC=+0.1336, 2nd-half IC=+0.0714, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.041, Q3_mid=+0.099, Q4=+0.125, Q5_high_vol=+0.121

**`combo_mean__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0857, Sharpe=-0.2639)
- Admission: Train IC=+0.2240, Deflated=+0.2233, IR=0.80, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.066 | 2017: +0.200 | 2018: +0.167 | 2019: +0.100 | 2020: +0.141 | 2021: +0.114 | 2022: +0.103 | 2023: +0.102 | 2024: +0.144 | 2025: +0.114 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.406 | 2016: +0.275 | 2017: +0.320 | 2018: +0.207 | 2019: +0.228 | 2020: +0.213 | 2021: +0.217 | 2022: +0.257 | 2023: +0.262 | 2024: +0.234 | 2025: +0.002 | 2026: -0.102
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.77
- Early IC=+0.1331, Recent IC=+0.1028, 1st-half IC=+0.1333, 2nd-half IC=+0.1152, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.009, Q3_mid=+0.143, Q4=+0.132, Q5_high_vol=+0.174

**`combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0`** (Lock IC=+0.0852, Sharpe=-0.1000)
- Admission: Train IC=+0.2204, Deflated=+0.2201, IR=0.76, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.094 | 2017: +0.219 | 2018: +0.206 | 2019: +0.115 | 2020: +0.154 | 2021: +0.108 | 2022: +0.048 | 2023: +0.113 | 2024: +0.133 | 2025: +0.116 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.514 | 2016: +0.225 | 2017: +0.294 | 2018: +0.422 | 2019: +0.175 | 2020: +0.162 | 2021: +0.263 | 2022: +0.187 | 2023: +0.227 | 2024: +0.146 | 2025: -0.048 | 2026: -0.255
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.51
- Early IC=+0.1565, Recent IC=+0.0801, 1st-half IC=+0.1541, 2nd-half IC=+0.1020, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.193, Q2=-0.014, Q3_mid=+0.136, Q4=+0.154, Q5_high_vol=+0.167

**`combo_rank_max__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0819, Sharpe=-0.3162)
- Admission: Train IC=+0.1652, Deflated=+0.1641, IR=0.62, Mono=0.72, p=0.0012, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.059 | 2017: +0.231 | 2018: +0.133 | 2019: +0.121 | 2020: +0.130 | 2021: +0.125 | 2022: +0.098 | 2023: +0.097 | 2024: +0.128 | 2025: +0.128 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.324 | 2016: +0.097 | 2017: +0.265 | 2018: +0.250 | 2019: +0.358 | 2020: -0.002 | 2021: +0.246 | 2022: +0.188 | 2023: +0.250 | 2024: +0.326 | 2025: +0.038 | 2026: -0.210
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.67
- Early IC=+0.1450, Recent IC=+0.0975, 1st-half IC=+0.1295, 2nd-half IC=+0.1141, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.003, Q3_mid=+0.119, Q4=+0.129, Q5_high_vol=+0.175

**`combo_mean__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0807, Sharpe=-0.0811)
- Admission: Train IC=+0.2104, Deflated=+0.2099, IR=0.56, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.092 | 2017: +0.204 | 2018: +0.174 | 2019: +0.135 | 2020: +0.097 | 2021: +0.130 | 2022: +0.074 | 2023: +0.094 | 2024: +0.107 | 2025: +0.155 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.209 | 2016: +0.064 | 2017: +0.169 | 2018: +0.389 | 2019: +0.280 | 2020: +0.016 | 2021: +0.278 | 2022: +0.290 | 2023: +0.303 | 2024: +0.192 | 2025: +0.125 | 2026: -0.349
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.57
- Early IC=+0.1482, Recent IC=+0.0841, 1st-half IC=+0.1482, 2nd-half IC=+0.0980, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.206, Q2=-0.022, Q3_mid=+0.116, Q4=+0.148, Q5_high_vol=+0.150

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.0802, Sharpe=-0.1927)
- Admission: Train IC=+0.2180, Deflated=+0.2185, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.136 | 2017: +0.164 | 2018: +0.241 | 2019: +0.127 | 2020: +0.103 | 2021: +0.160 | 2022: +0.084 | 2023: +0.085 | 2024: +0.149 | 2025: +0.095 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.178 | 2017: +0.330 | 2018: +0.462 | 2019: +0.156 | 2020: +0.269 | 2021: +0.336 | 2022: +0.144 | 2023: +0.096 | 2024: +0.269 | 2025: -0.069 | 2026: -0.338
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.56
- Early IC=+0.1504, Recent IC=+0.0846, 1st-half IC=+0.1603, 2nd-half IC=+0.1085, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.015, Q3_mid=+0.100, Q4=+0.153, Q5_high_vol=+0.218

**`combo_mean__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0798, Sharpe=-0.0579)
- Admission: Train IC=+0.1797, Deflated=+0.1783, IR=0.56, Mono=0.72, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.032 | 2017: +0.214 | 2018: +0.130 | 2019: +0.113 | 2020: +0.096 | 2021: +0.084 | 2022: +0.073 | 2023: +0.087 | 2024: +0.116 | 2025: +0.124 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.256 | 2016: +0.143 | 2017: +0.228 | 2018: +0.198 | 2019: +0.247 | 2020: +0.089 | 2021: +0.280 | 2022: +0.238 | 2023: +0.295 | 2024: +0.201 | 2025: +0.122 | 2026: -0.283
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.65
- Early IC=+0.1232, Recent IC=+0.0797, 1st-half IC=+0.1150, 2nd-half IC=+0.0832, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.026, Q3_mid=+0.111, Q4=+0.087, Q5_high_vol=+0.134

**`combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0794, Sharpe=-0.3704)
- Admission: Train IC=+0.1779, Deflated=+0.1766, IR=0.47, Mono=0.67, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.098 | 2017: +0.162 | 2018: +0.087 | 2019: +0.080 | 2020: +0.102 | 2021: +0.048 | 2022: +0.068 | 2023: +0.087 | 2024: +0.122 | 2025: +0.100 | 2026: -0.041
- Yearly Tail ICs:   2015: +0.544 | 2016: +0.132 | 2017: +0.220 | 2018: +0.133 | 2019: +0.154 | 2020: +0.247 | 2021: +0.275 | 2022: +0.129 | 2023: +0.323 | 2024: +0.071 | 2025: +0.054 | 2026: -0.060
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.60
- Early IC=+0.1298, Recent IC=+0.0779, 1st-half IC=+0.1067, 2nd-half IC=+0.0732, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.047, Q3_mid=+0.126, Q4=+0.092, Q5_high_vol=+0.089

**`combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance`** (Lock IC=+0.0793, Sharpe=-0.5241)
- Admission: Train IC=+0.2356, Deflated=+0.2347, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.012 | 2017: +0.194 | 2018: +0.167 | 2019: +0.143 | 2020: +0.116 | 2021: +0.145 | 2022: +0.114 | 2023: +0.092 | 2024: +0.141 | 2025: +0.107 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.390 | 2016: +0.094 | 2017: +0.191 | 2018: +0.283 | 2019: +0.427 | 2020: +0.108 | 2021: +0.317 | 2022: +0.341 | 2023: +0.223 | 2024: +0.376 | 2025: -0.048 | 2026: -0.214
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=1.00
- Early IC=+0.1031, Recent IC=+0.1034, 1st-half IC=+0.1326, 2nd-half IC=+0.1173, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.015, Q3_mid=+0.127, Q4=+0.137, Q5_high_vol=+0.173

**`combo_mean__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0781, Sharpe=-0.2958)
- Admission: Train IC=+0.2011, Deflated=+0.1998, IR=0.77, Mono=0.78, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.043 | 2017: +0.221 | 2018: +0.143 | 2019: +0.121 | 2020: +0.133 | 2021: +0.128 | 2022: +0.082 | 2023: +0.112 | 2024: +0.124 | 2025: +0.119 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.251 | 2016: +0.113 | 2017: +0.195 | 2018: +0.314 | 2019: +0.307 | 2020: +0.097 | 2021: +0.292 | 2022: +0.211 | 2023: +0.266 | 2024: +0.318 | 2025: +0.028 | 2026: -0.275
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.74
- Early IC=+0.1320, Recent IC=+0.0973, 1st-half IC=+0.1279, 2nd-half IC=+0.1157, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.004, Q3_mid=+0.135, Q4=+0.110, Q5_high_vol=+0.174

**`combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0`** (Lock IC=+0.0776, Sharpe=-0.1178)
- Admission: Train IC=+0.1739, Deflated=+0.1748, IR=0.59, Mono=0.70, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.081 | 2017: +0.233 | 2018: +0.163 | 2019: +0.074 | 2020: +0.106 | 2021: +0.071 | 2022: +0.102 | 2023: +0.063 | 2024: +0.129 | 2025: +0.104 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.288 | 2016: -0.021 | 2017: +0.298 | 2018: +0.079 | 2019: +0.123 | 2020: +0.206 | 2021: +0.239 | 2022: +0.194 | 2023: +0.279 | 2024: +0.247 | 2025: +0.069 | 2026: -0.238
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.70, Recency ratio=0.52
- Early IC=+0.1571, Recent IC=+0.0823, 1st-half IC=+0.1304, 2nd-half IC=+0.0913, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.043, Q3_mid=+0.109, Q4=+0.134, Q5_high_vol=+0.126

**`combo_max__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0760, Sharpe=-0.5936)
- Admission: Train IC=+0.1982, Deflated=+0.1981, IR=0.67, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.107 | 2017: +0.149 | 2018: +0.176 | 2019: +0.120 | 2020: +0.106 | 2021: +0.143 | 2022: +0.095 | 2023: +0.088 | 2024: +0.107 | 2025: +0.143 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.315 | 2016: -0.012 | 2017: +0.106 | 2018: +0.326 | 2019: +0.318 | 2020: +0.031 | 2021: +0.248 | 2022: +0.175 | 2023: +0.301 | 2024: +0.177 | 2025: +0.019 | 2026: -0.441
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.71
- Early IC=+0.1282, Recent IC=+0.0917, 1st-half IC=+0.1366, 2nd-half IC=+0.1115, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.008, Q3_mid=+0.124, Q4=+0.120, Q5_high_vol=+0.171

**`combo_rank_max__net_volume_flow__vwap_close_divergence_trend`** (Lock IC=+0.0731, Sharpe=-0.3285)
- Admission: Train IC=+0.1796, Deflated=+0.1788, IR=0.57, Mono=0.71, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.041 | 2017: +0.166 | 2018: +0.097 | 2019: +0.086 | 2020: +0.085 | 2021: +0.084 | 2022: +0.105 | 2023: +0.097 | 2024: +0.115 | 2025: +0.150 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.056 | 2017: +0.189 | 2018: +0.190 | 2019: +0.263 | 2020: +0.091 | 2021: +0.253 | 2022: +0.184 | 2023: +0.274 | 2024: +0.282 | 2025: +0.071 | 2026: -0.179
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=0.99
- Early IC=+0.1037, Recent IC=+0.1025, 1st-half IC=+0.0920, 2nd-half IC=+0.0988, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.018, Q3_mid=+0.099, Q4=+0.078, Q5_high_vol=+0.127

**`combo_min__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0721, Sharpe=-0.1601)
- Admission: Train IC=+0.2025, Deflated=+0.2013, IR=0.56, Mono=0.69, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.147 | 2016: +0.033 | 2017: +0.204 | 2018: +0.090 | 2019: +0.093 | 2020: +0.091 | 2021: +0.123 | 2022: +0.084 | 2023: +0.090 | 2024: +0.118 | 2025: +0.134 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.096 | 2017: +0.195 | 2018: +0.318 | 2019: +0.264 | 2020: +0.121 | 2021: +0.285 | 2022: +0.180 | 2023: +0.253 | 2024: +0.146 | 2025: +0.168 | 2026: -0.382
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=0.73
- Early IC=+0.1185, Recent IC=+0.0870, 1st-half IC=+0.0897, 2nd-half IC=+0.1019, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.183, Q2=-0.014, Q3_mid=+0.103, Q4=+0.102, Q5_high_vol=+0.136

**`vwap_trend_channel_slope`** (Lock IC=+0.0712, Sharpe=-0.3626)
- Admission: Train IC=+0.1436, Deflated=+0.1423, IR=0.46, Mono=0.65, p=0.0058, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.90
- Early IC=+0.1028, Recent IC=+0.0926, 1st-half IC=+0.0798, 2nd-half IC=+0.0888, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.007, Q3_mid=+0.088, Q4=+0.063, Q5_high_vol=+0.120

**`combo_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0704, Sharpe=-0.1210)
- Admission: Train IC=+0.1896, Deflated=+0.1896, IR=0.72, Mono=0.75, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.108 | 2017: +0.200 | 2018: +0.172 | 2019: +0.103 | 2020: +0.132 | 2021: +0.092 | 2022: +0.124 | 2023: +0.126 | 2024: +0.131 | 2025: +0.094 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.238 | 2016: +0.187 | 2017: +0.167 | 2018: +0.307 | 2019: +0.193 | 2020: +0.094 | 2021: +0.195 | 2022: +0.118 | 2023: +0.409 | 2024: +0.213 | 2025: -0.163 | 2026: -0.481
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.81
- Early IC=+0.1540, Recent IC=+0.1251, 1st-half IC=+0.1315, 2nd-half IC=+0.1293, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.027, Q3_mid=+0.118, Q4=+0.090, Q5_high_vol=+0.207

**`combo_max__volatility_expansion_trend_vector__vwap_close_divergence_trend`** (Lock IC=+0.0700, Sharpe=-0.1626)
- Admission: Train IC=+0.1775, Deflated=+0.1768, IR=0.47, Mono=0.66, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.128 | 2016: +0.042 | 2017: +0.207 | 2018: +0.102 | 2019: +0.095 | 2020: +0.086 | 2021: +0.063 | 2022: +0.088 | 2023: +0.089 | 2024: +0.109 | 2025: +0.146 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.095 | 2017: +0.250 | 2018: +0.303 | 2019: +0.261 | 2020: -0.009 | 2021: +0.254 | 2022: +0.130 | 2023: +0.179 | 2024: +0.263 | 2025: +0.052 | 2026: -0.286
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.71
- Early IC=+0.1244, Recent IC=+0.0886, 1st-half IC=+0.1053, 2nd-half IC=+0.0862, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.021, Q3_mid=+0.096, Q4=+0.076, Q5_high_vol=+0.141

**`combo_rel_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0684, Sharpe=-0.4386)
- Admission: Train IC=+0.2365, Deflated=+0.2371, IR=0.85, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.331 | 2016: +0.118 | 2017: +0.179 | 2018: +0.204 | 2019: +0.128 | 2020: +0.123 | 2021: +0.137 | 2022: +0.042 | 2023: +0.077 | 2024: +0.087 | 2025: +0.022 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.081 | 2017: +0.414 | 2018: +0.371 | 2019: +0.380 | 2020: +0.089 | 2021: +0.234 | 2022: +0.117 | 2023: +0.170 | 2024: -0.063 | 2025: -0.052 | 2026: +0.019
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.40
- Early IC=+0.1482, Recent IC=+0.0594, 1st-half IC=+0.1500, 2nd-half IC=+0.0942, Neg regimes=1/5
- Weak component: `early_late_momentum_divergence` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.028, Q3_mid=+0.061, Q4=+0.163, Q5_high_vol=+0.197

**`combo_rel_diff__first_bar_return__h2_l2_pullback_continuation`** (Lock IC=+0.0669, Sharpe=-0.3064)
- Admission: Train IC=+0.1851, Deflated=+0.1845, IR=0.56, Mono=0.72, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.097 | 2017: +0.151 | 2018: +0.152 | 2019: +0.111 | 2020: +0.092 | 2021: +0.076 | 2022: +0.094 | 2023: +0.078 | 2024: +0.115 | 2025: +0.126 | 2026: -0.105
- Yearly Tail ICs:   2015: +0.389 | 2016: +0.004 | 2017: +0.040 | 2018: +0.334 | 2019: +0.196 | 2020: +0.082 | 2021: +0.150 | 2022: +0.246 | 2023: +0.311 | 2024: +0.276 | 2025: +0.030 | 2026: -0.506
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.70
- Early IC=+0.1239, Recent IC=+0.0862, 1st-half IC=+0.1262, 2nd-half IC=+0.0891, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.222, Q2=-0.060, Q3_mid=+0.133, Q4=+0.142, Q5_high_vol=+0.109

**`combo_mean__early_order_flow_imbalance__bar_body_rng_0`** (Lock IC=+0.0668, Sharpe=-0.1367)
- Admission: Train IC=+0.2558, Deflated=+0.2559, IR=0.66, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.040 | 2017: +0.162 | 2018: +0.178 | 2019: +0.139 | 2020: +0.065 | 2021: +0.133 | 2022: +0.107 | 2023: +0.077 | 2024: +0.119 | 2025: +0.105 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.053 | 2017: +0.065 | 2018: +0.370 | 2019: +0.319 | 2020: +0.115 | 2021: +0.303 | 2022: +0.351 | 2023: +0.384 | 2024: +0.355 | 2025: +0.040 | 2026: -0.127
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.92
- Early IC=+0.1006, Recent IC=+0.0922, 1st-half IC=+0.1330, 2nd-half IC=+0.0939, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.164, Q2=-0.001, Q3_mid=+0.094, Q4=+0.166, Q5_high_vol=+0.130

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0668, Sharpe=-0.1367)
- Admission: Train IC=+0.1967, Deflated=+0.1957, IR=0.45, Mono=0.67, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.032 | 2017: +0.181 | 2018: +0.191 | 2019: +0.121 | 2020: +0.172 | 2021: +0.149 | 2022: +0.101 | 2023: +0.083 | 2024: +0.120 | 2025: +0.096 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.005 | 2016: +0.132 | 2017: +0.257 | 2018: +0.474 | 2019: +0.214 | 2020: +0.178 | 2021: +0.253 | 2022: +0.053 | 2023: +0.137 | 2024: +0.134 | 2025: -0.103 | 2026: -0.359
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.86
- Early IC=+0.1063, Recent IC=+0.0919, 1st-half IC=+0.1270, 2nd-half IC=+0.1340, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.012, Q3_mid=+0.181, Q4=+0.131, Q5_high_vol=+0.188

**`combo_max__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0644, Sharpe=-0.4181)
- Admission: Train IC=+0.1886, Deflated=+0.1888, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.112 | 2017: +0.171 | 2018: +0.195 | 2019: +0.101 | 2020: +0.109 | 2021: +0.158 | 2022: +0.111 | 2023: +0.118 | 2024: +0.123 | 2025: +0.130 | 2026: -0.108
- Yearly Tail ICs:   2015: +0.263 | 2016: -0.052 | 2017: +0.109 | 2018: +0.317 | 2019: +0.229 | 2020: +0.182 | 2021: +0.194 | 2022: +0.194 | 2023: +0.414 | 2024: +0.118 | 2025: -0.084 | 2026: -0.563
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=0.98, Recency ratio=0.81
- Early IC=+0.1417, Recent IC=+0.1146, 1st-half IC=+0.1306, 2nd-half IC=+0.1276, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.022, Q3_mid=+0.139, Q4=+0.113, Q5_high_vol=+0.176

**`combo_rank_max__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0639, Sharpe=-0.3337)
- Admission: Train IC=+0.1924, Deflated=+0.1927, IR=0.65, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.114 | 2017: +0.179 | 2018: +0.194 | 2019: +0.102 | 2020: +0.110 | 2021: +0.153 | 2022: +0.110 | 2023: +0.122 | 2024: +0.124 | 2025: +0.132 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.258 | 2016: -0.034 | 2017: +0.134 | 2018: +0.351 | 2019: +0.208 | 2020: +0.214 | 2021: +0.196 | 2022: +0.233 | 2023: +0.407 | 2024: +0.103 | 2025: -0.061 | 2026: -0.476
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=0.96, Recency ratio=0.79
- Early IC=+0.1456, Recent IC=+0.1156, 1st-half IC=+0.1324, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.024, Q3_mid=+0.138, Q4=+0.110, Q5_high_vol=+0.175

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0586, Sharpe=-0.0789)
- Admission: Train IC=+0.2446, Deflated=+0.2452, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.125 | 2017: +0.154 | 2018: +0.226 | 2019: +0.083 | 2020: +0.134 | 2021: +0.102 | 2022: +0.108 | 2023: +0.080 | 2024: +0.126 | 2025: +0.122 | 2026: -0.123
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.099 | 2017: +0.215 | 2018: +0.264 | 2019: +0.075 | 2020: +0.348 | 2021: +0.179 | 2022: +0.303 | 2023: +0.395 | 2024: +0.216 | 2025: -0.102 | 2026: -0.544
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.67
- Early IC=+0.1414, Recent IC=+0.0945, 1st-half IC=+0.1449, 2nd-half IC=+0.1071, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.012, Q3_mid=+0.126, Q4=+0.163, Q5_high_vol=+0.157

**`combo_max__early_body_momentum__first_bar_return`** (Lock IC=+0.0580, Sharpe=-0.3703)
- Admission: Train IC=+0.2327, Deflated=+0.2333, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.108 | 2017: +0.152 | 2018: +0.225 | 2019: +0.084 | 2020: +0.127 | 2021: +0.096 | 2022: +0.109 | 2023: +0.070 | 2024: +0.117 | 2025: +0.126 | 2026: -0.120
- Yearly Tail ICs:   2015: +0.118 | 2016: +0.110 | 2017: +0.197 | 2018: +0.273 | 2019: +0.103 | 2020: +0.346 | 2021: +0.202 | 2022: +0.241 | 2023: +0.409 | 2024: +0.182 | 2025: -0.123 | 2026: -0.557
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.69
- Early IC=+0.1299, Recent IC=+0.0894, 1st-half IC=+0.1394, 2nd-half IC=+0.1032, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.013, Q3_mid=+0.122, Q4=+0.157, Q5_high_vol=+0.152

**`combo_min__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0573, Sharpe=-0.3285)
- Admission: Train IC=+0.2122, Deflated=+0.2124, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.026 | 2017: +0.169 | 2018: +0.124 | 2019: +0.142 | 2020: +0.080 | 2021: +0.199 | 2022: +0.144 | 2023: +0.108 | 2024: +0.136 | 2025: +0.094 | 2026: -0.125
- Yearly Tail ICs:   2015: +0.206 | 2016: +0.066 | 2017: +0.299 | 2018: +0.326 | 2019: +0.312 | 2020: +0.032 | 2021: +0.230 | 2022: +0.287 | 2023: +0.195 | 2024: +0.355 | 2025: +0.014 | 2026: -0.246
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.29
- Early IC=+0.0976, Recent IC=+0.1263, 1st-half IC=+0.1082, 2nd-half IC=+0.1334, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.034, Q3_mid=+0.119, Q4=+0.129, Q5_high_vol=+0.149

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0540, Sharpe=-0.2136)
- Admission: Train IC=+0.1886, Deflated=+0.1880, IR=0.51, Mono=0.67, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.087 | 2017: +0.207 | 2018: +0.148 | 2019: +0.106 | 2020: +0.167 | 2021: +0.053 | 2022: +0.113 | 2023: +0.130 | 2024: +0.095 | 2025: +0.086 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.386 | 2016: +0.147 | 2017: +0.347 | 2018: +0.235 | 2019: +0.179 | 2020: +0.141 | 2021: +0.176 | 2022: +0.055 | 2023: +0.102 | 2024: +0.232 | 2025: -0.029 | 2026: +0.006
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.83
- Early IC=+0.1467, Recent IC=+0.1215, 1st-half IC=+0.1354, 2nd-half IC=+0.1186, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.182, Q2=-0.001, Q3_mid=+0.157, Q4=+0.124, Q5_high_vol=+0.160

**`combo_rank_max__early_body_momentum__early_order_flow_imbalance`** (Lock IC=+0.0530, Sharpe=-0.1975)
- Admission: Train IC=+0.2101, Deflated=+0.2092, IR=0.61, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.120 | 2016: +0.009 | 2017: +0.102 | 2018: +0.093 | 2019: +0.096 | 2020: +0.065 | 2021: +0.082 | 2022: +0.141 | 2023: +0.067 | 2024: +0.107 | 2025: +0.128 | 2026: -0.131
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.021 | 2017: +0.152 | 2018: +0.137 | 2019: +0.250 | 2020: +0.200 | 2021: +0.220 | 2022: +0.388 | 2023: +0.163 | 2024: +0.330 | 2025: +0.070 | 2026: -0.131
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.85
- Early IC=+0.0562, Recent IC=+0.1038, 1st-half IC=+0.0781, 2nd-half IC=+0.0880, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.128, Q2=-0.006, Q3_mid=+0.087, Q4=+0.113, Q5_high_vol=+0.108

**`combo_rank_max__first_bar_return__early_order_flow_imbalance`** (Lock IC=+0.0480, Sharpe=-0.5454)
- Admission: Train IC=+0.2115, Deflated=+0.2117, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.067 | 2017: +0.131 | 2018: +0.204 | 2019: +0.119 | 2020: +0.070 | 2021: +0.092 | 2022: +0.092 | 2023: +0.081 | 2024: +0.107 | 2025: +0.095 | 2026: -0.124
- Yearly Tail ICs:   2015: +0.178 | 2016: -0.101 | 2017: +0.051 | 2018: +0.344 | 2019: +0.176 | 2020: +0.162 | 2021: +0.294 | 2022: +0.229 | 2023: +0.374 | 2024: +0.250 | 2025: -0.089 | 2026: -0.454
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.84
- Early IC=+0.1030, Recent IC=+0.0865, 1st-half IC=+0.1346, 2nd-half IC=+0.0869, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.152, Q2=-0.002, Q3_mid=+0.098, Q4=+0.145, Q5_high_vol=+0.136

**`combo_max__first_bar_return__early_order_flow_imbalance`** (Lock IC=+0.0459, Sharpe=-0.4898)
- Admission: Train IC=+0.2063, Deflated=+0.2063, IR=0.50, Mono=0.71, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.062 | 2017: +0.124 | 2018: +0.204 | 2019: +0.115 | 2020: +0.069 | 2021: +0.083 | 2022: +0.097 | 2023: +0.077 | 2024: +0.106 | 2025: +0.091 | 2026: -0.119
- Yearly Tail ICs:   2015: +0.189 | 2016: -0.058 | 2017: +0.048 | 2018: +0.378 | 2019: +0.185 | 2020: +0.204 | 2021: +0.337 | 2022: +0.220 | 2023: +0.333 | 2024: +0.201 | 2025: -0.093 | 2026: -0.470
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.94
- Early IC=+0.0926, Recent IC=+0.0869, 1st-half IC=+0.1287, 2nd-half IC=+0.0830, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.150, Q2=-0.008, Q3_mid=+0.089, Q4=+0.138, Q5_high_vol=+0.137

**`combo_sig_product__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0370, Sharpe=-0.1907)
- Admission: Train IC=+0.2091, Deflated=+0.2092, IR=0.59, Mono=0.67, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.131 | 2017: +0.165 | 2018: +0.202 | 2019: +0.140 | 2020: +0.089 | 2021: +0.007 | 2022: +0.096 | 2023: +0.097 | 2024: +0.091 | 2025: +0.039 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.250 | 2017: +0.164 | 2018: +0.319 | 2019: +0.310 | 2020: +0.059 | 2021: +0.254 | 2022: +0.038 | 2023: +0.364 | 2024: +0.313 | 2025: -0.102 | 2026: -0.112
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.65
- Early IC=+0.1480, Recent IC=+0.0963, 1st-half IC=+0.1528, 2nd-half IC=+0.0814, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.174, Q2=-0.010, Q3_mid=+0.077, Q4=+0.090, Q5_high_vol=+0.212

**`combo_sig_product__first_bar_return__vwap_close_divergence_trend`** (Lock IC=+0.0244, Sharpe=-0.5970)
- Admission: Train IC=+0.1948, Deflated=+0.1955, IR=0.59, Mono=0.73, p=0.0002, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.095 | 2017: +0.067 | 2018: +0.194 | 2019: +0.179 | 2020: +0.100 | 2021: +0.071 | 2022: +0.137 | 2023: +0.117 | 2024: +0.073 | 2025: +0.068 | 2026: -0.104
- Yearly Tail ICs:   2015: +0.276 | 2016: +0.127 | 2017: -0.032 | 2018: +0.295 | 2019: +0.356 | 2020: +0.053 | 2021: +0.075 | 2022: +0.263 | 2023: +0.271 | 2024: +0.229 | 2025: -0.112 | 2026: +0.010
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.80, Recency ratio=1.56
- Early IC=+0.0811, Recent IC=+0.1269, 1st-half IC=+0.1340, 2nd-half IC=+0.1078, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.013, Q3_mid=+0.110, Q4=+0.173, Q5_high_vol=+0.149

### 159915ETF — `single` Median Features

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1316, Sharpe=-0.2817)
- Admission: Train IC=+0.1802, Deflated=+0.1801, IR=0.45, Mono=0.68, p=0.0010, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.036 | 2017: -0.003 | 2018: +0.096 | 2019: +0.182 | 2020: +0.119 | 2021: +0.142 | 2022: +0.151 | 2023: +0.104 | 2024: +0.087 | 2025: +0.165 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.102 | 2016: +0.069 | 2017: +0.087 | 2018: +0.192 | 2019: +0.331 | 2020: +0.174 | 2021: +0.189 | 2022: +0.123 | 2023: +0.112 | 2024: -0.099 | 2025: +0.457 | 2026: +0.361
- IC CV=0.55, Neg years (linear/tail)=1/0 of 8, Half ratio=1.76, Recency ratio=7.89
- Early IC=+0.0162, Recent IC=+0.1275, 1st-half IC=+0.0817, 2nd-half IC=+0.1442, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.141, Q3_mid=+0.080, Q4=+0.116, Q5_high_vol=+0.152

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0922, Sharpe=-0.0879)
- Admission: Train IC=+0.2568, Deflated=+0.2560, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.105 | 2017: +0.006 | 2018: +0.129 | 2019: +0.198 | 2020: +0.115 | 2021: +0.134 | 2022: +0.106 | 2023: +0.200 | 2024: +0.078 | 2025: +0.167 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.373 | 2016: -0.016 | 2017: +0.072 | 2018: +0.330 | 2019: +0.449 | 2020: +0.204 | 2021: +0.343 | 2022: +0.207 | 2023: +0.598 | 2024: +0.145 | 2025: +0.217 | 2026: +0.008
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=1.26, Recency ratio=2.77
- Early IC=+0.0552, Recent IC=+0.1527, 1st-half IC=+0.1075, 2nd-half IC=+0.1354, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.069, Q2=+0.152, Q3_mid=+0.099, Q4=+0.113, Q5_high_vol=+0.162

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0683, Sharpe=-0.2283)
- Admission: Train IC=+0.1881, Deflated=+0.1870, IR=0.61, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.013 | 2017: +0.054 | 2018: +0.086 | 2019: +0.172 | 2020: +0.101 | 2021: +0.172 | 2022: +0.099 | 2023: +0.193 | 2024: +0.041 | 2025: +0.177 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.186 | 2016: +0.055 | 2017: +0.166 | 2018: +0.096 | 2019: +0.113 | 2020: +0.281 | 2021: +0.152 | 2022: +0.287 | 2023: +0.381 | 2024: -0.011 | 2025: +0.123 | 2026: -0.253
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.81, Recency ratio=4.38
- Early IC=+0.0333, Recent IC=+0.1458, 1st-half IC=+0.0767, 2nd-half IC=+0.1392, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.137, Q3_mid=+0.130, Q4=+0.102, Q5_high_vol=+0.140

**`combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0677, Sharpe=-0.1117)
- Admission: Train IC=+0.2096, Deflated=+0.2089, IR=0.65, Mono=0.72, p=0.0002, MaxCorr=0.67
- Yearly Linear ICs: 2015: +0.072 | 2016: +0.055 | 2017: +0.020 | 2018: +0.035 | 2019: +0.139 | 2020: +0.033 | 2021: +0.160 | 2022: +0.086 | 2023: +0.142 | 2024: +0.096 | 2025: +0.111 | 2026: -0.055
- Yearly Tail ICs:   2015: -0.014 | 2016: +0.181 | 2017: +0.163 | 2018: +0.002 | 2019: +0.316 | 2020: +0.279 | 2021: +0.072 | 2022: +0.359 | 2023: +0.334 | 2024: +0.215 | 2025: +0.153 | 2026: -0.269
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=1.66, Recency ratio=3.03
- Early IC=+0.0375, Recent IC=+0.1138, 1st-half IC=+0.0649, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.132, Q3_mid=+0.124, Q4=+0.101, Q5_high_vol=+0.058

**`combo_ifelse__gap_pct__yesterday_early_momentum__bar_body_rng_0`** (Lock IC=+0.0174, Sharpe=-0.0890)
- Admission: Train IC=+0.1644, Deflated=+0.1660, IR=0.34, Mono=0.65, p=0.0022, MaxCorr=0.54
- Yearly Linear ICs: 2015: +0.137 | 2016: +0.158 | 2017: -0.090 | 2018: +0.119 | 2019: +0.061 | 2020: +0.155 | 2021: +0.091 | 2022: +0.116 | 2023: +0.191 | 2024: -0.045 | 2025: +0.073 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.144 | 2016: +0.010 | 2017: -0.170 | 2018: +0.210 | 2019: +0.281 | 2020: +0.185 | 2021: +0.255 | 2022: +0.083 | 2023: +0.206 | 2024: -0.071 | 2025: +0.158 | 2026: -0.093
- IC CV=0.81, Neg years (linear/tail)=1/1 of 8, Half ratio=1.97, Recency ratio=4.52
- Early IC=+0.0340, Recent IC=+0.1536, 1st-half IC=+0.0686, 2nd-half IC=+0.1348, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.118, Q3_mid=+0.046, Q4=+0.071, Q5_high_vol=+0.180

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0334, Sharpe=+0.9753)
- Admission: Train IC=+0.2155, Deflated=+0.2160, IR=0.44, Mono=0.65, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.115 | 2017: -0.058 | 2018: +0.142 | 2019: +0.102 | 2020: +0.073 | 2021: +0.138 | 2022: +0.040 | 2023: +0.132 | 2024: +0.053 | 2025: +0.050 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.400 | 2016: +0.169 | 2017: -0.034 | 2018: +0.304 | 2019: +0.334 | 2020: +0.176 | 2021: +0.340 | 2022: +0.244 | 2023: +0.137 | 2024: +0.410 | 2025: +0.062 | 2026: +0.135
- IC CV=0.74, Neg years (linear/tail)=1/1 of 8, Half ratio=1.18, Recency ratio=3.01
- Early IC=+0.0286, Recent IC=+0.0860, 1st-half IC=+0.0818, 2nd-half IC=+0.0962, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.055, Q3_mid=+0.083, Q4=+0.023, Q5_high_vol=+0.196

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0655, Sharpe=+0.9697)
- Admission: Train IC=+0.2082, Deflated=+0.2081, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=0.80, Recency ratio=8.68
- Early IC=+0.0095, Recent IC=+0.0825, 1st-half IC=+0.0963, 2nd-half IC=+0.0772, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.043, Q3_mid=+0.074, Q4=+0.041, Q5_high_vol=+0.181

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0311, Sharpe=+0.7153)
- Admission: Train IC=+0.2033, Deflated=+0.2027, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.090 | 2017: -0.061 | 2018: +0.193 | 2019: +0.085 | 2020: +0.067 | 2021: +0.163 | 2022: +0.063 | 2023: +0.126 | 2024: +0.043 | 2025: +0.068 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.140 | 2017: +0.062 | 2018: +0.422 | 2019: +0.262 | 2020: +0.136 | 2021: +0.248 | 2022: +0.198 | 2023: +0.124 | 2024: +0.194 | 2025: +0.209 | 2026: +0.145
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=1.21, Recency ratio=6.50
- Early IC=+0.0145, Recent IC=+0.0943, 1st-half IC=+0.0876, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.078, Q3_mid=+0.067, Q4=+0.049, Q5_high_vol=+0.233

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0572, Sharpe=+0.6639)
- Admission: Train IC=+0.1812, Deflated=+0.1812, IR=0.50, Mono=0.68, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.062 | 2017: -0.040 | 2018: +0.162 | 2019: +0.137 | 2020: +0.018 | 2021: +0.125 | 2022: +0.028 | 2023: +0.138 | 2024: +0.029 | 2025: +0.098 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.063 | 2017: -0.116 | 2018: +0.316 | 2019: +0.221 | 2020: +0.182 | 2021: +0.260 | 2022: +0.151 | 2023: +0.231 | 2024: +0.255 | 2025: +0.090 | 2026: +0.262
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=0.74, Recency ratio=7.30
- Early IC=+0.0114, Recent IC=+0.0830, 1st-half IC=+0.0993, 2nd-half IC=+0.0738, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.043, Q3_mid=+0.077, Q4=+0.040, Q5_high_vol=+0.173

**`combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0377, Sharpe=+0.6416)
- Admission: Train IC=+0.1773, Deflated=+0.1770, IR=0.51, Mono=0.68, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.066 | 2017: -0.045 | 2018: +0.197 | 2019: +0.126 | 2020: +0.046 | 2021: +0.137 | 2022: +0.039 | 2023: +0.115 | 2024: +0.031 | 2025: +0.085 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.374 | 2016: +0.005 | 2017: -0.093 | 2018: +0.248 | 2019: +0.303 | 2020: +0.127 | 2021: +0.385 | 2022: +0.263 | 2023: +0.062 | 2024: +0.236 | 2025: +0.049 | 2026: +0.283
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=0.81, Recency ratio=7.29
- Early IC=+0.0106, Recent IC=+0.0771, 1st-half IC=+0.1009, 2nd-half IC=+0.0819, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.042, Q3_mid=+0.087, Q4=+0.056, Q5_high_vol=+0.196

**`combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0362, Sharpe=+0.6343)
- Admission: Train IC=+0.1857, Deflated=+0.1856, IR=0.51, Mono=0.69, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.107 | 2017: -0.024 | 2018: +0.224 | 2019: +0.103 | 2020: +0.051 | 2021: +0.160 | 2022: +0.069 | 2023: +0.121 | 2024: +0.029 | 2025: +0.072 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.122 | 2016: +0.140 | 2017: -0.090 | 2018: +0.383 | 2019: +0.285 | 2020: +0.118 | 2021: +0.369 | 2022: +0.200 | 2023: +0.123 | 2024: +0.165 | 2025: +0.248 | 2026: +0.106
- IC CV=0.68, Neg years (linear/tail)=1/1 of 8, Half ratio=0.87, Recency ratio=2.26
- Early IC=+0.0420, Recent IC=+0.0948, 1st-half IC=+0.1152, 2nd-half IC=+0.0997, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.077, Q3_mid=+0.077, Q4=+0.056, Q5_high_vol=+0.230

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0512, Sharpe=+0.6322)
- Admission: Train IC=+0.2502, Deflated=+0.2509, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.77, Neg years (linear/tail)=1/0 of 8, Half ratio=0.86, Recency ratio=5.39
- Early IC=+0.0203, Recent IC=+0.1096, 1st-half IC=+0.1114, 2nd-half IC=+0.0954, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.054, Q3_mid=+0.102, Q4=+0.066, Q5_high_vol=+0.200

**`combo_mean__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0496, Sharpe=+0.5363)
- Admission: Train IC=+0.1786, Deflated=+0.1792, IR=0.46, Mono=0.71, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.102 | 2017: -0.001 | 2018: +0.200 | 2019: +0.105 | 2020: +0.047 | 2021: +0.140 | 2022: +0.075 | 2023: +0.090 | 2024: +0.014 | 2025: +0.065 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.107 | 2016: +0.093 | 2017: -0.066 | 2018: +0.334 | 2019: +0.204 | 2020: +0.177 | 2021: +0.328 | 2022: +0.219 | 2023: +0.012 | 2024: +0.165 | 2025: +0.239 | 2026: +0.049
- IC CV=0.59, Neg years (linear/tail)=1/1 of 8, Half ratio=0.75, Recency ratio=1.63
- Early IC=+0.0506, Recent IC=+0.0824, 1st-half IC=+0.1153, 2nd-half IC=+0.0870, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.045, Q3_mid=+0.061, Q4=+0.060, Q5_high_vol=+0.204

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0254, Sharpe=+0.4883)
- Admission: Train IC=+0.2251, Deflated=+0.2250, IR=0.49, Mono=0.65, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.093 | 2017: -0.048 | 2018: +0.184 | 2019: +0.102 | 2020: +0.020 | 2021: +0.173 | 2022: +0.059 | 2023: +0.171 | 2024: +0.056 | 2025: +0.067 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.078 | 2017: -0.022 | 2018: +0.230 | 2019: +0.266 | 2020: +0.036 | 2021: +0.419 | 2022: +0.401 | 2023: +0.231 | 2024: +0.293 | 2025: +0.071 | 2026: -0.049
- IC CV=0.81, Neg years (linear/tail)=1/1 of 8, Half ratio=1.11, Recency ratio=5.15
- Early IC=+0.0224, Recent IC=+0.1152, 1st-half IC=+0.0950, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.073, Q3_mid=+0.095, Q4=+0.045, Q5_high_vol=+0.190

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early`** (Lock IC=+0.0352, Sharpe=+0.4654)
- Admission: Train IC=+0.1989, Deflated=+0.1979, IR=0.55, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.046 | 2017: -0.059 | 2018: +0.174 | 2019: +0.084 | 2020: +0.062 | 2021: +0.140 | 2022: +0.039 | 2023: +0.161 | 2024: +0.053 | 2025: +0.101 | 2026: -0.104
- Yearly Tail ICs:   2015: -0.077 | 2016: +0.111 | 2017: +0.016 | 2018: +0.361 | 2019: +0.236 | 2020: +0.163 | 2021: +0.262 | 2022: +0.211 | 2023: +0.197 | 2024: +0.211 | 2025: +0.121 | 2026: -0.228
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.31, Recency ratio=-15.67
- Early IC=-0.0064, Recent IC=+0.0998, 1st-half IC=+0.0743, 2nd-half IC=+0.0977, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.095, Q3_mid=+0.080, Q4=+0.017, Q5_high_vol=+0.207

**`combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`** (Lock IC=+0.0231, Sharpe=+0.3889)
- Admission: Train IC=+0.1673, Deflated=+0.1669, IR=0.54, Mono=0.72, p=0.0010, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.029 | 2017: -0.056 | 2018: +0.072 | 2019: +0.065 | 2020: +0.050 | 2021: +0.199 | 2022: +0.084 | 2023: +0.113 | 2024: +0.005 | 2025: +0.075 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.326 | 2016: +0.103 | 2017: +0.003 | 2018: +0.277 | 2019: +0.136 | 2020: +0.097 | 2021: +0.309 | 2022: +0.283 | 2023: +0.190 | 2024: +0.179 | 2025: +0.247 | 2026: +0.120
- IC CV=0.97, Neg years (linear/tail)=1/0 of 8, Half ratio=2.71, Recency ratio=-7.24
- Early IC=-0.0136, Recent IC=+0.0981, 1st-half IC=+0.0422, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `morning_volume_weighted_momentum` (CV=1.71)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.060, Q3_mid=+0.086, Q4=+0.077, Q5_high_vol=+0.149

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0329, Sharpe=+0.3820)
- Admission: Train IC=+0.2034, Deflated=+0.2038, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.121 | 2017: -0.013 | 2018: +0.219 | 2019: +0.089 | 2020: +0.057 | 2021: +0.162 | 2022: +0.072 | 2023: +0.123 | 2024: +0.029 | 2025: +0.072 | 2026: -0.028
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.153 | 2017: +0.031 | 2018: +0.329 | 2019: +0.149 | 2020: +0.103 | 2021: +0.398 | 2022: +0.268 | 2023: +0.135 | 2024: +0.169 | 2025: +0.090 | 2026: +0.115
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=0.94, Recency ratio=1.81
- Early IC=+0.0537, Recent IC=+0.0973, 1st-half IC=+0.1123, 2nd-half IC=+0.1053, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.073, Q3_mid=+0.063, Q4=+0.054, Q5_high_vol=+0.230

**`combo_tri_median__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0238, Sharpe=+0.3693)
- Admission: Train IC=+0.2055, Deflated=+0.2052, IR=0.52, Mono=0.67, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.080 | 2017: -0.048 | 2018: +0.164 | 2019: +0.121 | 2020: +0.044 | 2021: +0.174 | 2022: +0.053 | 2023: +0.166 | 2024: +0.041 | 2025: +0.073 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.117 | 2016: +0.061 | 2017: -0.054 | 2018: +0.171 | 2019: +0.259 | 2020: +0.094 | 2021: +0.381 | 2022: +0.349 | 2023: +0.224 | 2024: +0.262 | 2025: +0.014 | 2026: -0.097
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=1.13, Recency ratio=6.91
- Early IC=+0.0159, Recent IC=+0.1098, 1st-half IC=+0.0948, 2nd-half IC=+0.1067, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.088, Q3_mid=+0.091, Q4=+0.061, Q5_high_vol=+0.180

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0362, Sharpe=+0.3660)
- Admission: Train IC=+0.2341, Deflated=+0.2347, IR=0.59, Mono=0.74, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.108 | 2017: +0.017 | 2018: +0.217 | 2019: +0.106 | 2020: +0.040 | 2021: +0.142 | 2022: +0.073 | 2023: +0.129 | 2024: +0.014 | 2025: +0.084 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.046 | 2017: -0.002 | 2018: +0.302 | 2019: +0.175 | 2020: +0.236 | 2021: +0.451 | 2022: +0.307 | 2023: +0.233 | 2024: +0.102 | 2025: +0.150 | 2026: +0.042
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=1.61
- Early IC=+0.0626, Recent IC=+0.1009, 1st-half IC=+0.1241, 2nd-half IC=+0.0951, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.060, Q3_mid=+0.078, Q4=+0.074, Q5_high_vol=+0.197

**`combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0483, Sharpe=+0.3089)
- Admission: Train IC=+0.1694, Deflated=+0.1691, IR=0.42, Mono=0.66, p=0.0010, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.073 | 2017: -0.034 | 2018: +0.209 | 2019: +0.106 | 2020: +0.028 | 2021: +0.148 | 2022: +0.021 | 2023: +0.111 | 2024: +0.043 | 2025: +0.079 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.083 | 2017: -0.114 | 2018: +0.380 | 2019: +0.322 | 2020: +0.138 | 2021: +0.305 | 2022: +0.161 | 2023: +0.052 | 2024: +0.273 | 2025: +0.037 | 2026: +0.266
- IC CV=0.88, Neg years (linear/tail)=1/1 of 8, Half ratio=0.72, Recency ratio=3.36
- Early IC=+0.0196, Recent IC=+0.0659, 1st-half IC=+0.1055, 2nd-half IC=+0.0758, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.047, Q3_mid=+0.082, Q4=+0.038, Q5_high_vol=+0.203

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0193, Sharpe=+0.2919)
- Admission: Train IC=+0.1871, Deflated=+0.1864, IR=0.48, Mono=0.69, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.080 | 2017: -0.053 | 2018: +0.163 | 2019: +0.083 | 2020: +0.044 | 2021: +0.141 | 2022: +0.033 | 2023: +0.161 | 2024: +0.046 | 2025: +0.069 | 2026: -0.110
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.117 | 2017: +0.043 | 2018: +0.297 | 2019: +0.270 | 2020: +0.054 | 2021: +0.348 | 2022: +0.210 | 2023: +0.232 | 2024: +0.313 | 2025: +0.023 | 2026: -0.211
- IC CV=0.85, Neg years (linear/tail)=1/0 of 8, Half ratio=1.27, Recency ratio=7.30
- Early IC=+0.0133, Recent IC=+0.0970, 1st-half IC=+0.0730, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.074, Q3_mid=+0.071, Q4=+0.018, Q5_high_vol=+0.201

**`combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0337, Sharpe=+0.2687)
- Admission: Train IC=+0.1930, Deflated=+0.1928, IR=0.60, Mono=0.70, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.114 | 2017: -0.037 | 2018: +0.200 | 2019: +0.134 | 2020: +0.018 | 2021: +0.146 | 2022: +0.069 | 2023: +0.175 | 2024: +0.050 | 2025: +0.073 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.193 | 2017: -0.111 | 2018: +0.227 | 2019: +0.216 | 2020: +0.083 | 2021: +0.387 | 2022: +0.333 | 2023: +0.216 | 2024: +0.163 | 2025: +0.227 | 2026: -0.030
- IC CV=0.74, Neg years (linear/tail)=1/1 of 8, Half ratio=0.87, Recency ratio=3.16
- Early IC=+0.0385, Recent IC=+0.1220, 1st-half IC=+0.1167, 2nd-half IC=+0.1020, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.103, Q3_mid=+0.101, Q4=+0.030, Q5_high_vol=+0.211

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0351, Sharpe=+0.1736)
- Admission: Train IC=+0.2509, Deflated=+0.2505, IR=0.74, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.87, Neg years (linear/tail)=1/0 of 8, Half ratio=1.13, Recency ratio=-40.14
- Early IC=-0.0023, Recent IC=+0.0922, 1st-half IC=+0.0952, 2nd-half IC=+0.1073, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.067, Q3_mid=+0.129, Q4=+0.053, Q5_high_vol=+0.214

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0124, Sharpe=+0.1247)
- Admission: Train IC=+0.2167, Deflated=+0.2167, IR=0.71, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.075 | 2017: +0.048 | 2018: +0.173 | 2019: +0.064 | 2020: +0.032 | 2021: +0.176 | 2022: +0.011 | 2023: +0.163 | 2024: +0.060 | 2025: +0.077 | 2026: -0.156
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.085 | 2017: +0.044 | 2018: +0.383 | 2019: +0.230 | 2020: +0.137 | 2021: +0.433 | 2022: +0.238 | 2023: +0.346 | 2024: +0.122 | 2025: +0.070 | 2026: -0.295
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.40
- Early IC=+0.0619, Recent IC=+0.0867, 1st-half IC=+0.0843, 2nd-half IC=+0.0956, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.076, Q3_mid=+0.063, Q4=+0.046, Q5_high_vol=+0.162

**`combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0094, Sharpe=+0.1080)
- Admission: Train IC=+0.2493, Deflated=+0.2494, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.107 | 2016: +0.081 | 2017: +0.041 | 2018: +0.222 | 2019: +0.065 | 2020: -0.027 | 2021: +0.145 | 2022: +0.066 | 2023: +0.176 | 2024: +0.015 | 2025: +0.076 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.053 | 2016: -0.023 | 2017: +0.226 | 2018: +0.296 | 2019: +0.286 | 2020: +0.061 | 2021: +0.427 | 2022: +0.327 | 2023: +0.379 | 2024: +0.066 | 2025: -0.056 | 2026: -0.157
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=0.82, Recency ratio=1.96
- Early IC=+0.0614, Recent IC=+0.1207, 1st-half IC=+0.1105, 2nd-half IC=+0.0905, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.112, Q3_mid=+0.086, Q4=+0.060, Q5_high_vol=+0.149

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0460, Sharpe=+0.1064)
- Admission: Train IC=+0.2599, Deflated=+0.2605, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.063 | 2017: -0.016 | 2018: +0.189 | 2019: +0.144 | 2020: +0.030 | 2021: +0.132 | 2022: +0.046 | 2023: +0.173 | 2024: +0.043 | 2025: +0.095 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.177 | 2017: +0.078 | 2018: +0.349 | 2019: +0.209 | 2020: +0.188 | 2021: +0.488 | 2022: +0.218 | 2023: +0.247 | 2024: +0.239 | 2025: -0.017 | 2026: +0.296
- IC CV=0.73, Neg years (linear/tail)=1/0 of 8, Half ratio=0.85, Recency ratio=4.68
- Early IC=+0.0234, Recent IC=+0.1097, 1st-half IC=+0.1086, 2nd-half IC=+0.0920, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.051, Q3_mid=+0.095, Q4=+0.066, Q5_high_vol=+0.188

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0245, Sharpe=+0.1045)
- Admission: Train IC=+0.2592, Deflated=+0.2591, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.089 | 2017: -0.052 | 2018: +0.208 | 2019: +0.118 | 2020: +0.070 | 2021: +0.173 | 2022: +0.016 | 2023: +0.138 | 2024: +0.065 | 2025: +0.033 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.292 | 2016: +0.152 | 2017: +0.065 | 2018: +0.347 | 2019: +0.371 | 2020: +0.161 | 2021: +0.519 | 2022: +0.224 | 2023: +0.132 | 2024: +0.315 | 2025: -0.067 | 2026: +0.109
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=0.98, Recency ratio=4.08
- Early IC=+0.0188, Recent IC=+0.0769, 1st-half IC=+0.1024, 2nd-half IC=+0.1002, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.058, Q3_mid=+0.112, Q4=+0.050, Q5_high_vol=+0.218

**`combo_tri_median__max_up_ret__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0012, Sharpe=+0.0941)
- Admission: Train IC=+0.1982, Deflated=+0.1987, IR=0.47, Mono=0.67, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.127 | 2016: +0.076 | 2017: -0.016 | 2018: +0.197 | 2019: +0.080 | 2020: -0.005 | 2021: +0.168 | 2022: +0.040 | 2023: +0.175 | 2024: +0.013 | 2025: +0.068 | 2026: -0.116
- Yearly Tail ICs:   2015: +0.075 | 2016: +0.058 | 2017: -0.154 | 2018: +0.357 | 2019: +0.180 | 2020: +0.044 | 2021: +0.395 | 2022: +0.208 | 2023: +0.398 | 2024: +0.157 | 2025: +0.090 | 2026: -0.068
- IC CV=0.87, Neg years (linear/tail)=2/1 of 8, Half ratio=1.05, Recency ratio=3.58
- Early IC=+0.0299, Recent IC=+0.1072, 1st-half IC=+0.0918, 2nd-half IC=+0.0967, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.107, Q3_mid=+0.059, Q4=+0.057, Q5_high_vol=+0.158

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration`** (Lock IC=+0.0048, Sharpe=+0.0349)
- Admission: Train IC=+0.2060, Deflated=+0.2054, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.098 | 2017: -0.024 | 2018: +0.140 | 2019: +0.051 | 2020: +0.053 | 2021: +0.164 | 2022: -0.001 | 2023: +0.155 | 2024: +0.059 | 2025: +0.048 | 2026: -0.161
- Yearly Tail ICs:   2015: +0.045 | 2016: +0.283 | 2017: +0.030 | 2018: +0.311 | 2019: +0.099 | 2020: +0.249 | 2021: +0.338 | 2022: +0.123 | 2023: +0.281 | 2024: +0.214 | 2025: -0.048 | 2026: -0.334
- IC CV=0.84, Neg years (linear/tail)=2/0 of 8, Half ratio=1.35, Recency ratio=2.05
- Early IC=+0.0373, Recent IC=+0.0767, 1st-half IC=+0.0671, 2nd-half IC=+0.0904, Neg regimes=0/5
- Weak component: `volume_concentration` (CV=0.95)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.079, Q3_mid=+0.062, Q4=+0.042, Q5_high_vol=+0.172

### 500ETF — `single` True Positives

**`combo_tri_min__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction`** (Lock IC=+0.1143, Sharpe=+1.4452)
- Admission: Train IC=+0.2217, Deflated=+0.2224, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.113 | 2017: +0.213 | 2018: +0.096 | 2019: +0.106 | 2020: +0.126 | 2021: +0.116 | 2022: +0.044 | 2023: +0.107 | 2024: +0.145 | 2025: +0.107 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.233 | 2017: +0.274 | 2018: +0.303 | 2019: +0.183 | 2020: +0.173 | 2021: +0.161 | 2022: +0.184 | 2023: +0.097 | 2024: +0.283 | 2025: +0.107 | 2026: +0.390
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.46
- Early IC=+0.1627, Recent IC=+0.0755, 1st-half IC=+0.1221, 2nd-half IC=+0.0962, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.223, Q2=-0.019, Q3_mid=+0.095, Q4=+0.099, Q5_high_vol=+0.135

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1136, Sharpe=+1.3415)
- Admission: Train IC=+0.2451, Deflated=+0.2458, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.116 | 2017: +0.223 | 2018: +0.204 | 2019: +0.159 | 2020: +0.162 | 2021: +0.125 | 2022: +0.044 | 2023: +0.097 | 2024: +0.106 | 2025: +0.133 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.195 | 2017: +0.227 | 2018: +0.405 | 2019: +0.246 | 2020: +0.335 | 2021: +0.177 | 2022: +0.041 | 2023: +0.162 | 2024: +0.223 | 2025: +0.257 | 2026: +0.178
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.39
- Early IC=+0.1724, Recent IC=+0.0680, 1st-half IC=+0.1711, 2nd-half IC=+0.1013, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.225, Q2=-0.030, Q3_mid=+0.090, Q4=+0.197, Q5_high_vol=+0.175

**`combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.1246, Sharpe=+1.3362)
- Admission: Train IC=+0.2317, Deflated=+0.2320, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.065 | 2017: +0.225 | 2018: +0.087 | 2019: +0.108 | 2020: +0.121 | 2021: +0.098 | 2022: +0.042 | 2023: +0.099 | 2024: +0.139 | 2025: +0.131 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.168 | 2017: +0.279 | 2018: +0.269 | 2019: +0.303 | 2020: +0.277 | 2021: +0.193 | 2022: +0.116 | 2023: +0.216 | 2024: +0.236 | 2025: +0.068 | 2026: +0.194
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.48
- Early IC=+0.1466, Recent IC=+0.0706, 1st-half IC=+0.1180, 2nd-half IC=+0.0881, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.026, Q3_mid=+0.104, Q4=+0.100, Q5_high_vol=+0.122

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1125, Sharpe=+1.2249)
- Admission: Train IC=+0.2524, Deflated=+0.2531, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.096 | 2017: +0.220 | 2018: +0.142 | 2019: +0.098 | 2020: +0.115 | 2021: +0.120 | 2022: +0.072 | 2023: +0.111 | 2024: +0.124 | 2025: +0.140 | 2026: +0.042
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.217 | 2017: +0.309 | 2018: +0.361 | 2019: +0.184 | 2020: +0.305 | 2021: +0.187 | 2022: +0.177 | 2023: +0.198 | 2024: +0.316 | 2025: +0.171 | 2026: +0.245
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.58
- Early IC=+0.1578, Recent IC=+0.0914, 1st-half IC=+0.1311, 2nd-half IC=+0.1021, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.009, Q3_mid=+0.097, Q4=+0.107, Q5_high_vol=+0.158

**`combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.1215, Sharpe=+1.2167)
- Admission: Train IC=+0.2346, Deflated=+0.2350, IR=0.85, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.096 | 2017: +0.227 | 2018: +0.137 | 2019: +0.123 | 2020: +0.150 | 2021: +0.116 | 2022: +0.070 | 2023: +0.090 | 2024: +0.121 | 2025: +0.148 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.248 | 2017: +0.311 | 2018: +0.407 | 2019: +0.129 | 2020: +0.336 | 2021: +0.116 | 2022: +0.084 | 2023: +0.195 | 2024: +0.361 | 2025: +0.093 | 2026: +0.243
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.47
- Early IC=+0.1637, Recent IC=+0.0769, 1st-half IC=+0.1387, 2nd-half IC=+0.1041, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.216, Q2=-0.022, Q3_mid=+0.111, Q4=+0.134, Q5_high_vol=+0.155

**`combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1214, Sharpe=+1.1911)
- Admission: Train IC=+0.2217, Deflated=+0.2224, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.063 | 2017: +0.212 | 2018: +0.120 | 2019: +0.146 | 2020: +0.115 | 2021: +0.104 | 2022: +0.049 | 2023: +0.071 | 2024: +0.133 | 2025: +0.133 | 2026: +0.097
- Yearly Tail ICs:   2015: +0.316 | 2016: +0.101 | 2017: +0.184 | 2018: +0.319 | 2019: +0.290 | 2020: +0.201 | 2021: +0.143 | 2022: +0.190 | 2023: +0.253 | 2024: +0.380 | 2025: +0.139 | 2026: +0.231
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.44
- Early IC=+0.1373, Recent IC=+0.0599, 1st-half IC=+0.1293, 2nd-half IC=+0.0789, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.053, Q3_mid=+0.081, Q4=+0.143, Q5_high_vol=+0.120

**`combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range`** (Lock IC=+0.1196, Sharpe=+1.1815)
- Admission: Train IC=+0.2256, Deflated=+0.2262, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.101 | 2017: +0.226 | 2018: +0.122 | 2019: +0.077 | 2020: +0.128 | 2021: +0.108 | 2022: +0.060 | 2023: +0.100 | 2024: +0.129 | 2025: +0.149 | 2026: +0.060
- Yearly Tail ICs:   2015: +0.260 | 2016: +0.270 | 2017: +0.322 | 2018: +0.324 | 2019: +0.098 | 2020: +0.226 | 2021: +0.223 | 2022: +0.126 | 2023: +0.014 | 2024: +0.266 | 2025: +0.211 | 2026: +0.283
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.49
- Early IC=+0.1639, Recent IC=+0.0802, 1st-half IC=+0.1241, 2nd-half IC=+0.0984, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.005, Q3_mid=+0.092, Q4=+0.098, Q5_high_vol=+0.151

**`combo_rank_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1418, Sharpe=+1.1539)
- Admission: Train IC=+0.1568, Deflated=+0.1564, IR=0.44, Mono=0.65, p=0.0030, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.057 | 2017: +0.230 | 2018: +0.093 | 2019: +0.123 | 2020: +0.133 | 2021: +0.031 | 2022: +0.096 | 2023: +0.036 | 2024: +0.139 | 2025: +0.111 | 2026: +0.152
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.065 | 2017: +0.185 | 2018: +0.151 | 2019: +0.343 | 2020: +0.164 | 2021: +0.294 | 2022: +0.113 | 2023: +0.030 | 2024: +0.178 | 2025: +0.302 | 2026: +0.147
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.46
- Early IC=+0.1435, Recent IC=+0.0667, 1st-half IC=+0.1211, 2nd-half IC=+0.0735, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.015, Q3_mid=+0.096, Q4=+0.114, Q5_high_vol=+0.123

**`combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range`** (Lock IC=+0.1201, Sharpe=+1.0892)
- Admission: Train IC=+0.2271, Deflated=+0.2273, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.123 | 2017: +0.207 | 2018: +0.144 | 2019: +0.105 | 2020: +0.147 | 2021: +0.068 | 2022: +0.099 | 2023: +0.073 | 2024: +0.110 | 2025: +0.114 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.183 | 2016: +0.229 | 2017: +0.308 | 2018: +0.290 | 2019: +0.243 | 2020: +0.201 | 2021: +0.165 | 2022: +0.144 | 2023: +0.012 | 2024: +0.262 | 2025: +0.100 | 2026: +0.157
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.52
- Early IC=+0.1649, Recent IC=+0.0863, 1st-half IC=+0.1386, 2nd-half IC=+0.1012, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.010, Q3_mid=+0.087, Q4=+0.106, Q5_high_vol=+0.178

**`combo_min__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1235, Sharpe=+1.0733)
- Admission: Train IC=+0.2285, Deflated=+0.2290, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.062 | 2017: +0.229 | 2018: +0.101 | 2019: +0.126 | 2020: +0.120 | 2021: +0.096 | 2022: +0.062 | 2023: +0.082 | 2024: +0.139 | 2025: +0.136 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.291 | 2016: +0.200 | 2017: +0.224 | 2018: +0.331 | 2019: +0.260 | 2020: +0.265 | 2021: -0.014 | 2022: +0.182 | 2023: +0.180 | 2024: +0.382 | 2025: +0.034 | 2026: +0.286
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.50
- Early IC=+0.1458, Recent IC=+0.0723, 1st-half IC=+0.1234, 2nd-half IC=+0.0851, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.033, Q3_mid=+0.101, Q4=+0.113, Q5_high_vol=+0.121

**`combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0898, Sharpe=+1.0714)
- Admission: Train IC=+0.2045, Deflated=+0.2031, IR=0.57, Mono=0.72, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.050 | 2017: +0.154 | 2018: +0.200 | 2019: +0.172 | 2020: +0.197 | 2021: +0.147 | 2022: +0.046 | 2023: +0.107 | 2024: +0.142 | 2025: +0.061 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.367 | 2016: -0.054 | 2017: +0.147 | 2018: +0.322 | 2019: +0.292 | 2020: +0.153 | 2021: +0.063 | 2022: +0.250 | 2023: +0.161 | 2024: +0.162 | 2025: +0.168 | 2026: -0.301
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=0.75
- Early IC=+0.1020, Recent IC=+0.0766, 1st-half IC=+0.1446, 2nd-half IC=+0.1230, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.156, Q2=-0.002, Q3_mid=+0.149, Q4=+0.141, Q5_high_vol=+0.207

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.1084, Sharpe=+1.0418)
- Admission: Train IC=+0.2777, Deflated=+0.2783, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.107 | 2017: +0.207 | 2018: +0.137 | 2019: +0.131 | 2020: +0.156 | 2021: +0.156 | 2022: +0.074 | 2023: +0.107 | 2024: +0.131 | 2025: +0.122 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.225 | 2017: +0.232 | 2018: +0.388 | 2019: +0.210 | 2020: +0.317 | 2021: +0.248 | 2022: +0.200 | 2023: +0.235 | 2024: +0.423 | 2025: +0.106 | 2026: +0.286
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.58
- Early IC=+0.1574, Recent IC=+0.0905, 1st-half IC=+0.1383, 2nd-half IC=+0.1220, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.216, Q2=-0.011, Q3_mid=+0.110, Q4=+0.142, Q5_high_vol=+0.171

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1294, Sharpe=+1.0283)
- Admission: Train IC=+0.2136, Deflated=+0.2130, IR=0.84, Mono=0.81, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.045 | 2017: +0.226 | 2018: +0.140 | 2019: +0.157 | 2020: +0.154 | 2021: +0.138 | 2022: +0.032 | 2023: +0.096 | 2024: +0.174 | 2025: +0.105 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.163 | 2017: +0.307 | 2018: +0.406 | 2019: +0.362 | 2020: +0.212 | 2021: +0.216 | 2022: +0.114 | 2023: +0.006 | 2024: +0.367 | 2025: +0.039 | 2026: +0.231
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.49
- Early IC=+0.1347, Recent IC=+0.0660, 1st-half IC=+0.1412, 2nd-half IC=+0.1051, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.027, Q3_mid=+0.131, Q4=+0.140, Q5_high_vol=+0.154

**`combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`** (Lock IC=+0.0877, Sharpe=+1.0117)
- Admission: Train IC=+0.1568, Deflated=+0.1566, IR=0.58, Mono=0.69, p=0.0030, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.290 | 2016: +0.033 | 2017: +0.193 | 2018: +0.175 | 2019: +0.153 | 2020: +0.143 | 2021: +0.128 | 2022: +0.036 | 2023: +0.094 | 2024: +0.101 | 2025: +0.047 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.446 | 2016: +0.041 | 2017: +0.428 | 2018: +0.143 | 2019: +0.298 | 2020: +0.117 | 2021: +0.179 | 2022: +0.049 | 2023: +0.129 | 2024: +0.215 | 2025: +0.042 | 2026: +0.346
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.57
- Early IC=+0.1134, Recent IC=+0.0650, 1st-half IC=+0.1393, 2nd-half IC=+0.0959, Neg regimes=1/5
- Weak component: `late_bar_momentum` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.159, Q2=-0.024, Q3_mid=+0.101, Q4=+0.164, Q5_high_vol=+0.162

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1105, Sharpe=+0.9584)
- Admission: Train IC=+0.2665, Deflated=+0.2668, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.091 | 2017: +0.219 | 2018: +0.192 | 2019: +0.122 | 2020: +0.138 | 2021: +0.155 | 2022: +0.039 | 2023: +0.111 | 2024: +0.141 | 2025: +0.118 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.234 | 2017: +0.311 | 2018: +0.436 | 2019: +0.298 | 2020: +0.282 | 2021: +0.250 | 2022: +0.197 | 2023: +0.195 | 2024: +0.299 | 2025: +0.047 | 2026: +0.246
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.48
- Early IC=+0.1547, Recent IC=+0.0747, 1st-half IC=+0.1504, 2nd-half IC=+0.1105, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.210, Q2=-0.012, Q3_mid=+0.113, Q4=+0.115, Q5_high_vol=+0.188

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1055, Sharpe=+0.9440)
- Admission: Train IC=+0.2062, Deflated=+0.2059, IR=0.65, Mono=0.69, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.121 | 2017: +0.238 | 2018: +0.234 | 2019: +0.163 | 2020: +0.181 | 2021: +0.117 | 2022: +0.082 | 2023: +0.084 | 2024: +0.140 | 2025: +0.110 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.389 | 2016: +0.149 | 2017: +0.293 | 2018: +0.388 | 2019: +0.261 | 2020: +0.225 | 2021: +0.164 | 2022: +0.026 | 2023: +0.161 | 2024: +0.211 | 2025: +0.027 | 2026: -0.026
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.46
- Early IC=+0.1796, Recent IC=+0.0830, 1st-half IC=+0.1837, 2nd-half IC=+0.1166, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.017, Q3_mid=+0.146, Q4=+0.157, Q5_high_vol=+0.197

**`combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0891, Sharpe=+0.9407)
- Admission: Train IC=+0.2037, Deflated=+0.2032, IR=0.53, Mono=0.67, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.113 | 2017: +0.117 | 2018: +0.160 | 2019: +0.091 | 2020: +0.103 | 2021: +0.020 | 2022: +0.138 | 2023: +0.079 | 2024: +0.101 | 2025: +0.090 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.046 | 2016: +0.458 | 2017: +0.197 | 2018: +0.162 | 2019: +0.172 | 2020: +0.112 | 2021: +0.121 | 2022: +0.140 | 2023: +0.150 | 2024: +0.232 | 2025: -0.056 | 2026: -0.127
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.94
- Early IC=+0.1150, Recent IC=+0.1086, 1st-half IC=+0.1197, 2nd-half IC=+0.0884, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.011, Q3_mid=+0.067, Q4=+0.108, Q5_high_vol=+0.161

**`combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.1123, Sharpe=+0.9259)
- Admission: Train IC=+0.2377, Deflated=+0.2386, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.070 | 2017: +0.209 | 2018: +0.178 | 2019: +0.131 | 2020: +0.105 | 2021: +0.118 | 2022: +0.035 | 2023: +0.093 | 2024: +0.115 | 2025: +0.132 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.099 | 2017: +0.291 | 2018: +0.378 | 2019: +0.247 | 2020: +0.173 | 2021: +0.193 | 2022: +0.139 | 2023: +0.241 | 2024: +0.297 | 2025: +0.200 | 2026: +0.211
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.46
- Early IC=+0.1394, Recent IC=+0.0641, 1st-half IC=+0.1405, 2nd-half IC=+0.0819, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.242, Q2=-0.049, Q3_mid=+0.071, Q4=+0.143, Q5_high_vol=+0.144

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0858, Sharpe=+0.9255)
- Admission: Train IC=+0.2566, Deflated=+0.2561, IR=0.98, Mono=0.83, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.089 | 2017: +0.132 | 2018: +0.261 | 2019: +0.173 | 2020: +0.172 | 2021: +0.171 | 2022: +0.067 | 2023: +0.081 | 2024: +0.141 | 2025: +0.071 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.203 | 2016: +0.143 | 2017: +0.307 | 2018: +0.604 | 2019: +0.196 | 2020: +0.164 | 2021: +0.291 | 2022: +0.168 | 2023: +0.255 | 2024: +0.189 | 2025: -0.040 | 2026: +0.007
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.67
- Early IC=+0.1104, Recent IC=+0.0742, 1st-half IC=+0.1624, 2nd-half IC=+0.1248, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.002, Q3_mid=+0.130, Q4=+0.141, Q5_high_vol=+0.244

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1056, Sharpe=+0.9169)
- Admission: Train IC=+0.2753, Deflated=+0.2761, IR=0.89, Mono=0.79, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.104 | 2017: +0.215 | 2018: +0.215 | 2019: +0.154 | 2020: +0.131 | 2021: +0.129 | 2022: +0.040 | 2023: +0.090 | 2024: +0.106 | 2025: +0.119 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.242 | 2017: +0.302 | 2018: +0.463 | 2019: +0.313 | 2020: +0.355 | 2021: +0.045 | 2022: +0.060 | 2023: +0.155 | 2024: +0.264 | 2025: +0.128 | 2026: +0.198
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.41
- Early IC=+0.1592, Recent IC=+0.0650, 1st-half IC=+0.1652, 2nd-half IC=+0.0930, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.230, Q2=-0.039, Q3_mid=+0.075, Q4=+0.189, Q5_high_vol=+0.164

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0874, Sharpe=+0.8706)
- Admission: Train IC=+0.2513, Deflated=+0.2506, IR=0.88, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.110 | 2017: +0.143 | 2018: +0.284 | 2019: +0.175 | 2020: +0.171 | 2021: +0.171 | 2022: +0.054 | 2023: +0.101 | 2024: +0.158 | 2025: +0.058 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.204 | 2017: +0.306 | 2018: +0.603 | 2019: +0.184 | 2020: +0.123 | 2021: +0.299 | 2022: +0.158 | 2023: +0.252 | 2024: +0.191 | 2025: -0.034 | 2026: +0.013
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.61
- Early IC=+0.1265, Recent IC=+0.0775, 1st-half IC=+0.1778, 2nd-half IC=+0.1247, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.004, Q3_mid=+0.143, Q4=+0.164, Q5_high_vol=+0.241

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0908, Sharpe=+0.8692)
- Admission: Train IC=+0.2425, Deflated=+0.2437, IR=0.62, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.325 | 2016: +0.091 | 2017: +0.223 | 2018: +0.190 | 2019: +0.157 | 2020: +0.157 | 2021: +0.104 | 2022: +0.034 | 2023: +0.091 | 2024: +0.100 | 2025: +0.103 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.137 | 2017: +0.138 | 2018: +0.474 | 2019: +0.259 | 2020: +0.283 | 2021: +0.160 | 2022: +0.129 | 2023: +0.143 | 2024: +0.248 | 2025: +0.099 | 2026: +0.117
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.40
- Early IC=+0.1570, Recent IC=+0.0625, 1st-half IC=+0.1550, 2nd-half IC=+0.0965, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.252, Q2=-0.057, Q3_mid=+0.097, Q4=+0.167, Q5_high_vol=+0.163

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0855, Sharpe=+0.8416)
- Admission: Train IC=+0.2698, Deflated=+0.2695, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.101 | 2017: +0.199 | 2018: +0.218 | 2019: +0.146 | 2020: +0.162 | 2021: +0.137 | 2022: +0.068 | 2023: +0.105 | 2024: +0.136 | 2025: +0.021 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.164 | 2017: +0.434 | 2018: +0.346 | 2019: +0.293 | 2020: +0.075 | 2021: +0.226 | 2022: +0.235 | 2023: +0.210 | 2024: +0.342 | 2025: +0.068 | 2026: +0.012
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.58
- Early IC=+0.1497, Recent IC=+0.0865, 1st-half IC=+0.1623, 2nd-half IC=+0.1171, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.015, Q3_mid=+0.106, Q4=+0.173, Q5_high_vol=+0.219

**`combo_rank_max__max_up_ret__max_down_ret`** (Lock IC=+0.0983, Sharpe=+0.8388)
- Admission: Train IC=+0.1683, Deflated=+0.1681, IR=0.66, Mono=0.75, p=0.0008, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.079 | 2017: +0.232 | 2018: +0.240 | 2019: +0.123 | 2020: +0.132 | 2021: +0.128 | 2022: +0.077 | 2023: +0.052 | 2024: +0.142 | 2025: +0.111 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.520 | 2016: -0.023 | 2017: +0.192 | 2018: +0.193 | 2019: +0.374 | 2020: +0.193 | 2021: +0.307 | 2022: +0.142 | 2023: +0.092 | 2024: +0.311 | 2025: +0.202 | 2026: -0.142
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.47
- Early IC=+0.1548, Recent IC=+0.0731, 1st-half IC=+0.1604, 2nd-half IC=+0.1015, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.200, Q2=-0.047, Q3_mid=+0.129, Q4=+0.115, Q5_high_vol=+0.221

**`combo_tri_median__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.1079, Sharpe=+0.8366)
- Admission: Train IC=+0.2165, Deflated=+0.2163, IR=0.65, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.077 | 2017: +0.201 | 2018: +0.202 | 2019: +0.111 | 2020: +0.141 | 2021: +0.088 | 2022: +0.131 | 2023: +0.115 | 2024: +0.156 | 2025: +0.157 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.236 | 2016: +0.155 | 2017: +0.250 | 2018: +0.341 | 2019: +0.292 | 2020: +0.154 | 2021: +0.102 | 2022: +0.257 | 2023: +0.153 | 2024: +0.247 | 2025: +0.005 | 2026: -0.203
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.88
- Early IC=+0.1392, Recent IC=+0.1232, 1st-half IC=+0.1396, 2nd-half IC=+0.1209, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.009, Q3_mid=+0.129, Q4=+0.125, Q5_high_vol=+0.200

**`combo_min__net_volume_flow__shaved_bar_trend_conviction`** (Lock IC=+0.0598, Sharpe=+0.8130)
- Admission: Train IC=+0.2016, Deflated=+0.2009, IR=0.67, Mono=0.75, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.039 | 2017: +0.149 | 2018: +0.087 | 2019: +0.018 | 2020: +0.095 | 2021: +0.040 | 2022: +0.053 | 2023: +0.099 | 2024: +0.089 | 2025: +0.108 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.192 | 2016: +0.079 | 2017: +0.214 | 2018: +0.167 | 2019: +0.179 | 2020: +0.190 | 2021: +0.160 | 2022: +0.128 | 2023: +0.294 | 2024: +0.362 | 2025: +0.121 | 2026: -0.155
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.81
- Early IC=+0.0937, Recent IC=+0.0761, 1st-half IC=+0.0739, 2nd-half IC=+0.0717, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.19)
- Regime ICs: Q1_low_vol=+0.158, Q2=-0.026, Q3_mid=+0.075, Q4=+0.095, Q5_high_vol=+0.076

**`combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1127, Sharpe=+0.8107)
- Admission: Train IC=+0.2290, Deflated=+0.2289, IR=0.83, Mono=0.80, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.278 | 2016: +0.084 | 2017: +0.229 | 2018: +0.191 | 2019: +0.141 | 2020: +0.178 | 2021: +0.111 | 2022: +0.082 | 2023: +0.077 | 2024: +0.131 | 2025: +0.101 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.152 | 2017: +0.297 | 2018: +0.312 | 2019: +0.332 | 2020: +0.150 | 2021: +0.203 | 2022: +0.340 | 2023: +0.170 | 2024: +0.206 | 2025: +0.020 | 2026: +0.077
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.51
- Early IC=+0.1567, Recent IC=+0.0796, 1st-half IC=+0.1611, 2nd-half IC=+0.1112, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.205, Q2=-0.007, Q3_mid=+0.118, Q4=+0.152, Q5_high_vol=+0.196

**`combo_tri_median__volatility_expansion_trend_vector__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1105, Sharpe=+0.7811)
- Admission: Train IC=+0.2168, Deflated=+0.2169, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.109 | 2017: +0.240 | 2018: +0.220 | 2019: +0.136 | 2020: +0.131 | 2021: +0.064 | 2022: +0.096 | 2023: +0.080 | 2024: +0.125 | 2025: +0.172 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.148 | 2017: +0.315 | 2018: +0.301 | 2019: +0.274 | 2020: +0.208 | 2021: +0.083 | 2022: +0.208 | 2023: +0.209 | 2024: +0.291 | 2025: +0.035 | 2026: -0.075
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.51
- Early IC=+0.1745, Recent IC=+0.0882, 1st-half IC=+0.1711, 2nd-half IC=+0.0942, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.004, Q3_mid=+0.138, Q4=+0.147, Q5_high_vol=+0.159

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1096, Sharpe=+0.7699)
- Admission: Train IC=+0.2410, Deflated=+0.2404, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.146 | 2017: +0.223 | 2018: +0.215 | 2019: +0.111 | 2020: +0.187 | 2021: +0.145 | 2022: +0.107 | 2023: +0.116 | 2024: +0.174 | 2025: +0.102 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.262 | 2017: +0.270 | 2018: +0.387 | 2019: +0.260 | 2020: +0.320 | 2021: +0.322 | 2022: +0.031 | 2023: +0.115 | 2024: +0.341 | 2025: -0.030 | 2026: -0.105
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.60
- Early IC=+0.1847, Recent IC=+0.1116, 1st-half IC=+0.1576, 2nd-half IC=+0.1433, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.015, Q3_mid=+0.138, Q4=+0.138, Q5_high_vol=+0.245

**`combo_min__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0997, Sharpe=+0.7541)
- Admission: Train IC=+0.2226, Deflated=+0.2229, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.069 | 2017: +0.197 | 2018: +0.177 | 2019: +0.123 | 2020: +0.076 | 2021: +0.068 | 2022: +0.059 | 2023: +0.084 | 2024: +0.128 | 2025: +0.135 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.363 | 2016: -0.009 | 2017: +0.339 | 2018: +0.328 | 2019: +0.191 | 2020: +0.108 | 2021: +0.337 | 2022: +0.259 | 2023: +0.261 | 2024: +0.189 | 2025: +0.193 | 2026: -0.129
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.51, Recency ratio=0.54
- Early IC=+0.1326, Recent IC=+0.0711, 1st-half IC=+0.1401, 2nd-half IC=+0.0720, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.043, Q3_mid=+0.099, Q4=+0.126, Q5_high_vol=+0.131

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1023, Sharpe=+0.7538)
- Admission: Train IC=+0.2532, Deflated=+0.2532, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.126 | 2017: +0.154 | 2018: +0.157 | 2019: +0.098 | 2020: +0.141 | 2021: +0.059 | 2022: +0.125 | 2023: +0.073 | 2024: +0.090 | 2025: +0.108 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.258 | 2017: +0.222 | 2018: +0.364 | 2019: +0.297 | 2020: +0.181 | 2021: +0.121 | 2022: +0.227 | 2023: +0.176 | 2024: +0.188 | 2025: +0.095 | 2026: +0.115
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.71
- Early IC=+0.1404, Recent IC=+0.0990, 1st-half IC=+0.1329, 2nd-half IC=+0.1050, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.006, Q3_mid=+0.081, Q4=+0.118, Q5_high_vol=+0.173

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1104, Sharpe=+0.7177)
- Admission: Train IC=+0.2428, Deflated=+0.2429, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.078 | 2017: +0.227 | 2018: +0.228 | 2019: +0.176 | 2020: +0.145 | 2021: +0.115 | 2022: +0.024 | 2023: +0.078 | 2024: +0.125 | 2025: +0.118 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.420 | 2016: +0.112 | 2017: +0.319 | 2018: +0.510 | 2019: +0.267 | 2020: +0.213 | 2021: +0.264 | 2022: +0.154 | 2023: +0.145 | 2024: +0.251 | 2025: +0.230 | 2026: +0.225
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.33
- Early IC=+0.1526, Recent IC=+0.0507, 1st-half IC=+0.1736, 2nd-half IC=+0.0901, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.043, Q3_mid=+0.116, Q4=+0.179, Q5_high_vol=+0.176

**`combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure`** (Lock IC=+0.0929, Sharpe=+0.7066)
- Admission: Train IC=+0.2400, Deflated=+0.2396, IR=0.78, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.070 | 2017: +0.154 | 2018: +0.135 | 2019: +0.099 | 2020: +0.111 | 2021: +0.092 | 2022: +0.103 | 2023: +0.097 | 2024: +0.146 | 2025: +0.123 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.296 | 2016: +0.167 | 2017: +0.152 | 2018: +0.278 | 2019: +0.227 | 2020: +0.259 | 2021: +0.271 | 2022: +0.319 | 2023: +0.229 | 2024: +0.296 | 2025: +0.027 | 2026: -0.203
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.89
- Early IC=+0.1121, Recent IC=+0.0999, 1st-half IC=+0.1157, 2nd-half IC=+0.0966, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.031, Q3_mid=+0.103, Q4=+0.132, Q5_high_vol=+0.139

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.1007, Sharpe=+0.6887)
- Admission: Train IC=+0.1757, Deflated=+0.1753, IR=0.60, Mono=0.72, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.070 | 2017: +0.271 | 2018: +0.191 | 2019: +0.147 | 2020: +0.174 | 2021: +0.099 | 2022: +0.054 | 2023: +0.065 | 2024: +0.158 | 2025: +0.105 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.084 | 2017: +0.234 | 2018: +0.163 | 2019: +0.358 | 2020: +0.068 | 2021: +0.297 | 2022: +0.084 | 2023: +0.183 | 2024: +0.402 | 2025: +0.178 | 2026: -0.048
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.38
- Early IC=+0.1685, Recent IC=+0.0640, 1st-half IC=+0.1649, 2nd-half IC=+0.1004, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.048, Q3_mid=+0.144, Q4=+0.135, Q5_high_vol=+0.199

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.1011, Sharpe=+0.6858)
- Admission: Train IC=+0.2503, Deflated=+0.2509, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.113 | 2017: +0.200 | 2018: +0.208 | 2019: +0.108 | 2020: +0.148 | 2021: +0.090 | 2022: +0.095 | 2023: +0.078 | 2024: +0.103 | 2025: +0.138 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.108 | 2017: +0.261 | 2018: +0.403 | 2019: +0.214 | 2020: +0.249 | 2021: +0.149 | 2022: +0.252 | 2023: +0.204 | 2024: +0.189 | 2025: +0.053 | 2026: +0.116
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.55
- Early IC=+0.1564, Recent IC=+0.0865, 1st-half IC=+0.1527, 2nd-half IC=+0.1032, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.011, Q3_mid=+0.095, Q4=+0.149, Q5_high_vol=+0.179

**`combo_rank_max__early_body_momentum__close_vs_open_range`** (Lock IC=+0.0793, Sharpe=+0.6809)
- Admission: Train IC=+0.1659, Deflated=+0.1661, IR=0.40, Mono=0.67, p=0.0012, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.156 | 2016: +0.069 | 2017: +0.160 | 2018: +0.108 | 2019: +0.043 | 2020: +0.096 | 2021: +0.059 | 2022: +0.103 | 2023: +0.078 | 2024: +0.128 | 2025: +0.145 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.146 | 2017: +0.200 | 2018: +0.103 | 2019: +0.107 | 2020: +0.236 | 2021: +0.239 | 2022: +0.159 | 2023: +0.114 | 2024: +0.331 | 2025: +0.052 | 2026: -0.053
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.79
- Early IC=+0.1138, Recent IC=+0.0897, 1st-half IC=+0.0950, 2nd-half IC=+0.0853, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.028, Q3_mid=+0.111, Q4=+0.095, Q5_high_vol=+0.104

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1093, Sharpe=+0.6791)
- Admission: Train IC=+0.1698, Deflated=+0.1698, IR=0.48, Mono=0.65, p=0.0006, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.035 | 2017: +0.230 | 2018: +0.096 | 2019: +0.112 | 2020: +0.112 | 2021: +0.045 | 2022: +0.059 | 2023: +0.041 | 2024: +0.101 | 2025: +0.097 | 2026: +0.123
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.149 | 2017: +0.179 | 2018: +0.258 | 2019: +0.335 | 2020: +0.233 | 2021: +0.135 | 2022: +0.067 | 2023: +0.017 | 2024: +0.243 | 2025: -0.030 | 2026: +0.271
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.37
- Early IC=+0.1328, Recent IC=+0.0497, 1st-half IC=+0.1081, 2nd-half IC=+0.0599, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.046, Q3_mid=+0.084, Q4=+0.105, Q5_high_vol=+0.090

**`combo_mean__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1133, Sharpe=+0.6694)
- Admission: Train IC=+0.2335, Deflated=+0.2337, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.094 | 2017: +0.192 | 2018: +0.143 | 2019: +0.122 | 2020: +0.147 | 2021: +0.089 | 2022: +0.086 | 2023: +0.058 | 2024: +0.111 | 2025: +0.105 | 2026: +0.107
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.136 | 2017: +0.233 | 2018: +0.338 | 2019: +0.401 | 2020: +0.183 | 2021: +0.109 | 2022: +0.277 | 2023: +0.155 | 2024: +0.249 | 2025: +0.039 | 2026: +0.240
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.50
- Early IC=+0.1430, Recent IC=+0.0718, 1st-half IC=+0.1345, 2nd-half IC=+0.0946, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.008, Q3_mid=+0.085, Q4=+0.125, Q5_high_vol=+0.151

**`combo_tri_median__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0`** (Lock IC=+0.0813, Sharpe=+0.6652)
- Admission: Train IC=+0.2343, Deflated=+0.2343, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.120 | 2017: +0.166 | 2018: +0.228 | 2019: +0.145 | 2020: +0.147 | 2021: +0.071 | 2022: +0.115 | 2023: +0.097 | 2024: +0.111 | 2025: +0.130 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.232 | 2016: +0.148 | 2017: +0.250 | 2018: +0.312 | 2019: +0.252 | 2020: +0.318 | 2021: +0.031 | 2022: +0.170 | 2023: +0.244 | 2024: +0.244 | 2025: -0.119 | 2026: -0.388
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.74
- Early IC=+0.1434, Recent IC=+0.1057, 1st-half IC=+0.1658, 2nd-half IC=+0.1105, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.013, Q3_mid=+0.133, Q4=+0.165, Q5_high_vol=+0.166

**`combo_rel_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1206, Sharpe=+0.6620)
- Admission: Train IC=+0.2294, Deflated=+0.2297, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.094 | 2017: +0.224 | 2018: +0.180 | 2019: +0.155 | 2020: +0.147 | 2021: +0.105 | 2022: +0.082 | 2023: +0.116 | 2024: +0.125 | 2025: +0.156 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.033 | 2017: +0.245 | 2018: +0.257 | 2019: +0.246 | 2020: +0.229 | 2021: +0.146 | 2022: +0.219 | 2023: +0.236 | 2024: +0.193 | 2025: +0.087 | 2026: -0.071
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.62
- Early IC=+0.1588, Recent IC=+0.0989, 1st-half IC=+0.1606, 2nd-half IC=+0.1107, Neg regimes=1/5
- Weak component: `demark_setup_reversal_early` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.010, Q3_mid=+0.141, Q4=+0.168, Q5_high_vol=+0.150

**`combo_rank_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0922, Sharpe=+0.6593)
- Admission: Train IC=+0.1583, Deflated=+0.1587, IR=0.56, Mono=0.68, p=0.0028, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.090 | 2017: +0.239 | 2018: +0.234 | 2019: +0.150 | 2020: +0.126 | 2021: +0.098 | 2022: +0.093 | 2023: +0.036 | 2024: +0.117 | 2025: +0.112 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.605 | 2016: -0.121 | 2017: +0.202 | 2018: +0.245 | 2019: +0.306 | 2020: +0.177 | 2021: +0.248 | 2022: +0.130 | 2023: +0.169 | 2024: +0.217 | 2025: +0.104 | 2026: -0.076
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.51, Recency ratio=0.39
- Early IC=+0.1609, Recent IC=+0.0632, 1st-half IC=+0.1717, 2nd-half IC=+0.0878, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.061, Q3_mid=+0.141, Q4=+0.174, Q5_high_vol=+0.154

**`combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0943, Sharpe=+0.6580)
- Admission: Train IC=+0.2055, Deflated=+0.2048, IR=0.52, Mono=0.69, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.119 | 2017: +0.121 | 2018: +0.159 | 2019: +0.097 | 2020: +0.097 | 2021: +0.025 | 2022: +0.154 | 2023: +0.090 | 2024: +0.103 | 2025: +0.093 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.377 | 2017: +0.216 | 2018: +0.137 | 2019: +0.181 | 2020: +0.126 | 2021: +0.107 | 2022: +0.164 | 2023: +0.128 | 2024: +0.236 | 2025: -0.002 | 2026: -0.189
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=1.01
- Early IC=+0.1216, Recent IC=+0.1223, 1st-half IC=+0.1257, 2nd-half IC=+0.0946, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.017, Q3_mid=+0.071, Q4=+0.123, Q5_high_vol=+0.165

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1253, Sharpe=+0.6575)
- Admission: Train IC=+0.2227, Deflated=+0.2222, IR=0.62, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.059 | 2017: +0.234 | 2018: +0.157 | 2019: +0.152 | 2020: +0.147 | 2021: +0.139 | 2022: +0.011 | 2023: +0.094 | 2024: +0.180 | 2025: +0.083 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.343 | 2016: +0.185 | 2017: +0.278 | 2018: +0.447 | 2019: +0.340 | 2020: +0.195 | 2021: +0.082 | 2022: +0.126 | 2023: +0.001 | 2024: +0.298 | 2025: -0.098 | 2026: +0.305
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.36
- Early IC=+0.1463, Recent IC=+0.0527, 1st-half IC=+0.1492, 2nd-half IC=+0.1003, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.019, Q3_mid=+0.137, Q4=+0.129, Q5_high_vol=+0.160

**`combo_min__first_bar_return__early_order_flow_imbalance`** (Lock IC=+0.0742, Sharpe=+0.6558)
- Admission: Train IC=+0.1969, Deflated=+0.1972, IR=0.61, Mono=0.72, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.157 | 2016: +0.003 | 2017: +0.137 | 2018: +0.161 | 2019: +0.159 | 2020: +0.060 | 2021: +0.158 | 2022: +0.124 | 2023: +0.075 | 2024: +0.118 | 2025: +0.102 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.020 | 2017: +0.320 | 2018: +0.414 | 2019: +0.238 | 2020: -0.015 | 2021: +0.249 | 2022: +0.253 | 2023: +0.115 | 2024: +0.323 | 2025: +0.248 | 2026: -0.096
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.90, Recency ratio=1.42
- Early IC=+0.0699, Recent IC=+0.0992, 1st-half IC=+0.1157, 2nd-half IC=+0.1043, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.015, Q3_mid=+0.094, Q4=+0.155, Q5_high_vol=+0.127

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1142, Sharpe=+0.6523)
- Admission: Train IC=+0.2331, Deflated=+0.2334, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.300 | 2016: +0.117 | 2017: +0.245 | 2018: +0.245 | 2019: +0.158 | 2020: +0.193 | 2021: +0.125 | 2022: +0.089 | 2023: +0.082 | 2024: +0.128 | 2025: +0.114 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.289 | 2016: +0.119 | 2017: +0.212 | 2018: +0.403 | 2019: +0.277 | 2020: +0.247 | 2021: +0.232 | 2022: +0.103 | 2023: +0.037 | 2024: +0.121 | 2025: +0.039 | 2026: +0.142
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.47
- Early IC=+0.1809, Recent IC=+0.0852, 1st-half IC=+0.1876, 2nd-half IC=+0.1242, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.216, Q2=-0.010, Q3_mid=+0.129, Q4=+0.179, Q5_high_vol=+0.218

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0998, Sharpe=+0.6467)
- Admission: Train IC=+0.1954, Deflated=+0.1949, IR=0.53, Mono=0.69, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.302 | 2016: +0.082 | 2017: +0.253 | 2018: +0.146 | 2019: +0.106 | 2020: +0.169 | 2021: +0.110 | 2022: +0.109 | 2023: +0.072 | 2024: +0.150 | 2025: +0.110 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.530 | 2016: +0.111 | 2017: +0.254 | 2018: +0.235 | 2019: +0.224 | 2020: +0.090 | 2021: +0.234 | 2022: +0.223 | 2023: +0.138 | 2024: +0.238 | 2025: -0.026 | 2026: -0.101
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.54
- Early IC=+0.1673, Recent IC=+0.0904, 1st-half IC=+0.1431, 2nd-half IC=+0.1167, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.021, Q3_mid=+0.133, Q4=+0.152, Q5_high_vol=+0.185

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__smooth_momentum_structure`** (Lock IC=+0.0994, Sharpe=+0.6449)
- Admission: Train IC=+0.2037, Deflated=+0.2045, IR=0.52, Mono=0.71, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.124 | 2017: +0.192 | 2018: +0.104 | 2019: +0.063 | 2020: +0.106 | 2021: +0.010 | 2022: +0.097 | 2023: +0.054 | 2024: +0.080 | 2025: +0.112 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.195 | 2016: +0.164 | 2017: +0.326 | 2018: +0.268 | 2019: +0.111 | 2020: +0.224 | 2021: +0.112 | 2022: +0.161 | 2023: +0.034 | 2024: +0.229 | 2025: +0.025 | 2026: +0.249
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.48
- Early IC=+0.1582, Recent IC=+0.0754, 1st-half IC=+0.1142, 2nd-half IC=+0.0738, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.022, Q3_mid=+0.066, Q4=+0.079, Q5_high_vol=+0.140

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0994, Sharpe=+0.6418)
- Admission: Train IC=+0.1739, Deflated=+0.1741, IR=0.73, Mono=0.74, p=0.0006, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.048 | 2017: +0.233 | 2018: +0.113 | 2019: +0.122 | 2020: +0.121 | 2021: +0.073 | 2022: +0.056 | 2023: +0.064 | 2024: +0.085 | 2025: +0.133 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.111 | 2017: +0.267 | 2018: +0.360 | 2019: +0.324 | 2020: +0.217 | 2021: +0.340 | 2022: +0.063 | 2023: +0.041 | 2024: +0.147 | 2025: +0.082 | 2026: +0.223
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.40
- Early IC=+0.1421, Recent IC=+0.0574, 1st-half IC=+0.1225, 2nd-half IC=+0.0694, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.059, Q3_mid=+0.115, Q4=+0.122, Q5_high_vol=+0.095

**`combo_tri_median__max_up_ret__smooth_momentum_structure__bar_ret_0`** (Lock IC=+0.0578, Sharpe=+0.6416)
- Admission: Train IC=+0.1801, Deflated=+0.1816, IR=0.45, Mono=0.66, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.129 | 2017: +0.159 | 2018: +0.191 | 2019: +0.076 | 2020: +0.109 | 2021: +0.111 | 2022: +0.111 | 2023: +0.075 | 2024: +0.085 | 2025: +0.125 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.069 | 2017: +0.239 | 2018: +0.238 | 2019: +0.132 | 2020: +0.256 | 2021: +0.213 | 2022: +0.092 | 2023: +0.101 | 2024: +0.198 | 2025: +0.217 | 2026: -0.298
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.65
- Early IC=+0.1436, Recent IC=+0.0930, 1st-half IC=+0.1301, 2nd-half IC=+0.1060, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.230, Q2=-0.015, Q3_mid=+0.074, Q4=+0.147, Q5_high_vol=+0.144

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1066, Sharpe=+0.6200)
- Admission: Train IC=+0.2031, Deflated=+0.2036, IR=0.42, Mono=0.66, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.130 | 2017: +0.209 | 2018: +0.236 | 2019: +0.147 | 2020: +0.133 | 2021: +0.118 | 2022: +0.087 | 2023: +0.087 | 2024: +0.132 | 2025: +0.113 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.147 | 2017: +0.225 | 2018: +0.406 | 2019: +0.123 | 2020: +0.276 | 2021: +0.103 | 2022: +0.055 | 2023: +0.152 | 2024: +0.156 | 2025: -0.023 | 2026: +0.122
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.51
- Early IC=+0.1695, Recent IC=+0.0872, 1st-half IC=+0.1744, 2nd-half IC=+0.1078, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.015, Q3_mid=+0.105, Q4=+0.152, Q5_high_vol=+0.182

**`combo_tri_mean__early_body_momentum__star50_limit_proximity_early__trend_day_regime_conviction`** (Lock IC=+0.0978, Sharpe=+0.6135)
- Admission: Train IC=+0.2121, Deflated=+0.2121, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.082 | 2017: +0.178 | 2018: +0.151 | 2019: +0.099 | 2020: +0.127 | 2021: +0.055 | 2022: +0.099 | 2023: +0.061 | 2024: +0.108 | 2025: +0.114 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.344 | 2016: +0.129 | 2017: +0.240 | 2018: +0.182 | 2019: +0.261 | 2020: +0.142 | 2021: +0.135 | 2022: +0.290 | 2023: +0.229 | 2024: +0.208 | 2025: +0.127 | 2026: -0.122
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.61
- Early IC=+0.1302, Recent IC=+0.0801, 1st-half IC=+0.1265, 2nd-half IC=+0.0866, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.007, Q3_mid=+0.088, Q4=+0.111, Q5_high_vol=+0.150

**`combo_mean__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0987, Sharpe=+0.6068)
- Admission: Train IC=+0.2019, Deflated=+0.2018, IR=0.56, Mono=0.69, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.099 | 2017: +0.226 | 2018: +0.232 | 2019: +0.144 | 2020: +0.147 | 2021: +0.137 | 2022: +0.070 | 2023: +0.092 | 2024: +0.137 | 2025: +0.110 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.579 | 2016: +0.003 | 2017: +0.197 | 2018: +0.170 | 2019: +0.354 | 2020: +0.085 | 2021: +0.440 | 2022: +0.118 | 2023: +0.085 | 2024: +0.224 | 2025: +0.148 | 2026: -0.049
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.50
- Early IC=+0.1624, Recent IC=+0.0809, 1st-half IC=+0.1739, 2nd-half IC=+0.1101, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.032, Q3_mid=+0.139, Q4=+0.185, Q5_high_vol=+0.187

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1193, Sharpe=+0.5966)
- Admission: Train IC=+0.2745, Deflated=+0.2746, IR=1.02, Mono=0.84, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.120 | 2017: +0.225 | 2018: +0.180 | 2019: +0.173 | 2020: +0.172 | 2021: +0.143 | 2022: +0.006 | 2023: +0.103 | 2024: +0.159 | 2025: +0.093 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.361 | 2016: +0.235 | 2017: +0.326 | 2018: +0.506 | 2019: +0.324 | 2020: +0.261 | 2021: +0.289 | 2022: +0.138 | 2023: +0.114 | 2024: +0.281 | 2025: -0.018 | 2026: +0.171
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.32
- Early IC=+0.1723, Recent IC=+0.0546, 1st-half IC=+0.1698, 2nd-half IC=+0.1121, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.033, Q3_mid=+0.133, Q4=+0.134, Q5_high_vol=+0.215

**`combo_mean__max_up_ret__max_down_ret`** (Lock IC=+0.0997, Sharpe=+0.5811)
- Admission: Train IC=+0.2057, Deflated=+0.2058, IR=0.64, Mono=0.72, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.066 | 2017: +0.238 | 2018: +0.208 | 2019: +0.116 | 2020: +0.134 | 2021: +0.111 | 2022: +0.104 | 2023: +0.094 | 2024: +0.159 | 2025: +0.107 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.369 | 2016: +0.212 | 2017: +0.322 | 2018: +0.292 | 2019: +0.175 | 2020: +0.130 | 2021: +0.318 | 2022: +0.136 | 2023: +0.259 | 2024: +0.293 | 2025: -0.032 | 2026: -0.164
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.65
- Early IC=+0.1520, Recent IC=+0.0989, 1st-half IC=+0.1435, 2nd-half IC=+0.1120, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.021, Q3_mid=+0.116, Q4=+0.136, Q5_high_vol=+0.189

**`combo_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1173, Sharpe=+0.5806)
- Admission: Train IC=+0.2258, Deflated=+0.2262, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.070 | 2017: +0.246 | 2018: +0.198 | 2019: +0.135 | 2020: +0.149 | 2021: +0.087 | 2022: +0.096 | 2023: +0.127 | 2024: +0.127 | 2025: +0.151 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.310 | 2016: -0.026 | 2017: +0.251 | 2018: +0.271 | 2019: +0.243 | 2020: +0.241 | 2021: +0.145 | 2022: +0.233 | 2023: +0.294 | 2024: +0.225 | 2025: +0.125 | 2026: -0.090
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.71
- Early IC=+0.1576, Recent IC=+0.1115, 1st-half IC=+0.1603, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.223, Q2=+0.003, Q3_mid=+0.144, Q4=+0.170, Q5_high_vol=+0.149

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1177, Sharpe=+0.5773)
- Admission: Train IC=+0.2364, Deflated=+0.2365, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.110 | 2017: +0.252 | 2018: +0.158 | 2019: +0.118 | 2020: +0.149 | 2021: +0.098 | 2022: +0.108 | 2023: +0.128 | 2024: +0.128 | 2025: +0.130 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.353 | 2017: +0.361 | 2018: +0.201 | 2019: +0.183 | 2020: +0.138 | 2021: +0.148 | 2022: +0.184 | 2023: +0.180 | 2024: +0.215 | 2025: -0.077 | 2026: -0.313
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.65
- Early IC=+0.1813, Recent IC=+0.1183, 1st-half IC=+0.1508, 2nd-half IC=+0.1251, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.236, Q2=+0.010, Q3_mid=+0.130, Q4=+0.129, Q5_high_vol=+0.188

**`combo_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0928, Sharpe=+0.5738)
- Admission: Train IC=+0.2153, Deflated=+0.2147, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.065 | 2017: +0.261 | 2018: +0.095 | 2019: +0.118 | 2020: +0.102 | 2021: +0.115 | 2022: +0.045 | 2023: +0.092 | 2024: +0.107 | 2025: +0.101 | 2026: +0.036
- Yearly Tail ICs:   2015: +0.101 | 2016: +0.162 | 2017: +0.335 | 2018: +0.336 | 2019: +0.267 | 2020: +0.129 | 2021: +0.292 | 2022: +0.122 | 2023: +0.125 | 2024: +0.139 | 2025: +0.148 | 2026: -0.210
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.42
- Early IC=+0.1631, Recent IC=+0.0684, 1st-half IC=+0.1214, 2nd-half IC=+0.0907, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.021, Q3_mid=+0.112, Q4=+0.120, Q5_high_vol=+0.133

**`combo_min__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0912, Sharpe=+0.5728)
- Admission: Train IC=+0.1920, Deflated=+0.1909, IR=0.57, Mono=0.68, p=0.0002, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.063 | 2017: +0.221 | 2018: +0.089 | 2019: +0.115 | 2020: +0.116 | 2021: +0.036 | 2022: +0.097 | 2023: +0.085 | 2024: +0.116 | 2025: +0.104 | 2026: +0.032
- Yearly Tail ICs:   2015: +0.348 | 2016: +0.040 | 2017: +0.319 | 2018: +0.143 | 2019: +0.238 | 2020: +0.113 | 2021: +0.331 | 2022: +0.339 | 2023: +0.096 | 2024: +0.152 | 2025: +0.274 | 2026: -0.045
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.64
- Early IC=+0.1420, Recent IC=+0.0911, 1st-half IC=+0.1194, 2nd-half IC=+0.0842, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.027, Q3_mid=+0.115, Q4=+0.114, Q5_high_vol=+0.117

**`open_to_current_return`** (Lock IC=+0.0774, Sharpe=+0.5603)
- Admission: Train IC=+0.1415, Deflated=+0.1415, IR=0.52, Mono=0.71, p=0.0068, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.73
- Early IC=+0.1305, Recent IC=+0.0947, 1st-half IC=+0.1067, 2nd-half IC=+0.0938, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.008, Q3_mid=+0.101, Q4=+0.092, Q5_high_vol=+0.146

**`combo_mean__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0841, Sharpe=+0.5556)
- Admission: Train IC=+0.2423, Deflated=+0.2424, IR=0.76, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.090 | 2017: +0.213 | 2018: +0.180 | 2019: +0.094 | 2020: +0.127 | 2021: +0.112 | 2022: +0.109 | 2023: +0.104 | 2024: +0.137 | 2025: +0.117 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.234 | 2017: +0.277 | 2018: +0.380 | 2019: +0.177 | 2020: +0.255 | 2021: +0.260 | 2022: +0.141 | 2023: +0.350 | 2024: +0.239 | 2025: -0.076 | 2026: -0.258
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.70
- Early IC=+0.1517, Recent IC=+0.1064, 1st-half IC=+0.1345, 2nd-half IC=+0.1163, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.211, Q2=-0.012, Q3_mid=+0.114, Q4=+0.112, Q5_high_vol=+0.193

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0705, Sharpe=+0.5535)
- Admission: Train IC=+0.1563, Deflated=+0.1574, IR=0.59, Mono=0.69, p=0.0034, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.106 | 2017: +0.094 | 2018: +0.063 | 2019: +0.021 | 2020: +0.060 | 2021: -0.058 | 2022: +0.109 | 2023: +0.049 | 2024: +0.036 | 2025: +0.096 | 2026: +0.066
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.142 | 2017: +0.152 | 2018: +0.190 | 2019: +0.057 | 2020: +0.133 | 2021: +0.201 | 2022: +0.261 | 2023: +0.071 | 2024: +0.181 | 2025: +0.112 | 2026: +0.044
- IC CV=0.93, Neg years (linear/tail)=1/0 of 8, Half ratio=0.63, Recency ratio=0.79
- Early IC=+0.0999, Recent IC=+0.0786, 1st-half IC=+0.0700, 2nd-half IC=+0.0439, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.120, Q2=-0.010, Q3_mid=+0.010, Q4=+0.049, Q5_high_vol=+0.093

**`combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0956, Sharpe=+0.5503)
- Admission: Train IC=+0.2056, Deflated=+0.2051, IR=0.73, Mono=0.74, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.068 | 2017: +0.261 | 2018: +0.097 | 2019: +0.119 | 2020: +0.106 | 2021: +0.117 | 2022: +0.038 | 2023: +0.082 | 2024: +0.103 | 2025: +0.105 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.157 | 2017: +0.294 | 2018: +0.388 | 2019: +0.249 | 2020: +0.130 | 2021: +0.347 | 2022: +0.070 | 2023: +0.147 | 2024: +0.134 | 2025: +0.106 | 2026: -0.122
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.35
- Early IC=+0.1649, Recent IC=+0.0583, 1st-half IC=+0.1239, 2nd-half IC=+0.0882, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.019, Q3_mid=+0.109, Q4=+0.119, Q5_high_vol=+0.136

**`combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`** (Lock IC=+0.0701, Sharpe=+0.5499)
- Admission: Train IC=+0.1651, Deflated=+0.1641, IR=0.35, Mono=0.65, p=0.0012, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.142 | 2016: +0.084 | 2017: +0.164 | 2018: +0.085 | 2019: +0.060 | 2020: +0.085 | 2021: +0.049 | 2022: +0.089 | 2023: +0.103 | 2024: +0.115 | 2025: +0.125 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.343 | 2016: +0.149 | 2017: +0.118 | 2018: +0.157 | 2019: +0.231 | 2020: +0.061 | 2021: +0.184 | 2022: +0.161 | 2023: +0.256 | 2024: +0.326 | 2025: -0.045 | 2026: +0.176
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.77
- Early IC=+0.1239, Recent IC=+0.0958, 1st-half IC=+0.0963, 2nd-half IC=+0.0837, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.028, Q3_mid=+0.118, Q4=+0.084, Q5_high_vol=+0.099

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1019, Sharpe=+0.5491)
- Admission: Train IC=+0.1679, Deflated=+0.1678, IR=0.66, Mono=0.72, p=0.0008, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.041 | 2017: +0.233 | 2018: +0.110 | 2019: +0.116 | 2020: +0.103 | 2021: +0.071 | 2022: +0.074 | 2023: +0.074 | 2024: +0.084 | 2025: +0.142 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.325 | 2016: +0.084 | 2017: +0.266 | 2018: +0.347 | 2019: +0.288 | 2020: +0.182 | 2021: +0.345 | 2022: +0.119 | 2023: +0.050 | 2024: +0.203 | 2025: +0.108 | 2026: +0.212
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.54
- Early IC=+0.1370, Recent IC=+0.0738, 1st-half IC=+0.1126, 2nd-half IC=+0.0725, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.046, Q3_mid=+0.113, Q4=+0.110, Q5_high_vol=+0.090

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1566, Sharpe=+0.5389)
- Admission: Train IC=+0.1738, Deflated=+0.1732, IR=0.41, Mono=0.66, p=0.0006, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.046 | 2017: +0.193 | 2018: +0.147 | 2019: +0.180 | 2020: +0.113 | 2021: +0.083 | 2022: +0.063 | 2023: +0.096 | 2024: +0.159 | 2025: +0.106 | 2026: +0.198
- Yearly Tail ICs:   2015: -0.019 | 2016: +0.052 | 2017: +0.182 | 2018: +0.211 | 2019: +0.382 | 2020: +0.184 | 2021: +0.145 | 2022: +0.176 | 2023: +0.051 | 2024: +0.225 | 2025: +0.105 | 2026: +0.332
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.67
- Early IC=+0.1197, Recent IC=+0.0799, 1st-half IC=+0.1493, 2nd-half IC=+0.0766, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.001, Q3_mid=+0.123, Q4=+0.094, Q5_high_vol=+0.156

**`combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0785, Sharpe=+0.5352)
- Admission: Train IC=+0.1871, Deflated=+0.1865, IR=0.49, Mono=0.65, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.030 | 2017: +0.240 | 2018: +0.135 | 2019: +0.127 | 2020: +0.076 | 2021: +0.069 | 2022: +0.045 | 2023: +0.092 | 2024: +0.101 | 2025: +0.120 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.162 | 2016: -0.016 | 2017: +0.166 | 2018: +0.295 | 2019: +0.320 | 2020: +0.039 | 2021: +0.229 | 2022: +0.178 | 2023: +0.195 | 2024: -0.014 | 2025: +0.449 | 2026: -0.123
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=0.54, Recency ratio=0.51
- Early IC=+0.1335, Recent IC=+0.0681, 1st-half IC=+0.1263, 2nd-half IC=+0.0683, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.043, Q3_mid=+0.088, Q4=+0.141, Q5_high_vol=+0.110

**`combo_min__close_vs_open_range__bar_body_rng_0`** (Lock IC=+0.0982, Sharpe=+0.5337)
- Admission: Train IC=+0.1796, Deflated=+0.1800, IR=0.53, Mono=0.69, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.081 | 2017: +0.198 | 2018: +0.170 | 2019: +0.106 | 2020: +0.065 | 2021: +0.081 | 2022: +0.036 | 2023: +0.082 | 2024: +0.128 | 2025: +0.134 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.172 | 2017: +0.154 | 2018: +0.240 | 2019: +0.264 | 2020: +0.155 | 2021: +0.150 | 2022: +0.121 | 2023: +0.109 | 2024: +0.119 | 2025: +0.230 | 2026: +0.312
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.47, Recency ratio=0.42
- Early IC=+0.1391, Recent IC=+0.0590, 1st-half IC=+0.1366, 2nd-half IC=+0.0637, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.185, Q2=-0.043, Q3_mid=+0.080, Q4=+0.144, Q5_high_vol=+0.123

**`combo_tri_median__max_up_ret__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0821, Sharpe=+0.5332)
- Admission: Train IC=+0.1350, Deflated=+0.1357, IR=0.53, Mono=0.70, p=0.0088, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.070 | 2017: +0.103 | 2018: +0.120 | 2019: +0.060 | 2020: +0.071 | 2021: +0.080 | 2022: +0.102 | 2023: +0.098 | 2024: +0.123 | 2025: +0.133 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.186 | 2016: +0.178 | 2017: +0.134 | 2018: +0.185 | 2019: +0.148 | 2020: +0.057 | 2021: +0.303 | 2022: +0.086 | 2023: +0.051 | 2024: +0.264 | 2025: +0.090 | 2026: -0.286
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=1.10, Recency ratio=1.16
- Early IC=+0.0865, Recent IC=+0.1001, 1st-half IC=+0.0832, 2nd-half IC=+0.0916, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.158, Q2=-0.039, Q3_mid=+0.096, Q4=+0.102, Q5_high_vol=+0.120

**`opening_drive_thrust_ratio`** (Lock IC=+0.0962, Sharpe=+0.5296)
- Admission: Train IC=+0.1931, Deflated=+0.1922, IR=0.63, Mono=0.77, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069 | 2023: +0.102 | 2024: +0.152 | 2025: +0.088 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.517 | 2016: +0.047 | 2017: +0.205 | 2018: +0.244 | 2019: +0.347 | 2020: +0.069 | 2021: +0.321 | 2022: +0.278 | 2023: +0.019 | 2024: +0.151 | 2025: +0.052 | 2026: -0.026
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.57
- Early IC=+0.1495, Recent IC=+0.0856, 1st-half IC=+0.1601, 2nd-half IC=+0.1219, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.016, Q3_mid=+0.149, Q4=+0.151, Q5_high_vol=+0.214

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0678, Sharpe=+0.5233)
- Admission: Train IC=+0.2424, Deflated=+0.2435, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.094 | 2017: +0.216 | 2018: +0.244 | 2019: +0.125 | 2020: +0.121 | 2021: +0.117 | 2022: +0.089 | 2023: +0.107 | 2024: +0.098 | 2025: +0.080 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.329 | 2016: +0.062 | 2017: +0.336 | 2018: +0.428 | 2019: +0.150 | 2020: +0.151 | 2021: +0.212 | 2022: +0.068 | 2023: +0.243 | 2024: +0.069 | 2025: +0.111 | 2026: +0.038
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.63
- Early IC=+0.1551, Recent IC=+0.0982, 1st-half IC=+0.1629, 2nd-half IC=+0.1081, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.030, Q3_mid=+0.117, Q4=+0.182, Q5_high_vol=+0.167

**`combo_min__net_volume_flow__max_down_ret`** (Lock IC=+0.1016, Sharpe=+0.5225)
- Admission: Train IC=+0.1787, Deflated=+0.1786, IR=0.58, Mono=0.70, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.061 | 2017: +0.194 | 2018: +0.133 | 2019: +0.100 | 2020: +0.132 | 2021: +0.081 | 2022: +0.097 | 2023: +0.080 | 2024: +0.114 | 2025: +0.137 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.304 | 2016: -0.077 | 2017: +0.210 | 2018: +0.115 | 2019: +0.300 | 2020: +0.222 | 2021: +0.286 | 2022: +0.252 | 2023: +0.211 | 2024: +0.297 | 2025: +0.178 | 2026: +0.056
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.69
- Early IC=+0.1274, Recent IC=+0.0884, 1st-half IC=+0.1197, 2nd-half IC=+0.0935, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.039, Q3_mid=+0.121, Q4=+0.130, Q5_high_vol=+0.121

**`combo_mean__rsi_opening__bar_body_rng_0`** (Lock IC=+0.0951, Sharpe=+0.5082)
- Admission: Train IC=+0.2031, Deflated=+0.2033, IR=0.55, Mono=0.73, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.092 | 2017: +0.218 | 2018: +0.188 | 2019: +0.113 | 2020: +0.105 | 2021: +0.102 | 2022: +0.089 | 2023: +0.078 | 2024: +0.134 | 2025: +0.136 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.443 | 2016: +0.013 | 2017: +0.176 | 2018: +0.311 | 2019: +0.209 | 2020: +0.155 | 2021: +0.137 | 2022: +0.362 | 2023: +0.272 | 2024: +0.299 | 2025: +0.146 | 2026: -0.119
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.54
- Early IC=+0.1553, Recent IC=+0.0831, 1st-half IC=+0.1502, 2nd-half IC=+0.0931, Neg regimes=1/5
- Weak component: `rsi_opening` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.024, Q3_mid=+0.115, Q4=+0.155, Q5_high_vol=+0.145

**`combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction`** (Lock IC=+0.0597, Sharpe=+0.5081)
- Admission: Train IC=+0.1663, Deflated=+0.1647, IR=0.60, Mono=0.72, p=0.0012, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.031 | 2017: +0.155 | 2018: +0.069 | 2019: +0.021 | 2020: +0.096 | 2021: +0.031 | 2022: +0.027 | 2023: +0.122 | 2024: +0.087 | 2025: +0.124 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.109 | 2016: +0.115 | 2017: +0.277 | 2018: +0.155 | 2019: +0.136 | 2020: +0.126 | 2021: +0.260 | 2022: +0.189 | 2023: +0.152 | 2024: +0.220 | 2025: +0.205 | 2026: -0.268
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=1.16, Recency ratio=0.84
- Early IC=+0.0917, Recent IC=+0.0768, 1st-half IC=+0.0643, 2nd-half IC=+0.0745, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.19)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.002, Q3_mid=+0.080, Q4=+0.065, Q5_high_vol=+0.075

**`combo_sig_product__max_up_ret__net_volume_flow`** (Lock IC=+0.0933, Sharpe=+0.5076)
- Admission: Train IC=+0.2285, Deflated=+0.2294, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.151 | 2017: +0.118 | 2018: +0.175 | 2019: +0.064 | 2020: +0.115 | 2021: +0.090 | 2022: +0.074 | 2023: +0.112 | 2024: +0.157 | 2025: +0.078 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.388 | 2016: +0.140 | 2017: +0.185 | 2018: +0.242 | 2019: +0.165 | 2020: +0.276 | 2021: +0.195 | 2022: +0.188 | 2023: +0.350 | 2024: +0.276 | 2025: +0.014 | 2026: -0.115
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.69
- Early IC=+0.1348, Recent IC=+0.0933, 1st-half IC=+0.1225, 2nd-half IC=+0.0970, Neg regimes=1/5
- Weak component: `net_volume_flow` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.170, Q2=-0.021, Q3_mid=+0.093, Q4=+0.093, Q5_high_vol=+0.180

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0955, Sharpe=+0.5066)
- Admission: Train IC=+0.2717, Deflated=+0.2718, IR=0.76, Mono=0.74, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.112 | 2017: +0.195 | 2018: +0.204 | 2019: +0.085 | 2020: +0.161 | 2021: +0.081 | 2022: +0.116 | 2023: +0.089 | 2024: +0.085 | 2025: +0.134 | 2026: +0.033
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.271 | 2017: +0.313 | 2018: +0.362 | 2019: +0.228 | 2020: +0.237 | 2021: +0.124 | 2022: +0.264 | 2023: +0.107 | 2024: +0.219 | 2025: -0.037 | 2026: -0.011
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.67
- Early IC=+0.1537, Recent IC=+0.1028, 1st-half IC=+0.1455, 2nd-half IC=+0.1157, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.002, Q3_mid=+0.093, Q4=+0.129, Q5_high_vol=+0.217

**`combo_sig_product__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0599, Sharpe=+0.5033)
- Admission: Train IC=+0.1737, Deflated=+0.1729, IR=0.55, Mono=0.69, p=0.0006, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.134 | 2017: +0.106 | 2018: +0.121 | 2019: +0.052 | 2020: +0.098 | 2021: +0.047 | 2022: +0.130 | 2023: +0.147 | 2024: +0.095 | 2025: +0.126 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.166 | 2016: +0.178 | 2017: +0.093 | 2018: +0.131 | 2019: +0.171 | 2020: +0.107 | 2021: +0.163 | 2022: +0.184 | 2023: +0.274 | 2024: +0.283 | 2025: +0.278 | 2026: -0.258
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.16
- Early IC=+0.1200, Recent IC=+0.1387, 1st-half IC=+0.0999, 2nd-half IC=+0.0995, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.051, Q3_mid=+0.039, Q4=+0.161, Q5_high_vol=+0.100

**`combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`** (Lock IC=+0.0662, Sharpe=+0.5029)
- Admission: Train IC=+0.1665, Deflated=+0.1655, IR=0.36, Mono=0.66, p=0.0012, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.081 | 2017: +0.161 | 2018: +0.091 | 2019: +0.059 | 2020: +0.091 | 2021: +0.058 | 2022: +0.094 | 2023: +0.099 | 2024: +0.106 | 2025: +0.127 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.359 | 2016: +0.147 | 2017: +0.132 | 2018: +0.158 | 2019: +0.235 | 2020: +0.064 | 2021: +0.180 | 2022: +0.169 | 2023: +0.263 | 2024: +0.323 | 2025: -0.045 | 2026: +0.192
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.80
- Early IC=+0.1207, Recent IC=+0.0967, 1st-half IC=+0.0956, 2nd-half IC=+0.0883, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.030, Q3_mid=+0.123, Q4=+0.090, Q5_high_vol=+0.105

**`combo_max__max_up_ret__max_down_ret`** (Lock IC=+0.0839, Sharpe=+0.4972)
- Admission: Train IC=+0.2069, Deflated=+0.2068, IR=0.74, Mono=0.76, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.085 | 2017: +0.239 | 2018: +0.252 | 2019: +0.115 | 2020: +0.138 | 2021: +0.114 | 2022: +0.084 | 2023: +0.065 | 2024: +0.137 | 2025: +0.097 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.264 | 2016: +0.240 | 2017: +0.303 | 2018: +0.364 | 2019: +0.175 | 2020: +0.178 | 2021: +0.259 | 2022: +0.125 | 2023: +0.242 | 2024: +0.255 | 2025: -0.111 | 2026: -0.297
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.46
- Early IC=+0.1619, Recent IC=+0.0746, 1st-half IC=+0.1661, 2nd-half IC=+0.1008, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.046, Q3_mid=+0.118, Q4=+0.125, Q5_high_vol=+0.219

**`combo_min__first_bar_return__close_vs_open_range`** (Lock IC=+0.1023, Sharpe=+0.4955)
- Admission: Train IC=+0.1848, Deflated=+0.1852, IR=0.62, Mono=0.71, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.084 | 2017: +0.185 | 2018: +0.172 | 2019: +0.117 | 2020: +0.065 | 2021: +0.057 | 2022: +0.046 | 2023: +0.071 | 2024: +0.132 | 2025: +0.140 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.434 | 2016: +0.135 | 2017: +0.273 | 2018: +0.296 | 2019: +0.187 | 2020: +0.085 | 2021: +0.270 | 2022: +0.191 | 2023: +0.134 | 2024: +0.228 | 2025: +0.195 | 2026: +0.285
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.43, Recency ratio=0.43
- Early IC=+0.1346, Recent IC=+0.0584, 1st-half IC=+0.1367, 2nd-half IC=+0.0584, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.052, Q3_mid=+0.081, Q4=+0.118, Q5_high_vol=+0.127

**`combo_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0842, Sharpe=+0.4912)
- Admission: Train IC=+0.2593, Deflated=+0.2590, IR=0.88, Mono=0.78, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.106 | 2017: +0.199 | 2018: +0.220 | 2019: +0.148 | 2020: +0.158 | 2021: +0.139 | 2022: +0.066 | 2023: +0.102 | 2024: +0.127 | 2025: +0.022 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.207 | 2017: +0.415 | 2018: +0.372 | 2019: +0.320 | 2020: +0.121 | 2021: +0.258 | 2022: +0.165 | 2023: +0.197 | 2024: +0.033 | 2025: -0.045 | 2026: +0.030
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.55
- Early IC=+0.1523, Recent IC=+0.0840, 1st-half IC=+0.1638, 2nd-half IC=+0.1167, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.013, Q3_mid=+0.104, Q4=+0.175, Q5_high_vol=+0.219

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0857, Sharpe=+0.4882)
- Admission: Train IC=+0.2493, Deflated=+0.2487, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.104 | 2017: +0.143 | 2018: +0.283 | 2019: +0.175 | 2020: +0.174 | 2021: +0.171 | 2022: +0.053 | 2023: +0.092 | 2024: +0.160 | 2025: +0.060 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.093 | 2017: +0.306 | 2018: +0.593 | 2019: +0.226 | 2020: +0.024 | 2021: +0.311 | 2022: +0.170 | 2023: +0.069 | 2024: +0.344 | 2025: +0.147 | 2026: -0.120
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.59
- Early IC=+0.1237, Recent IC=+0.0729, 1st-half IC=+0.1779, 2nd-half IC=+0.1232, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.003, Q3_mid=+0.146, Q4=+0.165, Q5_high_vol=+0.238

**`combo_min__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0683, Sharpe=+0.4863)
- Admission: Train IC=+0.1673, Deflated=+0.1674, IR=0.56, Mono=0.69, p=0.0010, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.020 | 2017: +0.158 | 2018: +0.118 | 2019: +0.128 | 2020: +0.093 | 2021: +0.121 | 2022: +0.150 | 2023: +0.077 | 2024: +0.109 | 2025: +0.080 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.323 | 2016: -0.033 | 2017: +0.192 | 2018: +0.154 | 2019: +0.235 | 2020: +0.162 | 2021: +0.322 | 2022: +0.286 | 2023: +0.121 | 2024: +0.302 | 2025: +0.157 | 2026: -0.071
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=1.03, Recency ratio=1.28
- Early IC=+0.0891, Recent IC=+0.1137, 1st-half IC=+0.1042, 2nd-half IC=+0.1074, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.014, Q3_mid=+0.101, Q4=+0.130, Q5_high_vol=+0.129

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0991, Sharpe=+0.4835)
- Admission: Train IC=+0.2612, Deflated=+0.2604, IR=0.89, Mono=0.82, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.056 | 2017: +0.164 | 2018: +0.246 | 2019: +0.173 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145 | 2025: +0.096 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.054 | 2017: +0.194 | 2018: +0.413 | 2019: +0.231 | 2020: +0.221 | 2021: +0.335 | 2022: +0.237 | 2023: +0.314 | 2024: +0.298 | 2025: +0.095 | 2026: -0.350
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.75
- Early IC=+0.1100, Recent IC=+0.0820, 1st-half IC=+0.1649, 2nd-half IC=+0.1118, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.169, Q2=-0.006, Q3_mid=+0.147, Q4=+0.167, Q5_high_vol=+0.197

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.1043, Sharpe=+0.4791)
- Admission: Train IC=+0.2511, Deflated=+0.2517, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.138 | 2017: +0.219 | 2018: +0.249 | 2019: +0.140 | 2020: +0.163 | 2021: +0.123 | 2022: +0.105 | 2023: +0.083 | 2024: +0.117 | 2025: +0.108 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.331 | 2016: +0.201 | 2017: +0.174 | 2018: +0.443 | 2019: +0.175 | 2020: +0.247 | 2021: +0.231 | 2022: +0.118 | 2023: +0.046 | 2024: +0.107 | 2025: +0.037 | 2026: +0.127
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.53
- Early IC=+0.1786, Recent IC=+0.0941, 1st-half IC=+0.1759, 2nd-half IC=+0.1223, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.231, Q2=-0.005, Q3_mid=+0.094, Q4=+0.177, Q5_high_vol=+0.224

**`combo_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1149, Sharpe=+0.4770)
- Admission: Train IC=+0.2279, Deflated=+0.2277, IR=0.59, Mono=0.68, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.086 | 2017: +0.249 | 2018: +0.189 | 2019: +0.124 | 2020: +0.168 | 2021: +0.092 | 2022: +0.119 | 2023: +0.133 | 2024: +0.120 | 2025: +0.141 | 2026: +0.026
- Yearly Tail ICs:   2015: +0.316 | 2016: +0.305 | 2017: +0.347 | 2018: +0.234 | 2019: +0.187 | 2020: +0.163 | 2021: +0.146 | 2022: +0.176 | 2023: +0.118 | 2024: +0.187 | 2025: -0.032 | 2026: -0.291
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.75
- Early IC=+0.1674, Recent IC=+0.1262, 1st-half IC=+0.1529, 2nd-half IC=+0.1334, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.226, Q2=+0.014, Q3_mid=+0.135, Q4=+0.144, Q5_high_vol=+0.206

**`combo_clamp_diff__bar_ret_0__body_size_progression`** (Lock IC=+0.0778, Sharpe=+0.4715)
- Admission: Train IC=+0.2421, Deflated=+0.2423, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.065 | 2017: +0.168 | 2018: +0.233 | 2019: +0.209 | 2020: +0.121 | 2021: +0.101 | 2022: +0.063 | 2023: +0.072 | 2024: +0.105 | 2025: +0.037 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.352 | 2016: +0.024 | 2017: +0.445 | 2018: +0.410 | 2019: +0.325 | 2020: +0.093 | 2021: +0.084 | 2022: +0.108 | 2023: +0.102 | 2024: +0.183 | 2025: +0.060 | 2026: -0.096
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.58
- Early IC=+0.1162, Recent IC=+0.0673, 1st-half IC=+0.1694, 2nd-half IC=+0.0868, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.032, Q3_mid=+0.106, Q4=+0.199, Q5_high_vol=+0.163

**`combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction`** (Lock IC=+0.0934, Sharpe=+0.4700)
- Admission: Train IC=+0.1982, Deflated=+0.1978, IR=0.47, Mono=0.70, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.061 | 2017: +0.194 | 2018: +0.121 | 2019: +0.079 | 2020: +0.092 | 2021: +0.068 | 2022: +0.090 | 2023: +0.090 | 2024: +0.138 | 2025: +0.136 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.342 | 2016: +0.160 | 2017: +0.192 | 2018: +0.142 | 2019: +0.188 | 2020: +0.158 | 2021: +0.109 | 2022: +0.352 | 2023: +0.208 | 2024: +0.342 | 2025: +0.126 | 2026: +0.037
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.71
- Early IC=+0.1276, Recent IC=+0.0900, 1st-half IC=+0.1091, 2nd-half IC=+0.0848, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.036, Q3_mid=+0.106, Q4=+0.089, Q5_high_vol=+0.144

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0836, Sharpe=+0.4618)
- Admission: Train IC=+0.2518, Deflated=+0.2523, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.262 | 2016: +0.141 | 2017: +0.199 | 2018: +0.248 | 2019: +0.127 | 2020: +0.115 | 2021: +0.133 | 2022: +0.091 | 2023: +0.095 | 2024: +0.137 | 2025: +0.096 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.175 | 2017: +0.342 | 2018: +0.474 | 2019: +0.112 | 2020: +0.190 | 2021: +0.330 | 2022: +0.128 | 2023: +0.201 | 2024: +0.180 | 2025: +0.011 | 2026: -0.260
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.55
- Early IC=+0.1696, Recent IC=+0.0933, 1st-half IC=+0.1749, 2nd-half IC=+0.1115, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.203, Q2=-0.029, Q3_mid=+0.110, Q4=+0.179, Q5_high_vol=+0.205

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum`** (Lock IC=+0.0797, Sharpe=+0.4571)
- Admission: Train IC=+0.2340, Deflated=+0.2337, IR=0.80, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.109 | 2017: +0.211 | 2018: +0.209 | 2019: +0.087 | 2020: +0.170 | 2021: +0.109 | 2022: +0.129 | 2023: +0.079 | 2024: +0.144 | 2025: +0.079 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.268 | 2017: +0.348 | 2018: +0.333 | 2019: +0.081 | 2020: +0.206 | 2021: +0.187 | 2022: +0.152 | 2023: +0.188 | 2024: +0.245 | 2025: -0.177 | 2026: -0.296
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.65
- Early IC=+0.1600, Recent IC=+0.1041, 1st-half IC=+0.1550, 2nd-half IC=+0.1255, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.016, Q3_mid=+0.119, Q4=+0.166, Q5_high_vol=+0.209

**`combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0835, Sharpe=+0.4536)
- Admission: Train IC=+0.2263, Deflated=+0.2264, IR=0.55, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.067 | 2017: +0.198 | 2018: +0.174 | 2019: +0.078 | 2020: +0.112 | 2021: +0.085 | 2022: +0.091 | 2023: +0.087 | 2024: +0.126 | 2025: +0.134 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.003 | 2017: +0.231 | 2018: +0.336 | 2019: +0.186 | 2020: +0.151 | 2021: +0.296 | 2022: +0.275 | 2023: +0.273 | 2024: +0.284 | 2025: +0.189 | 2026: -0.267
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.67
- Early IC=+0.1322, Recent IC=+0.0888, 1st-half IC=+0.1261, 2nd-half IC=+0.0936, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.023, Q3_mid=+0.112, Q4=+0.122, Q5_high_vol=+0.145

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0802, Sharpe=+0.4497)
- Admission: Train IC=+0.2342, Deflated=+0.2348, IR=0.52, Mono=0.67, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.152 | 2017: +0.098 | 2018: +0.140 | 2019: +0.092 | 2020: +0.116 | 2021: +0.086 | 2022: +0.083 | 2023: +0.138 | 2024: +0.138 | 2025: +0.086 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.072 | 2017: +0.261 | 2018: +0.219 | 2019: +0.371 | 2020: +0.226 | 2021: +0.253 | 2022: +0.148 | 2023: +0.344 | 2024: +0.228 | 2025: -0.048 | 2026: -0.001
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.88
- Early IC=+0.1249, Recent IC=+0.1103, 1st-half IC=+0.1191, 2nd-half IC=+0.1052, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.004, Q3_mid=+0.075, Q4=+0.092, Q5_high_vol=+0.208

**`combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0774, Sharpe=+0.4480)
- Admission: Train IC=+0.2299, Deflated=+0.2295, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.066 | 2017: +0.223 | 2018: +0.174 | 2019: +0.103 | 2020: +0.152 | 2021: +0.055 | 2022: +0.112 | 2023: +0.092 | 2024: +0.111 | 2025: +0.112 | 2026: -0.043
- Yearly Tail ICs:   2015: +0.381 | 2016: +0.107 | 2017: +0.240 | 2018: +0.244 | 2019: +0.166 | 2020: +0.274 | 2021: +0.175 | 2022: +0.245 | 2023: +0.334 | 2024: +0.276 | 2025: +0.032 | 2026: -0.115
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.70
- Early IC=+0.1448, Recent IC=+0.1020, 1st-half IC=+0.1397, 2nd-half IC=+0.1045, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.183, Q2=-0.005, Q3_mid=+0.143, Q4=+0.127, Q5_high_vol=+0.153

**`combo_rank_min__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0898, Sharpe=+0.4472)
- Admission: Train IC=+0.1951, Deflated=+0.1943, IR=0.59, Mono=0.72, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.069 | 2017: +0.241 | 2018: +0.095 | 2019: +0.122 | 2020: +0.124 | 2021: +0.038 | 2022: +0.090 | 2023: +0.074 | 2024: +0.114 | 2025: +0.102 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.318 | 2016: +0.073 | 2017: +0.320 | 2018: +0.161 | 2019: +0.238 | 2020: +0.140 | 2021: +0.362 | 2022: +0.359 | 2023: +0.079 | 2024: +0.088 | 2025: +0.236 | 2026: -0.234
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.51
- Early IC=+0.1565, Recent IC=+0.0799, 1st-half IC=+0.1277, 2nd-half IC=+0.0802, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.050, Q3_mid=+0.132, Q4=+0.128, Q5_high_vol=+0.106

**`combo_rel_diff__first_bar_return__body_size_progression`** (Lock IC=+0.0690, Sharpe=+0.4411)
- Admission: Train IC=+0.1720, Deflated=+0.1725, IR=0.49, Mono=0.67, p=0.0006, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.061 | 2017: +0.176 | 2018: +0.212 | 2019: +0.192 | 2020: +0.119 | 2021: +0.114 | 2022: +0.053 | 2023: +0.068 | 2024: +0.092 | 2025: +0.033 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.268 | 2016: -0.094 | 2017: +0.368 | 2018: +0.368 | 2019: +0.117 | 2020: +0.189 | 2021: +0.204 | 2022: +0.078 | 2023: +0.241 | 2024: +0.161 | 2025: -0.027 | 2026: +0.046
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.51
- Early IC=+0.1184, Recent IC=+0.0610, 1st-half IC=+0.1613, 2nd-half IC=+0.0851, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.170, Q2=-0.046, Q3_mid=+0.090, Q4=+0.202, Q5_high_vol=+0.156

**`combo_min__first_bar_return__vwap_close_divergence_trend`** (Lock IC=+0.0838, Sharpe=+0.4349)
- Admission: Train IC=+0.1884, Deflated=+0.1878, IR=0.40, Mono=0.65, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.033 | 2017: +0.221 | 2018: +0.150 | 2019: +0.153 | 2020: +0.072 | 2021: +0.055 | 2022: +0.038 | 2023: +0.054 | 2024: +0.098 | 2025: +0.118 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.068 | 2017: +0.225 | 2018: +0.280 | 2019: +0.304 | 2020: +0.038 | 2021: +0.193 | 2022: +0.230 | 2023: +0.059 | 2024: +0.105 | 2025: +0.347 | 2026: -0.072
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.36
- Early IC=+0.1270, Recent IC=+0.0462, 1st-half IC=+0.1363, 2nd-half IC=+0.0555, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.057, Q3_mid=+0.084, Q4=+0.139, Q5_high_vol=+0.111

**`combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0955, Sharpe=+0.4321)
- Admission: Train IC=+0.2204, Deflated=+0.2203, IR=0.58, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.077 | 2017: +0.239 | 2018: +0.224 | 2019: +0.131 | 2020: +0.141 | 2021: +0.117 | 2022: +0.095 | 2023: +0.092 | 2024: +0.154 | 2025: +0.110 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.359 | 2016: -0.003 | 2017: +0.226 | 2018: +0.387 | 2019: +0.218 | 2020: +0.206 | 2021: +0.305 | 2022: +0.230 | 2023: +0.254 | 2024: +0.259 | 2025: +0.079 | 2026: -0.283
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.59
- Early IC=+0.1580, Recent IC=+0.0936, 1st-half IC=+0.1640, 2nd-half IC=+0.1128, Neg regimes=1/5
- Weak component: `trend_day_regime_conviction` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.017, Q3_mid=+0.145, Q4=+0.148, Q5_high_vol=+0.181

**`combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0`** (Lock IC=+0.0945, Sharpe=+0.4270)
- Admission: Train IC=+0.2252, Deflated=+0.2255, IR=0.70, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.078 | 2017: +0.183 | 2018: +0.188 | 2019: +0.134 | 2020: +0.103 | 2021: +0.111 | 2022: +0.110 | 2023: +0.092 | 2024: +0.129 | 2025: +0.126 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.376 | 2016: +0.000 | 2017: +0.211 | 2018: +0.419 | 2019: +0.159 | 2020: +0.098 | 2021: +0.244 | 2022: +0.229 | 2023: +0.271 | 2024: +0.309 | 2025: +0.112 | 2026: -0.005
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.77
- Early IC=+0.1304, Recent IC=+0.1009, 1st-half IC=+0.1391, 2nd-half IC=+0.1054, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.023, Q3_mid=+0.115, Q4=+0.151, Q5_high_vol=+0.147

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0949, Sharpe=+0.4145)
- Admission: Train IC=+0.2494, Deflated=+0.2489, IR=0.89, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.101 | 2017: +0.206 | 2018: +0.217 | 2019: +0.146 | 2020: +0.152 | 2021: +0.126 | 2022: +0.061 | 2023: +0.119 | 2024: +0.156 | 2025: +0.095 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.515 | 2016: +0.270 | 2017: +0.341 | 2018: +0.367 | 2019: +0.206 | 2020: +0.182 | 2021: +0.279 | 2022: +0.210 | 2023: +0.221 | 2024: +0.183 | 2025: -0.133 | 2026: -0.059
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.59
- Early IC=+0.1535, Recent IC=+0.0899, 1st-half IC=+0.1552, 2nd-half IC=+0.1203, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.022, Q3_mid=+0.151, Q4=+0.121, Q5_high_vol=+0.230

**`combo_rank_max__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0915, Sharpe=+0.4102)
- Admission: Train IC=+0.2266, Deflated=+0.2259, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.084 | 2017: +0.219 | 2018: +0.152 | 2019: +0.083 | 2020: +0.137 | 2021: +0.098 | 2022: +0.107 | 2023: +0.073 | 2024: +0.151 | 2025: +0.120 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.482 | 2016: +0.207 | 2017: +0.388 | 2018: +0.181 | 2019: +0.287 | 2020: +0.206 | 2021: +0.232 | 2022: +0.306 | 2023: +0.214 | 2024: +0.288 | 2025: +0.067 | 2026: -0.136
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.59
- Early IC=+0.1520, Recent IC=+0.0901, 1st-half IC=+0.1366, 2nd-half IC=+0.1032, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.023, Q3_mid=+0.117, Q4=+0.153, Q5_high_vol=+0.157

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0889, Sharpe=+0.4004)
- Admission: Train IC=+0.2615, Deflated=+0.2607, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.046 | 2017: +0.160 | 2018: +0.221 | 2019: +0.173 | 2020: +0.158 | 2021: +0.162 | 2022: +0.052 | 2023: +0.086 | 2024: +0.126 | 2025: +0.097 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.028 | 2017: +0.191 | 2018: +0.386 | 2019: +0.254 | 2020: +0.224 | 2021: +0.331 | 2022: +0.238 | 2023: +0.306 | 2024: +0.297 | 2025: +0.090 | 2026: -0.354
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.67
- Early IC=+0.1030, Recent IC=+0.0688, 1st-half IC=+0.1550, 2nd-half IC=+0.1081, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.013, Q3_mid=+0.142, Q4=+0.164, Q5_high_vol=+0.182

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1128, Sharpe=+0.4001)
- Admission: Train IC=+0.2549, Deflated=+0.2538, IR=0.86, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.087 | 2017: +0.209 | 2018: +0.191 | 2019: +0.152 | 2020: +0.159 | 2021: +0.119 | 2022: +0.101 | 2023: +0.114 | 2024: +0.156 | 2025: +0.139 | 2026: -0.005
- Yearly Tail ICs:   2015: +0.413 | 2016: +0.300 | 2017: +0.292 | 2018: +0.361 | 2019: +0.203 | 2020: +0.269 | 2021: +0.222 | 2022: +0.246 | 2023: +0.160 | 2024: +0.269 | 2025: +0.021 | 2026: -0.201
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.72
- Early IC=+0.1484, Recent IC=+0.1073, 1st-half IC=+0.1564, 2nd-half IC=+0.1246, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.214, Q2=-0.007, Q3_mid=+0.154, Q4=+0.134, Q5_high_vol=+0.207

**`combo_rank_max__early_body_momentum__max_down_ret`** (Lock IC=+0.0881, Sharpe=+0.3895)
- Admission: Train IC=+0.1738, Deflated=+0.1735, IR=0.48, Mono=0.68, p=0.0006, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.047 | 2017: +0.196 | 2018: +0.163 | 2019: +0.093 | 2020: +0.102 | 2021: +0.073 | 2022: +0.075 | 2023: +0.042 | 2024: +0.131 | 2025: +0.167 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.058 | 2017: +0.278 | 2018: +0.099 | 2019: +0.329 | 2020: +0.051 | 2021: +0.261 | 2022: +0.263 | 2023: +0.160 | 2024: +0.238 | 2025: +0.295 | 2026: -0.085
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.49
- Early IC=+0.1205, Recent IC=+0.0593, 1st-half IC=+0.1256, 2nd-half IC=+0.0695, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.029, Q3_mid=+0.118, Q4=+0.127, Q5_high_vol=+0.111

**`combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0`** (Lock IC=+0.0963, Sharpe=+0.3889)
- Admission: Train IC=+0.2344, Deflated=+0.2341, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.066 | 2017: +0.190 | 2018: +0.223 | 2019: +0.136 | 2020: +0.115 | 2021: +0.110 | 2022: +0.080 | 2023: +0.085 | 2024: +0.127 | 2025: +0.120 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.350 | 2016: -0.006 | 2017: +0.323 | 2018: +0.395 | 2019: +0.178 | 2020: +0.127 | 2021: +0.344 | 2022: +0.278 | 2023: +0.267 | 2024: +0.318 | 2025: +0.034 | 2026: -0.100
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.65
- Early IC=+0.1278, Recent IC=+0.0825, 1st-half IC=+0.1527, 2nd-half IC=+0.0984, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.023, Q3_mid=+0.132, Q4=+0.150, Q5_high_vol=+0.162

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0908, Sharpe=+0.3829)
- Admission: Train IC=+0.1986, Deflated=+0.1988, IR=0.50, Mono=0.68, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.087 | 2017: +0.228 | 2018: +0.163 | 2019: +0.092 | 2020: +0.125 | 2021: +0.121 | 2022: +0.101 | 2023: +0.097 | 2024: +0.128 | 2025: +0.108 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.522 | 2016: +0.226 | 2017: +0.282 | 2018: +0.204 | 2019: +0.163 | 2020: +0.144 | 2021: +0.346 | 2022: +0.126 | 2023: +0.178 | 2024: +0.200 | 2025: +0.045 | 2026: -0.110
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.63
- Early IC=+0.1573, Recent IC=+0.0992, 1st-half IC=+0.1278, 2nd-half IC=+0.1192, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.006, Q3_mid=+0.113, Q4=+0.121, Q5_high_vol=+0.205

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum`** (Lock IC=+0.0903, Sharpe=+0.3727)
- Admission: Train IC=+0.2455, Deflated=+0.2452, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.111 | 2017: +0.210 | 2018: +0.198 | 2019: +0.130 | 2020: +0.141 | 2021: +0.095 | 2022: +0.099 | 2023: +0.109 | 2024: +0.143 | 2025: +0.125 | 2026: -0.048
- Yearly Tail ICs:   2015: +0.199 | 2016: +0.228 | 2017: +0.342 | 2018: +0.358 | 2019: +0.282 | 2020: +0.299 | 2021: +0.193 | 2022: +0.071 | 2023: +0.141 | 2024: +0.360 | 2025: -0.109 | 2026: -0.241
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.65
- Early IC=+0.1601, Recent IC=+0.1039, 1st-half IC=+0.1505, 2nd-half IC=+0.1125, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.006, Q3_mid=+0.110, Q4=+0.126, Q5_high_vol=+0.210

**`combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.0992, Sharpe=+0.3583)
- Admission: Train IC=+0.1854, Deflated=+0.1850, IR=0.43, Mono=0.65, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.082 | 2017: +0.161 | 2018: +0.135 | 2019: +0.088 | 2020: +0.114 | 2021: +0.022 | 2022: +0.127 | 2023: +0.065 | 2024: +0.106 | 2025: +0.117 | 2026: +0.052
- Yearly Tail ICs:   2015: +0.074 | 2016: +0.209 | 2017: +0.150 | 2018: +0.052 | 2019: +0.233 | 2020: +0.107 | 2021: +0.121 | 2022: +0.301 | 2023: +0.157 | 2024: +0.147 | 2025: +0.002 | 2026: -0.163
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.79
- Early IC=+0.1215, Recent IC=+0.0963, 1st-half IC=+0.1130, 2nd-half IC=+0.0837, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.007, Q3_mid=+0.082, Q4=+0.101, Q5_high_vol=+0.136

**`combo_tri_max__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0636, Sharpe=+0.3582)
- Admission: Train IC=+0.2181, Deflated=+0.2183, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.098 | 2017: +0.204 | 2018: +0.193 | 2019: +0.066 | 2020: +0.140 | 2021: +0.076 | 2022: +0.100 | 2023: +0.114 | 2024: +0.112 | 2025: +0.084 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.246 | 2017: +0.219 | 2018: +0.345 | 2019: +0.115 | 2020: +0.206 | 2021: +0.300 | 2022: +0.093 | 2023: +0.157 | 2024: +0.250 | 2025: -0.139 | 2026: -0.297
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.71
- Early IC=+0.1511, Recent IC=+0.1073, 1st-half IC=+0.1364, 2nd-half IC=+0.1123, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.182, Q2=-0.024, Q3_mid=+0.120, Q4=+0.122, Q5_high_vol=+0.192

**`combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0794, Sharpe=+0.3571)
- Admission: Train IC=+0.1724, Deflated=+0.1720, IR=0.31, Mono=0.66, p=0.0006, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.125 | 2017: +0.106 | 2018: +0.104 | 2019: +0.187 | 2020: +0.085 | 2021: +0.096 | 2022: +0.121 | 2023: +0.073 | 2024: +0.068 | 2025: +0.045 | 2026: +0.116
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.135 | 2017: +0.163 | 2018: +0.275 | 2019: +0.245 | 2020: +0.115 | 2021: +0.153 | 2022: +0.004 | 2023: +0.013 | 2024: -0.017 | 2025: -0.140 | 2026: +0.101
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.84
- Early IC=+0.1153, Recent IC=+0.0972, 1st-half IC=+0.1331, 2nd-half IC=+0.0932, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.230, Q2=-0.014, Q3_mid=+0.064, Q4=+0.126, Q5_high_vol=+0.146

**`combo_rank_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0760, Sharpe=+0.3554)
- Admission: Train IC=+0.2283, Deflated=+0.2286, IR=0.71, Mono=0.73, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.111 | 2017: +0.152 | 2018: +0.220 | 2019: +0.070 | 2020: +0.137 | 2021: +0.059 | 2022: +0.127 | 2023: +0.094 | 2024: +0.130 | 2025: +0.095 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.282 | 2016: +0.238 | 2017: +0.217 | 2018: +0.277 | 2019: +0.080 | 2020: +0.366 | 2021: +0.175 | 2022: +0.146 | 2023: +0.168 | 2024: +0.253 | 2025: -0.106 | 2026: -0.333
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.85
- Early IC=+0.1338, Recent IC=+0.1138, 1st-half IC=+0.1340, 2nd-half IC=+0.1119, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.162, Q2=-0.017, Q3_mid=+0.101, Q4=+0.138, Q5_high_vol=+0.211

**`combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`** (Lock IC=+0.0815, Sharpe=+0.3462)
- Admission: Train IC=+0.1889, Deflated=+0.1874, IR=0.58, Mono=0.70, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.089 | 2017: +0.199 | 2018: +0.127 | 2019: +0.104 | 2020: +0.134 | 2021: +0.095 | 2022: +0.077 | 2023: +0.115 | 2024: +0.145 | 2025: +0.095 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.465 | 2016: +0.289 | 2017: +0.211 | 2018: +0.212 | 2019: +0.233 | 2020: -0.021 | 2021: +0.183 | 2022: +0.240 | 2023: +0.212 | 2024: +0.317 | 2025: -0.119 | 2026: +0.128
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=0.67
- Early IC=+0.1441, Recent IC=+0.0959, 1st-half IC=+0.1315, 2nd-half IC=+0.1061, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.023, Q3_mid=+0.150, Q4=+0.117, Q5_high_vol=+0.154

**`combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`** (Lock IC=+0.0752, Sharpe=+0.3462)
- Admission: Train IC=+0.1900, Deflated=+0.1885, IR=0.56, Mono=0.70, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.075 | 2017: +0.193 | 2018: +0.114 | 2019: +0.099 | 2020: +0.138 | 2021: +0.089 | 2022: +0.090 | 2023: +0.108 | 2024: +0.132 | 2025: +0.098 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.465 | 2016: +0.280 | 2017: +0.207 | 2018: +0.219 | 2019: +0.226 | 2020: -0.031 | 2021: +0.186 | 2022: +0.246 | 2023: +0.219 | 2024: +0.314 | 2025: -0.109 | 2026: +0.121
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.89, Recency ratio=0.74
- Early IC=+0.1338, Recent IC=+0.0991, 1st-half IC=+0.1216, 2nd-half IC=+0.1082, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.203, Q2=-0.029, Q3_mid=+0.157, Q4=+0.108, Q5_high_vol=+0.148

**`combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.1147, Sharpe=+0.3396)
- Admission: Train IC=+0.2179, Deflated=+0.2173, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.081 | 2017: +0.208 | 2018: +0.169 | 2019: +0.117 | 2020: +0.140 | 2021: +0.083 | 2022: +0.085 | 2023: +0.083 | 2024: +0.105 | 2025: +0.147 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.146 | 2016: +0.197 | 2017: +0.251 | 2018: +0.325 | 2019: +0.370 | 2020: +0.137 | 2021: +0.286 | 2022: +0.150 | 2023: +0.099 | 2024: +0.144 | 2025: +0.051 | 2026: -0.138
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.58
- Early IC=+0.1447, Recent IC=+0.0843, 1st-half IC=+0.1337, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.031, Q3_mid=+0.075, Q4=+0.122, Q5_high_vol=+0.183

**`combo_min__max_up_ret__max_down_ret`** (Lock IC=+0.1039, Sharpe=+0.3390)
- Admission: Train IC=+0.1741, Deflated=+0.1743, IR=0.51, Mono=0.67, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.086 | 2017: +0.208 | 2018: +0.124 | 2019: +0.102 | 2020: +0.149 | 2021: +0.101 | 2022: +0.109 | 2023: +0.103 | 2024: +0.119 | 2025: +0.139 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.347 | 2016: +0.002 | 2017: +0.250 | 2018: +0.190 | 2019: +0.280 | 2020: +0.125 | 2021: +0.316 | 2022: +0.214 | 2023: +0.056 | 2024: +0.232 | 2025: +0.229 | 2026: +0.034
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=0.72
- Early IC=+0.1470, Recent IC=+0.1062, 1st-half IC=+0.1171, 2nd-half IC=+0.1166, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.003, Q3_mid=+0.114, Q4=+0.129, Q5_high_vol=+0.137

**`combo_mean__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0632, Sharpe=+0.3295)
- Admission: Train IC=+0.2468, Deflated=+0.2465, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.047 | 2017: +0.154 | 2018: +0.179 | 2019: +0.127 | 2020: +0.099 | 2021: +0.148 | 2022: +0.148 | 2023: +0.096 | 2024: +0.135 | 2025: +0.086 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.206 | 2016: +0.172 | 2017: +0.190 | 2018: +0.461 | 2019: +0.209 | 2020: +0.169 | 2021: +0.325 | 2022: +0.218 | 2023: +0.337 | 2024: +0.310 | 2025: -0.042 | 2026: -0.310
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.22
- Early IC=+0.1001, Recent IC=+0.1222, 1st-half IC=+0.1254, 2nd-half IC=+0.1260, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.027, Q3_mid=+0.102, Q4=+0.139, Q5_high_vol=+0.191

**`combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0695, Sharpe=+0.3252)
- Admission: Train IC=+0.1971, Deflated=+0.1961, IR=0.55, Mono=0.71, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.082 | 2017: +0.174 | 2018: +0.124 | 2019: +0.089 | 2020: +0.124 | 2021: +0.064 | 2022: +0.112 | 2023: +0.115 | 2024: +0.130 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.127 | 2017: +0.154 | 2018: +0.247 | 2019: +0.271 | 2020: +0.048 | 2021: +0.247 | 2022: +0.153 | 2023: +0.330 | 2024: +0.153 | 2025: +0.077 | 2026: -0.120
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.88
- Early IC=+0.1283, Recent IC=+0.1131, 1st-half IC=+0.1113, 2nd-half IC=+0.1097, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.020, Q3_mid=+0.131, Q4=+0.101, Q5_high_vol=+0.156

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum`** (Lock IC=+0.0841, Sharpe=+0.3166)
- Admission: Train IC=+0.2104, Deflated=+0.2102, IR=0.62, Mono=0.70, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.117 | 2017: +0.137 | 2018: +0.217 | 2019: +0.065 | 2020: +0.109 | 2021: +0.029 | 2022: +0.157 | 2023: +0.079 | 2024: +0.084 | 2025: +0.083 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.419 | 2017: +0.186 | 2018: +0.284 | 2019: +0.061 | 2020: +0.123 | 2021: +0.196 | 2022: +0.172 | 2023: +0.147 | 2024: +0.113 | 2025: -0.117 | 2026: -0.135
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.93
- Early IC=+0.1269, Recent IC=+0.1181, 1st-half IC=+0.1297, 2nd-half IC=+0.1001, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.007, Q3_mid=+0.074, Q4=+0.126, Q5_high_vol=+0.202

**`combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction`** (Lock IC=+0.0577, Sharpe=+0.3163)
- Admission: Train IC=+0.1817, Deflated=+0.1801, IR=0.59, Mono=0.71, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.026 | 2017: +0.151 | 2018: +0.079 | 2019: +0.012 | 2020: +0.092 | 2021: +0.034 | 2022: +0.020 | 2023: +0.128 | 2024: +0.081 | 2025: +0.123 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.107 | 2016: +0.132 | 2017: +0.273 | 2018: +0.164 | 2019: +0.174 | 2020: +0.120 | 2021: +0.251 | 2022: +0.209 | 2023: +0.210 | 2024: +0.166 | 2025: +0.175 | 2026: -0.258
- IC CV=0.73, Neg years (linear/tail)=0/0 of 8, Half ratio=1.15, Recency ratio=0.84
- Early IC=+0.0883, Recent IC=+0.0740, 1st-half IC=+0.0627, 2nd-half IC=+0.0719, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.19)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.006, Q3_mid=+0.072, Q4=+0.062, Q5_high_vol=+0.074

**`combo_rank_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0890, Sharpe=+0.3159)
- Admission: Train IC=+0.2313, Deflated=+0.2310, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.073 | 2017: +0.176 | 2018: +0.136 | 2019: +0.076 | 2020: +0.099 | 2021: +0.063 | 2022: +0.080 | 2023: +0.093 | 2024: +0.130 | 2025: +0.140 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.322 | 2016: +0.122 | 2017: +0.348 | 2018: +0.222 | 2019: +0.196 | 2020: +0.261 | 2021: +0.207 | 2022: +0.146 | 2023: +0.270 | 2024: +0.265 | 2025: -0.017 | 2026: -0.063
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.70
- Early IC=+0.1238, Recent IC=+0.0865, 1st-half IC=+0.1130, 2nd-half IC=+0.0808, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.041, Q3_mid=+0.100, Q4=+0.103, Q5_high_vol=+0.140

**`combo_mean__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.1011, Sharpe=+0.3129)
- Admission: Train IC=+0.1368, Deflated=+0.1362, IR=0.54, Mono=0.72, p=0.0082, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.290 | 2016: +0.058 | 2017: +0.244 | 2018: +0.190 | 2019: +0.136 | 2020: +0.163 | 2021: +0.120 | 2022: +0.079 | 2023: +0.087 | 2024: +0.136 | 2025: +0.110 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.398 | 2016: -0.041 | 2017: +0.109 | 2018: +0.120 | 2019: +0.320 | 2020: +0.019 | 2021: +0.384 | 2022: +0.254 | 2023: +0.141 | 2024: +0.230 | 2025: +0.090 | 2026: +0.015
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.72, Recency ratio=0.55
- Early IC=+0.1509, Recent IC=+0.0828, 1st-half IC=+0.1523, 2nd-half IC=+0.1091, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.023, Q3_mid=+0.147, Q4=+0.149, Q5_high_vol=+0.171

**`combo_mean__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0969, Sharpe=+0.3003)
- Admission: Train IC=+0.1751, Deflated=+0.1749, IR=0.49, Mono=0.67, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.068 | 2017: +0.225 | 2018: +0.138 | 2019: +0.098 | 2020: +0.119 | 2021: +0.070 | 2022: +0.077 | 2023: +0.074 | 2024: +0.123 | 2025: +0.143 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.286 | 2016: -0.117 | 2017: +0.327 | 2018: +0.101 | 2019: +0.233 | 2020: +0.092 | 2021: +0.303 | 2022: +0.322 | 2023: +0.276 | 2024: +0.311 | 2025: +0.126 | 2026: -0.168
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.51
- Early IC=+0.1468, Recent IC=+0.0754, 1st-half IC=+0.1276, 2nd-half IC=+0.0847, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.038, Q3_mid=+0.111, Q4=+0.106, Q5_high_vol=+0.141

**`combo_rank_min__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0931, Sharpe=+0.2815)
- Admission: Train IC=+0.2285, Deflated=+0.2289, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.075 | 2017: +0.191 | 2018: +0.189 | 2019: +0.131 | 2020: +0.076 | 2021: +0.068 | 2022: +0.049 | 2023: +0.067 | 2024: +0.109 | 2025: +0.131 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.070 | 2017: +0.308 | 2018: +0.297 | 2019: +0.272 | 2020: +0.175 | 2021: +0.291 | 2022: +0.185 | 2023: +0.210 | 2024: +0.119 | 2025: +0.147 | 2026: -0.075
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.45, Recency ratio=0.43
- Early IC=+0.1335, Recent IC=+0.0579, 1st-half IC=+0.1452, 2nd-half IC=+0.0655, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.050, Q3_mid=+0.092, Q4=+0.134, Q5_high_vol=+0.131

**`combo_min__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0808, Sharpe=+0.2788)
- Admission: Train IC=+0.2056, Deflated=+0.2051, IR=0.54, Mono=0.69, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.050 | 2017: +0.226 | 2018: +0.159 | 2019: +0.132 | 2020: +0.083 | 2021: +0.095 | 2022: +0.050 | 2023: +0.091 | 2024: +0.099 | 2025: +0.121 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.069 | 2017: +0.147 | 2018: +0.254 | 2019: +0.333 | 2020: +0.079 | 2021: +0.215 | 2022: +0.175 | 2023: +0.298 | 2024: +0.001 | 2025: +0.393 | 2026: -0.156
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.51
- Early IC=+0.1382, Recent IC=+0.0705, 1st-half IC=+0.1387, 2nd-half IC=+0.0786, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.185, Q2=-0.036, Q3_mid=+0.089, Q4=+0.162, Q5_high_vol=+0.123

**`combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0780, Sharpe=+0.2753)
- Admission: Train IC=+0.2364, Deflated=+0.2349, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.030 | 2017: +0.202 | 2018: +0.115 | 2019: +0.115 | 2020: +0.119 | 2021: +0.099 | 2022: +0.071 | 2023: +0.124 | 2024: +0.122 | 2025: +0.106 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.294 | 2017: +0.275 | 2018: +0.225 | 2019: +0.284 | 2020: +0.156 | 2021: +0.335 | 2022: +0.259 | 2023: +0.179 | 2024: +0.091 | 2025: +0.219 | 2026: -0.182
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.84
- Early IC=+0.1165, Recent IC=+0.0973, 1st-half IC=+0.1123, 2nd-half IC=+0.1060, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.002, Q3_mid=+0.133, Q4=+0.081, Q5_high_vol=+0.153

**`combo_rank_min__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0961, Sharpe=+0.2697)
- Admission: Train IC=+0.1977, Deflated=+0.1978, IR=0.55, Mono=0.69, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.077 | 2017: +0.236 | 2018: +0.132 | 2019: +0.097 | 2020: +0.142 | 2021: +0.054 | 2022: +0.084 | 2023: +0.081 | 2024: +0.112 | 2025: +0.135 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.285 | 2016: -0.076 | 2017: +0.295 | 2018: +0.113 | 2019: +0.263 | 2020: +0.207 | 2021: +0.349 | 2022: +0.282 | 2023: +0.266 | 2024: +0.142 | 2025: +0.162 | 2026: -0.067
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.68, Recency ratio=0.51
- Early IC=+0.1585, Recent IC=+0.0801, 1st-half IC=+0.1318, 2nd-half IC=+0.0895, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.053, Q3_mid=+0.139, Q4=+0.126, Q5_high_vol=+0.125

**`combo_max__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0679, Sharpe=+0.2608)
- Admission: Train IC=+0.2164, Deflated=+0.2158, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.062 | 2017: +0.112 | 2018: +0.209 | 2019: +0.101 | 2020: +0.107 | 2021: +0.093 | 2022: +0.135 | 2023: +0.083 | 2024: +0.118 | 2025: +0.088 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.180 | 2017: +0.074 | 2018: +0.467 | 2019: +0.123 | 2020: +0.180 | 2021: +0.388 | 2022: +0.145 | 2023: +0.155 | 2024: +0.250 | 2025: -0.057 | 2026: -0.302
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=1.25
- Early IC=+0.0868, Recent IC=+0.1090, 1st-half IC=+0.1236, 2nd-half IC=+0.1107, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.013, Q3_mid=+0.082, Q4=+0.135, Q5_high_vol=+0.201

**`combo_rank_min__volatility_expansion_trend_vector__early_order_flow_imbalance`** (Lock IC=+0.0693, Sharpe=+0.2543)
- Admission: Train IC=+0.2196, Deflated=+0.2194, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.022 | 2017: +0.159 | 2018: +0.126 | 2019: +0.113 | 2020: +0.054 | 2021: +0.112 | 2022: +0.118 | 2023: +0.106 | 2024: +0.137 | 2025: +0.107 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.079 | 2017: +0.247 | 2018: +0.222 | 2019: +0.330 | 2020: +0.116 | 2021: +0.244 | 2022: +0.181 | 2023: +0.267 | 2024: +0.290 | 2025: +0.060 | 2026: -0.212
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=1.23
- Early IC=+0.0909, Recent IC=+0.1117, 1st-half IC=+0.1031, 2nd-half IC=+0.0938, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.026, Q3_mid=+0.083, Q4=+0.102, Q5_high_vol=+0.119

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0881, Sharpe=+0.2537)
- Admission: Train IC=+0.2637, Deflated=+0.2634, IR=0.82, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.072 | 2017: +0.182 | 2018: +0.187 | 2019: +0.123 | 2020: +0.124 | 2021: +0.132 | 2022: +0.077 | 2023: +0.131 | 2024: +0.143 | 2025: +0.123 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.365 | 2016: +0.258 | 2017: +0.294 | 2018: +0.281 | 2019: +0.289 | 2020: +0.215 | 2021: +0.274 | 2022: +0.275 | 2023: +0.318 | 2024: +0.162 | 2025: +0.001 | 2026: -0.057
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.82
- Early IC=+0.1272, Recent IC=+0.1038, 1st-half IC=+0.1312, 2nd-half IC=+0.1181, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.009, Q3_mid=+0.129, Q4=+0.099, Q5_high_vol=+0.190

**`combo_mean__first_bar_return__close_vs_open_range`** (Lock IC=+0.0927, Sharpe=+0.2533)
- Admission: Train IC=+0.2087, Deflated=+0.2093, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.100 | 2017: +0.214 | 2018: +0.205 | 2019: +0.110 | 2020: +0.114 | 2021: +0.101 | 2022: +0.096 | 2023: +0.080 | 2024: +0.151 | 2025: +0.114 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.042 | 2017: +0.267 | 2018: +0.355 | 2019: +0.134 | 2020: +0.183 | 2021: +0.361 | 2022: +0.268 | 2023: +0.228 | 2024: +0.310 | 2025: +0.016 | 2026: -0.244
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.56
- Early IC=+0.1570, Recent IC=+0.0884, 1st-half IC=+0.1518, 2nd-half IC=+0.1005, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.214, Q2=-0.029, Q3_mid=+0.119, Q4=+0.137, Q5_high_vol=+0.151

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0557, Sharpe=+0.2440)
- Admission: Train IC=+0.1831, Deflated=+0.1835, IR=0.51, Mono=0.71, p=0.0002, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.120 | 2017: +0.118 | 2018: +0.283 | 2019: +0.095 | 2020: +0.105 | 2021: +0.084 | 2022: +0.101 | 2023: +0.039 | 2024: +0.101 | 2025: +0.077 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.148 | 2016: +0.089 | 2017: +0.306 | 2018: +0.479 | 2019: +0.081 | 2020: +0.187 | 2021: +0.206 | 2022: +0.012 | 2023: +0.064 | 2024: +0.172 | 2025: +0.148 | 2026: -0.305
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.59
- Early IC=+0.1191, Recent IC=+0.0702, 1st-half IC=+0.1527, 2nd-half IC=+0.0857, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.037, Q3_mid=+0.067, Q4=+0.127, Q5_high_vol=+0.184

**`combo_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0868, Sharpe=+0.2383)
- Admission: Train IC=+0.2381, Deflated=+0.2379, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.073 | 2017: +0.176 | 2018: +0.137 | 2019: +0.078 | 2020: +0.099 | 2021: +0.068 | 2022: +0.083 | 2023: +0.090 | 2024: +0.124 | 2025: +0.138 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.311 | 2016: +0.104 | 2017: +0.339 | 2018: +0.220 | 2019: +0.228 | 2020: +0.258 | 2021: +0.220 | 2022: +0.161 | 2023: +0.222 | 2024: +0.264 | 2025: -0.030 | 2026: -0.070
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.69
- Early IC=+0.1246, Recent IC=+0.0863, 1st-half IC=+0.1146, 2nd-half IC=+0.0821, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.174, Q2=-0.041, Q3_mid=+0.102, Q4=+0.107, Q5_high_vol=+0.138

**`max_up_ret`** (Lock IC=+0.0813, Sharpe=+0.2357)
- Admission: Train IC=+0.2055, Deflated=+0.2058, IR=0.54, Mono=0.70, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143 | 2025: +0.080 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.194 | 2017: +0.220 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.134 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.64
- Early IC=+0.1558, Recent IC=+0.0999, 1st-half IC=+0.1344, 2nd-half IC=+0.1246, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.009, Q3_mid=+0.112, Q4=+0.124, Q5_high_vol=+0.222

**`combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0904, Sharpe=+0.2350)
- Admission: Train IC=+0.2521, Deflated=+0.2515, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.058 | 2017: +0.196 | 2018: +0.193 | 2019: +0.106 | 2020: +0.126 | 2021: +0.124 | 2022: +0.074 | 2023: +0.129 | 2024: +0.137 | 2025: +0.126 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.337 | 2016: +0.186 | 2017: +0.255 | 2018: +0.246 | 2019: +0.278 | 2020: +0.176 | 2021: +0.328 | 2022: +0.235 | 2023: +0.261 | 2024: +0.195 | 2025: +0.075 | 2026: -0.075
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.79
- Early IC=+0.1275, Recent IC=+0.1003, 1st-half IC=+0.1351, 2nd-half IC=+0.1147, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.011, Q3_mid=+0.134, Q4=+0.108, Q5_high_vol=+0.186

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0607, Sharpe=+0.2343)
- Admission: Train IC=+0.2155, Deflated=+0.2148, IR=0.50, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.077 | 2017: +0.214 | 2018: +0.161 | 2019: +0.117 | 2020: +0.170 | 2021: +0.048 | 2022: +0.113 | 2023: +0.117 | 2024: +0.097 | 2025: +0.102 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.326 | 2016: -0.048 | 2017: +0.326 | 2018: +0.221 | 2019: +0.292 | 2020: +0.226 | 2021: +0.184 | 2022: +0.240 | 2023: +0.284 | 2024: +0.228 | 2025: -0.037 | 2026: -0.099
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.84, Recency ratio=0.79
- Early IC=+0.1452, Recent IC=+0.1150, 1st-half IC=+0.1399, 2nd-half IC=+0.1169, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.007, Q3_mid=+0.154, Q4=+0.122, Q5_high_vol=+0.167

**`combo_rank_min__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0702, Sharpe=+0.2248)
- Admission: Train IC=+0.1653, Deflated=+0.1658, IR=0.55, Mono=0.73, p=0.0012, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.038 | 2017: +0.162 | 2018: +0.111 | 2019: +0.122 | 2020: +0.103 | 2021: +0.105 | 2022: +0.144 | 2023: +0.079 | 2024: +0.114 | 2025: +0.068 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.080 | 2017: +0.182 | 2018: +0.160 | 2019: +0.242 | 2020: +0.142 | 2021: +0.279 | 2022: +0.308 | 2023: +0.056 | 2024: +0.329 | 2025: +0.114 | 2026: -0.083
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=1.02
- Early IC=+0.1032, Recent IC=+0.1054, 1st-half IC=+0.1080, 2nd-half IC=+0.0990, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.000, Q3_mid=+0.101, Q4=+0.141, Q5_high_vol=+0.124

**`combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0`** (Lock IC=+0.0907, Sharpe=+0.2213)
- Admission: Train IC=+0.1918, Deflated=+0.1924, IR=0.61, Mono=0.71, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.085 | 2017: +0.203 | 2018: +0.175 | 2019: +0.113 | 2020: +0.126 | 2021: +0.110 | 2022: +0.054 | 2023: +0.096 | 2024: +0.120 | 2025: +0.116 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.396 | 2016: +0.135 | 2017: +0.361 | 2018: +0.270 | 2019: +0.191 | 2020: +0.141 | 2021: +0.184 | 2022: +0.134 | 2023: +0.237 | 2024: +0.197 | 2025: +0.024 | 2026: -0.227
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.52
- Early IC=+0.1444, Recent IC=+0.0748, 1st-half IC=+0.1392, 2nd-half IC=+0.0971, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.177, Q2=-0.036, Q3_mid=+0.123, Q4=+0.160, Q5_high_vol=+0.142

**`combo_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0877, Sharpe=+0.2021)
- Admission: Train IC=+0.2090, Deflated=+0.2086, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.262 | 2016: +0.099 | 2017: +0.235 | 2018: +0.222 | 2019: +0.110 | 2020: +0.174 | 2021: +0.157 | 2022: +0.101 | 2023: +0.094 | 2024: +0.148 | 2025: +0.081 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.238 | 2017: +0.112 | 2018: +0.433 | 2019: +0.209 | 2020: +0.147 | 2021: +0.371 | 2022: +0.025 | 2023: +0.026 | 2024: +0.270 | 2025: -0.078 | 2026: -0.289
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.58
- Early IC=+0.1673, Recent IC=+0.0975, 1st-half IC=+0.1625, 2nd-half IC=+0.1360, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.214, Q2=-0.004, Q3_mid=+0.134, Q4=+0.162, Q5_high_vol=+0.227

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0912, Sharpe=+0.2017)
- Admission: Train IC=+0.2354, Deflated=+0.2355, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.098 | 2017: +0.233 | 2018: +0.253 | 2019: +0.146 | 2020: +0.146 | 2021: +0.143 | 2022: +0.095 | 2023: +0.097 | 2024: +0.160 | 2025: +0.084 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.134 | 2017: +0.244 | 2018: +0.450 | 2019: +0.136 | 2020: +0.208 | 2021: +0.330 | 2022: +0.119 | 2023: +0.156 | 2024: +0.180 | 2025: -0.034 | 2026: -0.214
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.58
- Early IC=+0.1657, Recent IC=+0.0957, 1st-half IC=+0.1783, 2nd-half IC=+0.1231, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.214, Q2=-0.019, Q3_mid=+0.143, Q4=+0.165, Q5_high_vol=+0.216

**`combo_mean__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0758, Sharpe=+0.1995)
- Admission: Train IC=+0.1901, Deflated=+0.1909, IR=0.47, Mono=0.66, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.124 | 2017: +0.171 | 2018: +0.224 | 2019: +0.136 | 2020: +0.093 | 2021: +0.108 | 2022: +0.064 | 2023: +0.065 | 2024: +0.113 | 2025: +0.095 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.276 | 2016: -0.033 | 2017: +0.338 | 2018: +0.412 | 2019: +0.166 | 2020: +0.193 | 2021: +0.314 | 2022: +0.138 | 2023: +0.131 | 2024: +0.250 | 2025: +0.040 | 2026: -0.208
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.44
- Early IC=+0.1476, Recent IC=+0.0647, 1st-half IC=+0.1626, 2nd-half IC=+0.0809, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.174, Q2=-0.034, Q3_mid=+0.099, Q4=+0.182, Q5_high_vol=+0.142

**`combo_diff__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0818, Sharpe=+0.1956)
- Admission: Train IC=+0.1410, Deflated=+0.1398, IR=0.50, Mono=0.67, p=0.0074, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.100 | 2017: +0.159 | 2018: +0.085 | 2019: +0.082 | 2020: +0.094 | 2021: +0.047 | 2022: +0.074 | 2023: +0.090 | 2024: +0.131 | 2025: +0.095 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.162 | 2017: +0.137 | 2018: +0.072 | 2019: +0.173 | 2020: +0.009 | 2021: +0.222 | 2022: +0.241 | 2023: +0.353 | 2024: +0.349 | 2025: -0.030 | 2026: +0.078
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.63
- Early IC=+0.1293, Recent IC=+0.0820, 1st-half IC=+0.1062, 2nd-half IC=+0.0728, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.198, Q2=-0.046, Q3_mid=+0.123, Q4=+0.094, Q5_high_vol=+0.087

**`combo_tri_median__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.0816, Sharpe=+0.1952)
- Admission: Train IC=+0.1994, Deflated=+0.1992, IR=0.42, Mono=0.67, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.048 | 2017: +0.189 | 2018: +0.137 | 2019: +0.081 | 2020: +0.097 | 2021: +0.076 | 2022: +0.086 | 2023: +0.090 | 2024: +0.109 | 2025: +0.150 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.367 | 2016: +0.083 | 2017: +0.291 | 2018: +0.187 | 2019: +0.184 | 2020: +0.207 | 2021: +0.242 | 2022: +0.195 | 2023: +0.113 | 2024: +0.246 | 2025: +0.119 | 2026: -0.312
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.75
- Early IC=+0.1184, Recent IC=+0.0882, 1st-half IC=+0.1148, 2nd-half IC=+0.0869, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.022, Q3_mid=+0.106, Q4=+0.110, Q5_high_vol=+0.128

**`combo_rank_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0749, Sharpe=+0.1819)
- Admission: Train IC=+0.1952, Deflated=+0.1954, IR=0.65, Mono=0.71, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.103 | 2017: +0.203 | 2018: +0.170 | 2019: +0.101 | 2020: +0.139 | 2021: +0.094 | 2022: +0.120 | 2023: +0.128 | 2024: +0.134 | 2025: +0.095 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.255 | 2016: +0.139 | 2017: +0.157 | 2018: +0.289 | 2019: +0.203 | 2020: +0.112 | 2021: +0.111 | 2022: +0.114 | 2023: +0.408 | 2024: +0.211 | 2025: -0.160 | 2026: -0.477
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.82
- Early IC=+0.1531, Recent IC=+0.1249, 1st-half IC=+0.1270, 2nd-half IC=+0.1331, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.025, Q3_mid=+0.116, Q4=+0.096, Q5_high_vol=+0.206

**`combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0`** (Lock IC=+0.0739, Sharpe=+0.1807)
- Admission: Train IC=+0.2685, Deflated=+0.2690, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.119 | 2017: +0.152 | 2018: +0.263 | 2019: +0.110 | 2020: +0.115 | 2021: +0.109 | 2022: +0.121 | 2023: +0.079 | 2024: +0.145 | 2025: +0.108 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.234 | 2016: +0.256 | 2017: +0.209 | 2018: +0.381 | 2019: +0.167 | 2020: +0.276 | 2021: +0.241 | 2022: +0.232 | 2023: +0.380 | 2024: +0.261 | 2025: -0.129 | 2026: -0.370
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.74
- Early IC=+0.1355, Recent IC=+0.0997, 1st-half IC=+0.1586, 2nd-half IC=+0.1095, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.019, Q3_mid=+0.107, Q4=+0.160, Q5_high_vol=+0.217

**`combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0`** (Lock IC=+0.0783, Sharpe=+0.1736)
- Admission: Train IC=+0.2405, Deflated=+0.2406, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.105 | 2017: +0.205 | 2018: +0.232 | 2019: +0.101 | 2020: +0.160 | 2021: +0.140 | 2022: +0.141 | 2023: +0.070 | 2024: +0.153 | 2025: +0.104 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.188 | 2016: +0.115 | 2017: +0.274 | 2018: +0.287 | 2019: +0.095 | 2020: +0.337 | 2021: +0.248 | 2022: +0.204 | 2023: +0.389 | 2024: +0.241 | 2025: -0.094 | 2026: -0.462
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.68
- Early IC=+0.1546, Recent IC=+0.1051, 1st-half IC=+0.1600, 2nd-half IC=+0.1308, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.205, Q2=-0.018, Q3_mid=+0.142, Q4=+0.171, Q5_high_vol=+0.189

**`combo_max__net_volume_flow__bar_body_rng_0`** (Lock IC=+0.0820, Sharpe=+0.1731)
- Admission: Train IC=+0.2422, Deflated=+0.2426, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.121 | 2017: +0.179 | 2018: +0.205 | 2019: +0.115 | 2020: +0.121 | 2021: +0.118 | 2022: +0.088 | 2023: +0.078 | 2024: +0.124 | 2025: +0.111 | 2026: -0.043
- Yearly Tail ICs:   2015: +0.440 | 2016: +0.114 | 2017: +0.283 | 2018: +0.225 | 2019: +0.174 | 2020: +0.201 | 2021: +0.284 | 2022: +0.291 | 2023: +0.349 | 2024: +0.245 | 2025: +0.041 | 2026: -0.377
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.56
- Early IC=+0.1500, Recent IC=+0.0833, 1st-half IC=+0.1555, 2nd-half IC=+0.0979, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.024, Q3_mid=+0.108, Q4=+0.174, Q5_high_vol=+0.160

**`combo_min__net_volume_flow__vwap_close_divergence_trend`** (Lock IC=+0.0779, Sharpe=+0.1726)
- Admission: Train IC=+0.2186, Deflated=+0.2179, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.040 | 2017: +0.188 | 2018: +0.121 | 2019: +0.089 | 2020: +0.104 | 2021: +0.081 | 2022: +0.090 | 2023: +0.102 | 2024: +0.104 | 2025: +0.140 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.191 | 2016: +0.074 | 2017: +0.173 | 2018: +0.172 | 2019: +0.285 | 2020: +0.156 | 2021: +0.202 | 2022: +0.199 | 2023: +0.296 | 2024: +0.157 | 2025: +0.138 | 2026: -0.212
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.85
- Early IC=+0.1138, Recent IC=+0.0962, 1st-half IC=+0.1064, 2nd-half IC=+0.0937, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.027, Q3_mid=+0.116, Q4=+0.106, Q5_high_vol=+0.137

**`combo_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0885, Sharpe=+0.1705)
- Admission: Train IC=+0.2188, Deflated=+0.2187, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.077 | 2017: +0.184 | 2018: +0.143 | 2019: +0.087 | 2020: +0.104 | 2021: +0.128 | 2022: +0.108 | 2023: +0.113 | 2024: +0.140 | 2025: +0.149 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.122 | 2017: +0.314 | 2018: +0.286 | 2019: +0.204 | 2020: +0.236 | 2021: +0.190 | 2022: +0.197 | 2023: +0.317 | 2024: +0.188 | 2025: +0.068 | 2026: -0.099
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=0.85
- Early IC=+0.1306, Recent IC=+0.1106, 1st-half IC=+0.1110, 2nd-half IC=+0.1159, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.001, Q3_mid=+0.109, Q4=+0.103, Q5_high_vol=+0.157

**`combo_min__max_down_ret__close_vs_open_range`** (Lock IC=+0.1016, Sharpe=+0.1701)
- Admission: Train IC=+0.1540, Deflated=+0.1540, IR=0.54, Mono=0.70, p=0.0038, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.070 | 2017: +0.219 | 2018: +0.119 | 2019: +0.084 | 2020: +0.133 | 2021: +0.048 | 2022: +0.083 | 2023: +0.080 | 2024: +0.114 | 2025: +0.140 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.326 | 2016: -0.017 | 2017: +0.240 | 2018: +0.164 | 2019: +0.172 | 2020: +0.101 | 2021: +0.345 | 2022: +0.303 | 2023: +0.139 | 2024: +0.158 | 2025: +0.149 | 2026: +0.035
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.56
- Early IC=+0.1443, Recent IC=+0.0814, 1st-half IC=+0.1199, 2nd-half IC=+0.0856, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.057, Q3_mid=+0.133, Q4=+0.104, Q5_high_vol=+0.127

**`combo_rank_max__bar_ret_0__shaved_bar_trend_conviction`** (Lock IC=+0.0631, Sharpe=+0.1674)
- Admission: Train IC=+0.1800, Deflated=+0.1798, IR=0.58, Mono=0.69, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.108 | 2017: +0.174 | 2018: +0.229 | 2019: +0.059 | 2020: +0.176 | 2021: +0.104 | 2022: +0.047 | 2023: +0.079 | 2024: +0.108 | 2025: +0.135 | 2026: -0.108
- Yearly Tail ICs:   2015: +0.082 | 2016: +0.006 | 2017: +0.168 | 2018: +0.247 | 2019: +0.050 | 2020: +0.271 | 2021: +0.109 | 2022: +0.279 | 2023: +0.075 | 2024: +0.156 | 2025: +0.066 | 2026: -0.398
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.46
- Early IC=+0.1396, Recent IC=+0.0644, 1st-half IC=+0.1385, 2nd-half IC=+0.1053, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.19)
- Regime ICs: Q1_low_vol=+0.155, Q2=-0.030, Q3_mid=+0.131, Q4=+0.152, Q5_high_vol=+0.159

**`combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0902, Sharpe=+0.1578)
- Admission: Train IC=+0.2505, Deflated=+0.2497, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.038 | 2017: +0.200 | 2018: +0.197 | 2019: +0.185 | 2020: +0.174 | 2021: +0.124 | 2022: +0.054 | 2023: +0.100 | 2024: +0.116 | 2025: +0.047 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.520 | 2016: +0.069 | 2017: +0.343 | 2018: +0.250 | 2019: +0.502 | 2020: +0.214 | 2021: +0.208 | 2022: +0.205 | 2023: +0.144 | 2024: +0.238 | 2025: +0.177 | 2026: +0.024
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.64
- Early IC=+0.1191, Recent IC=+0.0766, 1st-half IC=+0.1584, 2nd-half IC=+0.1090, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.164, Q2=-0.018, Q3_mid=+0.130, Q4=+0.171, Q5_high_vol=+0.189

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0995, Sharpe=+0.1554)
- Admission: Train IC=+0.2721, Deflated=+0.2714, IR=0.97, Mono=0.85, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.085 | 2017: +0.228 | 2018: +0.207 | 2019: +0.114 | 2020: +0.127 | 2021: +0.124 | 2022: +0.089 | 2023: +0.107 | 2024: +0.152 | 2025: +0.125 | 2026: -0.028
- Yearly Tail ICs:   2015: +0.458 | 2016: +0.327 | 2017: +0.262 | 2018: +0.386 | 2019: +0.214 | 2020: +0.193 | 2021: +0.267 | 2022: +0.229 | 2023: +0.252 | 2024: +0.271 | 2025: -0.065 | 2026: -0.277
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.63
- Early IC=+0.1562, Recent IC=+0.0984, 1st-half IC=+0.1549, 2nd-half IC=+0.1104, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.203, Q2=-0.007, Q3_mid=+0.128, Q4=+0.134, Q5_high_vol=+0.202

**`combo_rank_max__first_bar_return__close_vs_open_range`** (Lock IC=+0.0752, Sharpe=+0.1487)
- Admission: Train IC=+0.2161, Deflated=+0.2169, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.113 | 2017: +0.209 | 2018: +0.216 | 2019: +0.103 | 2020: +0.141 | 2021: +0.128 | 2022: +0.124 | 2023: +0.086 | 2024: +0.140 | 2025: +0.119 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.042 | 2017: +0.263 | 2018: +0.327 | 2019: +0.151 | 2020: +0.314 | 2021: +0.258 | 2022: +0.267 | 2023: +0.316 | 2024: +0.271 | 2025: -0.123 | 2026: -0.469
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.66
- Early IC=+0.1617, Recent IC=+0.1060, 1st-half IC=+0.1523, 2nd-half IC=+0.1240, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.011, Q3_mid=+0.146, Q4=+0.151, Q5_high_vol=+0.164

**`combo_sig_product__early_body_momentum__close_vs_open_range`** (Lock IC=+0.0783, Sharpe=+0.1475)
- Admission: Train IC=+0.1827, Deflated=+0.1826, IR=0.43, Mono=0.65, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.075 | 2017: +0.153 | 2018: +0.086 | 2019: +0.061 | 2020: +0.094 | 2021: +0.038 | 2022: +0.129 | 2023: +0.080 | 2024: +0.111 | 2025: +0.151 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.313 | 2016: +0.126 | 2017: +0.361 | 2018: +0.216 | 2019: +0.087 | 2020: +0.117 | 2021: +0.249 | 2022: +0.127 | 2023: +0.046 | 2024: +0.255 | 2025: -0.009 | 2026: +0.006
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.92
- Early IC=+0.1140, Recent IC=+0.1044, 1st-half IC=+0.0917, 2nd-half IC=+0.0856, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.014, Q3_mid=+0.088, Q4=+0.089, Q5_high_vol=+0.098

**`combo_rank_max__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0900, Sharpe=+0.1144)
- Admission: Train IC=+0.1828, Deflated=+0.1817, IR=0.54, Mono=0.70, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.217 | 2016: -0.005 | 2017: +0.203 | 2018: +0.154 | 2019: +0.130 | 2020: +0.084 | 2021: +0.100 | 2022: +0.061 | 2023: +0.044 | 2024: +0.119 | 2025: +0.177 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.355 | 2016: -0.164 | 2017: +0.253 | 2018: +0.186 | 2019: +0.387 | 2020: +0.014 | 2021: +0.361 | 2022: +0.274 | 2023: +0.158 | 2024: +0.327 | 2025: +0.267 | 2026: -0.164
- IC CV=0.63, Neg years (linear/tail)=1/1 of 8, Half ratio=0.56, Recency ratio=0.55
- Early IC=+0.1010, Recent IC=+0.0555, 1st-half IC=+0.1217, 2nd-half IC=+0.0683, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.028, Q3_mid=+0.110, Q4=+0.115, Q5_high_vol=+0.117

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0818, Sharpe=+0.0961)
- Admission: Train IC=+0.2061, Deflated=+0.2067, IR=0.57, Mono=0.69, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.094 | 2017: +0.257 | 2018: +0.230 | 2019: +0.145 | 2020: +0.132 | 2021: +0.089 | 2022: +0.091 | 2023: +0.045 | 2024: +0.124 | 2025: +0.108 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.012 | 2017: +0.235 | 2018: +0.426 | 2019: +0.114 | 2020: +0.240 | 2021: +0.196 | 2022: +0.200 | 2023: +0.229 | 2024: +0.223 | 2025: +0.035 | 2026: -0.250
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.39
- Early IC=+0.1753, Recent IC=+0.0679, 1st-half IC=+0.1733, 2nd-half IC=+0.0874, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.060, Q3_mid=+0.140, Q4=+0.161, Q5_high_vol=+0.151

**`combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0`** (Lock IC=+0.0873, Sharpe=+0.0959)
- Admission: Train IC=+0.2176, Deflated=+0.2179, IR=0.60, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.143 | 2017: +0.142 | 2018: +0.195 | 2019: +0.073 | 2020: +0.120 | 2021: +0.071 | 2022: +0.131 | 2023: +0.065 | 2024: +0.109 | 2025: +0.082 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.150 | 2016: +0.309 | 2017: +0.182 | 2018: +0.251 | 2019: +0.134 | 2020: +0.058 | 2021: +0.365 | 2022: +0.192 | 2023: +0.129 | 2024: +0.122 | 2025: -0.063 | 2026: -0.155
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.69
- Early IC=+0.1425, Recent IC=+0.0984, 1st-half IC=+0.1363, 2nd-half IC=+0.1018, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.000, Q3_mid=+0.098, Q4=+0.129, Q5_high_vol=+0.180

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=+0.0856, Sharpe=+0.0926)
- Admission: Train IC=+0.2288, Deflated=+0.2293, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.62
- Early IC=+0.1532, Recent IC=+0.0956, 1st-half IC=+0.1514, 2nd-half IC=+0.1182, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.008, Q3_mid=+0.106, Q4=+0.148, Q5_high_vol=+0.216

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0894, Sharpe=+0.0870)
- Admission: Train IC=+0.2372, Deflated=+0.2372, IR=0.77, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.102 | 2017: +0.211 | 2018: +0.247 | 2019: +0.163 | 2020: +0.140 | 2021: +0.103 | 2022: +0.065 | 2023: +0.084 | 2024: +0.119 | 2025: +0.118 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.395 | 2016: +0.066 | 2017: +0.336 | 2018: +0.446 | 2019: +0.185 | 2020: +0.147 | 2021: +0.271 | 2022: +0.271 | 2023: +0.157 | 2024: +0.183 | 2025: +0.067 | 2026: -0.142
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.48
- Early IC=+0.1563, Recent IC=+0.0746, 1st-half IC=+0.1741, 2nd-half IC=+0.1014, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.198, Q2=-0.033, Q3_mid=+0.142, Q4=+0.156, Q5_high_vol=+0.183

**`combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend`** (Lock IC=+0.0800, Sharpe=+0.0855)
- Admission: Train IC=+0.2291, Deflated=+0.2281, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.037 | 2017: +0.186 | 2018: +0.098 | 2019: +0.085 | 2020: +0.096 | 2021: +0.070 | 2022: +0.097 | 2023: +0.100 | 2024: +0.112 | 2025: +0.152 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.025 | 2017: +0.229 | 2018: +0.202 | 2019: +0.321 | 2020: +0.194 | 2021: +0.267 | 2022: +0.189 | 2023: +0.322 | 2024: +0.170 | 2025: +0.148 | 2026: -0.298
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.89
- Early IC=+0.1108, Recent IC=+0.0991, 1st-half IC=+0.0949, 2nd-half IC=+0.0940, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.001, Q3_mid=+0.100, Q4=+0.086, Q5_high_vol=+0.129

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.0778, Sharpe=+0.0854)
- Admission: Train IC=+0.2133, Deflated=+0.2138, IR=0.55, Mono=0.68, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.179 | 2017: +0.097 | 2018: +0.117 | 2019: +0.074 | 2020: +0.116 | 2021: +0.072 | 2022: +0.081 | 2023: +0.140 | 2024: +0.144 | 2025: +0.074 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.197 | 2017: +0.338 | 2018: +0.242 | 2019: +0.176 | 2020: +0.135 | 2021: +0.250 | 2022: +0.134 | 2023: +0.076 | 2024: +0.255 | 2025: -0.130 | 2026: +0.008
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.80
- Early IC=+0.1379, Recent IC=+0.1108, 1st-half IC=+0.1130, 2nd-half IC=+0.1000, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.003, Q3_mid=+0.061, Q4=+0.092, Q5_high_vol=+0.206

**`combo_mean__net_volume_flow__first_bar_return`** (Lock IC=+0.0871, Sharpe=+0.0841)
- Admission: Train IC=+0.2230, Deflated=+0.2235, IR=0.51, Mono=0.67, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.094 | 2017: +0.186 | 2018: +0.214 | 2019: +0.124 | 2020: +0.108 | 2021: +0.107 | 2022: +0.099 | 2023: +0.076 | 2024: +0.136 | 2025: +0.108 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.285 | 2016: -0.023 | 2017: +0.198 | 2018: +0.374 | 2019: +0.150 | 2020: +0.210 | 2021: +0.310 | 2022: +0.265 | 2023: +0.310 | 2024: +0.256 | 2025: -0.032 | 2026: -0.250
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.63
- Early IC=+0.1399, Recent IC=+0.0877, 1st-half IC=+0.1519, 2nd-half IC=+0.0978, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.028, Q3_mid=+0.114, Q4=+0.162, Q5_high_vol=+0.150

**`combo_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0977, Sharpe=+0.0827)
- Admission: Train IC=+0.1985, Deflated=+0.1985, IR=0.57, Mono=0.71, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.085 | 2017: +0.179 | 2018: +0.123 | 2019: +0.073 | 2020: +0.112 | 2021: +0.120 | 2022: +0.088 | 2023: +0.106 | 2024: +0.150 | 2025: +0.158 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.264 | 2017: +0.301 | 2018: +0.273 | 2019: +0.098 | 2020: +0.092 | 2021: +0.237 | 2022: +0.083 | 2023: +0.185 | 2024: +0.243 | 2025: +0.099 | 2026: -0.047
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=0.73
- Early IC=+0.1322, Recent IC=+0.0970, 1st-half IC=+0.1004, 2nd-half IC=+0.1098, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.211, Q2=+0.003, Q3_mid=+0.094, Q4=+0.092, Q5_high_vol=+0.148

**`combo_min__close_vs_open_range__vwap_close_divergence_trend`** (Lock IC=+0.0800, Sharpe=+0.0807)
- Admission: Train IC=+0.2069, Deflated=+0.2061, IR=0.63, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.055 | 2017: +0.186 | 2018: +0.085 | 2019: +0.070 | 2020: +0.093 | 2021: +0.077 | 2022: +0.098 | 2023: +0.120 | 2024: +0.116 | 2025: +0.150 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.243 | 2016: +0.167 | 2017: +0.277 | 2018: +0.203 | 2019: +0.277 | 2020: +0.133 | 2021: +0.310 | 2022: +0.117 | 2023: +0.254 | 2024: +0.166 | 2025: +0.116 | 2026: -0.207
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=0.90
- Early IC=+0.1207, Recent IC=+0.1091, 1st-half IC=+0.0922, 2nd-half IC=+0.0984, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.009, Q3_mid=+0.100, Q4=+0.084, Q5_high_vol=+0.130

**`combo_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0639, Sharpe=+0.0800)
- Admission: Train IC=+0.2173, Deflated=+0.2163, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.095 | 2017: +0.174 | 2018: +0.128 | 2019: +0.082 | 2020: +0.122 | 2021: +0.065 | 2022: +0.112 | 2023: +0.116 | 2024: +0.134 | 2025: +0.086 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.342 | 2017: +0.129 | 2018: +0.300 | 2019: +0.146 | 2020: +0.104 | 2021: +0.236 | 2022: +0.139 | 2023: +0.318 | 2024: +0.252 | 2025: -0.207 | 2026: -0.172
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.85
- Early IC=+0.1342, Recent IC=+0.1138, 1st-half IC=+0.1132, 2nd-half IC=+0.1088, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.025, Q3_mid=+0.129, Q4=+0.106, Q5_high_vol=+0.160

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0747, Sharpe=+0.0706)
- Admission: Train IC=+0.2676, Deflated=+0.2677, IR=0.95, Mono=0.79, p=0.0000, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.100 | 2017: +0.194 | 2018: +0.213 | 2019: +0.156 | 2020: +0.155 | 2021: +0.137 | 2022: +0.066 | 2023: +0.083 | 2024: +0.102 | 2025: +0.025 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.132 | 2017: +0.408 | 2018: +0.398 | 2019: +0.397 | 2020: +0.142 | 2021: +0.253 | 2022: +0.166 | 2023: +0.188 | 2024: -0.024 | 2025: -0.046 | 2026: +0.020
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.51
- Early IC=+0.1469, Recent IC=+0.0746, 1st-half IC=+0.1597, 2nd-half IC=+0.1112, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.028, Q3_mid=+0.089, Q4=+0.167, Q5_high_vol=+0.225

**`combo_min__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0946, Sharpe=+0.0682)
- Admission: Train IC=+0.2188, Deflated=+0.2182, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.065 | 2017: +0.197 | 2018: +0.176 | 2019: +0.108 | 2020: +0.131 | 2021: +0.115 | 2022: +0.052 | 2023: +0.114 | 2024: +0.141 | 2025: +0.122 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.227 | 2017: +0.245 | 2018: +0.250 | 2019: +0.335 | 2020: +0.166 | 2021: +0.330 | 2022: +0.164 | 2023: +0.107 | 2024: +0.282 | 2025: +0.022 | 2026: +0.149
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.63
- Early IC=+0.1308, Recent IC=+0.0831, 1st-half IC=+0.1338, 2nd-half IC=+0.1049, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.019, Q3_mid=+0.131, Q4=+0.096, Q5_high_vol=+0.181

**`combo_rel_diff__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0721, Sharpe=+0.0593)
- Admission: Train IC=+0.1392, Deflated=+0.1382, IR=0.50, Mono=0.68, p=0.0076, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.095 | 2017: +0.157 | 2018: +0.084 | 2019: +0.065 | 2020: +0.090 | 2021: +0.047 | 2022: +0.093 | 2023: +0.091 | 2024: +0.119 | 2025: +0.103 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.428 | 2016: +0.164 | 2017: +0.140 | 2018: +0.063 | 2019: +0.167 | 2020: +0.009 | 2021: +0.194 | 2022: +0.241 | 2023: +0.350 | 2024: +0.323 | 2025: +0.003 | 2026: +0.080
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.73
- Early IC=+0.1263, Recent IC=+0.0920, 1st-half IC=+0.0988, 2nd-half IC=+0.0767, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.049, Q3_mid=+0.120, Q4=+0.107, Q5_high_vol=+0.073

**`combo_max__first_bar_return__close_vs_open_range`** (Lock IC=+0.0749, Sharpe=+0.0494)
- Admission: Train IC=+0.2195, Deflated=+0.2202, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.109 | 2017: +0.209 | 2018: +0.218 | 2019: +0.101 | 2020: +0.141 | 2021: +0.125 | 2022: +0.123 | 2023: +0.085 | 2024: +0.136 | 2025: +0.121 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.043 | 2017: +0.258 | 2018: +0.337 | 2019: +0.164 | 2020: +0.276 | 2021: +0.244 | 2022: +0.235 | 2023: +0.337 | 2024: +0.264 | 2025: -0.124 | 2026: -0.473
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.66
- Early IC=+0.1588, Recent IC=+0.1040, 1st-half IC=+0.1509, 2nd-half IC=+0.1240, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.015, Q3_mid=+0.149, Q4=+0.150, Q5_high_vol=+0.167

**`combo_clamp_diff__bar_ret_0__h2_l2_pullback_continuation`** (Lock IC=+0.0748, Sharpe=+0.0395)
- Admission: Train IC=+0.1962, Deflated=+0.1957, IR=0.54, Mono=0.70, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.102 | 2017: +0.171 | 2018: +0.171 | 2019: +0.101 | 2020: +0.109 | 2021: +0.080 | 2022: +0.084 | 2023: +0.100 | 2024: +0.129 | 2025: +0.098 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.409 | 2016: -0.096 | 2017: +0.168 | 2018: +0.373 | 2019: +0.168 | 2020: +0.304 | 2021: +0.270 | 2022: +0.069 | 2023: +0.276 | 2024: +0.192 | 2025: +0.122 | 2026: -0.157
- IC CV=0.29, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.68
- Early IC=+0.1362, Recent IC=+0.0921, 1st-half IC=+0.1357, 2nd-half IC=+0.0958, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.038, Q3_mid=+0.146, Q4=+0.142, Q5_high_vol=+0.110

**`combo_rel_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0633, Sharpe=+0.0279)
- Admission: Train IC=+0.2253, Deflated=+0.2245, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.109 | 2017: +0.163 | 2018: +0.129 | 2019: +0.070 | 2020: +0.107 | 2021: +0.063 | 2022: +0.111 | 2023: +0.111 | 2024: +0.122 | 2025: +0.090 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.347 | 2017: +0.136 | 2018: +0.298 | 2019: +0.145 | 2020: +0.068 | 2021: +0.251 | 2022: +0.141 | 2023: +0.332 | 2024: +0.245 | 2025: -0.186 | 2026: -0.170
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.82
- Early IC=+0.1360, Recent IC=+0.1110, 1st-half IC=+0.1119, 2nd-half IC=+0.1039, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.031, Q3_mid=+0.124, Q4=+0.104, Q5_high_vol=+0.151

**`combo_tri_median__max_up_ret__net_volume_flow__bar_ret_0`** (Lock IC=+0.0637, Sharpe=+0.0275)
- Admission: Train IC=+0.2190, Deflated=+0.2195, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.091 | 2017: +0.209 | 2018: +0.211 | 2019: +0.103 | 2020: +0.125 | 2021: +0.109 | 2022: +0.085 | 2023: +0.089 | 2024: +0.121 | 2025: +0.081 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.176 | 2016: +0.095 | 2017: +0.366 | 2018: +0.359 | 2019: +0.068 | 2020: +0.245 | 2021: +0.307 | 2022: +0.101 | 2023: +0.258 | 2024: +0.197 | 2025: -0.090 | 2026: -0.476
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1499, Recent IC=+0.0871, 1st-half IC=+0.1473, 2nd-half IC=+0.1051, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.020, Q3_mid=+0.117, Q4=+0.149, Q5_high_vol=+0.165

**`combo_min__early_order_flow_imbalance__close_vs_open_range`** (Lock IC=+0.0608, Sharpe=+0.0246)
- Admission: Train IC=+0.1961, Deflated=+0.1960, IR=0.47, Mono=0.68, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.026 | 2017: +0.159 | 2018: +0.113 | 2019: +0.106 | 2020: +0.048 | 2021: +0.112 | 2022: +0.104 | 2023: +0.110 | 2024: +0.130 | 2025: +0.099 | 2026: -0.119
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.143 | 2017: +0.320 | 2018: +0.220 | 2019: +0.279 | 2020: +0.085 | 2021: +0.255 | 2022: +0.129 | 2023: +0.174 | 2024: +0.256 | 2025: +0.009 | 2026: -0.117
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=1.16
- Early IC=+0.0924, Recent IC=+0.1071, 1st-half IC=+0.1005, 2nd-half IC=+0.0916, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.023, Q3_mid=+0.077, Q4=+0.101, Q5_high_vol=+0.117

**`combo_max__first_bar_return__shaved_bar_trend_conviction`** (Lock IC=+0.0610, Sharpe=+0.0246)
- Admission: Train IC=+0.1663, Deflated=+0.1660, IR=0.45, Mono=0.66, p=0.0012, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.086 | 2017: +0.168 | 2018: +0.225 | 2019: +0.050 | 2020: +0.181 | 2021: +0.102 | 2022: +0.049 | 2023: +0.083 | 2024: +0.101 | 2025: +0.132 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.092 | 2016: -0.028 | 2017: +0.140 | 2018: +0.231 | 2019: +0.052 | 2020: +0.290 | 2021: +0.129 | 2022: +0.254 | 2023: +0.096 | 2024: +0.144 | 2025: +0.048 | 2026: -0.359
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=0.52
- Early IC=+0.1272, Recent IC=+0.0662, 1st-half IC=+0.1324, 2nd-half IC=+0.1068, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.19)
- Regime ICs: Q1_low_vol=+0.157, Q2=-0.032, Q3_mid=+0.127, Q4=+0.150, Q5_high_vol=+0.156

**`combo_max__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0866, Sharpe=+0.0051)
- Admission: Train IC=+0.1854, Deflated=+0.1856, IR=0.44, Mono=0.67, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.094 | 2017: +0.226 | 2018: +0.244 | 2019: +0.138 | 2020: +0.162 | 2021: +0.165 | 2022: +0.095 | 2023: +0.107 | 2024: +0.153 | 2025: +0.082 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.014 | 2017: +0.190 | 2018: +0.395 | 2019: +0.133 | 2020: +0.250 | 2021: +0.263 | 2022: +0.084 | 2023: +0.119 | 2024: +0.283 | 2025: -0.025 | 2026: -0.248
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.63
- Early IC=+0.1604, Recent IC=+0.1006, 1st-half IC=+0.1720, 2nd-half IC=+0.1322, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.236, Q2=-0.025, Q3_mid=+0.153, Q4=+0.165, Q5_high_vol=+0.203

### 159915ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`** (Lock IC=+0.1348, Sharpe=+1.8997)
- Admission: Train IC=+0.2202, Deflated=+0.2198, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.106 | 2017: +0.007 | 2018: +0.098 | 2019: +0.199 | 2020: +0.193 | 2021: +0.062 | 2022: +0.039 | 2023: +0.114 | 2024: +0.114 | 2025: +0.089 | 2026: +0.214
- Yearly Tail ICs:   2015: +0.251 | 2016: +0.206 | 2017: +0.075 | 2018: +0.299 | 2019: +0.363 | 2020: +0.381 | 2021: -0.055 | 2022: +0.073 | 2023: +0.338 | 2024: +0.467 | 2025: +0.091 | 2026: +0.413
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=1.36
- Early IC=+0.0566, Recent IC=+0.0768, 1st-half IC=+0.1120, 2nd-half IC=+0.1070, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=1.20)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.138, Q3_mid=+0.053, Q4=+0.075, Q5_high_vol=+0.179

**`combo_mean__first_bar_return__limit_down_proximity_early`** (Lock IC=+0.1170, Sharpe=+1.8672)
- Admission: Train IC=+0.1912, Deflated=+0.1915, IR=0.51, Mono=0.68, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.072 | 2017: -0.001 | 2018: +0.159 | 2019: +0.205 | 2020: +0.121 | 2021: +0.137 | 2022: +0.095 | 2023: +0.136 | 2024: +0.065 | 2025: +0.155 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.128 | 2016: +0.059 | 2017: +0.139 | 2018: +0.340 | 2019: +0.403 | 2020: +0.071 | 2021: +0.369 | 2022: +0.117 | 2023: +0.166 | 2024: +0.378 | 2025: +0.235 | 2026: +0.260
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.06, Recency ratio=3.25
- Early IC=+0.0355, Recent IC=+0.1156, 1st-half IC=+0.1140, 2nd-half IC=+0.1207, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.109, Q3_mid=+0.085, Q4=+0.104, Q5_high_vol=+0.175

**`combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature`** (Lock IC=+0.1345, Sharpe=+1.8390)
- Admission: Train IC=+0.2075, Deflated=+0.2073, IR=0.56, Mono=0.73, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.122 | 2017: -0.001 | 2018: +0.141 | 2019: +0.200 | 2020: +0.222 | 2021: +0.090 | 2022: +0.084 | 2023: +0.076 | 2024: +0.116 | 2025: +0.095 | 2026: +0.214
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.242 | 2017: -0.082 | 2018: +0.210 | 2019: +0.360 | 2020: +0.265 | 2021: +0.268 | 2022: +0.191 | 2023: +0.159 | 2024: +0.415 | 2025: -0.004 | 2026: +0.430
- IC CV=0.57, Neg years (linear/tail)=1/1 of 8, Half ratio=1.06, Recency ratio=1.32
- Early IC=+0.0607, Recent IC=+0.0801, 1st-half IC=+0.1180, 2nd-half IC=+0.1255, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=1.20)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.115, Q3_mid=+0.070, Q4=+0.107, Q5_high_vol=+0.195

**`combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1183, Sharpe=+1.7926)
- Admission: Train IC=+0.2208, Deflated=+0.2210, IR=0.55, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.086 | 2017: -0.029 | 2018: +0.142 | 2019: +0.226 | 2020: +0.125 | 2021: +0.132 | 2022: +0.087 | 2023: +0.104 | 2024: +0.071 | 2025: +0.134 | 2026: +0.133
- Yearly Tail ICs:   2015: +0.204 | 2016: +0.059 | 2017: +0.129 | 2018: +0.385 | 2019: +0.452 | 2020: +0.178 | 2021: +0.261 | 2022: +0.118 | 2023: +0.105 | 2024: +0.433 | 2025: +0.231 | 2026: +0.245
- IC CV=0.61, Neg years (linear/tail)=1/0 of 8, Half ratio=1.03, Recency ratio=3.37
- Early IC=+0.0283, Recent IC=+0.0954, 1st-half IC=+0.1106, 2nd-half IC=+0.1137, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.072, Q3_mid=+0.089, Q4=+0.119, Q5_high_vol=+0.153

**`combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1409, Sharpe=+1.7299)
- Admission: Train IC=+0.2630, Deflated=+0.2636, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.062 | 2017: -0.008 | 2018: +0.089 | 2019: +0.225 | 2020: +0.053 | 2021: +0.156 | 2022: +0.042 | 2023: +0.157 | 2024: +0.130 | 2025: +0.135 | 2026: +0.128
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.023 | 2017: +0.142 | 2018: +0.233 | 2019: +0.568 | 2020: +0.245 | 2021: +0.327 | 2022: +0.216 | 2023: +0.383 | 2024: +0.277 | 2025: +0.153 | 2026: +0.349
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=1.13, Recency ratio=4.05
- Early IC=+0.0248, Recent IC=+0.1002, 1st-half IC=+0.0972, 2nd-half IC=+0.1100, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.125, Q3_mid=+0.086, Q4=+0.113, Q5_high_vol=+0.132

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1283, Sharpe=+1.6959)
- Admission: Train IC=+0.2816, Deflated=+0.2820, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.124 | 2017: -0.001 | 2018: +0.125 | 2019: +0.213 | 2020: +0.067 | 2021: +0.189 | 2022: +0.060 | 2023: +0.148 | 2024: +0.120 | 2025: +0.140 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.063 | 2017: +0.103 | 2018: +0.280 | 2019: +0.527 | 2020: +0.305 | 2021: +0.389 | 2022: +0.110 | 2023: +0.381 | 2024: +0.281 | 2025: +0.148 | 2026: +0.325
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.04, Recency ratio=1.71
- Early IC=+0.0616, Recent IC=+0.1054, 1st-half IC=+0.1213, 2nd-half IC=+0.1264, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.137, Q3_mid=+0.089, Q4=+0.134, Q5_high_vol=+0.176

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1262, Sharpe=+1.6796)
- Admission: Train IC=+0.2614, Deflated=+0.2610, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.134 | 2017: +0.006 | 2018: +0.168 | 2019: +0.235 | 2020: +0.165 | 2021: +0.161 | 2022: +0.114 | 2023: +0.154 | 2024: +0.100 | 2025: +0.172 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.040 | 2016: +0.101 | 2017: +0.003 | 2018: +0.298 | 2019: +0.547 | 2020: +0.258 | 2021: +0.282 | 2022: +0.236 | 2023: +0.348 | 2024: +0.477 | 2025: +0.219 | 2026: -0.017
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.90
- Early IC=+0.0703, Recent IC=+0.1339, 1st-half IC=+0.1368, 2nd-half IC=+0.1485, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.122, Q3_mid=+0.115, Q4=+0.150, Q5_high_vol=+0.202

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1220, Sharpe=+1.6687)
- Admission: Train IC=+0.2053, Deflated=+0.2055, IR=0.39, Mono=0.66, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.125 | 2017: +0.063 | 2018: +0.203 | 2019: +0.218 | 2020: +0.208 | 2021: +0.107 | 2022: +0.109 | 2023: +0.085 | 2024: +0.084 | 2025: +0.105 | 2026: +0.184
- Yearly Tail ICs:   2015: -0.007 | 2016: +0.238 | 2017: -0.064 | 2018: +0.343 | 2019: +0.419 | 2020: +0.291 | 2021: +0.334 | 2022: +0.126 | 2023: +0.015 | 2024: +0.325 | 2025: +0.059 | 2026: +0.377
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.87, Recency ratio=1.04
- Early IC=+0.0940, Recent IC=+0.0973, 1st-half IC=+0.1506, 2nd-half IC=+0.1314, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.109, Q3_mid=+0.081, Q4=+0.149, Q5_high_vol=+0.223

**`combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1399, Sharpe=+1.6539)
- Admission: Train IC=+0.1933, Deflated=+0.1933, IR=0.49, Mono=0.69, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.057 | 2017: -0.043 | 2018: +0.098 | 2019: +0.252 | 2020: +0.140 | 2021: +0.106 | 2022: +0.045 | 2023: +0.125 | 2024: +0.107 | 2025: +0.153 | 2026: +0.144
- Yearly Tail ICs:   2015: +0.193 | 2016: +0.023 | 2017: -0.050 | 2018: +0.384 | 2019: +0.492 | 2020: +0.238 | 2021: +0.264 | 2022: +0.186 | 2023: +0.261 | 2024: +0.450 | 2025: +0.182 | 2026: +0.407
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=1.11, Recency ratio=12.14
- Early IC=+0.0070, Recent IC=+0.0852, 1st-half IC=+0.0950, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.088, Q3_mid=+0.088, Q4=+0.098, Q5_high_vol=+0.126

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1399, Sharpe=+1.6539)
- Admission: Train IC=+0.1933, Deflated=+0.1933, IR=0.49, Mono=0.69, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.057 | 2017: -0.043 | 2018: +0.098 | 2019: +0.252 | 2020: +0.140 | 2021: +0.106 | 2022: +0.045 | 2023: +0.125 | 2024: +0.107 | 2025: +0.153 | 2026: +0.144
- Yearly Tail ICs:   2015: +0.193 | 2016: +0.023 | 2017: -0.050 | 2018: +0.384 | 2019: +0.492 | 2020: +0.238 | 2021: +0.264 | 2022: +0.186 | 2023: +0.261 | 2024: +0.450 | 2025: +0.182 | 2026: +0.407
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=1.11, Recency ratio=12.14
- Early IC=+0.0070, Recent IC=+0.0852, 1st-half IC=+0.0950, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.088, Q3_mid=+0.088, Q4=+0.098, Q5_high_vol=+0.126

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum`** (Lock IC=+0.1257, Sharpe=+1.6419)
- Admission: Train IC=+0.2013, Deflated=+0.2015, IR=0.41, Mono=0.66, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.105 | 2017: +0.007 | 2018: +0.151 | 2019: +0.232 | 2020: +0.140 | 2021: +0.103 | 2022: +0.127 | 2023: +0.123 | 2024: +0.102 | 2025: +0.069 | 2026: +0.214
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.165 | 2017: +0.007 | 2018: +0.152 | 2019: +0.342 | 2020: +0.250 | 2021: +0.284 | 2022: +0.177 | 2023: +0.166 | 2024: +0.212 | 2025: +0.251 | 2026: +0.397
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=2.23
- Early IC=+0.0560, Recent IC=+0.1249, 1st-half IC=+0.1284, 2nd-half IC=+0.1254, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.117, Q3_mid=+0.063, Q4=+0.174, Q5_high_vol=+0.166

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1269, Sharpe=+1.6160)
- Admission: Train IC=+0.2595, Deflated=+0.2596, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.154 | 2017: -0.012 | 2018: +0.169 | 2019: +0.219 | 2020: +0.182 | 2021: +0.161 | 2022: +0.123 | 2023: +0.122 | 2024: +0.085 | 2025: +0.152 | 2026: +0.136
- Yearly Tail ICs:   2015: -0.046 | 2016: +0.193 | 2017: +0.029 | 2018: +0.343 | 2019: +0.427 | 2020: +0.272 | 2021: +0.327 | 2022: +0.186 | 2023: +0.174 | 2024: +0.409 | 2025: +0.175 | 2026: +0.234
- IC CV=0.46, Neg years (linear/tail)=1/0 of 8, Half ratio=1.11, Recency ratio=1.74
- Early IC=+0.0706, Recent IC=+0.1226, 1st-half IC=+0.1378, 2nd-half IC=+0.1523, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.119, Q3_mid=+0.099, Q4=+0.151, Q5_high_vol=+0.215

**`combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1171, Sharpe=+1.6028)
- Admission: Train IC=+0.1926, Deflated=+0.1920, IR=0.54, Mono=0.69, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.141 | 2017: -0.005 | 2018: +0.063 | 2019: +0.178 | 2020: +0.170 | 2021: +0.115 | 2022: +0.079 | 2023: +0.075 | 2024: +0.122 | 2025: +0.138 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.191 | 2016: +0.091 | 2017: +0.228 | 2018: +0.225 | 2019: +0.200 | 2020: +0.091 | 2021: +0.405 | 2022: +0.153 | 2023: +0.142 | 2024: +0.253 | 2025: +0.389 | 2026: -0.059
- IC CV=0.56, Neg years (linear/tail)=1/0 of 8, Half ratio=1.19, Recency ratio=1.13
- Early IC=+0.0683, Recent IC=+0.0774, 1st-half IC=+0.0950, 2nd-half IC=+0.1133, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.082, Q3_mid=+0.097, Q4=+0.103, Q5_high_vol=+0.120

**`combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1316, Sharpe=+1.5821)
- Admission: Train IC=+0.2883, Deflated=+0.2887, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.148 | 2016: +0.125 | 2017: +0.004 | 2018: +0.128 | 2019: +0.223 | 2020: +0.061 | 2021: +0.180 | 2022: +0.048 | 2023: +0.147 | 2024: +0.127 | 2025: +0.139 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.019 | 2016: +0.051 | 2017: +0.132 | 2018: +0.244 | 2019: +0.585 | 2020: +0.296 | 2021: +0.365 | 2022: +0.176 | 2023: +0.386 | 2024: +0.272 | 2025: +0.163 | 2026: +0.287
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=1.51
- Early IC=+0.0646, Recent IC=+0.0975, 1st-half IC=+0.1268, 2nd-half IC=+0.1187, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.141, Q3_mid=+0.089, Q4=+0.132, Q5_high_vol=+0.172

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1334, Sharpe=+1.5762)
- Admission: Train IC=+0.2347, Deflated=+0.2333, IR=0.47, Mono=0.66, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.101 | 2017: +0.046 | 2018: +0.177 | 2019: +0.236 | 2020: +0.155 | 2021: +0.128 | 2022: +0.156 | 2023: +0.167 | 2024: +0.123 | 2025: +0.146 | 2026: +0.125
- Yearly Tail ICs:   2015: +0.102 | 2016: +0.032 | 2017: -0.056 | 2018: +0.500 | 2019: +0.547 | 2020: +0.267 | 2021: +0.174 | 2022: +0.177 | 2023: +0.346 | 2024: +0.331 | 2025: +0.225 | 2026: +0.125
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=1.05, Recency ratio=2.19
- Early IC=+0.0735, Recent IC=+0.1614, 1st-half IC=+0.1414, 2nd-half IC=+0.1485, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.135, Q3_mid=+0.093, Q4=+0.170, Q5_high_vol=+0.201

**`combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1202, Sharpe=+1.5593)
- Admission: Train IC=+0.2465, Deflated=+0.2466, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.126 | 2017: -0.008 | 2018: +0.179 | 2019: +0.220 | 2020: +0.147 | 2021: +0.152 | 2022: +0.102 | 2023: +0.145 | 2024: +0.083 | 2025: +0.161 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.036 | 2017: +0.210 | 2018: +0.303 | 2019: +0.380 | 2020: +0.213 | 2021: +0.400 | 2022: +0.144 | 2023: +0.182 | 2024: +0.366 | 2025: +0.236 | 2026: +0.181
- IC CV=0.47, Neg years (linear/tail)=1/0 of 8, Half ratio=1.04, Recency ratio=2.10
- Early IC=+0.0591, Recent IC=+0.1238, 1st-half IC=+0.1315, 2nd-half IC=+0.1367, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.114, Q3_mid=+0.099, Q4=+0.121, Q5_high_vol=+0.206

**`combo_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1258, Sharpe=+1.5522)
- Admission: Train IC=+0.2292, Deflated=+0.2297, IR=0.52, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.092 | 2017: +0.055 | 2018: +0.171 | 2019: +0.175 | 2020: +0.191 | 2021: +0.049 | 2022: +0.062 | 2023: +0.130 | 2024: +0.102 | 2025: +0.119 | 2026: +0.166
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.114 | 2017: -0.021 | 2018: +0.469 | 2019: +0.479 | 2020: +0.360 | 2021: +0.136 | 2022: +0.044 | 2023: +0.207 | 2024: +0.472 | 2025: +0.217 | 2026: +0.381
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.87, Recency ratio=1.30
- Early IC=+0.0735, Recent IC=+0.0958, 1st-half IC=+0.1215, 2nd-half IC=+0.1053, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.105, Q3_mid=+0.042, Q4=+0.079, Q5_high_vol=+0.222

**`combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0`** (Lock IC=+0.1291, Sharpe=+1.5409)
- Admission: Train IC=+0.2504, Deflated=+0.2508, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.082 | 2017: -0.041 | 2018: +0.111 | 2019: +0.257 | 2020: +0.138 | 2021: +0.121 | 2022: +0.073 | 2023: +0.149 | 2024: +0.103 | 2025: +0.152 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.226 | 2016: +0.103 | 2017: -0.014 | 2018: +0.321 | 2019: +0.489 | 2020: +0.243 | 2021: +0.354 | 2022: +0.252 | 2023: +0.350 | 2024: +0.387 | 2025: +0.110 | 2026: +0.259
- IC CV=0.70, Neg years (linear/tail)=1/1 of 8, Half ratio=1.13, Recency ratio=5.36
- Early IC=+0.0207, Recent IC=+0.1112, 1st-half IC=+0.1072, 2nd-half IC=+0.1209, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.112, Q3_mid=+0.092, Q4=+0.104, Q5_high_vol=+0.165

**`combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1193, Sharpe=+1.5252)
- Admission: Train IC=+0.2576, Deflated=+0.2579, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.121 | 2017: +0.010 | 2018: +0.185 | 2019: +0.197 | 2020: +0.152 | 2021: +0.177 | 2022: +0.130 | 2023: +0.133 | 2024: +0.071 | 2025: +0.163 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.100 | 2016: +0.138 | 2017: +0.106 | 2018: +0.390 | 2019: +0.395 | 2020: +0.218 | 2021: +0.436 | 2022: +0.152 | 2023: +0.171 | 2024: +0.406 | 2025: +0.177 | 2026: +0.149
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.19, Recency ratio=2.01
- Early IC=+0.0653, Recent IC=+0.1314, 1st-half IC=+0.1283, 2nd-half IC=+0.1527, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.136, Q3_mid=+0.094, Q4=+0.136, Q5_high_vol=+0.213

**`combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1330, Sharpe=+1.4975)
- Admission: Train IC=+0.2816, Deflated=+0.2816, IR=0.70, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.101 | 2017: -0.012 | 2018: +0.121 | 2019: +0.242 | 2020: +0.149 | 2021: +0.111 | 2022: +0.068 | 2023: +0.164 | 2024: +0.115 | 2025: +0.156 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.153 | 2017: +0.007 | 2018: +0.431 | 2019: +0.468 | 2020: +0.411 | 2021: +0.276 | 2022: +0.253 | 2023: +0.384 | 2024: +0.456 | 2025: +0.182 | 2026: +0.263
- IC CV=0.58, Neg years (linear/tail)=1/0 of 8, Half ratio=1.11, Recency ratio=2.58
- Early IC=+0.0448, Recent IC=+0.1157, 1st-half IC=+0.1136, 2nd-half IC=+0.1258, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.125, Q3_mid=+0.092, Q4=+0.112, Q5_high_vol=+0.176

**`combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1315, Sharpe=+1.4786)
- Admission: Train IC=+0.2142, Deflated=+0.2137, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.060 | 2017: +0.018 | 2018: +0.131 | 2019: +0.209 | 2020: +0.112 | 2021: +0.148 | 2022: +0.120 | 2023: +0.146 | 2024: +0.122 | 2025: +0.152 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.064 | 2017: +0.072 | 2018: +0.242 | 2019: +0.460 | 2020: +0.158 | 2021: +0.237 | 2022: +0.209 | 2023: +0.298 | 2024: +0.354 | 2025: +0.108 | 2026: +0.186
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=3.43
- Early IC=+0.0388, Recent IC=+0.1332, 1st-half IC=+0.1099, 2nd-half IC=+0.1346, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.124, Q3_mid=+0.101, Q4=+0.144, Q5_high_vol=+0.149

**`combo_min__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.1271, Sharpe=+1.4730)
- Admission: Train IC=+0.1899, Deflated=+0.1902, IR=0.58, Mono=0.68, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.055 | 2017: -0.027 | 2018: +0.080 | 2019: +0.250 | 2020: +0.118 | 2021: +0.095 | 2022: +0.058 | 2023: +0.125 | 2024: +0.082 | 2025: +0.153 | 2026: +0.123
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.045 | 2017: +0.022 | 2018: +0.247 | 2019: +0.503 | 2020: +0.141 | 2021: +0.354 | 2022: +0.261 | 2023: +0.130 | 2024: +0.444 | 2025: +0.051 | 2026: +0.302
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.02, Recency ratio=6.45
- Early IC=+0.0142, Recent IC=+0.0913, 1st-half IC=+0.0935, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.092, Q3_mid=+0.080, Q4=+0.089, Q5_high_vol=+0.111

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1321, Sharpe=+1.4384)
- Admission: Train IC=+0.2752, Deflated=+0.2752, IR=0.94, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.079 | 2017: -0.005 | 2018: +0.082 | 2019: +0.155 | 2020: +0.093 | 2021: +0.184 | 2022: +0.120 | 2023: +0.154 | 2024: +0.083 | 2025: +0.210 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.049 | 2016: +0.286 | 2017: +0.150 | 2018: +0.244 | 2019: +0.341 | 2020: +0.308 | 2021: +0.283 | 2022: +0.244 | 2023: +0.337 | 2024: +0.448 | 2025: +0.357 | 2026: +0.173
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.90, Recency ratio=3.73
- Early IC=+0.0368, Recent IC=+0.1372, 1st-half IC=+0.0764, 2nd-half IC=+0.1448, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.150, Q3_mid=+0.077, Q4=+0.114, Q5_high_vol=+0.152

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1329, Sharpe=+1.4350)
- Admission: Train IC=+0.2049, Deflated=+0.2033, IR=0.61, Mono=0.74, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.157 | 2016: +0.094 | 2017: +0.014 | 2018: +0.052 | 2019: +0.147 | 2020: +0.139 | 2021: +0.146 | 2022: +0.102 | 2023: +0.159 | 2024: +0.149 | 2025: +0.192 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.298 | 2016: +0.112 | 2017: +0.148 | 2018: +0.079 | 2019: +0.307 | 2020: +0.312 | 2021: +0.201 | 2022: +0.293 | 2023: +0.325 | 2024: +0.358 | 2025: +0.344 | 2026: +0.077
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.91, Recency ratio=2.40
- Early IC=+0.0543, Recent IC=+0.1306, 1st-half IC=+0.0724, 2nd-half IC=+0.1386, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.127, Q3_mid=+0.096, Q4=+0.103, Q5_high_vol=+0.170

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1247, Sharpe=+1.4204)
- Admission: Train IC=+0.2434, Deflated=+0.2438, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.073 | 2017: -0.020 | 2018: +0.100 | 2019: +0.254 | 2020: +0.122 | 2021: +0.109 | 2022: +0.080 | 2023: +0.148 | 2024: +0.090 | 2025: +0.155 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.072 | 2017: +0.019 | 2018: +0.277 | 2019: +0.481 | 2020: +0.204 | 2021: +0.300 | 2022: +0.244 | 2023: +0.203 | 2024: +0.379 | 2025: +0.089 | 2026: +0.270
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=1.08, Recency ratio=4.36
- Early IC=+0.0265, Recent IC=+0.1154, 1st-half IC=+0.1057, 2nd-half IC=+0.1142, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.127, Q3_mid=+0.074, Q4=+0.099, Q5_high_vol=+0.154

**`combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1258, Sharpe=+1.4182)
- Admission: Train IC=+0.3042, Deflated=+0.3038, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.092 | 2017: +0.003 | 2018: +0.161 | 2019: +0.230 | 2020: +0.135 | 2021: +0.149 | 2022: +0.109 | 2023: +0.185 | 2024: +0.114 | 2025: +0.192 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.219 | 2016: +0.102 | 2017: +0.087 | 2018: +0.360 | 2019: +0.526 | 2020: +0.390 | 2021: +0.305 | 2022: +0.327 | 2023: +0.448 | 2024: +0.415 | 2025: +0.217 | 2026: +0.298
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=3.10
- Early IC=+0.0474, Recent IC=+0.1470, 1st-half IC=+0.1277, 2nd-half IC=+0.1488, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.044, Q2=+0.175, Q3_mid=+0.122, Q4=+0.153, Q5_high_vol=+0.161

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1191, Sharpe=+1.3989)
- Admission: Train IC=+0.2473, Deflated=+0.2472, IR=0.69, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.131 | 2017: +0.009 | 2018: +0.116 | 2019: +0.207 | 2020: +0.160 | 2021: +0.158 | 2022: +0.128 | 2023: +0.164 | 2024: +0.081 | 2025: +0.174 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.177 | 2017: +0.053 | 2018: +0.295 | 2019: +0.445 | 2020: +0.180 | 2021: +0.368 | 2022: +0.285 | 2023: +0.268 | 2024: +0.296 | 2025: +0.125 | 2026: +0.032
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.44, Recency ratio=2.17
- Early IC=+0.0683, Recent IC=+0.1486, 1st-half IC=+0.1132, 2nd-half IC=+0.1631, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.159, Q3_mid=+0.101, Q4=+0.137, Q5_high_vol=+0.190

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1231, Sharpe=+1.3859)
- Admission: Train IC=+0.2609, Deflated=+0.2610, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.143 | 2017: +0.015 | 2018: +0.120 | 2019: +0.197 | 2020: +0.163 | 2021: +0.157 | 2022: +0.120 | 2023: +0.159 | 2024: +0.085 | 2025: +0.174 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.264 | 2017: +0.083 | 2018: +0.366 | 2019: +0.316 | 2020: +0.254 | 2021: +0.345 | 2022: +0.292 | 2023: +0.173 | 2024: +0.334 | 2025: +0.193 | 2026: +0.246
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.34, Recency ratio=1.76
- Early IC=+0.0791, Recent IC=+0.1394, 1st-half IC=+0.1182, 2nd-half IC=+0.1582, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.057, Q2=+0.149, Q3_mid=+0.102, Q4=+0.139, Q5_high_vol=+0.186

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1262, Sharpe=+1.3787)
- Admission: Train IC=+0.2412, Deflated=+0.2405, IR=0.54, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.126 | 2017: +0.034 | 2018: +0.183 | 2019: +0.217 | 2020: +0.163 | 2021: +0.145 | 2022: +0.142 | 2023: +0.130 | 2024: +0.112 | 2025: +0.126 | 2026: +0.139
- Yearly Tail ICs:   2015: +0.033 | 2016: +0.200 | 2017: -0.052 | 2018: +0.496 | 2019: +0.545 | 2020: +0.214 | 2021: +0.192 | 2022: +0.078 | 2023: +0.170 | 2024: +0.262 | 2025: +0.292 | 2026: +0.301
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=1.01, Recency ratio=1.69
- Early IC=+0.0804, Recent IC=+0.1360, 1st-half IC=+0.1427, 2nd-half IC=+0.1447, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.058, Q2=+0.134, Q3_mid=+0.097, Q4=+0.182, Q5_high_vol=+0.191

**`combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.1190, Sharpe=+1.3567)
- Admission: Train IC=+0.2273, Deflated=+0.2273, IR=0.66, Mono=0.76, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.063 | 2017: +0.036 | 2018: +0.086 | 2019: +0.181 | 2020: +0.058 | 2021: +0.182 | 2022: +0.056 | 2023: +0.127 | 2024: +0.087 | 2025: +0.155 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.057 | 2017: +0.105 | 2018: +0.236 | 2019: +0.276 | 2020: +0.199 | 2021: +0.344 | 2022: +0.219 | 2023: +0.345 | 2024: +0.284 | 2025: +0.166 | 2026: +0.168
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=2.14
- Early IC=+0.0464, Recent IC=+0.0992, 1st-half IC=+0.0957, 2nd-half IC=+0.1195, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.34)
- Regime ICs: Q1_low_vol=+0.028, Q2=+0.148, Q3_mid=+0.107, Q4=+0.108, Q5_high_vol=+0.124

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1277, Sharpe=+1.2801)
- Admission: Train IC=+0.3031, Deflated=+0.3031, IR=0.79, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.121 | 2017: -0.012 | 2018: +0.160 | 2019: +0.257 | 2020: +0.175 | 2021: +0.138 | 2022: +0.085 | 2023: +0.153 | 2024: +0.094 | 2025: +0.162 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.087 | 2016: +0.190 | 2017: +0.035 | 2018: +0.423 | 2019: +0.551 | 2020: +0.375 | 2021: +0.314 | 2022: +0.215 | 2023: +0.351 | 2024: +0.447 | 2025: +0.293 | 2026: +0.293
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=1.04, Recency ratio=2.19
- Early IC=+0.0543, Recent IC=+0.1189, 1st-half IC=+0.1372, 2nd-half IC=+0.1421, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.142, Q3_mid=+0.099, Q4=+0.126, Q5_high_vol=+0.209

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1161, Sharpe=+1.2784)
- Admission: Train IC=+0.2780, Deflated=+0.2774, IR=0.90, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.060 | 2017: +0.030 | 2018: +0.134 | 2019: +0.207 | 2020: +0.147 | 2021: +0.166 | 2022: +0.103 | 2023: +0.170 | 2024: +0.062 | 2025: +0.189 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.054 | 2017: +0.213 | 2018: +0.323 | 2019: +0.334 | 2020: +0.430 | 2021: +0.322 | 2022: +0.358 | 2023: +0.266 | 2024: +0.293 | 2025: +0.176 | 2026: +0.373
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.30, Recency ratio=3.03
- Early IC=+0.0450, Recent IC=+0.1364, 1st-half IC=+0.1147, 2nd-half IC=+0.1497, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.145, Q3_mid=+0.120, Q4=+0.148, Q5_high_vol=+0.168

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1249, Sharpe=+1.2583)
- Admission: Train IC=+0.2224, Deflated=+0.2216, IR=0.54, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.113 | 2017: +0.019 | 2018: +0.094 | 2019: +0.229 | 2020: +0.134 | 2021: +0.137 | 2022: +0.100 | 2023: +0.163 | 2024: +0.072 | 2025: +0.221 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.385 | 2016: +0.093 | 2017: +0.045 | 2018: +0.145 | 2019: +0.448 | 2020: +0.312 | 2021: +0.229 | 2022: +0.152 | 2023: +0.409 | 2024: +0.330 | 2025: +0.355 | 2026: +0.143
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=2.00
- Early IC=+0.0657, Recent IC=+0.1317, 1st-half IC=+0.1113, 2nd-half IC=+0.1374, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.148, Q3_mid=+0.100, Q4=+0.105, Q5_high_vol=+0.177

**`combo_rank_min__max_up_ret__gap_pct`** (Lock IC=+0.1020, Sharpe=+1.2477)
- Admission: Train IC=+0.2010, Deflated=+0.2004, IR=0.52, Mono=0.71, p=0.0002, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.045 | 2017: -0.018 | 2018: +0.036 | 2019: +0.226 | 2020: +0.136 | 2021: +0.125 | 2022: +0.078 | 2023: +0.085 | 2024: +0.060 | 2025: +0.128 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.177 | 2016: +0.107 | 2017: +0.108 | 2018: +0.286 | 2019: +0.470 | 2020: +0.117 | 2021: +0.354 | 2022: +0.076 | 2023: +0.154 | 2024: +0.197 | 2025: +0.081 | 2026: +0.111
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=1.65, Recency ratio=17.82
- Early IC=+0.0043, Recent IC=+0.0762, 1st-half IC=+0.0721, 2nd-half IC=+0.1192, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.109, Q3_mid=+0.087, Q4=+0.094, Q5_high_vol=+0.113

**`combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.1080, Sharpe=+1.2363)
- Admission: Train IC=+0.2122, Deflated=+0.2120, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.056 | 2017: +0.026 | 2018: +0.097 | 2019: +0.223 | 2020: +0.058 | 2021: +0.193 | 2022: +0.056 | 2023: +0.122 | 2024: +0.075 | 2025: +0.137 | 2026: +0.094
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.024 | 2017: +0.062 | 2018: +0.187 | 2019: +0.393 | 2020: +0.158 | 2021: +0.366 | 2022: +0.183 | 2023: +0.343 | 2024: +0.282 | 2025: +0.138 | 2026: +0.152
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=2.20
- Early IC=+0.0406, Recent IC=+0.0892, 1st-half IC=+0.1041, 2nd-half IC=+0.1177, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.34)
- Regime ICs: Q1_low_vol=+0.031, Q2=+0.146, Q3_mid=+0.119, Q4=+0.109, Q5_high_vol=+0.130

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1164, Sharpe=+1.2316)
- Admission: Train IC=+0.2656, Deflated=+0.2655, IR=0.54, Mono=0.74, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.148 | 2017: +0.007 | 2018: +0.162 | 2019: +0.210 | 2020: +0.168 | 2021: +0.174 | 2022: +0.130 | 2023: +0.138 | 2024: +0.072 | 2025: +0.179 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.053 | 2016: +0.209 | 2017: +0.055 | 2018: +0.304 | 2019: +0.390 | 2020: +0.218 | 2021: +0.350 | 2022: +0.269 | 2023: +0.251 | 2024: +0.381 | 2025: +0.217 | 2026: +0.019
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.73
- Early IC=+0.0777, Recent IC=+0.1343, 1st-half IC=+0.1270, 2nd-half IC=+0.1562, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.126, Q3_mid=+0.111, Q4=+0.141, Q5_high_vol=+0.212

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1267, Sharpe=+1.2245)
- Admission: Train IC=+0.2633, Deflated=+0.2628, IR=0.59, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.072 | 2017: +0.030 | 2018: +0.134 | 2019: +0.197 | 2020: +0.126 | 2021: +0.156 | 2022: +0.132 | 2023: +0.161 | 2024: +0.119 | 2025: +0.179 | 2026: +0.037
- Yearly Tail ICs:   2015: +0.085 | 2016: +0.141 | 2017: +0.086 | 2018: +0.228 | 2019: +0.531 | 2020: +0.146 | 2021: +0.260 | 2022: +0.321 | 2023: +0.395 | 2024: +0.362 | 2025: +0.164 | 2026: +0.029
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.38, Recency ratio=2.86
- Early IC=+0.0512, Recent IC=+0.1464, 1st-half IC=+0.1061, 2nd-half IC=+0.1461, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.132, Q3_mid=+0.109, Q4=+0.137, Q5_high_vol=+0.177

**`combo_tri_median__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0`** (Lock IC=+0.1209, Sharpe=+1.2194)
- Admission: Train IC=+0.2005, Deflated=+0.1997, IR=0.57, Mono=0.69, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.186 | 2017: -0.017 | 2018: +0.103 | 2019: +0.185 | 2020: +0.186 | 2021: +0.130 | 2022: +0.076 | 2023: +0.102 | 2024: +0.108 | 2025: +0.136 | 2026: +0.123
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.153 | 2017: +0.178 | 2018: +0.330 | 2019: +0.181 | 2020: +0.128 | 2021: +0.310 | 2022: +0.201 | 2023: +0.176 | 2024: +0.329 | 2025: +0.430 | 2026: -0.153
- IC CV=0.55, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=1.05
- Early IC=+0.0846, Recent IC=+0.0889, 1st-half IC=+0.1130, 2nd-half IC=+0.1242, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.093, Q3_mid=+0.105, Q4=+0.111, Q5_high_vol=+0.174

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1042, Sharpe=+1.2122)
- Admission: Train IC=+0.1458, Deflated=+0.1452, IR=0.33, Mono=0.67, p=0.0050, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.021 | 2017: +0.033 | 2018: +0.073 | 2019: +0.158 | 2020: +0.050 | 2021: +0.127 | 2022: +0.136 | 2023: +0.121 | 2024: +0.109 | 2025: +0.108 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.067 | 2017: +0.104 | 2018: +0.076 | 2019: +0.356 | 2020: -0.022 | 2021: +0.237 | 2022: +0.053 | 2023: +0.176 | 2024: +0.309 | 2025: +0.181 | 2026: -0.043
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.46, Recency ratio=4.49
- Early IC=+0.0293, Recent IC=+0.1318, 1st-half IC=+0.0745, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.104, Q3_mid=+0.054, Q4=+0.109, Q5_high_vol=+0.124

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0`** (Lock IC=+0.0920, Sharpe=+1.2053)
- Admission: Train IC=+0.2367, Deflated=+0.2367, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.253 | 2017: -0.021 | 2018: +0.203 | 2019: +0.191 | 2020: +0.192 | 2021: +0.119 | 2022: +0.062 | 2023: +0.052 | 2024: +0.078 | 2025: +0.061 | 2026: +0.162
- Yearly Tail ICs:   2015: +0.014 | 2016: +0.328 | 2017: -0.030 | 2018: +0.275 | 2019: +0.356 | 2020: +0.261 | 2021: +0.275 | 2022: +0.081 | 2023: +0.122 | 2024: +0.382 | 2025: +0.159 | 2026: +0.263
- IC CV=0.67, Neg years (linear/tail)=1/1 of 8, Half ratio=0.71, Recency ratio=0.49
- Early IC=+0.1164, Recent IC=+0.0566, 1st-half IC=+0.1534, 2nd-half IC=+0.1084, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.049, Q3_mid=+0.074, Q4=+0.153, Q5_high_vol=+0.216

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1291, Sharpe=+1.1684)
- Admission: Train IC=+0.2593, Deflated=+0.2594, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.49, Neg years (linear/tail)=1/0 of 8, Half ratio=1.95, Recency ratio=3.70
- Early IC=+0.0401, Recent IC=+0.1487, 1st-half IC=+0.0767, 2nd-half IC=+0.1493, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.154, Q3_mid=+0.073, Q4=+0.110, Q5_high_vol=+0.155

**`combo_mean__max_up_ret__gap_pct`** (Lock IC=+0.1371, Sharpe=+1.1159)
- Admission: Train IC=+0.2374, Deflated=+0.2374, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.097 | 2017: +0.006 | 2018: +0.133 | 2019: +0.159 | 2020: +0.145 | 2021: +0.151 | 2022: +0.164 | 2023: +0.127 | 2024: +0.109 | 2025: +0.161 | 2026: +0.140
- Yearly Tail ICs:   2015: -0.053 | 2016: +0.269 | 2017: +0.091 | 2018: +0.347 | 2019: +0.275 | 2020: +0.157 | 2021: +0.343 | 2022: +0.182 | 2023: +0.015 | 2024: +0.228 | 2025: +0.045 | 2026: +0.236
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.64, Recency ratio=2.81
- Early IC=+0.0519, Recent IC=+0.1457, 1st-half IC=+0.0967, 2nd-half IC=+0.1582, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.150, Q3_mid=+0.069, Q4=+0.147, Q5_high_vol=+0.189

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1204, Sharpe=+1.1103)
- Admission: Train IC=+0.2306, Deflated=+0.2298, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.203 | 2016: -0.012 | 2017: -0.014 | 2018: +0.077 | 2019: +0.224 | 2020: +0.104 | 2021: +0.111 | 2022: +0.092 | 2023: +0.164 | 2024: +0.067 | 2025: +0.174 | 2026: +0.116
- Yearly Tail ICs:   2015: +0.210 | 2016: -0.107 | 2017: +0.066 | 2018: +0.349 | 2019: +0.484 | 2020: +0.155 | 2021: +0.309 | 2022: +0.301 | 2023: +0.392 | 2024: +0.284 | 2025: +0.131 | 2026: +0.337
- IC CV=0.81, Neg years (linear/tail)=2/1 of 8, Half ratio=1.49, Recency ratio=-9.71
- Early IC=-0.0130, Recent IC=+0.1265, 1st-half IC=+0.0765, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.113, Q3_mid=+0.107, Q4=+0.106, Q5_high_vol=+0.093

**`combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1385, Sharpe=+1.1011)
- Admission: Train IC=+0.1854, Deflated=+0.1852, IR=0.44, Mono=0.68, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.039 | 2017: +0.021 | 2018: +0.084 | 2019: +0.157 | 2020: +0.086 | 2021: +0.147 | 2022: +0.132 | 2023: +0.128 | 2024: +0.112 | 2025: +0.181 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.028 | 2016: +0.129 | 2017: +0.147 | 2018: +0.128 | 2019: +0.413 | 2020: +0.070 | 2021: +0.163 | 2022: +0.216 | 2023: +0.194 | 2024: +0.367 | 2025: +0.182 | 2026: +0.025
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.80, Recency ratio=4.33
- Early IC=+0.0300, Recent IC=+0.1300, 1st-half IC=+0.0726, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.090, Q3_mid=+0.089, Q4=+0.102, Q5_high_vol=+0.136

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1248, Sharpe=+1.0992)
- Admission: Train IC=+0.2786, Deflated=+0.2786, IR=0.64, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.121 | 2017: -0.019 | 2018: +0.157 | 2019: +0.240 | 2020: +0.166 | 2021: +0.144 | 2022: +0.095 | 2023: +0.154 | 2024: +0.081 | 2025: +0.171 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.089 | 2017: -0.027 | 2018: +0.488 | 2019: +0.475 | 2020: +0.344 | 2021: +0.352 | 2022: +0.141 | 2023: +0.267 | 2024: +0.322 | 2025: +0.369 | 2026: +0.282
- IC CV=0.52, Neg years (linear/tail)=1/1 of 8, Half ratio=1.14, Recency ratio=2.47
- Early IC=+0.0507, Recent IC=+0.1255, 1st-half IC=+0.1271, 2nd-half IC=+0.1447, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.146, Q3_mid=+0.073, Q4=+0.122, Q5_high_vol=+0.215

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1227, Sharpe=+1.0991)
- Admission: Train IC=+0.1875, Deflated=+0.1867, IR=0.60, Mono=0.72, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.101 | 2017: +0.021 | 2018: +0.052 | 2019: +0.121 | 2020: +0.145 | 2021: +0.156 | 2022: +0.089 | 2023: +0.158 | 2024: +0.106 | 2025: +0.186 | 2026: +0.032
- Yearly Tail ICs:   2015: +0.063 | 2016: +0.093 | 2017: +0.103 | 2018: +0.227 | 2019: +0.223 | 2020: +0.126 | 2021: +0.470 | 2022: +0.317 | 2023: +0.218 | 2024: +0.331 | 2025: +0.151 | 2026: -0.128
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=2.17, Recency ratio=2.04
- Early IC=+0.0605, Recent IC=+0.1235, 1st-half IC=+0.0646, 2nd-half IC=+0.1404, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.136, Q3_mid=+0.079, Q4=+0.081, Q5_high_vol=+0.169

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.1146, Sharpe=+1.0966)
- Admission: Train IC=+0.2534, Deflated=+0.2535, IR=0.60, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.103 | 2017: +0.006 | 2018: +0.160 | 2019: +0.225 | 2020: +0.143 | 2021: +0.130 | 2022: +0.088 | 2023: +0.155 | 2024: +0.079 | 2025: +0.162 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.147 | 2016: +0.094 | 2017: +0.050 | 2018: +0.353 | 2019: +0.460 | 2020: +0.218 | 2021: +0.265 | 2022: +0.266 | 2023: +0.298 | 2024: +0.365 | 2025: +0.133 | 2026: +0.171
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=2.22
- Early IC=+0.0546, Recent IC=+0.1214, 1st-half IC=+0.1238, 2nd-half IC=+0.1295, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.133, Q3_mid=+0.090, Q4=+0.116, Q5_high_vol=+0.201

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1028, Sharpe=+1.0956)
- Admission: Train IC=+0.2323, Deflated=+0.2320, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.119 | 2017: +0.028 | 2018: +0.094 | 2019: +0.202 | 2020: +0.130 | 2021: +0.162 | 2022: +0.112 | 2023: +0.172 | 2024: +0.043 | 2025: +0.183 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.185 | 2017: +0.169 | 2018: +0.356 | 2019: +0.321 | 2020: +0.102 | 2021: +0.356 | 2022: +0.177 | 2023: +0.309 | 2024: +0.207 | 2025: +0.244 | 2026: -0.012
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.38, Recency ratio=1.93
- Early IC=+0.0736, Recent IC=+0.1417, 1st-half IC=+0.1064, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.154, Q3_mid=+0.118, Q4=+0.093, Q5_high_vol=+0.155

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1103, Sharpe=+1.0913)
- Admission: Train IC=+0.2964, Deflated=+0.2958, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.092 | 2017: -0.005 | 2018: +0.166 | 2019: +0.223 | 2020: +0.135 | 2021: +0.148 | 2022: +0.127 | 2023: +0.186 | 2024: +0.081 | 2025: +0.182 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.022 | 2017: +0.048 | 2018: +0.386 | 2019: +0.452 | 2020: +0.337 | 2021: +0.367 | 2022: +0.294 | 2023: +0.467 | 2024: +0.301 | 2025: +0.195 | 2026: +0.190
- IC CV=0.48, Neg years (linear/tail)=1/1 of 8, Half ratio=1.26, Recency ratio=3.67
- Early IC=+0.0430, Recent IC=+0.1577, 1st-half IC=+0.1243, 2nd-half IC=+0.1567, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.057, Q2=+0.177, Q3_mid=+0.114, Q4=+0.148, Q5_high_vol=+0.173

**`combo_z_sum__volume_weighted_price_position__limit_down_proximity_early`** (Lock IC=+0.1254, Sharpe=+1.0792)
- Admission: Train IC=+0.1757, Deflated=+0.1759, IR=0.39, Mono=0.66, p=0.0010, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.060 | 2017: +0.036 | 2018: +0.120 | 2019: +0.221 | 2020: +0.040 | 2021: +0.168 | 2022: +0.043 | 2023: +0.112 | 2024: +0.095 | 2025: +0.141 | 2026: +0.121
- Yearly Tail ICs:   2015: +0.157 | 2016: -0.109 | 2017: +0.135 | 2018: +0.141 | 2019: +0.574 | 2020: +0.091 | 2021: +0.329 | 2022: +0.112 | 2023: +0.291 | 2024: +0.310 | 2025: +0.149 | 2026: +0.183
- IC CV=0.64, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=1.62
- Early IC=+0.0479, Recent IC=+0.0776, 1st-half IC=+0.1146, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.086, Q3_mid=+0.098, Q4=+0.128, Q5_high_vol=+0.119

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1169, Sharpe=+1.0451)
- Admission: Train IC=+0.2219, Deflated=+0.2208, IR=0.63, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.182 | 2017: +0.045 | 2018: +0.169 | 2019: +0.175 | 2020: +0.169 | 2021: +0.121 | 2022: +0.081 | 2023: +0.159 | 2024: +0.141 | 2025: +0.100 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.003 | 2016: +0.267 | 2017: +0.093 | 2018: +0.275 | 2019: +0.364 | 2020: +0.156 | 2021: +0.281 | 2022: +0.220 | 2023: +0.147 | 2024: +0.281 | 2025: +0.053 | 2026: +0.144
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=1.06
- Early IC=+0.1133, Recent IC=+0.1198, 1st-half IC=+0.1411, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.108, Q3_mid=+0.096, Q4=+0.177, Q5_high_vol=+0.184

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1301, Sharpe=+1.0434)
- Admission: Train IC=+0.2370, Deflated=+0.2374, IR=0.49, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.117 | 2017: +0.051 | 2018: +0.143 | 2019: +0.214 | 2020: +0.108 | 2021: +0.210 | 2022: +0.079 | 2023: +0.124 | 2024: +0.107 | 2025: +0.160 | 2026: +0.108
- Yearly Tail ICs:   2015: -0.127 | 2016: +0.133 | 2017: +0.192 | 2018: +0.253 | 2019: +0.576 | 2020: +0.092 | 2021: +0.337 | 2022: +0.147 | 2023: +0.276 | 2024: +0.299 | 2025: +0.121 | 2026: +0.144
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.21
- Early IC=+0.0836, Recent IC=+0.1012, 1st-half IC=+0.1343, 2nd-half IC=+0.1384, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.121, Q3_mid=+0.099, Q4=+0.165, Q5_high_vol=+0.185

**`combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1109, Sharpe=+0.9996)
- Admission: Train IC=+0.2152, Deflated=+0.2145, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.011 | 2017: +0.014 | 2018: +0.093 | 2019: +0.194 | 2020: +0.097 | 2021: +0.147 | 2022: +0.124 | 2023: +0.168 | 2024: +0.089 | 2025: +0.191 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.038 | 2017: +0.091 | 2018: -0.039 | 2019: +0.361 | 2020: +0.226 | 2021: +0.221 | 2022: +0.284 | 2023: +0.443 | 2024: +0.255 | 2025: +0.266 | 2026: -0.148
- IC CV=0.59, Neg years (linear/tail)=0/1 of 8, Half ratio=1.70, Recency ratio=11.98
- Early IC=+0.0122, Recent IC=+0.1457, 1st-half IC=+0.0822, 2nd-half IC=+0.1397, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.137, Q3_mid=+0.108, Q4=+0.107, Q5_high_vol=+0.148

**`combo_mean__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1327, Sharpe=+0.9738)
- Admission: Train IC=+0.2314, Deflated=+0.2314, IR=0.50, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.074 | 2017: +0.019 | 2018: +0.134 | 2019: +0.166 | 2020: +0.129 | 2021: +0.159 | 2022: +0.155 | 2023: +0.136 | 2024: +0.115 | 2025: +0.173 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.031 | 2016: +0.203 | 2017: +0.128 | 2018: +0.281 | 2019: +0.358 | 2020: +0.142 | 2021: +0.271 | 2022: +0.251 | 2023: +0.145 | 2024: +0.344 | 2025: +0.155 | 2026: +0.090
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.62, Recency ratio=3.11
- Early IC=+0.0468, Recent IC=+0.1456, 1st-half IC=+0.0938, 2nd-half IC=+0.1522, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.136, Q3_mid=+0.092, Q4=+0.134, Q5_high_vol=+0.184

**`combo_min__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1167, Sharpe=+0.9419)
- Admission: Train IC=+0.1664, Deflated=+0.1661, IR=0.40, Mono=0.66, p=0.0018, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.004 | 2017: +0.009 | 2018: +0.030 | 2019: +0.154 | 2020: +0.061 | 2021: +0.142 | 2022: +0.073 | 2023: +0.133 | 2024: +0.065 | 2025: +0.166 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.002 | 2017: +0.085 | 2018: +0.256 | 2019: +0.290 | 2020: +0.150 | 2021: +0.183 | 2022: +0.124 | 2023: +0.313 | 2024: +0.364 | 2025: +0.134 | 2026: +0.252
- IC CV=0.75, Neg years (linear/tail)=0/0 of 8, Half ratio=2.18, Recency ratio=15.45
- Early IC=+0.0067, Recent IC=+0.1033, 1st-half IC=+0.0490, 2nd-half IC=+0.1069, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.092, Q3_mid=+0.065, Q4=+0.084, Q5_high_vol=+0.080

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1188, Sharpe=+0.9339)
- Admission: Train IC=+0.2778, Deflated=+0.2774, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.090 | 2017: -0.004 | 2018: +0.181 | 2019: +0.236 | 2020: +0.130 | 2021: +0.139 | 2022: +0.116 | 2023: +0.181 | 2024: +0.107 | 2025: +0.172 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.053 | 2017: +0.026 | 2018: +0.401 | 2019: +0.527 | 2020: +0.241 | 2021: +0.272 | 2022: +0.251 | 2023: +0.493 | 2024: +0.370 | 2025: +0.157 | 2026: +0.176
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.08, Recency ratio=3.43
- Early IC=+0.0434, Recent IC=+0.1486, 1st-half IC=+0.1316, 2nd-half IC=+0.1424, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.167, Q3_mid=+0.106, Q4=+0.141, Q5_high_vol=+0.178

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1088, Sharpe=+0.9171)
- Admission: Train IC=+0.2551, Deflated=+0.2551, IR=0.55, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.054 | 2017: +0.017 | 2018: +0.072 | 2019: +0.188 | 2020: +0.090 | 2021: +0.158 | 2022: +0.143 | 2023: +0.153 | 2024: +0.078 | 2025: +0.185 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.000 | 2016: +0.251 | 2017: -0.024 | 2018: +0.094 | 2019: +0.390 | 2020: +0.199 | 2021: +0.344 | 2022: +0.392 | 2023: +0.328 | 2024: +0.254 | 2025: +0.231 | 2026: -0.228
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=1.87, Recency ratio=4.15
- Early IC=+0.0358, Recent IC=+0.1483, 1st-half IC=+0.0783, 2nd-half IC=+0.1461, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.147, Q3_mid=+0.097, Q4=+0.110, Q5_high_vol=+0.154

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0976, Sharpe=+0.8959)
- Admission: Train IC=+0.2209, Deflated=+0.2206, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.123 | 2017: +0.041 | 2018: +0.089 | 2019: +0.198 | 2020: +0.122 | 2021: +0.160 | 2022: +0.122 | 2023: +0.186 | 2024: +0.050 | 2025: +0.171 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.104 | 2017: +0.199 | 2018: +0.309 | 2019: +0.171 | 2020: +0.104 | 2021: +0.349 | 2022: +0.184 | 2023: +0.320 | 2024: +0.197 | 2025: +0.231 | 2026: +0.070
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.37, Recency ratio=1.89
- Early IC=+0.0817, Recent IC=+0.1541, 1st-half IC=+0.1085, 2nd-half IC=+0.1483, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.167, Q3_mid=+0.110, Q4=+0.085, Q5_high_vol=+0.164

**`combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.1270, Sharpe=+0.8942)
- Admission: Train IC=+0.2161, Deflated=+0.2154, IR=0.53, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.007 | 2017: -0.002 | 2018: +0.093 | 2019: +0.227 | 2020: +0.097 | 2021: +0.121 | 2022: +0.077 | 2023: +0.169 | 2024: +0.098 | 2025: +0.171 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.234 | 2016: -0.066 | 2017: +0.013 | 2018: +0.383 | 2019: +0.498 | 2020: +0.182 | 2021: +0.279 | 2022: +0.186 | 2023: +0.361 | 2024: +0.289 | 2025: +0.162 | 2026: +0.523
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=1.27, Recency ratio=48.39
- Early IC=+0.0025, Recent IC=+0.1230, 1st-half IC=+0.0913, 2nd-half IC=+0.1162, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.115, Q3_mid=+0.125, Q4=+0.120, Q5_high_vol=+0.096

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1118, Sharpe=+0.8851)
- Admission: Train IC=+0.2300, Deflated=+0.2294, IR=0.61, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.078 | 2017: +0.029 | 2018: +0.074 | 2019: +0.187 | 2020: +0.138 | 2021: +0.153 | 2022: +0.125 | 2023: +0.182 | 2024: +0.107 | 2025: +0.183 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.129 | 2017: +0.186 | 2018: +0.176 | 2019: +0.307 | 2020: +0.233 | 2021: +0.346 | 2022: +0.319 | 2023: +0.330 | 2024: +0.266 | 2025: +0.223 | 2026: -0.008
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.87, Recency ratio=2.88
- Early IC=+0.0531, Recent IC=+0.1532, 1st-half IC=+0.0827, 2nd-half IC=+0.1544, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.146, Q3_mid=+0.109, Q4=+0.117, Q5_high_vol=+0.166

**`combo_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0909, Sharpe=+0.8829)
- Admission: Train IC=+0.2197, Deflated=+0.2191, IR=0.47, Mono=0.69, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.134 | 2017: +0.004 | 2018: +0.110 | 2019: +0.212 | 2020: +0.114 | 2021: +0.145 | 2022: +0.056 | 2023: +0.177 | 2024: +0.078 | 2025: +0.162 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.401 | 2016: +0.072 | 2017: +0.106 | 2018: +0.222 | 2019: +0.410 | 2020: +0.193 | 2021: +0.205 | 2022: +0.127 | 2023: +0.382 | 2024: +0.284 | 2025: +0.255 | 2026: -0.132
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=1.69
- Early IC=+0.0690, Recent IC=+0.1165, 1st-half IC=+0.1118, 2nd-half IC=+0.1205, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.093, Q3_mid=+0.120, Q4=+0.095, Q5_high_vol=+0.180

**`combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1295, Sharpe=+0.8774)
- Admission: Train IC=+0.2291, Deflated=+0.2294, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.117 | 2017: +0.024 | 2018: +0.066 | 2019: +0.184 | 2020: +0.150 | 2021: +0.116 | 2022: +0.104 | 2023: +0.159 | 2024: +0.090 | 2025: +0.178 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.103 | 2016: +0.225 | 2017: +0.129 | 2018: +0.330 | 2019: +0.333 | 2020: +0.129 | 2021: +0.283 | 2022: +0.268 | 2023: +0.150 | 2024: +0.232 | 2025: +0.189 | 2026: +0.255
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.40, Recency ratio=1.86
- Early IC=+0.0707, Recent IC=+0.1316, 1st-half IC=+0.0984, 2nd-half IC=+0.1377, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.113, Q3_mid=+0.090, Q4=+0.125, Q5_high_vol=+0.136

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1235, Sharpe=+0.8704)
- Admission: Train IC=+0.3321, Deflated=+0.3316, IR=0.84, Mono=0.80, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.114 | 2017: -0.018 | 2018: +0.194 | 2019: +0.243 | 2020: +0.166 | 2021: +0.154 | 2022: +0.098 | 2023: +0.185 | 2024: +0.115 | 2025: +0.168 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.123 | 2017: +0.050 | 2018: +0.464 | 2019: +0.571 | 2020: +0.389 | 2021: +0.434 | 2022: +0.258 | 2023: +0.455 | 2024: +0.415 | 2025: +0.235 | 2026: +0.220
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=2.97
- Early IC=+0.0478, Recent IC=+0.1417, 1st-half IC=+0.1385, 2nd-half IC=+0.1529, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.158, Q3_mid=+0.108, Q4=+0.157, Q5_high_vol=+0.195

**`combo_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0985, Sharpe=+0.8687)
- Admission: Train IC=+0.2527, Deflated=+0.2525, IR=0.58, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.033 | 2017: +0.023 | 2018: +0.078 | 2019: +0.177 | 2020: +0.092 | 2021: +0.165 | 2022: +0.155 | 2023: +0.150 | 2024: +0.069 | 2025: +0.196 | 2026: -0.035
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.244 | 2017: +0.029 | 2018: +0.111 | 2019: +0.352 | 2020: +0.157 | 2021: +0.338 | 2022: +0.376 | 2023: +0.334 | 2024: +0.202 | 2025: +0.255 | 2026: -0.249
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=2.01, Recency ratio=5.46
- Early IC=+0.0279, Recent IC=+0.1521, 1st-half IC=+0.0750, 2nd-half IC=+0.1505, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.146, Q3_mid=+0.103, Q4=+0.105, Q5_high_vol=+0.162

**`combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=+0.0782, Sharpe=+0.8340)
- Admission: Train IC=+0.1684, Deflated=+0.1678, IR=0.40, Mono=0.69, p=0.0016, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.094 | 2017: +0.029 | 2018: +0.096 | 2019: +0.190 | 2020: +0.181 | 2021: +0.137 | 2022: +0.037 | 2023: +0.119 | 2024: +0.055 | 2025: +0.151 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.340 | 2016: -0.094 | 2017: +0.061 | 2018: +0.226 | 2019: +0.360 | 2020: +0.218 | 2021: +0.186 | 2022: +0.182 | 2023: +0.294 | 2024: +0.222 | 2025: +0.236 | 2026: +0.190
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.22, Recency ratio=1.37
- Early IC=+0.0584, Recent IC=+0.0800, 1st-half IC=+0.0996, 2nd-half IC=+0.1216, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.103, Q3_mid=+0.153, Q4=+0.061, Q5_high_vol=+0.163

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1236, Sharpe=+0.8328)
- Admission: Train IC=+0.2437, Deflated=+0.2438, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.142 | 2016: +0.103 | 2017: +0.037 | 2018: +0.112 | 2019: +0.155 | 2020: +0.064 | 2021: +0.163 | 2022: +0.158 | 2023: +0.133 | 2024: +0.125 | 2025: +0.113 | 2026: +0.117
- Yearly Tail ICs:   2015: -0.058 | 2016: +0.387 | 2017: +0.038 | 2018: +0.292 | 2019: +0.318 | 2020: +0.160 | 2021: +0.282 | 2022: +0.304 | 2023: +0.329 | 2024: +0.288 | 2025: -0.084 | 2026: +0.277
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.49, Recency ratio=2.06
- Early IC=+0.0704, Recent IC=+0.1453, 1st-half IC=+0.0911, 2nd-half IC=+0.1354, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=-0.025, Q2=+0.128, Q3_mid=+0.050, Q4=+0.147, Q5_high_vol=+0.182

**`combo_rank_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0810, Sharpe=+0.8246)
- Admission: Train IC=+0.2133, Deflated=+0.2127, IR=0.46, Mono=0.67, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.103 | 2017: +0.026 | 2018: +0.130 | 2019: +0.174 | 2020: +0.125 | 2021: +0.147 | 2022: +0.083 | 2023: +0.182 | 2024: +0.058 | 2025: +0.150 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.214 | 2016: +0.091 | 2017: +0.090 | 2018: +0.367 | 2019: +0.336 | 2020: +0.148 | 2021: +0.306 | 2022: +0.134 | 2023: +0.354 | 2024: +0.119 | 2025: +0.364 | 2026: -0.019
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.31, Recency ratio=1.96
- Early IC=+0.0667, Recent IC=+0.1305, 1st-half IC=+0.1020, 2nd-half IC=+0.1340, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.122, Q3_mid=+0.092, Q4=+0.089, Q5_high_vol=+0.194

**`combo_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.1012, Sharpe=+0.8236)
- Admission: Train IC=+0.1884, Deflated=+0.1897, IR=0.54, Mono=0.70, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.119 | 2017: +0.114 | 2018: +0.058 | 2019: +0.081 | 2020: +0.109 | 2021: +0.110 | 2022: +0.109 | 2023: +0.155 | 2024: +0.136 | 2025: +0.153 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.067 | 2017: +0.171 | 2018: +0.138 | 2019: +0.222 | 2020: +0.078 | 2021: +0.271 | 2022: +0.347 | 2023: +0.302 | 2024: +0.108 | 2025: +0.280 | 2026: -0.113
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.38, Recency ratio=1.13
- Early IC=+0.1163, Recent IC=+0.1320, 1st-half IC=+0.0813, 2nd-half IC=+0.1123, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.083, Q3_mid=+0.088, Q4=+0.108, Q5_high_vol=+0.142

**`combo_max__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0792, Sharpe=+0.7948)
- Admission: Train IC=+0.1534, Deflated=+0.1532, IR=0.45, Mono=0.68, p=0.0032, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.093 | 2017: +0.014 | 2018: +0.140 | 2019: +0.118 | 2020: +0.070 | 2021: +0.160 | 2022: +0.131 | 2023: +0.111 | 2024: +0.033 | 2025: +0.110 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.079 | 2016: +0.021 | 2017: +0.274 | 2018: +0.388 | 2019: +0.138 | 2020: +0.029 | 2021: +0.351 | 2022: +0.116 | 2023: +0.176 | 2024: +0.182 | 2025: +0.200 | 2026: +0.128
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=2.25
- Early IC=+0.0538, Recent IC=+0.1211, 1st-half IC=+0.0978, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.104, Q3_mid=+0.074, Q4=+0.085, Q5_high_vol=+0.169

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`** (Lock IC=+0.0720, Sharpe=+0.7769)
- Admission: Train IC=+0.1941, Deflated=+0.1945, IR=0.47, Mono=0.70, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.147 | 2017: +0.018 | 2018: +0.115 | 2019: +0.145 | 2020: +0.127 | 2021: +0.052 | 2022: +0.076 | 2023: +0.064 | 2024: +0.076 | 2025: +0.086 | 2026: +0.033
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.178 | 2017: +0.101 | 2018: +0.289 | 2019: +0.260 | 2020: +0.081 | 2021: +0.149 | 2022: +0.373 | 2023: +0.032 | 2024: +0.237 | 2025: +0.105 | 2026: +0.123
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.85
- Early IC=+0.0825, Recent IC=+0.0699, 1st-half IC=+0.1129, 2nd-half IC=+0.0854, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.091, Q3_mid=+0.089, Q4=+0.133, Q5_high_vol=+0.100

**`combo_clamp_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0975, Sharpe=+0.7347)
- Admission: Train IC=+0.1847, Deflated=+0.1859, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.118 | 2017: +0.115 | 2018: +0.058 | 2019: +0.079 | 2020: +0.108 | 2021: +0.110 | 2022: +0.107 | 2023: +0.154 | 2024: +0.135 | 2025: +0.147 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.343 | 2016: +0.004 | 2017: +0.186 | 2018: +0.180 | 2019: +0.259 | 2020: +0.064 | 2021: +0.262 | 2022: +0.270 | 2023: +0.273 | 2024: +0.195 | 2025: +0.214 | 2026: -0.144
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=1.12
- Early IC=+0.1164, Recent IC=+0.1304, 1st-half IC=+0.0806, 2nd-half IC=+0.1116, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.081, Q3_mid=+0.088, Q4=+0.103, Q5_high_vol=+0.140

**`combo_max__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0758, Sharpe=+0.7257)
- Admission: Train IC=+0.1997, Deflated=+0.1993, IR=0.69, Mono=0.72, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.114 | 2017: +0.042 | 2018: +0.113 | 2019: +0.180 | 2020: +0.161 | 2021: +0.150 | 2022: +0.088 | 2023: +0.105 | 2024: +0.071 | 2025: +0.131 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.147 | 2017: +0.027 | 2018: +0.269 | 2019: +0.284 | 2020: +0.217 | 2021: +0.338 | 2022: +0.175 | 2023: +0.305 | 2024: +0.325 | 2025: +0.081 | 2026: -0.084
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.16, Recency ratio=1.24
- Early IC=+0.0778, Recent IC=+0.0963, 1st-half IC=+0.1093, 2nd-half IC=+0.1269, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.102, Q3_mid=+0.118, Q4=+0.104, Q5_high_vol=+0.186

**`combo_tri_median__max_up_ret__demark_setup_reversal_early__star50_limit_proximity_early`** (Lock IC=+0.1156, Sharpe=+0.7244)
- Admission: Train IC=+0.2088, Deflated=+0.2082, IR=0.53, Mono=0.70, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.101 | 2017: +0.016 | 2018: +0.017 | 2019: +0.135 | 2020: +0.138 | 2021: +0.136 | 2022: +0.069 | 2023: +0.164 | 2024: +0.115 | 2025: +0.171 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.095 | 2016: +0.121 | 2017: +0.162 | 2018: +0.162 | 2019: +0.280 | 2020: +0.104 | 2021: +0.448 | 2022: +0.197 | 2023: +0.186 | 2024: +0.285 | 2025: +0.180 | 2026: -0.188
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=2.10, Recency ratio=2.00
- Early IC=+0.0582, Recent IC=+0.1162, 1st-half IC=+0.0601, 2nd-half IC=+0.1264, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.121, Q3_mid=+0.077, Q4=+0.077, Q5_high_vol=+0.124

**`combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return`** (Lock IC=+0.1005, Sharpe=+0.6911)
- Admission: Train IC=+0.1810, Deflated=+0.1807, IR=0.46, Mono=0.70, p=0.0010, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.182 | 2017: +0.087 | 2018: +0.125 | 2019: +0.140 | 2020: +0.100 | 2021: +0.040 | 2022: +0.051 | 2023: +0.091 | 2024: +0.099 | 2025: +0.109 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.086 | 2016: +0.377 | 2017: +0.067 | 2018: +0.130 | 2019: +0.330 | 2020: +0.049 | 2021: +0.123 | 2022: +0.336 | 2023: +0.150 | 2024: +0.309 | 2025: +0.006 | 2026: +0.008
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.53
- Early IC=+0.1347, Recent IC=+0.0712, 1st-half IC=+0.1326, 2nd-half IC=+0.0750, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.110, Q3_mid=+0.091, Q4=+0.123, Q5_high_vol=+0.084

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0966, Sharpe=+0.6825)
- Admission: Train IC=+0.2228, Deflated=+0.2222, IR=0.57, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.032 | 2017: +0.012 | 2018: +0.025 | 2019: +0.120 | 2020: +0.058 | 2021: +0.170 | 2022: +0.103 | 2023: +0.160 | 2024: +0.095 | 2025: +0.200 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.270 | 2017: +0.037 | 2018: +0.094 | 2019: +0.349 | 2020: +0.159 | 2021: +0.303 | 2022: +0.319 | 2023: +0.379 | 2024: +0.243 | 2025: +0.164 | 2026: -0.259
- IC CV=0.69, Neg years (linear/tail)=0/0 of 8, Half ratio=3.54, Recency ratio=6.25
- Early IC=+0.0209, Recent IC=+0.1310, 1st-half IC=+0.0354, 2nd-half IC=+0.1252, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.104, Q3_mid=+0.101, Q4=+0.056, Q5_high_vol=+0.118

**`combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend`** (Lock IC=+0.1105, Sharpe=+0.6779)
- Admission: Train IC=+0.2591, Deflated=+0.2613, IR=0.59, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.125 | 2016: +0.060 | 2017: -0.040 | 2018: +0.109 | 2019: +0.092 | 2020: +0.119 | 2021: +0.034 | 2022: +0.171 | 2023: +0.125 | 2024: +0.073 | 2025: +0.117 | 2026: +0.152
- Yearly Tail ICs:   2015: +0.174 | 2016: +0.184 | 2017: +0.027 | 2018: +0.404 | 2019: +0.269 | 2020: +0.379 | 2021: +0.227 | 2022: +0.410 | 2023: +0.083 | 2024: +0.046 | 2025: +0.082 | 2026: +0.208
- IC CV=0.73, Neg years (linear/tail)=1/0 of 8, Half ratio=1.59, Recency ratio=15.04
- Early IC=+0.0098, Recent IC=+0.1478, 1st-half IC=+0.0671, 2nd-half IC=+0.1064, Neg regimes=0/5
- Weak component: `yesterday_early_trend` (CV=1.03)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.129, Q3_mid=+0.040, Q4=+0.114, Q5_high_vol=+0.135

**`combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0987, Sharpe=+0.6482)
- Admission: Train IC=+0.2131, Deflated=+0.2122, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.015 | 2017: +0.017 | 2018: +0.053 | 2019: +0.133 | 2020: +0.056 | 2021: +0.148 | 2022: +0.073 | 2023: +0.199 | 2024: +0.077 | 2025: +0.203 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.097 | 2017: +0.122 | 2018: +0.039 | 2019: +0.305 | 2020: +0.139 | 2021: +0.217 | 2022: +0.377 | 2023: +0.523 | 2024: +0.156 | 2025: +0.214 | 2026: -0.191
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=2.37, Recency ratio=8.28
- Early IC=+0.0164, Recent IC=+0.1360, 1st-half IC=+0.0499, 2nd-half IC=+0.1181, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.112, Q3_mid=+0.088, Q4=+0.068, Q5_high_vol=+0.113

**`combo_mean__max_up_ret__rally_strength_max`** (Lock IC=+0.0728, Sharpe=+0.6410)
- Admission: Train IC=+0.2048, Deflated=+0.2043, IR=0.43, Mono=0.68, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.050 | 2017: +0.055 | 2018: +0.048 | 2019: +0.170 | 2020: +0.058 | 2021: +0.182 | 2022: +0.056 | 2023: +0.142 | 2024: +0.056 | 2025: +0.184 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.125 | 2016: +0.129 | 2017: +0.101 | 2018: +0.184 | 2019: +0.299 | 2020: +0.087 | 2021: +0.236 | 2022: +0.174 | 2023: +0.423 | 2024: +0.298 | 2025: +0.204 | 2026: -0.196
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=1.64, Recency ratio=1.88
- Early IC=+0.0526, Recent IC=+0.0990, 1st-half IC=+0.0700, 2nd-half IC=+0.1150, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.34)
- Regime ICs: Q1_low_vol=+0.023, Q2=+0.106, Q3_mid=+0.141, Q4=+0.098, Q5_high_vol=+0.114

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_momentum`** (Lock IC=+0.0660, Sharpe=+0.6358)
- Admission: Train IC=+0.1673, Deflated=+0.1667, IR=0.45, Mono=0.68, p=0.0016, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.092 | 2017: +0.053 | 2018: +0.169 | 2019: +0.142 | 2020: +0.119 | 2021: +0.078 | 2022: +0.055 | 2023: +0.087 | 2024: +0.078 | 2025: +0.102 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.205 | 2016: +0.227 | 2017: +0.130 | 2018: +0.203 | 2019: +0.107 | 2020: +0.229 | 2021: +0.160 | 2022: +0.180 | 2023: +0.233 | 2024: +0.282 | 2025: +0.043 | 2026: -0.050
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.98
- Early IC=+0.0725, Recent IC=+0.0709, 1st-half IC=+0.1251, 2nd-half IC=+0.0860, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.108, Q3_mid=+0.124, Q4=+0.132, Q5_high_vol=+0.087

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0888, Sharpe=+0.6277)
- Admission: Train IC=+0.2382, Deflated=+0.2378, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.187 | 2017: +0.069 | 2018: +0.136 | 2019: +0.070 | 2020: +0.141 | 2021: +0.123 | 2022: +0.120 | 2023: +0.090 | 2024: +0.066 | 2025: +0.103 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.015 | 2016: +0.254 | 2017: +0.152 | 2018: +0.365 | 2019: +0.313 | 2020: +0.277 | 2021: +0.289 | 2022: +0.228 | 2023: +0.182 | 2024: +0.289 | 2025: +0.037 | 2026: +0.123
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=0.82
- Early IC=+0.1276, Recent IC=+0.1051, 1st-half IC=+0.0975, 2nd-half IC=+0.1198, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.044, Q2=+0.074, Q3_mid=+0.060, Q4=+0.142, Q5_high_vol=+0.189

**`combo_rel_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.1071, Sharpe=+0.6274)
- Admission: Train IC=+0.2026, Deflated=+0.2036, IR=0.50, Mono=0.70, p=0.0002, MaxCorr=0.62
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.115 | 2017: +0.116 | 2018: +0.048 | 2019: +0.077 | 2020: +0.107 | 2021: +0.117 | 2022: +0.082 | 2023: +0.160 | 2024: +0.133 | 2025: +0.148 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.071 | 2017: +0.225 | 2018: +0.107 | 2019: +0.273 | 2020: +0.084 | 2021: +0.286 | 2022: +0.314 | 2023: +0.383 | 2024: +0.097 | 2025: +0.261 | 2026: -0.201
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.42, Recency ratio=1.05
- Early IC=+0.1155, Recent IC=+0.1211, 1st-half IC=+0.0764, 2nd-half IC=+0.1085, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.085, Q3_mid=+0.094, Q4=+0.095, Q5_high_vol=+0.125

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0838, Sharpe=+0.6139)
- Admission: Train IC=+0.2164, Deflated=+0.2150, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.096 | 2017: +0.057 | 2018: +0.107 | 2019: +0.187 | 2020: +0.127 | 2021: +0.126 | 2022: +0.103 | 2023: +0.186 | 2024: +0.078 | 2025: +0.135 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.038 | 2017: +0.107 | 2018: +0.294 | 2019: +0.277 | 2020: +0.169 | 2021: +0.297 | 2022: +0.167 | 2023: +0.526 | 2024: +0.191 | 2025: +0.153 | 2026: -0.182
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.88
- Early IC=+0.0767, Recent IC=+0.1445, 1st-half IC=+0.1070, 2nd-half IC=+0.1319, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.118, Q3_mid=+0.101, Q4=+0.128, Q5_high_vol=+0.162

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0926, Sharpe=+0.6024)
- Admission: Train IC=+0.1994, Deflated=+0.1984, IR=0.52, Mono=0.68, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.102 | 2017: +0.036 | 2018: +0.120 | 2019: +0.193 | 2020: +0.094 | 2021: +0.123 | 2022: +0.112 | 2023: +0.179 | 2024: +0.086 | 2025: +0.168 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.395 | 2016: -0.066 | 2017: +0.177 | 2018: +0.211 | 2019: +0.429 | 2020: +0.128 | 2021: +0.266 | 2022: +0.118 | 2023: +0.514 | 2024: +0.198 | 2025: +0.261 | 2026: +0.238
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=1.12, Recency ratio=2.11
- Early IC=+0.0689, Recent IC=+0.1455, 1st-half IC=+0.1117, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.144, Q3_mid=+0.099, Q4=+0.098, Q5_high_vol=+0.153

**`combo_tri_max__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1054, Sharpe=+0.5945)
- Admission: Train IC=+0.1939, Deflated=+0.1944, IR=0.58, Mono=0.70, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.119 | 2017: -0.044 | 2018: +0.117 | 2019: +0.075 | 2020: +0.114 | 2021: +0.082 | 2022: +0.103 | 2023: +0.117 | 2024: +0.124 | 2025: +0.081 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.146 | 2016: +0.320 | 2017: +0.046 | 2018: +0.367 | 2019: +0.189 | 2020: +0.047 | 2021: +0.140 | 2022: +0.237 | 2023: +0.260 | 2024: +0.126 | 2025: -0.054 | 2026: +0.028
- IC CV=0.60, Neg years (linear/tail)=1/0 of 8, Half ratio=1.45, Recency ratio=2.92
- Early IC=+0.0377, Recent IC=+0.1101, 1st-half IC=+0.0755, 2nd-half IC=+0.1093, Neg regimes=0/5
- Weak component: `yesterday_early_momentum` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.105, Q3_mid=+0.094, Q4=+0.120, Q5_high_vol=+0.071

**`combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0961, Sharpe=+0.5743)
- Admission: Train IC=+0.1870, Deflated=+0.1861, IR=0.49, Mono=0.70, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.048 | 2017: +0.034 | 2018: +0.048 | 2019: +0.165 | 2020: +0.087 | 2021: +0.143 | 2022: +0.100 | 2023: +0.179 | 2024: +0.106 | 2025: +0.197 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.249 | 2016: -0.053 | 2017: +0.064 | 2018: +0.031 | 2019: +0.396 | 2020: +0.246 | 2021: +0.109 | 2022: +0.308 | 2023: +0.347 | 2024: +0.267 | 2025: +0.295 | 2026: -0.202
- IC CV=0.53, Neg years (linear/tail)=0/1 of 8, Half ratio=1.73, Recency ratio=3.52
- Early IC=+0.0399, Recent IC=+0.1403, 1st-half IC=+0.0742, 2nd-half IC=+0.1282, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.117, Q3_mid=+0.128, Q4=+0.073, Q5_high_vol=+0.130

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.0911, Sharpe=+0.5434)
- Admission: Train IC=+0.2933, Deflated=+0.2948, IR=0.77, Mono=0.82, p=0.0000, MaxCorr=0.39
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.107 | 2017: -0.042 | 2018: +0.148 | 2019: +0.125 | 2020: +0.143 | 2021: +0.061 | 2022: +0.184 | 2023: +0.110 | 2024: +0.055 | 2025: +0.086 | 2026: +0.144
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.359 | 2017: +0.128 | 2018: +0.396 | 2019: +0.349 | 2020: +0.319 | 2021: +0.172 | 2022: +0.412 | 2023: +0.081 | 2024: +0.028 | 2025: +0.063 | 2026: +0.085
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=1.30, Recency ratio=4.55
- Early IC=+0.0323, Recent IC=+0.1469, 1st-half IC=+0.0983, 2nd-half IC=+0.1280, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.139, Q3_mid=+0.039, Q4=+0.138, Q5_high_vol=+0.190

**`combo_ifelse__gap_pct__max_up_ret__first_bar_return`** (Lock IC=+0.0614, Sharpe=+0.5184)
- Admission: Train IC=+0.1790, Deflated=+0.1786, IR=0.49, Mono=0.68, p=0.0010, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.150 | 2017: +0.056 | 2018: +0.134 | 2019: +0.144 | 2020: +0.121 | 2021: +0.137 | 2022: +0.084 | 2023: +0.167 | 2024: +0.019 | 2025: +0.129 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.174 | 2016: +0.120 | 2017: +0.182 | 2018: +0.242 | 2019: +0.139 | 2020: +0.030 | 2021: +0.299 | 2022: +0.139 | 2023: +0.244 | 2024: +0.174 | 2025: +0.243 | 2026: +0.111
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=1.22
- Early IC=+0.1030, Recent IC=+0.1256, 1st-half IC=+0.1168, 2nd-half IC=+0.1259, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.114, Q3_mid=+0.099, Q4=+0.088, Q5_high_vol=+0.162

**`combo_tri_mean__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.1005, Sharpe=+0.4995)
- Admission: Train IC=+0.2266, Deflated=+0.2283, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.131 | 2017: -0.077 | 2018: +0.135 | 2019: +0.113 | 2020: +0.106 | 2021: +0.061 | 2022: +0.152 | 2023: +0.133 | 2024: +0.080 | 2025: +0.083 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.133 | 2016: +0.195 | 2017: +0.076 | 2018: +0.403 | 2019: +0.244 | 2020: +0.351 | 2021: +0.149 | 2022: +0.348 | 2023: +0.039 | 2024: +0.124 | 2025: +0.033 | 2026: +0.302
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=1.24, Recency ratio=5.28
- Early IC=+0.0270, Recent IC=+0.1428, 1st-half IC=+0.0924, 2nd-half IC=+0.1141, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.131, Q3_mid=+0.071, Q4=+0.135, Q5_high_vol=+0.136

**`combo_diff__rbreaker_sell_setup_proximity_early__gap_pct`** (Lock IC=+0.0639, Sharpe=+0.4993)
- Admission: Train IC=+0.2328, Deflated=+0.2327, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.079 | 2017: +0.050 | 2018: +0.057 | 2019: +0.141 | 2020: +0.101 | 2021: +0.147 | 2022: +0.102 | 2023: +0.177 | 2024: +0.072 | 2025: +0.153 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.102 | 2016: +0.229 | 2017: +0.051 | 2018: +0.204 | 2019: +0.321 | 2020: +0.226 | 2021: +0.199 | 2022: +0.282 | 2023: +0.449 | 2024: +0.127 | 2025: +0.147 | 2026: -0.331
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.92, Recency ratio=2.16
- Early IC=+0.0647, Recent IC=+0.1399, 1st-half IC=+0.0695, 2nd-half IC=+0.1338, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.044, Q2=+0.121, Q3_mid=+0.110, Q4=+0.090, Q5_high_vol=+0.141

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0864, Sharpe=+0.4855)
- Admission: Train IC=+0.2120, Deflated=+0.2109, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.091 | 2017: +0.042 | 2018: +0.115 | 2019: +0.193 | 2020: +0.111 | 2021: +0.135 | 2022: +0.109 | 2023: +0.175 | 2024: +0.079 | 2025: +0.148 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.085 | 2016: +0.078 | 2017: +0.118 | 2018: +0.276 | 2019: +0.278 | 2020: +0.141 | 2021: +0.318 | 2022: +0.173 | 2023: +0.525 | 2024: +0.193 | 2025: +0.100 | 2026: -0.182
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=2.12
- Early IC=+0.0669, Recent IC=+0.1417, 1st-half IC=+0.1078, 2nd-half IC=+0.1306, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.126, Q3_mid=+0.113, Q4=+0.131, Q5_high_vol=+0.153

**`combo_rank_min__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=+0.0944, Sharpe=+0.4751)
- Admission: Train IC=+0.2003, Deflated=+0.1996, IR=0.44, Mono=0.70, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.071 | 2017: +0.020 | 2018: +0.061 | 2019: +0.163 | 2020: +0.054 | 2021: +0.114 | 2022: +0.073 | 2023: +0.177 | 2024: +0.075 | 2025: +0.150 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.015 | 2016: +0.184 | 2017: +0.120 | 2018: +0.086 | 2019: +0.253 | 2020: +0.119 | 2021: +0.071 | 2022: +0.235 | 2023: +0.411 | 2024: +0.190 | 2025: +0.132 | 2026: +0.044
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=1.37, Recency ratio=2.79
- Early IC=+0.0444, Recent IC=+0.1238, 1st-half IC=+0.0734, 2nd-half IC=+0.1007, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.095, Q3_mid=+0.063, Q4=+0.038, Q5_high_vol=+0.133

**`combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.1088, Sharpe=+0.4427)
- Admission: Train IC=+0.2033, Deflated=+0.2038, IR=0.49, Mono=0.70, p=0.0002, MaxCorr=0.62
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.121 | 2017: -0.071 | 2018: +0.115 | 2019: +0.066 | 2020: +0.116 | 2021: +0.100 | 2022: +0.119 | 2023: +0.135 | 2024: +0.143 | 2025: +0.074 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.321 | 2017: -0.016 | 2018: +0.309 | 2019: +0.113 | 2020: +0.071 | 2021: +0.261 | 2022: +0.113 | 2023: +0.185 | 2024: +0.194 | 2025: -0.077 | 2026: +0.161
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=1.83, Recency ratio=5.08
- Early IC=+0.0250, Recent IC=+0.1270, 1st-half IC=+0.0683, 2nd-half IC=+0.1248, Neg regimes=1/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=-0.028, Q2=+0.132, Q3_mid=+0.109, Q4=+0.127, Q5_high_vol=+0.089

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0866, Sharpe=+0.4183)
- Admission: Train IC=+0.2133, Deflated=+0.2125, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.190 | 2024: +0.078 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.063 | 2017: +0.039 | 2018: +0.143 | 2019: +0.289 | 2020: +0.186 | 2021: +0.349 | 2022: +0.232 | 2023: +0.457 | 2024: +0.231 | 2025: +0.146 | 2026: -0.277
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.91, Recency ratio=2.92
- Early IC=+0.0526, Recent IC=+0.1533, 1st-half IC=+0.0774, 2nd-half IC=+0.1476, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.058, Q2=+0.128, Q3_mid=+0.102, Q4=+0.103, Q5_high_vol=+0.164

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0872, Sharpe=+0.4131)
- Admission: Train IC=+0.2096, Deflated=+0.2094, IR=0.50, Mono=0.68, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.086 | 2017: +0.026 | 2018: +0.117 | 2019: +0.128 | 2020: +0.091 | 2021: +0.177 | 2022: +0.157 | 2023: +0.131 | 2024: +0.078 | 2025: +0.138 | 2026: +0.022
- Yearly Tail ICs:   2015: -0.008 | 2016: +0.152 | 2017: +0.168 | 2018: +0.285 | 2019: +0.154 | 2020: +0.117 | 2021: +0.463 | 2022: +0.201 | 2023: +0.209 | 2024: +0.198 | 2025: +0.120 | 2026: -0.124
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.69, Recency ratio=2.55
- Early IC=+0.0564, Recent IC=+0.1439, 1st-half IC=+0.0842, 2nd-half IC=+0.1425, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.110, Q3_mid=+0.091, Q4=+0.128, Q5_high_vol=+0.165

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0789, Sharpe=+0.4086)
- Admission: Train IC=+0.1712, Deflated=+0.1711, IR=0.64, Mono=0.74, p=0.0012, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.083 | 2016: +0.039 | 2017: +0.082 | 2018: +0.101 | 2019: +0.177 | 2020: +0.058 | 2021: +0.126 | 2022: +0.086 | 2023: +0.176 | 2024: +0.130 | 2025: +0.125 | 2026: -0.082
- Yearly Tail ICs:   2015: -0.243 | 2016: +0.198 | 2017: +0.166 | 2018: +0.229 | 2019: +0.254 | 2020: +0.156 | 2021: +0.074 | 2022: +0.174 | 2023: +0.389 | 2024: +0.298 | 2025: -0.010 | 2026: -0.104
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=2.17
- Early IC=+0.0606, Recent IC=+0.1314, 1st-half IC=+0.0919, 2nd-half IC=+0.1133, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.115, Q3_mid=+0.089, Q4=+0.106, Q5_high_vol=+0.130

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0861, Sharpe=+0.4034)
- Admission: Train IC=+0.2171, Deflated=+0.2172, IR=0.44, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.149 | 2017: +0.001 | 2018: +0.089 | 2019: +0.181 | 2020: +0.129 | 2021: +0.163 | 2022: +0.108 | 2023: +0.152 | 2024: +0.062 | 2025: +0.186 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.024 | 2017: +0.040 | 2018: +0.261 | 2019: +0.408 | 2020: +0.180 | 2021: +0.310 | 2022: +0.269 | 2023: +0.345 | 2024: +0.233 | 2025: +0.245 | 2026: -0.185
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.46, Recency ratio=1.85
- Early IC=+0.0708, Recent IC=+0.1313, 1st-half IC=+0.0948, 2nd-half IC=+0.1383, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.109, Q3_mid=+0.108, Q4=+0.108, Q5_high_vol=+0.169

**`combo_min__max_up_ret__rally_strength_max`** (Lock IC=+0.0812, Sharpe=+0.4028)
- Admission: Train IC=+0.1552, Deflated=+0.1542, IR=0.37, Mono=0.67, p=0.0032, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.039 | 2017: +0.051 | 2018: +0.038 | 2019: +0.175 | 2020: +0.059 | 2021: +0.191 | 2022: +0.044 | 2023: +0.123 | 2024: +0.077 | 2025: +0.172 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.365 | 2016: +0.122 | 2017: +0.081 | 2018: +0.137 | 2019: +0.314 | 2020: -0.036 | 2021: +0.308 | 2022: +0.118 | 2023: +0.331 | 2024: +0.179 | 2025: +0.182 | 2026: -0.102
- IC CV=0.66, Neg years (linear/tail)=0/1 of 8, Half ratio=1.68, Recency ratio=1.87
- Early IC=+0.0447, Recent IC=+0.0834, 1st-half IC=+0.0657, 2nd-half IC=+0.1103, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.34)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.089, Q3_mid=+0.145, Q4=+0.082, Q5_high_vol=+0.097

**`combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=+0.0988, Sharpe=+0.3616)
- Admission: Train IC=+0.2060, Deflated=+0.2057, IR=0.47, Mono=0.66, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.095 | 2017: +0.000 | 2018: +0.078 | 2019: +0.167 | 2020: +0.105 | 2021: +0.150 | 2022: +0.084 | 2023: +0.170 | 2024: +0.070 | 2025: +0.198 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.309 | 2016: -0.017 | 2017: +0.026 | 2018: +0.263 | 2019: +0.418 | 2020: +0.166 | 2021: +0.178 | 2022: +0.246 | 2023: +0.421 | 2024: +0.198 | 2025: +0.340 | 2026: -0.446
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.54, Recency ratio=2.67
- Early IC=+0.0476, Recent IC=+0.1270, 1st-half IC=+0.0820, 2nd-half IC=+0.1261, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.099, Q3_mid=+0.107, Q4=+0.068, Q5_high_vol=+0.150

**`combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1004, Sharpe=+0.3556)
- Admission: Train IC=+0.1884, Deflated=+0.1879, IR=0.50, Mono=0.67, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.063 | 2017: +0.031 | 2018: +0.079 | 2019: +0.122 | 2020: +0.109 | 2021: +0.161 | 2022: +0.161 | 2023: +0.145 | 2024: +0.093 | 2025: +0.143 | 2026: +0.049
- Yearly Tail ICs:   2015: -0.154 | 2016: +0.217 | 2017: +0.055 | 2018: +0.271 | 2019: +0.232 | 2020: +0.011 | 2021: +0.369 | 2022: +0.236 | 2023: +0.184 | 2024: +0.228 | 2025: -0.094 | 2026: -0.151
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=2.45, Recency ratio=3.26
- Early IC=+0.0470, Recent IC=+0.1532, 1st-half IC=+0.0609, 2nd-half IC=+0.1491, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.137, Q3_mid=+0.074, Q4=+0.117, Q5_high_vol=+0.164

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend`** (Lock IC=+0.0685, Sharpe=+0.3465)
- Admission: Train IC=+0.1935, Deflated=+0.1935, IR=0.53, Mono=0.72, p=0.0002, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.174 | 2017: +0.048 | 2018: +0.164 | 2019: +0.134 | 2020: +0.118 | 2021: +0.042 | 2022: +0.077 | 2023: +0.041 | 2024: +0.089 | 2025: +0.086 | 2026: -0.005
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.312 | 2017: +0.084 | 2018: +0.300 | 2019: +0.369 | 2020: +0.074 | 2021: +0.104 | 2022: +0.298 | 2023: +0.100 | 2024: +0.272 | 2025: +0.077 | 2026: +0.093
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.53
- Early IC=+0.1111, Recent IC=+0.0589, 1st-half IC=+0.1372, 2nd-half IC=+0.0770, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.84)
- Regime ICs: Q1_low_vol=+0.015, Q2=+0.084, Q3_mid=+0.117, Q4=+0.128, Q5_high_vol=+0.106

**`combo_mean__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0853, Sharpe=+0.3259)
- Admission: Train IC=+0.2366, Deflated=+0.2358, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.066 | 2017: +0.046 | 2018: +0.087 | 2019: +0.175 | 2020: +0.094 | 2021: +0.153 | 2022: +0.104 | 2023: +0.196 | 2024: +0.089 | 2025: +0.175 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.105 | 2017: +0.127 | 2018: +0.249 | 2019: +0.347 | 2020: +0.204 | 2021: +0.256 | 2022: +0.312 | 2023: +0.592 | 2024: +0.208 | 2025: +0.055 | 2026: -0.308
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=2.67
- Early IC=+0.0563, Recent IC=+0.1504, 1st-half IC=+0.0889, 2nd-half IC=+0.1375, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.139, Q3_mid=+0.114, Q4=+0.109, Q5_high_vol=+0.151

**`combo_ratio__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0538, Sharpe=+0.3166)
- Admission: Train IC=+0.1683, Deflated=+0.1674, IR=0.48, Mono=0.69, p=0.0016, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.055 | 2017: +0.032 | 2018: +0.028 | 2019: +0.120 | 2020: +0.113 | 2021: +0.149 | 2022: +0.110 | 2023: +0.150 | 2024: +0.057 | 2025: +0.127 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.084 | 2016: +0.084 | 2017: +0.055 | 2018: +0.093 | 2019: +0.379 | 2020: +0.196 | 2021: +0.168 | 2022: +0.133 | 2023: +0.250 | 2024: +0.184 | 2025: +0.173 | 2026: -0.348
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=2.67, Recency ratio=2.97
- Early IC=+0.0438, Recent IC=+0.1300, 1st-half IC=+0.0502, 2nd-half IC=+0.1343, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.103, Q3_mid=+0.095, Q4=+0.052, Q5_high_vol=+0.145

**`combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1273, Sharpe=+0.3112)
- Admission: Train IC=+0.1774, Deflated=+0.1767, IR=0.37, Mono=0.66, p=0.0010, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.050 | 2017: +0.034 | 2018: +0.054 | 2019: +0.131 | 2020: +0.104 | 2021: +0.109 | 2022: +0.148 | 2023: +0.133 | 2024: +0.127 | 2025: +0.164 | 2026: +0.066
- Yearly Tail ICs:   2015: -0.034 | 2016: +0.056 | 2017: +0.113 | 2018: +0.163 | 2019: +0.223 | 2020: +0.123 | 2021: +0.228 | 2022: +0.237 | 2023: +0.190 | 2024: +0.212 | 2025: +0.018 | 2026: -0.063
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=2.10, Recency ratio=3.36
- Early IC=+0.0419, Recent IC=+0.1406, 1st-half IC=+0.0627, 2nd-half IC=+0.1318, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.082, Q3_mid=+0.096, Q4=+0.088, Q5_high_vol=+0.130

**`combo_max__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=+0.0856, Sharpe=+0.3018)
- Admission: Train IC=+0.1777, Deflated=+0.1776, IR=0.37, Mono=0.66, p=0.0010, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.086 | 2017: +0.048 | 2018: +0.079 | 2019: +0.127 | 2020: +0.122 | 2021: +0.181 | 2022: +0.086 | 2023: +0.159 | 2024: +0.071 | 2025: +0.205 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.131 | 2016: -0.108 | 2017: +0.142 | 2018: +0.198 | 2019: +0.251 | 2020: +0.010 | 2021: +0.295 | 2022: +0.201 | 2023: +0.420 | 2024: +0.129 | 2025: +0.413 | 2026: -0.559
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=1.77, Recency ratio=1.83
- Early IC=+0.0671, Recent IC=+0.1227, 1st-half IC=+0.0790, 2nd-half IC=+0.1396, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.108, Q3_mid=+0.142, Q4=+0.080, Q5_high_vol=+0.147

**`combo_max__max_up_ret__rally_strength_max`** (Lock IC=+0.0649, Sharpe=+0.2842)
- Admission: Train IC=+0.2111, Deflated=+0.2109, IR=0.47, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.040 | 2017: +0.042 | 2018: +0.056 | 2019: +0.151 | 2020: +0.047 | 2021: +0.166 | 2022: +0.066 | 2023: +0.149 | 2024: +0.041 | 2025: +0.187 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.091 | 2016: +0.096 | 2017: +0.014 | 2018: +0.183 | 2019: +0.338 | 2020: +0.207 | 2021: +0.318 | 2022: +0.218 | 2023: +0.369 | 2024: +0.267 | 2025: +0.124 | 2026: -0.262
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=1.65, Recency ratio=2.63
- Early IC=+0.0410, Recent IC=+0.1077, 1st-half IC=+0.0680, 2nd-half IC=+0.1120, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.34)
- Regime ICs: Q1_low_vol=+0.003, Q2=+0.104, Q3_mid=+0.128, Q4=+0.111, Q5_high_vol=+0.104

**`combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1244, Sharpe=+0.2717)
- Admission: Train IC=+0.2020, Deflated=+0.2013, IR=0.44, Mono=0.66, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.087 | 2017: +0.029 | 2018: +0.070 | 2019: +0.151 | 2020: +0.121 | 2021: +0.145 | 2022: +0.148 | 2023: +0.140 | 2024: +0.129 | 2025: +0.126 | 2026: +0.116
- Yearly Tail ICs:   2015: -0.016 | 2016: +0.189 | 2017: +0.086 | 2018: +0.185 | 2019: +0.257 | 2020: +0.120 | 2021: +0.285 | 2022: +0.206 | 2023: +0.227 | 2024: +0.137 | 2025: +0.050 | 2026: +0.131
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.65, Recency ratio=2.48
- Early IC=+0.0581, Recent IC=+0.1442, 1st-half IC=+0.0847, 2nd-half IC=+0.1401, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.057, Q2=+0.102, Q3_mid=+0.077, Q4=+0.131, Q5_high_vol=+0.165

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0659, Sharpe=+0.2315)
- Admission: Train IC=+0.2283, Deflated=+0.2273, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.101 | 2017: +0.049 | 2018: +0.068 | 2019: +0.164 | 2020: +0.097 | 2021: +0.162 | 2022: +0.095 | 2023: +0.170 | 2024: +0.076 | 2025: +0.136 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.368 | 2016: +0.138 | 2017: +0.164 | 2018: +0.146 | 2019: +0.374 | 2020: +0.181 | 2021: +0.290 | 2022: +0.210 | 2023: +0.485 | 2024: +0.220 | 2025: +0.110 | 2026: -0.162
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.61, Recency ratio=1.77
- Early IC=+0.0749, Recent IC=+0.1324, 1st-half IC=+0.0828, 2nd-half IC=+0.1336, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.129, Q3_mid=+0.103, Q4=+0.106, Q5_high_vol=+0.151

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1026, Sharpe=+0.2266)
- Admission: Train IC=+0.2067, Deflated=+0.2063, IR=0.44, Mono=0.65, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.121 | 2017: +0.034 | 2018: +0.109 | 2019: +0.132 | 2020: +0.123 | 2021: +0.173 | 2022: +0.130 | 2023: +0.156 | 2024: +0.100 | 2025: +0.112 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.059 | 2016: +0.168 | 2017: +0.125 | 2018: +0.318 | 2019: +0.199 | 2020: +0.036 | 2021: +0.421 | 2022: +0.063 | 2023: +0.268 | 2024: +0.137 | 2025: +0.076 | 2026: +0.028
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.49, Recency ratio=1.85
- Early IC=+0.0774, Recent IC=+0.1433, 1st-half IC=+0.0976, 2nd-half IC=+0.1454, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.092, Q3_mid=+0.097, Q4=+0.131, Q5_high_vol=+0.185

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0846, Sharpe=+0.2222)
- Admission: Train IC=+0.2465, Deflated=+0.2463, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.142 | 2017: +0.007 | 2018: +0.120 | 2019: +0.193 | 2020: +0.128 | 2021: +0.160 | 2022: +0.096 | 2023: +0.173 | 2024: +0.059 | 2025: +0.174 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.163 | 2017: -0.001 | 2018: +0.271 | 2019: +0.369 | 2020: +0.256 | 2021: +0.255 | 2022: +0.228 | 2023: +0.534 | 2024: +0.192 | 2025: +0.074 | 2026: -0.090
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=1.27, Recency ratio=1.80
- Early IC=+0.0745, Recent IC=+0.1341, 1st-half IC=+0.1104, 2nd-half IC=+0.1397, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.126, Q3_mid=+0.111, Q4=+0.107, Q5_high_vol=+0.181

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1099, Sharpe=+0.2013)
- Admission: Train IC=+0.2131, Deflated=+0.2128, IR=0.50, Mono=0.66, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.161 | 2017: +0.030 | 2018: +0.132 | 2019: +0.123 | 2020: +0.132 | 2021: +0.160 | 2022: +0.154 | 2023: +0.136 | 2024: +0.080 | 2025: +0.147 | 2026: +0.107
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.148 | 2017: +0.200 | 2018: +0.323 | 2019: +0.164 | 2020: +0.081 | 2021: +0.457 | 2022: +0.123 | 2023: +0.282 | 2024: +0.169 | 2025: +0.125 | 2026: +0.096
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.37, Recency ratio=1.53
- Early IC=+0.0955, Recent IC=+0.1458, 1st-half IC=+0.1100, 2nd-half IC=+0.1511, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.131, Q3_mid=+0.090, Q4=+0.118, Q5_high_vol=+0.185

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1084, Sharpe=+0.1964)
- Admission: Train IC=+0.2177, Deflated=+0.2174, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.165 | 2017: +0.032 | 2018: +0.133 | 2019: +0.128 | 2020: +0.138 | 2021: +0.158 | 2022: +0.149 | 2023: +0.134 | 2024: +0.079 | 2025: +0.137 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.173 | 2017: +0.219 | 2018: +0.283 | 2019: +0.167 | 2020: +0.109 | 2021: +0.445 | 2022: +0.116 | 2023: +0.239 | 2024: +0.158 | 2025: +0.079 | 2026: +0.138
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.32, Recency ratio=1.43
- Early IC=+0.0989, Recent IC=+0.1413, 1st-half IC=+0.1130, 2nd-half IC=+0.1495, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.127, Q3_mid=+0.088, Q4=+0.125, Q5_high_vol=+0.182

**`combo_tri_median__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.0898, Sharpe=+0.1198)
- Admission: Train IC=+0.1936, Deflated=+0.1952, IR=0.43, Mono=0.68, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.131 | 2017: -0.073 | 2018: +0.112 | 2019: +0.088 | 2020: +0.097 | 2021: +0.001 | 2022: +0.163 | 2023: +0.160 | 2024: +0.077 | 2025: +0.082 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.268 | 2017: -0.194 | 2018: +0.226 | 2019: +0.076 | 2020: +0.231 | 2021: +0.119 | 2022: +0.425 | 2023: +0.080 | 2024: +0.089 | 2025: -0.053 | 2026: +0.005
- IC CV=0.90, Neg years (linear/tail)=1/1 of 8, Half ratio=1.25, Recency ratio=5.52
- Early IC=+0.0292, Recent IC=+0.1614, 1st-half IC=+0.0820, 2nd-half IC=+0.1026, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.121, Q3_mid=+0.064, Q4=+0.100, Q5_high_vol=+0.109

**`combo_rank_max__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0964, Sharpe=+0.0936)
- Admission: Train IC=+0.1871, Deflated=+0.1869, IR=0.57, Mono=0.68, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.040 | 2017: +0.033 | 2018: +0.085 | 2019: +0.130 | 2020: +0.074 | 2021: +0.174 | 2022: +0.173 | 2023: +0.138 | 2024: +0.083 | 2025: +0.135 | 2026: +0.066
- Yearly Tail ICs:   2015: -0.079 | 2016: +0.151 | 2017: +0.228 | 2018: +0.286 | 2019: +0.176 | 2020: +0.034 | 2021: +0.404 | 2022: +0.201 | 2023: +0.136 | 2024: +0.197 | 2025: +0.015 | 2026: -0.068
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=2.26, Recency ratio=3.83
- Early IC=+0.0406, Recent IC=+0.1555, 1st-half IC=+0.0641, 2nd-half IC=+0.1447, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.057, Q2=+0.124, Q3_mid=+0.077, Q4=+0.115, Q5_high_vol=+0.151

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0780, Sharpe=+0.0786)
- Admission: Train IC=+0.2391, Deflated=+0.2387, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.108 | 2017: +0.033 | 2018: +0.088 | 2019: +0.180 | 2020: +0.104 | 2021: +0.191 | 2022: +0.100 | 2023: +0.184 | 2024: +0.073 | 2025: +0.168 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.121 | 2017: +0.110 | 2018: +0.210 | 2019: +0.296 | 2020: +0.089 | 2021: +0.329 | 2022: +0.301 | 2023: +0.395 | 2024: +0.151 | 2025: +0.227 | 2026: -0.367
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.43, Recency ratio=2.01
- Early IC=+0.0707, Recent IC=+0.1417, 1st-half IC=+0.1006, 2nd-half IC=+0.1438, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.090, Q2=+0.109, Q3_mid=+0.128, Q4=+0.108, Q5_high_vol=+0.169

**`combo_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0770, Sharpe=+0.0324)
- Admission: Train IC=+0.1829, Deflated=+0.1825, IR=0.52, Mono=0.72, p=0.0008, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.050 | 2017: +0.055 | 2018: +0.049 | 2019: +0.124 | 2020: +0.094 | 2021: +0.159 | 2022: +0.102 | 2023: +0.183 | 2024: +0.061 | 2025: +0.190 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.114 | 2017: +0.002 | 2018: +0.126 | 2019: +0.256 | 2020: +0.088 | 2021: +0.301 | 2022: +0.293 | 2023: +0.472 | 2024: +0.228 | 2025: +0.118 | 2026: -0.527
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=2.11, Recency ratio=2.69
- Early IC=+0.0529, Recent IC=+0.1425, 1st-half IC=+0.0660, 2nd-half IC=+0.1395, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.111, Q3_mid=+0.114, Q4=+0.076, Q5_high_vol=+0.134

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0655 | +0.0326 | -0.0639 | 1y |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Median | gradual | +0.0634 | +0.0575 | -0.1666 | 2y |
| `combo_max__max_up_ret__bar_ret_0` | TP | gradual | +0.0601 | +0.0772 | -0.1564 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | TP | gradual | +0.0585 | +0.0483 | -0.1610 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0560 | +0.0672 | -0.0652 | 2y |
| `combo_min__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0541 | +0.0224 | -0.0760 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0533 | +0.0500 | -0.0305 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | TP | gradual | +0.0532 | +0.1011 | -0.1044 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0498 | +0.0530 | -0.0159 | 2y |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0497 | +0.0731 | -0.0612 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Median | gradual | +0.0487 | +0.0713 | -0.0495 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0479 | +0.0931 | +0.0021 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0458 | +0.0694 | -0.1100 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | gradual | +0.0431 | +0.0947 | -0.0161 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.0429 | +0.0675 | -0.0674 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.0427 | +0.0791 | -0.0285 | 2y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | gradual | +0.0418 | +0.1055 | -0.2078 | 2y |
| `combo_tri_median__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.0407 | +0.0730 | -0.0796 | 2y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0386 | +0.0944 | +0.0458 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0` | TP | gradual | +0.0305 | +0.0846 | -0.0513 | 2y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Median | gradual | +0.0297 | +0.1074 | -0.1940 | 2y |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0295 | +0.0718 | -0.0267 | 2y |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0290 | +0.0978 | +0.0141 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0290 | +0.0718 | -0.0276 | 2y |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0272 | +0.1119 | -0.1848 | 2y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0215 | +0.0910 | -0.1932 | 2y |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.0145 | +0.0760 | -0.0984 | 2y |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0142 | +0.0646 | +0.0712 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0138 | +0.0841 | -0.0065 | 2y |
| `combo_tri_median__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.0131 | +0.0679 | -0.1164 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Median | gradual | +0.0124 | +0.0988 | -0.1439 | 2y |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Median | gradual | +0.0106 | +0.1003 | -0.1508 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | FP | gradual | +0.0093 | +0.0956 | -0.1968 | ∞ |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | Median | gradual | +0.0084 | +0.1091 | -0.1474 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | TP | gradual | +0.0045 | +0.0755 | -0.0332 | ∞ |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | Median | gradual | +0.0032 | +0.1067 | -0.1238 | ∞ |
| `combo_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Median | immediate | -0.0044 | +0.1224 | -0.1415 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=32, persistent=4

**FP decay trajectories:**

- `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position`: Y1:+0.009 → Y2:+0.096 → Y3:-0.197
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:+0.022 → Y2:+0.091 → Y3:-0.193
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:+0.027 → Y2:+0.112 → Y3:-0.185
- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.042 → Y2:+0.105 → Y3:-0.208

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1803 | +0.0831 | +0.1124 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1735 | +0.1023 | +0.0066 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1723 | +0.1082 | +0.1064 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_return` | TP | gradual | +0.1632 | +0.0981 | -0.0677 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1606 | +0.1038 | +0.0031 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.1596 | +0.0843 | -0.0108 | 2y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.1595 | +0.0598 | -0.0091 | 1y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1590 | +0.1063 | +0.1978 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1587 | +0.0925 | +0.0908 | ∞ |
| `combo_mean__max_up_ret__max_down_ret` | TP | gradual | +0.1586 | +0.1074 | -0.0204 | 2y |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1576 | +0.0579 | +0.0057 | 1y |
| `combo_sig_product__max_up_ret__net_volume_flow` | TP | persistent | +0.1571 | +0.0784 | +0.0070 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | gradual | +0.1565 | +0.1389 | -0.0049 | 2y |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1560 | +0.0950 | -0.0080 | 2y |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | gradual | +0.1557 | +0.1569 | -0.0489 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | TP | gradual | +0.1540 | +0.1103 | -0.0291 | 2y |
| `combo_max__opening_drive_thrust_ratio__first_bar_return` | TP | gradual | +0.1531 | +0.0821 | -0.0151 | 2y |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | TP | gradual | +0.1527 | +0.1035 | -0.0696 | 2y |
| `opening_drive_thrust_ratio` | TP | persistent | +0.1521 | +0.0877 | +0.0025 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.1516 | +0.1255 | -0.0279 | 2y |
| `combo_mean__first_bar_return__close_vs_open_range` | TP | gradual | +0.1507 | +0.1141 | -0.0361 | 2y |
| `combo_min__max_up_ret__close_vs_open_range` | TP | gradual | +0.1498 | +0.1583 | -0.0680 | 2y |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1497 | +0.1101 | -0.0224 | 2y |
| `combo_max__max_up_ret__first_bar_return` | Median | gradual | +0.1493 | +0.0945 | -0.0638 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | TP | gradual | +0.1491 | +0.1211 | -0.0525 | 2y |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1482 | +0.0810 | -0.0241 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure` | TP | gradual | +0.1462 | +0.1226 | -0.0563 | 2y |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | TP | persistent | +0.1455 | +0.1073 | +0.0822 | ∞ |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | TP | gradual | +0.1453 | +0.1080 | -0.0871 | 2y |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | TP | gradual | +0.1448 | +0.0950 | -0.0493 | 2y |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.1445 | +0.0964 | +0.0136 | 2y |
| `combo_mean__opening_drive_thrust_ratio__early_body_momentum` | Median | gradual | +0.1443 | +0.1139 | -0.0632 | 2y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | TP | gradual | +0.1442 | +0.0788 | -0.0474 | 2y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | gradual | +0.1435 | +0.0745 | -0.0132 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | TP | gradual | +0.1432 | +0.1252 | -0.0478 | 2y |
| `combo_max__net_volume_flow__max_down_ret` | Median | gradual | +0.1430 | +0.1322 | -0.0558 | 2y |
| `max_up_ret` | TP | gradual | +0.1427 | +0.0801 | -0.0291 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1426 | +0.1228 | -0.0491 | 2y |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.1419 | +0.0608 | +0.0219 | 1y |
| `combo_rank_max__first_bar_return__close_vs_open_range` | TP | gradual | +0.1413 | +0.1183 | -0.0953 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1412 | +0.1184 | +0.0512 | 2y |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1412 | +0.1218 | -0.0390 | 2y |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | Median | gradual | +0.1410 | +0.1073 | -0.0717 | 2y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1409 | +0.0715 | +0.0212 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1403 | +0.1099 | +0.0272 | 2y |
| `combo_min__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1397 | +0.1492 | -0.0797 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | persistent | +0.1393 | +0.1316 | +0.0955 | ∞ |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1385 | +0.1357 | +0.0880 | ∞ |
| `combo_rank_max__max_up_ret__max_down_ret` | TP | gradual | +0.1384 | +0.1115 | -0.0022 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.1382 | +0.1259 | -0.0552 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | TP | gradual | +0.1379 | +0.1358 | -0.0538 | 2y |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1378 | +0.1148 | +0.1554 | ∞ |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1377 | +0.0863 | -0.0133 | 2y |
| `combo_mean__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1373 | +0.0963 | -0.0352 | 2y |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | TP | persistent | +0.1369 | +0.1104 | +0.0072 | 2y |
| `combo_max__max_up_ret__max_down_ret` | TP | gradual | +0.1369 | +0.0967 | -0.0339 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__early_order_flow_imbalance` | TP | gradual | +0.1368 | +0.1061 | -0.1125 | 2y |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1367 | +0.1166 | -0.0695 | 2y |
| `combo_mean__net_volume_flow__first_bar_return` | TP | gradual | +0.1363 | +0.1080 | -0.0295 | 2y |
| `combo_max__first_bar_return__close_vs_open_range` | TP | gradual | +0.1359 | +0.1213 | -0.0914 | 2y |
| `combo_min__max_up_ret__early_order_flow_imbalance` | Median | gradual | +0.1357 | +0.0940 | -0.1246 | 2y |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1356 | +0.1097 | +0.0226 | 2y |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1356 | +0.0212 | +0.0758 | 1y |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.1349 | +0.0857 | -0.0954 | 2y |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1342 | +0.0859 | -0.0871 | 2y |
| `combo_mean__rsi_opening__bar_body_rng_0` | TP | gradual | +0.1338 | +0.1362 | -0.0347 | 2y |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1333 | +0.0912 | -0.0506 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | Median | gradual | +0.1328 | +0.1159 | -0.0487 | 2y |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1327 | +0.1330 | +0.0970 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | TP | gradual | +0.1323 | +0.0978 | -0.0619 | 2y |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1318 | +0.1127 | +0.0511 | 2y |
| `combo_min__first_bar_return__close_vs_open_range` | TP | persistent | +0.1316 | +0.1401 | +0.0121 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | TP | persistent | +0.1313 | +0.1223 | +0.0508 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1311 | +0.1011 | +0.0718 | ∞ |
| `combo_rank_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1310 | +0.0931 | -0.0433 | 2y |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1307 | +0.0953 | -0.0374 | 2y |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Median | gradual | +0.1306 | +0.0940 | -0.0634 | 2y |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1301 | +0.1004 | -0.0674 | 2y |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | TP | gradual | +0.1300 | +0.1418 | -0.0720 | 2y |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | TP | gradual | +0.1299 | +0.0992 | -0.1193 | 2y |
| `combo_rank_max__early_body_momentum__max_down_ret` | TP | gradual | +0.1298 | +0.1701 | -0.0787 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Median | gradual | +0.1294 | +0.1035 | -0.0465 | 2y |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | TP | gradual | +0.1293 | +0.1257 | -0.0021 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | TP | persistent | +0.1291 | +0.1487 | +0.0601 | 2y |
| `combo_clamp_diff__bar_ret_0__h2_l2_pullback_continuation` | TP | gradual | +0.1286 | +0.0985 | -0.0521 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.1283 | +0.1082 | -0.0063 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1281 | +0.1143 | +0.0829 | ∞ |
| `combo_min__close_vs_open_range__bar_body_rng_0` | TP | gradual | +0.1276 | +0.1339 | -0.0087 | 2y |
| `combo_min__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.1276 | +0.1354 | +0.0016 | 2y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1276 | +0.1303 | +0.0451 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Median | gradual | +0.1274 | +0.1268 | -0.0748 | 2y |
| `combo_rank_max__early_body_momentum__close_vs_open_range` | TP | gradual | +0.1274 | +0.1443 | -0.0910 | 2y |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.1274 | +0.1509 | +0.0451 | 2y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | gradual | +0.1272 | +0.1213 | -0.1240 | 2y |
| `combo_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1272 | +0.0217 | +0.0778 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | TP | persistent | +0.1271 | +0.1195 | +0.0048 | 2y |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.1265 | +0.0965 | +0.0040 | 2y |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.1258 | +0.1343 | -0.0732 | 2y |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.1253 | +0.1558 | +0.0502 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1252 | +0.1182 | +0.0845 | ∞ |
| `combo_tri_median__volatility_expansion_trend_vector__star50_limit_proximity_early__bar_ret_0` | TP | gradual | +0.1251 | +0.1715 | -0.0066 | 2y |
| `combo_max__bar_ret_0__max_down_ret` | TP | persistent | +0.1244 | +0.1076 | +0.0004 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1239 | +0.1399 | +0.0424 | 2y |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Median | gradual | +0.1238 | +0.1309 | -0.1085 | 2y |
| `combo_min__net_volume_flow__close_vs_open_range` | TP | gradual | +0.1237 | +0.1380 | -0.0671 | 2y |
| `combo_max__net_volume_flow__bar_body_rng_0` | TP | gradual | +0.1236 | +0.1114 | -0.0428 | 2y |
| `combo_mean__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Median | gradual | +0.1236 | +0.1189 | -0.0651 | 2y |
| `combo_max__bar_ret_0__vwap_close_divergence_trend` | Median | gradual | +0.1232 | +0.1303 | -0.1077 | 2y |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | TP | gradual | +0.1229 | +0.1434 | -0.0217 | 2y |
| `combo_tri_median__max_up_ret__net_volume_flow__volume_weighted_momentum_acceleration` | TP | gradual | +0.1227 | +0.1334 | -0.0584 | 2y |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1217 | +0.0896 | -0.0867 | 2y |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | Median | gradual | +0.1217 | +0.0996 | -0.0411 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend` | TP | gradual | +0.1209 | +0.1059 | -0.0352 | 2y |
| `combo_tri_median__max_up_ret__net_volume_flow__bar_ret_0` | TP | gradual | +0.1207 | +0.0813 | -0.0638 | 2y |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1205 | +0.1406 | +0.0260 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | TP | gradual | +0.1202 | +0.1161 | -0.0147 | 2y |
| `open_to_current_return` | TP | gradual | +0.1202 | +0.1639 | -0.1128 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Median | gradual | +0.1197 | +0.0962 | -0.0817 | 2y |
| `combo_mean__early_order_flow_imbalance__bar_body_rng_0` | Median | gradual | +0.1194 | +0.1053 | -0.0755 | 2y |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1193 | +0.1027 | -0.0638 | 2y |
| `combo_min__max_up_ret__max_down_ret` | TP | persistent | +0.1191 | +0.1388 | +0.0338 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | persistent | +0.1188 | +0.1183 | +0.0006 | 2y |
| `combo_max__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.1183 | +0.0878 | -0.0542 | 2y |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.1178 | +0.1721 | -0.0740 | 2y |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | Median | gradual | +0.1177 | +0.1343 | -0.0871 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.1177 | +0.1493 | +0.0858 | ∞ |
| `combo_min__first_bar_return__early_order_flow_imbalance` | TP | gradual | +0.1175 | +0.1017 | -0.0335 | 2y |
| `combo_max__early_body_momentum__first_bar_return` | Median | gradual | +0.1167 | +0.1258 | -0.1197 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.1167 | +0.1082 | +0.0649 | ∞ |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | TP | gradual | +0.1165 | +0.1502 | -0.0821 | 2y |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.1164 | +0.0467 | +0.0797 | 1y |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | Median | gradual | +0.1161 | +0.1242 | -0.0522 | 2y |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | TP | persistent | +0.1155 | +0.1037 | +0.0319 | 2y |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | Median | gradual | +0.1154 | +0.1265 | -0.1051 | 2y |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | TP | gradual | +0.1154 | +0.1253 | -0.0910 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.1151 | +0.1324 | +0.0778 | ∞ |
| `combo_rank_max__bar_ret_0__max_down_ret` | TP | persistent | +0.1144 | +0.1160 | +0.0292 | 2y |
| `combo_min__max_down_ret__close_vs_open_range` | TP | persistent | +0.1141 | +0.1398 | +0.0376 | 2y |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.1138 | +0.0683 | -0.0039 | 2y |
| `combo_min__net_volume_flow__max_down_ret` | TP | persistent | +0.1137 | +0.1375 | +0.0352 | 2y |
| `combo_rank_max__net_volume_flow__vwap_close_divergence_trend` | Median | gradual | +0.1134 | +0.1487 | -0.0987 | 2y |
| `combo_mean__first_bar_return__bar_body_rng_0` | TP | gradual | +0.1126 | +0.0948 | -0.0044 | 2y |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | TP | persistent | +0.1119 | +0.1076 | +0.0249 | 2y |
| `combo_tri_max__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | gradual | +0.1119 | +0.0841 | -0.0686 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | TP | gradual | +0.1113 | +0.1117 | -0.0434 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | TP | gradual | +0.1112 | +0.1509 | -0.0779 | 2y |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1110 | +0.1045 | +0.1074 | ∞ |
| `combo_sig_product__early_body_momentum__close_vs_open_range` | TP | gradual | +0.1109 | +0.1511 | -0.0883 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | TP | gradual | +0.1107 | +0.1298 | -0.0391 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | TP | persistent | +0.1107 | +0.1390 | +0.0238 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | TP | persistent | +0.1102 | +0.1142 | +0.1111 | ∞ |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.1101 | +0.1307 | +0.0118 | 2y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | TP | persistent | +0.1092 | +0.0819 | +0.0690 | ∞ |
| `combo_tri_median__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | gradual | +0.1092 | +0.1503 | -0.0835 | 2y |
| `combo_max__volatility_expansion_trend_vector__vwap_close_divergence_trend` | Median | gradual | +0.1088 | +0.1462 | -0.0961 | 2y |
| `combo_min__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.1087 | +0.0804 | -0.0090 | 2y |
| `combo_rank_max__first_bar_return__early_order_flow_imbalance` | Median | gradual | +0.1083 | +0.0976 | -0.1213 | 2y |
| `combo_tri_mean__early_body_momentum__star50_limit_proximity_early__trend_day_regime_conviction` | TP | persistent | +0.1078 | +0.1141 | +0.0284 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.1074 | +0.1014 | +0.0358 | 2y |
| `combo_max__vwap_close_divergence_trend__bar_body_rng_0` | Median | gradual | +0.1072 | +0.1433 | -0.0802 | 2y |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | Median | gradual | +0.1071 | +0.1552 | -0.0705 | 2y |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | TP | gradual | +0.1066 | +0.1354 | -0.1029 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1062 | +0.1351 | +0.0962 | ∞ |
| `combo_rank_max__early_body_momentum__early_order_flow_imbalance` | Median | gradual | +0.1061 | +0.1277 | -0.1270 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1061 | +0.1194 | +0.1047 | ∞ |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early` | TP | persistent | +0.1059 | +0.1166 | +0.0519 | 2y |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | TP | gradual | +0.1058 | +0.1269 | -0.0926 | 2y |
| `combo_max__first_bar_return__early_order_flow_imbalance` | Median | gradual | +0.1056 | +0.0915 | -0.1190 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.1054 | +0.1474 | +0.0539 | ∞ |
| `combo_clamp_diff__bar_ret_0__body_size_progression` | TP | persistent | +0.1048 | +0.0366 | +0.0879 | 1y |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | TP | gradual | +0.1039 | +0.1401 | -0.0605 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.1037 | +0.1053 | +0.0518 | 2y |
| `vwap_trend_channel_slope` | Median | gradual | +0.1037 | +0.0941 | -0.0312 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__bar_ret_0` | TP | persistent | +0.1035 | +0.1382 | +0.0428 | 2y |
| `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0` | TP | gradual | +0.1026 | +0.1203 | -0.0238 | 2y |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1019 | +0.0250 | +0.0952 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1018 | +0.0924 | +0.0836 | ∞ |
| `combo_sig_product__max_up_ret__first_bar_return` | TP | gradual | +0.1013 | +0.0769 | -0.0792 | 2y |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | TP | persistent | +0.1012 | +0.0470 | +0.1094 | 1y |
| `combo_max__first_bar_return__shaved_bar_trend_conviction` | TP | gradual | +0.1009 | +0.1323 | -0.1011 | 2y |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1007 | +0.0966 | +0.1228 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1006 | +0.0900 | +0.0731 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.1004 | +0.1027 | +0.0777 | ∞ |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | TP | gradual | +0.0990 | +0.1208 | -0.0065 | 2y |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0984 | +0.0800 | +0.0015 | 2y |
| `combo_min__first_bar_return__vwap_close_divergence_trend` | TP | persistent | +0.0980 | +0.1185 | +0.0081 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0968 | +0.1016 | -0.0804 | 2y |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | TP | gradual | +0.0954 | +0.1265 | -0.0958 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Median | gradual | +0.0950 | +0.0858 | -0.0790 | 2y |
| `combo_rel_diff__first_bar_return__body_size_progression` | TP | persistent | +0.0921 | +0.0326 | +0.0788 | 1y |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | Median | gradual | +0.0906 | +0.0395 | -0.0579 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.0902 | +0.1084 | +0.0820 | ∞ |
| `combo_min__net_volume_flow__shaved_bar_trend_conviction` | TP | gradual | +0.0890 | +0.1080 | -0.0844 | 2y |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | TP | gradual | +0.0883 | +0.1219 | -0.0861 | 2y |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0876 | +0.1301 | +0.0834 | ∞ |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0874 | +0.0221 | +0.0886 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0853 | +0.1336 | +0.0332 | 2y |
| `combo_tri_median__max_up_ret__smooth_momentum_structure__bar_ret_0` | TP | gradual | +0.0847 | +0.1254 | -0.0874 | 2y |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0842 | +0.1415 | +0.0832 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | TP | persistent | +0.0841 | +0.0834 | +0.0853 | ∞ |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | TP | gradual | +0.0811 | +0.1234 | -0.0876 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__smooth_momentum_structure` | TP | persistent | +0.0802 | +0.1118 | +0.1038 | ∞ |
| `combo_sig_product__first_bar_return__vwap_close_divergence_trend` | Median | gradual | +0.0727 | +0.0676 | -0.1037 | 2y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0683 | +0.0453 | +0.1157 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.0362 | +0.0959 | +0.0658 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=123, persistent=82

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1489 | +0.1924 | +0.0123 | 2y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.1426 | +0.0743 | +0.1028 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1405 | +0.1002 | +0.1012 | ∞ |
| `combo_diff__max_up_ret__keltner_squeeze_width` | TP | gradual | +0.1364 | +0.1533 | -0.0616 | 2y |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | TP | gradual | +0.1349 | +0.1468 | -0.0633 | 2y |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1326 | +0.1360 | +0.1259 | ∞ |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | TP | gradual | +0.1325 | +0.1484 | -0.0230 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1297 | +0.1248 | -0.0819 | 2y |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1291 | +0.1262 | +0.1158 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1269 | +0.1640 | +0.0657 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1267 | +0.1392 | +0.1129 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1247 | +0.1135 | +0.1174 | ∞ |
| `combo_tri_max__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1238 | +0.0811 | +0.0849 | ∞ |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1232 | +0.1464 | +0.1249 | ∞ |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1225 | +0.1376 | +0.0821 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1225 | +0.1516 | +0.1037 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1194 | +0.1395 | +0.1093 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1193 | +0.1790 | +0.0373 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | TP | persistent | +0.1160 | +0.0949 | +0.2140 | ∞ |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1154 | +0.1557 | +0.1169 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1153 | +0.1681 | +0.0618 | ∞ |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1148 | +0.1732 | +0.0894 | ∞ |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__star50_limit_proximity_early` | TP | persistent | +0.1148 | +0.1707 | +0.0058 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | TP | persistent | +0.1137 | +0.0890 | +0.2142 | ∞ |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1135 | +0.1921 | +0.0467 | 2y |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1121 | +0.1255 | +0.1387 | ∞ |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1119 | +0.1805 | +0.0905 | ∞ |
| `combo_mean__max_up_ret__gap_pct` | TP | persistent | +0.1093 | +0.1611 | +0.1401 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1088 | +0.1069 | +0.0703 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | TP | persistent | +0.1084 | +0.1360 | +0.1233 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.1075 | +0.1827 | -0.0023 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1071 | +0.1602 | +0.1080 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1067 | +0.1723 | +0.0606 | ∞ |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1066 | +0.1533 | +0.1438 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1066 | +0.1533 | +0.1438 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.1061 | +0.1980 | -0.0899 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1055 | +0.1856 | +0.0321 | 2y |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0` | TP | persistent | +0.1028 | +0.1517 | +0.1023 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.1024 | +0.1185 | +0.1661 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | TP | persistent | +0.1023 | +0.0688 | +0.2140 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1003 | +0.1121 | +0.0918 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0999 | +0.1720 | +0.0720 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | TP | persistent | +0.0990 | +0.1088 | +0.0500 | ∞ |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.0983 | +0.1706 | +0.1014 | ∞ |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Median | gradual | +0.0965 | +0.1114 | -0.0547 | 2y |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.0955 | +0.2018 | -0.0890 | 2y |
| `combo_z_sum__volume_weighted_price_position__limit_down_proximity_early` | TP | persistent | +0.0945 | +0.1410 | +0.1206 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0944 | +0.1619 | +0.0982 | ∞ |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0934 | +0.1430 | +0.0494 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.0902 | +0.1776 | +0.1060 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0900 | +0.1568 | +0.1039 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | TP | gradual | +0.0889 | +0.0859 | -0.0046 | 2y |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0888 | +0.1747 | -0.0705 | 2y |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | gradual | +0.0886 | +0.1909 | -0.0074 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | TP | persistent | +0.0881 | +0.1553 | +0.0896 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Median | persistent | +0.0872 | +0.1651 | +0.1242 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | TP | gradual | +0.0861 | +0.1675 | -0.0014 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0854 | +0.1519 | +0.1362 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0849 | +0.1743 | +0.0798 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.0841 | +0.1049 | +0.1840 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0830 | +0.1740 | +0.0745 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.0827 | +0.1610 | +0.0867 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0825 | +0.2095 | +0.0649 | ∞ |
| `combo_min__bar_ret_0__limit_down_proximity_early` | TP | persistent | +0.0821 | +0.1534 | +0.1227 | ∞ |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.0814 | +0.1313 | +0.0607 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.0802 | +0.0835 | +0.1344 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0801 | +0.1735 | +0.1094 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0797 | +0.1820 | +0.0509 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0796 | +0.1442 | +0.1059 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0789 | +0.1366 | +0.1130 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.0788 | +0.1624 | +0.0797 | ∞ |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.0788 | +0.1482 | -0.0153 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | TP | persistent | +0.0784 | +0.0608 | +0.1619 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0781 | +0.1616 | -0.0242 | 2y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.0781 | +0.1350 | -0.0033 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0780 | +0.1727 | -0.0641 | 2y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_momentum` | TP | gradual | +0.0779 | +0.1016 | -0.0064 | 2y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.0778 | +0.1847 | +0.0017 | 2y |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0776 | +0.1381 | +0.0217 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0776 | +0.1667 | -0.0001 | 2y |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0775 | +0.2033 | -0.0561 | 2y |
| `combo_min__max_up_ret__rally_strength_max` | TP | gradual | +0.0771 | +0.1717 | -0.0676 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0767 | +0.2129 | +0.0668 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.0766 | +0.0820 | +0.1018 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | TP | gradual | +0.0759 | +0.1364 | -0.0681 | 2y |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | TP | persistent | +0.0758 | +0.0855 | +0.0326 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | TP | persistent | +0.0750 | +0.1370 | +0.0941 | ∞ |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | TP | persistent | +0.0747 | +0.1498 | +0.0176 | 2y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.0732 | +0.1684 | -0.0687 | 2y |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | TP | persistent | +0.0728 | +0.1175 | +0.1525 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0724 | +0.2210 | +0.0502 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0722 | +0.1788 | +0.0652 | ∞ |
| `combo_diff__rbreaker_sell_setup_proximity_early__gap_pct` | TP | gradual | +0.0719 | +0.1528 | -0.0925 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0712 | +0.1626 | +0.1095 | ∞ |
| `combo_max__max_up_ret__volume_price_confirmation` | TP | gradual | +0.0709 | +0.1307 | -0.0293 | 2y |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | TP | gradual | +0.0708 | +0.2053 | -0.0784 | 2y |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0708 | +0.1339 | +0.1332 | ∞ |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | TP | gradual | +0.0703 | +0.1982 | -0.0377 | 2y |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | TP | gradual | +0.0685 | +0.1962 | -0.0346 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.0661 | +0.1026 | +0.0794 | ∞ |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0653 | +0.1664 | +0.0917 | ∞ |
| `combo_mean__first_bar_return__limit_down_proximity_early` | TP | persistent | +0.0650 | +0.1549 | +0.1123 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0638 | +0.1735 | +0.1144 | ∞ |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0628 | +0.1841 | -0.0596 | 2y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0617 | +0.1891 | +0.0840 | ∞ |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.0612 | +0.1900 | -0.0929 | 2y |
| `combo_rank_min__max_up_ret__gap_pct` | TP | persistent | +0.0591 | +0.1288 | +0.1004 | ∞ |
| `combo_mean__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0588 | +0.1735 | -0.0304 | 2y |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0577 | +0.1494 | +0.0044 | 2y |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | TP | gradual | +0.0568 | +0.1274 | -0.0851 | 2y |
| `combo_mean__max_up_ret__rally_strength_max` | TP | gradual | +0.0558 | +0.1835 | -0.0910 | 2y |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | TP | gradual | +0.0557 | +0.1555 | -0.0187 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.0546 | +0.0855 | +0.1440 | ∞ |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0498 | +0.1709 | +0.0448 | ∞ |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0428 | +0.1826 | +0.0538 | ∞ |
| `combo_max__max_up_ret__rally_strength_max` | TP | gradual | +0.0415 | +0.1872 | -0.0915 | 2y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | Median | gradual | +0.0406 | +0.1773 | -0.0616 | 2y |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0333 | +0.1095 | +0.0851 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | TP | persistent | +0.0186 | +0.1295 | +0.0193 | ∞ |
| `combo_ifelse__gap_pct__yesterday_early_momentum__bar_body_rng_0` | Median | immediate | -0.0449 | +0.0734 | +0.0351 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=35, persistent=84

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.796±0.023 | 0.707±0.036 | 10% | USEFUL |
| ic_ir | 0.797±0.055 | 0.568±0.094 | 6% | USEFUL |
| p_value | 0.000±0.000 | 0.000±0.000 | 20% | USEFUL |
| max_corr | 0.818±0.137 | 0.914±0.028 | 21% | USEFUL |
| deflated_ic | 0.223±0.025 | 0.209±0.028 | 68% | WEAK |
| overall_ic | 0.223±0.025 | 0.209±0.028 | 68% | WEAK |
| raw_ic | 0.090±0.004 | 0.097±0.009 | 36% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 9/20 top rejects are profitable (45%)

- `combo_clamp_diff__volume_weighted_momentum_acceleration__morning_volume_weighted_momentum`: Train IC=+0.2776, Lock IC=+0.0257, Sharpe=+0.5519
- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188
- `combo_z_sum__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188

**B2 Rolling Guard**: 2/20 top rejects are profitable (10%)

- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`: Train IC=+0.1707, Lock IC=+0.0091, Sharpe=+0.1498
- `combo_clamp_diff__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.1830, Lock IC=+0.0145, Sharpe=+0.0044

**Temporal Validation Gate**: 12/20 top rejects are profitable (60%)

- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2135, Lock IC=+0.0413, Sharpe=+0.4517
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2135, Lock IC=+0.0413, Sharpe=+0.4517
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2133, Lock IC=+0.0412, Sharpe=+0.4517

**BH-FDR Gate**: 1/13 top rejects are profitable (8%)

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Sharpe=+0.1611

**B6 Yearly IC CV Gate**: 5/20 top rejects are profitable (25%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1686, Lock IC=+0.0350, Sharpe=+0.7401
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1615, Lock IC=+0.0427, Sharpe=+0.6518
- `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1615, Lock IC=+0.0427, Sharpe=+0.6518

**B4 Correlation Gate**: 10/20 top rejects are profitable (50%)

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2291, Lock IC=+0.0645, Sharpe=+0.9458
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2341, Lock IC=+0.0362, Sharpe=+0.3660
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2338, Lock IC=+0.0362, Sharpe=+0.3660

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2404, Lock IC=+0.1152, Sharpe=+1.1696
- `combo_z_sum__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2404, Lock IC=+0.1152, Sharpe=+1.1696

**B2 Rolling Guard**: 18/20 top rejects are profitable (90%)

- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Sharpe=+1.1213
- `combo_mean__first_bar_return__max_down_ret`: Train IC=+0.2006, Lock IC=+0.0980, Sharpe=+0.7814
- `combo_z_sum__first_bar_return__max_down_ret`: Train IC=+0.2006, Lock IC=+0.0980, Sharpe=+0.7814

**Temporal Validation Gate**: 15/20 top rejects are profitable (75%)

- `combo_rel_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2280, Lock IC=+0.0970, Sharpe=+1.1607
- `combo_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621
- `combo_z_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621

**B3 Composite Floor**: 14/18 top rejects are profitable (78%)

- `combo_tri_min__early_body_momentum__trend_day_regime_conviction__bar_ret_0`: Train IC=+0.1861, Lock IC=+0.0952, Sharpe=+0.8694
- `combo_tri_min__opening_momentum_score__trend_day_regime_conviction__bar_ret_0`: Train IC=+0.1861, Lock IC=+0.0952, Sharpe=+0.8694
- `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788

**B6 Yearly IC CV Gate**: 15/20 top rejects are profitable (75%)

- `combo_tri_min__smooth_momentum_structure__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.1429, Lock IC=+0.0568, Sharpe=+1.4431
- `combo_tri_min__net_volume_flow__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904
- `combo_tri_min__opening_auction_imbalance__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904

**B6 Temporal Stability Gate**: 8/9 top rejects are profitable (89%)

- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_mean__max_up_ret__net_volume_flow`: Train IC=+0.2524, Lock IC=+0.0849, Sharpe=+0.5247

**B4 Correlation Gate**: 18/20 top rejects are profitable (90%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.2777, Lock IC=+0.1084, Sharpe=+1.0418
- `combo_diff__net_volume_flow__smooth_momentum_structure`: Train IC=+0.2670, Lock IC=+0.0979, Sharpe=+1.0088
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.2671, Lock IC=+0.1077, Sharpe=+0.7168

### 159915ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation`: Train IC=+0.1910, Lock IC=+0.1273, Sharpe=+1.6071
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Sharpe=+1.0349

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2171, Lock IC=+0.1247, Sharpe=+1.7216
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2171, Lock IC=+0.1247, Sharpe=+1.7216
- `combo_diff__rbreaker_sell_setup_proximity_early__body_size_progression`: Train IC=+0.2045, Lock IC=+0.1229, Sharpe=+1.7085

**Temporal Validation Gate**: 19/20 top rejects are profitable (95%)

- `combo_diff__demark_setup_reversal_early__first_bar_return`: Train IC=+0.2499, Lock IC=+0.1062, Sharpe=+1.1247
- `combo_z_diff__demark_setup_reversal_early__first_bar_return`: Train IC=+0.2499, Lock IC=+0.1062, Sharpe=+1.1247
- `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Train IC=+0.2156, Lock IC=+0.1112, Sharpe=+1.0666

**BH-FDR Gate**: 1/3 top rejects are profitable (33%)

- `combo_min__volatility_expansion_trend_vector__volume_price_confirmation`: Train IC=+0.0993, Lock IC=+0.1096, Sharpe=+1.2340

**B3 Composite Floor**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2080, Lock IC=+0.1414, Sharpe=+1.4883
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return`: Train IC=+0.2197, Lock IC=+0.0779, Sharpe=+1.1602
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return`: Train IC=+0.2197, Lock IC=+0.0779, Sharpe=+1.1602

**B6 Yearly IC CV Gate**: 2/5 top rejects are profitable (40%)

- `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943
- `combo_rank_min__volume_weighted_price_position__rbreaker_buy_setup_proximity_early`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Sharpe=+1.8009
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2725, Lock IC=+0.1237, Sharpe=+1.5940

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1217 | 78 | 24 | 34 | 20 | 31% | 26% |
| B2 Rolling Guard | 141 | 78 | 33 | 25 | 20 | 42% | 26% |
| Temporal Validation Gate | 121 | 78 | 7 | 29 | 42 | 9% | 54% |
| BH-FDR Gate | 13 | 13 | 11 | 1 | 1 | 85% | 8% |
| B3 Composite Floor | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B6 Yearly IC CV Gate | 53 | 53 | 29 | 12 | 12 | 55% | 23% |
| B4 Correlation Gate | 58 | 58 | 4 | 15 | 39 | 7% | 67% |

**7-Year Jackknife** — top TP casualties:
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.1904, Lock IC=+0.0460, Sharpe=+0.7358
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.1904, Lock IC=+0.0460, Sharpe=+0.7358
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.1904, Lock IC=+0.0460, Sharpe=+0.7358

**B2 Rolling Guard** — top TP casualties:
- `combo_sig_product__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1341, Lock IC=+0.0176, Sharpe=+0.6337
- `combo_sig_product__smooth_momentum_structure__first_bar_return`: Train IC=+0.1340, Lock IC=+0.0177, Sharpe=+0.6337
- `combo_max__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0814, Lock IC=+0.0326, Sharpe=+0.6120

**Temporal Validation Gate** — top TP casualties:
- `sma100_dist`: Train IC=+0.1056, Lock IC=+0.0455, Sharpe=+0.6172
- `sma10_dist`: Train IC=+0.0626, Lock IC=+0.0444, Sharpe=+0.5378
- `keltner_position_atr10_20d`: Train IC=+0.0207, Lock IC=+0.0265, Sharpe=+0.5125

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1487, Lock IC=+0.0310, Sharpe=+0.9813
- `combo_rank_min__star50_limit_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1202, Lock IC=+0.0237, Sharpe=+0.8457
- `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1582, Lock IC=+0.0184, Sharpe=+0.8139

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2082, Lock IC=+0.0662, Sharpe=+1.2725
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2291, Lock IC=+0.0645, Sharpe=+0.9458
- `combo_tri_z_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.2033, Lock IC=+0.0311, Sharpe=+0.7153

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2628 | 78 | 31 | 20 | 27 | 40% | 35% |
| B2 Rolling Guard | 513 | 78 | 17 | 16 | 45 | 22% | 58% |
| Temporal Validation Gate | 149 | 78 | 23 | 14 | 41 | 29% | 53% |
| BH-FDR Gate | 6 | 6 | 1 | 5 | 0 | 17% | 0% |
| B3 Composite Floor | 18 | 18 | 0 | 4 | 14 | 0% | 78% |
| B6 Yearly IC CV Gate | 20 | 20 | 2 | 3 | 15 | 10% | 75% |
| B6 Temporal Stability Gate | 9 | 9 | 0 | 1 | 8 | 0% | 89% |
| B4 Correlation Gate | 857 | 78 | 0 | 4 | 74 | 0% | 95% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2404, Lock IC=+0.1152, Sharpe=+1.1696
- `combo_z_sum__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2404, Lock IC=+0.1152, Sharpe=+1.1696

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.1971, Lock IC=+0.1117, Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Sharpe=+1.2071
- `combo_mean__trend_day_regime_conviction__shaved_bar_trend_conviction`: Train IC=+0.1953, Lock IC=+0.0721, Sharpe=+1.1401

**Temporal Validation Gate** — top TP casualties:
- `combo_rank_min__volume_weighted_momentum_acceleration__demark_setup_reversal_early`: Train IC=+0.1922, Lock IC=+0.1059, Sharpe=+1.7076
- `close_location_in_range_3d`: Train IC=+0.0449, Lock IC=+0.0506, Sharpe=+1.3268
- `combo_diff__smooth_momentum_structure__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0974, Sharpe=+1.2934

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__early_body_momentum__trend_day_regime_conviction__bar_ret_0`: Train IC=+0.1861, Lock IC=+0.0952, Sharpe=+0.8694
- `combo_tri_min__opening_momentum_score__trend_day_regime_conviction__bar_ret_0`: Train IC=+0.1861, Lock IC=+0.0952, Sharpe=+0.8694
- `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.1429, Lock IC=+0.0568, Sharpe=+1.4431
- `combo_tri_min__net_volume_flow__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904
- `combo_tri_min__opening_auction_imbalance__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_mean__max_up_ret__net_volume_flow`: Train IC=+0.2524, Lock IC=+0.0849, Sharpe=+0.5247

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2217, Lock IC=+0.1214, Sharpe=+1.1911
- `combo_rel_diff__net_volume_flow__smooth_momentum_structure`: Train IC=+0.2655, Lock IC=+0.0902, Sharpe=+1.1893
- `combo_rel_diff__opening_auction_imbalance__smooth_momentum_structure`: Train IC=+0.2655, Lock IC=+0.0902, Sharpe=+1.1893

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2065 | 78 | 24 | 20 | 34 | 31% | 44% |
| B2 Rolling Guard | 336 | 78 | 21 | 8 | 49 | 27% | 63% |
| Temporal Validation Gate | 83 | 78 | 13 | 10 | 55 | 17% | 71% |
| BH-FDR Gate | 3 | 3 | 0 | 2 | 1 | 0% | 33% |
| B3 Composite Floor | 123 | 78 | 1 | 9 | 68 | 1% | 87% |
| B6 Yearly IC CV Gate | 5 | 5 | 3 | 0 | 2 | 60% | 40% |
| B4 Correlation Gate | 204 | 78 | 0 | 0 | 78 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation`: Train IC=+0.1910, Lock IC=+0.1273, Sharpe=+1.6071
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951

**B2 Rolling Guard** — top TP casualties:
- `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2171, Lock IC=+0.1247, Sharpe=+1.7216
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2171, Lock IC=+0.1247, Sharpe=+1.7216
- `combo_diff__rbreaker_sell_setup_proximity_early__body_size_progression`: Train IC=+0.2045, Lock IC=+0.1229, Sharpe=+1.7085

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rank_min__demark_setup_reversal_early__volume_weighted_momentum_acceleration`: Train IC=+0.1699, Lock IC=+0.0912, Sharpe=+1.3833

**BH-FDR Gate** — top TP casualties:
- `combo_min__volatility_expansion_trend_vector__volume_price_confirmation`: Train IC=+0.0993, Lock IC=+0.1096, Sharpe=+1.2340

**B3 Composite Floor** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2080, Lock IC=+0.1414, Sharpe=+1.4883
- `combo_rank_min__volatility_expansion_trend_vector__volume_price_confirmation`: Train IC=+0.1247, Lock IC=+0.1110, Sharpe=+1.4614
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2049, Lock IC=+0.1184, Sharpe=+1.3299

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943
- `combo_rank_min__volume_weighted_price_position__rbreaker_buy_setup_proximity_early`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943

**B4 Correlation Gate** — top TP casualties:
- `combo_mean__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.1781, Lock IC=+0.1324, Sharpe=+1.9041
- `combo_z_sum__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.1781, Lock IC=+0.1324, Sharpe=+1.9041
- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (121 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 84 | 50 | 8 | 16 | 26 | 16% | 32% |
| recency_ratio >= 2.5 (late-concentrated) | 30 | 30 | 0 | 24 | 6 | 0% | 80% |

**Top TP killed by recency_ratio cap:**
- `first_bar_return`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `bar_ret_0`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `combo_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1732, Lock IC=+0.0201, Sharpe=+0.4670
- `combo_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1731, Lock IC=+0.0200, Sharpe=+0.4670
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.1952, Lock IC=+0.0171, Sharpe=+0.4208

### 500ETF — `single` (149 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 142 | 50 | 0 | 41 | 9 | 0% | 82% |
| recency_ratio >= 2.5 (late-concentrated) | 2 | 2 | 0 | 0 | 2 | 0% | 0% |

### 159915ETF — `single` (83 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 57 | 50 | 8 | 36 | 6 | 16% | 72% |
| recency_ratio >= 2.5 (late-concentrated) | 24 | 24 | 0 | 21 | 3 | 0% | 88% |

**Top TP killed by recency_ratio cap:**
- `combo_mean__max_up_ret__directional_volume_signature`: Train IC=+0.1697, Lock IC=+0.1016, Sharpe=+1.3696
- `combo_z_sum__max_up_ret__directional_volume_signature`: Train IC=+0.1697, Lock IC=+0.1016, Sharpe=+1.3696
- `combo_rank_max__max_up_ret__directional_volume_signature`: Train IC=+0.1514, Lock IC=+0.0867, Sharpe=+1.2162
- `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Train IC=+0.2156, Lock IC=+0.1112, Sharpe=+1.0666
- `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation`: Train IC=+0.1563, Lock IC=+0.1072, Sharpe=+0.9969

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `half_ratio`: FP is higher (d=+2.02). Threshold 1.413 → 96% accuracy.
- `ic_cv`: FP is higher (d=+1.22). Threshold 0.896 → 89% accuracy.
- `weak_link_cv`: FP is lower (d=-0.85). Threshold 2.084 → 82% accuracy.
- `n_negative_years`: FP is lower (d=-0.74). Threshold 1.500 → 82% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-0.57). Threshold 0.073 → 82% accuracy.
- `recency_ratio`: FP is higher (d=+0.53). Threshold 7.992 → 82% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/4
- Decaying signal (half ratio < 0.3): 0/4
- Weak component (CV > 2.0): 0/4
- Regime-dependent (≥2 negative regimes): 0/4

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_weighted_price_position` | 4 | 7 | 11 | 36% |  |
| `first_bar_return` | 1 | 27 | 28 | 4% |  |
| `max_up_ret` | 3 | 112 | 115 | 3% |  |
| `opening_drive_thrust_ratio` | 1 | 79 | 80 | 1% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 87 | 87 | 0% |  |
| `trend_bar_close_consistency` | 0 | 5 | 5 | 0% |  |
| `bar_ret_0` | 0 | 41 | 41 | 0% |  |
| `yesterday_first_30min_return` | 0 | 7 | 7 | 0% |  |
| `keltner_squeeze_width` | 0 | 4 | 4 | 0% |  |
| `vwap_close_divergence_trend` | 0 | 16 | 16 | 0% |  |
| `body_size_progression` | 0 | 6 | 6 | 0% |  |
| `shaved_bar_trend_conviction` | 0 | 5 | 5 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 37 | 37 | 0% |  |
| `directional_volume_signature` | 0 | 2 | 2 | 0% |  |
| `max_down_ret` | 0 | 26 | 26 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 9 | 9 | 0% |  |
| `early_order_flow_imbalance` | 0 | 8 | 8 | 0% |  |
| `h2_l2_pullback_continuation` | 0 | 10 | 10 | 0% |  |
| `bar_body_rng_0` | 0 | 47 | 47 | 0% |  |
| `volume_price_confirmation` | 0 | 4 | 4 | 0% |  |
| `gap_pct` | 0 | 11 | 11 | 0% |  |
| `trend_day_regime_conviction` | 0 | 4 | 4 | 0% |  |
| `yesterday_early_momentum` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 13 | 13 | 0% |  |
| `limit_down_proximity_early` | 0 | 8 | 8 | 0% |  |
| `early_body_momentum` | 0 | 18 | 18 | 0% |  |
| `late_bar_momentum` | 0 | 2 | 2 | 0% |  |
| `rally_strength_max` | 0 | 5 | 5 | 0% |  |
| `demark_setup_reversal_early` | 0 | 16 | 16 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 5 | 5 | 0% |  |
| `yesterday_early_trend` | 0 | 2 | 2 | 0% |  |
| `net_volume_flow` | 0 | 24 | 24 | 0% |  |
| `close_vs_open_range` | 0 | 18 | 18 | 0% |  |
| `smooth_momentum_structure` | 0 | 5 | 5 | 0% |  |
| `star50_limit_proximity_early` | 0 | 44 | 44 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=3, TP=155, FP rate=2%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=0, TP=33, FP rate=0%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=93, FP rate=1%

