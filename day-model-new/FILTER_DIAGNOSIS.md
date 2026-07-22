# Filter Pipeline Deep Diagnosis

**Purpose**: Understand WHY admission gates fail, using only training-period signals.
Lockbox is used solely for labeling TP/FP — all proposed fixes are training-only.

---

## 1. FP/TP Summary

| ETF | Side | Admitted | FP | TP | FP Rate |
| :--- | :--- | ---: | ---: | ---: | ---: |
| 500ETF | single | 26 | 18 | 8 | 69% |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 500ETF — `single` (FP=18, TP=8)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.527 | 0.373 | 0.541 | 0.336 | +0.83 | 0.323 | 77% |
| n_negative_years | 0.389 | 0.000 | 0.000 | 0.000 | +0.81 | 0.000 | 65% |
| recency_ratio | 0.634 | 0.853 | 0.556 | 0.836 | -0.74 | 0.162 | 65% |
| ic_std_across_regimes | 0.068 | 0.058 | 0.069 | 0.062 | +0.52 | 0.033 | 77% |
| half_ratio | 0.768 | 0.907 | 0.770 | 0.833 | -0.51 | 0.357 | 65% |
| n_negative_regimes | 0.222 | 0.125 | 0.000 | 0.000 | +0.26 | 0.000 | 65% |
| weak_link_cv | 1.464 | 1.491 | 1.135 | 1.697 | -0.04 | 0.821 | 76% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 500ETF — `single` False Positives

**`combo_mean__body_to_range_ratio__cl_pos_in_range`** (Lock IC=+0.0370, Sharpe=-1.1209)
- Yearly ICs: 2015: +0.041 | 2016: +0.102 | 2017: +0.180 | 2018: +0.085 | 2019: -0.003 | 2020: +0.078 | 2021: -0.036
- IC CV=1.03, Neg years=2/7, Half ratio=0.27, Recency ratio=0.29
- Weak component: `cl_pos_in_range` (CV=1.14, neg years=0)
- Regime ICs: Q1_low_vol=+0.128, Q2=-0.045, Q3_mid=+0.104, Q4=+0.107, Q5_high_vol=+0.031

**`combo_rank_max__max_up_ret__yesterday_return`** (Lock IC=+0.0016, Sharpe=-1.1092)
- Yearly ICs: 2015: +0.205 | 2016: +0.134 | 2017: +0.103 | 2018: +0.193 | 2019: +0.054 | 2020: +0.036 | 2021: +0.042
- IC CV=0.59, Neg years=0/7, Half ratio=0.46, Recency ratio=0.23
- Weak component: `yesterday_return` (CV=0.92, neg years=2)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.073, Q3_mid=+0.163, Q4=+0.073, Q5_high_vol=+0.248

**`combo_max__max_up_ret__roc5`** (Lock IC=+0.0401, Sharpe=-1.0757)
- Yearly ICs: 2015: +0.138 | 2016: +0.112 | 2017: +0.068 | 2018: +0.206 | 2019: +0.032 | 2020: +0.089 | 2021: +0.040
- IC CV=0.58, Neg years=0/7, Half ratio=0.54, Recency ratio=0.51
- Weak component: `roc5` (CV=1.09, neg years=1)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.010, Q3_mid=+0.137, Q4=+0.086, Q5_high_vol=+0.249

**`combo_max__max_up_ret__yesterday_return`** (Lock IC=+0.0084, Sharpe=-0.9714)
- Yearly ICs: 2015: +0.205 | 2016: +0.130 | 2017: +0.084 | 2018: +0.200 | 2019: +0.048 | 2020: +0.039 | 2021: +0.025
- IC CV=0.67, Neg years=0/7, Half ratio=0.45, Recency ratio=0.19
- Weak component: `yesterday_return` (CV=0.92, neg years=2)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.065, Q3_mid=+0.149, Q4=+0.069, Q5_high_vol=+0.260

**`combo_product__body_to_range_ratio__cl_pos_in_range`** (Lock IC=+0.0473, Sharpe=-0.7434)
- Yearly ICs: 2015: +0.273 | 2016: +0.052 | 2017: +0.194 | 2018: +0.105 | 2019: +0.035 | 2020: +0.104 | 2021: +0.139
- IC CV=0.59, Neg years=0/7, Half ratio=0.59, Recency ratio=0.75
- Weak component: `cl_pos_in_range` (CV=1.14, neg years=0)
- Regime ICs: Q1_low_vol=+0.232, Q2=+0.060, Q3_mid=+0.098, Q4=+0.078, Q5_high_vol=+0.214

**`combo_ifelse__bb_width__first_bar_return__bar_vwap_dev_2`** (Lock IC=+0.0275, Sharpe=-0.4510)
- Yearly ICs: 2015: +0.126 | 2016: +0.079 | 2017: +0.094 | 2018: +0.087 | 2019: +0.112 | 2020: +0.158 | 2021: +0.146
- IC CV=0.24, Neg years=0/7, Half ratio=1.32, Recency ratio=1.48
- Weak component: `bb_width` (CV=2.19, neg years=2)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.097, Q3_mid=+0.109, Q4=+0.083, Q5_high_vol=+0.156

**`combo_ifelse__bb_width__max_up_ret__first_30min_return`** (Lock IC=+0.0620, Sharpe=-0.4256)
- Yearly ICs: 2015: +0.140 | 2016: +0.058 | 2017: +0.167 | 2018: +0.154 | 2019: +0.079 | 2020: +0.093 | 2021: +0.148
- IC CV=0.33, Neg years=0/7, Half ratio=0.79, Recency ratio=1.22
- Weak component: `bb_width` (CV=2.19, neg years=2)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.054, Q3_mid=+0.183, Q4=+0.123, Q5_high_vol=+0.134

**`combo_diff__max_up_ret__stoch_k`** (Lock IC=+0.0032, Sharpe=-0.4252)
- Yearly ICs: 2015: +0.122 | 2016: +0.136 | 2017: +0.143 | 2018: +0.110 | 2019: +0.037 | 2020: +0.114 | 2021: +0.182
- IC CV=0.34, Neg years=0/7, Half ratio=0.90, Recency ratio=1.15
- Weak component: `stoch_k` (CV=1.39, neg years=1)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.067, Q3_mid=+0.157, Q4=+0.089, Q5_high_vol=+0.162

**`combo_ifelse__bb_width__num_up_bars__bar_body_rng_0`** (Lock IC=+0.0619, Sharpe=-0.4187)
- Yearly ICs: 2015: +0.190 | 2016: +0.140 | 2017: +0.085 | 2018: +0.180 | 2019: +0.147 | 2020: +0.121 | 2021: -0.011
- IC CV=0.52, Neg years=1/7, Half ratio=0.80, Recency ratio=0.33
- Weak component: `bb_width` (CV=2.19, neg years=2)
- Regime ICs: Q1_low_vol=+0.101, Q2=-0.043, Q3_mid=+0.169, Q4=+0.144, Q5_high_vol=+0.243

**`combo_max__max_up_ret__stoch_k`** (Lock IC=+0.0293, Sharpe=-0.3798)
- Yearly ICs: 2015: +0.158 | 2016: +0.095 | 2017: -0.004 | 2018: +0.205 | 2019: +0.089 | 2020: +0.105 | 2021: -0.070
- IC CV=1.05, Neg years=2/7, Half ratio=0.76, Recency ratio=0.14
- Weak component: `stoch_k` (CV=1.39, neg years=1)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.027, Q3_mid=+0.088, Q4=+0.121, Q5_high_vol=+0.253

**`combo_tri_median__max_up_ret__num_up_bars__bar_ret_1`** (Lock IC=+0.1110, Sharpe=-0.3356)
- Yearly ICs: 2015: +0.173 | 2016: +0.143 | 2017: +0.156 | 2018: +0.187 | 2019: +0.119 | 2020: +0.110 | 2021: +0.076
- IC CV=0.26, Neg years=0/7, Half ratio=0.75, Recency ratio=0.59
- Weak component: `bar_ret_1` (CV=0.62, neg years=1)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.047, Q3_mid=+0.178, Q4=+0.156, Q5_high_vol=+0.208

**`combo_ifelse__bb_width__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0758, Sharpe=-0.3053)
- Yearly ICs: 2015: +0.203 | 2016: +0.117 | 2017: +0.150 | 2018: +0.228 | 2019: +0.155 | 2020: +0.069 | 2021: +0.089
- IC CV=0.37, Neg years=0/7, Half ratio=0.78, Recency ratio=0.50
- Weak component: `bb_width` (CV=2.19, neg years=2)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.006, Q3_mid=+0.146, Q4=+0.158, Q5_high_vol=+0.244

**`combo_mean__max_up_ret__roc5`** (Lock IC=+0.0425, Sharpe=-0.1626)
- Yearly ICs: 2015: +0.201 | 2016: +0.069 | 2017: +0.121 | 2018: +0.179 | 2019: +0.041 | 2020: +0.091 | 2021: +0.039
- IC CV=0.56, Neg years=0/7, Half ratio=0.51, Recency ratio=0.48
- Weak component: `roc5` (CV=1.09, neg years=1)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.048, Q3_mid=+0.144, Q4=+0.067, Q5_high_vol=+0.200

**`combo_clamp_diff__max_up_ret__cl_pos_in_range`** (Lock IC=+0.0101, Sharpe=-0.1160)
- Yearly ICs: 2015: +0.187 | 2016: +0.125 | 2017: -0.027 | 2018: +0.144 | 2019: +0.074 | 2020: +0.098 | 2021: +0.067
- IC CV=0.66, Neg years=1/7, Half ratio=0.87, Recency ratio=0.53
- Weak component: `cl_pos_in_range` (CV=1.14, neg years=0)
- Regime ICs: Q1_low_vol=-0.009, Q2=+0.093, Q3_mid=+0.075, Q4=+0.041, Q5_high_vol=+0.300

**`combo_ifelse__bb_width__max_up_ret__max_down_ret`** (Lock IC=+0.0850, Sharpe=-0.1109)
- Yearly ICs: 2015: +0.256 | 2016: +0.084 | 2017: +0.144 | 2018: +0.155 | 2019: +0.108 | 2020: +0.153 | 2021: +0.120
- IC CV=0.35, Neg years=0/7, Half ratio=0.75, Recency ratio=0.81
- Weak component: `bb_width` (CV=2.19, neg years=2)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.036, Q3_mid=+0.208, Q4=+0.091, Q5_high_vol=+0.233

**`combo_clamp_diff__max_down_ret__yesterday_return`** (Lock IC=+0.0783, Sharpe=-0.0692)
- Yearly ICs: 2015: +0.149 | 2016: +0.069 | 2017: +0.194 | 2018: +0.142 | 2019: +0.069 | 2020: +0.103 | 2021: +0.089
- IC CV=0.37, Neg years=0/7, Half ratio=1.14, Recency ratio=0.88
- Weak component: `yesterday_return` (CV=0.92, neg years=2)
- Regime ICs: Q1_low_vol=+0.089, Q2=-0.011, Q3_mid=+0.073, Q4=+0.103, Q5_high_vol=+0.151

**`first_bar_return`** (Lock IC=+0.0690, Sharpe=-0.0418)
- Yearly ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099
- IC CV=0.35, Neg years=0/7, Half ratio=0.81, Recency ratio=0.58
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.025, Q3_mid=+0.141, Q4=+0.143, Q5_high_vol=+0.231

**`combo_rank_max__max_up_ret__bb_width`** (Lock IC=-0.0092, Sharpe=+0.3502)
- Yearly ICs: 2015: +0.241 | 2016: +0.089 | 2017: -0.004 | 2018: +0.237 | 2019: +0.096 | 2020: +0.145 | 2021: +0.103
- IC CV=0.62, Neg years=1/7, Half ratio=1.35, Recency ratio=0.75
- Weak component: `bb_width` (CV=2.19, neg years=2)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.065, Q3_mid=+0.138, Q4=+0.180, Q5_high_vol=+0.270

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`combo_tri_mean__max_up_ret__first_bar_return__bar_ret_1`** (Lock IC=+0.1008, Sharpe=+0.3322)
- Yearly ICs: 2015: +0.263 | 2016: +0.114 | 2017: +0.225 | 2018: +0.224 | 2019: +0.122 | 2020: +0.121 | 2021: +0.171
- IC CV=0.32, Neg years=0/7, Half ratio=0.81, Recency ratio=0.77
- Weak component: `bar_ret_1` (CV=0.62)

**`combo_ratio__max_down_ret__bb_width`** (Lock IC=+0.1238, Sharpe=+0.3124)
- Yearly ICs: 2015: +0.285 | 2016: +0.012 | 2017: +0.225 | 2018: +0.150 | 2019: +0.115 | 2020: +0.105 | 2021: +0.054
- IC CV=0.65, Neg years=0/7, Half ratio=0.60, Recency ratio=0.54
- Weak component: `bb_width` (CV=2.19)

**`combo_mean__max_up_ret__bb_width`** (Lock IC=+0.0576, Sharpe=+0.2027)
- Yearly ICs: 2015: +0.128 | 2016: +0.153 | 2017: +0.191 | 2018: +0.164 | 2019: +0.070 | 2020: +0.171 | 2021: +0.152
- IC CV=0.25, Neg years=0/7, Half ratio=1.30, Recency ratio=1.15
- Weak component: `bb_width` (CV=2.19)

**`combo_tri_max__max_up_ret__bar_body_rng_1__bar_ret_1`** (Lock IC=+0.0700, Sharpe=+0.1891)
- Yearly ICs: 2015: +0.134 | 2016: +0.110 | 2017: +0.158 | 2018: +0.138 | 2019: +0.055 | 2020: +0.123 | 2021: +0.149
- IC CV=0.26, Neg years=0/7, Half ratio=0.86, Recency ratio=1.11
- Weak component: `bar_body_rng_1` (CV=0.72)

**`combo_max__max_up_ret__bb_width`** (Lock IC=+0.0176, Sharpe=+0.1479)
- Yearly ICs: 2015: +0.235 | 2016: +0.096 | 2017: +0.019 | 2018: +0.213 | 2019: +0.108 | 2020: +0.150 | 2021: +0.116
- IC CV=0.51, Neg years=0/7, Half ratio=1.31, Recency ratio=0.80
- Weak component: `bb_width` (CV=2.19)

**`combo_tri_median__bar_ret_0__max_down_ret__bar_ret_1`** (Lock IC=+0.0996, Sharpe=+0.1192)
- Yearly ICs: 2015: +0.276 | 2016: +0.113 | 2017: +0.200 | 2018: +0.170 | 2019: +0.129 | 2020: +0.114 | 2021: +0.114
- IC CV=0.36, Neg years=0/7, Half ratio=0.80, Recency ratio=0.59
- Weak component: `bar_ret_1` (CV=0.62)

**`combo_mean__max_up_ret__capital_sell_volume`** (Lock IC=+0.0377, Sharpe=+0.0955)
- Yearly ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.147 | 2018: +0.094 | 2019: +0.063 | 2020: +0.135 | 2021: +0.170
- IC CV=0.38, Neg years=0/7, Half ratio=0.55, Recency ratio=0.87
- Weak component: `capital_sell_volume` (CV=1.20)

**`combo_ratio__max_up_ret__bb_width`** (Lock IC=+0.0574, Sharpe=+0.0841)
- Yearly ICs: 2015: +0.203 | 2016: +0.109 | 2017: +0.198 | 2018: +0.144 | 2019: +0.082 | 2020: +0.160 | 2021: +0.150
- IC CV=0.27, Neg years=0/7, Half ratio=1.03, Recency ratio=0.99
- Weak component: `bb_width` (CV=2.19)

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.707±0.072 | 0.733±0.027 | 38% | USEFUL |
| ic_ir | 0.576±0.213 | 0.669±0.054 | 22% | USEFUL |
| p_value | 0.001±0.003 | 0.000±0.001 | 21% | USEFUL |
| max_corr | 0.643±0.196 | 0.649±0.132 | 53% | WEAK |
| deflated_ic | 0.206±0.038 | 0.232±0.033 | 65% | WEAK |
| overall_ic | 0.206±0.038 | 0.232±0.034 | 66% | WEAK |
| raw_ic | 0.126±0.023 | 0.148±0.017 | 24% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 500ETF — `single`

**7-Year Jackknife**: 3/20 top rejects are profitable (15%)

- `combo_mean__max_up_ret__stoch_k`: Train IC=+0.2268, Lock IC=+0.0728, Sharpe=+0.4348
- `combo_tri_mean__max_down_ret__early_range__bar_ret_1`: Train IC=+0.2420, Lock IC=+0.0743, Sharpe=+0.3674
- `combo_tri_mean__max_up_ret__bar_body_rng_1__bar_ret_1`: Train IC=+0.2171, Lock IC=+0.0660, Sharpe=+0.2888

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `combo_rank_min__max_up_ret__stoch_k`: Train IC=+0.1568, Lock IC=+0.1236, Sharpe=+0.8166
- `combo_ifelse__bb_width__yesterday_early_vwap_dev__num_up_bars`: Train IC=+0.1680, Lock IC=+0.0838, Sharpe=+0.2497
- `combo_ifelse__bb_width__yesterday_early_vwap_dev__first_30min_return`: Train IC=+0.1661, Lock IC=+0.0498, Sharpe=+0.2219

**BH-FDR Gate**: 3/20 top rejects are profitable (15%)

- `vol_ratio_10_60`: Train IC=+0.0927, Lock IC=+0.0309, Sharpe=+0.3757
- `combo_diff__max_down_ret__roc5`: Train IC=+0.1049, Lock IC=+0.0349, Sharpe=+0.1231
- `combo_clamp_diff__max_down_ret__roc5`: Train IC=+0.1047, Lock IC=+0.0340, Sharpe=+0.1231

**B3 Composite Floor**: 2/20 top rejects are profitable (10%)

- `combo_tri_median__max_up_ret__early_range__bar_ret_1`: Train IC=+0.2295, Lock IC=+0.0667, Sharpe=+0.2838
- `combo_tri_max__max_up_ret__first_30min_return__bar_ret_1`: Train IC=+0.2328, Lock IC=+0.0693, Sharpe=+0.0995

**B4 Correlation Gate**: 3/20 top rejects are profitable (15%)

- `combo_tri_mean__max_up_ret__bar_ret_0__bar_ret_1`: Train IC=+0.2711, Lock IC=+0.1008, Sharpe=+0.3322
- `combo_tri_median__first_bar_return__max_down_ret__bar_ret_1`: Train IC=+0.2558, Lock IC=+0.0996, Sharpe=+0.1192
- `combo_tri_mean__first_bar_return__max_down_ret__bar_ret_1`: Train IC=+0.2465, Lock IC=+0.1133, Sharpe=+0.0419

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is higher (d=+0.83). Threshold 0.323 → 77% accuracy.
- `n_negative_years`: FP is higher (d=+0.81). Threshold 0.000 → 65% accuracy.
- `recency_ratio`: FP is lower (d=-0.74). Threshold 0.162 → 65% accuracy.
- `ic_std_across_regimes`: FP is higher (d=+0.52). Threshold 0.033 → 77% accuracy.
- `half_ratio`: FP is lower (d=-0.51). Threshold 0.357 → 65% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/18
- Decaying signal (half ratio < 0.3): 1/18
- Weak component (CV > 2.0): 6/18
- Regime-dependent (≥2 negative regimes): 0/18

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `num_up_bars` | 2 | 0 | 2 | 100% |  |
| `bar_body_rng_0` | 2 | 0 | 2 | 100% |  |
| `roc5` | 2 | 0 | 2 | 100% |  |
| `stoch_k` | 2 | 0 | 2 | 100% |  |
| `cl_pos_in_range` | 3 | 0 | 3 | 100% |  |
| `body_to_range_ratio` | 2 | 0 | 2 | 100% |  |
| `yesterday_return` | 3 | 0 | 3 | 100% |  |
| `max_up_ret` | 11 | 6 | 17 | 65% |  |
| `bb_width` | 6 | 4 | 10 | 60% |  |
| `first_bar_return` | 1 | 1 | 2 | 50% |  |
| `max_down_ret` | 2 | 2 | 4 | 50% |  |
| `bar_ret_0` | 1 | 1 | 2 | 50% |  |
| `bar_ret_1` | 1 | 3 | 4 | 25% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=7, TP=3, FP rate=70%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=9, TP=2, FP rate=82%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=3, FP rate=25%

