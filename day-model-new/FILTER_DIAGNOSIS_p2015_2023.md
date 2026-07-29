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
| 300ETF | single | 20 | 1 | 2 | 17 | 5% | 0.64 |
| 500ETF | single | 43 | 1 | 4 | 38 | 2% | 0.86 |
| 159915ETF | single | 22 | 1 | 1 | 20 | 5% | 0.89 |

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

**`combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=-0.0017, Sharpe=-0.6567)
- Admission: Train IC=+0.1107, Deflated=+0.1113, IR=0.47, Mono=0.66, p=0.0288, MaxCorr=0.55
- Yearly Linear ICs: 2015: -0.039 | 2016: +0.011 | 2017: +0.011 | 2018: +0.104 | 2019: +0.066 | 2020: +0.017 | 2021: +0.093 | 2022: +0.021 | 2023: +0.065 | 2024: -0.026 | 2025: +0.040 | 2026: -0.175
- Yearly Tail ICs:   2015: +0.076 | 2016: -0.009 | 2017: +0.221 | 2018: +0.166 | 2019: +0.179 | 2020: +0.069 | 2021: +0.225 | 2022: +0.060 | 2023: +0.169 | 2024: +0.013 | 2025: +0.061 | 2026: -0.265
- IC CV=1.27, Neg years (linear/tail)=1/1 of 8, Half ratio=2.11, Recency ratio=-4.04
- Early IC=-0.0141, Recent IC=+0.0570, 1st-half IC=+0.0228, 2nd-half IC=+0.0481, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18, neg years=1)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.018, Q3_mid=+0.038, Q4=+0.073, Q5_high_vol=+0.021

### 500ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__close_vs_open_range`** (Lock IC=-0.0211, Sharpe=-0.4893)
- Admission: Train IC=+0.1933, Deflated=+0.1943, IR=0.53, Mono=0.67, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.048 | 2017: +0.100 | 2018: +0.185 | 2019: +0.059 | 2020: +0.099 | 2021: -0.069 | 2022: +0.102 | 2023: +0.016 | 2024: +0.009 | 2025: -0.094 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.169 | 2016: +0.222 | 2017: -0.013 | 2018: +0.301 | 2019: +0.160 | 2020: +0.234 | 2021: +0.174 | 2022: +0.173 | 2023: +0.012 | 2024: +0.062 | 2025: -0.343 | 2026: -0.446
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=0.50, Recency ratio=0.17
- Early IC=+0.0963, Recent IC=+0.0165, 1st-half IC=+0.1252, 2nd-half IC=+0.0631, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47, neg years=0)
- Regime ICs: Q1_low_vol=+0.044, Q2=-0.025, Q3_mid=+0.045, Q4=+0.093, Q5_high_vol=+0.240

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0132, Sharpe=-0.5256)
- Admission: Train IC=+0.1499, Deflated=+0.1520, IR=0.47, Mono=0.71, p=0.0022, MaxCorr=0.40
- Yearly Linear ICs: 2015: +0.026 | 2016: +0.053 | 2017: +0.097 | 2018: +0.128 | 2019: -0.015 | 2020: +0.094 | 2021: +0.082 | 2022: -0.005 | 2023: +0.054 | 2024: -0.052 | 2025: -0.026 | 2026: -0.001
- Yearly Tail ICs:   2015: -0.010 | 2016: +0.087 | 2017: +0.065 | 2018: +0.280 | 2019: +0.087 | 2020: +0.152 | 2021: +0.316 | 2022: +0.144 | 2023: +0.164 | 2024: +0.085 | 2025: -0.016 | 2026: -0.201
- IC CV=0.84, Neg years (linear/tail)=2/1 of 8, Half ratio=0.53, Recency ratio=0.98
- Early IC=+0.0394, Recent IC=+0.0386, 1st-half IC=+0.0765, 2nd-half IC=+0.0405, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.011, Q3_mid=+0.095, Q4=+0.042, Q5_high_vol=+0.091

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_rel_diff__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0522, Sharpe=-0.1443)
- Admission: Train IC=+0.1925, Deflated=+0.1927, IR=0.59, Mono=0.74, p=0.0002, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.082 | 2016: +0.035 | 2017: -0.003 | 2018: +0.108 | 2019: +0.086 | 2020: -0.003 | 2021: +0.142 | 2022: +0.100 | 2023: +0.032 | 2024: -0.039 | 2025: +0.093 | 2026: +0.203
- Yearly Tail ICs:   2015: +0.169 | 2016: +0.259 | 2017: +0.032 | 2018: +0.316 | 2019: +0.176 | 2020: +0.192 | 2021: +0.253 | 2022: +0.266 | 2023: -0.139 | 2024: +0.210 | 2025: -0.025 | 2026: +0.382
- IC CV=0.73, Neg years (linear/tail)=2/0 of 8, Half ratio=1.82, Recency ratio=2.07
- Early IC=+0.0585, Recent IC=+0.1208, 1st-half IC=+0.0492, 2nd-half IC=+0.0894, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.006, Q2=+0.019, Q3_mid=+0.047, Q4=+0.162, Q5_high_vol=+0.103

**`combo_ratio__first_bar_sentiment__volume_surge_direction`** (Lock IC=+0.0048, Sharpe=-0.5873)
- Admission: Train IC=+0.1333, Deflated=+0.1336, IR=0.52, Mono=0.72, p=0.0092, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.083 | 2016: +0.112 | 2017: +0.044 | 2018: +0.089 | 2019: +0.064 | 2020: -0.038 | 2021: +0.135 | 2022: +0.019 | 2023: +0.058 | 2024: -0.051 | 2025: +0.006 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.250 | 2017: -0.084 | 2018: +0.104 | 2019: +0.145 | 2020: +0.030 | 2021: +0.411 | 2022: +0.051 | 2023: -0.030 | 2024: +0.059 | 2025: -0.149 | 2026: -0.034
- IC CV=0.81, Neg years (linear/tail)=1/1 of 8, Half ratio=0.58, Recency ratio=0.79
- Early IC=+0.0977, Recent IC=+0.0770, 1st-half IC=+0.0834, 2nd-half IC=+0.0487, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.97)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.042, Q3_mid=+0.077, Q4=+0.064, Q5_high_vol=+0.086

### 500ETF — `single` Median Features

**`combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0862, Sharpe=-0.3387)
- Admission: Train IC=+0.2526, Deflated=+0.2535, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.054 | 2017: +0.162 | 2018: +0.182 | 2019: +0.149 | 2020: +0.192 | 2021: +0.148 | 2022: +0.007 | 2023: +0.105 | 2024: +0.096 | 2025: +0.071 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.238 | 2016: +0.227 | 2017: +0.124 | 2018: +0.440 | 2019: +0.144 | 2020: +0.106 | 2021: +0.405 | 2022: +0.156 | 2023: -0.124 | 2024: +0.008 | 2025: +0.083 | 2026: +0.182
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.59
- Early IC=+0.1313, Recent IC=+0.0776, 1st-half IC=+0.1603, 2nd-half IC=+0.1308, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.059, Q3_mid=+0.135, Q4=+0.105, Q5_high_vol=+0.235

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0726, Sharpe=-0.7944)
- Admission: Train IC=+0.2962, Deflated=+0.2969, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.143 | 2017: +0.182 | 2018: +0.238 | 2019: +0.137 | 2020: +0.141 | 2021: +0.083 | 2022: +0.110 | 2023: +0.072 | 2024: +0.084 | 2025: +0.103 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.220 | 2017: +0.379 | 2018: +0.451 | 2019: +0.259 | 2020: +0.199 | 2021: +0.009 | 2022: +0.313 | 2023: +0.114 | 2024: +0.090 | 2025: +0.096 | 2026: -0.181
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.48
- Early IC=+0.2006, Recent IC=+0.0965, 1st-half IC=+0.2220, 2nd-half IC=+0.1210, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.005, Q3_mid=+0.193, Q4=+0.190, Q5_high_vol=+0.225

**`combo_sig_product__first_bar_sentiment__close_vs_open_range`** (Lock IC=+0.0673, Sharpe=-0.4527)
- Admission: Train IC=+0.1815, Deflated=+0.1822, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.125 | 2017: +0.122 | 2018: +0.138 | 2019: +0.115 | 2020: +0.099 | 2021: +0.054 | 2022: +0.122 | 2023: +0.083 | 2024: +0.067 | 2025: +0.078 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.068 | 2017: +0.110 | 2018: +0.150 | 2019: +0.214 | 2020: +0.072 | 2021: +0.113 | 2022: +0.284 | 2023: +0.170 | 2024: -0.104 | 2025: +0.127 | 2026: +0.176
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.46
- Early IC=+0.1924, Recent IC=+0.0880, 1st-half IC=+0.1623, 2nd-half IC=+0.1033, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.110, Q2=-0.025, Q3_mid=+0.162, Q4=+0.176, Q5_high_vol=+0.187

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0475, Sharpe=-0.0575)
- Admission: Train IC=+0.2446, Deflated=+0.2447, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.133 | 2017: +0.056 | 2018: +0.080 | 2019: -0.018 | 2020: +0.052 | 2021: -0.087 | 2022: +0.104 | 2023: +0.041 | 2024: -0.013 | 2025: +0.085 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.208 | 2016: +0.216 | 2017: +0.284 | 2018: +0.257 | 2019: -0.016 | 2020: +0.195 | 2021: +0.191 | 2022: +0.161 | 2023: -0.139 | 2024: +0.214 | 2025: +0.049 | 2026: +0.234
- IC CV=1.25, Neg years (linear/tail)=2/1 of 8, Half ratio=0.12, Recency ratio=0.06
- Early IC=+0.1364, Recent IC=+0.0088, 1st-half IC=+0.1316, 2nd-half IC=+0.0156, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.003, Q3_mid=+0.040, Q4=+0.114, Q5_high_vol=+0.124

### 159915ETF — `single` Median Features

**`combo_rank_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1018, Sharpe=-0.0105)
- Admission: Train IC=+0.2317, Deflated=+0.2328, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.162 | 2016: -0.004 | 2017: -0.050 | 2018: +0.063 | 2019: +0.110 | 2020: +0.080 | 2021: +0.018 | 2022: +0.163 | 2023: +0.109 | 2024: +0.072 | 2025: +0.124 | 2026: +0.118
- Yearly Tail ICs:   2015: +0.176 | 2016: +0.025 | 2017: -0.099 | 2018: +0.344 | 2019: +0.188 | 2020: +0.339 | 2021: +0.105 | 2022: +0.514 | 2023: +0.128 | 2024: +0.070 | 2025: +0.084 | 2026: +0.231
- IC CV=1.06, Neg years (linear/tail)=2/1 of 8, Half ratio=1.29, Recency ratio=1.16
- Early IC=+0.0786, Recent IC=+0.0908, 1st-half IC=+0.0757, 2nd-half IC=+0.0974, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.065, Q3_mid=+0.118, Q4=+0.085, Q5_high_vol=+0.122

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0706, Sharpe=+0.8555)
- Admission: Train IC=+0.2691, Deflated=+0.2697, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.117 | 2017: -0.053 | 2018: +0.140 | 2019: +0.099 | 2020: +0.074 | 2021: +0.143 | 2022: +0.037 | 2023: +0.135 | 2024: +0.055 | 2025: +0.049 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.398 | 2016: +0.177 | 2017: -0.045 | 2018: +0.311 | 2019: +0.294 | 2020: +0.171 | 2021: +0.368 | 2022: +0.249 | 2023: +0.127 | 2024: +0.392 | 2025: +0.055 | 2026: +0.139
- IC CV=0.84, Neg years (linear/tail)=1/1 of 8, Half ratio=0.59, Recency ratio=0.47
- Early IC=+0.1915, Recent IC=+0.0900, 1st-half IC=+0.1476, 2nd-half IC=+0.0872, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.005, Q2=+0.021, Q3_mid=+0.037, Q4=+0.214, Q5_high_vol=+0.205

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0776, Sharpe=+0.8447)
- Admission: Train IC=+0.2226, Deflated=+0.2238, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.097 | 2017: +0.052 | 2018: +0.199 | 2019: +0.090 | 2020: +0.000 | 2021: +0.126 | 2022: +0.037 | 2023: +0.151 | 2024: +0.061 | 2025: +0.066 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.019 | 2017: +0.121 | 2018: +0.385 | 2019: +0.292 | 2020: +0.127 | 2021: +0.215 | 2022: +0.280 | 2023: +0.335 | 2024: +0.166 | 2025: +0.173 | 2026: +0.220
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.62
- Early IC=+0.1323, Recent IC=+0.0817, 1st-half IC=+0.1359, 2nd-half IC=+0.0664, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.037, Q3_mid=+0.068, Q4=+0.124, Q5_high_vol=+0.172

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0876, Sharpe=+0.7186)
- Admission: Train IC=+0.2593, Deflated=+0.2602, IR=0.67, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.71, Recency ratio=0.71
- Early IC=+0.1376, Recent IC=+0.0979, 1st-half IC=+0.1324, 2nd-half IC=+0.0936, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.028, Q2=+0.039, Q3_mid=+0.076, Q4=+0.186, Q5_high_vol=+0.196

**`combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0675, Sharpe=+0.6210)
- Admission: Train IC=+0.2241, Deflated=+0.2247, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.111 | 2017: +0.068 | 2018: +0.203 | 2019: +0.091 | 2020: +0.013 | 2021: +0.144 | 2022: +0.034 | 2023: +0.146 | 2024: +0.067 | 2025: +0.054 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.204 | 2016: +0.090 | 2017: +0.137 | 2018: +0.275 | 2019: +0.230 | 2020: +0.126 | 2021: +0.282 | 2022: +0.252 | 2023: +0.309 | 2024: +0.212 | 2025: -0.023 | 2026: -0.248
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.87
- Early IC=+0.1032, Recent IC=+0.0893, 1st-half IC=+0.1227, 2nd-half IC=+0.0759, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.044, Q3_mid=+0.078, Q4=+0.120, Q5_high_vol=+0.160

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`** (Lock IC=+0.0529, Sharpe=+0.5709)
- Admission: Train IC=+0.1929, Deflated=+0.1930, IR=0.43, Mono=0.67, p=0.0002, MaxCorr=0.52
- Yearly Linear ICs: 2015: +0.129 | 2016: +0.085 | 2017: +0.014 | 2018: +0.127 | 2019: +0.038 | 2020: -0.016 | 2021: +0.121 | 2022: +0.069 | 2023: +0.055 | 2024: -0.005 | 2025: +0.070 | 2026: +0.139
- Yearly Tail ICs:   2015: +0.242 | 2016: +0.174 | 2017: +0.147 | 2018: +0.348 | 2019: +0.075 | 2020: -0.140 | 2021: +0.285 | 2022: +0.078 | 2023: +0.036 | 2024: +0.203 | 2025: +0.162 | 2026: +0.190
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=0.59, Recency ratio=0.89
- Early IC=+0.1072, Recent IC=+0.0952, 1st-half IC=+0.0984, 2nd-half IC=+0.0578, Neg regimes=1/5
- Weak component: `bar_vol_0` (CV=1.91)
- Regime ICs: Q1_low_vol=+0.052, Q2=-0.012, Q3_mid=+0.030, Q4=+0.136, Q5_high_vol=+0.133

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0755, Sharpe=+0.5654)
- Admission: Train IC=+0.2800, Deflated=+0.2807, IR=0.74, Mono=0.72, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.096 | 2017: +0.009 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132 | 2022: +0.037 | 2023: +0.176 | 2024: +0.054 | 2025: +0.048 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.333 | 2016: +0.092 | 2017: +0.103 | 2018: +0.397 | 2019: +0.266 | 2020: +0.232 | 2021: +0.485 | 2022: +0.150 | 2023: +0.333 | 2024: +0.235 | 2025: -0.037 | 2026: +0.148
- IC CV=0.70, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.48
- Early IC=+0.1754, Recent IC=+0.0845, 1st-half IC=+0.1567, 2nd-half IC=+0.0837, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.034, Q3_mid=+0.069, Q4=+0.186, Q5_high_vol=+0.207

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0567, Sharpe=+0.4294)
- Admission: Train IC=+0.2244, Deflated=+0.2251, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.054 | 2017: +0.002 | 2018: +0.173 | 2019: +0.051 | 2020: -0.002 | 2021: +0.178 | 2022: +0.055 | 2023: +0.191 | 2024: +0.025 | 2025: +0.114 | 2026: -0.181
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.202 | 2017: +0.155 | 2018: +0.396 | 2019: +0.184 | 2020: +0.071 | 2021: +0.366 | 2022: +0.371 | 2023: +0.352 | 2024: +0.077 | 2025: +0.083 | 2026: +0.009
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=0.72, Recency ratio=1.37
- Early IC=+0.0853, Recent IC=+0.1167, 1st-half IC=+0.1042, 2nd-half IC=+0.0751, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.029, Q3_mid=+0.076, Q4=+0.086, Q5_high_vol=+0.173

**`combo_tri_min__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0510, Sharpe=+0.4110)
- Admission: Train IC=+0.2233, Deflated=+0.2247, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.073 | 2017: +0.024 | 2018: +0.218 | 2019: +0.099 | 2020: -0.020 | 2021: +0.170 | 2022: +0.076 | 2023: +0.173 | 2024: -0.011 | 2025: +0.061 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.124 | 2016: -0.047 | 2017: +0.156 | 2018: +0.252 | 2019: +0.239 | 2020: +0.041 | 2021: +0.476 | 2022: +0.340 | 2023: +0.437 | 2024: -0.169 | 2025: +0.006 | 2026: -0.079
- IC CV=0.76, Neg years (linear/tail)=1/1 of 8, Half ratio=0.74, Recency ratio=1.40
- Early IC=+0.0879, Recent IC=+0.1232, 1st-half IC=+0.1141, 2nd-half IC=+0.0842, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.082, Q3_mid=+0.101, Q4=+0.088, Q5_high_vol=+0.151

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0701, Sharpe=+0.3915)
- Admission: Train IC=+0.1467, Deflated=+0.1473, IR=0.45, Mono=0.66, p=0.0036, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.068 | 2017: +0.035 | 2018: +0.194 | 2019: +0.043 | 2020: +0.043 | 2021: +0.166 | 2022: +0.016 | 2023: +0.161 | 2024: +0.115 | 2025: +0.020 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.171 | 2017: +0.145 | 2018: +0.374 | 2019: +0.142 | 2020: +0.041 | 2021: +0.228 | 2022: +0.005 | 2023: +0.249 | 2024: +0.150 | 2025: -0.023 | 2026: -0.122
- IC CV=0.73, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=1.10
- Early IC=+0.0829, Recent IC=+0.0913, 1st-half IC=+0.1088, 2nd-half IC=+0.0686, Neg regimes=0/5
- Weak component: `early_vwap_acceleration` (CV=1.17)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.049, Q3_mid=+0.062, Q4=+0.162, Q5_high_vol=+0.129

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0529, Sharpe=+0.3808)
- Admission: Train IC=+0.2417, Deflated=+0.2421, IR=0.59, Mono=0.70, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.116 | 2017: -0.045 | 2018: +0.205 | 2019: +0.113 | 2020: +0.057 | 2021: +0.160 | 2022: +0.086 | 2023: +0.108 | 2024: +0.009 | 2025: +0.063 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.204 | 2017: -0.023 | 2018: +0.348 | 2019: +0.231 | 2020: +0.177 | 2021: +0.366 | 2022: +0.279 | 2023: +0.178 | 2024: +0.219 | 2025: +0.133 | 2026: +0.146
- IC CV=0.68, Neg years (linear/tail)=1/1 of 8, Half ratio=0.73, Recency ratio=0.79
- Early IC=+0.1556, Recent IC=+0.1228, 1st-half IC=+0.1413, 2nd-half IC=+0.1029, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.043, Q3_mid=+0.079, Q4=+0.193, Q5_high_vol=+0.188

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0703, Sharpe=+0.3240)
- Admission: Train IC=+0.2764, Deflated=+0.2775, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.90, Neg years (linear/tail)=1/0 of 8, Half ratio=0.73, Recency ratio=0.73
- Early IC=+0.1479, Recent IC=+0.1075, 1st-half IC=+0.1387, 2nd-half IC=+0.1018, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.02)
- Regime ICs: Q1_low_vol=-0.016, Q2=+0.030, Q3_mid=+0.061, Q4=+0.251, Q5_high_vol=+0.183

**`combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0566, Sharpe=+0.3084)
- Admission: Train IC=+0.2409, Deflated=+0.2417, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.085 | 2017: +0.041 | 2018: +0.223 | 2019: +0.065 | 2020: -0.027 | 2021: +0.144 | 2022: +0.066 | 2023: +0.176 | 2024: +0.015 | 2025: +0.079 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.009 | 2017: +0.244 | 2018: +0.342 | 2019: +0.286 | 2020: +0.034 | 2021: +0.424 | 2022: +0.323 | 2023: +0.363 | 2024: +0.080 | 2025: -0.074 | 2026: -0.164
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.51, Recency ratio=1.11
- Early IC=+0.0948, Recent IC=+0.1049, 1st-half IC=+0.1270, 2nd-half IC=+0.0651, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.073, Q3_mid=+0.100, Q4=+0.084, Q5_high_vol=+0.150

**`combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=+0.0591, Sharpe=+0.2819)
- Admission: Train IC=+0.1799, Deflated=+0.1818, IR=0.49, Mono=0.70, p=0.0002, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.074 | 2016: +0.088 | 2017: -0.045 | 2018: +0.216 | 2019: +0.095 | 2020: +0.051 | 2021: +0.124 | 2022: +0.054 | 2023: +0.133 | 2024: +0.010 | 2025: +0.099 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.183 | 2016: +0.054 | 2017: -0.157 | 2018: +0.314 | 2019: +0.254 | 2020: +0.197 | 2021: +0.296 | 2022: +0.127 | 2023: +0.296 | 2024: +0.156 | 2025: +0.339 | 2026: -0.229
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=0.90, Recency ratio=1.13
- Early IC=+0.0787, Recent IC=+0.0886, 1st-half IC=+0.0932, 2nd-half IC=+0.0837, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.97)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.006, Q3_mid=+0.094, Q4=+0.137, Q5_high_vol=+0.124

**`combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.0581, Sharpe=+0.1301)
- Admission: Train IC=+0.2047, Deflated=+0.2058, IR=0.49, Mono=0.73, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.040 | 2017: -0.102 | 2018: +0.113 | 2019: +0.071 | 2020: +0.037 | 2021: +0.108 | 2022: +0.104 | 2023: +0.028 | 2024: +0.006 | 2025: +0.040 | 2026: +0.169
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.196 | 2017: -0.027 | 2018: +0.280 | 2019: +0.198 | 2020: +0.223 | 2021: +0.141 | 2022: +0.238 | 2023: -0.209 | 2024: +0.189 | 2025: -0.019 | 2026: +0.320
- IC CV=1.14, Neg years (linear/tail)=1/1 of 8, Half ratio=0.76, Recency ratio=0.91
- Early IC=+0.1168, Recent IC=+0.1063, 1st-half IC=+0.1047, 2nd-half IC=+0.0794, Neg regimes=2/5
- Weak component: `limit_down_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.041, Q2=-0.011, Q3_mid=+0.014, Q4=+0.209, Q5_high_vol=+0.158

**`combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0581, Sharpe=+0.1301)
- Admission: Train IC=+0.2047, Deflated=+0.2058, IR=0.49, Mono=0.73, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.040 | 2017: -0.102 | 2018: +0.113 | 2019: +0.071 | 2020: +0.037 | 2021: +0.108 | 2022: +0.104 | 2023: +0.028 | 2024: +0.006 | 2025: +0.040 | 2026: +0.169
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.196 | 2017: -0.027 | 2018: +0.280 | 2019: +0.198 | 2020: +0.223 | 2021: +0.141 | 2022: +0.238 | 2023: -0.209 | 2024: +0.189 | 2025: -0.019 | 2026: +0.320
- IC CV=1.13, Neg years (linear/tail)=1/1 of 8, Half ratio=0.76, Recency ratio=0.91
- Early IC=+0.1167, Recent IC=+0.1063, 1st-half IC=+0.1047, 2nd-half IC=+0.0794, Neg regimes=2/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.45)
- Regime ICs: Q1_low_vol=-0.041, Q2=-0.011, Q3_mid=+0.014, Q4=+0.209, Q5_high_vol=+0.158

**`combo_ratio__bar_ret_0__volume_surge_direction`** (Lock IC=+0.0383, Sharpe=+0.0933)
- Admission: Train IC=+0.1657, Deflated=+0.1665, IR=0.48, Mono=0.70, p=0.0010, MaxCorr=0.05
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.143 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.388 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.101
- IC CV=0.58, Neg years (linear/tail)=1/1 of 8, Half ratio=0.54, Recency ratio=0.79
- Early IC=+0.1140, Recent IC=+0.0901, 1st-half IC=+0.1201, 2nd-half IC=+0.0646, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.97)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.064, Q3_mid=+0.087, Q4=+0.099, Q5_high_vol=+0.138

**`combo_ratio__first_bar_return__volume_surge_direction`** (Lock IC=+0.0383, Sharpe=+0.0725)
- Admission: Train IC=+0.1657, Deflated=+0.1664, IR=0.48, Mono=0.70, p=0.0010, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.144 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.393 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.114
- IC CV=0.58, Neg years (linear/tail)=1/1 of 8, Half ratio=0.54, Recency ratio=0.79
- Early IC=+0.1140, Recent IC=+0.0903, 1st-half IC=+0.1201, 2nd-half IC=+0.0646, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.97)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.064, Q3_mid=+0.087, Q4=+0.099, Q5_high_vol=+0.138

### 500ETF — `single` True Positives

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1058, Sharpe=+1.1405)
- Admission: Train IC=+0.2233, Deflated=+0.2239, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.66
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.121 | 2017: +0.105 | 2018: +0.199 | 2019: +0.090 | 2020: +0.107 | 2021: +0.138 | 2022: +0.091 | 2023: +0.051 | 2024: +0.124 | 2025: +0.140 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.434 | 2016: +0.180 | 2017: +0.216 | 2018: +0.386 | 2019: -0.033 | 2020: +0.112 | 2021: +0.323 | 2022: +0.086 | 2023: +0.203 | 2024: +0.170 | 2025: +0.262 | 2026: +0.288
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=0.59
- Early IC=+0.1937, Recent IC=+0.1144, 1st-half IC=+0.1889, 2nd-half IC=+0.1066, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.034, Q3_mid=+0.109, Q4=+0.170, Q5_high_vol=+0.234

**`combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1141, Sharpe=+0.9327)
- Admission: Train IC=+0.3150, Deflated=+0.3172, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.071 | 2017: +0.223 | 2018: +0.168 | 2019: +0.131 | 2020: +0.141 | 2021: +0.143 | 2022: +0.028 | 2023: +0.100 | 2024: +0.152 | 2025: +0.106 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.287 | 2016: +0.141 | 2017: +0.343 | 2018: +0.419 | 2019: +0.314 | 2020: +0.267 | 2021: +0.138 | 2022: +0.274 | 2023: +0.112 | 2024: +0.289 | 2025: -0.048 | 2026: +0.166
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.56
- Early IC=+0.1519, Recent IC=+0.0855, 1st-half IC=+0.1810, 2nd-half IC=+0.1170, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.019, Q3_mid=+0.161, Q4=+0.185, Q5_high_vol=+0.171

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1215, Sharpe=+0.9205)
- Admission: Train IC=+0.3075, Deflated=+0.3095, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.045 | 2017: +0.226 | 2018: +0.140 | 2019: +0.157 | 2020: +0.154 | 2021: +0.138 | 2022: +0.032 | 2023: +0.096 | 2024: +0.174 | 2025: +0.105 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.163 | 2017: +0.307 | 2018: +0.406 | 2019: +0.362 | 2020: +0.212 | 2021: +0.216 | 2022: +0.114 | 2023: +0.006 | 2024: +0.367 | 2025: +0.039 | 2026: +0.231
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.52
- Early IC=+0.1578, Recent IC=+0.0828, 1st-half IC=+0.1832, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.041, Q3_mid=+0.153, Q4=+0.197, Q5_high_vol=+0.185

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1217, Sharpe=+0.8196)
- Admission: Train IC=+0.3308, Deflated=+0.3324, IR=1.12, Mono=0.86, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.121 | 2017: +0.223 | 2018: +0.184 | 2019: +0.172 | 2020: +0.173 | 2021: +0.142 | 2022: +0.014 | 2023: +0.106 | 2024: +0.167 | 2025: +0.090 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.402 | 2016: +0.204 | 2017: +0.346 | 2018: +0.521 | 2019: +0.344 | 2020: +0.241 | 2021: +0.291 | 2022: +0.168 | 2023: +0.117 | 2024: +0.321 | 2025: -0.031 | 2026: +0.176
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.39
- Early IC=+0.2006, Recent IC=+0.0784, 1st-half IC=+0.2191, 2nd-half IC=+0.1318, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.051, Q3_mid=+0.164, Q4=+0.217, Q5_high_vol=+0.217

**`combo_min__net_volume_flow__max_down_ret`** (Lock IC=+0.0986, Sharpe=+0.8052)
- Admission: Train IC=+0.2245, Deflated=+0.2270, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.059 | 2017: +0.190 | 2018: +0.134 | 2019: +0.105 | 2020: +0.123 | 2021: +0.085 | 2022: +0.107 | 2023: +0.085 | 2024: +0.116 | 2025: +0.140 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.307 | 2016: -0.078 | 2017: +0.227 | 2018: +0.131 | 2019: +0.322 | 2020: +0.272 | 2021: +0.261 | 2022: +0.265 | 2023: +0.211 | 2024: +0.310 | 2025: +0.156 | 2026: +0.079
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.72, Recency ratio=0.62
- Early IC=+0.1550, Recent IC=+0.0959, 1st-half IC=+0.1523, 2nd-half IC=+0.1090, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.033, Q3_mid=+0.179, Q4=+0.134, Q5_high_vol=+0.183

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1096, Sharpe=+0.7682)
- Admission: Train IC=+0.2893, Deflated=+0.2907, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.065 | 2017: +0.217 | 2018: +0.200 | 2019: +0.124 | 2020: +0.170 | 2021: +0.092 | 2022: +0.093 | 2023: +0.115 | 2024: +0.158 | 2025: +0.121 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.393 | 2016: +0.172 | 2017: +0.196 | 2018: +0.310 | 2019: +0.229 | 2020: +0.241 | 2021: +0.241 | 2022: +0.340 | 2023: +0.239 | 2024: +0.200 | 2025: +0.036 | 2026: -0.199
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.56
- Early IC=+0.1652, Recent IC=+0.0925, 1st-half IC=+0.1959, 2nd-half IC=+0.1260, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.016, Q3_mid=+0.200, Q4=+0.158, Q5_high_vol=+0.203

**`combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`** (Lock IC=+0.1105, Sharpe=+0.7630)
- Admission: Train IC=+0.3221, Deflated=+0.3241, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.307 | 2016: +0.084 | 2017: +0.193 | 2018: +0.209 | 2019: +0.169 | 2020: +0.123 | 2021: +0.126 | 2022: +0.022 | 2023: +0.085 | 2024: +0.151 | 2025: +0.103 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.313 | 2016: +0.138 | 2017: +0.319 | 2018: +0.436 | 2019: +0.356 | 2020: +0.223 | 2021: +0.079 | 2022: +0.202 | 2023: -0.004 | 2024: +0.262 | 2025: -0.021 | 2026: +0.312
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.38
- Early IC=+0.1953, Recent IC=+0.0738, 1st-half IC=+0.2162, 2nd-half IC=+0.1149, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.004, Q3_mid=+0.186, Q4=+0.208, Q5_high_vol=+0.215

**`combo_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.1025, Sharpe=+0.7249)
- Admission: Train IC=+0.2336, Deflated=+0.2352, IR=0.72, Mono=0.73, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.041 | 2017: +0.225 | 2018: +0.180 | 2019: +0.135 | 2020: +0.168 | 2021: +0.135 | 2022: +0.070 | 2023: +0.088 | 2024: +0.140 | 2025: +0.115 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.373 | 2016: -0.068 | 2017: +0.260 | 2018: +0.212 | 2019: +0.436 | 2020: +0.140 | 2021: +0.337 | 2022: +0.140 | 2023: +0.071 | 2024: +0.322 | 2025: +0.201 | 2026: +0.139
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.62
- Early IC=+0.1645, Recent IC=+0.1023, 1st-half IC=+0.1821, 2nd-half IC=+0.1292, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.031, Q3_mid=+0.198, Q4=+0.146, Q5_high_vol=+0.220

**`combo_tri_median__rbreaker_sell_setup_proximity_early__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0968, Sharpe=+0.6897)
- Admission: Train IC=+0.3092, Deflated=+0.3101, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.134 | 2017: +0.150 | 2018: +0.222 | 2019: +0.128 | 2020: +0.142 | 2021: +0.073 | 2022: +0.112 | 2023: +0.077 | 2024: +0.131 | 2025: +0.134 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.232 | 2016: +0.307 | 2017: +0.231 | 2018: +0.264 | 2019: +0.205 | 2020: +0.308 | 2021: +0.104 | 2022: +0.053 | 2023: +0.092 | 2024: +0.305 | 2025: +0.203 | 2026: -0.131
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.47
- Early IC=+0.1984, Recent IC=+0.0926, 1st-half IC=+0.2077, 2nd-half IC=+0.1209, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.006, Q3_mid=+0.186, Q4=+0.171, Q5_high_vol=+0.216

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.1092, Sharpe=+0.6573)
- Admission: Train IC=+0.3295, Deflated=+0.3319, IR=0.92, Mono=0.81, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.099 | 2017: +0.203 | 2018: +0.227 | 2019: +0.166 | 2020: +0.146 | 2021: +0.129 | 2022: +0.036 | 2023: +0.090 | 2024: +0.136 | 2025: +0.110 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.399 | 2016: +0.165 | 2017: +0.359 | 2018: +0.473 | 2019: +0.342 | 2020: +0.185 | 2021: +0.164 | 2022: +0.184 | 2023: +0.068 | 2024: +0.238 | 2025: +0.070 | 2026: +0.222
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.41
- Early IC=+0.2042, Recent IC=+0.0828, 1st-half IC=+0.2287, 2nd-half IC=+0.1249, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.014, Q3_mid=+0.199, Q4=+0.224, Q5_high_vol=+0.215

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0916, Sharpe=+0.6369)
- Admission: Train IC=+0.2963, Deflated=+0.2976, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.101 | 2017: +0.135 | 2018: +0.280 | 2019: +0.178 | 2020: +0.172 | 2021: +0.170 | 2022: +0.053 | 2023: +0.094 | 2024: +0.154 | 2025: +0.058 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.404 | 2016: +0.129 | 2017: +0.325 | 2018: +0.584 | 2019: +0.275 | 2020: +0.105 | 2021: +0.237 | 2022: +0.147 | 2023: +0.124 | 2024: +0.202 | 2025: +0.186 | 2026: +0.120
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.58
- Early IC=+0.1934, Recent IC=+0.1119, 1st-half IC=+0.2275, 2nd-half IC=+0.1450, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.073, Q3_mid=+0.188, Q4=+0.170, Q5_high_vol=+0.290

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1177, Sharpe=+0.6330)
- Admission: Train IC=+0.3148, Deflated=+0.3165, IR=1.11, Mono=0.84, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.101 | 2017: +0.231 | 2018: +0.185 | 2019: +0.157 | 2020: +0.172 | 2021: +0.142 | 2022: +0.033 | 2023: +0.098 | 2024: +0.145 | 2025: +0.105 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.251 | 2017: +0.357 | 2018: +0.456 | 2019: +0.298 | 2020: +0.315 | 2021: +0.302 | 2022: +0.078 | 2023: -0.003 | 2024: +0.236 | 2025: +0.074 | 2026: +0.233
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.46
- Early IC=+0.1926, Recent IC=+0.0877, 1st-half IC=+0.2183, 2nd-half IC=+0.1340, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.060, Q3_mid=+0.153, Q4=+0.229, Q5_high_vol=+0.208

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0883, Sharpe=+0.6113)
- Admission: Train IC=+0.3158, Deflated=+0.3165, IR=0.99, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.306 | 2016: +0.124 | 2017: +0.192 | 2018: +0.195 | 2019: +0.131 | 2020: +0.173 | 2021: +0.116 | 2022: +0.056 | 2023: +0.072 | 2024: +0.083 | 2025: +0.111 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.325 | 2016: +0.296 | 2017: +0.364 | 2018: +0.469 | 2019: +0.147 | 2020: +0.351 | 2021: +0.083 | 2022: +0.060 | 2023: -0.007 | 2024: +0.191 | 2025: +0.074 | 2026: +0.210
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.40
- Early IC=+0.2149, Recent IC=+0.0858, 1st-half IC=+0.2278, 2nd-half IC=+0.1217, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.004, Q3_mid=+0.172, Q4=+0.251, Q5_high_vol=+0.210

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1300, Sharpe=+0.6068)
- Admission: Train IC=+0.2005, Deflated=+0.2021, IR=0.49, Mono=0.66, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.042 | 2017: +0.207 | 2018: +0.136 | 2019: +0.166 | 2020: +0.117 | 2021: +0.085 | 2022: +0.065 | 2023: +0.102 | 2024: +0.148 | 2025: +0.101 | 2026: +0.175
- Yearly Tail ICs:   2015: +0.011 | 2016: +0.029 | 2017: +0.160 | 2018: +0.211 | 2019: +0.465 | 2020: +0.260 | 2021: +0.230 | 2022: +0.173 | 2023: +0.060 | 2024: +0.225 | 2025: +0.057 | 2026: +0.296
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.67
- Early IC=+0.1113, Recent IC=+0.0749, 1st-half IC=+0.1568, 2nd-half IC=+0.1039, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.061, Q3_mid=+0.128, Q4=+0.115, Q5_high_vol=+0.184

**`combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1000, Sharpe=+0.5841)
- Admission: Train IC=+0.2710, Deflated=+0.2723, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.126 | 2017: +0.216 | 2018: +0.215 | 2019: +0.132 | 2020: +0.169 | 2021: +0.103 | 2022: +0.083 | 2023: +0.071 | 2024: +0.095 | 2025: +0.117 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.145 | 2017: +0.268 | 2018: +0.397 | 2019: +0.271 | 2020: +0.219 | 2021: +0.176 | 2022: +0.180 | 2023: -0.028 | 2024: +0.137 | 2025: +0.127 | 2026: +0.143
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.44
- Early IC=+0.2099, Recent IC=+0.0928, 1st-half IC=+0.2383, 2nd-half IC=+0.1204, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.014, Q3_mid=+0.137, Q4=+0.206, Q5_high_vol=+0.242

**`combo_mean__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0992, Sharpe=+0.5697)
- Admission: Train IC=+0.2705, Deflated=+0.2722, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.093 | 2017: +0.218 | 2018: +0.187 | 2019: +0.127 | 2020: +0.166 | 2021: +0.086 | 2022: +0.064 | 2023: +0.067 | 2024: +0.088 | 2025: +0.130 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.083 | 2017: +0.265 | 2018: +0.371 | 2019: +0.296 | 2020: +0.201 | 2021: +0.175 | 2022: +0.224 | 2023: -0.021 | 2024: +0.177 | 2025: +0.172 | 2026: +0.110
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.39
- Early IC=+0.1914, Recent IC=+0.0747, 1st-half IC=+0.2161, 2nd-half IC=+0.1100, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.010, Q3_mid=+0.128, Q4=+0.186, Q5_high_vol=+0.217

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.1069, Sharpe=+0.5585)
- Admission: Train IC=+0.3110, Deflated=+0.3123, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.309 | 2016: +0.125 | 2017: +0.215 | 2018: +0.232 | 2019: +0.160 | 2020: +0.165 | 2021: +0.130 | 2022: +0.087 | 2023: +0.070 | 2024: +0.154 | 2025: +0.102 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.414 | 2016: +0.222 | 2017: +0.229 | 2018: +0.443 | 2019: +0.273 | 2020: +0.241 | 2021: +0.194 | 2022: +0.210 | 2023: +0.082 | 2024: +0.142 | 2025: +0.034 | 2026: +0.035
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.50
- Early IC=+0.2170, Recent IC=+0.1081, 1st-half IC=+0.2384, 2nd-half IC=+0.1396, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.045, Q3_mid=+0.198, Q4=+0.180, Q5_high_vol=+0.254

**`combo_clamp_diff__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0933, Sharpe=+0.5494)
- Admission: Train IC=+0.2952, Deflated=+0.2964, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.088 | 2017: +0.137 | 2018: +0.251 | 2019: +0.171 | 2020: +0.188 | 2021: +0.165 | 2022: +0.050 | 2023: +0.104 | 2024: +0.154 | 2025: +0.047 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.099 | 2017: +0.382 | 2018: +0.539 | 2019: +0.302 | 2020: -0.018 | 2021: +0.199 | 2022: +0.235 | 2023: +0.080 | 2024: +0.123 | 2025: -0.016 | 2026: -0.012
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.67, Recency ratio=0.58
- Early IC=+0.1858, Recent IC=+0.1076, 1st-half IC=+0.2187, 2nd-half IC=+0.1470, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.080, Q3_mid=+0.187, Q4=+0.163, Q5_high_vol=+0.284

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.1061, Sharpe=+0.5479)
- Admission: Train IC=+0.3062, Deflated=+0.3081, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.058 | 2017: +0.215 | 2018: +0.135 | 2019: +0.094 | 2020: +0.114 | 2021: +0.099 | 2022: +0.022 | 2023: +0.081 | 2024: +0.146 | 2025: +0.104 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.142 | 2017: +0.418 | 2018: +0.376 | 2019: +0.193 | 2020: +0.262 | 2021: +0.150 | 2022: +0.359 | 2023: -0.183 | 2024: +0.302 | 2025: -0.025 | 2026: +0.204
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.50
- Early IC=+0.1221, Recent IC=+0.0606, 1st-half IC=+0.1544, 2nd-half IC=+0.0929, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.024, Q3_mid=+0.123, Q4=+0.162, Q5_high_vol=+0.130

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1175, Sharpe=+0.4851)
- Admission: Train IC=+0.2722, Deflated=+0.2732, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.178 | 2017: +0.079 | 2018: +0.133 | 2019: +0.078 | 2020: +0.127 | 2021: +0.110 | 2022: +0.120 | 2023: +0.156 | 2024: +0.134 | 2025: +0.127 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.234 | 2017: +0.382 | 2018: +0.247 | 2019: +0.181 | 2020: +0.134 | 2021: +0.279 | 2022: +0.141 | 2023: +0.085 | 2024: +0.255 | 2025: -0.001 | 2026: +0.008
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.52
- Early IC=+0.2223, Recent IC=+0.1155, 1st-half IC=+0.1862, 2nd-half IC=+0.1084, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.046, Q3_mid=+0.149, Q4=+0.171, Q5_high_vol=+0.220

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1223, Sharpe=+0.4818)
- Admission: Train IC=+0.2008, Deflated=+0.2010, IR=0.36, Mono=0.66, p=0.0000, MaxCorr=0.64
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.063 | 2017: +0.223 | 2018: +0.101 | 2019: +0.174 | 2020: +0.110 | 2021: +0.090 | 2022: +0.106 | 2023: +0.078 | 2024: +0.144 | 2025: +0.052 | 2026: +0.194
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.071 | 2017: +0.236 | 2018: +0.331 | 2019: +0.253 | 2020: +0.183 | 2021: +0.236 | 2022: +0.212 | 2023: -0.015 | 2024: +0.070 | 2025: -0.138 | 2026: +0.235
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.72, Recency ratio=0.83
- Early IC=+0.1189, Recent IC=+0.0983, 1st-half IC=+0.1602, 2nd-half IC=+0.1161, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.042, Q3_mid=+0.131, Q4=+0.158, Q5_high_vol=+0.167

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1223, Sharpe=+0.4818)
- Admission: Train IC=+0.2006, Deflated=+0.2008, IR=0.37, Mono=0.67, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.063 | 2017: +0.223 | 2018: +0.101 | 2019: +0.173 | 2020: +0.110 | 2021: +0.090 | 2022: +0.107 | 2023: +0.079 | 2024: +0.145 | 2025: +0.051 | 2026: +0.194
- Yearly Tail ICs:   2015: +0.200 | 2016: -0.072 | 2017: +0.236 | 2018: +0.331 | 2019: +0.253 | 2020: +0.180 | 2021: +0.237 | 2022: +0.213 | 2023: -0.015 | 2024: +0.070 | 2025: -0.142 | 2026: +0.233
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.73, Recency ratio=0.83
- Early IC=+0.1188, Recent IC=+0.0983, 1st-half IC=+0.1602, 2nd-half IC=+0.1161, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.043, Q3_mid=+0.131, Q4=+0.158, Q5_high_vol=+0.167

**`combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1064, Sharpe=+0.4742)
- Admission: Train IC=+0.2437, Deflated=+0.2446, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.137 | 2017: +0.227 | 2018: +0.161 | 2019: +0.120 | 2020: +0.188 | 2021: +0.091 | 2022: +0.118 | 2023: +0.075 | 2024: +0.110 | 2025: +0.081 | 2026: +0.138
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.378 | 2017: +0.076 | 2018: +0.136 | 2019: +0.253 | 2020: +0.147 | 2021: +0.156 | 2022: +0.040 | 2023: -0.129 | 2024: +0.106 | 2025: +0.032 | 2026: +0.161
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.49
- Early IC=+0.2154, Recent IC=+0.1047, 1st-half IC=+0.2340, 2nd-half IC=+0.1305, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.038, Q3_mid=+0.193, Q4=+0.148, Q5_high_vol=+0.270

**`combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1125, Sharpe=+0.4636)
- Admission: Train IC=+0.2216, Deflated=+0.2224, IR=0.56, Mono=0.68, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.139 | 2017: +0.236 | 2018: +0.142 | 2019: +0.131 | 2020: +0.152 | 2021: +0.083 | 2022: +0.138 | 2023: +0.085 | 2024: +0.111 | 2025: +0.083 | 2026: +0.160
- Yearly Tail ICs:   2015: +0.206 | 2016: +0.233 | 2017: +0.089 | 2018: +0.095 | 2019: +0.251 | 2020: +0.054 | 2021: +0.128 | 2022: +0.159 | 2023: -0.042 | 2024: +0.142 | 2025: +0.101 | 2026: +0.231
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.53
- Early IC=+0.2113, Recent IC=+0.1115, 1st-half IC=+0.2289, 2nd-half IC=+0.1281, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.043, Q3_mid=+0.193, Q4=+0.152, Q5_high_vol=+0.254

**`combo_sig_product__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.1063, Sharpe=+0.4590)
- Admission: Train IC=+0.2466, Deflated=+0.2470, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.168 | 2017: +0.109 | 2018: +0.152 | 2019: +0.062 | 2020: +0.115 | 2021: +0.075 | 2022: +0.080 | 2023: +0.123 | 2024: +0.131 | 2025: +0.133 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.397 | 2016: +0.262 | 2017: +0.311 | 2018: +0.187 | 2019: +0.033 | 2020: +0.222 | 2021: +0.245 | 2022: +0.130 | 2023: -0.000 | 2024: +0.324 | 2025: +0.087 | 2026: -0.195
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.45, Recency ratio=0.39
- Early IC=+0.2005, Recent IC=+0.0773, 1st-half IC=+0.1943, 2nd-half IC=+0.0879, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.022, Q3_mid=+0.119, Q4=+0.147, Q5_high_vol=+0.208

**`trend_bar_close_consistency`** (Lock IC=+0.0642, Sharpe=+0.4479)
- Admission: Train IC=+0.2230, Deflated=+0.2235, IR=0.44, Mono=0.69, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.084 | 2016: +0.019 | 2017: +0.150 | 2018: +0.091 | 2019: +0.002 | 2020: +0.080 | 2021: +0.031 | 2022: +0.085 | 2023: +0.087 | 2024: +0.091 | 2025: +0.126 | 2026: -0.121
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.110 | 2017: +0.224 | 2018: +0.188 | 2019: -0.016 | 2020: +0.225 | 2021: +0.219 | 2022: +0.194 | 2023: +0.023 | 2024: +0.301 | 2025: +0.095 | 2026: -0.233
- IC CV=0.66, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=1.12
- Early IC=+0.0517, Recent IC=+0.0580, 1st-half IC=+0.0994, 2nd-half IC=+0.0556, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.130, Q2=-0.021, Q3_mid=+0.125, Q4=+0.105, Q5_high_vol=+0.049

**`combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0995, Sharpe=+0.4399)
- Admission: Train IC=+0.2821, Deflated=+0.2838, IR=0.95, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.068 | 2017: +0.231 | 2018: +0.171 | 2019: +0.121 | 2020: +0.150 | 2021: +0.117 | 2022: +0.088 | 2023: +0.100 | 2024: +0.145 | 2025: +0.122 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.508 | 2016: +0.166 | 2017: +0.235 | 2018: +0.255 | 2019: +0.351 | 2020: +0.225 | 2021: +0.273 | 2022: +0.309 | 2023: +0.282 | 2024: +0.244 | 2025: +0.092 | 2026: -0.070
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.68
- Early IC=+0.1497, Recent IC=+0.1021, 1st-half IC=+0.1856, 2nd-half IC=+0.1221, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.028, Q3_mid=+0.181, Q4=+0.151, Q5_high_vol=+0.189

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0792, Sharpe=+0.3953)
- Admission: Train IC=+0.1690, Deflated=+0.1706, IR=0.53, Mono=0.72, p=0.0002, MaxCorr=0.69
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.115 | 2017: +0.109 | 2018: +0.281 | 2019: +0.096 | 2020: +0.130 | 2021: +0.101 | 2022: +0.112 | 2023: +0.050 | 2024: +0.098 | 2025: +0.104 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.105 | 2017: +0.327 | 2018: +0.466 | 2019: +0.109 | 2020: +0.215 | 2021: +0.190 | 2022: +0.000 | 2023: +0.090 | 2024: +0.175 | 2025: +0.153 | 2026: -0.308
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.66
- Early IC=+0.1609, Recent IC=+0.1064, 1st-half IC=+0.2118, 2nd-half IC=+0.1108, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.016, Q3_mid=+0.146, Q4=+0.171, Q5_high_vol=+0.207

**`combo_ratio__bar_ret_0__net_volume_flow`** (Lock IC=+0.0500, Sharpe=+0.3938)
- Admission: Train IC=+0.1425, Deflated=+0.1442, IR=0.33, Mono=0.65, p=0.0062, MaxCorr=0.09
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.055 | 2017: +0.106 | 2018: +0.193 | 2019: +0.120 | 2020: +0.060 | 2021: +0.138 | 2022: +0.020 | 2023: +0.008 | 2024: +0.061 | 2025: +0.089 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.334 | 2016: -0.088 | 2017: +0.096 | 2018: +0.173 | 2019: +0.045 | 2020: +0.132 | 2021: +0.368 | 2022: +0.124 | 2023: -0.017 | 2024: +0.020 | 2025: +0.104 | 2026: +0.197
- IC CV=0.52, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.67
- Early IC=+0.1174, Recent IC=+0.0790, 1st-half IC=+0.1435, 2nd-half IC=+0.0766, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.142, Q2=-0.024, Q3_mid=+0.099, Q4=+0.126, Q5_high_vol=+0.142

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0789, Sharpe=+0.3856)
- Admission: Train IC=+0.2082, Deflated=+0.2102, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.097 | 2017: +0.261 | 2018: +0.230 | 2019: +0.144 | 2020: +0.130 | 2021: +0.079 | 2022: +0.088 | 2023: +0.044 | 2024: +0.128 | 2025: +0.102 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.006 | 2017: +0.195 | 2018: +0.423 | 2019: +0.116 | 2020: +0.219 | 2021: +0.191 | 2022: +0.201 | 2023: +0.203 | 2024: +0.225 | 2025: +0.034 | 2026: -0.223
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.55, Recency ratio=0.52
- Early IC=+0.1615, Recent IC=+0.0833, 1st-half IC=+0.2079, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.006, Q3_mid=+0.153, Q4=+0.157, Q5_high_vol=+0.202

**`combo_sig_product__first_bar_sentiment__trend_bar_close_consistency`** (Lock IC=+0.0631, Sharpe=+0.3781)
- Admission: Train IC=+0.2198, Deflated=+0.2202, IR=0.51, Mono=0.68, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.126 | 2017: +0.087 | 2018: +0.182 | 2019: +0.082 | 2020: +0.117 | 2021: +0.100 | 2022: +0.079 | 2023: +0.058 | 2024: +0.073 | 2025: +0.092 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.064 | 2017: +0.081 | 2018: +0.324 | 2019: +0.206 | 2020: +0.144 | 2021: +0.030 | 2022: +0.247 | 2023: +0.162 | 2024: +0.140 | 2025: +0.144 | 2026: -0.096
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.50
- Early IC=+0.1780, Recent IC=+0.0898, 1st-half IC=+0.1629, 2nd-half IC=+0.0984, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.006, Q3_mid=+0.144, Q4=+0.144, Q5_high_vol=+0.200

**`combo_rank_max__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.0884, Sharpe=+0.3251)
- Admission: Train IC=+0.2029, Deflated=+0.2033, IR=0.46, Mono=0.67, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.070 | 2017: +0.120 | 2018: +0.140 | 2019: +0.089 | 2020: +0.074 | 2021: +0.017 | 2022: +0.139 | 2023: +0.084 | 2024: +0.102 | 2025: +0.091 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.202 | 2017: +0.188 | 2018: +0.083 | 2019: +0.255 | 2020: +0.059 | 2021: +0.107 | 2022: +0.269 | 2023: +0.199 | 2024: +0.182 | 2025: -0.007 | 2026: -0.248
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.48
- Early IC=+0.1624, Recent IC=+0.0774, 1st-half IC=+0.1785, 2nd-half IC=+0.0819, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.013, Q3_mid=+0.169, Q4=+0.102, Q5_high_vol=+0.186

**`combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction`** (Lock IC=+0.0889, Sharpe=+0.2828)
- Admission: Train IC=+0.2347, Deflated=+0.2360, IR=0.61, Mono=0.78, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.070 | 2017: +0.252 | 2018: +0.144 | 2019: +0.124 | 2020: +0.132 | 2021: +0.082 | 2022: +0.094 | 2023: +0.067 | 2024: +0.146 | 2025: +0.099 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.423 | 2016: +0.123 | 2017: +0.218 | 2018: +0.122 | 2019: +0.399 | 2020: +0.110 | 2021: +0.013 | 2022: +0.305 | 2023: +0.179 | 2024: +0.187 | 2025: -0.071 | 2026: +0.081
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.54
- Early IC=+0.1689, Recent IC=+0.0912, 1st-half IC=+0.1952, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.034, Q3_mid=+0.175, Q4=+0.152, Q5_high_vol=+0.204

**`combo_clamp_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0850, Sharpe=+0.2338)
- Admission: Train IC=+0.2612, Deflated=+0.2626, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.110 | 2017: +0.188 | 2018: +0.217 | 2019: +0.121 | 2020: +0.145 | 2021: +0.150 | 2022: +0.057 | 2023: +0.093 | 2024: +0.119 | 2025: +0.010 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.377 | 2016: +0.129 | 2017: +0.405 | 2018: +0.342 | 2019: +0.335 | 2020: +0.177 | 2021: +0.186 | 2022: +0.125 | 2023: +0.129 | 2024: +0.072 | 2025: -0.082 | 2026: +0.163
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.49
- Early IC=+0.2100, Recent IC=+0.1031, 1st-half IC=+0.2244, 2nd-half IC=+0.1206, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.023, Q3_mid=+0.186, Q4=+0.174, Q5_high_vol=+0.275

**`combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0919, Sharpe=+0.1792)
- Admission: Train IC=+0.2461, Deflated=+0.2465, IR=0.63, Mono=0.77, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.110 | 2017: +0.135 | 2018: +0.201 | 2019: +0.098 | 2020: +0.150 | 2021: +0.086 | 2022: +0.104 | 2023: +0.082 | 2024: +0.108 | 2025: +0.136 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.315 | 2016: +0.188 | 2017: +0.159 | 2018: +0.315 | 2019: +0.144 | 2020: +0.173 | 2021: +0.073 | 2022: +0.137 | 2023: +0.012 | 2024: +0.227 | 2025: +0.160 | 2026: -0.028
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.52
- Early IC=+0.1843, Recent IC=+0.0950, 1st-half IC=+0.1954, 2nd-half IC=+0.1156, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.004, Q3_mid=+0.195, Q4=+0.160, Q5_high_vol=+0.182

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0780, Sharpe=+0.1459)
- Admission: Train IC=+0.2551, Deflated=+0.2562, IR=0.93, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.336 | 2016: +0.119 | 2017: +0.177 | 2018: +0.207 | 2019: +0.122 | 2020: +0.136 | 2021: +0.143 | 2022: +0.050 | 2023: +0.082 | 2024: +0.084 | 2025: +0.036 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.287 | 2016: +0.138 | 2017: +0.387 | 2018: +0.363 | 2019: +0.336 | 2020: +0.093 | 2021: +0.204 | 2022: +0.077 | 2023: +0.145 | 2024: -0.047 | 2025: -0.056 | 2026: +0.117
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.50, Recency ratio=0.42
- Early IC=+0.2275, Recent IC=+0.0964, 1st-half IC=+0.2286, 2nd-half IC=+0.1152, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.014, Q3_mid=+0.177, Q4=+0.169, Q5_high_vol=+0.273

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0912, Sharpe=+0.1026)
- Admission: Train IC=+0.3025, Deflated=+0.3043, IR=0.73, Mono=0.78, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.108 | 2017: +0.193 | 2018: +0.220 | 2019: +0.126 | 2020: +0.109 | 2021: +0.167 | 2022: +0.095 | 2023: +0.087 | 2024: +0.134 | 2025: +0.070 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.504 | 2016: +0.114 | 2017: +0.109 | 2018: +0.317 | 2019: +0.321 | 2020: +0.122 | 2021: +0.267 | 2022: +0.324 | 2023: +0.075 | 2024: +0.084 | 2025: +0.119 | 2026: +0.022
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.68
- Early IC=+0.1934, Recent IC=+0.1311, 1st-half IC=+0.2077, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.015, Q3_mid=+0.198, Q4=+0.185, Q5_high_vol=+0.210

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0716, Sharpe=+0.0053)
- Admission: Train IC=+0.1728, Deflated=+0.1759, IR=0.45, Mono=0.65, p=0.0000, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.144 | 2016: -0.044 | 2017: +0.110 | 2018: +0.039 | 2019: +0.111 | 2020: +0.086 | 2021: +0.060 | 2022: +0.027 | 2023: +0.011 | 2024: +0.194 | 2025: +0.038 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.368 | 2016: -0.079 | 2017: +0.119 | 2018: +0.275 | 2019: +0.294 | 2020: +0.024 | 2021: +0.277 | 2022: +0.168 | 2023: +0.002 | 2024: +0.343 | 2025: +0.085 | 2026: -0.155
- IC CV=0.84, Neg years (linear/tail)=1/1 of 8, Half ratio=1.18, Recency ratio=0.87
- Early IC=+0.0499, Recent IC=+0.0436, 1st-half IC=+0.0613, 2nd-half IC=+0.0721, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.022, Q3_mid=+0.102, Q4=+0.058, Q5_high_vol=+0.114

### 159915ETF — `single` True Positives

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1269, Sharpe=+1.6324)
- Admission: Train IC=+0.2946, Deflated=+0.2960, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.128 | 2017: +0.014 | 2018: +0.092 | 2019: +0.242 | 2020: +0.153 | 2021: +0.129 | 2022: +0.102 | 2023: +0.143 | 2024: +0.105 | 2025: +0.185 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.295 | 2016: +0.195 | 2017: +0.094 | 2018: +0.140 | 2019: +0.570 | 2020: +0.368 | 2021: +0.174 | 2022: +0.276 | 2023: +0.354 | 2024: +0.241 | 2025: +0.333 | 2026: +0.255
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.60
- Early IC=+0.1943, Recent IC=+0.1156, 1st-half IC=+0.1597, 2nd-half IC=+0.1587, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.75)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.074, Q3_mid=+0.173, Q4=+0.135, Q5_high_vol=+0.239

**`combo_mean__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1219, Sharpe=+1.3598)
- Admission: Train IC=+0.2431, Deflated=+0.2440, IR=0.58, Mono=0.70, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.090 | 2017: +0.002 | 2018: +0.172 | 2019: +0.207 | 2020: +0.135 | 2021: +0.156 | 2022: +0.118 | 2023: +0.146 | 2024: +0.068 | 2025: +0.156 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.067 | 2017: +0.152 | 2018: +0.389 | 2019: +0.401 | 2020: +0.186 | 2021: +0.387 | 2022: +0.119 | 2023: +0.111 | 2024: +0.399 | 2025: +0.193 | 2026: +0.217
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.87
- Early IC=+0.1583, Recent IC=+0.1370, 1st-half IC=+0.1627, 2nd-half IC=+0.1542, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.063, Q3_mid=+0.128, Q4=+0.203, Q5_high_vol=+0.185

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1458, Sharpe=+1.3138)
- Admission: Train IC=+0.3068, Deflated=+0.3083, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.046 | 2017: +0.008 | 2018: +0.125 | 2019: +0.235 | 2020: +0.126 | 2021: +0.142 | 2022: +0.096 | 2023: +0.183 | 2024: +0.125 | 2025: +0.180 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.080 | 2017: +0.102 | 2018: +0.356 | 2019: +0.519 | 2020: +0.307 | 2021: +0.332 | 2022: +0.401 | 2023: +0.342 | 2024: +0.335 | 2025: +0.159 | 2026: +0.364
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.00
- Early IC=+0.1186, Recent IC=+0.1187, 1st-half IC=+0.1228, 2nd-half IC=+0.1548, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.105, Q3_mid=+0.162, Q4=+0.149, Q5_high_vol=+0.148

**`combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1385, Sharpe=+1.2999)
- Admission: Train IC=+0.2361, Deflated=+0.2375, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.041 | 2017: -0.003 | 2018: +0.045 | 2019: +0.156 | 2020: +0.089 | 2021: +0.150 | 2022: +0.115 | 2023: +0.164 | 2024: +0.081 | 2025: +0.195 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.058 | 2016: +0.210 | 2017: +0.146 | 2018: +0.212 | 2019: +0.261 | 2020: +0.209 | 2021: +0.246 | 2022: +0.275 | 2023: +0.359 | 2024: +0.326 | 2025: +0.192 | 2026: +0.109
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=1.37, Recency ratio=1.20
- Early IC=+0.1127, Recent IC=+0.1351, 1st-half IC=+0.0986, 2nd-half IC=+0.1355, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.041, Q3_mid=+0.132, Q4=+0.171, Q5_high_vol=+0.113

**`combo_rank_min__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1246, Sharpe=+1.2377)
- Admission: Train IC=+0.2397, Deflated=+0.2407, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.045 | 2017: -0.028 | 2018: +0.081 | 2019: +0.253 | 2020: +0.109 | 2021: +0.096 | 2022: +0.059 | 2023: +0.125 | 2024: +0.080 | 2025: +0.157 | 2026: +0.118
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.026 | 2017: +0.003 | 2018: +0.262 | 2019: +0.516 | 2020: +0.083 | 2021: +0.342 | 2022: +0.226 | 2023: +0.143 | 2024: +0.445 | 2025: +0.077 | 2026: +0.245
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.14, Recency ratio=0.55
- Early IC=+0.1372, Recent IC=+0.0750, 1st-half IC=+0.1113, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.046, Q3_mid=+0.102, Q4=+0.104, Q5_high_vol=+0.165

**`combo_min__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1216, Sharpe=+1.1418)
- Admission: Train IC=+0.2454, Deflated=+0.2463, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.068 | 2017: -0.024 | 2018: +0.085 | 2019: +0.246 | 2020: +0.125 | 2021: +0.101 | 2022: +0.053 | 2023: +0.125 | 2024: +0.087 | 2025: +0.147 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.256 | 2016: +0.015 | 2017: +0.040 | 2018: +0.238 | 2019: +0.522 | 2020: +0.092 | 2021: +0.329 | 2022: +0.244 | 2023: +0.160 | 2024: +0.444 | 2025: +0.053 | 2026: +0.220
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=0.52
- Early IC=+0.1484, Recent IC=+0.0772, 1st-half IC=+0.1191, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.049, Q3_mid=+0.106, Q4=+0.108, Q5_high_vol=+0.169

**`combo_min__first_bar_return__limit_down_proximity_early`** (Lock IC=+0.1216, Sharpe=+1.1418)
- Admission: Train IC=+0.2454, Deflated=+0.2463, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.068 | 2017: -0.024 | 2018: +0.085 | 2019: +0.246 | 2020: +0.125 | 2021: +0.101 | 2022: +0.053 | 2023: +0.125 | 2024: +0.087 | 2025: +0.147 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.256 | 2016: +0.015 | 2017: +0.040 | 2018: +0.238 | 2019: +0.522 | 2020: +0.092 | 2021: +0.329 | 2022: +0.244 | 2023: +0.160 | 2024: +0.444 | 2025: +0.053 | 2026: +0.220
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=0.52
- Early IC=+0.1483, Recent IC=+0.0772, 1st-half IC=+0.1191, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.049, Q3_mid=+0.106, Q4=+0.108, Q5_high_vol=+0.169

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0986, Sharpe=+1.1068)
- Admission: Train IC=+0.2446, Deflated=+0.2460, IR=0.49, Mono=0.68, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.093 | 2017: +0.003 | 2018: +0.085 | 2019: +0.225 | 2020: +0.133 | 2021: +0.109 | 2022: +0.070 | 2023: +0.147 | 2024: +0.088 | 2025: +0.119 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.452 | 2016: +0.156 | 2017: -0.031 | 2018: +0.061 | 2019: +0.384 | 2020: +0.267 | 2021: +0.122 | 2022: +0.189 | 2023: +0.391 | 2024: +0.215 | 2025: +0.315 | 2026: -0.204
- IC CV=0.60, Neg years (linear/tail)=0/1 of 8, Half ratio=1.09, Recency ratio=0.56
- Early IC=+0.1585, Recent IC=+0.0895, 1st-half IC=+0.1272, 2nd-half IC=+0.1382, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.75)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.067, Q3_mid=+0.144, Q4=+0.052, Q5_high_vol=+0.264

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1008, Sharpe=+1.0903)
- Admission: Train IC=+0.2842, Deflated=+0.2846, IR=0.71, Mono=0.74, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.168 | 2017: -0.008 | 2018: +0.180 | 2019: +0.206 | 2020: +0.190 | 2021: +0.111 | 2022: +0.070 | 2023: +0.107 | 2024: +0.074 | 2025: +0.119 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.188 | 2016: +0.250 | 2017: +0.079 | 2018: +0.364 | 2019: +0.399 | 2020: +0.256 | 2021: +0.207 | 2022: +0.272 | 2023: +0.177 | 2024: +0.279 | 2025: +0.287 | 2026: +0.135
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.80, Recency ratio=0.42
- Early IC=+0.2144, Recent IC=+0.0904, 1st-half IC=+0.1848, 2nd-half IC=+0.1472, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.75)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.056, Q3_mid=+0.120, Q4=+0.208, Q5_high_vol=+0.238

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1260, Sharpe=+1.0555)
- Admission: Train IC=+0.2510, Deflated=+0.2517, IR=0.53, Mono=0.72, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.103 | 2017: +0.023 | 2018: +0.127 | 2019: +0.160 | 2020: +0.154 | 2021: +0.167 | 2022: +0.157 | 2023: +0.140 | 2024: +0.089 | 2025: +0.179 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.005 | 2016: +0.249 | 2017: +0.070 | 2018: +0.325 | 2019: +0.351 | 2020: +0.181 | 2021: +0.386 | 2022: +0.252 | 2023: +0.141 | 2024: +0.292 | 2025: +0.142 | 2026: +0.114
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.19, Recency ratio=1.11
- Early IC=+0.1465, Recent IC=+0.1621, 1st-half IC=+0.1392, 2nd-half IC=+0.1659, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.078, Q3_mid=+0.155, Q4=+0.251, Q5_high_vol=+0.163

**`combo_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1097, Sharpe=+1.0080)
- Admission: Train IC=+0.2283, Deflated=+0.2300, IR=0.51, Mono=0.69, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.057 | 2017: +0.039 | 2018: +0.071 | 2019: +0.171 | 2020: +0.107 | 2021: +0.185 | 2022: +0.107 | 2023: +0.191 | 2024: +0.085 | 2025: +0.168 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.043 | 2016: +0.137 | 2017: +0.076 | 2018: +0.211 | 2019: +0.337 | 2020: +0.174 | 2021: +0.328 | 2022: +0.226 | 2023: +0.423 | 2024: +0.235 | 2025: +0.165 | 2026: -0.257
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.20, Recency ratio=1.18
- Early IC=+0.1231, Recent IC=+0.1456, 1st-half IC=+0.1215, 2nd-half IC=+0.1460, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.087, Q3_mid=+0.160, Q4=+0.116, Q5_high_vol=+0.195

**`combo_tri_median__max_up_ret__first_bar_sentiment__star50_limit_proximity_early`** (Lock IC=+0.1236, Sharpe=+0.8616)
- Admission: Train IC=+0.2629, Deflated=+0.2644, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.112 | 2017: +0.005 | 2018: +0.076 | 2019: +0.216 | 2020: +0.144 | 2021: +0.151 | 2022: +0.127 | 2023: +0.145 | 2024: +0.079 | 2025: +0.175 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.154 | 2016: +0.205 | 2017: +0.102 | 2018: +0.316 | 2019: +0.383 | 2020: +0.177 | 2021: +0.274 | 2022: +0.389 | 2023: +0.229 | 2024: +0.255 | 2025: +0.113 | 2026: +0.156
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=0.76
- Early IC=+0.1821, Recent IC=+0.1389, 1st-half IC=+0.1497, 2nd-half IC=+0.1611, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.75)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.085, Q3_mid=+0.161, Q4=+0.134, Q5_high_vol=+0.193

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1311, Sharpe=+0.8565)
- Admission: Train IC=+0.2494, Deflated=+0.2513, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.034 | 2017: +0.029 | 2018: +0.071 | 2019: +0.170 | 2020: +0.110 | 2021: +0.138 | 2022: +0.142 | 2023: +0.178 | 2024: +0.113 | 2025: +0.181 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.271 | 2016: +0.130 | 2017: +0.141 | 2018: +0.137 | 2019: +0.486 | 2020: +0.360 | 2021: +0.223 | 2022: +0.218 | 2023: +0.427 | 2024: +0.219 | 2025: +0.349 | 2026: +0.172
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=1.12
- Early IC=+0.1255, Recent IC=+0.1404, 1st-half IC=+0.1203, 2nd-half IC=+0.1450, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=1.03)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.068, Q3_mid=+0.151, Q4=+0.157, Q5_high_vol=+0.158

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1302, Sharpe=+0.6763)
- Admission: Train IC=+0.2140, Deflated=+0.2149, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.56
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.100 | 2017: -0.031 | 2018: +0.096 | 2019: +0.091 | 2020: +0.077 | 2021: +0.066 | 2022: +0.131 | 2023: +0.154 | 2024: +0.122 | 2025: +0.085 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.264 | 2017: +0.061 | 2018: +0.442 | 2019: +0.295 | 2020: +0.014 | 2021: +0.130 | 2022: +0.254 | 2023: +0.202 | 2024: +0.169 | 2025: -0.014 | 2026: +0.123
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=0.77, Recency ratio=0.68
- Early IC=+0.1432, Recent IC=+0.0978, 1st-half IC=+0.1258, 2nd-half IC=+0.0965, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.095, Q3_mid=+0.138, Q4=+0.171, Q5_high_vol=+0.060

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.0937, Sharpe=+0.6050)
- Admission: Train IC=+0.2655, Deflated=+0.2665, IR=0.78, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.161 | 2016: +0.107 | 2017: -0.041 | 2018: +0.149 | 2019: +0.127 | 2020: +0.143 | 2021: +0.060 | 2022: +0.185 | 2023: +0.105 | 2024: +0.058 | 2025: +0.087 | 2026: +0.145
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.359 | 2017: +0.140 | 2018: +0.406 | 2019: +0.343 | 2020: +0.324 | 2021: +0.172 | 2022: +0.426 | 2023: +0.103 | 2024: +0.010 | 2025: +0.063 | 2026: +0.074
- IC CV=0.61, Neg years (linear/tail)=1/0 of 8, Half ratio=1.14, Recency ratio=0.91
- Early IC=+0.1339, Recent IC=+0.1225, 1st-half IC=+0.1201, 2nd-half IC=+0.1366, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.103, Q3_mid=+0.171, Q4=+0.163, Q5_high_vol=+0.153

**`combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1226, Sharpe=+0.5885)
- Admission: Train IC=+0.2142, Deflated=+0.2150, IR=0.51, Mono=0.69, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.036 | 2017: -0.022 | 2018: +0.093 | 2019: +0.183 | 2020: +0.116 | 2021: +0.128 | 2022: +0.160 | 2023: +0.096 | 2024: +0.104 | 2025: +0.111 | 2026: +0.171
- Yearly Tail ICs:   2015: -0.025 | 2016: +0.242 | 2017: +0.015 | 2018: +0.241 | 2019: +0.267 | 2020: +0.183 | 2021: +0.298 | 2022: +0.157 | 2023: +0.010 | 2024: +0.196 | 2025: -0.030 | 2026: +0.283
- IC CV=0.61, Neg years (linear/tail)=1/1 of 8, Half ratio=1.32, Recency ratio=1.38
- Early IC=+0.1039, Recent IC=+0.1436, 1st-half IC=+0.1154, 2nd-half IC=+0.1529, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.052, Q3_mid=+0.121, Q4=+0.221, Q5_high_vol=+0.125

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1090, Sharpe=+0.3724)
- Admission: Train IC=+0.1551, Deflated=+0.1554, IR=0.48, Mono=0.70, p=0.0018, MaxCorr=0.13
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087 | 2022: +0.139 | 2023: +0.083 | 2024: +0.083 | 2025: +0.120 | 2026: +0.148
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.017 | 2017: +0.138 | 2018: +0.257 | 2019: +0.117 | 2020: +0.189 | 2021: +0.114 | 2022: +0.057 | 2023: -0.092 | 2024: +0.146 | 2025: +0.162 | 2026: +0.240
- IC CV=0.66, Neg years (linear/tail)=0/1 of 8, Half ratio=1.03, Recency ratio=1.15
- Early IC=+0.0981, Recent IC=+0.1130, 1st-half IC=+0.1055, 2nd-half IC=+0.1088, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.038, Q3_mid=+0.091, Q4=+0.189, Q5_high_vol=+0.098

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1075, Sharpe=+0.3554)
- Admission: Train IC=+0.2737, Deflated=+0.2745, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.58
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.080 | 2019: +0.132 | 2020: +0.100 | 2021: +0.035 | 2022: +0.178 | 2023: +0.116 | 2024: +0.078 | 2025: +0.129 | 2026: +0.128
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.187 | 2017: +0.027 | 2018: +0.357 | 2019: +0.278 | 2020: +0.402 | 2021: +0.168 | 2022: +0.464 | 2023: +0.089 | 2024: +0.032 | 2025: +0.062 | 2026: +0.267
- IC CV=0.82, Neg years (linear/tail)=1/0 of 8, Half ratio=1.22, Recency ratio=0.96
- Early IC=+0.1110, Recent IC=+0.1065, 1st-half IC=+0.0978, 2nd-half IC=+0.1188, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.92)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.076, Q3_mid=+0.124, Q4=+0.143, Q5_high_vol=+0.137

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.0961, Sharpe=+0.2321)
- Admission: Train IC=+0.2273, Deflated=+0.2288, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.140 | 2017: +0.038 | 2018: +0.101 | 2019: +0.184 | 2020: +0.120 | 2021: +0.173 | 2022: +0.110 | 2023: +0.161 | 2024: +0.073 | 2025: +0.172 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.133 | 2017: +0.189 | 2018: +0.214 | 2019: +0.214 | 2020: +0.089 | 2021: +0.368 | 2022: +0.294 | 2023: +0.334 | 2024: +0.111 | 2025: +0.230 | 2026: -0.359
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=0.89
- Early IC=+0.1592, Recent IC=+0.1414, 1st-half IC=+0.1408, 2nd-half IC=+0.1467, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.076, Q3_mid=+0.154, Q4=+0.108, Q5_high_vol=+0.202

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0960, Sharpe=+0.2321)
- Admission: Train IC=+0.2273, Deflated=+0.2288, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.141 | 2017: +0.038 | 2018: +0.101 | 2019: +0.184 | 2020: +0.121 | 2021: +0.173 | 2022: +0.109 | 2023: +0.161 | 2024: +0.073 | 2025: +0.171 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.133 | 2017: +0.189 | 2018: +0.216 | 2019: +0.214 | 2020: +0.092 | 2021: +0.366 | 2022: +0.294 | 2023: +0.335 | 2024: +0.099 | 2025: +0.231 | 2026: -0.354
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=0.89
- Early IC=+0.1594, Recent IC=+0.1411, 1st-half IC=+0.1409, 2nd-half IC=+0.1468, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.076, Q3_mid=+0.154, Q4=+0.108, Q5_high_vol=+0.202

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_mean__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.1914 | +0.0249 | -0.1806 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1763 | +0.0543 | -0.0356 | 1y |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | TP | gradual | +0.1763 | +0.0147 | -0.1012 | 1y |
| `combo_tri_min__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0` | TP | fast | +0.1734 | -0.0108 | -0.0853 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1716 | +0.0478 | +0.0010 | 1y |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | TP | gradual | +0.1608 | +0.1147 | -0.0782 | 2y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | gradual | +0.1508 | +0.0609 | -0.0216 | 1y |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | TP | gradual | +0.1462 | +0.0672 | -0.0704 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.1394 | +0.0494 | -0.0180 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.1355 | +0.0552 | -0.0352 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction` | TP | gradual | +0.1336 | +0.0064 | -0.0535 | 1y |
| `combo_ratio__bar_ret_0__volume_surge_direction` | TP | gradual | +0.1143 | +0.0230 | -0.0934 | 1y |
| `combo_ratio__first_bar_return__volume_surge_direction` | TP | gradual | +0.1143 | +0.0230 | -0.0939 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | gradual | +0.1082 | +0.0091 | -0.0307 | 1y |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | FP | fast | +0.0649 | -0.0256 | -0.1745 | 1y |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Median | fast | +0.0578 | -0.0512 | -0.0352 | 1y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | TP | fast | +0.0550 | -0.0050 | +0.1389 | 1y |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | Median | fast | +0.0317 | -0.0394 | +0.2032 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.0279 | +0.0061 | +0.1692 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0279 | +0.0061 | +0.1692 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=5, gradual=12, persistent=3

**FP decay trajectories:**

- `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`: Y1:+0.065 → Y2:-0.026 → Y3:+0.040 → Y4:-0.175

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1561 | +0.1336 | +0.0302 | 3y |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.1231 | +0.1313 | +0.0074 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | gradual | +0.1146 | +0.1576 | -0.0087 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1059 | +0.1666 | +0.0842 | ∞ |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Median | persistent | +0.1054 | +0.0958 | +0.0535 | ∞ |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | TP | persistent | +0.1044 | +0.1539 | +0.0150 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.1021 | +0.1470 | +0.0963 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1020 | +0.1482 | +0.1749 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0998 | +0.1518 | +0.0735 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0997 | +0.1450 | -0.0350 | 3y |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0972 | +0.1786 | +0.1005 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0938 | +0.1539 | +0.0091 | 3y |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.0926 | +0.1187 | +0.0957 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_sentiment` | TP | persistent | +0.0899 | +0.1364 | +0.0784 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0877 | +0.1398 | +0.0379 | 3y |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | TP | persistent | +0.0866 | +0.1342 | +0.0214 | 3y |
| `trend_bar_close_consistency` | TP | gradual | +0.0865 | +0.0906 | -0.1208 | 3y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.0855 | +0.1101 | +0.1526 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early` | TP | persistent | +0.0851 | +0.1506 | +0.0915 | ∞ |
| `combo_min__net_volume_flow__max_down_ret` | TP | persistent | +0.0847 | +0.1158 | +0.0291 | 3y |
| `combo_sig_product__first_bar_sentiment__close_vs_open_range` | Median | gradual | +0.0835 | +0.0671 | -0.0089 | 3y |
| `combo_rank_max__star50_limit_proximity_early__early_body_momentum` | TP | persistent | +0.0832 | +0.1026 | +0.0587 | ∞ |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.0821 | +0.0840 | +0.1024 | 2y |
| `combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__trend_bar_close_consistency` | TP | gradual | +0.0818 | +0.1084 | -0.0073 | 3y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.0813 | +0.1459 | +0.0623 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0786 | +0.1448 | +0.1939 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0781 | +0.1444 | +0.1943 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__net_volume_flow__first_bar_sentiment` | TP | gradual | +0.0767 | +0.1306 | -0.0087 | 3y |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.0748 | +0.1103 | +0.1383 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0724 | +0.0832 | +0.0874 | ∞ |
| `combo_min__max_up_ret__first_bar_sentiment` | Median | gradual | +0.0724 | +0.0838 | -0.0110 | 3y |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0711 | +0.0950 | +0.1054 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_sentiment` | TP | persistent | +0.0702 | +0.1536 | +0.0461 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | TP | gradual | +0.0696 | +0.1432 | -0.0156 | 3y |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0674 | +0.0878 | +0.1036 | ∞ |
| `combo_sig_product__first_bar_sentiment__trend_bar_close_consistency` | TP | gradual | +0.0581 | +0.0727 | -0.0199 | 3y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0514 | +0.1238 | +0.0782 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | TP | persistent | +0.0501 | +0.0982 | +0.0041 | 3y |
| `combo_max__bar_ret_0__max_down_ret` | TP | gradual | +0.0438 | +0.1284 | -0.0001 | 3y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volume_weighted_momentum_acceleration` | Median | fast | +0.0408 | -0.0133 | +0.0727 | 1y |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | FP | gradual | +0.0157 | +0.0088 | -0.0217 | 2y |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | TP | gradual | +0.0107 | +0.1940 | -0.0295 | 3y |
| `combo_ratio__bar_ret_0__net_volume_flow` | TP | gradual | +0.0078 | +0.0609 | -0.0032 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=1, gradual=13, persistent=29

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__close_vs_open_range`: Y1:+0.016 → Y2:+0.009 → Y3:-0.094 → Y4:-0.022

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1911 | +0.0846 | -0.0676 | 1y |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1829 | +0.1255 | +0.0725 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1778 | +0.1133 | +0.0201 | 3y |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1640 | +0.0818 | +0.0840 | 1y |
| `combo_max__max_up_ret__first_bar_return` | TP | gradual | +0.1606 | +0.0733 | -0.0756 | 1y |
| `combo_max__max_up_ret__bar_ret_0` | TP | gradual | +0.1606 | +0.0733 | -0.0756 | 1y |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1537 | +0.1217 | +0.1543 | ∞ |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | TP | gradual | +0.1465 | +0.0876 | -0.0016 | 3y |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1456 | +0.0685 | +0.1121 | 1y |
| `combo_tri_median__max_up_ret__first_bar_sentiment__star50_limit_proximity_early` | TP | persistent | +0.1447 | +0.0786 | +0.0745 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.1432 | +0.1047 | +0.0473 | 3y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1397 | +0.0889 | +0.0767 | ∞ |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1249 | +0.0872 | +0.1193 | ∞ |
| `combo_min__first_bar_return__limit_down_proximity_early` | TP | persistent | +0.1249 | +0.0872 | +0.1193 | ∞ |
| `combo_rank_min__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1242 | +0.0819 | +0.1179 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1157 | +0.0779 | +0.1278 | ∞ |
| `combo_rank_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.1077 | +0.0732 | +0.1164 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1072 | +0.0738 | +0.0948 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.1051 | +0.0583 | +0.1446 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0965 | +0.1043 | +0.1710 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0826 | +0.0831 | +0.1479 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | fast | +0.0544 | -0.0517 | -0.0008 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=1, gradual=4, persistent=17

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:+0.054 → Y2:-0.052 → Y3:-0.026 → Y4:-0.001

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 13/20 top rejects are profitable (65%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_diff__bar_ret_0__demark_setup_reversal_early`: Train IC=+0.2145, Lock IC=+0.0671, Sharpe=+0.4632
- `combo_z_diff__bar_ret_0__demark_setup_reversal_early`: Train IC=+0.2145, Lock IC=+0.0671, Sharpe=+0.4632
- `combo_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2142, Lock IC=+0.0670, Sharpe=+0.4632

**Temporal Validation Gate**: 9/20 top rejects are profitable (45%)

- `combo_max__volume_weighted_momentum_acceleration__demark_setup_reversal_early`: Train IC=+0.2099, Lock IC=+0.0829, Sharpe=+0.4258
- `combo_clamp_diff__volume_weighted_momentum_acceleration__max_up_ret`: Train IC=+0.1901, Lock IC=+0.0622, Sharpe=+0.3586
- `combo_diff__smooth_momentum_structure__max_up_ret`: Train IC=+0.1987, Lock IC=+0.0635, Sharpe=+0.2865

**B3 Composite Floor**: 18/20 top rejects are profitable (90%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2104, Lock IC=+0.0769, Sharpe=+0.8833
- `combo_tri_min__first_bar_return__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1633, Lock IC=+0.0550, Sharpe=+0.6654
- `combo_tri_min__bar_ret_0__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1629, Lock IC=+0.0550, Sharpe=+0.6654

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Sharpe=+0.5292
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Sharpe=+0.5292
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2346, Lock IC=+0.0716, Sharpe=+0.5292

**Adaptive Correlation Gate**: 6/14 top rejects are profitable (43%)

- `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.1955, Lock IC=+0.0678, Sharpe=+0.6776
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1824, Lock IC=+0.0655, Sharpe=+0.4621
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1780, Lock IC=+0.0525, Sharpe=+0.4588

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.2819, Lock IC=+0.1134, Sharpe=+0.8586

**B2 Rolling Guard**: 14/20 top rejects are profitable (70%)

- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Sharpe=+0.5808
- `combo_tri_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1951, Lock IC=+0.0826, Sharpe=+0.4663
- `combo_tri_median__max_up_ret__first_bar_sentiment__body_size_progression`: Train IC=+0.1934, Lock IC=+0.0755, Sharpe=+0.4069

**Temporal Validation Gate**: 19/20 top rejects are profitable (95%)

- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824

**B6 Yearly IC CV Gate**: 7/7 top rejects are profitable (100%)

- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2190, Lock IC=+0.0434, Sharpe=+0.9681

**B6 Temporal Stability Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2881, Lock IC=+0.1110, Sharpe=+1.1024
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_tri_min__net_volume_flow__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2971, Lock IC=+0.1120, Sharpe=+1.1041
- `combo_tri_min__opening_auction_imbalance__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2971, Lock IC=+0.1120, Sharpe=+1.1041

**Adaptive Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2620, Lock IC=+0.0944, Sharpe=+0.8030
- `combo_rank_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.2082, Lock IC=+0.1196, Sharpe=+0.7000

### 159915ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2597, Lock IC=+0.0980, Sharpe=+1.7078
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Sharpe=+1.3789
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Sharpe=+1.3789

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Sharpe=+1.3582
- `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2326, Lock IC=+0.0999, Sharpe=+1.0768
- `combo_tri_median__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2348, Lock IC=+0.1189, Sharpe=+1.0159

**Temporal Validation Gate**: 18/20 top rejects are profitable (90%)

- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.2333, Lock IC=+0.1049, Sharpe=+1.0469

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2828, Lock IC=+0.1401, Sharpe=+1.7039
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3073, Lock IC=+0.1158, Sharpe=+1.5577
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Sharpe=+1.4133

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Sharpe=+1.6742
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2904, Lock IC=+0.1209, Sharpe=+1.5937

**Adaptive Correlation Gate**: 13/13 top rejects are profitable (100%)

- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2320, Lock IC=+0.1354, Sharpe=+1.4221
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2355, Lock IC=+0.1397, Sharpe=+1.2824
- `combo_max__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.2304, Lock IC=+0.1104, Sharpe=+1.1839

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1205 | 78 | 21 | 35 | 22 | 27% | 28% |
| B2 Rolling Guard | 204 | 78 | 20 | 14 | 44 | 26% | 56% |
| Temporal Validation Gate | 74 | 74 | 2 | 32 | 40 | 3% | 54% |
| BH-FDR Gate | 5 | 5 | 0 | 5 | 0 | 0% | 0% |
| B3 Composite Floor | 35 | 35 | 1 | 7 | 27 | 3% | 77% |
| B6 Yearly IC CV Gate | 1 | 1 | 0 | 1 | 0 | 0% | 0% |
| B4 Correlation Gate | 196 | 78 | 0 | 15 | 63 | 0% | 81% |
| Adaptive Correlation Gate | 14 | 14 | 0 | 8 | 6 | 0% | 43% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Sharpe=+0.5289

**B2 Rolling Guard** — top TP casualties:
- `combo_clamp_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1349, Lock IC=+0.0570, Sharpe=+1.0307
- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Sharpe=+0.7446
- `combo_tri_min__bar_ret_0__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.1360, Lock IC=+0.0557, Sharpe=+0.6991

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_z_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1469, Lock IC=+0.0614, Sharpe=+0.8233

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2104, Lock IC=+0.0769, Sharpe=+0.8833
- `combo_tri_min__first_bar_return__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1633, Lock IC=+0.0550, Sharpe=+0.6654
- `combo_tri_min__bar_ret_0__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1629, Lock IC=+0.0550, Sharpe=+0.6654

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2265, Lock IC=+0.0937, Sharpe=+1.0629
- `combo_tri_min__bar_ret_0__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.1950, Lock IC=+0.0678, Sharpe=+0.6776
- `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1864, Lock IC=+0.0676, Sharpe=+0.6205

**Adaptive Correlation Gate** — top TP casualties:
- `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.1955, Lock IC=+0.0678, Sharpe=+0.6776
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1824, Lock IC=+0.0655, Sharpe=+0.4621
- `combo_rank_max__max_up_ret__volume_surge_direction`: Train IC=+0.1780, Lock IC=+0.0525, Sharpe=+0.4588

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1823 | 78 | 25 | 23 | 30 | 32% | 38% |
| B2 Rolling Guard | 221 | 78 | 18 | 26 | 34 | 23% | 44% |
| Temporal Validation Gate | 131 | 78 | 16 | 9 | 53 | 21% | 68% |
| BH-FDR Gate | 7 | 7 | 1 | 6 | 0 | 14% | 0% |
| B3 Composite Floor | 150 | 78 | 1 | 2 | 75 | 1% | 96% |
| B6 Yearly IC CV Gate | 7 | 7 | 0 | 0 | 7 | 0% | 100% |
| B6 Temporal Stability Gate | 158 | 78 | 0 | 16 | 62 | 0% | 79% |
| B4 Correlation Gate | 660 | 78 | 0 | 10 | 68 | 0% | 87% |
| Adaptive Correlation Gate | 29 | 29 | 0 | 3 | 26 | 0% | 90% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2312, Lock IC=+0.1016, Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0355, Lock IC=+0.0707, Sharpe=+0.8914
- `combo_rel_diff__body_size_progression__first_bar_return`: Train IC=+0.1888, Lock IC=+0.0693, Sharpe=+0.5882
- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Sharpe=+0.5808

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2104, Lock IC=+0.0406, Sharpe=+1.1125
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2104, Lock IC=+0.0406, Sharpe=+1.1125
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression`: Train IC=+0.1094, Lock IC=+0.0362, Sharpe=+1.0604

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2135, Lock IC=+0.0334, Sharpe=+0.9808
- `combo_tri_min__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2190, Lock IC=+0.0434, Sharpe=+0.9681

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2881, Lock IC=+0.1110, Sharpe=+1.1024
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3026, Lock IC=+0.1078, Sharpe=+0.9888

**B4 Correlation Gate** — top TP casualties:
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_tri_min__net_volume_flow__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2971, Lock IC=+0.1120, Sharpe=+1.1041
- `combo_tri_min__opening_auction_imbalance__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2971, Lock IC=+0.1120, Sharpe=+1.1041

**Adaptive Correlation Gate** — top TP casualties:
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2620, Lock IC=+0.0944, Sharpe=+0.8030
- `combo_rank_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.2082, Lock IC=+0.1196, Sharpe=+0.7000

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1044 | 78 | 20 | 10 | 48 | 26% | 62% |
| B2 Rolling Guard | 258 | 78 | 21 | 6 | 51 | 27% | 65% |
| Temporal Validation Gate | 24 | 24 | 5 | 0 | 19 | 21% | 79% |
| BH-FDR Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 161 | 78 | 0 | 0 | 78 | 0% | 100% |
| B4 Correlation Gate | 179 | 78 | 0 | 0 | 78 | 0% | 100% |
| Adaptive Correlation Gate | 13 | 13 | 0 | 0 | 13 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2597, Lock IC=+0.0980, Sharpe=+1.7078
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Sharpe=+1.3789
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Sharpe=+1.3789

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Sharpe=+1.3582
- `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2326, Lock IC=+0.0999, Sharpe=+1.0768
- `combo_tri_median__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2348, Lock IC=+0.1189, Sharpe=+1.0159

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179
- `combo_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.2333, Lock IC=+0.1049, Sharpe=+1.0469

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__impulse_bar_dominance`: Train IC=+0.2036, Lock IC=+0.1274, Sharpe=+1.7158
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__impulse_bar_dominance`: Train IC=+0.2036, Lock IC=+0.1274, Sharpe=+1.7158
- `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2828, Lock IC=+0.1401, Sharpe=+1.7039

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Sharpe=+1.6742
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2334, Lock IC=+0.1300, Sharpe=+1.6301

**Adaptive Correlation Gate** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2320, Lock IC=+0.1354, Sharpe=+1.4221
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2355, Lock IC=+0.1397, Sharpe=+1.2824
- `combo_max__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.2304, Lock IC=+0.1104, Sharpe=+1.1839

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (74 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 74 | 50 | 2 | 32 | 16 | 4% | 64% |

### 500ETF — `single` (131 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 128 | 50 | 0 | 45 | 5 | 0% | 90% |
| recency_ratio >= 2.5 (late-concentrated) | 3 | 3 | 0 | 2 | 1 | 0% | 67% |

**Top TP killed by recency_ratio cap:**
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Train IC=+0.1291, Lock IC=+0.0798, Sharpe=+0.4226
- `combo_sig_product__trend_day_regime_conviction__max_down_ret`: Train IC=+0.1323, Lock IC=+0.0715, Sharpe=+0.1181

### 159915ETF — `single` (24 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 24 | 24 | 5 | 19 | 0 | 21% | 79% |

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `double_bottom_bull_flag_early` | 1 | 1 | 2 | 50% |  |
| `close_vs_open_range` | 1 | 1 | 2 | 50% |  |
| `volume_weighted_price_position` | 1 | 3 | 4 | 25% |  |
| `volatility_expansion_trend_vector` | 1 | 4 | 5 | 20% |  |
| `max_up_ret` | 2 | 23 | 25 | 8% |  |
| `limit_down_proximity_early` | 0 | 2 | 2 | 0% |  |
| `trend_bar_close_consistency` | 0 | 4 | 4 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 4 | 4 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 24 | 24 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 23 | 23 | 0% |  |
| `yesterday_first_30min_return` | 0 | 3 | 3 | 0% |  |
| `bar_body_rng_0` | 0 | 6 | 6 | 0% |  |
| `bar_ret_0` | 0 | 7 | 7 | 0% |  |
| `late_bar_momentum` | 0 | 2 | 2 | 0% |  |
| `volume_surge_direction` | 0 | 3 | 3 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 2 | 2 | 0% |  |
| `net_volume_flow` | 0 | 4 | 4 | 0% |  |
| `first_bar_return` | 0 | 8 | 8 | 0% |  |
| `first_bar_sentiment` | 0 | 16 | 16 | 0% |  |
| `max_down_ret` | 0 | 4 | 4 | 0% |  |
| `star50_limit_proximity_early` | 0 | 18 | 18 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=1, TP=35, FP rate=3%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=8, FP rate=20%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=21, FP rate=0%

