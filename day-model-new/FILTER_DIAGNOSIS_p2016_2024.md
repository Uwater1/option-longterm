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
| 300ETF | single | 62 | 28 | `[4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (28 clusters)]` | 0.2693 | 16 | 19 | 27 | 26% | 0.44 |
| 500ETF | single | 146 | 57 | `[12, 9, 6, 5, 5, 5, 5, 5, 4, 4, 4, 3, ... (57 clusters)]` | 0.2600 | 0 | 20 | 126 | 0% | 0.82 |
| 159915ETF | single | 118 | 40 | `[17, 12, 9, 7, 5, 5, 4, 4, 3, 2, 2, 2, ... (40 clusters)]` | 0.2372 | 1 | 3 | 114 | 1% | 0.90 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=16, TP=27)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_std_across_regimes | 0.040 | 0.053 | 0.039 | 0.052 | -1.08 | 0.077 | 60% |
| half_ratio | 1.302 | 0.992 | 1.320 | 0.968 | +0.79 | 1.375 | 79% |
| ic_cv | 0.844 | 0.753 | 0.834 | 0.766 | +0.74 | 0.874 | 72% |
| recency_ratio | 6.371 | 1.028 | 3.543 | 1.896 | +0.65 | 2.025 | 70% |
| weak_link_cv | 1.031 | 1.222 | 1.106 | 1.067 | -0.59 | 1.086 | 72% |
| n_negative_regimes | 0.000 | 0.074 | 0.000 | 0.000 | -0.40 | 1.000 | 60% |
| n_negative_years | 0.938 | 0.741 | 1.000 | 1.000 | +0.32 | 1.500 | 65% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_rank_max__volume_weighted_price_position__first_bar_sentiment`** (Lock IC=-0.0229, Sharpe=-1.8533)
- Admission: Train IC=+0.1512, Deflated=+0.1511, IR=0.57, Mono=0.70, p=0.0026, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.066 | 2017: +0.023 | 2018: +0.182 | 2019: +0.128 | 2020: -0.024 | 2021: +0.158 | 2022: +0.050 | 2023: +0.156 | 2024: -0.038 | 2025: +0.065 | 2026: -0.154
- Yearly Tail ICs:   2015: +0.048 | 2016: -0.088 | 2017: +0.051 | 2018: +0.393 | 2019: +0.173 | 2020: +0.132 | 2021: +0.242 | 2022: +0.225 | 2023: +0.202 | 2024: -0.110 | 2025: -0.148 | 2026: -0.204
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=0.78, Recency ratio=2.33
- Early IC=+0.0442, Recent IC=+0.1028, 1st-half IC=+0.1101, 2nd-half IC=+0.0861, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.079, Q3_mid=+0.089, Q4=+0.076, Q5_high_vol=+0.105

**`combo_ratio__first_bar_sentiment__volume_weighted_price_position`** (Lock IC=-0.0364, Sharpe=-1.1617)
- Admission: Train IC=+0.1326, Deflated=+0.1330, IR=0.43, Mono=0.66, p=0.0098, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.071 | 2016: +0.044 | 2017: +0.038 | 2018: +0.137 | 2019: +0.148 | 2020: -0.008 | 2021: +0.138 | 2022: +0.020 | 2023: +0.120 | 2024: -0.036 | 2025: +0.017 | 2026: -0.159
- Yearly Tail ICs:   2015: +0.044 | 2016: -0.163 | 2017: +0.113 | 2018: +0.071 | 2019: +0.364 | 2020: +0.033 | 2021: +0.287 | 2022: +0.167 | 2023: +0.149 | 2024: +0.001 | 2025: -0.185 | 2026: -0.356
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=0.68, Recency ratio=1.70
- Early IC=+0.0412, Recent IC=+0.0700, 1st-half IC=+0.0987, 2nd-half IC=+0.0673, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.030, Q3_mid=+0.090, Q4=+0.073, Q5_high_vol=+0.073

**`combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=-0.0158, Sharpe=-1.0471)
- Admission: Train IC=+0.1287, Deflated=+0.1304, IR=0.55, Mono=0.71, p=0.0110, MaxCorr=0.57
- Yearly Linear ICs: 2015: -0.041 | 2016: -0.001 | 2017: +0.004 | 2018: +0.097 | 2019: +0.073 | 2020: +0.010 | 2021: +0.063 | 2022: +0.018 | 2023: +0.047 | 2024: -0.007 | 2025: +0.032 | 2026: -0.133
- Yearly Tail ICs:   2015: +0.075 | 2016: -0.008 | 2017: +0.221 | 2018: +0.166 | 2019: +0.172 | 2020: +0.069 | 2021: +0.225 | 2022: +0.051 | 2023: +0.165 | 2024: +0.013 | 2025: +0.061 | 2026: -0.274
- IC CV=0.88, Neg years (linear/tail)=1/1 of 8, Half ratio=0.77, Recency ratio=20.36
- Early IC=+0.0016, Recent IC=+0.0323, 1st-half IC=+0.0466, 2nd-half IC=+0.0359, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.015, Q3_mid=+0.006, Q4=+0.090, Q5_high_vol=+0.032

**`combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=-0.0066, Sharpe=-0.7138)
- Admission: Train IC=+0.1792, Deflated=+0.1783, IR=0.68, Mono=0.75, p=0.0006, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.087 | 2017: -0.034 | 2018: +0.174 | 2019: +0.091 | 2020: +0.046 | 2021: +0.165 | 2022: +0.025 | 2023: +0.157 | 2024: +0.033 | 2025: +0.055 | 2026: -0.184
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.226 | 2017: +0.015 | 2018: +0.309 | 2019: +0.111 | 2020: +0.093 | 2021: +0.431 | 2022: +0.175 | 2023: +0.139 | 2024: +0.161 | 2025: -0.073 | 2026: -0.389
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=3.44
- Early IC=+0.0264, Recent IC=+0.0908, 1st-half IC=+0.0859, 2nd-half IC=+0.0996, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.087, Q3_mid=+0.081, Q4=+0.039, Q5_high_vol=+0.217

**`net_volume_flow`** (Lock IC=-0.0024, Sharpe=-0.6933)
- Admission: Train IC=+0.1211, Deflated=+0.1204, IR=0.53, Mono=0.70, p=0.0166, MaxCorr=0.85
- Yearly Linear ICs: 2015: -0.008 | 2016: +0.100 | 2017: -0.075 | 2018: +0.093 | 2019: +0.030 | 2020: +0.023 | 2021: +0.166 | 2022: +0.051 | 2023: +0.115 | 2024: +0.040 | 2025: +0.069 | 2026: -0.176
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.175 | 2017: +0.080 | 2018: +0.156 | 2019: +0.123 | 2020: -0.058 | 2021: +0.205 | 2022: +0.150 | 2023: +0.260 | 2024: +0.176 | 2025: +0.010 | 2026: -0.342
- IC CV=1.09, Neg years (linear/tail)=1/1 of 8, Half ratio=2.00, Recency ratio=6.74
- Early IC=+0.0124, Recent IC=+0.0833, 1st-half IC=+0.0439, 2nd-half IC=+0.0877, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.073, Q3_mid=+0.063, Q4=+0.052, Q5_high_vol=+0.128

**`combo_sig_product__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0116, Sharpe=-0.6265)
- Admission: Train IC=+0.1733, Deflated=+0.1741, IR=0.72, Mono=0.76, p=0.0008, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.082 | 2017: +0.012 | 2018: +0.199 | 2019: +0.115 | 2020: -0.026 | 2021: +0.144 | 2022: +0.040 | 2023: +0.132 | 2024: -0.005 | 2025: +0.036 | 2026: -0.093
- Yearly Tail ICs:   2015: -0.013 | 2016: +0.024 | 2017: +0.190 | 2018: +0.251 | 2019: +0.185 | 2020: -0.032 | 2021: +0.360 | 2022: +0.317 | 2023: +0.198 | 2024: +0.067 | 2025: +0.201 | 2026: -0.163
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=0.66, Recency ratio=1.83
- Early IC=+0.0468, Recent IC=+0.0857, 1st-half IC=+0.1056, 2nd-half IC=+0.0696, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.095, Q3_mid=+0.049, Q4=+0.069, Q5_high_vol=+0.111

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0023, Sharpe=-0.5759)
- Admission: Train IC=+0.2524, Deflated=+0.2527, IR=0.86, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.037 | 2017: +0.040 | 2018: +0.154 | 2019: +0.041 | 2020: +0.015 | 2021: +0.191 | 2022: +0.037 | 2023: +0.200 | 2024: +0.042 | 2025: +0.105 | 2026: -0.208
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.160 | 2017: +0.186 | 2018: +0.475 | 2019: +0.255 | 2020: +0.206 | 2021: +0.326 | 2022: +0.202 | 2023: +0.220 | 2024: +0.125 | 2025: +0.154 | 2026: -0.448
- IC CV=0.82, Neg years (linear/tail)=0/0 of 8, Half ratio=1.74, Recency ratio=3.10
- Early IC=+0.0382, Recent IC=+0.1184, 1st-half IC=+0.0644, 2nd-half IC=+0.1117, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.096, Q3_mid=+0.070, Q4=+0.032, Q5_high_vol=+0.169

**`combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0131, Sharpe=-0.5701)
- Admission: Train IC=+0.1892, Deflated=+0.1892, IR=0.71, Mono=0.76, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.087 | 2016: +0.065 | 2017: -0.025 | 2018: +0.158 | 2019: +0.063 | 2020: -0.011 | 2021: +0.164 | 2022: +0.069 | 2023: +0.192 | 2024: +0.010 | 2025: +0.095 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.097 | 2017: +0.128 | 2018: +0.352 | 2019: +0.151 | 2020: +0.030 | 2021: +0.404 | 2022: +0.227 | 2023: +0.218 | 2024: +0.175 | 2025: +0.194 | 2026: -0.148
- IC CV=0.90, Neg years (linear/tail)=2/0 of 8, Half ratio=1.54, Recency ratio=6.91
- Early IC=+0.0188, Recent IC=+0.1298, 1st-half IC=+0.0700, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.104, Q3_mid=+0.062, Q4=+0.036, Q5_high_vol=+0.196

**`early_order_flow_imbalance`** (Lock IC=-0.0189, Sharpe=-0.4041)
- Admission: Train IC=+0.1648, Deflated=+0.1646, IR=0.62, Mono=0.71, p=0.0012, MaxCorr=0.71
- Yearly Linear ICs: 2015: -0.032 | 2016: +0.074 | 2017: -0.067 | 2018: +0.082 | 2019: +0.048 | 2020: -0.019 | 2021: +0.147 | 2022: +0.098 | 2023: +0.111 | 2024: -0.001 | 2025: +0.076 | 2026: -0.202
- Yearly Tail ICs:   2015: -0.115 | 2016: +0.147 | 2017: +0.009 | 2018: +0.142 | 2019: +0.189 | 2020: -0.092 | 2021: +0.406 | 2022: +0.190 | 2023: +0.100 | 2024: +0.087 | 2025: +0.113 | 2026: -0.121
- IC CV=1.12, Neg years (linear/tail)=2/1 of 8, Half ratio=2.03, Recency ratio=31.17
- Early IC=+0.0033, Recent IC=+0.1041, 1st-half IC=+0.0422, 2nd-half IC=+0.0855, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.094, Q3_mid=+0.096, Q4=+0.088, Q5_high_vol=+0.045

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=-0.0166, Sharpe=-0.3738)
- Admission: Train IC=+0.1276, Deflated=+0.1271, IR=0.37, Mono=0.66, p=0.0126, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.100 | 2017: -0.021 | 2018: +0.168 | 2019: +0.104 | 2020: +0.008 | 2021: +0.171 | 2022: +0.042 | 2023: +0.202 | 2024: -0.015 | 2025: +0.054 | 2026: -0.140
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.188 | 2017: -0.132 | 2018: +0.339 | 2019: +0.146 | 2020: +0.048 | 2021: +0.256 | 2022: +0.262 | 2023: +0.429 | 2024: +0.028 | 2025: +0.147 | 2026: -0.238
- IC CV=0.79, Neg years (linear/tail)=1/1 of 8, Half ratio=1.03, Recency ratio=3.12
- Early IC=+0.0392, Recent IC=+0.1223, 1st-half IC=+0.1016, 2nd-half IC=+0.1044, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.83, neg years=1)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.104, Q3_mid=+0.082, Q4=+0.062, Q5_high_vol=+0.179

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0138, Sharpe=-0.3231)
- Admission: Train IC=+0.2116, Deflated=+0.2119, IR=0.83, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.92, Neg years (linear/tail)=0/0 of 8, Half ratio=1.93, Recency ratio=5.15
- Early IC=+0.0224, Recent IC=+0.1153, 1st-half IC=+0.0549, 2nd-half IC=+0.1063, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.091, Q3_mid=+0.035, Q4=+0.029, Q5_high_vol=+0.178

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0025, Sharpe=-0.2562)
- Admission: Train IC=+0.1930, Deflated=+0.1935, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.086 | 2016: +0.111 | 2017: -0.010 | 2018: +0.159 | 2019: +0.087 | 2020: +0.031 | 2021: +0.116 | 2022: +0.060 | 2023: +0.150 | 2024: +0.008 | 2025: +0.033 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.024 | 2016: +0.269 | 2017: +0.115 | 2018: +0.144 | 2019: +0.207 | 2020: +0.036 | 2021: +0.142 | 2022: +0.323 | 2023: +0.340 | 2024: +0.052 | 2025: +0.111 | 2026: -0.046
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=0.89, Recency ratio=2.08
- Early IC=+0.0505, Recent IC=+0.1049, 1st-half IC=+0.0967, 2nd-half IC=+0.0864, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89, neg years=1)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.090, Q3_mid=+0.044, Q4=+0.083, Q5_high_vol=+0.131

**`always_in_trend_persistence`** (Lock IC=-0.0421, Sharpe=-0.1859)
- Admission: Train IC=+0.1369, Deflated=+0.1365, IR=0.47, Mono=0.69, p=0.0072, MaxCorr=0.91
- Yearly Linear ICs: 2015: -0.030 | 2016: +0.075 | 2017: -0.026 | 2018: +0.074 | 2019: +0.026 | 2020: -0.016 | 2021: +0.128 | 2022: +0.110 | 2023: +0.093 | 2024: -0.004 | 2025: +0.051 | 2026: -0.260
- Yearly Tail ICs:   2015: -0.155 | 2016: +0.144 | 2017: -0.007 | 2018: +0.037 | 2019: +0.136 | 2020: +0.071 | 2021: +0.219 | 2022: +0.282 | 2023: +0.054 | 2024: +0.187 | 2025: +0.191 | 2026: -0.267
- IC CV=0.92, Neg years (linear/tail)=2/1 of 8, Half ratio=1.78, Recency ratio=4.11
- Early IC=+0.0247, Recent IC=+0.1014, 1st-half IC=+0.0448, 2nd-half IC=+0.0797, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.060, Q3_mid=+0.092, Q4=+0.119, Q5_high_vol=+0.047

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0018, Sharpe=+0.1999)
- Admission: Train IC=+0.2395, Deflated=+0.2396, IR=0.78, Mono=0.79, p=0.0000, MaxCorr=0.59
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.055 | 2017: +0.003 | 2018: +0.171 | 2019: +0.049 | 2020: +0.002 | 2021: +0.181 | 2022: +0.049 | 2023: +0.189 | 2024: +0.027 | 2025: +0.112 | 2026: -0.185
- Yearly Tail ICs:   2015: +0.041 | 2016: +0.202 | 2017: +0.144 | 2018: +0.377 | 2019: +0.178 | 2020: +0.068 | 2021: +0.365 | 2022: +0.360 | 2023: +0.364 | 2024: +0.065 | 2025: +0.068 | 2026: +0.020
- IC CV=0.85, Neg years (linear/tail)=0/0 of 8, Half ratio=1.48, Recency ratio=4.09
- Early IC=+0.0292, Recent IC=+0.1194, 1st-half IC=+0.0738, 2nd-half IC=+0.1092, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.107, Q3_mid=+0.062, Q4=+0.041, Q5_high_vol=+0.169

**`max_up_ret`** (Lock IC=-0.0047, Sharpe=+0.3486)
- Admission: Train IC=+0.1850, Deflated=+0.1850, IR=0.46, Mono=0.67, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.084 | 2017: -0.040 | 2018: +0.136 | 2019: +0.049 | 2020: +0.048 | 2021: +0.166 | 2022: +0.013 | 2023: +0.149 | 2024: +0.056 | 2025: +0.033 | 2026: -0.152
- Yearly Tail ICs:   2015: +0.070 | 2016: +0.035 | 2017: +0.015 | 2018: +0.265 | 2019: +0.208 | 2020: +0.110 | 2021: +0.462 | 2022: +0.221 | 2023: +0.279 | 2024: +0.213 | 2025: -0.013 | 2026: -0.315
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.65, Recency ratio=3.65
- Early IC=+0.0221, Recent IC=+0.0807, 1st-half IC=+0.0577, 2nd-half IC=+0.0951, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.073, Q3_mid=+0.045, Q4=+0.045, Q5_high_vol=+0.168

**`combo_max__bar_ret_0__first_bar_sentiment`** (Lock IC=-0.0050, Sharpe=+0.4800)
- Admission: Train IC=+0.1804, Deflated=+0.1804, IR=0.44, Mono=0.66, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.089 | 2016: +0.075 | 2017: +0.020 | 2018: +0.192 | 2019: +0.106 | 2020: +0.020 | 2021: +0.111 | 2022: +0.047 | 2023: +0.159 | 2024: -0.007 | 2025: +0.057 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.049 | 2017: +0.027 | 2018: +0.407 | 2019: +0.169 | 2020: +0.253 | 2021: +0.091 | 2022: +0.196 | 2023: +0.266 | 2024: +0.118 | 2025: +0.146 | 2026: -0.287
- IC CV=0.65, Neg years (linear/tail)=0/1 of 8, Half ratio=0.72, Recency ratio=2.17
- Early IC=+0.0475, Recent IC=+0.1032, 1st-half IC=+0.1112, 2nd-half IC=+0.0799, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.69, neg years=1)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.081, Q3_mid=+0.092, Q4=+0.071, Q5_high_vol=+0.131

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0273, Sharpe=+0.1690)
- Admission: Train IC=+0.1678, Deflated=+0.1664, IR=0.44, Mono=0.66, p=0.0016, MaxCorr=0.53
- Yearly Linear ICs: 2015: +0.047 | 2016: +0.053 | 2017: +0.103 | 2018: +0.108 | 2019: +0.010 | 2020: +0.088 | 2021: +0.048 | 2022: +0.028 | 2023: +0.071 | 2024: -0.053 | 2025: -0.030 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.000 | 2016: +0.193 | 2017: -0.004 | 2018: +0.270 | 2019: +0.043 | 2020: +0.052 | 2021: +0.168 | 2022: +0.246 | 2023: +0.195 | 2024: +0.053 | 2025: +0.098 | 2026: -0.157
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.75, Recency ratio=0.64
- Early IC=+0.0779, Recent IC=+0.0497, 1st-half IC=+0.0798, 2nd-half IC=+0.0599, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=-0.003, Q3_mid=+0.061, Q4=+0.073, Q5_high_vol=+0.070

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0427, Sharpe=-0.6213)
- Admission: Train IC=+0.1940, Deflated=+0.1933, IR=0.59, Mono=0.73, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.080 | 2016: +0.032 | 2017: -0.035 | 2018: +0.148 | 2019: +0.098 | 2020: +0.038 | 2021: +0.151 | 2022: +0.081 | 2023: +0.091 | 2024: -0.025 | 2025: +0.075 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.071 | 2017: -0.129 | 2018: +0.310 | 2019: +0.210 | 2020: +0.133 | 2021: +0.496 | 2022: +0.331 | 2023: +0.173 | 2024: +0.023 | 2025: +0.006 | 2026: +0.025
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=1.27, Recency ratio=-59.25
- Early IC=-0.0014, Recent IC=+0.0858, 1st-half IC=+0.0736, 2nd-half IC=+0.0938, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.020, Q2=+0.045, Q3_mid=+0.083, Q4=+0.049, Q5_high_vol=+0.188

**`combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0374, Sharpe=-0.6001)
- Admission: Train IC=+0.1557, Deflated=+0.1559, IR=0.49, Mono=0.66, p=0.0022, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.094 | 2016: -0.001 | 2017: -0.034 | 2018: +0.106 | 2019: +0.065 | 2020: +0.039 | 2021: +0.118 | 2022: +0.070 | 2023: +0.098 | 2024: +0.001 | 2025: +0.021 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.038 | 2016: +0.035 | 2017: -0.070 | 2018: +0.220 | 2019: +0.223 | 2020: +0.125 | 2021: +0.319 | 2022: +0.273 | 2023: +0.173 | 2024: +0.162 | 2025: -0.034 | 2026: -0.070
- IC CV=0.87, Neg years (linear/tail)=2/1 of 8, Half ratio=2.34, Recency ratio=-4.74
- Early IC=-0.0178, Recent IC=+0.0842, 1st-half IC=+0.0363, 2nd-half IC=+0.0850, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=-0.019, Q2=+0.005, Q3_mid=+0.059, Q4=+0.058, Q5_high_vol=+0.176

**`combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0340, Sharpe=-0.1960)
- Admission: Train IC=+0.2515, Deflated=+0.2511, IR=0.68, Mono=0.77, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.054 | 2017: -0.066 | 2018: +0.211 | 2019: +0.121 | 2020: +0.055 | 2021: +0.171 | 2022: +0.028 | 2023: +0.136 | 2024: +0.052 | 2025: +0.045 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.162 | 2017: +0.013 | 2018: +0.364 | 2019: +0.365 | 2020: +0.131 | 2021: +0.515 | 2022: +0.271 | 2023: +0.129 | 2024: +0.260 | 2025: -0.079 | 2026: +0.260
- IC CV=0.93, Neg years (linear/tail)=1/0 of 8, Half ratio=1.02, Recency ratio=-14.03
- Early IC=-0.0058, Recent IC=+0.0819, 1st-half IC=+0.0965, 2nd-half IC=+0.0988, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.050, Q3_mid=+0.127, Q4=+0.050, Q5_high_vol=+0.212

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0306, Sharpe=-0.3020)
- Admission: Train IC=+0.1915, Deflated=+0.1915, IR=0.63, Mono=0.74, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.100 | 2017: +0.028 | 2018: +0.154 | 2019: -0.002 | 2020: +0.057 | 2021: +0.147 | 2022: +0.069 | 2023: +0.088 | 2024: +0.030 | 2025: +0.032 | 2026: +0.025
- Yearly Tail ICs:   2015: -0.095 | 2016: +0.135 | 2017: -0.009 | 2018: +0.490 | 2019: +0.119 | 2020: +0.055 | 2021: +0.273 | 2022: +0.370 | 2023: +0.136 | 2024: +0.118 | 2025: -0.048 | 2026: -0.051
- IC CV=0.63, Neg years (linear/tail)=1/1 of 8, Half ratio=1.41, Recency ratio=1.24
- Early IC=+0.0637, Recent IC=+0.0787, 1st-half IC=+0.0660, 2nd-half IC=+0.0929, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.058, Q3_mid=+0.020, Q4=+0.037, Q5_high_vol=+0.190

**`bar_body_rng_0`** (Lock IC=+0.0301, Sharpe=-0.1439)
- Admission: Train IC=+0.1976, Deflated=+0.1979, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.107 | 2017: +0.047 | 2018: +0.192 | 2019: +0.077 | 2020: -0.009 | 2021: +0.155 | 2022: +0.035 | 2023: +0.153 | 2024: +0.041 | 2025: +0.072 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.081 | 2016: +0.174 | 2017: +0.052 | 2018: +0.365 | 2019: +0.131 | 2020: -0.020 | 2021: +0.383 | 2022: +0.249 | 2023: +0.339 | 2024: +0.122 | 2025: +0.057 | 2026: -0.139
- IC CV=0.68, Neg years (linear/tail)=1/1 of 8, Half ratio=0.73, Recency ratio=1.22
- Early IC=+0.0771, Recent IC=+0.0942, 1st-half IC=+0.1130, 2nd-half IC=+0.0826, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.073, Q3_mid=+0.082, Q4=+0.057, Q5_high_vol=+0.157

**`combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`** (Lock IC=+0.0288, Sharpe=-0.2338)
- Admission: Train IC=+0.1591, Deflated=+0.1593, IR=0.48, Mono=0.69, p=0.0016, MaxCorr=0.64
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.086 | 2017: +0.035 | 2018: +0.110 | 2019: +0.038 | 2020: -0.014 | 2021: +0.179 | 2022: +0.091 | 2023: +0.059 | 2024: -0.063 | 2025: +0.068 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.201 | 2016: +0.171 | 2017: +0.155 | 2018: +0.354 | 2019: +0.021 | 2020: -0.099 | 2021: +0.264 | 2022: +0.124 | 2023: +0.129 | 2024: +0.017 | 2025: +0.105 | 2026: +0.319
- IC CV=0.74, Neg years (linear/tail)=1/1 of 8, Half ratio=1.21, Recency ratio=1.24
- Early IC=+0.0603, Recent IC=+0.0749, 1st-half IC=+0.0709, 2nd-half IC=+0.0854, Neg regimes=0/5
- Weak component: `first_bar_volume` (CV=2.19)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.034, Q3_mid=+0.028, Q4=+0.012, Q5_high_vol=+0.163

**`combo_rel_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0225, Sharpe=-0.2686)
- Admission: Train IC=+0.1449, Deflated=+0.1449, IR=0.48, Mono=0.68, p=0.0040, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.085 | 2016: +0.074 | 2017: +0.016 | 2018: +0.181 | 2019: +0.039 | 2020: +0.032 | 2021: +0.150 | 2022: +0.004 | 2023: +0.175 | 2024: +0.109 | 2025: +0.015 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.091 | 2016: +0.099 | 2017: +0.224 | 2018: +0.312 | 2019: +0.163 | 2020: +0.008 | 2021: +0.178 | 2022: +0.074 | 2023: +0.232 | 2024: +0.083 | 2025: -0.094 | 2026: -0.100
- IC CV=0.82, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=2.01
- Early IC=+0.0446, Recent IC=+0.0895, 1st-half IC=+0.0780, 2nd-half IC=+0.0892, Neg regimes=0/5
- Weak component: `early_vwap_acceleration` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.028, Q2=+0.115, Q3_mid=+0.090, Q4=+0.015, Q5_high_vol=+0.168

**`combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0222, Sharpe=-0.2736)
- Admission: Train IC=+0.2176, Deflated=+0.2173, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.098 | 2017: -0.003 | 2018: +0.221 | 2019: +0.077 | 2020: +0.007 | 2021: +0.166 | 2022: +0.036 | 2023: +0.152 | 2024: +0.039 | 2025: +0.071 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.034 | 2016: +0.182 | 2017: -0.104 | 2018: +0.330 | 2019: +0.176 | 2020: +0.076 | 2021: +0.474 | 2022: +0.096 | 2023: +0.285 | 2024: +0.027 | 2025: +0.121 | 2026: -0.130
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=0.83, Recency ratio=1.99
- Early IC=+0.0470, Recent IC=+0.0936, 1st-half IC=+0.1075, 2nd-half IC=+0.0889, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.83)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.088, Q3_mid=+0.074, Q4=+0.034, Q5_high_vol=+0.214

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0183, Sharpe=-0.0646)
- Admission: Train IC=+0.2075, Deflated=+0.2076, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.096 | 2017: +0.026 | 2018: +0.191 | 2019: +0.080 | 2020: +0.017 | 2021: +0.173 | 2022: +0.028 | 2023: +0.172 | 2024: +0.060 | 2025: +0.054 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.029 | 2016: +0.135 | 2017: +0.081 | 2018: +0.301 | 2019: +0.156 | 2020: +0.051 | 2021: +0.302 | 2022: +0.235 | 2023: +0.406 | 2024: +0.180 | 2025: -0.003 | 2026: -0.073
- IC CV=0.69, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=1.64
- Early IC=+0.0613, Recent IC=+0.1003, 1st-half IC=+0.1020, 2nd-half IC=+0.0975, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.082, Q3_mid=+0.070, Q4=+0.049, Q5_high_vol=+0.183

**`combo_rank_min__volume_weighted_price_position__first_bar_sentiment`** (Lock IC=+0.0132, Sharpe=-0.6477)
- Admission: Train IC=+0.1196, Deflated=+0.1201, IR=0.40, Mono=0.67, p=0.0172, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.093 | 2017: -0.015 | 2018: +0.173 | 2019: +0.069 | 2020: -0.022 | 2021: +0.113 | 2022: +0.067 | 2023: +0.139 | 2024: -0.030 | 2025: +0.098 | 2026: -0.042
- Yearly Tail ICs:   2015: -0.066 | 2016: +0.136 | 2017: +0.087 | 2018: +0.116 | 2019: +0.068 | 2020: -0.113 | 2021: +0.191 | 2022: +0.349 | 2023: +0.210 | 2024: +0.055 | 2025: +0.412 | 2026: +0.093
- IC CV=0.83, Neg years (linear/tail)=2/1 of 8, Half ratio=0.82, Recency ratio=2.66
- Early IC=+0.0387, Recent IC=+0.1031, 1st-half IC=+0.0901, 2nd-half IC=+0.0735, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.090, Q2=+0.116, Q3_mid=+0.049, Q4=+0.052, Q5_high_vol=+0.104

**`combo_min__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=+0.0125, Sharpe=-0.4568)
- Admission: Train IC=+0.2167, Deflated=+0.2162, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.082 | 2016: +0.041 | 2017: +0.013 | 2018: +0.223 | 2019: +0.067 | 2020: -0.005 | 2021: +0.179 | 2022: +0.036 | 2023: +0.173 | 2024: -0.004 | 2025: +0.122 | 2026: -0.141
- Yearly Tail ICs:   2015: +0.021 | 2016: +0.086 | 2017: -0.052 | 2018: +0.218 | 2019: +0.300 | 2020: +0.064 | 2021: +0.472 | 2022: +0.317 | 2023: +0.459 | 2024: -0.102 | 2025: +0.110 | 2026: +0.014
- IC CV=0.90, Neg years (linear/tail)=1/1 of 8, Half ratio=1.06, Recency ratio=3.88
- Early IC=+0.0268, Recent IC=+0.1041, 1st-half IC=+0.0910, 2nd-half IC=+0.0961, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.123, Q3_mid=+0.112, Q4=+0.036, Q5_high_vol=+0.147

**`combo_mean__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0123, Sharpe=-0.4689)
- Admission: Train IC=+0.2003, Deflated=+0.2006, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.075 | 2017: +0.044 | 2018: +0.210 | 2019: +0.072 | 2020: -0.038 | 2021: +0.160 | 2022: +0.063 | 2023: +0.180 | 2024: +0.003 | 2025: +0.107 | 2026: -0.124
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.002 | 2017: +0.171 | 2018: +0.416 | 2019: +0.146 | 2020: -0.022 | 2021: +0.326 | 2022: +0.323 | 2023: +0.412 | 2024: +0.065 | 2025: +0.179 | 2026: -0.062
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=0.86, Recency ratio=2.06
- Early IC=+0.0591, Recent IC=+0.1219, 1st-half IC=+0.1076, 2nd-half IC=+0.0927, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.110, Q3_mid=+0.084, Q4=+0.054, Q5_high_vol=+0.141

**`combo_rank_max__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0117, Sharpe=-0.3080)
- Admission: Train IC=+0.1835, Deflated=+0.1832, IR=0.44, Mono=0.69, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.046 | 2018: +0.125 | 2019: +0.050 | 2020: +0.040 | 2021: +0.174 | 2022: +0.018 | 2023: +0.171 | 2024: +0.046 | 2025: +0.077 | 2026: -0.148
- Yearly Tail ICs:   2015: -0.034 | 2016: +0.068 | 2017: -0.092 | 2018: +0.289 | 2019: +0.241 | 2020: +0.096 | 2021: +0.371 | 2022: +0.246 | 2023: +0.229 | 2024: +0.159 | 2025: +0.084 | 2026: -0.332
- IC CV=0.93, Neg years (linear/tail)=1/1 of 8, Half ratio=1.76, Recency ratio=5.15
- Early IC=+0.0187, Recent IC=+0.0963, 1st-half IC=+0.0574, 2nd-half IC=+0.1008, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.093, Q3_mid=+0.053, Q4=+0.035, Q5_high_vol=+0.173

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0084, Sharpe=-0.0883)
- Admission: Train IC=+0.2468, Deflated=+0.2470, IR=0.64, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.090 | 2017: +0.022 | 2018: +0.184 | 2019: +0.074 | 2020: -0.002 | 2021: +0.132 | 2022: +0.046 | 2023: +0.172 | 2024: +0.054 | 2025: +0.022 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.099 | 2017: +0.155 | 2018: +0.376 | 2019: +0.260 | 2020: +0.079 | 2021: +0.374 | 2022: +0.167 | 2023: +0.386 | 2024: +0.235 | 2025: -0.045 | 2026: -0.015
- IC CV=0.71, Neg years (linear/tail)=1/0 of 8, Half ratio=0.87, Recency ratio=1.96
- Early IC=+0.0557, Recent IC=+0.1089, 1st-half IC=+0.0990, 2nd-half IC=+0.0858, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.081, Q3_mid=+0.062, Q4=+0.059, Q5_high_vol=+0.168

**`combo_rank_max__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0069, Sharpe=-0.3876)
- Admission: Train IC=+0.1743, Deflated=+0.1744, IR=0.69, Mono=0.73, p=0.0008, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.074 | 2017: +0.071 | 2018: +0.189 | 2019: +0.057 | 2020: -0.032 | 2021: +0.165 | 2022: +0.060 | 2023: +0.183 | 2024: +0.008 | 2025: +0.110 | 2026: -0.148
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.156 | 2017: +0.221 | 2018: +0.426 | 2019: +0.146 | 2020: -0.046 | 2021: +0.354 | 2022: +0.215 | 2023: +0.229 | 2024: +0.145 | 2025: +0.176 | 2026: -0.270
- IC CV=0.76, Neg years (linear/tail)=1/1 of 8, Half ratio=0.92, Recency ratio=1.72
- Early IC=+0.0708, Recent IC=+0.1217, 1st-half IC=+0.1005, 2nd-half IC=+0.0925, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.098, Q3_mid=+0.100, Q4=+0.041, Q5_high_vol=+0.128

**`combo_mean__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0067, Sharpe=-0.2911)
- Admission: Train IC=+0.2419, Deflated=+0.2414, IR=0.75, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.080 | 2017: -0.034 | 2018: +0.160 | 2019: +0.073 | 2020: +0.052 | 2021: +0.175 | 2022: +0.015 | 2023: +0.161 | 2024: +0.063 | 2025: +0.057 | 2026: -0.167
- Yearly Tail ICs:   2015: -0.026 | 2016: +0.171 | 2017: +0.150 | 2018: +0.341 | 2019: +0.360 | 2020: +0.126 | 2021: +0.367 | 2022: +0.210 | 2023: +0.247 | 2024: +0.288 | 2025: -0.129 | 2026: -0.337
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.37, Recency ratio=3.88
- Early IC=+0.0226, Recent IC=+0.0878, 1st-half IC=+0.0731, 2nd-half IC=+0.0999, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.089, Q3_mid=+0.069, Q4=+0.037, Q5_high_vol=+0.195

**`opening_drive_thrust_ratio`** (Lock IC=+0.0060, Sharpe=-0.4547)
- Admission: Train IC=+0.1783, Deflated=+0.1775, IR=0.54, Mono=0.72, p=0.0006, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.039 | 2018: +0.176 | 2019: +0.078 | 2020: +0.042 | 2021: +0.170 | 2022: +0.024 | 2023: +0.166 | 2024: +0.033 | 2025: +0.069 | 2026: -0.151
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.178 | 2017: -0.121 | 2018: +0.326 | 2019: +0.224 | 2020: +0.117 | 2021: +0.389 | 2022: +0.169 | 2023: +0.259 | 2024: +0.120 | 2025: +0.073 | 2026: -0.040
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=1.21, Recency ratio=4.07
- Early IC=+0.0233, Recent IC=+0.0951, 1st-half IC=+0.0830, 2nd-half IC=+0.1001, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.097, Q3_mid=+0.086, Q4=+0.032, Q5_high_vol=+0.209

**`combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0045, Sharpe=-0.5240)
- Admission: Train IC=+0.2226, Deflated=+0.2227, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.072 | 2017: +0.064 | 2018: +0.200 | 2019: +0.058 | 2020: -0.012 | 2021: +0.169 | 2022: +0.057 | 2023: +0.180 | 2024: +0.011 | 2025: +0.100 | 2026: -0.151
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.029 | 2017: +0.158 | 2018: +0.512 | 2019: +0.200 | 2020: +0.228 | 2021: +0.345 | 2022: +0.234 | 2023: +0.228 | 2024: +0.108 | 2025: +0.190 | 2026: -0.322
- IC CV=0.71, Neg years (linear/tail)=1/1 of 8, Half ratio=0.94, Recency ratio=1.74
- Early IC=+0.0683, Recent IC=+0.1186, 1st-half IC=+0.1027, 2nd-half IC=+0.0962, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.096, Q3_mid=+0.091, Q4=+0.050, Q5_high_vol=+0.144

**`combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0022, Sharpe=-0.4646)
- Admission: Train IC=+0.1776, Deflated=+0.1774, IR=0.53, Mono=0.72, p=0.0006, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.108 | 2017: -0.035 | 2018: +0.191 | 2019: +0.109 | 2020: +0.020 | 2021: +0.166 | 2022: +0.044 | 2023: +0.166 | 2024: +0.004 | 2025: +0.071 | 2026: -0.123
- Yearly Tail ICs:   2015: -0.007 | 2016: +0.140 | 2017: -0.092 | 2018: +0.343 | 2019: +0.246 | 2020: +0.113 | 2021: +0.389 | 2022: +0.182 | 2023: +0.259 | 2024: +0.120 | 2025: +0.091 | 2026: -0.040
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=0.95, Recency ratio=2.88
- Early IC=+0.0365, Recent IC=+0.1050, 1st-half IC=+0.1036, 2nd-half IC=+0.0980, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.83)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.098, Q3_mid=+0.082, Q4=+0.056, Q5_high_vol=+0.182

### 500ETF — `single` Median Features

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1236, Sharpe=-0.0797)
- Admission: Train IC=+0.1311, Deflated=+0.1301, IR=0.42, Mono=0.67, p=0.0096, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.030 | 2017: +0.203 | 2018: +0.097 | 2019: +0.089 | 2020: +0.098 | 2021: +0.071 | 2022: +0.088 | 2023: +0.108 | 2024: +0.127 | 2025: +0.125 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.027 | 2017: +0.254 | 2018: +0.168 | 2019: +0.201 | 2020: +0.133 | 2021: +0.054 | 2022: +0.099 | 2023: +0.046 | 2024: +0.083 | 2025: -0.005 | 2026: -0.056
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.84
- Early IC=+0.1165, Recent IC=+0.0980, 1st-half IC=+0.1021, 2nd-half IC=+0.0899, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.223, Q2=-0.003, Q3_mid=+0.110, Q4=+0.091, Q5_high_vol=+0.110

**`combo_sig_product__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.1148, Sharpe=-0.0882)
- Admission: Train IC=+0.1747, Deflated=+0.1744, IR=0.40, Mono=0.66, p=0.0002, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.052 | 2017: +0.232 | 2018: +0.062 | 2019: +0.076 | 2020: +0.101 | 2021: +0.081 | 2022: +0.076 | 2023: +0.077 | 2024: +0.154 | 2025: +0.078 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.142 | 2016: +0.004 | 2017: +0.239 | 2018: +0.111 | 2019: +0.168 | 2020: +0.216 | 2021: +0.089 | 2022: +0.055 | 2023: +0.219 | 2024: +0.218 | 2025: -0.026 | 2026: +0.031
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.54
- Early IC=+0.1421, Recent IC=+0.0766, 1st-half IC=+0.1015, 2nd-half IC=+0.0857, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.036, Q3_mid=+0.100, Q4=+0.073, Q5_high_vol=+0.092

**`combo_mean__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0937, Sharpe=-0.2836)
- Admission: Train IC=+0.2499, Deflated=+0.2494, IR=1.00, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.102 | 2017: +0.236 | 2018: +0.226 | 2019: +0.130 | 2020: +0.163 | 2021: +0.146 | 2022: +0.086 | 2023: +0.114 | 2024: +0.163 | 2025: +0.083 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.245 | 2017: +0.332 | 2018: +0.430 | 2019: +0.216 | 2020: +0.190 | 2021: +0.310 | 2022: +0.217 | 2023: +0.153 | 2024: +0.247 | 2025: -0.208 | 2026: -0.289
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.59
- Early IC=+0.1686, Recent IC=+0.1003, 1st-half IC=+0.1668, 2nd-half IC=+0.1321, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.009, Q3_mid=+0.144, Q4=+0.150, Q5_high_vol=+0.231

**`combo_max__net_volume_flow__max_down_ret`** (Lock IC=+0.0913, Sharpe=-0.1427)
- Admission: Train IC=+0.1624, Deflated=+0.1621, IR=0.55, Mono=0.71, p=0.0020, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.079 | 2017: +0.203 | 2018: +0.168 | 2019: +0.102 | 2020: +0.108 | 2021: +0.072 | 2022: +0.071 | 2023: +0.047 | 2024: +0.143 | 2025: +0.132 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.329 | 2016: +0.146 | 2017: +0.165 | 2018: +0.139 | 2019: +0.177 | 2020: -0.003 | 2021: +0.233 | 2022: +0.224 | 2023: +0.309 | 2024: +0.292 | 2025: +0.041 | 2026: -0.122
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.42
- Early IC=+0.1413, Recent IC=+0.0591, 1st-half IC=+0.1336, 2nd-half IC=+0.0714, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.041, Q3_mid=+0.099, Q4=+0.125, Q5_high_vol=+0.121

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0880, Sharpe=-0.3280)
- Admission: Train IC=+0.2231, Deflated=+0.2228, IR=0.60, Mono=0.74, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.108 | 2017: +0.193 | 2018: +0.220 | 2019: +0.126 | 2020: +0.108 | 2021: +0.167 | 2022: +0.095 | 2023: +0.088 | 2024: +0.134 | 2025: +0.072 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.504 | 2016: +0.114 | 2017: +0.109 | 2018: +0.317 | 2019: +0.321 | 2020: +0.122 | 2021: +0.267 | 2022: +0.324 | 2023: +0.075 | 2024: +0.084 | 2025: +0.119 | 2026: +0.022
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.61
- Early IC=+0.1505, Recent IC=+0.0918, 1st-half IC=+0.1596, 2nd-half IC=+0.1141, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.221, Q2=-0.023, Q3_mid=+0.131, Q4=+0.185, Q5_high_vol=+0.166

**`combo_mean__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0857, Sharpe=-0.2639)
- Admission: Train IC=+0.2240, Deflated=+0.2233, IR=0.80, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.066 | 2017: +0.200 | 2018: +0.167 | 2019: +0.100 | 2020: +0.141 | 2021: +0.114 | 2022: +0.103 | 2023: +0.102 | 2024: +0.144 | 2025: +0.114 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.406 | 2016: +0.275 | 2017: +0.320 | 2018: +0.207 | 2019: +0.228 | 2020: +0.213 | 2021: +0.217 | 2022: +0.257 | 2023: +0.262 | 2024: +0.234 | 2025: +0.002 | 2026: -0.102
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.77
- Early IC=+0.1331, Recent IC=+0.1028, 1st-half IC=+0.1333, 2nd-half IC=+0.1152, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.009, Q3_mid=+0.143, Q4=+0.132, Q5_high_vol=+0.174

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0836, Sharpe=-0.0273)
- Admission: Train IC=+0.2227, Deflated=+0.2225, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.085 | 2017: +0.205 | 2018: +0.250 | 2019: +0.155 | 2020: +0.120 | 2021: +0.089 | 2022: +0.055 | 2023: +0.059 | 2024: +0.109 | 2025: +0.100 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.168 | 2017: +0.351 | 2018: +0.314 | 2019: +0.237 | 2020: +0.201 | 2021: +0.357 | 2022: +0.284 | 2023: +0.165 | 2024: +0.165 | 2025: +0.070 | 2026: -0.178
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.40
- Early IC=+0.1445, Recent IC=+0.0579, 1st-half IC=+0.1747, 2nd-half IC=+0.0797, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.155, Q2=-0.038, Q3_mid=+0.127, Q4=+0.171, Q5_high_vol=+0.166

**`combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=+0.0835, Sharpe=-0.1410)
- Admission: Train IC=+0.1873, Deflated=+0.1876, IR=0.65, Mono=0.74, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.130 | 2017: +0.183 | 2018: +0.188 | 2019: +0.116 | 2020: +0.111 | 2021: +0.074 | 2022: +0.066 | 2023: +0.063 | 2024: +0.084 | 2025: +0.139 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.365 | 2016: +0.180 | 2017: +0.358 | 2018: +0.151 | 2019: +0.248 | 2020: +0.140 | 2021: +0.053 | 2022: +0.295 | 2023: +0.066 | 2024: +0.057 | 2025: +0.131 | 2026: -0.433
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.41
- Early IC=+0.1566, Recent IC=+0.0646, 1st-half IC=+0.1528, 2nd-half IC=+0.0788, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.027, Q3_mid=+0.084, Q4=+0.178, Q5_high_vol=+0.148

**`combo_rank_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0742, Sharpe=-0.0921)
- Admission: Train IC=+0.2644, Deflated=+0.2653, IR=0.81, Mono=0.77, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.148 | 2017: +0.146 | 2018: +0.232 | 2019: +0.124 | 2020: +0.121 | 2021: +0.095 | 2022: +0.065 | 2023: +0.058 | 2024: +0.102 | 2025: +0.125 | 2026: -0.026
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.202 | 2017: +0.372 | 2018: +0.527 | 2019: +0.070 | 2020: +0.250 | 2021: +0.008 | 2022: +0.268 | 2023: -0.001 | 2024: +0.153 | 2025: +0.160 | 2026: -0.223
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.52, Recency ratio=0.42
- Early IC=+0.1471, Recent IC=+0.0611, 1st-half IC=+0.1610, 2nd-half IC=+0.0843, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.147, Q2=-0.014, Q3_mid=+0.105, Q4=+0.173, Q5_high_vol=+0.155

**`combo_min__max_up_ret__early_body_momentum`** (Lock IC=+0.0739, Sharpe=-0.4096)
- Admission: Train IC=+0.1929, Deflated=+0.1925, IR=0.50, Mono=0.69, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.136 | 2016: +0.080 | 2017: +0.176 | 2018: +0.128 | 2019: +0.077 | 2020: +0.102 | 2021: +0.126 | 2022: +0.127 | 2023: +0.121 | 2024: +0.124 | 2025: +0.134 | 2026: -0.097
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.201 | 2017: +0.176 | 2018: +0.277 | 2019: +0.108 | 2020: +0.220 | 2021: +0.216 | 2022: +0.144 | 2023: +0.191 | 2024: +0.205 | 2025: -0.012 | 2026: -0.165
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.97
- Early IC=+0.1279, Recent IC=+0.1244, 1st-half IC=+0.1063, 2nd-half IC=+0.1181, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.011, Q3_mid=+0.129, Q4=+0.108, Q5_high_vol=+0.134

**`vwap_trend_channel_slope`** (Lock IC=+0.0712, Sharpe=-0.3626)
- Admission: Train IC=+0.1436, Deflated=+0.1423, IR=0.46, Mono=0.65, p=0.0058, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.90
- Early IC=+0.1028, Recent IC=+0.0926, 1st-half IC=+0.0798, 2nd-half IC=+0.0888, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.007, Q3_mid=+0.088, Q4=+0.063, Q5_high_vol=+0.120

**`combo_rel_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0684, Sharpe=-0.4386)
- Admission: Train IC=+0.2365, Deflated=+0.2371, IR=0.85, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.331 | 2016: +0.118 | 2017: +0.179 | 2018: +0.204 | 2019: +0.128 | 2020: +0.123 | 2021: +0.137 | 2022: +0.042 | 2023: +0.077 | 2024: +0.087 | 2025: +0.022 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.081 | 2017: +0.414 | 2018: +0.371 | 2019: +0.380 | 2020: +0.089 | 2021: +0.234 | 2022: +0.117 | 2023: +0.170 | 2024: -0.063 | 2025: -0.052 | 2026: +0.019
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.40
- Early IC=+0.1482, Recent IC=+0.0594, 1st-half IC=+0.1500, 2nd-half IC=+0.0942, Neg regimes=1/5
- Weak component: `early_late_momentum_divergence` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.028, Q3_mid=+0.061, Q4=+0.163, Q5_high_vol=+0.197

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0668, Sharpe=-0.1367)
- Admission: Train IC=+0.1967, Deflated=+0.1957, IR=0.45, Mono=0.67, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.032 | 2017: +0.181 | 2018: +0.191 | 2019: +0.121 | 2020: +0.172 | 2021: +0.149 | 2022: +0.101 | 2023: +0.083 | 2024: +0.120 | 2025: +0.096 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.005 | 2016: +0.132 | 2017: +0.257 | 2018: +0.474 | 2019: +0.214 | 2020: +0.178 | 2021: +0.253 | 2022: +0.053 | 2023: +0.137 | 2024: +0.134 | 2025: -0.103 | 2026: -0.359
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.86
- Early IC=+0.1063, Recent IC=+0.0919, 1st-half IC=+0.1270, 2nd-half IC=+0.1340, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.012, Q3_mid=+0.181, Q4=+0.131, Q5_high_vol=+0.188

**`early_body_momentum`** (Lock IC=+0.0648, Sharpe=-0.2198)
- Admission: Train IC=+0.1903, Deflated=+0.1899, IR=0.40, Mono=0.67, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.056 | 2017: +0.120 | 2018: +0.113 | 2019: +0.038 | 2020: +0.083 | 2021: +0.046 | 2022: +0.118 | 2023: +0.087 | 2024: +0.107 | 2025: +0.135 | 2026: -0.099
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.133 | 2017: +0.081 | 2018: +0.142 | 2019: +0.132 | 2020: +0.274 | 2021: +0.217 | 2022: +0.118 | 2023: +0.118 | 2024: +0.211 | 2025: +0.009 | 2026: -0.159
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=1.16
- Early IC=+0.0883, Recent IC=+0.1024, 1st-half IC=+0.0835, 2nd-half IC=+0.0826, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.150, Q2=-0.009, Q3_mid=+0.098, Q4=+0.096, Q5_high_vol=+0.098

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0640, Sharpe=-0.0373)
- Admission: Train IC=+0.2468, Deflated=+0.2475, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.150 | 2017: +0.182 | 2018: +0.240 | 2019: +0.135 | 2020: +0.137 | 2021: +0.083 | 2022: +0.102 | 2023: +0.072 | 2024: +0.083 | 2025: +0.097 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.302 | 2017: +0.378 | 2018: +0.505 | 2019: +0.129 | 2020: +0.123 | 2021: +0.004 | 2022: +0.124 | 2023: +0.117 | 2024: +0.064 | 2025: -0.049 | 2026: -0.277
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.53
- Early IC=+0.1656, Recent IC=+0.0874, 1st-half IC=+0.1702, 2nd-half IC=+0.1039, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.026, Q3_mid=+0.098, Q4=+0.195, Q5_high_vol=+0.190

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0586, Sharpe=-0.0789)
- Admission: Train IC=+0.2446, Deflated=+0.2452, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.125 | 2017: +0.154 | 2018: +0.226 | 2019: +0.083 | 2020: +0.134 | 2021: +0.102 | 2022: +0.108 | 2023: +0.080 | 2024: +0.126 | 2025: +0.122 | 2026: -0.123
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.099 | 2017: +0.215 | 2018: +0.264 | 2019: +0.075 | 2020: +0.348 | 2021: +0.179 | 2022: +0.303 | 2023: +0.395 | 2024: +0.216 | 2025: -0.102 | 2026: -0.544
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.67
- Early IC=+0.1414, Recent IC=+0.0945, 1st-half IC=+0.1449, 2nd-half IC=+0.1071, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.012, Q3_mid=+0.126, Q4=+0.163, Q5_high_vol=+0.157

**`combo_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0581, Sharpe=-0.3703)
- Admission: Train IC=+0.2326, Deflated=+0.2332, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.108 | 2017: +0.151 | 2018: +0.225 | 2019: +0.084 | 2020: +0.127 | 2021: +0.095 | 2022: +0.109 | 2023: +0.070 | 2024: +0.117 | 2025: +0.126 | 2026: -0.120
- Yearly Tail ICs:   2015: +0.118 | 2016: +0.107 | 2017: +0.197 | 2018: +0.276 | 2019: +0.103 | 2020: +0.345 | 2021: +0.202 | 2022: +0.241 | 2023: +0.409 | 2024: +0.182 | 2025: -0.123 | 2026: -0.557
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.69
- Early IC=+0.1296, Recent IC=+0.0892, 1st-half IC=+0.1393, 2nd-half IC=+0.1031, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.162, Q2=-0.013, Q3_mid=+0.122, Q4=+0.157, Q5_high_vol=+0.152

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0540, Sharpe=-0.2136)
- Admission: Train IC=+0.1886, Deflated=+0.1880, IR=0.51, Mono=0.67, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.087 | 2017: +0.207 | 2018: +0.148 | 2019: +0.106 | 2020: +0.167 | 2021: +0.053 | 2022: +0.113 | 2023: +0.130 | 2024: +0.095 | 2025: +0.086 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.386 | 2016: +0.147 | 2017: +0.347 | 2018: +0.235 | 2019: +0.179 | 2020: +0.141 | 2021: +0.176 | 2022: +0.055 | 2023: +0.102 | 2024: +0.232 | 2025: -0.029 | 2026: +0.006
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.83
- Early IC=+0.1467, Recent IC=+0.1215, 1st-half IC=+0.1354, 2nd-half IC=+0.1186, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.182, Q2=-0.001, Q3_mid=+0.157, Q4=+0.124, Q5_high_vol=+0.160

**`early_order_flow_imbalance`** (Lock IC=+0.0431, Sharpe=-0.4332)
- Admission: Train IC=+0.1856, Deflated=+0.1850, IR=0.41, Mono=0.67, p=0.0002, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.093 | 2016: -0.043 | 2017: +0.093 | 2018: +0.101 | 2019: +0.121 | 2020: +0.038 | 2021: +0.122 | 2022: +0.141 | 2023: +0.079 | 2024: +0.107 | 2025: +0.091 | 2026: -0.135
- Yearly Tail ICs:   2015: +0.234 | 2016: -0.073 | 2017: +0.091 | 2018: +0.296 | 2019: +0.233 | 2020: +0.049 | 2021: +0.226 | 2022: +0.337 | 2023: +0.131 | 2024: +0.366 | 2025: +0.046 | 2026: -0.113
- IC CV=0.68, Neg years (linear/tail)=1/1 of 8, Half ratio=1.29, Recency ratio=4.35
- Early IC=+0.0252, Recent IC=+0.1098, 1st-half IC=+0.0726, 2nd-half IC=+0.0939, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.037, Q3_mid=+0.071, Q4=+0.109, Q5_high_vol=+0.099

**`combo_diff__bar_ret_0__max_down_ret`** (Lock IC=+0.0120, Sharpe=-0.8026)
- Admission: Train IC=+0.1682, Deflated=+0.1692, IR=0.40, Mono=0.66, p=0.0008, MaxCorr=0.48
- Yearly Linear ICs: 2015: -0.046 | 2016: +0.147 | 2017: +0.004 | 2018: +0.205 | 2019: +0.060 | 2020: +0.043 | 2021: +0.065 | 2022: +0.004 | 2023: +0.029 | 2024: +0.003 | 2025: +0.052 | 2026: -0.020
- Yearly Tail ICs:   2015: -0.114 | 2016: +0.052 | 2017: +0.039 | 2018: +0.403 | 2019: +0.107 | 2020: +0.168 | 2021: +0.077 | 2022: +0.146 | 2023: +0.158 | 2024: +0.036 | 2025: -0.006 | 2026: +0.061
- IC CV=0.95, Neg years (linear/tail)=0/0 of 8, Half ratio=0.34, Recency ratio=0.22
- Early IC=+0.0753, Recent IC=+0.0168, 1st-half IC=+0.1043, 2nd-half IC=+0.0355, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.030, Q3_mid=+0.011, Q4=+0.102, Q5_high_vol=+0.127

### 159915ETF — `single` Median Features

**`net_volume_flow`** (Lock IC=+0.0976, Sharpe=-0.0344)
- Admission: Train IC=+0.1831, Deflated=+0.1824, IR=0.60, Mono=0.72, p=0.0008, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.053 | 2017: -0.019 | 2018: +0.036 | 2019: +0.116 | 2020: +0.049 | 2021: +0.139 | 2022: +0.063 | 2023: +0.165 | 2024: +0.072 | 2025: +0.205 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.110 | 2017: +0.061 | 2018: +0.026 | 2019: +0.301 | 2020: +0.192 | 2021: -0.005 | 2022: +0.332 | 2023: +0.452 | 2024: +0.160 | 2025: +0.185 | 2026: -0.324
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=2.23, Recency ratio=6.70
- Early IC=+0.0170, Recent IC=+0.1140, 1st-half IC=+0.0477, 2nd-half IC=+0.1061, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.108, Q3_mid=+0.091, Q4=+0.039, Q5_high_vol=+0.107

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0922, Sharpe=-0.0879)
- Admission: Train IC=+0.2568, Deflated=+0.2560, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.105 | 2017: +0.006 | 2018: +0.129 | 2019: +0.198 | 2020: +0.115 | 2021: +0.134 | 2022: +0.106 | 2023: +0.200 | 2024: +0.078 | 2025: +0.167 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.373 | 2016: -0.016 | 2017: +0.072 | 2018: +0.330 | 2019: +0.449 | 2020: +0.204 | 2021: +0.343 | 2022: +0.207 | 2023: +0.598 | 2024: +0.145 | 2025: +0.217 | 2026: +0.008
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=1.26, Recency ratio=2.77
- Early IC=+0.0552, Recent IC=+0.1527, 1st-half IC=+0.1075, 2nd-half IC=+0.1354, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.069, Q2=+0.152, Q3_mid=+0.099, Q4=+0.113, Q5_high_vol=+0.162

**`combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0677, Sharpe=-0.1117)
- Admission: Train IC=+0.2096, Deflated=+0.2089, IR=0.65, Mono=0.72, p=0.0002, MaxCorr=0.67
- Yearly Linear ICs: 2015: +0.072 | 2016: +0.055 | 2017: +0.020 | 2018: +0.035 | 2019: +0.139 | 2020: +0.033 | 2021: +0.160 | 2022: +0.086 | 2023: +0.142 | 2024: +0.096 | 2025: +0.111 | 2026: -0.055
- Yearly Tail ICs:   2015: -0.014 | 2016: +0.181 | 2017: +0.163 | 2018: +0.002 | 2019: +0.316 | 2020: +0.279 | 2021: +0.072 | 2022: +0.359 | 2023: +0.334 | 2024: +0.215 | 2025: +0.153 | 2026: -0.269
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=1.66, Recency ratio=3.03
- Early IC=+0.0375, Recent IC=+0.1138, 1st-half IC=+0.0649, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.132, Q3_mid=+0.124, Q4=+0.101, Q5_high_vol=+0.058

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0334, Sharpe=+0.9753)
- Admission: Train IC=+0.2155, Deflated=+0.2160, IR=0.44, Mono=0.65, p=0.0000, MaxCorr=0.89
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

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0572, Sharpe=+0.6639)
- Admission: Train IC=+0.1812, Deflated=+0.1812, IR=0.50, Mono=0.68, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.062 | 2017: -0.040 | 2018: +0.162 | 2019: +0.137 | 2020: +0.018 | 2021: +0.125 | 2022: +0.028 | 2023: +0.138 | 2024: +0.029 | 2025: +0.098 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.063 | 2017: -0.116 | 2018: +0.316 | 2019: +0.221 | 2020: +0.182 | 2021: +0.260 | 2022: +0.151 | 2023: +0.231 | 2024: +0.255 | 2025: +0.090 | 2026: +0.262
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=0.74, Recency ratio=7.30
- Early IC=+0.0114, Recent IC=+0.0830, 1st-half IC=+0.0993, 2nd-half IC=+0.0738, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.043, Q3_mid=+0.077, Q4=+0.040, Q5_high_vol=+0.173

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`** (Lock IC=+0.0530, Sharpe=+0.6589)
- Admission: Train IC=+0.1458, Deflated=+0.1458, IR=0.41, Mono=0.66, p=0.0040, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.093 | 2017: -0.004 | 2018: +0.124 | 2019: +0.048 | 2020: -0.020 | 2021: +0.135 | 2022: +0.076 | 2023: +0.056 | 2024: -0.011 | 2025: +0.082 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.192 | 2017: +0.175 | 2018: +0.368 | 2019: +0.076 | 2020: -0.147 | 2021: +0.276 | 2022: +0.078 | 2023: +0.091 | 2024: +0.204 | 2025: +0.165 | 2026: +0.199
- IC CV=0.82, Neg years (linear/tail)=2/1 of 8, Half ratio=0.96, Recency ratio=1.47
- Early IC=+0.0448, Recent IC=+0.0660, 1st-half IC=+0.0735, 2nd-half IC=+0.0703, Neg regimes=0/5
- Weak component: `first_bar_volume` (CV=2.19)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.056, Q3_mid=+0.028, Q4=+0.004, Q5_high_vol=+0.160

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0512, Sharpe=+0.6322)
- Admission: Train IC=+0.2502, Deflated=+0.2509, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.88
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

**`combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0317, Sharpe=+0.5329)
- Admission: Train IC=+0.2067, Deflated=+0.2064, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.107 | 2017: -0.070 | 2018: +0.204 | 2019: +0.089 | 2020: +0.068 | 2021: +0.149 | 2022: +0.082 | 2023: +0.109 | 2024: +0.028 | 2025: +0.054 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.196 | 2017: -0.044 | 2018: +0.437 | 2019: +0.318 | 2020: +0.066 | 2021: +0.338 | 2022: +0.240 | 2023: +0.050 | 2024: +0.207 | 2025: +0.098 | 2026: +0.150
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=1.12, Recency ratio=5.24
- Early IC=+0.0183, Recent IC=+0.0958, 1st-half IC=+0.0936, 2nd-half IC=+0.1046, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.001, Q2=+0.074, Q3_mid=+0.076, Q4=+0.050, Q5_high_vol=+0.241

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0270, Sharpe=+0.5172)
- Admission: Train IC=+0.2350, Deflated=+0.2352, IR=0.60, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.110 | 2017: -0.075 | 2018: +0.168 | 2019: +0.086 | 2020: +0.075 | 2021: +0.151 | 2022: +0.094 | 2023: +0.092 | 2024: +0.026 | 2025: +0.042 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.224 | 2017: -0.034 | 2018: +0.419 | 2019: +0.209 | 2020: +0.180 | 2021: +0.391 | 2022: +0.271 | 2023: +0.157 | 2024: +0.194 | 2025: +0.121 | 2026: +0.197
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=1.27, Recency ratio=5.19
- Early IC=+0.0179, Recent IC=+0.0928, 1st-half IC=+0.0827, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.062, Q3_mid=+0.059, Q4=+0.049, Q5_high_vol=+0.223

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.0215, Sharpe=+0.5132)
- Admission: Train IC=+0.1925, Deflated=+0.1925, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.102 | 2017: -0.058 | 2018: +0.199 | 2019: +0.108 | 2020: +0.025 | 2021: +0.163 | 2022: +0.052 | 2023: +0.166 | 2024: +0.062 | 2025: +0.063 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.139 | 2016: +0.070 | 2017: -0.016 | 2018: +0.240 | 2019: +0.248 | 2020: +0.087 | 2021: +0.364 | 2022: +0.227 | 2023: +0.333 | 2024: +0.266 | 2025: +0.021 | 2026: -0.003
- IC CV=0.84, Neg years (linear/tail)=1/1 of 8, Half ratio=0.97, Recency ratio=5.06
- Early IC=+0.0215, Recent IC=+0.1090, 1st-half IC=+0.1025, 2nd-half IC=+0.0992, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.071, Q3_mid=+0.099, Q4=+0.054, Q5_high_vol=+0.184

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0254, Sharpe=+0.4883)
- Admission: Train IC=+0.2251, Deflated=+0.2250, IR=0.49, Mono=0.65, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.093 | 2017: -0.048 | 2018: +0.184 | 2019: +0.102 | 2020: +0.020 | 2021: +0.173 | 2022: +0.059 | 2023: +0.171 | 2024: +0.056 | 2025: +0.067 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.078 | 2017: -0.022 | 2018: +0.230 | 2019: +0.266 | 2020: +0.036 | 2021: +0.419 | 2022: +0.401 | 2023: +0.231 | 2024: +0.293 | 2025: +0.071 | 2026: -0.049
- IC CV=0.81, Neg years (linear/tail)=1/1 of 8, Half ratio=1.11, Recency ratio=5.15
- Early IC=+0.0224, Recent IC=+0.1152, 1st-half IC=+0.0950, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.073, Q3_mid=+0.095, Q4=+0.045, Q5_high_vol=+0.190

**`combo_rank_min__bar_ret_0__first_bar_sentiment`** (Lock IC=+0.0112, Sharpe=+0.4878)
- Admission: Train IC=+0.1450, Deflated=+0.1456, IR=0.44, Mono=0.67, p=0.0040, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.078 | 2016: +0.115 | 2017: +0.042 | 2018: +0.176 | 2019: +0.069 | 2020: +0.027 | 2021: +0.125 | 2022: +0.039 | 2023: +0.127 | 2024: +0.016 | 2025: +0.053 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.133 | 2017: +0.002 | 2018: +0.279 | 2019: +0.063 | 2020: +0.145 | 2021: +0.121 | 2022: +0.337 | 2023: +0.272 | 2024: +0.142 | 2025: +0.188 | 2026: -0.104
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=1.05
- Early IC=+0.0786, Recent IC=+0.0829, 1st-half IC=+0.1046, 2nd-half IC=+0.0766, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.077, Q3_mid=+0.051, Q4=+0.073, Q5_high_vol=+0.117

**`combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.0449, Sharpe=+0.4220)
- Admission: Train IC=+0.1702, Deflated=+0.1694, IR=0.59, Mono=0.72, p=0.0010, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.060 | 2017: -0.078 | 2018: +0.158 | 2019: +0.108 | 2020: +0.050 | 2021: +0.142 | 2022: +0.041 | 2023: +0.108 | 2024: +0.035 | 2025: +0.062 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.191 | 2016: +0.083 | 2017: -0.170 | 2018: +0.357 | 2019: +0.430 | 2020: +0.129 | 2021: +0.309 | 2022: +0.261 | 2023: +0.033 | 2024: +0.334 | 2025: -0.024 | 2026: +0.265
- IC CV=0.97, Neg years (linear/tail)=1/1 of 8, Half ratio=1.04, Recency ratio=-6.10
- Early IC=-0.0123, Recent IC=+0.0748, 1st-half IC=+0.0820, 2nd-half IC=+0.0853, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=-0.023, Q2=+0.053, Q3_mid=+0.103, Q4=+0.039, Q5_high_vol=+0.182

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0449, Sharpe=+0.4220)
- Admission: Train IC=+0.1702, Deflated=+0.1694, IR=0.59, Mono=0.72, p=0.0010, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.060 | 2017: -0.078 | 2018: +0.158 | 2019: +0.108 | 2020: +0.050 | 2021: +0.142 | 2022: +0.041 | 2023: +0.108 | 2024: +0.035 | 2025: +0.062 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.191 | 2016: +0.083 | 2017: -0.170 | 2018: +0.357 | 2019: +0.430 | 2020: +0.129 | 2021: +0.309 | 2022: +0.261 | 2023: +0.033 | 2024: +0.334 | 2025: -0.024 | 2026: +0.265
- IC CV=0.97, Neg years (linear/tail)=1/1 of 8, Half ratio=1.04, Recency ratio=-6.11
- Early IC=-0.0122, Recent IC=+0.0748, 1st-half IC=+0.0820, 2nd-half IC=+0.0853, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=-0.023, Q2=+0.053, Q3_mid=+0.103, Q4=+0.039, Q5_high_vol=+0.182

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0266, Sharpe=+0.3866)
- Admission: Train IC=+0.1778, Deflated=+0.1777, IR=0.44, Mono=0.66, p=0.0006, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.067 | 2017: +0.029 | 2018: +0.190 | 2019: +0.043 | 2020: +0.046 | 2021: +0.168 | 2022: +0.020 | 2023: +0.162 | 2024: +0.112 | 2025: +0.021 | 2026: -0.089
- Yearly Tail ICs:   2015: +0.238 | 2016: +0.141 | 2017: +0.176 | 2018: +0.478 | 2019: +0.146 | 2020: +0.065 | 2021: +0.253 | 2022: +0.131 | 2023: +0.279 | 2024: +0.174 | 2025: -0.002 | 2026: -0.169
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.90
- Early IC=+0.0482, Recent IC=+0.0914, 1st-half IC=+0.0810, 2nd-half IC=+0.1000, Neg regimes=0/5
- Weak component: `early_vwap_acceleration` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.118, Q3_mid=+0.085, Q4=+0.022, Q5_high_vol=+0.197

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0329, Sharpe=+0.3820)
- Admission: Train IC=+0.2034, Deflated=+0.2038, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.121 | 2017: -0.013 | 2018: +0.219 | 2019: +0.089 | 2020: +0.057 | 2021: +0.162 | 2022: +0.072 | 2023: +0.123 | 2024: +0.029 | 2025: +0.072 | 2026: -0.028
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.153 | 2017: +0.031 | 2018: +0.329 | 2019: +0.149 | 2020: +0.103 | 2021: +0.398 | 2022: +0.268 | 2023: +0.135 | 2024: +0.169 | 2025: +0.090 | 2026: +0.115
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=0.94, Recency ratio=1.81
- Early IC=+0.0537, Recent IC=+0.0973, 1st-half IC=+0.1123, 2nd-half IC=+0.1053, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.073, Q3_mid=+0.063, Q4=+0.054, Q5_high_vol=+0.230

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0362, Sharpe=+0.3660)
- Admission: Train IC=+0.2341, Deflated=+0.2347, IR=0.59, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.108 | 2017: +0.017 | 2018: +0.217 | 2019: +0.106 | 2020: +0.040 | 2021: +0.142 | 2022: +0.073 | 2023: +0.129 | 2024: +0.014 | 2025: +0.084 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.046 | 2017: -0.002 | 2018: +0.302 | 2019: +0.175 | 2020: +0.236 | 2021: +0.451 | 2022: +0.307 | 2023: +0.233 | 2024: +0.102 | 2025: +0.150 | 2026: +0.042
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=1.61
- Early IC=+0.0626, Recent IC=+0.1009, 1st-half IC=+0.1241, 2nd-half IC=+0.0951, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.060, Q3_mid=+0.078, Q4=+0.074, Q5_high_vol=+0.197

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0000, Sharpe=+0.3515)
- Admission: Train IC=+0.1850, Deflated=+0.1847, IR=0.54, Mono=0.68, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.055 | 2017: +0.003 | 2018: +0.171 | 2019: +0.097 | 2020: +0.036 | 2021: +0.191 | 2022: +0.020 | 2023: +0.150 | 2024: +0.035 | 2025: +0.038 | 2026: -0.130
- Yearly Tail ICs:   2015: +0.070 | 2016: +0.035 | 2017: -0.018 | 2018: +0.269 | 2019: +0.208 | 2020: +0.110 | 2021: +0.462 | 2022: +0.221 | 2023: +0.315 | 2024: +0.207 | 2025: -0.033 | 2026: -0.315
- IC CV=0.76, Neg years (linear/tail)=0/1 of 8, Half ratio=1.14, Recency ratio=2.94
- Early IC=+0.0289, Recent IC=+0.0848, 1st-half IC=+0.0876, 2nd-half IC=+0.1002, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.082, Q3_mid=+0.077, Q4=+0.048, Q5_high_vol=+0.165

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0134, Sharpe=+0.2457)
- Admission: Train IC=+0.2224, Deflated=+0.2225, IR=0.64, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.087 | 2017: +0.035 | 2018: +0.169 | 2019: +0.060 | 2020: +0.041 | 2021: +0.170 | 2022: +0.015 | 2023: +0.166 | 2024: +0.060 | 2025: +0.078 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.033 | 2017: +0.026 | 2018: +0.412 | 2019: +0.206 | 2020: +0.193 | 2021: +0.360 | 2022: +0.306 | 2023: +0.290 | 2024: +0.141 | 2025: +0.095 | 2026: -0.308
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=1.20, Recency ratio=1.53
- Early IC=+0.0595, Recent IC=+0.0910, 1st-half IC=+0.0833, 2nd-half IC=+0.1002, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.075, Q3_mid=+0.067, Q4=+0.048, Q5_high_vol=+0.166

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0351, Sharpe=+0.1736)
- Admission: Train IC=+0.2509, Deflated=+0.2505, IR=0.74, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.87, Neg years (linear/tail)=1/0 of 8, Half ratio=1.13, Recency ratio=-40.14
- Early IC=-0.0023, Recent IC=+0.0922, 1st-half IC=+0.0952, 2nd-half IC=+0.1073, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.067, Q3_mid=+0.129, Q4=+0.053, Q5_high_vol=+0.214

**`combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0203, Sharpe=+0.1467)
- Admission: Train IC=+0.1476, Deflated=+0.1485, IR=0.55, Mono=0.69, p=0.0036, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.063 | 2016: +0.069 | 2017: +0.020 | 2018: +0.106 | 2019: +0.044 | 2020: -0.005 | 2021: +0.076 | 2022: +0.030 | 2023: +0.076 | 2024: +0.045 | 2025: +0.055 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.049 | 2017: +0.187 | 2018: +0.194 | 2019: -0.114 | 2020: +0.061 | 2021: +0.154 | 2022: +0.311 | 2023: +0.140 | 2024: +0.253 | 2025: +0.331 | 2026: -0.221
- IC CV=0.65, Neg years (linear/tail)=1/1 of 8, Half ratio=0.64, Recency ratio=1.19
- Early IC=+0.0444, Recent IC=+0.0529, 1st-half IC=+0.0638, 2nd-half IC=+0.0406, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.001, Q3_mid=+0.037, Q4=+0.067, Q5_high_vol=+0.060

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0124, Sharpe=+0.1247)
- Admission: Train IC=+0.2167, Deflated=+0.2167, IR=0.71, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.075 | 2017: +0.048 | 2018: +0.173 | 2019: +0.064 | 2020: +0.032 | 2021: +0.176 | 2022: +0.011 | 2023: +0.163 | 2024: +0.060 | 2025: +0.077 | 2026: -0.156
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.085 | 2017: +0.044 | 2018: +0.383 | 2019: +0.230 | 2020: +0.137 | 2021: +0.433 | 2022: +0.238 | 2023: +0.346 | 2024: +0.122 | 2025: +0.070 | 2026: -0.295
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.40
- Early IC=+0.0619, Recent IC=+0.0867, 1st-half IC=+0.0843, 2nd-half IC=+0.0956, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.076, Q3_mid=+0.063, Q4=+0.046, Q5_high_vol=+0.162

**`combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0225, Sharpe=+0.1191)
- Admission: Train IC=+0.1643, Deflated=+0.1641, IR=0.57, Mono=0.68, p=0.0012, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.082 | 2017: -0.068 | 2018: +0.131 | 2019: +0.030 | 2020: +0.046 | 2021: +0.142 | 2022: +0.084 | 2023: +0.087 | 2024: +0.029 | 2025: +0.022 | 2026: +0.041
- Yearly Tail ICs:   2015: -0.154 | 2016: +0.140 | 2017: +0.068 | 2018: +0.295 | 2019: +0.117 | 2020: +0.037 | 2021: +0.285 | 2022: +0.339 | 2023: +0.054 | 2024: +0.121 | 2025: -0.096 | 2026: -0.003
- IC CV=0.90, Neg years (linear/tail)=1/0 of 8, Half ratio=1.82, Recency ratio=8.85
- Early IC=+0.0096, Recent IC=+0.0853, 1st-half IC=+0.0506, 2nd-half IC=+0.0923, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.031, Q2=+0.047, Q3_mid=+0.030, Q4=+0.050, Q5_high_vol=+0.191

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0166, Sharpe=+0.1134)
- Admission: Train IC=+0.1917, Deflated=+0.1921, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.127 | 2016: +0.091 | 2017: +0.052 | 2018: +0.209 | 2019: +0.100 | 2020: +0.002 | 2021: +0.137 | 2022: +0.043 | 2023: +0.139 | 2024: +0.035 | 2025: +0.046 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.177 | 2016: -0.008 | 2017: +0.013 | 2018: +0.278 | 2019: +0.193 | 2020: +0.190 | 2021: +0.332 | 2022: +0.265 | 2023: +0.338 | 2024: +0.096 | 2025: +0.052 | 2026: +0.028
- IC CV=0.63, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=1.27
- Early IC=+0.0715, Recent IC=+0.0909, 1st-half IC=+0.1182, 2nd-half IC=+0.0770, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.071, Q3_mid=+0.076, Q4=+0.068, Q5_high_vol=+0.154

**`combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0094, Sharpe=+0.1080)
- Admission: Train IC=+0.2493, Deflated=+0.2494, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.107 | 2016: +0.081 | 2017: +0.041 | 2018: +0.222 | 2019: +0.065 | 2020: -0.027 | 2021: +0.145 | 2022: +0.066 | 2023: +0.176 | 2024: +0.015 | 2025: +0.076 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.053 | 2016: -0.023 | 2017: +0.226 | 2018: +0.296 | 2019: +0.286 | 2020: +0.061 | 2021: +0.427 | 2022: +0.327 | 2023: +0.379 | 2024: +0.066 | 2025: -0.056 | 2026: -0.157
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=0.82, Recency ratio=1.96
- Early IC=+0.0614, Recent IC=+0.1207, 1st-half IC=+0.1105, 2nd-half IC=+0.0905, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.112, Q3_mid=+0.086, Q4=+0.060, Q5_high_vol=+0.149

**`combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0012, Sharpe=+0.0941)
- Admission: Train IC=+0.1982, Deflated=+0.1987, IR=0.47, Mono=0.67, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.127 | 2016: +0.076 | 2017: -0.016 | 2018: +0.197 | 2019: +0.080 | 2020: -0.005 | 2021: +0.168 | 2022: +0.040 | 2023: +0.175 | 2024: +0.013 | 2025: +0.068 | 2026: -0.116
- Yearly Tail ICs:   2015: +0.075 | 2016: +0.058 | 2017: -0.154 | 2018: +0.357 | 2019: +0.180 | 2020: +0.044 | 2021: +0.395 | 2022: +0.208 | 2023: +0.398 | 2024: +0.157 | 2025: +0.090 | 2026: -0.068
- IC CV=0.87, Neg years (linear/tail)=2/1 of 8, Half ratio=1.05, Recency ratio=3.58
- Early IC=+0.0299, Recent IC=+0.1072, 1st-half IC=+0.0918, 2nd-half IC=+0.0967, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.107, Q3_mid=+0.059, Q4=+0.057, Q5_high_vol=+0.158

**`combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0512, Sharpe=+0.0639)
- Admission: Train IC=+0.1797, Deflated=+0.1800, IR=0.55, Mono=0.74, p=0.0006, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.130 | 2016: +0.150 | 2017: +0.018 | 2018: +0.179 | 2019: +0.012 | 2020: +0.042 | 2021: +0.143 | 2022: +0.080 | 2023: +0.070 | 2024: +0.033 | 2025: +0.033 | 2026: +0.097
- Yearly Tail ICs:   2015: -0.090 | 2016: +0.135 | 2017: -0.015 | 2018: +0.316 | 2019: +0.073 | 2020: +0.075 | 2021: +0.239 | 2022: +0.373 | 2023: +0.048 | 2024: +0.202 | 2025: +0.008 | 2026: +0.023
- IC CV=0.68, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=0.89
- Early IC=+0.0843, Recent IC=+0.0752, 1st-half IC=+0.1009, 2nd-half IC=+0.0859, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.090, Q2=+0.060, Q3_mid=+0.045, Q4=+0.040, Q5_high_vol=+0.185

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0354, Sharpe=+0.0566)
- Admission: Train IC=+0.2637, Deflated=+0.2645, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.100 | 2017: +0.002 | 2018: +0.184 | 2019: +0.115 | 2020: +0.044 | 2021: +0.132 | 2022: +0.035 | 2023: +0.166 | 2024: +0.057 | 2025: +0.050 | 2026: -0.026
- Yearly Tail ICs:   2015: +0.352 | 2016: +0.169 | 2017: +0.098 | 2018: +0.339 | 2019: +0.260 | 2020: +0.238 | 2021: +0.493 | 2022: +0.143 | 2023: +0.300 | 2024: +0.247 | 2025: -0.054 | 2026: +0.161
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=1.97
- Early IC=+0.0510, Recent IC=+0.1006, 1st-half IC=+0.1082, 2nd-half IC=+0.0906, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.065, Q3_mid=+0.079, Q4=+0.053, Q5_high_vol=+0.194

### 500ETF — `single` True Positives

**`combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1246, Sharpe=+1.3362)
- Admission: Train IC=+0.2317, Deflated=+0.2320, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.065 | 2017: +0.225 | 2018: +0.087 | 2019: +0.108 | 2020: +0.121 | 2021: +0.098 | 2022: +0.042 | 2023: +0.099 | 2024: +0.139 | 2025: +0.131 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.168 | 2017: +0.279 | 2018: +0.269 | 2019: +0.303 | 2020: +0.277 | 2021: +0.193 | 2022: +0.116 | 2023: +0.216 | 2024: +0.236 | 2025: +0.068 | 2026: +0.194
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.48
- Early IC=+0.1466, Recent IC=+0.0706, 1st-half IC=+0.1180, 2nd-half IC=+0.0881, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.026, Q3_mid=+0.104, Q4=+0.100, Q5_high_vol=+0.122

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0934, Sharpe=+1.2539)
- Admission: Train IC=+0.1884, Deflated=+0.1888, IR=0.64, Mono=0.72, p=0.0002, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.264 | 2016: +0.095 | 2017: +0.149 | 2018: +0.192 | 2019: +0.092 | 2020: +0.099 | 2021: +0.119 | 2022: +0.084 | 2023: +0.002 | 2024: +0.129 | 2025: +0.092 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.433 | 2016: +0.169 | 2017: +0.281 | 2018: +0.473 | 2019: +0.076 | 2020: +0.111 | 2021: +0.367 | 2022: +0.073 | 2023: +0.040 | 2024: +0.169 | 2025: +0.224 | 2026: +0.367
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.35
- Early IC=+0.1222, Recent IC=+0.0433, 1st-half IC=+0.1276, 2nd-half IC=+0.0817, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.001, Q3_mid=+0.038, Q4=+0.083, Q5_high_vol=+0.213

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

**`combo_rank_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1418, Sharpe=+1.1539)
- Admission: Train IC=+0.1568, Deflated=+0.1564, IR=0.44, Mono=0.65, p=0.0030, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.057 | 2017: +0.230 | 2018: +0.093 | 2019: +0.123 | 2020: +0.133 | 2021: +0.031 | 2022: +0.096 | 2023: +0.036 | 2024: +0.139 | 2025: +0.111 | 2026: +0.152
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.065 | 2017: +0.185 | 2018: +0.151 | 2019: +0.343 | 2020: +0.164 | 2021: +0.294 | 2022: +0.113 | 2023: +0.030 | 2024: +0.178 | 2025: +0.302 | 2026: +0.147
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.46
- Early IC=+0.1435, Recent IC=+0.0667, 1st-half IC=+0.1211, 2nd-half IC=+0.0735, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.015, Q3_mid=+0.096, Q4=+0.114, Q5_high_vol=+0.123

**`combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1170, Sharpe=+1.0936)
- Admission: Train IC=+0.2313, Deflated=+0.2314, IR=0.60, Mono=0.71, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.071 | 2017: +0.223 | 2018: +0.155 | 2019: +0.131 | 2020: +0.142 | 2021: +0.139 | 2022: +0.019 | 2023: +0.096 | 2024: +0.153 | 2025: +0.106 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.272 | 2016: +0.182 | 2017: +0.290 | 2018: +0.439 | 2019: +0.290 | 2020: +0.234 | 2021: +0.104 | 2022: +0.225 | 2023: +0.116 | 2024: +0.347 | 2025: -0.038 | 2026: +0.271
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.39
- Early IC=+0.1470, Recent IC=+0.0575, 1st-half IC=+0.1435, 2nd-half IC=+0.0982, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.029, Q3_mid=+0.127, Q4=+0.130, Q5_high_vol=+0.153

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
- Admission: Train IC=+0.2136, Deflated=+0.2130, IR=0.84, Mono=0.81, p=0.0000, MaxCorr=0.88
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

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0939, Sharpe=+0.9969)
- Admission: Train IC=+0.2272, Deflated=+0.2281, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.092 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.142 | 2021: +0.098 | 2022: +0.041 | 2023: +0.078 | 2024: +0.091 | 2025: +0.124 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.155 | 2017: +0.169 | 2018: +0.459 | 2019: +0.286 | 2020: +0.274 | 2021: +0.162 | 2022: +0.108 | 2023: +0.162 | 2024: +0.281 | 2025: +0.156 | 2026: +0.171
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.39
- Early IC=+0.1546, Recent IC=+0.0595, 1st-half IC=+0.1646, 2nd-half IC=+0.0846, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.235, Q2=-0.036, Q3_mid=+0.078, Q4=+0.184, Q5_high_vol=+0.159

**`combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0969, Sharpe=+0.9615)
- Admission: Train IC=+0.2278, Deflated=+0.2278, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.076 | 2017: +0.193 | 2018: +0.139 | 2019: +0.080 | 2020: +0.126 | 2021: +0.056 | 2022: +0.083 | 2023: +0.068 | 2024: +0.099 | 2025: +0.125 | 2026: +0.025
- Yearly Tail ICs:   2015: +0.358 | 2016: +0.113 | 2017: +0.268 | 2018: +0.238 | 2019: +0.238 | 2020: +0.184 | 2021: +0.207 | 2022: +0.335 | 2023: +0.198 | 2024: +0.239 | 2025: +0.207 | 2026: -0.046
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.56
- Early IC=+0.1344, Recent IC=+0.0758, 1st-half IC=+0.1212, 2nd-half IC=+0.0825, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.014, Q3_mid=+0.083, Q4=+0.101, Q5_high_vol=+0.146

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.1105, Sharpe=+0.9584)
- Admission: Train IC=+0.2665, Deflated=+0.2668, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.091 | 2017: +0.219 | 2018: +0.192 | 2019: +0.122 | 2020: +0.138 | 2021: +0.155 | 2022: +0.039 | 2023: +0.111 | 2024: +0.141 | 2025: +0.118 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.234 | 2017: +0.311 | 2018: +0.436 | 2019: +0.298 | 2020: +0.282 | 2021: +0.250 | 2022: +0.197 | 2023: +0.195 | 2024: +0.299 | 2025: +0.047 | 2026: +0.246
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.48
- Early IC=+0.1547, Recent IC=+0.0747, 1st-half IC=+0.1504, 2nd-half IC=+0.1105, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.210, Q2=-0.012, Q3_mid=+0.113, Q4=+0.115, Q5_high_vol=+0.188

**`combo_sig_product__max_up_ret__body_size_progression`** (Lock IC=+0.0895, Sharpe=+0.9555)
- Admission: Train IC=+0.1627, Deflated=+0.1620, IR=0.61, Mono=0.69, p=0.0020, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.135 | 2017: +0.136 | 2018: +0.134 | 2019: +0.110 | 2020: +0.103 | 2021: +0.064 | 2022: +0.077 | 2023: +0.051 | 2024: +0.146 | 2025: +0.054 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.372 | 2016: +0.180 | 2017: +0.143 | 2018: +0.220 | 2019: +0.145 | 2020: +0.202 | 2021: +0.198 | 2022: +0.013 | 2023: +0.030 | 2024: +0.114 | 2025: +0.036 | 2026: +0.297
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.47
- Early IC=+0.1355, Recent IC=+0.0639, 1st-half IC=+0.1274, 2nd-half IC=+0.0762, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.014, Q3_mid=+0.039, Q4=+0.082, Q5_high_vol=+0.162

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0927, Sharpe=+0.9538)
- Admission: Train IC=+0.2266, Deflated=+0.2275, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.313 | 2016: +0.088 | 2017: +0.217 | 2018: +0.206 | 2019: +0.175 | 2020: +0.133 | 2021: +0.089 | 2022: +0.045 | 2023: +0.078 | 2024: +0.089 | 2025: +0.120 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.130 | 2017: +0.195 | 2018: +0.459 | 2019: +0.287 | 2020: +0.262 | 2021: +0.056 | 2022: +0.145 | 2023: +0.128 | 2024: +0.262 | 2025: +0.103 | 2026: +0.094
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.40
- Early IC=+0.1526, Recent IC=+0.0616, 1st-half IC=+0.1634, 2nd-half IC=+0.0814, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.239, Q2=-0.040, Q3_mid=+0.077, Q4=+0.180, Q5_high_vol=+0.154

**`combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0891, Sharpe=+0.9407)
- Admission: Train IC=+0.2037, Deflated=+0.2032, IR=0.53, Mono=0.67, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.113 | 2017: +0.117 | 2018: +0.160 | 2019: +0.091 | 2020: +0.103 | 2021: +0.020 | 2022: +0.138 | 2023: +0.079 | 2024: +0.101 | 2025: +0.090 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.046 | 2016: +0.458 | 2017: +0.197 | 2018: +0.162 | 2019: +0.172 | 2020: +0.112 | 2021: +0.121 | 2022: +0.140 | 2023: +0.150 | 2024: +0.232 | 2025: -0.056 | 2026: -0.127
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.94
- Early IC=+0.1150, Recent IC=+0.1086, 1st-half IC=+0.1197, 2nd-half IC=+0.0884, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.011, Q3_mid=+0.067, Q4=+0.108, Q5_high_vol=+0.161

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0858, Sharpe=+0.9255)
- Admission: Train IC=+0.2566, Deflated=+0.2561, IR=0.98, Mono=0.83, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.089 | 2017: +0.132 | 2018: +0.261 | 2019: +0.173 | 2020: +0.172 | 2021: +0.171 | 2022: +0.067 | 2023: +0.081 | 2024: +0.141 | 2025: +0.071 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.203 | 2016: +0.143 | 2017: +0.307 | 2018: +0.604 | 2019: +0.196 | 2020: +0.164 | 2021: +0.291 | 2022: +0.168 | 2023: +0.255 | 2024: +0.189 | 2025: -0.040 | 2026: +0.007
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.67
- Early IC=+0.1104, Recent IC=+0.0742, 1st-half IC=+0.1624, 2nd-half IC=+0.1248, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.002, Q3_mid=+0.130, Q4=+0.141, Q5_high_vol=+0.244

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0874, Sharpe=+0.8706)
- Admission: Train IC=+0.2513, Deflated=+0.2506, IR=0.88, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.110 | 2017: +0.143 | 2018: +0.284 | 2019: +0.175 | 2020: +0.171 | 2021: +0.171 | 2022: +0.054 | 2023: +0.101 | 2024: +0.158 | 2025: +0.058 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.204 | 2017: +0.306 | 2018: +0.603 | 2019: +0.184 | 2020: +0.123 | 2021: +0.299 | 2022: +0.158 | 2023: +0.252 | 2024: +0.191 | 2025: -0.034 | 2026: +0.013
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.61
- Early IC=+0.1265, Recent IC=+0.0775, 1st-half IC=+0.1778, 2nd-half IC=+0.1247, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.004, Q3_mid=+0.143, Q4=+0.164, Q5_high_vol=+0.241

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0855, Sharpe=+0.8416)
- Admission: Train IC=+0.2698, Deflated=+0.2695, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.101 | 2017: +0.199 | 2018: +0.218 | 2019: +0.146 | 2020: +0.162 | 2021: +0.137 | 2022: +0.068 | 2023: +0.105 | 2024: +0.136 | 2025: +0.021 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.164 | 2017: +0.434 | 2018: +0.346 | 2019: +0.293 | 2020: +0.075 | 2021: +0.226 | 2022: +0.235 | 2023: +0.210 | 2024: +0.342 | 2025: +0.068 | 2026: +0.012
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.58
- Early IC=+0.1497, Recent IC=+0.0865, 1st-half IC=+0.1623, 2nd-half IC=+0.1171, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.015, Q3_mid=+0.106, Q4=+0.173, Q5_high_vol=+0.219

**`combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1127, Sharpe=+0.8107)
- Admission: Train IC=+0.2290, Deflated=+0.2289, IR=0.83, Mono=0.80, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.278 | 2016: +0.084 | 2017: +0.229 | 2018: +0.191 | 2019: +0.141 | 2020: +0.178 | 2021: +0.111 | 2022: +0.082 | 2023: +0.077 | 2024: +0.131 | 2025: +0.101 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.152 | 2017: +0.297 | 2018: +0.312 | 2019: +0.332 | 2020: +0.150 | 2021: +0.203 | 2022: +0.340 | 2023: +0.170 | 2024: +0.206 | 2025: +0.020 | 2026: +0.077
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.51
- Early IC=+0.1567, Recent IC=+0.0796, 1st-half IC=+0.1611, 2nd-half IC=+0.1112, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.205, Q2=-0.007, Q3_mid=+0.118, Q4=+0.152, Q5_high_vol=+0.196

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1096, Sharpe=+0.7699)
- Admission: Train IC=+0.2410, Deflated=+0.2404, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.146 | 2017: +0.223 | 2018: +0.215 | 2019: +0.111 | 2020: +0.187 | 2021: +0.145 | 2022: +0.107 | 2023: +0.116 | 2024: +0.174 | 2025: +0.102 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.262 | 2017: +0.270 | 2018: +0.387 | 2019: +0.260 | 2020: +0.320 | 2021: +0.322 | 2022: +0.031 | 2023: +0.115 | 2024: +0.341 | 2025: -0.030 | 2026: -0.105
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.60
- Early IC=+0.1847, Recent IC=+0.1116, 1st-half IC=+0.1576, 2nd-half IC=+0.1433, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.015, Q3_mid=+0.138, Q4=+0.138, Q5_high_vol=+0.245

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1023, Sharpe=+0.7538)
- Admission: Train IC=+0.2532, Deflated=+0.2532, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.126 | 2017: +0.154 | 2018: +0.157 | 2019: +0.098 | 2020: +0.141 | 2021: +0.059 | 2022: +0.125 | 2023: +0.073 | 2024: +0.090 | 2025: +0.108 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.258 | 2017: +0.222 | 2018: +0.364 | 2019: +0.297 | 2020: +0.181 | 2021: +0.121 | 2022: +0.227 | 2023: +0.176 | 2024: +0.188 | 2025: +0.095 | 2026: +0.115
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.71
- Early IC=+0.1404, Recent IC=+0.0990, 1st-half IC=+0.1329, 2nd-half IC=+0.1050, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.006, Q3_mid=+0.081, Q4=+0.118, Q5_high_vol=+0.173

**`combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0883, Sharpe=+0.7016)
- Admission: Train IC=+0.1563, Deflated=+0.1555, IR=0.37, Mono=0.66, p=0.0034, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.111 | 2017: +0.225 | 2018: +0.128 | 2019: +0.069 | 2020: +0.163 | 2021: +0.053 | 2022: +0.139 | 2023: +0.061 | 2024: +0.099 | 2025: +0.074 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.408 | 2017: +0.159 | 2018: +0.101 | 2019: +0.125 | 2020: +0.127 | 2021: +0.100 | 2022: +0.034 | 2023: +0.015 | 2024: +0.221 | 2025: -0.093 | 2026: -0.080
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.60
- Early IC=+0.1682, Recent IC=+0.1003, 1st-half IC=+0.1335, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.004, Q3_mid=+0.100, Q4=+0.130, Q5_high_vol=+0.174

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.1007, Sharpe=+0.6887)
- Admission: Train IC=+0.1757, Deflated=+0.1753, IR=0.60, Mono=0.72, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.070 | 2017: +0.271 | 2018: +0.191 | 2019: +0.147 | 2020: +0.174 | 2021: +0.099 | 2022: +0.054 | 2023: +0.065 | 2024: +0.158 | 2025: +0.105 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.084 | 2017: +0.234 | 2018: +0.163 | 2019: +0.358 | 2020: +0.068 | 2021: +0.297 | 2022: +0.084 | 2023: +0.183 | 2024: +0.402 | 2025: +0.178 | 2026: -0.048
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.38
- Early IC=+0.1685, Recent IC=+0.0640, 1st-half IC=+0.1649, 2nd-half IC=+0.1004, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.048, Q3_mid=+0.144, Q4=+0.135, Q5_high_vol=+0.199

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0876, Sharpe=+0.6874)
- Admission: Train IC=+0.1727, Deflated=+0.1712, IR=0.47, Mono=0.68, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.036 | 2017: +0.153 | 2018: +0.193 | 2019: +0.171 | 2020: +0.188 | 2021: +0.150 | 2022: +0.028 | 2023: +0.095 | 2024: +0.135 | 2025: +0.058 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.352 | 2016: +0.002 | 2017: +0.327 | 2018: +0.290 | 2019: +0.306 | 2020: +0.004 | 2021: +0.319 | 2022: +0.074 | 2023: +0.118 | 2024: +0.174 | 2025: +0.040 | 2026: +0.253
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.65
- Early IC=+0.0949, Recent IC=+0.0615, 1st-half IC=+0.1385, 2nd-half IC=+0.1149, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.146, Q2=-0.019, Q3_mid=+0.143, Q4=+0.136, Q5_high_vol=+0.204

**`combo_rank_max__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0793, Sharpe=+0.6809)
- Admission: Train IC=+0.1659, Deflated=+0.1661, IR=0.40, Mono=0.67, p=0.0012, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.156 | 2016: +0.069 | 2017: +0.160 | 2018: +0.108 | 2019: +0.043 | 2020: +0.096 | 2021: +0.059 | 2022: +0.103 | 2023: +0.078 | 2024: +0.128 | 2025: +0.145 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.146 | 2017: +0.200 | 2018: +0.103 | 2019: +0.107 | 2020: +0.236 | 2021: +0.239 | 2022: +0.159 | 2023: +0.114 | 2024: +0.331 | 2025: +0.052 | 2026: -0.053
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.79
- Early IC=+0.1138, Recent IC=+0.0897, 1st-half IC=+0.0950, 2nd-half IC=+0.0853, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.028, Q3_mid=+0.111, Q4=+0.095, Q5_high_vol=+0.104

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1093, Sharpe=+0.6791)
- Admission: Train IC=+0.1698, Deflated=+0.1698, IR=0.48, Mono=0.65, p=0.0006, MaxCorr=0.86
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

**`morning_volume_weighted_momentum`** (Lock IC=+0.0778, Sharpe=+0.6660)
- Admission: Train IC=+0.1465, Deflated=+0.1464, IR=0.47, Mono=0.67, p=0.0050, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.039 | 2017: +0.203 | 2018: +0.126 | 2019: +0.090 | 2020: +0.097 | 2021: +0.088 | 2022: +0.095 | 2023: +0.096 | 2024: +0.115 | 2025: +0.165 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.078 | 2017: +0.280 | 2018: +0.104 | 2019: +0.039 | 2020: +0.117 | 2021: +0.174 | 2022: +0.149 | 2023: +0.283 | 2024: +0.184 | 2025: +0.241 | 2026: -0.108
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.79
- Early IC=+0.1210, Recent IC=+0.0951, 1st-half IC=+0.1003, 2nd-half IC=+0.0960, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.176, Q2=-0.011, Q3_mid=+0.111, Q4=+0.095, Q5_high_vol=+0.135

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

**`combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0840, Sharpe=+0.6564)
- Admission: Train IC=+0.1644, Deflated=+0.1637, IR=0.52, Mono=0.70, p=0.0016, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.049 | 2017: +0.152 | 2018: +0.118 | 2019: +0.074 | 2020: +0.101 | 2021: +0.010 | 2022: +0.146 | 2023: +0.084 | 2024: +0.086 | 2025: +0.097 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.060 | 2016: +0.200 | 2017: +0.146 | 2018: +0.101 | 2019: +0.241 | 2020: +0.119 | 2021: +0.106 | 2022: +0.179 | 2023: +0.111 | 2024: +0.153 | 2025: -0.004 | 2026: -0.210
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=1.16
- Early IC=+0.1011, Recent IC=+0.1173, 1st-half IC=+0.0977, 2nd-half IC=+0.0838, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.013, Q3_mid=+0.088, Q4=+0.085, Q5_high_vol=+0.127

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0998, Sharpe=+0.6467)
- Admission: Train IC=+0.1954, Deflated=+0.1949, IR=0.53, Mono=0.69, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.302 | 2016: +0.082 | 2017: +0.253 | 2018: +0.146 | 2019: +0.106 | 2020: +0.169 | 2021: +0.110 | 2022: +0.109 | 2023: +0.072 | 2024: +0.150 | 2025: +0.110 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.530 | 2016: +0.111 | 2017: +0.254 | 2018: +0.235 | 2019: +0.224 | 2020: +0.090 | 2021: +0.234 | 2022: +0.223 | 2023: +0.138 | 2024: +0.238 | 2025: -0.026 | 2026: -0.101
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.54
- Early IC=+0.1673, Recent IC=+0.0904, 1st-half IC=+0.1431, 2nd-half IC=+0.1167, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.021, Q3_mid=+0.133, Q4=+0.152, Q5_high_vol=+0.185

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0994, Sharpe=+0.6449)
- Admission: Train IC=+0.2037, Deflated=+0.2045, IR=0.52, Mono=0.71, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.124 | 2017: +0.192 | 2018: +0.104 | 2019: +0.063 | 2020: +0.106 | 2021: +0.010 | 2022: +0.097 | 2023: +0.054 | 2024: +0.080 | 2025: +0.112 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.195 | 2016: +0.164 | 2017: +0.326 | 2018: +0.268 | 2019: +0.111 | 2020: +0.224 | 2021: +0.112 | 2022: +0.161 | 2023: +0.034 | 2024: +0.229 | 2025: +0.025 | 2026: +0.249
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.48
- Early IC=+0.1582, Recent IC=+0.0754, 1st-half IC=+0.1142, 2nd-half IC=+0.0738, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.022, Q3_mid=+0.066, Q4=+0.079, Q5_high_vol=+0.140

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0994, Sharpe=+0.6418)
- Admission: Train IC=+0.1740, Deflated=+0.1741, IR=0.73, Mono=0.74, p=0.0006, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.048 | 2017: +0.233 | 2018: +0.113 | 2019: +0.122 | 2020: +0.121 | 2021: +0.073 | 2022: +0.056 | 2023: +0.064 | 2024: +0.085 | 2025: +0.133 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.111 | 2017: +0.267 | 2018: +0.360 | 2019: +0.324 | 2020: +0.217 | 2021: +0.340 | 2022: +0.063 | 2023: +0.041 | 2024: +0.147 | 2025: +0.082 | 2026: +0.223
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.40
- Early IC=+0.1421, Recent IC=+0.0574, 1st-half IC=+0.1225, 2nd-half IC=+0.0694, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.059, Q3_mid=+0.115, Q4=+0.122, Q5_high_vol=+0.095

**`combo_mean__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1182, Sharpe=+0.6219)
- Admission: Train IC=+0.2147, Deflated=+0.2150, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.088 | 2017: +0.203 | 2018: +0.106 | 2019: +0.104 | 2020: +0.124 | 2021: +0.059 | 2022: +0.078 | 2023: +0.062 | 2024: +0.115 | 2025: +0.112 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.233 | 2016: +0.196 | 2017: +0.303 | 2018: +0.261 | 2019: +0.297 | 2020: +0.210 | 2021: +0.209 | 2022: +0.207 | 2023: +0.013 | 2024: +0.270 | 2025: +0.060 | 2026: +0.095
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.48
- Early IC=+0.1459, Recent IC=+0.0702, 1st-half IC=+0.1212, 2nd-half IC=+0.0827, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.021, Q3_mid=+0.078, Q4=+0.094, Q5_high_vol=+0.134

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_day_regime_conviction`** (Lock IC=+0.1157, Sharpe=+0.6030)
- Admission: Train IC=+0.2357, Deflated=+0.2348, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.085 | 2017: +0.227 | 2018: +0.189 | 2019: +0.135 | 2020: +0.164 | 2021: +0.103 | 2022: +0.098 | 2023: +0.113 | 2024: +0.153 | 2025: +0.135 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.402 | 2016: +0.197 | 2017: +0.232 | 2018: +0.266 | 2019: +0.228 | 2020: +0.162 | 2021: +0.152 | 2022: +0.353 | 2023: +0.246 | 2024: +0.246 | 2025: +0.061 | 2026: -0.035
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.68
- Early IC=+0.1560, Recent IC=+0.1057, 1st-half IC=+0.1555, 2nd-half IC=+0.1208, Neg regimes=1/5
- Weak component: `trend_day_regime_conviction` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.214, Q2=-0.009, Q3_mid=+0.147, Q4=+0.127, Q5_high_vol=+0.215

**`combo_sig_product__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0826, Sharpe=+0.6025)
- Admission: Train IC=+0.1800, Deflated=+0.1806, IR=0.39, Mono=0.66, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.156 | 2017: +0.140 | 2018: +0.140 | 2019: +0.046 | 2020: +0.106 | 2021: +0.059 | 2022: +0.043 | 2023: +0.112 | 2024: +0.136 | 2025: +0.090 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.267 | 2017: +0.266 | 2018: +0.185 | 2019: -0.030 | 2020: +0.222 | 2021: +0.222 | 2022: +0.041 | 2023: +0.101 | 2024: +0.326 | 2025: -0.004 | 2026: -0.194
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.52
- Early IC=+0.1477, Recent IC=+0.0775, 1st-half IC=+0.1179, 2nd-half IC=+0.0810, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.024, Q3_mid=+0.080, Q4=+0.054, Q5_high_vol=+0.203

**`combo_max__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0803, Sharpe=+0.5993)
- Admission: Train IC=+0.2269, Deflated=+0.2265, IR=0.54, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.106 | 2017: +0.133 | 2018: +0.205 | 2019: +0.089 | 2020: +0.095 | 2021: +0.115 | 2022: +0.102 | 2023: +0.059 | 2024: +0.126 | 2025: +0.098 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.255 | 2017: +0.164 | 2018: +0.252 | 2019: +0.138 | 2020: +0.213 | 2021: +0.228 | 2022: +0.219 | 2023: +0.324 | 2024: +0.265 | 2025: +0.163 | 2026: -0.226
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.67
- Early IC=+0.1197, Recent IC=+0.0803, 1st-half IC=+0.1323, 2nd-half IC=+0.0924, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.166, Q2=-0.029, Q3_mid=+0.085, Q4=+0.168, Q5_high_vol=+0.148

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1193, Sharpe=+0.5966)
- Admission: Train IC=+0.2745, Deflated=+0.2746, IR=1.02, Mono=0.84, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.120 | 2017: +0.225 | 2018: +0.180 | 2019: +0.173 | 2020: +0.172 | 2021: +0.143 | 2022: +0.006 | 2023: +0.103 | 2024: +0.159 | 2025: +0.093 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.361 | 2016: +0.235 | 2017: +0.326 | 2018: +0.506 | 2019: +0.324 | 2020: +0.261 | 2021: +0.289 | 2022: +0.138 | 2023: +0.114 | 2024: +0.281 | 2025: -0.018 | 2026: +0.171
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.32
- Early IC=+0.1723, Recent IC=+0.0546, 1st-half IC=+0.1698, 2nd-half IC=+0.1121, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.033, Q3_mid=+0.133, Q4=+0.134, Q5_high_vol=+0.215

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=+0.0784, Sharpe=+0.5697)
- Admission: Train IC=+0.2183, Deflated=+0.2190, IR=0.58, Mono=0.68, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.111 | 2017: +0.191 | 2018: +0.243 | 2019: +0.136 | 2020: +0.111 | 2021: +0.136 | 2022: +0.102 | 2023: +0.097 | 2024: +0.141 | 2025: +0.076 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.130 | 2017: +0.264 | 2018: +0.469 | 2019: +0.116 | 2020: +0.232 | 2021: +0.280 | 2022: +0.105 | 2023: +0.141 | 2024: +0.143 | 2025: +0.045 | 2026: -0.250
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.66
- Early IC=+0.1508, Recent IC=+0.0991, 1st-half IC=+0.1616, 2nd-half IC=+0.1100, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.025, Q3_mid=+0.112, Q4=+0.159, Q5_high_vol=+0.202

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0595, Sharpe=+0.5616)
- Admission: Train IC=+0.1711, Deflated=+0.1716, IR=0.46, Mono=0.70, p=0.0006, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.137 | 2017: +0.074 | 2018: +0.168 | 2019: +0.094 | 2020: +0.137 | 2021: +0.078 | 2022: +0.098 | 2023: +0.076 | 2024: +0.093 | 2025: +0.079 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.389 | 2016: +0.058 | 2017: +0.086 | 2018: +0.203 | 2019: +0.184 | 2020: +0.214 | 2021: +0.007 | 2022: +0.179 | 2023: +0.250 | 2024: +0.119 | 2025: +0.074 | 2026: -0.063
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.82
- Early IC=+0.1057, Recent IC=+0.0868, 1st-half IC=+0.1182, 2nd-half IC=+0.1006, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.139, Q2=-0.029, Q3_mid=+0.108, Q4=+0.154, Q5_high_vol=+0.151

**`open_to_current_return`** (Lock IC=+0.0774, Sharpe=+0.5603)
- Admission: Train IC=+0.1415, Deflated=+0.1415, IR=0.52, Mono=0.71, p=0.0068, MaxCorr=0.88
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

**`opening_drive_thrust_ratio`** (Lock IC=+0.0962, Sharpe=+0.5296)
- Admission: Train IC=+0.1931, Deflated=+0.1922, IR=0.63, Mono=0.77, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069 | 2023: +0.102 | 2024: +0.152 | 2025: +0.088 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.517 | 2016: +0.047 | 2017: +0.205 | 2018: +0.244 | 2019: +0.347 | 2020: +0.069 | 2021: +0.321 | 2022: +0.278 | 2023: +0.019 | 2024: +0.151 | 2025: +0.052 | 2026: -0.026
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.57
- Early IC=+0.1495, Recent IC=+0.0856, 1st-half IC=+0.1601, 2nd-half IC=+0.1219, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.016, Q3_mid=+0.149, Q4=+0.151, Q5_high_vol=+0.214

**`combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1094, Sharpe=+0.5292)
- Admission: Train IC=+0.1706, Deflated=+0.1698, IR=0.57, Mono=0.71, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.109 | 2017: +0.202 | 2018: +0.159 | 2019: +0.123 | 2020: +0.126 | 2021: +0.028 | 2022: +0.147 | 2023: +0.087 | 2024: +0.100 | 2025: +0.126 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.001 | 2017: +0.182 | 2018: +0.132 | 2019: +0.276 | 2020: +0.111 | 2021: +0.185 | 2022: +0.256 | 2023: +0.145 | 2024: +0.137 | 2025: +0.162 | 2026: -0.354
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.74
- Early IC=+0.1573, Recent IC=+0.1170, 1st-half IC=+0.1447, 2nd-half IC=+0.1022, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.013, Q3_mid=+0.086, Q4=+0.129, Q5_high_vol=+0.177

**`combo_rank_max__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1136, Sharpe=+0.5275)
- Admission: Train IC=+0.1600, Deflated=+0.1594, IR=0.51, Mono=0.71, p=0.0024, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.068 | 2017: +0.194 | 2018: +0.126 | 2019: +0.122 | 2020: +0.097 | 2021: +0.015 | 2022: +0.143 | 2023: +0.065 | 2024: +0.111 | 2025: +0.106 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.194 | 2017: +0.158 | 2018: +0.069 | 2019: +0.328 | 2020: +0.085 | 2021: +0.148 | 2022: +0.263 | 2023: +0.060 | 2024: +0.229 | 2025: -0.056 | 2026: -0.138
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.81
- Early IC=+0.1310, Recent IC=+0.1057, 1st-half IC=+0.1204, 2nd-half IC=+0.0838, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.007, Q3_mid=+0.087, Q4=+0.102, Q5_high_vol=+0.130

**`combo_min__net_volume_flow__max_down_ret`** (Lock IC=+0.1016, Sharpe=+0.5225)
- Admission: Train IC=+0.1787, Deflated=+0.1786, IR=0.58, Mono=0.70, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.061 | 2017: +0.194 | 2018: +0.133 | 2019: +0.100 | 2020: +0.132 | 2021: +0.081 | 2022: +0.097 | 2023: +0.080 | 2024: +0.114 | 2025: +0.137 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.304 | 2016: -0.077 | 2017: +0.210 | 2018: +0.115 | 2019: +0.300 | 2020: +0.222 | 2021: +0.286 | 2022: +0.252 | 2023: +0.211 | 2024: +0.297 | 2025: +0.178 | 2026: +0.056
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.69
- Early IC=+0.1274, Recent IC=+0.0884, 1st-half IC=+0.1197, 2nd-half IC=+0.0935, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.039, Q3_mid=+0.121, Q4=+0.130, Q5_high_vol=+0.121

**`combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0919, Sharpe=+0.5194)
- Admission: Train IC=+0.1910, Deflated=+0.1907, IR=0.67, Mono=0.76, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.098 | 2017: +0.196 | 2018: +0.233 | 2019: +0.142 | 2020: +0.133 | 2021: +0.143 | 2022: +0.090 | 2023: +0.083 | 2024: +0.135 | 2025: +0.098 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.521 | 2016: +0.025 | 2017: +0.172 | 2018: +0.248 | 2019: +0.347 | 2020: +0.053 | 2021: +0.287 | 2022: +0.311 | 2023: +0.023 | 2024: +0.160 | 2025: +0.038 | 2026: -0.005
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.59
- Early IC=+0.1470, Recent IC=+0.0867, 1st-half IC=+0.1659, 2nd-half IC=+0.1128, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.030, Q3_mid=+0.131, Q4=+0.191, Q5_high_vol=+0.188

**`combo_rank_max__max_up_ret__close_vs_open_range`** (Lock IC=+0.0785, Sharpe=+0.5109)
- Admission: Train IC=+0.2045, Deflated=+0.2049, IR=0.66, Mono=0.71, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.098 | 2017: +0.216 | 2018: +0.206 | 2019: +0.101 | 2020: +0.143 | 2021: +0.092 | 2022: +0.116 | 2023: +0.095 | 2024: +0.131 | 2025: +0.078 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.252 | 2017: +0.228 | 2018: +0.284 | 2019: +0.150 | 2020: +0.278 | 2021: +0.168 | 2022: +0.077 | 2023: +0.158 | 2024: +0.260 | 2025: -0.228 | 2026: -0.409
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.68
- Early IC=+0.1555, Recent IC=+0.1065, 1st-half IC=+0.1468, 2nd-half IC=+0.1188, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.206, Q2=-0.024, Q3_mid=+0.127, Q4=+0.123, Q5_high_vol=+0.214

**`combo_sig_product__max_up_ret__net_volume_flow`** (Lock IC=+0.0933, Sharpe=+0.5076)
- Admission: Train IC=+0.2285, Deflated=+0.2294, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.151 | 2017: +0.118 | 2018: +0.175 | 2019: +0.064 | 2020: +0.115 | 2021: +0.090 | 2022: +0.074 | 2023: +0.112 | 2024: +0.157 | 2025: +0.078 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.388 | 2016: +0.140 | 2017: +0.185 | 2018: +0.242 | 2019: +0.165 | 2020: +0.276 | 2021: +0.195 | 2022: +0.188 | 2023: +0.350 | 2024: +0.276 | 2025: +0.014 | 2026: -0.115
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.69
- Early IC=+0.1348, Recent IC=+0.0933, 1st-half IC=+0.1225, 2nd-half IC=+0.0970, Neg regimes=1/5
- Weak component: `net_volume_flow` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.170, Q2=-0.021, Q3_mid=+0.093, Q4=+0.093, Q5_high_vol=+0.180

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0955, Sharpe=+0.5066)
- Admission: Train IC=+0.2717, Deflated=+0.2718, IR=0.76, Mono=0.74, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.112 | 2017: +0.195 | 2018: +0.204 | 2019: +0.085 | 2020: +0.161 | 2021: +0.081 | 2022: +0.116 | 2023: +0.089 | 2024: +0.085 | 2025: +0.134 | 2026: +0.033
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.271 | 2017: +0.313 | 2018: +0.362 | 2019: +0.228 | 2020: +0.237 | 2021: +0.124 | 2022: +0.264 | 2023: +0.107 | 2024: +0.219 | 2025: -0.037 | 2026: -0.011
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.67
- Early IC=+0.1537, Recent IC=+0.1028, 1st-half IC=+0.1455, 2nd-half IC=+0.1157, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.002, Q3_mid=+0.093, Q4=+0.129, Q5_high_vol=+0.217

**`combo_min__close_vs_open_range__first_bar_return`** (Lock IC=+0.1023, Sharpe=+0.4955)
- Admission: Train IC=+0.1848, Deflated=+0.1852, IR=0.62, Mono=0.71, p=0.0002, MaxCorr=0.91
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

**`combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0815, Sharpe=+0.4854)
- Admission: Train IC=+0.1674, Deflated=+0.1658, IR=0.62, Mono=0.74, p=0.0008, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.229 | 2016: -0.012 | 2017: +0.146 | 2018: +0.169 | 2019: +0.135 | 2020: +0.166 | 2021: +0.146 | 2022: +0.048 | 2023: +0.058 | 2024: +0.119 | 2025: +0.080 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.054 | 2017: +0.282 | 2018: +0.345 | 2019: +0.219 | 2020: +0.102 | 2021: +0.296 | 2022: +0.004 | 2023: +0.198 | 2024: +0.270 | 2025: -0.023 | 2026: +0.336
- IC CV=0.58, Neg years (linear/tail)=1/0 of 8, Half ratio=0.91, Recency ratio=0.79
- Early IC=+0.0673, Recent IC=+0.0531, 1st-half IC=+0.1125, 2nd-half IC=+0.1024, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.136, Q2=-0.050, Q3_mid=+0.130, Q4=+0.100, Q5_high_vol=+0.183

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0991, Sharpe=+0.4835)
- Admission: Train IC=+0.2612, Deflated=+0.2604, IR=0.89, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.056 | 2017: +0.164 | 2018: +0.246 | 2019: +0.173 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145 | 2025: +0.096 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.054 | 2017: +0.194 | 2018: +0.413 | 2019: +0.231 | 2020: +0.221 | 2021: +0.335 | 2022: +0.237 | 2023: +0.314 | 2024: +0.298 | 2025: +0.095 | 2026: -0.350
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.75
- Early IC=+0.1100, Recent IC=+0.0820, 1st-half IC=+0.1649, 2nd-half IC=+0.1118, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.169, Q2=-0.006, Q3_mid=+0.147, Q4=+0.167, Q5_high_vol=+0.197

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.1052, Sharpe=+0.4780)
- Admission: Train IC=+0.2277, Deflated=+0.2278, IR=0.62, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.117 | 2017: +0.218 | 2018: +0.207 | 2019: +0.122 | 2020: +0.136 | 2021: +0.108 | 2022: +0.101 | 2023: +0.108 | 2024: +0.153 | 2025: +0.127 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.226 | 2016: +0.223 | 2017: +0.308 | 2018: +0.388 | 2019: +0.238 | 2020: +0.189 | 2021: +0.248 | 2022: +0.066 | 2023: +0.140 | 2024: +0.316 | 2025: -0.075 | 2026: -0.285
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.62
- Early IC=+0.1676, Recent IC=+0.1045, 1st-half IC=+0.1533, 2nd-half IC=+0.1154, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.221, Q2=-0.010, Q3_mid=+0.112, Q4=+0.128, Q5_high_vol=+0.211

**`combo_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0735, Sharpe=+0.4772)
- Admission: Train IC=+0.2318, Deflated=+0.2320, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.105 | 2017: +0.151 | 2018: +0.213 | 2019: +0.072 | 2020: +0.131 | 2021: +0.058 | 2022: +0.120 | 2023: +0.092 | 2024: +0.128 | 2025: +0.096 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.249 | 2016: +0.256 | 2017: +0.253 | 2018: +0.358 | 2019: +0.117 | 2020: +0.228 | 2021: +0.214 | 2022: +0.129 | 2023: +0.154 | 2024: +0.250 | 2025: -0.157 | 2026: -0.296
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.83
- Early IC=+0.1277, Recent IC=+0.1059, 1st-half IC=+0.1329, 2nd-half IC=+0.1066, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.160, Q2=-0.024, Q3_mid=+0.097, Q4=+0.130, Q5_high_vol=+0.206

**`combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0946, Sharpe=+0.4749)
- Admission: Train IC=+0.2369, Deflated=+0.2364, IR=0.84, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.062 | 2017: +0.153 | 2018: +0.136 | 2019: +0.084 | 2020: +0.119 | 2021: +0.095 | 2022: +0.100 | 2023: +0.099 | 2024: +0.140 | 2025: +0.125 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.191 | 2017: +0.172 | 2018: +0.276 | 2019: +0.220 | 2020: +0.269 | 2021: +0.263 | 2022: +0.304 | 2023: +0.229 | 2024: +0.291 | 2025: +0.016 | 2026: -0.203
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.93
- Early IC=+0.1076, Recent IC=+0.0998, 1st-half IC=+0.1098, 2nd-half IC=+0.0995, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.035, Q3_mid=+0.107, Q4=+0.126, Q5_high_vol=+0.137

**`combo_min__net_volume_flow__first_bar_return`** (Lock IC=+0.0967, Sharpe=+0.4715)
- Admission: Train IC=+0.2237, Deflated=+0.2241, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.071 | 2017: +0.181 | 2018: +0.179 | 2019: +0.124 | 2020: +0.092 | 2021: +0.082 | 2022: +0.085 | 2023: +0.076 | 2024: +0.130 | 2025: +0.121 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.374 | 2016: +0.010 | 2017: +0.227 | 2018: +0.400 | 2019: +0.144 | 2020: +0.090 | 2021: +0.286 | 2022: +0.257 | 2023: +0.300 | 2024: +0.321 | 2025: +0.121 | 2026: -0.008
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.64
- Early IC=+0.1261, Recent IC=+0.0804, 1st-half IC=+0.1355, 2nd-half IC=+0.0836, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.031, Q3_mid=+0.102, Q4=+0.151, Q5_high_vol=+0.123

**`combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction`** (Lock IC=+0.0934, Sharpe=+0.4700)
- Admission: Train IC=+0.1982, Deflated=+0.1978, IR=0.47, Mono=0.70, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.061 | 2017: +0.194 | 2018: +0.121 | 2019: +0.079 | 2020: +0.092 | 2021: +0.068 | 2022: +0.090 | 2023: +0.090 | 2024: +0.138 | 2025: +0.136 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.342 | 2016: +0.160 | 2017: +0.192 | 2018: +0.142 | 2019: +0.188 | 2020: +0.158 | 2021: +0.109 | 2022: +0.352 | 2023: +0.208 | 2024: +0.342 | 2025: +0.126 | 2026: +0.037
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.71
- Early IC=+0.1276, Recent IC=+0.0900, 1st-half IC=+0.1091, 2nd-half IC=+0.0848, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.036, Q3_mid=+0.106, Q4=+0.089, Q5_high_vol=+0.144

**`combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1529, Sharpe=+0.4587)
- Admission: Train IC=+0.1543, Deflated=+0.1535, IR=0.50, Mono=0.67, p=0.0038, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.191 | 2016: -0.006 | 2017: +0.187 | 2018: +0.098 | 2019: +0.192 | 2020: +0.089 | 2021: +0.103 | 2022: +0.045 | 2023: +0.029 | 2024: +0.151 | 2025: +0.091 | 2026: +0.225
- Yearly Tail ICs:   2015: +0.099 | 2016: -0.040 | 2017: +0.262 | 2018: +0.183 | 2019: +0.367 | 2020: +0.023 | 2021: +0.300 | 2022: +0.157 | 2023: +0.070 | 2024: +0.121 | 2025: -0.038 | 2026: +0.325
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=0.54, Recency ratio=0.41
- Early IC=+0.0908, Recent IC=+0.0372, 1st-half IC=+0.1188, 2nd-half IC=+0.0642, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.156, Q2=-0.025, Q3_mid=+0.075, Q4=+0.117, Q5_high_vol=+0.143

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

**`combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1124, Sharpe=+0.4201)
- Admission: Train IC=+0.1635, Deflated=+0.1628, IR=0.42, Mono=0.67, p=0.0018, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.079 | 2017: +0.213 | 2018: +0.141 | 2019: +0.114 | 2020: +0.130 | 2021: +0.029 | 2022: +0.116 | 2023: +0.053 | 2024: +0.108 | 2025: +0.126 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.161 | 2017: +0.218 | 2018: +0.075 | 2019: +0.253 | 2020: +0.162 | 2021: +0.082 | 2022: +0.259 | 2023: +0.065 | 2024: +0.085 | 2025: +0.102 | 2026: -0.062
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.58
- Early IC=+0.1461, Recent IC=+0.0844, 1st-half IC=+0.1308, 2nd-half IC=+0.0847, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.001, Q3_mid=+0.083, Q4=+0.114, Q5_high_vol=+0.151

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0949, Sharpe=+0.4145)
- Admission: Train IC=+0.2494, Deflated=+0.2489, IR=0.89, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.101 | 2017: +0.206 | 2018: +0.217 | 2019: +0.146 | 2020: +0.152 | 2021: +0.126 | 2022: +0.061 | 2023: +0.119 | 2024: +0.156 | 2025: +0.095 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.515 | 2016: +0.270 | 2017: +0.341 | 2018: +0.367 | 2019: +0.206 | 2020: +0.182 | 2021: +0.279 | 2022: +0.210 | 2023: +0.221 | 2024: +0.183 | 2025: -0.133 | 2026: -0.059
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.59
- Early IC=+0.1535, Recent IC=+0.0899, 1st-half IC=+0.1552, 2nd-half IC=+0.1203, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.022, Q3_mid=+0.151, Q4=+0.121, Q5_high_vol=+0.230

**`combo_rank_max__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0915, Sharpe=+0.4102)
- Admission: Train IC=+0.2266, Deflated=+0.2259, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.084 | 2017: +0.219 | 2018: +0.152 | 2019: +0.083 | 2020: +0.137 | 2021: +0.098 | 2022: +0.107 | 2023: +0.073 | 2024: +0.151 | 2025: +0.120 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.482 | 2016: +0.207 | 2017: +0.388 | 2018: +0.181 | 2019: +0.287 | 2020: +0.206 | 2021: +0.232 | 2022: +0.306 | 2023: +0.214 | 2024: +0.288 | 2025: +0.067 | 2026: -0.136
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.59
- Early IC=+0.1520, Recent IC=+0.0901, 1st-half IC=+0.1366, 2nd-half IC=+0.1032, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.023, Q3_mid=+0.117, Q4=+0.153, Q5_high_vol=+0.157

**`combo_max__trend_bar_close_consistency__max_down_ret`** (Lock IC=+0.0635, Sharpe=+0.4032)
- Admission: Train IC=+0.1319, Deflated=+0.1314, IR=0.36, Mono=0.66, p=0.0094, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.014 | 2017: +0.209 | 2018: +0.118 | 2019: +0.044 | 2020: +0.118 | 2021: +0.067 | 2022: +0.075 | 2023: +0.072 | 2024: +0.103 | 2025: +0.137 | 2026: -0.121
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.153 | 2017: +0.183 | 2018: -0.020 | 2019: +0.027 | 2020: +0.034 | 2021: +0.232 | 2022: +0.257 | 2023: +0.246 | 2024: +0.290 | 2025: +0.094 | 2026: -0.188
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=0.87, Recency ratio=0.66
- Early IC=+0.1113, Recent IC=+0.0736, 1st-half IC=+0.0930, 2nd-half IC=+0.0811, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.166, Q2=-0.012, Q3_mid=+0.108, Q4=+0.099, Q5_high_vol=+0.094

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0889, Sharpe=+0.4004)
- Admission: Train IC=+0.2615, Deflated=+0.2607, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.046 | 2017: +0.160 | 2018: +0.221 | 2019: +0.173 | 2020: +0.158 | 2021: +0.162 | 2022: +0.052 | 2023: +0.086 | 2024: +0.126 | 2025: +0.097 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.028 | 2017: +0.191 | 2018: +0.386 | 2019: +0.254 | 2020: +0.224 | 2021: +0.331 | 2022: +0.238 | 2023: +0.306 | 2024: +0.297 | 2025: +0.090 | 2026: -0.354
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.67
- Early IC=+0.1030, Recent IC=+0.0688, 1st-half IC=+0.1550, 2nd-half IC=+0.1081, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.013, Q3_mid=+0.142, Q4=+0.164, Q5_high_vol=+0.182

**`combo_sig_product__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.0762, Sharpe=+0.3899)
- Admission: Train IC=+0.1462, Deflated=+0.1464, IR=0.40, Mono=0.66, p=0.0052, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.140 | 2016: +0.074 | 2017: +0.133 | 2018: +0.046 | 2019: +0.059 | 2020: +0.057 | 2021: +0.093 | 2022: +0.102 | 2023: +0.122 | 2024: +0.068 | 2025: +0.055 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.147 | 2017: +0.228 | 2018: +0.163 | 2019: +0.094 | 2020: +0.079 | 2021: +0.027 | 2022: +0.197 | 2023: +0.264 | 2024: +0.141 | 2025: -0.029 | 2026: -0.032
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=1.08
- Early IC=+0.1037, Recent IC=+0.1121, 1st-half IC=+0.0759, 2nd-half IC=+0.0884, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.010, Q3_mid=+0.057, Q4=+0.079, Q5_high_vol=+0.095

**`combo_rank_max__early_body_momentum__max_down_ret`** (Lock IC=+0.0881, Sharpe=+0.3895)
- Admission: Train IC=+0.1738, Deflated=+0.1735, IR=0.48, Mono=0.68, p=0.0006, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.047 | 2017: +0.196 | 2018: +0.163 | 2019: +0.093 | 2020: +0.102 | 2021: +0.073 | 2022: +0.075 | 2023: +0.042 | 2024: +0.131 | 2025: +0.167 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.058 | 2017: +0.278 | 2018: +0.099 | 2019: +0.329 | 2020: +0.051 | 2021: +0.261 | 2022: +0.263 | 2023: +0.160 | 2024: +0.238 | 2025: +0.295 | 2026: -0.085
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.49
- Early IC=+0.1205, Recent IC=+0.0593, 1st-half IC=+0.1256, 2nd-half IC=+0.0695, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.029, Q3_mid=+0.118, Q4=+0.127, Q5_high_vol=+0.111

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`** (Lock IC=+0.0963, Sharpe=+0.3789)
- Admission: Train IC=+0.2402, Deflated=+0.2398, IR=0.60, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.119 | 2017: +0.231 | 2018: +0.185 | 2019: +0.099 | 2020: +0.143 | 2021: +0.130 | 2022: +0.132 | 2023: +0.103 | 2024: +0.144 | 2025: +0.118 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.510 | 2016: +0.361 | 2017: +0.225 | 2018: +0.290 | 2019: +0.164 | 2020: +0.205 | 2021: +0.393 | 2022: +0.129 | 2023: +0.179 | 2024: +0.175 | 2025: +0.107 | 2026: -0.140
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.67
- Early IC=+0.1748, Recent IC=+0.1177, 1st-half IC=+0.1437, 2nd-half IC=+0.1350, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.004, Q3_mid=+0.136, Q4=+0.128, Q5_high_vol=+0.227

**`combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0794, Sharpe=+0.3571)
- Admission: Train IC=+0.1724, Deflated=+0.1720, IR=0.31, Mono=0.66, p=0.0006, MaxCorr=0.62
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

**`combo_min__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0882, Sharpe=+0.3496)
- Admission: Train IC=+0.1870, Deflated=+0.1874, IR=0.57, Mono=0.73, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.107 | 2017: +0.171 | 2018: +0.175 | 2019: +0.113 | 2020: +0.117 | 2021: +0.090 | 2022: +0.101 | 2023: +0.090 | 2024: +0.121 | 2025: +0.136 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.263 | 2016: -0.063 | 2017: +0.210 | 2018: +0.215 | 2019: +0.187 | 2020: +0.297 | 2021: +0.055 | 2022: +0.208 | 2023: +0.265 | 2024: +0.277 | 2025: +0.234 | 2026: -0.009
- IC CV=0.26, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.69
- Early IC=+0.1388, Recent IC=+0.0955, 1st-half IC=+0.1404, 2nd-half IC=+0.0995, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.008, Q3_mid=+0.110, Q4=+0.173, Q5_high_vol=+0.131

**`combo_rank_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0988, Sharpe=+0.3362)
- Admission: Train IC=+0.1410, Deflated=+0.1404, IR=0.52, Mono=0.71, p=0.0074, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.048 | 2017: +0.223 | 2018: +0.166 | 2019: +0.110 | 2020: +0.147 | 2021: +0.099 | 2022: +0.078 | 2023: +0.080 | 2024: +0.120 | 2025: +0.121 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.050 | 2017: +0.153 | 2018: +0.091 | 2019: +0.327 | 2020: +0.059 | 2021: +0.353 | 2022: +0.208 | 2023: +0.072 | 2024: +0.188 | 2025: +0.122 | 2026: -0.052
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=0.68, Recency ratio=0.55
- Early IC=+0.1365, Recent IC=+0.0747, 1st-half IC=+0.1345, 2nd-half IC=+0.0913, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.027, Q3_mid=+0.139, Q4=+0.154, Q5_high_vol=+0.119

**`combo_tri_median__max_up_ret__net_volume_flow__body_size_progression`** (Lock IC=+0.0770, Sharpe=+0.3299)
- Admission: Train IC=+0.1509, Deflated=+0.1512, IR=0.51, Mono=0.68, p=0.0042, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.085 | 2017: +0.101 | 2018: +0.137 | 2019: +0.069 | 2020: +0.075 | 2021: +0.112 | 2022: +0.114 | 2023: +0.116 | 2024: +0.113 | 2025: +0.144 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.158 | 2017: +0.078 | 2018: +0.234 | 2019: +0.161 | 2020: +0.085 | 2021: +0.290 | 2022: +0.102 | 2023: +0.089 | 2024: +0.163 | 2025: +0.184 | 2026: -0.426
- IC CV=0.21, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.23
- Early IC=+0.0933, Recent IC=+0.1147, 1st-half IC=+0.0944, 2nd-half IC=+0.1064, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.002, Q3_mid=+0.106, Q4=+0.110, Q5_high_vol=+0.135

**`combo_mean__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0905, Sharpe=+0.3245)
- Admission: Train IC=+0.2230, Deflated=+0.2230, IR=0.62, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.093 | 2017: +0.234 | 2018: +0.259 | 2019: +0.154 | 2020: +0.155 | 2021: +0.131 | 2022: +0.084 | 2023: +0.089 | 2024: +0.149 | 2025: +0.087 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.002 | 2017: +0.213 | 2018: +0.483 | 2019: +0.147 | 2020: +0.248 | 2021: +0.302 | 2022: +0.191 | 2023: +0.153 | 2024: +0.213 | 2025: +0.021 | 2026: -0.237
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.53
- Early IC=+0.1637, Recent IC=+0.0867, 1st-half IC=+0.1830, 2nd-half IC=+0.1160, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.022, Q3_mid=+0.149, Q4=+0.174, Q5_high_vol=+0.193

**`combo_rank_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0890, Sharpe=+0.3159)
- Admission: Train IC=+0.2313, Deflated=+0.2310, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.94
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
- Admission: Train IC=+0.1751, Deflated=+0.1749, IR=0.49, Mono=0.67, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.068 | 2017: +0.225 | 2018: +0.138 | 2019: +0.098 | 2020: +0.119 | 2021: +0.070 | 2022: +0.077 | 2023: +0.074 | 2024: +0.123 | 2025: +0.143 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.286 | 2016: -0.117 | 2017: +0.327 | 2018: +0.101 | 2019: +0.233 | 2020: +0.092 | 2021: +0.303 | 2022: +0.322 | 2023: +0.276 | 2024: +0.311 | 2025: +0.126 | 2026: -0.168
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.51
- Early IC=+0.1468, Recent IC=+0.0754, 1st-half IC=+0.1276, 2nd-half IC=+0.0847, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.038, Q3_mid=+0.111, Q4=+0.106, Q5_high_vol=+0.141

**`combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0579, Sharpe=+0.2946)
- Admission: Train IC=+0.2054, Deflated=+0.2045, IR=0.51, Mono=0.68, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.059 | 2017: +0.239 | 2018: +0.132 | 2019: +0.081 | 2020: +0.162 | 2021: +0.089 | 2022: +0.093 | 2023: +0.110 | 2024: +0.086 | 2025: +0.096 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.329 | 2016: +0.052 | 2017: +0.388 | 2018: +0.235 | 2019: +0.062 | 2020: +0.251 | 2021: +0.278 | 2022: +0.232 | 2023: +0.074 | 2024: +0.316 | 2025: +0.083 | 2026: -0.233
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.68
- Early IC=+0.1492, Recent IC=+0.1015, 1st-half IC=+0.1259, 2nd-half IC=+0.1154, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.185, Q2=-0.004, Q3_mid=+0.160, Q4=+0.100, Q5_high_vol=+0.166

**`combo_rank_min__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0931, Sharpe=+0.2815)
- Admission: Train IC=+0.2285, Deflated=+0.2289, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.075 | 2017: +0.191 | 2018: +0.189 | 2019: +0.131 | 2020: +0.076 | 2021: +0.068 | 2022: +0.049 | 2023: +0.067 | 2024: +0.109 | 2025: +0.131 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.070 | 2017: +0.308 | 2018: +0.297 | 2019: +0.272 | 2020: +0.175 | 2021: +0.291 | 2022: +0.185 | 2023: +0.210 | 2024: +0.119 | 2025: +0.147 | 2026: -0.075
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.45, Recency ratio=0.43
- Early IC=+0.1335, Recent IC=+0.0579, 1st-half IC=+0.1452, 2nd-half IC=+0.0655, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.050, Q3_mid=+0.092, Q4=+0.134, Q5_high_vol=+0.131

**`first_bar_return`** (Lock IC=+0.0686, Sharpe=+0.2803)
- Admission: Train IC=+0.1959, Deflated=+0.1970, IR=0.49, Mono=0.67, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.47, Recency ratio=0.47
- Early IC=+0.1327, Recent IC=+0.0624, 1st-half IC=+0.1626, 2nd-half IC=+0.0765, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.031, Q3_mid=+0.102, Q4=+0.169, Q5_high_vol=+0.139

**`combo_mean__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0686, Sharpe=+0.2803)
- Admission: Train IC=+0.1959, Deflated=+0.1970, IR=0.49, Mono=0.67, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.47, Recency ratio=0.47
- Early IC=+0.1327, Recent IC=+0.0624, 1st-half IC=+0.1626, 2nd-half IC=+0.0765, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.031, Q3_mid=+0.102, Q4=+0.169, Q5_high_vol=+0.139

**`combo_max__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1108, Sharpe=+0.2764)
- Admission: Train IC=+0.1561, Deflated=+0.1555, IR=0.42, Mono=0.68, p=0.0034, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.069 | 2017: +0.197 | 2018: +0.124 | 2019: +0.121 | 2020: +0.111 | 2021: +0.016 | 2022: +0.131 | 2023: +0.053 | 2024: +0.104 | 2025: +0.108 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.181 | 2017: +0.163 | 2018: +0.059 | 2019: +0.278 | 2020: +0.113 | 2021: +0.099 | 2022: +0.261 | 2023: +0.046 | 2024: +0.224 | 2025: -0.017 | 2026: -0.111
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.69
- Early IC=+0.1332, Recent IC=+0.0920, 1st-half IC=+0.1218, 2nd-half IC=+0.0821, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.012, Q3_mid=+0.083, Q4=+0.105, Q5_high_vol=+0.136

**`combo_rank_min__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0961, Sharpe=+0.2697)
- Admission: Train IC=+0.1977, Deflated=+0.1978, IR=0.55, Mono=0.69, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.077 | 2017: +0.236 | 2018: +0.132 | 2019: +0.097 | 2020: +0.142 | 2021: +0.054 | 2022: +0.084 | 2023: +0.081 | 2024: +0.112 | 2025: +0.135 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.285 | 2016: -0.076 | 2017: +0.295 | 2018: +0.113 | 2019: +0.263 | 2020: +0.207 | 2021: +0.349 | 2022: +0.282 | 2023: +0.266 | 2024: +0.142 | 2025: +0.162 | 2026: -0.067
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.68, Recency ratio=0.51
- Early IC=+0.1585, Recent IC=+0.0801, 1st-half IC=+0.1318, 2nd-half IC=+0.0895, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.053, Q3_mid=+0.139, Q4=+0.126, Q5_high_vol=+0.125

**`combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0885, Sharpe=+0.2644)
- Admission: Train IC=+0.1983, Deflated=+0.1986, IR=0.61, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.100 | 2017: +0.226 | 2018: +0.241 | 2019: +0.145 | 2020: +0.142 | 2021: +0.169 | 2022: +0.092 | 2023: +0.108 | 2024: +0.150 | 2025: +0.088 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.336 | 2016: -0.072 | 2017: +0.187 | 2018: +0.368 | 2019: +0.218 | 2020: +0.248 | 2021: +0.353 | 2022: +0.155 | 2023: +0.156 | 2024: +0.280 | 2025: -0.017 | 2026: -0.111
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.74, Recency ratio=0.61
- Early IC=+0.1626, Recent IC=+0.0994, 1st-half IC=+0.1721, 2nd-half IC=+0.1276, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.234, Q2=-0.019, Q3_mid=+0.145, Q4=+0.172, Q5_high_vol=+0.189

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0881, Sharpe=+0.2537)
- Admission: Train IC=+0.2637, Deflated=+0.2634, IR=0.82, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.072 | 2017: +0.182 | 2018: +0.187 | 2019: +0.123 | 2020: +0.124 | 2021: +0.132 | 2022: +0.077 | 2023: +0.131 | 2024: +0.143 | 2025: +0.123 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.365 | 2016: +0.258 | 2017: +0.294 | 2018: +0.281 | 2019: +0.289 | 2020: +0.215 | 2021: +0.274 | 2022: +0.275 | 2023: +0.318 | 2024: +0.162 | 2025: +0.001 | 2026: -0.057
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.82
- Early IC=+0.1272, Recent IC=+0.1038, 1st-half IC=+0.1312, 2nd-half IC=+0.1181, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.009, Q3_mid=+0.129, Q4=+0.099, Q5_high_vol=+0.190

**`combo_mean__close_vs_open_range__first_bar_return`** (Lock IC=+0.0927, Sharpe=+0.2533)
- Admission: Train IC=+0.2087, Deflated=+0.2093, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.100 | 2017: +0.214 | 2018: +0.205 | 2019: +0.110 | 2020: +0.114 | 2021: +0.101 | 2022: +0.096 | 2023: +0.080 | 2024: +0.151 | 2025: +0.114 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.042 | 2017: +0.267 | 2018: +0.355 | 2019: +0.134 | 2020: +0.183 | 2021: +0.361 | 2022: +0.268 | 2023: +0.228 | 2024: +0.310 | 2025: +0.016 | 2026: -0.244
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.56
- Early IC=+0.1570, Recent IC=+0.0884, 1st-half IC=+0.1518, 2nd-half IC=+0.1005, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.214, Q2=-0.029, Q3_mid=+0.119, Q4=+0.137, Q5_high_vol=+0.151

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0557, Sharpe=+0.2440)
- Admission: Train IC=+0.1831, Deflated=+0.1835, IR=0.51, Mono=0.71, p=0.0002, MaxCorr=0.86
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
- Admission: Train IC=+0.2055, Deflated=+0.2058, IR=0.54, Mono=0.70, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143 | 2025: +0.080 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.194 | 2017: +0.220 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.134 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.64
- Early IC=+0.1558, Recent IC=+0.0999, 1st-half IC=+0.1344, 2nd-half IC=+0.1246, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.009, Q3_mid=+0.112, Q4=+0.124, Q5_high_vol=+0.222

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0811, Sharpe=+0.2357)
- Admission: Train IC=+0.2055, Deflated=+0.2047, IR=0.47, Mono=0.69, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.114 | 2017: +0.107 | 2018: +0.255 | 2019: +0.109 | 2020: +0.103 | 2021: +0.172 | 2022: +0.094 | 2023: +0.059 | 2024: +0.145 | 2025: +0.077 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.204 | 2017: +0.171 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.101 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.69
- Early IC=+0.1105, Recent IC=+0.0765, 1st-half IC=+0.1441, 2nd-half IC=+0.1103, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.014, Q3_mid=+0.104, Q4=+0.151, Q5_high_vol=+0.206

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0890, Sharpe=+0.2357)
- Admission: Train IC=+0.2198, Deflated=+0.2196, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.106 | 2017: +0.230 | 2018: +0.211 | 2019: +0.100 | 2020: +0.170 | 2021: +0.128 | 2022: +0.107 | 2023: +0.083 | 2024: +0.144 | 2025: +0.080 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.220 | 2016: +0.237 | 2017: +0.252 | 2018: +0.369 | 2019: +0.146 | 2020: +0.155 | 2021: +0.293 | 2022: +0.081 | 2023: +0.210 | 2024: +0.250 | 2025: -0.119 | 2026: -0.313
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.57
- Early IC=+0.1682, Recent IC=+0.0955, 1st-half IC=+0.1602, 2nd-half IC=+0.1260, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.208, Q2=-0.019, Q3_mid=+0.120, Q4=+0.161, Q5_high_vol=+0.217

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

**`combo_rank_max__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1033, Sharpe=+0.2208)
- Admission: Train IC=+0.1638, Deflated=+0.1632, IR=0.45, Mono=0.66, p=0.0016, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.085 | 2017: +0.158 | 2018: +0.159 | 2019: +0.103 | 2020: +0.101 | 2021: +0.037 | 2022: +0.140 | 2023: +0.077 | 2024: +0.103 | 2025: +0.083 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.196 | 2017: +0.154 | 2018: +0.098 | 2019: +0.233 | 2020: +0.066 | 2021: +0.225 | 2022: +0.189 | 2023: +0.098 | 2024: +0.144 | 2025: +0.017 | 2026: -0.237
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.89
- Early IC=+0.1242, Recent IC=+0.1109, 1st-half IC=+0.1242, 2nd-half IC=+0.0913, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.016, Q3_mid=+0.085, Q4=+0.123, Q5_high_vol=+0.136

**`combo_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0905, Sharpe=+0.2175)
- Admission: Train IC=+0.1321, Deflated=+0.1322, IR=0.51, Mono=0.67, p=0.0094, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.304 | 2016: +0.095 | 2017: +0.190 | 2018: +0.166 | 2019: +0.133 | 2020: +0.110 | 2021: +0.099 | 2022: +0.075 | 2023: +0.049 | 2024: +0.081 | 2025: +0.143 | 2026: +0.036
- Yearly Tail ICs:   2015: +0.346 | 2016: -0.013 | 2017: +0.170 | 2018: +0.102 | 2019: +0.322 | 2020: +0.060 | 2021: +0.310 | 2022: +0.141 | 2023: +0.146 | 2024: +0.230 | 2025: +0.233 | 2026: +0.035
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.55, Recency ratio=0.43
- Early IC=+0.1424, Recent IC=+0.0618, 1st-half IC=+0.1431, 2nd-half IC=+0.0791, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.031, Q3_mid=+0.106, Q4=+0.165, Q5_high_vol=+0.128

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0905, Sharpe=+0.2004)
- Admission: Train IC=+0.2278, Deflated=+0.2275, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.089 | 2017: +0.213 | 2018: +0.253 | 2019: +0.158 | 2020: +0.134 | 2021: +0.097 | 2022: +0.055 | 2023: +0.067 | 2024: +0.122 | 2025: +0.109 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.397 | 2016: +0.098 | 2017: +0.365 | 2018: +0.409 | 2019: +0.190 | 2020: +0.133 | 2021: +0.319 | 2022: +0.280 | 2023: +0.145 | 2024: +0.171 | 2025: +0.057 | 2026: -0.142
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.41
- Early IC=+0.1509, Recent IC=+0.0613, 1st-half IC=+0.1770, 2nd-half IC=+0.0888, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.153, Q2=-0.019, Q3_mid=+0.135, Q4=+0.169, Q5_high_vol=+0.172

**`combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0816, Sharpe=+0.1952)
- Admission: Train IC=+0.1994, Deflated=+0.1992, IR=0.42, Mono=0.67, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.048 | 2017: +0.189 | 2018: +0.137 | 2019: +0.081 | 2020: +0.097 | 2021: +0.076 | 2022: +0.086 | 2023: +0.090 | 2024: +0.109 | 2025: +0.150 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.367 | 2016: +0.083 | 2017: +0.291 | 2018: +0.187 | 2019: +0.184 | 2020: +0.207 | 2021: +0.242 | 2022: +0.195 | 2023: +0.113 | 2024: +0.246 | 2025: +0.119 | 2026: -0.312
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.75
- Early IC=+0.1184, Recent IC=+0.0882, 1st-half IC=+0.1148, 2nd-half IC=+0.0869, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.022, Q3_mid=+0.106, Q4=+0.110, Q5_high_vol=+0.128

**`trend_strength_intraday`** (Lock IC=+0.0894, Sharpe=+0.1836)
- Admission: Train IC=+0.1217, Deflated=+0.1211, IR=0.36, Mono=0.67, p=0.0154, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.077 | 2016: +0.103 | 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083 | 2024: +0.141 | 2025: +0.117 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.253 | 2017: +0.002 | 2018: +0.082 | 2019: +0.121 | 2020: +0.184 | 2021: -0.075 | 2022: +0.221 | 2023: +0.122 | 2024: +0.211 | 2025: -0.019 | 2026: -0.077
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.93, Recency ratio=1.36
- Early IC=+0.0785, Recent IC=+0.1070, 1st-half IC=+0.0864, 2nd-half IC=+0.0807, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.004, Q3_mid=+0.111, Q4=+0.111, Q5_high_vol=+0.092

**`combo_mean__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0916, Sharpe=+0.1735)
- Admission: Train IC=+0.2011, Deflated=+0.2014, IR=0.46, Mono=0.66, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.108 | 2017: +0.180 | 2018: +0.170 | 2019: +0.095 | 2020: +0.111 | 2021: +0.093 | 2022: +0.102 | 2023: +0.077 | 2024: +0.138 | 2025: +0.131 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.391 | 2016: +0.152 | 2017: +0.229 | 2018: +0.189 | 2019: +0.174 | 2020: +0.145 | 2021: +0.185 | 2022: +0.233 | 2023: +0.151 | 2024: +0.160 | 2025: +0.061 | 2026: +0.005
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.62
- Early IC=+0.1441, Recent IC=+0.0892, 1st-half IC=+0.1331, 2nd-half IC=+0.0965, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.026, Q3_mid=+0.102, Q4=+0.149, Q5_high_vol=+0.136

**`combo_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0885, Sharpe=+0.1705)
- Admission: Train IC=+0.2188, Deflated=+0.2187, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.077 | 2017: +0.184 | 2018: +0.143 | 2019: +0.087 | 2020: +0.104 | 2021: +0.128 | 2022: +0.108 | 2023: +0.113 | 2024: +0.140 | 2025: +0.149 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.122 | 2017: +0.314 | 2018: +0.286 | 2019: +0.204 | 2020: +0.236 | 2021: +0.190 | 2022: +0.197 | 2023: +0.317 | 2024: +0.188 | 2025: +0.068 | 2026: -0.099
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=0.85
- Early IC=+0.1306, Recent IC=+0.1106, 1st-half IC=+0.1110, 2nd-half IC=+0.1159, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.001, Q3_mid=+0.109, Q4=+0.103, Q5_high_vol=+0.157

**`combo_min__close_vs_open_range__max_down_ret`** (Lock IC=+0.1016, Sharpe=+0.1701)
- Admission: Train IC=+0.1540, Deflated=+0.1540, IR=0.54, Mono=0.70, p=0.0038, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.070 | 2017: +0.219 | 2018: +0.119 | 2019: +0.084 | 2020: +0.133 | 2021: +0.048 | 2022: +0.083 | 2023: +0.080 | 2024: +0.114 | 2025: +0.140 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.326 | 2016: -0.017 | 2017: +0.240 | 2018: +0.164 | 2019: +0.172 | 2020: +0.101 | 2021: +0.345 | 2022: +0.303 | 2023: +0.139 | 2024: +0.158 | 2025: +0.149 | 2026: +0.035
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.56
- Early IC=+0.1443, Recent IC=+0.0814, 1st-half IC=+0.1199, 2nd-half IC=+0.0856, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.057, Q3_mid=+0.133, Q4=+0.104, Q5_high_vol=+0.127

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

**`combo_rank_max__close_vs_open_range__first_bar_return`** (Lock IC=+0.0752, Sharpe=+0.1487)
- Admission: Train IC=+0.2161, Deflated=+0.2169, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.113 | 2017: +0.209 | 2018: +0.216 | 2019: +0.103 | 2020: +0.141 | 2021: +0.128 | 2022: +0.124 | 2023: +0.086 | 2024: +0.140 | 2025: +0.119 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.042 | 2017: +0.263 | 2018: +0.327 | 2019: +0.151 | 2020: +0.314 | 2021: +0.258 | 2022: +0.267 | 2023: +0.316 | 2024: +0.271 | 2025: -0.123 | 2026: -0.469
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.66
- Early IC=+0.1617, Recent IC=+0.1060, 1st-half IC=+0.1523, 2nd-half IC=+0.1240, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.011, Q3_mid=+0.146, Q4=+0.151, Q5_high_vol=+0.164

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0730, Sharpe=+0.1410)
- Admission: Train IC=+0.1953, Deflated=+0.1950, IR=0.52, Mono=0.66, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.088 | 2017: +0.170 | 2018: +0.201 | 2019: +0.048 | 2020: +0.126 | 2021: +0.035 | 2022: +0.141 | 2023: +0.091 | 2024: +0.063 | 2025: +0.077 | 2026: +0.075
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.409 | 2017: +0.082 | 2018: +0.298 | 2019: +0.059 | 2020: +0.129 | 2021: +0.231 | 2022: +0.124 | 2023: +0.108 | 2024: +0.121 | 2025: -0.120 | 2026: -0.127
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.90
- Early IC=+0.1292, Recent IC=+0.1159, 1st-half IC=+0.1218, 2nd-half IC=+0.1031, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.014, Q3_mid=+0.091, Q4=+0.114, Q5_high_vol=+0.192

**`combo_min__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0828, Sharpe=+0.1020)
- Admission: Train IC=+0.1476, Deflated=+0.1482, IR=0.45, Mono=0.67, p=0.0050, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.112 | 2017: +0.180 | 2018: +0.155 | 2019: +0.090 | 2020: +0.119 | 2021: +0.071 | 2022: +0.067 | 2023: +0.063 | 2024: +0.105 | 2025: +0.146 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.382 | 2016: +0.005 | 2017: +0.278 | 2018: +0.127 | 2019: +0.118 | 2020: +0.156 | 2021: +0.227 | 2022: +0.102 | 2023: +0.122 | 2024: +0.143 | 2025: +0.188 | 2026: +0.146
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.44
- Early IC=+0.1462, Recent IC=+0.0650, 1st-half IC=+0.1324, 2nd-half IC=+0.0802, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.027, Q3_mid=+0.075, Q4=+0.154, Q5_high_vol=+0.124

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0818, Sharpe=+0.0961)
- Admission: Train IC=+0.2061, Deflated=+0.2067, IR=0.57, Mono=0.69, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.094 | 2017: +0.257 | 2018: +0.230 | 2019: +0.145 | 2020: +0.132 | 2021: +0.089 | 2022: +0.091 | 2023: +0.045 | 2024: +0.124 | 2025: +0.108 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.012 | 2017: +0.235 | 2018: +0.426 | 2019: +0.114 | 2020: +0.240 | 2021: +0.196 | 2022: +0.200 | 2023: +0.229 | 2024: +0.223 | 2025: +0.035 | 2026: -0.250
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.39
- Early IC=+0.1753, Recent IC=+0.0679, 1st-half IC=+0.1733, 2nd-half IC=+0.0874, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.060, Q3_mid=+0.140, Q4=+0.161, Q5_high_vol=+0.151

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=+0.0856, Sharpe=+0.0926)
- Admission: Train IC=+0.2288, Deflated=+0.2293, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.62
- Early IC=+0.1532, Recent IC=+0.0956, 1st-half IC=+0.1514, 2nd-half IC=+0.1182, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.008, Q3_mid=+0.106, Q4=+0.148, Q5_high_vol=+0.216

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.0778, Sharpe=+0.0854)
- Admission: Train IC=+0.2133, Deflated=+0.2138, IR=0.55, Mono=0.68, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.179 | 2017: +0.097 | 2018: +0.117 | 2019: +0.074 | 2020: +0.116 | 2021: +0.072 | 2022: +0.081 | 2023: +0.140 | 2024: +0.144 | 2025: +0.074 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.197 | 2017: +0.338 | 2018: +0.242 | 2019: +0.176 | 2020: +0.135 | 2021: +0.250 | 2022: +0.134 | 2023: +0.076 | 2024: +0.255 | 2025: -0.130 | 2026: +0.008
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.80
- Early IC=+0.1379, Recent IC=+0.1108, 1st-half IC=+0.1130, 2nd-half IC=+0.1000, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.003, Q3_mid=+0.061, Q4=+0.092, Q5_high_vol=+0.206

**`combo_mean__net_volume_flow__first_bar_return`** (Lock IC=+0.0871, Sharpe=+0.0841)
- Admission: Train IC=+0.2230, Deflated=+0.2235, IR=0.51, Mono=0.67, p=0.0000, MaxCorr=0.92
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

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0747, Sharpe=+0.0706)
- Admission: Train IC=+0.2676, Deflated=+0.2677, IR=0.95, Mono=0.79, p=0.0000, MaxCorr=0.76
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

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0678, Sharpe=+0.0596)
- Admission: Train IC=+0.1853, Deflated=+0.1856, IR=0.56, Mono=0.68, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.099 | 2017: +0.220 | 2018: +0.122 | 2019: +0.031 | 2020: +0.133 | 2021: +0.051 | 2022: +0.127 | 2023: +0.104 | 2024: +0.127 | 2025: +0.093 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.293 | 2017: +0.353 | 2018: +0.243 | 2019: -0.041 | 2020: +0.184 | 2021: +0.214 | 2022: +0.092 | 2023: +0.139 | 2024: +0.215 | 2025: -0.051 | 2026: -0.181
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=1.09, Recency ratio=0.72
- Early IC=+0.1598, Recent IC=+0.1156, 1st-half IC=+0.1031, 2nd-half IC=+0.1120, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.017, Q3_mid=+0.105, Q4=+0.091, Q5_high_vol=+0.170

**`combo_max__close_vs_open_range__first_bar_return`** (Lock IC=+0.0749, Sharpe=+0.0494)
- Admission: Train IC=+0.2195, Deflated=+0.2202, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.109 | 2017: +0.209 | 2018: +0.218 | 2019: +0.101 | 2020: +0.141 | 2021: +0.125 | 2022: +0.123 | 2023: +0.085 | 2024: +0.136 | 2025: +0.121 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.043 | 2017: +0.258 | 2018: +0.337 | 2019: +0.164 | 2020: +0.276 | 2021: +0.244 | 2022: +0.235 | 2023: +0.337 | 2024: +0.264 | 2025: -0.124 | 2026: -0.473
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.66
- Early IC=+0.1588, Recent IC=+0.1040, 1st-half IC=+0.1509, 2nd-half IC=+0.1240, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.015, Q3_mid=+0.149, Q4=+0.150, Q5_high_vol=+0.167

**`combo_mean__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0775, Sharpe=+0.0450)
- Admission: Train IC=+0.1989, Deflated=+0.1991, IR=0.52, Mono=0.73, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.104 | 2017: +0.127 | 2018: +0.184 | 2019: +0.081 | 2020: +0.101 | 2021: +0.093 | 2022: +0.118 | 2023: +0.075 | 2024: +0.116 | 2025: +0.125 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.146 | 2017: +0.117 | 2018: +0.232 | 2019: +0.159 | 2020: +0.244 | 2021: +0.142 | 2022: +0.211 | 2023: +0.215 | 2024: +0.162 | 2025: +0.111 | 2026: -0.122
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.83
- Early IC=+0.1159, Recent IC=+0.0965, 1st-half IC=+0.1240, 2nd-half IC=+0.0966, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.176, Q2=-0.026, Q3_mid=+0.106, Q4=+0.162, Q5_high_vol=+0.126

### 159915ETF — `single` True Positives

**`combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1211, Sharpe=+1.8009)
- Admission: Train IC=+0.2717, Deflated=+0.2715, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.097 | 2017: -0.036 | 2018: +0.130 | 2019: +0.263 | 2020: +0.156 | 2021: +0.130 | 2022: +0.052 | 2023: +0.128 | 2024: +0.113 | 2025: +0.129 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.181 | 2016: +0.136 | 2017: +0.014 | 2018: +0.405 | 2019: +0.480 | 2020: +0.428 | 2021: +0.287 | 2022: +0.206 | 2023: +0.320 | 2024: +0.421 | 2025: +0.189 | 2026: +0.364
- IC CV=0.69, Neg years (linear/tail)=1/0 of 8, Half ratio=1.00, Recency ratio=2.95
- Early IC=+0.0306, Recent IC=+0.0902, 1st-half IC=+0.1217, 2nd-half IC=+0.1217, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.103, Q3_mid=+0.091, Q4=+0.118, Q5_high_vol=+0.176

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

**`combo_mean__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1241, Sharpe=+1.6362)
- Admission: Train IC=+0.2583, Deflated=+0.2585, IR=0.55, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.112 | 2017: -0.022 | 2018: +0.156 | 2019: +0.227 | 2020: +0.153 | 2021: +0.145 | 2022: +0.111 | 2023: +0.117 | 2024: +0.082 | 2025: +0.141 | 2026: +0.142
- Yearly Tail ICs:   2015: +0.040 | 2016: +0.159 | 2017: +0.108 | 2018: +0.399 | 2019: +0.448 | 2020: +0.244 | 2021: +0.293 | 2022: +0.157 | 2023: +0.105 | 2024: +0.407 | 2025: +0.211 | 2026: +0.233
- IC CV=0.53, Neg years (linear/tail)=1/0 of 8, Half ratio=1.09, Recency ratio=2.52
- Early IC=+0.0452, Recent IC=+0.1137, 1st-half IC=+0.1236, 2nd-half IC=+0.1346, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.098, Q3_mid=+0.094, Q4=+0.134, Q5_high_vol=+0.185

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1190, Sharpe=+1.6230)
- Admission: Train IC=+0.2626, Deflated=+0.2623, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.158 | 2017: -0.015 | 2018: +0.161 | 2019: +0.233 | 2020: +0.183 | 2021: +0.134 | 2022: +0.113 | 2023: +0.122 | 2024: +0.087 | 2025: +0.145 | 2026: +0.115
- Yearly Tail ICs:   2015: -0.005 | 2016: +0.185 | 2017: +0.029 | 2018: +0.323 | 2019: +0.437 | 2020: +0.320 | 2021: +0.297 | 2022: +0.239 | 2023: +0.222 | 2024: +0.480 | 2025: +0.236 | 2026: +0.234
- IC CV=0.49, Neg years (linear/tail)=1/0 of 8, Half ratio=1.01, Recency ratio=1.64
- Early IC=+0.0716, Recent IC=+0.1177, 1st-half IC=+0.1393, 2nd-half IC=+0.1411, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.115, Q3_mid=+0.103, Q4=+0.138, Q5_high_vol=+0.205

**`combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1316, Sharpe=+1.5821)
- Admission: Train IC=+0.2883, Deflated=+0.2887, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.148 | 2016: +0.125 | 2017: +0.004 | 2018: +0.128 | 2019: +0.223 | 2020: +0.061 | 2021: +0.180 | 2022: +0.048 | 2023: +0.147 | 2024: +0.127 | 2025: +0.139 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.019 | 2016: +0.051 | 2017: +0.132 | 2018: +0.244 | 2019: +0.585 | 2020: +0.296 | 2021: +0.365 | 2022: +0.176 | 2023: +0.386 | 2024: +0.272 | 2025: +0.163 | 2026: +0.287
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=1.51
- Early IC=+0.0646, Recent IC=+0.0975, 1st-half IC=+0.1268, 2nd-half IC=+0.1187, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.141, Q3_mid=+0.089, Q4=+0.132, Q5_high_vol=+0.172

**`combo_mean__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1191, Sharpe=+1.5664)
- Admission: Train IC=+0.2314, Deflated=+0.2317, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.090 | 2017: +0.001 | 2018: +0.170 | 2019: +0.205 | 2020: +0.134 | 2021: +0.155 | 2022: +0.119 | 2023: +0.143 | 2024: +0.066 | 2025: +0.155 | 2026: +0.120
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.055 | 2017: +0.144 | 2018: +0.382 | 2019: +0.384 | 2020: +0.173 | 2021: +0.375 | 2022: +0.108 | 2023: +0.107 | 2024: +0.396 | 2025: +0.173 | 2026: +0.228
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=2.90
- Early IC=+0.0452, Recent IC=+0.1311, 1st-half IC=+0.1202, 2nd-half IC=+0.1376, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.132, Q3_mid=+0.090, Q4=+0.118, Q5_high_vol=+0.193

**`combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1290, Sharpe=+1.5409)
- Admission: Train IC=+0.2508, Deflated=+0.2511, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.082 | 2017: -0.040 | 2018: +0.111 | 2019: +0.257 | 2020: +0.138 | 2021: +0.121 | 2022: +0.073 | 2023: +0.149 | 2024: +0.103 | 2025: +0.151 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.103 | 2017: -0.014 | 2018: +0.321 | 2019: +0.489 | 2020: +0.243 | 2021: +0.357 | 2022: +0.252 | 2023: +0.349 | 2024: +0.388 | 2025: +0.111 | 2026: +0.259
- IC CV=0.70, Neg years (linear/tail)=1/1 of 8, Half ratio=1.13, Recency ratio=5.27
- Early IC=+0.0211, Recent IC=+0.1112, 1st-half IC=+0.1072, 2nd-half IC=+0.1209, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.112, Q3_mid=+0.092, Q4=+0.104, Q5_high_vol=+0.165

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

**`combo_min__first_bar_return__limit_down_proximity_early`** (Lock IC=+0.1269, Sharpe=+1.4730)
- Admission: Train IC=+0.1899, Deflated=+0.1902, IR=0.58, Mono=0.68, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.055 | 2017: -0.026 | 2018: +0.081 | 2019: +0.250 | 2020: +0.118 | 2021: +0.095 | 2022: +0.058 | 2023: +0.124 | 2024: +0.082 | 2025: +0.153 | 2026: +0.123
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.045 | 2017: +0.023 | 2018: +0.253 | 2019: +0.508 | 2020: +0.137 | 2021: +0.354 | 2022: +0.258 | 2023: +0.130 | 2024: +0.445 | 2025: +0.051 | 2026: +0.310
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.02, Recency ratio=6.36
- Early IC=+0.0143, Recent IC=+0.0909, 1st-half IC=+0.0935, 2nd-half IC=+0.0958, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.092, Q3_mid=+0.080, Q4=+0.089, Q5_high_vol=+0.112

**`combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0954, Sharpe=+1.4524)
- Admission: Train IC=+0.2330, Deflated=+0.2322, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.149 | 2017: -0.018 | 2018: +0.115 | 2019: +0.238 | 2020: +0.171 | 2021: +0.075 | 2022: +0.082 | 2023: +0.094 | 2024: +0.062 | 2025: +0.117 | 2026: +0.094
- Yearly Tail ICs:   2015: -0.031 | 2016: +0.335 | 2017: +0.111 | 2018: -0.012 | 2019: +0.495 | 2020: +0.181 | 2021: -0.167 | 2022: +0.351 | 2023: +0.241 | 2024: +0.294 | 2025: +0.088 | 2026: +0.250
- IC CV=0.63, Neg years (linear/tail)=1/2 of 8, Half ratio=0.85, Recency ratio=1.33
- Early IC=+0.0659, Recent IC=+0.0877, 1st-half IC=+0.1308, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.125, Q3_mid=+0.099, Q4=+0.106, Q5_high_vol=+0.156

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1321, Sharpe=+1.4384)
- Admission: Train IC=+0.2752, Deflated=+0.2752, IR=0.94, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.079 | 2017: -0.005 | 2018: +0.082 | 2019: +0.155 | 2020: +0.093 | 2021: +0.184 | 2022: +0.120 | 2023: +0.154 | 2024: +0.083 | 2025: +0.210 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.049 | 2016: +0.286 | 2017: +0.150 | 2018: +0.244 | 2019: +0.341 | 2020: +0.308 | 2021: +0.283 | 2022: +0.244 | 2023: +0.337 | 2024: +0.448 | 2025: +0.357 | 2026: +0.173
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.90, Recency ratio=3.73
- Early IC=+0.0368, Recent IC=+0.1372, 1st-half IC=+0.0764, 2nd-half IC=+0.1448, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.150, Q3_mid=+0.077, Q4=+0.114, Q5_high_vol=+0.152

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

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1230, Sharpe=+1.4125)
- Admission: Train IC=+0.2331, Deflated=+0.2329, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.128 | 2017: +0.040 | 2018: +0.079 | 2019: +0.202 | 2020: +0.143 | 2021: +0.154 | 2022: +0.127 | 2023: +0.149 | 2024: +0.087 | 2025: +0.184 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.244 | 2017: +0.127 | 2018: +0.260 | 2019: +0.333 | 2020: +0.232 | 2021: +0.294 | 2022: +0.371 | 2023: +0.221 | 2024: +0.310 | 2025: +0.215 | 2026: +0.140
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.38, Recency ratio=1.64
- Early IC=+0.0842, Recent IC=+0.1378, 1st-half IC=+0.1083, 2nd-half IC=+0.1495, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.152, Q3_mid=+0.136, Q4=+0.104, Q5_high_vol=+0.139

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

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0983, Sharpe=+1.3740)
- Admission: Train IC=+0.2572, Deflated=+0.2565, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.167 | 2017: -0.010 | 2018: +0.175 | 2019: +0.214 | 2020: +0.183 | 2021: +0.105 | 2022: +0.056 | 2023: +0.102 | 2024: +0.063 | 2025: +0.137 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.176 | 2016: +0.259 | 2017: +0.130 | 2018: +0.383 | 2019: +0.363 | 2020: +0.239 | 2021: +0.176 | 2022: +0.243 | 2023: +0.153 | 2024: +0.242 | 2025: +0.356 | 2026: +0.147
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=0.78, Recency ratio=1.01
- Early IC=+0.0783, Recent IC=+0.0792, 1st-half IC=+0.1445, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.114, Q3_mid=+0.081, Q4=+0.117, Q5_high_vol=+0.197

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1277, Sharpe=+1.2801)
- Admission: Train IC=+0.3031, Deflated=+0.3031, IR=0.79, Mono=0.78, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.121 | 2017: -0.012 | 2018: +0.160 | 2019: +0.257 | 2020: +0.175 | 2021: +0.138 | 2022: +0.085 | 2023: +0.153 | 2024: +0.094 | 2025: +0.162 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.087 | 2016: +0.190 | 2017: +0.035 | 2018: +0.423 | 2019: +0.551 | 2020: +0.375 | 2021: +0.314 | 2022: +0.215 | 2023: +0.351 | 2024: +0.447 | 2025: +0.293 | 2026: +0.293
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=1.04, Recency ratio=2.19
- Early IC=+0.0543, Recent IC=+0.1189, 1st-half IC=+0.1372, 2nd-half IC=+0.1421, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.142, Q3_mid=+0.099, Q4=+0.126, Q5_high_vol=+0.209

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1068, Sharpe=+1.2738)
- Admission: Train IC=+0.2809, Deflated=+0.2804, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.103 | 2017: -0.025 | 2018: +0.171 | 2019: +0.219 | 2020: +0.162 | 2021: +0.133 | 2022: +0.079 | 2023: +0.140 | 2024: +0.104 | 2025: +0.130 | 2026: +0.068
- Yearly Tail ICs:   2015: +0.237 | 2016: +0.111 | 2017: +0.064 | 2018: +0.454 | 2019: +0.477 | 2020: +0.335 | 2021: +0.259 | 2022: +0.282 | 2023: +0.356 | 2024: +0.269 | 2025: +0.194 | 2026: +0.437
- IC CV=0.56, Neg years (linear/tail)=1/0 of 8, Half ratio=1.02, Recency ratio=2.80
- Early IC=+0.0391, Recent IC=+0.1097, 1st-half IC=+0.1291, 2nd-half IC=+0.1311, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.121, Q3_mid=+0.105, Q4=+0.150, Q5_high_vol=+0.163

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1249, Sharpe=+1.2583)
- Admission: Train IC=+0.2224, Deflated=+0.2216, IR=0.54, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.113 | 2017: +0.019 | 2018: +0.094 | 2019: +0.229 | 2020: +0.134 | 2021: +0.137 | 2022: +0.100 | 2023: +0.163 | 2024: +0.072 | 2025: +0.221 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.385 | 2016: +0.093 | 2017: +0.045 | 2018: +0.145 | 2019: +0.448 | 2020: +0.312 | 2021: +0.229 | 2022: +0.152 | 2023: +0.409 | 2024: +0.330 | 2025: +0.355 | 2026: +0.143
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=2.00
- Early IC=+0.0657, Recent IC=+0.1317, 1st-half IC=+0.1113, 2nd-half IC=+0.1374, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.148, Q3_mid=+0.100, Q4=+0.105, Q5_high_vol=+0.177

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

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1042, Sharpe=+1.2122)
- Admission: Train IC=+0.1458, Deflated=+0.1452, IR=0.33, Mono=0.67, p=0.0050, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.021 | 2017: +0.033 | 2018: +0.073 | 2019: +0.158 | 2020: +0.050 | 2021: +0.127 | 2022: +0.136 | 2023: +0.121 | 2024: +0.109 | 2025: +0.108 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.067 | 2017: +0.104 | 2018: +0.076 | 2019: +0.356 | 2020: -0.022 | 2021: +0.237 | 2022: +0.053 | 2023: +0.176 | 2024: +0.309 | 2025: +0.181 | 2026: -0.043
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.46, Recency ratio=4.49
- Early IC=+0.0293, Recent IC=+0.1318, 1st-half IC=+0.0745, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.104, Q3_mid=+0.054, Q4=+0.109, Q5_high_vol=+0.124

**`combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1284, Sharpe=+1.2074)
- Admission: Train IC=+0.2219, Deflated=+0.2223, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.065 | 2017: +0.040 | 2018: +0.108 | 2019: +0.112 | 2020: +0.057 | 2021: +0.163 | 2022: +0.116 | 2023: +0.145 | 2024: +0.097 | 2025: +0.194 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.190 | 2017: +0.168 | 2018: +0.349 | 2019: +0.262 | 2020: +0.160 | 2021: +0.352 | 2022: +0.105 | 2023: +0.072 | 2024: +0.280 | 2025: +0.350 | 2026: +0.183
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.61, Recency ratio=2.48
- Early IC=+0.0526, Recent IC=+0.1308, 1st-half IC=+0.0766, 2nd-half IC=+0.1230, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.136, Q3_mid=+0.070, Q4=+0.122, Q5_high_vol=+0.124

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1291, Sharpe=+1.1684)
- Admission: Train IC=+0.2593, Deflated=+0.2594, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.49, Neg years (linear/tail)=1/0 of 8, Half ratio=1.95, Recency ratio=3.70
- Early IC=+0.0401, Recent IC=+0.1487, 1st-half IC=+0.0767, 2nd-half IC=+0.1493, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.154, Q3_mid=+0.073, Q4=+0.110, Q5_high_vol=+0.155

**`combo_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1062, Sharpe=+1.1247)
- Admission: Train IC=+0.2499, Deflated=+0.2499, IR=0.48, Mono=0.70, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.044 | 2017: +0.016 | 2018: +0.125 | 2019: +0.186 | 2020: +0.109 | 2021: +0.159 | 2022: +0.127 | 2023: +0.159 | 2024: +0.057 | 2025: +0.195 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.140 | 2016: -0.041 | 2017: +0.085 | 2018: +0.164 | 2019: +0.410 | 2020: +0.237 | 2021: +0.303 | 2022: +0.269 | 2023: +0.302 | 2024: +0.256 | 2025: +0.291 | 2026: -0.059
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=1.52, Recency ratio=4.78
- Early IC=+0.0299, Recent IC=+0.1429, 1st-half IC=+0.0947, 2nd-half IC=+0.1442, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.141, Q3_mid=+0.100, Q4=+0.093, Q5_high_vol=+0.177

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

**`combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1250, Sharpe=+1.0832)
- Admission: Train IC=+0.1965, Deflated=+0.1966, IR=0.49, Mono=0.67, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.060 | 2017: +0.021 | 2018: +0.105 | 2019: +0.114 | 2020: +0.130 | 2021: +0.159 | 2022: +0.162 | 2023: +0.129 | 2024: +0.097 | 2025: +0.159 | 2026: +0.102
- Yearly Tail ICs:   2015: -0.045 | 2016: +0.146 | 2017: +0.093 | 2018: +0.168 | 2019: +0.293 | 2020: +0.166 | 2021: +0.344 | 2022: +0.169 | 2023: +0.072 | 2024: +0.188 | 2025: +0.052 | 2026: +0.077
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=2.08, Recency ratio=3.62
- Early IC=+0.0402, Recent IC=+0.1452, 1st-half IC=+0.0729, 2nd-half IC=+0.1512, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.113, Q3_mid=+0.077, Q4=+0.138, Q5_high_vol=+0.151

**`combo_z_sum__limit_down_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1254, Sharpe=+1.0792)
- Admission: Train IC=+0.1757, Deflated=+0.1759, IR=0.39, Mono=0.66, p=0.0010, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.060 | 2017: +0.036 | 2018: +0.120 | 2019: +0.221 | 2020: +0.040 | 2021: +0.168 | 2022: +0.043 | 2023: +0.112 | 2024: +0.095 | 2025: +0.141 | 2026: +0.121
- Yearly Tail ICs:   2015: +0.157 | 2016: -0.109 | 2017: +0.135 | 2018: +0.141 | 2019: +0.574 | 2020: +0.091 | 2021: +0.329 | 2022: +0.112 | 2023: +0.291 | 2024: +0.310 | 2025: +0.149 | 2026: +0.183
- IC CV=0.64, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=1.62
- Early IC=+0.0479, Recent IC=+0.0776, 1st-half IC=+0.1146, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.086, Q3_mid=+0.098, Q4=+0.128, Q5_high_vol=+0.119

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1167, Sharpe=+1.0752)
- Admission: Train IC=+0.2501, Deflated=+0.2503, IR=0.66, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.097 | 2017: -0.005 | 2018: +0.154 | 2019: +0.240 | 2020: +0.146 | 2021: +0.129 | 2022: +0.097 | 2023: +0.137 | 2024: +0.073 | 2025: +0.160 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.085 | 2017: +0.080 | 2018: +0.318 | 2019: +0.490 | 2020: +0.224 | 2021: +0.271 | 2022: +0.240 | 2023: +0.208 | 2024: +0.388 | 2025: +0.136 | 2026: +0.252
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.02, Recency ratio=2.55
- Early IC=+0.0460, Recent IC=+0.1172, 1st-half IC=+0.1276, 2nd-half IC=+0.1302, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.146, Q3_mid=+0.084, Q4=+0.112, Q5_high_vol=+0.199

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1301, Sharpe=+1.0434)
- Admission: Train IC=+0.2370, Deflated=+0.2374, IR=0.49, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.117 | 2017: +0.051 | 2018: +0.143 | 2019: +0.214 | 2020: +0.108 | 2021: +0.210 | 2022: +0.079 | 2023: +0.124 | 2024: +0.107 | 2025: +0.160 | 2026: +0.108
- Yearly Tail ICs:   2015: -0.127 | 2016: +0.133 | 2017: +0.192 | 2018: +0.253 | 2019: +0.576 | 2020: +0.092 | 2021: +0.337 | 2022: +0.147 | 2023: +0.276 | 2024: +0.299 | 2025: +0.121 | 2026: +0.144
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.21
- Early IC=+0.0836, Recent IC=+0.1012, 1st-half IC=+0.1343, 2nd-half IC=+0.1384, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.121, Q3_mid=+0.099, Q4=+0.165, Q5_high_vol=+0.185

**`combo_mean__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1330, Sharpe=+1.0200)
- Admission: Train IC=+0.2348, Deflated=+0.2361, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.105 | 2017: -0.075 | 2018: +0.110 | 2019: +0.118 | 2020: +0.092 | 2021: +0.055 | 2022: +0.169 | 2023: +0.133 | 2024: +0.104 | 2025: +0.108 | 2026: +0.178
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.139 | 2017: +0.142 | 2018: +0.376 | 2019: +0.308 | 2020: +0.278 | 2021: +0.226 | 2022: +0.365 | 2023: +0.097 | 2024: +0.122 | 2025: +0.178 | 2026: +0.303
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.49, Recency ratio=10.17
- Early IC=+0.0149, Recent IC=+0.1510, 1st-half IC=+0.0789, 2nd-half IC=+0.1177, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.128, Q3_mid=+0.060, Q4=+0.126, Q5_high_vol=+0.123

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0989, Sharpe=+1.0037)
- Admission: Train IC=+0.2439, Deflated=+0.2436, IR=0.63, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.135 | 2017: -0.017 | 2018: +0.150 | 2019: +0.241 | 2020: +0.155 | 2021: +0.136 | 2022: +0.070 | 2023: +0.088 | 2024: +0.077 | 2025: +0.129 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.325 | 2016: +0.070 | 2017: +0.100 | 2018: +0.314 | 2019: +0.503 | 2020: +0.190 | 2021: +0.265 | 2022: +0.243 | 2023: +0.194 | 2024: +0.349 | 2025: +0.111 | 2026: +0.211
- IC CV=0.59, Neg years (linear/tail)=1/0 of 8, Half ratio=0.84, Recency ratio=1.33
- Early IC=+0.0591, Recent IC=+0.0788, 1st-half IC=+0.1379, 2nd-half IC=+0.1153, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.109, Q3_mid=+0.077, Q4=+0.125, Q5_high_vol=+0.193

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

**`combo_rel_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1093, Sharpe=+0.9727)
- Admission: Train IC=+0.2493, Deflated=+0.2494, IR=0.49, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.066 | 2017: +0.016 | 2018: +0.134 | 2019: +0.210 | 2020: +0.115 | 2021: +0.153 | 2022: +0.119 | 2023: +0.144 | 2024: +0.082 | 2025: +0.171 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.007 | 2017: +0.082 | 2018: +0.177 | 2019: +0.483 | 2020: +0.220 | 2021: +0.301 | 2022: +0.267 | 2023: +0.267 | 2024: +0.239 | 2025: +0.255 | 2026: -0.094
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.30, Recency ratio=3.22
- Early IC=+0.0408, Recent IC=+0.1316, 1st-half IC=+0.1066, 2nd-half IC=+0.1384, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.130, Q3_mid=+0.100, Q4=+0.097, Q5_high_vol=+0.177

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1214, Sharpe=+0.9475)
- Admission: Train IC=+0.2055, Deflated=+0.2046, IR=0.50, Mono=0.70, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.115 | 2017: +0.033 | 2018: +0.083 | 2019: +0.241 | 2020: +0.121 | 2021: +0.127 | 2022: +0.098 | 2023: +0.133 | 2024: +0.093 | 2025: +0.179 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.214 | 2016: +0.078 | 2017: +0.254 | 2018: +0.166 | 2019: +0.435 | 2020: +0.188 | 2021: +0.073 | 2022: +0.233 | 2023: +0.254 | 2024: +0.148 | 2025: +0.289 | 2026: +0.210
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=1.56
- Early IC=+0.0739, Recent IC=+0.1157, 1st-half IC=+0.1223, 2nd-half IC=+0.1210, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.131, Q3_mid=+0.114, Q4=+0.110, Q5_high_vol=+0.147

**`combo_min__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1167, Sharpe=+0.9419)
- Admission: Train IC=+0.1664, Deflated=+0.1661, IR=0.40, Mono=0.66, p=0.0018, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.004 | 2017: +0.009 | 2018: +0.030 | 2019: +0.154 | 2020: +0.061 | 2021: +0.142 | 2022: +0.073 | 2023: +0.133 | 2024: +0.065 | 2025: +0.166 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.002 | 2017: +0.085 | 2018: +0.256 | 2019: +0.290 | 2020: +0.150 | 2021: +0.183 | 2022: +0.124 | 2023: +0.313 | 2024: +0.364 | 2025: +0.134 | 2026: +0.252
- IC CV=0.75, Neg years (linear/tail)=0/0 of 8, Half ratio=2.18, Recency ratio=15.45
- Early IC=+0.0067, Recent IC=+0.1033, 1st-half IC=+0.0490, 2nd-half IC=+0.1069, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.092, Q3_mid=+0.065, Q4=+0.084, Q5_high_vol=+0.080

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1187, Sharpe=+0.9339)
- Admission: Train IC=+0.2773, Deflated=+0.2770, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.090 | 2017: -0.004 | 2018: +0.181 | 2019: +0.236 | 2020: +0.130 | 2021: +0.139 | 2022: +0.117 | 2023: +0.181 | 2024: +0.107 | 2025: +0.172 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.053 | 2017: +0.026 | 2018: +0.402 | 2019: +0.525 | 2020: +0.237 | 2021: +0.274 | 2022: +0.250 | 2023: +0.493 | 2024: +0.371 | 2025: +0.153 | 2026: +0.176
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.08, Recency ratio=3.43
- Early IC=+0.0434, Recent IC=+0.1488, 1st-half IC=+0.1317, 2nd-half IC=+0.1423, Neg regimes=0/5
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

**`combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0941, Sharpe=+0.8986)
- Admission: Train IC=+0.2066, Deflated=+0.2073, IR=0.49, Mono=0.67, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.053 | 2017: +0.034 | 2018: +0.074 | 2019: +0.073 | 2020: +0.011 | 2021: +0.156 | 2022: +0.135 | 2023: +0.180 | 2024: +0.084 | 2025: +0.165 | 2026: -0.031
- Yearly Tail ICs:   2015: -0.095 | 2016: +0.160 | 2017: +0.121 | 2018: +0.123 | 2019: +0.285 | 2020: -0.088 | 2021: +0.215 | 2022: +0.270 | 2023: +0.272 | 2024: +0.343 | 2025: +0.121 | 2026: -0.085
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=2.23, Recency ratio=3.60
- Early IC=+0.0434, Recent IC=+0.1564, 1st-half IC=+0.0535, 2nd-half IC=+0.1192, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.147, Q3_mid=+0.071, Q4=+0.098, Q5_high_vol=+0.084

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0976, Sharpe=+0.8959)
- Admission: Train IC=+0.2208, Deflated=+0.2205, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.123 | 2017: +0.041 | 2018: +0.089 | 2019: +0.199 | 2020: +0.122 | 2021: +0.160 | 2022: +0.122 | 2023: +0.186 | 2024: +0.050 | 2025: +0.171 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.104 | 2017: +0.199 | 2018: +0.309 | 2019: +0.171 | 2020: +0.104 | 2021: +0.349 | 2022: +0.184 | 2023: +0.320 | 2024: +0.197 | 2025: +0.231 | 2026: +0.071
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.37, Recency ratio=1.88
- Early IC=+0.0818, Recent IC=+0.1540, 1st-half IC=+0.1086, 2nd-half IC=+0.1483, Neg regimes=0/5
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

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1235, Sharpe=+0.8704)
- Admission: Train IC=+0.3321, Deflated=+0.3316, IR=0.84, Mono=0.80, p=0.0000, MaxCorr=0.94
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

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0891, Sharpe=+0.8097)
- Admission: Train IC=+0.2406, Deflated=+0.2395, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.086 | 2017: +0.034 | 2018: +0.094 | 2019: +0.195 | 2020: +0.118 | 2021: +0.143 | 2022: +0.074 | 2023: +0.164 | 2024: +0.095 | 2025: +0.160 | 2026: -0.045
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.214 | 2017: +0.112 | 2018: +0.138 | 2019: +0.419 | 2020: +0.305 | 2021: +0.104 | 2022: +0.286 | 2023: +0.493 | 2024: +0.265 | 2025: +0.185 | 2026: -0.196
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.98
- Early IC=+0.0602, Recent IC=+0.1191, 1st-half IC=+0.0981, 2nd-half IC=+0.1236, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.118, Q3_mid=+0.104, Q4=+0.106, Q5_high_vol=+0.155

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0883, Sharpe=+0.8073)
- Admission: Train IC=+0.2099, Deflated=+0.2099, IR=0.39, Mono=0.67, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.093 | 2017: +0.067 | 2018: +0.066 | 2019: +0.189 | 2020: +0.059 | 2021: +0.197 | 2022: +0.058 | 2023: +0.172 | 2024: +0.094 | 2025: +0.172 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.042 | 2016: +0.036 | 2017: +0.148 | 2018: +0.180 | 2019: +0.343 | 2020: +0.115 | 2021: +0.263 | 2022: +0.121 | 2023: +0.434 | 2024: +0.181 | 2025: +0.218 | 2026: -0.058
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.27, Recency ratio=1.44
- Early IC=+0.0798, Recent IC=+0.1152, 1st-half IC=+0.0988, 2nd-half IC=+0.1255, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.127, Q3_mid=+0.117, Q4=+0.109, Q5_high_vol=+0.148

**`first_bar_return`** (Lock IC=+0.0706, Sharpe=+0.8068)
- Admission: Train IC=+0.1377, Deflated=+0.1376, IR=0.38, Mono=0.66, p=0.0080, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.162 | 2017: +0.017 | 2018: +0.137 | 2019: +0.192 | 2020: +0.116 | 2021: +0.135 | 2022: +0.073 | 2023: +0.144 | 2024: +0.061 | 2025: +0.123 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.026 | 2017: +0.218 | 2018: +0.219 | 2019: +0.181 | 2020: +0.014 | 2021: +0.292 | 2022: +0.172 | 2023: +0.298 | 2024: +0.059 | 2025: +0.264 | 2026: +0.083
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=1.22
- Early IC=+0.0892, Recent IC=+0.1086, 1st-half IC=+0.1222, 2nd-half IC=+0.1139, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.106, Q3_mid=+0.097, Q4=+0.073, Q5_high_vol=+0.179

**`combo_max__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0792, Sharpe=+0.7948)
- Admission: Train IC=+0.1534, Deflated=+0.1532, IR=0.45, Mono=0.68, p=0.0032, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.093 | 2017: +0.014 | 2018: +0.140 | 2019: +0.118 | 2020: +0.070 | 2021: +0.160 | 2022: +0.131 | 2023: +0.111 | 2024: +0.033 | 2025: +0.110 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.079 | 2016: +0.021 | 2017: +0.274 | 2018: +0.388 | 2019: +0.138 | 2020: +0.029 | 2021: +0.351 | 2022: +0.116 | 2023: +0.176 | 2024: +0.182 | 2025: +0.200 | 2026: +0.128
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=2.25
- Early IC=+0.0538, Recent IC=+0.1211, 1st-half IC=+0.0978, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.104, Q3_mid=+0.074, Q4=+0.085, Q5_high_vol=+0.169

**`close_vs_open_range`** (Lock IC=+0.1017, Sharpe=+0.6838)
- Admission: Train IC=+0.1148, Deflated=+0.1144, IR=0.50, Mono=0.72, p=0.0230, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.029 | 2017: +0.037 | 2018: +0.002 | 2019: +0.076 | 2020: +0.040 | 2021: +0.122 | 2022: +0.087 | 2023: +0.162 | 2024: +0.093 | 2025: +0.219 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.077 | 2016: +0.121 | 2017: +0.163 | 2018: -0.055 | 2019: +0.196 | 2020: +0.115 | 2021: +0.052 | 2022: +0.358 | 2023: +0.228 | 2024: +0.144 | 2025: +0.219 | 2026: -0.030
- IC CV=0.72, Neg years (linear/tail)=0/1 of 8, Half ratio=3.56, Recency ratio=3.79
- Early IC=+0.0328, Recent IC=+0.1242, 1st-half IC=+0.0293, 2nd-half IC=+0.1043, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.086, Q3_mid=+0.094, Q4=+0.027, Q5_high_vol=+0.080

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0966, Sharpe=+0.6825)
- Admission: Train IC=+0.2228, Deflated=+0.2222, IR=0.57, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.032 | 2017: +0.012 | 2018: +0.025 | 2019: +0.120 | 2020: +0.058 | 2021: +0.170 | 2022: +0.103 | 2023: +0.160 | 2024: +0.095 | 2025: +0.200 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.270 | 2017: +0.037 | 2018: +0.094 | 2019: +0.349 | 2020: +0.159 | 2021: +0.303 | 2022: +0.319 | 2023: +0.379 | 2024: +0.243 | 2025: +0.164 | 2026: -0.259
- IC CV=0.69, Neg years (linear/tail)=0/0 of 8, Half ratio=3.54, Recency ratio=6.25
- Early IC=+0.0209, Recent IC=+0.1310, 1st-half IC=+0.0354, 2nd-half IC=+0.1252, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.104, Q3_mid=+0.101, Q4=+0.056, Q5_high_vol=+0.118

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.0831, Sharpe=+0.6530)
- Admission: Train IC=+0.1850, Deflated=+0.1843, IR=0.52, Mono=0.67, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.088 | 2017: +0.004 | 2018: +0.117 | 2019: +0.152 | 2020: +0.110 | 2021: +0.172 | 2022: +0.147 | 2023: +0.092 | 2024: +0.053 | 2025: +0.118 | 2026: +0.044
- Yearly Tail ICs:   2015: -0.040 | 2016: +0.171 | 2017: +0.133 | 2018: +0.272 | 2019: +0.111 | 2020: +0.080 | 2021: +0.446 | 2022: +0.172 | 2023: +0.189 | 2024: +0.216 | 2025: +0.048 | 2026: -0.151
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.52, Recency ratio=2.62
- Early IC=+0.0457, Recent IC=+0.1196, 1st-half IC=+0.0903, 2nd-half IC=+0.1370, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.076, Q3_mid=+0.114, Q4=+0.146, Q5_high_vol=+0.139

**`combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0987, Sharpe=+0.6482)
- Admission: Train IC=+0.2131, Deflated=+0.2122, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.015 | 2017: +0.017 | 2018: +0.053 | 2019: +0.133 | 2020: +0.056 | 2021: +0.148 | 2022: +0.073 | 2023: +0.199 | 2024: +0.077 | 2025: +0.203 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.097 | 2017: +0.122 | 2018: +0.039 | 2019: +0.305 | 2020: +0.139 | 2021: +0.217 | 2022: +0.377 | 2023: +0.523 | 2024: +0.156 | 2025: +0.214 | 2026: -0.191
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=2.37, Recency ratio=8.28
- Early IC=+0.0164, Recent IC=+0.1360, 1st-half IC=+0.0499, 2nd-half IC=+0.1181, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.112, Q3_mid=+0.088, Q4=+0.068, Q5_high_vol=+0.113

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1242, Sharpe=+0.6361)
- Admission: Train IC=+0.2124, Deflated=+0.2126, IR=0.56, Mono=0.68, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.100 | 2017: -0.031 | 2018: +0.096 | 2019: +0.091 | 2020: +0.077 | 2021: +0.066 | 2022: +0.131 | 2023: +0.154 | 2024: +0.122 | 2025: +0.085 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.264 | 2017: +0.061 | 2018: +0.442 | 2019: +0.295 | 2020: +0.014 | 2021: +0.130 | 2022: +0.254 | 2023: +0.202 | 2024: +0.169 | 2025: -0.014 | 2026: +0.123
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=1.59, Recency ratio=4.28
- Early IC=+0.0329, Recent IC=+0.1408, 1st-half IC=+0.0685, 2nd-half IC=+0.1090, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.118, Q3_mid=+0.081, Q4=+0.120, Q5_high_vol=+0.054

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0759, Sharpe=+0.6053)
- Admission: Train IC=+0.2587, Deflated=+0.2576, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.140 | 2017: +0.004 | 2018: +0.136 | 2019: +0.191 | 2020: +0.118 | 2021: +0.105 | 2022: +0.106 | 2023: +0.168 | 2024: +0.064 | 2025: +0.132 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.114 | 2017: +0.128 | 2018: +0.357 | 2019: +0.425 | 2020: +0.119 | 2021: +0.230 | 2022: +0.288 | 2023: +0.541 | 2024: +0.057 | 2025: +0.213 | 2026: -0.056
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=1.91
- Early IC=+0.0717, Recent IC=+0.1370, 1st-half IC=+0.1220, 2nd-half IC=+0.1198, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.146, Q3_mid=+0.099, Q4=+0.114, Q5_high_vol=+0.144

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0926, Sharpe=+0.6024)
- Admission: Train IC=+0.1994, Deflated=+0.1984, IR=0.52, Mono=0.68, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.102 | 2017: +0.036 | 2018: +0.120 | 2019: +0.193 | 2020: +0.094 | 2021: +0.123 | 2022: +0.112 | 2023: +0.179 | 2024: +0.086 | 2025: +0.168 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.395 | 2016: -0.066 | 2017: +0.177 | 2018: +0.211 | 2019: +0.429 | 2020: +0.128 | 2021: +0.266 | 2022: +0.118 | 2023: +0.514 | 2024: +0.198 | 2025: +0.261 | 2026: +0.238
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=1.12, Recency ratio=2.11
- Early IC=+0.0689, Recent IC=+0.1455, 1st-half IC=+0.1117, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.144, Q3_mid=+0.099, Q4=+0.098, Q5_high_vol=+0.153

**`combo_tri_max__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return`** (Lock IC=+0.1054, Sharpe=+0.5945)
- Admission: Train IC=+0.1939, Deflated=+0.1944, IR=0.58, Mono=0.70, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.119 | 2017: -0.044 | 2018: +0.117 | 2019: +0.075 | 2020: +0.114 | 2021: +0.082 | 2022: +0.103 | 2023: +0.117 | 2024: +0.124 | 2025: +0.081 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.146 | 2016: +0.320 | 2017: +0.046 | 2018: +0.367 | 2019: +0.189 | 2020: +0.047 | 2021: +0.140 | 2022: +0.237 | 2023: +0.260 | 2024: +0.126 | 2025: -0.054 | 2026: +0.028
- IC CV=0.60, Neg years (linear/tail)=1/0 of 8, Half ratio=1.45, Recency ratio=2.92
- Early IC=+0.0377, Recent IC=+0.1101, 1st-half IC=+0.0755, 2nd-half IC=+0.1093, Neg regimes=0/5
- Weak component: `yesterday_early_momentum` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.105, Q3_mid=+0.094, Q4=+0.120, Q5_high_vol=+0.071

**`combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0925, Sharpe=+0.5763)
- Admission: Train IC=+0.1675, Deflated=+0.1672, IR=0.40, Mono=0.71, p=0.0016, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.038 | 2017: +0.044 | 2018: +0.020 | 2019: +0.148 | 2020: +0.029 | 2021: +0.190 | 2022: +0.050 | 2023: +0.168 | 2024: +0.082 | 2025: +0.194 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.136 | 2016: -0.050 | 2017: +0.148 | 2018: +0.078 | 2019: +0.453 | 2020: +0.079 | 2021: +0.223 | 2022: +0.155 | 2023: +0.300 | 2024: +0.145 | 2025: +0.281 | 2026: -0.303
- IC CV=0.76, Neg years (linear/tail)=0/1 of 8, Half ratio=1.84, Recency ratio=2.65
- Early IC=+0.0411, Recent IC=+0.1088, 1st-half IC=+0.0610, 2nd-half IC=+0.1122, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.104, Q3_mid=+0.107, Q4=+0.062, Q5_high_vol=+0.104

**`combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0961, Sharpe=+0.5743)
- Admission: Train IC=+0.1870, Deflated=+0.1861, IR=0.49, Mono=0.70, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.048 | 2017: +0.034 | 2018: +0.048 | 2019: +0.165 | 2020: +0.087 | 2021: +0.143 | 2022: +0.100 | 2023: +0.179 | 2024: +0.106 | 2025: +0.197 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.249 | 2016: -0.053 | 2017: +0.064 | 2018: +0.031 | 2019: +0.396 | 2020: +0.246 | 2021: +0.109 | 2022: +0.308 | 2023: +0.347 | 2024: +0.267 | 2025: +0.295 | 2026: -0.202
- IC CV=0.53, Neg years (linear/tail)=0/1 of 8, Half ratio=1.73, Recency ratio=3.52
- Early IC=+0.0399, Recent IC=+0.1403, 1st-half IC=+0.0742, 2nd-half IC=+0.1282, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.117, Q3_mid=+0.128, Q4=+0.073, Q5_high_vol=+0.130

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.0911, Sharpe=+0.5434)
- Admission: Train IC=+0.2933, Deflated=+0.2948, IR=0.77, Mono=0.82, p=0.0000, MaxCorr=0.39
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.107 | 2017: -0.042 | 2018: +0.148 | 2019: +0.125 | 2020: +0.143 | 2021: +0.061 | 2022: +0.184 | 2023: +0.110 | 2024: +0.055 | 2025: +0.086 | 2026: +0.144
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.359 | 2017: +0.128 | 2018: +0.396 | 2019: +0.349 | 2020: +0.319 | 2021: +0.172 | 2022: +0.412 | 2023: +0.081 | 2024: +0.028 | 2025: +0.063 | 2026: +0.085
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=1.30, Recency ratio=4.55
- Early IC=+0.0323, Recent IC=+0.1469, 1st-half IC=+0.0983, 2nd-half IC=+0.1280, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.139, Q3_mid=+0.039, Q4=+0.138, Q5_high_vol=+0.190

**`combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=+0.0659, Sharpe=+0.5416)
- Admission: Train IC=+0.1754, Deflated=+0.1747, IR=0.53, Mono=0.72, p=0.0010, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.012 | 2017: +0.034 | 2018: +0.056 | 2019: +0.136 | 2020: +0.071 | 2021: +0.157 | 2022: +0.131 | 2023: +0.175 | 2024: +0.086 | 2025: +0.132 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.356 | 2016: -0.299 | 2017: +0.059 | 2018: +0.204 | 2019: +0.348 | 2020: +0.248 | 2021: +0.259 | 2022: +0.187 | 2023: +0.336 | 2024: +0.096 | 2025: +0.225 | 2026: +0.057
- IC CV=0.59, Neg years (linear/tail)=0/1 of 8, Half ratio=2.24, Recency ratio=6.60
- Early IC=+0.0232, Recent IC=+0.1529, 1st-half IC=+0.0569, 2nd-half IC=+0.1275, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.115, Q3_mid=+0.106, Q4=+0.081, Q5_high_vol=+0.115

**`combo_tri_mean__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1005, Sharpe=+0.4995)
- Admission: Train IC=+0.2266, Deflated=+0.2283, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.131 | 2017: -0.077 | 2018: +0.135 | 2019: +0.113 | 2020: +0.106 | 2021: +0.061 | 2022: +0.152 | 2023: +0.133 | 2024: +0.080 | 2025: +0.083 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.133 | 2016: +0.195 | 2017: +0.076 | 2018: +0.403 | 2019: +0.244 | 2020: +0.351 | 2021: +0.149 | 2022: +0.348 | 2023: +0.039 | 2024: +0.124 | 2025: +0.033 | 2026: +0.302
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=1.24, Recency ratio=5.28
- Early IC=+0.0270, Recent IC=+0.1428, 1st-half IC=+0.0924, 2nd-half IC=+0.1141, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.131, Q3_mid=+0.071, Q4=+0.135, Q5_high_vol=+0.136

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1119, Sharpe=+0.4883)
- Admission: Train IC=+0.2581, Deflated=+0.2602, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.045 | 2017: -0.050 | 2018: +0.080 | 2019: +0.133 | 2020: +0.101 | 2021: +0.040 | 2022: +0.179 | 2023: +0.115 | 2024: +0.082 | 2025: +0.129 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.178 | 2017: +0.063 | 2018: +0.361 | 2019: +0.261 | 2020: +0.392 | 2021: +0.196 | 2022: +0.466 | 2023: +0.088 | 2024: +0.041 | 2025: +0.066 | 2026: +0.303
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=1.67, Recency ratio=-68.28
- Early IC=-0.0022, Recent IC=+0.1471, 1st-half IC=+0.0646, 2nd-half IC=+0.1080, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.129, Q3_mid=+0.020, Q4=+0.105, Q5_high_vol=+0.146

**`combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.1018, Sharpe=+0.4840)
- Admission: Train IC=+0.2126, Deflated=+0.2122, IR=0.56, Mono=0.67, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.156 | 2017: +0.028 | 2018: +0.138 | 2019: +0.211 | 2020: +0.112 | 2021: +0.132 | 2022: +0.084 | 2023: +0.130 | 2024: +0.054 | 2025: +0.151 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.180 | 2016: +0.067 | 2017: +0.210 | 2018: +0.183 | 2019: +0.382 | 2020: +0.118 | 2021: +0.267 | 2022: +0.212 | 2023: +0.146 | 2024: +0.263 | 2025: +0.188 | 2026: +0.131
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=1.16
- Early IC=+0.0921, Recent IC=+0.1069, 1st-half IC=+0.1350, 2nd-half IC=+0.1145, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.115, Q3_mid=+0.111, Q4=+0.078, Q5_high_vol=+0.165

**`combo_rank_min__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=+0.0944, Sharpe=+0.4751)
- Admission: Train IC=+0.2003, Deflated=+0.1996, IR=0.44, Mono=0.70, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.071 | 2017: +0.020 | 2018: +0.061 | 2019: +0.163 | 2020: +0.054 | 2021: +0.114 | 2022: +0.073 | 2023: +0.177 | 2024: +0.075 | 2025: +0.150 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.015 | 2016: +0.184 | 2017: +0.120 | 2018: +0.086 | 2019: +0.253 | 2020: +0.119 | 2021: +0.071 | 2022: +0.235 | 2023: +0.411 | 2024: +0.190 | 2025: +0.132 | 2026: +0.044
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=1.37, Recency ratio=2.79
- Early IC=+0.0444, Recent IC=+0.1238, 1st-half IC=+0.0734, 2nd-half IC=+0.1007, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.095, Q3_mid=+0.063, Q4=+0.038, Q5_high_vol=+0.133

**`opening_drive_thrust_ratio`** (Lock IC=+0.0919, Sharpe=+0.4669)
- Admission: Train IC=+0.2148, Deflated=+0.2136, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.045 | 2017: +0.030 | 2018: +0.088 | 2019: +0.188 | 2020: +0.095 | 2021: +0.133 | 2022: +0.085 | 2023: +0.199 | 2024: +0.100 | 2025: +0.166 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.041 | 2017: -0.006 | 2018: +0.191 | 2019: +0.375 | 2020: +0.225 | 2021: +0.278 | 2022: +0.275 | 2023: +0.459 | 2024: +0.198 | 2025: +0.229 | 2026: -0.077
- IC CV=0.53, Neg years (linear/tail)=0/1 of 8, Half ratio=1.41, Recency ratio=3.77
- Early IC=+0.0376, Recent IC=+0.1418, 1st-half IC=+0.0885, 2nd-half IC=+0.1246, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.125, Q3_mid=+0.108, Q4=+0.106, Q5_high_vol=+0.143

**`combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0818, Sharpe=+0.4668)
- Admission: Train IC=+0.2157, Deflated=+0.2144, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.106 | 2017: +0.001 | 2018: +0.113 | 2019: +0.207 | 2020: +0.141 | 2021: +0.122 | 2022: +0.081 | 2023: +0.169 | 2024: +0.074 | 2025: +0.135 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.042 | 2017: +0.041 | 2018: +0.143 | 2019: +0.375 | 2020: +0.225 | 2021: +0.278 | 2022: +0.275 | 2023: +0.459 | 2024: +0.222 | 2025: +0.217 | 2026: -0.077
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.15, Recency ratio=2.32
- Early IC=+0.0539, Recent IC=+0.1253, 1st-half IC=+0.1085, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.116, Q3_mid=+0.117, Q4=+0.108, Q5_high_vol=+0.153

**`combo_max__yesterday_first_30min_return__limit_down_proximity_early`** (Lock IC=+0.0974, Sharpe=+0.4494)
- Admission: Train IC=+0.1746, Deflated=+0.1748, IR=0.53, Mono=0.69, p=0.0012, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.085 | 2017: -0.054 | 2018: +0.086 | 2019: +0.093 | 2020: +0.047 | 2021: +0.067 | 2022: +0.103 | 2023: +0.112 | 2024: +0.080 | 2025: +0.039 | 2026: +0.154
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.240 | 2017: +0.033 | 2018: +0.353 | 2019: +0.278 | 2020: +0.002 | 2021: +0.117 | 2022: +0.297 | 2023: +0.210 | 2024: +0.111 | 2025: +0.001 | 2026: +0.103
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=1.32, Recency ratio=6.94
- Early IC=+0.0154, Recent IC=+0.1073, 1st-half IC=+0.0654, 2nd-half IC=+0.0861, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.080, Q3_mid=+0.066, Q4=+0.106, Q5_high_vol=+0.043

**`combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1088, Sharpe=+0.4427)
- Admission: Train IC=+0.2033, Deflated=+0.2038, IR=0.49, Mono=0.70, p=0.0002, MaxCorr=0.55
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.121 | 2017: -0.071 | 2018: +0.115 | 2019: +0.066 | 2020: +0.116 | 2021: +0.100 | 2022: +0.119 | 2023: +0.135 | 2024: +0.143 | 2025: +0.074 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.321 | 2017: -0.016 | 2018: +0.309 | 2019: +0.113 | 2020: +0.071 | 2021: +0.261 | 2022: +0.113 | 2023: +0.185 | 2024: +0.194 | 2025: -0.077 | 2026: +0.161
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=1.83, Recency ratio=5.08
- Early IC=+0.0250, Recent IC=+0.1270, 1st-half IC=+0.0683, 2nd-half IC=+0.1248, Neg regimes=1/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=-0.028, Q2=+0.132, Q3_mid=+0.109, Q4=+0.127, Q5_high_vol=+0.089

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1267, Sharpe=+0.4263)
- Admission: Train IC=+0.1877, Deflated=+0.1873, IR=0.47, Mono=0.65, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.140 | 2017: -0.026 | 2018: +0.118 | 2019: +0.177 | 2020: +0.168 | 2021: +0.131 | 2022: +0.125 | 2023: +0.069 | 2024: +0.106 | 2025: +0.101 | 2026: +0.170
- Yearly Tail ICs:   2015: +0.084 | 2016: +0.223 | 2017: +0.030 | 2018: +0.243 | 2019: +0.158 | 2020: +0.179 | 2021: +0.265 | 2022: +0.223 | 2023: -0.007 | 2024: +0.166 | 2025: -0.011 | 2026: +0.239
- IC CV=0.54, Neg years (linear/tail)=1/1 of 8, Half ratio=1.18, Recency ratio=1.70
- Early IC=+0.0571, Recent IC=+0.0971, 1st-half IC=+0.1126, 2nd-half IC=+0.1326, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.079, Q3_mid=+0.115, Q4=+0.152, Q5_high_vol=+0.129

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0866, Sharpe=+0.4183)
- Admission: Train IC=+0.2133, Deflated=+0.2125, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.190 | 2024: +0.078 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.063 | 2017: +0.039 | 2018: +0.143 | 2019: +0.289 | 2020: +0.186 | 2021: +0.349 | 2022: +0.232 | 2023: +0.457 | 2024: +0.231 | 2025: +0.146 | 2026: -0.277
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.91, Recency ratio=2.92
- Early IC=+0.0526, Recent IC=+0.1533, 1st-half IC=+0.0774, 2nd-half IC=+0.1476, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.058, Q2=+0.128, Q3_mid=+0.102, Q4=+0.103, Q5_high_vol=+0.164

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0874, Sharpe=+0.4131)
- Admission: Train IC=+0.2097, Deflated=+0.2095, IR=0.51, Mono=0.69, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.087 | 2017: +0.027 | 2018: +0.117 | 2019: +0.128 | 2020: +0.091 | 2021: +0.177 | 2022: +0.156 | 2023: +0.131 | 2024: +0.078 | 2025: +0.139 | 2026: +0.022
- Yearly Tail ICs:   2015: -0.008 | 2016: +0.152 | 2017: +0.169 | 2018: +0.285 | 2019: +0.154 | 2020: +0.124 | 2021: +0.465 | 2022: +0.201 | 2023: +0.210 | 2024: +0.199 | 2025: +0.120 | 2026: -0.124
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.69, Recency ratio=2.54
- Early IC=+0.0567, Recent IC=+0.1438, 1st-half IC=+0.0842, 2nd-half IC=+0.1425, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.110, Q3_mid=+0.091, Q4=+0.128, Q5_high_vol=+0.165

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

**`combo_rank_min__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0702, Sharpe=+0.3954)
- Admission: Train IC=+0.1932, Deflated=+0.1931, IR=0.61, Mono=0.73, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.150 | 2016: +0.036 | 2017: +0.034 | 2018: +0.058 | 2019: +0.074 | 2020: +0.030 | 2021: +0.158 | 2022: +0.146 | 2023: +0.176 | 2024: +0.092 | 2025: +0.166 | 2026: -0.116
- Yearly Tail ICs:   2015: -0.161 | 2016: +0.189 | 2017: +0.145 | 2018: +0.158 | 2019: +0.172 | 2020: +0.018 | 2021: +0.124 | 2022: +0.357 | 2023: +0.418 | 2024: +0.282 | 2025: +0.215 | 2026: -0.226
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=3.42, Recency ratio=4.61
- Early IC=+0.0347, Recent IC=+0.1600, 1st-half IC=+0.0358, 2nd-half IC=+0.1223, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.104, Q3_mid=+0.111, Q4=+0.057, Q5_high_vol=+0.109

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0890, Sharpe=+0.3617)
- Admission: Train IC=+0.1798, Deflated=+0.1782, IR=0.45, Mono=0.67, p=0.0010, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.095 | 2017: +0.006 | 2018: +0.085 | 2019: +0.226 | 2020: +0.129 | 2021: +0.113 | 2022: +0.069 | 2023: +0.145 | 2024: +0.089 | 2025: +0.126 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.452 | 2016: +0.136 | 2017: -0.031 | 2018: +0.061 | 2019: +0.384 | 2020: +0.267 | 2021: +0.122 | 2022: +0.189 | 2023: +0.391 | 2024: +0.215 | 2025: +0.315 | 2026: -0.204
- IC CV=0.55, Neg years (linear/tail)=0/1 of 8, Half ratio=1.07, Recency ratio=2.10
- Early IC=+0.0508, Recent IC=+0.1069, 1st-half IC=+0.1038, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.095, Q3_mid=+0.121, Q4=+0.088, Q5_high_vol=+0.164

**`combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=+0.0988, Sharpe=+0.3616)
- Admission: Train IC=+0.2060, Deflated=+0.2057, IR=0.47, Mono=0.66, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.095 | 2017: +0.000 | 2018: +0.078 | 2019: +0.167 | 2020: +0.105 | 2021: +0.150 | 2022: +0.084 | 2023: +0.170 | 2024: +0.070 | 2025: +0.198 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.309 | 2016: -0.017 | 2017: +0.026 | 2018: +0.263 | 2019: +0.418 | 2020: +0.166 | 2021: +0.178 | 2022: +0.246 | 2023: +0.421 | 2024: +0.198 | 2025: +0.340 | 2026: -0.446
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.54, Recency ratio=2.67
- Early IC=+0.0476, Recent IC=+0.1270, 1st-half IC=+0.0820, 2nd-half IC=+0.1261, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.099, Q3_mid=+0.107, Q4=+0.068, Q5_high_vol=+0.150

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.0196, Sharpe=+0.3480)
- Admission: Train IC=+0.1782, Deflated=+0.1779, IR=0.51, Mono=0.68, p=0.0010, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.021 | 2016: +0.121 | 2017: +0.020 | 2018: +0.103 | 2019: +0.043 | 2020: +0.097 | 2021: +0.050 | 2022: +0.079 | 2023: +0.087 | 2024: +0.014 | 2025: +0.076 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.350 | 2017: +0.107 | 2018: +0.215 | 2019: +0.055 | 2020: +0.303 | 2021: +0.213 | 2022: +0.256 | 2023: +0.029 | 2024: +0.204 | 2025: -0.026 | 2026: +0.189
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.18
- Early IC=+0.0705, Recent IC=+0.0831, 1st-half IC=+0.0611, 2nd-half IC=+0.0831, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=-0.082, Q2=+0.135, Q3_mid=+0.042, Q4=+0.106, Q5_high_vol=+0.139

**`combo_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.0200, Sharpe=+0.3480)
- Admission: Train IC=+0.1774, Deflated=+0.1770, IR=0.52, Mono=0.69, p=0.0010, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.014 | 2016: +0.120 | 2017: +0.020 | 2018: +0.103 | 2019: +0.043 | 2020: +0.097 | 2021: +0.050 | 2022: +0.079 | 2023: +0.087 | 2024: +0.014 | 2025: +0.076 | 2026: -0.076
- Yearly Tail ICs:   2015: -0.089 | 2016: +0.330 | 2017: +0.107 | 2018: +0.215 | 2019: +0.055 | 2020: +0.300 | 2021: +0.220 | 2022: +0.256 | 2023: +0.029 | 2024: +0.222 | 2025: -0.032 | 2026: +0.188
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.19
- Early IC=+0.0701, Recent IC=+0.0831, 1st-half IC=+0.0610, 2nd-half IC=+0.0831, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=-0.082, Q2=+0.135, Q3_mid=+0.042, Q4=+0.106, Q5_high_vol=+0.139

**`combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1109, Sharpe=+0.3355)
- Admission: Train IC=+0.2538, Deflated=+0.2559, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.044 | 2017: -0.054 | 2018: +0.073 | 2019: +0.131 | 2020: +0.100 | 2021: +0.042 | 2022: +0.180 | 2023: +0.112 | 2024: +0.081 | 2025: +0.126 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.166 | 2017: +0.014 | 2018: +0.359 | 2019: +0.259 | 2020: +0.391 | 2021: +0.172 | 2022: +0.463 | 2023: +0.068 | 2024: +0.023 | 2025: +0.066 | 2026: +0.302
- IC CV=0.82, Neg years (linear/tail)=1/0 of 8, Half ratio=1.76, Recency ratio=-34.61
- Early IC=-0.0042, Recent IC=+0.1465, 1st-half IC=+0.0627, 2nd-half IC=+0.1103, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.130, Q3_mid=+0.020, Q4=+0.106, Q5_high_vol=+0.146

**`combo_mean__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0853, Sharpe=+0.3259)
- Admission: Train IC=+0.2366, Deflated=+0.2358, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.066 | 2017: +0.046 | 2018: +0.087 | 2019: +0.175 | 2020: +0.094 | 2021: +0.153 | 2022: +0.104 | 2023: +0.196 | 2024: +0.089 | 2025: +0.175 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.105 | 2017: +0.127 | 2018: +0.249 | 2019: +0.347 | 2020: +0.204 | 2021: +0.256 | 2022: +0.312 | 2023: +0.592 | 2024: +0.208 | 2025: +0.055 | 2026: -0.308
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=2.67
- Early IC=+0.0563, Recent IC=+0.1504, 1st-half IC=+0.0889, 2nd-half IC=+0.1375, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.139, Q3_mid=+0.114, Q4=+0.109, Q5_high_vol=+0.151

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

**`combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1244, Sharpe=+0.2717)
- Admission: Train IC=+0.2020, Deflated=+0.2013, IR=0.44, Mono=0.66, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.087 | 2017: +0.029 | 2018: +0.070 | 2019: +0.151 | 2020: +0.121 | 2021: +0.145 | 2022: +0.148 | 2023: +0.140 | 2024: +0.129 | 2025: +0.126 | 2026: +0.116
- Yearly Tail ICs:   2015: -0.016 | 2016: +0.189 | 2017: +0.086 | 2018: +0.185 | 2019: +0.257 | 2020: +0.120 | 2021: +0.285 | 2022: +0.206 | 2023: +0.227 | 2024: +0.137 | 2025: +0.050 | 2026: +0.131
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.65, Recency ratio=2.48
- Early IC=+0.0581, Recent IC=+0.1442, 1st-half IC=+0.0847, 2nd-half IC=+0.1401, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.057, Q2=+0.102, Q3_mid=+0.077, Q4=+0.131, Q5_high_vol=+0.165

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1026, Sharpe=+0.2266)
- Admission: Train IC=+0.2073, Deflated=+0.2069, IR=0.44, Mono=0.65, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.121 | 2017: +0.034 | 2018: +0.109 | 2019: +0.132 | 2020: +0.124 | 2021: +0.173 | 2022: +0.130 | 2023: +0.156 | 2024: +0.100 | 2025: +0.112 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.167 | 2017: +0.125 | 2018: +0.315 | 2019: +0.197 | 2020: +0.036 | 2021: +0.420 | 2022: +0.065 | 2023: +0.269 | 2024: +0.137 | 2025: +0.082 | 2026: +0.028
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.49, Recency ratio=1.85
- Early IC=+0.0773, Recent IC=+0.1434, 1st-half IC=+0.0976, 2nd-half IC=+0.1454, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.092, Q3_mid=+0.096, Q4=+0.131, Q5_high_vol=+0.185

**`combo_max__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0673, Sharpe=+0.2240)
- Admission: Train IC=+0.1981, Deflated=+0.1980, IR=0.63, Mono=0.74, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.043 | 2017: +0.042 | 2018: +0.063 | 2019: +0.066 | 2020: +0.104 | 2021: +0.151 | 2022: +0.122 | 2023: +0.157 | 2024: +0.075 | 2025: +0.140 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.016 | 2016: +0.198 | 2017: +0.040 | 2018: +0.164 | 2019: +0.278 | 2020: +0.156 | 2021: +0.338 | 2022: +0.272 | 2023: +0.346 | 2024: +0.186 | 2025: +0.135 | 2026: -0.316
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=2.90, Recency ratio=3.31
- Early IC=+0.0421, Recent IC=+0.1395, 1st-half IC=+0.0466, 2nd-half IC=+0.1348, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.100, Q3_mid=+0.090, Q4=+0.096, Q5_high_vol=+0.136

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0846, Sharpe=+0.2222)
- Admission: Train IC=+0.2465, Deflated=+0.2463, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.142 | 2017: +0.007 | 2018: +0.120 | 2019: +0.193 | 2020: +0.128 | 2021: +0.160 | 2022: +0.096 | 2023: +0.173 | 2024: +0.059 | 2025: +0.174 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.163 | 2017: -0.001 | 2018: +0.271 | 2019: +0.369 | 2020: +0.256 | 2021: +0.255 | 2022: +0.228 | 2023: +0.534 | 2024: +0.192 | 2025: +0.074 | 2026: -0.090
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=1.27, Recency ratio=1.80
- Early IC=+0.0745, Recent IC=+0.1341, 1st-half IC=+0.1104, 2nd-half IC=+0.1397, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.126, Q3_mid=+0.111, Q4=+0.107, Q5_high_vol=+0.181

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0702, Sharpe=+0.2137)
- Admission: Train IC=+0.2220, Deflated=+0.2210, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.163 | 2017: +0.013 | 2018: +0.122 | 2019: +0.186 | 2020: +0.138 | 2021: +0.085 | 2022: +0.092 | 2023: +0.134 | 2024: +0.051 | 2025: +0.112 | 2026: +0.030
- Yearly Tail ICs:   2015: -0.098 | 2016: +0.328 | 2017: +0.115 | 2018: +0.023 | 2019: +0.258 | 2020: +0.173 | 2021: -0.104 | 2022: +0.361 | 2023: +0.394 | 2024: +0.159 | 2025: +0.091 | 2026: -0.148
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.88, Recency ratio=1.29
- Early IC=+0.0876, Recent IC=+0.1127, 1st-half IC=+0.1228, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.123, Q3_mid=+0.103, Q4=+0.087, Q5_high_vol=+0.161

**`max_up_ret`** (Lock IC=+0.0765, Sharpe=+0.2136)
- Admission: Train IC=+0.2061, Deflated=+0.2058, IR=0.71, Mono=0.76, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.080 | 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175 | 2024: +0.074 | 2025: +0.164 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.048 | 2016: +0.198 | 2017: +0.106 | 2018: +0.212 | 2019: +0.279 | 2020: +0.177 | 2021: +0.343 | 2022: +0.267 | 2023: +0.389 | 2024: +0.190 | 2025: +0.128 | 2026: -0.261
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=2.01, Recency ratio=2.24
- Early IC=+0.0651, Recent IC=+0.1457, 1st-half IC=+0.0718, 2nd-half IC=+0.1444, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.126, Q3_mid=+0.106, Q4=+0.097, Q5_high_vol=+0.158

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0834, Sharpe=+0.2125)
- Admission: Train IC=+0.2139, Deflated=+0.2129, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.093 | 2017: +0.005 | 2018: +0.085 | 2019: +0.212 | 2020: +0.120 | 2021: +0.166 | 2022: +0.110 | 2023: +0.147 | 2024: +0.075 | 2025: +0.172 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.055 | 2016: +0.125 | 2017: +0.041 | 2018: +0.198 | 2019: +0.346 | 2020: +0.160 | 2021: +0.299 | 2022: +0.263 | 2023: +0.376 | 2024: +0.186 | 2025: +0.118 | 2026: -0.248
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=2.63
- Early IC=+0.0489, Recent IC=+0.1287, 1st-half IC=+0.0983, 2nd-half IC=+0.1362, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.106, Q3_mid=+0.145, Q4=+0.103, Q5_high_vol=+0.158

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

**`combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.1056, Sharpe=+0.1964)
- Admission: Train IC=+0.2173, Deflated=+0.2166, IR=0.52, Mono=0.67, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.166 | 2017: +0.023 | 2018: +0.145 | 2019: +0.155 | 2020: +0.159 | 2021: +0.164 | 2022: +0.129 | 2023: +0.122 | 2024: +0.066 | 2025: +0.133 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.016 | 2016: +0.185 | 2017: +0.213 | 2018: +0.285 | 2019: +0.166 | 2020: +0.104 | 2021: +0.440 | 2022: +0.118 | 2023: +0.239 | 2024: +0.159 | 2025: +0.081 | 2026: +0.120
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.15, Recency ratio=1.33
- Early IC=+0.0944, Recent IC=+0.1255, 1st-half IC=+0.1269, 2nd-half IC=+0.1460, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.115, Q3_mid=+0.122, Q4=+0.134, Q5_high_vol=+0.170

**`combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.0898, Sharpe=+0.1198)
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

**`combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0866, Sharpe=+0.0893)
- Admission: Train IC=+0.2550, Deflated=+0.2548, IR=0.54, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.174 | 2017: -0.015 | 2018: +0.141 | 2019: +0.203 | 2020: +0.106 | 2021: +0.139 | 2022: +0.078 | 2023: +0.159 | 2024: +0.049 | 2025: +0.165 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.263 | 2016: +0.223 | 2017: +0.143 | 2018: +0.354 | 2019: +0.381 | 2020: +0.067 | 2021: +0.243 | 2022: +0.305 | 2023: +0.444 | 2024: +0.196 | 2025: +0.440 | 2026: -0.098
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=0.95, Recency ratio=1.50
- Early IC=+0.0794, Recent IC=+0.1188, 1st-half IC=+0.1245, 2nd-half IC=+0.1180, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.117, Q3_mid=+0.105, Q4=+0.102, Q5_high_vol=+0.172

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return`** (Lock IC=+0.0781, Sharpe=+0.0786)
- Admission: Train IC=+0.2392, Deflated=+0.2387, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.108 | 2017: +0.033 | 2018: +0.089 | 2019: +0.180 | 2020: +0.105 | 2021: +0.190 | 2022: +0.100 | 2023: +0.184 | 2024: +0.074 | 2025: +0.169 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.128 | 2017: +0.110 | 2018: +0.211 | 2019: +0.296 | 2020: +0.095 | 2021: +0.331 | 2022: +0.301 | 2023: +0.395 | 2024: +0.151 | 2025: +0.230 | 2026: -0.367
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.43, Recency ratio=2.01
- Early IC=+0.0706, Recent IC=+0.1418, 1st-half IC=+0.1006, 2nd-half IC=+0.1439, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.090, Q2=+0.109, Q3_mid=+0.128, Q4=+0.108, Q5_high_vol=+0.169

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0258, Sharpe=+0.0683)
- Admission: Train IC=+0.1841, Deflated=+0.1841, IR=0.48, Mono=0.65, p=0.0004, MaxCorr=0.49
- Yearly Linear ICs: 2015: -0.033 | 2016: +0.102 | 2017: +0.047 | 2018: +0.082 | 2019: +0.039 | 2020: +0.087 | 2021: +0.066 | 2022: +0.087 | 2023: +0.093 | 2024: +0.008 | 2025: +0.113 | 2026: -0.105
- Yearly Tail ICs:   2015: -0.055 | 2016: +0.322 | 2017: +0.142 | 2018: +0.229 | 2019: -0.010 | 2020: +0.184 | 2021: +0.323 | 2022: +0.158 | 2023: +0.256 | 2024: +0.167 | 2025: +0.125 | 2026: +0.162
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=1.63, Recency ratio=1.21
- Early IC=+0.0743, Recent IC=+0.0897, 1st-half IC=+0.0547, 2nd-half IC=+0.0891, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=-0.074, Q2=+0.126, Q3_mid=+0.043, Q4=+0.087, Q5_high_vol=+0.139

**`combo_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0770, Sharpe=+0.0324)
- Admission: Train IC=+0.1829, Deflated=+0.1825, IR=0.52, Mono=0.72, p=0.0008, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.050 | 2017: +0.055 | 2018: +0.049 | 2019: +0.124 | 2020: +0.094 | 2021: +0.159 | 2022: +0.102 | 2023: +0.183 | 2024: +0.061 | 2025: +0.190 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.114 | 2017: +0.002 | 2018: +0.126 | 2019: +0.256 | 2020: +0.088 | 2021: +0.301 | 2022: +0.293 | 2023: +0.472 | 2024: +0.228 | 2025: +0.118 | 2026: -0.527
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=2.11, Recency ratio=2.69
- Early IC=+0.0529, Recent IC=+0.1425, 1st-half IC=+0.0660, 2nd-half IC=+0.1395, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.111, Q3_mid=+0.114, Q4=+0.076, Q5_high_vol=+0.134

**`combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1298, Sharpe=+0.0321)
- Admission: Train IC=+0.1848, Deflated=+0.1848, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.176 | 2016: -0.013 | 2017: -0.005 | 2018: +0.091 | 2019: +0.175 | 2020: +0.098 | 2021: +0.137 | 2022: +0.146 | 2023: +0.111 | 2024: +0.091 | 2025: +0.151 | 2026: +0.125
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.147 | 2017: +0.028 | 2018: +0.209 | 2019: +0.253 | 2020: +0.283 | 2021: +0.123 | 2022: +0.144 | 2023: +0.121 | 2024: -0.075 | 2025: +0.268 | 2026: +0.084
- IC CV=0.69, Neg years (linear/tail)=2/0 of 8, Half ratio=1.97, Recency ratio=-14.53
- Early IC=-0.0089, Recent IC=+0.1287, 1st-half IC=+0.0677, 2nd-half IC=+0.1335, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.126, Q3_mid=+0.078, Q4=+0.117, Q5_high_vol=+0.127

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1188, Sharpe=+0.0236)
- Admission: Train IC=+0.1747, Deflated=+0.1742, IR=0.52, Mono=0.71, p=0.0012, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.057 | 2017: -0.019 | 2018: +0.009 | 2019: +0.161 | 2020: +0.102 | 2021: +0.104 | 2022: +0.081 | 2023: +0.153 | 2024: +0.126 | 2025: +0.193 | 2026: -0.042
- Yearly Tail ICs:   2015: +0.195 | 2016: +0.114 | 2017: +0.083 | 2018: -0.016 | 2019: +0.319 | 2020: +0.179 | 2021: +0.151 | 2022: +0.361 | 2023: +0.374 | 2024: +0.169 | 2025: +0.262 | 2026: -0.291
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=2.85, Recency ratio=6.13
- Early IC=+0.0191, Recent IC=+0.1168, 1st-half IC=+0.0413, 2nd-half IC=+0.1178, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=-0.044, Q2=+0.120, Q3_mid=+0.077, Q4=+0.057, Q5_high_vol=+0.149

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | TP | gradual | +0.1120 | +0.0212 | -0.0888 | 1y |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Median | gradual | +0.1087 | +0.0145 | -0.0866 | 1y |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Median | gradual | +0.0634 | +0.0575 | -0.1666 | 2y |
| `combo_rank_max__max_up_ret__bar_ret_0` | TP | gradual | +0.0623 | +0.0758 | -0.1575 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | TP | gradual | +0.0616 | +0.0630 | -0.0777 | 2y |
| `combo_mean__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0602 | +0.0544 | -0.1131 | 2y |
| `combo_max__max_up_ret__bar_ret_0` | TP | gradual | +0.0601 | +0.0772 | -0.1564 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0565 | +0.0495 | -0.0265 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0560 | +0.0672 | -0.0652 | 2y |
| `max_up_ret` | FP | gradual | +0.0557 | +0.0327 | -0.1524 | 2y |
| `combo_min__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0541 | +0.0224 | -0.0760 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0533 | +0.0500 | -0.0305 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | gradual | +0.0522 | +0.0448 | -0.0334 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0498 | +0.0530 | -0.0159 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0479 | +0.0931 | +0.0021 | 2y |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0453 | +0.0553 | -0.0801 | 2y |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Median | gradual | +0.0443 | +0.0757 | -0.1496 | 2y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | gradual | +0.0418 | +0.1055 | -0.2078 | 2y |
| `bar_body_rng_0` | Median | gradual | +0.0410 | +0.0721 | -0.0623 | 2y |
| `net_volume_flow` | FP | gradual | +0.0403 | +0.0693 | -0.1763 | 2y |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | Median | gradual | +0.0392 | +0.0704 | -0.0938 | 2y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0386 | +0.0944 | +0.0458 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.0364 | +0.0628 | +0.0098 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0364 | +0.0628 | +0.0098 | 2y |
| `combo_max__max_up_ret__first_bar_sentiment` | TP | gradual | +0.0353 | +0.0379 | -0.1303 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0347 | +0.0464 | -0.0486 | 2y |
| `opening_drive_thrust_ratio` | Median | gradual | +0.0331 | +0.0693 | -0.1510 | 2y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | TP | persistent | +0.0329 | +0.0335 | +0.0967 | ∞ |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | FP | gradual | +0.0329 | +0.0553 | -0.1845 | 2y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Median | persistent | +0.0300 | +0.0320 | +0.0251 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0290 | +0.0978 | +0.0141 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0290 | +0.0718 | -0.0276 | 2y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0282 | +0.0190 | +0.0363 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0279 | +0.0542 | -0.0204 | 2y |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0272 | +0.1119 | -0.1848 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0258 | +0.0420 | -0.0021 | 2y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0215 | +0.0910 | -0.1932 | 2y |
| `combo_rank_min__bar_ret_0__first_bar_sentiment` | TP | gradual | +0.0163 | +0.0531 | -0.0638 | 2y |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | TP | gradual | +0.0145 | +0.0760 | -0.0984 | 2y |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0142 | +0.0646 | +0.0712 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0138 | +0.0841 | -0.0065 | 2y |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | TP | gradual | +0.0131 | +0.0679 | -0.1164 | 2y |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0106 | +0.1003 | -0.1508 | 2y |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | gradual | +0.0093 | +0.0956 | -0.1968 | ∞ |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0084 | +0.1091 | -0.1474 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | FP | gradual | +0.0078 | +0.0327 | -0.0648 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Median | gradual | +0.0045 | +0.0710 | -0.1230 | ∞ |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0032 | +0.1067 | -0.1238 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0012 | +0.0206 | +0.0855 | ∞ |
| `early_order_flow_imbalance` | FP | immediate | -0.0011 | +0.0765 | -0.2024 | ∞ |
| `always_in_trend_persistence` | FP | immediate | -0.0041 | +0.0514 | -0.2597 | ∞ |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Median | immediate | -0.0044 | +0.1224 | -0.1415 | ∞ |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | FP | immediate | -0.0045 | +0.0356 | -0.0932 | ∞ |
| `combo_max__bar_ret_0__first_bar_sentiment` | FP | immediate | -0.0067 | +0.0569 | -0.0824 | ∞ |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | FP | immediate | -0.0075 | +0.0315 | -0.1334 | ∞ |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | TP | immediate | -0.0107 | +0.0823 | +0.1260 | ∞ |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | FP | immediate | -0.0155 | +0.0539 | -0.1395 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Median | immediate | -0.0254 | +0.0749 | +0.0648 | ∞ |
| `combo_rank_min__volume_weighted_price_position__first_bar_sentiment` | Median | immediate | -0.0298 | +0.0985 | -0.0418 | ∞ |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | FP | immediate | -0.0365 | +0.0173 | -0.1589 | ∞ |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | FP | immediate | -0.0375 | +0.0646 | -0.1536 | ∞ |
| `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | Median | immediate | -0.0628 | +0.0683 | +0.1244 | ∞ |

**Decay distribution**: immediate=13, fast(1-2y)=0, gradual=39, persistent=10

**FP decay trajectories:**

- `combo_rank_max__volume_weighted_price_position__first_bar_sentiment`: Y1:-0.038 → Y2:+0.065 → Y3:-0.154
- `combo_ratio__first_bar_sentiment__volume_weighted_price_position`: Y1:-0.036 → Y2:+0.017 → Y3:-0.159
- `combo_max__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:-0.015 → Y2:+0.054 → Y3:-0.140
- `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`: Y1:-0.007 → Y2:+0.032 → Y3:-0.133
- `combo_max__bar_ret_0__first_bar_sentiment`: Y1:-0.007 → Y2:+0.057 → Y3:-0.082
- `combo_sig_product__bar_ret_0__volume_weighted_price_position`: Y1:-0.005 → Y2:+0.036 → Y3:-0.093
- `always_in_trend_persistence`: Y1:-0.004 → Y2:+0.051 → Y3:-0.260
- `early_order_flow_imbalance`: Y1:-0.001 → Y2:+0.076 → Y3:-0.202
- `combo_rank_min__max_up_ret__first_bar_sentiment`: Y1:+0.008 → Y2:+0.033 → Y3:-0.065
- `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.009 → Y2:+0.096 → Y3:-0.197
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:+0.022 → Y2:+0.091 → Y3:-0.193
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:+0.027 → Y2:+0.112 → Y3:-0.185
- `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`: Y1:+0.033 → Y2:+0.055 → Y3:-0.184
- `net_volume_flow`: Y1:+0.040 → Y2:+0.069 → Y3:-0.176
- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.042 → Y2:+0.105 → Y3:-0.208
- `max_up_ret`: Y1:+0.056 → Y2:+0.033 → Y3:-0.152

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1803 | +0.0831 | +0.1124 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1735 | +0.1023 | +0.0066 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1723 | +0.1082 | +0.1064 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Median | gradual | +0.1633 | +0.0833 | -0.0266 | 2y |
| `combo_rank_max__max_up_ret__first_bar_return` | TP | gradual | +0.1632 | +0.0981 | -0.0677 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1606 | +0.1038 | +0.0031 | 2y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.1595 | +0.0598 | -0.0091 | 1y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1590 | +0.1063 | +0.1978 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1587 | +0.0925 | +0.0908 | ∞ |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1576 | +0.0579 | +0.0057 | 1y |
| `combo_sig_product__max_up_ret__net_volume_flow` | TP | persistent | +0.1571 | +0.0784 | +0.0070 | 1y |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1560 | +0.0950 | -0.0080 | 2y |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.1537 | +0.0781 | +0.0842 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1535 | +0.1059 | +0.0888 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | TP | gradual | +0.1534 | +0.1272 | -0.0153 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_day_regime_conviction` | TP | persistent | +0.1534 | +0.1353 | +0.0076 | 2y |
| `opening_drive_thrust_ratio` | TP | persistent | +0.1521 | +0.0877 | +0.0025 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.1516 | +0.1255 | -0.0279 | 2y |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1508 | +0.0908 | +0.2248 | ∞ |
| `combo_mean__close_vs_open_range__first_bar_return` | TP | gradual | +0.1507 | +0.1141 | -0.0361 | 2y |
| `combo_min__max_up_ret__close_vs_open_range` | TP | gradual | +0.1498 | +0.1583 | -0.0680 | 2y |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1497 | +0.1101 | -0.0224 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | TP | gradual | +0.1491 | +0.1211 | -0.0525 | 2y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | TP | persistent | +0.1488 | +0.0865 | +0.0000 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | TP | gradual | +0.1483 | +0.0867 | -0.0110 | 2y |
| `combo_sig_product__max_up_ret__body_size_progression` | TP | persistent | +0.1455 | +0.0540 | +0.0397 | 1y |
| `combo_max__max_up_ret__first_bar_sentiment` | TP | gradual | +0.1447 | +0.0768 | -0.0347 | 2y |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.1445 | +0.0964 | +0.0136 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | TP | gradual | +0.1444 | +0.1184 | -0.0313 | 2y |
| `combo_mean__opening_drive_thrust_ratio__early_body_momentum` | Median | gradual | +0.1443 | +0.1139 | -0.0632 | 2y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.1436 | +0.0801 | -0.0138 | 2y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | gradual | +0.1435 | +0.0745 | -0.0132 | 2y |
| `combo_max__net_volume_flow__max_down_ret` | Median | gradual | +0.1430 | +0.1322 | -0.0558 | 2y |
| `max_up_ret` | TP | gradual | +0.1427 | +0.0801 | -0.0291 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1426 | +0.1228 | -0.0491 | 2y |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.1419 | +0.0608 | +0.0219 | 1y |
| `combo_rank_max__close_vs_open_range__first_bar_return` | TP | gradual | +0.1413 | +0.1183 | -0.0953 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | persistent | +0.1412 | +0.1184 | +0.0512 | 2y |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1412 | +0.1218 | -0.0390 | 2y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1409 | +0.0715 | +0.0212 | 2y |
| `trend_strength_intraday` | TP | gradual | +0.1407 | +0.1166 | -0.0474 | 2y |
| `combo_mean__max_up_ret__first_bar_return` | TP | gradual | +0.1406 | +0.0763 | -0.0344 | 2y |
| `combo_min__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1397 | +0.1492 | -0.0797 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | TP | gradual | +0.1396 | +0.1249 | -0.0383 | 2y |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1393 | +0.1316 | +0.0955 | ∞ |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1385 | +0.1357 | +0.0880 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.1382 | +0.1259 | -0.0552 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | TP | gradual | +0.1379 | +0.1358 | -0.0538 | 2y |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | TP | gradual | +0.1379 | +0.1307 | -0.0495 | 2y |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1378 | +0.1148 | +0.1554 | ∞ |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1377 | +0.0863 | -0.0133 | 2y |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1367 | +0.1166 | -0.0695 | 2y |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | TP | gradual | +0.1363 | +0.0901 | -0.0115 | 2y |
| `combo_mean__net_volume_flow__first_bar_return` | TP | gradual | +0.1363 | +0.1080 | -0.0295 | 2y |
| `combo_max__close_vs_open_range__first_bar_return` | TP | gradual | +0.1359 | +0.1213 | -0.0914 | 2y |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1356 | +0.1097 | +0.0226 | 2y |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1356 | +0.0212 | +0.0758 | 1y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | TP | persistent | +0.1354 | +0.0983 | +0.0010 | 2y |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.1353 | +0.0578 | +0.0381 | 1y |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.1342 | +0.0723 | +0.0187 | 2y |
| `combo_rank_max__max_up_ret__close_vs_open_range` | TP | gradual | +0.1328 | +0.0785 | -0.0319 | 2y |
| `combo_min__close_vs_open_range__first_bar_return` | TP | persistent | +0.1316 | +0.1401 | +0.0121 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | TP | persistent | +0.1313 | +0.1223 | +0.0508 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1311 | +0.1011 | +0.0718 | ∞ |
| `combo_rank_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1310 | +0.0931 | -0.0433 | 2y |
| `combo_min__net_volume_flow__first_bar_return` | TP | persistent | +0.1302 | +0.1212 | +0.0078 | 2y |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | TP | gradual | +0.1300 | +0.1418 | -0.0720 | 2y |
| `combo_rank_max__early_body_momentum__max_down_ret` | TP | gradual | +0.1298 | +0.1701 | -0.0787 | 2y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1287 | +0.0921 | +0.0337 | 2y |
| `combo_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1284 | +0.0961 | -0.0572 | 2y |
| `combo_rank_max__close_vs_open_range__early_body_momentum` | TP | gradual | +0.1274 | +0.1443 | -0.0910 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Median | persistent | +0.1273 | +0.1253 | +0.0730 | ∞ |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | gradual | +0.1272 | +0.1213 | -0.1240 | 2y |
| `combo_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1272 | +0.0217 | +0.0778 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.1270 | +0.0934 | -0.0804 | 2y |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.1265 | +0.0965 | +0.0040 | 2y |
| `combo_max__net_volume_flow__first_bar_sentiment` | TP | gradual | +0.1263 | +0.0979 | -0.0370 | 2y |
| `combo_max__bar_ret_0__max_down_ret` | TP | persistent | +0.1244 | +0.1076 | +0.0004 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1239 | +0.1399 | +0.0424 | 2y |
| `combo_min__net_volume_flow__close_vs_open_range` | TP | gradual | +0.1237 | +0.1380 | -0.0671 | 2y |
| `combo_min__max_up_ret__early_body_momentum` | Median | gradual | +0.1235 | +0.1342 | -0.0967 | 2y |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | TP | gradual | +0.1229 | +0.1434 | -0.0217 | 2y |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.1224 | +0.1093 | +0.0049 | 2y |
| `combo_min__net_volume_flow__first_bar_sentiment` | TP | gradual | +0.1211 | +0.1358 | -0.0496 | 2y |
| `open_to_current_return` | TP | gradual | +0.1202 | +0.1639 | -0.1128 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Median | gradual | +0.1197 | +0.0962 | -0.0817 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | TP | persistent | +0.1188 | +0.0801 | +0.0193 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.1177 | +0.1493 | +0.0858 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1175 | +0.1215 | +0.0366 | 2y |
| `combo_max__early_body_momentum__bar_ret_0` | Median | gradual | +0.1171 | +0.1257 | -0.1198 | 2y |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.1164 | +0.0467 | +0.0797 | 1y |
| `combo_mean__first_bar_sentiment__early_body_momentum` | TP | gradual | +0.1158 | +0.1247 | -0.0609 | 2y |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.1149 | +0.1119 | +0.1037 | ∞ |
| `morning_volume_weighted_momentum` | TP | gradual | +0.1146 | +0.1651 | -0.0906 | 2y |
| `combo_rank_max__bar_ret_0__max_down_ret` | TP | persistent | +0.1144 | +0.1160 | +0.0292 | 2y |
| `combo_min__close_vs_open_range__max_down_ret` | TP | persistent | +0.1141 | +0.1398 | +0.0376 | 2y |
| `combo_min__net_volume_flow__max_down_ret` | TP | persistent | +0.1137 | +0.1375 | +0.0352 | 2y |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | TP | gradual | +0.1126 | +0.1435 | -0.0824 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | TP | gradual | +0.1113 | +0.1117 | -0.0434 | 2y |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1110 | +0.1045 | +0.1074 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Median | persistent | +0.1110 | +0.1002 | +0.0055 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | TP | persistent | +0.1107 | +0.1390 | +0.0238 | 2y |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.1107 | +0.1069 | +0.0822 | ∞ |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.1101 | +0.1307 | +0.0118 | 2y |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | gradual | +0.1092 | +0.1503 | -0.0835 | 2y |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1078 | +0.1257 | +0.0764 | ∞ |
| `early_body_momentum` | Median | gradual | +0.1071 | +0.1345 | -0.0993 | 2y |
| `first_bar_return` | TP | gradual | +0.1067 | +0.0924 | -0.0114 | 2y |
| `combo_mean__first_bar_sentiment__bar_ret_0` | TP | gradual | +0.1067 | +0.0924 | -0.0114 | 2y |
| `early_order_flow_imbalance` | Median | gradual | +0.1066 | +0.0913 | -0.1345 | 2y |
| `combo_min__close_vs_open_range__first_bar_sentiment` | TP | gradual | +0.1045 | +0.1462 | -0.0465 | 2y |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.1039 | +0.1080 | +0.0783 | ∞ |
| `vwap_trend_channel_slope` | Median | gradual | +0.1037 | +0.0941 | -0.0312 | 2y |
| `combo_max__trend_bar_close_consistency__max_down_ret` | TP | gradual | +0.1035 | +0.1373 | -0.1214 | 2y |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1023 | +0.0824 | +0.0844 | ∞ |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1019 | +0.0250 | +0.0952 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1018 | +0.0924 | +0.0836 | ∞ |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Median | gradual | +0.1017 | +0.1252 | -0.0261 | 2y |
| `combo_sig_product__max_up_ret__first_bar_return` | TP | gradual | +0.1013 | +0.0769 | -0.0792 | 2y |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | TP | persistent | +0.1012 | +0.0470 | +0.1094 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1008 | +0.1253 | +0.0865 | ∞ |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1007 | +0.0966 | +0.1228 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1006 | +0.0900 | +0.0731 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | persistent | +0.0995 | +0.0735 | +0.0731 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | persistent | +0.0986 | +0.1251 | +0.0245 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0968 | +0.1016 | -0.0804 | 2y |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Median | gradual | +0.0950 | +0.0858 | -0.0790 | 2y |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | TP | gradual | +0.0929 | +0.0786 | -0.0198 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0908 | +0.1225 | +0.0791 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.0902 | +0.1084 | +0.0820 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0892 | +0.1205 | +0.0795 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0876 | +0.1301 | +0.0834 | ∞ |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0874 | +0.0221 | +0.0886 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | gradual | +0.0865 | +0.0957 | -0.0716 | 2y |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.0860 | +0.0971 | +0.0377 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0853 | +0.1336 | +0.0332 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | Median | gradual | +0.0844 | +0.1390 | -0.0012 | 2y |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0842 | +0.1415 | +0.0832 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Median | gradual | +0.0831 | +0.0973 | -0.0114 | 2y |
| `combo_min__first_bar_sentiment__max_down_ret` | TP | persistent | +0.0806 | +0.1427 | +0.0359 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.0802 | +0.1118 | +0.1038 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.0684 | +0.0547 | +0.0734 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0683 | +0.0453 | +0.1157 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0630 | +0.0772 | +0.0754 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.0362 | +0.0959 | +0.0658 | ∞ |
| `combo_diff__bar_ret_0__max_down_ret` | Median | gradual | +0.0035 | +0.0521 | -0.0202 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=70, persistent=76

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.1426 | +0.0743 | +0.1028 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1326 | +0.1360 | +0.1259 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1297 | +0.1248 | -0.0819 | 2y |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1291 | +0.1262 | +0.1158 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1269 | +0.1640 | +0.0657 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1267 | +0.1392 | +0.1129 | ∞ |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1260 | +0.1935 | -0.0415 | 2y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1247 | +0.1135 | +0.1174 | ∞ |
| `combo_tri_max__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | TP | persistent | +0.1238 | +0.0811 | +0.0849 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1225 | +0.1516 | +0.1037 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1214 | +0.0780 | +0.1570 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1194 | +0.1395 | +0.1093 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1193 | +0.1790 | +0.0373 | 2y |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1154 | +0.1557 | +0.1169 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1153 | +0.1681 | +0.0618 | ∞ |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1148 | +0.1732 | +0.0894 | ∞ |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1135 | +0.1921 | +0.0467 | 2y |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1128 | +0.1291 | +0.1138 | ∞ |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1119 | +0.1805 | +0.0905 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1088 | +0.1069 | +0.0703 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.1075 | +0.1827 | -0.0023 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1071 | +0.1602 | +0.1080 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1067 | +0.1720 | +0.0607 | ∞ |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1066 | +0.1533 | +0.1438 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1066 | +0.1533 | +0.1438 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.1063 | +0.1008 | +0.1704 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.1061 | +0.1980 | -0.0899 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1044 | +0.1303 | +0.0684 | ∞ |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1038 | +0.1081 | +0.1782 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1028 | +0.1514 | +0.1019 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1004 | +0.1122 | +0.0925 | ∞ |
| `opening_drive_thrust_ratio` | TP | gradual | +0.1002 | +0.1663 | -0.0464 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0999 | +0.1720 | +0.0720 | ∞ |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.0983 | +0.1706 | +0.1014 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0972 | +0.1937 | +0.0566 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0969 | +0.1593 | +0.1024 | ∞ |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Median | gradual | +0.0965 | +0.1114 | -0.0547 | 2y |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.0955 | +0.2018 | -0.0890 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | TP | gradual | +0.0946 | +0.1602 | -0.0453 | 2y |
| `combo_z_sum__limit_down_proximity_early__volume_weighted_price_position` | TP | persistent | +0.0945 | +0.1410 | +0.1206 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0944 | +0.1619 | +0.0982 | ∞ |
| `combo_mean__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.0938 | +0.1718 | -0.0570 | 2y |
| `close_vs_open_range` | TP | gradual | +0.0931 | +0.2187 | -0.0831 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.0928 | +0.1791 | +0.0672 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.0912 | +0.1511 | +0.1250 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0900 | +0.1568 | +0.1039 | ∞ |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | TP | gradual | +0.0898 | +0.1642 | -0.1156 | 2y |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | TP | gradual | +0.0892 | +0.1264 | -0.0029 | 2y |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0888 | +0.1747 | -0.0705 | 2y |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | gradual | +0.0886 | +0.1909 | -0.0074 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0870 | +0.1843 | +0.0649 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0868 | +0.1454 | +0.1150 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | TP | gradual | +0.0861 | +0.1675 | -0.0014 | 2y |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | TP | gradual | +0.0860 | +0.1324 | -0.0806 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0849 | +0.1743 | +0.0798 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | gradual | +0.0841 | +0.1651 | -0.0281 | 2y |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0832 | +0.1283 | +0.1239 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0830 | +0.1740 | +0.0745 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0825 | +0.2095 | +0.0649 | ∞ |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | TP | gradual | +0.0823 | +0.1936 | -0.0776 | 2y |
| `combo_min__first_bar_return__limit_down_proximity_early` | TP | persistent | +0.0822 | +0.1530 | +0.1233 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0819 | +0.1412 | +0.1421 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0817 | +0.1293 | +0.1257 | ∞ |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.0817 | +0.1708 | +0.0456 | ∞ |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.0814 | +0.1313 | +0.0607 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0802 | +0.0835 | +0.1344 | ∞ |
| `combo_max__yesterday_first_30min_return__limit_down_proximity_early` | TP | persistent | +0.0802 | +0.0392 | +0.1538 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0801 | +0.1735 | +0.1094 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0797 | +0.1820 | +0.0509 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0796 | +0.1442 | +0.1059 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0789 | +0.1366 | +0.1130 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0781 | +0.1616 | -0.0242 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0780 | +0.1727 | -0.0641 | 2y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.0778 | +0.1847 | +0.0017 | 2y |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0778 | +0.1387 | +0.0217 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0776 | +0.1667 | -0.0001 | 2y |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0775 | +0.2033 | -0.0561 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.0774 | +0.1291 | +0.0692 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0767 | +0.2129 | +0.0668 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0766 | +0.0820 | +0.1018 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | TP | gradual | +0.0753 | +0.1717 | -0.0690 | 2y |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | TP | persistent | +0.0747 | +0.1498 | +0.0176 | 2y |
| `combo_max__max_up_ret__impulse_bar_dominance` | TP | gradual | +0.0746 | +0.1403 | -0.0761 | 2y |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | TP | gradual | +0.0741 | +0.1353 | -0.0071 | 2y |
| `max_up_ret` | TP | gradual | +0.0739 | +0.1636 | -0.0753 | 2y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | TP | gradual | +0.0735 | +0.1687 | -0.0686 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0725 | +0.1598 | +0.0903 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0724 | +0.2210 | +0.0502 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0722 | +0.1788 | +0.0652 | ∞ |
| `net_volume_flow` | Median | gradual | +0.0717 | +0.2054 | -0.0663 | 2y |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | TP | gradual | +0.0708 | +0.2053 | -0.0784 | 2y |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | TP | gradual | +0.0703 | +0.1982 | -0.0377 | 2y |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | TP | gradual | +0.0685 | +0.1962 | -0.0346 | 2y |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0660 | +0.1554 | +0.1204 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.0657 | +0.1334 | +0.1140 | ∞ |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0653 | +0.1664 | +0.0917 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0644 | +0.1319 | +0.0080 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0638 | +0.1735 | +0.1144 | ∞ |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0628 | +0.1841 | -0.0596 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0627 | +0.1368 | +0.0847 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0620 | +0.1167 | +0.0941 | ∞ |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.0612 | +0.1900 | -0.0929 | 2y |
| `first_bar_return` | TP | persistent | +0.0607 | +0.1228 | +0.0226 | 2y |
| `combo_mean__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0588 | +0.1735 | -0.0304 | 2y |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0577 | +0.1494 | +0.0044 | 2y |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.0572 | +0.1946 | +0.0272 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0546 | +0.0855 | +0.1440 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.0535 | +0.1506 | +0.0898 | ∞ |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.0533 | +0.1179 | +0.0435 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0505 | +0.1121 | +0.0299 | ∞ |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0496 | +0.1711 | +0.0451 | ∞ |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0491 | +0.1651 | +0.0170 | 2y |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0428 | +0.1826 | +0.0538 | ∞ |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0333 | +0.1095 | +0.0851 | ∞ |
| `combo_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | gradual | +0.0144 | +0.0759 | -0.0765 | 2y |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | gradual | +0.0135 | +0.0761 | -0.0765 | 2y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.0083 | +0.1126 | -0.1052 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0535 | -0.0299 | +0.0233 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=37, persistent=80

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.053 → Y2:-0.030 → Y3:+0.023

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.721±0.052 | 0.702±0.032 | 73% | WEAK |
| ic_ir | 0.596±0.147 | 0.560±0.086 | 67% | WEAK |
| p_value | 0.004±0.005 | 0.001±0.001 | 24% | USEFUL |
| max_corr | 0.851±0.117 | 0.866±0.176 | 37% | USEFUL |
| deflated_ic | 0.173±0.038 | 0.200±0.033 | 74% | WEAK |
| overall_ic | 0.173±0.038 | 0.200±0.033 | 75% | WEAK |
| raw_ic | 0.083±0.016 | 0.093±0.012 | 75% | WEAK |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 7/20 top rejects are profitable (35%)

- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188
- `combo_z_sum__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188
- `combo_rank_min__max_up_ret__bar_ret_0`: Train IC=+0.1872, Lock IC=+0.0024, Sharpe=+0.4080

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `combo_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1719, Lock IC=+0.0140, Sharpe=+0.1415
- `combo_z_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1719, Lock IC=+0.0140, Sharpe=+0.1415
- `combo_rel_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1713, Lock IC=+0.0143, Sharpe=+0.1267

**Temporal Validation Gate**: 12/20 top rejects are profitable (60%)

- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2135, Lock IC=+0.0413, Sharpe=+0.4517
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2135, Lock IC=+0.0413, Sharpe=+0.4517
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2133, Lock IC=+0.0412, Sharpe=+0.4517

**BH-FDR Gate**: 3/12 top rejects are profitable (25%)

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Sharpe=+0.1611
- `first_30min_return`: Train IC=+0.1085, Lock IC=+0.0077, Sharpe=+0.0592
- `open_to_current_return`: Train IC=+0.1085, Lock IC=+0.0077, Sharpe=+0.0592

**B6 Yearly IC CV Gate**: 3/20 top rejects are profitable (15%)

- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1615, Lock IC=+0.0427, Sharpe=+0.6518
- `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1615, Lock IC=+0.0427, Sharpe=+0.6518
- `combo_product__max_up_ret__first_bar_sentiment`: Train IC=+0.1701, Lock IC=+0.0113, Sharpe=+0.3291

**B4 Correlation Gate**: 10/20 top rejects are profitable (50%)

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2291, Lock IC=+0.0645, Sharpe=+0.9458
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Sharpe=+0.5172
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2341, Lock IC=+0.0362, Sharpe=+0.3660

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Sharpe=+1.1505

**B2 Rolling Guard**: 17/20 top rejects are profitable (85%)

- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Sharpe=+1.2071
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Sharpe=+1.1213

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_rel_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2655, Lock IC=+0.0902, Sharpe=+1.1893
- `combo_rel_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2655, Lock IC=+0.0902, Sharpe=+1.1893
- `combo_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621

**B3 Composite Floor**: 6/6 top rejects are profitable (100%)

- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788
- `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1912, Lock IC=+0.0954, Sharpe=+0.5787
- `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression`: Train IC=+0.1969, Lock IC=+0.0548, Sharpe=+0.2617

**B6 Yearly IC CV Gate**: 14/14 top rejects are profitable (100%)

- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1429, Lock IC=+0.0568, Sharpe=+1.4431
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904
- `combo_tri_min__smooth_momentum_structure__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904

**B6 Temporal Stability Gate**: 8/8 top rejects are profitable (100%)

- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_mean__max_up_ret__net_volume_flow`: Train IC=+0.2524, Lock IC=+0.0849, Sharpe=+0.5247

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2670, Lock IC=+0.1103, Sharpe=+1.1260

### 159915ETF — `single`

**7-Year Jackknife**: 18/20 top rejects are profitable (90%)

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.1924, Lock IC=+0.1128, Sharpe=+1.3200
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Sharpe=+1.0349

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_clamp_diff__demark_setup_reversal_early__volume_weighted_price_position`: Train IC=+0.1966, Lock IC=+0.1071, Sharpe=+0.9221

**Temporal Validation Gate**: 18/20 top rejects are profitable (90%)

- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Train IC=+0.2156, Lock IC=+0.1112, Sharpe=+1.0666

**BH-FDR Gate**: 5/7 top rejects are profitable (71%)

- `combo_rank_min__volume_weighted_price_position__impulse_bar_dominance`: Train IC=+0.0973, Lock IC=+0.0572, Sharpe=+0.5988
- `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance`: Train IC=+0.0986, Lock IC=+0.0840, Sharpe=+0.3214
- `combo_rank_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.0986, Lock IC=+0.0840, Sharpe=+0.3214

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2047, Lock IC=+0.1185, Sharpe=+1.3299
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2019, Lock IC=+0.1192, Sharpe=+1.1310
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2110, Lock IC=+0.0899, Sharpe=+1.0542

**B6 Yearly IC CV Gate**: 6/8 top rejects are profitable (75%)

- `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943
- `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943
- `combo_rank_min__yesterday_first_30min_return__limit_down_proximity_early`: Train IC=+0.1995, Lock IC=+0.1045, Sharpe=+0.2794

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Sharpe=+1.8009
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2724, Lock IC=+0.1237, Sharpe=+1.5940

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 874 | 78 | 27 | 38 | 13 | 35% | 17% |
| B2 Rolling Guard | 107 | 78 | 41 | 17 | 20 | 53% | 26% |
| Temporal Validation Gate | 97 | 78 | 9 | 25 | 44 | 12% | 56% |
| BH-FDR Gate | 12 | 12 | 8 | 1 | 3 | 67% | 25% |
| B3 Composite Floor | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B6 Yearly IC CV Gate | 26 | 26 | 18 | 5 | 3 | 69% | 12% |
| B4 Correlation Gate | 101 | 78 | 10 | 17 | 51 | 13% | 65% |

**B2 Rolling Guard** — top TP casualties:
- `combo_rel_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1409, Lock IC=+0.0194, Sharpe=+0.8289
- `combo_rel_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1404, Lock IC=+0.0195, Sharpe=+0.6625
- `combo_sig_product__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1341, Lock IC=+0.0176, Sharpe=+0.6337

**Temporal Validation Gate** — top TP casualties:
- `sma100_dist`: Train IC=+0.1056, Lock IC=+0.0455, Sharpe=+0.6172
- `sma10_dist`: Train IC=+0.0626, Lock IC=+0.0444, Sharpe=+0.5378
- `keltner_position_atr10_20d`: Train IC=+0.0207, Lock IC=+0.0265, Sharpe=+0.5125

**BH-FDR Gate** — top TP casualties:
- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Sharpe=+0.1611
- `first_30min_return`: Train IC=+0.1085, Lock IC=+0.0077, Sharpe=+0.0592
- `open_to_current_return`: Train IC=+0.1085, Lock IC=+0.0077, Sharpe=+0.0592

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2291, Lock IC=+0.0645, Sharpe=+0.9458
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1458, Lock IC=+0.0530, Sharpe=+0.6589
- `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.1786, Lock IC=+0.0496, Sharpe=+0.5363

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1791 | 78 | 38 | 12 | 28 | 49% | 36% |
| B2 Rolling Guard | 347 | 78 | 15 | 14 | 49 | 19% | 63% |
| Temporal Validation Gate | 144 | 78 | 22 | 7 | 49 | 28% | 63% |
| BH-FDR Gate | 6 | 6 | 1 | 5 | 0 | 17% | 0% |
| B3 Composite Floor | 6 | 6 | 0 | 0 | 6 | 0% | 100% |
| B6 Yearly IC CV Gate | 14 | 14 | 0 | 0 | 14 | 0% | 100% |
| B6 Temporal Stability Gate | 8 | 8 | 0 | 0 | 8 | 0% | 100% |
| B4 Correlation Gate | 575 | 78 | 0 | 12 | 66 | 0% | 85% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Sharpe=+1.1505

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_min__star50_limit_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1346, Lock IC=+0.0442, Sharpe=+1.2935
- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Sharpe=+1.2071

**Temporal Validation Gate** — top TP casualties:
- `close_location_in_range_3d`: Train IC=+0.0449, Lock IC=+0.0506, Sharpe=+1.3268
- `combo_rel_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2655, Lock IC=+0.0902, Sharpe=+1.1893
- `combo_rel_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2655, Lock IC=+0.0902, Sharpe=+1.1893

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788
- `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1912, Lock IC=+0.0954, Sharpe=+0.5787
- `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression`: Train IC=+0.1969, Lock IC=+0.0548, Sharpe=+0.2617

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1429, Lock IC=+0.0568, Sharpe=+1.4431
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904
- `combo_tri_min__smooth_momentum_structure__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2306, Lock IC=+0.0788, Sharpe=+0.5529
- `combo_mean__max_up_ret__net_volume_flow`: Train IC=+0.2524, Lock IC=+0.0849, Sharpe=+0.5247

**B4 Correlation Gate** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_min__rbreaker_sell_setup_proximity_early__high_low_sequence_momentum`: Train IC=+0.2144, Lock IC=+0.1142, Sharpe=+1.1672

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1161 | 78 | 25 | 18 | 35 | 32% | 45% |
| B2 Rolling Guard | 229 | 78 | 22 | 9 | 47 | 28% | 60% |
| Temporal Validation Gate | 47 | 47 | 11 | 7 | 29 | 23% | 62% |
| BH-FDR Gate | 7 | 7 | 0 | 2 | 5 | 0% | 71% |
| B3 Composite Floor | 78 | 78 | 1 | 3 | 74 | 1% | 95% |
| B6 Yearly IC CV Gate | 8 | 8 | 2 | 0 | 6 | 25% | 75% |
| B4 Correlation Gate | 231 | 78 | 0 | 1 | 77 | 0% | 99% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.1924, Lock IC=+0.1128, Sharpe=+1.3200

**B2 Rolling Guard** — top TP casualties:
- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.1883, Lock IC=+0.1273, Sharpe=+1.0683

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Train IC=+0.2156, Lock IC=+0.1112, Sharpe=+1.0666

**BH-FDR Gate** — top TP casualties:
- `combo_rank_min__volume_weighted_price_position__impulse_bar_dominance`: Train IC=+0.0973, Lock IC=+0.0572, Sharpe=+0.5988
- `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance`: Train IC=+0.0986, Lock IC=+0.0840, Sharpe=+0.3214
- `combo_rank_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.0986, Lock IC=+0.0840, Sharpe=+0.3214

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2047, Lock IC=+0.1185, Sharpe=+1.3299
- `combo_rank_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1518, Lock IC=+0.0800, Sharpe=+1.1719
- `combo_rank_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1518, Lock IC=+0.0800, Sharpe=+1.1719

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943
- `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2020, Lock IC=+0.1358, Sharpe=+1.3943
- `combo_rank_min__yesterday_first_30min_return__limit_down_proximity_early`: Train IC=+0.1995, Lock IC=+0.1045, Sharpe=+0.2794

**B4 Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Sharpe=+1.8009
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2208, Lock IC=+0.1183, Sharpe=+1.7926

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (97 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 68 | 50 | 10 | 18 | 22 | 20% | 36% |
| recency_ratio >= 2.5 (late-concentrated) | 25 | 25 | 0 | 23 | 2 | 0% | 92% |

**Top TP killed by recency_ratio cap:**
- `first_bar_return`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `bar_ret_0`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `combo_mean__bar_ret_0__first_bar_sentiment`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `combo_z_sum__bar_ret_0__first_bar_sentiment`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `combo_mean__first_bar_return__first_bar_sentiment`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827

### 500ETF — `single` (144 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 135 | 50 | 0 | 48 | 2 | 0% | 96% |
| recency_ratio >= 2.5 (late-concentrated) | 4 | 4 | 0 | 2 | 2 | 0% | 50% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.1424, Lock IC=+0.0686, Sharpe=+0.4355
- `combo_rank_max__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.1424, Lock IC=+0.0686, Sharpe=+0.4355

### 159915ETF — `single` (47 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 33 | 33 | 11 | 17 | 5 | 33% | 52% |
| recency_ratio >= 2.5 (late-concentrated) | 12 | 12 | 0 | 10 | 2 | 0% | 83% |

**Top TP killed by recency_ratio cap:**
- `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Train IC=+0.2156, Lock IC=+0.1112, Sharpe=+1.0666
- `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.1974, Lock IC=+0.0965, Sharpe=+0.6171
- `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2016, Lock IC=+0.0980, Sharpe=+0.4373
- `combo_z_sum__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2016, Lock IC=+0.0980, Sharpe=+0.4373
- `volatility_expansion_trend_vector`: Train IC=+0.1637, Lock IC=+0.0943, Sharpe=+0.3332

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_std_across_regimes`: FP is lower (d=-1.08). Threshold 0.077 → 60% accuracy.
- `half_ratio`: FP is higher (d=+0.79). Threshold 1.375 → 79% accuracy.
- `ic_cv`: FP is higher (d=+0.74). Threshold 0.874 → 72% accuracy.
- `recency_ratio`: FP is higher (d=+0.65). Threshold 2.025 → 70% accuracy.
- `weak_link_cv`: FP is lower (d=-0.59). Threshold 1.086 → 72% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/16
- Decaying signal (half ratio < 0.3): 0/16
- Weak component (CV > 2.0): 0/16
- Regime-dependent (≥2 negative regimes): 0/16

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_weighted_price_position` | 9 | 9 | 18 | 50% |  |
| `first_bar_sentiment` | 5 | 31 | 36 | 14% |  |
| `bar_ret_0` | 2 | 14 | 16 | 12% |  |
| `max_up_ret` | 5 | 83 | 88 | 6% |  |
| `opening_drive_thrust_ratio` | 3 | 72 | 75 | 4% |  |
| `volatility_expansion_trend_vector` | 1 | 30 | 31 | 3% |  |
| `first_bar_return` | 1 | 34 | 35 | 3% |  |
| `yesterday_early_vwap_dev` | 0 | 4 | 4 | 0% |  |
| `early_body_momentum` | 0 | 10 | 10 | 0% |  |
| `trend_day_regime_conviction` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 11 | 11 | 0% |  |
| `impulse_bar_dominance` | 0 | 6 | 6 | 0% |  |
| `bar_body_rng_0` | 0 | 33 | 33 | 0% |  |
| `body_size_progression` | 0 | 7 | 7 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 7 | 7 | 0% |  |
| `max_down_ret` | 0 | 17 | 17 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 74 | 74 | 0% |  |
| `close_vs_open_range` | 0 | 18 | 18 | 0% |  |
| `yesterday_first_30min_return` | 0 | 10 | 10 | 0% |  |
| `demark_setup_reversal_early` | 0 | 6 | 6 | 0% |  |
| `limit_down_proximity_early` | 0 | 10 | 10 | 0% |  |
| `smooth_momentum_structure` | 0 | 5 | 5 | 0% |  |
| `star50_limit_proximity_early` | 0 | 49 | 49 | 0% |  |
| `trend_bar_close_consistency` | 0 | 9 | 9 | 0% |  |
| `net_volume_flow` | 0 | 25 | 25 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=8, TP=146, FP rate=5%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=3, TP=14, FP rate=18%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=66, FP rate=1%

