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

| ETF | Side | Admitted | FP | Median | TP | FP Rate | Prod Score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 25 | 10 | 13 | 2 | 40% | 0.16 |
| 500ETF | single | 29 | 0 | 16 | 13 | 0% | 0.57 |
| 159915ETF | single | 30 | 1 | 7 | 22 | 3% | 0.79 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=10, TP=2)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| weak_link_cv | 1.255 | 1.807 | 1.236 | 1.807 | -1.02 | 0.935 | 73% |
| half_ratio | 1.906 | 1.310 | 1.410 | 1.310 | +0.56 | 0.594 | 75% |
| n_negative_years | 0.800 | 1.000 | 1.000 | 1.000 | -0.47 | 0.000 | 75% |
| ic_cv | 0.956 | 1.025 | 0.903 | 1.025 | -0.42 | 0.678 | 75% |
| ic_std_across_regimes | 0.048 | 0.051 | 0.047 | 0.051 | -0.23 | 0.029 | 75% |
| recency_ratio | 0.663 | 0.494 | 0.931 | 0.494 | +0.09 | 0.317 | 83% |
| n_negative_regimes | 0.500 | 0.500 | 0.500 | 0.500 | +0.00 | 0.000 | 75% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0760, Sharpe=-2.1231)
- Admission: Train IC=+0.1637, Deflated=+0.1628, IR=0.75, Mono=0.73, p=0.0014, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.051 | 2016: +0.049 | 2017: +0.035 | 2018: +0.008 | 2019: +0.070 | 2020: +0.043 | 2021: -0.065 | 2022: +0.027 | 2023: +0.096 | 2024: +0.099 | 2025: -0.177 | 2026: +0.060
- Yearly Tail ICs:   2015: -0.013 | 2016: +0.053 | 2017: +0.104 | 2018: +0.205 | 2019: +0.329 | 2020: +0.220 | 2021: -0.001 | 2022: +0.120 | 2023: +0.404 | 2024: +0.067 | 2025: -0.258 | 2026: +0.053
- IC CV=1.27, Neg years (linear/tail)=1/1 of 8, Half ratio=0.99, Recency ratio=4.55
- Early IC=+0.0214, Recent IC=+0.0974, 1st-half IC=+0.0368, 2nd-half IC=+0.0363, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=1.06, neg years=2)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.029, Q3_mid=-0.070, Q4=+0.047, Q5_high_vol=+0.094

**`combo_mean__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0365, Sharpe=-1.6583)
- Admission: Train IC=+0.2523, Deflated=+0.2529, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.080 | 2017: -0.034 | 2018: +0.160 | 2019: +0.072 | 2020: +0.053 | 2021: +0.175 | 2022: +0.015 | 2023: +0.160 | 2024: +0.064 | 2025: +0.057 | 2026: -0.166
- Yearly Tail ICs:   2015: -0.023 | 2016: +0.177 | 2017: +0.157 | 2018: +0.341 | 2019: +0.358 | 2020: +0.125 | 2021: +0.374 | 2022: +0.208 | 2023: +0.245 | 2024: +0.290 | 2025: -0.131 | 2026: -0.344
- IC CV=0.85, Neg years (linear/tail)=1/0 of 8, Half ratio=1.81, Recency ratio=1.78
- Early IC=+0.0627, Recent IC=+0.1118, 1st-half IC=+0.0615, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.085, Q3_mid=+0.028, Q4=+0.054, Q5_high_vol=+0.212

**`combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=-0.0133, Sharpe=-1.5530)
- Admission: Train IC=+0.1264, Deflated=+0.1276, IR=0.47, Mono=0.66, p=0.0124, MaxCorr=0.50
- Yearly Linear ICs: 2015: -0.054 | 2016: -0.023 | 2017: +0.030 | 2018: +0.101 | 2019: +0.077 | 2020: +0.028 | 2021: +0.092 | 2022: +0.022 | 2023: +0.061 | 2024: +0.004 | 2025: +0.026 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.076 | 2016: -0.017 | 2017: +0.226 | 2018: +0.164 | 2019: +0.162 | 2020: +0.060 | 2021: +0.230 | 2022: +0.050 | 2023: +0.158 | 2024: +0.013 | 2025: +0.050 | 2026: -0.255
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.49
- Early IC=+0.0653, Recent IC=+0.0321, 1st-half IC=+0.0610, 2nd-half IC=+0.0457, Neg regimes=1/5
- Weak component: `double_bottom_bull_flag_early` (CV=1.91, neg years=2)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.038, Q3_mid=+0.053, Q4=+0.111, Q5_high_vol=-0.008

**`combo_min__bar_body_rng_0__demark_setup_reversal_early`** (Lock IC=-0.0600, Sharpe=-1.4098)
- Admission: Train IC=+0.1682, Deflated=+0.1694, IR=0.50, Mono=0.68, p=0.0012, MaxCorr=0.40
- Yearly Linear ICs: 2015: -0.084 | 2016: -0.011 | 2017: +0.118 | 2018: +0.112 | 2019: +0.049 | 2020: -0.010 | 2021: +0.099 | 2022: -0.079 | 2023: +0.029 | 2024: +0.086 | 2025: -0.048 | 2026: -0.066
- Yearly Tail ICs:   2015: -0.163 | 2016: -0.018 | 2017: +0.168 | 2018: +0.273 | 2019: -0.114 | 2020: +0.096 | 2021: +0.391 | 2022: +0.002 | 2023: +0.206 | 2024: +0.062 | 2025: -0.191 | 2026: -0.007
- IC CV=1.27, Neg years (linear/tail)=2/1 of 8, Half ratio=0.44, Recency ratio=0.50
- Early IC=+0.1151, Recent IC=+0.0575, 1st-half IC=+0.0653, 2nd-half IC=+0.0287, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=1.65, neg years=2)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.019, Q3_mid=+0.061, Q4=+0.046, Q5_high_vol=+0.032

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0223, Sharpe=-1.3571)
- Admission: Train IC=+0.2655, Deflated=+0.2657, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.091 | 2017: +0.020 | 2018: +0.182 | 2019: +0.072 | 2020: -0.000 | 2021: +0.133 | 2022: +0.045 | 2023: +0.170 | 2024: +0.055 | 2025: +0.022 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.083 | 2017: +0.154 | 2018: +0.376 | 2019: +0.248 | 2020: +0.086 | 2021: +0.371 | 2022: +0.169 | 2023: +0.381 | 2024: +0.225 | 2025: -0.048 | 2026: -0.016
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.46, Recency ratio=1.11
- Early IC=+0.1009, Recent IC=+0.1125, 1st-half IC=+0.0717, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.079, Q3_mid=+0.041, Q4=+0.072, Q5_high_vol=+0.177

**`combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.0022, Sharpe=-1.3090)
- Admission: Train IC=+0.2499, Deflated=+0.2501, IR=0.67, Mono=0.78, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.084 | 2017: +0.039 | 2018: +0.222 | 2019: +0.067 | 2020: -0.023 | 2021: +0.147 | 2022: +0.065 | 2023: +0.177 | 2024: +0.018 | 2025: +0.070 | 2026: -0.099
- Yearly Tail ICs:   2015: +0.041 | 2016: -0.038 | 2017: +0.224 | 2018: +0.300 | 2019: +0.288 | 2020: +0.057 | 2021: +0.441 | 2022: +0.310 | 2023: +0.375 | 2024: +0.061 | 2025: -0.061 | 2026: -0.163
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.36, Recency ratio=0.75
- Early IC=+0.1305, Recent IC=+0.0975, 1st-half IC=+0.0789, 2nd-half IC=+0.1075, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.098, Q3_mid=+0.062, Q4=+0.075, Q5_high_vol=+0.151

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0388, Sharpe=-0.9976)
- Admission: Train IC=+0.2042, Deflated=+0.2050, IR=0.89, Mono=0.83, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.95, Neg years (linear/tail)=0/0 of 8, Half ratio=2.70, Recency ratio=1.68
- Early IC=+0.0659, Recent IC=+0.1111, 1st-half IC=+0.0425, 2nd-half IC=+0.1149, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.094, Q3_mid=-0.004, Q4=+0.043, Q5_high_vol=+0.182

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0391, Sharpe=-0.9630)
- Admission: Train IC=+0.2074, Deflated=+0.2081, IR=0.83, Mono=0.80, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.039 | 2017: +0.008 | 2018: +0.136 | 2019: +0.044 | 2020: +0.004 | 2021: +0.171 | 2022: +0.037 | 2023: +0.200 | 2024: +0.032 | 2025: +0.096 | 2026: -0.200
- Yearly Tail ICs:   2015: +0.107 | 2016: +0.233 | 2017: +0.213 | 2018: +0.374 | 2019: +0.124 | 2020: +0.085 | 2021: +0.324 | 2022: +0.252 | 2023: +0.202 | 2024: +0.187 | 2025: +0.119 | 2026: -0.372
- IC CV=0.92, Neg years (linear/tail)=0/0 of 8, Half ratio=2.68, Recency ratio=1.61
- Early IC=+0.0723, Recent IC=+0.1164, 1st-half IC=+0.0439, 2nd-half IC=+0.1176, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.099, Q3_mid=-0.001, Q4=+0.042, Q5_high_vol=+0.183

**`combo_ratio__first_bar_return__volume_surge_direction`** (Lock IC=-0.0091, Sharpe=-0.5472)
- Admission: Train IC=+0.1306, Deflated=+0.1312, IR=0.32, Mono=0.66, p=0.0094, MaxCorr=0.03
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.144 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.393 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.114
- IC CV=0.71, Neg years (linear/tail)=1/2 of 8, Half ratio=1.09, Recency ratio=0.60
- Early IC=+0.1140, Recent IC=+0.0687, 1st-half IC=+0.0760, 2nd-half IC=+0.0827, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10, neg years=2)
- Regime ICs: Q1_low_vol=+0.058, Q2=+0.080, Q3_mid=+0.049, Q4=+0.056, Q5_high_vol=+0.148

**`first_30min_return`** (Lock IC=-0.0197, Sharpe=-0.4422)
- Admission: Train IC=+0.1189, Deflated=+0.1197, IR=0.45, Mono=0.69, p=0.0188, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.027 | 2016: +0.026 | 2017: -0.078 | 2018: +0.052 | 2019: +0.024 | 2020: +0.040 | 2021: +0.159 | 2022: +0.039 | 2023: +0.120 | 2024: +0.048 | 2025: +0.091 | 2026: -0.187
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.115 | 2017: +0.044 | 2018: +0.131 | 2019: +0.177 | 2020: -0.025 | 2021: +0.258 | 2022: +0.118 | 2023: +0.256 | 2024: +0.238 | 2025: +0.303 | 2026: -0.328
- IC CV=1.29, Neg years (linear/tail)=1/1 of 8, Half ratio=5.79, Recency ratio=-6.45
- Early IC=-0.0130, Recent IC=+0.0837, 1st-half IC=+0.0169, 2nd-half IC=+0.0979, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.005, Q2=+0.071, Q3_mid=-0.001, Q4=+0.058, Q5_high_vol=+0.123

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0153, Sharpe=-0.1443)
- Admission: Train IC=+0.1698, Deflated=+0.1696, IR=0.51, Mono=0.65, p=0.0012, MaxCorr=0.38
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
- Admission: Train IC=+0.1986, Deflated=+0.1991, IR=0.58, Mono=0.72, p=0.0002, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.080 | 2016: +0.040 | 2017: -0.059 | 2018: +0.144 | 2019: +0.097 | 2020: +0.039 | 2021: +0.142 | 2022: +0.100 | 2023: +0.086 | 2024: -0.004 | 2025: +0.074 | 2026: +0.063
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.074 | 2017: -0.142 | 2018: +0.322 | 2019: +0.206 | 2020: +0.145 | 2021: +0.514 | 2022: +0.334 | 2023: +0.186 | 2024: +0.119 | 2025: +0.014 | 2026: +0.008
- IC CV=0.98, Neg years (linear/tail)=2/1 of 8, Half ratio=1.48, Recency ratio=0.96
- Early IC=+0.0425, Recent IC=+0.0409, 1st-half IC=+0.0597, 2nd-half IC=+0.0884, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=-0.001, Q2=+0.062, Q3_mid=+0.079, Q4=+0.058, Q5_high_vol=+0.154

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0544, Sharpe=-0.0805)
- Admission: Train IC=+0.2766, Deflated=+0.2766, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.80, Neg years (linear/tail)=1/0 of 8, Half ratio=1.14, Recency ratio=1.31
- Early IC=+0.0834, Recent IC=+0.1090, 1st-half IC=+0.0944, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.023, Q2=+0.054, Q3_mid=+0.094, Q4=+0.081, Q5_high_vol=+0.219

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0463, Sharpe=-0.5117)
- Admission: Train IC=+0.2881, Deflated=+0.2875, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.057 | 2017: -0.016 | 2018: +0.189 | 2019: +0.144 | 2020: +0.031 | 2021: +0.133 | 2022: +0.047 | 2023: +0.177 | 2024: +0.042 | 2025: +0.096 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.332 | 2016: +0.097 | 2017: +0.092 | 2018: +0.385 | 2019: +0.206 | 2020: +0.187 | 2021: +0.514 | 2022: +0.201 | 2023: +0.297 | 2024: +0.223 | 2025: -0.006 | 2026: +0.299
- IC CV=0.77, Neg years (linear/tail)=1/0 of 8, Half ratio=1.13, Recency ratio=1.26
- Early IC=+0.0866, Recent IC=+0.1095, 1st-half IC=+0.0932, 2nd-half IC=+0.1049, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.062, Q3_mid=+0.086, Q4=+0.082, Q5_high_vol=+0.204

**`combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__first_bar_sentiment`** (Lock IC=+0.0313, Sharpe=-0.3645)
- Admission: Train IC=+0.1965, Deflated=+0.1951, IR=0.56, Mono=0.74, p=0.0002, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.123 | 2017: -0.019 | 2018: +0.189 | 2019: +0.043 | 2020: +0.035 | 2021: +0.121 | 2022: +0.095 | 2023: +0.091 | 2024: -0.023 | 2025: +0.007 | 2026: +0.068
- Yearly Tail ICs:   2015: -0.081 | 2016: +0.130 | 2017: -0.060 | 2018: +0.408 | 2019: +0.117 | 2020: +0.106 | 2021: +0.226 | 2022: +0.347 | 2023: +0.073 | 2024: +0.227 | 2025: -0.052 | 2026: +0.121
- IC CV=1.01, Neg years (linear/tail)=2/1 of 8, Half ratio=1.11, Recency ratio=0.40
- Early IC=+0.0847, Recent IC=+0.0342, 1st-half IC=+0.0687, 2nd-half IC=+0.0760, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.077, Q3_mid=+0.006, Q4=+0.062, Q5_high_vol=+0.170

**`combo_min__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=+0.0303, Sharpe=-0.4943)
- Admission: Train IC=+0.1898, Deflated=+0.1891, IR=0.57, Mono=0.71, p=0.0002, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.088 | 2016: +0.073 | 2017: -0.049 | 2018: +0.215 | 2019: +0.079 | 2020: +0.053 | 2021: +0.129 | 2022: +0.039 | 2023: +0.138 | 2024: +0.017 | 2025: +0.109 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.021 | 2017: -0.154 | 2018: +0.243 | 2019: +0.208 | 2020: +0.201 | 2021: +0.296 | 2022: +0.121 | 2023: +0.223 | 2024: +0.222 | 2025: +0.340 | 2026: -0.198
- IC CV=0.99, Neg years (linear/tail)=1/1 of 8, Half ratio=1.07, Recency ratio=0.93
- Early IC=+0.0831, Recent IC=+0.0771, 1st-half IC=+0.0812, 2nd-half IC=+0.0865, Neg regimes=1/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=-0.006, Q2=+0.111, Q3_mid=+0.021, Q4=+0.079, Q5_high_vol=+0.184

**`combo_min__bar_body_rng_0__volume_surge_direction`** (Lock IC=+0.0300, Sharpe=-0.0790)
- Admission: Train IC=+0.2339, Deflated=+0.2334, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.059 | 2016: +0.029 | 2017: -0.002 | 2018: +0.189 | 2019: +0.080 | 2020: +0.037 | 2021: +0.160 | 2022: +0.026 | 2023: +0.166 | 2024: +0.015 | 2025: +0.085 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.261 | 2016: -0.200 | 2017: +0.047 | 2018: +0.188 | 2019: +0.034 | 2020: +0.263 | 2021: +0.464 | 2022: -0.044 | 2023: +0.423 | 2024: +0.271 | 2025: +0.386 | 2026: -0.259
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=1.16, Recency ratio=0.97
- Early IC=+0.0937, Recent IC=+0.0906, 1st-half IC=+0.0814, 2nd-half IC=+0.0944, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.104, Q3_mid=+0.056, Q4=+0.076, Q5_high_vol=+0.148

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.0296, Sharpe=-0.6485)
- Admission: Train IC=+0.2023, Deflated=+0.2026, IR=0.69, Mono=0.78, p=0.0002, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.071 | 2017: -0.076 | 2018: +0.173 | 2019: +0.076 | 2020: +0.027 | 2021: +0.141 | 2022: +0.063 | 2023: +0.132 | 2024: +0.004 | 2025: +0.077 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.247 | 2017: -0.088 | 2018: +0.363 | 2019: +0.275 | 2020: +0.165 | 2021: +0.412 | 2022: +0.198 | 2023: +0.264 | 2024: +0.041 | 2025: +0.125 | 2026: -0.083
- IC CV=1.14, Neg years (linear/tail)=1/1 of 8, Half ratio=1.76, Recency ratio=1.41
- Early IC=+0.0484, Recent IC=+0.0681, 1st-half IC=+0.0536, 2nd-half IC=+0.0942, Neg regimes=1/5
- Weak component: `demark_setup_reversal_early` (CV=1.65)
- Regime ICs: Q1_low_vol=-0.024, Q2=+0.062, Q3_mid=+0.045, Q4=+0.055, Q5_high_vol=+0.213

**`combo_tri_max__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0241, Sharpe=-0.9421)
- Admission: Train IC=+0.1895, Deflated=+0.1896, IR=0.62, Mono=0.73, p=0.0002, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.072 | 2017: +0.047 | 2018: +0.199 | 2019: +0.087 | 2020: -0.029 | 2021: +0.161 | 2022: +0.051 | 2023: +0.179 | 2024: -0.002 | 2025: +0.116 | 2026: -0.127
- Yearly Tail ICs:   2015: +0.091 | 2016: +0.024 | 2017: +0.156 | 2018: +0.445 | 2019: +0.129 | 2020: +0.005 | 2021: +0.425 | 2022: +0.213 | 2023: +0.261 | 2024: +0.202 | 2025: +0.126 | 2026: -0.300
- IC CV=0.92, Neg years (linear/tail)=2/0 of 8, Half ratio=1.32, Recency ratio=0.72
- Early IC=+0.1230, Recent IC=+0.0885, 1st-half IC=+0.0764, 2nd-half IC=+0.1011, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.115, Q3_mid=+0.053, Q4=+0.071, Q5_high_vol=+0.125

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0200, Sharpe=-0.6924)
- Admission: Train IC=+0.2900, Deflated=+0.2899, IR=0.77, Mono=0.74, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.096 | 2017: +0.003 | 2018: +0.184 | 2019: +0.113 | 2020: +0.043 | 2021: +0.135 | 2022: +0.037 | 2023: +0.165 | 2024: +0.056 | 2025: +0.047 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.096 | 2017: +0.082 | 2018: +0.374 | 2019: +0.242 | 2020: +0.230 | 2021: +0.520 | 2022: +0.121 | 2023: +0.327 | 2024: +0.227 | 2025: -0.034 | 2026: +0.159
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.18
- Early IC=+0.0938, Recent IC=+0.1105, 1st-half IC=+0.0900, 2nd-half IC=+0.1024, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.062, Q3_mid=+0.072, Q4=+0.064, Q5_high_vol=+0.215

**`combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0164, Sharpe=-0.7568)
- Admission: Train IC=+0.2578, Deflated=+0.2581, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.054 | 2017: -0.066 | 2018: +0.214 | 2019: +0.120 | 2020: +0.054 | 2021: +0.169 | 2022: +0.026 | 2023: +0.133 | 2024: +0.052 | 2025: +0.044 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.165 | 2017: +0.008 | 2018: +0.372 | 2019: +0.363 | 2020: +0.149 | 2021: +0.501 | 2022: +0.251 | 2023: +0.084 | 2024: +0.271 | 2025: -0.060 | 2026: +0.199
- IC CV=0.95, Neg years (linear/tail)=1/0 of 8, Half ratio=1.15, Recency ratio=1.25
- Early IC=+0.0737, Recent IC=+0.0923, 1st-half IC=+0.0904, 2nd-half IC=+0.1043, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.029, Q2=+0.052, Q3_mid=+0.104, Q4=+0.071, Q5_high_vol=+0.233

**`combo_max__first_bar_return__volume_surge_direction`** (Lock IC=+0.0104, Sharpe=-0.1272)
- Admission: Train IC=+0.2280, Deflated=+0.2267, IR=0.70, Mono=0.77, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.086 | 2017: -0.009 | 2018: +0.199 | 2019: +0.145 | 2020: -0.004 | 2021: +0.043 | 2022: +0.048 | 2023: +0.168 | 2024: +0.026 | 2025: +0.075 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.154 | 2016: -0.018 | 2017: -0.017 | 2018: +0.420 | 2019: +0.331 | 2020: +0.160 | 2021: +0.014 | 2022: +0.275 | 2023: +0.180 | 2024: +0.305 | 2025: +0.339 | 2026: -0.101
- IC CV=0.99, Neg years (linear/tail)=2/1 of 8, Half ratio=0.80, Recency ratio=1.03
- Early IC=+0.0946, Recent IC=+0.0971, 1st-half IC=+0.0878, 2nd-half IC=+0.0701, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.093, Q3_mid=+0.046, Q4=+0.076, Q5_high_vol=+0.128

**`combo_abs_diff__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0103, Sharpe=-0.9746)
- Admission: Train IC=+0.1050, Deflated=+0.1065, IR=0.47, Mono=0.70, p=0.0358, MaxCorr=0.42
- Yearly Linear ICs: 2015: +0.024 | 2016: +0.063 | 2017: +0.009 | 2018: +0.074 | 2019: +0.137 | 2020: -0.005 | 2021: +0.122 | 2022: -0.018 | 2023: +0.056 | 2024: -0.021 | 2025: +0.096 | 2026: -0.132
- Yearly Tail ICs:   2015: +0.058 | 2016: +0.104 | 2017: -0.279 | 2018: +0.221 | 2019: +0.108 | 2020: +0.198 | 2021: +0.213 | 2022: +0.010 | 2023: +0.307 | 2024: +0.189 | 2025: +0.147 | 2026: -0.191
- IC CV=1.33, Neg years (linear/tail)=3/1 of 8, Half ratio=0.77, Recency ratio=0.43
- Early IC=+0.0415, Recent IC=+0.0178, 1st-half IC=+0.0491, 2nd-half IC=+0.0380, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.016, Q3_mid=+0.056, Q4=+0.030, Q5_high_vol=+0.082

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0007, Sharpe=-1.2659)
- Admission: Train IC=+0.2456, Deflated=+0.2452, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.137 | 2016: +0.093 | 2017: -0.047 | 2018: +0.181 | 2019: +0.105 | 2020: +0.022 | 2021: +0.171 | 2022: +0.057 | 2023: +0.174 | 2024: +0.055 | 2025: +0.066 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.276 | 2016: +0.076 | 2017: -0.014 | 2018: +0.199 | 2019: +0.257 | 2020: +0.078 | 2021: +0.423 | 2022: +0.416 | 2023: +0.226 | 2024: +0.301 | 2025: +0.021 | 2026: -0.023
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=1.72, Recency ratio=1.71
- Early IC=+0.0671, Recent IC=+0.1149, 1st-half IC=+0.0704, 2nd-half IC=+0.1209, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.066, Q3_mid=+0.056, Q4=+0.066, Q5_high_vol=+0.218

### 500ETF — `single` Median Features

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0883, Sharpe=-0.5698)
- Admission: Train IC=+0.2689, Deflated=+0.2675, IR=1.07, Mono=0.83, p=0.0000, MaxCorr=0.67
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.123 | 2017: +0.222 | 2018: +0.178 | 2019: +0.172 | 2020: +0.171 | 2021: +0.141 | 2022: +0.008 | 2023: +0.106 | 2024: +0.163 | 2025: +0.094 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.247 | 2017: +0.328 | 2018: +0.514 | 2019: +0.346 | 2020: +0.235 | 2021: +0.278 | 2022: +0.140 | 2023: +0.112 | 2024: +0.297 | 2025: -0.002 | 2026: +0.151
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.67
- Early IC=+0.2002, Recent IC=+0.1341, 1st-half IC=+0.1783, 2nd-half IC=+0.1107, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.005, Q3_mid=+0.122, Q4=+0.123, Q5_high_vol=+0.235

**`combo_min__early_body_momentum__max_down_ret`** (Lock IC=+0.0745, Sharpe=-0.5203)
- Admission: Train IC=+0.1907, Deflated=+0.1904, IR=0.59, Mono=0.74, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.065 | 2017: +0.164 | 2018: +0.105 | 2019: +0.080 | 2020: +0.120 | 2021: +0.056 | 2022: +0.107 | 2023: +0.077 | 2024: +0.107 | 2025: +0.126 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.300 | 2016: -0.113 | 2017: +0.131 | 2018: +0.073 | 2019: +0.171 | 2020: +0.143 | 2021: +0.364 | 2022: +0.319 | 2023: +0.183 | 2024: +0.234 | 2025: +0.082 | 2026: -0.056
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.68
- Early IC=+0.1345, Recent IC=+0.0918, 1st-half IC=+0.1043, 2nd-half IC=+0.0946, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.007, Q3_mid=+0.120, Q4=+0.089, Q5_high_vol=+0.123

**`combo_tri_max__first_bar_sentiment__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0702, Sharpe=-0.3842)
- Admission: Train IC=+0.1753, Deflated=+0.1746, IR=0.56, Mono=0.71, p=0.0004, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.290 | 2016: +0.105 | 2017: +0.163 | 2018: +0.150 | 2019: +0.089 | 2020: +0.113 | 2021: +0.111 | 2022: +0.118 | 2023: +0.024 | 2024: +0.096 | 2025: +0.062 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.207 | 2016: +0.121 | 2017: +0.141 | 2018: +0.138 | 2019: +0.229 | 2020: +0.085 | 2021: +0.132 | 2022: +0.290 | 2023: +0.041 | 2024: +0.121 | 2025: -0.014 | 2026: +0.001
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.38
- Early IC=+0.1568, Recent IC=+0.0604, 1st-half IC=+0.1239, 2nd-half IC=+0.0931, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.023, Q3_mid=+0.088, Q4=+0.144, Q5_high_vol=+0.125

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0573, Sharpe=-0.2479)
- Admission: Train IC=+0.2982, Deflated=+0.2978, IR=1.05, Mono=0.85, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.056 | 2017: +0.164 | 2018: +0.246 | 2019: +0.174 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145 | 2025: +0.095 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.450 | 2016: +0.051 | 2017: +0.191 | 2018: +0.407 | 2019: +0.229 | 2020: +0.221 | 2021: +0.337 | 2022: +0.238 | 2023: +0.314 | 2024: +0.298 | 2025: +0.104 | 2026: -0.330
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.59
- Early IC=+0.2051, Recent IC=+0.1217, 1st-half IC=+0.1755, 2nd-half IC=+0.1177, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.006, Q3_mid=+0.133, Q4=+0.148, Q5_high_vol=+0.215

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0527, Sharpe=-0.2479)
- Admission: Train IC=+0.2970, Deflated=+0.2966, IR=1.08, Mono=0.85, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.042 | 2017: +0.163 | 2018: +0.219 | 2019: +0.178 | 2020: +0.159 | 2021: +0.163 | 2022: +0.058 | 2023: +0.086 | 2024: +0.125 | 2025: +0.095 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.431 | 2016: +0.025 | 2017: +0.193 | 2018: +0.389 | 2019: +0.254 | 2020: +0.220 | 2021: +0.337 | 2022: +0.238 | 2023: +0.307 | 2024: +0.298 | 2025: +0.104 | 2026: -0.330
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.55
- Early IC=+0.1909, Recent IC=+0.1050, 1st-half IC=+0.1692, 2nd-half IC=+0.1102, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.001, Q3_mid=+0.122, Q4=+0.137, Q5_high_vol=+0.205

**`combo_tri_min__first_bar_sentiment__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0527, Sharpe=-0.4717)
- Admission: Train IC=+0.2648, Deflated=+0.2648, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.57
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.077 | 2017: +0.155 | 2018: +0.152 | 2019: +0.077 | 2020: +0.085 | 2021: +0.048 | 2022: +0.097 | 2023: +0.092 | 2024: +0.124 | 2025: +0.137 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.280 | 2016: -0.061 | 2017: +0.353 | 2018: +0.194 | 2019: +0.124 | 2020: +0.212 | 2021: +0.173 | 2022: +0.280 | 2023: +0.159 | 2024: +0.214 | 2025: +0.158 | 2026: -0.006
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.70
- Early IC=+0.1536, Recent IC=+0.1078, 1st-half IC=+0.1055, 2nd-half IC=+0.0952, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.006, Q3_mid=+0.088, Q4=+0.110, Q5_high_vol=+0.148

**`combo_tri_mean__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0488, Sharpe=-1.1019)
- Admission: Train IC=+0.2612, Deflated=+0.2607, IR=0.78, Mono=0.80, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.055 | 2017: +0.210 | 2018: +0.148 | 2019: +0.075 | 2020: +0.128 | 2021: +0.092 | 2022: +0.090 | 2023: +0.099 | 2024: +0.134 | 2025: +0.133 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.448 | 2016: +0.205 | 2017: +0.333 | 2018: +0.218 | 2019: +0.230 | 2020: +0.256 | 2021: +0.262 | 2022: +0.230 | 2023: +0.252 | 2024: +0.310 | 2025: +0.053 | 2026: -0.143
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.65
- Early IC=+0.1792, Recent IC=+0.1165, 1st-half IC=+0.1294, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.015, Q3_mid=+0.127, Q4=+0.105, Q5_high_vol=+0.142

**`combo_mean__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0469, Sharpe=-1.2311)
- Admission: Train IC=+0.2594, Deflated=+0.2588, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.095 | 2017: +0.214 | 2018: +0.198 | 2019: +0.106 | 2020: +0.115 | 2021: +0.099 | 2022: +0.097 | 2023: +0.078 | 2024: +0.153 | 2025: +0.120 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.039 | 2017: +0.255 | 2018: +0.345 | 2019: +0.137 | 2020: +0.180 | 2021: +0.374 | 2022: +0.269 | 2023: +0.219 | 2024: +0.337 | 2025: +0.063 | 2026: -0.260
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.56
- Early IC=+0.2060, Recent IC=+0.1156, 1st-half IC=+0.1444, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.229, Q2=+0.005, Q3_mid=+0.124, Q4=+0.126, Q5_high_vol=+0.159

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0451, Sharpe=-0.8388)
- Admission: Train IC=+0.2318, Deflated=+0.2311, IR=0.82, Mono=0.75, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.306 | 2016: +0.113 | 2017: +0.192 | 2018: +0.218 | 2019: +0.121 | 2020: +0.145 | 2021: +0.156 | 2022: +0.058 | 2023: +0.093 | 2024: +0.118 | 2025: +0.013 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.135 | 2017: +0.439 | 2018: +0.357 | 2019: +0.364 | 2020: +0.148 | 2021: +0.229 | 2022: +0.113 | 2023: +0.179 | 2024: +0.041 | 2025: -0.070 | 2026: +0.027
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.51
- Early IC=+0.2050, Recent IC=+0.1056, 1st-half IC=+0.1588, 2nd-half IC=+0.1075, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.000, Q3_mid=+0.080, Q4=+0.157, Q5_high_vol=+0.209

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0427, Sharpe=-0.2324)
- Admission: Train IC=+0.2524, Deflated=+0.2516, IR=1.00, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.091 | 2017: +0.132 | 2018: +0.260 | 2019: +0.170 | 2020: +0.173 | 2021: +0.170 | 2022: +0.068 | 2023: +0.082 | 2024: +0.140 | 2025: +0.068 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.214 | 2016: +0.155 | 2017: +0.302 | 2018: +0.602 | 2019: +0.200 | 2020: +0.172 | 2021: +0.293 | 2022: +0.165 | 2023: +0.256 | 2024: +0.191 | 2025: -0.034 | 2026: +0.013
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.57
- Early IC=+0.1960, Recent IC=+0.1110, 1st-half IC=+0.1767, 2nd-half IC=+0.1171, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.015, Q3_mid=+0.105, Q4=+0.119, Q5_high_vol=+0.256

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0337, Sharpe=-1.4167)
- Admission: Train IC=+0.2577, Deflated=+0.2564, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.106 | 2017: +0.201 | 2018: +0.209 | 2019: +0.129 | 2020: +0.142 | 2021: +0.089 | 2022: +0.105 | 2023: +0.119 | 2024: +0.137 | 2025: +0.119 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.254 | 2017: +0.358 | 2018: +0.384 | 2019: +0.236 | 2020: +0.249 | 2021: +0.298 | 2022: +0.163 | 2023: +0.132 | 2024: +0.354 | 2025: -0.127 | 2026: -0.132
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.62
- Early IC=+0.2048, Recent IC=+0.1279, 1st-half IC=+0.1552, 2nd-half IC=+0.1139, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.010, Q3_mid=+0.120, Q4=+0.127, Q5_high_vol=+0.210

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0289, Sharpe=-0.4555)
- Admission: Train IC=+0.2882, Deflated=+0.2875, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.103 | 2017: +0.142 | 2018: +0.284 | 2019: +0.177 | 2020: +0.173 | 2021: +0.171 | 2022: +0.055 | 2023: +0.093 | 2024: +0.161 | 2025: +0.060 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.093 | 2017: +0.301 | 2018: +0.612 | 2019: +0.247 | 2020: +0.024 | 2021: +0.311 | 2022: +0.155 | 2023: +0.095 | 2024: +0.368 | 2025: +0.165 | 2026: -0.193
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.59
- Early IC=+0.2133, Recent IC=+0.1268, 1st-half IC=+0.1870, 2nd-half IC=+0.1223, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.005, Q3_mid=+0.133, Q4=+0.139, Q5_high_vol=+0.259

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0247, Sharpe=-1.6524)
- Admission: Train IC=+0.2006, Deflated=+0.1998, IR=0.50, Mono=0.70, p=0.0000, MaxCorr=0.78
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
- Admission: Train IC=+0.1810, Deflated=+0.1810, IR=0.54, Mono=0.66, p=0.0002, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.034 | 2017: +0.155 | 2018: +0.199 | 2019: +0.138 | 2020: +0.068 | 2021: +0.044 | 2022: +0.058 | 2023: +0.067 | 2024: +0.054 | 2025: +0.108 | 2026: -0.100
- Yearly Tail ICs:   2015: +0.237 | 2016: -0.042 | 2017: +0.209 | 2018: +0.425 | 2019: +0.231 | 2020: +0.166 | 2021: +0.145 | 2022: +0.174 | 2023: +0.106 | 2024: +0.160 | 2025: +0.159 | 2026: -0.386
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.34
- Early IC=+0.1770, Recent IC=+0.0606, 1st-half IC=+0.1285, 2nd-half IC=+0.0529, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.033, Q3_mid=+0.066, Q4=+0.113, Q5_high_vol=+0.117

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0206, Sharpe=-0.7130)
- Admission: Train IC=+0.1744, Deflated=+0.1740, IR=0.60, Mono=0.77, p=0.0006, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.121 | 2017: +0.116 | 2018: +0.277 | 2019: +0.078 | 2020: +0.110 | 2021: +0.083 | 2022: +0.127 | 2023: +0.036 | 2024: +0.101 | 2025: +0.073 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.148 | 2016: +0.089 | 2017: +0.306 | 2018: +0.479 | 2019: +0.081 | 2020: +0.190 | 2021: +0.206 | 2022: +0.012 | 2023: +0.064 | 2024: +0.172 | 2025: +0.148 | 2026: -0.305
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.35
- Early IC=+0.1966, Recent IC=+0.0687, 1st-half IC=+0.1384, 2nd-half IC=+0.0904, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.006, Q3_mid=+0.062, Q4=+0.118, Q5_high_vol=+0.180

### 159915ETF — `single` Median Features

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1161, Sharpe=-0.1261)
- Admission: Train IC=+0.1924, Deflated=+0.1914, IR=0.64, Mono=0.71, p=0.0002, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.168 | 2017: +0.029 | 2018: +0.133 | 2019: +0.128 | 2020: +0.137 | 2021: +0.158 | 2022: +0.146 | 2023: +0.134 | 2024: +0.077 | 2025: +0.135 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.174 | 2017: +0.193 | 2018: +0.300 | 2019: +0.155 | 2020: +0.091 | 2021: +0.455 | 2022: +0.116 | 2023: +0.293 | 2024: +0.147 | 2025: +0.105 | 2026: +0.109
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.29
- Early IC=+0.0815, Recent IC=+0.1054, 1st-half IC=+0.1104, 2nd-half IC=+0.1360, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.122, Q3_mid=+0.079, Q4=+0.118, Q5_high_vol=+0.169

**`combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1079, Sharpe=-0.2788)
- Admission: Train IC=+0.2028, Deflated=+0.2020, IR=0.46, Mono=0.68, p=0.0000, MaxCorr=0.56
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.023 | 2017: -0.058 | 2018: +0.036 | 2019: +0.135 | 2020: +0.037 | 2021: +0.133 | 2022: +0.143 | 2023: +0.143 | 2024: +0.054 | 2025: +0.066 | 2026: +0.166
- Yearly Tail ICs:   2015: +0.075 | 2016: -0.087 | 2017: -0.081 | 2018: +0.099 | 2019: +0.341 | 2020: +0.141 | 2021: +0.172 | 2022: +0.208 | 2023: +0.292 | 2024: +0.125 | 2025: -0.089 | 2026: +0.357
- IC CV=0.88, Neg years (linear/tail)=1/1 of 8, Half ratio=2.54, Recency ratio=-8.81
- Early IC=-0.0112, Recent IC=+0.0983, 1st-half IC=+0.0471, 2nd-half IC=+0.1194, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.046, Q3_mid=+0.091, Q4=+0.116, Q5_high_vol=+0.131

**`combo_max__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=+0.0916, Sharpe=-0.4785)
- Admission: Train IC=+0.2424, Deflated=+0.2422, IR=0.71, Mono=0.72, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.124 | 2017: -0.000 | 2018: +0.072 | 2019: +0.155 | 2020: +0.134 | 2021: +0.171 | 2022: +0.093 | 2023: +0.151 | 2024: +0.058 | 2025: +0.206 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.295 | 2016: -0.036 | 2017: +0.068 | 2018: +0.061 | 2019: +0.441 | 2020: +0.269 | 2021: +0.294 | 2022: +0.237 | 2023: +0.392 | 2024: +0.185 | 2025: +0.310 | 2026: -0.400
- IC CV=0.53, Neg years (linear/tail)=1/0 of 8, Half ratio=1.57, Recency ratio=2.89
- Early IC=+0.0361, Recent IC=+0.1042, 1st-half IC=+0.0795, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.082, Q3_mid=+0.136, Q4=+0.074, Q5_high_vol=+0.117

**`combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0813, Sharpe=-0.1094)
- Admission: Train IC=+0.1940, Deflated=+0.1952, IR=0.63, Mono=0.71, p=0.0002, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.072 | 2016: +0.062 | 2017: +0.019 | 2018: +0.026 | 2019: +0.149 | 2020: +0.033 | 2021: +0.161 | 2022: +0.084 | 2023: +0.113 | 2024: +0.094 | 2025: +0.167 | 2026: -0.045
- Yearly Tail ICs:   2015: -0.014 | 2016: +0.181 | 2017: +0.163 | 2018: -0.053 | 2019: +0.316 | 2020: +0.279 | 2021: +0.075 | 2022: +0.359 | 2023: +0.242 | 2024: +0.151 | 2025: +0.204 | 2026: -0.275
- IC CV=0.61, Neg years (linear/tail)=0/1 of 8, Half ratio=2.36, Recency ratio=4.52
- Early IC=+0.0229, Recent IC=+0.1036, 1st-half IC=+0.0518, 2nd-half IC=+0.1224, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.095, Q3_mid=+0.123, Q4=+0.136, Q5_high_vol=+0.030

**`combo_rank_min__impulse_bar_dominance__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0803, Sharpe=-0.6903)
- Admission: Train IC=+0.1960, Deflated=+0.1951, IR=0.50, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.001 | 2017: +0.026 | 2018: +0.021 | 2019: +0.089 | 2020: +0.031 | 2021: +0.120 | 2022: +0.109 | 2023: +0.148 | 2024: +0.079 | 2025: +0.119 | 2026: -0.010
- Yearly Tail ICs:   2015: -0.029 | 2016: +0.041 | 2017: +0.087 | 2018: +0.083 | 2019: +0.258 | 2020: -0.152 | 2021: +0.269 | 2022: +0.191 | 2023: +0.255 | 2024: +0.307 | 2025: +0.130 | 2026: -0.145
- IC CV=0.57, Neg years (linear/tail)=0/1 of 8, Half ratio=3.09, Recency ratio=5.20
- Early IC=+0.0224, Recent IC=+0.1164, 1st-half IC=+0.0381, 2nd-half IC=+0.1174, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.060, Q3_mid=+0.103, Q4=+0.082, Q5_high_vol=+0.054

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0732, Sharpe=-0.9166)
- Admission: Train IC=+0.2401, Deflated=+0.2408, IR=0.66, Mono=0.71, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.084 | 2017: +0.059 | 2018: +0.069 | 2019: +0.178 | 2020: +0.049 | 2021: +0.219 | 2022: +0.083 | 2023: +0.163 | 2024: +0.082 | 2025: +0.177 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.063 | 2017: +0.216 | 2018: +0.221 | 2019: +0.339 | 2020: +0.069 | 2021: +0.343 | 2022: +0.241 | 2023: +0.367 | 2024: +0.254 | 2025: +0.200 | 2026: -0.243
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.87, Recency ratio=1.92
- Early IC=+0.0637, Recent IC=+0.1225, 1st-half IC=+0.0786, 2nd-half IC=+0.1470, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.103, Q3_mid=+0.128, Q4=+0.117, Q5_high_vol=+0.120

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.0705, Sharpe=-1.2636)
- Admission: Train IC=+0.2118, Deflated=+0.2118, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.133 | 2017: +0.042 | 2018: +0.096 | 2019: +0.181 | 2020: +0.119 | 2021: +0.172 | 2022: +0.107 | 2023: +0.161 | 2024: +0.074 | 2025: +0.169 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.131 | 2017: +0.207 | 2018: +0.196 | 2019: +0.235 | 2020: +0.080 | 2021: +0.371 | 2022: +0.288 | 2023: +0.316 | 2024: +0.123 | 2025: +0.229 | 2026: -0.357
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.33, Recency ratio=1.70
- Early IC=+0.0691, Recent IC=+0.1174, 1st-half IC=+0.1021, 2nd-half IC=+0.1354, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.100, Q3_mid=+0.113, Q4=+0.103, Q5_high_vol=+0.121

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration`** (Lock IC=+0.0575, Sharpe=+0.6959)
- Admission: Train IC=+0.1451, Deflated=+0.1460, IR=0.44, Mono=0.67, p=0.0042, MaxCorr=0.25
- Yearly Linear ICs: 2015: +0.022 | 2016: +0.005 | 2017: +0.040 | 2018: +0.076 | 2019: +0.041 | 2020: +0.030 | 2021: +0.170 | 2022: +0.027 | 2023: +0.048 | 2024: -0.031 | 2025: +0.044 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.108 | 2017: +0.045 | 2018: +0.319 | 2019: +0.057 | 2020: +0.178 | 2021: +0.173 | 2022: +0.149 | 2023: +0.060 | 2024: +0.193 | 2025: +0.078 | 2026: +0.104
- IC CV=1.06, Neg years (linear/tail)=1/0 of 8, Half ratio=1.61, Recency ratio=0.14
- Early IC=+0.0581, Recent IC=+0.0083, 1st-half IC=+0.0385, 2nd-half IC=+0.0621, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.024, Q3_mid=+0.048, Q4=+0.030, Q5_high_vol=+0.129

**`combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=+0.0306, Sharpe=+0.1091)
- Admission: Train IC=+0.1905, Deflated=+0.1897, IR=0.54, Mono=0.72, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.074 | 2016: +0.088 | 2017: -0.045 | 2018: +0.216 | 2019: +0.095 | 2020: +0.051 | 2021: +0.124 | 2022: +0.054 | 2023: +0.133 | 2024: +0.010 | 2025: +0.099 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.183 | 2016: +0.054 | 2017: -0.157 | 2018: +0.314 | 2019: +0.254 | 2020: +0.197 | 2021: +0.296 | 2022: +0.127 | 2023: +0.296 | 2024: +0.156 | 2025: +0.339 | 2026: -0.229
- IC CV=0.98, Neg years (linear/tail)=1/1 of 8, Half ratio=1.01, Recency ratio=0.85
- Early IC=+0.0848, Recent IC=+0.0717, 1st-half IC=+0.0834, 2nd-half IC=+0.0839, Neg regimes=1/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=-0.003, Q2=+0.114, Q3_mid=+0.022, Q4=+0.084, Q5_high_vol=+0.177

### 500ETF — `single` True Positives

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0661, Sharpe=+1.4473)
- Admission: Train IC=+0.1843, Deflated=+0.1829, IR=0.58, Mono=0.69, p=0.0002, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.097 | 2017: +0.143 | 2018: +0.183 | 2019: +0.076 | 2020: +0.106 | 2021: +0.120 | 2022: +0.098 | 2023: -0.003 | 2024: +0.128 | 2025: +0.092 | 2026: +0.032
- Yearly Tail ICs:   2015: +0.413 | 2016: +0.171 | 2017: +0.267 | 2018: +0.413 | 2019: +0.079 | 2020: +0.098 | 2021: +0.343 | 2022: +0.070 | 2023: +0.048 | 2024: +0.169 | 2025: +0.232 | 2026: +0.367
- IC CV=0.48, Neg years (linear/tail)=1/0 of 8, Half ratio=0.80, Recency ratio=0.38
- Early IC=+0.1629, Recent IC=+0.0623, 1st-half IC=+0.1197, 2nd-half IC=+0.0956, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.027, Q3_mid=+0.037, Q4=+0.083, Q5_high_vol=+0.211

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1034, Sharpe=+1.0177)
- Admission: Train IC=+0.1469, Deflated=+0.1469, IR=0.50, Mono=0.67, p=0.0040, MaxCorr=0.12
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052 | 2022: +0.096 | 2023: +0.046 | 2024: +0.073 | 2025: +0.148 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.229 | 2017: +0.386 | 2018: +0.332 | 2019: +0.207 | 2020: +0.271 | 2021: +0.214 | 2022: -0.027 | 2023: +0.087 | 2024: +0.035 | 2025: +0.246 | 2026: +0.214
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.34
- Early IC=+0.1761, Recent IC=+0.0591, 1st-half IC=+0.1355, 2nd-half IC=+0.0682, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.148, Q2=-0.015, Q3_mid=+0.115, Q4=+0.160, Q5_high_vol=+0.116

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0959, Sharpe=+0.5933)
- Admission: Train IC=+0.2070, Deflated=+0.2069, IR=0.58, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.069 | 2017: +0.192 | 2018: +0.152 | 2019: +0.175 | 2020: +0.115 | 2021: +0.089 | 2022: +0.033 | 2023: +0.063 | 2024: +0.109 | 2025: +0.130 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.125 | 2017: +0.226 | 2018: +0.380 | 2019: +0.338 | 2020: +0.229 | 2021: +0.062 | 2022: +0.122 | 2023: +0.116 | 2024: +0.315 | 2025: +0.140 | 2026: +0.185
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.47, Recency ratio=0.50
- Early IC=+0.1720, Recent IC=+0.0859, 1st-half IC=+0.1454, 2nd-half IC=+0.0686, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.208, Q2=-0.029, Q3_mid=+0.063, Q4=+0.138, Q5_high_vol=+0.167

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0958, Sharpe=+0.5075)
- Admission: Train IC=+0.2267, Deflated=+0.2261, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.092 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.142 | 2021: +0.098 | 2022: +0.041 | 2023: +0.078 | 2024: +0.091 | 2025: +0.124 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.155 | 2017: +0.169 | 2018: +0.459 | 2019: +0.286 | 2020: +0.274 | 2021: +0.162 | 2022: +0.108 | 2023: +0.162 | 2024: +0.281 | 2025: +0.156 | 2026: +0.171
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.41
- Early IC=+0.2081, Recent IC=+0.0846, 1st-half IC=+0.1734, 2nd-half IC=+0.0709, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.210, Q2=-0.029, Q3_mid=+0.064, Q4=+0.154, Q5_high_vol=+0.202

**`combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1112, Sharpe=+0.3432)
- Admission: Train IC=+0.2520, Deflated=+0.2506, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.80
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
- Admission: Train IC=+0.1767, Deflated=+0.1756, IR=0.56, Mono=0.71, p=0.0002, MaxCorr=0.62
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.032 | 2017: +0.038 | 2018: +0.068 | 2019: +0.151 | 2020: +0.080 | 2021: +0.101 | 2022: -0.007 | 2023: +0.011 | 2024: +0.054 | 2025: -0.055 | 2026: +0.188
- Yearly Tail ICs:   2015: +0.079 | 2016: +0.006 | 2017: +0.370 | 2018: +0.192 | 2019: +0.353 | 2020: +0.212 | 2021: +0.094 | 2022: -0.095 | 2023: +0.100 | 2024: +0.083 | 2025: -0.086 | 2026: +0.210
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=0.59, Recency ratio=0.61
- Early IC=+0.0528, Recent IC=+0.0323, 1st-half IC=+0.0810, 2nd-half IC=+0.0477, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.051, Q2=-0.012, Q3_mid=+0.059, Q4=+0.058, Q5_high_vol=+0.124

**`combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0817, Sharpe=+0.3027)
- Admission: Train IC=+0.2502, Deflated=+0.2492, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.075 | 2017: +0.193 | 2018: +0.139 | 2019: +0.080 | 2020: +0.127 | 2021: +0.055 | 2022: +0.084 | 2023: +0.069 | 2024: +0.100 | 2025: +0.126 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.359 | 2016: +0.110 | 2017: +0.268 | 2018: +0.242 | 2019: +0.237 | 2020: +0.193 | 2021: +0.210 | 2022: +0.340 | 2023: +0.197 | 2024: +0.238 | 2025: +0.209 | 2026: -0.053
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.51
- Early IC=+0.1663, Recent IC=+0.0841, 1st-half IC=+0.1269, 2nd-half IC=+0.0820, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.018, Q3_mid=+0.087, Q4=+0.095, Q5_high_vol=+0.135

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0920, Sharpe=+0.2951)
- Admission: Train IC=+0.2329, Deflated=+0.2322, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.315 | 2016: +0.087 | 2017: +0.219 | 2018: +0.204 | 2019: +0.175 | 2020: +0.134 | 2021: +0.087 | 2022: +0.047 | 2023: +0.079 | 2024: +0.088 | 2025: +0.119 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.123 | 2017: +0.186 | 2018: +0.457 | 2019: +0.304 | 2020: +0.267 | 2021: +0.041 | 2022: +0.131 | 2023: +0.134 | 2024: +0.262 | 2025: +0.096 | 2026: +0.094
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.40, Recency ratio=0.39
- Early IC=+0.2119, Recent IC=+0.0836, 1st-half IC=+0.1713, 2nd-half IC=+0.0682, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.029, Q3_mid=+0.059, Q4=+0.152, Q5_high_vol=+0.192

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1138, Sharpe=+0.2628)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.42, Mono=0.67, p=0.0002, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.064 | 2017: +0.196 | 2018: +0.105 | 2019: +0.176 | 2020: +0.076 | 2021: +0.087 | 2022: +0.089 | 2023: +0.057 | 2024: +0.164 | 2025: +0.058 | 2026: +0.181
- Yearly Tail ICs:   2015: +0.201 | 2016: -0.078 | 2017: +0.194 | 2018: +0.319 | 2019: +0.255 | 2020: +0.061 | 2021: +0.195 | 2022: +0.202 | 2023: -0.020 | 2024: +0.075 | 2025: -0.152 | 2026: +0.171
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.74
- Early IC=+0.1505, Recent IC=+0.1107, 1st-half IC=+0.1298, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.066, Q3_mid=+0.094, Q4=+0.137, Q5_high_vol=+0.151

**`combo_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0843, Sharpe=+0.1933)
- Admission: Train IC=+0.1848, Deflated=+0.1842, IR=0.65, Mono=0.72, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.038 | 2017: +0.223 | 2018: +0.173 | 2019: +0.122 | 2020: +0.153 | 2021: +0.120 | 2022: +0.077 | 2023: +0.080 | 2024: +0.123 | 2025: +0.119 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.393 | 2016: -0.073 | 2017: +0.217 | 2018: +0.134 | 2019: +0.353 | 2020: +0.082 | 2021: +0.357 | 2022: +0.185 | 2023: +0.099 | 2024: +0.272 | 2025: +0.191 | 2026: +0.066
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.51
- Early IC=+0.1979, Recent IC=+0.1013, 1st-half IC=+0.1547, 2nd-half IC=+0.1038, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.004, Q3_mid=+0.152, Q4=+0.149, Q5_high_vol=+0.148

**`combo_sig_product__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1335, Sharpe=+0.1748)
- Admission: Train IC=+0.1662, Deflated=+0.1640, IR=0.52, Mono=0.68, p=0.0012, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.138 | 2016: -0.089 | 2017: +0.171 | 2018: -0.002 | 2019: +0.109 | 2020: +0.088 | 2021: +0.112 | 2022: +0.042 | 2023: +0.097 | 2024: +0.216 | 2025: +0.100 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.268 | 2016: -0.147 | 2017: +0.310 | 2018: +0.022 | 2019: +0.130 | 2020: +0.100 | 2021: +0.170 | 2022: -0.165 | 2023: +0.181 | 2024: +0.406 | 2025: -0.094 | 2026: +0.226
- IC CV=0.61, Neg years (linear/tail)=1/1 of 8, Half ratio=1.41, Recency ratio=1.86
- Early IC=+0.0841, Recent IC=+0.1561, 1st-half IC=+0.0875, 2nd-half IC=+0.1237, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.036, Q3_mid=+0.079, Q4=+0.118, Q5_high_vol=+0.144

**`combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1371, Sharpe=+0.1462)
- Admission: Train IC=+0.1707, Deflated=+0.1690, IR=0.52, Mono=0.68, p=0.0006, MaxCorr=0.67
- Yearly Linear ICs: 2015: +0.195 | 2016: -0.009 | 2017: +0.128 | 2018: +0.102 | 2019: +0.171 | 2020: +0.058 | 2021: +0.119 | 2022: +0.027 | 2023: +0.046 | 2024: +0.167 | 2025: +0.095 | 2026: +0.206
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.008 | 2017: +0.213 | 2018: +0.153 | 2019: +0.357 | 2020: +0.002 | 2021: +0.382 | 2022: +0.080 | 2023: +0.082 | 2024: +0.123 | 2025: -0.037 | 2026: +0.325
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.93
- Early IC=+0.1152, Recent IC=+0.1066, 1st-half IC=+0.1132, 2nd-half IC=+0.0920, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.017, Q3_mid=+0.084, Q4=+0.123, Q5_high_vol=+0.156

### 159915ETF — `single` True Positives

**`combo_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1307, Sharpe=+1.7816)
- Admission: Train IC=+0.3282, Deflated=+0.3282, IR=1.09, Mono=0.87, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.074 | 2017: -0.006 | 2018: +0.097 | 2019: +0.227 | 2020: +0.043 | 2021: +0.155 | 2022: +0.034 | 2023: +0.154 | 2024: +0.136 | 2025: +0.131 | 2026: +0.130
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.038 | 2017: +0.123 | 2018: +0.286 | 2019: +0.586 | 2020: +0.294 | 2021: +0.346 | 2022: +0.266 | 2023: +0.366 | 2024: +0.304 | 2025: +0.145 | 2026: +0.355
- IC CV=0.69, Neg years (linear/tail)=1/0 of 8, Half ratio=1.41, Recency ratio=3.20
- Early IC=+0.0453, Recent IC=+0.1451, 1st-half IC=+0.0912, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.106, Q3_mid=+0.112, Q4=+0.100, Q5_high_vol=+0.171

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1527, Sharpe=+1.5226)
- Admission: Train IC=+0.2931, Deflated=+0.2931, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.203 | 2016: -0.012 | 2017: -0.014 | 2018: +0.077 | 2019: +0.224 | 2020: +0.104 | 2021: +0.111 | 2022: +0.092 | 2023: +0.164 | 2024: +0.067 | 2025: +0.174 | 2026: +0.116
- Yearly Tail ICs:   2015: +0.210 | 2016: -0.107 | 2017: +0.066 | 2018: +0.349 | 2019: +0.484 | 2020: +0.155 | 2021: +0.309 | 2022: +0.301 | 2023: +0.392 | 2024: +0.284 | 2025: +0.131 | 2026: +0.337
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=3.62
- Early IC=+0.0310, Recent IC=+0.1125, 1st-half IC=+0.0963, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.077, Q3_mid=+0.132, Q4=+0.105, Q5_high_vol=+0.117

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1346, Sharpe=+1.4890)
- Admission: Train IC=+0.3215, Deflated=+0.3208, IR=0.89, Mono=0.79, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.115 | 2017: +0.001 | 2018: +0.162 | 2019: +0.239 | 2020: +0.149 | 2021: +0.149 | 2022: +0.103 | 2023: +0.158 | 2024: +0.106 | 2025: +0.167 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.154 | 2016: +0.030 | 2017: +0.026 | 2018: +0.306 | 2019: +0.526 | 2020: +0.281 | 2021: +0.251 | 2022: +0.185 | 2023: +0.414 | 2024: +0.503 | 2025: +0.286 | 2026: +0.029
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.62
- Early IC=+0.0815, Recent IC=+0.1321, 1st-half IC=+0.1313, 2nd-half IC=+0.1358, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.089, Q3_mid=+0.107, Q4=+0.133, Q5_high_vol=+0.193

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1277, Sharpe=+1.1407)
- Admission: Train IC=+0.3360, Deflated=+0.3352, IR=1.05, Mono=0.83, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.092 | 2017: -0.005 | 2018: +0.166 | 2019: +0.223 | 2020: +0.135 | 2021: +0.148 | 2022: +0.127 | 2023: +0.186 | 2024: +0.081 | 2025: +0.182 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.022 | 2017: +0.048 | 2018: +0.386 | 2019: +0.452 | 2020: +0.337 | 2021: +0.367 | 2022: +0.294 | 2023: +0.467 | 2024: +0.301 | 2025: +0.195 | 2026: +0.190
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.07, Recency ratio=1.68
- Early IC=+0.0789, Recent IC=+0.1327, 1st-half IC=+0.1338, 2nd-half IC=+0.1438, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.138, Q3_mid=+0.123, Q4=+0.139, Q5_high_vol=+0.199

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1325, Sharpe=+1.0456)
- Admission: Train IC=+0.2890, Deflated=+0.2872, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.78
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

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1337, Sharpe=+0.9648)
- Admission: Train IC=+0.2967, Deflated=+0.2960, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.159 | 2017: -0.017 | 2018: +0.158 | 2019: +0.231 | 2020: +0.183 | 2021: +0.135 | 2022: +0.109 | 2023: +0.126 | 2024: +0.091 | 2025: +0.152 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.187 | 2017: +0.025 | 2018: +0.332 | 2019: +0.413 | 2020: +0.323 | 2021: +0.314 | 2022: +0.226 | 2023: +0.236 | 2024: +0.462 | 2025: +0.232 | 2026: +0.168
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.88, Recency ratio=1.53
- Early IC=+0.0708, Recent IC=+0.1083, 1st-half IC=+0.1395, 2nd-half IC=+0.1229, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.104, Q3_mid=+0.080, Q4=+0.131, Q5_high_vol=+0.204

**`combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return`** (Lock IC=+0.1197, Sharpe=+0.9323)
- Admission: Train IC=+0.2378, Deflated=+0.2380, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.138 | 2016: +0.083 | 2017: -0.054 | 2018: +0.112 | 2019: +0.113 | 2020: +0.135 | 2021: +0.037 | 2022: +0.178 | 2023: +0.123 | 2024: +0.050 | 2025: +0.096 | 2026: +0.149
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.237 | 2017: +0.018 | 2018: +0.408 | 2019: +0.228 | 2020: +0.405 | 2021: +0.133 | 2022: +0.395 | 2023: +0.107 | 2024: +0.062 | 2025: +0.176 | 2026: +0.214
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.01, Recency ratio=3.02
- Early IC=+0.0288, Recent IC=+0.0869, 1st-half IC=+0.0887, 2nd-half IC=+0.0894, Neg regimes=0/5
- Weak component: `yesterday_early_momentum` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.151, Q3_mid=+0.052, Q4=+0.115, Q5_high_vol=+0.171

**`combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`** (Lock IC=+0.1191, Sharpe=+0.8724)
- Admission: Train IC=+0.3534, Deflated=+0.3528, IR=1.10, Mono=0.86, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.068 | 2017: +0.013 | 2018: +0.123 | 2019: +0.190 | 2020: +0.088 | 2021: +0.159 | 2022: +0.094 | 2023: +0.174 | 2024: +0.142 | 2025: +0.148 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.163 | 2017: +0.047 | 2018: +0.390 | 2019: +0.540 | 2020: +0.434 | 2021: +0.348 | 2022: +0.246 | 2023: +0.351 | 2024: +0.438 | 2025: +0.142 | 2026: +0.327
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.47, Recency ratio=2.32
- Early IC=+0.0680, Recent IC=+0.1578, 1st-half IC=+0.1014, 2nd-half IC=+0.1488, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.080, Q3_mid=+0.117, Q4=+0.127, Q5_high_vol=+0.173

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1275, Sharpe=+0.8333)
- Admission: Train IC=+0.3801, Deflated=+0.3803, IR=1.24, Mono=0.88, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.084 | 2017: -0.024 | 2018: +0.157 | 2019: +0.245 | 2020: +0.161 | 2021: +0.143 | 2022: +0.085 | 2023: +0.178 | 2024: +0.127 | 2025: +0.159 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.113 | 2017: +0.052 | 2018: +0.432 | 2019: +0.564 | 2020: +0.344 | 2021: +0.411 | 2022: +0.264 | 2023: +0.423 | 2024: +0.408 | 2025: +0.167 | 2026: +0.332
- IC CV=0.55, Neg years (linear/tail)=1/0 of 8, Half ratio=1.05, Recency ratio=2.29
- Early IC=+0.0665, Recent IC=+0.1525, 1st-half IC=+0.1341, 2nd-half IC=+0.1411, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.110, Q3_mid=+0.113, Q4=+0.143, Q5_high_vol=+0.196

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1135, Sharpe=+0.7682)
- Admission: Train IC=+0.2885, Deflated=+0.2871, IR=0.94, Mono=0.80, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.074 | 2017: +0.031 | 2018: +0.130 | 2019: +0.196 | 2020: +0.124 | 2021: +0.157 | 2022: +0.130 | 2023: +0.164 | 2024: +0.116 | 2025: +0.178 | 2026: +0.031
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.132 | 2017: +0.091 | 2018: +0.225 | 2019: +0.533 | 2020: +0.127 | 2021: +0.272 | 2022: +0.322 | 2023: +0.436 | 2024: +0.349 | 2025: +0.154 | 2026: +0.022
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.74
- Early IC=+0.0805, Recent IC=+0.1398, 1st-half IC=+0.1165, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.099, Q3_mid=+0.114, Q4=+0.130, Q5_high_vol=+0.185

**`combo_ratio__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1308, Sharpe=+0.7043)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.46, Mono=0.68, p=0.0004, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.009 | 2017: -0.012 | 2018: +0.072 | 2019: +0.170 | 2020: +0.085 | 2021: +0.112 | 2022: +0.141 | 2023: +0.103 | 2024: +0.117 | 2025: +0.125 | 2026: +0.147
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.030 | 2017: +0.155 | 2018: +0.235 | 2019: +0.268 | 2020: +0.153 | 2021: +0.188 | 2022: +0.076 | 2023: +0.066 | 2024: +0.234 | 2025: +0.025 | 2026: +0.202
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.38, Recency ratio=3.68
- Early IC=+0.0299, Recent IC=+0.1100, 1st-half IC=+0.0914, 2nd-half IC=+0.1259, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.131, Q3_mid=+0.066, Q4=+0.120, Q5_high_vol=+0.153

**`combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1511, Sharpe=+0.6805)
- Admission: Train IC=+0.2750, Deflated=+0.2737, IR=0.90, Mono=0.81, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.041 | 2017: -0.003 | 2018: +0.045 | 2019: +0.156 | 2020: +0.089 | 2021: +0.150 | 2022: +0.115 | 2023: +0.164 | 2024: +0.081 | 2025: +0.195 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.058 | 2016: +0.210 | 2017: +0.146 | 2018: +0.212 | 2019: +0.261 | 2020: +0.209 | 2021: +0.246 | 2022: +0.275 | 2023: +0.359 | 2024: +0.326 | 2025: +0.192 | 2026: +0.109
- IC CV=0.55, Neg years (linear/tail)=1/0 of 8, Half ratio=1.85, Recency ratio=5.93
- Early IC=+0.0206, Recent IC=+0.1220, 1st-half IC=+0.0724, 2nd-half IC=+0.1343, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.106, Q3_mid=+0.081, Q4=+0.092, Q5_high_vol=+0.137

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1100, Sharpe=+0.5568)
- Admission: Train IC=+0.2297, Deflated=+0.2299, IR=0.78, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.112 | 2017: -0.039 | 2018: +0.156 | 2019: +0.124 | 2020: +0.144 | 2021: +0.056 | 2022: +0.185 | 2023: +0.124 | 2024: +0.055 | 2025: +0.080 | 2026: +0.143
- Yearly Tail ICs:   2015: +0.074 | 2016: +0.385 | 2017: +0.158 | 2018: +0.385 | 2019: +0.386 | 2020: +0.301 | 2021: +0.156 | 2022: +0.438 | 2023: +0.126 | 2024: +0.007 | 2025: +0.073 | 2026: +0.091
- IC CV=0.67, Neg years (linear/tail)=1/0 of 8, Half ratio=0.87, Recency ratio=1.54
- Early IC=+0.0581, Recent IC=+0.0895, 1st-half IC=+0.1131, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.29)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.161, Q3_mid=+0.052, Q4=+0.134, Q5_high_vol=+0.190

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1286, Sharpe=+0.5529)
- Admission: Train IC=+0.2467, Deflated=+0.2465, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.43
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.047 | 2017: -0.047 | 2018: +0.084 | 2019: +0.131 | 2020: +0.102 | 2021: +0.033 | 2022: +0.180 | 2023: +0.115 | 2024: +0.083 | 2025: +0.129 | 2026: +0.127
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.222 | 2017: +0.080 | 2018: +0.355 | 2019: +0.275 | 2020: +0.402 | 2021: +0.130 | 2022: +0.486 | 2023: +0.119 | 2024: +0.057 | 2025: +0.101 | 2026: +0.271
- IC CV=0.75, Neg years (linear/tail)=1/0 of 8, Half ratio=1.22, Recency ratio=5.34
- Early IC=+0.0186, Recent IC=+0.0992, 1st-half IC=+0.0787, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.138, Q3_mid=+0.034, Q4=+0.104, Q5_high_vol=+0.175

**`combo_rank_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1250, Sharpe=+0.4385)
- Admission: Train IC=+0.2051, Deflated=+0.2051, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.162 | 2016: -0.004 | 2017: -0.050 | 2018: +0.063 | 2019: +0.110 | 2020: +0.080 | 2021: +0.018 | 2022: +0.163 | 2023: +0.109 | 2024: +0.072 | 2025: +0.124 | 2026: +0.118
- Yearly Tail ICs:   2015: +0.176 | 2016: +0.025 | 2017: -0.099 | 2018: +0.344 | 2019: +0.188 | 2020: +0.339 | 2021: +0.105 | 2022: +0.514 | 2023: +0.128 | 2024: +0.070 | 2025: +0.084 | 2026: +0.231
- IC CV=0.84, Neg years (linear/tail)=1/1 of 8, Half ratio=1.44, Recency ratio=15.06
- Early IC=+0.0060, Recent IC=+0.0902, 1st-half IC=+0.0566, 2nd-half IC=+0.0817, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.122, Q3_mid=+0.036, Q4=+0.091, Q5_high_vol=+0.136

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1124, Sharpe=+0.3952)
- Admission: Train IC=+0.1987, Deflated=+0.1960, IR=0.52, Mono=0.69, p=0.0000, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.100 | 2017: -0.031 | 2018: +0.096 | 2019: +0.091 | 2020: +0.077 | 2021: +0.066 | 2022: +0.131 | 2023: +0.154 | 2024: +0.122 | 2025: +0.085 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.264 | 2017: +0.061 | 2018: +0.442 | 2019: +0.295 | 2020: +0.014 | 2021: +0.130 | 2022: +0.254 | 2023: +0.202 | 2024: +0.169 | 2025: -0.014 | 2026: +0.123
- IC CV=0.61, Neg years (linear/tail)=1/0 of 8, Half ratio=1.60, Recency ratio=4.45
- Early IC=+0.0309, Recent IC=+0.1378, 1st-half IC=+0.0747, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.111, Q3_mid=+0.063, Q4=+0.145, Q5_high_vol=+0.090

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1299, Sharpe=+0.3365)
- Admission: Train IC=+0.2847, Deflated=+0.2843, IR=0.84, Mono=0.81, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.096 | 2017: -0.001 | 2018: +0.155 | 2019: +0.246 | 2020: +0.145 | 2021: +0.127 | 2022: +0.095 | 2023: +0.139 | 2024: +0.074 | 2025: +0.160 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.152 | 2016: +0.057 | 2017: +0.091 | 2018: +0.305 | 2019: +0.509 | 2020: +0.193 | 2021: +0.254 | 2022: +0.256 | 2023: +0.208 | 2024: +0.403 | 2025: +0.134 | 2026: +0.237
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.84, Recency ratio=1.39
- Early IC=+0.0767, Recent IC=+0.1063, 1st-half IC=+0.1412, 2nd-half IC=+0.1181, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.117, Q3_mid=+0.071, Q4=+0.114, Q5_high_vol=+0.218

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1296, Sharpe=+0.3365)
- Admission: Train IC=+0.2847, Deflated=+0.2842, IR=0.84, Mono=0.81, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.096 | 2017: -0.001 | 2018: +0.155 | 2019: +0.246 | 2020: +0.145 | 2021: +0.127 | 2022: +0.095 | 2023: +0.139 | 2024: +0.074 | 2025: +0.159 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.152 | 2016: +0.057 | 2017: +0.092 | 2018: +0.305 | 2019: +0.509 | 2020: +0.194 | 2021: +0.254 | 2022: +0.253 | 2023: +0.208 | 2024: +0.405 | 2025: +0.130 | 2026: +0.237
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.83, Recency ratio=1.38
- Early IC=+0.0771, Recent IC=+0.1062, 1st-half IC=+0.1414, 2nd-half IC=+0.1180, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.117, Q3_mid=+0.071, Q4=+0.114, Q5_high_vol=+0.217

**`combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1073, Sharpe=+0.1834)
- Admission: Train IC=+0.1853, Deflated=+0.1840, IR=0.52, Mono=0.68, p=0.0004, MaxCorr=0.60
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

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0930, Sharpe=+0.0368)
- Admission: Train IC=+0.2553, Deflated=+0.2560, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.097 | 2017: +0.024 | 2018: +0.126 | 2019: +0.194 | 2020: +0.112 | 2021: +0.133 | 2022: +0.103 | 2023: +0.174 | 2024: +0.071 | 2025: +0.164 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.342 | 2016: -0.030 | 2017: +0.140 | 2018: +0.196 | 2019: +0.482 | 2020: +0.137 | 2021: +0.288 | 2022: +0.129 | 2023: +0.502 | 2024: +0.185 | 2025: +0.246 | 2026: +0.149
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.61
- Early IC=+0.0758, Recent IC=+0.1222, 1st-half IC=+0.1106, 2nd-half IC=+0.1254, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.110, Q3_mid=+0.099, Q4=+0.101, Q5_high_vol=+0.140

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_max__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0` | Median | fast | +0.1163 | -0.1270 | -0.1270 | 1y |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Median | fast | +0.1087 | -0.0759 | -0.0759 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction` | TP | fast | +0.1033 | -0.0655 | -0.0655 | 1y |
| `combo_max__max_up_ret__volume_weighted_price_position` | FP | fast | +0.0964 | -0.2004 | -0.2004 | 1y |
| `combo_abs_diff__max_up_ret__first_bar_sentiment` | Median | fast | +0.0963 | -0.1324 | -0.1324 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | fast | +0.0958 | -0.0206 | -0.0206 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.0945 | +0.0032 | +0.0032 | 1y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | fast | +0.0925 | -0.1974 | -0.1974 | 1y |
| `first_30min_return` | FP | fast | +0.0908 | -0.1874 | -0.1874 | 1y |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Median | fast | +0.0845 | -0.0552 | -0.0552 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Median | fast | +0.0775 | -0.0811 | -0.0811 | 1y |
| `combo_max__first_bar_return__volume_surge_direction` | Median | fast | +0.0750 | -0.0872 | -0.0872 | 1y |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0743 | +0.0631 | +0.0631 | ∞ |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | FP | fast | +0.0699 | -0.0987 | -0.0987 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | fast | +0.0657 | -0.0650 | -0.0650 | 1y |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0569 | -0.1658 | -0.1658 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | fast | +0.0467 | -0.0313 | -0.0313 | 1y |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | TP | persistent | +0.0442 | +0.0707 | +0.0707 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | fast | +0.0436 | -0.0364 | -0.0364 | 1y |
| `combo_ratio__first_bar_return__volume_surge_direction` | FP | fast | +0.0417 | -0.0939 | -0.0939 | 1y |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | FP | fast | +0.0256 | -0.1056 | -0.1056 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | FP | fast | +0.0216 | -0.0774 | -0.0774 | 1y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__first_bar_sentiment` | Median | persistent | +0.0072 | +0.0676 | +0.0676 | ∞ |
| `combo_min__bar_body_rng_0__demark_setup_reversal_early` | FP | immediate | -0.0476 | -0.0656 | -0.0656 | ∞ |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | FP | immediate | -0.1771 | +0.0597 | +0.0597 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=19, gradual=0, persistent=4

**FP decay trajectories:**

- `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment`: Y1:-0.177 → Y2:+0.060
- `combo_min__bar_body_rng_0__demark_setup_reversal_early`: Y1:-0.048 → Y2:-0.066
- `combo_min__max_up_ret__bar_body_rng_0`: Y1:+0.022 → Y2:-0.077
- `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`: Y1:+0.026 → Y2:-0.106
- `combo_ratio__first_bar_return__volume_surge_direction`: Y1:+0.042 → Y2:-0.094
- `combo_mean__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.057 → Y2:-0.166
- `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Y1:+0.070 → Y2:-0.099
- `first_30min_return`: Y1:+0.091 → Y2:-0.187
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:+0.092 → Y2:-0.197
- `combo_max__max_up_ret__volume_weighted_price_position`: Y1:+0.096 → Y2:-0.200

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1483 | +0.0404 | +0.0404 | 1y |
| `combo_tri_min__first_bar_sentiment__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | fast | +0.1372 | -0.0641 | -0.0641 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | fast | +0.1327 | -0.0711 | -0.0711 | 1y |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1298 | +0.0857 | +0.0857 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | persistent | +0.1264 | +0.0207 | +0.0207 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1260 | +0.0780 | +0.0780 | ∞ |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1259 | +0.1051 | +0.1051 | ∞ |
| `combo_min__early_body_momentum__max_down_ret` | Median | persistent | +0.1255 | +0.0098 | +0.0098 | 1y |
| `combo_mean__close_vs_open_range__bar_ret_0` | Median | fast | +0.1198 | -0.0391 | -0.0391 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1196 | +0.0802 | +0.0802 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1192 | +0.0805 | +0.0805 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | fast | +0.1192 | -0.0517 | -0.0517 | 1y |
| `combo_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1187 | +0.0462 | +0.0462 | 1y |
| `combo_sig_product__net_volume_flow__first_bar_return` | Median | fast | +0.1085 | -0.1006 | -0.1006 | 1y |
| `combo_sig_product__net_volume_flow__bar_ret_0` | Median | fast | +0.1079 | -0.0996 | -0.0996 | 1y |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0999 | +0.1857 | +0.1857 | ∞ |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Median | persistent | +0.0953 | +0.0159 | +0.0159 | 1y |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Median | persistent | +0.0949 | +0.0039 | +0.0039 | 1y |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0949 | +0.2061 | +0.2061 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Median | persistent | +0.0944 | +0.0858 | +0.0858 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0917 | +0.0324 | +0.0324 | 1y |
| `combo_max__max_up_ret__first_bar_sentiment` | Median | fast | +0.0739 | -0.0361 | -0.0361 | 1y |
| `combo_sig_product__max_up_ret__first_bar_return` | Median | fast | +0.0734 | -0.0792 | -0.0792 | 1y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0685 | +0.0222 | +0.0222 | 1y |
| `combo_tri_max__first_bar_sentiment__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0623 | +0.0894 | +0.0894 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | fast | +0.0601 | -0.0041 | -0.0041 | 1y |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0578 | +0.1809 | +0.1809 | ∞ |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0129 | +0.0895 | +0.0895 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | immediate | -0.0548 | +0.1878 | +0.1878 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=9, gradual=0, persistent=19

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_max__bar_body_rng_0__volatility_expansion_trend_vector` | Median | fast | +0.2059 | -0.0835 | -0.0835 | 1y |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1959 | +0.0869 | +0.0869 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1826 | +0.0526 | +0.0526 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1776 | +0.0306 | +0.0306 | 1y |
| `combo_max__max_up_ret__volume_weighted_price_position` | Median | fast | +0.1770 | -0.0804 | -0.0804 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1750 | +0.1164 | +0.1164 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1704 | +0.0712 | +0.0712 | 1y |
| `combo_max__max_up_ret__first_bar_return` | Median | fast | +0.1689 | -0.0747 | -0.0747 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1675 | +0.0833 | +0.0833 | 1y |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Median | fast | +0.1672 | -0.0446 | -0.0446 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.1637 | +0.0055 | +0.0055 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1599 | +0.0855 | +0.0855 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1594 | +0.0841 | +0.0841 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1590 | +0.0858 | +0.0858 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1518 | +0.1112 | +0.1112 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0` | TP | persistent | +0.1479 | +0.0806 | +0.0806 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1433 | +0.1123 | +0.1123 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Median | persistent | +0.1348 | +0.1140 | +0.1140 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1313 | +0.1302 | +0.1302 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1291 | +0.1272 | +0.1272 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1247 | +0.1472 | +0.1472 | ∞ |
| `combo_rank_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1239 | +0.1135 | +0.1135 | ∞ |
| `combo_rank_min__impulse_bar_dominance__rbreaker_buy_setup_proximity_early` | Median | fast | +0.1205 | -0.0094 | -0.0094 | 1y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1014 | +0.1299 | +0.1299 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1012 | +0.1304 | +0.1304 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | TP | persistent | +0.0964 | +0.1495 | +0.1495 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0804 | +0.1430 | +0.1430 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0791 | +0.1555 | +0.1555 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Median | persistent | +0.0655 | +0.1661 | +0.1661 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0273 | +0.0202 | +0.0202 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=5, gradual=0, persistent=24

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.027 → Y2:+0.020

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.738±0.061 | 0.694±0.027 | 31% | USEFUL |
| ic_ir | 0.658±0.196 | 0.486±0.051 | 18% | USEFUL |
| p_value | 0.004±0.006 | 0.002±0.002 | 21% | USEFUL |
| max_corr | 0.654±0.253 | 0.516±0.268 | 61% | WEAK |
| deflated_ic | 0.189±0.052 | 0.168±0.022 | 30% | USEFUL |
| overall_ic | 0.189±0.052 | 0.168±0.023 | 31% | USEFUL |
| raw_ic | 0.070±0.019 | 0.069±0.015 | 53% | WEAK |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 8/20 top rejects are profitable (40%)

- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0963, Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0963, Sharpe=+0.8491
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2310, Lock IC=+0.0219, Sharpe=+0.0687

**BH-FDR Gate**: 1/4 top rejects are profitable (25%)

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Sharpe=+0.1297

**B4 Correlation Gate**: 3/20 top rejects are profitable (15%)

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2534, Lock IC=+0.0736, Sharpe=+0.3417
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2625, Lock IC=+0.0436, Sharpe=+0.0327
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2622, Lock IC=+0.0437, Sharpe=+0.0327

### 500ETF — `single`

**7-Year Jackknife**: 12/20 top rejects are profitable (60%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2197, Lock IC=+0.0922, Sharpe=+0.4695
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340

**B2 Rolling Guard**: 2/20 top rejects are profitable (10%)

- `combo_clamp_diff__first_bar_sentiment__early_late_momentum_divergence`: Train IC=+0.1855, Lock IC=+0.0659, Sharpe=+0.3681
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2239, Lock IC=+0.0978, Sharpe=+0.0194

**Temporal Validation Gate**: 1/20 top rejects are profitable (5%)

- `combo_clamp_diff__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.2743, Lock IC=+0.0624, Sharpe=+0.6830

**B3 Composite Floor**: 2/20 top rejects are profitable (10%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1847, Lock IC=+0.0017, Sharpe=+0.3201
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__trend_bar_close_consistency`: Train IC=+0.1698, Lock IC=+0.0611, Sharpe=+0.1260

**B6 Yearly IC CV Gate**: 6/6 top rejects are profitable (100%)

- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1680, Lock IC=+0.0263, Sharpe=+0.6290
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352

**B6 Temporal Stability Gate**: 4/20 top rejects are profitable (20%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2741, Lock IC=+0.0880, Sharpe=+0.3545
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2699, Lock IC=+0.0867, Sharpe=+0.2984
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__first_bar_sentiment`: Train IC=+0.2687, Lock IC=+0.1075, Sharpe=+0.0417

**B4 Correlation Gate**: 1/20 top rejects are profitable (5%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__volatility_expansion_trend_vector`: Train IC=+0.2568, Lock IC=+0.0991, Sharpe=+0.2078

**Adaptive Correlation Gate**: 5/20 top rejects are profitable (25%)

- `combo_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2043, Lock IC=+0.1117, Sharpe=+1.3824
- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1888, Lock IC=+0.1502, Sharpe=+1.1714
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2469, Lock IC=+0.1136, Sharpe=+0.6574

### 159915ETF — `single`

**7-Year Jackknife**: 14/20 top rejects are profitable (70%)

- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2018, Lock IC=+0.1126, Sharpe=+1.5724
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.9095
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.9095

**B2 Rolling Guard**: 14/20 top rejects are profitable (70%)

- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_rank_max__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1830, Lock IC=+0.0792, Sharpe=+0.8691

**Temporal Validation Gate**: 16/20 top rejects are profitable (80%)

- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1734, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1734, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1987, Lock IC=+0.1447, Sharpe=+1.1411

**BH-FDR Gate**: 1/3 top rejects are profitable (33%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0396, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__impulse_bar_dominance`: Train IC=+0.2725, Lock IC=+0.1182, Sharpe=+1.4944
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.2628, Lock IC=+0.1068, Sharpe=+1.3589
- `combo_tri_min__max_up_ret__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2417, Lock IC=+0.1107, Sharpe=+1.2956

**B6 Temporal Stability Gate**: 1/1 top rejects are profitable (100%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2356, Lock IC=+0.1259, Sharpe=+0.1557

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.5184
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.5184
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890

**Adaptive Correlation Gate**: 10/17 top rejects are profitable (59%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2468, Lock IC=+0.1592, Sharpe=+1.2335
- `combo_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1602, Lock IC=+0.0659, Sharpe=+0.7397
- `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.2329, Lock IC=+0.0968, Sharpe=+0.5705

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1114 | 78 | 27 | 31 | 20 | 35% | 26% |
| B2 Rolling Guard | 121 | 78 | 34 | 35 | 9 | 44% | 12% |
| Temporal Validation Gate | 122 | 78 | 24 | 43 | 11 | 31% | 14% |
| BH-FDR Gate | 4 | 4 | 1 | 2 | 1 | 25% | 25% |
| B3 Composite Floor | 3 | 3 | 0 | 3 | 0 | 0% | 0% |
| B6 Yearly IC CV Gate | 13 | 13 | 12 | 1 | 0 | 92% | 0% |
| B6 Quality Gate | 3 | 3 | 2 | 1 | 0 | 67% | 0% |
| B4 Correlation Gate | 339 | 78 | 41 | 28 | 9 | 53% | 12% |
| Adaptive Correlation Gate | 10 | 10 | 7 | 3 | 0 | 70% | 0% |

**7-Year Jackknife** — top TP casualties:
- `combo_diff__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0002, Lock IC=+0.0825, Sharpe=+0.8131
- `combo_z_diff__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0002, Lock IC=+0.0825, Sharpe=+0.8131
- `combo_abs_diff__volume_weighted_momentum_acceleration__volume_weighted_price_position`: Train IC=+0.0008, Lock IC=+0.0964, Sharpe=+0.7411

**BH-FDR Gate** — top TP casualties:
- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Sharpe=+0.1297

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1802 | 78 | 33 | 25 | 20 | 42% | 26% |
| B2 Rolling Guard | 217 | 78 | 30 | 37 | 11 | 38% | 14% |
| Temporal Validation Gate | 211 | 78 | 20 | 38 | 20 | 26% | 26% |
| BH-FDR Gate | 5 | 5 | 2 | 3 | 0 | 40% | 0% |
| B3 Composite Floor | 56 | 56 | 5 | 29 | 22 | 9% | 39% |
| B6 Yearly IC CV Gate | 6 | 6 | 0 | 0 | 6 | 0% | 100% |
| B6 Temporal Stability Gate | 360 | 78 | 0 | 65 | 13 | 0% | 17% |
| B6 Quality Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B4 Correlation Gate | 521 | 78 | 1 | 63 | 14 | 1% | 18% |
| Adaptive Correlation Gate | 21 | 21 | 1 | 15 | 5 | 5% | 24% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=-0.0027, Lock IC=+0.0733, Sharpe=+0.7176
- `combo_min__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=-0.0090, Lock IC=+0.0732, Sharpe=+0.7176
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2197, Lock IC=+0.0922, Sharpe=+0.4695

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

**Adaptive Correlation Gate** — top TP casualties:
- `combo_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2043, Lock IC=+0.1117, Sharpe=+1.3824
- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1888, Lock IC=+0.1502, Sharpe=+1.1714
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2469, Lock IC=+0.1136, Sharpe=+0.6574

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 970 | 78 | 19 | 24 | 35 | 24% | 45% |
| B2 Rolling Guard | 145 | 78 | 20 | 26 | 32 | 26% | 41% |
| Temporal Validation Gate | 36 | 36 | 5 | 6 | 25 | 14% | 69% |
| BH-FDR Gate | 3 | 3 | 0 | 2 | 1 | 0% | 33% |
| B3 Composite Floor | 121 | 78 | 1 | 23 | 54 | 1% | 69% |
| B6 Yearly IC CV Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B6 Temporal Stability Gate | 1 | 1 | 0 | 0 | 1 | 0% | 100% |
| B4 Correlation Gate | 379 | 78 | 0 | 12 | 66 | 0% | 85% |
| Adaptive Correlation Gate | 17 | 17 | 0 | 7 | 10 | 0% | 59% |

**7-Year Jackknife** — top TP casualties:
- `yesterday_illiquidity_amihud`: Train IC=+0.0550, Lock IC=+0.1294, Sharpe=+1.6004
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2018, Lock IC=+0.1126, Sharpe=+1.5724
- `combo_product__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.0564, Lock IC=+0.1137, Sharpe=+0.9127

**B2 Rolling Guard** — top TP casualties:
- `yesterday_day_vwap_dev`: Train IC=+0.1185, Lock IC=+0.1197, Sharpe=+1.1213
- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1734, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1734, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1987, Lock IC=+0.1447, Sharpe=+1.1411

**BH-FDR Gate** — top TP casualties:
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0396, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__impulse_bar_dominance`: Train IC=+0.2725, Lock IC=+0.1182, Sharpe=+1.4944
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.2628, Lock IC=+0.1068, Sharpe=+1.3589
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2227, Lock IC=+0.1193, Sharpe=+1.3049

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2356, Lock IC=+0.1259, Sharpe=+0.1557

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3122, Lock IC=+0.1361, Sharpe=+1.6091
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.5184
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.5184

**Adaptive Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2468, Lock IC=+0.1592, Sharpe=+1.2335
- `combo_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1602, Lock IC=+0.0659, Sharpe=+0.7397
- `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.2329, Lock IC=+0.0968, Sharpe=+0.5705

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (122 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 114 | 50 | 15 | 0 | 35 | 30% | 0% |
| recency_ratio >= 2.5 (late-concentrated) | 8 | 8 | 4 | 0 | 4 | 50% | 0% |

### 500ETF — `single` (211 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 207 | 50 | 0 | 8 | 42 | 0% | 16% |
| recency_ratio >= 2.5 (late-concentrated) | 4 | 4 | 2 | 0 | 2 | 50% | 0% |

### 159915ETF — `single` (36 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 29 | 29 | 5 | 21 | 3 | 17% | 72% |
| recency_ratio >= 2.5 (late-concentrated) | 7 | 7 | 0 | 4 | 3 | 0% | 57% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.0957, Lock IC=+0.0822, Sharpe=+0.7710
- `vwap_slope_intraday`: Train IC=+0.0934, Lock IC=+0.0337, Sharpe=+0.2590
- `combo_min__rbreaker_buy_setup_proximity_early__late_bar_momentum`: Train IC=+0.1182, Lock IC=+0.0724, Sharpe=+0.0058
- `combo_min__limit_down_proximity_early__late_bar_momentum`: Train IC=+0.1181, Lock IC=+0.0724, Sharpe=+0.0058

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `weak_link_cv`: FP is lower (d=-1.02). Threshold 0.935 → 73% accuracy.
- `half_ratio`: FP is higher (d=+0.56). Threshold 0.594 → 75% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/10
- Decaying signal (half ratio < 0.3): 0/10
- Weak component (CV > 2.0): 0/10
- Regime-dependent (≥2 negative regimes): 0/10

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | 7 | 3 | 10 | 70% |  |
| `volume_weighted_price_position` | 4 | 3 | 7 | 57% |  |
| `volume_surge_direction` | 1 | 1 | 2 | 50% |  |
| `first_bar_sentiment` | 1 | 1 | 2 | 50% |  |
| `bar_body_rng_0` | 3 | 4 | 7 | 43% |  |
| `volatility_expansion_trend_vector` | 1 | 3 | 4 | 25% |  |
| `volume_weighted_momentum_acceleration` | 1 | 3 | 4 | 25% |  |
| `first_bar_return` | 1 | 4 | 5 | 20% |  |
| `opening_drive_thrust_ratio` | 1 | 9 | 10 | 10% |  |
| `yesterday_first_30min_return` | 0 | 5 | 5 | 0% |  |
| `bar_ret_0` | 0 | 6 | 6 | 0% |  |
| `max_down_ret` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 12 | 12 | 0% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 3 | 3 | 0% |  |
| `star50_limit_proximity_early` | 0 | 16 | 16 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=6, TP=19, FP rate=24%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=4, FP rate=33%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=8, FP rate=11%

