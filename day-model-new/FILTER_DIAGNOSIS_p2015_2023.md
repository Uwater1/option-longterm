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
| 300ETF | single | 47 | 17 | `[12, 5, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (17 clusters)]` | 0.1935 | 0 | 6 | 41 | 0% | 0.73 |
| 500ETF | single | 297 | 104 | `[18, 18, 13, 13, 12, 12, 11, 10, 8, 5, 4, 3, ... (104 clusters)]` | 0.2266 | 1 | 24 | 272 | 0% | 0.84 |
| 159915ETF | single | 77 | 39 | `[4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, ... (39 clusters)]` | 0.2979 | 1 | 0 | 76 | 1% | 0.90 |

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

### 500ETF — `single` False Positives

**`combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction`** (Lock IC=-0.0030, Sharpe=+0.5284)
- Admission: Train IC=+0.1999, Deflated=+0.1997, IR=0.64, Mono=0.76, p=0.0000, MaxCorr=0.46
- Yearly Linear ICs: 2015: +0.093 | 2016: +0.143 | 2017: -0.079 | 2018: +0.108 | 2019: +0.135 | 2020: -0.014 | 2021: +0.098 | 2022: +0.103 | 2023: -0.003 | 2024: +0.080 | 2025: -0.115 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.336 | 2017: -0.015 | 2018: +0.271 | 2019: +0.264 | 2020: +0.228 | 2021: +0.212 | 2022: +0.115 | 2023: +0.222 | 2024: +0.170 | 2025: -0.150 | 2026: +0.142
- IC CV=1.00, Neg years (linear/tail)=2/1 of 8, Half ratio=0.95, Recency ratio=0.85
- Early IC=+0.1180, Recent IC=+0.1001, 1st-half IC=+0.0749, 2nd-half IC=+0.0714, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17, neg years=3)
- Regime ICs: Q1_low_vol=-0.011, Q2=+0.080, Q3_mid=+0.053, Q4=+0.025, Q5_high_vol=+0.205

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0132, Sharpe=-0.5256)
- Admission: Train IC=+0.1499, Deflated=+0.1520, IR=0.47, Mono=0.71, p=0.0022, MaxCorr=0.43
- Yearly Linear ICs: 2015: +0.026 | 2016: +0.053 | 2017: +0.097 | 2018: +0.128 | 2019: -0.015 | 2020: +0.094 | 2021: +0.082 | 2022: -0.005 | 2023: +0.054 | 2024: -0.052 | 2025: -0.026 | 2026: -0.001
- Yearly Tail ICs:   2015: -0.010 | 2016: +0.087 | 2017: +0.065 | 2018: +0.280 | 2019: +0.087 | 2020: +0.152 | 2021: +0.316 | 2022: +0.144 | 2023: +0.164 | 2024: +0.085 | 2025: -0.016 | 2026: -0.201
- IC CV=0.84, Neg years (linear/tail)=2/1 of 8, Half ratio=0.53, Recency ratio=0.98
- Early IC=+0.0394, Recent IC=+0.0386, 1st-half IC=+0.0765, 2nd-half IC=+0.0405, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.011, Q3_mid=+0.095, Q4=+0.042, Q5_high_vol=+0.091

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_max__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0572, Sharpe=-0.0542)
- Admission: Train IC=+0.1938, Deflated=+0.1949, IR=0.57, Mono=0.72, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.110 | 2017: +0.049 | 2018: +0.194 | 2019: +0.094 | 2020: +0.007 | 2021: +0.139 | 2022: +0.039 | 2023: +0.142 | 2024: +0.028 | 2025: +0.076 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.105 | 2016: +0.062 | 2017: +0.065 | 2018: +0.318 | 2019: +0.146 | 2020: +0.185 | 2021: +0.321 | 2022: +0.359 | 2023: +0.260 | 2024: +0.060 | 2025: +0.152 | 2026: -0.326
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.88
- Early IC=+0.1008, Recent IC=+0.0888, 1st-half IC=+0.1175, 2nd-half IC=+0.0721, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.068, Q3_mid=+0.090, Q4=+0.108, Q5_high_vol=+0.141

**`combo_tri_max__bar_ret_0__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0538, Sharpe=-0.2305)
- Admission: Train IC=+0.1839, Deflated=+0.1847, IR=0.58, Mono=0.70, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.070 | 2017: +0.065 | 2018: +0.201 | 2019: +0.056 | 2020: -0.013 | 2021: +0.169 | 2022: +0.057 | 2023: +0.178 | 2024: +0.006 | 2025: +0.102 | 2026: -0.143
- Yearly Tail ICs:   2015: +0.110 | 2016: -0.057 | 2017: +0.157 | 2018: +0.511 | 2019: +0.147 | 2020: +0.183 | 2021: +0.370 | 2022: +0.212 | 2023: +0.228 | 2024: +0.079 | 2025: +0.167 | 2026: -0.278
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=0.63, Recency ratio=1.35
- Early IC=+0.0840, Recent IC=+0.1134, 1st-half IC=+0.1134, 2nd-half IC=+0.0716, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.039, Q3_mid=+0.100, Q4=+0.072, Q5_high_vol=+0.149

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0448, Sharpe=-0.2936)
- Admission: Train IC=+0.2103, Deflated=+0.2113, IR=0.55, Mono=0.71, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.073 | 2017: -0.029 | 2018: +0.197 | 2019: +0.081 | 2020: +0.053 | 2021: +0.169 | 2022: -0.006 | 2023: +0.150 | 2024: +0.061 | 2025: +0.035 | 2026: -0.173
- Yearly Tail ICs:   2015: +0.019 | 2016: +0.244 | 2017: +0.127 | 2018: +0.378 | 2019: +0.313 | 2020: +0.137 | 2021: +0.409 | 2022: +0.094 | 2023: +0.233 | 2024: +0.230 | 2025: -0.105 | 2026: -0.113
- IC CV=0.91, Neg years (linear/tail)=2/0 of 8, Half ratio=0.70, Recency ratio=0.95
- Early IC=+0.0862, Recent IC=+0.0817, 1st-half IC=+0.1072, 2nd-half IC=+0.0753, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.004, Q3_mid=+0.078, Q4=+0.141, Q5_high_vol=+0.157

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0417, Sharpe=-0.0329)
- Admission: Train IC=+0.1858, Deflated=+0.1864, IR=0.66, Mono=0.75, p=0.0004, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130 | 2022: +0.096 | 2023: +0.023 | 2024: -0.052 | 2025: +0.076 | 2026: +0.197
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.203 | 2017: +0.113 | 2018: +0.268 | 2019: +0.174 | 2020: +0.304 | 2021: +0.283 | 2022: +0.225 | 2023: -0.082 | 2024: +0.218 | 2025: +0.014 | 2026: +0.361
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=1.45, Recency ratio=1.93
- Early IC=+0.0585, Recent IC=+0.1128, 1st-half IC=+0.0554, 2nd-half IC=+0.0802, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.022, Q2=+0.005, Q3_mid=+0.048, Q4=+0.174, Q5_high_vol=+0.099

**`combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`** (Lock IC=+0.0368, Sharpe=-0.3026)
- Admission: Train IC=+0.2001, Deflated=+0.2002, IR=0.55, Mono=0.70, p=0.0002, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.081 | 2017: +0.058 | 2018: +0.108 | 2019: +0.035 | 2020: -0.022 | 2021: +0.187 | 2022: +0.077 | 2023: +0.060 | 2024: -0.059 | 2025: +0.074 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.233 | 2017: +0.143 | 2018: +0.380 | 2019: +0.000 | 2020: -0.146 | 2021: +0.296 | 2022: +0.127 | 2023: +0.093 | 2024: +0.037 | 2025: +0.108 | 2026: +0.272
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=0.58, Recency ratio=1.10
- Early IC=+0.1194, Recent IC=+0.1318, 1st-half IC=+0.1169, 2nd-half IC=+0.0680, Neg regimes=1/5
- Weak component: `volume_surge_max` (CV=1.98)
- Regime ICs: Q1_low_vol=+0.078, Q2=-0.019, Q3_mid=+0.010, Q4=+0.146, Q5_high_vol=+0.146

**`combo_sig_product__first_bar_return__morning_volume_weighted_momentum`** (Lock IC=+0.0290, Sharpe=-0.2006)
- Admission: Train IC=+0.1279, Deflated=+0.1280, IR=0.44, Mono=0.67, p=0.0136, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.064 | 2017: +0.022 | 2018: +0.184 | 2019: +0.126 | 2020: -0.038 | 2021: +0.098 | 2022: +0.041 | 2023: +0.118 | 2024: +0.015 | 2025: +0.018 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.123 | 2017: +0.113 | 2018: +0.144 | 2019: +0.258 | 2020: -0.063 | 2021: +0.182 | 2022: +0.161 | 2023: +0.239 | 2024: +0.114 | 2025: +0.053 | 2026: -0.335
- IC CV=0.84, Neg years (linear/tail)=1/1 of 8, Half ratio=0.49, Recency ratio=0.71
- Early IC=+0.0981, Recent IC=+0.0695, 1st-half IC=+0.1168, 2nd-half IC=+0.0569, Neg regimes=0/5
- Weak component: `morning_volume_weighted_momentum` (CV=2.01)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.006, Q3_mid=+0.104, Q4=+0.098, Q5_high_vol=+0.122

### 500ETF — `single` Median Features

**`combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early`** (Lock IC=+0.1053, Sharpe=-0.3095)
- Admission: Train IC=+0.1645, Deflated=+0.1654, IR=0.44, Mono=0.68, p=0.0006, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.028 | 2017: +0.233 | 2018: +0.086 | 2019: +0.065 | 2020: +0.062 | 2021: +0.058 | 2022: +0.088 | 2023: +0.097 | 2024: +0.099 | 2025: +0.100 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.298 | 2016: +0.044 | 2017: +0.274 | 2018: +0.009 | 2019: +0.191 | 2020: +0.040 | 2021: +0.014 | 2022: +0.095 | 2023: -0.002 | 2024: -0.047 | 2025: -0.171 | 2026: +0.211
- IC CV=0.74, Neg years (linear/tail)=0/0 of 8, Half ratio=0.40, Recency ratio=0.50
- Early IC=+0.1444, Recent IC=+0.0728, 1st-half IC=+0.1735, 2nd-half IC=+0.0700, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.000, Q3_mid=+0.141, Q4=+0.142, Q5_high_vol=+0.124

**`combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1040, Sharpe=-0.0012)
- Admission: Train IC=+0.2247, Deflated=+0.2256, IR=0.52, Mono=0.70, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.313 | 2016: +0.099 | 2017: +0.233 | 2018: +0.156 | 2019: +0.130 | 2020: +0.174 | 2021: +0.075 | 2022: +0.120 | 2023: +0.073 | 2024: +0.102 | 2025: +0.090 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.169 | 2017: +0.112 | 2018: +0.124 | 2019: +0.261 | 2020: +0.166 | 2021: +0.145 | 2022: +0.106 | 2023: -0.052 | 2024: -0.049 | 2025: +0.091 | 2026: +0.175
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.47
- Early IC=+0.2057, Recent IC=+0.0974, 1st-half IC=+0.2262, 2nd-half IC=+0.1271, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.033, Q3_mid=+0.195, Q4=+0.138, Q5_high_vol=+0.258

**`combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0933, Sharpe=-0.0259)
- Admission: Train IC=+0.2540, Deflated=+0.2552, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.046 | 2017: +0.155 | 2018: +0.199 | 2019: +0.170 | 2020: +0.196 | 2021: +0.147 | 2022: +0.044 | 2023: +0.104 | 2024: +0.141 | 2025: +0.067 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.367 | 2016: -0.018 | 2017: +0.141 | 2018: +0.322 | 2019: +0.256 | 2020: +0.168 | 2021: +0.147 | 2022: +0.268 | 2023: +0.062 | 2024: +0.165 | 2025: +0.168 | 2026: -0.144
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.64
- Early IC=+0.1486, Recent IC=+0.0956, 1st-half IC=+0.1751, 2nd-half IC=+0.1433, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.061, Q3_mid=+0.175, Q4=+0.130, Q5_high_vol=+0.262

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0922, Sharpe=-0.1324)
- Admission: Train IC=+0.2230, Deflated=+0.2240, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.264 | 2016: +0.106 | 2017: +0.203 | 2018: +0.244 | 2019: +0.107 | 2020: +0.113 | 2021: +0.097 | 2022: +0.132 | 2023: +0.076 | 2024: +0.097 | 2025: +0.083 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.209 | 2016: +0.171 | 2017: +0.239 | 2018: +0.392 | 2019: +0.076 | 2020: +0.079 | 2021: +0.285 | 2022: +0.191 | 2023: -0.059 | 2024: +0.048 | 2025: -0.034 | 2026: -0.155
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.48, Recency ratio=0.62
- Early IC=+0.1851, Recent IC=+0.1145, 1st-half IC=+0.2309, 2nd-half IC=+0.1105, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.057, Q3_mid=+0.168, Q4=+0.149, Q5_high_vol=+0.261

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0893, Sharpe=-0.0123)
- Admission: Train IC=+0.2138, Deflated=+0.2151, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.290 | 2016: +0.104 | 2017: +0.233 | 2018: +0.197 | 2019: +0.114 | 2020: +0.156 | 2021: +0.083 | 2022: +0.117 | 2023: +0.063 | 2024: +0.084 | 2025: +0.083 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.254 | 2017: +0.102 | 2018: +0.294 | 2019: +0.144 | 2020: +0.090 | 2021: +0.190 | 2022: +0.146 | 2023: -0.083 | 2024: +0.084 | 2025: -0.027 | 2026: -0.099
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.51
- Early IC=+0.1974, Recent IC=+0.1001, 1st-half IC=+0.2396, 2nd-half IC=+0.1207, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.032, Q3_mid=+0.197, Q4=+0.146, Q5_high_vol=+0.271

**`combo_max__net_volume_flow__max_down_ret`** (Lock IC=+0.0851, Sharpe=-0.0023)
- Admission: Train IC=+0.1903, Deflated=+0.1919, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.086 | 2017: +0.204 | 2018: +0.168 | 2019: +0.095 | 2020: +0.114 | 2021: +0.070 | 2022: +0.066 | 2023: +0.041 | 2024: +0.141 | 2025: +0.129 | 2026: -0.041
- Yearly Tail ICs:   2015: +0.319 | 2016: +0.122 | 2017: +0.157 | 2018: +0.150 | 2019: +0.181 | 2020: -0.000 | 2021: +0.261 | 2022: +0.182 | 2023: +0.278 | 2024: +0.219 | 2025: +0.086 | 2026: -0.195
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=0.49
- Early IC=+0.1397, Recent IC=+0.0681, 1st-half IC=+0.1634, 2nd-half IC=+0.0920, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.011, Q3_mid=+0.167, Q4=+0.121, Q5_high_vol=+0.146

**`combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0844, Sharpe=-0.1714)
- Admission: Train IC=+0.2209, Deflated=+0.2221, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.047 | 2017: +0.232 | 2018: +0.165 | 2019: +0.123 | 2020: +0.156 | 2021: +0.120 | 2022: +0.098 | 2023: +0.090 | 2024: +0.131 | 2025: +0.126 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.070 | 2017: +0.230 | 2018: +0.345 | 2019: +0.368 | 2020: +0.051 | 2021: +0.285 | 2022: +0.131 | 2023: +0.166 | 2024: +0.299 | 2025: +0.096 | 2026: -0.343
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.81
- Early IC=+0.1336, Recent IC=+0.1087, 1st-half IC=+0.1851, 2nd-half IC=+0.1282, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.068, Q3_mid=+0.178, Q4=+0.157, Q5_high_vol=+0.172

**`combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance`** (Lock IC=+0.0843, Sharpe=-0.2363)
- Admission: Train IC=+0.2645, Deflated=+0.2660, IR=0.77, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.012 | 2017: +0.194 | 2018: +0.166 | 2019: +0.142 | 2020: +0.116 | 2021: +0.146 | 2022: +0.115 | 2023: +0.093 | 2024: +0.141 | 2025: +0.107 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.385 | 2016: +0.092 | 2017: +0.191 | 2018: +0.281 | 2019: +0.427 | 2020: +0.108 | 2021: +0.319 | 2022: +0.340 | 2023: +0.224 | 2024: +0.375 | 2025: -0.051 | 2026: -0.214
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=1.23
- Early IC=+0.1059, Recent IC=+0.1303, 1st-half IC=+0.1563, 2nd-half IC=+0.1335, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.027, Q3_mid=+0.177, Q4=+0.153, Q5_high_vol=+0.164

**`combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation`** (Lock IC=+0.0828, Sharpe=-0.1066)
- Admission: Train IC=+0.2227, Deflated=+0.2246, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.126 | 2017: +0.184 | 2018: +0.151 | 2019: +0.108 | 2020: +0.100 | 2021: +0.099 | 2022: +0.075 | 2023: +0.097 | 2024: +0.118 | 2025: +0.120 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.403 | 2016: -0.008 | 2017: +0.188 | 2018: +0.250 | 2019: +0.274 | 2020: +0.283 | 2021: +0.195 | 2022: +0.066 | 2023: +0.205 | 2024: +0.183 | 2025: +0.159 | 2026: -0.169
- IC CV=0.32, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=0.53
- Early IC=+0.1642, Recent IC=+0.0871, 1st-half IC=+0.1772, 2nd-half IC=+0.0984, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.018, Q3_mid=+0.171, Q4=+0.143, Q5_high_vol=+0.169

**`combo_rank_max__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0812, Sharpe=-0.0084)
- Admission: Train IC=+0.2028, Deflated=+0.2036, IR=0.62, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.114 | 2017: +0.179 | 2018: +0.194 | 2019: +0.102 | 2020: +0.110 | 2021: +0.153 | 2022: +0.110 | 2023: +0.122 | 2024: +0.124 | 2025: +0.132 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.258 | 2016: -0.034 | 2017: +0.134 | 2018: +0.351 | 2019: +0.208 | 2020: +0.214 | 2021: +0.196 | 2022: +0.233 | 2023: +0.407 | 2024: +0.103 | 2025: -0.061 | 2026: -0.476
- IC CV=0.25, Neg years (linear/tail)=0/1 of 8, Half ratio=0.67, Recency ratio=0.90
- Early IC=+0.1461, Recent IC=+0.1313, 1st-half IC=+0.1832, 2nd-half IC=+0.1221, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.083, Q3_mid=+0.145, Q4=+0.133, Q5_high_vol=+0.178

**`combo_max__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0811, Sharpe=-0.0987)
- Admission: Train IC=+0.1959, Deflated=+0.1967, IR=0.54, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.111 | 2017: +0.174 | 2018: +0.194 | 2019: +0.101 | 2020: +0.108 | 2021: +0.160 | 2022: +0.111 | 2023: +0.118 | 2024: +0.122 | 2025: +0.131 | 2026: -0.111
- Yearly Tail ICs:   2015: +0.284 | 2016: -0.052 | 2017: +0.109 | 2018: +0.314 | 2019: +0.232 | 2020: +0.161 | 2021: +0.202 | 2022: +0.169 | 2023: +0.414 | 2024: +0.116 | 2025: -0.093 | 2026: -0.558
- IC CV=0.25, Neg years (linear/tail)=0/1 of 8, Half ratio=0.68, Recency ratio=0.94
- Early IC=+0.1438, Recent IC=+0.1353, 1st-half IC=+0.1812, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.083, Q3_mid=+0.147, Q4=+0.134, Q5_high_vol=+0.177

**`combo_rel_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0805, Sharpe=-0.0723)
- Admission: Train IC=+0.2542, Deflated=+0.2555, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.117 | 2017: +0.158 | 2018: +0.127 | 2019: +0.073 | 2020: +0.112 | 2021: +0.060 | 2022: +0.123 | 2023: +0.107 | 2024: +0.126 | 2025: +0.094 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.303 | 2016: +0.327 | 2017: +0.133 | 2018: +0.283 | 2019: +0.161 | 2020: +0.069 | 2021: +0.259 | 2022: +0.161 | 2023: +0.292 | 2024: +0.260 | 2025: -0.177 | 2026: -0.120
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.57
- Early IC=+0.1602, Recent IC=+0.0915, 1st-half IC=+0.1758, 2nd-half IC=+0.0986, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.025, Q3_mid=+0.174, Q4=+0.130, Q5_high_vol=+0.167

**`combo_mean__close_vs_open_range__vwap_close_divergence_trend`** (Lock IC=+0.0802, Sharpe=-0.3656)
- Admission: Train IC=+0.1649, Deflated=+0.1659, IR=0.55, Mono=0.70, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.042 | 2017: +0.181 | 2018: +0.080 | 2019: +0.081 | 2020: +0.089 | 2021: +0.072 | 2022: +0.090 | 2023: +0.101 | 2024: +0.101 | 2025: +0.148 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.120 | 2017: +0.244 | 2018: +0.206 | 2019: +0.185 | 2020: +0.045 | 2021: +0.299 | 2022: +0.108 | 2023: +0.171 | 2024: +0.233 | 2025: +0.106 | 2026: -0.217
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.87
- Early IC=+0.0926, Recent IC=+0.0807, 1st-half IC=+0.1206, 2nd-half IC=+0.0890, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.021, Q3_mid=+0.146, Q4=+0.101, Q5_high_vol=+0.091

**`combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0`** (Lock IC=+0.0788, Sharpe=-0.0583)
- Admission: Train IC=+0.1845, Deflated=+0.1861, IR=0.62, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.076 | 2017: +0.232 | 2018: +0.149 | 2019: +0.066 | 2020: +0.108 | 2021: +0.069 | 2022: +0.105 | 2023: +0.060 | 2024: +0.128 | 2025: +0.107 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.315 | 2016: -0.008 | 2017: +0.342 | 2018: +0.069 | 2019: +0.130 | 2020: +0.210 | 2021: +0.188 | 2022: +0.186 | 2023: +0.241 | 2024: +0.236 | 2025: +0.046 | 2026: -0.170
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.68
- Early IC=+0.1270, Recent IC=+0.0867, 1st-half IC=+0.1670, 2nd-half IC=+0.0879, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.016, Q3_mid=+0.116, Q4=+0.161, Q5_high_vol=+0.142

**`combo_rank_min__opening_drive_thrust_ratio__early_order_flow_imbalance`** (Lock IC=+0.0753, Sharpe=-0.0440)
- Admission: Train IC=+0.2515, Deflated=+0.2537, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.153 | 2016: +0.014 | 2017: +0.149 | 2018: +0.153 | 2019: +0.145 | 2020: +0.115 | 2021: +0.161 | 2022: +0.117 | 2023: +0.117 | 2024: +0.130 | 2025: +0.059 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.373 | 2016: +0.156 | 2017: +0.282 | 2018: +0.252 | 2019: +0.389 | 2020: +0.129 | 2021: +0.296 | 2022: +0.285 | 2023: +0.120 | 2024: +0.385 | 2025: +0.040 | 2026: -0.250
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.62
- Early IC=+0.0842, Recent IC=+0.1362, 1st-half IC=+0.1260, 2nd-half IC=+0.1371, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.041, Q3_mid=+0.169, Q4=+0.140, Q5_high_vol=+0.136

**`combo_max__net_volume_flow__first_bar_return`** (Lock IC=+0.0731, Sharpe=-0.3903)
- Admission: Train IC=+0.1927, Deflated=+0.1942, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.106 | 2017: +0.170 | 2018: +0.235 | 2019: +0.119 | 2020: +0.109 | 2021: +0.105 | 2022: +0.095 | 2023: +0.075 | 2024: +0.110 | 2025: +0.106 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.039 | 2017: +0.159 | 2018: +0.277 | 2019: +0.141 | 2020: +0.260 | 2021: +0.281 | 2022: +0.162 | 2023: +0.363 | 2024: +0.185 | 2025: -0.065 | 2026: -0.491
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.67
- Early IC=+0.1495, Recent IC=+0.1003, 1st-half IC=+0.1931, 2nd-half IC=+0.1115, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.001, Q3_mid=+0.164, Q4=+0.159, Q5_high_vol=+0.198

**`combo_min__early_order_flow_imbalance__close_vs_open_range`** (Lock IC=+0.0719, Sharpe=-0.1114)
- Admission: Train IC=+0.2173, Deflated=+0.2192, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.029 | 2017: +0.157 | 2018: +0.116 | 2019: +0.109 | 2020: +0.052 | 2021: +0.115 | 2022: +0.110 | 2023: +0.107 | 2024: +0.127 | 2025: +0.097 | 2026: -0.115
- Yearly Tail ICs:   2015: +0.295 | 2016: +0.118 | 2017: +0.303 | 2018: +0.178 | 2019: +0.306 | 2020: +0.090 | 2021: +0.234 | 2022: +0.158 | 2023: +0.152 | 2024: +0.381 | 2025: -0.043 | 2026: -0.149
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=1.62
- Early IC=+0.0694, Recent IC=+0.1128, 1st-half IC=+0.1057, 2nd-half IC=+0.0994, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.003, Q3_mid=+0.149, Q4=+0.128, Q5_high_vol=+0.070

**`combo_rel_diff__first_bar_return__h2_l2_pullback_continuation`** (Lock IC=+0.0714, Sharpe=-0.1819)
- Admission: Train IC=+0.2195, Deflated=+0.2207, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.096 | 2017: +0.147 | 2018: +0.146 | 2019: +0.105 | 2020: +0.089 | 2021: +0.072 | 2022: +0.095 | 2023: +0.080 | 2024: +0.118 | 2025: +0.123 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.402 | 2016: +0.019 | 2017: +0.077 | 2018: +0.343 | 2019: +0.168 | 2020: +0.053 | 2021: +0.117 | 2022: +0.252 | 2023: +0.301 | 2024: +0.283 | 2025: +0.014 | 2026: -0.430
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.54
- Early IC=+0.1537, Recent IC=+0.0833, 1st-half IC=+0.1693, 2nd-half IC=+0.0971, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.001, Q3_mid=+0.161, Q4=+0.140, Q5_high_vol=+0.155

**`combo_rank_max__trend_day_regime_conviction__early_order_flow_imbalance`** (Lock IC=+0.0704, Sharpe=-0.0750)
- Admission: Train IC=+0.2362, Deflated=+0.2371, IR=0.51, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.005 | 2017: +0.146 | 2018: +0.098 | 2019: +0.101 | 2020: +0.084 | 2021: +0.086 | 2022: +0.123 | 2023: +0.070 | 2024: +0.107 | 2025: +0.127 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.346 | 2016: -0.006 | 2017: +0.192 | 2018: +0.243 | 2019: +0.305 | 2020: +0.212 | 2021: +0.087 | 2022: +0.398 | 2023: +0.114 | 2024: +0.302 | 2025: +0.006 | 2026: +0.039
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.98, Recency ratio=1.39
- Early IC=+0.0743, Recent IC=+0.1036, 1st-half IC=+0.1035, 2nd-half IC=+0.1015, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.139, Q2=-0.024, Q3_mid=+0.140, Q4=+0.133, Q5_high_vol=+0.097

**`combo_rank_min__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0695, Sharpe=-0.0684)
- Admission: Train IC=+0.2092, Deflated=+0.2116, IR=0.68, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.038 | 2017: +0.162 | 2018: +0.111 | 2019: +0.122 | 2020: +0.103 | 2021: +0.105 | 2022: +0.144 | 2023: +0.079 | 2024: +0.114 | 2025: +0.068 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.080 | 2017: +0.182 | 2018: +0.160 | 2019: +0.242 | 2020: +0.142 | 2021: +0.279 | 2022: +0.308 | 2023: +0.056 | 2024: +0.329 | 2025: +0.114 | 2026: -0.083
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=0.91
- Early IC=+0.1384, Recent IC=+0.1257, 1st-half IC=+0.1198, 2nd-half IC=+0.1230, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.122, Q2=-0.010, Q3_mid=+0.145, Q4=+0.137, Q5_high_vol=+0.175

**`combo_sig_product__max_down_ret__close_vs_open_range`** (Lock IC=+0.0608, Sharpe=-0.1007)
- Admission: Train IC=+0.2103, Deflated=+0.2120, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.152 | 2016: +0.089 | 2017: +0.202 | 2018: +0.055 | 2019: +0.115 | 2020: +0.075 | 2021: +0.035 | 2022: +0.079 | 2023: +0.046 | 2024: +0.119 | 2025: +0.085 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.248 | 2016: +0.104 | 2017: +0.338 | 2018: +0.155 | 2019: +0.167 | 2020: +0.098 | 2021: +0.250 | 2022: +0.138 | 2023: +0.023 | 2024: +0.214 | 2025: -0.009 | 2026: +0.006
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.47
- Early IC=+0.1205, Recent IC=+0.0568, 1st-half IC=+0.1071, 2nd-half IC=+0.0837, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.026, Q3_mid=+0.117, Q4=+0.064, Q5_high_vol=+0.107

**`combo_rank_max__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0573, Sharpe=-0.2389)
- Admission: Train IC=+0.1869, Deflated=+0.1883, IR=0.48, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.067 | 2017: +0.131 | 2018: +0.204 | 2019: +0.119 | 2020: +0.070 | 2021: +0.092 | 2022: +0.092 | 2023: +0.081 | 2024: +0.107 | 2025: +0.095 | 2026: -0.124
- Yearly Tail ICs:   2015: +0.178 | 2016: -0.101 | 2017: +0.051 | 2018: +0.344 | 2019: +0.176 | 2020: +0.162 | 2021: +0.294 | 2022: +0.229 | 2023: +0.374 | 2024: +0.250 | 2025: -0.089 | 2026: -0.454
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.75
- Early IC=+0.1232, Recent IC=+0.0922, 1st-half IC=+0.1614, 2nd-half IC=+0.1021, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.003, Q3_mid=+0.131, Q4=+0.141, Q5_high_vol=+0.165

**`combo_max__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0535, Sharpe=-0.4023)
- Admission: Train IC=+0.1830, Deflated=+0.1842, IR=0.48, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.055 | 2017: +0.122 | 2018: +0.195 | 2019: +0.115 | 2020: +0.067 | 2021: +0.077 | 2022: +0.100 | 2023: +0.069 | 2024: +0.103 | 2025: +0.090 | 2026: -0.126
- Yearly Tail ICs:   2015: +0.209 | 2016: -0.095 | 2017: +0.057 | 2018: +0.329 | 2019: +0.204 | 2020: +0.161 | 2021: +0.318 | 2022: +0.185 | 2023: +0.313 | 2024: +0.171 | 2025: -0.097 | 2026: -0.496
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.77
- Early IC=+0.1147, Recent IC=+0.0887, 1st-half IC=+0.1510, 2nd-half IC=+0.0974, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.126, Q2=-0.004, Q3_mid=+0.125, Q4=+0.142, Q5_high_vol=+0.155

**`combo_sig_product__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0420, Sharpe=-0.5395)
- Admission: Train IC=+0.1873, Deflated=+0.1882, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.69
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.095 | 2017: +0.084 | 2018: +0.185 | 2019: +0.182 | 2020: +0.100 | 2021: +0.069 | 2022: +0.130 | 2023: +0.137 | 2024: +0.058 | 2025: +0.053 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.122 | 2017: +0.032 | 2018: +0.294 | 2019: +0.349 | 2020: +0.048 | 2021: +0.077 | 2022: +0.270 | 2023: +0.276 | 2024: +0.231 | 2025: -0.117 | 2026: +0.012
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.67
- Early IC=+0.1474, Recent IC=+0.0993, 1st-half IC=+0.1571, 2nd-half IC=+0.1225, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.041, Q3_mid=+0.136, Q4=+0.152, Q5_high_vol=+0.181

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0706, Sharpe=+0.8555)
- Admission: Train IC=+0.2691, Deflated=+0.2697, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.117 | 2017: -0.053 | 2018: +0.140 | 2019: +0.099 | 2020: +0.074 | 2021: +0.143 | 2022: +0.037 | 2023: +0.135 | 2024: +0.055 | 2025: +0.049 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.398 | 2016: +0.177 | 2017: -0.045 | 2018: +0.311 | 2019: +0.294 | 2020: +0.171 | 2021: +0.368 | 2022: +0.249 | 2023: +0.127 | 2024: +0.392 | 2025: +0.055 | 2026: +0.139
- IC CV=0.84, Neg years (linear/tail)=1/1 of 8, Half ratio=0.59, Recency ratio=0.47
- Early IC=+0.1915, Recent IC=+0.0901, 1st-half IC=+0.1476, 2nd-half IC=+0.0872, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.005, Q2=+0.021, Q3_mid=+0.037, Q4=+0.214, Q5_high_vol=+0.205

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0761, Sharpe=+0.8091)
- Admission: Train IC=+0.2197, Deflated=+0.2208, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.093 | 2017: -0.047 | 2018: +0.182 | 2019: +0.103 | 2020: +0.018 | 2021: +0.175 | 2022: +0.059 | 2023: +0.173 | 2024: +0.056 | 2025: +0.076 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.284 | 2016: +0.117 | 2017: -0.015 | 2018: +0.221 | 2019: +0.179 | 2020: +0.051 | 2021: +0.540 | 2022: +0.334 | 2023: +0.170 | 2024: +0.273 | 2025: +0.045 | 2026: -0.046
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=0.76, Recency ratio=1.03
- Early IC=+0.1136, Recent IC=+0.1168, 1st-half IC=+0.1146, 2nd-half IC=+0.0873, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.037, Q3_mid=+0.063, Q4=+0.156, Q5_high_vol=+0.176

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0876, Sharpe=+0.7186)
- Admission: Train IC=+0.2593, Deflated=+0.2602, IR=0.67, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.71, Recency ratio=0.71
- Early IC=+0.1376, Recent IC=+0.0979, 1st-half IC=+0.1324, 2nd-half IC=+0.0936, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.028, Q2=+0.039, Q3_mid=+0.076, Q4=+0.186, Q5_high_vol=+0.196

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0843, Sharpe=+0.7153)
- Admission: Train IC=+0.1818, Deflated=+0.1831, IR=0.53, Mono=0.68, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=0.86, Recency ratio=0.71
- Early IC=+0.1112, Recent IC=+0.0793, 1st-half IC=+0.0952, 2nd-half IC=+0.0816, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.030, Q3_mid=+0.048, Q4=+0.167, Q5_high_vol=+0.163

**`combo_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0839, Sharpe=+0.6572)
- Admission: Train IC=+0.2134, Deflated=+0.2144, IR=0.68, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.060 | 2017: -0.024 | 2018: +0.181 | 2019: +0.146 | 2020: +0.024 | 2021: +0.126 | 2022: +0.042 | 2023: +0.163 | 2024: +0.032 | 2025: +0.090 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.076 | 2017: +0.022 | 2018: +0.382 | 2019: +0.218 | 2020: +0.202 | 2021: +0.360 | 2022: +0.213 | 2023: +0.282 | 2024: +0.150 | 2025: -0.026 | 2026: +0.248
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=0.70, Recency ratio=0.60
- Early IC=+0.1385, Recent IC=+0.0837, 1st-half IC=+0.1247, 2nd-half IC=+0.0867, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.09)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.033, Q3_mid=+0.061, Q4=+0.167, Q5_high_vol=+0.187

**`combo_tri_min__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0743, Sharpe=+0.6390)
- Admission: Train IC=+0.1916, Deflated=+0.1923, IR=0.53, Mono=0.65, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.086 | 2017: +0.014 | 2018: +0.179 | 2019: +0.108 | 2020: +0.020 | 2021: +0.098 | 2022: +0.037 | 2023: +0.159 | 2024: +0.052 | 2025: +0.038 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.067 | 2017: +0.100 | 2018: +0.449 | 2019: +0.258 | 2020: +0.206 | 2021: +0.160 | 2022: +0.128 | 2023: +0.332 | 2024: +0.149 | 2025: -0.095 | 2026: +0.169
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.45
- Early IC=+0.1517, Recent IC=+0.0678, 1st-half IC=+0.1392, 2nd-half IC=+0.0697, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.025, Q3_mid=+0.055, Q4=+0.161, Q5_high_vol=+0.185

**`combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0520, Sharpe=+0.6190)
- Admission: Train IC=+0.2000, Deflated=+0.2009, IR=0.51, Mono=0.69, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.124 | 2016: +0.092 | 2017: +0.054 | 2018: +0.204 | 2019: +0.095 | 2020: +0.004 | 2021: +0.134 | 2022: +0.041 | 2023: +0.137 | 2024: +0.036 | 2025: +0.048 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.187 | 2016: +0.003 | 2017: +0.011 | 2018: +0.261 | 2019: +0.131 | 2020: +0.219 | 2021: +0.345 | 2022: +0.275 | 2023: +0.347 | 2024: +0.152 | 2025: +0.064 | 2026: -0.091
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.81
- Early IC=+0.1079, Recent IC=+0.0874, 1st-half IC=+0.1277, 2nd-half IC=+0.0695, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.058, Q3_mid=+0.083, Q4=+0.107, Q5_high_vol=+0.163

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0708, Sharpe=+0.5931)
- Admission: Train IC=+0.1870, Deflated=+0.1876, IR=0.44, Mono=0.67, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.112 | 2017: -0.050 | 2018: +0.133 | 2019: +0.102 | 2020: +0.072 | 2021: +0.119 | 2022: +0.045 | 2023: +0.129 | 2024: +0.046 | 2025: +0.048 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.235 | 2016: +0.085 | 2017: -0.056 | 2018: +0.318 | 2019: +0.344 | 2020: +0.201 | 2021: +0.200 | 2022: +0.176 | 2023: +0.072 | 2024: +0.420 | 2025: -0.001 | 2026: +0.163
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=0.66, Recency ratio=0.50
- Early IC=+0.1648, Recent IC=+0.0819, 1st-half IC=+0.1272, 2nd-half IC=+0.0837, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.012, Q2=+0.026, Q3_mid=+0.036, Q4=+0.199, Q5_high_vol=+0.177

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0684, Sharpe=+0.5896)
- Admission: Train IC=+0.1747, Deflated=+0.1759, IR=0.42, Mono=0.67, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.074 | 2017: -0.056 | 2018: +0.156 | 2019: +0.082 | 2020: +0.040 | 2021: +0.143 | 2022: +0.034 | 2023: +0.160 | 2024: +0.045 | 2025: +0.074 | 2026: -0.104
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.144 | 2017: +0.032 | 2018: +0.247 | 2019: +0.197 | 2020: +0.078 | 2021: +0.334 | 2022: +0.204 | 2023: +0.248 | 2024: +0.282 | 2025: +0.099 | 2026: -0.143
- IC CV=0.87, Neg years (linear/tail)=1/0 of 8, Half ratio=0.67, Recency ratio=0.76
- Early IC=+0.1168, Recent IC=+0.0885, 1st-half IC=+0.1089, 2nd-half IC=+0.0732, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.013, Q2=+0.020, Q3_mid=+0.042, Q4=+0.159, Q5_high_vol=+0.181

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0756, Sharpe=+0.5654)
- Admission: Train IC=+0.2800, Deflated=+0.2807, IR=0.74, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.097 | 2017: +0.009 | 2018: +0.184 | 2019: +0.117 | 2020: +0.042 | 2021: +0.132 | 2022: +0.037 | 2023: +0.177 | 2024: +0.055 | 2025: +0.048 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.333 | 2016: +0.106 | 2017: +0.102 | 2018: +0.396 | 2019: +0.276 | 2020: +0.232 | 2021: +0.485 | 2022: +0.149 | 2023: +0.338 | 2024: +0.242 | 2025: -0.037 | 2026: +0.148
- IC CV=0.70, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.48
- Early IC=+0.1757, Recent IC=+0.0846, 1st-half IC=+0.1567, 2nd-half IC=+0.0837, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.034, Q3_mid=+0.069, Q4=+0.186, Q5_high_vol=+0.207

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`** (Lock IC=+0.0521, Sharpe=+0.5457)
- Admission: Train IC=+0.1999, Deflated=+0.1999, IR=0.45, Mono=0.68, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.127 | 2016: +0.087 | 2017: +0.013 | 2018: +0.130 | 2019: +0.038 | 2020: -0.017 | 2021: +0.121 | 2022: +0.069 | 2023: +0.054 | 2024: -0.006 | 2025: +0.070 | 2026: +0.137
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.207 | 2017: +0.151 | 2018: +0.363 | 2019: +0.088 | 2020: -0.140 | 2021: +0.278 | 2022: +0.078 | 2023: +0.038 | 2024: +0.202 | 2025: +0.165 | 2026: +0.186
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=0.58, Recency ratio=0.88
- Early IC=+0.1072, Recent IC=+0.0948, 1st-half IC=+0.0991, 2nd-half IC=+0.0575, Neg regimes=1/5
- Weak component: `volume_surge_max` (CV=1.98)
- Regime ICs: Q1_low_vol=+0.053, Q2=-0.007, Q3_mid=+0.026, Q4=+0.137, Q5_high_vol=+0.133

**`combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0587, Sharpe=+0.5249)
- Admission: Train IC=+0.2054, Deflated=+0.2064, IR=0.39, Mono=0.66, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.113 | 2016: +0.083 | 2017: +0.020 | 2018: +0.179 | 2019: +0.082 | 2020: +0.007 | 2021: +0.118 | 2022: +0.043 | 2023: +0.166 | 2024: +0.055 | 2025: +0.028 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.203 | 2016: +0.004 | 2017: +0.096 | 2018: +0.214 | 2019: +0.210 | 2020: +0.150 | 2021: +0.336 | 2022: +0.248 | 2023: +0.319 | 2024: +0.316 | 2025: +0.023 | 2026: -0.107
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.82
- Early IC=+0.0978, Recent IC=+0.0807, 1st-half IC=+0.1155, 2nd-half IC=+0.0660, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.044, Q2=+0.039, Q3_mid=+0.085, Q4=+0.099, Q5_high_vol=+0.156

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0678, Sharpe=+0.5240)
- Admission: Train IC=+0.1957, Deflated=+0.1970, IR=0.69, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.115 | 2017: -0.019 | 2018: +0.233 | 2019: +0.100 | 2020: +0.053 | 2021: +0.165 | 2022: +0.065 | 2023: +0.130 | 2024: +0.029 | 2025: +0.077 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.181 | 2016: +0.114 | 2017: -0.024 | 2018: +0.354 | 2019: +0.282 | 2020: +0.123 | 2021: +0.405 | 2022: +0.236 | 2023: +0.121 | 2024: +0.178 | 2025: +0.199 | 2026: +0.079
- IC CV=0.69, Neg years (linear/tail)=1/1 of 8, Half ratio=0.64, Recency ratio=0.70
- Early IC=+0.1643, Recent IC=+0.1149, 1st-half IC=+0.1513, 2nd-half IC=+0.0966, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.042, Q3_mid=+0.074, Q4=+0.220, Q5_high_vol=+0.202

**`combo_tri_mean__first_bar_return__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0629, Sharpe=+0.5008)
- Admission: Train IC=+0.2018, Deflated=+0.2028, IR=0.50, Mono=0.68, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.118 | 2016: +0.078 | 2017: +0.043 | 2018: +0.209 | 2019: +0.080 | 2020: -0.016 | 2021: +0.151 | 2022: +0.055 | 2023: +0.171 | 2024: +0.023 | 2025: +0.099 | 2026: -0.110
- Yearly Tail ICs:   2015: +0.214 | 2016: -0.088 | 2017: +0.144 | 2018: +0.381 | 2019: +0.125 | 2020: +0.087 | 2021: +0.417 | 2022: +0.269 | 2023: +0.284 | 2024: +0.211 | 2025: +0.172 | 2026: -0.102
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=0.60, Recency ratio=1.05
- Early IC=+0.0976, Recent IC=+0.1028, 1st-half IC=+0.1205, 2nd-half IC=+0.0721, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.061, Q3_mid=+0.094, Q4=+0.087, Q5_high_vol=+0.154

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`** (Lock IC=+0.0619, Sharpe=+0.4938)
- Admission: Train IC=+0.2299, Deflated=+0.2304, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.105 | 2017: -0.069 | 2018: +0.143 | 2019: +0.078 | 2020: +0.060 | 2021: +0.129 | 2022: +0.093 | 2023: +0.070 | 2024: +0.018 | 2025: +0.032 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.098 | 2017: -0.004 | 2018: +0.406 | 2019: +0.220 | 2020: +0.256 | 2021: +0.286 | 2022: +0.277 | 2023: -0.014 | 2024: +0.271 | 2025: +0.154 | 2026: +0.220
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=0.66, Recency ratio=0.65
- Early IC=+0.1701, Recent IC=+0.1110, 1st-half IC=+0.1348, 2nd-half IC=+0.0885, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.015, Q2=+0.005, Q3_mid=+0.050, Q4=+0.221, Q5_high_vol=+0.187

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0723, Sharpe=+0.4930)
- Admission: Train IC=+0.2664, Deflated=+0.2674, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.070 | 2017: -0.018 | 2018: +0.234 | 2019: +0.116 | 2020: +0.041 | 2021: +0.179 | 2022: +0.028 | 2023: +0.141 | 2024: +0.046 | 2025: +0.074 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.251 | 2016: +0.043 | 2017: +0.062 | 2018: +0.377 | 2019: +0.310 | 2020: +0.143 | 2021: +0.571 | 2022: +0.187 | 2023: +0.144 | 2024: +0.184 | 2025: -0.068 | 2026: +0.311
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=0.63, Recency ratio=0.72
- Early IC=+0.1432, Recent IC=+0.1032, 1st-half IC=+0.1475, 2nd-half IC=+0.0934, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.018, Q3_mid=+0.093, Q4=+0.210, Q5_high_vol=+0.192

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0640, Sharpe=+0.4387)
- Admission: Train IC=+0.2107, Deflated=+0.2118, IR=0.68, Mono=0.75, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.092 | 2017: -0.076 | 2018: +0.172 | 2019: +0.089 | 2020: +0.058 | 2021: +0.135 | 2022: +0.086 | 2023: +0.089 | 2024: +0.019 | 2025: +0.052 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.165 | 2017: -0.151 | 2018: +0.413 | 2019: +0.307 | 2020: +0.166 | 2021: +0.332 | 2022: +0.213 | 2023: -0.054 | 2024: +0.196 | 2025: +0.112 | 2026: +0.141
- IC CV=0.84, Neg years (linear/tail)=1/1 of 8, Half ratio=0.70, Recency ratio=0.74
- Early IC=+0.1496, Recent IC=+0.1104, 1st-half IC=+0.1295, 2nd-half IC=+0.0905, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.036, Q2=+0.009, Q3_mid=+0.059, Q4=+0.234, Q5_high_vol=+0.177

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0592, Sharpe=+0.4308)
- Admission: Train IC=+0.2181, Deflated=+0.2193, IR=0.53, Mono=0.65, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.090 | 2017: +0.021 | 2018: +0.183 | 2019: +0.078 | 2020: -0.001 | 2021: +0.127 | 2022: +0.049 | 2023: +0.177 | 2024: +0.057 | 2025: +0.025 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.132 | 2017: +0.156 | 2018: +0.359 | 2019: +0.261 | 2020: +0.068 | 2021: +0.397 | 2022: +0.172 | 2023: +0.424 | 2024: +0.242 | 2025: -0.047 | 2026: -0.082
- IC CV=0.68, Neg years (linear/tail)=1/0 of 8, Half ratio=0.57, Recency ratio=0.87
- Early IC=+0.1009, Recent IC=+0.0882, 1st-half IC=+0.1180, 2nd-half IC=+0.0669, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.044, Q2=+0.033, Q3_mid=+0.085, Q4=+0.110, Q5_high_vol=+0.166

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0567, Sharpe=+0.4294)
- Admission: Train IC=+0.2244, Deflated=+0.2251, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.054 | 2017: +0.002 | 2018: +0.173 | 2019: +0.051 | 2020: -0.002 | 2021: +0.178 | 2022: +0.055 | 2023: +0.191 | 2024: +0.025 | 2025: +0.114 | 2026: -0.181
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.202 | 2017: +0.155 | 2018: +0.396 | 2019: +0.184 | 2020: +0.071 | 2021: +0.366 | 2022: +0.371 | 2023: +0.352 | 2024: +0.077 | 2025: +0.083 | 2026: +0.009
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=0.72, Recency ratio=1.37
- Early IC=+0.0853, Recent IC=+0.1167, 1st-half IC=+0.1042, 2nd-half IC=+0.0751, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.029, Q3_mid=+0.076, Q4=+0.086, Q5_high_vol=+0.173

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0694, Sharpe=+0.4182)
- Admission: Train IC=+0.2218, Deflated=+0.2227, IR=0.62, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.114 | 2017: +0.003 | 2018: +0.209 | 2019: +0.105 | 2020: +0.047 | 2021: +0.145 | 2022: +0.084 | 2023: +0.107 | 2024: +0.016 | 2025: +0.068 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.209 | 2016: +0.113 | 2017: +0.049 | 2018: +0.274 | 2019: +0.240 | 2020: +0.153 | 2021: +0.452 | 2022: +0.271 | 2023: +0.061 | 2024: +0.162 | 2025: +0.221 | 2026: +0.095
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.70
- Early IC=+0.1644, Recent IC=+0.1143, 1st-half IC=+0.1540, 2nd-half IC=+0.0939, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.043, Q3_mid=+0.066, Q4=+0.201, Q5_high_vol=+0.196

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration`** (Lock IC=+0.0560, Sharpe=+0.4156)
- Admission: Train IC=+0.1733, Deflated=+0.1746, IR=0.66, Mono=0.70, p=0.0006, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.093 | 2017: -0.029 | 2018: +0.137 | 2019: +0.052 | 2020: +0.051 | 2021: +0.165 | 2022: -0.002 | 2023: +0.151 | 2024: +0.064 | 2025: +0.047 | 2026: -0.158
- Yearly Tail ICs:   2015: +0.048 | 2016: +0.253 | 2017: +0.048 | 2018: +0.335 | 2019: +0.060 | 2020: +0.199 | 2021: +0.395 | 2022: +0.119 | 2023: +0.195 | 2024: +0.217 | 2025: -0.004 | 2026: -0.304
- IC CV=0.87, Neg years (linear/tail)=2/0 of 8, Half ratio=0.74, Recency ratio=0.87
- Early IC=+0.0934, Recent IC=+0.0817, 1st-half IC=+0.0887, 2nd-half IC=+0.0653, Neg regimes=0/5
- Weak component: `volume_concentration` (CV=1.15)
- Regime ICs: Q1_low_vol=+0.001, Q2=+0.014, Q3_mid=+0.048, Q4=+0.129, Q5_high_vol=+0.155

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0660, Sharpe=+0.4096)
- Admission: Train IC=+0.2128, Deflated=+0.2133, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.120 | 2017: -0.007 | 2018: +0.221 | 2019: +0.091 | 2020: +0.054 | 2021: +0.167 | 2022: +0.073 | 2023: +0.126 | 2024: +0.029 | 2025: +0.075 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.139 | 2016: +0.152 | 2017: +0.035 | 2018: +0.335 | 2019: +0.134 | 2020: +0.111 | 2021: +0.396 | 2022: +0.284 | 2023: +0.138 | 2024: +0.168 | 2025: +0.080 | 2026: +0.110
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=0.62, Recency ratio=0.77
- Early IC=+0.1572, Recent IC=+0.1204, 1st-half IC=+0.1530, 2nd-half IC=+0.0949, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.044, Q3_mid=+0.062, Q4=+0.203, Q5_high_vol=+0.206

**`combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`** (Lock IC=+0.0524, Sharpe=+0.3920)
- Admission: Train IC=+0.1980, Deflated=+0.1978, IR=0.58, Mono=0.72, p=0.0002, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.029 | 2017: -0.055 | 2018: +0.074 | 2019: +0.066 | 2020: +0.047 | 2021: +0.201 | 2022: +0.083 | 2023: +0.112 | 2024: +0.008 | 2025: +0.075 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.317 | 2016: +0.102 | 2017: +0.012 | 2018: +0.266 | 2019: +0.137 | 2020: +0.080 | 2021: +0.304 | 2022: +0.275 | 2023: +0.188 | 2024: +0.175 | 2025: +0.228 | 2026: +0.130
- IC CV=0.99, Neg years (linear/tail)=1/0 of 8, Half ratio=1.21, Recency ratio=1.26
- Early IC=+0.1126, Recent IC=+0.1421, 1st-half IC=+0.0863, 2nd-half IC=+0.1046, Neg regimes=1/5
- Weak component: `morning_volume_weighted_momentum` (CV=2.01)
- Regime ICs: Q1_low_vol=-0.014, Q2=+0.005, Q3_mid=+0.083, Q4=+0.223, Q5_high_vol=+0.115

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0632, Sharpe=+0.3639)
- Admission: Train IC=+0.2852, Deflated=+0.2860, IR=0.80, Mono=0.80, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.090 | 2017: -0.044 | 2018: +0.215 | 2019: +0.118 | 2020: +0.070 | 2021: +0.175 | 2022: +0.012 | 2023: +0.138 | 2024: +0.066 | 2025: +0.033 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.289 | 2016: +0.145 | 2017: +0.079 | 2018: +0.385 | 2019: +0.374 | 2020: +0.164 | 2021: +0.510 | 2022: +0.235 | 2023: +0.115 | 2024: +0.335 | 2025: -0.048 | 2026: +0.050
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=0.61, Recency ratio=0.56
- Early IC=+0.1665, Recent IC=+0.0937, 1st-half IC=+0.1548, 2nd-half IC=+0.0949, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.003, Q2=+0.013, Q3_mid=+0.074, Q4=+0.234, Q5_high_vol=+0.193

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0682, Sharpe=+0.3507)
- Admission: Train IC=+0.2426, Deflated=+0.2433, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.108 | 2017: +0.023 | 2018: +0.214 | 2019: +0.106 | 2020: +0.039 | 2021: +0.141 | 2022: +0.070 | 2023: +0.131 | 2024: +0.015 | 2025: +0.083 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.052 | 2017: -0.006 | 2018: +0.295 | 2019: +0.182 | 2020: +0.237 | 2021: +0.441 | 2022: +0.322 | 2023: +0.243 | 2024: +0.097 | 2025: +0.166 | 2026: +0.041
- IC CV=0.57, Neg years (linear/tail)=0/1 of 8, Half ratio=0.59, Recency ratio=0.70
- Early IC=+0.1502, Recent IC=+0.1055, 1st-half IC=+0.1514, 2nd-half IC=+0.0897, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.047, Q3_mid=+0.076, Q4=+0.184, Q5_high_vol=+0.184

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0521, Sharpe=+0.3504)
- Admission: Train IC=+0.1940, Deflated=+0.1950, IR=0.75, Mono=0.78, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.88, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=1.55
- Early IC=+0.0700, Recent IC=+0.1088, 1st-half IC=+0.0824, 2nd-half IC=+0.0707, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.035, Q2=-0.007, Q3_mid=+0.042, Q4=+0.087, Q5_high_vol=+0.174

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0543, Sharpe=+0.3473)
- Admission: Train IC=+0.2634, Deflated=+0.2636, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.074 | 2018: +0.167 | 2019: +0.086 | 2020: +0.075 | 2021: +0.151 | 2022: +0.094 | 2023: +0.091 | 2024: +0.027 | 2025: +0.042 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.194 | 2016: +0.223 | 2017: -0.034 | 2018: +0.421 | 2019: +0.216 | 2020: +0.179 | 2021: +0.406 | 2022: +0.271 | 2023: +0.145 | 2024: +0.209 | 2025: +0.119 | 2026: +0.191
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=0.75, Recency ratio=0.80
- Early IC=+0.1528, Recent IC=+0.1228, 1st-half IC=+0.1276, 2nd-half IC=+0.0952, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.020, Q2=+0.030, Q3_mid=+0.059, Q4=+0.209, Q5_high_vol=+0.191

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0588, Sharpe=+0.3446)
- Admission: Train IC=+0.2066, Deflated=+0.2074, IR=0.65, Mono=0.71, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.105 | 2017: -0.059 | 2018: +0.210 | 2019: +0.080 | 2020: +0.073 | 2021: +0.170 | 2022: +0.066 | 2023: +0.122 | 2024: +0.032 | 2025: +0.069 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.023 | 2016: +0.129 | 2017: +0.079 | 2018: +0.399 | 2019: +0.276 | 2020: +0.059 | 2021: +0.349 | 2022: +0.219 | 2023: +0.091 | 2024: +0.212 | 2025: +0.079 | 2026: +0.042
- IC CV=0.77, Neg years (linear/tail)=1/0 of 8, Half ratio=0.69, Recency ratio=0.81
- Early IC=+0.1456, Recent IC=+0.1183, 1st-half IC=+0.1353, 2nd-half IC=+0.0939, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.015, Q2=+0.020, Q3_mid=+0.063, Q4=+0.222, Q5_high_vol=+0.195

**`combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0675, Sharpe=+0.3265)
- Admission: Train IC=+0.1805, Deflated=+0.1820, IR=0.54, Mono=0.68, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.064 | 2017: -0.030 | 2018: +0.224 | 2019: +0.106 | 2020: +0.022 | 2021: +0.149 | 2022: +0.020 | 2023: +0.118 | 2024: +0.037 | 2025: +0.074 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.125 | 2016: +0.061 | 2017: -0.098 | 2018: +0.412 | 2019: +0.306 | 2020: +0.194 | 2021: +0.329 | 2022: +0.160 | 2023: +0.090 | 2024: +0.170 | 2025: +0.022 | 2026: +0.266
- IC CV=0.91, Neg years (linear/tail)=1/1 of 8, Half ratio=0.62, Recency ratio=0.62
- Early IC=+0.1352, Recent IC=+0.0844, 1st-half IC=+0.1248, 2nd-half IC=+0.0775, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.018, Q3_mid=+0.074, Q4=+0.190, Q5_high_vol=+0.179

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0703, Sharpe=+0.3240)
- Admission: Train IC=+0.2764, Deflated=+0.2775, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.90, Neg years (linear/tail)=1/0 of 8, Half ratio=0.73, Recency ratio=0.73
- Early IC=+0.1479, Recent IC=+0.1075, 1st-half IC=+0.1387, 2nd-half IC=+0.1018, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.016, Q2=+0.030, Q3_mid=+0.061, Q4=+0.251, Q5_high_vol=+0.183

**`combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0566, Sharpe=+0.3084)
- Admission: Train IC=+0.2409, Deflated=+0.2417, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.085 | 2017: +0.041 | 2018: +0.223 | 2019: +0.065 | 2020: -0.027 | 2021: +0.144 | 2022: +0.066 | 2023: +0.176 | 2024: +0.015 | 2025: +0.079 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.021 | 2017: +0.243 | 2018: +0.341 | 2019: +0.287 | 2020: +0.034 | 2021: +0.424 | 2022: +0.322 | 2023: +0.363 | 2024: +0.081 | 2025: -0.074 | 2026: -0.164
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.51, Recency ratio=1.10
- Early IC=+0.0950, Recent IC=+0.1049, 1st-half IC=+0.1271, 2nd-half IC=+0.0652, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.073, Q3_mid=+0.100, Q4=+0.084, Q5_high_vol=+0.150

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0677, Sharpe=+0.2304)
- Admission: Train IC=+0.1869, Deflated=+0.1879, IR=0.60, Mono=0.71, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.101 | 2017: -0.015 | 2018: +0.181 | 2019: +0.097 | 2020: +0.044 | 2021: +0.137 | 2022: +0.083 | 2023: +0.080 | 2024: +0.013 | 2025: +0.051 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.166 | 2016: +0.073 | 2017: -0.074 | 2018: +0.363 | 2019: +0.184 | 2020: +0.254 | 2021: +0.261 | 2022: +0.240 | 2023: -0.062 | 2024: +0.205 | 2025: +0.098 | 2026: +0.134
- IC CV=0.66, Neg years (linear/tail)=1/1 of 8, Half ratio=0.62, Recency ratio=0.68
- Early IC=+0.1614, Recent IC=+0.1100, 1st-half IC=+0.1453, 2nd-half IC=+0.0893, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.019, Q3_mid=+0.058, Q4=+0.206, Q5_high_vol=+0.185

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0524, Sharpe=+0.2193)
- Admission: Train IC=+0.1836, Deflated=+0.1849, IR=0.57, Mono=0.73, p=0.0004, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156 | 2022: +0.028 | 2023: +0.137 | 2024: +0.039 | 2025: +0.058 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.055 | 2017: +0.207 | 2018: +0.385 | 2019: +0.133 | 2020: +0.033 | 2021: +0.203 | 2022: +0.122 | 2023: +0.108 | 2024: +0.061 | 2025: +0.105 | 2026: -0.330
- IC CV=0.65, Neg years (linear/tail)=1/0 of 8, Half ratio=0.63, Recency ratio=0.92
- Early IC=+0.1003, Recent IC=+0.0922, 1st-half IC=+0.1135, 2nd-half IC=+0.0718, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.055, Q3_mid=+0.086, Q4=+0.086, Q5_high_vol=+0.152

**`combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0622, Sharpe=+0.2186)
- Admission: Train IC=+0.2329, Deflated=+0.2342, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.105 | 2017: -0.070 | 2018: +0.211 | 2019: +0.091 | 2020: +0.066 | 2021: +0.154 | 2022: +0.079 | 2023: +0.113 | 2024: +0.028 | 2025: +0.059 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.190 | 2017: -0.038 | 2018: +0.433 | 2019: +0.333 | 2020: +0.048 | 2021: +0.349 | 2022: +0.232 | 2023: +0.062 | 2024: +0.219 | 2025: +0.104 | 2026: +0.123
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=0.69, Recency ratio=0.76
- Early IC=+0.1539, Recent IC=+0.1163, 1st-half IC=+0.1388, 2nd-half IC=+0.0951, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.027, Q2=+0.026, Q3_mid=+0.066, Q4=+0.235, Q5_high_vol=+0.192

**`combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0742, Sharpe=+0.1837)
- Admission: Train IC=+0.2261, Deflated=+0.2276, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.058 | 2017: -0.074 | 2018: +0.198 | 2019: +0.116 | 2020: +0.049 | 2021: +0.162 | 2022: +0.020 | 2023: +0.128 | 2024: +0.052 | 2025: +0.060 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.255 | 2016: +0.155 | 2017: -0.045 | 2018: +0.362 | 2019: +0.401 | 2020: +0.121 | 2021: +0.372 | 2022: +0.206 | 2023: +0.115 | 2024: +0.243 | 2025: -0.069 | 2026: +0.257
- IC CV=1.00, Neg years (linear/tail)=1/1 of 8, Half ratio=0.68, Recency ratio=0.63
- Early IC=+0.1448, Recent IC=+0.0906, 1st-half IC=+0.1326, 2nd-half IC=+0.0901, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=1.09)
- Regime ICs: Q1_low_vol=-0.029, Q2=+0.015, Q3_mid=+0.056, Q4=+0.244, Q5_high_vol=+0.177

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0573, Sharpe=+0.1800)
- Admission: Train IC=+0.2335, Deflated=+0.2348, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.079 | 2017: +0.004 | 2018: +0.216 | 2019: +0.088 | 2020: +0.020 | 2021: +0.163 | 2022: +0.034 | 2023: +0.164 | 2024: +0.052 | 2025: +0.040 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.062 | 2016: +0.104 | 2017: +0.156 | 2018: +0.356 | 2019: +0.347 | 2020: +0.114 | 2021: +0.470 | 2022: +0.092 | 2023: +0.262 | 2024: +0.174 | 2025: -0.080 | 2026: -0.025
- IC CV=0.78, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=1.16
- Early IC=+0.0848, Recent IC=+0.0984, 1st-half IC=+0.1172, 2nd-half IC=+0.0795, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.016, Q3_mid=+0.094, Q4=+0.132, Q5_high_vol=+0.166

**`combo_tri_mean__max_up_ret__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0637, Sharpe=+0.1613)
- Admission: Train IC=+0.2134, Deflated=+0.2142, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.085 | 2017: +0.035 | 2018: +0.206 | 2019: +0.068 | 2020: -0.007 | 2021: +0.174 | 2022: +0.054 | 2023: +0.181 | 2024: +0.029 | 2025: +0.097 | 2026: -0.148
- Yearly Tail ICs:   2015: +0.074 | 2016: +0.122 | 2017: +0.117 | 2018: +0.480 | 2019: +0.139 | 2020: +0.031 | 2021: +0.331 | 2022: +0.337 | 2023: +0.364 | 2024: +0.114 | 2025: +0.045 | 2026: -0.077
- IC CV=0.73, Neg years (linear/tail)=1/0 of 8, Half ratio=0.64, Recency ratio=1.11
- Early IC=+0.1032, Recent IC=+0.1140, 1st-half IC=+0.1215, 2nd-half IC=+0.0773, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.046, Q3_mid=+0.086, Q4=+0.100, Q5_high_vol=+0.172

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0540, Sharpe=+0.0387)
- Admission: Train IC=+0.2172, Deflated=+0.2175, IR=0.79, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.030 | 2017: +0.039 | 2018: +0.150 | 2019: +0.045 | 2020: +0.010 | 2021: +0.192 | 2022: +0.045 | 2023: +0.196 | 2024: +0.037 | 2025: +0.104 | 2026: -0.207
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.101 | 2017: +0.163 | 2018: +0.462 | 2019: +0.214 | 2020: +0.210 | 2021: +0.316 | 2022: +0.242 | 2023: +0.205 | 2024: +0.092 | 2025: +0.205 | 2026: -0.351
- IC CV=0.80, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=1.95
- Early IC=+0.0610, Recent IC=+0.1187, 1st-half IC=+0.0886, 2nd-half IC=+0.0770, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.024, Q3_mid=+0.050, Q4=+0.084, Q5_high_vol=+0.158

**`star50_limit_proximity_early`** (Lock IC=+0.0606, Sharpe=+0.0343)
- Admission: Train IC=+0.1720, Deflated=+0.1727, IR=0.46, Mono=0.70, p=0.0012, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.059 | 2017: -0.103 | 2018: +0.108 | 2019: +0.076 | 2020: +0.041 | 2021: +0.102 | 2022: +0.097 | 2023: +0.030 | 2024: +0.001 | 2025: +0.045 | 2026: +0.162
- Yearly Tail ICs:   2015: +0.158 | 2016: +0.132 | 2017: -0.017 | 2018: +0.273 | 2019: +0.161 | 2020: +0.180 | 2021: +0.093 | 2022: +0.181 | 2023: -0.240 | 2024: +0.224 | 2025: -0.012 | 2026: +0.288
- IC CV=1.09, Neg years (linear/tail)=1/1 of 8, Half ratio=0.76, Recency ratio=0.81
- Early IC=+0.1228, Recent IC=+0.0998, 1st-half IC=+0.1025, 2nd-half IC=+0.0783, Neg regimes=2/5
- Regime ICs: Q1_low_vol=-0.040, Q2=-0.001, Q3_mid=+0.021, Q4=+0.200, Q5_high_vol=+0.152

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0662, Sharpe=+0.0044)
- Admission: Train IC=+0.2243, Deflated=+0.2248, IR=0.57, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109 | 2023: +0.058 | 2024: +0.021 | 2025: +0.045 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.260 | 2017: -0.063 | 2018: +0.287 | 2019: +0.204 | 2020: +0.254 | 2021: +0.174 | 2022: +0.239 | 2023: -0.083 | 2024: +0.166 | 2025: -0.078 | 2026: +0.337
- IC CV=1.02, Neg years (linear/tail)=1/1 of 8, Half ratio=0.66, Recency ratio=0.75
- Early IC=+0.1357, Recent IC=+0.1021, 1st-half IC=+0.1154, 2nd-half IC=+0.0759, Neg regimes=1/5
- Regime ICs: Q1_low_vol=-0.037, Q2=+0.017, Q3_mid=+0.018, Q4=+0.198, Q5_high_vol=+0.167

**`combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0596, Sharpe=+0.0022)
- Admission: Train IC=+0.2101, Deflated=+0.2106, IR=0.68, Mono=0.74, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.089 | 2016: +0.103 | 2017: +0.047 | 2018: +0.188 | 2019: +0.070 | 2020: +0.029 | 2021: +0.190 | 2022: +0.006 | 2023: +0.147 | 2024: +0.049 | 2025: +0.091 | 2026: -0.136
- Yearly Tail ICs:   2015: +0.083 | 2016: +0.139 | 2017: +0.063 | 2018: +0.428 | 2019: +0.182 | 2020: +0.153 | 2021: +0.367 | 2022: +0.345 | 2023: +0.190 | 2024: +0.108 | 2025: +0.143 | 2026: -0.344
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=1.02
- Early IC=+0.0960, Recent IC=+0.0977, 1st-half IC=+0.1116, 2nd-half IC=+0.0769, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.056, Q3_mid=+0.059, Q4=+0.125, Q5_high_vol=+0.140

### 500ETF — `single` True Positives

**`combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.1041, Sharpe=+1.3062)
- Admission: Train IC=+0.2717, Deflated=+0.2732, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.060 | 2017: +0.196 | 2018: +0.089 | 2019: +0.060 | 2020: +0.087 | 2021: +0.049 | 2022: +0.058 | 2023: +0.091 | 2024: +0.124 | 2025: +0.112 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.132 | 2017: +0.365 | 2018: +0.286 | 2019: +0.114 | 2020: +0.273 | 2021: +0.046 | 2022: +0.306 | 2023: +0.033 | 2024: +0.324 | 2025: +0.028 | 2026: +0.175
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.48
- Early IC=+0.1110, Recent IC=+0.0535, 1st-half IC=+0.1277, 2nd-half IC=+0.0693, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.012, Q3_mid=+0.091, Q4=+0.158, Q5_high_vol=+0.089

**`combo_rank_min__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1205, Sharpe=+1.2069)
- Admission: Train IC=+0.2835, Deflated=+0.2853, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.062 | 2017: +0.234 | 2018: +0.094 | 2019: +0.126 | 2020: +0.128 | 2021: +0.102 | 2022: +0.063 | 2023: +0.081 | 2024: +0.147 | 2025: +0.138 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.179 | 2017: +0.308 | 2018: +0.369 | 2019: +0.230 | 2020: +0.307 | 2021: +0.069 | 2022: +0.163 | 2023: +0.183 | 2024: +0.355 | 2025: +0.082 | 2026: +0.280
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.60
- Early IC=+0.1390, Recent IC=+0.0839, 1st-half IC=+0.1552, 2nd-half IC=+0.1112, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.005, Q3_mid=+0.139, Q4=+0.181, Q5_high_vol=+0.144

**`combo_rank_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1199, Sharpe=+1.1425)
- Admission: Train IC=+0.2737, Deflated=+0.2753, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.073 | 2017: +0.226 | 2018: +0.079 | 2019: +0.082 | 2020: +0.119 | 2021: +0.089 | 2022: +0.032 | 2023: +0.095 | 2024: +0.142 | 2025: +0.138 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.208 | 2017: +0.338 | 2018: +0.282 | 2019: +0.119 | 2020: +0.215 | 2021: +0.215 | 2022: +0.160 | 2023: +0.008 | 2024: +0.221 | 2025: +0.089 | 2026: +0.313
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.43
- Early IC=+0.1468, Recent IC=+0.0633, 1st-half IC=+0.1550, 2nd-half IC=+0.0858, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.008, Q3_mid=+0.118, Q4=+0.175, Q5_high_vol=+0.118

**`combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0952, Sharpe=+1.1424)
- Admission: Train IC=+0.2458, Deflated=+0.2464, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.066 | 2017: +0.201 | 2018: +0.082 | 2019: +0.010 | 2020: +0.122 | 2021: +0.021 | 2022: -0.021 | 2023: +0.093 | 2024: +0.066 | 2025: +0.134 | 2026: +0.052
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.187 | 2017: +0.262 | 2018: +0.320 | 2019: +0.071 | 2020: +0.327 | 2021: -0.003 | 2022: +0.085 | 2023: +0.004 | 2024: +0.393 | 2025: +0.281 | 2026: +0.155
- IC CV=0.90, Neg years (linear/tail)=1/1 of 8, Half ratio=0.31, Recency ratio=0.00
- Early IC=+0.1105, Recent IC=+0.0002, 1st-half IC=+0.1395, 2nd-half IC=+0.0426, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.153, Q2=-0.006, Q3_mid=+0.065, Q4=+0.166, Q5_high_vol=+0.066

**`combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.1152, Sharpe=+1.1416)
- Admission: Train IC=+0.2647, Deflated=+0.2663, IR=0.68, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.071 | 2017: +0.208 | 2018: +0.175 | 2019: +0.129 | 2020: +0.108 | 2021: +0.113 | 2022: +0.045 | 2023: +0.104 | 2024: +0.124 | 2025: +0.136 | 2026: +0.068
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.062 | 2017: +0.291 | 2018: +0.373 | 2019: +0.272 | 2020: +0.210 | 2021: +0.106 | 2022: +0.153 | 2023: +0.270 | 2024: +0.350 | 2025: +0.257 | 2026: +0.250
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.49
- Early IC=+0.1617, Recent IC=+0.0789, 1st-half IC=+0.1865, 2nd-half IC=+0.0970, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.013, Q3_mid=+0.129, Q4=+0.213, Q5_high_vol=+0.146

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1058, Sharpe=+1.1405)
- Admission: Train IC=+0.2233, Deflated=+0.2239, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.121 | 2017: +0.105 | 2018: +0.199 | 2019: +0.090 | 2020: +0.107 | 2021: +0.138 | 2022: +0.091 | 2023: +0.051 | 2024: +0.124 | 2025: +0.140 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.434 | 2016: +0.180 | 2017: +0.216 | 2018: +0.386 | 2019: -0.033 | 2020: +0.112 | 2021: +0.323 | 2022: +0.086 | 2023: +0.203 | 2024: +0.170 | 2025: +0.262 | 2026: +0.288
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=0.59
- Early IC=+0.1937, Recent IC=+0.1144, 1st-half IC=+0.1889, 2nd-half IC=+0.1066, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.034, Q3_mid=+0.109, Q4=+0.170, Q5_high_vol=+0.234

**`combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.1048, Sharpe=+1.1248)
- Admission: Train IC=+0.2477, Deflated=+0.2488, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.038 | 2017: +0.215 | 2018: +0.063 | 2019: +0.038 | 2020: +0.130 | 2021: +0.019 | 2022: -0.008 | 2023: +0.079 | 2024: +0.101 | 2025: +0.134 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.151 | 2017: +0.271 | 2018: +0.307 | 2019: +0.055 | 2020: +0.321 | 2021: +0.098 | 2022: +0.096 | 2023: -0.072 | 2024: +0.377 | 2025: +0.160 | 2026: +0.278
- IC CV=0.90, Neg years (linear/tail)=1/0 of 8, Half ratio=0.41, Recency ratio=0.06
- Early IC=+0.1127, Recent IC=+0.0062, 1st-half IC=+0.1313, 2nd-half IC=+0.0533, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.155, Q2=-0.031, Q3_mid=+0.082, Q4=+0.144, Q5_high_vol=+0.094

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1153, Sharpe=+1.1001)
- Admission: Train IC=+0.2720, Deflated=+0.2731, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.099 | 2017: +0.233 | 2018: +0.132 | 2019: +0.098 | 2020: +0.133 | 2021: +0.117 | 2022: +0.056 | 2023: +0.096 | 2024: +0.118 | 2025: +0.140 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.228 | 2017: +0.343 | 2018: +0.291 | 2019: +0.226 | 2020: +0.281 | 2021: +0.290 | 2022: +0.057 | 2023: +0.199 | 2024: +0.212 | 2025: +0.046 | 2026: +0.090
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.58
- Early IC=+0.1532, Recent IC=+0.0883, 1st-half IC=+0.1798, 2nd-half IC=+0.1048, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.045, Q3_mid=+0.118, Q4=+0.204, Q5_high_vol=+0.129

**`combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1126, Sharpe=+1.0957)
- Admission: Train IC=+0.3103, Deflated=+0.3111, IR=0.90, Mono=0.79, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.115 | 2017: +0.200 | 2018: +0.107 | 2019: +0.129 | 2020: +0.146 | 2021: +0.154 | 2022: +0.075 | 2023: +0.105 | 2024: +0.154 | 2025: +0.100 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.272 | 2016: +0.182 | 2017: +0.269 | 2018: +0.350 | 2019: +0.292 | 2020: +0.303 | 2021: +0.216 | 2022: +0.320 | 2023: +0.234 | 2024: +0.353 | 2025: +0.006 | 2026: +0.150
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.66
- Early IC=+0.1752, Recent IC=+0.1148, 1st-half IC=+0.1729, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.027, Q3_mid=+0.153, Q4=+0.213, Q5_high_vol=+0.149

**`combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0975, Sharpe=+1.0302)
- Admission: Train IC=+0.2474, Deflated=+0.2481, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.068 | 2017: +0.208 | 2018: +0.088 | 2019: +0.022 | 2020: +0.124 | 2021: +0.030 | 2022: -0.016 | 2023: +0.077 | 2024: +0.067 | 2025: +0.136 | 2026: +0.066
- Yearly Tail ICs:   2015: +0.321 | 2016: +0.232 | 2017: +0.295 | 2018: +0.341 | 2019: +0.034 | 2020: +0.327 | 2021: +0.259 | 2022: +0.038 | 2023: -0.061 | 2024: +0.343 | 2025: +0.204 | 2026: +0.189
- IC CV=0.82, Neg years (linear/tail)=1/0 of 8, Half ratio=0.34, Recency ratio=0.07
- Early IC=+0.1114, Recent IC=+0.0073, 1st-half IC=+0.1468, 2nd-half IC=+0.0500, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.003, Q3_mid=+0.071, Q4=+0.170, Q5_high_vol=+0.072

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1040, Sharpe=+1.0270)
- Admission: Train IC=+0.3147, Deflated=+0.3164, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.099 | 2017: +0.211 | 2018: +0.217 | 2019: +0.157 | 2020: +0.122 | 2021: +0.133 | 2022: +0.050 | 2023: +0.090 | 2024: +0.105 | 2025: +0.117 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.254 | 2017: +0.299 | 2018: +0.479 | 2019: +0.376 | 2020: +0.312 | 2021: +0.039 | 2022: +0.093 | 2023: +0.141 | 2024: +0.278 | 2025: +0.150 | 2026: +0.202
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.45
- Early IC=+0.2049, Recent IC=+0.0914, 1st-half IC=+0.2303, 2nd-half IC=+0.1135, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.024, Q3_mid=+0.152, Q4=+0.226, Q5_high_vol=+0.221

**`combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early`** (Lock IC=+0.1088, Sharpe=+0.9778)
- Admission: Train IC=+0.2661, Deflated=+0.2673, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.046 | 2017: +0.223 | 2018: +0.072 | 2019: +0.069 | 2020: +0.104 | 2021: +0.067 | 2022: +0.039 | 2023: +0.079 | 2024: +0.119 | 2025: +0.124 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.167 | 2017: +0.388 | 2018: +0.314 | 2019: +0.091 | 2020: +0.186 | 2021: +0.145 | 2022: +0.211 | 2023: -0.043 | 2024: +0.320 | 2025: +0.084 | 2026: +0.230
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.49
- Early IC=+0.1129, Recent IC=+0.0558, 1st-half IC=+0.1333, 2nd-half IC=+0.0756, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.001, Q3_mid=+0.104, Q4=+0.159, Q5_high_vol=+0.092

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0948, Sharpe=+0.9751)
- Admission: Train IC=+0.2828, Deflated=+0.2845, IR=0.55, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.073 | 2017: +0.197 | 2018: +0.154 | 2019: +0.172 | 2020: +0.113 | 2021: +0.095 | 2022: +0.028 | 2023: +0.065 | 2024: +0.113 | 2025: +0.126 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.242 | 2016: +0.098 | 2017: +0.247 | 2018: +0.372 | 2019: +0.331 | 2020: +0.242 | 2021: +0.067 | 2022: +0.129 | 2023: +0.097 | 2024: +0.318 | 2025: +0.123 | 2026: +0.108
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.34
- Early IC=+0.1810, Recent IC=+0.0614, 1st-half IC=+0.1905, 2nd-half IC=+0.1044, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.178, Q2=-0.030, Q3_mid=+0.121, Q4=+0.185, Q5_high_vol=+0.205

**`combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range`** (Lock IC=+0.1117, Sharpe=+0.9540)
- Admission: Train IC=+0.2655, Deflated=+0.2665, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.123 | 2017: +0.207 | 2018: +0.146 | 2019: +0.104 | 2020: +0.147 | 2021: +0.068 | 2022: +0.101 | 2023: +0.072 | 2024: +0.110 | 2025: +0.116 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.187 | 2016: +0.229 | 2017: +0.304 | 2018: +0.296 | 2019: +0.254 | 2020: +0.194 | 2021: +0.167 | 2022: +0.157 | 2023: -0.004 | 2024: +0.264 | 2025: +0.103 | 2026: +0.145
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.43
- Early IC=+0.1938, Recent IC=+0.0841, 1st-half IC=+0.2082, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.017, Q3_mid=+0.156, Q4=+0.177, Q5_high_vol=+0.189

**`combo_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1261, Sharpe=+0.9460)
- Admission: Train IC=+0.2474, Deflated=+0.2488, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.066 | 2017: +0.245 | 2018: +0.190 | 2019: +0.134 | 2020: +0.152 | 2021: +0.084 | 2022: +0.097 | 2023: +0.130 | 2024: +0.130 | 2025: +0.155 | 2026: +0.048
- Yearly Tail ICs:   2015: +0.319 | 2016: -0.047 | 2017: +0.247 | 2018: +0.221 | 2019: +0.245 | 2020: +0.221 | 2021: +0.130 | 2022: +0.245 | 2023: +0.289 | 2024: +0.228 | 2025: +0.157 | 2026: -0.057
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.55, Recency ratio=0.52
- Early IC=+0.1747, Recent IC=+0.0903, 1st-half IC=+0.2173, 2nd-half IC=+0.1188, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.020, Q3_mid=+0.153, Q4=+0.171, Q5_high_vol=+0.223

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1216, Sharpe=+0.9299)
- Admission: Train IC=+0.2752, Deflated=+0.2762, IR=0.72, Mono=0.73, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.138 | 2017: +0.218 | 2018: +0.124 | 2019: +0.143 | 2020: +0.175 | 2021: +0.141 | 2022: +0.048 | 2023: +0.106 | 2024: +0.153 | 2025: +0.104 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.193 | 2017: +0.175 | 2018: +0.350 | 2019: +0.367 | 2020: +0.257 | 2021: +0.326 | 2022: +0.012 | 2023: +0.014 | 2024: +0.355 | 2025: +0.029 | 2026: +0.017
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.46
- Early IC=+0.2109, Recent IC=+0.0967, 1st-half IC=+0.2142, 2nd-half IC=+0.1290, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.043, Q3_mid=+0.141, Q4=+0.223, Q5_high_vol=+0.221

**`combo_clamp_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1257, Sharpe=+0.9262)
- Admission: Train IC=+0.2538, Deflated=+0.2549, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.292 | 2016: +0.085 | 2017: +0.248 | 2018: +0.183 | 2019: +0.123 | 2020: +0.176 | 2021: +0.089 | 2022: +0.119 | 2023: +0.134 | 2024: +0.123 | 2025: +0.151 | 2026: +0.048
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.259 | 2017: +0.224 | 2018: +0.229 | 2019: +0.199 | 2020: +0.202 | 2021: +0.213 | 2022: +0.279 | 2023: +0.185 | 2024: +0.349 | 2025: +0.205 | 2026: -0.277
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.55
- Early IC=+0.1885, Recent IC=+0.1042, 1st-half IC=+0.2298, 2nd-half IC=+0.1293, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.047, Q3_mid=+0.181, Q4=+0.172, Q5_high_vol=+0.245

**`combo_rank_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0976, Sharpe=+0.9250)
- Admission: Train IC=+0.2736, Deflated=+0.2754, IR=0.55, Mono=0.67, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.067 | 2017: +0.194 | 2018: +0.149 | 2019: +0.171 | 2020: +0.117 | 2021: +0.089 | 2022: +0.034 | 2023: +0.064 | 2024: +0.111 | 2025: +0.131 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.249 | 2016: +0.097 | 2017: +0.214 | 2018: +0.389 | 2019: +0.325 | 2020: +0.223 | 2021: +0.118 | 2022: +0.125 | 2023: +0.121 | 2024: +0.318 | 2025: +0.150 | 2026: +0.051
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.35
- Early IC=+0.1782, Recent IC=+0.0625, 1st-half IC=+0.1878, 2nd-half IC=+0.1059, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.031, Q3_mid=+0.123, Q4=+0.181, Q5_high_vol=+0.203

**`combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence`** (Lock IC=+0.0871, Sharpe=+0.9219)
- Admission: Train IC=+0.1857, Deflated=+0.1873, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.033 | 2017: +0.196 | 2018: +0.177 | 2019: +0.157 | 2020: +0.141 | 2021: +0.136 | 2022: +0.033 | 2023: +0.097 | 2024: +0.098 | 2025: +0.045 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.423 | 2016: +0.058 | 2017: +0.369 | 2018: +0.150 | 2019: +0.300 | 2020: +0.085 | 2021: +0.225 | 2022: +0.030 | 2023: +0.146 | 2024: +0.192 | 2025: +0.047 | 2026: +0.321
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.52
- Early IC=+0.1634, Recent IC=+0.0848, 1st-half IC=+0.1775, 2nd-half IC=+0.1195, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.020, Q3_mid=+0.176, Q4=+0.142, Q5_high_vol=+0.232

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1166, Sharpe=+0.9210)
- Admission: Train IC=+0.2943, Deflated=+0.2960, IR=0.93, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.088 | 2017: +0.219 | 2018: +0.200 | 2019: +0.125 | 2020: +0.135 | 2021: +0.155 | 2022: +0.046 | 2023: +0.113 | 2024: +0.146 | 2025: +0.125 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.144 | 2017: +0.303 | 2018: +0.435 | 2019: +0.322 | 2020: +0.225 | 2021: +0.274 | 2022: +0.244 | 2023: +0.151 | 2024: +0.290 | 2025: +0.074 | 2026: +0.224
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.68
- Early IC=+0.1476, Recent IC=+0.1006, 1st-half IC=+0.1890, 2nd-half IC=+0.1180, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.047, Q3_mid=+0.145, Q4=+0.194, Q5_high_vol=+0.153

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1215, Sharpe=+0.9205)
- Admission: Train IC=+0.3075, Deflated=+0.3095, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.045 | 2017: +0.226 | 2018: +0.140 | 2019: +0.157 | 2020: +0.154 | 2021: +0.138 | 2022: +0.032 | 2023: +0.096 | 2024: +0.174 | 2025: +0.105 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.163 | 2017: +0.307 | 2018: +0.406 | 2019: +0.362 | 2020: +0.212 | 2021: +0.216 | 2022: +0.114 | 2023: +0.006 | 2024: +0.367 | 2025: +0.039 | 2026: +0.231
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.52
- Early IC=+0.1578, Recent IC=+0.0828, 1st-half IC=+0.1832, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.041, Q3_mid=+0.153, Q4=+0.197, Q5_high_vol=+0.185

**`combo_tri_min__early_body_momentum__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1097, Sharpe=+0.9163)
- Admission: Train IC=+0.2670, Deflated=+0.2687, IR=0.66, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.062 | 2017: +0.182 | 2018: +0.106 | 2019: +0.121 | 2020: +0.092 | 2021: +0.084 | 2022: +0.073 | 2023: +0.091 | 2024: +0.125 | 2025: +0.129 | 2026: +0.075
- Yearly Tail ICs:   2015: +0.290 | 2016: +0.071 | 2017: +0.195 | 2018: +0.229 | 2019: +0.177 | 2020: +0.259 | 2021: +0.172 | 2022: +0.214 | 2023: +0.149 | 2024: +0.349 | 2025: +0.219 | 2026: +0.121
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.52
- Early IC=+0.1494, Recent IC=+0.0784, 1st-half IC=+0.1491, 2nd-half IC=+0.0922, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.056, Q3_mid=+0.119, Q4=+0.190, Q5_high_vol=+0.136

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1311, Sharpe=+0.9144)
- Admission: Train IC=+0.2592, Deflated=+0.2601, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.118 | 2017: +0.254 | 2018: +0.166 | 2019: +0.128 | 2020: +0.155 | 2021: +0.088 | 2022: +0.111 | 2023: +0.137 | 2024: +0.128 | 2025: +0.144 | 2026: +0.055
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.346 | 2017: +0.365 | 2018: +0.197 | 2019: +0.177 | 2020: +0.132 | 2021: +0.132 | 2022: +0.171 | 2023: +0.174 | 2024: +0.227 | 2025: -0.054 | 2026: -0.317
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.47
- Early IC=+0.2128, Recent IC=+0.0993, 1st-half IC=+0.2323, 2nd-half IC=+0.1225, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.053, Q3_mid=+0.173, Q4=+0.168, Q5_high_vol=+0.237

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0922, Sharpe=+0.9091)
- Admission: Train IC=+0.2210, Deflated=+0.2237, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.070 | 2017: +0.271 | 2018: +0.191 | 2019: +0.147 | 2020: +0.174 | 2021: +0.099 | 2022: +0.054 | 2023: +0.065 | 2024: +0.158 | 2025: +0.105 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.084 | 2017: +0.234 | 2018: +0.163 | 2019: +0.358 | 2020: +0.068 | 2021: +0.297 | 2022: +0.084 | 2023: +0.183 | 2024: +0.402 | 2025: +0.178 | 2026: -0.048
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.44
- Early IC=+0.1750, Recent IC=+0.0770, 1st-half IC=+0.1999, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.007, Q3_mid=+0.184, Q4=+0.152, Q5_high_vol=+0.240

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.1048, Sharpe=+0.9028)
- Admission: Train IC=+0.2897, Deflated=+0.2901, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.106 | 2017: +0.201 | 2018: +0.100 | 2019: +0.070 | 2020: +0.120 | 2021: +0.111 | 2022: +0.059 | 2023: +0.103 | 2024: +0.131 | 2025: +0.118 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.351 | 2016: +0.227 | 2017: +0.336 | 2018: +0.318 | 2019: +0.102 | 2020: +0.235 | 2021: +0.231 | 2022: +0.265 | 2023: -0.020 | 2024: +0.405 | 2025: +0.214 | 2026: +0.173
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.60
- Early IC=+0.1420, Recent IC=+0.0849, 1st-half IC=+0.1591, 2nd-half IC=+0.0901, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.019, Q3_mid=+0.129, Q4=+0.191, Q5_high_vol=+0.091

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0959, Sharpe=+0.8981)
- Admission: Train IC=+0.2905, Deflated=+0.2914, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.328 | 2016: +0.096 | 2017: +0.223 | 2018: +0.184 | 2019: +0.153 | 2020: +0.155 | 2021: +0.118 | 2022: +0.039 | 2023: +0.098 | 2024: +0.106 | 2025: +0.096 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.129 | 2017: +0.201 | 2018: +0.475 | 2019: +0.271 | 2020: +0.290 | 2021: +0.192 | 2022: +0.125 | 2023: +0.100 | 2024: +0.247 | 2025: +0.094 | 2026: +0.132
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.37
- Early IC=+0.2121, Recent IC=+0.0781, 1st-half IC=+0.2316, 2nd-half IC=+0.1183, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.025, Q3_mid=+0.142, Q4=+0.238, Q5_high_vol=+0.216

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1134, Sharpe=+0.8964)
- Admission: Train IC=+0.2807, Deflated=+0.2818, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.094 | 2017: +0.219 | 2018: +0.146 | 2019: +0.099 | 2020: +0.113 | 2021: +0.119 | 2022: +0.082 | 2023: +0.115 | 2024: +0.122 | 2025: +0.141 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.284 | 2016: +0.175 | 2017: +0.309 | 2018: +0.380 | 2019: +0.196 | 2020: +0.294 | 2021: +0.167 | 2022: +0.234 | 2023: +0.203 | 2024: +0.304 | 2025: +0.211 | 2026: +0.243
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.67
- Early IC=+0.1500, Recent IC=+0.1001, 1st-half IC=+0.1776, 2nd-half IC=+0.1041, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.043, Q3_mid=+0.125, Q4=+0.199, Q5_high_vol=+0.124

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1101, Sharpe=+0.8958)
- Admission: Train IC=+0.3102, Deflated=+0.3126, IR=0.89, Mono=0.80, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.309 | 2016: +0.078 | 2017: +0.230 | 2018: +0.229 | 2019: +0.175 | 2020: +0.154 | 2021: +0.118 | 2022: +0.036 | 2023: +0.082 | 2024: +0.135 | 2025: +0.124 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.094 | 2017: +0.322 | 2018: +0.501 | 2019: +0.257 | 2020: +0.215 | 2021: +0.185 | 2022: +0.156 | 2023: +0.198 | 2024: +0.298 | 2025: +0.247 | 2026: +0.290
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.40
- Early IC=+0.1936, Recent IC=+0.0771, 1st-half IC=+0.2242, 2nd-half IC=+0.1258, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.021, Q3_mid=+0.169, Q4=+0.224, Q5_high_vol=+0.227

**`combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.1041, Sharpe=+0.8851)
- Admission: Train IC=+0.2722, Deflated=+0.2729, IR=0.76, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.088 | 2017: +0.221 | 2018: +0.112 | 2019: +0.064 | 2020: +0.115 | 2021: +0.084 | 2022: +0.049 | 2023: +0.080 | 2024: +0.103 | 2025: +0.135 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.301 | 2017: +0.429 | 2018: +0.349 | 2019: +0.070 | 2020: +0.211 | 2021: +0.189 | 2022: +0.161 | 2023: -0.060 | 2024: +0.335 | 2025: +0.117 | 2026: +0.170
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.56
- Early IC=+0.1243, Recent IC=+0.0690, 1st-half IC=+0.1575, 2nd-half IC=+0.0819, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.033, Q3_mid=+0.098, Q4=+0.189, Q5_high_vol=+0.086

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0946, Sharpe=+0.8755)
- Admission: Train IC=+0.2620, Deflated=+0.2630, IR=0.95, Mono=0.80, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.092 | 2017: +0.126 | 2018: +0.262 | 2019: +0.168 | 2020: +0.178 | 2021: +0.173 | 2022: +0.072 | 2023: +0.092 | 2024: +0.143 | 2025: +0.071 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.210 | 2016: +0.145 | 2017: +0.301 | 2018: +0.612 | 2019: +0.185 | 2020: +0.165 | 2021: +0.286 | 2022: +0.172 | 2023: +0.266 | 2024: +0.194 | 2025: -0.001 | 2026: +0.010
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.68
- Early IC=+0.1784, Recent IC=+0.1221, 1st-half IC=+0.2129, 2nd-half IC=+0.1495, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.061, Q3_mid=+0.167, Q4=+0.174, Q5_high_vol=+0.274

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0913, Sharpe=+0.8496)
- Admission: Train IC=+0.2877, Deflated=+0.2893, IR=0.63, Mono=0.74, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.092 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.142 | 2021: +0.098 | 2022: +0.041 | 2023: +0.078 | 2024: +0.091 | 2025: +0.124 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.155 | 2017: +0.169 | 2018: +0.459 | 2019: +0.286 | 2020: +0.274 | 2021: +0.162 | 2022: +0.108 | 2023: +0.162 | 2024: +0.281 | 2025: +0.156 | 2026: +0.171
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.34
- Early IC=+0.2037, Recent IC=+0.0693, 1st-half IC=+0.2243, 2nd-half IC=+0.1165, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.009, Q3_mid=+0.132, Q4=+0.236, Q5_high_vol=+0.222

**`combo_min__star50_limit_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0907, Sharpe=+0.8442)
- Admission: Train IC=+0.2356, Deflated=+0.2364, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.045 | 2017: +0.245 | 2018: +0.050 | 2019: +0.122 | 2020: +0.087 | 2021: +0.071 | 2022: +0.033 | 2023: +0.084 | 2024: +0.110 | 2025: +0.082 | 2026: +0.048
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.120 | 2017: +0.305 | 2018: +0.320 | 2019: +0.241 | 2020: +0.180 | 2021: +0.186 | 2022: +0.160 | 2023: +0.120 | 2024: +0.112 | 2025: +0.028 | 2026: -0.126
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.42
- Early IC=+0.1227, Recent IC=+0.0518, 1st-half IC=+0.1324, 2nd-half IC=+0.0880, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.028, Q3_mid=+0.106, Q4=+0.177, Q5_high_vol=+0.100

**`combo_sig_product__max_up_ret__shaved_bar_trend_conviction`** (Lock IC=+0.1258, Sharpe=+0.8365)
- Admission: Train IC=+0.2300, Deflated=+0.2302, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.167 | 2017: +0.082 | 2018: +0.128 | 2019: +0.039 | 2020: +0.129 | 2021: +0.051 | 2022: +0.083 | 2023: +0.122 | 2024: +0.141 | 2025: +0.177 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.181 | 2017: +0.264 | 2018: +0.169 | 2019: -0.042 | 2020: +0.202 | 2021: +0.098 | 2022: +0.079 | 2023: +0.012 | 2024: +0.213 | 2025: +0.262 | 2026: -0.292
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=0.43, Recency ratio=0.32
- Early IC=+0.2111, Recent IC=+0.0673, 1st-half IC=+0.1857, 2nd-half IC=+0.0792, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.127, Q2=-0.007, Q3_mid=+0.108, Q4=+0.167, Q5_high_vol=+0.205

**`combo_rank_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1178, Sharpe=+0.8307)
- Admission: Train IC=+0.2082, Deflated=+0.2096, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.057 | 2017: +0.230 | 2018: +0.093 | 2019: +0.123 | 2020: +0.133 | 2021: +0.031 | 2022: +0.096 | 2023: +0.036 | 2024: +0.139 | 2025: +0.111 | 2026: +0.152
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.065 | 2017: +0.185 | 2018: +0.151 | 2019: +0.343 | 2020: +0.164 | 2021: +0.294 | 2022: +0.113 | 2023: +0.030 | 2024: +0.178 | 2025: +0.302 | 2026: +0.147
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.36
- Early IC=+0.1760, Recent IC=+0.0640, 1st-half IC=+0.1840, 2nd-half IC=+0.0984, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.018, Q3_mid=+0.170, Q4=+0.102, Q5_high_vol=+0.220

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1141, Sharpe=+0.8262)
- Admission: Train IC=+0.2415, Deflated=+0.2427, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.146 | 2017: +0.059 | 2018: +0.156 | 2019: +0.093 | 2020: +0.133 | 2021: +0.131 | 2022: +0.138 | 2023: +0.148 | 2024: +0.132 | 2025: +0.133 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.055 | 2017: +0.259 | 2018: +0.219 | 2019: +0.368 | 2020: +0.226 | 2021: +0.287 | 2022: +0.244 | 2023: +0.295 | 2024: +0.228 | 2025: +0.065 | 2026: +0.000
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.72
- Early IC=+0.1872, Recent IC=+0.1348, 1st-half IC=+0.1753, 2nd-half IC=+0.1241, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.053, Q3_mid=+0.144, Q4=+0.176, Q5_high_vol=+0.211

**`combo_rel_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1224, Sharpe=+0.8206)
- Admission: Train IC=+0.2483, Deflated=+0.2495, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.089 | 2017: +0.221 | 2018: +0.174 | 2019: +0.150 | 2020: +0.144 | 2021: +0.100 | 2022: +0.082 | 2023: +0.119 | 2024: +0.122 | 2025: +0.156 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.285 | 2016: +0.010 | 2017: +0.244 | 2018: +0.212 | 2019: +0.236 | 2020: +0.216 | 2021: +0.129 | 2022: +0.241 | 2023: +0.237 | 2024: +0.195 | 2025: +0.112 | 2026: -0.071
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.49
- Early IC=+0.1868, Recent IC=+0.0909, 1st-half IC=+0.2117, 2nd-half IC=+0.1209, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.033, Q3_mid=+0.149, Q4=+0.172, Q5_high_vol=+0.227

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1217, Sharpe=+0.8196)
- Admission: Train IC=+0.3308, Deflated=+0.3324, IR=1.12, Mono=0.86, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.121 | 2017: +0.223 | 2018: +0.184 | 2019: +0.172 | 2020: +0.173 | 2021: +0.142 | 2022: +0.014 | 2023: +0.106 | 2024: +0.167 | 2025: +0.090 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.402 | 2016: +0.204 | 2017: +0.346 | 2018: +0.521 | 2019: +0.344 | 2020: +0.241 | 2021: +0.291 | 2022: +0.168 | 2023: +0.117 | 2024: +0.321 | 2025: -0.031 | 2026: +0.176
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.39
- Early IC=+0.2006, Recent IC=+0.0784, 1st-half IC=+0.2191, 2nd-half IC=+0.1318, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.051, Q3_mid=+0.164, Q4=+0.217, Q5_high_vol=+0.217

**`combo_mean__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0974, Sharpe=+0.8110)
- Admission: Train IC=+0.2471, Deflated=+0.2494, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.099 | 2017: +0.225 | 2018: +0.233 | 2019: +0.144 | 2020: +0.147 | 2021: +0.137 | 2022: +0.070 | 2023: +0.092 | 2024: +0.137 | 2025: +0.110 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.579 | 2016: +0.003 | 2017: +0.197 | 2018: +0.174 | 2019: +0.354 | 2020: +0.085 | 2021: +0.440 | 2022: +0.118 | 2023: +0.085 | 2024: +0.224 | 2025: +0.148 | 2026: -0.049
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.56
- Early IC=+0.1847, Recent IC=+0.1035, 1st-half IC=+0.2132, 2nd-half IC=+0.1296, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.008, Q3_mid=+0.181, Q4=+0.180, Q5_high_vol=+0.254

**`combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range`** (Lock IC=+0.1178, Sharpe=+0.8065)
- Admission: Train IC=+0.2717, Deflated=+0.2727, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.102 | 2017: +0.227 | 2018: +0.122 | 2019: +0.078 | 2020: +0.129 | 2021: +0.108 | 2022: +0.062 | 2023: +0.102 | 2024: +0.131 | 2025: +0.149 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.282 | 2016: +0.267 | 2017: +0.323 | 2018: +0.317 | 2019: +0.071 | 2020: +0.228 | 2021: +0.201 | 2022: +0.126 | 2023: +0.016 | 2024: +0.261 | 2025: +0.226 | 2026: +0.256
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.53
- Early IC=+0.1617, Recent IC=+0.0853, 1st-half IC=+0.1818, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.051, Q3_mid=+0.123, Q4=+0.200, Q5_high_vol=+0.123

**`combo_clamp_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.1267, Sharpe=+0.8006)
- Admission: Train IC=+0.2855, Deflated=+0.2869, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.067 | 2017: +0.246 | 2018: +0.192 | 2019: +0.135 | 2020: +0.158 | 2021: +0.086 | 2022: +0.091 | 2023: +0.128 | 2024: +0.127 | 2025: +0.157 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.385 | 2016: +0.008 | 2017: +0.269 | 2018: +0.354 | 2019: +0.343 | 2020: +0.373 | 2021: +0.193 | 2022: +0.204 | 2023: +0.184 | 2024: +0.340 | 2025: +0.218 | 2026: -0.169
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.50
- Early IC=+0.1760, Recent IC=+0.0888, 1st-half IC=+0.2178, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.021, Q3_mid=+0.153, Q4=+0.169, Q5_high_vol=+0.227

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0875, Sharpe=+0.7974)
- Admission: Train IC=+0.2091, Deflated=+0.2098, IR=0.45, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.139 | 2017: +0.194 | 2018: +0.151 | 2019: +0.077 | 2020: +0.157 | 2021: +0.062 | 2022: +0.132 | 2023: +0.055 | 2024: +0.114 | 2025: +0.075 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.352 | 2017: +0.156 | 2018: +0.156 | 2019: +0.155 | 2020: +0.119 | 2021: +0.147 | 2022: +0.111 | 2023: +0.110 | 2024: +0.200 | 2025: -0.073 | 2026: -0.164
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.47
- Early IC=+0.2051, Recent IC=+0.0968, 1st-half IC=+0.2204, 2nd-half IC=+0.1113, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.023, Q3_mid=+0.183, Q4=+0.139, Q5_high_vol=+0.257

**`combo_mean__max_up_ret__close_vs_open_range`** (Lock IC=+0.0939, Sharpe=+0.7756)
- Admission: Train IC=+0.2364, Deflated=+0.2379, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.095 | 2017: +0.212 | 2018: +0.173 | 2019: +0.086 | 2020: +0.133 | 2021: +0.102 | 2022: +0.108 | 2023: +0.104 | 2024: +0.141 | 2025: +0.115 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.297 | 2017: +0.270 | 2018: +0.334 | 2019: +0.138 | 2020: +0.187 | 2021: +0.271 | 2022: +0.060 | 2023: +0.196 | 2024: +0.245 | 2025: -0.059 | 2026: -0.171
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.65
- Early IC=+0.1618, Recent IC=+0.1051, 1st-half IC=+0.1926, 2nd-half IC=+0.1109, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.025, Q3_mid=+0.177, Q4=+0.144, Q5_high_vol=+0.197

**`combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.1096, Sharpe=+0.7682)
- Admission: Train IC=+0.2893, Deflated=+0.2907, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.065 | 2017: +0.217 | 2018: +0.200 | 2019: +0.124 | 2020: +0.170 | 2021: +0.092 | 2022: +0.093 | 2023: +0.115 | 2024: +0.158 | 2025: +0.121 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.393 | 2016: +0.172 | 2017: +0.196 | 2018: +0.310 | 2019: +0.229 | 2020: +0.241 | 2021: +0.241 | 2022: +0.340 | 2023: +0.239 | 2024: +0.200 | 2025: +0.036 | 2026: -0.199
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.56
- Early IC=+0.1652, Recent IC=+0.0925, 1st-half IC=+0.1959, 2nd-half IC=+0.1260, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.016, Q3_mid=+0.200, Q4=+0.158, Q5_high_vol=+0.203

**`combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.1064, Sharpe=+0.7637)
- Admission: Train IC=+0.2205, Deflated=+0.2215, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.078 | 2017: +0.191 | 2018: +0.176 | 2019: +0.125 | 2020: +0.104 | 2021: +0.108 | 2022: +0.099 | 2023: +0.112 | 2024: +0.137 | 2025: +0.142 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.028 | 2017: +0.293 | 2018: +0.371 | 2019: +0.175 | 2020: +0.173 | 2021: +0.227 | 2022: +0.226 | 2023: +0.280 | 2024: +0.228 | 2025: +0.238 | 2026: -0.067
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.77
- Early IC=+0.1346, Recent IC=+0.1033, 1st-half IC=+0.1709, 2nd-half IC=+0.1081, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.012, Q3_mid=+0.163, Q4=+0.145, Q5_high_vol=+0.145

**`combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1078, Sharpe=+0.7630)
- Admission: Train IC=+0.2613, Deflated=+0.2624, IR=0.67, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.117 | 2017: +0.215 | 2018: +0.168 | 2019: +0.108 | 2020: +0.157 | 2021: +0.076 | 2022: +0.099 | 2023: +0.074 | 2024: +0.106 | 2025: +0.131 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.218 | 2017: +0.256 | 2018: +0.295 | 2019: +0.362 | 2020: +0.127 | 2021: +0.199 | 2022: +0.270 | 2023: +0.146 | 2024: +0.255 | 2025: +0.072 | 2026: +0.162
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.49
- Early IC=+0.1786, Recent IC=+0.0876, 1st-half IC=+0.2076, 2nd-half IC=+0.1122, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.018, Q3_mid=+0.163, Q4=+0.186, Q5_high_vol=+0.183

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0934, Sharpe=+0.7611)
- Admission: Train IC=+0.2575, Deflated=+0.2589, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.103 | 2017: +0.134 | 2018: +0.282 | 2019: +0.177 | 2020: +0.172 | 2021: +0.172 | 2022: +0.052 | 2023: +0.100 | 2024: +0.158 | 2025: +0.055 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.198 | 2017: +0.309 | 2018: +0.602 | 2019: +0.198 | 2020: +0.120 | 2021: +0.283 | 2022: +0.164 | 2023: +0.261 | 2024: +0.190 | 2025: +0.010 | 2026: +0.013
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.60
- Early IC=+0.1876, Recent IC=+0.1121, 1st-half IC=+0.2263, 2nd-half IC=+0.1449, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.070, Q3_mid=+0.186, Q4=+0.172, Q5_high_vol=+0.289

**`combo_min__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0799, Sharpe=+0.7594)
- Admission: Train IC=+0.2314, Deflated=+0.2331, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.109 | 2017: +0.160 | 2018: +0.232 | 2019: +0.127 | 2020: +0.086 | 2021: +0.119 | 2022: +0.068 | 2023: +0.080 | 2024: +0.111 | 2025: +0.099 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.392 | 2016: -0.051 | 2017: +0.304 | 2018: +0.440 | 2019: +0.123 | 2020: +0.087 | 2021: +0.270 | 2022: +0.180 | 2023: +0.190 | 2024: +0.174 | 2025: +0.197 | 2026: -0.167
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.51, Recency ratio=0.57
- Early IC=+0.1632, Recent IC=+0.0935, 1st-half IC=+0.1949, 2nd-half IC=+0.1003, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.160, Q2=-0.019, Q3_mid=+0.127, Q4=+0.165, Q5_high_vol=+0.208

**`combo_mean__max_up_ret__max_down_ret`** (Lock IC=+0.1024, Sharpe=+0.7530)
- Admission: Train IC=+0.2210, Deflated=+0.2224, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.065 | 2017: +0.237 | 2018: +0.210 | 2019: +0.116 | 2020: +0.134 | 2021: +0.111 | 2022: +0.105 | 2023: +0.093 | 2024: +0.160 | 2025: +0.108 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.368 | 2016: +0.215 | 2017: +0.319 | 2018: +0.291 | 2019: +0.175 | 2020: +0.132 | 2021: +0.320 | 2022: +0.130 | 2023: +0.257 | 2024: +0.297 | 2025: -0.034 | 2026: -0.171
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.66
- Early IC=+0.1625, Recent IC=+0.1076, 1st-half IC=+0.2104, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.026, Q3_mid=+0.190, Q4=+0.162, Q5_high_vol=+0.212

**`combo_min__net_volume_flow__bar_ret_0`** (Lock IC=+0.0962, Sharpe=+0.7432)
- Admission: Train IC=+0.2395, Deflated=+0.2414, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.069 | 2017: +0.182 | 2018: +0.174 | 2019: +0.118 | 2020: +0.097 | 2021: +0.085 | 2022: +0.089 | 2023: +0.081 | 2024: +0.137 | 2025: +0.125 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.308 | 2016: +0.004 | 2017: +0.260 | 2018: +0.369 | 2019: +0.137 | 2020: +0.144 | 2021: +0.282 | 2022: +0.223 | 2023: +0.326 | 2024: +0.367 | 2025: +0.129 | 2026: -0.019
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.66
- Early IC=+0.1323, Recent IC=+0.0872, 1st-half IC=+0.1618, 2nd-half IC=+0.1005, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.044, Q3_mid=+0.161, Q4=+0.140, Q5_high_vol=+0.158

**`combo_mean__net_volume_flow__bar_body_rng_0`** (Lock IC=+0.0894, Sharpe=+0.7399)
- Admission: Train IC=+0.2585, Deflated=+0.2606, IR=0.73, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.096 | 2017: +0.190 | 2018: +0.195 | 2019: +0.118 | 2020: +0.104 | 2021: +0.109 | 2022: +0.091 | 2023: +0.085 | 2024: +0.129 | 2025: +0.121 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.055 | 2017: +0.161 | 2018: +0.306 | 2019: +0.158 | 2020: +0.163 | 2021: +0.242 | 2022: +0.316 | 2023: +0.288 | 2024: +0.316 | 2025: +0.105 | 2026: -0.228
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.65
- Early IC=+0.1537, Recent IC=+0.0996, 1st-half IC=+0.1813, 2nd-half IC=+0.1085, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.025, Q3_mid=+0.167, Q4=+0.157, Q5_high_vol=+0.193

**`combo_rank_max__max_up_ret__max_down_ret`** (Lock IC=+0.0865, Sharpe=+0.7342)
- Admission: Train IC=+0.2287, Deflated=+0.2312, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.079 | 2017: +0.232 | 2018: +0.240 | 2019: +0.123 | 2020: +0.132 | 2021: +0.128 | 2022: +0.077 | 2023: +0.052 | 2024: +0.142 | 2025: +0.111 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.520 | 2016: -0.023 | 2017: +0.192 | 2018: +0.193 | 2019: +0.374 | 2020: +0.193 | 2021: +0.307 | 2022: +0.142 | 2023: +0.092 | 2024: +0.311 | 2025: +0.202 | 2026: -0.142
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.54, Recency ratio=0.59
- Early IC=+0.1751, Recent IC=+0.1030, 1st-half IC=+0.2221, 2nd-half IC=+0.1199, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.193, Q2=-0.001, Q3_mid=+0.186, Q4=+0.178, Q5_high_vol=+0.243

**`combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0905, Sharpe=+0.7330)
- Admission: Train IC=+0.2275, Deflated=+0.2284, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.119 | 2017: +0.121 | 2018: +0.159 | 2019: +0.097 | 2020: +0.097 | 2021: +0.025 | 2022: +0.154 | 2023: +0.090 | 2024: +0.103 | 2025: +0.093 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.377 | 2017: +0.216 | 2018: +0.137 | 2019: +0.181 | 2020: +0.126 | 2021: +0.107 | 2022: +0.164 | 2023: +0.128 | 2024: +0.236 | 2025: -0.002 | 2026: -0.189
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.51
- Early IC=+0.1777, Recent IC=+0.0902, 1st-half IC=+0.1923, 2nd-half IC=+0.0948, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.141, Q2=-0.000, Q3_mid=+0.172, Q4=+0.126, Q5_high_vol=+0.232

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0908, Sharpe=+0.7297)
- Admission: Train IC=+0.2814, Deflated=+0.2830, IR=0.99, Mono=0.84, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.051 | 2017: +0.158 | 2018: +0.229 | 2019: +0.171 | 2020: +0.164 | 2021: +0.163 | 2022: +0.057 | 2023: +0.089 | 2024: +0.128 | 2025: +0.096 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.026 | 2017: +0.193 | 2018: +0.389 | 2019: +0.255 | 2020: +0.227 | 2021: +0.336 | 2022: +0.237 | 2023: +0.313 | 2024: +0.301 | 2025: +0.108 | 2026: -0.368
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.81
- Early IC=+0.1358, Recent IC=+0.1098, 1st-half IC=+0.1820, 2nd-half IC=+0.1413, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.027, Q3_mid=+0.196, Q4=+0.141, Q5_high_vol=+0.225

**`combo_min__opening_drive_thrust_ratio__rsi_opening`** (Lock IC=+0.0993, Sharpe=+0.7283)
- Admission: Train IC=+0.2659, Deflated=+0.2677, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.052 | 2017: +0.205 | 2018: +0.190 | 2019: +0.099 | 2020: +0.143 | 2021: +0.113 | 2022: +0.068 | 2023: +0.108 | 2024: +0.147 | 2025: +0.118 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.412 | 2016: +0.193 | 2017: +0.254 | 2018: +0.237 | 2019: +0.288 | 2020: +0.154 | 2021: +0.301 | 2022: +0.269 | 2023: +0.117 | 2024: +0.321 | 2025: +0.112 | 2026: +0.097
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.81
- Early IC=+0.1122, Recent IC=+0.0907, 1st-half IC=+0.1626, 2nd-half IC=+0.1123, Neg regimes=0/5
- Weak component: `rsi_opening` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.025, Q3_mid=+0.165, Q4=+0.133, Q5_high_vol=+0.157

**`combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`** (Lock IC=+0.0864, Sharpe=+0.7260)
- Admission: Train IC=+0.2244, Deflated=+0.2257, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.074 | 2017: +0.196 | 2018: +0.120 | 2019: +0.102 | 2020: +0.137 | 2021: +0.090 | 2022: +0.088 | 2023: +0.110 | 2024: +0.133 | 2025: +0.097 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.460 | 2016: +0.288 | 2017: +0.215 | 2018: +0.224 | 2019: +0.238 | 2020: -0.037 | 2021: +0.186 | 2022: +0.251 | 2023: +0.223 | 2024: +0.316 | 2025: -0.141 | 2026: +0.121
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.67, Recency ratio=0.61
- Early IC=+0.1444, Recent IC=+0.0888, 1st-half IC=+0.1675, 2nd-half IC=+0.1123, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.036, Q3_mid=+0.180, Q4=+0.122, Q5_high_vol=+0.173

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1039, Sharpe=+0.7125)
- Admission: Train IC=+0.2407, Deflated=+0.2423, IR=0.71, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.117 | 2017: +0.245 | 2018: +0.233 | 2019: +0.156 | 2020: +0.179 | 2021: +0.115 | 2022: +0.080 | 2023: +0.089 | 2024: +0.136 | 2025: +0.111 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.383 | 2016: +0.152 | 2017: +0.280 | 2018: +0.407 | 2019: +0.273 | 2020: +0.203 | 2021: +0.168 | 2022: +0.016 | 2023: +0.130 | 2024: +0.231 | 2025: +0.075 | 2026: -0.136
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.50
- Early IC=+0.1934, Recent IC=+0.0975, 1st-half IC=+0.2331, 2nd-half IC=+0.1370, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.043, Q3_mid=+0.181, Q4=+0.166, Q5_high_vol=+0.246

**`combo_mean__net_volume_flow__shaved_bar_trend_conviction`** (Lock IC=+0.0770, Sharpe=+0.7110)
- Admission: Train IC=+0.2152, Deflated=+0.2165, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.042 | 2017: +0.158 | 2018: +0.122 | 2019: +0.036 | 2020: +0.109 | 2021: +0.039 | 2022: +0.045 | 2023: +0.092 | 2024: +0.094 | 2025: +0.128 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.194 | 2016: +0.130 | 2017: +0.239 | 2018: +0.227 | 2019: +0.116 | 2020: +0.162 | 2021: +0.185 | 2022: +0.207 | 2023: +0.127 | 2024: +0.245 | 2025: +0.149 | 2026: -0.239
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.48
- Early IC=+0.0876, Recent IC=+0.0421, 1st-half IC=+0.1280, 2nd-half IC=+0.0685, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.146, Q2=-0.030, Q3_mid=+0.138, Q4=+0.125, Q5_high_vol=+0.087

**`combo_rel_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0872, Sharpe=+0.7049)
- Admission: Train IC=+0.1636, Deflated=+0.1651, IR=0.63, Mono=0.74, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.016 | 2017: +0.201 | 2018: +0.193 | 2019: +0.177 | 2020: +0.168 | 2021: +0.122 | 2022: +0.054 | 2023: +0.098 | 2024: +0.107 | 2025: +0.042 | 2026: +0.094
- Yearly Tail ICs:   2015: +0.375 | 2016: -0.009 | 2017: +0.381 | 2018: +0.143 | 2019: +0.261 | 2020: +0.052 | 2021: +0.204 | 2022: +0.060 | 2023: +0.157 | 2024: +0.256 | 2025: +0.047 | 2026: +0.384
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.59
- Early IC=+0.1484, Recent IC=+0.0878, 1st-half IC=+0.1749, 2nd-half IC=+0.1349, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.021, Q3_mid=+0.174, Q4=+0.149, Q5_high_vol=+0.257

**`combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`** (Lock IC=+0.0960, Sharpe=+0.7037)
- Admission: Train IC=+0.2323, Deflated=+0.2339, IR=0.86, Mono=0.84, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.056 | 2017: +0.163 | 2018: +0.240 | 2019: +0.161 | 2020: +0.162 | 2021: +0.158 | 2022: +0.067 | 2023: +0.091 | 2024: +0.138 | 2025: +0.106 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.367 | 2016: -0.040 | 2017: +0.114 | 2018: +0.354 | 2019: +0.322 | 2020: +0.162 | 2021: +0.286 | 2022: +0.162 | 2023: +0.309 | 2024: +0.224 | 2025: +0.269 | 2026: -0.359
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.76, Recency ratio=0.78
- Early IC=+0.1429, Recent IC=+0.1121, 1st-half IC=+0.1842, 2nd-half IC=+0.1404, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.038, Q3_mid=+0.183, Q4=+0.140, Q5_high_vol=+0.231

**`combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`** (Lock IC=+0.0781, Sharpe=+0.7031)
- Admission: Train IC=+0.1909, Deflated=+0.1923, IR=0.43, Mono=0.67, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.141 | 2016: +0.084 | 2017: +0.164 | 2018: +0.085 | 2019: +0.060 | 2020: +0.085 | 2021: +0.049 | 2022: +0.089 | 2023: +0.103 | 2024: +0.115 | 2025: +0.125 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.348 | 2016: +0.147 | 2017: +0.116 | 2018: +0.157 | 2019: +0.229 | 2020: +0.061 | 2021: +0.184 | 2022: +0.167 | 2023: +0.259 | 2024: +0.326 | 2025: -0.050 | 2026: +0.176
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.61
- Early IC=+0.1128, Recent IC=+0.0689, 1st-half IC=+0.1278, 2nd-half IC=+0.0780, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.008, Q3_mid=+0.149, Q4=+0.108, Q5_high_vol=+0.088

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1108, Sharpe=+0.6987)
- Admission: Train IC=+0.2950, Deflated=+0.2963, IR=0.95, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.137 | 2017: +0.242 | 2018: +0.242 | 2019: +0.136 | 2020: +0.199 | 2021: +0.137 | 2022: +0.091 | 2023: +0.085 | 2024: +0.130 | 2025: +0.109 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.291 | 2016: +0.229 | 2017: +0.320 | 2018: +0.383 | 2019: +0.293 | 2020: +0.181 | 2021: +0.246 | 2022: +0.140 | 2023: -0.035 | 2024: +0.149 | 2025: -0.103 | 2026: +0.060
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.53
- Early IC=+0.2149, Recent IC=+0.1138, 1st-half IC=+0.2569, 2nd-half IC=+0.1451, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.052, Q3_mid=+0.202, Q4=+0.210, Q5_high_vol=+0.274

**`combo_rank_min__close_vs_open_range__shaved_bar_trend_conviction`** (Lock IC=+0.0723, Sharpe=+0.6918)
- Admission: Train IC=+0.1968, Deflated=+0.1980, IR=0.46, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.142 | 2016: +0.065 | 2017: +0.161 | 2018: +0.090 | 2019: -0.001 | 2020: +0.110 | 2021: +0.021 | 2022: +0.040 | 2023: +0.099 | 2024: +0.083 | 2025: +0.131 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.165 | 2016: +0.186 | 2017: +0.328 | 2018: +0.136 | 2019: +0.014 | 2020: +0.193 | 2021: +0.132 | 2022: +0.095 | 2023: -0.021 | 2024: +0.258 | 2025: +0.148 | 2026: -0.075
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.29
- Early IC=+0.1043, Recent IC=+0.0305, 1st-half IC=+0.1260, 2nd-half IC=+0.0512, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.136, Q2=-0.017, Q3_mid=+0.124, Q4=+0.103, Q5_high_vol=+0.076

**`combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`** (Lock IC=+0.0749, Sharpe=+0.6891)
- Admission: Train IC=+0.1905, Deflated=+0.1919, IR=0.44, Mono=0.69, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.080 | 2017: +0.162 | 2018: +0.089 | 2019: +0.061 | 2020: +0.092 | 2021: +0.053 | 2022: +0.094 | 2023: +0.099 | 2024: +0.107 | 2025: +0.126 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.343 | 2016: +0.151 | 2017: +0.126 | 2018: +0.157 | 2019: +0.231 | 2020: +0.056 | 2021: +0.181 | 2022: +0.159 | 2023: +0.260 | 2024: +0.321 | 2025: -0.054 | 2026: +0.192
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.65
- Early IC=+0.1129, Recent IC=+0.0732, 1st-half IC=+0.1278, 2nd-half IC=+0.0823, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.010, Q3_mid=+0.154, Q4=+0.107, Q5_high_vol=+0.096

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0993, Sharpe=+0.6878)
- Admission: Train IC=+0.2850, Deflated=+0.2868, IR=0.98, Mono=0.84, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.056 | 2017: +0.164 | 2018: +0.246 | 2019: +0.172 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.144 | 2025: +0.097 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.444 | 2016: +0.054 | 2017: +0.194 | 2018: +0.413 | 2019: +0.231 | 2020: +0.221 | 2021: +0.334 | 2022: +0.237 | 2023: +0.318 | 2024: +0.299 | 2025: +0.102 | 2026: -0.350
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.74
- Early IC=+0.1452, Recent IC=+0.1070, 1st-half IC=+0.1912, 2nd-half IC=+0.1398, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.034, Q3_mid=+0.206, Q4=+0.143, Q5_high_vol=+0.240

**`combo_diff__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0814, Sharpe=+0.6836)
- Admission: Train IC=+0.1625, Deflated=+0.1638, IR=0.52, Mono=0.67, p=0.0006, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.097 | 2017: +0.153 | 2018: +0.079 | 2019: +0.077 | 2020: +0.085 | 2021: +0.045 | 2022: +0.078 | 2023: +0.094 | 2024: +0.130 | 2025: +0.093 | 2026: -0.043
- Yearly Tail ICs:   2015: +0.407 | 2016: +0.162 | 2017: +0.098 | 2018: +0.077 | 2019: +0.163 | 2020: -0.022 | 2021: +0.180 | 2022: +0.227 | 2023: +0.352 | 2024: +0.374 | 2025: -0.005 | 2026: +0.054
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=0.39
- Early IC=+0.1581, Recent IC=+0.0613, 1st-half IC=+0.1412, 2nd-half IC=+0.0789, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.155, Q2=-0.003, Q3_mid=+0.153, Q4=+0.098, Q5_high_vol=+0.134

**`combo_tri_max__max_up_ret__early_body_momentum__trend_day_regime_conviction`** (Lock IC=+0.0781, Sharpe=+0.6799)
- Admission: Train IC=+0.2341, Deflated=+0.2359, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.108 | 2017: +0.179 | 2018: +0.189 | 2019: +0.070 | 2020: +0.130 | 2021: +0.064 | 2022: +0.109 | 2023: +0.083 | 2024: +0.136 | 2025: +0.076 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.217 | 2017: +0.278 | 2018: +0.275 | 2019: +0.133 | 2020: +0.251 | 2021: +0.103 | 2022: +0.137 | 2023: +0.119 | 2024: +0.289 | 2025: -0.162 | 2026: -0.339
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.53
- Early IC=+0.1627, Recent IC=+0.0861, 1st-half IC=+0.1933, 2nd-half IC=+0.0981, Neg regimes=1/5
- Weak component: `trend_day_regime_conviction` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.014, Q3_mid=+0.165, Q4=+0.148, Q5_high_vol=+0.218

**`combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0815, Sharpe=+0.6738)
- Admission: Train IC=+0.2587, Deflated=+0.2601, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.091 | 2017: +0.165 | 2018: +0.117 | 2019: +0.085 | 2020: +0.121 | 2021: +0.061 | 2022: +0.110 | 2023: +0.116 | 2024: +0.128 | 2025: +0.101 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.369 | 2016: +0.225 | 2017: +0.111 | 2018: +0.259 | 2019: +0.286 | 2020: +0.066 | 2021: +0.320 | 2022: +0.189 | 2023: +0.298 | 2024: +0.192 | 2025: +0.066 | 2026: -0.157
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.60
- Early IC=+0.1419, Recent IC=+0.0856, 1st-half IC=+0.1655, 2nd-half IC=+0.0996, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.023, Q3_mid=+0.172, Q4=+0.123, Q5_high_vol=+0.163

**`combo_sig_product__max_up_ret__body_size_progression`** (Lock IC=+0.1031, Sharpe=+0.6726)
- Admission: Train IC=+0.1907, Deflated=+0.1915, IR=0.78, Mono=0.74, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.174 | 2017: +0.083 | 2018: +0.155 | 2019: +0.100 | 2020: +0.124 | 2021: +0.104 | 2022: +0.069 | 2023: +0.064 | 2024: +0.137 | 2025: +0.115 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.335 | 2016: +0.290 | 2017: +0.062 | 2018: +0.157 | 2019: +0.036 | 2020: +0.244 | 2021: +0.201 | 2022: +0.051 | 2023: +0.093 | 2024: +0.101 | 2025: +0.202 | 2026: +0.245
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.41
- Early IC=+0.2108, Recent IC=+0.0866, 1st-half IC=+0.1859, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.028, Q3_mid=+0.123, Q4=+0.143, Q5_high_vol=+0.216

**`combo_tri_mean__max_up_ret__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1040, Sharpe=+0.6683)
- Admission: Train IC=+0.2819, Deflated=+0.2832, IR=0.88, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.117 | 2017: +0.200 | 2018: +0.209 | 2019: +0.120 | 2020: +0.166 | 2021: +0.110 | 2022: +0.108 | 2023: +0.076 | 2024: +0.118 | 2025: +0.120 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.331 | 2016: +0.190 | 2017: +0.220 | 2018: +0.340 | 2019: +0.255 | 2020: +0.218 | 2021: +0.215 | 2022: +0.235 | 2023: +0.200 | 2024: +0.218 | 2025: -0.076 | 2026: -0.018
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.56
- Early IC=+0.1931, Recent IC=+0.1090, 1st-half IC=+0.2232, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.011, Q3_mid=+0.196, Q4=+0.187, Q5_high_vol=+0.230

**`combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0961, Sharpe=+0.6661)
- Admission: Train IC=+0.2528, Deflated=+0.2544, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.122 | 2017: +0.228 | 2018: +0.221 | 2019: +0.145 | 2020: +0.139 | 2021: +0.072 | 2022: +0.119 | 2023: +0.083 | 2024: +0.119 | 2025: +0.147 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.151 | 2017: +0.220 | 2018: +0.293 | 2019: +0.295 | 2020: +0.308 | 2021: +0.097 | 2022: +0.219 | 2023: +0.232 | 2024: +0.327 | 2025: -0.039 | 2026: -0.270
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.51
- Early IC=+0.1879, Recent IC=+0.0954, 1st-half IC=+0.2215, 2nd-half IC=+0.1219, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.021, Q3_mid=+0.173, Q4=+0.172, Q5_high_vol=+0.226

**`combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0851, Sharpe=+0.6624)
- Admission: Train IC=+0.1753, Deflated=+0.1762, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.236 | 2016: -0.019 | 2017: +0.159 | 2018: +0.214 | 2019: +0.134 | 2020: +0.173 | 2021: +0.140 | 2022: +0.042 | 2023: +0.085 | 2024: +0.118 | 2025: +0.070 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.054 | 2017: +0.217 | 2018: +0.364 | 2019: +0.215 | 2020: +0.102 | 2021: +0.297 | 2022: +0.004 | 2023: +0.278 | 2024: +0.270 | 2025: -0.022 | 2026: +0.345
- IC CV=0.59, Neg years (linear/tail)=1/0 of 8, Half ratio=0.82, Recency ratio=0.84
- Early IC=+0.1084, Recent IC=+0.0909, 1st-half IC=+0.1505, 2nd-half IC=+0.1229, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.045, Q3_mid=+0.150, Q4=+0.128, Q5_high_vol=+0.229

**`combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early`** (Lock IC=+0.0820, Sharpe=+0.6587)
- Admission: Train IC=+0.2093, Deflated=+0.2107, IR=0.54, Mono=0.66, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.082 | 2017: +0.195 | 2018: +0.063 | 2019: +0.058 | 2020: +0.085 | 2021: +0.008 | 2022: +0.081 | 2023: +0.032 | 2024: +0.082 | 2025: +0.105 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.031 | 2017: +0.298 | 2018: +0.215 | 2019: +0.115 | 2020: +0.174 | 2021: +0.047 | 2022: +0.198 | 2023: +0.023 | 2024: +0.170 | 2025: +0.100 | 2026: +0.187
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.39, Recency ratio=0.31
- Early IC=+0.1435, Recent IC=+0.0443, 1st-half IC=+0.1515, 2nd-half IC=+0.0584, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.166, Q2=-0.016, Q3_mid=+0.091, Q4=+0.145, Q5_high_vol=+0.113

**`combo_mean__close_vs_open_range__bar_body_rng_0`** (Lock IC=+0.0958, Sharpe=+0.6571)
- Admission: Train IC=+0.2326, Deflated=+0.2348, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.106 | 2017: +0.219 | 2018: +0.186 | 2019: +0.112 | 2020: +0.107 | 2021: +0.115 | 2022: +0.074 | 2023: +0.084 | 2024: +0.144 | 2025: +0.132 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.433 | 2016: +0.107 | 2017: +0.228 | 2018: +0.268 | 2019: +0.209 | 2020: +0.143 | 2021: +0.264 | 2022: +0.324 | 2023: +0.201 | 2024: +0.338 | 2025: +0.125 | 2026: -0.075
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.54
- Early IC=+0.1743, Recent IC=+0.0944, 1st-half IC=+0.1889, 2nd-half IC=+0.1048, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.029, Q3_mid=+0.160, Q4=+0.157, Q5_high_vol=+0.203

**`combo_rank_min__first_bar_return__close_vs_open_range`** (Lock IC=+0.0969, Sharpe=+0.6560)
- Admission: Train IC=+0.2241, Deflated=+0.2260, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.080 | 2017: +0.185 | 2018: +0.173 | 2019: +0.118 | 2020: +0.063 | 2021: +0.055 | 2022: +0.043 | 2023: +0.067 | 2024: +0.123 | 2025: +0.138 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.448 | 2016: +0.133 | 2017: +0.248 | 2018: +0.283 | 2019: +0.223 | 2020: +0.076 | 2021: +0.272 | 2022: +0.156 | 2023: +0.140 | 2024: +0.200 | 2025: +0.186 | 2026: +0.283
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.44, Recency ratio=0.35
- Early IC=+0.1449, Recent IC=+0.0501, 1st-half IC=+0.1666, 2nd-half IC=+0.0732, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.056, Q3_mid=+0.140, Q4=+0.141, Q5_high_vol=+0.153

**`combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`** (Lock IC=+0.0897, Sharpe=+0.6542)
- Admission: Train IC=+0.2241, Deflated=+0.2256, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.090 | 2017: +0.199 | 2018: +0.127 | 2019: +0.104 | 2020: +0.133 | 2021: +0.095 | 2022: +0.078 | 2023: +0.115 | 2024: +0.144 | 2025: +0.095 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.462 | 2016: +0.290 | 2017: +0.207 | 2018: +0.215 | 2019: +0.233 | 2020: -0.025 | 2021: +0.183 | 2022: +0.240 | 2023: +0.214 | 2024: +0.317 | 2025: -0.123 | 2026: +0.128
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.56
- Early IC=+0.1535, Recent IC=+0.0861, 1st-half IC=+0.1748, 2nd-half IC=+0.1102, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.032, Q3_mid=+0.181, Q4=+0.131, Q5_high_vol=+0.171

**`combo_min__max_up_ret__rsi_opening`** (Lock IC=+0.0971, Sharpe=+0.6507)
- Admission: Train IC=+0.2334, Deflated=+0.2342, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.072 | 2017: +0.195 | 2018: +0.154 | 2019: +0.087 | 2020: +0.111 | 2021: +0.107 | 2022: +0.114 | 2023: +0.113 | 2024: +0.150 | 2025: +0.141 | 2026: -0.090
- Yearly Tail ICs:   2015: +0.256 | 2016: +0.178 | 2017: +0.339 | 2018: +0.372 | 2019: +0.122 | 2020: +0.197 | 2021: +0.133 | 2022: +0.149 | 2023: +0.207 | 2024: +0.213 | 2025: +0.097 | 2026: -0.097
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.95
- Early IC=+0.1158, Recent IC=+0.1102, 1st-half IC=+0.1560, 2nd-half IC=+0.1050, Neg regimes=0/5
- Weak component: `rsi_opening` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.029, Q3_mid=+0.167, Q4=+0.152, Q5_high_vol=+0.123

**`combo_diff__close_vs_open_range__h2_l2_pullback_continuation`** (Lock IC=+0.0746, Sharpe=+0.6466)
- Admission: Train IC=+0.1765, Deflated=+0.1777, IR=0.39, Mono=0.65, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.147 | 2016: +0.090 | 2017: +0.155 | 2018: +0.063 | 2019: +0.049 | 2020: +0.081 | 2021: +0.038 | 2022: +0.089 | 2023: +0.099 | 2024: +0.111 | 2025: +0.118 | 2026: -0.090
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.194 | 2017: +0.237 | 2018: +0.171 | 2019: +0.199 | 2020: +0.039 | 2021: +0.181 | 2022: +0.115 | 2023: +0.205 | 2024: +0.332 | 2025: -0.055 | 2026: +0.144
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.54
- Early IC=+0.1184, Recent IC=+0.0636, 1st-half IC=+0.1221, 2nd-half IC=+0.0727, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.005, Q3_mid=+0.148, Q4=+0.096, Q5_high_vol=+0.082

**`combo_mean__bar_ret_0__max_down_ret`** (Lock IC=+0.0916, Sharpe=+0.6450)
- Admission: Train IC=+0.2220, Deflated=+0.2243, IR=0.55, Mono=0.65, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.107 | 2017: +0.225 | 2018: +0.209 | 2019: +0.136 | 2020: +0.112 | 2021: +0.088 | 2022: +0.072 | 2023: +0.055 | 2024: +0.124 | 2025: +0.132 | 2026: +0.011
- Yearly Tail ICs:   2015: +0.319 | 2016: +0.027 | 2017: +0.271 | 2018: +0.421 | 2019: +0.159 | 2020: +0.200 | 2021: +0.264 | 2022: +0.184 | 2023: +0.147 | 2024: +0.248 | 2025: +0.137 | 2026: -0.216
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.48
- Early IC=+0.1671, Recent IC=+0.0799, 1st-half IC=+0.1897, 2nd-half IC=+0.1065, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.010, Q3_mid=+0.153, Q4=+0.138, Q5_high_vol=+0.195

**`combo_rank_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.1013, Sharpe=+0.6416)
- Admission: Train IC=+0.2568, Deflated=+0.2574, IR=0.63, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.084 | 2017: +0.178 | 2018: +0.119 | 2019: +0.074 | 2020: +0.106 | 2021: +0.122 | 2022: +0.077 | 2023: +0.091 | 2024: +0.149 | 2025: +0.154 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.222 | 2017: +0.179 | 2018: +0.282 | 2019: +0.330 | 2020: +0.148 | 2021: +0.286 | 2022: +0.022 | 2023: +0.103 | 2024: +0.332 | 2025: +0.115 | 2026: -0.098
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.69
- Early IC=+0.1411, Recent IC=+0.0977, 1st-half IC=+0.1566, 2nd-half IC=+0.0939, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.025, Q3_mid=+0.155, Q4=+0.136, Q5_high_vol=+0.127

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1205, Sharpe=+0.6397)
- Admission: Train IC=+0.3202, Deflated=+0.3220, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.058 | 2017: +0.232 | 2018: +0.167 | 2019: +0.152 | 2020: +0.151 | 2021: +0.140 | 2022: +0.018 | 2023: +0.098 | 2024: +0.181 | 2025: +0.082 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.159 | 2017: +0.319 | 2018: +0.432 | 2019: +0.349 | 2020: +0.251 | 2021: +0.080 | 2022: +0.192 | 2023: +0.002 | 2024: +0.262 | 2025: -0.144 | 2026: +0.213
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.48
- Early IC=+0.1640, Recent IC=+0.0789, 1st-half IC=+0.1957, 2nd-half IC=+0.1242, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.047, Q3_mid=+0.155, Q4=+0.188, Q5_high_vol=+0.199

**`combo_min__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0782, Sharpe=+0.6383)
- Admission: Train IC=+0.2229, Deflated=+0.2243, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.151 | 2016: -0.001 | 2017: +0.134 | 2018: +0.155 | 2019: +0.155 | 2020: +0.065 | 2021: +0.164 | 2022: +0.131 | 2023: +0.083 | 2024: +0.122 | 2025: +0.100 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.217 | 2016: -0.002 | 2017: +0.328 | 2018: +0.444 | 2019: +0.200 | 2020: +0.021 | 2021: +0.233 | 2022: +0.267 | 2023: +0.161 | 2024: +0.421 | 2025: +0.267 | 2026: -0.147
- IC CV=0.45, Neg years (linear/tail)=1/1 of 8, Half ratio=1.08, Recency ratio=1.97
- Early IC=+0.0748, Recent IC=+0.1473, 1st-half IC=+0.1194, 2nd-half IC=+0.1289, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.160, Q2=-0.017, Q3_mid=+0.142, Q4=+0.163, Q5_high_vol=+0.123

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1177, Sharpe=+0.6330)
- Admission: Train IC=+0.3148, Deflated=+0.3165, IR=1.11, Mono=0.84, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.101 | 2017: +0.231 | 2018: +0.185 | 2019: +0.157 | 2020: +0.172 | 2021: +0.142 | 2022: +0.033 | 2023: +0.098 | 2024: +0.145 | 2025: +0.105 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.251 | 2017: +0.357 | 2018: +0.456 | 2019: +0.298 | 2020: +0.315 | 2021: +0.302 | 2022: +0.078 | 2023: -0.003 | 2024: +0.236 | 2025: +0.074 | 2026: +0.233
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.46
- Early IC=+0.1926, Recent IC=+0.0877, 1st-half IC=+0.2183, 2nd-half IC=+0.1340, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.060, Q3_mid=+0.153, Q4=+0.229, Q5_high_vol=+0.208

**`combo_sig_product__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.1062, Sharpe=+0.6289)
- Admission: Train IC=+0.1905, Deflated=+0.1919, IR=0.48, Mono=0.69, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.215 | 2017: +0.102 | 2018: +0.143 | 2019: +0.102 | 2020: +0.105 | 2021: +0.123 | 2022: +0.130 | 2023: +0.093 | 2024: +0.131 | 2025: +0.114 | 2026: +0.048
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.335 | 2017: +0.022 | 2018: +0.071 | 2019: +0.178 | 2020: -0.071 | 2021: +0.186 | 2022: +0.140 | 2023: +0.243 | 2024: +0.405 | 2025: -0.099 | 2026: +0.239
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.55, Recency ratio=0.51
- Early IC=+0.2486, Recent IC=+0.1264, 1st-half IC=+0.2073, 2nd-half IC=+0.1149, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.048, Q3_mid=+0.145, Q4=+0.145, Q5_high_vol=+0.257

**`combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0840, Sharpe=+0.6202)
- Admission: Train IC=+0.2150, Deflated=+0.2161, IR=0.48, Mono=0.67, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.105 | 2017: +0.115 | 2018: +0.161 | 2019: +0.080 | 2020: +0.101 | 2021: +0.021 | 2022: +0.126 | 2023: +0.075 | 2024: +0.099 | 2025: +0.090 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.049 | 2016: +0.378 | 2017: +0.151 | 2018: +0.215 | 2019: +0.151 | 2020: +0.112 | 2021: +0.136 | 2022: +0.098 | 2023: +0.158 | 2024: +0.211 | 2025: -0.035 | 2026: -0.150
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.48, Recency ratio=0.46
- Early IC=+0.1593, Recent IC=+0.0735, 1st-half IC=+0.1790, 2nd-half IC=+0.0860, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.140, Q2=-0.017, Q3_mid=+0.165, Q4=+0.116, Q5_high_vol=+0.211

**`combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1053, Sharpe=+0.6127)
- Admission: Train IC=+0.2906, Deflated=+0.2921, IR=0.94, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.278 | 2016: +0.083 | 2017: +0.229 | 2018: +0.199 | 2019: +0.143 | 2020: +0.175 | 2021: +0.115 | 2022: +0.083 | 2023: +0.082 | 2024: +0.136 | 2025: +0.103 | 2026: +0.064
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.154 | 2017: +0.285 | 2018: +0.340 | 2019: +0.327 | 2020: +0.127 | 2021: +0.237 | 2022: +0.333 | 2023: +0.193 | 2024: +0.212 | 2025: +0.008 | 2026: +0.049
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.55
- Early IC=+0.1804, Recent IC=+0.0988, 1st-half IC=+0.2124, 2nd-half IC=+0.1335, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.015, Q3_mid=+0.195, Q4=+0.187, Q5_high_vol=+0.219

**`combo_sig_product__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0726, Sharpe=+0.6092)
- Admission: Train IC=+0.1293, Deflated=+0.1302, IR=0.35, Mono=0.65, p=0.0120, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.110 | 2017: +0.118 | 2018: +0.099 | 2019: +0.064 | 2020: +0.076 | 2021: +0.062 | 2022: +0.110 | 2023: +0.131 | 2024: +0.125 | 2025: +0.082 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.084 | 2017: +0.167 | 2018: +0.129 | 2019: -0.021 | 2020: -0.026 | 2021: +0.095 | 2022: +0.198 | 2023: +0.232 | 2024: +0.421 | 2025: -0.080 | 2026: +0.044
- IC CV=0.37, Neg years (linear/tail)=0/2 of 8, Half ratio=0.70, Recency ratio=0.57
- Early IC=+0.1501, Recent IC=+0.0862, 1st-half IC=+0.1194, 2nd-half IC=+0.0836, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.008, Q3_mid=+0.113, Q4=+0.057, Q5_high_vol=+0.172

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1015, Sharpe=+0.6089)
- Admission: Train IC=+0.2794, Deflated=+0.2812, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.158 | 2017: +0.193 | 2018: +0.198 | 2019: +0.148 | 2020: +0.154 | 2021: +0.114 | 2022: +0.072 | 2023: +0.058 | 2024: +0.091 | 2025: +0.113 | 2026: +0.140
- Yearly Tail ICs:   2015: +0.188 | 2016: +0.251 | 2017: +0.273 | 2018: +0.352 | 2019: +0.352 | 2020: +0.163 | 2021: +0.275 | 2022: +0.092 | 2023: -0.064 | 2024: +0.101 | 2025: +0.071 | 2026: +0.284
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.42
- Early IC=+0.2212, Recent IC=+0.0932, 1st-half IC=+0.2309, 2nd-half IC=+0.1209, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.016, Q3_mid=+0.140, Q4=+0.217, Q5_high_vol=+0.246

**`combo_rank_max__early_body_momentum__close_vs_open_range`** (Lock IC=+0.0820, Sharpe=+0.6056)
- Admission: Train IC=+0.2002, Deflated=+0.2012, IR=0.53, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.156 | 2016: +0.069 | 2017: +0.160 | 2018: +0.108 | 2019: +0.043 | 2020: +0.096 | 2021: +0.059 | 2022: +0.103 | 2023: +0.078 | 2024: +0.128 | 2025: +0.145 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.146 | 2017: +0.200 | 2018: +0.103 | 2019: +0.107 | 2020: +0.236 | 2021: +0.239 | 2022: +0.159 | 2023: +0.114 | 2024: +0.331 | 2025: +0.052 | 2026: -0.053
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.71
- Early IC=+0.1134, Recent IC=+0.0800, 1st-half IC=+0.1356, 2nd-half IC=+0.0796, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.016, Q3_mid=+0.163, Q4=+0.123, Q5_high_vol=+0.094

**`combo_mean__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.1004, Sharpe=+0.6046)
- Admission: Train IC=+0.2626, Deflated=+0.2641, IR=0.84, Mono=0.80, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.073 | 2017: +0.226 | 2018: +0.165 | 2019: +0.116 | 2020: +0.152 | 2021: +0.124 | 2022: +0.080 | 2023: +0.101 | 2024: +0.151 | 2025: +0.114 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.407 | 2016: +0.198 | 2017: +0.311 | 2018: +0.219 | 2019: +0.355 | 2020: +0.160 | 2021: +0.314 | 2022: +0.198 | 2023: +0.202 | 2024: +0.320 | 2025: -0.017 | 2026: -0.020
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.62
- Early IC=+0.1638, Recent IC=+0.1020, 1st-half IC=+0.1880, 2nd-half IC=+0.1242, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.030, Q3_mid=+0.185, Q4=+0.148, Q5_high_vol=+0.199

**`combo_rank_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0918, Sharpe=+0.6021)
- Admission: Train IC=+0.2423, Deflated=+0.2441, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.073 | 2017: +0.176 | 2018: +0.136 | 2019: +0.076 | 2020: +0.099 | 2021: +0.063 | 2022: +0.080 | 2023: +0.093 | 2024: +0.130 | 2025: +0.140 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.322 | 2016: +0.122 | 2017: +0.348 | 2018: +0.222 | 2019: +0.196 | 2020: +0.261 | 2021: +0.207 | 2022: +0.146 | 2023: +0.270 | 2024: +0.265 | 2025: -0.017 | 2026: -0.063
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.60
- Early IC=+0.1175, Recent IC=+0.0702, 1st-half IC=+0.1406, 2nd-half IC=+0.0822, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.156, Q2=-0.024, Q3_mid=+0.166, Q4=+0.126, Q5_high_vol=+0.121

**`combo_min__max_up_ret__bar_ret_0`** (Lock IC=+0.0798, Sharpe=+0.5993)
- Admission: Train IC=+0.2045, Deflated=+0.2055, IR=0.46, Mono=0.67, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.100 | 2017: +0.204 | 2018: +0.227 | 2019: +0.134 | 2020: +0.123 | 2021: +0.101 | 2022: +0.087 | 2023: +0.098 | 2024: +0.105 | 2025: +0.080 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.035 | 2017: +0.174 | 2018: +0.450 | 2019: +0.152 | 2020: +0.190 | 2021: +0.157 | 2022: +0.112 | 2023: +0.153 | 2024: +0.176 | 2025: +0.008 | 2026: -0.162
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.54
- Early IC=+0.1762, Recent IC=+0.0943, 1st-half IC=+0.2156, 2nd-half IC=+0.1133, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.028, Q3_mid=+0.166, Q4=+0.165, Q5_high_vol=+0.213

**`combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0837, Sharpe=+0.5987)
- Admission: Train IC=+0.2501, Deflated=+0.2506, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.053 | 2017: +0.173 | 2018: +0.096 | 2019: +0.052 | 2020: +0.116 | 2021: +0.016 | 2022: +0.006 | 2023: +0.068 | 2024: +0.055 | 2025: +0.110 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.150 | 2017: +0.253 | 2018: +0.315 | 2019: +0.238 | 2020: +0.269 | 2021: +0.052 | 2022: +0.167 | 2023: -0.132 | 2024: +0.156 | 2025: +0.192 | 2026: +0.196
- IC CV=0.75, Neg years (linear/tail)=0/0 of 8, Half ratio=0.34, Recency ratio=0.08
- Early IC=+0.1276, Recent IC=+0.0108, 1st-half IC=+0.1557, 2nd-half IC=+0.0533, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.132, Q2=-0.020, Q3_mid=+0.094, Q4=+0.160, Q5_high_vol=+0.114

**`combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0933, Sharpe=+0.5933)
- Admission: Train IC=+0.2296, Deflated=+0.2305, IR=0.71, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.036 | 2017: +0.251 | 2018: +0.055 | 2019: +0.130 | 2020: +0.084 | 2021: +0.086 | 2022: +0.033 | 2023: +0.078 | 2024: +0.109 | 2025: +0.088 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.184 | 2016: +0.122 | 2017: +0.354 | 2018: +0.360 | 2019: +0.281 | 2020: +0.109 | 2021: +0.253 | 2022: +0.127 | 2023: +0.118 | 2024: +0.131 | 2025: +0.028 | 2026: -0.142
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.49
- Early IC=+0.1198, Recent IC=+0.0587, 1st-half IC=+0.1350, 2nd-half IC=+0.0935, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.026, Q3_mid=+0.120, Q4=+0.182, Q5_high_vol=+0.102

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.1061, Sharpe=+0.5929)
- Admission: Train IC=+0.2652, Deflated=+0.2666, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.122 | 2017: +0.223 | 2018: +0.217 | 2019: +0.127 | 2020: +0.154 | 2021: +0.106 | 2022: +0.095 | 2023: +0.077 | 2024: +0.114 | 2025: +0.142 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.065 | 2017: +0.258 | 2018: +0.364 | 2019: +0.265 | 2020: +0.243 | 2021: +0.225 | 2022: +0.261 | 2023: +0.233 | 2024: +0.184 | 2025: +0.073 | 2026: +0.015
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.50
- Early IC=+0.2017, Recent IC=+0.1007, 1st-half IC=+0.2319, 2nd-half IC=+0.1228, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.011, Q3_mid=+0.165, Q4=+0.198, Q5_high_vol=+0.218

**`combo_rank_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0814, Sharpe=+0.5897)
- Admission: Train IC=+0.2496, Deflated=+0.2512, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.109 | 2017: +0.217 | 2018: +0.227 | 2019: +0.127 | 2020: +0.123 | 2021: +0.101 | 2022: +0.080 | 2023: +0.086 | 2024: +0.115 | 2025: +0.082 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.374 | 2016: +0.121 | 2017: +0.209 | 2018: +0.402 | 2019: +0.269 | 2020: +0.189 | 2021: +0.229 | 2022: +0.007 | 2023: +0.017 | 2024: +0.153 | 2025: +0.200 | 2026: -0.119
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.48, Recency ratio=0.46
- Early IC=+0.1889, Recent IC=+0.0867, 1st-half IC=+0.2224, 2nd-half IC=+0.1066, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.006, Q3_mid=+0.165, Q4=+0.181, Q5_high_vol=+0.219

**`combo_rank_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0954, Sharpe=+0.5791)
- Admission: Train IC=+0.2093, Deflated=+0.2107, IR=0.64, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.048 | 2017: +0.223 | 2018: +0.166 | 2019: +0.110 | 2020: +0.147 | 2021: +0.099 | 2022: +0.078 | 2023: +0.080 | 2024: +0.120 | 2025: +0.121 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.050 | 2017: +0.153 | 2018: +0.091 | 2019: +0.327 | 2020: +0.059 | 2021: +0.353 | 2022: +0.208 | 2023: +0.072 | 2024: +0.188 | 2025: +0.122 | 2026: -0.052
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.54
- Early IC=+0.1685, Recent IC=+0.0911, 1st-half IC=+0.1756, 2nd-half IC=+0.1158, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.022, Q3_mid=+0.187, Q4=+0.140, Q5_high_vol=+0.207

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0869, Sharpe=+0.5783)
- Admission: Train IC=+0.2208, Deflated=+0.2227, IR=0.52, Mono=0.71, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.064 | 2017: +0.222 | 2018: +0.185 | 2019: +0.112 | 2020: +0.179 | 2021: +0.059 | 2022: +0.120 | 2023: +0.147 | 2024: +0.100 | 2025: +0.095 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.326 | 2016: -0.050 | 2017: +0.284 | 2018: +0.219 | 2019: +0.292 | 2020: +0.226 | 2021: +0.188 | 2022: +0.238 | 2023: +0.331 | 2024: +0.228 | 2025: -0.037 | 2026: -0.099
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.75, Recency ratio=0.71
- Early IC=+0.1254, Recent IC=+0.0892, 1st-half IC=+0.1656, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.035, Q3_mid=+0.189, Q4=+0.155, Q5_high_vol=+0.159

**`combo_min__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0801, Sharpe=+0.5713)
- Admission: Train IC=+0.1756, Deflated=+0.1770, IR=0.42, Mono=0.65, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.032 | 2017: +0.220 | 2018: +0.148 | 2019: +0.152 | 2020: +0.071 | 2021: +0.053 | 2022: +0.039 | 2023: +0.055 | 2024: +0.099 | 2025: +0.117 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.093 | 2016: +0.075 | 2017: +0.229 | 2018: +0.282 | 2019: +0.281 | 2020: +0.047 | 2021: +0.187 | 2022: +0.238 | 2023: +0.069 | 2024: +0.103 | 2025: +0.328 | 2026: -0.051
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.42
- Early IC=+0.1090, Recent IC=+0.0462, 1st-half IC=+0.1491, 2nd-half IC=+0.0832, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.054, Q3_mid=+0.151, Q4=+0.127, Q5_high_vol=+0.131

**`combo_mean__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0992, Sharpe=+0.5697)
- Admission: Train IC=+0.2705, Deflated=+0.2722, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.093 | 2017: +0.218 | 2018: +0.187 | 2019: +0.127 | 2020: +0.166 | 2021: +0.086 | 2022: +0.064 | 2023: +0.067 | 2024: +0.088 | 2025: +0.130 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.083 | 2017: +0.265 | 2018: +0.371 | 2019: +0.296 | 2020: +0.201 | 2021: +0.175 | 2022: +0.224 | 2023: -0.021 | 2024: +0.177 | 2025: +0.172 | 2026: +0.110
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.39
- Early IC=+0.1914, Recent IC=+0.0747, 1st-half IC=+0.2161, 2nd-half IC=+0.1100, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.010, Q3_mid=+0.128, Q4=+0.186, Q5_high_vol=+0.217

**`combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0788, Sharpe=+0.5668)
- Admission: Train IC=+0.1769, Deflated=+0.1781, IR=0.46, Mono=0.65, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.095 | 2017: +0.155 | 2018: +0.081 | 2019: +0.076 | 2020: +0.090 | 2021: +0.047 | 2022: +0.073 | 2023: +0.092 | 2024: +0.121 | 2025: +0.095 | 2026: -0.048
- Yearly Tail ICs:   2015: +0.444 | 2016: +0.127 | 2017: +0.151 | 2018: +0.148 | 2019: +0.116 | 2020: +0.119 | 2021: +0.252 | 2022: +0.110 | 2023: +0.346 | 2024: +0.127 | 2025: +0.045 | 2026: -0.060
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.38
- Early IC=+0.1555, Recent IC=+0.0598, 1st-half IC=+0.1413, 2nd-half IC=+0.0787, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.156, Q2=-0.002, Q3_mid=+0.154, Q4=+0.094, Q5_high_vol=+0.135

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1045, Sharpe=+0.5644)
- Admission: Train IC=+0.2279, Deflated=+0.2297, IR=0.47, Mono=0.67, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.136 | 2017: +0.208 | 2018: +0.240 | 2019: +0.151 | 2020: +0.123 | 2021: +0.116 | 2022: +0.075 | 2023: +0.081 | 2024: +0.129 | 2025: +0.114 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.210 | 2016: +0.171 | 2017: +0.222 | 2018: +0.406 | 2019: +0.115 | 2020: +0.269 | 2021: +0.096 | 2022: +0.005 | 2023: +0.146 | 2024: +0.186 | 2025: -0.057 | 2026: +0.115
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.51
- Early IC=+0.1862, Recent IC=+0.0953, 1st-half IC=+0.2237, 2nd-half IC=+0.1192, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.217, Q2=-0.003, Q3_mid=+0.174, Q4=+0.166, Q5_high_vol=+0.230

**`combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0`** (Lock IC=+0.0977, Sharpe=+0.5571)
- Admission: Train IC=+0.2527, Deflated=+0.2547, IR=0.75, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.078 | 2017: +0.226 | 2018: +0.222 | 2019: +0.134 | 2020: +0.144 | 2021: +0.127 | 2022: +0.096 | 2023: +0.097 | 2024: +0.155 | 2025: +0.106 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.030 | 2017: +0.255 | 2018: +0.355 | 2019: +0.133 | 2020: +0.218 | 2021: +0.327 | 2022: +0.246 | 2023: +0.335 | 2024: +0.261 | 2025: +0.019 | 2026: -0.230
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.71
- Early IC=+0.1576, Recent IC=+0.1113, 1st-half IC=+0.2063, 2nd-half IC=+0.1297, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.010, Q3_mid=+0.191, Q4=+0.166, Q5_high_vol=+0.216

**`combo_rank_max__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.0990, Sharpe=+0.5523)
- Admission: Train IC=+0.2007, Deflated=+0.2015, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.085 | 2017: +0.158 | 2018: +0.159 | 2019: +0.103 | 2020: +0.101 | 2021: +0.037 | 2022: +0.140 | 2023: +0.077 | 2024: +0.103 | 2025: +0.083 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.196 | 2017: +0.154 | 2018: +0.098 | 2019: +0.233 | 2020: +0.066 | 2021: +0.225 | 2022: +0.189 | 2023: +0.098 | 2024: +0.144 | 2025: +0.017 | 2026: -0.237
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.51
- Early IC=+0.1702, Recent IC=+0.0872, 1st-half IC=+0.1910, 2nd-half IC=+0.0987, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.008, Q3_mid=+0.181, Q4=+0.110, Q5_high_vol=+0.200

**`combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0987, Sharpe=+0.5514)
- Admission: Train IC=+0.2495, Deflated=+0.2515, IR=0.83, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.061 | 2017: +0.199 | 2018: +0.211 | 2019: +0.135 | 2020: +0.107 | 2021: +0.105 | 2022: +0.069 | 2023: +0.084 | 2024: +0.135 | 2025: +0.143 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.339 | 2016: +0.064 | 2017: +0.318 | 2018: +0.341 | 2019: +0.235 | 2020: +0.173 | 2021: +0.346 | 2022: +0.261 | 2023: +0.239 | 2024: +0.262 | 2025: +0.126 | 2026: -0.101
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.67
- Early IC=+0.1305, Recent IC=+0.0870, 1st-half IC=+0.1755, 2nd-half IC=+0.1075, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.185, Q2=-0.007, Q3_mid=+0.160, Q4=+0.139, Q5_high_vol=+0.177

**`combo_clamp_diff__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0933, Sharpe=+0.5494)
- Admission: Train IC=+0.2952, Deflated=+0.2964, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.088 | 2017: +0.137 | 2018: +0.251 | 2019: +0.171 | 2020: +0.188 | 2021: +0.165 | 2022: +0.050 | 2023: +0.104 | 2024: +0.154 | 2025: +0.047 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.099 | 2017: +0.382 | 2018: +0.539 | 2019: +0.302 | 2020: -0.018 | 2021: +0.199 | 2022: +0.235 | 2023: +0.080 | 2024: +0.123 | 2025: -0.016 | 2026: -0.012
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.67, Recency ratio=0.58
- Early IC=+0.1858, Recent IC=+0.1076, 1st-half IC=+0.2187, 2nd-half IC=+0.1470, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.080, Q3_mid=+0.187, Q4=+0.163, Q5_high_vol=+0.284

**`combo_mean__max_down_ret__close_vs_open_range`** (Lock IC=+0.0920, Sharpe=+0.5487)
- Admission: Train IC=+0.1908, Deflated=+0.1925, IR=0.48, Mono=0.66, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.072 | 2017: +0.211 | 2018: +0.127 | 2019: +0.092 | 2020: +0.130 | 2021: +0.066 | 2022: +0.077 | 2023: +0.069 | 2024: +0.131 | 2025: +0.131 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.295 | 2016: -0.084 | 2017: +0.259 | 2018: +0.076 | 2019: +0.252 | 2020: +0.106 | 2021: +0.332 | 2022: +0.247 | 2023: +0.135 | 2024: +0.382 | 2025: +0.001 | 2026: -0.030
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.58, Recency ratio=0.42
- Early IC=+0.1679, Recent IC=+0.0713, 1st-half IC=+0.1625, 2nd-half IC=+0.0950, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.018, Q3_mid=+0.159, Q4=+0.127, Q5_high_vol=+0.170

**`combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early`** (Lock IC=+0.1061, Sharpe=+0.5479)
- Admission: Train IC=+0.3062, Deflated=+0.3081, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.058 | 2017: +0.215 | 2018: +0.135 | 2019: +0.094 | 2020: +0.114 | 2021: +0.099 | 2022: +0.022 | 2023: +0.081 | 2024: +0.146 | 2025: +0.104 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.142 | 2017: +0.418 | 2018: +0.376 | 2019: +0.193 | 2020: +0.262 | 2021: +0.150 | 2022: +0.359 | 2023: -0.183 | 2024: +0.302 | 2025: -0.025 | 2026: +0.204
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.50
- Early IC=+0.1221, Recent IC=+0.0606, 1st-half IC=+0.1544, 2nd-half IC=+0.0929, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.024, Q3_mid=+0.123, Q4=+0.162, Q5_high_vol=+0.130

**`combo_sig_product__max_up_ret__max_down_ret`** (Lock IC=+0.1262, Sharpe=+0.5466)
- Admission: Train IC=+0.1686, Deflated=+0.1689, IR=0.52, Mono=0.70, p=0.0002, MaxCorr=0.69
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.185 | 2017: -0.006 | 2018: +0.164 | 2019: +0.173 | 2020: +0.156 | 2021: +0.096 | 2022: +0.084 | 2023: +0.140 | 2024: +0.165 | 2025: +0.148 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.156 | 2017: +0.141 | 2018: +0.196 | 2019: +0.299 | 2020: +0.079 | 2021: +0.298 | 2022: +0.051 | 2023: +0.106 | 2024: +0.334 | 2025: +0.248 | 2026: -0.007
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=0.72, Recency ratio=0.45
- Early IC=+0.1992, Recent IC=+0.0903, 1st-half IC=+0.1767, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.104, Q3_mid=+0.167, Q4=+0.132, Q5_high_vol=+0.222

**`combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0798, Sharpe=+0.5325)
- Admission: Train IC=+0.1522, Deflated=+0.1526, IR=0.40, Mono=0.66, p=0.0024, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.052 | 2017: +0.153 | 2018: +0.129 | 2019: +0.073 | 2020: +0.101 | 2021: +0.023 | 2022: +0.070 | 2023: +0.082 | 2024: +0.046 | 2025: +0.109 | 2026: +0.066
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.046 | 2017: +0.137 | 2018: +0.210 | 2019: +0.186 | 2020: +0.063 | 2021: +0.037 | 2022: +0.053 | 2023: -0.050 | 2024: +0.057 | 2025: +0.137 | 2026: -0.007
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.39, Recency ratio=0.33
- Early IC=+0.1410, Recent IC=+0.0467, 1st-half IC=+0.1724, 2nd-half IC=+0.0680, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.004, Q3_mid=+0.132, Q4=+0.140, Q5_high_vol=+0.158

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0954, Sharpe=+0.5296)
- Admission: Train IC=+0.2575, Deflated=+0.2596, IR=0.95, Mono=0.83, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.104 | 2017: +0.210 | 2018: +0.237 | 2019: +0.160 | 2020: +0.150 | 2021: +0.109 | 2022: +0.072 | 2023: +0.094 | 2024: +0.125 | 2025: +0.124 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.399 | 2016: +0.072 | 2017: +0.312 | 2018: +0.441 | 2019: +0.147 | 2020: +0.177 | 2021: +0.229 | 2022: +0.233 | 2023: +0.191 | 2024: +0.241 | 2025: +0.111 | 2026: -0.190
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.49
- Early IC=+0.1834, Recent IC=+0.0904, 1st-half IC=+0.2168, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.037, Q3_mid=+0.186, Q4=+0.156, Q5_high_vol=+0.236

**`combo_rel_diff__max_down_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0757, Sharpe=+0.5266)
- Admission: Train IC=+0.1663, Deflated=+0.1677, IR=0.53, Mono=0.70, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.091 | 2017: +0.153 | 2018: +0.081 | 2019: +0.072 | 2020: +0.087 | 2021: +0.056 | 2022: +0.084 | 2023: +0.093 | 2024: +0.121 | 2025: +0.100 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.429 | 2016: +0.161 | 2017: +0.164 | 2018: +0.075 | 2019: +0.149 | 2020: -0.022 | 2021: +0.179 | 2022: +0.229 | 2023: +0.342 | 2024: +0.349 | 2025: +0.002 | 2026: +0.065
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=0.59, Recency ratio=0.45
- Early IC=+0.1544, Recent IC=+0.0701, 1st-half IC=+0.1370, 2nd-half IC=+0.0815, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.003, Q3_mid=+0.157, Q4=+0.088, Q5_high_vol=+0.132

**`combo_rank_max__max_down_ret__close_vs_open_range`** (Lock IC=+0.0837, Sharpe=+0.5254)
- Admission: Train IC=+0.1851, Deflated=+0.1867, IR=0.51, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.052 | 2017: +0.221 | 2018: +0.142 | 2019: +0.105 | 2020: +0.110 | 2021: +0.094 | 2022: +0.060 | 2023: +0.040 | 2024: +0.137 | 2025: +0.164 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.102 | 2017: +0.265 | 2018: +0.092 | 2019: +0.302 | 2020: +0.059 | 2021: +0.286 | 2022: +0.167 | 2023: +0.094 | 2024: +0.275 | 2025: +0.369 | 2026: +0.119
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.53
- Early IC=+0.1449, Recent IC=+0.0774, 1st-half IC=+0.1607, 2nd-half IC=+0.0960, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.011, Q3_mid=+0.165, Q4=+0.126, Q5_high_vol=+0.141

**`combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction`** (Lock IC=+0.0741, Sharpe=+0.5169)
- Admission: Train IC=+0.1889, Deflated=+0.1893, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.031 | 2017: +0.155 | 2018: +0.069 | 2019: +0.021 | 2020: +0.096 | 2021: +0.031 | 2022: +0.027 | 2023: +0.122 | 2024: +0.087 | 2025: +0.124 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.109 | 2016: +0.115 | 2017: +0.277 | 2018: +0.155 | 2019: +0.136 | 2020: +0.126 | 2021: +0.260 | 2022: +0.189 | 2023: +0.152 | 2024: +0.220 | 2025: +0.205 | 2026: -0.268
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.43
- Early IC=+0.0713, Recent IC=+0.0304, 1st-half IC=+0.1038, 2nd-half IC=+0.0550, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.010, Q3_mid=+0.100, Q4=+0.092, Q5_high_vol=+0.060

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0911, Sharpe=+0.5122)
- Admission: Train IC=+0.2762, Deflated=+0.2774, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.307 | 2016: +0.097 | 2017: +0.193 | 2018: +0.219 | 2019: +0.152 | 2020: +0.160 | 2021: +0.131 | 2022: +0.064 | 2023: +0.102 | 2024: +0.127 | 2025: +0.017 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.161 | 2017: +0.391 | 2018: +0.359 | 2019: +0.363 | 2020: +0.102 | 2021: +0.125 | 2022: +0.226 | 2023: +0.180 | 2024: +0.150 | 2025: +0.055 | 2026: +0.120
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.48
- Early IC=+0.2019, Recent IC=+0.0978, 1st-half IC=+0.2231, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.025, Q3_mid=+0.184, Q4=+0.165, Q5_high_vol=+0.295

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0953, Sharpe=+0.5051)
- Admission: Train IC=+0.2677, Deflated=+0.2692, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.298 | 2016: +0.084 | 2017: +0.247 | 2018: +0.153 | 2019: +0.107 | 2020: +0.169 | 2021: +0.114 | 2022: +0.115 | 2023: +0.079 | 2024: +0.150 | 2025: +0.115 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.519 | 2016: +0.162 | 2017: +0.286 | 2018: +0.231 | 2019: +0.256 | 2020: +0.067 | 2021: +0.312 | 2022: +0.231 | 2023: +0.113 | 2024: +0.242 | 2025: +0.054 | 2026: -0.056
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.60
- Early IC=+0.1910, Recent IC=+0.1145, 1st-half IC=+0.2028, 2nd-half IC=+0.1301, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.038, Q3_mid=+0.184, Q4=+0.171, Q5_high_vol=+0.226

**`combo_clamp_diff__first_bar_return__early_late_momentum_divergence`** (Lock IC=+0.0777, Sharpe=+0.5035)
- Admission: Train IC=+0.2452, Deflated=+0.2470, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.068 | 2017: +0.156 | 2018: +0.223 | 2019: +0.193 | 2020: +0.114 | 2021: +0.121 | 2022: +0.065 | 2023: +0.063 | 2024: +0.115 | 2025: +0.012 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.078 | 2017: +0.384 | 2018: +0.352 | 2019: +0.188 | 2020: +0.248 | 2021: +0.114 | 2022: +0.199 | 2023: +0.106 | 2024: +0.120 | 2025: -0.006 | 2026: -0.169
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.50
- Early IC=+0.1848, Recent IC=+0.0929, 1st-half IC=+0.1962, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.006, Q3_mid=+0.166, Q4=+0.170, Q5_high_vol=+0.260

**`combo_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0893, Sharpe=+0.5003)
- Admission: Train IC=+0.2436, Deflated=+0.2448, IR=0.90, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.299 | 2016: +0.098 | 2017: +0.194 | 2018: +0.220 | 2019: +0.151 | 2020: +0.157 | 2021: +0.135 | 2022: +0.064 | 2023: +0.101 | 2024: +0.124 | 2025: +0.013 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.216 | 2017: +0.413 | 2018: +0.380 | 2019: +0.326 | 2020: +0.132 | 2021: +0.245 | 2022: +0.134 | 2023: +0.198 | 2024: +0.036 | 2025: -0.032 | 2026: +0.053
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.50
- Early IC=+0.1985, Recent IC=+0.0992, 1st-half IC=+0.2229, 2nd-half IC=+0.1287, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.027, Q3_mid=+0.182, Q4=+0.162, Q5_high_vol=+0.290

**`combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1101, Sharpe=+0.4988)
- Admission: Train IC=+0.2091, Deflated=+0.2099, IR=0.48, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.102 | 2017: +0.246 | 2018: +0.139 | 2019: +0.137 | 2020: +0.130 | 2021: +0.050 | 2022: +0.134 | 2023: +0.080 | 2024: +0.104 | 2025: +0.080 | 2026: +0.142
- Yearly Tail ICs:   2015: +0.222 | 2016: +0.144 | 2017: +0.171 | 2018: +0.053 | 2019: +0.295 | 2020: +0.064 | 2021: +0.144 | 2022: +0.108 | 2023: -0.025 | 2024: +0.060 | 2025: +0.087 | 2026: +0.140
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.46
- Early IC=+0.2043, Recent IC=+0.0947, 1st-half IC=+0.2235, 2nd-half IC=+0.1189, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.036, Q3_mid=+0.188, Q4=+0.128, Q5_high_vol=+0.246

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum`** (Lock IC=+0.0976, Sharpe=+0.4983)
- Admission: Train IC=+0.2819, Deflated=+0.2831, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.106 | 2017: +0.218 | 2018: +0.209 | 2019: +0.128 | 2020: +0.140 | 2021: +0.092 | 2022: +0.103 | 2023: +0.107 | 2024: +0.140 | 2025: +0.129 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.241 | 2017: +0.343 | 2018: +0.424 | 2019: +0.242 | 2020: +0.246 | 2021: +0.183 | 2022: +0.086 | 2023: +0.103 | 2024: +0.315 | 2025: -0.090 | 2026: -0.212
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.54
- Early IC=+0.1800, Recent IC=+0.0974, 1st-half IC=+0.2206, 2nd-half IC=+0.1178, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.045, Q3_mid=+0.171, Q4=+0.176, Q5_high_vol=+0.223

**`combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction`** (Lock IC=+0.0934, Sharpe=+0.4880)
- Admission: Train IC=+0.2287, Deflated=+0.2301, IR=0.57, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.063 | 2017: +0.194 | 2018: +0.119 | 2019: +0.079 | 2020: +0.094 | 2021: +0.069 | 2022: +0.089 | 2023: +0.088 | 2024: +0.138 | 2025: +0.134 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.342 | 2016: +0.154 | 2017: +0.207 | 2018: +0.130 | 2019: +0.220 | 2020: +0.167 | 2021: +0.115 | 2022: +0.356 | 2023: +0.207 | 2024: +0.318 | 2025: +0.125 | 2026: +0.037
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.71
- Early IC=+0.1111, Recent IC=+0.0792, 1st-half IC=+0.1402, 2nd-half IC=+0.0861, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.166, Q2=-0.006, Q3_mid=+0.133, Q4=+0.129, Q5_high_vol=+0.119

**`combo_diff__first_bar_return__early_late_momentum_divergence`** (Lock IC=+0.0786, Sharpe=+0.4874)
- Admission: Train IC=+0.1828, Deflated=+0.1845, IR=0.45, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.062 | 2017: +0.157 | 2018: +0.222 | 2019: +0.190 | 2020: +0.112 | 2021: +0.122 | 2022: +0.064 | 2023: +0.066 | 2024: +0.119 | 2025: +0.012 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.271 | 2016: -0.079 | 2017: +0.392 | 2018: +0.328 | 2019: +0.050 | 2020: +0.224 | 2021: +0.147 | 2022: +0.060 | 2023: +0.278 | 2024: +0.225 | 2025: +0.007 | 2026: -0.070
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.52
- Early IC=+0.1779, Recent IC=+0.0932, 1st-half IC=+0.1942, 2nd-half IC=+0.1230, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.002, Q3_mid=+0.163, Q4=+0.172, Q5_high_vol=+0.251

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0906, Sharpe=+0.4864)
- Admission: Train IC=+0.2176, Deflated=+0.2187, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.036 | 2017: +0.155 | 2018: +0.201 | 2019: +0.172 | 2020: +0.189 | 2021: +0.153 | 2022: +0.030 | 2023: +0.100 | 2024: +0.134 | 2025: +0.055 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.354 | 2016: -0.005 | 2017: +0.344 | 2018: +0.297 | 2019: +0.307 | 2020: -0.005 | 2021: +0.320 | 2022: +0.061 | 2023: +0.106 | 2024: +0.177 | 2025: +0.040 | 2026: +0.250
- IC CV=0.48, Neg years (linear/tail)=0/2 of 8, Half ratio=0.83, Recency ratio=0.66
- Early IC=+0.1396, Recent IC=+0.0915, 1st-half IC=+0.1699, 2nd-half IC=+0.1407, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.063, Q3_mid=+0.166, Q4=+0.140, Q5_high_vol=+0.251

**`combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1257, Sharpe=+0.4863)
- Admission: Train IC=+0.2515, Deflated=+0.2530, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.057 | 2017: +0.252 | 2018: +0.164 | 2019: +0.141 | 2020: +0.165 | 2021: +0.096 | 2022: +0.088 | 2023: +0.126 | 2024: +0.140 | 2025: +0.136 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.437 | 2016: +0.141 | 2017: +0.180 | 2018: +0.102 | 2019: +0.335 | 2020: +0.115 | 2021: +0.163 | 2022: +0.411 | 2023: +0.091 | 2024: +0.277 | 2025: +0.202 | 2026: -0.036
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.52
- Early IC=+0.1761, Recent IC=+0.0922, 1st-half IC=+0.2079, 2nd-half IC=+0.1292, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.047, Q3_mid=+0.175, Q4=+0.169, Q5_high_vol=+0.236

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum`** (Lock IC=+0.0791, Sharpe=+0.4862)
- Admission: Train IC=+0.2403, Deflated=+0.2417, IR=0.88, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.104 | 2017: +0.211 | 2018: +0.194 | 2019: +0.084 | 2020: +0.162 | 2021: +0.111 | 2022: +0.123 | 2023: +0.077 | 2024: +0.147 | 2025: +0.073 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.229 | 2017: +0.346 | 2018: +0.267 | 2019: +0.112 | 2020: +0.217 | 2021: +0.163 | 2022: +0.180 | 2023: +0.164 | 2024: +0.262 | 2025: -0.163 | 2026: -0.339
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.68
- Early IC=+0.1720, Recent IC=+0.1170, 1st-half IC=+0.2120, 2nd-half IC=+0.1273, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.020, Q3_mid=+0.193, Q4=+0.177, Q5_high_vol=+0.234

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1175, Sharpe=+0.4851)
- Admission: Train IC=+0.2722, Deflated=+0.2732, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.178 | 2017: +0.079 | 2018: +0.133 | 2019: +0.078 | 2020: +0.127 | 2021: +0.110 | 2022: +0.120 | 2023: +0.156 | 2024: +0.134 | 2025: +0.127 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.234 | 2017: +0.382 | 2018: +0.247 | 2019: +0.181 | 2020: +0.134 | 2021: +0.279 | 2022: +0.141 | 2023: +0.085 | 2024: +0.255 | 2025: -0.001 | 2026: +0.008
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.52
- Early IC=+0.2223, Recent IC=+0.1155, 1st-half IC=+0.1862, 2nd-half IC=+0.1084, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.046, Q3_mid=+0.149, Q4=+0.171, Q5_high_vol=+0.220

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0908, Sharpe=+0.4830)
- Admission: Train IC=+0.2386, Deflated=+0.2405, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.142 | 2017: +0.197 | 2018: +0.245 | 2019: +0.130 | 2020: +0.114 | 2021: +0.134 | 2022: +0.089 | 2023: +0.092 | 2024: +0.137 | 2025: +0.099 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.172 | 2017: +0.333 | 2018: +0.460 | 2019: +0.133 | 2020: +0.190 | 2021: +0.347 | 2022: +0.114 | 2023: +0.194 | 2024: +0.178 | 2025: +0.043 | 2026: -0.224
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.56
- Early IC=+0.2014, Recent IC=+0.1118, 1st-half IC=+0.2339, 2nd-half IC=+0.1196, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.011, Q3_mid=+0.173, Q4=+0.191, Q5_high_vol=+0.265

**`combo_rel_diff__net_volume_flow__h2_l2_pullback_continuation`** (Lock IC=+0.0737, Sharpe=+0.4824)
- Admission: Train IC=+0.2300, Deflated=+0.2314, IR=0.43, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.074 | 2017: +0.149 | 2018: +0.096 | 2019: +0.069 | 2020: +0.096 | 2021: +0.061 | 2022: +0.101 | 2023: +0.097 | 2024: +0.106 | 2025: +0.121 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.154 | 2017: +0.058 | 2018: +0.176 | 2019: +0.246 | 2020: +0.136 | 2021: +0.189 | 2022: +0.191 | 2023: +0.254 | 2024: +0.276 | 2025: -0.048 | 2026: +0.085
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.74
- Early IC=+0.1094, Recent IC=+0.0809, 1st-half IC=+0.1271, 2nd-half IC=+0.0882, Neg regimes=1/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.160, Q2=-0.010, Q3_mid=+0.170, Q4=+0.103, Q5_high_vol=+0.103

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1223, Sharpe=+0.4818)
- Admission: Train IC=+0.2006, Deflated=+0.2008, IR=0.37, Mono=0.67, p=0.0000, MaxCorr=0.64
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.063 | 2017: +0.223 | 2018: +0.101 | 2019: +0.173 | 2020: +0.110 | 2021: +0.090 | 2022: +0.107 | 2023: +0.079 | 2024: +0.145 | 2025: +0.051 | 2026: +0.194
- Yearly Tail ICs:   2015: +0.200 | 2016: -0.072 | 2017: +0.236 | 2018: +0.331 | 2019: +0.253 | 2020: +0.180 | 2021: +0.237 | 2022: +0.213 | 2023: -0.015 | 2024: +0.070 | 2025: -0.142 | 2026: +0.233
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.73, Recency ratio=0.83
- Early IC=+0.1188, Recent IC=+0.0983, 1st-half IC=+0.1602, 2nd-half IC=+0.1161, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.043, Q3_mid=+0.131, Q4=+0.158, Q5_high_vol=+0.167

**`combo_mean__max_up_ret__bar_ret_0`** (Lock IC=+0.0854, Sharpe=+0.4811)
- Admission: Train IC=+0.2289, Deflated=+0.2302, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.110 | 2017: +0.192 | 2018: +0.242 | 2019: +0.136 | 2020: +0.112 | 2021: +0.136 | 2022: +0.101 | 2023: +0.097 | 2024: +0.142 | 2025: +0.077 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.127 | 2017: +0.268 | 2018: +0.466 | 2019: +0.114 | 2020: +0.232 | 2021: +0.278 | 2022: +0.107 | 2023: +0.141 | 2024: +0.147 | 2025: +0.045 | 2026: -0.250
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.66
- Early IC=+0.1802, Recent IC=+0.1188, 1st-half IC=+0.2228, 2nd-half IC=+0.1214, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.015, Q3_mid=+0.161, Q4=+0.184, Q5_high_vol=+0.245

**`combo_tri_median__trend_bar_close_consistency__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0970, Sharpe=+0.4794)
- Admission: Train IC=+0.2394, Deflated=+0.2405, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.096 | 2017: +0.191 | 2018: +0.226 | 2019: +0.125 | 2020: +0.127 | 2021: +0.065 | 2022: +0.092 | 2023: +0.106 | 2024: +0.108 | 2025: +0.145 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.161 | 2017: +0.324 | 2018: +0.379 | 2019: +0.247 | 2020: +0.246 | 2021: +0.014 | 2022: +0.212 | 2023: +0.251 | 2024: +0.179 | 2025: -0.070 | 2026: +0.090
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.51
- Early IC=+0.1551, Recent IC=+0.0784, 1st-half IC=+0.1991, 2nd-half IC=+0.1081, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.021, Q3_mid=+0.168, Q4=+0.159, Q5_high_vol=+0.184

**`combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1136, Sharpe=+0.4793)
- Admission: Train IC=+0.2597, Deflated=+0.2611, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.292 | 2016: +0.088 | 2017: +0.243 | 2018: +0.176 | 2019: +0.147 | 2020: +0.179 | 2021: +0.116 | 2022: +0.068 | 2023: +0.075 | 2024: +0.138 | 2025: +0.091 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.195 | 2017: +0.182 | 2018: +0.278 | 2019: +0.392 | 2020: +0.133 | 2021: +0.163 | 2022: +0.096 | 2023: -0.090 | 2024: +0.213 | 2025: -0.058 | 2026: +0.173
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.48
- Early IC=+0.1902, Recent IC=+0.0920, 1st-half IC=+0.2236, 2nd-half IC=+0.1327, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.043, Q3_mid=+0.180, Q4=+0.196, Q5_high_vol=+0.228

**`combo_rank_max__max_up_ret__close_vs_open_range`** (Lock IC=+0.0854, Sharpe=+0.4781)
- Admission: Train IC=+0.2286, Deflated=+0.2307, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.098 | 2017: +0.216 | 2018: +0.206 | 2019: +0.101 | 2020: +0.143 | 2021: +0.092 | 2022: +0.116 | 2023: +0.095 | 2024: +0.131 | 2025: +0.078 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.252 | 2017: +0.228 | 2018: +0.284 | 2019: +0.150 | 2020: +0.278 | 2021: +0.168 | 2022: +0.077 | 2023: +0.158 | 2024: +0.260 | 2025: -0.228 | 2026: -0.409
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.58
- Early IC=+0.1768, Recent IC=+0.1028, 1st-half IC=+0.2058, 2nd-half IC=+0.1173, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.018, Q3_mid=+0.182, Q4=+0.160, Q5_high_vol=+0.239

**`combo_rank_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0813, Sharpe=+0.4751)
- Admission: Train IC=+0.2412, Deflated=+0.2430, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.111 | 2017: +0.152 | 2018: +0.220 | 2019: +0.070 | 2020: +0.137 | 2021: +0.059 | 2022: +0.127 | 2023: +0.094 | 2024: +0.130 | 2025: +0.095 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.282 | 2016: +0.238 | 2017: +0.217 | 2018: +0.277 | 2019: +0.080 | 2020: +0.366 | 2021: +0.175 | 2022: +0.146 | 2023: +0.168 | 2024: +0.253 | 2025: -0.106 | 2026: -0.333
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.56
- Early IC=+0.1675, Recent IC=+0.0931, 1st-half IC=+0.1973, 2nd-half IC=+0.1037, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.000, Q3_mid=+0.179, Q4=+0.161, Q5_high_vol=+0.236

**`combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1064, Sharpe=+0.4742)
- Admission: Train IC=+0.2437, Deflated=+0.2446, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.137 | 2017: +0.227 | 2018: +0.161 | 2019: +0.120 | 2020: +0.188 | 2021: +0.091 | 2022: +0.118 | 2023: +0.075 | 2024: +0.110 | 2025: +0.081 | 2026: +0.138
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.378 | 2017: +0.076 | 2018: +0.136 | 2019: +0.253 | 2020: +0.147 | 2021: +0.156 | 2022: +0.040 | 2023: -0.129 | 2024: +0.106 | 2025: +0.032 | 2026: +0.161
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.49
- Early IC=+0.2154, Recent IC=+0.1047, 1st-half IC=+0.2340, 2nd-half IC=+0.1305, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.038, Q3_mid=+0.193, Q4=+0.148, Q5_high_vol=+0.270

**`combo_rank_min__early_order_flow_imbalance__bar_body_rng_0`** (Lock IC=+0.0788, Sharpe=+0.4742)
- Admission: Train IC=+0.1961, Deflated=+0.1980, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.012 | 2017: +0.163 | 2018: +0.154 | 2019: +0.149 | 2020: +0.064 | 2021: +0.161 | 2022: +0.126 | 2023: +0.089 | 2024: +0.121 | 2025: +0.089 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.306 | 2016: +0.067 | 2017: +0.183 | 2018: +0.329 | 2019: +0.271 | 2020: +0.065 | 2021: +0.236 | 2022: +0.258 | 2023: +0.072 | 2024: +0.302 | 2025: +0.215 | 2026: -0.122
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=1.69
- Early IC=+0.0842, Recent IC=+0.1427, 1st-half IC=+0.1243, 2nd-half IC=+0.1231, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.160, Q2=-0.030, Q3_mid=+0.150, Q4=+0.172, Q5_high_vol=+0.125

**`combo_mean__star50_limit_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.1064, Sharpe=+0.4728)
- Admission: Train IC=+0.2248, Deflated=+0.2253, IR=0.70, Mono=0.73, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.058 | 2017: +0.206 | 2018: +0.152 | 2019: +0.123 | 2020: +0.114 | 2021: +0.074 | 2022: +0.067 | 2023: +0.077 | 2024: +0.108 | 2025: +0.132 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.235 | 2016: +0.175 | 2017: +0.258 | 2018: +0.200 | 2019: +0.360 | 2020: +0.124 | 2021: +0.245 | 2022: +0.186 | 2023: +0.082 | 2024: +0.146 | 2025: +0.057 | 2026: -0.135
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.49
- Early IC=+0.1455, Recent IC=+0.0706, 1st-half IC=+0.1878, 2nd-half IC=+0.1021, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.045, Q3_mid=+0.168, Q4=+0.159, Q5_high_vol=+0.143

**`combo_mean__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0942, Sharpe=+0.4728)
- Admission: Train IC=+0.2226, Deflated=+0.2236, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.042 | 2017: +0.212 | 2018: +0.120 | 2019: +0.097 | 2020: +0.126 | 2021: +0.110 | 2022: +0.109 | 2023: +0.117 | 2024: +0.140 | 2025: +0.126 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.118 | 2017: +0.223 | 2018: +0.318 | 2019: +0.314 | 2020: +0.106 | 2021: +0.274 | 2022: +0.190 | 2023: +0.366 | 2024: +0.233 | 2025: +0.052 | 2026: -0.376
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=1.01
- Early IC=+0.1087, Recent IC=+0.1093, 1st-half IC=+0.1553, 2nd-half IC=+0.1138, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.059, Q3_mid=+0.170, Q4=+0.127, Q5_high_vol=+0.147

**`combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1017, Sharpe=+0.4703)
- Admission: Train IC=+0.2048, Deflated=+0.2053, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.159 | 2017: +0.184 | 2018: +0.186 | 2019: +0.101 | 2020: +0.128 | 2021: +0.085 | 2022: +0.113 | 2023: +0.074 | 2024: +0.111 | 2025: +0.079 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.273 | 2017: +0.254 | 2018: +0.244 | 2019: +0.109 | 2020: +0.125 | 2021: +0.185 | 2022: +0.099 | 2023: -0.084 | 2024: +0.011 | 2025: -0.013 | 2026: +0.214
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.55
- Early IC=+0.1783, Recent IC=+0.0979, 1st-half IC=+0.2084, 2nd-half IC=+0.1059, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.055, Q3_mid=+0.137, Q4=+0.136, Q5_high_vol=+0.217

**`first_bar_return`** (Lock IC=+0.0699, Sharpe=+0.4640)
- Admission: Train IC=+0.1931, Deflated=+0.1945, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.52, Recency ratio=0.50
- Early IC=+0.1605, Recent IC=+0.0808, 1st-half IC=+0.1957, 2nd-half IC=+0.1008, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.162, Q2=-0.010, Q3_mid=+0.122, Q4=+0.157, Q5_high_vol=+0.200

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0884, Sharpe=+0.4616)
- Admission: Train IC=+0.2716, Deflated=+0.2730, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.097 | 2017: +0.226 | 2018: +0.192 | 2019: +0.098 | 2020: +0.118 | 2021: +0.120 | 2022: +0.103 | 2023: +0.073 | 2024: +0.130 | 2025: +0.092 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.530 | 2016: +0.310 | 2017: +0.257 | 2018: +0.249 | 2019: +0.158 | 2020: +0.152 | 2021: +0.334 | 2022: +0.050 | 2023: +0.186 | 2024: +0.259 | 2025: +0.009 | 2026: -0.089
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.61
- Early IC=+0.1823, Recent IC=+0.1115, 1st-half IC=+0.2102, 2nd-half IC=+0.1128, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.042, Q3_mid=+0.182, Q4=+0.161, Q5_high_vol=+0.243

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction`** (Lock IC=+0.1026, Sharpe=+0.4610)
- Admission: Train IC=+0.2792, Deflated=+0.2808, IR=0.79, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.264 | 2016: +0.083 | 2017: +0.232 | 2018: +0.195 | 2019: +0.102 | 2020: +0.150 | 2021: +0.124 | 2022: +0.102 | 2023: +0.112 | 2024: +0.143 | 2025: +0.122 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.378 | 2016: +0.262 | 2017: +0.251 | 2018: +0.354 | 2019: +0.149 | 2020: +0.135 | 2021: +0.176 | 2022: +0.317 | 2023: +0.307 | 2024: +0.236 | 2025: -0.011 | 2026: -0.141
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.65
- Early IC=+0.1737, Recent IC=+0.1130, 1st-half IC=+0.2102, 2nd-half IC=+0.1231, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.032, Q3_mid=+0.191, Q4=+0.168, Q5_high_vol=+0.218

**`combo_sig_product__max_up_ret__early_body_momentum`** (Lock IC=+0.1052, Sharpe=+0.4585)
- Admission: Train IC=+0.2543, Deflated=+0.2549, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.184 | 2017: +0.135 | 2018: +0.159 | 2019: +0.071 | 2020: +0.151 | 2021: +0.103 | 2022: +0.107 | 2023: +0.138 | 2024: +0.138 | 2025: +0.122 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.361 | 2016: +0.212 | 2017: +0.163 | 2018: +0.176 | 2019: +0.144 | 2020: +0.312 | 2021: +0.281 | 2022: +0.089 | 2023: +0.142 | 2024: +0.317 | 2025: +0.009 | 2026: -0.143
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.51
- Early IC=+0.2072, Recent IC=+0.1048, 1st-half IC=+0.1959, 2nd-half IC=+0.1124, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.031, Q3_mid=+0.151, Q4=+0.154, Q5_high_vol=+0.221

**`combo_max__max_up_ret__close_vs_open_range`** (Lock IC=+0.0860, Sharpe=+0.4491)
- Admission: Train IC=+0.2333, Deflated=+0.2353, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.098 | 2017: +0.208 | 2018: +0.208 | 2019: +0.092 | 2020: +0.147 | 2021: +0.079 | 2022: +0.116 | 2023: +0.097 | 2024: +0.129 | 2025: +0.088 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.318 | 2016: +0.242 | 2017: +0.210 | 2018: +0.313 | 2019: +0.127 | 2020: +0.271 | 2021: +0.154 | 2022: +0.072 | 2023: +0.185 | 2024: +0.259 | 2025: -0.203 | 2026: -0.403
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.56
- Early IC=+0.1725, Recent IC=+0.0974, 1st-half IC=+0.2080, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.011, Q3_mid=+0.180, Q4=+0.162, Q5_high_vol=+0.235

**`combo_max__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0880, Sharpe=+0.4480)
- Admission: Train IC=+0.2658, Deflated=+0.2668, IR=0.91, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.087 | 2017: +0.214 | 2018: +0.161 | 2019: +0.087 | 2020: +0.153 | 2021: +0.107 | 2022: +0.109 | 2023: +0.075 | 2024: +0.149 | 2025: +0.116 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.242 | 2017: +0.355 | 2018: +0.162 | 2019: +0.245 | 2020: +0.250 | 2021: +0.237 | 2022: +0.202 | 2023: +0.241 | 2024: +0.275 | 2025: +0.001 | 2026: -0.196
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.62
- Early IC=+0.1735, Recent IC=+0.1080, 1st-half IC=+0.1993, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.030, Q3_mid=+0.189, Q4=+0.168, Q5_high_vol=+0.207

**`combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction`** (Lock IC=+0.0736, Sharpe=+0.4467)
- Admission: Train IC=+0.1927, Deflated=+0.1930, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.026 | 2017: +0.150 | 2018: +0.080 | 2019: +0.011 | 2020: +0.091 | 2021: +0.035 | 2022: +0.018 | 2023: +0.130 | 2024: +0.078 | 2025: +0.124 | 2026: -0.090
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.125 | 2017: +0.275 | 2018: +0.165 | 2019: +0.188 | 2020: +0.129 | 2021: +0.236 | 2022: +0.191 | 2023: +0.218 | 2024: +0.180 | 2025: +0.145 | 2026: -0.275
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.39
- Early IC=+0.0677, Recent IC=+0.0266, 1st-half IC=+0.1045, 2nd-half IC=+0.0482, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.007, Q3_mid=+0.089, Q4=+0.094, Q5_high_vol=+0.056

**`combo_rank_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0894, Sharpe=+0.4449)
- Admission: Train IC=+0.2083, Deflated=+0.2092, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.103 | 2017: +0.203 | 2018: +0.170 | 2019: +0.101 | 2020: +0.139 | 2021: +0.094 | 2022: +0.120 | 2023: +0.128 | 2024: +0.134 | 2025: +0.095 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.255 | 2016: +0.139 | 2017: +0.157 | 2018: +0.289 | 2019: +0.203 | 2020: +0.112 | 2021: +0.111 | 2022: +0.114 | 2023: +0.408 | 2024: +0.211 | 2025: -0.160 | 2026: -0.477
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.69
- Early IC=+0.1556, Recent IC=+0.1078, 1st-half IC=+0.1871, 2nd-half IC=+0.1218, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.072, Q3_mid=+0.164, Q4=+0.130, Q5_high_vol=+0.210

**`combo_rank_max__early_body_momentum__max_down_ret`** (Lock IC=+0.0776, Sharpe=+0.4425)
- Admission: Train IC=+0.2028, Deflated=+0.2041, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.047 | 2017: +0.196 | 2018: +0.163 | 2019: +0.093 | 2020: +0.102 | 2021: +0.073 | 2022: +0.075 | 2023: +0.042 | 2024: +0.131 | 2025: +0.167 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.058 | 2017: +0.278 | 2018: +0.099 | 2019: +0.329 | 2020: +0.051 | 2021: +0.261 | 2022: +0.263 | 2023: +0.160 | 2024: +0.238 | 2025: +0.295 | 2026: -0.085
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.62
- Early IC=+0.1197, Recent IC=+0.0741, 1st-half IC=+0.1582, 2nd-half IC=+0.0909, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.008, Q3_mid=+0.178, Q4=+0.140, Q5_high_vol=+0.121

**`combo_min__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.1018, Sharpe=+0.4421)
- Admission: Train IC=+0.2378, Deflated=+0.2396, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.061 | 2017: +0.201 | 2018: +0.176 | 2019: +0.114 | 2020: +0.137 | 2021: +0.113 | 2022: +0.048 | 2023: +0.111 | 2024: +0.143 | 2025: +0.116 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.339 | 2016: +0.152 | 2017: +0.326 | 2018: +0.242 | 2019: +0.368 | 2020: +0.134 | 2021: +0.286 | 2022: +0.142 | 2023: +0.087 | 2024: +0.399 | 2025: -0.016 | 2026: +0.118
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.63
- Early IC=+0.1283, Recent IC=+0.0805, 1st-half IC=+0.1647, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.015, Q3_mid=+0.175, Q4=+0.120, Q5_high_vol=+0.167

**`combo_mean__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.0923, Sharpe=+0.4385)
- Admission: Train IC=+0.2601, Deflated=+0.2609, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.089 | 2017: +0.154 | 2018: +0.130 | 2019: +0.094 | 2020: +0.125 | 2021: +0.055 | 2022: +0.105 | 2023: +0.058 | 2024: +0.096 | 2025: +0.106 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.269 | 2016: +0.108 | 2017: +0.230 | 2018: +0.267 | 2019: +0.301 | 2020: +0.166 | 2021: +0.134 | 2022: +0.295 | 2023: +0.161 | 2024: +0.173 | 2025: +0.089 | 2026: -0.023
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.54
- Early IC=+0.1487, Recent IC=+0.0802, 1st-half IC=+0.1656, 2nd-half IC=+0.0994, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.005, Q3_mid=+0.154, Q4=+0.168, Q5_high_vol=+0.139

**`combo_max__early_body_momentum__bar_body_rng_0`** (Lock IC=+0.0715, Sharpe=+0.4327)
- Admission: Train IC=+0.2782, Deflated=+0.2798, IR=0.94, Mono=0.84, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.127 | 2017: +0.155 | 2018: +0.182 | 2019: +0.088 | 2020: +0.141 | 2021: +0.106 | 2022: +0.093 | 2023: +0.066 | 2024: +0.115 | 2025: +0.120 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.415 | 2016: +0.132 | 2017: +0.236 | 2018: +0.185 | 2019: +0.217 | 2020: +0.369 | 2021: +0.212 | 2022: +0.291 | 2023: +0.303 | 2024: +0.268 | 2025: -0.013 | 2026: -0.430
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.60
- Early IC=+0.1659, Recent IC=+0.0997, 1st-half IC=+0.1792, 2nd-half IC=+0.1121, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.023, Q3_mid=+0.153, Q4=+0.153, Q5_high_vol=+0.212

**`max_up_ret`** (Lock IC=+0.0920, Sharpe=+0.4322)
- Admission: Train IC=+0.2317, Deflated=+0.2328, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143 | 2025: +0.080 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.194 | 2017: +0.220 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.134 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.66
- Early IC=+0.1762, Recent IC=+0.1170, 1st-half IC=+0.2058, 2nd-half IC=+0.1174, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.046, Q3_mid=+0.174, Q4=+0.172, Q5_high_vol=+0.241

**`combo_min__net_volume_flow__vwap_close_divergence_trend`** (Lock IC=+0.0864, Sharpe=+0.4303)
- Admission: Train IC=+0.2026, Deflated=+0.2039, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.124 | 2016: +0.039 | 2017: +0.187 | 2018: +0.124 | 2019: +0.089 | 2020: +0.105 | 2021: +0.085 | 2022: +0.090 | 2023: +0.103 | 2024: +0.102 | 2025: +0.140 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.166 | 2016: +0.052 | 2017: +0.153 | 2018: +0.184 | 2019: +0.299 | 2020: +0.187 | 2021: +0.213 | 2022: +0.176 | 2023: +0.302 | 2024: +0.139 | 2025: +0.118 | 2026: -0.206
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=1.07
- Early IC=+0.0815, Recent IC=+0.0874, 1st-half IC=+0.1261, 2nd-half IC=+0.0966, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.155, Q2=-0.010, Q3_mid=+0.167, Q4=+0.120, Q5_high_vol=+0.103

**`combo_min__first_bar_return__close_vs_open_range`** (Lock IC=+0.0979, Sharpe=+0.4302)
- Admission: Train IC=+0.2276, Deflated=+0.2295, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.085 | 2017: +0.185 | 2018: +0.172 | 2019: +0.117 | 2020: +0.065 | 2021: +0.057 | 2022: +0.046 | 2023: +0.070 | 2024: +0.131 | 2025: +0.140 | 2026: +0.011
- Yearly Tail ICs:   2015: +0.431 | 2016: +0.142 | 2017: +0.273 | 2018: +0.295 | 2019: +0.186 | 2020: +0.080 | 2021: +0.270 | 2022: +0.195 | 2023: +0.133 | 2024: +0.219 | 2025: +0.193 | 2026: +0.292
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.45, Recency ratio=0.36
- Early IC=+0.1445, Recent IC=+0.0515, 1st-half IC=+0.1659, 2nd-half IC=+0.0739, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.054, Q3_mid=+0.140, Q4=+0.139, Q5_high_vol=+0.153

**`combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0889, Sharpe=+0.4280)
- Admission: Train IC=+0.2581, Deflated=+0.2597, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.047 | 2017: +0.227 | 2018: +0.182 | 2019: +0.097 | 2020: +0.158 | 2021: +0.084 | 2022: +0.120 | 2023: +0.120 | 2024: +0.111 | 2025: +0.101 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.383 | 2016: +0.089 | 2017: +0.250 | 2018: +0.248 | 2019: +0.163 | 2020: +0.274 | 2021: +0.185 | 2022: +0.244 | 2023: +0.334 | 2024: +0.276 | 2025: +0.032 | 2026: -0.115
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.81
- Early IC=+0.1256, Recent IC=+0.1020, 1st-half IC=+0.1680, 2nd-half IC=+0.1208, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.035, Q3_mid=+0.189, Q4=+0.143, Q5_high_vol=+0.167

**`combo_rank_min__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0829, Sharpe=+0.4277)
- Admission: Train IC=+0.2390, Deflated=+0.2404, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.045 | 2017: +0.156 | 2018: +0.171 | 2019: +0.101 | 2020: +0.037 | 2021: +0.062 | 2022: +0.066 | 2023: +0.062 | 2024: +0.112 | 2025: +0.116 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.006 | 2017: +0.316 | 2018: +0.395 | 2019: +0.113 | 2020: +0.057 | 2021: +0.252 | 2022: +0.293 | 2023: -0.003 | 2024: +0.322 | 2025: +0.094 | 2026: +0.158
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.47, Recency ratio=0.59
- Early IC=+0.1075, Recent IC=+0.0638, 1st-half IC=+0.1442, 2nd-half IC=+0.0677, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.063, Q3_mid=+0.126, Q4=+0.137, Q5_high_vol=+0.119

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1089, Sharpe=+0.4243)
- Admission: Train IC=+0.2746, Deflated=+0.2765, IR=0.84, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.306 | 2016: +0.094 | 2017: +0.247 | 2018: +0.229 | 2019: +0.154 | 2020: +0.192 | 2021: +0.120 | 2022: +0.078 | 2023: +0.087 | 2024: +0.127 | 2025: +0.118 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.030 | 2017: +0.188 | 2018: +0.368 | 2019: +0.303 | 2020: +0.217 | 2021: +0.308 | 2022: +0.117 | 2023: +0.048 | 2024: +0.158 | 2025: +0.092 | 2026: +0.157
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.50
- Early IC=+0.2001, Recent IC=+0.0990, 1st-half IC=+0.2410, 2nd-half IC=+0.1402, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.026, Q3_mid=+0.185, Q4=+0.205, Q5_high_vol=+0.248

**`combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0841, Sharpe=+0.4215)
- Admission: Train IC=+0.2398, Deflated=+0.2409, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.075 | 2017: +0.195 | 2018: +0.209 | 2019: +0.087 | 2020: +0.114 | 2021: +0.106 | 2022: +0.104 | 2023: +0.101 | 2024: +0.127 | 2025: +0.110 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.290 | 2016: +0.122 | 2017: +0.292 | 2018: +0.386 | 2019: +0.111 | 2020: +0.179 | 2021: +0.185 | 2022: +0.175 | 2023: +0.300 | 2024: +0.245 | 2025: -0.057 | 2026: -0.267
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.73
- Early IC=+0.1450, Recent IC=+0.1051, 1st-half IC=+0.1966, 2nd-half IC=+0.1055, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.001, Q3_mid=+0.166, Q4=+0.161, Q5_high_vol=+0.198

**`combo_rank_max__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1051, Sharpe=+0.4203)
- Admission: Train IC=+0.1798, Deflated=+0.1805, IR=0.53, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.068 | 2017: +0.194 | 2018: +0.126 | 2019: +0.122 | 2020: +0.097 | 2021: +0.015 | 2022: +0.143 | 2023: +0.065 | 2024: +0.111 | 2025: +0.106 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.194 | 2017: +0.158 | 2018: +0.069 | 2019: +0.328 | 2020: +0.085 | 2021: +0.148 | 2022: +0.263 | 2023: +0.060 | 2024: +0.229 | 2025: -0.056 | 2026: -0.138
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.44
- Early IC=+0.1765, Recent IC=+0.0781, 1st-half IC=+0.1869, 2nd-half IC=+0.0963, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.009, Q3_mid=+0.173, Q4=+0.102, Q5_high_vol=+0.199

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1249, Sharpe=+0.4168)
- Admission: Train IC=+0.2528, Deflated=+0.2542, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.066 | 2017: +0.250 | 2018: +0.157 | 2019: +0.142 | 2020: +0.165 | 2021: +0.097 | 2022: +0.094 | 2023: +0.125 | 2024: +0.131 | 2025: +0.138 | 2026: +0.052
- Yearly Tail ICs:   2015: +0.426 | 2016: +0.145 | 2017: +0.187 | 2018: +0.111 | 2019: +0.340 | 2020: +0.103 | 2021: +0.179 | 2022: +0.408 | 2023: +0.108 | 2024: +0.284 | 2025: +0.202 | 2026: -0.049
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.54
- Early IC=+0.1771, Recent IC=+0.0955, 1st-half IC=+0.2064, 2nd-half IC=+0.1306, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.055, Q3_mid=+0.170, Q4=+0.171, Q5_high_vol=+0.235

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0933, Sharpe=+0.4158)
- Admission: Train IC=+0.2203, Deflated=+0.2218, IR=0.56, Mono=0.68, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.035 | 2017: +0.230 | 2018: +0.096 | 2019: +0.111 | 2020: +0.112 | 2021: +0.045 | 2022: +0.060 | 2023: +0.040 | 2024: +0.101 | 2025: +0.097 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.151 | 2017: +0.179 | 2018: +0.256 | 2019: +0.332 | 2020: +0.234 | 2021: +0.139 | 2022: +0.074 | 2023: +0.017 | 2024: +0.244 | 2025: -0.028 | 2026: +0.271
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.31
- Early IC=+0.1684, Recent IC=+0.0525, 1st-half IC=+0.1828, 2nd-half IC=+0.0843, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.002, Q3_mid=+0.135, Q4=+0.142, Q5_high_vol=+0.178

**`combo_max__max_up_ret__max_down_ret`** (Lock IC=+0.0820, Sharpe=+0.4153)
- Admission: Train IC=+0.2458, Deflated=+0.2482, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.080 | 2017: +0.244 | 2018: +0.245 | 2019: +0.121 | 2020: +0.139 | 2021: +0.099 | 2022: +0.078 | 2023: +0.051 | 2024: +0.139 | 2025: +0.096 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.265 | 2016: +0.236 | 2017: +0.269 | 2018: +0.394 | 2019: +0.149 | 2020: +0.134 | 2021: +0.326 | 2022: +0.128 | 2023: +0.185 | 2024: +0.277 | 2025: -0.102 | 2026: -0.309
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.53
- Early IC=+0.1662, Recent IC=+0.0889, 1st-half IC=+0.2201, 2nd-half IC=+0.1144, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.007, Q3_mid=+0.181, Q4=+0.170, Q5_high_vol=+0.240

**`combo_sig_product__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0697, Sharpe=+0.4152)
- Admission: Train IC=+0.1458, Deflated=+0.1476, IR=0.57, Mono=0.68, p=0.0042, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.126 | 2017: +0.086 | 2018: +0.120 | 2019: +0.091 | 2020: +0.090 | 2021: +0.126 | 2022: +0.116 | 2023: +0.148 | 2024: +0.080 | 2025: +0.116 | 2026: -0.103
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.196 | 2017: +0.101 | 2018: +0.144 | 2019: +0.193 | 2020: +0.107 | 2021: +0.263 | 2022: +0.161 | 2023: +0.309 | 2024: +0.283 | 2025: +0.238 | 2026: -0.269
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.80
- Early IC=+0.1504, Recent IC=+0.1210, 1st-half IC=+0.1217, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.044, Q3_mid=+0.120, Q4=+0.075, Q5_high_vol=+0.138

**`combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0852, Sharpe=+0.4144)
- Admission: Train IC=+0.1742, Deflated=+0.1745, IR=0.45, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.056 | 2017: +0.156 | 2018: +0.111 | 2019: +0.086 | 2020: +0.082 | 2021: +0.012 | 2022: +0.098 | 2023: +0.086 | 2024: +0.056 | 2025: +0.101 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.041 | 2016: +0.169 | 2017: +0.092 | 2018: +0.065 | 2019: +0.259 | 2020: +0.097 | 2021: +0.079 | 2022: +0.107 | 2023: -0.077 | 2024: +0.071 | 2025: +0.044 | 2026: +0.043
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.39, Recency ratio=0.35
- Early IC=+0.1516, Recent IC=+0.0536, 1st-half IC=+0.1750, 2nd-half IC=+0.0675, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.012, Q3_mid=+0.126, Q4=+0.133, Q5_high_vol=+0.166

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0913, Sharpe=+0.4100)
- Admission: Train IC=+0.2530, Deflated=+0.2544, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.094 | 2017: +0.235 | 2018: +0.223 | 2019: +0.107 | 2020: +0.153 | 2021: +0.154 | 2022: +0.123 | 2023: +0.098 | 2024: +0.145 | 2025: +0.078 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.103 | 2017: +0.148 | 2018: +0.362 | 2019: +0.318 | 2020: +0.098 | 2021: +0.316 | 2022: +0.211 | 2023: -0.005 | 2024: +0.273 | 2025: +0.022 | 2026: -0.232
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.77
- Early IC=+0.1813, Recent IC=+0.1394, 1st-half IC=+0.2254, 2nd-half IC=+0.1380, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.049, Q3_mid=+0.190, Q4=+0.198, Q5_high_vol=+0.243

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0869, Sharpe=+0.4098)
- Admission: Train IC=+0.2498, Deflated=+0.2510, IR=1.02, Mono=0.79, p=0.0000, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.106 | 2017: +0.192 | 2018: +0.211 | 2019: +0.154 | 2020: +0.164 | 2021: +0.138 | 2022: +0.066 | 2023: +0.093 | 2024: +0.100 | 2025: +0.041 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.155 | 2017: +0.360 | 2018: +0.371 | 2019: +0.377 | 2020: +0.144 | 2021: +0.251 | 2022: +0.138 | 2023: +0.186 | 2024: -0.019 | 2025: -0.020 | 2026: +0.060
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.51
- Early IC=+0.2010, Recent IC=+0.1019, 1st-half IC=+0.2177, 2nd-half IC=+0.1328, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.022, Q3_mid=+0.179, Q4=+0.166, Q5_high_vol=+0.281

**`combo_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.1011, Sharpe=+0.4084)
- Admission: Train IC=+0.2377, Deflated=+0.2385, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.086 | 2017: +0.183 | 2018: +0.126 | 2019: +0.074 | 2020: +0.109 | 2021: +0.128 | 2022: +0.091 | 2023: +0.101 | 2024: +0.147 | 2025: +0.151 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.275 | 2017: +0.302 | 2018: +0.295 | 2019: +0.090 | 2020: +0.101 | 2021: +0.226 | 2022: +0.076 | 2023: +0.172 | 2024: +0.249 | 2025: +0.107 | 2026: -0.057
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.78
- Early IC=+0.1405, Recent IC=+0.1097, 1st-half IC=+0.1590, 2nd-half IC=+0.1002, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.033, Q3_mid=+0.167, Q4=+0.139, Q5_high_vol=+0.133

**`combo_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0840, Sharpe=+0.4024)
- Admission: Train IC=+0.2080, Deflated=+0.2090, IR=0.61, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.105 | 2017: +0.197 | 2018: +0.165 | 2019: +0.100 | 2020: +0.131 | 2021: +0.086 | 2022: +0.125 | 2023: +0.121 | 2024: +0.127 | 2025: +0.090 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.272 | 2016: +0.160 | 2017: +0.156 | 2018: +0.306 | 2019: +0.207 | 2020: +0.096 | 2021: +0.230 | 2022: +0.100 | 2023: +0.412 | 2024: +0.208 | 2025: -0.168 | 2026: -0.504
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.68
- Early IC=+0.1557, Recent IC=+0.1057, 1st-half IC=+0.1874, 2nd-half IC=+0.1192, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.071, Q3_mid=+0.159, Q4=+0.129, Q5_high_vol=+0.209

**`combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.1086, Sharpe=+0.4017)
- Admission: Train IC=+0.2652, Deflated=+0.2672, IR=0.80, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.091 | 2017: +0.231 | 2018: +0.204 | 2019: +0.112 | 2020: +0.157 | 2021: +0.107 | 2022: +0.063 | 2023: +0.127 | 2024: +0.140 | 2025: +0.119 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.468 | 2016: +0.080 | 2017: +0.246 | 2018: +0.370 | 2019: +0.210 | 2020: +0.212 | 2021: +0.286 | 2022: +0.275 | 2023: +0.259 | 2024: +0.191 | 2025: -0.025 | 2026: -0.272
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.51
- Early IC=+0.1666, Recent IC=+0.0854, 1st-half IC=+0.2019, 2nd-half IC=+0.1135, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.030, Q3_mid=+0.189, Q4=+0.154, Q5_high_vol=+0.201

**`combo_min__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0695, Sharpe=+0.4002)
- Admission: Train IC=+0.2305, Deflated=+0.2328, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.007 | 2017: +0.153 | 2018: +0.121 | 2019: +0.128 | 2020: +0.085 | 2021: +0.124 | 2022: +0.156 | 2023: +0.077 | 2024: +0.112 | 2025: +0.078 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.315 | 2016: -0.040 | 2017: +0.209 | 2018: +0.239 | 2019: +0.244 | 2020: +0.159 | 2021: +0.306 | 2022: +0.303 | 2023: +0.135 | 2024: +0.331 | 2025: +0.134 | 2026: +0.039
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.14, Recency ratio=1.30
- Early IC=+0.1082, Recent IC=+0.1401, 1st-half IC=+0.1110, 2nd-half IC=+0.1261, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.131, Q2=-0.011, Q3_mid=+0.140, Q4=+0.152, Q5_high_vol=+0.152

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1050, Sharpe=+0.3978)
- Admission: Train IC=+0.2845, Deflated=+0.2863, IR=1.01, Mono=0.84, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.101 | 2017: +0.207 | 2018: +0.219 | 2019: +0.145 | 2020: +0.153 | 2021: +0.125 | 2022: +0.060 | 2023: +0.119 | 2024: +0.154 | 2025: +0.097 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.506 | 2016: +0.310 | 2017: +0.348 | 2018: +0.390 | 2019: +0.189 | 2020: +0.200 | 2021: +0.284 | 2022: +0.135 | 2023: +0.224 | 2024: +0.212 | 2025: -0.134 | 2026: -0.155
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.51
- Early IC=+0.1818, Recent IC=+0.0926, 1st-half IC=+0.2108, 2nd-half IC=+0.1262, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.052, Q3_mid=+0.189, Q4=+0.149, Q5_high_vol=+0.246

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0792, Sharpe=+0.3953)
- Admission: Train IC=+0.1690, Deflated=+0.1706, IR=0.53, Mono=0.72, p=0.0002, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.115 | 2017: +0.109 | 2018: +0.281 | 2019: +0.096 | 2020: +0.130 | 2021: +0.101 | 2022: +0.112 | 2023: +0.050 | 2024: +0.098 | 2025: +0.104 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.105 | 2017: +0.327 | 2018: +0.466 | 2019: +0.109 | 2020: +0.215 | 2021: +0.190 | 2022: +0.000 | 2023: +0.090 | 2024: +0.175 | 2025: +0.153 | 2026: -0.308
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.66
- Early IC=+0.1609, Recent IC=+0.1064, 1st-half IC=+0.2118, 2nd-half IC=+0.1108, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.016, Q3_mid=+0.146, Q4=+0.171, Q5_high_vol=+0.207

**`combo_ratio__bar_ret_0__net_volume_flow`** (Lock IC=+0.0500, Sharpe=+0.3938)
- Admission: Train IC=+0.1425, Deflated=+0.1442, IR=0.33, Mono=0.65, p=0.0062, MaxCorr=0.10
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.055 | 2017: +0.106 | 2018: +0.193 | 2019: +0.120 | 2020: +0.060 | 2021: +0.138 | 2022: +0.020 | 2023: +0.008 | 2024: +0.061 | 2025: +0.089 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.334 | 2016: -0.088 | 2017: +0.096 | 2018: +0.173 | 2019: +0.045 | 2020: +0.132 | 2021: +0.368 | 2022: +0.124 | 2023: -0.017 | 2024: +0.020 | 2025: +0.104 | 2026: +0.197
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.67
- Early IC=+0.1174, Recent IC=+0.0790, 1st-half IC=+0.1435, 2nd-half IC=+0.0766, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.142, Q2=-0.024, Q3_mid=+0.099, Q4=+0.126, Q5_high_vol=+0.142

**`combo_mean__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0911, Sharpe=+0.3935)
- Admission: Train IC=+0.2389, Deflated=+0.2406, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.064 | 2017: +0.180 | 2018: +0.138 | 2019: +0.072 | 2020: +0.113 | 2021: +0.077 | 2022: +0.101 | 2023: +0.088 | 2024: +0.133 | 2025: +0.139 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.336 | 2016: +0.107 | 2017: +0.289 | 2018: +0.194 | 2019: +0.157 | 2020: +0.229 | 2021: +0.282 | 2022: +0.164 | 2023: +0.227 | 2024: +0.273 | 2025: +0.016 | 2026: -0.030
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.76
- Early IC=+0.1164, Recent IC=+0.0888, 1st-half IC=+0.1434, 2nd-half IC=+0.0944, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.177, Q2=-0.015, Q3_mid=+0.167, Q4=+0.125, Q5_high_vol=+0.126

**`combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0`** (Lock IC=+0.0649, Sharpe=+0.3923)
- Admission: Train IC=+0.1806, Deflated=+0.1816, IR=0.51, Mono=0.67, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.120 | 2017: +0.155 | 2018: +0.196 | 2019: +0.064 | 2020: +0.109 | 2021: +0.093 | 2022: +0.099 | 2023: +0.072 | 2024: +0.080 | 2025: +0.119 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.106 | 2017: +0.244 | 2018: +0.280 | 2019: +0.128 | 2020: +0.281 | 2021: +0.192 | 2022: +0.070 | 2023: +0.118 | 2024: +0.211 | 2025: +0.215 | 2026: -0.333
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.60
- Early IC=+0.1596, Recent IC=+0.0959, 1st-half IC=+0.1867, 2nd-half IC=+0.0947, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.005, Q3_mid=+0.142, Q4=+0.173, Q5_high_vol=+0.172

**`combo_rank_min__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0950, Sharpe=+0.3896)
- Admission: Train IC=+0.2649, Deflated=+0.2672, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.059 | 2017: +0.180 | 2018: +0.205 | 2019: +0.121 | 2020: +0.137 | 2021: +0.134 | 2022: +0.082 | 2023: +0.118 | 2024: +0.134 | 2025: +0.108 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.399 | 2016: +0.158 | 2017: +0.169 | 2018: +0.256 | 2019: +0.282 | 2020: +0.186 | 2021: +0.309 | 2022: +0.250 | 2023: +0.127 | 2024: +0.245 | 2025: +0.015 | 2026: +0.031
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.85
- Early IC=+0.1269, Recent IC=+0.1085, 1st-half IC=+0.1685, 2nd-half IC=+0.1240, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.012, Q3_mid=+0.191, Q4=+0.139, Q5_high_vol=+0.176

**`combo_max__first_bar_return__max_down_ret`** (Lock IC=+0.0789, Sharpe=+0.3856)
- Admission: Train IC=+0.2082, Deflated=+0.2102, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.098 | 2017: +0.261 | 2018: +0.231 | 2019: +0.144 | 2020: +0.130 | 2021: +0.079 | 2022: +0.087 | 2023: +0.044 | 2024: +0.128 | 2025: +0.102 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.006 | 2017: +0.195 | 2018: +0.423 | 2019: +0.116 | 2020: +0.219 | 2021: +0.191 | 2022: +0.201 | 2023: +0.203 | 2024: +0.225 | 2025: +0.034 | 2026: -0.223
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.55, Recency ratio=0.51
- Early IC=+0.1618, Recent IC=+0.0828, 1st-half IC=+0.2080, 2nd-half IC=+0.1143, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.006, Q3_mid=+0.153, Q4=+0.157, Q5_high_vol=+0.202

**`combo_rank_min__close_vs_open_range__vwap_close_divergence_trend`** (Lock IC=+0.0881, Sharpe=+0.3843)
- Admission: Train IC=+0.2211, Deflated=+0.2220, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.056 | 2017: +0.188 | 2018: +0.086 | 2019: +0.073 | 2020: +0.092 | 2021: +0.068 | 2022: +0.093 | 2023: +0.112 | 2024: +0.115 | 2025: +0.148 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.265 | 2016: +0.164 | 2017: +0.279 | 2018: +0.201 | 2019: +0.249 | 2020: +0.111 | 2021: +0.314 | 2022: +0.117 | 2023: +0.240 | 2024: +0.171 | 2025: +0.140 | 2026: -0.257
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.73
- Early IC=+0.1111, Recent IC=+0.0808, 1st-half IC=+0.1295, 2nd-half IC=+0.0901, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.025, Q3_mid=+0.144, Q4=+0.120, Q5_high_vol=+0.097

**`combo_rank_min__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0873, Sharpe=+0.3829)
- Admission: Train IC=+0.2443, Deflated=+0.2460, IR=0.63, Mono=0.74, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.069 | 2017: +0.241 | 2018: +0.095 | 2019: +0.122 | 2020: +0.124 | 2021: +0.038 | 2022: +0.090 | 2023: +0.074 | 2024: +0.114 | 2025: +0.102 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.318 | 2016: +0.073 | 2017: +0.320 | 2018: +0.161 | 2019: +0.238 | 2020: +0.140 | 2021: +0.362 | 2022: +0.359 | 2023: +0.079 | 2024: +0.088 | 2025: +0.236 | 2026: -0.234
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.38
- Early IC=+0.1662, Recent IC=+0.0628, 1st-half IC=+0.1539, 2nd-half IC=+0.1009, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.159, Q2=-0.013, Q3_mid=+0.168, Q4=+0.118, Q5_high_vol=+0.172

**`combo_max__max_down_ret__close_vs_open_range`** (Lock IC=+0.0831, Sharpe=+0.3714)
- Admission: Train IC=+0.1777, Deflated=+0.1790, IR=0.42, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.059 | 2017: +0.217 | 2018: +0.133 | 2019: +0.094 | 2020: +0.130 | 2021: +0.086 | 2022: +0.061 | 2023: +0.043 | 2024: +0.127 | 2025: +0.149 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.092 | 2017: +0.262 | 2018: +0.031 | 2019: +0.211 | 2020: +0.018 | 2021: +0.273 | 2022: +0.213 | 2023: +0.180 | 2024: +0.332 | 2025: +0.017 | 2026: -0.043
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.47
- Early IC=+0.1552, Recent IC=+0.0735, 1st-half IC=+0.1599, 2nd-half IC=+0.0973, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.002, Q3_mid=+0.155, Q4=+0.120, Q5_high_vol=+0.152

**`combo_mean__first_bar_return__close_vs_open_range`** (Lock IC=+0.0936, Sharpe=+0.3680)
- Admission: Train IC=+0.2132, Deflated=+0.2150, IR=0.73, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.100 | 2017: +0.214 | 2018: +0.204 | 2019: +0.109 | 2020: +0.114 | 2021: +0.101 | 2022: +0.096 | 2023: +0.081 | 2024: +0.151 | 2025: +0.114 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.038 | 2017: +0.265 | 2018: +0.360 | 2019: +0.141 | 2020: +0.172 | 2021: +0.369 | 2022: +0.259 | 2023: +0.232 | 2024: +0.311 | 2025: +0.015 | 2026: -0.244
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.60
- Early IC=+0.1649, Recent IC=+0.0986, 1st-half IC=+0.1983, 2nd-half IC=+0.1082, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.005, Q3_mid=+0.155, Q4=+0.157, Q5_high_vol=+0.187

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.1034, Sharpe=+0.3676)
- Admission: Train IC=+0.2923, Deflated=+0.2933, IR=0.80, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.139 | 2017: +0.218 | 2018: +0.251 | 2019: +0.141 | 2020: +0.163 | 2021: +0.124 | 2022: +0.103 | 2023: +0.083 | 2024: +0.116 | 2025: +0.106 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.327 | 2016: +0.209 | 2017: +0.169 | 2018: +0.455 | 2019: +0.178 | 2020: +0.249 | 2021: +0.233 | 2022: +0.122 | 2023: +0.048 | 2024: +0.103 | 2025: +0.047 | 2026: +0.120
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.52
- Early IC=+0.2178, Recent IC=+0.1136, 1st-half IC=+0.2511, 2nd-half IC=+0.1337, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.022, Q3_mid=+0.171, Q4=+0.215, Q5_high_vol=+0.273

**`combo_rank_max__trend_bar_close_consistency__star50_limit_proximity_early`** (Lock IC=+0.0839, Sharpe=+0.3605)
- Admission: Train IC=+0.1931, Deflated=+0.1932, IR=0.51, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.049 | 2017: +0.152 | 2018: +0.118 | 2019: +0.074 | 2020: +0.101 | 2021: +0.010 | 2022: +0.146 | 2023: +0.084 | 2024: +0.086 | 2025: +0.097 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.060 | 2016: +0.200 | 2017: +0.146 | 2018: +0.101 | 2019: +0.241 | 2020: +0.119 | 2021: +0.106 | 2022: +0.179 | 2023: +0.111 | 2024: +0.153 | 2025: -0.004 | 2026: -0.210
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.50
- Early IC=+0.1532, Recent IC=+0.0765, 1st-half IC=+0.1738, 2nd-half IC=+0.0845, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.002, Q3_mid=+0.162, Q4=+0.113, Q5_high_vol=+0.179

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__early_body_momentum`** (Lock IC=+0.0960, Sharpe=+0.3514)
- Admission: Train IC=+0.2732, Deflated=+0.2749, IR=1.06, Mono=0.86, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.086 | 2017: +0.211 | 2018: +0.196 | 2019: +0.107 | 2020: +0.150 | 2021: +0.121 | 2022: +0.105 | 2023: +0.110 | 2024: +0.149 | 2025: +0.107 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.386 | 2016: +0.294 | 2017: +0.294 | 2018: +0.325 | 2019: +0.184 | 2020: +0.239 | 2021: +0.260 | 2022: +0.236 | 2023: +0.274 | 2024: +0.240 | 2025: -0.079 | 2026: -0.244
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.72
- Early IC=+0.1577, Recent IC=+0.1131, 1st-half IC=+0.2015, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.028, Q3_mid=+0.198, Q4=+0.159, Q5_high_vol=+0.207

**`combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1220, Sharpe=+0.3484)
- Admission: Train IC=+0.2005, Deflated=+0.2014, IR=0.60, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.058 | 2017: +0.239 | 2018: +0.098 | 2019: +0.125 | 2020: +0.108 | 2021: +0.035 | 2022: +0.087 | 2023: +0.101 | 2024: +0.108 | 2025: +0.107 | 2026: +0.166
- Yearly Tail ICs:   2015: +0.183 | 2016: +0.117 | 2017: +0.156 | 2018: +0.266 | 2019: +0.205 | 2020: +0.162 | 2021: +0.025 | 2022: +0.041 | 2023: -0.064 | 2024: +0.137 | 2025: -0.008 | 2026: +0.322
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.38
- Early IC=+0.1622, Recent IC=+0.0613, 1st-half IC=+0.1896, 2nd-half IC=+0.0951, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.038, Q3_mid=+0.127, Q4=+0.145, Q5_high_vol=+0.168

**`combo_rank_max__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0836, Sharpe=+0.3480)
- Admission: Train IC=+0.1580, Deflated=+0.1594, IR=0.55, Mono=0.70, p=0.0014, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.027 | 2017: +0.203 | 2018: +0.128 | 2019: +0.107 | 2020: +0.095 | 2021: +0.106 | 2022: +0.058 | 2023: +0.074 | 2024: +0.109 | 2025: +0.179 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.197 | 2016: +0.001 | 2017: +0.242 | 2018: +0.063 | 2019: +0.276 | 2020: +0.095 | 2021: +0.300 | 2022: +0.202 | 2023: +0.159 | 2024: +0.176 | 2025: +0.363 | 2026: -0.039
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.79
- Early IC=+0.1032, Recent IC=+0.0820, 1st-half IC=+0.1441, 2nd-half IC=+0.0946, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.026, Q3_mid=+0.165, Q4=+0.096, Q5_high_vol=+0.119

**`combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.0972, Sharpe=+0.3472)
- Admission: Train IC=+0.2246, Deflated=+0.2252, IR=0.77, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.068 | 2017: +0.261 | 2018: +0.097 | 2019: +0.119 | 2020: +0.106 | 2021: +0.117 | 2022: +0.038 | 2023: +0.082 | 2024: +0.103 | 2025: +0.105 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.157 | 2017: +0.294 | 2018: +0.388 | 2019: +0.249 | 2020: +0.130 | 2021: +0.347 | 2022: +0.070 | 2023: +0.147 | 2024: +0.134 | 2025: +0.106 | 2026: -0.122
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.60
- Early IC=+0.1277, Recent IC=+0.0769, 1st-half IC=+0.1585, 2nd-half IC=+0.1017, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.052, Q3_mid=+0.123, Q4=+0.204, Q5_high_vol=+0.102

**`combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`** (Lock IC=+0.1035, Sharpe=+0.3387)
- Admission: Train IC=+0.1767, Deflated=+0.1771, IR=0.44, Mono=0.67, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.096 | 2017: +0.168 | 2018: +0.116 | 2019: +0.128 | 2020: +0.121 | 2021: +0.025 | 2022: +0.141 | 2023: +0.098 | 2024: +0.092 | 2025: +0.137 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.040 | 2016: +0.174 | 2017: +0.071 | 2018: +0.210 | 2019: +0.198 | 2020: +0.116 | 2021: +0.040 | 2022: +0.119 | 2023: +0.133 | 2024: +0.068 | 2025: +0.002 | 2026: -0.090
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.54
- Early IC=+0.1531, Recent IC=+0.0831, 1st-half IC=+0.1773, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.055, Q3_mid=+0.167, Q4=+0.077, Q5_high_vol=+0.204

**`combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0977, Sharpe=+0.3369)
- Admission: Train IC=+0.2387, Deflated=+0.2404, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.178 | 2017: +0.159 | 2018: +0.154 | 2019: +0.112 | 2020: +0.134 | 2021: +0.085 | 2022: +0.094 | 2023: +0.034 | 2024: +0.105 | 2025: +0.081 | 2026: +0.148
- Yearly Tail ICs:   2015: +0.147 | 2016: +0.381 | 2017: +0.162 | 2018: +0.192 | 2019: +0.181 | 2020: +0.062 | 2021: +0.167 | 2022: +0.034 | 2023: -0.143 | 2024: +0.042 | 2025: -0.043 | 2026: +0.365
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.45
- Early IC=+0.1997, Recent IC=+0.0895, 1st-half IC=+0.1991, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.007, Q3_mid=+0.126, Q4=+0.154, Q5_high_vol=+0.241

**`combo_mean__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0886, Sharpe=+0.3333)
- Admission: Train IC=+0.2236, Deflated=+0.2251, IR=0.52, Mono=0.67, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.083 | 2017: +0.217 | 2018: +0.201 | 2019: +0.110 | 2020: +0.112 | 2021: +0.092 | 2022: +0.095 | 2023: +0.080 | 2024: +0.141 | 2025: +0.117 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.286 | 2016: -0.015 | 2017: +0.177 | 2018: +0.356 | 2019: +0.217 | 2020: +0.212 | 2021: +0.158 | 2022: +0.309 | 2023: +0.234 | 2024: +0.245 | 2025: +0.149 | 2026: -0.289
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.57, Recency ratio=0.66
- Early IC=+0.1415, Recent IC=+0.0933, 1st-half IC=+0.1860, 2nd-half IC=+0.1054, Neg regimes=1/5
- Weak component: `trend_day_regime_conviction` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.002, Q3_mid=+0.147, Q4=+0.153, Q5_high_vol=+0.170

**`combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1246, Sharpe=+0.3320)
- Admission: Train IC=+0.1994, Deflated=+0.2002, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.061 | 2017: +0.241 | 2018: +0.100 | 2019: +0.124 | 2020: +0.106 | 2021: +0.032 | 2022: +0.084 | 2023: +0.102 | 2024: +0.105 | 2025: +0.116 | 2026: +0.169
- Yearly Tail ICs:   2015: +0.189 | 2016: +0.119 | 2017: +0.161 | 2018: +0.263 | 2019: +0.200 | 2020: +0.164 | 2021: +0.017 | 2022: +0.042 | 2023: -0.057 | 2024: +0.135 | 2025: -0.008 | 2026: +0.311
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.35
- Early IC=+0.1629, Recent IC=+0.0577, 1st-half IC=+0.1894, 2nd-half IC=+0.0927, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.038, Q3_mid=+0.128, Q4=+0.145, Q5_high_vol=+0.165

**`combo_rel_diff__bar_ret_0__late_bar_momentum`** (Lock IC=+0.0672, Sharpe=+0.3283)
- Admission: Train IC=+0.1758, Deflated=+0.1776, IR=0.45, Mono=0.66, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.312 | 2016: +0.059 | 2017: +0.160 | 2018: +0.226 | 2019: +0.178 | 2020: +0.091 | 2021: +0.122 | 2022: +0.030 | 2023: +0.068 | 2024: +0.088 | 2025: +0.020 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.294 | 2016: -0.088 | 2017: +0.409 | 2018: +0.319 | 2019: +0.103 | 2020: +0.188 | 2021: +0.125 | 2022: +0.037 | 2023: +0.225 | 2024: +0.122 | 2025: -0.016 | 2026: +0.020
- IC CV=0.59, Neg years (linear/tail)=0/1 of 8, Half ratio=0.52, Recency ratio=0.41
- Early IC=+0.1856, Recent IC=+0.0758, 1st-half IC=+0.1955, 2nd-half IC=+0.1021, Neg regimes=1/5
- Weak component: `late_bar_momentum` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.128, Q2=-0.004, Q3_mid=+0.149, Q4=+0.164, Q5_high_vol=+0.248

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0977, Sharpe=+0.3280)
- Admission: Train IC=+0.2509, Deflated=+0.2526, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.097 | 2017: +0.234 | 2018: +0.253 | 2019: +0.147 | 2020: +0.150 | 2021: +0.143 | 2022: +0.094 | 2023: +0.098 | 2024: +0.162 | 2025: +0.087 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.121 | 2017: +0.264 | 2018: +0.450 | 2019: +0.130 | 2020: +0.189 | 2021: +0.338 | 2022: +0.118 | 2023: +0.159 | 2024: +0.186 | 2025: -0.015 | 2026: -0.214
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.64
- Early IC=+0.1843, Recent IC=+0.1184, 1st-half IC=+0.2380, 2nd-half IC=+0.1366, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.036, Q3_mid=+0.191, Q4=+0.185, Q5_high_vol=+0.259

**`combo_rank_max__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0954, Sharpe=+0.3172)
- Admission: Train IC=+0.2301, Deflated=+0.2316, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.100 | 2017: +0.226 | 2018: +0.241 | 2019: +0.145 | 2020: +0.142 | 2021: +0.169 | 2022: +0.092 | 2023: +0.108 | 2024: +0.150 | 2025: +0.088 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.336 | 2016: -0.072 | 2017: +0.187 | 2018: +0.368 | 2019: +0.218 | 2020: +0.248 | 2021: +0.353 | 2022: +0.155 | 2023: +0.156 | 2024: +0.280 | 2025: -0.017 | 2026: -0.111
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.74
- Early IC=+0.1772, Recent IC=+0.1308, 1st-half IC=+0.2187, 2nd-half IC=+0.1409, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.040, Q3_mid=+0.175, Q4=+0.177, Q5_high_vol=+0.235

**`opening_drive_thrust_ratio`** (Lock IC=+0.0993, Sharpe=+0.3094)
- Admission: Train IC=+0.2632, Deflated=+0.2649, IR=0.79, Mono=0.81, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069 | 2023: +0.102 | 2024: +0.152 | 2025: +0.088 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.517 | 2016: +0.047 | 2017: +0.205 | 2018: +0.244 | 2019: +0.347 | 2020: +0.069 | 2021: +0.321 | 2022: +0.278 | 2023: +0.019 | 2024: +0.151 | 2025: +0.052 | 2026: -0.026
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.63
- Early IC=+0.1704, Recent IC=+0.1065, 1st-half IC=+0.2044, 2nd-half IC=+0.1359, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.048, Q3_mid=+0.189, Q4=+0.158, Q5_high_vol=+0.241

**`combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.0963, Sharpe=+0.3050)
- Admission: Train IC=+0.1956, Deflated=+0.1963, IR=0.43, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.100 | 2017: +0.219 | 2018: +0.157 | 2019: +0.102 | 2020: +0.162 | 2021: +0.068 | 2022: +0.117 | 2023: +0.053 | 2024: +0.108 | 2025: +0.088 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.169 | 2017: +0.160 | 2018: +0.158 | 2019: +0.168 | 2020: +0.055 | 2021: +0.136 | 2022: +0.225 | 2023: +0.101 | 2024: +0.020 | 2025: +0.021 | 2026: -0.117
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.47
- Early IC=+0.1984, Recent IC=+0.0925, 1st-half IC=+0.2203, 2nd-half IC=+0.1136, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.021, Q3_mid=+0.186, Q4=+0.132, Q5_high_vol=+0.252

**`combo_tri_median__early_body_momentum__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0809, Sharpe=+0.3003)
- Admission: Train IC=+0.2283, Deflated=+0.2297, IR=0.52, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.047 | 2017: +0.176 | 2018: +0.144 | 2019: +0.074 | 2020: +0.100 | 2021: +0.068 | 2022: +0.097 | 2023: +0.083 | 2024: +0.110 | 2025: +0.157 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.366 | 2016: +0.069 | 2017: +0.138 | 2018: +0.162 | 2019: +0.186 | 2020: +0.191 | 2021: +0.198 | 2022: +0.205 | 2023: +0.184 | 2024: +0.255 | 2025: +0.010 | 2026: -0.093
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.85
- Early IC=+0.0962, Recent IC=+0.0822, 1st-half IC=+0.1379, 2nd-half IC=+0.0894, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.006, Q3_mid=+0.161, Q4=+0.122, Q5_high_vol=+0.100

**`combo_rank_max__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0745, Sharpe=+0.2995)
- Admission: Train IC=+0.2277, Deflated=+0.2290, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: +0.120 | 2018: +0.212 | 2019: +0.098 | 2020: +0.108 | 2021: +0.098 | 2022: +0.134 | 2023: +0.084 | 2024: +0.119 | 2025: +0.086 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.227 | 2016: +0.111 | 2017: +0.112 | 2018: +0.398 | 2019: +0.159 | 2020: +0.173 | 2021: +0.334 | 2022: +0.222 | 2023: +0.247 | 2024: +0.297 | 2025: -0.024 | 2026: -0.267
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.77
- Early IC=+0.1469, Recent IC=+0.1125, 1st-half IC=+0.1787, 2nd-half IC=+0.1116, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.124, Q2=-0.013, Q3_mid=+0.181, Q4=+0.162, Q5_high_vol=+0.223

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.0951, Sharpe=+0.2989)
- Admission: Train IC=+0.2274, Deflated=+0.2283, IR=0.58, Mono=0.69, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.123 | 2017: +0.205 | 2018: +0.077 | 2019: +0.050 | 2020: +0.104 | 2021: -0.011 | 2022: +0.101 | 2023: +0.065 | 2024: +0.099 | 2025: +0.095 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.192 | 2016: +0.179 | 2017: +0.355 | 2018: +0.216 | 2019: +0.080 | 2020: +0.169 | 2021: +0.178 | 2022: +0.179 | 2023: +0.016 | 2024: +0.156 | 2025: +0.029 | 2026: +0.234
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=0.37, Recency ratio=0.29
- Early IC=+0.1536, Recent IC=+0.0449, 1st-half IC=+0.1710, 2nd-half IC=+0.0632, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.007, Q3_mid=+0.099, Q4=+0.152, Q5_high_vol=+0.125

**`combo_tri_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0904, Sharpe=+0.2926)
- Admission: Train IC=+0.2179, Deflated=+0.2189, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.141 | 2017: +0.196 | 2018: +0.189 | 2019: +0.090 | 2020: +0.136 | 2021: +0.086 | 2022: +0.114 | 2023: +0.057 | 2024: +0.108 | 2025: +0.086 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.170 | 2016: +0.198 | 2017: +0.234 | 2018: +0.336 | 2019: +0.092 | 2020: +0.079 | 2021: +0.342 | 2022: +0.228 | 2023: -0.000 | 2024: +0.038 | 2025: +0.060 | 2026: -0.023
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.53
- Early IC=+0.1898, Recent IC=+0.0998, 1st-half IC=+0.2180, 2nd-half IC=+0.1088, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.031, Q3_mid=+0.155, Q4=+0.140, Q5_high_vol=+0.240

**`combo_rank_min__early_order_flow_imbalance__close_vs_open_range`** (Lock IC=+0.0779, Sharpe=+0.2912)
- Admission: Train IC=+0.2009, Deflated=+0.2029, IR=0.49, Mono=0.68, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.030 | 2017: +0.161 | 2018: +0.116 | 2019: +0.100 | 2020: +0.051 | 2021: +0.105 | 2022: +0.103 | 2023: +0.109 | 2024: +0.134 | 2025: +0.102 | 2026: -0.115
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.147 | 2017: +0.307 | 2018: +0.232 | 2019: +0.279 | 2020: +0.065 | 2021: +0.250 | 2022: +0.127 | 2023: +0.188 | 2024: +0.271 | 2025: +0.016 | 2026: -0.160
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=1.49
- Early IC=+0.0690, Recent IC=+0.1026, 1st-half IC=+0.1087, 2nd-half IC=+0.0908, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.002, Q3_mid=+0.143, Q4=+0.121, Q5_high_vol=+0.067

**`combo_min__first_bar_return__max_down_ret`** (Lock IC=+0.0836, Sharpe=+0.2902)
- Admission: Train IC=+0.2016, Deflated=+0.2038, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.099 | 2017: +0.176 | 2018: +0.173 | 2019: +0.138 | 2020: +0.099 | 2021: +0.089 | 2022: +0.041 | 2023: +0.054 | 2024: +0.097 | 2025: +0.140 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.055 | 2017: +0.306 | 2018: +0.182 | 2019: +0.332 | 2020: +0.215 | 2021: +0.384 | 2022: +0.104 | 2023: +0.104 | 2024: +0.260 | 2025: +0.142 | 2026: +0.048
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.52, Recency ratio=0.35
- Early IC=+0.1879, Recent IC=+0.0648, 1st-half IC=+0.1784, 2nd-half IC=+0.0925, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.019, Q3_mid=+0.137, Q4=+0.120, Q5_high_vol=+0.208

**`combo_min__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0908, Sharpe=+0.2900)
- Admission: Train IC=+0.2406, Deflated=+0.2419, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.054 | 2017: +0.210 | 2018: +0.079 | 2019: +0.116 | 2020: +0.112 | 2021: +0.037 | 2022: +0.102 | 2023: +0.091 | 2024: +0.117 | 2025: +0.105 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.352 | 2016: +0.061 | 2017: +0.285 | 2018: +0.180 | 2019: +0.267 | 2020: +0.142 | 2021: +0.309 | 2022: +0.328 | 2023: +0.109 | 2024: +0.124 | 2025: +0.311 | 2026: -0.053
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.45
- Early IC=+0.1538, Recent IC=+0.0691, 1st-half IC=+0.1441, 2nd-half IC=+0.1008, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.005, Q3_mid=+0.155, Q4=+0.116, Q5_high_vol=+0.164

**`open_to_current_return`** (Lock IC=+0.0851, Sharpe=+0.2899)
- Admission: Train IC=+0.1557, Deflated=+0.1567, IR=0.48, Mono=0.70, p=0.0018, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.90
- Early IC=+0.0999, Recent IC=+0.0896, 1st-half IC=+0.1422, 2nd-half IC=+0.0903, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.019, Q3_mid=+0.156, Q4=+0.125, Q5_high_vol=+0.107

**`combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction`** (Lock IC=+0.0889, Sharpe=+0.2828)
- Admission: Train IC=+0.2347, Deflated=+0.2360, IR=0.61, Mono=0.78, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.070 | 2017: +0.252 | 2018: +0.144 | 2019: +0.124 | 2020: +0.132 | 2021: +0.082 | 2022: +0.094 | 2023: +0.067 | 2024: +0.146 | 2025: +0.099 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.423 | 2016: +0.123 | 2017: +0.218 | 2018: +0.122 | 2019: +0.399 | 2020: +0.110 | 2021: +0.013 | 2022: +0.305 | 2023: +0.179 | 2024: +0.187 | 2025: -0.071 | 2026: +0.081
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.54
- Early IC=+0.1689, Recent IC=+0.0912, 1st-half IC=+0.1952, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.034, Q3_mid=+0.175, Q4=+0.152, Q5_high_vol=+0.204

**`combo_rank_max__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0811, Sharpe=+0.2779)
- Admission: Train IC=+0.1987, Deflated=+0.2001, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.217 | 2016: -0.005 | 2017: +0.203 | 2018: +0.154 | 2019: +0.130 | 2020: +0.084 | 2021: +0.100 | 2022: +0.061 | 2023: +0.044 | 2024: +0.119 | 2025: +0.177 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.355 | 2016: -0.164 | 2017: +0.253 | 2018: +0.186 | 2019: +0.387 | 2020: +0.014 | 2021: +0.361 | 2022: +0.274 | 2023: +0.158 | 2024: +0.327 | 2025: +0.267 | 2026: -0.164
- IC CV=0.59, Neg years (linear/tail)=1/1 of 8, Half ratio=0.65, Recency ratio=0.73
- Early IC=+0.1093, Recent IC=+0.0801, 1st-half IC=+0.1472, 2nd-half IC=+0.0963, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.177, Q2=-0.016, Q3_mid=+0.172, Q4=+0.131, Q5_high_vol=+0.123

**`combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0961, Sharpe=+0.2777)
- Admission: Train IC=+0.2131, Deflated=+0.2139, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.101 | 2017: +0.222 | 2018: +0.200 | 2019: +0.114 | 2020: +0.163 | 2021: +0.112 | 2022: +0.132 | 2023: +0.079 | 2024: +0.112 | 2025: +0.063 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.210 | 2016: +0.070 | 2017: +0.111 | 2018: +0.293 | 2019: +0.093 | 2020: +0.160 | 2021: +0.250 | 2022: +0.191 | 2023: -0.073 | 2024: -0.026 | 2025: -0.066 | 2026: -0.029
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.65
- Early IC=+0.1886, Recent IC=+0.1219, 1st-half IC=+0.2292, 2nd-half IC=+0.1305, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.039, Q3_mid=+0.186, Q4=+0.156, Q5_high_vol=+0.241

**`combo_rank_max__max_up_ret__shaved_bar_trend_conviction`** (Lock IC=+0.0805, Sharpe=+0.2751)
- Admission: Train IC=+0.2182, Deflated=+0.2195, IR=0.75, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.074 | 2017: +0.184 | 2018: +0.223 | 2019: +0.072 | 2020: +0.168 | 2021: +0.093 | 2022: +0.074 | 2023: +0.106 | 2024: +0.107 | 2025: +0.122 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.233 | 2016: +0.243 | 2017: +0.190 | 2018: +0.289 | 2019: +0.061 | 2020: +0.281 | 2021: +0.198 | 2022: +0.116 | 2023: -0.083 | 2024: +0.191 | 2025: -0.006 | 2026: -0.248
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.58
- Early IC=+0.1424, Recent IC=+0.0824, 1st-half IC=+0.1950, 2nd-half IC=+0.1054, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.020, Q3_mid=+0.156, Q4=+0.189, Q5_high_vol=+0.212

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0836, Sharpe=+0.2749)
- Admission: Train IC=+0.2373, Deflated=+0.2394, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.073 | 2017: +0.215 | 2018: +0.170 | 2019: +0.102 | 2020: +0.175 | 2021: +0.060 | 2022: +0.117 | 2023: +0.160 | 2024: +0.099 | 2025: +0.073 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.401 | 2016: +0.139 | 2017: +0.339 | 2018: +0.243 | 2019: +0.168 | 2020: +0.145 | 2021: +0.180 | 2022: +0.063 | 2023: +0.187 | 2024: +0.230 | 2025: -0.033 | 2026: +0.006
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.65
- Early IC=+0.1368, Recent IC=+0.0888, 1st-half IC=+0.1642, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.031, Q3_mid=+0.190, Q4=+0.148, Q5_high_vol=+0.163

**`combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0818, Sharpe=+0.2746)
- Admission: Train IC=+0.1889, Deflated=+0.1908, IR=0.48, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.085 | 2017: +0.218 | 2018: +0.212 | 2019: +0.089 | 2020: +0.102 | 2021: +0.101 | 2022: +0.078 | 2023: +0.098 | 2024: +0.125 | 2025: +0.097 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.214 | 2016: +0.055 | 2017: +0.263 | 2018: +0.361 | 2019: +0.165 | 2020: +0.114 | 2021: +0.267 | 2022: +0.066 | 2023: +0.235 | 2024: +0.215 | 2025: -0.068 | 2026: -0.317
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.55
- Early IC=+0.1634, Recent IC=+0.0892, 1st-half IC=+0.2106, 2nd-half IC=+0.0971, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.006, Q3_mid=+0.174, Q4=+0.167, Q5_high_vol=+0.201

**`combo_min__close_vs_open_range__vwap_close_divergence_trend`** (Lock IC=+0.0900, Sharpe=+0.2723)
- Admission: Train IC=+0.2148, Deflated=+0.2157, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.053 | 2017: +0.187 | 2018: +0.082 | 2019: +0.072 | 2020: +0.091 | 2021: +0.075 | 2022: +0.099 | 2023: +0.119 | 2024: +0.115 | 2025: +0.148 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.158 | 2017: +0.274 | 2018: +0.194 | 2019: +0.281 | 2020: +0.126 | 2021: +0.303 | 2022: +0.138 | 2023: +0.242 | 2024: +0.162 | 2025: +0.129 | 2026: -0.206
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.80
- Early IC=+0.1086, Recent IC=+0.0874, 1st-half IC=+0.1262, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.030, Q3_mid=+0.142, Q4=+0.121, Q5_high_vol=+0.097

**`combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0873, Sharpe=+0.2699)
- Admission: Train IC=+0.2739, Deflated=+0.2751, IR=0.92, Mono=0.85, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.044 | 2017: +0.218 | 2018: +0.156 | 2019: +0.077 | 2020: +0.135 | 2021: +0.095 | 2022: +0.085 | 2023: +0.100 | 2024: +0.139 | 2025: +0.116 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.246 | 2017: +0.377 | 2018: +0.238 | 2019: +0.144 | 2020: +0.220 | 2021: +0.248 | 2022: +0.181 | 2023: +0.200 | 2024: +0.325 | 2025: +0.079 | 2026: -0.169
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.75
- Early IC=+0.1194, Recent IC=+0.0900, 1st-half IC=+0.1671, 2nd-half IC=+0.1070, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.013, Q3_mid=+0.174, Q4=+0.140, Q5_high_vol=+0.162

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1132, Sharpe=+0.2639)
- Admission: Train IC=+0.3059, Deflated=+0.3074, IR=1.10, Mono=0.86, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.262 | 2016: +0.085 | 2017: +0.210 | 2018: +0.192 | 2019: +0.148 | 2020: +0.160 | 2021: +0.115 | 2022: +0.098 | 2023: +0.117 | 2024: +0.152 | 2025: +0.131 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.395 | 2016: +0.300 | 2017: +0.341 | 2018: +0.336 | 2019: +0.210 | 2020: +0.259 | 2021: +0.229 | 2022: +0.223 | 2023: +0.191 | 2024: +0.257 | 2025: -0.007 | 2026: -0.258
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.61
- Early IC=+0.1739, Recent IC=+0.1061, 1st-half IC=+0.2066, 2nd-half IC=+0.1365, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.018, Q3_mid=+0.203, Q4=+0.173, Q5_high_vol=+0.214

**`combo_mean__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.1002, Sharpe=+0.2632)
- Admission: Train IC=+0.2099, Deflated=+0.2116, IR=0.66, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.061 | 2017: +0.243 | 2018: +0.192 | 2019: +0.138 | 2020: +0.165 | 2021: +0.122 | 2022: +0.078 | 2023: +0.091 | 2024: +0.137 | 2025: +0.108 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.401 | 2016: -0.022 | 2017: +0.137 | 2018: +0.124 | 2019: +0.335 | 2020: +0.016 | 2021: +0.390 | 2022: +0.251 | 2023: +0.146 | 2024: +0.232 | 2025: +0.086 | 2026: +0.013
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.67, Recency ratio=0.57
- Early IC=+0.1747, Recent IC=+0.0999, 1st-half IC=+0.1953, 2nd-half IC=+0.1299, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.030, Q3_mid=+0.191, Q4=+0.152, Q5_high_vol=+0.230

**`combo_rank_min__trend_bar_close_consistency__max_down_ret`** (Lock IC=+0.0855, Sharpe=+0.2616)
- Admission: Train IC=+0.2101, Deflated=+0.2123, IR=0.52, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.058 | 2017: +0.194 | 2018: +0.110 | 2019: +0.056 | 2020: +0.113 | 2021: +0.024 | 2022: +0.068 | 2023: +0.061 | 2024: +0.107 | 2025: +0.120 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.022 | 2017: +0.269 | 2018: +0.236 | 2019: +0.039 | 2020: +0.207 | 2021: +0.304 | 2022: +0.285 | 2023: +0.004 | 2024: +0.245 | 2025: +0.131 | 2026: +0.043
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.30
- Early IC=+0.1529, Recent IC=+0.0452, 1st-half IC=+0.1412, 2nd-half IC=+0.0735, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.147, Q2=-0.040, Q3_mid=+0.140, Q4=+0.103, Q5_high_vol=+0.168

**`combo_min__max_down_ret__shaved_bar_trend_conviction`** (Lock IC=+0.0768, Sharpe=+0.2589)
- Admission: Train IC=+0.1696, Deflated=+0.1711, IR=0.47, Mono=0.68, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.019 | 2017: +0.169 | 2018: +0.090 | 2019: +0.030 | 2020: +0.136 | 2021: -0.000 | 2022: -0.009 | 2023: +0.090 | 2024: +0.068 | 2025: +0.131 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.330 | 2016: -0.054 | 2017: +0.232 | 2018: +0.045 | 2019: +0.135 | 2020: +0.249 | 2021: +0.145 | 2022: +0.084 | 2023: -0.032 | 2024: +0.206 | 2025: +0.285 | 2026: +0.068
- IC CV=0.98, Neg years (linear/tail)=2/1 of 8, Half ratio=0.38, Recency ratio=-0.04
- Early IC=+0.1202, Recent IC=-0.0047, 1st-half IC=+0.1252, 2nd-half IC=+0.0473, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.132, Q2=-0.059, Q3_mid=+0.129, Q4=+0.095, Q5_high_vol=+0.124

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0789, Sharpe=+0.2580)
- Admission: Train IC=+0.2068, Deflated=+0.2080, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.095 | 2017: +0.219 | 2018: +0.111 | 2019: +0.027 | 2020: +0.130 | 2021: +0.044 | 2022: +0.127 | 2023: +0.100 | 2024: +0.125 | 2025: +0.092 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.293 | 2017: +0.367 | 2018: +0.241 | 2019: +0.004 | 2020: +0.183 | 2021: +0.193 | 2022: +0.103 | 2023: +0.104 | 2024: +0.218 | 2025: -0.075 | 2026: -0.143
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.62
- Early IC=+0.1374, Recent IC=+0.0854, 1st-half IC=+0.1644, 2nd-half IC=+0.0847, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.014, Q3_mid=+0.143, Q4=+0.140, Q5_high_vol=+0.156

**`combo_mean__net_volume_flow__max_down_ret`** (Lock IC=+0.0937, Sharpe=+0.2553)
- Admission: Train IC=+0.2123, Deflated=+0.2142, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.074 | 2017: +0.189 | 2018: +0.155 | 2019: +0.101 | 2020: +0.118 | 2021: +0.078 | 2022: +0.091 | 2023: +0.076 | 2024: +0.134 | 2025: +0.130 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.050 | 2017: +0.171 | 2018: +0.153 | 2019: +0.188 | 2020: +0.099 | 2021: +0.303 | 2022: +0.325 | 2023: +0.341 | 2024: +0.337 | 2025: +0.021 | 2026: -0.119
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.56
- Early IC=+0.1522, Recent IC=+0.0847, 1st-half IC=+0.1608, 2nd-half IC=+0.1035, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.020, Q3_mid=+0.173, Q4=+0.127, Q5_high_vol=+0.176

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0906, Sharpe=+0.2518)
- Admission: Train IC=+0.2462, Deflated=+0.2482, IR=0.77, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.048 | 2017: +0.233 | 2018: +0.113 | 2019: +0.122 | 2020: +0.121 | 2021: +0.073 | 2022: +0.056 | 2023: +0.064 | 2024: +0.085 | 2025: +0.133 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.111 | 2017: +0.267 | 2018: +0.360 | 2019: +0.324 | 2020: +0.217 | 2021: +0.340 | 2022: +0.063 | 2023: +0.041 | 2024: +0.147 | 2025: +0.082 | 2026: +0.223
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.41
- Early IC=+0.1606, Recent IC=+0.0656, 1st-half IC=+0.1605, 2nd-half IC=+0.0954, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.015, Q3_mid=+0.130, Q4=+0.169, Q5_high_vol=+0.150

**`combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0934, Sharpe=+0.2455)
- Admission: Train IC=+0.2494, Deflated=+0.2513, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.041 | 2017: +0.203 | 2018: +0.197 | 2019: +0.182 | 2020: +0.174 | 2021: +0.121 | 2022: +0.054 | 2023: +0.101 | 2024: +0.118 | 2025: +0.050 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.141 | 2017: +0.292 | 2018: +0.232 | 2019: +0.544 | 2020: +0.186 | 2021: +0.192 | 2022: +0.205 | 2023: +0.075 | 2024: +0.238 | 2025: +0.189 | 2026: +0.060
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.54
- Early IC=+0.1633, Recent IC=+0.0877, 1st-half IC=+0.1867, 2nd-half IC=+0.1362, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.033, Q3_mid=+0.182, Q4=+0.142, Q5_high_vol=+0.268

**`combo_sig_product__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0893, Sharpe=+0.2451)
- Admission: Train IC=+0.2270, Deflated=+0.2282, IR=0.62, Mono=0.68, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.110 | 2017: +0.179 | 2018: +0.187 | 2019: +0.131 | 2020: +0.119 | 2021: +0.013 | 2022: +0.115 | 2023: +0.112 | 2024: +0.095 | 2025: +0.092 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.262 | 2017: +0.158 | 2018: +0.323 | 2019: +0.321 | 2020: +0.066 | 2021: +0.252 | 2022: +0.126 | 2023: +0.290 | 2024: +0.316 | 2025: -0.008 | 2026: -0.101
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.38
- Early IC=+0.1679, Recent IC=+0.0640, 1st-half IC=+0.2039, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.029, Q3_mid=+0.136, Q4=+0.143, Q5_high_vol=+0.215

**`combo_rank_min__max_down_ret__close_vs_open_range`** (Lock IC=+0.0988, Sharpe=+0.2415)
- Admission: Train IC=+0.2083, Deflated=+0.2107, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.081 | 2017: +0.225 | 2018: +0.120 | 2019: +0.084 | 2020: +0.141 | 2021: +0.037 | 2022: +0.078 | 2023: +0.082 | 2024: +0.114 | 2025: +0.137 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.336 | 2016: +0.021 | 2017: +0.210 | 2018: +0.113 | 2019: +0.166 | 2020: +0.128 | 2021: +0.307 | 2022: +0.293 | 2023: +0.153 | 2024: +0.190 | 2025: +0.127 | 2026: +0.209
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.33
- Early IC=+0.1778, Recent IC=+0.0578, 1st-half IC=+0.1625, 2nd-half IC=+0.0918, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.034, Q3_mid=+0.169, Q4=+0.126, Q5_high_vol=+0.186

**`combo_max__first_bar_return__close_vs_open_range`** (Lock IC=+0.0794, Sharpe=+0.2412)
- Admission: Train IC=+0.2151, Deflated=+0.2165, IR=0.73, Mono=0.78, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.108 | 2017: +0.209 | 2018: +0.218 | 2019: +0.101 | 2020: +0.141 | 2021: +0.125 | 2022: +0.124 | 2023: +0.084 | 2024: +0.135 | 2025: +0.121 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.040 | 2017: +0.258 | 2018: +0.335 | 2019: +0.162 | 2020: +0.284 | 2021: +0.250 | 2022: +0.237 | 2023: +0.337 | 2024: +0.262 | 2025: -0.128 | 2026: -0.472
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.73
- Early IC=+0.1694, Recent IC=+0.1245, 1st-half IC=+0.2047, 2nd-half IC=+0.1277, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.043, Q3_mid=+0.162, Q4=+0.165, Q5_high_vol=+0.201

**`combo_rank_min__bar_ret_0__max_down_ret`** (Lock IC=+0.0797, Sharpe=+0.2390)
- Admission: Train IC=+0.2082, Deflated=+0.2105, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.098 | 2017: +0.201 | 2018: +0.164 | 2019: +0.130 | 2020: +0.098 | 2021: +0.071 | 2022: +0.027 | 2023: +0.056 | 2024: +0.103 | 2025: +0.123 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.344 | 2016: -0.075 | 2017: +0.320 | 2018: +0.225 | 2019: +0.326 | 2020: +0.179 | 2021: +0.349 | 2022: +0.131 | 2023: +0.073 | 2024: +0.220 | 2025: +0.160 | 2026: -0.097
- IC CV=0.55, Neg years (linear/tail)=0/1 of 8, Half ratio=0.48, Recency ratio=0.27
- Early IC=+0.1868, Recent IC=+0.0507, 1st-half IC=+0.1756, 2nd-half IC=+0.0850, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.162, Q2=-0.034, Q3_mid=+0.139, Q4=+0.116, Q5_high_vol=+0.202

**`combo_min__trend_bar_close_consistency__max_down_ret`** (Lock IC=+0.0870, Sharpe=+0.2373)
- Admission: Train IC=+0.1967, Deflated=+0.1983, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.040 | 2017: +0.173 | 2018: +0.105 | 2019: +0.057 | 2020: +0.095 | 2021: +0.030 | 2022: +0.077 | 2023: +0.069 | 2024: +0.113 | 2025: +0.125 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.318 | 2016: -0.118 | 2017: +0.307 | 2018: +0.116 | 2019: +0.119 | 2020: +0.233 | 2021: +0.261 | 2022: +0.261 | 2023: -0.035 | 2024: +0.247 | 2025: +0.173 | 2026: -0.001
- IC CV=0.60, Neg years (linear/tail)=0/1 of 8, Half ratio=0.54, Recency ratio=0.43
- Early IC=+0.1240, Recent IC=+0.0534, 1st-half IC=+0.1268, 2nd-half IC=+0.0686, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.140, Q2=-0.035, Q3_mid=+0.133, Q4=+0.106, Q5_high_vol=+0.134

**`combo_min__trend_day_regime_conviction__close_vs_open_range`** (Lock IC=+0.0833, Sharpe=+0.2334)
- Admission: Train IC=+0.2448, Deflated=+0.2463, IR=0.48, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.069 | 2017: +0.203 | 2018: +0.123 | 2019: +0.062 | 2020: +0.099 | 2021: +0.055 | 2022: +0.093 | 2023: +0.080 | 2024: +0.115 | 2025: +0.138 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.178 | 2017: +0.359 | 2018: +0.240 | 2019: +0.201 | 2020: +0.124 | 2021: +0.193 | 2022: +0.147 | 2023: +0.095 | 2024: +0.259 | 2025: -0.065 | 2026: -0.017
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.60
- Early IC=+0.1233, Recent IC=+0.0738, 1st-half IC=+0.1447, 2nd-half IC=+0.0818, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.008, Q3_mid=+0.146, Q4=+0.132, Q5_high_vol=+0.112

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0851, Sharpe=+0.2287)
- Admission: Train IC=+0.2408, Deflated=+0.2421, IR=0.63, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.108 | 2017: +0.225 | 2018: +0.253 | 2019: +0.121 | 2020: +0.163 | 2021: +0.175 | 2022: +0.113 | 2023: +0.096 | 2024: +0.144 | 2025: +0.094 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.171 | 2017: +0.161 | 2018: +0.435 | 2019: +0.161 | 2020: +0.293 | 2021: +0.350 | 2022: +0.202 | 2023: +0.059 | 2024: +0.253 | 2025: +0.021 | 2026: -0.411
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.79
- Early IC=+0.1829, Recent IC=+0.1437, 1st-half IC=+0.2339, 2nd-half IC=+0.1476, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.035, Q3_mid=+0.189, Q4=+0.201, Q5_high_vol=+0.250

**`combo_max__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.1001, Sharpe=+0.2217)
- Admission: Train IC=+0.1867, Deflated=+0.1876, IR=0.49, Mono=0.66, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.264 | 2016: +0.078 | 2017: +0.211 | 2018: +0.148 | 2019: +0.111 | 2020: +0.133 | 2021: +0.034 | 2022: +0.109 | 2023: +0.048 | 2024: +0.107 | 2025: +0.127 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.164 | 2016: +0.095 | 2017: +0.218 | 2018: +0.157 | 2019: +0.199 | 2020: +0.143 | 2021: +0.153 | 2022: +0.272 | 2023: +0.041 | 2024: +0.082 | 2025: +0.116 | 2026: -0.073
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.42
- Early IC=+0.1711, Recent IC=+0.0716, 1st-half IC=+0.1955, 2nd-half IC=+0.0983, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.007, Q3_mid=+0.183, Q4=+0.114, Q5_high_vol=+0.205

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0830, Sharpe=+0.2163)
- Admission: Train IC=+0.2285, Deflated=+0.2300, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.132 | 2017: +0.167 | 2018: +0.256 | 2019: +0.127 | 2020: +0.098 | 2021: +0.151 | 2022: +0.082 | 2023: +0.079 | 2024: +0.143 | 2025: +0.092 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.170 | 2017: +0.322 | 2018: +0.471 | 2019: +0.162 | 2020: +0.254 | 2021: +0.297 | 2022: +0.147 | 2023: +0.089 | 2024: +0.257 | 2025: -0.063 | 2026: -0.361
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.65
- Early IC=+0.1797, Recent IC=+0.1168, 1st-half IC=+0.2183, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.002, Q3_mid=+0.147, Q4=+0.184, Q5_high_vol=+0.248

**`combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction`** (Lock IC=+0.0841, Sharpe=+0.2138)
- Admission: Train IC=+0.2576, Deflated=+0.2585, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.058 | 2017: +0.252 | 2018: +0.145 | 2019: +0.072 | 2020: +0.185 | 2021: +0.094 | 2022: +0.047 | 2023: +0.080 | 2024: +0.105 | 2025: +0.144 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.416 | 2016: +0.171 | 2017: +0.250 | 2018: +0.200 | 2019: +0.141 | 2020: +0.115 | 2021: +0.226 | 2022: +0.293 | 2023: -0.036 | 2024: +0.226 | 2025: +0.178 | 2026: -0.112
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.48
- Early IC=+0.1432, Recent IC=+0.0687, 1st-half IC=+0.1855, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.023, Q3_mid=+0.156, Q4=+0.192, Q5_high_vol=+0.159

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0958, Sharpe=+0.2125)
- Admission: Train IC=+0.2448, Deflated=+0.2467, IR=0.71, Mono=0.73, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.233 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.071 | 2022: +0.082 | 2023: +0.077 | 2024: +0.080 | 2025: +0.146 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.321 | 2016: +0.101 | 2017: +0.263 | 2018: +0.348 | 2019: +0.296 | 2020: +0.189 | 2021: +0.240 | 2022: +0.112 | 2023: +0.035 | 2024: +0.144 | 2025: +0.078 | 2026: +0.194
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.47
- Early IC=+0.1625, Recent IC=+0.0765, 1st-half IC=+0.1626, 2nd-half IC=+0.0948, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.028, Q3_mid=+0.131, Q4=+0.158, Q5_high_vol=+0.152

**`combo_max__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.0978, Sharpe=+0.2106)
- Admission: Train IC=+0.1898, Deflated=+0.1908, IR=0.47, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.077 | 2017: +0.155 | 2018: +0.171 | 2019: +0.104 | 2020: +0.121 | 2021: +0.044 | 2022: +0.117 | 2023: +0.060 | 2024: +0.106 | 2025: +0.091 | 2026: +0.094
- Yearly Tail ICs:   2015: +0.160 | 2016: +0.140 | 2017: +0.163 | 2018: +0.230 | 2019: +0.155 | 2020: +0.062 | 2021: +0.164 | 2022: +0.215 | 2023: +0.139 | 2024: +0.029 | 2025: +0.087 | 2026: -0.103
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.52
- Early IC=+0.1556, Recent IC=+0.0802, 1st-half IC=+0.1832, 2nd-half IC=+0.0986, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.177, Q2=-0.009, Q3_mid=+0.187, Q4=+0.116, Q5_high_vol=+0.195

**`combo_max__max_up_ret__shaved_bar_trend_conviction`** (Lock IC=+0.0806, Sharpe=+0.2085)
- Admission: Train IC=+0.2213, Deflated=+0.2224, IR=0.64, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.062 | 2017: +0.173 | 2018: +0.211 | 2019: +0.056 | 2020: +0.173 | 2021: +0.076 | 2022: +0.049 | 2023: +0.104 | 2024: +0.098 | 2025: +0.124 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.200 | 2017: +0.155 | 2018: +0.321 | 2019: +0.120 | 2020: +0.298 | 2021: +0.219 | 2022: +0.047 | 2023: -0.075 | 2024: +0.274 | 2025: -0.038 | 2026: -0.269
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.46
- Early IC=+0.1360, Recent IC=+0.0628, 1st-half IC=+0.1876, 2nd-half IC=+0.0975, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.007, Q3_mid=+0.146, Q4=+0.176, Q5_high_vol=+0.205

**`combo_rank_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0831, Sharpe=+0.2070)
- Admission: Train IC=+0.2295, Deflated=+0.2317, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.090 | 2017: +0.239 | 2018: +0.234 | 2019: +0.150 | 2020: +0.126 | 2021: +0.098 | 2022: +0.093 | 2023: +0.036 | 2024: +0.117 | 2025: +0.112 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.605 | 2016: -0.121 | 2017: +0.202 | 2018: +0.245 | 2019: +0.306 | 2020: +0.177 | 2021: +0.248 | 2022: +0.130 | 2023: +0.169 | 2024: +0.217 | 2025: +0.104 | 2026: -0.076
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.58, Recency ratio=0.54
- Early IC=+0.1753, Recent IC=+0.0948, 1st-half IC=+0.2092, 2nd-half IC=+0.1211, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.005, Q3_mid=+0.165, Q4=+0.173, Q5_high_vol=+0.219

**`combo_min__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0736, Sharpe=+0.2013)
- Admission: Train IC=+0.2288, Deflated=+0.2301, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.137 | 2016: +0.027 | 2017: +0.172 | 2018: +0.129 | 2019: +0.143 | 2020: +0.084 | 2021: +0.203 | 2022: +0.147 | 2023: +0.111 | 2024: +0.129 | 2025: +0.101 | 2026: -0.115
- Yearly Tail ICs:   2015: +0.171 | 2016: +0.056 | 2017: +0.324 | 2018: +0.362 | 2019: +0.251 | 2020: +0.053 | 2021: +0.232 | 2022: +0.278 | 2023: +0.213 | 2024: +0.329 | 2025: +0.065 | 2026: -0.276
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=2.13
- Early IC=+0.0822, Recent IC=+0.1750, 1st-half IC=+0.1330, 2nd-half IC=+0.1444, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.058, Q3_mid=+0.170, Q4=+0.162, Q5_high_vol=+0.101

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0982, Sharpe=+0.2007)
- Admission: Train IC=+0.2589, Deflated=+0.2608, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.071 | 2017: +0.178 | 2018: +0.194 | 2019: +0.134 | 2020: +0.141 | 2021: +0.136 | 2022: +0.088 | 2023: +0.128 | 2024: +0.146 | 2025: +0.112 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.380 | 2016: +0.140 | 2017: +0.327 | 2018: +0.339 | 2019: +0.247 | 2020: +0.214 | 2021: +0.228 | 2022: +0.172 | 2023: +0.323 | 2024: +0.248 | 2025: -0.125 | 2026: -0.064
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.85
- Early IC=+0.1309, Recent IC=+0.1118, 1st-half IC=+0.1733, 2nd-half IC=+0.1284, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.029, Q3_mid=+0.196, Q4=+0.139, Q5_high_vol=+0.179

**`combo_mean__max_down_ret__vwap_close_divergence_trend`** (Lock IC=+0.0833, Sharpe=+0.2002)
- Admission: Train IC=+0.1924, Deflated=+0.1934, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.033 | 2017: +0.214 | 2018: +0.126 | 2019: +0.113 | 2020: +0.091 | 2021: +0.085 | 2022: +0.073 | 2023: +0.088 | 2024: +0.114 | 2025: +0.124 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.130 | 2017: +0.224 | 2018: +0.185 | 2019: +0.245 | 2020: +0.080 | 2021: +0.277 | 2022: +0.227 | 2023: +0.304 | 2024: +0.200 | 2025: +0.137 | 2026: -0.287
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.65
- Early IC=+0.1208, Recent IC=+0.0791, 1st-half IC=+0.1509, 2nd-half IC=+0.0968, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.013, Q3_mid=+0.168, Q4=+0.106, Q5_high_vol=+0.136

**`combo_rank_min__max_up_ret__max_down_ret`** (Lock IC=+0.0995, Sharpe=+0.1901)
- Admission: Train IC=+0.2603, Deflated=+0.2617, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.302 | 2016: +0.097 | 2017: +0.217 | 2018: +0.126 | 2019: +0.096 | 2020: +0.146 | 2021: +0.090 | 2022: +0.080 | 2023: +0.091 | 2024: +0.130 | 2025: +0.123 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.466 | 2016: +0.019 | 2017: +0.266 | 2018: +0.235 | 2019: +0.301 | 2020: +0.270 | 2021: +0.291 | 2022: +0.081 | 2023: -0.015 | 2024: +0.189 | 2025: +0.125 | 2026: -0.194
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.41
- Early IC=+0.2000, Recent IC=+0.0829, 1st-half IC=+0.1836, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.031, Q3_mid=+0.175, Q4=+0.124, Q5_high_vol=+0.200

**`combo_max__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0709, Sharpe=+0.1776)
- Admission: Train IC=+0.2264, Deflated=+0.2277, IR=0.76, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.055 | 2017: +0.105 | 2018: +0.196 | 2019: +0.107 | 2020: +0.092 | 2021: +0.092 | 2022: +0.132 | 2023: +0.083 | 2024: +0.123 | 2025: +0.079 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.104 | 2017: +0.067 | 2018: +0.432 | 2019: +0.129 | 2020: +0.179 | 2021: +0.349 | 2022: +0.137 | 2023: +0.121 | 2024: +0.254 | 2025: +0.003 | 2026: -0.284
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.81
- Early IC=+0.1385, Recent IC=+0.1119, 1st-half IC=+0.1665, 2nd-half IC=+0.1105, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.111, Q2=-0.017, Q3_mid=+0.171, Q4=+0.155, Q5_high_vol=+0.219

**`vwap_trend_channel_slope`** (Lock IC=+0.0839, Sharpe=+0.1758)
- Admission: Train IC=+0.1543, Deflated=+0.1549, IR=0.42, Mono=0.66, p=0.0020, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.93
- Early IC=+0.0779, Recent IC=+0.0726, 1st-half IC=+0.1148, 2nd-half IC=+0.0843, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.057, Q3_mid=+0.138, Q4=+0.073, Q5_high_vol=+0.096

**`max_down_ret`** (Lock IC=+0.0828, Sharpe=+0.1693)
- Admission: Train IC=+0.1750, Deflated=+0.1774, IR=0.51, Mono=0.66, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.052 | 2017: +0.240 | 2018: +0.131 | 2019: +0.112 | 2020: +0.138 | 2021: +0.064 | 2022: +0.057 | 2023: +0.031 | 2024: +0.115 | 2025: +0.129 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.346 | 2016: -0.013 | 2017: +0.236 | 2018: +0.099 | 2019: +0.326 | 2020: +0.060 | 2021: +0.325 | 2022: +0.141 | 2023: +0.096 | 2024: +0.230 | 2025: +0.240 | 2026: +0.035
- IC CV=0.60, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.36
- Early IC=+0.1665, Recent IC=+0.0603, 1st-half IC=+0.1563, 2nd-half IC=+0.0957, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.018, Q3_mid=+0.162, Q4=+0.119, Q5_high_vol=+0.193

**`combo_rank_min__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0764, Sharpe=+0.1600)
- Admission: Train IC=+0.2251, Deflated=+0.2268, IR=0.51, Mono=0.66, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.125 | 2017: +0.162 | 2018: +0.206 | 2019: +0.130 | 2020: +0.089 | 2021: +0.107 | 2022: +0.055 | 2023: +0.064 | 2024: +0.098 | 2025: +0.099 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.417 | 2016: -0.074 | 2017: +0.299 | 2018: +0.329 | 2019: +0.187 | 2020: +0.137 | 2021: +0.350 | 2022: +0.097 | 2023: +0.106 | 2024: +0.108 | 2025: +0.151 | 2026: -0.084
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.47
- Early IC=+0.1736, Recent IC=+0.0812, 1st-half IC=+0.1870, 2nd-half IC=+0.0986, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.024, Q3_mid=+0.128, Q4=+0.168, Q5_high_vol=+0.206

**`combo_min__max_up_ret__max_down_ret`** (Lock IC=+0.1077, Sharpe=+0.1595)
- Admission: Train IC=+0.2299, Deflated=+0.2309, IR=0.58, Mono=0.69, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.304 | 2016: +0.081 | 2017: +0.198 | 2018: +0.129 | 2019: +0.106 | 2020: +0.136 | 2021: +0.120 | 2022: +0.114 | 2023: +0.105 | 2024: +0.117 | 2025: +0.134 | 2026: +0.037
- Yearly Tail ICs:   2015: +0.378 | 2016: +0.013 | 2017: +0.214 | 2018: +0.180 | 2019: +0.221 | 2020: +0.151 | 2021: +0.328 | 2022: +0.206 | 2023: +0.163 | 2024: +0.212 | 2025: +0.204 | 2026: +0.066
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.61
- Early IC=+0.1925, Recent IC=+0.1173, 1st-half IC=+0.1898, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.046, Q3_mid=+0.181, Q4=+0.138, Q5_high_vol=+0.207

**`combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early`** (Lock IC=+0.0825, Sharpe=+0.1565)
- Admission: Train IC=+0.2186, Deflated=+0.2199, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.105 | 2017: +0.135 | 2018: +0.211 | 2019: +0.063 | 2020: +0.109 | 2021: +0.042 | 2022: +0.132 | 2023: +0.073 | 2024: +0.073 | 2025: +0.091 | 2026: +0.060
- Yearly Tail ICs:   2015: +0.147 | 2016: +0.274 | 2017: +0.174 | 2018: +0.224 | 2019: +0.162 | 2020: +0.082 | 2021: +0.204 | 2022: +0.105 | 2023: +0.092 | 2024: +0.151 | 2025: -0.044 | 2026: -0.205
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.44, Recency ratio=0.49
- Early IC=+0.1777, Recent IC=+0.0868, 1st-half IC=+0.2082, 2nd-half IC=+0.0923, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.152, Q2=-0.000, Q3_mid=+0.182, Q4=+0.116, Q5_high_vol=+0.254

**`combo_max__volatility_expansion_trend_vector__bar_body_rng_0`** (Lock IC=+0.0835, Sharpe=+0.1550)
- Admission: Train IC=+0.2482, Deflated=+0.2501, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.119 | 2017: +0.206 | 2018: +0.181 | 2019: +0.107 | 2020: +0.133 | 2021: +0.120 | 2022: +0.104 | 2023: +0.077 | 2024: +0.120 | 2025: +0.130 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.447 | 2016: -0.125 | 2017: +0.280 | 2018: +0.287 | 2019: +0.322 | 2020: +0.197 | 2021: +0.219 | 2022: +0.329 | 2023: +0.328 | 2024: +0.228 | 2025: +0.085 | 2026: -0.353
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.63
- Early IC=+0.1765, Recent IC=+0.1120, 1st-half IC=+0.1912, 2nd-half IC=+0.1206, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.015, Q3_mid=+0.151, Q4=+0.163, Q5_high_vol=+0.220

**`combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1238, Sharpe=+0.1525)
- Admission: Train IC=+0.2374, Deflated=+0.2383, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.060 | 2017: +0.242 | 2018: +0.095 | 2019: +0.124 | 2020: +0.107 | 2021: +0.031 | 2022: +0.089 | 2023: +0.101 | 2024: +0.105 | 2025: +0.121 | 2026: +0.142
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.147 | 2017: +0.199 | 2018: +0.253 | 2019: +0.220 | 2020: +0.208 | 2021: +0.001 | 2022: +0.200 | 2023: -0.107 | 2024: +0.138 | 2025: +0.123 | 2026: -0.108
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.36
- Early IC=+0.1667, Recent IC=+0.0600, 1st-half IC=+0.1887, 2nd-half IC=+0.0940, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.040, Q3_mid=+0.128, Q4=+0.140, Q5_high_vol=+0.176

**`combo_max__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0991, Sharpe=+0.1521)
- Admission: Train IC=+0.1916, Deflated=+0.1924, IR=0.68, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.112 | 2017: +0.203 | 2018: +0.197 | 2019: +0.110 | 2020: +0.127 | 2021: +0.062 | 2022: +0.120 | 2023: +0.071 | 2024: +0.104 | 2025: +0.077 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.139 | 2016: +0.149 | 2017: +0.230 | 2018: +0.258 | 2019: +0.094 | 2020: +0.192 | 2021: +0.219 | 2022: +0.112 | 2023: -0.040 | 2024: +0.024 | 2025: -0.048 | 2026: +0.123
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.53
- Early IC=+0.1708, Recent IC=+0.0911, 1st-half IC=+0.2082, 2nd-half IC=+0.1057, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.050, Q3_mid=+0.147, Q4=+0.134, Q5_high_vol=+0.203

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0779, Sharpe=+0.1500)
- Admission: Train IC=+0.2551, Deflated=+0.2562, IR=0.93, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.336 | 2016: +0.119 | 2017: +0.177 | 2018: +0.207 | 2019: +0.122 | 2020: +0.136 | 2021: +0.143 | 2022: +0.050 | 2023: +0.082 | 2024: +0.084 | 2025: +0.035 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.142 | 2017: +0.386 | 2018: +0.360 | 2019: +0.347 | 2020: +0.099 | 2021: +0.207 | 2022: +0.077 | 2023: +0.135 | 2024: -0.044 | 2025: -0.062 | 2026: +0.137
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.42
- Early IC=+0.2276, Recent IC=+0.0964, 1st-half IC=+0.2286, 2nd-half IC=+0.1152, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.014, Q3_mid=+0.177, Q4=+0.169, Q5_high_vol=+0.273

**`combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0`** (Lock IC=+0.0727, Sharpe=+0.1480)
- Admission: Train IC=+0.2461, Deflated=+0.2475, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.112 | 2017: +0.148 | 2018: +0.261 | 2019: +0.107 | 2020: +0.114 | 2021: +0.105 | 2022: +0.120 | 2023: +0.070 | 2024: +0.135 | 2025: +0.106 | 2026: -0.097
- Yearly Tail ICs:   2015: +0.249 | 2016: +0.210 | 2017: +0.170 | 2018: +0.314 | 2019: +0.143 | 2020: +0.304 | 2021: +0.221 | 2022: +0.229 | 2023: +0.369 | 2024: +0.243 | 2025: -0.192 | 2026: -0.443
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.70
- Early IC=+0.1618, Recent IC=+0.1129, 1st-half IC=+0.2063, 2nd-half IC=+0.1174, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.015, Q3_mid=+0.161, Q4=+0.171, Q5_high_vol=+0.241

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0823, Sharpe=+0.1403)
- Admission: Train IC=+0.2737, Deflated=+0.2758, IR=0.88, Mono=0.79, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.085 | 2017: +0.205 | 2018: +0.250 | 2019: +0.155 | 2020: +0.120 | 2021: +0.089 | 2022: +0.055 | 2023: +0.059 | 2024: +0.109 | 2025: +0.100 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.168 | 2017: +0.351 | 2018: +0.314 | 2019: +0.237 | 2020: +0.201 | 2021: +0.357 | 2022: +0.284 | 2023: +0.165 | 2024: +0.165 | 2025: +0.070 | 2026: -0.178
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.40
- Early IC=+0.1768, Recent IC=+0.0714, 1st-half IC=+0.2134, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.005, Q3_mid=+0.165, Q4=+0.163, Q5_high_vol=+0.236

**`combo_sig_product__rsi_opening__h2_l2_pullback_continuation`** (Lock IC=+0.0727, Sharpe=+0.1402)
- Admission: Train IC=+0.1441, Deflated=+0.1457, IR=0.36, Mono=0.65, p=0.0048, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.091 | 2017: +0.145 | 2018: +0.125 | 2019: +0.058 | 2020: +0.064 | 2021: +0.052 | 2022: +0.073 | 2023: +0.087 | 2024: +0.097 | 2025: +0.114 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.192 | 2017: +0.069 | 2018: +0.120 | 2019: +0.109 | 2020: -0.016 | 2021: +0.069 | 2022: +0.182 | 2023: +0.232 | 2024: +0.373 | 2025: -0.123 | 2026: +0.075
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.49, Recency ratio=0.50
- Early IC=+0.1257, Recent IC=+0.0624, 1st-half IC=+0.1385, 2nd-half IC=+0.0680, Neg regimes=1/5
- Weak component: `rsi_opening` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.096, Q2=-0.002, Q3_mid=+0.161, Q4=+0.095, Q5_high_vol=+0.128

**`combo_min__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0885, Sharpe=+0.1366)
- Admission: Train IC=+0.1946, Deflated=+0.1954, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.152 | 2016: +0.037 | 2017: +0.206 | 2018: +0.096 | 2019: +0.094 | 2020: +0.096 | 2021: +0.126 | 2022: +0.086 | 2023: +0.093 | 2024: +0.123 | 2025: +0.139 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.121 | 2017: +0.203 | 2018: +0.326 | 2019: +0.252 | 2020: +0.121 | 2021: +0.291 | 2022: +0.175 | 2023: +0.231 | 2024: +0.133 | 2025: +0.203 | 2026: -0.398
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=1.13
- Early IC=+0.0940, Recent IC=+0.1058, 1st-half IC=+0.1329, 2nd-half IC=+0.1012, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.035, Q3_mid=+0.171, Q4=+0.123, Q5_high_vol=+0.106

**`combo_z_sum__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=+0.0883, Sharpe=+0.1362)
- Admission: Train IC=+0.2177, Deflated=+0.2195, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.097 | 2017: +0.201 | 2018: +0.180 | 2019: +0.140 | 2020: +0.096 | 2021: +0.127 | 2022: +0.076 | 2023: +0.094 | 2024: +0.108 | 2025: +0.154 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.235 | 2016: +0.071 | 2017: +0.142 | 2018: +0.383 | 2019: +0.278 | 2020: +0.028 | 2021: +0.282 | 2022: +0.287 | 2023: +0.278 | 2024: +0.183 | 2025: +0.128 | 2026: -0.338
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.67
- Early IC=+0.1515, Recent IC=+0.1014, 1st-half IC=+0.1826, 2nd-half IC=+0.1123, Neg regimes=1/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.008, Q3_mid=+0.172, Q4=+0.148, Q5_high_vol=+0.166

**`combo_sig_product__early_body_momentum__close_vs_open_range`** (Lock IC=+0.0775, Sharpe=+0.1341)
- Admission: Train IC=+0.2234, Deflated=+0.2253, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.073 | 2017: +0.143 | 2018: +0.082 | 2019: +0.064 | 2020: +0.094 | 2021: +0.036 | 2022: +0.119 | 2023: +0.084 | 2024: +0.109 | 2025: +0.144 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.313 | 2016: +0.126 | 2017: +0.361 | 2018: +0.216 | 2019: +0.087 | 2020: +0.117 | 2021: +0.249 | 2022: +0.128 | 2023: +0.046 | 2024: +0.255 | 2025: -0.009 | 2026: +0.006
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.67
- Early IC=+0.1166, Recent IC=+0.0779, 1st-half IC=+0.1222, 2nd-half IC=+0.0828, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.169, Q2=-0.013, Q3_mid=+0.157, Q4=+0.125, Q5_high_vol=+0.079

**`combo_max__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0950, Sharpe=+0.1326)
- Admission: Train IC=+0.2123, Deflated=+0.2141, IR=0.47, Mono=0.68, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.129 | 2017: +0.172 | 2018: +0.148 | 2019: +0.126 | 2020: +0.130 | 2021: +0.068 | 2022: +0.090 | 2023: +0.048 | 2024: +0.092 | 2025: +0.082 | 2026: +0.141
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.127 | 2017: +0.113 | 2018: +0.114 | 2019: +0.212 | 2020: +0.069 | 2021: +0.166 | 2022: +0.082 | 2023: -0.125 | 2024: -0.084 | 2025: +0.007 | 2026: +0.291
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.42
- Early IC=+0.1899, Recent IC=+0.0792, 1st-half IC=+0.1900, 2nd-half IC=+0.1063, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.008, Q3_mid=+0.132, Q4=+0.150, Q5_high_vol=+0.229

**`combo_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0778, Sharpe=+0.1204)
- Admission: Train IC=+0.2451, Deflated=+0.2464, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.097 | 2017: +0.166 | 2018: +0.119 | 2019: +0.082 | 2020: +0.119 | 2021: +0.059 | 2022: +0.112 | 2023: +0.115 | 2024: +0.133 | 2025: +0.088 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.322 | 2017: +0.126 | 2018: +0.287 | 2019: +0.158 | 2020: +0.103 | 2021: +0.244 | 2022: +0.159 | 2023: +0.276 | 2024: +0.260 | 2025: -0.179 | 2026: -0.123
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.60
- Early IC=+0.1438, Recent IC=+0.0858, 1st-half IC=+0.1679, 2nd-half IC=+0.0983, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.024, Q3_mid=+0.173, Q4=+0.125, Q5_high_vol=+0.168

**`combo_max__early_body_momentum__close_vs_open_range`** (Lock IC=+0.0793, Sharpe=+0.1117)
- Admission: Train IC=+0.2053, Deflated=+0.2064, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.064 | 2017: +0.153 | 2018: +0.110 | 2019: +0.031 | 2020: +0.094 | 2021: +0.054 | 2022: +0.100 | 2023: +0.078 | 2024: +0.129 | 2025: +0.141 | 2026: -0.105
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.211 | 2017: +0.206 | 2018: +0.109 | 2019: +0.030 | 2020: +0.202 | 2021: +0.239 | 2022: +0.103 | 2023: +0.043 | 2024: +0.286 | 2025: +0.132 | 2026: -0.082
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.74
- Early IC=+0.1038, Recent IC=+0.0770, 1st-half IC=+0.1306, 2nd-half IC=+0.0749, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.161, Q2=-0.009, Q3_mid=+0.154, Q4=+0.117, Q5_high_vol=+0.088

**`combo_mean__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0733, Sharpe=+0.0937)
- Admission: Train IC=+0.2730, Deflated=+0.2744, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.042 | 2017: +0.150 | 2018: +0.172 | 2019: +0.128 | 2020: +0.094 | 2021: +0.145 | 2022: +0.149 | 2023: +0.098 | 2024: +0.133 | 2025: +0.086 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.203 | 2016: +0.162 | 2017: +0.172 | 2018: +0.444 | 2019: +0.227 | 2020: +0.162 | 2021: +0.309 | 2022: +0.227 | 2023: +0.331 | 2024: +0.310 | 2025: -0.017 | 2026: -0.331
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=1.21
- Early IC=+0.1214, Recent IC=+0.1468, 1st-half IC=+0.1625, 2nd-half IC=+0.1324, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.014, Q3_mid=+0.180, Q4=+0.161, Q5_high_vol=+0.183

**`combo_rank_max__net_volume_flow__bar_ret_0`** (Lock IC=+0.0744, Sharpe=+0.0795)
- Admission: Train IC=+0.2139, Deflated=+0.2155, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.119 | 2017: +0.176 | 2018: +0.234 | 2019: +0.119 | 2020: +0.115 | 2021: +0.114 | 2022: +0.098 | 2023: +0.077 | 2024: +0.124 | 2025: +0.106 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.216 | 2016: +0.087 | 2017: +0.177 | 2018: +0.286 | 2019: +0.113 | 2020: +0.338 | 2021: +0.271 | 2022: +0.249 | 2023: +0.369 | 2024: +0.243 | 2025: -0.040 | 2026: -0.519
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.68
- Early IC=+0.1568, Recent IC=+0.1064, 1st-half IC=+0.1962, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.012, Q3_mid=+0.159, Q4=+0.156, Q5_high_vol=+0.205

**`combo_diff__bar_ret_0__h2_l2_pullback_continuation`** (Lock IC=+0.0830, Sharpe=+0.0754)
- Admission: Train IC=+0.1964, Deflated=+0.1979, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.100 | 2017: +0.159 | 2018: +0.157 | 2019: +0.100 | 2020: +0.100 | 2021: +0.072 | 2022: +0.087 | 2023: +0.100 | 2024: +0.138 | 2025: +0.092 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.306 | 2016: +0.036 | 2017: +0.110 | 2018: +0.331 | 2019: +0.169 | 2020: +0.081 | 2021: +0.177 | 2022: +0.223 | 2023: +0.304 | 2024: +0.312 | 2025: -0.015 | 2026: -0.310
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.55
- Early IC=+0.1460, Recent IC=+0.0796, 1st-half IC=+0.1732, 2nd-half IC=+0.0970, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.005, Q3_mid=+0.155, Q4=+0.138, Q5_high_vol=+0.158

**`combo_mean__first_bar_return__early_order_flow_imbalance`** (Lock IC=+0.0687, Sharpe=+0.0726)
- Admission: Train IC=+0.2076, Deflated=+0.2090, IR=0.61, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.025 | 2017: +0.137 | 2018: +0.190 | 2019: +0.135 | 2020: +0.075 | 2021: +0.131 | 2022: +0.122 | 2023: +0.073 | 2024: +0.119 | 2025: +0.087 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.189 | 2016: -0.074 | 2017: +0.148 | 2018: +0.399 | 2019: +0.278 | 2020: +0.096 | 2021: +0.337 | 2022: +0.261 | 2023: +0.310 | 2024: +0.309 | 2025: +0.095 | 2026: -0.274
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.84, Recency ratio=1.30
- Early IC=+0.0968, Recent IC=+0.1264, 1st-half IC=+0.1428, 2nd-half IC=+0.1202, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.151, Q2=-0.013, Q3_mid=+0.139, Q4=+0.160, Q5_high_vol=+0.145

**`combo_rank_max__bar_ret_0__shaved_bar_trend_conviction`** (Lock IC=+0.0695, Sharpe=+0.0693)
- Admission: Train IC=+0.1705, Deflated=+0.1713, IR=0.64, Mono=0.70, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.108 | 2017: +0.174 | 2018: +0.229 | 2019: +0.059 | 2020: +0.176 | 2021: +0.104 | 2022: +0.047 | 2023: +0.079 | 2024: +0.108 | 2025: +0.135 | 2026: -0.108
- Yearly Tail ICs:   2015: +0.082 | 2016: +0.006 | 2017: +0.168 | 2018: +0.247 | 2019: +0.050 | 2020: +0.271 | 2021: +0.109 | 2022: +0.279 | 2023: +0.075 | 2024: +0.156 | 2025: +0.066 | 2026: -0.398
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.57
- Early IC=+0.1373, Recent IC=+0.0783, 1st-half IC=+0.1901, 2nd-half IC=+0.1010, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.050, Q3_mid=+0.127, Q4=+0.180, Q5_high_vol=+0.174

**`combo_mean__early_order_flow_imbalance__max_down_ret`** (Lock IC=+0.0717, Sharpe=+0.0640)
- Admission: Train IC=+0.1923, Deflated=+0.1939, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.205 | 2016: -0.004 | 2017: +0.144 | 2018: +0.119 | 2019: +0.130 | 2020: +0.072 | 2021: +0.105 | 2022: +0.118 | 2023: +0.072 | 2024: +0.120 | 2025: +0.113 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.029 | 2017: +0.196 | 2018: +0.187 | 2019: +0.267 | 2020: +0.077 | 2021: +0.335 | 2022: +0.337 | 2023: +0.232 | 2024: +0.362 | 2025: +0.098 | 2026: -0.185
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=0.95, Recency ratio=1.11
- Early IC=+0.1004, Recent IC=+0.1114, 1st-half IC=+0.1149, 2nd-half IC=+0.1091, Neg regimes=1/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.136, Q2=-0.016, Q3_mid=+0.144, Q4=+0.131, Q5_high_vol=+0.134

**`combo_min__max_down_ret__close_vs_open_range`** (Lock IC=+0.0988, Sharpe=+0.0640)
- Admission: Train IC=+0.2037, Deflated=+0.2059, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.074 | 2017: +0.215 | 2018: +0.114 | 2019: +0.081 | 2020: +0.123 | 2021: +0.045 | 2022: +0.087 | 2023: +0.086 | 2024: +0.118 | 2025: +0.137 | 2026: +0.025
- Yearly Tail ICs:   2015: +0.341 | 2016: -0.016 | 2017: +0.226 | 2018: +0.176 | 2019: +0.191 | 2020: +0.134 | 2021: +0.288 | 2022: +0.299 | 2023: +0.135 | 2024: +0.183 | 2025: +0.146 | 2026: +0.045
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=0.39
- Early IC=+0.1693, Recent IC=+0.0662, 1st-half IC=+0.1593, 2nd-half IC=+0.0889, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.028, Q3_mid=+0.166, Q4=+0.128, Q5_high_vol=+0.171

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0928, Sharpe=+0.0552)
- Admission: Train IC=+0.2309, Deflated=+0.2323, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.68
- Early IC=+0.1848, Recent IC=+0.1264, 1st-half IC=+0.2142, 2nd-half IC=+0.1186, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.018, Q3_mid=+0.150, Q4=+0.180, Q5_high_vol=+0.246

**`combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0`** (Lock IC=+0.0932, Sharpe=+0.0468)
- Admission: Train IC=+0.2109, Deflated=+0.2119, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.083 | 2017: +0.207 | 2018: +0.178 | 2019: +0.104 | 2020: +0.126 | 2021: +0.111 | 2022: +0.057 | 2023: +0.097 | 2024: +0.118 | 2025: +0.112 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.399 | 2016: +0.105 | 2017: +0.358 | 2018: +0.260 | 2019: +0.167 | 2020: +0.077 | 2021: +0.161 | 2022: +0.130 | 2023: +0.160 | 2024: +0.209 | 2025: +0.071 | 2026: -0.297
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.53
- Early IC=+0.1583, Recent IC=+0.0837, 1st-half IC=+0.1870, 2nd-half IC=+0.1027, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.010, Q3_mid=+0.142, Q4=+0.160, Q5_high_vol=+0.188

**`combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0774, Sharpe=+0.0400)
- Admission: Train IC=+0.2205, Deflated=+0.2218, IR=0.60, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.082 | 2017: +0.247 | 2018: +0.212 | 2019: +0.117 | 2020: +0.157 | 2021: +0.147 | 2022: +0.133 | 2023: +0.059 | 2024: +0.141 | 2025: +0.094 | 2026: -0.048
- Yearly Tail ICs:   2015: +0.225 | 2016: -0.024 | 2017: +0.167 | 2018: +0.325 | 2019: +0.177 | 2020: +0.284 | 2021: +0.240 | 2022: +0.231 | 2023: +0.229 | 2024: +0.243 | 2025: +0.052 | 2026: -0.286
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.80
- Early IC=+0.1741, Recent IC=+0.1399, 1st-half IC=+0.2191, 2nd-half IC=+0.1441, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.046, Q3_mid=+0.173, Q4=+0.188, Q5_high_vol=+0.230

**`combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance`** (Lock IC=+0.0872, Sharpe=+0.0379)
- Admission: Train IC=+0.2685, Deflated=+0.2693, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.015 | 2017: +0.219 | 2018: +0.156 | 2019: +0.125 | 2020: +0.092 | 2021: +0.132 | 2022: +0.113 | 2023: +0.061 | 2024: +0.128 | 2025: +0.140 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.484 | 2016: -0.054 | 2017: +0.213 | 2018: +0.347 | 2019: +0.367 | 2020: +0.035 | 2021: +0.345 | 2022: +0.384 | 2023: +0.185 | 2024: +0.312 | 2025: +0.036 | 2026: -0.125
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.97
- Early IC=+0.1278, Recent IC=+0.1242, 1st-half IC=+0.1744, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.67)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.008, Q3_mid=+0.174, Q4=+0.164, Q5_high_vol=+0.177

**`combo_tri_max__net_volume_flow__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0881, Sharpe=+0.0286)
- Admission: Train IC=+0.1823, Deflated=+0.1833, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.111 | 2017: +0.163 | 2018: +0.200 | 2019: +0.096 | 2020: +0.130 | 2021: +0.087 | 2022: +0.129 | 2023: +0.059 | 2024: +0.101 | 2025: +0.068 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.022 | 2017: +0.133 | 2018: +0.282 | 2019: +0.078 | 2020: +0.079 | 2021: +0.290 | 2022: +0.217 | 2023: +0.099 | 2024: -0.010 | 2025: -0.048 | 2026: -0.272
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.62
- Early IC=+0.1749, Recent IC=+0.1081, 1st-half IC=+0.2063, 2nd-half IC=+0.1117, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.020, Q3_mid=+0.170, Q4=+0.141, Q5_high_vol=+0.220

**`combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0938, Sharpe=+0.0240)
- Admission: Train IC=+0.2059, Deflated=+0.2067, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.122 | 2017: +0.214 | 2018: +0.211 | 2019: +0.088 | 2020: +0.115 | 2021: +0.075 | 2022: +0.140 | 2023: +0.089 | 2024: +0.082 | 2025: +0.080 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.350 | 2017: +0.170 | 2018: +0.272 | 2019: +0.105 | 2020: +0.112 | 2021: +0.131 | 2022: +0.143 | 2023: -0.070 | 2024: +0.109 | 2025: -0.176 | 2026: -0.063
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.48, Recency ratio=0.59
- Early IC=+0.1814, Recent IC=+0.1067, 1st-half IC=+0.2146, 2nd-half IC=+0.1024, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.061, Q3_mid=+0.174, Q4=+0.133, Q5_high_vol=+0.255

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0729, Sharpe=+0.0143)
- Admission: Train IC=+0.1937, Deflated=+0.1948, IR=0.43, Mono=0.67, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.007 | 2017: +0.175 | 2018: +0.224 | 2019: +0.123 | 2020: +0.167 | 2021: +0.165 | 2022: +0.103 | 2023: +0.092 | 2024: +0.111 | 2025: +0.074 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.037 | 2016: +0.163 | 2017: +0.176 | 2018: +0.513 | 2019: +0.189 | 2020: +0.178 | 2021: +0.298 | 2022: +0.005 | 2023: +0.116 | 2024: +0.134 | 2025: -0.103 | 2026: -0.359
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=1.32
- Early IC=+0.1010, Recent IC=+0.1338, 1st-half IC=+0.1644, 2nd-half IC=+0.1419, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.052, Q3_mid=+0.191, Q4=+0.169, Q5_high_vol=+0.197

**`combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend`** (Lock IC=+0.0912, Sharpe=+0.0122)
- Admission: Train IC=+0.2504, Deflated=+0.2515, IR=0.77, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.030 | 2017: +0.202 | 2018: +0.115 | 2019: +0.115 | 2020: +0.119 | 2021: +0.099 | 2022: +0.071 | 2023: +0.124 | 2024: +0.122 | 2025: +0.106 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.294 | 2017: +0.275 | 2018: +0.225 | 2019: +0.284 | 2020: +0.156 | 2021: +0.335 | 2022: +0.259 | 2023: +0.179 | 2024: +0.091 | 2025: +0.219 | 2026: -0.182
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.83
- Early IC=+0.1031, Recent IC=+0.0856, 1st-half IC=+0.1409, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.022, Q3_mid=+0.175, Q4=+0.095, Q5_high_vol=+0.135

**`combo_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0936, Sharpe=+0.0056)
- Admission: Train IC=+0.2337, Deflated=+0.2357, IR=0.59, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.072 | 2017: +0.252 | 2018: +0.190 | 2019: +0.132 | 2020: +0.163 | 2021: +0.095 | 2022: +0.082 | 2023: +0.078 | 2024: +0.137 | 2025: +0.101 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.448 | 2016: +0.074 | 2017: +0.152 | 2018: +0.148 | 2019: +0.252 | 2020: +0.036 | 2021: +0.349 | 2022: +0.227 | 2023: +0.103 | 2024: +0.102 | 2025: +0.158 | 2026: -0.044
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.50
- Early IC=+0.1783, Recent IC=+0.0886, 1st-half IC=+0.2005, 2nd-half IC=+0.1231, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.013, Q3_mid=+0.173, Q4=+0.151, Q5_high_vol=+0.233

### 159915ETF — `single` True Positives

**`combo_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1365, Sharpe=+1.6742)
- Admission: Train IC=+0.2774, Deflated=+0.2787, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.089 | 2017: -0.026 | 2018: +0.119 | 2019: +0.266 | 2020: +0.164 | 2021: +0.126 | 2022: +0.061 | 2023: +0.148 | 2024: +0.110 | 2025: +0.151 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.165 | 2016: +0.147 | 2017: +0.065 | 2018: +0.343 | 2019: +0.519 | 2020: +0.373 | 2021: +0.280 | 2022: +0.209 | 2023: +0.321 | 2024: +0.445 | 2025: +0.225 | 2026: +0.378
- IC CV=0.68, Neg years (linear/tail)=1/0 of 8, Half ratio=1.17, Recency ratio=0.58
- Early IC=+0.1592, Recent IC=+0.0931, 1st-half IC=+0.1349, 2nd-half IC=+0.1582, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.057, Q3_mid=+0.127, Q4=+0.164, Q5_high_vol=+0.201

**`combo_min__star50_limit_proximity_early__volume_price_confirmation`** (Lock IC=+0.1287, Sharpe=+1.6490)
- Admission: Train IC=+0.2682, Deflated=+0.2691, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.071 | 2017: +0.028 | 2018: +0.142 | 2019: +0.182 | 2020: +0.170 | 2021: +0.033 | 2022: +0.055 | 2023: +0.116 | 2024: +0.123 | 2025: +0.102 | 2026: +0.191
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.055 | 2017: +0.007 | 2018: +0.408 | 2019: +0.494 | 2020: +0.328 | 2021: +0.129 | 2022: +0.194 | 2023: +0.124 | 2024: +0.430 | 2025: +0.221 | 2026: +0.418
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.33
- Early IC=+0.1335, Recent IC=+0.0437, 1st-half IC=+0.1221, 2nd-half IC=+0.1123, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.051, Q3_mid=+0.056, Q4=+0.121, Q5_high_vol=+0.207

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1423, Sharpe=+1.5753)
- Admission: Train IC=+0.3059, Deflated=+0.3073, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.080 | 2017: -0.020 | 2018: +0.166 | 2019: +0.242 | 2020: +0.163 | 2021: +0.149 | 2022: +0.086 | 2023: +0.183 | 2024: +0.130 | 2025: +0.156 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.251 | 2016: +0.044 | 2017: +0.068 | 2018: +0.425 | 2019: +0.570 | 2020: +0.329 | 2021: +0.373 | 2022: +0.259 | 2023: +0.409 | 2024: +0.387 | 2025: +0.218 | 2026: +0.286
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.24, Recency ratio=0.87
- Early IC=+0.1356, Recent IC=+0.1176, 1st-half IC=+0.1316, 2nd-half IC=+0.1635, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.075, Q3_mid=+0.162, Q4=+0.167, Q5_high_vol=+0.183

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1361, Sharpe=+1.5551)
- Admission: Train IC=+0.2277, Deflated=+0.2291, IR=0.47, Mono=0.66, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.095 | 2017: +0.026 | 2018: +0.157 | 2019: +0.224 | 2020: +0.126 | 2021: +0.163 | 2022: +0.112 | 2023: +0.178 | 2024: +0.109 | 2025: +0.174 | 2026: +0.064
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.008 | 2017: +0.095 | 2018: +0.307 | 2019: +0.472 | 2020: +0.231 | 2021: +0.351 | 2022: +0.192 | 2023: +0.353 | 2024: +0.426 | 2025: +0.273 | 2026: +0.064
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.87
- Early IC=+0.1580, Recent IC=+0.1374, 1st-half IC=+0.1626, 2nd-half IC=+0.1565, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.081, Q3_mid=+0.158, Q4=+0.170, Q5_high_vol=+0.200

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1354, Sharpe=+1.5192)
- Admission: Train IC=+0.2773, Deflated=+0.2784, IR=0.74, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.116 | 2017: +0.016 | 2018: +0.157 | 2019: +0.214 | 2020: +0.125 | 2021: +0.136 | 2022: +0.098 | 2023: +0.181 | 2024: +0.116 | 2025: +0.185 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.139 | 2017: +0.083 | 2018: +0.330 | 2019: +0.537 | 2020: +0.337 | 2021: +0.279 | 2022: +0.383 | 2023: +0.459 | 2024: +0.309 | 2025: +0.206 | 2026: +0.077
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=0.79
- Early IC=+0.1474, Recent IC=+0.1168, 1st-half IC=+0.1470, 2nd-half IC=+0.1468, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.096, Q3_mid=+0.158, Q4=+0.185, Q5_high_vol=+0.156

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1228, Sharpe=+1.5130)
- Admission: Train IC=+0.2400, Deflated=+0.2409, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.094 | 2017: +0.035 | 2018: +0.170 | 2019: +0.182 | 2020: +0.185 | 2021: +0.051 | 2022: +0.068 | 2023: +0.128 | 2024: +0.091 | 2025: +0.131 | 2026: +0.156
- Yearly Tail ICs:   2015: +0.343 | 2016: +0.085 | 2017: -0.088 | 2018: +0.440 | 2019: +0.444 | 2020: +0.358 | 2021: +0.143 | 2022: -0.001 | 2023: +0.120 | 2024: +0.415 | 2025: +0.176 | 2026: +0.357
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=0.37
- Early IC=+0.1579, Recent IC=+0.0584, 1st-half IC=+0.1457, 2nd-half IC=+0.1241, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.058, Q3_mid=+0.054, Q4=+0.148, Q5_high_vol=+0.241

**`combo_mean__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1208, Sharpe=+1.4577)
- Admission: Train IC=+0.2575, Deflated=+0.2589, IR=0.59, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.120 | 2017: -0.024 | 2018: +0.163 | 2019: +0.230 | 2020: +0.158 | 2021: +0.145 | 2022: +0.107 | 2023: +0.116 | 2024: +0.082 | 2025: +0.143 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.162 | 2017: +0.100 | 2018: +0.372 | 2019: +0.462 | 2020: +0.230 | 2021: +0.299 | 2022: +0.180 | 2023: +0.157 | 2024: +0.447 | 2025: +0.232 | 2026: +0.173
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.11, Recency ratio=0.76
- Early IC=+0.1658, Recent IC=+0.1263, 1st-half IC=+0.1479, 2nd-half IC=+0.1638, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.051, Q3_mid=+0.149, Q4=+0.195, Q5_high_vol=+0.190

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1323, Sharpe=+1.4436)
- Admission: Train IC=+0.2369, Deflated=+0.2383, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.073 | 2017: +0.030 | 2018: +0.131 | 2019: +0.197 | 2020: +0.124 | 2021: +0.154 | 2022: +0.130 | 2023: +0.163 | 2024: +0.118 | 2025: +0.177 | 2026: +0.031
- Yearly Tail ICs:   2015: +0.085 | 2016: +0.128 | 2017: +0.072 | 2018: +0.221 | 2019: +0.542 | 2020: +0.137 | 2021: +0.253 | 2022: +0.330 | 2023: +0.429 | 2024: +0.362 | 2025: +0.155 | 2026: +0.040
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=1.04
- Early IC=+0.1370, Recent IC=+0.1424, 1st-half IC=+0.1462, 2nd-half IC=+0.1550, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.085, Q3_mid=+0.166, Q4=+0.185, Q5_high_vol=+0.175

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1362, Sharpe=+1.4190)
- Admission: Train IC=+0.2651, Deflated=+0.2657, IR=0.50, Mono=0.67, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.125 | 2017: +0.003 | 2018: +0.176 | 2019: +0.241 | 2020: +0.166 | 2021: +0.132 | 2022: +0.075 | 2023: +0.176 | 2024: +0.100 | 2025: +0.155 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.131 | 2017: +0.013 | 2018: +0.409 | 2019: +0.516 | 2020: +0.395 | 2021: +0.241 | 2022: +0.207 | 2023: +0.433 | 2024: +0.402 | 2025: +0.216 | 2026: +0.167
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.56
- Early IC=+0.1854, Recent IC=+0.1035, 1st-half IC=+0.1696, 2nd-half IC=+0.1556, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.067, Q3_mid=+0.126, Q4=+0.222, Q5_high_vol=+0.226

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1220, Sharpe=+1.4110)
- Admission: Train IC=+0.2328, Deflated=+0.2337, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.123 | 2017: +0.035 | 2018: +0.180 | 2019: +0.219 | 2020: +0.160 | 2021: +0.143 | 2022: +0.139 | 2023: +0.127 | 2024: +0.110 | 2025: +0.124 | 2026: +0.139
- Yearly Tail ICs:   2015: +0.150 | 2016: +0.189 | 2017: -0.026 | 2018: +0.414 | 2019: +0.517 | 2020: +0.268 | 2021: +0.193 | 2022: +0.134 | 2023: +0.156 | 2024: +0.298 | 2025: +0.286 | 2026: +0.229
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=1.04, Recency ratio=0.88
- Early IC=+0.1605, Recent IC=+0.1410, 1st-half IC=+0.1628, 2nd-half IC=+0.1688, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.084, Q3_mid=+0.190, Q4=+0.185, Q5_high_vol=+0.203

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1300, Sharpe=+1.4067)
- Admission: Train IC=+0.2710, Deflated=+0.2713, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.142 | 2017: +0.026 | 2018: +0.125 | 2019: +0.195 | 2020: +0.162 | 2021: +0.158 | 2022: +0.116 | 2023: +0.158 | 2024: +0.091 | 2025: +0.170 | 2026: +0.070
- Yearly Tail ICs:   2015: +0.055 | 2016: +0.265 | 2017: +0.064 | 2018: +0.376 | 2019: +0.359 | 2020: +0.250 | 2021: +0.338 | 2022: +0.294 | 2023: +0.175 | 2024: +0.339 | 2025: +0.184 | 2026: +0.257
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.78
- Early IC=+0.1767, Recent IC=+0.1370, 1st-half IC=+0.1620, 2nd-half IC=+0.1648, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.085, Q3_mid=+0.150, Q4=+0.237, Q5_high_vol=+0.179

**`combo_mean__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1219, Sharpe=+1.3598)
- Admission: Train IC=+0.2431, Deflated=+0.2440, IR=0.58, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.090 | 2017: +0.002 | 2018: +0.172 | 2019: +0.207 | 2020: +0.135 | 2021: +0.156 | 2022: +0.118 | 2023: +0.146 | 2024: +0.068 | 2025: +0.156 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.067 | 2017: +0.152 | 2018: +0.389 | 2019: +0.401 | 2020: +0.186 | 2021: +0.387 | 2022: +0.119 | 2023: +0.111 | 2024: +0.399 | 2025: +0.193 | 2026: +0.217
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.87
- Early IC=+0.1583, Recent IC=+0.1370, 1st-half IC=+0.1627, 2nd-half IC=+0.1542, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.063, Q3_mid=+0.128, Q4=+0.203, Q5_high_vol=+0.185

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1267, Sharpe=+1.3544)
- Admission: Train IC=+0.2753, Deflated=+0.2770, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.047 | 2017: +0.048 | 2018: +0.135 | 2019: +0.206 | 2020: +0.147 | 2021: +0.167 | 2022: +0.102 | 2023: +0.173 | 2024: +0.061 | 2025: +0.184 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.060 | 2016: +0.017 | 2017: +0.266 | 2018: +0.319 | 2019: +0.320 | 2020: +0.414 | 2021: +0.350 | 2022: +0.386 | 2023: +0.249 | 2024: +0.271 | 2025: +0.166 | 2026: +0.337
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=1.13
- Early IC=+0.1187, Recent IC=+0.1344, 1st-half IC=+0.1340, 2nd-half IC=+0.1627, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.090, Q3_mid=+0.161, Q4=+0.165, Q5_high_vol=+0.174

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1368, Sharpe=+1.3236)
- Admission: Train IC=+0.2813, Deflated=+0.2825, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.065 | 2017: -0.009 | 2018: +0.146 | 2019: +0.236 | 2020: +0.133 | 2021: +0.128 | 2022: +0.108 | 2023: +0.185 | 2024: +0.124 | 2025: +0.159 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.044 | 2017: +0.019 | 2018: +0.348 | 2019: +0.511 | 2020: +0.192 | 2021: +0.289 | 2022: +0.295 | 2023: +0.474 | 2024: +0.368 | 2025: +0.152 | 2026: +0.207
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.18, Recency ratio=0.88
- Early IC=+0.1341, Recent IC=+0.1181, 1st-half IC=+0.1297, 2nd-half IC=+0.1532, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.083, Q3_mid=+0.151, Q4=+0.149, Q5_high_vol=+0.176

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1458, Sharpe=+1.3138)
- Admission: Train IC=+0.3068, Deflated=+0.3083, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.046 | 2017: +0.008 | 2018: +0.125 | 2019: +0.235 | 2020: +0.126 | 2021: +0.142 | 2022: +0.096 | 2023: +0.183 | 2024: +0.125 | 2025: +0.180 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.080 | 2017: +0.102 | 2018: +0.356 | 2019: +0.519 | 2020: +0.307 | 2021: +0.332 | 2022: +0.401 | 2023: +0.342 | 2024: +0.335 | 2025: +0.159 | 2026: +0.364
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.00
- Early IC=+0.1186, Recent IC=+0.1187, 1st-half IC=+0.1228, 2nd-half IC=+0.1548, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.105, Q3_mid=+0.162, Q4=+0.149, Q5_high_vol=+0.148

**`combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1333, Sharpe=+1.3096)
- Admission: Train IC=+0.2517, Deflated=+0.2530, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.039 | 2017: -0.001 | 2018: +0.048 | 2019: +0.155 | 2020: +0.081 | 2021: +0.168 | 2022: +0.098 | 2023: +0.149 | 2024: +0.082 | 2025: +0.187 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.158 | 2016: +0.196 | 2017: +0.168 | 2018: +0.209 | 2019: +0.328 | 2020: +0.219 | 2021: +0.278 | 2022: +0.282 | 2023: +0.341 | 2024: +0.372 | 2025: +0.239 | 2026: +0.150
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=1.32, Recency ratio=1.17
- Early IC=+0.1143, Recent IC=+0.1332, 1st-half IC=+0.1007, 2nd-half IC=+0.1325, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.046, Q3_mid=+0.132, Q4=+0.169, Q5_high_vol=+0.110

**`combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1385, Sharpe=+1.2999)
- Admission: Train IC=+0.2361, Deflated=+0.2375, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.041 | 2017: -0.003 | 2018: +0.045 | 2019: +0.156 | 2020: +0.089 | 2021: +0.150 | 2022: +0.115 | 2023: +0.164 | 2024: +0.081 | 2025: +0.195 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.058 | 2016: +0.210 | 2017: +0.146 | 2018: +0.212 | 2019: +0.261 | 2020: +0.209 | 2021: +0.246 | 2022: +0.275 | 2023: +0.359 | 2024: +0.326 | 2025: +0.192 | 2026: +0.109
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=1.37, Recency ratio=1.20
- Early IC=+0.1127, Recent IC=+0.1351, 1st-half IC=+0.0986, 2nd-half IC=+0.1355, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.041, Q3_mid=+0.132, Q4=+0.171, Q5_high_vol=+0.113

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1295, Sharpe=+1.2978)
- Admission: Train IC=+0.2672, Deflated=+0.2686, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.092 | 2017: -0.005 | 2018: +0.166 | 2019: +0.223 | 2020: +0.135 | 2021: +0.148 | 2022: +0.127 | 2023: +0.186 | 2024: +0.081 | 2025: +0.182 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.022 | 2017: +0.048 | 2018: +0.386 | 2019: +0.452 | 2020: +0.337 | 2021: +0.367 | 2022: +0.294 | 2023: +0.467 | 2024: +0.301 | 2025: +0.195 | 2026: +0.190
- IC CV=0.48, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=0.98
- Early IC=+0.1402, Recent IC=+0.1370, 1st-half IC=+0.1407, 2nd-half IC=+0.1637, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.094, Q3_mid=+0.159, Q4=+0.180, Q5_high_vol=+0.174

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1273, Sharpe=+1.2414)
- Admission: Train IC=+0.2283, Deflated=+0.2295, IR=0.60, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.071 | 2017: +0.024 | 2018: +0.078 | 2019: +0.187 | 2020: +0.141 | 2021: +0.152 | 2022: +0.122 | 2023: +0.185 | 2024: +0.105 | 2025: +0.192 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.154 | 2017: +0.225 | 2018: +0.204 | 2019: +0.289 | 2020: +0.228 | 2021: +0.280 | 2022: +0.283 | 2023: +0.365 | 2024: +0.207 | 2025: +0.317 | 2026: -0.070
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.20, Recency ratio=0.99
- Early IC=+0.1385, Recent IC=+0.1373, 1st-half IC=+0.1280, 2nd-half IC=+0.1534, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.099, Q3_mid=+0.149, Q4=+0.139, Q5_high_vol=+0.181

**`combo_rank_min__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1345, Sharpe=+1.2143)
- Admission: Train IC=+0.2548, Deflated=+0.2555, IR=0.65, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.068 | 2017: +0.003 | 2018: +0.069 | 2019: +0.212 | 2020: +0.149 | 2021: +0.125 | 2022: +0.111 | 2023: +0.156 | 2024: +0.108 | 2025: +0.170 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.140 | 2017: +0.069 | 2018: +0.291 | 2019: +0.442 | 2020: +0.162 | 2021: +0.354 | 2022: +0.262 | 2023: +0.226 | 2024: +0.237 | 2025: +0.120 | 2026: +0.056
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=0.81
- Early IC=+0.1458, Recent IC=+0.1187, 1st-half IC=+0.1263, 2nd-half IC=+0.1551, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.080, Q3_mid=+0.142, Q4=+0.173, Q5_high_vol=+0.162

**`combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1313, Sharpe=+1.2050)
- Admission: Train IC=+0.2599, Deflated=+0.2610, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.113 | 2017: +0.022 | 2018: +0.157 | 2019: +0.202 | 2020: +0.120 | 2021: +0.170 | 2022: +0.135 | 2023: +0.163 | 2024: +0.093 | 2025: +0.181 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.137 | 2016: +0.125 | 2017: +0.087 | 2018: +0.265 | 2019: +0.338 | 2020: +0.203 | 2021: +0.376 | 2022: +0.277 | 2023: +0.281 | 2024: +0.382 | 2025: +0.225 | 2026: +0.018
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.88
- Early IC=+0.1741, Recent IC=+0.1523, 1st-half IC=+0.1704, 2nd-half IC=+0.1570, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.073, Q3_mid=+0.152, Q4=+0.199, Q5_high_vol=+0.210

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1402, Sharpe=+1.1873)
- Admission: Train IC=+0.2355, Deflated=+0.2365, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.21, Recency ratio=1.23
- Early IC=+0.1261, Recent IC=+0.1550, 1st-half IC=+0.1196, 2nd-half IC=+0.1442, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.053, Q3_mid=+0.134, Q4=+0.212, Q5_high_vol=+0.129

**`combo_min__first_bar_return__limit_down_proximity_early`** (Lock IC=+0.1216, Sharpe=+1.1418)
- Admission: Train IC=+0.2454, Deflated=+0.2463, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.068 | 2017: -0.024 | 2018: +0.085 | 2019: +0.246 | 2020: +0.125 | 2021: +0.101 | 2022: +0.053 | 2023: +0.125 | 2024: +0.087 | 2025: +0.147 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.256 | 2016: +0.015 | 2017: +0.040 | 2018: +0.238 | 2019: +0.522 | 2020: +0.092 | 2021: +0.329 | 2022: +0.244 | 2023: +0.160 | 2024: +0.444 | 2025: +0.053 | 2026: +0.220
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=0.52
- Early IC=+0.1483, Recent IC=+0.0772, 1st-half IC=+0.1191, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.049, Q3_mid=+0.106, Q4=+0.108, Q5_high_vol=+0.169

**`opening_drive_thrust_ratio`** (Lock IC=+0.1176, Sharpe=+1.1307)
- Admission: Train IC=+0.2418, Deflated=+0.2438, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.045 | 2017: +0.030 | 2018: +0.088 | 2019: +0.188 | 2020: +0.095 | 2021: +0.133 | 2022: +0.085 | 2023: +0.199 | 2024: +0.100 | 2025: +0.166 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.041 | 2017: -0.006 | 2018: +0.191 | 2019: +0.375 | 2020: +0.225 | 2021: +0.278 | 2022: +0.275 | 2023: +0.459 | 2024: +0.198 | 2025: +0.229 | 2026: -0.077
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=1.21, Recency ratio=0.99
- Early IC=+0.1098, Recent IC=+0.1089, 1st-half IC=+0.1060, 2nd-half IC=+0.1284, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.079, Q3_mid=+0.156, Q4=+0.067, Q5_high_vol=+0.186

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1181, Sharpe=+1.1200)
- Admission: Train IC=+0.2557, Deflated=+0.2570, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.134 | 2017: +0.045 | 2018: +0.085 | 2019: +0.192 | 2020: +0.139 | 2021: +0.167 | 2022: +0.124 | 2023: +0.164 | 2024: +0.052 | 2025: +0.187 | 2026: +0.052
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.258 | 2017: +0.194 | 2018: +0.349 | 2019: +0.297 | 2020: +0.173 | 2021: +0.397 | 2022: +0.176 | 2023: +0.293 | 2024: +0.239 | 2025: +0.306 | 2026: +0.128
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=0.80
- Early IC=+0.1829, Recent IC=+0.1458, 1st-half IC=+0.1520, 2nd-half IC=+0.1606, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.097, Q3_mid=+0.161, Q4=+0.131, Q5_high_vol=+0.209

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1277, Sharpe=+1.0889)
- Admission: Train IC=+0.2094, Deflated=+0.2090, IR=0.47, Mono=0.67, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.101 | 2017: +0.040 | 2018: +0.088 | 2019: +0.144 | 2020: +0.062 | 2021: +0.147 | 2022: +0.167 | 2023: +0.137 | 2024: +0.139 | 2025: +0.122 | 2026: +0.090
- Yearly Tail ICs:   2015: -0.093 | 2016: +0.241 | 2017: +0.080 | 2018: +0.334 | 2019: +0.305 | 2020: +0.198 | 2021: +0.227 | 2022: +0.365 | 2023: +0.308 | 2024: +0.331 | 2025: -0.022 | 2026: +0.197
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=1.18, Recency ratio=1.34
- Early IC=+0.1168, Recent IC=+0.1569, 1st-half IC=+0.1116, 2nd-half IC=+0.1315, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.001, Q2=+0.089, Q3_mid=+0.096, Q4=+0.220, Q5_high_vol=+0.141

**`combo_max__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0793, Sharpe=+1.0689)
- Admission: Train IC=+0.2195, Deflated=+0.2205, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.112 | 2017: +0.039 | 2018: +0.115 | 2019: +0.180 | 2020: +0.175 | 2021: +0.144 | 2022: +0.077 | 2023: +0.097 | 2024: +0.067 | 2025: +0.127 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.110 | 2017: +0.016 | 2018: +0.290 | 2019: +0.326 | 2020: +0.205 | 2021: +0.336 | 2022: +0.176 | 2023: +0.263 | 2024: +0.342 | 2025: +0.085 | 2026: -0.081
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=0.70
- Early IC=+0.1577, Recent IC=+0.1107, 1st-half IC=+0.1444, 2nd-half IC=+0.1481, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.086, Q3_mid=+0.154, Q4=+0.094, Q5_high_vol=+0.235

**`combo_mean__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=+0.1165, Sharpe=+1.0610)
- Admission: Train IC=+0.1766, Deflated=+0.1784, IR=0.36, Mono=0.66, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.070 | 2017: +0.053 | 2018: +0.089 | 2019: +0.167 | 2020: +0.147 | 2021: +0.105 | 2022: +0.071 | 2023: +0.147 | 2024: +0.082 | 2025: +0.162 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.406 | 2016: -0.182 | 2017: +0.004 | 2018: +0.295 | 2019: +0.334 | 2020: +0.155 | 2021: +0.199 | 2022: +0.122 | 2023: +0.466 | 2024: +0.221 | 2025: +0.305 | 2026: +0.022
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=1.00, Recency ratio=0.60
- Early IC=+0.1480, Recent IC=+0.0882, 1st-half IC=+0.1261, 2nd-half IC=+0.1264, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.062, Q3_mid=+0.131, Q4=+0.069, Q5_high_vol=+0.229

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.1076, Sharpe=+1.0604)
- Admission: Train IC=+0.2058, Deflated=+0.2072, IR=0.50, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.086 | 2017: +0.022 | 2018: +0.080 | 2019: +0.201 | 2020: +0.111 | 2021: +0.093 | 2022: +0.097 | 2023: +0.171 | 2024: +0.082 | 2025: +0.083 | 2026: +0.068
- Yearly Tail ICs:   2015: +0.177 | 2016: +0.098 | 2017: +0.162 | 2018: +0.201 | 2019: +0.284 | 2020: -0.020 | 2021: +0.334 | 2022: +0.233 | 2023: +0.365 | 2024: +0.208 | 2025: +0.047 | 2026: -0.048
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.08, Recency ratio=0.69
- Early IC=+0.1368, Recent IC=+0.0949, 1st-half IC=+0.1178, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.83)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.066, Q3_mid=+0.119, Q4=+0.107, Q5_high_vol=+0.195

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1260, Sharpe=+1.0555)
- Admission: Train IC=+0.2510, Deflated=+0.2517, IR=0.53, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.103 | 2017: +0.023 | 2018: +0.127 | 2019: +0.160 | 2020: +0.154 | 2021: +0.167 | 2022: +0.157 | 2023: +0.140 | 2024: +0.089 | 2025: +0.179 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.005 | 2016: +0.249 | 2017: +0.070 | 2018: +0.325 | 2019: +0.351 | 2020: +0.181 | 2021: +0.386 | 2022: +0.252 | 2023: +0.141 | 2024: +0.292 | 2025: +0.142 | 2026: +0.114
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.19, Recency ratio=1.11
- Early IC=+0.1465, Recent IC=+0.1621, 1st-half IC=+0.1392, 2nd-half IC=+0.1659, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.078, Q3_mid=+0.155, Q4=+0.251, Q5_high_vol=+0.163

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1086, Sharpe=+1.0439)
- Admission: Train IC=+0.2021, Deflated=+0.2034, IR=0.51, Mono=0.68, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.096 | 2017: +0.053 | 2018: +0.123 | 2019: +0.180 | 2020: +0.121 | 2021: +0.130 | 2022: +0.097 | 2023: +0.179 | 2024: +0.078 | 2025: +0.143 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.076 | 2017: +0.129 | 2018: +0.289 | 2019: +0.277 | 2020: +0.143 | 2021: +0.305 | 2022: +0.176 | 2023: +0.530 | 2024: +0.211 | 2025: +0.143 | 2026: -0.173
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.77
- Early IC=+0.1485, Recent IC=+0.1136, 1st-half IC=+0.1437, 2nd-half IC=+0.1326, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.063, Q3_mid=+0.159, Q4=+0.089, Q5_high_vol=+0.229

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1268, Sharpe=+1.0353)
- Admission: Train IC=+0.2580, Deflated=+0.2589, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.073 | 2017: -0.020 | 2018: +0.100 | 2019: +0.254 | 2020: +0.122 | 2021: +0.109 | 2022: +0.080 | 2023: +0.148 | 2024: +0.090 | 2025: +0.155 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.072 | 2017: +0.019 | 2018: +0.277 | 2019: +0.481 | 2020: +0.204 | 2021: +0.300 | 2022: +0.244 | 2023: +0.203 | 2024: +0.379 | 2025: +0.089 | 2026: +0.270
- IC CV=0.70, Neg years (linear/tail)=1/0 of 8, Half ratio=1.05, Recency ratio=0.61
- Early IC=+0.1550, Recent IC=+0.0948, 1st-half IC=+0.1347, 2nd-half IC=+0.1421, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.049, Q3_mid=+0.100, Q4=+0.151, Q5_high_vol=+0.189

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0`** (Lock IC=+0.1211, Sharpe=+1.0186)
- Admission: Train IC=+0.2557, Deflated=+0.2569, IR=0.49, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.149 | 2017: -0.005 | 2018: +0.182 | 2019: +0.221 | 2020: +0.157 | 2021: +0.162 | 2022: +0.109 | 2023: +0.140 | 2024: +0.077 | 2025: +0.163 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.088 | 2017: +0.128 | 2018: +0.268 | 2019: +0.369 | 2020: +0.278 | 2021: +0.444 | 2022: +0.170 | 2023: +0.222 | 2024: +0.319 | 2025: +0.218 | 2026: +0.186
- IC CV=0.46, Neg years (linear/tail)=1/0 of 8, Half ratio=0.95, Recency ratio=0.71
- Early IC=+0.1913, Recent IC=+0.1355, 1st-half IC=+0.1720, 2nd-half IC=+0.1636, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.059, Q3_mid=+0.147, Q4=+0.190, Q5_high_vol=+0.232

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1314, Sharpe=+1.0098)
- Admission: Train IC=+0.2176, Deflated=+0.2185, IR=0.50, Mono=0.67, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.104 | 2017: +0.021 | 2018: +0.043 | 2019: +0.114 | 2020: +0.142 | 2021: +0.146 | 2022: +0.098 | 2023: +0.152 | 2024: +0.105 | 2025: +0.198 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.068 | 2016: +0.099 | 2017: +0.093 | 2018: +0.187 | 2019: +0.202 | 2020: +0.106 | 2021: +0.426 | 2022: +0.270 | 2023: +0.165 | 2024: +0.319 | 2025: +0.157 | 2026: -0.116
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.24, Recency ratio=0.87
- Early IC=+0.1398, Recent IC=+0.1220, 1st-half IC=+0.1034, 2nd-half IC=+0.1282, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.083, Q3_mid=+0.134, Q4=+0.128, Q5_high_vol=+0.152

**`combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1292, Sharpe=+0.9902)
- Admission: Train IC=+0.2574, Deflated=+0.2578, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.088 | 2017: +0.015 | 2018: +0.119 | 2019: +0.222 | 2020: +0.119 | 2021: +0.114 | 2022: +0.076 | 2023: +0.145 | 2024: +0.098 | 2025: +0.159 | 2026: +0.093
- Yearly Tail ICs:   2015: +0.186 | 2016: +0.083 | 2017: +0.031 | 2018: +0.313 | 2019: +0.464 | 2020: +0.173 | 2021: +0.247 | 2022: +0.282 | 2023: +0.304 | 2024: +0.376 | 2025: +0.090 | 2026: +0.185
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.56
- Early IC=+0.1700, Recent IC=+0.0948, 1st-half IC=+0.1524, 2nd-half IC=+0.1350, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.068, Q3_mid=+0.112, Q4=+0.191, Q5_high_vol=+0.186

**`combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1187, Sharpe=+0.9375)
- Admission: Train IC=+0.2607, Deflated=+0.2614, IR=0.67, Mono=0.78, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.113 | 2017: -0.005 | 2018: +0.153 | 2019: +0.238 | 2020: +0.149 | 2021: +0.127 | 2022: +0.102 | 2023: +0.135 | 2024: +0.074 | 2025: +0.153 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.090 | 2017: +0.064 | 2018: +0.342 | 2019: +0.459 | 2020: +0.231 | 2021: +0.294 | 2022: +0.243 | 2023: +0.207 | 2024: +0.376 | 2025: +0.128 | 2026: +0.250
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.93, Recency ratio=0.65
- Early IC=+0.1803, Recent IC=+0.1166, 1st-half IC=+0.1676, 2nd-half IC=+0.1556, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.067, Q3_mid=+0.100, Q4=+0.200, Q5_high_vol=+0.228

**`combo_clamp_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1122, Sharpe=+0.9216)
- Admission: Train IC=+0.2445, Deflated=+0.2461, IR=0.45, Mono=0.68, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.028 | 2017: +0.024 | 2018: +0.079 | 2019: +0.180 | 2020: +0.093 | 2021: +0.156 | 2022: +0.157 | 2023: +0.147 | 2024: +0.062 | 2025: +0.190 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.060 | 2016: +0.298 | 2017: +0.113 | 2018: +0.102 | 2019: +0.416 | 2020: +0.217 | 2021: +0.171 | 2022: +0.370 | 2023: +0.364 | 2024: -0.012 | 2025: +0.199 | 2026: -0.144
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=1.32, Recency ratio=1.45
- Early IC=+0.1082, Recent IC=+0.1564, 1st-half IC=+0.1126, 2nd-half IC=+0.1484, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.080, Q3_mid=+0.142, Q4=+0.164, Q5_high_vol=+0.156

**`combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1272, Sharpe=+0.9212)
- Admission: Train IC=+0.2362, Deflated=+0.2363, IR=0.52, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.138 | 2017: +0.017 | 2018: +0.060 | 2019: +0.172 | 2020: +0.151 | 2021: +0.110 | 2022: +0.088 | 2023: +0.158 | 2024: +0.083 | 2025: +0.162 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.231 | 2017: +0.139 | 2018: +0.307 | 2019: +0.374 | 2020: +0.139 | 2021: +0.301 | 2022: +0.277 | 2023: +0.168 | 2024: +0.208 | 2025: +0.136 | 2026: +0.255
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.56
- Early IC=+0.1777, Recent IC=+0.0992, 1st-half IC=+0.1501, 2nd-half IC=+0.1395, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.042, Q3_mid=+0.150, Q4=+0.183, Q5_high_vol=+0.158

**`combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__star50_limit_proximity_early`** (Lock IC=+0.1344, Sharpe=+0.9145)
- Admission: Train IC=+0.2060, Deflated=+0.2061, IR=0.48, Mono=0.67, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.084 | 2017: -0.003 | 2018: +0.062 | 2019: +0.161 | 2020: +0.120 | 2021: +0.104 | 2022: +0.139 | 2023: +0.123 | 2024: +0.111 | 2025: +0.138 | 2026: +0.173
- Yearly Tail ICs:   2015: +0.064 | 2016: +0.224 | 2017: +0.119 | 2018: +0.308 | 2019: +0.237 | 2020: +0.130 | 2021: +0.268 | 2022: +0.151 | 2023: +0.005 | 2024: +0.170 | 2025: -0.033 | 2026: +0.341
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.20, Recency ratio=0.92
- Early IC=+0.1323, Recent IC=+0.1213, 1st-half IC=+0.1155, 2nd-half IC=+0.1384, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.055, Q3_mid=+0.128, Q4=+0.214, Q5_high_vol=+0.102

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1056, Sharpe=+0.8986)
- Admission: Train IC=+0.1982, Deflated=+0.1997, IR=0.53, Mono=0.67, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.089 | 2017: +0.040 | 2018: +0.116 | 2019: +0.193 | 2020: +0.112 | 2021: +0.132 | 2022: +0.108 | 2023: +0.173 | 2024: +0.082 | 2025: +0.141 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.094 | 2016: +0.071 | 2017: +0.142 | 2018: +0.279 | 2019: +0.282 | 2020: +0.147 | 2021: +0.311 | 2022: +0.177 | 2023: +0.528 | 2024: +0.195 | 2025: +0.117 | 2026: -0.193
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.88
- Early IC=+0.1364, Recent IC=+0.1202, 1st-half IC=+0.1370, 2nd-half IC=+0.1379, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.075, Q3_mid=+0.170, Q4=+0.089, Q5_high_vol=+0.210

**`combo_rank_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1033, Sharpe=+0.8765)
- Admission: Train IC=+0.2157, Deflated=+0.2170, IR=0.40, Mono=0.65, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.103 | 2017: +0.026 | 2018: +0.130 | 2019: +0.174 | 2020: +0.125 | 2021: +0.147 | 2022: +0.083 | 2023: +0.182 | 2024: +0.058 | 2025: +0.150 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.214 | 2016: +0.091 | 2017: +0.090 | 2018: +0.367 | 2019: +0.336 | 2020: +0.148 | 2021: +0.306 | 2022: +0.134 | 2023: +0.354 | 2024: +0.119 | 2025: +0.364 | 2026: -0.019
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.70
- Early IC=+0.1641, Recent IC=+0.1152, 1st-half IC=+0.1424, 2nd-half IC=+0.1341, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.068, Q3_mid=+0.120, Q4=+0.123, Q5_high_vol=+0.234

**`combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=+0.0890, Sharpe=+0.8526)
- Admission: Train IC=+0.1816, Deflated=+0.1830, IR=0.43, Mono=0.68, p=0.0002, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.094 | 2017: +0.029 | 2018: +0.096 | 2019: +0.190 | 2020: +0.181 | 2021: +0.137 | 2022: +0.037 | 2023: +0.119 | 2024: +0.055 | 2025: +0.151 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.340 | 2016: -0.094 | 2017: +0.061 | 2018: +0.226 | 2019: +0.360 | 2020: +0.218 | 2021: +0.186 | 2022: +0.182 | 2023: +0.294 | 2024: +0.222 | 2025: +0.236 | 2026: +0.190
- IC CV=0.55, Neg years (linear/tail)=0/1 of 8, Half ratio=1.02, Recency ratio=0.54
- Early IC=+0.1619, Recent IC=+0.0873, 1st-half IC=+0.1377, 2nd-half IC=+0.1402, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.093, Q3_mid=+0.176, Q4=+0.056, Q5_high_vol=+0.238

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1129, Sharpe=+0.7706)
- Admission: Train IC=+0.2025, Deflated=+0.2048, IR=0.36, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.078 | 2017: +0.024 | 2018: +0.097 | 2019: +0.192 | 2020: +0.108 | 2021: +0.138 | 2022: +0.072 | 2023: +0.171 | 2024: +0.085 | 2025: +0.184 | 2026: -0.048
- Yearly Tail ICs:   2015: +0.369 | 2016: +0.086 | 2017: -0.001 | 2018: +0.149 | 2019: +0.365 | 2020: +0.193 | 2021: +0.109 | 2022: +0.089 | 2023: +0.407 | 2024: +0.340 | 2025: +0.246 | 2026: -0.189
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=0.99, Recency ratio=0.67
- Early IC=+0.1552, Recent IC=+0.1048, 1st-half IC=+0.1320, 2nd-half IC=+0.1304, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.060, Q3_mid=+0.140, Q4=+0.116, Q5_high_vol=+0.211

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.1021, Sharpe=+0.7660)
- Admission: Train IC=+0.1849, Deflated=+0.1866, IR=0.38, Mono=0.66, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.082 | 2017: +0.057 | 2018: +0.064 | 2019: +0.171 | 2020: +0.054 | 2021: +0.223 | 2022: +0.082 | 2023: +0.157 | 2024: +0.085 | 2025: +0.170 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.026 | 2016: +0.056 | 2017: +0.221 | 2018: +0.209 | 2019: +0.318 | 2020: -0.003 | 2021: +0.386 | 2022: +0.240 | 2023: +0.308 | 2024: +0.236 | 2025: +0.195 | 2026: -0.249
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=1.12, Recency ratio=1.20
- Early IC=+0.1272, Recent IC=+0.1528, 1st-half IC=+0.1207, 2nd-half IC=+0.1356, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.83)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.067, Q3_mid=+0.171, Q4=+0.119, Q5_high_vol=+0.164

**`combo_rel_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.1187, Sharpe=+0.7449)
- Admission: Train IC=+0.1990, Deflated=+0.2002, IR=0.47, Mono=0.70, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.089 | 2017: +0.028 | 2018: +0.078 | 2019: +0.194 | 2020: +0.105 | 2021: +0.096 | 2022: +0.099 | 2023: +0.179 | 2024: +0.083 | 2025: +0.105 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.233 | 2016: +0.022 | 2017: +0.201 | 2018: +0.176 | 2019: +0.338 | 2020: -0.077 | 2021: +0.330 | 2022: +0.222 | 2023: +0.382 | 2024: +0.154 | 2025: +0.067 | 2026: -0.049
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=1.05, Recency ratio=0.69
- Early IC=+0.1405, Recent IC=+0.0975, 1st-half IC=+0.1183, 2nd-half IC=+0.1239, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.83)
- Regime ICs: Q1_low_vol=+0.057, Q2=+0.064, Q3_mid=+0.121, Q4=+0.094, Q5_high_vol=+0.185

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return`** (Lock IC=+0.0981, Sharpe=+0.7118)
- Admission: Train IC=+0.2334, Deflated=+0.2349, IR=0.57, Mono=0.75, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.097 | 2017: +0.116 | 2018: +0.118 | 2019: +0.166 | 2020: +0.098 | 2021: +0.086 | 2022: +0.050 | 2023: +0.137 | 2024: +0.079 | 2025: +0.105 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.241 | 2017: +0.191 | 2018: +0.002 | 2019: +0.206 | 2020: +0.304 | 2021: +0.070 | 2022: +0.328 | 2023: +0.196 | 2024: +0.220 | 2025: -0.030 | 2026: +0.033
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.52
- Early IC=+0.1298, Recent IC=+0.0680, 1st-half IC=+0.1388, 2nd-half IC=+0.1047, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.150, Q3_mid=+0.164, Q4=+0.094, Q5_high_vol=+0.106

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0884, Sharpe=+0.6934)
- Admission: Train IC=+0.1851, Deflated=+0.1865, IR=0.43, Mono=0.68, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.069 | 2017: +0.088 | 2018: +0.148 | 2019: +0.164 | 2020: +0.119 | 2021: +0.172 | 2022: +0.077 | 2023: +0.186 | 2024: -0.009 | 2025: +0.148 | 2026: +0.032
- Yearly Tail ICs:   2015: +0.236 | 2016: -0.107 | 2017: +0.289 | 2018: +0.193 | 2019: +0.087 | 2020: +0.165 | 2021: +0.320 | 2022: +0.139 | 2023: +0.337 | 2024: -0.017 | 2025: +0.219 | 2026: +0.121
- IC CV=0.32, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=1.05
- Early IC=+0.1187, Recent IC=+0.1242, 1st-half IC=+0.1438, 2nd-half IC=+0.1370, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.077, Q3_mid=+0.151, Q4=+0.070, Q5_high_vol=+0.208

**`combo_ifelse__gap_pct__max_up_ret__bar_ret_0`** (Lock IC=+0.0817, Sharpe=+0.6895)
- Admission: Train IC=+0.1802, Deflated=+0.1801, IR=0.49, Mono=0.68, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.166 | 2017: +0.048 | 2018: +0.124 | 2019: +0.138 | 2020: +0.121 | 2021: +0.141 | 2022: +0.077 | 2023: +0.163 | 2024: +0.017 | 2025: +0.120 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.171 | 2016: +0.116 | 2017: +0.258 | 2018: +0.240 | 2019: +0.094 | 2020: +0.042 | 2021: +0.333 | 2022: +0.144 | 2023: +0.211 | 2024: +0.175 | 2025: +0.225 | 2026: +0.127
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.61
- Early IC=+0.1791, Recent IC=+0.1091, 1st-half IC=+0.1702, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.097, Q2=+0.049, Q3_mid=+0.140, Q4=+0.116, Q5_high_vol=+0.208

**`combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration`** (Lock IC=+0.0903, Sharpe=+0.6870)
- Admission: Train IC=+0.2176, Deflated=+0.2193, IR=0.43, Mono=0.65, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.134 | 2017: +0.004 | 2018: +0.167 | 2019: +0.217 | 2020: +0.139 | 2021: +0.112 | 2022: +0.086 | 2023: +0.131 | 2024: +0.060 | 2025: +0.126 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.192 | 2016: +0.042 | 2017: +0.057 | 2018: +0.310 | 2019: +0.514 | 2020: -0.015 | 2021: +0.220 | 2022: +0.199 | 2023: +0.180 | 2024: +0.235 | 2025: +0.307 | 2026: -0.132
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=1.02, Recency ratio=0.65
- Early IC=+0.1528, Recent IC=+0.0990, 1st-half IC=+0.1348, 2nd-half IC=+0.1381, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.059, Q3_mid=+0.166, Q4=+0.059, Q5_high_vol=+0.246

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=+0.0991, Sharpe=+0.6764)
- Admission: Train IC=+0.2286, Deflated=+0.2301, IR=0.47, Mono=0.68, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.144 | 2017: +0.039 | 2018: +0.090 | 2019: +0.170 | 2020: +0.123 | 2021: +0.182 | 2022: +0.107 | 2023: +0.162 | 2024: +0.076 | 2025: +0.169 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.110 | 2017: +0.207 | 2018: +0.247 | 2019: +0.212 | 2020: +0.075 | 2021: +0.387 | 2022: +0.280 | 2023: +0.372 | 2024: +0.081 | 2025: +0.269 | 2026: -0.309
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=0.90
- Early IC=+0.1622, Recent IC=+0.1453, 1st-half IC=+0.1386, 2nd-half IC=+0.1463, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.097, Q2=+0.071, Q3_mid=+0.153, Q4=+0.110, Q5_high_vol=+0.206

**`combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return`** (Lock IC=+0.0909, Sharpe=+0.6701)
- Admission: Train IC=+0.2197, Deflated=+0.2201, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.207 | 2017: +0.086 | 2018: +0.101 | 2019: +0.128 | 2020: +0.105 | 2021: +0.057 | 2022: +0.052 | 2023: +0.102 | 2024: +0.092 | 2025: +0.077 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.095 | 2016: +0.375 | 2017: +0.136 | 2018: +0.107 | 2019: +0.291 | 2020: +0.078 | 2021: +0.135 | 2022: +0.301 | 2023: +0.208 | 2024: +0.306 | 2025: -0.081 | 2026: +0.042
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.29
- Early IC=+0.1905, Recent IC=+0.0546, 1st-half IC=+0.1653, 2nd-half IC=+0.0884, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.138, Q3_mid=+0.147, Q4=+0.148, Q5_high_vol=+0.101

**`combo_z_sum__max_up_ret__gap_pct`** (Lock IC=+0.1357, Sharpe=+0.6634)
- Admission: Train IC=+0.2277, Deflated=+0.2280, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.097 | 2017: +0.007 | 2018: +0.133 | 2019: +0.159 | 2020: +0.145 | 2021: +0.152 | 2022: +0.164 | 2023: +0.128 | 2024: +0.110 | 2025: +0.162 | 2026: +0.140
- Yearly Tail ICs:   2015: -0.053 | 2016: +0.265 | 2017: +0.091 | 2018: +0.337 | 2019: +0.277 | 2020: +0.151 | 2021: +0.345 | 2022: +0.175 | 2023: +0.011 | 2024: +0.230 | 2025: +0.048 | 2026: +0.247
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=1.18, Recency ratio=1.10
- Early IC=+0.1436, Recent IC=+0.1580, 1st-half IC=+0.1388, 2nd-half IC=+0.1638, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.076, Q3_mid=+0.137, Q4=+0.273, Q5_high_vol=+0.143

**`combo_rank_max__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.1046, Sharpe=+0.6295)
- Admission: Train IC=+0.1837, Deflated=+0.1855, IR=0.46, Mono=0.66, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.115 | 2017: +0.028 | 2018: +0.107 | 2019: +0.198 | 2020: +0.109 | 2021: +0.153 | 2022: +0.071 | 2023: +0.183 | 2024: +0.085 | 2025: +0.136 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.327 | 2016: -0.015 | 2017: +0.187 | 2018: +0.304 | 2019: +0.229 | 2020: +0.099 | 2021: +0.324 | 2022: +0.124 | 2023: +0.387 | 2024: +0.089 | 2025: +0.255 | 2026: -0.089
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.91, Recency ratio=0.68
- Early IC=+0.1631, Recent IC=+0.1101, 1st-half IC=+0.1438, 2nd-half IC=+0.1311, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.070, Q3_mid=+0.119, Q4=+0.083, Q5_high_vol=+0.256

**`combo_rel_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.1130, Sharpe=+0.6257)
- Admission: Train IC=+0.2203, Deflated=+0.2208, IR=0.46, Mono=0.68, p=0.0000, MaxCorr=0.63
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.111 | 2017: +0.118 | 2018: +0.063 | 2019: +0.071 | 2020: +0.090 | 2021: +0.111 | 2022: +0.076 | 2023: +0.159 | 2024: +0.114 | 2025: +0.152 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.069 | 2017: +0.220 | 2018: +0.121 | 2019: +0.237 | 2020: +0.079 | 2021: +0.270 | 2022: +0.324 | 2023: +0.374 | 2024: +0.097 | 2025: +0.281 | 2026: -0.212
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.62
- Early IC=+0.1497, Recent IC=+0.0934, 1st-half IC=+0.1337, 2nd-half IC=+0.0885, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.019, Q3_mid=+0.137, Q4=+0.111, Q5_high_vol=+0.153

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.0937, Sharpe=+0.6050)
- Admission: Train IC=+0.2655, Deflated=+0.2665, IR=0.78, Mono=0.80, p=0.0000, MaxCorr=0.31
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.107 | 2017: -0.041 | 2018: +0.149 | 2019: +0.127 | 2020: +0.143 | 2021: +0.060 | 2022: +0.185 | 2023: +0.105 | 2024: +0.058 | 2025: +0.087 | 2026: +0.145
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.359 | 2017: +0.140 | 2018: +0.406 | 2019: +0.343 | 2020: +0.324 | 2021: +0.172 | 2022: +0.426 | 2023: +0.103 | 2024: +0.010 | 2025: +0.063 | 2026: +0.074
- IC CV=0.61, Neg years (linear/tail)=1/0 of 8, Half ratio=1.14, Recency ratio=0.91
- Early IC=+0.1339, Recent IC=+0.1225, 1st-half IC=+0.1201, 2nd-half IC=+0.1366, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.103, Q3_mid=+0.171, Q4=+0.163, Q5_high_vol=+0.153

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1097, Sharpe=+0.5964)
- Admission: Train IC=+0.1628, Deflated=+0.1639, IR=0.42, Mono=0.69, p=0.0012, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.142 | 2016: +0.024 | 2017: +0.034 | 2018: +0.045 | 2019: +0.111 | 2020: +0.095 | 2021: +0.130 | 2022: +0.066 | 2023: +0.137 | 2024: +0.075 | 2025: +0.188 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.095 | 2017: +0.133 | 2018: -0.016 | 2019: +0.258 | 2020: +0.179 | 2021: +0.151 | 2022: +0.361 | 2023: +0.379 | 2024: +0.160 | 2025: +0.257 | 2026: -0.268
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=1.25, Recency ratio=1.18
- Early IC=+0.0832, Recent IC=+0.0981, 1st-half IC=+0.0841, 2nd-half IC=+0.1048, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.031, Q3_mid=+0.105, Q4=+0.112, Q5_high_vol=+0.140

**`combo_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.1151, Sharpe=+0.5953)
- Admission: Train IC=+0.2149, Deflated=+0.2155, IR=0.41, Mono=0.67, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.119 | 2017: +0.113 | 2018: +0.059 | 2019: +0.075 | 2020: +0.104 | 2021: +0.108 | 2022: +0.105 | 2023: +0.152 | 2024: +0.139 | 2025: +0.147 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.247 | 2016: +0.059 | 2017: +0.164 | 2018: +0.111 | 2019: +0.213 | 2020: +0.077 | 2021: +0.251 | 2022: +0.339 | 2023: +0.281 | 2024: +0.102 | 2025: +0.301 | 2026: -0.182
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.70
- Early IC=+0.1515, Recent IC=+0.1066, 1st-half IC=+0.1340, 2nd-half IC=+0.0966, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.018, Q3_mid=+0.142, Q4=+0.135, Q5_high_vol=+0.155

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.1106, Sharpe=+0.5865)
- Admission: Train IC=+0.2239, Deflated=+0.2256, IR=0.45, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.086 | 2017: +0.039 | 2018: +0.109 | 2019: +0.193 | 2020: +0.096 | 2021: +0.162 | 2022: +0.098 | 2023: +0.191 | 2024: +0.079 | 2025: +0.170 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.174 | 2016: +0.094 | 2017: +0.145 | 2018: +0.277 | 2019: +0.334 | 2020: +0.122 | 2021: +0.285 | 2022: +0.189 | 2023: +0.531 | 2024: +0.201 | 2025: +0.137 | 2026: -0.022
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.87
- Early IC=+0.1489, Recent IC=+0.1299, 1st-half IC=+0.1480, 2nd-half IC=+0.1380, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.081, Q3_mid=+0.150, Q4=+0.106, Q5_high_vol=+0.218

**`combo_rank_max__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=+0.1051, Sharpe=+0.5856)
- Admission: Train IC=+0.1882, Deflated=+0.1900, IR=0.37, Mono=0.65, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.104 | 2017: +0.038 | 2018: +0.076 | 2019: +0.133 | 2020: +0.131 | 2021: +0.170 | 2022: +0.106 | 2023: +0.156 | 2024: +0.073 | 2025: +0.187 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.325 | 2016: -0.103 | 2017: +0.112 | 2018: +0.122 | 2019: +0.266 | 2020: +0.099 | 2021: +0.262 | 2022: +0.326 | 2023: +0.376 | 2024: +0.114 | 2025: +0.296 | 2026: -0.399
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=1.05, Recency ratio=0.95
- Early IC=+0.1444, Recent IC=+0.1373, 1st-half IC=+0.1306, 2nd-half IC=+0.1374, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.077, Q3_mid=+0.155, Q4=+0.087, Q5_high_vol=+0.210

**`max_up_ret`** (Lock IC=+0.1014, Sharpe=+0.5632)
- Admission: Train IC=+0.2136, Deflated=+0.2148, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.080 | 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175 | 2024: +0.074 | 2025: +0.164 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.048 | 2016: +0.198 | 2017: +0.106 | 2018: +0.212 | 2019: +0.279 | 2020: +0.177 | 2021: +0.343 | 2022: +0.267 | 2023: +0.389 | 2024: +0.190 | 2025: +0.128 | 2026: -0.261
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.08
- Early IC=+0.1308, Recent IC=+0.1411, 1st-half IC=+0.1192, 2nd-half IC=+0.1353, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.079, Q3_mid=+0.145, Q4=+0.132, Q5_high_vol=+0.173

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1045, Sharpe=+0.5197)
- Admission: Train IC=+0.2336, Deflated=+0.2354, IR=0.45, Mono=0.68, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.147 | 2017: +0.003 | 2018: +0.124 | 2019: +0.196 | 2020: +0.131 | 2021: +0.157 | 2022: +0.092 | 2023: +0.174 | 2024: +0.058 | 2025: +0.171 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.126 | 2016: +0.172 | 2017: -0.009 | 2018: +0.272 | 2019: +0.369 | 2020: +0.252 | 2021: +0.259 | 2022: +0.220 | 2023: +0.543 | 2024: +0.193 | 2025: +0.088 | 2026: -0.072
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=0.68
- Early IC=+0.1830, Recent IC=+0.1245, 1st-half IC=+0.1538, 2nd-half IC=+0.1467, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.061, Q3_mid=+0.150, Q4=+0.123, Q5_high_vol=+0.241

**`combo_rank_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1083, Sharpe=+0.5114)
- Admission: Train IC=+0.1684, Deflated=+0.1702, IR=0.50, Mono=0.72, p=0.0008, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.059 | 2017: +0.061 | 2018: +0.047 | 2019: +0.137 | 2020: +0.115 | 2021: +0.146 | 2022: +0.108 | 2023: +0.179 | 2024: +0.061 | 2025: +0.188 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.319 | 2016: -0.005 | 2017: +0.036 | 2018: +0.069 | 2019: +0.292 | 2020: +0.212 | 2021: +0.256 | 2022: +0.199 | 2023: +0.434 | 2024: +0.167 | 2025: +0.183 | 2026: -0.543
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=1.14, Recency ratio=1.07
- Early IC=+0.1189, Recent IC=+0.1269, 1st-half IC=+0.1121, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.061, Q3_mid=+0.142, Q4=+0.118, Q5_high_vol=+0.169

**`combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend`** (Lock IC=+0.1094, Sharpe=+0.4547)
- Admission: Train IC=+0.2808, Deflated=+0.2817, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.062 | 2017: -0.047 | 2018: +0.111 | 2019: +0.093 | 2020: +0.119 | 2021: +0.034 | 2022: +0.170 | 2023: +0.129 | 2024: +0.072 | 2025: +0.118 | 2026: +0.147
- Yearly Tail ICs:   2015: +0.166 | 2016: +0.200 | 2017: +0.002 | 2018: +0.404 | 2019: +0.276 | 2020: +0.387 | 2021: +0.213 | 2022: +0.389 | 2023: +0.115 | 2024: +0.037 | 2025: +0.090 | 2026: +0.171
- IC CV=0.75, Neg years (linear/tail)=1/0 of 8, Half ratio=1.32, Recency ratio=1.09
- Early IC=+0.0937, Recent IC=+0.1017, 1st-half IC=+0.0827, 2nd-half IC=+0.1088, Neg regimes=1/5
- Weak component: `yesterday_early_trend` (CV=1.01)
- Regime ICs: Q1_low_vol=-0.011, Q2=+0.090, Q3_mid=+0.155, Q4=+0.118, Q5_high_vol=+0.108

**`combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1229, Sharpe=+0.4385)
- Admission: Train IC=+0.1971, Deflated=+0.1978, IR=0.48, Mono=0.67, p=0.0002, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.046 | 2017: -0.014 | 2018: +0.102 | 2019: +0.172 | 2020: +0.107 | 2021: +0.146 | 2022: +0.166 | 2023: +0.109 | 2024: +0.100 | 2025: +0.123 | 2026: +0.173
- Yearly Tail ICs:   2015: -0.069 | 2016: +0.207 | 2017: +0.032 | 2018: +0.220 | 2019: +0.240 | 2020: +0.156 | 2021: +0.246 | 2022: +0.184 | 2023: -0.050 | 2024: +0.213 | 2025: +0.015 | 2026: +0.332
- IC CV=0.56, Neg years (linear/tail)=1/1 of 8, Half ratio=1.33, Recency ratio=1.44
- Early IC=+0.1077, Recent IC=+0.1557, 1st-half IC=+0.1173, 2nd-half IC=+0.1559, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.055, Q3_mid=+0.117, Q4=+0.242, Q5_high_vol=+0.122

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev`** (Lock IC=+0.0701, Sharpe=+0.4317)
- Admission: Train IC=+0.2012, Deflated=+0.2027, IR=0.41, Mono=0.66, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.066 | 2017: +0.050 | 2018: +0.112 | 2019: +0.163 | 2020: +0.114 | 2021: +0.104 | 2022: +0.066 | 2023: +0.110 | 2024: +0.054 | 2025: +0.081 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.226 | 2016: +0.019 | 2017: +0.285 | 2018: +0.151 | 2019: +0.068 | 2020: +0.204 | 2021: +0.150 | 2022: +0.296 | 2023: +0.207 | 2024: +0.152 | 2025: +0.037 | 2026: -0.023
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.66
- Early IC=+0.1297, Recent IC=+0.0850, 1st-half IC=+0.1312, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.122, Q3_mid=+0.199, Q4=+0.087, Q5_high_vol=+0.120

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`** (Lock IC=+0.0619, Sharpe=+0.4262)
- Admission: Train IC=+0.2156, Deflated=+0.2160, IR=0.42, Mono=0.67, p=0.0000, MaxCorr=0.49
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.170 | 2017: +0.007 | 2018: +0.086 | 2019: +0.131 | 2020: +0.130 | 2021: +0.058 | 2022: +0.067 | 2023: +0.071 | 2024: +0.068 | 2025: +0.053 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.227 | 2016: +0.160 | 2017: +0.165 | 2018: +0.260 | 2019: +0.183 | 2020: +0.094 | 2021: +0.154 | 2022: +0.361 | 2023: +0.050 | 2024: +0.211 | 2025: +0.057 | 2026: +0.156
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.33
- Early IC=+0.1874, Recent IC=+0.0622, 1st-half IC=+0.1543, 2nd-half IC=+0.0996, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.103, Q3_mid=+0.191, Q4=+0.143, Q5_high_vol=+0.113

**`combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct`** (Lock IC=+0.1197, Sharpe=+0.4214)
- Admission: Train IC=+0.1991, Deflated=+0.1991, IR=0.44, Mono=0.66, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.060 | 2017: -0.027 | 2018: +0.101 | 2019: +0.129 | 2020: +0.090 | 2021: +0.104 | 2022: +0.152 | 2023: +0.081 | 2024: +0.079 | 2025: +0.133 | 2026: +0.181
- Yearly Tail ICs:   2015: -0.044 | 2016: +0.268 | 2017: +0.125 | 2018: +0.301 | 2019: +0.198 | 2020: +0.198 | 2021: +0.161 | 2022: +0.133 | 2023: -0.044 | 2024: +0.196 | 2025: -0.068 | 2026: +0.404
- IC CV=0.55, Neg years (linear/tail)=1/1 of 8, Half ratio=1.12, Recency ratio=1.29
- Early IC=+0.1015, Recent IC=+0.1304, 1st-half IC=+0.1136, 2nd-half IC=+0.1271, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.056, Q3_mid=+0.084, Q4=+0.244, Q5_high_vol=+0.087

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.1031, Sharpe=+0.3991)
- Admission: Train IC=+0.2439, Deflated=+0.2457, IR=0.45, Mono=0.66, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.101 | 2017: +0.037 | 2018: +0.095 | 2019: +0.180 | 2020: +0.113 | 2021: +0.192 | 2022: +0.094 | 2023: +0.187 | 2024: +0.071 | 2025: +0.174 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.105 | 2016: +0.104 | 2017: +0.141 | 2018: +0.202 | 2019: +0.289 | 2020: +0.110 | 2021: +0.350 | 2022: +0.299 | 2023: +0.426 | 2024: +0.132 | 2025: +0.268 | 2026: -0.354
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.95
- Early IC=+0.1506, Recent IC=+0.1427, 1st-half IC=+0.1406, 2nd-half IC=+0.1472, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.058, Q2=+0.086, Q3_mid=+0.156, Q4=+0.100, Q5_high_vol=+0.223

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1090, Sharpe=+0.3724)
- Admission: Train IC=+0.1551, Deflated=+0.1554, IR=0.48, Mono=0.70, p=0.0018, MaxCorr=0.14
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087 | 2022: +0.139 | 2023: +0.083 | 2024: +0.083 | 2025: +0.120 | 2026: +0.148
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.017 | 2017: +0.138 | 2018: +0.257 | 2019: +0.117 | 2020: +0.189 | 2021: +0.114 | 2022: +0.057 | 2023: -0.092 | 2024: +0.146 | 2025: +0.162 | 2026: +0.240
- IC CV=0.66, Neg years (linear/tail)=0/1 of 8, Half ratio=1.03, Recency ratio=1.15
- Early IC=+0.0981, Recent IC=+0.1130, 1st-half IC=+0.1055, 2nd-half IC=+0.1088, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.038, Q3_mid=+0.091, Q4=+0.189, Q5_high_vol=+0.098

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1038, Sharpe=+0.3582)
- Admission: Train IC=+0.2140, Deflated=+0.2164, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.163 | 2016: -0.000 | 2017: +0.065 | 2018: +0.090 | 2019: +0.182 | 2020: +0.103 | 2021: +0.173 | 2022: +0.107 | 2023: +0.193 | 2024: +0.043 | 2025: +0.186 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.189 | 2016: +0.079 | 2017: +0.201 | 2018: +0.094 | 2019: +0.179 | 2020: +0.323 | 2021: +0.146 | 2022: +0.259 | 2023: +0.389 | 2024: +0.067 | 2025: +0.168 | 2026: -0.241
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.42, Recency ratio=1.72
- Early IC=+0.0815, Recent IC=+0.1399, 1st-half IC=+0.1009, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.095, Q3_mid=+0.156, Q4=+0.079, Q5_high_vol=+0.167

**`combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1034, Sharpe=+0.3154)
- Admission: Train IC=+0.2006, Deflated=+0.2009, IR=0.36, Mono=0.68, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.168 | 2017: +0.081 | 2018: +0.105 | 2019: +0.113 | 2020: +0.082 | 2021: +0.057 | 2022: +0.087 | 2023: +0.067 | 2024: +0.122 | 2025: +0.061 | 2026: +0.147
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.399 | 2017: +0.074 | 2018: +0.161 | 2019: +0.240 | 2020: +0.038 | 2021: +0.112 | 2022: +0.273 | 2023: -0.051 | 2024: +0.189 | 2025: -0.118 | 2026: +0.183
- IC CV=0.34, Neg years (linear/tail)=0/1 of 8, Half ratio=0.62, Recency ratio=0.44
- Early IC=+0.1636, Recent IC=+0.0720, 1st-half IC=+0.1462, 2nd-half IC=+0.0907, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.143, Q3_mid=+0.133, Q4=+0.201, Q5_high_vol=+0.066

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend`** (Lock IC=+0.0634, Sharpe=+0.3043)
- Admission: Train IC=+0.2111, Deflated=+0.2126, IR=0.45, Mono=0.66, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.097 | 2017: +0.073 | 2018: +0.154 | 2019: +0.159 | 2020: +0.111 | 2021: +0.083 | 2022: +0.064 | 2023: +0.094 | 2024: +0.061 | 2025: +0.076 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.148 | 2017: +0.149 | 2018: +0.161 | 2019: +0.102 | 2020: +0.259 | 2021: +0.214 | 2022: +0.259 | 2023: +0.217 | 2024: +0.213 | 2025: +0.010 | 2026: +0.017
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.51
- Early IC=+0.1428, Recent IC=+0.0733, 1st-half IC=+0.1507, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.144, Q3_mid=+0.176, Q4=+0.113, Q5_high_vol=+0.135

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0960, Sharpe=+0.2321)
- Admission: Train IC=+0.2273, Deflated=+0.2288, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.141 | 2017: +0.038 | 2018: +0.101 | 2019: +0.184 | 2020: +0.121 | 2021: +0.173 | 2022: +0.109 | 2023: +0.161 | 2024: +0.073 | 2025: +0.171 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.133 | 2017: +0.189 | 2018: +0.216 | 2019: +0.214 | 2020: +0.092 | 2021: +0.366 | 2022: +0.294 | 2023: +0.335 | 2024: +0.099 | 2025: +0.231 | 2026: -0.354
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=0.89
- Early IC=+0.1594, Recent IC=+0.1411, 1st-half IC=+0.1409, 2nd-half IC=+0.1468, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.076, Q3_mid=+0.154, Q4=+0.108, Q5_high_vol=+0.202

**`combo_max__rbreaker_sell_setup_proximity_early__gap_pct`** (Lock IC=+0.1139, Sharpe=+0.1910)
- Admission: Train IC=+0.2200, Deflated=+0.2201, IR=0.54, Mono=0.68, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.145 | 2016: +0.064 | 2017: -0.037 | 2018: +0.108 | 2019: +0.136 | 2020: +0.092 | 2021: +0.099 | 2022: +0.156 | 2023: +0.078 | 2024: +0.061 | 2025: +0.127 | 2026: +0.187
- Yearly Tail ICs:   2015: +0.010 | 2016: +0.294 | 2017: +0.103 | 2018: +0.313 | 2019: +0.249 | 2020: +0.191 | 2021: +0.209 | 2022: +0.135 | 2023: +0.006 | 2024: +0.163 | 2025: -0.027 | 2026: +0.410
- IC CV=0.60, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=1.22
- Early IC=+0.1046, Recent IC=+0.1273, 1st-half IC=+0.1153, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.057, Q3_mid=+0.080, Q4=+0.237, Q5_high_vol=+0.097

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend`** (Lock IC=+0.0519, Sharpe=+0.0925)
- Admission: Train IC=+0.2039, Deflated=+0.2041, IR=0.59, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.198 | 2017: +0.035 | 2018: +0.138 | 2019: +0.122 | 2020: +0.119 | 2021: +0.039 | 2022: +0.067 | 2023: +0.050 | 2024: +0.080 | 2025: +0.053 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.243 | 2016: +0.289 | 2017: +0.109 | 2018: +0.281 | 2019: +0.337 | 2020: +0.061 | 2021: +0.111 | 2022: +0.274 | 2023: +0.093 | 2024: +0.277 | 2025: -0.000 | 2026: +0.086
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.26
- Early IC=+0.2014, Recent IC=+0.0531, 1st-half IC=+0.1790, 2nd-half IC=+0.0892, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.133, Q3_mid=+0.167, Q4=+0.171, Q5_high_vol=+0.131

**`combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev`** (Lock IC=+0.0720, Sharpe=+0.0140)
- Admission: Train IC=+0.1950, Deflated=+0.1952, IR=0.43, Mono=0.65, p=0.0002, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.138 | 2017: -0.015 | 2018: +0.096 | 2019: +0.121 | 2020: +0.111 | 2021: +0.078 | 2022: +0.088 | 2023: +0.027 | 2024: +0.107 | 2025: +0.034 | 2026: +0.108
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.251 | 2017: +0.082 | 2018: +0.307 | 2019: +0.263 | 2020: +0.060 | 2021: +0.152 | 2022: +0.303 | 2023: -0.071 | 2024: +0.112 | 2025: -0.124 | 2026: +0.196
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.74, Recency ratio=0.51
- Early IC=+0.1621, Recent IC=+0.0829, 1st-half IC=+0.1349, 2nd-half IC=+0.1001, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.101, Q3_mid=+0.176, Q4=+0.189, Q5_high_vol=+0.085

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.1997 | +0.0223 | -0.1891 | 1y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | TP | gradual | +0.1962 | +0.0375 | -0.2072 | 1y |
| `combo_mean__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.1914 | +0.0249 | -0.1806 | 1y |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.1811 | +0.0288 | -0.1482 | 1y |
| `combo_tri_max__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | Median | gradual | +0.1779 | +0.0062 | -0.1431 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1774 | +0.0573 | -0.0793 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1765 | +0.0546 | -0.0356 | 1y |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.1763 | +0.0148 | -0.1012 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1730 | +0.0564 | -0.0650 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1716 | +0.0478 | +0.0010 | 1y |
| `combo_tri_mean__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.1706 | +0.0226 | -0.1104 | 1y |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.1656 | +0.0547 | -0.0727 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1641 | +0.0519 | -0.1064 | 1y |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | TP | gradual | +0.1627 | +0.0317 | -0.0038 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1598 | +0.0451 | -0.1043 | 1y |
| `combo_tri_min__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1587 | +0.0523 | +0.0028 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | TP | gradual | +0.1515 | +0.0643 | -0.1582 | 1y |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Median | gradual | +0.1504 | +0.0612 | -0.1734 | 1y |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.1467 | +0.0486 | -0.1363 | 1y |
| `combo_max__first_bar_return__bar_body_rng_0` | Median | gradual | +0.1418 | +0.0283 | -0.0748 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.1411 | +0.0458 | -0.0515 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.1394 | +0.0494 | -0.0180 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1383 | +0.0659 | -0.0752 | 1y |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.1374 | +0.0386 | -0.0976 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.1366 | +0.0359 | -0.0577 | 1y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1361 | +0.0322 | +0.0384 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.1355 | +0.0552 | -0.0352 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.1315 | +0.0154 | -0.0089 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.1298 | +0.0289 | -0.0495 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.1286 | +0.0462 | -0.0128 | 1y |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.1282 | +0.0515 | -0.0272 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1258 | +0.0288 | -0.0303 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1224 | +0.0324 | -0.0787 | 1y |
| `combo_sig_product__first_bar_return__morning_volume_weighted_momentum` | Median | gradual | +0.1180 | +0.0150 | -0.0954 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.1179 | +0.0366 | -0.0350 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.1130 | +0.0276 | -0.0320 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | TP | gradual | +0.1121 | +0.0081 | -0.0355 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1073 | +0.0163 | +0.0388 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0912 | +0.0267 | +0.0014 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0887 | +0.0194 | +0.0499 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0796 | +0.0130 | +0.1057 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` | TP | persistent | +0.0702 | +0.0181 | +0.0964 | 1y |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | Median | fast | +0.0603 | -0.0592 | +0.1171 | 1y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0576 | +0.0214 | +0.1515 | 1y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | TP | fast | +0.0537 | -0.0061 | +0.1373 | 1y |
| `star50_limit_proximity_early` | TP | persistent | +0.0305 | +0.0013 | +0.1617 | 1y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Median | fast | +0.0234 | -0.0520 | +0.1970 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=3, gradual=34, persistent=10

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1597 | +0.0992 | -0.0470 | 2y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1561 | +0.1336 | +0.0302 | 3y |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | TP | gradual | +0.1482 | +0.0803 | -0.1033 | 3y |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.1480 | +0.1321 | +0.0278 | 3y |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.1475 | +0.0995 | -0.0552 | 3y |
| `combo_sig_product__max_up_ret__max_down_ret` | TP | persistent | +0.1397 | +0.1650 | +0.0268 | 3y |
| `combo_sig_product__max_up_ret__early_body_momentum` | TP | persistent | +0.1381 | +0.1375 | +0.0162 | 3y |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | Median | gradual | +0.1368 | +0.0576 | -0.1091 | 1y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1367 | +0.1278 | +0.0555 | 3y |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1341 | +0.1231 | +0.0484 | 3y |
| `combo_sig_product__max_down_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1310 | +0.1250 | -0.1091 | 3y |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | TP | gradual | +0.1302 | +0.0782 | -0.0902 | 3y |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.1302 | +0.1296 | +0.0477 | 3y |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1284 | +0.1343 | -0.0537 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.1280 | +0.1456 | -0.0548 | 3y |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | TP | persistent | +0.1280 | +0.1272 | +0.0513 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.1273 | +0.1403 | -0.0241 | 3y |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | persistent | +0.1263 | +0.1397 | +0.0585 | 3y |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | persistent | +0.1246 | +0.1307 | +0.0525 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend` | TP | gradual | +0.1229 | +0.1224 | -0.0360 | 3y |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Median | gradual | +0.1226 | +0.1251 | -0.1079 | 3y |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | TP | gradual | +0.1224 | +0.0875 | -0.0907 | 3y |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | TP | persistent | +0.1218 | +0.1408 | +0.0136 | 3y |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1205 | +0.1273 | -0.0690 | 3y |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | TP | gradual | +0.1197 | +0.1110 | -0.0297 | 3y |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.1193 | +0.1218 | +0.0505 | 3y |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1189 | +0.1544 | -0.0155 | 3y |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | TP | gradual | +0.1187 | +0.1150 | -0.0792 | 3y |
| `vwap_trend_channel_slope` | TP | gradual | +0.1186 | +0.1037 | -0.0312 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | TP | gradual | +0.1177 | +0.1360 | -0.0478 | 3y |
| `combo_max__bar_ret_0__vwap_close_divergence_trend` | Median | gradual | +0.1176 | +0.1225 | -0.1108 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__early_order_flow_imbalance` | Median | gradual | +0.1171 | +0.1339 | -0.0895 | 3y |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.1170 | +0.1400 | -0.0733 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | gradual | +0.1168 | +0.1524 | -0.0090 | 3y |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1156 | +0.1275 | -0.0792 | 3y |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | TP | gradual | +0.1151 | +0.1445 | -0.0498 | 3y |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1147 | +0.1217 | +0.0284 | 3y |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | TP | gradual | +0.1147 | +0.1327 | -0.0929 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | gradual | +0.1146 | +0.1576 | -0.0087 | 3y |
| `combo_min__max_up_ret__rsi_opening` | TP | gradual | +0.1131 | +0.1497 | -0.0901 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1130 | +0.1463 | +0.0468 | 3y |
| `combo_rank_min__close_vs_open_range__vwap_close_divergence_trend` | TP | gradual | +0.1123 | +0.1138 | -0.0814 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | TP | gradual | +0.1120 | +0.1426 | -0.0361 | 3y |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.1119 | +0.1373 | -0.0173 | 3y |
| `combo_rank_min__early_order_flow_imbalance__close_vs_open_range` | TP | gradual | +0.1119 | +0.1337 | -0.1181 | 3y |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | TP | persistent | +0.1118 | +0.0949 | +0.0050 | 3y |
| `combo_min__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.1115 | +0.1294 | -0.1146 | 3y |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | TP | gradual | +0.1111 | +0.1486 | -0.0112 | 3y |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1107 | +0.1431 | -0.0301 | 3y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | TP | gradual | +0.1101 | +0.1489 | -0.0592 | 3y |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | TP | gradual | +0.1097 | +0.1326 | -0.0552 | 3y |
| `combo_min__opening_drive_thrust_ratio__rsi_opening` | TP | gradual | +0.1083 | +0.1475 | -0.0463 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | TP | gradual | +0.1072 | +0.1404 | -0.0457 | 3y |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | Median | gradual | +0.1072 | +0.1255 | -0.0807 | 3y |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | TP | gradual | +0.1065 | +0.1070 | -0.0664 | 3y |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | Median | gradual | +0.1065 | +0.1270 | -0.1146 | 3y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1063 | +0.1535 | +0.0927 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1059 | +0.1666 | +0.0842 | ∞ |
| `combo_tri_median__trend_bar_close_consistency__star50_limit_proximity_early__bar_ret_0` | TP | gradual | +0.1059 | +0.1075 | -0.0063 | 3y |
| `combo_min__max_up_ret__max_down_ret` | TP | persistent | +0.1055 | +0.1169 | +0.0366 | 3y |
| `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1049 | +0.1535 | +0.0570 | ∞ |
| `max_up_ret` | TP | gradual | +0.1044 | +0.1427 | -0.0291 | 3y |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | TP | persistent | +0.1044 | +0.1539 | +0.0150 | 2y |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.1042 | +0.1409 | +0.0154 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.1038 | +0.1236 | +0.0682 | ∞ |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | TP | gradual | +0.1036 | +0.0980 | -0.0713 | 3y |
| `combo_mean__max_up_ret__close_vs_open_range` | TP | gradual | +0.1035 | +0.1408 | -0.0694 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.1031 | +0.1312 | +0.0239 | 3y |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | TP | gradual | +0.1031 | +0.1152 | -0.0916 | 3y |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | TP | gradual | +0.1028 | +0.1022 | -0.0673 | 3y |
| `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1025 | +0.1055 | +0.1692 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | TP | persistent | +0.1021 | +0.1310 | +0.0607 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1021 | +0.1470 | +0.0963 | ∞ |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1019 | +0.1270 | +0.0962 | 2y |
| `opening_drive_thrust_ratio` | TP | persistent | +0.1017 | +0.1521 | +0.0025 | 3y |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | Median | gradual | +0.1015 | +0.1009 | -0.0950 | 3y |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.1013 | +0.1176 | +0.0817 | 2y |
| `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1012 | +0.1077 | +0.1663 | ∞ |
| `combo_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1009 | +0.1237 | +0.0896 | 2y |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1008 | +0.1515 | -0.0358 | 3y |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1007 | +0.1050 | +0.1417 | ∞ |
| `combo_min__max_up_ret__close_vs_open_range` | TP | gradual | +0.1006 | +0.1471 | -0.0667 | 3y |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | TP | gradual | +0.1006 | +0.1275 | -0.0661 | 3y |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | gradual | +0.1004 | +0.1386 | -0.0665 | 3y |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | TP | gradual | +0.1000 | +0.1379 | -0.0699 | 3y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.0998 | +0.1253 | -0.0837 | 3y |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0996 | +0.1580 | +0.0125 | 3y |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.0995 | +0.1340 | +0.0394 | 3y |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.0992 | +0.1444 | +0.0143 | 3y |
| `combo_rank_min__close_vs_open_range__shaved_bar_trend_conviction` | TP | gradual | +0.0989 | +0.0836 | -0.0832 | 3y |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | TP | gradual | +0.0988 | +0.1108 | -0.0902 | 3y |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | TP | gradual | +0.0987 | +0.1069 | -0.0931 | 3y |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.0985 | +0.1248 | -0.0491 | 3y |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0984 | +0.1815 | +0.1057 | ∞ |
| `combo_rank_max__max_up_ret__bar_ret_0` | TP | gradual | +0.0982 | +0.1623 | -0.0692 | 3y |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.0981 | +0.1334 | -0.1008 | 3y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.0979 | +0.1617 | -0.0130 | 3y |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.0977 | +0.1071 | +0.0944 | 2y |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0977 | +0.0922 | +0.0407 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.0977 | +0.1059 | +0.0813 | ∞ |
| `combo_min__max_up_ret__bar_ret_0` | TP | persistent | +0.0976 | +0.1050 | +0.0071 | 3y |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | Median | gradual | +0.0974 | +0.1184 | -0.0754 | 3y |
| `combo_rel_diff__net_volume_flow__h2_l2_pullback_continuation` | TP | gradual | +0.0972 | +0.1055 | -0.0912 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0972 | +0.1786 | +0.1005 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | TP | persistent | +0.0970 | +0.0976 | +0.1122 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0970 | +0.1197 | +0.0753 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Median | persistent | +0.0969 | +0.0988 | +0.0840 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | TP | gradual | +0.0969 | +0.1176 | -0.0156 | 3y |
| `combo_mean__max_up_ret__bar_ret_0` | TP | gradual | +0.0969 | +0.1417 | -0.0334 | 3y |
| `combo_max__max_up_ret__close_vs_open_range` | TP | gradual | +0.0968 | +0.1288 | -0.0460 | 3y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0968 | +0.1455 | -0.0104 | 3y |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | TP | gradual | +0.0967 | +0.1553 | -0.0240 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.0962 | +0.1437 | -0.0686 | 3y |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0962 | +0.1455 | +0.0788 | ∞ |
| `open_to_current_return` | TP | gradual | +0.0954 | +0.1202 | -0.1128 | 3y |
| `combo_rank_max__max_up_ret__early_body_momentum` | TP | gradual | +0.0949 | +0.1310 | -0.0551 | 3y |
| `combo_rank_max__max_up_ret__close_vs_open_range` | TP | gradual | +0.0946 | +0.1317 | -0.0330 | 3y |
| `combo_z_sum__vwap_close_divergence_trend__bar_body_rng_0` | TP | gradual | +0.0940 | +0.1081 | -0.0718 | 3y |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | TP | gradual | +0.0939 | +0.1304 | -0.0427 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.0936 | +0.1254 | -0.0079 | 3y |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0934 | +0.0659 | +0.0516 | ∞ |
| `combo_mean__max_up_ret__max_down_ret` | TP | gradual | +0.0934 | +0.1601 | -0.0201 | 3y |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | TP | gradual | +0.0932 | +0.1230 | -0.0786 | 3y |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | TP | gradual | +0.0932 | +0.1290 | -0.0703 | 3y |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0931 | +0.1002 | +0.1063 | 2y |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | TP | gradual | +0.0929 | +0.1215 | -0.0677 | 3y |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | Median | gradual | +0.0927 | +0.1407 | -0.0721 | 3y |
| `combo_sig_product__max_up_ret__h2_l2_pullback_continuation` | TP | persistent | +0.0925 | +0.1313 | +0.0482 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | TP | persistent | +0.0925 | +0.1368 | +0.0074 | 3y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0922 | +0.1113 | -0.0699 | 3y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0921 | +0.1425 | +0.0389 | 3y |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | TP | gradual | +0.0919 | +0.1212 | -0.0476 | 3y |
| `combo_mean__net_volume_flow__shaved_bar_trend_conviction` | TP | gradual | +0.0918 | +0.0943 | -0.0846 | 3y |
| `combo_mean__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0916 | +0.1370 | -0.0315 | 3y |
| `combo_rank_min__max_up_ret__max_down_ret` | TP | persistent | +0.0912 | +0.1319 | +0.0194 | 3y |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0910 | +0.1367 | +0.0198 | 3y |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | TP | persistent | +0.0910 | +0.1376 | +0.0020 | 3y |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | persistent | +0.0910 | +0.1236 | +0.0586 | ∞ |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | TP | persistent | +0.0909 | +0.1169 | +0.0222 | 3y |
| `combo_tri_min__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0906 | +0.1247 | +0.0747 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0899 | +0.1053 | +0.0965 | ∞ |
| `combo_rank_min__max_up_ret__close_vs_open_range` | TP | gradual | +0.0899 | +0.1485 | -0.0650 | 3y |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Median | gradual | +0.0898 | +0.1310 | -0.0764 | 3y |
| `combo_min__max_down_ret__shaved_bar_trend_conviction` | TP | gradual | +0.0897 | +0.0678 | -0.0098 | 3y |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.0894 | +0.1282 | +0.0007 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0886 | +0.1357 | +0.0283 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | TP | gradual | +0.0884 | +0.1376 | -0.0532 | 3y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0882 | +0.0820 | +0.1183 | ∞ |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | TP | gradual | +0.0881 | +0.1225 | -0.0400 | 3y |
| `combo_mean__net_volume_flow__close_vs_open_range` | TP | gradual | +0.0881 | +0.1327 | -0.0713 | 3y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.0879 | +0.1000 | +0.0754 | ∞ |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | TP | gradual | +0.0877 | +0.1142 | -0.0546 | 3y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0870 | +0.1272 | +0.0759 | ∞ |
| `combo_sig_product__rsi_opening__h2_l2_pullback_continuation` | TP | gradual | +0.0869 | +0.0971 | -0.0783 | 3y |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0864 | +0.1133 | +0.0026 | 3y |
| `combo_min__max_down_ret__close_vs_open_range` | TP | persistent | +0.0857 | +0.1180 | +0.0251 | 3y |
| `combo_rank_max__trend_bar_close_consistency__star50_limit_proximity_early` | TP | persistent | +0.0854 | +0.0847 | +0.0355 | 3y |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0853 | +0.0511 | +0.0894 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | TP | persistent | +0.0851 | +0.1180 | +0.0488 | ∞ |
| `combo_mean__net_volume_flow__bar_body_rng_0` | TP | gradual | +0.0851 | +0.1294 | -0.0285 | 3y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0849 | +0.1297 | +0.0817 | ∞ |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0844 | +0.1103 | +0.0476 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.0843 | +0.1347 | -0.0120 | 3y |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | TP | gradual | +0.0840 | +0.1436 | -0.0332 | 3y |
| `combo_sig_product__early_body_momentum__close_vs_open_range` | TP | gradual | +0.0839 | +0.1092 | -0.0913 | 3y |
| `combo_max__first_bar_return__close_vs_open_range` | TP | gradual | +0.0838 | +0.1354 | -0.0910 | 3y |
| `combo_rank_min__max_down_ret__close_vs_open_range` | TP | persistent | +0.0833 | +0.1153 | +0.0325 | 3y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.0832 | +0.1162 | +0.0620 | ∞ |
| `combo_tri_median__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | TP | gradual | +0.0832 | +0.1096 | -0.0918 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | TP | gradual | +0.0831 | +0.1185 | -0.0179 | 3y |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | TP | gradual | +0.0829 | +0.1217 | -0.0350 | 3y |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.0829 | +0.1198 | -0.0521 | 3y |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | TP | gradual | +0.0828 | +0.1073 | -0.1035 | 3y |
| `combo_tri_max__max_up_ret__early_body_momentum__trend_day_regime_conviction` | TP | gradual | +0.0827 | +0.1357 | -0.0573 | 3y |
| `combo_max__max_up_ret__early_order_flow_imbalance` | TP | gradual | +0.0827 | +0.1225 | -0.0645 | 3y |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0823 | +0.1356 | +0.0642 | ∞ |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0822 | +0.1498 | +0.0903 | ∞ |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0822 | +0.0456 | +0.0658 | ∞ |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | Median | gradual | +0.0821 | +0.1070 | -0.1258 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0818 | +0.1348 | +0.0830 | ∞ |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.0816 | +0.0842 | +0.1032 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.0814 | +0.1034 | +0.0533 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | TP | persistent | +0.0813 | +0.1459 | +0.0623 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0812 | +0.1218 | +0.0425 | ∞ |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0811 | +0.1290 | +0.0506 | ∞ |
| `combo_mean__first_bar_return__close_vs_open_range` | TP | gradual | +0.0808 | +0.1507 | -0.0362 | 3y |
| `combo_min__net_volume_flow__bar_ret_0` | TP | gradual | +0.0806 | +0.1372 | -0.0086 | 3y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0805 | +0.1039 | +0.0478 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0801 | +0.0915 | +0.0804 | ∞ |
| `combo_min__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0801 | +0.1106 | -0.0042 | 3y |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | TP | gradual | +0.0800 | +0.1152 | -0.0755 | 3y |
| `combo_mean__trend_day_regime_conviction__bar_ret_0` | TP | gradual | +0.0798 | +0.1406 | -0.0436 | 3y |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | Median | gradual | +0.0796 | +0.1175 | -0.1094 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0794 | +0.1122 | +0.0962 | ∞ |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | TP | persistent | +0.0794 | +0.1220 | +0.0761 | ∞ |
| `combo_rank_max__net_volume_flow__bar_ret_0` | TP | gradual | +0.0792 | +0.1248 | -0.0783 | 3y |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0789 | +0.1023 | +0.0825 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0786 | +0.1448 | +0.1939 | ∞ |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.0786 | +0.1501 | -0.0235 | 3y |
| `combo_max__max_up_ret__bar_ret_0` | TP | gradual | +0.0785 | +0.1428 | -0.0684 | 3y |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0785 | +0.1015 | +0.1440 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0781 | +0.1092 | +0.0507 | ∞ |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | Median | gradual | +0.0780 | +0.1137 | -0.0138 | 3y |
| `combo_max__early_body_momentum__close_vs_open_range` | TP | gradual | +0.0778 | +0.1293 | -0.1045 | 3y |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0778 | +0.1367 | +0.0043 | 3y |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0777 | +0.1034 | +0.0643 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0775 | +0.0680 | +0.0634 | ∞ |
| `combo_rank_max__early_body_momentum__close_vs_open_range` | TP | gradual | +0.0774 | +0.1283 | -0.0912 | 3y |
| `combo_min__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.0772 | +0.1122 | -0.0182 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | TP | gradual | +0.0772 | +0.1469 | -0.0525 | 3y |
| `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | TP | gradual | +0.0768 | +0.1041 | -0.0727 | 3y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.0768 | +0.1144 | +0.0468 | ∞ |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | TP | gradual | +0.0768 | +0.1201 | -0.0559 | 3y |
| `combo_mean__star50_limit_proximity_early__vwap_close_divergence_trend` | TP | persistent | +0.0767 | +0.1084 | +0.0509 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0766 | +0.0799 | +0.0886 | ∞ |
| `combo_tri_mean__max_up_ret__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0759 | +0.1181 | +0.0452 | ∞ |
| `combo_mean__net_volume_flow__max_down_ret` | TP | gradual | +0.0759 | +0.1343 | -0.0101 | 3y |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Median | persistent | +0.0755 | +0.0974 | +0.0540 | ∞ |
| `combo_max__net_volume_flow__first_bar_return` | Median | gradual | +0.0751 | +0.1096 | -0.0699 | 3y |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | TP | persistent | +0.0750 | +0.1148 | +0.0215 | 3y |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0748 | +0.1385 | +0.1224 | ∞ |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0748 | +0.1103 | +0.1383 | ∞ |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | TP | gradual | +0.0747 | +0.1488 | -0.0473 | 3y |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.0746 | +0.0988 | +0.0624 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0744 | +0.1064 | +0.0853 | ∞ |
| `combo_rank_max__max_down_ret__vwap_close_divergence_trend` | TP | gradual | +0.0739 | +0.1097 | -0.0629 | 3y |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | TP | gradual | +0.0733 | +0.1189 | -0.0710 | 3y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0728 | +0.1107 | +0.1234 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | TP | gradual | +0.0727 | +0.1296 | -0.0089 | 3y |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | TP | persistent | +0.0727 | +0.0727 | +0.0598 | ∞ |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Median | persistent | +0.0725 | +0.1015 | +0.1130 | ∞ |
| `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0` | TP | gradual | +0.0723 | +0.0798 | -0.0679 | 3y |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | TP | persistent | +0.0723 | +0.1103 | +0.1059 | ∞ |
| `combo_mean__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.0716 | +0.1196 | -0.0799 | 3y |
| `combo_max__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0710 | +0.1035 | +0.1192 | ∞ |
| `combo_min__first_bar_return__close_vs_open_range` | TP | persistent | +0.0704 | +0.1313 | +0.0112 | 3y |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | TP | gradual | +0.0697 | +0.1349 | -0.0971 | 3y |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | TP | gradual | +0.0696 | +0.1432 | -0.0156 | 3y |
| `combo_max__bar_ret_0__early_order_flow_imbalance` | Median | gradual | +0.0695 | +0.1034 | -0.1262 | 3y |
| `combo_rank_max__trend_day_regime_conviction__early_order_flow_imbalance` | Median | gradual | +0.0693 | +0.1076 | -0.0907 | 3y |
| `combo_mean__max_down_ret__close_vs_open_range` | TP | gradual | +0.0691 | +0.1306 | -0.0231 | 3y |
| `combo_min__trend_bar_close_consistency__max_down_ret` | TP | gradual | +0.0690 | +0.1126 | -0.0070 | 3y |
| `combo_rank_min__first_bar_return__close_vs_open_range` | TP | persistent | +0.0689 | +0.1270 | +0.0124 | 3y |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | TP | persistent | +0.0681 | +0.0553 | +0.0807 | ∞ |
| `combo_rel_diff__bar_ret_0__late_bar_momentum` | TP | persistent | +0.0681 | +0.0875 | +0.0888 | 2y |
| `combo_rank_min__bar_ret_0__bar_body_rng_0` | TP | persistent | +0.0674 | +0.1001 | +0.0065 | 3y |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0674 | +0.0878 | +0.1036 | ∞ |
| `combo_max__early_body_momentum__bar_body_rng_0` | TP | gradual | +0.0660 | +0.1150 | -0.0773 | 3y |
| `combo_diff__first_bar_return__early_late_momentum_divergence` | TP | persistent | +0.0659 | +0.1186 | +0.1044 | 2y |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0654 | +0.1081 | +0.0835 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0653 | +0.1132 | +0.0871 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0651 | +0.0985 | +0.0978 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0651 | +0.1559 | +0.0041 | 3y |
| `combo_sig_product__max_up_ret__body_size_progression` | TP | persistent | +0.0645 | +0.1370 | +0.0791 | ∞ |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | TP | gradual | +0.0635 | +0.1132 | -0.0016 | 3y |
| `combo_rank_min__trend_bar_close_consistency__max_down_ret` | TP | persistent | +0.0631 | +0.1085 | +0.0185 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.0630 | +0.0844 | +0.0798 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0630 | +0.1130 | +0.0822 | ∞ |
| `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | TP | persistent | +0.0628 | +0.1152 | +0.1110 | 2y |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0625 | +0.0851 | +0.0819 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | TP | gradual | +0.0619 | +0.1286 | -0.0480 | 3y |
| `first_bar_return` | TP | gradual | +0.0618 | +0.1067 | -0.0114 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.0615 | +0.1143 | +0.0045 | 3y |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0603 | +0.1064 | +0.0944 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Median | gradual | +0.0603 | +0.1283 | -0.0554 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | TP | gradual | +0.0589 | +0.1415 | -0.0482 | 3y |
| `combo_tri_max__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0588 | +0.1013 | +0.0767 | ∞ |
| `combo_mean__early_body_momentum__star50_limit_proximity_early` | TP | persistent | +0.0585 | +0.0955 | +0.0690 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0582 | +0.0911 | +0.1405 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.0572 | +0.1077 | +0.0826 | ∞ |
| `combo_rank_min__bar_ret_0__max_down_ret` | TP | persistent | +0.0562 | +0.1026 | +0.0059 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.0553 | +0.1141 | +0.0846 | ∞ |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | TP | persistent | +0.0549 | +0.0991 | +0.0046 | 3y |
| `combo_mean__bar_ret_0__max_down_ret` | TP | persistent | +0.0549 | +0.1243 | +0.0110 | 3y |
| `combo_min__first_bar_return__max_down_ret` | TP | persistent | +0.0544 | +0.0971 | +0.0162 | 3y |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0527 | +0.1077 | +0.1000 | ∞ |
| `combo_rank_max__max_up_ret__max_down_ret` | TP | gradual | +0.0515 | +0.1419 | -0.0037 | 3y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0514 | +0.1238 | +0.0782 | ∞ |
| `combo_max__max_up_ret__max_down_ret` | TP | gradual | +0.0513 | +0.1389 | -0.0338 | 3y |
| `combo_sig_product__max_up_ret__bar_ret_0` | TP | persistent | +0.0501 | +0.0982 | +0.0041 | 3y |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0483 | +0.0923 | +0.1405 | ∞ |
| `combo_max__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | persistent | +0.0481 | +0.1067 | +0.0743 | ∞ |
| `combo_sig_product__max_down_ret__close_vs_open_range` | Median | gradual | +0.0461 | +0.1194 | -0.1011 | 3y |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | TP | gradual | +0.0446 | +0.1169 | -0.0714 | 3y |
| `combo_max__first_bar_return__max_down_ret` | TP | gradual | +0.0438 | +0.1285 | -0.0002 | 3y |
| `combo_rank_max__early_body_momentum__max_down_ret` | TP | gradual | +0.0435 | +0.1316 | -0.0799 | 3y |
| `combo_max__max_down_ret__close_vs_open_range` | TP | gradual | +0.0432 | +0.1266 | -0.0625 | 3y |
| `combo_max__net_volume_flow__max_down_ret` | Median | gradual | +0.0406 | +0.1411 | -0.0411 | 3y |
| `combo_rank_max__max_down_ret__close_vs_open_range` | TP | gradual | +0.0405 | +0.1383 | -0.0626 | 3y |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0400 | +0.1007 | +0.1218 | ∞ |
| `combo_rank_max__bar_ret_0__max_down_ret` | TP | persistent | +0.0365 | +0.1171 | +0.0311 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0336 | +0.1046 | +0.1485 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0328 | +0.1379 | +0.1461 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | TP | persistent | +0.0316 | +0.0822 | +0.0919 | ∞ |
| `max_down_ret` | TP | persistent | +0.0309 | +0.1149 | +0.0305 | ∞ |
| `combo_ratio__bar_ret_0__net_volume_flow` | TP | gradual | +0.0078 | +0.0609 | -0.0032 | ∞ |
| `combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction` | FP | immediate | -0.0026 | +0.0803 | +0.0489 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=151, persistent=145

**FP decay trajectories:**

- `combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction`: Y1:-0.003 → Y2:+0.080 → Y3:-0.115 → Y4:+0.049

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | TP | gradual | +0.1985 | +0.1002 | -0.0464 | 3y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1933 | +0.0429 | -0.0517 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.1909 | +0.0792 | -0.0331 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | TP | gradual | +0.1873 | +0.0714 | -0.0618 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | TP | gradual | +0.1861 | +0.0835 | -0.0155 | 1y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__first_bar_return` | TP | fast | +0.1855 | -0.0092 | +0.0317 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.1853 | +0.1051 | -0.0222 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1851 | +0.0840 | +0.0473 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1846 | +0.1244 | +0.0709 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1834 | +0.1297 | +0.0834 | 3y |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1830 | +0.0579 | +0.0039 | 1y |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1829 | +0.1255 | +0.0725 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1809 | +0.1158 | +0.0267 | 3y |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1791 | +0.0627 | -0.0893 | 1y |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.1790 | +0.0833 | +0.0852 | 1y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1786 | +0.0785 | +0.0003 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1777 | +0.1092 | +0.0640 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1763 | +0.0995 | +0.0898 | ∞ |
| `max_up_ret` | TP | gradual | +0.1753 | +0.0739 | -0.0753 | 1y |
| `combo_mean__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1744 | +0.0585 | -0.0288 | 1y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1725 | +0.0614 | +0.0856 | 1y |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | gradual | +0.1725 | +0.0817 | -0.0179 | 1y |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.1710 | +0.0824 | +0.0678 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1707 | +0.0852 | -0.0475 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1661 | +0.0772 | +0.0633 | 1y |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1640 | +0.0818 | +0.0840 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1636 | +0.0515 | +0.0524 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1631 | +0.1184 | +0.0315 | 3y |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1630 | +0.0930 | +0.0619 | 3y |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | TP | persistent | +0.1626 | +0.0169 | +0.0216 | 1y |
| `combo_rank_max__max_up_ret__first_bar_return` | TP | gradual | +0.1616 | +0.0768 | -0.0623 | 1y |
| `combo_max__max_up_ret__bar_ret_0` | TP | gradual | +0.1606 | +0.0733 | -0.0756 | 1y |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | TP | gradual | +0.1585 | +0.1141 | -0.0350 | 3y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1583 | +0.0912 | +0.0705 | 3y |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1577 | +0.0831 | +0.1027 | ∞ |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | TP | gradual | +0.1577 | +0.0746 | -0.0736 | 1y |
| `combo_max__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.1572 | +0.0849 | -0.0845 | 3y |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1568 | +0.1111 | +0.0834 | ∞ |
| `combo_diff__max_up_ret__keltner_squeeze_width` | TP | gradual | +0.1525 | +0.1395 | -0.0619 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.1523 | +0.1050 | +0.0178 | 3y |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1489 | +0.0824 | +0.0743 | 3y |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1478 | +0.1097 | +0.1242 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | TP | persistent | +0.1472 | +0.0821 | +0.0304 | 3y |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | TP | gradual | +0.1469 | +0.0622 | -0.0214 | 1y |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1468 | +0.0898 | +0.1017 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1456 | +0.0685 | +0.1121 | 1y |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1449 | +0.0982 | +0.0926 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0` | TP | persistent | +0.1402 | +0.0775 | +0.0823 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1397 | +0.0889 | +0.0767 | ∞ |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | TP | gradual | +0.1371 | +0.0753 | -0.0582 | 3y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | TP | persistent | +0.1368 | +0.0792 | +0.0606 | 3y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1366 | +0.1389 | +0.0904 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1338 | +0.0735 | +0.0934 | ∞ |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | TP | persistent | +0.1314 | +0.0604 | +0.0203 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.1302 | +0.0909 | +0.1540 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | TP | persistent | +0.1295 | +0.0718 | +0.1475 | ∞ |
| `combo_z_sum__max_up_ret__gap_pct` | TP | persistent | +0.1280 | +0.1098 | +0.1396 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1270 | +0.1100 | +0.1389 | ∞ |
| `combo_min__first_bar_return__limit_down_proximity_early` | TP | persistent | +0.1249 | +0.0872 | +0.1193 | ∞ |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__star50_limit_proximity_early` | TP | persistent | +0.1226 | +0.1112 | +0.1734 | ∞ |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | TP | gradual | +0.1196 | +0.0551 | -0.0120 | 1y |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1164 | +0.0816 | +0.1343 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | TP | persistent | +0.1160 | +0.1233 | +0.1909 | ∞ |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | TP | persistent | +0.1096 | +0.0544 | +0.0340 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1073 | +0.1001 | +0.1722 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.1051 | +0.0583 | +0.1446 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | TP | persistent | +0.1023 | +0.0916 | +0.0534 | ∞ |
| `combo_max__max_up_ret__volume_price_confirmation` | TP | gradual | +0.0966 | +0.0675 | -0.0176 | 3y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | TP | gradual | +0.0936 | +0.0611 | -0.0001 | 3y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct` | TP | persistent | +0.0851 | +0.0766 | +0.1831 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0826 | +0.0831 | +0.1479 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__gap_pct` | TP | persistent | +0.0779 | +0.0606 | +0.1869 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | TP | persistent | +0.0713 | +0.0682 | +0.0377 | ∞ |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0667 | +0.1215 | +0.1465 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | fast | +0.0544 | -0.0517 | -0.0008 | 1y |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | TP | gradual | +0.0503 | +0.0801 | -0.0134 | 3y |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev` | TP | persistent | +0.0273 | +0.1066 | +0.1080 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=2, gradual=23, persistent=52

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:+0.054 → Y2:-0.052 → Y3:-0.026 → Y4:-0.001

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 15/20 top rejects are profitable (75%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard**: 18/20 top rejects are profitable (90%)

- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Sharpe=+0.7446
- `combo_tri_median__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.1758, Lock IC=+0.0545, Sharpe=+0.7446
- `combo_clamp_diff__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.1843, Lock IC=+0.0574, Sharpe=+0.5286

**Temporal Validation Gate**: 19/20 top rejects are profitable (95%)

- `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1955, Lock IC=+0.0678, Sharpe=+0.6776
- `combo_tri_min__bar_ret_0__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1950, Lock IC=+0.0678, Sharpe=+0.6776
- `combo_tri_median__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1940, Lock IC=+0.0760, Sharpe=+0.6618

**BH-FDR Gate**: 3/13 top rejects are profitable (23%)

- `combo_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1027, Lock IC=+0.0707, Sharpe=+0.3328
- `combo_z_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1027, Lock IC=+0.0707, Sharpe=+0.3328
- `combo_rel_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1028, Lock IC=+0.0730, Sharpe=+0.1567

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0590, Sharpe=+0.7052
- `combo_tri_z_mean__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0590, Sharpe=+0.7052
- `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0591, Sharpe=+0.7052

**B6 Yearly IC CV Gate**: 16/20 top rejects are profitable (80%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1777, Lock IC=+0.0574, Sharpe=+0.8686
- `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1764, Lock IC=+0.0433, Sharpe=+0.5822
- `combo_z_sum__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1764, Lock IC=+0.0433, Sharpe=+0.5822

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2265, Lock IC=+0.0937, Sharpe=+1.0629
- `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__first_bar_return`: Train IC=+0.2370, Lock IC=+0.0693, Sharpe=+0.5695
- `combo_tri_z_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__first_bar_return`: Train IC=+0.2370, Lock IC=+0.0693, Sharpe=+0.5695

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2539, Lock IC=+0.0972, Sharpe=+1.1933
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2899, Lock IC=+0.1070, Sharpe=+1.0919
- `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.2491, Lock IC=+0.0947, Sharpe=+1.0575

**B2 Rolling Guard**: 13/20 top rejects are profitable (65%)

- `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Sharpe=+0.3984
- `combo_tri_z_mean__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Sharpe=+0.3984
- `combo_tri_mean__opening_drive_thrust_ratio__opening_auction_imbalance__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Sharpe=+0.3984

**Temporal Validation Gate**: 16/20 top rejects are profitable (80%)

- `combo_diff__volume_weighted_momentum_acceleration__rsi_opening`: Train IC=+0.2534, Lock IC=+0.0993, Sharpe=+0.9228
- `combo_z_diff__volume_weighted_momentum_acceleration__rsi_opening`: Train IC=+0.2534, Lock IC=+0.0993, Sharpe=+0.9228
- `combo_diff__volume_weighted_momentum_acceleration__high_low_sequence_momentum`: Train IC=+0.2534, Lock IC=+0.0993, Sharpe=+0.9228

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824

**B6 Yearly IC CV Gate**: 13/20 top rejects are profitable (65%)

- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__net_volume_flow__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.2190, Lock IC=+0.0434, Sharpe=+0.9681

**B6 Temporal Stability Gate**: 4/4 top rejects are profitable (100%)

- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2473, Lock IC=+0.0892, Sharpe=+0.4980
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2473, Lock IC=+0.0892, Sharpe=+0.4980
- `combo_rank_min__max_up_ret__net_volume_flow`: Train IC=+0.2253, Lock IC=+0.0908, Sharpe=+0.4724

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.3103, Lock IC=+0.1126, Sharpe=+1.0957
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.3348, Lock IC=+0.1232, Sharpe=+0.9722

### 159915ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Sharpe=+1.8587
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2154, Lock IC=+0.1298, Sharpe=+1.4980

**B2 Rolling Guard**: 18/20 top rejects are profitable (90%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2340, Lock IC=+0.1332, Sharpe=+1.4122
- `combo_rank_min__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2251, Lock IC=+0.1287, Sharpe=+1.4106
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Sharpe=+1.3582

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2321, Lock IC=+0.1334, Sharpe=+1.9776
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2334, Lock IC=+0.1300, Sharpe=+1.6301
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2334, Lock IC=+0.1300, Sharpe=+1.6301

**BH-FDR Gate**: 2/4 top rejects are profitable (50%)

- `combo_mean__max_up_ret__keltner_squeeze_width`: Train IC=+0.1054, Lock IC=+0.0291, Sharpe=+0.0947
- `combo_z_sum__max_up_ret__keltner_squeeze_width`: Train IC=+0.1054, Lock IC=+0.0291, Sharpe=+0.0947

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Sharpe=+1.4133
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2419, Lock IC=+0.1373, Sharpe=+1.3304
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2344, Lock IC=+0.1306, Sharpe=+1.3039

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2813, Lock IC=+0.1406, Sharpe=+1.4794
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2777, Lock IC=+0.1338, Sharpe=+1.4166
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0`: Train IC=+0.2775, Lock IC=+0.1337, Sharpe=+1.4166

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1212 | 78 | 25 | 29 | 24 | 32% | 31% |
| B2 Rolling Guard | 206 | 78 | 18 | 26 | 34 | 23% | 44% |
| Temporal Validation Gate | 99 | 78 | 0 | 24 | 54 | 0% | 69% |
| BH-FDR Gate | 13 | 13 | 1 | 9 | 3 | 8% | 23% |
| B3 Composite Floor | 44 | 44 | 0 | 15 | 29 | 0% | 66% |
| B6 Yearly IC CV Gate | 26 | 26 | 0 | 7 | 19 | 0% | 73% |
| B4 Correlation Gate | 86 | 78 | 0 | 7 | 71 | 0% | 91% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `yesterday_early_vwap_dev`: Train IC=+0.0677, Lock IC=+0.0657, Sharpe=+0.6437
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Sharpe=+0.7446
- `combo_tri_median__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.1758, Lock IC=+0.0545, Sharpe=+0.7446
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Train IC=+0.1710, Lock IC=+0.0652, Sharpe=+0.5621

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_z_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1469, Lock IC=+0.0614, Sharpe=+0.8233

**BH-FDR Gate** — top TP casualties:
- `combo_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1027, Lock IC=+0.0707, Sharpe=+0.3328
- `combo_z_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1027, Lock IC=+0.0707, Sharpe=+0.3328
- `combo_rel_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1028, Lock IC=+0.0730, Sharpe=+0.1567

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0590, Sharpe=+0.7052
- `combo_tri_z_mean__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0590, Sharpe=+0.7052
- `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0591, Sharpe=+0.7052

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1777, Lock IC=+0.0574, Sharpe=+0.8686
- `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1764, Lock IC=+0.0433, Sharpe=+0.5822
- `combo_z_sum__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1764, Lock IC=+0.0433, Sharpe=+0.5822

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1818, Lock IC=+0.0875, Sharpe=+1.1020
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2265, Lock IC=+0.0937, Sharpe=+1.0629
- `combo_tri_min__max_up_ret__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1916, Lock IC=+0.0743, Sharpe=+0.6390

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2453 | 78 | 14 | 21 | 43 | 18% | 55% |
| B2 Rolling Guard | 372 | 78 | 21 | 19 | 38 | 27% | 49% |
| Temporal Validation Gate | 145 | 78 | 16 | 10 | 52 | 21% | 67% |
| BH-FDR Gate | 8 | 8 | 0 | 8 | 0 | 0% | 0% |
| B3 Composite Floor | 262 | 78 | 2 | 7 | 69 | 3% | 88% |
| B6 Yearly IC CV Gate | 23 | 23 | 5 | 5 | 13 | 22% | 57% |
| B6 Temporal Stability Gate | 4 | 4 | 0 | 0 | 4 | 0% | 100% |
| B4 Correlation Gate | 963 | 78 | 0 | 11 | 67 | 0% | 86% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2539, Lock IC=+0.0972, Sharpe=+1.1933
- `combo_rel_diff__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.2431, Lock IC=+0.1135, Sharpe=+1.1899
- `combo_rel_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.2456, Lock IC=+0.0932, Sharpe=+1.1142

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0355, Lock IC=+0.0707, Sharpe=+0.8914
- `combo_max__max_down_ret__shaved_bar_trend_conviction`: Train IC=+0.1470, Lock IC=+0.0743, Sharpe=+0.6093
- `combo_sig_product__shaved_bar_trend_conviction__h2_l2_pullback_continuation`: Train IC=+0.1466, Lock IC=+0.0527, Sharpe=+0.4446

**Temporal Validation Gate** — top TP casualties:
- `combo_rank_max__demark_setup_reversal_early__h2_l2_pullback_continuation`: Train IC=+0.2183, Lock IC=+0.1051, Sharpe=+1.0657
- `combo_rel_diff__demark_setup_reversal_early__close_vs_open_range`: Train IC=+0.2089, Lock IC=+0.1233, Sharpe=+1.0346
- `combo_diff__demark_setup_reversal_early__close_vs_open_range`: Train IC=+0.2133, Lock IC=+0.1228, Sharpe=+1.0300

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__net_volume_flow__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.2190, Lock IC=+0.0434, Sharpe=+0.9681

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2473, Lock IC=+0.0892, Sharpe=+0.4980
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2473, Lock IC=+0.0892, Sharpe=+0.4980
- `combo_rank_min__max_up_ret__net_volume_flow`: Train IC=+0.2253, Lock IC=+0.0908, Sharpe=+0.4724

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.3103, Lock IC=+0.1126, Sharpe=+1.0957
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2039 | 78 | 31 | 12 | 35 | 40% | 45% |
| B2 Rolling Guard | 468 | 78 | 17 | 12 | 49 | 22% | 63% |
| Temporal Validation Gate | 103 | 78 | 7 | 0 | 71 | 9% | 91% |
| BH-FDR Gate | 4 | 4 | 2 | 0 | 2 | 50% | 50% |
| B3 Composite Floor | 153 | 78 | 4 | 4 | 70 | 5% | 90% |
| B4 Correlation Gate | 128 | 78 | 0 | 1 | 77 | 0% | 99% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Sharpe=+1.8587
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2154, Lock IC=+0.1298, Sharpe=+1.4980

**B2 Rolling Guard** — top TP casualties:
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2340, Lock IC=+0.1332, Sharpe=+1.4122
- `combo_rank_min__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2251, Lock IC=+0.1287, Sharpe=+1.4106
- `combo_rel_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1530, Lock IC=+0.1231, Sharpe=+1.3887

**Temporal Validation Gate** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2321, Lock IC=+0.1334, Sharpe=+1.9776
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2321, Lock IC=+0.1334, Sharpe=+1.9776
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2334, Lock IC=+0.1300, Sharpe=+1.6301

**BH-FDR Gate** — top TP casualties:
- `combo_mean__max_up_ret__keltner_squeeze_width`: Train IC=+0.1054, Lock IC=+0.0291, Sharpe=+0.0947
- `combo_z_sum__max_up_ret__keltner_squeeze_width`: Train IC=+0.1054, Lock IC=+0.0291, Sharpe=+0.0947

**B3 Composite Floor** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Sharpe=+1.4133
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.1939, Lock IC=+0.1254, Sharpe=+1.3957
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.1938, Lock IC=+0.1253, Sharpe=+1.3957

**B4 Correlation Gate** — top TP casualties:
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (99 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 66 | 50 | 0 | 35 | 15 | 0% | 70% |
| recency_ratio >= 2.5 (late-concentrated) | 29 | 29 | 0 | 27 | 2 | 0% | 93% |

**Top TP killed by recency_ratio cap:**
- `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1955, Lock IC=+0.0678, Sharpe=+0.6776
- `combo_tri_min__bar_ret_0__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1950, Lock IC=+0.0678, Sharpe=+0.6776
- `combo_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1686, Lock IC=+0.0633, Sharpe=+0.6654
- `combo_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1682, Lock IC=+0.0633, Sharpe=+0.6654
- `combo_tri_median__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1940, Lock IC=+0.0760, Sharpe=+0.6618

### 500ETF — `single` (145 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 136 | 50 | 0 | 42 | 8 | 0% | 84% |
| recency_ratio >= 2.5 (late-concentrated) | 7 | 7 | 0 | 6 | 1 | 0% | 86% |

**Top TP killed by recency_ratio cap:**
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Train IC=+0.1291, Lock IC=+0.0798, Sharpe=+0.4226
- `combo_min__early_body_momentum__max_down_ret`: Train IC=+0.2071, Lock IC=+0.0940, Sharpe=+0.3762
- `combo_min__opening_momentum_score__max_down_ret`: Train IC=+0.2071, Lock IC=+0.0940, Sharpe=+0.3762
- `combo_sig_product__rsi_opening__max_down_ret`: Train IC=+0.1380, Lock IC=+0.0788, Sharpe=+0.1181
- `combo_sig_product__high_low_sequence_momentum__max_down_ret`: Train IC=+0.1380, Lock IC=+0.0788, Sharpe=+0.1181

### 159915ETF — `single` (103 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 41 | 41 | 5 | 36 | 0 | 12% | 88% |
| recency_ratio >= 2.5 (late-concentrated) | 36 | 36 | 2 | 31 | 3 | 6% | 86% |

**Top TP killed by recency_ratio cap:**
- `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2060, Lock IC=+0.1337, Sharpe=+1.5702
- `combo_z_sum__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2060, Lock IC=+0.1337, Sharpe=+1.5702
- `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2777, Lock IC=+0.1372, Sharpe=+1.4558
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2113, Lock IC=+0.1351, Sharpe=+1.3658
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2113, Lock IC=+0.1351, Sharpe=+1.3658

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `shaved_bar_trend_conviction` | 1 | 16 | 17 | 6% |  |
| `volatility_expansion_trend_vector` | 1 | 30 | 31 | 3% |  |
| `max_up_ret` | 2 | 137 | 139 | 1% |  |
| `gap_pct` | 0 | 17 | 17 | 0% |  |
| `vwap_close_divergence_trend` | 0 | 23 | 23 | 0% |  |
| `demark_setup_reversal_early` | 0 | 12 | 12 | 0% |  |
| `trend_day_regime_conviction` | 0 | 8 | 8 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 7 | 7 | 0% |  |
| `star50_limit_proximity_early` | 0 | 70 | 70 | 0% |  |
| `rsi_opening` | 0 | 3 | 3 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 4 | 4 | 0% |  |
| `yesterday_early_trend` | 0 | 3 | 3 | 0% |  |
| `keltner_squeeze_width` | 0 | 2 | 2 | 0% |  |
| `close_vs_open_range` | 0 | 35 | 35 | 0% |  |
| `late_bar_momentum` | 0 | 2 | 2 | 0% |  |
| `early_body_momentum` | 0 | 21 | 21 | 0% |  |
| `volume_weighted_price_position` | 0 | 8 | 8 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 15 | 15 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 99 | 99 | 0% |  |
| `early_late_momentum_divergence` | 0 | 5 | 5 | 0% |  |
| `bar_ret_0` | 0 | 66 | 66 | 0% |  |
| `h2_l2_pullback_continuation` | 0 | 15 | 15 | 0% |  |
| `bar_body_rng_0` | 0 | 47 | 47 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 80 | 80 | 0% |  |
| `limit_down_proximity_early` | 0 | 2 | 2 | 0% |  |
| `body_size_progression` | 0 | 6 | 6 | 0% |  |
| `early_order_flow_imbalance` | 0 | 12 | 12 | 0% |  |
| `yesterday_first_30min_return` | 0 | 5 | 5 | 0% |  |
| `smooth_momentum_structure` | 0 | 5 | 5 | 0% |  |
| `max_down_ret` | 0 | 41 | 41 | 0% |  |
| `net_volume_flow` | 0 | 24 | 24 | 0% |  |
| `trend_bar_close_consistency` | 0 | 12 | 12 | 0% |  |
| `volume_price_confirmation` | 0 | 5 | 5 | 0% |  |
| `first_bar_return` | 0 | 26 | 26 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=195, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=45, FP rate=4%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=94, FP rate=0%

