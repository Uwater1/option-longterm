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
| 300ETF | single | 11 | 2 | 4 | 5 | 18% | 0.49 |
| 500ETF | single | 37 | 0 | 15 | 22 | 0% | 0.71 |
| 159915ETF | single | 15 | 0 | 2 | 13 | 0% | 0.90 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=2, TP=5)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_std_across_regimes | 0.051 | 0.090 | 0.051 | 0.090 | -4.53 | 0.101 | 57% |
| n_negative_regimes | 0.500 | 1.400 | 0.500 | 1.000 | -1.12 | 2.500 | 57% |
| ic_cv | 0.801 | 1.793 | 0.801 | 0.880 | -0.73 | 3.267 | 57% |
| n_negative_years | 1.000 | 1.600 | 1.000 | 1.000 | -0.71 | 2.500 | 57% |
| weak_link_cv | 1.157 | 1.252 | 1.157 | 1.141 | -0.58 | 1.256 | 71% |
| recency_ratio | 0.763 | 0.548 | 0.763 | 0.628 | +0.57 | 0.884 | 71% |
| half_ratio | 1.064 | 0.887 | 1.064 | 1.025 | +0.35 | 1.194 | 71% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_ratio__first_bar_sentiment__volume_surge_direction`** (Lock IC=-0.0280, Sharpe=-1.7117)
- Yearly ICs: 2015: +0.083 | 2016: +0.112 | 2017: +0.044 | 2018: +0.089 | 2019: +0.064 | 2020: -0.038 | 2021: +0.135
- IC CV=0.75, Neg years=1/7, Half ratio=0.87, Recency ratio=0.50
- Weak component: `volume_surge_direction` (CV=1.02, neg years=1)
- Regime ICs: Q1_low_vol=+0.088, Q2=-0.007, Q3_mid=+0.119, Q4=+0.059, Q5_high_vol=+0.111

**`combo_z_sum__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0129, Sharpe=-0.7923)
- Yearly ICs: 2015: +0.117 | 2016: +0.054 | 2017: +0.002 | 2018: +0.172 | 2019: +0.051 | 2020: -0.003 | 2021: +0.179
- IC CV=0.86, Neg years=1/7, Half ratio=1.26, Recency ratio=1.03
- Weak component: `volume_weighted_price_position` (CV=1.30, neg years=1)
- Regime ICs: Q1_low_vol=+0.005, Q2=+0.054, Q3_mid=+0.101, Q4=+0.092, Q5_high_vol=+0.178

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0616, Sharpe=-0.0803)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095
- IC CV=1.14, Neg years=1/7, Half ratio=0.62, Recency ratio=0.50
- Regime ICs: Q1_low_vol=-0.067, Q2=+0.000, Q3_mid=+0.053, Q4=+0.178, Q5_high_vol=+0.171

**`combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0285, Sharpe=-0.8593)
- Yearly ICs: 2015: +0.224 | 2016: +0.053 | 2017: -0.064 | 2018: +0.216 | 2019: +0.121 | 2020: +0.053 | 2021: +0.169
- IC CV=0.87, Neg years=1/7, Half ratio=1.13, Recency ratio=0.80
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.046, Q2=-0.008, Q3_mid=+0.122, Q4=+0.250, Q5_high_vol=+0.195

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0280, Sharpe=-0.3103)
- Yearly ICs: 2015: +0.254 | 2016: +0.095 | 2017: +0.008 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132
- IC CV=0.65, Neg years=0/7, Half ratio=0.81, Recency ratio=0.50
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.027, Q3_mid=+0.113, Q4=+0.191, Q5_high_vol=+0.227

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0120, Sharpe=-0.2082)
- Yearly ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156
- IC CV=0.58, Neg years=1/7, Half ratio=1.19, Recency ratio=0.77
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.052, Q3_mid=+0.124, Q4=+0.091, Q5_high_vol=+0.162

### 500ETF — `single` Median Features

**`combo_ratio__max_down_ret__opening_auction_imbalance`** (Lock IC=+0.1213, Sharpe=-0.2902)
- Yearly ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004
- IC CV=0.47, Neg years=0/7, Half ratio=0.64, Recency ratio=0.42
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.001, Q3_mid=+0.137, Q4=+0.092, Q5_high_vol=+0.174

**`combo_rank_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1080, Sharpe=-0.0771)
- Yearly ICs: 2015: +0.231 | 2016: +0.111 | 2017: +0.207 | 2018: +0.196 | 2019: +0.110 | 2020: +0.121 | 2021: +0.062
- IC CV=0.39, Neg years=0/7, Half ratio=0.60, Recency ratio=0.54
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.088, Q3_mid=+0.152, Q4=+0.089, Q5_high_vol=+0.242

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

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0935, Sharpe=-0.0443)
- Yearly ICs: 2015: +0.232 | 2016: +0.107 | 2017: +0.188 | 2018: +0.199 | 2019: +0.083 | 2020: +0.160 | 2021: +0.074
- IC CV=0.38, Neg years=0/7, Half ratio=0.60, Recency ratio=0.69
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.026, Q3_mid=+0.161, Q4=+0.189, Q5_high_vol=+0.246

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0879, Sharpe=-0.1032)
- Yearly ICs: 2015: +0.212 | 2016: +0.116 | 2017: +0.206 | 2018: +0.042 | 2019: +0.139 | 2020: +0.111 | 2021: +0.105
- IC CV=0.42, Neg years=0/7, Half ratio=0.58, Recency ratio=0.66
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.090, Q3_mid=+0.093, Q4=+0.140, Q5_high_vol=+0.221

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`** (Lock IC=+0.0843, Sharpe=-0.9623)
- Yearly ICs: 2015: +0.247 | 2016: +0.115 | 2017: +0.227 | 2018: +0.194 | 2019: +0.094 | 2020: +0.144 | 2021: +0.122
- IC CV=0.34, Neg years=0/7, Half ratio=0.70, Recency ratio=0.73
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.065, Q3_mid=+0.181, Q4=+0.172, Q5_high_vol=+0.269

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0810, Sharpe=-0.9675)
- Yearly ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172
- IC CV=0.33, Neg years=0/7, Half ratio=0.99, Recency ratio=0.89
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.128, Q3_mid=+0.198, Q4=+0.162, Q5_high_vol=+0.330

**`combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0797, Sharpe=-0.5306)
- Yearly ICs: 2015: +0.277 | 2016: +0.121 | 2017: +0.185 | 2018: +0.234 | 2019: +0.134 | 2020: +0.136 | 2021: +0.111
- IC CV=0.34, Neg years=0/7, Half ratio=0.77, Recency ratio=0.62
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.047, Q3_mid=+0.177, Q4=+0.181, Q5_high_vol=+0.272

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

**`combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0692, Sharpe=-0.4550)
- Yearly ICs: 2015: +0.236 | 2016: +0.052 | 2017: +0.089 | 2018: +0.180 | 2019: +0.118 | 2020: +0.076 | 2021: +0.132
- IC CV=0.47, Neg years=0/7, Half ratio=0.98, Recency ratio=0.72
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.018, Q3_mid=+0.147, Q4=+0.106, Q5_high_vol=+0.210

**`combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0685, Sharpe=-0.9256)
- Yearly ICs: 2015: +0.210 | 2016: +0.049 | 2017: +0.164 | 2018: +0.182 | 2019: +0.150 | 2020: +0.194 | 2021: +0.148
- IC CV=0.31, Neg years=0/7, Half ratio=1.42, Recency ratio=1.32
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.092, Q3_mid=+0.144, Q4=+0.092, Q5_high_vol=+0.272

**`combo_rank_max__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0566, Sharpe=-0.5423)
- Yearly ICs: 2015: +0.241 | 2016: +0.039 | 2017: +0.087 | 2018: +0.188 | 2019: +0.136 | 2020: +0.045 | 2021: +0.102
- IC CV=0.57, Neg years=0/7, Half ratio=0.92, Recency ratio=0.53
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.129, Q2=-0.017, Q3_mid=+0.130, Q4=+0.127, Q5_high_vol=+0.202

### 159915ETF — `single` Median Features

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.0844, Sharpe=-0.3459)
- Yearly ICs: 2015: +0.178 | 2016: +0.141 | 2017: +0.038 | 2018: +0.099 | 2019: +0.184 | 2020: +0.122 | 2021: +0.175
- IC CV=0.37, Neg years=0/7, Half ratio=1.37, Recency ratio=0.93
- Weak component: `max_up_ret` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.083, Q3_mid=+0.204, Q4=+0.111, Q5_high_vol=+0.194

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0585, Sharpe=-0.3911)
- Yearly ICs: 2015: +0.244 | 2016: +0.095 | 2017: -0.027 | 2018: +0.075 | 2019: +0.172 | 2020: +0.164 | 2021: +0.131
- IC CV=0.65, Neg years=1/7, Half ratio=2.26, Recency ratio=0.87
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.046, Q3_mid=+0.197, Q4=+0.063, Q5_high_vol=+0.245

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0379, Sharpe=+0.7043)
- Yearly ICs: 2015: +0.262 | 2016: +0.094 | 2017: -0.073 | 2018: +0.144 | 2019: +0.090 | 2020: +0.062 | 2021: +0.136
- IC CV=0.91, Neg years=1/7, Half ratio=0.75, Recency ratio=0.56
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0660, Sharpe=+0.3638)
- Yearly ICs: 2015: +0.197 | 2016: +0.071 | 2017: -0.030 | 2018: +0.186 | 2019: +0.143 | 2020: +0.035 | 2021: +0.134
- IC CV=0.74, Neg years=1/7, Half ratio=1.13, Recency ratio=0.63
- Weak component: `star50_limit_proximity_early` (CV=1.21)

**`combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0016, Sharpe=+0.2719)
- Yearly ICs: 2015: +0.223 | 2016: -0.064 | 2017: +0.071 | 2018: -0.050 | 2019: -0.011 | 2020: +0.022 | 2021: -0.071
- IC CV=5.62, Neg years=4/7, Half ratio=-0.29, Recency ratio=-0.31
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0706, Sharpe=+0.1258)
- Yearly ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130
- IC CV=0.88, Neg years=1/7, Half ratio=1.82, Recency ratio=1.12
- Weak component: `limit_down_proximity_early` (CV=1.62)

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0189, Sharpe=+0.0731)
- Yearly ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.075 | 2018: +0.166 | 2019: +0.085 | 2020: +0.075 | 2021: +0.151
- IC CV=0.82, Neg years=1/7, Half ratio=1.02, Recency ratio=0.74
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1183, Sharpe=+1.2421)
- Yearly ICs: 2015: +0.294 | 2016: +0.022 | 2017: +0.204 | 2018: +0.144 | 2019: +0.184 | 2020: +0.146 | 2021: +0.091
- IC CV=0.51, Neg years=0/7, Half ratio=0.88, Recency ratio=0.75
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1083, Sharpe=+1.1127)
- Yearly ICs: 2015: +0.289 | 2016: +0.074 | 2017: +0.196 | 2018: +0.155 | 2019: +0.174 | 2020: +0.112 | 2021: +0.096
- IC CV=0.43, Neg years=0/7, Half ratio=0.71, Recency ratio=0.57
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1139, Sharpe=+1.0377)
- Yearly ICs: 2015: +0.268 | 2016: +0.119 | 2017: +0.110 | 2018: +0.189 | 2019: +0.088 | 2020: +0.115 | 2021: +0.140
- IC CV=0.39, Neg years=0/7, Half ratio=0.73, Recency ratio=0.66
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1015, Sharpe=+0.8294)
- Yearly ICs: 2015: +0.313 | 2016: +0.094 | 2017: +0.215 | 2018: +0.203 | 2019: +0.178 | 2020: +0.143 | 2021: +0.098
- IC CV=0.40, Neg years=0/7, Half ratio=0.70, Recency ratio=0.59
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1256, Sharpe=+0.7571)
- Yearly ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.194 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148
- IC CV=0.42, Neg years=0/7, Half ratio=1.09, Recency ratio=1.10
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1135, Sharpe=+0.6871)
- Yearly ICs: 2015: +0.292 | 2016: +0.072 | 2017: +0.122 | 2018: +0.214 | 2019: +0.183 | 2020: +0.187 | 2021: +0.129
- IC CV=0.39, Neg years=0/7, Half ratio=0.95, Recency ratio=0.87
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0793, Sharpe=+0.6251)
- Yearly ICs: 2015: +0.236 | 2016: +0.060 | 2017: +0.075 | 2018: +0.174 | 2019: +0.093 | 2020: +0.072 | 2021: +0.143
- IC CV=0.50, Neg years=0/7, Half ratio=0.92, Recency ratio=0.73
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1100, Sharpe=+0.5932)
- Yearly ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052
- IC CV=0.52, Neg years=0/7, Half ratio=0.67, Recency ratio=0.56
- Weak component: `max_down_ret` (CV=0.55)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1261, Sharpe=+0.5742)
- Yearly ICs: 2015: +0.245 | 2016: +0.138 | 2017: +0.226 | 2018: +0.116 | 2019: +0.121 | 2020: +0.123 | 2021: +0.067
- IC CV=0.40, Neg years=0/7, Half ratio=0.47, Recency ratio=0.49

**`combo_rel_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0020, Sharpe=+0.4829)
- Yearly ICs: 2015: +0.149 | 2016: +0.138 | 2017: -0.011 | 2018: +0.082 | 2019: +0.070 | 2020: +0.030 | 2021: +0.081
- IC CV=0.68, Neg years=1/7, Half ratio=0.62, Recency ratio=0.39
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_mean__bar_ret_0__max_down_ret`** (Lock IC=+0.1025, Sharpe=+0.4799)
- Yearly ICs: 2015: +0.227 | 2016: +0.106 | 2017: +0.224 | 2018: +0.210 | 2019: +0.137 | 2020: +0.111 | 2021: +0.088
- IC CV=0.36, Neg years=0/7, Half ratio=0.81, Recency ratio=0.60
- Weak component: `max_down_ret` (CV=0.55)

**`combo_sig_product__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0992, Sharpe=+0.3137)
- Yearly ICs: 2015: +0.236 | 2016: +0.145 | 2017: +0.119 | 2018: +0.143 | 2019: +0.067 | 2020: +0.118 | 2021: +0.071
- IC CV=0.41, Neg years=0/7, Half ratio=0.69, Recency ratio=0.50
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0938, Sharpe=+0.3068)
- Yearly ICs: 2015: +0.280 | 2016: +0.069 | 2017: +0.269 | 2018: +0.189 | 2019: +0.147 | 2020: +0.176 | 2021: +0.098
- IC CV=0.42, Neg years=0/7, Half ratio=0.86, Recency ratio=0.78
- Weak component: `max_down_ret` (CV=0.55)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1504, Sharpe=+0.3043)
- Yearly ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089
- IC CV=0.38, Neg years=0/7, Half ratio=0.79, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_mean__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1219, Sharpe=+0.2731)
- Yearly ICs: 2015: +0.271 | 2016: +0.087 | 2017: +0.202 | 2018: +0.108 | 2019: +0.105 | 2020: +0.125 | 2021: +0.059
- IC CV=0.50, Neg years=0/7, Half ratio=0.52, Recency ratio=0.51
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1114, Sharpe=+0.2420)
- Yearly ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.232 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.072
- IC CV=0.60, Neg years=0/7, Half ratio=0.58, Recency ratio=0.53
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0995, Sharpe=+0.1817)
- Yearly ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022
- IC CV=0.53, Neg years=0/7, Half ratio=0.63, Recency ratio=0.44
- Weak component: `max_down_ret` (CV=0.55)

**`combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1115, Sharpe=+0.1148)
- Yearly ICs: 2015: +0.313 | 2016: +0.098 | 2017: +0.234 | 2018: +0.157 | 2019: +0.132 | 2020: +0.173 | 2021: +0.075
- IC CV=0.45, Neg years=0/7, Half ratio=0.65, Recency ratio=0.60
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0907, Sharpe=+0.1115)
- Yearly ICs: 2015: +0.310 | 2016: +0.110 | 2017: +0.179 | 2018: +0.192 | 2019: +0.131 | 2020: +0.145 | 2021: +0.107
- IC CV=0.39, Neg years=0/7, Half ratio=0.63, Recency ratio=0.60
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

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1147, Sharpe=+1.4841)
- Yearly ICs: 2015: +0.254 | 2016: +0.171 | 2017: -0.008 | 2018: +0.180 | 2019: +0.206 | 2020: +0.202 | 2021: +0.114
- IC CV=0.50, Neg years=1/7, Half ratio=1.09, Recency ratio=0.74
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1182, Sharpe=+1.3926)
- Yearly ICs: 2015: +0.238 | 2016: +0.049 | 2017: -0.027 | 2018: +0.121 | 2019: +0.229 | 2020: +0.140 | 2021: +0.103
- IC CV=0.71, Neg years=1/7, Half ratio=1.56, Recency ratio=0.85
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.21)

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1318, Sharpe=+1.2965)
- Yearly ICs: 2015: +0.228 | 2016: +0.122 | 2017: +0.009 | 2018: +0.185 | 2019: +0.198 | 2020: +0.148 | 2021: +0.176
- IC CV=0.44, Neg years=0/7, Half ratio=1.16, Recency ratio=0.93
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1423, Sharpe=+1.2341)
- Yearly ICs: 2015: +0.190 | 2016: +0.046 | 2017: +0.009 | 2018: +0.127 | 2019: +0.235 | 2020: +0.125 | 2021: +0.141
- IC CV=0.58, Neg years=0/7, Half ratio=1.42, Recency ratio=1.13
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1327, Sharpe=+1.1160)
- Yearly ICs: 2015: +0.239 | 2016: +0.078 | 2017: -0.023 | 2018: +0.106 | 2019: +0.259 | 2020: +0.133 | 2021: +0.110
- IC CV=0.69, Neg years=1/7, Half ratio=1.25, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1426, Sharpe=+0.9756)
- Yearly ICs: 2015: +0.225 | 2016: +0.120 | 2017: -0.020 | 2018: +0.156 | 2019: +0.239 | 2020: +0.165 | 2021: +0.143
- IC CV=0.54, Neg years=1/7, Half ratio=1.24, Recency ratio=0.89
- Weak component: `bar_body_rng_0` (CV=0.51)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0900, Sharpe=+0.9652)
- Yearly ICs: 2015: +0.225 | 2016: +0.116 | 2017: -0.030 | 2018: +0.100 | 2019: +0.153 | 2020: +0.167 | 2021: +0.117
- IC CV=0.60, Neg years=1/7, Half ratio=2.10, Recency ratio=0.83
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1338, Sharpe=+0.6628)
- Yearly ICs: 2015: +0.190 | 2016: +0.103 | 2017: +0.023 | 2018: +0.127 | 2019: +0.160 | 2020: +0.153 | 2021: +0.167
- IC CV=0.39, Neg years=0/7, Half ratio=1.26, Recency ratio=1.09
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1192, Sharpe=+0.4661)
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034
- IC CV=0.90, Neg years=1/7, Half ratio=0.89, Recency ratio=0.61
- Weak component: `yesterday_first_30min_return` (CV=1.04)

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1269, Sharpe=+0.4442)
- Yearly ICs: 2015: +0.247 | 2016: +0.117 | 2017: +0.034 | 2018: +0.080 | 2019: +0.244 | 2020: +0.132 | 2021: +0.128
- IC CV=0.53, Neg years=0/7, Half ratio=1.24, Recency ratio=0.71
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1297, Sharpe=+0.2566)
- Yearly ICs: 2015: +0.232 | 2016: +0.175 | 2017: -0.028 | 2018: +0.143 | 2019: +0.206 | 2020: +0.138 | 2021: +0.124
- IC CV=0.55, Neg years=1/7, Half ratio=1.22, Recency ratio=0.64
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0906, Sharpe=+0.1387)
- Yearly ICs: 2015: +0.195 | 2016: +0.061 | 2017: +0.043 | 2018: +0.054 | 2019: +0.164 | 2020: +0.103 | 2021: +0.186
- IC CV=0.53, Neg years=0/7, Half ratio=1.39, Recency ratio=1.13
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)

**`combo_clamp_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.1109, Sharpe=+0.0049)
- Yearly ICs: 2015: +0.232 | 2016: +0.041 | 2017: +0.015 | 2018: +0.122 | 2019: +0.181 | 2020: +0.105 | 2021: +0.158
- IC CV=0.58, Neg years=0/7, Half ratio=1.29, Recency ratio=0.97
- Weak component: `demark_setup_reversal_early` (CV=0.85)

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | Median | persistent | +0.1093 | +0.0576 | +0.1515 | 2y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | TP | persistent | +0.0960 | +0.0234 | +0.1970 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0951 | +0.0914 | +0.0035 | 2y |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0563 | +0.1922 | -0.1808 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0446 | +0.1313 | -0.0310 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0377 | +0.1764 | -0.0345 | 4y |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0283 | +0.1463 | +0.0265 | ∞ |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Median | gradual | +0.0283 | +0.1374 | -0.0976 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | gradual | +0.0254 | +0.1334 | -0.0436 | 4y |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | FP | gradual | +0.0185 | +0.0578 | -0.0352 | 2y |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | immediate | -0.0453 | +0.0618 | -0.0376 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=6, persistent=4

**FP decay trajectories:**

- `combo_ratio__first_bar_sentiment__volume_surge_direction`: Y1:+0.019 → Y2:+0.058 → Y3:-0.051 → Y4:+0.006 → Y5:-0.035
- `combo_z_sum__max_up_ret__volume_weighted_price_position`: Y1:+0.056 → Y2:+0.192 → Y3:+0.025 → Y4:+0.114 → Y5:-0.181

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | Median | persistent | +0.1281 | +0.0718 | +0.1198 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Median | gradual | +0.1278 | +0.0960 | -0.0439 | 4y |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1204 | +0.0726 | +0.1121 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | persistent | +0.1165 | +0.0912 | +0.0177 | 4y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1162 | +0.1552 | +0.0293 | 4y |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1159 | +0.0796 | -0.0265 | 4y |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1053 | +0.0568 | +0.2040 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | gradual | +0.0966 | +0.1332 | -0.0072 | 4y |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0404 | 1y |
| `max_up_ret` | Median | gradual | +0.0954 | +0.1044 | -0.0291 | 4y |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0943 | +0.0574 | +0.0022 | 4y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | persistent | +0.0942 | +0.0937 | +0.0717 | 3y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0921 | +0.0793 | +0.1842 | ∞ |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0885 | +0.1234 | +0.0058 | 4y |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0824 | +0.0767 | +0.0885 | ∞ |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0785 | +0.0606 | +0.1007 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | TP | gradual | +0.0779 | +0.0506 | -0.0035 | 4y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0756 | +0.0530 | +0.0807 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0754 | +0.0626 | +0.0030 | 4y |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | Median | persistent | +0.0732 | +0.0401 | +0.0175 | 4y |
| `combo_mean__bar_ret_0__max_down_ret` | TP | persistent | +0.0721 | +0.0548 | +0.0105 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0701 | +0.0496 | +0.0708 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0667 | +0.0659 | +0.1729 | ∞ |
| `combo_rel_diff__max_up_ret__body_size_progression` | Median | persistent | +0.0641 | +0.0925 | +0.1061 | ∞ |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0570 | +0.0915 | +0.1035 | 3y |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | TP | fast | +0.0569 | -0.0040 | +0.1243 | 1y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0514 | +0.0668 | +0.2403 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0509 | +0.0691 | +0.0097 | 4y |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Median | persistent | +0.0496 | +0.0684 | +0.0085 | 4y |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0472 | +0.0604 | +0.1725 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0396 | +0.0769 | +0.0854 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0279 | +0.0649 | +0.0855 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0158 | +0.0999 | +0.1018 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Median | persistent | +0.0063 | +0.1139 | +0.0526 | ∞ |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | TP | immediate | -0.0168 | -0.0247 | +0.1016 | ∞ |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | Median | immediate | -0.0560 | +0.0066 | +0.1091 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=1, gradual=5, persistent=29

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1776 | +0.1159 | +0.1263 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1573 | +0.1397 | +0.0771 | 4y |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | TP | persistent | +0.1316 | +0.1618 | +0.0271 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1299 | +0.1363 | +0.1021 | ∞ |
| `combo_max__max_up_ret__first_bar_return` | Median | gradual | +0.1102 | +0.1603 | -0.0743 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1047 | +0.1902 | -0.0535 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1031 | +0.1410 | +0.0658 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0959 | +0.1502 | +0.1125 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0959 | +0.1836 | +0.0723 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0899 | +0.1369 | +0.0817 | ∞ |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0864 | +0.0552 | +0.1287 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0799 | +0.1128 | +0.0949 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0776 | +0.0662 | +0.0816 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0733 | +0.1517 | +0.1033 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Median | gradual | +0.0483 | +0.0875 | -0.0177 | 4y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=3, persistent=12

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.743±0.003 | 0.690±0.035 | 0% | USEFUL |
| ic_ir | 0.648±0.018 | 0.572±0.048 | 0% | USEFUL |
| p_value | 0.006±0.006 | 0.000±0.000 | 4% | USEFUL |
| max_corr | 0.352±0.288 | 0.693±0.142 | 25% | USEFUL |
| deflated_ic | 0.169±0.042 | 0.237±0.038 | 11% | USEFUL |
| overall_ic | 0.170±0.042 | 0.237±0.038 | 12% | USEFUL |
| raw_ic | 0.079±0.009 | 0.086±0.041 | 18% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 3/20 top rejects are profitable (15%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.2340, Lock IC=+0.0050, Sharpe=+0.1767

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1637, Lock IC=+0.0306, Sharpe=+0.2008
- `gap_pct`: Train IC=+0.1525, Lock IC=+0.0795, Sharpe=+0.1398
- `combo_min__bar_ret_0__volume_surge_direction`: Train IC=+0.1563, Lock IC=+0.0151, Sharpe=+0.0150

**BH-FDR Gate**: 3/8 top rejects are profitable (38%)

- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0280, Sharpe=+0.3353
- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0260, Sharpe=+0.3353
- `combo_sig_product__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1072, Lock IC=+0.0233, Sharpe=+0.3353

**B3 Composite Floor**: 7/20 top rejects are profitable (35%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2603, Lock IC=+0.0248, Sharpe=+0.0677
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2603, Lock IC=+0.0248, Sharpe=+0.0677
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2601, Lock IC=+0.0248, Sharpe=+0.0677

**B4 Correlation Gate**: 6/15 top rejects are profitable (40%)

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2690, Lock IC=+0.0342, Sharpe=+0.8997
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2687, Lock IC=+0.0505, Sharpe=+0.2804
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1659, Lock IC=+0.0418, Sharpe=+0.1010

### 500ETF — `single`

**7-Year Jackknife**: 16/20 top rejects are profitable (80%)

- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2667, Lock IC=+0.1120, Sharpe=+0.4588
- `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2758, Lock IC=+0.1064, Sharpe=+0.4173
- `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2354, Lock IC=+0.0891, Sharpe=+0.4106

**B2 Rolling Guard**: 9/20 top rejects are profitable (45%)

- `combo_tri_mean__opening_auction_imbalance__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Sharpe=+0.4761
- `combo_tri_z_mean__opening_auction_imbalance__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Sharpe=+0.4761
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Sharpe=+0.4761

**BH-FDR Gate**: 3/20 top rejects are profitable (15%)

- `vol_ratio_10_60`: Train IC=+0.0927, Lock IC=+0.0309, Sharpe=+0.3757
- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.2780
- `combo_z_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.2780

**B3 Composite Floor**: 17/20 top rejects are profitable (85%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2827, Lock IC=+0.1172, Sharpe=+0.8869
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2827, Lock IC=+0.1172, Sharpe=+0.8869
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_day_regime_conviction`: Train IC=+0.2819, Lock IC=+0.1041, Sharpe=+0.8493

**B4 Correlation Gate**: 9/20 top rejects are profitable (45%)

- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.1127
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3072, Lock IC=+0.1015, Sharpe=+0.8294
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+0.7942

**Adaptive Correlation Gate**: 8/20 top rejects are profitable (40%)

- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.2059, Lock IC=+0.1703, Sharpe=+0.7632
- `combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2850, Lock IC=+0.1319, Sharpe=+0.7126
- `combo_rank_max__close_vs_open_range__first_bar_sentiment`: Train IC=+0.2583, Lock IC=+0.0713, Sharpe=+0.5539

### 159915ETF — `single`

**7-Year Jackknife**: 11/20 top rejects are profitable (55%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.3653
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.3653
- `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2092, Lock IC=+0.1358, Sharpe=+0.8345

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+0.8573
- `combo_z_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+0.8573
- `combo_tri_median__first_bar_sentiment__bar_body_rng_0__first_bar_return`: Train IC=+0.1949, Lock IC=+0.0856, Sharpe=+0.5636

**BH-FDR Gate**: 5/6 top rejects are profitable (83%)

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+0.7804
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+0.7804
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Sharpe=+0.7804

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.5392
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.5392
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2766, Lock IC=+0.1375, Sharpe=+1.5099

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2895, Lock IC=+0.1279, Sharpe=+1.5377
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Sharpe=+1.5377
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2692, Lock IC=+0.1273, Sharpe=+1.4562

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_std_across_regimes`: FP is lower (d=-4.53). Threshold 0.101 → 57% accuracy.
- `n_negative_regimes`: FP is lower (d=-1.12). Threshold 2.500 → 57% accuracy.
- `ic_cv`: FP is lower (d=-0.73). Threshold 3.267 → 57% accuracy.
- `n_negative_years`: FP is lower (d=-0.71). Threshold 2.500 → 57% accuracy.
- `weak_link_cv`: FP is lower (d=-0.58). Threshold 1.256 → 71% accuracy.
- `recency_ratio`: FP is higher (d=+0.57). Threshold 0.884 → 71% accuracy.

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
| `first_bar_sentiment` | 1 | 7 | 8 | 12% |  |
| `max_up_ret` | 1 | 11 | 12 | 8% |  |
| `star50_limit_proximity_early` | 0 | 14 | 14 | 0% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 7 | 7 | 0% |  |
| `max_down_ret` | 0 | 5 | 5 | 0% |  |
| `bar_body_rng_0` | 0 | 3 | 3 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 11 | 11 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 4 | 4 | 0% |  |
| `close_vs_open_range` | 0 | 3 | 3 | 0% |  |
| `bar_ret_0` | 0 | 7 | 7 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=22, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=6, FP rate=14%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=3, FP rate=0%

