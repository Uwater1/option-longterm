# Filter Pipeline Deep Diagnosis

**Purpose**: Understand WHY admission gates fail, using only training-period signals.
Lockbox is used solely for labeling TP/FP — all proposed fixes are training-only.

---

## 1. FP/TP Summary

| ETF | Side | Admitted | FP | TP | FP Rate |
| :--- | :--- | ---: | ---: | ---: | ---: |
| 300ETF | single | 10 | 5 | 5 | 50% |
| 500ETF | single | 48 | 21 | 27 | 44% |
| 159915ETF | single | 11 | 4 | 7 | 36% |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=5, TP=5)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_std_across_regimes | 0.065 | 0.090 | 0.057 | 0.090 | -1.52 | 0.045 | 40% |
| n_negative_regimes | 0.400 | 1.400 | 0.000 | 1.000 | -1.25 | 0.000 | 40% |
| n_negative_years | 0.600 | 1.600 | 1.000 | 1.000 | -1.09 | 0.000 | 40% |
| ic_cv | 0.794 | 1.787 | 0.746 | 0.880 | -0.73 | 1.012 | 50% |
| weak_link_cv | 1.149 | 1.252 | 1.141 | 1.141 | -0.69 | 1.256 | 56% |
| recency_ratio | 0.605 | 0.549 | 0.500 | 0.626 | +0.15 | 0.096 | 60% |
| half_ratio | 0.877 | 0.888 | 0.826 | 1.025 | -0.02 | 0.168 | 60% |

### 500ETF — `single` (FP=21, TP=27)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| half_ratio | 0.734 | 0.659 | 0.793 | 0.667 | +0.35 | 0.789 | 71% |
| n_negative_years | 0.190 | 0.037 | 0.000 | 0.000 | +0.35 | 1.500 | 60% |
| n_negative_regimes | 0.381 | 0.222 | 0.000 | 0.000 | +0.35 | 0.500 | 60% |
| recency_ratio | 0.648 | 0.582 | 0.643 | 0.564 | +0.32 | 0.579 | 65% |
| weak_link_cv | 0.561 | 0.596 | 0.547 | 0.616 | -0.23 | 0.693 | 59% |
| ic_cv | 0.505 | 0.466 | 0.414 | 0.434 | +0.16 | 1.005 | 60% |
| ic_std_across_regimes | 0.068 | 0.068 | 0.067 | 0.070 | -0.05 | 0.077 | 58% |

### 159915ETF — `single` (FP=4, TP=7)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_std_across_regimes | 0.057 | 0.072 | 0.056 | 0.074 | -2.15 | 0.080 | 55% |
| n_negative_years | 0.000 | 0.429 | 0.000 | 0.000 | -1.22 | 1.000 | 55% |
| ic_cv | 0.462 | 0.553 | 0.455 | 0.537 | -0.77 | 0.413 | 55% |
| n_negative_regimes | 0.000 | 0.143 | 0.000 | 0.000 | -0.58 | 0.500 | 55% |
| half_ratio | 1.252 | 1.204 | 1.288 | 1.241 | +0.36 | 1.270 | 73% |
| weak_link_cv | 0.713 | 0.724 | 0.702 | 0.768 | -0.07 | 0.603 | 64% |
| recency_ratio | 0.946 | 0.955 | 0.947 | 0.957 | -0.06 | 1.009 | 64% |

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

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0280, Sharpe=-0.3103)
- Yearly ICs: 2015: +0.254 | 2016: +0.095 | 2017: +0.008 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132
- IC CV=0.65, Neg years=0/7, Half ratio=0.81, Recency ratio=0.50
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14, neg years=1)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.027, Q3_mid=+0.113, Q4=+0.191, Q5_high_vol=+0.227

**`combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment`** (Lock IC=+0.0353, Sharpe=-0.1685)
- Yearly ICs: 2015: +0.168 | 2016: +0.099 | 2017: +0.056 | 2018: +0.198 | 2019: +0.087 | 2020: +0.003 | 2021: +0.132
- IC CV=0.58, Neg years=0/7, Half ratio=0.83, Recency ratio=0.50
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14, neg years=1)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.053, Q3_mid=+0.106, Q4=+0.124, Q5_high_vol=+0.185

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0616, Sharpe=-0.0803)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095
- IC CV=1.14, Neg years=1/7, Half ratio=0.62, Recency ratio=0.50
- Regime ICs: Q1_low_vol=-0.067, Q2=+0.000, Q3_mid=+0.053, Q4=+0.178, Q5_high_vol=+0.171

### 500ETF — `single` False Positives

**`combo_z_sum__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0543, Sharpe=-0.8437)
- Yearly ICs: 2015: +0.168 | 2016: +0.025 | 2017: +0.136 | 2018: +0.189 | 2019: +0.135 | 2020: +0.075 | 2021: +0.132
- IC CV=0.42, Neg years=0/7, Half ratio=1.10, Recency ratio=1.07
- Weak component: `early_order_flow_imbalance` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.144, Q2=-0.004, Q3_mid=+0.128, Q4=+0.154, Q5_high_vol=+0.170

**`combo_diff__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0267, Sharpe=-0.7948)
- Yearly ICs: 2015: +0.111 | 2016: +0.195 | 2017: +0.032 | 2018: +0.081 | 2019: -0.087 | 2020: +0.110 | 2021: -0.065
- IC CV=1.74, Neg years=2/7, Half ratio=0.05, Recency ratio=0.15
- Weak component: `early_order_flow_imbalance` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.079, Q3_mid=+0.022, Q4=+0.022, Q5_high_vol=+0.192

**`combo_rank_min__close_vs_open_range__early_order_flow_imbalance`** (Lock IC=+0.0527, Sharpe=-0.6880)
- Yearly ICs: 2015: +0.108 | 2016: +0.032 | 2017: +0.160 | 2018: +0.114 | 2019: +0.101 | 2020: +0.050 | 2021: +0.105
- IC CV=0.41, Neg years=0/7, Half ratio=0.98, Recency ratio=1.11
- Weak component: `early_order_flow_imbalance` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.159, Q2=-0.025, Q3_mid=+0.127, Q4=+0.126, Q5_high_vol=+0.092

**`combo_sig_product__max_up_ret__rsi_opening`** (Lock IC=+0.0927, Sharpe=-0.5972)
- Yearly ICs: 2015: +0.212 | 2016: +0.114 | 2017: +0.088 | 2018: +0.148 | 2019: +0.071 | 2020: +0.140 | 2021: +0.093
- IC CV=0.36, Neg years=0/7, Half ratio=0.81, Recency ratio=0.71
- Weak component: `rsi_opening` (CV=0.50, neg years=0)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.055, Q3_mid=+0.126, Q4=+0.167, Q5_high_vol=+0.211

**`combo_rank_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.1003, Sharpe=-0.5172)
- Yearly ICs: 2015: +0.286 | 2016: +0.089 | 2017: +0.190 | 2018: +0.136 | 2019: +0.148 | 2020: +0.136 | 2021: +0.087
- IC CV=0.41, Neg years=0/7, Half ratio=0.86, Recency ratio=0.59
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.026, Q3_mid=+0.136, Q4=+0.104, Q5_high_vol=+0.248

**`combo_clamp_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0782, Sharpe=-0.5067)
- Yearly ICs: 2015: +0.309 | 2016: +0.109 | 2017: +0.187 | 2018: +0.217 | 2019: +0.121 | 2020: +0.145 | 2021: +0.149
- IC CV=0.36, Neg years=0/7, Half ratio=0.79, Recency ratio=0.70
- Weak component: `late_bar_momentum` (CV=0.56, neg years=0)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.093, Q3_mid=+0.195, Q4=+0.147, Q5_high_vol=+0.318

**`combo_z_sum__opening_auction_imbalance__max_down_ret`** (Lock IC=+0.0977, Sharpe=-0.3952)
- Yearly ICs: 2015: +0.230 | 2016: +0.074 | 2017: +0.188 | 2018: +0.155 | 2019: +0.099 | 2020: +0.118 | 2021: +0.078
- IC CV=0.41, Neg years=0/7, Half ratio=0.80, Recency ratio=0.64
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.014, Q3_mid=+0.152, Q4=+0.112, Q5_high_vol=+0.211

**`combo_rel_diff__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0337, Sharpe=-0.3776)
- Yearly ICs: 2015: +0.147 | 2016: +0.182 | 2017: +0.070 | 2018: +0.112 | 2019: -0.046 | 2020: +0.127 | 2021: -0.041
- IC CV=1.06, Neg years=2/7, Half ratio=0.21, Recency ratio=0.26
- Weak component: `early_order_flow_imbalance` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.115, Q3_mid=+0.075, Q4=+0.039, Q5_high_vol=+0.179

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0538, Sharpe=-0.3729)
- Yearly ICs: 2015: +0.227 | 2016: +0.131 | 2017: +0.079 | 2018: +0.166 | 2019: +0.094 | 2020: +0.138 | 2021: +0.079
- IC CV=0.38, Neg years=0/7, Half ratio=0.88, Recency ratio=0.60
- Weak component: `first_bar_sentiment` (CV=0.44, neg years=0)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.050, Q3_mid=+0.169, Q4=+0.111, Q5_high_vol=+0.225

**`combo_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0888, Sharpe=-0.3507)
- Yearly ICs: 2015: +0.295 | 2016: +0.105 | 2017: +0.190 | 2018: +0.167 | 2019: +0.129 | 2020: +0.102 | 2021: +0.096
- IC CV=0.43, Neg years=0/7, Half ratio=0.72, Recency ratio=0.49
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.008, Q3_mid=+0.161, Q4=+0.127, Q5_high_vol=+0.260

**`combo_tri_max__max_up_ret__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0734, Sharpe=-0.3144)
- Yearly ICs: 2015: +0.221 | 2016: +0.099 | 2017: +0.169 | 2018: +0.196 | 2019: +0.060 | 2020: +0.135 | 2021: +0.066
- IC CV=0.43, Neg years=0/7, Half ratio=0.66, Recency ratio=0.63
- Weak component: `close_vs_open_range` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.170, Q2=-0.008, Q3_mid=+0.152, Q4=+0.172, Q5_high_vol=+0.249

**`combo_ratio__max_down_ret__opening_auction_imbalance`** (Lock IC=+0.1213, Sharpe=-0.2902)
- Yearly ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004
- IC CV=0.47, Neg years=0/7, Half ratio=0.64, Recency ratio=0.42
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.001, Q3_mid=+0.137, Q4=+0.092, Q5_high_vol=+0.174

**`combo_z_sum__max_up_ret__early_order_flow_imbalance`** (Lock IC=+0.0517, Sharpe=-0.2664)
- Yearly ICs: 2015: +0.201 | 2016: +0.041 | 2017: +0.149 | 2018: +0.172 | 2019: +0.128 | 2020: +0.093 | 2021: +0.144
- IC CV=0.37, Neg years=0/7, Half ratio=0.90, Recency ratio=0.98
- Weak component: `early_order_flow_imbalance` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.013, Q3_mid=+0.165, Q4=+0.168, Q5_high_vol=+0.205

**`combo_z_sum__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0719, Sharpe=-0.2248)
- Yearly ICs: 2015: +0.136 | 2016: +0.062 | 2017: +0.153 | 2018: +0.106 | 2019: +0.050 | 2020: +0.094 | 2021: +0.054
- IC CV=0.40, Neg years=0/7, Half ratio=0.65, Recency ratio=0.74
- Weak component: `close_vs_open_range` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.024, Q3_mid=+0.135, Q4=+0.116, Q5_high_vol=+0.118

**`combo_rank_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0942, Sharpe=-0.1917)
- Yearly ICs: 2015: +0.196 | 2016: +0.090 | 2017: +0.179 | 2018: +0.119 | 2019: +0.066 | 2020: +0.108 | 2021: +0.119
- IC CV=0.34, Neg years=0/7, Half ratio=0.66, Recency ratio=0.79
- Weak component: `close_vs_open_range` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.032, Q3_mid=+0.153, Q4=+0.129, Q5_high_vol=+0.157

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0879, Sharpe=-0.1032)
- Yearly ICs: 2015: +0.212 | 2016: +0.116 | 2017: +0.206 | 2018: +0.042 | 2019: +0.139 | 2020: +0.111 | 2021: +0.105
- IC CV=0.42, Neg years=0/7, Half ratio=0.58, Recency ratio=0.66
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40, neg years=0)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.090, Q3_mid=+0.093, Q4=+0.140, Q5_high_vol=+0.221

**`combo_rel_diff__max_down_ret__early_vwap_acceleration`** (Lock IC=+0.0755, Sharpe=-0.0824)
- Yearly ICs: 2015: +0.222 | 2016: +0.015 | 2017: +0.131 | 2018: +0.059 | 2019: +0.122 | 2020: +0.082 | 2021: +0.144
- IC CV=0.56, Neg years=0/7, Half ratio=1.19, Recency ratio=0.95
- Weak component: `early_vwap_acceleration` (CV=0.56, neg years=0)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.090, Q3_mid=+0.119, Q4=+0.066, Q5_high_vol=+0.183

**`combo_rank_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.1037, Sharpe=-0.0814)
- Yearly ICs: 2015: +0.211 | 2016: +0.082 | 2017: +0.181 | 2018: +0.172 | 2019: +0.115 | 2020: +0.063 | 2021: +0.056
- IC CV=0.46, Neg years=0/7, Half ratio=0.63, Recency ratio=0.41
- Weak component: `close_vs_open_range` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.031, Q3_mid=+0.122, Q4=+0.142, Q5_high_vol=+0.185

**`combo_rank_max__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0939, Sharpe=-0.0706)
- Yearly ICs: 2015: +0.275 | 2016: +0.082 | 2017: +0.187 | 2018: +0.190 | 2019: +0.140 | 2020: +0.133 | 2021: +0.114
- IC CV=0.37, Neg years=0/7, Half ratio=0.85, Recency ratio=0.69
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.001, Q3_mid=+0.175, Q4=+0.138, Q5_high_vol=+0.244

**`first_bar_return`** (Lock IC=+0.0690, Sharpe=-0.0418)
- Yearly ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099
- IC CV=0.35, Neg years=0/7, Half ratio=0.81, Recency ratio=0.58
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.025, Q3_mid=+0.141, Q4=+0.143, Q5_high_vol=+0.231

**`combo_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.1022, Sharpe=-0.0410)
- Yearly ICs: 2015: +0.205 | 2016: +0.084 | 2017: +0.185 | 2018: +0.173 | 2019: +0.118 | 2020: +0.064 | 2021: +0.057
- IC CV=0.45, Neg years=0/7, Half ratio=0.64, Recency ratio=0.42
- Weak component: `close_vs_open_range` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.028, Q3_mid=+0.123, Q4=+0.138, Q5_high_vol=+0.185

### 159915ETF — `single` False Positives

**`combo_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0802, Sharpe=-0.3755)
- Yearly ICs: 2015: +0.179 | 2016: +0.073 | 2017: +0.042 | 2018: +0.065 | 2019: +0.114 | 2020: +0.116 | 2021: +0.149
- IC CV=0.43, Neg years=0/7, Half ratio=1.31, Recency ratio=1.05
- Weak component: `volume_weighted_price_position` (CV=0.71, neg years=0)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.079, Q3_mid=+0.145, Q4=+0.152, Q5_high_vol=+0.150

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1131, Sharpe=-0.2609)
- Yearly ICs: 2015: +0.212 | 2016: +0.104 | 2017: +0.015 | 2018: +0.106 | 2019: +0.150 | 2020: +0.155 | 2021: +0.111
- IC CV=0.46, Neg years=0/7, Half ratio=1.12, Recency ratio=0.84
- Weak component: `first_bar_sentiment` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.073, Q3_mid=+0.159, Q4=+0.206, Q5_high_vol=+0.159

**`combo_z_sum__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0792, Sharpe=-0.2440)
- Yearly ICs: 2015: +0.235 | 2016: +0.126 | 2017: +0.019 | 2018: +0.110 | 2019: +0.180 | 2020: +0.146 | 2021: +0.146
- IC CV=0.45, Neg years=0/7, Half ratio=1.28, Recency ratio=0.81
- Weak component: `first_bar_sentiment` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.085, Q3_mid=+0.194, Q4=+0.139, Q5_high_vol=+0.231

**`combo_rank_max__max_up_ret__opening_auction_imbalance`** (Lock IC=+0.0933, Sharpe=-0.0378)
- Yearly ICs: 2015: +0.169 | 2016: +0.082 | 2017: +0.009 | 2018: +0.060 | 2019: +0.134 | 2020: +0.114 | 2021: +0.158
- IC CV=0.51, Neg years=0/7, Half ratio=1.29, Recency ratio=1.08
- Weak component: `opening_auction_imbalance` (CV=0.75, neg years=1)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.056, Q3_mid=+0.162, Q4=+0.145, Q5_high_vol=+0.155

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

**`combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early`** (Lock IC=+0.1320, Sharpe=+0.7508)
- Yearly ICs: 2015: +0.217 | 2016: +0.059 | 2017: +0.233 | 2018: +0.094 | 2019: +0.128 | 2020: +0.129 | 2021: +0.103
- IC CV=0.43, Neg years=0/7, Half ratio=0.77, Recency ratio=0.84
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0842, Sharpe=+0.7133)
- Yearly ICs: 2015: +0.303 | 2016: +0.124 | 2017: +0.192 | 2018: +0.197 | 2019: +0.140 | 2020: +0.173 | 2021: +0.106
- IC CV=0.34, Neg years=0/7, Half ratio=0.68, Recency ratio=0.65
- Weak component: `first_bar_sentiment` (CV=0.44)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1261, Sharpe=+0.5742)
- Yearly ICs: 2015: +0.245 | 2016: +0.138 | 2017: +0.226 | 2018: +0.116 | 2019: +0.121 | 2020: +0.123 | 2021: +0.067
- IC CV=0.40, Neg years=0/7, Half ratio=0.47, Recency ratio=0.49

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

**`combo_tri_mean__max_up_ret__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0884, Sharpe=+0.2245)
- Yearly ICs: 2015: +0.252 | 2016: +0.114 | 2017: +0.194 | 2018: +0.213 | 2019: +0.111 | 2020: +0.123 | 2021: +0.107
- IC CV=0.34, Neg years=0/7, Half ratio=0.70, Recency ratio=0.63
- Weak component: `close_vs_open_range` (CV=0.48)

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

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range`** (Lock IC=+0.1138, Sharpe=+0.1133)
- Yearly ICs: 2015: +0.286 | 2016: +0.130 | 2017: +0.219 | 2018: +0.208 | 2019: +0.106 | 2020: +0.163 | 2021: +0.098
- IC CV=0.37, Neg years=0/7, Half ratio=0.61, Recency ratio=0.63
- Weak component: `close_vs_open_range` (CV=0.48)

**`combo_diff__max_down_ret__early_vwap_acceleration`** (Lock IC=+0.0826, Sharpe=+0.1035)
- Yearly ICs: 2015: +0.226 | 2016: +0.008 | 2017: +0.128 | 2018: +0.064 | 2019: +0.126 | 2020: +0.082 | 2021: +0.127
- IC CV=0.58, Neg years=0/7, Half ratio=1.18, Recency ratio=0.90
- Weak component: `early_vwap_acceleration` (CV=0.56)

**`combo_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1053, Sharpe=+0.0931)
- Yearly ICs: 2015: +0.228 | 2016: +0.113 | 2017: +0.202 | 2018: +0.196 | 2019: +0.109 | 2020: +0.127 | 2021: +0.063
- IC CV=0.38, Neg years=0/7, Half ratio=0.62, Recency ratio=0.56
- Weak component: `star50_limit_proximity_early` (CV=0.62)

**`combo_max__first_bar_sentiment__limit_down_proximity_early`** (Lock IC=+0.0718, Sharpe=+0.0924)
- Yearly ICs: 2015: +0.245 | 2016: +0.065 | 2017: +0.078 | 2018: +0.162 | 2019: +0.140 | 2020: +0.096 | 2021: +0.075
- IC CV=0.49, Neg years=0/7, Half ratio=0.80, Recency ratio=0.55
- Weak component: `limit_down_proximity_early` (CV=1.03)

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

### 159915ETF — `single` True Positives

**`combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1279, Sharpe=+1.5377)
- Yearly ICs: 2015: +0.234 | 2016: +0.094 | 2017: -0.031 | 2018: +0.132 | 2019: +0.264 | 2020: +0.182 | 2021: +0.132
- IC CV=0.63, Neg years=1/7, Half ratio=1.49, Recency ratio=0.96
- Weak component: `star50_limit_proximity_early` (CV=0.77)

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1318, Sharpe=+1.2965)
- Yearly ICs: 2015: +0.228 | 2016: +0.122 | 2017: +0.009 | 2018: +0.185 | 2019: +0.198 | 2020: +0.148 | 2021: +0.176
- IC CV=0.44, Neg years=0/7, Half ratio=1.16, Recency ratio=0.93
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)

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

**`combo_clamp_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.1109, Sharpe=+0.0049)
- Yearly ICs: 2015: +0.232 | 2016: +0.041 | 2017: +0.015 | 2018: +0.122 | 2019: +0.181 | 2020: +0.105 | 2021: +0.158
- IC CV=0.58, Neg years=0/7, Half ratio=1.29, Recency ratio=0.97
- Weak component: `demark_setup_reversal_early` (CV=0.85)

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.729±0.020 | 0.690±0.035 | 40% | USEFUL |
| ic_ir | 0.631±0.080 | 0.572±0.048 | 24% | USEFUL |
| p_value | 0.002±0.005 | 0.000±0.000 | 4% | USEFUL |
| max_corr | 0.438±0.335 | 0.684±0.148 | 42% | USEFUL |
| deflated_ic | 0.220±0.054 | 0.237±0.038 | 60% | WEAK |
| overall_ic | 0.221±0.054 | 0.237±0.038 | 60% | WEAK |
| raw_ic | 0.098±0.020 | 0.086±0.041 | 49% | USEFUL |

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.715±0.049 | 0.731±0.052 | 72% | WEAK |
| ic_ir | 0.607±0.150 | 0.678±0.176 | 71% | WEAK |
| p_value | 0.000±0.000 | 0.000±0.001 | 18% | USEFUL |
| max_corr | 0.729±0.189 | 0.727±0.203 | 89% | USELESS |
| deflated_ic | 0.222±0.030 | 0.251±0.047 | 55% | WEAK |
| overall_ic | 0.222±0.030 | 0.251±0.047 | 55% | WEAK |
| raw_ic | 0.131±0.028 | 0.150±0.027 | 93% | USELESS |

### 159915ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.720±0.036 | 0.699±0.029 | 36% | USEFUL |
| ic_ir | 0.576±0.050 | 0.570±0.091 | 40% | USEFUL |
| p_value | 0.000±0.000 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.774±0.027 | 0.641±0.288 | 9% | USEFUL |
| deflated_ic | 0.221±0.023 | 0.254±0.019 | 39% | USEFUL |
| overall_ic | 0.222±0.023 | 0.256±0.019 | 38% | USEFUL |
| raw_ic | 0.134±0.015 | 0.145±0.026 | 42% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 3/20 top rejects are profitable (15%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Sharpe=+0.4253
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.2340, Lock IC=+0.0054, Sharpe=+0.1767

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1637, Lock IC=+0.0306, Sharpe=+0.2008
- `gap_pct`: Train IC=+0.1525, Lock IC=+0.0795, Sharpe=+0.1398
- `combo_min__bar_ret_0__volume_surge_direction`: Train IC=+0.1563, Lock IC=+0.0151, Sharpe=+0.0150

**B3 Composite Floor**: 9/20 top rejects are profitable (45%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.2368, Lock IC=+0.0411, Sharpe=+0.2081
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.2368, Lock IC=+0.0411, Sharpe=+0.2081
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.2367, Lock IC=+0.0411, Sharpe=+0.2081

**B4 Correlation Gate**: 10/19 top rejects are profitable (53%)

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

**BH-FDR Gate**: 3/20 top rejects are profitable (15%)

- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.2780
- `combo_z_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Sharpe=+0.2780
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__late_bar_momentum`: Train IC=+0.0861, Lock IC=+0.0539, Sharpe=+0.1258

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__close_vs_open_range__rsi_opening`: Train IC=+0.2850, Lock IC=+0.1081, Sharpe=+0.9961
- `combo_tri_min__rbreaker_sell_setup_proximity_early__close_vs_open_range__high_low_sequence_momentum`: Train IC=+0.2850, Lock IC=+0.1081, Sharpe=+0.9961
- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2827, Lock IC=+0.1174, Sharpe=+0.8869

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Sharpe=+1.1127
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2914, Lock IC=+0.1158, Sharpe=+0.9651
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2788, Lock IC=+0.1329, Sharpe=+0.8899

### 159915ETF — `single`

**7-Year Jackknife**: 17/20 top rejects are profitable (85%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__early_range`: Train IC=+0.2105, Lock IC=+0.1395, Sharpe=+1.6071
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2242, Lock IC=+0.1531, Sharpe=+1.3653
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2242, Lock IC=+0.1531, Sharpe=+1.3653

**B2 Rolling Guard**: 18/20 top rejects are profitable (90%)

- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+0.8573
- `combo_z_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Sharpe=+0.8573
- `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1874, Lock IC=+0.1369, Sharpe=+0.8573

**BH-FDR Gate**: 1/3 top rejects are profitable (33%)

- `close_vs_open_range`: Train IC=+0.0863, Lock IC=+0.0988, Sharpe=+0.4620

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.5392
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Sharpe=+1.5392
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0`: Train IC=+0.2767, Lock IC=+0.1374, Sharpe=+1.5099

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Sharpe=+1.5377
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_ret_0`: Train IC=+0.2693, Lock IC=+0.1274, Sharpe=+1.4562
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_ret_0`: Train IC=+0.2693, Lock IC=+0.1274, Sharpe=+1.4562

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_std_across_regimes`: FP is lower (d=-1.52). Threshold 0.045 → 40% accuracy.
- `n_negative_regimes`: FP is lower (d=-1.25). Threshold 0.000 → 40% accuracy.
- `n_negative_years`: FP is lower (d=-1.09). Threshold 0.000 → 40% accuracy.
- `ic_cv`: FP is lower (d=-0.73). Threshold 1.012 → 50% accuracy.
- `weak_link_cv`: FP is lower (d=-0.69). Threshold 1.256 → 56% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/5
- Decaying signal (half ratio < 0.3): 0/5
- Weak component (CV > 2.0): 0/5
- Regime-dependent (≥2 negative regimes): 0/5

### 500ETF — `single`

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 1/21
- Decaying signal (half ratio < 0.3): 2/21
- Weak component (CV > 2.0): 0/21
- Regime-dependent (≥2 negative regimes): 0/21

### 159915ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_std_across_regimes`: FP is lower (d=-2.15). Threshold 0.080 → 55% accuracy.
- `n_negative_years`: FP is lower (d=-1.22). Threshold 1.000 → 55% accuracy.
- `ic_cv`: FP is lower (d=-0.77). Threshold 0.413 → 55% accuracy.
- `n_negative_regimes`: FP is lower (d=-0.58). Threshold 0.500 → 55% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/4
- Decaying signal (half ratio < 0.3): 0/4
- Weak component (CV > 2.0): 0/4
- Regime-dependent (≥2 negative regimes): 0/4

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_weighted_price_position` | 2 | 0 | 2 | 100% |  |
| `early_order_flow_imbalance` | 5 | 1 | 6 | 83% | ⚠ TOXIC |
| `first_bar_sentiment` | 8 | 5 | 13 | 62% |  |
| `early_body_momentum` | 3 | 2 | 5 | 60% |  |
| `max_down_ret` | 6 | 5 | 11 | 55% |  |
| `max_up_ret` | 13 | 12 | 25 | 52% |  |
| `opening_auction_imbalance` | 3 | 3 | 6 | 50% |  |
| `early_vwap_acceleration` | 1 | 1 | 2 | 50% |  |
| `close_vs_open_range` | 6 | 6 | 12 | 50% |  |
| `bar_body_rng_0` | 2 | 3 | 5 | 40% |  |
| `bar_ret_0` | 3 | 7 | 10 | 30% |  |
| `rbreaker_sell_setup_proximity_early` | 4 | 15 | 19 | 21% |  |
| `demark_setup_reversal_early` | 0 | 3 | 3 | 0% |  |
| `limit_down_proximity_early` | 0 | 4 | 4 | 0% |  |
| `star50_limit_proximity_early` | 0 | 11 | 11 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=9, TP=21, FP rate=30%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=5, TP=6, FP rate=45%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=3, TP=6, FP rate=33%

