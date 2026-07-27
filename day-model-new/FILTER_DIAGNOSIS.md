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
| 300ETF | single | 11 | 3 | 0 | 8 | 27% | 0.57 |
| 500ETF | single | 42 | 0 | 10 | 32 | 0% | 0.77 |
| 159915ETF | single | 8 | 0 | 0 | 8 | 0% | 0.94 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=3, TP=8)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| weak_link_cv | 0.973 | 1.348 | 0.812 | 1.297 | -1.56 | 1.624 | 60% |
| ic_std_across_regimes | 0.056 | 0.081 | 0.059 | 0.083 | -1.41 | 0.104 | 64% |
| recency_ratio | 1.235 | 0.708 | 1.282 | 0.668 | +1.24 | 1.266 | 91% |
| half_ratio | 1.377 | 1.051 | 1.472 | 0.976 | +0.60 | 1.386 | 73% |
| n_negative_regimes | 1.000 | 1.500 | 1.000 | 1.500 | -0.59 | 2.500 | 64% |
| ic_cv | 0.823 | 1.464 | 0.865 | 0.832 | -0.57 | 3.465 | 64% |
| n_negative_years | 1.333 | 1.250 | 1.000 | 1.000 | +0.10 | 1.500 | 73% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_product__smooth_momentum_structure__opening_drive_thrust_ratio`** (Lock IC=-0.0238, Sharpe=-0.5100)
- Yearly ICs: 2015: +0.076 | 2016: -0.018 | 2017: +0.100 | 2018: -0.017 | 2019: +0.089 | 2020: +0.024 | 2021: +0.072
- IC CV=0.99, Neg years=2/7, Half ratio=1.47, Recency ratio=1.66
- Weak component: `opening_drive_thrust_ratio` (CV=0.81, neg years=1)
- Regime ICs: Q1_low_vol=+0.122, Q2=-0.051, Q3_mid=+0.108, Q4=-0.033, Q5_high_vol=+0.037

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0212, Sharpe=-0.4391)
- Yearly ICs: 2015: +0.102 | 2016: +0.042 | 2017: -0.000 | 2018: +0.124 | 2019: +0.044 | 2020: +0.006 | 2021: +0.179
- IC CV=0.87, Neg years=1/7, Half ratio=1.53, Recency ratio=1.28
- Weak component: `volume_weighted_price_position` (CV=1.30, neg years=1)
- Regime ICs: Q1_low_vol=-0.000, Q2=+0.032, Q3_mid=+0.060, Q4=+0.102, Q5_high_vol=+0.169

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0111, Sharpe=-0.2404)
- Yearly ICs: 2015: +0.087 | 2016: +0.109 | 2017: -0.010 | 2018: +0.157 | 2019: +0.086 | 2020: +0.035 | 2021: +0.115
- IC CV=0.62, Neg years=1/7, Half ratio=1.13, Recency ratio=0.76
- Weak component: `max_up_ret` (CV=0.81, neg years=1)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.041, Q3_mid=+0.135, Q4=+0.109, Q5_high_vol=+0.126

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 500ETF — `single` Median Features

**`combo_sig_product__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.1189, Sharpe=-0.2740)
- Yearly ICs: 2015: +0.164 | 2016: +0.045 | 2017: +0.234 | 2018: +0.062 | 2019: +0.071 | 2020: +0.098 | 2021: +0.088
- IC CV=0.57, Neg years=0/7, Half ratio=0.60, Recency ratio=0.89
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.035, Q3_mid=+0.124, Q4=+0.063, Q5_high_vol=+0.147

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0913, Sharpe=-0.2578)
- Yearly ICs: 2015: +0.146 | 2016: -0.049 | 2017: +0.116 | 2018: +0.052 | 2019: +0.111 | 2020: +0.099 | 2021: +0.059
- IC CV=0.78, Neg years=1/7, Half ratio=0.96, Recency ratio=1.62
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.082, Q3_mid=+0.074, Q4=+0.067, Q5_high_vol=+0.139

**`combo_clamp_diff__opening_drive_thrust_ratio__late_bar_momentum`** (Lock IC=+0.0846, Sharpe=-0.1942)
- Yearly ICs: 2015: +0.291 | 2016: +0.045 | 2017: +0.198 | 2018: +0.189 | 2019: +0.165 | 2020: +0.151 | 2021: +0.135
- IC CV=0.41, Neg years=0/7, Half ratio=1.02, Recency ratio=0.85
- Weak component: `late_bar_momentum` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.093, Q3_mid=+0.171, Q4=+0.124, Q5_high_vol=+0.292

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`** (Lock IC=+0.0843, Sharpe=-0.4259)
- Yearly ICs: 2015: +0.247 | 2016: +0.115 | 2017: +0.227 | 2018: +0.194 | 2019: +0.094 | 2020: +0.144 | 2021: +0.122
- IC CV=0.34, Neg years=0/7, Half ratio=0.70, Recency ratio=0.73
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.065, Q3_mid=+0.181, Q4=+0.172, Q5_high_vol=+0.269

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0810, Sharpe=-0.4849)
- Yearly ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172
- IC CV=0.33, Neg years=0/7, Half ratio=0.99, Recency ratio=0.89
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.128, Q3_mid=+0.198, Q4=+0.162, Q5_high_vol=+0.330

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0808, Sharpe=-0.5540)
- Yearly ICs: 2015: +0.279 | 2016: +0.108 | 2017: +0.193 | 2018: +0.220 | 2019: +0.126 | 2020: +0.106 | 2021: +0.167
- IC CV=0.35, Neg years=0/7, Half ratio=0.79, Recency ratio=0.71
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.044, Q3_mid=+0.181, Q4=+0.155, Q5_high_vol=+0.258

**`combo_rank_min__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0778, Sharpe=-0.5870)
- Yearly ICs: 2015: +0.253 | 2016: +0.133 | 2017: +0.179 | 2018: +0.182 | 2019: +0.113 | 2020: +0.101 | 2021: +0.065
- IC CV=0.40, Neg years=0/7, Half ratio=0.64, Recency ratio=0.43
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.011, Q3_mid=+0.170, Q4=+0.156, Q5_high_vol=+0.214

**`combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0685, Sharpe=-0.4390)
- Yearly ICs: 2015: +0.210 | 2016: +0.049 | 2017: +0.164 | 2018: +0.182 | 2019: +0.150 | 2020: +0.194 | 2021: +0.148
- IC CV=0.31, Neg years=0/7, Half ratio=1.42, Recency ratio=1.32
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.092, Q3_mid=+0.144, Q4=+0.092, Q5_high_vol=+0.272

**`vwap_trend_channel_slope`** (Lock IC=+0.0602, Sharpe=-0.5999)
- Yearly ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079
- IC CV=0.52, Neg years=0/7, Half ratio=0.87, Recency ratio=0.99
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.063, Q3_mid=+0.120, Q4=+0.066, Q5_high_vol=+0.119

**`combo_sig_product__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0286, Sharpe=-0.7078)
- Yearly ICs: 2015: +0.111 | 2016: +0.005 | 2017: +0.142 | 2018: +0.143 | 2019: +0.074 | 2020: +0.060 | 2021: +0.067
- IC CV=0.53, Neg years=0/7, Half ratio=0.90, Recency ratio=1.09
- Weak component: `trend_day_regime_conviction` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.102, Q2=-0.054, Q3_mid=+0.156, Q4=+0.071, Q5_high_vol=+0.110

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0342, Sharpe=+1.2516)
- Yearly ICs: 2015: +0.266 | 2016: +0.117 | 2017: -0.053 | 2018: +0.140 | 2019: +0.100 | 2020: +0.074 | 2021: +0.143
- IC CV=0.78, Neg years=1/7, Half ratio=0.77, Recency ratio=0.57
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0016, Sharpe=+0.5869)
- Yearly ICs: 2015: +0.223 | 2016: -0.064 | 2017: +0.071 | 2018: -0.050 | 2019: -0.011 | 2020: +0.022 | 2021: -0.071
- IC CV=5.62, Neg years=4/7, Half ratio=-0.29, Recency ratio=-0.31
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0706, Sharpe=+0.4878)
- Yearly ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130
- IC CV=0.88, Neg years=1/7, Half ratio=1.82, Recency ratio=1.12
- Weak component: `limit_down_proximity_early` (CV=1.62)

**`combo_rel_diff__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0747, Sharpe=+0.3762)
- Yearly ICs: 2015: +0.094 | 2016: +0.037 | 2017: -0.008 | 2018: +0.101 | 2019: +0.086 | 2020: +0.012 | 2021: +0.146
- IC CV=0.76, Neg years=1/7, Half ratio=2.31, Recency ratio=1.21
- Weak component: `limit_down_proximity_early` (CV=1.62)

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0184, Sharpe=+0.3625)
- Yearly ICs: 2015: +0.098 | 2016: +0.068 | 2017: +0.034 | 2018: +0.193 | 2019: +0.044 | 2020: +0.042 | 2021: +0.166
- IC CV=0.64, Neg years=0/7, Half ratio=1.30, Recency ratio=1.25
- Weak component: `early_vwap_acceleration` (CV=0.99)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0616, Sharpe=+0.2757)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095
- IC CV=1.14, Neg years=1/7, Half ratio=0.62, Recency ratio=0.50

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0120, Sharpe=+0.2477)
- Yearly ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156
- IC CV=0.58, Neg years=1/7, Half ratio=1.19, Recency ratio=0.77
- Weak component: `volume_weighted_price_position` (CV=1.30)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.0696, Sharpe=+0.2355)
- Yearly ICs: 2015: +0.193 | 2016: +0.045 | 2017: -0.102 | 2018: +0.110 | 2019: +0.072 | 2020: +0.029 | 2021: +0.103
- IC CV=1.31, Neg years=1/7, Half ratio=0.69, Recency ratio=0.55
- Weak component: `limit_down_proximity_early` (CV=1.62)

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1183, Sharpe=+1.6160)
- Yearly ICs: 2015: +0.294 | 2016: +0.022 | 2017: +0.204 | 2018: +0.144 | 2019: +0.184 | 2020: +0.146 | 2021: +0.091
- IC CV=0.51, Neg years=0/7, Half ratio=0.88, Recency ratio=0.75
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1139, Sharpe=+1.4937)
- Yearly ICs: 2015: +0.268 | 2016: +0.119 | 2017: +0.110 | 2018: +0.189 | 2019: +0.088 | 2020: +0.115 | 2021: +0.140
- IC CV=0.39, Neg years=0/7, Half ratio=0.73, Recency ratio=0.66
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1083, Sharpe=+1.3443)
- Yearly ICs: 2015: +0.289 | 2016: +0.074 | 2017: +0.196 | 2018: +0.155 | 2019: +0.174 | 2020: +0.112 | 2021: +0.096
- IC CV=0.43, Neg years=0/7, Half ratio=0.71, Recency ratio=0.57
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rank_min__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1321, Sharpe=+1.3027)
- Yearly ICs: 2015: +0.218 | 2016: +0.059 | 2017: +0.233 | 2018: +0.094 | 2019: +0.128 | 2020: +0.129 | 2021: +0.103
- IC CV=0.43, Neg years=0/7, Half ratio=0.77, Recency ratio=0.84
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1256, Sharpe=+1.1032)
- Yearly ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.194 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148
- IC CV=0.42, Neg years=0/7, Half ratio=1.09, Recency ratio=1.10
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1100, Sharpe=+1.0815)
- Yearly ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052
- IC CV=0.52, Neg years=0/7, Half ratio=0.67, Recency ratio=0.56
- Weak component: `max_down_ret` (CV=0.55)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0991, Sharpe=+1.0237)
- Yearly ICs: 2015: +0.313 | 2016: +0.094 | 2017: +0.215 | 2018: +0.203 | 2019: +0.178 | 2020: +0.143 | 2021: +0.098
- IC CV=0.40, Neg years=0/7, Half ratio=0.70, Recency ratio=0.59
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0943, Sharpe=+0.8842)
- Yearly ICs: 2015: +0.280 | 2016: +0.069 | 2017: +0.269 | 2018: +0.189 | 2019: +0.147 | 2020: +0.176 | 2021: +0.098
- IC CV=0.42, Neg years=0/7, Half ratio=0.86, Recency ratio=0.78
- Weak component: `max_down_ret` (CV=0.55)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1261, Sharpe=+0.8321)
- Yearly ICs: 2015: +0.245 | 2016: +0.138 | 2017: +0.226 | 2018: +0.116 | 2019: +0.121 | 2020: +0.123 | 2021: +0.067
- IC CV=0.40, Neg years=0/7, Half ratio=0.47, Recency ratio=0.49

**`combo_rel_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0020, Sharpe=+0.7804)
- Yearly ICs: 2015: +0.149 | 2016: +0.138 | 2017: -0.011 | 2018: +0.082 | 2019: +0.070 | 2020: +0.030 | 2021: +0.081
- IC CV=0.68, Neg years=1/7, Half ratio=0.62, Recency ratio=0.39
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_sig_product__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0992, Sharpe=+0.7582)
- Yearly ICs: 2015: +0.236 | 2016: +0.145 | 2017: +0.119 | 2018: +0.143 | 2019: +0.067 | 2020: +0.118 | 2021: +0.071
- IC CV=0.41, Neg years=0/7, Half ratio=0.69, Recency ratio=0.50
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_mean__bar_ret_0__max_down_ret`** (Lock IC=+0.1025, Sharpe=+0.7111)
- Yearly ICs: 2015: +0.227 | 2016: +0.106 | 2017: +0.224 | 2018: +0.210 | 2019: +0.137 | 2020: +0.111 | 2021: +0.088
- IC CV=0.36, Neg years=0/7, Half ratio=0.81, Recency ratio=0.60
- Weak component: `max_down_ret` (CV=0.55)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1504, Sharpe=+0.5807)
- Yearly ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089
- IC CV=0.38, Neg years=0/7, Half ratio=0.79, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1679, Sharpe=+0.5771)
- Yearly ICs: 2015: +0.130 | 2016: -0.082 | 2017: +0.229 | 2018: -0.004 | 2019: +0.128 | 2020: +0.110 | 2021: +0.103
- IC CV=1.06, Neg years=2/7, Half ratio=1.20, Recency ratio=4.41
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0995, Sharpe=+0.5483)
- Yearly ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022
- IC CV=0.53, Neg years=0/7, Half ratio=0.63, Recency ratio=0.44
- Weak component: `max_down_ret` (CV=0.55)

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0907, Sharpe=+0.4826)
- Yearly ICs: 2015: +0.310 | 2016: +0.110 | 2017: +0.179 | 2018: +0.192 | 2019: +0.131 | 2020: +0.145 | 2021: +0.107
- IC CV=0.39, Neg years=0/7, Half ratio=0.63, Recency ratio=0.60
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1114, Sharpe=+0.4728)
- Yearly ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.232 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.072
- IC CV=0.60, Neg years=0/7, Half ratio=0.58, Recency ratio=0.53
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1001, Sharpe=+0.4564)
- Yearly ICs: 2015: +0.270 | 2016: +0.153 | 2017: +0.085 | 2018: +0.126 | 2019: +0.079 | 2020: +0.129 | 2021: +0.109
- IC CV=0.44, Neg years=0/7, Half ratio=0.69, Recency ratio=0.56
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1115, Sharpe=+0.4562)
- Yearly ICs: 2015: +0.313 | 2016: +0.098 | 2017: +0.234 | 2018: +0.157 | 2019: +0.132 | 2020: +0.173 | 2021: +0.075
- IC CV=0.45, Neg years=0/7, Half ratio=0.65, Recency ratio=0.60
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0948, Sharpe=+0.4283)
- Yearly ICs: 2015: +0.297 | 2016: +0.084 | 2017: +0.247 | 2018: +0.154 | 2019: +0.106 | 2020: +0.168 | 2021: +0.113
- IC CV=0.43, Neg years=0/7, Half ratio=0.73, Recency ratio=0.74
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1226, Sharpe=+0.4270)
- Yearly ICs: 2015: +0.270 | 2016: +0.058 | 2017: +0.232 | 2018: +0.171 | 2019: +0.151 | 2020: +0.152 | 2021: +0.140
- IC CV=0.38, Neg years=0/7, Half ratio=0.81, Recency ratio=0.89
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0949, Sharpe=+0.3837)
- Yearly ICs: 2015: +0.263 | 2016: +0.080 | 2017: +0.216 | 2018: +0.198 | 2019: +0.144 | 2020: +0.159 | 2021: +0.107
- IC CV=0.35, Neg years=0/7, Half ratio=0.75, Recency ratio=0.78
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_rank_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1039, Sharpe=+0.2943)
- Yearly ICs: 2015: +0.231 | 2016: +0.111 | 2017: +0.207 | 2018: +0.196 | 2019: +0.110 | 2020: +0.121 | 2021: +0.062
- IC CV=0.39, Neg years=0/7, Half ratio=0.60, Recency ratio=0.54
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0879, Sharpe=+0.2708)
- Yearly ICs: 2015: +0.212 | 2016: +0.116 | 2017: +0.206 | 2018: +0.042 | 2019: +0.139 | 2020: +0.111 | 2021: +0.105
- IC CV=0.42, Neg years=0/7, Half ratio=0.58, Recency ratio=0.66
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0778, Sharpe=+0.2187)
- Yearly ICs: 2015: +0.307 | 2016: +0.108 | 2017: +0.187 | 2018: +0.214 | 2019: +0.121 | 2020: +0.142 | 2021: +0.152
- IC CV=0.36, Neg years=0/7, Half ratio=0.80, Recency ratio=0.71
- Weak component: `early_late_momentum_divergence` (CV=0.56)

**`combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0439, Sharpe=+0.1933)
- Yearly ICs: 2015: +0.198 | 2016: +0.031 | 2017: +0.038 | 2018: +0.083 | 2019: +0.134 | 2020: +0.109 | 2021: +0.111
- IC CV=0.53, Neg years=0/7, Half ratio=1.55, Recency ratio=0.96
- Weak component: `trend_bar_close_consistency` (CV=0.73)

**`combo_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0693, Sharpe=+0.1614)
- Yearly ICs: 2015: +0.215 | 2016: +0.100 | 2017: +0.147 | 2018: +0.200 | 2019: +0.067 | 2020: +0.125 | 2021: +0.058
- IC CV=0.43, Neg years=0/7, Half ratio=0.67, Recency ratio=0.58
- Weak component: `early_body_momentum` (CV=0.39)

**`combo_ratio__max_down_ret__net_volume_flow`** (Lock IC=+0.1213, Sharpe=+0.1422)
- Yearly ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004
- IC CV=0.47, Neg years=0/7, Half ratio=0.64, Recency ratio=0.42
- Weak component: `max_down_ret` (CV=0.55)

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0712, Sharpe=+0.1313)
- Yearly ICs: 2015: +0.244 | 2016: +0.102 | 2017: +0.094 | 2018: +0.267 | 2019: +0.112 | 2020: +0.108 | 2021: +0.178
- IC CV=0.43, Neg years=0/7, Half ratio=0.86, Recency ratio=0.83
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0538, Sharpe=+0.1090)
- Yearly ICs: 2015: +0.227 | 2016: +0.131 | 2017: +0.079 | 2018: +0.166 | 2019: +0.094 | 2020: +0.138 | 2021: +0.079
- IC CV=0.38, Neg years=0/7, Half ratio=0.88, Recency ratio=0.60
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_sig_product__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1170, Sharpe=+0.0449)
- Yearly ICs: 2015: +0.152 | 2016: +0.029 | 2017: +0.255 | 2018: +0.022 | 2019: +0.109 | 2020: +0.115 | 2021: +0.073
- IC CV=0.69, Neg years=0/7, Half ratio=0.69, Recency ratio=1.04
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0773, Sharpe=+0.0073)
- Yearly ICs: 2015: +0.296 | 2016: +0.104 | 2017: +0.192 | 2018: +0.209 | 2019: +0.154 | 2020: +0.167 | 2021: +0.138
- IC CV=0.32, Neg years=0/7, Half ratio=0.89, Recency ratio=0.76
- Weak component: `body_size_progression` (CV=0.54)

### 159915ETF — `single` True Positives

**`combo_z_sum__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1307, Sharpe=+2.0165)
- Yearly ICs: 2015: +0.217 | 2016: +0.098 | 2017: -0.029 | 2018: +0.150 | 2019: +0.229 | 2020: +0.133 | 2021: +0.132
- IC CV=0.60, Neg years=1/7, Half ratio=1.53, Recency ratio=0.84
- Weak component: `limit_down_proximity_early` (CV=1.21)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1147, Sharpe=+1.4823)
- Yearly ICs: 2015: +0.254 | 2016: +0.171 | 2017: -0.008 | 2018: +0.180 | 2019: +0.206 | 2020: +0.202 | 2021: +0.114
- IC CV=0.50, Neg years=1/7, Half ratio=1.09, Recency ratio=0.74
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1355, Sharpe=+1.4543)
- Yearly ICs: 2015: +0.184 | 2016: +0.087 | 2017: +0.006 | 2018: +0.160 | 2019: +0.235 | 2020: +0.131 | 2021: +0.144
- IC CV=0.50, Neg years=0/7, Half ratio=1.27, Recency ratio=1.01
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1311, Sharpe=+1.1520)
- Yearly ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087
- IC CV=0.73, Neg years=0/7, Half ratio=0.82, Recency ratio=0.73
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1192, Sharpe=+0.6699)
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034
- IC CV=0.90, Neg years=1/7, Half ratio=0.89, Recency ratio=0.61
- Weak component: `yesterday_first_30min_return` (CV=1.04)

**`combo_clamp_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1021, Sharpe=+0.6179)
- Yearly ICs: 2015: +0.193 | 2016: +0.029 | 2017: +0.020 | 2018: +0.081 | 2019: +0.180 | 2020: +0.093 | 2021: +0.157
- IC CV=0.60, Neg years=0/7, Half ratio=1.36, Recency ratio=1.12
- Weak component: `demark_setup_reversal_early` (CV=0.85)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1297, Sharpe=+0.5252)
- Yearly ICs: 2015: +0.232 | 2016: +0.175 | 2017: -0.028 | 2018: +0.143 | 2019: +0.206 | 2020: +0.138 | 2021: +0.124
- IC CV=0.55, Neg years=1/7, Half ratio=1.22, Recency ratio=0.64
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_z_sum__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0866, Sharpe=+0.2848)
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
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1093 | +0.0576 | +0.1515 | 2y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.1093 | +0.0449 | +0.1569 | 1y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | TP | persistent | +0.0960 | +0.0234 | +0.1970 | 1y |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | TP | persistent | +0.0930 | +0.0212 | +0.1873 | 1y |
| `combo_min__max_up_ret__first_bar_sentiment` | FP | gradual | +0.0576 | +0.1502 | -0.0647 | 2y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0422 | +0.2027 | -0.1995 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0369 | +0.1355 | -0.0350 | 4y |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.0283 | +0.1374 | -0.0976 | 4y |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | TP | gradual | +0.0168 | +0.1601 | -0.0787 | 4y |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | immediate | -0.0453 | +0.0618 | -0.0376 | ∞ |
| `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio` | FP | immediate | -0.1021 | -0.0764 | -0.1781 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=0, gradual=5, persistent=4

**FP decay trajectories:**

- `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio`: Y1:-0.102 → Y2:-0.076 → Y3:+0.005 → Y4:+0.035 → Y5:-0.178
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:+0.042 → Y2:+0.203 → Y3:+0.025 → Y4:+0.086 → Y5:-0.200
- `combo_min__max_up_ret__first_bar_sentiment`: Y1:+0.058 → Y2:+0.150 → Y3:+0.012 → Y4:+0.033 → Y5:-0.065

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1281 | +0.0718 | +0.1198 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Median | gradual | +0.1278 | +0.0960 | -0.0439 | 4y |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1204 | +0.0726 | +0.1121 | ∞ |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1162 | +0.1552 | +0.0293 | 4y |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1159 | +0.0796 | -0.0265 | 4y |
| `combo_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1130 | +0.0872 | -0.0648 | 4y |
| `combo_sig_product__trend_day_regime_conviction__bar_ret_0` | Median | gradual | +0.1127 | +0.0590 | -0.1212 | 4y |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1053 | +0.0568 | +0.2040 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.1027 | +0.0847 | +0.0947 | ∞ |
| `combo_max__max_up_ret__first_bar_sentiment` | TP | gradual | +0.0993 | +0.0551 | -0.0397 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | gradual | +0.0966 | +0.1332 | -0.0072 | 4y |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0404 | 1y |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | TP | gradual | +0.0964 | +0.0699 | -0.0186 | 4y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0942 | +0.0937 | +0.0717 | 3y |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0934 | +0.0884 | +0.0187 | 4y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0921 | +0.0793 | +0.1842 | ∞ |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0885 | +0.1234 | +0.0058 | 4y |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0824 | +0.0767 | +0.0885 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0756 | +0.0530 | +0.0807 | ∞ |
| `combo_mean__bar_ret_0__max_down_ret` | TP | persistent | +0.0721 | +0.0548 | +0.0105 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0701 | +0.0496 | +0.0708 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0667 | +0.0659 | +0.1729 | ∞ |
| `vwap_trend_channel_slope` | Median | gradual | +0.0667 | +0.1186 | -0.0312 | 4y |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0641 | +0.0925 | +0.1061 | ∞ |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0617 | +0.0718 | +0.0910 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.0615 | +0.0744 | +0.0820 | ∞ |
| `combo_rank_min__close_vs_open_range__first_bar_sentiment` | Median | gradual | +0.0603 | +0.0596 | -0.0000 | 4y |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0577 | +0.1003 | +0.2035 | ∞ |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0570 | +0.0915 | +0.1035 | 3y |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | TP | fast | +0.0569 | -0.0040 | +0.1243 | 1y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0514 | +0.0668 | +0.2403 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0509 | +0.0691 | +0.0097 | 4y |
| `combo_clamp_diff__opening_drive_thrust_ratio__late_bar_momentum` | Median | persistent | +0.0473 | +0.0986 | +0.1046 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0396 | +0.0769 | +0.0854 | ∞ |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Median | gradual | +0.0315 | +0.0144 | -0.0292 | 1y |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0279 | +0.0649 | +0.0855 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0158 | +0.0999 | +0.1018 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | persistent | +0.0093 | +0.0167 | +0.1802 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Median | persistent | +0.0063 | +0.1139 | +0.0526 | ∞ |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | TP | immediate | -0.0168 | -0.0247 | +0.1016 | ∞ |
| `combo_ratio__max_down_ret__net_volume_flow` | TP | immediate | -0.0560 | +0.0066 | +0.1091 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=1, gradual=10, persistent=29

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1776 | +0.1159 | +0.1263 | 2y |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | TP | gradual | +0.1564 | +0.1470 | -0.0204 | 2y |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1388 | +0.0826 | +0.1479 | ∞ |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1062 | +0.1869 | +0.0371 | 4y |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1023 | +0.1961 | -0.0670 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0899 | +0.1369 | +0.0817 | ∞ |
| `combo_z_sum__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0858 | +0.1120 | +0.1316 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0799 | +0.1128 | +0.0949 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=2, persistent=6

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.702±0.059 | 0.708±0.037 | 80% | USELESS |
| ic_ir | 0.563±0.151 | 0.536±0.073 | 73% | WEAK |
| p_value | 0.002±0.002 | 0.001±0.001 | 96% | USELESS |
| max_corr | 0.502±0.283 | 0.540±0.269 | 78% | WEAK |
| deflated_ic | 0.180±0.021 | 0.204±0.032 | 41% | USEFUL |
| overall_ic | 0.180±0.019 | 0.204±0.031 | 38% | USEFUL |
| raw_ic | 0.071±0.022 | 0.080±0.031 | 49% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 8/20 top rejects are profitable (40%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.2340, Lock IC=+0.0050, Sharpe=+0.4905

**B2 Rolling Guard**: 7/20 top rejects are profitable (35%)

- `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1637, Lock IC=+0.0306, Sharpe=+0.6413
- `gap_pct`: Train IC=+0.1525, Lock IC=+0.0795, Sharpe=+0.4477
- `combo_min__bar_ret_0__volume_surge_direction`: Train IC=+0.1563, Lock IC=+0.0151, Sharpe=+0.3242

**BH-FDR Gate**: 10/18 top rejects are profitable (56%)

- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0260, Sharpe=+0.6440
- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0280, Sharpe=+0.6440
- `combo_sig_product__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1072, Lock IC=+0.0233, Sharpe=+0.6440

**B3 Composite Floor**: 4/11 top rejects are profitable (36%)

- `combo_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1556, Lock IC=+0.0646, Sharpe=+0.6057
- `combo_min__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1556, Lock IC=+0.0646, Sharpe=+0.6057
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1636, Lock IC=+0.0026, Sharpe=+0.3167

**B4 Correlation Gate**: 15/16 top rejects are profitable (94%)

- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2037, Lock IC=+0.0658, Sharpe=+0.4921
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2037, Lock IC=+0.0658, Sharpe=+0.4921
- `combo_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1914, Lock IC=+0.0675, Sharpe=+0.4271

### 500ETF — `single`

**7-Year Jackknife**: 18/20 top rejects are profitable (90%)

- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2426, Lock IC=+0.0860, Sharpe=+0.7897
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897

**B2 Rolling Guard**: 16/20 top rejects are profitable (80%)

- `combo_rank_max__first_bar_sentiment__early_body_momentum`: Train IC=+0.1912, Lock IC=+0.0630, Sharpe=+1.1475
- `combo_rank_max__first_bar_sentiment__opening_momentum_score`: Train IC=+0.1912, Lock IC=+0.0630, Sharpe=+1.1475
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Sharpe=+0.7965

**BH-FDR Gate**: 2/15 top rejects are profitable (13%)

- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.5766
- `combo_z_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.5766

**B3 Composite Floor**: 18/20 top rejects are profitable (90%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_day_regime_conviction`: Train IC=+0.2819, Lock IC=+0.1041, Sharpe=+1.2212
- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2806, Lock IC=+0.1172, Sharpe=+1.1947
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2806, Lock IC=+0.1172, Sharpe=+1.1947

**B4 Correlation Gate**: 18/20 top rejects are profitable (90%)

- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.3443
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+1.1454
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+1.1454

**Adaptive Correlation Gate**: 18/20 top rejects are profitable (90%)

- `combo_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2426, Lock IC=+0.1093, Sharpe=+1.3542
- `combo_rank_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.2149, Lock IC=+0.1459, Sharpe=+0.9887
- `combo_sig_product__max_up_ret__body_size_progression`: Train IC=+0.2143, Lock IC=+0.1120, Sharpe=+0.8178

### 159915ETF — `single`

**7-Year Jackknife**: 13/20 top rejects are profitable (65%)

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2092, Lock IC=+0.1358, Sharpe=+1.1251

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+1.1250
- `combo_z_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+1.1250
- `combo_tri_median__first_bar_sentiment__bar_body_rng_0__first_bar_return`: Train IC=+0.1949, Lock IC=+0.0856, Sharpe=+0.8407

**BH-FDR Gate**: 8/15 top rejects are profitable (53%)

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Sharpe=+1.0460

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.8373

**B4 Correlation Gate**: 14/14 top rejects are profitable (100%)

- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Sharpe=+1.8188
- `combo_z_sum__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2225, Lock IC=+0.1219, Sharpe=+1.7502

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1044 | 78 | 33 | 25 | 20 | 42% | 26% |
| B2 Rolling Guard | 130 | 78 | 37 | 29 | 12 | 47% | 15% |
| BH-FDR Gate | 18 | 18 | 8 | 0 | 10 | 44% | 56% |
| B3 Composite Floor | 11 | 11 | 4 | 3 | 4 | 36% | 36% |
| B4 Correlation Gate | 16 | 16 | 1 | 0 | 15 | 6% | 94% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.8717
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.2340, Lock IC=+0.0050, Sharpe=+0.4905

**BH-FDR Gate** — top TP casualties:
- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0260, Sharpe=+0.6440
- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0280, Sharpe=+0.6440
- `combo_sig_product__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1072, Lock IC=+0.0233, Sharpe=+0.6440

**B3 Composite Floor** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1556, Lock IC=+0.0646, Sharpe=+0.6057
- `combo_min__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1556, Lock IC=+0.0646, Sharpe=+0.6057
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1636, Lock IC=+0.0026, Sharpe=+0.3167

**B4 Correlation Gate** — top TP casualties:
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2037, Lock IC=+0.0658, Sharpe=+0.4921
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2037, Lock IC=+0.0658, Sharpe=+0.4921
- `combo_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1914, Lock IC=+0.0675, Sharpe=+0.4271

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1491 | 78 | 19 | 29 | 30 | 24% | 38% |
| B2 Rolling Guard | 141 | 78 | 18 | 24 | 36 | 23% | 46% |
| BH-FDR Gate | 15 | 15 | 11 | 2 | 2 | 73% | 13% |
| B3 Composite Floor | 323 | 78 | 3 | 14 | 61 | 4% | 78% |
| B4 Correlation Gate | 452 | 78 | 1 | 15 | 62 | 1% | 79% |
| Adaptive Correlation Gate | 39 | 39 | 3 | 8 | 28 | 8% | 72% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2426, Lock IC=+0.0860, Sharpe=+0.7897
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Sharpe=+0.7897

**B2 Rolling Guard** — top TP casualties:
- `combo_rank_max__first_bar_sentiment__early_body_momentum`: Train IC=+0.1912, Lock IC=+0.0630, Sharpe=+1.1475
- `combo_rank_max__first_bar_sentiment__opening_momentum_score`: Train IC=+0.1912, Lock IC=+0.0630, Sharpe=+1.1475
- `iv_diff_1d`: Train IC=+0.0000, Lock IC=+0.0648, Sharpe=+1.0326

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1986, Lock IC=+0.0503, Sharpe=+1.2596
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_day_regime_conviction`: Train IC=+0.2819, Lock IC=+0.1041, Sharpe=+1.2212
- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2806, Lock IC=+0.1172, Sharpe=+1.1947

**B4 Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.3443
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+1.1454
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Sharpe=+1.1454

**Adaptive Correlation Gate** — top TP casualties:
- `combo_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2426, Lock IC=+0.1093, Sharpe=+1.3542
- `combo_rank_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.2149, Lock IC=+0.1459, Sharpe=+0.9887
- `combo_sig_product__max_up_ret__body_size_progression`: Train IC=+0.2143, Lock IC=+0.1120, Sharpe=+0.8178

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1116 | 78 | 20 | 20 | 38 | 26% | 49% |
| B2 Rolling Guard | 229 | 78 | 22 | 11 | 45 | 28% | 58% |
| BH-FDR Gate | 15 | 15 | 2 | 5 | 8 | 13% | 53% |
| B3 Composite Floor | 186 | 78 | 1 | 16 | 61 | 1% | 78% |
| B4 Correlation Gate | 14 | 14 | 0 | 0 | 14 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Sharpe=+1.6125
- `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2092, Lock IC=+0.1358, Sharpe=+1.1251

**B2 Rolling Guard** — top TP casualties:
- `combo_max__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1229, Lock IC=+0.0882, Sharpe=+1.1675
- `combo_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1229, Lock IC=+0.0882, Sharpe=+1.1675
- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+1.1250

**BH-FDR Gate** — top TP casualties:
- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Sharpe=+1.0460
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Sharpe=+1.0460

**B3 Composite Floor** — top TP casualties:
- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.8373

**B4 Correlation Gate** — top TP casualties:
- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Sharpe=+2.0165
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Sharpe=+1.8188
- `combo_z_sum__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2225, Lock IC=+0.1219, Sharpe=+1.7502

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `weak_link_cv`: FP is lower (d=-1.56). Threshold 1.624 → 60% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-1.41). Threshold 0.104 → 64% accuracy.
- `recency_ratio`: FP is higher (d=+1.24). Threshold 1.266 → 91% accuracy.
- `half_ratio`: FP is higher (d=+0.60). Threshold 1.386 → 73% accuracy.
- `n_negative_regimes`: FP is lower (d=-0.59). Threshold 2.500 → 64% accuracy.
- `ic_cv`: FP is lower (d=-0.57). Threshold 3.465 → 64% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/3
- Decaying signal (half ratio < 0.3): 0/3
- Weak component (CV > 2.0): 0/3
- Regime-dependent (≥2 negative regimes): 1/3

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_weighted_price_position` | 1 | 1 | 2 | 50% |  |
| `first_bar_sentiment` | 1 | 5 | 6 | 17% |  |
| `max_up_ret` | 2 | 15 | 17 | 12% |  |
| `opening_drive_thrust_ratio` | 1 | 8 | 9 | 11% |  |
| `star50_limit_proximity_early` | 0 | 13 | 13 | 0% |  |
| `max_down_ret` | 0 | 6 | 6 | 0% |  |
| `close_vs_open_range` | 0 | 3 | 3 | 0% |  |
| `trend_bar_close_consistency` | 0 | 4 | 4 | 0% |  |
| `body_size_progression` | 0 | 3 | 3 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 2 | 2 | 0% |  |
| `volume_concentration` | 0 | 2 | 2 | 0% |  |
| `limit_down_proximity_early` | 0 | 4 | 4 | 0% |  |
| `bar_body_rng_0` | 0 | 3 | 3 | 0% |  |
| `early_body_momentum` | 0 | 2 | 2 | 0% |  |
| `bar_ret_0` | 0 | 5 | 5 | 0% |  |
| `net_volume_flow` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 10 | 10 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 3 | 3 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=2, TP=17, FP rate=11%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=10, FP rate=9%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=3, FP rate=0%

