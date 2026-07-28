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
| 300ETF | single | 2 | 1 | 1 | 0 | 50% | 0.19 |
| 500ETF | single | 12 | 0 | 1 | 11 | 0% | 0.91 |
| 159915ETF | single | 12 | 2 | 1 | 9 | 17% | 0.72 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 159915ETF — `single` (FP=2, TP=9)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 1.146 | 0.559 | 1.146 | 0.521 | +1.29 | 1.292 | 91% |
| half_ratio | 4.351 | 1.686 | 4.351 | 1.487 | +1.03 | 5.756 | 91% |
| n_negative_years | 1.000 | 0.444 | 1.000 | 0.000 | +0.70 | 1.500 | 91% |
| ic_std_across_regimes | 0.034 | 0.043 | 0.034 | 0.040 | -0.61 | 0.076 | 73% |
| n_negative_regimes | 0.500 | 0.222 | 0.500 | 0.000 | +0.60 | 0.500 | 73% |
| recency_ratio | 2.341 | -5.160 | 2.341 | 2.063 | +0.47 | 4.023 | 82% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`early_order_flow_imbalance`** (Lock IC=-0.0189, Sharpe=-0.4041)
- Yearly ICs: 2016: +0.074 | 2017: -0.067 | 2018: +0.082 | 2019: +0.048 | 2020: -0.019 | 2021: +0.147 | 2022: +0.098 | 2023: +0.111
- IC CV=1.12, Neg years=2/8, Half ratio=2.03, Recency ratio=31.17
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.094, Q3_mid=+0.096, Q4=+0.088, Q5_high_vol=+0.045

### 159915ETF — `single` False Positives

**`consecutive_higher_highs`** (Lock IC=-0.0251, Sharpe=-0.2592)
- Yearly ICs: 2016: +0.048 | 2017: +0.008 | 2018: -0.086 | 2019: +0.052 | 2020: -0.038 | 2021: +0.100 | 2022: +0.129 | 2023: +0.097
- IC CV=1.78, Neg years=2/8, Half ratio=7.95, Recency ratio=4.04
- Regime ICs: Q1_low_vol=+0.003, Q2=+0.070, Q3_mid=+0.045, Q4=+0.048, Q5_high_vol=+0.051

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0273, Sharpe=+0.1690)
- Yearly ICs: 2016: +0.053 | 2017: +0.103 | 2018: +0.108 | 2019: +0.010 | 2020: +0.088 | 2021: +0.048 | 2022: +0.028 | 2023: +0.071
- IC CV=0.52, Neg years=0/8, Half ratio=0.75, Recency ratio=0.64
- Weak component: `volatility_expansion_trend_vector` (CV=0.74, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=-0.003, Q3_mid=+0.061, Q4=+0.073, Q5_high_vol=+0.070

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0083, Sharpe=-0.0883)
- Yearly ICs: 2016: +0.089 | 2017: +0.022 | 2018: +0.184 | 2019: +0.073 | 2020: -0.002 | 2021: +0.132 | 2022: +0.046 | 2023: +0.172
- IC CV=0.71, Neg years=1/8, Half ratio=0.87, Recency ratio=1.96
- Weak component: `max_up_ret` (CV=0.89)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.081, Q3_mid=+0.062, Q4=+0.059, Q5_high_vol=+0.168

### 500ETF — `single` Median Features

**`combo_rank_min__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0742, Sharpe=-0.0464)
- Yearly ICs: 2016: +0.148 | 2017: +0.146 | 2018: +0.232 | 2019: +0.124 | 2020: +0.121 | 2021: +0.095 | 2022: +0.065 | 2023: +0.058
- IC CV=0.42, Neg years=0/8, Half ratio=0.52, Recency ratio=0.42
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.147, Q2=-0.014, Q3_mid=+0.105, Q4=+0.173, Q5_high_vol=+0.155

### 159915ETF — `single` Median Features

**`combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0677, Sharpe=-0.1117)
- Yearly ICs: 2016: +0.055 | 2017: +0.020 | 2018: +0.035 | 2019: +0.139 | 2020: +0.033 | 2021: +0.160 | 2022: +0.086 | 2023: +0.142
- IC CV=0.63, Neg years=0/8, Half ratio=1.66, Recency ratio=3.03
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.132, Q3_mid=+0.124, Q4=+0.101, Q5_high_vol=+0.058

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`combo_rank_min__star50_limit_proximity_early__opening_momentum_score`** (Lock IC=+0.1213, Sharpe=+1.2788)
- Yearly ICs: 2016: +0.064 | 2017: +0.219 | 2018: +0.070 | 2019: +0.098 | 2020: +0.129 | 2021: +0.081 | 2022: +0.081 | 2023: +0.077
- IC CV=0.47, Neg years=0/8, Half ratio=0.82, Recency ratio=0.56
- Weak component: `star50_limit_proximity_early` (CV=0.55)

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0934, Sharpe=+1.2539)
- Yearly ICs: 2016: +0.095 | 2017: +0.149 | 2018: +0.192 | 2019: +0.092 | 2020: +0.099 | 2021: +0.119 | 2022: +0.084 | 2023: +0.002
- IC CV=0.49, Neg years=0/8, Half ratio=0.64, Recency ratio=0.35
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1193, Sharpe=+0.5966)
- Yearly ICs: 2016: +0.120 | 2017: +0.225 | 2018: +0.180 | 2019: +0.173 | 2020: +0.172 | 2021: +0.143 | 2022: +0.006 | 2023: +0.103
- IC CV=0.44, Neg years=0/8, Half ratio=0.66, Recency ratio=0.32
- Weak component: `opening_drive_thrust_ratio` (CV=0.40)

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0875, Sharpe=+0.5745)
- Yearly ICs: 2016: +0.036 | 2017: +0.153 | 2018: +0.194 | 2019: +0.171 | 2020: +0.188 | 2021: +0.150 | 2022: +0.028 | 2023: +0.094
- IC CV=0.49, Neg years=0/8, Half ratio=0.83, Recency ratio=0.65
- Weak component: `smooth_momentum_structure` (CV=0.62)

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0910, Sharpe=+0.5264)
- Yearly ICs: 2016: +0.077 | 2017: +0.226 | 2018: +0.202 | 2019: +0.110 | 2020: +0.154 | 2021: +0.112 | 2022: +0.087 | 2023: +0.122
- IC CV=0.37, Neg years=0/8, Half ratio=0.81, Recency ratio=0.69
- Weak component: `trend_bar_close_consistency` (CV=0.66)

**`combo_min__net_volume_flow__max_down_ret`** (Lock IC=+0.1016, Sharpe=+0.5253)
- Yearly ICs: 2016: +0.061 | 2017: +0.194 | 2018: +0.133 | 2019: +0.100 | 2020: +0.132 | 2021: +0.081 | 2022: +0.097 | 2023: +0.080
- IC CV=0.36, Neg years=0/8, Half ratio=0.78, Recency ratio=0.69
- Weak component: `max_down_ret` (CV=0.62)

**`combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1529, Sharpe=+0.4587)
- Yearly ICs: 2016: -0.006 | 2017: +0.187 | 2018: +0.098 | 2019: +0.192 | 2020: +0.089 | 2021: +0.103 | 2022: +0.045 | 2023: +0.029
- IC CV=0.72, Neg years=1/8, Half ratio=0.54, Recency ratio=0.41
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.62)

**`combo_max__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1108, Sharpe=+0.2764)
- Yearly ICs: 2016: +0.069 | 2017: +0.197 | 2018: +0.124 | 2019: +0.121 | 2020: +0.111 | 2021: +0.016 | 2022: +0.131 | 2023: +0.053
- IC CV=0.51, Neg years=0/8, Half ratio=0.67, Recency ratio=0.69
- Weak component: `star50_limit_proximity_early` (CV=0.55)

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0747, Sharpe=+0.2436)
- Yearly ICs: 2016: +0.100 | 2017: +0.194 | 2018: +0.213 | 2019: +0.156 | 2020: +0.156 | 2021: +0.137 | 2022: +0.066 | 2023: +0.083
- IC CV=0.35, Neg years=0/8, Half ratio=0.70, Recency ratio=0.51
- Weak component: `body_size_progression` (CV=0.60)

**`trend_strength_intraday`** (Lock IC=+0.0894, Sharpe=+0.1090)
- Yearly ICs: 2016: +0.103 | 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083
- IC CV=0.36, Neg years=0/8, Half ratio=0.93, Recency ratio=1.36

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0818, Sharpe=+0.0961)
- Yearly ICs: 2016: +0.094 | 2017: +0.257 | 2018: +0.230 | 2019: +0.145 | 2020: +0.132 | 2021: +0.089 | 2022: +0.091 | 2023: +0.045
- IC CV=0.51, Neg years=0/8, Half ratio=0.50, Recency ratio=0.39
- Weak component: `max_down_ret` (CV=0.62)

### 159915ETF — `single` True Positives

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1085, Sharpe=+0.9171)
- Yearly ICs: 2016: +0.055 | 2017: +0.019 | 2018: +0.072 | 2019: +0.188 | 2020: +0.090 | 2021: +0.157 | 2022: +0.143 | 2023: +0.153
- IC CV=0.50, Neg years=0/8, Half ratio=1.86, Recency ratio=4.00
- Weak component: `demark_setup_reversal_early` (CV=0.76)

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1235, Sharpe=+0.8704)
- Yearly ICs: 2016: +0.113 | 2017: -0.018 | 2018: +0.194 | 2019: +0.243 | 2020: +0.166 | 2021: +0.154 | 2022: +0.098 | 2023: +0.185
- IC CV=0.52, Neg years=1/8, Half ratio=1.10, Recency ratio=2.98
- Weak component: `bar_body_rng_0` (CV=0.54)

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1236, Sharpe=+0.8328)
- Yearly ICs: 2016: +0.103 | 2017: +0.037 | 2018: +0.112 | 2019: +0.155 | 2020: +0.064 | 2021: +0.163 | 2022: +0.158 | 2023: +0.133
- IC CV=0.37, Neg years=0/8, Half ratio=1.49, Recency ratio=2.06
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)

**`close_vs_open_range`** (Lock IC=+0.1017, Sharpe=+0.6838)
- Yearly ICs: 2016: +0.029 | 2017: +0.037 | 2018: +0.002 | 2019: +0.076 | 2020: +0.040 | 2021: +0.122 | 2022: +0.087 | 2023: +0.162
- IC CV=0.72, Neg years=0/8, Half ratio=3.56, Recency ratio=3.79

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1242, Sharpe=+0.6361)
- Yearly ICs: 2016: +0.102 | 2017: -0.036 | 2018: +0.096 | 2019: +0.088 | 2020: +0.077 | 2021: +0.065 | 2022: +0.130 | 2023: +0.152
- IC CV=0.62, Neg years=1/8, Half ratio=1.59, Recency ratio=4.28
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1119, Sharpe=+0.4883)
- Yearly ICs: 2016: +0.045 | 2017: -0.050 | 2018: +0.080 | 2019: +0.133 | 2020: +0.101 | 2021: +0.040 | 2022: +0.179 | 2023: +0.115
- IC CV=0.81, Neg years=1/8, Half ratio=1.67, Recency ratio=-68.28
- Weak component: `yesterday_first_30min_return` (CV=0.92)

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1267, Sharpe=+0.4263)
- Yearly ICs: 2016: +0.140 | 2017: -0.026 | 2018: +0.118 | 2019: +0.177 | 2020: +0.168 | 2021: +0.131 | 2022: +0.125 | 2023: +0.069
- IC CV=0.54, Neg years=1/8, Half ratio=1.18, Recency ratio=1.70
- Weak component: `first_bar_sentiment` (CV=0.76)

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return`** (Lock IC=+0.0781, Sharpe=+0.0786)
- Yearly ICs: 2016: +0.108 | 2017: +0.033 | 2018: +0.089 | 2019: +0.180 | 2020: +0.105 | 2021: +0.190 | 2022: +0.100 | 2023: +0.184
- IC CV=0.42, Neg years=0/8, Half ratio=1.43, Recency ratio=2.01
- Weak component: `opening_drive_thrust_ratio` (CV=0.53)

**`early_range`** (Lock IC=+0.0033, Sharpe=+0.0118)
- Yearly ICs: 2016: +0.118 | 2017: +0.018 | 2018: +0.076 | 2019: +0.026 | 2020: +0.079 | 2021: +0.032 | 2022: +0.062 | 2023: +0.076
- IC CV=0.51, Neg years=0/8, Half ratio=1.29, Recency ratio=1.01

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__max_up_ret__bar_body_rng_0` | Median | gradual | +0.0538 | +0.0224 | -0.0760 | 1y |
| `early_order_flow_imbalance` | FP | immediate | -0.0011 | +0.0765 | -0.2024 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=0, gradual=1, persistent=0

**FP decay trajectories:**

- `early_order_flow_imbalance`: Y1:-0.001 → Y2:+0.076 → Y3:-0.202

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1587 | +0.0925 | +0.0908 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1508 | +0.0908 | +0.2248 | ∞ |
| `trend_strength_intraday` | TP | gradual | +0.1407 | +0.1166 | -0.0474 | 2y |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.1350 | +0.0579 | +0.0375 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | TP | gradual | +0.1330 | +0.1324 | -0.0522 | 2y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1287 | +0.0921 | +0.0337 | 2y |
| `combo_max__bar_ret_0__max_down_ret` | TP | persistent | +0.1244 | +0.1076 | +0.0004 | 2y |
| `combo_rank_min__star50_limit_proximity_early__opening_momentum_score` | TP | persistent | +0.1223 | +0.1346 | +0.0943 | ∞ |
| `combo_min__net_volume_flow__max_down_ret` | TP | persistent | +0.1137 | +0.1375 | +0.0352 | 2y |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.1039 | +0.1080 | +0.0783 | ∞ |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.1022 | +0.0249 | +0.0948 | 1y |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | Median | gradual | +0.1017 | +0.1252 | -0.0261 | 2y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=3, persistent=9

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1247 | +0.1135 | +0.1174 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1214 | +0.0780 | +0.1570 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1153 | +0.1681 | +0.0618 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.1063 | +0.1008 | +0.1704 | ∞ |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Median | gradual | +0.0965 | +0.1114 | -0.0547 | 2y |
| `close_vs_open_range` | TP | gradual | +0.0931 | +0.2187 | -0.0831 | 2y |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0817 | +0.1293 | +0.1257 | ∞ |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | TP | persistent | +0.0775 | +0.1848 | +0.0010 | 2y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | TP | gradual | +0.0735 | +0.1687 | -0.0686 | 2y |
| `early_range` | TP | gradual | +0.0086 | +0.0512 | -0.1056 | ∞ |
| `consecutive_higher_highs` | FP | immediate | -0.0237 | +0.0232 | -0.1355 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0535 | -0.0299 | +0.0233 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=0, gradual=4, persistent=6

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.053 → Y2:-0.030 → Y3:+0.023
- `consecutive_higher_highs`: Y1:-0.024 → Y2:+0.023 → Y3:-0.135

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 159915ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.672±0.012 | 0.718±0.046 | 15% | USEFUL |
| ic_ir | 0.459±0.015 | 0.586±0.116 | 2% | USEFUL |
| p_value | 0.001±0.001 | 0.003±0.007 | 6% | USEFUL |
| max_corr | 0.442±0.031 | 0.499±0.211 | 9% | USEFUL |
| deflated_ic | 0.175±0.009 | 0.222±0.061 | 8% | USEFUL |
| overall_ic | 0.176±0.009 | 0.222±0.060 | 8% | USEFUL |
| raw_ic | 0.057±0.010 | 0.103±0.027 | 6% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 8/20 top rejects are profitable (40%)

- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188
- `combo_z_sum__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Sharpe=+0.5188
- `combo_rank_min__max_up_ret__bar_ret_0`: Train IC=+0.1872, Lock IC=+0.0024, Sharpe=+0.4080

**B2 Rolling Guard**: 3/20 top rejects are profitable (15%)

- `combo_clamp_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1900, Lock IC=+0.0133, Sharpe=+0.2244
- `combo_rel_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1721, Lock IC=+0.0138, Sharpe=+0.1415
- `combo_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1719, Lock IC=+0.0140, Sharpe=+0.1415

**Temporal Validation Gate**: 5/20 top rejects are profitable (25%)

- `volume_weighted_momentum_acceleration`: Train IC=+0.1838, Lock IC=+0.0201, Sharpe=+0.1887
- `combo_diff__volume_weighted_momentum_acceleration__max_up_ret`: Train IC=+0.2233, Lock IC=+0.0108, Sharpe=+0.1489
- `combo_z_diff__volume_weighted_momentum_acceleration__max_up_ret`: Train IC=+0.2233, Lock IC=+0.0108, Sharpe=+0.1489

**BH-FDR Gate**: 1/11 top rejects are profitable (9%)

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Sharpe=+0.1611

**B4 Correlation Gate**: 8/20 top rejects are profitable (40%)

- `combo_rank_max__max_up_ret__bar_ret_0`: Train IC=+0.2224, Lock IC=+0.0109, Sharpe=+0.1585
- `combo_rank_max__max_up_ret__first_bar_return`: Train IC=+0.2224, Lock IC=+0.0109, Sharpe=+0.1585
- `combo_max__first_bar_return__bar_body_rng_0`: Train IC=+0.2061, Lock IC=+0.0219, Sharpe=+0.1568

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2343, Lock IC=+0.1237, Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Sharpe=+1.1505

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Sharpe=+1.2071
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Sharpe=+1.1213
- `combo_mean__first_bar_return__max_down_ret`: Train IC=+0.2006, Lock IC=+0.0980, Sharpe=+0.7814

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621
- `combo_z_diff__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.2304, Lock IC=+0.1001, Sharpe=+1.0621
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2670, Lock IC=+0.0979, Sharpe=+1.0088

**B3 Composite Floor**: 6/6 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.1552, Lock IC=+0.0576, Sharpe=+1.0912
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.1552, Lock IC=+0.0576, Sharpe=+1.0912
- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_clamp_diff__max_up_ret__body_size_progression`: Train IC=+0.2698, Lock IC=+0.0855, Sharpe=+1.1336
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2665, Lock IC=+0.1105, Sharpe=+0.9584
- `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2575, Lock IC=+0.0857, Sharpe=+0.8706

### 159915ETF — `single`

**7-Year Jackknife**: 18/20 top rejects are profitable (90%)

- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2329, Lock IC=+0.1019, Sharpe=+1.0683
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Sharpe=+1.0349
- `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Sharpe=+1.0349

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322
- `combo_mean__first_bar_return__volatility_expansion_trend_vector`: Train IC=+0.2050, Lock IC=+0.0947, Sharpe=+0.8825

**Temporal Validation Gate**: 16/20 top rejects are profitable (80%)

- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1821, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1821, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rank_max__max_up_ret__directional_volume_signature`: Train IC=+0.1514, Lock IC=+0.0867, Sharpe=+1.2162

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2080, Lock IC=+0.1414, Sharpe=+1.4883
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2047, Lock IC=+0.1185, Sharpe=+1.3299
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2373, Lock IC=+0.1072, Sharpe=+1.2684

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2883, Lock IC=+0.1316, Sharpe=+1.5821
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2816, Lock IC=+0.1330, Sharpe=+1.4975

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 875 | 78 | 23 | 41 | 14 | 29% | 18% |
| B2 Rolling Guard | 106 | 78 | 37 | 21 | 20 | 47% | 26% |
| Temporal Validation Gate | 72 | 72 | 10 | 30 | 32 | 14% | 44% |
| BH-FDR Gate | 11 | 11 | 8 | 2 | 1 | 73% | 9% |
| B3 Composite Floor | 1 | 1 | 0 | 1 | 0 | 0% | 0% |
| B4 Correlation Gate | 59 | 59 | 11 | 17 | 31 | 19% | 53% |

**B2 Rolling Guard** — top TP casualties:
- `combo_sig_product__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1341, Lock IC=+0.0176, Sharpe=+0.6337
- `combo_sig_product__smooth_momentum_structure__first_bar_return`: Train IC=+0.1340, Lock IC=+0.0177, Sharpe=+0.6337
- `combo_max__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0814, Lock IC=+0.0326, Sharpe=+0.6120

**Temporal Validation Gate** — top TP casualties:
- `sma100_dist`: Train IC=+0.1056, Lock IC=+0.0455, Sharpe=+0.6172
- `sma10_dist`: Train IC=+0.0626, Lock IC=+0.0444, Sharpe=+0.5378
- `combo_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1362, Lock IC=+0.0148, Sharpe=+0.4746

**B4 Correlation Gate** — top TP casualties:
- `first_bar_return`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `bar_ret_0`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827
- `combo_mean__bar_ret_0__first_bar_sentiment`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.4827

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1883 | 78 | 36 | 11 | 31 | 46% | 40% |
| B2 Rolling Guard | 405 | 78 | 15 | 13 | 50 | 19% | 64% |
| Temporal Validation Gate | 121 | 78 | 21 | 7 | 50 | 27% | 64% |
| BH-FDR Gate | 7 | 7 | 1 | 6 | 0 | 14% | 0% |
| B3 Composite Floor | 6 | 6 | 0 | 0 | 6 | 0% | 100% |
| B4 Correlation Gate | 529 | 78 | 0 | 6 | 72 | 0% | 92% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2343, Lock IC=+0.1237, Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Sharpe=+1.1505

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Sharpe=+1.2071
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Sharpe=+1.1213

**Temporal Validation Gate** — top TP casualties:
- `close_location_in_range_3d`: Train IC=+0.0449, Lock IC=+0.0506, Sharpe=+1.3268
- `combo_rel_diff__smooth_momentum_structure__trend_day_regime_conviction`: Train IC=+0.2219, Lock IC=+0.0980, Sharpe=+1.2934
- `combo_diff__smooth_momentum_structure__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0974, Sharpe=+1.2934

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.1552, Lock IC=+0.0576, Sharpe=+1.0912
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.1552, Lock IC=+0.0576, Sharpe=+1.0912
- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Sharpe=+0.5788

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2051, Lock IC=+0.1194, Sharpe=+1.2468
- `combo_clamp_diff__max_up_ret__body_size_progression`: Train IC=+0.2698, Lock IC=+0.0855, Sharpe=+1.1336
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.2052, Lock IC=+0.1212, Sharpe=+1.0399

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1189 | 78 | 23 | 20 | 35 | 29% | 45% |
| B2 Rolling Guard | 221 | 78 | 21 | 9 | 48 | 27% | 62% |
| Temporal Validation Gate | 35 | 35 | 11 | 5 | 19 | 31% | 54% |
| BH-FDR Gate | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B3 Composite Floor | 90 | 78 | 0 | 2 | 76 | 0% | 97% |
| B4 Correlation Gate | 255 | 78 | 0 | 2 | 76 | 0% | 97% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Sharpe=+1.4951
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.1917, Lock IC=+0.1128, Sharpe=+1.2793

**B2 Rolling Guard** — top TP casualties:
- `combo_max__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1250, Lock IC=+0.0975, Sharpe=+1.3580
- `combo_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1250, Lock IC=+0.0975, Sharpe=+1.3580
- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Sharpe=+1.3322

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1821, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1821, Lock IC=+0.1314, Sharpe=+1.5305
- `combo_rank_max__max_up_ret__directional_volume_signature`: Train IC=+0.1514, Lock IC=+0.0867, Sharpe=+1.2162

**B3 Composite Floor** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2080, Lock IC=+0.1414, Sharpe=+1.4883
- `combo_mean__max_up_ret__directional_volume_signature`: Train IC=+0.1697, Lock IC=+0.1016, Sharpe=+1.3696
- `combo_min__opening_drive_thrust_ratio__directional_volume_signature`: Train IC=+0.1498, Lock IC=+0.0982, Sharpe=+1.3529

**B4 Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Sharpe=+1.8009
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2717, Lock IC=+0.1211, Sharpe=+1.8009

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (72 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 68 | 50 | 10 | 17 | 23 | 20% | 34% |
| recency_ratio >= 2.5 (late-concentrated) | 4 | 4 | 0 | 4 | 0 | 0% | 100% |

**Top TP killed by recency_ratio cap:**
- `combo_tri_mean__volume_weighted_momentum_acceleration__first_bar_return__bar_body_rng_0`: Train IC=+0.1352, Lock IC=+0.0188, Sharpe=+0.2741
- `combo_tri_z_mean__volume_weighted_momentum_acceleration__first_bar_return__bar_body_rng_0`: Train IC=+0.1352, Lock IC=+0.0188, Sharpe=+0.2741
- `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__bar_body_rng_0`: Train IC=+0.1350, Lock IC=+0.0187, Sharpe=+0.2741
- `combo_tri_z_mean__volume_weighted_momentum_acceleration__bar_ret_0__bar_body_rng_0`: Train IC=+0.1350, Lock IC=+0.0187, Sharpe=+0.2741

### 500ETF — `single` (121 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 120 | 50 | 0 | 50 | 0 | 0% | 100% |
| recency_ratio >= 2.5 (late-concentrated) | 1 | 1 | 0 | 0 | 1 | 0% | 0% |

### 159915ETF — `single` (35 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 33 | 33 | 11 | 17 | 5 | 33% | 52% |
| recency_ratio >= 2.5 (late-concentrated) | 2 | 2 | 0 | 2 | 0 | 0% | 100% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__max_up_ret__directional_volume_signature`: Train IC=+0.1514, Lock IC=+0.0867, Sharpe=+1.2162
- `combo_ratio__max_up_ret__directional_volume_signature`: Train IC=+0.0846, Lock IC=+0.0603, Sharpe=+0.5381

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 159915ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is higher (d=+1.29). Threshold 1.292 → 91% accuracy.
- `half_ratio`: FP is higher (d=+1.03). Threshold 5.756 → 91% accuracy.
- `n_negative_years`: FP is higher (d=+0.70). Threshold 1.500 → 91% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-0.61). Threshold 0.076 → 73% accuracy.
- `n_negative_regimes`: FP is higher (d=+0.60). Threshold 0.500 → 73% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 1/2
- Decaying signal (half ratio < 0.3): 0/2
- Weak component (CV > 2.0): 0/2
- Regime-dependent (≥2 negative regimes): 0/2

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | 1 | 7 | 8 | 12% |  |
| `max_down_ret` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 2 | 2 | 0% |  |
| `star50_limit_proximity_early` | 0 | 5 | 5 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 4 | 4 | 0% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 5 | 5 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=7, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=0, FP rate=100%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=4, FP rate=0%

