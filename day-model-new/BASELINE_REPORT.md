# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `(none)`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **50ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **500ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **588000ETF**: Train `2020-11-01` → `2025-01-01` | Holdout OOS from `2025-01-01` | Lockbox from `2025-07-01`
- **159915ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._
_Note: Cost metrics incorporate 8 bps (0.0008) transaction cost per position state transition (realistic for liquid ETFs). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted | Clusters | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 300ETF | single | 1,797 | 558 | 348 | 125 | 119 | 110 | 90 | 90 | 26 | 26 | 8 | `[9, 6, 3, 2, 2, 2, 1, 1]` |
| 50ETF | single | 985 | 248 | 181 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 4,744 | 2,438 | 2,135 | 1,921 | 1,919 | 1,513 | 1,480 | 1,480 | 317 | 317 | 117 | `[15, 14, 12, 12, 11, 9, 8, 8, 7, 7, 7, 6, ... (117 clusters)]` |
| 588000ETF | single | 1,583 | 1,016 | 691 | 453 | 415 | 29 | 29 | 29 | 8 | 8 | 4 | `[4, 2, 1, 1]` |
| 159915ETF | single | 2,974 | 955 | 508 | 318 | 308 | 61 | 56 | 56 | 37 | 37 | 22 | `[3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ... (22 clusters)]` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 26 | 8 | `[9, 6, 3, 2, 2, 2, 1, 1]` | +0.1285 | [+0.0834, +0.1708] | +0.2428 | [+0.1110, +0.3465] | +0.9273 | 7.47% | 1.6274 | 5.88% | 1.2991 | 2.8222 | 6.38% |
| 500ETF | single | 317 | 117 | `[15, 14, 12, 12, 11, 9, 8, 8, 7, 7, 7, 6, ... (117 clusters)]` | +0.1961 | [+0.1522, +0.2388] | +0.3008 | [+0.2130, +0.3860] | +0.9758 | 8.77% | 1.7493 | 7.13% | 1.4375 | 2.6546 | 3.82% |
| 588000ETF | single | 8 | 4 | `[4, 2, 1, 1]` | +0.1340 | [+0.0694, +0.1933] | +0.3536 | [+0.2106, +0.4477] | +0.8061 | 7.82% | 2.2008 | 6.38% | 1.8279 | 3.7105 | 2.01% |
| 159915ETF | single | 37 | 22 | `[3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ... (22 clusters)]` | +0.1772 | [+0.1318, +0.2202] | +0.2986 | [+0.2055, +0.3771] | +0.8909 | 9.83% | 1.9305 | 8.22% | 1.6337 | 2.9785 | 4.88% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 26 | 8 | `[9, 6, 3, 2, 2, 2, 1, 1]` | +0.0716 | [+0.0038, +0.1330] | +0.1818 | [+0.0180, +0.3182] | +0.7212 | 4.33% | 1.1498 | 2.72% | 0.7315 | 1.4608 | 3.36% |
| 500ETF | single | 317 | 117 | `[15, 14, 12, 12, 11, 9, 8, 8, 7, 7, 7, 6, ... (117 clusters)]` | +0.1084 | [+0.0477, +0.1673] | +0.1474 | [+0.0161, +0.2600] | +0.9030 | 4.52% | 0.9963 | 3.01% | 0.6684 | 1.2423 | 4.81% |
| 588000ETF | single | 8 | 4 | `[4, 2, 1, 1]` | +0.0059* | [-0.0930, +0.0830] | -0.1255* | [-0.3423, +0.1175] | +0.4788 | -1.94% | -0.3988 | -3.41% | -0.6974 | -0.9470 | 8.84% |
| 159915ETF | single | 37 | 22 | `[3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ... (22 clusters)]` | +0.1301 | [+0.0658, +0.1841] | +0.2396 | [+0.0773, +0.3503] | +0.6606 | 8.35% | 1.4779 | 6.90% | 1.2341 | 3.4091 | 4.26% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 26 | 8 | `[9, 6, 3, 2, 2, 2, 1, 1]` | +0.0297* | [-0.0664, +0.1232] | +0.1001* | [-0.1408, +0.3102] | +0.6121 | 3.70% | 0.8321 | 2.11% | 0.4805 | 1.0478 | 4.36% |
| 500ETF | single | 317 | 117 | `[15, 14, 12, 12, 11, 9, 8, 8, 7, 7, 7, 6, ... (117 clusters)]` | +0.1094 | [+0.0203, +0.1903] | +0.0582* | [-0.1289, +0.2137] | +0.7697 | 3.62% | 0.8133 | 2.12% | 0.4784 | 0.9051 | 4.46% |
| 588000ETF | single | 8 | 4 | `[4, 2, 1, 1]` | -0.0125* | [-0.1129, +0.1013] | -0.1301* | [-0.3634, +0.1942] | +0.1152 | -1.88% | -0.3639 | -3.33% | -0.6403 | -0.8778 | 8.44% |
| 159915ETF | single | 37 | 22 | `[3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ... (22 clusters)]` | +0.1361 | [+0.0528, +0.2133] | +0.1973* | [-0.0270, +0.3766] | +0.6727 | 9.25% | 1.3154 | 7.74% | 1.1113 | 3.2881 | 5.43% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 1 | +1 | +0.1265 | +0.2758 | +0.2757 | 0.0000 | +0.8117 | +0.7949 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 0 | +1 | +0.1248 | +0.2737 | +0.2728 | 0.0000 | +0.7042 | +0.7205 | 0.864 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 0 | +1 | +0.1286 | +0.2705 | +0.2699 | 0.0000 | +0.7933 | +0.7636 | 0.944 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1189 | +0.2604 | +0.2599 | 0.0000 | +0.8145 | +0.7805 | 0.877 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1145 | +0.2525 | +0.2516 | 0.0000 | +0.6300 | +0.7005 | 0.710 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 3 | +1 | +0.1161 | +0.2489 | +0.2489 | 0.0000 | +0.4464 | +0.6692 | 0.902 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 0 | +1 | +0.1141 | +0.2341 | +0.2329 | 0.0000 | +0.5505 | +0.6621 | 0.927 |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1148 | +0.2309 | +0.2304 | 0.0000 | +0.7202 | +0.7528 | 0.949 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | Cluster 4 | +1 | +0.1224 | +0.2228 | +0.2223 | 0.0000 | +0.6798 | +0.7400 | 0.927 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 5 | +1 | +0.0938 | +0.2222 | +0.2224 | 0.0000 | +0.5848 | +0.7149 | 0.864 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 0 | +1 | +0.1114 | +0.2220 | +0.2212 | 0.0000 | +0.4951 | +0.7118 | 0.927 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Cluster 5 | +1 | +0.0757 | +0.2160 | +0.2161 | 0.0000 | +0.7970 | +0.7831 | 0.650 |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 5 | +1 | +0.0880 | +0.2130 | +0.2127 | 0.0000 | +0.4688 | +0.6687 | 0.920 |
| `rbreaker_sell_setup_proximity_early` | Cluster 6 | +1 | +0.0883 | +0.2089 | +0.2086 | 0.0000 | +0.5326 | +0.7333 | 0.830 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1170 | +0.2077 | +0.2074 | 0.0000 | +0.6116 | +0.7410 | 0.873 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | Cluster 2 | +1 | +0.1074 | +0.2044 | +0.2045 | 0.0000 | +0.5899 | +0.7174 | 0.868 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 7 | +1 | +0.0911 | +0.2037 | +0.2027 | 0.0000 | +0.6652 | +0.7487 | 0.736 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1092 | +0.2023 | +0.2012 | 0.0000 | +0.6132 | +0.7000 | 0.936 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__limit_down_proximity_early` | Cluster 0 | +1 | +0.1116 | +0.1956 | +0.1946 | 0.0000 | +0.5385 | +0.6579 | 0.949 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 5 | +1 | +0.0829 | +0.1921 | +0.1919 | 0.0000 | +0.7141 | +0.7805 | 0.876 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.0937 | +0.1905 | +0.1895 | 0.0000 | +0.5153 | +0.6805 | 0.873 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Cluster 5 | +1 | +0.0874 | +0.1900 | +0.1902 | 0.0000 | +0.6618 | +0.7287 | 0.923 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 2 | +1 | +0.1188 | +0.1883 | +0.1881 | 0.0000 | +0.6625 | +0.7272 | 0.928 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | Cluster 5 | +1 | +0.0810 | +0.1728 | +0.1729 | 0.0002 | +0.6839 | +0.7385 | 0.902 |
| `star50_limit_proximity_early` | Cluster 6 | +1 | +0.0853 | +0.1622 | +0.1616 | 0.0014 | +0.4487 | +0.6923 | 0.939 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 7 | +1 | +0.1007 | +0.1373 | +0.1371 | 0.0076 | +0.3652 | +0.6708 | 0.862 |

### 50ETF / single
No features admitted.

### 500ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 41 | +1 | +0.2007 | +0.3546 | +0.3533 | 0.0000 | +1.1952 | +0.8697 | 0.936 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 41 | +1 | +0.2033 | +0.3481 | +0.3467 | 0.0000 | +1.2154 | +0.8733 | 0.824 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 44 | +1 | +0.1922 | +0.3474 | +0.3463 | 0.0000 | +0.8109 | +0.7759 | 0.720 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Cluster 91 | +1 | +0.1789 | +0.3473 | +0.3462 | 0.0000 | +1.2814 | +0.8836 | 0.936 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1921 | +0.3455 | +0.3443 | 0.0000 | +0.9362 | +0.7949 | 0.899 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 43 | +1 | +0.2010 | +0.3449 | +0.3436 | 0.0000 | +0.9436 | +0.7964 | 0.000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 42 | +1 | +0.1865 | +0.3418 | +0.3405 | 0.0000 | +0.9491 | +0.8015 | 0.868 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 44 | +1 | +0.1912 | +0.3316 | +0.3305 | 0.0000 | +0.8902 | +0.8010 | 0.910 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 40 | +1 | +0.1957 | +0.3277 | +0.3266 | 0.0000 | +0.9772 | +0.8231 | 0.805 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 114 | +1 | +0.2042 | +0.3230 | +0.3224 | 0.0000 | +0.9566 | +0.8021 | 0.935 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 92 | +1 | +0.2054 | +0.3217 | +0.3210 | 0.0000 | +1.0252 | +0.8528 | 0.900 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 115 | +1 | +0.1971 | +0.3206 | +0.3200 | 0.0000 | +1.0352 | +0.8415 | 0.925 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 4 | +1 | +0.1871 | +0.3197 | +0.3192 | 0.0000 | +1.2054 | +0.8708 | 0.837 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 92 | +1 | +0.2170 | +0.3175 | +0.3169 | 0.0000 | +1.0677 | +0.8379 | 0.947 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | Cluster 65 | +1 | +0.1455 | +0.3173 | +0.3162 | 0.0000 | +0.7842 | +0.7738 | 0.943 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 40 | +1 | +0.1981 | +0.3161 | +0.3146 | 0.0000 | +0.7127 | +0.7364 | 0.923 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 87 | +1 | +0.1828 | +0.3158 | +0.3151 | 0.0000 | +1.0648 | +0.8538 | 0.890 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.2023 | +0.3131 | +0.3126 | 0.0000 | +0.9775 | +0.8179 | 0.924 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 65 | +1 | +0.1724 | +0.3110 | +0.3094 | 0.0000 | +0.9912 | +0.8267 | 0.945 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1913 | +0.3106 | +0.3098 | 0.0000 | +0.8568 | +0.8072 | 0.905 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1989 | +0.3099 | +0.3086 | 0.0000 | +0.8795 | +0.7790 | 0.870 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 111 | +1 | +0.1813 | +0.3089 | +0.3083 | 0.0000 | +1.0229 | +0.8354 | 0.926 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 40 | +1 | +0.1926 | +0.3079 | +0.3067 | 0.0000 | +0.9156 | +0.7785 | 0.871 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 25 | +1 | +0.1710 | +0.3074 | +0.3066 | 0.0000 | +0.7947 | +0.7923 | 0.894 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 111 | +1 | +0.1795 | +0.3070 | +0.3066 | 0.0000 | +1.0246 | +0.8364 | 0.870 |
| `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | Cluster 67 | +1 | +0.1638 | +0.3066 | +0.3054 | 0.0000 | +0.8740 | +0.7933 | 0.891 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 44 | +1 | +0.1906 | +0.3053 | +0.3044 | 0.0000 | +0.7865 | +0.7503 | 0.939 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 100 | +1 | +0.2051 | +0.3038 | +0.3025 | 0.0000 | +0.9152 | +0.7774 | 0.879 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | Cluster 28 | +1 | +0.1661 | +0.3012 | +0.3000 | 0.0000 | +0.6327 | +0.7241 | 0.935 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | Cluster 66 | +1 | +0.1668 | +0.2987 | +0.2975 | 0.0000 | +0.9927 | +0.8226 | 0.946 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 111 | +1 | +0.1773 | +0.2978 | +0.2971 | 0.0000 | +0.8942 | +0.7933 | 0.931 |
| `combo_tri_mean__opening_drive_thrust_ratio__early_body_momentum__star50_limit_proximity_early` | Cluster 2 | +1 | +0.1835 | +0.2971 | +0.2965 | 0.0000 | +1.0032 | +0.8277 | 0.909 |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | Cluster 97 | +1 | +0.1814 | +0.2947 | +0.2935 | 0.0000 | +0.7330 | +0.7621 | 0.853 |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 35 | +1 | +0.1334 | +0.2947 | +0.2943 | 0.0000 | +0.8541 | +0.7841 | 0.938 |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 37 | +1 | +0.1658 | +0.2939 | +0.2928 | 0.0000 | +0.9205 | +0.8221 | 0.926 |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | Cluster 69 | +1 | +0.1526 | +0.2926 | +0.2912 | 0.0000 | +0.7852 | +0.7646 | 0.950 |
| `combo_rank_min__max_up_ret__max_down_ret` | Cluster 101 | +1 | +0.1574 | +0.2923 | +0.2910 | 0.0000 | +0.7654 | +0.7779 | 0.854 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | Cluster 0 | +1 | +0.1935 | +0.2923 | +0.2918 | 0.0000 | +1.0598 | +0.8374 | 0.816 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Cluster 28 | +1 | +0.1650 | +0.2918 | +0.2906 | 0.0000 | +0.6309 | +0.7026 | 0.923 |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | Cluster 17 | +1 | +0.1517 | +0.2910 | +0.2905 | 0.0000 | +0.9940 | +0.8323 | 0.913 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.2024 | +0.2908 | +0.2902 | 0.0000 | +1.0004 | +0.8272 | 0.949 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 3 | +1 | +0.1885 | +0.2907 | +0.2903 | 0.0000 | +0.9551 | +0.8128 | 0.931 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 28 | +1 | +0.1942 | +0.2898 | +0.2888 | 0.0000 | +0.9092 | +0.7995 | 0.892 |
| `opening_drive_thrust_ratio` | Cluster 111 | +1 | +0.1812 | +0.2887 | +0.2875 | 0.0000 | +0.8354 | +0.8185 | 0.791 |
| `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum` | Cluster 44 | +1 | +0.1584 | +0.2885 | +0.2880 | 0.0000 | +0.7854 | +0.7790 | 0.900 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Cluster 110 | +1 | +0.1783 | +0.2881 | +0.2870 | 0.0000 | +0.7801 | +0.7749 | 0.875 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 69 | +1 | +0.1592 | +0.2877 | +0.2858 | 0.0000 | +0.7306 | +0.7349 | 0.914 |
| `combo_tri_mean__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early` | Cluster 2 | +1 | +0.1489 | +0.2874 | +0.2871 | 0.0000 | +0.7436 | +0.7523 | 0.949 |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 19 | +1 | +0.1369 | +0.2870 | +0.2870 | 0.0000 | +0.8923 | +0.7969 | 0.855 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Cluster 1 | +1 | +0.1910 | +0.2866 | +0.2858 | 0.0000 | +0.7436 | +0.7662 | 0.936 |
| `combo_tri_median__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | Cluster 91 | +1 | +0.1704 | +0.2862 | +0.2850 | 0.0000 | +0.8257 | +0.7892 | 0.948 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 100 | +1 | +0.1966 | +0.2853 | +0.2842 | 0.0000 | +0.8144 | +0.7421 | 0.915 |
| `combo_rank_max__max_down_ret__bar_body_rng_0` | Cluster 45 | +1 | +0.1631 | +0.2847 | +0.2832 | 0.0000 | +0.7272 | +0.7451 | 0.889 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 71 | +1 | +0.1533 | +0.2845 | +0.2830 | 0.0000 | +0.8130 | +0.7538 | 0.940 |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 111 | +1 | +0.1830 | +0.2837 | +0.2826 | 0.0000 | +0.7376 | +0.7446 | 0.925 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 12 | +1 | +0.1582 | +0.2836 | +0.2835 | 0.0000 | +0.8622 | +0.7610 | 0.936 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | Cluster 30 | +1 | +0.1739 | +0.2836 | +0.2832 | 0.0000 | +0.8484 | +0.8144 | 0.946 |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | Cluster 64 | +1 | +0.1208 | +0.2831 | +0.2820 | 0.0000 | +0.7155 | +0.7513 | 0.948 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Cluster 0 | +1 | +0.1794 | +0.2819 | +0.2817 | 0.0000 | +0.8429 | +0.7836 | 0.929 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Cluster 97 | +1 | +0.1829 | +0.2817 | +0.2806 | 0.0000 | +0.6706 | +0.7436 | 0.934 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 3 | +1 | +0.1758 | +0.2814 | +0.2803 | 0.0000 | +0.8087 | +0.7964 | 0.947 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Cluster 97 | +1 | +0.1819 | +0.2814 | +0.2801 | 0.0000 | +0.6513 | +0.7379 | 0.947 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 87 | +1 | +0.1616 | +0.2812 | +0.2809 | 0.0000 | +0.8123 | +0.7790 | 0.944 |
| `combo_tri_median__max_up_ret__early_body_momentum__star50_limit_proximity_early` | Cluster 3 | +1 | +0.1650 | +0.2811 | +0.2803 | 0.0000 | +0.6835 | +0.7549 | 0.897 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 111 | +1 | +0.1811 | +0.2810 | +0.2804 | 0.0000 | +0.9099 | +0.7744 | 0.937 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 42 | +1 | +0.1956 | +0.2808 | +0.2796 | 0.0000 | +0.8376 | +0.7795 | 0.924 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 98 | +1 | +0.1905 | +0.2806 | +0.2797 | 0.0000 | +0.7756 | +0.7892 | 0.922 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Cluster 0 | +1 | +0.1778 | +0.2800 | +0.2799 | 0.0000 | +0.8882 | +0.7621 | 0.884 |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 19 | +1 | +0.1371 | +0.2797 | +0.2794 | 0.0000 | +0.8429 | +0.7938 | 0.904 |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 19 | +1 | +0.1364 | +0.2790 | +0.2786 | 0.0000 | +0.7474 | +0.7621 | 0.939 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 88 | +1 | +0.1829 | +0.2789 | +0.2777 | 0.0000 | +0.6882 | +0.7277 | 0.794 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | Cluster 98 | +1 | +0.1815 | +0.2788 | +0.2785 | 0.0000 | +0.7784 | +0.7810 | 0.906 |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | Cluster 104 | +1 | +0.1703 | +0.2778 | +0.2772 | 0.0000 | +0.8427 | +0.7549 | 0.880 |
| `combo_mean__net_volume_flow__bar_body_rng_0` | Cluster 46 | +1 | +0.1554 | +0.2776 | +0.2767 | 0.0000 | +0.7495 | +0.7969 | 0.909 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 93 | +1 | +0.1976 | +0.2775 | +0.2765 | 0.0000 | +1.1047 | +0.8477 | 0.938 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 21 | +1 | +0.1394 | +0.2765 | +0.2756 | 0.0000 | +0.7131 | +0.7672 | 0.901 |
| `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 71 | +1 | +0.1389 | +0.2765 | +0.2750 | 0.0000 | +0.7851 | +0.7405 | 0.871 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | Cluster 29 | +1 | +0.1712 | +0.2765 | +0.2756 | 0.0000 | +1.0521 | +0.8554 | 0.922 |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Cluster 71 | +1 | +0.1531 | +0.2759 | +0.2744 | 0.0000 | +0.8689 | +0.7877 | 0.927 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 93 | +1 | +0.1890 | +0.2756 | +0.2745 | 0.0000 | +0.8504 | +0.7805 | 0.919 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Cluster 71 | +1 | +0.1527 | +0.2755 | +0.2740 | 0.0000 | +0.8914 | +0.7682 | 0.946 |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | Cluster 0 | +1 | +0.1738 | +0.2752 | +0.2753 | 0.0000 | +1.0096 | +0.7949 | 0.709 |
| `combo_rank_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 31 | +1 | +0.1472 | +0.2750 | +0.2740 | 0.0000 | +0.7965 | +0.7826 | 0.948 |
| `rbreaker_sell_setup_proximity_early` | Cluster 63 | +1 | +0.1701 | +0.2746 | +0.2737 | 0.0000 | +0.7525 | +0.7636 | 0.872 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | Cluster 58 | +1 | +0.1623 | +0.2746 | +0.2739 | 0.0000 | +0.7230 | +0.7600 | 0.948 |
| `combo_clamp_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | Cluster 36 | +1 | +0.1511 | +0.2746 | +0.2741 | 0.0000 | +0.6611 | +0.7318 | 0.931 |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | Cluster 61 | +1 | +0.1543 | +0.2743 | +0.2733 | 0.0000 | +0.7001 | +0.7662 | 0.901 |
| `combo_rel_diff__star50_limit_proximity_early__late_bar_momentum` | Cluster 44 | +1 | +0.1559 | +0.2742 | +0.2739 | 0.0000 | +0.6800 | +0.7349 | 0.931 |
| `combo_min__trend_bar_close_consistency__star50_limit_proximity_early` | Cluster 64 | +1 | +0.1114 | +0.2735 | +0.2727 | 0.0000 | +0.6630 | +0.7108 | 0.930 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 102 | +1 | +0.1427 | +0.2731 | +0.2716 | 0.0000 | +0.8616 | +0.7974 | 0.812 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 1 | +1 | +0.1897 | +0.2730 | +0.2723 | 0.0000 | +0.8458 | +0.7800 | 0.857 |
| `combo_tri_max__max_up_ret__volatility_expansion_trend_vector__early_body_momentum` | Cluster 14 | +1 | +0.1608 | +0.2729 | +0.2720 | 0.0000 | +0.9985 | +0.8349 | 0.947 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | Cluster 93 | +1 | +0.1873 | +0.2723 | +0.2713 | 0.0000 | +0.8685 | +0.7964 | 0.934 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | Cluster 72 | +1 | +0.1645 | +0.2721 | +0.2717 | 0.0000 | +0.8101 | +0.7492 | 0.948 |
| `combo_rank_max__max_up_ret__net_volume_flow` | Cluster 14 | +1 | +0.1670 | +0.2716 | +0.2705 | 0.0000 | +0.9339 | +0.8287 | 0.909 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Cluster 44 | +1 | +0.1601 | +0.2714 | +0.2709 | 0.0000 | +0.6792 | +0.7359 | 0.776 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 99 | +1 | +0.1831 | +0.2703 | +0.2694 | 0.0000 | +0.6392 | +0.7277 | 0.930 |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | Cluster 32 | +1 | +0.1543 | +0.2695 | +0.2688 | 0.0000 | +0.7846 | +0.7851 | 0.945 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 102 | +1 | +0.1409 | +0.2683 | +0.2667 | 0.0000 | +0.8145 | +0.7754 | 0.769 |
| `combo_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Cluster 102 | +1 | +0.1702 | +0.2680 | +0.2673 | 0.0000 | +0.7784 | +0.7446 | 0.886 |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | Cluster 111 | +1 | +0.1769 | +0.2679 | +0.2674 | 0.0000 | +0.8838 | +0.8462 | 0.937 |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Cluster 54 | +1 | +0.1548 | +0.2677 | +0.2670 | 0.0000 | +0.8339 | +0.7738 | 0.942 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 93 | +1 | +0.1958 | +0.2675 | +0.2664 | 0.0000 | +0.8314 | +0.8118 | 0.912 |
| `max_up_ret` | Cluster 92 | +1 | +0.1728 | +0.2674 | +0.2663 | 0.0000 | +0.8154 | +0.7979 | 0.916 |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 70 | +1 | +0.1316 | +0.2673 | +0.2672 | 0.0000 | +0.7174 | +0.7713 | 0.926 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 0 | +1 | +0.1671 | +0.2672 | +0.2666 | 0.0000 | +0.6984 | +0.7492 | 0.888 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Cluster 67 | +1 | +0.1556 | +0.2670 | +0.2661 | 0.0000 | +0.8821 | +0.7764 | 0.947 |
| `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Cluster 29 | +1 | +0.1548 | +0.2670 | +0.2665 | 0.0000 | +0.8187 | +0.7985 | 0.944 |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | Cluster 103 | +1 | +0.1622 | +0.2665 | +0.2655 | 0.0000 | +0.7411 | +0.7728 | 0.920 |
| `combo_min__bar_ret_0__bar_body_rng_0` | Cluster 45 | +1 | +0.1569 | +0.2664 | +0.2656 | 0.0000 | +0.7032 | +0.7179 | 0.777 |
| `combo_tri_median__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | Cluster 98 | +1 | +0.1687 | +0.2656 | +0.2649 | 0.0000 | +0.8653 | +0.7590 | 0.942 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 112 | +1 | +0.1887 | +0.2652 | +0.2644 | 0.0000 | +0.7041 | +0.7400 | 0.944 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Cluster 53 | +1 | +0.1196 | +0.2651 | +0.2642 | 0.0000 | +0.6903 | +0.7164 | 0.943 |
| `combo_max__max_up_ret__max_down_ret` | Cluster 90 | +1 | +0.1776 | +0.2650 | +0.2644 | 0.0000 | +0.9238 | +0.8108 | 0.855 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 59 | +1 | +0.1527 | +0.2643 | +0.2635 | 0.0000 | +0.8273 | +0.7887 | 0.869 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 29 | +1 | +0.1700 | +0.2638 | +0.2624 | 0.0000 | +0.8614 | +0.7979 | 0.933 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Cluster 102 | +1 | +0.1732 | +0.2636 | +0.2629 | 0.0000 | +0.7531 | +0.7385 | 0.872 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Cluster 73 | +1 | +0.1273 | +0.2630 | +0.2623 | 0.0000 | +0.8738 | +0.7867 | 0.893 |
| `combo_mean__max_up_ret__first_bar_return` | Cluster 106 | +1 | +0.1802 | +0.2625 | +0.2615 | 0.0000 | +0.7995 | +0.7708 | 0.929 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Cluster 86 | +1 | +0.1553 | +0.2623 | +0.2619 | 0.0000 | +0.6908 | +0.7569 | 0.791 |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 102 | +1 | +0.1166 | +0.2613 | +0.2603 | 0.0000 | +0.6697 | +0.7272 | 0.945 |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | Cluster 20 | +1 | +0.1634 | +0.2607 | +0.2605 | 0.0000 | +0.9027 | +0.8354 | 0.937 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Cluster 0 | +1 | +0.1765 | +0.2607 | +0.2605 | 0.0000 | +1.0283 | +0.7903 | 0.931 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 86 | +1 | +0.1463 | +0.2604 | +0.2597 | 0.0000 | +0.7890 | +0.7713 | 0.752 |
| `combo_rank_max__max_up_ret__max_down_ret` | Cluster 90 | +1 | +0.1799 | +0.2602 | +0.2591 | 0.0000 | +0.9524 | +0.8262 | 0.906 |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | Cluster 26 | +1 | +0.1593 | +0.2592 | +0.2584 | 0.0000 | +0.9651 | +0.8462 | 0.947 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Cluster 111 | +1 | +0.1928 | +0.2585 | +0.2573 | 0.0000 | +0.7416 | +0.7313 | 0.905 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 37 | +1 | +0.1651 | +0.2584 | +0.2572 | 0.0000 | +0.8468 | +0.8000 | 0.939 |
| `combo_min__max_up_ret__net_volume_flow` | Cluster 22 | +1 | +0.1506 | +0.2578 | +0.2572 | 0.0000 | +0.8845 | +0.7954 | 0.937 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 111 | +1 | +0.1840 | +0.2574 | +0.2559 | 0.0000 | +0.7858 | +0.7954 | 0.943 |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Cluster 72 | +1 | +0.1702 | +0.2574 | +0.2568 | 0.0000 | +0.8514 | +0.7697 | 0.891 |
| `combo_max__trend_bar_close_consistency__bar_body_rng_0` | Cluster 103 | +1 | +0.1462 | +0.2568 | +0.2563 | 0.0000 | +0.7114 | +0.8113 | 0.941 |
| `combo_max__max_up_ret__close_vs_open_range` | Cluster 14 | +1 | +0.1705 | +0.2563 | +0.2555 | 0.0000 | +0.9275 | +0.7841 | 0.876 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 106 | +1 | +0.1710 | +0.2561 | +0.2555 | 0.0000 | +0.8715 | +0.7995 | 0.948 |
| `combo_rel_diff__early_body_momentum__h2_l2_pullback_continuation` | Cluster 74 | +1 | +0.0939 | +0.2558 | +0.2559 | 0.0000 | +0.5088 | +0.7056 | 0.930 |
| `combo_rank_min__trend_bar_close_consistency__close_vs_open_range` | Cluster 83 | +1 | +0.1017 | +0.2557 | +0.2556 | 0.0000 | +0.6670 | +0.7662 | 0.938 |
| `combo_min__net_volume_flow__first_bar_return` | Cluster 53 | +1 | +0.1386 | +0.2548 | +0.2539 | 0.0000 | +0.7716 | +0.7626 | 0.943 |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Cluster 73 | +1 | +0.1190 | +0.2539 | +0.2534 | 0.0000 | +0.7931 | +0.7749 | 0.904 |
| `combo_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Cluster 29 | +1 | +0.1662 | +0.2538 | +0.2530 | 0.0000 | +0.8099 | +0.7985 | 0.922 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 86 | +1 | +0.1455 | +0.2531 | +0.2526 | 0.0000 | +0.6267 | +0.7128 | 0.912 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Cluster 85 | +1 | +0.1481 | +0.2529 | +0.2523 | 0.0000 | +0.9486 | +0.8262 | 0.307 |
| `combo_rank_min__bar_ret_0__close_vs_open_range` | Cluster 49 | +1 | +0.1324 | +0.2527 | +0.2517 | 0.0000 | +0.8245 | +0.7621 | 0.841 |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | Cluster 68 | +1 | +0.1211 | +0.2521 | +0.2509 | 0.0000 | +0.7054 | +0.7308 | 0.886 |
| `combo_max__max_up_ret__early_order_flow_imbalance` | Cluster 18 | +1 | +0.1460 | +0.2521 | +0.2518 | 0.0000 | +0.9086 | +0.8092 | 0.945 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1610 | +0.2520 | +0.2515 | 0.0000 | +0.6130 | +0.7174 | 0.889 |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | Cluster 86 | +1 | +0.1518 | +0.2518 | +0.2520 | 0.0000 | +0.7338 | +0.7354 | 0.788 |
| `combo_clamp_diff__net_volume_flow__demark_setup_reversal_early` | Cluster 2 | +1 | +0.1552 | +0.2516 | +0.2510 | 0.0000 | +0.4422 | +0.6590 | 0.910 |
| `combo_mean__first_bar_return__rsi_opening` | Cluster 51 | +1 | +0.1515 | +0.2514 | +0.2503 | 0.0000 | +0.6106 | +0.7118 | 0.938 |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | Cluster 47 | +1 | +0.1460 | +0.2511 | +0.2504 | 0.0000 | +0.6548 | +0.7410 | 0.946 |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | Cluster 47 | +1 | +0.1364 | +0.2507 | +0.2504 | 0.0000 | +0.6382 | +0.7256 | 0.733 |
| `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 11 | +1 | +0.1667 | +0.2497 | +0.2498 | 0.0000 | +0.8810 | +0.7836 | 0.904 |
| `combo_min__bar_ret_0__close_vs_open_range` | Cluster 49 | +1 | +0.1320 | +0.2497 | +0.2486 | 0.0000 | +0.8546 | +0.7913 | 0.908 |
| `combo_clamp_diff__first_bar_return__late_bar_momentum` | Cluster 0 | +1 | +0.1672 | +0.2486 | +0.2483 | 0.0000 | +0.6190 | +0.7210 | 0.880 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 7 | +1 | +0.1579 | +0.2485 | +0.2485 | 0.0000 | +0.5623 | +0.7154 | 0.827 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 111 | +1 | +0.1706 | +0.2472 | +0.2463 | 0.0000 | +0.7644 | +0.7744 | 0.947 |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | Cluster 20 | +1 | +0.1675 | +0.2469 | +0.2465 | 0.0000 | +0.9725 | +0.8318 | 0.913 |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Cluster 60 | +1 | +0.1647 | +0.2469 | +0.2463 | 0.0000 | +0.7021 | +0.7595 | 0.892 |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | Cluster 94 | +1 | +0.1841 | +0.2464 | +0.2454 | 0.0000 | +0.8252 | +0.7918 | 0.938 |
| `combo_min__close_vs_open_range__bar_body_rng_0` | Cluster 56 | +1 | +0.1396 | +0.2463 | +0.2452 | 0.0000 | +0.7275 | +0.7872 | 0.903 |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | Cluster 39 | +1 | +0.1306 | +0.2462 | +0.2455 | 0.0000 | +0.6771 | +0.7513 | 0.831 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 31 | +1 | +0.1506 | +0.2460 | +0.2451 | 0.0000 | +0.7870 | +0.8062 | 0.932 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 0 | +1 | +0.1665 | +0.2458 | +0.2451 | 0.0000 | +0.6024 | +0.7287 | 0.934 |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | Cluster 68 | +1 | +0.1263 | +0.2457 | +0.2444 | 0.0000 | +0.7786 | +0.7523 | 0.933 |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | Cluster 54 | +1 | +0.1458 | +0.2437 | +0.2425 | 0.0000 | +0.7822 | +0.7631 | 0.871 |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | Cluster 39 | +1 | +0.1238 | +0.2434 | +0.2427 | 0.0000 | +0.6827 | +0.7385 | 0.778 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 96 | +1 | +0.1829 | +0.2433 | +0.2422 | 0.0000 | +0.7550 | +0.7728 | 0.918 |
| `combo_mean__max_up_ret__max_down_ret` | Cluster 89 | +1 | +0.1715 | +0.2430 | +0.2419 | 0.0000 | +0.8193 | +0.7856 | 0.852 |
| `combo_mean__max_up_ret__close_vs_open_range` | Cluster 26 | +1 | +0.1575 | +0.2429 | +0.2418 | 0.0000 | +0.9525 | +0.8174 | 0.938 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 96 | +1 | +0.1821 | +0.2426 | +0.2414 | 0.0000 | +0.7611 | +0.7851 | 0.854 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 68 | +1 | +0.1452 | +0.2425 | +0.2415 | 0.0000 | +0.8393 | +0.7692 | 0.947 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 111 | +1 | +0.1663 | +0.2425 | +0.2416 | 0.0000 | +0.6095 | +0.7692 | 0.888 |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | Cluster 18 | +1 | +0.1523 | +0.2424 | +0.2422 | 0.0000 | +0.8455 | +0.7964 | 0.927 |
| `combo_mean__bar_ret_0__max_down_ret` | Cluster 45 | +1 | +0.1550 | +0.2422 | +0.2413 | 0.0000 | +0.6026 | +0.6585 | 0.885 |
| `combo_diff__star50_limit_proximity_early__late_bar_momentum` | Cluster 44 | +1 | +0.1571 | +0.2421 | +0.2417 | 0.0000 | +0.6314 | +0.7210 | 0.937 |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | Cluster 88 | +1 | +0.1651 | +0.2420 | +0.2411 | 0.0000 | +0.6382 | +0.7477 | 0.941 |
| `combo_mean__net_volume_flow__close_vs_open_range` | Cluster 38 | +1 | +0.1259 | +0.2417 | +0.2409 | 0.0000 | +0.7365 | +0.7692 | 0.947 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 112 | +1 | +0.1828 | +0.2416 | +0.2406 | 0.0000 | +0.5912 | +0.7092 | 0.864 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Cluster 104 | +1 | +0.1609 | +0.2412 | +0.2405 | 0.0000 | +0.8523 | +0.7923 | 0.859 |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | Cluster 8 | +1 | +0.1644 | +0.2411 | +0.2410 | 0.0000 | +0.6930 | +0.7595 | 0.904 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 102 | +1 | +0.1471 | +0.2407 | +0.2396 | 0.0000 | +0.6484 | +0.7328 | 0.934 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 113 | +1 | +0.1771 | +0.2406 | +0.2399 | 0.0000 | +0.6879 | +0.7400 | 0.906 |
| `combo_clamp_diff__first_bar_return__h2_l2_pullback_continuation` | Cluster 57 | +1 | +0.1423 | +0.2403 | +0.2396 | 0.0000 | +0.6615 | +0.7333 | 0.914 |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | Cluster 86 | +1 | +0.1409 | +0.2403 | +0.2396 | 0.0000 | +0.7120 | +0.7482 | 0.880 |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | Cluster 16 | +1 | +0.1393 | +0.2400 | +0.2393 | 0.0000 | +0.7415 | +0.7646 | 0.949 |
| `combo_min__max_up_ret__early_order_flow_imbalance` | Cluster 23 | +1 | +0.1417 | +0.2397 | +0.2389 | 0.0000 | +0.7663 | +0.7626 | 0.911 |
| `combo_rank_min__volatility_expansion_trend_vector__early_order_flow_imbalance` | Cluster 80 | +1 | +0.1115 | +0.2388 | +0.2387 | 0.0000 | +0.6832 | +0.7544 | 0.894 |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | Cluster 45 | +1 | +0.1293 | +0.2377 | +0.2367 | 0.0000 | +0.7661 | +0.7549 | 0.872 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Cluster 102 | +1 | +0.1682 | +0.2367 | +0.2359 | 0.0000 | +0.6124 | +0.7174 | 0.945 |
| `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Cluster 59 | +1 | +0.1527 | +0.2367 | +0.2355 | 0.0000 | +0.7366 | +0.7631 | 0.862 |
| `combo_min__max_up_ret__first_bar_return` | Cluster 110 | +1 | +0.1782 | +0.2359 | +0.2347 | 0.0000 | +0.5691 | +0.7036 | 0.922 |
| `combo_min__max_up_ret__close_vs_open_range` | Cluster 21 | +1 | +0.1333 | +0.2358 | +0.2349 | 0.0000 | +0.7209 | +0.7697 | 0.876 |
| `combo_rel_diff__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Cluster 62 | +1 | +0.0989 | +0.2356 | +0.2342 | 0.0000 | +0.6227 | +0.7190 | 0.705 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 112 | +1 | +0.1904 | +0.2354 | +0.2345 | 0.0000 | +0.7085 | +0.7626 | 0.918 |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Cluster 27 | +1 | +0.1570 | +0.2351 | +0.2348 | 0.0000 | +0.7450 | +0.7415 | 0.949 |
| `combo_max__first_bar_return__close_vs_open_range` | Cluster 104 | +1 | +0.1670 | +0.2347 | +0.2335 | 0.0000 | +0.8259 | +0.7959 | 0.783 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | Cluster 27 | +1 | +0.1603 | +0.2344 | +0.2341 | 0.0000 | +0.7465 | +0.7421 | 0.899 |
| `combo_max__rsi_opening__early_order_flow_imbalance` | Cluster 79 | +1 | +0.1065 | +0.2342 | +0.2335 | 0.0000 | +0.5723 | +0.7462 | 0.922 |
| `combo_max__early_body_momentum__close_vs_open_range` | Cluster 82 | +1 | +0.1101 | +0.2336 | +0.2326 | 0.0000 | +0.6831 | +0.7718 | 0.851 |
| `combo_max__net_volume_flow__first_bar_return` | Cluster 104 | +1 | +0.1628 | +0.2333 | +0.2324 | 0.0000 | +0.7205 | +0.7615 | 0.918 |
| `combo_min__max_up_ret__max_down_ret` | Cluster 95 | +1 | +0.1592 | +0.2330 | +0.2318 | 0.0000 | +0.6119 | +0.7041 | 0.919 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 112 | +1 | +0.1851 | +0.2330 | +0.2321 | 0.0000 | +0.5964 | +0.7092 | 0.894 |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 55 | +1 | +0.1543 | +0.2330 | +0.2324 | 0.0000 | +0.6378 | +0.7005 | 0.917 |
| `combo_min__early_order_flow_imbalance__max_down_ret` | Cluster 39 | +1 | +0.1201 | +0.2320 | +0.2318 | 0.0000 | +0.7262 | +0.7456 | 0.905 |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | Cluster 46 | +1 | +0.1532 | +0.2320 | +0.2306 | 0.0000 | +0.7622 | +0.7703 | 0.918 |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | Cluster 57 | +1 | +0.1424 | +0.2309 | +0.2301 | 0.0000 | +0.6925 | +0.7169 | 0.947 |
| `combo_mean__volatility_expansion_trend_vector__shaved_bar_trend_conviction` | Cluster 84 | +1 | +0.1127 | +0.2307 | +0.2304 | 0.0000 | +0.6273 | +0.7256 | 0.941 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Cluster 63 | +1 | +0.1536 | +0.2303 | +0.2288 | 0.0000 | +0.4253 | +0.6821 | 0.648 |
| `combo_rank_max__net_volume_flow__max_down_ret` | Cluster 38 | +1 | +0.1484 | +0.2301 | +0.2292 | 0.0000 | +0.6751 | +0.7313 | 0.935 |
| `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | Cluster 76 | +1 | +0.1117 | +0.2298 | +0.2292 | 0.0000 | +0.5888 | +0.7205 | 0.908 |
| `combo_max__bar_ret_0__max_down_ret` | Cluster 45 | +1 | +0.1659 | +0.2297 | +0.2282 | 0.0000 | +0.6435 | +0.7185 | 0.905 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 111 | +1 | +0.1596 | +0.2296 | +0.2284 | 0.0000 | +0.6546 | +0.7487 | 0.888 |
| `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__trend_day_regime_conviction` | Cluster 34 | +1 | +0.1294 | +0.2293 | +0.2286 | 0.0000 | +0.6329 | +0.7487 | 0.936 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 112 | +1 | +0.1831 | +0.2291 | +0.2278 | 0.0000 | +0.6641 | +0.7333 | 0.917 |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1578 | +0.2287 | +0.2278 | 0.0000 | +0.5926 | +0.7138 | 0.946 |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | Cluster 80 | +1 | +0.1082 | +0.2285 | +0.2283 | 0.0000 | +0.7906 | +0.8123 | 0.912 |
| `combo_rank_min__max_up_ret__vwap_close_divergence_trend` | Cluster 24 | +1 | +0.1218 | +0.2280 | +0.2270 | 0.0000 | +0.6538 | +0.7579 | 0.946 |
| `combo_max__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 109 | +1 | +0.1498 | +0.2275 | +0.2272 | 0.0000 | +0.6841 | +0.7072 | 0.914 |
| `combo_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 7 | +1 | +0.1466 | +0.2269 | +0.2276 | 0.0000 | +0.5543 | +0.6831 | 0.867 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Cluster 86 | +1 | +0.1403 | +0.2268 | +0.2265 | 0.0000 | +0.7668 | +0.7554 | 0.767 |
| `combo_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 111 | +1 | +0.1863 | +0.2268 | +0.2252 | 0.0000 | +0.6419 | +0.7718 | 0.929 |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | Cluster 108 | +1 | +0.1384 | +0.2261 | +0.2254 | 0.0000 | +0.6820 | +0.7251 | 0.919 |
| `combo_min__rsi_opening__close_vs_open_range` | Cluster 83 | +1 | +0.1178 | +0.2259 | +0.2253 | 0.0000 | +0.6288 | +0.7333 | 0.933 |
| `combo_mean__bar_ret_0__close_vs_open_range` | Cluster 51 | +1 | +0.1589 | +0.2257 | +0.2242 | 0.0000 | +0.7633 | +0.7918 | 0.869 |
| `combo_mean__first_bar_return__vwap_close_divergence_trend` | Cluster 55 | +1 | +0.1548 | +0.2252 | +0.2243 | 0.0000 | +0.5797 | +0.6836 | 0.919 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Cluster 0 | +1 | +0.1582 | +0.2249 | +0.2245 | 0.0000 | +0.6689 | +0.7210 | 0.923 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 113 | +1 | +0.1634 | +0.2238 | +0.2231 | 0.0000 | +0.7558 | +0.7354 | 0.824 |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | Cluster 77 | +1 | +0.1170 | +0.2231 | +0.2229 | 0.0000 | +0.6501 | +0.7436 | 0.918 |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 48 | +1 | +0.1375 | +0.2230 | +0.2223 | 0.0000 | +0.6249 | +0.6979 | 0.939 |
| `star50_limit_proximity_early` | Cluster 102 | +1 | +0.1441 | +0.2228 | +0.2216 | 0.0000 | +0.7001 | +0.7467 | 0.916 |
| `combo_mean__bar_ret_0__shaved_bar_trend_conviction` | Cluster 50 | +1 | +0.1456 | +0.2227 | +0.2220 | 0.0000 | +0.5906 | +0.6841 | 0.919 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 115 | +1 | +0.1684 | +0.2222 | +0.2214 | 0.0000 | +0.7796 | +0.7672 | 0.843 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 59 | +1 | +0.1651 | +0.2214 | +0.2206 | 0.0000 | +0.5982 | +0.7226 | 0.850 |
| `combo_ratio__max_down_ret__net_volume_flow` | Cluster 85 | +1 | +0.1330 | +0.2207 | +0.2209 | 0.0000 | +0.8220 | +0.7738 | 0.103 |
| `combo_sig_product__max_up_ret__first_bar_return` | Cluster 86 | +1 | +0.1587 | +0.2196 | +0.2192 | 0.0000 | +0.6795 | +0.7492 | 0.793 |
| `combo_mean__net_volume_flow__max_down_ret` | Cluster 38 | +1 | +0.1416 | +0.2194 | +0.2187 | 0.0000 | +0.6620 | +0.7415 | 0.902 |
| `combo_min__first_bar_return__max_down_ret` | Cluster 45 | +1 | +0.1467 | +0.2194 | +0.2189 | 0.0000 | +0.6090 | +0.7010 | 0.940 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 59 | +1 | +0.1463 | +0.2192 | +0.2187 | 0.0000 | +0.8303 | +0.7903 | 0.847 |
| `combo_min__max_down_ret__bar_body_rng_0` | Cluster 45 | +1 | +0.1501 | +0.2192 | +0.2185 | 0.0000 | +0.6253 | +0.7010 | 0.941 |
| `combo_max__star50_limit_proximity_early__first_bar_return` | Cluster 28 | +1 | +0.1643 | +0.2190 | +0.2179 | 0.0000 | +0.7720 | +0.7359 | 0.881 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 12 | +1 | +0.1288 | +0.2189 | +0.2186 | 0.0000 | +0.5917 | +0.6954 | 0.909 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 102 | +1 | +0.1520 | +0.2188 | +0.2179 | 0.0000 | +0.5946 | +0.7036 | 0.811 |
| `combo_rank_min__early_body_momentum__max_down_ret` | Cluster 39 | +1 | +0.1249 | +0.2185 | +0.2177 | 0.0000 | +0.5913 | +0.7005 | 0.946 |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | Cluster 39 | +1 | +0.1240 | +0.2183 | +0.2180 | 0.0000 | +0.7181 | +0.7738 | 0.878 |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Cluster 74 | +1 | +0.1097 | +0.2182 | +0.2181 | 0.0000 | +0.5815 | +0.7226 | 0.878 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 111 | +1 | +0.1729 | +0.2181 | +0.2170 | 0.0000 | +0.6978 | +0.7785 | 0.921 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Cluster 102 | +1 | +0.1504 | +0.2174 | +0.2160 | 0.0000 | +0.5547 | +0.6764 | 0.847 |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Cluster 74 | +1 | +0.1089 | +0.2172 | +0.2169 | 0.0000 | +0.5797 | +0.7272 | 0.934 |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | Cluster 52 | +1 | +0.1336 | +0.2165 | +0.2155 | 0.0000 | +0.6579 | +0.7436 | 0.882 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1575 | +0.2165 | +0.2161 | 0.0000 | +0.5362 | +0.6800 | 0.924 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | Cluster 116 | +1 | +0.1642 | +0.2152 | +0.2147 | 0.0000 | +0.6348 | +0.7292 | 0.929 |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | Cluster 24 | +1 | +0.1221 | +0.2141 | +0.2132 | 0.0000 | +0.6383 | +0.7482 | 0.943 |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Cluster 109 | +1 | +0.1561 | +0.2137 | +0.2133 | 0.0000 | +0.6947 | +0.7600 | 0.885 |
| `first_bar_return` | Cluster 45 | +1 | +0.1568 | +0.2137 | +0.2128 | 0.0000 | +0.6369 | +0.7118 | 0.948 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1500 | +0.2130 | +0.2118 | 0.0000 | +0.7661 | +0.7662 | 0.876 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Cluster 39 | +1 | +0.1407 | +0.2125 | +0.2115 | 0.0000 | +0.6111 | +0.6913 | 0.937 |
| `combo_max__first_bar_return__early_order_flow_imbalance` | Cluster 108 | +1 | +0.1324 | +0.2125 | +0.2123 | 0.0000 | +0.5934 | +0.7221 | 0.929 |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | Cluster 109 | +1 | +0.1557 | +0.2124 | +0.2120 | 0.0000 | +0.6309 | +0.7379 | 0.899 |
| `combo_max__star50_limit_proximity_early__max_down_ret` | Cluster 102 | +1 | +0.1447 | +0.2114 | +0.2107 | 0.0000 | +0.4466 | +0.6733 | 0.856 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 63 | +1 | +0.1290 | +0.2112 | +0.2097 | 0.0000 | +0.5068 | +0.6713 | 0.721 |
| `combo_sig_product__opening_drive_thrust_ratio__rsi_opening` | Cluster 59 | +1 | +0.1460 | +0.2106 | +0.2098 | 0.0000 | +0.5082 | +0.6979 | 0.928 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_ret_0` | Cluster 59 | +1 | +0.1581 | +0.2097 | +0.2083 | 0.0000 | +0.5194 | +0.6831 | 0.802 |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | Cluster 108 | +1 | +0.1381 | +0.2096 | +0.2093 | 0.0000 | +0.5455 | +0.7164 | 0.909 |
| `combo_rel_diff__first_bar_return__early_late_momentum_divergence` | Cluster 0 | +1 | +0.1565 | +0.2089 | +0.2087 | 0.0000 | +0.5292 | +0.7000 | 0.939 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 63 | +1 | +0.1405 | +0.2081 | +0.2069 | 0.0000 | +0.5996 | +0.7292 | 0.150 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure` | Cluster 82 | +1 | +0.1067 | +0.2078 | +0.2072 | 0.0000 | +0.5888 | +0.7133 | 0.929 |
| `combo_tri_max__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | Cluster 116 | +1 | +0.1587 | +0.2078 | +0.2073 | 0.0000 | +0.6588 | +0.7272 | 0.896 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | Cluster 85 | +1 | +0.1407 | +0.2075 | +0.2074 | 0.0000 | +0.7022 | +0.7456 | 0.880 |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | Cluster 45 | +1 | +0.1331 | +0.2072 | +0.2062 | 0.0000 | +0.7792 | +0.7759 | 0.898 |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | Cluster 76 | +1 | +0.1096 | +0.2072 | +0.2066 | 0.0000 | +0.6454 | +0.7231 | 0.875 |
| `combo_min__max_down_ret__close_vs_open_range` | Cluster 39 | +1 | +0.1326 | +0.2070 | +0.2060 | 0.0000 | +0.6302 | +0.7190 | 0.941 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Cluster 107 | +1 | +0.1209 | +0.2069 | +0.2070 | 0.0000 | +0.5405 | +0.6872 | 0.825 |
| `combo_tri_max__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | Cluster 5 | +1 | +0.1678 | +0.2068 | +0.2064 | 0.0000 | +0.4460 | +0.6554 | 0.905 |
| `combo_sig_product__max_up_ret__max_down_ret` | Cluster 86 | +1 | +0.1536 | +0.2062 | +0.2067 | 0.0000 | +0.6289 | +0.7195 | 0.686 |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | Cluster 81 | +1 | +0.1165 | +0.2062 | +0.2059 | 0.0000 | +0.5826 | +0.6918 | 0.935 |
| `combo_max__early_body_momentum__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1405 | +0.2059 | +0.2060 | 0.0000 | +0.4901 | +0.6559 | 0.930 |
| `combo_rel_diff__first_bar_return__body_size_progression` | Cluster 0 | +1 | +0.1559 | +0.2058 | +0.2054 | 0.0000 | +0.5112 | +0.6805 | 0.887 |
| `combo_min__bar_ret_0__shaved_bar_trend_conviction` | Cluster 39 | +1 | +0.1144 | +0.2049 | +0.2042 | 0.0002 | +0.6011 | +0.6795 | 0.902 |
| `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 48 | +1 | +0.1273 | +0.2046 | +0.2038 | 0.0002 | +0.6163 | +0.6738 | 0.919 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 15 | +1 | +0.1341 | +0.2044 | +0.2036 | 0.0002 | +0.7505 | +0.7738 | 0.950 |
| `combo_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | Cluster 9 | +1 | +0.1612 | +0.2040 | +0.2042 | 0.0002 | +0.4952 | +0.6882 | 0.948 |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | Cluster 78 | +1 | +0.0920 | +0.2033 | +0.2037 | 0.0002 | +0.6453 | +0.7256 | 0.940 |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | Cluster 45 | +1 | +0.1540 | +0.2014 | +0.2003 | 0.0002 | +0.6990 | +0.7554 | 0.894 |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | Cluster 78 | +1 | +0.0919 | +0.2006 | +0.2008 | 0.0002 | +0.6488 | +0.7272 | 0.912 |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | Cluster 48 | +1 | +0.1249 | +0.2000 | +0.1991 | 0.0002 | +0.4918 | +0.6703 | 0.900 |
| `combo_diff__bar_ret_0__late_bar_momentum` | Cluster 0 | +1 | +0.1658 | +0.1993 | +0.1989 | 0.0002 | +0.4662 | +0.6554 | 0.945 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | Cluster 79 | +1 | +0.1162 | +0.1979 | +0.1970 | 0.0002 | +0.6447 | +0.7451 | 0.922 |
| `combo_max__early_body_momentum__max_down_ret` | Cluster 38 | +1 | +0.1250 | +0.1974 | +0.1966 | 0.0002 | +0.5310 | +0.7174 | 0.890 |
| `combo_z_sum__max_down_ret__shaved_bar_trend_conviction` | Cluster 39 | +1 | +0.1190 | +0.1968 | +0.1964 | 0.0002 | +0.4589 | +0.6697 | 0.936 |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | Cluster 33 | +1 | +0.1308 | +0.1966 | +0.1962 | 0.0002 | +0.5843 | +0.7282 | 0.932 |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Cluster 58 | +1 | +0.1307 | +0.1962 | +0.1948 | 0.0002 | +0.7008 | +0.7544 | 0.941 |
| `max_down_ret` | Cluster 39 | +1 | +0.1370 | +0.1959 | +0.1949 | 0.0002 | +0.5313 | +0.6590 | 0.944 |
| `combo_rank_max__max_down_ret__close_vs_open_range` | Cluster 38 | +1 | +0.1380 | +0.1957 | +0.1947 | 0.0002 | +0.6154 | +0.7185 | 0.949 |
| `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` | Cluster 77 | +1 | +0.0949 | +0.1925 | +0.1926 | 0.0004 | +0.5532 | +0.6944 | 0.943 |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | Cluster 74 | +1 | +0.0990 | +0.1917 | +0.1914 | 0.0004 | +0.5719 | +0.7169 | 0.942 |
| `combo_sig_product__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Cluster 59 | +1 | +0.1554 | +0.1914 | +0.1908 | 0.0006 | +0.5857 | +0.6831 | 0.862 |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 13 | +1 | +0.1417 | +0.1911 | +0.1912 | 0.0006 | +0.5044 | +0.6985 | 0.902 |
| `combo_sig_product__star50_limit_proximity_early__late_bar_momentum` | Cluster 63 | +1 | +0.1146 | +0.1904 | +0.1899 | 0.0006 | +0.4569 | +0.6574 | 0.652 |
| `combo_rank_min__max_down_ret__shaved_bar_trend_conviction` | Cluster 39 | +1 | +0.1137 | +0.1898 | +0.1893 | 0.0006 | +0.6076 | +0.7077 | 0.912 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 63 | +1 | +0.1555 | +0.1892 | +0.1881 | 0.0006 | +0.5155 | +0.7010 | 0.656 |
| `combo_sig_product__first_bar_return__vwap_close_divergence_trend` | Cluster 85 | +1 | +0.1390 | +0.1877 | +0.1876 | 0.0006 | +0.6195 | +0.7256 | 0.698 |
| `combo_rank_max__first_bar_return__shaved_bar_trend_conviction` | Cluster 105 | +1 | +0.1622 | +0.1857 | +0.1855 | 0.0008 | +0.7174 | +0.7379 | 0.921 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 10 | +1 | +0.1537 | +0.1816 | +0.1817 | 0.0008 | +0.5081 | +0.6785 | 0.875 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Cluster 102 | +1 | +0.1385 | +0.1800 | +0.1793 | 0.0010 | +0.5593 | +0.7067 | 0.816 |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 10 | +1 | +0.1516 | +0.1778 | +0.1780 | 0.0010 | +0.4904 | +0.6918 | 0.881 |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 13 | +1 | +0.1426 | +0.1764 | +0.1768 | 0.0010 | +0.4436 | +0.6774 | 0.908 |
| `combo_mean__max_down_ret__close_vs_open_range` | Cluster 38 | +1 | +0.1357 | +0.1754 | +0.1742 | 0.0010 | +0.4931 | +0.6533 | 0.928 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | Cluster 85 | +1 | +0.1175 | +0.1733 | +0.1726 | 0.0012 | +0.5991 | +0.6928 | 0.722 |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | Cluster 76 | +1 | +0.1082 | +0.1718 | +0.1714 | 0.0012 | +0.6399 | +0.7390 | 0.929 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Cluster 59 | +1 | +0.1689 | +0.1717 | +0.1707 | 0.0012 | +0.5389 | +0.6949 | 0.891 |
| `vwap_trend_channel_slope` | Cluster 60 | +1 | +0.1054 | +0.1689 | +0.1689 | 0.0014 | +0.4567 | +0.6754 | 0.900 |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | Cluster 75 | +1 | +0.1045 | +0.1689 | +0.1686 | 0.0014 | +0.4500 | +0.6503 | 0.935 |
| `combo_sig_product__max_down_ret__close_vs_open_range` | Cluster 85 | +1 | +0.0992 | +0.1675 | +0.1673 | 0.0016 | +0.6042 | +0.7364 | 0.856 |
| `open_to_current_return` | Cluster 75 | +1 | +0.1229 | +0.1659 | +0.1656 | 0.0018 | +0.5562 | +0.7292 | 0.914 |
| `combo_max__max_down_ret__bar_body_rng_0` | Cluster 45 | +1 | +0.1478 | +0.1607 | +0.1595 | 0.0022 | +0.4782 | +0.6528 | 0.949 |
| `combo_max__trend_day_regime_conviction__max_down_ret` | Cluster 38 | +1 | +0.1264 | +0.1604 | +0.1596 | 0.0022 | +0.4200 | +0.6523 | 0.923 |
| `combo_sig_product__rsi_opening__max_down_ret` | Cluster 39 | +1 | +0.1283 | +0.1497 | +0.1491 | 0.0036 | +0.5896 | +0.7133 | 0.876 |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | Cluster 85 | +1 | +0.1123 | +0.1471 | +0.1468 | 0.0040 | +0.4408 | +0.6703 | 0.083 |

### 588000ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | Cluster 3 | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.787 |
| `combo_rel_diff__directional_volume_signature__smooth_momentum_structure` | Cluster 3 | +1 | +0.1078 | +0.3011 | +0.2999 | 0.0000 | +0.7892 | +0.7651 | 0.897 |
| `combo_diff__directional_volume_signature__early_vwap_acceleration` | Cluster 3 | +1 | +0.1087 | +0.2917 | +0.2905 | 0.0000 | +0.7855 | +0.7838 | 0.903 |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | Cluster 1 | +1 | +0.1329 | +0.2836 | +0.2825 | 0.0000 | +0.8900 | +0.7947 | 0.000 |
| `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | Cluster 1 | +1 | +0.1389 | +0.2830 | +0.2820 | 0.0000 | +0.8709 | +0.7927 | 0.917 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | Cluster 0 | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0002 | +0.8649 | +0.7779 | 0.730 |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | Cluster 3 | +1 | +0.0645 | +0.2645 | +0.2642 | 0.0002 | +0.6275 | +0.7512 | 0.808 |
| `max_up_ret` | Cluster 2 | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0046 | +0.6051 | +0.7266 | 0.728 |

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 11 | +1 | +0.1455 | +0.2786 | +0.2769 | 0.0000 | +0.6022 | +0.7118 | 0.645 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | Cluster 3 | +1 | +0.0839 | +0.2745 | +0.2746 | 0.0000 | +0.5504 | +0.7087 | 0.937 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 3 | +1 | +0.1204 | +0.2511 | +0.2511 | 0.0000 | +0.7555 | +0.8133 | 0.000 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Cluster 11 | +1 | +0.1454 | +0.2454 | +0.2432 | 0.0000 | +0.5036 | +0.7046 | 0.804 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 14 | +1 | +0.1458 | +0.2448 | +0.2434 | 0.0000 | +0.5461 | +0.7231 | 0.859 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1445 | +0.2341 | +0.2333 | 0.0000 | +0.5461 | +0.6923 | 0.084 |
| `combo_rank_min__max_up_ret__volume_price_confirmation` | Cluster 17 | +1 | +0.1375 | +0.2336 | +0.2318 | 0.0000 | +0.4855 | +0.6574 | 0.819 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 14 | +1 | +0.1467 | +0.2299 | +0.2289 | 0.0000 | +0.4917 | +0.6585 | 0.865 |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | Cluster 10 | +1 | +0.1458 | +0.2287 | +0.2280 | 0.0000 | +0.4880 | +0.6682 | 0.917 |
| `combo_max__max_up_ret__volume_price_confirmation` | Cluster 6 | +1 | +0.1455 | +0.2262 | +0.2255 | 0.0000 | +0.6337 | +0.7005 | 0.764 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | Cluster 15 | +1 | +0.1343 | +0.2238 | +0.2238 | 0.0000 | +0.5669 | +0.7215 | 0.835 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 7 | +1 | +0.1504 | +0.2227 | +0.2218 | 0.0000 | +0.5398 | +0.7067 | 0.785 |
| `combo_max__max_up_ret__first_bar_return` | Cluster 7 | +1 | +0.1499 | +0.2222 | +0.2215 | 0.0000 | +0.5609 | +0.7200 | 0.866 |
| `combo_rank_min__max_up_ret__directional_volume_signature` | Cluster 17 | +1 | +0.1392 | +0.2193 | +0.2180 | 0.0000 | +0.4859 | +0.6815 | 0.884 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | Cluster 1 | +1 | +0.1329 | +0.2177 | +0.2177 | 0.0000 | +0.5643 | +0.7262 | 0.914 |
| `combo_min__bar_ret_0__volume_price_confirmation` | Cluster 2 | +1 | +0.1319 | +0.2142 | +0.2129 | 0.0000 | +0.4705 | +0.6703 | 0.730 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 13 | +1 | +0.1349 | +0.2142 | +0.2127 | 0.0000 | +0.4677 | +0.6908 | 0.872 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | Cluster 15 | +1 | +0.1434 | +0.2130 | +0.2130 | 0.0000 | +0.4483 | +0.6610 | 0.924 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | Cluster 19 | +1 | +0.1249 | +0.2121 | +0.2121 | 0.0000 | +0.4073 | +0.7000 | 0.861 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | Cluster 9 | +1 | +0.1217 | +0.2081 | +0.2076 | 0.0000 | +0.3946 | +0.6533 | 0.604 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | Cluster 1 | +1 | +0.1410 | +0.2057 | +0.2056 | 0.0000 | +0.6054 | +0.7303 | 0.939 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1500 | +0.2051 | +0.2042 | 0.0000 | +0.5341 | +0.6821 | 0.936 |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 5 | +1 | +0.1424 | +0.2045 | +0.2036 | 0.0000 | +0.4941 | +0.7154 | 0.812 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | Cluster 13 | +1 | +0.1347 | +0.2018 | +0.2006 | 0.0000 | +0.5041 | +0.7123 | 0.938 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | Cluster 1 | +1 | +0.1346 | +0.1992 | +0.1996 | 0.0000 | +0.3716 | +0.6651 | 0.447 |
| `combo_min__bar_ret_0__directional_volume_signature` | Cluster 2 | +1 | +0.1349 | +0.1981 | +0.1973 | 0.0000 | +0.6160 | +0.7179 | 0.883 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 4 | +1 | +0.1520 | +0.1964 | +0.1955 | 0.0000 | +0.4819 | +0.6667 | 0.867 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Cluster 0 | +1 | +0.1296 | +0.1953 | +0.1947 | 0.0000 | +0.4529 | +0.6954 | 0.860 |
| `combo_diff__first_bar_return__volume_weighted_momentum_acceleration` | Cluster 10 | +1 | +0.1486 | +0.1912 | +0.1903 | 0.0000 | +0.4754 | +0.6641 | 0.853 |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | Cluster 21 | +1 | +0.1513 | +0.1896 | +0.1886 | 0.0000 | +0.5275 | +0.7154 | 0.783 |
| `combo_rel_diff__directional_volume_signature__early_late_momentum_divergence` | Cluster 12 | +1 | +0.1042 | +0.1884 | +0.1879 | 0.0000 | +0.5109 | +0.6979 | 0.717 |
| `combo_z_sum__max_up_ret__rally_strength_max` | Cluster 0 | +1 | +0.1203 | +0.1870 | +0.1858 | 0.0002 | +0.3804 | +0.6662 | 0.840 |
| `combo_z_sum__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 5 | +1 | +0.1217 | +0.1793 | +0.1776 | 0.0002 | +0.4203 | +0.6831 | 0.909 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Cluster 20 | +1 | +0.1518 | +0.1703 | +0.1692 | 0.0008 | +0.3332 | +0.6687 | 0.806 |
| `combo_max__star50_limit_proximity_early__directional_volume_signature` | Cluster 18 | +1 | +0.1334 | +0.1634 | +0.1626 | 0.0012 | +0.5218 | +0.6718 | 0.613 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Cluster 16 | +1 | +0.1165 | +0.1615 | +0.1600 | 0.0012 | +0.6528 | +0.7256 | 0.731 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | Cluster 20 | +1 | +0.1376 | +0.1597 | +0.1585 | 0.0014 | +0.3290 | +0.6523 | 0.853 |


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

### Cluster Overview per ETF / Side

| ETF | Side | Total Features | Clusters | Avg Silhouette | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 300ETF | single | 26 | 8 | 0.2535 | `[9, 6, 3, 2, 2, 2, 1, 1]` |
| 500ETF | single | 317 | 117 | 0.2159 | `[15, 14, 12, 12, 11, 9, 8, 8, 7, 7, 7, 6, ... (117 clusters)]` |
| 588000ETF | single | 8 | 4 | 0.3860 | `[4, 2, 1, 1]` |
| 159915ETF | single | 37 | 22 | 0.3421 | `[3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ... (22 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 9 | 0.2535 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_min__star50_limit_proximity_early__bar_body_rng_0`, `combo_tri_min__max_up_ret__bar_body_rng_0__limit_down_proximity_early` |
| 300ETF | single | Cluster 1 | 3 | 0.2535 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 2 | 2 | 0.2535 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` |
| 300ETF | single | Cluster 3 | 1 | 0.2535 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | _(none)_ |
| 300ETF | single | Cluster 4 | 1 | 0.2535 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | _(none)_ |
| 300ETF | single | Cluster 5 | 6 | 0.2535 | `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_min__opening_drive_thrust_ratio__max_up_ret`, `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` |
| 300ETF | single | Cluster 6 | 2 | 0.2535 | `rbreaker_sell_setup_proximity_early` | `star50_limit_proximity_early` |
| 300ETF | single | Cluster 7 | 2 | 0.2535 | `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 500ETF | single | Cluster 0 | 15 | 0.2159 | `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | `combo_rel_diff__max_up_ret__body_size_progression`, `combo_rel_diff__max_up_ret__smooth_momentum_structure`, `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__early_late_momentum_divergence`, `combo_clamp_diff__max_up_ret__body_size_progression`, `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_clamp_diff__first_bar_return__late_bar_momentum`, `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`, `combo_rel_diff__first_bar_return__body_size_progression`, `combo_diff__bar_ret_0__late_bar_momentum`, `combo_rel_diff__first_bar_return__early_late_momentum_divergence`, `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 1 | 2 | 0.2159 | `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` |
| 500ETF | single | Cluster 2 | 3 | 0.2159 | `combo_tri_mean__opening_drive_thrust_ratio__early_body_momentum__star50_limit_proximity_early` | `combo_tri_mean__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early`, `combo_clamp_diff__net_volume_flow__demark_setup_reversal_early` |
| 500ETF | single | Cluster 3 | 3 | 0.2159 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `combo_tri_median__max_up_ret__early_body_momentum__star50_limit_proximity_early`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 4 | 1 | 0.2159 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | _(none)_ |
| 500ETF | single | Cluster 5 | 1 | 0.2159 | `combo_tri_max__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 6 | 2 | 0.2159 | `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | `combo_max__early_body_momentum__star50_limit_proximity_early` |
| 500ETF | single | Cluster 7 | 2 | 0.2159 | `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` |
| 500ETF | single | Cluster 8 | 1 | 0.2159 | `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 9 | 1 | 0.2159 | `combo_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | _(none)_ |
| 500ETF | single | Cluster 10 | 2 | 0.2159 | `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 11 | 1 | 0.2159 | `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 12 | 2 | 0.2159 | `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 13 | 2 | 0.2159 | `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 14 | 3 | 0.2159 | `combo_rank_max__max_up_ret__net_volume_flow` | `combo_tri_max__max_up_ret__volatility_expansion_trend_vector__early_body_momentum`, `combo_max__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 15 | 1 | 0.2159 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | _(none)_ |
| 500ETF | single | Cluster 16 | 1 | 0.2159 | `combo_mean__max_up_ret__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 17 | 1 | 0.2159 | `combo_mean__max_up_ret__early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 18 | 2 | 0.2159 | `combo_rank_max__max_up_ret__early_order_flow_imbalance` | `combo_max__max_up_ret__early_order_flow_imbalance` |
| 500ETF | single | Cluster 19 | 3 | 0.2159 | `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | `combo_diff__max_up_ret__h2_l2_pullback_continuation`, `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 20 | 2 | 0.2159 | `combo_max__max_up_ret__shaved_bar_trend_conviction` | `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 21 | 2 | 0.2159 | `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `combo_min__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 22 | 1 | 0.2159 | `combo_min__max_up_ret__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 23 | 1 | 0.2159 | `combo_min__max_up_ret__early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 24 | 2 | 0.2159 | `combo_min__max_up_ret__vwap_close_divergence_trend` | `combo_rank_min__max_up_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 25 | 1 | 0.2159 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | _(none)_ |
| 500ETF | single | Cluster 26 | 2 | 0.2159 | `combo_mean__max_up_ret__volatility_expansion_trend_vector` | `combo_mean__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 27 | 2 | 0.2159 | `combo_max__max_up_ret__vwap_close_divergence_trend` | `combo_rank_max__max_up_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 28 | 9 | 0.2159 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_rank_min__star50_limit_proximity_early__bar_ret_0`, `combo_min__star50_limit_proximity_early__first_bar_return`, `combo_max__star50_limit_proximity_early__first_bar_return`, `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_max__star50_limit_proximity_early__bar_body_rng_0` |
| 500ETF | single | Cluster 29 | 4 | 0.2159 | `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `combo_max__opening_drive_thrust_ratio__early_body_momentum`, `combo_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction`, `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 30 | 1 | 0.2159 | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | _(none)_ |
| 500ETF | single | Cluster 31 | 2 | 0.2159 | `combo_rank_min__opening_drive_thrust_ratio__close_vs_open_range` | `combo_min__opening_drive_thrust_ratio__close_vs_open_range` |
| 500ETF | single | Cluster 32 | 1 | 0.2159 | `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 33 | 1 | 0.2159 | `combo_mean__max_down_ret__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 34 | 1 | 0.2159 | `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__trend_day_regime_conviction` | _(none)_ |
| 500ETF | single | Cluster 35 | 1 | 0.2159 | `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 36 | 1 | 0.2159 | `combo_clamp_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | _(none)_ |
| 500ETF | single | Cluster 37 | 2 | 0.2159 | `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` |
| 500ETF | single | Cluster 38 | 7 | 0.2159 | `combo_mean__net_volume_flow__close_vs_open_range` | `combo_mean__net_volume_flow__max_down_ret`, `combo_rank_max__net_volume_flow__max_down_ret`, `combo_mean__max_down_ret__close_vs_open_range`, `combo_max__early_body_momentum__max_down_ret`, `combo_rank_max__max_down_ret__close_vs_open_range`, `combo_max__trend_day_regime_conviction__max_down_ret` |
| 500ETF | single | Cluster 39 | 12 | 0.2159 | `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | `combo_min__max_down_ret__vwap_close_divergence_trend`, `combo_rank_min__volatility_expansion_trend_vector__max_down_ret`, `max_down_ret`, `combo_min__early_order_flow_imbalance__max_down_ret`, `combo_min__max_down_ret__close_vs_open_range`, `combo_rank_min__early_order_flow_imbalance__max_down_ret`, `combo_rank_min__early_body_momentum__max_down_ret`, `combo_rank_min__max_down_ret__shaved_bar_trend_conviction`, `combo_sig_product__rsi_opening__max_down_ret`, `combo_z_sum__max_down_ret__shaved_bar_trend_conviction`, `combo_min__bar_ret_0__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 40 | 3 | 0.2159 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`, `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 41 | 2 | 0.2159 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 42 | 2 | 0.2159 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 500ETF | single | Cluster 43 | 1 | 0.2159 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 44 | 7 | 0.2159 | `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `combo_rel_diff__star50_limit_proximity_early__body_size_progression`, `combo_rel_diff__star50_limit_proximity_early__late_bar_momentum`, `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`, `combo_diff__star50_limit_proximity_early__late_bar_momentum` |
| 500ETF | single | Cluster 45 | 11 | 0.2159 | `combo_min__bar_ret_0__bar_body_rng_0` | `combo_max__bar_ret_0__max_down_ret`, `first_bar_return`, `combo_mean__bar_ret_0__max_down_ret`, `combo_rank_max__max_down_ret__bar_body_rng_0`, `combo_rank_max__bar_ret_0__bar_body_rng_0`, `combo_min__bar_ret_0__early_order_flow_imbalance`, `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0`, `combo_min__first_bar_return__max_down_ret`, `combo_min__max_down_ret__bar_body_rng_0`, `combo_max__max_down_ret__bar_body_rng_0` |
| 500ETF | single | Cluster 46 | 2 | 0.2159 | `combo_mean__net_volume_flow__bar_body_rng_0` | `combo_mean__close_vs_open_range__bar_body_rng_0` |
| 500ETF | single | Cluster 47 | 2 | 0.2159 | `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 48 | 3 | 0.2159 | `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0` | `combo_min__bar_ret_0__vwap_close_divergence_trend`, `combo_min__vwap_close_divergence_trend__bar_body_rng_0` |
| 500ETF | single | Cluster 49 | 2 | 0.2159 | `combo_rank_min__bar_ret_0__close_vs_open_range` | `combo_min__bar_ret_0__close_vs_open_range` |
| 500ETF | single | Cluster 50 | 1 | 0.2159 | `combo_mean__bar_ret_0__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 51 | 2 | 0.2159 | `combo_mean__bar_ret_0__close_vs_open_range` | `combo_mean__first_bar_return__rsi_opening` |
| 500ETF | single | Cluster 52 | 1 | 0.2159 | `combo_rank_max__early_order_flow_imbalance__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 53 | 2 | 0.2159 | `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | `combo_min__net_volume_flow__first_bar_return` |
| 500ETF | single | Cluster 54 | 2 | 0.2159 | `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` |
| 500ETF | single | Cluster 55 | 2 | 0.2159 | `combo_mean__first_bar_return__vwap_close_divergence_trend` | `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` |
| 500ETF | single | Cluster 56 | 1 | 0.2159 | `combo_min__close_vs_open_range__bar_body_rng_0` | _(none)_ |
| 500ETF | single | Cluster 57 | 2 | 0.2159 | `combo_clamp_diff__first_bar_return__h2_l2_pullback_continuation` | `combo_diff__bar_ret_0__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 58 | 2 | 0.2159 | `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` |
| 500ETF | single | Cluster 59 | 8 | 0.2159 | `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`, `combo_sig_product__opening_drive_thrust_ratio__max_down_ret`, `combo_sig_product__opening_drive_thrust_ratio__vwap_close_divergence_trend`, `combo_sig_product__opening_drive_thrust_ratio__bar_ret_0`, `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`, `combo_sig_product__opening_drive_thrust_ratio__rsi_opening`, `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 60 | 2 | 0.2159 | `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 61 | 1 | 0.2159 | `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 62 | 1 | 0.2159 | `combo_rel_diff__opening_drive_thrust_ratio__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 63 | 6 | 0.2159 | `rbreaker_sell_setup_proximity_early` | `combo_sig_product__star50_limit_proximity_early__first_bar_return`, `combo_sig_product__star50_limit_proximity_early__late_bar_momentum`, `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_sig_product__rbreaker_sell_setup_proximity_early__early_body_momentum` |
| 500ETF | single | Cluster 64 | 2 | 0.2159 | `combo_min__trend_bar_close_consistency__star50_limit_proximity_early` | `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` |
| 500ETF | single | Cluster 65 | 2 | 0.2159 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` |
| 500ETF | single | Cluster 66 | 1 | 0.2159 | `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 67 | 2 | 0.2159 | `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` |
| 500ETF | single | Cluster 68 | 3 | 0.2159 | `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend`, `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 69 | 2 | 0.2159 | `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 70 | 1 | 0.2159 | `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 71 | 4 | 0.2159 | `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_rank_min__rbreaker_sell_setup_proximity_early__close_vs_open_range`, `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 72 | 2 | 0.2159 | `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `combo_mean__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 73 | 2 | 0.2159 | `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 74 | 4 | 0.2159 | `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`, `combo_rel_diff__early_body_momentum__h2_l2_pullback_continuation`, `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 75 | 2 | 0.2159 | `open_to_current_return` | `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 76 | 3 | 0.2159 | `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | `combo_min__close_vs_open_range__vwap_close_divergence_trend`, `combo_mean__close_vs_open_range__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 77 | 2 | 0.2159 | `combo_min__net_volume_flow__vwap_close_divergence_trend` | `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 78 | 2 | 0.2159 | `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 79 | 2 | 0.2159 | `combo_sig_product__net_volume_flow__close_vs_open_range` | `combo_max__rsi_opening__early_order_flow_imbalance` |
| 500ETF | single | Cluster 80 | 2 | 0.2159 | `combo_rank_min__volatility_expansion_trend_vector__early_order_flow_imbalance` | `combo_min__early_order_flow_imbalance__close_vs_open_range` |
| 500ETF | single | Cluster 81 | 1 | 0.2159 | `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | _(none)_ |
| 500ETF | single | Cluster 82 | 2 | 0.2159 | `combo_max__early_body_momentum__close_vs_open_range` | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure` |
| 500ETF | single | Cluster 83 | 2 | 0.2159 | `combo_min__rsi_opening__close_vs_open_range` | `combo_rank_min__trend_bar_close_consistency__close_vs_open_range` |
| 500ETF | single | Cluster 84 | 1 | 0.2159 | `combo_mean__volatility_expansion_trend_vector__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 85 | 7 | 0.2159 | `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `combo_sig_product__max_down_ret__vwap_close_divergence_trend`, `combo_ratio__max_down_ret__early_order_flow_imbalance`, `combo_ratio__max_down_ret__net_volume_flow`, `combo_sig_product__first_bar_return__vwap_close_divergence_trend`, `combo_ratio__max_down_ret__volatility_expansion_trend_vector`, `combo_sig_product__max_down_ret__close_vs_open_range` |
| 500ETF | single | Cluster 86 | 8 | 0.2159 | `combo_sig_product__max_up_ret__early_body_momentum` | `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`, `combo_sig_product__max_up_ret__vwap_close_divergence_trend`, `combo_sig_product__max_up_ret__close_vs_open_range`, `combo_sig_product__max_up_ret__max_down_ret`, `combo_sig_product__max_up_ret__first_bar_return`, `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`, `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 87 | 2 | 0.2159 | `combo_min__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` |
| 500ETF | single | Cluster 88 | 2 | 0.2159 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` |
| 500ETF | single | Cluster 89 | 1 | 0.2159 | `combo_mean__max_up_ret__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 90 | 2 | 0.2159 | `combo_max__max_up_ret__max_down_ret` | `combo_rank_max__max_up_ret__max_down_ret` |
| 500ETF | single | Cluster 91 | 2 | 0.2159 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | `combo_tri_median__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` |
| 500ETF | single | Cluster 92 | 3 | 0.2159 | `max_up_ret` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 93 | 4 | 0.2159 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector`, `combo_mean__opening_drive_thrust_ratio__max_up_ret`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 94 | 1 | 0.2159 | `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 95 | 1 | 0.2159 | `combo_min__max_up_ret__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 96 | 2 | 0.2159 | `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` |
| 500ETF | single | Cluster 97 | 3 | 0.2159 | `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | `combo_diff__first_bar_return__demark_setup_reversal_early`, `combo_rel_diff__first_bar_return__demark_setup_reversal_early` |
| 500ETF | single | Cluster 98 | 3 | 0.2159 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0`, `combo_tri_median__net_volume_flow__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 99 | 1 | 0.2159 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 100 | 2 | 0.2159 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 101 | 1 | 0.2159 | `combo_rank_min__max_up_ret__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 102 | 12 | 0.2159 | `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `combo_min__star50_limit_proximity_early__max_down_ret`, `combo_mean__star50_limit_proximity_early__max_down_ret`, `combo_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`, `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`, `combo_rank_max__star50_limit_proximity_early__max_down_ret`, `star50_limit_proximity_early`, `combo_sig_product__star50_limit_proximity_early__max_down_ret`, `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`, `combo_max__star50_limit_proximity_early__max_down_ret`, `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction`, `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` |
| 500ETF | single | Cluster 103 | 2 | 0.2159 | `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | `combo_max__trend_bar_close_consistency__bar_body_rng_0` |
| 500ETF | single | Cluster 104 | 4 | 0.2159 | `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | `combo_max__first_bar_return__close_vs_open_range`, `combo_rank_max__early_body_momentum__bar_ret_0`, `combo_max__net_volume_flow__first_bar_return` |
| 500ETF | single | Cluster 105 | 1 | 0.2159 | `combo_rank_max__first_bar_return__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 106 | 2 | 0.2159 | `combo_mean__max_up_ret__first_bar_return` | `combo_max__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 107 | 1 | 0.2159 | `combo_sig_product__net_volume_flow__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 108 | 3 | 0.2159 | `combo_max__first_bar_return__early_order_flow_imbalance` | `combo_mean__first_bar_return__early_order_flow_imbalance`, `combo_rank_max__bar_ret_0__early_order_flow_imbalance` |
| 500ETF | single | Cluster 109 | 3 | 0.2159 | `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | `combo_max__vwap_close_divergence_trend__bar_body_rng_0`, `combo_max__first_bar_return__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 110 | 2 | 0.2159 | `combo_rank_min__max_up_ret__bar_body_rng_0` | `combo_min__max_up_ret__first_bar_return` |
| 500ETF | single | Cluster 111 | 14 | 0.2159 | `opening_drive_thrust_ratio` | `combo_mean__opening_drive_thrust_ratio__first_bar_return`, `combo_min__opening_drive_thrust_ratio__first_bar_return`, `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0`, `combo_max__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`, `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`, `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_max__opening_drive_thrust_ratio__first_bar_return`, `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_rank_max__opening_drive_thrust_ratio__max_down_ret`, `combo_mean__opening_drive_thrust_ratio__max_down_ret`, `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`, `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 112 | 5 | 0.2159 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`, `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` |
| 500ETF | single | Cluster 113 | 2 | 0.2159 | `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 114 | 1 | 0.2159 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 115 | 2 | 0.2159 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 116 | 2 | 0.2159 | `combo_tri_max__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | `combo_tri_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` |
| 588000ETF | single | Cluster 0 | 1 | 0.3860 | `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | _(none)_ |
| 588000ETF | single | Cluster 1 | 2 | 0.3860 | `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` |
| 588000ETF | single | Cluster 2 | 1 | 0.3860 | `max_up_ret` | _(none)_ |
| 588000ETF | single | Cluster 3 | 4 | 0.3860 | `combo_diff__directional_volume_signature__smooth_momentum_structure` | `combo_rel_diff__directional_volume_signature__smooth_momentum_structure`, `combo_diff__directional_volume_signature__early_vwap_acceleration`, `combo_sig_product__directional_volume_signature__smooth_momentum_structure` |
| 159915ETF | single | Cluster 0 | 2 | 0.3421 | `combo_max__max_up_ret__volume_weighted_price_position` | `combo_z_sum__max_up_ret__rally_strength_max` |
| 159915ETF | single | Cluster 1 | 3 | 0.3421 | `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend`, `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` |
| 159915ETF | single | Cluster 2 | 2 | 0.3421 | `combo_min__bar_ret_0__volume_price_confirmation` | `combo_min__bar_ret_0__directional_volume_signature` |
| 159915ETF | single | Cluster 3 | 2 | 0.3421 | `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` |
| 159915ETF | single | Cluster 4 | 1 | 0.3421 | `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__bar_ret_0` | _(none)_ |
| 159915ETF | single | Cluster 5 | 2 | 0.3421 | `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | `combo_z_sum__volatility_expansion_trend_vector__volume_price_confirmation` |
| 159915ETF | single | Cluster 6 | 1 | 0.3421 | `combo_max__max_up_ret__volume_price_confirmation` | _(none)_ |
| 159915ETF | single | Cluster 7 | 2 | 0.3421 | `combo_rank_max__max_up_ret__bar_ret_0` | `combo_max__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 8 | 2 | 0.3421 | `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` |
| 159915ETF | single | Cluster 9 | 1 | 0.3421 | `combo_rel_diff__max_up_ret__keltner_squeeze_width` | _(none)_ |
| 159915ETF | single | Cluster 10 | 2 | 0.3421 | `combo_diff__first_bar_return__volume_weighted_momentum_acceleration` | `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` |
| 159915ETF | single | Cluster 11 | 2 | 0.3421 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_min__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 12 | 1 | 0.3421 | `combo_rel_diff__directional_volume_signature__early_late_momentum_divergence` | _(none)_ |
| 159915ETF | single | Cluster 13 | 2 | 0.3421 | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 14 | 2 | 0.3421 | `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0` |
| 159915ETF | single | Cluster 15 | 2 | 0.3421 | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` |
| 159915ETF | single | Cluster 16 | 1 | 0.3421 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | _(none)_ |
| 159915ETF | single | Cluster 17 | 2 | 0.3421 | `combo_rank_min__max_up_ret__volume_price_confirmation` | `combo_rank_min__max_up_ret__directional_volume_signature` |
| 159915ETF | single | Cluster 18 | 1 | 0.3421 | `combo_max__star50_limit_proximity_early__directional_volume_signature` | _(none)_ |
| 159915ETF | single | Cluster 19 | 1 | 0.3421 | `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | _(none)_ |
| 159915ETF | single | Cluster 20 | 2 | 0.3421 | `combo_ratio__bar_ret_0__volume_weighted_price_position` | `combo_z_sum__first_bar_return__volume_weighted_price_position` |
| 159915ETF | single | Cluster 21 | 1 | 0.3421 | `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | _(none)_ |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | `min` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_mean` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`limit_down_proximity_early` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__limit_down_proximity_early` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`limit_down_proximity_early` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_concentration` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`early_body_momentum` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency`, c=`star50_limit_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | `tri_min` | a=`max_up_ret`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_min__star50_limit_proximity_early__first_bar_return` | `min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`net_volume_flow` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__early_body_momentum__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum`, c=`star50_limit_proximity_early` |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | `clamp_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | `min` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `mean` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | `tri_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_min__max_up_ret__max_down_ret` | `rank_min` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | `rel_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | `mean` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`late_bar_momentum` |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | `rank_min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_mean__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early` | `tri_mean` | a=`volatility_expansion_trend_vector`, b=`early_body_momentum`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | `rel_diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | `clamp_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_median__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_max__max_down_ret__bar_body_rng_0` | `rank_max` | a=`max_down_ret`, b=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`trend_day_regime_conviction` |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | `rank_min` | a=`trend_bar_close_consistency`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | `rel_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | `diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_median__max_up_ret__early_body_momentum__star50_limit_proximity_early` | `tri_median` | a=`max_up_ret`, b=`early_body_momentum`, c=`star50_limit_proximity_early` |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | `diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | `clamp_diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | `tri_max` | a=`max_up_ret`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_mean__net_volume_flow__bar_body_rng_0` | `mean` | a=`net_volume_flow`, b=`bar_body_rng_0` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `rank_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`star50_limit_proximity_early` |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | `max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | `rel_diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_rank_min__opening_drive_thrust_ratio__close_vs_open_range` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | `tri_mean` | a=`max_up_ret`, b=`trend_bar_close_consistency`, c=`bar_ret_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`h2_l2_pullback_continuation` |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`early_order_flow_imbalance` |
| `combo_rel_diff__star50_limit_proximity_early__late_bar_momentum` | `rel_diff` | a=`star50_limit_proximity_early`, b=`late_bar_momentum` |
| `combo_min__trend_bar_close_consistency__star50_limit_proximity_early` | `min` | a=`trend_bar_close_consistency`, b=`star50_limit_proximity_early` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_max__max_up_ret__volatility_expansion_trend_vector__early_body_momentum` | `tri_max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector`, c=`early_body_momentum` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | `mean` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__net_volume_flow` | `rank_max` | a=`max_up_ret`, b=`net_volume_flow` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | `mean` | a=`opening_drive_thrust_ratio`, b=`early_order_flow_imbalance` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | `rel_diff` | a=`volatility_expansion_trend_vector`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | `mean` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `mean` | a=`opening_drive_thrust_ratio`, b=`shaved_bar_trend_conviction` |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | `max` | a=`volatility_expansion_trend_vector`, b=`bar_body_rng_0` |
| `combo_min__bar_ret_0__bar_body_rng_0` | `min` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_tri_median__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`net_volume_flow`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | `rank_min` | a=`trend_bar_close_consistency`, b=`bar_ret_0` |
| `combo_max__max_up_ret__max_down_ret` | `max` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_mean__max_up_ret__first_bar_return` | `mean` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__early_body_momentum` | `sig_product` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | `rank_min` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | `max` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__max_up_ret__max_down_ret` | `rank_max` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | `mean` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | `mean` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_min__max_up_ret__net_volume_flow` | `min` | a=`max_up_ret`, b=`net_volume_flow` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range` |
| `combo_max__trend_bar_close_consistency__bar_body_rng_0` | `max` | a=`trend_bar_close_consistency`, b=`bar_body_rng_0` |
| `combo_max__max_up_ret__close_vs_open_range` | `max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rel_diff__early_body_momentum__h2_l2_pullback_continuation` | `rel_diff` | a=`early_body_momentum`, b=`h2_l2_pullback_continuation` |
| `combo_rank_min__trend_bar_close_consistency__close_vs_open_range` | `rank_min` | a=`trend_bar_close_consistency`, b=`close_vs_open_range` |
| `combo_min__net_volume_flow__first_bar_return` | `min` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `max` | a=`opening_drive_thrust_ratio`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__bar_ret_0__close_vs_open_range` | `rank_min` | a=`bar_ret_0`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | `min` | a=`star50_limit_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_max__max_up_ret__early_order_flow_imbalance` | `max` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_clamp_diff__net_volume_flow__demark_setup_reversal_early` | `clamp_diff` | a=`net_volume_flow`, b=`demark_setup_reversal_early` |
| `combo_mean__first_bar_return__rsi_opening` | `mean` | a=`first_bar_return`, b=`rsi_opening` |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | `clamp_diff` | a=`bar_body_rng_0`, b=`h2_l2_pullback_continuation` |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | `rel_diff` | a=`first_bar_return`, b=`h2_l2_pullback_continuation` |
| `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_min__bar_ret_0__close_vs_open_range` | `min` | a=`bar_ret_0`, b=`close_vs_open_range` |
| `combo_clamp_diff__first_bar_return__late_bar_momentum` | `clamp_diff` | a=`first_bar_return`, b=`late_bar_momentum` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | `rank_max` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `max` | a=`opening_drive_thrust_ratio`, b=`vwap_close_divergence_trend` |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_min__close_vs_open_range__bar_body_rng_0` | `min` | a=`close_vs_open_range`, b=`bar_body_rng_0` |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | `rank_min` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | `min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | `rank_min` | a=`star50_limit_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | `min` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_mean__max_up_ret__max_down_ret` | `mean` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_mean__max_up_ret__close_vs_open_range` | `mean` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | `rank_max` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_diff__star50_limit_proximity_early__late_bar_momentum` | `diff` | a=`star50_limit_proximity_early`, b=`late_bar_momentum` |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_mean__net_volume_flow__close_vs_open_range` | `mean` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | `tri_max` | a=`max_up_ret`, b=`early_body_momentum`, c=`star50_limit_proximity_early` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_clamp_diff__first_bar_return__h2_l2_pullback_continuation` | `clamp_diff` | a=`first_bar_return`, b=`h2_l2_pullback_continuation` |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | `sig_product` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | `mean` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_min__max_up_ret__early_order_flow_imbalance` | `min` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rank_min__volatility_expansion_trend_vector__early_order_flow_imbalance` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`early_order_flow_imbalance` |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | `min` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`shaved_bar_trend_conviction` |
| `combo_min__max_up_ret__first_bar_return` | `min` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_min__max_up_ret__close_vs_open_range` | `min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rel_diff__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`vwap_close_divergence_trend` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | `max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_max__first_bar_return__close_vs_open_range` | `max` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | `rank_max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_max__rsi_opening__early_order_flow_imbalance` | `max` | a=`rsi_opening`, b=`early_order_flow_imbalance` |
| `combo_max__early_body_momentum__close_vs_open_range` | `max` | a=`early_body_momentum`, b=`close_vs_open_range` |
| `combo_max__net_volume_flow__first_bar_return` | `max` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_min__max_up_ret__max_down_ret` | `min` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | `mean` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_min__early_order_flow_imbalance__max_down_ret` | `min` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | `mean` | a=`close_vs_open_range`, b=`bar_body_rng_0` |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | `diff` | a=`bar_ret_0`, b=`h2_l2_pullback_continuation` |
| `combo_mean__volatility_expansion_trend_vector__shaved_bar_trend_conviction` | `mean` | a=`volatility_expansion_trend_vector`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rank_max__net_volume_flow__max_down_ret` | `rank_max` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`vwap_close_divergence_trend` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum`, c=`trend_day_regime_conviction` |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | `min` | a=`early_order_flow_imbalance`, b=`close_vs_open_range` |
| `combo_rank_min__max_up_ret__vwap_close_divergence_trend` | `rank_min` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_max__vwap_close_divergence_trend__bar_body_rng_0` | `max` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__opening_drive_thrust_ratio__first_bar_return` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | `mean` | a=`first_bar_return`, b=`early_order_flow_imbalance` |
| `combo_min__rsi_opening__close_vs_open_range` | `min` | a=`rsi_opening`, b=`close_vs_open_range` |
| `combo_mean__bar_ret_0__close_vs_open_range` | `mean` | a=`bar_ret_0`, b=`close_vs_open_range` |
| `combo_mean__first_bar_return__vwap_close_divergence_trend` | `mean` | a=`first_bar_return`, b=`vwap_close_divergence_trend` |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`late_bar_momentum` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | `min` | a=`net_volume_flow`, b=`vwap_close_divergence_trend` |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | `min` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_mean__bar_ret_0__shaved_bar_trend_conviction` | `mean` | a=`bar_ret_0`, b=`shaved_bar_trend_conviction` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_ratio__max_down_ret__net_volume_flow` | `ratio` | a=`max_down_ret`, b=`net_volume_flow` |
| `combo_sig_product__max_up_ret__first_bar_return` | `sig_product` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_mean__net_volume_flow__max_down_ret` | `mean` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_min__first_bar_return__max_down_ret` | `min` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_min__max_down_ret__bar_body_rng_0` | `min` | a=`max_down_ret`, b=`bar_body_rng_0` |
| `combo_max__star50_limit_proximity_early__first_bar_return` | `max` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_min__early_body_momentum__max_down_ret` | `rank_min` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | `rank_min` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | `rel_diff` | a=`volatility_expansion_trend_vector`, b=`h2_l2_pullback_continuation` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | `diff` | a=`volatility_expansion_trend_vector`, b=`h2_l2_pullback_continuation` |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | `rank_max` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | `rank_max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | `min` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | `rank_max` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_max__first_bar_return__early_order_flow_imbalance` | `max` | a=`first_bar_return`, b=`early_order_flow_imbalance` |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | `max` | a=`first_bar_return`, b=`vwap_close_divergence_trend` |
| `combo_max__star50_limit_proximity_early__max_down_ret` | `max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__early_body_momentum` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_sig_product__opening_drive_thrust_ratio__rsi_opening` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`rsi_opening` |
| `combo_sig_product__opening_drive_thrust_ratio__bar_ret_0` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | `rank_max` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_rel_diff__first_bar_return__early_late_momentum_divergence` | `rel_diff` | a=`first_bar_return`, b=`early_late_momentum_divergence` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`smooth_momentum_structure` |
| `combo_tri_max__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | `tri_max` | a=`early_body_momentum`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | `ratio` | a=`max_down_ret`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | `rank_min` | a=`early_order_flow_imbalance`, b=`bar_body_rng_0` |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | `min` | a=`close_vs_open_range`, b=`vwap_close_divergence_trend` |
| `combo_min__max_down_ret__close_vs_open_range` | `min` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_sig_product__net_volume_flow__first_bar_return` | `sig_product` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_tri_max__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency`, c=`star50_limit_proximity_early` |
| `combo_sig_product__max_up_ret__max_down_ret` | `sig_product` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | `clamp_diff` | a=`max_down_ret`, b=`h2_l2_pullback_continuation` |
| `combo_max__early_body_momentum__star50_limit_proximity_early` | `max` | a=`early_body_momentum`, b=`star50_limit_proximity_early` |
| `combo_rel_diff__first_bar_return__body_size_progression` | `rel_diff` | a=`first_bar_return`, b=`body_size_progression` |
| `combo_min__bar_ret_0__shaved_bar_trend_conviction` | `min` | a=`bar_ret_0`, b=`shaved_bar_trend_conviction` |
| `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0` | `rank_min` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_day_regime_conviction` |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | `min` | a=`vwap_close_divergence_trend`, b=`shaved_bar_trend_conviction` |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | `rank_max` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | `rank_min` | a=`vwap_close_divergence_trend`, b=`shaved_bar_trend_conviction` |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | `min` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_diff__bar_ret_0__late_bar_momentum` | `diff` | a=`bar_ret_0`, b=`late_bar_momentum` |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | `sig_product` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_max__early_body_momentum__max_down_ret` | `max` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_z_sum__max_down_ret__shaved_bar_trend_conviction` | `z_sum` | a=`max_down_ret`, b=`shaved_bar_trend_conviction` |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | `mean` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration`, c=`bar_ret_0` |
| `combo_rank_max__max_down_ret__close_vs_open_range` | `rank_max` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` | `mean` | a=`trend_bar_close_consistency`, b=`vwap_close_divergence_trend` |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | `diff` | a=`close_vs_open_range`, b=`h2_l2_pullback_continuation` |
| `combo_sig_product__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | `rank_max` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__star50_limit_proximity_early__late_bar_momentum` | `sig_product` | a=`star50_limit_proximity_early`, b=`late_bar_momentum` |
| `combo_rank_min__max_down_ret__shaved_bar_trend_conviction` | `rank_min` | a=`max_down_ret`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__first_bar_return__vwap_close_divergence_trend` | `sig_product` | a=`first_bar_return`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__first_bar_return__shaved_bar_trend_conviction` | `rank_max` | a=`first_bar_return`, b=`shaved_bar_trend_conviction` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`star50_limit_proximity_early` |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | `max` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_mean__max_down_ret__close_vs_open_range` | `mean` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | `mean` | a=`close_vs_open_range`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | `sig_product` | a=`trend_day_regime_conviction`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__max_down_ret__close_vs_open_range` | `sig_product` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_max__max_down_ret__bar_body_rng_0` | `max` | a=`max_down_ret`, b=`bar_body_rng_0` |
| `combo_max__trend_day_regime_conviction__max_down_ret` | `max` | a=`trend_day_regime_conviction`, b=`max_down_ret` |
| `combo_sig_product__rsi_opening__max_down_ret` | `sig_product` | a=`rsi_opening`, b=`max_down_ret` |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | `ratio` | a=`max_down_ret`, b=`early_order_flow_imbalance` |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | `diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_rel_diff__directional_volume_signature__smooth_momentum_structure` | `rel_diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_diff__directional_volume_signature__early_vwap_acceleration` | `diff` | a=`directional_volume_signature`, b=`early_vwap_acceleration` |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `diff` | a=`trend_day_regime_conviction`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `rel_diff` | a=`trend_day_regime_conviction`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | `sig_product` | a=`high_low_sequence_momentum`, b=`vwap_trend_channel_slope` |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | `sig_product` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | `tri_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_trend` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__max_up_ret__volume_price_confirmation` | `rank_min` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, cond=`gap_pct` |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`bar_body_rng_0`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__max_up_ret__volume_price_confirmation` | `max` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_max__max_up_ret__first_bar_return` | `max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_min__max_up_ret__directional_volume_signature` | `rank_min` | a=`max_up_ret`, b=`directional_volume_signature` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | `ifelse` | a=`max_up_ret`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_min__bar_ret_0__volume_price_confirmation` | `min` | a=`bar_ret_0`, b=`volume_price_confirmation` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`yesterday_early_trend`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | `ifelse` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | `rel_diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_trend`, cond=`gap_pct` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | `max` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_min__bar_ret_0__directional_volume_signature` | `min` | a=`bar_ret_0`, b=`directional_volume_signature` |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__bar_ret_0` | `ifelse` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, cond=`gap_pct` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_diff__first_bar_return__volume_weighted_momentum_acceleration` | `diff` | a=`first_bar_return`, b=`volume_weighted_momentum_acceleration` |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | `ifelse` | a=`max_up_ret`, b=`first_bar_return`, cond=`gap_pct` |
| `combo_rel_diff__directional_volume_signature__early_late_momentum_divergence` | `rel_diff` | a=`directional_volume_signature`, b=`early_late_momentum_divergence` |
| `combo_z_sum__max_up_ret__rally_strength_max` | `z_sum` | a=`max_up_ret`, b=`rally_strength_max` |
| `combo_z_sum__volatility_expansion_trend_vector__volume_price_confirmation` | `z_sum` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_max__star50_limit_proximity_early__directional_volume_signature` | `max` | a=`star50_limit_proximity_early`, b=`directional_volume_signature` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`gap_pct` |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | `z_sum` | a=`first_bar_return`, b=`volume_weighted_price_position` |
