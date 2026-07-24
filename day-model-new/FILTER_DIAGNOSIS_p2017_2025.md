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
| 300ETF | single | 19 | 8 | 11 | 0 | 42% | 0.15 |
| 500ETF | single | 32 | 2 | 23 | 7 | 6% | 0.43 |
| 159915ETF | single | 27 | 0 | 10 | 17 | 0% | 0.76 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 500ETF — `single` (FP=2, TP=7)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recency_ratio | 0.986 | 0.576 | 0.986 | 0.526 | +3.48 | 0.911 | 100% |
| ic_std_across_regimes | 0.034 | 0.070 | 0.034 | 0.067 | -2.75 | 0.091 | 67% |
| n_negative_years | 1.000 | 0.000 | 1.000 | 0.000 | +1.41 | 1.000 | 89% |
| half_ratio | -6.747 | 0.570 | -6.747 | 0.501 | -1.27 | 1.143 | 89% |
| ic_cv | 0.811 | 0.401 | 0.811 | 0.401 | +1.12 | 0.895 | 89% |
| n_negative_regimes | 1.000 | 0.429 | 1.000 | 0.000 | +0.72 | 1.500 | 89% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0315, Sharpe=-2.3158)
- Yearly ICs: 2017: +0.009 | 2018: +0.176 | 2019: +0.100 | 2020: +0.034 | 2021: +0.182 | 2022: +0.022 | 2023: +0.151 | 2024: +0.031
- IC CV=0.78, Neg years=0/8, Half ratio=1.36, Recency ratio=0.99
- Weak component: `first_bar_sentiment` (CV=1.06, neg years=2)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.108, Q3_mid=+0.034, Q4=+0.056, Q5_high_vol=+0.188

**`combo_mean__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0365, Sharpe=-2.1647)
- Yearly ICs: 2017: -0.034 | 2018: +0.160 | 2019: +0.072 | 2020: +0.053 | 2021: +0.175 | 2022: +0.015 | 2023: +0.160 | 2024: +0.064
- IC CV=0.85, Neg years=1/8, Half ratio=1.81, Recency ratio=1.78
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.085, Q3_mid=+0.028, Q4=+0.054, Q5_high_vol=+0.212

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0282, Sharpe=-2.0075)
- Yearly ICs: 2017: -0.041 | 2018: +0.138 | 2019: +0.113 | 2020: +0.035 | 2021: +0.173 | 2022: +0.000 | 2023: +0.187 | 2024: +0.024
- IC CV=1.01, Neg years=1/8, Half ratio=1.66, Recency ratio=2.18
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.003, Q2=+0.170, Q3_mid=+0.051, Q4=+0.115, Q5_high_vol=+0.065

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0223, Sharpe=-1.9107)
- Yearly ICs: 2017: +0.020 | 2018: +0.182 | 2019: +0.072 | 2020: -0.000 | 2021: +0.133 | 2022: +0.045 | 2023: +0.170 | 2024: +0.055
- IC CV=0.76, Neg years=1/8, Half ratio=1.46, Recency ratio=1.11
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.079, Q3_mid=+0.041, Q4=+0.072, Q5_high_vol=+0.177

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0391, Sharpe=-1.5357)
- Yearly ICs: 2017: +0.008 | 2018: +0.136 | 2019: +0.044 | 2020: +0.004 | 2021: +0.171 | 2022: +0.037 | 2023: +0.200 | 2024: +0.032
- IC CV=0.92, Neg years=0/8, Half ratio=2.68, Recency ratio=1.61
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.099, Q3_mid=-0.001, Q4=+0.042, Q5_high_vol=+0.183

**`combo_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=-0.0284, Sharpe=-1.4926)
- Yearly ICs: 2017: +0.034 | 2018: +0.192 | 2019: +0.044 | 2020: +0.043 | 2021: +0.166 | 2022: +0.020 | 2023: +0.162 | 2024: +0.115
- IC CV=0.67, Neg years=0/8, Half ratio=1.60, Recency ratio=1.23
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.084, Q3_mid=+0.059, Q4=+0.037, Q5_high_vol=+0.211

**`combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=-0.0056, Sharpe=-1.4567)
- Yearly ICs: 2017: -0.034 | 2018: +0.191 | 2019: +0.109 | 2020: +0.020 | 2021: +0.166 | 2022: +0.044 | 2023: +0.166 | 2024: +0.005
- IC CV=0.96, Neg years=1/8, Half ratio=1.38, Recency ratio=1.09
- Weak component: `first_bar_sentiment` (CV=1.06, neg years=2)
- Regime ICs: Q1_low_vol=+0.012, Q2=+0.112, Q3_mid=+0.038, Q4=+0.078, Q5_high_vol=+0.183

**`morning_volume_weighted_momentum`** (Lock IC=-0.0202, Sharpe=-0.8452)
- Yearly ICs: 2017: -0.097 | 2018: +0.060 | 2019: +0.016 | 2020: +0.033 | 2021: +0.153 | 2022: +0.045 | 2023: +0.123 | 2024: +0.053
- IC CV=1.45, Neg years=1/8, Half ratio=6.53, Recency ratio=-4.76
- Regime ICs: Q1_low_vol=+0.015, Q2=+0.057, Q3_mid=+0.002, Q4=+0.068, Q5_high_vol=+0.117

### 500ETF — `single` False Positives

**`early_order_flow_imbalance`** (Lock IC=-0.0041, Sharpe=-2.4279)
- Yearly ICs: 2017: +0.093 | 2018: +0.101 | 2019: +0.121 | 2020: +0.038 | 2021: +0.122 | 2022: +0.141 | 2023: +0.079 | 2024: +0.107
- IC CV=0.29, Neg years=0/8, Half ratio=1.40, Recency ratio=0.96
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.072, Q3_mid=+0.065, Q4=+0.113, Q5_high_vol=+0.095

**`vol_pk20`** (Lock IC=-0.0296, Sharpe=-1.4193)
- Yearly ICs: 2017: +0.075 | 2018: +0.101 | 2019: -0.033 | 2020: -0.078 | 2021: +0.047 | 2022: +0.188 | 2023: +0.052 | 2024: +0.127
- IC CV=1.33, Neg years=2/8, Half ratio=-14.89, Recency ratio=1.02
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.054, Q3_mid=-0.050, Q4=-0.002, Q5_high_vol=+0.031

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_rank_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0813, Sharpe=-0.1254)
- Yearly ICs: 2017: -0.039 | 2018: +0.157 | 2019: +0.133 | 2020: +0.031 | 2021: +0.124 | 2022: +0.029 | 2023: +0.133 | 2024: +0.038
- IC CV=0.86, Neg years=1/8, Half ratio=1.04, Recency ratio=1.45
- Weak component: `limit_down_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.064, Q3_mid=+0.070, Q4=+0.060, Q5_high_vol=+0.200

**`combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0753, Sharpe=-0.7047)
- Yearly ICs: 2017: -0.059 | 2018: +0.144 | 2019: +0.097 | 2020: +0.039 | 2021: +0.142 | 2022: +0.100 | 2023: +0.086 | 2024: -0.004
- IC CV=0.98, Neg years=2/8, Half ratio=1.48, Recency ratio=0.96
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=-0.001, Q2=+0.062, Q3_mid=+0.079, Q4=+0.058, Q5_high_vol=+0.154

**`combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=+0.0409, Sharpe=-0.7980)
- Yearly ICs: 2017: -0.003 | 2018: +0.026 | 2019: +0.036 | 2020: -0.032 | 2021: +0.045 | 2022: +0.060 | 2023: +0.115 | 2024: +0.077
- IC CV=1.06, Neg years=2/8, Half ratio=10.38, Recency ratio=8.54
- Weak component: `double_bottom_bull_flag_early` (CV=1.91)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.100, Q3_mid=-0.043, Q4=+0.084, Q5_high_vol=-0.008

**`combo_min__bar_body_rng_0__volume_surge_direction`** (Lock IC=+0.0300, Sharpe=-0.5586)
- Yearly ICs: 2017: -0.002 | 2018: +0.189 | 2019: +0.080 | 2020: +0.037 | 2021: +0.160 | 2022: +0.026 | 2023: +0.166 | 2024: +0.015
- IC CV=0.85, Neg years=1/8, Half ratio=1.16, Recency ratio=0.97
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.104, Q3_mid=+0.056, Q4=+0.076, Q5_high_vol=+0.148

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0224, Sharpe=-0.9420)
- Yearly ICs: 2017: -0.038 | 2018: +0.090 | 2019: +0.037 | 2020: +0.034 | 2021: +0.114 | 2022: +0.042 | 2023: +0.097 | 2024: +0.033
- IC CV=0.89, Neg years=1/8, Half ratio=2.28, Recency ratio=2.47
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.012, Q2=-0.023, Q3_mid=+0.059, Q4=+0.032, Q5_high_vol=+0.150

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0211, Sharpe=-1.1010)
- Yearly ICs: 2017: -0.068 | 2018: +0.203 | 2019: +0.122 | 2020: +0.060 | 2021: +0.173 | 2022: +0.045 | 2023: +0.140 | 2024: +0.050
- IC CV=0.89, Neg years=1/8, Half ratio=1.26, Recency ratio=1.41
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.032, Q2=+0.068, Q3_mid=+0.113, Q4=+0.074, Q5_high_vol=+0.235

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0200, Sharpe=-1.1921)
- Yearly ICs: 2017: +0.003 | 2018: +0.184 | 2019: +0.113 | 2020: +0.043 | 2021: +0.135 | 2022: +0.037 | 2023: +0.165 | 2024: +0.056
- IC CV=0.67, Neg years=0/8, Half ratio=1.14, Recency ratio=1.18
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.062, Q3_mid=+0.072, Q4=+0.064, Q5_high_vol=+0.215

**`combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0164, Sharpe=-0.8274)
- Yearly ICs: 2017: -0.076 | 2018: +0.170 | 2019: +0.084 | 2020: +0.074 | 2021: +0.154 | 2022: +0.090 | 2023: +0.095 | 2024: +0.025
- IC CV=0.93, Neg years=1/8, Half ratio=1.41, Recency ratio=1.28
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.019, Q2=+0.043, Q3_mid=+0.028, Q4=+0.056, Q5_high_vol=+0.237

**`combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=+0.0155, Sharpe=-2.6320)
- Yearly ICs: 2017: +0.006 | 2018: +0.229 | 2019: +0.065 | 2020: -0.005 | 2021: +0.177 | 2022: +0.034 | 2023: +0.176 | 2024: +0.002
- IC CV=1.03, Neg years=1/8, Half ratio=1.43, Recency ratio=0.76
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.122, Q3_mid=+0.067, Q4=+0.058, Q5_high_vol=+0.144

**`combo_min__max_up_ret__volume_surge_direction`** (Lock IC=+0.0128, Sharpe=-1.0073)
- Yearly ICs: 2017: -0.021 | 2018: +0.188 | 2019: +0.065 | 2020: +0.069 | 2021: +0.132 | 2022: +0.044 | 2023: +0.152 | 2024: +0.030
- IC CV=0.79, Neg years=1/8, Half ratio=1.32, Recency ratio=1.09
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.109, Q3_mid=+0.020, Q4=+0.085, Q5_high_vol=+0.156

**`combo_z_sum__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0088, Sharpe=-1.4167)
- Yearly ICs: 2017: +0.044 | 2018: +0.210 | 2019: +0.071 | 2020: -0.020 | 2021: +0.140 | 2022: +0.063 | 2023: +0.186 | 2024: +0.013
- IC CV=0.87, Neg years=1/8, Half ratio=1.41, Recency ratio=0.78
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.123, Q3_mid=+0.051, Q4=+0.062, Q5_high_vol=+0.144

### 500ETF — `single` Median Features

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1138, Sharpe=-0.0363)
- Yearly ICs: 2017: +0.196 | 2018: +0.105 | 2019: +0.176 | 2020: +0.076 | 2021: +0.087 | 2022: +0.089 | 2023: +0.057 | 2024: +0.164
- IC CV=0.41, Neg years=0/8, Half ratio=0.83, Recency ratio=0.74
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.066, Q3_mid=+0.094, Q4=+0.137, Q5_high_vol=+0.151

**`combo_z_sum__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0970, Sharpe=-0.0976)
- Yearly ICs: 2017: +0.233 | 2018: +0.100 | 2019: +0.110 | 2020: +0.116 | 2021: +0.047 | 2022: +0.058 | 2023: +0.046 | 2024: +0.103
- IC CV=0.55, Neg years=0/8, Half ratio=0.56, Recency ratio=0.45
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.001, Q3_mid=+0.092, Q4=+0.116, Q5_high_vol=+0.108

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0950, Sharpe=-0.5138)
- Yearly ICs: 2017: +0.240 | 2018: +0.181 | 2019: +0.128 | 2020: +0.172 | 2021: +0.100 | 2022: +0.076 | 2023: +0.077 | 2024: +0.135
- IC CV=0.38, Neg years=0/8, Half ratio=0.62, Recency ratio=0.50
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.018, Q3_mid=+0.117, Q4=+0.131, Q5_high_vol=+0.195

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0883, Sharpe=-1.0127)
- Yearly ICs: 2017: +0.222 | 2018: +0.178 | 2019: +0.172 | 2020: +0.171 | 2021: +0.141 | 2022: +0.008 | 2023: +0.106 | 2024: +0.163
- IC CV=0.42, Neg years=0/8, Half ratio=0.62, Recency ratio=0.67
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.005, Q3_mid=+0.122, Q4=+0.123, Q5_high_vol=+0.235

**`combo_sig_product__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0705, Sharpe=-0.6834)
- Yearly ICs: 2017: +0.202 | 2018: +0.134 | 2019: +0.129 | 2020: +0.090 | 2021: +0.097 | 2022: +0.083 | 2023: +0.096 | 2024: +0.121
- IC CV=0.30, Neg years=0/8, Half ratio=0.81, Recency ratio=0.65
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.040, Q3_mid=+0.154, Q4=+0.115, Q5_high_vol=+0.118

**`combo_rank_min__early_body_momentum__bar_ret_0`** (Lock IC=+0.0699, Sharpe=-1.1836)
- Yearly ICs: 2017: +0.145 | 2018: +0.167 | 2019: +0.118 | 2020: +0.047 | 2021: +0.073 | 2022: +0.090 | 2023: +0.082 | 2024: +0.112
- IC CV=0.35, Neg years=0/8, Half ratio=0.84, Recency ratio=0.62
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.013, Q3_mid=+0.078, Q4=+0.112, Q5_high_vol=+0.120

**`combo_max__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0613, Sharpe=-1.1301)
- Yearly ICs: 2017: +0.145 | 2018: +0.123 | 2019: +0.069 | 2020: +0.111 | 2021: +0.019 | 2022: +0.121 | 2023: +0.070 | 2024: +0.083
- IC CV=0.41, Neg years=0/8, Half ratio=0.69, Recency ratio=0.57
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.036, Q3_mid=+0.093, Q4=+0.084, Q5_high_vol=+0.095

**`combo_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration`** (Lock IC=+0.0573, Sharpe=-0.7712)
- Yearly ICs: 2017: +0.164 | 2018: +0.246 | 2019: +0.174 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145
- IC CV=0.33, Neg years=0/8, Half ratio=0.67, Recency ratio=0.59
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.006, Q3_mid=+0.133, Q4=+0.148, Q5_high_vol=+0.215

**`combo_z_sum__close_vs_open_range__rsi_opening`** (Lock IC=+0.0532, Sharpe=-1.0874)
- Yearly ICs: 2017: +0.190 | 2018: +0.117 | 2019: +0.065 | 2020: +0.102 | 2021: +0.059 | 2022: +0.097 | 2023: +0.078 | 2024: +0.133
- IC CV=0.38, Neg years=0/8, Half ratio=0.95, Recency ratio=0.69
- Weak component: `rsi_opening` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.022, Q3_mid=+0.112, Q4=+0.085, Q5_high_vol=+0.112

**`combo_min__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0486, Sharpe=-0.8978)
- Yearly ICs: 2017: +0.145 | 2018: +0.224 | 2019: +0.146 | 2020: +0.088 | 2021: +0.104 | 2022: +0.062 | 2023: +0.062 | 2024: +0.116
- IC CV=0.42, Neg years=0/8, Half ratio=0.60, Recency ratio=0.48
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.138, Q2=-0.009, Q3_mid=+0.080, Q4=+0.143, Q5_high_vol=+0.181

**`combo_mean__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0469, Sharpe=-1.6472)
- Yearly ICs: 2017: +0.214 | 2018: +0.198 | 2019: +0.106 | 2020: +0.115 | 2021: +0.099 | 2022: +0.097 | 2023: +0.078 | 2024: +0.153
- IC CV=0.36, Neg years=0/8, Half ratio=0.79, Recency ratio=0.56
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.229, Q2=+0.005, Q3_mid=+0.124, Q4=+0.126, Q5_high_vol=+0.159

**`num_up_bars`** (Lock IC=+0.0459, Sharpe=-1.5665)
- Yearly ICs: 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083 | 2024: +0.141
- IC CV=0.40, Neg years=0/8, Half ratio=1.47, Recency ratio=1.31
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.054, Q3_mid=+0.097, Q4=+0.105, Q5_high_vol=+0.089

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0457, Sharpe=-0.8920)
- Yearly ICs: 2017: +0.154 | 2018: +0.193 | 2019: +0.168 | 2020: +0.190 | 2021: +0.151 | 2022: +0.035 | 2023: +0.095 | 2024: +0.134
- IC CV=0.35, Neg years=0/8, Half ratio=0.66, Recency ratio=0.66
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.001, Q3_mid=+0.132, Q4=+0.119, Q5_high_vol=+0.223

**`combo_clamp_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0447, Sharpe=-1.3542)
- Yearly ICs: 2017: +0.191 | 2018: +0.217 | 2019: +0.121 | 2020: +0.146 | 2021: +0.154 | 2022: +0.059 | 2023: +0.095 | 2024: +0.130
- IC CV=0.34, Neg years=0/8, Half ratio=0.69, Recency ratio=0.55
- Weak component: `late_bar_momentum` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.002, Q3_mid=+0.078, Q4=+0.159, Q5_high_vol=+0.211

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0427, Sharpe=-0.7498)
- Yearly ICs: 2017: +0.132 | 2018: +0.260 | 2019: +0.170 | 2020: +0.173 | 2021: +0.170 | 2022: +0.068 | 2023: +0.082 | 2024: +0.140
- IC CV=0.38, Neg years=0/8, Half ratio=0.66, Recency ratio=0.57
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.015, Q3_mid=+0.105, Q4=+0.119, Q5_high_vol=+0.256

**`combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0383, Sharpe=-1.0012)
- Yearly ICs: 2017: +0.236 | 2018: +0.134 | 2019: +0.080 | 2020: +0.161 | 2021: +0.091 | 2022: +0.106 | 2023: +0.114 | 2024: +0.077
- IC CV=0.40, Neg years=0/8, Half ratio=0.69, Recency ratio=0.52
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.010, Q3_mid=+0.176, Q4=+0.086, Q5_high_vol=+0.130

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0337, Sharpe=-1.9117)
- Yearly ICs: 2017: +0.201 | 2018: +0.209 | 2019: +0.129 | 2020: +0.142 | 2021: +0.089 | 2022: +0.105 | 2023: +0.119 | 2024: +0.137
- IC CV=0.28, Neg years=0/8, Half ratio=0.73, Recency ratio=0.62
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.010, Q3_mid=+0.120, Q4=+0.127, Q5_high_vol=+0.210

**`vwap_close_divergence_trend`** (Lock IC=+0.0323, Sharpe=-0.6894)
- Yearly ICs: 2017: +0.184 | 2018: +0.055 | 2019: +0.091 | 2020: +0.075 | 2021: +0.069 | 2022: +0.094 | 2023: +0.107 | 2024: +0.092
- IC CV=0.38, Neg years=0/8, Half ratio=1.19, Recency ratio=0.83
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.058, Q3_mid=+0.094, Q4=+0.045, Q5_high_vol=+0.084

**`combo_sig_product__rsi_opening__first_bar_return`** (Lock IC=+0.0279, Sharpe=-0.8995)
- Yearly ICs: 2017: +0.150 | 2018: +0.180 | 2019: +0.078 | 2020: +0.065 | 2021: +0.075 | 2022: +0.090 | 2023: +0.054 | 2024: +0.132
- IC CV=0.41, Neg years=0/8, Half ratio=0.95, Recency ratio=0.56
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.004, Q3_mid=+0.111, Q4=+0.109, Q5_high_vol=+0.157

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0268, Sharpe=-1.9409)
- Yearly ICs: 2017: +0.166 | 2018: +0.244 | 2019: +0.128 | 2020: +0.103 | 2021: +0.157 | 2022: +0.085 | 2023: +0.082 | 2024: +0.148
- IC CV=0.36, Neg years=0/8, Half ratio=0.80, Recency ratio=0.56
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.015, Q3_mid=+0.104, Q4=+0.142, Q5_high_vol=+0.219

**`combo_sig_product__opening_auction_imbalance__bar_ret_0`** (Lock IC=+0.0245, Sharpe=-0.8223)
- Yearly ICs: 2017: +0.155 | 2018: +0.199 | 2019: +0.138 | 2020: +0.068 | 2021: +0.044 | 2022: +0.058 | 2023: +0.067 | 2024: +0.054
- IC CV=0.55, Neg years=0/8, Half ratio=0.41, Recency ratio=0.34
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.033, Q3_mid=+0.066, Q4=+0.113, Q5_high_vol=+0.117

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0205, Sharpe=-1.0002)
- Yearly ICs: 2017: +0.116 | 2018: +0.278 | 2019: +0.078 | 2020: +0.109 | 2021: +0.083 | 2022: +0.128 | 2023: +0.036 | 2024: +0.101
- IC CV=0.57, Neg years=0/8, Half ratio=0.65, Recency ratio=0.35
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.006, Q3_mid=+0.062, Q4=+0.118, Q5_high_vol=+0.180

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0148, Sharpe=-2.6617)
- Yearly ICs: 2017: +0.155 | 2018: +0.225 | 2019: +0.081 | 2020: +0.134 | 2021: +0.102 | 2022: +0.108 | 2023: +0.080 | 2024: +0.124
- IC CV=0.35, Neg years=0/8, Half ratio=0.74, Recency ratio=0.54
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.016, Q3_mid=+0.129, Q4=+0.151, Q5_high_vol=+0.147

### 159915ETF — `single` Median Features

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1264, Sharpe=-0.1409)
- Yearly ICs: 2017: +0.026 | 2018: +0.122 | 2019: +0.160 | 2020: +0.151 | 2021: +0.169 | 2022: +0.156 | 2023: +0.139 | 2024: +0.086
- IC CV=0.36, Neg years=0/8, Half ratio=1.27, Recency ratio=1.53
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.119, Q3_mid=+0.091, Q4=+0.139, Q5_high_vol=+0.193

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1161, Sharpe=-0.4268)
- Yearly ICs: 2017: +0.029 | 2018: +0.133 | 2019: +0.128 | 2020: +0.137 | 2021: +0.158 | 2022: +0.146 | 2023: +0.134 | 2024: +0.077
- IC CV=0.34, Neg years=0/8, Half ratio=1.23, Recency ratio=1.29
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.122, Q3_mid=+0.079, Q4=+0.118, Q5_high_vol=+0.169

**`combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1079, Sharpe=-0.5498)
- Yearly ICs: 2017: -0.058 | 2018: +0.036 | 2019: +0.135 | 2020: +0.037 | 2021: +0.133 | 2022: +0.143 | 2023: +0.143 | 2024: +0.054
- IC CV=0.88, Neg years=1/8, Half ratio=2.54, Recency ratio=-8.81
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.046, Q3_mid=+0.091, Q4=+0.116, Q5_high_vol=+0.131

**`combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1073, Sharpe=-0.0881)
- Yearly ICs: 2017: +0.033 | 2018: +0.122 | 2019: +0.197 | 2020: +0.149 | 2021: +0.137 | 2022: +0.137 | 2023: +0.160 | 2024: +0.139
- IC CV=0.32, Neg years=0/8, Half ratio=1.11, Recency ratio=1.93
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.111, Q3_mid=+0.045, Q4=+0.160, Q5_high_vol=+0.261

**`combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0802, Sharpe=-1.3851)
- Yearly ICs: 2017: +0.001 | 2018: +0.129 | 2019: +0.197 | 2020: +0.139 | 2021: +0.144 | 2022: +0.090 | 2023: +0.172 | 2024: +0.050
- IC CV=0.53, Neg years=0/8, Half ratio=1.12, Recency ratio=1.71
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.100, Q3_mid=+0.092, Q4=+0.097, Q5_high_vol=+0.147

**`combo_rank_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0738, Sharpe=-0.5477)
- Yearly ICs: 2017: +0.032 | 2018: +0.106 | 2019: +0.174 | 2020: +0.115 | 2021: +0.130 | 2022: +0.087 | 2023: +0.186 | 2024: +0.099
- IC CV=0.40, Neg years=0/8, Half ratio=1.40, Recency ratio=2.06
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.090, Q3_mid=+0.139, Q4=+0.098, Q5_high_vol=+0.122

**`combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0710, Sharpe=-0.4825)
- Yearly ICs: 2017: +0.029 | 2018: +0.086 | 2019: +0.185 | 2020: +0.048 | 2021: +0.159 | 2022: +0.052 | 2023: +0.180 | 2024: +0.083
- IC CV=0.57, Neg years=0/8, Half ratio=1.59, Recency ratio=2.30
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.092, Q3_mid=+0.134, Q4=+0.093, Q5_high_vol=+0.117

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0684, Sharpe=-0.2354)
- Yearly ICs: 2017: -0.037 | 2018: +0.058 | 2019: +0.165 | 2020: +0.079 | 2021: +0.086 | 2022: +0.109 | 2023: +0.155 | 2024: +0.149
- IC CV=0.65, Neg years=1/8, Half ratio=1.63, Recency ratio=14.55
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.044, Q2=+0.072, Q3_mid=+0.079, Q4=+0.123, Q5_high_vol=+0.189

**`max_up_ret`** (Lock IC=+0.0682, Sharpe=-0.9705)
- Yearly ICs: 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175 | 2024: +0.074
- IC CV=0.39, Neg years=0/8, Half ratio=1.68, Recency ratio=2.15
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.098, Q3_mid=+0.115, Q4=+0.089, Q5_high_vol=+0.126

**`combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0658, Sharpe=-0.2206)
- Yearly ICs: 2017: +0.003 | 2018: +0.043 | 2019: +0.038 | 2020: +0.119 | 2021: +0.141 | 2022: +0.130 | 2023: +0.126 | 2024: +0.093
- IC CV=0.56, Neg years=0/8, Half ratio=2.94, Recency ratio=4.76
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.024, Q3_mid=+0.097, Q4=+0.065, Q5_high_vol=+0.158

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1108, Sharpe=+0.9093)
- Yearly ICs: 2017: +0.190 | 2018: +0.142 | 2019: +0.181 | 2020: +0.142 | 2021: +0.093 | 2022: +0.048 | 2023: +0.069 | 2024: +0.097
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.50
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1502, Sharpe=+0.8062)
- Yearly ICs: 2017: +0.167 | 2018: +0.148 | 2019: +0.174 | 2020: +0.083 | 2021: +0.082 | 2022: +0.053 | 2023: +0.110 | 2024: +0.162
- IC CV=0.35, Neg years=0/8, Half ratio=0.72, Recency ratio=0.86
- Weak component: `max_down_ret` (CV=0.55)

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1041, Sharpe=+0.4133)
- Yearly ICs: 2017: +0.129 | 2018: +0.203 | 2019: +0.177 | 2020: +0.184 | 2021: +0.122 | 2022: +0.050 | 2023: +0.062 | 2024: +0.112
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.53
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1136, Sharpe=+0.3024)
- Yearly ICs: 2017: +0.137 | 2018: +0.191 | 2019: +0.196 | 2020: +0.194 | 2021: +0.142 | 2022: +0.064 | 2023: +0.067 | 2024: +0.123
- IC CV=0.36, Neg years=0/8, Half ratio=0.57, Recency ratio=0.58
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0999, Sharpe=+0.1111)
- Yearly ICs: 2017: +0.215 | 2018: +0.201 | 2019: +0.175 | 2020: +0.145 | 2021: +0.098 | 2022: +0.039 | 2023: +0.079 | 2024: +0.090
- IC CV=0.45, Neg years=0/8, Half ratio=0.41, Recency ratio=0.41
- Weak component: `bar_ret_0` (CV=0.46)

**`combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0998, Sharpe=+0.0418)
- Yearly ICs: 2017: +0.208 | 2018: +0.105 | 2019: +0.101 | 2020: +0.097 | 2021: +0.096 | 2022: +0.052 | 2023: +0.103 | 2024: +0.136
- IC CV=0.37, Neg years=0/8, Half ratio=0.89, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0920, Sharpe=+0.0124)
- Yearly ICs: 2017: +0.219 | 2018: +0.204 | 2019: +0.175 | 2020: +0.134 | 2021: +0.087 | 2022: +0.047 | 2023: +0.079 | 2024: +0.088
- IC CV=0.46, Neg years=0/8, Half ratio=0.40, Recency ratio=0.39
- Weak component: `bar_ret_0` (CV=0.46)

### 159915ETF — `single` True Positives

**`combo_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1307, Sharpe=+1.4405)
- Yearly ICs: 2017: -0.006 | 2018: +0.097 | 2019: +0.227 | 2020: +0.043 | 2021: +0.155 | 2022: +0.034 | 2023: +0.154 | 2024: +0.136
- IC CV=0.69, Neg years=1/8, Half ratio=1.41, Recency ratio=3.20
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1316, Sharpe=+1.2800)
- Yearly ICs: 2017: +0.035 | 2018: +0.105 | 2019: +0.108 | 2020: +0.061 | 2021: +0.170 | 2022: +0.135 | 2023: +0.149 | 2024: +0.106
- IC CV=0.38, Neg years=0/8, Half ratio=2.02, Recency ratio=1.82
- Weak component: `impulse_bar_dominance` (CV=0.77)

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1300, Sharpe=+1.2547)
- Yearly ICs: 2017: -0.006 | 2018: +0.164 | 2019: +0.223 | 2020: +0.136 | 2021: +0.147 | 2022: +0.129 | 2023: +0.186 | 2024: +0.080
- IC CV=0.50, Neg years=1/8, Half ratio=1.07, Recency ratio=1.68
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)

**`combo_mean__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1160, Sharpe=+1.0577)
- Yearly ICs: 2017: -0.021 | 2018: +0.133 | 2019: +0.234 | 2020: +0.171 | 2021: +0.125 | 2022: +0.100 | 2023: +0.074 | 2024: +0.083
- IC CV=0.62, Neg years=1/8, Half ratio=0.78, Recency ratio=1.40
- Weak component: `first_bar_sentiment` (CV=0.86)

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1592, Sharpe=+0.9464)
- Yearly ICs: 2017: -0.057 | 2018: +0.093 | 2019: +0.245 | 2020: +0.120 | 2021: +0.099 | 2022: +0.061 | 2023: +0.135 | 2024: +0.095
- IC CV=0.79, Neg years=1/8, Half ratio=1.08, Recency ratio=6.24
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1302, Sharpe=+0.8754)
- Yearly ICs: 2017: +0.026 | 2018: +0.159 | 2019: +0.224 | 2020: +0.126 | 2021: +0.163 | 2022: +0.113 | 2023: +0.175 | 2024: +0.105
- IC CV=0.40, Neg years=0/8, Half ratio=1.11, Recency ratio=1.52
- Weak component: `star50_limit_proximity_early` (CV=0.52)

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1325, Sharpe=+0.7447)
- Yearly ICs: 2017: +0.023 | 2018: +0.124 | 2019: +0.198 | 2020: +0.163 | 2021: +0.160 | 2022: +0.117 | 2023: +0.158 | 2024: +0.094
- IC CV=0.39, Neg years=0/8, Half ratio=1.10, Recency ratio=1.71
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)

**`combo_min__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1466, Sharpe=+0.6474)
- Yearly ICs: 2017: -0.028 | 2018: +0.079 | 2019: +0.250 | 2020: +0.117 | 2021: +0.094 | 2022: +0.059 | 2023: +0.126 | 2024: +0.082
- IC CV=0.75, Neg years=1/8, Half ratio=0.90, Recency ratio=4.02
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1275, Sharpe=+0.5336)
- Yearly ICs: 2017: -0.024 | 2018: +0.157 | 2019: +0.245 | 2020: +0.161 | 2021: +0.143 | 2022: +0.085 | 2023: +0.178 | 2024: +0.127
- IC CV=0.55, Neg years=1/8, Half ratio=1.05, Recency ratio=2.29
- Weak component: `bar_body_rng_0` (CV=0.63)

**`combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1466, Sharpe=+0.5276)
- Yearly ICs: 2017: -0.004 | 2018: +0.048 | 2019: +0.159 | 2020: +0.084 | 2021: +0.169 | 2022: +0.100 | 2023: +0.148 | 2024: +0.085
- IC CV=0.56, Neg years=1/8, Half ratio=1.86, Recency ratio=5.29
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)

**`combo_ratio__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1308, Sharpe=+0.4527)
- Yearly ICs: 2017: -0.012 | 2018: +0.072 | 2019: +0.170 | 2020: +0.085 | 2021: +0.112 | 2022: +0.141 | 2023: +0.103 | 2024: +0.117
- IC CV=0.52, Neg years=1/8, Half ratio=1.38, Recency ratio=3.68
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0659, Sharpe=+0.4490)
- Yearly ICs: 2017: +0.008 | 2018: +0.135 | 2019: +0.197 | 2020: +0.110 | 2021: +0.134 | 2022: +0.058 | 2023: +0.150 | 2024: +0.061
- IC CV=0.53, Neg years=0/8, Half ratio=0.94, Recency ratio=1.48
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1286, Sharpe=+0.3148)
- Yearly ICs: 2017: -0.047 | 2018: +0.084 | 2019: +0.131 | 2020: +0.102 | 2021: +0.033 | 2022: +0.180 | 2023: +0.115 | 2024: +0.083
- IC CV=0.75, Neg years=1/8, Half ratio=1.22, Recency ratio=5.34
- Weak component: `yesterday_first_30min_return` (CV=0.99)

**`combo_mean__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1320, Sharpe=+0.2281)
- Yearly ICs: 2017: +0.042 | 2018: +0.134 | 2019: +0.221 | 2020: +0.070 | 2021: +0.190 | 2022: +0.063 | 2023: +0.114 | 2024: +0.107
- IC CV=0.50, Neg years=0/8, Half ratio=1.05, Recency ratio=1.26
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1064, Sharpe=+0.2130)
- Yearly ICs: 2017: +0.032 | 2018: +0.063 | 2019: +0.150 | 2020: +0.122 | 2021: +0.158 | 2022: +0.150 | 2023: +0.134 | 2024: +0.137
- IC CV=0.36, Neg years=0/8, Half ratio=1.63, Recency ratio=2.87
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1454, Sharpe=+0.1295)
- Yearly ICs: 2017: -0.008 | 2018: +0.152 | 2019: +0.236 | 2020: +0.148 | 2021: +0.129 | 2022: +0.103 | 2023: +0.136 | 2024: +0.075
- IC CV=0.54, Neg years=1/8, Half ratio=0.88, Recency ratio=1.46
- Weak component: `first_bar_return` (CV=0.48)

**`combo_rel_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1200, Sharpe=+0.0394)
- Yearly ICs: 2017: +0.010 | 2018: +0.132 | 2019: +0.195 | 2020: +0.138 | 2021: +0.153 | 2022: +0.125 | 2023: +0.142 | 2024: +0.082
- IC CV=0.42, Neg years=0/8, Half ratio=1.19, Recency ratio=1.57
- Weak component: `demark_setup_reversal_early` (CV=0.51)

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Median | fast | +0.1203 | -0.1421 | -0.1421 | 1y |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | Median | fast | +0.1057 | -0.1387 | -0.1387 | 1y |
| `combo_max__max_up_ret__volume_weighted_price_position` | FP | fast | +0.0964 | -0.2004 | -0.2004 | 1y |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | Median | persistent | +0.0925 | +0.0510 | +0.0510 | ∞ |
| `morning_volume_weighted_momentum` | FP | fast | +0.0883 | -0.1752 | -0.1752 | 1y |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Median | fast | +0.0845 | -0.0552 | -0.0552 | 1y |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0743 | +0.0631 | +0.0631 | ∞ |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | FP | fast | +0.0711 | -0.1230 | -0.1230 | 1y |
| `combo_min__max_up_ret__volume_surge_direction` | Median | fast | +0.0673 | -0.0609 | -0.0609 | 1y |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0569 | -0.1658 | -0.1658 | 1y |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | Median | persistent | +0.0528 | +0.0124 | +0.0124 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | fast | +0.0477 | -0.0312 | -0.0312 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | fast | +0.0467 | -0.0313 | -0.0313 | 1y |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | fast | +0.0419 | -0.0169 | -0.0169 | 1y |
| `combo_max__max_up_ret__first_bar_sentiment` | FP | fast | +0.0380 | -0.1327 | -0.1327 | 1y |
| `combo_diff__max_up_ret__early_vwap_acceleration` | FP | fast | +0.0218 | -0.0859 | -0.0859 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | FP | fast | +0.0216 | -0.0774 | -0.0774 | 1y |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.0207 | -0.0951 | -0.0951 | 1y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | persistent | +0.0069 | +0.0623 | +0.0623 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=15, gradual=0, persistent=4

**FP decay trajectories:**

- `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.021 → Y2:-0.095
- `combo_min__max_up_ret__bar_body_rng_0`: Y1:+0.022 → Y2:-0.077
- `combo_diff__max_up_ret__early_vwap_acceleration`: Y1:+0.022 → Y2:-0.086
- `combo_max__max_up_ret__first_bar_sentiment`: Y1:+0.038 → Y2:-0.133
- `combo_mean__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.057 → Y2:-0.166
- `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:+0.071 → Y2:-0.123
- `morning_volume_weighted_momentum`: Y1:+0.088 → Y2:-0.175
- `combo_max__max_up_ret__volume_weighted_price_position`: Y1:+0.096 → Y2:-0.200

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Median | fast | +0.1941 | -0.0734 | -0.0734 | 1y |
| `combo_z_sum__close_vs_open_range__rsi_opening` | Median | fast | +0.1430 | -0.0685 | -0.0685 | 1y |
| `vwap_close_divergence_trend` | Median | fast | +0.1327 | -0.0940 | -0.0940 | 1y |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1275 | +0.0743 | +0.0743 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1262 | +0.0854 | +0.0854 | ∞ |
| `combo_sig_product__rsi_opening__first_bar_return` | Median | fast | +0.1255 | -0.1226 | -0.1226 | 1y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | fast | +0.1244 | -0.1147 | -0.1147 | 1y |
| `combo_mean__close_vs_open_range__bar_ret_0` | Median | fast | +0.1198 | -0.0391 | -0.0391 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1192 | +0.0805 | +0.0805 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | fast | +0.1192 | -0.0517 | -0.0517 | 1y |
| `combo_rank_min__early_body_momentum__bar_ret_0` | Median | persistent | +0.1192 | +0.0067 | +0.0067 | 1y |
| `num_up_bars` | Median | fast | +0.1166 | -0.0474 | -0.0474 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.1158 | +0.0713 | +0.0713 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1083 | +0.1990 | +0.1990 | ∞ |
| `combo_sig_product__opening_auction_imbalance__bar_ret_0` | Median | fast | +0.1079 | -0.0996 | -0.0996 | 1y |
| `combo_min__first_bar_sentiment__first_bar_return` | Median | fast | +0.1049 | -0.0093 | -0.0093 | 1y |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | Median | persistent | +0.1048 | +0.0149 | +0.0149 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | fast | +0.0978 | -0.0539 | -0.0539 | 1y |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | Median | persistent | +0.0971 | +0.1049 | +0.1049 | ∞ |
| `combo_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | Median | persistent | +0.0953 | +0.0159 | +0.0159 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Median | persistent | +0.0944 | +0.0858 | +0.0858 | ∞ |
| `early_order_flow_imbalance` | FP | fast | +0.0913 | -0.1345 | -0.1345 | 1y |
| `combo_max__max_up_ret__bar_ret_0` | Median | fast | +0.0912 | -0.0638 | -0.0638 | 1y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0889 | +0.1750 | +0.1750 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | Median | fast | +0.0731 | -0.0782 | -0.0782 | 1y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0685 | +0.0222 | +0.0222 | 1y |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0602 | +0.1848 | +0.1848 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Median | persistent | +0.0578 | +0.1809 | +0.1809 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.0558 | +0.0389 | +0.0389 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0391 | +0.2313 | +0.2313 | ∞ |
| `vol_pk20` | FP | fast | +0.0337 | -0.1585 | -0.1585 | 1y |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Median | persistent | +0.0156 | +0.0876 | +0.0876 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=15, gradual=0, persistent=17

**FP decay trajectories:**

- `vol_pk20`: Y1:+0.034 → Y2:-0.159
- `early_order_flow_imbalance`: Y1:+0.091 → Y2:-0.135

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1894 | +0.0801 | +0.0801 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1878 | +0.0637 | +0.0637 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | persistent | +0.1819 | +0.0654 | +0.0654 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1813 | +0.0531 | +0.0531 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Median | fast | +0.1755 | -0.0752 | -0.0752 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1744 | +0.0678 | +0.0678 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1727 | -0.0740 | -0.0740 | 1y |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.1716 | +0.0486 | +0.0486 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1704 | +0.0712 | +0.0712 | 1y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1679 | +0.1321 | +0.1321 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1654 | +0.1061 | +0.1061 | ∞ |
| `max_up_ret` | Median | fast | +0.1636 | -0.0753 | -0.0753 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1594 | +0.0841 | +0.0841 | ∞ |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1537 | +0.1220 | +0.1220 | ∞ |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Median | fast | +0.1477 | -0.0170 | -0.0170 | 1y |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1468 | +0.1163 | +0.1163 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1412 | +0.0738 | +0.0738 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Median | persistent | +0.1348 | +0.1140 | +0.1140 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1313 | +0.1302 | +0.1302 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1291 | +0.1272 | +0.1272 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1247 | +0.1472 | +0.1472 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Median | persistent | +0.1187 | +0.0086 | +0.0086 | 1y |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.1143 | +0.0098 | +0.0098 | 1y |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1081 | +0.1384 | +0.1384 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | Median | persistent | +0.1014 | +0.1299 | +0.1299 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Median | persistent | +0.0655 | +0.1661 | +0.1661 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Median | persistent | +0.0612 | +0.0874 | +0.0874 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=4, gradual=0, persistent=23

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.709±0.024 | 0.722±0.032 | 48% | USEFUL |
| ic_ir | 0.520±0.062 | 0.604±0.076 | 51% | WEAK |
| p_value | 0.018±0.018 | 0.000±0.000 | 1% | USEFUL |
| max_corr | 0.511±0.237 | 0.787±0.060 | 17% | USEFUL |
| deflated_ic | 0.170±0.065 | 0.221±0.017 | 34% | USEFUL |
| overall_ic | 0.170±0.065 | 0.222±0.017 | 32% | USEFUL |
| raw_ic | 0.067±0.032 | 0.124±0.010 | 0% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**B2 Rolling Guard**: 2/20 top rejects are profitable (10%)

- `combo_product__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Sharpe=+0.0079
- `combo_product__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Sharpe=+0.0079

### 500ETF — `single`

**7-Year Jackknife**: 3/20 top rejects are profitable (15%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Sharpe=+0.2052
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.0912
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.0912

**B2 Rolling Guard**: 1/20 top rejects are profitable (5%)

- `combo_min__late_bar_momentum__double_bottom_bull_flag_early`: Train IC=+0.1190, Lock IC=+0.0815, Sharpe=+0.5805

**BH-FDR Gate**: 2/11 top rejects are profitable (18%)

- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0658, Lock IC=+0.0308, Sharpe=+0.8091
- `combo_sig_product__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.0665, Lock IC=+0.1374, Sharpe=+0.7669

**B3 Composite Floor**: 3/20 top rejects are profitable (15%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2503, Lock IC=+0.0951, Sharpe=+0.2253
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2503, Lock IC=+0.0879, Sharpe=+0.0310
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2503, Lock IC=+0.0879, Sharpe=+0.0310

### 159915ETF — `single`

**7-Year Jackknife**: 15/20 top rejects are profitable (75%)

- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.1890, Lock IC=+0.1126, Sharpe=+1.2851
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.6296
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.6296

**B2 Rolling Guard**: 11/20 top rejects are profitable (55%)

- `combo_min__first_bar_sentiment__demark_setup_reversal_early`: Train IC=+0.1451, Lock IC=+0.0857, Sharpe=+1.1030
- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+0.7571
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+0.7571

**BH-FDR Gate**: 2/13 top rejects are profitable (15%)

- `combo_rank_min__first_bar_sentiment__first_bar_return`: Train IC=+0.0825, Lock IC=+0.0759, Sharpe=+1.2304
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.0825, Lock IC=+0.0759, Sharpe=+1.2304

**B3 Composite Floor**: 12/20 top rejects are profitable (60%)

- `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Sharpe=+1.5392
- `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Sharpe=+1.5392
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2433, Lock IC=+0.1490, Sharpe=+1.1150

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.1834
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.1600
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.1600

**Adaptive Correlation Gate**: 4/9 top rejects are profitable (44%)

- `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2407, Lock IC=+0.1394, Sharpe=+0.6965
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.1916, Lock IC=+0.1428, Sharpe=+0.4500
- `combo_z_sum__first_bar_return__volume_weighted_price_position`: Train IC=+0.1783, Lock IC=+0.0739, Sharpe=+0.3511

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `recency_ratio`: FP is higher (d=+3.48). Threshold 0.911 → 100% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-2.75). Threshold 0.091 → 67% accuracy.
- `n_negative_years`: FP is higher (d=+1.41). Threshold 1.000 → 89% accuracy.
- `half_ratio`: FP is lower (d=-1.27). Threshold 1.143 → 89% accuracy.
- `ic_cv`: FP is higher (d=+1.12). Threshold 0.895 → 89% accuracy.
- `n_negative_regimes`: FP is higher (d=+0.72). Threshold 1.500 → 89% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/2
- Decaying signal (half ratio < 0.3): 1/2
- Weak component (CV > 2.0): 0/2
- Regime-dependent (≥2 negative regimes): 1/2

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | 5 | 1 | 6 | 83% | ⚠ TOXIC |
| `first_bar_sentiment` | 2 | 1 | 3 | 67% |  |
| `opening_drive_thrust_ratio` | 3 | 4 | 7 | 43% |  |
| `bar_body_rng_0` | 1 | 2 | 3 | 33% |  |
| `volume_weighted_price_position` | 2 | 4 | 6 | 33% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 7 | 7 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 2 | 2 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 2 | 2 | 0% |  |
| `bar_ret_0` | 0 | 3 | 3 | 0% |  |
| `first_bar_return` | 0 | 4 | 4 | 0% |  |
| `star50_limit_proximity_early` | 0 | 13 | 13 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 2 | 2 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=4, TP=15, FP rate=21%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=3, FP rate=25%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=2, FP rate=0%

