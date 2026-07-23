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
| 300ETF | single | 11 | 2 | 4 | 5 | 18% | 0.50 |
| 500ETF | single | 51 | 0 | 20 | 31 | 0% | 0.72 |
| 159915ETF | single | 13 | 0 | 2 | 11 | 0% | 0.89 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=2, TP=5)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_std_across_regimes | 0.051 | 0.090 | 0.051 | 0.090 | -4.40 | 0.102 | 57% |
| n_negative_regimes | 0.500 | 1.400 | 0.500 | 1.000 | -1.12 | 2.500 | 57% |
| ic_cv | 0.801 | 1.787 | 0.801 | 0.880 | -0.73 | 3.252 | 57% |
| n_negative_years | 1.000 | 1.600 | 1.000 | 1.000 | -0.71 | 2.500 | 57% |
| weak_link_cv | 1.157 | 1.252 | 1.157 | 1.141 | -0.58 | 1.256 | 71% |
| recency_ratio | 0.763 | 0.549 | 0.763 | 0.626 | +0.56 | 0.884 | 71% |
| half_ratio | 1.064 | 0.888 | 1.064 | 1.025 | +0.35 | 1.193 | 71% |

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

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0280, Sharpe=-0.3103)
- Yearly ICs: 2015: +0.254 | 2016: +0.095 | 2017: +0.008 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132
- IC CV=0.65, Neg years=0/7, Half ratio=0.81, Recency ratio=0.50
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.027, Q3_mid=+0.113, Q4=+0.191, Q5_high_vol=+0.227

**`combo_tri_mean__star50_limit_proximity_early__first_bar_return__first_bar_sentiment`** (Lock IC=+0.0237, Sharpe=-0.1462)
- Yearly ICs: 2015: +0.196 | 2016: +0.088 | 2017: -0.004 | 2018: +0.193 | 2019: +0.117 | 2020: +0.038 | 2021: +0.124
- IC CV=0.64, Neg years=1/7, Half ratio=0.91, Recency ratio=0.57
- Weak component: `star50_limit_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.035, Q3_mid=+0.137, Q4=+0.154, Q5_high_vol=+0.180

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

**`combo_rank_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.1037, Sharpe=-0.0814)
- Yearly ICs: 2015: +0.211 | 2016: +0.082 | 2017: +0.181 | 2018: +0.172 | 2019: +0.115 | 2020: +0.063 | 2021: +0.056
- IC CV=0.46, Neg years=0/7, Half ratio=0.63, Recency ratio=0.41
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.031, Q3_mid=+0.122, Q4=+0.142, Q5_high_vol=+0.185

**`combo_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.1022, Sharpe=-0.0410)
- Yearly ICs: 2015: +0.205 | 2016: +0.084 | 2017: +0.185 | 2018: +0.173 | 2019: +0.118 | 2020: +0.064 | 2021: +0.057
- IC CV=0.45, Neg years=0/7, Half ratio=0.64, Recency ratio=0.42
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.028, Q3_mid=+0.123, Q4=+0.138, Q5_high_vol=+0.185

**`combo_rank_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.1003, Sharpe=-0.5172)
- Yearly ICs: 2015: +0.286 | 2016: +0.089 | 2017: +0.190 | 2018: +0.136 | 2019: +0.148 | 2020: +0.136 | 2021: +0.087
- IC CV=0.41, Neg years=0/7, Half ratio=0.86, Recency ratio=0.59
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.026, Q3_mid=+0.136, Q4=+0.104, Q5_high_vol=+0.248

**`combo_z_sum__opening_auction_imbalance__max_down_ret`** (Lock IC=+0.0977, Sharpe=-0.3952)
- Yearly ICs: 2015: +0.230 | 2016: +0.074 | 2017: +0.188 | 2018: +0.155 | 2019: +0.099 | 2020: +0.118 | 2021: +0.078
- IC CV=0.41, Neg years=0/7, Half ratio=0.80, Recency ratio=0.64
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.014, Q3_mid=+0.152, Q4=+0.112, Q5_high_vol=+0.211

**`combo_rank_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0942, Sharpe=-0.1917)
- Yearly ICs: 2015: +0.196 | 2016: +0.090 | 2017: +0.179 | 2018: +0.119 | 2019: +0.066 | 2020: +0.108 | 2021: +0.119
- IC CV=0.34, Neg years=0/7, Half ratio=0.66, Recency ratio=0.79
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.032, Q3_mid=+0.153, Q4=+0.129, Q5_high_vol=+0.157

**`combo_sig_product__max_up_ret__rsi_opening`** (Lock IC=+0.0927, Sharpe=-0.5972)
- Yearly ICs: 2015: +0.212 | 2016: +0.114 | 2017: +0.088 | 2018: +0.148 | 2019: +0.071 | 2020: +0.140 | 2021: +0.093
- IC CV=0.36, Neg years=0/7, Half ratio=0.81, Recency ratio=0.71
- Weak component: `rsi_opening` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.055, Q3_mid=+0.126, Q4=+0.167, Q5_high_vol=+0.211

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0879, Sharpe=-0.1032)
- Yearly ICs: 2015: +0.212 | 2016: +0.116 | 2017: +0.206 | 2018: +0.042 | 2019: +0.139 | 2020: +0.111 | 2021: +0.105
- IC CV=0.42, Neg years=0/7, Half ratio=0.58, Recency ratio=0.66
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.090, Q3_mid=+0.093, Q4=+0.140, Q5_high_vol=+0.221

**`combo_rank_max__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0870, Sharpe=-1.0229)
- Yearly ICs: 2015: +0.251 | 2016: +0.095 | 2017: +0.169 | 2018: +0.142 | 2019: +0.095 | 2020: +0.129 | 2021: +0.131
- IC CV=0.34, Neg years=0/7, Half ratio=0.80, Recency ratio=0.75
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.002, Q3_mid=+0.169, Q4=+0.162, Q5_high_vol=+0.197

**`combo_tri_min__max_up_ret__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0831, Sharpe=-0.4346)
- Yearly ICs: 2015: +0.236 | 2016: +0.130 | 2017: +0.185 | 2018: +0.210 | 2019: +0.118 | 2020: +0.094 | 2021: +0.089
- IC CV=0.36, Neg years=0/7, Half ratio=0.65, Recency ratio=0.50
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.036, Q3_mid=+0.188, Q4=+0.130, Q5_high_vol=+0.228

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0810, Sharpe=-0.9675)
- Yearly ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172
- IC CV=0.33, Neg years=0/7, Half ratio=0.99, Recency ratio=0.89
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.128, Q3_mid=+0.198, Q4=+0.162, Q5_high_vol=+0.330

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0773, Sharpe=-0.5905)
- Yearly ICs: 2015: +0.226 | 2016: +0.126 | 2017: +0.115 | 2018: +0.252 | 2019: +0.091 | 2020: +0.122 | 2021: +0.168
- IC CV=0.36, Neg years=0/7, Half ratio=0.83, Recency ratio=0.82
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.049, Q3_mid=+0.185, Q4=+0.175, Q5_high_vol=+0.269

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0735, Sharpe=-0.9279)
- Yearly ICs: 2015: +0.336 | 2016: +0.119 | 2017: +0.177 | 2018: +0.206 | 2019: +0.122 | 2020: +0.138 | 2021: +0.144
- IC CV=0.40, Neg years=0/7, Half ratio=0.76, Recency ratio=0.62
- Weak component: `late_bar_momentum` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.090, Q3_mid=+0.187, Q4=+0.149, Q5_high_vol=+0.317

**`combo_tri_max__max_up_ret__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0734, Sharpe=-0.3144)
- Yearly ICs: 2015: +0.221 | 2016: +0.099 | 2017: +0.169 | 2018: +0.196 | 2019: +0.060 | 2020: +0.135 | 2021: +0.066
- IC CV=0.43, Neg years=0/7, Half ratio=0.66, Recency ratio=0.63
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.170, Q2=-0.008, Q3_mid=+0.152, Q4=+0.172, Q5_high_vol=+0.249

**`combo_rank_max__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0688, Sharpe=-0.7434)
- Yearly ICs: 2015: +0.196 | 2016: +0.128 | 2017: +0.152 | 2018: +0.246 | 2019: +0.136 | 2020: +0.094 | 2021: +0.088
- IC CV=0.35, Neg years=0/7, Half ratio=0.76, Recency ratio=0.56
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.004, Q3_mid=+0.145, Q4=+0.143, Q5_high_vol=+0.229

**`combo_z_sum__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0543, Sharpe=-0.8437)
- Yearly ICs: 2015: +0.168 | 2016: +0.025 | 2017: +0.136 | 2018: +0.189 | 2019: +0.135 | 2020: +0.075 | 2021: +0.132
- IC CV=0.42, Neg years=0/7, Half ratio=1.10, Recency ratio=1.07
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.144, Q2=-0.004, Q3_mid=+0.128, Q4=+0.154, Q5_high_vol=+0.170

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0538, Sharpe=-0.3729)
- Yearly ICs: 2015: +0.227 | 2016: +0.131 | 2017: +0.079 | 2018: +0.166 | 2019: +0.094 | 2020: +0.138 | 2021: +0.079
- IC CV=0.38, Neg years=0/7, Half ratio=0.88, Recency ratio=0.60
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.050, Q3_mid=+0.169, Q4=+0.111, Q5_high_vol=+0.225

**`combo_z_sum__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0517, Sharpe=-0.2664)
- Yearly ICs: 2015: +0.201 | 2016: +0.041 | 2017: +0.149 | 2018: +0.172 | 2019: +0.128 | 2020: +0.093 | 2021: +0.144
- IC CV=0.37, Neg years=0/7, Half ratio=0.90, Recency ratio=0.98
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.013, Q3_mid=+0.165, Q4=+0.168, Q5_high_vol=+0.205

**`combo_rel_diff__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0337, Sharpe=-0.3776)
- Yearly ICs: 2015: +0.147 | 2016: +0.182 | 2017: +0.070 | 2018: +0.112 | 2019: -0.046 | 2020: +0.127 | 2021: -0.041
- IC CV=1.06, Neg years=2/7, Half ratio=0.21, Recency ratio=0.26
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.115, Q3_mid=+0.075, Q4=+0.039, Q5_high_vol=+0.179

**`combo_diff__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0267, Sharpe=-0.7948)
- Yearly ICs: 2015: +0.111 | 2016: +0.195 | 2017: +0.032 | 2018: +0.081 | 2019: -0.087 | 2020: +0.110 | 2021: -0.065
- IC CV=1.74, Neg years=2/7, Half ratio=0.05, Recency ratio=0.15
- Weak component: `early_order_flow_imbalance` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.079, Q3_mid=+0.022, Q4=+0.022, Q5_high_vol=+0.192

### 159915ETF — `single` Median Features

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1131, Sharpe=-0.2609)
- Yearly ICs: 2015: +0.212 | 2016: +0.104 | 2017: +0.015 | 2018: +0.106 | 2019: +0.150 | 2020: +0.155 | 2021: +0.111
- IC CV=0.46, Neg years=0/7, Half ratio=1.12, Recency ratio=0.84
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.073, Q3_mid=+0.159, Q4=+0.206, Q5_high_vol=+0.159

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.0844, Sharpe=-0.3459)
- Yearly ICs: 2015: +0.178 | 2016: +0.141 | 2017: +0.038 | 2018: +0.099 | 2019: +0.184 | 2020: +0.122 | 2021: +0.175
- IC CV=0.37, Neg years=0/7, Half ratio=1.37, Recency ratio=0.93
- Weak component: `max_up_ret` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.083, Q3_mid=+0.204, Q4=+0.111, Q5_high_vol=+0.194

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0384, Sharpe=+0.7043)
- Yearly ICs: 2015: +0.267 | 2016: +0.102 | 2017: -0.073 | 2018: +0.149 | 2019: +0.095 | 2020: +0.068 | 2021: +0.142
- IC CV=0.88, Neg years=1/7, Half ratio=0.76, Recency ratio=0.57
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)

**`combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0658, Sharpe=+0.3638)
- Yearly ICs: 2015: +0.198 | 2016: +0.071 | 2017: -0.030 | 2018: +0.186 | 2019: +0.144 | 2020: +0.034 | 2021: +0.134
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

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1083, Sharpe=+1.1127)
- Yearly ICs: 2015: +0.289 | 2016: +0.074 | 2017: +0.196 | 2018: +0.155 | 2019: +0.174 | 2020: +0.112 | 2021: +0.096
- IC CV=0.43, Neg years=0/7, Half ratio=0.71, Recency ratio=0.57
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1139, Sharpe=+1.0377)
- Yearly ICs: 2015: +0.268 | 2016: +0.119 | 2017: +0.110 | 2018: +0.189 | 2019: +0.088 | 2020: +0.115 | 2021: +0.140
- IC CV=0.39, Neg years=0/7, Half ratio=0.73, Recency ratio=0.66
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)

**`combo_ratio__max_down_ret__early_order_flow_imbalance`** (Lock IC=+0.1357, Sharpe=+1.0168)
- Yearly ICs: 2015: +0.256 | 2016: +0.069 | 2017: +0.233 | 2018: +0.129 | 2019: +0.074 | 2020: +0.091 | 2021: -0.081
- IC CV=0.95, Neg years=1/7, Half ratio=0.34, Recency ratio=0.03
- Weak component: `early_order_flow_imbalance` (CV=0.73)

**`combo_rank_min__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.1238, Sharpe=+1.0093)
- Yearly ICs: 2015: +0.266 | 2016: +0.030 | 2017: +0.182 | 2018: +0.123 | 2019: +0.167 | 2020: +0.085 | 2021: +0.075
- IC CV=0.55, Neg years=0/7, Half ratio=0.73, Recency ratio=0.54
- Weak component: `limit_down_proximity_early` (CV=1.03)

**`combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1158, Sharpe=+0.9651)
- Yearly ICs: 2015: +0.207 | 2016: +0.066 | 2017: +0.218 | 2018: +0.111 | 2019: +0.097 | 2020: +0.113 | 2021: +0.104
- IC CV=0.41, Neg years=0/7, Half ratio=0.71, Recency ratio=0.80
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1015, Sharpe=+0.8294)
- Yearly ICs: 2015: +0.313 | 2016: +0.094 | 2017: +0.215 | 2018: +0.203 | 2019: +0.178 | 2020: +0.143 | 2021: +0.099
- IC CV=0.40, Neg years=0/7, Half ratio=0.69, Recency ratio=0.59
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1703, Sharpe=+0.7632)
- Yearly ICs: 2015: +0.187 | 2016: +0.049 | 2017: +0.197 | 2018: +0.137 | 2019: +0.171 | 2020: +0.117 | 2021: +0.085
- IC CV=0.38, Neg years=0/7, Half ratio=0.85, Recency ratio=0.85
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1256, Sharpe=+0.7571)
- Yearly ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.194 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148
- IC CV=0.42, Neg years=0/7, Half ratio=1.09, Recency ratio=1.10
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early`** (Lock IC=+0.1320, Sharpe=+0.7508)
- Yearly ICs: 2015: +0.217 | 2016: +0.059 | 2017: +0.233 | 2018: +0.094 | 2019: +0.128 | 2020: +0.129 | 2021: +0.103
- IC CV=0.43, Neg years=0/7, Half ratio=0.77, Recency ratio=0.84
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1135, Sharpe=+0.6871)
- Yearly ICs: 2015: +0.292 | 2016: +0.072 | 2017: +0.122 | 2018: +0.214 | 2019: +0.183 | 2020: +0.187 | 2021: +0.129
- IC CV=0.39, Neg years=0/7, Half ratio=0.95, Recency ratio=0.87
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1100, Sharpe=+0.5932)
- Yearly ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052
- IC CV=0.52, Neg years=0/7, Half ratio=0.67, Recency ratio=0.56
- Weak component: `max_down_ret` (CV=0.55)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1261, Sharpe=+0.5742)
- Yearly ICs: 2015: +0.245 | 2016: +0.138 | 2017: +0.226 | 2018: +0.116 | 2019: +0.121 | 2020: +0.123 | 2021: +0.067
- IC CV=0.40, Neg years=0/7, Half ratio=0.47, Recency ratio=0.49

**`combo_mean__bar_ret_0__max_down_ret`** (Lock IC=+0.1025, Sharpe=+0.4799)
- Yearly ICs: 2015: +0.227 | 2016: +0.106 | 2017: +0.224 | 2018: +0.210 | 2019: +0.137 | 2020: +0.111 | 2021: +0.088
- IC CV=0.36, Neg years=0/7, Half ratio=0.81, Recency ratio=0.60
- Weak component: `max_down_ret` (CV=0.55)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.1145, Sharpe=+0.4686)
- Yearly ICs: 2015: +0.312 | 2016: +0.146 | 2017: +0.181 | 2018: +0.188 | 2019: +0.144 | 2020: +0.164 | 2021: +0.068
- IC CV=0.40, Neg years=0/7, Half ratio=0.65, Recency ratio=0.51
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1504, Sharpe=+0.3043)
- Yearly ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089
- IC CV=0.38, Neg years=0/7, Half ratio=0.79, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_mean__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1219, Sharpe=+0.2731)
- Yearly ICs: 2015: +0.271 | 2016: +0.087 | 2017: +0.202 | 2018: +0.108 | 2019: +0.105 | 2020: +0.125 | 2021: +0.059
- IC CV=0.50, Neg years=0/7, Half ratio=0.52, Recency ratio=0.51
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rel_diff__max_up_ret__early_body_momentum`** (Lock IC=+0.0027, Sharpe=+0.2656)
- Yearly ICs: 2015: +0.135 | 2016: +0.110 | 2017: +0.004 | 2018: +0.085 | 2019: +0.051 | 2020: +0.023 | 2021: +0.065
- IC CV=0.64, Neg years=0/7, Half ratio=0.54, Recency ratio=0.36
- Weak component: `early_body_momentum` (CV=0.39)

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1114, Sharpe=+0.2420)
- Yearly ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.232 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.072
- IC CV=0.60, Neg years=0/7, Half ratio=0.58, Recency ratio=0.53
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0925, Sharpe=+0.2109)
- Yearly ICs: 2015: +0.243 | 2016: +0.120 | 2017: +0.214 | 2018: +0.212 | 2019: +0.088 | 2020: +0.115 | 2021: +0.074
- IC CV=0.42, Neg years=0/7, Half ratio=0.56, Recency ratio=0.52
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)

**`combo_clamp_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1258, Sharpe=+0.2051)
- Yearly ICs: 2015: +0.285 | 2016: +0.070 | 2017: +0.246 | 2018: +0.192 | 2019: +0.135 | 2020: +0.158 | 2021: +0.086
- IC CV=0.44, Neg years=0/7, Half ratio=0.67, Recency ratio=0.69
- Weak component: `demark_setup_reversal_early` (CV=0.66)

**`combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.1241, Sharpe=+0.1894)
- Yearly ICs: 2015: +0.246 | 2016: +0.093 | 2017: +0.197 | 2018: +0.106 | 2019: +0.124 | 2020: +0.110 | 2021: +0.040
- IC CV=0.49, Neg years=0/7, Half ratio=0.45, Recency ratio=0.44
- Weak component: `limit_down_proximity_early` (CV=1.03)

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1270, Sharpe=+0.1877)
- Yearly ICs: 2015: +0.268 | 2016: +0.107 | 2017: +0.248 | 2018: +0.122 | 2019: +0.122 | 2020: +0.132 | 2021: +0.044
- IC CV=0.50, Neg years=0/7, Half ratio=0.46, Recency ratio=0.47
- Weak component: `demark_setup_reversal_early` (CV=0.66)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0842, Sharpe=+0.1731)
- Yearly ICs: 2015: +0.303 | 2016: +0.124 | 2017: +0.192 | 2018: +0.197 | 2019: +0.140 | 2020: +0.173 | 2021: +0.106
- IC CV=0.34, Neg years=0/7, Half ratio=0.68, Recency ratio=0.65
- Weak component: `first_bar_sentiment` (CV=0.44)

**`combo_max__first_bar_sentiment__limit_down_proximity_early`** (Lock IC=+0.0718, Sharpe=+0.1293)
- Yearly ICs: 2015: +0.245 | 2016: +0.065 | 2017: +0.078 | 2018: +0.162 | 2019: +0.140 | 2020: +0.096 | 2021: +0.075
- IC CV=0.49, Neg years=0/7, Half ratio=0.80, Recency ratio=0.55
- Weak component: `limit_down_proximity_early` (CV=1.03)

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range`** (Lock IC=+0.1138, Sharpe=+0.1133)
- Yearly ICs: 2015: +0.286 | 2016: +0.130 | 2017: +0.219 | 2018: +0.208 | 2019: +0.106 | 2020: +0.163 | 2021: +0.098
- IC CV=0.37, Neg years=0/7, Half ratio=0.61, Recency ratio=0.63
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1053, Sharpe=+0.0931)
- Yearly ICs: 2015: +0.228 | 2016: +0.113 | 2017: +0.202 | 2018: +0.196 | 2019: +0.109 | 2020: +0.127 | 2021: +0.063
- IC CV=0.38, Neg years=0/7, Half ratio=0.62, Recency ratio=0.56
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1001, Sharpe=+0.0682)
- Yearly ICs: 2015: +0.270 | 2016: +0.153 | 2017: +0.085 | 2018: +0.126 | 2019: +0.079 | 2020: +0.129 | 2021: +0.109
- IC CV=0.44, Neg years=0/7, Half ratio=0.69, Recency ratio=0.56
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0936, Sharpe=+0.0308)
- Yearly ICs: 2015: +0.243 | 2016: +0.124 | 2017: +0.217 | 2018: +0.233 | 2019: +0.089 | 2020: +0.114 | 2021: +0.081
- IC CV=0.42, Neg years=0/7, Half ratio=0.58, Recency ratio=0.53
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)

**`combo_rank_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0714, Sharpe=+0.0284)
- Yearly ICs: 2015: +0.226 | 2016: +0.111 | 2017: +0.152 | 2018: +0.216 | 2019: +0.068 | 2020: +0.134 | 2021: +0.060
- IC CV=0.44, Neg years=0/7, Half ratio=0.65, Recency ratio=0.58
- Weak component: `early_body_momentum` (CV=0.39)

**`combo_rank_min__opening_auction_imbalance__max_down_ret`** (Lock IC=+0.1021, Sharpe=+0.0072)
- Yearly ICs: 2015: +0.266 | 2016: +0.073 | 2017: +0.207 | 2018: +0.134 | 2019: +0.085 | 2020: +0.145 | 2021: +0.068
- IC CV=0.49, Neg years=0/7, Half ratio=0.81, Recency ratio=0.63
- Weak component: `max_down_ret` (CV=0.55)

**`combo_z_sum__opening_auction_imbalance__close_vs_open_range`** (Lock IC=+0.0872, Sharpe=+0.0060)
- Yearly ICs: 2015: +0.169 | 2016: +0.063 | 2017: +0.180 | 2018: +0.138 | 2019: +0.072 | 2020: +0.113 | 2021: +0.077
- IC CV=0.38, Neg years=0/7, Half ratio=0.74, Recency ratio=0.82
- Weak component: `close_vs_open_range` (CV=0.48)

### 159915ETF — `single` True Positives

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1147, Sharpe=+1.4841)
- Yearly ICs: 2015: +0.254 | 2016: +0.171 | 2017: -0.008 | 2018: +0.180 | 2019: +0.206 | 2020: +0.202 | 2021: +0.114
- IC CV=0.50, Neg years=1/7, Half ratio=1.09, Recency ratio=0.74
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_z_sum__first_bar_sentiment__limit_down_proximity_early`** (Lock IC=+0.1182, Sharpe=+1.3926)
- Yearly ICs: 2015: +0.238 | 2016: +0.049 | 2017: -0.027 | 2018: +0.121 | 2019: +0.229 | 2020: +0.140 | 2021: +0.103
- IC CV=0.71, Neg years=1/7, Half ratio=1.56, Recency ratio=0.85
- Weak component: `limit_down_proximity_early` (CV=1.21)

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1318, Sharpe=+1.2965)
- Yearly ICs: 2015: +0.228 | 2016: +0.122 | 2017: +0.009 | 2018: +0.185 | 2019: +0.198 | 2020: +0.148 | 2021: +0.176
- IC CV=0.44, Neg years=0/7, Half ratio=1.16, Recency ratio=0.93
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1327, Sharpe=+1.1160)
- Yearly ICs: 2015: +0.239 | 2016: +0.078 | 2017: -0.023 | 2018: +0.106 | 2019: +0.259 | 2020: +0.133 | 2021: +0.110
- IC CV=0.69, Neg years=1/7, Half ratio=1.25, Recency ratio=0.76
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1424, Sharpe=+0.9282)
- Yearly ICs: 2015: +0.225 | 2016: +0.119 | 2017: -0.020 | 2018: +0.156 | 2019: +0.239 | 2020: +0.165 | 2021: +0.143
- IC CV=0.54, Neg years=1/7, Half ratio=1.24, Recency ratio=0.90
- Weak component: `bar_body_rng_0` (CV=0.51)

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1338, Sharpe=+0.6628)
- Yearly ICs: 2015: +0.190 | 2016: +0.103 | 2017: +0.023 | 2018: +0.127 | 2019: +0.160 | 2020: +0.153 | 2021: +0.167
- IC CV=0.39, Neg years=0/7, Half ratio=1.26, Recency ratio=1.09
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)

**`combo_mean__rbreaker_sell_setup_proximity_early__early_range`** (Lock IC=+0.1059, Sharpe=+0.5093)
- Yearly ICs: 2015: +0.124 | 2016: +0.107 | 2017: +0.013 | 2018: +0.143 | 2019: +0.099 | 2020: +0.159 | 2021: +0.127
- IC CV=0.40, Neg years=0/7, Half ratio=1.11, Recency ratio=1.24
- Weak component: `early_range` (CV=0.96)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1192, Sharpe=+0.4661)
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034
- IC CV=0.90, Neg years=1/7, Half ratio=0.89, Recency ratio=0.61
- Weak component: `yesterday_first_30min_return` (CV=1.04)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1297, Sharpe=+0.2566)
- Yearly ICs: 2015: +0.232 | 2016: +0.175 | 2017: -0.028 | 2018: +0.143 | 2019: +0.206 | 2020: +0.138 | 2021: +0.124
- IC CV=0.55, Neg years=1/7, Half ratio=1.22, Recency ratio=0.64
- Weak component: `first_bar_sentiment` (CV=0.70)

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0770, Sharpe=+0.0223)
- Yearly ICs: 2015: +0.191 | 2016: +0.103 | 2017: -0.003 | 2018: +0.097 | 2019: +0.170 | 2020: +0.132 | 2021: +0.146
- IC CV=0.50, Neg years=1/7, Half ratio=1.41, Recency ratio=0.95
- Weak component: `first_bar_sentiment` (CV=0.70)

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
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__first_bar_sentiment` | Median | persistent | +0.0778 | +0.1286 | +0.0055 | 2y |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | FP | gradual | +0.0563 | +0.1922 | -0.1808 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0452 | +0.1266 | -0.0301 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0377 | +0.1764 | -0.0345 | 4y |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0285 | +0.1448 | +0.0269 | ∞ |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Median | gradual | +0.0283 | +0.1374 | -0.0976 | 4y |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | FP | gradual | +0.0185 | +0.0578 | -0.0352 | 2y |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | immediate | -0.0453 | +0.0618 | -0.0376 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=5, persistent=5

**FP decay trajectories:**

- `combo_ratio__first_bar_sentiment__volume_surge_direction`: Y1:+0.019 → Y2:+0.058 → Y3:-0.051 → Y4:+0.006 → Y5:-0.035
- `combo_z_sum__max_up_ret__volume_weighted_price_position`: Y1:+0.056 → Y2:+0.192 → Y3:+0.025 → Y4:+0.114 → Y5:-0.181

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__max_up_ret__rsi_opening` | Median | persistent | +0.1538 | +0.1385 | +0.0241 | 4y |
| `combo_z_sum__max_up_ret__early_order_flow_imbalance` | Median | gradual | +0.1494 | +0.0980 | -0.1027 | 4y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1419 | +0.0909 | +0.1224 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1402 | +0.0834 | +0.1093 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | TP | persistent | +0.1290 | +0.0817 | +0.0130 | 4y |
| `combo_z_sum__bar_ret_0__early_order_flow_imbalance` | Median | gradual | +0.1212 | +0.0733 | -0.0718 | 4y |
| `combo_tri_max__max_up_ret__close_vs_open_range__early_body_momentum` | Median | gradual | +0.1209 | +0.0881 | -0.0644 | 4y |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1186 | +0.0712 | +0.1193 | ∞ |
| `combo_rank_max__close_vs_open_range__first_bar_sentiment` | Median | gradual | +0.1186 | +0.0623 | -0.0436 | 4y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1162 | +0.1552 | +0.0293 | 4y |
| `combo_rank_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1159 | +0.1133 | -0.0669 | 4y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | TP | persistent | +0.1116 | +0.0848 | +0.0697 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1053 | +0.0568 | +0.2040 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Median | gradual | +0.1051 | +0.0949 | -0.0401 | 4y |
| `combo_z_sum__opening_auction_imbalance__close_vs_open_range` | TP | gradual | +0.1015 | +0.0878 | -0.0722 | 4y |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0404 | 1y |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Median | gradual | +0.0964 | +0.0699 | -0.0186 | 4y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | persistent | +0.0942 | +0.0937 | +0.0717 | 3y |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.0925 | +0.1270 | +0.0521 | ∞ |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.0922 | +0.1106 | +0.1416 | ∞ |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0921 | +0.0793 | +0.1842 | ∞ |
| `combo_z_sum__opening_auction_imbalance__max_down_ret` | Median | gradual | +0.0916 | +0.0763 | -0.0107 | 4y |
| `combo_tri_min__max_up_ret__close_vs_open_range__first_bar_sentiment` | Median | gradual | +0.0849 | +0.0723 | -0.0243 | 4y |
| `combo_rank_min__opening_auction_imbalance__max_down_ret` | TP | persistent | +0.0842 | +0.0650 | +0.0064 | 4y |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0824 | +0.0767 | +0.0885 | ∞ |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Median | gradual | +0.0801 | +0.0817 | -0.0571 | 4y |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | Median | persistent | +0.0786 | +0.0512 | +0.0133 | 4y |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0785 | +0.0606 | +0.1007 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.0773 | +0.0593 | +0.1847 | ∞ |
| `combo_max__first_bar_sentiment__limit_down_proximity_early` | TP | persistent | +0.0764 | +0.0314 | +0.1051 | 1y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0756 | +0.0530 | +0.0807 | ∞ |
| `combo_mean__bar_ret_0__max_down_ret` | TP | persistent | +0.0721 | +0.0548 | +0.0105 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0667 | +0.0659 | +0.1729 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0626 | +0.0952 | +0.1864 | ∞ |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Median | persistent | +0.0618 | +0.0635 | +0.0293 | 4y |
| `combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early` | TP | persistent | +0.0610 | +0.0716 | +0.0904 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0600 | +0.0723 | +0.0459 | ∞ |
| `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0526 | +0.0908 | +0.0529 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Median | persistent | +0.0494 | +0.0815 | +0.1020 | ∞ |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Median | persistent | +0.0493 | +0.0677 | +0.0072 | 4y |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0472 | +0.0604 | +0.1725 | ∞ |
| `combo_min__close_vs_open_range__bar_ret_0` | Median | persistent | +0.0446 | +0.0704 | +0.0151 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0396 | +0.0773 | +0.0847 | ∞ |
| `combo_rel_diff__max_up_ret__early_body_momentum` | TP | persistent | +0.0342 | +0.0018 | +0.0962 | 1y |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0279 | +0.0649 | +0.0855 | ∞ |
| `combo_rank_min__bar_ret_0__limit_down_proximity_early` | TP | persistent | +0.0063 | +0.0355 | +0.0769 | ∞ |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | TP | immediate | -0.0146 | +0.0148 | +0.0983 | ∞ |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | Median | immediate | -0.0345 | -0.0366 | +0.1313 | ∞ |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | Median | immediate | -0.0560 | +0.0066 | +0.1091 | ∞ |
| `combo_diff__max_up_ret__early_order_flow_imbalance` | Median | immediate | -0.0796 | -0.0390 | +0.1297 | ∞ |

**Decay distribution**: immediate=4, fast(1-2y)=0, gradual=11, persistent=36

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1776 | +0.1159 | +0.1263 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1573 | +0.1397 | +0.0771 | 4y |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_range` | TP | persistent | +0.1425 | +0.1116 | +0.0766 | 2y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Median | persistent | +0.1423 | +0.0972 | +0.1589 | 3y |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | TP | persistent | +0.1316 | +0.1618 | +0.0271 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1299 | +0.1363 | +0.1021 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | TP | gradual | +0.1233 | +0.1529 | -0.0404 | 2y |
| `combo_max__max_up_ret__first_bar_return` | Median | gradual | +0.1102 | +0.1603 | -0.0743 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0961 | +0.1503 | +0.1128 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0899 | +0.1369 | +0.0817 | ∞ |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | TP | persistent | +0.0864 | +0.0552 | +0.1287 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0799 | +0.1128 | +0.0949 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0733 | +0.1517 | +0.1033 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=2, persistent=11

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.743±0.003 | 0.690±0.035 | 0% | USEFUL |
| ic_ir | 0.648±0.018 | 0.572±0.048 | 0% | USEFUL |
| p_value | 0.006±0.006 | 0.000±0.000 | 4% | USEFUL |
| max_corr | 0.352±0.288 | 0.684±0.148 | 25% | USEFUL |
| deflated_ic | 0.169±0.042 | 0.237±0.038 | 11% | USEFUL |
| overall_ic | 0.170±0.042 | 0.237±0.038 | 12% | USEFUL |
| raw_ic | 0.079±0.009 | 0.086±0.041 | 18% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 3/20 top rejects are profitable (15%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.2340, Lock IC=+0.0054, Sharpe=+0.1767

**B2 Rolling Guard**: 3/20 top rejects are profitable (15%)

- `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1637, Lock IC=+0.0306, Sharpe=+0.2008
- `combo_min__bar_ret_0__volume_surge_direction`: Train IC=+0.1563, Lock IC=+0.0151, Sharpe=+0.0150
- `combo_min__first_bar_return__volume_surge_direction`: Train IC=+0.1562, Lock IC=+0.0151, Sharpe=+0.0150

**B3 Composite Floor**: 6/20 top rejects are profitable (30%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.2367, Lock IC=+0.0411, Sharpe=+0.2081
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.2367, Lock IC=+0.0411, Sharpe=+0.2081
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0345, Sharpe=+0.0673

**B4 Correlation Gate**: 9/16 top rejects are profitable (56%)

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2690, Lock IC=+0.0342, Sharpe=+0.8997
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2687, Lock IC=+0.0505, Sharpe=+0.2804
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.2055, Lock IC=+0.0608, Sharpe=+0.2200

### 500ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_rel_diff__yesterday_afternoon_momentum__limit_down_proximity_early`: Train IC=+0.2609, Lock IC=+0.1167, Sharpe=+1.3583
- `combo_rel_diff__yesterday_afternoon_momentum__rbreaker_buy_setup_proximity_early`: Train IC=+0.2609, Lock IC=+0.1167, Sharpe=+1.3583
- `combo_min__opening_auction_imbalance__limit_down_proximity_early`: Train IC=+0.2355, Lock IC=+0.1258, Sharpe=+0.7275

**B2 Rolling Guard**: 12/20 top rejects are profitable (60%)

- `combo_rank_min__early_body_momentum__limit_down_proximity_early`: Train IC=+0.2147, Lock IC=+0.1243, Sharpe=+0.8249
- `combo_rank_min__early_body_momentum__rbreaker_buy_setup_proximity_early`: Train IC=+0.2147, Lock IC=+0.1243, Sharpe=+0.8249
- `combo_rank_min__opening_momentum_score__limit_down_proximity_early`: Train IC=+0.2147, Lock IC=+0.1243, Sharpe=+0.8249

**BH-FDR Gate**: 4/20 top rejects are profitable (20%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__late_bar_momentum__early_body_momentum`: Train IC=+0.0919, Lock IC=+0.0576, Sharpe=+0.6556
- `vol_ratio_10_60`: Train IC=+0.0927, Lock IC=+0.0309, Sharpe=+0.3757
- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.2780

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__close_vs_open_range__rsi_opening`: Train IC=+0.2850, Lock IC=+0.1081, Sharpe=+0.9961
- `combo_tri_min__rbreaker_sell_setup_proximity_early__close_vs_open_range__high_low_sequence_momentum`: Train IC=+0.2850, Lock IC=+0.1081, Sharpe=+0.9961
- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2827, Lock IC=+0.1174, Sharpe=+0.8869

**B4 Correlation Gate**: 16/20 top rejects are profitable (80%)

- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.1127
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2914, Lock IC=+0.1158, Sharpe=+0.9651
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3072, Lock IC=+0.1015, Sharpe=+0.8294

### 159915ETF — `single`

**7-Year Jackknife**: 17/20 top rejects are profitable (85%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__early_range`: Train IC=+0.2105, Lock IC=+0.1395, Sharpe=+1.6071
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2242, Lock IC=+0.1531, Sharpe=+1.3653
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2242, Lock IC=+0.1531, Sharpe=+1.3653

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+0.8573
- `combo_z_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+0.8573
- `combo_min__star50_limit_proximity_early__early_range`: Train IC=+0.1909, Lock IC=+0.1232, Sharpe=+0.8131

**BH-FDR Gate**: 3/5 top rejects are profitable (60%)

- `close_vs_open_range`: Train IC=+0.0863, Lock IC=+0.0988, Sharpe=+0.4620
- `combo_rank_min__lunch_transition_volume_skew__early_range`: Train IC=+0.1011, Lock IC=+0.0686, Sharpe=+0.0615
- `combo_rank_max__yesterday_first_30min_return__yesterday_afternoon_reversal`: Train IC=+0.0350, Lock IC=+0.0387, Sharpe=+0.0512

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.5392
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.5392
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0`: Train IC=+0.2767, Lock IC=+0.1374, Sharpe=+1.5099

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2895, Lock IC=+0.1279, Sharpe=+1.5377
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Sharpe=+1.5377
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_ret_0`: Train IC=+0.2693, Lock IC=+0.1274, Sharpe=+1.4562

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_std_across_regimes`: FP is lower (d=-4.40). Threshold 0.102 → 57% accuracy.
- `n_negative_regimes`: FP is lower (d=-1.12). Threshold 2.500 → 57% accuracy.
- `ic_cv`: FP is lower (d=-0.73). Threshold 3.252 → 57% accuracy.
- `n_negative_years`: FP is lower (d=-0.71). Threshold 2.500 → 57% accuracy.
- `weak_link_cv`: FP is lower (d=-0.58). Threshold 1.256 → 71% accuracy.
- `recency_ratio`: FP is higher (d=+0.56). Threshold 0.884 → 71% accuracy.

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
| `max_up_ret` | 1 | 14 | 15 | 7% |  |
| `star50_limit_proximity_early` | 0 | 13 | 13 | 0% |  |
| `close_vs_open_range` | 0 | 6 | 6 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 17 | 17 | 0% |  |
| `bar_ret_0` | 0 | 9 | 9 | 0% |  |
| `max_down_ret` | 0 | 6 | 6 | 0% |  |
| `demark_setup_reversal_early` | 0 | 3 | 3 | 0% |  |
| `early_body_momentum` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 4 | 4 | 0% |  |
| `bar_body_rng_0` | 0 | 3 | 3 | 0% |  |
| `opening_auction_imbalance` | 0 | 4 | 4 | 0% |  |
| `limit_down_proximity_early` | 0 | 5 | 5 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=24, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=7, FP rate=12%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=6, FP rate=0%

