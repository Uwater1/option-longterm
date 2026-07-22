# Filter Pipeline Deep Diagnosis

**Purpose**: Understand WHY admission gates fail, using only training-period signals.
Lockbox is used solely for labeling TP/FP — all proposed fixes are training-only.

---

## 1. FP/TP Summary

| ETF | Side | Admitted | FP | TP | FP Rate |
| :--- | :--- | ---: | ---: | ---: | ---: |
| 300ETF | single | 1 | 1 | 0 | 100% |
| 500ETF | single | 31 | 14 | 17 | 45% |
| 159915ETF | single | 12 | 2 | 10 | 17% |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 500ETF — `single` (FP=14, TP=17)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_std_across_regimes | 0.067 | 0.059 | 0.068 | 0.058 | +0.47 | 0.057 | 65% |
| recency_ratio | 0.698 | 0.769 | 0.580 | 0.748 | -0.35 | 0.803 | 58% |
| ic_cv | 0.460 | 0.502 | 0.437 | 0.476 | -0.26 | 0.786 | 55% |
| n_negative_regimes | 0.286 | 0.235 | 0.000 | 0.000 | +0.12 | 0.500 | 55% |
| n_negative_years | 0.143 | 0.176 | 0.000 | 0.000 | -0.09 | 0.500 | 52% |
| weak_link_cv | 1.112 | 1.133 | 1.291 | 1.291 | -0.05 | 1.811 | 58% |
| half_ratio | 0.784 | 0.785 | 0.733 | 0.765 | -0.00 | 0.896 | 61% |

### 159915ETF — `single` (FP=2, TP=10)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.300 | 0.522 | 0.300 | 0.466 | -1.73 | 0.833 | 75% |
| weak_link_cv | 1.370 | 1.172 | 1.370 | 1.311 | +1.06 | 1.370 | 75% |
| n_negative_years | 0.000 | 0.200 | 0.000 | 0.000 | -0.71 | 1.000 | 75% |
| recency_ratio | 0.886 | 0.755 | 0.886 | 0.741 | +0.67 | 0.790 | 75% |
| n_negative_regimes | 0.000 | 0.100 | 0.000 | 0.000 | -0.47 | 0.500 | 75% |
| half_ratio | 0.992 | 1.034 | 0.992 | 0.966 | -0.18 | 1.501 | 75% |
| ic_std_across_regimes | 0.049 | 0.051 | 0.049 | 0.045 | -0.12 | 0.086 | 75% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_diff__short_sell_quantity__roc60`** (Lock IC=-0.0007, Sharpe=+0.5778)
- Yearly ICs: 2015: +0.089 | 2016: +0.084 | 2017: +0.068 | 2018: +0.063 | 2019: +0.039 | 2020: +0.017 | 2021: +0.067
- IC CV=0.38, Neg years=0/7, Half ratio=0.16, Recency ratio=0.49
- Weak component: `short_sell_quantity` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.013, Q2=-0.008, Q3_mid=-0.058, Q4=+0.075, Q5_high_vol=+0.086

### 500ETF — `single` False Positives

**`combo_diff__yesterday_early_momentum__yesterday_day_skew`** (Lock IC=+0.0263, Sharpe=-1.0382)
- Yearly ICs: 2015: +0.038 | 2016: +0.092 | 2017: +0.037 | 2018: +0.060 | 2019: +0.045 | 2020: +0.149 | 2021: -0.024
- IC CV=0.88, Neg years=1/7, Half ratio=0.61, Recency ratio=0.95
- Weak component: `yesterday_day_skew` (CV=2.33, neg years=2)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.061, Q3_mid=+0.070, Q4=+0.130, Q5_high_vol=+0.080

**`combo_rank_min__max_up_ret__bar_vwap_dev_2`** (Lock IC=+0.0745, Sharpe=-0.9201)
- Yearly ICs: 2015: +0.198 | 2016: +0.015 | 2017: +0.150 | 2018: +0.124 | 2019: +0.130 | 2020: +0.117 | 2021: +0.108
- IC CV=0.43, Neg years=0/7, Half ratio=0.99, Recency ratio=1.05
- Weak component: `bar_vwap_dev_2` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.074, Q3_mid=+0.127, Q4=+0.095, Q5_high_vol=+0.192

**`combo_ifelse__gap_pct__first_30min_return__num_up_bars`** (Lock IC=+0.0635, Sharpe=-0.8721)
- Yearly ICs: 2015: +0.105 | 2016: +0.074 | 2017: +0.041 | 2018: +0.162 | 2019: +0.081 | 2020: +0.083 | 2021: +0.086
- IC CV=0.38, Neg years=0/7, Half ratio=0.98, Recency ratio=0.95
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.114, Q2=-0.029, Q3_mid=+0.187, Q4=+0.123, Q5_high_vol=+0.107

**`combo_ifelse__gap_pct__bar_ret_0__num_up_bars`** (Lock IC=+0.0782, Sharpe=-0.8694)
- Yearly ICs: 2015: +0.184 | 2016: +0.070 | 2017: +0.009 | 2018: +0.233 | 2019: +0.142 | 2020: +0.104 | 2021: +0.103
- IC CV=0.57, Neg years=0/7, Half ratio=1.16, Recency ratio=0.81
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.142, Q2=-0.069, Q3_mid=+0.217, Q4=+0.134, Q5_high_vol=+0.202

**`combo_mean__max_down_ret__bar_vwap_dev_2`** (Lock IC=+0.0660, Sharpe=-0.7547)
- Yearly ICs: 2015: +0.225 | 2016: -0.009 | 2017: +0.162 | 2018: +0.104 | 2019: +0.126 | 2020: +0.131 | 2021: +0.086
- IC CV=0.56, Neg years=1/7, Half ratio=1.03, Recency ratio=1.01
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.062, Q3_mid=+0.121, Q4=+0.054, Q5_high_vol=+0.212

**`combo_mean__max_up_ret__body_to_range_ratio`** (Lock IC=+0.0634, Sharpe=-0.7138)
- Yearly ICs: 2015: +0.187 | 2016: +0.157 | 2017: +0.217 | 2018: +0.183 | 2019: +0.068 | 2020: +0.158 | 2021: +0.019
- IC CV=0.47, Neg years=0/7, Half ratio=0.54, Recency ratio=0.51
- Weak component: `body_to_range_ratio` (CV=0.79, neg years=1)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.007, Q3_mid=+0.184, Q4=+0.161, Q5_high_vol=+0.213

**`combo_rank_min__max_down_ret__first_30min_return`** (Lock IC=+0.0996, Sharpe=-0.4745)
- Yearly ICs: 2015: +0.269 | 2016: +0.100 | 2017: +0.252 | 2018: +0.137 | 2019: +0.112 | 2020: +0.135 | 2021: +0.059
- IC CV=0.48, Neg years=0/7, Half ratio=0.73, Recency ratio=0.53
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.200, Q2=-0.022, Q3_mid=+0.147, Q4=+0.108, Q5_high_vol=+0.221

**`combo_tri_max__max_up_ret__max_down_ret__num_up_bars`** (Lock IC=+0.0782, Sharpe=-0.4143)
- Yearly ICs: 2015: +0.204 | 2016: +0.142 | 2017: +0.110 | 2018: +0.243 | 2019: +0.091 | 2020: +0.114 | 2021: +0.071
- IC CV=0.42, Neg years=0/7, Half ratio=0.74, Recency ratio=0.53
- Weak component: `max_down_ret` (CV=0.55, neg years=0)
- Regime ICs: Q1_low_vol=+0.153, Q2=-0.008, Q3_mid=+0.164, Q4=+0.179, Q5_high_vol=+0.241

**`combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0607, Sharpe=-0.3849)
- Yearly ICs: 2015: +0.220 | 2016: +0.150 | 2017: +0.150 | 2018: +0.156 | 2019: +0.110 | 2020: +0.111 | 2021: +0.104
- IC CV=0.26, Neg years=0/7, Half ratio=0.76, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.049, Q3_mid=+0.143, Q4=+0.176, Q5_high_vol=+0.259

**`combo_ifelse__gap_pct__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0605, Sharpe=-0.2036)
- Yearly ICs: 2015: +0.228 | 2016: +0.104 | 2017: +0.160 | 2018: +0.203 | 2019: +0.141 | 2020: +0.093 | 2021: +0.099
- IC CV=0.34, Neg years=0/7, Half ratio=0.91, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.019, Q3_mid=+0.139, Q4=+0.159, Q5_high_vol=+0.252

**`combo_max__max_up_ret__gap_pct`** (Lock IC=+0.0931, Sharpe=-0.1976)
- Yearly ICs: 2015: +0.221 | 2016: +0.115 | 2017: +0.167 | 2018: +0.286 | 2019: +0.088 | 2020: +0.095 | 2021: +0.033
- IC CV=0.56, Neg years=0/7, Half ratio=0.56, Recency ratio=0.38
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.113, Q3_mid=+0.154, Q4=+0.114, Q5_high_vol=+0.285

**`combo_ifelse__gap_pct__max_up_ret__bar_ret_0`** (Lock IC=+0.0663, Sharpe=-0.1682)
- Yearly ICs: 2015: +0.201 | 2016: +0.157 | 2017: +0.138 | 2018: +0.174 | 2019: +0.111 | 2020: +0.113 | 2021: +0.094
- IC CV=0.25, Neg years=0/7, Half ratio=0.71, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.29, neg years=1)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.067, Q3_mid=+0.133, Q4=+0.159, Q5_high_vol=+0.241

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

### 159915ETF — `single` False Positives

**`combo_ifelse__gap_pct__max_up_ret__early_range`** (Lock IC=+0.0511, Sharpe=-0.2340)
- Yearly ICs: 2015: +0.134 | 2016: +0.092 | 2017: +0.062 | 2018: +0.118 | 2019: +0.132 | 2020: +0.129 | 2021: +0.092
- IC CV=0.23, Neg years=0/7, Half ratio=0.99, Recency ratio=0.98
- Weak component: `gap_pct` (CV=1.37, neg years=2)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.185, Q3_mid=+0.112, Q4=+0.202, Q5_high_vol=+0.099

**`combo_ifelse__gap_pct__max_up_ret__bar_vol_5`** (Lock IC=+0.0729, Sharpe=-0.0801)
- Yearly ICs: 2015: +0.163 | 2016: +0.104 | 2017: +0.053 | 2018: +0.095 | 2019: +0.182 | 2020: +0.131 | 2021: +0.081
- IC CV=0.37, Neg years=0/7, Half ratio=1.00, Recency ratio=0.79
- Weak component: `gap_pct` (CV=1.37, neg years=2)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.156, Q3_mid=+0.153, Q4=+0.193, Q5_high_vol=+0.113

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`combo_min__max_up_ret__gap_pct`** (Lock IC=+0.1222, Sharpe=+0.9246)
- Yearly ICs: 2015: +0.227 | 2016: +0.110 | 2017: +0.203 | 2018: +0.028 | 2019: +0.139 | 2020: +0.140 | 2021: +0.121
- IC CV=0.44, Neg years=0/7, Half ratio=0.62, Recency ratio=0.77
- Weak component: `gap_pct` (CV=1.29)

**`combo_rank_min__max_up_ret__gap_pct`** (Lock IC=+0.1302, Sharpe=+0.8964)
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

**`combo_ifelse__gap_pct__max_up_ret__max_down_ret`** (Lock IC=+0.1086, Sharpe=+0.4535)
- Yearly ICs: 2015: +0.273 | 2016: +0.141 | 2017: +0.132 | 2018: +0.093 | 2019: +0.133 | 2020: +0.166 | 2021: +0.073
- IC CV=0.41, Neg years=0/7, Half ratio=0.83, Recency ratio=0.58
- Weak component: `gap_pct` (CV=1.29)

**`combo_rank_max__max_down_ret__bar_body_rng_0`** (Lock IC=+0.1067, Sharpe=+0.4291)
- Yearly ICs: 2015: +0.275 | 2016: +0.109 | 2017: +0.217 | 2018: +0.187 | 2019: +0.148 | 2020: +0.129 | 2021: +0.103
- IC CV=0.35, Neg years=0/7, Half ratio=0.87, Recency ratio=0.61
- Weak component: `max_down_ret` (CV=0.55)

**`combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_vwap_dev_2`** (Lock IC=+0.0700, Sharpe=+0.3163)
- Yearly ICs: 2015: +0.130 | 2016: +0.094 | 2017: +0.120 | 2018: +0.050 | 2019: +0.153 | 2020: +0.162 | 2021: -0.015
- IC CV=0.59, Neg years=1/7, Half ratio=0.70, Recency ratio=0.66
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

**`combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_body_rng_0`** (Lock IC=+0.0691, Sharpe=+0.1687)
- Yearly ICs: 2015: +0.116 | 2016: +0.117 | 2017: +0.167 | 2018: +0.124 | 2019: +0.109 | 2020: +0.146 | 2021: +0.024
- IC CV=0.36, Neg years=0/7, Half ratio=0.88, Recency ratio=0.73
- Weak component: `gap_pct` (CV=1.29)

**`combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud`** (Lock IC=+0.0279, Sharpe=+0.0586)
- Yearly ICs: 2015: +0.066 | 2016: +0.050 | 2017: +0.161 | 2018: +0.057 | 2019: +0.029 | 2020: +0.179 | 2021: -0.041
- IC CV=0.98, Neg years=1/7, Half ratio=0.67, Recency ratio=1.20
- Weak component: `yesterday_illiquidity_amihud` (CV=1.29)

**`combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars`** (Lock IC=+0.0861, Sharpe=+0.0453)
- Yearly ICs: 2015: +0.084 | 2016: +0.081 | 2017: +0.035 | 2018: +0.142 | 2019: +0.106 | 2020: +0.139 | 2021: +0.020
- IC CV=0.50, Neg years=0/7, Half ratio=1.16, Recency ratio=0.96
- Weak component: `gap_pct` (CV=1.29)

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0856, Sharpe=+0.0245)
- Yearly ICs: 2015: +0.227 | 2016: +0.099 | 2017: +0.263 | 2018: +0.229 | 2019: +0.143 | 2020: +0.129 | 2021: +0.080
- IC CV=0.40, Neg years=0/7, Half ratio=0.78, Recency ratio=0.64
- Weak component: `max_down_ret` (CV=0.55)

**`combo_ifelse__gap_pct__max_up_ret__first_30min_return`** (Lock IC=+0.0858, Sharpe=+0.0042)
- Yearly ICs: 2015: +0.208 | 2016: +0.096 | 2017: +0.139 | 2018: +0.127 | 2019: +0.107 | 2020: +0.136 | 2021: +0.096
- IC CV=0.28, Neg years=0/7, Half ratio=0.77, Recency ratio=0.76
- Weak component: `gap_pct` (CV=1.29)

### 159915ETF — `single` True Positives

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

**`combo_ifelse__bb_width__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0731, Sharpe=+0.6021)
- Yearly ICs: 2015: +0.204 | 2016: +0.121 | 2017: +0.020 | 2018: +0.129 | 2019: +0.200 | 2020: +0.120 | 2021: +0.134
- IC CV=0.43, Neg years=0/7, Half ratio=1.38, Recency ratio=0.78
- Weak component: `bb_width` (CV=1.25)

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

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.725±0.050 | 0.682±0.049 | 52% | WEAK |
| ic_ir | 0.608±0.142 | 0.537±0.133 | 69% | WEAK |
| p_value | 0.000±0.001 | 0.001±0.001 | 65% | WEAK |
| max_corr | 0.767±0.110 | 0.661±0.128 | 87% | USELESS |
| deflated_ic | 0.222±0.034 | 0.221±0.040 | 79% | WEAK |
| overall_ic | 0.222±0.034 | 0.221±0.040 | 79% | WEAK |
| raw_ic | 0.136±0.023 | 0.122±0.031 | 68% | WEAK |

### 159915ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.753±0.058 | 0.685±0.034 | 26% | USEFUL |
| ic_ir | 0.784±0.188 | 0.494±0.092 | 3% | USEFUL |
| p_value | 0.000±0.000 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.656±0.046 | 0.670±0.185 | 17% | USEFUL |
| deflated_ic | 0.190±0.001 | 0.206±0.029 | 3% | USEFUL |
| overall_ic | 0.191±0.002 | 0.208±0.029 | 4% | USEFUL |
| raw_ic | 0.133±0.001 | 0.131±0.011 | 5% | USEFUL |

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

**B4 Correlation Gate**: 1/2 top rejects are profitable (50%)

- `combo_diff__short_sell_quantity__sma100_dist`: Train IC=+0.1484, Lock IC=+0.0220, Sharpe=+0.8087

### 500ETF — `single`

**7-Year Jackknife**: 1/20 top rejects are profitable (5%)

- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum`: Train IC=+0.2464, Lock IC=+0.0560, Sharpe=+0.6438

**B2 Rolling Guard**: 1/20 top rejects are profitable (5%)

- `combo_mean__max_down_ret__num_up_bars`: Train IC=+0.1617, Lock IC=+0.0992, Sharpe=+0.1165

**BH-FDR Gate**: 3/20 top rejects are profitable (15%)

- `combo_min__first_30min_return__gap_pct`: Train IC=+0.1475, Lock IC=+0.0989, Sharpe=+0.3067
- `combo_rank_max__max_down_ret__bar_body_rng_1`: Train IC=+0.1453, Lock IC=+0.0913, Sharpe=+0.1859
- `first_30min_return`: Train IC=+0.1461, Lock IC=+0.0708, Sharpe=+0.1356

**B4 Correlation Gate**: 3/20 top rejects are profitable (15%)

- `combo_ifelse__gap_pct__bar_ret_0__max_down_ret`: Train IC=+0.2581, Lock IC=+0.1099, Sharpe=+0.5744
- `combo_ifelse__gap_pct__first_bar_return__max_down_ret`: Train IC=+0.2578, Lock IC=+0.1097, Sharpe=+0.5744
- `combo_rank_min__max_up_ret__yesterday_illiquidity_amihud`: Train IC=+0.2527, Lock IC=+0.0152, Sharpe=+0.3461

### 159915ETF — `single`

**B2 Rolling Guard**: 5/20 top rejects are profitable (25%)

- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2106, Lock IC=+0.1310, Sharpe=+1.2087
- `combo_rank_min__max_up_ret__max_down_ret`: Train IC=+0.2204, Lock IC=+0.0988, Sharpe=+0.7200
- `combo_rank_max__bar_body_rng_0__max_down_ret`: Train IC=+0.1938, Lock IC=+0.0875, Sharpe=+0.5045

**BH-FDR Gate**: 7/20 top rejects are profitable (35%)

- `combo_ifelse__gap_pct__bar_body_rng_0__bar_ret_0`: Train IC=+0.1620, Lock IC=+0.0798, Sharpe=+0.6001
- `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return`: Train IC=+0.1616, Lock IC=+0.0797, Sharpe=+0.6001
- `combo_tri_median__max_up_ret__bar_body_rng_0__bar_ret_0`: Train IC=+0.1635, Lock IC=+0.0795, Sharpe=+0.3644

**B3 Composite Floor**: 2/20 top rejects are profitable (10%)

- `combo_mean__max_up_ret__gap_pct`: Train IC=+0.2287, Lock IC=+0.1505, Sharpe=+1.0973
- `combo_rank_min__max_up_ret__gap_pct`: Train IC=+0.2544, Lock IC=+0.1252, Sharpe=+0.9217

**B4 Correlation Gate**: 9/19 top rejects are profitable (47%)

- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`: Train IC=+0.1943, Lock IC=+0.0837, Sharpe=+0.7716
- `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_early_vwap_dev`: Train IC=+0.1810, Lock IC=+0.0932, Sharpe=+0.5611
- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend`: Train IC=+0.1915, Lock IC=+0.0734, Sharpe=+0.4170

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 500ETF — `single`

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/14
- Decaying signal (half ratio < 0.3): 0/14
- Weak component (CV > 2.0): 1/14
- Regime-dependent (≥2 negative regimes): 0/14

### 159915ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is lower (d=-1.73). Threshold 0.833 → 75% accuracy.
- `weak_link_cv`: FP is higher (d=+1.06). Threshold 1.370 → 75% accuracy.
- `n_negative_years`: FP is lower (d=-0.71). Threshold 1.000 → 75% accuracy.
- `recency_ratio`: FP is higher (d=+0.67). Threshold 0.790 → 75% accuracy.

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
| `bar_vwap_dev_2` | 3 | 1 | 4 | 75% |  |
| `bar_ret_0` | 2 | 1 | 3 | 67% |  |
| `num_up_bars` | 3 | 2 | 5 | 60% |  |
| `bar_vol_5` | 1 | 1 | 2 | 50% |  |
| `max_up_ret` | 10 | 10 | 20 | 50% |  |
| `body_to_range_ratio` | 1 | 1 | 2 | 50% |  |
| `max_down_ret` | 3 | 4 | 7 | 43% |  |
| `first_30min_return` | 2 | 3 | 5 | 40% |  |
| `gap_pct` | 9 | 18 | 27 | 33% |  |
| `early_range` | 1 | 2 | 3 | 33% |  |
| `yesterday_illiquidity_amihud` | 1 | 3 | 4 | 25% |  |
| `bar_body_rng_0` | 2 | 6 | 8 | 25% |  |
| `first_bar_return` | 1 | 4 | 5 | 20% |  |
| `yesterday_early_momentum` | 1 | 4 | 5 | 20% |  |
| `yesterday_day_vwap_dev` | 0 | 2 | 2 | 0% |  |
| `bb_width` | 0 | 2 | 2 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 4 | 4 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=6, TP=6, FP rate=50%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=10, TP=21, FP rate=32%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=0, FP rate=100%

