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
| 300ETF | single | 3 | 0 | 1 | 2 | 0% | 0.71 |
| 500ETF | single | 13 | 1 | 0 | 12 | 8% | 0.87 |
| 159915ETF | single | 10 | 1 | 0 | 9 | 10% | 0.88 |

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

### 500ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__close_vs_open_range`** (Lock IC=-0.0211, Sharpe=-0.4893)
- Yearly ICs: 2015: +0.144 | 2016: +0.048 | 2017: +0.100 | 2018: +0.185 | 2019: +0.059 | 2020: +0.099 | 2021: -0.069 | 2022: +0.102
- IC CV=0.85, Neg years=1/8, Half ratio=0.50, Recency ratio=0.17
- Weak component: `close_vs_open_range` (CV=0.47, neg years=0)
- Regime ICs: Q1_low_vol=+0.044, Q2=-0.025, Q3_mid=+0.045, Q4=+0.093, Q5_high_vol=+0.240

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0132, Sharpe=-0.5256)
- Yearly ICs: 2015: +0.026 | 2016: +0.053 | 2017: +0.097 | 2018: +0.128 | 2019: -0.015 | 2020: +0.094 | 2021: +0.082 | 2022: -0.005
- IC CV=0.84, Neg years=2/8, Half ratio=0.53, Recency ratio=0.98
- Weak component: `volatility_expansion_trend_vector` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.011, Q3_mid=+0.095, Q4=+0.042, Q5_high_vol=+0.091

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`opening_drive_thrust_ratio`** (Lock IC=+0.0564, Sharpe=-0.0889)
- Yearly ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.039 | 2018: +0.176 | 2019: +0.078 | 2020: +0.042 | 2021: +0.170 | 2022: +0.024
- IC CV=0.87, Neg years=1/8, Half ratio=0.96, Recency ratio=1.17
- Regime ICs: Q1_low_vol=-0.008, Q2=+0.015, Q3_mid=+0.079, Q4=+0.157, Q5_high_vol=+0.140

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0592, Sharpe=+0.4308)
- Yearly ICs: 2015: +0.112 | 2016: +0.089 | 2017: +0.021 | 2018: +0.183 | 2019: +0.078 | 2020: -0.001 | 2021: +0.127 | 2022: +0.049
- IC CV=0.68, Neg years=1/8, Half ratio=0.57, Recency ratio=0.88
- Weak component: `max_up_ret` (CV=0.90)

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0662, Sharpe=+0.0044)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109
- IC CV=1.02, Neg years=1/8, Half ratio=0.66, Recency ratio=0.75

### 500ETF — `single` True Positives

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1058, Sharpe=+1.1006)
- Yearly ICs: 2015: +0.266 | 2016: +0.121 | 2017: +0.105 | 2018: +0.199 | 2019: +0.090 | 2020: +0.107 | 2021: +0.138 | 2022: +0.091
- IC CV=0.42, Neg years=0/8, Half ratio=0.56, Recency ratio=0.59
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.57)

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0976, Sharpe=+0.9250)
- Yearly ICs: 2015: +0.288 | 2016: +0.068 | 2017: +0.194 | 2018: +0.151 | 2019: +0.172 | 2020: +0.117 | 2021: +0.091 | 2022: +0.034
- IC CV=0.54, Neg years=0/8, Half ratio=0.56, Recency ratio=0.35
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1217, Sharpe=+0.8196)
- Yearly ICs: 2015: +0.280 | 2016: +0.121 | 2017: +0.223 | 2018: +0.184 | 2019: +0.172 | 2020: +0.173 | 2021: +0.142 | 2022: +0.014
- IC CV=0.44, Neg years=0/8, Half ratio=0.60, Recency ratio=0.39
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)

**`combo_min__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0787, Sharpe=+0.6658)
- Yearly ICs: 2015: +0.220 | 2016: +0.127 | 2017: +0.141 | 2018: +0.227 | 2019: +0.145 | 2020: +0.087 | 2021: +0.098 | 2022: +0.065
- IC CV=0.40, Neg years=0/8, Half ratio=0.50, Recency ratio=0.47
- Weak component: `first_bar_sentiment` (CV=0.45)

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1175, Sharpe=+0.4851)
- Yearly ICs: 2015: +0.266 | 2016: +0.178 | 2017: +0.079 | 2018: +0.133 | 2019: +0.078 | 2020: +0.127 | 2021: +0.110 | 2022: +0.120
- IC CV=0.42, Neg years=0/8, Half ratio=0.58, Recency ratio=0.52
- Weak component: `close_vs_open_range` (CV=0.47)

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1223, Sharpe=+0.4818)
- Yearly ICs: 2015: +0.175 | 2016: +0.063 | 2017: +0.223 | 2018: +0.101 | 2019: +0.174 | 2020: +0.110 | 2021: +0.090 | 2022: +0.106
- IC CV=0.39, Neg years=0/8, Half ratio=0.72, Recency ratio=0.83
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_clamp_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0851, Sharpe=+0.4559)
- Yearly ICs: 2015: +0.313 | 2016: +0.108 | 2017: +0.187 | 2018: +0.215 | 2019: +0.120 | 2020: +0.143 | 2021: +0.150 | 2022: +0.059
- IC CV=0.45, Neg years=0/8, Half ratio=0.54, Recency ratio=0.50
- Weak component: `early_late_momentum_divergence` (CV=0.70)

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.1003, Sharpe=+0.4546)
- Yearly ICs: 2015: +0.266 | 2016: +0.079 | 2017: +0.222 | 2018: +0.215 | 2019: +0.114 | 2020: +0.131 | 2021: +0.132 | 2022: +0.092
- IC CV=0.41, Neg years=0/8, Half ratio=0.57, Recency ratio=0.65
- Weak component: `opening_drive_thrust_ratio` (CV=0.42)

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0792, Sharpe=+0.3953)
- Yearly ICs: 2015: +0.206 | 2016: +0.115 | 2017: +0.109 | 2018: +0.281 | 2019: +0.096 | 2020: +0.130 | 2021: +0.101 | 2022: +0.112
- IC CV=0.43, Neg years=0/8, Half ratio=0.52, Recency ratio=0.66
- Weak component: `bar_ret_0` (CV=0.41)

**`combo_ratio__bar_ret_0__net_volume_flow`** (Lock IC=+0.0500, Sharpe=+0.3938)
- Yearly ICs: 2015: +0.180 | 2016: +0.055 | 2017: +0.106 | 2018: +0.193 | 2019: +0.120 | 2020: +0.060 | 2021: +0.138 | 2022: +0.020
- IC CV=0.52, Neg years=0/8, Half ratio=0.53, Recency ratio=0.67
- Weak component: `bar_ret_0` (CV=0.41)

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0958, Sharpe=+0.2125)
- Yearly ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.233 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.071 | 2022: +0.082
- IC CV=0.61, Neg years=0/8, Half ratio=0.58, Recency ratio=0.47
- Weak component: `star50_limit_proximity_early` (CV=0.61)

**`combo_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0990, Sharpe=+0.1521)
- Yearly ICs: 2015: +0.230 | 2016: +0.112 | 2017: +0.202 | 2018: +0.197 | 2019: +0.110 | 2020: +0.127 | 2021: +0.063 | 2022: +0.120
- IC CV=0.37, Neg years=0/8, Half ratio=0.51, Recency ratio=0.53
- Weak component: `star50_limit_proximity_early` (CV=0.61)

### 159915ETF — `single` True Positives

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1458, Sharpe=+1.3138)
- Yearly ICs: 2015: +0.191 | 2016: +0.046 | 2017: +0.008 | 2018: +0.125 | 2019: +0.235 | 2020: +0.126 | 2021: +0.142 | 2022: +0.096
- IC CV=0.56, Neg years=0/8, Half ratio=1.26, Recency ratio=1.00
- Weak component: `star50_limit_proximity_early` (CV=0.69)

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1277, Sharpe=+1.0889)
- Yearly ICs: 2015: +0.132 | 2016: +0.101 | 2017: +0.040 | 2018: +0.088 | 2019: +0.144 | 2020: +0.062 | 2021: +0.147 | 2022: +0.167
- IC CV=0.38, Neg years=0/8, Half ratio=1.18, Recency ratio=1.34
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.44)

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.1260, Sharpe=+1.0612)
- Yearly ICs: 2015: +0.252 | 2016: +0.132 | 2017: +0.036 | 2018: +0.078 | 2019: +0.206 | 2020: +0.150 | 2021: +0.154 | 2022: +0.131
- IC CV=0.45, Neg years=0/8, Half ratio=1.04, Recency ratio=0.74
- Weak component: `first_bar_sentiment` (CV=0.75)

**`volatility_expansion_trend_vector`** (Lock IC=+0.1157, Sharpe=+1.0095)
- Yearly ICs: 2015: +0.127 | 2016: +0.016 | 2017: +0.028 | 2018: +0.009 | 2019: +0.101 | 2020: +0.047 | 2021: +0.138 | 2022: +0.089
- IC CV=0.69, Neg years=0/8, Half ratio=1.44, Recency ratio=1.58

**`combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0958, Sharpe=+0.8917)
- Yearly ICs: 2015: +0.209 | 2016: +0.166 | 2017: -0.009 | 2018: +0.130 | 2019: +0.187 | 2020: +0.127 | 2021: +0.143 | 2022: +0.053
- IC CV=0.53, Neg years=1/8, Half ratio=0.83, Recency ratio=0.52
- Weak component: `first_bar_sentiment` (CV=0.75)

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1302, Sharpe=+0.6763)
- Yearly ICs: 2015: +0.184 | 2016: +0.102 | 2017: -0.035 | 2018: +0.096 | 2019: +0.089 | 2020: +0.078 | 2021: +0.064 | 2022: +0.131
- IC CV=0.66, Neg years=1/8, Half ratio=0.77, Recency ratio=0.68
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.1169, Sharpe=+0.6278)
- Yearly ICs: 2015: +0.194 | 2016: +0.089 | 2017: +0.026 | 2018: +0.081 | 2019: +0.195 | 2020: +0.106 | 2021: +0.095 | 2022: +0.098
- IC CV=0.49, Neg years=0/8, Half ratio=1.04, Recency ratio=0.68
- Weak component: `late_bar_momentum` (CV=0.82)

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1090, Sharpe=+0.3724)
- Yearly ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087 | 2022: +0.139
- IC CV=0.66, Neg years=0/8, Half ratio=1.03, Recency ratio=1.15
- Weak component: `star50_limit_proximity_early` (CV=0.69)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1075, Sharpe=+0.3554)
- Yearly ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.080 | 2019: +0.132 | 2020: +0.100 | 2021: +0.035 | 2022: +0.178
- IC CV=0.82, Neg years=1/8, Half ratio=1.22, Recency ratio=0.96
- Weak component: `yesterday_first_30min_return` (CV=0.92)

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | gradual | +0.1772 | +0.0570 | -0.0793 | 1y |
| `opening_drive_thrust_ratio` | Median | gradual | +0.1663 | +0.0331 | -0.1510 | 1y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0576 | +0.0214 | +0.1515 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=2, persistent=1

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1561 | +0.1336 | +0.0302 | 3y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.1071 | +0.1459 | -0.0338 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1059 | +0.1666 | +0.0842 | ∞ |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0915 | +0.1184 | +0.1051 | 2y |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0781 | +0.1444 | +0.1943 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0766 | +0.0799 | +0.0886 | ∞ |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0715 | +0.1035 | +0.1197 | ∞ |
| `combo_min__first_bar_sentiment__first_bar_return` | TP | gradual | +0.0698 | +0.1230 | -0.0173 | 3y |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0630 | +0.1130 | +0.0822 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0514 | +0.1238 | +0.0782 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | TP | persistent | +0.0501 | +0.0982 | +0.0041 | 3y |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | FP | gradual | +0.0157 | +0.0088 | -0.0217 | 2y |
| `combo_ratio__bar_ret_0__net_volume_flow` | TP | gradual | +0.0078 | +0.0609 | -0.0032 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=4, persistent=9

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__close_vs_open_range`: Y1:+0.016 → Y2:+0.009 → Y3:-0.094 → Y4:-0.022

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1829 | +0.1255 | +0.0725 | 3y |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.1754 | +0.0818 | +0.0863 | 1y |
| `volatility_expansion_trend_vector` | TP | gradual | +0.1663 | +0.0804 | -0.0952 | 1y |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1537 | +0.1217 | +0.1543 | ∞ |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1471 | +0.0787 | +0.0305 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1469 | +0.0883 | +0.0544 | 3y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1366 | +0.1389 | +0.0904 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1157 | +0.0779 | +0.1278 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0826 | +0.0831 | +0.1479 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | fast | +0.0544 | -0.0517 | -0.0008 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=1, gradual=1, persistent=8

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:+0.054 → Y2:-0.052 → Y3:-0.026 → Y4:-0.001

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 15/20 top rejects are profitable (75%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `combo_mean__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Sharpe=+0.5376
- `combo_z_sum__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Sharpe=+0.5376

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_clamp_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1751, Lock IC=+0.0617, Sharpe=+0.8233
- `combo_clamp_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1643, Lock IC=+0.0619, Sharpe=+0.8233
- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Sharpe=+0.7446

**Temporal Validation Gate**: 14/20 top rejects are profitable (70%)

- `combo_diff__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=+0.1479, Lock IC=+0.0593, Sharpe=+0.6920
- `combo_z_diff__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=+0.1479, Lock IC=+0.0593, Sharpe=+0.6920
- `combo_diff__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.1479, Lock IC=+0.0593, Sharpe=+0.6920

**B3 Composite Floor**: 14/20 top rejects are profitable (70%)

- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.1982, Lock IC=+0.0610, Sharpe=+0.5317
- `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1979, Lock IC=+0.0611, Sharpe=+0.5317
- `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`: Train IC=+0.2052, Lock IC=+0.0587, Sharpe=+0.5249

**B4 Correlation Gate**: 15/20 top rejects are profitable (75%)

- `combo_rank_max__max_up_ret__bar_ret_0`: Train IC=+0.2083, Lock IC=+0.0599, Sharpe=+0.6497
- `combo_rank_max__max_up_ret__first_bar_return`: Train IC=+0.2083, Lock IC=+0.0599, Sharpe=+0.6497
- `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`: Train IC=+0.2054, Lock IC=+0.0587, Sharpe=+0.5249

### 500ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.2819, Lock IC=+0.1134, Sharpe=+0.8586

**B2 Rolling Guard**: 14/20 top rejects are profitable (70%)

- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Sharpe=+0.5808
- `combo_tri_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1954, Lock IC=+0.0826, Sharpe=+0.4663
- `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Sharpe=+0.3984

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_clamp_diff__smooth_momentum_structure__trend_day_regime_conviction`: Train IC=+0.2510, Lock IC=+0.1002, Sharpe=+1.2074
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Sharpe=+0.8023
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Sharpe=+0.7824

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Sharpe=+0.9985

**Adaptive Correlation Gate**: 4/5 top rejects are profitable (80%)

- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2231, Lock IC=+0.0936, Sharpe=+0.7388
- `combo_max__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2150, Lock IC=+0.0840, Sharpe=+0.6202
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`: Train IC=+0.2722, Lock IC=+0.1066, Sharpe=+0.5017

### 159915ETF — `single`

**7-Year Jackknife**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Sharpe=+1.8587
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2421, Lock IC=+0.0980, Sharpe=+1.4278

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Sharpe=+1.3582
- `combo_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2299, Lock IC=+0.1187, Sharpe=+1.1602
- `combo_z_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2299, Lock IC=+0.1187, Sharpe=+1.1602

**Temporal Validation Gate**: 19/20 top rejects are profitable (95%)

- `combo_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_z_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3073, Lock IC=+0.1158, Sharpe=+1.5577
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Sharpe=+1.4133
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2393, Lock IC=+0.1373, Sharpe=+1.3191

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Sharpe=+1.6742
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Sharpe=+1.6287

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 882 | 78 | 16 | 37 | 25 | 21% | 32% |
| B2 Rolling Guard | 148 | 78 | 22 | 19 | 37 | 28% | 47% |
| Temporal Validation Gate | 58 | 58 | 2 | 24 | 32 | 3% | 55% |
| BH-FDR Gate | 5 | 5 | 0 | 5 | 0 | 0% | 0% |
| B3 Composite Floor | 23 | 23 | 0 | 6 | 17 | 0% | 74% |
| B4 Correlation Gate | 35 | 35 | 0 | 5 | 30 | 0% | 86% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Sharpe=+0.9639
- `combo_mean__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Sharpe=+0.5376
- `combo_z_sum__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Sharpe=+0.5376

**B2 Rolling Guard** — top TP casualties:
- `combo_clamp_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1751, Lock IC=+0.0617, Sharpe=+0.8233
- `combo_clamp_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1643, Lock IC=+0.0619, Sharpe=+0.8233
- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Sharpe=+0.7446

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_z_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1470, Lock IC=+0.0614, Sharpe=+0.8233
- `combo_diff__smooth_momentum_structure__first_bar_return`: Train IC=+0.1469, Lock IC=+0.0614, Sharpe=+0.8233

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.1982, Lock IC=+0.0610, Sharpe=+0.5317
- `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1979, Lock IC=+0.0611, Sharpe=+0.5317
- `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`: Train IC=+0.2052, Lock IC=+0.0587, Sharpe=+0.5249

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_max__max_up_ret__bar_ret_0`: Train IC=+0.2083, Lock IC=+0.0599, Sharpe=+0.6497
- `combo_rank_max__max_up_ret__first_bar_return`: Train IC=+0.2083, Lock IC=+0.0599, Sharpe=+0.6497
- `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`: Train IC=+0.2054, Lock IC=+0.0587, Sharpe=+0.5249

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1823 | 78 | 27 | 23 | 28 | 35% | 36% |
| B2 Rolling Guard | 242 | 78 | 19 | 24 | 35 | 24% | 45% |
| Temporal Validation Gate | 117 | 78 | 16 | 5 | 57 | 21% | 73% |
| BH-FDR Gate | 7 | 7 | 1 | 6 | 0 | 14% | 0% |
| B3 Composite Floor | 156 | 78 | 1 | 4 | 73 | 1% | 94% |
| B4 Correlation Gate | 629 | 78 | 0 | 10 | 68 | 0% | 87% |
| Adaptive Correlation Gate | 5 | 5 | 0 | 1 | 4 | 0% | 80% |

**7-Year Jackknife** — top TP casualties:
- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2305, Lock IC=+0.1016, Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Sharpe=+0.9464

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0336, Lock IC=+0.0707, Sharpe=+0.8914
- `combo_rel_diff__body_size_progression__first_bar_return`: Train IC=+0.1891, Lock IC=+0.0693, Sharpe=+0.5882
- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Sharpe=+0.5808

**Temporal Validation Gate** — top TP casualties:
- `combo_clamp_diff__smooth_momentum_structure__trend_day_regime_conviction`: Train IC=+0.2510, Lock IC=+0.1002, Sharpe=+1.2074
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2906, Lock IC=+0.1008, Sharpe=+1.1528

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1987, Lock IC=+0.0381, Sharpe=+1.0944
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression`: Train IC=+0.1094, Lock IC=+0.0362, Sharpe=+1.0604
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__body_size_progression`: Train IC=+0.1094, Lock IC=+0.0362, Sharpe=+1.0604

**B4 Correlation Gate** — top TP casualties:
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Sharpe=+1.1317
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Sharpe=+0.9985

**Adaptive Correlation Gate** — top TP casualties:
- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2231, Lock IC=+0.0936, Sharpe=+0.7388
- `combo_max__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2150, Lock IC=+0.0840, Sharpe=+0.6202
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`: Train IC=+0.2722, Lock IC=+0.1066, Sharpe=+0.5017

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1181 | 78 | 23 | 15 | 40 | 29% | 51% |
| B2 Rolling Guard | 312 | 78 | 19 | 5 | 54 | 24% | 69% |
| Temporal Validation Gate | 29 | 29 | 5 | 0 | 24 | 17% | 83% |
| BH-FDR Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 148 | 78 | 0 | 1 | 77 | 0% | 99% |
| B4 Correlation Gate | 172 | 78 | 0 | 0 | 78 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Sharpe=+1.8587
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2421, Lock IC=+0.0980, Sharpe=+1.4278

**B2 Rolling Guard** — top TP casualties:
- `combo_mean__max_up_ret__directional_volume_signature`: Train IC=+0.1547, Lock IC=+0.1106, Sharpe=+1.5561
- `combo_z_sum__max_up_ret__directional_volume_signature`: Train IC=+0.1547, Lock IC=+0.1106, Sharpe=+1.5561
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Sharpe=+1.3582

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_z_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1458, Lock IC=+0.1257, Sharpe=+1.1249
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2051, Lock IC=+0.1248, Sharpe=+1.1179

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3073, Lock IC=+0.1158, Sharpe=+1.5577
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2324, Lock IC=+0.1197, Sharpe=+1.5206
- `combo_mean__first_bar_return__limit_down_proximity_early`: Train IC=+0.2026, Lock IC=+0.1193, Sharpe=+1.4931

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Sharpe=+1.6742
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Sharpe=+1.6287

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (58 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 58 | 50 | 2 | 29 | 19 | 4% | 58% |

### 500ETF — `single` (117 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 114 | 50 | 0 | 50 | 0 | 0% | 100% |
| recency_ratio >= 2.5 (late-concentrated) | 3 | 3 | 0 | 2 | 1 | 0% | 67% |

**Top TP killed by recency_ratio cap:**
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Train IC=+0.1291, Lock IC=+0.0798, Sharpe=+0.5154
- `combo_sig_product__trend_day_regime_conviction__max_down_ret`: Train IC=+0.1323, Lock IC=+0.0715, Sharpe=+0.1942

### 159915ETF — `single` (29 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 29 | 29 | 5 | 24 | 0 | 17% | 83% |

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volatility_expansion_trend_vector` | 1 | 1 | 2 | 50% |  |
| `close_vs_open_range` | 1 | 1 | 2 | 50% |  |
| `max_up_ret` | 2 | 10 | 12 | 17% |  |
| `bar_body_rng_0` | 0 | 2 | 2 | 0% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 3 | 3 | 0% |  |
| `first_bar_sentiment` | 0 | 3 | 3 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 3 | 3 | 0% |  |
| `first_bar_return` | 0 | 3 | 3 | 0% |  |
| `bar_ret_0` | 0 | 4 | 4 | 0% |  |
| `net_volume_flow` | 0 | 2 | 2 | 0% |  |
| `star50_limit_proximity_early` | 0 | 8 | 8 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=8, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=3, FP rate=40%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=4, FP rate=0%

