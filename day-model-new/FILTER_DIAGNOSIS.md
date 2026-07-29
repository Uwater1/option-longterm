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

| ETF | Side | Admitted | FP | Median | TP | FP Rate | Prod Score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | 4 | 3 | 5 | 33% | 0.47 |
| 500ETF | single | 20 | 0 | 4 | 16 | 0% | 0.71 |
| 159915ETF | single | 8 | 0 | 1 | 7 | 0% | 0.92 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=4, TP=5)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_std_across_regimes | 0.057 | 0.085 | 0.057 | 0.082 | -2.43 | 0.096 | 44% |
| recency_ratio | 1.417 | 0.821 | 1.664 | 0.739 | +1.36 | 1.455 | 89% |
| half_ratio | 1.540 | 1.115 | 1.548 | 1.025 | +0.95 | 1.386 | 78% |
| n_negative_years | 1.000 | 0.600 | 1.000 | 1.000 | +0.66 | 1.500 | 67% |
| weak_link_cv | 1.105 | 1.223 | 1.157 | 1.141 | -0.53 | 1.219 | 62% |
| ic_cv | 0.877 | 0.826 | 0.887 | 0.817 | +0.34 | 0.697 | 67% |
| n_negative_regimes | 1.000 | 1.000 | 1.000 | 1.000 | +0.00 | 1.500 | 56% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_ratio__first_bar_sentiment__volume_surge_direction`** (Lock IC=-0.0280, Sharpe=-1.2340)
- Admission: Train IC=+0.1277, Deflated=+0.1278, IR=0.63, Mono=0.75, p=0.0154, MaxCorr=0.07
- Yearly Linear ICs: 2015: +0.083 | 2016: +0.112 | 2017: +0.044 | 2018: +0.089 | 2019: +0.064 | 2020: -0.038 | 2021: +0.135 | 2022: +0.019 | 2023: +0.058 | 2024: -0.051 | 2025: +0.006 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.250 | 2017: -0.084 | 2018: +0.104 | 2019: +0.145 | 2020: +0.030 | 2021: +0.411 | 2022: +0.051 | 2023: -0.030 | 2024: +0.059 | 2025: -0.149 | 2026: -0.034
- IC CV=0.75, Neg years (linear/tail)=1/1 of 7, Half ratio=0.87, Recency ratio=0.50
- Early IC=+0.0977, Recent IC=+0.0485, 1st-half IC=+0.0764, 2nd-half IC=+0.0665, Neg regimes=1/5
- Weak component: `volume_surge_direction` (CV=1.02, neg years=1)
- Regime ICs: Q1_low_vol=+0.088, Q2=-0.007, Q3_mid=+0.119, Q4=+0.059, Q5_high_vol=+0.111

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0337, Sharpe=-1.1178)
- Admission: Train IC=+0.1466, Deflated=+0.1457, IR=0.59, Mono=0.73, p=0.0058, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.076 | 2016: +0.034 | 2017: -0.050 | 2018: +0.114 | 2019: +0.086 | 2020: +0.032 | 2021: +0.170 | 2022: +0.016 | 2023: +0.173 | 2024: +0.026 | 2025: +0.012 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.136 | 2017: -0.036 | 2018: +0.199 | 2019: +0.293 | 2020: +0.101 | 2021: +0.421 | 2022: +0.234 | 2023: +0.203 | 2024: +0.120 | 2025: -0.101 | 2026: +0.030
- IC CV=0.98, Neg years (linear/tail)=1/1 of 7, Half ratio=2.19, Recency ratio=1.84
- Early IC=+0.0546, Recent IC=+0.1006, 1st-half IC=+0.0450, 2nd-half IC=+0.0985, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.30, neg years=1)
- Regime ICs: Q1_low_vol=-0.043, Q2=+0.089, Q3_mid=+0.140, Q4=+0.030, Q5_high_vol=+0.132

**`combo_product__smooth_momentum_structure__opening_drive_thrust_ratio`** (Lock IC=-0.0238, Sharpe=-0.5100)
- Admission: Train IC=+0.2002, Deflated=+0.2033, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.12
- Yearly Linear ICs: 2015: +0.076 | 2016: -0.018 | 2017: +0.100 | 2018: -0.017 | 2019: +0.089 | 2020: +0.024 | 2021: +0.072 | 2022: -0.102 | 2023: -0.076 | 2024: +0.005 | 2025: +0.035 | 2026: -0.178
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.167 | 2017: +0.199 | 2018: +0.087 | 2019: +0.215 | 2020: +0.273 | 2021: +0.246 | 2022: -0.201 | 2023: -0.100 | 2024: +0.306 | 2025: -0.195 | 2026: -0.605
- IC CV=0.99, Neg years (linear/tail)=2/0 of 7, Half ratio=1.47, Recency ratio=1.66
- Early IC=+0.0290, Recent IC=+0.0481, 1st-half IC=+0.0357, 2nd-half IC=+0.0526, Neg regimes=2/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.81, neg years=1)
- Regime ICs: Q1_low_vol=+0.122, Q2=-0.051, Q3_mid=+0.108, Q4=-0.033, Q5_high_vol=+0.037

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0103, Sharpe=-0.3294)
- Admission: Train IC=+0.2240, Deflated=+0.2229, IR=0.80, Mono=0.79, p=0.0000, MaxCorr=0.66
- Yearly Linear ICs: 2015: +0.093 | 2016: +0.030 | 2017: +0.039 | 2018: +0.150 | 2019: +0.044 | 2020: +0.011 | 2021: +0.194 | 2022: +0.045 | 2023: +0.196 | 2024: +0.038 | 2025: +0.106 | 2026: -0.206
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.101 | 2017: +0.156 | 2018: +0.425 | 2019: +0.208 | 2020: +0.213 | 2021: +0.325 | 2022: +0.238 | 2023: +0.225 | 2024: +0.102 | 2025: +0.226 | 2026: -0.338
- IC CV=0.79, Neg years (linear/tail)=0/0 of 7, Half ratio=1.62, Recency ratio=1.67
- Early IC=+0.0614, Recent IC=+0.1023, 1st-half IC=+0.0643, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30, neg years=1)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.047, Q3_mid=+0.077, Q4=+0.098, Q5_high_vol=+0.153

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0334, Sharpe=-0.0663)
- Admission: Train IC=+0.2662, Deflated=+0.2660, IR=0.85, Mono=0.81, p=0.0000, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.86, Neg years (linear/tail)=1/0 of 7, Half ratio=1.11, Recency ratio=0.79
- Early IC=+0.1475, Recent IC=+0.1159, 1st-half IC=+0.1209, 2nd-half IC=+0.1345, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.049, Q2=+0.010, Q3_mid=+0.110, Q4=+0.248, Q5_high_vol=+0.207

**`combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0225, Sharpe=-0.1138)
- Admission: Train IC=+0.2754, Deflated=+0.2751, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.111 | 2017: +0.068 | 2018: +0.201 | 2019: +0.089 | 2020: +0.013 | 2021: +0.146 | 2022: +0.036 | 2023: +0.151 | 2024: +0.070 | 2025: +0.057 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.204 | 2016: +0.093 | 2017: +0.137 | 2018: +0.277 | 2019: +0.195 | 2020: +0.121 | 2021: +0.338 | 2022: +0.255 | 2023: +0.431 | 2024: +0.209 | 2025: -0.001 | 2026: -0.176
- IC CV=0.53, Neg years (linear/tail)=0/0 of 7, Half ratio=1.13, Recency ratio=0.77
- Early IC=+0.1026, Recent IC=+0.0794, 1st-half IC=+0.1004, 2nd-half IC=+0.1131, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.058, Q3_mid=+0.120, Q4=+0.128, Q5_high_vol=+0.162

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.0094, Sharpe=-1.2715)
- Admission: Train IC=+0.2054, Deflated=+0.2038, IR=0.77, Mono=0.80, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.069 | 2017: -0.078 | 2018: +0.184 | 2019: +0.072 | 2020: +0.017 | 2021: +0.151 | 2022: +0.062 | 2023: +0.138 | 2024: -0.004 | 2025: +0.075 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.250 | 2017: -0.088 | 2018: +0.353 | 2019: +0.275 | 2020: +0.165 | 2021: +0.414 | 2022: +0.198 | 2023: +0.264 | 2024: +0.041 | 2025: +0.123 | 2026: -0.083
- IC CV=1.04, Neg years (linear/tail)=1/1 of 7, Half ratio=1.32, Recency ratio=0.68
- Early IC=+0.1243, Recent IC=+0.0841, 1st-half IC=+0.0774, 2nd-half IC=+0.1025, Neg regimes=2/5
- Weak component: `demark_setup_reversal_early` (CV=1.42)
- Regime ICs: Q1_low_vol=-0.061, Q2=-0.010, Q3_mid=+0.102, Q4=+0.188, Q5_high_vol=+0.192

### 500ETF — `single` Median Features

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0913, Sharpe=-0.2578)
- Admission: Train IC=+0.1732, Deflated=+0.1723, IR=0.47, Mono=0.66, p=0.0016, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.146 | 2016: -0.049 | 2017: +0.116 | 2018: +0.052 | 2019: +0.111 | 2020: +0.099 | 2021: +0.059 | 2022: +0.031 | 2023: +0.014 | 2024: +0.206 | 2025: +0.045 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.366 | 2016: -0.072 | 2017: +0.120 | 2018: +0.289 | 2019: +0.301 | 2020: +0.036 | 2021: +0.277 | 2022: +0.172 | 2023: +0.004 | 2024: +0.350 | 2025: +0.081 | 2026: -0.170
- IC CV=0.78, Neg years (linear/tail)=1/1 of 7, Half ratio=0.96, Recency ratio=1.62
- Early IC=+0.0484, Recent IC=+0.0785, 1st-half IC=+0.0774, 2nd-half IC=+0.0742, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.082, Q3_mid=+0.074, Q4=+0.067, Q5_high_vol=+0.139

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0810, Sharpe=-0.4849)
- Admission: Train IC=+0.3327, Deflated=+0.3325, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.48
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172 | 2022: +0.052 | 2023: +0.095 | 2024: +0.153 | 2025: +0.057 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.208 | 2017: +0.327 | 2018: +0.611 | 2019: +0.275 | 2020: +0.129 | 2021: +0.238 | 2022: +0.147 | 2023: +0.148 | 2024: +0.202 | 2025: +0.099 | 2026: +0.012
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.99, Recency ratio=0.89
- Early IC=+0.1934, Recent IC=+0.1721, 1st-half IC=+0.2037, 2nd-half IC=+0.2016, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.128, Q3_mid=+0.198, Q4=+0.162, Q5_high_vol=+0.330

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0735, Sharpe=-0.4531)
- Admission: Train IC=+0.2749, Deflated=+0.2743, IR=0.98, Mono=0.78, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.336 | 2016: +0.119 | 2017: +0.177 | 2018: +0.206 | 2019: +0.122 | 2020: +0.138 | 2021: +0.144 | 2022: +0.049 | 2023: +0.082 | 2024: +0.082 | 2025: +0.036 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.138 | 2017: +0.392 | 2018: +0.365 | 2019: +0.340 | 2020: +0.091 | 2021: +0.204 | 2022: +0.072 | 2023: +0.148 | 2024: -0.046 | 2025: -0.056 | 2026: +0.117
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.76, Recency ratio=0.62
- Early IC=+0.2275, Recent IC=+0.1407, 1st-half IC=+0.2151, 2nd-half IC=+0.1629, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.090, Q3_mid=+0.187, Q4=+0.149, Q5_high_vol=+0.317

**`vwap_trend_channel_slope`** (Lock IC=+0.0602, Sharpe=-0.5999)
- Admission: Train IC=+0.1640, Deflated=+0.1634, IR=0.44, Mono=0.67, p=0.0028, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.52, Neg years (linear/tail)=0/0 of 7, Half ratio=0.87, Recency ratio=0.99
- Early IC=+0.0779, Recent IC=+0.0768, 1st-half IC=+0.1100, 2nd-half IC=+0.0960, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.063, Q3_mid=+0.120, Q4=+0.066, Q5_high_vol=+0.119

### 159915ETF — `single` Median Features

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0874, Sharpe=-0.0146)
- Admission: Train IC=+0.2252, Deflated=+0.2233, IR=0.49, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.144 | 2017: +0.039 | 2018: +0.090 | 2019: +0.170 | 2020: +0.123 | 2021: +0.182 | 2022: +0.107 | 2023: +0.162 | 2024: +0.076 | 2025: +0.169 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.110 | 2017: +0.207 | 2018: +0.247 | 2019: +0.212 | 2020: +0.075 | 2021: +0.387 | 2022: +0.280 | 2023: +0.372 | 2024: +0.081 | 2025: +0.269 | 2026: -0.309
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=1.37, Recency ratio=0.94
- Early IC=+0.1619, Recent IC=+0.1525, 1st-half IC=+0.1223, 2nd-half IC=+0.1675, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.082, Q3_mid=+0.198, Q4=+0.118, Q5_high_vol=+0.197

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0706, Sharpe=+0.4878)
- Admission: Train IC=+0.1928, Deflated=+0.1935, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130 | 2022: +0.096 | 2023: +0.023 | 2024: -0.052 | 2025: +0.076 | 2026: +0.197
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.203 | 2017: +0.113 | 2018: +0.268 | 2019: +0.174 | 2020: +0.304 | 2021: +0.283 | 2022: +0.225 | 2023: -0.082 | 2024: +0.218 | 2025: +0.014 | 2026: +0.361
- IC CV=0.88, Neg years (linear/tail)=1/0 of 7, Half ratio=1.82, Recency ratio=1.12
- Early IC=+0.0585, Recent IC=+0.0654, 1st-half IC=+0.0384, 2nd-half IC=+0.0698, Neg regimes=2/5
- Weak component: `limit_down_proximity_early` (CV=1.62)
- Regime ICs: Q1_low_vol=-0.027, Q2=-0.051, Q3_mid=+0.035, Q4=+0.145, Q5_high_vol=+0.115

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0189, Sharpe=+0.4526)
- Admission: Train IC=+0.2660, Deflated=+0.2658, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.075 | 2018: +0.166 | 2019: +0.085 | 2020: +0.075 | 2021: +0.151 | 2022: +0.095 | 2023: +0.091 | 2024: +0.027 | 2025: +0.042 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.223 | 2017: -0.036 | 2018: +0.422 | 2019: +0.218 | 2020: +0.178 | 2021: +0.408 | 2022: +0.272 | 2023: +0.144 | 2024: +0.208 | 2025: +0.115 | 2026: +0.191
- IC CV=0.82, Neg years (linear/tail)=1/1 of 7, Half ratio=1.02, Recency ratio=0.74
- Early IC=+0.1530, Recent IC=+0.1131, 1st-half IC=+0.1144, 2nd-half IC=+0.1172, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.053, Q2=+0.037, Q3_mid=+0.103, Q4=+0.200, Q5_high_vol=+0.197

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0184, Sharpe=+0.3625)
- Admission: Train IC=+0.1570, Deflated=+0.1561, IR=0.51, Mono=0.68, p=0.0036, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.068 | 2017: +0.034 | 2018: +0.193 | 2019: +0.044 | 2020: +0.042 | 2021: +0.166 | 2022: +0.017 | 2023: +0.160 | 2024: +0.115 | 2025: +0.020 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.208 | 2017: +0.139 | 2018: +0.354 | 2019: +0.158 | 2020: +0.046 | 2021: +0.209 | 2022: +0.019 | 2023: +0.234 | 2024: +0.156 | 2025: -0.023 | 2026: -0.122
- IC CV=0.64, Neg years (linear/tail)=0/0 of 7, Half ratio=1.30, Recency ratio=1.25
- Early IC=+0.0830, Recent IC=+0.1038, 1st-half IC=+0.0870, 2nd-half IC=+0.1131, Neg regimes=1/5
- Weak component: `early_vwap_acceleration` (CV=0.99)
- Regime ICs: Q1_low_vol=-0.029, Q2=+0.071, Q3_mid=+0.087, Q4=+0.187, Q5_high_vol=+0.135

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0616, Sharpe=+0.2757)
- Admission: Train IC=+0.2294, Deflated=+0.2299, IR=0.55, Mono=0.74, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109 | 2023: +0.058 | 2024: +0.021 | 2025: +0.045 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.260 | 2017: -0.063 | 2018: +0.287 | 2019: +0.204 | 2020: +0.254 | 2021: +0.174 | 2022: +0.239 | 2023: -0.083 | 2024: +0.166 | 2025: -0.078 | 2026: +0.337
- IC CV=1.14, Neg years (linear/tail)=1/1 of 7, Half ratio=0.62, Recency ratio=0.50
- Early IC=+0.1357, Recent IC=+0.0678, 1st-half IC=+0.1151, 2nd-half IC=+0.0718, Neg regimes=1/5
- Regime ICs: Q1_low_vol=-0.067, Q2=+0.000, Q3_mid=+0.053, Q4=+0.178, Q5_high_vol=+0.171

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0280, Sharpe=+0.0482)
- Admission: Train IC=+0.2949, Deflated=+0.2950, IR=0.76, Mono=0.73, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.095 | 2017: +0.008 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132 | 2022: +0.038 | 2023: +0.176 | 2024: +0.054 | 2025: +0.049 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.333 | 2016: +0.093 | 2017: +0.101 | 2018: +0.399 | 2019: +0.266 | 2020: +0.235 | 2021: +0.493 | 2022: +0.150 | 2023: +0.324 | 2024: +0.235 | 2025: -0.040 | 2026: +0.148
- IC CV=0.65, Neg years (linear/tail)=0/0 of 7, Half ratio=0.81, Recency ratio=0.50
- Early IC=+0.1745, Recent IC=+0.0867, 1st-half IC=+0.1480, 2nd-half IC=+0.1193, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.027, Q3_mid=+0.113, Q4=+0.191, Q5_high_vol=+0.227

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1183, Sharpe=+1.6160)
- Admission: Train IC=+0.2664, Deflated=+0.2657, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.022 | 2017: +0.204 | 2018: +0.144 | 2019: +0.184 | 2020: +0.146 | 2021: +0.091 | 2022: +0.051 | 2023: +0.067 | 2024: +0.098 | 2025: +0.035 | 2026: +0.240
- Yearly Tail ICs:   2015: +0.318 | 2016: -0.063 | 2017: +0.332 | 2018: +0.260 | 2019: +0.360 | 2020: +0.206 | 2021: +0.281 | 2022: -0.064 | 2023: +0.259 | 2024: +0.213 | 2025: -0.016 | 2026: +0.281
- IC CV=0.51, Neg years (linear/tail)=0/1 of 7, Half ratio=0.88, Recency ratio=0.75
- Early IC=+0.1578, Recent IC=+0.1187, 1st-half IC=+0.1709, 2nd-half IC=+0.1510, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.069, Q3_mid=+0.133, Q4=+0.104, Q5_high_vol=+0.298

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1139, Sharpe=+1.4937)
- Admission: Train IC=+0.2552, Deflated=+0.2542, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.119 | 2017: +0.110 | 2018: +0.189 | 2019: +0.088 | 2020: +0.115 | 2021: +0.140 | 2022: +0.076 | 2023: +0.053 | 2024: +0.120 | 2025: +0.138 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.471 | 2016: +0.195 | 2017: +0.217 | 2018: +0.389 | 2019: -0.049 | 2020: +0.108 | 2021: +0.319 | 2022: +0.065 | 2023: +0.203 | 2024: +0.172 | 2025: +0.259 | 2026: +0.331
- IC CV=0.39, Neg years (linear/tail)=0/1 of 7, Half ratio=0.73, Recency ratio=0.66
- Early IC=+0.1934, Recent IC=+0.1275, 1st-half IC=+0.1821, 2nd-half IC=+0.1331, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.047, Q3_mid=+0.127, Q4=+0.189, Q5_high_vol=+0.255

**`combo_rank_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1326, Sharpe=+1.4616)
- Admission: Train IC=+0.2789, Deflated=+0.2783, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.073 | 2017: +0.226 | 2018: +0.079 | 2019: +0.082 | 2020: +0.119 | 2021: +0.089 | 2022: +0.032 | 2023: +0.095 | 2024: +0.142 | 2025: +0.138 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.208 | 2017: +0.338 | 2018: +0.282 | 2019: +0.119 | 2020: +0.215 | 2021: +0.215 | 2022: +0.160 | 2023: +0.008 | 2024: +0.221 | 2025: +0.089 | 2026: +0.313
- IC CV=0.49, Neg years (linear/tail)=0/0 of 7, Half ratio=0.57, Recency ratio=0.71
- Early IC=+0.1481, Recent IC=+0.1050, 1st-half IC=+0.1663, 2nd-half IC=+0.0955, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.021, Q3_mid=+0.075, Q4=+0.159, Q5_high_vol=+0.166

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1703, Sharpe=+1.1170)
- Admission: Train IC=+0.2059, Deflated=+0.2050, IR=0.54, Mono=0.67, p=0.0006, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.049 | 2017: +0.197 | 2018: +0.137 | 2019: +0.171 | 2020: +0.117 | 2021: +0.085 | 2022: +0.063 | 2023: +0.095 | 2024: +0.154 | 2025: +0.121 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.029 | 2017: +0.149 | 2018: +0.211 | 2019: +0.461 | 2020: +0.261 | 2021: +0.230 | 2022: +0.173 | 2023: +0.060 | 2024: +0.225 | 2025: +0.057 | 2026: +0.339
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.85
- Early IC=+0.1182, Recent IC=+0.1008, 1st-half IC=+0.1531, 2nd-half IC=+0.1305, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.064, Q3_mid=+0.083, Q4=+0.120, Q5_high_vol=+0.224

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1256, Sharpe=+1.1032)
- Admission: Train IC=+0.3278, Deflated=+0.3273, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.194 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148 | 2022: +0.067 | 2023: +0.066 | 2024: +0.124 | 2025: +0.091 | 2026: +0.173
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.050 | 2017: +0.172 | 2018: +0.350 | 2019: +0.480 | 2020: +0.209 | 2021: +0.281 | 2022: -0.024 | 2023: +0.135 | 2024: +0.177 | 2025: +0.125 | 2026: +0.352
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=1.09, Recency ratio=1.10
- Early IC=+0.1593, Recent IC=+0.1745, 1st-half IC=+0.1769, 2nd-half IC=+0.1933, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.127, Q3_mid=+0.142, Q4=+0.125, Q5_high_vol=+0.303

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1100, Sharpe=+1.0815)
- Admission: Train IC=+0.2642, Deflated=+0.2624, IR=0.92, Mono=0.82, p=0.0000, MaxCorr=0.23
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052 | 2022: +0.096 | 2023: +0.046 | 2024: +0.073 | 2025: +0.148 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.229 | 2017: +0.386 | 2018: +0.332 | 2019: +0.207 | 2020: +0.271 | 2021: +0.214 | 2022: -0.027 | 2023: +0.087 | 2024: +0.035 | 2025: +0.246 | 2026: +0.214
- IC CV=0.52, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.56
- Early IC=+0.1961, Recent IC=+0.1099, 1st-half IC=+0.1766, 2nd-half IC=+0.1186, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.040, Q3_mid=+0.111, Q4=+0.129, Q5_high_vol=+0.273

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0842, Sharpe=+0.9334)
- Admission: Train IC=+0.3397, Deflated=+0.3393, IR=1.05, Mono=0.84, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.124 | 2017: +0.192 | 2018: +0.197 | 2019: +0.140 | 2020: +0.173 | 2021: +0.106 | 2022: +0.060 | 2023: +0.072 | 2024: +0.083 | 2025: +0.103 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.325 | 2016: +0.264 | 2017: +0.363 | 2018: +0.460 | 2019: +0.190 | 2020: +0.344 | 2021: +0.046 | 2022: +0.063 | 2023: -0.009 | 2024: +0.191 | 2025: +0.028 | 2026: +0.081
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.68, Recency ratio=0.65
- Early IC=+0.2133, Recent IC=+0.1391, 1st-half IC=+0.2280, 2nd-half IC=+0.1555, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.045, Q3_mid=+0.163, Q4=+0.237, Q5_high_vol=+0.255

**`combo_rel_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0020, Sharpe=+0.7804)
- Admission: Train IC=+0.2636, Deflated=+0.2642, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.42
- Yearly Linear ICs: 2015: +0.149 | 2016: +0.138 | 2017: -0.011 | 2018: +0.082 | 2019: +0.070 | 2020: +0.030 | 2021: +0.081 | 2022: +0.057 | 2023: -0.004 | 2024: +0.054 | 2025: -0.068 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.451 | 2016: +0.224 | 2017: +0.122 | 2018: +0.264 | 2019: +0.306 | 2020: +0.144 | 2021: +0.132 | 2022: -0.023 | 2023: -0.009 | 2024: +0.100 | 2025: -0.102 | 2026: +0.414
- IC CV=0.68, Neg years (linear/tail)=1/0 of 7, Half ratio=0.62, Recency ratio=0.39
- Early IC=+0.1439, Recent IC=+0.0554, 1st-half IC=+0.1027, 2nd-half IC=+0.0632, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.132, Q3_mid=+0.068, Q4=+0.036, Q5_high_vol=+0.186

**`combo_rank_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0890, Sharpe=+0.7110)
- Admission: Train IC=+0.3274, Deflated=+0.3260, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.120 | 2017: +0.197 | 2018: +0.186 | 2019: +0.120 | 2020: +0.115 | 2021: +0.090 | 2022: +0.055 | 2023: +0.027 | 2024: +0.084 | 2025: +0.133 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.174 | 2017: +0.334 | 2018: +0.177 | 2019: +0.333 | 2020: +0.149 | 2021: +0.117 | 2022: +0.152 | 2023: -0.119 | 2024: +0.186 | 2025: +0.247 | 2026: -0.229
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.51
- Early IC=+0.2027, Recent IC=+0.1027, 1st-half IC=+0.1819, 2nd-half IC=+0.1313, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.018, Q3_mid=+0.169, Q4=+0.138, Q5_high_vol=+0.267

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1504, Sharpe=+0.5807)
- Admission: Train IC=+0.2007, Deflated=+0.1999, IR=0.34, Mono=0.66, p=0.0006, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089 | 2022: +0.105 | 2023: +0.057 | 2024: +0.162 | 2025: +0.063 | 2026: +0.204
- Yearly Tail ICs:   2015: +0.192 | 2016: -0.072 | 2017: +0.231 | 2018: +0.325 | 2019: +0.267 | 2020: +0.186 | 2021: +0.230 | 2022: +0.217 | 2023: -0.018 | 2024: +0.079 | 2025: -0.129 | 2026: +0.216
- IC CV=0.38, Neg years (linear/tail)=0/1 of 7, Half ratio=0.79, Recency ratio=0.76
- Early IC=+0.1304, Recent IC=+0.0989, 1st-half IC=+0.1628, 2nd-half IC=+0.1279, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.044, Q3_mid=+0.093, Q4=+0.132, Q5_high_vol=+0.210

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0995, Sharpe=+0.5483)
- Admission: Train IC=+0.2185, Deflated=+0.2177, IR=0.74, Mono=0.75, p=0.0004, MaxCorr=0.09
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022 | 2022: -0.017 | 2023: -0.025 | 2024: +0.066 | 2025: +0.145 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.012 | 2017: +0.223 | 2018: +0.364 | 2019: +0.285 | 2020: +0.243 | 2021: +0.162 | 2022: -0.008 | 2023: -0.037 | 2024: +0.089 | 2025: +0.216 | 2026: +0.070
- IC CV=0.53, Neg years (linear/tail)=0/0 of 7, Half ratio=0.63, Recency ratio=0.44
- Early IC=+0.1622, Recent IC=+0.0708, 1st-half IC=+0.1680, 2nd-half IC=+0.1053, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.018, Q3_mid=+0.193, Q4=+0.079, Q5_high_vol=+0.219

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0948, Sharpe=+0.4283)
- Admission: Train IC=+0.2721, Deflated=+0.2709, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.084 | 2017: +0.247 | 2018: +0.154 | 2019: +0.106 | 2020: +0.168 | 2021: +0.113 | 2022: +0.116 | 2023: +0.080 | 2024: +0.149 | 2025: +0.116 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.543 | 2016: +0.168 | 2017: +0.280 | 2018: +0.201 | 2019: +0.261 | 2020: +0.072 | 2021: +0.310 | 2022: +0.226 | 2023: +0.106 | 2024: +0.236 | 2025: +0.069 | 2026: -0.077
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.74
- Early IC=+0.1904, Recent IC=+0.1405, 1st-half IC=+0.1985, 2nd-half IC=+0.1446, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.053, Q3_mid=+0.145, Q4=+0.173, Q5_high_vol=+0.266

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0856, Sharpe=+0.2376)
- Admission: Train IC=+0.2083, Deflated=+0.2078, IR=0.62, Mono=0.71, p=0.0006, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.099 | 2017: +0.263 | 2018: +0.229 | 2019: +0.143 | 2020: +0.129 | 2021: +0.080 | 2022: +0.086 | 2023: +0.045 | 2024: +0.129 | 2025: +0.103 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.253 | 2016: -0.005 | 2017: +0.209 | 2018: +0.421 | 2019: +0.111 | 2020: +0.210 | 2021: +0.198 | 2022: +0.202 | 2023: +0.201 | 2024: +0.222 | 2025: +0.037 | 2026: -0.223
- IC CV=0.40, Neg years (linear/tail)=0/1 of 7, Half ratio=0.78, Recency ratio=0.64
- Early IC=+0.1627, Recent IC=+0.1045, 1st-half IC=+0.1910, 2nd-half IC=+0.1492, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.021, Q3_mid=+0.154, Q4=+0.131, Q5_high_vol=+0.236

**`combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0439, Sharpe=+0.1933)
- Admission: Train IC=+0.2254, Deflated=+0.2258, IR=0.64, Mono=0.71, p=0.0002, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.031 | 2017: +0.038 | 2018: +0.083 | 2019: +0.134 | 2020: +0.109 | 2021: +0.111 | 2022: +0.009 | 2023: +0.017 | 2024: +0.060 | 2025: -0.043 | 2026: +0.180
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.035 | 2017: +0.446 | 2018: +0.249 | 2019: +0.260 | 2020: +0.316 | 2021: +0.032 | 2022: -0.110 | 2023: +0.042 | 2024: +0.107 | 2025: -0.109 | 2026: +0.430
- IC CV=0.53, Neg years (linear/tail)=0/0 of 7, Half ratio=1.55, Recency ratio=0.96
- Early IC=+0.1143, Recent IC=+0.1099, 1st-half IC=+0.0785, 2nd-half IC=+0.1219, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.117, Q3_mid=+0.049, Q4=+0.035, Q5_high_vol=+0.208

**`combo_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0693, Sharpe=+0.1614)
- Admission: Train IC=+0.2549, Deflated=+0.2541, IR=0.91, Mono=0.80, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.100 | 2017: +0.147 | 2018: +0.200 | 2019: +0.067 | 2020: +0.125 | 2021: +0.058 | 2022: +0.113 | 2023: +0.087 | 2024: +0.124 | 2025: +0.091 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.212 | 2017: +0.248 | 2018: +0.292 | 2019: +0.116 | 2020: +0.235 | 2021: +0.206 | 2022: +0.130 | 2023: +0.136 | 2024: +0.269 | 2025: -0.136 | 2026: -0.330
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.58
- Early IC=+0.1575, Recent IC=+0.0915, 1st-half IC=+0.1763, 2nd-half IC=+0.1174, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.151, Q2=-0.013, Q3_mid=+0.161, Q4=+0.169, Q5_high_vol=+0.250

**`combo_ratio__max_down_ret__net_volume_flow`** (Lock IC=+0.1213, Sharpe=+0.1422)
- Admission: Train IC=+0.2240, Deflated=+0.2235, IR=0.85, Mono=0.79, p=0.0002, MaxCorr=0.09
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004 | 2022: -0.056 | 2023: +0.007 | 2024: +0.084 | 2025: +0.166 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.355 | 2016: +0.225 | 2017: +0.296 | 2018: +0.169 | 2019: +0.110 | 2020: +0.294 | 2021: +0.250 | 2022: -0.197 | 2023: -0.187 | 2024: +0.121 | 2025: +0.191 | 2026: -0.073
- IC CV=0.47, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.42
- Early IC=+0.1662, Recent IC=+0.0693, 1st-half IC=+0.1599, 2nd-half IC=+0.1020, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.001, Q3_mid=+0.137, Q4=+0.092, Q5_high_vol=+0.174

### 159915ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1249, Sharpe=+1.6314)
- Admission: Train IC=+0.2559, Deflated=+0.2535, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.147 | 2017: -0.017 | 2018: +0.150 | 2019: +0.223 | 2020: +0.209 | 2021: +0.110 | 2022: +0.076 | 2023: +0.086 | 2024: +0.078 | 2025: +0.124 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.141 | 2016: +0.231 | 2017: +0.120 | 2018: +0.313 | 2019: +0.366 | 2020: +0.293 | 2021: +0.225 | 2022: +0.186 | 2023: +0.115 | 2024: +0.337 | 2025: +0.341 | 2026: +0.246
- IC CV=0.55, Neg years (linear/tail)=1/0 of 7, Half ratio=1.12, Recency ratio=0.78
- Early IC=+0.2057, Recent IC=+0.1596, 1st-half IC=+0.1691, 2nd-half IC=+0.1894, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.076, Q3_mid=+0.149, Q4=+0.215, Q5_high_vol=+0.246

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1318, Sharpe=+1.5570)
- Admission: Train IC=+0.2614, Deflated=+0.2594, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.122 | 2017: +0.009 | 2018: +0.185 | 2019: +0.198 | 2020: +0.148 | 2021: +0.176 | 2022: +0.130 | 2023: +0.136 | 2024: +0.070 | 2025: +0.162 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.117 | 2016: +0.125 | 2017: +0.107 | 2018: +0.415 | 2019: +0.384 | 2020: +0.219 | 2021: +0.441 | 2022: +0.152 | 2023: +0.165 | 2024: +0.395 | 2025: +0.173 | 2026: +0.125
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=1.16, Recency ratio=0.93
- Early IC=+0.1753, Recent IC=+0.1623, 1st-half IC=+0.1624, 2nd-half IC=+0.1878, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.071, Q3_mid=+0.162, Q4=+0.257, Q5_high_vol=+0.208

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1423, Sharpe=+1.5511)
- Admission: Train IC=+0.2945, Deflated=+0.2928, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.046 | 2017: +0.009 | 2018: +0.127 | 2019: +0.235 | 2020: +0.125 | 2021: +0.141 | 2022: +0.096 | 2023: +0.184 | 2024: +0.126 | 2025: +0.179 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.075 | 2017: +0.102 | 2018: +0.348 | 2019: +0.519 | 2020: +0.299 | 2021: +0.329 | 2022: +0.400 | 2023: +0.342 | 2024: +0.335 | 2025: +0.165 | 2026: +0.364
- IC CV=0.58, Neg years (linear/tail)=0/0 of 7, Half ratio=1.42, Recency ratio=1.13
- Early IC=+0.1182, Recent IC=+0.1331, 1st-half IC=+0.1155, 2nd-half IC=+0.1644, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.101, Q3_mid=+0.163, Q4=+0.164, Q5_high_vol=+0.162

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1327, Sharpe=+1.3316)
- Admission: Train IC=+0.2637, Deflated=+0.2612, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.078 | 2017: -0.023 | 2018: +0.106 | 2019: +0.259 | 2020: +0.133 | 2021: +0.110 | 2022: +0.073 | 2023: +0.152 | 2024: +0.091 | 2025: +0.148 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.178 | 2016: +0.083 | 2017: +0.045 | 2018: +0.286 | 2019: +0.500 | 2020: +0.173 | 2021: +0.294 | 2022: +0.258 | 2023: +0.211 | 2024: +0.394 | 2025: +0.080 | 2026: +0.232
- IC CV=0.69, Neg years (linear/tail)=1/0 of 7, Half ratio=1.25, Recency ratio=0.76
- Early IC=+0.1588, Recent IC=+0.1212, 1st-half IC=+0.1288, 2nd-half IC=+0.1607, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.035, Q3_mid=+0.115, Q4=+0.166, Q5_high_vol=+0.214

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1311, Sharpe=+1.1520)
- Admission: Train IC=+0.1683, Deflated=+0.1674, IR=0.47, Mono=0.70, p=0.0024, MaxCorr=0.10
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087 | 2022: +0.139 | 2023: +0.083 | 2024: +0.083 | 2025: +0.120 | 2026: +0.148
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.017 | 2017: +0.138 | 2018: +0.257 | 2019: +0.117 | 2020: +0.189 | 2021: +0.114 | 2022: +0.057 | 2023: -0.092 | 2024: +0.146 | 2025: +0.162 | 2026: +0.240
- IC CV=0.73, Neg years (linear/tail)=0/1 of 7, Half ratio=0.82, Recency ratio=0.73
- Early IC=+0.0981, Recent IC=+0.0711, 1st-half IC=+0.1115, 2nd-half IC=+0.0914, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.004, Q3_mid=+0.061, Q4=+0.194, Q5_high_vol=+0.118

**`combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1258, Sharpe=+0.7925)
- Admission: Train IC=+0.2920, Deflated=+0.2899, IR=0.48, Mono=0.66, p=0.0000, MaxCorr=0.54
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.155 | 2017: -0.024 | 2018: +0.139 | 2019: +0.212 | 2020: +0.130 | 2021: +0.133 | 2022: +0.085 | 2023: +0.133 | 2024: +0.070 | 2025: +0.156 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.204 | 2016: +0.127 | 2017: +0.059 | 2018: +0.221 | 2019: +0.504 | 2020: +0.153 | 2021: +0.402 | 2022: +0.185 | 2023: +0.168 | 2024: +0.205 | 2025: +0.224 | 2026: +0.145
- IC CV=0.54, Neg years (linear/tail)=1/0 of 7, Half ratio=1.31, Recency ratio=0.70
- Early IC=+0.1884, Recent IC=+0.1311, 1st-half IC=+0.1293, 2nd-half IC=+0.1688, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.061, Q3_mid=+0.182, Q4=+0.149, Q5_high_vol=+0.232

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1192, Sharpe=+0.6699)
- Admission: Train IC=+0.2510, Deflated=+0.2513, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034 | 2022: +0.178 | 2023: +0.116 | 2024: +0.078 | 2025: +0.128 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.193 | 2016: +0.190 | 2017: +0.027 | 2018: +0.354 | 2019: +0.280 | 2020: +0.401 | 2021: +0.167 | 2022: +0.459 | 2023: +0.095 | 2024: +0.032 | 2025: +0.061 | 2026: +0.267
- IC CV=0.90, Neg years (linear/tail)=1/0 of 7, Half ratio=0.89, Recency ratio=0.61
- Early IC=+0.1112, Recent IC=+0.0677, 1st-half IC=+0.0972, 2nd-half IC=+0.0869, Neg regimes=1/5
- Weak component: `yesterday_first_30min_return` (CV=1.04)
- Regime ICs: Q1_low_vol=-0.035, Q2=+0.057, Q3_mid=+0.071, Q4=+0.110, Q5_high_vol=+0.159

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1093 | +0.0576 | +0.1515 | 2y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | TP | persistent | +0.0960 | +0.0234 | +0.1970 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0951 | +0.0914 | +0.0035 | 2y |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Median | gradual | +0.0623 | +0.1381 | -0.0763 | 2y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | gradual | +0.0447 | +0.1960 | -0.2064 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | gradual | +0.0440 | +0.1405 | -0.0163 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0377 | +0.1764 | -0.0345 | 4y |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Median | gradual | +0.0361 | +0.1513 | -0.0650 | 4y |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | FP | gradual | +0.0185 | +0.0578 | -0.0352 | 2y |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | TP | gradual | +0.0168 | +0.1601 | -0.0787 | 4y |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | gradual | +0.0156 | +0.1733 | -0.1061 | 4y |
| `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio` | FP | immediate | -0.1021 | -0.0764 | -0.1781 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=8, persistent=3

**FP decay trajectories:**

- `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio`: Y1:-0.102 → Y2:-0.076 → Y3:+0.005 → Y4:+0.035 → Y5:-0.178
- `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.016 → Y2:+0.173 → Y3:+0.026 → Y4:+0.012 → Y5:-0.106
- `combo_ratio__first_bar_sentiment__volume_surge_direction`: Y1:+0.019 → Y2:+0.058 → Y3:-0.051 → Y4:+0.006 → Y5:-0.035
- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.045 → Y2:+0.196 → Y3:+0.038 → Y4:+0.106 → Y5:-0.206

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1159 | +0.0796 | -0.0265 | 4y |
| `combo_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1130 | +0.0872 | -0.0648 | 4y |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1053 | +0.0568 | +0.2040 | ∞ |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0404 | 1y |
| `combo_max__bar_ret_0__max_down_ret` | TP | gradual | +0.0865 | +0.0449 | -0.0028 | 4y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0756 | +0.0530 | +0.0807 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0667 | +0.0659 | +0.1729 | ∞ |
| `vwap_trend_channel_slope` | Median | gradual | +0.0667 | +0.1186 | -0.0312 | 4y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0626 | +0.0952 | +0.1864 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0600 | +0.0723 | +0.0459 | ∞ |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | TP | fast | +0.0569 | -0.0040 | +0.1243 | 1y |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | TP | persistent | +0.0553 | +0.0273 | +0.0177 | 1y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0514 | +0.0668 | +0.2403 | ∞ |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Median | persistent | +0.0494 | +0.0815 | +0.1020 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0392 | +0.0958 | +0.0770 | ∞ |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Median | gradual | +0.0315 | +0.0144 | -0.0292 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | persistent | +0.0093 | +0.0167 | +0.1802 | ∞ |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | TP | immediate | -0.0168 | -0.0247 | +0.1016 | ∞ |
| `combo_ratio__max_down_ret__net_volume_flow` | TP | immediate | -0.0560 | +0.0066 | +0.1091 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=1, gradual=5, persistent=12

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1776 | +0.1159 | +0.1263 | 2y |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1388 | +0.0826 | +0.1479 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1299 | +0.1363 | +0.1021 | ∞ |
| `combo_rank_max__max_up_ret__bar_ret_0` | Median | gradual | +0.1079 | +0.1605 | -0.0628 | 4y |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0959 | +0.1836 | +0.0723 | ∞ |
| `combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0850 | +0.1331 | +0.1010 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0761 | +0.0861 | +0.1174 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0733 | +0.1517 | +0.1033 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=1, persistent=7

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.746±0.027 | 0.717±0.024 | 24% | USEFUL |
| ic_ir | 0.662±0.083 | 0.608±0.085 | 60% | WEAK |
| p_value | 0.005±0.006 | 0.001±0.001 | 23% | USEFUL |
| max_corr | 0.392±0.299 | 0.602±0.303 | 83% | USELESS |
| deflated_ic | 0.175±0.039 | 0.228±0.050 | 40% | USEFUL |
| overall_ic | 0.175±0.039 | 0.228±0.049 | 40% | USEFUL |
| raw_ic | 0.067±0.015 | 0.099±0.026 | 33% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 14/20 top rejects are profitable (70%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0379, Sharpe=+1.0599
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717

**B2 Rolling Guard**: 8/20 top rejects are profitable (40%)

- `combo_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2064, Lock IC=+0.0263, Sharpe=+0.8994
- `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2042, Lock IC=+0.0016, Sharpe=+0.5869
- `combo_clamp_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1865, Lock IC=+0.0088, Sharpe=+0.5399

**Temporal Validation Gate**: 5/20 top rejects are profitable (25%)

- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2050, Lock IC=+0.0161, Sharpe=+0.4649
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1940, Lock IC=+0.0446, Sharpe=+0.2764
- `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1940, Lock IC=+0.0446, Sharpe=+0.2764

**B3 Composite Floor**: 9/20 top rejects are profitable (45%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2005, Lock IC=+0.0275, Sharpe=+0.4235
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2005, Lock IC=+0.0275, Sharpe=+0.4235
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2120, Lock IC=+0.0218, Sharpe=+0.3967

**B4 Correlation Gate**: 17/20 top rejects are profitable (85%)

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2747, Lock IC=+0.0342, Sharpe=+1.2516
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2356, Lock IC=+0.0236, Sharpe=+0.7941
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2667, Lock IC=+0.0505, Sharpe=+0.6801

**Adaptive Correlation Gate**: 3/8 top rejects are profitable (38%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1836, Lock IC=+0.0737, Sharpe=+1.3074
- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.2141, Lock IC=+0.0747, Sharpe=+0.3762
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Train IC=+0.1600, Lock IC=+0.0283, Sharpe=+0.0760

### 500ETF — `single`

**7-Year Jackknife**: 18/20 top rejects are profitable (90%)

- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2429, Lock IC=+0.0860, Sharpe=+0.7897
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897

**B2 Rolling Guard**: 16/20 top rejects are profitable (80%)

- `combo_rank_max__first_bar_sentiment__trend_bar_close_consistency`: Train IC=+0.2188, Lock IC=+0.0624, Sharpe=+0.9635
- `combo_mean__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Sharpe=+0.7111
- `combo_z_sum__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Sharpe=+0.7111

**Temporal Validation Gate**: 19/20 top rejects are profitable (95%)

- `combo_clamp_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.2680, Lock IC=+0.0706, Sharpe=+0.9373
- `combo_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293
- `combo_z_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293

**B3 Composite Floor**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2806, Lock IC=+0.1172, Sharpe=+1.1947
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2806, Lock IC=+0.1172, Sharpe=+1.1947
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2945, Lock IC=+0.1037, Sharpe=+1.1804

**B6 Yearly IC CV Gate**: 2/2 top rejects are profitable (100%)

- `combo_rel_diff__close_vs_open_range__early_body_momentum`: Train IC=+0.1203, Lock IC=+0.0327, Sharpe=+0.3549
- `combo_rel_diff__close_vs_open_range__opening_momentum_score`: Train IC=+0.1203, Lock IC=+0.0327, Sharpe=+0.3549

**B6 Temporal Stability Gate**: 17/20 top rejects are profitable (85%)

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.3316, Lock IC=+0.1208, Sharpe=+1.2786
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.3032, Lock IC=+0.1262, Sharpe=+1.2622
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.3136, Lock IC=+0.1081, Sharpe=+0.9335

**B4 Correlation Gate**: 18/20 top rejects are profitable (90%)

- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.3443
- `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.3197, Lock IC=+0.1285, Sharpe=+1.1219
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.3068, Lock IC=+0.1015, Sharpe=+1.0848

**Adaptive Correlation Gate**: 16/20 top rejects are profitable (80%)

- `combo_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2965, Lock IC=+0.1083, Sharpe=+1.3443
- `combo_rank_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2868, Lock IC=+0.1125, Sharpe=+1.0528
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.2832, Lock IC=+0.1261, Sharpe=+0.8321

### 159915ETF — `single`

**7-Year Jackknife**: 13/20 top rejects are profitable (65%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3040, Lock IC=+0.1149, Sharpe=+1.4111

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2801, Lock IC=+0.1413, Sharpe=+1.4595

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.2088, Lock IC=+0.1414, Sharpe=+1.7112
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2088, Lock IC=+0.1414, Sharpe=+1.7112
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.2395, Lock IC=+0.1342, Sharpe=+1.6593

**BH-FDR Gate**: 4/5 top rejects are profitable (80%)

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Sharpe=+1.0460

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.8373
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.8373
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2895, Lock IC=+0.1279, Sharpe=+1.8188

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Sharpe=+1.8188

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1182 | 78 | 25 | 25 | 28 | 32% | 36% |
| B2 Rolling Guard | 254 | 78 | 34 | 25 | 19 | 44% | 24% |
| Temporal Validation Gate | 132 | 78 | 11 | 31 | 36 | 14% | 46% |
| BH-FDR Gate | 3 | 3 | 3 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 60 | 60 | 20 | 8 | 32 | 33% | 53% |
| B4 Correlation Gate | 103 | 78 | 12 | 10 | 56 | 15% | 72% |
| Adaptive Correlation Gate | 8 | 8 | 4 | 1 | 3 | 50% | 38% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0379, Sharpe=+1.0599
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717

**B2 Rolling Guard** — top TP casualties:
- `combo_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2064, Lock IC=+0.0263, Sharpe=+0.8994
- `combo_abs_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1341, Lock IC=+0.0763, Sharpe=+0.7390
- `combo_abs_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1341, Lock IC=+0.0763, Sharpe=+0.7390

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1219, Lock IC=+0.0096, Sharpe=+0.5399
- `combo_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1663, Lock IC=+0.0518, Sharpe=+0.5227
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1663, Lock IC=+0.0518, Sharpe=+0.5227

**B3 Composite Floor** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.1565, Lock IC=+0.0788, Sharpe=+1.2884
- `combo_tri_min__first_bar_return__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1409, Lock IC=+0.0080, Sharpe=+0.5557
- `combo_tri_min__bar_ret_0__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1405, Lock IC=+0.0093, Sharpe=+0.5557

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1836, Lock IC=+0.0737, Sharpe=+1.3074
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2747, Lock IC=+0.0342, Sharpe=+1.2516
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2356, Lock IC=+0.0236, Sharpe=+0.7941

**Adaptive Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1836, Lock IC=+0.0737, Sharpe=+1.3074
- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.2141, Lock IC=+0.0747, Sharpe=+0.3762
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Train IC=+0.1600, Lock IC=+0.0283, Sharpe=+0.0760

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1583 | 78 | 32 | 18 | 28 | 41% | 36% |
| B2 Rolling Guard | 322 | 78 | 20 | 15 | 43 | 26% | 55% |
| Temporal Validation Gate | 249 | 78 | 20 | 19 | 39 | 26% | 50% |
| BH-FDR Gate | 11 | 11 | 11 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 276 | 78 | 0 | 17 | 61 | 0% | 78% |
| B6 Yearly IC CV Gate | 2 | 2 | 0 | 0 | 2 | 0% | 100% |
| B6 Temporal Stability Gate | 249 | 78 | 0 | 24 | 54 | 0% | 69% |
| B4 Correlation Gate | 484 | 78 | 0 | 13 | 65 | 0% | 83% |
| Adaptive Correlation Gate | 33 | 33 | 0 | 10 | 23 | 0% | 70% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2429, Lock IC=+0.0860, Sharpe=+0.7897
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0000, Lock IC=+0.0648, Sharpe=+1.0326
- `combo_rank_max__first_bar_sentiment__trend_bar_close_consistency`: Train IC=+0.2188, Lock IC=+0.0624, Sharpe=+0.9635
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1336, Lock IC=+0.0664, Sharpe=+0.9384

**Temporal Validation Gate** — top TP casualties:
- `combo_clamp_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.2680, Lock IC=+0.0706, Sharpe=+0.9373
- `combo_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293
- `combo_z_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293

**B3 Composite Floor** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2806, Lock IC=+0.1172, Sharpe=+1.1947
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2806, Lock IC=+0.1172, Sharpe=+1.1947
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2945, Lock IC=+0.1037, Sharpe=+1.1804

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_rel_diff__close_vs_open_range__early_body_momentum`: Train IC=+0.1203, Lock IC=+0.0327, Sharpe=+0.3549
- `combo_rel_diff__close_vs_open_range__opening_momentum_score`: Train IC=+0.1203, Lock IC=+0.0327, Sharpe=+0.3549

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.3316, Lock IC=+0.1208, Sharpe=+1.2786
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.3032, Lock IC=+0.1262, Sharpe=+1.2622
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.3136, Lock IC=+0.1081, Sharpe=+0.9335

**B4 Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.3443
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+1.1454
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+1.1454

**Adaptive Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2965, Lock IC=+0.1083, Sharpe=+1.3443
- `combo_rank_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2868, Lock IC=+0.1125, Sharpe=+1.0528
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.2832, Lock IC=+0.1261, Sharpe=+0.8321

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1013 | 78 | 19 | 20 | 39 | 24% | 50% |
| B2 Rolling Guard | 324 | 78 | 17 | 9 | 52 | 22% | 67% |
| Temporal Validation Gate | 46 | 46 | 5 | 11 | 30 | 11% | 65% |
| BH-FDR Gate | 5 | 5 | 1 | 0 | 4 | 20% | 80% |
| B3 Composite Floor | 257 | 78 | 0 | 5 | 73 | 0% | 94% |
| B4 Correlation Gate | 50 | 50 | 0 | 4 | 46 | 0% | 92% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3040, Lock IC=+0.1149, Sharpe=+1.4111

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2801, Lock IC=+0.1413, Sharpe=+1.4595

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.2088, Lock IC=+0.1414, Sharpe=+1.7112
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2088, Lock IC=+0.1414, Sharpe=+1.7112
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.2395, Lock IC=+0.1342, Sharpe=+1.6593

**BH-FDR Gate** — top TP casualties:
- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Sharpe=+1.0460

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.8373
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.8373
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2895, Lock IC=+0.1279, Sharpe=+1.8188

**B4 Correlation Gate** — top TP casualties:
- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_z_sum__bar_ret_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2144, Lock IC=+0.1277, Sharpe=+1.8753

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (132 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 95 | 50 | 14 | 10 | 26 | 28% | 20% |
| recency_ratio >= 2.5 (late-concentrated) | 37 | 37 | 9 | 18 | 10 | 24% | 49% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1705, Lock IC=+0.0632, Sharpe=+0.7291
- `combo_rank_min__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1705, Lock IC=+0.0632, Sharpe=+0.7291
- `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1774, Lock IC=+0.0530, Sharpe=+0.6354
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1774, Lock IC=+0.0530, Sharpe=+0.6354
- `combo_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1663, Lock IC=+0.0518, Sharpe=+0.5227

### 500ETF — `single` (249 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 231 | 50 | 0 | 44 | 6 | 0% | 88% |
| recency_ratio >= 2.5 (late-concentrated) | 18 | 18 | 9 | 7 | 2 | 50% | 39% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.2296, Lock IC=+0.0651, Sharpe=+0.8443
- `combo_rank_max__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.2296, Lock IC=+0.0651, Sharpe=+0.8443
- `combo_rank_max__max_up_ret__first_bar_sentiment`: Train IC=+0.2356, Lock IC=+0.0793, Sharpe=+0.8294
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression`: Train IC=+0.1384, Lock IC=+0.0581, Sharpe=+0.4682
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Train IC=+0.1208, Lock IC=+0.0733, Sharpe=+0.4136

### 159915ETF — `single` (46 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 30 | 30 | 5 | 14 | 11 | 17% | 47% |
| recency_ratio >= 2.5 (late-concentrated) | 16 | 16 | 0 | 16 | 0 | 0% | 100% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.2395, Lock IC=+0.1342, Sharpe=+1.6593
- `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.2395, Lock IC=+0.1342, Sharpe=+1.6593
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2409, Lock IC=+0.1319, Sharpe=+1.6572
- `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2102, Lock IC=+0.1315, Sharpe=+1.5332
- `combo_z_sum__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2102, Lock IC=+0.1315, Sharpe=+1.5332

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_std_across_regimes`: FP is lower (d=-2.43). Threshold 0.096 → 44% accuracy.
- `recency_ratio`: FP is higher (d=+1.36). Threshold 1.455 → 89% accuracy.
- `half_ratio`: FP is higher (d=+0.95). Threshold 1.386 → 78% accuracy.
- `n_negative_years`: FP is higher (d=+0.66). Threshold 1.500 → 67% accuracy.
- `weak_link_cv`: FP is lower (d=-0.53). Threshold 1.219 → 62% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/4
- Decaying signal (half ratio < 0.3): 0/4
- Weak component (CV > 2.0): 0/4
- Regime-dependent (≥2 negative regimes): 1/4

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_weighted_price_position` | 2 | 0 | 2 | 100% |  |
| `opening_drive_thrust_ratio` | 2 | 3 | 5 | 40% |  |
| `first_bar_sentiment` | 1 | 4 | 5 | 20% |  |
| `max_up_ret` | 1 | 7 | 8 | 12% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 5 | 5 | 0% |  |
| `bar_ret_0` | 0 | 4 | 4 | 0% |  |
| `star50_limit_proximity_early` | 0 | 10 | 10 | 0% |  |
| `max_down_ret` | 0 | 6 | 6 | 0% |  |
| `close_vs_open_range` | 0 | 2 | 2 | 0% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `bar_body_rng_0` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 3 | 3 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 2 | 2 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=11, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=6, FP rate=25%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=3, FP rate=25%

