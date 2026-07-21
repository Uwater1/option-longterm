# Filter Pipeline Deep Diagnosis

**Purpose**: Understand WHY admission gates fail, using only training-period signals.
Lockbox is used solely for labeling TP/FP — all proposed fixes are training-only.

---

## 1. FP/TP Summary

| ETF | Side | Admitted | FP | TP | FP Rate |
| :--- | :--- | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | 3 | 0 | 100% |
| 500ETF | single | 67 | 42 | 25 | 63% |
| 159915ETF | single | 20 | 4 | 16 | 20% |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 500ETF — `single` (FP=42, TP=25)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| weak_link_cv | 0.775 | 1.136 | 0.547 | 1.291 | -0.85 | 0.302 | 61% |
| ic_cv | 0.408 | 0.492 | 0.382 | 0.438 | -0.52 | 0.199 | 61% |
| ic_std_across_regimes | 0.065 | 0.059 | 0.068 | 0.057 | +0.37 | 0.038 | 66% |
| n_negative_years | 0.095 | 0.160 | 0.000 | 0.000 | -0.20 | 0.000 | 61% |
| recency_ratio | 0.748 | 0.774 | 0.725 | 0.748 | -0.12 | 0.427 | 64% |
| n_negative_regimes | 0.214 | 0.240 | 0.000 | 0.000 | -0.06 | 0.000 | 61% |
| half_ratio | 0.767 | 0.762 | 0.760 | 0.707 | +0.03 | 0.535 | 67% |

### 159915ETF — `single` (FP=4, TP=16)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.393 | 0.546 | 0.413 | 0.499 | -1.12 | 0.845 | 75% |
| n_negative_years | 0.000 | 0.250 | 0.000 | 0.000 | -0.82 | 1.000 | 75% |
| recency_ratio | 1.002 | 0.811 | 0.886 | 0.784 | +0.74 | 1.335 | 85% |
| half_ratio | 1.212 | 1.054 | 1.142 | 1.062 | +0.60 | 1.478 | 80% |
| weak_link_cv | 0.969 | 1.130 | 1.000 | 1.311 | -0.45 | 1.370 | 75% |
| n_negative_regimes | 0.000 | 0.062 | 0.000 | 0.000 | -0.37 | 0.500 | 75% |
| ic_std_across_regimes | 0.055 | 0.053 | 0.050 | 0.050 | +0.12 | 0.089 | 75% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_max__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0149, Sharpe=-0.7471)
- Yearly ICs: 2015: +0.092 | 2016: +0.110 | 2017: +0.049 | 2018: +0.194 | 2019: +0.095 | 2020: +0.006 | 2021: +0.139
- IC CV=0.57, Neg years=0/7, Half ratio=1.12, Recency ratio=0.72
- Weak component: `bar_body_rng_0` (CV=0.64, neg years=1)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.081, Q3_mid=+0.132, Q4=+0.098, Q5_high_vol=+0.153

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0031, Sharpe=-0.6926)
- Yearly ICs: 2015: +0.111 | 2016: +0.089 | 2017: +0.020 | 2018: +0.183 | 2019: +0.077 | 2020: -0.001 | 2021: +0.127
- IC CV=0.67, Neg years=1/7, Half ratio=1.07, Recency ratio=0.63
- Weak component: `max_up_ret` (CV=0.81, neg years=1)
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.054, Q3_mid=+0.113, Q4=+0.115, Q5_high_vol=+0.171

**`combo_diff__short_sell_quantity__roc60`** (Lock IC=-0.0007, Sharpe=+0.5778)
- Yearly ICs: 2015: +0.089 | 2016: +0.084 | 2017: +0.068 | 2018: +0.063 | 2019: +0.039 | 2020: +0.017 | 2021: +0.067
- IC CV=0.38, Neg years=0/7, Half ratio=0.16, Recency ratio=0.49
- Weak component: `short_sell_quantity` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.013, Q2=-0.008, Q3_mid=-0.058, Q4=+0.075, Q5_high_vol=+0.086

### 500ETF — `single` False Positives

**`combo_mean__max_up_ret__bar_vwap_dev_2`** (Lock IC=+0.0778, Sharpe=-1.2420)
- Yearly ICs: 2015: +0.189 | 2016: +0.094 | 2017: +0.186 | 2018: +0.129 | 2019: +0.111 | 2020: +0.178 | 2021: +0.106
- IC CV=0.27, Neg years=0/7, Half ratio=0.86, Recency ratio=1.00
- Weak component: `bar_vwap_dev_2` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.114, Q3_mid=+0.156, Q4=+0.117, Q5_high_vol=+0.229

**`combo_diff__yesterday_early_momentum__yesterday_day_skew`** (Lock IC=+0.0263, Sharpe=-1.0382)
- Yearly ICs: 2015: +0.038 | 2016: +0.092 | 2017: +0.037 | 2018: +0.060 | 2019: +0.045 | 2020: +0.149 | 2021: -0.024
- IC CV=0.88, Neg years=1/7, Half ratio=0.61, Recency ratio=0.95
- Weak component: `yesterday_day_skew` (CV=2.33, neg years=2)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.061, Q3_mid=+0.070, Q4=+0.130, Q5_high_vol=+0.080

**`combo_min__max_up_ret__bar_vwap_dev_2`** (Lock IC=+0.0691, Sharpe=-1.0165)
- Yearly ICs: 2015: +0.202 | 2016: +0.025 | 2017: +0.187 | 2018: +0.136 | 2019: +0.114 | 2020: +0.108 | 2021: +0.110
- IC CV=0.43, Neg years=0/7, Half ratio=0.88, Recency ratio=0.96
- Weak component: `bar_vwap_dev_2` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.063, Q3_mid=+0.136, Q4=+0.102, Q5_high_vol=+0.193

**`combo_mean__num_up_bars__bar_vwap_dev_2`** (Lock IC=+0.0572, Sharpe=-0.8822)
- Yearly ICs: 2015: +0.105 | 2016: +0.091 | 2017: +0.082 | 2018: +0.109 | 2019: +0.096 | 2020: +0.115 | 2021: +0.068
- IC CV=0.16, Neg years=0/7, Half ratio=0.94, Recency ratio=0.93
- Weak component: `bar_vwap_dev_2` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.024, Q3_mid=+0.157, Q4=+0.097, Q5_high_vol=+0.144

**`combo_ifelse__gap_pct__bar_ret_0__num_up_bars`** (Lock IC=+0.0782, Sharpe=-0.8694)
- Yearly ICs: 2015: +0.184 | 2016: +0.070 | 2017: +0.009 | 2018: +0.233 | 2019: +0.142 | 2020: +0.104 | 2021: +0.103
- IC CV=0.57, Neg years=0/7, Half ratio=1.16, Recency ratio=0.81
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.142, Q2=-0.069, Q3_mid=+0.217, Q4=+0.134, Q5_high_vol=+0.202

**`combo_max__bar_vwap_dev_2__bar_body_rng_1`** (Lock IC=+0.0172, Sharpe=-0.7758)
- Yearly ICs: 2015: +0.113 | 2016: +0.045 | 2017: +0.138 | 2018: +0.061 | 2019: +0.066 | 2020: +0.090 | 2021: +0.125
- IC CV=0.36, Neg years=0/7, Half ratio=0.83, Recency ratio=1.35
- Weak component: `bar_body_rng_1` (CV=0.72, neg years=0)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.125, Q3_mid=+0.103, Q4=+0.075, Q5_high_vol=+0.124

**`combo_mean__max_down_ret__bar_vwap_dev_2`** (Lock IC=+0.0660, Sharpe=-0.7547)
- Yearly ICs: 2015: +0.225 | 2016: -0.009 | 2017: +0.162 | 2018: +0.104 | 2019: +0.126 | 2020: +0.131 | 2021: +0.086
- IC CV=0.56, Neg years=1/7, Half ratio=1.03, Recency ratio=1.01
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.062, Q3_mid=+0.121, Q4=+0.054, Q5_high_vol=+0.212

**`combo_rank_min__max_up_ret__bar_vwap_dev_2`** (Lock IC=+0.0745, Sharpe=-0.7453)
- Yearly ICs: 2015: +0.198 | 2016: +0.015 | 2017: +0.150 | 2018: +0.124 | 2019: +0.130 | 2020: +0.117 | 2021: +0.108
- IC CV=0.43, Neg years=0/7, Half ratio=0.99, Recency ratio=1.05
- Weak component: `bar_vwap_dev_2` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.074, Q3_mid=+0.127, Q4=+0.095, Q5_high_vol=+0.192

**`combo_mean__max_up_ret__body_to_range_ratio`** (Lock IC=+0.0634, Sharpe=-0.7138)
- Yearly ICs: 2015: +0.187 | 2016: +0.157 | 2017: +0.217 | 2018: +0.183 | 2019: +0.068 | 2020: +0.158 | 2021: +0.019
- IC CV=0.47, Neg years=0/7, Half ratio=0.54, Recency ratio=0.51
- Weak component: `body_to_range_ratio` (CV=0.79, neg years=1)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.007, Q3_mid=+0.184, Q4=+0.161, Q5_high_vol=+0.213

**`combo_rank_max__max_down_ret__bar_vwap_dev_2`** (Lock IC=+0.0716, Sharpe=-0.6512)
- Yearly ICs: 2015: +0.169 | 2016: +0.096 | 2017: +0.235 | 2018: +0.102 | 2019: +0.127 | 2020: +0.191 | 2021: +0.094
- IC CV=0.35, Neg years=0/7, Half ratio=0.86, Recency ratio=1.08
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.072, Q3_mid=+0.160, Q4=+0.089, Q5_high_vol=+0.215

**`combo_max__bar_ret_0__first_30min_return`** (Lock IC=+0.0603, Sharpe=-0.6112)
- Yearly ICs: 2015: +0.215 | 2016: +0.102 | 2017: +0.191 | 2018: +0.222 | 2019: +0.102 | 2020: +0.112 | 2021: +0.140
- IC CV=0.32, Neg years=0/7, Half ratio=0.78, Recency ratio=0.80
- Weak component: `first_30min_return` (CV=0.41, neg years=0)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.072, Q3_mid=+0.163, Q4=+0.161, Q5_high_vol=+0.232

**`combo_rank_max__bar_ret_0__first_30min_return`** (Lock IC=+0.0601, Sharpe=-0.6093)
- Yearly ICs: 2015: +0.217 | 2016: +0.102 | 2017: +0.192 | 2018: +0.221 | 2019: +0.102 | 2020: +0.114 | 2021: +0.140
- IC CV=0.32, Neg years=0/7, Half ratio=0.78, Recency ratio=0.80
- Weak component: `first_30min_return` (CV=0.41, neg years=0)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.073, Q3_mid=+0.164, Q4=+0.160, Q5_high_vol=+0.233

**`combo_rank_min__max_up_ret__body_to_range_ratio`** (Lock IC=+0.0790, Sharpe=-0.5428)
- Yearly ICs: 2015: +0.201 | 2016: +0.077 | 2017: +0.206 | 2018: +0.109 | 2019: +0.103 | 2020: +0.144 | 2021: +0.049
- IC CV=0.44, Neg years=0/7, Half ratio=0.62, Recency ratio=0.69
- Weak component: `body_to_range_ratio` (CV=0.79, neg years=1)
- Regime ICs: Q1_low_vol=+0.174, Q2=-0.010, Q3_mid=+0.175, Q4=+0.100, Q5_high_vol=+0.192

**`combo_tri_median__max_up_ret__bar_ret_0__num_up_bars`** (Lock IC=+0.0726, Sharpe=-0.4965)
- Yearly ICs: 2015: +0.218 | 2016: +0.125 | 2017: +0.157 | 2018: +0.212 | 2019: +0.106 | 2020: +0.119 | 2021: +0.123
- IC CV=0.28, Neg years=0/7, Half ratio=0.71, Recency ratio=0.71
- Weak component: `bar_ret_0` (CV=0.35, neg years=0)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.020, Q3_mid=+0.192, Q4=+0.174, Q5_high_vol=+0.227

**`combo_rank_max__max_up_ret__bar_vwap_dev_2`** (Lock IC=+0.0547, Sharpe=-0.4762)
- Yearly ICs: 2015: +0.175 | 2016: +0.146 | 2017: +0.174 | 2018: +0.118 | 2019: +0.091 | 2020: +0.182 | 2021: +0.109
- IC CV=0.24, Neg years=0/7, Half ratio=0.73, Recency ratio=0.91
- Weak component: `bar_vwap_dev_2` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.137, Q3_mid=+0.158, Q4=+0.110, Q5_high_vol=+0.256

**`combo_rank_min__max_down_ret__first_30min_return`** (Lock IC=+0.0996, Sharpe=-0.4745)
- Yearly ICs: 2015: +0.269 | 2016: +0.100 | 2017: +0.252 | 2018: +0.137 | 2019: +0.112 | 2020: +0.135 | 2021: +0.059
- IC CV=0.48, Neg years=0/7, Half ratio=0.73, Recency ratio=0.53
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.200, Q2=-0.022, Q3_mid=+0.147, Q4=+0.108, Q5_high_vol=+0.221

**`combo_tri_max__max_up_ret__bar_ret_0__max_down_ret`** (Lock IC=+0.0790, Sharpe=-0.4708)
- Yearly ICs: 2015: +0.248 | 2016: +0.094 | 2017: +0.266 | 2018: +0.271 | 2019: +0.144 | 2020: +0.125 | 2021: +0.116
- IC CV=0.40, Neg years=0/7, Half ratio=0.76, Recency ratio=0.70
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.025, Q3_mid=+0.175, Q4=+0.172, Q5_high_vol=+0.284

**`combo_max__first_30min_return__bar_body_rng_0`** (Lock IC=+0.0750, Sharpe=-0.4293)
- Yearly ICs: 2015: +0.206 | 2016: +0.109 | 2017: +0.164 | 2018: +0.191 | 2019: +0.109 | 2020: +0.127 | 2021: +0.124
- IC CV=0.25, Neg years=0/7, Half ratio=0.86, Recency ratio=0.79
- Weak component: `first_30min_return` (CV=0.41, neg years=0)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.037, Q3_mid=+0.149, Q4=+0.147, Q5_high_vol=+0.235

**`combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0607, Sharpe=-0.3849)
- Yearly ICs: 2015: +0.220 | 2016: +0.150 | 2017: +0.150 | 2018: +0.156 | 2019: +0.110 | 2020: +0.111 | 2021: +0.104
- IC CV=0.26, Neg years=0/7, Half ratio=0.76, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.049, Q3_mid=+0.143, Q4=+0.176, Q5_high_vol=+0.259

**`combo_tri_max__max_up_ret__max_down_ret__bar_vwap_dev_2`** (Lock IC=+0.0751, Sharpe=-0.3584)
- Yearly ICs: 2015: +0.188 | 2016: +0.145 | 2017: +0.226 | 2018: +0.114 | 2019: +0.096 | 2020: +0.184 | 2021: +0.088
- IC CV=0.33, Neg years=0/7, Half ratio=0.69, Recency ratio=0.82
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.053, Q3_mid=+0.147, Q4=+0.111, Q5_high_vol=+0.266

**`combo_max__max_up_ret__num_up_bars`** (Lock IC=+0.0764, Sharpe=-0.3406)
- Yearly ICs: 2015: +0.216 | 2016: +0.177 | 2017: +0.093 | 2018: +0.214 | 2019: +0.087 | 2020: +0.116 | 2021: +0.057
- IC CV=0.44, Neg years=0/7, Half ratio=0.65, Recency ratio=0.44
- Weak component: `num_up_bars` (CV=0.34, neg years=0)
- Regime ICs: Q1_low_vol=+0.132, Q2=-0.005, Q3_mid=+0.187, Q4=+0.185, Q5_high_vol=+0.242

**`combo_ifelse__gap_pct__first_30min_return__bar_vwap_dev_2`** (Lock IC=+0.0491, Sharpe=-0.3047)
- Yearly ICs: 2015: +0.160 | 2016: +0.091 | 2017: +0.152 | 2018: +0.060 | 2019: +0.122 | 2020: +0.108 | 2021: +0.046
- IC CV=0.38, Neg years=0/7, Half ratio=0.54, Recency ratio=0.62
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.041, Q3_mid=+0.092, Q4=+0.115, Q5_high_vol=+0.152

**`combo_mean__max_down_ret__first_30min_return`** (Lock IC=+0.0857, Sharpe=-0.2895)
- Yearly ICs: 2015: +0.211 | 2016: +0.069 | 2017: +0.239 | 2018: +0.162 | 2019: +0.105 | 2020: +0.115 | 2021: +0.077
- IC CV=0.44, Neg years=0/7, Half ratio=0.73, Recency ratio=0.68
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.211, Q2=+0.002, Q3_mid=+0.152, Q4=+0.123, Q5_high_vol=+0.183

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0660, Sharpe=-0.2828)
- Yearly ICs: 2015: +0.266 | 2016: +0.091 | 2017: +0.212 | 2018: +0.246 | 2019: +0.128 | 2020: +0.121 | 2021: +0.120
- IC CV=0.38, Neg years=0/7, Half ratio=0.74, Recency ratio=0.67
- Weak component: `max_up_ret` (CV=0.30, neg years=0)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.043, Q3_mid=+0.183, Q4=+0.180, Q5_high_vol=+0.260

**`combo_min__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0754, Sharpe=-0.2482)
- Yearly ICs: 2015: +0.218 | 2016: +0.109 | 2017: +0.160 | 2018: +0.232 | 2019: +0.127 | 2020: +0.086 | 2021: +0.120
- IC CV=0.34, Neg years=0/7, Half ratio=0.81, Recency ratio=0.63
- Weak component: `bar_ret_0` (CV=0.35, neg years=0)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.024, Q3_mid=+0.143, Q4=+0.150, Q5_high_vol=+0.240

**`combo_rank_max__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0713, Sharpe=-0.2395)
- Yearly ICs: 2015: +0.193 | 2016: +0.107 | 2017: +0.161 | 2018: +0.219 | 2019: +0.150 | 2020: +0.091 | 2021: +0.107
- IC CV=0.30, Neg years=0/7, Half ratio=0.92, Recency ratio=0.66
- Weak component: `bar_ret_0` (CV=0.35, neg years=0)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.008, Q3_mid=+0.139, Q4=+0.150, Q5_high_vol=+0.232

**`combo_ifelse__gap_pct__max_up_ret__num_up_bars`** (Lock IC=+0.0826, Sharpe=-0.2371)
- Yearly ICs: 2015: +0.167 | 2016: +0.119 | 2017: +0.038 | 2018: +0.173 | 2019: +0.119 | 2020: +0.127 | 2021: +0.086
- IC CV=0.36, Neg years=0/7, Half ratio=0.96, Recency ratio=0.74
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.120, Q2=-0.029, Q3_mid=+0.219, Q4=+0.139, Q5_high_vol=+0.200

**`combo_rank_min__num_up_bars__body_to_range_ratio`** (Lock IC=+0.0727, Sharpe=-0.2221)
- Yearly ICs: 2015: +0.128 | 2016: +0.123 | 2017: +0.185 | 2018: +0.141 | 2019: +0.091 | 2020: +0.142 | 2021: +0.010
- IC CV=0.43, Neg years=0/7, Half ratio=0.64, Recency ratio=0.61
- Weak component: `body_to_range_ratio` (CV=0.79, neg years=1)
- Regime ICs: Q1_low_vol=+0.148, Q2=-0.047, Q3_mid=+0.239, Q4=+0.096, Q5_high_vol=+0.151

**`combo_max__max_up_ret__gap_pct`** (Lock IC=+0.0931, Sharpe=-0.1976)
- Yearly ICs: 2015: +0.221 | 2016: +0.115 | 2017: +0.167 | 2018: +0.286 | 2019: +0.088 | 2020: +0.095 | 2021: +0.033
- IC CV=0.56, Neg years=0/7, Half ratio=0.56, Recency ratio=0.38
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.113, Q3_mid=+0.154, Q4=+0.114, Q5_high_vol=+0.285

**`combo_rank_min__bar_ret_0__max_down_ret`** (Lock IC=+0.0898, Sharpe=-0.1902)
- Yearly ICs: 2015: +0.275 | 2016: +0.101 | 2017: +0.201 | 2018: +0.164 | 2019: +0.131 | 2020: +0.095 | 2021: +0.074
- IC CV=0.44, Neg years=0/7, Half ratio=0.74, Recency ratio=0.45
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.176, Q2=-0.000, Q3_mid=+0.120, Q4=+0.092, Q5_high_vol=+0.243

**`combo_ifelse__gap_pct__first_bar_return__bar_vwap_dev_2`** (Lock IC=+0.0654, Sharpe=-0.1873)
- Yearly ICs: 2015: +0.233 | 2016: +0.088 | 2017: +0.091 | 2018: +0.128 | 2019: +0.188 | 2020: +0.136 | 2021: +0.054
- IC CV=0.44, Neg years=0/7, Half ratio=0.72, Recency ratio=0.59
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.000, Q3_mid=+0.125, Q4=+0.119, Q5_high_vol=+0.239

**`combo_tri_min__max_up_ret__max_down_ret__num_up_bars`** (Lock IC=+0.0927, Sharpe=-0.1809)
- Yearly ICs: 2015: +0.230 | 2016: +0.069 | 2017: +0.161 | 2018: +0.117 | 2019: +0.122 | 2020: +0.118 | 2021: +0.097
- IC CV=0.37, Neg years=0/7, Half ratio=0.78, Recency ratio=0.72
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.005, Q3_mid=+0.185, Q4=+0.099, Q5_high_vol=+0.184

**`combo_ifelse__gap_pct__first_30min_return__yesterday_illiquidity_amihud`** (Lock IC=+0.0148, Sharpe=-0.1758)
- Yearly ICs: 2015: +0.087 | 2016: +0.022 | 2017: +0.191 | 2018: +0.095 | 2019: -0.002 | 2020: +0.068 | 2021: +0.026
- IC CV=0.86, Neg years=1/7, Half ratio=0.40, Recency ratio=0.87
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29, neg years=0)
- Regime ICs: Q1_low_vol=-0.003, Q2=+0.037, Q3_mid=+0.044, Q4=+0.133, Q5_high_vol=+0.072

**`combo_ifelse__gap_pct__max_up_ret__bar_ret_0`** (Lock IC=+0.0663, Sharpe=-0.1682)
- Yearly ICs: 2015: +0.201 | 2016: +0.157 | 2017: +0.138 | 2018: +0.174 | 2019: +0.111 | 2020: +0.113 | 2021: +0.094
- IC CV=0.25, Neg years=0/7, Half ratio=0.71, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.067, Q3_mid=+0.133, Q4=+0.159, Q5_high_vol=+0.241

**`combo_max__max_down_ret__yesterday_illiquidity_amihud`** (Lock IC=+0.0913, Sharpe=-0.1250)
- Yearly ICs: 2015: +0.163 | 2016: +0.068 | 2017: +0.273 | 2018: +0.168 | 2019: +0.073 | 2020: +0.140 | 2021: +0.071
- IC CV=0.51, Neg years=0/7, Half ratio=0.76, Recency ratio=0.91
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29, neg years=0)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.027, Q3_mid=+0.122, Q4=+0.079, Q5_high_vol=+0.190

**`combo_min__max_up_ret__yesterday_illiquidity_amihud`** (Lock IC=+0.0072, Sharpe=-0.1169)
- Yearly ICs: 2015: +0.186 | 2016: +0.068 | 2017: +0.187 | 2018: +0.166 | 2019: +0.080 | 2020: +0.067 | 2021: +0.121
- IC CV=0.40, Neg years=0/7, Half ratio=0.67, Recency ratio=0.74
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29, neg years=0)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.033, Q3_mid=+0.096, Q4=+0.164, Q5_high_vol=+0.221

**`combo_ifelse__gap_pct__max_up_ret__bar_vwap_dev_2`** (Lock IC=+0.0668, Sharpe=-0.1039)
- Yearly ICs: 2015: +0.230 | 2016: +0.144 | 2017: +0.097 | 2018: +0.067 | 2019: +0.148 | 2020: +0.162 | 2021: +0.048
- IC CV=0.45, Neg years=0/7, Half ratio=0.59, Recency ratio=0.56
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.053, Q3_mid=+0.117, Q4=+0.133, Q5_high_vol=+0.245

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0931, Sharpe=-0.0963)
- Yearly ICs: 2015: +0.224 | 2016: +0.134 | 2017: +0.164 | 2018: +0.199 | 2019: +0.117 | 2020: +0.116 | 2021: +0.164
- IC CV=0.24, Neg years=0/7, Half ratio=0.86, Recency ratio=0.78
- Weak component: `max_up_ret` (CV=0.30, neg years=0)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.013, Q3_mid=+0.163, Q4=+0.177, Q5_high_vol=+0.282

**`combo_rank_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0944, Sharpe=-0.0953)
- Yearly ICs: 2015: +0.246 | 2016: +0.091 | 2017: +0.237 | 2018: +0.236 | 2019: +0.141 | 2020: +0.130 | 2021: +0.098
- IC CV=0.38, Neg years=0/7, Half ratio=0.80, Recency ratio=0.68
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.019, Q3_mid=+0.174, Q4=+0.143, Q5_high_vol=+0.245

**`combo_rank_min__max_down_ret__bar_vwap_dev_2`** (Lock IC=+0.0740, Sharpe=-0.0416)
- Yearly ICs: 2015: +0.262 | 2016: -0.028 | 2017: +0.113 | 2018: +0.107 | 2019: +0.121 | 2020: +0.114 | 2021: +0.057
- IC CV=0.75, Neg years=1/7, Half ratio=1.11, Recency ratio=0.73
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.043, Q3_mid=+0.080, Q4=+0.054, Q5_high_vol=+0.206

**`combo_tri_median__max_up_ret__first_bar_return__max_down_ret`** (Lock IC=+0.0893, Sharpe=-0.0364)
- Yearly ICs: 2015: +0.240 | 2016: +0.116 | 2017: +0.189 | 2018: +0.217 | 2019: +0.131 | 2020: +0.105 | 2021: +0.121
- IC CV=0.32, Neg years=0/7, Half ratio=0.79, Recency ratio=0.63
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.024, Q3_mid=+0.170, Q4=+0.149, Q5_high_vol=+0.245

**`combo_mean__max_up_ret__yesterday_illiquidity_amihud`** (Lock IC=+0.0553, Sharpe=-0.0215)
- Yearly ICs: 2015: +0.181 | 2016: +0.110 | 2017: +0.206 | 2018: +0.163 | 2019: +0.083 | 2020: +0.085 | 2021: +0.138
- IC CV=0.32, Neg years=0/7, Half ratio=0.64, Recency ratio=0.77
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29, neg years=0)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.099, Q3_mid=+0.147, Q4=+0.143, Q5_high_vol=+0.244

### 159915ETF — `single` False Positives

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0930, Sharpe=-0.3239)
- Yearly ICs: 2015: +0.219 | 2016: +0.147 | 2017: +0.003 | 2018: +0.124 | 2019: +0.196 | 2020: +0.131 | 2021: +0.157
- IC CV=0.46, Neg years=0/7, Half ratio=1.29, Recency ratio=0.79
- Weak component: `bar_body_rng_0` (CV=0.51, neg years=1)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.070, Q3_mid=+0.195, Q4=+0.141, Q5_high_vol=+0.232

**`combo_ifelse__gap_pct__max_up_ret__early_range`** (Lock IC=+0.0511, Sharpe=-0.2340)
- Yearly ICs: 2015: +0.134 | 2016: +0.092 | 2017: +0.062 | 2018: +0.118 | 2019: +0.132 | 2020: +0.129 | 2021: +0.092
- IC CV=0.23, Neg years=0/7, Half ratio=0.99, Recency ratio=0.98
- Weak component: `gap_pct` (CV=1.37, neg years=2)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.185, Q3_mid=+0.112, Q4=+0.202, Q5_high_vol=+0.099

**`combo_ratio__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0608, Sharpe=-0.1597)
- Yearly ICs: 2015: +0.126 | 2016: +0.055 | 2017: +0.032 | 2018: +0.028 | 2019: +0.120 | 2020: +0.113 | 2021: +0.149
- IC CV=0.51, Neg years=0/7, Half ratio=1.58, Recency ratio=1.45
- Weak component: `keltner_squeeze_width` (CV=0.63, neg years=1)
- Regime ICs: Q1_low_vol=+0.010, Q2=+0.070, Q3_mid=+0.139, Q4=+0.097, Q5_high_vol=+0.151

**`combo_ifelse__gap_pct__max_up_ret__bar_vol_5`** (Lock IC=+0.0729, Sharpe=-0.0801)
- Yearly ICs: 2015: +0.163 | 2016: +0.104 | 2017: +0.053 | 2018: +0.095 | 2019: +0.182 | 2020: +0.131 | 2021: +0.081
- IC CV=0.37, Neg years=0/7, Half ratio=1.00, Recency ratio=0.79
- Weak component: `gap_pct` (CV=1.37, neg years=2)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.156, Q3_mid=+0.153, Q4=+0.193, Q5_high_vol=+0.113

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`combo_min__max_up_ret__gap_pct`** (Lock IC=+0.1222, Sharpe=+0.8978)
- Yearly ICs: 2015: +0.227 | 2016: +0.110 | 2017: +0.203 | 2018: +0.028 | 2019: +0.139 | 2020: +0.140 | 2021: +0.121
- IC CV=0.44, Neg years=0/7, Half ratio=0.62, Recency ratio=0.77
- Weak component: `gap_pct` (CV=1.29)

**`combo_rank_min__max_up_ret__gap_pct`** (Lock IC=+0.1302, Sharpe=+0.8877)
- Yearly ICs: 2015: +0.219 | 2016: +0.051 | 2017: +0.166 | 2018: +0.014 | 2019: +0.139 | 2020: +0.104 | 2021: +0.088
- IC CV=0.58, Neg years=0/7, Half ratio=0.53, Recency ratio=0.71
- Weak component: `gap_pct` (CV=1.29)

**`combo_mean__max_up_ret__gap_pct`** (Lock IC=+0.1307, Sharpe=+0.6572)
- Yearly ICs: 2015: +0.275 | 2016: +0.149 | 2017: +0.231 | 2018: +0.185 | 2019: +0.114 | 2020: +0.157 | 2021: +0.106
- IC CV=0.33, Neg years=0/7, Half ratio=0.56, Recency ratio=0.62
- Weak component: `gap_pct` (CV=1.29)

**`combo_product__num_up_bars__body_to_range_ratio`** (Lock IC=+0.0407, Sharpe=+0.6187)
- Yearly ICs: 2015: +0.192 | 2016: +0.125 | 2017: +0.189 | 2018: +0.033 | 2019: +0.017 | 2020: +0.074 | 2021: +0.052
- IC CV=0.69, Neg years=0/7, Half ratio=0.42, Recency ratio=0.40
- Weak component: `body_to_range_ratio` (CV=0.79)

**`combo_ifelse__gap_pct__yesterday_early_vwap_dev__first_30min_return`** (Lock IC=+0.0906, Sharpe=+0.5827)
- Yearly ICs: 2015: +0.117 | 2016: +0.059 | 2017: +0.170 | 2018: +0.116 | 2019: +0.110 | 2020: +0.159 | 2021: +0.014
- IC CV=0.48, Neg years=0/7, Half ratio=0.91, Recency ratio=0.98
- Weak component: `gap_pct` (CV=1.29)

**`combo_mean__bar_ret_0__max_down_ret`** (Lock IC=+0.1025, Sharpe=+0.4799)
- Yearly ICs: 2015: +0.227 | 2016: +0.106 | 2017: +0.224 | 2018: +0.210 | 2019: +0.137 | 2020: +0.111 | 2021: +0.088
- IC CV=0.36, Neg years=0/7, Half ratio=0.81, Recency ratio=0.60
- Weak component: `max_down_ret` (CV=0.55)

**`combo_mean__first_30min_return__gap_pct`** (Lock IC=+0.1047, Sharpe=+0.4212)
- Yearly ICs: 2015: +0.215 | 2016: +0.106 | 2017: +0.207 | 2018: +0.097 | 2019: +0.096 | 2020: +0.087 | 2021: +0.046
- IC CV=0.48, Neg years=0/7, Half ratio=0.42, Recency ratio=0.41
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__max_up_ret__max_down_ret`** (Lock IC=+0.1086, Sharpe=+0.4177)
- Yearly ICs: 2015: +0.273 | 2016: +0.141 | 2017: +0.132 | 2018: +0.093 | 2019: +0.133 | 2020: +0.166 | 2021: +0.073
- IC CV=0.41, Neg years=0/7, Half ratio=0.83, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_vwap_dev_2`** (Lock IC=+0.0700, Sharpe=+0.3163)
- Yearly ICs: 2015: +0.130 | 2016: +0.094 | 2017: +0.120 | 2018: +0.050 | 2019: +0.153 | 2020: +0.162 | 2021: -0.015
- IC CV=0.59, Neg years=1/7, Half ratio=0.70, Recency ratio=0.66
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__bar_ret_0__max_down_ret`** (Lock IC=+0.1099, Sharpe=+0.3121)
- Yearly ICs: 2015: +0.292 | 2016: +0.091 | 2017: +0.166 | 2018: +0.148 | 2019: +0.170 | 2020: +0.134 | 2021: +0.068
- IC CV=0.44, Neg years=0/7, Half ratio=0.91, Recency ratio=0.53
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum`** (Lock IC=+0.0546, Sharpe=+0.2905)
- Yearly ICs: 2015: +0.170 | 2016: +0.086 | 2017: -0.039 | 2018: +0.173 | 2019: +0.085 | 2020: +0.118 | 2021: +0.074
- IC CV=0.70, Neg years=1/7, Half ratio=0.80, Recency ratio=0.75
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud`** (Lock IC=+0.0258, Sharpe=+0.2539)
- Yearly ICs: 2015: +0.174 | 2016: +0.004 | 2017: +0.142 | 2018: +0.162 | 2019: +0.058 | 2020: +0.102 | 2021: +0.039
- IC CV=0.62, Neg years=0/7, Half ratio=0.71, Recency ratio=0.79
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29)

**`combo_diff__max_down_ret__yesterday_day_vwap_dev`** (Lock IC=+0.1064, Sharpe=+0.2445)
- Yearly ICs: 2015: +0.169 | 2016: +0.057 | 2017: +0.183 | 2018: +0.175 | 2019: +0.136 | 2020: +0.168 | 2021: +0.091
- IC CV=0.32, Neg years=0/7, Half ratio=1.64, Recency ratio=1.15
- Weak component: `yesterday_day_vwap_dev` (CV=0.59)

**`combo_ifelse__gap_pct__max_up_ret__yesterday_illiquidity_amihud`** (Lock IC=+0.0326, Sharpe=+0.2417)
- Yearly ICs: 2015: +0.167 | 2016: +0.073 | 2017: +0.143 | 2018: +0.094 | 2019: +0.013 | 2020: +0.126 | 2021: +0.056
- IC CV=0.52, Neg years=0/7, Half ratio=0.48, Recency ratio=0.76
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29)

**`combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew`** (Lock IC=+0.0338, Sharpe=+0.2319)
- Yearly ICs: 2015: +0.049 | 2016: +0.050 | 2017: +0.018 | 2018: +0.073 | 2019: +0.047 | 2020: +0.110 | 2021: -0.004
- IC CV=0.69, Neg years=1/7, Half ratio=0.69, Recency ratio=1.07
- Weak component: `yesterday_day_skew` (CV=2.33)

**`combo_max__max_up_ret__bar_body_rng_1`** (Lock IC=+0.0678, Sharpe=+0.2310)
- Yearly ICs: 2015: +0.150 | 2016: +0.107 | 2017: +0.174 | 2018: +0.131 | 2019: +0.045 | 2020: +0.128 | 2021: +0.138
- IC CV=0.30, Neg years=0/7, Half ratio=0.79, Recency ratio=1.03
- Weak component: `bar_body_rng_1` (CV=0.72)

**`combo_min__max_down_ret__bar_body_rng_1`** (Lock IC=+0.0858, Sharpe=+0.2271)
- Yearly ICs: 2015: +0.259 | 2016: +0.024 | 2017: +0.209 | 2018: +0.060 | 2019: +0.075 | 2020: +0.053 | 2021: +0.076
- IC CV=0.76, Neg years=0/7, Half ratio=0.59, Recency ratio=0.46
- Weak component: `bar_body_rng_1` (CV=0.72)

**`combo_rank_min__max_up_ret__yesterday_illiquidity_amihud`** (Lock IC=+0.0152, Sharpe=+0.2080)
- Yearly ICs: 2015: +0.182 | 2016: +0.062 | 2017: +0.169 | 2018: +0.175 | 2019: +0.086 | 2020: +0.049 | 2021: +0.112
- IC CV=0.44, Neg years=0/7, Half ratio=0.68, Recency ratio=0.66
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29)

**`combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_body_rng_0`** (Lock IC=+0.0691, Sharpe=+0.1687)
- Yearly ICs: 2015: +0.116 | 2016: +0.117 | 2017: +0.167 | 2018: +0.124 | 2019: +0.109 | 2020: +0.146 | 2021: +0.024
- IC CV=0.36, Neg years=0/7, Half ratio=0.88, Recency ratio=0.73
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__first_bar_return__first_30min_return`** (Lock IC=+0.0855, Sharpe=+0.1671)
- Yearly ICs: 2015: +0.218 | 2016: +0.051 | 2017: +0.153 | 2018: +0.203 | 2019: +0.141 | 2020: +0.113 | 2021: +0.096
- IC CV=0.39, Neg years=0/7, Half ratio=0.87, Recency ratio=0.78
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud`** (Lock IC=+0.0279, Sharpe=+0.0586)
- Yearly ICs: 2015: +0.066 | 2016: +0.050 | 2017: +0.161 | 2018: +0.057 | 2019: +0.029 | 2020: +0.179 | 2021: -0.041
- IC CV=0.98, Neg years=1/7, Half ratio=0.67, Recency ratio=1.20
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29)

**`combo_rank_max__max_up_ret__first_30min_return`** (Lock IC=+0.0690, Sharpe=+0.0554)
- Yearly ICs: 2015: +0.236 | 2016: +0.098 | 2017: +0.230 | 2018: +0.197 | 2019: +0.091 | 2020: +0.130 | 2021: +0.103
- IC CV=0.38, Neg years=0/7, Half ratio=0.67, Recency ratio=0.70
- Weak component: `first_30min_return` (CV=0.41)

**`combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars`** (Lock IC=+0.0861, Sharpe=+0.0453)
- Yearly ICs: 2015: +0.084 | 2016: +0.081 | 2017: +0.035 | 2018: +0.142 | 2019: +0.106 | 2020: +0.139 | 2021: +0.020
- IC CV=0.50, Neg years=0/7, Half ratio=1.16, Recency ratio=0.96
- Weak component: `gap_pct` (CV=1.29)

**`combo_rank_min__max_up_ret__num_up_bars`** (Lock IC=+0.0899, Sharpe=+0.0273)
- Yearly ICs: 2015: +0.115 | 2016: +0.055 | 2017: +0.157 | 2018: +0.122 | 2019: +0.112 | 2020: +0.092 | 2021: +0.126
- IC CV=0.26, Neg years=0/7, Half ratio=0.92, Recency ratio=1.28
- Weak component: `num_up_bars` (CV=0.34)

**`combo_ifelse__gap_pct__max_up_ret__first_30min_return`** (Lock IC=+0.0858, Sharpe=+0.0042)
- Yearly ICs: 2015: +0.208 | 2016: +0.096 | 2017: +0.139 | 2018: +0.127 | 2019: +0.107 | 2020: +0.136 | 2021: +0.096
- IC CV=0.28, Neg years=0/7, Half ratio=0.77, Recency ratio=0.76
- Weak component: `gap_pct` (CV=1.29)

### 159915ETF — `single` True Positives

**`combo_mean__max_up_ret__gap_pct`** (Lock IC=+0.1505, Sharpe=+1.0973)
- Yearly ICs: 2015: +0.190 | 2016: +0.097 | 2017: +0.007 | 2018: +0.133 | 2019: +0.160 | 2020: +0.145 | 2021: +0.152
- IC CV=0.44, Neg years=0/7, Half ratio=1.13, Recency ratio=1.03
- Weak component: `gap_pct` (CV=1.37)

**`combo_rank_min__max_up_ret__gap_pct`** (Lock IC=+0.1252, Sharpe=+0.9217)
- Yearly ICs: 2015: +0.202 | 2016: +0.043 | 2017: -0.019 | 2018: +0.040 | 2019: +0.223 | 2020: +0.136 | 2021: +0.129
- IC CV=0.77, Neg years=1/7, Half ratio=1.21, Recency ratio=1.08
- Weak component: `gap_pct` (CV=1.37)

**`combo_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.1063, Sharpe=+0.8462)
- Yearly ICs: 2015: +0.183 | 2016: +0.120 | 2017: +0.113 | 2018: +0.059 | 2019: +0.075 | 2020: +0.104 | 2021: +0.108
- IC CV=0.33, Neg years=0/7, Half ratio=0.87, Recency ratio=0.70
- Weak component: `keltner_squeeze_width` (CV=0.63)

**`combo_ifelse__gap_pct__bar_body_rng_0__yesterday_first_30min_return`** (Lock IC=+0.1243, Sharpe=+0.8402)
- Yearly ICs: 2015: +0.166 | 2016: +0.157 | 2017: +0.073 | 2018: +0.102 | 2019: +0.191 | 2020: +0.132 | 2021: +0.057
- IC CV=0.37, Neg years=0/7, Half ratio=0.94, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.37)

**`combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0`** (Lock IC=+0.0742, Sharpe=+0.7715)
- Yearly ICs: 2015: +0.206 | 2016: +0.145 | 2017: -0.093 | 2018: +0.234 | 2019: +0.114 | 2020: +0.091 | 2021: +0.069
- IC CV=0.91, Neg years=1/7, Half ratio=0.99, Recency ratio=0.45
- Weak component: `bb_width` (CV=1.25)

**`combo_min__bar_body_rng_0__bar_ret_0`** (Lock IC=+0.0873, Sharpe=+0.7078)
- Yearly ICs: 2015: +0.207 | 2016: +0.157 | 2017: +0.001 | 2018: +0.137 | 2019: +0.191 | 2020: +0.122 | 2021: +0.137
- IC CV=0.45, Neg years=0/7, Half ratio=1.27, Recency ratio=0.71
- Weak component: `bar_body_rng_0` (CV=0.51)

**`combo_ifelse__bb_width__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0731, Sharpe=+0.6021)
- Yearly ICs: 2015: +0.204 | 2016: +0.121 | 2017: +0.020 | 2018: +0.129 | 2019: +0.200 | 2020: +0.120 | 2021: +0.134
- IC CV=0.43, Neg years=0/7, Half ratio=1.38, Recency ratio=0.78
- Weak component: `bb_width` (CV=1.25)

**`combo_ifelse__gap_pct__bar_body_rng_0__yesterday_early_vwap_dev`** (Lock IC=+0.0932, Sharpe=+0.5611)
- Yearly ICs: 2015: +0.199 | 2016: +0.120 | 2017: +0.003 | 2018: +0.097 | 2019: +0.186 | 2020: +0.141 | 2021: +0.071
- IC CV=0.54, Neg years=0/7, Half ratio=1.00, Recency ratio=0.66
- Weak component: `gap_pct` (CV=1.37)

**`combo_ifelse__gap_pct__first_bar_return__yesterday_early_trend`** (Lock IC=+0.0784, Sharpe=+0.4088)
- Yearly ICs: 2015: +0.214 | 2016: +0.160 | 2017: +0.012 | 2018: +0.144 | 2019: +0.182 | 2020: +0.124 | 2021: +0.039
- IC CV=0.55, Neg years=0/7, Half ratio=0.67, Recency ratio=0.44
- Weak component: `gap_pct` (CV=1.37)

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum`** (Lock IC=+0.0751, Sharpe=+0.3462)
- Yearly ICs: 2015: +0.187 | 2016: +0.186 | 2017: +0.044 | 2018: +0.131 | 2019: +0.107 | 2020: +0.138 | 2021: +0.050
- IC CV=0.45, Neg years=0/7, Half ratio=0.59, Recency ratio=0.50
- Weak component: `gap_pct` (CV=1.37)

**`combo_ifelse__gap_pct__bar_body_rng_0__bar_vol_5`** (Lock IC=+0.0803, Sharpe=+0.2160)
- Yearly ICs: 2015: +0.156 | 2016: +0.083 | 2017: +0.031 | 2018: +0.089 | 2019: +0.230 | 2020: +0.145 | 2021: +0.087
- IC CV=0.51, Neg years=0/7, Half ratio=1.62, Recency ratio=0.97
- Weak component: `gap_pct` (CV=1.37)

**`combo_max__max_up_ret__first_30min_return`** (Lock IC=+0.0897, Sharpe=+0.2100)
- Yearly ICs: 2015: +0.168 | 2016: +0.058 | 2017: +0.065 | 2018: +0.031 | 2019: +0.124 | 2020: +0.075 | 2021: +0.173
- IC CV=0.52, Neg years=0/7, Half ratio=1.18, Recency ratio=1.10
- Weak component: `first_30min_return` (CV=0.78)

**`combo_rank_max__max_up_ret__first_30min_return`** (Lock IC=+0.0880, Sharpe=+0.1606)
- Yearly ICs: 2015: +0.169 | 2016: +0.072 | 2017: +0.074 | 2018: +0.037 | 2019: +0.127 | 2020: +0.103 | 2021: +0.167
- IC CV=0.43, Neg years=0/7, Half ratio=1.23, Recency ratio=1.12
- Weak component: `first_30min_return` (CV=0.78)

**`combo_ifelse__gap_pct__first_bar_return__early_range`** (Lock IC=+0.0556, Sharpe=+0.1047)
- Yearly ICs: 2015: +0.127 | 2016: +0.045 | 2017: +0.038 | 2018: +0.131 | 2019: +0.200 | 2020: +0.126 | 2021: +0.085
- IC CV=0.49, Neg years=0/7, Half ratio=1.31, Recency ratio=1.22
- Weak component: `gap_pct` (CV=1.37)

**`combo_clamp_diff__early_range__yesterday_day_vwap_dev`** (Lock IC=+0.1090, Sharpe=+0.1008)
- Yearly ICs: 2015: +0.062 | 2016: +0.169 | 2017: +0.067 | 2018: +0.129 | 2019: +0.033 | 2020: +0.194 | 2021: -0.013
- IC CV=0.76, Neg years=1/7, Half ratio=0.74, Recency ratio=0.79
- Weak component: `early_range` (CV=0.96)

**`combo_diff__early_range__yesterday_day_vwap_dev`** (Lock IC=+0.1069, Sharpe=+0.1008)
- Yearly ICs: 2015: +0.049 | 2016: +0.171 | 2017: +0.067 | 2018: +0.131 | 2019: +0.033 | 2020: +0.195 | 2021: -0.012
- IC CV=0.78, Neg years=1/7, Half ratio=0.75, Recency ratio=0.83
- Weak component: `early_range` (CV=0.96)

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.727±0.052 | 0.690±0.051 | 74% | WEAK |
| ic_ir | 0.624±0.140 | 0.563±0.127 | 78% | WEAK |
| p_value | 0.000±0.001 | 0.001±0.001 | 91% | USELESS |
| max_corr | 0.788±0.120 | 0.700±0.189 | 59% | WEAK |
| deflated_ic | 0.217±0.029 | 0.223±0.037 | 84% | USELESS |
| overall_ic | 0.218±0.029 | 0.224±0.037 | 84% | USELESS |
| raw_ic | 0.142±0.026 | 0.122±0.029 | 95% | USELESS |

### 159915ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.719±0.053 | 0.680±0.042 | 30% | USEFUL |
| ic_ir | 0.616±0.215 | 0.494±0.098 | 30% | USEFUL |
| p_value | 0.001±0.002 | 0.000±0.000 | 37% | USEFUL |
| max_corr | 0.754±0.097 | 0.682±0.247 | 26% | USEFUL |
| deflated_ic | 0.191±0.028 | 0.206±0.029 | 52% | WEAK |
| overall_ic | 0.192±0.029 | 0.207±0.029 | 54% | WEAK |
| raw_ic | 0.130±0.016 | 0.131±0.013 | 84% | USELESS |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 1/20 top rejects are profitable (5%)

- `yesterday_lunch_gap`: Train IC=+0.1668, Lock IC=+0.0943, Sharpe=+0.3158

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `combo_product__short_sell_quantity__roc60`: Train IC=+0.1013, Lock IC=+0.0008, Sharpe=+0.4965
- `combo_min__bar_ret_0__bar_body_rng_0`: Train IC=+0.1467, Lock IC=+0.0117, Sharpe=+0.2664
- `combo_min__first_bar_return__bar_body_rng_0`: Train IC=+0.1464, Lock IC=+0.0116, Sharpe=+0.2664

**BH-FDR Gate**: 2/2 top rejects are profitable (100%)

- `combo_clamp_diff__short_sell_quantity__sma100_dist`: Train IC=+0.1435, Lock IC=+0.0220, Sharpe=+0.8087
- `combo_product__short_sell_quantity__sma100_dist`: Train IC=+0.1023, Lock IC=+0.0248, Sharpe=+0.8017

**B4 Correlation Gate**: 1/4 top rejects are profitable (25%)

- `combo_diff__short_sell_quantity__sma100_dist`: Train IC=+0.1484, Lock IC=+0.0220, Sharpe=+0.8087

### 500ETF — `single`

**7-Year Jackknife**: 6/20 top rejects are profitable (30%)

- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum`: Train IC=+0.2464, Lock IC=+0.0560, Sharpe=+0.6438
- `combo_rank_max__margin_balance__short_balance`: Train IC=+0.1987, Lock IC=+0.0592, Sharpe=+0.4936
- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`: Train IC=+0.2061, Lock IC=+0.0705, Sharpe=+0.4007

**B2 Rolling Guard**: 5/20 top rejects are profitable (25%)

- `combo_abs_diff__margin_balance__yesterday_day_skew`: Train IC=+0.0386, Lock IC=+0.0458, Sharpe=+0.2660
- `combo_rank_min__first_30min_return__num_up_bars`: Train IC=+0.1488, Lock IC=+0.0796, Sharpe=+0.2450
- `combo_mean__max_down_ret__num_up_bars`: Train IC=+0.1617, Lock IC=+0.0992, Sharpe=+0.1165

**BH-FDR Gate**: 6/20 top rejects are profitable (30%)

- `vol_ratio_10_60`: Train IC=+0.0927, Lock IC=+0.0309, Sharpe=+0.3757
- `combo_ifelse__gap_pct__max_up_ret__short_balance`: Train IC=+0.1203, Lock IC=+0.0412, Sharpe=+0.2838
- `combo_ifelse__gap_pct__max_up_ret__margin_balance`: Train IC=+0.0806, Lock IC=+0.0318, Sharpe=+0.1877

**B3 Composite Floor**: 4/20 top rejects are profitable (20%)

- `combo_tri_mean__max_up_ret__first_bar_return__max_down_ret`: Train IC=+0.2436, Lock IC=+0.1014, Sharpe=+0.2785
- `combo_tri_mean__max_up_ret__bar_ret_0__max_down_ret`: Train IC=+0.2434, Lock IC=+0.1014, Sharpe=+0.2785
- `combo_tri_mean__max_up_ret__first_bar_return__first_30min_return`: Train IC=+0.2204, Lock IC=+0.0825, Sharpe=+0.1401

**B4 Correlation Gate**: 5/20 top rejects are profitable (25%)

- `combo_ifelse__gap_pct__first_bar_return__max_down_ret`: Train IC=+0.2578, Lock IC=+0.1097, Sharpe=+0.3121
- `combo_rank_min__max_up_ret__bar_body_rng_0`: Train IC=+0.2539, Lock IC=+0.0717, Sharpe=+0.2507
- `combo_mean__max_up_ret__first_bar_return`: Train IC=+0.2383, Lock IC=+0.0779, Sharpe=+0.1262

### 159915ETF — `single`

**7-Year Jackknife**: 16/20 top rejects are profitable (80%)

- `combo_diff__yesterday_first_30min_return__yesterday_day_vwap_dev`: Train IC=+0.1938, Lock IC=+0.0906, Sharpe=+1.1429
- `combo_ifelse__bb_width__yesterday_afternoon_momentum__bar_body_rng_0`: Train IC=+0.2038, Lock IC=+0.0555, Sharpe=+0.9824
- `combo_ifelse__bb_width__yesterday_early_momentum__first_bar_return`: Train IC=+0.1792, Lock IC=+0.0737, Sharpe=+0.9070

**B2 Rolling Guard**: 13/20 top rejects are profitable (65%)

- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2173, Lock IC=+0.1310, Sharpe=+1.2310
- `combo_rank_min__max_up_ret__max_down_ret`: Train IC=+0.2204, Lock IC=+0.0988, Sharpe=+0.7200
- `combo_max__first_bar_return__max_down_ret`: Train IC=+0.1709, Lock IC=+0.0907, Sharpe=+0.5764

**BH-FDR Gate**: 5/20 top rejects are profitable (25%)

- `combo_tri_max__yesterday_early_momentum__yesterday_first_30min_return__yesterday_afternoon_reversal`: Train IC=+0.0733, Lock IC=+0.0354, Sharpe=+0.3321
- `combo_rank_max__max_up_ret__gap_pct`: Train IC=+0.1253, Lock IC=+0.1090, Sharpe=+0.2066
- `combo_clamp_diff__early_range__bb_width`: Train IC=+0.0972, Lock IC=+0.0378, Sharpe=+0.1704

**B3 Composite Floor**: 15/20 top rejects are profitable (75%)

- `combo_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1949, Lock IC=+0.1521, Sharpe=+1.1944
- `combo_clamp_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1911, Lock IC=+0.1528, Sharpe=+1.1944
- `combo_max__max_up_ret__bb_width`: Train IC=+0.2165, Lock IC=+0.0465, Sharpe=+0.8908

**B4 Correlation Gate**: 15/20 top rejects are profitable (75%)

- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`: Train IC=+0.1943, Lock IC=+0.0837, Sharpe=+0.8417
- `combo_min__bar_body_rng_0__first_bar_return`: Train IC=+0.1936, Lock IC=+0.0873, Sharpe=+0.7078
- `combo_ifelse__gap_pct__bar_body_rng_0__bar_ret_0`: Train IC=+0.1620, Lock IC=+0.0798, Sharpe=+0.6001

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `weak_link_cv`: FP is lower (d=-0.85). Threshold 0.302 → 61% accuracy.
- `ic_cv`: FP is lower (d=-0.52). Threshold 0.199 → 61% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/42
- Decaying signal (half ratio < 0.3): 0/42
- Weak component (CV > 2.0): 1/42
- Regime-dependent (≥2 negative regimes): 0/42

### 159915ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is lower (d=-1.12). Threshold 0.845 → 75% accuracy.
- `n_negative_years`: FP is lower (d=-0.82). Threshold 1.000 → 75% accuracy.
- `recency_ratio`: FP is higher (d=+0.74). Threshold 1.335 → 85% accuracy.
- `half_ratio`: FP is higher (d=+0.60). Threshold 1.478 → 80% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/4
- Decaying signal (half ratio < 0.3): 0/4
- Weak component (CV > 2.0): 0/4
- Regime-dependent (≥2 negative regimes): 0/4

