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
| 300ETF | single | 19 | 7 | 11 | 1 | 37% | 0.16 |
| 500ETF | single | 30 | 1 | 20 | 9 | 3% | 0.47 |
| 159915ETF | single | 33 | 0 | 6 | 27 | 0% | 0.81 |

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

**`combo_mean__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0365, Sharpe=-1.6583)
- Yearly ICs: 2017: -0.034 | 2018: +0.160 | 2019: +0.072 | 2020: +0.053 | 2021: +0.175 | 2022: +0.015 | 2023: +0.160 | 2024: +0.064
- IC CV=0.85, Neg years=1/8, Half ratio=1.81, Recency ratio=1.78
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.085, Q3_mid=+0.028, Q4=+0.054, Q5_high_vol=+0.212

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0282, Sharpe=-1.4181)
- Yearly ICs: 2017: -0.041 | 2018: +0.138 | 2019: +0.113 | 2020: +0.035 | 2021: +0.173 | 2022: +0.000 | 2023: +0.187 | 2024: +0.024
- IC CV=1.01, Neg years=1/8, Half ratio=1.66, Recency ratio=2.18
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.003, Q2=+0.170, Q3_mid=+0.051, Q4=+0.115, Q5_high_vol=+0.065

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0223, Sharpe=-1.3571)
- Yearly ICs: 2017: +0.020 | 2018: +0.182 | 2019: +0.072 | 2020: -0.000 | 2021: +0.133 | 2022: +0.045 | 2023: +0.170 | 2024: +0.055
- IC CV=0.76, Neg years=1/8, Half ratio=1.46, Recency ratio=1.11
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.079, Q3_mid=+0.041, Q4=+0.072, Q5_high_vol=+0.177

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0391, Sharpe=-0.9630)
- Yearly ICs: 2017: +0.008 | 2018: +0.136 | 2019: +0.044 | 2020: +0.004 | 2021: +0.171 | 2022: +0.037 | 2023: +0.200 | 2024: +0.032
- IC CV=0.92, Neg years=0/8, Half ratio=2.68, Recency ratio=1.61
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.099, Q3_mid=-0.001, Q4=+0.042, Q5_high_vol=+0.183

**`combo_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=-0.0284, Sharpe=-0.8306)
- Yearly ICs: 2017: +0.034 | 2018: +0.192 | 2019: +0.044 | 2020: +0.043 | 2021: +0.166 | 2022: +0.020 | 2023: +0.162 | 2024: +0.115
- IC CV=0.67, Neg years=0/8, Half ratio=1.60, Recency ratio=1.23
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.084, Q3_mid=+0.059, Q4=+0.037, Q5_high_vol=+0.211

**`combo_sig_product__first_bar_sentiment__opening_drive_thrust_ratio`** (Lock IC=-0.0235, Sharpe=-0.7280)
- Yearly ICs: 2017: -0.050 | 2018: +0.155 | 2019: +0.153 | 2020: +0.008 | 2021: +0.160 | 2022: +0.053 | 2023: +0.178 | 2024: +0.000
- IC CV=1.02, Neg years=1/8, Half ratio=1.48, Recency ratio=1.69
- Weak component: `first_bar_sentiment` (CV=1.06, neg years=2)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.119, Q3_mid=+0.038, Q4=+0.095, Q5_high_vol=+0.137

**`combo_max__max_up_ret__volume_surge_direction`** (Lock IC=-0.0158, Sharpe=-0.6017)
- Yearly ICs: 2017: -0.037 | 2018: +0.152 | 2019: +0.107 | 2020: -0.001 | 2021: +0.119 | 2022: +0.029 | 2023: +0.157 | 2024: +0.027
- IC CV=1.00, Neg years=2/8, Half ratio=1.63, Recency ratio=1.61
- Weak component: `volume_surge_direction` (CV=1.10, neg years=2)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.089, Q3_mid=+0.021, Q4=+0.047, Q5_high_vol=+0.153

### 500ETF — `single` False Positives

**`early_order_flow_imbalance`** (Lock IC=-0.0041, Sharpe=-1.9661)
- Yearly ICs: 2017: +0.093 | 2018: +0.101 | 2019: +0.121 | 2020: +0.038 | 2021: +0.122 | 2022: +0.141 | 2023: +0.079 | 2024: +0.107
- IC CV=0.29, Neg years=0/8, Half ratio=1.40, Recency ratio=0.96
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.072, Q3_mid=+0.065, Q4=+0.113, Q5_high_vol=+0.095

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0753, Sharpe=-0.1501)
- Yearly ICs: 2017: -0.059 | 2018: +0.144 | 2019: +0.097 | 2020: +0.039 | 2021: +0.142 | 2022: +0.100 | 2023: +0.086 | 2024: -0.004
- IC CV=0.98, Neg years=2/8, Half ratio=1.48, Recency ratio=0.96
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=-0.001, Q2=+0.062, Q3_mid=+0.079, Q4=+0.058, Q5_high_vol=+0.154

**`combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=+0.0409, Sharpe=-0.1685)
- Yearly ICs: 2017: -0.003 | 2018: +0.026 | 2019: +0.036 | 2020: -0.032 | 2021: +0.045 | 2022: +0.060 | 2023: +0.115 | 2024: +0.077
- IC CV=1.06, Neg years=2/8, Half ratio=10.38, Recency ratio=8.54
- Weak component: `double_bottom_bull_flag_early` (CV=1.91)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.100, Q3_mid=-0.043, Q4=+0.084, Q5_high_vol=-0.008

**`combo_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.0396, Sharpe=-0.6327)
- Yearly ICs: 2017: -0.064 | 2018: +0.187 | 2019: +0.077 | 2020: +0.019 | 2021: +0.137 | 2022: +0.098 | 2023: +0.140 | 2024: +0.018
- IC CV=1.00, Neg years=1/8, Half ratio=1.58, Recency ratio=1.28
- Weak component: `demark_setup_reversal_early` (CV=1.65)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.067, Q3_mid=+0.055, Q4=+0.070, Q5_high_vol=+0.200

**`combo_min__bar_body_rng_0__volume_surge_direction`** (Lock IC=+0.0300, Sharpe=-0.0790)
- Yearly ICs: 2017: -0.002 | 2018: +0.189 | 2019: +0.080 | 2020: +0.037 | 2021: +0.160 | 2022: +0.026 | 2023: +0.166 | 2024: +0.015
- IC CV=0.85, Neg years=1/8, Half ratio=1.16, Recency ratio=0.97
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.104, Q3_mid=+0.056, Q4=+0.076, Q5_high_vol=+0.148

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0244, Sharpe=-0.2554)
- Yearly ICs: 2017: -0.068 | 2018: +0.203 | 2019: +0.122 | 2020: +0.060 | 2021: +0.173 | 2022: +0.045 | 2023: +0.140 | 2024: +0.050
- IC CV=0.89, Neg years=1/8, Half ratio=1.26, Recency ratio=1.41
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.032, Q2=+0.068, Q3_mid=+0.113, Q4=+0.074, Q5_high_vol=+0.235

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0200, Sharpe=-0.6924)
- Yearly ICs: 2017: +0.003 | 2018: +0.184 | 2019: +0.113 | 2020: +0.043 | 2021: +0.135 | 2022: +0.037 | 2023: +0.165 | 2024: +0.056
- IC CV=0.67, Neg years=0/8, Half ratio=1.14, Recency ratio=1.18
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.062, Q3_mid=+0.072, Q4=+0.064, Q5_high_vol=+0.215

**`combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0164, Sharpe=-0.3387)
- Yearly ICs: 2017: -0.076 | 2018: +0.170 | 2019: +0.084 | 2020: +0.074 | 2021: +0.154 | 2022: +0.090 | 2023: +0.095 | 2024: +0.025
- IC CV=0.93, Neg years=1/8, Half ratio=1.41, Recency ratio=1.28
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.019, Q2=+0.043, Q3_mid=+0.028, Q4=+0.056, Q5_high_vol=+0.237

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0148, Sharpe=-0.9076)
- Yearly ICs: 2017: -0.097 | 2018: +0.145 | 2019: +0.076 | 2020: +0.036 | 2021: +0.154 | 2022: +0.060 | 2023: +0.134 | 2024: +0.027
- IC CV=1.15, Neg years=1/8, Half ratio=2.24, Recency ratio=3.35
- Weak component: `demark_setup_reversal_early` (CV=1.65)
- Regime ICs: Q1_low_vol=-0.001, Q2=+0.052, Q3_mid=+0.023, Q4=+0.059, Q5_high_vol=+0.204

**`combo_min__max_up_ret__volume_surge_direction`** (Lock IC=+0.0128, Sharpe=-0.5403)
- Yearly ICs: 2017: -0.021 | 2018: +0.188 | 2019: +0.065 | 2020: +0.069 | 2021: +0.132 | 2022: +0.044 | 2023: +0.152 | 2024: +0.030
- IC CV=0.79, Neg years=1/8, Half ratio=1.32, Recency ratio=1.09
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.109, Q3_mid=+0.020, Q4=+0.085, Q5_high_vol=+0.156

**`combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=+0.0098, Sharpe=-1.6517)
- Yearly ICs: 2017: +0.006 | 2018: +0.229 | 2019: +0.065 | 2020: -0.005 | 2021: +0.177 | 2022: +0.034 | 2023: +0.176 | 2024: +0.002
- IC CV=1.03, Neg years=1/8, Half ratio=1.43, Recency ratio=0.76
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.122, Q3_mid=+0.067, Q4=+0.058, Q5_high_vol=+0.144

**`combo_z_sum__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0088, Sharpe=-0.8472)
- Yearly ICs: 2017: +0.044 | 2018: +0.210 | 2019: +0.071 | 2020: -0.020 | 2021: +0.140 | 2022: +0.063 | 2023: +0.186 | 2024: +0.013
- IC CV=0.87, Neg years=1/8, Half ratio=1.41, Recency ratio=0.78
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.123, Q3_mid=+0.051, Q4=+0.062, Q5_high_vol=+0.144

### 500ETF — `single` Median Features

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0950, Sharpe=-0.0776)
- Yearly ICs: 2017: +0.240 | 2018: +0.181 | 2019: +0.128 | 2020: +0.172 | 2021: +0.100 | 2022: +0.076 | 2023: +0.077 | 2024: +0.135
- IC CV=0.38, Neg years=0/8, Half ratio=0.62, Recency ratio=0.50
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.018, Q3_mid=+0.117, Q4=+0.131, Q5_high_vol=+0.195

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0883, Sharpe=-0.5698)
- Yearly ICs: 2017: +0.222 | 2018: +0.178 | 2019: +0.172 | 2020: +0.171 | 2021: +0.141 | 2022: +0.008 | 2023: +0.106 | 2024: +0.163
- IC CV=0.42, Neg years=0/8, Half ratio=0.62, Recency ratio=0.67
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.005, Q3_mid=+0.122, Q4=+0.123, Q5_high_vol=+0.235

**`combo_sig_product__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0705, Sharpe=-0.3494)
- Yearly ICs: 2017: +0.202 | 2018: +0.134 | 2019: +0.129 | 2020: +0.090 | 2021: +0.097 | 2022: +0.083 | 2023: +0.096 | 2024: +0.121
- IC CV=0.30, Neg years=0/8, Half ratio=0.81, Recency ratio=0.65
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.040, Q3_mid=+0.154, Q4=+0.115, Q5_high_vol=+0.118

**`combo_rank_min__early_body_momentum__bar_ret_0`** (Lock IC=+0.0669, Sharpe=-0.8535)
- Yearly ICs: 2017: +0.145 | 2018: +0.167 | 2019: +0.118 | 2020: +0.047 | 2021: +0.073 | 2022: +0.090 | 2023: +0.082 | 2024: +0.112
- IC CV=0.35, Neg years=0/8, Half ratio=0.84, Recency ratio=0.62
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.013, Q3_mid=+0.078, Q4=+0.112, Q5_high_vol=+0.120

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0639, Sharpe=-0.6077)
- Yearly ICs: 2017: +0.213 | 2018: +0.254 | 2019: +0.156 | 2020: +0.136 | 2021: +0.098 | 2022: +0.055 | 2023: +0.068 | 2024: +0.125
- IC CV=0.46, Neg years=0/8, Half ratio=0.49, Recency ratio=0.41
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.157, Q2=-0.001, Q3_mid=+0.135, Q4=+0.150, Q5_high_vol=+0.191

**`combo_max__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0613, Sharpe=-0.7320)
- Yearly ICs: 2017: +0.145 | 2018: +0.123 | 2019: +0.069 | 2020: +0.111 | 2021: +0.019 | 2022: +0.121 | 2023: +0.070 | 2024: +0.083
- IC CV=0.41, Neg years=0/8, Half ratio=0.69, Recency ratio=0.57
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.036, Q3_mid=+0.093, Q4=+0.084, Q5_high_vol=+0.095

**`combo_z_sum__close_vs_open_range__high_low_sequence_momentum`** (Lock IC=+0.0532, Sharpe=-0.6770)
- Yearly ICs: 2017: +0.190 | 2018: +0.117 | 2019: +0.065 | 2020: +0.102 | 2021: +0.059 | 2022: +0.097 | 2023: +0.078 | 2024: +0.133
- IC CV=0.38, Neg years=0/8, Half ratio=0.95, Recency ratio=0.69
- Weak component: `high_low_sequence_momentum` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.022, Q3_mid=+0.112, Q4=+0.085, Q5_high_vol=+0.112

**`combo_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0486, Sharpe=-0.6142)
- Yearly ICs: 2017: +0.145 | 2018: +0.224 | 2019: +0.146 | 2020: +0.088 | 2021: +0.104 | 2022: +0.063 | 2023: +0.062 | 2024: +0.118
- IC CV=0.42, Neg years=0/8, Half ratio=0.60, Recency ratio=0.49
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.138, Q2=-0.009, Q3_mid=+0.079, Q4=+0.144, Q5_high_vol=+0.180

**`combo_mean__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0469, Sharpe=-1.2311)
- Yearly ICs: 2017: +0.214 | 2018: +0.198 | 2019: +0.106 | 2020: +0.115 | 2021: +0.099 | 2022: +0.097 | 2023: +0.078 | 2024: +0.153
- IC CV=0.36, Neg years=0/8, Half ratio=0.79, Recency ratio=0.56
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.229, Q2=+0.005, Q3_mid=+0.124, Q4=+0.126, Q5_high_vol=+0.159

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0457, Sharpe=-0.3399)
- Yearly ICs: 2017: +0.154 | 2018: +0.193 | 2019: +0.168 | 2020: +0.190 | 2021: +0.151 | 2022: +0.035 | 2023: +0.095 | 2024: +0.134
- IC CV=0.35, Neg years=0/8, Half ratio=0.66, Recency ratio=0.66
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.001, Q3_mid=+0.132, Q4=+0.119, Q5_high_vol=+0.223

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0451, Sharpe=-0.8388)
- Yearly ICs: 2017: +0.192 | 2018: +0.218 | 2019: +0.121 | 2020: +0.145 | 2021: +0.156 | 2022: +0.058 | 2023: +0.093 | 2024: +0.118
- IC CV=0.35, Neg years=0/8, Half ratio=0.68, Recency ratio=0.51
- Weak component: `early_late_momentum_divergence` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.000, Q3_mid=+0.080, Q4=+0.157, Q5_high_vol=+0.209

**`combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0383, Sharpe=-0.5921)
- Yearly ICs: 2017: +0.236 | 2018: +0.134 | 2019: +0.080 | 2020: +0.161 | 2021: +0.091 | 2022: +0.106 | 2023: +0.114 | 2024: +0.077
- IC CV=0.40, Neg years=0/8, Half ratio=0.69, Recency ratio=0.52
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.010, Q3_mid=+0.176, Q4=+0.086, Q5_high_vol=+0.130

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0337, Sharpe=-1.4167)
- Yearly ICs: 2017: +0.201 | 2018: +0.209 | 2019: +0.129 | 2020: +0.142 | 2021: +0.089 | 2022: +0.105 | 2023: +0.119 | 2024: +0.137
- IC CV=0.28, Neg years=0/8, Half ratio=0.73, Recency ratio=0.62
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.010, Q3_mid=+0.120, Q4=+0.127, Q5_high_vol=+0.210

**`vwap_close_divergence_trend`** (Lock IC=+0.0323, Sharpe=-0.2960)
- Yearly ICs: 2017: +0.184 | 2018: +0.055 | 2019: +0.091 | 2020: +0.075 | 2021: +0.069 | 2022: +0.094 | 2023: +0.107 | 2024: +0.092
- IC CV=0.38, Neg years=0/8, Half ratio=1.19, Recency ratio=0.83
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.058, Q3_mid=+0.094, Q4=+0.045, Q5_high_vol=+0.084

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0289, Sharpe=-0.4555)
- Yearly ICs: 2017: +0.142 | 2018: +0.284 | 2019: +0.177 | 2020: +0.173 | 2021: +0.171 | 2022: +0.055 | 2023: +0.093 | 2024: +0.161
- IC CV=0.40, Neg years=0/8, Half ratio=0.65, Recency ratio=0.59
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.005, Q3_mid=+0.133, Q4=+0.139, Q5_high_vol=+0.259

**`combo_sig_product__high_low_sequence_momentum__first_bar_return`** (Lock IC=+0.0279, Sharpe=-0.5752)
- Yearly ICs: 2017: +0.150 | 2018: +0.180 | 2019: +0.078 | 2020: +0.065 | 2021: +0.075 | 2022: +0.090 | 2023: +0.054 | 2024: +0.132
- IC CV=0.41, Neg years=0/8, Half ratio=0.95, Recency ratio=0.56
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.004, Q3_mid=+0.111, Q4=+0.109, Q5_high_vol=+0.157

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0268, Sharpe=-1.5867)
- Yearly ICs: 2017: +0.166 | 2018: +0.244 | 2019: +0.128 | 2020: +0.103 | 2021: +0.157 | 2022: +0.085 | 2023: +0.082 | 2024: +0.148
- IC CV=0.36, Neg years=0/8, Half ratio=0.80, Recency ratio=0.56
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.015, Q3_mid=+0.104, Q4=+0.142, Q5_high_vol=+0.219

**`combo_sig_product__net_volume_flow__bar_ret_0`** (Lock IC=+0.0245, Sharpe=-0.5104)
- Yearly ICs: 2017: +0.155 | 2018: +0.199 | 2019: +0.138 | 2020: +0.068 | 2021: +0.044 | 2022: +0.058 | 2023: +0.067 | 2024: +0.054
- IC CV=0.55, Neg years=0/8, Half ratio=0.41, Recency ratio=0.34
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.033, Q3_mid=+0.066, Q4=+0.113, Q5_high_vol=+0.117

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0205, Sharpe=-0.7130)
- Yearly ICs: 2017: +0.116 | 2018: +0.278 | 2019: +0.078 | 2020: +0.109 | 2021: +0.083 | 2022: +0.128 | 2023: +0.036 | 2024: +0.101
- IC CV=0.57, Neg years=0/8, Half ratio=0.65, Recency ratio=0.35
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.006, Q3_mid=+0.062, Q4=+0.118, Q5_high_vol=+0.180

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0126, Sharpe=-2.1701)
- Yearly ICs: 2017: +0.155 | 2018: +0.225 | 2019: +0.081 | 2020: +0.134 | 2021: +0.102 | 2022: +0.108 | 2023: +0.080 | 2024: +0.124
- IC CV=0.35, Neg years=0/8, Half ratio=0.74, Recency ratio=0.54
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.016, Q3_mid=+0.129, Q4=+0.151, Q5_high_vol=+0.147

### 159915ETF — `single` Median Features

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1161, Sharpe=-0.1261)
- Yearly ICs: 2017: +0.029 | 2018: +0.133 | 2019: +0.128 | 2020: +0.137 | 2021: +0.158 | 2022: +0.146 | 2023: +0.134 | 2024: +0.077
- IC CV=0.34, Neg years=0/8, Half ratio=1.23, Recency ratio=1.29
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.122, Q3_mid=+0.079, Q4=+0.118, Q5_high_vol=+0.169

**`combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1079, Sharpe=-0.2788)
- Yearly ICs: 2017: -0.058 | 2018: +0.036 | 2019: +0.135 | 2020: +0.037 | 2021: +0.133 | 2022: +0.143 | 2023: +0.143 | 2024: +0.054
- IC CV=0.88, Neg years=1/8, Half ratio=2.54, Recency ratio=-8.81
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.046, Q3_mid=+0.091, Q4=+0.116, Q5_high_vol=+0.131

**`combo_rank_max__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0919, Sharpe=-0.8343)
- Yearly ICs: 2017: +0.034 | 2018: +0.085 | 2019: +0.126 | 2020: +0.074 | 2021: +0.172 | 2022: +0.175 | 2023: +0.139 | 2024: +0.082
- IC CV=0.42, Neg years=0/8, Half ratio=1.85, Recency ratio=1.86
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.124, Q3_mid=+0.076, Q4=+0.117, Q5_high_vol=+0.146

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0882, Sharpe=-1.0149)
- Yearly ICs: 2017: +0.001 | 2018: +0.087 | 2019: +0.180 | 2020: +0.127 | 2021: +0.163 | 2022: +0.107 | 2023: +0.152 | 2024: +0.062
- IC CV=0.50, Neg years=0/8, Half ratio=1.47, Recency ratio=2.43
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.090, Q3_mid=+0.099, Q4=+0.098, Q5_high_vol=+0.129

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0772, Sharpe=-0.5386)
- Yearly ICs: 2017: +0.064 | 2018: +0.068 | 2019: +0.175 | 2020: +0.065 | 2021: +0.219 | 2022: +0.089 | 2023: +0.165 | 2024: +0.078
- IC CV=0.50, Neg years=0/8, Half ratio=1.77, Recency ratio=1.84
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.100, Q3_mid=+0.135, Q4=+0.115, Q5_high_vol=+0.121

**`combo_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0753, Sharpe=-0.7836)
- Yearly ICs: 2017: +0.038 | 2018: +0.070 | 2019: +0.173 | 2020: +0.097 | 2021: +0.183 | 2022: +0.110 | 2023: +0.189 | 2024: +0.081
- IC CV=0.46, Neg years=0/8, Half ratio=1.68, Recency ratio=2.50
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.092, Q3_mid=+0.140, Q4=+0.094, Q5_high_vol=+0.144

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_rank_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0808, Sharpe=+0.3659)
- Yearly ICs: 2017: -0.039 | 2018: +0.157 | 2019: +0.133 | 2020: +0.031 | 2021: +0.124 | 2022: +0.029 | 2023: +0.133 | 2024: +0.038
- IC CV=0.86, Neg years=1/8, Half ratio=1.04, Recency ratio=1.45
- Weak component: `limit_down_proximity_early` (CV=2.51)

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1108, Sharpe=+1.2537)
- Yearly ICs: 2017: +0.190 | 2018: +0.142 | 2019: +0.181 | 2020: +0.142 | 2021: +0.093 | 2022: +0.048 | 2023: +0.069 | 2024: +0.097
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.50
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1502, Sharpe=+1.1714)
- Yearly ICs: 2017: +0.167 | 2018: +0.148 | 2019: +0.174 | 2020: +0.083 | 2021: +0.082 | 2022: +0.053 | 2023: +0.110 | 2024: +0.162
- IC CV=0.35, Neg years=0/8, Half ratio=0.72, Recency ratio=0.86
- Weak component: `max_down_ret` (CV=0.55)

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1041, Sharpe=+0.7497)
- Yearly ICs: 2017: +0.129 | 2018: +0.203 | 2019: +0.177 | 2020: +0.184 | 2021: +0.122 | 2022: +0.050 | 2023: +0.062 | 2024: +0.112
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.53
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1136, Sharpe=+0.6574)
- Yearly ICs: 2017: +0.137 | 2018: +0.191 | 2019: +0.196 | 2020: +0.194 | 2021: +0.142 | 2022: +0.064 | 2023: +0.067 | 2024: +0.123
- IC CV=0.36, Neg years=0/8, Half ratio=0.57, Recency ratio=0.58
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0958, Sharpe=+0.5075)
- Yearly ICs: 2017: +0.215 | 2018: +0.201 | 2019: +0.175 | 2020: +0.145 | 2021: +0.098 | 2022: +0.039 | 2023: +0.079 | 2024: +0.090
- IC CV=0.45, Neg years=0/8, Half ratio=0.41, Recency ratio=0.41
- Weak component: `bar_ret_0` (CV=0.46)

**`combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0998, Sharpe=+0.3882)
- Yearly ICs: 2017: +0.208 | 2018: +0.105 | 2019: +0.101 | 2020: +0.097 | 2021: +0.096 | 2022: +0.052 | 2023: +0.103 | 2024: +0.136
- IC CV=0.37, Neg years=0/8, Half ratio=0.89, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0920, Sharpe=+0.2951)
- Yearly ICs: 2017: +0.219 | 2018: +0.204 | 2019: +0.175 | 2020: +0.134 | 2021: +0.087 | 2022: +0.047 | 2023: +0.079 | 2024: +0.088
- IC CV=0.46, Neg years=0/8, Half ratio=0.40, Recency ratio=0.39
- Weak component: `bar_ret_0` (CV=0.46)

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1138, Sharpe=+0.2628)
- Yearly ICs: 2017: +0.196 | 2018: +0.105 | 2019: +0.176 | 2020: +0.076 | 2021: +0.087 | 2022: +0.089 | 2023: +0.057 | 2024: +0.164
- IC CV=0.41, Neg years=0/8, Half ratio=0.83, Recency ratio=0.74
- Weak component: `star50_limit_proximity_early` (CV=0.50)

**`combo_z_sum__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0970, Sharpe=+0.1808)
- Yearly ICs: 2017: +0.233 | 2018: +0.100 | 2019: +0.110 | 2020: +0.116 | 2021: +0.047 | 2022: +0.058 | 2023: +0.046 | 2024: +0.103
- IC CV=0.55, Neg years=0/8, Half ratio=0.56, Recency ratio=0.45
- Weak component: `max_down_ret` (CV=0.55)

### 159915ETF — `single` True Positives

**`combo_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1307, Sharpe=+1.7816)
- Yearly ICs: 2017: -0.006 | 2018: +0.097 | 2019: +0.227 | 2020: +0.043 | 2021: +0.155 | 2022: +0.034 | 2023: +0.154 | 2024: +0.136
- IC CV=0.69, Neg years=1/8, Half ratio=1.41, Recency ratio=3.20
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.1527, Sharpe=+1.5226)
- Yearly ICs: 2017: -0.011 | 2018: +0.073 | 2019: +0.222 | 2020: +0.103 | 2021: +0.111 | 2022: +0.093 | 2023: +0.161 | 2024: +0.064
- IC CV=0.63, Neg years=1/8, Half ratio=1.16, Recency ratio=3.62
- Weak component: `limit_down_proximity_early` (CV=0.71)

**`combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1361, Sharpe=+1.5184)
- Yearly ICs: 2017: -0.021 | 2018: +0.149 | 2019: +0.236 | 2020: +0.163 | 2021: +0.125 | 2022: +0.103 | 2023: +0.121 | 2024: +0.099
- IC CV=0.56, Neg years=1/8, Half ratio=0.92, Recency ratio=1.72
- Weak component: `first_bar_sentiment` (CV=0.86)

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1617, Sharpe=+1.1078)
- Yearly ICs: 2017: -0.057 | 2018: +0.093 | 2019: +0.245 | 2020: +0.120 | 2021: +0.099 | 2022: +0.061 | 2023: +0.135 | 2024: +0.095
- IC CV=0.79, Neg years=1/8, Half ratio=1.08, Recency ratio=6.24
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0891, Sharpe=+1.0541)
- Yearly ICs: 2017: +0.030 | 2018: +0.128 | 2019: +0.152 | 2020: +0.098 | 2021: +0.188 | 2022: +0.125 | 2023: +0.171 | 2024: +0.119
- IC CV=0.36, Neg years=0/8, Half ratio=1.66, Recency ratio=1.85
- Weak component: `impulse_bar_dominance` (CV=0.77)

**`combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1394, Sharpe=+0.9587)
- Yearly ICs: 2017: -0.072 | 2018: +0.110 | 2019: +0.111 | 2020: +0.091 | 2021: +0.047 | 2022: +0.170 | 2023: +0.132 | 2024: +0.102
- IC CV=0.79, Neg years=1/8, Half ratio=1.44, Recency ratio=6.15
- Weak component: `yesterday_first_30min_return` (CV=0.99)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1307, Sharpe=+0.9421)
- Yearly ICs: 2017: +0.035 | 2018: +0.080 | 2019: +0.202 | 2020: +0.147 | 2021: +0.150 | 2022: +0.125 | 2023: +0.152 | 2024: +0.090
- IC CV=0.40, Neg years=0/8, Half ratio=1.17, Recency ratio=2.11
- Weak component: `first_bar_sentiment` (CV=0.86)

**`combo_rank_max__first_bar_sentiment__star50_limit_proximity_early`** (Lock IC=+0.0725, Sharpe=+0.9220)
- Yearly ICs: 2017: -0.025 | 2018: +0.101 | 2019: +0.165 | 2020: +0.151 | 2021: +0.108 | 2022: +0.081 | 2023: +0.074 | 2024: +0.074
- IC CV=0.59, Neg years=1/8, Half ratio=0.99, Recency ratio=1.93
- Weak component: `first_bar_sentiment` (CV=0.86)

**`combo_min__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1466, Sharpe=+0.8978)
- Yearly ICs: 2017: -0.028 | 2018: +0.079 | 2019: +0.250 | 2020: +0.117 | 2021: +0.094 | 2022: +0.059 | 2023: +0.126 | 2024: +0.082
- IC CV=0.75, Neg years=1/8, Half ratio=0.90, Recency ratio=4.02
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)

**`combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1210, Sharpe=+0.8612)
- Yearly ICs: 2017: +0.025 | 2018: +0.143 | 2019: +0.211 | 2020: +0.141 | 2021: +0.158 | 2022: +0.125 | 2023: +0.156 | 2024: +0.125
- IC CV=0.36, Neg years=0/8, Half ratio=1.12, Recency ratio=1.66
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1275, Sharpe=+0.8333)
- Yearly ICs: 2017: -0.024 | 2018: +0.157 | 2019: +0.245 | 2020: +0.161 | 2021: +0.143 | 2022: +0.085 | 2023: +0.178 | 2024: +0.127
- IC CV=0.55, Neg years=1/8, Half ratio=1.05, Recency ratio=2.29
- Weak component: `bar_body_rng_0` (CV=0.63)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1325, Sharpe=+0.7977)
- Yearly ICs: 2017: +0.010 | 2018: +0.115 | 2019: +0.210 | 2020: +0.161 | 2021: +0.160 | 2022: +0.131 | 2023: +0.164 | 2024: +0.082
- IC CV=0.44, Neg years=0/8, Half ratio=1.13, Recency ratio=1.98
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0659, Sharpe=+0.7397)
- Yearly ICs: 2017: +0.008 | 2018: +0.135 | 2019: +0.197 | 2020: +0.110 | 2021: +0.134 | 2022: +0.058 | 2023: +0.150 | 2024: +0.061
- IC CV=0.53, Neg years=0/8, Half ratio=0.94, Recency ratio=1.48
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_z_sum__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0739, Sharpe=+0.7136)
- Yearly ICs: 2017: +0.053 | 2018: +0.088 | 2019: +0.199 | 2020: +0.065 | 2021: +0.177 | 2022: +0.039 | 2023: +0.150 | 2024: +0.063
- IC CV=0.55, Neg years=0/8, Half ratio=1.22, Recency ratio=1.51
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_ratio__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1308, Sharpe=+0.7043)
- Yearly ICs: 2017: -0.012 | 2018: +0.072 | 2019: +0.170 | 2020: +0.085 | 2021: +0.112 | 2022: +0.141 | 2023: +0.103 | 2024: +0.117
- IC CV=0.52, Neg years=1/8, Half ratio=1.38, Recency ratio=3.68
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1511, Sharpe=+0.6805)
- Yearly ICs: 2017: -0.005 | 2018: +0.046 | 2019: +0.156 | 2020: +0.089 | 2021: +0.151 | 2022: +0.116 | 2023: +0.162 | 2024: +0.082
- IC CV=0.55, Neg years=1/8, Half ratio=1.85, Recency ratio=5.93
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1101, Sharpe=+0.6443)
- Yearly ICs: 2017: +0.024 | 2018: +0.078 | 2019: +0.172 | 2020: +0.110 | 2021: +0.139 | 2022: +0.145 | 2023: +0.176 | 2024: +0.111
- IC CV=0.40, Neg years=0/8, Half ratio=1.56, Recency ratio=2.83
- Weak component: `impulse_bar_dominance` (CV=0.77)

**`combo_mean__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1320, Sharpe=+0.6019)
- Yearly ICs: 2017: +0.042 | 2018: +0.134 | 2019: +0.221 | 2020: +0.070 | 2021: +0.190 | 2022: +0.063 | 2023: +0.114 | 2024: +0.107
- IC CV=0.50, Neg years=0/8, Half ratio=1.05, Recency ratio=1.26
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1286, Sharpe=+0.5529)
- Yearly ICs: 2017: -0.047 | 2018: +0.084 | 2019: +0.131 | 2020: +0.102 | 2021: +0.033 | 2022: +0.180 | 2023: +0.115 | 2024: +0.083
- IC CV=0.75, Neg years=1/8, Half ratio=1.22, Recency ratio=5.34
- Weak component: `yesterday_first_30min_return` (CV=0.99)

**`combo_sig_product__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0904, Sharpe=+0.5068)
- Yearly ICs: 2017: +0.017 | 2018: +0.137 | 2019: +0.145 | 2020: +0.154 | 2021: +0.154 | 2022: +0.076 | 2023: +0.187 | 2024: +0.078
- IC CV=0.44, Neg years=0/8, Half ratio=1.19, Recency ratio=1.72
- Weak component: `bar_body_rng_0` (CV=0.63)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1283, Sharpe=+0.4172)
- Yearly ICs: 2017: -0.008 | 2018: +0.152 | 2019: +0.236 | 2020: +0.148 | 2021: +0.129 | 2022: +0.103 | 2023: +0.136 | 2024: +0.075
- IC CV=0.54, Neg years=1/8, Half ratio=0.88, Recency ratio=1.46
- Weak component: `bar_ret_0` (CV=0.48)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0679, Sharpe=+0.4043)
- Yearly ICs: 2017: +0.003 | 2018: +0.043 | 2019: +0.038 | 2020: +0.119 | 2021: +0.141 | 2022: +0.130 | 2023: +0.126 | 2024: +0.093
- IC CV=0.56, Neg years=0/8, Half ratio=2.94, Recency ratio=4.76
- Weak component: `impulse_bar_dominance` (CV=0.77)

**`combo_mean__star50_limit_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1222, Sharpe=+0.2742)
- Yearly ICs: 2017: +0.006 | 2018: +0.080 | 2019: +0.117 | 2020: +0.101 | 2021: +0.145 | 2022: +0.159 | 2023: +0.116 | 2024: +0.106
- IC CV=0.42, Neg years=0/8, Half ratio=1.73, Recency ratio=2.57
- Weak component: `impulse_bar_dominance` (CV=0.77)

**`combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1073, Sharpe=+0.1834)
- Yearly ICs: 2017: +0.033 | 2018: +0.122 | 2019: +0.197 | 2020: +0.149 | 2021: +0.137 | 2022: +0.137 | 2023: +0.160 | 2024: +0.139
- IC CV=0.32, Neg years=0/8, Half ratio=1.11, Recency ratio=1.93
- Weak component: `bar_ret_0` (CV=0.48)

**`combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0673, Sharpe=+0.1332)
- Yearly ICs: 2017: +0.029 | 2018: +0.086 | 2019: +0.185 | 2020: +0.048 | 2021: +0.159 | 2022: +0.052 | 2023: +0.180 | 2024: +0.083
- IC CV=0.57, Neg years=0/8, Half ratio=1.59, Recency ratio=2.30
- Weak component: `volume_weighted_price_position` (CV=0.77)

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0930, Sharpe=+0.0368)
- Yearly ICs: 2017: +0.026 | 2018: +0.126 | 2019: +0.193 | 2020: +0.113 | 2021: +0.134 | 2022: +0.107 | 2023: +0.172 | 2024: +0.073
- IC CV=0.42, Neg years=0/8, Half ratio=1.13, Recency ratio=1.61
- Weak component: `bar_ret_0` (CV=0.48)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0684, Sharpe=+0.0306)
- Yearly ICs: 2017: -0.037 | 2018: +0.058 | 2019: +0.165 | 2020: +0.079 | 2021: +0.086 | 2022: +0.109 | 2023: +0.155 | 2024: +0.149
- IC CV=0.65, Neg years=1/8, Half ratio=1.63, Recency ratio=14.55
- Weak component: `star50_limit_proximity_early` (CV=0.52)

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Median | fast | +0.1178 | -0.1506 | -0.1506 | 1y |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | Median | fast | +0.1057 | -0.1387 | -0.1387 | 1y |
| `combo_max__max_up_ret__volume_weighted_price_position` | FP | fast | +0.0964 | -0.2004 | -0.2004 | 1y |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0962 | +0.0468 | +0.0468 | 1y |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Median | fast | +0.0845 | -0.0552 | -0.0552 | 1y |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Median | fast | +0.0807 | -0.0428 | -0.0428 | 1y |
| `combo_max__max_up_ret__volume_surge_direction` | FP | fast | +0.0750 | -0.1448 | -0.1448 | 1y |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0743 | +0.0631 | +0.0631 | ∞ |
| `combo_min__max_up_ret__volume_surge_direction` | Median | fast | +0.0673 | -0.0609 | -0.0609 | 1y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Median | fast | +0.0586 | -0.0625 | -0.0625 | 1y |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0569 | -0.1658 | -0.1658 | 1y |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | Median | persistent | +0.0528 | +0.0124 | +0.0124 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | fast | +0.0527 | -0.0140 | -0.0140 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | fast | +0.0467 | -0.0313 | -0.0313 | 1y |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | fast | +0.0419 | -0.0169 | -0.0169 | 1y |
| `combo_sig_product__first_bar_sentiment__opening_drive_thrust_ratio` | FP | fast | +0.0220 | -0.0912 | -0.0912 | 1y |
| `combo_diff__max_up_ret__early_vwap_acceleration` | FP | fast | +0.0218 | -0.0859 | -0.0859 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | FP | fast | +0.0216 | -0.0774 | -0.0774 | 1y |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.0207 | -0.0951 | -0.0951 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=16, gradual=0, persistent=3

**FP decay trajectories:**

- `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.021 → Y2:-0.095
- `combo_min__max_up_ret__bar_body_rng_0`: Y1:+0.022 → Y2:-0.077
- `combo_diff__max_up_ret__early_vwap_acceleration`: Y1:+0.022 → Y2:-0.086
- `combo_sig_product__first_bar_sentiment__opening_drive_thrust_ratio`: Y1:+0.022 → Y2:-0.091
- `combo_mean__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.057 → Y2:-0.166
- `combo_max__max_up_ret__volume_surge_direction`: Y1:+0.075 → Y2:-0.145
- `combo_max__max_up_ret__volume_weighted_price_position`: Y1:+0.096 → Y2:-0.200

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Median | fast | +0.1941 | -0.0734 | -0.0734 | 1y |
| `combo_z_sum__close_vs_open_range__high_low_sequence_momentum` | Median | fast | +0.1430 | -0.0685 | -0.0685 | 1y |
| `vwap_close_divergence_trend` | Median | fast | +0.1327 | -0.0940 | -0.0940 | 1y |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1275 | +0.0743 | +0.0743 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1260 | +0.0780 | +0.0780 | ∞ |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | Median | fast | +0.1255 | -0.1226 | -0.1226 | 1y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | fast | +0.1239 | -0.1216 | -0.1216 | 1y |
| `combo_mean__close_vs_open_range__bar_ret_0` | Median | fast | +0.1198 | -0.0391 | -0.0391 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1192 | +0.0805 | +0.0805 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | fast | +0.1192 | -0.0517 | -0.0517 | 1y |
| `combo_rank_min__early_body_momentum__bar_ret_0` | Median | persistent | +0.1187 | +0.0111 | +0.0111 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.1158 | +0.0713 | +0.0713 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Median | persistent | +0.1127 | +0.0049 | +0.0049 | 1y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1083 | +0.1990 | +0.1990 | ∞ |
| `combo_sig_product__net_volume_flow__bar_ret_0` | Median | fast | +0.1079 | -0.0996 | -0.0996 | 1y |
| `combo_min__first_bar_sentiment__bar_ret_0` | Median | fast | +0.1049 | -0.0093 | -0.0093 | 1y |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | Median | persistent | +0.1048 | +0.0149 | +0.0149 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | fast | +0.0978 | -0.0539 | -0.0539 | 1y |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0971 | +0.1049 | +0.1049 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Median | persistent | +0.0944 | +0.0858 | +0.0858 | ∞ |
| `early_order_flow_imbalance` | FP | fast | +0.0913 | -0.1345 | -0.1345 | 1y |
| `combo_max__max_up_ret__bar_ret_0` | Median | fast | +0.0912 | -0.0638 | -0.0638 | 1y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0889 | +0.1750 | +0.1750 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | Median | fast | +0.0731 | -0.0782 | -0.0782 | 1y |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0602 | +0.1848 | +0.1848 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | fast | +0.0601 | -0.0041 | -0.0041 | 1y |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0578 | +0.1809 | +0.1809 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.0558 | +0.0389 | +0.0389 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0391 | +0.2313 | +0.2313 | ∞ |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0129 | +0.0895 | +0.0895 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=14, gradual=0, persistent=16

**FP decay trajectories:**

- `early_order_flow_imbalance`: Y1:+0.091 → Y2:-0.135

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1959 | +0.0869 | +0.0869 | 1y |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Median | fast | +0.1854 | -0.0560 | -0.0560 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1810 | +0.0155 | +0.0155 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1803 | +0.0582 | +0.0582 | 1y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Median | fast | +0.1777 | -0.0708 | -0.0708 | 1y |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1762 | -0.0741 | -0.0741 | 1y |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | TP | fast | +0.1761 | -0.0143 | -0.0143 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.1750 | +0.1164 | +0.1164 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1730 | +0.0733 | +0.0733 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | TP | fast | +0.1717 | -0.0766 | -0.0766 | 1y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1696 | +0.1445 | +0.1445 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.1637 | +0.0055 | +0.0055 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | fast | +0.1618 | -0.0105 | -0.0105 | 1y |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1617 | +0.0744 | +0.0744 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1594 | +0.0841 | +0.0841 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1544 | +0.1001 | +0.1001 | ∞ |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1537 | +0.1220 | +0.1220 | ∞ |
| `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1475 | +0.1024 | +0.1024 | ∞ |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1468 | +0.1163 | +0.1163 | ∞ |
| `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1456 | +0.1168 | +0.1168 | ∞ |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | TP | persistent | +0.1352 | +0.0002 | +0.0002 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Median | persistent | +0.1348 | +0.1140 | +0.1140 | ∞ |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.1325 | +0.0600 | +0.0600 | 1y |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1313 | +0.1302 | +0.1302 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1291 | +0.1272 | +0.1272 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1247 | +0.1472 | +0.1472 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1193 | +0.0120 | +0.0120 | 1y |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.1143 | +0.0098 | +0.0098 | 1y |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1078 | +0.1691 | +0.1691 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1014 | +0.1299 | +0.1299 | ∞ |
| `combo_rank_max__first_bar_sentiment__star50_limit_proximity_early` | TP | persistent | +0.0786 | +0.0812 | +0.0812 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Median | persistent | +0.0655 | +0.1661 | +0.1661 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0612 | +0.0874 | +0.0874 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=6, gradual=0, persistent=27

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 7/20 top rejects are profitable (35%)

- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449

**B2 Rolling Guard**: 2/20 top rejects are profitable (10%)

- `combo_product__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Sharpe=+0.4529
- `combo_product__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Sharpe=+0.4529

**B3 Composite Floor**: 6/20 top rejects are profitable (30%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Sharpe=+0.3783

**B4 Correlation Gate**: 7/20 top rejects are profitable (35%)

- `combo_mean__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Sharpe=+0.3895
- `combo_z_sum__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Sharpe=+0.3895
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2314, Lock IC=+0.0813, Sharpe=+0.3659

### 500ETF — `single`

**7-Year Jackknife**: 11/20 top rejects are profitable (55%)

- `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`: Train IC=+0.2240, Lock IC=+0.0599, Sharpe=+0.6347
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340

**B2 Rolling Guard**: 3/20 top rejects are profitable (15%)

- `combo_min__late_bar_momentum__double_bottom_bull_flag_early`: Train IC=+0.1190, Lock IC=+0.0815, Sharpe=+1.0361
- `combo_tri_max__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.1364, Lock IC=+0.0622, Sharpe=+0.0218
- `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__volume_weighted_momentum_acceleration`: Train IC=+0.1364, Lock IC=+0.0622, Sharpe=+0.0218

**Temporal Validation Gate**: 1/20 top rejects are profitable (5%)

- `combo_clamp_diff__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.2712, Lock IC=+0.0638, Sharpe=+0.3186

**BH-FDR Gate**: 1/9 top rejects are profitable (11%)

- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0658, Lock IC=+0.0308, Sharpe=+1.1651

**B3 Composite Floor**: 3/20 top rejects are profitable (15%)

- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__volatility_expansion_trend_vector`: Train IC=+0.2848, Lock IC=+0.0631, Sharpe=+0.3988
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2699, Lock IC=+0.0867, Sharpe=+0.2984
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__volatility_expansion_trend_vector`: Train IC=+0.2568, Lock IC=+0.0991, Sharpe=+0.2078

### 159915ETF — `single`

**7-Year Jackknife**: 15/20 top rejects are profitable (75%)

- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.9095
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.9095
- `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2346, Lock IC=+0.1159, Sharpe=+0.7959

**B2 Rolling Guard**: 13/20 top rejects are profitable (65%)

- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1528, Lock IC=+0.1099, Sharpe=+0.9501

**Temporal Validation Gate**: 15/20 top rejects are profitable (75%)

- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1987, Lock IC=+0.1447, Sharpe=+1.1411

**BH-FDR Gate**: 5/11 top rejects are profitable (45%)

- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.0740, Lock IC=+0.0759, Sharpe=+1.4912
- `combo_rank_min__first_bar_sentiment__first_bar_return`: Train IC=+0.0740, Lock IC=+0.0759, Sharpe=+1.4912
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0545, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor**: 18/20 top rejects are profitable (90%)

- `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Sharpe=+1.8637
- `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Sharpe=+1.8637
- `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2511, Lock IC=+0.1316, Sharpe=+1.5377

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3363, Lock IC=+0.1300, Sharpe=+1.5827
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1110 | 78 | 25 | 31 | 22 | 32% | 28% |
| B2 Rolling Guard | 52 | 52 | 27 | 21 | 4 | 52% | 8% |
| Temporal Validation Gate | 179 | 78 | 24 | 43 | 11 | 31% | 14% |
| BH-FDR Gate | 5 | 5 | 2 | 3 | 0 | 40% | 0% |
| B3 Composite Floor | 268 | 78 | 31 | 28 | 19 | 40% | 24% |
| B4 Correlation Gate | 120 | 78 | 30 | 37 | 11 | 38% | 14% |

**7-Year Jackknife** — top TP casualties:
- `combo_product__volume_weighted_momentum_acceleration__bar_body_rng_0`: Train IC=-0.0452, Lock IC=+0.0955, Sharpe=+1.1328
- `combo_rank_min__volume_weighted_momentum_acceleration__volume_surge_direction`: Train IC=-0.0480, Lock IC=+0.0083, Sharpe=+0.5340
- `combo_min__volume_weighted_momentum_acceleration__volume_surge_direction`: Train IC=-0.0447, Lock IC=+0.0013, Sharpe=+0.4875

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.1881, Lock IC=+0.0554, Sharpe=+0.3937
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.1881, Lock IC=+0.0554, Sharpe=+0.3937
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1797 | 78 | 14 | 25 | 39 | 18% | 50% |
| B2 Rolling Guard | 119 | 78 | 42 | 26 | 10 | 54% | 13% |
| Temporal Validation Gate | 281 | 78 | 20 | 45 | 13 | 26% | 17% |
| BH-FDR Gate | 9 | 9 | 2 | 6 | 1 | 22% | 11% |
| B3 Composite Floor | 516 | 78 | 3 | 62 | 13 | 4% | 17% |
| B4 Correlation Gate | 235 | 78 | 0 | 59 | 19 | 0% | 24% |

**7-Year Jackknife** — top TP casualties:
- `combo_abs_diff__first_bar_sentiment__close_vs_open_range`: Train IC=-0.0485, Lock IC=+0.1194, Sharpe=+1.1363
- `combo_tri_sig_max__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression`: Train IC=-0.0452, Lock IC=+0.1273, Sharpe=+1.0014
- `measured_move_proximity`: Train IC=-0.1018, Lock IC=+0.0769, Sharpe=+0.9457

**B4 Correlation Gate** — top TP casualties:
- `combo_mean__star50_limit_proximity_early__high_low_sequence_momentum`: Train IC=+0.2210, Lock IC=+0.1042, Sharpe=+0.8025
- `combo_z_sum__star50_limit_proximity_early__high_low_sequence_momentum`: Train IC=+0.2210, Lock IC=+0.1042, Sharpe=+0.8025
- `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2280, Lock IC=+0.1065, Sharpe=+0.6848

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 973 | 78 | 17 | 22 | 39 | 22% | 50% |
| B2 Rolling Guard | 81 | 78 | 24 | 11 | 43 | 31% | 55% |
| Temporal Validation Gate | 68 | 68 | 9 | 21 | 38 | 13% | 56% |
| BH-FDR Gate | 11 | 11 | 2 | 4 | 5 | 18% | 45% |
| B3 Composite Floor | 322 | 78 | 3 | 26 | 49 | 4% | 63% |
| B4 Correlation Gate | 214 | 78 | 0 | 10 | 68 | 0% | 87% |

**7-Year Jackknife** — top TP casualties:
- `yesterday_illiquidity_amihud`: Train IC=+0.0550, Lock IC=+0.1294, Sharpe=+1.6004
- `combo_product__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=-0.0231, Lock IC=+0.1027, Sharpe=+1.4578
- `combo_abs_diff__first_bar_sentiment__late_bar_momentum`: Train IC=-0.0227, Lock IC=+0.0136, Sharpe=+1.0191

**B2 Rolling Guard** — top TP casualties:
- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `bar_body_rng_1`: Train IC=+0.0666, Lock IC=+0.0293, Sharpe=+1.0155

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1735, Lock IC=+0.1530, Sharpe=+1.9091
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1987, Lock IC=+0.1447, Sharpe=+1.1411

**BH-FDR Gate** — top TP casualties:
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.0740, Lock IC=+0.0759, Sharpe=+1.4912
- `combo_rank_min__first_bar_sentiment__first_bar_return`: Train IC=+0.0740, Lock IC=+0.0759, Sharpe=+1.4912
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0545, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor** — top TP casualties:
- `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Sharpe=+1.8637
- `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Sharpe=+1.8637
- `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2511, Lock IC=+0.1316, Sharpe=+1.5377

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3115, Lock IC=+0.1361, Sharpe=+1.6091
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3363, Lock IC=+0.1300, Sharpe=+1.5827
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.5184

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (179 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 134 | 50 | 16 | 0 | 34 | 32% | 0% |
| recency_ratio >= 2.5 (late-concentrated) | 45 | 45 | 22 | 1 | 22 | 49% | 2% |

**Top TP killed by recency_ratio cap:**
- `volume_acceleration`: Train IC=+0.0801, Lock IC=+0.0566, Sharpe=+0.3891

### 500ETF — `single` (281 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 228 | 50 | 0 | 7 | 43 | 0% | 14% |
| recency_ratio >= 2.5 (late-concentrated) | 53 | 50 | 7 | 4 | 39 | 14% | 8% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__close_vs_open_range__max_down_ret`: Train IC=+0.1857, Lock IC=+0.0648, Sharpe=+0.9178
- `combo_sig_product__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1662, Lock IC=+0.1335, Sharpe=+0.1748
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1290, Lock IC=+0.0260, Sharpe=+0.0966
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1290, Lock IC=+0.0260, Sharpe=+0.0966

### 159915ETF — `single` (68 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 42 | 42 | 9 | 24 | 9 | 21% | 57% |
| recency_ratio >= 2.5 (late-concentrated) | 26 | 26 | 0 | 14 | 12 | 0% | 54% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1788, Lock IC=+0.0886, Sharpe=+0.7119
- `combo_rank_max__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1788, Lock IC=+0.0886, Sharpe=+0.7119
- `combo_max__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1344, Lock IC=+0.1171, Sharpe=+0.5989
- `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1344, Lock IC=+0.1171, Sharpe=+0.5989
- `combo_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1597, Lock IC=+0.0744, Sharpe=+0.4443

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | 5 | 3 | 8 | 62% |  |
| `opening_drive_thrust_ratio` | 3 | 7 | 10 | 30% |  |
| `first_bar_sentiment` | 1 | 3 | 4 | 25% |  |
| `volume_weighted_price_position` | 2 | 6 | 8 | 25% |  |
| `bar_body_rng_0` | 1 | 5 | 6 | 17% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |
| `max_down_ret` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 10 | 10 | 0% |  |
| `limit_down_proximity_early` | 0 | 2 | 2 | 0% |  |
| `bar_ret_0` | 0 | 7 | 7 | 0% |  |
| `impulse_bar_dominance` | 0 | 4 | 4 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 2 | 2 | 0% |  |
| `star50_limit_proximity_early` | 0 | 18 | 18 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 2 | 2 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 2 | 2 | 0% |  |
| `first_bar_return` | 0 | 3 | 3 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=4, TP=19, FP rate=17%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=3, FP rate=25%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=5, FP rate=0%

