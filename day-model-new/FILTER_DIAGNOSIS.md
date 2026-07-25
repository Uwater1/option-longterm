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
| 300ETF | single | 7 | 0 | 3 | 4 | 0% | 0.59 |
| 500ETF | single | 30 | 0 | 13 | 17 | 0% | 0.68 |
| 159915ETF | single | 11 | 0 | 3 | 8 | 0% | 0.83 |

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

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0616, Sharpe=-0.0803)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095
- IC CV=1.14, Neg years=1/7, Half ratio=0.62, Recency ratio=0.50
- Regime ICs: Q1_low_vol=-0.067, Q2=+0.000, Q3_mid=+0.053, Q4=+0.178, Q5_high_vol=+0.171

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.0360, Sharpe=-0.4739)
- Yearly ICs: 2015: +0.203 | 2016: +0.065 | 2017: -0.107 | 2018: +0.155 | 2019: +0.083 | 2020: +0.024 | 2021: +0.114
- IC CV=1.21, Neg years=1/7, Half ratio=0.79, Recency ratio=0.51
- Weak component: `demark_setup_reversal_early` (CV=1.42)
- Regime ICs: Q1_low_vol=-0.081, Q2=-0.015, Q3_mid=+0.094, Q4=+0.170, Q5_high_vol=+0.175

**`combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0225, Sharpe=-0.7417)
- Yearly ICs: 2015: +0.095 | 2016: +0.111 | 2017: +0.068 | 2018: +0.201 | 2019: +0.089 | 2020: +0.013 | 2021: +0.146
- IC CV=0.53, Neg years=0/7, Half ratio=1.13, Recency ratio=0.77
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.058, Q3_mid=+0.120, Q4=+0.128, Q5_high_vol=+0.162

### 500ETF — `single` Median Features

**`combo_ratio__max_down_ret__net_volume_flow`** (Lock IC=+0.1213, Sharpe=-0.3337)
- Yearly ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004
- IC CV=0.47, Neg years=0/7, Half ratio=0.64, Recency ratio=0.42
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.001, Q3_mid=+0.137, Q4=+0.092, Q5_high_vol=+0.174

**`combo_rank_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.1039, Sharpe=-0.0814)
- Yearly ICs: 2015: +0.210 | 2016: +0.082 | 2017: +0.181 | 2018: +0.172 | 2019: +0.115 | 2020: +0.062 | 2021: +0.055
- IC CV=0.46, Neg years=0/7, Half ratio=0.63, Recency ratio=0.40
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.030, Q3_mid=+0.122, Q4=+0.142, Q5_high_vol=+0.185

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0949, Sharpe=-0.0501)
- Yearly ICs: 2015: +0.263 | 2016: +0.080 | 2017: +0.216 | 2018: +0.198 | 2019: +0.144 | 2020: +0.159 | 2021: +0.107
- IC CV=0.35, Neg years=0/7, Half ratio=0.75, Recency ratio=0.78
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.045, Q3_mid=+0.181, Q4=+0.173, Q5_high_vol=+0.258

**`combo_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0941, Sharpe=-0.2540)
- Yearly ICs: 2015: +0.284 | 2016: +0.072 | 2017: +0.251 | 2018: +0.192 | 2019: +0.132 | 2020: +0.161 | 2021: +0.095
- IC CV=0.43, Neg years=0/7, Half ratio=0.86, Recency ratio=0.72
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.235, Q2=+0.021, Q3_mid=+0.147, Q4=+0.125, Q5_high_vol=+0.278

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0935, Sharpe=-0.0443)
- Yearly ICs: 2015: +0.232 | 2016: +0.107 | 2017: +0.188 | 2018: +0.199 | 2019: +0.083 | 2020: +0.160 | 2021: +0.074
- IC CV=0.38, Neg years=0/7, Half ratio=0.60, Recency ratio=0.69
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.026, Q3_mid=+0.161, Q4=+0.189, Q5_high_vol=+0.246

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`** (Lock IC=+0.0843, Sharpe=-0.9623)
- Yearly ICs: 2015: +0.247 | 2016: +0.115 | 2017: +0.227 | 2018: +0.194 | 2019: +0.094 | 2020: +0.144 | 2021: +0.122
- IC CV=0.34, Neg years=0/7, Half ratio=0.70, Recency ratio=0.73
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.065, Q3_mid=+0.181, Q4=+0.172, Q5_high_vol=+0.269

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0799, Sharpe=-0.4294)
- Yearly ICs: 2015: +0.245 | 2016: +0.037 | 2017: +0.155 | 2018: +0.203 | 2019: +0.171 | 2020: +0.189 | 2021: +0.151
- IC CV=0.37, Neg years=0/7, Half ratio=1.25, Recency ratio=1.21
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.114, Q3_mid=+0.151, Q4=+0.126, Q5_high_vol=+0.288

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0778, Sharpe=-0.2086)
- Yearly ICs: 2015: +0.307 | 2016: +0.108 | 2017: +0.187 | 2018: +0.214 | 2019: +0.121 | 2020: +0.142 | 2021: +0.152
- IC CV=0.36, Neg years=0/7, Half ratio=0.80, Recency ratio=0.71
- Weak component: `early_late_momentum_divergence` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.096, Q3_mid=+0.195, Q4=+0.141, Q5_high_vol=+0.317

**`max_up_ret`** (Lock IC=+0.0778, Sharpe=-0.2120)
- Yearly ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139
- IC CV=0.30, Neg years=0/7, Half ratio=0.73, Recency ratio=0.78
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.070, Q3_mid=+0.189, Q4=+0.169, Q5_high_vol=+0.274

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0773, Sharpe=-0.4393)
- Yearly ICs: 2015: +0.296 | 2016: +0.104 | 2017: +0.192 | 2018: +0.209 | 2019: +0.154 | 2020: +0.167 | 2021: +0.138
- IC CV=0.32, Neg years=0/7, Half ratio=0.89, Recency ratio=0.76
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.095, Q3_mid=+0.178, Q4=+0.154, Q5_high_vol=+0.321

**`combo_rank_max__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0743, Sharpe=-0.6333)
- Yearly ICs: 2015: +0.239 | 2016: +0.040 | 2017: +0.077 | 2018: +0.171 | 2019: +0.125 | 2020: +0.078 | 2021: +0.100
- IC CV=0.52, Neg years=0/7, Half ratio=1.01, Recency ratio=0.64
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.119, Q2=-0.007, Q3_mid=+0.141, Q4=+0.106, Q5_high_vol=+0.186

**`combo_rank_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0711, Sharpe=-0.0107)
- Yearly ICs: 2015: +0.226 | 2016: +0.111 | 2017: +0.152 | 2018: +0.216 | 2019: +0.068 | 2020: +0.134 | 2021: +0.060
- IC CV=0.44, Neg years=0/7, Half ratio=0.65, Recency ratio=0.58
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.010, Q3_mid=+0.173, Q4=+0.167, Q5_high_vol=+0.265

**`combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0685, Sharpe=-0.7765)
- Yearly ICs: 2015: +0.210 | 2016: +0.049 | 2017: +0.164 | 2018: +0.182 | 2019: +0.150 | 2020: +0.194 | 2021: +0.148
- IC CV=0.31, Neg years=0/7, Half ratio=1.42, Recency ratio=1.32
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.092, Q3_mid=+0.144, Q4=+0.092, Q5_high_vol=+0.272

### 159915ETF — `single` Median Features

**`combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`** (Lock IC=+0.1269, Sharpe=-0.1788)
- Yearly ICs: 2015: +0.247 | 2016: +0.117 | 2017: +0.034 | 2018: +0.080 | 2019: +0.244 | 2020: +0.132 | 2021: +0.128
- IC CV=0.53, Neg years=0/7, Half ratio=1.24, Recency ratio=0.71
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.091, Q3_mid=+0.183, Q4=+0.144, Q5_high_vol=+0.220

**`combo_sig_product__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0910, Sharpe=-1.0618)
- Yearly ICs: 2015: +0.209 | 2016: +0.092 | 2017: +0.067 | 2018: +0.095 | 2019: +0.094 | 2020: +0.091 | 2021: +0.127
- IC CV=0.39, Neg years=0/7, Half ratio=0.86, Recency ratio=0.72
- Weak component: `impulse_bar_dominance` (CV=1.19)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.096, Q3_mid=+0.126, Q4=+0.128, Q5_high_vol=+0.188

**`combo_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0802, Sharpe=-0.3755)
- Yearly ICs: 2015: +0.179 | 2016: +0.073 | 2017: +0.042 | 2018: +0.065 | 2019: +0.114 | 2020: +0.116 | 2021: +0.149
- IC CV=0.43, Neg years=0/7, Half ratio=1.31, Recency ratio=1.05
- Weak component: `volume_weighted_price_position` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.079, Q3_mid=+0.145, Q4=+0.152, Q5_high_vol=+0.150

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0342, Sharpe=+0.8997)
- Yearly ICs: 2015: +0.266 | 2016: +0.117 | 2017: -0.053 | 2018: +0.140 | 2019: +0.100 | 2020: +0.074 | 2021: +0.143
- IC CV=0.78, Neg years=1/7, Half ratio=0.77, Recency ratio=0.57
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0263, Sharpe=+0.3498)
- Yearly ICs: 2015: +0.225 | 2016: +0.091 | 2017: -0.022 | 2018: +0.157 | 2019: +0.122 | 2020: +0.042 | 2021: +0.132
- IC CV=0.69, Neg years=1/7, Half ratio=0.88, Recency ratio=0.55
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0016, Sharpe=+0.2719)
- Yearly ICs: 2015: +0.223 | 2016: -0.064 | 2017: +0.071 | 2018: -0.050 | 2019: -0.011 | 2020: +0.022 | 2021: -0.071
- IC CV=5.62, Neg years=4/7, Half ratio=-0.29, Recency ratio=-0.31
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0706, Sharpe=+0.1258)
- Yearly ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130
- IC CV=0.88, Neg years=1/7, Half ratio=1.82, Recency ratio=1.12
- Weak component: `limit_down_proximity_early` (CV=1.62)

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1183, Sharpe=+1.2421)
- Yearly ICs: 2015: +0.294 | 2016: +0.022 | 2017: +0.204 | 2018: +0.144 | 2019: +0.184 | 2020: +0.146 | 2021: +0.091
- IC CV=0.51, Neg years=0/7, Half ratio=0.88, Recency ratio=0.75
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1083, Sharpe=+1.1127)
- Yearly ICs: 2015: +0.289 | 2016: +0.074 | 2017: +0.196 | 2018: +0.155 | 2019: +0.174 | 2020: +0.112 | 2021: +0.096
- IC CV=0.43, Neg years=0/7, Half ratio=0.71, Recency ratio=0.57
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1015, Sharpe=+0.8294)
- Yearly ICs: 2015: +0.313 | 2016: +0.094 | 2017: +0.215 | 2018: +0.203 | 2019: +0.178 | 2020: +0.143 | 2021: +0.098
- IC CV=0.40, Neg years=0/7, Half ratio=0.70, Recency ratio=0.59
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1256, Sharpe=+0.7571)
- Yearly ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.194 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148
- IC CV=0.42, Neg years=0/7, Half ratio=1.09, Recency ratio=1.10
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1100, Sharpe=+0.5717)
- Yearly ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052
- IC CV=0.52, Neg years=0/7, Half ratio=0.67, Recency ratio=0.56
- Weak component: `max_down_ret` (CV=0.55)

**`combo_rel_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0020, Sharpe=+0.4829)
- Yearly ICs: 2015: +0.149 | 2016: +0.138 | 2017: -0.011 | 2018: +0.082 | 2019: +0.070 | 2020: +0.030 | 2021: +0.081
- IC CV=0.68, Neg years=1/7, Half ratio=0.62, Recency ratio=0.39
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_sig_product__max_up_ret__body_size_progression`** (Lock IC=+0.1120, Sharpe=+0.3972)
- Yearly ICs: 2015: +0.248 | 2016: +0.157 | 2017: +0.091 | 2018: +0.142 | 2019: +0.095 | 2020: +0.137 | 2021: +0.104
- IC CV=0.36, Neg years=0/7, Half ratio=0.66, Recency ratio=0.59
- Weak component: `body_size_progression` (CV=0.54)

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0793, Sharpe=+0.3143)
- Yearly ICs: 2015: +0.236 | 2016: +0.060 | 2017: +0.075 | 2018: +0.174 | 2019: +0.093 | 2020: +0.072 | 2021: +0.143
- IC CV=0.50, Neg years=0/7, Half ratio=0.92, Recency ratio=0.73
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1504, Sharpe=+0.3043)
- Yearly ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089
- IC CV=0.38, Neg years=0/7, Half ratio=0.79, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`** (Lock IC=+0.1187, Sharpe=+0.2762)
- Yearly ICs: 2015: +0.314 | 2016: +0.119 | 2017: +0.224 | 2018: +0.210 | 2019: +0.155 | 2020: +0.170 | 2021: +0.117
- IC CV=0.34, Neg years=0/7, Half ratio=0.71, Recency ratio=0.67
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1114, Sharpe=+0.2420)
- Yearly ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.232 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.072
- IC CV=0.60, Neg years=0/7, Half ratio=0.58, Recency ratio=0.53
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0995, Sharpe=+0.2130)
- Yearly ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022
- IC CV=0.53, Neg years=0/7, Half ratio=0.63, Recency ratio=0.44
- Weak component: `max_down_ret` (CV=0.55)

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0810, Sharpe=+0.1027)
- Yearly ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172
- IC CV=0.33, Neg years=0/7, Half ratio=0.99, Recency ratio=0.89
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0842, Sharpe=+0.0999)
- Yearly ICs: 2015: +0.303 | 2016: +0.124 | 2017: +0.192 | 2018: +0.197 | 2019: +0.140 | 2020: +0.173 | 2021: +0.106
- IC CV=0.34, Neg years=0/7, Half ratio=0.68, Recency ratio=0.65
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1001, Sharpe=+0.0682)
- Yearly ICs: 2015: +0.270 | 2016: +0.153 | 2017: +0.085 | 2018: +0.126 | 2019: +0.079 | 2020: +0.129 | 2021: +0.109
- IC CV=0.44, Neg years=0/7, Half ratio=0.69, Recency ratio=0.56
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1226, Sharpe=+0.0514)
- Yearly ICs: 2015: +0.270 | 2016: +0.058 | 2017: +0.232 | 2018: +0.171 | 2019: +0.151 | 2020: +0.152 | 2021: +0.140
- IC CV=0.38, Neg years=0/7, Half ratio=0.81, Recency ratio=0.89
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0948, Sharpe=+0.0248)
- Yearly ICs: 2015: +0.297 | 2016: +0.084 | 2017: +0.247 | 2018: +0.154 | 2019: +0.106 | 2020: +0.168 | 2021: +0.113
- IC CV=0.43, Neg years=0/7, Half ratio=0.73, Recency ratio=0.74
- Weak component: `close_vs_open_range` (CV=0.48)

### 159915ETF — `single` True Positives

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance`** (Lock IC=+0.1103, Sharpe=+1.5993)
- Yearly ICs: 2015: +0.214 | 2016: +0.134 | 2017: -0.001 | 2018: +0.166 | 2019: +0.189 | 2020: +0.196 | 2021: +0.146
- IC CV=0.45, Neg years=1/7, Half ratio=1.35, Recency ratio=0.99
- Weak component: `impulse_bar_dominance` (CV=1.19)

**`combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1279, Sharpe=+1.5377)
- Yearly ICs: 2015: +0.234 | 2016: +0.094 | 2017: -0.031 | 2018: +0.132 | 2019: +0.264 | 2020: +0.182 | 2021: +0.132
- IC CV=0.63, Neg years=1/7, Half ratio=1.49, Recency ratio=0.96
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1355, Sharpe=+1.1554)
- Yearly ICs: 2015: +0.184 | 2016: +0.087 | 2017: +0.006 | 2018: +0.160 | 2019: +0.235 | 2020: +0.131 | 2021: +0.144
- IC CV=0.50, Neg years=0/7, Half ratio=1.27, Recency ratio=1.01
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0900, Sharpe=+0.9682)
- Yearly ICs: 2015: +0.225 | 2016: +0.116 | 2017: -0.030 | 2018: +0.100 | 2019: +0.153 | 2020: +0.167 | 2021: +0.117
- IC CV=0.60, Neg years=1/7, Half ratio=2.10, Recency ratio=0.83
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_z_sum__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1452, Sharpe=+0.9601)
- Yearly ICs: 2015: +0.208 | 2016: +0.074 | 2017: +0.020 | 2018: +0.132 | 2019: +0.165 | 2020: +0.128 | 2021: +0.158
- IC CV=0.45, Neg years=0/7, Half ratio=1.13, Recency ratio=1.01
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1192, Sharpe=+0.4661)
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034
- IC CV=0.90, Neg years=1/7, Half ratio=0.89, Recency ratio=0.61
- Weak component: `yesterday_first_30min_return` (CV=1.04)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1297, Sharpe=+0.0522)
- Yearly ICs: 2015: +0.232 | 2016: +0.175 | 2017: -0.028 | 2018: +0.143 | 2019: +0.206 | 2020: +0.138 | 2021: +0.124
- IC CV=0.55, Neg years=1/7, Half ratio=1.22, Recency ratio=0.64
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_z_sum__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0866, Sharpe=+0.0136)
- Yearly ICs: 2015: +0.174 | 2016: +0.067 | 2017: +0.044 | 2018: +0.086 | 2019: +0.175 | 2020: +0.095 | 2021: +0.153
- IC CV=0.44, Neg years=0/7, Half ratio=1.32, Recency ratio=1.02
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Median | persistent | +0.1137 | +0.0712 | +0.0965 | 2y |
| `rbreaker_sell_setup_proximity_early` | Median | persistent | +0.1093 | +0.0576 | +0.1515 | 2y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | TP | persistent | +0.0960 | +0.0234 | +0.1970 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0670 | +0.1425 | +0.0083 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0369 | +0.1355 | -0.0350 | 4y |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Median | gradual | +0.0361 | +0.1513 | -0.0650 | 4y |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | immediate | -0.0453 | +0.0618 | -0.0376 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=2, persistent=4

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Median | gradual | +0.1278 | +0.0960 | -0.0439 | 4y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | persistent | +0.1165 | +0.0912 | +0.0177 | 4y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1162 | +0.1552 | +0.0293 | 4y |
| `combo_rank_max__max_up_ret__early_body_momentum` | Median | gradual | +0.1160 | +0.1125 | -0.0668 | 4y |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1159 | +0.0796 | -0.0265 | 4y |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1053 | +0.0568 | +0.2040 | ∞ |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | Median | persistent | +0.0973 | +0.0382 | +0.0127 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | gradual | +0.0966 | +0.1332 | -0.0072 | 4y |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0404 | 1y |
| `max_up_ret` | Median | gradual | +0.0954 | +0.1044 | -0.0291 | 4y |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0824 | +0.0767 | +0.0885 | ∞ |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Median | persistent | +0.0819 | +0.0775 | +0.0041 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early` | TP | persistent | +0.0819 | +0.0680 | +0.0578 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | TP | gradual | +0.0779 | +0.0506 | -0.0035 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0667 | +0.0659 | +0.1729 | ∞ |
| `combo_sig_product__max_up_ret__body_size_progression` | TP | persistent | +0.0643 | +0.0644 | +0.0777 | ∞ |
| `combo_rel_diff__max_up_ret__body_size_progression` | Median | persistent | +0.0641 | +0.0925 | +0.1061 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0600 | +0.0723 | +0.0459 | ∞ |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0570 | +0.0915 | +0.1035 | 3y |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | TP | fast | +0.0569 | -0.0040 | +0.1243 | 1y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0514 | +0.0668 | +0.2403 | ∞ |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Median | persistent | +0.0496 | +0.0684 | +0.0085 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0396 | +0.0769 | +0.0854 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.0308 | +0.0972 | +0.0407 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0279 | +0.0649 | +0.0855 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0158 | +0.0999 | +0.1018 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Median | persistent | +0.0063 | +0.1139 | +0.0526 | ∞ |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | TP | immediate | -0.0168 | -0.0247 | +0.1016 | ∞ |
| `combo_ratio__max_down_ret__net_volume_flow` | Median | immediate | -0.0560 | +0.0066 | +0.1091 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=1, gradual=6, persistent=21

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1776 | +0.1159 | +0.1263 | 2y |
| `combo_z_sum__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1550 | +0.1368 | +0.0881 | ∞ |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Median | gradual | +0.1251 | +0.1720 | -0.0681 | 4y |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1062 | +0.1869 | +0.0371 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early` | Median | persistent | +0.1031 | +0.1410 | +0.0658 | ∞ |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1023 | +0.1961 | -0.0670 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0899 | +0.1369 | +0.0817 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance` | TP | persistent | +0.0852 | +0.0942 | +0.0835 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0776 | +0.0662 | +0.0816 | ∞ |
| `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0499 | +0.1392 | +0.1150 | ∞ |
| `combo_sig_product__max_up_ret__impulse_bar_dominance` | Median | persistent | +0.0095 | +0.1798 | +0.0172 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=2, persistent=9

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 3/20 top rejects are profitable (15%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.2382, Lock IC=+0.0050, Sharpe=+0.1767

**B2 Rolling Guard**: 1/20 top rejects are profitable (5%)

- `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1637, Lock IC=+0.0306, Sharpe=+0.2008

**BH-FDR Gate**: 4/20 top rejects are profitable (20%)

- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0280, Sharpe=+0.3353
- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0260, Sharpe=+0.3353
- `combo_sig_product__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1072, Lock IC=+0.0233, Sharpe=+0.3353

**B3 Composite Floor**: 9/20 top rejects are profitable (45%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.1837, Lock IC=+0.0933, Sharpe=+1.0458
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2356, Lock IC=+0.0236, Sharpe=+0.5106
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2037, Lock IC=+0.0658, Sharpe=+0.1382

**B4 Correlation Gate**: 2/14 top rejects are profitable (14%)

- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1804, Lock IC=+0.0655, Sharpe=+0.0072
- `combo_z_sum__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1804, Lock IC=+0.0655, Sharpe=+0.0072

### 500ETF — `single`

**7-Year Jackknife**: 13/20 top rejects are profitable (65%)

- `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2758, Lock IC=+0.1064, Sharpe=+0.4173
- `combo_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2635, Lock IC=+0.1118, Sharpe=+0.3980
- `combo_min__star50_limit_proximity_early__opening_momentum_score`: Train IC=+0.2635, Lock IC=+0.1118, Sharpe=+0.3980

**B2 Rolling Guard**: 9/20 top rejects are profitable (45%)

- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Sharpe=+0.4761
- `combo_tri_z_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Sharpe=+0.4761
- `combo_tri_mean__opening_auction_imbalance__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Sharpe=+0.4761

**BH-FDR Gate**: 2/16 top rejects are profitable (12%)

- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.2780
- `combo_z_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.2780

**B3 Composite Floor**: 18/20 top rejects are profitable (90%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2827, Lock IC=+0.1172, Sharpe=+0.8869
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2827, Lock IC=+0.1172, Sharpe=+0.8869
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2945, Lock IC=+0.1037, Sharpe=+0.7837

**B4 Correlation Gate**: 10/20 top rejects are profitable (50%)

- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.1127
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3072, Lock IC=+0.1015, Sharpe=+0.8294
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+0.7942

**Adaptive Correlation Gate**: 10/20 top rejects are profitable (50%)

- `combo_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2426, Lock IC=+0.1093, Sharpe=+1.0727
- `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2552, Lock IC=+0.1139, Sharpe=+1.0377
- `combo_rank_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2841, Lock IC=+0.1319, Sharpe=+0.7126

### 159915ETF — `single`

**7-Year Jackknife**: 9/20 top rejects are profitable (45%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.3653
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.3653
- `combo_tri_min__max_up_ret__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.2426, Lock IC=+0.0756, Sharpe=+0.7419

**B2 Rolling Guard**: 16/20 top rejects are profitable (80%)

- `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2004, Lock IC=+0.1176, Sharpe=+0.5263
- `combo_diff__max_up_ret__impulse_bar_dominance`: Train IC=+0.2018, Lock IC=+0.0176, Sharpe=+0.4946
- `combo_z_diff__max_up_ret__impulse_bar_dominance`: Train IC=+0.2018, Lock IC=+0.0176, Sharpe=+0.4946

**BH-FDR Gate**: 5/14 top rejects are profitable (36%)

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+0.7804
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+0.7804
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Sharpe=+0.7804

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+1.7354
- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+1.7354
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.5392

**B4 Correlation Gate**: 18/20 top rejects are profitable (90%)

- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+1.7354
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+1.7354
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2531, Lock IC=+0.1242, Sharpe=+1.5756

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_down_ret` | 0 | 3 | 3 | 0% |  |
| `bar_ret_0` | 0 | 3 | 3 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 9 | 9 | 0% |  |
| `max_up_ret` | 0 | 11 | 11 | 0% |  |
| `star50_limit_proximity_early` | 0 | 10 | 10 | 0% |  |
| `close_vs_open_range` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 3 | 3 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 5 | 5 | 0% |  |
| `body_size_progression` | 0 | 2 | 2 | 0% |  |
| `first_bar_sentiment` | 0 | 8 | 8 | 0% |  |
| `bar_body_rng_0` | 0 | 2 | 2 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=10, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=0, TP=5, FP rate=0%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=6, FP rate=0%

