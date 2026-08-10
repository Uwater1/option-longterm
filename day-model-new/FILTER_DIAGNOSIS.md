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
| 300ETF | single | 26 | 8 | `[9, 6, 3, 2, 2, 2, 1, 1]` | 0.2537 | 0 | 3 | 23 | 0% | 0.72 |
| 500ETF | single | 317 | 117 | `[15, 14, 12, 12, 11, 9, 8, 8, 7, 7, 7, 6, ... (117 clusters)]` | 0.2164 | 0 | 14 | 303 | 0% | 0.82 |
| 159915ETF | single | 37 | 22 | `[3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ... (22 clusters)]` | 0.3425 | 0 | 1 | 36 | 0% | 0.85 |

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

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0394, Sharpe=-0.0493)
- Admission: Train IC=+0.2037, Deflated=+0.2027, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156 | 2022: +0.028 | 2023: +0.137 | 2024: +0.039 | 2025: +0.058 | 2026: -0.140
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.055 | 2017: +0.207 | 2018: +0.385 | 2019: +0.133 | 2020: +0.033 | 2021: +0.203 | 2022: +0.122 | 2023: +0.108 | 2024: +0.061 | 2025: +0.105 | 2026: -0.366
- IC CV=0.64, Neg years (linear/tail)=1/0 of 8, Half ratio=1.68, Recency ratio=1.16
- Early IC=+0.0663, Recent IC=+0.0769, 1st-half IC=+0.0657, 2nd-half IC=+0.1101, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.26)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.068, Q3_mid=+0.101, Q4=+0.064, Q5_high_vol=+0.156

**`combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0358, Sharpe=-0.4253)
- Admission: Train IC=+0.1921, Deflated=+0.1919, IR=0.71, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.087 | 2017: -0.034 | 2018: +0.174 | 2019: +0.091 | 2020: +0.046 | 2021: +0.165 | 2022: +0.025 | 2023: +0.157 | 2024: +0.033 | 2025: +0.055 | 2026: -0.208
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.226 | 2017: +0.015 | 2018: +0.309 | 2019: +0.111 | 2020: +0.093 | 2021: +0.431 | 2022: +0.175 | 2023: +0.139 | 2024: +0.161 | 2025: -0.073 | 2026: -0.408
- IC CV=0.77, Neg years (linear/tail)=1/0 of 8, Half ratio=2.45, Recency ratio=1.71
- Early IC=+0.0618, Recent IC=+0.1058, 1st-half IC=+0.0462, 2nd-half IC=+0.1132, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.26)
- Regime ICs: Q1_low_vol=-0.010, Q2=+0.039, Q3_mid=+0.091, Q4=+0.143, Q5_high_vol=+0.132

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0263, Sharpe=-0.6092)
- Admission: Train IC=+0.2222, Deflated=+0.2224, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.072 | 2017: -0.027 | 2018: +0.196 | 2019: +0.082 | 2020: +0.053 | 2021: +0.168 | 2022: -0.006 | 2023: +0.151 | 2024: +0.061 | 2025: +0.035 | 2026: -0.201
- Yearly Tail ICs:   2015: +0.019 | 2016: +0.242 | 2017: +0.127 | 2018: +0.378 | 2019: +0.313 | 2020: +0.139 | 2021: +0.409 | 2022: +0.094 | 2023: +0.233 | 2024: +0.230 | 2025: -0.104 | 2026: -0.180
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.75, Recency ratio=1.61
- Early IC=+0.0687, Recent IC=+0.1104, 1st-half IC=+0.0673, 2nd-half IC=+0.1180, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.045, Q3_mid=+0.097, Q4=+0.141, Q5_high_vol=+0.135

### 500ETF — `single` Median Features

**`combo_tri_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0869, Sharpe=-0.0245)
- Admission: Train IC=+0.2152, Deflated=+0.2147, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.132 | 2017: +0.195 | 2018: +0.179 | 2019: +0.097 | 2020: +0.137 | 2021: +0.076 | 2022: +0.111 | 2023: +0.058 | 2024: +0.108 | 2025: +0.069 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.173 | 2016: +0.183 | 2017: +0.179 | 2018: +0.234 | 2019: +0.098 | 2020: +0.092 | 2021: +0.216 | 2022: +0.156 | 2023: -0.018 | 2024: -0.016 | 2025: -0.053 | 2026: -0.129
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.50
- Early IC=+0.2145, Recent IC=+0.1062, 1st-half IC=+0.2048, 2nd-half IC=+0.1248, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.059, Q3_mid=+0.205, Q4=+0.104, Q5_high_vol=+0.231

**`combo_max__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0860, Sharpe=-0.0615)
- Admission: Train IC=+0.2268, Deflated=+0.2252, IR=0.64, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.088 | 2017: +0.226 | 2018: +0.245 | 2019: +0.136 | 2020: +0.161 | 2021: +0.165 | 2022: +0.097 | 2023: +0.106 | 2024: +0.148 | 2025: +0.076 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.231 | 2016: -0.044 | 2017: +0.170 | 2018: +0.368 | 2019: +0.128 | 2020: +0.233 | 2021: +0.285 | 2022: +0.116 | 2023: +0.052 | 2024: +0.277 | 2025: -0.025 | 2026: -0.274
- IC CV=0.29, Neg years (linear/tail)=0/1 of 8, Half ratio=0.86, Recency ratio=0.75
- Early IC=+0.2156, Recent IC=+0.1625, 1st-half IC=+0.1968, 2nd-half IC=+0.1689, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.223, Q2=+0.039, Q3_mid=+0.209, Q4=+0.195, Q5_high_vol=+0.241

**`combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0848, Sharpe=-0.0250)
- Admission: Train IC=+0.2469, Deflated=+0.2463, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.048 | 2017: +0.229 | 2018: +0.163 | 2019: +0.123 | 2020: +0.154 | 2021: +0.119 | 2022: +0.097 | 2023: +0.092 | 2024: +0.131 | 2025: +0.126 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.070 | 2017: +0.232 | 2018: +0.347 | 2019: +0.377 | 2020: +0.059 | 2021: +0.270 | 2022: +0.120 | 2023: +0.181 | 2024: +0.291 | 2025: +0.073 | 2026: -0.295
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.65
- Early IC=+0.2084, Recent IC=+0.1364, 1st-half IC=+0.1849, 2nd-half IC=+0.1381, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.066, Q3_mid=+0.196, Q4=+0.189, Q5_high_vol=+0.175

**`combo_max__early_body_momentum__close_vs_open_range`** (Lock IC=+0.0840, Sharpe=-0.1237)
- Admission: Train IC=+0.2336, Deflated=+0.2326, IR=0.68, Mono=0.77, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.063 | 2017: +0.152 | 2018: +0.110 | 2019: +0.029 | 2020: +0.092 | 2021: +0.052 | 2022: +0.100 | 2023: +0.078 | 2024: +0.131 | 2025: +0.142 | 2026: -0.100
- Yearly Tail ICs:   2015: +0.306 | 2016: +0.211 | 2017: +0.203 | 2018: +0.106 | 2019: +0.027 | 2020: +0.190 | 2021: +0.235 | 2022: +0.096 | 2023: +0.035 | 2024: +0.281 | 2025: +0.147 | 2026: -0.076
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.46
- Early IC=+0.1555, Recent IC=+0.0723, 1st-half IC=+0.1382, 2nd-half IC=+0.0743, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.015, Q3_mid=+0.153, Q4=+0.164, Q5_high_vol=+0.086

**`combo_mean__close_vs_open_range__vwap_close_divergence_trend`** (Lock IC=+0.0823, Sharpe=-0.1567)
- Admission: Train IC=+0.1718, Deflated=+0.1714, IR=0.64, Mono=0.74, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.042 | 2017: +0.181 | 2018: +0.079 | 2019: +0.080 | 2020: +0.088 | 2021: +0.073 | 2022: +0.090 | 2023: +0.102 | 2024: +0.100 | 2025: +0.148 | 2026: -0.090
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.122 | 2017: +0.248 | 2018: +0.206 | 2019: +0.192 | 2020: +0.040 | 2021: +0.317 | 2022: +0.109 | 2023: +0.169 | 2024: +0.225 | 2025: +0.104 | 2026: -0.182
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.56
- Early IC=+0.1434, Recent IC=+0.0802, 1st-half IC=+0.1329, 2nd-half IC=+0.0814, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.004, Q3_mid=+0.152, Q4=+0.142, Q5_high_vol=+0.087

**`combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0777, Sharpe=-0.2762)
- Admission: Train IC=+0.2458, Deflated=+0.2451, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.042 | 2017: +0.160 | 2018: +0.194 | 2019: +0.168 | 2020: +0.190 | 2021: +0.148 | 2022: +0.046 | 2023: +0.103 | 2024: +0.138 | 2025: +0.065 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.304 | 2016: -0.039 | 2017: +0.226 | 2018: +0.247 | 2019: +0.289 | 2020: +0.105 | 2021: +0.093 | 2022: +0.268 | 2023: +0.065 | 2024: +0.102 | 2025: +0.144 | 2026: -0.044
- IC CV=0.34, Neg years (linear/tail)=0/1 of 8, Half ratio=1.08, Recency ratio=0.84
- Early IC=+0.2014, Recent IC=+0.1691, 1st-half IC=+0.1576, 2nd-half IC=+0.1703, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.086, Q3_mid=+0.176, Q4=+0.156, Q5_high_vol=+0.259

**`combo_max__opening_auction_imbalance__first_bar_return`** (Lock IC=+0.0699, Sharpe=-0.0946)
- Admission: Train IC=+0.2333, Deflated=+0.2324, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.109 | 2017: +0.172 | 2018: +0.235 | 2019: +0.118 | 2020: +0.108 | 2021: +0.109 | 2022: +0.094 | 2023: +0.073 | 2024: +0.112 | 2025: +0.105 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.205 | 2016: +0.029 | 2017: +0.161 | 2018: +0.277 | 2019: +0.135 | 2020: +0.276 | 2021: +0.285 | 2022: +0.186 | 2023: +0.352 | 2024: +0.203 | 2025: -0.085 | 2026: -0.457
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.55
- Early IC=+0.1988, Recent IC=+0.1086, 1st-half IC=+0.1806, 2nd-half IC=+0.1411, Neg regimes=0/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.015, Q3_mid=+0.196, Q4=+0.170, Q5_high_vol=+0.207

**`combo_max__early_body_momentum__max_down_ret`** (Lock IC=+0.0672, Sharpe=-0.0809)
- Admission: Train IC=+0.1974, Deflated=+0.1966, IR=0.53, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.046 | 2017: +0.178 | 2018: +0.146 | 2019: +0.063 | 2020: +0.099 | 2021: +0.066 | 2022: +0.060 | 2023: +0.041 | 2024: +0.122 | 2025: +0.149 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.170 | 2017: +0.164 | 2018: +0.045 | 2019: +0.125 | 2020: +0.046 | 2021: +0.253 | 2022: +0.185 | 2023: +0.254 | 2024: +0.264 | 2025: +0.036 | 2026: -0.192
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.43
- Early IC=+0.1909, Recent IC=+0.0828, 1st-half IC=+0.1514, 2nd-half IC=+0.0925, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.018, Q3_mid=+0.157, Q4=+0.160, Q5_high_vol=+0.113

**`combo_rank_max__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0591, Sharpe=-0.1080)
- Admission: Train IC=+0.2096, Deflated=+0.2093, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.067 | 2017: +0.131 | 2018: +0.204 | 2019: +0.118 | 2020: +0.070 | 2021: +0.093 | 2022: +0.092 | 2023: +0.081 | 2024: +0.107 | 2025: +0.095 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.177 | 2016: -0.101 | 2017: +0.048 | 2018: +0.344 | 2019: +0.174 | 2020: +0.162 | 2021: +0.297 | 2022: +0.227 | 2023: +0.377 | 2024: +0.250 | 2025: -0.089 | 2026: -0.466
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=0.46
- Early IC=+0.1788, Recent IC=+0.0830, 1st-half IC=+0.1510, 2nd-half IC=+0.1224, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.022, Q3_mid=+0.143, Q4=+0.151, Q5_high_vol=+0.171

**`combo_max__first_bar_return__early_order_flow_imbalance`** (Lock IC=+0.0579, Sharpe=-0.1515)
- Admission: Train IC=+0.2125, Deflated=+0.2123, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.056 | 2017: +0.124 | 2018: +0.197 | 2019: +0.117 | 2020: +0.066 | 2021: +0.077 | 2022: +0.097 | 2023: +0.070 | 2024: +0.104 | 2025: +0.090 | 2026: -0.154
- Yearly Tail ICs:   2015: +0.201 | 2016: -0.097 | 2017: +0.063 | 2018: +0.335 | 2019: +0.208 | 2020: +0.172 | 2021: +0.315 | 2022: +0.186 | 2023: +0.314 | 2024: +0.190 | 2025: -0.100 | 2026: -0.441
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.79, Recency ratio=0.39
- Early IC=+0.1829, Recent IC=+0.0715, 1st-half IC=+0.1453, 2nd-half IC=+0.1150, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.015, Q3_mid=+0.134, Q4=+0.155, Q5_high_vol=+0.163

**`combo_sig_product__opening_auction_imbalance__first_bar_return`** (Lock IC=+0.0533, Sharpe=-0.0375)
- Admission: Train IC=+0.2069, Deflated=+0.2070, IR=0.54, Mono=0.69, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.035 | 2017: +0.154 | 2018: +0.191 | 2019: +0.111 | 2020: +0.089 | 2021: +0.063 | 2022: +0.053 | 2023: +0.070 | 2024: +0.052 | 2025: +0.104 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.039 | 2017: +0.221 | 2018: +0.425 | 2019: +0.230 | 2020: +0.167 | 2021: +0.137 | 2022: +0.182 | 2023: +0.092 | 2024: +0.126 | 2025: +0.162 | 2026: -0.365
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.93, Recency ratio=0.50
- Early IC=+0.1531, Recent IC=+0.0762, 1st-half IC=+0.1228, 2nd-half IC=+0.1142, Neg regimes=1/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.045, Q3_mid=+0.134, Q4=+0.193, Q5_high_vol=+0.111

**`combo_ratio__max_down_ret__opening_auction_imbalance`** (Lock IC=+0.0520, Sharpe=-0.4928)
- Admission: Train IC=+0.2207, Deflated=+0.2209, IR=0.82, Mono=0.77, p=0.0000, MaxCorr=0.10
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004 | 2022: -0.056 | 2023: +0.007 | 2024: +0.084 | 2025: +0.166 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.355 | 2016: +0.225 | 2017: +0.296 | 2018: +0.169 | 2019: +0.110 | 2020: +0.294 | 2021: +0.250 | 2022: -0.197 | 2023: -0.187 | 2024: +0.121 | 2025: +0.191 | 2026: +0.074
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.40
- Early IC=+0.1732, Recent IC=+0.0693, 1st-half IC=+0.1612, 2nd-half IC=+0.0986, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.225, Q2=+0.016, Q3_mid=+0.115, Q4=+0.147, Q5_high_vol=+0.158

**`combo_sig_product__first_bar_return__vwap_close_divergence_trend`** (Lock IC=+0.0446, Sharpe=-0.0937)
- Admission: Train IC=+0.1877, Deflated=+0.1876, IR=0.62, Mono=0.73, p=0.0002, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.095 | 2017: +0.070 | 2018: +0.186 | 2019: +0.182 | 2020: +0.100 | 2021: +0.069 | 2022: +0.115 | 2023: +0.119 | 2024: +0.058 | 2025: +0.037 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.121 | 2017: +0.027 | 2018: +0.297 | 2019: +0.348 | 2020: +0.039 | 2021: +0.073 | 2022: +0.269 | 2023: +0.199 | 2024: +0.237 | 2025: -0.120 | 2026: +0.018
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.47
- Early IC=+0.1815, Recent IC=+0.0847, 1st-half IC=+0.1462, 2nd-half IC=+0.1268, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.086, Q3_mid=+0.114, Q4=+0.133, Q5_high_vol=+0.209

**`combo_rel_diff__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0246, Sharpe=-0.3481)
- Admission: Train IC=+0.2356, Deflated=+0.2342, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.138 | 2016: -0.019 | 2017: +0.138 | 2018: +0.157 | 2019: +0.040 | 2020: +0.167 | 2021: +0.077 | 2022: +0.001 | 2023: +0.006 | 2024: +0.030 | 2025: -0.016 | 2026: +0.136
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.181 | 2017: +0.308 | 2018: +0.474 | 2019: +0.147 | 2020: +0.467 | 2021: +0.033 | 2022: -0.172 | 2023: -0.059 | 2024: +0.013 | 2025: -0.063 | 2026: +0.132
- IC CV=0.60, Neg years (linear/tail)=1/0 of 8, Half ratio=1.36, Recency ratio=1.01
- Early IC=+0.1214, Recent IC=+0.1221, 1st-half IC=+0.0801, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.052, Q3_mid=+0.105, Q4=+0.071, Q5_high_vol=+0.153

### 159915ETF — `single` Median Features

**`combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0930, Sharpe=-0.0233)
- Admission: Train IC=+0.1964, Deflated=+0.1955, IR=0.48, Mono=0.67, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.152 | 2017: +0.027 | 2018: +0.139 | 2019: +0.109 | 2020: +0.129 | 2021: +0.137 | 2022: +0.128 | 2023: +0.116 | 2024: +0.040 | 2025: +0.104 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.060 | 2016: +0.137 | 2017: +0.192 | 2018: +0.297 | 2019: +0.174 | 2020: +0.009 | 2021: +0.301 | 2022: +0.076 | 2023: +0.136 | 2024: +0.171 | 2025: -0.015 | 2026: +0.087
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.70
- Early IC=+0.1896, Recent IC=+0.1334, 1st-half IC=+0.1709, 2nd-half IC=+0.1376, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.128, Q3_mid=+0.195, Q4=+0.161, Q5_high_vol=+0.157

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0595, Sharpe=+1.0296)
- Admission: Train IC=+0.2489, Deflated=+0.2489, IR=0.45, Mono=0.67, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.116 | 2017: -0.055 | 2018: +0.141 | 2019: +0.103 | 2020: +0.075 | 2021: +0.141 | 2022: +0.036 | 2023: +0.136 | 2024: +0.056 | 2025: +0.049 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.399 | 2016: +0.177 | 2017: -0.023 | 2018: +0.310 | 2019: +0.306 | 2020: +0.168 | 2021: +0.346 | 2022: +0.251 | 2023: +0.164 | 2024: +0.411 | 2025: +0.064 | 2026: +0.091
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=0.87, Recency ratio=0.72
- Early IC=+0.1489, Recent IC=+0.1076, 1st-half IC=+0.1249, 2nd-half IC=+0.1090, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=-0.013, Q2=+0.020, Q3_mid=+0.066, Q4=+0.192, Q5_high_vol=+0.219

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0778, Sharpe=+0.6460)
- Admission: Train IC=+0.2525, Deflated=+0.2516, IR=0.63, Mono=0.70, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.029 | 2018: +0.197 | 2019: +0.148 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.091 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.051 | 2026: +0.079
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=1.39, Recency ratio=0.66
- Early IC=+0.1319, Recent IC=+0.0875, 1st-half IC=+0.0947, 2nd-half IC=+0.1320, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.055, Q3_mid=+0.079, Q4=+0.169, Q5_high_vol=+0.208

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0748, Sharpe=+0.6394)
- Admission: Train IC=+0.1905, Deflated=+0.1895, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.035 | 2018: +0.163 | 2019: +0.134 | 2020: +0.028 | 2021: +0.128 | 2022: +0.031 | 2023: +0.135 | 2024: +0.037 | 2025: +0.094 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.392 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.095
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=1.68, Recency ratio=0.64
- Early IC=+0.1204, Recent IC=+0.0773, 1st-half IC=+0.0674, 2nd-half IC=+0.1132, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.053, Q3_mid=+0.040, Q4=+0.139, Q5_high_vol=+0.192

**`combo_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0731, Sharpe=+0.6393)
- Admission: Train IC=+0.2023, Deflated=+0.2012, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.063 | 2017: -0.024 | 2018: +0.180 | 2019: +0.147 | 2020: +0.024 | 2021: +0.124 | 2022: +0.040 | 2023: +0.162 | 2024: +0.031 | 2025: +0.092 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.237 | 2016: +0.092 | 2017: +0.022 | 2018: +0.376 | 2019: +0.237 | 2020: +0.195 | 2021: +0.354 | 2022: +0.222 | 2023: +0.280 | 2024: +0.153 | 2025: -0.025 | 2026: +0.184
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.26, Recency ratio=0.52
- Early IC=+0.1435, Recent IC=+0.0742, 1st-half IC=+0.0944, 2nd-half IC=+0.1192, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.057, Q3_mid=+0.070, Q4=+0.138, Q5_high_vol=+0.214

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0673, Sharpe=+0.5857)
- Admission: Train IC=+0.2077, Deflated=+0.2074, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.114 | 2017: +0.003 | 2018: +0.209 | 2019: +0.105 | 2020: +0.047 | 2021: +0.144 | 2022: +0.084 | 2023: +0.107 | 2024: +0.017 | 2025: +0.067 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.216 | 2016: +0.118 | 2017: +0.039 | 2018: +0.273 | 2019: +0.240 | 2020: +0.155 | 2021: +0.445 | 2022: +0.268 | 2023: +0.064 | 2024: +0.157 | 2025: +0.233 | 2026: +0.018
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=1.18, Recency ratio=0.76
- Early IC=+0.1251, Recent IC=+0.0956, 1st-half IC=+0.1062, 2nd-half IC=+0.1252, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.050, Q3_mid=+0.085, Q4=+0.156, Q5_high_vol=+0.213

**`combo_tri_min__max_up_ret__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0632, Sharpe=+0.4323)
- Admission: Train IC=+0.1956, Deflated=+0.1946, IR=0.54, Mono=0.66, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.088 | 2017: +0.013 | 2018: +0.178 | 2019: +0.109 | 2020: +0.021 | 2021: +0.100 | 2022: +0.035 | 2023: +0.157 | 2024: +0.051 | 2025: +0.042 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.081 | 2017: +0.098 | 2018: +0.400 | 2019: +0.257 | 2020: +0.195 | 2021: +0.173 | 2022: +0.117 | 2023: +0.331 | 2024: +0.158 | 2025: -0.104 | 2026: +0.081
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.38
- Early IC=+0.1590, Recent IC=+0.0604, 1st-half IC=+0.1191, 2nd-half IC=+0.1058, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.056, Q3_mid=+0.077, Q4=+0.133, Q5_high_vol=+0.215

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0453, Sharpe=+0.4290)
- Admission: Train IC=+0.1900, Deflated=+0.1902, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.067 | 2017: -0.008 | 2018: +0.189 | 2019: +0.066 | 2020: +0.019 | 2021: +0.179 | 2022: +0.042 | 2023: +0.185 | 2024: +0.029 | 2025: +0.097 | 2026: -0.205
- Yearly Tail ICs:   2015: -0.008 | 2016: +0.182 | 2017: +0.145 | 2018: +0.340 | 2019: +0.226 | 2020: +0.042 | 2021: +0.375 | 2022: +0.344 | 2023: +0.342 | 2024: +0.088 | 2025: +0.081 | 2026: -0.039
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=1.70, Recency ratio=1.36
- Early IC=+0.0729, Recent IC=+0.0989, 1st-half IC=+0.0626, 2nd-half IC=+0.1064, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.26)
- Regime ICs: Q1_low_vol=+0.010, Q2=+0.052, Q3_mid=+0.105, Q4=+0.110, Q5_high_vol=+0.139

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0696, Sharpe=+0.4252)
- Admission: Train IC=+0.2341, Deflated=+0.2329, IR=0.55, Mono=0.66, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.046 | 2017: -0.017 | 2018: +0.177 | 2019: +0.150 | 2020: +0.038 | 2021: +0.122 | 2022: +0.050 | 2023: +0.166 | 2024: +0.034 | 2025: +0.098 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.428 | 2016: -0.077 | 2017: -0.003 | 2018: +0.264 | 2019: +0.283 | 2020: +0.233 | 2021: +0.362 | 2022: +0.328 | 2023: +0.141 | 2024: +0.273 | 2025: +0.108 | 2026: +0.113
- IC CV=0.77, Neg years (linear/tail)=1/2 of 8, Half ratio=1.16, Recency ratio=0.54
- Early IC=+0.1471, Recent IC=+0.0798, 1st-half IC=+0.1051, 2nd-half IC=+0.1217, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.057, Q3_mid=+0.085, Q4=+0.143, Q5_high_vol=+0.204

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0643, Sharpe=+0.4183)
- Admission: Train IC=+0.2737, Deflated=+0.2728, IR=0.70, Mono=0.72, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.097 | 2017: +0.005 | 2018: +0.184 | 2019: +0.118 | 2020: +0.043 | 2021: +0.130 | 2022: +0.035 | 2023: +0.176 | 2024: +0.055 | 2025: +0.050 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.342 | 2016: +0.123 | 2017: +0.102 | 2018: +0.378 | 2019: +0.304 | 2020: +0.226 | 2021: +0.489 | 2022: +0.142 | 2023: +0.364 | 2024: +0.242 | 2025: -0.042 | 2026: +0.103
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.51
- Early IC=+0.1707, Recent IC=+0.0865, 1st-half IC=+0.1322, 2nd-half IC=+0.1209, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.066, Q3_mid=+0.091, Q4=+0.170, Q5_high_vol=+0.222

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0623, Sharpe=+0.4134)
- Admission: Train IC=+0.2604, Deflated=+0.2599, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.097 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.158 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.050 | 2026: +0.178
- IC CV=0.88, Neg years (linear/tail)=1/0 of 8, Half ratio=1.38, Recency ratio=0.82
- Early IC=+0.1410, Recent IC=+0.1152, 1st-half IC=+0.0990, 2nd-half IC=+0.1364, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=-0.021, Q2=+0.035, Q3_mid=+0.096, Q4=+0.210, Q5_high_vol=+0.205

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0615, Sharpe=+0.4019)
- Admission: Train IC=+0.1883, Deflated=+0.1881, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.117 | 2017: -0.020 | 2018: +0.233 | 2019: +0.100 | 2020: +0.054 | 2021: +0.164 | 2022: +0.064 | 2023: +0.130 | 2024: +0.028 | 2025: +0.076 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.119 | 2017: -0.025 | 2018: +0.356 | 2019: +0.281 | 2020: +0.125 | 2021: +0.399 | 2022: +0.230 | 2023: +0.115 | 2024: +0.192 | 2025: +0.198 | 2026: -0.024
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=1.38, Recency ratio=0.85
- Early IC=+0.1291, Recent IC=+0.1094, 1st-half IC=+0.0981, 2nd-half IC=+0.1353, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=+0.019, Q2=+0.061, Q3_mid=+0.094, Q4=+0.180, Q5_high_vol=+0.217

**`combo_tri_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0593, Sharpe=+0.3908)
- Admission: Train IC=+0.1373, Deflated=+0.1371, IR=0.37, Mono=0.67, p=0.0076, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.151 | 2017: +0.021 | 2018: +0.175 | 2019: +0.015 | 2020: +0.030 | 2021: +0.152 | 2022: +0.087 | 2023: +0.041 | 2024: +0.029 | 2025: +0.030 | 2026: +0.056
- Yearly Tail ICs:   2015: -0.022 | 2016: +0.230 | 2017: +0.030 | 2018: +0.229 | 2019: +0.159 | 2020: +0.078 | 2021: +0.190 | 2022: +0.365 | 2023: -0.158 | 2024: +0.243 | 2025: +0.034 | 2026: -0.016
- IC CV=0.75, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=0.85
- Early IC=+0.1070, Recent IC=+0.0913, 1st-half IC=+0.1092, 2nd-half IC=+0.0925, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.026, Q3_mid=+0.073, Q4=+0.124, Q5_high_vol=+0.192

**`combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0515, Sharpe=+0.3469)
- Admission: Train IC=+0.2130, Deflated=+0.2127, IR=0.47, Mono=0.67, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.065 | 2017: +0.029 | 2018: +0.199 | 2019: +0.066 | 2020: -0.003 | 2021: +0.160 | 2022: +0.054 | 2023: +0.179 | 2024: +0.042 | 2025: +0.100 | 2026: -0.200
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.040 | 2017: +0.109 | 2018: +0.363 | 2019: +0.159 | 2020: +0.157 | 2021: +0.400 | 2022: +0.297 | 2023: +0.270 | 2024: +0.209 | 2025: +0.050 | 2026: -0.242
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=1.44, Recency ratio=1.13
- Early IC=+0.0696, Recent IC=+0.0785, 1st-half IC=+0.0708, 2nd-half IC=+0.1020, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.26)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.062, Q3_mid=+0.108, Q4=+0.078, Q5_high_vol=+0.140

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0759, Sharpe=+0.3372)
- Admission: Train IC=+0.2089, Deflated=+0.2086, IR=0.53, Mono=0.73, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109 | 2023: +0.058 | 2024: +0.021 | 2025: +0.045 | 2026: +0.149
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.260 | 2017: -0.063 | 2018: +0.287 | 2019: +0.204 | 2020: +0.254 | 2021: +0.174 | 2022: +0.239 | 2023: -0.083 | 2024: +0.166 | 2025: -0.078 | 2026: +0.217
- IC CV=1.16, Neg years (linear/tail)=1/1 of 8, Half ratio=0.91, Recency ratio=0.58
- Early IC=+0.1172, Recent IC=+0.0678, 1st-half IC=+0.0916, 2nd-half IC=+0.0836, Neg regimes=1/5
- Regime ICs: Q1_low_vol=-0.036, Q2=+0.007, Q3_mid=+0.034, Q4=+0.162, Q5_high_vol=+0.179

**`combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0617, Sharpe=+0.3344)
- Admission: Train IC=+0.2220, Deflated=+0.2212, IR=0.50, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.096 | 2017: +0.022 | 2018: +0.207 | 2019: +0.106 | 2020: +0.038 | 2021: +0.137 | 2022: +0.067 | 2023: +0.130 | 2024: +0.017 | 2025: +0.091 | 2026: -0.048
- Yearly Tail ICs:   2015: +0.291 | 2016: +0.022 | 2017: -0.041 | 2018: +0.335 | 2019: +0.142 | 2020: +0.268 | 2021: +0.367 | 2022: +0.326 | 2023: +0.220 | 2024: +0.148 | 2025: +0.285 | 2026: -0.046
- IC CV=0.65, Neg years (linear/tail)=0/1 of 8, Half ratio=1.32, Recency ratio=0.77
- Early IC=+0.1141, Recent IC=+0.0876, 1st-half IC=+0.0938, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.052, Q3_mid=+0.098, Q4=+0.137, Q5_high_vol=+0.192

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0603, Sharpe=+0.3065)
- Admission: Train IC=+0.2705, Deflated=+0.2699, IR=0.79, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.071 | 2017: -0.018 | 2018: +0.234 | 2019: +0.116 | 2020: +0.041 | 2021: +0.178 | 2022: +0.027 | 2023: +0.142 | 2024: +0.048 | 2025: +0.073 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.055 | 2017: +0.064 | 2018: +0.369 | 2019: +0.332 | 2020: +0.148 | 2021: +0.582 | 2022: +0.182 | 2023: +0.146 | 2024: +0.202 | 2025: -0.083 | 2026: +0.167
- IC CV=0.70, Neg years (linear/tail)=1/0 of 8, Half ratio=1.27, Recency ratio=0.68
- Early IC=+0.1603, Recent IC=+0.1096, 1st-half IC=+0.1124, 2nd-half IC=+0.1428, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=+0.020, Q2=+0.063, Q3_mid=+0.122, Q4=+0.190, Q5_high_vol=+0.217

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early`** (Lock IC=+0.0582, Sharpe=+0.2990)
- Admission: Train IC=+0.2044, Deflated=+0.2045, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.088 | 2017: -0.057 | 2018: +0.199 | 2019: +0.084 | 2020: +0.067 | 2021: +0.166 | 2022: +0.061 | 2023: +0.128 | 2024: +0.044 | 2025: +0.070 | 2026: -0.105
- Yearly Tail ICs:   2015: +0.128 | 2016: +0.130 | 2017: +0.056 | 2018: +0.441 | 2019: +0.265 | 2020: +0.117 | 2021: +0.245 | 2022: +0.210 | 2023: +0.117 | 2024: +0.192 | 2025: +0.165 | 2026: +0.008
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=1.50, Recency ratio=1.01
- Early IC=+0.1152, Recent IC=+0.1164, 1st-half IC=+0.0838, 2nd-half IC=+0.1260, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.43)
- Regime ICs: Q1_low_vol=-0.023, Q2=+0.035, Q3_mid=+0.086, Q4=+0.200, Q5_high_vol=+0.183

**`star50_limit_proximity_early`** (Lock IC=+0.0715, Sharpe=+0.2356)
- Admission: Train IC=+0.1622, Deflated=+0.1616, IR=0.45, Mono=0.69, p=0.0014, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.059 | 2017: -0.103 | 2018: +0.108 | 2019: +0.076 | 2020: +0.041 | 2021: +0.102 | 2022: +0.097 | 2023: +0.030 | 2024: +0.001 | 2025: +0.045 | 2026: +0.140
- Yearly Tail ICs:   2015: +0.158 | 2016: +0.132 | 2017: -0.017 | 2018: +0.273 | 2019: +0.161 | 2020: +0.180 | 2021: +0.093 | 2022: +0.181 | 2023: -0.240 | 2024: +0.224 | 2025: -0.012 | 2026: +0.188
- IC CV=1.14, Neg years (linear/tail)=1/1 of 8, Half ratio=0.97, Recency ratio=0.58
- Early IC=+0.1248, Recent IC=+0.0719, 1st-half IC=+0.0850, 2nd-half IC=+0.0826, Neg regimes=2/5
- Regime ICs: Q1_low_vol=-0.039, Q2=-0.007, Q3_mid=+0.028, Q4=+0.161, Q5_high_vol=+0.171

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0578, Sharpe=+0.1933)
- Admission: Train IC=+0.2228, Deflated=+0.2223, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.053 | 2017: -0.045 | 2018: +0.210 | 2019: +0.132 | 2020: +0.058 | 2021: +0.157 | 2022: +0.044 | 2023: +0.127 | 2024: +0.034 | 2025: +0.085 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.373 | 2016: -0.052 | 2017: -0.028 | 2018: +0.274 | 2019: +0.308 | 2020: +0.215 | 2021: +0.435 | 2022: +0.312 | 2023: +0.092 | 2024: +0.263 | 2025: +0.065 | 2026: +0.102
- IC CV=0.79, Neg years (linear/tail)=1/2 of 8, Half ratio=1.30, Recency ratio=0.66
- Early IC=+0.1627, Recent IC=+0.1075, 1st-half IC=+0.1042, 2nd-half IC=+0.1357, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=-0.003, Q2=+0.039, Q3_mid=+0.128, Q4=+0.184, Q5_high_vol=+0.218

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration`** (Lock IC=+0.0347, Sharpe=+0.1883)
- Admission: Train IC=+0.1728, Deflated=+0.1729, IR=0.68, Mono=0.74, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.090 | 2017: -0.037 | 2018: +0.144 | 2019: +0.060 | 2020: +0.052 | 2021: +0.169 | 2022: -0.000 | 2023: +0.152 | 2024: +0.068 | 2025: +0.052 | 2026: -0.193
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.240 | 2017: +0.015 | 2018: +0.324 | 2019: +0.046 | 2020: +0.165 | 2021: +0.411 | 2022: +0.129 | 2023: +0.219 | 2024: +0.217 | 2025: -0.044 | 2026: -0.400
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=1.65, Recency ratio=1.95
- Early IC=+0.0566, Recent IC=+0.1105, 1st-half IC=+0.0626, 2nd-half IC=+0.1034, Neg regimes=1/5
- Weak component: `volume_concentration` (CV=1.32)
- Regime ICs: Q1_low_vol=-0.010, Q2=+0.052, Q3_mid=+0.081, Q4=+0.137, Q5_high_vol=+0.122

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0482, Sharpe=+0.1668)
- Admission: Train IC=+0.2758, Deflated=+0.2757, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.087 | 2017: -0.045 | 2018: +0.213 | 2019: +0.120 | 2020: +0.070 | 2021: +0.174 | 2022: +0.012 | 2023: +0.139 | 2024: +0.067 | 2025: +0.035 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.147 | 2017: +0.079 | 2018: +0.383 | 2019: +0.372 | 2020: +0.176 | 2021: +0.517 | 2022: +0.241 | 2023: +0.124 | 2024: +0.335 | 2025: -0.058 | 2026: -0.016
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.24, Recency ratio=0.85
- Early IC=+0.1440, Recent IC=+0.1219, 1st-half IC=+0.1120, 2nd-half IC=+0.1393, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.16)
- Regime ICs: Q1_low_vol=-0.006, Q2=+0.032, Q3_mid=+0.110, Q4=+0.209, Q5_high_vol=+0.216

**`combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0430, Sharpe=+0.1463)
- Admission: Train IC=+0.2160, Deflated=+0.2161, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.030 | 2017: +0.039 | 2018: +0.150 | 2019: +0.044 | 2020: +0.011 | 2021: +0.194 | 2022: +0.045 | 2023: +0.198 | 2024: +0.039 | 2025: +0.105 | 2026: -0.251
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.097 | 2017: +0.159 | 2018: +0.431 | 2019: +0.203 | 2020: +0.215 | 2021: +0.326 | 2022: +0.241 | 2023: +0.237 | 2024: +0.107 | 2025: +0.226 | 2026: -0.384
- IC CV=0.83, Neg years (linear/tail)=0/0 of 8, Half ratio=1.62, Recency ratio=1.66
- Early IC=+0.0619, Recent IC=+0.1027, 1st-half IC=+0.0575, 2nd-half IC=+0.0931, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.26)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.044, Q3_mid=+0.084, Q4=+0.068, Q5_high_vol=+0.126

**`combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0598, Sharpe=+0.1129)
- Admission: Train IC=+0.2309, Deflated=+0.2304, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.059 | 2017: -0.074 | 2018: +0.196 | 2019: +0.116 | 2020: +0.050 | 2021: +0.160 | 2022: +0.020 | 2023: +0.128 | 2024: +0.052 | 2025: +0.061 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.150 | 2017: -0.050 | 2018: +0.354 | 2019: +0.400 | 2020: +0.129 | 2021: +0.351 | 2022: +0.212 | 2023: +0.120 | 2024: +0.251 | 2025: -0.062 | 2026: +0.155
- IC CV=0.91, Neg years (linear/tail)=1/1 of 8, Half ratio=1.36, Recency ratio=0.71
- Early IC=+0.1476, Recent IC=+0.1054, 1st-half IC=+0.0946, 2nd-half IC=+0.1282, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.028, Q2=+0.018, Q3_mid=+0.096, Q4=+0.206, Q5_high_vol=+0.213

### 500ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0729, Sharpe=+1.2832)
- Admission: Train IC=+0.2539, Deflated=+0.2534, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.150 | 2016: +0.066 | 2017: +0.199 | 2018: +0.083 | 2019: +0.008 | 2020: +0.124 | 2021: +0.024 | 2022: -0.025 | 2023: +0.093 | 2024: +0.066 | 2025: +0.132 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.268 | 2016: +0.173 | 2017: +0.269 | 2018: +0.338 | 2019: +0.035 | 2020: +0.326 | 2021: +0.035 | 2022: +0.089 | 2023: +0.004 | 2024: +0.378 | 2025: +0.264 | 2026: +0.182
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.40
- Early IC=+0.1868, Recent IC=+0.0740, 1st-half IC=+0.1668, 2nd-half IC=+0.0686, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.017, Q3_mid=+0.135, Q4=+0.195, Q5_high_vol=+0.089

**`combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early`** (Lock IC=+0.1078, Sharpe=+1.2593)
- Admission: Train IC=+0.3066, Deflated=+0.3054, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.112 | 2017: +0.201 | 2018: +0.104 | 2019: +0.132 | 2020: +0.143 | 2021: +0.152 | 2022: +0.075 | 2023: +0.104 | 2024: +0.153 | 2025: +0.101 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.185 | 2017: +0.271 | 2018: +0.337 | 2019: +0.308 | 2020: +0.309 | 2021: +0.205 | 2022: +0.319 | 2023: +0.230 | 2024: +0.362 | 2025: +0.011 | 2026: +0.085
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.69
- Early IC=+0.2152, Recent IC=+0.1477, 1st-half IC=+0.1962, 2nd-half IC=+0.1309, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.026, Q3_mid=+0.189, Q4=+0.214, Q5_high_vol=+0.180

**`combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1033, Sharpe=+1.1649)
- Admission: Train IC=+0.2926, Deflated=+0.2912, IR=0.79, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.059 | 2017: +0.210 | 2018: +0.125 | 2019: +0.137 | 2020: +0.119 | 2021: +0.109 | 2022: +0.061 | 2023: +0.076 | 2024: +0.140 | 2025: +0.130 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.066 | 2017: +0.209 | 2018: +0.300 | 2019: +0.312 | 2020: +0.282 | 2021: +0.130 | 2022: +0.210 | 2023: +0.278 | 2024: +0.383 | 2025: +0.142 | 2026: +0.159
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.49
- Early IC=+0.2325, Recent IC=+0.1143, 1st-half IC=+0.1802, 2nd-half IC=+0.1223, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.211, Q2=-0.017, Q3_mid=+0.131, Q4=+0.213, Q5_high_vol=+0.200

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.0958, Sharpe=+1.1231)
- Admission: Train IC=+0.2714, Deflated=+0.2709, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.299 | 2016: +0.023 | 2017: +0.203 | 2018: +0.146 | 2019: +0.185 | 2020: +0.147 | 2021: +0.091 | 2022: +0.054 | 2023: +0.066 | 2024: +0.100 | 2025: +0.036 | 2026: +0.237
- Yearly Tail ICs:   2015: +0.323 | 2016: -0.040 | 2017: +0.313 | 2018: +0.263 | 2019: +0.352 | 2020: +0.217 | 2021: +0.279 | 2022: -0.072 | 2023: +0.245 | 2024: +0.207 | 2025: -0.012 | 2026: +0.316
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.53
- Early IC=+0.2223, Recent IC=+0.1188, 1st-half IC=+0.1713, 2nd-half IC=+0.1424, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.059, Q3_mid=+0.160, Q4=+0.123, Q5_high_vol=+0.276

**`combo_sig_product__max_up_ret__shaved_bar_trend_conviction`** (Lock IC=+0.1053, Sharpe=+1.1165)
- Admission: Train IC=+0.2403, Deflated=+0.2396, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.171 | 2017: +0.092 | 2018: +0.125 | 2019: +0.040 | 2020: +0.124 | 2021: +0.037 | 2022: +0.054 | 2023: +0.089 | 2024: +0.149 | 2025: +0.181 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.443 | 2016: +0.183 | 2017: +0.278 | 2018: +0.171 | 2019: -0.058 | 2020: +0.193 | 2021: +0.083 | 2022: +0.024 | 2023: -0.020 | 2024: +0.225 | 2025: +0.261 | 2026: -0.226
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=0.44, Recency ratio=0.38
- Early IC=+0.2133, Recent IC=+0.0806, 1st-half IC=+0.1934, 2nd-half IC=+0.0850, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.005, Q3_mid=+0.145, Q4=+0.158, Q5_high_vol=+0.226

**`combo_rel_diff__star50_limit_proximity_early__late_bar_momentum`** (Lock IC=+0.0865, Sharpe=+1.0730)
- Admission: Train IC=+0.2742, Deflated=+0.2739, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.319 | 2016: +0.026 | 2017: +0.192 | 2018: +0.154 | 2019: +0.157 | 2020: +0.110 | 2021: +0.092 | 2022: +0.028 | 2023: +0.056 | 2024: +0.076 | 2025: +0.024 | 2026: +0.262
- Yearly Tail ICs:   2015: +0.394 | 2016: -0.037 | 2017: +0.379 | 2018: +0.267 | 2019: +0.356 | 2020: +0.149 | 2021: +0.242 | 2022: -0.055 | 2023: +0.255 | 2024: +0.086 | 2025: -0.079 | 2026: +0.354
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=0.73, Recency ratio=0.45
- Early IC=+0.2247, Recent IC=+0.1013, 1st-half IC=+0.1767, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.061, Q3_mid=+0.157, Q4=+0.129, Q5_high_vol=+0.260

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`** (Lock IC=+0.1095, Sharpe=+1.0664)
- Admission: Train IC=+0.2987, Deflated=+0.2975, IR=0.99, Mono=0.82, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.096 | 2017: +0.227 | 2018: +0.136 | 2019: +0.123 | 2020: +0.150 | 2021: +0.116 | 2022: +0.070 | 2023: +0.089 | 2024: +0.121 | 2025: +0.148 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.245 | 2017: +0.311 | 2018: +0.405 | 2019: +0.129 | 2020: +0.339 | 2021: +0.114 | 2022: +0.084 | 2023: +0.195 | 2024: +0.361 | 2025: +0.093 | 2026: +0.280
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.62
- Early IC=+0.2165, Recent IC=+0.1336, 1st-half IC=+0.2007, 2nd-half IC=+0.1338, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.051, Q3_mid=+0.170, Q4=+0.218, Q5_high_vol=+0.169

**`combo_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1157, Sharpe=+0.9778)
- Admission: Train IC=+0.2814, Deflated=+0.2801, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.066 | 2017: +0.244 | 2018: +0.192 | 2019: +0.135 | 2020: +0.151 | 2021: +0.084 | 2022: +0.097 | 2023: +0.129 | 2024: +0.129 | 2025: +0.153 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.316 | 2016: -0.039 | 2017: +0.242 | 2018: +0.233 | 2019: +0.244 | 2020: +0.224 | 2021: +0.124 | 2022: +0.236 | 2023: +0.291 | 2024: +0.223 | 2025: +0.156 | 2026: -0.095
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.68, Recency ratio=0.47
- Early IC=+0.2515, Recent IC=+0.1174, 1st-half IC=+0.2132, 2nd-half IC=+0.1442, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.225, Q2=+0.060, Q3_mid=+0.179, Q4=+0.187, Q5_high_vol=+0.238

**`combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.1071, Sharpe=+0.9757)
- Admission: Train IC=+0.2765, Deflated=+0.2750, IR=0.79, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.065 | 2017: +0.225 | 2018: +0.088 | 2019: +0.108 | 2020: +0.121 | 2021: +0.097 | 2022: +0.042 | 2023: +0.099 | 2024: +0.139 | 2025: +0.131 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.168 | 2017: +0.275 | 2018: +0.269 | 2019: +0.303 | 2020: +0.277 | 2021: +0.193 | 2022: +0.116 | 2023: +0.216 | 2024: +0.236 | 2025: +0.066 | 2026: +0.124
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.57
- Early IC=+0.1949, Recent IC=+0.1109, 1st-half IC=+0.1705, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.028, Q3_mid=+0.108, Q4=+0.213, Q5_high_vol=+0.151

**`combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0979, Sharpe=+0.9660)
- Admission: Train IC=+0.2877, Deflated=+0.2858, IR=0.73, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.072 | 2017: +0.208 | 2018: +0.174 | 2019: +0.131 | 2020: +0.108 | 2021: +0.115 | 2022: +0.044 | 2023: +0.101 | 2024: +0.123 | 2025: +0.134 | 2026: +0.068
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.083 | 2017: +0.291 | 2018: +0.363 | 2019: +0.279 | 2020: +0.187 | 2021: +0.122 | 2022: +0.184 | 2023: +0.268 | 2024: +0.338 | 2025: +0.255 | 2026: +0.257
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.50
- Early IC=+0.2221, Recent IC=+0.1111, 1st-half IC=+0.1854, 2nd-half IC=+0.1304, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.227, Q2=+0.021, Q3_mid=+0.113, Q4=+0.249, Q5_high_vol=+0.177

**`combo_min__opening_auction_imbalance__first_bar_return`** (Lock IC=+0.0907, Sharpe=+0.9586)
- Admission: Train IC=+0.2548, Deflated=+0.2539, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.069 | 2017: +0.181 | 2018: +0.175 | 2019: +0.119 | 2020: +0.098 | 2021: +0.085 | 2022: +0.090 | 2023: +0.081 | 2024: +0.138 | 2025: +0.124 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.340 | 2016: +0.014 | 2017: +0.255 | 2018: +0.375 | 2019: +0.135 | 2020: +0.123 | 2021: +0.277 | 2022: +0.228 | 2023: +0.321 | 2024: +0.378 | 2025: +0.128 | 2026: +0.041
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.48
- Early IC=+0.1901, Recent IC=+0.0911, 1st-half IC=+0.1529, 2nd-half IC=+0.1199, Neg regimes=1/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.027, Q3_mid=+0.158, Q4=+0.172, Q5_high_vol=+0.169

**`combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1186, Sharpe=+0.9560)
- Admission: Train IC=+0.2433, Deflated=+0.2422, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.057 | 2017: +0.251 | 2018: +0.164 | 2019: +0.141 | 2020: +0.165 | 2021: +0.096 | 2022: +0.089 | 2023: +0.127 | 2024: +0.139 | 2025: +0.137 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.438 | 2016: +0.141 | 2017: +0.180 | 2018: +0.102 | 2019: +0.335 | 2020: +0.115 | 2021: +0.163 | 2022: +0.413 | 2023: +0.091 | 2024: +0.279 | 2025: +0.207 | 2026: +0.053
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.50
- Early IC=+0.2616, Recent IC=+0.1306, 1st-half IC=+0.2153, 2nd-half IC=+0.1453, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.076, Q3_mid=+0.199, Q4=+0.197, Q5_high_vol=+0.244

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1179, Sharpe=+0.9552)
- Admission: Train IC=+0.2426, Deflated=+0.2414, IR=0.76, Mono=0.79, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.066 | 2017: +0.250 | 2018: +0.161 | 2019: +0.142 | 2020: +0.166 | 2021: +0.097 | 2022: +0.094 | 2023: +0.123 | 2024: +0.130 | 2025: +0.137 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.440 | 2016: +0.147 | 2017: +0.181 | 2018: +0.113 | 2019: +0.333 | 2020: +0.115 | 2021: +0.177 | 2022: +0.400 | 2023: +0.094 | 2024: +0.279 | 2025: +0.200 | 2026: +0.015
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.51
- Early IC=+0.2565, Recent IC=+0.1315, 1st-half IC=+0.2144, 2nd-half IC=+0.1447, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.086, Q3_mid=+0.197, Q4=+0.195, Q5_high_vol=+0.242

**`combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0856, Sharpe=+0.9522)
- Admission: Train IC=+0.2613, Deflated=+0.2603, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.038 | 2017: +0.215 | 2018: +0.063 | 2019: +0.037 | 2020: +0.130 | 2021: +0.019 | 2022: -0.007 | 2023: +0.079 | 2024: +0.101 | 2025: +0.133 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.152 | 2017: +0.271 | 2018: +0.309 | 2019: +0.054 | 2020: +0.319 | 2021: +0.096 | 2022: +0.098 | 2023: -0.072 | 2024: +0.377 | 2025: +0.158 | 2026: +0.300
- IC CV=0.69, Neg years (linear/tail)=0/0 of 8, Half ratio=0.44, Recency ratio=0.37
- Early IC=+0.1958, Recent IC=+0.0719, 1st-half IC=+0.1584, 2nd-half IC=+0.0692, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.008, Q3_mid=+0.111, Q4=+0.174, Q5_high_vol=+0.116

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1009, Sharpe=+0.9225)
- Admission: Train IC=+0.3546, Deflated=+0.3533, IR=1.20, Mono=0.87, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.121 | 2017: +0.225 | 2018: +0.187 | 2019: +0.172 | 2020: +0.173 | 2021: +0.145 | 2022: +0.014 | 2023: +0.108 | 2024: +0.165 | 2025: +0.090 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.406 | 2016: +0.227 | 2017: +0.344 | 2018: +0.526 | 2019: +0.335 | 2020: +0.237 | 2021: +0.292 | 2022: +0.172 | 2023: +0.123 | 2024: +0.312 | 2025: -0.007 | 2026: +0.184
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.62
- Early IC=+0.2553, Recent IC=+0.1586, 1st-half IC=+0.2276, 2nd-half IC=+0.1722, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.096, Q3_mid=+0.199, Q4=+0.229, Q5_high_vol=+0.251

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1002, Sharpe=+0.9162)
- Admission: Train IC=+0.3110, Deflated=+0.3094, IR=0.99, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.089 | 2017: +0.220 | 2018: +0.201 | 2019: +0.124 | 2020: +0.136 | 2021: +0.156 | 2022: +0.043 | 2023: +0.113 | 2024: +0.145 | 2025: +0.123 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.336 | 2016: +0.188 | 2017: +0.292 | 2018: +0.445 | 2019: +0.301 | 2020: +0.246 | 2021: +0.265 | 2022: +0.229 | 2023: +0.154 | 2024: +0.286 | 2025: +0.068 | 2026: +0.233
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.68
- Early IC=+0.2135, Recent IC=+0.1461, 1st-half IC=+0.1896, 2nd-half IC=+0.1536, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.070, Q3_mid=+0.165, Q4=+0.235, Q5_high_vol=+0.177

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1015, Sharpe=+0.9058)
- Admission: Train IC=+0.3099, Deflated=+0.3086, IR=0.88, Mono=0.78, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.116 | 2017: +0.223 | 2018: +0.204 | 2019: +0.159 | 2020: +0.162 | 2021: +0.125 | 2022: +0.044 | 2023: +0.097 | 2024: +0.105 | 2025: +0.133 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.195 | 2017: +0.227 | 2018: +0.402 | 2019: +0.245 | 2020: +0.333 | 2021: +0.177 | 2022: +0.037 | 2023: +0.163 | 2024: +0.227 | 2025: +0.257 | 2026: +0.246
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.53
- Early IC=+0.2713, Recent IC=+0.1438, 1st-half IC=+0.2342, 2nd-half IC=+0.1613, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.042, Q3_mid=+0.174, Q4=+0.249, Q5_high_vol=+0.252

**`combo_tri_mean__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.0947, Sharpe=+0.9043)
- Admission: Train IC=+0.2874, Deflated=+0.2871, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.088 | 2017: +0.179 | 2018: +0.147 | 2019: +0.095 | 2020: +0.130 | 2021: +0.063 | 2022: +0.098 | 2023: +0.070 | 2024: +0.101 | 2025: +0.125 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.129 | 2017: +0.266 | 2018: +0.271 | 2019: +0.267 | 2020: +0.224 | 2021: +0.153 | 2022: +0.310 | 2023: +0.272 | 2024: +0.190 | 2025: +0.114 | 2026: -0.143
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.46
- Early IC=+0.2126, Recent IC=+0.0968, 1st-half IC=+0.1827, 2nd-half IC=+0.1133, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.017, Q3_mid=+0.170, Q4=+0.204, Q5_high_vol=+0.154

**`combo_mean__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0855, Sharpe=+0.8907)
- Admission: Train IC=+0.2837, Deflated=+0.2826, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.099 | 2017: +0.225 | 2018: +0.233 | 2019: +0.144 | 2020: +0.147 | 2021: +0.137 | 2022: +0.070 | 2023: +0.092 | 2024: +0.137 | 2025: +0.110 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.582 | 2016: +0.004 | 2017: +0.196 | 2018: +0.178 | 2019: +0.350 | 2020: +0.085 | 2021: +0.440 | 2022: +0.118 | 2023: +0.085 | 2024: +0.224 | 2025: +0.150 | 2026: +0.004
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.60
- Early IC=+0.2352, Recent IC=+0.1422, 1st-half IC=+0.1963, 2nd-half IC=+0.1629, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.036, Q3_mid=+0.192, Q4=+0.200, Q5_high_vol=+0.267

**`combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction`** (Lock IC=+0.0978, Sharpe=+0.8875)
- Admission: Train IC=+0.2367, Deflated=+0.2355, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.067 | 2017: +0.228 | 2018: +0.144 | 2019: +0.104 | 2020: +0.174 | 2021: +0.120 | 2022: +0.085 | 2023: +0.096 | 2024: +0.137 | 2025: +0.130 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.144 | 2017: +0.314 | 2018: +0.195 | 2019: +0.095 | 2020: +0.185 | 2021: +0.092 | 2022: +0.150 | 2023: +0.028 | 2024: +0.171 | 2025: +0.234 | 2026: -0.249
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.82
- Early IC=+0.1799, Recent IC=+0.1472, 1st-half IC=+0.1607, 2nd-half IC=+0.1345, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.047, Q3_mid=+0.198, Q4=+0.188, Q5_high_vol=+0.165

**`combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`** (Lock IC=+0.0883, Sharpe=+0.8848)
- Admission: Train IC=+0.2885, Deflated=+0.2880, IR=0.79, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.305 | 2016: +0.083 | 2017: +0.171 | 2018: +0.152 | 2019: +0.169 | 2020: +0.108 | 2021: +0.086 | 2022: +0.040 | 2023: +0.045 | 2024: +0.093 | 2025: -0.002 | 2026: +0.279
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.247 | 2017: +0.418 | 2018: +0.311 | 2019: +0.295 | 2020: +0.142 | 2021: +0.274 | 2022: -0.097 | 2023: +0.184 | 2024: +0.168 | 2025: -0.145 | 2026: +0.395
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.46
- Early IC=+0.2120, Recent IC=+0.0973, 1st-half IC=+0.1825, 2nd-half IC=+0.1294, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.075, Q3_mid=+0.152, Q4=+0.142, Q5_high_vol=+0.250

**`combo_diff__star50_limit_proximity_early__late_bar_momentum`** (Lock IC=+0.0872, Sharpe=+0.8848)
- Admission: Train IC=+0.2421, Deflated=+0.2417, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.072 | 2017: +0.170 | 2018: +0.151 | 2019: +0.171 | 2020: +0.110 | 2021: +0.085 | 2022: +0.041 | 2023: +0.045 | 2024: +0.089 | 2025: -0.002 | 2026: +0.277
- Yearly Tail ICs:   2015: +0.195 | 2016: -0.031 | 2017: +0.374 | 2018: +0.269 | 2019: +0.314 | 2020: +0.164 | 2021: +0.232 | 2022: -0.075 | 2023: +0.178 | 2024: +0.077 | 2025: -0.153 | 2026: +0.330
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.72, Recency ratio=0.47
- Early IC=+0.2088, Recent IC=+0.0975, 1st-half IC=+0.1789, 2nd-half IC=+0.1296, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.074, Q3_mid=+0.152, Q4=+0.139, Q5_high_vol=+0.244

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1236, Sharpe=+0.8806)
- Admission: Train IC=+0.2730, Deflated=+0.2723, IR=0.85, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.307 | 2016: +0.119 | 2017: +0.254 | 2018: +0.165 | 2019: +0.128 | 2020: +0.155 | 2021: +0.087 | 2022: +0.109 | 2023: +0.128 | 2024: +0.128 | 2025: +0.143 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.298 | 2016: +0.348 | 2017: +0.361 | 2018: +0.191 | 2019: +0.174 | 2020: +0.136 | 2021: +0.138 | 2022: +0.182 | 2023: +0.155 | 2024: +0.234 | 2025: -0.059 | 2026: -0.266
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.45
- Early IC=+0.2676, Recent IC=+0.1211, 1st-half IC=+0.2426, 2nd-half IC=+0.1358, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.230, Q2=+0.094, Q3_mid=+0.206, Q4=+0.187, Q5_high_vol=+0.246

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0804, Sharpe=+0.8800)
- Admission: Train IC=+0.2472, Deflated=+0.2463, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.070 | 2017: +0.271 | 2018: +0.191 | 2019: +0.147 | 2020: +0.174 | 2021: +0.099 | 2022: +0.054 | 2023: +0.065 | 2024: +0.158 | 2025: +0.105 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.084 | 2017: +0.230 | 2018: +0.162 | 2019: +0.360 | 2020: +0.069 | 2021: +0.297 | 2022: +0.084 | 2023: +0.184 | 2024: +0.402 | 2025: +0.177 | 2026: +0.052
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.62
- Early IC=+0.2222, Recent IC=+0.1379, 1st-half IC=+0.1874, 2nd-half IC=+0.1464, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.228, Q2=+0.015, Q3_mid=+0.180, Q4=+0.193, Q5_high_vol=+0.248

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1085, Sharpe=+0.8733)
- Admission: Train IC=+0.2531, Deflated=+0.2526, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.147 | 2017: +0.065 | 2018: +0.154 | 2019: +0.088 | 2020: +0.134 | 2021: +0.117 | 2022: +0.119 | 2023: +0.134 | 2024: +0.136 | 2025: +0.135 | 2026: +0.026
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.053 | 2017: +0.259 | 2018: +0.219 | 2019: +0.368 | 2020: +0.223 | 2021: +0.272 | 2022: +0.213 | 2023: +0.293 | 2024: +0.228 | 2025: +0.065 | 2026: -0.010
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.71
- Early IC=+0.1756, Recent IC=+0.1255, 1st-half IC=+0.1648, 2nd-half IC=+0.1242, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.046, Q3_mid=+0.141, Q4=+0.171, Q5_high_vol=+0.224

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0803, Sharpe=+0.8682)
- Admission: Train IC=+0.3131, Deflated=+0.3126, IR=0.98, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.106 | 2017: +0.137 | 2018: +0.284 | 2019: +0.178 | 2020: +0.171 | 2021: +0.172 | 2022: +0.054 | 2023: +0.093 | 2024: +0.153 | 2025: +0.058 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.415 | 2016: +0.123 | 2017: +0.312 | 2018: +0.611 | 2019: +0.254 | 2020: +0.108 | 2021: +0.294 | 2022: +0.200 | 2023: +0.115 | 2024: +0.192 | 2025: +0.048 | 2026: +0.080
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.70
- Early IC=+0.2436, Recent IC=+0.1714, 1st-half IC=+0.2063, 2nd-half IC=+0.1927, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.105, Q3_mid=+0.220, Q4=+0.197, Q5_high_vol=+0.294

**`combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range`** (Lock IC=+0.1133, Sharpe=+0.8617)
- Admission: Train IC=+0.2574, Deflated=+0.2568, IR=0.85, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.124 | 2017: +0.207 | 2018: +0.144 | 2019: +0.105 | 2020: +0.147 | 2021: +0.068 | 2022: +0.100 | 2023: +0.073 | 2024: +0.110 | 2025: +0.113 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.194 | 2016: +0.230 | 2017: +0.304 | 2018: +0.284 | 2019: +0.237 | 2020: +0.199 | 2021: +0.153 | 2022: +0.155 | 2023: +0.010 | 2024: +0.262 | 2025: +0.086 | 2026: +0.057
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.45
- Early IC=+0.2371, Recent IC=+0.1077, 1st-half IC=+0.2190, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.053, Q3_mid=+0.164, Q4=+0.200, Q5_high_vol=+0.204

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1074, Sharpe=+0.8596)
- Admission: Train IC=+0.2845, Deflated=+0.2830, IR=0.81, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.096 | 2017: +0.219 | 2018: +0.144 | 2019: +0.099 | 2020: +0.112 | 2021: +0.120 | 2022: +0.079 | 2023: +0.113 | 2024: +0.122 | 2025: +0.141 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.218 | 2017: +0.309 | 2018: +0.381 | 2019: +0.189 | 2020: +0.286 | 2021: +0.178 | 2022: +0.241 | 2023: +0.201 | 2024: +0.319 | 2025: +0.203 | 2026: +0.158
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.58
- Early IC=+0.1994, Recent IC=+0.1161, 1st-half IC=+0.1869, 2nd-half IC=+0.1203, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.052, Q3_mid=+0.125, Q4=+0.241, Q5_high_vol=+0.147

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1054, Sharpe=+0.8412)
- Admission: Train IC=+0.2836, Deflated=+0.2835, IR=0.86, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.124 | 2017: +0.150 | 2018: +0.155 | 2019: +0.096 | 2020: +0.137 | 2021: +0.059 | 2022: +0.124 | 2023: +0.072 | 2024: +0.091 | 2025: +0.111 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.261 | 2017: +0.235 | 2018: +0.330 | 2019: +0.293 | 2020: +0.168 | 2021: +0.118 | 2022: +0.241 | 2023: +0.170 | 2024: +0.209 | 2025: +0.114 | 2026: +0.054
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.45
- Early IC=+0.2167, Recent IC=+0.0980, 1st-half IC=+0.1961, 2nd-half IC=+0.1206, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.032, Q3_mid=+0.180, Q4=+0.199, Q5_high_vol=+0.171

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0816, Sharpe=+0.8253)
- Admission: Train IC=+0.2908, Deflated=+0.2902, IR=1.00, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.106 | 2017: +0.136 | 2018: +0.284 | 2019: +0.177 | 2020: +0.172 | 2021: +0.172 | 2022: +0.053 | 2023: +0.100 | 2024: +0.158 | 2025: +0.056 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.191 | 2017: +0.296 | 2018: +0.604 | 2019: +0.191 | 2020: +0.123 | 2021: +0.291 | 2022: +0.173 | 2023: +0.256 | 2024: +0.188 | 2025: -0.016 | 2026: +0.077
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.71
- Early IC=+0.2423, Recent IC=+0.1718, 1st-half IC=+0.2070, 2nd-half IC=+0.1920, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.105, Q3_mid=+0.218, Q4=+0.200, Q5_high_vol=+0.293

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0847, Sharpe=+0.8135)
- Admission: Train IC=+0.2604, Deflated=+0.2597, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.132 | 2017: +0.111 | 2018: +0.195 | 2019: +0.080 | 2020: +0.103 | 2021: +0.126 | 2022: +0.078 | 2023: +0.006 | 2024: +0.139 | 2025: +0.141 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.471 | 2016: +0.198 | 2017: +0.217 | 2018: +0.387 | 2019: -0.048 | 2020: +0.109 | 2021: +0.319 | 2022: +0.088 | 2023: +0.078 | 2024: +0.170 | 2025: +0.259 | 2026: +0.388
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.74, Recency ratio=0.56
- Early IC=+0.2042, Recent IC=+0.1143, 1st-half IC=+0.1699, 2nd-half IC=+0.1253, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.025, Q3_mid=+0.148, Q4=+0.124, Q5_high_vol=+0.256

**`combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction`** (Lock IC=+0.0745, Sharpe=+0.8110)
- Admission: Train IC=+0.2670, Deflated=+0.2665, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.039 | 2017: +0.213 | 2018: +0.158 | 2019: +0.072 | 2020: +0.159 | 2021: +0.083 | 2022: +0.026 | 2023: +0.098 | 2024: +0.118 | 2025: +0.120 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.321 | 2016: +0.191 | 2017: +0.363 | 2018: +0.209 | 2019: +0.077 | 2020: +0.169 | 2021: +0.234 | 2022: +0.233 | 2023: +0.004 | 2024: +0.212 | 2025: +0.197 | 2026: -0.151
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.55
- Early IC=+0.2186, Recent IC=+0.1208, 1st-half IC=+0.1794, 2nd-half IC=+0.1216, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.018, Q3_mid=+0.212, Q4=+0.185, Q5_high_vol=+0.170

**`combo_rel_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1105, Sharpe=+0.8062)
- Admission: Train IC=+0.2817, Deflated=+0.2806, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.090 | 2017: +0.220 | 2018: +0.176 | 2019: +0.151 | 2020: +0.141 | 2021: +0.097 | 2022: +0.083 | 2023: +0.120 | 2024: +0.120 | 2025: +0.156 | 2026: +0.031
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.012 | 2017: +0.237 | 2018: +0.227 | 2019: +0.244 | 2020: +0.215 | 2021: +0.124 | 2022: +0.232 | 2023: +0.239 | 2024: +0.194 | 2025: +0.107 | 2026: -0.078
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.47
- Early IC=+0.2558, Recent IC=+0.1192, 1st-half IC=+0.2150, 2nd-half IC=+0.1436, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.086, Q3_mid=+0.177, Q4=+0.190, Q5_high_vol=+0.241

**`combo_mean__max_up_ret__close_vs_open_range`** (Lock IC=+0.0941, Sharpe=+0.8047)
- Admission: Train IC=+0.2429, Deflated=+0.2418, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.096 | 2017: +0.213 | 2018: +0.175 | 2019: +0.085 | 2020: +0.132 | 2021: +0.104 | 2022: +0.109 | 2023: +0.104 | 2024: +0.142 | 2025: +0.115 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.291 | 2017: +0.262 | 2018: +0.336 | 2019: +0.143 | 2020: +0.193 | 2021: +0.273 | 2022: +0.061 | 2023: +0.210 | 2024: +0.251 | 2025: -0.062 | 2026: -0.109
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.59
- Early IC=+0.2015, Recent IC=+0.1182, 1st-half IC=+0.1907, 2nd-half IC=+0.1227, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.029, Q3_mid=+0.192, Q4=+0.177, Q5_high_vol=+0.195

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.1005, Sharpe=+0.7895)
- Admission: Train IC=+0.2806, Deflated=+0.2797, IR=0.78, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.123 | 2017: +0.223 | 2018: +0.218 | 2019: +0.126 | 2020: +0.155 | 2021: +0.105 | 2022: +0.093 | 2023: +0.076 | 2024: +0.114 | 2025: +0.142 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.260 | 2016: +0.075 | 2017: +0.249 | 2018: +0.358 | 2019: +0.253 | 2020: +0.251 | 2021: +0.221 | 2022: +0.245 | 2023: +0.231 | 2024: +0.177 | 2025: +0.077 | 2026: -0.038
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.52
- Early IC=+0.2498, Recent IC=+0.1301, 1st-half IC=+0.2261, 2nd-half IC=+0.1537, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.237, Q2=+0.042, Q3_mid=+0.186, Q4=+0.212, Q5_high_vol=+0.239

**`combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0964, Sharpe=+0.7790)
- Admission: Train IC=+0.2437, Deflated=+0.2425, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.077 | 2017: +0.191 | 2018: +0.176 | 2019: +0.127 | 2020: +0.101 | 2021: +0.106 | 2022: +0.096 | 2023: +0.108 | 2024: +0.136 | 2025: +0.140 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.026 | 2017: +0.296 | 2018: +0.354 | 2019: +0.195 | 2020: +0.155 | 2021: +0.234 | 2022: +0.229 | 2023: +0.276 | 2024: +0.218 | 2025: +0.235 | 2026: -0.060
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.58
- Early IC=+0.1792, Recent IC=+0.1039, 1st-half IC=+0.1662, 2nd-half IC=+0.1246, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.232, Q2=+0.015, Q3_mid=+0.164, Q4=+0.173, Q5_high_vol=+0.154

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0961, Sharpe=+0.7731)
- Admission: Train IC=+0.3455, Deflated=+0.3443, IR=0.94, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.101 | 2017: +0.211 | 2018: +0.216 | 2019: +0.158 | 2020: +0.123 | 2021: +0.133 | 2022: +0.049 | 2023: +0.090 | 2024: +0.107 | 2025: +0.117 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.290 | 2016: +0.250 | 2017: +0.304 | 2018: +0.467 | 2019: +0.376 | 2020: +0.314 | 2021: +0.031 | 2022: +0.086 | 2023: +0.142 | 2024: +0.305 | 2025: +0.145 | 2026: +0.286
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.47
- Early IC=+0.2715, Recent IC=+0.1276, 1st-half IC=+0.2291, 2nd-half IC=+0.1544, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.201, Q2=+0.031, Q3_mid=+0.167, Q4=+0.238, Q5_high_vol=+0.256

**`combo_min__trend_bar_close_consistency__star50_limit_proximity_early`** (Lock IC=+0.0945, Sharpe=+0.7722)
- Admission: Train IC=+0.2735, Deflated=+0.2727, IR=0.66, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.049 | 2017: +0.207 | 2018: +0.078 | 2019: +0.061 | 2020: +0.088 | 2021: +0.041 | 2022: +0.046 | 2023: +0.090 | 2024: +0.113 | 2025: +0.118 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.271 | 2016: +0.145 | 2017: +0.348 | 2018: +0.283 | 2019: +0.036 | 2020: +0.284 | 2021: -0.007 | 2022: +0.307 | 2023: -0.086 | 2024: +0.272 | 2025: +0.034 | 2026: +0.078
- IC CV=0.58, Neg years (linear/tail)=0/1 of 8, Half ratio=0.48, Recency ratio=0.36
- Early IC=+0.1804, Recent IC=+0.0646, 1st-half IC=+0.1480, 2nd-half IC=+0.0710, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.009, Q3_mid=+0.098, Q4=+0.188, Q5_high_vol=+0.106

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0796, Sharpe=+0.7701)
- Admission: Train IC=+0.2800, Deflated=+0.2799, IR=0.89, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.110 | 2017: +0.189 | 2018: +0.216 | 2019: +0.121 | 2020: +0.144 | 2021: +0.154 | 2022: +0.058 | 2023: +0.093 | 2024: +0.116 | 2025: +0.011 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.150 | 2017: +0.444 | 2018: +0.359 | 2019: +0.379 | 2020: +0.159 | 2021: +0.222 | 2022: +0.099 | 2023: +0.193 | 2024: +0.045 | 2025: -0.051 | 2026: +0.105
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.71
- Early IC=+0.2098, Recent IC=+0.1488, 1st-half IC=+0.1979, 2nd-half IC=+0.1543, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.060, Q3_mid=+0.207, Q4=+0.150, Q5_high_vol=+0.291

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0929, Sharpe=+0.7697)
- Admission: Train IC=+0.3449, Deflated=+0.3436, IR=0.94, Mono=0.80, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.311 | 2016: +0.079 | 2017: +0.230 | 2018: +0.231 | 2019: +0.175 | 2020: +0.153 | 2021: +0.119 | 2022: +0.035 | 2023: +0.082 | 2024: +0.131 | 2025: +0.123 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.101 | 2017: +0.322 | 2018: +0.507 | 2019: +0.269 | 2020: +0.205 | 2021: +0.191 | 2022: +0.160 | 2023: +0.194 | 2024: +0.273 | 2025: +0.243 | 2026: +0.262
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.48
- Early IC=+0.2863, Recent IC=+0.1364, 1st-half IC=+0.2247, 2nd-half IC=+0.1727, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.084, Q3_mid=+0.182, Q4=+0.241, Q5_high_vol=+0.261

**`combo_rank_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0862, Sharpe=+0.7695)
- Admission: Train IC=+0.2918, Deflated=+0.2906, IR=0.63, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.067 | 2017: +0.194 | 2018: +0.149 | 2019: +0.171 | 2020: +0.116 | 2021: +0.090 | 2022: +0.034 | 2023: +0.064 | 2024: +0.112 | 2025: +0.131 | 2026: +0.093
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.097 | 2017: +0.214 | 2018: +0.387 | 2019: +0.325 | 2020: +0.223 | 2021: +0.118 | 2022: +0.127 | 2023: +0.119 | 2024: +0.320 | 2025: +0.148 | 2026: +0.071
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.40
- Early IC=+0.2566, Recent IC=+0.1035, 1st-half IC=+0.1977, 2nd-half IC=+0.1299, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.024, Q3_mid=+0.117, Q4=+0.192, Q5_high_vol=+0.236

**`combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range`** (Lock IC=+0.1070, Sharpe=+0.7604)
- Admission: Train IC=+0.2759, Deflated=+0.2744, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.102 | 2017: +0.228 | 2018: +0.123 | 2019: +0.077 | 2020: +0.129 | 2021: +0.109 | 2022: +0.058 | 2023: +0.100 | 2024: +0.130 | 2025: +0.149 | 2026: +0.064
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.267 | 2017: +0.326 | 2018: +0.324 | 2019: +0.091 | 2020: +0.225 | 2021: +0.223 | 2022: +0.122 | 2023: +0.007 | 2024: +0.266 | 2025: +0.205 | 2026: +0.221
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.59
- Early IC=+0.2004, Recent IC=+0.1188, 1st-half IC=+0.1932, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.068, Q3_mid=+0.119, Q4=+0.236, Q5_high_vol=+0.145

**`combo_min__star50_limit_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0843, Sharpe=+0.7587)
- Admission: Train IC=+0.2521, Deflated=+0.2509, IR=0.71, Mono=0.73, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.044 | 2017: +0.245 | 2018: +0.050 | 2019: +0.122 | 2020: +0.087 | 2021: +0.071 | 2022: +0.033 | 2023: +0.084 | 2024: +0.110 | 2025: +0.083 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.118 | 2017: +0.305 | 2018: +0.320 | 2019: +0.241 | 2020: +0.182 | 2021: +0.182 | 2022: +0.160 | 2023: +0.120 | 2024: +0.112 | 2025: +0.027 | 2026: -0.173
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.46
- Early IC=+0.1704, Recent IC=+0.0788, 1st-half IC=+0.1530, 2nd-half IC=+0.0894, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.019, Q3_mid=+0.100, Q4=+0.208, Q5_high_vol=+0.131

**`combo_mean__volatility_expansion_trend_vector__shaved_bar_trend_conviction`** (Lock IC=+0.0690, Sharpe=+0.7572)
- Admission: Train IC=+0.2307, Deflated=+0.2304, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.140 | 2016: +0.050 | 2017: +0.178 | 2018: +0.109 | 2019: +0.032 | 2020: +0.105 | 2021: +0.035 | 2022: +0.037 | 2023: +0.092 | 2024: +0.088 | 2025: +0.142 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.073 | 2017: +0.255 | 2018: +0.204 | 2019: +0.148 | 2020: +0.153 | 2021: +0.185 | 2022: +0.196 | 2023: +0.046 | 2024: +0.275 | 2025: +0.144 | 2026: -0.134
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.43
- Early IC=+0.1637, Recent IC=+0.0701, 1st-half IC=+0.1437, 2nd-half IC=+0.0755, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.016, Q3_mid=+0.163, Q4=+0.169, Q5_high_vol=+0.085

**`combo_min__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0843, Sharpe=+0.7451)
- Admission: Train IC=+0.2377, Deflated=+0.2367, IR=0.77, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.151 | 2016: -0.002 | 2017: +0.134 | 2018: +0.155 | 2019: +0.154 | 2020: +0.064 | 2021: +0.161 | 2022: +0.130 | 2023: +0.081 | 2024: +0.121 | 2025: +0.100 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.007 | 2017: +0.329 | 2018: +0.436 | 2019: +0.206 | 2020: +0.015 | 2021: +0.242 | 2022: +0.258 | 2023: +0.147 | 2024: +0.391 | 2025: +0.260 | 2026: -0.067
- IC CV=0.49, Neg years (linear/tail)=1/0 of 8, Half ratio=1.07, Recency ratio=0.61
- Early IC=+0.1838, Recent IC=+0.1126, 1st-half IC=+0.1231, 2nd-half IC=+0.1316, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.176, Q2=-0.032, Q3_mid=+0.141, Q4=+0.206, Q5_high_vol=+0.128

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0845, Sharpe=+0.7426)
- Admission: Train IC=+0.2819, Deflated=+0.2817, IR=0.84, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.099 | 2017: +0.193 | 2018: +0.219 | 2019: +0.150 | 2020: +0.160 | 2021: +0.133 | 2022: +0.065 | 2023: +0.103 | 2024: +0.131 | 2025: +0.019 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.327 | 2016: +0.214 | 2017: +0.422 | 2018: +0.338 | 2019: +0.349 | 2020: +0.102 | 2021: +0.171 | 2022: +0.216 | 2023: +0.219 | 2024: +0.192 | 2025: +0.066 | 2026: +0.180
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.69
- Early IC=+0.2115, Recent IC=+0.1465, 1st-half IC=+0.1930, 2nd-half IC=+0.1617, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.054, Q3_mid=+0.204, Q4=+0.151, Q5_high_vol=+0.310

**`combo_rank_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1111, Sharpe=+0.7424)
- Admission: Train IC=+0.2188, Deflated=+0.2179, IR=0.59, Mono=0.70, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.056 | 2017: +0.230 | 2018: +0.093 | 2019: +0.123 | 2020: +0.133 | 2021: +0.032 | 2022: +0.096 | 2023: +0.036 | 2024: +0.139 | 2025: +0.111 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.343 | 2016: +0.065 | 2017: +0.185 | 2018: +0.151 | 2019: +0.343 | 2020: +0.164 | 2021: +0.294 | 2022: +0.113 | 2023: +0.029 | 2024: +0.176 | 2025: +0.302 | 2026: +0.221
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.32
- Early IC=+0.2507, Recent IC=+0.0809, 1st-half IC=+0.2010, 2nd-half IC=+0.0997, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.042, Q3_mid=+0.162, Q4=+0.113, Q5_high_vol=+0.232

**`combo_sig_product__opening_drive_thrust_ratio__opening_auction_imbalance`** (Lock IC=+0.0913, Sharpe=+0.7352)
- Admission: Train IC=+0.2643, Deflated=+0.2635, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.049 | 2017: +0.222 | 2018: +0.209 | 2019: +0.089 | 2020: +0.156 | 2021: +0.099 | 2022: +0.119 | 2023: +0.108 | 2024: +0.110 | 2025: +0.085 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.388 | 2016: +0.083 | 2017: +0.256 | 2018: +0.245 | 2019: +0.166 | 2020: +0.274 | 2021: +0.180 | 2022: +0.244 | 2023: +0.334 | 2024: +0.276 | 2025: +0.032 | 2026: -0.076
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.66
- Early IC=+0.1918, Recent IC=+0.1273, 1st-half IC=+0.1619, 2nd-half IC=+0.1370, Neg regimes=0/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.038, Q3_mid=+0.200, Q4=+0.151, Q5_high_vol=+0.182

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1005, Sharpe=+0.7282)
- Admission: Train IC=+0.3474, Deflated=+0.3463, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.290 | 2016: +0.034 | 2017: +0.146 | 2018: +0.192 | 2019: +0.200 | 2020: +0.202 | 2021: +0.147 | 2022: +0.067 | 2023: +0.067 | 2024: +0.123 | 2025: +0.086 | 2026: +0.153
- Yearly Tail ICs:   2015: +0.238 | 2016: +0.056 | 2017: +0.178 | 2018: +0.343 | 2019: +0.478 | 2020: +0.231 | 2021: +0.269 | 2022: -0.033 | 2023: +0.131 | 2024: +0.159 | 2025: +0.113 | 2026: +0.374
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.66
- Early IC=+0.2628, Recent IC=+0.1742, 1st-half IC=+0.1950, 2nd-half IC=+0.1828, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.124, Q3_mid=+0.176, Q4=+0.181, Q5_high_vol=+0.272

**`combo_max__trend_bar_close_consistency__bar_body_rng_0`** (Lock IC=+0.0714, Sharpe=+0.7249)
- Admission: Train IC=+0.2568, Deflated=+0.2563, IR=0.71, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.117 | 2017: +0.188 | 2018: +0.149 | 2019: +0.059 | 2020: +0.145 | 2021: +0.105 | 2022: +0.100 | 2023: +0.092 | 2024: +0.095 | 2025: +0.122 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.453 | 2016: +0.137 | 2017: +0.189 | 2018: +0.177 | 2019: +0.035 | 2020: +0.303 | 2021: +0.186 | 2022: +0.296 | 2023: +0.217 | 2024: +0.251 | 2025: +0.044 | 2026: -0.288
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.65
- Early IC=+0.1916, Recent IC=+0.1251, 1st-half IC=+0.1740, 2nd-half IC=+0.1147, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.003, Q3_mid=+0.186, Q4=+0.143, Q5_high_vol=+0.203

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`** (Lock IC=+0.1066, Sharpe=+0.7248)
- Admission: Train IC=+0.2836, Deflated=+0.2832, IR=0.85, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.062 | 2017: +0.218 | 2018: +0.190 | 2019: +0.128 | 2020: +0.161 | 2021: +0.092 | 2022: +0.100 | 2023: +0.112 | 2024: +0.164 | 2025: +0.115 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.346 | 2016: +0.197 | 2017: +0.206 | 2018: +0.267 | 2019: +0.263 | 2020: +0.225 | 2021: +0.155 | 2022: +0.374 | 2023: +0.260 | 2024: +0.268 | 2025: +0.013 | 2026: -0.127
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.49
- Early IC=+0.2585, Recent IC=+0.1265, 1st-half IC=+0.2024, 2nd-half IC=+0.1414, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.220, Q2=+0.053, Q3_mid=+0.193, Q4=+0.194, Q5_high_vol=+0.210

**`combo_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0830, Sharpe=+0.7234)
- Admission: Train IC=+0.3012, Deflated=+0.3000, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.072 | 2017: +0.196 | 2018: +0.155 | 2019: +0.173 | 2020: +0.113 | 2021: +0.094 | 2022: +0.028 | 2023: +0.065 | 2024: +0.113 | 2025: +0.125 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.243 | 2016: +0.098 | 2017: +0.239 | 2018: +0.370 | 2019: +0.334 | 2020: +0.245 | 2021: +0.061 | 2022: +0.129 | 2023: +0.091 | 2024: +0.315 | 2025: +0.117 | 2026: +0.139
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.41
- Early IC=+0.2517, Recent IC=+0.1036, 1st-half IC=+0.1974, 2nd-half IC=+0.1319, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.029, Q3_mid=+0.113, Q4=+0.197, Q5_high_vol=+0.238

**`combo_mean__close_vs_open_range__bar_body_rng_0`** (Lock IC=+0.0857, Sharpe=+0.7210)
- Admission: Train IC=+0.2320, Deflated=+0.2306, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.104 | 2017: +0.219 | 2018: +0.187 | 2019: +0.113 | 2020: +0.107 | 2021: +0.115 | 2022: +0.073 | 2023: +0.084 | 2024: +0.143 | 2025: +0.130 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.100 | 2017: +0.221 | 2018: +0.285 | 2019: +0.214 | 2020: +0.144 | 2021: +0.260 | 2022: +0.326 | 2023: +0.201 | 2024: +0.337 | 2025: +0.118 | 2026: -0.042
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.56
- Early IC=+0.1995, Recent IC=+0.1108, 1st-half IC=+0.1733, 2nd-half IC=+0.1287, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.015, Q3_mid=+0.166, Q4=+0.187, Q5_high_vol=+0.210

**`combo_mean__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0938, Sharpe=+0.7191)
- Admission: Train IC=+0.2584, Deflated=+0.2572, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.073 | 2017: +0.226 | 2018: +0.165 | 2019: +0.117 | 2020: +0.152 | 2021: +0.122 | 2022: +0.080 | 2023: +0.100 | 2024: +0.152 | 2025: +0.113 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.411 | 2016: +0.196 | 2017: +0.321 | 2018: +0.218 | 2019: +0.351 | 2020: +0.163 | 2021: +0.315 | 2022: +0.202 | 2023: +0.200 | 2024: +0.323 | 2025: -0.025 | 2026: -0.022
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.62
- Early IC=+0.2210, Recent IC=+0.1373, 1st-half IC=+0.1866, 2nd-half IC=+0.1394, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.039, Q3_mid=+0.194, Q4=+0.196, Q5_high_vol=+0.197

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1089, Sharpe=+0.7190)
- Admission: Train IC=+0.3277, Deflated=+0.3266, IR=0.98, Mono=0.82, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.153 | 2017: +0.220 | 2018: +0.131 | 2019: +0.134 | 2020: +0.179 | 2021: +0.149 | 2022: +0.036 | 2023: +0.108 | 2024: +0.152 | 2025: +0.089 | 2026: +0.149
- Yearly Tail ICs:   2015: +0.248 | 2016: +0.288 | 2017: +0.231 | 2018: +0.435 | 2019: +0.215 | 2020: +0.297 | 2021: +0.395 | 2022: -0.022 | 2023: -0.036 | 2024: +0.277 | 2025: -0.019 | 2026: +0.307
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.64
- Early IC=+0.2542, Recent IC=+0.1639, 1st-half IC=+0.2437, 2nd-half IC=+0.1469, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.073, Q3_mid=+0.194, Q4=+0.229, Q5_high_vol=+0.249

**`combo_rel_diff__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0802, Sharpe=+0.7184)
- Admission: Train IC=+0.2923, Deflated=+0.2918, IR=1.06, Mono=0.84, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.089 | 2017: +0.124 | 2018: +0.244 | 2019: +0.170 | 2020: +0.188 | 2021: +0.167 | 2022: +0.039 | 2023: +0.095 | 2024: +0.142 | 2025: +0.068 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.159 | 2017: +0.308 | 2018: +0.546 | 2019: +0.247 | 2020: +0.128 | 2021: +0.292 | 2022: +0.133 | 2023: +0.172 | 2024: +0.177 | 2025: -0.047 | 2026: +0.088
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.75
- Early IC=+0.2369, Recent IC=+0.1775, 1st-half IC=+0.1955, 2nd-half IC=+0.1868, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.103, Q3_mid=+0.208, Q4=+0.194, Q5_high_vol=+0.280

**`combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`** (Lock IC=+0.0781, Sharpe=+0.7147)
- Admission: Train IC=+0.2182, Deflated=+0.2181, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.079 | 2017: +0.161 | 2018: +0.086 | 2019: +0.060 | 2020: +0.092 | 2021: +0.052 | 2022: +0.093 | 2023: +0.098 | 2024: +0.107 | 2025: +0.126 | 2026: -0.090
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.146 | 2017: +0.106 | 2018: +0.154 | 2019: +0.231 | 2020: +0.055 | 2021: +0.178 | 2022: +0.170 | 2023: +0.256 | 2024: +0.333 | 2025: -0.052 | 2026: +0.031
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.48
- Early IC=+0.1485, Recent IC=+0.0719, 1st-half IC=+0.1415, 2nd-half IC=+0.0774, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.011, Q3_mid=+0.167, Q4=+0.155, Q5_high_vol=+0.088

**`combo_rank_max__max_down_ret__close_vs_open_range`** (Lock IC=+0.0778, Sharpe=+0.7098)
- Admission: Train IC=+0.1957, Deflated=+0.1947, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.052 | 2017: +0.222 | 2018: +0.143 | 2019: +0.105 | 2020: +0.110 | 2021: +0.094 | 2022: +0.060 | 2023: +0.039 | 2024: +0.138 | 2025: +0.163 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.103 | 2017: +0.265 | 2018: +0.092 | 2019: +0.304 | 2020: +0.054 | 2021: +0.286 | 2022: +0.167 | 2023: +0.094 | 2024: +0.275 | 2025: +0.369 | 2026: +0.092
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.51
- Early IC=+0.1992, Recent IC=+0.1012, 1st-half IC=+0.1592, 2nd-half IC=+0.1085, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.021, Q3_mid=+0.165, Q4=+0.172, Q5_high_vol=+0.140

**`combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0987, Sharpe=+0.7070)
- Admission: Train IC=+0.2788, Deflated=+0.2785, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.121 | 2017: +0.226 | 2018: +0.223 | 2019: +0.146 | 2020: +0.139 | 2021: +0.071 | 2022: +0.119 | 2023: +0.080 | 2024: +0.118 | 2025: +0.149 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.247 | 2016: +0.142 | 2017: +0.215 | 2018: +0.294 | 2019: +0.303 | 2020: +0.289 | 2021: +0.098 | 2022: +0.225 | 2023: +0.205 | 2024: +0.327 | 2025: -0.026 | 2026: -0.214
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.43
- Early IC=+0.2425, Recent IC=+0.1050, 1st-half IC=+0.2188, 2nd-half IC=+0.1462, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.201, Q2=+0.039, Q3_mid=+0.199, Q4=+0.191, Q5_high_vol=+0.242

**`combo_rank_max__max_up_ret__opening_auction_imbalance`** (Lock IC=+0.0949, Sharpe=+0.7063)
- Admission: Train IC=+0.2716, Deflated=+0.2705, IR=0.93, Mono=0.83, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.101 | 2017: +0.185 | 2018: +0.218 | 2019: +0.083 | 2020: +0.125 | 2021: +0.095 | 2022: +0.106 | 2023: +0.096 | 2024: +0.139 | 2025: +0.102 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.329 | 2016: +0.217 | 2017: +0.239 | 2018: +0.285 | 2019: +0.120 | 2020: +0.309 | 2021: +0.296 | 2022: +0.156 | 2023: +0.208 | 2024: +0.314 | 2025: -0.028 | 2026: -0.217
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.49
- Early IC=+0.2238, Recent IC=+0.1096, 1st-half IC=+0.2022, 2nd-half IC=+0.1265, Neg regimes=1/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.000, Q3_mid=+0.209, Q4=+0.184, Q5_high_vol=+0.246

**`combo_tri_mean__opening_drive_thrust_ratio__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.0992, Sharpe=+0.7063)
- Admission: Train IC=+0.2971, Deflated=+0.2965, IR=1.00, Mono=0.83, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.084 | 2017: +0.215 | 2018: +0.186 | 2019: +0.128 | 2020: +0.168 | 2021: +0.106 | 2022: +0.089 | 2023: +0.079 | 2024: +0.132 | 2025: +0.102 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.371 | 2016: +0.185 | 2017: +0.325 | 2018: +0.290 | 2019: +0.313 | 2020: +0.171 | 2021: +0.182 | 2022: +0.325 | 2023: +0.198 | 2024: +0.231 | 2025: +0.037 | 2026: -0.133
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.54
- Early IC=+0.2546, Recent IC=+0.1370, 1st-half IC=+0.2128, 2nd-half IC=+0.1503, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.051, Q3_mid=+0.210, Q4=+0.221, Q5_high_vol=+0.215

**`combo_ratio__max_down_ret__early_order_flow_imbalance`** (Lock IC=+0.0698, Sharpe=+0.7012)
- Admission: Train IC=+0.1471, Deflated=+0.1468, IR=0.44, Mono=0.67, p=0.0034, MaxCorr=0.08
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.069 | 2017: +0.233 | 2018: +0.129 | 2019: +0.074 | 2020: +0.091 | 2021: -0.081 | 2022: -0.015 | 2023: +0.015 | 2024: +0.087 | 2025: +0.196 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.292 | 2016: +0.138 | 2017: +0.288 | 2018: +0.141 | 2019: +0.052 | 2020: +0.081 | 2021: +0.139 | 2022: -0.072 | 2023: -0.115 | 2024: +0.181 | 2025: +0.428 | 2026: +0.354
- IC CV=0.85, Neg years (linear/tail)=1/0 of 8, Half ratio=0.29, Recency ratio=0.02
- Early IC=+0.2059, Recent IC=+0.0050, 1st-half IC=+0.1641, 2nd-half IC=+0.0482, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.012, Q3_mid=+0.102, Q4=+0.100, Q5_high_vol=+0.153

**`combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early`** (Lock IC=+0.0993, Sharpe=+0.7007)
- Admission: Train IC=+0.2831, Deflated=+0.2820, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.046 | 2017: +0.222 | 2018: +0.072 | 2019: +0.070 | 2020: +0.104 | 2021: +0.067 | 2022: +0.039 | 2023: +0.080 | 2024: +0.119 | 2025: +0.124 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.167 | 2017: +0.388 | 2018: +0.314 | 2019: +0.091 | 2020: +0.189 | 2021: +0.145 | 2022: +0.211 | 2023: -0.043 | 2024: +0.320 | 2025: +0.085 | 2026: +0.115
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.46
- Early IC=+0.1894, Recent IC=+0.0881, 1st-half IC=+0.1549, 2nd-half IC=+0.0837, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.017, Q3_mid=+0.103, Q4=+0.189, Q5_high_vol=+0.120

**`combo_clamp_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1149, Sharpe=+0.7005)
- Admission: Train IC=+0.2947, Deflated=+0.2935, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.070 | 2017: +0.245 | 2018: +0.194 | 2019: +0.134 | 2020: +0.156 | 2021: +0.086 | 2022: +0.093 | 2023: +0.127 | 2024: +0.126 | 2025: +0.154 | 2026: +0.033
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.072 | 2017: +0.268 | 2018: +0.323 | 2019: +0.330 | 2020: +0.331 | 2021: +0.164 | 2022: +0.233 | 2023: +0.186 | 2024: +0.283 | 2025: +0.205 | 2026: -0.053
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.49
- Early IC=+0.2485, Recent IC=+0.1209, 1st-half IC=+0.2123, 2nd-half IC=+0.1453, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.224, Q2=+0.059, Q3_mid=+0.181, Q4=+0.183, Q5_high_vol=+0.242

**`combo_max__volatility_expansion_trend_vector__bar_body_rng_0`** (Lock IC=+0.0814, Sharpe=+0.6982)
- Admission: Train IC=+0.2665, Deflated=+0.2655, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.120 | 2017: +0.205 | 2018: +0.180 | 2019: +0.108 | 2020: +0.134 | 2021: +0.121 | 2022: +0.103 | 2023: +0.076 | 2024: +0.121 | 2025: +0.130 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.447 | 2016: -0.125 | 2017: +0.280 | 2018: +0.249 | 2019: +0.351 | 2020: +0.202 | 2021: +0.214 | 2022: +0.330 | 2023: +0.322 | 2024: +0.228 | 2025: +0.088 | 2026: -0.338
- IC CV=0.27, Neg years (linear/tail)=0/1 of 8, Half ratio=0.74, Recency ratio=0.63
- Early IC=+0.2023, Recent IC=+0.1274, 1st-half IC=+0.1830, 2nd-half IC=+0.1353, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.012, Q3_mid=+0.195, Q4=+0.163, Q5_high_vol=+0.223

**`combo_rank_max__max_up_ret__max_down_ret`** (Lock IC=+0.0842, Sharpe=+0.6905)
- Admission: Train IC=+0.2602, Deflated=+0.2591, IR=0.95, Mono=0.83, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.078 | 2017: +0.232 | 2018: +0.240 | 2019: +0.124 | 2020: +0.132 | 2021: +0.127 | 2022: +0.077 | 2023: +0.052 | 2024: +0.142 | 2025: +0.111 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.533 | 2016: -0.023 | 2017: +0.197 | 2018: +0.194 | 2019: +0.374 | 2020: +0.193 | 2021: +0.301 | 2022: +0.142 | 2023: +0.092 | 2024: +0.311 | 2025: +0.202 | 2026: -0.056
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.74, Recency ratio=0.55
- Early IC=+0.2348, Recent IC=+0.1288, 1st-half IC=+0.2020, 2nd-half IC=+0.1494, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.018, Q3_mid=+0.213, Q4=+0.188, Q5_high_vol=+0.251

**`combo_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration`** (Lock IC=+0.0882, Sharpe=+0.6855)
- Admission: Train IC=+0.3089, Deflated=+0.3083, IR=1.02, Mono=0.84, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.058 | 2017: +0.165 | 2018: +0.246 | 2019: +0.171 | 2020: +0.157 | 2021: +0.148 | 2022: +0.065 | 2023: +0.099 | 2024: +0.144 | 2025: +0.097 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.439 | 2016: +0.066 | 2017: +0.190 | 2018: +0.412 | 2019: +0.235 | 2020: +0.222 | 2021: +0.334 | 2022: +0.233 | 2023: +0.315 | 2024: +0.299 | 2025: +0.087 | 2026: -0.199
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.65
- Early IC=+0.2341, Recent IC=+0.1527, 1st-half IC=+0.1785, 2nd-half IC=+0.1754, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.060, Q3_mid=+0.217, Q4=+0.186, Q5_high_vol=+0.244

**`combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration`** (Lock IC=+0.0816, Sharpe=+0.6847)
- Admission: Train IC=+0.3070, Deflated=+0.3066, IR=1.02, Mono=0.84, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.056 | 2017: +0.153 | 2018: +0.232 | 2019: +0.171 | 2020: +0.164 | 2021: +0.162 | 2022: +0.056 | 2023: +0.095 | 2024: +0.130 | 2025: +0.092 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.026 | 2017: +0.189 | 2018: +0.388 | 2019: +0.258 | 2020: +0.218 | 2021: +0.336 | 2022: +0.233 | 2023: +0.306 | 2024: +0.300 | 2025: +0.086 | 2026: -0.204
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=0.73
- Early IC=+0.2248, Recent IC=+0.1632, 1st-half IC=+0.1710, 2nd-half IC=+0.1770, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.054, Q3_mid=+0.203, Q4=+0.192, Q5_high_vol=+0.234

**`combo_rank_min__rbreaker_sell_setup_proximity_early__close_vs_open_range`** (Lock IC=+0.1028, Sharpe=+0.6839)
- Admission: Train IC=+0.2755, Deflated=+0.2740, IR=0.89, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.107 | 2017: +0.232 | 2018: +0.119 | 2019: +0.077 | 2020: +0.135 | 2021: +0.108 | 2022: +0.046 | 2023: +0.087 | 2024: +0.119 | 2025: +0.151 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.255 | 2016: +0.285 | 2017: +0.360 | 2018: +0.335 | 2019: +0.079 | 2020: +0.200 | 2021: +0.292 | 2022: +0.083 | 2023: +0.013 | 2024: +0.219 | 2025: +0.174 | 2026: +0.248
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.63
- Early IC=+0.1942, Recent IC=+0.1216, 1st-half IC=+0.1920, 2nd-half IC=+0.1127, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.059, Q3_mid=+0.118, Q4=+0.235, Q5_high_vol=+0.144

**`combo_tri_median__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0972, Sharpe=+0.6793)
- Admission: Train IC=+0.2862, Deflated=+0.2850, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.097 | 2017: +0.239 | 2018: +0.202 | 2019: +0.114 | 2020: +0.154 | 2021: +0.100 | 2022: +0.072 | 2023: +0.131 | 2024: +0.150 | 2025: +0.111 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.184 | 2017: +0.257 | 2018: +0.393 | 2019: +0.162 | 2020: +0.068 | 2021: +0.204 | 2022: +0.294 | 2023: +0.308 | 2024: +0.270 | 2025: -0.026 | 2026: -0.107
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.57
- Early IC=+0.2225, Recent IC=+0.1270, 1st-half IC=+0.1962, 2nd-half IC=+0.1398, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.059, Q3_mid=+0.191, Q4=+0.191, Q5_high_vol=+0.206

**`combo_max__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0902, Sharpe=+0.6742)
- Admission: Train IC=+0.2765, Deflated=+0.2756, IR=1.05, Mono=0.86, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.087 | 2017: +0.214 | 2018: +0.161 | 2019: +0.088 | 2020: +0.153 | 2021: +0.107 | 2022: +0.110 | 2023: +0.075 | 2024: +0.149 | 2025: +0.116 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.244 | 2017: +0.356 | 2018: +0.158 | 2019: +0.252 | 2020: +0.245 | 2021: +0.237 | 2022: +0.203 | 2023: +0.243 | 2024: +0.277 | 2025: +0.001 | 2026: -0.164
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.54
- Early IC=+0.2403, Recent IC=+0.1300, 1st-half IC=+0.2064, 2nd-half IC=+0.1286, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.041, Q3_mid=+0.206, Q4=+0.199, Q5_high_vol=+0.214

**`combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`** (Lock IC=+0.0738, Sharpe=+0.6716)
- Admission: Train IC=+0.2249, Deflated=+0.2245, IR=0.67, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.033 | 2017: +0.201 | 2018: +0.182 | 2019: +0.155 | 2020: +0.142 | 2021: +0.138 | 2022: +0.033 | 2023: +0.096 | 2024: +0.100 | 2025: +0.045 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.447 | 2016: +0.051 | 2017: +0.432 | 2018: +0.149 | 2019: +0.287 | 2020: +0.115 | 2021: +0.186 | 2022: +0.048 | 2023: +0.134 | 2024: +0.222 | 2025: +0.041 | 2026: +0.329
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.67
- Early IC=+0.2089, Recent IC=+0.1397, 1st-half IC=+0.1595, 2nd-half IC=+0.1487, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.055, Q3_mid=+0.173, Q4=+0.147, Q5_high_vol=+0.252

**`combo_mean__bar_ret_0__close_vs_open_range`** (Lock IC=+0.0858, Sharpe=+0.6704)
- Admission: Train IC=+0.2257, Deflated=+0.2242, IR=0.76, Mono=0.79, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.101 | 2017: +0.216 | 2018: +0.208 | 2019: +0.110 | 2020: +0.115 | 2021: +0.103 | 2022: +0.096 | 2023: +0.079 | 2024: +0.151 | 2025: +0.115 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.043 | 2017: +0.263 | 2018: +0.355 | 2019: +0.142 | 2020: +0.178 | 2021: +0.367 | 2022: +0.247 | 2023: +0.236 | 2024: +0.313 | 2025: +0.024 | 2026: -0.211
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.56
- Early IC=+0.1943, Recent IC=+0.1089, 1st-half IC=+0.1819, 2nd-half IC=+0.1334, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.009, Q3_mid=+0.157, Q4=+0.187, Q5_high_vol=+0.195

**`combo_min__opening_auction_imbalance__vwap_close_divergence_trend`** (Lock IC=+0.0870, Sharpe=+0.6650)
- Admission: Train IC=+0.2231, Deflated=+0.2229, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.125 | 2016: +0.041 | 2017: +0.186 | 2018: +0.122 | 2019: +0.089 | 2020: +0.106 | 2021: +0.084 | 2022: +0.089 | 2023: +0.104 | 2024: +0.104 | 2025: +0.140 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.180 | 2016: +0.058 | 2017: +0.158 | 2018: +0.184 | 2019: +0.300 | 2020: +0.172 | 2021: +0.210 | 2022: +0.183 | 2023: +0.304 | 2024: +0.152 | 2025: +0.115 | 2026: -0.161
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.67
- Early IC=+0.1416, Recent IC=+0.0952, 1st-half IC=+0.1298, 2nd-half IC=+0.1014, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.025, Q3_mid=+0.182, Q4=+0.152, Q5_high_vol=+0.108

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1062, Sharpe=+0.6643)
- Admission: Train IC=+0.3175, Deflated=+0.3169, IR=1.07, Mono=0.84, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.136 | 2017: +0.242 | 2018: +0.242 | 2019: +0.136 | 2020: +0.199 | 2021: +0.136 | 2022: +0.091 | 2023: +0.084 | 2024: +0.129 | 2025: +0.110 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.246 | 2017: +0.317 | 2018: +0.389 | 2019: +0.295 | 2020: +0.182 | 2021: +0.232 | 2022: +0.135 | 2023: -0.035 | 2024: +0.148 | 2025: -0.102 | 2026: +0.062
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.62
- Early IC=+0.2676, Recent IC=+0.1671, 1st-half IC=+0.2505, 2nd-half IC=+0.1817, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.220, Q2=+0.091, Q3_mid=+0.237, Q4=+0.228, Q5_high_vol=+0.284

**`combo_mean__max_up_ret__max_down_ret`** (Lock IC=+0.0964, Sharpe=+0.6641)
- Admission: Train IC=+0.2430, Deflated=+0.2419, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.065 | 2017: +0.237 | 2018: +0.210 | 2019: +0.116 | 2020: +0.134 | 2021: +0.111 | 2022: +0.105 | 2023: +0.093 | 2024: +0.160 | 2025: +0.108 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.368 | 2016: +0.215 | 2017: +0.318 | 2018: +0.291 | 2019: +0.176 | 2020: +0.132 | 2021: +0.319 | 2022: +0.130 | 2023: +0.257 | 2024: +0.297 | 2025: -0.034 | 2026: -0.115
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.55
- Early IC=+0.2220, Recent IC=+0.1223, 1st-half IC=+0.2043, 2nd-half IC=+0.1379, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.038, Q3_mid=+0.201, Q4=+0.185, Q5_high_vol=+0.214

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0877, Sharpe=+0.6625)
- Admission: Train IC=+0.3161, Deflated=+0.3146, IR=0.71, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.328 | 2016: +0.093 | 2017: +0.223 | 2018: +0.185 | 2019: +0.157 | 2020: +0.156 | 2021: +0.114 | 2022: +0.038 | 2023: +0.094 | 2024: +0.105 | 2025: +0.097 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.123 | 2017: +0.186 | 2018: +0.473 | 2019: +0.272 | 2020: +0.287 | 2021: +0.184 | 2022: +0.125 | 2023: +0.123 | 2024: +0.245 | 2025: +0.098 | 2026: +0.158
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.49
- Early IC=+0.2774, Recent IC=+0.1351, 1st-half IC=+0.2418, 2nd-half IC=+0.1525, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.058, Q3_mid=+0.168, Q4=+0.234, Q5_high_vol=+0.255

**`combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`** (Lock IC=+0.0793, Sharpe=+0.6624)
- Admission: Train IC=+0.2172, Deflated=+0.2169, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.140 | 2016: +0.083 | 2017: +0.163 | 2018: +0.084 | 2019: +0.060 | 2020: +0.084 | 2021: +0.048 | 2022: +0.088 | 2023: +0.103 | 2024: +0.116 | 2025: +0.123 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.347 | 2016: +0.144 | 2017: +0.106 | 2018: +0.154 | 2019: +0.228 | 2020: +0.054 | 2021: +0.178 | 2022: +0.170 | 2023: +0.258 | 2024: +0.333 | 2025: -0.050 | 2026: +0.042
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.45
- Early IC=+0.1484, Recent IC=+0.0662, 1st-half IC=+0.1423, 2nd-half IC=+0.0745, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.013, Q3_mid=+0.164, Q4=+0.157, Q5_high_vol=+0.082

**`combo_min__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0697, Sharpe=+0.6569)
- Admission: Train IC=+0.2000, Deflated=+0.1991, IR=0.49, Mono=0.67, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.032 | 2017: +0.220 | 2018: +0.148 | 2019: +0.153 | 2020: +0.071 | 2021: +0.054 | 2022: +0.038 | 2023: +0.055 | 2024: +0.098 | 2025: +0.119 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.096 | 2016: +0.066 | 2017: +0.232 | 2018: +0.284 | 2019: +0.287 | 2020: +0.046 | 2021: +0.187 | 2022: +0.219 | 2023: +0.067 | 2024: +0.097 | 2025: +0.341 | 2026: -0.018
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.38
- Early IC=+0.1632, Recent IC=+0.0623, 1st-half IC=+0.1378, 2nd-half IC=+0.1084, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.035, Q3_mid=+0.141, Q4=+0.173, Q5_high_vol=+0.138

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0978, Sharpe=+0.6543)
- Admission: Train IC=+0.2638, Deflated=+0.2624, IR=0.86, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.084 | 2017: +0.247 | 2018: +0.154 | 2019: +0.106 | 2020: +0.168 | 2021: +0.113 | 2022: +0.116 | 2023: +0.079 | 2024: +0.148 | 2025: +0.115 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.543 | 2016: +0.166 | 2017: +0.280 | 2018: +0.204 | 2019: +0.261 | 2020: +0.072 | 2021: +0.311 | 2022: +0.226 | 2023: +0.106 | 2024: +0.237 | 2025: +0.066 | 2026: -0.097
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.62
- Early IC=+0.2258, Recent IC=+0.1406, 1st-half IC=+0.1989, 2nd-half IC=+0.1340, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.030, Q3_mid=+0.185, Q4=+0.199, Q5_high_vol=+0.231

**`combo_mean__bar_ret_0__max_down_ret`** (Lock IC=+0.0763, Sharpe=+0.6533)
- Admission: Train IC=+0.2422, Deflated=+0.2413, IR=0.60, Mono=0.66, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.106 | 2017: +0.224 | 2018: +0.210 | 2019: +0.137 | 2020: +0.111 | 2021: +0.088 | 2022: +0.072 | 2023: +0.055 | 2024: +0.125 | 2025: +0.131 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.319 | 2016: +0.029 | 2017: +0.273 | 2018: +0.412 | 2019: +0.165 | 2020: +0.209 | 2021: +0.267 | 2022: +0.182 | 2023: +0.148 | 2024: +0.250 | 2025: +0.127 | 2026: -0.219
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.50
- Early IC=+0.2001, Recent IC=+0.0993, 1st-half IC=+0.1744, 2nd-half IC=+0.1348, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.022, Q3_mid=+0.142, Q4=+0.164, Q5_high_vol=+0.208

**`combo_rel_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0706, Sharpe=+0.6516)
- Admission: Train IC=+0.2752, Deflated=+0.2753, IR=1.01, Mono=0.79, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.336 | 2016: +0.116 | 2017: +0.176 | 2018: +0.207 | 2019: +0.122 | 2020: +0.131 | 2021: +0.143 | 2022: +0.047 | 2023: +0.077 | 2024: +0.086 | 2025: +0.036 | 2026: +0.110
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.076 | 2017: +0.380 | 2018: +0.364 | 2019: +0.373 | 2020: +0.098 | 2021: +0.232 | 2022: +0.097 | 2023: +0.178 | 2024: -0.062 | 2025: -0.052 | 2026: +0.085
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.63
- Early IC=+0.2163, Recent IC=+0.1369, 1st-half IC=+0.1993, 2nd-half IC=+0.1466, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.049, Q3_mid=+0.197, Q4=+0.139, Q5_high_vol=+0.288

**`combo_mean__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0922, Sharpe=+0.6453)
- Admission: Train IC=+0.2592, Deflated=+0.2584, IR=0.97, Mono=0.85, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.088 | 2017: +0.212 | 2018: +0.177 | 2019: +0.095 | 2020: +0.126 | 2021: +0.112 | 2022: +0.108 | 2023: +0.100 | 2024: +0.137 | 2025: +0.117 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.231 | 2017: +0.258 | 2018: +0.390 | 2019: +0.168 | 2020: +0.260 | 2021: +0.267 | 2022: +0.144 | 2023: +0.348 | 2024: +0.243 | 2025: -0.083 | 2026: -0.157
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.58
- Early IC=+0.2057, Recent IC=+0.1189, 1st-half IC=+0.1914, 2nd-half IC=+0.1244, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.024, Q3_mid=+0.197, Q4=+0.184, Q5_high_vol=+0.186

**`combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0931, Sharpe=+0.6427)
- Admission: Train IC=+0.2939, Deflated=+0.2928, IR=0.92, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.068 | 2017: +0.231 | 2018: +0.171 | 2019: +0.121 | 2020: +0.150 | 2021: +0.117 | 2022: +0.087 | 2023: +0.100 | 2024: +0.145 | 2025: +0.122 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.508 | 2016: +0.171 | 2017: +0.235 | 2018: +0.255 | 2019: +0.354 | 2020: +0.225 | 2021: +0.273 | 2022: +0.309 | 2023: +0.282 | 2024: +0.244 | 2025: +0.092 | 2026: -0.026
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.60
- Early IC=+0.2224, Recent IC=+0.1335, 1st-half IC=+0.1892, 2nd-half IC=+0.1374, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.037, Q3_mid=+0.203, Q4=+0.198, Q5_high_vol=+0.189

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1146, Sharpe=+0.6421)
- Admission: Train IC=+0.3079, Deflated=+0.3067, IR=0.92, Mono=0.78, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.138 | 2017: +0.218 | 2018: +0.124 | 2019: +0.143 | 2020: +0.175 | 2021: +0.141 | 2022: +0.049 | 2023: +0.106 | 2024: +0.153 | 2025: +0.104 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.193 | 2017: +0.177 | 2018: +0.350 | 2019: +0.367 | 2020: +0.257 | 2021: +0.326 | 2022: +0.012 | 2023: +0.014 | 2024: +0.355 | 2025: +0.030 | 2026: +0.053
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.60
- Early IC=+0.2620, Recent IC=+0.1569, 1st-half IC=+0.2425, 2nd-half IC=+0.1429, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.075, Q3_mid=+0.195, Q4=+0.217, Q5_high_vol=+0.253

**`combo_mean__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0948, Sharpe=+0.6420)
- Admission: Train IC=+0.2775, Deflated=+0.2765, IR=1.10, Mono=0.85, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.101 | 2017: +0.237 | 2018: +0.226 | 2019: +0.133 | 2020: +0.166 | 2021: +0.146 | 2022: +0.086 | 2023: +0.113 | 2024: +0.164 | 2025: +0.083 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.249 | 2016: +0.250 | 2017: +0.343 | 2018: +0.424 | 2019: +0.227 | 2020: +0.192 | 2021: +0.318 | 2022: +0.221 | 2023: +0.150 | 2024: +0.250 | 2025: -0.205 | 2026: -0.149
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.64
- Early IC=+0.2441, Recent IC=+0.1563, 1st-half IC=+0.2241, 2nd-half IC=+0.1660, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.211, Q2=+0.074, Q3_mid=+0.234, Q4=+0.204, Q5_high_vol=+0.257

**`opening_drive_thrust_ratio`** (Lock IC=+0.0900, Sharpe=+0.6418)
- Admission: Train IC=+0.2887, Deflated=+0.2875, IR=0.84, Mono=0.82, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069 | 2023: +0.102 | 2024: +0.152 | 2025: +0.088 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.517 | 2016: +0.047 | 2017: +0.205 | 2018: +0.244 | 2019: +0.347 | 2020: +0.069 | 2021: +0.321 | 2022: +0.278 | 2023: +0.019 | 2024: +0.151 | 2025: +0.052 | 2026: +0.004
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.66
- Early IC=+0.2368, Recent IC=+0.1555, 1st-half IC=+0.1959, 2nd-half IC=+0.1607, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.071, Q3_mid=+0.200, Q4=+0.194, Q5_high_vol=+0.247

**`combo_min__max_up_ret__opening_auction_imbalance`** (Lock IC=+0.0922, Sharpe=+0.6394)
- Admission: Train IC=+0.2578, Deflated=+0.2572, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.073 | 2017: +0.181 | 2018: +0.165 | 2019: +0.111 | 2020: +0.117 | 2021: +0.138 | 2022: +0.127 | 2023: +0.113 | 2024: +0.139 | 2025: +0.123 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.133 | 2017: +0.256 | 2018: +0.343 | 2019: +0.135 | 2020: +0.278 | 2021: +0.163 | 2022: +0.203 | 2023: +0.365 | 2024: +0.267 | 2025: -0.015 | 2026: -0.044
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.68
- Early IC=+0.1882, Recent IC=+0.1273, 1st-half IC=+0.1731, 2nd-half IC=+0.1286, Neg regimes=0/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.025, Q3_mid=+0.230, Q4=+0.167, Q5_high_vol=+0.151

**`combo_tri_mean__opening_drive_thrust_ratio__opening_auction_imbalance__smooth_momentum_structure`** (Lock IC=+0.0809, Sharpe=+0.6374)
- Admission: Train IC=+0.2078, Deflated=+0.2072, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.062 | 2017: +0.179 | 2018: +0.100 | 2019: +0.038 | 2020: +0.088 | 2021: +0.061 | 2022: +0.112 | 2023: +0.065 | 2024: +0.119 | 2025: +0.131 | 2026: -0.097
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.081 | 2017: +0.304 | 2018: +0.053 | 2019: +0.054 | 2020: +0.284 | 2021: +0.166 | 2022: +0.226 | 2023: +0.189 | 2024: +0.208 | 2025: +0.095 | 2026: -0.059
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.50
- Early IC=+0.1491, Recent IC=+0.0741, 1st-half IC=+0.1364, 2nd-half IC=+0.0740, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.182, Q2=-0.032, Q3_mid=+0.155, Q4=+0.157, Q5_high_vol=+0.092

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1207, Sharpe=+0.6358)
- Admission: Train IC=+0.2174, Deflated=+0.2160, IR=0.55, Mono=0.68, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.049 | 2017: +0.188 | 2018: +0.141 | 2019: +0.175 | 2020: +0.114 | 2021: +0.083 | 2022: +0.070 | 2023: +0.098 | 2024: +0.158 | 2025: +0.115 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.052 | 2017: +0.155 | 2018: +0.211 | 2019: +0.452 | 2020: +0.257 | 2021: +0.203 | 2022: +0.173 | 2023: +0.060 | 2024: +0.225 | 2025: +0.033 | 2026: +0.279
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.52
- Early IC=+0.1878, Recent IC=+0.0985, 1st-half IC=+0.1601, 2nd-half IC=+0.1284, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.081, Q3_mid=+0.139, Q4=+0.157, Q5_high_vol=+0.196

**`combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend`** (Lock IC=+0.0892, Sharpe=+0.6330)
- Admission: Train IC=+0.2298, Deflated=+0.2292, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.037 | 2017: +0.186 | 2018: +0.098 | 2019: +0.085 | 2020: +0.095 | 2021: +0.070 | 2022: +0.096 | 2023: +0.101 | 2024: +0.112 | 2025: +0.151 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.033 | 2017: +0.229 | 2018: +0.204 | 2019: +0.322 | 2020: +0.194 | 2021: +0.267 | 2022: +0.189 | 2023: +0.323 | 2024: +0.170 | 2025: +0.148 | 2026: -0.239
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.58
- Early IC=+0.1416, Recent IC=+0.0815, 1st-half IC=+0.1325, 2nd-half IC=+0.0900, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.001, Q3_mid=+0.152, Q4=+0.149, Q5_high_vol=+0.093

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1017, Sharpe=+0.6307)
- Admission: Train IC=+0.3418, Deflated=+0.3405, IR=0.95, Mono=0.80, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.056 | 2017: +0.232 | 2018: +0.168 | 2019: +0.153 | 2020: +0.151 | 2021: +0.141 | 2022: +0.017 | 2023: +0.099 | 2024: +0.182 | 2025: +0.081 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.316 | 2016: +0.151 | 2017: +0.315 | 2018: +0.446 | 2019: +0.351 | 2020: +0.247 | 2021: +0.080 | 2022: +0.190 | 2023: +0.003 | 2024: +0.272 | 2025: -0.134 | 2026: +0.239
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.55
- Early IC=+0.2647, Recent IC=+0.1463, 1st-half IC=+0.2120, 2nd-half IC=+0.1570, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.111, Q3_mid=+0.181, Q4=+0.202, Q5_high_vol=+0.229

**`combo_mean__opening_auction_imbalance__star50_limit_proximity_early`** (Lock IC=+0.0998, Sharpe=+0.6269)
- Admission: Train IC=+0.2721, Deflated=+0.2717, IR=0.81, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.089 | 2017: +0.188 | 2018: +0.152 | 2019: +0.123 | 2020: +0.149 | 2021: +0.089 | 2022: +0.089 | 2023: +0.058 | 2024: +0.111 | 2025: +0.106 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.108 | 2017: +0.226 | 2018: +0.337 | 2019: +0.356 | 2020: +0.177 | 2021: +0.133 | 2022: +0.323 | 2023: +0.173 | 2024: +0.245 | 2025: +0.033 | 2026: +0.112
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.50
- Early IC=+0.2395, Recent IC=+0.1189, 1st-half IC=+0.2003, 2nd-half IC=+0.1302, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.026, Q3_mid=+0.179, Q4=+0.195, Q5_high_vol=+0.196

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1021, Sharpe=+0.6224)
- Admission: Train IC=+0.3481, Deflated=+0.3467, IR=1.22, Mono=0.87, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.101 | 2017: +0.231 | 2018: +0.185 | 2019: +0.156 | 2020: +0.172 | 2021: +0.142 | 2022: +0.033 | 2023: +0.099 | 2024: +0.145 | 2025: +0.105 | 2026: +0.107
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.250 | 2017: +0.358 | 2018: +0.459 | 2019: +0.298 | 2020: +0.314 | 2021: +0.303 | 2022: +0.082 | 2023: -0.007 | 2024: +0.241 | 2025: +0.070 | 2026: +0.303
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.58
- Early IC=+0.2761, Recent IC=+0.1593, 1st-half IC=+0.2347, 2nd-half IC=+0.1696, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.115, Q3_mid=+0.197, Q4=+0.237, Q5_high_vol=+0.240

**`combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0745, Sharpe=+0.6106)
- Admission: Train IC=+0.2046, Deflated=+0.2038, IR=0.62, Mono=0.67, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.030 | 2017: +0.241 | 2018: +0.136 | 2019: +0.126 | 2020: +0.076 | 2021: +0.069 | 2022: +0.045 | 2023: +0.091 | 2024: +0.101 | 2025: +0.119 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.162 | 2016: -0.016 | 2017: +0.166 | 2018: +0.295 | 2019: +0.320 | 2020: +0.036 | 2021: +0.232 | 2022: +0.179 | 2023: +0.197 | 2024: -0.014 | 2025: +0.449 | 2026: -0.035
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.40
- Early IC=+0.1808, Recent IC=+0.0729, 1st-half IC=+0.1484, 2nd-half IC=+0.1029, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.035, Q3_mid=+0.155, Q4=+0.185, Q5_high_vol=+0.133

**`combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0776, Sharpe=+0.6038)
- Admission: Train IC=+0.2630, Deflated=+0.2623, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.156 | 2016: +0.068 | 2017: +0.208 | 2018: +0.087 | 2019: +0.022 | 2020: +0.125 | 2021: +0.030 | 2022: -0.016 | 2023: +0.077 | 2024: +0.067 | 2025: +0.137 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.232 | 2017: +0.295 | 2018: +0.333 | 2019: +0.037 | 2020: +0.327 | 2021: +0.254 | 2022: +0.036 | 2023: -0.061 | 2024: +0.346 | 2025: +0.208 | 2026: +0.255
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.43, Recency ratio=0.42
- Early IC=+0.1875, Recent IC=+0.0779, 1st-half IC=+0.1757, 2nd-half IC=+0.0758, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.033, Q3_mid=+0.137, Q4=+0.192, Q5_high_vol=+0.095

**`combo_mean__opening_auction_imbalance__close_vs_open_range`** (Lock IC=+0.0907, Sharpe=+0.6017)
- Admission: Train IC=+0.2417, Deflated=+0.2409, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.063 | 2017: +0.180 | 2018: +0.138 | 2019: +0.072 | 2020: +0.113 | 2021: +0.078 | 2022: +0.101 | 2023: +0.088 | 2024: +0.133 | 2025: +0.139 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.106 | 2017: +0.294 | 2018: +0.198 | 2019: +0.162 | 2020: +0.228 | 2021: +0.282 | 2022: +0.164 | 2023: +0.223 | 2024: +0.270 | 2025: +0.015 | 2026: -0.058
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.56
- Early IC=+0.1714, Recent IC=+0.0952, 1st-half IC=+0.1473, 2nd-half IC=+0.1001, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.017, Q3_mid=+0.169, Q4=+0.165, Q5_high_vol=+0.127

**`combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction`** (Lock IC=+0.0655, Sharpe=+0.5967)
- Admission: Train IC=+0.2033, Deflated=+0.2037, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.027 | 2017: +0.153 | 2018: +0.081 | 2019: +0.007 | 2020: +0.095 | 2021: +0.035 | 2022: +0.017 | 2023: +0.128 | 2024: +0.080 | 2025: +0.127 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.128 | 2017: +0.279 | 2018: +0.169 | 2019: +0.168 | 2020: +0.119 | 2021: +0.242 | 2022: +0.193 | 2023: +0.187 | 2024: +0.183 | 2025: +0.164 | 2026: -0.170
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.49
- Early IC=+0.1328, Recent IC=+0.0648, 1st-half IC=+0.1181, 2nd-half IC=+0.0614, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.164, Q2=-0.018, Q3_mid=+0.136, Q4=+0.131, Q5_high_vol=+0.068

**`combo_mean__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0904, Sharpe=+0.5938)
- Admission: Train IC=+0.2181, Deflated=+0.2170, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.061 | 2017: +0.242 | 2018: +0.192 | 2019: +0.137 | 2020: +0.164 | 2021: +0.122 | 2022: +0.079 | 2023: +0.091 | 2024: +0.137 | 2025: +0.108 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.400 | 2016: -0.025 | 2017: +0.129 | 2018: +0.124 | 2019: +0.330 | 2020: +0.018 | 2021: +0.381 | 2022: +0.254 | 2023: +0.148 | 2024: +0.233 | 2025: +0.086 | 2026: +0.051
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.79, Recency ratio=0.60
- Early IC=+0.2397, Recent IC=+0.1430, 1st-half IC=+0.1896, 2nd-half IC=+0.1489, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.054, Q3_mid=+0.182, Q4=+0.192, Q5_high_vol=+0.235

**`combo_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0769, Sharpe=+0.5915)
- Admission: Train IC=+0.2810, Deflated=+0.2804, IR=0.91, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.088 | 2017: +0.214 | 2018: +0.252 | 2019: +0.158 | 2020: +0.144 | 2021: +0.099 | 2022: +0.061 | 2023: +0.072 | 2024: +0.129 | 2025: +0.115 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.097 | 2017: +0.364 | 2018: +0.421 | 2019: +0.201 | 2020: +0.126 | 2021: +0.262 | 2022: +0.257 | 2023: +0.171 | 2024: +0.229 | 2025: +0.114 | 2026: -0.117
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.51
- Early IC=+0.2372, Recent IC=+0.1214, 1st-half IC=+0.1929, 2nd-half IC=+0.1616, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.079, Q3_mid=+0.171, Q4=+0.191, Q5_high_vol=+0.248

**`combo_rank_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0859, Sharpe=+0.5866)
- Admission: Train IC=+0.2296, Deflated=+0.2284, IR=0.65, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.048 | 2017: +0.223 | 2018: +0.166 | 2019: +0.110 | 2020: +0.147 | 2021: +0.100 | 2022: +0.078 | 2023: +0.080 | 2024: +0.119 | 2025: +0.121 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.051 | 2017: +0.156 | 2018: +0.094 | 2019: +0.327 | 2020: +0.062 | 2021: +0.353 | 2022: +0.210 | 2023: +0.072 | 2024: +0.180 | 2025: +0.121 | 2026: -0.009
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.72, Recency ratio=0.51
- Early IC=+0.2479, Recent IC=+0.1256, 1st-half IC=+0.1812, 2nd-half IC=+0.1310, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.059, Q3_mid=+0.167, Q4=+0.182, Q5_high_vol=+0.211

**`combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`** (Lock IC=+0.0858, Sharpe=+0.5858)
- Admission: Train IC=+0.2679, Deflated=+0.2674, IR=0.88, Mono=0.85, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.057 | 2017: +0.164 | 2018: +0.237 | 2019: +0.160 | 2020: +0.163 | 2021: +0.150 | 2022: +0.067 | 2023: +0.090 | 2024: +0.139 | 2025: +0.106 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.364 | 2016: -0.044 | 2017: +0.117 | 2018: +0.348 | 2019: +0.322 | 2020: +0.163 | 2021: +0.294 | 2022: +0.166 | 2023: +0.311 | 2024: +0.220 | 2025: +0.258 | 2026: -0.202
- IC CV=0.32, Neg years (linear/tail)=0/1 of 8, Half ratio=1.00, Recency ratio=0.70
- Early IC=+0.2245, Recent IC=+0.1564, 1st-half IC=+0.1726, 2nd-half IC=+0.1727, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.060, Q3_mid=+0.198, Q4=+0.192, Q5_high_vol=+0.229

**`combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0846, Sharpe=+0.5809)
- Admission: Train IC=+0.2677, Deflated=+0.2670, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.059 | 2017: +0.198 | 2018: +0.212 | 2019: +0.138 | 2020: +0.107 | 2021: +0.106 | 2022: +0.069 | 2023: +0.084 | 2024: +0.131 | 2025: +0.142 | 2026: -0.043
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.059 | 2017: +0.296 | 2018: +0.340 | 2019: +0.268 | 2020: +0.163 | 2021: +0.334 | 2022: +0.278 | 2023: +0.241 | 2024: +0.250 | 2025: +0.124 | 2026: -0.062
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.52
- Early IC=+0.2067, Recent IC=+0.1065, 1st-half IC=+0.1637, 2nd-half IC=+0.1398, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.018, Q3_mid=+0.160, Q4=+0.191, Q5_high_vol=+0.183

**`combo_min__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0839, Sharpe=+0.5784)
- Admission: Train IC=+0.2320, Deflated=+0.2318, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.007 | 2017: +0.153 | 2018: +0.120 | 2019: +0.128 | 2020: +0.085 | 2021: +0.123 | 2022: +0.157 | 2023: +0.078 | 2024: +0.113 | 2025: +0.078 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.315 | 2016: -0.042 | 2017: +0.208 | 2018: +0.236 | 2019: +0.249 | 2020: +0.160 | 2021: +0.304 | 2022: +0.305 | 2023: +0.139 | 2024: +0.331 | 2025: +0.134 | 2026: +0.051
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.93, Recency ratio=0.52
- Early IC=+0.1986, Recent IC=+0.1043, 1st-half IC=+0.1224, 2nd-half IC=+0.1135, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.155, Q2=-0.035, Q3_mid=+0.117, Q4=+0.200, Q5_high_vol=+0.152

**`combo_rank_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0745, Sharpe=+0.5773)
- Admission: Train IC=+0.2881, Deflated=+0.2870, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.109 | 2017: +0.217 | 2018: +0.227 | 2019: +0.127 | 2020: +0.123 | 2021: +0.101 | 2022: +0.080 | 2023: +0.086 | 2024: +0.115 | 2025: +0.082 | 2026: -0.028
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.132 | 2017: +0.221 | 2018: +0.402 | 2019: +0.273 | 2020: +0.187 | 2021: +0.242 | 2022: +0.007 | 2023: +0.017 | 2024: +0.154 | 2025: +0.195 | 2026: -0.098
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.46
- Early IC=+0.2393, Recent IC=+0.1111, 1st-half IC=+0.2152, 2nd-half IC=+0.1402, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.28)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.040, Q3_mid=+0.198, Q4=+0.181, Q5_high_vol=+0.244

**`combo_min__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0870, Sharpe=+0.5770)
- Admission: Train IC=+0.2460, Deflated=+0.2451, IR=0.79, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.061 | 2017: +0.202 | 2018: +0.176 | 2019: +0.114 | 2020: +0.138 | 2021: +0.113 | 2022: +0.046 | 2023: +0.110 | 2024: +0.143 | 2025: +0.115 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.137 | 2017: +0.309 | 2018: +0.239 | 2019: +0.356 | 2020: +0.131 | 2021: +0.282 | 2022: +0.142 | 2023: +0.078 | 2024: +0.405 | 2025: -0.026 | 2026: +0.038
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.63
- Early IC=+0.1996, Recent IC=+0.1257, 1st-half IC=+0.1630, 2nd-half IC=+0.1353, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.201, Q2=+0.041, Q3_mid=+0.185, Q4=+0.176, Q5_high_vol=+0.163

**`combo_mean__opening_auction_imbalance__bar_body_rng_0`** (Lock IC=+0.0838, Sharpe=+0.5761)
- Admission: Train IC=+0.2776, Deflated=+0.2767, IR=0.75, Mono=0.80, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.096 | 2017: +0.190 | 2018: +0.195 | 2019: +0.118 | 2020: +0.104 | 2021: +0.108 | 2022: +0.091 | 2023: +0.085 | 2024: +0.129 | 2025: +0.121 | 2026: -0.043
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.055 | 2017: +0.161 | 2018: +0.306 | 2019: +0.158 | 2020: +0.160 | 2021: +0.239 | 2022: +0.316 | 2023: +0.288 | 2024: +0.316 | 2025: +0.105 | 2026: -0.141
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.51
- Early IC=+0.2076, Recent IC=+0.1060, 1st-half IC=+0.1746, 2nd-half IC=+0.1313, Neg regimes=1/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.007, Q3_mid=+0.188, Q4=+0.178, Q5_high_vol=+0.204

**`combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction`** (Lock IC=+0.0679, Sharpe=+0.5678)
- Admission: Train IC=+0.2006, Deflated=+0.2008, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.031 | 2017: +0.154 | 2018: +0.069 | 2019: +0.020 | 2020: +0.096 | 2021: +0.031 | 2022: +0.027 | 2023: +0.122 | 2024: +0.087 | 2025: +0.124 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.115 | 2017: +0.275 | 2018: +0.156 | 2019: +0.133 | 2020: +0.125 | 2021: +0.260 | 2022: +0.191 | 2023: +0.152 | 2024: +0.220 | 2025: +0.202 | 2026: -0.182
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.47
- Early IC=+0.1321, Recent IC=+0.0627, 1st-half IC=+0.1186, 2nd-half IC=+0.0609, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.011, Q3_mid=+0.136, Q4=+0.126, Q5_high_vol=+0.070

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__early_body_momentum`** (Lock IC=+0.0971, Sharpe=+0.5555)
- Admission: Train IC=+0.3473, Deflated=+0.3462, IR=1.28, Mono=0.88, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.091 | 2017: +0.218 | 2018: +0.199 | 2019: +0.106 | 2020: +0.147 | 2021: +0.115 | 2022: +0.090 | 2023: +0.100 | 2024: +0.144 | 2025: +0.141 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.430 | 2016: +0.360 | 2017: +0.247 | 2018: +0.395 | 2019: +0.155 | 2020: +0.274 | 2021: +0.221 | 2022: +0.169 | 2023: +0.241 | 2024: +0.232 | 2025: -0.004 | 2026: -0.171
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.52
- Early IC=+0.2530, Recent IC=+0.1310, 1st-half IC=+0.2145, 2nd-half IC=+0.1404, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.050, Q3_mid=+0.225, Q4=+0.194, Q5_high_vol=+0.232

**`combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0`** (Lock IC=+0.0826, Sharpe=+0.5554)
- Admission: Train IC=+0.2464, Deflated=+0.2454, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.098 | 2017: +0.203 | 2018: +0.229 | 2019: +0.101 | 2020: +0.155 | 2021: +0.141 | 2022: +0.143 | 2023: +0.067 | 2024: +0.146 | 2025: +0.101 | 2026: -0.111
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.097 | 2017: +0.253 | 2018: +0.255 | 2019: +0.097 | 2020: +0.321 | 2021: +0.249 | 2022: +0.214 | 2023: +0.393 | 2024: +0.241 | 2025: -0.124 | 2026: -0.435
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.66
- Early IC=+0.2255, Recent IC=+0.1483, 1st-half IC=+0.2044, 2nd-half IC=+0.1546, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.036, Q3_mid=+0.232, Q4=+0.191, Q5_high_vol=+0.231

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1104, Sharpe=+0.5543)
- Admission: Train IC=+0.3217, Deflated=+0.3210, IR=1.03, Mono=0.85, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.138 | 2017: +0.228 | 2018: +0.219 | 2019: +0.109 | 2020: +0.188 | 2021: +0.146 | 2022: +0.098 | 2023: +0.112 | 2024: +0.167 | 2025: +0.103 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.337 | 2016: +0.277 | 2017: +0.274 | 2018: +0.354 | 2019: +0.242 | 2020: +0.251 | 2021: +0.320 | 2022: -0.026 | 2023: +0.106 | 2024: +0.271 | 2025: -0.017 | 2026: -0.151
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.60
- Early IC=+0.2768, Recent IC=+0.1670, 1st-half IC=+0.2496, 2nd-half IC=+0.1620, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.096, Q3_mid=+0.238, Q4=+0.189, Q5_high_vol=+0.281

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1145, Sharpe=+0.5531)
- Admission: Train IC=+0.3206, Deflated=+0.3200, IR=1.04, Mono=0.84, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.139 | 2017: +0.223 | 2018: +0.222 | 2019: +0.105 | 2020: +0.171 | 2021: +0.116 | 2022: +0.103 | 2023: +0.085 | 2024: +0.097 | 2025: +0.126 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.242 | 2016: +0.342 | 2017: +0.172 | 2018: +0.459 | 2019: +0.220 | 2020: +0.266 | 2021: +0.251 | 2022: -0.009 | 2023: -0.024 | 2024: +0.087 | 2025: +0.054 | 2026: +0.139
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.55
- Early IC=+0.2590, Recent IC=+0.1432, 1st-half IC=+0.2391, 2nd-half IC=+0.1566, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.219, Q2=+0.090, Q3_mid=+0.227, Q4=+0.201, Q5_high_vol=+0.268

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0958, Sharpe=+0.5530)
- Admission: Train IC=+0.3106, Deflated=+0.3098, IR=0.86, Mono=0.81, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.158 | 2017: +0.195 | 2018: +0.197 | 2019: +0.149 | 2020: +0.154 | 2021: +0.114 | 2022: +0.074 | 2023: +0.058 | 2024: +0.091 | 2025: +0.113 | 2026: +0.130
- Yearly Tail ICs:   2015: +0.192 | 2016: +0.258 | 2017: +0.274 | 2018: +0.353 | 2019: +0.361 | 2020: +0.159 | 2021: +0.274 | 2022: +0.093 | 2023: -0.060 | 2024: +0.098 | 2025: +0.073 | 2026: +0.201
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.54
- Early IC=+0.2476, Recent IC=+0.1341, 1st-half IC=+0.2244, 2nd-half IC=+0.1549, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.042, Q3_mid=+0.167, Q4=+0.206, Q5_high_vol=+0.271

**`combo_diff__bar_ret_0__late_bar_momentum`** (Lock IC=+0.0710, Sharpe=+0.5530)
- Admission: Train IC=+0.1993, Deflated=+0.1989, IR=0.47, Mono=0.66, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.292 | 2016: +0.069 | 2017: +0.158 | 2018: +0.232 | 2019: +0.195 | 2020: +0.113 | 2021: +0.124 | 2022: +0.064 | 2023: +0.065 | 2024: +0.118 | 2025: +0.015 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.306 | 2016: -0.091 | 2017: +0.395 | 2018: +0.347 | 2019: +0.074 | 2020: +0.215 | 2021: +0.139 | 2022: +0.073 | 2023: +0.224 | 2024: +0.225 | 2025: -0.007 | 2026: +0.028
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.98, Recency ratio=0.60
- Early IC=+0.1990, Recent IC=+0.1184, 1st-half IC=+0.1632, 2nd-half IC=+0.1596, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.042, Q3_mid=+0.166, Q4=+0.144, Q5_high_vol=+0.275

**`combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation`** (Lock IC=+0.0745, Sharpe=+0.5522)
- Admission: Train IC=+0.2511, Deflated=+0.2504, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.125 | 2017: +0.183 | 2018: +0.149 | 2019: +0.106 | 2020: +0.100 | 2021: +0.098 | 2022: +0.077 | 2023: +0.096 | 2024: +0.115 | 2025: +0.121 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.397 | 2016: -0.001 | 2017: +0.153 | 2018: +0.259 | 2019: +0.277 | 2020: +0.241 | 2021: +0.238 | 2022: +0.108 | 2023: +0.211 | 2024: +0.204 | 2025: +0.132 | 2026: -0.062
- IC CV=0.27, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.52
- Early IC=+0.1906, Recent IC=+0.0993, 1st-half IC=+0.1767, 2nd-half IC=+0.1135, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.026, Q3_mid=+0.202, Q4=+0.174, Q5_high_vol=+0.177

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum`** (Lock IC=+0.1101, Sharpe=+0.5504)
- Admission: Train IC=+0.2670, Deflated=+0.2661, IR=0.88, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.123 | 2017: +0.205 | 2018: +0.118 | 2019: +0.096 | 2020: +0.138 | 2021: +0.141 | 2022: +0.093 | 2023: +0.124 | 2024: +0.125 | 2025: +0.124 | 2026: +0.048
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.237 | 2017: +0.188 | 2018: +0.327 | 2019: +0.176 | 2020: +0.263 | 2021: +0.245 | 2022: +0.228 | 2023: +0.094 | 2024: +0.344 | 2025: +0.191 | 2026: +0.094
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.69
- Early IC=+0.2009, Recent IC=+0.1395, 1st-half IC=+0.1896, 2nd-half IC=+0.1211, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.032, Q3_mid=+0.186, Q4=+0.226, Q5_high_vol=+0.131

**`combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0873, Sharpe=+0.5471)
- Admission: Train IC=+0.2457, Deflated=+0.2444, IR=0.78, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.036 | 2017: +0.251 | 2018: +0.055 | 2019: +0.130 | 2020: +0.084 | 2021: +0.086 | 2022: +0.033 | 2023: +0.078 | 2024: +0.110 | 2025: +0.088 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.184 | 2016: +0.120 | 2017: +0.354 | 2018: +0.364 | 2019: +0.279 | 2020: +0.109 | 2021: +0.254 | 2022: +0.128 | 2023: +0.120 | 2024: +0.131 | 2025: +0.028 | 2026: -0.152
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.47
- Early IC=+0.1801, Recent IC=+0.0851, 1st-half IC=+0.1590, 2nd-half IC=+0.0950, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.026, Q3_mid=+0.114, Q4=+0.209, Q5_high_vol=+0.133

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1257, Sharpe=+0.5456)
- Admission: Train IC=+0.2303, Deflated=+0.2288, IR=0.43, Mono=0.68, p=0.0000, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.071 | 2017: +0.224 | 2018: +0.106 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089 | 2022: +0.106 | 2023: +0.058 | 2024: +0.162 | 2025: +0.049 | 2026: +0.208
- Yearly Tail ICs:   2015: +0.190 | 2016: -0.080 | 2017: +0.235 | 2018: +0.331 | 2019: +0.267 | 2020: +0.185 | 2021: +0.236 | 2022: +0.213 | 2023: -0.012 | 2024: +0.073 | 2025: -0.137 | 2026: +0.207
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.48
- Early IC=+0.2076, Recent IC=+0.0992, 1st-half IC=+0.1881, 2nd-half IC=+0.1219, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.076, Q3_mid=+0.142, Q4=+0.173, Q5_high_vol=+0.182

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0797, Sharpe=+0.5442)
- Admission: Train IC=+0.2607, Deflated=+0.2605, IR=1.03, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.106 | 2017: +0.194 | 2018: +0.211 | 2019: +0.152 | 2020: +0.162 | 2021: +0.137 | 2022: +0.065 | 2023: +0.083 | 2024: +0.104 | 2025: +0.041 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.148 | 2017: +0.360 | 2018: +0.364 | 2019: +0.376 | 2020: +0.144 | 2021: +0.254 | 2022: +0.145 | 2023: +0.193 | 2024: -0.017 | 2025: -0.013 | 2026: +0.108
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.75
- Early IC=+0.2004, Recent IC=+0.1493, 1st-half IC=+0.1885, 2nd-half IC=+0.1617, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.052, Q3_mid=+0.195, Q4=+0.145, Q5_high_vol=+0.296

**`combo_rank_min__early_order_flow_imbalance__bar_body_rng_0`** (Lock IC=+0.0836, Sharpe=+0.5426)
- Admission: Train IC=+0.2072, Deflated=+0.2062, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.012 | 2017: +0.163 | 2018: +0.155 | 2019: +0.149 | 2020: +0.063 | 2021: +0.161 | 2022: +0.126 | 2023: +0.089 | 2024: +0.121 | 2025: +0.090 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.306 | 2016: +0.070 | 2017: +0.179 | 2018: +0.335 | 2019: +0.271 | 2020: +0.065 | 2021: +0.233 | 2022: +0.258 | 2023: +0.072 | 2024: +0.302 | 2025: +0.215 | 2026: -0.073
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.58
- Early IC=+0.1945, Recent IC=+0.1135, 1st-half IC=+0.1326, 2nd-half IC=+0.1296, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.035, Q3_mid=+0.156, Q4=+0.217, Q5_high_vol=+0.131

**`combo_min__bar_ret_0__shaved_bar_trend_conviction`** (Lock IC=+0.0560, Sharpe=+0.5421)
- Admission: Train IC=+0.2049, Deflated=+0.2042, IR=0.60, Mono=0.68, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.040 | 2017: +0.166 | 2018: +0.128 | 2019: +0.075 | 2020: +0.043 | 2021: +0.016 | 2022: +0.007 | 2023: +0.090 | 2024: +0.071 | 2025: +0.104 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.329 | 2016: +0.020 | 2017: +0.274 | 2018: +0.228 | 2019: +0.126 | 2020: +0.090 | 2021: +0.130 | 2022: +0.079 | 2023: +0.097 | 2024: +0.273 | 2025: +0.250 | 2026: +0.019
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.15
- Early IC=+0.1888, Recent IC=+0.0292, 1st-half IC=+0.1470, 2nd-half IC=+0.0734, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.057, Q3_mid=+0.120, Q4=+0.165, Q5_high_vol=+0.132

**`combo_mean__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0956, Sharpe=+0.5398)
- Admission: Train IC=+0.2400, Deflated=+0.2393, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.043 | 2017: +0.212 | 2018: +0.120 | 2019: +0.097 | 2020: +0.126 | 2021: +0.109 | 2022: +0.108 | 2023: +0.117 | 2024: +0.140 | 2025: +0.126 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.118 | 2017: +0.220 | 2018: +0.318 | 2019: +0.313 | 2020: +0.106 | 2021: +0.274 | 2022: +0.194 | 2023: +0.366 | 2024: +0.238 | 2025: +0.052 | 2026: -0.245
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.68
- Early IC=+0.1744, Recent IC=+0.1179, 1st-half IC=+0.1685, 2nd-half IC=+0.1133, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.044, Q3_mid=+0.198, Q4=+0.156, Q5_high_vol=+0.146

**`combo_rank_min__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0894, Sharpe=+0.5388)
- Admission: Train IC=+0.2750, Deflated=+0.2740, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.065 | 2017: +0.192 | 2018: +0.179 | 2019: +0.098 | 2020: +0.122 | 2021: +0.118 | 2022: +0.069 | 2023: +0.124 | 2024: +0.138 | 2025: +0.129 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.234 | 2017: +0.210 | 2018: +0.278 | 2019: +0.320 | 2020: +0.177 | 2021: +0.397 | 2022: +0.186 | 2023: +0.082 | 2024: +0.209 | 2025: +0.080 | 2026: +0.056
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.63
- Early IC=+0.1953, Recent IC=+0.1226, 1st-half IC=+0.1621, 2nd-half IC=+0.1305, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.035, Q3_mid=+0.173, Q4=+0.189, Q5_high_vol=+0.150

**`combo_rank_max__max_down_ret__bar_body_rng_0`** (Lock IC=+0.0808, Sharpe=+0.5384)
- Admission: Train IC=+0.2847, Deflated=+0.2832, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.109 | 2017: +0.219 | 2018: +0.190 | 2019: +0.147 | 2020: +0.132 | 2021: +0.105 | 2022: +0.077 | 2023: +0.027 | 2024: +0.122 | 2025: +0.117 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.577 | 2016: -0.092 | 2017: +0.244 | 2018: +0.221 | 2019: +0.387 | 2020: +0.138 | 2021: +0.355 | 2022: +0.063 | 2023: +0.133 | 2024: +0.356 | 2025: +0.138 | 2026: -0.036
- IC CV=0.33, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.56
- Early IC=+0.2135, Recent IC=+0.1204, 1st-half IC=+0.1749, 2nd-half IC=+0.1436, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.006, Q3_mid=+0.160, Q4=+0.169, Q5_high_vol=+0.259

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0947, Sharpe=+0.5347)
- Admission: Train IC=+0.2898, Deflated=+0.2888, IR=0.91, Mono=0.80, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.126 | 2017: +0.216 | 2018: +0.215 | 2019: +0.132 | 2020: +0.168 | 2021: +0.103 | 2022: +0.082 | 2023: +0.071 | 2024: +0.095 | 2025: +0.117 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.150 | 2016: +0.140 | 2017: +0.263 | 2018: +0.392 | 2019: +0.272 | 2020: +0.209 | 2021: +0.180 | 2022: +0.184 | 2023: -0.026 | 2024: +0.139 | 2025: +0.130 | 2026: +0.099
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.53
- Early IC=+0.2534, Recent IC=+0.1353, 1st-half IC=+0.2318, 2nd-half IC=+0.1562, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.082, Q3_mid=+0.165, Q4=+0.183, Q5_high_vol=+0.268

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1174, Sharpe=+0.5327)
- Admission: Train IC=+0.2814, Deflated=+0.2803, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.114 | 2017: +0.200 | 2018: +0.212 | 2019: +0.104 | 2020: +0.146 | 2021: +0.103 | 2022: +0.118 | 2023: +0.123 | 2024: +0.151 | 2025: +0.146 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.249 | 2016: +0.232 | 2017: +0.197 | 2018: +0.350 | 2019: +0.271 | 2020: +0.205 | 2021: +0.196 | 2022: +0.131 | 2023: +0.132 | 2024: +0.330 | 2025: +0.047 | 2026: -0.210
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.54
- Early IC=+0.2282, Recent IC=+0.1242, 1st-half IC=+0.2141, 2nd-half IC=+0.1390, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.071, Q3_mid=+0.194, Q4=+0.181, Q5_high_vol=+0.243

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0812, Sharpe=+0.5243)
- Admission: Train IC=+0.2529, Deflated=+0.2523, IR=0.95, Mono=0.83, p=0.0000, MaxCorr=0.31
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052 | 2022: +0.096 | 2023: +0.046 | 2024: +0.073 | 2025: +0.148 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.229 | 2017: +0.386 | 2018: +0.332 | 2019: +0.207 | 2020: +0.271 | 2021: +0.214 | 2022: -0.027 | 2023: +0.087 | 2024: +0.035 | 2025: +0.246 | 2026: +0.277
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.53
- Early IC=+0.2093, Recent IC=+0.1099, 1st-half IC=+0.1721, 2nd-half IC=+0.1106, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.032, Q3_mid=+0.118, Q4=+0.173, Q5_high_vol=+0.242

**`combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.0877, Sharpe=+0.5194)
- Admission: Train IC=+0.3316, Deflated=+0.3305, IR=0.89, Mono=0.80, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.076 | 2017: +0.125 | 2018: +0.210 | 2019: +0.178 | 2020: +0.189 | 2021: +0.128 | 2022: +0.048 | 2023: +0.059 | 2024: +0.116 | 2025: +0.059 | 2026: +0.153
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.064 | 2017: +0.164 | 2018: +0.370 | 2019: +0.457 | 2020: +0.275 | 2021: +0.261 | 2022: -0.094 | 2023: -0.009 | 2024: +0.210 | 2025: +0.104 | 2026: +0.332
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.61
- Early IC=+0.2599, Recent IC=+0.1587, 1st-half IC=+0.2004, 2nd-half IC=+0.1772, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.120, Q3_mid=+0.163, Q4=+0.180, Q5_high_vol=+0.287

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.0875, Sharpe=+0.5194)
- Admission: Train IC=+0.3053, Deflated=+0.3044, IR=0.79, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.075 | 2017: +0.125 | 2018: +0.209 | 2019: +0.180 | 2020: +0.187 | 2021: +0.127 | 2022: +0.049 | 2023: +0.062 | 2024: +0.112 | 2025: +0.058 | 2026: +0.154
- Yearly Tail ICs:   2015: +0.117 | 2016: +0.026 | 2017: +0.175 | 2018: +0.352 | 2019: +0.458 | 2020: +0.216 | 2021: +0.232 | 2022: -0.068 | 2023: +0.053 | 2024: +0.118 | 2025: +0.069 | 2026: +0.287
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.61
- Early IC=+0.2565, Recent IC=+0.1570, 1st-half IC=+0.1995, 2nd-half IC=+0.1767, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.120, Q3_mid=+0.161, Q4=+0.182, Q5_high_vol=+0.279

**`combo_sig_product__max_up_ret__early_body_momentum`** (Lock IC=+0.0937, Sharpe=+0.5110)
- Admission: Train IC=+0.2623, Deflated=+0.2619, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.180 | 2017: +0.139 | 2018: +0.159 | 2019: +0.064 | 2020: +0.146 | 2021: +0.086 | 2022: +0.089 | 2023: +0.114 | 2024: +0.148 | 2025: +0.124 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.211 | 2017: +0.145 | 2018: +0.189 | 2019: +0.148 | 2020: +0.312 | 2021: +0.271 | 2022: +0.078 | 2023: +0.118 | 2024: +0.316 | 2025: +0.007 | 2026: -0.115
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.63
- Early IC=+0.1845, Recent IC=+0.1158, 1st-half IC=+0.1914, 2nd-half IC=+0.1187, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.158, Q2=-0.003, Q3_mid=+0.172, Q4=+0.160, Q5_high_vol=+0.239

**`combo_min__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0690, Sharpe=+0.5093)
- Admission: Train IC=+0.2664, Deflated=+0.2656, IR=0.70, Mono=0.72, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.110 | 2017: +0.160 | 2018: +0.230 | 2019: +0.126 | 2020: +0.086 | 2021: +0.119 | 2022: +0.067 | 2023: +0.080 | 2024: +0.111 | 2025: +0.098 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.402 | 2016: -0.056 | 2017: +0.304 | 2018: +0.446 | 2019: +0.131 | 2020: +0.097 | 2021: +0.290 | 2022: +0.167 | 2023: +0.191 | 2024: +0.154 | 2025: +0.174 | 2026: -0.129
- IC CV=0.32, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.53
- Early IC=+0.1935, Recent IC=+0.1025, 1st-half IC=+0.1700, 2nd-half IC=+0.1390, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.021, Q3_mid=+0.142, Q4=+0.164, Q5_high_vol=+0.225

**`combo_tri_median__max_up_ret__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.1026, Sharpe=+0.5084)
- Admission: Train IC=+0.2811, Deflated=+0.2803, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.051 | 2017: +0.191 | 2018: +0.203 | 2019: +0.129 | 2020: +0.121 | 2021: +0.065 | 2022: +0.111 | 2023: +0.091 | 2024: +0.145 | 2025: +0.139 | 2026: -0.028
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.167 | 2017: +0.316 | 2018: +0.412 | 2019: +0.201 | 2020: +0.147 | 2021: +0.112 | 2022: +0.080 | 2023: +0.134 | 2024: +0.281 | 2025: -0.098 | 2026: -0.294
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.41
- Early IC=+0.2249, Recent IC=+0.0929, 1st-half IC=+0.1967, 2nd-half IC=+0.1302, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.045, Q3_mid=+0.190, Q4=+0.187, Q5_high_vol=+0.200

**`combo_max__max_up_ret__close_vs_open_range`** (Lock IC=+0.0927, Sharpe=+0.5084)
- Admission: Train IC=+0.2563, Deflated=+0.2555, IR=0.93, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.099 | 2017: +0.211 | 2018: +0.212 | 2019: +0.094 | 2020: +0.145 | 2021: +0.080 | 2022: +0.119 | 2023: +0.098 | 2024: +0.131 | 2025: +0.089 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.316 | 2016: +0.244 | 2017: +0.202 | 2018: +0.323 | 2019: +0.120 | 2020: +0.254 | 2021: +0.158 | 2022: +0.065 | 2023: +0.200 | 2024: +0.255 | 2025: -0.201 | 2026: -0.269
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.52
- Early IC=+0.2173, Recent IC=+0.1126, 1st-half IC=+0.1993, 2nd-half IC=+0.1347, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.014, Q3_mid=+0.191, Q4=+0.196, Q5_high_vol=+0.240

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1070, Sharpe=+0.5071)
- Admission: Train IC=+0.2907, Deflated=+0.2903, IR=0.96, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.126 | 2017: +0.220 | 2018: +0.214 | 2019: +0.108 | 2020: +0.163 | 2021: +0.104 | 2022: +0.113 | 2023: +0.083 | 2024: +0.107 | 2025: +0.139 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.230 | 2017: +0.231 | 2018: +0.356 | 2019: +0.321 | 2020: +0.198 | 2021: +0.265 | 2022: +0.246 | 2023: +0.178 | 2024: +0.200 | 2025: -0.035 | 2026: -0.059
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.55
- Early IC=+0.2415, Recent IC=+0.1338, 1st-half IC=+0.2261, 2nd-half IC=+0.1499, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.227, Q2=+0.054, Q3_mid=+0.208, Q4=+0.216, Q5_high_vol=+0.234

**`combo_sig_product__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0770, Sharpe=+0.4999)
- Admission: Train IC=+0.1733, Deflated=+0.1726, IR=0.60, Mono=0.69, p=0.0004, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.139 | 2017: +0.068 | 2018: +0.148 | 2019: +0.080 | 2020: +0.075 | 2021: +0.105 | 2022: +0.119 | 2023: +0.137 | 2024: +0.102 | 2025: +0.106 | 2026: -0.104
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.196 | 2017: +0.076 | 2018: +0.144 | 2019: +0.190 | 2020: +0.067 | 2021: +0.263 | 2022: +0.157 | 2023: +0.268 | 2024: +0.285 | 2025: +0.277 | 2026: -0.220
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.53
- Early IC=+0.1710, Recent IC=+0.0901, 1st-half IC=+0.1414, 2nd-half IC=+0.0954, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.040, Q3_mid=+0.092, Q4=+0.117, Q5_high_vol=+0.156

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0975, Sharpe=+0.4990)
- Admission: Train IC=+0.3038, Deflated=+0.3025, IR=0.92, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.306 | 2016: +0.095 | 2017: +0.247 | 2018: +0.228 | 2019: +0.154 | 2020: +0.191 | 2021: +0.120 | 2022: +0.080 | 2023: +0.088 | 2024: +0.128 | 2025: +0.118 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.033 | 2017: +0.189 | 2018: +0.376 | 2019: +0.291 | 2020: +0.215 | 2021: +0.304 | 2022: +0.119 | 2023: +0.061 | 2024: +0.171 | 2025: +0.086 | 2026: +0.101
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.58
- Early IC=+0.2692, Recent IC=+0.1556, 1st-half IC=+0.2334, 2nd-half IC=+0.1752, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.221, Q2=+0.072, Q3_mid=+0.196, Q4=+0.216, Q5_high_vol=+0.270

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0923, Sharpe=+0.4973)
- Admission: Train IC=+0.2853, Deflated=+0.2842, IR=0.81, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.119 | 2017: +0.243 | 2018: +0.231 | 2019: +0.161 | 2020: +0.179 | 2021: +0.112 | 2022: +0.081 | 2023: +0.089 | 2024: +0.136 | 2025: +0.110 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.170 | 2017: +0.279 | 2018: +0.407 | 2019: +0.273 | 2020: +0.212 | 2021: +0.174 | 2022: +0.016 | 2023: +0.142 | 2024: +0.226 | 2025: +0.073 | 2026: -0.068
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.59
- Early IC=+0.2466, Recent IC=+0.1454, 1st-half IC=+0.2259, 2nd-half IC=+0.1670, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.230, Q2=+0.087, Q3_mid=+0.187, Q4=+0.180, Q5_high_vol=+0.264

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0913, Sharpe=+0.4968)
- Admission: Train IC=+0.2703, Deflated=+0.2694, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.135 | 2017: +0.207 | 2018: +0.239 | 2019: +0.149 | 2020: +0.126 | 2021: +0.116 | 2022: +0.075 | 2023: +0.082 | 2024: +0.128 | 2025: +0.113 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.162 | 2017: +0.225 | 2018: +0.408 | 2019: +0.107 | 2020: +0.288 | 2021: +0.072 | 2022: +0.009 | 2023: +0.143 | 2024: +0.157 | 2025: -0.044 | 2026: +0.067
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.54
- Early IC=+0.2228, Recent IC=+0.1210, 1st-half IC=+0.2084, 2nd-half IC=+0.1552, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.234, Q2=+0.039, Q3_mid=+0.191, Q4=+0.178, Q5_high_vol=+0.250

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1119, Sharpe=+0.4948)
- Admission: Train IC=+0.3197, Deflated=+0.3192, IR=1.21, Mono=0.87, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.086 | 2017: +0.211 | 2018: +0.190 | 2019: +0.149 | 2020: +0.157 | 2021: +0.115 | 2022: +0.100 | 2023: +0.115 | 2024: +0.153 | 2025: +0.133 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.407 | 2016: +0.285 | 2017: +0.347 | 2018: +0.327 | 2019: +0.227 | 2020: +0.251 | 2021: +0.214 | 2022: +0.231 | 2023: +0.202 | 2024: +0.248 | 2025: -0.004 | 2026: -0.240
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.51
- Early IC=+0.2656, Recent IC=+0.1359, 1st-half IC=+0.2180, 2nd-half IC=+0.1529, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.221, Q2=+0.049, Q3_mid=+0.225, Q4=+0.206, Q5_high_vol=+0.232

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0886, Sharpe=+0.4864)
- Admission: Train IC=+0.3074, Deflated=+0.3066, IR=0.79, Mono=0.79, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.100 | 2017: +0.224 | 2018: +0.191 | 2019: +0.097 | 2020: +0.121 | 2021: +0.120 | 2022: +0.106 | 2023: +0.073 | 2024: +0.131 | 2025: +0.094 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.537 | 2016: +0.294 | 2017: +0.252 | 2018: +0.246 | 2019: +0.175 | 2020: +0.166 | 2021: +0.322 | 2022: +0.073 | 2023: +0.185 | 2024: +0.242 | 2025: +0.016 | 2026: -0.031
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.50
- Early IC=+0.2417, Recent IC=+0.1203, 1st-half IC=+0.2137, 2nd-half IC=+0.1292, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.074, Q3_mid=+0.217, Q4=+0.163, Q5_high_vol=+0.252

**`combo_tri_max__max_up_ret__volatility_expansion_trend_vector__early_body_momentum`** (Lock IC=+0.0860, Sharpe=+0.4837)
- Admission: Train IC=+0.2729, Deflated=+0.2720, IR=1.00, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.111 | 2017: +0.190 | 2018: +0.193 | 2019: +0.068 | 2020: +0.133 | 2021: +0.067 | 2022: +0.111 | 2023: +0.089 | 2024: +0.127 | 2025: +0.089 | 2026: -0.048
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.217 | 2017: +0.267 | 2018: +0.294 | 2019: +0.120 | 2020: +0.219 | 2021: +0.205 | 2022: +0.154 | 2023: +0.147 | 2024: +0.243 | 2025: -0.131 | 2026: -0.223
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.47
- Early IC=+0.2134, Recent IC=+0.1002, 1st-half IC=+0.1958, 2nd-half IC=+0.1174, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.010, Q3_mid=+0.188, Q4=+0.194, Q5_high_vol=+0.225

**`combo_sig_product__max_up_ret__max_down_ret`** (Lock IC=+0.0935, Sharpe=+0.4827)
- Admission: Train IC=+0.2062, Deflated=+0.2067, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.69
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.196 | 2017: +0.008 | 2018: +0.155 | 2019: +0.171 | 2020: +0.139 | 2021: +0.081 | 2022: +0.056 | 2023: +0.119 | 2024: +0.161 | 2025: +0.144 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.190 | 2017: +0.124 | 2018: +0.169 | 2019: +0.295 | 2020: +0.079 | 2021: +0.297 | 2022: +0.006 | 2023: +0.105 | 2024: +0.307 | 2025: +0.223 | 2026: +0.087
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.70
- Early IC=+0.1574, Recent IC=+0.1103, 1st-half IC=+0.1718, 2nd-half IC=+0.1350, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.105, Q3_mid=+0.145, Q4=+0.153, Q5_high_vol=+0.229

**`combo_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`** (Lock IC=+0.0966, Sharpe=+0.4824)
- Admission: Train IC=+0.2040, Deflated=+0.2042, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.106 | 2017: +0.195 | 2018: +0.144 | 2019: +0.125 | 2020: +0.135 | 2021: +0.023 | 2022: +0.098 | 2023: +0.053 | 2024: +0.106 | 2025: +0.090 | 2026: +0.107
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.320 | 2017: +0.142 | 2018: +0.104 | 2019: +0.182 | 2020: +0.201 | 2021: +0.003 | 2022: +0.099 | 2023: -0.045 | 2024: +0.116 | 2025: -0.078 | 2026: -0.070
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.32
- Early IC=+0.2446, Recent IC=+0.0788, 1st-half IC=+0.2125, 2nd-half IC=+0.1086, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.039, Q3_mid=+0.216, Q4=+0.112, Q5_high_vol=+0.225

**`combo_rank_min__volatility_expansion_trend_vector__early_order_flow_imbalance`** (Lock IC=+0.0841, Sharpe=+0.4804)
- Admission: Train IC=+0.2388, Deflated=+0.2387, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.022 | 2017: +0.159 | 2018: +0.126 | 2019: +0.113 | 2020: +0.054 | 2021: +0.112 | 2022: +0.118 | 2023: +0.106 | 2024: +0.137 | 2025: +0.107 | 2026: -0.114
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.079 | 2017: +0.247 | 2018: +0.222 | 2019: +0.330 | 2020: +0.115 | 2021: +0.244 | 2022: +0.179 | 2023: +0.269 | 2024: +0.290 | 2025: +0.057 | 2026: -0.233
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.55
- Early IC=+0.1519, Recent IC=+0.0841, 1st-half IC=+0.1233, 2nd-half IC=+0.0985, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.003, Q3_mid=+0.142, Q4=+0.178, Q5_high_vol=+0.065

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1106, Sharpe=+0.4784)
- Admission: Train IC=+0.2268, Deflated=+0.2265, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.177 | 2017: +0.065 | 2018: +0.133 | 2019: +0.072 | 2020: +0.129 | 2021: +0.100 | 2022: +0.107 | 2023: +0.144 | 2024: +0.141 | 2025: +0.130 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.415 | 2016: +0.234 | 2017: +0.291 | 2018: +0.253 | 2019: +0.180 | 2020: +0.130 | 2021: +0.281 | 2022: +0.142 | 2023: +0.081 | 2024: +0.255 | 2025: -0.001 | 2026: -0.035
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.63
- Early IC=+0.1805, Recent IC=+0.1145, 1st-half IC=+0.1722, 2nd-half IC=+0.1070, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.037, Q3_mid=+0.130, Q4=+0.170, Q5_high_vol=+0.237

**`combo_min__close_vs_open_range__bar_body_rng_0`** (Lock IC=+0.0775, Sharpe=+0.4704)
- Admission: Train IC=+0.2463, Deflated=+0.2452, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.080 | 2017: +0.201 | 2018: +0.182 | 2019: +0.111 | 2020: +0.064 | 2021: +0.083 | 2022: +0.036 | 2023: +0.081 | 2024: +0.123 | 2025: +0.124 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.072 | 2017: +0.204 | 2018: +0.276 | 2019: +0.320 | 2020: +0.121 | 2021: +0.116 | 2022: +0.105 | 2023: +0.109 | 2024: +0.235 | 2025: +0.182 | 2026: +0.235
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.35
- Early IC=+0.2073, Recent IC=+0.0735, 1st-half IC=+0.1637, 2nd-half IC=+0.1105, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.208, Q2=-0.026, Q3_mid=+0.148, Q4=+0.199, Q5_high_vol=+0.163

**`combo_max__max_up_ret__max_down_ret`** (Lock IC=+0.0806, Sharpe=+0.4697)
- Admission: Train IC=+0.2650, Deflated=+0.2644, IR=0.92, Mono=0.81, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.081 | 2017: +0.245 | 2018: +0.247 | 2019: +0.118 | 2020: +0.139 | 2021: +0.101 | 2022: +0.077 | 2023: +0.057 | 2024: +0.140 | 2025: +0.096 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.276 | 2016: +0.225 | 2017: +0.295 | 2018: +0.397 | 2019: +0.149 | 2020: +0.140 | 2021: +0.319 | 2022: +0.140 | 2023: +0.228 | 2024: +0.283 | 2025: -0.104 | 2026: -0.213
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.54
- Early IC=+0.2217, Recent IC=+0.1199, 1st-half IC=+0.1982, 2nd-half IC=+0.1490, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.019, Q3_mid=+0.189, Q4=+0.201, Q5_high_vol=+0.241

**`combo_min__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0840, Sharpe=+0.4678)
- Admission: Train IC=+0.2397, Deflated=+0.2389, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.025 | 2017: +0.170 | 2018: +0.128 | 2019: +0.143 | 2020: +0.084 | 2021: +0.202 | 2022: +0.146 | 2023: +0.110 | 2024: +0.131 | 2025: +0.100 | 2026: -0.120
- Yearly Tail ICs:   2015: +0.188 | 2016: +0.058 | 2017: +0.317 | 2018: +0.364 | 2019: +0.264 | 2020: +0.053 | 2021: +0.229 | 2022: +0.271 | 2023: +0.205 | 2024: +0.328 | 2025: +0.055 | 2026: -0.310
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.85
- Early IC=+0.1686, Recent IC=+0.1426, 1st-half IC=+0.1507, 2nd-half IC=+0.1330, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.019, Q3_mid=+0.210, Q4=+0.197, Q5_high_vol=+0.091

**`combo_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1013, Sharpe=+0.4669)
- Admission: Train IC=+0.2114, Deflated=+0.2107, IR=0.45, Mono=0.67, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.050 | 2017: +0.223 | 2018: +0.091 | 2019: +0.119 | 2020: +0.142 | 2021: +0.007 | 2022: +0.085 | 2023: +0.034 | 2024: +0.139 | 2025: +0.071 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.203 | 2016: +0.178 | 2017: +0.162 | 2018: +0.064 | 2019: +0.306 | 2020: +0.183 | 2021: +0.048 | 2022: +0.078 | 2023: -0.039 | 2024: +0.142 | 2025: -0.031 | 2026: +0.143
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.48, Recency ratio=0.31
- Early IC=+0.2417, Recent IC=+0.0746, 1st-half IC=+0.1963, 2nd-half IC=+0.0939, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.044, Q3_mid=+0.136, Q4=+0.117, Q5_high_vol=+0.222

**`combo_rel_diff__first_bar_return__body_size_progression`** (Lock IC=+0.0599, Sharpe=+0.4667)
- Admission: Train IC=+0.2058, Deflated=+0.2054, IR=0.51, Mono=0.68, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.057 | 2017: +0.170 | 2018: +0.204 | 2019: +0.194 | 2020: +0.121 | 2021: +0.117 | 2022: +0.051 | 2023: +0.070 | 2024: +0.089 | 2025: +0.027 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.284 | 2016: -0.078 | 2017: +0.368 | 2018: +0.348 | 2019: +0.099 | 2020: +0.205 | 2021: +0.181 | 2022: +0.060 | 2023: +0.249 | 2024: +0.164 | 2025: -0.037 | 2026: +0.072
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=1.06, Recency ratio=0.64
- Early IC=+0.1857, Recent IC=+0.1190, 1st-half IC=+0.1466, 2nd-half IC=+0.1560, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.037, Q3_mid=+0.151, Q4=+0.129, Q5_high_vol=+0.278

**`combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0834, Sharpe=+0.4637)
- Admission: Train IC=+0.2746, Deflated=+0.2739, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.075 | 2017: +0.196 | 2018: +0.209 | 2019: +0.089 | 2020: +0.114 | 2021: +0.107 | 2022: +0.103 | 2023: +0.100 | 2024: +0.128 | 2025: +0.109 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.110 | 2017: +0.291 | 2018: +0.399 | 2019: +0.117 | 2020: +0.192 | 2021: +0.196 | 2022: +0.166 | 2023: +0.306 | 2024: +0.244 | 2025: -0.052 | 2026: -0.238
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.52
- Early IC=+0.2136, Recent IC=+0.1106, 1st-half IC=+0.1899, 2nd-half IC=+0.1291, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.006, Q3_mid=+0.193, Q4=+0.183, Q5_high_vol=+0.205

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0900, Sharpe=+0.4628)
- Admission: Train IC=+0.3158, Deflated=+0.3151, IR=1.06, Mono=0.85, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.100 | 2017: +0.208 | 2018: +0.220 | 2019: +0.146 | 2020: +0.155 | 2021: +0.125 | 2022: +0.060 | 2023: +0.119 | 2024: +0.156 | 2025: +0.095 | 2026: -0.040
- Yearly Tail ICs:   2015: +0.523 | 2016: +0.309 | 2017: +0.348 | 2018: +0.386 | 2019: +0.196 | 2020: +0.211 | 2021: +0.271 | 2022: +0.160 | 2023: +0.226 | 2024: +0.207 | 2025: -0.140 | 2026: -0.065
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.59
- Early IC=+0.2360, Recent IC=+0.1400, 1st-half IC=+0.2089, 2nd-half IC=+0.1583, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.081, Q3_mid=+0.217, Q4=+0.172, Q5_high_vol=+0.254

**`combo_mean__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0841, Sharpe=+0.4615)
- Admission: Train IC=+0.2585, Deflated=+0.2573, IR=0.74, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.091 | 2017: +0.234 | 2018: +0.257 | 2019: +0.155 | 2020: +0.157 | 2021: +0.134 | 2022: +0.084 | 2023: +0.090 | 2024: +0.152 | 2025: +0.090 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.265 | 2016: -0.003 | 2017: +0.219 | 2018: +0.456 | 2019: +0.157 | 2020: +0.230 | 2021: +0.302 | 2022: +0.205 | 2023: +0.161 | 2024: +0.225 | 2025: +0.049 | 2026: -0.235
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.63
- Early IC=+0.2309, Recent IC=+0.1456, 1st-half IC=+0.2062, 2nd-half IC=+0.1719, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.056, Q3_mid=+0.200, Q4=+0.204, Q5_high_vol=+0.252

**`combo_min__max_up_ret__first_bar_return`** (Lock IC=+0.0745, Sharpe=+0.4517)
- Admission: Train IC=+0.2359, Deflated=+0.2347, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.098 | 2017: +0.204 | 2018: +0.231 | 2019: +0.137 | 2020: +0.122 | 2021: +0.098 | 2022: +0.086 | 2023: +0.093 | 2024: +0.103 | 2025: +0.079 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.043 | 2017: +0.173 | 2018: +0.450 | 2019: +0.149 | 2020: +0.182 | 2021: +0.151 | 2022: +0.111 | 2023: +0.155 | 2024: +0.173 | 2025: +0.005 | 2026: -0.188
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.48
- Early IC=+0.2293, Recent IC=+0.1102, 1st-half IC=+0.2128, 2nd-half IC=+0.1433, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.046, Q3_mid=+0.196, Q4=+0.169, Q5_high_vol=+0.233

**`combo_min__bar_ret_0__close_vs_open_range`** (Lock IC=+0.0802, Sharpe=+0.4484)
- Admission: Train IC=+0.2497, Deflated=+0.2486, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.082 | 2017: +0.184 | 2018: +0.173 | 2019: +0.119 | 2020: +0.064 | 2021: +0.057 | 2022: +0.044 | 2023: +0.068 | 2024: +0.126 | 2025: +0.138 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.456 | 2016: +0.114 | 2017: +0.255 | 2018: +0.268 | 2019: +0.228 | 2020: +0.075 | 2021: +0.274 | 2022: +0.166 | 2023: +0.139 | 2024: +0.196 | 2025: +0.169 | 2026: +0.221
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.32
- Early IC=+0.1866, Recent IC=+0.0604, 1st-half IC=+0.1550, 2nd-half IC=+0.1039, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.020, Q3_mid=+0.118, Q4=+0.184, Q5_high_vol=+0.163

**`combo_diff__close_vs_open_range__h2_l2_pullback_continuation`** (Lock IC=+0.0780, Sharpe=+0.4468)
- Admission: Train IC=+0.1917, Deflated=+0.1914, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.147 | 2016: +0.090 | 2017: +0.154 | 2018: +0.062 | 2019: +0.048 | 2020: +0.081 | 2021: +0.037 | 2022: +0.090 | 2023: +0.099 | 2024: +0.110 | 2025: +0.118 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.315 | 2016: +0.201 | 2017: +0.239 | 2018: +0.178 | 2019: +0.198 | 2020: +0.039 | 2021: +0.171 | 2022: +0.119 | 2023: +0.202 | 2024: +0.330 | 2025: -0.057 | 2026: +0.096
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.47, Recency ratio=0.43
- Early IC=+0.1386, Recent IC=+0.0590, 1st-half IC=+0.1341, 2nd-half IC=+0.0630, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.160, Q2=-0.021, Q3_mid=+0.155, Q4=+0.144, Q5_high_vol=+0.075

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0866, Sharpe=+0.4367)
- Admission: Train IC=+0.2723, Deflated=+0.2713, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.094 | 2017: +0.252 | 2018: +0.191 | 2019: +0.114 | 2020: +0.161 | 2021: +0.116 | 2022: +0.106 | 2023: +0.073 | 2024: +0.143 | 2025: +0.075 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.235 | 2016: +0.195 | 2017: +0.134 | 2018: +0.372 | 2019: +0.217 | 2020: +0.158 | 2021: +0.219 | 2022: +0.133 | 2023: +0.114 | 2024: +0.253 | 2025: -0.030 | 2026: -0.279
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.56
- Early IC=+0.2459, Recent IC=+0.1384, 1st-half IC=+0.2237, 2nd-half IC=+0.1432, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.222, Q2=+0.035, Q3_mid=+0.222, Q4=+0.208, Q5_high_vol=+0.244

**`combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0839, Sharpe=+0.4360)
- Admission: Train IC=+0.2672, Deflated=+0.2666, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.038 | 2017: +0.202 | 2018: +0.197 | 2019: +0.180 | 2020: +0.175 | 2021: +0.119 | 2022: +0.055 | 2023: +0.101 | 2024: +0.120 | 2025: +0.049 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.397 | 2016: +0.129 | 2017: +0.277 | 2018: +0.253 | 2019: +0.502 | 2020: +0.205 | 2021: +0.099 | 2022: +0.250 | 2023: +0.063 | 2024: +0.316 | 2025: +0.144 | 2026: -0.044
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=0.70
- Early IC=+0.2093, Recent IC=+0.1470, 1st-half IC=+0.1605, 2nd-half IC=+0.1654, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.065, Q3_mid=+0.178, Q4=+0.149, Q5_high_vol=+0.281

**`combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early`** (Lock IC=+0.0902, Sharpe=+0.4330)
- Admission: Train IC=+0.3173, Deflated=+0.3162, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.056 | 2017: +0.213 | 2018: +0.133 | 2019: +0.093 | 2020: +0.114 | 2021: +0.099 | 2022: +0.022 | 2023: +0.084 | 2024: +0.145 | 2025: +0.103 | 2026: +0.055
- Yearly Tail ICs:   2015: +0.317 | 2016: +0.133 | 2017: +0.410 | 2018: +0.373 | 2019: +0.210 | 2020: +0.257 | 2021: +0.163 | 2022: +0.342 | 2023: -0.167 | 2024: +0.287 | 2025: -0.027 | 2026: +0.165
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.51
- Early IC=+0.2069, Recent IC=+0.1065, 1st-half IC=+0.1689, 2nd-half IC=+0.1160, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.042, Q3_mid=+0.144, Q4=+0.196, Q5_high_vol=+0.155

**`combo_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction`** (Lock IC=+0.0772, Sharpe=+0.4324)
- Admission: Train IC=+0.2538, Deflated=+0.2530, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.056 | 2017: +0.258 | 2018: +0.154 | 2019: +0.071 | 2020: +0.185 | 2021: +0.099 | 2022: +0.055 | 2023: +0.075 | 2024: +0.105 | 2025: +0.145 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.151 | 2017: +0.307 | 2018: +0.212 | 2019: +0.076 | 2020: +0.192 | 2021: +0.236 | 2022: +0.304 | 2023: -0.084 | 2024: +0.236 | 2025: +0.135 | 2026: -0.102
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.64
- Early IC=+0.2212, Recent IC=+0.1421, 1st-half IC=+0.1977, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.036, Q3_mid=+0.210, Q4=+0.209, Q5_high_vol=+0.186

**`combo_rank_min__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0724, Sharpe=+0.4316)
- Admission: Train IC=+0.2651, Deflated=+0.2642, IR=0.69, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.045 | 2017: +0.156 | 2018: +0.171 | 2019: +0.101 | 2020: +0.037 | 2021: +0.062 | 2022: +0.066 | 2023: +0.062 | 2024: +0.112 | 2025: +0.116 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.429 | 2016: +0.008 | 2017: +0.317 | 2018: +0.397 | 2019: +0.113 | 2020: +0.056 | 2021: +0.249 | 2022: +0.293 | 2023: -0.003 | 2024: +0.322 | 2025: +0.094 | 2026: +0.128
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.28
- Early IC=+0.1788, Recent IC=+0.0501, 1st-half IC=+0.1340, 2nd-half IC=+0.0955, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.198, Q2=-0.036, Q3_mid=+0.113, Q4=+0.179, Q5_high_vol=+0.132

**`combo_mean__first_bar_return__vwap_close_divergence_trend`** (Lock IC=+0.0833, Sharpe=+0.4299)
- Admission: Train IC=+0.2252, Deflated=+0.2243, IR=0.58, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.065 | 2017: +0.222 | 2018: +0.184 | 2019: +0.129 | 2020: +0.107 | 2021: +0.123 | 2022: +0.092 | 2023: +0.090 | 2024: +0.130 | 2025: +0.132 | 2026: -0.090
- Yearly Tail ICs:   2015: +0.227 | 2016: +0.039 | 2017: +0.154 | 2018: +0.398 | 2019: +0.220 | 2020: +0.088 | 2021: +0.287 | 2022: +0.238 | 2023: +0.278 | 2024: +0.154 | 2025: +0.189 | 2026: -0.187
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.62
- Early IC=+0.1856, Recent IC=+0.1150, 1st-half IC=+0.1749, 2nd-half IC=+0.1355, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.219, Q2=+0.019, Q3_mid=+0.185, Q4=+0.179, Q5_high_vol=+0.166

**`combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__trend_day_regime_conviction`** (Lock IC=+0.0872, Sharpe=+0.4294)
- Admission: Train IC=+0.2293, Deflated=+0.2286, IR=0.63, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.050 | 2017: +0.182 | 2018: +0.129 | 2019: +0.083 | 2020: +0.100 | 2021: +0.077 | 2022: +0.105 | 2023: +0.088 | 2024: +0.116 | 2025: +0.136 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.303 | 2016: +0.144 | 2017: +0.174 | 2018: +0.159 | 2019: +0.260 | 2020: +0.157 | 2021: +0.195 | 2022: +0.271 | 2023: +0.156 | 2024: +0.210 | 2025: -0.002 | 2026: -0.056
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.47
- Early IC=+0.1864, Recent IC=+0.0884, 1st-half IC=+0.1556, 2nd-half IC=+0.0983, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.198, Q2=-0.001, Q3_mid=+0.182, Q4=+0.172, Q5_high_vol=+0.113

**`combo_rank_min__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0864, Sharpe=+0.4279)
- Admission: Train IC=+0.2462, Deflated=+0.2455, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.069 | 2017: +0.241 | 2018: +0.095 | 2019: +0.122 | 2020: +0.124 | 2021: +0.038 | 2022: +0.090 | 2023: +0.074 | 2024: +0.114 | 2025: +0.102 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.318 | 2016: +0.073 | 2017: +0.322 | 2018: +0.162 | 2019: +0.238 | 2020: +0.140 | 2021: +0.360 | 2022: +0.349 | 2023: +0.079 | 2024: +0.083 | 2025: +0.235 | 2026: -0.143
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.43
- Early IC=+0.1894, Recent IC=+0.0812, 1st-half IC=+0.1592, 2nd-half IC=+0.0992, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.021, Q3_mid=+0.143, Q4=+0.164, Q5_high_vol=+0.175

**`combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1106, Sharpe=+0.4239)
- Admission: Train IC=+0.2485, Deflated=+0.2485, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.119 | 2017: +0.121 | 2018: +0.159 | 2019: +0.097 | 2020: +0.096 | 2021: +0.025 | 2022: +0.155 | 2023: +0.090 | 2024: +0.103 | 2025: +0.094 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.056 | 2016: +0.374 | 2017: +0.217 | 2018: +0.139 | 2019: +0.181 | 2020: +0.124 | 2021: +0.106 | 2022: +0.169 | 2023: +0.128 | 2024: +0.236 | 2025: +0.005 | 2026: -0.241
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.47, Recency ratio=0.24
- Early IC=+0.2586, Recent IC=+0.0624, 1st-half IC=+0.2134, 2nd-half IC=+0.1008, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.042, Q3_mid=+0.214, Q4=+0.123, Q5_high_vol=+0.235

**`combo_mean__max_down_ret__close_vs_open_range`** (Lock IC=+0.0867, Sharpe=+0.4222)
- Admission: Train IC=+0.1754, Deflated=+0.1742, IR=0.49, Mono=0.65, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.073 | 2017: +0.212 | 2018: +0.128 | 2019: +0.091 | 2020: +0.130 | 2021: +0.064 | 2022: +0.076 | 2023: +0.069 | 2024: +0.130 | 2025: +0.131 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.300 | 2016: -0.077 | 2017: +0.254 | 2018: +0.091 | 2019: +0.249 | 2020: +0.108 | 2021: +0.333 | 2022: +0.251 | 2023: +0.136 | 2024: +0.382 | 2025: -0.000 | 2026: -0.043
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.62, Recency ratio=0.48
- Early IC=+0.2031, Recent IC=+0.0968, 1st-half IC=+0.1643, 2nd-half IC=+0.1018, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.216, Q2=-0.017, Q3_mid=+0.142, Q4=+0.174, Q5_high_vol=+0.176

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__opening_auction_imbalance`** (Lock IC=+0.0899, Sharpe=+0.4218)
- Admission: Train IC=+0.2812, Deflated=+0.2809, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.069 | 2017: +0.179 | 2018: +0.196 | 2019: +0.136 | 2020: +0.143 | 2021: +0.137 | 2022: +0.086 | 2023: +0.127 | 2024: +0.146 | 2025: +0.110 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.358 | 2016: +0.118 | 2017: +0.328 | 2018: +0.332 | 2019: +0.258 | 2020: +0.230 | 2021: +0.217 | 2022: +0.171 | 2023: +0.314 | 2024: +0.245 | 2025: -0.119 | 2026: -0.028
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.71
- Early IC=+0.1983, Recent IC=+0.1399, 1st-half IC=+0.1717, 2nd-half IC=+0.1507, Neg regimes=0/5
- Weak component: `opening_auction_imbalance` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.043, Q3_mid=+0.224, Q4=+0.170, Q5_high_vol=+0.181

**`combo_min__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0907, Sharpe=+0.4217)
- Admission: Train IC=+0.2434, Deflated=+0.2427, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.056 | 2017: +0.212 | 2018: +0.079 | 2019: +0.116 | 2020: +0.114 | 2021: +0.036 | 2022: +0.101 | 2023: +0.091 | 2024: +0.118 | 2025: +0.104 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.058 | 2017: +0.299 | 2018: +0.177 | 2019: +0.259 | 2020: +0.146 | 2021: +0.306 | 2022: +0.316 | 2023: +0.108 | 2024: +0.140 | 2025: +0.311 | 2026: -0.009
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.42
- Early IC=+0.1803, Recent IC=+0.0752, 1st-half IC=+0.1517, 2nd-half IC=+0.0936, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.022, Q3_mid=+0.134, Q4=+0.155, Q5_high_vol=+0.168

**`combo_rank_min__bar_ret_0__close_vs_open_range`** (Lock IC=+0.0786, Sharpe=+0.4206)
- Admission: Train IC=+0.2527, Deflated=+0.2517, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.081 | 2017: +0.184 | 2018: +0.173 | 2019: +0.117 | 2020: +0.063 | 2021: +0.055 | 2022: +0.043 | 2023: +0.068 | 2024: +0.123 | 2025: +0.138 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.448 | 2016: +0.133 | 2017: +0.247 | 2018: +0.283 | 2019: +0.223 | 2020: +0.076 | 2021: +0.272 | 2022: +0.156 | 2023: +0.136 | 2024: +0.197 | 2025: +0.191 | 2026: +0.232
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.31
- Early IC=+0.1919, Recent IC=+0.0586, 1st-half IC=+0.1564, 2nd-half IC=+0.1031, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.021, Q3_mid=+0.119, Q4=+0.189, Q5_high_vol=+0.162

**`combo_rank_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0942, Sharpe=+0.4160)
- Admission: Train IC=+0.2344, Deflated=+0.2341, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.103 | 2017: +0.202 | 2018: +0.169 | 2019: +0.100 | 2020: +0.139 | 2021: +0.092 | 2022: +0.121 | 2023: +0.128 | 2024: +0.133 | 2025: +0.095 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.272 | 2016: +0.136 | 2017: +0.159 | 2018: +0.289 | 2019: +0.206 | 2020: +0.112 | 2021: +0.111 | 2022: +0.117 | 2023: +0.413 | 2024: +0.212 | 2025: -0.160 | 2026: -0.324
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.59
- Early IC=+0.2014, Recent IC=+0.1196, 1st-half IC=+0.1949, 2nd-half IC=+0.1291, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.069, Q3_mid=+0.198, Q4=+0.146, Q5_high_vol=+0.212

**`combo_max__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.0955, Sharpe=+0.4146)
- Admission: Train IC=+0.2059, Deflated=+0.2060, IR=0.49, Mono=0.66, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.062 | 2017: +0.119 | 2018: +0.151 | 2019: +0.083 | 2020: +0.083 | 2021: +0.033 | 2022: +0.112 | 2023: +0.069 | 2024: +0.098 | 2025: +0.103 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.189 | 2017: +0.139 | 2018: +0.161 | 2019: +0.211 | 2020: +0.060 | 2021: +0.193 | 2022: +0.168 | 2023: +0.100 | 2024: +0.141 | 2025: +0.048 | 2026: -0.210
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.24
- Early IC=+0.2475, Recent IC=+0.0583, 1st-half IC=+0.1872, 2nd-half IC=+0.0932, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.044, Q3_mid=+0.192, Q4=+0.117, Q5_high_vol=+0.182

**`combo_rank_min__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0890, Sharpe=+0.4128)
- Admission: Train IC=+0.2125, Deflated=+0.2115, IR=0.61, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.077 | 2017: +0.235 | 2018: +0.132 | 2019: +0.096 | 2020: +0.142 | 2021: +0.053 | 2022: +0.084 | 2023: +0.081 | 2024: +0.112 | 2025: +0.135 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.285 | 2016: -0.076 | 2017: +0.295 | 2018: +0.113 | 2019: +0.262 | 2020: +0.207 | 2021: +0.347 | 2022: +0.282 | 2023: +0.269 | 2024: +0.136 | 2025: +0.160 | 2026: -0.026
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.47
- Early IC=+0.2152, Recent IC=+0.1002, 1st-half IC=+0.1694, 2nd-half IC=+0.1084, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.220, Q2=-0.012, Q3_mid=+0.135, Q4=+0.179, Q5_high_vol=+0.194

**`combo_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0820, Sharpe=+0.4112)
- Admission: Train IC=+0.2797, Deflated=+0.2794, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.097 | 2017: +0.166 | 2018: +0.119 | 2019: +0.082 | 2020: +0.118 | 2021: +0.059 | 2022: +0.112 | 2023: +0.115 | 2024: +0.131 | 2025: +0.088 | 2026: -0.089
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.320 | 2017: +0.126 | 2018: +0.284 | 2019: +0.160 | 2020: +0.103 | 2021: +0.245 | 2022: +0.162 | 2023: +0.276 | 2024: +0.260 | 2025: -0.179 | 2026: -0.081
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.51
- Early IC=+0.1735, Recent IC=+0.0888, 1st-half IC=+0.1742, 2nd-half IC=+0.1004, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.001, Q3_mid=+0.207, Q4=+0.163, Q5_high_vol=+0.165

**`combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1032, Sharpe=+0.4100)
- Admission: Train IC=+0.2808, Deflated=+0.2796, IR=0.84, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.292 | 2016: +0.088 | 2017: +0.244 | 2018: +0.174 | 2019: +0.147 | 2020: +0.179 | 2021: +0.116 | 2022: +0.068 | 2023: +0.074 | 2024: +0.138 | 2025: +0.092 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.163 | 2016: +0.200 | 2017: +0.186 | 2018: +0.276 | 2019: +0.396 | 2020: +0.146 | 2021: +0.157 | 2022: +0.071 | 2023: -0.085 | 2024: +0.207 | 2025: -0.056 | 2026: +0.072
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.56
- Early IC=+0.2622, Recent IC=+0.1477, 1st-half IC=+0.2292, 2nd-half IC=+0.1587, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.090, Q3_mid=+0.193, Q4=+0.214, Q5_high_vol=+0.245

**`combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0968, Sharpe=+0.4059)
- Admission: Train IC=+0.2291, Deflated=+0.2278, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.104 | 2017: +0.223 | 2018: +0.202 | 2019: +0.112 | 2020: +0.160 | 2021: +0.112 | 2022: +0.130 | 2023: +0.079 | 2024: +0.113 | 2025: +0.069 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.201 | 2016: +0.071 | 2017: +0.116 | 2018: +0.286 | 2019: +0.100 | 2020: +0.153 | 2021: +0.247 | 2022: +0.182 | 2023: -0.092 | 2024: -0.025 | 2025: -0.063 | 2026: -0.143
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.58
- Early IC=+0.2325, Recent IC=+0.1356, 1st-half IC=+0.2161, 2nd-half IC=+0.1468, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.211, Q2=+0.060, Q3_mid=+0.212, Q4=+0.159, Q5_high_vol=+0.243

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1272, Sharpe=+0.4052)
- Admission: Train IC=+0.2367, Deflated=+0.2359, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.094 | 2017: +0.245 | 2018: +0.116 | 2019: +0.123 | 2020: +0.135 | 2021: +0.040 | 2022: +0.097 | 2023: +0.116 | 2024: +0.107 | 2025: +0.117 | 2026: +0.172
- Yearly Tail ICs:   2015: +0.352 | 2016: +0.063 | 2017: +0.206 | 2018: +0.280 | 2019: +0.241 | 2020: +0.253 | 2021: +0.051 | 2022: +0.125 | 2023: -0.029 | 2024: +0.171 | 2025: +0.199 | 2026: +0.159
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.34
- Early IC=+0.2539, Recent IC=+0.0876, 1st-half IC=+0.2258, 2nd-half IC=+0.1129, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.092, Q3_mid=+0.168, Q4=+0.171, Q5_high_vol=+0.199

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=+0.0821, Sharpe=+0.4042)
- Admission: Train IC=+0.2625, Deflated=+0.2615, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.110 | 2017: +0.192 | 2018: +0.243 | 2019: +0.137 | 2020: +0.112 | 2021: +0.137 | 2022: +0.101 | 2023: +0.096 | 2024: +0.141 | 2025: +0.077 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.129 | 2017: +0.266 | 2018: +0.480 | 2019: +0.117 | 2020: +0.231 | 2021: +0.284 | 2022: +0.102 | 2023: +0.139 | 2024: +0.142 | 2025: +0.048 | 2026: -0.205
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.58
- Early IC=+0.2158, Recent IC=+0.1241, 1st-half IC=+0.2061, 2nd-half IC=+0.1525, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.034, Q3_mid=+0.197, Q4=+0.178, Q5_high_vol=+0.255

**`combo_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0938, Sharpe=+0.4037)
- Admission: Train IC=+0.2358, Deflated=+0.2349, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.087 | 2017: +0.183 | 2018: +0.123 | 2019: +0.074 | 2020: +0.110 | 2021: +0.128 | 2022: +0.089 | 2023: +0.101 | 2024: +0.146 | 2025: +0.151 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.331 | 2016: +0.261 | 2017: +0.305 | 2018: +0.273 | 2019: +0.092 | 2020: +0.091 | 2021: +0.228 | 2022: +0.080 | 2023: +0.181 | 2024: +0.244 | 2025: +0.099 | 2026: -0.140
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.68
- Early IC=+0.1737, Recent IC=+0.1187, 1st-half IC=+0.1668, 2nd-half IC=+0.1019, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.037, Q3_mid=+0.188, Q4=+0.155, Q5_high_vol=+0.129

**`combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance`** (Lock IC=+0.0873, Sharpe=+0.3999)
- Admission: Train IC=+0.2695, Deflated=+0.2688, IR=0.78, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.011 | 2017: +0.192 | 2018: +0.165 | 2019: +0.143 | 2020: +0.115 | 2021: +0.146 | 2022: +0.115 | 2023: +0.092 | 2024: +0.139 | 2025: +0.107 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.376 | 2016: +0.091 | 2017: +0.188 | 2018: +0.278 | 2019: +0.426 | 2020: +0.108 | 2021: +0.321 | 2022: +0.344 | 2023: +0.234 | 2024: +0.372 | 2025: -0.049 | 2026: -0.233
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.60
- Early IC=+0.2162, Recent IC=+0.1305, 1st-half IC=+0.1608, 2nd-half IC=+0.1412, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.028, Q3_mid=+0.188, Q4=+0.200, Q5_high_vol=+0.160

**`combo_min__close_vs_open_range__vwap_close_divergence_trend`** (Lock IC=+0.0924, Sharpe=+0.3978)
- Admission: Train IC=+0.2072, Deflated=+0.2066, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.056 | 2017: +0.188 | 2018: +0.081 | 2019: +0.075 | 2020: +0.092 | 2021: +0.073 | 2022: +0.100 | 2023: +0.117 | 2024: +0.115 | 2025: +0.146 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.152 | 2017: +0.285 | 2018: +0.172 | 2019: +0.281 | 2020: +0.125 | 2021: +0.313 | 2022: +0.125 | 2023: +0.228 | 2024: +0.170 | 2025: +0.106 | 2026: -0.227
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.59
- Early IC=+0.1402, Recent IC=+0.0823, 1st-half IC=+0.1340, 2nd-half IC=+0.0850, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.003, Q3_mid=+0.145, Q4=+0.157, Q5_high_vol=+0.094

**`combo_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0919, Sharpe=+0.3974)
- Admission: Train IC=+0.2351, Deflated=+0.2348, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.106 | 2017: +0.197 | 2018: +0.166 | 2019: +0.101 | 2020: +0.131 | 2021: +0.088 | 2022: +0.125 | 2023: +0.121 | 2024: +0.127 | 2025: +0.091 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.263 | 2016: +0.152 | 2017: +0.151 | 2018: +0.302 | 2019: +0.206 | 2020: +0.095 | 2021: +0.213 | 2022: +0.106 | 2023: +0.414 | 2024: +0.207 | 2025: -0.167 | 2026: -0.367
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.57
- Early IC=+0.1930, Recent IC=+0.1094, 1st-half IC=+0.1913, 2nd-half IC=+0.1254, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.064, Q3_mid=+0.183, Q4=+0.148, Q5_high_vol=+0.211

**`combo_rel_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0863, Sharpe=+0.3938)
- Admission: Train IC=+0.2870, Deflated=+0.2870, IR=0.89, Mono=0.80, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.116 | 2017: +0.158 | 2018: +0.126 | 2019: +0.071 | 2020: +0.111 | 2021: +0.058 | 2022: +0.123 | 2023: +0.105 | 2024: +0.126 | 2025: +0.093 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.330 | 2017: +0.132 | 2018: +0.285 | 2019: +0.157 | 2020: +0.073 | 2021: +0.262 | 2022: +0.150 | 2023: +0.292 | 2024: +0.254 | 2025: -0.171 | 2026: -0.073
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.49
- Early IC=+0.1737, Recent IC=+0.0843, 1st-half IC=+0.1779, 2nd-half IC=+0.0975, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.001, Q3_mid=+0.196, Q4=+0.156, Q5_high_vol=+0.167

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.1006, Sharpe=+0.3931)
- Admission: Train IC=+0.3230, Deflated=+0.3224, IR=0.96, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.139 | 2017: +0.218 | 2018: +0.252 | 2019: +0.142 | 2020: +0.163 | 2021: +0.124 | 2022: +0.103 | 2023: +0.083 | 2024: +0.116 | 2025: +0.106 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.204 | 2017: +0.166 | 2018: +0.455 | 2019: +0.177 | 2020: +0.249 | 2021: +0.229 | 2022: +0.122 | 2023: +0.043 | 2024: +0.102 | 2025: +0.046 | 2026: +0.075
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.56
- Early IC=+0.2575, Recent IC=+0.1434, 1st-half IC=+0.2390, 2nd-half IC=+0.1698, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.225, Q2=+0.070, Q3_mid=+0.208, Q4=+0.201, Q5_high_vol=+0.290

**`combo_tri_median__opening_auction_imbalance__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0860, Sharpe=+0.3894)
- Admission: Train IC=+0.2656, Deflated=+0.2649, IR=0.87, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.098 | 2017: +0.203 | 2018: +0.242 | 2019: +0.145 | 2020: +0.118 | 2021: +0.069 | 2022: +0.075 | 2023: +0.082 | 2024: +0.123 | 2025: +0.150 | 2026: -0.026
- Yearly Tail ICs:   2015: +0.354 | 2016: +0.150 | 2017: +0.282 | 2018: +0.371 | 2019: +0.268 | 2020: +0.172 | 2021: +0.121 | 2022: +0.080 | 2023: +0.218 | 2024: +0.292 | 2025: +0.051 | 2026: +0.059
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.43
- Early IC=+0.2190, Recent IC=+0.0933, 1st-half IC=+0.1928, 2nd-half IC=+0.1447, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.028, Q3_mid=+0.187, Q4=+0.177, Q5_high_vol=+0.212

**`combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0713, Sharpe=+0.3891)
- Admission: Train IC=+0.2673, Deflated=+0.2672, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.055 | 2017: +0.175 | 2018: +0.094 | 2019: +0.054 | 2020: +0.118 | 2021: +0.016 | 2022: +0.009 | 2023: +0.068 | 2024: +0.056 | 2025: +0.110 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.168 | 2017: +0.265 | 2018: +0.321 | 2019: +0.242 | 2020: +0.240 | 2021: +0.042 | 2022: +0.163 | 2023: -0.130 | 2024: +0.160 | 2025: +0.180 | 2026: +0.128
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.43, Recency ratio=0.31
- Early IC=+0.2151, Recent IC=+0.0671, 1st-half IC=+0.1794, 2nd-half IC=+0.0780, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.008, Q3_mid=+0.149, Q4=+0.185, Q5_high_vol=+0.142

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0899, Sharpe=+0.3887)
- Admission: Train IC=+0.2765, Deflated=+0.2756, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.082 | 2017: +0.182 | 2018: +0.136 | 2019: +0.081 | 2020: +0.112 | 2021: +0.134 | 2022: +0.091 | 2023: +0.093 | 2024: +0.144 | 2025: +0.143 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.364 | 2016: +0.130 | 2017: +0.272 | 2018: +0.256 | 2019: +0.307 | 2020: +0.134 | 2021: +0.264 | 2022: +0.098 | 2023: +0.099 | 2024: +0.279 | 2025: +0.078 | 2026: -0.157
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.68
- Early IC=+0.1802, Recent IC=+0.1230, 1st-half IC=+0.1689, 2nd-half IC=+0.1104, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.034, Q3_mid=+0.197, Q4=+0.165, Q5_high_vol=+0.123

**`combo_min__max_down_ret__bar_body_rng_0`** (Lock IC=+0.0695, Sharpe=+0.3857)
- Admission: Train IC=+0.2192, Deflated=+0.2185, IR=0.63, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.070 | 2017: +0.204 | 2018: +0.179 | 2019: +0.132 | 2020: +0.094 | 2021: +0.110 | 2022: +0.047 | 2023: +0.057 | 2024: +0.109 | 2025: +0.124 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.272 | 2016: -0.092 | 2017: +0.127 | 2018: +0.192 | 2019: +0.419 | 2020: +0.141 | 2021: +0.289 | 2022: +0.079 | 2023: +0.099 | 2024: +0.335 | 2025: +0.232 | 2026: +0.017
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.76, Recency ratio=0.45
- Early IC=+0.2266, Recent IC=+0.1020, 1st-half IC=+0.1658, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.001, Q3_mid=+0.154, Q4=+0.172, Q5_high_vol=+0.220

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0884, Sharpe=+0.3821)
- Admission: Train IC=+0.2675, Deflated=+0.2664, IR=0.83, Mono=0.81, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.108 | 2017: +0.226 | 2018: +0.255 | 2019: +0.124 | 2020: +0.162 | 2021: +0.173 | 2022: +0.111 | 2023: +0.095 | 2024: +0.146 | 2025: +0.099 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.170 | 2017: +0.166 | 2018: +0.473 | 2019: +0.154 | 2020: +0.284 | 2021: +0.339 | 2022: +0.189 | 2023: +0.047 | 2024: +0.256 | 2025: +0.006 | 2026: -0.297
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.74
- Early IC=+0.2258, Recent IC=+0.1677, 1st-half IC=+0.2124, 2nd-half IC=+0.1733, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.037, Q3_mid=+0.227, Q4=+0.216, Q5_high_vol=+0.253

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0965, Sharpe=+0.3807)
- Admission: Train IC=+0.2756, Deflated=+0.2745, IR=0.85, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.094 | 2017: +0.235 | 2018: +0.223 | 2019: +0.107 | 2020: +0.153 | 2021: +0.154 | 2022: +0.123 | 2023: +0.097 | 2024: +0.144 | 2025: +0.078 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.265 | 2016: +0.101 | 2017: +0.148 | 2018: +0.366 | 2019: +0.318 | 2020: +0.099 | 2021: +0.322 | 2022: +0.212 | 2023: -0.010 | 2024: +0.270 | 2025: +0.026 | 2026: -0.154
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.63
- Early IC=+0.2398, Recent IC=+0.1507, 1st-half IC=+0.2177, 2nd-half IC=+0.1542, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.062, Q3_mid=+0.231, Q4=+0.203, Q5_high_vol=+0.246

**`combo_mean__first_bar_return__rsi_opening`** (Lock IC=+0.0824, Sharpe=+0.3778)
- Admission: Train IC=+0.2514, Deflated=+0.2503, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.079 | 2017: +0.219 | 2018: +0.201 | 2019: +0.105 | 2020: +0.110 | 2021: +0.092 | 2022: +0.096 | 2023: +0.075 | 2024: +0.141 | 2025: +0.116 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.272 | 2016: -0.016 | 2017: +0.207 | 2018: +0.383 | 2019: +0.211 | 2020: +0.233 | 2021: +0.147 | 2022: +0.296 | 2023: +0.221 | 2024: +0.229 | 2025: +0.161 | 2026: -0.262
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.52
- Early IC=+0.1950, Recent IC=+0.1008, 1st-half IC=+0.1764, 2nd-half IC=+0.1257, Neg regimes=0/5
- Weak component: `rsi_opening` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.227, Q2=+0.007, Q3_mid=+0.161, Q4=+0.183, Q5_high_vol=+0.173

**`combo_rank_min__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0829, Sharpe=+0.3757)
- Admission: Train IC=+0.2183, Deflated=+0.2180, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.037 | 2017: +0.161 | 2018: +0.111 | 2019: +0.122 | 2020: +0.102 | 2021: +0.105 | 2022: +0.144 | 2023: +0.079 | 2024: +0.114 | 2025: +0.068 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.080 | 2017: +0.187 | 2018: +0.158 | 2019: +0.247 | 2020: +0.142 | 2021: +0.284 | 2022: +0.305 | 2023: +0.053 | 2024: +0.329 | 2025: +0.114 | 2026: -0.055
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.50
- Early IC=+0.2089, Recent IC=+0.1035, 1st-half IC=+0.1321, 2nd-half IC=+0.1117, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.147, Q2=-0.028, Q3_mid=+0.120, Q4=+0.190, Q5_high_vol=+0.171

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1235, Sharpe=+0.3726)
- Admission: Train IC=+0.2636, Deflated=+0.2629, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.109 | 2017: +0.248 | 2018: +0.122 | 2019: +0.125 | 2020: +0.132 | 2021: +0.046 | 2022: +0.092 | 2023: +0.111 | 2024: +0.108 | 2025: +0.111 | 2026: +0.161
- Yearly Tail ICs:   2015: +0.148 | 2016: +0.267 | 2017: +0.260 | 2018: +0.325 | 2019: +0.148 | 2020: +0.244 | 2021: +0.078 | 2022: -0.008 | 2023: -0.053 | 2024: +0.141 | 2025: +0.026 | 2026: +0.231
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.35
- Early IC=+0.2564, Recent IC=+0.0889, 1st-half IC=+0.2341, 2nd-half IC=+0.1148, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.104, Q3_mid=+0.174, Q4=+0.171, Q5_high_vol=+0.197

**`combo_tri_max__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early`** (Lock IC=+0.0869, Sharpe=+0.3667)
- Admission: Train IC=+0.2068, Deflated=+0.2064, IR=0.45, Mono=0.66, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.078 | 2017: +0.225 | 2018: +0.121 | 2019: +0.074 | 2020: +0.156 | 2021: +0.063 | 2022: +0.131 | 2023: +0.050 | 2024: +0.093 | 2025: +0.107 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.186 | 2016: +0.257 | 2017: +0.155 | 2018: +0.055 | 2019: +0.124 | 2020: +0.132 | 2021: +0.170 | 2022: +0.172 | 2023: +0.050 | 2024: +0.146 | 2025: +0.017 | 2026: -0.331
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.43
- Early IC=+0.2555, Recent IC=+0.1095, 1st-half IC=+0.2241, 2nd-half IC=+0.1088, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.038, Q3_mid=+0.202, Q4=+0.146, Q5_high_vol=+0.230

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0701, Sharpe=+0.3666)
- Admission: Train IC=+0.2297, Deflated=+0.2282, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.097 | 2017: +0.264 | 2018: +0.229 | 2019: +0.145 | 2020: +0.131 | 2021: +0.082 | 2022: +0.087 | 2023: +0.045 | 2024: +0.128 | 2025: +0.106 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.252 | 2016: -0.006 | 2017: +0.215 | 2018: +0.419 | 2019: +0.116 | 2020: +0.224 | 2021: +0.192 | 2022: +0.201 | 2023: +0.208 | 2024: +0.225 | 2025: +0.038 | 2026: -0.232
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.56
- Early IC=+0.1906, Recent IC=+0.1063, 1st-half IC=+0.1843, 2nd-half IC=+0.1432, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.025, Q3_mid=+0.163, Q4=+0.167, Q5_high_vol=+0.214

**`combo_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1251, Sharpe=+0.3604)
- Admission: Train IC=+0.2680, Deflated=+0.2673, IR=0.78, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.102 | 2017: +0.243 | 2018: +0.122 | 2019: +0.122 | 2020: +0.135 | 2021: +0.041 | 2022: +0.090 | 2023: +0.111 | 2024: +0.103 | 2025: +0.115 | 2026: +0.174
- Yearly Tail ICs:   2015: +0.153 | 2016: +0.297 | 2017: +0.266 | 2018: +0.329 | 2019: +0.150 | 2020: +0.251 | 2021: +0.074 | 2022: -0.012 | 2023: -0.044 | 2024: +0.136 | 2025: +0.030 | 2026: +0.228
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.35
- Early IC=+0.2508, Recent IC=+0.0881, 1st-half IC=+0.2279, 2nd-half IC=+0.1145, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.094, Q3_mid=+0.166, Q4=+0.176, Q5_high_vol=+0.200

**`combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0672, Sharpe=+0.3598)
- Admission: Train IC=+0.2130, Deflated=+0.2118, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.237 | 2016: -0.006 | 2017: +0.160 | 2018: +0.224 | 2019: +0.133 | 2020: +0.173 | 2021: +0.152 | 2022: +0.042 | 2023: +0.076 | 2024: +0.117 | 2025: +0.053 | 2026: +0.025
- Yearly Tail ICs:   2015: +0.287 | 2016: +0.054 | 2017: +0.217 | 2018: +0.369 | 2019: +0.215 | 2020: +0.102 | 2021: +0.297 | 2022: +0.004 | 2023: +0.278 | 2024: +0.270 | 2025: -0.020 | 2026: +0.360
- IC CV=0.46, Neg years (linear/tail)=1/0 of 8, Half ratio=1.26, Recency ratio=0.88
- Early IC=+0.1857, Recent IC=+0.1627, 1st-half IC=+0.1314, 2nd-half IC=+0.1651, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.061, Q3_mid=+0.164, Q4=+0.151, Q5_high_vol=+0.236

**`combo_sig_product__opening_drive_thrust_ratio__rsi_opening`** (Lock IC=+0.0877, Sharpe=+0.3480)
- Admission: Train IC=+0.2106, Deflated=+0.2098, IR=0.51, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.061 | 2017: +0.211 | 2018: +0.191 | 2019: +0.104 | 2020: +0.190 | 2021: +0.062 | 2022: +0.130 | 2023: +0.116 | 2024: +0.115 | 2025: +0.069 | 2026: -0.045
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.127 | 2017: +0.228 | 2018: +0.173 | 2019: +0.210 | 2020: +0.179 | 2021: -0.002 | 2022: +0.153 | 2023: +0.116 | 2024: +0.264 | 2025: -0.001 | 2026: -0.080
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=0.76
- Early IC=+0.1657, Recent IC=+0.1258, 1st-half IC=+0.1469, 2nd-half IC=+0.1392, Neg regimes=0/5
- Weak component: `rsi_opening` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.056, Q3_mid=+0.175, Q4=+0.173, Q5_high_vol=+0.149

**`first_bar_return`** (Lock IC=+0.0599, Sharpe=+0.3457)
- Admission: Train IC=+0.2137, Deflated=+0.2128, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.200
- IC CV=0.33, Neg years (linear/tail)=0/1 of 8, Half ratio=0.86, Recency ratio=0.52
- Early IC=+0.1795, Recent IC=+0.0933, 1st-half IC=+0.1658, 2nd-half IC=+0.1419, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.025, Q3_mid=+0.135, Q4=+0.157, Q5_high_vol=+0.216

**`combo_min__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0775, Sharpe=+0.3375)
- Admission: Train IC=+0.2230, Deflated=+0.2223, IR=0.62, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.053 | 2017: +0.225 | 2018: +0.164 | 2019: +0.134 | 2020: +0.083 | 2021: +0.099 | 2022: +0.052 | 2023: +0.091 | 2024: +0.099 | 2025: +0.122 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.044 | 2017: +0.158 | 2018: +0.254 | 2019: +0.378 | 2020: +0.062 | 2021: +0.233 | 2022: +0.215 | 2023: +0.249 | 2024: +0.023 | 2025: +0.377 | 2026: -0.094
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.51
- Early IC=+0.1800, Recent IC=+0.0912, 1st-half IC=+0.1518, 2nd-half IC=+0.1202, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.030, Q3_mid=+0.166, Q4=+0.194, Q5_high_vol=+0.150

**`combo_max__first_bar_return__close_vs_open_range`** (Lock IC=+0.0826, Sharpe=+0.3368)
- Admission: Train IC=+0.2347, Deflated=+0.2335, IR=0.83, Mono=0.80, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.114 | 2017: +0.213 | 2018: +0.220 | 2019: +0.103 | 2020: +0.141 | 2021: +0.126 | 2022: +0.122 | 2023: +0.086 | 2024: +0.137 | 2025: +0.122 | 2026: -0.119
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.069 | 2017: +0.248 | 2018: +0.353 | 2019: +0.150 | 2020: +0.296 | 2021: +0.256 | 2022: +0.262 | 2023: +0.324 | 2024: +0.242 | 2025: -0.107 | 2026: -0.436
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.72
- Early IC=+0.1864, Recent IC=+0.1336, 1st-half IC=+0.1838, 2nd-half IC=+0.1450, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.035, Q3_mid=+0.187, Q4=+0.170, Q5_high_vol=+0.209

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0855, Sharpe=+0.3293)
- Admission: Train IC=+0.2731, Deflated=+0.2716, IR=0.86, Mono=0.80, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.048 | 2017: +0.233 | 2018: +0.114 | 2019: +0.122 | 2020: +0.122 | 2021: +0.073 | 2022: +0.056 | 2023: +0.063 | 2024: +0.086 | 2025: +0.133 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.109 | 2017: +0.266 | 2018: +0.360 | 2019: +0.330 | 2020: +0.218 | 2021: +0.338 | 2022: +0.066 | 2023: +0.045 | 2024: +0.148 | 2025: +0.082 | 2026: +0.247
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.41
- Early IC=+0.2386, Recent IC=+0.0982, 1st-half IC=+0.1796, 2nd-half IC=+0.1042, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.048, Q3_mid=+0.114, Q4=+0.200, Q5_high_vol=+0.174

**`combo_clamp_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1249, Sharpe=+0.3282)
- Admission: Train IC=+0.2866, Deflated=+0.2858, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.085 | 2017: +0.250 | 2018: +0.184 | 2019: +0.123 | 2020: +0.176 | 2021: +0.090 | 2022: +0.116 | 2023: +0.134 | 2024: +0.123 | 2025: +0.151 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.259 | 2017: +0.250 | 2018: +0.231 | 2019: +0.199 | 2020: +0.241 | 2021: +0.212 | 2022: +0.260 | 2023: +0.216 | 2024: +0.334 | 2025: +0.205 | 2026: -0.185
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.51
- Early IC=+0.2587, Recent IC=+0.1329, 1st-half IC=+0.2333, 2nd-half IC=+0.1458, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.080, Q3_mid=+0.224, Q4=+0.185, Q5_high_vol=+0.250

**`combo_rank_min__max_up_ret__max_down_ret`** (Lock IC=+0.0865, Sharpe=+0.3251)
- Admission: Train IC=+0.2923, Deflated=+0.2910, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.302 | 2016: +0.097 | 2017: +0.217 | 2018: +0.125 | 2019: +0.095 | 2020: +0.146 | 2021: +0.090 | 2022: +0.081 | 2023: +0.091 | 2024: +0.130 | 2025: +0.122 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.465 | 2016: +0.025 | 2017: +0.267 | 2018: +0.233 | 2019: +0.298 | 2020: +0.270 | 2021: +0.283 | 2022: +0.082 | 2023: -0.015 | 2024: +0.185 | 2025: +0.123 | 2026: -0.125
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.50
- Early IC=+0.2383, Recent IC=+0.1180, 1st-half IC=+0.2043, 2nd-half IC=+0.1115, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.045, Q3_mid=+0.177, Q4=+0.159, Q5_high_vol=+0.205

**`combo_max__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0831, Sharpe=+0.3251)
- Admission: Train IC=+0.2521, Deflated=+0.2518, IR=0.91, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.057 | 2017: +0.106 | 2018: +0.198 | 2019: +0.108 | 2020: +0.096 | 2021: +0.090 | 2022: +0.130 | 2023: +0.081 | 2024: +0.122 | 2025: +0.080 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.119 | 2017: +0.076 | 2018: +0.437 | 2019: +0.138 | 2020: +0.168 | 2021: +0.351 | 2022: +0.115 | 2023: +0.115 | 2024: +0.254 | 2025: -0.010 | 2026: -0.207
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.42
- Early IC=+0.2205, Recent IC=+0.0928, 1st-half IC=+0.1652, 2nd-half IC=+0.1223, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.129, Q2=-0.009, Q3_mid=+0.161, Q4=+0.184, Q5_high_vol=+0.225

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0664, Sharpe=+0.3240)
- Admission: Train IC=+0.2412, Deflated=+0.2405, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.125 | 2017: +0.154 | 2018: +0.225 | 2019: +0.083 | 2020: +0.135 | 2021: +0.102 | 2022: +0.108 | 2023: +0.081 | 2024: +0.127 | 2025: +0.122 | 2026: -0.153
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.098 | 2017: +0.215 | 2018: +0.264 | 2019: +0.082 | 2020: +0.349 | 2021: +0.179 | 2022: +0.301 | 2023: +0.397 | 2024: +0.218 | 2025: -0.102 | 2026: -0.539
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.63
- Early IC=+0.1899, Recent IC=+0.1201, 1st-half IC=+0.1836, 2nd-half IC=+0.1349, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.039, Q3_mid=+0.196, Q4=+0.165, Q5_high_vol=+0.204

**`max_up_ret`** (Lock IC=+0.0901, Sharpe=+0.3132)
- Admission: Train IC=+0.2674, Deflated=+0.2663, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143 | 2025: +0.080 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.194 | 2017: +0.220 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.134 | 2024: +0.269 | 2025: -0.096 | 2026: -0.168
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.63
- Early IC=+0.2192, Recent IC=+0.1371, 1st-half IC=+0.2095, 2nd-half IC=+0.1385, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.058, Q3_mid=+0.231, Q4=+0.167, Q5_high_vol=+0.245

**`combo_min__max_down_ret__close_vs_open_range`** (Lock IC=+0.0921, Sharpe=+0.3111)
- Admission: Train IC=+0.2070, Deflated=+0.2060, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.075 | 2017: +0.216 | 2018: +0.115 | 2019: +0.082 | 2020: +0.123 | 2021: +0.044 | 2022: +0.087 | 2023: +0.086 | 2024: +0.117 | 2025: +0.137 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.362 | 2016: +0.000 | 2017: +0.217 | 2018: +0.145 | 2019: +0.192 | 2020: +0.132 | 2021: +0.282 | 2022: +0.310 | 2023: +0.151 | 2024: +0.196 | 2025: +0.126 | 2026: +0.060
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.40
- Early IC=+0.2091, Recent IC=+0.0832, 1st-half IC=+0.1682, 2nd-half IC=+0.0922, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.206, Q2=-0.022, Q3_mid=+0.132, Q4=+0.178, Q5_high_vol=+0.176

**`combo_mean__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0812, Sharpe=+0.3093)
- Admission: Train IC=+0.2330, Deflated=+0.2324, IR=0.64, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.097 | 2017: +0.201 | 2018: +0.177 | 2019: +0.140 | 2020: +0.096 | 2021: +0.128 | 2022: +0.076 | 2023: +0.095 | 2024: +0.107 | 2025: +0.154 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.226 | 2016: +0.068 | 2017: +0.144 | 2018: +0.382 | 2019: +0.271 | 2020: +0.025 | 2021: +0.278 | 2022: +0.288 | 2023: +0.280 | 2024: +0.188 | 2025: +0.130 | 2026: -0.264
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.58
- Early IC=+0.1928, Recent IC=+0.1123, 1st-half IC=+0.1730, 2nd-half IC=+0.1321, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.003, Q3_mid=+0.192, Q4=+0.175, Q5_high_vol=+0.172

**`combo_min__early_order_flow_imbalance__close_vs_open_range`** (Lock IC=+0.0766, Sharpe=+0.3061)
- Admission: Train IC=+0.2285, Deflated=+0.2283, IR=0.79, Mono=0.81, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.029 | 2017: +0.158 | 2018: +0.116 | 2019: +0.112 | 2020: +0.053 | 2021: +0.116 | 2022: +0.111 | 2023: +0.103 | 2024: +0.127 | 2025: +0.096 | 2026: -0.120
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.118 | 2017: +0.298 | 2018: +0.191 | 2019: +0.302 | 2020: +0.096 | 2021: +0.251 | 2022: +0.163 | 2023: +0.149 | 2024: +0.411 | 2025: -0.037 | 2026: -0.142
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.58
- Early IC=+0.1464, Recent IC=+0.0846, 1st-half IC=+0.1195, 2nd-half IC=+0.0963, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.014, Q3_mid=+0.138, Q4=+0.182, Q5_high_vol=+0.067

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0684, Sharpe=+0.3053)
- Admission: Train IC=+0.2978, Deflated=+0.2971, IR=0.89, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.085 | 2017: +0.205 | 2018: +0.250 | 2019: +0.155 | 2020: +0.120 | 2021: +0.089 | 2022: +0.055 | 2023: +0.059 | 2024: +0.109 | 2025: +0.101 | 2026: -0.028
- Yearly Tail ICs:   2015: +0.442 | 2016: +0.169 | 2017: +0.358 | 2018: +0.314 | 2019: +0.237 | 2020: +0.202 | 2021: +0.359 | 2022: +0.288 | 2023: +0.165 | 2024: +0.165 | 2025: +0.073 | 2026: -0.127
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.43
- Early IC=+0.2447, Recent IC=+0.1042, 1st-half IC=+0.1932, 2nd-half IC=+0.1536, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.055, Q3_mid=+0.163, Q4=+0.193, Q5_high_vol=+0.253

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0787, Sharpe=+0.2956)
- Admission: Train IC=+0.2561, Deflated=+0.2555, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.134 | 2017: +0.166 | 2018: +0.253 | 2019: +0.127 | 2020: +0.100 | 2021: +0.152 | 2022: +0.083 | 2023: +0.080 | 2024: +0.145 | 2025: +0.094 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.167 | 2017: +0.317 | 2018: +0.490 | 2019: +0.146 | 2020: +0.270 | 2021: +0.290 | 2022: +0.154 | 2023: +0.087 | 2024: +0.260 | 2025: -0.031 | 2026: -0.266
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.67
- Early IC=+0.1877, Recent IC=+0.1259, 1st-half IC=+0.1873, 2nd-half IC=+0.1524, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.030, Q3_mid=+0.182, Q4=+0.177, Q5_high_vol=+0.251

**`vwap_trend_channel_slope`** (Lock IC=+0.0797, Sharpe=+0.2930)
- Admission: Train IC=+0.1689, Deflated=+0.1689, IR=0.46, Mono=0.68, p=0.0004, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.156
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.60
- Early IC=+0.1284, Recent IC=+0.0768, 1st-half IC=+0.1314, 2nd-half IC=+0.0783, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.033, Q3_mid=+0.151, Q4=+0.116, Q5_high_vol=+0.091

**`combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance`** (Lock IC=+0.0916, Sharpe=+0.2927)
- Admission: Train IC=+0.2743, Deflated=+0.2733, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.015 | 2017: +0.219 | 2018: +0.156 | 2019: +0.125 | 2020: +0.092 | 2021: +0.131 | 2022: +0.113 | 2023: +0.061 | 2024: +0.128 | 2025: +0.140 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.484 | 2016: -0.054 | 2017: +0.213 | 2018: +0.347 | 2019: +0.367 | 2020: +0.034 | 2021: +0.344 | 2022: +0.384 | 2023: +0.186 | 2024: +0.312 | 2025: +0.036 | 2026: -0.161
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.49
- Early IC=+0.2291, Recent IC=+0.1121, 1st-half IC=+0.1780, 2nd-half IC=+0.1236, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.017, Q3_mid=+0.181, Q4=+0.186, Q5_high_vol=+0.183

**`combo_max__trend_day_regime_conviction__max_down_ret`** (Lock IC=+0.0742, Sharpe=+0.2904)
- Admission: Train IC=+0.1604, Deflated=+0.1596, IR=0.42, Mono=0.65, p=0.0012, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.049 | 2017: +0.221 | 2018: +0.136 | 2019: +0.091 | 2020: +0.102 | 2021: +0.069 | 2022: +0.066 | 2023: +0.051 | 2024: +0.132 | 2025: +0.129 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.248 | 2016: +0.080 | 2017: +0.195 | 2018: +0.008 | 2019: +0.209 | 2020: +0.045 | 2021: +0.085 | 2022: +0.228 | 2023: +0.146 | 2024: +0.302 | 2025: +0.056 | 2026: -0.083
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.47
- Early IC=+0.1834, Recent IC=+0.0856, 1st-half IC=+0.1531, 2nd-half IC=+0.0968, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.225, Q2=+0.006, Q3_mid=+0.155, Q4=+0.143, Q5_high_vol=+0.125

**`combo_rank_max__opening_auction_imbalance__star50_limit_proximity_early`** (Lock IC=+0.1063, Sharpe=+0.2899)
- Admission: Train IC=+0.2165, Deflated=+0.2161, IR=0.54, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.085 | 2017: +0.158 | 2018: +0.159 | 2019: +0.103 | 2020: +0.101 | 2021: +0.036 | 2022: +0.140 | 2023: +0.077 | 2024: +0.104 | 2025: +0.083 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.198 | 2017: +0.154 | 2018: +0.098 | 2019: +0.233 | 2020: +0.071 | 2021: +0.225 | 2022: +0.191 | 2023: +0.096 | 2024: +0.143 | 2025: +0.022 | 2026: -0.274
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.26
- Early IC=+0.2671, Recent IC=+0.0691, 1st-half IC=+0.2106, 2nd-half IC=+0.1054, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.058, Q3_mid=+0.204, Q4=+0.128, Q5_high_vol=+0.201

**`combo_min__first_bar_return__max_down_ret`** (Lock IC=+0.0649, Sharpe=+0.2882)
- Admission: Train IC=+0.2194, Deflated=+0.2189, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.101 | 2017: +0.177 | 2018: +0.173 | 2019: +0.139 | 2020: +0.097 | 2021: +0.086 | 2022: +0.040 | 2023: +0.054 | 2024: +0.097 | 2025: +0.139 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.384 | 2016: -0.055 | 2017: +0.299 | 2018: +0.189 | 2019: +0.340 | 2020: +0.196 | 2021: +0.350 | 2022: +0.096 | 2023: +0.077 | 2024: +0.260 | 2025: +0.156 | 2026: +0.059
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.72, Recency ratio=0.42
- Early IC=+0.2176, Recent IC=+0.0913, 1st-half IC=+0.1684, 2nd-half IC=+0.1216, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.017, Q3_mid=+0.112, Q4=+0.159, Q5_high_vol=+0.222

**`combo_max__max_up_ret__shaved_bar_trend_conviction`** (Lock IC=+0.0742, Sharpe=+0.2879)
- Admission: Train IC=+0.2607, Deflated=+0.2605, IR=0.90, Mono=0.84, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.066 | 2017: +0.176 | 2018: +0.220 | 2019: +0.063 | 2020: +0.174 | 2021: +0.084 | 2022: +0.056 | 2023: +0.108 | 2024: +0.105 | 2025: +0.123 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.213 | 2017: +0.152 | 2018: +0.353 | 2019: +0.130 | 2020: +0.282 | 2021: +0.254 | 2022: +0.032 | 2023: -0.049 | 2024: +0.282 | 2025: -0.054 | 2026: -0.194
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.62
- Early IC=+0.2073, Recent IC=+0.1293, 1st-half IC=+0.1820, 2nd-half IC=+0.1378, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.011, Q3_mid=+0.214, Q4=+0.204, Q5_high_vol=+0.221

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1029, Sharpe=+0.2868)
- Admission: Train IC=+0.2189, Deflated=+0.2186, IR=0.59, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.122 | 2017: +0.210 | 2018: +0.081 | 2019: +0.055 | 2020: +0.106 | 2021: -0.007 | 2022: +0.099 | 2023: +0.066 | 2024: +0.100 | 2025: +0.095 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.197 | 2016: +0.189 | 2017: +0.338 | 2018: +0.221 | 2019: +0.088 | 2020: +0.172 | 2021: +0.163 | 2022: +0.156 | 2023: +0.005 | 2024: +0.152 | 2025: +0.020 | 2026: +0.208
- IC CV=0.59, Neg years (linear/tail)=1/0 of 8, Half ratio=0.35, Recency ratio=0.27
- Early IC=+0.1802, Recent IC=+0.0494, 1st-half IC=+0.1909, 2nd-half IC=+0.0670, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.038, Q3_mid=+0.131, Q4=+0.160, Q5_high_vol=+0.147

**`combo_rank_max__max_up_ret__shaved_bar_trend_conviction`** (Lock IC=+0.0789, Sharpe=+0.2845)
- Admission: Train IC=+0.2469, Deflated=+0.2465, IR=0.97, Mono=0.83, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.073 | 2017: +0.184 | 2018: +0.223 | 2019: +0.072 | 2020: +0.169 | 2021: +0.094 | 2022: +0.073 | 2023: +0.106 | 2024: +0.107 | 2025: +0.124 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.241 | 2017: +0.190 | 2018: +0.286 | 2019: +0.062 | 2020: +0.293 | 2021: +0.197 | 2022: +0.116 | 2023: -0.081 | 2024: +0.190 | 2025: -0.003 | 2026: -0.175
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.62
- Early IC=+0.2081, Recent IC=+0.1295, 1st-half IC=+0.1883, 2nd-half IC=+0.1395, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.019, Q3_mid=+0.221, Q4=+0.203, Q5_high_vol=+0.229

**`combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0770, Sharpe=+0.2840)
- Admission: Train IC=+0.2062, Deflated=+0.2059, IR=0.58, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.096 | 2017: +0.153 | 2018: +0.082 | 2019: +0.075 | 2020: +0.092 | 2021: +0.045 | 2022: +0.073 | 2023: +0.093 | 2024: +0.124 | 2025: +0.095 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.543 | 2016: +0.153 | 2017: +0.114 | 2018: +0.163 | 2019: +0.108 | 2020: +0.191 | 2021: +0.193 | 2022: +0.105 | 2023: +0.356 | 2024: +0.166 | 2025: +0.027 | 2026: -0.280
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.39
- Early IC=+0.1744, Recent IC=+0.0684, 1st-half IC=+0.1529, 2nd-half IC=+0.0783, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.030, Q3_mid=+0.165, Q4=+0.150, Q5_high_vol=+0.135

**`combo_rank_min__trend_bar_close_consistency__close_vs_open_range`** (Lock IC=+0.0804, Sharpe=+0.2801)
- Admission: Train IC=+0.2557, Deflated=+0.2556, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.049 | 2017: +0.176 | 2018: +0.108 | 2019: +0.031 | 2020: +0.091 | 2021: +0.035 | 2022: +0.099 | 2023: +0.081 | 2024: +0.117 | 2025: +0.129 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.318 | 2016: +0.192 | 2017: +0.455 | 2018: +0.309 | 2019: +0.016 | 2020: +0.209 | 2021: +0.186 | 2022: +0.230 | 2023: -0.021 | 2024: +0.278 | 2025: -0.029 | 2026: -0.210
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.42
- Early IC=+0.1515, Recent IC=+0.0636, 1st-half IC=+0.1319, 2nd-half IC=+0.0696, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.003, Q3_mid=+0.124, Q4=+0.146, Q5_high_vol=+0.082

**`combo_mean__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0801, Sharpe=+0.2782)
- Admission: Train IC=+0.1966, Deflated=+0.1962, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.032 | 2017: +0.215 | 2018: +0.126 | 2019: +0.112 | 2020: +0.092 | 2021: +0.085 | 2022: +0.073 | 2023: +0.088 | 2024: +0.114 | 2025: +0.124 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.124 | 2017: +0.224 | 2018: +0.182 | 2019: +0.242 | 2020: +0.080 | 2021: +0.274 | 2022: +0.231 | 2023: +0.304 | 2024: +0.200 | 2025: +0.140 | 2026: -0.226
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.49
- Early IC=+0.1816, Recent IC=+0.0884, 1st-half IC=+0.1545, 2nd-half IC=+0.1037, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.000, Q3_mid=+0.174, Q4=+0.157, Q5_high_vol=+0.134

**`combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.1086, Sharpe=+0.2775)
- Admission: Train IC=+0.2497, Deflated=+0.2498, IR=0.88, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.074 | 2017: +0.207 | 2018: +0.169 | 2019: +0.117 | 2020: +0.141 | 2021: +0.083 | 2022: +0.087 | 2023: +0.084 | 2024: +0.104 | 2025: +0.149 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.162 | 2016: +0.216 | 2017: +0.265 | 2018: +0.330 | 2019: +0.398 | 2020: +0.166 | 2021: +0.294 | 2022: +0.171 | 2023: +0.098 | 2024: +0.149 | 2025: +0.057 | 2026: -0.144
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.50
- Early IC=+0.2227, Recent IC=+0.1119, 1st-half IC=+0.2019, 2nd-half IC=+0.1354, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.083, Q3_mid=+0.196, Q4=+0.203, Q5_high_vol=+0.169

**`combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0802, Sharpe=+0.2770)
- Admission: Train IC=+0.2947, Deflated=+0.2943, IR=0.85, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.031 | 2017: +0.185 | 2018: +0.156 | 2019: +0.085 | 2020: +0.113 | 2021: +0.096 | 2022: +0.067 | 2023: +0.103 | 2024: +0.132 | 2025: +0.112 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.206 | 2017: +0.311 | 2018: +0.300 | 2019: +0.181 | 2020: +0.149 | 2021: +0.303 | 2022: +0.278 | 2023: -0.056 | 2024: +0.236 | 2025: +0.090 | 2026: +0.001
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.56
- Early IC=+0.1860, Recent IC=+0.1041, 1st-half IC=+0.1468, 2nd-half IC=+0.1142, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.022, Q3_mid=+0.175, Q4=+0.160, Q5_high_vol=+0.132

**`combo_rank_max__opening_auction_imbalance__max_down_ret`** (Lock IC=+0.0815, Sharpe=+0.2752)
- Admission: Train IC=+0.2301, Deflated=+0.2292, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.059 | 2017: +0.211 | 2018: +0.179 | 2019: +0.126 | 2020: +0.107 | 2021: +0.090 | 2022: +0.079 | 2023: +0.043 | 2024: +0.142 | 2025: +0.152 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.047 | 2017: +0.247 | 2018: +0.112 | 2019: +0.383 | 2020: +0.039 | 2021: +0.301 | 2022: +0.244 | 2023: +0.162 | 2024: +0.340 | 2025: +0.243 | 2026: +0.035
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.45
- Early IC=+0.2141, Recent IC=+0.0970, 1st-half IC=+0.1658, 2nd-half IC=+0.1226, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.010, Q3_mid=+0.188, Q4=+0.180, Q5_high_vol=+0.165

**`combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1152, Sharpe=+0.2720)
- Admission: Train IC=+0.1892, Deflated=+0.1881, IR=0.52, Mono=0.70, p=0.0002, MaxCorr=0.66
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.115 | 2017: +0.107 | 2018: +0.080 | 2019: +0.164 | 2020: +0.084 | 2021: +0.091 | 2022: +0.140 | 2023: +0.096 | 2024: +0.096 | 2025: +0.056 | 2026: +0.143
- Yearly Tail ICs:   2015: +0.016 | 2016: +0.135 | 2017: +0.291 | 2018: +0.291 | 2019: +0.250 | 2020: +0.112 | 2021: +0.138 | 2022: +0.024 | 2023: +0.020 | 2024: -0.019 | 2025: -0.141 | 2026: +0.117
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.38
- Early IC=+0.2276, Recent IC=+0.0876, 1st-half IC=+0.2098, 2nd-half IC=+0.1040, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.077, Q3_mid=+0.185, Q4=+0.192, Q5_high_vol=+0.157

**`combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1091, Sharpe=+0.2719)
- Admission: Train IC=+0.2652, Deflated=+0.2644, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.290 | 2016: +0.136 | 2017: +0.227 | 2018: +0.158 | 2019: +0.121 | 2020: +0.186 | 2021: +0.087 | 2022: +0.119 | 2023: +0.076 | 2024: +0.111 | 2025: +0.080 | 2026: +0.118
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.388 | 2017: +0.079 | 2018: +0.109 | 2019: +0.266 | 2020: +0.172 | 2021: +0.107 | 2022: +0.022 | 2023: -0.131 | 2024: +0.119 | 2025: +0.018 | 2026: +0.043
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.55
- Early IC=+0.2474, Recent IC=+0.1367, 1st-half IC=+0.2320, 2nd-half IC=+0.1397, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.069, Q3_mid=+0.210, Q4=+0.172, Q5_high_vol=+0.265

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0834, Sharpe=+0.2704)
- Admission: Train IC=+0.2044, Deflated=+0.2036, IR=0.75, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.105 | 2017: +0.208 | 2018: +0.153 | 2019: +0.042 | 2020: +0.115 | 2021: +0.073 | 2022: +0.131 | 2023: +0.086 | 2024: +0.118 | 2025: +0.106 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.189 | 2016: +0.261 | 2017: +0.354 | 2018: +0.244 | 2019: -0.007 | 2020: +0.235 | 2021: +0.223 | 2022: +0.115 | 2023: +0.146 | 2024: +0.226 | 2025: +0.011 | 2026: -0.077
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.54, Recency ratio=0.57
- Early IC=+0.1651, Recent IC=+0.0940, 1st-half IC=+0.1731, 2nd-half IC=+0.0938, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.005, Q3_mid=+0.176, Q4=+0.164, Q5_high_vol=+0.168

**`combo_rank_max__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0871, Sharpe=+0.2701)
- Admission: Train IC=+0.2424, Deflated=+0.2422, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: +0.120 | 2018: +0.211 | 2019: +0.098 | 2020: +0.108 | 2021: +0.097 | 2022: +0.134 | 2023: +0.084 | 2024: +0.119 | 2025: +0.085 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.105 | 2017: +0.112 | 2018: +0.392 | 2019: +0.159 | 2020: +0.174 | 2021: +0.334 | 2022: +0.227 | 2023: +0.247 | 2024: +0.297 | 2025: -0.021 | 2026: -0.157
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.47
- Early IC=+0.2206, Recent IC=+0.1032, 1st-half IC=+0.1747, 2nd-half IC=+0.1263, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.143, Q2=-0.004, Q3_mid=+0.177, Q4=+0.186, Q5_high_vol=+0.229

**`combo_rank_max__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0652, Sharpe=+0.2701)
- Admission: Train IC=+0.2014, Deflated=+0.2003, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.108 | 2017: +0.161 | 2018: +0.219 | 2019: +0.149 | 2020: +0.093 | 2021: +0.109 | 2022: +0.065 | 2023: +0.065 | 2024: +0.109 | 2025: +0.094 | 2026: -0.041
- Yearly Tail ICs:   2015: +0.134 | 2016: -0.027 | 2017: +0.239 | 2018: +0.226 | 2019: +0.237 | 2020: +0.194 | 2021: +0.176 | 2022: +0.059 | 2023: +0.113 | 2024: +0.089 | 2025: +0.017 | 2026: -0.015
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=0.90, Recency ratio=0.55
- Early IC=+0.1797, Recent IC=+0.0997, 1st-half IC=+0.1579, 2nd-half IC=+0.1415, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.010, Q3_mid=+0.146, Q4=+0.162, Q5_high_vol=+0.219

**`combo_min__max_up_ret__max_down_ret`** (Lock IC=+0.1000, Sharpe=+0.2700)
- Admission: Train IC=+0.2330, Deflated=+0.2318, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.081 | 2017: +0.200 | 2018: +0.131 | 2019: +0.106 | 2020: +0.136 | 2021: +0.117 | 2022: +0.113 | 2023: +0.105 | 2024: +0.117 | 2025: +0.136 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.368 | 2016: +0.017 | 2017: +0.212 | 2018: +0.206 | 2019: +0.230 | 2020: +0.145 | 2021: +0.300 | 2022: +0.211 | 2023: +0.156 | 2024: +0.216 | 2025: +0.195 | 2026: +0.047
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.55
- Early IC=+0.2297, Recent IC=+0.1266, 1st-half IC=+0.2024, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.201, Q2=+0.050, Q3_mid=+0.194, Q4=+0.144, Q5_high_vol=+0.214

**`combo_sig_product__opening_auction_imbalance__close_vs_open_range`** (Lock IC=+0.0840, Sharpe=+0.2698)
- Admission: Train IC=+0.1979, Deflated=+0.1970, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.068 | 2017: +0.200 | 2018: +0.097 | 2019: +0.063 | 2020: +0.101 | 2021: +0.061 | 2022: +0.085 | 2023: +0.100 | 2024: +0.111 | 2025: +0.128 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.313 | 2016: +0.126 | 2017: +0.361 | 2018: +0.216 | 2019: +0.091 | 2020: +0.117 | 2021: +0.241 | 2022: +0.136 | 2023: +0.059 | 2024: +0.255 | 2025: -0.009 | 2026: -0.055
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.49
- Early IC=+0.1663, Recent IC=+0.0811, 1st-half IC=+0.1469, 2nd-half IC=+0.0798, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.205, Q2=-0.040, Q3_mid=+0.171, Q4=+0.160, Q5_high_vol=+0.107

**`combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0`** (Lock IC=+0.0814, Sharpe=+0.2646)
- Admission: Train IC=+0.2778, Deflated=+0.2772, IR=0.84, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.115 | 2017: +0.150 | 2018: +0.264 | 2019: +0.110 | 2020: +0.114 | 2021: +0.109 | 2022: +0.121 | 2023: +0.072 | 2024: +0.138 | 2025: +0.107 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.232 | 2016: +0.209 | 2017: +0.177 | 2018: +0.351 | 2019: +0.155 | 2020: +0.298 | 2021: +0.217 | 2022: +0.238 | 2023: +0.356 | 2024: +0.256 | 2025: -0.169 | 2026: -0.318
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.54
- Early IC=+0.2057, Recent IC=+0.1114, 1st-half IC=+0.1887, 2nd-half IC=+0.1463, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.023, Q3_mid=+0.193, Q4=+0.184, Q5_high_vol=+0.246

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1195, Sharpe=+0.2602)
- Admission: Train IC=+0.2330, Deflated=+0.2321, IR=0.60, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.139 | 2017: +0.236 | 2018: +0.142 | 2019: +0.131 | 2020: +0.152 | 2021: +0.084 | 2022: +0.139 | 2023: +0.085 | 2024: +0.110 | 2025: +0.084 | 2026: +0.150
- Yearly Tail ICs:   2015: +0.205 | 2016: +0.226 | 2017: +0.085 | 2018: +0.097 | 2019: +0.255 | 2020: +0.052 | 2021: +0.135 | 2022: +0.158 | 2023: -0.045 | 2024: +0.137 | 2025: +0.110 | 2026: +0.116
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.47
- Early IC=+0.2497, Recent IC=+0.1175, 1st-half IC=+0.2356, 2nd-half IC=+0.1310, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.073, Q3_mid=+0.216, Q4=+0.159, Q5_high_vol=+0.258

**`combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend`** (Lock IC=+0.0882, Sharpe=+0.2602)
- Admission: Train IC=+0.1689, Deflated=+0.1686, IR=0.45, Mono=0.65, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.124 | 2016: +0.023 | 2017: +0.164 | 2018: +0.115 | 2019: +0.096 | 2020: +0.081 | 2021: +0.031 | 2022: +0.127 | 2023: +0.114 | 2024: +0.094 | 2025: +0.118 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.019 | 2017: +0.138 | 2018: +0.210 | 2019: +0.269 | 2020: +0.030 | 2021: +0.253 | 2022: +0.105 | 2023: +0.291 | 2024: +0.202 | 2025: +0.169 | 2026: -0.299
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.39
- Early IC=+0.1437, Recent IC=+0.0559, 1st-half IC=+0.1263, 2nd-half IC=+0.0851, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.020, Q3_mid=+0.157, Q4=+0.138, Q5_high_vol=+0.081

**`combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0922, Sharpe=+0.2567)
- Admission: Train IC=+0.2520, Deflated=+0.2515, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.174 | 2017: +0.160 | 2018: +0.151 | 2019: +0.111 | 2020: +0.134 | 2021: +0.085 | 2022: +0.093 | 2023: +0.035 | 2024: +0.104 | 2025: +0.081 | 2026: +0.108
- Yearly Tail ICs:   2015: +0.146 | 2016: +0.381 | 2017: +0.160 | 2018: +0.171 | 2019: +0.175 | 2020: +0.082 | 2021: +0.155 | 2022: +0.038 | 2023: -0.160 | 2024: +0.042 | 2025: -0.074 | 2026: +0.238
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.56
- Early IC=+0.1959, Recent IC=+0.1099, 1st-half IC=+0.1906, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.055, Q3_mid=+0.164, Q4=+0.127, Q5_high_vol=+0.249

**`combo_mean__first_bar_return__early_order_flow_imbalance`** (Lock IC=+0.0733, Sharpe=+0.2547)
- Admission: Train IC=+0.2261, Deflated=+0.2254, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.026 | 2017: +0.137 | 2018: +0.191 | 2019: +0.135 | 2020: +0.075 | 2021: +0.132 | 2022: +0.121 | 2023: +0.073 | 2024: +0.119 | 2025: +0.086 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.186 | 2016: -0.078 | 2017: +0.150 | 2018: +0.390 | 2019: +0.276 | 2020: +0.096 | 2021: +0.345 | 2022: +0.262 | 2023: +0.316 | 2024: +0.307 | 2025: +0.091 | 2026: -0.246
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.94, Recency ratio=0.54
- Early IC=+0.1911, Recent IC=+0.1033, 1st-half IC=+0.1405, 2nd-half IC=+0.1315, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.013, Q3_mid=+0.148, Q4=+0.190, Q5_high_vol=+0.150

**`combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0803, Sharpe=+0.2519)
- Admission: Train IC=+0.1764, Deflated=+0.1768, IR=0.44, Mono=0.68, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.051 | 2017: +0.152 | 2018: +0.131 | 2019: +0.080 | 2020: +0.100 | 2021: +0.021 | 2022: +0.080 | 2023: +0.080 | 2024: +0.045 | 2025: +0.111 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.100 | 2016: +0.062 | 2017: +0.137 | 2018: +0.212 | 2019: +0.193 | 2020: +0.070 | 2021: +0.023 | 2022: +0.041 | 2023: -0.044 | 2024: +0.060 | 2025: +0.132 | 2026: -0.048
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.26
- Early IC=+0.2329, Recent IC=+0.0606, 1st-half IC=+0.1903, 2nd-half IC=+0.0879, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.034, Q3_mid=+0.188, Q4=+0.144, Q5_high_vol=+0.182

**`combo_sig_product__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0704, Sharpe=+0.2515)
- Admission: Train IC=+0.1914, Deflated=+0.1908, IR=0.59, Mono=0.68, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.072 | 2017: +0.182 | 2018: +0.199 | 2019: +0.141 | 2020: +0.166 | 2021: +0.077 | 2022: +0.063 | 2023: +0.129 | 2024: +0.109 | 2025: +0.065 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.073 | 2016: +0.023 | 2017: +0.155 | 2018: +0.312 | 2019: +0.269 | 2020: +0.030 | 2021: +0.249 | 2022: +0.036 | 2023: +0.295 | 2024: +0.371 | 2025: +0.127 | 2026: -0.299
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.68
- Early IC=+0.1785, Recent IC=+0.1217, 1st-half IC=+0.1591, 2nd-half IC=+0.1481, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.067, Q3_mid=+0.177, Q4=+0.172, Q5_high_vol=+0.160

**`combo_clamp_diff__first_bar_return__late_bar_momentum`** (Lock IC=+0.0702, Sharpe=+0.2511)
- Admission: Train IC=+0.2486, Deflated=+0.2483, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.074 | 2017: +0.159 | 2018: +0.233 | 2019: +0.199 | 2020: +0.113 | 2021: +0.123 | 2022: +0.063 | 2023: +0.063 | 2024: +0.116 | 2025: +0.016 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.352 | 2016: +0.020 | 2017: +0.426 | 2018: +0.351 | 2019: +0.296 | 2020: +0.213 | 2021: +0.137 | 2022: +0.189 | 2023: +0.086 | 2024: +0.126 | 2025: -0.008 | 2026: +0.027
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.59
- Early IC=+0.2008, Recent IC=+0.1183, 1st-half IC=+0.1649, 2nd-half IC=+0.1609, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.044, Q3_mid=+0.169, Q4=+0.141, Q5_high_vol=+0.284

**`combo_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0861, Sharpe=+0.2510)
- Admission: Train IC=+0.2425, Deflated=+0.2416, IR=0.61, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.071 | 2017: +0.252 | 2018: +0.190 | 2019: +0.134 | 2020: +0.161 | 2021: +0.095 | 2022: +0.081 | 2023: +0.077 | 2024: +0.137 | 2025: +0.101 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.456 | 2016: +0.074 | 2017: +0.152 | 2018: +0.151 | 2019: +0.257 | 2020: +0.030 | 2021: +0.349 | 2022: +0.232 | 2023: +0.103 | 2024: +0.106 | 2025: +0.158 | 2026: -0.016
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.59
- Early IC=+0.2192, Recent IC=+0.1284, 1st-half IC=+0.1851, 2nd-half IC=+0.1409, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.233, Q2=+0.005, Q3_mid=+0.166, Q4=+0.191, Q5_high_vol=+0.239

**`combo_mean__opening_auction_imbalance__max_down_ret`** (Lock IC=+0.0882, Sharpe=+0.2493)
- Admission: Train IC=+0.2194, Deflated=+0.2187, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.075 | 2017: +0.191 | 2018: +0.155 | 2019: +0.101 | 2020: +0.118 | 2021: +0.078 | 2022: +0.091 | 2023: +0.077 | 2024: +0.134 | 2025: +0.130 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.048 | 2017: +0.171 | 2018: +0.149 | 2019: +0.179 | 2020: +0.087 | 2021: +0.303 | 2022: +0.322 | 2023: +0.338 | 2024: +0.338 | 2025: +0.022 | 2026: -0.014
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.46
- Early IC=+0.2113, Recent IC=+0.0981, 1st-half IC=+0.1656, 2nd-half IC=+0.1136, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.010, Q3_mid=+0.172, Q4=+0.166, Q5_high_vol=+0.182

**`combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0885, Sharpe=+0.2487)
- Admission: Train IC=+0.2574, Deflated=+0.2559, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.100 | 2017: +0.226 | 2018: +0.242 | 2019: +0.145 | 2020: +0.142 | 2021: +0.169 | 2022: +0.092 | 2023: +0.108 | 2024: +0.150 | 2025: +0.088 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.335 | 2016: -0.070 | 2017: +0.184 | 2018: +0.368 | 2019: +0.219 | 2020: +0.248 | 2021: +0.357 | 2022: +0.153 | 2023: +0.156 | 2024: +0.271 | 2025: -0.018 | 2026: -0.152
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=0.84, Recency ratio=0.73
- Early IC=+0.2118, Recent IC=+0.1547, 1st-half IC=+0.1973, 2nd-half IC=+0.1650, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.224, Q2=+0.046, Q3_mid=+0.204, Q4=+0.180, Q5_high_vol=+0.243

**`combo_diff__bar_ret_0__h2_l2_pullback_continuation`** (Lock IC=+0.0773, Sharpe=+0.2462)
- Admission: Train IC=+0.2309, Deflated=+0.2301, IR=0.69, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.099 | 2017: +0.160 | 2018: +0.159 | 2019: +0.101 | 2020: +0.100 | 2021: +0.073 | 2022: +0.087 | 2023: +0.100 | 2024: +0.138 | 2025: +0.092 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.036 | 2017: +0.106 | 2018: +0.331 | 2019: +0.167 | 2020: +0.080 | 2021: +0.178 | 2022: +0.217 | 2023: +0.301 | 2024: +0.311 | 2025: -0.006 | 2026: -0.265
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.48
- Early IC=+0.1793, Recent IC=+0.0863, 1st-half IC=+0.1693, 2nd-half IC=+0.1135, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.013, Q3_mid=+0.186, Q4=+0.176, Q5_high_vol=+0.167

**`combo_rank_max__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0735, Sharpe=+0.2454)
- Admission: Train IC=+0.2165, Deflated=+0.2155, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.217 | 2016: -0.004 | 2017: +0.204 | 2018: +0.154 | 2019: +0.130 | 2020: +0.084 | 2021: +0.100 | 2022: +0.061 | 2023: +0.044 | 2024: +0.119 | 2025: +0.177 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.355 | 2016: -0.164 | 2017: +0.253 | 2018: +0.186 | 2019: +0.387 | 2020: +0.014 | 2021: +0.363 | 2022: +0.274 | 2023: +0.158 | 2024: +0.327 | 2025: +0.265 | 2026: -0.108
- IC CV=0.53, Neg years (linear/tail)=1/1 of 8, Half ratio=0.74, Recency ratio=0.42
- Early IC=+0.2166, Recent IC=+0.0912, 1st-half IC=+0.1509, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.003, Q3_mid=+0.169, Q4=+0.175, Q5_high_vol=+0.130

**`combo_mean__bar_ret_0__shaved_bar_trend_conviction`** (Lock IC=+0.0597, Sharpe=+0.2451)
- Admission: Train IC=+0.2227, Deflated=+0.2220, IR=0.59, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.067 | 2017: +0.172 | 2018: +0.190 | 2019: +0.071 | 2020: +0.116 | 2021: +0.073 | 2022: +0.038 | 2023: +0.083 | 2024: +0.096 | 2025: +0.118 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.293 | 2016: -0.016 | 2017: +0.167 | 2018: +0.252 | 2019: +0.118 | 2020: +0.181 | 2021: +0.038 | 2022: +0.177 | 2023: +0.130 | 2024: +0.184 | 2025: +0.181 | 2026: -0.281
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.70, Recency ratio=0.49
- Early IC=+0.1946, Recent IC=+0.0946, 1st-half IC=+0.1662, 2nd-half IC=+0.1169, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.013, Q3_mid=+0.176, Q4=+0.178, Q5_high_vol=+0.173

**`combo_rel_diff__first_bar_return__early_late_momentum_divergence`** (Lock IC=+0.0546, Sharpe=+0.2403)
- Admission: Train IC=+0.2089, Deflated=+0.2087, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.311 | 2016: +0.059 | 2017: +0.156 | 2018: +0.226 | 2019: +0.179 | 2020: +0.091 | 2021: +0.122 | 2022: +0.031 | 2023: +0.070 | 2024: +0.088 | 2025: +0.021 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.271 | 2016: -0.064 | 2017: +0.385 | 2018: +0.337 | 2019: +0.084 | 2020: +0.177 | 2021: +0.154 | 2022: +0.046 | 2023: +0.282 | 2024: +0.120 | 2025: +0.019 | 2026: -0.055
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.93, Recency ratio=0.52
- Early IC=+0.2042, Recent IC=+0.1068, 1st-half IC=+0.1580, 2nd-half IC=+0.1471, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.040, Q3_mid=+0.154, Q4=+0.131, Q5_high_vol=+0.277

**`combo_sig_product__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0802, Sharpe=+0.2391)
- Admission: Train IC=+0.2518, Deflated=+0.2520, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.114 | 2017: +0.169 | 2018: +0.185 | 2019: +0.124 | 2020: +0.118 | 2021: +0.006 | 2022: +0.111 | 2023: +0.084 | 2024: +0.094 | 2025: +0.093 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.262 | 2017: +0.158 | 2018: +0.324 | 2019: +0.321 | 2020: +0.061 | 2021: +0.254 | 2022: +0.099 | 2023: +0.281 | 2024: +0.305 | 2025: -0.008 | 2026: -0.066
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.35
- Early IC=+0.1755, Recent IC=+0.0620, 1st-half IC=+0.1858, 2nd-half IC=+0.1170, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.024, Q3_mid=+0.129, Q4=+0.158, Q5_high_vol=+0.222

**`combo_rank_min__max_down_ret__shaved_bar_trend_conviction`** (Lock IC=+0.0553, Sharpe=+0.2319)
- Admission: Train IC=+0.1898, Deflated=+0.1893, IR=0.61, Mono=0.71, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.029 | 2017: +0.184 | 2018: +0.097 | 2019: +0.052 | 2020: +0.130 | 2021: -0.017 | 2022: +0.003 | 2023: +0.065 | 2024: +0.087 | 2025: +0.106 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.341 | 2016: -0.044 | 2017: +0.192 | 2018: +0.092 | 2019: +0.126 | 2020: +0.219 | 2021: +0.176 | 2022: +0.088 | 2023: +0.030 | 2024: +0.215 | 2025: +0.220 | 2026: +0.084
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=0.50, Recency ratio=0.27
- Early IC=+0.2070, Recent IC=+0.0549, 1st-half IC=+0.1463, 2nd-half IC=+0.0735, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.038, Q3_mid=+0.127, Q4=+0.139, Q5_high_vol=+0.165

**`open_to_current_return`** (Lock IC=+0.0842, Sharpe=+0.2310)
- Admission: Train IC=+0.1659, Deflated=+0.1656, IR=0.56, Mono=0.73, p=0.0008, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.121
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.252
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.56
- Early IC=+0.1590, Recent IC=+0.0884, 1st-half IC=+0.1474, 2nd-half IC=+0.0965, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.017, Q3_mid=+0.161, Q4=+0.174, Q5_high_vol=+0.104

**`combo_mean__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0873, Sharpe=+0.2238)
- Admission: Train IC=+0.2910, Deflated=+0.2905, IR=0.99, Mono=0.83, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.042 | 2017: +0.150 | 2018: +0.172 | 2019: +0.128 | 2020: +0.095 | 2021: +0.145 | 2022: +0.149 | 2023: +0.098 | 2024: +0.133 | 2025: +0.087 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.161 | 2017: +0.175 | 2018: +0.444 | 2019: +0.226 | 2020: +0.162 | 2021: +0.309 | 2022: +0.227 | 2023: +0.333 | 2024: +0.312 | 2025: -0.017 | 2026: -0.234
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.58
- Early IC=+0.2066, Recent IC=+0.1197, 1st-half IC=+0.1683, 2nd-half IC=+0.1331, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.000, Q3_mid=+0.190, Q4=+0.198, Q5_high_vol=+0.180

**`combo_clamp_diff__first_bar_return__h2_l2_pullback_continuation`** (Lock IC=+0.0743, Sharpe=+0.2234)
- Admission: Train IC=+0.2403, Deflated=+0.2396, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.098 | 2017: +0.162 | 2018: +0.160 | 2019: +0.098 | 2020: +0.109 | 2021: +0.075 | 2022: +0.079 | 2023: +0.098 | 2024: +0.129 | 2025: +0.095 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.376 | 2016: -0.031 | 2017: +0.168 | 2018: +0.362 | 2019: +0.257 | 2020: +0.177 | 2021: +0.259 | 2022: +0.072 | 2023: +0.290 | 2024: +0.114 | 2025: +0.090 | 2026: -0.018
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.52
- Early IC=+0.1774, Recent IC=+0.0920, 1st-half IC=+0.1681, 2nd-half IC=+0.1155, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.182, Q2=-0.012, Q3_mid=+0.190, Q4=+0.176, Q5_high_vol=+0.162

**`combo_sig_product__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0856, Sharpe=+0.2206)
- Admission: Train IC=+0.1717, Deflated=+0.1707, IR=0.54, Mono=0.69, p=0.0004, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.041 | 2017: +0.225 | 2018: +0.171 | 2019: +0.139 | 2020: +0.198 | 2021: +0.131 | 2022: +0.038 | 2023: +0.105 | 2024: +0.116 | 2025: +0.135 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.214 | 2016: -0.045 | 2017: +0.193 | 2018: +0.098 | 2019: +0.271 | 2020: +0.060 | 2021: +0.342 | 2022: -0.023 | 2023: +0.157 | 2024: +0.267 | 2025: +0.253 | 2026: -0.089
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.90, Recency ratio=0.74
- Early IC=+0.2238, Recent IC=+0.1647, 1st-half IC=+0.1743, 2nd-half IC=+0.1572, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.069, Q3_mid=+0.196, Q4=+0.205, Q5_high_vol=+0.198

**`combo_max__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0880, Sharpe=+0.2195)
- Admission: Train IC=+0.2287, Deflated=+0.2278, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.129 | 2017: +0.173 | 2018: +0.147 | 2019: +0.125 | 2020: +0.130 | 2021: +0.067 | 2022: +0.092 | 2023: +0.048 | 2024: +0.092 | 2025: +0.082 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.139 | 2017: +0.113 | 2018: +0.112 | 2019: +0.210 | 2020: +0.077 | 2021: +0.154 | 2022: +0.086 | 2023: -0.128 | 2024: -0.084 | 2025: -0.009 | 2026: +0.180
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.46
- Early IC=+0.2146, Recent IC=+0.0985, 1st-half IC=+0.1858, 2nd-half IC=+0.1241, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.059, Q3_mid=+0.154, Q4=+0.126, Q5_high_vol=+0.241

**`combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0844, Sharpe=+0.2087)
- Admission: Train IC=+0.2790, Deflated=+0.2786, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.091 | 2017: +0.164 | 2018: +0.115 | 2019: +0.086 | 2020: +0.122 | 2021: +0.061 | 2022: +0.111 | 2023: +0.113 | 2024: +0.128 | 2025: +0.099 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.354 | 2016: +0.241 | 2017: +0.099 | 2018: +0.253 | 2019: +0.262 | 2020: +0.090 | 2021: +0.320 | 2022: +0.238 | 2023: +0.252 | 2024: +0.223 | 2025: +0.066 | 2026: +0.053
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.53
- Early IC=+0.1736, Recent IC=+0.0915, 1st-half IC=+0.1725, 2nd-half IC=+0.1017, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.001, Q3_mid=+0.209, Q4=+0.160, Q5_high_vol=+0.162

**`combo_rank_min__early_body_momentum__max_down_ret`** (Lock IC=+0.0860, Sharpe=+0.2069)
- Admission: Train IC=+0.2185, Deflated=+0.2177, IR=0.59, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.075 | 2017: +0.176 | 2018: +0.107 | 2019: +0.074 | 2020: +0.129 | 2021: +0.052 | 2022: +0.098 | 2023: +0.076 | 2024: +0.111 | 2025: +0.113 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.016 | 2017: +0.118 | 2018: +0.116 | 2019: +0.120 | 2020: +0.254 | 2021: +0.321 | 2022: +0.317 | 2023: +0.132 | 2024: +0.197 | 2025: +0.066 | 2026: +0.087
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.44
- Early IC=+0.2086, Recent IC=+0.0925, 1st-half IC=+0.1522, 2nd-half IC=+0.0933, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.029, Q3_mid=+0.147, Q4=+0.151, Q5_high_vol=+0.179

**`combo_sig_product__star50_limit_proximity_early__late_bar_momentum`** (Lock IC=+0.1365, Sharpe=+0.2056)
- Admission: Train IC=+0.1904, Deflated=+0.1899, IR=0.46, Mono=0.66, p=0.0002, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.143 | 2016: -0.054 | 2017: +0.216 | 2018: +0.017 | 2019: +0.089 | 2020: +0.102 | 2021: +0.097 | 2022: +0.080 | 2023: +0.100 | 2024: +0.225 | 2025: +0.068 | 2026: +0.194
- Yearly Tail ICs:   2015: +0.316 | 2016: -0.156 | 2017: +0.439 | 2018: +0.061 | 2019: +0.186 | 2020: +0.087 | 2021: +0.115 | 2022: -0.142 | 2023: +0.127 | 2024: +0.346 | 2025: -0.097 | 2026: +0.318
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=0.55, Recency ratio=0.52
- Early IC=+0.1899, Recent IC=+0.0994, 1st-half IC=+0.1449, 2nd-half IC=+0.0797, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.106, Q3_mid=+0.191, Q4=+0.036, Q5_high_vol=+0.136

**`combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0887, Sharpe=+0.1991)
- Admission: Train IC=+0.2425, Deflated=+0.2415, IR=0.84, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.068 | 2017: +0.261 | 2018: +0.097 | 2019: +0.119 | 2020: +0.106 | 2021: +0.117 | 2022: +0.038 | 2023: +0.083 | 2024: +0.103 | 2025: +0.105 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.156 | 2017: +0.294 | 2018: +0.388 | 2019: +0.253 | 2020: +0.130 | 2021: +0.347 | 2022: +0.070 | 2023: +0.143 | 2024: +0.134 | 2025: +0.106 | 2026: -0.106
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.60
- Early IC=+0.1837, Recent IC=+0.1109, 1st-half IC=+0.1797, 2nd-half IC=+0.1139, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.056, Q3_mid=+0.146, Q4=+0.237, Q5_high_vol=+0.129

**`combo_min__rsi_opening__close_vs_open_range`** (Lock IC=+0.0864, Sharpe=+0.1980)
- Admission: Train IC=+0.2259, Deflated=+0.2253, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.067 | 2017: +0.201 | 2018: +0.123 | 2019: +0.060 | 2020: +0.100 | 2021: +0.048 | 2022: +0.098 | 2023: +0.079 | 2024: +0.121 | 2025: +0.137 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.308 | 2016: +0.170 | 2017: +0.333 | 2018: +0.247 | 2019: +0.176 | 2020: +0.170 | 2021: +0.174 | 2022: +0.156 | 2023: +0.119 | 2024: +0.294 | 2025: -0.101 | 2026: -0.069
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.44
- Early IC=+0.1694, Recent IC=+0.0741, 1st-half IC=+0.1513, 2nd-half IC=+0.0827, Neg regimes=1/5
- Weak component: `rsi_opening` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.017, Q3_mid=+0.153, Q4=+0.169, Q5_high_vol=+0.109

**`combo_max__max_down_ret__bar_body_rng_0`** (Lock IC=+0.0766, Sharpe=+0.1954)
- Admission: Train IC=+0.1607, Deflated=+0.1595, IR=0.48, Mono=0.65, p=0.0012, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.114 | 2017: +0.192 | 2018: +0.171 | 2019: +0.144 | 2020: +0.130 | 2021: +0.088 | 2022: +0.077 | 2023: +0.054 | 2024: +0.120 | 2025: +0.123 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.395 | 2016: -0.081 | 2017: +0.100 | 2018: +0.014 | 2019: +0.313 | 2020: +0.055 | 2021: +0.178 | 2022: +0.131 | 2023: +0.164 | 2024: +0.127 | 2025: +0.073 | 2026: -0.015
- IC CV=0.27, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.59
- Early IC=+0.1854, Recent IC=+0.1086, 1st-half IC=+0.1569, 2nd-half IC=+0.1306, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.003, Q3_mid=+0.143, Q4=+0.157, Q5_high_vol=+0.226

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0937, Sharpe=+0.1867)
- Admission: Train IC=+0.2354, Deflated=+0.2345, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.101 | 2017: +0.234 | 2018: +0.199 | 2019: +0.115 | 2020: +0.154 | 2021: +0.083 | 2022: +0.120 | 2023: +0.063 | 2024: +0.085 | 2025: +0.085 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.143 | 2016: +0.259 | 2017: +0.085 | 2018: +0.316 | 2019: +0.149 | 2020: +0.092 | 2021: +0.184 | 2022: +0.125 | 2023: -0.069 | 2024: +0.085 | 2025: -0.047 | 2026: -0.107
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.46
- Early IC=+0.2575, Recent IC=+0.1189, 1st-half IC=+0.2327, 2nd-half IC=+0.1427, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.064, Q3_mid=+0.216, Q4=+0.177, Q5_high_vol=+0.262

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1169, Sharpe=+0.1847)
- Admission: Train IC=+0.2746, Deflated=+0.2737, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.138 | 2017: +0.226 | 2018: +0.116 | 2019: +0.121 | 2020: +0.123 | 2021: +0.067 | 2022: +0.092 | 2023: +0.079 | 2024: +0.089 | 2025: +0.095 | 2026: +0.200
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.323 | 2017: +0.179 | 2018: +0.315 | 2019: +0.188 | 2020: +0.216 | 2021: +0.069 | 2022: -0.095 | 2023: -0.115 | 2024: +0.110 | 2025: -0.186 | 2026: +0.399
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.48, Recency ratio=0.38
- Early IC=+0.2524, Recent IC=+0.0947, 1st-half IC=+0.2324, 2nd-half IC=+0.1105, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.111, Q3_mid=+0.176, Q4=+0.156, Q5_high_vol=+0.211

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0841, Sharpe=+0.1793)
- Admission: Train IC=+0.2192, Deflated=+0.2187, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.076 | 2017: +0.215 | 2018: +0.187 | 2019: +0.096 | 2020: +0.173 | 2021: +0.070 | 2022: +0.115 | 2023: +0.144 | 2024: +0.101 | 2025: +0.057 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.414 | 2016: +0.138 | 2017: +0.328 | 2018: +0.257 | 2019: +0.187 | 2020: +0.129 | 2021: +0.178 | 2022: +0.065 | 2023: +0.172 | 2024: +0.237 | 2025: -0.037 | 2026: -0.055
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.72
- Early IC=+0.1696, Recent IC=+0.1218, 1st-half IC=+0.1529, 2nd-half IC=+0.1353, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.038, Q3_mid=+0.188, Q4=+0.174, Q5_high_vol=+0.164

**`combo_max__rsi_opening__early_order_flow_imbalance`** (Lock IC=+0.0818, Sharpe=+0.1792)
- Admission: Train IC=+0.2342, Deflated=+0.2335, IR=0.57, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.005 | 2017: +0.144 | 2018: +0.096 | 2019: +0.094 | 2020: +0.086 | 2021: +0.083 | 2022: +0.130 | 2023: +0.070 | 2024: +0.106 | 2025: +0.130 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.340 | 2016: -0.025 | 2017: +0.177 | 2018: +0.236 | 2019: +0.321 | 2020: +0.191 | 2021: +0.119 | 2022: +0.397 | 2023: +0.144 | 2024: +0.310 | 2025: +0.058 | 2026: -0.109
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.75, Recency ratio=0.49
- Early IC=+0.1721, Recent IC=+0.0845, 1st-half IC=+0.1203, 2nd-half IC=+0.0905, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.157, Q2=-0.025, Q3_mid=+0.136, Q4=+0.167, Q5_high_vol=+0.101

**`combo_max__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0936, Sharpe=+0.1784)
- Admission: Train IC=+0.2190, Deflated=+0.2179, IR=0.77, Mono=0.74, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.112 | 2017: +0.201 | 2018: +0.196 | 2019: +0.109 | 2020: +0.126 | 2021: +0.064 | 2022: +0.118 | 2023: +0.071 | 2024: +0.104 | 2025: +0.078 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.147 | 2017: +0.226 | 2018: +0.265 | 2019: +0.093 | 2020: +0.187 | 2021: +0.232 | 2022: +0.114 | 2023: -0.040 | 2024: +0.024 | 2025: -0.036 | 2026: +0.010
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.44
- Early IC=+0.2164, Recent IC=+0.0950, 1st-half IC=+0.2031, 2nd-half IC=+0.1281, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.106, Q3_mid=+0.176, Q4=+0.110, Q5_high_vol=+0.214

**`max_down_ret`** (Lock IC=+0.0723, Sharpe=+0.1744)
- Admission: Train IC=+0.1959, Deflated=+0.1949, IR=0.53, Mono=0.66, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.052 | 2017: +0.240 | 2018: +0.131 | 2019: +0.112 | 2020: +0.138 | 2021: +0.064 | 2022: +0.057 | 2023: +0.031 | 2024: +0.115 | 2025: +0.129 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.346 | 2016: -0.013 | 2017: +0.236 | 2018: +0.099 | 2019: +0.326 | 2020: +0.060 | 2021: +0.325 | 2022: +0.141 | 2023: +0.096 | 2024: +0.230 | 2025: +0.240 | 2026: +0.072
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.68, Recency ratio=0.46
- Early IC=+0.2182, Recent IC=+0.1012, 1st-half IC=+0.1580, 2nd-half IC=+0.1079, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.006, Q3_mid=+0.132, Q4=+0.162, Q5_high_vol=+0.198

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0497, Sharpe=+0.1716)
- Admission: Train IC=+0.2075, Deflated=+0.2074, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022 | 2022: -0.017 | 2023: -0.025 | 2024: +0.066 | 2025: +0.145 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.012 | 2017: +0.223 | 2018: +0.364 | 2019: +0.285 | 2020: +0.243 | 2021: +0.162 | 2022: -0.008 | 2023: -0.037 | 2024: +0.089 | 2025: +0.216 | 2026: +0.209
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.36
- Early IC=+0.1962, Recent IC=+0.0708, 1st-half IC=+0.1636, 2nd-half IC=+0.1081, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.009, Q3_mid=+0.200, Q4=+0.118, Q5_high_vol=+0.208

**`combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0981, Sharpe=+0.1643)
- Admission: Train IC=+0.2238, Deflated=+0.2231, IR=0.76, Mono=0.74, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.159 | 2017: +0.184 | 2018: +0.186 | 2019: +0.101 | 2020: +0.128 | 2021: +0.085 | 2022: +0.113 | 2023: +0.074 | 2024: +0.111 | 2025: +0.079 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.274 | 2017: +0.254 | 2018: +0.245 | 2019: +0.106 | 2020: +0.126 | 2021: +0.183 | 2022: +0.102 | 2023: -0.084 | 2024: +0.010 | 2025: -0.012 | 2026: +0.115
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.55
- Early IC=+0.1949, Recent IC=+0.1076, 1st-half IC=+0.2003, 2nd-half IC=+0.1292, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.100, Q3_mid=+0.181, Q4=+0.110, Q5_high_vol=+0.225

**`combo_rel_diff__early_body_momentum__h2_l2_pullback_continuation`** (Lock IC=+0.0747, Sharpe=+0.1613)
- Admission: Train IC=+0.2558, Deflated=+0.2559, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.070 | 2017: +0.120 | 2018: +0.070 | 2019: +0.048 | 2020: +0.076 | 2021: +0.034 | 2022: +0.111 | 2023: +0.099 | 2024: +0.095 | 2025: +0.116 | 2026: -0.100
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.227 | 2017: +0.051 | 2018: +0.128 | 2019: +0.224 | 2020: +0.176 | 2021: +0.205 | 2022: +0.155 | 2023: +0.162 | 2024: +0.249 | 2025: -0.035 | 2026: -0.036
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.42
- Early IC=+0.1305, Recent IC=+0.0551, 1st-half IC=+0.1220, 2nd-half IC=+0.0625, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.142, Q2=-0.025, Q3_mid=+0.165, Q4=+0.143, Q5_high_vol=+0.064

**`combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1040, Sharpe=+0.1574)
- Admission: Train IC=+0.2416, Deflated=+0.2406, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.311 | 2016: +0.099 | 2017: +0.233 | 2018: +0.155 | 2019: +0.130 | 2020: +0.171 | 2021: +0.073 | 2022: +0.120 | 2023: +0.073 | 2024: +0.102 | 2025: +0.091 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.219 | 2016: +0.180 | 2017: +0.096 | 2018: +0.101 | 2019: +0.259 | 2020: +0.186 | 2021: +0.132 | 2022: +0.068 | 2023: -0.063 | 2024: -0.023 | 2025: +0.093 | 2026: +0.074
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.48
- Early IC=+0.2550, Recent IC=+0.1222, 1st-half IC=+0.2259, 2nd-half IC=+0.1353, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.059, Q3_mid=+0.193, Q4=+0.170, Q5_high_vol=+0.253

**`combo_z_sum__max_down_ret__shaved_bar_trend_conviction`** (Lock IC=+0.0613, Sharpe=+0.1571)
- Admission: Train IC=+0.1968, Deflated=+0.1964, IR=0.46, Mono=0.67, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.025 | 2017: +0.179 | 2018: +0.117 | 2019: +0.046 | 2020: +0.125 | 2021: +0.031 | 2022: +0.010 | 2023: +0.077 | 2024: +0.093 | 2025: +0.131 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.276 | 2016: +0.005 | 2017: +0.211 | 2018: +0.077 | 2019: +0.051 | 2020: +0.142 | 2021: +0.125 | 2022: +0.116 | 2023: +0.012 | 2024: +0.238 | 2025: +0.204 | 2026: +0.038
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.41
- Early IC=+0.1933, Recent IC=+0.0783, 1st-half IC=+0.1462, 2nd-half IC=+0.0845, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.030, Q3_mid=+0.157, Q4=+0.164, Q5_high_vol=+0.135

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0870, Sharpe=+0.1569)
- Admission: Train IC=+0.2407, Deflated=+0.2396, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.035 | 2017: +0.230 | 2018: +0.096 | 2019: +0.112 | 2020: +0.112 | 2021: +0.045 | 2022: +0.060 | 2023: +0.040 | 2024: +0.101 | 2025: +0.097 | 2026: +0.108
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.149 | 2017: +0.179 | 2018: +0.256 | 2019: +0.335 | 2020: +0.235 | 2021: +0.136 | 2022: +0.072 | 2023: +0.017 | 2024: +0.243 | 2025: -0.030 | 2026: +0.132
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.45, Recency ratio=0.30
- Early IC=+0.2592, Recent IC=+0.0784, 1st-half IC=+0.2049, 2nd-half IC=+0.0916, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.058, Q3_mid=+0.119, Q4=+0.159, Q5_high_vol=+0.202

**`combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0`** (Lock IC=+0.0775, Sharpe=+0.1531)
- Admission: Train IC=+0.1962, Deflated=+0.1948, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.237 | 2018: +0.155 | 2019: +0.072 | 2020: +0.110 | 2021: +0.073 | 2022: +0.103 | 2023: +0.061 | 2024: +0.131 | 2025: +0.105 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.306 | 2016: -0.006 | 2017: +0.336 | 2018: +0.072 | 2019: +0.142 | 2020: +0.211 | 2021: +0.214 | 2022: +0.208 | 2023: +0.251 | 2024: +0.244 | 2025: +0.061 | 2026: -0.239
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.61
- Early IC=+0.1504, Recent IC=+0.0917, 1st-half IC=+0.1558, 2nd-half IC=+0.1020, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.010, Q3_mid=+0.132, Q4=+0.168, Q5_high_vol=+0.157

**`combo_rank_max__first_bar_return__shaved_bar_trend_conviction`** (Lock IC=+0.0561, Sharpe=+0.1529)
- Admission: Train IC=+0.1857, Deflated=+0.1855, IR=0.72, Mono=0.74, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.108 | 2017: +0.174 | 2018: +0.229 | 2019: +0.059 | 2020: +0.177 | 2021: +0.104 | 2022: +0.048 | 2023: +0.080 | 2024: +0.108 | 2025: +0.136 | 2026: -0.139
- Yearly Tail ICs:   2015: +0.085 | 2016: +0.009 | 2017: +0.166 | 2018: +0.252 | 2019: +0.051 | 2020: +0.274 | 2021: +0.108 | 2022: +0.279 | 2023: +0.078 | 2024: +0.157 | 2025: +0.073 | 2026: -0.361
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.79
- Early IC=+0.1774, Recent IC=+0.1397, 1st-half IC=+0.1754, 2nd-half IC=+0.1411, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.051, Q3_mid=+0.199, Q4=+0.169, Q5_high_vol=+0.198

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0820, Sharpe=+0.1525)
- Admission: Train IC=+0.2789, Deflated=+0.2777, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.096 | 2017: +0.221 | 2018: +0.246 | 2019: +0.129 | 2020: +0.134 | 2021: +0.120 | 2022: +0.069 | 2023: +0.095 | 2024: +0.157 | 2025: +0.048 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.149 | 2017: +0.233 | 2018: +0.460 | 2019: +0.103 | 2020: +0.144 | 2021: +0.272 | 2022: -0.020 | 2023: +0.116 | 2024: +0.218 | 2025: -0.197 | 2026: -0.232
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.57
- Early IC=+0.2247, Recent IC=+0.1269, 1st-half IC=+0.2070, 2nd-half IC=+0.1522, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.073, Q3_mid=+0.191, Q4=+0.187, Q5_high_vol=+0.256

**`combo_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0884, Sharpe=+0.1423)
- Admission: Train IC=+0.2269, Deflated=+0.2276, IR=0.55, Mono=0.68, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.080 | 2017: +0.147 | 2018: +0.147 | 2019: +0.067 | 2020: +0.129 | 2021: +0.015 | 2022: +0.122 | 2023: +0.077 | 2024: +0.071 | 2025: +0.096 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.074 | 2016: +0.401 | 2017: +0.109 | 2018: +0.196 | 2019: +0.121 | 2020: +0.131 | 2021: +0.142 | 2022: +0.066 | 2023: +0.077 | 2024: +0.229 | 2025: -0.029 | 2026: -0.207
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.30
- Early IC=+0.2380, Recent IC=+0.0722, 1st-half IC=+0.1960, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.014, Q3_mid=+0.193, Q4=+0.122, Q5_high_vol=+0.213

**`combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0747, Sharpe=+0.1334)
- Admission: Train IC=+0.2420, Deflated=+0.2411, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.085 | 2017: +0.218 | 2018: +0.213 | 2019: +0.091 | 2020: +0.104 | 2021: +0.101 | 2022: +0.079 | 2023: +0.098 | 2024: +0.124 | 2025: +0.095 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.055 | 2017: +0.244 | 2018: +0.360 | 2019: +0.168 | 2020: +0.131 | 2021: +0.254 | 2022: +0.098 | 2023: +0.238 | 2024: +0.205 | 2025: -0.077 | 2026: -0.369
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.47
- Early IC=+0.2182, Recent IC=+0.1021, 1st-half IC=+0.2006, 2nd-half IC=+0.1268, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.021, Q3_mid=+0.197, Q4=+0.193, Q5_high_vol=+0.208

**`star50_limit_proximity_early`** (Lock IC=+0.1151, Sharpe=+0.1331)
- Admission: Train IC=+0.2228, Deflated=+0.2216, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.058 | 2017: +0.221 | 2018: +0.079 | 2019: +0.126 | 2020: +0.089 | 2021: +0.038 | 2022: +0.083 | 2023: +0.071 | 2024: +0.110 | 2025: +0.089 | 2026: +0.185
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.217 | 2017: +0.195 | 2018: +0.226 | 2019: +0.244 | 2020: +0.168 | 2021: -0.011 | 2022: -0.111 | 2023: -0.093 | 2024: +0.027 | 2025: -0.143 | 2026: +0.360
- IC CV=0.60, Neg years (linear/tail)=0/1 of 8, Half ratio=0.42, Recency ratio=0.25
- Early IC=+0.2515, Recent IC=+0.0639, 1st-half IC=+0.2049, 2nd-half IC=+0.0865, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.086, Q3_mid=+0.137, Q4=+0.128, Q5_high_vol=+0.181

**`combo_min__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0843, Sharpe=+0.1321)
- Admission: Train IC=+0.2141, Deflated=+0.2132, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.150 | 2016: +0.035 | 2017: +0.207 | 2018: +0.093 | 2019: +0.093 | 2020: +0.095 | 2021: +0.125 | 2022: +0.086 | 2023: +0.093 | 2024: +0.122 | 2025: +0.137 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.121 | 2017: +0.201 | 2018: +0.322 | 2019: +0.262 | 2020: +0.125 | 2021: +0.290 | 2022: +0.177 | 2023: +0.252 | 2024: +0.133 | 2025: +0.203 | 2026: -0.287
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.73
- Early IC=+0.1504, Recent IC=+0.1103, 1st-half IC=+0.1479, 2nd-half IC=+0.0987, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.020, Q3_mid=+0.202, Q4=+0.149, Q5_high_vol=+0.101

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0935, Sharpe=+0.1315)
- Admission: Train IC=+0.2683, Deflated=+0.2667, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.233 | 2018: +0.106 | 2019: +0.115 | 2020: +0.101 | 2021: +0.073 | 2022: +0.081 | 2023: +0.077 | 2024: +0.080 | 2025: +0.144 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.322 | 2016: +0.097 | 2017: +0.268 | 2018: +0.350 | 2019: +0.286 | 2020: +0.182 | 2021: +0.279 | 2022: +0.119 | 2023: +0.041 | 2024: +0.169 | 2025: +0.080 | 2026: +0.197
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.35
- Early IC=+0.2485, Recent IC=+0.0870, 1st-half IC=+0.1888, 2nd-half IC=+0.0954, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.065, Q3_mid=+0.112, Q4=+0.177, Q5_high_vol=+0.178

**`combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0893, Sharpe=+0.1233)
- Admission: Train IC=+0.1911, Deflated=+0.1912, IR=0.50, Mono=0.70, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.056 | 2017: +0.156 | 2018: +0.111 | 2019: +0.085 | 2020: +0.082 | 2021: +0.012 | 2022: +0.098 | 2023: +0.086 | 2024: +0.056 | 2025: +0.101 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.038 | 2016: +0.168 | 2017: +0.092 | 2018: +0.065 | 2019: +0.254 | 2020: +0.097 | 2021: +0.079 | 2022: +0.107 | 2023: -0.077 | 2024: +0.071 | 2025: +0.044 | 2026: -0.043
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.38, Recency ratio=0.18
- Early IC=+0.2517, Recent IC=+0.0453, 1st-half IC=+0.2021, 2nd-half IC=+0.0770, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=0.88)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.041, Q3_mid=+0.186, Q4=+0.133, Q5_high_vol=+0.184

**`combo_sig_product__rsi_opening__max_down_ret`** (Lock IC=+0.0855, Sharpe=+0.1164)
- Admission: Train IC=+0.1497, Deflated=+0.1491, IR=0.59, Mono=0.71, p=0.0026, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.033 | 2017: +0.210 | 2018: +0.133 | 2019: +0.130 | 2020: +0.116 | 2021: +0.052 | 2022: +0.086 | 2023: +0.087 | 2024: +0.081 | 2025: +0.169 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.149 | 2016: -0.181 | 2017: +0.216 | 2018: +0.113 | 2019: +0.216 | 2020: +0.063 | 2021: +0.286 | 2022: +0.168 | 2023: +0.113 | 2024: +0.147 | 2025: +0.363 | 2026: -0.172
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.79, Recency ratio=0.47
- Early IC=+0.1781, Recent IC=+0.0838, 1st-half IC=+0.1409, 2nd-half IC=+0.1115, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.027, Q3_mid=+0.162, Q4=+0.168, Q5_high_vol=+0.128

**`combo_rank_max__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0796, Sharpe=+0.1132)
- Admission: Train IC=+0.2137, Deflated=+0.2133, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.115 | 2017: +0.179 | 2018: +0.194 | 2019: +0.102 | 2020: +0.110 | 2021: +0.153 | 2022: +0.111 | 2023: +0.122 | 2024: +0.124 | 2025: +0.132 | 2026: -0.140
- Yearly Tail ICs:   2015: +0.266 | 2016: -0.034 | 2017: +0.131 | 2018: +0.351 | 2019: +0.208 | 2020: +0.214 | 2021: +0.196 | 2022: +0.235 | 2023: +0.408 | 2024: +0.114 | 2025: -0.061 | 2026: -0.393
- IC CV=0.22, Neg years (linear/tail)=0/1 of 8, Half ratio=0.75, Recency ratio=0.76
- Early IC=+0.1719, Recent IC=+0.1313, 1st-half IC=+0.1780, 2nd-half IC=+0.1342, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.071, Q3_mid=+0.184, Q4=+0.138, Q5_high_vol=+0.181

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0948, Sharpe=+0.1110)
- Admission: Train IC=+0.2406, Deflated=+0.2399, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.108 | 2017: +0.201 | 2018: +0.243 | 2019: +0.105 | 2020: +0.112 | 2021: +0.099 | 2022: +0.130 | 2023: +0.076 | 2024: +0.100 | 2025: +0.084 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.207 | 2016: +0.166 | 2017: +0.233 | 2018: +0.407 | 2019: +0.078 | 2020: +0.078 | 2021: +0.292 | 2022: +0.186 | 2023: -0.056 | 2024: +0.062 | 2025: -0.020 | 2026: -0.174
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.45
- Early IC=+0.2369, Recent IC=+0.1057, 1st-half IC=+0.2150, 2nd-half IC=+0.1419, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.111, Q3_mid=+0.207, Q4=+0.132, Q5_high_vol=+0.255

**`combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.1149, Sharpe=+0.1090)
- Admission: Train IC=+0.1778, Deflated=+0.1780, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.098 | 2017: +0.168 | 2018: +0.116 | 2019: +0.128 | 2020: +0.120 | 2021: +0.027 | 2022: +0.142 | 2023: +0.099 | 2024: +0.093 | 2025: +0.138 | 2026: +0.044
- Yearly Tail ICs:   2015: +0.046 | 2016: +0.173 | 2017: +0.079 | 2018: +0.209 | 2019: +0.205 | 2020: +0.124 | 2021: +0.040 | 2022: +0.118 | 2023: +0.133 | 2024: +0.068 | 2025: +0.007 | 2026: -0.055
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.32
- Early IC=+0.2299, Recent IC=+0.0738, 1st-half IC=+0.2036, 2nd-half IC=+0.1042, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.088, Q3_mid=+0.216, Q4=+0.081, Q5_high_vol=+0.200

**`combo_clamp_diff__opening_auction_imbalance__demark_setup_reversal_early`** (Lock IC=+0.1145, Sharpe=+0.1017)
- Admission: Train IC=+0.2516, Deflated=+0.2510, IR=0.44, Mono=0.66, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.051 | 2017: +0.225 | 2018: +0.136 | 2019: +0.108 | 2020: +0.129 | 2021: +0.081 | 2022: +0.103 | 2023: +0.110 | 2024: +0.115 | 2025: +0.163 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.331 | 2016: -0.072 | 2017: +0.280 | 2018: +0.159 | 2019: +0.192 | 2020: +0.054 | 2021: +0.114 | 2022: +0.306 | 2023: +0.060 | 2024: +0.283 | 2025: +0.277 | 2026: -0.292
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.60, Recency ratio=0.47
- Early IC=+0.2255, Recent IC=+0.1050, 1st-half IC=+0.1907, 2nd-half IC=+0.1150, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.034, Q3_mid=+0.194, Q4=+0.172, Q5_high_vol=+0.176

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0726, Sharpe=+0.0928)
- Admission: Train IC=+0.2214, Deflated=+0.2206, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.015 | 2017: +0.178 | 2018: +0.261 | 2019: +0.117 | 2020: +0.168 | 2021: +0.182 | 2022: +0.103 | 2023: +0.089 | 2024: +0.113 | 2025: +0.053 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.007 | 2016: +0.163 | 2017: +0.202 | 2018: +0.528 | 2019: +0.189 | 2020: +0.178 | 2021: +0.312 | 2022: +0.005 | 2023: +0.128 | 2024: +0.134 | 2025: -0.103 | 2026: -0.122
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.28, Recency ratio=1.04
- Early IC=+0.1684, Recent IC=+0.1752, 1st-half IC=+0.1413, 2nd-half IC=+0.1804, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.056, Q3_mid=+0.198, Q4=+0.195, Q5_high_vol=+0.199

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1027, Sharpe=+0.0905)
- Admission: Train IC=+0.2081, Deflated=+0.2069, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.15
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.054 | 2017: +0.184 | 2018: +0.095 | 2019: +0.102 | 2020: +0.092 | 2021: +0.034 | 2022: +0.078 | 2023: +0.039 | 2024: +0.071 | 2025: +0.109 | 2026: +0.190
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.053 | 2017: +0.038 | 2018: +0.301 | 2019: +0.064 | 2020: +0.316 | 2021: +0.150 | 2022: -0.059 | 2023: -0.058 | 2024: -0.058 | 2025: -0.001 | 2026: +0.456
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.44, Recency ratio=0.25
- Early IC=+0.2505, Recent IC=+0.0629, 1st-half IC=+0.1983, 2nd-half IC=+0.0870, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.081, Q3_mid=+0.172, Q4=+0.099, Q5_high_vol=+0.192

**`combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.0942, Sharpe=+0.0886)
- Admission: Train IC=+0.2411, Deflated=+0.2410, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.104 | 2017: +0.135 | 2018: +0.215 | 2019: +0.065 | 2020: +0.107 | 2021: +0.043 | 2022: +0.136 | 2023: +0.074 | 2024: +0.075 | 2025: +0.092 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.148 | 2016: +0.294 | 2017: +0.172 | 2018: +0.231 | 2019: +0.145 | 2020: +0.067 | 2021: +0.213 | 2022: +0.093 | 2023: +0.099 | 2024: +0.133 | 2025: -0.057 | 2026: -0.211
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.29
- Early IC=+0.2626, Recent IC=+0.0752, 1st-half IC=+0.2114, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.046, Q3_mid=+0.211, Q4=+0.136, Q5_high_vol=+0.248

**`combo_tri_max__early_body_momentum__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0812, Sharpe=+0.0801)
- Admission: Train IC=+0.2078, Deflated=+0.2073, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.103 | 2017: +0.141 | 2018: +0.196 | 2019: +0.070 | 2020: +0.115 | 2021: +0.073 | 2022: +0.128 | 2023: +0.058 | 2024: +0.100 | 2025: +0.081 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.061 | 2017: +0.142 | 2018: +0.271 | 2019: +0.132 | 2020: +0.056 | 2021: +0.327 | 2022: +0.224 | 2023: +0.082 | 2024: +0.110 | 2025: -0.040 | 2026: -0.423
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.40
- Early IC=+0.2359, Recent IC=+0.0941, 1st-half IC=+0.2001, 2nd-half IC=+0.1167, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.071, Q3_mid=+0.205, Q4=+0.116, Q5_high_vol=+0.218

**`combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend`** (Lock IC=+0.0722, Sharpe=+0.0634)
- Admission: Train IC=+0.1925, Deflated=+0.1926, IR=0.55, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.018 | 2017: +0.158 | 2018: +0.081 | 2019: +0.049 | 2020: +0.081 | 2021: +0.055 | 2022: +0.088 | 2023: +0.105 | 2024: +0.074 | 2025: +0.147 | 2026: -0.110
- Yearly Tail ICs:   2015: +0.150 | 2016: +0.116 | 2017: +0.234 | 2018: +0.146 | 2019: +0.196 | 2020: +0.036 | 2021: +0.261 | 2022: +0.179 | 2023: +0.184 | 2024: +0.249 | 2025: +0.125 | 2026: -0.223
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.49
- Early IC=+0.1379, Recent IC=+0.0677, 1st-half IC=+0.1149, 2nd-half IC=+0.0711, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.150, Q2=-0.009, Q3_mid=+0.144, Q4=+0.137, Q5_high_vol=+0.067

**`combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.1172, Sharpe=+0.0629)
- Admission: Train IC=+0.1816, Deflated=+0.1817, IR=0.51, Mono=0.68, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.099 | 2017: +0.168 | 2018: +0.121 | 2019: +0.128 | 2020: +0.121 | 2021: +0.020 | 2022: +0.146 | 2023: +0.103 | 2024: +0.096 | 2025: +0.140 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.269 | 2017: +0.065 | 2018: +0.170 | 2019: +0.235 | 2020: +0.149 | 2021: +0.007 | 2022: +0.116 | 2023: +0.125 | 2024: +0.093 | 2025: -0.016 | 2026: -0.104
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.31
- Early IC=+0.2366, Recent IC=+0.0738, 1st-half IC=+0.2076, 2nd-half IC=+0.1046, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.094, Q3_mid=+0.217, Q4=+0.084, Q5_high_vol=+0.203

**`combo_max__first_bar_return__vwap_close_divergence_trend`** (Lock IC=+0.0807, Sharpe=+0.0624)
- Admission: Train IC=+0.2124, Deflated=+0.2120, IR=0.63, Mono=0.74, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.112 | 2017: +0.172 | 2018: +0.195 | 2019: +0.101 | 2020: +0.108 | 2021: +0.160 | 2022: +0.111 | 2023: +0.118 | 2024: +0.122 | 2025: +0.130 | 2026: -0.138
- Yearly Tail ICs:   2015: +0.278 | 2016: -0.055 | 2017: +0.110 | 2018: +0.317 | 2019: +0.223 | 2020: +0.160 | 2021: +0.200 | 2022: +0.180 | 2023: +0.414 | 2024: +0.119 | 2025: -0.084 | 2026: -0.492
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.78
- Early IC=+0.1710, Recent IC=+0.1337, 1st-half IC=+0.1767, 2nd-half IC=+0.1352, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.071, Q3_mid=+0.188, Q4=+0.139, Q5_high_vol=+0.179

**`combo_rel_diff__first_bar_return__h2_l2_pullback_continuation`** (Lock IC=+0.0713, Sharpe=+0.0500)
- Admission: Train IC=+0.2507, Deflated=+0.2504, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.096 | 2017: +0.144 | 2018: +0.147 | 2019: +0.103 | 2020: +0.089 | 2021: +0.072 | 2022: +0.091 | 2023: +0.080 | 2024: +0.117 | 2025: +0.120 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.406 | 2016: +0.015 | 2017: +0.066 | 2018: +0.346 | 2019: +0.165 | 2020: +0.055 | 2021: +0.118 | 2022: +0.230 | 2023: +0.290 | 2024: +0.276 | 2025: +0.018 | 2026: -0.368
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.44
- Early IC=+0.1827, Recent IC=+0.0805, 1st-half IC=+0.1642, 2nd-half IC=+0.1061, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.006, Q3_mid=+0.174, Q4=+0.170, Q5_high_vol=+0.165

**`combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early`** (Lock IC=+0.1075, Sharpe=+0.0484)
- Admission: Train IC=+0.1800, Deflated=+0.1793, IR=0.56, Mono=0.71, p=0.0004, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.262 | 2016: +0.025 | 2017: +0.233 | 2018: +0.087 | 2019: +0.066 | 2020: +0.060 | 2021: +0.058 | 2022: +0.087 | 2023: +0.096 | 2024: +0.101 | 2025: +0.102 | 2026: +0.107
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.044 | 2017: +0.255 | 2018: +0.014 | 2019: +0.196 | 2020: +0.038 | 2021: +0.008 | 2022: +0.106 | 2023: -0.003 | 2024: -0.029 | 2025: -0.120 | 2026: +0.226
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.34, Recency ratio=0.23
- Early IC=+0.2583, Recent IC=+0.0589, 1st-half IC=+0.2076, 2nd-half IC=+0.0711, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.078, Q3_mid=+0.150, Q4=+0.155, Q5_high_vol=+0.139

**`combo_sig_product__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0741, Sharpe=+0.0411)
- Admission: Train IC=+0.2097, Deflated=+0.2083, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.046 | 2017: +0.214 | 2018: +0.242 | 2019: +0.072 | 2020: +0.160 | 2021: +0.130 | 2022: +0.056 | 2023: +0.135 | 2024: +0.074 | 2025: +0.073 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.173 | 2016: -0.085 | 2017: +0.265 | 2018: +0.541 | 2019: +0.054 | 2020: +0.254 | 2021: +0.265 | 2022: -0.097 | 2023: +0.230 | 2024: +0.082 | 2025: +0.151 | 2026: -0.296
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.88, Recency ratio=0.74
- Early IC=+0.1970, Recent IC=+0.1450, 1st-half IC=+0.1675, 2nd-half IC=+0.1468, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.045, Q3_mid=+0.142, Q4=+0.189, Q5_high_vol=+0.195

**`combo_sig_product__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0927, Sharpe=+0.0383)
- Admission: Train IC=+0.2112, Deflated=+0.2097, IR=0.51, Mono=0.67, p=0.0000, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.084 | 2017: +0.156 | 2018: +0.024 | 2019: +0.026 | 2020: +0.090 | 2021: +0.050 | 2022: +0.121 | 2023: +0.124 | 2024: +0.092 | 2025: +0.072 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.192 | 2016: +0.114 | 2017: +0.206 | 2018: +0.129 | 2019: +0.027 | 2020: +0.246 | 2021: +0.070 | 2022: +0.091 | 2023: +0.205 | 2024: +0.180 | 2025: -0.040 | 2026: -0.314
- IC CV=0.75, Neg years (linear/tail)=0/0 of 8, Half ratio=0.24, Recency ratio=0.28
- Early IC=+0.2451, Recent IC=+0.0697, 1st-half IC=+0.2087, 2nd-half IC=+0.0507, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.057, Q3_mid=+0.194, Q4=+0.112, Q5_high_vol=+0.129

**`combo_max__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0782, Sharpe=+0.0260)
- Admission: Train IC=+0.2275, Deflated=+0.2272, IR=0.68, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.102 | 2017: +0.152 | 2018: +0.175 | 2019: +0.118 | 2020: +0.105 | 2021: +0.139 | 2022: +0.091 | 2023: +0.084 | 2024: +0.107 | 2025: +0.142 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.314 | 2016: -0.020 | 2017: +0.081 | 2018: +0.293 | 2019: +0.311 | 2020: +0.029 | 2021: +0.234 | 2022: +0.154 | 2023: +0.271 | 2024: +0.189 | 2025: +0.013 | 2026: -0.356
- IC CV=0.20, Neg years (linear/tail)=0/1 of 8, Half ratio=0.80, Recency ratio=0.71
- Early IC=+0.1717, Recent IC=+0.1220, 1st-half IC=+0.1626, 2nd-half IC=+0.1304, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.039, Q3_mid=+0.185, Q4=+0.136, Q5_high_vol=+0.183

**`combo_clamp_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`** (Lock IC=+0.0825, Sharpe=+0.0229)
- Admission: Train IC=+0.2746, Deflated=+0.2741, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.081 | 2017: +0.202 | 2018: +0.125 | 2019: +0.100 | 2020: +0.144 | 2021: +0.095 | 2022: +0.068 | 2023: +0.110 | 2024: +0.138 | 2025: +0.105 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.072 | 2017: +0.328 | 2018: +0.259 | 2019: +0.217 | 2020: +0.334 | 2021: +0.159 | 2022: +0.144 | 2023: +0.268 | 2024: +0.162 | 2025: +0.021 | 2026: -0.292
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.61
- Early IC=+0.1976, Recent IC=+0.1196, 1st-half IC=+0.1775, 2nd-half IC=+0.1208, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.025, Q3_mid=+0.211, Q4=+0.176, Q5_high_vol=+0.162

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0626, Sharpe=+0.0170)
- Admission: Train IC=+0.2196, Deflated=+0.2192, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.126 | 2017: +0.111 | 2018: +0.272 | 2019: +0.094 | 2020: +0.126 | 2021: +0.082 | 2022: +0.096 | 2023: +0.004 | 2024: +0.104 | 2025: +0.109 | 2026: -0.090
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.105 | 2017: +0.341 | 2018: +0.458 | 2019: +0.109 | 2020: +0.215 | 2021: +0.192 | 2022: +0.000 | 2023: -0.014 | 2024: +0.175 | 2025: +0.148 | 2026: -0.301
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.59
- Early IC=+0.1763, Recent IC=+0.1041, 1st-half IC=+0.1747, 2nd-half IC=+0.1410, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.001, Q3_mid=+0.156, Q4=+0.183, Q5_high_vol=+0.211

**`combo_rank_min__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0783, Sharpe=+0.0121)
- Admission: Train IC=+0.2280, Deflated=+0.2270, IR=0.65, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.031 | 2017: +0.201 | 2018: +0.091 | 2019: +0.101 | 2020: +0.083 | 2021: +0.127 | 2022: +0.066 | 2023: +0.089 | 2024: +0.121 | 2025: +0.135 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.037 | 2017: +0.160 | 2018: +0.346 | 2019: +0.324 | 2020: +0.127 | 2021: +0.302 | 2022: +0.078 | 2023: +0.087 | 2024: +0.185 | 2025: +0.150 | 2026: -0.296
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.66
- Early IC=+0.1568, Recent IC=+0.1042, 1st-half IC=+0.1496, 2nd-half IC=+0.0965, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.014, Q3_mid=+0.198, Q4=+0.143, Q5_high_vol=+0.105

**`combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1001, Sharpe=+0.0085)
- Admission: Train IC=+0.2222, Deflated=+0.2214, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.123 | 2017: +0.214 | 2018: +0.210 | 2019: +0.088 | 2020: +0.115 | 2021: +0.074 | 2022: +0.140 | 2023: +0.089 | 2024: +0.083 | 2025: +0.080 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.171 | 2016: +0.350 | 2017: +0.170 | 2018: +0.270 | 2019: +0.104 | 2020: +0.112 | 2021: +0.130 | 2022: +0.140 | 2023: -0.070 | 2024: +0.112 | 2025: -0.176 | 2026: -0.064
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.39
- Early IC=+0.2445, Recent IC=+0.0947, 1st-half IC=+0.2168, 2nd-half IC=+0.1237, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.104, Q3_mid=+0.233, Q4=+0.121, Q5_high_vol=+0.248

**`combo_sig_product__max_down_ret__close_vs_open_range`** (Lock IC=+0.0638, Sharpe=+0.0073)
- Admission: Train IC=+0.1675, Deflated=+0.1673, IR=0.60, Mono=0.74, p=0.0004, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.094 | 2017: +0.185 | 2018: +0.077 | 2019: +0.086 | 2020: +0.057 | 2021: +0.028 | 2022: +0.084 | 2023: +0.040 | 2024: +0.120 | 2025: +0.086 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.101 | 2017: +0.319 | 2018: +0.171 | 2019: +0.130 | 2020: +0.060 | 2021: +0.252 | 2022: +0.145 | 2023: +0.016 | 2024: +0.206 | 2025: -0.009 | 2026: -0.053
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.27
- Early IC=+0.1538, Recent IC=+0.0422, 1st-half IC=+0.1298, 2nd-half IC=+0.0595, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.022, Q3_mid=+0.112, Q4=+0.111, Q5_high_vol=+0.100

### 159915ETF — `single` True Positives

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1353, Sharpe=+1.4533)
- Admission: Train IC=+0.2786, Deflated=+0.2769, IR=0.60, Mono=0.71, p=0.0000, MaxCorr=0.64
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.046 | 2017: +0.008 | 2018: +0.126 | 2019: +0.234 | 2020: +0.127 | 2021: +0.140 | 2022: +0.095 | 2023: +0.183 | 2024: +0.124 | 2025: +0.180 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.076 | 2017: +0.093 | 2018: +0.365 | 2019: +0.516 | 2020: +0.321 | 2021: +0.318 | 2022: +0.378 | 2023: +0.344 | 2024: +0.314 | 2025: +0.134 | 2026: +0.442
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=0.70
- Early IC=+0.1912, Recent IC=+0.1337, 1st-half IC=+0.1403, 2nd-half IC=+0.1520, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.157, Q3_mid=+0.173, Q4=+0.149, Q5_high_vol=+0.154

**`combo_rank_min__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1307, Sharpe=+1.1856)
- Admission: Train IC=+0.2454, Deflated=+0.2432, IR=0.50, Mono=0.70, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.068 | 2017: +0.003 | 2018: +0.069 | 2019: +0.212 | 2020: +0.149 | 2021: +0.125 | 2022: +0.111 | 2023: +0.156 | 2024: +0.109 | 2025: +0.169 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.140 | 2017: +0.070 | 2018: +0.292 | 2019: +0.442 | 2020: +0.164 | 2021: +0.354 | 2022: +0.262 | 2023: +0.226 | 2024: +0.237 | 2025: +0.120 | 2026: +0.077
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.70
- Early IC=+0.1964, Recent IC=+0.1380, 1st-half IC=+0.1553, 2nd-half IC=+0.1372, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.150, Q3_mid=+0.133, Q4=+0.168, Q5_high_vol=+0.169

**`combo_z_sum__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1102, Sharpe=+1.1345)
- Admission: Train IC=+0.2018, Deflated=+0.2006, IR=0.50, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.067 | 2017: +0.045 | 2018: +0.087 | 2019: +0.175 | 2020: +0.094 | 2021: +0.153 | 2022: +0.103 | 2023: +0.196 | 2024: +0.090 | 2025: +0.175 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.113 | 2017: +0.111 | 2018: +0.238 | 2019: +0.343 | 2020: +0.202 | 2021: +0.257 | 2022: +0.308 | 2023: +0.591 | 2024: +0.212 | 2025: +0.071 | 2026: -0.059
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.71
- Early IC=+0.1753, Recent IC=+0.1237, 1st-half IC=+0.1490, 2nd-half IC=+0.1208, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.150, Q3_mid=+0.181, Q4=+0.118, Q5_high_vol=+0.155

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.1234, Sharpe=+1.0801)
- Admission: Train IC=+0.2511, Deflated=+0.2511, IR=0.76, Mono=0.81, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.106 | 2017: -0.041 | 2018: +0.150 | 2019: +0.126 | 2020: +0.143 | 2021: +0.060 | 2022: +0.185 | 2023: +0.104 | 2024: +0.057 | 2025: +0.087 | 2026: +0.183
- Yearly Tail ICs:   2015: +0.102 | 2016: +0.355 | 2017: +0.138 | 2018: +0.403 | 2019: +0.347 | 2020: +0.330 | 2021: +0.170 | 2022: +0.417 | 2023: +0.100 | 2024: +0.015 | 2025: +0.066 | 2026: +0.215
- IC CV=0.59, Neg years (linear/tail)=1/0 of 8, Half ratio=1.01, Recency ratio=0.66
- Early IC=+0.1550, Recent IC=+0.1018, 1st-half IC=+0.1189, 2nd-half IC=+0.1204, Neg regimes=1/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.13)
- Regime ICs: Q1_low_vol=-0.037, Q2=+0.123, Q3_mid=+0.108, Q4=+0.179, Q5_high_vol=+0.155

**`combo_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0966, Sharpe=+0.9984)
- Admission: Train IC=+0.2448, Deflated=+0.2434, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.133 | 2017: +0.004 | 2018: +0.112 | 2019: +0.211 | 2020: +0.115 | 2021: +0.145 | 2022: +0.059 | 2023: +0.175 | 2024: +0.078 | 2025: +0.163 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.064 | 2017: +0.117 | 2018: +0.210 | 2019: +0.410 | 2020: +0.215 | 2021: +0.200 | 2022: +0.144 | 2023: +0.338 | 2024: +0.312 | 2025: +0.262 | 2026: -0.077
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.60
- Early IC=+0.2180, Recent IC=+0.1302, 1st-half IC=+0.1601, 2nd-half IC=+0.1332, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.133, Q3_mid=+0.186, Q4=+0.080, Q5_high_vol=+0.261

**`combo_max__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0796, Sharpe=+0.9588)
- Admission: Train IC=+0.2262, Deflated=+0.2255, IR=0.63, Mono=0.70, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.113 | 2017: +0.040 | 2018: +0.116 | 2019: +0.180 | 2020: +0.172 | 2021: +0.144 | 2022: +0.079 | 2023: +0.097 | 2024: +0.069 | 2025: +0.127 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.122 | 2017: +0.016 | 2018: +0.302 | 2019: +0.315 | 2020: +0.202 | 2021: +0.333 | 2022: +0.180 | 2023: +0.275 | 2024: +0.339 | 2025: +0.090 | 2026: +0.099
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=1.01
- Early IC=+0.1559, Recent IC=+0.1578, 1st-half IC=+0.1429, 2nd-half IC=+0.1489, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.140, Q3_mid=+0.200, Q4=+0.096, Q5_high_vol=+0.207

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1119, Sharpe=+0.9423)
- Admission: Train IC=+0.2142, Deflated=+0.2127, IR=0.47, Mono=0.69, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.191 | 2024: +0.077 | 2025: +0.174 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.189 | 2016: +0.059 | 2017: +0.039 | 2018: +0.140 | 2019: +0.289 | 2020: +0.180 | 2021: +0.348 | 2022: +0.231 | 2023: +0.458 | 2024: +0.228 | 2025: +0.149 | 2026: -0.067
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.76
- Early IC=+0.1860, Recent IC=+0.1422, 1st-half IC=+0.1463, 2nd-half IC=+0.1217, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.141, Q3_mid=+0.172, Q4=+0.137, Q5_high_vol=+0.160

**`combo_z_sum__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=+0.1043, Sharpe=+0.9097)
- Admission: Train IC=+0.1793, Deflated=+0.1776, IR=0.42, Mono=0.68, p=0.0008, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.070 | 2017: +0.054 | 2018: +0.090 | 2019: +0.168 | 2020: +0.147 | 2021: +0.105 | 2022: +0.071 | 2023: +0.147 | 2024: +0.081 | 2025: +0.163 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.410 | 2016: -0.182 | 2017: +0.003 | 2018: +0.295 | 2019: +0.335 | 2020: +0.156 | 2021: +0.201 | 2022: +0.102 | 2023: +0.466 | 2024: +0.214 | 2025: +0.314 | 2026: +0.074
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.89, Recency ratio=0.76
- Early IC=+0.1654, Recent IC=+0.1262, 1st-half IC=+0.1285, 2nd-half IC=+0.1150, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.012, Q2=+0.116, Q3_mid=+0.143, Q4=+0.090, Q5_high_vol=+0.200

**`combo_rank_min__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0862, Sharpe=+0.8630)
- Admission: Train IC=+0.2336, Deflated=+0.2318, IR=0.49, Mono=0.66, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.088 | 2017: +0.086 | 2018: +0.127 | 2019: +0.164 | 2020: +0.164 | 2021: +0.080 | 2022: +0.068 | 2023: +0.154 | 2024: +0.054 | 2025: +0.113 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.401 | 2016: -0.035 | 2017: +0.103 | 2018: +0.222 | 2019: +0.310 | 2020: +0.174 | 2021: +0.307 | 2022: -0.043 | 2023: +0.350 | 2024: +0.100 | 2025: +0.430 | 2026: +0.001
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.63
- Early IC=+0.1935, Recent IC=+0.1226, 1st-half IC=+0.1559, 2nd-half IC=+0.1215, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.118, Q3_mid=+0.150, Q4=+0.103, Q5_high_vol=+0.237

**`combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend`** (Lock IC=+0.1293, Sharpe=+0.8549)
- Admission: Train IC=+0.2745, Deflated=+0.2746, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.060 | 2017: -0.048 | 2018: +0.108 | 2019: +0.092 | 2020: +0.118 | 2021: +0.032 | 2022: +0.169 | 2023: +0.129 | 2024: +0.072 | 2025: +0.118 | 2026: +0.171
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.202 | 2017: -0.006 | 2018: +0.406 | 2019: +0.261 | 2020: +0.389 | 2021: +0.229 | 2022: +0.382 | 2023: +0.121 | 2024: +0.032 | 2025: +0.088 | 2026: +0.236
- IC CV=0.74, Neg years (linear/tail)=1/1 of 8, Half ratio=1.09, Recency ratio=0.63
- Early IC=+0.1194, Recent IC=+0.0750, 1st-half IC=+0.0799, 2nd-half IC=+0.0870, Neg regimes=1/5
- Weak component: `yesterday_early_trend` (CV=1.05)
- Regime ICs: Q1_low_vol=-0.070, Q2=+0.093, Q3_mid=+0.093, Q4=+0.126, Q5_high_vol=+0.117

**`combo_z_sum__max_up_ret__rally_strength_max`** (Lock IC=+0.0798, Sharpe=+0.8355)
- Admission: Train IC=+0.1870, Deflated=+0.1858, IR=0.38, Mono=0.67, p=0.0004, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.042 | 2017: +0.052 | 2018: +0.043 | 2019: +0.166 | 2020: +0.052 | 2021: +0.184 | 2022: +0.051 | 2023: +0.141 | 2024: +0.055 | 2025: +0.182 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.139 | 2016: +0.124 | 2017: +0.097 | 2018: +0.179 | 2019: +0.297 | 2020: +0.070 | 2021: +0.249 | 2022: +0.144 | 2023: +0.410 | 2024: +0.269 | 2025: +0.217 | 2026: +0.046
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.72
- Early IC=+0.1633, Recent IC=+0.1177, 1st-half IC=+0.1380, 2nd-half IC=+0.1071, Neg regimes=1/5
- Weak component: `rally_strength_max` (CV=0.94)
- Regime ICs: Q1_low_vol=-0.017, Q2=+0.148, Q3_mid=+0.165, Q4=+0.106, Q5_high_vol=+0.140

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1032, Sharpe=+0.7807)
- Admission: Train IC=+0.2051, Deflated=+0.2042, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.099 | 2017: +0.051 | 2018: +0.122 | 2019: +0.181 | 2020: +0.122 | 2021: +0.125 | 2022: +0.098 | 2023: +0.177 | 2024: +0.077 | 2025: +0.143 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.078 | 2017: +0.126 | 2018: +0.291 | 2019: +0.274 | 2020: +0.152 | 2021: +0.304 | 2022: +0.172 | 2023: +0.521 | 2024: +0.189 | 2025: +0.145 | 2026: -0.065
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.57
- Early IC=+0.2164, Recent IC=+0.1235, 1st-half IC=+0.1739, 2nd-half IC=+0.1310, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.131, Q3_mid=+0.212, Q4=+0.092, Q5_high_vol=+0.212

**`combo_rank_min__max_up_ret__directional_volume_signature`** (Lock IC=+0.0846, Sharpe=+0.7791)
- Admission: Train IC=+0.2193, Deflated=+0.2180, IR=0.49, Mono=0.68, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.103 | 2017: +0.065 | 2018: +0.069 | 2019: +0.186 | 2020: +0.156 | 2021: +0.094 | 2022: +0.044 | 2023: +0.162 | 2024: +0.099 | 2025: +0.066 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.461 | 2016: +0.184 | 2017: +0.035 | 2018: +0.181 | 2019: +0.361 | 2020: +0.159 | 2021: +0.209 | 2022: +0.132 | 2023: +0.361 | 2024: +0.290 | 2025: +0.142 | 2026: +0.023
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.60
- Early IC=+0.2040, Recent IC=+0.1226, 1st-half IC=+0.1654, 2nd-half IC=+0.1163, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.018, Q2=+0.139, Q3_mid=+0.163, Q4=+0.089, Q5_high_vol=+0.221

**`combo_min__bar_ret_0__directional_volume_signature`** (Lock IC=+0.0798, Sharpe=+0.7556)
- Admission: Train IC=+0.1981, Deflated=+0.1973, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.139 | 2017: +0.018 | 2018: +0.076 | 2019: +0.198 | 2020: +0.146 | 2021: +0.085 | 2022: +0.064 | 2023: +0.123 | 2024: +0.112 | 2025: +0.064 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.507 | 2016: +0.113 | 2017: +0.069 | 2018: +0.059 | 2019: +0.261 | 2020: +0.236 | 2021: +0.135 | 2022: +0.127 | 2023: +0.479 | 2024: +0.296 | 2025: +0.164 | 2026: +0.081
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.57
- Early IC=+0.2033, Recent IC=+0.1156, 1st-half IC=+0.1603, 2nd-half IC=+0.1125, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.093, Q3_mid=+0.158, Q4=+0.054, Q5_high_vol=+0.247

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1034, Sharpe=+0.7543)
- Admission: Train IC=+0.2341, Deflated=+0.2333, IR=0.55, Mono=0.69, p=0.0000, MaxCorr=0.08
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.094 | 2017: +0.039 | 2018: +0.112 | 2019: +0.195 | 2020: +0.113 | 2021: +0.132 | 2022: +0.108 | 2023: +0.164 | 2024: +0.074 | 2025: +0.146 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.306 | 2016: +0.150 | 2017: +0.136 | 2018: +0.188 | 2019: +0.381 | 2020: +0.123 | 2021: +0.328 | 2022: +0.063 | 2023: +0.458 | 2024: +0.078 | 2025: +0.174 | 2026: -0.141
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.62
- Early IC=+0.1959, Recent IC=+0.1223, 1st-half IC=+0.1604, 2nd-half IC=+0.1312, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.131, Q3_mid=+0.220, Q4=+0.089, Q5_high_vol=+0.192

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0868, Sharpe=+0.7347)
- Admission: Train IC=+0.2299, Deflated=+0.2289, IR=0.49, Mono=0.66, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.091 | 2017: +0.010 | 2018: +0.154 | 2019: +0.183 | 2020: +0.127 | 2021: +0.164 | 2022: +0.070 | 2023: +0.176 | 2024: +0.003 | 2025: +0.155 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.375 | 2016: -0.155 | 2017: +0.105 | 2018: +0.276 | 2019: +0.352 | 2020: +0.229 | 2021: +0.284 | 2022: +0.189 | 2023: +0.289 | 2024: +0.118 | 2025: +0.321 | 2026: -0.117
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=1.01, Recency ratio=0.70
- Early IC=+0.2086, Recent IC=+0.1451, 1st-half IC=+0.1468, 2nd-half IC=+0.1489, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.108, Q3_mid=+0.220, Q4=+0.090, Q5_high_vol=+0.208

**`combo_max__star50_limit_proximity_early__directional_volume_signature`** (Lock IC=+0.0827, Sharpe=+0.7218)
- Admission: Train IC=+0.1634, Deflated=+0.1626, IR=0.52, Mono=0.67, p=0.0016, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.075 | 2017: -0.046 | 2018: +0.087 | 2019: +0.152 | 2020: +0.144 | 2021: +0.085 | 2022: +0.089 | 2023: +0.043 | 2024: +0.096 | 2025: +0.057 | 2026: +0.118
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.182 | 2017: -0.044 | 2018: +0.031 | 2019: +0.215 | 2020: +0.188 | 2021: +0.245 | 2022: +0.075 | 2023: +0.016 | 2024: +0.188 | 2025: -0.028 | 2026: +0.431
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=0.79, Recency ratio=0.52
- Early IC=+0.2187, Recent IC=+0.1144, 1st-half IC=+0.1512, 2nd-half IC=+0.1200, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.095, Q3_mid=+0.156, Q4=+0.127, Q5_high_vol=+0.196

**`combo_ifelse__gap_pct__max_up_ret__first_bar_return`** (Lock IC=+0.0804, Sharpe=+0.6734)
- Admission: Train IC=+0.1896, Deflated=+0.1886, IR=0.53, Mono=0.72, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.165 | 2017: +0.046 | 2018: +0.130 | 2019: +0.141 | 2020: +0.122 | 2021: +0.142 | 2022: +0.080 | 2023: +0.164 | 2024: +0.020 | 2025: +0.123 | 2026: -0.005
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.121 | 2017: +0.225 | 2018: +0.228 | 2019: +0.107 | 2020: +0.032 | 2021: +0.336 | 2022: +0.143 | 2023: +0.195 | 2024: +0.177 | 2025: +0.221 | 2026: +0.129
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.75
- Early IC=+0.1747, Recent IC=+0.1318, 1st-half IC=+0.1811, 2nd-half IC=+0.1262, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.108, Q3_mid=+0.196, Q4=+0.117, Q5_high_vol=+0.188

**`combo_rel_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0992, Sharpe=+0.6728)
- Admission: Train IC=+0.2081, Deflated=+0.2076, IR=0.39, Mono=0.65, p=0.0000, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.113 | 2017: +0.113 | 2018: +0.061 | 2019: +0.072 | 2020: +0.092 | 2021: +0.108 | 2022: +0.075 | 2023: +0.159 | 2024: +0.119 | 2025: +0.153 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.067 | 2017: +0.225 | 2018: +0.122 | 2019: +0.264 | 2020: +0.075 | 2021: +0.264 | 2022: +0.329 | 2023: +0.374 | 2024: +0.117 | 2025: +0.282 | 2026: -0.278
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.57
- Early IC=+0.1747, Recent IC=+0.0997, 1st-half IC=+0.1597, 2nd-half IC=+0.0826, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.59)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.114, Q3_mid=+0.174, Q4=+0.120, Q5_high_vol=+0.129

**`combo_z_sum__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0767, Sharpe=+0.6193)
- Admission: Train IC=+0.1597, Deflated=+0.1585, IR=0.33, Mono=0.65, p=0.0018, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.124 | 2017: +0.054 | 2018: +0.088 | 2019: +0.199 | 2020: +0.064 | 2021: +0.177 | 2022: +0.038 | 2023: +0.150 | 2024: +0.064 | 2025: +0.137 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.060 | 2016: -0.121 | 2017: +0.165 | 2018: +0.195 | 2019: +0.313 | 2020: +0.104 | 2021: +0.328 | 2022: +0.051 | 2023: +0.316 | 2024: +0.071 | 2025: +0.300 | 2026: +0.041
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.72
- Early IC=+0.1686, Recent IC=+0.1207, 1st-half IC=+0.1528, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.095, Q3_mid=+0.197, Q4=+0.084, Q5_high_vol=+0.194

**`combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1000, Sharpe=+0.6090)
- Admission: Train IC=+0.2121, Deflated=+0.2121, IR=0.41, Mono=0.70, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.163 | 2017: +0.080 | 2018: +0.106 | 2019: +0.119 | 2020: +0.083 | 2021: +0.057 | 2022: +0.088 | 2023: +0.066 | 2024: +0.123 | 2025: +0.064 | 2026: +0.134
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.397 | 2017: +0.067 | 2018: +0.160 | 2019: +0.241 | 2020: +0.050 | 2021: +0.111 | 2022: +0.287 | 2023: -0.053 | 2024: +0.179 | 2025: -0.110 | 2026: +0.095
- IC CV=0.32, Neg years (linear/tail)=0/1 of 8, Half ratio=0.70, Recency ratio=0.50
- Early IC=+0.1388, Recent IC=+0.0698, 1st-half IC=+0.1464, 2nd-half IC=+0.1019, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.206, Q3_mid=+0.093, Q4=+0.215, Q5_high_vol=+0.081

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`** (Lock IC=+0.0663, Sharpe=+0.6044)
- Admission: Train IC=+0.1992, Deflated=+0.1996, IR=0.37, Mono=0.67, p=0.0000, MaxCorr=0.45
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.169 | 2017: +0.006 | 2018: +0.087 | 2019: +0.138 | 2020: +0.131 | 2021: +0.059 | 2022: +0.068 | 2023: +0.072 | 2024: +0.069 | 2025: +0.055 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.170 | 2017: +0.174 | 2018: +0.266 | 2019: +0.204 | 2020: +0.072 | 2021: +0.175 | 2022: +0.375 | 2023: +0.032 | 2024: +0.225 | 2025: +0.053 | 2026: +0.206
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.57
- Early IC=+0.1675, Recent IC=+0.0949, 1st-half IC=+0.1647, 2nd-half IC=+0.1027, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.006, Q2=+0.152, Q3_mid=+0.155, Q4=+0.192, Q5_high_vol=+0.122

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0981, Sharpe=+0.5593)
- Admission: Train IC=+0.1953, Deflated=+0.1947, IR=0.45, Mono=0.70, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.084 | 2017: +0.059 | 2018: +0.066 | 2019: +0.171 | 2020: +0.056 | 2021: +0.225 | 2022: +0.086 | 2023: +0.158 | 2024: +0.084 | 2025: +0.172 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.028 | 2016: +0.070 | 2017: +0.235 | 2018: +0.197 | 2019: +0.295 | 2020: +0.013 | 2021: +0.395 | 2022: +0.247 | 2023: +0.299 | 2024: +0.244 | 2025: +0.188 | 2026: -0.096
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.95
- Early IC=+0.1482, Recent IC=+0.1402, 1st-half IC=+0.1353, 2nd-half IC=+0.1265, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.114, Q3_mid=+0.190, Q4=+0.126, Q5_high_vol=+0.144

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return`** (Lock IC=+0.0871, Sharpe=+0.5558)
- Admission: Train IC=+0.2238, Deflated=+0.2238, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.103 | 2017: +0.115 | 2018: +0.122 | 2019: +0.170 | 2020: +0.099 | 2021: +0.085 | 2022: +0.048 | 2023: +0.138 | 2024: +0.083 | 2025: +0.103 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.170 | 2016: +0.261 | 2017: +0.181 | 2018: +0.018 | 2019: +0.189 | 2020: +0.310 | 2021: +0.063 | 2022: +0.305 | 2023: +0.210 | 2024: +0.264 | 2025: -0.036 | 2026: +0.040
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.52
- Early IC=+0.1769, Recent IC=+0.0920, 1st-half IC=+0.1524, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.205, Q3_mid=+0.131, Q4=+0.144, Q5_high_vol=+0.114

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct`** (Lock IC=+0.0867, Sharpe=+0.5388)
- Admission: Train IC=+0.1615, Deflated=+0.1600, IR=0.65, Mono=0.73, p=0.0016, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.091 | 2017: +0.100 | 2018: +0.076 | 2019: +0.099 | 2020: +0.078 | 2021: +0.126 | 2022: +0.099 | 2023: +0.132 | 2024: +0.059 | 2025: +0.133 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.171 | 2016: +0.191 | 2017: +0.188 | 2018: +0.154 | 2019: +0.060 | 2020: +0.223 | 2021: +0.129 | 2022: +0.241 | 2023: +0.453 | 2024: +0.064 | 2025: +0.012 | 2026: -0.110
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.70
- Early IC=+0.1460, Recent IC=+0.1022, 1st-half IC=+0.1406, 2nd-half IC=+0.0913, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.006, Q2=+0.130, Q3_mid=+0.146, Q4=+0.149, Q5_high_vol=+0.120

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0971, Sharpe=+0.5001)
- Admission: Train IC=+0.2227, Deflated=+0.2218, IR=0.54, Mono=0.71, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.144 | 2017: +0.039 | 2018: +0.090 | 2019: +0.169 | 2020: +0.123 | 2021: +0.182 | 2022: +0.108 | 2023: +0.161 | 2024: +0.076 | 2025: +0.169 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.110 | 2017: +0.210 | 2018: +0.248 | 2019: +0.210 | 2020: +0.075 | 2021: +0.384 | 2022: +0.277 | 2023: +0.376 | 2024: +0.081 | 2025: +0.270 | 2026: -0.199
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.80
- Early IC=+0.1907, Recent IC=+0.1517, 1st-half IC=+0.1714, 2nd-half IC=+0.1325, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.139, Q3_mid=+0.211, Q4=+0.105, Q5_high_vol=+0.189

**`combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return`** (Lock IC=+0.0866, Sharpe=+0.4695)
- Admission: Train IC=+0.2177, Deflated=+0.2177, IR=0.56, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.204 | 2017: +0.088 | 2018: +0.105 | 2019: +0.135 | 2020: +0.105 | 2021: +0.057 | 2022: +0.055 | 2023: +0.102 | 2024: +0.095 | 2025: +0.081 | 2026: +0.066
- Yearly Tail ICs:   2015: +0.093 | 2016: +0.379 | 2017: +0.122 | 2018: +0.113 | 2019: +0.299 | 2020: +0.090 | 2021: +0.155 | 2022: +0.319 | 2023: +0.162 | 2024: +0.301 | 2025: -0.048 | 2026: +0.192
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.58
- Early IC=+0.1390, Recent IC=+0.0810, 1st-half IC=+0.1664, 2nd-half IC=+0.0967, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.198, Q3_mid=+0.100, Q4=+0.190, Q5_high_vol=+0.105

**`combo_max__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=+0.0775, Sharpe=+0.4352)
- Admission: Train IC=+0.2045, Deflated=+0.2036, IR=0.49, Mono=0.72, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.090 | 2017: +0.027 | 2018: +0.098 | 2019: +0.190 | 2020: +0.183 | 2021: +0.138 | 2022: +0.030 | 2023: +0.116 | 2024: +0.058 | 2025: +0.144 | 2026: -0.005
- Yearly Tail ICs:   2015: +0.492 | 2016: -0.168 | 2017: +0.062 | 2018: +0.204 | 2019: +0.388 | 2020: +0.268 | 2021: +0.164 | 2022: -0.036 | 2023: +0.094 | 2024: +0.262 | 2025: +0.133 | 2026: +0.162
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.02, Recency ratio=0.86
- Early IC=+0.1857, Recent IC=+0.1603, 1st-half IC=+0.1414, 2nd-half IC=+0.1438, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.163, Q3_mid=+0.206, Q4=+0.062, Q5_high_vol=+0.220

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend`** (Lock IC=+0.0625, Sharpe=+0.3953)
- Admission: Train IC=+0.2130, Deflated=+0.2130, IR=0.45, Mono=0.66, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.104 | 2017: +0.070 | 2018: +0.157 | 2019: +0.162 | 2020: +0.113 | 2021: +0.082 | 2022: +0.063 | 2023: +0.094 | 2024: +0.061 | 2025: +0.074 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.174 | 2017: +0.152 | 2018: +0.178 | 2019: +0.095 | 2020: +0.256 | 2021: +0.213 | 2022: +0.254 | 2023: +0.217 | 2024: +0.231 | 2025: +0.012 | 2026: +0.084
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.51
- Early IC=+0.1922, Recent IC=+0.0972, 1st-half IC=+0.1567, 2nd-half IC=+0.1259, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.183, Q3_mid=+0.148, Q4=+0.166, Q5_high_vol=+0.145

**`combo_min__bar_ret_0__volume_price_confirmation`** (Lock IC=+0.0793, Sharpe=+0.3066)
- Admission: Train IC=+0.2142, Deflated=+0.2129, IR=0.47, Mono=0.67, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.115 | 2017: +0.041 | 2018: +0.125 | 2019: +0.178 | 2020: +0.127 | 2021: +0.083 | 2022: +0.079 | 2023: +0.118 | 2024: +0.055 | 2025: +0.110 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.516 | 2016: -0.027 | 2017: +0.092 | 2018: +0.121 | 2019: +0.341 | 2020: +0.136 | 2021: +0.304 | 2022: -0.004 | 2023: +0.443 | 2024: +0.115 | 2025: +0.224 | 2026: +0.235
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.76, Recency ratio=0.56
- Early IC=+0.1893, Recent IC=+0.1053, 1st-half IC=+0.1511, 2nd-half IC=+0.1151, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.073, Q3_mid=+0.169, Q4=+0.056, Q5_high_vol=+0.249

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend`** (Lock IC=+0.0575, Sharpe=+0.3011)
- Admission: Train IC=+0.2057, Deflated=+0.2056, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.198 | 2017: +0.034 | 2018: +0.140 | 2019: +0.127 | 2020: +0.119 | 2021: +0.041 | 2022: +0.069 | 2023: +0.050 | 2024: +0.080 | 2025: +0.055 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.249 | 2016: +0.296 | 2017: +0.143 | 2018: +0.274 | 2019: +0.344 | 2020: +0.063 | 2021: +0.116 | 2022: +0.288 | 2023: +0.095 | 2024: +0.270 | 2025: +0.007 | 2026: +0.199
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.50
- Early IC=+0.1589, Recent IC=+0.0801, 1st-half IC=+0.1719, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.016, Q2=+0.166, Q3_mid=+0.119, Q4=+0.220, Q5_high_vol=+0.138

**`combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration`** (Lock IC=+0.0867, Sharpe=+0.2295)
- Admission: Train IC=+0.2287, Deflated=+0.2280, IR=0.49, Mono=0.67, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.131 | 2017: +0.005 | 2018: +0.166 | 2019: +0.216 | 2020: +0.139 | 2021: +0.110 | 2022: +0.088 | 2023: +0.136 | 2024: +0.063 | 2025: +0.127 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.090 | 2017: +0.075 | 2018: +0.256 | 2019: +0.490 | 2020: +0.015 | 2021: +0.194 | 2022: +0.307 | 2023: +0.183 | 2024: +0.129 | 2025: +0.319 | 2026: -0.248
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.64
- Early IC=+0.1960, Recent IC=+0.1247, 1st-half IC=+0.1475, 2nd-half IC=+0.1440, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.104, Q3_mid=+0.229, Q4=+0.068, Q5_high_vol=+0.235

**`combo_rel_diff__directional_volume_signature__early_late_momentum_divergence`** (Lock IC=+0.0815, Sharpe=+0.2239)
- Admission: Train IC=+0.1884, Deflated=+0.1879, IR=0.51, Mono=0.70, p=0.0004, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.080 | 2017: -0.020 | 2018: +0.051 | 2019: +0.204 | 2020: +0.151 | 2021: +0.019 | 2022: +0.045 | 2023: +0.100 | 2024: +0.102 | 2025: +0.020 | 2026: +0.163
- Yearly Tail ICs:   2015: +0.477 | 2016: +0.027 | 2017: +0.102 | 2018: +0.041 | 2019: +0.260 | 2020: +0.222 | 2021: -0.001 | 2022: -0.097 | 2023: +0.084 | 2024: +0.090 | 2025: -0.039 | 2026: +0.425
- IC CV=0.79, Neg years (linear/tail)=1/1 of 8, Half ratio=0.86, Recency ratio=0.50
- Early IC=+0.1692, Recent IC=+0.0849, 1st-half IC=+0.1116, 2nd-half IC=+0.0965, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.062, Q3_mid=+0.167, Q4=+0.017, Q5_high_vol=+0.222

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0725, Sharpe=+0.1878)
- Admission: Train IC=+0.1703, Deflated=+0.1692, IR=0.33, Mono=0.67, p=0.0012, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.162 | 2017: +0.008 | 2018: +0.135 | 2019: +0.197 | 2020: +0.110 | 2021: +0.134 | 2022: +0.058 | 2023: +0.150 | 2024: +0.061 | 2025: +0.114 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.213 | 2016: -0.007 | 2017: +0.182 | 2018: +0.264 | 2019: +0.189 | 2020: +0.132 | 2021: +0.304 | 2022: +0.034 | 2023: +0.403 | 2024: +0.123 | 2025: +0.229 | 2026: +0.031
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.74, Recency ratio=0.60
- Early IC=+0.2039, Recent IC=+0.1224, 1st-half IC=+0.1782, 2nd-half IC=+0.1316, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.098, Q3_mid=+0.176, Q4=+0.078, Q5_high_vol=+0.242

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.0962, Sharpe=+0.1554)
- Admission: Train IC=+0.2222, Deflated=+0.2215, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.139 | 2017: +0.040 | 2018: +0.098 | 2019: +0.183 | 2020: +0.123 | 2021: +0.175 | 2022: +0.109 | 2023: +0.160 | 2024: +0.075 | 2025: +0.171 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.128 | 2017: +0.206 | 2018: +0.213 | 2019: +0.228 | 2020: +0.105 | 2021: +0.374 | 2022: +0.296 | 2023: +0.363 | 2024: +0.112 | 2025: +0.238 | 2026: -0.161
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.79
- Early IC=+0.1879, Recent IC=+0.1491, 1st-half IC=+0.1682, 2nd-half IC=+0.1357, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.138, Q3_mid=+0.218, Q4=+0.102, Q5_high_vol=+0.184

**`combo_diff__first_bar_return__volume_weighted_momentum_acceleration`** (Lock IC=+0.0855, Sharpe=+0.1420)
- Admission: Train IC=+0.1912, Deflated=+0.1903, IR=0.48, Mono=0.66, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.104 | 2017: +0.029 | 2018: +0.156 | 2019: +0.213 | 2020: +0.119 | 2021: +0.121 | 2022: +0.085 | 2023: +0.152 | 2024: +0.071 | 2025: +0.114 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.220 | 2016: -0.021 | 2017: +0.150 | 2018: +0.196 | 2019: +0.285 | 2020: +0.015 | 2021: +0.362 | 2022: -0.048 | 2023: +0.496 | 2024: +0.103 | 2025: +0.292 | 2026: +0.154
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.59
- Early IC=+0.2045, Recent IC=+0.1199, 1st-half IC=+0.1623, 2nd-half IC=+0.1350, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.058, Q2=+0.104, Q3_mid=+0.218, Q4=+0.063, Q5_high_vol=+0.233

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1093 | +0.0576 | +0.1489 | 2y |
| `star50_limit_proximity_early` | TP | persistent | +0.0972 | +0.0305 | +0.1399 | 1y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0871 | +0.0406 | +0.0559 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0837 | +0.1070 | +0.0151 | 2y |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.0669 | +0.1304 | -0.0477 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0644 | +0.1302 | -0.0846 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | TP | gradual | +0.0608 | +0.1284 | -0.1048 | 4y |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | TP | gradual | +0.0538 | +0.1786 | -0.2003 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.0503 | +0.1659 | -0.0327 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0482 | +0.1698 | +0.0210 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0450 | +0.1396 | -0.0262 | 4y |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | TP | gradual | +0.0446 | +0.1980 | -0.2513 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | TP | gradual | +0.0437 | +0.1274 | -0.0798 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.0417 | +0.1852 | -0.2047 | 4y |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | TP | gradual | +0.0400 | +0.1616 | -0.0066 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0362 | +0.1364 | -0.0309 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0349 | +0.1760 | -0.0233 | 4y |
| `combo_tri_min__max_up_ret__bar_body_rng_0__limit_down_proximity_early` | TP | gradual | +0.0347 | +0.1571 | -0.0055 | 4y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0334 | +0.1355 | +0.0408 | ∞ |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Median | gradual | +0.0283 | +0.1374 | -0.1401 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0270 | +0.1416 | -0.0496 | 4y |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Median | gradual | +0.0251 | +0.1565 | -0.2083 | 4y |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0196 | +0.1285 | -0.0556 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0123 | +0.1391 | -0.0821 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | TP | immediate | -0.0004 | +0.1518 | -0.1926 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Median | immediate | -0.0056 | +0.1508 | -0.2008 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=0, gradual=18, persistent=6

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.1567 | +0.0778 | -0.0384 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1547 | +0.0903 | +0.0992 | ∞ |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.1502 | +0.0780 | -0.0324 | 3y |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.1488 | +0.0980 | -0.0980 | 4y |
| `combo_min__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.1460 | +0.1102 | -0.1199 | 4y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.1459 | +0.1008 | +0.0498 | 4y |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | TP | gradual | +0.1430 | +0.0668 | -0.1106 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.1416 | +0.0986 | +0.0435 | 4y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1405 | +0.0964 | +0.1432 | 3y |
| `combo_rank_max__opening_auction_imbalance__star50_limit_proximity_early` | TP | persistent | +0.1386 | +0.0796 | +0.0711 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1379 | +0.0837 | +0.1523 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1375 | +0.0887 | +0.0863 | ∞ |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | TP | persistent | +0.1362 | +0.0740 | +0.0467 | 4y |
| `combo_tri_max__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | TP | persistent | +0.1313 | +0.0505 | +0.0137 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | TP | gradual | +0.1310 | +0.0857 | -0.0858 | 4y |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.1305 | +0.0848 | -0.0432 | 4y |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1304 | +0.0790 | +0.0293 | 4y |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | TP | gradual | +0.1304 | +0.0809 | -0.0556 | 4y |
| `combo_max__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.1303 | +0.0813 | -0.0538 | 4y |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1303 | +0.0761 | +0.0125 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__rsi_opening` | TP | gradual | +0.1299 | +0.1164 | -0.0452 | 4y |
| `combo_max__rsi_opening__early_order_flow_imbalance` | TP | gradual | +0.1296 | +0.0695 | -0.0930 | 4y |
| `combo_tri_max__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | TP | gradual | +0.1284 | +0.0584 | -0.0198 | 1y |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | TP | gradual | +0.1273 | +0.0887 | -0.0612 | 4y |
| `combo_min__max_up_ret__opening_auction_imbalance` | TP | gradual | +0.1269 | +0.1126 | -0.0875 | 4y |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | TP | gradual | +0.1266 | +0.1142 | -0.0693 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1263 | +0.0980 | -0.0147 | 4y |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1250 | +0.1210 | -0.0622 | 4y |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1244 | +0.0720 | +0.0822 | ∞ |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1228 | +0.1054 | -0.0686 | 4y |
| `combo_max__first_bar_return__close_vs_open_range` | TP | gradual | +0.1222 | +0.0859 | -0.1187 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.1216 | +0.0766 | +0.0456 | 4y |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | TP | gradual | +0.1210 | +0.0731 | -0.1008 | 4y |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | TP | gradual | +0.1207 | +0.0723 | -0.0984 | 4y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1206 | +0.1240 | +0.0345 | 4y |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1204 | +0.0728 | +0.0813 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1203 | +0.0633 | +0.0591 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__opening_auction_imbalance` | TP | gradual | +0.1191 | +0.1078 | -0.0142 | 4y |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.1189 | +0.1343 | +0.0255 | 4y |
| `combo_rank_min__volatility_expansion_trend_vector__early_order_flow_imbalance` | TP | gradual | +0.1189 | +0.1060 | -0.1141 | 4y |
| `combo_max__max_up_ret__close_vs_open_range` | TP | gradual | +0.1189 | +0.0977 | -0.0377 | 4y |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1188 | +0.0761 | +0.1180 | ∞ |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | TP | gradual | +0.1188 | +0.1367 | -0.1041 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | TP | gradual | +0.1187 | +0.0804 | -0.0163 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.1181 | +0.1235 | +0.0025 | 4y |
| `combo_max__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1177 | +0.0714 | +0.0503 | 4y |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1163 | +0.1339 | +0.0611 | ∞ |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1163 | +0.1291 | -0.0499 | 4y |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1159 | +0.0795 | -0.0337 | 4y |
| `combo_sig_product__first_bar_return__vwap_close_divergence_trend` | Median | gradual | +0.1151 | +0.1186 | -0.1116 | 3y |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1150 | +0.1443 | -0.0507 | 3y |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | TP | gradual | +0.1148 | +0.0624 | -0.0624 | 4y |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | TP | gradual | +0.1146 | +0.0923 | -0.0883 | 4y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.1127 | +0.0834 | +0.0494 | 4y |
| `combo_min__max_up_ret__max_down_ret` | TP | gradual | +0.1126 | +0.1054 | -0.0038 | 4y |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1122 | +0.1145 | -0.0892 | 4y |
| `combo_max__early_body_momentum__star50_limit_proximity_early` | TP | persistent | +0.1118 | +0.0689 | +0.0526 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__opening_auction_imbalance__smooth_momentum_structure` | TP | gradual | +0.1116 | +0.0647 | -0.0975 | 4y |
| `combo_rel_diff__early_body_momentum__h2_l2_pullback_continuation` | TP | gradual | +0.1115 | +0.0995 | -0.0996 | 4y |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | TP | gradual | +0.1113 | +0.1032 | -0.1197 | 4y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | Median | persistent | +0.1113 | +0.0582 | +0.0432 | 4y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1111 | +0.0724 | +0.0623 | ∞ |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1111 | +0.1128 | -0.0782 | 4y |
| `combo_tri_max__max_up_ret__volatility_expansion_trend_vector__early_body_momentum` | TP | gradual | +0.1110 | +0.0890 | -0.0479 | 4y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.1109 | +0.0952 | -0.0850 | 4y |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | TP | gradual | +0.1107 | +0.1177 | -0.1381 | 4y |
| `combo_tri_median__max_up_ret__early_body_momentum__star50_limit_proximity_early` | TP | gradual | +0.1106 | +0.0910 | -0.0276 | 4y |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1105 | +0.0844 | -0.0245 | 4y |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | TP | gradual | +0.1103 | +0.1229 | -0.1430 | 4y |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | TP | gradual | +0.1095 | +0.0746 | -0.0600 | 4y |
| `combo_mean__max_up_ret__close_vs_open_range` | TP | gradual | +0.1091 | +0.1040 | -0.0693 | 4y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1088 | +0.1278 | +0.0510 | 4y |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1084 | +0.1169 | -0.0689 | 4y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | TP | gradual | +0.1083 | +0.0822 | -0.1558 | 4y |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1076 | +0.0999 | -0.0717 | 4y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1066 | +0.1435 | +0.0382 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | TP | gradual | +0.1061 | +0.0725 | -0.0246 | 4y |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1060 | +0.0577 | +0.2076 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1059 | +0.0733 | -0.0265 | 4y |
| `combo_rank_max__max_up_ret__opening_auction_imbalance` | TP | gradual | +0.1050 | +0.0970 | -0.0136 | 4y |
| `combo_mean__max_up_ret__max_down_ret` | TP | gradual | +0.1048 | +0.0934 | -0.0393 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__trend_day_regime_conviction` | TP | gradual | +0.1046 | +0.0884 | -0.0817 | 4y |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | TP | gradual | +0.1035 | +0.0764 | -0.0725 | 4y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1034 | +0.0853 | +0.1336 | ∞ |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | TP | gradual | +0.1033 | +0.0996 | -0.0806 | 4y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.1032 | +0.0831 | +0.0445 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1032 | +0.0892 | -0.0731 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | TP | gradual | +0.1028 | +0.0610 | -0.0825 | 4y |
| `combo_clamp_diff__opening_auction_imbalance__demark_setup_reversal_early` | TP | persistent | +0.1028 | +0.1103 | +0.0207 | 4y |
| `combo_mean__opening_auction_imbalance__close_vs_open_range` | TP | gradual | +0.1015 | +0.0881 | -0.0784 | 4y |
| `combo_mean__max_up_ret__first_bar_return` | TP | gradual | +0.1010 | +0.0957 | -0.0531 | 4y |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | TP | persistent | +0.1008 | +0.0907 | +0.0116 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | gradual | +0.1001 | +0.1147 | -0.0069 | 4y |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | TP | persistent | +0.0999 | +0.0731 | +0.1134 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0999 | +0.0865 | +0.0821 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | TP | gradual | +0.0997 | +0.1123 | -0.0156 | 4y |
| `combo_max__early_body_momentum__close_vs_open_range` | Median | gradual | +0.0997 | +0.0776 | -0.0998 | 4y |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | TP | gradual | +0.0996 | +0.1172 | -0.0683 | 4y |
| `combo_max__trend_bar_close_consistency__bar_body_rng_0` | TP | gradual | +0.0995 | +0.0921 | -0.1090 | 4y |
| `combo_rank_min__trend_bar_close_consistency__close_vs_open_range` | TP | gradual | +0.0994 | +0.0819 | -0.0874 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0985 | +0.0664 | +0.1105 | ∞ |
| `combo_rank_min__early_body_momentum__max_down_ret` | TP | gradual | +0.0985 | +0.0762 | -0.0127 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0982 | +0.1121 | +0.0222 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | TP | persistent | +0.0979 | +0.0527 | +0.1074 | ∞ |
| `combo_tri_mean__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early` | TP | persistent | +0.0976 | +0.0703 | +0.0190 | 4y |
| `combo_min__rsi_opening__close_vs_open_range` | TP | gradual | +0.0975 | +0.0791 | -0.0803 | 4y |
| `combo_max__first_bar_return__early_order_flow_imbalance` | Median | gradual | +0.0975 | +0.0703 | -0.1538 | 4y |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.0971 | +0.1295 | +0.0283 | 4y |
| `combo_max__opening_drive_thrust_ratio__first_bar_return` | Median | gradual | +0.0971 | +0.1060 | -0.0617 | 4y |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Median | gradual | +0.0969 | +0.0923 | -0.0844 | 4y |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.0966 | +0.1155 | +0.1718 | ∞ |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0393 | 1y |
| `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | TP | gradual | +0.0964 | +0.1000 | -0.0700 | 4y |
| `combo_sig_product__max_up_ret__first_bar_return` | TP | gradual | +0.0963 | +0.0044 | -0.0902 | 1y |
| `combo_mean__first_bar_return__rsi_opening` | TP | gradual | +0.0960 | +0.0749 | -0.0699 | 4y |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.0960 | +0.1077 | -0.0344 | 4y |
| `combo_mean__bar_ret_0__close_vs_open_range` | TP | gradual | +0.0958 | +0.0793 | -0.0656 | 4y |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0957 | +0.0362 | +0.1265 | 1y |
| `max_up_ret` | TP | gradual | +0.0954 | +0.1044 | -0.0295 | 4y |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | persistent | +0.0940 | +0.1234 | +0.0488 | ∞ |
| `open_to_current_return` | TP | gradual | +0.0940 | +0.0954 | -0.1207 | 4y |
| `combo_max__opening_auction_imbalance__first_bar_return` | Median | gradual | +0.0937 | +0.0733 | -0.0964 | 4y |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | TP | gradual | +0.0933 | +0.0978 | -0.0900 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0931 | +0.0349 | +0.1076 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | TP | persistent | +0.0929 | +0.1241 | +0.0479 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.0928 | +0.0763 | +0.0295 | 4y |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.0926 | +0.1274 | +0.0335 | 4y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0921 | +0.0793 | +0.2001 | ∞ |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0919 | +0.0483 | +0.0909 | ∞ |
| `combo_mean__first_bar_return__vwap_close_divergence_trend` | TP | gradual | +0.0919 | +0.0895 | -0.0898 | 4y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.0919 | +0.1109 | +0.1613 | ∞ |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | TP | gradual | +0.0910 | +0.0803 | -0.1121 | 4y |
| `combo_max__vwap_close_divergence_trend__bar_body_rng_0` | TP | gradual | +0.0907 | +0.0844 | -0.0983 | 4y |
| `combo_mean__opening_auction_imbalance__bar_body_rng_0` | TP | gradual | +0.0907 | +0.0854 | -0.0431 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0907 | +0.0845 | +0.0719 | ∞ |
| `combo_mean__opening_auction_imbalance__max_down_ret` | TP | gradual | +0.0906 | +0.0766 | -0.0299 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | TP | gradual | +0.0905 | +0.1077 | -0.0540 | 4y |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | Median | gradual | +0.0904 | +0.0815 | -0.1589 | 4y |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | Median | gradual | +0.0903 | +0.1015 | -0.0904 | 4y |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | TP | gradual | +0.0903 | +0.0990 | -0.0832 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | TP | gradual | +0.0901 | +0.0998 | -0.0637 | 4y |
| `combo_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.0901 | +0.1113 | +0.1742 | ∞ |
| `combo_min__opening_auction_imbalance__first_bar_return` | TP | gradual | +0.0895 | +0.0813 | -0.0234 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__early_body_momentum__star50_limit_proximity_early` | TP | persistent | +0.0894 | +0.0785 | +0.0350 | 4y |
| `combo_min__opening_auction_imbalance__vwap_close_divergence_trend` | TP | gradual | +0.0893 | +0.1038 | -0.0609 | 4y |
| `combo_sig_product__max_up_ret__early_body_momentum` | TP | persistent | +0.0893 | +0.1136 | +0.0099 | 4y |
| `combo_mean__opening_auction_imbalance__star50_limit_proximity_early` | TP | persistent | +0.0892 | +0.0578 | +0.0902 | ∞ |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | persistent | +0.0890 | +0.1265 | +0.0532 | ∞ |
| `combo_min__max_up_ret__close_vs_open_range` | TP | gradual | +0.0887 | +0.1007 | -0.0741 | 4y |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | TP | gradual | +0.0885 | +0.1033 | -0.0923 | 4y |
| `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` | TP | gradual | +0.0883 | +0.1052 | -0.1097 | 4y |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | TP | persistent | +0.0879 | +0.0754 | +0.0110 | 4y |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0875 | +0.0998 | -0.0527 | 4y |
| `combo_min__max_down_ret__close_vs_open_range` | TP | gradual | +0.0874 | +0.0861 | -0.0012 | 4y |
| `combo_max__bar_ret_0__max_down_ret` | TP | gradual | +0.0871 | +0.0455 | -0.0519 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | TP | persistent | +0.0867 | +0.0961 | +0.1067 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0866 | +0.0841 | +0.0488 | ∞ |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | TP | gradual | +0.0865 | +0.0999 | -0.0863 | 4y |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.0862 | +0.0897 | -0.0799 | 4y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__opening_auction_imbalance` | TP | gradual | +0.0858 | +0.1270 | -0.0748 | 4y |
| `combo_min__max_up_ret__first_bar_return` | TP | gradual | +0.0858 | +0.0928 | -0.0252 | 4y |
| `combo_sig_product__rsi_opening__max_down_ret` | TP | gradual | +0.0858 | +0.0875 | -0.0246 | 4y |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0857 | +0.1126 | -0.0342 | 4y |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.0856 | +0.0929 | -0.0797 | 4y |
| `combo_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0851 | +0.0337 | +0.1257 | 1y |
| `combo_sig_product__opening_auction_imbalance__close_vs_open_range` | TP | gradual | +0.0846 | +0.1001 | -0.0717 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | TP | gradual | +0.0846 | +0.0962 | -0.0335 | 4y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | TP | gradual | +0.0843 | +0.0902 | -0.0437 | 4y |
| `combo_sig_product__max_down_ret__close_vs_open_range` | TP | gradual | +0.0842 | +0.0400 | -0.1092 | 1y |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | TP | gradual | +0.0832 | +0.0806 | -0.0030 | 4y |
| `combo_max__max_up_ret__bar_ret_0` | TP | gradual | +0.0827 | +0.0796 | -0.0813 | 4y |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.0827 | +0.1201 | +0.0311 | 4y |
| `star50_limit_proximity_early` | TP | persistent | +0.0825 | +0.0715 | +0.1849 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0822 | +0.0710 | +0.0875 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0814 | +0.0771 | +0.0840 | ∞ |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | TP | gradual | +0.0811 | +0.0771 | -0.0223 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0807 | +0.0887 | +0.0006 | 4y |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.0804 | +0.1004 | -0.0517 | 4y |
| `combo_rank_max__opening_auction_imbalance__max_down_ret` | TP | gradual | +0.0803 | +0.0441 | -0.0631 | 4y |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0800 | +0.0797 | +0.0711 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__late_bar_momentum` | TP | persistent | +0.0798 | +0.0997 | +0.1942 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0796 | +0.0881 | +0.0354 | 4y |
| `combo_rank_max__max_up_ret__max_down_ret` | TP | gradual | +0.0795 | +0.0589 | -0.0053 | 4y |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.0794 | +0.0980 | -0.0670 | 4y |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | TP | gradual | +0.0793 | +0.0906 | -0.0111 | 4y |
| `combo_clamp_diff__first_bar_return__h2_l2_pullback_continuation` | TP | gradual | +0.0792 | +0.0980 | -0.0837 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0790 | +0.1128 | +0.0375 | 4y |
| `combo_rank_max__max_down_ret__bar_body_rng_0` | TP | persistent | +0.0781 | +0.0280 | +0.0146 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0778 | +0.0797 | +0.0101 | 4y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0776 | +0.0056 | +0.0300 | 1y |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | TP | gradual | +0.0775 | +0.1065 | -0.0552 | 4y |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0775 | +0.0385 | +0.1895 | 1y |
| `combo_max__max_up_ret__max_down_ret` | TP | gradual | +0.0775 | +0.0566 | -0.0328 | 4y |
| `combo_max__max_down_ret__bar_body_rng_0` | TP | gradual | +0.0773 | +0.0535 | -0.0110 | 4y |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0768 | +0.0861 | -0.0275 | 4y |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | TP | gradual | +0.0765 | +0.0961 | -0.0841 | 4y |
| `combo_mean__max_down_ret__close_vs_open_range` | TP | gradual | +0.0764 | +0.0693 | -0.0381 | 4y |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | TP | gradual | +0.0755 | +0.0948 | -0.0823 | 4y |
| `combo_tri_median__opening_auction_imbalance__star50_limit_proximity_early__bar_ret_0` | TP | gradual | +0.0754 | +0.0816 | -0.0265 | 4y |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0753 | +0.0818 | +0.0095 | 4y |
| `combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early` | TP | persistent | +0.0746 | +0.1035 | +0.0710 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0742 | +0.0585 | +0.1303 | ∞ |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | TP | gradual | +0.0735 | +0.0839 | -0.0470 | 4y |
| `combo_rank_min__max_up_ret__max_down_ret` | TP | gradual | +0.0734 | +0.0882 | -0.0105 | 4y |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | TP | gradual | +0.0734 | +0.0877 | -0.0652 | 4y |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | TP | gradual | +0.0730 | +0.0925 | -0.0567 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | TP | gradual | +0.0721 | +0.1311 | -0.0392 | 4y |
| `combo_mean__bar_ret_0__max_down_ret` | TP | gradual | +0.0720 | +0.0548 | -0.0374 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance` | TP | persistent | +0.0706 | +0.0909 | +0.0930 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0697 | +0.0925 | -0.0211 | 4y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0696 | +0.0975 | +0.1515 | ∞ |
| `opening_drive_thrust_ratio` | TP | gradual | +0.0695 | +0.1017 | -0.0223 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.0690 | +0.0948 | -0.0137 | 4y |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.0686 | +0.0836 | -0.0426 | 4y |
| `combo_clamp_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | TP | gradual | +0.0684 | +0.1102 | -0.0725 | 4y |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0678 | +0.0740 | +0.1093 | ∞ |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | TP | gradual | +0.0676 | +0.0626 | -0.0222 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0669 | +0.0666 | +0.1530 | ∞ |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | TP | gradual | +0.0668 | +0.0895 | -0.0115 | 4y |
| `vwap_trend_channel_slope` | TP | gradual | +0.0667 | +0.1186 | -0.0323 | 4y |
| `combo_min__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.0666 | +0.0802 | -0.0357 | 4y |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | gradual | +0.0665 | +0.1025 | -0.0752 | 4y |
| `combo_rank_min__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.0660 | +0.1203 | -0.0694 | 4y |
| `combo_rank_min__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.0657 | +0.0856 | -0.0766 | 4y |
| `combo_max__trend_day_regime_conviction__max_down_ret` | TP | gradual | +0.0656 | +0.0515 | -0.0687 | 4y |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0654 | +0.1035 | +0.0828 | 3y |
| `combo_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | TP | gradual | +0.0647 | +0.0989 | -0.0113 | 4y |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0647 | +0.0833 | +0.0983 | ∞ |
| `combo_diff__bar_ret_0__late_bar_momentum` | TP | persistent | +0.0641 | +0.0654 | +0.0840 | 3y |
| `combo_clamp_diff__first_bar_return__late_bar_momentum` | TP | persistent | +0.0633 | +0.0627 | +0.0863 | 3y |
| `first_bar_return` | TP | gradual | +0.0630 | +0.0618 | -0.0544 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__vwap_close_divergence_trend` | TP | gradual | +0.0627 | +0.1286 | -0.0589 | 4y |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.0627 | +0.0669 | -0.0406 | 4y |
| `combo_rank_max__max_down_ret__close_vs_open_range` | TP | gradual | +0.0615 | +0.0409 | -0.0710 | 4y |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | TP | gradual | +0.0609 | +0.0721 | -0.0319 | 4y |
| `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0608 | +0.0762 | +0.0911 | ∞ |
| `combo_max__early_body_momentum__max_down_ret` | Median | gradual | +0.0604 | +0.0409 | -0.0937 | 4y |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0599 | +0.1194 | -0.0397 | 4y |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0596 | +0.0404 | +0.1077 | ∞ |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.0585 | +0.0445 | -0.0836 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | TP | persistent | +0.0584 | +0.1000 | +0.0645 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0578 | +0.0626 | +0.0799 | ∞ |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0575 | +0.0932 | +0.1058 | 3y |
| `max_down_ret` | TP | gradual | +0.0567 | +0.0309 | -0.0023 | 4y |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | TP | gradual | +0.0560 | +0.0953 | -0.0151 | 4y |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | TP | gradual | +0.0560 | +0.1079 | -0.0617 | 4y |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | TP | gradual | +0.0560 | +0.0601 | -0.0266 | 4y |
| `combo_sig_product__max_up_ret__max_down_ret` | TP | persistent | +0.0559 | +0.1194 | +0.0031 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.0558 | +0.1349 | +0.0030 | 4y |
| `combo_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | TP | gradual | +0.0554 | +0.0754 | -0.0742 | 4y |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.0551 | +0.1011 | +0.0624 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | gradual | +0.0546 | +0.0650 | -0.0226 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0543 | +0.0664 | +0.2371 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.0542 | +0.0933 | -0.0177 | 4y |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | TP | persistent | +0.0540 | +0.0886 | +0.0381 | ∞ |
| `combo_sig_product__opening_auction_imbalance__first_bar_return` | Median | gradual | +0.0534 | +0.0705 | -0.0571 | 4y |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.0529 | +0.1002 | -0.0100 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0518 | +0.1044 | +0.1349 | ∞ |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | TP | gradual | +0.0517 | +0.0908 | -0.0139 | 4y |
| `combo_rel_diff__first_bar_return__body_size_progression` | TP | persistent | +0.0513 | +0.0695 | +0.0606 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0487 | +0.0899 | +0.1130 | ∞ |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0487 | +0.0619 | +0.1536 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0477 | +0.0594 | +0.1530 | ∞ |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0475 | +0.0772 | +0.1102 | ∞ |
| `combo_min__max_down_ret__bar_body_rng_0` | TP | gradual | +0.0468 | +0.0570 | -0.0236 | 4y |
| `combo_rank_max__first_bar_return__shaved_bar_trend_conviction` | TP | gradual | +0.0466 | +0.0797 | -0.1426 | 4y |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.0465 | +0.1098 | -0.0570 | 4y |
| `combo_min__trend_bar_close_consistency__star50_limit_proximity_early` | TP | persistent | +0.0457 | +0.0901 | +0.0653 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | gradual | +0.0457 | +0.1028 | -0.0160 | 4y |
| `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | persistent | +0.0450 | +0.0985 | +0.0971 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | TP | persistent | +0.0447 | +0.0866 | +0.0828 | ∞ |
| `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0` | TP | gradual | +0.0445 | +0.0883 | -0.0276 | 4y |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | TP | persistent | +0.0441 | +0.0801 | +0.0837 | ∞ |
| `combo_min__bar_ret_0__close_vs_open_range` | TP | gradual | +0.0436 | +0.0685 | -0.0041 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.0435 | +0.1006 | +0.0677 | ∞ |
| `combo_rank_min__bar_ret_0__close_vs_open_range` | TP | gradual | +0.0434 | +0.0682 | -0.0068 | 4y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0427 | +0.1132 | +0.0378 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0423 | +0.0974 | +0.1233 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | TP | persistent | +0.0419 | +0.0764 | +0.0246 | ∞ |
| `combo_diff__star50_limit_proximity_early__late_bar_momentum` | TP | persistent | +0.0406 | +0.0454 | +0.2772 | 3y |
| `combo_min__first_bar_return__max_down_ret` | TP | gradual | +0.0398 | +0.0536 | -0.0232 | 4y |
| `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum` | TP | persistent | +0.0397 | +0.0454 | +0.2785 | 3y |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | TP | persistent | +0.0389 | +0.0946 | +0.0266 | ∞ |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | TP | gradual | +0.0383 | +0.0548 | -0.0064 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.0381 | +0.0941 | +0.1047 | ∞ |
| `combo_mean__bar_ret_0__shaved_bar_trend_conviction` | TP | gradual | +0.0381 | +0.0832 | -0.0709 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0380 | +0.0806 | +0.0634 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0376 | +0.1050 | +0.0156 | 4y |
| `combo_mean__volatility_expansion_trend_vector__shaved_bar_trend_conviction` | TP | gradual | +0.0366 | +0.0915 | -0.0780 | 4y |
| `combo_min__close_vs_open_range__bar_body_rng_0` | TP | gradual | +0.0361 | +0.0808 | -0.0193 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0360 | +0.1081 | +0.1491 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0354 | +0.0820 | +0.0819 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0348 | +0.0631 | +0.0923 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0346 | +0.0775 | +0.0682 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | TP | persistent | +0.0333 | +0.0965 | +0.0987 | ∞ |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0328 | +0.0837 | +0.0616 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0317 | +0.1018 | +0.1044 | ∞ |
| `combo_rel_diff__first_bar_return__early_late_momentum_divergence` | TP | persistent | +0.0308 | +0.0701 | +0.0649 | ∞ |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | TP | gradual | +0.0289 | +0.1211 | -0.0685 | 4y |
| `combo_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0281 | +0.0650 | +0.1005 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__late_bar_momentum` | TP | persistent | +0.0278 | +0.0559 | +0.2620 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | TP | gradual | +0.0262 | +0.0982 | -0.0550 | 4y |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | TP | persistent | +0.0218 | +0.0840 | +0.0550 | ∞ |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | TP | gradual | +0.0167 | +0.1284 | -0.0675 | 4y |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0166 | +0.0991 | +0.1132 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0144 | +0.1081 | +0.0874 | ∞ |
| `combo_z_sum__max_down_ret__shaved_bar_trend_conviction` | TP | gradual | +0.0096 | +0.0769 | -0.0441 | ∞ |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0090 | +0.0675 | +0.0861 | ∞ |
| `combo_min__bar_ret_0__shaved_bar_trend_conviction` | TP | gradual | +0.0068 | +0.0899 | -0.0056 | ∞ |
| `combo_rank_min__max_down_ret__shaved_bar_trend_conviction` | TP | gradual | +0.0053 | +0.0618 | -0.0195 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Median | persistent | +0.0006 | +0.0060 | +0.1359 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | immediate | -0.0035 | +0.0761 | +0.0828 | ∞ |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | TP | immediate | -0.0146 | +0.0148 | +0.0841 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | TP | immediate | -0.0149 | +0.0736 | +0.0824 | ∞ |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | TP | immediate | -0.0168 | -0.0247 | +0.1029 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | TP | immediate | -0.0247 | +0.0929 | +0.0648 | ∞ |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | Median | immediate | -0.0560 | +0.0066 | +0.0848 | ∞ |

**Decay distribution**: immediate=6, fast(1-2y)=0, gradual=182, persistent=129

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.1850 | +0.1037 | +0.1834 | 2y |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | TP | persistent | +0.1691 | +0.1287 | +0.1707 | 2y |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__bar_ret_0` | Median | persistent | +0.1284 | +0.1159 | +0.0743 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1167 | +0.1912 | -0.0577 | 4y |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1105 | +0.1585 | +0.0862 | ∞ |
| `combo_max__max_up_ret__first_bar_return` | TP | gradual | +0.1089 | +0.1605 | -0.0870 | 4y |
| `combo_rank_max__max_up_ret__bar_ret_0` | TP | gradual | +0.1081 | +0.1617 | -0.0791 | 4y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.1081 | +0.1637 | -0.0170 | 4y |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1033 | +0.1956 | -0.0614 | 4y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | TP | gradual | +0.0986 | +0.1321 | -0.0546 | 4y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.0975 | +0.1768 | -0.0059 | 4y |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0947 | +0.1830 | +0.0707 | ∞ |
| `combo_max__star50_limit_proximity_early__directional_volume_signature` | TP | persistent | +0.0890 | +0.0425 | +0.1179 | 1y |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0884 | +0.0657 | +0.1344 | ∞ |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | TP | gradual | +0.0878 | +0.1356 | -0.0238 | 4y |
| `combo_max__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.0864 | +0.1584 | -0.0759 | 4y |
| `combo_diff__first_bar_return__volume_weighted_momentum_acceleration` | TP | gradual | +0.0853 | +0.1515 | -0.0133 | 4y |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | TP | gradual | +0.0799 | +0.1638 | -0.0049 | 2y |
| `combo_min__bar_ret_0__volume_price_confirmation` | TP | persistent | +0.0793 | +0.1180 | +0.0092 | 4y |
| `combo_max__max_up_ret__volume_price_confirmation` | TP | gradual | +0.0785 | +0.0971 | -0.0161 | 4y |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | TP | gradual | +0.0753 | +0.1588 | -0.0572 | 4y |
| `combo_z_sum__volatility_expansion_trend_vector__volume_price_confirmation` | TP | persistent | +0.0710 | +0.1474 | +0.0087 | 4y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0697 | +0.1760 | -0.0164 | 2y |
| `combo_rank_min__max_up_ret__volume_price_confirmation` | TP | persistent | +0.0692 | +0.1556 | +0.0336 | 4y |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | TP | persistent | +0.0688 | +0.0500 | +0.0031 | 4y |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | TP | persistent | +0.0684 | +0.0716 | +0.0492 | ∞ |
| `combo_min__bar_ret_0__directional_volume_signature` | TP | persistent | +0.0638 | +0.1228 | +0.0297 | 4y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | TP | gradual | +0.0626 | +0.0944 | -0.0003 | 4y |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.0587 | +0.1751 | -0.0495 | 4y |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | gradual | +0.0583 | +0.1498 | -0.0387 | 4y |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | TP | persistent | +0.0546 | +0.1017 | +0.0656 | ∞ |
| `combo_z_sum__max_up_ret__rally_strength_max` | TP | gradual | +0.0508 | +0.1410 | -0.0837 | 4y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | TP | persistent | +0.0484 | +0.1377 | +0.0527 | ∞ |
| `combo_rel_diff__directional_volume_signature__early_late_momentum_divergence` | TP | persistent | +0.0452 | +0.1003 | +0.1627 | 3y |
| `combo_rank_min__max_up_ret__directional_volume_signature` | TP | persistent | +0.0442 | +0.1614 | +0.0696 | ∞ |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | TP | gradual | +0.0378 | +0.1504 | -0.0499 | 4y |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | TP | gradual | +0.0303 | +0.1156 | -0.0048 | 4y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=20, persistent=17

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 14/20 top rejects are profitable (70%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1978, Lock IC=+0.0618, Sharpe=+0.5778
- `combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.2090, Lock IC=+0.0555, Sharpe=+0.4984
- `combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__first_bar_return`: Train IC=+0.2088, Lock IC=+0.0555, Sharpe=+0.4984

**B2 Rolling Guard**: 5/20 top rejects are profitable (25%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.1926, Lock IC=+0.0621, Sharpe=+0.4231
- `combo_min__max_up_ret__bar_body_rng_0`: Train IC=+0.2075, Lock IC=+0.0484, Sharpe=+0.3431
- `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`: Train IC=+0.1944, Lock IC=+0.0452, Sharpe=+0.2091

**Temporal Validation Gate**: 13/20 top rejects are profitable (65%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.2249, Lock IC=+0.0621, Sharpe=+0.3608
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.2249, Lock IC=+0.0621, Sharpe=+0.3608
- `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.2471, Lock IC=+0.0639, Sharpe=+0.3064

**BH-FDR Gate**: 2/6 top rejects are profitable (33%)

- `combo_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1188, Lock IC=+0.0545, Sharpe=+0.2629
- `combo_z_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1188, Lock IC=+0.0545, Sharpe=+0.2629

**B3 Composite Floor**: 5/9 top rejects are profitable (56%)

- `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.1595, Lock IC=+0.0710, Sharpe=+0.3157
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.1642, Lock IC=+0.0656, Sharpe=+0.2961
- `combo_rank_min__opening_drive_thrust_ratio__first_bar_return`: Train IC=+0.1444, Lock IC=+0.0426, Sharpe=+0.0825

**B6 Yearly IC CV Gate**: 14/20 top rejects are profitable (70%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1757, Lock IC=+0.0618, Sharpe=+0.9516
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1750, Lock IC=+0.0585, Sharpe=+0.3823
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1750, Lock IC=+0.0585, Sharpe=+0.3823

**B4 Correlation Gate**: 17/20 top rejects are profitable (85%)

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2178, Lock IC=+0.0801, Sharpe=+0.5979
- `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2510, Lock IC=+0.0744, Sharpe=+0.4687
- `combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.2245, Lock IC=+0.0670, Sharpe=+0.4460

### 500ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2686, Lock IC=+0.0737, Sharpe=+1.2837
- `combo_mean__late_bar_momentum__demark_setup_reversal_early`: Train IC=+0.2417, Lock IC=+0.1133, Sharpe=+1.1369
- `combo_z_sum__late_bar_momentum__demark_setup_reversal_early`: Train IC=+0.2417, Lock IC=+0.1133, Sharpe=+1.1369

**B2 Rolling Guard**: 18/20 top rejects are profitable (90%)

- `combo_clamp_diff__demark_setup_reversal_early__close_vs_open_range`: Train IC=+0.2348, Lock IC=+0.1230, Sharpe=+1.2725
- `combo_diff__first_bar_return__body_size_progression`: Train IC=+0.1968, Lock IC=+0.0709, Sharpe=+0.6177
- `combo_z_diff__first_bar_return__body_size_progression`: Train IC=+0.1968, Lock IC=+0.0709, Sharpe=+0.6177

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_clamp_diff__demark_setup_reversal_early__bar_body_rng_0`: Train IC=+0.3075, Lock IC=+0.1089, Sharpe=+0.8604
- `combo_rel_diff__smooth_momentum_structure__rsi_opening`: Train IC=+0.2972, Lock IC=+0.0807, Sharpe=+0.8333
- `combo_rel_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2972, Lock IC=+0.0807, Sharpe=+0.8333

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2922, Lock IC=+0.1024, Sharpe=+0.7641
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__opening_auction_imbalance`: Train IC=+0.3212, Lock IC=+0.0946, Sharpe=+0.6751
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`: Train IC=+0.3212, Lock IC=+0.0946, Sharpe=+0.6751

**B6 Yearly IC CV Gate**: 14/17 top rejects are profitable (82%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.2425, Lock IC=+0.0705, Sharpe=+0.4988
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.2425, Lock IC=+0.0705, Sharpe=+0.4988
- `combo_rel_diff__max_up_ret__shaved_bar_trend_conviction`: Train IC=+0.2182, Lock IC=+0.0351, Sharpe=+0.4537

**B6 Temporal Stability Gate**: 14/16 top rejects are profitable (88%)

- `combo_rank_max__opening_auction_imbalance__bar_body_rng_0`: Train IC=+0.2575, Lock IC=+0.0761, Sharpe=+0.6670
- `combo_rank_max__net_volume_flow__bar_body_rng_0`: Train IC=+0.2575, Lock IC=+0.0761, Sharpe=+0.6670
- `combo_max__opening_auction_imbalance__bar_body_rng_0`: Train IC=+0.2758, Lock IC=+0.0774, Sharpe=+0.6487

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_rel_diff__opening_auction_imbalance__smooth_momentum_structure`: Train IC=+0.3185, Lock IC=+0.0771, Sharpe=+1.1722
- `combo_rel_diff__net_volume_flow__smooth_momentum_structure`: Train IC=+0.3185, Lock IC=+0.0771, Sharpe=+1.1722
- `combo_diff__opening_auction_imbalance__smooth_momentum_structure`: Train IC=+0.3187, Lock IC=+0.0896, Sharpe=+1.0879

### 159915ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2183, Lock IC=+0.1101, Sharpe=+1.5894
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2323, Lock IC=+0.1125, Sharpe=+1.3963
- `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2354, Lock IC=+0.1143, Sharpe=+1.2029

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2355, Lock IC=+0.1283, Sharpe=+1.3766
- `combo_tri_z_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2355, Lock IC=+0.1283, Sharpe=+1.3766
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2589, Lock IC=+0.1248, Sharpe=+1.2066

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2578, Lock IC=+0.1347, Sharpe=+1.5841
- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2559, Lock IC=+0.1353, Sharpe=+1.4035
- `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2533, Lock IC=+0.1238, Sharpe=+1.3668

**BH-FDR Gate**: 10/10 top rejects are profitable (100%)

- `net_volume_flow`: Train IC=+0.1096, Lock IC=+0.1057, Sharpe=+0.8587
- `opening_auction_imbalance`: Train IC=+0.1096, Lock IC=+0.1057, Sharpe=+0.8587
- `close_vs_open_range`: Train IC=+0.0811, Lock IC=+0.1116, Sharpe=+0.8258

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2754, Lock IC=+0.1108, Sharpe=+1.4111
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2664, Lock IC=+0.1302, Sharpe=+1.3509
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`: Train IC=+0.2489, Lock IC=+0.1242, Sharpe=+1.2631

**B6 Yearly IC CV Gate**: 1/5 top rejects are profitable (20%)

- `combo_ifelse__gap_pct__yesterday_first_30min_return__yesterday_early_trend`: Train IC=+0.1665, Lock IC=+0.0594, Sharpe=+0.0824

**B4 Correlation Gate**: 16/19 top rejects are profitable (84%)

- `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`: Train IC=+0.2624, Lock IC=+0.1117, Sharpe=+1.1560
- `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation`: Train IC=+0.1838, Lock IC=+0.0840, Sharpe=+1.1150
- `combo_tri_min__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2608, Lock IC=+0.1195, Sharpe=+1.0466

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1236 | 78 | 28 | 28 | 22 | 36% | 28% |
| B2 Rolling Guard | 214 | 78 | 22 | 32 | 24 | 28% | 31% |
| Temporal Validation Gate | 223 | 78 | 2 | 37 | 39 | 3% | 50% |
| BH-FDR Gate | 6 | 6 | 1 | 3 | 2 | 17% | 33% |
| B3 Composite Floor | 9 | 9 | 1 | 3 | 5 | 11% | 56% |
| B6 Yearly IC CV Gate | 20 | 20 | 0 | 6 | 14 | 0% | 70% |
| B4 Correlation Gate | 44 | 44 | 0 | 3 | 41 | 0% | 93% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1847, Lock IC=+0.0629, Sharpe=+0.5998
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1847, Lock IC=+0.0629, Sharpe=+0.5998
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1978, Lock IC=+0.0618, Sharpe=+0.5778

**B2 Rolling Guard** — top TP casualties:
- `combo_sig_product__star50_limit_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1336, Lock IC=+0.0696, Sharpe=+0.9008
- `combo_diff__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=+0.1352, Lock IC=+0.0462, Sharpe=+0.5020
- `combo_z_diff__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=+0.1352, Lock IC=+0.0462, Sharpe=+0.5020

**Temporal Validation Gate** — top TP casualties:
- `combo_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1720, Lock IC=+0.0660, Sharpe=+0.5615
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1720, Lock IC=+0.0660, Sharpe=+0.5615
- `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1722, Lock IC=+0.0531, Sharpe=+0.4980

**BH-FDR Gate** — top TP casualties:
- `combo_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1188, Lock IC=+0.0545, Sharpe=+0.2629
- `combo_z_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1188, Lock IC=+0.0545, Sharpe=+0.2629

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.1595, Lock IC=+0.0710, Sharpe=+0.3157
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.1642, Lock IC=+0.0656, Sharpe=+0.2961
- `combo_rank_min__opening_drive_thrust_ratio__first_bar_return`: Train IC=+0.1444, Lock IC=+0.0426, Sharpe=+0.0825

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1757, Lock IC=+0.0618, Sharpe=+0.9516
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1750, Lock IC=+0.0585, Sharpe=+0.3823
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1750, Lock IC=+0.0585, Sharpe=+0.3823

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1905, Lock IC=+0.0734, Sharpe=+0.7659
- `combo_mean__max_up_ret__volume_weighted_price_position`: Train IC=+0.2044, Lock IC=+0.0477, Sharpe=+0.6200
- `combo_z_sum__max_up_ret__volume_weighted_price_position`: Train IC=+0.2044, Lock IC=+0.0477, Sharpe=+0.6200

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2306 | 78 | 25 | 22 | 31 | 32% | 40% |
| B2 Rolling Guard | 304 | 78 | 27 | 12 | 39 | 35% | 50% |
| Temporal Validation Gate | 214 | 78 | 14 | 13 | 51 | 18% | 65% |
| BH-FDR Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 406 | 78 | 5 | 5 | 68 | 6% | 87% |
| B6 Yearly IC CV Gate | 17 | 17 | 2 | 1 | 14 | 12% | 82% |
| B6 Temporal Stability Gate | 16 | 16 | 0 | 2 | 14 | 0% | 88% |
| B4 Correlation Gate | 978 | 78 | 0 | 1 | 77 | 0% | 99% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2686, Lock IC=+0.0737, Sharpe=+1.2837
- `combo_mean__late_bar_momentum__demark_setup_reversal_early`: Train IC=+0.2417, Lock IC=+0.1133, Sharpe=+1.1369
- `combo_z_sum__late_bar_momentum__demark_setup_reversal_early`: Train IC=+0.2417, Lock IC=+0.1133, Sharpe=+1.1369

**B2 Rolling Guard** — top TP casualties:
- `combo_clamp_diff__demark_setup_reversal_early__close_vs_open_range`: Train IC=+0.2348, Lock IC=+0.1230, Sharpe=+1.2725
- `combo_clamp_diff__demark_setup_reversal_early__shaved_bar_trend_conviction`: Train IC=+0.1935, Lock IC=+0.1004, Sharpe=+0.9403
- `combo_diff__first_bar_return__body_size_progression`: Train IC=+0.1968, Lock IC=+0.0709, Sharpe=+0.6177

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__demark_setup_reversal_early__bar_body_rng_0`: Train IC=+0.2255, Lock IC=+0.1133, Sharpe=+1.0486
- `combo_z_diff__demark_setup_reversal_early__bar_body_rng_0`: Train IC=+0.2255, Lock IC=+0.1133, Sharpe=+1.0486
- `combo_rel_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2869, Lock IC=+0.0849, Sharpe=+0.8610

**B3 Composite Floor** — top TP casualties:
- `combo_min__opening_auction_imbalance__shaved_bar_trend_conviction`: Train IC=+0.2236, Lock IC=+0.0650, Sharpe=+1.1331
- `combo_min__net_volume_flow__shaved_bar_trend_conviction`: Train IC=+0.2236, Lock IC=+0.0650, Sharpe=+1.1331
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2225, Lock IC=+0.0304, Sharpe=+0.9896

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.2425, Lock IC=+0.0705, Sharpe=+0.4988
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.2425, Lock IC=+0.0705, Sharpe=+0.4988
- `combo_rel_diff__max_up_ret__shaved_bar_trend_conviction`: Train IC=+0.2182, Lock IC=+0.0351, Sharpe=+0.4537

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_rank_max__opening_auction_imbalance__bar_body_rng_0`: Train IC=+0.2575, Lock IC=+0.0761, Sharpe=+0.6670
- `combo_rank_max__net_volume_flow__bar_body_rng_0`: Train IC=+0.2575, Lock IC=+0.0761, Sharpe=+0.6670
- `combo_max__opening_auction_imbalance__bar_body_rng_0`: Train IC=+0.2758, Lock IC=+0.0774, Sharpe=+0.6487

**B4 Correlation Gate** — top TP casualties:
- `combo_rel_diff__opening_auction_imbalance__smooth_momentum_structure`: Train IC=+0.3185, Lock IC=+0.0771, Sharpe=+1.1722
- `combo_rel_diff__net_volume_flow__smooth_momentum_structure`: Train IC=+0.3185, Lock IC=+0.0771, Sharpe=+1.1722
- `combo_diff__opening_auction_imbalance__smooth_momentum_structure`: Train IC=+0.3187, Lock IC=+0.0896, Sharpe=+1.0879

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2019 | 78 | 20 | 14 | 44 | 26% | 56% |
| B2 Rolling Guard | 448 | 78 | 19 | 6 | 53 | 24% | 68% |
| Temporal Validation Gate | 190 | 78 | 3 | 3 | 72 | 4% | 92% |
| BH-FDR Gate | 10 | 10 | 0 | 0 | 10 | 0% | 100% |
| B3 Composite Floor | 247 | 78 | 0 | 9 | 69 | 0% | 88% |
| B6 Yearly IC CV Gate | 5 | 5 | 3 | 1 | 1 | 60% | 20% |
| B4 Correlation Gate | 19 | 19 | 0 | 3 | 16 | 0% | 84% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2183, Lock IC=+0.1101, Sharpe=+1.5894
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2323, Lock IC=+0.1125, Sharpe=+1.3963
- `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2354, Lock IC=+0.1143, Sharpe=+1.2029

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2355, Lock IC=+0.1283, Sharpe=+1.3766
- `combo_tri_z_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2355, Lock IC=+0.1283, Sharpe=+1.3766
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2169, Lock IC=+0.1255, Sharpe=+1.3241

**Temporal Validation Gate** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2254, Lock IC=+0.1252, Sharpe=+1.5884
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2254, Lock IC=+0.1252, Sharpe=+1.5884
- `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2578, Lock IC=+0.1347, Sharpe=+1.5841

**BH-FDR Gate** — top TP casualties:
- `net_volume_flow`: Train IC=+0.1096, Lock IC=+0.1057, Sharpe=+0.8587
- `opening_auction_imbalance`: Train IC=+0.1096, Lock IC=+0.1057, Sharpe=+0.8587
- `close_vs_open_range`: Train IC=+0.0811, Lock IC=+0.1116, Sharpe=+0.8258

**B3 Composite Floor** — top TP casualties:
- `combo_min__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2754, Lock IC=+0.1108, Sharpe=+1.4111
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2664, Lock IC=+0.1302, Sharpe=+1.3509
- `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2346, Lock IC=+0.1251, Sharpe=+1.3052

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`: Train IC=+0.2624, Lock IC=+0.1117, Sharpe=+1.1560
- `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation`: Train IC=+0.1838, Lock IC=+0.0840, Sharpe=+1.1150
- `combo_tri_min__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2608, Lock IC=+0.1195, Sharpe=+1.0466

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (223 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 90 | 50 | 12 | 13 | 25 | 24% | 26% |
| recency_ratio >= 2.5 (late-concentrated) | 127 | 50 | 0 | 45 | 5 | 0% | 90% |

**Top TP killed by recency_ratio cap:**
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.2130, Lock IC=+0.0672, Sharpe=+0.4918
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.2130, Lock IC=+0.0672, Sharpe=+0.4918
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.2130, Lock IC=+0.0672, Sharpe=+0.4918
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.2130, Lock IC=+0.0672, Sharpe=+0.4918
- `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1939, Lock IC=+0.0625, Sharpe=+0.4379

### 500ETF — `single` (214 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 207 | 50 | 0 | 49 | 1 | 0% | 98% |
| recency_ratio >= 2.5 (late-concentrated) | 4 | 4 | 0 | 0 | 4 | 0% | 0% |

### 159915ETF — `single` (190 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 48 | 48 | 2 | 44 | 2 | 4% | 92% |
| recency_ratio >= 2.5 (late-concentrated) | 130 | 50 | 0 | 50 | 0 | 0% | 100% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2425, Lock IC=+0.1336, Sharpe=+1.6068
- `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2578, Lock IC=+0.1347, Sharpe=+1.5841
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2477, Lock IC=+0.1309, Sharpe=+1.3944
- `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2533, Lock IC=+0.1238, Sharpe=+1.3668
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2670, Lock IC=+0.1202, Sharpe=+1.3587

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volatility_expansion_trend_vector` | 0 | 29 | 29 | 0% |  |
| `vwap_close_divergence_trend` | 0 | 32 | 32 | 0% |  |
| `early_order_flow_imbalance` | 0 | 16 | 16 | 0% |  |
| `shaved_bar_trend_conviction` | 0 | 20 | 20 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 17 | 17 | 0% |  |
| `limit_down_proximity_early` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 62 | 62 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 2 | 2 | 0% |  |
| `bar_body_rng_0` | 0 | 37 | 37 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 88 | 88 | 0% |  |
| `body_size_progression` | 0 | 5 | 5 | 0% |  |
| `trend_day_regime_conviction` | 0 | 7 | 7 | 0% |  |
| `volume_price_confirmation` | 0 | 5 | 5 | 0% |  |
| `yesterday_first_30min_return` | 0 | 5 | 5 | 0% |  |
| `rsi_opening` | 0 | 5 | 5 | 0% |  |
| `first_bar_return` | 0 | 31 | 31 | 0% |  |
| `opening_auction_imbalance` | 0 | 21 | 21 | 0% |  |
| `close_vs_open_range` | 0 | 29 | 29 | 0% |  |
| `late_bar_momentum` | 0 | 7 | 7 | 0% |  |
| `bar_ret_0` | 0 | 54 | 54 | 0% |  |
| `early_body_momentum` | 0 | 21 | 21 | 0% |  |
| `demark_setup_reversal_early` | 0 | 11 | 11 | 0% |  |
| `max_up_ret` | 0 | 107 | 107 | 0% |  |
| `gap_pct` | 0 | 9 | 9 | 0% |  |
| `early_late_momentum_divergence` | 0 | 4 | 4 | 0% |  |
| `max_down_ret` | 0 | 46 | 46 | 0% |  |
| `directional_volume_signature` | 0 | 4 | 4 | 0% |  |
| `h2_l2_pullback_continuation` | 0 | 13 | 13 | 0% |  |
| `smooth_momentum_structure` | 0 | 5 | 5 | 0% |  |
| `volume_weighted_price_position` | 0 | 6 | 6 | 0% |  |
| `star50_limit_proximity_early` | 0 | 60 | 60 | 0% |  |
| `trend_bar_close_consistency` | 0 | 11 | 11 | 0% |  |
| `yesterday_early_trend` | 0 | 3 | 3 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=186, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=0, TP=44, FP rate=0%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=67, FP rate=0%

