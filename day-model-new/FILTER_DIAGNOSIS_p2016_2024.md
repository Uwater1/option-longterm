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
| 300ETF | single | 21 | 7 | 12 | 2 | 33% | 0.25 |
| 500ETF | single | 31 | 0 | 15 | 16 | 0% | 0.70 |
| 159915ETF | single | 30 | 0 | 5 | 25 | 0% | 0.86 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=7, TP=2)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.873 | 0.760 | 0.890 | 0.760 | +1.85 | 0.800 | 89% |
| ic_std_across_regimes | 0.043 | 0.064 | 0.043 | 0.064 | -1.76 | 0.027 | 67% |
| weak_link_cv | 0.946 | 1.155 | 0.889 | 1.155 | -1.69 | 0.763 | 67% |
| n_negative_years | 1.429 | 1.000 | 2.000 | 1.000 | +0.83 | 0.500 | 67% |
| recency_ratio | -1.045 | 5.011 | 2.695 | 5.011 | -0.73 | -13.817 | 67% |
| half_ratio | 1.144 | 1.040 | 1.087 | 1.040 | +0.29 | 0.654 | 67% |
| n_negative_regimes | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 67% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_min__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0067, Sharpe=-1.6023)
- Yearly ICs: 2016: +0.078 | 2017: -0.031 | 2018: +0.196 | 2019: +0.082 | 2020: +0.055 | 2021: +0.168 | 2022: +0.001 | 2023: +0.150
- IC CV=0.86, Neg years=1/8, Half ratio=1.09, Recency ratio=3.24
- Weak component: `max_up_ret` (CV=0.89, neg years=1)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.077, Q3_mid=+0.080, Q4=+0.032, Q5_high_vol=+0.212

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0007, Sharpe=-1.2926)
- Yearly ICs: 2016: +0.037 | 2017: -0.043 | 2018: +0.134 | 2019: +0.121 | 2020: +0.028 | 2021: +0.186 | 2022: -0.001 | 2023: +0.186
- IC CV=1.01, Neg years=2/8, Half ratio=1.43, Recency ratio=-29.47
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.157, Q3_mid=+0.084, Q4=+0.100, Q5_high_vol=+0.068

**`combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0161, Sharpe=-1.1152)
- Yearly ICs: 2016: +0.065 | 2017: -0.028 | 2018: +0.157 | 2019: +0.062 | 2020: -0.010 | 2021: +0.165 | 2022: +0.067 | 2023: +0.192
- IC CV=0.90, Neg years=2/8, Half ratio=1.54, Recency ratio=6.91
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.104, Q3_mid=+0.062, Q4=+0.036, Q5_high_vol=+0.196

**`combo_sig_product__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.0080, Sharpe=-1.0044)
- Yearly ICs: 2016: +0.097 | 2017: -0.032 | 2018: +0.152 | 2019: +0.116 | 2020: -0.016 | 2021: +0.139 | 2022: +0.027 | 2023: +0.148
- IC CV=0.89, Neg years=2/8, Half ratio=0.76, Recency ratio=2.69
- Weak component: `opening_drive_thrust_ratio` (CV=0.83, neg years=1)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.083, Q3_mid=+0.044, Q4=+0.048, Q5_high_vol=+0.120

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0055, Sharpe=-0.8381)
- Yearly ICs: 2016: +0.079 | 2017: -0.009 | 2018: +0.164 | 2019: +0.114 | 2020: -0.006 | 2021: +0.156 | 2022: +0.022 | 2023: +0.121
- IC CV=0.82, Neg years=2/8, Half ratio=0.78, Recency ratio=2.04
- Weak component: `max_up_ret` (CV=0.89, neg years=1)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.070, Q3_mid=+0.071, Q4=+0.044, Q5_high_vol=+0.116

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0088, Sharpe=-0.7278)
- Yearly ICs: 2016: +0.039 | 2017: +0.005 | 2018: +0.133 | 2019: +0.045 | 2020: +0.004 | 2021: +0.172 | 2022: +0.036 | 2023: +0.202
- IC CV=0.92, Neg years=0/8, Half ratio=1.86, Recency ratio=5.44
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.097, Q3_mid=+0.036, Q4=+0.031, Q5_high_vol=+0.176

**`combo_rank_max__bar_ret_0__first_bar_sentiment`** (Lock IC=-0.0033, Sharpe=-0.5336)
- Yearly ICs: 2016: +0.067 | 2017: +0.029 | 2018: +0.171 | 2019: +0.130 | 2020: -0.018 | 2021: +0.107 | 2022: +0.043 | 2023: +0.134
- IC CV=0.71, Neg years=1/8, Half ratio=0.55, Recency ratio=1.84
- Weak component: `first_bar_sentiment` (CV=0.69, neg years=1)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.073, Q3_mid=+0.083, Q4=+0.053, Q5_high_vol=+0.108

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_mean__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=+0.0535, Sharpe=-1.0074)
- Yearly ICs: 2016: -0.030 | 2017: -0.003 | 2018: +0.027 | 2019: +0.036 | 2020: -0.031 | 2021: +0.045 | 2022: +0.060 | 2023: +0.118
- IC CV=1.68, Neg years=3/8, Half ratio=3.66, Recency ratio=-5.42
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.087, Q3_mid=-0.020, Q4=+0.060, Q5_high_vol=-0.005

**`combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0427, Sharpe=-1.1309)
- Yearly ICs: 2016: +0.032 | 2017: -0.035 | 2018: +0.148 | 2019: +0.098 | 2020: +0.038 | 2021: +0.151 | 2022: +0.081 | 2023: +0.091
- IC CV=0.77, Neg years=1/8, Half ratio=1.27, Recency ratio=-59.25
- Weak component: `star50_limit_proximity_early` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.020, Q2=+0.045, Q3_mid=+0.083, Q4=+0.049, Q5_high_vol=+0.188

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0366, Sharpe=-0.5842)
- Yearly ICs: 2016: +0.063 | 2017: -0.068 | 2018: +0.202 | 2019: +0.123 | 2020: +0.060 | 2021: +0.173 | 2022: +0.045 | 2023: +0.140
- IC CV=0.87, Neg years=1/8, Half ratio=1.13, Recency ratio=-40.14
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.067, Q3_mid=+0.129, Q4=+0.053, Q5_high_vol=+0.214

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0354, Sharpe=-0.3491)
- Yearly ICs: 2016: +0.099 | 2017: +0.002 | 2018: +0.184 | 2019: +0.115 | 2020: +0.044 | 2021: +0.132 | 2022: +0.035 | 2023: +0.166
- IC CV=0.63, Neg years=0/8, Half ratio=0.84, Recency ratio=1.98
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.065, Q3_mid=+0.079, Q4=+0.052, Q5_high_vol=+0.194

**`combo_min__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=+0.0291, Sharpe=-0.2330)
- Yearly ICs: 2016: +0.077 | 2017: -0.048 | 2018: +0.219 | 2019: +0.081 | 2020: +0.053 | 2021: +0.127 | 2022: +0.043 | 2023: +0.136
- IC CV=0.85, Neg years=1/8, Half ratio=0.91, Recency ratio=6.14
- Weak component: `volume_surge_direction` (CV=0.95)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.089, Q3_mid=+0.056, Q4=+0.071, Q5_high_vol=+0.176

**`combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`** (Lock IC=+0.0288, Sharpe=-0.5423)
- Yearly ICs: 2016: +0.086 | 2017: +0.035 | 2018: +0.110 | 2019: +0.038 | 2020: -0.014 | 2021: +0.179 | 2022: +0.091 | 2023: +0.059
- IC CV=0.74, Neg years=1/8, Half ratio=1.21, Recency ratio=1.24
- Weak component: `bar_vol_0` (CV=2.19)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.034, Q3_mid=+0.028, Q4=+0.012, Q5_high_vol=+0.163

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0266, Sharpe=-0.1199)
- Yearly ICs: 2016: +0.067 | 2017: +0.029 | 2018: +0.190 | 2019: +0.043 | 2020: +0.046 | 2021: +0.168 | 2022: +0.020 | 2023: +0.162
- IC CV=0.72, Neg years=0/8, Half ratio=1.23, Recency ratio=1.90
- Weak component: `early_vwap_acceleration` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.118, Q3_mid=+0.085, Q4=+0.022, Q5_high_vol=+0.197

**`combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0234, Sharpe=-0.6582)
- Yearly ICs: 2016: +0.098 | 2017: +0.043 | 2018: +0.178 | 2019: +0.069 | 2020: +0.033 | 2021: +0.187 | 2022: +0.008 | 2023: +0.160
- IC CV=0.67, Neg years=0/8, Half ratio=0.97, Recency ratio=1.19
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.082, Q3_mid=+0.069, Q4=+0.047, Q5_high_vol=+0.171

**`combo_min__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=+0.0125, Sharpe=-1.0630)
- Yearly ICs: 2016: +0.041 | 2017: +0.013 | 2018: +0.223 | 2019: +0.067 | 2020: -0.005 | 2021: +0.179 | 2022: +0.036 | 2023: +0.173
- IC CV=0.90, Neg years=1/8, Half ratio=1.06, Recency ratio=3.88
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.123, Q3_mid=+0.112, Q4=+0.036, Q5_high_vol=+0.147

**`combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0094, Sharpe=-0.4218)
- Yearly ICs: 2016: +0.081 | 2017: +0.041 | 2018: +0.222 | 2019: +0.065 | 2020: -0.027 | 2021: +0.145 | 2022: +0.066 | 2023: +0.176
- IC CV=0.78, Neg years=1/8, Half ratio=0.82, Recency ratio=1.97
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.112, Q3_mid=+0.086, Q4=+0.060, Q5_high_vol=+0.149

**`combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0045, Sharpe=-1.0539)
- Yearly ICs: 2016: +0.072 | 2017: +0.064 | 2018: +0.200 | 2019: +0.058 | 2020: -0.012 | 2021: +0.169 | 2022: +0.057 | 2023: +0.180
- IC CV=0.71, Neg years=1/8, Half ratio=0.94, Recency ratio=1.74
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.096, Q3_mid=+0.091, Q4=+0.050, Q5_high_vol=+0.144

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0042, Sharpe=-0.2878)
- Yearly ICs: 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142
- IC CV=0.57, Neg years=0/8, Half ratio=0.64, Recency ratio=1.09
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.069, Q3_mid=+0.077, Q4=+0.073, Q5_high_vol=+0.130

### 500ETF — `single` Median Features

**`combo_z_sum__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.1011, Sharpe=-0.0960)
- Yearly ICs: 2016: +0.058 | 2017: +0.244 | 2018: +0.190 | 2019: +0.136 | 2020: +0.163 | 2021: +0.120 | 2022: +0.079 | 2023: +0.087
- IC CV=0.43, Neg years=0/8, Half ratio=0.72, Recency ratio=0.55
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.023, Q3_mid=+0.147, Q4=+0.149, Q5_high_vol=+0.171

**`combo_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0905, Sharpe=-0.1233)
- Yearly ICs: 2016: +0.089 | 2017: +0.213 | 2018: +0.253 | 2019: +0.159 | 2020: +0.134 | 2021: +0.097 | 2022: +0.055 | 2023: +0.067
- IC CV=0.50, Neg years=0/8, Half ratio=0.50, Recency ratio=0.41
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.153, Q2=-0.019, Q3_mid=+0.135, Q4=+0.170, Q5_high_vol=+0.172

**`combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration`** (Lock IC=+0.0887, Sharpe=-0.0130)
- Yearly ICs: 2016: +0.046 | 2017: +0.160 | 2018: +0.222 | 2019: +0.173 | 2020: +0.159 | 2021: +0.162 | 2022: +0.052 | 2023: +0.086
- IC CV=0.45, Neg years=0/8, Half ratio=0.70, Recency ratio=0.67
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.013, Q3_mid=+0.142, Q4=+0.164, Q5_high_vol=+0.183

**`combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0872, Sharpe=-0.2020)
- Yearly ICs: 2016: +0.099 | 2017: +0.226 | 2018: +0.241 | 2019: +0.146 | 2020: +0.142 | 2021: +0.168 | 2022: +0.091 | 2023: +0.108
- IC CV=0.35, Neg years=0/8, Half ratio=0.74, Recency ratio=0.61
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.234, Q2=-0.019, Q3_mid=+0.145, Q4=+0.172, Q5_high_vol=+0.189

**`combo_min__volatility_expansion_trend_vector__close_vs_open_range`** (Lock IC=+0.0848, Sharpe=-0.2413)
- Yearly ICs: 2016: +0.069 | 2017: +0.198 | 2018: +0.116 | 2019: +0.066 | 2020: +0.094 | 2021: +0.069 | 2022: +0.094 | 2023: +0.091
- IC CV=0.41, Neg years=0/8, Half ratio=0.82, Recency ratio=0.69
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.025, Q3_mid=+0.098, Q4=+0.091, Q5_high_vol=+0.133

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0833, Sharpe=-0.0910)
- Yearly ICs: 2016: +0.060 | 2017: +0.075 | 2018: +0.174 | 2019: +0.093 | 2020: +0.072 | 2021: +0.143 | 2022: +0.071 | 2023: +0.051
- IC CV=0.44, Neg years=0/8, Half ratio=0.84, Recency ratio=0.90
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.148, Q2=-0.033, Q3_mid=+0.091, Q4=+0.145, Q5_high_vol=+0.108

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0818, Sharpe=-0.1349)
- Yearly ICs: 2016: +0.094 | 2017: +0.257 | 2018: +0.230 | 2019: +0.145 | 2020: +0.132 | 2021: +0.089 | 2022: +0.091 | 2023: +0.045
- IC CV=0.51, Neg years=0/8, Half ratio=0.50, Recency ratio=0.39
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.060, Q3_mid=+0.140, Q4=+0.161, Q5_high_vol=+0.151

**`max_up_ret`** (Lock IC=+0.0813, Sharpe=-0.0733)
- Yearly ICs: 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104
- IC CV=0.30, Neg years=0/8, Half ratio=0.93, Recency ratio=0.64
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.009, Q3_mid=+0.112, Q4=+0.124, Q5_high_vol=+0.222

**`combo_max__close_vs_open_range__first_bar_return`** (Lock IC=+0.0749, Sharpe=-0.2700)
- Yearly ICs: 2016: +0.109 | 2017: +0.209 | 2018: +0.218 | 2019: +0.101 | 2020: +0.141 | 2021: +0.125 | 2022: +0.123 | 2023: +0.085
- IC CV=0.33, Neg years=0/8, Half ratio=0.82, Recency ratio=0.66
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.213, Q2=-0.015, Q3_mid=+0.149, Q4=+0.150, Q5_high_vol=+0.167

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0607, Sharpe=-0.1655)
- Yearly ICs: 2016: +0.077 | 2017: +0.214 | 2018: +0.161 | 2019: +0.117 | 2020: +0.170 | 2021: +0.048 | 2022: +0.113 | 2023: +0.117
- IC CV=0.39, Neg years=0/8, Half ratio=0.84, Recency ratio=0.79
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.007, Q3_mid=+0.154, Q4=+0.122, Q5_high_vol=+0.167

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0591, Sharpe=-0.7835)
- Yearly ICs: 2016: +0.128 | 2017: +0.155 | 2018: +0.225 | 2019: +0.082 | 2020: +0.136 | 2021: +0.102 | 2022: +0.108 | 2023: +0.081
- IC CV=0.35, Neg years=0/8, Half ratio=0.74, Recency ratio=0.67
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.012, Q3_mid=+0.126, Q4=+0.163, Q5_high_vol=+0.157

**`combo_rank_max__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0585, Sharpe=-0.0658)
- Yearly ICs: 2016: +0.039 | 2017: +0.087 | 2018: +0.188 | 2019: +0.136 | 2020: +0.045 | 2021: +0.102 | 2022: +0.073 | 2023: +0.040
- IC CV=0.55, Neg years=0/8, Half ratio=0.54, Recency ratio=0.90
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.170, Q2=-0.053, Q3_mid=+0.076, Q4=+0.166, Q5_high_vol=+0.088

**`vwap_close_divergence_trend`** (Lock IC=+0.0582, Sharpe=-0.5326)
- Yearly ICs: 2016: +0.023 | 2017: +0.184 | 2018: +0.055 | 2019: +0.091 | 2020: +0.075 | 2021: +0.069 | 2022: +0.094 | 2023: +0.107
- IC CV=0.50, Neg years=0/8, Half ratio=1.21, Recency ratio=0.97
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.016, Q3_mid=+0.092, Q4=+0.055, Q5_high_vol=+0.119

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0557, Sharpe=-0.0463)
- Yearly ICs: 2016: +0.120 | 2017: +0.118 | 2018: +0.283 | 2019: +0.095 | 2020: +0.105 | 2021: +0.084 | 2022: +0.101 | 2023: +0.039
- IC CV=0.56, Neg years=0/8, Half ratio=0.56, Recency ratio=0.59
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.037, Q3_mid=+0.067, Q4=+0.127, Q5_high_vol=+0.184

**`combo_sig_product__opening_auction_imbalance__first_bar_return`** (Lock IC=+0.0538, Sharpe=-0.3051)
- Yearly ICs: 2016: +0.038 | 2017: +0.152 | 2018: +0.198 | 2019: +0.108 | 2020: +0.065 | 2021: +0.056 | 2022: +0.041 | 2023: +0.052
- IC CV=0.62, Neg years=0/8, Half ratio=0.40, Recency ratio=0.49
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.176, Q2=-0.038, Q3_mid=+0.059, Q4=+0.148, Q5_high_vol=+0.086

### 159915ETF — `single` Median Features

**`combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1298, Sharpe=-0.2127)
- Yearly ICs: 2016: -0.013 | 2017: -0.005 | 2018: +0.091 | 2019: +0.175 | 2020: +0.098 | 2021: +0.137 | 2022: +0.146 | 2023: +0.111
- IC CV=0.69, Neg years=2/8, Half ratio=1.97, Recency ratio=-14.53
- Weak component: `demark_setup_reversal_early` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.126, Q3_mid=+0.078, Q4=+0.117, Q5_high_vol=+0.127

**`combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1212, Sharpe=-0.0863)
- Yearly ICs: 2016: +0.173 | 2017: -0.009 | 2018: +0.126 | 2019: +0.151 | 2020: +0.147 | 2021: +0.141 | 2022: +0.146 | 2023: +0.110
- IC CV=0.43, Neg years=1/8, Half ratio=1.28, Recency ratio=1.56
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.099, Q3_mid=+0.080, Q4=+0.142, Q5_high_vol=+0.175

**`combo_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1067, Sharpe=-0.1148)
- Yearly ICs: 2016: +0.004 | 2017: -0.050 | 2018: +0.063 | 2019: +0.108 | 2020: +0.072 | 2021: +0.020 | 2022: +0.158 | 2023: +0.110
- IC CV=1.03, Neg years=1/8, Half ratio=2.02, Recency ratio=-5.79
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.114, Q3_mid=+0.017, Q4=+0.086, Q5_high_vol=+0.100

**`combo_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0674, Sharpe=-0.2641)
- Yearly ICs: 2016: +0.073 | 2017: +0.042 | 2018: +0.065 | 2019: +0.114 | 2020: +0.116 | 2021: +0.149 | 2022: +0.125 | 2023: +0.172
- IC CV=0.39, Neg years=0/8, Half ratio=2.49, Recency ratio=2.58
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.125, Q3_mid=+0.090, Q4=+0.088, Q5_high_vol=+0.151

**`combo_rank_max__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0575, Sharpe=-0.6942)
- Yearly ICs: 2016: -0.002 | 2017: +0.035 | 2018: +0.034 | 2019: +0.050 | 2020: +0.103 | 2021: +0.145 | 2022: +0.072 | 2023: +0.155
- IC CV=0.71, Neg years=1/8, Half ratio=5.34, Recency ratio=7.01
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.068, Q3_mid=+0.068, Q4=+0.073, Q5_high_vol=+0.107

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0645, Sharpe=+0.5284)
- Yearly ICs: 2016: +0.073 | 2017: -0.032 | 2018: +0.181 | 2019: +0.145 | 2020: +0.038 | 2021: +0.130 | 2022: +0.045 | 2023: +0.154
- IC CV=0.74, Neg years=1/8, Half ratio=0.81, Recency ratio=4.83
- Weak component: `star50_limit_proximity_early` (CV=1.24)

**`combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0270, Sharpe=+0.1230)
- Yearly ICs: 2016: +0.110 | 2017: -0.075 | 2018: +0.168 | 2019: +0.086 | 2020: +0.075 | 2021: +0.151 | 2022: +0.094 | 2023: +0.092
- IC CV=0.78, Neg years=1/8, Half ratio=1.27, Recency ratio=5.19
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)

### 500ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0972, Sharpe=+0.7833)
- Yearly ICs: 2016: +0.095 | 2017: +0.215 | 2018: +0.202 | 2019: +0.177 | 2020: +0.143 | 2021: +0.100 | 2022: +0.039 | 2023: +0.081
- IC CV=0.45, Neg years=0/8, Half ratio=0.51, Recency ratio=0.39
- Weak component: `bar_ret_0` (CV=0.46)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1193, Sharpe=+0.7763)
- Yearly ICs: 2016: +0.101 | 2017: +0.233 | 2018: +0.130 | 2019: +0.099 | 2020: +0.135 | 2021: +0.115 | 2022: +0.052 | 2023: +0.094
- IC CV=0.41, Neg years=0/8, Half ratio=0.74, Recency ratio=0.44
- Weak component: `volatility_expansion_trend_vector` (CV=0.41)

**`combo_min__opening_auction_imbalance__star50_limit_proximity_early`** (Lock IC=+0.1235, Sharpe=+0.7688)
- Yearly ICs: 2016: +0.062 | 2017: +0.229 | 2018: +0.101 | 2019: +0.126 | 2020: +0.120 | 2021: +0.096 | 2022: +0.062 | 2023: +0.082
- IC CV=0.46, Neg years=0/8, Half ratio=0.69, Recency ratio=0.50
- Weak component: `star50_limit_proximity_early` (CV=0.55)

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0926, Sharpe=+0.7209)
- Yearly ICs: 2016: +0.088 | 2017: +0.218 | 2018: +0.206 | 2019: +0.175 | 2020: +0.133 | 2021: +0.089 | 2022: +0.045 | 2023: +0.078
- IC CV=0.47, Neg years=0/8, Half ratio=0.50, Recency ratio=0.40
- Weak component: `bar_ret_0` (CV=0.46)

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0855, Sharpe=+0.5052)
- Yearly ICs: 2016: +0.101 | 2017: +0.199 | 2018: +0.218 | 2019: +0.146 | 2020: +0.162 | 2021: +0.137 | 2022: +0.068 | 2023: +0.105
- IC CV=0.33, Neg years=0/8, Half ratio=0.72, Recency ratio=0.58
- Weak component: `body_size_progression` (CV=0.60)

**`combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`** (Lock IC=+0.0876, Sharpe=+0.4478)
- Yearly ICs: 2016: +0.034 | 2017: +0.193 | 2018: +0.175 | 2019: +0.153 | 2020: +0.142 | 2021: +0.129 | 2022: +0.036 | 2023: +0.095
- IC CV=0.47, Neg years=0/8, Half ratio=0.69, Recency ratio=0.57
- Weak component: `late_bar_momentum` (CV=0.60)

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1093, Sharpe=+0.4426)
- Yearly ICs: 2016: +0.035 | 2017: +0.230 | 2018: +0.096 | 2019: +0.112 | 2020: +0.112 | 2021: +0.045 | 2022: +0.059 | 2023: +0.041
- IC CV=0.66, Neg years=0/8, Half ratio=0.55, Recency ratio=0.37
- Weak component: `max_down_ret` (CV=0.62)

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1046, Sharpe=+0.4052)
- Yearly ICs: 2016: +0.047 | 2017: +0.237 | 2018: +0.114 | 2019: +0.124 | 2020: +0.126 | 2021: +0.076 | 2022: +0.053 | 2023: +0.062
- IC CV=0.55, Neg years=0/8, Half ratio=0.57, Recency ratio=0.40
- Weak component: `max_down_ret` (CV=0.62)

**`combo_z_sum__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0982, Sharpe=+0.3203)
- Yearly ICs: 2016: +0.091 | 2017: +0.194 | 2018: +0.174 | 2019: +0.140 | 2020: +0.118 | 2021: +0.094 | 2022: +0.077 | 2023: +0.032
- IC CV=0.43, Neg years=0/8, Half ratio=0.54, Recency ratio=0.38
- Weak component: `max_down_ret` (CV=0.62)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1193, Sharpe=+0.2422)
- Yearly ICs: 2016: +0.120 | 2017: +0.225 | 2018: +0.180 | 2019: +0.173 | 2020: +0.172 | 2021: +0.143 | 2022: +0.006 | 2023: +0.103
- IC CV=0.44, Neg years=0/8, Half ratio=0.66, Recency ratio=0.32
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1566, Sharpe=+0.2157)
- Yearly ICs: 2016: +0.046 | 2017: +0.193 | 2018: +0.147 | 2019: +0.180 | 2020: +0.113 | 2021: +0.083 | 2022: +0.063 | 2023: +0.096
- IC CV=0.44, Neg years=0/8, Half ratio=0.51, Recency ratio=0.67
- Weak component: `max_down_ret` (CV=0.62)

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0955, Sharpe=+0.2044)
- Yearly ICs: 2016: +0.112 | 2017: +0.195 | 2018: +0.204 | 2019: +0.085 | 2020: +0.161 | 2021: +0.081 | 2022: +0.116 | 2023: +0.089
- IC CV=0.36, Neg years=0/8, Half ratio=0.80, Recency ratio=0.67
- Weak component: `trend_bar_close_consistency` (CV=0.66)

**`combo_rank_min__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0999, Sharpe=+0.1009)
- Yearly ICs: 2016: +0.078 | 2017: +0.240 | 2018: +0.133 | 2019: +0.098 | 2020: +0.145 | 2021: +0.056 | 2022: +0.084 | 2023: +0.076
- IC CV=0.49, Neg years=0/8, Half ratio=0.68, Recency ratio=0.51
- Weak component: `max_down_ret` (CV=0.62)

**`combo_rel_diff__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0869, Sharpe=+0.0875)
- Yearly ICs: 2016: +0.084 | 2017: +0.127 | 2018: +0.240 | 2019: +0.171 | 2020: +0.183 | 2021: +0.167 | 2022: +0.040 | 2023: +0.091
- IC CV=0.44, Neg years=0/8, Half ratio=0.80, Recency ratio=0.62
- Weak component: `smooth_momentum_structure` (CV=0.62)

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0910, Sharpe=+0.0732)
- Yearly ICs: 2016: +0.077 | 2017: +0.226 | 2018: +0.202 | 2019: +0.110 | 2020: +0.154 | 2021: +0.112 | 2022: +0.087 | 2023: +0.122
- IC CV=0.37, Neg years=0/8, Half ratio=0.81, Recency ratio=0.69
- Weak component: `trend_bar_close_consistency` (CV=0.66)

**`combo_max__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.0916, Sharpe=+0.0703)
- Yearly ICs: 2016: +0.064 | 2017: +0.118 | 2018: +0.146 | 2019: +0.082 | 2020: +0.082 | 2021: +0.030 | 2022: +0.118 | 2023: +0.072
- IC CV=0.39, Neg years=0/8, Half ratio=0.74, Recency ratio=1.05
- Weak component: `star50_limit_proximity_early` (CV=0.55)

### 159915ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1316, Sharpe=+1.2887)
- Yearly ICs: 2016: +0.125 | 2017: +0.004 | 2018: +0.128 | 2019: +0.223 | 2020: +0.061 | 2021: +0.180 | 2022: +0.048 | 2023: +0.147
- IC CV=0.59, Neg years=0/8, Half ratio=0.94, Recency ratio=1.51
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1246, Sharpe=+1.2584)
- Yearly ICs: 2016: +0.073 | 2017: -0.019 | 2018: +0.104 | 2019: +0.257 | 2020: +0.125 | 2021: +0.113 | 2022: +0.079 | 2023: +0.149
- IC CV=0.66, Neg years=1/8, Half ratio=1.06, Recency ratio=4.21
- Weak component: `star50_limit_proximity_early` (CV=0.68)

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1181, Sharpe=+1.2510)
- Yearly ICs: 2016: +0.147 | 2017: -0.003 | 2018: +0.184 | 2019: +0.218 | 2020: +0.158 | 2021: +0.163 | 2022: +0.108 | 2023: +0.137
- IC CV=0.44, Neg years=1/8, Half ratio=1.04, Recency ratio=1.70
- Weak component: `bar_body_rng_0` (CV=0.54)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1156, Sharpe=+1.1752)
- Yearly ICs: 2016: +0.129 | 2017: +0.008 | 2018: +0.113 | 2019: +0.209 | 2020: +0.159 | 2021: +0.161 | 2022: +0.132 | 2023: +0.165
- IC CV=0.41, Neg years=0/8, Half ratio=1.44, Recency ratio=2.17
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)

**`combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1020, Sharpe=+1.0549)
- Yearly ICs: 2016: +0.050 | 2017: -0.027 | 2018: +0.120 | 2019: +0.226 | 2020: +0.132 | 2021: +0.107 | 2022: +0.081 | 2023: +0.052
- IC CV=0.74, Neg years=1/8, Half ratio=0.91, Recency ratio=5.83
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)

**`combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1273, Sharpe=+0.9833)
- Yearly ICs: 2016: +0.037 | 2017: -0.006 | 2018: +0.045 | 2019: +0.157 | 2020: +0.091 | 2021: +0.148 | 2022: +0.119 | 2023: +0.165
- IC CV=0.63, Neg years=1/8, Half ratio=2.28, Recency ratio=9.21
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)

**`combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1284, Sharpe=+0.9565)
- Yearly ICs: 2016: +0.065 | 2017: +0.040 | 2018: +0.108 | 2019: +0.112 | 2020: +0.057 | 2021: +0.163 | 2022: +0.116 | 2023: +0.145
- IC CV=0.40, Neg years=0/8, Half ratio=1.61, Recency ratio=2.48
- Weak component: `impulse_bar_dominance` (CV=1.04)

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1192, Sharpe=+0.8728)
- Yearly ICs: 2016: -0.014 | 2017: -0.013 | 2018: +0.074 | 2019: +0.221 | 2020: +0.103 | 2021: +0.110 | 2022: +0.094 | 2023: +0.159
- IC CV=0.81, Neg years=2/8, Half ratio=1.49, Recency ratio=-9.71
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)

**`combo_ratio__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1348, Sharpe=+0.8488)
- Yearly ICs: 2016: +0.009 | 2017: -0.012 | 2018: +0.072 | 2019: +0.170 | 2020: +0.085 | 2021: +0.112 | 2022: +0.141 | 2023: +0.103
- IC CV=0.68, Neg years=1/8, Half ratio=1.80, Recency ratio=-87.61
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_mean__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1330, Sharpe=+0.8015)
- Yearly ICs: 2016: +0.105 | 2017: -0.075 | 2018: +0.110 | 2019: +0.118 | 2020: +0.092 | 2021: +0.055 | 2022: +0.169 | 2023: +0.133
- IC CV=0.78, Neg years=1/8, Half ratio=1.49, Recency ratio=10.17
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_rel_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1094, Sharpe=+0.7442)
- Yearly ICs: 2016: +0.066 | 2017: +0.016 | 2018: +0.133 | 2019: +0.209 | 2020: +0.115 | 2021: +0.153 | 2022: +0.119 | 2023: +0.144
- IC CV=0.45, Neg years=0/8, Half ratio=1.30, Recency ratio=3.19
- Weak component: `demark_setup_reversal_early` (CV=0.76)

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1085, Sharpe=+0.6332)
- Yearly ICs: 2016: +0.055 | 2017: +0.019 | 2018: +0.072 | 2019: +0.188 | 2020: +0.090 | 2021: +0.157 | 2022: +0.143 | 2023: +0.153
- IC CV=0.50, Neg years=0/8, Half ratio=1.86, Recency ratio=4.00
- Weak component: `demark_setup_reversal_early` (CV=0.76)

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1274, Sharpe=+0.5997)
- Yearly ICs: 2016: +0.084 | 2017: +0.032 | 2018: +0.063 | 2019: +0.152 | 2020: +0.122 | 2021: +0.158 | 2022: +0.149 | 2023: +0.132
- IC CV=0.39, Neg years=0/8, Half ratio=1.77, Recency ratio=2.44
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)

**`combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0486, Sharpe=+0.5769)
- Yearly ICs: 2016: +0.141 | 2017: +0.020 | 2018: +0.109 | 2019: +0.129 | 2020: +0.023 | 2021: -0.037 | 2022: +0.058 | 2023: +0.020
- IC CV=1.02, Neg years=1/8, Half ratio=0.21, Recency ratio=0.48
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1236, Sharpe=+0.5605)
- Yearly ICs: 2016: +0.103 | 2017: +0.037 | 2018: +0.112 | 2019: +0.155 | 2020: +0.064 | 2021: +0.163 | 2022: +0.158 | 2023: +0.133
- IC CV=0.37, Neg years=0/8, Half ratio=1.49, Recency ratio=2.06
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1235, Sharpe=+0.5461)
- Yearly ICs: 2016: +0.113 | 2017: -0.018 | 2018: +0.194 | 2019: +0.243 | 2020: +0.166 | 2021: +0.154 | 2022: +0.098 | 2023: +0.185
- IC CV=0.52, Neg years=1/8, Half ratio=1.10, Recency ratio=2.98
- Weak component: `bar_body_rng_0` (CV=0.54)

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1243, Sharpe=+0.5212)
- Yearly ICs: 2016: +0.102 | 2017: -0.036 | 2018: +0.096 | 2019: +0.088 | 2020: +0.077 | 2021: +0.065 | 2022: +0.130 | 2023: +0.152
- IC CV=0.62, Neg years=1/8, Half ratio=1.59, Recency ratio=4.28
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.0911, Sharpe=+0.3186)
- Yearly ICs: 2016: +0.107 | 2017: -0.042 | 2018: +0.148 | 2019: +0.125 | 2020: +0.143 | 2021: +0.061 | 2022: +0.184 | 2023: +0.110
- IC CV=0.62, Neg years=1/8, Half ratio=1.30, Recency ratio=4.55
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0804, Sharpe=+0.2268)
- Yearly ICs: 2016: -0.016 | 2017: +0.002 | 2018: +0.043 | 2019: +0.038 | 2020: +0.119 | 2021: +0.140 | 2022: +0.129 | 2023: +0.121
- IC CV=0.81, Neg years=1/8, Half ratio=10.68, Recency ratio=-17.64
- Weak component: `impulse_bar_dominance` (CV=1.04)

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0874, Sharpe=+0.1633)
- Yearly ICs: 2016: +0.087 | 2017: +0.027 | 2018: +0.117 | 2019: +0.128 | 2020: +0.091 | 2021: +0.177 | 2022: +0.156 | 2023: +0.131
- IC CV=0.38, Neg years=0/8, Half ratio=1.69, Recency ratio=2.54
- Weak component: `star50_limit_proximity_early` (CV=0.68)

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0879, Sharpe=+0.1448)
- Yearly ICs: 2016: +0.072 | 2017: +0.030 | 2018: +0.091 | 2019: +0.172 | 2020: +0.096 | 2021: +0.116 | 2022: +0.093 | 2023: +0.192
- IC CV=0.45, Neg years=0/8, Half ratio=1.46, Recency ratio=2.78
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0872, Sharpe=+0.0736)
- Yearly ICs: 2016: +0.141 | 2017: +0.001 | 2018: +0.083 | 2019: +0.181 | 2020: +0.124 | 2021: +0.161 | 2022: +0.107 | 2023: +0.156
- IC CV=0.45, Neg years=0/8, Half ratio=1.46, Recency ratio=1.85
- Weak component: `bar_body_rng_0` (CV=0.54)

**`combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1273, Sharpe=+0.0566)
- Yearly ICs: 2016: +0.050 | 2017: +0.034 | 2018: +0.054 | 2019: +0.131 | 2020: +0.104 | 2021: +0.109 | 2022: +0.148 | 2023: +0.133
- IC CV=0.43, Neg years=0/8, Half ratio=2.10, Recency ratio=3.36
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)

**`combo_rank_max__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.0753, Sharpe=+0.0409)
- Yearly ICs: 2016: +0.104 | 2017: -0.025 | 2018: +0.101 | 2019: +0.165 | 2020: +0.151 | 2021: +0.108 | 2022: +0.081 | 2023: +0.067
- IC CV=0.58, Neg years=1/8, Half ratio=1.13, Recency ratio=1.88
- Weak component: `first_bar_sentiment` (CV=0.76)

**`combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1090, Sharpe=+0.0124)
- Yearly ICs: 2016: +0.041 | 2017: -0.049 | 2018: +0.074 | 2019: +0.133 | 2020: +0.100 | 2021: +0.044 | 2022: +0.182 | 2023: +0.111
- IC CV=0.82, Neg years=1/8, Half ratio=1.76, Recency ratio=-34.61
- Weak component: `yesterday_first_30min_return` (CV=0.92)

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Median | gradual | +0.1120 | +0.0212 | -0.0888 | 1y |
| `combo_mean__volume_weighted_price_position__double_bottom_bull_flag_early` | Median | persistent | +0.0761 | +0.0533 | +0.0116 | 2y |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Median | gradual | +0.0615 | +0.0893 | -0.1475 | 2y |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | FP | gradual | +0.0576 | +0.0341 | -0.1722 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0563 | +0.0495 | -0.0265 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | gradual | +0.0511 | +0.0477 | -0.0312 | 2y |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0443 | +0.0992 | +0.0265 | ∞ |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Median | gradual | +0.0365 | +0.0437 | -0.1087 | 2y |
| `combo_max__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0296 | +0.0967 | -0.1987 | 2y |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | gradual | +0.0268 | +0.0354 | -0.0986 | 2y |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0258 | +0.0420 | -0.0021 | 2y |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | FP | gradual | +0.0251 | +0.0017 | -0.0855 | 1y |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Median | gradual | +0.0155 | +0.1053 | -0.0733 | 2y |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0145 | +0.0760 | -0.0984 | 2y |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0107 | +0.1002 | -0.1508 | 2y |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | gradual | +0.0003 | +0.0910 | -0.2032 | ∞ |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Median | immediate | -0.0044 | +0.1224 | -0.1415 | ∞ |
| `combo_rank_max__bar_ret_0__first_bar_sentiment` | FP | immediate | -0.0195 | +0.0639 | -0.0831 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0247 | +0.0663 | -0.1086 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Median | immediate | -0.0254 | +0.0749 | +0.0648 | ∞ |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Median | immediate | -0.0628 | +0.0683 | +0.1244 | ∞ |

**Decay distribution**: immediate=5, fast(1-2y)=0, gradual=14, persistent=2

**FP decay trajectories:**

- `combo_rank_max__max_up_ret__first_bar_sentiment`: Y1:-0.025 → Y2:+0.066 → Y3:-0.109
- `combo_rank_max__bar_ret_0__first_bar_sentiment`: Y1:-0.020 → Y2:+0.064 → Y3:-0.083
- `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.000 → Y2:+0.091 → Y3:-0.203
- `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio`: Y1:+0.025 → Y2:+0.002 → Y3:-0.085
- `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.027 → Y2:+0.035 → Y3:-0.099
- `combo_max__max_up_ret__volume_weighted_price_position`: Y1:+0.030 → Y2:+0.097 → Y3:-0.199
- `combo_min__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.058 → Y2:+0.034 → Y3:-0.172

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1590 | +0.1063 | +0.1978 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1587 | +0.0925 | +0.0908 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Median | gradual | +0.1516 | +0.0889 | -0.0079 | 2y |
| `max_up_ret` | Median | gradual | +0.1427 | +0.0801 | -0.0291 | 2y |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | TP | persistent | +0.1417 | +0.0595 | +0.0396 | 1y |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | TP | persistent | +0.1385 | +0.1357 | +0.0880 | ∞ |
| `combo_max__close_vs_open_range__first_bar_return` | Median | gradual | +0.1359 | +0.1213 | -0.0914 | 2y |
| `combo_z_sum__opening_drive_thrust_ratio__max_down_ret` | Median | persistent | +0.1356 | +0.1097 | +0.0226 | 2y |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1356 | +0.0212 | +0.0758 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | TP | gradual | +0.1330 | +0.1324 | -0.0522 | 2y |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Median | gradual | +0.1300 | +0.0741 | -0.0035 | 2y |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | Median | persistent | +0.1264 | +0.0968 | +0.0042 | 2y |
| `combo_max__bar_ret_0__max_down_ret` | Median | persistent | +0.1244 | +0.1076 | +0.0004 | 2y |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Median | persistent | +0.1222 | +0.1093 | +0.0044 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1202 | +0.1407 | +0.0686 | ∞ |
| `combo_min__volatility_expansion_trend_vector__close_vs_open_range` | Median | gradual | +0.1187 | +0.1437 | -0.0747 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | TP | gradual | +0.1166 | +0.1389 | -0.0149 | 2y |
| `combo_z_sum__first_bar_sentiment__max_down_ret` | TP | persistent | +0.1151 | +0.1330 | +0.0242 | 2y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | gradual | +0.1139 | +0.1244 | -0.1147 | 2y |
| `combo_sig_product__max_up_ret__first_bar_return` | Median | gradual | +0.1013 | +0.0769 | -0.0792 | 2y |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | TP | persistent | +0.1013 | +0.0472 | +0.1097 | 1y |
| `combo_max__star50_limit_proximity_early__early_body_momentum` | TP | persistent | +0.1010 | +0.0986 | +0.0498 | 2y |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1007 | +0.0966 | +0.1228 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | gradual | +0.0968 | +0.1016 | -0.0804 | 2y |
| `vwap_close_divergence_trend` | Median | gradual | +0.0918 | +0.1327 | -0.0940 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0908 | +0.1262 | +0.0854 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0889 | +0.1203 | +0.0797 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0866 | +0.1395 | +0.1038 | ∞ |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | Median | persistent | +0.0858 | +0.0437 | +0.0175 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0853 | +0.1336 | +0.0332 | 2y |
| `combo_sig_product__opening_auction_imbalance__first_bar_return` | Median | gradual | +0.0638 | +0.1279 | -0.0827 | 2y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=12, persistent=19

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1323 | +0.1412 | +0.0738 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1289 | +0.0717 | +0.1499 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1269 | +0.1640 | +0.0657 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1267 | +0.1392 | +0.1129 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1247 | +0.1135 | +0.1174 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1168 | +0.1247 | +0.1472 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1153 | +0.1681 | +0.0618 | ∞ |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1038 | +0.1081 | +0.1782 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0999 | +0.1726 | -0.0587 | 2y |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0972 | +0.1937 | +0.0566 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Median | persistent | +0.0912 | +0.1511 | +0.1250 | ∞ |
| `combo_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0891 | +0.1540 | +0.1046 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0885 | +0.1187 | +0.0086 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0847 | +0.1690 | +0.0625 | ∞ |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.0820 | +0.1709 | +0.0454 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.0787 | +0.1628 | +0.0825 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.0779 | +0.1403 | +0.1523 | ∞ |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0778 | +0.1387 | +0.0217 | 2y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.0775 | +0.1848 | +0.0010 | 2y |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0752 | +0.1956 | +0.0682 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.0737 | +0.0720 | +0.0812 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0719 | +0.1276 | +0.1211 | ∞ |
| `combo_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.0719 | +0.1280 | +0.1150 | ∞ |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Median | gradual | +0.0682 | +0.1393 | -0.0681 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0674 | +0.1701 | +0.0868 | ∞ |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0663 | +0.0938 | +0.1351 | ∞ |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | Median | gradual | +0.0606 | +0.1081 | -0.0435 | 2y |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0601 | +0.1915 | -0.0566 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0546 | +0.0855 | +0.1440 | ∞ |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | immediate | -0.0206 | +0.0512 | +0.1070 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=4, persistent=25

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.724±0.048 | 0.704±0.009 | 13% | USEFUL |
| ic_ir | 0.596±0.122 | 0.591±0.012 | 6% | USEFUL |
| p_value | 0.000±0.001 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.824±0.024 | 0.809±0.040 | 76% | WEAK |
| deflated_ic | 0.199±0.025 | 0.231±0.004 | 9% | USEFUL |
| overall_ic | 0.199±0.025 | 0.231±0.004 | 9% | USEFUL |
| raw_ic | 0.087±0.005 | 0.098±0.003 | 0% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 2/20 top rejects are profitable (10%)

- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.1003
- `combo_z_sum__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.1003

**BH-FDR Gate**: 1/10 top rejects are profitable (10%)

- `combo_max__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0814, Lock IC=+0.0326, Sharpe=+0.2087

**B3 Composite Floor**: 2/20 top rejects are profitable (10%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2251, Lock IC=+0.0254, Sharpe=+0.1308
- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Sharpe=+0.1230

**B4 Correlation Gate**: 2/20 top rejects are profitable (10%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2249, Lock IC=+0.0346, Sharpe=+0.8154
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2492, Lock IC=+0.0505, Sharpe=+0.3436

### 500ETF — `single`

**7-Year Jackknife**: 16/20 top rejects are profitable (80%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2706, Lock IC=+0.1225, Sharpe=+0.9860
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Sharpe=+0.8086
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Sharpe=+0.7825

**B2 Rolling Guard**: 10/20 top rejects are profitable (50%)

- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Sharpe=+0.5034
- `combo_tri_z_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Sharpe=+0.5034
- `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__volume_weighted_momentum_acceleration`: Train IC=+0.1765, Lock IC=+0.0288, Sharpe=+0.3345

**BH-FDR Gate**: 2/12 top rejects are profitable (17%)

- `combo_tri_median__max_up_ret__smooth_momentum_structure__trend_day_regime_conviction`: Train IC=+0.0891, Lock IC=+0.0815, Sharpe=+1.1272
- `vol_ratio_10_60`: Train IC=+0.0761, Lock IC=+0.0275, Sharpe=+0.2531

**B3 Composite Floor**: 14/20 top rejects are profitable (70%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2415, Lock IC=+0.1182, Sharpe=+0.8786
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2414, Lock IC=+0.1134, Sharpe=+0.6142
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2414, Lock IC=+0.1134, Sharpe=+0.6142

**B4 Correlation Gate**: 11/20 top rejects are profitable (55%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2665, Lock IC=+0.1105, Sharpe=+0.5932
- `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2566, Lock IC=+0.0857, Sharpe=+0.5044
- `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2513, Lock IC=+0.0874, Sharpe=+0.5044

### 159915ETF — `single`

**7-Year Jackknife**: 14/20 top rejects are profitable (70%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1899, Lock IC=+0.1399, Sharpe=+1.2423
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1899, Lock IC=+0.1399, Sharpe=+1.2423
- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.1924, Lock IC=+0.1128, Sharpe=+1.0445

**B2 Rolling Guard**: 17/20 top rejects are profitable (85%)

- `combo_mean__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1514, Lock IC=+0.0813, Sharpe=+0.9788
- `combo_z_sum__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1514, Lock IC=+0.0813, Sharpe=+0.9788
- `combo_mean__first_bar_return__volume_weighted_price_position`: Train IC=+0.1523, Lock IC=+0.0775, Sharpe=+0.6978

**BH-FDR Gate**: 4/9 top rejects are profitable (44%)

- `combo_sig_product__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.0665, Lock IC=+0.0430, Sharpe=+0.1390
- `combo_sig_product__yesterday_first_30min_return__limit_down_proximity_early`: Train IC=+0.0665, Lock IC=+0.0430, Sharpe=+0.1390
- `vol_gk20`: Train IC=+0.0370, Lock IC=+0.0210, Sharpe=+0.0601

**B3 Composite Floor**: 15/20 top rejects are profitable (75%)

- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2508, Lock IC=+0.1290, Sharpe=+1.3284
- `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2522, Lock IC=+0.1236, Sharpe=+1.2838
- `combo_tri_z_mean__max_up_ret__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2522, Lock IC=+0.1236, Sharpe=+1.2838

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.5260
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2816, Lock IC=+0.1330, Sharpe=+1.2412
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2829, Lock IC=+0.1357, Sharpe=+1.2218

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is higher (d=+1.85). Threshold 0.800 → 89% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-1.76). Threshold 0.027 → 67% accuracy.
- `weak_link_cv`: FP is lower (d=-1.69). Threshold 0.763 → 67% accuracy.
- `n_negative_years`: FP is higher (d=+0.83). Threshold 0.500 → 67% accuracy.
- `recency_ratio`: FP is lower (d=-0.73). Threshold -13.817 → 67% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/7
- Decaying signal (half ratio < 0.3): 0/7
- Weak component (CV > 2.0): 0/7
- Regime-dependent (≥2 negative regimes): 0/7

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_weighted_price_position` | 3 | 2 | 5 | 60% |  |
| `bar_ret_0` | 2 | 2 | 4 | 50% |  |
| `first_bar_sentiment` | 2 | 3 | 5 | 40% |  |
| `opening_drive_thrust_ratio` | 4 | 7 | 11 | 36% |  |
| `max_up_ret` | 3 | 13 | 16 | 19% |  |
| `max_down_ret` | 0 | 5 | 5 | 0% |  |
| `first_bar_return` | 0 | 4 | 4 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 2 | 2 | 0% |  |
| `demark_setup_reversal_early` | 0 | 2 | 2 | 0% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `impulse_bar_dominance` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 17 | 17 | 0% |  |
| `yesterday_first_30min_return` | 0 | 4 | 4 | 0% |  |
| `bar_body_rng_0` | 0 | 4 | 4 | 0% |  |
| `star50_limit_proximity_early` | 0 | 14 | 14 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 4 | 4 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=5, TP=24, FP rate=17%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=0, TP=3, FP rate=0%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=7, FP rate=0%

