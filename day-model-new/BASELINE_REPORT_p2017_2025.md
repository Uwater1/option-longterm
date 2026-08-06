# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2017_2025`

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
| 300ETF | single | 1,798 | 638 | 517 | 334 | 329 | 329 | 272 | 272 | 35 | 34 | 14 | `[5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1]` |
| 300ETF | long | 585 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 587 | 69 | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | single | 985 | 186 | 111 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | long | 363 | 42 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | short | 320 | 42 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 4,744 | 2,228 | 1,927 | 1,694 | 1,691 | 1,635 | 1,542 | 1,540 | 100 | 100 | 44 | `[6, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, ... (44 clusters)]` |
| 500ETF | long | 1,347 | 119 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | short | 429 | 60 | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | single | 2,977 | 1,015 | 735 | 627 | 625 | 504 | 503 | 503 | 125 | 122 | 49 | `[9, 6, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3, ... (49 clusters)]` |
| 159915ETF | long | 1,118 | 180 | 117 | 117 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | short | 299 | 43 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 34 | 14 | `[5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1]` | +0.1093 | [+0.0659, +0.1524] | +0.2397 | [+0.1470, +0.3325] | +0.8182 | 5.89% | 1.6282 | 4.29% | 1.2071 | 2.6609 | 2.93% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 100 | 44 | `[6, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, ... (44 clusters)]` | +0.1561 | [+0.1122, +0.1975] | +0.2597 | [+0.1654, +0.3447] | +0.9758 | 7.19% | 1.6095 | 5.60% | 1.2694 | 2.5230 | 4.04% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 122 | 49 | `[9, 6, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3, ... (49 clusters)]` | +0.1465 | [+0.1052, +0.1891] | +0.3197 | [+0.2279, +0.4063] | +0.8061 | 9.56% | 1.8708 | 7.96% | 1.5801 | 3.8780 | 2.53% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 34 | 14 | `[5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1]` | +0.0161* | [-0.1204, +0.1153] | +0.0991* | [-0.2146, +0.3181] | +0.2848 | 1.28% | 0.4664 | -0.41% | -0.1486 | -0.2103 | 5.17% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 100 | 44 | `[6, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, ... (44 clusters)]` | +0.0742* | [-0.0507, +0.1634] | -0.0568* | [-0.2981, +0.1168] | +0.3576 | -1.22% | -0.3346 | -2.75% | -0.7499 | -0.9900 | 6.95% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 122 | 49 | `[9, 6, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3, ... (49 clusters)]` | +0.1437 | [+0.0034, +0.2426] | +0.1314* | [-0.1708, +0.3397] | +0.6000 | 7.14% | 1.2732 | 5.68% | 1.0213 | 1.8154 | 5.73% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 1 | +1 | +0.0996 | +0.2881 | +0.2875 | 0.0000 | +0.8325 | +0.7694 | 0.937 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 10 | +1 | +0.1035 | +0.2826 | +0.2824 | 0.0000 | +0.6965 | +0.7571 | 0.861 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 1 | +1 | +0.1012 | +0.2766 | +0.2766 | 0.0000 | +0.6959 | +0.7375 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 3 | +1 | +0.1003 | +0.2709 | +0.2714 | 0.0000 | +0.7164 | +0.7576 | 0.981 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 7 | +1 | +0.0875 | +0.2655 | +0.2657 | 0.0000 | +0.8219 | +0.7566 | 0.904 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.0996 | +0.2628 | +0.2633 | 0.0000 | +0.7808 | +0.7885 | 0.899 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 2 | +1 | +0.0864 | +0.2523 | +0.2529 | 0.0000 | +0.8743 | +0.8003 | 0.785 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Cluster 12 | +1 | +0.0936 | +0.2499 | +0.2501 | 0.0000 | +0.6698 | +0.7761 | 0.702 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | Cluster 10 | +1 | +0.0971 | +0.2430 | +0.2433 | 0.0000 | +0.7080 | +0.7560 | 0.947 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Cluster 5 | +1 | +0.0926 | +0.2384 | +0.2392 | 0.0000 | +0.6527 | +0.7391 | 0.908 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 10 | +1 | +0.0843 | +0.2365 | +0.2367 | 0.0000 | +0.5135 | +0.7097 | 0.932 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 13 | +1 | +0.0969 | +0.2333 | +0.2327 | 0.0000 | +0.6480 | +0.7916 | 0.941 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Cluster 4 | +1 | +0.0914 | +0.2318 | +0.2326 | 0.0000 | +0.8216 | +0.8029 | 0.936 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 9 | +1 | +0.0906 | +0.2309 | +0.2312 | 0.0000 | +0.7847 | +0.7571 | 0.922 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0852 | +0.2286 | +0.2287 | 0.0000 | +0.4841 | +0.6778 | 0.895 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 5 | +1 | +0.0901 | +0.2199 | +0.2204 | 0.0002 | +0.7998 | +0.7833 | 0.890 |
| `combo_tri_mean__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | Cluster 0 | +1 | +0.0953 | +0.2186 | +0.2190 | 0.0002 | +0.6989 | +0.7658 | 0.948 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 8 | +1 | +0.0956 | +0.2183 | +0.2179 | 0.0002 | +0.5874 | +0.7283 | 0.916 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | Cluster 3 | +1 | +0.0934 | +0.2167 | +0.2164 | 0.0002 | +0.7277 | +0.7442 | 0.908 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 7 | +1 | +0.0959 | +0.2163 | +0.2166 | 0.0002 | +0.6930 | +0.7277 | 0.944 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Cluster 4 | +1 | +0.0907 | +0.2155 | +0.2166 | 0.0002 | +0.5717 | +0.7138 | 0.927 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 9 | +1 | +0.0892 | +0.2147 | +0.2148 | 0.0002 | +0.7471 | +0.7617 | 0.873 |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | Cluster 11 | +1 | +0.0979 | +0.2124 | +0.2130 | 0.0002 | +0.7324 | +0.7787 | 0.923 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 2 | +1 | +0.0804 | +0.2119 | +0.2119 | 0.0002 | +0.6780 | +0.7545 | 0.945 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 0 | +1 | +0.0893 | +0.2095 | +0.2097 | 0.0002 | +0.7133 | +0.7499 | 0.882 |
| `max_up_ret` | Cluster 2 | +1 | +0.0742 | +0.2051 | +0.2056 | 0.0002 | +0.6225 | +0.7216 | 0.937 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 13 | +1 | +0.0963 | +0.2034 | +0.2025 | 0.0002 | +0.5403 | +0.7241 | 0.862 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 0 | +1 | +0.0905 | +0.2028 | +0.2027 | 0.0002 | +0.6456 | +0.7777 | 0.930 |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | Cluster 6 | +1 | +0.0767 | +0.2023 | +0.2029 | 0.0002 | +0.6274 | +0.7231 | 0.898 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 11 | +1 | +0.0847 | +0.1997 | +0.1998 | 0.0002 | +0.6211 | +0.6974 | 0.919 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 2 | +1 | +0.0885 | +0.1963 | +0.1971 | 0.0002 | +0.7102 | +0.7458 | 0.901 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0906 | +0.1946 | +0.1941 | 0.0002 | +0.5628 | +0.7118 | 0.949 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 10 | +1 | +0.0887 | +0.1882 | +0.1881 | 0.0002 | +0.4158 | +0.6722 | 0.946 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | Cluster 2 | +1 | +0.0750 | +0.1856 | +0.1856 | 0.0002 | +0.6871 | +0.7247 | 0.931 |

### 300ETF / long
No features admitted.

### 300ETF / short
No features admitted.

### 50ETF / single
No features admitted.

### 50ETF / long
No features admitted.

### 50ETF / short
No features admitted.

### 500ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 2 | +1 | +0.1315 | +0.2897 | +0.2885 | 0.0000 | +1.1021 | +0.8533 | 0.724 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 22 | +1 | +0.1545 | +0.2882 | +0.2875 | 0.0000 | +0.8177 | +0.7838 | 0.931 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 14 | +1 | +0.1474 | +0.2700 | +0.2690 | 0.0000 | +1.1888 | +0.8688 | 0.821 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 1 | +1 | +0.1361 | +0.2699 | +0.2686 | 0.0000 | +0.8517 | +0.7869 | 0.948 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 1 | +1 | +0.1453 | +0.2689 | +0.2675 | 0.0000 | +1.0684 | +0.8286 | 0.916 |
| `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 0 | +1 | +0.1382 | +0.2668 | +0.2654 | 0.0000 | +0.8524 | +0.8209 | 0.933 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 16 | +1 | +0.1279 | +0.2620 | +0.2617 | 0.0000 | +0.8071 | +0.7771 | 0.897 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__early_body_momentum` | Cluster 21 | +1 | +0.1115 | +0.2612 | +0.2599 | 0.0000 | +0.7989 | +0.7952 | 0.944 |
| `combo_mean__bar_ret_0__close_vs_open_range` | Cluster 13 | +1 | +0.1292 | +0.2594 | +0.2588 | 0.0000 | +0.9535 | +0.8183 | 0.896 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 37 | +1 | +0.1133 | +0.2588 | +0.2581 | 0.0000 | +0.8473 | +0.8250 | 0.920 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 41 | +1 | +0.1359 | +0.2578 | +0.2570 | 0.0000 | +0.9398 | +0.7998 | 0.919 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 6 | +1 | +0.1364 | +0.2577 | +0.2564 | 0.0000 | +0.8679 | +0.8080 | 0.918 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Cluster 6 | +1 | +0.1473 | +0.2573 | +0.2555 | 0.0000 | +0.6869 | +0.7524 | 0.866 |
| `combo_min__net_volume_flow__close_vs_open_range` | Cluster 37 | +1 | +0.1032 | +0.2540 | +0.2534 | 0.0000 | +0.7063 | +0.7679 | 0.872 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0` | Cluster 34 | +1 | +0.1213 | +0.2529 | +0.2522 | 0.0000 | +0.9934 | +0.8194 | 0.905 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 22 | +1 | +0.1473 | +0.2524 | +0.2516 | 0.0000 | +0.9968 | +0.8224 | 0.758 |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | Cluster 13 | +1 | +0.1282 | +0.2523 | +0.2515 | 0.0000 | +0.8768 | +0.7880 | 0.909 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 6 | +1 | +0.1404 | +0.2523 | +0.2504 | 0.0000 | +0.9815 | +0.8446 | 0.892 |
| `combo_mean__bar_ret_0__early_order_flow_imbalance` | Cluster 30 | +1 | +0.1218 | +0.2516 | +0.2518 | 0.0000 | +0.7376 | +0.7674 | 0.929 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Cluster 21 | +1 | +0.1131 | +0.2512 | +0.2503 | 0.0000 | +0.7318 | +0.7607 | 0.945 |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 21 | +1 | +0.1050 | +0.2502 | +0.2492 | 0.0000 | +0.7010 | +0.7581 | 0.937 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Cluster 15 | +1 | +0.1493 | +0.2499 | +0.2492 | 0.0000 | +0.8095 | +0.7864 | 0.938 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 6 | +1 | +0.1490 | +0.2488 | +0.2476 | 0.0000 | +0.8950 | +0.8266 | 0.916 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 33 | +1 | +0.1379 | +0.2481 | +0.2472 | 0.0000 | +0.9097 | +0.7849 | 0.928 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 10 | +1 | +0.1414 | +0.2469 | +0.2455 | 0.0000 | +0.6286 | +0.7087 | 0.786 |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 2 | +1 | +0.1151 | +0.2467 | +0.2454 | 0.0000 | +0.7822 | +0.7715 | 0.950 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Cluster 39 | +1 | +0.1334 | +0.2463 | +0.2457 | 0.0000 | +0.7197 | +0.7427 | 0.933 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 3 | +1 | +0.1402 | +0.2458 | +0.2455 | 0.0000 | +0.8210 | +0.7972 | 0.894 |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | Cluster 38 | +1 | +0.1329 | +0.2448 | +0.2443 | 0.0000 | +0.8047 | +0.7504 | 0.880 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Cluster 38 | +1 | +0.1223 | +0.2447 | +0.2444 | 0.0000 | +0.7819 | +0.7735 | 0.948 |
| `combo_tri_mean__max_up_ret__early_body_momentum__bar_ret_0` | Cluster 13 | +1 | +0.1327 | +0.2440 | +0.2432 | 0.0000 | +0.7072 | +0.7478 | 0.944 |
| `combo_min__net_volume_flow__bar_body_rng_0` | Cluster 11 | +1 | +0.1168 | +0.2439 | +0.2441 | 0.0000 | +0.6540 | +0.7257 | 0.920 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Cluster 35 | +1 | +0.1439 | +0.2433 | +0.2421 | 0.0000 | +0.7315 | +0.7715 | 0.000 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Cluster 21 | +1 | +0.1055 | +0.2432 | +0.2416 | 0.0000 | +0.7688 | +0.7560 | 0.920 |
| `combo_rank_max__bar_ret_0__close_vs_open_range` | Cluster 38 | +1 | +0.1373 | +0.2430 | +0.2424 | 0.0000 | +1.0065 | +0.8528 | 0.888 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 22 | +1 | +0.1540 | +0.2424 | +0.2416 | 0.0000 | +0.9301 | +0.8111 | 0.945 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 34 | +1 | +0.1246 | +0.2415 | +0.2406 | 0.0000 | +0.6617 | +0.7077 | 0.915 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 3 | +1 | +0.1336 | +0.2409 | +0.2406 | 0.0000 | +0.8543 | +0.8255 | 0.933 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Cluster 18 | +1 | +0.1523 | +0.2406 | +0.2401 | 0.0000 | +0.8455 | +0.7771 | 0.903 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 23 | +1 | +0.1375 | +0.2403 | +0.2389 | 0.0000 | +0.8854 | +0.8101 | 0.945 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 20 | +1 | +0.1386 | +0.2387 | +0.2377 | 0.0000 | +0.9187 | +0.8214 | 0.935 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 21 | +1 | +0.1144 | +0.2385 | +0.2369 | 0.0000 | +0.7321 | +0.7813 | 0.915 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Cluster 40 | +1 | +0.1315 | +0.2381 | +0.2375 | 0.0000 | +0.7025 | +0.7694 | 0.947 |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 18 | +1 | +0.1434 | +0.2379 | +0.2378 | 0.0000 | +0.7315 | +0.7380 | 0.940 |
| `combo_tri_mean__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | Cluster 37 | +1 | +0.1183 | +0.2370 | +0.2365 | 0.0000 | +0.5969 | +0.7540 | 0.947 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 19 | +1 | +0.1578 | +0.2369 | +0.2361 | 0.0000 | +0.7626 | +0.8013 | 0.924 |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | Cluster 30 | +1 | +0.1241 | +0.2361 | +0.2364 | 0.0000 | +0.6850 | +0.7571 | 0.805 |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__bar_ret_0` | Cluster 38 | +1 | +0.1253 | +0.2354 | +0.2348 | 0.0000 | +0.8472 | +0.8091 | 0.948 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 23 | +1 | +0.1382 | +0.2353 | +0.2343 | 0.0000 | +0.8256 | +0.8091 | 0.927 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 16 | +1 | +0.1329 | +0.2351 | +0.2348 | 0.0000 | +0.8038 | +0.7880 | 0.835 |
| `combo_rank_max__max_up_ret__net_volume_flow` | Cluster 41 | +1 | +0.1288 | +0.2350 | +0.2339 | 0.0000 | +0.7221 | +0.7385 | 0.927 |
| `combo_min__first_bar_return__early_order_flow_imbalance` | Cluster 30 | +1 | +0.1213 | +0.2335 | +0.2334 | 0.0000 | +0.7416 | +0.7427 | 0.921 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 10 | +1 | +0.1330 | +0.2334 | +0.2321 | 0.0000 | +0.5792 | +0.7066 | 0.908 |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | Cluster 35 | +1 | +0.1404 | +0.2310 | +0.2299 | 0.0000 | +0.7030 | +0.7607 | 0.861 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 3 | +1 | +0.1353 | +0.2306 | +0.2300 | 0.0000 | +0.8583 | +0.8173 | 0.909 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 25 | +1 | +0.1447 | +0.2303 | +0.2293 | 0.0000 | +0.9868 | +0.8549 | 0.940 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 36 | +1 | +0.1501 | +0.2298 | +0.2285 | 0.0000 | +0.8171 | +0.7921 | 0.942 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 39 | +1 | +0.1404 | +0.2281 | +0.2271 | 0.0000 | +0.9676 | +0.8096 | 0.928 |
| `combo_clamp_diff__first_bar_return__body_size_progression` | Cluster 5 | +1 | +0.1306 | +0.2269 | +0.2269 | 0.0000 | +0.6421 | +0.7200 | 0.855 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 36 | +1 | +0.1463 | +0.2255 | +0.2236 | 0.0000 | +0.7254 | +0.7411 | 0.935 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 21 | +1 | +0.1188 | +0.2252 | +0.2238 | 0.0000 | +0.7435 | +0.7571 | 0.866 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Cluster 41 | +1 | +0.1418 | +0.2216 | +0.2203 | 0.0000 | +0.8203 | +0.7524 | 0.934 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 17 | +1 | +0.1546 | +0.2198 | +0.2185 | 0.0000 | +0.7011 | +0.7262 | 0.911 |
| `combo_mean__first_bar_return__max_down_ret` | Cluster 12 | +1 | +0.1199 | +0.2194 | +0.2195 | 0.0000 | +0.7236 | +0.7396 | 0.929 |
| `combo_mean__max_up_ret__first_bar_return` | Cluster 3 | +1 | +0.1375 | +0.2184 | +0.2177 | 0.0000 | +0.6775 | +0.7452 | 0.942 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 10 | +1 | +0.1329 | +0.2181 | +0.2169 | 0.0000 | +0.5428 | +0.6943 | 0.940 |
| `combo_rank_min__net_volume_flow__vwap_close_divergence_trend` | Cluster 37 | +1 | +0.1055 | +0.2179 | +0.2177 | 0.0000 | +0.5735 | +0.7005 | 0.910 |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | Cluster 13 | +1 | +0.1285 | +0.2166 | +0.2163 | 0.0000 | +0.6584 | +0.7174 | 0.933 |
| `combo_mean__max_up_ret__close_vs_open_range` | Cluster 26 | +1 | +0.1276 | +0.2162 | +0.2150 | 0.0000 | +0.8206 | +0.7777 | 0.947 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | Cluster 32 | +1 | +0.1154 | +0.2159 | +0.2145 | 0.0000 | +0.6088 | +0.7262 | 0.801 |
| `combo_mean__first_bar_return__bar_body_rng_0` | Cluster 11 | +1 | +0.1185 | +0.2148 | +0.2153 | 0.0000 | +0.6798 | +0.7437 | 0.915 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | Cluster 6 | +1 | +0.1403 | +0.2145 | +0.2134 | 0.0000 | +0.7437 | +0.7684 | 0.949 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 25 | +1 | +0.1526 | +0.2127 | +0.2112 | 0.0000 | +0.7040 | +0.7710 | 0.929 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 25 | +1 | +0.1512 | +0.2120 | +0.2108 | 0.0000 | +0.7433 | +0.7607 | 0.927 |
| `combo_mean__max_up_ret__max_down_ret` | Cluster 14 | +1 | +0.1372 | +0.2117 | +0.2107 | 0.0000 | +0.7372 | +0.7401 | 0.911 |
| `combo_max__max_up_ret__max_down_ret` | Cluster 42 | +1 | +0.1352 | +0.2098 | +0.2091 | 0.0000 | +0.8223 | +0.7833 | 0.898 |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | Cluster 29 | +1 | +0.1250 | +0.2071 | +0.2061 | 0.0000 | +0.8287 | +0.7859 | 0.949 |
| `combo_rank_max__max_up_ret__max_down_ret` | Cluster 42 | +1 | +0.1341 | +0.2062 | +0.2054 | 0.0000 | +0.8021 | +0.7946 | 0.918 |
| `combo_max__bar_ret_0__max_down_ret` | Cluster 12 | +1 | +0.1301 | +0.2053 | +0.2054 | 0.0000 | +0.7967 | +0.7766 | 0.857 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 17 | +1 | +0.1425 | +0.2052 | +0.2045 | 0.0000 | +0.5864 | +0.7200 | 0.950 |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Cluster 38 | +1 | +0.1305 | +0.2046 | +0.2042 | 0.0000 | +0.8361 | +0.7864 | 0.922 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | Cluster 32 | +1 | +0.1153 | +0.2043 | +0.2028 | 0.0000 | +0.5608 | +0.7185 | 0.936 |
| `combo_max__max_up_ret__close_vs_open_range` | Cluster 26 | +1 | +0.1336 | +0.2013 | +0.2001 | 0.0000 | +0.6961 | +0.7494 | 0.928 |
| `max_up_ret` | Cluster 25 | +1 | +0.1323 | +0.2006 | +0.1991 | 0.0000 | +0.6170 | +0.7216 | 0.910 |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | Cluster 38 | +1 | +0.1306 | +0.1999 | +0.1994 | 0.0000 | +0.7956 | +0.7823 | 0.913 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 25 | +1 | +0.1289 | +0.1993 | +0.1979 | 0.0000 | +0.5715 | +0.7010 | 0.927 |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 28 | +1 | +0.1157 | +0.1950 | +0.1938 | 0.0000 | +0.5741 | +0.6861 | 0.925 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | Cluster 27 | +1 | +0.1341 | +0.1943 | +0.1932 | 0.0000 | +0.8175 | +0.7627 | 0.913 |
| `combo_tri_median__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | Cluster 23 | +1 | +0.1308 | +0.1919 | +0.1911 | 0.0000 | +0.7340 | +0.7720 | 0.941 |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | Cluster 43 | +1 | +0.1161 | +0.1899 | +0.1889 | 0.0000 | +0.6130 | +0.7422 | 0.714 |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Cluster 27 | +1 | +0.1323 | +0.1896 | +0.1885 | 0.0000 | +0.8641 | +0.7679 | 0.943 |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | Cluster 8 | +1 | +0.1042 | +0.1879 | +0.1873 | 0.0000 | +0.6664 | +0.7221 | 0.891 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | Cluster 7 | +1 | +0.1108 | +0.1876 | +0.1864 | 0.0000 | +0.5775 | +0.6773 | 0.860 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 4 | +1 | +0.1380 | +0.1841 | +0.1827 | 0.0002 | +0.5099 | +0.6953 | 0.945 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 16 | +1 | +0.0954 | +0.1833 | +0.1822 | 0.0002 | +0.6465 | +0.7169 | 0.847 |
| `combo_mean__first_bar_return__shaved_bar_trend_conviction` | Cluster 24 | +1 | +0.1024 | +0.1832 | +0.1827 | 0.0002 | +0.5514 | +0.6763 | 0.908 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Cluster 31 | +1 | +0.1186 | +0.1819 | +0.1803 | 0.0002 | +0.4240 | +0.6696 | 0.611 |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | Cluster 8 | +1 | +0.0845 | +0.1654 | +0.1646 | 0.0014 | +0.6425 | +0.7154 | 0.930 |
| `combo_sig_product__net_volume_flow__vwap_close_divergence_trend` | Cluster 8 | +1 | +0.1018 | +0.1604 | +0.1593 | 0.0020 | +0.6621 | +0.7128 | 0.904 |
| `num_up_bars` | Cluster 9 | +1 | +0.0907 | +0.1213 | +0.1198 | 0.0144 | +0.3576 | +0.6531 | 0.799 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 3 | +1 | +0.1386 | +0.3801 | +0.3803 | 0.0000 | +1.2371 | +0.8770 | 0.000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 2 | +1 | +0.1387 | +0.3394 | +0.3392 | 0.0000 | +0.9307 | +0.8065 | 0.919 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 22 | +1 | +0.1413 | +0.3360 | +0.3352 | 0.0000 | +1.0526 | +0.8322 | 0.873 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 22 | +1 | +0.1407 | +0.3352 | +0.3344 | 0.0000 | +1.2363 | +0.8852 | 0.950 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 3 | +1 | +0.1324 | +0.3315 | +0.3315 | 0.0000 | +1.0386 | +0.8384 | 0.947 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 13 | +1 | +0.1256 | +0.3197 | +0.3193 | 0.0000 | +1.0333 | +0.8435 | 0.780 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 27 | +1 | +0.1374 | +0.3174 | +0.3167 | 0.0000 | +0.7667 | +0.7658 | 0.845 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 13 | +1 | +0.1268 | +0.3122 | +0.3118 | 0.0000 | +0.9771 | +0.8235 | 0.926 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 1 | +1 | +0.1207 | +0.3064 | +0.3065 | 0.0000 | +0.9346 | +0.8250 | 0.936 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 2 | +1 | +0.1335 | +0.3040 | +0.3035 | 0.0000 | +0.8353 | +0.7766 | 0.944 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 21 | +1 | +0.1057 | +0.2931 | +0.2931 | 0.0000 | +0.8018 | +0.7766 | 0.859 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 43 | +1 | +0.1369 | +0.2925 | +0.2914 | 0.0000 | +0.7572 | +0.7679 | 0.944 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 1 | +1 | +0.1165 | +0.2920 | +0.2917 | 0.0000 | +0.7272 | +0.7391 | 0.939 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 19 | +1 | +0.1385 | +0.2890 | +0.2872 | 0.0000 | +0.8075 | +0.7818 | 0.876 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.1120 | +0.2889 | +0.2884 | 0.0000 | +0.7581 | +0.7633 | 0.931 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 11 | +1 | +0.1332 | +0.2885 | +0.2871 | 0.0000 | +0.9380 | +0.8039 | 0.937 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 43 | +1 | +0.1364 | +0.2881 | +0.2871 | 0.0000 | +0.8502 | +0.7890 | 0.901 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 28 | +1 | +0.1329 | +0.2864 | +0.2852 | 0.0000 | +0.8006 | +0.7777 | 0.942 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 43 | +1 | +0.1289 | +0.2854 | +0.2851 | 0.0000 | +0.7943 | +0.8049 | 0.942 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 23 | +1 | +0.1316 | +0.2847 | +0.2837 | 0.0000 | +0.9684 | +0.8322 | 0.929 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 2 | +1 | +0.1304 | +0.2847 | +0.2842 | 0.0000 | +0.8442 | +0.8085 | 0.937 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | Cluster 31 | +1 | +0.1097 | +0.2836 | +0.2837 | 0.0000 | +0.7036 | +0.7524 | 0.831 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 1 | +1 | +0.1091 | +0.2819 | +0.2822 | 0.0000 | +0.7058 | +0.7488 | 1.000 |
| `combo_min__volume_weighted_price_position__limit_down_proximity_early` | Cluster 42 | +1 | +0.0981 | +0.2796 | +0.2799 | 0.0000 | +0.8639 | +0.8070 | 0.872 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 41 | +1 | +0.1165 | +0.2780 | +0.2763 | 0.0000 | +0.9388 | +0.8338 | 0.948 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 21 | +1 | +0.1146 | +0.2774 | +0.2769 | 0.0000 | +0.7870 | +0.7931 | 0.901 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 41 | +1 | +0.1133 | +0.2769 | +0.2751 | 0.0000 | +0.8994 | +0.8415 | 0.865 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 15 | +1 | +0.1490 | +0.2691 | +0.2682 | 0.0000 | +0.6875 | +0.7303 | 0.766 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 32 | +1 | +0.1161 | +0.2666 | +0.2649 | 0.0000 | +0.8949 | +0.8291 | 0.892 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 44 | +1 | +0.1282 | +0.2638 | +0.2625 | 0.0000 | +1.0263 | +0.8435 | 0.926 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 19 | +1 | +0.1375 | +0.2636 | +0.2619 | 0.0000 | +0.9520 | +0.8260 | 0.917 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 11 | +1 | +0.1322 | +0.2593 | +0.2579 | 0.0000 | +0.8587 | +0.7895 | 0.939 |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 32 | +1 | +0.1174 | +0.2577 | +0.2562 | 0.0000 | +0.8017 | +0.7761 | 0.831 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 37 | +1 | +0.1186 | +0.2553 | +0.2560 | 0.0000 | +0.7522 | +0.7838 | 0.879 |
| `combo_mean__volume_weighted_price_position__rbreaker_buy_setup_proximity_early` | Cluster 12 | +1 | +0.1118 | +0.2549 | +0.2555 | 0.0000 | +0.6829 | +0.7473 | 0.917 |
| `combo_mean__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 32 | +1 | +0.1211 | +0.2537 | +0.2521 | 0.0000 | +0.6770 | +0.7056 | 0.859 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 12 | +1 | +0.1362 | +0.2533 | +0.2532 | 0.0000 | +0.8112 | +0.7694 | 0.845 |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Cluster 31 | +1 | +0.1140 | +0.2515 | +0.2510 | 0.0000 | +0.6486 | +0.7144 | 0.795 |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 15 | +1 | +0.1434 | +0.2512 | +0.2503 | 0.0000 | +0.5992 | +0.7164 | 0.944 |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | Cluster 42 | +1 | +0.0954 | +0.2498 | +0.2501 | 0.0000 | +0.7952 | +0.7735 | 0.879 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | Cluster 5 | +1 | +0.0924 | +0.2482 | +0.2482 | 0.0000 | +0.6604 | +0.7694 | 0.940 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 9 | +1 | +0.1187 | +0.2480 | +0.2465 | 0.0000 | +0.7656 | +0.7777 | 0.886 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 30 | +1 | +0.1064 | +0.2480 | +0.2489 | 0.0000 | +0.6380 | +0.7221 | 0.849 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 15 | +1 | +0.1426 | +0.2476 | +0.2467 | 0.0000 | +0.6039 | +0.7241 | 0.921 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | Cluster 1 | +1 | +0.1016 | +0.2469 | +0.2472 | 0.0000 | +0.6897 | +0.7447 | 1.000 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0996 | +0.2468 | +0.2472 | 0.0000 | +0.7183 | +0.7838 | 0.935 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 35 | +1 | +0.1172 | +0.2466 | +0.2467 | 0.0000 | +0.7524 | +0.7560 | 0.914 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Cluster 10 | +1 | +0.1331 | +0.2459 | +0.2439 | 0.0000 | +0.6629 | +0.7524 | 0.943 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Cluster 35 | +1 | +0.1101 | +0.2457 | +0.2456 | 0.0000 | +0.7346 | +0.7612 | 0.932 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 8 | +1 | +0.1219 | +0.2452 | +0.2443 | 0.0000 | +0.7611 | +0.7674 | 0.822 |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | Cluster 47 | +1 | +0.0978 | +0.2444 | +0.2446 | 0.0000 | +0.6709 | +0.7643 | 0.824 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 44 | +1 | +0.1182 | +0.2438 | +0.2433 | 0.0000 | +0.9986 | +0.8147 | 0.944 |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | Cluster 43 | +1 | +0.1184 | +0.2434 | +0.2430 | 0.0000 | +0.6100 | +0.7427 | 0.944 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 27 | +1 | +0.1172 | +0.2433 | +0.2432 | 0.0000 | +0.6826 | +0.7437 | 0.941 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 8 | +1 | +0.1215 | +0.2413 | +0.2405 | 0.0000 | +0.7630 | +0.7627 | 0.920 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Cluster 30 | +1 | +0.1158 | +0.2401 | +0.2408 | 0.0000 | +0.6555 | +0.7118 | 0.912 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | Cluster 15 | +1 | +0.1350 | +0.2401 | +0.2391 | 0.0000 | +0.4433 | +0.6526 | 0.917 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Cluster 31 | +1 | +0.1096 | +0.2390 | +0.2386 | 0.0000 | +0.6116 | +0.7102 | 0.919 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 33 | +1 | +0.1115 | +0.2387 | +0.2388 | 0.0000 | +0.6329 | +0.7272 | 0.927 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 6 | +1 | +0.0917 | +0.2380 | +0.2374 | 0.0000 | +0.7177 | +0.7828 | 0.896 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 9 | +1 | +0.1185 | +0.2367 | +0.2353 | 0.0000 | +0.7438 | +0.7741 | 0.911 |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Cluster 15 | +1 | +0.1205 | +0.2363 | +0.2352 | 0.0000 | +0.5719 | +0.7226 | 0.886 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 41 | +1 | +0.1188 | +0.2358 | +0.2340 | 0.0000 | +0.7567 | +0.7458 | 0.930 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 26 | +1 | +0.1152 | +0.2356 | +0.2340 | 0.0000 | +0.8327 | +0.7890 | 0.794 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 44 | +1 | +0.1182 | +0.2351 | +0.2346 | 0.0000 | +0.7805 | +0.7550 | 0.946 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | Cluster 7 | +1 | +0.1077 | +0.2344 | +0.2339 | 0.0000 | +0.8870 | +0.8075 | 0.933 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 28 | +1 | +0.1235 | +0.2326 | +0.2319 | 0.0000 | +0.7852 | +0.8003 | 0.911 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 27 | +1 | +0.1239 | +0.2322 | +0.2318 | 0.0000 | +0.8503 | +0.7926 | 0.916 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 30 | +1 | +0.1175 | +0.2313 | +0.2317 | 0.0000 | +0.6298 | +0.7005 | 0.847 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 44 | +1 | +0.1208 | +0.2299 | +0.2298 | 0.0000 | +0.6544 | +0.7247 | 0.941 |
| `combo_max__max_up_ret__volume_price_confirmation` | Cluster 29 | +1 | +0.1149 | +0.2299 | +0.2306 | 0.0000 | +0.8111 | +0.7694 | 0.881 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 5 | +1 | +0.1104 | +0.2297 | +0.2299 | 0.0000 | +0.7790 | +0.8065 | 0.362 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | Cluster 20 | +1 | +0.1169 | +0.2280 | +0.2264 | 0.0000 | +0.5884 | +0.7473 | 0.942 |
| `combo_rank_min__max_up_ret__gap_pct` | Cluster 25 | +1 | +0.1030 | +0.2276 | +0.2265 | 0.0000 | +0.7503 | +0.7844 | 0.814 |
| `combo_max__max_up_ret__rally_strength_max` | Cluster 48 | +1 | +0.0915 | +0.2262 | +0.2255 | 0.0000 | +0.6197 | +0.7216 | 0.843 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 29 | +1 | +0.1207 | +0.2233 | +0.2230 | 0.0000 | +0.8404 | +0.7694 | 0.835 |
| `combo_clamp_diff__volume_weighted_price_position__body_size_progression` | Cluster 46 | +1 | +0.1006 | +0.2219 | +0.2236 | 0.0000 | +0.3863 | +0.6588 | 0.839 |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | Cluster 29 | +1 | +0.1130 | +0.2214 | +0.2220 | 0.0000 | +0.5924 | +0.6938 | 0.923 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Cluster 15 | +1 | +0.1353 | +0.2195 | +0.2187 | 0.0000 | +0.4737 | +0.6619 | 0.894 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 29 | +1 | +0.1210 | +0.2190 | +0.2189 | 0.0000 | +0.8299 | +0.7597 | 0.933 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | Cluster 5 | +1 | +0.0961 | +0.2173 | +0.2164 | 0.0000 | +0.3589 | +0.6505 | 0.791 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 45 | +1 | +0.1112 | +0.2167 | +0.2161 | 0.0000 | +0.7488 | +0.7422 | 0.917 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 34 | +1 | +0.1124 | +0.2165 | +0.2165 | 0.0000 | +0.5730 | +0.7221 | 0.943 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 5 | +1 | +0.1050 | +0.2163 | +0.2151 | 0.0000 | +0.5095 | +0.7267 | 0.806 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__bar_ret_0` | Cluster 17 | +1 | +0.1149 | +0.2151 | +0.2159 | 0.0000 | +0.4981 | +0.6850 | 0.916 |
| `combo_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | Cluster 15 | +1 | +0.1276 | +0.2143 | +0.2134 | 0.0000 | +0.3547 | +0.6516 | 0.886 |
| `combo_tri_mean__opening_drive_thrust_ratio__demark_setup_reversal_early__star50_limit_proximity_early` | Cluster 46 | +1 | +0.1118 | +0.2137 | +0.2129 | 0.0000 | +0.5595 | +0.7010 | 0.813 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | Cluster 14 | +1 | +0.0972 | +0.2116 | +0.2104 | 0.0000 | +0.5083 | +0.6943 | 0.643 |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 29 | +1 | +0.1083 | +0.2105 | +0.2107 | 0.0000 | +0.5713 | +0.6933 | 0.835 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Cluster 6 | +1 | +0.1037 | +0.2087 | +0.2078 | 0.0000 | +1.0254 | +0.8173 | 0.922 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Cluster 6 | +1 | +0.1040 | +0.2064 | +0.2048 | 0.0000 | +0.7689 | +0.7643 | 0.941 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 41 | +1 | +0.1013 | +0.2057 | +0.2041 | 0.0000 | +0.7372 | +0.7699 | 0.927 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Cluster 40 | +1 | +0.1159 | +0.2039 | +0.2024 | 0.0000 | +0.7503 | +0.7231 | 0.901 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 4 | +1 | +0.1171 | +0.2034 | +0.2027 | 0.0000 | +0.6135 | +0.7308 | 0.927 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | Cluster 15 | +1 | +0.1292 | +0.2033 | +0.2024 | 0.0000 | +0.3656 | +0.6619 | 0.915 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 4 | +1 | +0.1181 | +0.2031 | +0.2023 | 0.0000 | +0.4827 | +0.6788 | 0.888 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | Cluster 18 | +1 | +0.1064 | +0.2029 | +0.2030 | 0.0000 | +0.5683 | +0.7041 | 0.809 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 4 | +1 | +0.1249 | +0.2001 | +0.1990 | 0.0000 | +0.6117 | +0.7108 | 0.873 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | Cluster 14 | +1 | +0.1001 | +0.1969 | +0.1959 | 0.0000 | +0.5736 | +0.6948 | 0.940 |
| `combo_rank_min__max_up_ret__rally_strength_max` | Cluster 47 | +1 | +0.0965 | +0.1964 | +0.1959 | 0.0000 | +0.6970 | +0.7833 | 0.884 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 7 | +1 | +0.1159 | +0.1947 | +0.1949 | 0.0002 | +0.8814 | +0.8127 | 0.902 |
| `combo_max__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 48 | +1 | +0.0989 | +0.1943 | +0.1936 | 0.0002 | +0.4773 | +0.6670 | 0.854 |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | Cluster 36 | +1 | +0.1093 | +0.1936 | +0.1931 | 0.0002 | +0.5769 | +0.7144 | 0.898 |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | Cluster 14 | +1 | +0.0995 | +0.1917 | +0.1907 | 0.0002 | +0.5482 | +0.6861 | 0.933 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Cluster 24 | +1 | +0.1233 | +0.1916 | +0.1896 | 0.0002 | +0.5834 | +0.7133 | 0.855 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Cluster 4 | +1 | +0.1145 | +0.1891 | +0.1883 | 0.0004 | +0.5569 | +0.6994 | 0.888 |
| `combo_mean__max_up_ret__volume_price_confirmation` | Cluster 29 | +1 | +0.1170 | +0.1889 | +0.1892 | 0.0004 | +0.5403 | +0.6855 | 0.944 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 39 | +1 | +0.1210 | +0.1889 | +0.1875 | 0.0004 | +0.4934 | +0.6897 | 0.938 |
| `combo_rank_max__star50_limit_proximity_early__volume_price_confirmation` | Cluster 15 | +1 | +0.1177 | +0.1884 | +0.1876 | 0.0004 | +0.5262 | +0.6572 | 0.832 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 39 | +1 | +0.1127 | +0.1878 | +0.1863 | 0.0004 | +0.5725 | +0.6814 | 0.873 |
| `combo_min__max_up_ret__gap_pct` | Cluster 25 | +1 | +0.1058 | +0.1870 | +0.1853 | 0.0004 | +0.5404 | +0.6814 | 0.860 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 39 | +1 | +0.1175 | +0.1865 | +0.1852 | 0.0004 | +0.5493 | +0.6861 | 0.944 |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | Cluster 6 | +1 | +0.0954 | +0.1858 | +0.1848 | 0.0004 | +0.6188 | +0.7195 | 0.869 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 26 | +1 | +0.1429 | +0.1852 | +0.1839 | 0.0004 | +0.5265 | +0.6794 | 0.668 |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | Cluster 31 | +1 | +0.0863 | +0.1836 | +0.1843 | 0.0004 | +0.4572 | +0.6613 | 1.000 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 40 | +1 | +0.1151 | +0.1828 | +0.1810 | 0.0004 | +0.6629 | +0.7174 | 0.947 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Cluster 24 | +1 | +0.1120 | +0.1819 | +0.1803 | 0.0004 | +0.4602 | +0.6799 | 0.768 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 33 | +1 | +0.1133 | +0.1777 | +0.1777 | 0.0010 | +0.4930 | +0.6552 | 0.936 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 34 | +1 | +0.1051 | +0.1748 | +0.1745 | 0.0012 | +0.6039 | +0.7597 | 0.919 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 38 | +1 | +0.1070 | +0.1709 | +0.1697 | 0.0012 | +0.4793 | +0.6747 | 0.908 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Cluster 17 | +1 | +0.1064 | +0.1602 | +0.1611 | 0.0022 | +0.5019 | +0.7298 | 0.811 |
| `combo_min__bar_ret_0__directional_volume_signature` | Cluster 16 | +1 | +0.0967 | +0.1572 | +0.1579 | 0.0026 | +0.5853 | +0.7283 | 0.844 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

### Cluster Overview per ETF / Side

| ETF | Side | Total Features | Clusters | Avg Silhouette | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 300ETF | single | 34 | 14 | 0.2806 | `[5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1]` |
| 500ETF | single | 100 | 44 | 0.2085 | `[6, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, ... (44 clusters)]` |
| 159915ETF | single | 122 | 49 | 0.3293 | `[9, 6, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3, ... (49 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 3 | 0.2806 | `combo_tri_mean__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 1 | 4 | 0.2806 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 2 | 5 | 0.2806 | `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`, `max_up_ret`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration`, `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 300ETF | single | Cluster 3 | 3 | 0.2806 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 4 | 2 | 0.2806 | `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | `combo_rank_max__bar_ret_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 5 | 2 | 0.2806 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 6 | 1 | 0.2806 | `combo_max__bar_ret_0__morning_volume_weighted_momentum` | _(none)_ |
| 300ETF | single | Cluster 7 | 2 | 0.2806 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_mean__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 8 | 1 | 0.2806 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | _(none)_ |
| 300ETF | single | Cluster 9 | 2 | 0.2806 | `combo_max__max_up_ret__bar_ret_0` | `combo_rank_max__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 10 | 4 | 0.2806 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 11 | 2 | 0.2806 | `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 12 | 1 | 0.2806 | `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 13 | 2 | 0.2806 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` |
| 500ETF | single | Cluster 0 | 1 | 0.2085 | `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 1 | 2 | 0.2085 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 2 | 2 | 0.2085 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` |
| 500ETF | single | Cluster 3 | 4 | 0.2085 | `combo_mean__max_up_ret__bar_body_rng_0` | `combo_mean__max_up_ret__first_bar_return`, `combo_min__max_up_ret__bar_body_rng_0`, `combo_rank_max__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 4 | 1 | 0.2085 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 5 | 1 | 0.2085 | `combo_clamp_diff__first_bar_return__body_size_progression` | _(none)_ |
| 500ETF | single | Cluster 6 | 5 | 0.2085 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`, `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_clamp_diff__max_up_ret__demark_setup_reversal_early`, `combo_tri_median__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` |
| 500ETF | single | Cluster 7 | 1 | 0.2085 | `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 8 | 3 | 0.2085 | `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend`, `combo_sig_product__net_volume_flow__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 9 | 1 | 0.2085 | `num_up_bars` | _(none)_ |
| 500ETF | single | Cluster 10 | 3 | 0.2085 | `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 11 | 2 | 0.2085 | `combo_min__net_volume_flow__bar_body_rng_0` | `combo_mean__first_bar_return__bar_body_rng_0` |
| 500ETF | single | Cluster 12 | 2 | 0.2085 | `combo_max__bar_ret_0__max_down_ret` | `combo_mean__first_bar_return__max_down_ret` |
| 500ETF | single | Cluster 13 | 4 | 0.2085 | `combo_mean__bar_ret_0__close_vs_open_range` | `combo_tri_mean__max_up_ret__early_body_momentum__bar_ret_0`, `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0`, `combo_mean__bar_ret_0__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 14 | 2 | 0.2085 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `combo_mean__max_up_ret__max_down_ret` |
| 500ETF | single | Cluster 15 | 1 | 0.2085 | `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 16 | 3 | 0.2085 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_mean__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 17 | 2 | 0.2085 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 18 | 2 | 0.2085 | `combo_mean__opening_drive_thrust_ratio__first_bar_return` | `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` |
| 500ETF | single | Cluster 19 | 1 | 0.2085 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 20 | 1 | 0.2085 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 21 | 6 | 0.2085 | `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`, `combo_min__net_volume_flow__star50_limit_proximity_early`, `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__early_body_momentum`, `combo_mean__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 22 | 3 | 0.2085 | `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 23 | 3 | 0.2085 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`, `combo_tri_median__early_body_momentum__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 24 | 1 | 0.2085 | `combo_mean__first_bar_return__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 25 | 5 | 0.2085 | `max_up_ret` | `combo_min__opening_drive_thrust_ratio__max_up_ret`, `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` |
| 500ETF | single | Cluster 26 | 2 | 0.2085 | `combo_max__max_up_ret__close_vs_open_range` | `combo_mean__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 27 | 2 | 0.2085 | `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | `combo_max__max_up_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 28 | 1 | 0.2085 | `combo_diff__max_up_ret__h2_l2_pullback_continuation` | _(none)_ |
| 500ETF | single | Cluster 29 | 1 | 0.2085 | `combo_mean__max_up_ret__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 30 | 3 | 0.2085 | `combo_min__early_order_flow_imbalance__bar_body_rng_0` | `combo_min__first_bar_return__early_order_flow_imbalance`, `combo_mean__bar_ret_0__early_order_flow_imbalance` |
| 500ETF | single | Cluster 31 | 1 | 0.2085 | `combo_sig_product__star50_limit_proximity_early__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 32 | 2 | 0.2085 | `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | `combo_diff__star50_limit_proximity_early__body_size_progression` |
| 500ETF | single | Cluster 33 | 1 | 0.2085 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 34 | 2 | 0.2085 | `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 35 | 2 | 0.2085 | `combo_diff__first_bar_return__demark_setup_reversal_early` | `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` |
| 500ETF | single | Cluster 36 | 2 | 0.2085 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 37 | 4 | 0.2085 | `combo_min__net_volume_flow__close_vs_open_range` | `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_tri_mean__early_body_momentum__trend_day_regime_conviction__bar_ret_0`, `combo_rank_min__net_volume_flow__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 38 | 6 | 0.2085 | `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__bar_ret_0`, `combo_rank_max__bar_ret_0__close_vs_open_range`, `combo_rank_max__early_body_momentum__bar_ret_0`, `combo_rank_max__bar_ret_0__vwap_close_divergence_trend`, `combo_max__first_bar_return__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 39 | 2 | 0.2085 | `combo_diff__max_up_ret__body_size_progression` | `combo_clamp_diff__max_up_ret__late_bar_momentum` |
| 500ETF | single | Cluster 40 | 1 | 0.2085 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | _(none)_ |
| 500ETF | single | Cluster 41 | 3 | 0.2085 | `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_rank_max__max_up_ret__net_volume_flow`, `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` |
| 500ETF | single | Cluster 42 | 2 | 0.2085 | `combo_max__max_up_ret__max_down_ret` | `combo_rank_max__max_up_ret__max_down_ret` |
| 500ETF | single | Cluster 43 | 1 | 0.2085 | `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | _(none)_ |
| 159915ETF | single | Cluster 0 | 1 | 0.3293 | `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 1 | 5 | 0.3293 | `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `combo_min__bar_body_rng_0__limit_down_proximity_early`, `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_min__bar_ret_0__limit_down_proximity_early` |
| 159915ETF | single | Cluster 2 | 3 | 0.3293 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 3 | 2 | 0.3293 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` |
| 159915ETF | single | Cluster 4 | 4 | 0.3293 | `combo_max__star50_limit_proximity_early__bar_ret_0` | `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return`, `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 5 | 4 | 0.3293 | `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`, `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 6 | 4 | 0.3293 | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `combo_rank_min__max_up_ret__volatility_expansion_trend_vector`, `combo_ratio__max_up_ret__keltner_squeeze_width`, `combo_ratio__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 7 | 2 | 0.3293 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 8 | 2 | 0.3293 | `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 9 | 2 | 0.3293 | `combo_diff__max_up_ret__demark_setup_reversal_early` | `combo_rel_diff__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 10 | 1 | 0.3293 | `combo_mean__max_up_ret__star50_limit_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 11 | 2 | 0.3293 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 12 | 2 | 0.3293 | `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_mean__volume_weighted_price_position__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 13 | 2 | 0.3293 | `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 14 | 3 | 0.3293 | `combo_rel_diff__max_up_ret__keltner_squeeze_width` | `combo_clamp_diff__max_up_ret__keltner_squeeze_width`, `combo_diff__max_up_ret__keltner_squeeze_width` |
| 159915ETF | single | Cluster 15 | 9 | 0.3293 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`, `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`, `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation`, `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature`, `combo_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum`, `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression`, `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression`, `combo_rank_max__star50_limit_proximity_early__volume_price_confirmation` |
| 159915ETF | single | Cluster 16 | 1 | 0.3293 | `combo_min__bar_ret_0__directional_volume_signature` | _(none)_ |
| 159915ETF | single | Cluster 17 | 2 | 0.3293 | `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__bar_ret_0` | `combo_ratio__bar_ret_0__volume_weighted_price_position` |
| 159915ETF | single | Cluster 18 | 1 | 0.3293 | `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | _(none)_ |
| 159915ETF | single | Cluster 19 | 2 | 0.3293 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 20 | 1 | 0.3293 | `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 21 | 2 | 0.3293 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 159915ETF | single | Cluster 22 | 2 | 0.3293 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` |
| 159915ETF | single | Cluster 23 | 1 | 0.3293 | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 24 | 2 | 0.3293 | `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 25 | 2 | 0.3293 | `combo_rank_min__max_up_ret__gap_pct` | `combo_min__max_up_ret__gap_pct` |
| 159915ETF | single | Cluster 26 | 2 | 0.3293 | `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 27 | 3 | 0.3293 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 28 | 2 | 0.3293 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` |
| 159915ETF | single | Cluster 29 | 6 | 0.3293 | `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | `combo_max__max_up_ret__volume_price_confirmation`, `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_rank_max__max_up_ret__volume_price_confirmation`, `combo_mean__max_up_ret__volume_price_confirmation` |
| 159915ETF | single | Cluster 30 | 3 | 0.3293 | `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_rank_max__max_up_ret__volume_weighted_price_position`, `combo_max__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 31 | 4 | 0.3293 | `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `combo_min__star50_limit_proximity_early__volume_price_confirmation`, `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`, `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` |
| 159915ETF | single | Cluster 32 | 3 | 0.3293 | `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `combo_mean__rbreaker_sell_setup_proximity_early__rally_strength_max`, `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` |
| 159915ETF | single | Cluster 33 | 2 | 0.3293 | `combo_max__opening_drive_thrust_ratio__bar_ret_0` | `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` |
| 159915ETF | single | Cluster 34 | 2 | 0.3293 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_min__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 35 | 2 | 0.3293 | `combo_mean__max_up_ret__bar_body_rng_0` | `combo_rank_max__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 36 | 1 | 0.3293 | `combo_max__bar_ret_0__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 37 | 1 | 0.3293 | `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | _(none)_ |
| 159915ETF | single | Cluster 38 | 1 | 0.3293 | `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 39 | 3 | 0.3293 | `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 40 | 2 | 0.3293 | `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 41 | 4 | 0.3293 | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 42 | 2 | 0.3293 | `combo_min__volume_weighted_price_position__limit_down_proximity_early` | `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` |
| 159915ETF | single | Cluster 43 | 4 | 0.3293 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_mean__bar_ret_0__limit_down_proximity_early` |
| 159915ETF | single | Cluster 44 | 4 | 0.3293 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_mean__opening_drive_thrust_ratio__max_up_ret`, `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 45 | 1 | 0.3293 | `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 46 | 2 | 0.3293 | `combo_tri_mean__opening_drive_thrust_ratio__demark_setup_reversal_early__star50_limit_proximity_early` | `combo_clamp_diff__volume_weighted_price_position__body_size_progression` |
| 159915ETF | single | Cluster 47 | 2 | 0.3293 | `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | `combo_rank_min__max_up_ret__rally_strength_max` |
| 159915ETF | single | Cluster 48 | 2 | 0.3293 | `combo_max__max_up_ret__rally_strength_max` | `combo_max__rbreaker_sell_setup_proximity_early__rally_strength_max` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`first_bar_return` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_mean__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | `tri_mean` | a=`bar_ret_0`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | `rank_max` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | `max` | a=`bar_ret_0`, b=`morning_volume_weighted_momentum` |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_median` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_concentration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__early_body_momentum` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`early_body_momentum` |
| `combo_mean__bar_ret_0__close_vs_open_range` | `mean` | a=`bar_ret_0`, b=`close_vs_open_range` |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`volume_weighted_momentum_acceleration` |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | `clamp_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_min__net_volume_flow__close_vs_open_range` | `min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`net_volume_flow`, c=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | `tri_min` | a=`max_up_ret`, b=`net_volume_flow`, c=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_mean__bar_ret_0__early_order_flow_imbalance` | `mean` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | `min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_mean` | a=`trend_bar_close_consistency`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`early_body_momentum` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | `clamp_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | `tri_max` | a=`max_up_ret`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_tri_mean__max_up_ret__early_body_momentum__bar_ret_0` | `tri_mean` | a=`max_up_ret`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_min__net_volume_flow__bar_body_rng_0` | `min` | a=`net_volume_flow`, b=`bar_body_rng_0` |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | `diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_max__bar_ret_0__close_vs_open_range` | `rank_max` | a=`bar_ret_0`, b=`close_vs_open_range` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_day_regime_conviction` |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_tri_mean__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | `tri_mean` | a=`early_body_momentum`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | `min` | a=`early_order_flow_imbalance`, b=`bar_body_rng_0` |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__bar_ret_0` | `tri_max` | a=`volatility_expansion_trend_vector`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__net_volume_flow` | `rank_max` | a=`max_up_ret`, b=`net_volume_flow` |
| `combo_min__first_bar_return__early_order_flow_imbalance` | `min` | a=`first_bar_return`, b=`early_order_flow_imbalance` |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | `rel_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_clamp_diff__first_bar_return__body_size_progression` | `clamp_diff` | a=`first_bar_return`, b=`body_size_progression` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_mean__first_bar_return__max_down_ret` | `mean` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_mean__max_up_ret__first_bar_return` | `mean` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__net_volume_flow__vwap_close_divergence_trend` | `rank_min` | a=`net_volume_flow`, b=`vwap_close_divergence_trend` |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | `mean` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_mean__max_up_ret__close_vs_open_range` | `mean` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_mean__first_bar_return__bar_body_rng_0` | `mean` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`trend_day_regime_conviction` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_mean__max_up_ret__max_down_ret` | `mean` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_max__max_up_ret__max_down_ret` | `max` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | `mean` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__max_up_ret__max_down_ret` | `rank_max` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | `rank_max` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | `diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_max__max_up_ret__close_vs_open_range` | `max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | `max` | a=`first_bar_return`, b=`vwap_close_divergence_trend` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | `diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | `rank_max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_tri_median__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`early_body_momentum`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | `sig_product` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | `max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | `sig_product` | a=`trend_day_regime_conviction`, b=`vwap_close_divergence_trend` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_mean__first_bar_return__shaved_bar_trend_conviction` | `mean` | a=`first_bar_return`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | `sig_product` | a=`trend_bar_close_consistency`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__net_volume_flow__vwap_close_divergence_trend` | `sig_product` | a=`net_volume_flow`, b=`vwap_close_divergence_trend` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, cond=`gap_pct` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | `min` | a=`star50_limit_proximity_early`, b=`volume_price_confirmation` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_min__volume_weighted_price_position__limit_down_proximity_early` | `min` | a=`volume_weighted_price_position`, b=`limit_down_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_mean__volume_weighted_price_position__rbreaker_buy_setup_proximity_early` | `mean` | a=`volume_weighted_price_position`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__rally_strength_max` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`directional_volume_signature` |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | `rank_min` | a=`volume_weighted_price_position`, b=`limit_down_proximity_early` |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | `tri_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_trend` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__bar_ret_0__limit_down_proximity_early` | `min` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | `mean` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rally_strength_max` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | `mean` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`body_size_progression` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`directional_volume_signature` |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `rank_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`directional_volume_signature` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`demark_setup_reversal_early` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_return` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_max__max_up_ret__volume_price_confirmation` | `max` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | `ifelse` | a=`max_up_ret`, b=`star50_limit_proximity_early`, cond=`gap_pct` |
| `combo_rank_min__max_up_ret__gap_pct` | `rank_min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_max__max_up_ret__rally_strength_max` | `max` | a=`max_up_ret`, b=`rally_strength_max` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_clamp_diff__volume_weighted_price_position__body_size_progression` | `clamp_diff` | a=`volume_weighted_price_position`, b=`body_size_progression` |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | `rank_max` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_price_confirmation` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | `ifelse` | a=`yesterday_early_momentum`, b=`star50_limit_proximity_early`, cond=`gap_pct` |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, c=`bar_ret_0` |
| `combo_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`late_bar_momentum` |
| `combo_tri_mean__opening_drive_thrust_ratio__demark_setup_reversal_early__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | `rel_diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | `max` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`gap_pct` |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | `ratio` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `rank_max` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`body_size_progression` |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | `tri_median` | a=`demark_setup_reversal_early`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_diff__max_up_ret__keltner_squeeze_width` | `diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_rank_min__max_up_ret__rally_strength_max` | `rank_min` | a=`max_up_ret`, b=`rally_strength_max` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_max__rbreaker_sell_setup_proximity_early__rally_strength_max` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | `max` | a=`bar_ret_0`, b=`volatility_expansion_trend_vector` |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | `clamp_diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_mean__max_up_ret__volume_price_confirmation` | `mean` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_rank_max__star50_limit_proximity_early__volume_price_confirmation` | `rank_max` | a=`star50_limit_proximity_early`, b=`volume_price_confirmation` |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_min__max_up_ret__gap_pct` | `min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | `ratio` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | `rank_min` | a=`limit_down_proximity_early`, b=`volume_price_confirmation` |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | `ifelse` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, cond=`gap_pct` |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | `ratio` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_min__bar_ret_0__directional_volume_signature` | `min` | a=`bar_ret_0`, b=`directional_volume_signature` |
