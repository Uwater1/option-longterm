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
| 300ETF | single | 1,584 | 522 | 341 | 277 | 272 | 219 | 218 | 218 | 92 | 77 | 29 | `[9, 7, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (29 clusters)]` |
| 300ETF | long | 579 | 40 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 586 | 93 | 26 | 26 | 5 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | single | 1,244 | 391 | 339 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | long | 361 | 46 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | short | 317 | 39 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 3,100 | 1,382 | 1,164 | 1,030 | 1,023 | 879 | 866 | 866 | 260 | 197 | 76 | `[12, 9, 9, 8, 7, 6, 6, 6, 5, 5, 5, 4, ... (76 clusters)]` |
| 500ETF | long | 1,360 | 108 | 62 | 62 | 29 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | short | 426 | 54 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | single | 1,910 | 747 | 439 | 411 | 409 | 264 | 264 | 264 | 119 | 96 | 42 | `[5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` |
| 159915ETF | long | 1,121 | 108 | 48 | 48 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | short | 302 | 47 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 77 | 29 | `[9, 7, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (29 clusters)]` | +0.1235 | [+0.0812, +0.1656] | +0.2214 | [+0.0990, +0.3189] | +0.8667 | 5.51% | 1.4313 | 3.91% | 1.0288 | 1.9062 | 5.30% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 197 | 76 | `[12, 9, 9, 8, 7, 6, 6, 6, 5, 5, 5, 4, ... (76 clusters)]` | +0.1817 | [+0.1400, +0.2260] | +0.2863 | [+0.1910, +0.3761] | +0.9030 | 8.27% | 1.7518 | 6.65% | 1.4240 | 2.6259 | 3.82% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 96 | 42 | `[5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` | +0.1647 | [+0.1192, +0.2084] | +0.2603 | [+0.1801, +0.3507] | +0.9394 | 8.38% | 1.5965 | 6.78% | 1.3040 | 2.0658 | 8.55% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 77 | 29 | `[9, 7, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (29 clusters)]` | +0.0761* | [-0.0002, +0.1533] | +0.1565* | [-0.0187, +0.3202] | +0.7455 | 3.42% | 0.9983 | 1.87% | 0.5514 | 1.0764 | 3.20% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 197 | 76 | `[12, 9, 9, 8, 7, 6, 6, 6, 5, 5, 5, 4, ... (76 clusters)]` | +0.1118 | [+0.0357, +0.1821] | +0.1046* | [-0.0368, +0.2437] | +0.8788 | 4.14% | 0.9430 | 2.67% | 0.6120 | 1.1088 | 4.33% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 96 | 42 | `[5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` | +0.1433 | [+0.0613, +0.2117] | +0.2815 | [+0.1145, +0.4531] | +0.6364 | 10.64% | 1.6041 | 9.24% | 1.4090 | 3.8768 | 5.91% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1225 | +0.2852 | +0.2860 | 0.0000 | +0.7955 | +0.7966 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 21 | +1 | +0.1187 | +0.2800 | +0.2807 | 0.0000 | +0.7370 | +0.7191 | 0.862 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1188 | +0.2764 | +0.2775 | 0.0000 | +0.8678 | +0.8074 | 0.881 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 3 | +1 | +0.1156 | +0.2691 | +0.2697 | 0.0000 | +0.5471 | +0.7072 | 0.912 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 21 | +1 | +0.1193 | +0.2664 | +0.2674 | 0.0000 | +0.7162 | +0.7524 | 0.945 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 13 | +1 | +0.1119 | +0.2634 | +0.2636 | 0.0000 | +0.6357 | +0.7155 | 0.822 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 21 | +1 | +0.1132 | +0.2593 | +0.2602 | 0.0000 | +0.6700 | +0.7042 | 0.867 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 17 | +1 | +0.1197 | +0.2426 | +0.2433 | 0.0000 | +0.5789 | +0.7129 | 1.000 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 9 | +1 | +0.0941 | +0.2409 | +0.2417 | 0.0000 | +0.5785 | +0.7062 | 0.768 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0967 | +0.2335 | +0.2348 | 0.0000 | +0.5436 | +0.7016 | 0.877 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1165 | +0.2329 | +0.2342 | 0.0000 | +0.7329 | +0.7678 | 0.898 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 26 | +1 | +0.0927 | +0.2276 | +0.2285 | 0.0000 | +0.5897 | +0.7088 | 0.888 |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1111 | +0.2261 | +0.2276 | 0.0000 | +0.7574 | +0.7643 | 0.948 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 25 | +1 | +0.0872 | +0.2244 | +0.2251 | 0.0000 | +0.7215 | +0.7571 | 0.956 |
| `rbreaker_sell_setup_proximity_early` | Cluster 12 | +1 | +0.0965 | +0.2243 | +0.2248 | 0.0000 | +0.5652 | +0.7360 | 0.818 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 19 | +1 | +0.1235 | +0.2218 | +0.2227 | 0.0000 | +0.6181 | +0.7427 | 0.941 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 18 | +1 | +0.0995 | +0.2197 | +0.2208 | 0.0000 | +0.5241 | +0.6769 | 0.903 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 7 | +1 | +0.0912 | +0.2181 | +0.2193 | 0.0000 | +0.5315 | +0.6533 | 0.944 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 25 | +1 | +0.0811 | +0.2172 | +0.2175 | 0.0000 | +0.7860 | +0.7750 | 1.000 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 20 | +1 | +0.1074 | +0.2134 | +0.2144 | 0.0000 | +0.6836 | +0.7191 | 0.935 |
| `combo_tri_mean__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 9 | +1 | +0.0980 | +0.2134 | +0.2142 | 0.0000 | +0.5718 | +0.7155 | 0.949 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0859 | +0.2129 | +0.2140 | 0.0000 | +0.6572 | +0.7483 | 0.873 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 17 | +1 | +0.1222 | +0.2128 | +0.2133 | 0.0000 | +0.5504 | +0.7062 | 0.964 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0898 | +0.2103 | +0.2113 | 0.0000 | +0.5473 | +0.7083 | 0.943 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 15 | +1 | +0.0935 | +0.2101 | +0.2106 | 0.0000 | +0.6761 | +0.7432 | 0.904 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 15 | +1 | +0.0890 | +0.2083 | +0.2087 | 0.0000 | +0.5712 | +0.6918 | 0.873 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.1131 | +0.2066 | +0.2074 | 0.0000 | +0.6498 | +0.7088 | 0.934 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 7 | +1 | +0.0893 | +0.2054 | +0.2064 | 0.0000 | +0.3937 | +0.6636 | 0.938 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 1 | +1 | +0.0947 | +0.2018 | +0.2028 | 0.0000 | +0.4961 | +0.6831 | 0.973 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 27 | +1 | +0.0963 | +0.2000 | +0.2009 | 0.0002 | +0.5073 | +0.6882 | 0.923 |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Cluster 15 | +1 | +0.0914 | +0.1995 | +0.2002 | 0.0002 | +0.5245 | +0.7103 | 0.943 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 24 | +1 | +0.0795 | +0.1991 | +0.2002 | 0.0002 | +0.6744 | +0.7658 | 0.933 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0908 | +0.1980 | +0.1997 | 0.0002 | +0.4755 | +0.6733 | 0.945 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 17 | +1 | +0.1232 | +0.1957 | +0.1970 | 0.0002 | +0.6911 | +0.7360 | 0.955 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 0 | +1 | +0.0897 | +0.1955 | +0.1964 | 0.0002 | +0.4870 | +0.6733 | 0.938 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 25 | +1 | +0.0754 | +0.1940 | +0.1950 | 0.0002 | +0.7475 | +0.7807 | 0.885 |
| `combo_max__first_bar_return__bar_body_rng_0` | Cluster 27 | +1 | +0.0944 | +0.1938 | +0.1949 | 0.0002 | +0.5724 | +0.7191 | 0.939 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Cluster 4 | +1 | +0.0742 | +0.1929 | +0.1930 | 0.0002 | +0.4284 | +0.6718 | 0.494 |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | Cluster 4 | +1 | +0.0665 | +0.1925 | +0.1927 | 0.0002 | +0.5928 | +0.7401 | 0.610 |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 3 | +1 | +0.1000 | +0.1864 | +0.1881 | 0.0002 | +0.7547 | +0.7535 | 0.891 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Cluster 4 | +1 | +0.0660 | +0.1858 | +0.1864 | 0.0002 | +0.6574 | +0.7488 | 0.795 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 8 | +1 | +0.0872 | +0.1852 | +0.1865 | 0.0002 | +0.5869 | +0.7057 | 0.938 |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Cluster 2 | +1 | +0.0902 | +0.1839 | +0.1847 | 0.0002 | +0.5811 | +0.7026 | 0.936 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 27 | +1 | +0.0917 | +0.1836 | +0.1849 | 0.0002 | +0.5672 | +0.7304 | 0.901 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 5 | +1 | +0.0833 | +0.1830 | +0.1846 | 0.0002 | +0.6883 | +0.7576 | 0.880 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 20 | +1 | +0.0910 | +0.1818 | +0.1831 | 0.0002 | +0.5267 | +0.6780 | 1.000 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 26 | +1 | +0.0828 | +0.1817 | +0.1829 | 0.0002 | +0.4753 | +0.6528 | 0.985 |
| `combo_max__max_up_ret__volume_surge_direction` | Cluster 14 | +1 | +0.0754 | +0.1797 | +0.1806 | 0.0002 | +0.6226 | +0.7504 | 0.884 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 8 | +1 | +0.0866 | +0.1780 | +0.1799 | 0.0002 | +0.4991 | +0.6888 | 0.981 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | Cluster 14 | +1 | +0.0745 | +0.1780 | +0.1791 | 0.0002 | +0.5990 | +0.7314 | 0.899 |
| `combo_rank_min__bar_body_rng_0__volume_surge_direction` | Cluster 27 | +1 | +0.0754 | +0.1769 | +0.1783 | 0.0002 | +0.5397 | +0.6923 | 0.886 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0893 | +0.1747 | +0.1759 | 0.0004 | +0.4218 | +0.6651 | 0.933 |
| `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` | Cluster 4 | +1 | +0.0619 | +0.1738 | +0.1741 | 0.0004 | +0.4638 | +0.6965 | 1.000 |
| `star50_limit_proximity_early` | Cluster 12 | +1 | +0.0915 | +0.1720 | +0.1727 | 0.0008 | +0.4589 | +0.6954 | 0.945 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 14 | +1 | +0.0868 | +0.1690 | +0.1699 | 0.0010 | +0.6099 | +0.6949 | 0.943 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.1062 | +0.1686 | +0.1706 | 0.0010 | +0.4878 | +0.6615 | 0.917 |
| `max_up_ret` | Cluster 6 | +1 | +0.0767 | +0.1676 | +0.1683 | 0.0010 | +0.3955 | +0.6549 | 0.909 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 16 | +1 | +0.0979 | +0.1676 | +0.1678 | 0.0010 | +0.4518 | +0.6723 | 0.934 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 24 | +1 | +0.0803 | +0.1660 | +0.1672 | 0.0010 | +0.6402 | +0.7191 | 0.879 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 23 | +1 | +0.0777 | +0.1660 | +0.1670 | 0.0010 | +0.6048 | +0.7381 | 0.783 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Cluster 27 | +1 | +0.0928 | +0.1657 | +0.1664 | 0.0010 | +0.4785 | +0.7021 | 1.000 |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 3 | +1 | +0.1032 | +0.1643 | +0.1656 | 0.0010 | +0.6259 | +0.7160 | 0.919 |
| `combo_z_sum__first_bar_return__first_bar_sentiment` | Cluster 27 | +1 | +0.0921 | +0.1635 | +0.1643 | 0.0010 | +0.4150 | +0.6636 | 0.938 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 27 | +1 | +0.0929 | +0.1632 | +0.1640 | 0.0010 | +0.4797 | +0.6564 | 0.962 |
| `combo_rank_max__bar_body_rng_0__volume_surge_direction` | Cluster 27 | +1 | +0.0852 | +0.1619 | +0.1635 | 0.0012 | +0.4940 | +0.6790 | 0.978 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 12 | +1 | +0.0830 | +0.1612 | +0.1619 | 0.0012 | +0.4948 | +0.6949 | 0.802 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Cluster 19 | +1 | +0.1095 | +0.1599 | +0.1610 | 0.0012 | +0.4455 | +0.6769 | 0.919 |
| `combo_rank_min__first_bar_return__volume_weighted_price_position` | Cluster 0 | +1 | +0.0878 | +0.1583 | +0.1593 | 0.0014 | +0.4863 | +0.6965 | 0.934 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 10 | +1 | +0.0909 | +0.1527 | +0.1532 | 0.0020 | +0.4236 | +0.6610 | 0.909 |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | Cluster 27 | +1 | +0.0901 | +0.1492 | +0.1501 | 0.0026 | +0.5479 | +0.7016 | 0.878 |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | Cluster 2 | +1 | +0.0848 | +0.1476 | +0.1484 | 0.0028 | +0.6663 | +0.7149 | 0.972 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Cluster 22 | +1 | +0.0894 | +0.1467 | +0.1473 | 0.0036 | +0.4503 | +0.6646 | 0.789 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 13 | +1 | +0.0767 | +0.1416 | +0.1421 | 0.0050 | +0.5120 | +0.7088 | 0.880 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 13 | +1 | +0.0757 | +0.1356 | +0.1361 | 0.0080 | +0.4172 | +0.6888 | 0.813 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Cluster 28 | +1 | +0.0680 | +0.1333 | +0.1336 | 0.0092 | +0.5209 | +0.7216 | 0.806 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 22 | +1 | +0.0768 | +0.1267 | +0.1277 | 0.0122 | +0.5022 | +0.6805 | 0.927 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 22 | +1 | +0.0890 | +0.1262 | +0.1270 | 0.0132 | +0.4936 | +0.6841 | 0.947 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 30 | +1 | +0.1763 | +0.3308 | +0.3324 | 0.0000 | +1.1222 | +0.8567 | 0.000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 28 | +1 | +0.1603 | +0.3202 | +0.3220 | 0.0000 | +0.8630 | +0.7925 | 0.934 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 30 | +1 | +0.1776 | +0.3148 | +0.3165 | 0.0000 | +1.1131 | +0.8377 | 0.854 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 28 | +1 | +0.1544 | +0.3075 | +0.3095 | 0.0000 | +0.9528 | +0.8197 | 0.950 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 26 | +1 | +0.1634 | +0.3074 | +0.3082 | 0.0000 | +0.9093 | +0.7966 | 0.824 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 7 | +1 | +0.1240 | +0.3062 | +0.3081 | 0.0000 | +0.7219 | +0.7560 | 0.923 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 27 | +1 | +0.1605 | +0.3026 | +0.3035 | 0.0000 | +1.1008 | +0.8279 | 0.905 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 12 | +1 | +0.1641 | +0.3025 | +0.3043 | 0.0000 | +0.7337 | +0.7807 | 0.765 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 58 | +1 | +0.1702 | +0.2962 | +0.2969 | 0.0000 | +0.8348 | +0.7920 | 0.734 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1310 | +0.2956 | +0.2974 | 0.0000 | +0.7405 | +0.7406 | 0.936 |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | Cluster 13 | +1 | +0.1817 | +0.2952 | +0.2964 | 0.0000 | +0.8010 | +0.7807 | 0.986 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 47 | +1 | +0.2012 | +0.2950 | +0.2963 | 0.0000 | +0.9487 | +0.7925 | 0.920 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 29 | +1 | +0.1531 | +0.2943 | +0.2960 | 0.0000 | +0.9313 | +0.8264 | 0.974 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 35 | +1 | +0.1685 | +0.2912 | +0.2924 | 0.0000 | +0.8171 | +0.7771 | 0.813 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 54 | +1 | +0.1713 | +0.2906 | +0.2921 | 0.0000 | +0.9437 | +0.8095 | 0.986 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 35 | +1 | +0.1711 | +0.2877 | +0.2893 | 0.0000 | +0.6299 | +0.7355 | 0.834 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 12 | +1 | +0.1629 | +0.2850 | +0.2868 | 0.0000 | +0.9770 | +0.8356 | 0.862 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 53 | +1 | +0.1672 | +0.2845 | +0.2863 | 0.0000 | +1.0054 | +0.8444 | 0.910 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1317 | +0.2835 | +0.2853 | 0.0000 | +0.7668 | +0.7576 | 0.855 |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 56 | +1 | +0.1511 | +0.2821 | +0.2838 | 0.0000 | +0.9539 | +0.8295 | 0.962 |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | Cluster 52 | +1 | +0.1514 | +0.2815 | +0.2825 | 0.0000 | +0.9732 | +0.8254 | 0.929 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 12 | +1 | +0.1590 | +0.2814 | +0.2830 | 0.0000 | +0.9932 | +0.8356 | 0.901 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 9 | +1 | +0.1410 | +0.2807 | +0.2818 | 0.0000 | +0.7409 | +0.7463 | 0.944 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | Cluster 54 | +1 | +0.1582 | +0.2798 | +0.2811 | 0.0000 | +0.8260 | +0.8197 | 0.989 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 55 | +1 | +0.1688 | +0.2797 | +0.2815 | 0.0000 | +1.1388 | +0.8670 | 0.937 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 35 | +1 | +0.1697 | +0.2790 | +0.2806 | 0.0000 | +0.6106 | +0.7155 | 1.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 2 | +1 | +0.1677 | +0.2765 | +0.2774 | 0.0000 | +0.7535 | +0.7838 | 0.919 |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 3 | +1 | +0.1136 | +0.2763 | +0.2769 | 0.0000 | +0.6910 | +0.7643 | 0.947 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Cluster 13 | +1 | +0.1754 | +0.2762 | +0.2774 | 0.0000 | +0.7731 | +0.7668 | 0.970 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 27 | +1 | +0.1720 | +0.2752 | +0.2762 | 0.0000 | +0.7229 | +0.7345 | 0.885 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 12 | +1 | +0.1585 | +0.2737 | +0.2758 | 0.0000 | +0.8841 | +0.7920 | 0.895 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 5 | +1 | +0.1207 | +0.2737 | +0.2753 | 0.0000 | +0.6781 | +0.7401 | 0.945 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Cluster 35 | +1 | +0.1447 | +0.2736 | +0.2754 | 0.0000 | +0.5541 | +0.6703 | 0.945 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 3 | +1 | +0.1202 | +0.2722 | +0.2729 | 0.0000 | +0.7559 | +0.7776 | 0.947 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Cluster 32 | +1 | +0.1484 | +0.2722 | +0.2732 | 0.0000 | +0.7569 | +0.7494 | 0.629 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 9 | +1 | +0.1429 | +0.2720 | +0.2731 | 0.0000 | +0.8170 | +0.7797 | 0.959 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 2 | +1 | +0.1602 | +0.2716 | +0.2730 | 0.0000 | +0.6443 | +0.7339 | 0.904 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 26 | +1 | +0.1283 | +0.2707 | +0.2716 | 0.0000 | +0.5943 | +0.7170 | 0.925 |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | Cluster 35 | +1 | +0.1624 | +0.2705 | +0.2722 | 0.0000 | +0.7158 | +0.7571 | 0.967 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | Cluster 26 | +1 | +0.1477 | +0.2695 | +0.2707 | 0.0000 | +0.8145 | +0.7730 | 0.944 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 51 | +1 | +0.1643 | +0.2677 | +0.2692 | 0.0000 | +0.7719 | +0.7756 | 0.824 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 5 | +1 | +0.1191 | +0.2676 | +0.2691 | 0.0000 | +0.6455 | +0.7119 | 0.915 |
| `combo_rank_min__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 11 | +1 | +0.1041 | +0.2661 | +0.2673 | 0.0000 | +0.6435 | +0.7206 | 0.948 |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | Cluster 49 | +1 | +0.1437 | +0.2649 | +0.2672 | 0.0000 | +0.7841 | +0.7771 | 0.948 |
| `combo_rank_min__close_vs_open_range__first_bar_sentiment` | Cluster 58 | +1 | +0.1391 | +0.2639 | +0.2648 | 0.0000 | +0.7718 | +0.7946 | 0.874 |
| `opening_drive_thrust_ratio` | Cluster 68 | +1 | +0.1682 | +0.2632 | +0.2649 | 0.0000 | +0.7902 | +0.8084 | 0.931 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 56 | +1 | +0.1535 | +0.2626 | +0.2641 | 0.0000 | +0.8366 | +0.7961 | 0.939 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 72 | +1 | +0.1140 | +0.2623 | +0.2641 | 0.0000 | +0.7439 | +0.7689 | 0.991 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 12 | +1 | +0.1691 | +0.2621 | +0.2638 | 0.0000 | +0.8295 | +0.8007 | 0.940 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1804 | +0.2620 | +0.2630 | 0.0000 | +0.9544 | +0.8038 | 0.913 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 26 | +1 | +0.1598 | +0.2613 | +0.2624 | 0.0000 | +0.6663 | +0.7108 | 0.960 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Cluster 8 | +1 | +0.1405 | +0.2602 | +0.2611 | 0.0000 | +0.7573 | +0.7524 | 0.894 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 31 | +1 | +0.1782 | +0.2597 | +0.2611 | 0.0000 | +0.7347 | +0.7417 | 0.968 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 53 | +1 | +0.1490 | +0.2589 | +0.2608 | 0.0000 | +0.7877 | +0.7653 | 0.965 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 67 | +1 | +0.1418 | +0.2581 | +0.2597 | 0.0000 | +0.7611 | +0.7745 | 0.875 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1842 | +0.2575 | +0.2589 | 0.0000 | +0.8809 | +0.8043 | 0.941 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Cluster 2 | +1 | +0.1243 | +0.2568 | +0.2574 | 0.0000 | +0.6319 | +0.7483 | 0.921 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | Cluster 74 | +1 | +0.1446 | +0.2567 | +0.2569 | 0.0000 | +0.6597 | +0.7339 | 0.796 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Cluster 13 | +1 | +0.1709 | +0.2551 | +0.2562 | 0.0000 | +0.9313 | +0.7802 | 0.898 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Cluster 32 | +1 | +0.1546 | +0.2543 | +0.2549 | 0.0000 | +0.5488 | +0.7026 | 0.960 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 57 | +1 | +0.1580 | +0.2540 | +0.2552 | 0.0000 | +0.6084 | +0.7242 | 0.921 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 50 | +1 | +0.1799 | +0.2530 | +0.2544 | 0.0000 | +0.8288 | +0.7699 | 0.916 |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 57 | +1 | +0.1440 | +0.2526 | +0.2535 | 0.0000 | +0.6405 | +0.7514 | 0.976 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Cluster 13 | +1 | +0.1749 | +0.2498 | +0.2510 | 0.0000 | +1.0192 | +0.7910 | 0.933 |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | Cluster 41 | +1 | +0.1423 | +0.2497 | +0.2512 | 0.0000 | +0.5443 | +0.6975 | 0.908 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 57 | +1 | +0.1626 | +0.2494 | +0.2513 | 0.0000 | +0.6742 | +0.7483 | 0.936 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 12 | +1 | +0.1619 | +0.2487 | +0.2510 | 0.0000 | +0.9078 | +0.7802 | 0.905 |
| `net_volume_flow` | Cluster 72 | +1 | +0.1188 | +0.2475 | +0.2493 | 0.0000 | +0.7388 | +0.7756 | 0.932 |
| `combo_rel_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 57 | +1 | +0.1417 | +0.2464 | +0.2471 | 0.0000 | +0.6409 | +0.7565 | 0.924 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 4 | +1 | +0.1258 | +0.2462 | +0.2482 | 0.0000 | +0.7698 | +0.7514 | 0.872 |
| `combo_max__max_up_ret__early_body_momentum` | Cluster 2 | +1 | +0.1440 | +0.2456 | +0.2473 | 0.0000 | +0.8651 | +0.8017 | 0.956 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 4 | +1 | +0.1269 | +0.2448 | +0.2467 | 0.0000 | +0.7120 | +0.7350 | 0.798 |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | Cluster 72 | +1 | +0.1116 | +0.2448 | +0.2463 | 0.0000 | +0.4780 | +0.7011 | 0.957 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 47 | +1 | +0.1820 | +0.2437 | +0.2446 | 0.0000 | +0.6067 | +0.7211 | 0.870 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 13 | +1 | +0.1750 | +0.2436 | +0.2448 | 0.0000 | +0.9014 | +0.7761 | 0.974 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 50 | +1 | +0.1796 | +0.2426 | +0.2440 | 0.0000 | +0.6256 | +0.7447 | 0.914 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Cluster 72 | +1 | +0.1097 | +0.2423 | +0.2441 | 0.0000 | +0.6350 | +0.7458 | 0.956 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 32 | +1 | +0.1511 | +0.2415 | +0.2427 | 0.0000 | +0.5920 | +0.7103 | 0.920 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Cluster 2 | +1 | +0.1501 | +0.2412 | +0.2430 | 0.0000 | +0.8954 | +0.7966 | 0.976 |
| `combo_min__net_volume_flow__bar_ret_0` | Cluster 43 | +1 | +0.1279 | +0.2395 | +0.2414 | 0.0000 | +0.7200 | +0.7643 | 1.000 |
| `combo_mean__net_volume_flow__close_vs_open_range` | Cluster 72 | +1 | +0.1170 | +0.2389 | +0.2406 | 0.0000 | +0.5893 | +0.7072 | 0.932 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 49 | +1 | +0.1351 | +0.2378 | +0.2396 | 0.0000 | +0.7319 | +0.7709 | 0.929 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | Cluster 37 | +1 | +0.1285 | +0.2378 | +0.2393 | 0.0000 | +0.5810 | +0.7524 | 0.986 |
| `combo_min__max_up_ret__close_vs_open_range` | Cluster 2 | +1 | +0.1283 | +0.2377 | +0.2385 | 0.0000 | +0.7087 | +0.7735 | 0.887 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 67 | +1 | +0.1401 | +0.2373 | +0.2394 | 0.0000 | +0.6639 | +0.7278 | 0.848 |
| `combo_mean__max_up_ret__close_vs_open_range` | Cluster 2 | +1 | +0.1503 | +0.2364 | +0.2379 | 0.0000 | +0.7792 | +0.7740 | 0.885 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Cluster 1 | +1 | +0.1468 | +0.2363 | +0.2374 | 0.0000 | +0.8415 | +0.7843 | 0.909 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 67 | +1 | +0.1373 | +0.2358 | +0.2368 | 0.0000 | +0.5414 | +0.6970 | 0.926 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure` | Cluster 34 | +1 | +0.0825 | +0.2357 | +0.2361 | 0.0000 | +0.7815 | +0.7766 | 0.782 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 68 | +1 | +0.1595 | +0.2337 | +0.2357 | 0.0000 | +0.5864 | +0.7581 | 0.891 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 48 | +1 | +0.1626 | +0.2336 | +0.2356 | 0.0000 | +0.5429 | +0.7370 | 0.842 |
| `combo_min__max_up_ret__high_low_sequence_momentum` | Cluster 2 | +1 | +0.1291 | +0.2334 | +0.2342 | 0.0000 | +0.6834 | +0.7442 | 0.999 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | Cluster 12 | +1 | +0.1781 | +0.2334 | +0.2353 | 0.0000 | +0.6913 | +0.7319 | 0.943 |
| `combo_max__max_up_ret__close_vs_open_range` | Cluster 2 | +1 | +0.1616 | +0.2333 | +0.2353 | 0.0000 | +0.7526 | +0.7391 | 0.937 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | Cluster 37 | +1 | +0.1379 | +0.2333 | +0.2348 | 0.0000 | +0.5756 | +0.7072 | 0.905 |
| `combo_mean__net_volume_flow__first_bar_return` | Cluster 36 | +1 | +0.1453 | +0.2322 | +0.2340 | 0.0000 | +0.6074 | +0.7252 | 0.971 |
| `max_up_ret` | Cluster 48 | +1 | +0.1619 | +0.2317 | +0.2328 | 0.0000 | +0.6107 | +0.7370 | 0.900 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 48 | +1 | +0.1639 | +0.2309 | +0.2323 | 0.0000 | +0.7465 | +0.7756 | 0.867 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Cluster 73 | +1 | +0.1089 | +0.2306 | +0.2314 | 0.0000 | +0.5900 | +0.7242 | 0.857 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 12 | +1 | +0.1764 | +0.2301 | +0.2316 | 0.0000 | +0.7031 | +0.7761 | 0.920 |
| `combo_max__first_bar_sentiment__early_body_momentum` | Cluster 41 | +1 | +0.1304 | +0.2299 | +0.2313 | 0.0000 | +0.6076 | +0.7334 | 0.944 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Cluster 65 | +1 | +0.1606 | +0.2295 | +0.2317 | 0.0000 | +0.6319 | +0.7103 | 0.895 |
| `combo_mean__max_up_ret__bar_ret_0` | Cluster 48 | +1 | +0.1709 | +0.2289 | +0.2302 | 0.0000 | +0.6458 | +0.7206 | 1.000 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | Cluster 72 | +1 | +0.1117 | +0.2287 | +0.2301 | 0.0000 | +0.5667 | +0.7334 | 0.996 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Cluster 2 | +1 | +0.1611 | +0.2286 | +0.2307 | 0.0000 | +0.8236 | +0.7781 | 0.947 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 48 | +1 | +0.1639 | +0.2285 | +0.2300 | 0.0000 | +0.7050 | +0.7678 | 1.000 |
| `combo_min__close_vs_open_range__first_bar_return` | Cluster 40 | +1 | +0.1185 | +0.2276 | +0.2295 | 0.0000 | +0.7442 | +0.7524 | 1.000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 24 | +1 | +0.1441 | +0.2275 | +0.2284 | 0.0000 | +0.5344 | +0.6913 | 0.814 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 73 | +1 | +0.1183 | +0.2274 | +0.2283 | 0.0000 | +0.5771 | +0.6888 | 0.912 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | Cluster 63 | +1 | +0.1362 | +0.2270 | +0.2286 | 0.0000 | +0.5799 | +0.7108 | 0.895 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Cluster 52 | +1 | +0.1589 | +0.2267 | +0.2277 | 0.0000 | +0.7850 | +0.7899 | 0.939 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 47 | +1 | +0.1760 | +0.2247 | +0.2256 | 0.0000 | +0.5212 | +0.7021 | 0.947 |
| `combo_rank_min__close_vs_open_range__first_bar_return` | Cluster 40 | +1 | +0.1185 | +0.2241 | +0.2260 | 0.0000 | +0.7916 | +0.7684 | 0.953 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 69 | +1 | +0.1489 | +0.2233 | +0.2239 | 0.0000 | +0.7037 | +0.7437 | 0.753 |
| `trend_bar_close_consistency` | Cluster 46 | +1 | +0.0765 | +0.2230 | +0.2235 | 0.0000 | +0.4448 | +0.6918 | 0.910 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | Cluster 72 | +1 | +0.1076 | +0.2226 | +0.2243 | 0.0000 | +0.5686 | +0.7206 | 0.922 |
| `combo_mean__bar_ret_0__max_down_ret` | Cluster 61 | +1 | +0.1425 | +0.2220 | +0.2243 | 0.0000 | +0.5490 | +0.6518 | 1.000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 68 | +1 | +0.1590 | +0.2210 | +0.2237 | 0.0000 | +0.6806 | +0.7427 | 0.949 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 67 | +1 | +0.1422 | +0.2208 | +0.2227 | 0.0000 | +0.5242 | +0.7124 | 0.937 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Cluster 42 | +1 | +0.1480 | +0.2208 | +0.2221 | 0.0000 | +0.7142 | +0.7401 | 0.906 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 10 | +1 | +0.1305 | +0.2203 | +0.2218 | 0.0000 | +0.5629 | +0.6795 | 0.933 |
| `combo_mean__max_up_ret__trend_day_regime_conviction` | Cluster 2 | +1 | +0.1464 | +0.2191 | +0.2206 | 0.0000 | +0.6153 | +0.6939 | 0.999 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 57 | +1 | +0.1542 | +0.2176 | +0.2187 | 0.0000 | +0.5720 | +0.7175 | 0.970 |
| `combo_rank_min__early_body_momentum__bar_ret_0` | Cluster 43 | +1 | +0.1134 | +0.2173 | +0.2189 | 0.0000 | +0.5864 | +0.7072 | 0.945 |
| `combo_rank_max__close_vs_open_range__first_bar_return` | Cluster 39 | +1 | +0.1631 | +0.2155 | +0.2168 | 0.0000 | +0.7266 | +0.7704 | 0.938 |
| `combo_max__close_vs_open_range__first_bar_return` | Cluster 39 | +1 | +0.1634 | +0.2151 | +0.2165 | 0.0000 | +0.7342 | +0.7766 | 1.000 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 24 | +1 | +0.1328 | +0.2150 | +0.2161 | 0.0000 | +0.4780 | +0.6687 | 0.887 |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | Cluster 46 | +1 | +0.1012 | +0.2149 | +0.2163 | 0.0000 | +0.4602 | +0.6959 | 0.937 |
| `combo_mean__close_vs_open_range__first_bar_return` | Cluster 36 | +1 | +0.1498 | +0.2132 | +0.2150 | 0.0000 | +0.7345 | +0.7766 | 1.000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 47 | +1 | +0.1795 | +0.2126 | +0.2135 | 0.0000 | +0.6781 | +0.7406 | 0.889 |
| `combo_mean__net_volume_flow__max_down_ret` | Cluster 20 | +1 | +0.1285 | +0.2123 | +0.2142 | 0.0000 | +0.6531 | +0.7360 | 0.956 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Cluster 0 | +1 | +0.1323 | +0.2100 | +0.2111 | 0.0000 | +0.4841 | +0.7026 | 0.836 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 68 | +1 | +0.1611 | +0.2099 | +0.2116 | 0.0000 | +0.6553 | +0.7678 | 0.967 |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Cluster 73 | +1 | +0.1057 | +0.2093 | +0.2107 | 0.0000 | +0.5429 | +0.6569 | 0.940 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 68 | +1 | +0.1453 | +0.2093 | +0.2107 | 0.0000 | +0.6419 | +0.7720 | 0.889 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 47 | +1 | +0.1705 | +0.2091 | +0.2099 | 0.0000 | +0.4839 | +0.7129 | 0.953 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Cluster 74 | +1 | +0.1280 | +0.2083 | +0.2087 | 0.0000 | +0.5525 | +0.7108 | 0.923 |
| `combo_rank_min__close_vs_open_range__max_down_ret` | Cluster 16 | +1 | +0.1278 | +0.2083 | +0.2107 | 0.0000 | +0.5384 | +0.7031 | 0.954 |
| `combo_max__first_bar_return__max_down_ret` | Cluster 65 | +1 | +0.1553 | +0.2082 | +0.2102 | 0.0000 | +0.6162 | +0.7093 | 1.000 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Cluster 66 | +1 | +0.1276 | +0.2082 | +0.2105 | 0.0000 | +0.5260 | +0.6882 | 0.859 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 75 | +1 | +0.1405 | +0.2082 | +0.2096 | 0.0000 | +0.5216 | +0.6821 | 0.872 |
| `combo_rank_min__early_body_momentum__max_down_ret` | Cluster 18 | +1 | +0.1179 | +0.2081 | +0.2106 | 0.0000 | +0.5658 | +0.7108 | 0.947 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Cluster 38 | +1 | +0.1361 | +0.2076 | +0.2092 | 0.0000 | +0.6319 | +0.7427 | 0.928 |
| `combo_min__early_body_momentum__max_down_ret` | Cluster 18 | +1 | +0.1145 | +0.2071 | +0.2094 | 0.0000 | +0.5983 | +0.7001 | 0.935 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 2 | +1 | +0.1248 | +0.2068 | +0.2080 | 0.0000 | +0.6500 | +0.7165 | 0.941 |
| `combo_max__early_body_momentum__first_bar_return` | Cluster 42 | +1 | +0.1413 | +0.2063 | +0.2076 | 0.0000 | +0.6204 | +0.7001 | 0.909 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 71 | +1 | +0.1657 | +0.2060 | +0.2069 | 0.0000 | +0.6661 | +0.7678 | 0.930 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 71 | +1 | +0.1609 | +0.2059 | +0.2067 | 0.0000 | +0.6144 | +0.7232 | 0.820 |
| `combo_max__close_vs_open_range__early_body_momentum` | Cluster 46 | +1 | +0.1020 | +0.2053 | +0.2064 | 0.0000 | +0.5463 | +0.7232 | 0.945 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 71 | +1 | +0.1578 | +0.2048 | +0.2053 | 0.0000 | +0.6479 | +0.7170 | 0.846 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 48 | +1 | +0.1641 | +0.2045 | +0.2055 | 0.0000 | +0.4603 | +0.6703 | 0.924 |
| `combo_min__close_vs_open_range__max_down_ret` | Cluster 16 | +1 | +0.1254 | +0.2037 | +0.2059 | 0.0000 | +0.5772 | +0.7052 | 0.946 |
| `combo_rank_max__early_body_momentum__max_down_ret` | Cluster 19 | +1 | +0.1203 | +0.2028 | +0.2041 | 0.0000 | +0.5737 | +0.7165 | 0.972 |
| `early_order_flow_imbalance` | Cluster 45 | +1 | +0.0858 | +0.2021 | +0.2032 | 0.0000 | +0.4667 | +0.6846 | 0.844 |
| `combo_min__first_bar_return__max_down_ret` | Cluster 66 | +1 | +0.1327 | +0.2016 | +0.2038 | 0.0000 | +0.5563 | +0.6975 | 1.000 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | Cluster 25 | +1 | +0.1432 | +0.2007 | +0.2015 | 0.0000 | +0.5244 | +0.6821 | 0.921 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Cluster 33 | +1 | +0.1369 | +0.2006 | +0.2008 | 0.0000 | +0.3657 | +0.6697 | 1.000 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Cluster 33 | +1 | +0.1322 | +0.2005 | +0.2021 | 0.0000 | +0.4868 | +0.6569 | 0.834 |
| `combo_rank_max__close_vs_open_range__early_body_momentum` | Cluster 46 | +1 | +0.1067 | +0.2002 | +0.2012 | 0.0000 | +0.5342 | +0.7278 | 0.945 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 23 | +1 | +0.1589 | +0.1973 | +0.1988 | 0.0000 | +0.5426 | +0.6852 | 0.967 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 12 | +1 | +0.1788 | +0.1971 | +0.1984 | 0.0000 | +0.5185 | +0.7334 | 1.000 |
| `combo_max__volatility_expansion_trend_vector__bar_ret_0` | Cluster 39 | +1 | +0.1567 | +0.1960 | +0.1975 | 0.0000 | +0.5633 | +0.7211 | 0.944 |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 47 | +1 | +0.1649 | +0.1956 | +0.1963 | 0.0000 | +0.4333 | +0.6826 | 0.946 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 67 | +1 | +0.1530 | +0.1937 | +0.1948 | 0.0000 | +0.4332 | +0.6703 | 0.853 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 59 | +1 | +0.1672 | +0.1937 | +0.1948 | 0.0000 | +0.7073 | +0.7622 | 0.931 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | Cluster 44 | +1 | +0.0947 | +0.1933 | +0.1943 | 0.0000 | +0.5294 | +0.6662 | 0.706 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 21 | +1 | +0.1280 | +0.1931 | +0.1932 | 0.0000 | +0.5135 | +0.6821 | 0.947 |
| `combo_mean__first_bar_sentiment__bar_ret_0` | Cluster 64 | +1 | +0.1457 | +0.1931 | +0.1945 | 0.0000 | +0.6014 | +0.7180 | 0.962 |
| `first_bar_return` | Cluster 64 | +1 | +0.1457 | +0.1931 | +0.1945 | 0.0000 | +0.6014 | +0.7180 | 0.948 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Cluster 71 | +1 | +0.1562 | +0.1917 | +0.1925 | 0.0000 | +0.6775 | +0.7144 | 0.954 |
| `combo_mean__close_vs_open_range__max_down_ret` | Cluster 20 | +1 | +0.1278 | +0.1908 | +0.1925 | 0.0000 | +0.4766 | +0.6646 | 0.927 |
| `combo_sig_product__max_up_ret__body_size_progression` | Cluster 69 | +1 | +0.1454 | +0.1907 | +0.1915 | 0.0000 | +0.7799 | +0.7447 | 0.837 |
| `combo_max__net_volume_flow__max_down_ret` | Cluster 19 | +1 | +0.1223 | +0.1903 | +0.1919 | 0.0000 | +0.5420 | +0.7031 | 0.913 |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | Cluster 25 | +1 | +0.1398 | +0.1898 | +0.1908 | 0.0000 | +0.4713 | +0.6954 | 0.939 |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1469 | +0.1867 | +0.1876 | 0.0000 | +0.4895 | +0.6615 | 0.948 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | Cluster 57 | +1 | +0.1484 | +0.1857 | +0.1873 | 0.0000 | +0.6888 | +0.7540 | 1.000 |
| `combo_rank_max__close_vs_open_range__max_down_ret` | Cluster 15 | +1 | +0.1247 | +0.1851 | +0.1867 | 0.0000 | +0.5096 | +0.6995 | 0.947 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Cluster 62 | +1 | +0.1447 | +0.1846 | +0.1865 | 0.0000 | +0.7050 | +0.7550 | 0.909 |
| `combo_min__first_bar_sentiment__max_down_ret` | Cluster 62 | +1 | +0.1437 | +0.1841 | +0.1863 | 0.0000 | +0.5824 | +0.6934 | 0.963 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | Cluster 0 | +1 | +0.1262 | +0.1816 | +0.1828 | 0.0000 | +0.4172 | +0.6662 | 0.970 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | Cluster 23 | +1 | +0.1532 | +0.1800 | +0.1809 | 0.0000 | +0.4993 | +0.6949 | 0.942 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 22 | +1 | +0.1407 | +0.1798 | +0.1805 | 0.0000 | +0.5327 | +0.7155 | 0.945 |
| `combo_max__close_vs_open_range__max_down_ret` | Cluster 15 | +1 | +0.1253 | +0.1777 | +0.1790 | 0.0000 | +0.4249 | +0.6857 | 0.897 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 57 | +1 | +0.1361 | +0.1753 | +0.1762 | 0.0000 | +0.6395 | +0.7422 | 0.872 |
| `max_down_ret` | Cluster 14 | +1 | +0.1248 | +0.1750 | +0.1774 | 0.0000 | +0.5100 | +0.6590 | 0.941 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 70 | +1 | +0.0671 | +0.1728 | +0.1759 | 0.0000 | +0.4477 | +0.6502 | 0.658 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 32 | +1 | +0.1603 | +0.1690 | +0.1706 | 0.0002 | +0.5264 | +0.7201 | 0.787 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Cluster 74 | +1 | +0.1208 | +0.1645 | +0.1654 | 0.0006 | +0.4439 | +0.6754 | 0.916 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 57 | +1 | +0.1556 | +0.1636 | +0.1651 | 0.0006 | +0.6321 | +0.7381 | 0.946 |
| `morning_volume_weighted_momentum` | Cluster 72 | +1 | +0.1104 | +0.1578 | +0.1586 | 0.0014 | +0.4396 | +0.6579 | 0.909 |
| `open_to_current_return` | Cluster 72 | +1 | +0.1142 | +0.1557 | +0.1567 | 0.0018 | +0.4824 | +0.6954 | 1.000 |
| `vwap_trend_channel_slope` | Cluster 67 | +1 | +0.0991 | +0.1543 | +0.1549 | 0.0020 | +0.4231 | +0.6564 | 0.816 |
| `combo_ratio__bar_ret_0__net_volume_flow` | Cluster 1 | +1 | +0.1119 | +0.1425 | +0.1442 | 0.0062 | +0.3291 | +0.6523 | 0.101 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 33 | +1 | +0.1424 | +0.1417 | +0.1413 | 0.0064 | +0.3671 | +0.6662 | 0.622 |
| `combo_sig_product__high_low_sequence_momentum__max_down_ret` | Cluster 17 | +1 | +0.1200 | +0.1380 | +0.1398 | 0.0082 | +0.4859 | +0.6929 | 0.872 |
| `or_fill_ratio` | Cluster 46 | +1 | +0.0805 | +0.1332 | +0.1342 | 0.0100 | +0.4954 | +0.7180 | 0.935 |
| `bar_body_rng_0` | Cluster 60 | +1 | +0.1360 | +0.1298 | +0.1322 | 0.0118 | +0.5355 | +0.6754 | 0.913 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 22 | +1 | +0.1376 | +0.3068 | +0.3083 | 0.0000 | +0.6713 | +0.7483 | 0.000 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1461 | +0.3059 | +0.3073 | 0.0000 | +0.6470 | +0.7437 | 0.929 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 15 | +1 | +0.1569 | +0.2946 | +0.2960 | 0.0000 | +0.7050 | +0.7519 | 0.745 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 8 | +1 | +0.1650 | +0.2842 | +0.2846 | 0.0000 | +0.7080 | +0.7365 | 0.872 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 10 | +1 | +0.1585 | +0.2840 | +0.2852 | 0.0000 | +0.7025 | +0.7632 | 0.949 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Cluster 10 | +1 | +0.1404 | +0.2802 | +0.2815 | 0.0000 | +0.6570 | +0.7478 | 0.944 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 30 | +1 | +0.1504 | +0.2800 | +0.2810 | 0.0000 | +0.6266 | +0.7134 | 0.923 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 22 | +1 | +0.1362 | +0.2777 | +0.2793 | 0.0000 | +0.6800 | +0.7463 | 0.900 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 23 | +1 | +0.1458 | +0.2773 | +0.2784 | 0.0000 | +0.7403 | +0.7833 | 0.934 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 41 | +1 | +0.1072 | +0.2737 | +0.2745 | 0.0000 | +0.6264 | +0.7252 | 0.577 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 13 | +1 | +0.1459 | +0.2717 | +0.2732 | 0.0000 | +0.5321 | +0.6816 | 0.830 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 21 | +1 | +0.1647 | +0.2710 | +0.2713 | 0.0000 | +0.6711 | +0.7370 | 0.914 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 41 | +1 | +0.1078 | +0.2703 | +0.2712 | 0.0000 | +0.6304 | +0.7345 | 0.826 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1670 | +0.2677 | +0.2687 | 0.0000 | +0.5756 | +0.6718 | 0.954 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 23 | +1 | +0.1519 | +0.2672 | +0.2686 | 0.0000 | +0.7041 | +0.7612 | 0.949 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 41 | +1 | +0.1299 | +0.2655 | +0.2665 | 0.0000 | +0.7819 | +0.7992 | 0.917 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 36 | +1 | +0.1676 | +0.2636 | +0.2646 | 0.0000 | +0.6272 | +0.7206 | 0.957 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 8 | +1 | +0.1647 | +0.2634 | +0.2639 | 0.0000 | +0.6946 | +0.7509 | 0.920 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Cluster 14 | +1 | +0.1535 | +0.2629 | +0.2644 | 0.0000 | +0.6050 | +0.7062 | 0.962 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 9 | +1 | +0.1617 | +0.2607 | +0.2614 | 0.0000 | +0.6710 | +0.7786 | 0.913 |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 14 | +1 | +0.1620 | +0.2602 | +0.2612 | 0.0000 | +0.5313 | +0.7057 | 0.987 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 12 | +1 | +0.1188 | +0.2597 | +0.2609 | 0.0000 | +0.8228 | +0.8038 | 0.869 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Cluster 38 | +1 | +0.1383 | +0.2594 | +0.2608 | 0.0000 | +0.4770 | +0.6872 | 0.848 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 36 | +1 | +0.1687 | +0.2583 | +0.2595 | 0.0000 | +0.5300 | +0.6867 | 0.937 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 30 | +1 | +0.1388 | +0.2580 | +0.2589 | 0.0000 | +0.6265 | +0.7268 | 0.946 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 7 | +1 | +0.1437 | +0.2575 | +0.2579 | 0.0000 | +0.5477 | +0.7072 | 0.969 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 14 | +1 | +0.1572 | +0.2557 | +0.2570 | 0.0000 | +0.6130 | +0.7365 | 0.934 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Cluster 21 | +1 | +0.1415 | +0.2548 | +0.2555 | 0.0000 | +0.6451 | +0.7607 | 0.951 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 13 | +1 | +0.1515 | +0.2525 | +0.2537 | 0.0000 | +0.6885 | +0.7345 | 0.941 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 31 | +1 | +0.1153 | +0.2517 | +0.2530 | 0.0000 | +0.6115 | +0.7052 | 0.880 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 27 | +1 | +0.1532 | +0.2510 | +0.2517 | 0.0000 | +0.5328 | +0.7191 | 0.892 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 14 | +1 | +0.1670 | +0.2492 | +0.2504 | 0.0000 | +0.5781 | +0.7119 | 0.928 |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 30 | +1 | +0.1272 | +0.2484 | +0.2499 | 0.0000 | +0.5348 | +0.6949 | 1.000 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Cluster 30 | +1 | +0.1385 | +0.2469 | +0.2485 | 0.0000 | +0.6003 | +0.6775 | 0.931 |
| `combo_min__first_bar_return__limit_down_proximity_early` | Cluster 30 | +1 | +0.1236 | +0.2454 | +0.2463 | 0.0000 | +0.5984 | +0.6898 | 0.941 |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 18 | +1 | +0.1346 | +0.2447 | +0.2468 | 0.0000 | +0.5327 | +0.7026 | 0.928 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 18 | +1 | +0.1297 | +0.2446 | +0.2460 | 0.0000 | +0.4890 | +0.6790 | 0.944 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 17 | +1 | +0.1402 | +0.2438 | +0.2456 | 0.0000 | +0.4463 | +0.6600 | 0.843 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Cluster 36 | +1 | +0.1562 | +0.2431 | +0.2440 | 0.0000 | +0.5808 | +0.7006 | 0.924 |
| `opening_drive_thrust_ratio` | Cluster 33 | +1 | +0.1143 | +0.2418 | +0.2438 | 0.0000 | +0.5411 | +0.7016 | 0.886 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 26 | +1 | +0.1301 | +0.2397 | +0.2412 | 0.0000 | +0.4812 | +0.7021 | 0.940 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 24 | +1 | +0.1487 | +0.2369 | +0.2383 | 0.0000 | +0.4898 | +0.6918 | 0.921 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 31 | +1 | +0.1155 | +0.2361 | +0.2375 | 0.0000 | +0.5942 | +0.7062 | 0.901 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Cluster 16 | +1 | +0.1495 | +0.2360 | +0.2379 | 0.0000 | +0.4509 | +0.6846 | 0.941 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 31 | +1 | +0.1315 | +0.2355 | +0.2365 | 0.0000 | +0.6505 | +0.7262 | 0.949 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 5 | +1 | +0.1315 | +0.2320 | +0.2339 | 0.0000 | +0.6545 | +0.7309 | 0.960 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 26 | +1 | +0.1308 | +0.2294 | +0.2309 | 0.0000 | +0.4801 | +0.6965 | 0.966 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 2 | +1 | +0.1418 | +0.2283 | +0.2295 | 0.0000 | +0.5990 | +0.7555 | 0.933 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Cluster 15 | +1 | +0.1563 | +0.2277 | +0.2291 | 0.0000 | +0.4677 | +0.6574 | 0.957 |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | Cluster 5 | +1 | +0.1202 | +0.2275 | +0.2294 | 0.0000 | +0.5582 | +0.7129 | 0.872 |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | Cluster 16 | +1 | +0.1489 | +0.2273 | +0.2292 | 0.0000 | +0.4921 | +0.6795 | 0.948 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 16 | +1 | +0.1416 | +0.2273 | +0.2288 | 0.0000 | +0.5309 | +0.7103 | 1.000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Cluster 19 | +1 | +0.1413 | +0.2271 | +0.2289 | 0.0000 | +0.5107 | +0.6913 | 0.948 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 39 | +1 | +0.1530 | +0.2269 | +0.2290 | 0.0000 | +0.5759 | +0.6882 | 0.866 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 1 | +1 | +0.1299 | +0.2267 | +0.2284 | 0.0000 | +0.4590 | +0.6862 | 0.939 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 17 | +1 | +0.1402 | +0.2241 | +0.2258 | 0.0000 | +0.4478 | +0.6888 | 0.955 |
| `combo_z_sum__star50_limit_proximity_early__first_bar_sentiment` | Cluster 37 | +1 | +0.1544 | +0.2235 | +0.2250 | 0.0000 | +0.6641 | +0.7396 | 0.929 |
| `combo_min__star50_limit_proximity_early__impulse_bar_dominance` | Cluster 35 | +1 | +0.1086 | +0.2194 | +0.2204 | 0.0000 | +0.6129 | +0.7324 | 0.876 |
| `combo_max__max_up_ret__bar_body_rng_0` | Cluster 16 | +1 | +0.1381 | +0.2168 | +0.2188 | 0.0000 | +0.4918 | +0.6867 | 0.947 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Cluster 16 | +1 | +0.1346 | +0.2155 | +0.2174 | 0.0000 | +0.3701 | +0.6626 | 0.964 |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 28 | +1 | +0.1348 | +0.2142 | +0.2150 | 0.0000 | +0.5075 | +0.6857 | 0.962 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 12 | +1 | +0.1127 | +0.2140 | +0.2149 | 0.0000 | +0.6132 | +0.7006 | 0.773 |
| `max_up_ret` | Cluster 2 | +1 | +0.1282 | +0.2136 | +0.2148 | 0.0000 | +0.5942 | +0.7165 | 0.942 |
| `combo_z_sum__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 33 | +1 | +0.1053 | +0.2131 | +0.2151 | 0.0000 | +0.5028 | +0.7144 | 0.905 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 29 | +1 | +0.1243 | +0.2094 | +0.2090 | 0.0000 | +0.4687 | +0.6739 | 0.763 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 0 | +1 | +0.1152 | +0.2069 | +0.2090 | 0.0000 | +0.4383 | +0.6929 | 0.919 |
| `combo_max__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 12 | +1 | +0.1113 | +0.2067 | +0.2077 | 0.0000 | +0.5718 | +0.7298 | 0.885 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 25 | +1 | +0.1175 | +0.2049 | +0.2070 | 0.0000 | +0.4553 | +0.6888 | 0.876 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 25 | +1 | +0.1206 | +0.2026 | +0.2046 | 0.0000 | +0.4451 | +0.6846 | 0.925 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 17 | +1 | +0.1288 | +0.2025 | +0.2048 | 0.0000 | +0.3580 | +0.7083 | 0.934 |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | Cluster 13 | +1 | +0.1374 | +0.2021 | +0.2033 | 0.0000 | +0.4381 | +0.6636 | 0.922 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Cluster 28 | +1 | +0.1187 | +0.2017 | +0.2029 | 0.0000 | +0.5439 | +0.7036 | 0.847 |
| `combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Cluster 13 | +1 | +0.1453 | +0.2012 | +0.2023 | 0.0000 | +0.3972 | +0.6636 | 0.955 |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | Cluster 38 | +1 | +0.1356 | +0.2010 | +0.2030 | 0.0000 | +0.4885 | +0.6857 | 0.926 |
| `combo_mean__max_up_ret__impulse_bar_dominance` | Cluster 3 | +1 | +0.1130 | +0.1984 | +0.2000 | 0.0002 | +0.5658 | +0.7191 | 0.899 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Cluster 28 | +1 | +0.1370 | +0.1971 | +0.1978 | 0.0002 | +0.4809 | +0.6713 | 1.000 |
| `combo_diff__max_up_ret__late_bar_momentum` | Cluster 40 | +1 | +0.1218 | +0.1949 | +0.1963 | 0.0002 | +0.4571 | +0.6934 | 0.827 |
| `combo_z_sum__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 4 | +1 | +0.1023 | +0.1898 | +0.1920 | 0.0002 | +0.5278 | +0.6970 | 0.939 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 34 | +1 | +0.1297 | +0.1891 | +0.1901 | 0.0002 | +0.4915 | +0.6610 | 0.870 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Cluster 40 | +1 | +0.1211 | +0.1884 | +0.1896 | 0.0002 | +0.4226 | +0.6872 | 0.870 |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | Cluster 20 | +1 | +0.1314 | +0.1882 | +0.1900 | 0.0002 | +0.3714 | +0.6533 | 0.892 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 6 | +1 | +0.1505 | +0.1881 | +0.1897 | 0.0002 | +0.3850 | +0.6528 | 0.875 |
| `combo_rank_max__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | Cluster 12 | +1 | +0.0991 | +0.1872 | +0.1886 | 0.0002 | +0.6005 | +0.7062 | 0.946 |
| `combo_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 34 | +1 | +0.1193 | +0.1871 | +0.1889 | 0.0002 | +0.3994 | +0.6667 | 0.904 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Cluster 32 | +1 | +0.1261 | +0.1849 | +0.1866 | 0.0002 | +0.3769 | +0.6564 | 0.870 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 17 | +1 | +0.1350 | +0.1837 | +0.1855 | 0.0002 | +0.4576 | +0.6605 | 0.968 |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | Cluster 13 | +1 | +0.1358 | +0.1749 | +0.1760 | 0.0002 | +0.4639 | +0.6790 | 0.945 |
| `combo_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | Cluster 39 | +1 | +0.1311 | +0.1706 | +0.1725 | 0.0006 | +0.4649 | +0.6610 | 1.000 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 0 | +1 | +0.1182 | +0.1684 | +0.1702 | 0.0008 | +0.5036 | +0.7242 | 0.915 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 32 | +1 | +0.0958 | +0.1628 | +0.1639 | 0.0012 | +0.4227 | +0.6918 | 0.832 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 28 | +1 | +0.1095 | +0.1551 | +0.1554 | 0.0018 | +0.4801 | +0.6959 | 0.135 |
| `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector` | Cluster 33 | +1 | +0.0833 | +0.1539 | +0.1559 | 0.0018 | +0.4351 | +0.6805 | 0.888 |
| `volatility_expansion_trend_vector` | Cluster 33 | +1 | +0.0795 | +0.1531 | +0.1550 | 0.0020 | +0.3923 | +0.6667 | 0.939 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 33 | +1 | +0.0962 | +0.1502 | +0.1531 | 0.0022 | +0.4143 | +0.6733 | 0.915 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Cluster 11 | +1 | +0.0591 | +0.1499 | +0.1520 | 0.0022 | +0.4729 | +0.7052 | 0.536 |
| `combo_mean__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | Cluster 35 | +1 | +0.1010 | +0.1423 | +0.1439 | 0.0038 | +0.3506 | +0.6636 | 1.000 |

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
| 300ETF | single | 77 | 29 | 0.2843 | `[9, 7, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (29 clusters)]` |
| 500ETF | single | 197 | 76 | 0.2797 | `[12, 9, 9, 8, 7, 6, 6, 6, 5, 5, 5, 4, ... (76 clusters)]` |
| 159915ETF | single | 96 | 42 | 0.2766 | `[5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 2 | 0.2843 | `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `combo_rank_min__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 1 | 1 | 0.2843 | `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 2 | 2 | 0.2843 | `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 3 | 7 | 0.2843 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio`, `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`, `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 300ETF | single | Cluster 4 | 4 | 0.2843 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `combo_rel_diff__limit_down_proximity_early__volume_concentration`, `combo_ratio__limit_down_proximity_early__volume_concentration`, `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` |
| 300ETF | single | Cluster 5 | 1 | 0.2843 | `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 6 | 5 | 0.2843 | `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `combo_min__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `max_up_ret` |
| 300ETF | single | Cluster 7 | 2 | 0.2843 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 8 | 2 | 0.2843 | `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_min__opening_drive_thrust_ratio__volume_surge_direction` |
| 300ETF | single | Cluster 9 | 2 | 0.2843 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_mean__max_up_ret__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 10 | 1 | 0.2843 | `combo_rank_min__max_up_ret__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 11 | 2 | 0.2843 | `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 12 | 3 | 0.2843 | `rbreaker_sell_setup_proximity_early` | `star50_limit_proximity_early`, `combo_rank_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` |
| 300ETF | single | Cluster 13 | 3 | 0.2843 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 300ETF | single | Cluster 14 | 3 | 0.2843 | `combo_max__max_up_ret__volume_surge_direction` | `combo_rank_max__max_up_ret__volume_surge_direction`, `combo_mean__max_up_ret__volume_surge_direction` |
| 300ETF | single | Cluster 15 | 3 | 0.2843 | `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `combo_rank_max__max_up_ret__first_bar_return`, `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 16 | 1 | 0.2843 | `combo_max__max_up_ret__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 17 | 3 | 0.2843 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 18 | 2 | 0.2843 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 19 | 2 | 0.2843 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_mean__bar_body_rng_0__limit_down_proximity_early` |
| 300ETF | single | Cluster 20 | 2 | 0.2843 | `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 21 | 3 | 0.2843 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 22 | 3 | 0.2843 | `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `combo_rel_diff__max_up_ret__early_vwap_acceleration`, `combo_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 23 | 1 | 0.2843 | `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 24 | 2 | 0.2843 | `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 25 | 3 | 0.2843 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 26 | 2 | 0.2843 | `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 27 | 9 | 0.2843 | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `combo_max__first_bar_return__bar_body_rng_0`, `combo_ratio__bar_body_rng_0__volume_weighted_price_position`, `combo_rank_min__bar_body_rng_0__volume_surge_direction`, `combo_ratio__first_bar_return__volume_surge_direction`, `combo_rank_max__bar_body_rng_0__volume_surge_direction`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_z_sum__first_bar_return__first_bar_sentiment`, `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` |
| 300ETF | single | Cluster 28 | 1 | 0.2843 | `combo_ratio__first_bar_sentiment__volume_surge_direction` | _(none)_ |
| 500ETF | single | Cluster 0 | 2 | 0.2797 | `combo_sig_product__first_bar_sentiment__early_body_momentum` | `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` |
| 500ETF | single | Cluster 1 | 2 | 0.2797 | `combo_rank_min__first_bar_sentiment__bar_ret_0` | `combo_ratio__bar_ret_0__net_volume_flow` |
| 500ETF | single | Cluster 2 | 12 | 0.2797 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`, `combo_max__max_up_ret__early_body_momentum`, `combo_rank_min__max_up_ret__close_vs_open_range`, `combo_rank_max__max_up_ret__early_body_momentum`, `combo_min__max_up_ret__close_vs_open_range`, `combo_mean__max_up_ret__close_vs_open_range`, `combo_min__max_up_ret__high_low_sequence_momentum`, `combo_max__max_up_ret__close_vs_open_range`, `combo_rank_max__max_up_ret__close_vs_open_range`, `combo_mean__max_up_ret__trend_day_regime_conviction`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 3 | 2 | 0.2797 | `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` |
| 500ETF | single | Cluster 4 | 2 | 0.2797 | `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `combo_min__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 5 | 2 | 0.2797 | `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `combo_min__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 6 | 2 | 0.2797 | `combo_min__net_volume_flow__star50_limit_proximity_early` | `combo_rank_min__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 7 | 1 | 0.2797 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 8 | 1 | 0.2797 | `combo_mean__star50_limit_proximity_early__close_vs_open_range` | _(none)_ |
| 500ETF | single | Cluster 9 | 2 | 0.2797 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 10 | 1 | 0.2797 | `combo_mean__star50_limit_proximity_early__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 11 | 1 | 0.2797 | `combo_rank_min__star50_limit_proximity_early__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 12 | 9 | 0.2797 | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`, `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_min__opening_drive_thrust_ratio__first_bar_return`, `combo_mean__opening_drive_thrust_ratio__bar_ret_0`, `combo_rank_max__opening_drive_thrust_ratio__first_bar_return`, `combo_max__opening_drive_thrust_ratio__bar_ret_0` |
| 500ETF | single | Cluster 13 | 7 | 0.2797 | `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | `combo_clamp_diff__max_up_ret__body_size_progression`, `combo_diff__max_up_ret__body_size_progression`, `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_rel_diff__max_up_ret__late_bar_momentum`, `combo_rel_diff__max_up_ret__body_size_progression` |
| 500ETF | single | Cluster 14 | 1 | 0.2797 | `max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 15 | 2 | 0.2797 | `combo_rank_max__close_vs_open_range__max_down_ret` | `combo_max__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 16 | 2 | 0.2797 | `combo_rank_min__close_vs_open_range__max_down_ret` | `combo_min__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 17 | 1 | 0.2797 | `combo_sig_product__high_low_sequence_momentum__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 18 | 2 | 0.2797 | `combo_rank_min__early_body_momentum__max_down_ret` | `combo_min__early_body_momentum__max_down_ret` |
| 500ETF | single | Cluster 19 | 2 | 0.2797 | `combo_rank_max__early_body_momentum__max_down_ret` | `combo_max__net_volume_flow__max_down_ret` |
| 500ETF | single | Cluster 20 | 2 | 0.2797 | `combo_mean__net_volume_flow__max_down_ret` | `combo_mean__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 21 | 1 | 0.2797 | `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 22 | 2 | 0.2797 | `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 23 | 2 | 0.2797 | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` |
| 500ETF | single | Cluster 24 | 2 | 0.2797 | `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` |
| 500ETF | single | Cluster 25 | 2 | 0.2797 | `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | `combo_max__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 26 | 4 | 0.2797 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`, `combo_mean__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 27 | 2 | 0.2797 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 28 | 2 | 0.2797 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 500ETF | single | Cluster 29 | 1 | 0.2797 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | _(none)_ |
| 500ETF | single | Cluster 30 | 2 | 0.2797 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 500ETF | single | Cluster 31 | 1 | 0.2797 | `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 32 | 4 | 0.2797 | `combo_sig_product__max_up_ret__close_vs_open_range` | `combo_sig_product__max_up_ret__early_body_momentum`, `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`, `combo_sig_product__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 33 | 3 | 0.2797 | `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `combo_sig_product__star50_limit_proximity_early__max_down_ret`, `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 34 | 1 | 0.2797 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure` | _(none)_ |
| 500ETF | single | Cluster 35 | 5 | 0.2797 | `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_rank_min__star50_limit_proximity_early__bar_ret_0`, `combo_mean__star50_limit_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 36 | 2 | 0.2797 | `combo_mean__net_volume_flow__first_bar_return` | `combo_mean__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 37 | 2 | 0.2797 | `combo_mean__first_bar_sentiment__early_body_momentum` | `combo_mean__close_vs_open_range__first_bar_sentiment` |
| 500ETF | single | Cluster 38 | 1 | 0.2797 | `combo_min__close_vs_open_range__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 39 | 3 | 0.2797 | `combo_max__close_vs_open_range__first_bar_return` | `combo_rank_max__close_vs_open_range__first_bar_return`, `combo_max__volatility_expansion_trend_vector__bar_ret_0` |
| 500ETF | single | Cluster 40 | 2 | 0.2797 | `combo_rank_min__close_vs_open_range__first_bar_return` | `combo_min__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 41 | 2 | 0.2797 | `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | `combo_max__first_bar_sentiment__early_body_momentum` |
| 500ETF | single | Cluster 42 | 2 | 0.2797 | `combo_rank_max__early_body_momentum__bar_ret_0` | `combo_max__early_body_momentum__first_bar_return` |
| 500ETF | single | Cluster 43 | 2 | 0.2797 | `combo_min__net_volume_flow__bar_ret_0` | `combo_rank_min__early_body_momentum__bar_ret_0` |
| 500ETF | single | Cluster 44 | 1 | 0.2797 | `combo_abs_diff__max_up_ret__close_vs_open_range` | _(none)_ |
| 500ETF | single | Cluster 45 | 1 | 0.2797 | `early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 46 | 5 | 0.2797 | `trend_bar_close_consistency` | `combo_sig_product__close_vs_open_range__early_body_momentum`, `combo_max__close_vs_open_range__early_body_momentum`, `combo_rank_max__close_vs_open_range__early_body_momentum`, `or_fill_ratio` |
| 500ETF | single | Cluster 47 | 6 | 0.2797 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`, `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 48 | 6 | 0.2797 | `combo_max__max_up_ret__first_bar_sentiment` | `max_up_ret`, `combo_rank_max__max_up_ret__bar_ret_0`, `combo_mean__max_up_ret__bar_ret_0`, `combo_max__max_up_ret__bar_ret_0`, `combo_min__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 49 | 2 | 0.2797 | `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | `combo_min__opening_drive_thrust_ratio__close_vs_open_range` |
| 500ETF | single | Cluster 50 | 2 | 0.2797 | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `combo_max__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 51 | 1 | 0.2797 | `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | _(none)_ |
| 500ETF | single | Cluster 52 | 2 | 0.2797 | `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` |
| 500ETF | single | Cluster 53 | 2 | 0.2797 | `combo_min__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` |
| 500ETF | single | Cluster 54 | 2 | 0.2797 | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` |
| 500ETF | single | Cluster 55 | 1 | 0.2797 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 56 | 2 | 0.2797 | `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` |
| 500ETF | single | Cluster 57 | 8 | 0.2797 | `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_rel_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`, `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence`, `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`, `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` |
| 500ETF | single | Cluster 58 | 2 | 0.2797 | `combo_min__max_up_ret__first_bar_sentiment` | `combo_rank_min__close_vs_open_range__first_bar_sentiment` |
| 500ETF | single | Cluster 59 | 1 | 0.2797 | `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 60 | 1 | 0.2797 | `bar_body_rng_0` | _(none)_ |
| 500ETF | single | Cluster 61 | 1 | 0.2797 | `combo_mean__bar_ret_0__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 62 | 2 | 0.2797 | `combo_min__first_bar_sentiment__max_down_ret` | `combo_rank_min__first_bar_sentiment__max_down_ret` |
| 500ETF | single | Cluster 63 | 1 | 0.2797 | `combo_max__close_vs_open_range__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 64 | 2 | 0.2797 | `combo_mean__first_bar_sentiment__bar_ret_0` | `first_bar_return` |
| 500ETF | single | Cluster 65 | 2 | 0.2797 | `combo_rank_max__bar_ret_0__max_down_ret` | `combo_max__first_bar_return__max_down_ret` |
| 500ETF | single | Cluster 66 | 2 | 0.2797 | `combo_rank_min__bar_ret_0__max_down_ret` | `combo_min__first_bar_return__max_down_ret` |
| 500ETF | single | Cluster 67 | 6 | 0.2797 | `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`, `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`, `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 68 | 5 | 0.2797 | `opening_drive_thrust_ratio` | `combo_max__opening_drive_thrust_ratio__max_down_ret`, `combo_mean__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_max__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 69 | 2 | 0.2797 | `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `combo_sig_product__max_up_ret__body_size_progression` |
| 500ETF | single | Cluster 70 | 1 | 0.2797 | `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | _(none)_ |
| 500ETF | single | Cluster 71 | 4 | 0.2797 | `combo_max__star50_limit_proximity_early__bar_ret_0` | `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 72 | 9 | 0.2797 | `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | `combo_min__trend_day_regime_conviction__close_vs_open_range`, `combo_rank_min__net_volume_flow__close_vs_open_range`, `net_volume_flow`, `combo_mean__net_volume_flow__close_vs_open_range`, `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction`, `combo_sig_product__net_volume_flow__close_vs_open_range`, `morning_volume_weighted_momentum`, `open_to_current_return` |
| 500ETF | single | Cluster 73 | 3 | 0.2797 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`, `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` |
| 500ETF | single | Cluster 74 | 3 | 0.2797 | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression`, `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` |
| 500ETF | single | Cluster 75 | 1 | 0.2797 | `combo_rank_max__star50_limit_proximity_early__max_down_ret` | _(none)_ |
| 159915ETF | single | Cluster 0 | 2 | 0.2766 | `combo_max__max_up_ret__volatility_expansion_trend_vector` | `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 1 | 1 | 0.2766 | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 159915ETF | single | Cluster 2 | 2 | 0.2766 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `max_up_ret` |
| 159915ETF | single | Cluster 3 | 1 | 0.2766 | `combo_mean__max_up_ret__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 4 | 1 | 0.2766 | `combo_z_sum__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 5 | 2 | 0.2766 | `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 6 | 1 | 0.2766 | `combo_z_sum__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | _(none)_ |
| 159915ETF | single | Cluster 7 | 1 | 0.2766 | `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return` | _(none)_ |
| 159915ETF | single | Cluster 8 | 2 | 0.2766 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` |
| 159915ETF | single | Cluster 9 | 2 | 0.2766 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 10 | 3 | 0.2766 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`, `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 11 | 1 | 0.2766 | `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 12 | 4 | 0.2766 | `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_max__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_rank_max__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 13 | 5 | 0.2766 | `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`, `combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0`, `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return`, `combo_rank_min__first_bar_sentiment__first_bar_return` |
| 159915ETF | single | Cluster 14 | 4 | 0.2766 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` |
| 159915ETF | single | Cluster 15 | 2 | 0.2766 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 16 | 5 | 0.2766 | `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `combo_rank_max__max_up_ret__bar_body_rng_0`, `combo_max__max_up_ret__bar_ret_0`, `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return`, `combo_max__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 17 | 4 | 0.2766 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__first_bar_return`, `combo_rank_max__opening_drive_thrust_ratio__first_bar_return`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 18 | 2 | 0.2766 | `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` |
| 159915ETF | single | Cluster 19 | 1 | 0.2766 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | _(none)_ |
| 159915ETF | single | Cluster 20 | 1 | 0.2766 | `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 21 | 2 | 0.2766 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 22 | 2 | 0.2766 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 23 | 2 | 0.2766 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` |
| 159915ETF | single | Cluster 24 | 1 | 0.2766 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 25 | 2 | 0.2766 | `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 26 | 2 | 0.2766 | `combo_diff__max_up_ret__demark_setup_reversal_early` | `combo_rel_diff__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 27 | 1 | 0.2766 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | _(none)_ |
| 159915ETF | single | Cluster 28 | 4 | 0.2766 | `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early`, `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`, `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 29 | 1 | 0.2766 | `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | _(none)_ |
| 159915ETF | single | Cluster 30 | 5 | 0.2766 | `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_mean__bar_body_rng_0__limit_down_proximity_early`, `combo_min__first_bar_return__limit_down_proximity_early` |
| 159915ETF | single | Cluster 31 | 3 | 0.2766 | `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 32 | 2 | 0.2766 | `combo_max__max_up_ret__volume_weighted_price_position` | `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 33 | 5 | 0.2766 | `opening_drive_thrust_ratio` | `combo_z_sum__opening_drive_thrust_ratio__impulse_bar_dominance`, `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector`, `volatility_expansion_trend_vector`, `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 34 | 2 | 0.2766 | `combo_z_sum__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `combo_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` |
| 159915ETF | single | Cluster 35 | 2 | 0.2766 | `combo_min__star50_limit_proximity_early__impulse_bar_dominance` | `combo_mean__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` |
| 159915ETF | single | Cluster 36 | 3 | 0.2766 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_mean__star50_limit_proximity_early__bar_ret_0` |
| 159915ETF | single | Cluster 37 | 1 | 0.2766 | `combo_z_sum__star50_limit_proximity_early__first_bar_sentiment` | _(none)_ |
| 159915ETF | single | Cluster 38 | 2 | 0.2766 | `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 39 | 2 | 0.2766 | `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `combo_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 40 | 2 | 0.2766 | `combo_diff__max_up_ret__late_bar_momentum` | `combo_rel_diff__max_up_ret__late_bar_momentum` |
| 159915ETF | single | Cluster 41 | 3 | 0.2766 | `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | `min` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_mean` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `mean` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | `min` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_mean` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | `min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__first_bar_return__bar_body_rng_0` | `max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | `rel_diff` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_max__max_up_ret__volume_surge_direction` | `max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_rank_max__max_up_ret__volume_surge_direction` | `rank_max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_rank_min__bar_body_rng_0__volume_surge_direction` | `rank_min` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` | `clamp_diff` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_concentration` |
| `combo_mean__max_up_ret__volume_surge_direction` | `mean` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_ratio__first_bar_return__volume_surge_direction` | `ratio` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_z_sum__first_bar_return__first_bar_sentiment` | `z_sum` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_rank_max__bar_body_rng_0__volume_surge_direction` | `rank_max` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_rank_min__first_bar_return__volume_weighted_price_position` | `rank_min` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | `rank_max` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | `rank_max` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`trend_bar_close_consistency` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | `min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | `clamp_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | `rank_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `mean` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`trend_day_regime_conviction` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_mean` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | `mean` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | `mean` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | `min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_min__star50_limit_proximity_early__trend_bar_close_consistency` | `rank_min` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_rank_min__close_vs_open_range__first_bar_sentiment` | `rank_min` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | `mean` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__max_up_ret__close_vs_open_range` | `rank_min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`body_size_progression` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_sig_product__max_up_ret__early_body_momentum` | `sig_product` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | `max` | a=`volatility_expansion_trend_vector`, b=`first_bar_sentiment` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rel_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_max__max_up_ret__early_body_momentum` | `max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | `min` | a=`trend_day_regime_conviction`, b=`close_vs_open_range` |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | `rank_min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_min__net_volume_flow__bar_ret_0` | `min` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_mean__net_volume_flow__close_vs_open_range` | `mean` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | `min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__first_bar_sentiment__early_body_momentum` | `mean` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_min__max_up_ret__close_vs_open_range` | `min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__max_up_ret__close_vs_open_range` | `mean` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | `rank_min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__max_up_ret__high_low_sequence_momentum` | `min` | a=`max_up_ret`, b=`high_low_sequence_momentum` |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_max__max_up_ret__close_vs_open_range` | `max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | `mean` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_mean__net_volume_flow__first_bar_return` | `mean` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_max__first_bar_sentiment__early_body_momentum` | `max` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_mean__max_up_ret__bar_ret_0` | `mean` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`trend_day_regime_conviction` |
| `combo_rank_max__max_up_ret__close_vs_open_range` | `rank_max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__close_vs_open_range__first_bar_return` | `min` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`volume_weighted_momentum_acceleration` |
| `combo_max__close_vs_open_range__first_bar_sentiment` | `max` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__close_vs_open_range__first_bar_return` | `rank_min` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | `sig_product` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_mean__max_up_ret__trend_day_regime_conviction` | `mean` | a=`max_up_ret`, b=`trend_day_regime_conviction` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_rank_min__early_body_momentum__bar_ret_0` | `rank_min` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_rank_max__close_vs_open_range__first_bar_return` | `rank_max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_max__close_vs_open_range__first_bar_return` | `max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | `sig_product` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_mean__close_vs_open_range__first_bar_return` | `mean` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_mean__net_volume_flow__max_down_ret` | `mean` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_rank_min__close_vs_open_range__max_down_ret` | `rank_min` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_max__first_bar_return__max_down_ret` | `max` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_min__bar_ret_0__max_down_ret` | `rank_min` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_min__early_body_momentum__max_down_ret` | `rank_min` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_min__close_vs_open_range__first_bar_sentiment` | `min` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_min__early_body_momentum__max_down_ret` | `min` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_momentum_acceleration` |
| `combo_max__early_body_momentum__first_bar_return` | `max` | a=`early_body_momentum`, b=`first_bar_return` |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__close_vs_open_range__early_body_momentum` | `max` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__close_vs_open_range__max_down_ret` | `min` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_rank_max__early_body_momentum__max_down_ret` | `rank_max` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_min__first_bar_return__max_down_ret` | `min` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | `rank_max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_max__close_vs_open_range__early_body_momentum` | `rank_max` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_max__volatility_expansion_trend_vector__bar_ret_0` | `max` | a=`volatility_expansion_trend_vector`, b=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | `abs_diff` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | `rank_max` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_mean__first_bar_sentiment__bar_ret_0` | `mean` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_mean__close_vs_open_range__max_down_ret` | `mean` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__net_volume_flow__max_down_ret` | `max` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | `max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `max` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`early_late_momentum_divergence` |
| `combo_rank_max__close_vs_open_range__max_down_ret` | `rank_max` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_min__first_bar_sentiment__max_down_ret` | `min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | `rank_max` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_day_regime_conviction` |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | `rank_max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_max__close_vs_open_range__max_down_ret` | `max` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `min` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_ratio__bar_ret_0__net_volume_flow` | `ratio` | a=`bar_ret_0`, b=`net_volume_flow` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__high_low_sequence_momentum__max_down_ret` | `sig_product` | a=`high_low_sequence_momentum`, b=`max_down_ret` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_mean` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `mean` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_min` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_min__first_bar_return__limit_down_proximity_early` | `min` | a=`first_bar_return`, b=`limit_down_proximity_early` |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | `rank_min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | `tri_max` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_z_sum__star50_limit_proximity_early__first_bar_sentiment` | `z_sum` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__impulse_bar_dominance` | `min` | a=`star50_limit_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__max_up_ret__bar_body_rng_0` | `max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_z_sum__opening_drive_thrust_ratio__impulse_bar_dominance` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | `max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_max__star50_limit_proximity_early__yesterday_first_30min_return` | `max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | `tri_min` | a=`first_bar_sentiment`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | `rel_diff` | a=`bar_body_rng_0`, b=`demark_setup_reversal_early` |
| `combo_mean__max_up_ret__impulse_bar_dominance` | `mean` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_diff__max_up_ret__late_bar_momentum` | `diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_z_sum__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `z_sum` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | `rank_max` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `z_sum` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_max__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`yesterday_first_30min_return`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | `rank_min` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | `max` | a=`first_bar_sentiment`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | `rank_max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector` | `sig_product` | a=`impulse_bar_dominance`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | `mean` | a=`rbreaker_buy_setup_proximity_early`, b=`impulse_bar_dominance` |
