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
| 300ETF | single | 13 | 0 | 4 | 9 | 0% | 0.59 |
| 500ETF | single | 32 | 0 | 1 | 31 | 0% | 0.92 |
| 159915ETF | single | 25 | 0 | 1 | 24 | 0% | 0.94 |

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

**`combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0444, Sharpe=-0.2618)
- Yearly ICs: 2015: +0.079 | 2016: +0.087 | 2017: -0.034 | 2018: +0.174 | 2019: +0.091 | 2020: +0.046 | 2021: +0.165 | 2022: +0.025
- IC CV=0.82, Neg years=1/8, Half ratio=0.99, Recency ratio=1.14
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=-0.004, Q2=+0.014, Q3_mid=+0.072, Q4=+0.160, Q5_high_vol=+0.148

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0417, Sharpe=-0.0329)
- Yearly ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130 | 2022: +0.096
- IC CV=0.79, Neg years=1/8, Half ratio=1.45, Recency ratio=1.93
- Weak component: `limit_down_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.022, Q2=+0.005, Q3_mid=+0.048, Q4=+0.174, Q5_high_vol=+0.099

**`combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=+0.0082, Sharpe=-0.3794)
- Yearly ICs: 2015: -0.102 | 2016: -0.058 | 2017: -0.023 | 2018: -0.114 | 2019: -0.014 | 2020: +0.073 | 2021: -0.121 | 2022: -0.021
- IC CV=1.29, Neg years=7/8, Half ratio=0.31, Recency ratio=0.89
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=-0.006, Q2=-0.049, Q3_mid=-0.070, Q4=+0.026, Q5_high_vol=-0.126

**`combo_ratio__first_bar_sentiment__volume_surge_direction`** (Lock IC=+0.0048, Sharpe=-0.5873)
- Yearly ICs: 2015: +0.083 | 2016: +0.112 | 2017: +0.044 | 2018: +0.089 | 2019: +0.064 | 2020: -0.038 | 2021: +0.135 | 2022: +0.019
- IC CV=0.81, Neg years=1/8, Half ratio=0.58, Recency ratio=0.79
- Weak component: `volume_surge_direction` (CV=0.97)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.042, Q3_mid=+0.077, Q4=+0.064, Q5_high_vol=+0.086

### 500ETF — `single` Median Features

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0726, Sharpe=-0.7944)
- Yearly ICs: 2015: +0.258 | 2016: +0.143 | 2017: +0.182 | 2018: +0.238 | 2019: +0.137 | 2020: +0.141 | 2021: +0.083 | 2022: +0.110
- IC CV=0.35, Neg years=0/8, Half ratio=0.55, Recency ratio=0.48
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.005, Q3_mid=+0.193, Q4=+0.190, Q5_high_vol=+0.225

### 159915ETF — `single` Median Features

**`combo_rank_max__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0791, Sharpe=-0.4350)
- Yearly ICs: 2015: +0.165 | 2016: -0.002 | 2017: +0.034 | 2018: +0.033 | 2019: +0.047 | 2020: +0.102 | 2021: +0.143 | 2022: +0.073
- IC CV=0.73, Neg years=1/8, Half ratio=1.47, Recency ratio=1.32
- Weak component: `impulse_bar_dominance` (CV=1.03)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.018, Q3_mid=+0.111, Q4=+0.095, Q5_high_vol=+0.115

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0679, Sharpe=+1.0056)
- Yearly ICs: 2015: +0.262 | 2016: +0.095 | 2017: -0.072 | 2018: +0.144 | 2019: +0.090 | 2020: +0.062 | 2021: +0.137 | 2022: +0.048
- IC CV=0.93, Neg years=1/8, Half ratio=0.60, Recency ratio=0.52
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0876, Sharpe=+0.7186)
- Yearly ICs: 2015: +0.207 | 2016: +0.068 | 2017: -0.029 | 2018: +0.198 | 2019: +0.149 | 2020: +0.025 | 2021: +0.150 | 2022: +0.046
- IC CV=0.79, Neg years=1/8, Half ratio=0.71, Recency ratio=0.71
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`** (Lock IC=+0.0529, Sharpe=+0.5709)
- Yearly ICs: 2015: +0.129 | 2016: +0.085 | 2017: +0.014 | 2018: +0.127 | 2019: +0.038 | 2020: -0.016 | 2021: +0.121 | 2022: +0.069
- IC CV=0.72, Neg years=1/8, Half ratio=0.59, Recency ratio=0.89
- Weak component: `bar_vol_0` (CV=1.91)

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0567, Sharpe=+0.4294)
- Yearly ICs: 2015: +0.117 | 2016: +0.054 | 2017: +0.002 | 2018: +0.173 | 2019: +0.051 | 2020: -0.002 | 2021: +0.178 | 2022: +0.055
- IC CV=0.84, Neg years=1/8, Half ratio=0.72, Recency ratio=1.37
- Weak component: `volume_weighted_price_position` (CV=1.18)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0632, Sharpe=+0.3639)
- Yearly ICs: 2015: +0.243 | 2016: +0.090 | 2017: -0.044 | 2018: +0.215 | 2019: +0.118 | 2020: +0.070 | 2021: +0.175 | 2022: +0.012
- IC CV=0.84, Neg years=1/8, Half ratio=0.61, Recency ratio=0.56
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0543, Sharpe=+0.3473)
- Yearly ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.074 | 2018: +0.167 | 2019: +0.086 | 2020: +0.075 | 2021: +0.151 | 2022: +0.094
- IC CV=0.77, Neg years=1/8, Half ratio=0.75, Recency ratio=0.80
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)

**`combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0728, Sharpe=+0.2811)
- Yearly ICs: 2015: +0.235 | 2016: +0.071 | 2017: -0.078 | 2018: +0.181 | 2019: +0.107 | 2020: +0.058 | 2021: +0.158 | 2022: +0.041
- IC CV=0.94, Neg years=1/8, Half ratio=0.73, Recency ratio=0.65
- Weak component: `star50_limit_proximity_early` (CV=1.09)

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0524, Sharpe=+0.2193)
- Yearly ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156 | 2022: +0.028
- IC CV=0.65, Neg years=1/8, Half ratio=0.63, Recency ratio=0.92
- Weak component: `volume_weighted_price_position` (CV=1.18)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0662, Sharpe=+0.0044)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109
- IC CV=1.02, Neg years=1/8, Half ratio=0.66, Recency ratio=0.75

### 500ETF — `single` True Positives

**`combo_rank_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1199, Sharpe=+1.1425)
- Yearly ICs: 2015: +0.221 | 2016: +0.073 | 2017: +0.224 | 2018: +0.080 | 2019: +0.082 | 2020: +0.120 | 2021: +0.089 | 2022: +0.038
- IC CV=0.56, Neg years=0/8, Half ratio=0.55, Recency ratio=0.43
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_min__opening_auction_imbalance__star50_limit_proximity_early`** (Lock IC=+0.1134, Sharpe=+1.1317)
- Yearly ICs: 2015: +0.222 | 2016: +0.058 | 2017: +0.226 | 2018: +0.108 | 2019: +0.123 | 2020: +0.116 | 2021: +0.101 | 2022: +0.069
- IC CV=0.47, Neg years=0/8, Half ratio=0.66, Recency ratio=0.61
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0948, Sharpe=+0.9751)
- Yearly ICs: 2015: +0.289 | 2016: +0.073 | 2017: +0.197 | 2018: +0.154 | 2019: +0.172 | 2020: +0.113 | 2021: +0.095 | 2022: +0.028
- IC CV=0.54, Neg years=0/8, Half ratio=0.55, Recency ratio=0.34
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1216, Sharpe=+0.9299)
- Yearly ICs: 2015: +0.285 | 2016: +0.137 | 2017: +0.221 | 2018: +0.122 | 2019: +0.140 | 2020: +0.173 | 2021: +0.143 | 2022: +0.050
- IC CV=0.41, Neg years=0/8, Half ratio=0.60, Recency ratio=0.46
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1215, Sharpe=+0.9205)
- Yearly ICs: 2015: +0.272 | 2016: +0.044 | 2017: +0.226 | 2018: +0.142 | 2019: +0.157 | 2020: +0.153 | 2021: +0.136 | 2022: +0.030
- IC CV=0.53, Neg years=0/8, Half ratio=0.69, Recency ratio=0.52
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0913, Sharpe=+0.8496)
- Yearly ICs: 2015: +0.313 | 2016: +0.094 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.143 | 2021: +0.098 | 2022: +0.040
- IC CV=0.50, Neg years=0/8, Half ratio=0.52, Recency ratio=0.34
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1217, Sharpe=+0.8196)
- Yearly ICs: 2015: +0.280 | 2016: +0.121 | 2017: +0.223 | 2018: +0.184 | 2019: +0.172 | 2020: +0.173 | 2021: +0.142 | 2022: +0.014
- IC CV=0.44, Neg years=0/8, Half ratio=0.60, Recency ratio=0.39
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)

**`combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration`** (Lock IC=+0.0909, Sharpe=+0.6878)
- Yearly ICs: 2015: +0.221 | 2016: +0.050 | 2017: +0.158 | 2018: +0.229 | 2019: +0.171 | 2020: +0.164 | 2021: +0.163 | 2022: +0.056
- IC CV=0.41, Neg years=0/8, Half ratio=0.78, Recency ratio=0.81
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`** (Lock IC=+0.1099, Sharpe=+0.6820)
- Yearly ICs: 2015: +0.263 | 2016: +0.076 | 2017: +0.223 | 2018: +0.201 | 2019: +0.159 | 2020: +0.160 | 2021: +0.111 | 2022: +0.103
- IC CV=0.37, Neg years=0/8, Half ratio=0.66, Recency ratio=0.63
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)

**`combo_sig_product__max_up_ret__body_size_progression`** (Lock IC=+0.1031, Sharpe=+0.6726)
- Yearly ICs: 2015: +0.248 | 2016: +0.174 | 2017: +0.083 | 2018: +0.155 | 2019: +0.100 | 2020: +0.124 | 2021: +0.104 | 2022: +0.069
- IC CV=0.41, Neg years=0/8, Half ratio=0.57, Recency ratio=0.41
- Weak component: `body_size_progression` (CV=0.64)

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0916, Sharpe=+0.6369)
- Yearly ICs: 2015: +0.286 | 2016: +0.101 | 2017: +0.135 | 2018: +0.280 | 2019: +0.178 | 2020: +0.172 | 2021: +0.170 | 2022: +0.053
- IC CV=0.44, Neg years=0/8, Half ratio=0.64, Recency ratio=0.58
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)

**`combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1000, Sharpe=+0.5841)
- Yearly ICs: 2015: +0.293 | 2016: +0.126 | 2017: +0.216 | 2018: +0.215 | 2019: +0.132 | 2020: +0.169 | 2021: +0.103 | 2022: +0.083
- IC CV=0.39, Neg years=0/8, Half ratio=0.51, Recency ratio=0.44
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)

**`combo_mean__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1069, Sharpe=+0.5237)
- Yearly ICs: 2015: +0.271 | 2016: +0.087 | 2017: +0.202 | 2018: +0.107 | 2019: +0.105 | 2020: +0.125 | 2021: +0.058 | 2022: +0.078
- IC CV=0.52, Neg years=0/8, Half ratio=0.50, Recency ratio=0.38
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0840, Sharpe=+0.5104)
- Yearly ICs: 2015: +0.308 | 2016: +0.109 | 2017: +0.188 | 2018: +0.216 | 2019: +0.121 | 2020: +0.143 | 2021: +0.152 | 2022: +0.057
- IC CV=0.44, Neg years=0/8, Half ratio=0.55, Recency ratio=0.50
- Weak component: `early_late_momentum_divergence` (CV=0.70)

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1175, Sharpe=+0.4851)
- Yearly ICs: 2015: +0.266 | 2016: +0.178 | 2017: +0.079 | 2018: +0.133 | 2019: +0.078 | 2020: +0.127 | 2021: +0.110 | 2022: +0.120
- IC CV=0.42, Neg years=0/8, Half ratio=0.58, Recency ratio=0.52
- Weak component: `close_vs_open_range` (CV=0.47)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1223, Sharpe=+0.4818)
- Yearly ICs: 2015: +0.175 | 2016: +0.063 | 2017: +0.223 | 2018: +0.101 | 2019: +0.174 | 2020: +0.110 | 2021: +0.090 | 2022: +0.106
- IC CV=0.39, Neg years=0/8, Half ratio=0.72, Recency ratio=0.83
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0884, Sharpe=+0.4616)
- Yearly ICs: 2015: +0.267 | 2016: +0.097 | 2017: +0.226 | 2018: +0.192 | 2019: +0.098 | 2020: +0.118 | 2021: +0.120 | 2022: +0.103
- IC CV=0.41, Neg years=0/8, Half ratio=0.54, Recency ratio=0.61
- Weak component: `smooth_momentum_structure` (CV=0.60)

**`combo_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0787, Sharpe=+0.4560)
- Yearly ICs: 2015: +0.220 | 2016: +0.127 | 2017: +0.141 | 2018: +0.227 | 2019: +0.145 | 2020: +0.087 | 2021: +0.098 | 2022: +0.065
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.47
- Weak component: `first_bar_sentiment` (CV=0.45)

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0936, Sharpe=+0.4546)
- Yearly ICs: 2015: +0.233 | 2016: +0.107 | 2017: +0.189 | 2018: +0.200 | 2019: +0.082 | 2020: +0.161 | 2021: +0.075 | 2022: +0.117
- IC CV=0.38, Neg years=0/8, Half ratio=0.53, Recency ratio=0.56
- Weak component: `trend_bar_close_consistency` (CV=0.66)

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0765, Sharpe=+0.4322)
- Yearly ICs: 2015: +0.244 | 2016: +0.117 | 2017: +0.094 | 2018: +0.268 | 2019: +0.109 | 2020: +0.108 | 2021: +0.178 | 2022: +0.102
- IC CV=0.42, Neg years=0/8, Half ratio=0.60, Recency ratio=0.78
- Weak component: `first_bar_sentiment` (CV=0.45)

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0868, Sharpe=+0.4062)
- Yearly ICs: 2015: +0.296 | 2016: +0.106 | 2017: +0.192 | 2018: +0.211 | 2019: +0.154 | 2020: +0.164 | 2021: +0.138 | 2022: +0.066
- IC CV=0.39, Neg years=0/8, Half ratio=0.61, Recency ratio=0.51
- Weak component: `body_size_progression` (CV=0.64)

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0792, Sharpe=+0.3953)
- Yearly ICs: 2015: +0.206 | 2016: +0.115 | 2017: +0.109 | 2018: +0.281 | 2019: +0.096 | 2020: +0.130 | 2021: +0.101 | 2022: +0.112
- IC CV=0.43, Neg years=0/8, Half ratio=0.52, Recency ratio=0.66
- Weak component: `bar_ret_0` (CV=0.41)

**`combo_ratio__bar_ret_0__opening_auction_imbalance`** (Lock IC=+0.0500, Sharpe=+0.3938)
- Yearly ICs: 2015: +0.180 | 2016: +0.055 | 2017: +0.106 | 2018: +0.193 | 2019: +0.120 | 2020: +0.060 | 2021: +0.138 | 2022: +0.020
- IC CV=0.52, Neg years=0/8, Half ratio=0.53, Recency ratio=0.67
- Weak component: `bar_ret_0` (CV=0.41)

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0789, Sharpe=+0.3856)
- Yearly ICs: 2015: +0.226 | 2016: +0.097 | 2017: +0.261 | 2018: +0.230 | 2019: +0.144 | 2020: +0.130 | 2021: +0.079 | 2022: +0.088
- IC CV=0.43, Neg years=0/8, Half ratio=0.55, Recency ratio=0.52
- Weak component: `max_down_ret` (CV=0.60)

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0654, Sharpe=+0.3641)
- Yearly ICs: 2015: +0.226 | 2016: +0.134 | 2017: +0.077 | 2018: +0.166 | 2019: +0.094 | 2020: +0.138 | 2021: +0.078 | 2022: +0.097
- IC CV=0.38, Neg years=0/8, Half ratio=0.68, Recency ratio=0.49
- Weak component: `first_bar_sentiment` (CV=0.45)

**`combo_max__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0768, Sharpe=+0.3491)
- Yearly ICs: 2015: +0.264 | 2016: +0.110 | 2017: +0.138 | 2018: +0.165 | 2019: +0.100 | 2020: +0.096 | 2021: +0.130 | 2022: +0.125
- IC CV=0.36, Neg years=0/8, Half ratio=0.69, Recency ratio=0.68
- Weak component: `close_vs_open_range` (CV=0.47)

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0836, Sharpe=+0.2749)
- Yearly ICs: 2015: +0.201 | 2016: +0.073 | 2017: +0.215 | 2018: +0.170 | 2019: +0.102 | 2020: +0.175 | 2021: +0.060 | 2022: +0.117
- IC CV=0.40, Neg years=0/8, Half ratio=0.73, Recency ratio=0.65
- Weak component: `close_vs_open_range` (CV=0.47)

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0958, Sharpe=+0.2125)
- Yearly ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.233 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.071 | 2022: +0.082
- IC CV=0.61, Neg years=0/8, Half ratio=0.58, Recency ratio=0.47
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0823, Sharpe=+0.1403)
- Yearly ICs: 2015: +0.269 | 2016: +0.085 | 2017: +0.205 | 2018: +0.250 | 2019: +0.156 | 2020: +0.122 | 2021: +0.088 | 2022: +0.055
- IC CV=0.49, Neg years=0/8, Half ratio=0.51, Recency ratio=0.40
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0893, Sharpe=+0.1304)
- Yearly ICs: 2015: +0.312 | 2016: +0.110 | 2017: +0.179 | 2018: +0.189 | 2019: +0.124 | 2020: +0.146 | 2021: +0.118 | 2022: +0.065
- IC CV=0.45, Neg years=0/8, Half ratio=0.51, Recency ratio=0.43
- Weak component: `first_bar_sentiment` (CV=0.45)

**`combo_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0936, Sharpe=+0.0056)
- Yearly ICs: 2015: +0.284 | 2016: +0.072 | 2017: +0.252 | 2018: +0.190 | 2019: +0.132 | 2020: +0.163 | 2021: +0.095 | 2022: +0.082
- IC CV=0.47, Neg years=0/8, Half ratio=0.61, Recency ratio=0.50
- Weak component: `max_down_ret` (CV=0.60)

### 159915ETF — `single` True Positives

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1158, Sharpe=+1.5577)
- Yearly ICs: 2015: +0.210 | 2016: +0.098 | 2017: -0.023 | 2018: +0.176 | 2019: +0.217 | 2020: +0.178 | 2021: +0.135 | 2022: +0.080
- IC CV=0.56, Neg years=1/8, Half ratio=1.09, Recency ratio=0.70
- Weak component: `first_bar_sentiment` (CV=0.75)

**`combo_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1375, Sharpe=+1.5481)
- Yearly ICs: 2015: +0.179 | 2016: +0.080 | 2017: -0.009 | 2018: +0.102 | 2019: +0.226 | 2020: +0.038 | 2021: +0.159 | 2022: +0.027
- IC CV=0.76, Neg years=1/8, Half ratio=1.04, Recency ratio=0.72
- Weak component: `volume_weighted_price_position` (CV=0.83)

**`combo_clamp_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.1176, Sharpe=+1.3628)
- Yearly ICs: 2015: +0.231 | 2016: +0.041 | 2017: +0.017 | 2018: +0.122 | 2019: +0.183 | 2020: +0.107 | 2021: +0.158 | 2022: +0.128
- IC CV=0.53, Neg years=0/8, Half ratio=1.12, Recency ratio=1.05
- Weak component: `demark_setup_reversal_early` (CV=0.76)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1260, Sharpe=+1.3254)
- Yearly ICs: 2015: +0.252 | 2016: +0.132 | 2017: +0.036 | 2018: +0.078 | 2019: +0.206 | 2020: +0.150 | 2021: +0.154 | 2022: +0.131
- IC CV=0.45, Neg years=0/8, Half ratio=1.04, Recency ratio=0.74
- Weak component: `first_bar_sentiment` (CV=0.75)

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1220, Sharpe=+1.3232)
- Yearly ICs: 2015: +0.236 | 2016: +0.159 | 2017: -0.017 | 2018: +0.158 | 2019: +0.231 | 2020: +0.183 | 2021: +0.135 | 2022: +0.109
- IC CV=0.50, Neg years=1/8, Half ratio=1.04, Recency ratio=0.62
- Weak component: `first_bar_sentiment` (CV=0.75)

**`combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1316, Sharpe=+1.2548)
- Yearly ICs: 2015: +0.168 | 2016: +0.057 | 2017: +0.036 | 2018: +0.105 | 2019: +0.108 | 2020: +0.062 | 2021: +0.170 | 2022: +0.136
- IC CV=0.45, Neg years=0/8, Half ratio=1.09, Recency ratio=1.36
- Weak component: `impulse_bar_dominance` (CV=1.03)

**`combo_rank_min__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1345, Sharpe=+1.2143)
- Yearly ICs: 2015: +0.225 | 2016: +0.067 | 2017: +0.003 | 2018: +0.069 | 2019: +0.211 | 2020: +0.149 | 2021: +0.126 | 2022: +0.112
- IC CV=0.58, Neg years=0/8, Half ratio=1.23, Recency ratio=0.81
- Weak component: `star50_limit_proximity_early` (CV=0.69)

**`combo_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.1104, Sharpe=+1.1839)
- Yearly ICs: 2015: +0.219 | 2016: +0.133 | 2017: +0.003 | 2018: +0.112 | 2019: +0.210 | 2020: +0.114 | 2021: +0.146 | 2022: +0.057
- IC CV=0.54, Neg years=0/8, Half ratio=0.99, Recency ratio=0.58
- Weak component: `bar_body_rng_0` (CV=0.54)

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1268, Sharpe=+1.0353)
- Yearly ICs: 2015: +0.238 | 2016: +0.072 | 2017: -0.022 | 2018: +0.101 | 2019: +0.255 | 2020: +0.121 | 2021: +0.110 | 2022: +0.080
- IC CV=0.70, Neg years=1/8, Half ratio=1.05, Recency ratio=0.61
- Weak component: `star50_limit_proximity_early` (CV=0.69)

**`combo_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1261, Sharpe=+0.9894)
- Yearly ICs: 2015: +0.240 | 2016: +0.079 | 2017: -0.023 | 2018: +0.105 | 2019: +0.258 | 2020: +0.131 | 2021: +0.109 | 2022: +0.075
- IC CV=0.70, Neg years=1/8, Half ratio=1.06, Recency ratio=0.58
- Weak component: `star50_limit_proximity_early` (CV=0.69)

**`combo_clamp_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.1069, Sharpe=+0.9698)
- Yearly ICs: 2015: +0.187 | 2016: +0.087 | 2017: +0.016 | 2018: +0.080 | 2019: +0.201 | 2020: +0.112 | 2021: +0.086 | 2022: +0.090
- IC CV=0.52, Neg years=0/8, Half ratio=1.08, Recency ratio=0.64
- Weak component: `late_bar_momentum` (CV=0.82)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1309, Sharpe=+0.9097)
- Yearly ICs: 2015: +0.179 | 2016: +0.104 | 2017: -0.004 | 2018: +0.114 | 2019: +0.160 | 2020: +0.124 | 2021: +0.142 | 2022: +0.160
- IC CV=0.44, Neg years=1/8, Half ratio=1.18, Recency ratio=1.07

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1116, Sharpe=+0.7844)
- Yearly ICs: 2015: +0.236 | 2016: +0.098 | 2017: +0.030 | 2018: +0.125 | 2019: +0.197 | 2020: +0.111 | 2021: +0.134 | 2022: +0.075
- IC CV=0.49, Neg years=0/8, Half ratio=0.86, Recency ratio=0.63
- Weak component: `bar_body_rng_0` (CV=0.54)

**`combo_z_sum__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1126, Sharpe=+0.7612)
- Yearly ICs: 2015: +0.174 | 2016: +0.067 | 2017: +0.044 | 2018: +0.086 | 2019: +0.175 | 2020: +0.094 | 2021: +0.152 | 2022: +0.103
- IC CV=0.41, Neg years=0/8, Half ratio=1.07, Recency ratio=1.06
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1302, Sharpe=+0.6763)
- Yearly ICs: 2015: +0.184 | 2016: +0.102 | 2017: -0.035 | 2018: +0.096 | 2019: +0.089 | 2020: +0.078 | 2021: +0.064 | 2022: +0.131
- IC CV=0.66, Neg years=1/8, Half ratio=0.77, Recency ratio=0.68
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1043, Sharpe=+0.6683)
- Yearly ICs: 2015: +0.171 | 2016: -0.030 | 2017: +0.006 | 2018: +0.070 | 2019: +0.112 | 2020: +0.071 | 2021: +0.133 | 2022: +0.149
- IC CV=0.77, Neg years=1/8, Half ratio=1.42, Recency ratio=2.01
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.06)

**`combo_min__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0985, Sharpe=+0.5273)
- Yearly ICs: 2015: +0.141 | 2016: +0.022 | 2017: +0.036 | 2018: +0.041 | 2019: +0.091 | 2020: +0.014 | 2021: +0.142 | 2022: +0.161
- IC CV=0.69, Neg years=0/8, Half ratio=1.31, Recency ratio=1.86
- Weak component: `impulse_bar_dominance` (CV=1.03)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0763, Sharpe=+0.4953)
- Yearly ICs: 2015: +0.225 | 2016: +0.116 | 2017: -0.030 | 2018: +0.100 | 2019: +0.153 | 2020: +0.167 | 2021: +0.117 | 2022: +0.078
- IC CV=0.60, Neg years=1/8, Half ratio=1.25, Recency ratio=0.57
- Weak component: `first_bar_sentiment` (CV=0.75)

**`combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return`** (Lock IC=+0.1048, Sharpe=+0.4833)
- Yearly ICs: 2015: +0.166 | 2016: +0.125 | 2017: -0.068 | 2018: +0.142 | 2019: +0.097 | 2020: +0.126 | 2021: +0.041 | 2022: +0.150
- IC CV=0.74, Neg years=1/8, Half ratio=0.85, Recency ratio=0.65
- Weak component: `yesterday_early_momentum` (CV=1.03)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1075, Sharpe=+0.3554)
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.080 | 2019: +0.132 | 2020: +0.100 | 2021: +0.035 | 2022: +0.178
- IC CV=0.82, Neg years=1/8, Half ratio=1.22, Recency ratio=0.96
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0641, Sharpe=+0.3448)
- Yearly ICs: 2015: +0.251 | 2016: +0.100 | 2017: -0.024 | 2018: +0.098 | 2019: +0.174 | 2020: +0.131 | 2021: +0.090 | 2022: +0.078
- IC CV=0.66, Neg years=1/8, Half ratio=0.99, Recency ratio=0.48
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.06)

**`combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1077, Sharpe=+0.3400)
- Yearly ICs: 2015: +0.167 | 2016: +0.043 | 2017: -0.050 | 2018: +0.073 | 2019: +0.133 | 2020: +0.101 | 2021: +0.042 | 2022: +0.183
- IC CV=0.82, Neg years=1/8, Half ratio=1.31, Recency ratio=1.07
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0928, Sharpe=+0.3022)
- Yearly ICs: 2015: +0.179 | 2016: +0.073 | 2017: +0.042 | 2018: +0.065 | 2019: +0.114 | 2020: +0.116 | 2021: +0.149 | 2022: +0.125
- IC CV=0.40, Neg years=0/8, Half ratio=1.17, Recency ratio=1.09
- Weak component: `volume_weighted_price_position` (CV=0.83)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1111, Sharpe=+0.1333)
- Yearly ICs: 2015: +0.185 | 2016: +0.060 | 2017: +0.041 | 2018: +0.082 | 2019: +0.117 | 2020: +0.111 | 2021: +0.159 | 2022: +0.166
- IC CV=0.42, Neg years=0/8, Half ratio=1.29, Recency ratio=1.33
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_mean__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.1914 | +0.0249 | -0.1806 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1716 | +0.0478 | +0.0010 | 1y |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Median | gradual | +0.1565 | +0.0329 | -0.1845 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | TP | gradual | +0.1383 | +0.0659 | -0.0752 | 1y |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.1374 | +0.0386 | -0.0976 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.1339 | +0.0438 | -0.0316 | 1y |
| `combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.1277 | +0.0500 | -0.0119 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0912 | +0.0267 | +0.0014 | 1y |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Median | fast | +0.0578 | -0.0512 | -0.0352 | 1y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0576 | +0.0214 | +0.1515 | 1y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | TP | fast | +0.0550 | -0.0050 | +0.1389 | 1y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Median | fast | +0.0234 | -0.0520 | +0.1970 | 1y |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Median | immediate | -0.0818 | +0.0549 | +0.1410 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=3, gradual=6, persistent=3

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1597 | +0.0992 | -0.0470 | 2y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1561 | +0.1336 | +0.0302 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | TP | persistent | +0.1086 | +0.1478 | +0.0020 | 3y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1063 | +0.1535 | +0.0927 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1059 | +0.1666 | +0.0842 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0972 | +0.1786 | +0.1005 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0962 | +0.1455 | +0.0788 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0938 | +0.1539 | +0.0091 | 3y |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0935 | +0.1003 | +0.1060 | 2y |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0921 | +0.1142 | +0.1008 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0910 | +0.0861 | +0.0192 | 3y |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | TP | persistent | +0.0897 | +0.1283 | +0.0019 | 3y |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | TP | persistent | +0.0842 | +0.1372 | +0.0680 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0801 | +0.0915 | +0.0804 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0781 | +0.1444 | +0.1943 | ∞ |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0778 | +0.1367 | +0.0043 | 3y |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0766 | +0.0799 | +0.0886 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | TP | gradual | +0.0727 | +0.1296 | -0.0089 | 3y |
| `combo_min__max_up_ret__first_bar_sentiment` | Median | gradual | +0.0724 | +0.0838 | -0.0110 | 3y |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | TP | gradual | +0.0721 | +0.0899 | -0.0195 | 3y |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0711 | +0.0950 | +0.1054 | ∞ |
| `combo_min__first_bar_sentiment__bar_ret_0` | TP | gradual | +0.0698 | +0.1230 | -0.0173 | 3y |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0653 | +0.1132 | +0.0871 | ∞ |
| `combo_sig_product__max_up_ret__body_size_progression` | TP | persistent | +0.0645 | +0.1370 | +0.0791 | ∞ |
| `combo_max__close_vs_open_range__first_bar_sentiment` | TP | gradual | +0.0619 | +0.1368 | -0.0554 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.0615 | +0.1143 | +0.0045 | 3y |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0607 | +0.1146 | +0.1007 | ∞ |
| `combo_max__max_up_ret__first_bar_sentiment` | TP | gradual | +0.0551 | +0.1458 | -0.0397 | 3y |
| `combo_sig_product__max_up_ret__bar_ret_0` | TP | persistent | +0.0501 | +0.0982 | +0.0041 | 3y |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0496 | +0.0710 | +0.1123 | ∞ |
| `combo_max__bar_ret_0__max_down_ret` | TP | gradual | +0.0438 | +0.1284 | -0.0001 | 3y |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | TP | gradual | +0.0078 | +0.0609 | -0.0032 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=9, persistent=23

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1960 | +0.0897 | -0.0668 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1940 | +0.0552 | +0.0285 | 1y |
| `combo_min__max_up_ret__impulse_bar_dominance` | TP | gradual | +0.1888 | +0.0771 | -0.1009 | 1y |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | TP | gradual | +0.1763 | +0.0780 | -0.0237 | 1y |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.1720 | +0.0682 | -0.0681 | 1y |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.1673 | +0.0789 | +0.0656 | 1y |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | TP | persistent | +0.1585 | +0.0569 | +0.0294 | 1y |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1574 | +0.1340 | +0.1203 | ∞ |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1568 | +0.1111 | +0.0834 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1537 | +0.1217 | +0.1543 | ∞ |
| `combo_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1524 | +0.0907 | +0.1049 | ∞ |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | Median | gradual | +0.1522 | +0.0615 | -0.0388 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1492 | +0.1055 | +0.0526 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1490 | +0.1076 | +0.0711 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1469 | +0.0883 | +0.0544 | 3y |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1468 | +0.0898 | +0.1017 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1399 | +0.0945 | +0.0571 | 3y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1256 | +0.0913 | +0.1102 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | TP | persistent | +0.1194 | +0.0864 | +0.1110 | ∞ |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1181 | +0.0985 | +0.1637 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1157 | +0.0779 | +0.1278 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1117 | +0.0834 | +0.1233 | ∞ |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0931 | +0.0930 | +0.0831 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0734 | +0.0692 | +0.0816 | ∞ |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0598 | +0.0615 | +0.0735 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=5, persistent=20

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 15/20 top rejects are profitable (75%)

- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.1991, Lock IC=+0.0524, Sharpe=+0.7239
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard**: 13/20 top rejects are profitable (65%)

- `combo_rel_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1331, Lock IC=+0.0625, Sharpe=+0.5170
- `combo_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1322, Lock IC=+0.0684, Sharpe=+0.5170
- `combo_z_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1322, Lock IC=+0.0684, Sharpe=+0.5170

**BH-FDR Gate**: 2/12 top rejects are profitable (17%)

- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.0951, Lock IC=+0.0600, Sharpe=+0.6245
- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.0951, Lock IC=+0.0600, Sharpe=+0.6245

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2370, Lock IC=+0.0693, Sharpe=+0.5695
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2370, Lock IC=+0.0693, Sharpe=+0.5695
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2366, Lock IC=+0.0693, Sharpe=+0.5695

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0937, Sharpe=+1.0629
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2691, Lock IC=+0.0706, Sharpe=+0.8555
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1929, Lock IC=+0.0529, Sharpe=+0.5709

### 500ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2312, Lock IC=+0.1016, Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464

**B2 Rolling Guard**: 9/20 top rejects are profitable (45%)

- `combo_tri_min__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.1705, Lock IC=+0.0264, Sharpe=+0.3458
- `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.1508, Lock IC=+0.0731, Sharpe=+0.2561
- `combo_tri_z_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.1508, Lock IC=+0.0731, Sharpe=+0.2561

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2996, Lock IC=+0.1132, Sharpe=+0.9985
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Sharpe=+0.9985

**Adaptive Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2233, Lock IC=+0.1058, Sharpe=+1.1405
- `combo_mean__max_up_ret__close_vs_open_range`: Train IC=+0.2364, Lock IC=+0.0939, Sharpe=+0.7756
- `combo_min__opening_auction_imbalance__first_bar_return`: Train IC=+0.2396, Lock IC=+0.0962, Sharpe=+0.7432

### 159915ETF — `single`

**7-Year Jackknife**: 16/20 top rejects are profitable (80%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Sharpe=+1.3789
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Sharpe=+1.3789
- `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.2197, Lock IC=+0.0920, Sharpe=+1.0913

**B2 Rolling Guard**: 14/20 top rejects are profitable (70%)

- `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.2001, Lock IC=+0.1023, Sharpe=+1.2236
- `combo_tri_mean__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.1824, Lock IC=+0.1067, Sharpe=+0.8067
- `combo_tri_z_mean__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.1824, Lock IC=+0.1067, Sharpe=+0.8067

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2646, Lock IC=+0.1269, Sharpe=+1.6324
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2777, Lock IC=+0.1338, Sharpe=+1.4166
- `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2517, Lock IC=+0.1333, Sharpe=+1.3096

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Sharpe=+1.6742
- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Sharpe=+1.6287

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1042 | 78 | 19 | 34 | 25 | 24% | 32% |
| B2 Rolling Guard | 78 | 78 | 24 | 32 | 22 | 31% | 28% |
| BH-FDR Gate | 12 | 12 | 3 | 7 | 2 | 25% | 17% |
| B3 Composite Floor | 196 | 78 | 1 | 18 | 59 | 1% | 76% |
| B4 Correlation Gate | 27 | 27 | 0 | 1 | 26 | 0% | 96% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.1991, Lock IC=+0.0524, Sharpe=+0.7239
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard** — top TP casualties:
- `combo_diff__volume_weighted_momentum_acceleration__bar_body_rng_0`: Train IC=+0.1135, Lock IC=+0.0679, Sharpe=+0.5884
- `combo_z_diff__volume_weighted_momentum_acceleration__bar_body_rng_0`: Train IC=+0.1135, Lock IC=+0.0679, Sharpe=+0.5884
- `combo_rel_diff__volume_weighted_momentum_acceleration__bar_body_rng_0`: Train IC=+0.1130, Lock IC=+0.0644, Sharpe=+0.5884

**B3 Composite Floor** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1832, Lock IC=+0.0875, Sharpe=+1.1020
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1832, Lock IC=+0.0875, Sharpe=+1.1020
- `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`: Train IC=+0.1938, Lock IC=+0.0590, Sharpe=+0.7052

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0937, Sharpe=+1.0629
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2691, Lock IC=+0.0706, Sharpe=+0.8555
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1929, Lock IC=+0.0529, Sharpe=+0.5709

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1680 | 78 | 25 | 26 | 27 | 32% | 35% |
| B2 Rolling Guard | 104 | 78 | 29 | 21 | 28 | 37% | 36% |
| BH-FDR Gate | 9 | 9 | 1 | 8 | 0 | 11% | 0% |
| B3 Composite Floor | 434 | 78 | 1 | 10 | 67 | 1% | 86% |
| B4 Correlation Gate | 432 | 78 | 0 | 9 | 69 | 0% | 88% |
| Adaptive Correlation Gate | 29 | 29 | 0 | 3 | 26 | 0% | 90% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2312, Lock IC=+0.1016, Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0388, Lock IC=+0.0707, Sharpe=+0.8914
- `combo_ratio__close_vs_open_range__volatility_expansion_trend_vector`: Train IC=+0.0925, Lock IC=+0.0735, Sharpe=+0.5811
- `combo_ratio__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`: Train IC=+0.1036, Lock IC=+0.0785, Sharpe=+0.5304

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__body_size_progression`: Train IC=+0.1094, Lock IC=+0.0362, Sharpe=+1.0604
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression`: Train IC=+0.1094, Lock IC=+0.0362, Sharpe=+1.0604
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1195, Lock IC=+0.0398, Sharpe=+0.9095

**B4 Correlation Gate** — top TP casualties:
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_diff__opening_drive_thrust_ratio__early_late_momentum_divergence`: Train IC=+0.1842, Lock IC=+0.0899, Sharpe=+0.9996
- `combo_z_diff__opening_drive_thrust_ratio__early_late_momentum_divergence`: Train IC=+0.1842, Lock IC=+0.0899, Sharpe=+0.9996

**Adaptive Correlation Gate** — top TP casualties:
- `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2233, Lock IC=+0.1058, Sharpe=+1.1405
- `combo_mean__max_up_ret__close_vs_open_range`: Train IC=+0.2364, Lock IC=+0.0939, Sharpe=+0.7756
- `combo_min__opening_auction_imbalance__first_bar_return`: Train IC=+0.2396, Lock IC=+0.0962, Sharpe=+0.7432

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1119 | 78 | 27 | 16 | 35 | 35% | 45% |
| B2 Rolling Guard | 174 | 78 | 22 | 9 | 47 | 28% | 60% |
| BH-FDR Gate | 4 | 4 | 4 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 279 | 78 | 5 | 5 | 68 | 6% | 87% |
| B4 Correlation Gate | 141 | 78 | 0 | 0 | 78 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Sharpe=+1.3789
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Sharpe=+1.3789
- `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.2197, Lock IC=+0.0920, Sharpe=+1.0913

**B2 Rolling Guard** — top TP casualties:
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.1303, Lock IC=+0.1315, Sharpe=+1.2721
- `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.1302, Lock IC=+0.1313, Sharpe=+1.2721
- `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.2001, Lock IC=+0.1023, Sharpe=+1.2236

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2646, Lock IC=+0.1269, Sharpe=+1.6324
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2777, Lock IC=+0.1338, Sharpe=+1.4166
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Sharpe=+1.4133

**B4 Correlation Gate** — top TP casualties:
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835
- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2469, Lock IC=+0.1161, Sharpe=+1.6835

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `opening_auction_imbalance` | 0 | 4 | 4 | 0% |  |
| `bar_ret_0` | 0 | 9 | 9 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 12 | 12 | 0% |  |
| `first_bar_sentiment` | 0 | 10 | 10 | 0% |  |
| `max_up_ret` | 0 | 23 | 23 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 17 | 17 | 0% |  |
| `max_down_ret` | 0 | 3 | 3 | 0% |  |
| `bar_body_rng_0` | 0 | 5 | 5 | 0% |  |
| `star50_limit_proximity_early` | 0 | 17 | 17 | 0% |  |
| `volume_weighted_price_position` | 0 | 4 | 4 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 2 | 2 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 2 | 2 | 0% |  |
| `impulse_bar_dominance` | 0 | 3 | 3 | 0% |  |
| `body_size_progression` | 0 | 2 | 2 | 0% |  |
| `close_vs_open_range` | 0 | 5 | 5 | 0% |  |
| `yesterday_first_30min_return` | 0 | 4 | 4 | 0% |  |
| `first_bar_return` | 0 | 3 | 3 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=35, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=0, TP=7, FP rate=0%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=9, FP rate=0%

