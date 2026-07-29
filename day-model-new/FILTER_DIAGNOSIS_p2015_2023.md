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
| 300ETF | single | 12 | 1 | 1 | 10 | 8% | 0.64 |
| 500ETF | single | 13 | 1 | 0 | 12 | 8% | 0.87 |
| 159915ETF | single | 10 | 1 | 0 | 9 | 10% | 0.88 |

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

**`combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=-0.0017, Sharpe=-0.6567)
- Admission: Train IC=+0.1107, Deflated=+0.1113, IR=0.47, Mono=0.66, p=0.0288, MaxCorr=0.53
- Yearly ICs: 2015: -0.039 | 2016: +0.011 | 2017: +0.011 | 2018: +0.104 | 2019: +0.066 | 2020: +0.017 | 2021: +0.093 | 2022: +0.021
- IC CV=1.27, Neg years=1/8, Half ratio=2.11, Recency ratio=-4.04
- Early IC=-0.0141, Recent IC=+0.0570, 1st-half IC=+0.0228, 2nd-half IC=+0.0481, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18, neg years=1)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.018, Q3_mid=+0.038, Q4=+0.073, Q5_high_vol=+0.021

### 500ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__close_vs_open_range`** (Lock IC=-0.0211, Sharpe=-0.4893)
- Admission: Train IC=+0.1933, Deflated=+0.1943, IR=0.53, Mono=0.67, p=0.0000, MaxCorr=0.41
- Yearly ICs: 2015: +0.144 | 2016: +0.048 | 2017: +0.100 | 2018: +0.185 | 2019: +0.059 | 2020: +0.099 | 2021: -0.069 | 2022: +0.102
- IC CV=0.85, Neg years=1/8, Half ratio=0.50, Recency ratio=0.17
- Early IC=+0.0963, Recent IC=+0.0165, 1st-half IC=+0.1252, 2nd-half IC=+0.0631, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47, neg years=0)
- Regime ICs: Q1_low_vol=+0.044, Q2=-0.025, Q3_mid=+0.045, Q4=+0.093, Q5_high_vol=+0.240

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0132, Sharpe=-0.5256)
- Admission: Train IC=+0.1499, Deflated=+0.1520, IR=0.47, Mono=0.71, p=0.0022, MaxCorr=0.24
- Yearly ICs: 2015: +0.026 | 2016: +0.053 | 2017: +0.097 | 2018: +0.128 | 2019: -0.015 | 2020: +0.094 | 2021: +0.082 | 2022: -0.005
- IC CV=0.84, Neg years=2/8, Half ratio=0.53, Recency ratio=0.98
- Early IC=+0.0394, Recent IC=+0.0386, 1st-half IC=+0.0765, 2nd-half IC=+0.0405, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.011, Q3_mid=+0.095, Q4=+0.042, Q5_high_vol=+0.091

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0417, Sharpe=-0.0329)
- Admission: Train IC=+0.1858, Deflated=+0.1864, IR=0.66, Mono=0.75, p=0.0002, MaxCorr=0.79
- Yearly ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130 | 2022: +0.096
- IC CV=0.79, Neg years=1/8, Half ratio=1.45, Recency ratio=1.93
- Early IC=+0.0585, Recent IC=+0.1128, 1st-half IC=+0.0554, 2nd-half IC=+0.0802, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.022, Q2=+0.005, Q3_mid=+0.048, Q4=+0.174, Q5_high_vol=+0.099

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0776, Sharpe=+0.8447)
- Admission: Train IC=+0.2226, Deflated=+0.2238, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.78
- Yearly ICs: 2015: +0.168 | 2016: +0.097 | 2017: +0.052 | 2018: +0.199 | 2019: +0.090 | 2020: +0.000 | 2021: +0.126 | 2022: +0.037
- IC CV=0.65, Neg years=0/8, Half ratio=0.49, Recency ratio=0.62
- Early IC=+0.1323, Recent IC=+0.0817, 1st-half IC=+0.1359, 2nd-half IC=+0.0664, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.037, Q3_mid=+0.068, Q4=+0.124, Q5_high_vol=+0.172

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`** (Lock IC=+0.0529, Sharpe=+0.5709)
- Admission: Train IC=+0.1929, Deflated=+0.1930, IR=0.43, Mono=0.67, p=0.0002, MaxCorr=0.52
- Yearly ICs: 2015: +0.129 | 2016: +0.085 | 2017: +0.014 | 2018: +0.127 | 2019: +0.038 | 2020: -0.016 | 2021: +0.121 | 2022: +0.069
- IC CV=0.72, Neg years=1/8, Half ratio=0.59, Recency ratio=0.89
- Early IC=+0.1072, Recent IC=+0.0952, 1st-half IC=+0.0984, 2nd-half IC=+0.0578, Neg regimes=1/5
- Weak component: `bar_vol_0` (CV=1.91)
- Regime ICs: Q1_low_vol=+0.052, Q2=-0.012, Q3_mid=+0.030, Q4=+0.136, Q5_high_vol=+0.133

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0755, Sharpe=+0.5654)
- Admission: Train IC=+0.2800, Deflated=+0.2807, IR=0.74, Mono=0.72, p=0.0000, MaxCorr=0.00
- Yearly ICs: 2015: +0.255 | 2016: +0.096 | 2017: +0.009 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132 | 2022: +0.037
- IC CV=0.70, Neg years=0/8, Half ratio=0.53, Recency ratio=0.48
- Early IC=+0.1754, Recent IC=+0.0845, 1st-half IC=+0.1567, 2nd-half IC=+0.0837, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.034, Q3_mid=+0.069, Q4=+0.186, Q5_high_vol=+0.207

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0701, Sharpe=+0.3915)
- Admission: Train IC=+0.1467, Deflated=+0.1473, IR=0.45, Mono=0.66, p=0.0036, MaxCorr=0.78
- Yearly ICs: 2015: +0.098 | 2016: +0.068 | 2017: +0.035 | 2018: +0.194 | 2019: +0.043 | 2020: +0.043 | 2021: +0.166 | 2022: +0.016
- IC CV=0.73, Neg years=0/8, Half ratio=0.63, Recency ratio=1.10
- Early IC=+0.0829, Recent IC=+0.0913, 1st-half IC=+0.1088, 2nd-half IC=+0.0686, Neg regimes=0/5
- Weak component: `early_vwap_acceleration` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.049, Q3_mid=+0.062, Q4=+0.162, Q5_high_vol=+0.129

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0543, Sharpe=+0.3473)
- Admission: Train IC=+0.2634, Deflated=+0.2636, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.71
- Yearly ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.074 | 2018: +0.167 | 2019: +0.086 | 2020: +0.075 | 2021: +0.151 | 2022: +0.094
- IC CV=0.77, Neg years=1/8, Half ratio=0.75, Recency ratio=0.80
- Early IC=+0.1528, Recent IC=+0.1228, 1st-half IC=+0.1276, 2nd-half IC=+0.0952, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.020, Q2=+0.030, Q3_mid=+0.059, Q4=+0.209, Q5_high_vol=+0.191

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0703, Sharpe=+0.3240)
- Admission: Train IC=+0.2764, Deflated=+0.2775, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.73
- Yearly ICs: 2015: +0.233 | 2016: +0.063 | 2017: -0.069 | 2018: +0.203 | 2019: +0.122 | 2020: +0.057 | 2021: +0.173 | 2022: +0.043
- IC CV=0.90, Neg years=1/8, Half ratio=0.73, Recency ratio=0.73
- Early IC=+0.1479, Recent IC=+0.1075, 1st-half IC=+0.1387, 2nd-half IC=+0.1018, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.016, Q2=+0.030, Q3_mid=+0.061, Q4=+0.251, Q5_high_vol=+0.183

**`combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0566, Sharpe=+0.3084)
- Admission: Train IC=+0.2409, Deflated=+0.2417, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.63
- Yearly ICs: 2015: +0.105 | 2016: +0.085 | 2017: +0.041 | 2018: +0.223 | 2019: +0.065 | 2020: -0.027 | 2021: +0.144 | 2022: +0.066
- IC CV=0.79, Neg years=1/8, Half ratio=0.51, Recency ratio=1.11
- Early IC=+0.0948, Recent IC=+0.1049, 1st-half IC=+0.1270, 2nd-half IC=+0.0651, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.073, Q3_mid=+0.100, Q4=+0.084, Q5_high_vol=+0.150

**`combo_ratio__bar_ret_0__volume_surge_direction`** (Lock IC=+0.0383, Sharpe=+0.0933)
- Admission: Train IC=+0.1657, Deflated=+0.1665, IR=0.48, Mono=0.70, p=0.0010, MaxCorr=0.05
- Yearly ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.143 | 2022: +0.037
- IC CV=0.58, Neg years=1/8, Half ratio=0.54, Recency ratio=0.79
- Early IC=+0.1140, Recent IC=+0.0901, 1st-half IC=+0.1201, 2nd-half IC=+0.0646, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.97)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.064, Q3_mid=+0.087, Q4=+0.099, Q5_high_vol=+0.138

**`combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0539, Sharpe=+0.0387)
- Admission: Train IC=+0.2172, Deflated=+0.2176, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.71
- Yearly ICs: 2015: +0.093 | 2016: +0.030 | 2017: +0.040 | 2018: +0.150 | 2019: +0.045 | 2020: +0.010 | 2021: +0.192 | 2022: +0.045
- IC CV=0.80, Neg years=0/8, Half ratio=0.87, Recency ratio=1.95
- Early IC=+0.0611, Recent IC=+0.1188, 1st-half IC=+0.0887, 2nd-half IC=+0.0769, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.024, Q3_mid=+0.050, Q4=+0.084, Q5_high_vol=+0.158

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0662, Sharpe=+0.0044)
- Admission: Train IC=+0.2243, Deflated=+0.2248, IR=0.57, Mono=0.74, p=0.0000, MaxCorr=0.80
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109
- IC CV=1.02, Neg years=1/8, Half ratio=0.66, Recency ratio=0.75
- Early IC=+0.1357, Recent IC=+0.1021, 1st-half IC=+0.1154, 2nd-half IC=+0.0759, Neg regimes=1/5
- Regime ICs: Q1_low_vol=-0.037, Q2=+0.017, Q3_mid=+0.018, Q4=+0.198, Q5_high_vol=+0.167

### 500ETF — `single` True Positives

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1058, Sharpe=+1.1405)
- Admission: Train IC=+0.2233, Deflated=+0.2239, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.65
- Yearly ICs: 2015: +0.266 | 2016: +0.121 | 2017: +0.105 | 2018: +0.199 | 2019: +0.090 | 2020: +0.107 | 2021: +0.138 | 2022: +0.091
- IC CV=0.42, Neg years=0/8, Half ratio=0.56, Recency ratio=0.59
- Early IC=+0.1937, Recent IC=+0.1144, 1st-half IC=+0.1889, 2nd-half IC=+0.1066, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.034, Q3_mid=+0.109, Q4=+0.170, Q5_high_vol=+0.234

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0976, Sharpe=+0.9250)
- Admission: Train IC=+0.2736, Deflated=+0.2754, IR=0.55, Mono=0.67, p=0.0000, MaxCorr=0.69
- Yearly ICs: 2015: +0.288 | 2016: +0.068 | 2017: +0.194 | 2018: +0.151 | 2019: +0.172 | 2020: +0.117 | 2021: +0.091 | 2022: +0.034
- IC CV=0.54, Neg years=0/8, Half ratio=0.56, Recency ratio=0.35
- Early IC=+0.1782, Recent IC=+0.0625, 1st-half IC=+0.1878, 2nd-half IC=+0.1059, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.031, Q3_mid=+0.123, Q4=+0.181, Q5_high_vol=+0.203

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1217, Sharpe=+0.8196)
- Admission: Train IC=+0.3308, Deflated=+0.3324, IR=1.12, Mono=0.86, p=0.0000, MaxCorr=0.00
- Yearly ICs: 2015: +0.280 | 2016: +0.121 | 2017: +0.223 | 2018: +0.184 | 2019: +0.172 | 2020: +0.173 | 2021: +0.142 | 2022: +0.014
- IC CV=0.44, Neg years=0/8, Half ratio=0.60, Recency ratio=0.39
- Early IC=+0.2006, Recent IC=+0.0784, 1st-half IC=+0.2191, 2nd-half IC=+0.1318, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.051, Q3_mid=+0.164, Q4=+0.217, Q5_high_vol=+0.217

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1175, Sharpe=+0.4851)
- Admission: Train IC=+0.2722, Deflated=+0.2732, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.62
- Yearly ICs: 2015: +0.266 | 2016: +0.178 | 2017: +0.079 | 2018: +0.133 | 2019: +0.078 | 2020: +0.127 | 2021: +0.110 | 2022: +0.120
- IC CV=0.42, Neg years=0/8, Half ratio=0.58, Recency ratio=0.52
- Early IC=+0.2223, Recent IC=+0.1155, 1st-half IC=+0.1862, 2nd-half IC=+0.1084, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.046, Q3_mid=+0.149, Q4=+0.171, Q5_high_vol=+0.220

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1223, Sharpe=+0.4818)
- Admission: Train IC=+0.2008, Deflated=+0.2010, IR=0.36, Mono=0.66, p=0.0000, MaxCorr=0.61
- Yearly ICs: 2015: +0.175 | 2016: +0.063 | 2017: +0.223 | 2018: +0.101 | 2019: +0.174 | 2020: +0.110 | 2021: +0.090 | 2022: +0.106
- IC CV=0.39, Neg years=0/8, Half ratio=0.72, Recency ratio=0.83
- Early IC=+0.1189, Recent IC=+0.0983, 1st-half IC=+0.1602, 2nd-half IC=+0.1161, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.042, Q3_mid=+0.131, Q4=+0.158, Q5_high_vol=+0.167

**`combo_min__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0787, Sharpe=+0.4560)
- Admission: Train IC=+0.2349, Deflated=+0.2363, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.66
- Yearly ICs: 2015: +0.220 | 2016: +0.127 | 2017: +0.141 | 2018: +0.227 | 2019: +0.145 | 2020: +0.087 | 2021: +0.098 | 2022: +0.065
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.47
- Early IC=+0.1736, Recent IC=+0.0817, 1st-half IC=+0.1962, 2nd-half IC=+0.0981, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.152, Q2=-0.003, Q3_mid=+0.124, Q4=+0.160, Q5_high_vol=+0.206

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.1003, Sharpe=+0.4546)
- Admission: Train IC=+0.3105, Deflated=+0.3121, IR=1.17, Mono=0.87, p=0.0000, MaxCorr=0.66
- Yearly ICs: 2015: +0.266 | 2016: +0.079 | 2017: +0.222 | 2018: +0.215 | 2019: +0.114 | 2020: +0.131 | 2021: +0.132 | 2022: +0.092
- IC CV=0.41, Neg years=0/8, Half ratio=0.57, Recency ratio=0.65
- Early IC=+0.1726, Recent IC=+0.1119, 1st-half IC=+0.2127, 2nd-half IC=+0.1218, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.026, Q3_mid=+0.191, Q4=+0.165, Q5_high_vol=+0.227

**`combo_clamp_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0851, Sharpe=+0.4503)
- Admission: Train IC=+0.2919, Deflated=+0.2933, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.68
- Yearly ICs: 2015: +0.313 | 2016: +0.108 | 2017: +0.187 | 2018: +0.215 | 2019: +0.120 | 2020: +0.143 | 2021: +0.150 | 2022: +0.059
- IC CV=0.45, Neg years=0/8, Half ratio=0.54, Recency ratio=0.50
- Early IC=+0.2103, Recent IC=+0.1046, 1st-half IC=+0.2239, 2nd-half IC=+0.1216, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.025, Q3_mid=+0.189, Q4=+0.169, Q5_high_vol=+0.275

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0792, Sharpe=+0.3953)
- Admission: Train IC=+0.1690, Deflated=+0.1706, IR=0.53, Mono=0.72, p=0.0002, MaxCorr=0.63
- Yearly ICs: 2015: +0.206 | 2016: +0.115 | 2017: +0.109 | 2018: +0.281 | 2019: +0.096 | 2020: +0.130 | 2021: +0.101 | 2022: +0.112
- IC CV=0.43, Neg years=0/8, Half ratio=0.52, Recency ratio=0.66
- Early IC=+0.1609, Recent IC=+0.1064, 1st-half IC=+0.2118, 2nd-half IC=+0.1108, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.016, Q3_mid=+0.146, Q4=+0.171, Q5_high_vol=+0.207

**`combo_ratio__bar_ret_0__net_volume_flow`** (Lock IC=+0.0500, Sharpe=+0.3938)
- Admission: Train IC=+0.1425, Deflated=+0.1442, IR=0.33, Mono=0.65, p=0.0062, MaxCorr=0.09
- Yearly ICs: 2015: +0.180 | 2016: +0.055 | 2017: +0.106 | 2018: +0.193 | 2019: +0.120 | 2020: +0.060 | 2021: +0.138 | 2022: +0.020
- IC CV=0.52, Neg years=0/8, Half ratio=0.53, Recency ratio=0.67
- Early IC=+0.1174, Recent IC=+0.0790, 1st-half IC=+0.1435, 2nd-half IC=+0.0766, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.142, Q2=-0.024, Q3_mid=+0.099, Q4=+0.126, Q5_high_vol=+0.142

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0958, Sharpe=+0.2125)
- Admission: Train IC=+0.2448, Deflated=+0.2467, IR=0.71, Mono=0.73, p=0.0000, MaxCorr=0.67
- Yearly ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.233 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.071 | 2022: +0.082
- IC CV=0.61, Neg years=0/8, Half ratio=0.58, Recency ratio=0.47
- Early IC=+0.1625, Recent IC=+0.0765, 1st-half IC=+0.1626, 2nd-half IC=+0.0948, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.028, Q3_mid=+0.131, Q4=+0.158, Q5_high_vol=+0.152

**`combo_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0990, Sharpe=+0.1521)
- Admission: Train IC=+0.1917, Deflated=+0.1925, IR=0.68, Mono=0.71, p=0.0000, MaxCorr=0.66
- Yearly ICs: 2015: +0.230 | 2016: +0.112 | 2017: +0.202 | 2018: +0.197 | 2019: +0.110 | 2020: +0.127 | 2021: +0.063 | 2022: +0.120
- IC CV=0.37, Neg years=0/8, Half ratio=0.51, Recency ratio=0.53
- Early IC=+0.1709, Recent IC=+0.0914, 1st-half IC=+0.2083, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.050, Q3_mid=+0.147, Q4=+0.134, Q5_high_vol=+0.203

### 159915ETF — `single` True Positives

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1260, Sharpe=+1.3254)
- Admission: Train IC=+0.2762, Deflated=+0.2775, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.60
- Yearly ICs: 2015: +0.252 | 2016: +0.132 | 2017: +0.036 | 2018: +0.078 | 2019: +0.206 | 2020: +0.150 | 2021: +0.154 | 2022: +0.131
- IC CV=0.45, Neg years=0/8, Half ratio=1.04, Recency ratio=0.74
- Early IC=+0.1921, Recent IC=+0.1426, 1st-half IC=+0.1570, 2nd-half IC=+0.1629, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.75)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.097, Q3_mid=+0.171, Q4=+0.151, Q5_high_vol=+0.198

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1458, Sharpe=+1.3138)
- Admission: Train IC=+0.3068, Deflated=+0.3083, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.00
- Yearly ICs: 2015: +0.191 | 2016: +0.046 | 2017: +0.008 | 2018: +0.125 | 2019: +0.235 | 2020: +0.126 | 2021: +0.142 | 2022: +0.096
- IC CV=0.56, Neg years=0/8, Half ratio=1.26, Recency ratio=1.00
- Early IC=+0.1186, Recent IC=+0.1187, 1st-half IC=+0.1228, 2nd-half IC=+0.1548, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.105, Q3_mid=+0.162, Q4=+0.149, Q5_high_vol=+0.148

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1277, Sharpe=+1.0889)
- Admission: Train IC=+0.2094, Deflated=+0.2090, IR=0.47, Mono=0.67, p=0.0000, MaxCorr=0.67
- Yearly ICs: 2015: +0.132 | 2016: +0.101 | 2017: +0.040 | 2018: +0.088 | 2019: +0.144 | 2020: +0.062 | 2021: +0.147 | 2022: +0.167
- IC CV=0.38, Neg years=0/8, Half ratio=1.18, Recency ratio=1.34
- Early IC=+0.1168, Recent IC=+0.1569, 1st-half IC=+0.1116, 2nd-half IC=+0.1315, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.001, Q2=+0.089, Q3_mid=+0.096, Q4=+0.220, Q5_high_vol=+0.141

**`volatility_expansion_trend_vector`** (Lock IC=+0.1157, Sharpe=+1.0095)
- Admission: Train IC=+0.1531, Deflated=+0.1550, IR=0.39, Mono=0.67, p=0.0020, MaxCorr=0.69
- Yearly ICs: 2015: +0.127 | 2016: +0.016 | 2017: +0.028 | 2018: +0.009 | 2019: +0.101 | 2020: +0.047 | 2021: +0.138 | 2022: +0.089
- IC CV=0.69, Neg years=0/8, Half ratio=1.44, Recency ratio=1.58
- Early IC=+0.0718, Recent IC=+0.1138, 1st-half IC=+0.0678, 2nd-half IC=+0.0978, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.041, Q3_mid=+0.126, Q4=+0.062, Q5_high_vol=+0.091

**`combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0958, Sharpe=+0.8819)
- Admission: Train IC=+0.1863, Deflated=+0.1875, IR=0.44, Mono=0.66, p=0.0002, MaxCorr=0.68
- Yearly ICs: 2015: +0.209 | 2016: +0.166 | 2017: -0.009 | 2018: +0.130 | 2019: +0.187 | 2020: +0.127 | 2021: +0.143 | 2022: +0.053
- IC CV=0.53, Neg years=1/8, Half ratio=0.83, Recency ratio=0.52
- Early IC=+0.1879, Recent IC=+0.0982, 1st-half IC=+0.1523, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.75)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.043, Q3_mid=+0.108, Q4=+0.094, Q5_high_vol=+0.257

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1302, Sharpe=+0.6763)
- Admission: Train IC=+0.2140, Deflated=+0.2149, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.46
- Yearly ICs: 2015: +0.184 | 2016: +0.102 | 2017: -0.035 | 2018: +0.096 | 2019: +0.089 | 2020: +0.078 | 2021: +0.064 | 2022: +0.131
- IC CV=0.66, Neg years=1/8, Half ratio=0.77, Recency ratio=0.68
- Early IC=+0.1432, Recent IC=+0.0978, 1st-half IC=+0.1258, 2nd-half IC=+0.0965, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.095, Q3_mid=+0.138, Q4=+0.171, Q5_high_vol=+0.060

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.1169, Sharpe=+0.6278)
- Admission: Train IC=+0.1886, Deflated=+0.1898, IR=0.42, Mono=0.69, p=0.0002, MaxCorr=0.67
- Yearly ICs: 2015: +0.194 | 2016: +0.089 | 2017: +0.026 | 2018: +0.081 | 2019: +0.195 | 2020: +0.106 | 2021: +0.095 | 2022: +0.098
- IC CV=0.49, Neg years=0/8, Half ratio=1.04, Recency ratio=0.68
- Early IC=+0.1412, Recent IC=+0.0966, 1st-half IC=+0.1188, 2nd-half IC=+0.1234, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.82)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.066, Q3_mid=+0.119, Q4=+0.094, Q5_high_vol=+0.187

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1090, Sharpe=+0.3724)
- Admission: Train IC=+0.1551, Deflated=+0.1554, IR=0.48, Mono=0.70, p=0.0018, MaxCorr=0.10
- Yearly ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087 | 2022: +0.139
- IC CV=0.66, Neg years=0/8, Half ratio=1.03, Recency ratio=1.15
- Early IC=+0.0981, Recent IC=+0.1130, 1st-half IC=+0.1055, 2nd-half IC=+0.1088, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.038, Q3_mid=+0.091, Q4=+0.189, Q5_high_vol=+0.098

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1075, Sharpe=+0.3554)
- Admission: Train IC=+0.2737, Deflated=+0.2745, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.58
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.080 | 2019: +0.132 | 2020: +0.100 | 2021: +0.035 | 2022: +0.178
- IC CV=0.82, Neg years=1/8, Half ratio=1.22, Recency ratio=0.96
- Early IC=+0.1110, Recent IC=+0.1065, 1st-half IC=+0.0978, 2nd-half IC=+0.1188, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.076, Q3_mid=+0.124, Q4=+0.143, Q5_high_vol=+0.137

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | TP | gradual | +0.1959 | +0.0373 | -0.2073 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1763 | +0.0543 | -0.0356 | 1y |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | TP | gradual | +0.1763 | +0.0147 | -0.1012 | 1y |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | TP | gradual | +0.1608 | +0.1147 | -0.0782 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | gradual | +0.1508 | +0.0609 | -0.0216 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.1394 | +0.0494 | -0.0180 | 1y |
| `combo_ratio__bar_ret_0__volume_surge_direction` | TP | gradual | +0.1143 | +0.0230 | -0.0934 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0912 | +0.0267 | +0.0014 | 1y |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | FP | fast | +0.0649 | -0.0256 | -0.1745 | 1y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0576 | +0.0214 | +0.1515 | 1y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | TP | fast | +0.0550 | -0.0050 | +0.1389 | 1y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Median | fast | +0.0234 | -0.0520 | +0.1970 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=3, gradual=7, persistent=2

**FP decay trajectories:**

- `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`: Y1:+0.065 → Y2:-0.026 → Y3:+0.040 → Y4:-0.175

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1561 | +0.1336 | +0.0302 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.1071 | +0.1459 | -0.0338 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1059 | +0.1666 | +0.0842 | ∞ |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0915 | +0.1184 | +0.1051 | 2y |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0781 | +0.1444 | +0.1943 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0766 | +0.0799 | +0.0886 | ∞ |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0715 | +0.1035 | +0.1197 | ∞ |
| `combo_min__first_bar_sentiment__first_bar_return` | TP | gradual | +0.0698 | +0.1230 | -0.0173 | 3y |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0630 | +0.1130 | +0.0822 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0514 | +0.1238 | +0.0782 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | TP | persistent | +0.0501 | +0.0982 | +0.0041 | 3y |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | FP | gradual | +0.0157 | +0.0088 | -0.0217 | 2y |
| `combo_ratio__bar_ret_0__net_volume_flow` | TP | gradual | +0.0078 | +0.0609 | -0.0032 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=4, persistent=9

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__close_vs_open_range`: Y1:+0.016 → Y2:+0.009 → Y3:-0.094 → Y4:-0.022

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1829 | +0.1255 | +0.0725 | 3y |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.1754 | +0.0818 | +0.0863 | 1y |
| `volatility_expansion_trend_vector` | TP | gradual | +0.1663 | +0.0804 | -0.0952 | 1y |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1537 | +0.1217 | +0.1543 | ∞ |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1471 | +0.0787 | +0.0305 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1469 | +0.0883 | +0.0544 | 3y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1366 | +0.1389 | +0.0904 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1157 | +0.0779 | +0.1278 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0826 | +0.0831 | +0.1479 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | fast | +0.0544 | -0.0517 | -0.0008 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=1, gradual=1, persistent=8

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:+0.054 → Y2:-0.052 → Y3:-0.026 → Y4:-0.001

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 13/20 top rejects are profitable (65%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_diff__bar_ret_0__demark_setup_reversal_early`: Train IC=+0.2145, Lock IC=+0.0671, Sharpe=+0.4632
- `combo_z_diff__bar_ret_0__demark_setup_reversal_early`: Train IC=+0.2145, Lock IC=+0.0671, Sharpe=+0.4632
- `combo_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2142, Lock IC=+0.0670, Sharpe=+0.4632

**Temporal Validation Gate**: 9/20 top rejects are profitable (45%)

- `combo_max__volume_weighted_momentum_acceleration__demark_setup_reversal_early`: Train IC=+0.2099, Lock IC=+0.0829, Sharpe=+0.4258
- `combo_clamp_diff__volume_weighted_momentum_acceleration__max_up_ret`: Train IC=+0.1901, Lock IC=+0.0622, Sharpe=+0.3586
- `combo_diff__smooth_momentum_structure__max_up_ret`: Train IC=+0.1987, Lock IC=+0.0635, Sharpe=+0.2865

**B3 Composite Floor**: 18/20 top rejects are profitable (90%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2104, Lock IC=+0.0769, Sharpe=+0.8833
- `combo_tri_min__first_bar_return__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1633, Lock IC=+0.0550, Sharpe=+0.6654
- `combo_tri_min__bar_ret_0__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1629, Lock IC=+0.0550, Sharpe=+0.6654

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2593, Lock IC=+0.0877, Sharpe=+1.0876
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2691, Lock IC=+0.0706, Sharpe=+0.8555
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Sharpe=+0.5292

**Adaptive Correlation Gate**: 6/13 top rejects are profitable (46%)

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1818, Lock IC=+0.0875, Sharpe=+1.1020
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1824, Lock IC=+0.0655, Sharpe=+0.4621
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1780, Lock IC=+0.0525, Sharpe=+0.4588

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.2819, Lock IC=+0.1134, Sharpe=+0.8586

**B2 Rolling Guard**: 13/20 top rejects are profitable (65%)

- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Sharpe=+0.5808
- `combo_tri_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1954, Lock IC=+0.0826, Sharpe=+0.4663
- `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Sharpe=+0.3984

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824

**B6 Yearly IC CV Gate**: 9/13 top rejects are profitable (69%)

- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2140, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2140, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2190, Lock IC=+0.0434, Sharpe=+0.9681

**B6 Unstable Component Gate**: 15/20 top rejects are profitable (75%)

- `combo_min__bar_ret_0__impulse_bar_dominance`: Train IC=+0.2256, Lock IC=+0.0927, Sharpe=+0.5215
- `combo_min__first_bar_return__impulse_bar_dominance`: Train IC=+0.2226, Lock IC=+0.0927, Sharpe=+0.5215
- `combo_diff__max_up_ret__impulse_bar_dominance`: Train IC=+0.2440, Lock IC=+0.0103, Sharpe=+0.4555

**B6 Temporal Stability Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2881, Lock IC=+0.1110, Sharpe=+1.1024
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Sharpe=+0.9985

**Adaptive Correlation Gate**: 4/5 top rejects are profitable (80%)

- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2231, Lock IC=+0.0936, Sharpe=+0.7388
- `combo_max__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2150, Lock IC=+0.0840, Sharpe=+0.6202
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`: Train IC=+0.2722, Lock IC=+0.1066, Sharpe=+0.5017

### 159915ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Sharpe=+1.8587
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2421, Lock IC=+0.0980, Sharpe=+1.7078

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Sharpe=+1.3582
- `combo_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2299, Lock IC=+0.1187, Sharpe=+1.1602
- `combo_z_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2299, Lock IC=+0.1187, Sharpe=+1.1602

**Temporal Validation Gate**: 19/20 top rejects are profitable (95%)

- `combo_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_z_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3073, Lock IC=+0.1158, Sharpe=+1.5577
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Sharpe=+1.4133
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2393, Lock IC=+0.1373, Sharpe=+1.3304

**B6 Yearly IC CV Gate**: 8/8 top rejects are profitable (100%)

- `combo_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2326, Lock IC=+0.1309, Sharpe=+1.4421
- `combo_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2326, Lock IC=+0.1309, Sharpe=+1.4421
- `combo_z_sum__yesterday_first_30min_return__limit_down_proximity_early`: Train IC=+0.2233, Lock IC=+0.1158, Sharpe=+0.5062

**B6 Unstable Component Gate**: 20/20 top rejects are profitable (100%)

- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Sharpe=+1.6742
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2819, Lock IC=+0.1269, Sharpe=+1.6324

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1205 | 78 | 21 | 35 | 22 | 27% | 28% |
| B2 Rolling Guard | 204 | 78 | 20 | 14 | 44 | 26% | 56% |
| Temporal Validation Gate | 74 | 74 | 2 | 32 | 40 | 3% | 54% |
| BH-FDR Gate | 5 | 5 | 0 | 5 | 0 | 0% | 0% |
| B3 Composite Floor | 35 | 35 | 1 | 7 | 27 | 3% | 77% |
| B6 Yearly IC CV Gate | 1 | 1 | 0 | 1 | 0 | 0% | 0% |
| B4 Correlation Gate | 205 | 78 | 0 | 17 | 61 | 0% | 78% |
| Adaptive Correlation Gate | 13 | 13 | 0 | 7 | 6 | 0% | 46% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard** — top TP casualties:
- `combo_clamp_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1349, Lock IC=+0.0570, Sharpe=+1.0307
- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Sharpe=+0.7446
- `combo_tri_min__bar_ret_0__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.1360, Lock IC=+0.0557, Sharpe=+0.6991

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_z_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1469, Lock IC=+0.0614, Sharpe=+0.8233

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2104, Lock IC=+0.0769, Sharpe=+0.8833
- `combo_tri_min__first_bar_return__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1633, Lock IC=+0.0550, Sharpe=+0.6654
- `combo_tri_min__bar_ret_0__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1629, Lock IC=+0.0550, Sharpe=+0.6654

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2593, Lock IC=+0.0877, Sharpe=+1.0876
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2691, Lock IC=+0.0706, Sharpe=+0.8555
- `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.1955, Lock IC=+0.0678, Sharpe=+0.6776

**Adaptive Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1818, Lock IC=+0.0875, Sharpe=+1.1020
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1824, Lock IC=+0.0655, Sharpe=+0.4621
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1780, Lock IC=+0.0525, Sharpe=+0.4588

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1823 | 78 | 27 | 26 | 25 | 35% | 32% |
| B2 Rolling Guard | 242 | 78 | 19 | 23 | 36 | 24% | 46% |
| Temporal Validation Gate | 117 | 78 | 16 | 6 | 56 | 21% | 72% |
| BH-FDR Gate | 7 | 7 | 1 | 6 | 0 | 14% | 0% |
| B3 Composite Floor | 156 | 78 | 1 | 6 | 71 | 1% | 91% |
| B6 Yearly IC CV Gate | 13 | 13 | 0 | 4 | 9 | 0% | 69% |
| B6 Unstable Component Gate | 66 | 66 | 0 | 15 | 51 | 0% | 77% |
| B6 Temporal Stability Gate | 151 | 78 | 0 | 16 | 62 | 0% | 79% |
| B4 Correlation Gate | 629 | 78 | 0 | 12 | 66 | 0% | 85% |
| Adaptive Correlation Gate | 5 | 5 | 0 | 1 | 4 | 0% | 80% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2305, Lock IC=+0.1016, Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0336, Lock IC=+0.0707, Sharpe=+0.8914
- `combo_rel_diff__body_size_progression__first_bar_return`: Train IC=+0.1891, Lock IC=+0.0693, Sharpe=+0.5882
- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Sharpe=+0.5808

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression`: Train IC=+0.1094, Lock IC=+0.0362, Sharpe=+1.0604
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__body_size_progression`: Train IC=+0.1094, Lock IC=+0.0362, Sharpe=+1.0604
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1987, Lock IC=+0.0381, Sharpe=+1.0422

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2140, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2140, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2190, Lock IC=+0.0434, Sharpe=+0.9681

**B6 Unstable Component Gate** — top TP casualties:
- `combo_max__volatility_expansion_trend_vector__impulse_bar_dominance`: Train IC=+0.2003, Lock IC=+0.0798, Sharpe=+0.5553
- `combo_mean__max_up_ret__impulse_bar_dominance`: Train IC=+0.2080, Lock IC=+0.0842, Sharpe=+0.5393
- `combo_z_sum__max_up_ret__impulse_bar_dominance`: Train IC=+0.2080, Lock IC=+0.0842, Sharpe=+0.5393

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2881, Lock IC=+0.1110, Sharpe=+1.1024
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888

**B4 Correlation Gate** — top TP casualties:
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Sharpe=+0.9985

**Adaptive Correlation Gate** — top TP casualties:
- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2231, Lock IC=+0.0936, Sharpe=+0.7388
- `combo_max__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2150, Lock IC=+0.0840, Sharpe=+0.6202
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`: Train IC=+0.2722, Lock IC=+0.1066, Sharpe=+0.5017

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1181 | 78 | 23 | 17 | 38 | 29% | 49% |
| B2 Rolling Guard | 312 | 78 | 19 | 5 | 54 | 24% | 69% |
| Temporal Validation Gate | 29 | 29 | 5 | 0 | 24 | 17% | 83% |
| BH-FDR Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 148 | 78 | 0 | 1 | 77 | 0% | 99% |
| B6 Yearly IC CV Gate | 8 | 8 | 0 | 0 | 8 | 0% | 100% |
| B6 Unstable Component Gate | 39 | 39 | 0 | 0 | 39 | 0% | 100% |
| B4 Correlation Gate | 172 | 78 | 0 | 0 | 78 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Sharpe=+1.8587
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2421, Lock IC=+0.0980, Sharpe=+1.7078

**B2 Rolling Guard** — top TP casualties:
- `combo_mean__max_up_ret__directional_volume_signature`: Train IC=+0.1547, Lock IC=+0.1106, Sharpe=+1.5561
- `combo_z_sum__max_up_ret__directional_volume_signature`: Train IC=+0.1547, Lock IC=+0.1106, Sharpe=+1.5561
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Sharpe=+1.3582

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_z_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3073, Lock IC=+0.1158, Sharpe=+1.5577
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2324, Lock IC=+0.1197, Sharpe=+1.5206
- `combo_mean__first_bar_return__limit_down_proximity_early`: Train IC=+0.2026, Lock IC=+0.1193, Sharpe=+1.4931

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2326, Lock IC=+0.1309, Sharpe=+1.4421
- `combo_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2326, Lock IC=+0.1309, Sharpe=+1.4421
- `combo_z_sum__yesterday_first_30min_return__limit_down_proximity_early`: Train IC=+0.2233, Lock IC=+0.1158, Sharpe=+0.5062

**B6 Unstable Component Gate** — top TP casualties:
- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Sharpe=+1.6742
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2819, Lock IC=+0.1269, Sharpe=+1.6324

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (74 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 74 | 50 | 2 | 32 | 16 | 4% | 64% |

### 500ETF — `single` (117 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 114 | 50 | 0 | 48 | 2 | 0% | 96% |
| recency_ratio >= 2.5 (late-concentrated) | 3 | 3 | 0 | 2 | 1 | 0% | 67% |

**Top TP killed by recency_ratio cap:**
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Train IC=+0.1291, Lock IC=+0.0798, Sharpe=+0.4226
- `combo_sig_product__trend_day_regime_conviction__max_down_ret`: Train IC=+0.1323, Lock IC=+0.0715, Sharpe=+0.1181

### 159915ETF — `single` (29 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 29 | 29 | 5 | 24 | 0 | 17% | 83% |

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volatility_expansion_trend_vector` | 1 | 1 | 2 | 50% |  |
| `close_vs_open_range` | 1 | 1 | 2 | 50% |  |
| `volume_weighted_price_position` | 1 | 2 | 3 | 33% |  |
| `max_up_ret` | 2 | 14 | 16 | 12% |  |
| `bar_body_rng_0` | 0 | 4 | 4 | 0% |  |
| `first_bar_return` | 0 | 3 | 3 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 8 | 8 | 0% |  |
| `star50_limit_proximity_early` | 0 | 8 | 8 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 4 | 4 | 0% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |
| `net_volume_flow` | 0 | 2 | 2 | 0% |  |
| `first_bar_sentiment` | 0 | 4 | 4 | 0% |  |
| `bar_ret_0` | 0 | 6 | 6 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=1, TP=9, FP rate=10%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=5, FP rate=29%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=8, FP rate=0%

