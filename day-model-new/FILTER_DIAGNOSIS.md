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
| 500ETF | single | 20 | 0 | 3 | 17 | 0% | 0.74 |
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
- Yearly ICs: 2015: +0.083 | 2016: +0.112 | 2017: +0.044 | 2018: +0.089 | 2019: +0.064 | 2020: -0.038 | 2021: +0.135
- IC CV=0.75, Neg years=1/7, Half ratio=0.87, Recency ratio=0.50
- Weak component: `volume_surge_direction` (CV=1.02, neg years=1)
- Regime ICs: Q1_low_vol=+0.088, Q2=-0.007, Q3_mid=+0.119, Q4=+0.059, Q5_high_vol=+0.111

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0337, Sharpe=-1.1178)
- Yearly ICs: 2015: +0.076 | 2016: +0.034 | 2017: -0.050 | 2018: +0.114 | 2019: +0.086 | 2020: +0.032 | 2021: +0.170
- IC CV=0.98, Neg years=1/7, Half ratio=2.19, Recency ratio=1.84
- Weak component: `volume_weighted_price_position` (CV=1.30, neg years=1)
- Regime ICs: Q1_low_vol=-0.043, Q2=+0.089, Q3_mid=+0.140, Q4=+0.030, Q5_high_vol=+0.132

**`combo_product__smooth_momentum_structure__opening_drive_thrust_ratio`** (Lock IC=-0.0238, Sharpe=-0.5100)
- Yearly ICs: 2015: +0.076 | 2016: -0.018 | 2017: +0.100 | 2018: -0.017 | 2019: +0.089 | 2020: +0.024 | 2021: +0.072
- IC CV=0.99, Neg years=2/7, Half ratio=1.47, Recency ratio=1.66
- Weak component: `opening_drive_thrust_ratio` (CV=0.81, neg years=1)
- Regime ICs: Q1_low_vol=+0.122, Q2=-0.051, Q3_mid=+0.108, Q4=-0.033, Q5_high_vol=+0.037

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0103, Sharpe=-0.3294)
- Yearly ICs: 2015: +0.093 | 2016: +0.030 | 2017: +0.039 | 2018: +0.150 | 2019: +0.044 | 2020: +0.011 | 2021: +0.194
- IC CV=0.79, Neg years=0/7, Half ratio=1.62, Recency ratio=1.67
- Weak component: `volume_weighted_price_position` (CV=1.30, neg years=1)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.047, Q3_mid=+0.077, Q4=+0.098, Q5_high_vol=+0.153

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0334, Sharpe=-0.0663)
- Yearly ICs: 2015: +0.233 | 2016: +0.062 | 2017: -0.069 | 2018: +0.203 | 2019: +0.122 | 2020: +0.058 | 2021: +0.173
- IC CV=0.86, Neg years=1/7, Half ratio=1.11, Recency ratio=0.79
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.049, Q2=+0.010, Q3_mid=+0.110, Q4=+0.248, Q5_high_vol=+0.207

**`combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0225, Sharpe=-0.2962)
- Yearly ICs: 2015: +0.095 | 2016: +0.111 | 2017: +0.068 | 2018: +0.201 | 2019: +0.089 | 2020: +0.013 | 2021: +0.146
- IC CV=0.53, Neg years=0/7, Half ratio=1.13, Recency ratio=0.77
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.058, Q3_mid=+0.120, Q4=+0.128, Q5_high_vol=+0.162

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.0094, Sharpe=-1.2715)
- Yearly ICs: 2015: +0.180 | 2016: +0.069 | 2017: -0.078 | 2018: +0.184 | 2019: +0.072 | 2020: +0.017 | 2021: +0.151
- IC CV=1.04, Neg years=1/7, Half ratio=1.32, Recency ratio=0.68
- Weak component: `demark_setup_reversal_early` (CV=1.42)
- Regime ICs: Q1_low_vol=-0.061, Q2=-0.010, Q3_mid=+0.102, Q4=+0.188, Q5_high_vol=+0.192

### 500ETF — `single` Median Features

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0913, Sharpe=-0.2578)
- Yearly ICs: 2015: +0.146 | 2016: -0.049 | 2017: +0.116 | 2018: +0.052 | 2019: +0.111 | 2020: +0.099 | 2021: +0.059
- IC CV=0.78, Neg years=1/7, Half ratio=0.96, Recency ratio=1.62
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.082, Q3_mid=+0.074, Q4=+0.067, Q5_high_vol=+0.139

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0735, Sharpe=-0.4531)
- Yearly ICs: 2015: +0.336 | 2016: +0.119 | 2017: +0.177 | 2018: +0.206 | 2019: +0.122 | 2020: +0.138 | 2021: +0.144
- IC CV=0.40, Neg years=0/7, Half ratio=0.76, Recency ratio=0.62
- Weak component: `late_bar_momentum` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.090, Q3_mid=+0.187, Q4=+0.149, Q5_high_vol=+0.317

**`vwap_trend_channel_slope`** (Lock IC=+0.0602, Sharpe=-0.5999)
- Yearly ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079
- IC CV=0.52, Neg years=0/7, Half ratio=0.87, Recency ratio=0.99
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.063, Q3_mid=+0.120, Q4=+0.066, Q5_high_vol=+0.119

### 159915ETF — `single` Median Features

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0874, Sharpe=-0.0146)
- Yearly ICs: 2015: +0.181 | 2016: +0.143 | 2017: +0.037 | 2018: +0.088 | 2019: +0.170 | 2020: +0.122 | 2021: +0.183
- IC CV=0.38, Neg years=0/7, Half ratio=1.37, Recency ratio=0.94
- Weak component: `max_up_ret` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.082, Q3_mid=+0.198, Q4=+0.118, Q5_high_vol=+0.197

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0706, Sharpe=+0.4878)
- Yearly ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130
- IC CV=0.88, Neg years=1/7, Half ratio=1.82, Recency ratio=1.12
- Weak component: `limit_down_proximity_early` (CV=1.62)

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0189, Sharpe=+0.4526)
- Yearly ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.075 | 2018: +0.166 | 2019: +0.085 | 2020: +0.075 | 2021: +0.151
- IC CV=0.82, Neg years=1/7, Half ratio=1.02, Recency ratio=0.74
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0184, Sharpe=+0.3625)
- Yearly ICs: 2015: +0.098 | 2016: +0.068 | 2017: +0.034 | 2018: +0.193 | 2019: +0.044 | 2020: +0.042 | 2021: +0.166
- IC CV=0.64, Neg years=0/7, Half ratio=1.30, Recency ratio=1.25
- Weak component: `early_vwap_acceleration` (CV=0.99)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0616, Sharpe=+0.2757)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095
- IC CV=1.14, Neg years=1/7, Half ratio=0.62, Recency ratio=0.50

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0280, Sharpe=+0.0482)
- Yearly ICs: 2015: +0.254 | 2016: +0.095 | 2017: +0.008 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132
- IC CV=0.65, Neg years=0/7, Half ratio=0.81, Recency ratio=0.50
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1183, Sharpe=+1.6160)
- Yearly ICs: 2015: +0.294 | 2016: +0.022 | 2017: +0.204 | 2018: +0.144 | 2019: +0.184 | 2020: +0.146 | 2021: +0.091
- IC CV=0.51, Neg years=0/7, Half ratio=0.88, Recency ratio=0.75
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1139, Sharpe=+1.4937)
- Yearly ICs: 2015: +0.268 | 2016: +0.119 | 2017: +0.110 | 2018: +0.189 | 2019: +0.088 | 2020: +0.115 | 2021: +0.140
- IC CV=0.39, Neg years=0/7, Half ratio=0.73, Recency ratio=0.66
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)

**`combo_rank_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1326, Sharpe=+1.4616)
- Yearly ICs: 2015: +0.222 | 2016: +0.074 | 2017: +0.224 | 2018: +0.080 | 2019: +0.081 | 2020: +0.121 | 2021: +0.089
- IC CV=0.49, Neg years=0/7, Half ratio=0.57, Recency ratio=0.71
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1256, Sharpe=+1.1032)
- Yearly ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.194 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148
- IC CV=0.42, Neg years=0/7, Half ratio=1.09, Recency ratio=1.10
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1703, Sharpe=+1.0880)
- Yearly ICs: 2015: +0.187 | 2016: +0.049 | 2017: +0.197 | 2018: +0.137 | 2019: +0.171 | 2020: +0.117 | 2021: +0.085
- IC CV=0.38, Neg years=0/7, Half ratio=0.85, Recency ratio=0.85
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1100, Sharpe=+1.0387)
- Yearly ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052
- IC CV=0.52, Neg years=0/7, Half ratio=0.67, Recency ratio=0.56
- Weak component: `max_down_ret` (CV=0.55)

**`combo_rel_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0020, Sharpe=+0.7804)
- Yearly ICs: 2015: +0.149 | 2016: +0.138 | 2017: -0.011 | 2018: +0.082 | 2019: +0.070 | 2020: +0.030 | 2021: +0.081
- IC CV=0.68, Neg years=1/7, Half ratio=0.62, Recency ratio=0.39
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1504, Sharpe=+0.5807)
- Yearly ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089
- IC CV=0.38, Neg years=0/7, Half ratio=0.79, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0995, Sharpe=+0.5803)
- Yearly ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022
- IC CV=0.53, Neg years=0/7, Half ratio=0.63, Recency ratio=0.44
- Weak component: `max_down_ret` (CV=0.55)

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0810, Sharpe=+0.5100)
- Yearly ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172
- IC CV=0.33, Neg years=0/7, Half ratio=0.99, Recency ratio=0.89
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0948, Sharpe=+0.4283)
- Yearly ICs: 2015: +0.297 | 2016: +0.084 | 2017: +0.247 | 2018: +0.154 | 2019: +0.106 | 2020: +0.168 | 2021: +0.113
- IC CV=0.43, Neg years=0/7, Half ratio=0.73, Recency ratio=0.74
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0842, Sharpe=+0.3567)
- Yearly ICs: 2015: +0.303 | 2016: +0.124 | 2017: +0.192 | 2018: +0.197 | 2019: +0.140 | 2020: +0.173 | 2021: +0.106
- IC CV=0.34, Neg years=0/7, Half ratio=0.68, Recency ratio=0.65
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_rank_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0890, Sharpe=+0.2416)
- Yearly ICs: 2015: +0.285 | 2016: +0.120 | 2017: +0.197 | 2018: +0.186 | 2019: +0.120 | 2020: +0.115 | 2021: +0.090
- IC CV=0.40, Neg years=0/7, Half ratio=0.72, Recency ratio=0.51
- Weak component: `max_down_ret` (CV=0.55)

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0856, Sharpe=+0.2376)
- Yearly ICs: 2015: +0.227 | 2016: +0.099 | 2017: +0.263 | 2018: +0.229 | 2019: +0.143 | 2020: +0.129 | 2021: +0.080
- IC CV=0.40, Neg years=0/7, Half ratio=0.78, Recency ratio=0.64
- Weak component: `max_down_ret` (CV=0.55)

**`combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0439, Sharpe=+0.1933)
- Yearly ICs: 2015: +0.198 | 2016: +0.031 | 2017: +0.038 | 2018: +0.083 | 2019: +0.134 | 2020: +0.109 | 2021: +0.111
- IC CV=0.53, Neg years=0/7, Half ratio=1.55, Recency ratio=0.96
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0693, Sharpe=+0.1614)
- Yearly ICs: 2015: +0.215 | 2016: +0.100 | 2017: +0.147 | 2018: +0.200 | 2019: +0.067 | 2020: +0.125 | 2021: +0.058
- IC CV=0.43, Neg years=0/7, Half ratio=0.67, Recency ratio=0.58
- Weak component: `early_body_momentum` (CV=0.39)

**`combo_ratio__max_down_ret__net_volume_flow`** (Lock IC=+0.1213, Sharpe=+0.1000)
- Yearly ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004
- IC CV=0.47, Neg years=0/7, Half ratio=0.64, Recency ratio=0.42
- Weak component: `max_down_ret` (CV=0.55)

### 159915ETF — `single` True Positives

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1318, Sharpe=+1.5570)
- Yearly ICs: 2015: +0.228 | 2016: +0.122 | 2017: +0.009 | 2018: +0.185 | 2019: +0.198 | 2020: +0.148 | 2021: +0.176
- IC CV=0.44, Neg years=0/7, Half ratio=1.16, Recency ratio=0.93
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1423, Sharpe=+1.5511)
- Yearly ICs: 2015: +0.190 | 2016: +0.046 | 2017: +0.009 | 2018: +0.127 | 2019: +0.235 | 2020: +0.125 | 2021: +0.141
- IC CV=0.58, Neg years=0/7, Half ratio=1.42, Recency ratio=1.13
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1249, Sharpe=+1.5336)
- Yearly ICs: 2015: +0.265 | 2016: +0.147 | 2017: -0.017 | 2018: +0.150 | 2019: +0.223 | 2020: +0.209 | 2021: +0.110
- IC CV=0.55, Neg years=1/7, Half ratio=1.12, Recency ratio=0.78
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1327, Sharpe=+1.3316)
- Yearly ICs: 2015: +0.239 | 2016: +0.078 | 2017: -0.023 | 2018: +0.106 | 2019: +0.259 | 2020: +0.133 | 2021: +0.110
- IC CV=0.69, Neg years=1/7, Half ratio=1.25, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1311, Sharpe=+1.1520)
- Yearly ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087
- IC CV=0.73, Neg years=0/7, Half ratio=0.82, Recency ratio=0.73
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1258, Sharpe=+1.0384)
- Yearly ICs: 2015: +0.222 | 2016: +0.155 | 2017: -0.024 | 2018: +0.139 | 2019: +0.212 | 2020: +0.130 | 2021: +0.133
- IC CV=0.54, Neg years=1/7, Half ratio=1.31, Recency ratio=0.70
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1192, Sharpe=+0.6699)
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034
- IC CV=0.90, Neg years=1/7, Half ratio=0.89, Recency ratio=0.61
- Weak component: `yesterday_first_30min_return` (CV=1.04)

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
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
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

**B4 Correlation Gate**: 16/20 top rejects are profitable (80%)

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2747, Lock IC=+0.0342, Sharpe=+1.2516
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2356, Lock IC=+0.0236, Sharpe=+0.8727
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2571, Lock IC=+0.0263, Sharpe=+0.6902

**Adaptive Correlation Gate**: 3/8 top rejects are profitable (38%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1836, Lock IC=+0.0737, Sharpe=+1.3074
- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.2141, Lock IC=+0.0747, Sharpe=+0.3762
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Train IC=+0.1600, Lock IC=+0.0283, Sharpe=+0.0760

### 500ETF — `single`

**7-Year Jackknife**: 17/20 top rejects are profitable (85%)

- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2429, Lock IC=+0.0860, Sharpe=+0.7897
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897

**B2 Rolling Guard**: 16/20 top rejects are profitable (80%)

- `combo_mean__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Sharpe=+0.7111
- `combo_z_sum__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Sharpe=+0.7111
- `combo_mean__first_bar_return__max_down_ret`: Train IC=+0.2253, Lock IC=+0.1025, Sharpe=+0.7111

**Temporal Validation Gate**: 16/20 top rejects are profitable (80%)

- `combo_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293
- `combo_z_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293
- `combo_diff__smooth_momentum_structure__rsi_opening`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293

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

**B4 Correlation Gate**: 17/20 top rejects are profitable (85%)

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
- `combo_rank_min__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.2719, Lock IC=+0.1134, Sharpe=+1.4409

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2355, Lock IC=+0.1495, Sharpe=+1.4705

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
| 7-Year Jackknife | 1182 | 78 | 25 | 26 | 27 | 32% | 35% |
| B2 Rolling Guard | 254 | 78 | 34 | 24 | 20 | 44% | 26% |
| Temporal Validation Gate | 132 | 78 | 11 | 33 | 34 | 14% | 44% |
| BH-FDR Gate | 3 | 3 | 3 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 60 | 60 | 20 | 8 | 32 | 33% | 53% |
| B4 Correlation Gate | 103 | 78 | 12 | 11 | 55 | 15% | 71% |
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
- `combo_min__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.1565, Lock IC=+0.0788, Sharpe=+1.4456
- `combo_tri_min__first_bar_return__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1409, Lock IC=+0.0080, Sharpe=+0.5557
- `combo_tri_min__bar_ret_0__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1405, Lock IC=+0.0093, Sharpe=+0.5557

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1836, Lock IC=+0.0737, Sharpe=+1.3074
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2747, Lock IC=+0.0342, Sharpe=+1.2516
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2356, Lock IC=+0.0236, Sharpe=+0.8727

**Adaptive Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1836, Lock IC=+0.0737, Sharpe=+1.3074
- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.2141, Lock IC=+0.0747, Sharpe=+0.3762
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Train IC=+0.1600, Lock IC=+0.0283, Sharpe=+0.0760

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1583 | 78 | 32 | 19 | 27 | 41% | 35% |
| B2 Rolling Guard | 322 | 78 | 20 | 11 | 47 | 26% | 60% |
| Temporal Validation Gate | 249 | 78 | 20 | 21 | 37 | 26% | 47% |
| BH-FDR Gate | 11 | 11 | 11 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 276 | 78 | 0 | 19 | 59 | 0% | 76% |
| B6 Yearly IC CV Gate | 2 | 2 | 0 | 0 | 2 | 0% | 100% |
| B6 Temporal Stability Gate | 249 | 78 | 0 | 27 | 51 | 0% | 65% |
| B4 Correlation Gate | 484 | 78 | 0 | 14 | 64 | 0% | 82% |
| Adaptive Correlation Gate | 33 | 33 | 0 | 10 | 23 | 0% | 70% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2429, Lock IC=+0.0860, Sharpe=+0.7897
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0000, Lock IC=+0.0648, Sharpe=+1.0326
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1336, Lock IC=+0.0664, Sharpe=+0.9384
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1336, Lock IC=+0.0664, Sharpe=+0.9384

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293
- `combo_z_diff__smooth_momentum_structure__high_low_sequence_momentum`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293
- `combo_diff__smooth_momentum_structure__rsi_opening`: Train IC=+0.2636, Lock IC=+0.0912, Sharpe=+0.9293

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
| B2 Rolling Guard | 324 | 78 | 17 | 7 | 54 | 22% | 69% |
| Temporal Validation Gate | 46 | 46 | 5 | 11 | 30 | 11% | 65% |
| BH-FDR Gate | 5 | 5 | 1 | 0 | 4 | 20% | 80% |
| B3 Composite Floor | 257 | 78 | 0 | 6 | 72 | 0% | 92% |
| B4 Correlation Gate | 50 | 50 | 0 | 4 | 46 | 0% | 92% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.2719, Lock IC=+0.1134, Sharpe=+1.4409

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Sharpe=+1.7191
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2355, Lock IC=+0.1495, Sharpe=+1.4705

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
| recent_ic <= 0 (decayed) | 95 | 50 | 14 | 9 | 27 | 28% | 18% |
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
| recent_ic <= 0 (decayed) | 231 | 50 | 0 | 41 | 9 | 0% | 82% |
| recency_ratio >= 2.5 (late-concentrated) | 18 | 18 | 9 | 8 | 1 | 50% | 44% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__max_up_ret__first_bar_sentiment`: Train IC=+0.2356, Lock IC=+0.0793, Sharpe=+0.4892
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression`: Train IC=+0.1384, Lock IC=+0.0581, Sharpe=+0.4682
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.2296, Lock IC=+0.0651, Sharpe=+0.4412
- `combo_rank_max__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.2296, Lock IC=+0.0651, Sharpe=+0.4412
- `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment`: Train IC=+0.2199, Lock IC=+0.0692, Sharpe=+0.3202

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
| `max_up_ret` | 1 | 8 | 9 | 11% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `bar_ret_0` | 0 | 4 | 4 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 2 | 2 | 0% |  |
| `star50_limit_proximity_early` | 0 | 10 | 10 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 4 | 4 | 0% |  |
| `max_down_ret` | 0 | 6 | 6 | 0% |  |
| `bar_body_rng_0` | 0 | 2 | 2 | 0% |  |
| `close_vs_open_range` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 5 | 5 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=11, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=7, FP rate=22%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=3, FP rate=25%

