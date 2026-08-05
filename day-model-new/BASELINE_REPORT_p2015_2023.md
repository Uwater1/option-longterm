# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2015_2023`

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
| 300ETF | single | 1,797 | 585 | 379 | 280 | 267 | 223 | 197 | 197 | 61 | 61 | 25 | `[9, 5, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (25 clusters)]` |
| 300ETF | long | 579 | 40 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 586 | 93 | 26 | 26 | 5 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | single | 985 | 214 | 145 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | long | 361 | 46 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | short | 317 | 39 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 4,745 | 2,292 | 1,920 | 1,775 | 1,767 | 1,505 | 1,478 | 1,478 | 339 | 338 | 110 | `[18, 18, 14, 13, 12, 12, 11, 11, 11, 10, 7, 5, ... (110 clusters)]` |
| 500ETF | long | 1,360 | 108 | 62 | 62 | 29 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | short | 426 | 54 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | single | 2,974 | 935 | 467 | 364 | 360 | 207 | 207 | 207 | 78 | 78 | 35 | `[8, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (35 clusters)]` |
| 159915ETF | long | 1,121 | 108 | 48 | 48 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | short | 302 | 47 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 61 | 25 | `[9, 5, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (25 clusters)]` | +0.1275 | [+0.0859, +0.1697] | +0.2414 | [+0.1242, +0.3358] | +0.9515 | 6.67% | 1.6458 | 5.05% | 1.2634 | 2.4006 | 5.57% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 338 | 110 | `[18, 18, 14, 13, 12, 12, 11, 11, 11, 10, 7, 5, ... (110 clusters)]` | +0.1753 | [+0.1335, +0.2187] | +0.2789 | [+0.1892, +0.3676] | +0.9636 | 8.36% | 1.7355 | 6.73% | 1.4122 | 2.6215 | 3.51% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 78 | 35 | `[8, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (35 clusters)]` | +0.1702 | [+0.1259, +0.2124] | +0.2615 | [+0.1842, +0.3464] | +0.9152 | 8.73% | 1.5916 | 7.12% | 1.3111 | 2.0744 | 10.29% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 61 | 25 | `[9, 5, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (25 clusters)]` | +0.0739* | [-0.0021, +0.1477] | +0.1595* | [-0.0266, +0.3288] | +0.9152 | 3.77% | 1.0052 | 2.17% | 0.5854 | 1.1534 | 3.70% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 338 | 110 | `[18, 18, 14, 13, 12, 12, 11, 11, 11, 10, 7, 5, ... (110 clusters)]` | +0.1107 | [+0.0350, +0.1827] | +0.1058* | [-0.0321, +0.2519] | +0.7576 | 3.75% | 0.8562 | 2.26% | 0.5181 | 0.9051 | 4.89% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 78 | 35 | `[8, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (35 clusters)]` | +0.1489 | [+0.0688, +0.2155] | +0.2597 | [+0.0909, +0.4203] | +0.7576 | 10.71% | 1.5801 | 9.28% | 1.3847 | 3.8166 | 4.91% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 12 | +1 | +0.1225 | +0.2852 | +0.2860 | 0.0000 | +0.7955 | +0.7966 | 0.881 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 0 | +1 | +0.1187 | +0.2800 | +0.2807 | 0.0000 | +0.7370 | +0.7191 | 0.945 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.1188 | +0.2764 | +0.2775 | 0.0000 | +0.8678 | +0.8074 | 0.000 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 11 | +1 | +0.1156 | +0.2691 | +0.2697 | 0.0000 | +0.5471 | +0.7072 | 0.912 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 0 | +1 | +0.1193 | +0.2664 | +0.2674 | 0.0000 | +0.7162 | +0.7524 | 0.909 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 10 | +1 | +0.1119 | +0.2634 | +0.2636 | 0.0000 | +0.6357 | +0.7155 | 0.822 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1132 | +0.2593 | +0.2602 | 0.0000 | +0.6700 | +0.7042 | 0.791 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 17 | +1 | +0.1197 | +0.2426 | +0.2433 | 0.0000 | +0.5789 | +0.7129 | 0.941 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Cluster 22 | +1 | +0.0941 | +0.2409 | +0.2417 | 0.0000 | +0.5785 | +0.7062 | 0.853 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 21 | +1 | +0.0967 | +0.2335 | +0.2348 | 0.0000 | +0.5436 | +0.7016 | 0.944 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1165 | +0.2329 | +0.2342 | 0.0000 | +0.7329 | +0.7678 | 0.875 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` | Cluster 10 | +1 | +0.1109 | +0.2299 | +0.2304 | 0.0000 | +0.6560 | +0.7185 | 0.914 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Cluster 7 | +1 | +0.0927 | +0.2276 | +0.2285 | 0.0000 | +0.5897 | +0.7088 | 0.888 |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.1111 | +0.2261 | +0.2276 | 0.0000 | +0.7574 | +0.7643 | 0.948 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 23 | +1 | +0.0872 | +0.2244 | +0.2251 | 0.0000 | +0.7215 | +0.7571 | 0.770 |
| `rbreaker_sell_setup_proximity_early` | Cluster 16 | +1 | +0.0965 | +0.2243 | +0.2248 | 0.0000 | +0.5652 | +0.7360 | 0.936 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1235 | +0.2218 | +0.2227 | 0.0000 | +0.6181 | +0.7427 | 0.873 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 18 | +1 | +0.0995 | +0.2197 | +0.2208 | 0.0000 | +0.5241 | +0.6769 | 0.920 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 20 | +1 | +0.0912 | +0.2181 | +0.2193 | 0.0000 | +0.5315 | +0.6533 | 0.895 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 23 | +1 | +0.0811 | +0.2172 | +0.2175 | 0.0000 | +0.7860 | +0.7750 | 0.924 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1074 | +0.2134 | +0.2144 | 0.0000 | +0.6836 | +0.7191 | 0.935 |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Cluster 3 | +1 | +0.0980 | +0.2134 | +0.2142 | 0.0000 | +0.5718 | +0.7155 | 0.949 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 5 | +1 | +0.0859 | +0.2129 | +0.2140 | 0.0000 | +0.6572 | +0.7483 | 0.943 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 17 | +1 | +0.1222 | +0.2128 | +0.2133 | 0.0000 | +0.5504 | +0.7062 | 0.923 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 9 | +1 | +0.1091 | +0.2107 | +0.2118 | 0.0002 | +0.6800 | +0.7524 | 0.943 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 5 | +1 | +0.0898 | +0.2103 | +0.2113 | 0.0002 | +0.5473 | +0.7083 | 0.903 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 2 | +1 | +0.0935 | +0.2101 | +0.2106 | 0.0002 | +0.6761 | +0.7432 | 0.904 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 2 | +1 | +0.0890 | +0.2083 | +0.2087 | 0.0002 | +0.5712 | +0.6918 | 0.873 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 19 | +1 | +0.1131 | +0.2066 | +0.2074 | 0.0002 | +0.6498 | +0.7088 | 0.934 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 20 | +1 | +0.0893 | +0.2054 | +0.2064 | 0.0002 | +0.3937 | +0.6636 | 0.938 |
| `combo_tri_mean__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Cluster 14 | +1 | +0.0947 | +0.2018 | +0.2028 | 0.0002 | +0.4961 | +0.6831 | 0.942 |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | Cluster 4 | +1 | +0.0840 | +0.2001 | +0.2002 | 0.0002 | +0.5497 | +0.7011 | 0.679 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 14 | +1 | +0.0963 | +0.2000 | +0.2009 | 0.0002 | +0.5073 | +0.6882 | 0.919 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | Cluster 4 | +1 | +0.0745 | +0.1999 | +0.1999 | 0.0002 | +0.4465 | +0.6800 | 0.775 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 1 | +1 | +0.0914 | +0.1995 | +0.2002 | 0.0002 | +0.5245 | +0.7103 | 0.943 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 21 | +1 | +0.0908 | +0.1980 | +0.1997 | 0.0002 | +0.4755 | +0.6733 | 0.945 |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Cluster 8 | +1 | +0.0958 | +0.1980 | +0.1978 | 0.0002 | +0.5832 | +0.7160 | 0.844 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 19 | +1 | +0.1232 | +0.1957 | +0.1970 | 0.0002 | +0.6911 | +0.7360 | 0.926 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 23 | +1 | +0.0754 | +0.1940 | +0.1950 | 0.0002 | +0.7475 | +0.7807 | 0.885 |
| `combo_max__first_bar_return__bar_body_rng_0` | Cluster 14 | +1 | +0.0944 | +0.1938 | +0.1949 | 0.0002 | +0.5724 | +0.7191 | 0.939 |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__volume_concentration` | Cluster 13 | +1 | +0.0665 | +0.1925 | +0.1927 | 0.0002 | +0.5928 | +0.7401 | 0.795 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.1044 | +0.1916 | +0.1923 | 0.0002 | +0.5319 | +0.6528 | 0.949 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early` | Cluster 11 | +1 | +0.1047 | +0.1870 | +0.1876 | 0.0002 | +0.4424 | +0.6713 | 0.881 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.1169 | +0.1869 | +0.1879 | 0.0002 | +0.6009 | +0.7067 | 0.942 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Cluster 13 | +1 | +0.0660 | +0.1858 | +0.1864 | 0.0004 | +0.6574 | +0.7488 | 0.742 |
| `combo_tri_max__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | Cluster 24 | +1 | +0.0902 | +0.1839 | +0.1847 | 0.0004 | +0.5811 | +0.7026 | 0.906 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 14 | +1 | +0.0917 | +0.1836 | +0.1849 | 0.0004 | +0.5672 | +0.7304 | 0.747 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 6 | +1 | +0.0833 | +0.1830 | +0.1846 | 0.0004 | +0.6883 | +0.7576 | 0.822 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.0910 | +0.1818 | +0.1831 | 0.0004 | +0.5267 | +0.6780 | 0.880 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.1034 | +0.1805 | +0.1820 | 0.0006 | +0.5393 | +0.6775 | 0.927 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 5 | +1 | +0.0893 | +0.1747 | +0.1759 | 0.0006 | +0.4218 | +0.6651 | 0.933 |
| `combo_clamp_diff__limit_down_proximity_early__volume_concentration` | Cluster 13 | +1 | +0.0619 | +0.1738 | +0.1741 | 0.0006 | +0.4638 | +0.6965 | 0.910 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | Cluster 5 | +1 | +0.0763 | +0.1733 | +0.1746 | 0.0006 | +0.6598 | +0.6990 | 0.911 |
| `star50_limit_proximity_early` | Cluster 16 | +1 | +0.0915 | +0.1720 | +0.1727 | 0.0012 | +0.4589 | +0.6954 | 0.945 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 6 | +1 | +0.0842 | +0.1707 | +0.1716 | 0.0014 | +0.4922 | +0.6877 | 0.871 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 19 | +1 | +0.1062 | +0.1686 | +0.1706 | 0.0018 | +0.4878 | +0.6615 | 0.917 |
| `max_up_ret` | Cluster 5 | +1 | +0.0767 | +0.1676 | +0.1683 | 0.0018 | +0.3955 | +0.6549 | 0.909 |
| `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 23 | +1 | +0.0803 | +0.1660 | +0.1672 | 0.0018 | +0.6402 | +0.7191 | 0.879 |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 9 | +1 | +0.1032 | +0.1643 | +0.1656 | 0.0018 | +0.6259 | +0.7160 | 0.947 |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | Cluster 24 | +1 | +0.0848 | +0.1476 | +0.1484 | 0.0036 | +0.6663 | +0.7149 | 0.931 |
| `combo_sig_product__first_bar_return__morning_volume_weighted_momentum` | Cluster 15 | +1 | +0.0835 | +0.1279 | +0.1280 | 0.0136 | +0.4361 | +0.6662 | 0.775 |

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
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 6 | +1 | +0.1763 | +0.3308 | +0.3324 | 0.0000 | +1.1222 | +0.8567 | 0.944 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1603 | +0.3202 | +0.3220 | 0.0000 | +0.8630 | +0.7925 | 0.875 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 6 | +1 | +0.1776 | +0.3148 | +0.3165 | 0.0000 | +1.1131 | +0.8377 | 0.950 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 76 | +1 | +0.1725 | +0.3147 | +0.3164 | 0.0000 | +0.8679 | +0.7925 | 0.900 |
| `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | Cluster 97 | +1 | +0.1503 | +0.3103 | +0.3111 | 0.0000 | +0.9032 | +0.7920 | 0.845 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 6 | +1 | +0.1753 | +0.3102 | +0.3126 | 0.0000 | +0.8870 | +0.7971 | 0.000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1544 | +0.3075 | +0.3095 | 0.0000 | +0.9528 | +0.8197 | 0.859 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | Cluster 97 | +1 | +0.1240 | +0.3062 | +0.3081 | 0.0000 | +0.7219 | +0.7560 | 0.943 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 77 | +1 | +0.1701 | +0.3059 | +0.3074 | 0.0000 | +1.0974 | +0.8557 | 0.900 |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | Cluster 38 | +1 | +0.1817 | +0.2952 | +0.2964 | 0.0000 | +0.8010 | +0.7807 | 0.941 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 47 | +1 | +0.2012 | +0.2950 | +0.2963 | 0.0000 | +0.9487 | +0.7925 | 0.936 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 103 | +1 | +0.1531 | +0.2943 | +0.2960 | 0.0000 | +0.9313 | +0.8264 | 0.916 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 46 | +1 | +0.1929 | +0.2923 | +0.2933 | 0.0000 | +0.7985 | +0.7555 | 0.924 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 103 | +1 | +0.1713 | +0.2906 | +0.2921 | 0.0000 | +0.9437 | +0.8095 | 0.915 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 76 | +1 | +0.1764 | +0.2905 | +0.2914 | 0.0000 | +0.6412 | +0.7129 | 0.927 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 97 | +1 | +0.1256 | +0.2897 | +0.2901 | 0.0000 | +0.8157 | +0.8012 | 0.943 |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 77 | +1 | +0.1596 | +0.2893 | +0.2907 | 0.0000 | +0.8691 | +0.8120 | 0.944 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 76 | +1 | +0.1711 | +0.2877 | +0.2893 | 0.0000 | +0.6299 | +0.7355 | 0.811 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Cluster 50 | +1 | +0.1688 | +0.2855 | +0.2869 | 0.0000 | +0.6612 | +0.7329 | 0.950 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 5 | +1 | +0.1629 | +0.2850 | +0.2868 | 0.0000 | +0.9770 | +0.8356 | 0.933 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 57 | +1 | +0.1672 | +0.2845 | +0.2863 | 0.0000 | +1.0054 | +0.8444 | 0.892 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Cluster 97 | +1 | +0.1317 | +0.2835 | +0.2853 | 0.0000 | +0.7668 | +0.7576 | 0.945 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Cluster 76 | +1 | +0.1458 | +0.2828 | +0.2845 | 0.0000 | +0.5522 | +0.6913 | 0.932 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Cluster 0 | +1 | +0.1691 | +0.2819 | +0.2831 | 0.0000 | +0.7169 | +0.7560 | 0.899 |
| `combo_tri_mean__max_up_ret__net_volume_flow__star50_limit_proximity_early` | Cluster 100 | +1 | +0.1764 | +0.2819 | +0.2832 | 0.0000 | +0.8822 | +0.7797 | 0.941 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 5 | +1 | +0.1590 | +0.2814 | +0.2830 | 0.0000 | +0.9932 | +0.8356 | 0.901 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 97 | +1 | +0.1410 | +0.2807 | +0.2818 | 0.0000 | +0.7409 | +0.7463 | 0.940 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 76 | +1 | +0.1765 | +0.2794 | +0.2812 | 0.0000 | +0.7121 | +0.7673 | 0.879 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Cluster 77 | +1 | +0.1646 | +0.2792 | +0.2808 | 0.0000 | +0.7857 | +0.7910 | 0.925 |
| `combo_max__early_body_momentum__bar_body_rng_0` | Cluster 109 | +1 | +0.1433 | +0.2782 | +0.2798 | 0.0000 | +0.9385 | +0.8392 | 0.945 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Cluster 38 | +1 | +0.1754 | +0.2762 | +0.2774 | 0.0000 | +0.7731 | +0.7668 | 0.925 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 6 | +1 | +0.1720 | +0.2752 | +0.2762 | 0.0000 | +0.7229 | +0.7345 | 0.874 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 47 | +1 | +0.1884 | +0.2746 | +0.2765 | 0.0000 | +0.8408 | +0.7576 | 0.880 |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 77 | +1 | +0.1354 | +0.2739 | +0.2751 | 0.0000 | +0.9157 | +0.8511 | 0.950 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 5 | +1 | +0.1585 | +0.2737 | +0.2758 | 0.0000 | +0.8841 | +0.7920 | 0.868 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 44 | +1 | +0.1207 | +0.2737 | +0.2753 | 0.0000 | +0.6781 | +0.7401 | 0.832 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Cluster 76 | +1 | +0.1447 | +0.2736 | +0.2754 | 0.0000 | +0.5541 | +0.6703 | 0.945 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Cluster 77 | +1 | +0.1616 | +0.2732 | +0.2749 | 0.0000 | +1.0593 | +0.8552 | 0.949 |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | Cluster 58 | +1 | +0.1456 | +0.2730 | +0.2744 | 0.0000 | +0.8196 | +0.7643 | 0.944 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 43 | +1 | +0.1202 | +0.2722 | +0.2729 | 0.0000 | +0.7559 | +0.7776 | 0.949 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Cluster 66 | +1 | +0.1484 | +0.2722 | +0.2732 | 0.0000 | +0.7569 | +0.7494 | 0.766 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 97 | +1 | +0.1429 | +0.2720 | +0.2731 | 0.0000 | +0.8170 | +0.7797 | 0.944 |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Cluster 97 | +1 | +0.1411 | +0.2717 | +0.2727 | 0.0000 | +0.7770 | +0.7643 | 0.930 |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 97 | +1 | +0.0984 | +0.2717 | +0.2732 | 0.0000 | +0.6015 | +0.7165 | 0.947 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 55 | +1 | +0.1602 | +0.2716 | +0.2730 | 0.0000 | +0.6443 | +0.7339 | 0.904 |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | Cluster 76 | +1 | +0.1624 | +0.2705 | +0.2722 | 0.0000 | +0.7158 | +0.7571 | 0.923 |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | Cluster 65 | +1 | +0.1436 | +0.2685 | +0.2693 | 0.0000 | +0.7282 | +0.7863 | 0.947 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 77 | +1 | +0.1643 | +0.2677 | +0.2692 | 0.0000 | +0.7719 | +0.7756 | 0.932 |
| `combo_tri_min__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | Cluster 97 | +1 | +0.1211 | +0.2670 | +0.2687 | 0.0000 | +0.6638 | +0.7093 | 0.947 |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | Cluster 43 | +1 | +0.1041 | +0.2661 | +0.2673 | 0.0000 | +0.6435 | +0.7206 | 0.947 |
| `combo_min__opening_drive_thrust_ratio__rsi_opening` | Cluster 77 | +1 | +0.1351 | +0.2659 | +0.2677 | 0.0000 | +0.6530 | +0.7355 | 0.933 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | Cluster 77 | +1 | +0.1574 | +0.2658 | +0.2668 | 0.0000 | +0.9146 | +0.8136 | 0.943 |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Cluster 98 | +1 | +0.1580 | +0.2655 | +0.2665 | 0.0000 | +0.8156 | +0.7571 | 0.879 |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Cluster 88 | +1 | +0.1545 | +0.2652 | +0.2672 | 0.0000 | +0.8004 | +0.7607 | 0.938 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 46 | +1 | +0.1760 | +0.2652 | +0.2666 | 0.0000 | +0.7186 | +0.7678 | 0.928 |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | Cluster 77 | +1 | +0.1437 | +0.2649 | +0.2672 | 0.0000 | +0.7841 | +0.7771 | 0.948 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 97 | +1 | +0.1418 | +0.2647 | +0.2663 | 0.0000 | +0.6823 | +0.7185 | 0.917 |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | Cluster 77 | +1 | +0.1420 | +0.2645 | +0.2660 | 0.0000 | +0.7733 | +0.7874 | 0.909 |
| `opening_drive_thrust_ratio` | Cluster 5 | +1 | +0.1682 | +0.2632 | +0.2649 | 0.0000 | +0.7902 | +0.8084 | 0.905 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 77 | +1 | +0.1535 | +0.2626 | +0.2641 | 0.0000 | +0.8366 | +0.7961 | 0.907 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 38 | +1 | +0.1804 | +0.2620 | +0.2630 | 0.0000 | +0.9544 | +0.8038 | 0.859 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 98 | +1 | +0.1598 | +0.2613 | +0.2624 | 0.0000 | +0.6663 | +0.7108 | 0.935 |
| `combo_rank_min__max_up_ret__max_down_ret` | Cluster 5 | +1 | +0.1444 | +0.2603 | +0.2617 | 0.0000 | +0.5959 | +0.7232 | 0.874 |
| `combo_mean__early_body_momentum__star50_limit_proximity_early` | Cluster 97 | +1 | +0.1313 | +0.2601 | +0.2609 | 0.0000 | +0.7447 | +0.7632 | 0.901 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1782 | +0.2597 | +0.2611 | 0.0000 | +0.7347 | +0.7417 | 0.943 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 51 | +1 | +0.1769 | +0.2592 | +0.2601 | 0.0000 | +0.7428 | +0.7483 | 0.855 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 77 | +1 | +0.1490 | +0.2589 | +0.2608 | 0.0000 | +0.7877 | +0.7653 | 0.947 |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 0 | +1 | +0.1310 | +0.2587 | +0.2601 | 0.0000 | +0.6284 | +0.7350 | 0.929 |
| `combo_mean__net_volume_flow__bar_body_rng_0` | Cluster 30 | +1 | +0.1415 | +0.2585 | +0.2606 | 0.0000 | +0.7271 | +0.8053 | 0.927 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 62 | +1 | +0.1418 | +0.2581 | +0.2597 | 0.0000 | +0.7611 | +0.7745 | 0.937 |
| `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Cluster 63 | +1 | +0.1444 | +0.2576 | +0.2585 | 0.0000 | +0.7216 | +0.7838 | 0.896 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 72 | +1 | +0.1701 | +0.2575 | +0.2596 | 0.0000 | +0.9509 | +0.8254 | 0.875 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 38 | +1 | +0.1842 | +0.2575 | +0.2589 | 0.0000 | +0.8809 | +0.8043 | 0.901 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Cluster 0 | +1 | +0.1243 | +0.2568 | +0.2574 | 0.0000 | +0.6319 | +0.7483 | 0.905 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Cluster 38 | +1 | +0.1709 | +0.2551 | +0.2562 | 0.0000 | +0.9313 | +0.7802 | 0.933 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Cluster 66 | +1 | +0.1546 | +0.2543 | +0.2549 | 0.0000 | +0.5488 | +0.7026 | 0.761 |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 0 | +1 | +0.1361 | +0.2542 | +0.2555 | 0.0000 | +0.7127 | +0.7452 | 0.848 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 38 | +1 | +0.1580 | +0.2540 | +0.2552 | 0.0000 | +0.6084 | +0.7242 | 0.921 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Cluster 51 | +1 | +0.1793 | +0.2538 | +0.2549 | 0.0000 | +0.6876 | +0.7499 | 0.937 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 56 | +1 | +0.1799 | +0.2530 | +0.2544 | 0.0000 | +0.8288 | +0.7699 | 0.911 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 102 | +1 | +0.1683 | +0.2528 | +0.2542 | 0.0000 | +0.7759 | +0.7735 | 0.859 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | Cluster 94 | +1 | +0.1696 | +0.2528 | +0.2544 | 0.0000 | +0.6915 | +0.7499 | 0.941 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | Cluster 88 | +1 | +0.1641 | +0.2527 | +0.2547 | 0.0000 | +0.7468 | +0.7853 | 0.943 |
| `combo_rank_min__opening_drive_thrust_ratio__early_order_flow_imbalance` | Cluster 65 | +1 | +0.1297 | +0.2515 | +0.2537 | 0.0000 | +0.8004 | +0.7822 | 0.943 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 102 | +1 | +0.1687 | +0.2515 | +0.2530 | 0.0000 | +0.7622 | +0.7725 | 0.917 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 69 | +1 | +0.1848 | +0.2509 | +0.2526 | 0.0000 | +0.7580 | +0.7581 | 0.891 |
| `combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Cluster 64 | +1 | +0.1224 | +0.2504 | +0.2515 | 0.0000 | +0.7665 | +0.7853 | 0.936 |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 40 | +1 | +0.1057 | +0.2501 | +0.2506 | 0.0000 | +0.6973 | +0.7750 | 0.927 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Cluster 38 | +1 | +0.1749 | +0.2498 | +0.2510 | 0.0000 | +1.0192 | +0.7910 | 0.613 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Cluster 73 | +1 | +0.1631 | +0.2496 | +0.2512 | 0.0000 | +0.5890 | +0.7134 | 0.879 |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Cluster 35 | +1 | +0.1389 | +0.2495 | +0.2515 | 0.0000 | +0.8336 | +0.7756 | 0.936 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 38 | +1 | +0.1626 | +0.2494 | +0.2513 | 0.0000 | +0.6742 | +0.7483 | 0.936 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Cluster 50 | +1 | +0.1659 | +0.2483 | +0.2495 | 0.0000 | +0.5905 | +0.7247 | 0.934 |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | Cluster 91 | +1 | +0.1533 | +0.2482 | +0.2501 | 0.0000 | +0.7183 | +0.7684 | 0.879 |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 41 | +1 | +0.0926 | +0.2477 | +0.2488 | 0.0000 | +0.5626 | +0.7201 | 0.917 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Cluster 39 | +1 | +0.1003 | +0.2474 | +0.2481 | 0.0000 | +0.6966 | +0.7452 | 0.945 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Cluster 50 | +1 | +0.1683 | +0.2474 | +0.2488 | 0.0000 | +0.5774 | +0.7093 | 0.901 |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 68 | +1 | +0.1687 | +0.2471 | +0.2494 | 0.0000 | +0.6856 | +0.7319 | 0.935 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 108 | +1 | +0.1258 | +0.2462 | +0.2482 | 0.0000 | +0.7698 | +0.7514 | 0.872 |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | Cluster 59 | +1 | +0.1596 | +0.2461 | +0.2475 | 0.0000 | +0.6578 | +0.7273 | 0.852 |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Cluster 39 | +1 | +0.0926 | +0.2458 | +0.2464 | 0.0000 | +0.7014 | +0.7668 | 0.902 |
| `combo_max__max_up_ret__max_down_ret` | Cluster 96 | +1 | +0.1650 | +0.2458 | +0.2482 | 0.0000 | +0.7544 | +0.7411 | 0.913 |
| `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | Cluster 104 | +1 | +0.1604 | +0.2452 | +0.2470 | 0.0000 | +0.6554 | +0.7262 | 0.881 |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 0 | +1 | +0.1321 | +0.2451 | +0.2464 | 0.0000 | +0.6621 | +0.7386 | 0.941 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 108 | +1 | +0.1269 | +0.2448 | +0.2467 | 0.0000 | +0.7120 | +0.7350 | 0.837 |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | Cluster 23 | +1 | +0.1116 | +0.2448 | +0.2463 | 0.0000 | +0.4780 | +0.7011 | 0.929 |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | Cluster 80 | +1 | +0.1271 | +0.2443 | +0.2460 | 0.0000 | +0.6266 | +0.7365 | 0.796 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 48 | +1 | +0.1820 | +0.2437 | +0.2446 | 0.0000 | +0.6067 | +0.7211 | 0.947 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 38 | +1 | +0.1750 | +0.2436 | +0.2448 | 0.0000 | +0.9014 | +0.7761 | 0.950 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Cluster 19 | +1 | +0.1097 | +0.2423 | +0.2441 | 0.0000 | +0.6350 | +0.7458 | 0.924 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 66 | +1 | +0.1511 | +0.2415 | +0.2427 | 0.0000 | +0.5920 | +0.7103 | 0.920 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Cluster 0 | +1 | +0.1501 | +0.2412 | +0.2430 | 0.0000 | +0.8954 | +0.7966 | 0.895 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 69 | +1 | +0.1873 | +0.2408 | +0.2421 | 0.0000 | +0.6319 | +0.7565 | 0.924 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 5 | +1 | +0.1815 | +0.2407 | +0.2423 | 0.0000 | +0.7096 | +0.7016 | 0.917 |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | Cluster 80 | +1 | +0.1226 | +0.2406 | +0.2419 | 0.0000 | +0.6537 | +0.7262 | 0.915 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Cluster 77 | +1 | +0.1676 | +0.2403 | +0.2417 | 0.0000 | +0.8841 | +0.8136 | 0.949 |
| `combo_diff__net_volume_flow__demark_setup_reversal_early` | Cluster 101 | +1 | +0.1452 | +0.2399 | +0.2411 | 0.0000 | +0.6472 | +0.7678 | 0.915 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | Cluster 92 | +1 | +0.1501 | +0.2398 | +0.2409 | 0.0000 | +0.6127 | +0.7319 | 0.950 |
| `combo_min__net_volume_flow__bar_ret_0` | Cluster 27 | +1 | +0.1279 | +0.2395 | +0.2414 | 0.0000 | +0.7200 | +0.7643 | 0.897 |
| `combo_tri_median__trend_bar_close_consistency__star50_limit_proximity_early__bar_ret_0` | Cluster 29 | +1 | +0.1499 | +0.2394 | +0.2405 | 0.0000 | +0.7600 | +0.7565 | 0.888 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Cluster 27 | +1 | +0.1054 | +0.2390 | +0.2404 | 0.0000 | +0.6328 | +0.7155 | 0.946 |
| `combo_mean__net_volume_flow__close_vs_open_range` | Cluster 19 | +1 | +0.1170 | +0.2389 | +0.2406 | 0.0000 | +0.5893 | +0.7072 | 0.918 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 76 | +1 | +0.1535 | +0.2387 | +0.2404 | 0.0000 | +0.5158 | +0.6769 | 0.948 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 67 | +1 | +0.1744 | +0.2386 | +0.2405 | 0.0000 | +0.7458 | +0.7776 | 0.931 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 77 | +1 | +0.1351 | +0.2378 | +0.2396 | 0.0000 | +0.7319 | +0.7709 | 0.937 |
| `combo_rel_diff__net_volume_flow__demark_setup_reversal_early` | Cluster 101 | +1 | +0.1406 | +0.2378 | +0.2392 | 0.0000 | +0.6468 | +0.7714 | 0.897 |
| `combo_min__max_up_ret__close_vs_open_range` | Cluster 0 | +1 | +0.1283 | +0.2377 | +0.2385 | 0.0000 | +0.7087 | +0.7735 | 0.887 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Cluster 107 | +1 | +0.1417 | +0.2374 | +0.2383 | 0.0000 | +0.5798 | +0.7067 | 0.849 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 62 | +1 | +0.1401 | +0.2373 | +0.2394 | 0.0000 | +0.6639 | +0.7278 | 0.846 |
| `combo_mean__max_up_ret__close_vs_open_range` | Cluster 0 | +1 | +0.1503 | +0.2364 | +0.2379 | 0.0000 | +0.7792 | +0.7740 | 0.937 |
| `combo_rank_max__trend_day_regime_conviction__early_order_flow_imbalance` | Cluster 18 | +1 | +0.1001 | +0.2362 | +0.2371 | 0.0000 | +0.5103 | +0.7268 | 0.904 |
| `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Cluster 4 | +1 | +0.1395 | +0.2361 | +0.2374 | 0.0000 | +0.6791 | +0.7396 | 0.878 |
| `combo_sig_product__max_up_ret__early_order_flow_imbalance` | Cluster 66 | +1 | +0.1581 | +0.2361 | +0.2368 | 0.0000 | +0.6287 | +0.7653 | 0.866 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 62 | +1 | +0.1373 | +0.2358 | +0.2368 | 0.0000 | +0.5414 | +0.6970 | 0.926 |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | Cluster 42 | +1 | +0.1107 | +0.2356 | +0.2364 | 0.0000 | +0.6557 | +0.7319 | 0.882 |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | Cluster 77 | +1 | +0.1524 | +0.2347 | +0.2360 | 0.0000 | +0.6128 | +0.7786 | 0.751 |
| `combo_tri_max__max_up_ret__early_body_momentum__trend_day_regime_conviction` | Cluster 0 | +1 | +0.1447 | +0.2341 | +0.2359 | 0.0000 | +0.8363 | +0.7935 | 0.947 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 5 | +1 | +0.1595 | +0.2337 | +0.2357 | 0.0000 | +0.5864 | +0.7581 | 0.891 |
| `combo_rel_diff__volatility_expansion_trend_vector__demark_setup_reversal_early` | Cluster 101 | +1 | +0.1366 | +0.2334 | +0.2348 | 0.0000 | +0.5492 | +0.6831 | 0.939 |
| `combo_min__max_up_ret__rsi_opening` | Cluster 0 | +1 | +0.1291 | +0.2334 | +0.2342 | 0.0000 | +0.6834 | +0.7442 | 0.942 |
| `combo_max__max_up_ret__close_vs_open_range` | Cluster 0 | +1 | +0.1616 | +0.2333 | +0.2353 | 0.0000 | +0.7526 | +0.7391 | 0.879 |
| `combo_max__early_body_momentum__early_order_flow_imbalance` | Cluster 18 | +1 | +0.0947 | +0.2327 | +0.2335 | 0.0000 | +0.6316 | +0.7689 | 0.942 |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | Cluster 30 | +1 | +0.1438 | +0.2326 | +0.2348 | 0.0000 | +0.7242 | +0.7494 | 0.918 |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | Cluster 5 | +1 | +0.1599 | +0.2323 | +0.2339 | 0.0000 | +0.8607 | +0.8362 | 0.939 |
| `max_up_ret` | Cluster 55 | +1 | +0.1619 | +0.2317 | +0.2328 | 0.0000 | +0.6107 | +0.7370 | 0.948 |
| `combo_min__first_bar_return__bar_body_rng_0` | Cluster 75 | +1 | +0.1456 | +0.2314 | +0.2331 | 0.0000 | +0.6864 | +0.7268 | 0.785 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 71 | +1 | +0.1639 | +0.2309 | +0.2323 | 0.0000 | +0.7465 | +0.7756 | 0.861 |
| `combo_min__early_order_flow_imbalance__max_down_ret` | Cluster 78 | +1 | +0.1169 | +0.2305 | +0.2328 | 0.0000 | +0.6790 | +0.7401 | 0.905 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 69 | +1 | +0.1764 | +0.2301 | +0.2316 | 0.0000 | +0.7031 | +0.7761 | 0.946 |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | Cluster 66 | +1 | +0.1351 | +0.2300 | +0.2302 | 0.0000 | +0.6199 | +0.7149 | 0.863 |
| `combo_rel_diff__net_volume_flow__h2_l2_pullback_continuation` | Cluster 13 | +1 | +0.1054 | +0.2300 | +0.2314 | 0.0000 | +0.4312 | +0.6790 | 0.946 |
| `combo_min__max_up_ret__max_down_ret` | Cluster 5 | +1 | +0.1552 | +0.2299 | +0.2309 | 0.0000 | +0.5796 | +0.6888 | 0.700 |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | Cluster 42 | +1 | +0.1145 | +0.2296 | +0.2305 | 0.0000 | +0.7096 | +0.7345 | 0.930 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Cluster 75 | +1 | +0.1606 | +0.2295 | +0.2317 | 0.0000 | +0.6319 | +0.7103 | 0.895 |
| `combo_rel_diff__max_up_ret__shaved_bar_trend_conviction` | Cluster 25 | +1 | +0.0871 | +0.2292 | +0.2294 | 0.0000 | +0.6995 | +0.7601 | 0.882 |
| `combo_mean__max_up_ret__bar_ret_0` | Cluster 67 | +1 | +0.1709 | +0.2289 | +0.2302 | 0.0000 | +0.6458 | +0.7206 | 0.949 |
| `combo_min__max_up_ret__early_order_flow_imbalance` | Cluster 59 | +1 | +0.1372 | +0.2288 | +0.2301 | 0.0000 | +0.6431 | +0.7160 | 0.912 |
| `combo_rank_max__max_up_ret__max_down_ret` | Cluster 96 | +1 | +0.1673 | +0.2287 | +0.2312 | 0.0000 | +0.8076 | +0.7869 | 0.907 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | Cluster 23 | +1 | +0.1117 | +0.2287 | +0.2301 | 0.0000 | +0.5667 | +0.7334 | 0.943 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Cluster 0 | +1 | +0.1611 | +0.2286 | +0.2307 | 0.0000 | +0.8236 | +0.7781 | 0.947 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 71 | +1 | +0.1639 | +0.2285 | +0.2300 | 0.0000 | +0.7050 | +0.7678 | 0.942 |
| `combo_tri_median__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | Cluster 20 | +1 | +0.1115 | +0.2283 | +0.2297 | 0.0000 | +0.5166 | +0.7221 | 0.948 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 74 | +1 | +0.1685 | +0.2279 | +0.2297 | 0.0000 | +0.4652 | +0.6749 | 0.929 |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | Cluster 58 | +1 | +0.1439 | +0.2277 | +0.2290 | 0.0000 | +0.8184 | +0.7889 | 0.908 |
| `combo_min__first_bar_return__close_vs_open_range` | Cluster 36 | +1 | +0.1185 | +0.2276 | +0.2295 | 0.0000 | +0.7442 | +0.7524 | 0.910 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 61 | +1 | +0.1441 | +0.2275 | +0.2284 | 0.0000 | +0.5344 | +0.6913 | 0.921 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 45 | +1 | +0.1183 | +0.2274 | +0.2283 | 0.0000 | +0.5771 | +0.6888 | 0.912 |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | Cluster 66 | +1 | +0.1543 | +0.2270 | +0.2282 | 0.0000 | +0.6197 | +0.6810 | 0.826 |
| `combo_max__max_up_ret__early_order_flow_imbalance` | Cluster 58 | +1 | +0.1366 | +0.2264 | +0.2277 | 0.0000 | +0.7601 | +0.7807 | 0.922 |
| `combo_rank_min__bar_ret_0__bar_body_rng_0` | Cluster 75 | +1 | +0.1420 | +0.2251 | +0.2268 | 0.0000 | +0.5095 | +0.6559 | 0.922 |
| `combo_rel_diff__early_order_flow_imbalance__demark_setup_reversal_early` | Cluster 101 | +1 | +0.1335 | +0.2249 | +0.2258 | 0.0000 | +0.5582 | +0.7196 | 0.901 |
| `combo_mean__star50_limit_proximity_early__vwap_close_divergence_trend` | Cluster 99 | +1 | +0.1439 | +0.2248 | +0.2253 | 0.0000 | +0.6959 | +0.7350 | 0.893 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 48 | +1 | +0.1760 | +0.2247 | +0.2256 | 0.0000 | +0.5212 | +0.7021 | 0.866 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 42 | +1 | +0.1304 | +0.2246 | +0.2252 | 0.0000 | +0.7691 | +0.7422 | 0.946 |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | Cluster 77 | +1 | +0.1379 | +0.2244 | +0.2257 | 0.0000 | +0.6812 | +0.7483 | 0.900 |
| `combo_sig_product__bar_ret_0__early_order_flow_imbalance` | Cluster 2 | +1 | +0.1256 | +0.2241 | +0.2253 | 0.0000 | +0.5151 | +0.7622 | 0.783 |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | Cluster 77 | +1 | +0.1403 | +0.2241 | +0.2256 | 0.0000 | +0.6716 | +0.7350 | 0.918 |
| `combo_rank_min__first_bar_return__close_vs_open_range` | Cluster 36 | +1 | +0.1185 | +0.2241 | +0.2260 | 0.0000 | +0.7916 | +0.7684 | 0.854 |
| `combo_mean__trend_day_regime_conviction__bar_ret_0` | Cluster 95 | +1 | +0.1408 | +0.2236 | +0.2251 | 0.0000 | +0.5210 | +0.6697 | 0.950 |
| `combo_sig_product__early_body_momentum__close_vs_open_range` | Cluster 24 | +1 | +0.1013 | +0.2234 | +0.2253 | 0.0000 | +0.5679 | +0.7180 | 0.920 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 66 | +1 | +0.1489 | +0.2233 | +0.2239 | 0.0000 | +0.7037 | +0.7437 | 0.753 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 53 | +1 | +0.1708 | +0.2230 | +0.2240 | 0.0000 | +0.6195 | +0.7134 | 0.923 |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | Cluster 109 | +1 | +0.1213 | +0.2229 | +0.2243 | 0.0000 | +0.7048 | +0.7565 | 0.922 |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | Cluster 28 | +1 | +0.1344 | +0.2227 | +0.2246 | 0.0000 | +0.5331 | +0.7011 | 0.918 |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | Cluster 0 | +1 | +0.1333 | +0.2226 | +0.2236 | 0.0000 | +0.6478 | +0.7401 | 0.950 |
| `combo_mean__bar_ret_0__max_down_ret` | Cluster 75 | +1 | +0.1425 | +0.2220 | +0.2243 | 0.0000 | +0.5490 | +0.6518 | 0.852 |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | Cluster 0 | +1 | +0.1425 | +0.2213 | +0.2224 | 0.0000 | +0.6418 | +0.7612 | 0.919 |
| `combo_rank_min__close_vs_open_range__vwap_close_divergence_trend` | Cluster 15 | +1 | +0.1086 | +0.2211 | +0.2220 | 0.0000 | +0.6927 | +0.7355 | 0.874 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 5 | +1 | +0.1590 | +0.2210 | +0.2237 | 0.0000 | +0.6806 | +0.7427 | 0.949 |
| `combo_mean__max_up_ret__max_down_ret` | Cluster 96 | +1 | +0.1624 | +0.2210 | +0.2224 | 0.0000 | +0.6861 | +0.7375 | 0.871 |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Cluster 64 | +1 | +0.1547 | +0.2209 | +0.2221 | 0.0000 | +0.5992 | +0.7206 | 0.896 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 62 | +1 | +0.1422 | +0.2208 | +0.2227 | 0.0000 | +0.5242 | +0.7124 | 0.876 |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | Cluster 93 | +1 | +0.1378 | +0.2205 | +0.2215 | 0.0000 | +0.7024 | +0.7452 | 0.947 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Cluster 90 | +1 | +0.1787 | +0.2205 | +0.2218 | 0.0000 | +0.5976 | +0.7391 | 0.925 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 108 | +1 | +0.1305 | +0.2203 | +0.2218 | 0.0000 | +0.5629 | +0.6795 | 0.933 |
| `combo_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | Cluster 14 | +1 | +0.0902 | +0.2198 | +0.2210 | 0.0000 | +0.4374 | +0.6636 | 0.934 |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | Cluster 28 | +1 | +0.1311 | +0.2195 | +0.2207 | 0.0000 | +0.5855 | +0.7078 | 0.806 |
| `combo_rel_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | Cluster 14 | +1 | +0.0862 | +0.2190 | +0.2200 | 0.0000 | +0.4512 | +0.6656 | 0.904 |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | Cluster 61 | +1 | +0.1503 | +0.2186 | +0.2199 | 0.0000 | +0.5573 | +0.7031 | 0.909 |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | Cluster 0 | +1 | +0.1504 | +0.2182 | +0.2195 | 0.0000 | +0.7500 | +0.7699 | 0.905 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 52 | +1 | +0.1616 | +0.2179 | +0.2189 | 0.0000 | +0.5959 | +0.6918 | 0.894 |
| `combo_z_sum__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 89 | +1 | +0.1428 | +0.2177 | +0.2195 | 0.0000 | +0.5245 | +0.6795 | 0.920 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 38 | +1 | +0.1542 | +0.2176 | +0.2187 | 0.0000 | +0.5720 | +0.7175 | 0.939 |
| `combo_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Cluster 63 | +1 | +0.1086 | +0.2174 | +0.2189 | 0.0000 | +0.6424 | +0.7452 | 0.903 |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | Cluster 7 | +1 | +0.0998 | +0.2173 | +0.2192 | 0.0000 | +0.6144 | +0.7458 | 0.880 |
| `combo_mean__net_volume_flow__shaved_bar_trend_conviction` | Cluster 12 | +1 | +0.0965 | +0.2152 | +0.2165 | 0.0000 | +0.5668 | +0.7026 | 0.935 |
| `combo_max__first_bar_return__close_vs_open_range` | Cluster 91 | +1 | +0.1634 | +0.2151 | +0.2165 | 0.0000 | +0.7342 | +0.7766 | 0.781 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 61 | +1 | +0.1328 | +0.2150 | +0.2161 | 0.0000 | +0.4780 | +0.6687 | 0.926 |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | Cluster 15 | +1 | +0.1082 | +0.2148 | +0.2157 | 0.0000 | +0.6170 | +0.7119 | 0.888 |
| `combo_rank_max__net_volume_flow__bar_ret_0` | Cluster 70 | +1 | +0.1510 | +0.2139 | +0.2155 | 0.0000 | +0.6885 | +0.7504 | 0.944 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 49 | +1 | +0.1801 | +0.2138 | +0.2151 | 0.0000 | +0.5739 | +0.7175 | 0.882 |
| `combo_mean__first_bar_return__close_vs_open_range` | Cluster 95 | +1 | +0.1498 | +0.2132 | +0.2150 | 0.0000 | +0.7345 | +0.7766 | 0.923 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 49 | +1 | +0.1783 | +0.2131 | +0.2139 | 0.0000 | +0.5710 | +0.7006 | 0.883 |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | Cluster 76 | +1 | +0.1496 | +0.2123 | +0.2141 | 0.0000 | +0.4691 | +0.6846 | 0.877 |
| `combo_mean__net_volume_flow__max_down_ret` | Cluster 26 | +1 | +0.1285 | +0.2123 | +0.2142 | 0.0000 | +0.6531 | +0.7360 | 0.891 |
| `combo_sig_product__opening_drive_thrust_ratio__early_order_flow_imbalance` | Cluster 4 | +1 | +0.1231 | +0.2116 | +0.2122 | 0.0000 | +0.4259 | +0.6821 | 0.882 |
| `combo_rel_diff__trend_bar_close_consistency__demark_setup_reversal_early` | Cluster 101 | +1 | +0.1197 | +0.2112 | +0.2119 | 0.0000 | +0.4448 | +0.6600 | 0.937 |
| `early_body_momentum` | Cluster 24 | +1 | +0.0917 | +0.2110 | +0.2122 | 0.0000 | +0.4426 | +0.6862 | 0.948 |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Cluster 70 | +1 | +0.1404 | +0.2109 | +0.2119 | 0.0000 | +0.5747 | +0.6882 | 0.879 |
| `combo_abs_diff__max_up_ret__shaved_bar_trend_conviction` | Cluster 25 | +1 | +0.0754 | +0.2104 | +0.2108 | 0.0000 | +0.5671 | +0.7078 | 0.631 |
| `combo_sig_product__max_down_ret__close_vs_open_range` | Cluster 3 | +1 | +0.0945 | +0.2103 | +0.2120 | 0.0000 | +0.5773 | +0.7262 | 0.866 |
| `combo_rank_min__trend_bar_close_consistency__max_down_ret` | Cluster 79 | +1 | +0.1068 | +0.2101 | +0.2123 | 0.0000 | +0.5233 | +0.6898 | 0.947 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 5 | +1 | +0.1611 | +0.2099 | +0.2116 | 0.0000 | +0.6553 | +0.7678 | 0.923 |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Cluster 45 | +1 | +0.1057 | +0.2093 | +0.2107 | 0.0000 | +0.5429 | +0.6569 | 0.940 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 5 | +1 | +0.1453 | +0.2093 | +0.2107 | 0.0000 | +0.6419 | +0.7720 | 0.889 |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | Cluster 78 | +1 | +0.1199 | +0.2092 | +0.2116 | 0.0000 | +0.6814 | +0.7714 | 0.869 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 48 | +1 | +0.1705 | +0.2091 | +0.2099 | 0.0000 | +0.4839 | +0.7129 | 0.928 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 61 | +1 | +0.1648 | +0.2091 | +0.2098 | 0.0000 | +0.4521 | +0.6841 | 0.945 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | Cluster 60 | +1 | +0.1537 | +0.2083 | +0.2092 | 0.0000 | +0.6046 | +0.6949 | 0.924 |
| `combo_rank_min__max_down_ret__close_vs_open_range` | Cluster 85 | +1 | +0.1278 | +0.2083 | +0.2107 | 0.0000 | +0.5384 | +0.7031 | 0.935 |
| `combo_max__first_bar_return__max_down_ret` | Cluster 75 | +1 | +0.1553 | +0.2082 | +0.2102 | 0.0000 | +0.6162 | +0.7093 | 0.891 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Cluster 75 | +1 | +0.1276 | +0.2082 | +0.2105 | 0.0000 | +0.5260 | +0.6882 | 0.873 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 106 | +1 | +0.1405 | +0.2082 | +0.2096 | 0.0000 | +0.5216 | +0.6821 | 0.872 |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Cluster 60 | +1 | +0.1522 | +0.2080 | +0.2090 | 0.0000 | +0.6121 | +0.6800 | 0.946 |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | Cluster 109 | +1 | +0.1280 | +0.2076 | +0.2090 | 0.0000 | +0.6099 | +0.6913 | 0.924 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1248 | +0.2068 | +0.2080 | 0.0000 | +0.6500 | +0.7165 | 0.919 |
| `combo_sig_product__volatility_expansion_trend_vector__early_order_flow_imbalance` | Cluster 16 | +1 | +0.1116 | +0.2065 | +0.2079 | 0.0000 | +0.5513 | +0.7155 | 0.987 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 66 | +1 | +0.1609 | +0.2059 | +0.2067 | 0.0000 | +0.6144 | +0.7232 | 0.806 |
| `combo_max__early_body_momentum__close_vs_open_range` | Cluster 10 | +1 | +0.1020 | +0.2053 | +0.2064 | 0.0000 | +0.5463 | +0.7232 | 0.945 |
| `combo_min__close_vs_open_range__bar_body_rng_0` | Cluster 32 | +1 | +0.1224 | +0.2051 | +0.2075 | 0.0000 | +0.5537 | +0.7149 | 0.906 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 76 | +1 | +0.1578 | +0.2048 | +0.2053 | 0.0000 | +0.6479 | +0.7170 | 0.846 |
| `combo_max__bar_body_rng_0__shaved_bar_trend_conviction` | Cluster 109 | +1 | +0.1368 | +0.2047 | +0.2060 | 0.0000 | +0.6861 | +0.7725 | 0.948 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 73 | +1 | +0.1641 | +0.2045 | +0.2055 | 0.0000 | +0.4603 | +0.6703 | 0.924 |
| `combo_min__max_down_ret__close_vs_open_range` | Cluster 85 | +1 | +0.1254 | +0.2037 | +0.2059 | 0.0000 | +0.5772 | +0.7052 | 0.942 |
| `combo_rank_max__early_body_momentum__max_down_ret` | Cluster 82 | +1 | +0.1203 | +0.2028 | +0.2041 | 0.0000 | +0.5737 | +0.7165 | 0.891 |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Cluster 54 | +1 | +0.1503 | +0.2028 | +0.2036 | 0.0000 | +0.6185 | +0.7401 | 0.885 |
| `combo_sig_product__early_order_flow_imbalance__close_vs_open_range` | Cluster 1 | +1 | +0.0937 | +0.2027 | +0.2033 | 0.0000 | +0.5923 | +0.7298 | 0.729 |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | Cluster 8 | +1 | +0.1090 | +0.2026 | +0.2039 | 0.0000 | +0.5526 | +0.7072 | 0.909 |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 31 | +1 | +0.1257 | +0.2021 | +0.2038 | 0.0000 | +0.5020 | +0.6574 | 0.914 |
| `combo_min__first_bar_return__max_down_ret` | Cluster 75 | +1 | +0.1327 | +0.2016 | +0.2038 | 0.0000 | +0.5563 | +0.6975 | 0.934 |
| `combo_rank_min__early_order_flow_imbalance__close_vs_open_range` | Cluster 7 | +1 | +0.0971 | +0.2009 | +0.2029 | 0.0000 | +0.4899 | +0.6841 | 0.931 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | Cluster 61 | +1 | +0.1432 | +0.2007 | +0.2015 | 0.0000 | +0.5244 | +0.6821 | 0.876 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Cluster 105 | +1 | +0.1369 | +0.2006 | +0.2008 | 0.0000 | +0.3657 | +0.6697 | 0.641 |
| `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Cluster 107 | +1 | +0.1428 | +0.2005 | +0.2014 | 0.0000 | +0.6050 | +0.6995 | 0.923 |
| `combo_rank_max__early_body_momentum__close_vs_open_range` | Cluster 10 | +1 | +0.1067 | +0.2002 | +0.2012 | 0.0000 | +0.5342 | +0.7278 | 0.945 |
| `combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction` | Cluster 25 | +1 | +0.0743 | +0.1999 | +0.1997 | 0.0000 | +0.6403 | +0.7627 | 0.464 |
| `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Cluster 107 | +1 | +0.1416 | +0.1994 | +0.2002 | 0.0000 | +0.6114 | +0.7088 | 0.944 |
| `combo_mean__close_vs_open_range__shaved_bar_trend_conviction` | Cluster 17 | +1 | +0.0872 | +0.1988 | +0.1999 | 0.0000 | +0.4369 | +0.6600 | 0.937 |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | Cluster 33 | +1 | +0.1162 | +0.1987 | +0.2001 | 0.0000 | +0.6154 | +0.7221 | 0.911 |
| `combo_min__close_vs_open_range__shaved_bar_trend_conviction` | Cluster 17 | +1 | +0.0832 | +0.1971 | +0.1983 | 0.0000 | +0.4861 | +0.6826 | 0.941 |
| `combo_rank_min__close_vs_open_range__shaved_bar_trend_conviction` | Cluster 17 | +1 | +0.0872 | +0.1968 | +0.1980 | 0.0000 | +0.4587 | +0.7114 | 0.930 |
| `combo_min__trend_bar_close_consistency__max_down_ret` | Cluster 79 | +1 | +0.0976 | +0.1967 | +0.1983 | 0.0000 | +0.5251 | +0.6826 | 0.942 |
| `combo_rank_max__trend_day_regime_conviction__shaved_bar_trend_conviction` | Cluster 12 | +1 | +0.0926 | +0.1965 | +0.1976 | 0.0000 | +0.4219 | +0.6923 | 0.917 |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | Cluster 28 | +1 | +0.1321 | +0.1964 | +0.1979 | 0.0000 | +0.5962 | +0.6949 | 0.934 |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | Cluster 109 | +1 | +0.1219 | +0.1961 | +0.1980 | 0.0000 | +0.6716 | +0.7601 | 0.899 |
| `combo_max__bar_ret_0__vwap_close_divergence_trend` | Cluster 54 | +1 | +0.1502 | +0.1959 | +0.1967 | 0.0000 | +0.5393 | +0.6934 | 0.898 |
| `combo_min__max_up_ret__shaved_bar_trend_conviction` | Cluster 0 | +1 | +0.0913 | +0.1957 | +0.1964 | 0.0000 | +0.5771 | +0.7067 | 0.879 |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 48 | +1 | +0.1649 | +0.1956 | +0.1963 | 0.0000 | +0.4333 | +0.6826 | 0.946 |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | Cluster 0 | +1 | +0.1161 | +0.1946 | +0.1954 | 0.0000 | +0.5540 | +0.7083 | 0.944 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 62 | +1 | +0.1530 | +0.1937 | +0.1948 | 0.0000 | +0.4332 | +0.6703 | 0.845 |
| `combo_rank_max__trend_bar_close_consistency__star50_limit_proximity_early` | Cluster 61 | +1 | +0.1280 | +0.1931 | +0.1932 | 0.0000 | +0.5135 | +0.6821 | 0.947 |
| `first_bar_return` | Cluster 75 | +1 | +0.1457 | +0.1931 | +0.1945 | 0.0000 | +0.6014 | +0.7180 | 0.948 |
| `combo_max__net_volume_flow__first_bar_return` | Cluster 91 | +1 | +0.1489 | +0.1927 | +0.1942 | 0.0000 | +0.5515 | +0.7114 | 0.921 |
| `combo_max__close_vs_open_range__bar_body_rng_0` | Cluster 109 | +1 | +0.1514 | +0.1927 | +0.1947 | 0.0000 | +0.7571 | +0.7637 | 0.903 |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | Cluster 9 | +1 | +0.0752 | +0.1927 | +0.1930 | 0.0000 | +0.6017 | +0.7304 | 0.942 |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | Cluster 77 | +1 | +0.1222 | +0.1924 | +0.1934 | 0.0000 | +0.5330 | +0.7144 | 0.934 |
| `combo_mean__early_order_flow_imbalance__max_down_ret` | Cluster 78 | +1 | +0.1086 | +0.1923 | +0.1939 | 0.0000 | +0.6018 | +0.7175 | 0.947 |
| `combo_max__star50_limit_proximity_early__first_bar_return` | Cluster 76 | +1 | +0.1562 | +0.1916 | +0.1924 | 0.0000 | +0.6772 | +0.7144 | 0.919 |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Cluster 13 | +1 | +0.1011 | +0.1909 | +0.1923 | 0.0000 | +0.4255 | +0.6733 | 0.931 |
| `combo_mean__max_down_ret__close_vs_open_range` | Cluster 84 | +1 | +0.1278 | +0.1908 | +0.1925 | 0.0000 | +0.4766 | +0.6646 | 0.913 |
| `combo_sig_product__max_up_ret__body_size_progression` | Cluster 66 | +1 | +0.1454 | +0.1907 | +0.1915 | 0.0000 | +0.7799 | +0.7447 | 0.837 |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Cluster 13 | +1 | +0.1032 | +0.1905 | +0.1919 | 0.0000 | +0.4436 | +0.6862 | 0.866 |
| `combo_sig_product__max_up_ret__h2_l2_pullback_continuation` | Cluster 66 | +1 | +0.1588 | +0.1905 | +0.1919 | 0.0000 | +0.4848 | +0.6929 | 0.853 |
| `combo_max__net_volume_flow__max_down_ret` | Cluster 26 | +1 | +0.1223 | +0.1903 | +0.1919 | 0.0000 | +0.5420 | +0.7031 | 0.913 |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | Cluster 61 | +1 | +0.1398 | +0.1898 | +0.1908 | 0.0000 | +0.4713 | +0.6954 | 0.939 |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | Cluster 92 | +1 | +0.1518 | +0.1889 | +0.1908 | 0.0000 | +0.4800 | +0.7016 | 0.930 |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | Cluster 9 | +1 | +0.0778 | +0.1889 | +0.1893 | 0.0000 | +0.5937 | +0.7144 | 0.938 |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | Cluster 2 | +1 | +0.1381 | +0.1873 | +0.1882 | 0.0000 | +0.6091 | +0.7237 | 0.691 |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | Cluster 109 | +1 | +0.1277 | +0.1869 | +0.1883 | 0.0000 | +0.4792 | +0.6882 | 0.921 |
| `combo_max__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 61 | +1 | +0.1469 | +0.1867 | +0.1876 | 0.0000 | +0.4895 | +0.6615 | 0.948 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | Cluster 38 | +1 | +0.1484 | +0.1857 | +0.1873 | 0.0000 | +0.6888 | +0.7540 | 0.920 |
| `combo_rank_max__max_down_ret__close_vs_open_range` | Cluster 81 | +1 | +0.1247 | +0.1851 | +0.1867 | 0.0000 | +0.5096 | +0.6995 | 0.947 |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Cluster 34 | +1 | +0.1253 | +0.1845 | +0.1861 | 0.0000 | +0.6167 | +0.7298 | 0.942 |
| `combo_max__bar_ret_0__early_order_flow_imbalance` | Cluster 109 | +1 | +0.1216 | +0.1830 | +0.1842 | 0.0000 | +0.4815 | +0.6852 | 0.926 |
| `combo_diff__first_bar_return__early_late_momentum_divergence` | Cluster 104 | +1 | +0.1589 | +0.1828 | +0.1845 | 0.0000 | +0.4467 | +0.6754 | 0.950 |
| `combo_sig_product__bar_ret_0__close_vs_open_range` | Cluster 2 | +1 | +0.1244 | +0.1826 | +0.1841 | 0.0000 | +0.6300 | +0.7103 | 0.668 |
| `combo_tri_max__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | Cluster 52 | +1 | +0.1566 | +0.1823 | +0.1833 | 0.0000 | +0.5544 | +0.7062 | 0.937 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 61 | +1 | +0.1447 | +0.1819 | +0.1824 | 0.0000 | +0.4613 | +0.6528 | 0.923 |
| `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0` | Cluster 109 | +1 | +0.1399 | +0.1806 | +0.1816 | 0.0000 | +0.5121 | +0.6687 | 0.905 |
| `combo_min__max_down_ret__bar_body_rng_0` | Cluster 75 | +1 | +0.1357 | +0.1802 | +0.1827 | 0.0000 | +0.5409 | +0.6780 | 0.944 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | Cluster 61 | +1 | +0.1532 | +0.1800 | +0.1809 | 0.0000 | +0.4993 | +0.6949 | 0.942 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 61 | +1 | +0.1407 | +0.1798 | +0.1805 | 0.0000 | +0.5327 | +0.7155 | 0.945 |
| `combo_max__max_down_ret__close_vs_open_range` | Cluster 81 | +1 | +0.1253 | +0.1777 | +0.1790 | 0.0000 | +0.4249 | +0.6857 | 0.896 |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | Cluster 83 | +1 | +0.1083 | +0.1769 | +0.1781 | 0.0000 | +0.4620 | +0.6507 | 0.936 |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 61 | +1 | +0.1434 | +0.1767 | +0.1771 | 0.0000 | +0.4436 | +0.6682 | 0.858 |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | Cluster 13 | +1 | +0.0956 | +0.1765 | +0.1777 | 0.0000 | +0.3853 | +0.6543 | 0.942 |
| `combo_rel_diff__bar_ret_0__late_bar_momentum` | Cluster 104 | +1 | +0.1489 | +0.1758 | +0.1776 | 0.0000 | +0.4466 | +0.6646 | 0.920 |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | Cluster 31 | +1 | +0.1131 | +0.1756 | +0.1770 | 0.0000 | +0.4213 | +0.6502 | 0.904 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 38 | +1 | +0.1361 | +0.1753 | +0.1762 | 0.0000 | +0.6395 | +0.7422 | 0.872 |
| `max_down_ret` | Cluster 87 | +1 | +0.1248 | +0.1750 | +0.1774 | 0.0000 | +0.5100 | +0.6590 | 0.942 |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 61 | +1 | +0.1217 | +0.1742 | +0.1745 | 0.0000 | +0.4469 | +0.6903 | 0.921 |
| `combo_rank_max__max_down_ret__h2_l2_pullback_continuation` | Cluster 25 | +1 | +0.0884 | +0.1739 | +0.1740 | 0.0000 | +0.6419 | +0.7422 | 0.416 |
| `combo_mean__max_down_ret__shaved_bar_trend_conviction` | Cluster 86 | +1 | +0.0980 | +0.1728 | +0.1738 | 0.0000 | +0.4224 | +0.6677 | 0.942 |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | Cluster 109 | +1 | +0.1440 | +0.1705 | +0.1713 | 0.0000 | +0.6384 | +0.7016 | 0.896 |
| `combo_min__max_down_ret__shaved_bar_trend_conviction` | Cluster 86 | +1 | +0.0882 | +0.1696 | +0.1711 | 0.0002 | +0.4737 | +0.6821 | 0.936 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 66 | +1 | +0.1603 | +0.1690 | +0.1706 | 0.0002 | +0.5264 | +0.7201 | 0.798 |
| `combo_sig_product__max_up_ret__max_down_ret` | Cluster 66 | +1 | +0.1565 | +0.1686 | +0.1689 | 0.0002 | +0.5195 | +0.7001 | 0.688 |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | Cluster 83 | +1 | +0.1070 | +0.1663 | +0.1677 | 0.0004 | +0.5343 | +0.6954 | 0.873 |
| `combo_sig_product__net_volume_flow__shaved_bar_trend_conviction` | Cluster 11 | +1 | +0.0930 | +0.1657 | +0.1666 | 0.0006 | +0.3758 | +0.6538 | 0.912 |
| `combo_mean__bar_body_rng_0__shaved_bar_trend_conviction` | Cluster 37 | +1 | +0.1239 | +0.1651 | +0.1669 | 0.0006 | +0.4410 | +0.6959 | 0.933 |
| `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` | Cluster 8 | +1 | +0.0856 | +0.1650 | +0.1656 | 0.0006 | +0.4544 | +0.6728 | 0.943 |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | Cluster 15 | +1 | +0.1029 | +0.1649 | +0.1659 | 0.0006 | +0.5461 | +0.7036 | 0.929 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Cluster 106 | +1 | +0.1208 | +0.1645 | +0.1654 | 0.0006 | +0.4439 | +0.6754 | 0.832 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 38 | +1 | +0.1556 | +0.1636 | +0.1651 | 0.0006 | +0.6321 | +0.7381 | 0.946 |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | Cluster 83 | +1 | +0.1082 | +0.1625 | +0.1638 | 0.0006 | +0.5200 | +0.6718 | 0.916 |
| `combo_rank_max__max_down_ret__vwap_close_divergence_trend` | Cluster 64 | +1 | +0.1163 | +0.1580 | +0.1594 | 0.0014 | +0.5530 | +0.6970 | 0.929 |
| `morning_volume_weighted_momentum` | Cluster 21 | +1 | +0.1104 | +0.1578 | +0.1586 | 0.0014 | +0.4396 | +0.6579 | 0.909 |
| `combo_max__first_bar_return__bar_body_rng_0` | Cluster 75 | +1 | +0.1409 | +0.1566 | +0.1587 | 0.0016 | +0.4919 | +0.6795 | 0.923 |
| `open_to_current_return` | Cluster 21 | +1 | +0.1142 | +0.1557 | +0.1567 | 0.0018 | +0.4824 | +0.6954 | 0.911 |
| `vwap_trend_channel_slope` | Cluster 64 | +1 | +0.0991 | +0.1543 | +0.1549 | 0.0020 | +0.4231 | +0.6564 | 0.898 |
| `combo_max__first_bar_return__shaved_bar_trend_conviction` | Cluster 109 | +1 | +0.1396 | +0.1539 | +0.1549 | 0.0022 | +0.4790 | +0.6584 | 0.905 |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | Cluster 61 | +1 | +0.1212 | +0.1522 | +0.1526 | 0.0024 | +0.4006 | +0.6636 | 0.905 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | Cluster 3 | +1 | +0.1142 | +0.1458 | +0.1476 | 0.0042 | +0.5680 | +0.6826 | 0.758 |
| `combo_sig_product__rsi_opening__h2_l2_pullback_continuation` | Cluster 22 | +1 | +0.1008 | +0.1441 | +0.1457 | 0.0048 | +0.3627 | +0.6507 | 0.929 |
| `combo_ratio__bar_ret_0__net_volume_flow` | Cluster 104 | +1 | +0.1119 | +0.1425 | +0.1442 | 0.0062 | +0.3291 | +0.6523 | 0.101 |
| `combo_diff__net_volume_flow__shaved_bar_trend_conviction` | Cluster 25 | +1 | +0.0722 | +0.1356 | +0.1368 | 0.0088 | +0.4219 | +0.6713 | 0.583 |
| `combo_sig_product__max_down_ret__h2_l2_pullback_continuation` | Cluster 3 | +1 | +0.1002 | +0.1293 | +0.1302 | 0.0120 | +0.3509 | +0.6502 | 0.799 |
| `combo_sig_product__early_order_flow_imbalance__bar_body_rng_0` | Cluster 1 | +1 | +0.0859 | +0.1256 | +0.1265 | 0.0136 | +0.4824 | +0.6954 | 0.742 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 14 | +1 | +0.1376 | +0.3068 | +0.3083 | 0.0000 | +0.6713 | +0.7483 | 0.704 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 25 | +1 | +0.1461 | +0.3059 | +0.3073 | 0.0000 | +0.6470 | +0.7437 | 0.929 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 25 | +1 | +0.1403 | +0.2813 | +0.2825 | 0.0000 | +0.6613 | +0.7468 | 0.943 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | Cluster 8 | +1 | +0.0957 | +0.2808 | +0.2817 | 0.0000 | +0.5615 | +0.7196 | 0.939 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 6 | +1 | +0.1470 | +0.2774 | +0.2787 | 0.0000 | +0.6014 | +0.6939 | 0.945 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 14 | +1 | +0.1458 | +0.2773 | +0.2784 | 0.0000 | +0.7403 | +0.7833 | 0.934 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 14 | +1 | +0.1485 | +0.2753 | +0.2770 | 0.0000 | +0.9020 | +0.7966 | 0.918 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 3 | +1 | +0.1647 | +0.2710 | +0.2713 | 0.0000 | +0.6711 | +0.7370 | 0.914 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | Cluster 15 | +1 | +0.1194 | +0.2682 | +0.2691 | 0.0000 | +0.5722 | +0.7011 | 0.860 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 14 | +1 | +0.1519 | +0.2672 | +0.2686 | 0.0000 | +0.7041 | +0.7612 | 0.869 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 8 | +1 | +0.1299 | +0.2655 | +0.2665 | 0.0000 | +0.7819 | +0.7992 | 0.315 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 23 | +1 | +0.1627 | +0.2651 | +0.2657 | 0.0000 | +0.4974 | +0.6744 | 0.932 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 7 | +1 | +0.1617 | +0.2607 | +0.2614 | 0.0000 | +0.6710 | +0.7786 | 0.891 |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 31 | +1 | +0.1619 | +0.2599 | +0.2610 | 0.0000 | +0.5271 | +0.7057 | 0.000 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 6 | +1 | +0.1388 | +0.2580 | +0.2589 | 0.0000 | +0.6265 | +0.7268 | 0.946 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 24 | +1 | +0.1542 | +0.2575 | +0.2589 | 0.0000 | +0.5916 | +0.6918 | 0.936 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 25 | +1 | +0.1438 | +0.2574 | +0.2578 | 0.0000 | +0.5489 | +0.7072 | 0.894 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 12 | +1 | +0.1572 | +0.2557 | +0.2570 | 0.0000 | +0.6130 | +0.7365 | 0.906 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0` | Cluster 24 | +1 | +0.1649 | +0.2557 | +0.2569 | 0.0000 | +0.4864 | +0.6816 | 0.941 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Cluster 3 | +1 | +0.1415 | +0.2548 | +0.2555 | 0.0000 | +0.6451 | +0.7607 | 0.883 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 28 | +1 | +0.1153 | +0.2517 | +0.2530 | 0.0000 | +0.6115 | +0.7052 | 0.880 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 32 | +1 | +0.1532 | +0.2510 | +0.2517 | 0.0000 | +0.5328 | +0.7191 | 0.904 |
| `combo_min__first_bar_return__limit_down_proximity_early` | Cluster 6 | +1 | +0.1236 | +0.2454 | +0.2463 | 0.0000 | +0.5984 | +0.6898 | 0.930 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Cluster 11 | +1 | +0.1296 | +0.2445 | +0.2461 | 0.0000 | +0.4506 | +0.6795 | 0.878 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 0 | +1 | +0.1402 | +0.2439 | +0.2457 | 0.0000 | +0.4476 | +0.6590 | 0.922 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Cluster 24 | +1 | +0.1562 | +0.2431 | +0.2440 | 0.0000 | +0.5808 | +0.7006 | 0.938 |
| `opening_drive_thrust_ratio` | Cluster 33 | +1 | +0.1143 | +0.2418 | +0.2438 | 0.0000 | +0.5411 | +0.7016 | 0.907 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Cluster 15 | +1 | +0.1351 | +0.2400 | +0.2409 | 0.0000 | +0.5252 | +0.6929 | 0.845 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 31 | +1 | +0.1487 | +0.2369 | +0.2383 | 0.0000 | +0.4898 | +0.6918 | 0.925 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | Cluster 4 | +1 | +0.1433 | +0.2362 | +0.2363 | 0.0000 | +0.5173 | +0.6898 | 0.936 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 28 | +1 | +0.1155 | +0.2361 | +0.2375 | 0.0000 | +0.5942 | +0.7062 | 0.949 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 28 | +1 | +0.1315 | +0.2355 | +0.2365 | 0.0000 | +0.6505 | +0.7262 | 0.875 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 0 | +1 | +0.1466 | +0.2336 | +0.2354 | 0.0000 | +0.4500 | +0.6821 | 0.873 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | Cluster 17 | +1 | +0.1195 | +0.2334 | +0.2349 | 0.0000 | +0.5659 | +0.7452 | 0.844 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 16 | +1 | +0.1633 | +0.2328 | +0.2337 | 0.0000 | +0.5155 | +0.6795 | 0.815 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 0 | +1 | +0.1406 | +0.2286 | +0.2301 | 0.0000 | +0.4719 | +0.6795 | 0.925 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 12 | +1 | +0.1418 | +0.2283 | +0.2295 | 0.0000 | +0.5990 | +0.7555 | 0.933 |
| `combo_z_sum__max_up_ret__gap_pct` | Cluster 22 | +1 | +0.1537 | +0.2277 | +0.2280 | 0.0000 | +0.5756 | +0.7093 | 0.943 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Cluster 31 | +1 | +0.1563 | +0.2277 | +0.2291 | 0.0000 | +0.4677 | +0.6574 | 0.935 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 0 | +1 | +0.1416 | +0.2273 | +0.2288 | 0.0000 | +0.5309 | +0.7103 | 0.948 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 0 | +1 | +0.1402 | +0.2239 | +0.2256 | 0.0000 | +0.4500 | +0.6888 | 0.947 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | Cluster 29 | +1 | +0.1105 | +0.2203 | +0.2208 | 0.0000 | +0.4556 | +0.6800 | 0.628 |
| `combo_max__rbreaker_sell_setup_proximity_early__gap_pct` | Cluster 5 | +1 | +0.1218 | +0.2200 | +0.2201 | 0.0000 | +0.5405 | +0.6821 | 0.755 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | Cluster 2 | +1 | +0.1263 | +0.2197 | +0.2201 | 0.0000 | +0.4871 | +0.6923 | 0.906 |
| `combo_max__max_up_ret__volume_price_confirmation` | Cluster 19 | +1 | +0.1436 | +0.2195 | +0.2205 | 0.0000 | +0.6197 | +0.7144 | 0.871 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | Cluster 10 | +1 | +0.1184 | +0.2176 | +0.2185 | 0.0000 | +0.5028 | +0.6677 | 0.891 |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | Cluster 18 | +1 | +0.1340 | +0.2176 | +0.2193 | 0.0000 | +0.4283 | +0.6543 | 0.866 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Cluster 1 | +1 | +0.1380 | +0.2157 | +0.2170 | 0.0000 | +0.4049 | +0.6502 | 0.921 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | Cluster 2 | +1 | +0.1271 | +0.2156 | +0.2160 | 0.0000 | +0.4222 | +0.6739 | 0.492 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | Cluster 29 | +1 | +0.1157 | +0.2149 | +0.2155 | 0.0000 | +0.4148 | +0.6687 | 0.867 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | Cluster 33 | +1 | +0.1220 | +0.2140 | +0.2164 | 0.0000 | +0.6771 | +0.7612 | 0.887 |
| `max_up_ret` | Cluster 12 | +1 | +0.1282 | +0.2136 | +0.2148 | 0.0000 | +0.5942 | +0.7165 | 0.942 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | Cluster 17 | +1 | +0.1285 | +0.2111 | +0.2126 | 0.0000 | +0.4468 | +0.6590 | 0.948 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 22 | +1 | +0.1243 | +0.2094 | +0.2090 | 0.0000 | +0.4687 | +0.6739 | 0.763 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__star50_limit_proximity_early` | Cluster 26 | +1 | +0.1282 | +0.2060 | +0.2061 | 0.0000 | +0.4774 | +0.6656 | 0.945 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Cluster 13 | +1 | +0.1223 | +0.2058 | +0.2072 | 0.0000 | +0.5002 | +0.7180 | 0.904 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | Cluster 2 | +1 | +0.1350 | +0.2039 | +0.2041 | 0.0000 | +0.5874 | +0.7021 | 0.941 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 0 | +1 | +0.1288 | +0.2025 | +0.2048 | 0.0000 | +0.3580 | +0.7083 | 0.934 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1346 | +0.2021 | +0.2034 | 0.0000 | +0.5089 | +0.6831 | 0.879 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | Cluster 17 | +1 | +0.1220 | +0.2012 | +0.2027 | 0.0000 | +0.4139 | +0.6569 | 0.891 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | Cluster 30 | +1 | +0.1204 | +0.2006 | +0.2009 | 0.0000 | +0.3648 | +0.6826 | 0.890 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct` | Cluster 5 | +1 | +0.1214 | +0.1991 | +0.1991 | 0.0002 | +0.4350 | +0.6579 | 0.910 |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | Cluster 13 | +1 | +0.1212 | +0.1990 | +0.2002 | 0.0002 | +0.4682 | +0.6959 | 0.881 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1345 | +0.1982 | +0.1997 | 0.0002 | +0.5336 | +0.6739 | 0.911 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Cluster 26 | +1 | +0.1370 | +0.1971 | +0.1978 | 0.0002 | +0.4809 | +0.6713 | 0.814 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev` | Cluster 30 | +1 | +0.1204 | +0.1950 | +0.1952 | 0.0002 | +0.4341 | +0.6533 | 0.839 |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | Cluster 0 | +1 | +0.1314 | +0.1882 | +0.1900 | 0.0002 | +0.3714 | +0.6533 | 0.908 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__first_bar_return` | Cluster 34 | +1 | +0.1364 | +0.1851 | +0.1865 | 0.0002 | +0.4277 | +0.6764 | 0.856 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Cluster 20 | +1 | +0.1261 | +0.1849 | +0.1866 | 0.0002 | +0.3769 | +0.6564 | 0.870 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 0 | +1 | +0.1350 | +0.1837 | +0.1855 | 0.0002 | +0.4576 | +0.6605 | 0.911 |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 19 | +1 | +0.1357 | +0.1816 | +0.1830 | 0.0002 | +0.4308 | +0.6795 | 0.826 |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | Cluster 1 | +1 | +0.1412 | +0.1802 | +0.1801 | 0.0002 | +0.4868 | +0.6836 | 0.852 |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 19 | +1 | +0.1228 | +0.1766 | +0.1784 | 0.0002 | +0.3569 | +0.6626 | 0.908 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Cluster 9 | +1 | +0.1112 | +0.1700 | +0.1698 | 0.0006 | +0.6940 | +0.7483 | 0.760 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 12 | +1 | +0.1182 | +0.1684 | +0.1702 | 0.0008 | +0.5036 | +0.7242 | 0.905 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 9 | +1 | +0.0958 | +0.1628 | +0.1639 | 0.0012 | +0.4227 | +0.6918 | 0.832 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 27 | +1 | +0.1095 | +0.1551 | +0.1554 | 0.0018 | +0.4801 | +0.6959 | 0.135 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Cluster 21 | +1 | +0.0591 | +0.1499 | +0.1520 | 0.0022 | +0.4729 | +0.7052 | 0.434 |

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
| 300ETF | single | 61 | 25 | 0.2655 | `[9, 5, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (25 clusters)]` |
| 500ETF | single | 338 | 110 | 0.2074 | `[18, 18, 14, 13, 12, 12, 11, 11, 11, 10, 7, 5, ... (110 clusters)]` |
| 159915ETF | single | 78 | 35 | 0.2633 | `[8, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (35 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 9 | 0.2655 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_min__star50_limit_proximity_early__bar_body_rng_0`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_tri_min__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 1 | 1 | 0.2655 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | _(none)_ |
| 300ETF | single | Cluster 2 | 2 | 0.2655 | `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `combo_rank_max__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 3 | 1 | 0.2655 | `combo_tri_mean__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 4 | 2 | 0.2655 | `combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` |
| 300ETF | single | Cluster 5 | 5 | 0.2655 | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_min__opening_drive_thrust_ratio__max_up_ret`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration`, `combo_mean__opening_drive_thrust_ratio__max_up_ret`, `max_up_ret` |
| 300ETF | single | Cluster 6 | 2 | 0.2655 | `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 300ETF | single | Cluster 7 | 1 | 0.2655 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 8 | 1 | 0.2655 | `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | _(none)_ |
| 300ETF | single | Cluster 9 | 3 | 0.2655 | `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 300ETF | single | Cluster 10 | 2 | 0.2655 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` |
| 300ETF | single | Cluster 11 | 2 | 0.2655 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 12 | 3 | 0.2655 | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`, `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 13 | 3 | 0.2655 | `combo_ratio__limit_down_proximity_early__volume_concentration` | `combo_rel_diff__rbreaker_buy_setup_proximity_early__volume_concentration`, `combo_clamp_diff__limit_down_proximity_early__volume_concentration` |
| 300ETF | single | Cluster 14 | 4 | 0.2655 | `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_max__first_bar_return__bar_body_rng_0`, `combo_tri_mean__first_bar_return__bar_body_rng_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 15 | 1 | 0.2655 | `combo_sig_product__first_bar_return__morning_volume_weighted_momentum` | _(none)_ |
| 300ETF | single | Cluster 16 | 2 | 0.2655 | `rbreaker_sell_setup_proximity_early` | `star50_limit_proximity_early` |
| 300ETF | single | Cluster 17 | 2 | 0.2655 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 18 | 1 | 0.2655 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 19 | 3 | 0.2655 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`, `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` |
| 300ETF | single | Cluster 20 | 2 | 0.2655 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 21 | 2 | 0.2655 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` |
| 300ETF | single | Cluster 22 | 1 | 0.2655 | `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 23 | 4 | 0.2655 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position`, `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` |
| 300ETF | single | Cluster 24 | 2 | 0.2655 | `combo_tri_max__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` |
| 500ETF | single | Cluster 0 | 18 | 0.2074 | `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | `combo_rank_max__max_up_ret__early_body_momentum`, `combo_tri_max__max_up_ret__early_body_momentum__trend_day_regime_conviction`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum`, `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation`, `combo_rank_min__max_up_ret__close_vs_open_range`, `combo_mean__max_up_ret__vwap_close_divergence_trend`, `combo_rank_max__max_up_ret__close_vs_open_range`, `combo_diff__max_up_ret__h2_l2_pullback_continuation`, `combo_rank_max__max_up_ret__shaved_bar_trend_conviction`, `combo_min__max_up_ret__close_vs_open_range`, `combo_max__max_up_ret__close_vs_open_range`, `combo_mean__max_up_ret__close_vs_open_range`, `combo_max__max_up_ret__shaved_bar_trend_conviction`, `combo_min__max_up_ret__vwap_close_divergence_trend`, `combo_min__max_up_ret__rsi_opening`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration`, `combo_min__max_up_ret__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 1 | 2 | 0.2074 | `combo_sig_product__early_order_flow_imbalance__bar_body_rng_0` | `combo_sig_product__early_order_flow_imbalance__close_vs_open_range` |
| 500ETF | single | Cluster 2 | 3 | 0.2074 | `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | `combo_sig_product__bar_ret_0__early_order_flow_imbalance`, `combo_sig_product__bar_ret_0__close_vs_open_range` |
| 500ETF | single | Cluster 3 | 3 | 0.2074 | `combo_sig_product__max_down_ret__close_vs_open_range` | `combo_sig_product__max_down_ret__vwap_close_divergence_trend`, `combo_sig_product__max_down_ret__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 4 | 2 | 0.2074 | `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `combo_sig_product__opening_drive_thrust_ratio__early_order_flow_imbalance` |
| 500ETF | single | Cluster 5 | 12 | 0.2074 | `opening_drive_thrust_ratio` | `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`, `combo_min__max_up_ret__max_down_ret`, `combo_max__opening_drive_thrust_ratio__max_down_ret`, `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`, `combo_rank_max__opening_drive_thrust_ratio__max_down_ret`, `combo_mean__opening_drive_thrust_ratio__max_down_ret`, `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`, `combo_rank_min__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_min__max_up_ret__max_down_ret` |
| 500ETF | single | Cluster 6 | 7 | 0.2074 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 7 | 2 | 0.2074 | `combo_min__early_order_flow_imbalance__close_vs_open_range` | `combo_rank_min__early_order_flow_imbalance__close_vs_open_range` |
| 500ETF | single | Cluster 8 | 2 | 0.2074 | `combo_min__net_volume_flow__vwap_close_divergence_trend` | `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 9 | 2 | 0.2074 | `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 10 | 2 | 0.2074 | `combo_max__early_body_momentum__close_vs_open_range` | `combo_rank_max__early_body_momentum__close_vs_open_range` |
| 500ETF | single | Cluster 11 | 1 | 0.2074 | `combo_sig_product__net_volume_flow__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 12 | 2 | 0.2074 | `combo_rank_max__trend_day_regime_conviction__shaved_bar_trend_conviction` | `combo_mean__net_volume_flow__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 13 | 4 | 0.2074 | `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation`, `combo_rel_diff__net_volume_flow__h2_l2_pullback_continuation`, `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 14 | 2 | 0.2074 | `combo_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | `combo_rel_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 15 | 3 | 0.2074 | `combo_rank_min__close_vs_open_range__vwap_close_divergence_trend` | `combo_min__close_vs_open_range__vwap_close_divergence_trend`, `combo_mean__close_vs_open_range__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 16 | 1 | 0.2074 | `combo_sig_product__volatility_expansion_trend_vector__early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 17 | 3 | 0.2074 | `combo_rank_min__close_vs_open_range__shaved_bar_trend_conviction` | `combo_mean__close_vs_open_range__shaved_bar_trend_conviction`, `combo_min__close_vs_open_range__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 18 | 2 | 0.2074 | `combo_rank_max__trend_day_regime_conviction__early_order_flow_imbalance` | `combo_max__early_body_momentum__early_order_flow_imbalance` |
| 500ETF | single | Cluster 19 | 2 | 0.2074 | `combo_mean__net_volume_flow__close_vs_open_range` | `combo_rank_min__net_volume_flow__close_vs_open_range` |
| 500ETF | single | Cluster 20 | 1 | 0.2074 | `combo_tri_median__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 21 | 2 | 0.2074 | `open_to_current_return` | `morning_volume_weighted_momentum` |
| 500ETF | single | Cluster 22 | 1 | 0.2074 | `combo_sig_product__rsi_opening__h2_l2_pullback_continuation` | _(none)_ |
| 500ETF | single | Cluster 23 | 2 | 0.2074 | `combo_min__trend_day_regime_conviction__close_vs_open_range` | `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` |
| 500ETF | single | Cluster 24 | 2 | 0.2074 | `combo_sig_product__early_body_momentum__close_vs_open_range` | `early_body_momentum` |
| 500ETF | single | Cluster 25 | 5 | 0.2074 | `combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction` | `combo_abs_diff__max_up_ret__shaved_bar_trend_conviction`, `combo_rank_max__max_down_ret__h2_l2_pullback_continuation`, `combo_rel_diff__max_up_ret__shaved_bar_trend_conviction`, `combo_diff__net_volume_flow__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 26 | 2 | 0.2074 | `combo_mean__net_volume_flow__max_down_ret` | `combo_max__net_volume_flow__max_down_ret` |
| 500ETF | single | Cluster 27 | 2 | 0.2074 | `combo_min__net_volume_flow__bar_ret_0` | `combo_rank_min__trend_bar_close_consistency__bar_ret_0` |
| 500ETF | single | Cluster 28 | 3 | 0.2074 | `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation`, `combo_diff__bar_ret_0__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 29 | 1 | 0.2074 | `combo_tri_median__trend_bar_close_consistency__star50_limit_proximity_early__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 30 | 2 | 0.2074 | `combo_mean__net_volume_flow__bar_body_rng_0` | `combo_mean__close_vs_open_range__bar_body_rng_0` |
| 500ETF | single | Cluster 31 | 2 | 0.2074 | `combo_min__bar_ret_0__vwap_close_divergence_trend` | `combo_min__vwap_close_divergence_trend__bar_body_rng_0` |
| 500ETF | single | Cluster 32 | 1 | 0.2074 | `combo_min__close_vs_open_range__bar_body_rng_0` | _(none)_ |
| 500ETF | single | Cluster 33 | 1 | 0.2074 | `combo_rank_max__early_order_flow_imbalance__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 34 | 1 | 0.2074 | `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 35 | 1 | 0.2074 | `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 36 | 2 | 0.2074 | `combo_rank_min__first_bar_return__close_vs_open_range` | `combo_min__first_bar_return__close_vs_open_range` |
| 500ETF | single | Cluster 37 | 1 | 0.2074 | `combo_mean__bar_body_rng_0__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 38 | 13 | 0.2074 | `combo_rel_diff__max_up_ret__body_size_progression` | `combo_rel_diff__max_up_ret__late_bar_momentum`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_clamp_diff__max_up_ret__smooth_momentum_structure`, `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_clamp_diff__max_up_ret__body_size_progression`, `combo_diff__max_up_ret__body_size_progression`, `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence`, `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 39 | 2 | 0.2074 | `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 40 | 1 | 0.2074 | `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 41 | 1 | 0.2074 | `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 42 | 3 | 0.2074 | `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend`, `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 43 | 2 | 0.2074 | `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` |
| 500ETF | single | Cluster 44 | 1 | 0.2074 | `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | _(none)_ |
| 500ETF | single | Cluster 45 | 2 | 0.2074 | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` |
| 500ETF | single | Cluster 46 | 2 | 0.2074 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 47 | 2 | 0.2074 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 48 | 4 | 0.2074 | `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 49 | 2 | 0.2074 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 50 | 3 | 0.2074 | `combo_diff__first_bar_return__demark_setup_reversal_early` | `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early`, `combo_rel_diff__first_bar_return__demark_setup_reversal_early` |
| 500ETF | single | Cluster 51 | 2 | 0.2074 | `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` |
| 500ETF | single | Cluster 52 | 2 | 0.2074 | `combo_tri_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_max__net_volume_flow__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 53 | 1 | 0.2074 | `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 54 | 2 | 0.2074 | `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | `combo_max__bar_ret_0__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 55 | 2 | 0.2074 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `max_up_ret` |
| 500ETF | single | Cluster 56 | 1 | 0.2074 | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 500ETF | single | Cluster 57 | 1 | 0.2074 | `combo_min__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 500ETF | single | Cluster 58 | 3 | 0.2074 | `combo_max__max_up_ret__early_order_flow_imbalance` | `combo_rank_max__max_up_ret__early_order_flow_imbalance`, `combo_mean__max_up_ret__early_order_flow_imbalance` |
| 500ETF | single | Cluster 59 | 2 | 0.2074 | `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | `combo_min__max_up_ret__early_order_flow_imbalance` |
| 500ETF | single | Cluster 60 | 2 | 0.2074 | `combo_max__max_up_ret__vwap_close_divergence_trend` | `combo_rank_max__max_up_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 61 | 14 | 0.2074 | `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | `combo_rank_max__net_volume_flow__star50_limit_proximity_early`, `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_rank_max__trend_bar_close_consistency__star50_limit_proximity_early`, `combo_max__net_volume_flow__star50_limit_proximity_early`, `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_max__volatility_expansion_trend_vector__star50_limit_proximity_early`, `combo_rank_max__star50_limit_proximity_early__close_vs_open_range`, `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`, `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction`, `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend`, `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction`, `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 62 | 5 | 0.2074 | `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`, `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`, `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` |
| 500ETF | single | Cluster 63 | 2 | 0.2074 | `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `combo_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 64 | 4 | 0.2074 | `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend`, `combo_rank_max__max_down_ret__vwap_close_divergence_trend`, `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 65 | 2 | 0.2074 | `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | `combo_rank_min__opening_drive_thrust_ratio__early_order_flow_imbalance` |
| 500ETF | single | Cluster 66 | 12 | 0.2074 | `combo_sig_product__max_up_ret__close_vs_open_range` | `combo_sig_product__max_up_ret__early_body_momentum`, `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`, `combo_sig_product__max_up_ret__h2_l2_pullback_continuation`, `combo_sig_product__max_up_ret__vwap_close_divergence_trend`, `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`, `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_sig_product__max_up_ret__max_down_ret`, `combo_sig_product__max_up_ret__body_size_progression`, `combo_sig_product__max_up_ret__shaved_bar_trend_conviction`, `combo_sig_product__max_up_ret__early_order_flow_imbalance`, `combo_sig_product__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 67 | 2 | 0.2074 | `combo_mean__max_up_ret__bar_ret_0` | `combo_mean__max_up_ret__bar_body_rng_0` |
| 500ETF | single | Cluster 68 | 1 | 0.2074 | `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | _(none)_ |
| 500ETF | single | Cluster 69 | 3 | 0.2074 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`, `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` |
| 500ETF | single | Cluster 70 | 2 | 0.2074 | `combo_rank_max__net_volume_flow__bar_ret_0` | `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` |
| 500ETF | single | Cluster 71 | 2 | 0.2074 | `combo_rank_max__max_up_ret__bar_ret_0` | `combo_max__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 72 | 1 | 0.2074 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 73 | 2 | 0.2074 | `combo_rank_min__max_up_ret__bar_body_rng_0` | `combo_min__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 74 | 1 | 0.2074 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 75 | 10 | 0.2074 | `combo_min__first_bar_return__bar_body_rng_0` | `combo_mean__bar_ret_0__max_down_ret`, `combo_rank_min__bar_ret_0__bar_body_rng_0`, `combo_max__first_bar_return__max_down_ret`, `first_bar_return`, `combo_rank_max__bar_ret_0__max_down_ret`, `combo_min__first_bar_return__max_down_ret`, `combo_rank_min__bar_ret_0__max_down_ret`, `combo_min__max_down_ret__bar_body_rng_0`, `combo_max__first_bar_return__bar_body_rng_0` |
| 500ETF | single | Cluster 76 | 11 | 0.2074 | `combo_mean__star50_limit_proximity_early__first_bar_return` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`, `combo_rank_min__star50_limit_proximity_early__bar_ret_0`, `combo_min__star50_limit_proximity_early__bar_ret_0`, `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_max__star50_limit_proximity_early__first_bar_return`, `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_max__star50_limit_proximity_early__bar_body_rng_0`, `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 500ETF | single | Cluster 77 | 18 | 0.2074 | `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction`, `combo_mean__opening_drive_thrust_ratio__close_vs_open_range`, `combo_min__opening_drive_thrust_ratio__rsi_opening`, `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__early_body_momentum`, `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`, `combo_max__opening_drive_thrust_ratio__early_body_momentum`, `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`, `combo_min__opening_drive_thrust_ratio__close_vs_open_range`, `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance`, `combo_max__opening_drive_thrust_ratio__close_vs_open_range`, `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`, `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum`, `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow`, `combo_mean__max_down_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 78 | 3 | 0.2074 | `combo_min__early_order_flow_imbalance__max_down_ret` | `combo_rank_min__early_order_flow_imbalance__max_down_ret`, `combo_mean__early_order_flow_imbalance__max_down_ret` |
| 500ETF | single | Cluster 79 | 2 | 0.2074 | `combo_rank_min__trend_bar_close_consistency__max_down_ret` | `combo_min__trend_bar_close_consistency__max_down_ret` |
| 500ETF | single | Cluster 80 | 2 | 0.2074 | `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | `combo_min__max_down_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 81 | 2 | 0.2074 | `combo_max__max_down_ret__close_vs_open_range` | `combo_rank_max__max_down_ret__close_vs_open_range` |
| 500ETF | single | Cluster 82 | 1 | 0.2074 | `combo_rank_max__early_body_momentum__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 83 | 3 | 0.2074 | `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | `combo_diff__max_down_ret__h2_l2_pullback_continuation`, `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` |
| 500ETF | single | Cluster 84 | 1 | 0.2074 | `combo_mean__max_down_ret__close_vs_open_range` | _(none)_ |
| 500ETF | single | Cluster 85 | 2 | 0.2074 | `combo_rank_min__max_down_ret__close_vs_open_range` | `combo_min__max_down_ret__close_vs_open_range` |
| 500ETF | single | Cluster 86 | 2 | 0.2074 | `combo_min__max_down_ret__shaved_bar_trend_conviction` | `combo_mean__max_down_ret__shaved_bar_trend_conviction` |
| 500ETF | single | Cluster 87 | 1 | 0.2074 | `max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 88 | 2 | 0.2074 | `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` |
| 500ETF | single | Cluster 89 | 1 | 0.2074 | `combo_z_sum__vwap_close_divergence_trend__bar_body_rng_0` | _(none)_ |
| 500ETF | single | Cluster 90 | 1 | 0.2074 | `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 91 | 3 | 0.2074 | `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | `combo_max__first_bar_return__close_vs_open_range`, `combo_max__net_volume_flow__first_bar_return` |
| 500ETF | single | Cluster 92 | 2 | 0.2074 | `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` |
| 500ETF | single | Cluster 93 | 1 | 0.2074 | `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 94 | 1 | 0.2074 | `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 95 | 2 | 0.2074 | `combo_mean__trend_day_regime_conviction__bar_ret_0` | `combo_mean__first_bar_return__close_vs_open_range` |
| 500ETF | single | Cluster 96 | 3 | 0.2074 | `combo_max__max_up_ret__max_down_ret` | `combo_mean__max_up_ret__max_down_ret`, `combo_rank_max__max_up_ret__max_down_ret` |
| 500ETF | single | Cluster 97 | 11 | 0.2074 | `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early`, `combo_rank_min__net_volume_flow__star50_limit_proximity_early`, `combo_mean__early_body_momentum__star50_limit_proximity_early`, `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early`, `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`, `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`, `combo_tri_min__early_body_momentum__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 98 | 2 | 0.2074 | `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 99 | 1 | 0.2074 | `combo_mean__star50_limit_proximity_early__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 100 | 1 | 0.2074 | `combo_tri_mean__max_up_ret__net_volume_flow__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 101 | 5 | 0.2074 | `combo_diff__net_volume_flow__demark_setup_reversal_early` | `combo_rel_diff__net_volume_flow__demark_setup_reversal_early`, `combo_rel_diff__early_order_flow_imbalance__demark_setup_reversal_early`, `combo_rel_diff__volatility_expansion_trend_vector__demark_setup_reversal_early`, `combo_rel_diff__trend_bar_close_consistency__demark_setup_reversal_early` |
| 500ETF | single | Cluster 102 | 2 | 0.2074 | `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` |
| 500ETF | single | Cluster 103 | 2 | 0.2074 | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 104 | 4 | 0.2074 | `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | `combo_diff__first_bar_return__early_late_momentum_divergence`, `combo_rel_diff__bar_ret_0__late_bar_momentum`, `combo_ratio__bar_ret_0__net_volume_flow` |
| 500ETF | single | Cluster 105 | 1 | 0.2074 | `combo_sig_product__star50_limit_proximity_early__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 106 | 2 | 0.2074 | `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` |
| 500ETF | single | Cluster 107 | 3 | 0.2074 | `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early`, `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early` |
| 500ETF | single | Cluster 108 | 3 | 0.2074 | `combo_min__star50_limit_proximity_early__max_down_ret` | `combo_rank_min__star50_limit_proximity_early__max_down_ret`, `combo_mean__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 109 | 11 | 0.2074 | `combo_max__early_body_momentum__bar_body_rng_0` | `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0`, `combo_min__bar_ret_0__early_order_flow_imbalance`, `combo_max__bar_ret_0__early_order_flow_imbalance`, `combo_mean__first_bar_return__early_order_flow_imbalance`, `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0`, `combo_rank_max__bar_ret_0__early_order_flow_imbalance`, `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction`, `combo_max__close_vs_open_range__bar_body_rng_0`, `combo_max__first_bar_return__shaved_bar_trend_conviction`, `combo_max__bar_body_rng_0__shaved_bar_trend_conviction` |
| 159915ETF | single | Cluster 0 | 8 | 0.2633 | `combo_mean__max_up_ret__bar_body_rng_0` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`, `combo_rank_max__max_up_ret__first_bar_return`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`, `combo_max__max_up_ret__bar_ret_0`, `combo_rank_max__opening_drive_thrust_ratio__first_bar_return`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`, `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 1 | 2 | 0.2633 | `combo_rank_min__max_up_ret__bar_body_rng_0` | `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 2 | 3 | 0.2633 | `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend`, `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` |
| 159915ETF | single | Cluster 3 | 2 | 0.2633 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 4 | 1 | 0.2633 | `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 5 | 2 | 0.2633 | `combo_max__rbreaker_sell_setup_proximity_early__gap_pct` | `combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct` |
| 159915ETF | single | Cluster 6 | 3 | 0.2633 | `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_min__first_bar_return__limit_down_proximity_early` |
| 159915ETF | single | Cluster 7 | 1 | 0.2633 | `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | _(none)_ |
| 159915ETF | single | Cluster 8 | 2 | 0.2633 | `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` |
| 159915ETF | single | Cluster 9 | 2 | 0.2633 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 10 | 1 | 0.2633 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | _(none)_ |
| 159915ETF | single | Cluster 11 | 1 | 0.2633 | `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | _(none)_ |
| 159915ETF | single | Cluster 12 | 4 | 0.2633 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `max_up_ret`, `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 13 | 4 | 0.2633 | `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__early_late_momentum_divergence`, `combo_rel_diff__max_up_ret__early_late_momentum_divergence` |
| 159915ETF | single | Cluster 14 | 4 | 0.2633 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 15 | 2 | 0.2633 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `combo_min__star50_limit_proximity_early__volume_price_confirmation` |
| 159915ETF | single | Cluster 16 | 1 | 0.2633 | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | _(none)_ |
| 159915ETF | single | Cluster 17 | 3 | 0.2633 | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev`, `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` |
| 159915ETF | single | Cluster 18 | 1 | 0.2633 | `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | _(none)_ |
| 159915ETF | single | Cluster 19 | 3 | 0.2633 | `combo_max__max_up_ret__volume_price_confirmation` | `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation`, `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` |
| 159915ETF | single | Cluster 20 | 1 | 0.2633 | `combo_max__max_up_ret__volume_weighted_price_position` | _(none)_ |
| 159915ETF | single | Cluster 21 | 1 | 0.2633 | `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 22 | 2 | 0.2633 | `combo_z_sum__max_up_ret__gap_pct` | `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 23 | 1 | 0.2633 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | _(none)_ |
| 159915ETF | single | Cluster 24 | 3 | 0.2633 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0` | `combo_mean__star50_limit_proximity_early__bar_ret_0`, `combo_mean__star50_limit_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 25 | 3 | 0.2633 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0`, `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` |
| 159915ETF | single | Cluster 26 | 2 | 0.2633 | `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 27 | 1 | 0.2633 | `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 28 | 3 | 0.2633 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 29 | 2 | 0.2633 | `combo_rel_diff__max_up_ret__keltner_squeeze_width` | `combo_diff__max_up_ret__keltner_squeeze_width` |
| 159915ETF | single | Cluster 30 | 2 | 0.2633 | `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev` | `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` |
| 159915ETF | single | Cluster 31 | 3 | 0.2633 | `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 32 | 1 | 0.2633 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | _(none)_ |
| 159915ETF | single | Cluster 33 | 2 | 0.2633 | `opening_drive_thrust_ratio` | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 34 | 1 | 0.2633 | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__first_bar_return` | _(none)_ |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`limit_down_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | `min` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | `tri_mean` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_mean__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | `tri_mean` | a=`first_bar_return`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_surge_max` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_surge_max` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`morning_volume_weighted_momentum` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__first_bar_return__bar_body_rng_0` | `max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__volume_concentration` | `rel_diff` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_concentration` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_tri_max__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | `tri_max` | a=`bar_ret_0`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_clamp_diff__limit_down_proximity_early__volume_concentration` | `clamp_diff` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_concentration` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | `rank_max` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_sig_product__first_bar_return__morning_volume_weighted_momentum` | `sig_product` | a=`first_bar_return`, b=`morning_volume_weighted_momentum` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | `tri_min` | a=`max_up_ret`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency`, c=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`early_body_momentum` |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | `clamp_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | `rank_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_tri_mean__max_up_ret__net_volume_flow__star50_limit_proximity_early` | `tri_mean` | a=`max_up_ret`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_day_regime_conviction` |
| `combo_max__early_body_momentum__bar_body_rng_0` | `max` | a=`early_body_momentum`, b=`bar_body_rng_0` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | `mean` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | `mean` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range` |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_min` | a=`trend_bar_close_consistency`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | `mean` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`early_order_flow_imbalance` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_tri_min__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | `tri_min` | a=`early_body_momentum`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | `rank_min` | a=`trend_bar_close_consistency`, b=`star50_limit_proximity_early` |
| `combo_min__opening_drive_thrust_ratio__rsi_opening` | `min` | a=`opening_drive_thrust_ratio`, b=`rsi_opening` |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | `max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range` |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | `mean` | a=`opening_drive_thrust_ratio`, b=`early_order_flow_imbalance` |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | `mean` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__max_up_ret__max_down_ret` | `rank_min` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_mean__early_body_momentum__star50_limit_proximity_early` | `mean` | a=`early_body_momentum`, b=`star50_limit_proximity_early` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | `clamp_diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_mean__net_volume_flow__bar_body_rng_0` | `mean` | a=`net_volume_flow`, b=`bar_body_rng_0` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`shaved_bar_trend_conviction` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__max_up_ret__close_vs_open_range` | `rank_min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_sig_product__max_up_ret__early_body_momentum` | `sig_product` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | `rel_diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | `clamp_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__early_order_flow_imbalance` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`early_order_flow_imbalance` |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`vwap_close_divergence_trend` |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | `mean` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | `rank_min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | `rel_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | `max` | a=`volatility_expansion_trend_vector`, b=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | `rank_min` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | `diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | `tri_max` | a=`max_up_ret`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_max__max_up_ret__max_down_ret` | `max` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | `clamp_diff` | a=`first_bar_return`, b=`early_late_momentum_divergence` |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | `diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | `min` | a=`trend_day_regime_conviction`, b=`close_vs_open_range` |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | `rank_min` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | `rank_min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | `min` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_diff__net_volume_flow__demark_setup_reversal_early` | `diff` | a=`net_volume_flow`, b=`demark_setup_reversal_early` |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | `tri_mean` | a=`max_up_ret`, b=`trend_bar_close_consistency`, c=`bar_ret_0` |
| `combo_min__net_volume_flow__bar_ret_0` | `min` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_tri_median__trend_bar_close_consistency__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`trend_bar_close_consistency`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | `rank_min` | a=`trend_bar_close_consistency`, b=`bar_ret_0` |
| `combo_mean__net_volume_flow__close_vs_open_range` | `mean` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | `min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_rel_diff__net_volume_flow__demark_setup_reversal_early` | `rel_diff` | a=`net_volume_flow`, b=`demark_setup_reversal_early` |
| `combo_min__max_up_ret__close_vs_open_range` | `min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__max_up_ret__close_vs_open_range` | `mean` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_max__trend_day_regime_conviction__early_order_flow_imbalance` | `rank_max` | a=`trend_day_regime_conviction`, b=`early_order_flow_imbalance` |
| `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__max_up_ret__early_order_flow_imbalance` | `sig_product` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | `min` | a=`star50_limit_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction` |
| `combo_tri_max__max_up_ret__early_body_momentum__trend_day_regime_conviction` | `tri_max` | a=`max_up_ret`, b=`early_body_momentum`, c=`trend_day_regime_conviction` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rel_diff__volatility_expansion_trend_vector__demark_setup_reversal_early` | `rel_diff` | a=`volatility_expansion_trend_vector`, b=`demark_setup_reversal_early` |
| `combo_min__max_up_ret__rsi_opening` | `min` | a=`max_up_ret`, b=`rsi_opening` |
| `combo_max__max_up_ret__close_vs_open_range` | `max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__early_body_momentum__early_order_flow_imbalance` | `max` | a=`early_body_momentum`, b=`early_order_flow_imbalance` |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | `mean` | a=`close_vs_open_range`, b=`bar_body_rng_0` |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | `rel_diff` | a=`volatility_expansion_trend_vector`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__first_bar_return__bar_body_rng_0` | `min` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__early_order_flow_imbalance__max_down_ret` | `min` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | `sig_product` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_rel_diff__net_volume_flow__h2_l2_pullback_continuation` | `rel_diff` | a=`net_volume_flow`, b=`h2_l2_pullback_continuation` |
| `combo_min__max_up_ret__max_down_ret` | `min` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | `rank_min` | a=`star50_limit_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rel_diff__max_up_ret__shaved_bar_trend_conviction` | `rel_diff` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_mean__max_up_ret__bar_ret_0` | `mean` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__max_up_ret__early_order_flow_imbalance` | `min` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rank_max__max_up_ret__max_down_ret` | `rank_max` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`trend_day_regime_conviction` |
| `combo_rank_max__max_up_ret__close_vs_open_range` | `rank_max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_median__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | `tri_median` | a=`early_body_momentum`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | `rank_max` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_min__first_bar_return__close_vs_open_range` | `min` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_max__max_up_ret__early_order_flow_imbalance` | `max` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rank_min__bar_ret_0__bar_body_rng_0` | `rank_min` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_rel_diff__early_order_flow_imbalance__demark_setup_reversal_early` | `rel_diff` | a=`early_order_flow_imbalance`, b=`demark_setup_reversal_early` |
| `combo_mean__star50_limit_proximity_early__vwap_close_divergence_trend` | `mean` | a=`star50_limit_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`h2_l2_pullback_continuation` |
| `combo_sig_product__bar_ret_0__early_order_flow_imbalance` | `sig_product` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | `diff` | a=`opening_drive_thrust_ratio`, b=`h2_l2_pullback_continuation` |
| `combo_rank_min__first_bar_return__close_vs_open_range` | `rank_min` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_mean__trend_day_regime_conviction__bar_ret_0` | `mean` | a=`trend_day_regime_conviction`, b=`bar_ret_0` |
| `combo_sig_product__early_body_momentum__close_vs_open_range` | `sig_product` | a=`early_body_momentum`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | `min` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | `clamp_diff` | a=`bar_body_rng_0`, b=`h2_l2_pullback_continuation` |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | `mean` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | `max` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_rank_min__close_vs_open_range__vwap_close_divergence_trend` | `rank_min` | a=`close_vs_open_range`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_mean__max_up_ret__max_down_ret` | `mean` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `max` | a=`opening_drive_thrust_ratio`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | `diff` | a=`early_order_flow_imbalance`, b=`h2_l2_pullback_continuation` |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | `rel_diff` | a=`first_bar_return`, b=`h2_l2_pullback_continuation` |
| `combo_rel_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | `rel_diff` | a=`early_order_flow_imbalance`, b=`h2_l2_pullback_continuation` |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | `tri_max` | a=`max_up_ret`, b=`early_body_momentum`, c=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | `rank_max` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_z_sum__vwap_close_divergence_trend__bar_body_rng_0` | `z_sum` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | `min` | a=`opening_drive_thrust_ratio`, b=`shaved_bar_trend_conviction` |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | `min` | a=`early_order_flow_imbalance`, b=`close_vs_open_range` |
| `combo_mean__net_volume_flow__shaved_bar_trend_conviction` | `mean` | a=`net_volume_flow`, b=`shaved_bar_trend_conviction` |
| `combo_max__first_bar_return__close_vs_open_range` | `max` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | `min` | a=`close_vs_open_range`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__net_volume_flow__bar_ret_0` | `rank_max` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_mean__first_bar_return__close_vs_open_range` | `mean` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_mean__net_volume_flow__max_down_ret` | `mean` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__early_order_flow_imbalance` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`early_order_flow_imbalance` |
| `combo_rel_diff__trend_bar_close_consistency__demark_setup_reversal_early` | `rel_diff` | a=`trend_bar_close_consistency`, b=`demark_setup_reversal_early` |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration`, c=`bar_ret_0` |
| `combo_abs_diff__max_up_ret__shaved_bar_trend_conviction` | `abs_diff` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__max_down_ret__close_vs_open_range` | `sig_product` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_rank_min__trend_bar_close_consistency__max_down_ret` | `rank_min` | a=`trend_bar_close_consistency`, b=`max_down_ret` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | `rank_min` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`early_body_momentum` |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | `rank_max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_rank_min__max_down_ret__close_vs_open_range` | `rank_min` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_max__first_bar_return__max_down_ret` | `max` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_min__bar_ret_0__max_down_ret` | `rank_min` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | `max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | `mean` | a=`first_bar_return`, b=`early_order_flow_imbalance` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__volatility_expansion_trend_vector__early_order_flow_imbalance` | `sig_product` | a=`volatility_expansion_trend_vector`, b=`early_order_flow_imbalance` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__early_body_momentum__close_vs_open_range` | `max` | a=`early_body_momentum`, b=`close_vs_open_range` |
| `combo_min__close_vs_open_range__bar_body_rng_0` | `min` | a=`close_vs_open_range`, b=`bar_body_rng_0` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_max__bar_body_rng_0__shaved_bar_trend_conviction` | `max` | a=`bar_body_rng_0`, b=`shaved_bar_trend_conviction` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__max_down_ret__close_vs_open_range` | `min` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_rank_max__early_body_momentum__max_down_ret` | `rank_max` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | `rank_max` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__early_order_flow_imbalance__close_vs_open_range` | `sig_product` | a=`early_order_flow_imbalance`, b=`close_vs_open_range` |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | `min` | a=`net_volume_flow`, b=`vwap_close_divergence_trend` |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | `min` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_min__first_bar_return__max_down_ret` | `min` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_min__early_order_flow_imbalance__close_vs_open_range` | `rank_min` | a=`early_order_flow_imbalance`, b=`close_vs_open_range` |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | `rank_max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `rel_diff` | a=`star50_limit_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rank_max__early_body_momentum__close_vs_open_range` | `rank_max` | a=`early_body_momentum`, b=`close_vs_open_range` |
| `combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction` | `clamp_diff` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `diff` | a=`star50_limit_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_mean__close_vs_open_range__shaved_bar_trend_conviction` | `mean` | a=`close_vs_open_range`, b=`shaved_bar_trend_conviction` |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | `rank_max` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_min__close_vs_open_range__shaved_bar_trend_conviction` | `min` | a=`close_vs_open_range`, b=`shaved_bar_trend_conviction` |
| `combo_rank_min__close_vs_open_range__shaved_bar_trend_conviction` | `rank_min` | a=`close_vs_open_range`, b=`shaved_bar_trend_conviction` |
| `combo_min__trend_bar_close_consistency__max_down_ret` | `min` | a=`trend_bar_close_consistency`, b=`max_down_ret` |
| `combo_rank_max__trend_day_regime_conviction__shaved_bar_trend_conviction` | `rank_max` | a=`trend_day_regime_conviction`, b=`shaved_bar_trend_conviction` |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | `diff` | a=`bar_ret_0`, b=`h2_l2_pullback_continuation` |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | `rank_min` | a=`early_order_flow_imbalance`, b=`bar_body_rng_0` |
| `combo_max__bar_ret_0__vwap_close_divergence_trend` | `max` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_min__max_up_ret__shaved_bar_trend_conviction` | `min` | a=`max_up_ret`, b=`shaved_bar_trend_conviction` |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | `min` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__trend_bar_close_consistency__star50_limit_proximity_early` | `rank_max` | a=`trend_bar_close_consistency`, b=`star50_limit_proximity_early` |
| `combo_max__net_volume_flow__first_bar_return` | `max` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_max__close_vs_open_range__bar_body_rng_0` | `max` | a=`close_vs_open_range`, b=`bar_body_rng_0` |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | `min` | a=`vwap_close_divergence_trend`, b=`shaved_bar_trend_conviction` |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | `mean` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__early_order_flow_imbalance__max_down_ret` | `mean` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_max__star50_limit_proximity_early__first_bar_return` | `max` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | `diff` | a=`volatility_expansion_trend_vector`, b=`h2_l2_pullback_continuation` |
| `combo_mean__max_down_ret__close_vs_open_range` | `mean` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | `rel_diff` | a=`volatility_expansion_trend_vector`, b=`h2_l2_pullback_continuation` |
| `combo_sig_product__max_up_ret__h2_l2_pullback_continuation` | `sig_product` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_max__net_volume_flow__max_down_ret` | `max` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | `max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | `rank_min` | a=`vwap_close_divergence_trend`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | `sig_product` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | `rank_max` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_max__volatility_expansion_trend_vector__star50_limit_proximity_early` | `max` | a=`volatility_expansion_trend_vector`, b=`star50_limit_proximity_early` |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`early_late_momentum_divergence` |
| `combo_rank_max__max_down_ret__close_vs_open_range` | `rank_max` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration`, c=`bar_ret_0` |
| `combo_max__bar_ret_0__early_order_flow_imbalance` | `max` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_diff__first_bar_return__early_late_momentum_divergence` | `diff` | a=`first_bar_return`, b=`early_late_momentum_divergence` |
| `combo_sig_product__bar_ret_0__close_vs_open_range` | `sig_product` | a=`bar_ret_0`, b=`close_vs_open_range` |
| `combo_tri_max__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | `tri_max` | a=`net_volume_flow`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration`, c=`bar_ret_0` |
| `combo_min__max_down_ret__bar_body_rng_0` | `min` | a=`max_down_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_day_regime_conviction` |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | `rank_max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_max__max_down_ret__close_vs_open_range` | `max` | a=`max_down_ret`, b=`close_vs_open_range` |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | `clamp_diff` | a=`max_down_ret`, b=`h2_l2_pullback_continuation` |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | `diff` | a=`close_vs_open_range`, b=`h2_l2_pullback_continuation` |
| `combo_rel_diff__bar_ret_0__late_bar_momentum` | `rel_diff` | a=`bar_ret_0`, b=`late_bar_momentum` |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | `min` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | `rank_max` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_rank_max__max_down_ret__h2_l2_pullback_continuation` | `rank_max` | a=`max_down_ret`, b=`h2_l2_pullback_continuation` |
| `combo_mean__max_down_ret__shaved_bar_trend_conviction` | `mean` | a=`max_down_ret`, b=`shaved_bar_trend_conviction` |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | `rank_max` | a=`bar_ret_0`, b=`shaved_bar_trend_conviction` |
| `combo_min__max_down_ret__shaved_bar_trend_conviction` | `min` | a=`max_down_ret`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_sig_product__max_up_ret__max_down_ret` | `sig_product` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | `rel_diff` | a=`max_down_ret`, b=`h2_l2_pullback_continuation` |
| `combo_sig_product__net_volume_flow__shaved_bar_trend_conviction` | `sig_product` | a=`net_volume_flow`, b=`shaved_bar_trend_conviction` |
| `combo_mean__bar_body_rng_0__shaved_bar_trend_conviction` | `mean` | a=`bar_body_rng_0`, b=`shaved_bar_trend_conviction` |
| `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` | `mean` | a=`trend_bar_close_consistency`, b=`vwap_close_divergence_trend` |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | `mean` | a=`close_vs_open_range`, b=`vwap_close_divergence_trend` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | `diff` | a=`max_down_ret`, b=`h2_l2_pullback_continuation` |
| `combo_rank_max__max_down_ret__vwap_close_divergence_trend` | `rank_max` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_max__first_bar_return__bar_body_rng_0` | `max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_max__first_bar_return__shaved_bar_trend_conviction` | `max` | a=`first_bar_return`, b=`shaved_bar_trend_conviction` |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | `max` | a=`star50_limit_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__rsi_opening__h2_l2_pullback_continuation` | `sig_product` | a=`rsi_opening`, b=`h2_l2_pullback_continuation` |
| `combo_ratio__bar_ret_0__net_volume_flow` | `ratio` | a=`bar_ret_0`, b=`net_volume_flow` |
| `combo_diff__net_volume_flow__shaved_bar_trend_conviction` | `diff` | a=`net_volume_flow`, b=`shaved_bar_trend_conviction` |
| `combo_sig_product__max_down_ret__h2_l2_pullback_continuation` | `sig_product` | a=`max_down_ret`, b=`h2_l2_pullback_continuation` |
| `combo_sig_product__early_order_flow_imbalance__bar_body_rng_0` | `sig_product` | a=`early_order_flow_imbalance`, b=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | `tri_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_trend` |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, cond=`gap_pct` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | `min` | a=`star50_limit_proximity_early`, b=`volume_price_confirmation` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_mean` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_min` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`bar_ret_0` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_min__first_bar_return__limit_down_proximity_early` | `min` | a=`first_bar_return`, b=`limit_down_proximity_early` |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | `clamp_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_price_confirmation` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | `ifelse` | a=`max_up_ret`, b=`star50_limit_proximity_early`, cond=`gap_pct` |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_z_sum__max_up_ret__gap_pct` | `z_sum` | a=`max_up_ret`, b=`gap_pct` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | `rel_diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_max__rbreaker_sell_setup_proximity_early__gap_pct` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | `ifelse` | a=`max_up_ret`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_max__max_up_ret__volume_price_confirmation` | `max` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`demark_setup_reversal_early` |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`bar_body_rng_0`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | `rank_min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_diff__max_up_ret__keltner_squeeze_width` | `diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`yesterday_early_trend`, cond=`gap_pct` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__star50_limit_proximity_early` | `ifelse` | a=`rbreaker_sell_setup_proximity_early`, b=`star50_limit_proximity_early`, cond=`gap_pct` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_trend`, cond=`gap_pct` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | `ifelse` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`gap_pct` |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | `rel_diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev` | `ifelse` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | `rank_max` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__first_bar_return` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`first_bar_return`, cond=`gap_pct` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | `rank_max` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | `ifelse` | a=`max_up_ret`, b=`bar_ret_0`, cond=`gap_pct` |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | `mean` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`gap_pct` |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | `rank_max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
