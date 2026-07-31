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
| 300ETF | single | 1,597 | 637 | 522 | 388 | 386 | 386 | 365 | 364 | 125 | 97 | 41 | `[8, 7, 6, 5, 5, 5, 4, 3, 2, 2, 2, 2, ... (41 clusters)]` |
| 300ETF | long | 585 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 587 | 69 | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | single | 1,244 | 403 | 326 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | long | 363 | 42 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | short | 320 | 42 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 3,084 | 1,385 | 1,178 | 956 | 950 | 898 | 852 | 851 | 206 | 159 | 47 | `[12, 10, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, ... (47 clusters)]` |
| 500ETF | long | 1,347 | 119 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | short | 429 | 60 | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | single | 1,924 | 835 | 663 | 605 | 601 | 500 | 499 | 499 | 183 | 146 | 48 | `[12, 12, 10, 9, 7, 6, 5, 5, 5, 4, 4, 3, ... (48 clusters)]` |
| 159915ETF | long | 1,118 | 180 | 117 | 117 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | short | 299 | 43 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 97 | 41 | `[8, 7, 6, 5, 5, 5, 4, 3, 2, 2, 2, 2, ... (41 clusters)]` | +0.1043 | [+0.0614, +0.1461] | +0.2457 | [+0.1507, +0.3374] | +0.8545 | 5.60% | 1.5974 | 4.04% | 1.1726 | 2.6453 | 2.49% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 159 | 47 | `[12, 10, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, ... (47 clusters)]` | +0.1505 | [+0.1059, +0.1918] | +0.2450 | [+0.1474, +0.3246] | +0.9515 | 5.52% | 1.3937 | 3.93% | 1.0029 | 1.7911 | 3.28% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 146 | 48 | `[12, 12, 10, 9, 7, 6, 5, 5, 5, 4, 4, 3, ... (48 clusters)]` | +0.1413 | [+0.1003, +0.1835] | +0.3130 | [+0.2229, +0.3994] | +0.7818 | 9.03% | 1.8336 | 7.47% | 1.5380 | 3.7444 | 2.47% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 97 | 41 | `[8, 7, 6, 5, 5, 5, 4, 3, 2, 2, 2, 2, ... (41 clusters)]` | +0.0136* | [-0.1216, +0.1129] | +0.0518* | [-0.2628, +0.2960] | +0.2242 | 0.37% | 0.1575 | -1.21% | -0.5145 | -0.7122 | 5.46% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 159 | 47 | `[12, 10, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, ... (47 clusters)]` | +0.0756* | [-0.0415, +0.1601] | -0.0129* | [-0.2650, +0.1760] | +0.7333 | 0.77% | 0.2224 | -0.71% | -0.2035 | -0.2824 | 4.56% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 146 | 48 | `[12, 12, 10, 9, 7, 6, 5, 5, 5, 4, 4, 3, ... (48 clusters)]` | +0.1423 | [+0.0090, +0.2435] | +0.1174* | [-0.1901, +0.3129] | +0.7455 | 5.70% | 1.0374 | 4.25% | 0.7809 | 1.3537 | 6.73% |
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
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 3 | +1 | +0.0996 | +0.2881 | +0.2875 | 0.0000 | +0.8325 | +0.7694 | 0.973 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1035 | +0.2826 | +0.2824 | 0.0000 | +0.6965 | +0.7571 | 0.937 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 3 | +1 | +0.1012 | +0.2766 | +0.2766 | 0.0000 | +0.6959 | +0.7375 | 0.913 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 25 | +1 | +0.1003 | +0.2709 | +0.2714 | 0.0000 | +0.7164 | +0.7576 | 0.907 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 15 | +1 | +0.0875 | +0.2655 | +0.2657 | 0.0000 | +0.8219 | +0.7566 | 0.782 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 25 | +1 | +0.0996 | +0.2628 | +0.2633 | 0.0000 | +0.7808 | +0.7885 | 0.899 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.0864 | +0.2523 | +0.2529 | 0.0000 | +0.8743 | +0.8003 | 0.827 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 28 | +1 | +0.0936 | +0.2499 | +0.2501 | 0.0000 | +0.6698 | +0.7761 | 0.904 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 40 | +1 | +0.0957 | +0.2456 | +0.2452 | 0.0000 | +0.6495 | +0.7185 | 0.874 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0971 | +0.2430 | +0.2433 | 0.0000 | +0.7080 | +0.7560 | 0.947 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0926 | +0.2384 | +0.2392 | 0.0000 | +0.6527 | +0.7391 | 0.908 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 2 | +1 | +0.0843 | +0.2365 | +0.2367 | 0.0000 | +0.5135 | +0.7097 | 1.000 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Cluster 30 | +1 | +0.0875 | +0.2339 | +0.2334 | 0.0000 | +0.7192 | +0.7468 | 0.820 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 11 | +1 | +0.0969 | +0.2333 | +0.2327 | 0.0000 | +0.6480 | +0.7916 | 0.994 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Cluster 34 | +1 | +0.0914 | +0.2318 | +0.2326 | 0.0000 | +0.8216 | +0.8029 | 1.000 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 15 | +1 | +0.0906 | +0.2309 | +0.2312 | 0.0000 | +0.7847 | +0.7571 | 0.864 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 4 | +1 | +0.0852 | +0.2286 | +0.2287 | 0.0000 | +0.4841 | +0.6778 | 1.000 |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 8 | +1 | +0.0923 | +0.2284 | +0.2274 | 0.0000 | +0.6106 | +0.7488 | 0.862 |
| `combo_max__first_bar_return__volume_surge_direction` | Cluster 30 | +1 | +0.0790 | +0.2280 | +0.2267 | 0.0002 | +0.7009 | +0.7669 | 0.865 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 26 | +1 | +0.0858 | +0.2260 | +0.2253 | 0.0002 | +0.5785 | +0.7180 | 0.843 |
| `combo_rank_max__first_bar_return__volume_surge_direction` | Cluster 30 | +1 | +0.0762 | +0.2246 | +0.2232 | 0.0002 | +0.7177 | +0.7782 | 0.925 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 38 | +1 | +0.0925 | +0.2232 | +0.2229 | 0.0002 | +0.6634 | +0.7344 | 0.873 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 31 | +1 | +0.0934 | +0.2221 | +0.2231 | 0.0002 | +0.6061 | +0.7257 | 0.913 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 20 | +1 | +0.0851 | +0.2219 | +0.2207 | 0.0002 | +0.7889 | +0.7669 | 0.904 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 28 | +1 | +0.0903 | +0.2219 | +0.2221 | 0.0002 | +0.6850 | +0.7792 | 0.945 |
| `combo_max__max_up_ret__volume_surge_direction` | Cluster 35 | +1 | +0.0732 | +0.2210 | +0.2198 | 0.0002 | +0.7910 | +0.7643 | 0.946 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 10 | +1 | +0.0901 | +0.2199 | +0.2204 | 0.0002 | +0.7998 | +0.7833 | 0.964 |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Cluster 27 | +1 | +0.0953 | +0.2186 | +0.2190 | 0.0002 | +0.6989 | +0.7658 | 1.000 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 33 | +1 | +0.0932 | +0.2167 | +0.2178 | 0.0002 | +0.6191 | +0.7133 | 0.931 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 15 | +1 | +0.0959 | +0.2163 | +0.2166 | 0.0002 | +0.6930 | +0.7277 | 0.960 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Cluster 31 | +1 | +0.0907 | +0.2155 | +0.2166 | 0.0002 | +0.5717 | +0.7138 | 0.943 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 15 | +1 | +0.0892 | +0.2147 | +0.2148 | 0.0002 | +0.7471 | +0.7617 | 0.954 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 32 | +1 | +0.0979 | +0.2124 | +0.2130 | 0.0002 | +0.7324 | +0.7787 | 1.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.0804 | +0.2119 | +0.2119 | 0.0002 | +0.6780 | +0.7545 | 0.945 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | Cluster 35 | +1 | +0.0722 | +0.2113 | +0.2101 | 0.0002 | +0.7967 | +0.7679 | 0.901 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 39 | +1 | +0.1028 | +0.2112 | +0.2105 | 0.0002 | +0.6170 | +0.7236 | 0.973 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 11 | +1 | +0.0893 | +0.2095 | +0.2097 | 0.0002 | +0.7133 | +0.7499 | 1.000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.0927 | +0.2066 | +0.2062 | 0.0002 | +0.6739 | +0.7149 | 0.939 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 27 | +1 | +0.0902 | +0.2062 | +0.2060 | 0.0002 | +0.6930 | +0.7910 | 0.949 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 26 | +1 | +0.0807 | +0.2054 | +0.2055 | 0.0002 | +0.5406 | +0.7226 | 0.911 |
| `max_up_ret` | Cluster 18 | +1 | +0.0742 | +0.2051 | +0.2056 | 0.0002 | +0.6225 | +0.7216 | 0.937 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 40 | +1 | +0.0951 | +0.2045 | +0.2038 | 0.0002 | +0.6024 | +0.7375 | 0.930 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 10 | +1 | +0.0805 | +0.2042 | +0.2050 | 0.0002 | +0.8858 | +0.8322 | 0.904 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.0963 | +0.2034 | +0.2025 | 0.0002 | +0.5403 | +0.7241 | 0.941 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0834 | +0.2033 | +0.2039 | 0.0002 | +0.7770 | +0.8024 | 0.940 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 11 | +1 | +0.0905 | +0.2028 | +0.2027 | 0.0002 | +0.6456 | +0.7777 | 0.965 |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Cluster 5 | +1 | +0.0924 | +0.2012 | +0.2019 | 0.0002 | +0.6164 | +0.7437 | 1.000 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 7 | +1 | +0.1039 | +0.2012 | +0.2009 | 0.0002 | +0.5110 | +0.7205 | 1.000 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0992 | +0.2005 | +0.2011 | 0.0002 | +0.4677 | +0.7195 | 0.912 |
| `combo_rank_min__max_up_ret__volume_surge_direction` | Cluster 20 | +1 | +0.0815 | +0.2000 | +0.1994 | 0.0002 | +0.4369 | +0.6758 | 0.901 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 29 | +1 | +0.0847 | +0.1997 | +0.1998 | 0.0002 | +0.6211 | +0.6974 | 1.000 |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 5 | +1 | +0.0932 | +0.1995 | +0.1997 | 0.0002 | +0.5166 | +0.6768 | 0.893 |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 37 | +1 | +0.0846 | +0.1995 | +0.1983 | 0.0002 | +0.6159 | +0.7411 | 0.930 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 15 | +1 | +0.0790 | +0.1994 | +0.1999 | 0.0002 | +0.4588 | +0.7349 | 0.921 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 23 | +1 | +0.0768 | +0.1986 | +0.1991 | 0.0002 | +0.5819 | +0.7210 | 0.714 |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 4 | +1 | +0.0854 | +0.1985 | +0.1982 | 0.0002 | +0.4670 | +0.6783 | 1.000 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0985 | +0.1959 | +0.1967 | 0.0002 | +0.4688 | +0.6938 | 1.000 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0848 | +0.1930 | +0.1936 | 0.0002 | +0.6691 | +0.7329 | 0.907 |
| `first_bar_return` | Cluster 11 | +1 | +0.0874 | +0.1925 | +0.1926 | 0.0002 | +0.6512 | +0.7524 | 0.949 |
| `combo_mean__first_bar_return__first_bar_sentiment` | Cluster 11 | +1 | +0.0874 | +0.1925 | +0.1926 | 0.0002 | +0.6512 | +0.7524 | 0.947 |
| `combo_min__first_bar_return__bar_body_rng_0` | Cluster 11 | +1 | +0.0891 | +0.1923 | +0.1926 | 0.0002 | +0.6256 | +0.7375 | 0.950 |
| `combo_sig_product__bar_ret_0__bar_body_rng_0` | Cluster 11 | +1 | +0.0927 | +0.1921 | +0.1925 | 0.0002 | +0.6657 | +0.7221 | 1.000 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0910 | +0.1910 | +0.1915 | 0.0002 | +0.5273 | +0.7005 | 0.933 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 17 | +1 | +0.0732 | +0.1899 | +0.1894 | 0.0002 | +0.6872 | +0.7735 | 0.876 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 20 | +1 | +0.0840 | +0.1898 | +0.1891 | 0.0002 | +0.5697 | +0.7123 | 0.968 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.0762 | +0.1886 | +0.1891 | 0.0002 | +0.5094 | +0.7262 | 0.946 |
| `combo_min__max_up_ret__volume_surge_direction` | Cluster 20 | +1 | +0.0854 | +0.1881 | +0.1872 | 0.0002 | +0.4516 | +0.6526 | 0.925 |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 7 | +1 | +0.1031 | +0.1879 | +0.1880 | 0.0002 | +0.5934 | +0.6799 | 0.939 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.0712 | +0.1875 | +0.1876 | 0.0002 | +0.5021 | +0.7108 | 0.930 |
| `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0984 | +0.1816 | +0.1821 | 0.0004 | +0.6208 | +0.7452 | 0.940 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 9 | +1 | +0.0827 | +0.1811 | +0.1817 | 0.0004 | +0.5828 | +0.7118 | 1.000 |
| `combo_min__first_bar_return__volume_surge_direction` | Cluster 30 | +1 | +0.0812 | +0.1784 | +0.1778 | 0.0006 | +0.5580 | +0.6948 | 1.000 |
| `volume_weighted_price_position` | Cluster 22 | +1 | +0.0791 | +0.1777 | +0.1783 | 0.0008 | +0.6336 | +0.7535 | 0.871 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0` | Cluster 36 | +1 | +0.0662 | +0.1770 | +0.1774 | 0.0008 | +0.4040 | +0.6783 | 0.886 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 22 | +1 | +0.0868 | +0.1766 | +0.1782 | 0.0008 | +0.5792 | +0.7123 | 0.825 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 20 | +1 | +0.0858 | +0.1756 | +0.1752 | 0.0008 | +0.5438 | +0.7066 | 0.921 |
| `combo_max__volume_weighted_price_position__volume_surge_direction` | Cluster 14 | +1 | +0.0754 | +0.1755 | +0.1750 | 0.0008 | +0.6122 | +0.7118 | 0.957 |
| `combo_mean__volume_weighted_price_position__first_bar_sentiment` | Cluster 14 | +1 | +0.0855 | +0.1745 | +0.1740 | 0.0008 | +0.5993 | +0.7586 | 0.934 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 18 | +1 | +0.0887 | +0.1738 | +0.1743 | 0.0010 | +0.5990 | +0.7283 | 0.906 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 8 | +1 | +0.0904 | +0.1731 | +0.1727 | 0.0010 | +0.5593 | +0.7344 | 0.943 |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | Cluster 13 | +1 | +0.0812 | +0.1727 | +0.1722 | 0.0010 | +0.6644 | +0.7648 | 0.881 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 23 | +1 | +0.0589 | +0.1714 | +0.1712 | 0.0010 | +0.5584 | +0.6742 | 0.827 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Cluster 17 | +1 | +0.0805 | +0.1702 | +0.1701 | 0.0012 | +0.4800 | +0.6840 | 0.922 |
| `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | Cluster 13 | +1 | +0.0743 | +0.1693 | +0.1698 | 0.0012 | +0.5537 | +0.6814 | 0.894 |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | Cluster 14 | +1 | +0.0918 | +0.1680 | +0.1672 | 0.0012 | +0.5785 | +0.7015 | 0.941 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 9 | +1 | +0.0836 | +0.1680 | +0.1686 | 0.0012 | +0.4024 | +0.6557 | 1.000 |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | Cluster 14 | +1 | +0.0888 | +0.1673 | +0.1660 | 0.0012 | +0.5857 | +0.7216 | 0.932 |
| `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | Cluster 24 | +1 | +0.0677 | +0.1663 | +0.1665 | 0.0014 | +0.5386 | +0.6958 | 0.892 |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 33 | +1 | +0.0943 | +0.1647 | +0.1656 | 0.0014 | +0.6586 | +0.7370 | 0.937 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 16 | +1 | +0.0964 | +0.1614 | +0.1623 | 0.0014 | +0.5990 | +0.7174 | 0.841 |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | Cluster 21 | +1 | +0.0779 | +0.1557 | +0.1552 | 0.0020 | +0.4840 | +0.6948 | 0.893 |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | Cluster 19 | +1 | +0.0534 | +0.1451 | +0.1460 | 0.0042 | +0.4351 | +0.6665 | 0.320 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 16 | +1 | +0.0889 | +0.1362 | +0.1369 | 0.0064 | +0.5725 | +0.7154 | 0.875 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Cluster 11 | +1 | +0.0796 | +0.1306 | +0.1312 | 0.0094 | +0.3195 | +0.6577 | 0.031 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Cluster 12 | +1 | +0.0528 | +0.1264 | +0.1276 | 0.0124 | +0.4721 | +0.6629 | 0.577 |
| `open_to_current_return` | Cluster 24 | +1 | +0.0582 | +0.1189 | +0.1197 | 0.0188 | +0.4529 | +0.6855 | 1.000 |
| `combo_max__first_bar_sentiment__volume_surge_direction` | Cluster 30 | +1 | +0.0750 | +0.1068 | +0.1051 | 0.0324 | +0.4097 | +0.6516 | 0.916 |

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
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1462 | +0.2982 | +0.2978 | 0.0000 | +1.0529 | +0.8466 | 0.000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1388 | +0.2970 | +0.2966 | 0.0000 | +1.0832 | +0.8518 | 0.901 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 11 | +1 | +0.1315 | +0.2897 | +0.2885 | 0.0000 | +1.1021 | +0.8533 | 0.640 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1545 | +0.2882 | +0.2875 | 0.0000 | +0.8177 | +0.7838 | 0.908 |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | Cluster 41 | +1 | +0.1141 | +0.2718 | +0.2718 | 0.0000 | +0.5334 | +0.6922 | 0.773 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 8 | +1 | +0.1415 | +0.2713 | +0.2707 | 0.0000 | +0.7383 | +0.7586 | 0.895 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 18 | +1 | +0.1474 | +0.2700 | +0.2690 | 0.0000 | +1.1888 | +0.8688 | 0.906 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 11 | +1 | +0.1361 | +0.2699 | +0.2686 | 0.0000 | +0.8517 | +0.7869 | 0.926 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 28 | +1 | +0.1453 | +0.2689 | +0.2675 | 0.0000 | +1.0684 | +0.8286 | 0.948 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Cluster 16 | +1 | +0.1496 | +0.2649 | +0.2639 | 0.0000 | +1.0489 | +0.8652 | 0.945 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 11 | +1 | +0.1205 | +0.2631 | +0.2618 | 0.0000 | +0.8119 | +0.7633 | 0.947 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Cluster 39 | +1 | +0.1292 | +0.2594 | +0.2588 | 0.0000 | +0.9535 | +0.8183 | 0.896 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 9 | +1 | +0.1133 | +0.2588 | +0.2581 | 0.0000 | +0.8473 | +0.8250 | 0.955 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 16 | +1 | +0.1359 | +0.2578 | +0.2570 | 0.0000 | +0.9398 | +0.7998 | 0.967 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 29 | +1 | +0.1364 | +0.2577 | +0.2564 | 0.0000 | +0.8679 | +0.8080 | 0.870 |
| `combo_min__net_volume_flow__first_bar_return` | Cluster 44 | +1 | +0.1151 | +0.2561 | +0.2559 | 0.0000 | +0.8070 | +0.7828 | 0.904 |
| `combo_min__net_volume_flow__close_vs_open_range` | Cluster 3 | +1 | +0.1032 | +0.2540 | +0.2534 | 0.0000 | +0.7063 | +0.7679 | 0.934 |
| `combo_mean__trend_bar_close_consistency__bar_ret_0` | Cluster 39 | +1 | +0.1128 | +0.2530 | +0.2530 | 0.0000 | +0.6931 | +0.7339 | 0.948 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1473 | +0.2524 | +0.2516 | 0.0000 | +0.9968 | +0.8224 | 0.931 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 29 | +1 | +0.1404 | +0.2523 | +0.2504 | 0.0000 | +0.9815 | +0.8446 | 0.918 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Cluster 11 | +1 | +0.1131 | +0.2512 | +0.2503 | 0.0000 | +0.7318 | +0.7607 | 0.945 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 2 | +1 | +0.1050 | +0.2502 | +0.2492 | 0.0000 | +0.7010 | +0.7581 | 0.956 |
| `combo_rank_min__net_volume_flow__first_bar_return` | Cluster 44 | +1 | +0.1137 | +0.2478 | +0.2476 | 0.0000 | +0.7399 | +0.7463 | 0.943 |
| `combo_mean__net_volume_flow__first_bar_sentiment` | Cluster 40 | +1 | +0.1186 | +0.2476 | +0.2473 | 0.0000 | +0.7408 | +0.7730 | 0.979 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1414 | +0.2469 | +0.2455 | 0.0000 | +0.6286 | +0.7087 | 0.786 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Cluster 29 | +1 | +0.1475 | +0.2468 | +0.2452 | 0.0000 | +0.9216 | +0.8080 | 0.978 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 37 | +1 | +0.1263 | +0.2464 | +0.2461 | 0.0000 | +0.7730 | +0.7808 | 0.945 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Cluster 8 | +1 | +0.1334 | +0.2463 | +0.2457 | 0.0000 | +0.7197 | +0.7427 | 0.977 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Cluster 42 | +1 | +0.1223 | +0.2447 | +0.2444 | 0.0000 | +0.7819 | +0.7735 | 0.892 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Cluster 11 | +1 | +0.1055 | +0.2432 | +0.2416 | 0.0000 | +0.7688 | +0.7560 | 0.942 |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | Cluster 33 | +1 | +0.1373 | +0.2430 | +0.2424 | 0.0000 | +1.0065 | +0.8528 | 0.948 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1540 | +0.2424 | +0.2416 | 0.0000 | +0.9301 | +0.8111 | 0.989 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Cluster 0 | +1 | +0.1523 | +0.2406 | +0.2401 | 0.0000 | +0.8455 | +0.7771 | 0.920 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 3 | +1 | +0.1151 | +0.2405 | +0.2399 | 0.0000 | +0.7211 | +0.7591 | 0.938 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 46 | +1 | +0.1144 | +0.2385 | +0.2369 | 0.0000 | +0.7321 | +0.7813 | 0.965 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Cluster 14 | +1 | +0.1315 | +0.2381 | +0.2375 | 0.0000 | +0.7025 | +0.7694 | 0.952 |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 16 | +1 | +0.1248 | +0.2363 | +0.2358 | 0.0000 | +0.7923 | +0.8317 | 0.948 |
| `combo_rank_max__max_up_ret__net_volume_flow` | Cluster 19 | +1 | +0.1288 | +0.2350 | +0.2339 | 0.0000 | +0.7221 | +0.7385 | 0.927 |
| `early_order_flow_imbalance` | Cluster 23 | +1 | +0.0995 | +0.2348 | +0.2351 | 0.0000 | +0.5819 | +0.7334 | 0.805 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1330 | +0.2334 | +0.2321 | 0.0000 | +0.5792 | +0.7066 | 0.908 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 25 | +1 | +0.1207 | +0.2329 | +0.2322 | 0.0000 | +0.6727 | +0.7319 | 1.000 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 17 | +1 | +0.1271 | +0.2328 | +0.2321 | 0.0000 | +0.7429 | +0.7633 | 0.917 |
| `combo_max__close_vs_open_range__first_bar_return` | Cluster 33 | +1 | +0.1359 | +0.2328 | +0.2321 | 0.0000 | +0.9856 | +0.8451 | 0.909 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 0 | +1 | +0.1347 | +0.2306 | +0.2301 | 0.0000 | +0.7860 | +0.7638 | 1.000 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 31 | +1 | +0.1353 | +0.2306 | +0.2300 | 0.0000 | +0.8583 | +0.8173 | 0.895 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 14 | +1 | +0.1447 | +0.2303 | +0.2293 | 0.0000 | +0.9868 | +0.8549 | 0.947 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 8 | +1 | +0.1404 | +0.2281 | +0.2271 | 0.0000 | +0.9676 | +0.8096 | 0.933 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 0 | +1 | +0.1529 | +0.2278 | +0.2276 | 0.0000 | +0.8704 | +0.8230 | 0.926 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 0 | +1 | +0.1276 | +0.2276 | +0.2272 | 0.0000 | +0.8782 | +0.8194 | 0.950 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 37 | +1 | +0.1239 | +0.2273 | +0.2272 | 0.0000 | +0.5862 | +0.7169 | 0.927 |
| `combo_rank_max__net_volume_flow__close_vs_open_range` | Cluster 3 | +1 | +0.1128 | +0.2272 | +0.2265 | 0.0000 | +0.5407 | +0.7154 | 0.970 |
| `combo_max__early_body_momentum__bar_ret_0` | Cluster 42 | +1 | +0.1180 | +0.2272 | +0.2269 | 0.0000 | +0.8255 | +0.8013 | 0.939 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 25 | +1 | +0.1228 | +0.2267 | +0.2261 | 0.0000 | +0.7036 | +0.7828 | 0.849 |
| `combo_min__trend_bar_close_consistency__bar_ret_0` | Cluster 43 | +1 | +0.0936 | +0.2262 | +0.2265 | 0.0000 | +0.7021 | +0.7169 | 1.000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 11 | +1 | +0.1188 | +0.2252 | +0.2238 | 0.0000 | +0.7435 | +0.7571 | 0.964 |
| `combo_min__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 11 | +1 | +0.1142 | +0.2246 | +0.2231 | 0.0000 | +0.7179 | +0.7797 | 0.949 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Cluster 11 | +1 | +0.1172 | +0.2219 | +0.2209 | 0.0000 | +0.8008 | +0.7998 | 0.932 |
| `combo_mean__first_bar_return__max_down_ret` | Cluster 36 | +1 | +0.1199 | +0.2194 | +0.2195 | 0.0000 | +0.7236 | +0.7396 | 0.884 |
| `combo_mean__max_up_ret__first_bar_return` | Cluster 32 | +1 | +0.1375 | +0.2184 | +0.2177 | 0.0000 | +0.6775 | +0.7452 | 1.000 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1329 | +0.2181 | +0.2169 | 0.0000 | +0.5428 | +0.6943 | 0.940 |
| `combo_mean__net_volume_flow__max_down_ret` | Cluster 9 | +1 | +0.1136 | +0.2161 | +0.2158 | 0.0000 | +0.7181 | +0.7838 | 0.979 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | Cluster 13 | +1 | +0.1154 | +0.2159 | +0.2145 | 0.0000 | +0.6088 | +0.7262 | 0.894 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Cluster 15 | +1 | +0.1421 | +0.2151 | +0.2139 | 0.0000 | +0.6228 | +0.7108 | 0.926 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 0 | +1 | +0.1395 | +0.2150 | +0.2149 | 0.0000 | +0.7724 | +0.7895 | 0.898 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 18 | +1 | +0.1444 | +0.2144 | +0.2132 | 0.0000 | +0.7882 | +0.7581 | 0.947 |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 3 | +1 | +0.1064 | +0.2139 | +0.2135 | 0.0000 | +0.4943 | +0.6917 | 0.950 |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | Cluster 34 | +1 | +0.1011 | +0.2134 | +0.2111 | 0.0000 | +0.5497 | +0.6655 | 0.758 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 15 | +1 | +0.1526 | +0.2127 | +0.2112 | 0.0000 | +0.7040 | +0.7710 | 0.929 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Cluster 27 | +1 | +0.1125 | +0.2127 | +0.2115 | 0.0000 | +0.4502 | +0.6855 | 0.821 |
| `combo_max__max_up_ret__early_body_momentum` | Cluster 4 | +1 | +0.1206 | +0.2121 | +0.2111 | 0.0000 | +0.7002 | +0.7241 | 0.965 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 18 | +1 | +0.1512 | +0.2120 | +0.2108 | 0.0000 | +0.7433 | +0.7607 | 0.927 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Cluster 13 | +1 | +0.1203 | +0.2114 | +0.2098 | 0.0000 | +0.6243 | +0.7164 | 0.906 |
| `combo_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 8 | +1 | +0.1452 | +0.2096 | +0.2090 | 0.0000 | +0.6906 | +0.7319 | 0.991 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 8 | +1 | +0.1399 | +0.2092 | +0.2085 | 0.0000 | +0.6924 | +0.7380 | 0.970 |
| `combo_min__max_up_ret__trend_bar_close_consistency` | Cluster 7 | +1 | +0.1028 | +0.2084 | +0.2077 | 0.0000 | +0.5949 | +0.6871 | 0.939 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 1 | +1 | +0.0822 | +0.2069 | +0.2053 | 0.0000 | +0.6361 | +0.7221 | 0.920 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 0 | +1 | +0.1398 | +0.2059 | +0.2054 | 0.0000 | +0.7075 | +0.7560 | 0.930 |
| `combo_max__bar_ret_0__max_down_ret` | Cluster 36 | +1 | +0.1301 | +0.2053 | +0.2054 | 0.0000 | +0.7967 | +0.7766 | 0.929 |
| `combo_rank_min__high_low_sequence_momentum__max_down_ret` | Cluster 9 | +1 | +0.1103 | +0.2050 | +0.2050 | 0.0000 | +0.7129 | +0.7607 | 0.992 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | Cluster 13 | +1 | +0.1153 | +0.2043 | +0.2028 | 0.0000 | +0.5608 | +0.7185 | 0.936 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 37 | +1 | +0.1260 | +0.2043 | +0.2041 | 0.0000 | +0.6227 | +0.7056 | 0.920 |
| `combo_min__volatility_expansion_trend_vector__max_down_ret` | Cluster 9 | +1 | +0.1111 | +0.2027 | +0.2025 | 0.0000 | +0.6945 | +0.7422 | 0.946 |
| `combo_min__close_vs_open_range__first_bar_return` | Cluster 45 | +1 | +0.1038 | +0.2013 | +0.2013 | 0.0000 | +0.7080 | +0.7499 | 0.913 |
| `max_up_ret` | Cluster 31 | +1 | +0.1323 | +0.2006 | +0.1991 | 0.0000 | +0.6170 | +0.7216 | 0.923 |
| `combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 8 | +1 | +0.1208 | +0.1999 | +0.1994 | 0.0000 | +0.5335 | +0.7138 | 0.916 |
| `combo_rank_min__max_up_ret__first_bar_return` | Cluster 32 | +1 | +0.1223 | +0.1999 | +0.1991 | 0.0000 | +0.5017 | +0.6948 | 1.000 |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | Cluster 9 | +1 | +0.1075 | +0.1991 | +0.1993 | 0.0000 | +0.6355 | +0.7241 | 0.970 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Cluster 12 | +1 | +0.1129 | +0.1985 | +0.1984 | 0.0000 | +0.7085 | +0.7494 | 0.947 |
| `combo_mean__first_bar_sentiment__bar_ret_0` | Cluster 12 | +1 | +0.1160 | +0.1983 | +0.1986 | 0.0000 | +0.6758 | +0.7463 | 0.961 |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | Cluster 12 | +1 | +0.1150 | +0.1983 | +0.1986 | 0.0000 | +0.6758 | +0.7463 | 1.000 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Cluster 32 | +1 | +0.1355 | +0.1980 | +0.1968 | 0.0000 | +0.5171 | +0.7015 | 0.956 |
| `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression` | Cluster 2 | +1 | +0.0811 | +0.1942 | +0.1940 | 0.0000 | +0.4885 | +0.7252 | 0.930 |
| `combo_max__net_volume_flow__max_down_ret` | Cluster 9 | +1 | +0.1114 | +0.1926 | +0.1922 | 0.0000 | +0.7041 | +0.7519 | 0.941 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Cluster 8 | +1 | +0.1250 | +0.1920 | +0.1913 | 0.0000 | +0.6777 | +0.7313 | 0.928 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 46 | +1 | +0.1088 | +0.1908 | +0.1895 | 0.0000 | +0.6568 | +0.7571 | 0.987 |
| `always_in_trend_persistence` | Cluster 23 | +1 | +0.0826 | +0.1892 | +0.1892 | 0.0000 | +0.5484 | +0.7344 | 0.954 |
| `combo_min__trend_day_regime_conviction__first_bar_sentiment` | Cluster 38 | +1 | +0.1098 | +0.1889 | +0.1883 | 0.0000 | +0.4472 | +0.6819 | 0.952 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Cluster 34 | +1 | +0.1205 | +0.1888 | +0.1873 | 0.0000 | +0.4556 | +0.6752 | 0.700 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_day_regime_conviction` | Cluster 37 | +1 | +0.1277 | +0.1884 | +0.1883 | 0.0000 | +0.4629 | +0.6608 | 0.979 |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | Cluster 12 | +1 | +0.1023 | +0.1877 | +0.1871 | 0.0000 | +0.5674 | +0.7108 | 0.946 |
| `combo_min__max_up_ret__close_vs_open_range` | Cluster 20 | +1 | +0.1127 | +0.1861 | +0.1850 | 0.0000 | +0.6973 | +0.7566 | 0.905 |
| `combo_max__close_vs_open_range__max_down_ret` | Cluster 9 | +1 | +0.1039 | +0.1851 | +0.1847 | 0.0000 | +0.4960 | +0.6732 | 0.900 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 35 | +1 | +0.1090 | +0.1843 | +0.1829 | 0.0002 | +0.5820 | +0.6938 | 0.746 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 25 | +1 | +0.0954 | +0.1833 | +0.1822 | 0.0002 | +0.6465 | +0.7169 | 0.847 |
| `combo_min__first_bar_return__max_down_ret` | Cluster 36 | +1 | +0.1016 | +0.1828 | +0.1830 | 0.0002 | +0.6878 | +0.7586 | 1.000 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Cluster 36 | +1 | +0.1289 | +0.1827 | +0.1829 | 0.0002 | +0.7165 | +0.7524 | 0.905 |
| `combo_max__close_vs_open_range__early_body_momentum` | Cluster 3 | +1 | +0.0958 | +0.1819 | +0.1813 | 0.0002 | +0.4591 | +0.6963 | 0.953 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Cluster 34 | +1 | +0.1186 | +0.1819 | +0.1803 | 0.0002 | +0.4240 | +0.6696 | 0.680 |
| `combo_rank_min__first_bar_return__max_down_ret` | Cluster 36 | +1 | +0.0994 | +0.1811 | +0.1815 | 0.0002 | +0.6421 | +0.7241 | 0.891 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Cluster 21 | +1 | +0.0903 | +0.1810 | +0.1810 | 0.0002 | +0.5412 | +0.6650 | 1.000 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Cluster 34 | +1 | +0.1004 | +0.1802 | +0.1784 | 0.0002 | +0.4287 | +0.6835 | 0.883 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 46 | +1 | +0.1066 | +0.1802 | +0.1790 | 0.0002 | +0.5065 | +0.6917 | 0.977 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Cluster 20 | +1 | +0.1086 | +0.1800 | +0.1788 | 0.0002 | +0.6440 | +0.7396 | 0.926 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 25 | +1 | +0.1087 | +0.1775 | +0.1764 | 0.0002 | +0.5482 | +0.6922 | 0.859 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Cluster 12 | +1 | +0.1031 | +0.1772 | +0.1773 | 0.0002 | +0.4427 | +0.6886 | 0.851 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 10 | +1 | +0.0634 | +0.1767 | +0.1756 | 0.0002 | +0.5581 | +0.7087 | 0.652 |
| `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression` | Cluster 24 | +1 | +0.0487 | +0.1762 | +0.1755 | 0.0002 | +0.4718 | +0.6660 | 0.879 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 46 | +1 | +0.1074 | +0.1758 | +0.1744 | 0.0004 | +0.5965 | +0.7406 | 0.932 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 0 | +1 | +0.1368 | +0.1755 | +0.1750 | 0.0004 | +0.6450 | +0.7385 | 0.971 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 22 | +1 | +0.1154 | +0.1743 | +0.1739 | 0.0006 | +0.6045 | +0.7679 | 1.000 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 12 | +1 | +0.1250 | +0.1737 | +0.1729 | 0.0006 | +0.6310 | +0.7499 | 0.943 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 46 | +1 | +0.0998 | +0.1735 | +0.1724 | 0.0006 | +0.5618 | +0.7072 | 0.975 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 25 | +1 | +0.0993 | +0.1734 | +0.1721 | 0.0006 | +0.6641 | +0.7051 | 0.881 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 34 | +1 | +0.1036 | +0.1707 | +0.1690 | 0.0006 | +0.5198 | +0.6835 | 0.677 |
| `combo_tri_max__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 46 | +1 | +0.0978 | +0.1706 | +0.1696 | 0.0006 | +0.4824 | +0.6958 | 0.946 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | Cluster 1 | +1 | +0.1035 | +0.1698 | +0.1679 | 0.0008 | +0.5695 | +0.7123 | 0.851 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 0 | +1 | +0.1201 | +0.1686 | +0.1682 | 0.0008 | +0.5750 | +0.7123 | 0.908 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 25 | +1 | +0.1016 | +0.1672 | +0.1666 | 0.0010 | +0.7432 | +0.7545 | 0.894 |
| `open_to_current_return` | Cluster 5 | +1 | +0.1077 | +0.1669 | +0.1665 | 0.0010 | +0.6878 | +0.7581 | 1.000 |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | Cluster 34 | +1 | +0.1061 | +0.1662 | +0.1640 | 0.0012 | +0.5196 | +0.6804 | 0.857 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1237 | +0.1662 | +0.1648 | 0.0012 | +0.5053 | +0.6902 | 0.927 |
| `combo_mean__first_bar_sentiment__max_down_ret` | Cluster 36 | +1 | +0.1113 | +0.1661 | +0.1662 | 0.0012 | +0.6094 | +0.7164 | 0.902 |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | Cluster 8 | +1 | +0.1139 | +0.1649 | +0.1635 | 0.0014 | +0.4405 | +0.6629 | 0.868 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__net_volume_flow` | Cluster 46 | +1 | +0.1219 | +0.1642 | +0.1626 | 0.0014 | +0.5351 | +0.6912 | 0.939 |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | Cluster 21 | +1 | +0.1024 | +0.1638 | +0.1646 | 0.0014 | +0.4435 | +0.6747 | 0.841 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 4 | +1 | +0.1092 | +0.1623 | +0.1608 | 0.0014 | +0.6035 | +0.7102 | 0.922 |
| `combo_sig_product__max_up_ret__high_low_sequence_momentum` | Cluster 27 | +1 | +0.1076 | +0.1607 | +0.1599 | 0.0018 | +0.4172 | +0.6613 | 0.926 |
| `combo_max__trend_bar_close_consistency__first_bar_sentiment` | Cluster 41 | +1 | +0.1064 | +0.1575 | +0.1577 | 0.0022 | +0.4035 | +0.6799 | 0.950 |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | Cluster 12 | +1 | +0.1004 | +0.1574 | +0.1569 | 0.0022 | +0.4343 | +0.6706 | 0.938 |
| `morning_volume_weighted_momentum` | Cluster 5 | +1 | +0.1068 | +0.1559 | +0.1555 | 0.0024 | +0.5888 | +0.7118 | 0.924 |
| `combo_tri_median__max_up_ret__smooth_momentum_structure__net_volume_flow` | Cluster 6 | +1 | +0.0946 | +0.1550 | +0.1542 | 0.0024 | +0.5390 | +0.7005 | 0.971 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Cluster 21 | +1 | +0.1155 | +0.1543 | +0.1543 | 0.0024 | +0.5723 | +0.7051 | 0.882 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Cluster 38 | +1 | +0.1042 | +0.1539 | +0.1533 | 0.0024 | +0.4765 | +0.6706 | 0.941 |
| `combo_max__high_low_sequence_momentum__max_down_ret` | Cluster 9 | +1 | +0.1006 | +0.1538 | +0.1534 | 0.0024 | +0.4683 | +0.7036 | 0.949 |
| `vwap_close_divergence_trend` | Cluster 26 | +1 | +0.0926 | +0.1534 | +0.1529 | 0.0024 | +0.5998 | +0.7046 | 0.879 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Cluster 35 | +1 | +0.1111 | +0.1523 | +0.1495 | 0.0030 | +0.5684 | +0.6840 | 0.818 |
| `max_down_ret` | Cluster 36 | +1 | +0.1028 | +0.1510 | +0.1514 | 0.0032 | +0.5796 | +0.7066 | 0.947 |
| `combo_sig_product__max_up_ret__body_size_progression` | Cluster 35 | +1 | +0.1015 | +0.1469 | +0.1447 | 0.0040 | +0.5569 | +0.6804 | 0.948 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Cluster 34 | +1 | +0.1022 | +0.1469 | +0.1469 | 0.0040 | +0.5005 | +0.6675 | 0.127 |
| `bar_body_rng_0` | Cluster 12 | +1 | +0.1136 | +0.1378 | +0.1385 | 0.0060 | +0.4920 | +0.6680 | 0.919 |
| `vwap_trend_channel_slope` | Cluster 26 | +1 | +0.0953 | +0.1370 | +0.1363 | 0.0064 | +0.5846 | +0.6943 | 0.940 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | Cluster 8 | +1 | +0.1085 | +0.1343 | +0.1330 | 0.0078 | +0.4120 | +0.6567 | 0.950 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_day_regime_conviction` | Cluster 10 | +1 | +0.0532 | +0.1321 | +0.1313 | 0.0092 | +0.4439 | +0.6639 | 0.891 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 12 | +1 | +0.1064 | +0.1309 | +0.1303 | 0.0092 | +0.4888 | +0.6897 | 0.975 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 30 | +1 | +0.1292 | +0.1284 | +0.1268 | 0.0104 | +0.3894 | +0.6943 | 0.899 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 46 | +1 | +0.1190 | +0.1257 | +0.1240 | 0.0116 | +0.5504 | +0.6886 | 0.973 |
| `num_up_bars` | Cluster 24 | +1 | +0.0907 | +0.1213 | +0.1198 | 0.0144 | +0.3576 | +0.6531 | 0.833 |
| `combo_sig_product__net_volume_flow__max_down_ret` | Cluster 21 | +1 | +0.0967 | +0.1207 | +0.1196 | 0.0146 | +0.4767 | +0.6624 | 0.905 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Cluster 37 | +1 | +0.1195 | +0.1205 | +0.1201 | 0.0150 | +0.4378 | +0.6536 | 0.898 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 41 | +1 | +0.1386 | +0.3801 | +0.3803 | 0.0000 | +1.2371 | +0.8770 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 39 | +1 | +0.1375 | +0.3408 | +0.3403 | 0.0000 | +0.9333 | +0.8137 | 0.974 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 43 | +1 | +0.1264 | +0.3403 | +0.3403 | 0.0000 | +0.9629 | +0.8332 | 0.964 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 47 | +1 | +0.1413 | +0.3360 | +0.3352 | 0.0000 | +1.0526 | +0.8322 | 0.835 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 47 | +1 | +0.1407 | +0.3352 | +0.3344 | 0.0000 | +1.2363 | +0.8852 | 0.950 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 40 | +1 | +0.1361 | +0.3342 | +0.3337 | 0.0000 | +0.8929 | +0.7957 | 0.940 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Cluster 41 | +1 | +0.1324 | +0.3317 | +0.3317 | 0.0000 | +1.0364 | +0.8384 | 0.948 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 44 | +1 | +0.1365 | +0.3304 | +0.3302 | 0.0000 | +1.2083 | +0.8662 | 0.932 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 11 | +1 | +0.1340 | +0.3215 | +0.3208 | 0.0000 | +0.8853 | +0.7895 | 0.871 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 9 | +1 | +0.1256 | +0.3197 | +0.3193 | 0.0000 | +1.0333 | +0.8435 | 0.963 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 9 | +1 | +0.1268 | +0.3122 | +0.3118 | 0.0000 | +0.9771 | +0.8235 | 0.926 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 39 | +1 | +0.1335 | +0.3040 | +0.3035 | 0.0000 | +0.8353 | +0.7766 | 0.923 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 11 | +1 | +0.1320 | +0.2967 | +0.2960 | 0.0000 | +0.8626 | +0.7921 | 0.939 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 8 | +1 | +0.1057 | +0.2931 | +0.2931 | 0.0000 | +0.8018 | +0.7766 | 1.000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 11 | +1 | +0.1369 | +0.2925 | +0.2914 | 0.0000 | +0.7572 | +0.7679 | 1.000 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 43 | +1 | +0.1165 | +0.2920 | +0.2917 | 0.0000 | +0.7272 | +0.7391 | 0.939 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | Cluster 43 | +1 | +0.1193 | +0.2909 | +0.2908 | 0.0000 | +0.7749 | +0.7560 | 0.965 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 47 | +1 | +0.1385 | +0.2890 | +0.2872 | 0.0000 | +0.8075 | +0.7818 | 0.876 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 47 | +1 | +0.1332 | +0.2885 | +0.2871 | 0.0000 | +0.9380 | +0.8039 | 0.992 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 11 | +1 | +0.1364 | +0.2881 | +0.2871 | 0.0000 | +0.8502 | +0.7890 | 0.981 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 39 | +1 | +0.1286 | +0.2870 | +0.2861 | 0.0000 | +0.8390 | +0.8188 | 0.933 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 11 | +1 | +0.1329 | +0.2864 | +0.2852 | 0.0000 | +0.8006 | +0.7777 | 0.942 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 11 | +1 | +0.1289 | +0.2854 | +0.2851 | 0.0000 | +0.7943 | +0.8049 | 0.945 |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | Cluster 11 | +1 | +0.1225 | +0.2832 | +0.2830 | 0.0000 | +0.7505 | +0.7864 | 1.000 |
| `combo_min__limit_down_proximity_early__volume_weighted_price_position` | Cluster 7 | +1 | +0.0981 | +0.2796 | +0.2799 | 0.0000 | +0.8639 | +0.8070 | 0.872 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 40 | +1 | +0.1235 | +0.2785 | +0.2777 | 0.0000 | +0.7573 | +0.7622 | 0.974 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Cluster 11 | +1 | +0.1274 | +0.2782 | +0.2779 | 0.0000 | +0.7446 | +0.7864 | 0.885 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 12 | +1 | +0.1165 | +0.2780 | +0.2763 | 0.0000 | +0.9388 | +0.8338 | 0.897 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 8 | +1 | +0.1146 | +0.2774 | +0.2769 | 0.0000 | +0.7870 | +0.7931 | 0.901 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 12 | +1 | +0.1133 | +0.2769 | +0.2751 | 0.0000 | +0.8994 | +0.8415 | 0.968 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 32 | +1 | +0.1283 | +0.2696 | +0.2694 | 0.0000 | +0.8704 | +0.7998 | 0.903 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 13 | +1 | +0.1126 | +0.2653 | +0.2632 | 0.0000 | +0.6774 | +0.7288 | 0.852 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 5 | +1 | +0.1282 | +0.2638 | +0.2625 | 0.0000 | +1.0263 | +0.8435 | 0.926 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 47 | +1 | +0.1375 | +0.2636 | +0.2619 | 0.0000 | +0.9520 | +0.8260 | 0.917 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 35 | +1 | +0.1210 | +0.2622 | +0.2622 | 0.0000 | +0.8174 | +0.7560 | 0.914 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Cluster 33 | +1 | +0.1132 | +0.2620 | +0.2622 | 0.0000 | +0.8594 | +0.7885 | 0.913 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 47 | +1 | +0.1322 | +0.2593 | +0.2579 | 0.0000 | +0.8587 | +0.7895 | 0.939 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 33 | +1 | +0.1186 | +0.2553 | +0.2560 | 0.0000 | +0.7522 | +0.7838 | 0.928 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 10 | +1 | +0.1362 | +0.2533 | +0.2532 | 0.0000 | +0.8112 | +0.7694 | 0.980 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Cluster 35 | +1 | +0.1149 | +0.2511 | +0.2513 | 0.0000 | +0.7559 | +0.7560 | 0.941 |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | Cluster 7 | +1 | +0.0954 | +0.2498 | +0.2501 | 0.0000 | +0.7952 | +0.7735 | 0.879 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 47 | +1 | +0.1187 | +0.2480 | +0.2465 | 0.0000 | +0.7656 | +0.7777 | 0.838 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 20 | +1 | +0.1064 | +0.2480 | +0.2489 | 0.0000 | +0.6380 | +0.7221 | 0.849 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 45 | +1 | +0.0996 | +0.2468 | +0.2472 | 0.0000 | +0.7183 | +0.7838 | 1.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 0 | +1 | +0.1128 | +0.2467 | +0.2471 | 0.0000 | +0.8567 | +0.7895 | 0.934 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 6 | +1 | +0.0918 | +0.2467 | +0.2465 | 0.0000 | +0.7058 | +0.7648 | 0.507 |
| `combo_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 12 | +1 | +0.0877 | +0.2465 | +0.2453 | 0.0000 | +0.6740 | +0.7319 | 1.000 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Cluster 47 | +1 | +0.1331 | +0.2459 | +0.2439 | 0.0000 | +0.6629 | +0.7524 | 0.943 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Cluster 37 | +1 | +0.1101 | +0.2457 | +0.2456 | 0.0000 | +0.7346 | +0.7612 | 0.928 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 47 | +1 | +0.1219 | +0.2452 | +0.2443 | 0.0000 | +0.7611 | +0.7674 | 0.877 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 5 | +1 | +0.1133 | +0.2435 | +0.2428 | 0.0000 | +0.8926 | +0.8116 | 0.981 |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | Cluster 46 | +1 | +0.1184 | +0.2434 | +0.2430 | 0.0000 | +0.6100 | +0.7427 | 1.000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 32 | +1 | +0.1172 | +0.2433 | +0.2432 | 0.0000 | +0.6826 | +0.7437 | 0.946 |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | Cluster 42 | +1 | +0.1233 | +0.2422 | +0.2410 | 0.0000 | +0.6208 | +0.7082 | 0.944 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 47 | +1 | +0.1215 | +0.2413 | +0.2405 | 0.0000 | +0.7630 | +0.7627 | 0.920 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 6 | +1 | +0.0988 | +0.2407 | +0.2389 | 0.0000 | +0.7062 | +0.7787 | 0.822 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Cluster 15 | +1 | +0.1158 | +0.2401 | +0.2408 | 0.0000 | +0.6555 | +0.7118 | 0.840 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 36 | +1 | +0.1230 | +0.2399 | +0.2387 | 0.0000 | +0.7677 | +0.7849 | 0.942 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 37 | +1 | +0.1115 | +0.2387 | +0.2388 | 0.0000 | +0.6329 | +0.7272 | 0.927 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 4 | +1 | +0.0917 | +0.2380 | +0.2374 | 0.0000 | +0.7177 | +0.7828 | 0.900 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | Cluster 6 | +1 | +0.0941 | +0.2378 | +0.2380 | 0.0000 | +0.6599 | +0.7473 | 0.949 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 6 | +1 | +0.0926 | +0.2377 | +0.2376 | 0.0000 | +0.5934 | +0.7283 | 0.874 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 47 | +1 | +0.1185 | +0.2367 | +0.2353 | 0.0000 | +0.7438 | +0.7741 | 0.911 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 47 | +1 | +0.1188 | +0.2358 | +0.2340 | 0.0000 | +0.7567 | +0.7458 | 0.930 |
| `opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1150 | +0.2357 | +0.2357 | 0.0000 | +0.7774 | +0.7545 | 0.928 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 1 | +1 | +0.1152 | +0.2356 | +0.2340 | 0.0000 | +0.8327 | +0.7890 | 0.794 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1022 | +0.2353 | +0.2355 | 0.0000 | +0.7220 | +0.7267 | 0.952 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 5 | +1 | +0.1182 | +0.2351 | +0.2346 | 0.0000 | +0.7805 | +0.7550 | 0.933 |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 2 | +1 | +0.1032 | +0.2329 | +0.2328 | 0.0000 | +0.5958 | +0.7082 | 0.865 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 36 | +1 | +0.1236 | +0.2325 | +0.2317 | 0.0000 | +0.7849 | +0.8003 | 0.950 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 32 | +1 | +0.1239 | +0.2322 | +0.2318 | 0.0000 | +0.8503 | +0.7926 | 0.941 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 15 | +1 | +0.1175 | +0.2313 | +0.2317 | 0.0000 | +0.6298 | +0.7005 | 0.912 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 37 | +1 | +0.1208 | +0.2299 | +0.2298 | 0.0000 | +0.6544 | +0.7247 | 0.943 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 6 | +1 | +0.1104 | +0.2297 | +0.2299 | 0.0000 | +0.7790 | +0.8065 | 0.943 |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | Cluster 33 | +1 | +0.1145 | +0.2285 | +0.2289 | 0.0000 | +0.6644 | +0.7437 | 0.946 |
| `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early` | Cluster 11 | +1 | +0.1203 | +0.2239 | +0.2237 | 0.0000 | +0.6347 | +0.7164 | 0.943 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 4 | +1 | +0.0915 | +0.2239 | +0.2237 | 0.0000 | +0.7930 | +0.7880 | 0.977 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 3 | +1 | +0.1030 | +0.2231 | +0.2230 | 0.0000 | +0.6816 | +0.7504 | 0.885 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Cluster 29 | +1 | +0.1176 | +0.2217 | +0.2222 | 0.0000 | +0.8068 | +0.7597 | 0.962 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 4 | +1 | +0.1112 | +0.2167 | +0.2161 | 0.0000 | +0.7488 | +0.7422 | 0.999 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 34 | +1 | +0.1124 | +0.2165 | +0.2165 | 0.0000 | +0.5730 | +0.7221 | 0.965 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 6 | +1 | +0.1050 | +0.2163 | +0.2151 | 0.0000 | +0.5095 | +0.7267 | 0.912 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | Cluster 0 | +1 | +0.1149 | +0.2160 | +0.2168 | 0.0000 | +0.4976 | +0.6850 | 0.939 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 33 | +1 | +0.1132 | +0.2148 | +0.2156 | 0.0000 | +0.6667 | +0.7478 | 0.953 |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | Cluster 0 | +1 | +0.1226 | +0.2118 | +0.2126 | 0.0000 | +0.7037 | +0.7622 | 0.947 |
| `max_up_ret` | Cluster 5 | +1 | +0.1114 | +0.2091 | +0.2080 | 0.0000 | +0.9114 | +0.8132 | 0.913 |
| `combo_mean__max_up_ret__bar_ret_0` | Cluster 35 | +1 | +0.1141 | +0.2089 | +0.2087 | 0.0000 | +0.6310 | +0.7566 | 1.000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 13 | +1 | +0.1196 | +0.2077 | +0.2054 | 0.0000 | +0.6410 | +0.7370 | 0.895 |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | Cluster 0 | +1 | +0.0893 | +0.2068 | +0.2059 | 0.0000 | +0.4704 | +0.6794 | 0.807 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 12 | +1 | +0.1013 | +0.2057 | +0.2041 | 0.0000 | +0.7372 | +0.7699 | 0.927 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Cluster 25 | +1 | +0.1159 | +0.2039 | +0.2024 | 0.0000 | +0.7503 | +0.7231 | 0.895 |
| `combo_max__max_up_ret__impulse_bar_dominance` | Cluster 18 | +1 | +0.1001 | +0.2036 | +0.2027 | 0.0000 | +0.8439 | +0.7926 | 0.863 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 27 | +1 | +0.1171 | +0.2034 | +0.2027 | 0.0000 | +0.6135 | +0.7308 | 0.967 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 1 | +1 | +0.0864 | +0.2028 | +0.2020 | 0.0000 | +0.4631 | +0.6778 | 0.546 |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | Cluster 17 | +1 | +0.0916 | +0.2020 | +0.2008 | 0.0000 | +0.7231 | +0.7545 | 0.875 |
| `combo_rank_min__bar_body_rng_0__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.0921 | +0.2017 | +0.2023 | 0.0000 | +0.6695 | +0.7308 | 0.949 |
| `combo_min__limit_down_proximity_early__impulse_bar_dominance` | Cluster 13 | +1 | +0.0950 | +0.2009 | +0.1995 | 0.0000 | +0.5349 | +0.7092 | 0.883 |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | Cluster 19 | +1 | +0.0941 | +0.2003 | +0.2011 | 0.0000 | +0.5653 | +0.7123 | 0.886 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 27 | +1 | +0.1249 | +0.2001 | +0.1990 | 0.0000 | +0.6117 | +0.7108 | 0.966 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 6 | +1 | +0.0983 | +0.1987 | +0.1960 | 0.0000 | +0.5182 | +0.6855 | 0.746 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 4 | +1 | +0.1050 | +0.1984 | +0.1975 | 0.0000 | +0.7656 | +0.7648 | 0.924 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 5 | +1 | +0.1159 | +0.1947 | +0.1949 | 0.0002 | +0.8814 | +0.8127 | 0.885 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.0883 | +0.1940 | +0.1952 | 0.0002 | +0.6258 | +0.7118 | 0.786 |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | Cluster 38 | +1 | +0.1093 | +0.1936 | +0.1931 | 0.0002 | +0.5769 | +0.7144 | 0.906 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 29 | +1 | +0.1088 | +0.1929 | +0.1933 | 0.0002 | +0.6112 | +0.7102 | 0.940 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 23 | +1 | +0.0906 | +0.1923 | +0.1916 | 0.0002 | +0.6414 | +0.7463 | 0.877 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Cluster 1 | +1 | +0.1233 | +0.1916 | +0.1896 | 0.0002 | +0.5834 | +0.7133 | 0.855 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | Cluster 21 | +1 | +0.1175 | +0.1912 | +0.1910 | 0.0002 | +0.4525 | +0.6835 | 0.817 |
| `combo_rank_min__max_up_ret__volume_weighted_price_position` | Cluster 20 | +1 | +0.1028 | +0.1904 | +0.1908 | 0.0002 | +0.4855 | +0.7123 | 0.909 |
| `combo_max__star50_limit_proximity_early__first_bar_return` | Cluster 27 | +1 | +0.1145 | +0.1892 | +0.1884 | 0.0004 | +0.5569 | +0.6994 | 0.981 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 25 | +1 | +0.1210 | +0.1889 | +0.1875 | 0.0004 | +0.4934 | +0.6897 | 0.938 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 25 | +1 | +0.1127 | +0.1878 | +0.1863 | 0.0004 | +0.5725 | +0.6814 | 0.963 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 21 | +1 | +0.1189 | +0.1874 | +0.1876 | 0.0004 | +0.6157 | +0.7247 | 1.000 |
| `net_volume_flow` | Cluster 4 | +1 | +0.0815 | +0.1871 | +0.1873 | 0.0004 | +0.6489 | +0.7272 | 0.909 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 25 | +1 | +0.1175 | +0.1865 | +0.1852 | 0.0004 | +0.5493 | +0.6861 | 0.944 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 1 | +1 | +0.1429 | +0.1852 | +0.1839 | 0.0004 | +0.5265 | +0.6794 | 1.000 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Cluster 0 | +1 | +0.0893 | +0.1846 | +0.1851 | 0.0004 | +0.3821 | +0.6572 | 0.921 |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | Cluster 13 | +1 | +0.0975 | +0.1840 | +0.1821 | 0.0004 | +0.5131 | +0.6824 | 0.923 |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | Cluster 26 | +1 | +0.1110 | +0.1824 | +0.1820 | 0.0004 | +0.4856 | +0.6675 | 0.895 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Cluster 1 | +1 | +0.1120 | +0.1819 | +0.1803 | 0.0004 | +0.4602 | +0.6799 | 0.768 |
| `volatility_expansion_trend_vector` | Cluster 4 | +1 | +0.0820 | +0.1817 | +0.1810 | 0.0004 | +0.5987 | +0.7319 | 0.943 |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | Cluster 29 | +1 | +0.1102 | +0.1800 | +0.1803 | 0.0006 | +0.4852 | +0.6557 | 0.929 |
| `combo_diff__max_up_ret__late_bar_momentum` | Cluster 24 | +1 | +0.1100 | +0.1794 | +0.1795 | 0.0008 | +0.4678 | +0.6974 | 0.841 |
| `combo_mean__first_bar_return__volume_weighted_price_position` | Cluster 0 | +1 | +0.1080 | +0.1783 | +0.1799 | 0.0010 | +0.4256 | +0.6619 | 0.871 |
| `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | Cluster 4 | +1 | +0.0854 | +0.1772 | +0.1763 | 0.0010 | +0.6257 | +0.7329 | 0.957 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 25 | +1 | +0.1238 | +0.1738 | +0.1730 | 0.0012 | +0.5033 | +0.6603 | 0.959 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 25 | +1 | +0.1070 | +0.1709 | +0.1697 | 0.0012 | +0.4793 | +0.6747 | 0.908 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Cluster 6 | +1 | +0.0557 | +0.1698 | +0.1696 | 0.0012 | +0.5148 | +0.6505 | 0.510 |
| `combo_max__bar_body_rng_0__limit_down_proximity_early` | Cluster 28 | +1 | +0.0942 | +0.1686 | +0.1681 | 0.0012 | +0.4242 | +0.6737 | 0.907 |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | Cluster 18 | +1 | +0.0888 | +0.1651 | +0.1654 | 0.0016 | +0.4389 | +0.6598 | 0.850 |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | Cluster 31 | +1 | +0.1001 | +0.1631 | +0.1632 | 0.0016 | +0.4064 | +0.6711 | 0.925 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 26 | +1 | +0.1139 | +0.1626 | +0.1625 | 0.0016 | +0.5747 | +0.6675 | 0.931 |
| `combo_max__first_bar_sentiment__bar_ret_0` | Cluster 0 | +1 | +0.1078 | +0.1618 | +0.1631 | 0.0018 | +0.4986 | +0.6809 | 0.931 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Cluster 0 | +1 | +0.1064 | +0.1602 | +0.1611 | 0.0022 | +0.5019 | +0.7298 | 0.833 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Cluster 0 | +1 | +0.0981 | +0.1591 | +0.1596 | 0.0022 | +0.4804 | +0.6866 | 0.924 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 0 | +1 | +0.1015 | +0.1561 | +0.1557 | 0.0026 | +0.6635 | +0.7319 | 0.947 |
| `trend_bar_close_consistency` | Cluster 14 | +1 | +0.0595 | +0.1553 | +0.1549 | 0.0028 | +0.4516 | +0.6758 | 0.921 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 13 | +1 | +0.0947 | +0.1541 | +0.1522 | 0.0032 | +0.5754 | +0.6989 | 0.920 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 42 | +1 | +0.1116 | +0.1539 | +0.1533 | 0.0032 | +0.6312 | +0.7128 | 0.939 |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | Cluster 0 | +1 | +0.1079 | +0.1526 | +0.1536 | 0.0034 | +0.5372 | +0.7072 | 1.000 |
| `combo_max__first_bar_return__impulse_bar_dominance` | Cluster 18 | +1 | +0.0908 | +0.1516 | +0.1517 | 0.0036 | +0.4635 | +0.6706 | 0.920 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 16 | +1 | +0.1166 | +0.1484 | +0.1481 | 0.0038 | +0.3427 | +0.6526 | 0.847 |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | Cluster 0 | +1 | +0.0962 | +0.1483 | +0.1490 | 0.0040 | +0.5376 | +0.7118 | 0.948 |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 6 | +1 | +0.0858 | +0.1482 | +0.1479 | 0.0044 | +0.4066 | +0.6634 | 0.914 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Cluster 16 | +1 | +0.1104 | +0.1264 | +0.1264 | 0.0144 | +0.4097 | +0.6768 | 0.867 |
| `combo_z_sum__yesterday_first_30min_return__yesterday_early_trend` | Cluster 6 | +1 | +0.0675 | +0.1124 | +0.1121 | 0.0294 | +0.3706 | +0.6531 | 0.932 |

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
| 300ETF | single | 97 | 41 | 0.2737 | `[8, 7, 6, 5, 5, 5, 4, 3, 2, 2, 2, 2, ... (41 clusters)]` |
| 500ETF | single | 159 | 47 | 0.2603 | `[12, 10, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, ... (47 clusters)]` |
| 159915ETF | single | 146 | 48 | 0.2140 | `[12, 12, 10, 9, 7, 6, 5, 5, 5, 4, 4, 3, ... (48 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 1 | 0.2737 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 1 | 2 | 0.2737 | `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 2 | 1 | 0.2737 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | _(none)_ |
| 300ETF | single | Cluster 3 | 2 | 0.2737 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 4 | 2 | 0.2737 | `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 5 | 2 | 0.2737 | `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 6 | 3 | 0.2737 | `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | `combo_max__first_bar_return__opening_drive_thrust_ratio`, `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 7 | 2 | 0.2737 | `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 8 | 2 | 0.2737 | `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` |
| 300ETF | single | Cluster 9 | 2 | 0.2737 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 10 | 6 | 0.2737 | `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_mean__max_up_ret__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position`, `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 11 | 8 | 0.2737 | `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_min__first_bar_return__bar_body_rng_0`, `first_bar_return`, `combo_mean__first_bar_return__first_bar_sentiment`, `combo_sig_product__bar_ret_0__bar_body_rng_0`, `combo_ratio__first_bar_return__volume_surge_direction` |
| 300ETF | single | Cluster 12 | 1 | 0.2737 | `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | _(none)_ |
| 300ETF | single | Cluster 13 | 2 | 0.2737 | `combo_sig_product__first_bar_return__volume_weighted_price_position` | `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 14 | 4 | 0.2737 | `combo_max__volume_weighted_price_position__volume_surge_direction` | `combo_mean__volume_weighted_price_position__first_bar_sentiment`, `combo_mean__volume_weighted_price_position__volume_surge_direction`, `combo_min__volume_weighted_price_position__volume_surge_direction` |
| 300ETF | single | Cluster 15 | 5 | 0.2737 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_rank_max__max_up_ret__first_bar_return`, `combo_mean__max_up_ret__bar_body_rng_0`, `combo_max__max_up_ret__bar_ret_0`, `combo_min__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 16 | 2 | 0.2737 | `combo_diff__max_up_ret__early_vwap_acceleration` | `combo_rel_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 17 | 2 | 0.2737 | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 18 | 7 | 0.2737 | `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `max_up_ret`, `combo_rank_max__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio`, `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` |
| 300ETF | single | Cluster 19 | 1 | 0.2737 | `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | _(none)_ |
| 300ETF | single | Cluster 20 | 5 | 0.2737 | `combo_mean__max_up_ret__volume_surge_direction` | `combo_rank_min__max_up_ret__volume_surge_direction`, `combo_min__opening_drive_thrust_ratio__volume_surge_direction`, `combo_min__max_up_ret__volume_surge_direction`, `combo_min__max_up_ret__first_bar_sentiment` |
| 300ETF | single | Cluster 21 | 1 | 0.2737 | `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 22 | 2 | 0.2737 | `volume_weighted_price_position` | `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 23 | 2 | 0.2737 | `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 24 | 2 | 0.2737 | `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | `open_to_current_return` |
| 300ETF | single | Cluster 25 | 2 | 0.2737 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 26 | 2 | 0.2737 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 300ETF | single | Cluster 27 | 2 | 0.2737 | `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 28 | 2 | 0.2737 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 29 | 1 | 0.2737 | `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 30 | 5 | 0.2737 | `combo_min__bar_body_rng_0__volume_surge_direction` | `combo_max__first_bar_return__volume_surge_direction`, `combo_rank_max__first_bar_return__volume_surge_direction`, `combo_min__first_bar_return__volume_surge_direction`, `combo_max__first_bar_sentiment__volume_surge_direction` |
| 300ETF | single | Cluster 31 | 2 | 0.2737 | `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `combo_rank_max__bar_ret_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 32 | 1 | 0.2737 | `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 33 | 2 | 0.2737 | `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 34 | 1 | 0.2737 | `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 35 | 2 | 0.2737 | `combo_max__max_up_ret__volume_surge_direction` | `combo_rank_max__max_up_ret__volume_surge_direction` |
| 300ETF | single | Cluster 36 | 1 | 0.2737 | `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0` | _(none)_ |
| 300ETF | single | Cluster 37 | 1 | 0.2737 | `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 38 | 1 | 0.2737 | `combo_max__max_up_ret__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 39 | 1 | 0.2737 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 40 | 2 | 0.2737 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 500ETF | single | Cluster 0 | 10 | 0.2603 | `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_mean__opening_drive_thrust_ratio__first_bar_return`, `combo_min__opening_drive_thrust_ratio__first_bar_return`, `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`, `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`, `combo_rank_max__opening_drive_thrust_ratio__max_down_ret`, `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_mean__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 1 | 2 | 0.2603 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` |
| 500ETF | single | Cluster 2 | 2 | 0.2603 | `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression` |
| 500ETF | single | Cluster 3 | 5 | 0.2603 | `combo_rank_max__net_volume_flow__close_vs_open_range` | `combo_min__net_volume_flow__close_vs_open_range`, `combo_tri_mean__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector`, `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`, `combo_max__close_vs_open_range__early_body_momentum` |
| 500ETF | single | Cluster 4 | 2 | 0.2603 | `combo_max__max_up_ret__early_body_momentum` | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 5 | 2 | 0.2603 | `open_to_current_return` | `morning_volume_weighted_momentum` |
| 500ETF | single | Cluster 6 | 1 | 0.2603 | `combo_tri_median__max_up_ret__smooth_momentum_structure__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 7 | 1 | 0.2603 | `combo_min__max_up_ret__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 8 | 12 | 0.2603 | `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_clamp_diff__max_up_ret__late_bar_momentum`, `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__body_size_progression`, `combo_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`, `combo_sig_product__opening_drive_thrust_ratio__body_size_progression`, `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` |
| 500ETF | single | Cluster 9 | 8 | 0.2603 | `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | `combo_mean__net_volume_flow__max_down_ret`, `combo_rank_min__high_low_sequence_momentum__max_down_ret`, `combo_rank_max__volatility_expansion_trend_vector__max_down_ret`, `combo_min__volatility_expansion_trend_vector__max_down_ret`, `combo_max__net_volume_flow__max_down_ret`, `combo_max__close_vs_open_range__max_down_ret`, `combo_max__high_low_sequence_momentum__max_down_ret` |
| 500ETF | single | Cluster 10 | 2 | 0.2603 | `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `combo_clamp_diff__opening_drive_thrust_ratio__trend_day_regime_conviction` |
| 500ETF | single | Cluster 11 | 8 | 0.2603 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_min__net_volume_flow__star50_limit_proximity_early`, `combo_mean__star50_limit_proximity_early__close_vs_open_range`, `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_min__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_rank_min__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 12 | 9 | 0.2603 | `combo_mean__first_bar_sentiment__bar_ret_0` | `combo_rank_min__first_bar_sentiment__bar_ret_0`, `combo_sig_product__first_bar_sentiment__first_bar_return`, `combo_rank_max__net_volume_flow__first_bar_sentiment`, `combo_sig_product__first_bar_sentiment__early_body_momentum`, `combo_rank_min__max_up_ret__first_bar_sentiment`, `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_rank_min__first_bar_sentiment__early_body_momentum`, `bar_body_rng_0` |
| 500ETF | single | Cluster 13 | 6 | 0.2603 | `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`, `combo_rel_diff__star50_limit_proximity_early__body_size_progression`, `combo_diff__star50_limit_proximity_early__body_size_progression` |
| 500ETF | single | Cluster 14 | 2 | 0.2603 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | `combo_min__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 15 | 2 | 0.2603 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 16 | 3 | 0.2603 | `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`, `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` |
| 500ETF | single | Cluster 17 | 1 | 0.2603 | `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | _(none)_ |
| 500ETF | single | Cluster 18 | 3 | 0.2603 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 19 | 1 | 0.2603 | `combo_rank_max__max_up_ret__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 20 | 2 | 0.2603 | `combo_min__max_up_ret__close_vs_open_range` | `combo_rank_min__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 21 | 4 | 0.2603 | `combo_sig_product__net_volume_flow__first_bar_return` | `combo_sig_product__high_low_sequence_momentum__first_bar_return`, `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`, `combo_sig_product__net_volume_flow__max_down_ret` |
| 500ETF | single | Cluster 22 | 1 | 0.2603 | `combo_sig_product__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 23 | 2 | 0.2603 | `early_order_flow_imbalance` | `always_in_trend_persistence` |
| 500ETF | single | Cluster 24 | 2 | 0.2603 | `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression` | `num_up_bars` |
| 500ETF | single | Cluster 25 | 6 | 0.2603 | `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_mean__star50_limit_proximity_early__max_down_ret`, `combo_rank_max__star50_limit_proximity_early__max_down_ret`, `combo_min__star50_limit_proximity_early__max_down_ret`, `combo_rank_min__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 26 | 2 | 0.2603 | `vwap_close_divergence_trend` | `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 27 | 2 | 0.2603 | `combo_sig_product__max_up_ret__early_body_momentum` | `combo_sig_product__max_up_ret__high_low_sequence_momentum` |
| 500ETF | single | Cluster 28 | 1 | 0.2603 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 500ETF | single | Cluster 29 | 3 | 0.2603 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` |
| 500ETF | single | Cluster 30 | 2 | 0.2603 | `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 500ETF | single | Cluster 31 | 2 | 0.2603 | `combo_rank_max__max_up_ret__bar_ret_0` | `max_up_ret` |
| 500ETF | single | Cluster 32 | 3 | 0.2603 | `combo_mean__max_up_ret__first_bar_return` | `combo_mean__max_up_ret__first_bar_sentiment`, `combo_rank_min__max_up_ret__first_bar_return` |
| 500ETF | single | Cluster 33 | 2 | 0.2603 | `combo_rank_max__close_vs_open_range__bar_ret_0` | `combo_max__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 34 | 7 | 0.2603 | `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | `combo_sig_product__star50_limit_proximity_early__max_down_ret`, `combo_sig_product__star50_limit_proximity_early__first_bar_return`, `combo_sig_product__star50_limit_proximity_early__early_body_momentum`, `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_sig_product__star50_limit_proximity_early__body_size_progression`, `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 35 | 3 | 0.2603 | `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `combo_sig_product__max_up_ret__early_late_momentum_divergence`, `combo_sig_product__max_up_ret__body_size_progression` |
| 500ETF | single | Cluster 36 | 7 | 0.2603 | `combo_mean__first_bar_return__max_down_ret` | `combo_max__bar_ret_0__max_down_ret`, `combo_min__first_bar_return__max_down_ret`, `combo_rank_max__bar_ret_0__max_down_ret`, `combo_rank_min__first_bar_return__max_down_ret`, `combo_mean__first_bar_sentiment__max_down_ret`, `max_down_ret` |
| 500ETF | single | Cluster 37 | 5 | 0.2603 | `combo_sig_product__opening_drive_thrust_ratio__trend_day_regime_conviction` | `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`, `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`, `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 38 | 2 | 0.2603 | `combo_min__trend_day_regime_conviction__first_bar_sentiment` | `combo_min__close_vs_open_range__first_bar_sentiment` |
| 500ETF | single | Cluster 39 | 2 | 0.2603 | `combo_mean__close_vs_open_range__bar_ret_0` | `combo_mean__trend_bar_close_consistency__bar_ret_0` |
| 500ETF | single | Cluster 40 | 1 | 0.2603 | `combo_mean__net_volume_flow__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 41 | 2 | 0.2603 | `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | `combo_max__trend_bar_close_consistency__first_bar_sentiment` |
| 500ETF | single | Cluster 42 | 2 | 0.2603 | `combo_rank_max__early_body_momentum__bar_ret_0` | `combo_max__early_body_momentum__bar_ret_0` |
| 500ETF | single | Cluster 43 | 1 | 0.2603 | `combo_min__trend_bar_close_consistency__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 44 | 2 | 0.2603 | `combo_min__net_volume_flow__first_bar_return` | `combo_rank_min__net_volume_flow__first_bar_return` |
| 500ETF | single | Cluster 45 | 1 | 0.2603 | `combo_min__close_vs_open_range__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 46 | 8 | 0.2603 | `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_rank_max__star50_limit_proximity_early__close_vs_open_range`, `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`, `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_max__star50_limit_proximity_early__close_vs_open_range`, `combo_tri_max__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`, `combo_rank_max__rbreaker_sell_setup_proximity_early__net_volume_flow`, `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 0 | 12 | 0.2140 | `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`, `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return`, `combo_sig_product__first_bar_return__demark_setup_reversal_early`, `combo_rank_max__max_up_ret__first_bar_sentiment`, `combo_mean__first_bar_return__volume_weighted_price_position`, `combo_max__first_bar_sentiment__bar_ret_0`, `combo_ratio__bar_ret_0__volume_weighted_price_position`, `combo_min__first_bar_sentiment__bar_ret_0`, `combo_rank_min__max_up_ret__first_bar_sentiment`, `combo_sig_product__first_bar_sentiment__first_bar_return`, `combo_rank_min__first_bar_sentiment__first_bar_return` |
| 159915ETF | single | Cluster 1 | 5 | 0.2140 | `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`, `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 2 | 1 | 0.2140 | `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 3 | 2 | 0.2140 | `opening_drive_thrust_ratio` | `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` |
| 159915ETF | single | Cluster 4 | 7 | 0.2140 | `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_max__max_up_ret__volatility_expansion_trend_vector`, `net_volume_flow`, `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector`, `volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 5 | 5 | 0.2140 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__opening_drive_thrust_ratio__max_up_ret`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`, `max_up_ret`, `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 6 | 10 | 0.2140 | `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return`, `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`, `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`, `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`, `combo_z_sum__yesterday_first_30min_return__yesterday_early_trend` |
| 159915ETF | single | Cluster 7 | 2 | 0.2140 | `combo_min__limit_down_proximity_early__volume_weighted_price_position` | `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 8 | 2 | 0.2140 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 159915ETF | single | Cluster 9 | 2 | 0.2140 | `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 10 | 1 | 0.2140 | `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | _(none)_ |
| 159915ETF | single | Cluster 11 | 9 | 0.2140 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_diff__bar_ret_0__demark_setup_reversal_early`, `combo_rel_diff__first_bar_return__demark_setup_reversal_early`, `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 12 | 4 | 0.2140 | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector`, `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 13 | 5 | 0.2140 | `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`, `combo_min__limit_down_proximity_early__impulse_bar_dominance`, `combo_mean__limit_down_proximity_early__impulse_bar_dominance`, `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` |
| 159915ETF | single | Cluster 14 | 1 | 0.2140 | `trend_bar_close_consistency` | _(none)_ |
| 159915ETF | single | Cluster 15 | 2 | 0.2140 | `combo_max__max_up_ret__volume_weighted_price_position` | `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 16 | 2 | 0.2140 | `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` |
| 159915ETF | single | Cluster 17 | 1 | 0.2140 | `combo_rank_min__max_up_ret__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 18 | 3 | 0.2140 | `combo_max__max_up_ret__impulse_bar_dominance` | `combo_max__bar_body_rng_0__impulse_bar_dominance`, `combo_max__first_bar_return__impulse_bar_dominance` |
| 159915ETF | single | Cluster 19 | 1 | 0.2140 | `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 20 | 2 | 0.2140 | `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_rank_min__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 21 | 2 | 0.2140 | `combo_sig_product__max_up_ret__bar_body_rng_0` | `combo_sig_product__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 22 | 1 | 0.2140 | `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 23 | 1 | 0.2140 | `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 24 | 1 | 0.2140 | `combo_diff__max_up_ret__late_bar_momentum` | _(none)_ |
| 159915ETF | single | Cluster 25 | 6 | 0.2140 | `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_rank_max__max_up_ret__star50_limit_proximity_early`, `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 26 | 2 | 0.2140 | `combo_max__star50_limit_proximity_early__first_bar_sentiment` | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` |
| 159915ETF | single | Cluster 27 | 3 | 0.2140 | `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return`, `combo_max__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 28 | 1 | 0.2140 | `combo_max__bar_body_rng_0__limit_down_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 29 | 3 | 0.2140 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` |
| 159915ETF | single | Cluster 30 | 2 | 0.2140 | `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | `combo_rank_min__bar_body_rng_0__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 31 | 1 | 0.2140 | `combo_mean__bar_body_rng_0__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 32 | 3 | 0.2140 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`, `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 33 | 4 | 0.2140 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `combo_rank_min__opening_drive_thrust_ratio__first_bar_return`, `combo_min__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` |
| 159915ETF | single | Cluster 34 | 1 | 0.2140 | `combo_min__max_up_ret__bar_body_rng_0` | _(none)_ |
| 159915ETF | single | Cluster 35 | 3 | 0.2140 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0`, `combo_mean__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 36 | 2 | 0.2140 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 37 | 3 | 0.2140 | `combo_rank_max__max_up_ret__bar_body_rng_0` | `combo_max__opening_drive_thrust_ratio__bar_body_rng_0`, `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 38 | 1 | 0.2140 | `combo_max__bar_ret_0__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 39 | 3 | 0.2140 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 40 | 2 | 0.2140 | `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` |
| 159915ETF | single | Cluster 41 | 2 | 0.2140 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 42 | 2 | 0.2140 | `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 43 | 3 | 0.2140 | `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_min__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 44 | 1 | 0.2140 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | _(none)_ |
| 159915ETF | single | Cluster 45 | 1 | 0.2140 | `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 46 | 1 | 0.2140 | `combo_mean__bar_ret_0__limit_down_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 47 | 12 | 0.2140 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`, `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_rel_diff__max_up_ret__demark_setup_reversal_early`, `combo_mean__max_up_ret__star50_limit_proximity_early`, `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`, `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`, `combo_diff__max_up_ret__demark_setup_reversal_early`, `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `mean` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_min__bar_body_rng_0__volume_surge_direction` | `min` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | `mean` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_max__first_bar_return__volume_surge_direction` | `max` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__first_bar_return__volume_surge_direction` | `rank_max` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__volume_surge_direction` | `mean` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_max__max_up_ret__volume_surge_direction` | `max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `tri_mean` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | `rank_max` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_mean` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__max_up_ret__volume_surge_direction` | `rank_max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `tri_median` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | `rank_max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__max_up_ret__volume_surge_direction` | `rank_min` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_median` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `rank_min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | `max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_mean__first_bar_return__first_bar_sentiment` | `mean` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_min__first_bar_return__bar_body_rng_0` | `min` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_sig_product__bar_ret_0__bar_body_rng_0` | `sig_product` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `rank_max` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__volume_surge_direction` | `min` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__first_bar_return__volume_surge_direction` | `min` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_max__volume_weighted_price_position__volume_surge_direction` | `max` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_mean__volume_weighted_price_position__first_bar_sentiment` | `mean` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | `sig_product` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | `tri_median` | a=`smooth_momentum_structure`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | `mean` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | `min` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | `sig_product` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_max` | a=`volume_weighted_price_position`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | `sig_product` | a=`bar_ret_0`, b=`opening_drive_thrust_ratio` |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | `ratio` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_concentration` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_ratio__first_bar_return__volume_surge_direction` | `ratio` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_max__first_bar_sentiment__volume_surge_direction` | `max` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | `max` | a=`volatility_expansion_trend_vector`, b=`first_bar_sentiment` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`volatility_expansion_trend_vector` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`net_volume_flow` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__close_vs_open_range__bar_ret_0` | `mean` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`volume_weighted_momentum_acceleration` |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_min__net_volume_flow__first_bar_return` | `min` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_min__net_volume_flow__close_vs_open_range` | `min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_mean__trend_bar_close_consistency__bar_ret_0` | `mean` | a=`trend_bar_close_consistency`, b=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | `min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_mean` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_rank_min__net_volume_flow__first_bar_return` | `rank_min` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_mean__net_volume_flow__first_bar_sentiment` | `mean` | a=`net_volume_flow`, b=`first_bar_sentiment` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`net_volume_flow` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | `clamp_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | `rank_max` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_mean` | a=`max_up_ret`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_day_regime_conviction` |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | `mean` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_max__max_up_ret__net_volume_flow` | `rank_max` | a=`max_up_ret`, b=`net_volume_flow` |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | `min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_max__close_vs_open_range__first_bar_return` | `max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_max__net_volume_flow__close_vs_open_range` | `rank_max` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_max__early_body_momentum__bar_ret_0` | `max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__trend_bar_close_consistency__bar_ret_0` | `min` | a=`trend_bar_close_consistency`, b=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__early_body_momentum` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | `rank_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_mean__first_bar_return__max_down_ret` | `mean` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_mean__max_up_ret__first_bar_return` | `mean` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__net_volume_flow__max_down_ret` | `mean` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_median` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | `sig_product` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_sig_product__max_up_ret__early_body_momentum` | `sig_product` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_max__max_up_ret__early_body_momentum` | `max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_min__max_up_ret__trend_bar_close_consistency` | `min` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`smooth_momentum_structure` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_min__high_low_sequence_momentum__max_down_ret` | `rank_min` | a=`high_low_sequence_momentum`, b=`max_down_ret` |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | `diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_min__volatility_expansion_trend_vector__max_down_ret` | `min` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_min__close_vs_open_range__first_bar_return` | `min` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_rank_min__max_up_ret__first_bar_return` | `rank_min` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | `rank_max` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | `rank_min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_mean__first_bar_sentiment__bar_ret_0` | `mean` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | `sig_product` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_mean__max_up_ret__first_bar_sentiment` | `mean` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency`, c=`body_size_progression` |
| `combo_max__net_volume_flow__max_down_ret` | `max` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`late_bar_momentum` |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | `rank_max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_min__trend_day_regime_conviction__first_bar_sentiment` | `min` | a=`trend_day_regime_conviction`, b=`first_bar_sentiment` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_day_regime_conviction` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction` |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | `rank_max` | a=`net_volume_flow`, b=`first_bar_sentiment` |
| `combo_min__max_up_ret__close_vs_open_range` | `min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__close_vs_open_range__max_down_ret` | `max` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__first_bar_return__max_down_ret` | `min` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_max__close_vs_open_range__early_body_momentum` | `max` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rank_min__first_bar_return__max_down_ret` | `rank_min` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_sig_product__net_volume_flow__first_bar_return` | `sig_product` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | `sig_product` | a=`star50_limit_proximity_early`, b=`early_body_momentum` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_rank_min__max_up_ret__close_vs_open_range` | `rank_min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression` | `tri_mean` | a=`net_volume_flow`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | `max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `sig_product` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_max__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_max` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | `sig_product` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_mean__first_bar_sentiment__max_down_ret` | `mean` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__net_volume_flow` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`net_volume_flow` |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | `sig_product` | a=`high_low_sequence_momentum`, b=`first_bar_return` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__max_up_ret__high_low_sequence_momentum` | `sig_product` | a=`max_up_ret`, b=`high_low_sequence_momentum` |
| `combo_max__trend_bar_close_consistency__first_bar_sentiment` | `max` | a=`trend_bar_close_consistency`, b=`first_bar_sentiment` |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | `rank_min` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_tri_median__max_up_ret__smooth_momentum_structure__net_volume_flow` | `tri_median` | a=`max_up_ret`, b=`smooth_momentum_structure`, c=`net_volume_flow` |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | `sig_product` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_min__close_vs_open_range__first_bar_sentiment` | `min` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_max__high_low_sequence_momentum__max_down_ret` | `max` | a=`high_low_sequence_momentum`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | `sig_product` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`early_late_momentum_divergence` |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_day_regime_conviction` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_sig_product__net_volume_flow__max_down_ret` | `sig_product` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_min__star50_limit_proximity_early__first_bar_return` | `min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | `diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_min__limit_down_proximity_early__volume_weighted_price_position` | `min` | a=`limit_down_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | `rel_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | `rank_min` | a=`limit_down_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_buy_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | `mean` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | `mean` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | `mean` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `mean` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `rank_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | `tri_min` | a=`star50_limit_proximity_early`, b=`yesterday_early_momentum`, c=`yesterday_first_30min_return` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | `mean` | a=`bar_body_rng_0`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | `max` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_return` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_body_rng_0`, b=`demark_setup_reversal_early` |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `min` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | `min` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | `tri_max` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_mean__max_up_ret__bar_ret_0` | `mean` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | `sig_product` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `rank_max` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_max__max_up_ret__impulse_bar_dominance` | `max` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | `rank_min` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_rank_min__bar_body_rng_0__volatility_expansion_trend_vector` | `rank_min` | a=`bar_body_rng_0`, b=`volatility_expansion_trend_vector` |
| `combo_min__limit_down_proximity_early__impulse_bar_dominance` | `min` | a=`limit_down_proximity_early`, b=`impulse_bar_dominance` |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | `z_sum` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | `max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | `sig_product` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | `max` | a=`bar_ret_0`, b=`volatility_expansion_trend_vector` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | `sig_product` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__max_up_ret__volume_weighted_price_position` | `rank_min` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__star50_limit_proximity_early__first_bar_return` | `max` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | `mean` | a=`limit_down_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | `max` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | `ratio` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_diff__max_up_ret__late_bar_momentum` | `diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_mean__first_bar_return__volume_weighted_price_position` | `mean` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | `z_sum` | a=`impulse_bar_dominance`, b=`volatility_expansion_trend_vector` |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_return` |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_max__bar_body_rng_0__limit_down_proximity_early` | `max` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | `max` | a=`bar_body_rng_0`, b=`impulse_bar_dominance` |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | `mean` | a=`bar_body_rng_0`, b=`impulse_bar_dominance` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_max__first_bar_sentiment__bar_ret_0` | `max` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_min__first_bar_sentiment__bar_ret_0` | `min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | `sig_product` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_max__first_bar_return__impulse_bar_dominance` | `max` | a=`first_bar_return`, b=`impulse_bar_dominance` |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | `rank_min` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_median` | a=`star50_limit_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_z_sum__yesterday_first_30min_return__yesterday_early_trend` | `z_sum` | a=`yesterday_first_30min_return`, b=`yesterday_early_trend` |
