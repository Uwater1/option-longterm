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
| 300ETF | single | 19 | 5 | 2 | 12 | 26% | 0.52 |
| 500ETF | single | 29 | 0 | 4 | 25 | 0% | 0.86 |
| 159915ETF | single | 17 | 1 | 2 | 14 | 6% | 0.81 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=5, TP=12)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.957 | 0.697 | 0.876 | 0.673 | +1.73 | 0.839 | 88% |
| half_ratio | 1.149 | 0.796 | 1.087 | 0.805 | +1.10 | 1.035 | 82% |
| recency_ratio | 7.031 | -0.463 | 3.240 | 1.917 | +0.75 | 2.542 | 76% |
| n_negative_regimes | 0.200 | 0.000 | 0.000 | 0.000 | +0.71 | 0.500 | 76% |
| n_negative_years | 1.000 | 0.667 | 1.000 | 1.000 | +0.60 | 1.500 | 76% |
| ic_std_across_regimes | 0.049 | 0.043 | 0.049 | 0.039 | +0.56 | 0.054 | 76% |
| weak_link_cv | 1.019 | 1.135 | 1.106 | 1.009 | -0.36 | 1.086 | 71% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_min__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0067, Sharpe=-1.0941)
- Admission: Train IC=+0.2421, Deflated=+0.2414, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.078 | 2017: -0.031 | 2018: +0.196 | 2019: +0.082 | 2020: +0.055 | 2021: +0.168 | 2022: +0.001 | 2023: +0.150 | 2024: +0.058 | 2025: +0.034 | 2026: -0.172
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.232 | 2017: +0.132 | 2018: +0.376 | 2019: +0.322 | 2020: +0.219 | 2021: +0.353 | 2022: +0.117 | 2023: +0.249 | 2024: +0.232 | 2025: -0.113 | 2026: -0.149
- IC CV=0.86, Neg years (linear/tail)=1/0 of 8, Half ratio=1.09, Recency ratio=3.24
- Early IC=+0.0233, Recent IC=+0.0754, 1st-half IC=+0.0861, 2nd-half IC=+0.0936, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89, neg years=1)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.077, Q3_mid=+0.080, Q4=+0.032, Q5_high_vol=+0.212

**`combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=-0.0158, Sharpe=-1.0471)
- Admission: Train IC=+0.1287, Deflated=+0.1304, IR=0.55, Mono=0.71, p=0.0110, MaxCorr=0.54
- Yearly Linear ICs: 2015: -0.041 | 2016: -0.001 | 2017: +0.004 | 2018: +0.097 | 2019: +0.073 | 2020: +0.010 | 2021: +0.063 | 2022: +0.018 | 2023: +0.047 | 2024: -0.007 | 2025: +0.032 | 2026: -0.133
- Yearly Tail ICs:   2015: +0.075 | 2016: -0.008 | 2017: +0.221 | 2018: +0.166 | 2019: +0.172 | 2020: +0.069 | 2021: +0.225 | 2022: +0.051 | 2023: +0.165 | 2024: +0.013 | 2025: +0.061 | 2026: -0.274
- IC CV=0.88, Neg years (linear/tail)=1/1 of 8, Half ratio=0.77, Recency ratio=20.36
- Early IC=+0.0016, Recent IC=+0.0323, 1st-half IC=+0.0466, 2nd-half IC=+0.0359, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.015, Q3_mid=+0.006, Q4=+0.090, Q5_high_vol=+0.032

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0023, Sharpe=-0.5759)
- Admission: Train IC=+0.2524, Deflated=+0.2527, IR=0.86, Mono=0.81, p=0.0000, MaxCorr=0.52
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.037 | 2017: +0.040 | 2018: +0.154 | 2019: +0.041 | 2020: +0.015 | 2021: +0.191 | 2022: +0.037 | 2023: +0.200 | 2024: +0.042 | 2025: +0.105 | 2026: -0.208
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.160 | 2017: +0.186 | 2018: +0.475 | 2019: +0.255 | 2020: +0.206 | 2021: +0.326 | 2022: +0.202 | 2023: +0.220 | 2024: +0.125 | 2025: +0.154 | 2026: -0.448
- IC CV=0.82, Neg years (linear/tail)=0/0 of 8, Half ratio=1.74, Recency ratio=3.10
- Early IC=+0.0382, Recent IC=+0.1184, 1st-half IC=+0.0644, 2nd-half IC=+0.1117, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.096, Q3_mid=+0.070, Q4=+0.032, Q5_high_vol=+0.169

**`combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0131, Sharpe=-0.5701)
- Admission: Train IC=+0.1892, Deflated=+0.1892, IR=0.71, Mono=0.76, p=0.0002, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.087 | 2016: +0.065 | 2017: -0.025 | 2018: +0.158 | 2019: +0.063 | 2020: -0.011 | 2021: +0.164 | 2022: +0.069 | 2023: +0.192 | 2024: +0.010 | 2025: +0.095 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.097 | 2017: +0.128 | 2018: +0.352 | 2019: +0.151 | 2020: +0.030 | 2021: +0.404 | 2022: +0.227 | 2023: +0.218 | 2024: +0.175 | 2025: +0.194 | 2026: -0.148
- IC CV=0.90, Neg years (linear/tail)=2/0 of 8, Half ratio=1.54, Recency ratio=6.91
- Early IC=+0.0188, Recent IC=+0.1298, 1st-half IC=+0.0700, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11, neg years=1)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.104, Q3_mid=+0.062, Q4=+0.036, Q5_high_vol=+0.196

**`combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0099, Sharpe=-0.2153)
- Admission: Train IC=+0.1604, Deflated=+0.1602, IR=0.61, Mono=0.70, p=0.0014, MaxCorr=0.39
- Yearly Linear ICs: 2015: +0.053 | 2016: +0.047 | 2017: +0.035 | 2018: +0.008 | 2019: +0.070 | 2020: +0.042 | 2021: -0.061 | 2022: +0.025 | 2023: +0.101 | 2024: +0.100 | 2025: -0.179 | 2026: +0.057
- Yearly Tail ICs:   2015: -0.001 | 2016: +0.058 | 2017: +0.094 | 2018: +0.213 | 2019: +0.325 | 2020: +0.221 | 2021: -0.003 | 2022: +0.123 | 2023: +0.396 | 2024: +0.067 | 2025: -0.250 | 2026: +0.053
- IC CV=1.33, Neg years (linear/tail)=1/1 of 8, Half ratio=0.61, Recency ratio=1.54
- Early IC=+0.0409, Recent IC=+0.0632, 1st-half IC=+0.0384, 2nd-half IC=+0.0235, Neg regimes=1/5
- Weak component: `max_up_ret` (CV=0.89, neg years=1)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.017, Q3_mid=-0.057, Q4=+0.065, Q5_high_vol=+0.085

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0273, Sharpe=+0.1690)
- Admission: Train IC=+0.1678, Deflated=+0.1664, IR=0.44, Mono=0.66, p=0.0016, MaxCorr=0.39
- Yearly Linear ICs: 2015: +0.047 | 2016: +0.053 | 2017: +0.103 | 2018: +0.108 | 2019: +0.010 | 2020: +0.088 | 2021: +0.048 | 2022: +0.028 | 2023: +0.071 | 2024: -0.053 | 2025: -0.030 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.000 | 2016: +0.193 | 2017: -0.004 | 2018: +0.270 | 2019: +0.043 | 2020: +0.052 | 2021: +0.168 | 2022: +0.246 | 2023: +0.195 | 2024: +0.053 | 2025: +0.098 | 2026: -0.157
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.75, Recency ratio=0.64
- Early IC=+0.0779, Recent IC=+0.0497, 1st-half IC=+0.0798, 2nd-half IC=+0.0599, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=-0.003, Q3_mid=+0.061, Q4=+0.073, Q5_high_vol=+0.070

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`** (Lock IC=+0.0288, Sharpe=-0.2338)
- Admission: Train IC=+0.1591, Deflated=+0.1593, IR=0.48, Mono=0.69, p=0.0016, MaxCorr=0.59
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.086 | 2017: +0.035 | 2018: +0.110 | 2019: +0.038 | 2020: -0.014 | 2021: +0.179 | 2022: +0.091 | 2023: +0.059 | 2024: -0.063 | 2025: +0.068 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.201 | 2016: +0.171 | 2017: +0.155 | 2018: +0.354 | 2019: +0.021 | 2020: -0.099 | 2021: +0.264 | 2022: +0.124 | 2023: +0.129 | 2024: +0.017 | 2025: +0.105 | 2026: +0.319
- IC CV=0.74, Neg years (linear/tail)=1/1 of 8, Half ratio=1.21, Recency ratio=1.24
- Early IC=+0.0603, Recent IC=+0.0749, 1st-half IC=+0.0709, 2nd-half IC=+0.0854, Neg regimes=0/5
- Weak component: `bar_vol_0` (CV=2.19)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.034, Q3_mid=+0.028, Q4=+0.012, Q5_high_vol=+0.163

**`combo_rank_min__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0141, Sharpe=-0.2026)
- Admission: Train IC=+0.2157, Deflated=+0.2161, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.074 | 2017: +0.013 | 2018: +0.217 | 2019: +0.066 | 2020: -0.039 | 2021: +0.156 | 2022: +0.061 | 2023: +0.186 | 2024: +0.004 | 2025: +0.096 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.070 | 2016: -0.007 | 2017: -0.036 | 2018: +0.313 | 2019: +0.138 | 2020: +0.027 | 2021: +0.416 | 2022: +0.325 | 2023: +0.493 | 2024: -0.008 | 2025: +0.141 | 2026: -0.014
- IC CV=0.89, Neg years (linear/tail)=1/1 of 8, Half ratio=0.89, Recency ratio=2.80
- Early IC=+0.0447, Recent IC=+0.1251, 1st-half IC=+0.1036, 2nd-half IC=+0.0919, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.120, Q3_mid=+0.076, Q4=+0.059, Q5_high_vol=+0.145

### 500ETF — `single` Median Features

**`combo_sig_product__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.1148, Sharpe=-0.0882)
- Admission: Train IC=+0.1747, Deflated=+0.1744, IR=0.40, Mono=0.66, p=0.0002, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.052 | 2017: +0.232 | 2018: +0.062 | 2019: +0.076 | 2020: +0.101 | 2021: +0.081 | 2022: +0.076 | 2023: +0.077 | 2024: +0.154 | 2025: +0.078 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.142 | 2016: +0.004 | 2017: +0.239 | 2018: +0.111 | 2019: +0.168 | 2020: +0.216 | 2021: +0.089 | 2022: +0.055 | 2023: +0.219 | 2024: +0.218 | 2025: -0.026 | 2026: +0.031
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.54
- Early IC=+0.1421, Recent IC=+0.0766, 1st-half IC=+0.1015, 2nd-half IC=+0.0857, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.036, Q3_mid=+0.100, Q4=+0.073, Q5_high_vol=+0.092

**`vwap_trend_channel_slope`** (Lock IC=+0.0712, Sharpe=-0.3626)
- Admission: Train IC=+0.1436, Deflated=+0.1423, IR=0.46, Mono=0.65, p=0.0058, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.90
- Early IC=+0.1028, Recent IC=+0.0926, 1st-half IC=+0.0798, 2nd-half IC=+0.0888, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.007, Q3_mid=+0.088, Q4=+0.063, Q5_high_vol=+0.120

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0586, Sharpe=-0.0789)
- Admission: Train IC=+0.2446, Deflated=+0.2452, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.125 | 2017: +0.154 | 2018: +0.226 | 2019: +0.083 | 2020: +0.134 | 2021: +0.102 | 2022: +0.108 | 2023: +0.080 | 2024: +0.126 | 2025: +0.122 | 2026: -0.123
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.099 | 2017: +0.215 | 2018: +0.264 | 2019: +0.075 | 2020: +0.348 | 2021: +0.179 | 2022: +0.303 | 2023: +0.395 | 2024: +0.216 | 2025: -0.102 | 2026: -0.544
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.67
- Early IC=+0.1414, Recent IC=+0.0945, 1st-half IC=+0.1449, 2nd-half IC=+0.1071, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.012, Q3_mid=+0.126, Q4=+0.163, Q5_high_vol=+0.157

**`combo_diff__bar_ret_0__max_down_ret`** (Lock IC=+0.0120, Sharpe=-0.8026)
- Admission: Train IC=+0.1682, Deflated=+0.1692, IR=0.40, Mono=0.66, p=0.0008, MaxCorr=0.44
- Yearly Linear ICs: 2015: -0.046 | 2016: +0.147 | 2017: +0.004 | 2018: +0.205 | 2019: +0.060 | 2020: +0.043 | 2021: +0.065 | 2022: +0.004 | 2023: +0.029 | 2024: +0.003 | 2025: +0.052 | 2026: -0.020
- Yearly Tail ICs:   2015: -0.114 | 2016: +0.052 | 2017: +0.039 | 2018: +0.403 | 2019: +0.107 | 2020: +0.168 | 2021: +0.077 | 2022: +0.146 | 2023: +0.158 | 2024: +0.036 | 2025: -0.006 | 2026: +0.061
- IC CV=0.95, Neg years (linear/tail)=0/0 of 8, Half ratio=0.34, Recency ratio=0.22
- Early IC=+0.0753, Recent IC=+0.0168, 1st-half IC=+0.1043, 2nd-half IC=+0.0355, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.030, Q3_mid=+0.011, Q4=+0.102, Q5_high_vol=+0.127

### 159915ETF — `single` Median Features

**`net_volume_flow`** (Lock IC=+0.0976, Sharpe=-0.0344)
- Admission: Train IC=+0.1831, Deflated=+0.1824, IR=0.60, Mono=0.72, p=0.0008, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.053 | 2017: -0.019 | 2018: +0.036 | 2019: +0.116 | 2020: +0.049 | 2021: +0.139 | 2022: +0.063 | 2023: +0.165 | 2024: +0.072 | 2025: +0.205 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.110 | 2017: +0.061 | 2018: +0.026 | 2019: +0.301 | 2020: +0.192 | 2021: -0.005 | 2022: +0.332 | 2023: +0.452 | 2024: +0.160 | 2025: +0.185 | 2026: -0.324
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=2.23, Recency ratio=6.70
- Early IC=+0.0170, Recent IC=+0.1140, 1st-half IC=+0.0477, 2nd-half IC=+0.1061, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.108, Q3_mid=+0.091, Q4=+0.039, Q5_high_vol=+0.107

**`combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0677, Sharpe=-0.1117)
- Admission: Train IC=+0.2096, Deflated=+0.2089, IR=0.65, Mono=0.72, p=0.0002, MaxCorr=0.63
- Yearly Linear ICs: 2015: +0.072 | 2016: +0.055 | 2017: +0.020 | 2018: +0.035 | 2019: +0.139 | 2020: +0.033 | 2021: +0.160 | 2022: +0.086 | 2023: +0.142 | 2024: +0.096 | 2025: +0.111 | 2026: -0.055
- Yearly Tail ICs:   2015: -0.014 | 2016: +0.181 | 2017: +0.163 | 2018: +0.002 | 2019: +0.316 | 2020: +0.279 | 2021: +0.072 | 2022: +0.359 | 2023: +0.334 | 2024: +0.215 | 2025: +0.153 | 2026: -0.269
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=1.66, Recency ratio=3.03
- Early IC=+0.0375, Recent IC=+0.1138, 1st-half IC=+0.0649, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.132, Q3_mid=+0.124, Q4=+0.101, Q5_high_vol=+0.058

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_rank_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0656, Sharpe=+0.9697)
- Admission: Train IC=+0.2082, Deflated=+0.2081, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=0.80, Recency ratio=8.68
- Early IC=+0.0095, Recent IC=+0.0825, 1st-half IC=+0.0963, 2nd-half IC=+0.0772, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.043, Q3_mid=+0.074, Q4=+0.041, Q5_high_vol=+0.181

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0655, Sharpe=+0.9697)
- Admission: Train IC=+0.2082, Deflated=+0.2081, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=0.80, Recency ratio=8.68
- Early IC=+0.0095, Recent IC=+0.0825, 1st-half IC=+0.0963, 2nd-half IC=+0.0772, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.08)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.043, Q3_mid=+0.074, Q4=+0.041, Q5_high_vol=+0.181

**`combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0095, Sharpe=+0.2579)
- Admission: Train IC=+0.1924, Deflated=+0.1926, IR=0.50, Mono=0.68, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.083 | 2017: +0.019 | 2018: +0.178 | 2019: +0.083 | 2020: +0.008 | 2021: +0.117 | 2022: +0.038 | 2023: +0.157 | 2024: +0.054 | 2025: +0.023 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.250 | 2016: -0.002 | 2017: +0.074 | 2018: +0.211 | 2019: +0.248 | 2020: +0.165 | 2021: +0.327 | 2022: +0.275 | 2023: +0.252 | 2024: +0.277 | 2025: +0.037 | 2026: +0.023
- IC CV=0.68, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=1.92
- Early IC=+0.0510, Recent IC=+0.0976, 1st-half IC=+0.0963, 2nd-half IC=+0.0779, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.080, Q3_mid=+0.063, Q4=+0.053, Q5_high_vol=+0.156

**`combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0096, Sharpe=+0.2579)
- Admission: Train IC=+0.1917, Deflated=+0.1919, IR=0.50, Mono=0.68, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.082 | 2017: +0.019 | 2018: +0.178 | 2019: +0.083 | 2020: +0.008 | 2021: +0.117 | 2022: +0.038 | 2023: +0.157 | 2024: +0.054 | 2025: +0.023 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.250 | 2016: -0.002 | 2017: +0.074 | 2018: +0.211 | 2019: +0.256 | 2020: +0.165 | 2021: +0.327 | 2022: +0.275 | 2023: +0.252 | 2024: +0.277 | 2025: +0.037 | 2026: +0.023
- IC CV=0.69, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=1.92
- Early IC=+0.0508, Recent IC=+0.0976, 1st-half IC=+0.0963, 2nd-half IC=+0.0779, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.080, Q3_mid=+0.063, Q4=+0.053, Q5_high_vol=+0.156

**`combo_ratio__bar_ret_0__volume_surge_direction`** (Lock IC=+0.0050, Sharpe=+0.2005)
- Admission: Train IC=+0.1403, Deflated=+0.1408, IR=0.43, Mono=0.69, p=0.0060, MaxCorr=0.06
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.143 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.388 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.101
- IC CV=0.58, Neg years (linear/tail)=1/1 of 8, Half ratio=0.60, Recency ratio=0.81
- Early IC=+0.0928, Recent IC=+0.0756, 1st-half IC=+0.1111, 2nd-half IC=+0.0672, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.95)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.059, Q3_mid=+0.092, Q4=+0.036, Q5_high_vol=+0.130

**`combo_ratio__first_bar_return__volume_surge_direction`** (Lock IC=+0.0050, Sharpe=+0.2005)
- Admission: Train IC=+0.1402, Deflated=+0.1408, IR=0.43, Mono=0.69, p=0.0062, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.144 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.393 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.114
- IC CV=0.58, Neg years (linear/tail)=1/1 of 8, Half ratio=0.60, Recency ratio=0.82
- Early IC=+0.0928, Recent IC=+0.0756, 1st-half IC=+0.1111, 2nd-half IC=+0.0672, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.95)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.059, Q3_mid=+0.091, Q4=+0.036, Q5_high_vol=+0.130

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0351, Sharpe=+0.1736)
- Admission: Train IC=+0.2509, Deflated=+0.2505, IR=0.74, Mono=0.78, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.87, Neg years (linear/tail)=1/0 of 8, Half ratio=1.13, Recency ratio=-40.14
- Early IC=-0.0023, Recent IC=+0.0922, 1st-half IC=+0.0952, 2nd-half IC=+0.1073, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.067, Q3_mid=+0.129, Q4=+0.053, Q5_high_vol=+0.214

**`combo_tri_max__first_bar_return__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0210, Sharpe=+0.1568)
- Admission: Train IC=+0.2201, Deflated=+0.2200, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.084 | 2016: +0.100 | 2017: +0.039 | 2018: +0.201 | 2019: +0.101 | 2020: +0.013 | 2021: +0.135 | 2022: +0.051 | 2023: +0.166 | 2024: +0.014 | 2025: +0.094 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.242 | 2016: +0.057 | 2017: +0.073 | 2018: +0.381 | 2019: +0.238 | 2020: +0.218 | 2021: +0.247 | 2022: +0.315 | 2023: +0.274 | 2024: +0.002 | 2025: +0.134 | 2026: -0.380
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=1.57
- Early IC=+0.0694, Recent IC=+0.1087, 1st-half IC=+0.1214, 2nd-half IC=+0.0863, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.081, Q3_mid=+0.099, Q4=+0.074, Q5_high_vol=+0.151

**`combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0203, Sharpe=+0.1467)
- Admission: Train IC=+0.1476, Deflated=+0.1485, IR=0.55, Mono=0.69, p=0.0036, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.063 | 2016: +0.069 | 2017: +0.020 | 2018: +0.106 | 2019: +0.044 | 2020: -0.005 | 2021: +0.076 | 2022: +0.030 | 2023: +0.076 | 2024: +0.045 | 2025: +0.055 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.049 | 2017: +0.187 | 2018: +0.194 | 2019: -0.114 | 2020: +0.061 | 2021: +0.154 | 2022: +0.311 | 2023: +0.140 | 2024: +0.253 | 2025: +0.331 | 2026: -0.221
- IC CV=0.65, Neg years (linear/tail)=1/1 of 8, Half ratio=0.64, Recency ratio=1.19
- Early IC=+0.0444, Recent IC=+0.0529, 1st-half IC=+0.0638, 2nd-half IC=+0.0406, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.001, Q3_mid=+0.037, Q4=+0.067, Q5_high_vol=+0.060

**`combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0094, Sharpe=+0.1080)
- Admission: Train IC=+0.2493, Deflated=+0.2494, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.107 | 2016: +0.081 | 2017: +0.041 | 2018: +0.222 | 2019: +0.065 | 2020: -0.027 | 2021: +0.145 | 2022: +0.066 | 2023: +0.176 | 2024: +0.015 | 2025: +0.076 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.053 | 2016: -0.039 | 2017: +0.227 | 2018: +0.297 | 2019: +0.279 | 2020: +0.061 | 2021: +0.427 | 2022: +0.327 | 2023: +0.379 | 2024: +0.066 | 2025: -0.056 | 2026: -0.157
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=0.82, Recency ratio=1.97
- Early IC=+0.0611, Recent IC=+0.1207, 1st-half IC=+0.1104, 2nd-half IC=+0.0905, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.112, Q3_mid=+0.086, Q4=+0.060, Q5_high_vol=+0.149

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0336, Sharpe=+0.1064)
- Admission: Train IC=+0.2682, Deflated=+0.2690, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.067 | 2017: -0.020 | 2018: +0.188 | 2019: +0.138 | 2020: +0.053 | 2021: +0.155 | 2022: +0.064 | 2023: +0.171 | 2024: +0.009 | 2025: +0.085 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.166 | 2017: +0.081 | 2018: +0.345 | 2019: +0.190 | 2020: +0.209 | 2021: +0.493 | 2022: +0.213 | 2023: +0.265 | 2024: +0.202 | 2025: -0.017 | 2026: +0.300
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=0.98, Recency ratio=5.05
- Early IC=+0.0233, Recent IC=+0.1175, 1st-half IC=+0.1090, 2nd-half IC=+0.1071, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.060, Q3_mid=+0.095, Q4=+0.085, Q5_high_vol=+0.192

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0354, Sharpe=+0.0566)
- Admission: Train IC=+0.2637, Deflated=+0.2645, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.099 | 2017: +0.002 | 2018: +0.184 | 2019: +0.115 | 2020: +0.044 | 2021: +0.132 | 2022: +0.035 | 2023: +0.166 | 2024: +0.056 | 2025: +0.050 | 2026: -0.026
- Yearly Tail ICs:   2015: +0.352 | 2016: +0.156 | 2017: +0.099 | 2018: +0.341 | 2019: +0.250 | 2020: +0.237 | 2021: +0.493 | 2022: +0.143 | 2023: +0.295 | 2024: +0.241 | 2025: -0.054 | 2026: +0.161
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=1.98
- Early IC=+0.0507, Recent IC=+0.1006, 1st-half IC=+0.1081, 2nd-half IC=+0.0906, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.07)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.065, Q3_mid=+0.079, Q4=+0.052, Q5_high_vol=+0.194

### 500ETF — `single` True Positives

**`combo_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1043, Sharpe=+1.0918)
- Admission: Train IC=+0.1869, Deflated=+0.1876, IR=0.50, Mono=0.65, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.070 | 2017: +0.193 | 2018: +0.152 | 2019: +0.175 | 2020: +0.114 | 2021: +0.090 | 2022: +0.030 | 2023: +0.064 | 2024: +0.110 | 2025: +0.130 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.118 | 2017: +0.236 | 2018: +0.376 | 2019: +0.335 | 2020: +0.239 | 2021: +0.059 | 2022: +0.124 | 2023: +0.095 | 2024: +0.313 | 2025: +0.129 | 2026: +0.145
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.35
- Early IC=+0.1317, Recent IC=+0.0467, 1st-half IC=+0.1450, 2nd-half IC=+0.0671, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.039, Q3_mid=+0.075, Q4=+0.151, Q5_high_vol=+0.119

**`combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0927, Sharpe=+0.9299)
- Admission: Train IC=+0.1785, Deflated=+0.1773, IR=0.59, Mono=0.74, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.035 | 2017: +0.154 | 2018: +0.217 | 2019: +0.177 | 2020: +0.181 | 2021: +0.162 | 2022: +0.044 | 2023: +0.087 | 2024: +0.141 | 2025: +0.073 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.388 | 2016: -0.005 | 2017: +0.280 | 2018: +0.361 | 2019: +0.296 | 2020: -0.007 | 2021: +0.352 | 2022: +0.136 | 2023: +0.172 | 2024: +0.177 | 2025: +0.155 | 2026: +0.069
- IC CV=0.48, Neg years (linear/tail)=0/2 of 8, Half ratio=0.81, Recency ratio=0.69
- Early IC=+0.0949, Recent IC=+0.0655, 1st-half IC=+0.1455, 2nd-half IC=+0.1178, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.151, Q2=-0.008, Q3_mid=+0.149, Q4=+0.143, Q5_high_vol=+0.205

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0874, Sharpe=+0.8706)
- Admission: Train IC=+0.2513, Deflated=+0.2506, IR=0.88, Mono=0.81, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.110 | 2017: +0.143 | 2018: +0.284 | 2019: +0.175 | 2020: +0.171 | 2021: +0.171 | 2022: +0.054 | 2023: +0.101 | 2024: +0.158 | 2025: +0.058 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.204 | 2017: +0.306 | 2018: +0.603 | 2019: +0.184 | 2020: +0.123 | 2021: +0.299 | 2022: +0.158 | 2023: +0.252 | 2024: +0.191 | 2025: -0.034 | 2026: +0.013
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.61
- Early IC=+0.1265, Recent IC=+0.0775, 1st-half IC=+0.1778, 2nd-half IC=+0.1247, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.004, Q3_mid=+0.143, Q4=+0.164, Q5_high_vol=+0.241

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0855, Sharpe=+0.8416)
- Admission: Train IC=+0.2698, Deflated=+0.2695, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.101 | 2017: +0.199 | 2018: +0.218 | 2019: +0.146 | 2020: +0.162 | 2021: +0.137 | 2022: +0.068 | 2023: +0.105 | 2024: +0.136 | 2025: +0.021 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.164 | 2017: +0.434 | 2018: +0.346 | 2019: +0.293 | 2020: +0.075 | 2021: +0.226 | 2022: +0.235 | 2023: +0.210 | 2024: +0.342 | 2025: +0.068 | 2026: +0.012
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.58
- Early IC=+0.1497, Recent IC=+0.0865, 1st-half IC=+0.1623, 2nd-half IC=+0.1171, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.015, Q3_mid=+0.106, Q4=+0.173, Q5_high_vol=+0.219

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`** (Lock IC=+0.0655, Sharpe=+0.6803)
- Admission: Train IC=+0.1582, Deflated=+0.1595, IR=0.61, Mono=0.72, p=0.0028, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.104 | 2017: +0.090 | 2018: +0.081 | 2019: +0.029 | 2020: +0.054 | 2021: -0.045 | 2022: +0.098 | 2023: +0.033 | 2024: +0.032 | 2025: +0.101 | 2026: +0.060
- Yearly Tail ICs:   2015: +0.203 | 2016: +0.122 | 2017: +0.121 | 2018: +0.249 | 2019: +0.042 | 2020: +0.195 | 2021: +0.213 | 2022: +0.253 | 2023: +0.090 | 2024: +0.170 | 2025: +0.137 | 2026: +0.117
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=0.53, Recency ratio=0.68
- Early IC=+0.0971, Recent IC=+0.0658, 1st-half IC=+0.0743, 2nd-half IC=+0.0395, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.121, Q2=-0.013, Q3_mid=+0.007, Q4=+0.056, Q5_high_vol=+0.096

**`combo_min__high_low_sequence_momentum__first_bar_return`** (Lock IC=+0.1007, Sharpe=+0.6524)
- Admission: Train IC=+0.2040, Deflated=+0.2043, IR=0.68, Mono=0.73, p=0.0002, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.065 | 2017: +0.205 | 2018: +0.192 | 2019: +0.115 | 2020: +0.083 | 2021: +0.065 | 2022: +0.057 | 2023: +0.078 | 2024: +0.140 | 2025: +0.130 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.394 | 2016: +0.043 | 2017: +0.344 | 2018: +0.335 | 2019: +0.163 | 2020: +0.077 | 2021: +0.320 | 2022: +0.247 | 2023: +0.130 | 2024: +0.297 | 2025: +0.173 | 2026: -0.058
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.50
- Early IC=+0.1350, Recent IC=+0.0677, 1st-half IC=+0.1417, 2nd-half IC=+0.0694, Neg regimes=1/5
- Weak component: `high_low_sequence_momentum` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.044, Q3_mid=+0.105, Q4=+0.132, Q5_high_vol=+0.131

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1193, Sharpe=+0.5966)
- Admission: Train IC=+0.2745, Deflated=+0.2746, IR=1.02, Mono=0.84, p=0.0000, MaxCorr=0.66
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.120 | 2017: +0.225 | 2018: +0.180 | 2019: +0.173 | 2020: +0.172 | 2021: +0.143 | 2022: +0.006 | 2023: +0.103 | 2024: +0.159 | 2025: +0.093 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.361 | 2016: +0.235 | 2017: +0.326 | 2018: +0.506 | 2019: +0.324 | 2020: +0.261 | 2021: +0.289 | 2022: +0.138 | 2023: +0.114 | 2024: +0.281 | 2025: -0.018 | 2026: +0.171
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.32
- Early IC=+0.1723, Recent IC=+0.0546, 1st-half IC=+0.1698, 2nd-half IC=+0.1121, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.033, Q3_mid=+0.133, Q4=+0.134, Q5_high_vol=+0.215

**`combo_tri_max__first_bar_sentiment__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0913, Sharpe=+0.5615)
- Admission: Train IC=+0.1658, Deflated=+0.1653, IR=0.48, Mono=0.68, p=0.0012, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.106 | 2017: +0.163 | 2018: +0.151 | 2019: +0.092 | 2020: +0.111 | 2021: +0.099 | 2022: +0.123 | 2023: +0.025 | 2024: +0.102 | 2025: +0.060 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.207 | 2016: +0.125 | 2017: +0.157 | 2018: +0.137 | 2019: +0.244 | 2020: +0.111 | 2021: +0.144 | 2022: +0.250 | 2023: +0.037 | 2024: +0.138 | 2025: +0.018 | 2026: -0.002
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.55
- Early IC=+0.1342, Recent IC=+0.0739, 1st-half IC=+0.1234, 2nd-half IC=+0.0940, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.183, Q2=-0.002, Q3_mid=+0.069, Q4=+0.149, Q5_high_vol=+0.134

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1566, Sharpe=+0.5389)
- Admission: Train IC=+0.1738, Deflated=+0.1732, IR=0.41, Mono=0.66, p=0.0006, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.046 | 2017: +0.193 | 2018: +0.147 | 2019: +0.180 | 2020: +0.113 | 2021: +0.083 | 2022: +0.063 | 2023: +0.096 | 2024: +0.159 | 2025: +0.106 | 2026: +0.198
- Yearly Tail ICs:   2015: -0.019 | 2016: +0.052 | 2017: +0.182 | 2018: +0.211 | 2019: +0.382 | 2020: +0.184 | 2021: +0.145 | 2022: +0.176 | 2023: +0.051 | 2024: +0.225 | 2025: +0.105 | 2026: +0.332
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.67
- Early IC=+0.1197, Recent IC=+0.0799, 1st-half IC=+0.1493, 2nd-half IC=+0.0766, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.001, Q3_mid=+0.123, Q4=+0.094, Q5_high_vol=+0.156

**`combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0983, Sharpe=+0.5323)
- Admission: Train IC=+0.2501, Deflated=+0.2495, IR=0.88, Mono=0.83, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.090 | 2017: +0.222 | 2018: +0.191 | 2019: +0.112 | 2020: +0.151 | 2021: +0.132 | 2022: +0.086 | 2023: +0.088 | 2024: +0.164 | 2025: +0.115 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.239 | 2017: +0.250 | 2018: +0.318 | 2019: +0.242 | 2020: +0.268 | 2021: +0.254 | 2022: +0.305 | 2023: +0.229 | 2024: +0.291 | 2025: +0.036 | 2026: -0.203
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.56
- Early IC=+0.1562, Recent IC=+0.0868, 1st-half IC=+0.1498, 2nd-half IC=+0.1132, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.193, Q2=-0.023, Q3_mid=+0.125, Q4=+0.166, Q5_high_vol=+0.172

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0910, Sharpe=+0.5264)
- Admission: Train IC=+0.2743, Deflated=+0.2737, IR=0.76, Mono=0.78, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.077 | 2017: +0.226 | 2018: +0.202 | 2019: +0.110 | 2020: +0.154 | 2021: +0.112 | 2022: +0.087 | 2023: +0.122 | 2024: +0.133 | 2025: +0.132 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.466 | 2016: +0.294 | 2017: +0.293 | 2018: +0.413 | 2019: +0.107 | 2020: +0.231 | 2021: +0.259 | 2022: +0.190 | 2023: +0.283 | 2024: +0.239 | 2025: -0.001 | 2026: -0.187
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.69
- Early IC=+0.1517, Recent IC=+0.1046, 1st-half IC=+0.1503, 2nd-half IC=+0.1216, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.000, Q3_mid=+0.143, Q4=+0.135, Q5_high_vol=+0.210

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0955, Sharpe=+0.5066)
- Admission: Train IC=+0.2717, Deflated=+0.2718, IR=0.76, Mono=0.74, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.112 | 2017: +0.195 | 2018: +0.204 | 2019: +0.085 | 2020: +0.161 | 2021: +0.081 | 2022: +0.116 | 2023: +0.089 | 2024: +0.085 | 2025: +0.134 | 2026: +0.033
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.271 | 2017: +0.313 | 2018: +0.362 | 2019: +0.228 | 2020: +0.237 | 2021: +0.124 | 2022: +0.264 | 2023: +0.107 | 2024: +0.219 | 2025: -0.037 | 2026: -0.011
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.67
- Early IC=+0.1537, Recent IC=+0.1028, 1st-half IC=+0.1455, 2nd-half IC=+0.1157, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.002, Q3_mid=+0.093, Q4=+0.129, Q5_high_vol=+0.217

**`combo_rank_min__volatility_expansion_trend_vector__close_vs_open_range`** (Lock IC=+0.0885, Sharpe=+0.5055)
- Admission: Train IC=+0.2419, Deflated=+0.2417, IR=0.46, Mono=0.69, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.072 | 2017: +0.202 | 2018: +0.115 | 2019: +0.069 | 2020: +0.095 | 2021: +0.064 | 2022: +0.087 | 2023: +0.088 | 2024: +0.128 | 2025: +0.148 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.123 | 2017: +0.327 | 2018: +0.237 | 2019: +0.299 | 2020: +0.226 | 2021: +0.215 | 2022: +0.121 | 2023: +0.247 | 2024: +0.220 | 2025: -0.042 | 2026: -0.145
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.64
- Early IC=+0.1363, Recent IC=+0.0873, 1st-half IC=+0.1095, 2nd-half IC=+0.0849, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.023, Q3_mid=+0.096, Q4=+0.087, Q5_high_vol=+0.136

**`combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__volatility_expansion_trend_vector`** (Lock IC=+0.0960, Sharpe=+0.4859)
- Admission: Train IC=+0.2365, Deflated=+0.2363, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.074 | 2017: +0.182 | 2018: +0.206 | 2019: +0.149 | 2020: +0.121 | 2021: +0.104 | 2022: +0.073 | 2023: +0.096 | 2024: +0.130 | 2025: +0.137 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.282 | 2016: +0.015 | 2017: +0.253 | 2018: +0.215 | 2019: +0.381 | 2020: +0.226 | 2021: +0.298 | 2022: +0.247 | 2023: +0.339 | 2024: +0.194 | 2025: +0.150 | 2026: -0.089
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.66
- Early IC=+0.1282, Recent IC=+0.0845, 1st-half IC=+0.1506, 2nd-half IC=+0.1006, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.006, Q3_mid=+0.112, Q4=+0.158, Q5_high_vol=+0.162

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0887, Sharpe=+0.4835)
- Admission: Train IC=+0.2615, Deflated=+0.2607, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.046 | 2017: +0.160 | 2018: +0.222 | 2019: +0.173 | 2020: +0.159 | 2021: +0.162 | 2022: +0.052 | 2023: +0.086 | 2024: +0.126 | 2025: +0.097 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.436 | 2016: +0.028 | 2017: +0.190 | 2018: +0.389 | 2019: +0.254 | 2020: +0.220 | 2021: +0.335 | 2022: +0.237 | 2023: +0.307 | 2024: +0.298 | 2025: +0.095 | 2026: -0.350
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.67
- Early IC=+0.1031, Recent IC=+0.0689, 1st-half IC=+0.1551, 2nd-half IC=+0.1082, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.013, Q3_mid=+0.142, Q4=+0.164, Q5_high_vol=+0.183

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0991, Sharpe=+0.4835)
- Admission: Train IC=+0.2612, Deflated=+0.2604, IR=0.89, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.056 | 2017: +0.164 | 2018: +0.246 | 2019: +0.173 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145 | 2025: +0.096 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.054 | 2017: +0.194 | 2018: +0.413 | 2019: +0.231 | 2020: +0.221 | 2021: +0.335 | 2022: +0.237 | 2023: +0.314 | 2024: +0.298 | 2025: +0.095 | 2026: -0.350
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.75
- Early IC=+0.1100, Recent IC=+0.0820, 1st-half IC=+0.1649, 2nd-half IC=+0.1118, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.169, Q2=-0.006, Q3_mid=+0.147, Q4=+0.167, Q5_high_vol=+0.197

**`combo_min__net_volume_flow__first_bar_return`** (Lock IC=+0.0967, Sharpe=+0.4715)
- Admission: Train IC=+0.2237, Deflated=+0.2241, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.071 | 2017: +0.181 | 2018: +0.179 | 2019: +0.124 | 2020: +0.092 | 2021: +0.082 | 2022: +0.085 | 2023: +0.076 | 2024: +0.130 | 2025: +0.121 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.374 | 2016: +0.010 | 2017: +0.227 | 2018: +0.400 | 2019: +0.144 | 2020: +0.090 | 2021: +0.286 | 2022: +0.257 | 2023: +0.300 | 2024: +0.321 | 2025: +0.121 | 2026: -0.008
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.64
- Early IC=+0.1261, Recent IC=+0.0804, 1st-half IC=+0.1355, 2nd-half IC=+0.0836, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.179, Q2=-0.031, Q3_mid=+0.102, Q4=+0.151, Q5_high_vol=+0.123

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0747, Sharpe=+0.2436)
- Admission: Train IC=+0.2676, Deflated=+0.2677, IR=0.95, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.100 | 2017: +0.194 | 2018: +0.213 | 2019: +0.156 | 2020: +0.156 | 2021: +0.137 | 2022: +0.066 | 2023: +0.083 | 2024: +0.102 | 2025: +0.025 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.137 | 2017: +0.412 | 2018: +0.407 | 2019: +0.402 | 2020: +0.146 | 2021: +0.256 | 2022: +0.165 | 2023: +0.190 | 2024: -0.015 | 2025: -0.045 | 2026: +0.030
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.51
- Early IC=+0.1471, Recent IC=+0.0745, 1st-half IC=+0.1598, 2nd-half IC=+0.1113, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.028, Q3_mid=+0.089, Q4=+0.167, Q5_high_vol=+0.225

**`combo_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0905, Sharpe=+0.2004)
- Admission: Train IC=+0.2280, Deflated=+0.2277, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.089 | 2017: +0.213 | 2018: +0.253 | 2019: +0.159 | 2020: +0.134 | 2021: +0.097 | 2022: +0.055 | 2023: +0.067 | 2024: +0.122 | 2025: +0.109 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.397 | 2016: +0.098 | 2017: +0.365 | 2018: +0.409 | 2019: +0.189 | 2020: +0.130 | 2021: +0.320 | 2022: +0.280 | 2023: +0.141 | 2024: +0.170 | 2025: +0.062 | 2026: -0.142
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.41
- Early IC=+0.1508, Recent IC=+0.0613, 1st-half IC=+0.1769, 2nd-half IC=+0.0887, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.153, Q2=-0.019, Q3_mid=+0.135, Q4=+0.170, Q5_high_vol=+0.172

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0905, Sharpe=+0.2004)
- Admission: Train IC=+0.2278, Deflated=+0.2275, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.089 | 2017: +0.213 | 2018: +0.253 | 2019: +0.158 | 2020: +0.134 | 2021: +0.097 | 2022: +0.055 | 2023: +0.067 | 2024: +0.122 | 2025: +0.109 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.397 | 2016: +0.098 | 2017: +0.365 | 2018: +0.409 | 2019: +0.190 | 2020: +0.133 | 2021: +0.319 | 2022: +0.280 | 2023: +0.145 | 2024: +0.171 | 2025: +0.057 | 2026: -0.142
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.41
- Early IC=+0.1509, Recent IC=+0.0613, 1st-half IC=+0.1770, 2nd-half IC=+0.0888, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.153, Q2=-0.019, Q3_mid=+0.135, Q4=+0.169, Q5_high_vol=+0.172

**`combo_min__volatility_expansion_trend_vector__close_vs_open_range`** (Lock IC=+0.0848, Sharpe=+0.1999)
- Admission: Train IC=+0.2250, Deflated=+0.2248, IR=0.44, Mono=0.67, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.069 | 2017: +0.198 | 2018: +0.116 | 2019: +0.066 | 2020: +0.094 | 2021: +0.069 | 2022: +0.094 | 2023: +0.091 | 2024: +0.119 | 2025: +0.144 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.326 | 2016: +0.114 | 2017: +0.284 | 2018: +0.220 | 2019: +0.273 | 2020: +0.208 | 2021: +0.227 | 2022: +0.192 | 2023: +0.218 | 2024: +0.232 | 2025: -0.030 | 2026: -0.010
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.69
- Early IC=+0.1334, Recent IC=+0.0925, 1st-half IC=+0.1075, 2nd-half IC=+0.0885, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.025, Q3_mid=+0.098, Q4=+0.091, Q5_high_vol=+0.133

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.1139, Sharpe=+0.1221)
- Admission: Train IC=+0.2081, Deflated=+0.2074, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.300 | 2016: +0.122 | 2017: +0.218 | 2018: +0.223 | 2019: +0.163 | 2020: +0.162 | 2021: +0.126 | 2022: +0.094 | 2023: +0.065 | 2024: +0.143 | 2025: +0.113 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.413 | 2016: +0.204 | 2017: +0.246 | 2018: +0.449 | 2019: +0.246 | 2020: +0.238 | 2021: +0.170 | 2022: +0.137 | 2023: +0.089 | 2024: +0.103 | 2025: +0.100 | 2026: +0.048
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.47
- Early IC=+0.1702, Recent IC=+0.0795, 1st-half IC=+0.1800, 2nd-half IC=+0.1149, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.002, Q3_mid=+0.137, Q4=+0.169, Q5_high_vol=+0.207

**`combo_rank_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0742, Sharpe=+0.1097)
- Admission: Train IC=+0.2644, Deflated=+0.2653, IR=0.81, Mono=0.77, p=0.0000, MaxCorr=0.62
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.148 | 2017: +0.146 | 2018: +0.232 | 2019: +0.124 | 2020: +0.121 | 2021: +0.095 | 2022: +0.065 | 2023: +0.058 | 2024: +0.102 | 2025: +0.125 | 2026: -0.026
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.202 | 2017: +0.372 | 2018: +0.527 | 2019: +0.070 | 2020: +0.250 | 2021: +0.008 | 2022: +0.268 | 2023: -0.001 | 2024: +0.153 | 2025: +0.160 | 2026: -0.223
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.52, Recency ratio=0.42
- Early IC=+0.1471, Recent IC=+0.0611, 1st-half IC=+0.1610, 2nd-half IC=+0.0843, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.147, Q2=-0.014, Q3_mid=+0.105, Q4=+0.173, Q5_high_vol=+0.155

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0818, Sharpe=+0.0961)
- Admission: Train IC=+0.2061, Deflated=+0.2067, IR=0.57, Mono=0.69, p=0.0002, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.094 | 2017: +0.257 | 2018: +0.230 | 2019: +0.145 | 2020: +0.132 | 2021: +0.089 | 2022: +0.091 | 2023: +0.045 | 2024: +0.124 | 2025: +0.108 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.012 | 2017: +0.235 | 2018: +0.426 | 2019: +0.114 | 2020: +0.240 | 2021: +0.196 | 2022: +0.200 | 2023: +0.229 | 2024: +0.223 | 2025: +0.035 | 2026: -0.250
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.39
- Early IC=+0.1753, Recent IC=+0.0679, 1st-half IC=+0.1733, 2nd-half IC=+0.0874, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.060, Q3_mid=+0.140, Q4=+0.161, Q5_high_vol=+0.151

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0939, Sharpe=+0.0157)
- Admission: Train IC=+0.2928, Deflated=+0.2924, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.095 | 2017: +0.218 | 2018: +0.226 | 2019: +0.130 | 2020: +0.137 | 2021: +0.136 | 2022: +0.092 | 2023: +0.096 | 2024: +0.156 | 2025: +0.076 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.490 | 2016: +0.335 | 2017: +0.316 | 2018: +0.436 | 2019: +0.193 | 2020: +0.236 | 2021: +0.254 | 2022: +0.239 | 2023: +0.166 | 2024: +0.123 | 2025: -0.089 | 2026: +0.010
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.60
- Early IC=+0.1565, Recent IC=+0.0939, 1st-half IC=+0.1620, 2nd-half IC=+0.1176, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.185, Q2=-0.017, Q3_mid=+0.134, Q4=+0.157, Q5_high_vol=+0.215

### 159915ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1283, Sharpe=+1.6959)
- Admission: Train IC=+0.2816, Deflated=+0.2820, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.124 | 2017: -0.001 | 2018: +0.125 | 2019: +0.213 | 2020: +0.067 | 2021: +0.189 | 2022: +0.060 | 2023: +0.148 | 2024: +0.120 | 2025: +0.140 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.063 | 2017: +0.103 | 2018: +0.280 | 2019: +0.527 | 2020: +0.305 | 2021: +0.389 | 2022: +0.110 | 2023: +0.381 | 2024: +0.281 | 2025: +0.148 | 2026: +0.325
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.04, Recency ratio=1.71
- Early IC=+0.0616, Recent IC=+0.1054, 1st-half IC=+0.1213, 2nd-half IC=+0.1264, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.137, Q3_mid=+0.089, Q4=+0.134, Q5_high_vol=+0.176

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1291, Sharpe=+1.1684)
- Admission: Train IC=+0.2593, Deflated=+0.2594, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.49, Neg years (linear/tail)=1/0 of 8, Half ratio=1.95, Recency ratio=3.70
- Early IC=+0.0401, Recent IC=+0.1487, 1st-half IC=+0.0767, 2nd-half IC=+0.1493, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.74)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.154, Q3_mid=+0.073, Q4=+0.110, Q5_high_vol=+0.155

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1204, Sharpe=+1.1103)
- Admission: Train IC=+0.2306, Deflated=+0.2298, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.203 | 2016: -0.012 | 2017: -0.014 | 2018: +0.077 | 2019: +0.224 | 2020: +0.104 | 2021: +0.111 | 2022: +0.092 | 2023: +0.164 | 2024: +0.067 | 2025: +0.174 | 2026: +0.116
- Yearly Tail ICs:   2015: +0.210 | 2016: -0.107 | 2017: +0.066 | 2018: +0.349 | 2019: +0.484 | 2020: +0.155 | 2021: +0.309 | 2022: +0.301 | 2023: +0.392 | 2024: +0.284 | 2025: +0.131 | 2026: +0.337
- IC CV=0.81, Neg years (linear/tail)=2/1 of 8, Half ratio=1.49, Recency ratio=-9.71
- Early IC=-0.0130, Recent IC=+0.1265, 1st-half IC=+0.0765, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.113, Q3_mid=+0.107, Q4=+0.106, Q5_high_vol=+0.093

**`combo_mean__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1327, Sharpe=+0.9738)
- Admission: Train IC=+0.2314, Deflated=+0.2314, IR=0.50, Mono=0.72, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.074 | 2017: +0.019 | 2018: +0.134 | 2019: +0.166 | 2020: +0.129 | 2021: +0.159 | 2022: +0.155 | 2023: +0.136 | 2024: +0.115 | 2025: +0.173 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.031 | 2016: +0.203 | 2017: +0.128 | 2018: +0.281 | 2019: +0.358 | 2020: +0.142 | 2021: +0.271 | 2022: +0.251 | 2023: +0.145 | 2024: +0.344 | 2025: +0.155 | 2026: +0.090
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.62, Recency ratio=3.11
- Early IC=+0.0468, Recent IC=+0.1456, 1st-half IC=+0.0938, 2nd-half IC=+0.1522, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.136, Q3_mid=+0.092, Q4=+0.134, Q5_high_vol=+0.184

**`combo_tri_min__max_up_ret__star50_limit_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1200, Sharpe=+0.9514)
- Admission: Train IC=+0.2353, Deflated=+0.2357, IR=0.52, Mono=0.70, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.069 | 2017: +0.032 | 2018: +0.078 | 2019: +0.121 | 2020: +0.036 | 2021: +0.141 | 2022: +0.128 | 2023: +0.153 | 2024: +0.116 | 2025: +0.170 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.179 | 2016: +0.218 | 2017: +0.115 | 2018: +0.354 | 2019: +0.328 | 2020: +0.174 | 2021: +0.260 | 2022: +0.229 | 2023: +0.101 | 2024: +0.292 | 2025: +0.197 | 2026: +0.206
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.65, Recency ratio=2.78
- Early IC=+0.0507, Recent IC=+0.1407, 1st-half IC=+0.0699, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.106, Q3_mid=+0.086, Q4=+0.107, Q5_high_vol=+0.110

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1235, Sharpe=+0.8704)
- Admission: Train IC=+0.3321, Deflated=+0.3316, IR=0.84, Mono=0.80, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.113 | 2017: -0.018 | 2018: +0.194 | 2019: +0.243 | 2020: +0.166 | 2021: +0.154 | 2022: +0.098 | 2023: +0.185 | 2024: +0.115 | 2025: +0.168 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.113 | 2017: +0.050 | 2018: +0.464 | 2019: +0.573 | 2020: +0.390 | 2021: +0.435 | 2022: +0.258 | 2023: +0.459 | 2024: +0.415 | 2025: +0.235 | 2026: +0.220
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=2.98
- Early IC=+0.0476, Recent IC=+0.1418, 1st-half IC=+0.1385, 2nd-half IC=+0.1529, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.075, Q2=+0.158, Q3_mid=+0.108, Q4=+0.157, Q5_high_vol=+0.195

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1190, Sharpe=+0.8629)
- Admission: Train IC=+0.2604, Deflated=+0.2603, IR=0.59, Mono=0.70, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.166 | 2017: -0.023 | 2018: +0.145 | 2019: +0.205 | 2020: +0.136 | 2021: +0.124 | 2022: +0.086 | 2023: +0.131 | 2024: +0.076 | 2025: +0.178 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.187 | 2017: +0.200 | 2018: +0.320 | 2019: +0.433 | 2020: +0.148 | 2021: +0.271 | 2022: +0.203 | 2023: +0.281 | 2024: +0.239 | 2025: +0.451 | 2026: +0.119
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=0.96, Recency ratio=1.53
- Early IC=+0.0714, Recent IC=+0.1089, 1st-half IC=+0.1252, 2nd-half IC=+0.1205, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.100, Q3_mid=+0.104, Q4=+0.106, Q5_high_vol=+0.179

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0904, Sharpe=+0.8135)
- Admission: Train IC=+0.2643, Deflated=+0.2641, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.067 | 2017: +0.044 | 2018: +0.069 | 2019: +0.152 | 2020: +0.079 | 2021: +0.136 | 2022: +0.126 | 2023: +0.180 | 2024: +0.092 | 2025: +0.196 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.225 | 2017: +0.118 | 2018: +0.162 | 2019: +0.369 | 2020: +0.241 | 2021: +0.123 | 2022: +0.282 | 2023: +0.533 | 2024: +0.238 | 2025: +0.239 | 2026: -0.114
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.62, Recency ratio=2.75
- Early IC=+0.0557, Recent IC=+0.1530, 1st-half IC=+0.0792, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.04)
- Regime ICs: Q1_low_vol=+0.069, Q2=+0.123, Q3_mid=+0.103, Q4=+0.102, Q5_high_vol=+0.136

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.0911, Sharpe=+0.5434)
- Admission: Train IC=+0.2933, Deflated=+0.2948, IR=0.77, Mono=0.82, p=0.0000, MaxCorr=0.37
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.107 | 2017: -0.042 | 2018: +0.148 | 2019: +0.125 | 2020: +0.143 | 2021: +0.061 | 2022: +0.184 | 2023: +0.110 | 2024: +0.055 | 2025: +0.086 | 2026: +0.144
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.359 | 2017: +0.128 | 2018: +0.396 | 2019: +0.349 | 2020: +0.319 | 2021: +0.172 | 2022: +0.412 | 2023: +0.081 | 2024: +0.028 | 2025: +0.063 | 2026: +0.085
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=1.30, Recency ratio=4.55
- Early IC=+0.0323, Recent IC=+0.1469, 1st-half IC=+0.0983, 2nd-half IC=+0.1280, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.139, Q3_mid=+0.039, Q4=+0.138, Q5_high_vol=+0.190

**`combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1088, Sharpe=+0.4427)
- Admission: Train IC=+0.2033, Deflated=+0.2038, IR=0.49, Mono=0.70, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.121 | 2017: -0.071 | 2018: +0.115 | 2019: +0.066 | 2020: +0.116 | 2021: +0.100 | 2022: +0.119 | 2023: +0.135 | 2024: +0.143 | 2025: +0.074 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.321 | 2017: -0.016 | 2018: +0.309 | 2019: +0.113 | 2020: +0.071 | 2021: +0.261 | 2022: +0.113 | 2023: +0.185 | 2024: +0.194 | 2025: -0.077 | 2026: +0.161
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=1.83, Recency ratio=5.08
- Early IC=+0.0250, Recent IC=+0.1270, 1st-half IC=+0.0683, 2nd-half IC=+0.1248, Neg regimes=1/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=-0.028, Q2=+0.132, Q3_mid=+0.109, Q4=+0.127, Q5_high_vol=+0.089

**`combo_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0199, Sharpe=+0.3480)
- Admission: Train IC=+0.1774, Deflated=+0.1770, IR=0.52, Mono=0.69, p=0.0010, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.014 | 2016: +0.120 | 2017: +0.020 | 2018: +0.103 | 2019: +0.043 | 2020: +0.097 | 2021: +0.050 | 2022: +0.079 | 2023: +0.087 | 2024: +0.014 | 2025: +0.076 | 2026: -0.076
- Yearly Tail ICs:   2015: -0.089 | 2016: +0.330 | 2017: +0.107 | 2018: +0.215 | 2019: +0.055 | 2020: +0.300 | 2021: +0.220 | 2022: +0.256 | 2023: +0.029 | 2024: +0.222 | 2025: -0.032 | 2026: +0.188
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.19
- Early IC=+0.0701, Recent IC=+0.0831, 1st-half IC=+0.0610, 2nd-half IC=+0.0831, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=-0.082, Q2=+0.135, Q3_mid=+0.042, Q4=+0.106, Q5_high_vol=+0.139

**`combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0760, Sharpe=+0.1170)
- Admission: Train IC=+0.2465, Deflated=+0.2461, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.160 | 2017: +0.001 | 2018: +0.129 | 2019: +0.197 | 2020: +0.139 | 2021: +0.144 | 2022: +0.090 | 2023: +0.172 | 2024: +0.050 | 2025: +0.148 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.120 | 2016: +0.130 | 2017: -0.002 | 2018: +0.271 | 2019: +0.371 | 2020: +0.256 | 2021: +0.256 | 2022: +0.228 | 2023: +0.539 | 2024: +0.223 | 2025: +0.068 | 2026: -0.090
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=1.14, Recency ratio=1.62
- Early IC=+0.0806, Recent IC=+0.1309, 1st-half IC=+0.1188, 2nd-half IC=+0.1353, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.123, Q3_mid=+0.109, Q4=+0.104, Q5_high_vol=+0.185

**`combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0866, Sharpe=+0.0893)
- Admission: Train IC=+0.2550, Deflated=+0.2548, IR=0.54, Mono=0.69, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.174 | 2017: -0.015 | 2018: +0.141 | 2019: +0.203 | 2020: +0.106 | 2021: +0.139 | 2022: +0.079 | 2023: +0.159 | 2024: +0.049 | 2025: +0.165 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.218 | 2017: +0.143 | 2018: +0.354 | 2019: +0.381 | 2020: +0.067 | 2021: +0.243 | 2022: +0.306 | 2023: +0.444 | 2024: +0.196 | 2025: +0.440 | 2026: -0.097
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=0.95, Recency ratio=1.50
- Early IC=+0.0793, Recent IC=+0.1188, 1st-half IC=+0.1244, 2nd-half IC=+0.1180, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.117, Q3_mid=+0.105, Q4=+0.102, Q5_high_vol=+0.172

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0259, Sharpe=+0.0683)
- Admission: Train IC=+0.1841, Deflated=+0.1841, IR=0.48, Mono=0.65, p=0.0004, MaxCorr=0.49
- Yearly Linear ICs: 2015: -0.033 | 2016: +0.102 | 2017: +0.046 | 2018: +0.082 | 2019: +0.039 | 2020: +0.087 | 2021: +0.066 | 2022: +0.087 | 2023: +0.093 | 2024: +0.008 | 2025: +0.113 | 2026: -0.105
- Yearly Tail ICs:   2015: -0.051 | 2016: +0.324 | 2017: +0.142 | 2018: +0.231 | 2019: -0.009 | 2020: +0.183 | 2021: +0.323 | 2022: +0.157 | 2023: +0.258 | 2024: +0.167 | 2025: +0.123 | 2026: +0.162
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=1.63, Recency ratio=1.21
- Early IC=+0.0741, Recent IC=+0.0897, 1st-half IC=+0.0547, 2nd-half IC=+0.0891, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.12)
- Regime ICs: Q1_low_vol=-0.074, Q2=+0.126, Q3_mid=+0.043, Q4=+0.087, Q5_high_vol=+0.139

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | FP | fast | +0.0995 | -0.1789 | +0.0571 | 1y |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | FP | gradual | +0.0576 | +0.0341 | -0.1722 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0563 | +0.0495 | -0.0265 | 2y |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.0542 | +0.0226 | -0.0699 | 1y |
| `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0540 | +0.0226 | -0.0699 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0498 | +0.0530 | -0.0159 | 2y |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0453 | +0.0553 | -0.0801 | 2y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | gradual | +0.0418 | +0.1055 | -0.2078 | 2y |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0387 | +0.0944 | +0.0458 | ∞ |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0386 | +0.0944 | +0.0458 | ∞ |
| `combo_ratio__bar_ret_0__volume_surge_direction` | TP | gradual | +0.0230 | +0.0417 | -0.0934 | 2y |
| `combo_ratio__first_bar_return__volume_surge_direction` | TP | gradual | +0.0230 | +0.0417 | -0.0939 | 2y |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | TP | gradual | +0.0145 | +0.0760 | -0.0984 | 2y |
| `combo_tri_max__first_bar_return__first_bar_sentiment__bar_body_rng_0` | TP | gradual | +0.0142 | +0.0938 | -0.0762 | 2y |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | gradual | +0.0093 | +0.0956 | -0.1968 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | gradual | +0.0089 | +0.0852 | -0.0030 | ∞ |
| `combo_rank_min__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0042 | +0.0960 | -0.1011 | ∞ |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | FP | immediate | -0.0075 | +0.0315 | -0.1334 | ∞ |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Median | immediate | -0.0628 | +0.0683 | +0.1244 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=1, gradual=14, persistent=2

**FP decay trajectories:**

- `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`: Y1:-0.007 → Y2:+0.032 → Y3:-0.133
- `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.009 → Y2:+0.096 → Y3:-0.197
- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.042 → Y2:+0.105 → Y3:-0.208
- `combo_min__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.058 → Y2:+0.034 → Y3:-0.172
- `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment`: Y1:+0.100 → Y2:-0.179 → Y3:+0.057

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__first_bar_sentiment` | TP | gradual | +0.1644 | +0.1148 | -0.0503 | 2y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1590 | +0.1063 | +0.1978 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1587 | +0.0925 | +0.0908 | ∞ |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1576 | +0.0579 | +0.0057 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1558 | +0.0765 | +0.0171 | 1y |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.1537 | +0.0781 | +0.0842 | ∞ |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.1445 | +0.0964 | +0.0136 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_sentiment` | TP | persistent | +0.1434 | +0.1135 | +0.0435 | 2y |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | TP | persistent | +0.1410 | +0.0727 | +0.0337 | 2y |
| `combo_min__high_low_sequence_momentum__first_bar_return` | TP | gradual | +0.1404 | +0.1297 | -0.0098 | 2y |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1356 | +0.0212 | +0.0758 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | TP | gradual | +0.1330 | +0.1324 | -0.0522 | 2y |
| `combo_min__net_volume_flow__first_bar_return` | TP | persistent | +0.1302 | +0.1212 | +0.0078 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__volatility_expansion_trend_vector` | TP | gradual | +0.1297 | +0.1371 | -0.0245 | 2y |
| `combo_rank_min__volatility_expansion_trend_vector__close_vs_open_range` | TP | gradual | +0.1273 | +0.1477 | -0.0753 | 2y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | gradual | +0.1272 | +0.1213 | -0.1240 | 2y |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.1264 | +0.0968 | +0.0042 | 2y |
| `combo_max__bar_ret_0__max_down_ret` | TP | persistent | +0.1244 | +0.1076 | +0.0004 | 2y |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.1224 | +0.1093 | +0.0049 | 2y |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | TP | persistent | +0.1222 | +0.1093 | +0.0044 | 2y |
| `combo_min__volatility_expansion_trend_vector__close_vs_open_range` | TP | gradual | +0.1187 | +0.1437 | -0.0747 | 2y |
| `combo_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1102 | +0.1298 | +0.0854 | ∞ |
| `vwap_trend_channel_slope` | Median | gradual | +0.1037 | +0.0941 | -0.0312 | 2y |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1022 | +0.0249 | +0.0948 | 1y |
| `combo_tri_max__first_bar_sentiment__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1020 | +0.0603 | +0.0914 | ∞ |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | TP | gradual | +0.1017 | +0.1252 | -0.0261 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0853 | +0.1336 | +0.0332 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow` | TP | persistent | +0.0319 | +0.1014 | +0.0598 | ∞ |
| `combo_diff__bar_ret_0__max_down_ret` | Median | gradual | +0.0035 | +0.0521 | -0.0202 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=10, persistent=19

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.1426 | +0.0743 | +0.1028 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1194 | +0.1395 | +0.1093 | ∞ |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1165 | +0.1698 | +0.0465 | 2y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1153 | +0.1681 | +0.0618 | ∞ |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1148 | +0.1732 | +0.0894 | ∞ |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Median | gradual | +0.0965 | +0.1114 | -0.0547 | 2y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__impulse_bar_dominance` | TP | gradual | +0.0921 | +0.1960 | -0.0813 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0767 | +0.2129 | +0.0668 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0764 | +0.1783 | +0.0831 | ∞ |
| `net_volume_flow` | Median | gradual | +0.0717 | +0.2054 | -0.0663 | 2y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0638 | +0.1735 | +0.1144 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0546 | +0.0855 | +0.1440 | ∞ |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | TP | gradual | +0.0498 | +0.1479 | -0.0170 | 2y |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0491 | +0.1651 | +0.0170 | 2y |
| `combo_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.0142 | +0.0759 | -0.0765 | 2y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.0083 | +0.1126 | -0.1051 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0535 | -0.0299 | +0.0233 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=6, persistent=10

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.053 → Y2:-0.030 → Y3:+0.023

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.739±0.044 | 0.708±0.035 | 63% | WEAK |
| ic_ir | 0.672±0.106 | 0.569±0.101 | 44% | USEFUL |
| p_value | 0.003±0.004 | 0.001±0.002 | 56% | WEAK |
| max_corr | 0.606±0.159 | 0.729±0.326 | 40% | USEFUL |
| deflated_ic | 0.195±0.047 | 0.207±0.044 | 81% | USELESS |
| overall_ic | 0.195±0.047 | 0.207±0.044 | 80% | USELESS |
| raw_ic | 0.069±0.027 | 0.092±0.014 | 51% | WEAK |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 8/20 top rejects are profitable (40%)

- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188
- `combo_z_sum__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__first_bar_sentiment`: Train IC=+0.2062, Lock IC=+0.0300, Sharpe=+0.3444

**B2 Rolling Guard**: 1/20 top rejects are profitable (5%)

- `combo_clamp_diff__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.1830, Lock IC=+0.0145, Sharpe=+0.0044

**Temporal Validation Gate**: 5/20 top rejects are profitable (25%)

- `volume_weighted_momentum_acceleration`: Train IC=+0.1838, Lock IC=+0.0201, Sharpe=+0.1887
- `combo_diff__volume_weighted_momentum_acceleration__max_up_ret`: Train IC=+0.2233, Lock IC=+0.0108, Sharpe=+0.1489
- `combo_z_diff__volume_weighted_momentum_acceleration__max_up_ret`: Train IC=+0.2233, Lock IC=+0.0108, Sharpe=+0.1489

**BH-FDR Gate**: 1/12 top rejects are profitable (8%)

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Sharpe=+0.1611

**B6 Yearly IC CV Gate**: 1/18 top rejects are profitable (6%)

- `combo_product__max_up_ret__first_bar_sentiment`: Train IC=+0.1701, Lock IC=+0.0113, Sharpe=+0.3291

**B4 Correlation Gate**: 7/20 top rejects are profitable (35%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2502, Lock IC=+0.0505, Sharpe=+0.7439
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Sharpe=+0.5172
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2341, Lock IC=+0.0362, Sharpe=+0.3660

**Adaptive Correlation Gate**: 7/14 top rejects are profitable (50%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1458, Lock IC=+0.0531, Sharpe=+0.6589
- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Sharpe=+0.5172
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1971, Lock IC=+0.0093, Sharpe=+0.3898

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Sharpe=+1.1505

**B2 Rolling Guard**: 17/20 top rejects are profitable (85%)

- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Sharpe=+1.2071
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Sharpe=+1.1213

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621
- `combo_z_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2670, Lock IC=+0.0979, Sharpe=+1.0088

**BH-FDR Gate**: 1/8 top rejects are profitable (12%)

- `combo_tri_median__max_up_ret__smooth_momentum_structure__first_bar_sentiment`: Train IC=+0.0830, Lock IC=+0.0744, Sharpe=+0.6203

**B3 Composite Floor**: 13/15 top rejects are profitable (87%)

- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788
- `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1912, Lock IC=+0.0954, Sharpe=+0.5787
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.1424, Lock IC=+0.0686, Sharpe=+0.4355

**B6 Yearly IC CV Gate**: 9/9 top rejects are profitable (100%)

- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1429, Lock IC=+0.0568, Sharpe=+1.4431
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904
- `combo_tri_min__smooth_momentum_structure__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904

**B6 Temporal Stability Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2670, Lock IC=+0.1103, Sharpe=+1.1260

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__volatility_expansion_trend_vector`: Train IC=+0.2537, Lock IC=+0.1136, Sharpe=+1.0585
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2665, Lock IC=+0.1105, Sharpe=+0.9584
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__first_bar_sentiment`: Train IC=+0.2651, Lock IC=+0.1143, Sharpe=+0.9484

**Adaptive Correlation Gate**: 18/20 top rejects are profitable (90%)

- `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.1884, Lock IC=+0.0934, Sharpe=+1.2539
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2272, Lock IC=+0.0972, Sharpe=+1.0190
- `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2317, Lock IC=+0.1200, Sharpe=+0.9907

### 159915ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.1924, Lock IC=+0.1128, Sharpe=+1.2866
- `combo_tri_min__max_up_ret__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.2045, Lock IC=+0.0681, Sharpe=+1.1823

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_tri_median__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2186, Lock IC=+0.1202, Sharpe=+1.0165

**Temporal Validation Gate**: 12/20 top rejects are profitable (60%)

- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1912, Lock IC=+0.1181, Sharpe=+1.0501

**BH-FDR Gate**: 2/4 top rejects are profitable (50%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0763, Lock IC=+0.1143, Sharpe=+0.2104
- `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector`: Train IC=+0.0869, Lock IC=+0.0809, Sharpe=+0.1650

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__impulse_bar_dominance`: Train IC=+0.2037, Lock IC=+0.1093, Sharpe=+1.1046
- `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.1927, Lock IC=+0.0859, Sharpe=+0.7701
- `combo_tri_z_mean__opening_drive_thrust_ratio__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.1927, Lock IC=+0.0859, Sharpe=+0.7701

**B6 Temporal Stability Gate**: 8/8 top rejects are profitable (100%)

- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2408, Lock IC=+0.1206, Sharpe=+0.8251
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2408, Lock IC=+0.1206, Sharpe=+0.8251
- `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2131, Lock IC=+0.1080, Sharpe=+0.2128

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229
- `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2798, Lock IC=+0.1292, Sharpe=+1.7062
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2883, Lock IC=+0.1316, Sharpe=+1.5821

**Adaptive Correlation Gate**: 13/13 top rejects are profitable (100%)

- `combo_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2118, Lock IC=+0.1343, Sharpe=+1.6634
- `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1458, Lock IC=+0.1083, Sharpe=+1.5271
- `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2219, Lock IC=+0.1284, Sharpe=+1.2074

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1196 | 78 | 29 | 37 | 12 | 37% | 15% |
| B2 Rolling Guard | 143 | 78 | 34 | 21 | 23 | 44% | 29% |
| Temporal Validation Gate | 95 | 78 | 11 | 34 | 33 | 14% | 42% |
| BH-FDR Gate | 12 | 12 | 9 | 2 | 1 | 75% | 8% |
| B3 Composite Floor | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B6 Yearly IC CV Gate | 18 | 18 | 13 | 4 | 1 | 72% | 6% |
| B4 Correlation Gate | 255 | 78 | 19 | 12 | 47 | 24% | 60% |
| Adaptive Correlation Gate | 14 | 14 | 5 | 2 | 7 | 36% | 50% |

**B2 Rolling Guard** — top TP casualties:
- `combo_mean__bar_ret_0__demark_setup_reversal_early`: Train IC=+0.0661, Lock IC=+0.0010, Sharpe=+0.6498
- `combo_z_sum__bar_ret_0__demark_setup_reversal_early`: Train IC=+0.0661, Lock IC=+0.0010, Sharpe=+0.6498
- `combo_mean__first_bar_return__demark_setup_reversal_early`: Train IC=+0.0656, Lock IC=+0.0011, Sharpe=+0.6498

**Temporal Validation Gate** — top TP casualties:
- `sma100_dist`: Train IC=+0.1056, Lock IC=+0.0455, Sharpe=+0.6172
- `sma10_dist`: Train IC=+0.0626, Lock IC=+0.0444, Sharpe=+0.5378
- `keltner_position_atr10_20d`: Train IC=+0.0207, Lock IC=+0.0265, Sharpe=+0.5125

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2291, Lock IC=+0.0645, Sharpe=+0.9458
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2502, Lock IC=+0.0505, Sharpe=+0.7439
- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1904, Lock IC=+0.0192, Sharpe=+0.6828

**Adaptive Correlation Gate** — top TP casualties:
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1458, Lock IC=+0.0531, Sharpe=+0.6589
- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Sharpe=+0.5172
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1971, Lock IC=+0.0093, Sharpe=+0.3898

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1903 | 78 | 29 | 18 | 31 | 37% | 40% |
| B2 Rolling Guard | 357 | 78 | 15 | 14 | 49 | 19% | 63% |
| Temporal Validation Gate | 133 | 78 | 22 | 7 | 49 | 28% | 63% |
| BH-FDR Gate | 8 | 8 | 1 | 6 | 1 | 12% | 12% |
| B3 Composite Floor | 15 | 15 | 0 | 2 | 13 | 0% | 87% |
| B6 Yearly IC CV Gate | 9 | 9 | 0 | 0 | 9 | 0% | 100% |
| B6 Temporal Stability Gate | 221 | 78 | 0 | 5 | 73 | 0% | 94% |
| B4 Correlation Gate | 533 | 78 | 0 | 0 | 78 | 0% | 100% |
| Adaptive Correlation Gate | 21 | 21 | 0 | 2 | 19 | 0% | 90% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Sharpe=+1.1505

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_min__star50_limit_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1346, Lock IC=+0.0442, Sharpe=+1.2935
- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Sharpe=+1.2071

**Temporal Validation Gate** — top TP casualties:
- `close_location_in_range_3d`: Train IC=+0.0449, Lock IC=+0.0506, Sharpe=+1.3268
- `combo_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621
- `combo_z_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788
- `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1912, Lock IC=+0.0954, Sharpe=+0.5787
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.1424, Lock IC=+0.0686, Sharpe=+0.4355

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1429, Lock IC=+0.0568, Sharpe=+1.4431
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904
- `combo_tri_min__smooth_momentum_structure__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.1440, Lock IC=+0.0617, Sharpe=+1.2904

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2594, Lock IC=+0.1176, Sharpe=+1.2041
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2670, Lock IC=+0.1103, Sharpe=+1.1260

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2051, Lock IC=+0.1194, Sharpe=+1.2468
- `combo_rank_min__star50_limit_proximity_early__opening_momentum_score`: Train IC=+0.2051, Lock IC=+0.1194, Sharpe=+1.2468
- `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`: Train IC=+0.2045, Lock IC=+0.0898, Sharpe=+1.0714

**Adaptive Correlation Gate** — top TP casualties:
- `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.1884, Lock IC=+0.0934, Sharpe=+1.2539
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2272, Lock IC=+0.0972, Sharpe=+1.0190
- `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2317, Lock IC=+0.1200, Sharpe=+0.9907

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1022 | 78 | 27 | 12 | 39 | 35% | 50% |
| B2 Rolling Guard | 216 | 78 | 18 | 10 | 50 | 23% | 64% |
| Temporal Validation Gate | 27 | 27 | 11 | 3 | 13 | 41% | 48% |
| BH-FDR Gate | 4 | 4 | 0 | 2 | 2 | 0% | 50% |
| B3 Composite Floor | 77 | 77 | 1 | 3 | 73 | 1% | 95% |
| B6 Yearly IC CV Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B6 Temporal Stability Gate | 8 | 8 | 0 | 0 | 8 | 0% | 100% |
| B4 Correlation Gate | 317 | 78 | 0 | 2 | 76 | 0% | 97% |
| Adaptive Correlation Gate | 13 | 13 | 0 | 0 | 13 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.1924, Lock IC=+0.1128, Sharpe=+1.2866

**B2 Rolling Guard** — top TP casualties:
- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.1826, Lock IC=+0.1317, Sharpe=+1.2186

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1823, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1912, Lock IC=+0.1181, Sharpe=+1.0501

**BH-FDR Gate** — top TP casualties:
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0763, Lock IC=+0.1143, Sharpe=+0.2104
- `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector`: Train IC=+0.0869, Lock IC=+0.0809, Sharpe=+0.1650

**B3 Composite Floor** — top TP casualties:
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.1306, Lock IC=+0.0712, Sharpe=+1.1859
- `combo_rank_min__first_bar_sentiment__first_bar_return`: Train IC=+0.1306, Lock IC=+0.0712, Sharpe=+1.1859
- `combo_rank_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1518, Lock IC=+0.0800, Sharpe=+1.1719

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2408, Lock IC=+0.1206, Sharpe=+0.8251
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2408, Lock IC=+0.1206, Sharpe=+0.8251
- `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2131, Lock IC=+0.1080, Sharpe=+0.2128

**B4 Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Sharpe=+1.8009
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2717, Lock IC=+0.1211, Sharpe=+1.8009

**Adaptive Correlation Gate** — top TP casualties:
- `combo_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2118, Lock IC=+0.1343, Sharpe=+1.6634
- `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1458, Lock IC=+0.1083, Sharpe=+1.5271
- `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2219, Lock IC=+0.1284, Sharpe=+1.2074

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (95 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 90 | 50 | 9 | 14 | 27 | 18% | 28% |
| recency_ratio >= 2.5 (late-concentrated) | 5 | 5 | 0 | 5 | 0 | 0% | 100% |

**Top TP killed by recency_ratio cap:**
- `combo_tri_mean__volume_weighted_momentum_acceleration__first_bar_return__bar_body_rng_0`: Train IC=+0.1352, Lock IC=+0.0188, Sharpe=+0.2741
- `combo_tri_z_mean__volume_weighted_momentum_acceleration__first_bar_return__bar_body_rng_0`: Train IC=+0.1352, Lock IC=+0.0188, Sharpe=+0.2741
- `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__bar_body_rng_0`: Train IC=+0.1350, Lock IC=+0.0187, Sharpe=+0.2741
- `combo_tri_z_mean__volume_weighted_momentum_acceleration__bar_ret_0__bar_body_rng_0`: Train IC=+0.1350, Lock IC=+0.0187, Sharpe=+0.2741
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Train IC=+0.1520, Lock IC=+0.0302, Sharpe=+0.0799

### 500ETF — `single` (133 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 132 | 50 | 0 | 48 | 2 | 0% | 96% |
| recency_ratio >= 2.5 (late-concentrated) | 1 | 1 | 0 | 0 | 1 | 0% | 0% |

### 159915ETF — `single` (27 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 27 | 27 | 11 | 13 | 3 | 41% | 48% |

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is higher (d=+1.73). Threshold 0.839 → 88% accuracy.
- `half_ratio`: FP is higher (d=+1.10). Threshold 1.035 → 82% accuracy.
- `recency_ratio`: FP is higher (d=+0.75). Threshold 2.542 → 76% accuracy.
- `n_negative_regimes`: FP is higher (d=+0.71). Threshold 0.500 → 76% accuracy.
- `n_negative_years`: FP is higher (d=+0.60). Threshold 1.500 → 76% accuracy.
- `ic_std_across_regimes`: FP is higher (d=+0.56). Threshold 0.054 → 76% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/5
- Decaying signal (half ratio < 0.3): 0/5
- Weak component (CV > 2.0): 0/5
- Regime-dependent (≥2 negative regimes): 0/5

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_weighted_price_position` | 3 | 2 | 5 | 60% |  |
| `max_up_ret` | 4 | 16 | 20 | 20% |  |
| `volume_weighted_momentum_acceleration` | 1 | 4 | 5 | 20% |  |
| `volatility_expansion_trend_vector` | 1 | 5 | 6 | 17% |  |
| `opening_drive_thrust_ratio` | 2 | 13 | 15 | 13% |  |
| `first_bar_return` | 1 | 8 | 9 | 11% |  |
| `first_bar_sentiment` | 1 | 11 | 12 | 8% |  |
| `impulse_bar_dominance` | 0 | 2 | 2 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 2 | 2 | 0% |  |
| `bar_ret_0` | 0 | 5 | 5 | 0% |  |
| `volume_surge_direction` | 0 | 2 | 2 | 0% |  |
| `net_volume_flow` | 0 | 5 | 5 | 0% |  |
| `star50_limit_proximity_early` | 0 | 5 | 5 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 4 | 4 | 0% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |
| `close_vs_open_range` | 0 | 2 | 2 | 0% |  |
| `max_down_ret` | 0 | 2 | 2 | 0% |  |
| `bar_body_rng_0` | 0 | 13 | 13 | 0% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `body_size_progression` | 0 | 2 | 2 | 0% |  |
| `smooth_momentum_structure` | 0 | 2 | 2 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 15 | 15 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=3, TP=16, FP rate=16%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=6, FP rate=14%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=1, TP=24, FP rate=4%

