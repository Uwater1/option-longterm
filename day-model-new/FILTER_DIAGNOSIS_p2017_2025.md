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
| 300ETF | single | 4 | 3 | 1 | 0 | 75% | 0.03 |
| 500ETF | single | 12 | 1 | 7 | 4 | 8% | 0.38 |
| 159915ETF | single | 11 | 0 | 2 | 9 | 0% | 0.81 |

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

### 300ETF — `single` False Positives

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0223, Sharpe=-1.3571)
- Admission: Train IC=+0.2655, Deflated=+0.2657, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.00
- Yearly ICs: 2017: +0.020 | 2018: +0.182 | 2019: +0.072 | 2020: -0.000 | 2021: +0.133 | 2022: +0.045 | 2023: +0.170 | 2024: +0.055
- IC CV=0.76, Neg years=1/8, Half ratio=1.46, Recency ratio=1.11
- Early IC=+0.1009, Recent IC=+0.1125, 1st-half IC=+0.0717, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.079, Q3_mid=+0.041, Q4=+0.072, Q5_high_vol=+0.177

**`combo_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=-0.0284, Sharpe=-0.8306)
- Admission: Train IC=+0.1614, Deflated=+0.1623, IR=0.60, Mono=0.72, p=0.0014, MaxCorr=0.57
- Yearly ICs: 2017: +0.034 | 2018: +0.192 | 2019: +0.044 | 2020: +0.043 | 2021: +0.166 | 2022: +0.020 | 2023: +0.162 | 2024: +0.115
- IC CV=0.67, Neg years=0/8, Half ratio=1.60, Recency ratio=1.23
- Early IC=+0.1128, Recent IC=+0.1383, 1st-half IC=+0.0744, 2nd-half IC=+0.1186, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.084, Q3_mid=+0.059, Q4=+0.037, Q5_high_vol=+0.211

**`first_30min_return`** (Lock IC=-0.0197, Sharpe=-0.4422)
- Admission: Train IC=+0.1189, Deflated=+0.1197, IR=0.45, Mono=0.69, p=0.0188, MaxCorr=0.66
- Yearly ICs: 2017: -0.078 | 2018: +0.052 | 2019: +0.024 | 2020: +0.040 | 2021: +0.159 | 2022: +0.039 | 2023: +0.120 | 2024: +0.048
- IC CV=1.29, Neg years=1/8, Half ratio=5.79, Recency ratio=-6.45
- Early IC=-0.0130, Recent IC=+0.0837, 1st-half IC=+0.0169, 2nd-half IC=+0.0979, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.005, Q2=+0.071, Q3_mid=-0.001, Q4=+0.058, Q5_high_vol=+0.123

### 500ETF — `single` False Positives

**`combo_diff__max_up_ret__impulse_bar_dominance`** (Lock IC=-0.0318, Sharpe=-1.2793)
- Admission: Train IC=+0.1786, Deflated=+0.1768, IR=0.51, Mono=0.70, p=0.0002, MaxCorr=0.60
- Yearly ICs: 2017: -0.040 | 2018: +0.167 | 2019: +0.100 | 2020: +0.090 | 2021: +0.131 | 2022: +0.074 | 2023: +0.042 | 2024: +0.049
- IC CV=0.77, Neg years=1/8, Half ratio=0.95, Recency ratio=0.71
- Early IC=+0.0636, Recent IC=+0.0455, 1st-half IC=+0.0742, 2nd-half IC=+0.0708, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.91, neg years=2)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.062, Q3_mid=+0.009, Q4=+0.097, Q5_high_vol=+0.150

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`volume_weighted_price_position`** (Lock IC=+0.0000, Sharpe=-0.4047)
- Admission: Train IC=+0.1777, Deflated=+0.1783, IR=0.63, Mono=0.75, p=0.0008, MaxCorr=0.60
- Yearly ICs: 2017: +0.013 | 2018: +0.181 | 2019: +0.043 | 2020: -0.059 | 2021: +0.154 | 2022: +0.076 | 2023: +0.195 | 2024: -0.023
- IC CV=1.24, Neg years=2/8, Half ratio=2.38, Recency ratio=0.88
- Early IC=+0.0972, Recent IC=+0.0857, 1st-half IC=+0.0446, 2nd-half IC=+0.1062, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.122, Q3_mid=+0.033, Q4=+0.066, Q5_high_vol=+0.084

### 500ETF — `single` Median Features

**`combo_sig_product__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.0944, Sharpe=-0.6509)
- Admission: Train IC=+0.2134, Deflated=+0.2111, IR=0.55, Mono=0.67, p=0.0000, MaxCorr=0.58
- Yearly ICs: 2017: +0.222 | 2018: +0.023 | 2019: +0.090 | 2020: +0.095 | 2021: +0.070 | 2022: +0.079 | 2023: +0.096 | 2024: +0.156
- IC CV=0.54, Neg years=0/8, Half ratio=1.10, Recency ratio=1.03
- Early IC=+0.1228, Recent IC=+0.1261, 1st-half IC=+0.0984, 2nd-half IC=+0.1078, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.070, Q3_mid=+0.087, Q4=+0.121, Q5_high_vol=+0.082

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0883, Sharpe=-0.5698)
- Admission: Train IC=+0.2689, Deflated=+0.2675, IR=1.07, Mono=0.83, p=0.0000, MaxCorr=0.67
- Yearly ICs: 2017: +0.222 | 2018: +0.178 | 2019: +0.172 | 2020: +0.171 | 2021: +0.141 | 2022: +0.008 | 2023: +0.106 | 2024: +0.163
- IC CV=0.42, Neg years=0/8, Half ratio=0.62, Recency ratio=0.67
- Early IC=+0.2002, Recent IC=+0.1341, 1st-half IC=+0.1783, 2nd-half IC=+0.1107, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.005, Q3_mid=+0.122, Q4=+0.123, Q5_high_vol=+0.235

**`combo_min__net_volume_flow__impulse_bar_dominance`** (Lock IC=+0.0717, Sharpe=-0.8298)
- Admission: Train IC=+0.2687, Deflated=+0.2690, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.59
- Yearly ICs: 2017: +0.194 | 2018: +0.133 | 2019: +0.064 | 2020: +0.111 | 2021: +0.077 | 2022: +0.051 | 2023: +0.088 | 2024: +0.127
- IC CV=0.41, Neg years=0/8, Half ratio=0.77, Recency ratio=0.66
- Early IC=+0.1632, Recent IC=+0.1074, 1st-half IC=+0.1126, 2nd-half IC=+0.0872, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.004, Q3_mid=+0.123, Q4=+0.077, Q5_high_vol=+0.122

**`combo_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0486, Sharpe=-0.6142)
- Admission: Train IC=+0.2200, Deflated=+0.2202, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.68
- Yearly ICs: 2017: +0.145 | 2018: +0.224 | 2019: +0.146 | 2020: +0.088 | 2021: +0.104 | 2022: +0.063 | 2023: +0.062 | 2024: +0.118
- IC CV=0.42, Neg years=0/8, Half ratio=0.60, Recency ratio=0.49
- Early IC=+0.1846, Recent IC=+0.0900, 1st-half IC=+0.1431, 2nd-half IC=+0.0859, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.138, Q2=-0.009, Q3_mid=+0.079, Q4=+0.144, Q5_high_vol=+0.180

**`combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0383, Sharpe=-0.5921)
- Admission: Train IC=+0.2273, Deflated=+0.2272, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.69
- Yearly ICs: 2017: +0.236 | 2018: +0.134 | 2019: +0.080 | 2020: +0.161 | 2021: +0.091 | 2022: +0.106 | 2023: +0.114 | 2024: +0.077
- IC CV=0.40, Neg years=0/8, Half ratio=0.69, Recency ratio=0.52
- Early IC=+0.1853, Recent IC=+0.0957, 1st-half IC=+0.1460, 2nd-half IC=+0.1003, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.010, Q3_mid=+0.176, Q4=+0.086, Q5_high_vol=+0.130

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0289, Sharpe=-0.4555)
- Admission: Train IC=+0.3042, Deflated=+0.3034, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.00
- Yearly ICs: 2017: +0.142 | 2018: +0.284 | 2019: +0.177 | 2020: +0.173 | 2021: +0.171 | 2022: +0.055 | 2023: +0.093 | 2024: +0.161
- IC CV=0.40, Neg years=0/8, Half ratio=0.65, Recency ratio=0.59
- Early IC=+0.2133, Recent IC=+0.1268, 1st-half IC=+0.1870, 2nd-half IC=+0.1223, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.005, Q3_mid=+0.133, Q4=+0.139, Q5_high_vol=+0.259

**`combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=+0.0032, Sharpe=-0.4809)
- Admission: Train IC=+0.1999, Deflated=+0.1991, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.46
- Yearly ICs: 2017: +0.075 | 2018: +0.141 | 2019: +0.166 | 2020: +0.085 | 2021: +0.174 | 2022: +0.043 | 2023: +0.103 | 2024: +0.087
- IC CV=0.40, Neg years=0/8, Half ratio=0.89, Recency ratio=0.88
- Early IC=+0.1079, Recent IC=+0.0950, 1st-half IC=+0.1186, 2nd-half IC=+0.1055, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.053, Q3_mid=+0.088, Q4=+0.128, Q5_high_vol=+0.115

### 159915ETF — `single` Median Features

**`combo_sig_product__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.0887, Sharpe=-0.3901)
- Admission: Train IC=+0.2007, Deflated=+0.1997, IR=0.47, Mono=0.68, p=0.0000, MaxCorr=0.61
- Yearly ICs: 2017: +0.027 | 2018: +0.045 | 2019: +0.181 | 2020: +0.158 | 2021: +0.065 | 2022: +0.072 | 2023: +0.073 | 2024: +0.091
- IC CV=0.56, Neg years=0/8, Half ratio=0.95, Recency ratio=2.28
- Early IC=+0.0360, Recent IC=+0.0819, 1st-half IC=+0.0909, 2nd-half IC=+0.0865, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.075, Q3_mid=+0.088, Q4=+0.041, Q5_high_vol=+0.126

**`trend_bar_close_consistency`** (Lock IC=+0.0806, Sharpe=-0.4274)
- Admission: Train IC=+0.1553, Deflated=+0.1549, IR=0.45, Mono=0.68, p=0.0028, MaxCorr=0.58
- Yearly ICs: 2017: -0.031 | 2018: +0.000 | 2019: +0.074 | 2020: +0.026 | 2021: +0.109 | 2022: +0.058 | 2023: +0.144 | 2024: +0.066
- IC CV=0.95, Neg years=1/8, Half ratio=5.80, Recency ratio=-6.86
- Early IC=-0.0153, Recent IC=+0.1046, 1st-half IC=+0.0168, 2nd-half IC=+0.0973, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.087, Q3_mid=+0.112, Q4=+0.025, Q5_high_vol=+0.014

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1108, Sharpe=+1.2537)
- Admission: Train IC=+0.2116, Deflated=+0.2101, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.67
- Yearly ICs: 2017: +0.190 | 2018: +0.142 | 2019: +0.181 | 2020: +0.142 | 2021: +0.093 | 2022: +0.048 | 2023: +0.069 | 2024: +0.097
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.50
- Early IC=+0.1661, Recent IC=+0.0830, 1st-half IC=+0.1589, 2nd-half IC=+0.0788, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.003, Q3_mid=+0.069, Q4=+0.153, Q5_high_vol=+0.182

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1034, Sharpe=+1.0177)
- Admission: Train IC=+0.1469, Deflated=+0.1469, IR=0.50, Mono=0.67, p=0.0040, MaxCorr=0.11
- Yearly ICs: 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052 | 2022: +0.096 | 2023: +0.046 | 2024: +0.073
- IC CV=0.50, Neg years=0/8, Half ratio=0.50, Recency ratio=0.34
- Early IC=+0.1761, Recent IC=+0.0591, 1st-half IC=+0.1355, 2nd-half IC=+0.0682, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.148, Q2=-0.015, Q3_mid=+0.115, Q4=+0.160, Q5_high_vol=+0.116

**`combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0335, Sharpe=+0.3145)
- Admission: Train IC=+0.1767, Deflated=+0.1756, IR=0.56, Mono=0.71, p=0.0002, MaxCorr=0.58
- Yearly ICs: 2017: +0.038 | 2018: +0.068 | 2019: +0.151 | 2020: +0.080 | 2021: +0.101 | 2022: -0.007 | 2023: +0.011 | 2024: +0.054
- IC CV=0.77, Neg years=1/8, Half ratio=0.59, Recency ratio=0.61
- Early IC=+0.0528, Recent IC=+0.0323, 1st-half IC=+0.0810, 2nd-half IC=+0.0477, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.051, Q2=-0.012, Q3_mid=+0.059, Q4=+0.058, Q5_high_vol=+0.124

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1138, Sharpe=+0.2628)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.42, Mono=0.67, p=0.0002, MaxCorr=0.68
- Yearly ICs: 2017: +0.196 | 2018: +0.105 | 2019: +0.176 | 2020: +0.076 | 2021: +0.087 | 2022: +0.089 | 2023: +0.057 | 2024: +0.164
- IC CV=0.41, Neg years=0/8, Half ratio=0.83, Recency ratio=0.74
- Early IC=+0.1505, Recent IC=+0.1107, 1st-half IC=+0.1298, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.066, Q3_mid=+0.094, Q4=+0.137, Q5_high_vol=+0.151

### 159915ETF — `single` True Positives

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.1239, Sharpe=+1.0994)
- Admission: Train IC=+0.2722, Deflated=+0.2710, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.69
- Yearly ICs: 2017: +0.031 | 2018: +0.151 | 2019: +0.198 | 2020: +0.131 | 2021: +0.179 | 2022: +0.136 | 2023: +0.155 | 2024: +0.077
- IC CV=0.38, Neg years=0/8, Half ratio=1.22, Recency ratio=1.27
- Early IC=+0.0910, Recent IC=+0.1159, 1st-half IC=+0.1201, 2nd-half IC=+0.1467, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.116, Q3_mid=+0.098, Q4=+0.129, Q5_high_vol=+0.187

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1275, Sharpe=+0.8333)
- Admission: Train IC=+0.3801, Deflated=+0.3803, IR=1.24, Mono=0.88, p=0.0000, MaxCorr=0.00
- Yearly ICs: 2017: -0.024 | 2018: +0.157 | 2019: +0.245 | 2020: +0.161 | 2021: +0.143 | 2022: +0.085 | 2023: +0.178 | 2024: +0.127
- IC CV=0.55, Neg years=1/8, Half ratio=1.05, Recency ratio=2.29
- Early IC=+0.0665, Recent IC=+0.1525, 1st-half IC=+0.1341, 2nd-half IC=+0.1411, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.110, Q3_mid=+0.113, Q4=+0.143, Q5_high_vol=+0.196

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0659, Sharpe=+0.7397)
- Admission: Train IC=+0.1602, Deflated=+0.1611, IR=0.50, Mono=0.73, p=0.0022, MaxCorr=0.65
- Yearly ICs: 2017: +0.008 | 2018: +0.135 | 2019: +0.197 | 2020: +0.110 | 2021: +0.134 | 2022: +0.058 | 2023: +0.150 | 2024: +0.061
- IC CV=0.53, Neg years=0/8, Half ratio=0.94, Recency ratio=1.48
- Early IC=+0.0715, Recent IC=+0.1055, 1st-half IC=+0.1115, 2nd-half IC=+0.1046, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.086, Q3_mid=+0.070, Q4=+0.066, Q5_high_vol=+0.157

**`combo_ratio__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1308, Sharpe=+0.7043)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.46, Mono=0.68, p=0.0004, MaxCorr=0.69
- Yearly ICs: 2017: -0.012 | 2018: +0.072 | 2019: +0.170 | 2020: +0.085 | 2021: +0.112 | 2022: +0.141 | 2023: +0.103 | 2024: +0.117
- IC CV=0.52, Neg years=1/8, Half ratio=1.38, Recency ratio=3.68
- Early IC=+0.0299, Recent IC=+0.1100, 1st-half IC=+0.0914, 2nd-half IC=+0.1259, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.131, Q3_mid=+0.066, Q4=+0.120, Q5_high_vol=+0.153

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1428, Sharpe=+0.6972)
- Admission: Train IC=+0.2473, Deflated=+0.2454, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.68
- Yearly ICs: 2017: -0.003 | 2018: +0.098 | 2019: +0.181 | 2020: +0.120 | 2021: +0.143 | 2022: +0.150 | 2023: +0.108 | 2024: +0.090
- IC CV=0.46, Neg years=1/8, Half ratio=1.20, Recency ratio=2.09
- Early IC=+0.0473, Recent IC=+0.0988, 1st-half IC=+0.1106, 2nd-half IC=+0.1328, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.121, Q3_mid=+0.097, Q4=+0.116, Q5_high_vol=+0.189

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1286, Sharpe=+0.5529)
- Admission: Train IC=+0.2467, Deflated=+0.2465, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.44
- Yearly ICs: 2017: -0.047 | 2018: +0.084 | 2019: +0.131 | 2020: +0.102 | 2021: +0.033 | 2022: +0.180 | 2023: +0.115 | 2024: +0.083
- IC CV=0.75, Neg years=1/8, Half ratio=1.22, Recency ratio=5.34
- Early IC=+0.0186, Recent IC=+0.0992, 1st-half IC=+0.0787, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.138, Q3_mid=+0.034, Q4=+0.104, Q5_high_vol=+0.175

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1124, Sharpe=+0.3952)
- Admission: Train IC=+0.1987, Deflated=+0.1960, IR=0.52, Mono=0.69, p=0.0000, MaxCorr=0.59
- Yearly ICs: 2017: -0.033 | 2018: +0.095 | 2019: +0.089 | 2020: +0.078 | 2021: +0.065 | 2022: +0.131 | 2023: +0.154 | 2024: +0.122
- IC CV=0.61, Neg years=1/8, Half ratio=1.60, Recency ratio=4.45
- Early IC=+0.0309, Recent IC=+0.1378, 1st-half IC=+0.0747, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.111, Q3_mid=+0.063, Q4=+0.145, Q5_high_vol=+0.090

**`combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1073, Sharpe=+0.1834)
- Admission: Train IC=+0.1853, Deflated=+0.1840, IR=0.52, Mono=0.68, p=0.0004, MaxCorr=0.64
- Yearly ICs: 2017: +0.033 | 2018: +0.122 | 2019: +0.197 | 2020: +0.149 | 2021: +0.137 | 2022: +0.137 | 2023: +0.160 | 2024: +0.139
- IC CV=0.32, Neg years=0/8, Half ratio=1.11, Recency ratio=1.93
- Early IC=+0.0775, Recent IC=+0.1496, 1st-half IC=+0.1344, 2nd-half IC=+0.1491, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.111, Q3_mid=+0.045, Q4=+0.160, Q5_high_vol=+0.261

**`combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0673, Sharpe=+0.1332)
- Admission: Train IC=+0.2480, Deflated=+0.2489, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.65
- Yearly ICs: 2017: +0.029 | 2018: +0.086 | 2019: +0.185 | 2020: +0.048 | 2021: +0.159 | 2022: +0.052 | 2023: +0.180 | 2024: +0.083
- IC CV=0.57, Neg years=0/8, Half ratio=1.59, Recency ratio=2.30
- Early IC=+0.0572, Recent IC=+0.1314, 1st-half IC=+0.0796, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.092, Q3_mid=+0.134, Q4=+0.093, Q5_high_vol=+0.117

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `volume_weighted_price_position` | Median | fast | +0.1077 | -0.1599 | -0.1599 | 1y |
| `first_30min_return` | FP | fast | +0.0908 | -0.1874 | -0.1874 | 1y |
| `combo_diff__max_up_ret__early_vwap_acceleration` | FP | fast | +0.0218 | -0.0859 | -0.0859 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | FP | fast | +0.0216 | -0.0774 | -0.0774 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=4, gradual=0, persistent=0

**FP decay trajectories:**

- `combo_min__max_up_ret__bar_body_rng_0`: Y1:+0.022 → Y2:-0.077
- `combo_diff__max_up_ret__early_vwap_acceleration`: Y1:+0.022 → Y2:-0.086
- `first_30min_return`: Y1:+0.091 → Y2:-0.187

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__net_volume_flow__impulse_bar_dominance` | Median | fast | +0.1556 | -0.0362 | -0.0362 | 1y |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1483 | +0.0404 | +0.0404 | 1y |
| `combo_min__first_bar_sentiment__bar_ret_0` | Median | fast | +0.1049 | -0.0093 | -0.0093 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | fast | +0.0978 | -0.0539 | -0.0539 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Median | persistent | +0.0944 | +0.0858 | +0.0858 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | Median | persistent | +0.0847 | +0.0862 | +0.0862 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | fast | +0.0601 | -0.0041 | -0.0041 | 1y |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0578 | +0.1809 | +0.1809 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0391 | +0.2313 | +0.2313 | ∞ |
| `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | Median | immediate | -0.0258 | +0.0544 | +0.0544 | ∞ |
| `combo_diff__max_up_ret__impulse_bar_dominance` | FP | immediate | -0.0423 | -0.0040 | -0.0040 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | immediate | -0.0548 | +0.1878 | +0.1878 | ∞ |

**Decay distribution**: immediate=3, fast(1-2y)=4, gradual=0, persistent=5

**FP decay trajectories:**

- `combo_diff__max_up_ret__impulse_bar_dominance`: Y1:-0.042 → Y2:-0.004

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `trend_bar_close_consistency` | Median | fast | +0.2224 | -0.1362 | -0.1362 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | TP | persistent | +0.1839 | +0.0423 | +0.0423 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | TP | fast | +0.1717 | -0.0766 | -0.0766 | 1y |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1608 | +0.1238 | +0.1238 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1594 | +0.0841 | +0.0841 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1291 | +0.1272 | +0.1272 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1247 | +0.1472 | +0.1472 | ∞ |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | Median | persistent | +0.1232 | +0.0322 | +0.0322 | 1y |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.1143 | +0.0098 | +0.0098 | 1y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1014 | +0.1299 | +0.1299 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0791 | +0.1555 | +0.1555 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=2, gradual=0, persistent=9

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 9/20 top rejects are profitable (45%)

- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1721, Lock IC=+0.1466, Sharpe=+0.7732
- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449

**B2 Rolling Guard**: 6/20 top rejects are profitable (30%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0963, Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0963, Sharpe=+0.8491
- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1325, Lock IC=+0.0920, Sharpe=+0.5353

**BH-FDR Gate**: 1/3 top rejects are profitable (33%)

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Sharpe=+0.1297

**B6 Yearly IC CV Gate**: 2/20 top rejects are profitable (10%)

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2286, Lock IC=+0.0813, Sharpe=+0.3659
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2286, Lock IC=+0.0813, Sharpe=+0.3659

**B6 Unstable Component Gate**: 8/20 top rejects are profitable (40%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Sharpe=+0.3783

### 500ETF — `single`

**7-Year Jackknife**: 11/20 top rejects are profitable (55%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Sharpe=+0.5717
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340

**B2 Rolling Guard**: 1/20 top rejects are profitable (5%)

- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2239, Lock IC=+0.0978, Sharpe=+0.0194

**Temporal Validation Gate**: 1/20 top rejects are profitable (5%)

- `combo_clamp_diff__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.2712, Lock IC=+0.0638, Sharpe=+0.3186

**B3 Composite Floor**: 1/20 top rejects are profitable (5%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1881, Lock IC=+0.0017, Sharpe=+0.3201

**B6 Yearly IC CV Gate**: 6/9 top rejects are profitable (67%)

- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1684, Lock IC=+0.0263, Sharpe=+0.6290
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1782, Lock IC=+0.0154, Sharpe=+0.4352
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1782, Lock IC=+0.0154, Sharpe=+0.4352

**B6 Temporal Stability Gate**: 2/20 top rejects are profitable (10%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2741, Lock IC=+0.0880, Sharpe=+0.3545
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2699, Lock IC=+0.0867, Sharpe=+0.2984

**Adaptive Correlation Gate**: 5/8 top rejects are profitable (62%)

- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1888, Lock IC=+0.1502, Sharpe=+1.1714
- `combo_rank_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1775, Lock IC=+0.1253, Sharpe=+0.7571
- `combo_min__opening_drive_thrust_ratio__max_down_ret`: Train IC=+0.1848, Lock IC=+0.0843, Sharpe=+0.1933

### 159915ETF — `single`

**7-Year Jackknife**: 15/20 top rejects are profitable (75%)

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2358, Lock IC=+0.1409, Sharpe=+1.7700
- `combo_rank_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2072, Lock IC=+0.1597, Sharpe=+1.6299
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2218, Lock IC=+0.1126, Sharpe=+1.5724

**B2 Rolling Guard**: 17/20 top rejects are profitable (85%)

- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676
- `combo_z_sum__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676
- `combo_mean__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676

**Temporal Validation Gate**: 15/20 top rejects are profitable (75%)

- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_clamp_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1762, Lock IC=+0.1285, Sharpe=+1.1921

**BH-FDR Gate**: 1/4 top rejects are profitable (25%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0545, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor**: 19/20 top rejects are profitable (95%)

- `combo_tri_min__max_up_ret__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2424, Lock IC=+0.1107, Sharpe=+1.2956
- `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2133, Lock IC=+0.1295, Sharpe=+1.2146
- `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`: Train IC=+0.2460, Lock IC=+0.1133, Sharpe=+0.8865

**B6 Unstable Component Gate**: 12/17 top rejects are profitable (71%)

- `combo_mean__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2248, Lock IC=+0.1308, Sharpe=+1.4985
- `combo_z_sum__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2248, Lock IC=+0.1308, Sharpe=+1.4985
- `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2363, Lock IC=+0.1348, Sharpe=+1.4350

**B6 Temporal Stability Gate**: 1/2 top rejects are profitable (50%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2356, Lock IC=+0.1259, Sharpe=+0.1557

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3282, Lock IC=+0.1307, Sharpe=+1.7816
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3360, Lock IC=+0.1300, Sharpe=+1.5827
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 824 | 78 | 32 | 20 | 26 | 41% | 33% |
| B2 Rolling Guard | 98 | 78 | 37 | 31 | 10 | 47% | 13% |
| Temporal Validation Gate | 103 | 78 | 27 | 41 | 10 | 35% | 13% |
| BH-FDR Gate | 3 | 3 | 0 | 2 | 1 | 0% | 33% |
| B6 Yearly IC CV Gate | 109 | 78 | 49 | 24 | 5 | 63% | 6% |
| B6 Unstable Component Gate | 72 | 72 | 18 | 38 | 16 | 25% | 22% |
| B6 Quality Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B4 Correlation Gate | 70 | 70 | 45 | 25 | 0 | 64% | 0% |

**7-Year Jackknife** — top TP casualties:
- `combo_ratio__limit_down_proximity_early__volume_concentration`: Train IC=+0.1720, Lock IC=+0.1235, Sharpe=+0.9843
- `combo_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Sharpe=+0.8611
- `combo_z_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Sharpe=+0.8611

**BH-FDR Gate** — top TP casualties:
- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Sharpe=+0.1297

**B6 Unstable Component Gate** — top TP casualties:
- `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2034, Lock IC=+0.0592, Sharpe=+0.5373
- `combo_z_sum__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2034, Lock IC=+0.0592, Sharpe=+0.5373
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1781 | 78 | 30 | 26 | 22 | 38% | 28% |
| B2 Rolling Guard | 250 | 78 | 35 | 38 | 5 | 45% | 6% |
| Temporal Validation Gate | 217 | 78 | 21 | 34 | 23 | 27% | 29% |
| BH-FDR Gate | 5 | 5 | 2 | 3 | 0 | 40% | 0% |
| B3 Composite Floor | 54 | 54 | 5 | 28 | 21 | 9% | 39% |
| B6 Yearly IC CV Gate | 9 | 9 | 0 | 3 | 6 | 0% | 67% |
| B6 Temporal Stability Gate | 324 | 78 | 0 | 68 | 10 | 0% | 13% |
| B6 Quality Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B4 Correlation Gate | 561 | 78 | 1 | 65 | 12 | 1% | 15% |
| Adaptive Correlation Gate | 8 | 8 | 1 | 2 | 5 | 12% | 62% |

**7-Year Jackknife** — top TP casualties:
- `roll_spread_proxy_10d`: Train IC=-0.0159, Lock IC=+0.0344, Sharpe=+0.9913
- `combo_min__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=-0.0050, Lock IC=+0.0733, Sharpe=+0.7176
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Sharpe=+0.5717

**Temporal Validation Gate** — top TP casualties:
- `combo_clamp_diff__body_size_progression__max_down_ret`: Train IC=+0.1887, Lock IC=+0.0814, Sharpe=+0.7886
- `combo_sig_product__smooth_momentum_structure__first_bar_return`: Train IC=+0.1187, Lock IC=+0.0775, Sharpe=+0.7142
- `combo_sig_product__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1187, Lock IC=+0.0774, Sharpe=+0.7142

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443
- `combo_tri_z_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443
- `combo_tri_mean__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1684, Lock IC=+0.0263, Sharpe=+0.6290
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1782, Lock IC=+0.0154, Sharpe=+0.4352
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1782, Lock IC=+0.0154, Sharpe=+0.4352

**Adaptive Correlation Gate** — top TP casualties:
- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1888, Lock IC=+0.1502, Sharpe=+1.1714
- `combo_rank_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1775, Lock IC=+0.1253, Sharpe=+0.7571
- `combo_min__opening_drive_thrust_ratio__max_down_ret`: Train IC=+0.1848, Lock IC=+0.0843, Sharpe=+0.1933

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1149 | 78 | 30 | 12 | 36 | 38% | 46% |
| B2 Rolling Guard | 148 | 78 | 18 | 14 | 46 | 23% | 59% |
| Temporal Validation Gate | 47 | 47 | 5 | 10 | 32 | 11% | 68% |
| BH-FDR Gate | 4 | 4 | 0 | 3 | 1 | 0% | 25% |
| B3 Composite Floor | 107 | 78 | 1 | 14 | 63 | 1% | 81% |
| B6 Yearly IC CV Gate | 5 | 5 | 2 | 3 | 0 | 40% | 0% |
| B6 Unstable Component Gate | 17 | 17 | 0 | 5 | 12 | 0% | 71% |
| B6 Temporal Stability Gate | 2 | 2 | 0 | 1 | 1 | 0% | 50% |
| B4 Correlation Gate | 411 | 78 | 0 | 9 | 69 | 0% | 88% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2358, Lock IC=+0.1409, Sharpe=+1.7700
- `combo_rank_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2072, Lock IC=+0.1597, Sharpe=+1.6299
- `yesterday_illiquidity_amihud`: Train IC=+0.0550, Lock IC=+0.1294, Sharpe=+1.6004

**B2 Rolling Guard** — top TP casualties:
- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676
- `combo_z_sum__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676
- `combo_mean__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_clamp_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1762, Lock IC=+0.1285, Sharpe=+1.1921

**BH-FDR Gate** — top TP casualties:
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0545, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor** — top TP casualties:
- `combo_rank_min__first_bar_sentiment__first_bar_return`: Train IC=+0.1172, Lock IC=+0.0759, Sharpe=+1.4912
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.1172, Lock IC=+0.0759, Sharpe=+1.4912
- `combo_tri_min__max_up_ret__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2424, Lock IC=+0.1107, Sharpe=+1.2956

**B6 Unstable Component Gate** — top TP casualties:
- `combo_mean__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2248, Lock IC=+0.1308, Sharpe=+1.4985
- `combo_z_sum__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2248, Lock IC=+0.1308, Sharpe=+1.4985
- `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2363, Lock IC=+0.1348, Sharpe=+1.4350

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2356, Lock IC=+0.1259, Sharpe=+0.1557

**B4 Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3282, Lock IC=+0.1307, Sharpe=+1.7816
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3122, Lock IC=+0.1361, Sharpe=+1.6091
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3360, Lock IC=+0.1300, Sharpe=+1.5827

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (103 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 95 | 50 | 20 | 0 | 30 | 40% | 0% |
| recency_ratio >= 2.5 (late-concentrated) | 8 | 8 | 4 | 0 | 4 | 50% | 0% |

### 500ETF — `single` (217 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 210 | 50 | 0 | 7 | 43 | 0% | 14% |
| recency_ratio >= 2.5 (late-concentrated) | 7 | 7 | 2 | 3 | 2 | 29% | 43% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__high_low_sequence_momentum__impulse_bar_dominance`: Train IC=+0.1313, Lock IC=+0.0670, Sharpe=+0.7377
- `combo_rank_min__rsi_opening__impulse_bar_dominance`: Train IC=+0.1313, Lock IC=+0.0670, Sharpe=+0.7377
- `combo_rank_min__trend_bar_close_consistency__impulse_bar_dominance`: Train IC=+0.1362, Lock IC=+0.0561, Sharpe=+0.3906

### 159915ETF — `single` (47 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 42 | 42 | 5 | 28 | 9 | 12% | 67% |
| recency_ratio >= 2.5 (late-concentrated) | 5 | 5 | 0 | 4 | 1 | 0% | 80% |

**Top TP killed by recency_ratio cap:**
- `vwap_slope_intraday`: Train IC=+0.0934, Lock IC=+0.0337, Sharpe=+0.2590
- `combo_max__max_up_ret__directional_volume_signature`: Train IC=+0.2016, Lock IC=+0.0796, Sharpe=+0.2332
- `combo_min__rbreaker_buy_setup_proximity_early__late_bar_momentum`: Train IC=+0.1182, Lock IC=+0.0724, Sharpe=+0.0058
- `combo_min__limit_down_proximity_early__late_bar_momentum`: Train IC=+0.1181, Lock IC=+0.0724, Sharpe=+0.0058

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | 3 | 1 | 4 | 75% |  |
| `bar_body_rng_0` | 1 | 1 | 2 | 50% |  |
| `volume_weighted_price_position` | 0 | 3 | 3 | 0% |  |
| `star50_limit_proximity_early` | 0 | 6 | 6 | 0% |  |
| `first_bar_return` | 0 | 2 | 2 | 0% |  |
| `bar_ret_0` | 0 | 2 | 2 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 3 | 3 | 0% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 3 | 3 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=1, TP=3, FP rate=25%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=5, FP rate=29%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=2, FP rate=0%

