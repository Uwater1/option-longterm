# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2016_2024`

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
| 300ETF | single | 1,594 | 545 | 422 | 320 | 309 | 307 | 284 | 284 | 114 | 89 | 44 | `[7, 6, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, ... (44 clusters)]` |
| 300ETF | long | 586 | 58 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 587 | 69 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | single | 1,244 | 342 | 302 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | long | 368 | 43 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | short | 321 | 46 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 3,074 | 1,283 | 936 | 800 | 793 | 785 | 767 | 767 | 181 | 144 | 60 | `[12, 11, 11, 5, 5, 4, 4, 4, 3, 3, 3, 3, ... (60 clusters)]` |
| 500ETF | long | 1,350 | 96 | 37 | 37 | 2 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | short | 428 | 51 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | single | 1,915 | 754 | 525 | 483 | 476 | 397 | 395 | 395 | 149 | 121 | 42 | `[12, 12, 10, 6, 6, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` |
| 159915ETF | long | 1,120 | 214 | 130 | 130 | 11 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | short | 299 | 52 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 89 | 44 | `[7, 6, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, ... (44 clusters)]` | +0.1106 | [+0.0682, +0.1521] | +0.2287 | [+0.1292, +0.3265] | +0.7939 | 4.87% | 1.5690 | 3.27% | 1.0737 | 2.0775 | 2.86% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 144 | 60 | `[12, 11, 11, 5, 5, 4, 4, 4, 3, 3, 3, 3, ... (60 clusters)]` | +0.1420 | [+0.0996, +0.1855] | +0.2341 | [+0.1466, +0.3259] | +0.8788 | 5.83% | 1.5401 | 4.22% | 1.1255 | 1.9366 | 3.75% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 121 | 42 | `[12, 12, 10, 6, 6, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` | +0.1407 | [+0.0984, +0.1833] | +0.2803 | [+0.1902, +0.3724] | +0.8061 | 7.91% | 1.8741 | 6.32% | 1.5191 | 2.5972 | 4.92% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 89 | 44 | `[7, 6, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, ... (44 clusters)]` | +0.0247* | [-0.0648, +0.1154] | +0.0724* | [-0.1315, +0.2429] | +0.3576 | 2.56% | 0.6804 | 0.99% | 0.2668 | 0.5745 | 5.01% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 144 | 60 | `[12, 11, 11, 5, 5, 4, 4, 4, 3, 3, 3, 3, ... (60 clusters)]` | +0.1095 | [+0.0274, +0.1874] | +0.0705* | [-0.1215, +0.2086] | +0.8303 | 4.18% | 0.8695 | 2.69% | 0.5621 | 1.0084 | 4.46% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 121 | 42 | `[12, 12, 10, 6, 6, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` | +0.1366 | [+0.0449, +0.2153] | +0.2764 | [+0.0499, +0.4842] | +0.7455 | 11.55% | 1.5047 | 10.08% | 1.3270 | 3.7623 | 6.20% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 40 | +1 | +0.1068 | +0.2602 | +0.2602 | 0.0000 | +0.6687 | +0.7568 | 0.954 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 25 | +1 | +0.1019 | +0.2599 | +0.2605 | 0.0000 | +0.7393 | +0.7640 | 0.939 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 33 | +1 | +0.1023 | +0.2592 | +0.2591 | 0.0000 | +0.6578 | +0.7532 | 0.916 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.0989 | +0.2566 | +0.2561 | 0.0000 | +0.7056 | +0.7496 | 0.653 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 1 | +1 | +0.0915 | +0.2524 | +0.2527 | 0.0000 | +0.8557 | +0.8123 | 0.753 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 33 | +1 | +0.1022 | +0.2509 | +0.2505 | 0.0000 | +0.7382 | +0.7810 | 0.896 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 25 | +1 | +0.1045 | +0.2502 | +0.2509 | 0.0000 | +0.6504 | +0.7244 | 0.912 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 43 | +1 | +0.1013 | +0.2493 | +0.2494 | 0.0000 | +0.6618 | +0.7450 | 0.903 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 41 | +1 | +0.0924 | +0.2468 | +0.2470 | 0.0000 | +0.6402 | +0.6946 | 0.903 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 14 | +1 | +0.0886 | +0.2419 | +0.2414 | 0.0000 | +0.7478 | +0.7548 | 0.958 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 1 | +1 | +0.0939 | +0.2395 | +0.2396 | 0.0000 | +0.7820 | +0.7856 | 0.970 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 15 | +1 | +0.0952 | +0.2350 | +0.2352 | 0.0000 | +0.6025 | +0.7136 | 0.786 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 24 | +1 | +0.1098 | +0.2341 | +0.2347 | 0.0000 | +0.5858 | +0.7368 | 0.876 |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.0980 | +0.2273 | +0.2269 | 0.0000 | +0.6344 | +0.7393 | 1.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 35 | +1 | +0.1008 | +0.2251 | +0.2250 | 0.0000 | +0.4935 | +0.6545 | 0.871 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 29 | +1 | +0.0998 | +0.2226 | +0.2227 | 0.0000 | +0.6215 | +0.7167 | 0.882 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 18 | +1 | +0.0926 | +0.2224 | +0.2225 | 0.0000 | +0.6399 | +0.7028 | 0.887 |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0995 | +0.2176 | +0.2173 | 0.0000 | +0.5767 | +0.7126 | 0.889 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.0876 | +0.2168 | +0.2168 | 0.0000 | +0.7633 | +0.8087 | 0.939 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.0955 | +0.2167 | +0.2162 | 0.0000 | +0.6142 | +0.6982 | 0.948 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 32 | +1 | +0.0899 | +0.2155 | +0.2160 | 0.0000 | +0.4379 | +0.6545 | 0.928 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 1 | +1 | +0.0828 | +0.2116 | +0.2119 | 0.0000 | +0.8349 | +0.8231 | 0.898 |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0992 | +0.2088 | +0.2086 | 0.0000 | +0.5960 | +0.7152 | 0.932 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 23 | +1 | +0.0882 | +0.2082 | +0.2081 | 0.0000 | +0.5333 | +0.6766 | 1.000 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 41 | +1 | +0.1001 | +0.2075 | +0.2076 | 0.0000 | +0.5693 | +0.6915 | 0.961 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 34 | +1 | +0.1010 | +0.2067 | +0.2064 | 0.0000 | +0.6578 | +0.7326 | 0.925 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 17 | +1 | +0.0898 | +0.2047 | +0.2047 | 0.0000 | +0.7352 | +0.7512 | 0.914 |
| `combo_max__max_up_ret__volume_surge_direction` | Cluster 17 | +1 | +0.0764 | +0.2038 | +0.2037 | 0.0000 | +0.7216 | +0.7496 | 0.947 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 35 | +1 | +0.1095 | +0.2034 | +0.2038 | 0.0000 | +0.5295 | +0.6869 | 0.975 |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | Cluster 29 | +1 | +0.1007 | +0.2003 | +0.2006 | 0.0000 | +0.6771 | +0.7368 | 0.936 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 42 | +1 | +0.0953 | +0.1982 | +0.1987 | 0.0000 | +0.4731 | +0.6668 | 0.925 |
| `combo_sig_product__first_bar_return__bar_body_rng_0` | Cluster 5 | +1 | +0.0991 | +0.1976 | +0.1979 | 0.0000 | +0.6275 | +0.7054 | 1.000 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | Cluster 17 | +1 | +0.0776 | +0.1971 | +0.1969 | 0.0000 | +0.7476 | +0.7568 | 0.901 |
| `combo_rank_max__bar_body_rng_0__volume_surge_direction` | Cluster 5 | +1 | +0.0901 | +0.1964 | +0.1964 | 0.0000 | +0.5589 | +0.7203 | 0.922 |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1034 | +0.1960 | +0.1958 | 0.0000 | +0.5606 | +0.7090 | 0.944 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 43 | +1 | +0.0971 | +0.1952 | +0.1951 | 0.0000 | +0.5140 | +0.7126 | 0.948 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 36 | +1 | +0.0849 | +0.1940 | +0.1933 | 0.0000 | +0.5866 | +0.7260 | 0.715 |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.1102 | +0.1930 | +0.1928 | 0.0000 | +0.5957 | +0.6961 | 0.992 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 35 | +1 | +0.1013 | +0.1925 | +0.1925 | 0.0000 | +0.5461 | +0.6961 | 0.950 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 5 | +1 | +0.0972 | +0.1917 | +0.1921 | 0.0000 | +0.5346 | +0.7008 | 0.946 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 21 | +1 | +0.0808 | +0.1915 | +0.1915 | 0.0000 | +0.6276 | +0.7445 | 0.865 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 7 | +1 | +0.0929 | +0.1899 | +0.1904 | 0.0002 | +0.5031 | +0.6869 | 0.912 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.0915 | +0.1892 | +0.1892 | 0.0002 | +0.7145 | +0.7635 | 0.907 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 14 | +1 | +0.0841 | +0.1871 | +0.1864 | 0.0002 | +0.4842 | +0.6941 | 0.940 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.1085 | +0.1857 | +0.1856 | 0.0002 | +0.5117 | +0.6859 | 0.992 |
| `max_up_ret` | Cluster 14 | +1 | +0.0773 | +0.1850 | +0.1850 | 0.0002 | +0.4645 | +0.6740 | 0.919 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 18 | +1 | +0.0955 | +0.1850 | +0.1847 | 0.0002 | +0.5382 | +0.6807 | 0.927 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Cluster 14 | +1 | +0.0807 | +0.1835 | +0.1832 | 0.0002 | +0.4425 | +0.6905 | 0.939 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 10 | +1 | +0.1045 | +0.1829 | +0.1824 | 0.0002 | +0.3689 | +0.6576 | 0.862 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 12 | +1 | +0.0922 | +0.1828 | +0.1826 | 0.0002 | +0.5287 | +0.7167 | 0.979 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 23 | +1 | +0.0881 | +0.1812 | +0.1812 | 0.0004 | +0.5050 | +0.6812 | 0.914 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 27 | +1 | +0.0884 | +0.1805 | +0.1801 | 0.0004 | +0.5938 | +0.7352 | 0.803 |
| `combo_max__first_bar_return__first_bar_sentiment` | Cluster 5 | +1 | +0.0962 | +0.1804 | +0.1804 | 0.0004 | +0.4409 | +0.6617 | 0.920 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 21 | +1 | +0.0937 | +0.1797 | +0.1800 | 0.0006 | +0.5541 | +0.7368 | 1.000 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 14 | +1 | +0.0938 | +0.1792 | +0.1783 | 0.0006 | +0.6786 | +0.7537 | 0.907 |
| `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_body_rng_0` | Cluster 19 | +1 | +0.0701 | +0.1787 | +0.1793 | 0.0006 | +0.4248 | +0.6596 | 0.884 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 24 | +1 | +0.1013 | +0.1786 | +0.1792 | 0.0006 | +0.4619 | +0.7111 | 0.937 |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 17 | +1 | +0.0908 | +0.1776 | +0.1770 | 0.0006 | +0.4792 | +0.7013 | 0.923 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 10 | +1 | +0.1022 | +0.1776 | +0.1774 | 0.0006 | +0.5254 | +0.7239 | 0.943 |
| `combo_tri_min__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Cluster 40 | +1 | +0.0925 | +0.1773 | +0.1770 | 0.0006 | +0.5099 | +0.6787 | 1.000 |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0967 | +0.1749 | +0.1744 | 0.0008 | +0.4005 | +0.6761 | 0.899 |
| `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | Cluster 39 | +1 | +0.0730 | +0.1747 | +0.1747 | 0.0008 | +0.5400 | +0.6931 | 0.867 |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | Cluster 29 | +1 | +0.0962 | +0.1743 | +0.1744 | 0.0008 | +0.6924 | +0.7342 | 0.977 |
| `combo_max__volume_weighted_price_position__volume_surge_direction` | Cluster 31 | +1 | +0.0848 | +0.1738 | +0.1740 | 0.0008 | +0.5086 | +0.6715 | 0.850 |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | Cluster 6 | +1 | +0.0892 | +0.1733 | +0.1741 | 0.0008 | +0.7161 | +0.7553 | 0.869 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | Cluster 14 | +1 | +0.0714 | +0.1714 | +0.1711 | 0.0010 | +0.3509 | +0.6535 | 0.996 |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 4 | +1 | +0.0856 | +0.1702 | +0.1694 | 0.0010 | +0.5890 | +0.7229 | 0.898 |
| `combo_tri_median__volume_weighted_momentum_acceleration__bar_ret_0__volume_weighted_price_position` | Cluster 30 | +1 | +0.0722 | +0.1658 | +0.1664 | 0.0012 | +0.4887 | +0.6566 | 1.000 |
| `early_order_flow_imbalance` | Cluster 27 | +1 | +0.0652 | +0.1648 | +0.1646 | 0.0012 | +0.6152 | +0.7090 | 0.708 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 15 | +1 | +0.0727 | +0.1643 | +0.1641 | 0.0012 | +0.5736 | +0.6776 | 0.820 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Cluster 22 | +1 | +0.0906 | +0.1641 | +0.1638 | 0.0012 | +0.4526 | +0.6684 | 1.000 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 5 | +1 | +0.0957 | +0.1636 | +0.1639 | 0.0012 | +0.5257 | +0.6771 | 1.000 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 4 | +1 | +0.0856 | +0.1615 | +0.1608 | 0.0014 | +0.4347 | +0.6586 | 0.911 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 26 | +1 | +0.0918 | +0.1615 | +0.1615 | 0.0014 | +0.5475 | +0.6925 | 0.958 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Cluster 20 | +1 | +0.0719 | +0.1591 | +0.1593 | 0.0016 | +0.4843 | +0.6864 | 0.639 |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 7 | +1 | +0.0859 | +0.1577 | +0.1580 | 0.0016 | +0.4386 | +0.6797 | 0.993 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 36 | +1 | +0.0609 | +0.1557 | +0.1559 | 0.0022 | +0.4904 | +0.6638 | 0.803 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 16 | +1 | +0.0791 | +0.1550 | +0.1548 | 0.0022 | +0.5846 | +0.7362 | 0.929 |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | Cluster 7 | +1 | +0.0976 | +0.1512 | +0.1511 | 0.0026 | +0.5730 | +0.7018 | 0.887 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | Cluster 28 | +1 | +0.0523 | +0.1476 | +0.1485 | 0.0036 | +0.5459 | +0.6879 | 0.832 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Cluster 20 | +1 | +0.0681 | +0.1458 | +0.1458 | 0.0040 | +0.4134 | +0.6638 | 0.791 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 26 | +1 | +0.0854 | +0.1449 | +0.1449 | 0.0040 | +0.4847 | +0.6848 | 0.869 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Cluster 5 | +1 | +0.0898 | +0.1402 | +0.1408 | 0.0062 | +0.4259 | +0.6853 | 1.000 |
| `always_in_trend_persistence` | Cluster 13 | +1 | +0.0640 | +0.1369 | +0.1365 | 0.0072 | +0.4691 | +0.6900 | 0.906 |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | Cluster 28 | +1 | +0.0817 | +0.1326 | +0.1330 | 0.0098 | +0.4283 | +0.6602 | 0.935 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Cluster 37 | +1 | +0.0405 | +0.1287 | +0.1304 | 0.0110 | +0.5507 | +0.7059 | 0.571 |
| `net_volume_flow` | Cluster 38 | +1 | +0.0673 | +0.1211 | +0.1204 | 0.0166 | +0.5337 | +0.6977 | 0.854 |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | Cluster 5 | +1 | +0.0912 | +0.1163 | +0.1168 | 0.0198 | +0.4432 | +0.6674 | 0.935 |
| `first_30min_return` | Cluster 38 | +1 | +0.0560 | +0.1085 | +0.1077 | 0.0322 | +0.4196 | +0.6812 | 0.847 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 34 | +1 | +0.1297 | +0.2777 | +0.2783 | 0.0000 | +0.9524 | +0.8190 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 33 | +1 | +0.1412 | +0.2745 | +0.2746 | 0.0000 | +1.0155 | +0.8370 | 0.916 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 25 | +1 | +0.1304 | +0.2721 | +0.2714 | 0.0000 | +0.9682 | +0.8509 | 0.977 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 47 | +1 | +0.1302 | +0.2717 | +0.2718 | 0.0000 | +0.7606 | +0.7429 | 0.835 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Cluster 12 | +1 | +0.1384 | +0.2698 | +0.2695 | 0.0000 | +0.7336 | +0.7630 | 0.738 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Cluster 12 | +1 | +0.1350 | +0.2676 | +0.2677 | 0.0000 | +0.9482 | +0.7856 | 0.928 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 33 | +1 | +0.1289 | +0.2665 | +0.2668 | 0.0000 | +0.7864 | +0.7666 | 0.948 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Cluster 16 | +1 | +0.1202 | +0.2644 | +0.2653 | 0.0000 | +0.8057 | +0.7733 | 0.667 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 31 | +1 | +0.1283 | +0.2615 | +0.2607 | 0.0000 | +0.8854 | +0.8077 | 0.809 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 31 | +1 | +0.1351 | +0.2612 | +0.2604 | 0.0000 | +0.8902 | +0.8170 | 0.901 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 12 | +1 | +0.1390 | +0.2593 | +0.2590 | 0.0000 | +0.8755 | +0.7784 | 0.946 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 12 | +1 | +0.1433 | +0.2566 | +0.2561 | 0.0000 | +0.9772 | +0.8283 | 0.853 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 13 | +1 | +0.1176 | +0.2532 | +0.2532 | 0.0000 | +0.7250 | +0.7491 | 0.932 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 32 | +1 | +0.1162 | +0.2524 | +0.2531 | 0.0000 | +0.6638 | +0.7162 | 0.948 |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1211 | +0.2521 | +0.2515 | 0.0000 | +0.6833 | +0.7522 | 0.965 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 12 | +1 | +0.1496 | +0.2513 | +0.2506 | 0.0000 | +0.8829 | +0.8072 | 0.924 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 12 | +1 | +0.1327 | +0.2505 | +0.2497 | 0.0000 | +0.6147 | +0.7352 | 0.909 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 24 | +1 | +0.1471 | +0.2499 | +0.2494 | 0.0000 | +1.0000 | +0.8339 | 0.926 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 24 | +1 | +0.1367 | +0.2494 | +0.2489 | 0.0000 | +0.8916 | +0.8242 | 0.953 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 12 | +1 | +0.1489 | +0.2493 | +0.2487 | 0.0000 | +0.7715 | +0.7825 | 0.945 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 16 | +1 | +0.1350 | +0.2468 | +0.2475 | 0.0000 | +0.7253 | +0.7630 | 0.937 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Cluster 58 | +1 | +0.1231 | +0.2446 | +0.2452 | 0.0000 | +0.7011 | +0.7398 | 0.831 |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | Cluster 42 | +1 | +0.1232 | +0.2423 | +0.2424 | 0.0000 | +0.7620 | +0.7820 | 0.922 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 23 | +1 | +0.1502 | +0.2410 | +0.2404 | 0.0000 | +0.6713 | +0.7733 | 0.923 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Cluster 40 | +1 | +0.1378 | +0.2402 | +0.2398 | 0.0000 | +0.5987 | +0.7147 | 0.917 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__net_volume_flow` | Cluster 3 | +1 | +0.1034 | +0.2400 | +0.2396 | 0.0000 | +0.7828 | +0.8046 | 0.945 |
| `combo_min__net_volume_flow__close_vs_open_range` | Cluster 9 | +1 | +0.0954 | +0.2381 | +0.2379 | 0.0000 | +0.6002 | +0.7316 | 0.909 |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | Cluster 12 | +1 | +0.1219 | +0.2365 | +0.2371 | 0.0000 | +0.8543 | +0.7563 | 0.931 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_day_regime_conviction` | Cluster 25 | +1 | +0.1367 | +0.2357 | +0.2348 | 0.0000 | +0.6670 | +0.7707 | 0.965 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 50 | +1 | +0.1132 | +0.2342 | +0.2348 | 0.0000 | +0.5153 | +0.6735 | 0.850 |
| `combo_max__early_body_momentum__first_bar_return` | Cluster 58 | +1 | +0.1192 | +0.2327 | +0.2333 | 0.0000 | +0.7129 | +0.7501 | 0.906 |
| `combo_max__max_up_ret__early_body_momentum` | Cluster 46 | +1 | +0.1187 | +0.2318 | +0.2320 | 0.0000 | +0.7035 | +0.7434 | 0.929 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 32 | +1 | +0.1016 | +0.2317 | +0.2320 | 0.0000 | +0.6309 | +0.7085 | 0.960 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Cluster 9 | +1 | +0.0939 | +0.2313 | +0.2310 | 0.0000 | +0.6055 | +0.7486 | 0.951 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Cluster 24 | +1 | +0.1215 | +0.2307 | +0.2303 | 0.0000 | +0.6538 | +0.7496 | 0.945 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 59 | +1 | +0.1192 | +0.2299 | +0.2295 | 0.0000 | +0.7190 | +0.7676 | 0.902 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 26 | +1 | +0.1343 | +0.2290 | +0.2289 | 0.0000 | +0.8276 | +0.7995 | 0.987 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 17 | +1 | +0.1326 | +0.2288 | +0.2293 | 0.0000 | +0.6973 | +0.7717 | 0.891 |
| `combo_sig_product__max_up_ret__net_volume_flow` | Cluster 50 | +1 | +0.1096 | +0.2285 | +0.2294 | 0.0000 | +0.6970 | +0.7712 | 0.939 |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | Cluster 55 | +1 | +0.1012 | +0.2285 | +0.2289 | 0.0000 | +0.6139 | +0.7290 | 0.862 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Cluster 32 | +1 | +0.1029 | +0.2285 | +0.2290 | 0.0000 | +0.5745 | +0.6992 | 0.951 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Cluster 46 | +1 | +0.1218 | +0.2283 | +0.2286 | 0.0000 | +0.7052 | +0.7337 | 0.973 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 31 | +1 | +0.1289 | +0.2278 | +0.2275 | 0.0000 | +0.7355 | +0.7373 | 1.000 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 11 | +1 | +0.1003 | +0.2278 | +0.2278 | 0.0000 | +0.5596 | +0.6997 | 0.957 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 41 | +1 | +0.1336 | +0.2277 | +0.2278 | 0.0000 | +0.6246 | +0.7316 | 0.976 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 38 | +1 | +0.1242 | +0.2272 | +0.2281 | 0.0000 | +0.6052 | +0.7532 | 0.762 |
| `combo_max__net_volume_flow__first_bar_sentiment` | Cluster 51 | +1 | +0.1073 | +0.2269 | +0.2265 | 0.0000 | +0.5448 | +0.7100 | 0.891 |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | Cluster 21 | +1 | +0.1174 | +0.2266 | +0.2259 | 0.0000 | +0.8901 | +0.8062 | 0.962 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 38 | +1 | +0.1223 | +0.2266 | +0.2275 | 0.0000 | +0.5691 | +0.7049 | 1.000 |
| `combo_mean__opening_drive_thrust_ratio__early_body_momentum` | Cluster 25 | +1 | +0.1212 | +0.2240 | +0.2233 | 0.0000 | +0.8012 | +0.8129 | 0.988 |
| `combo_min__net_volume_flow__first_bar_return` | Cluster 54 | +1 | +0.1045 | +0.2237 | +0.2241 | 0.0000 | +0.6377 | +0.7147 | 0.921 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 15 | +1 | +0.1321 | +0.2231 | +0.2228 | 0.0000 | +0.6007 | +0.7383 | 0.876 |
| `combo_mean__net_volume_flow__first_bar_return` | Cluster 57 | +1 | +0.1198 | +0.2230 | +0.2235 | 0.0000 | +0.5086 | +0.6689 | 0.971 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | Cluster 31 | +1 | +0.1447 | +0.2230 | +0.2230 | 0.0000 | +0.6242 | +0.6859 | 1.000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 37 | +1 | +0.1250 | +0.2227 | +0.2222 | 0.0000 | +0.6187 | +0.7388 | 0.932 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 31 | +1 | +0.1237 | +0.2227 | +0.2225 | 0.0000 | +0.7743 | +0.7835 | 0.949 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 32 | +1 | +0.1107 | +0.2212 | +0.2214 | 0.0000 | +0.5919 | +0.7188 | 0.918 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 20 | +1 | +0.1389 | +0.2198 | +0.2196 | 0.0000 | +0.6980 | +0.7491 | 0.946 |
| `combo_max__close_vs_open_range__first_bar_return` | Cluster 53 | +1 | +0.1344 | +0.2195 | +0.2202 | 0.0000 | +0.6971 | +0.7666 | 0.937 |
| `combo_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 44 | +1 | +0.1123 | +0.2188 | +0.2187 | 0.0000 | +0.5834 | +0.7105 | 0.947 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 22 | +1 | +0.1164 | +0.2188 | +0.2182 | 0.0000 | +0.6191 | +0.7239 | 0.926 |
| `combo_mean__max_up_ret__first_bar_return` | Cluster 17 | +1 | +0.1334 | +0.2183 | +0.2190 | 0.0000 | +0.5754 | +0.6828 | 0.895 |
| `combo_rank_max__close_vs_open_range__first_bar_return` | Cluster 53 | +1 | +0.1349 | +0.2161 | +0.2169 | 0.0000 | +0.7060 | +0.7640 | 0.943 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 59 | +1 | +0.1252 | +0.2155 | +0.2148 | 0.0000 | +0.5008 | +0.6951 | 0.940 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Cluster 32 | +1 | +0.1006 | +0.2147 | +0.2150 | 0.0000 | +0.6343 | +0.7162 | 0.912 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 37 | +1 | +0.1228 | +0.2136 | +0.2130 | 0.0000 | +0.8447 | +0.8062 | 0.868 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Cluster 50 | +1 | +0.1077 | +0.2133 | +0.2138 | 0.0000 | +0.5487 | +0.6807 | 0.902 |
| `combo_mean__close_vs_open_range__first_bar_return` | Cluster 57 | +1 | +0.1215 | +0.2087 | +0.2093 | 0.0000 | +0.6712 | +0.7455 | 1.000 |
| `combo_max__bar_ret_0__max_down_ret` | Cluster 19 | +1 | +0.1239 | +0.2061 | +0.2067 | 0.0002 | +0.5692 | +0.6879 | 0.886 |
| `max_up_ret` | Cluster 41 | +1 | +0.1293 | +0.2055 | +0.2058 | 0.0002 | +0.5418 | +0.6967 | 0.915 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 18 | +1 | +0.1234 | +0.2055 | +0.2047 | 0.0002 | +0.4652 | +0.6889 | 0.882 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 13 | +1 | +0.1106 | +0.2055 | +0.2048 | 0.0002 | +0.5201 | +0.6900 | 0.838 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 59 | +1 | +0.1188 | +0.2054 | +0.2045 | 0.0002 | +0.5088 | +0.6797 | 0.925 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Cluster 42 | +1 | +0.1302 | +0.2045 | +0.2049 | 0.0002 | +0.6593 | +0.7095 | 0.950 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 12 | +1 | +0.1330 | +0.2045 | +0.2031 | 0.0002 | +0.5743 | +0.7198 | 0.942 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 13 | +1 | +0.0934 | +0.2037 | +0.2045 | 0.0002 | +0.5239 | +0.7085 | 0.924 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 13 | +1 | +0.1035 | +0.2037 | +0.2032 | 0.0002 | +0.5299 | +0.6715 | 0.900 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | Cluster 52 | +1 | +0.1092 | +0.2011 | +0.2014 | 0.0002 | +0.4592 | +0.6607 | 0.967 |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 5 | +1 | +0.0982 | +0.1994 | +0.1992 | 0.0002 | +0.4190 | +0.6684 | 0.943 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | Cluster 52 | +1 | +0.1062 | +0.1989 | +0.1991 | 0.0002 | +0.5206 | +0.7347 | 0.945 |
| `combo_min__max_up_ret__close_vs_open_range` | Cluster 44 | +1 | +0.1042 | +0.1985 | +0.1985 | 0.0002 | +0.5656 | +0.7085 | 0.907 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 31 | +1 | +0.1454 | +0.1983 | +0.1986 | 0.0002 | +0.6091 | +0.7434 | 0.929 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | Cluster 5 | +1 | +0.0942 | +0.1982 | +0.1978 | 0.0002 | +0.4692 | +0.6982 | 0.997 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Cluster 7 | +1 | +0.1078 | +0.1977 | +0.1978 | 0.0002 | +0.5549 | +0.6889 | 0.886 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 59 | +1 | +0.1286 | +0.1967 | +0.1957 | 0.0002 | +0.4497 | +0.6746 | 0.906 |
| `combo_sig_product__first_bar_sentiment__bar_ret_0` | Cluster 16 | +1 | +0.1164 | +0.1959 | +0.1970 | 0.0002 | +0.4899 | +0.6684 | 1.000 |
| `combo_mean__first_bar_sentiment__bar_ret_0` | Cluster 16 | +1 | +0.1165 | +0.1959 | +0.1970 | 0.0002 | +0.4899 | +0.6684 | 0.947 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 21 | +1 | +0.1266 | +0.1954 | +0.1949 | 0.0002 | +0.5322 | +0.6864 | 0.933 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 13 | +1 | +0.1124 | +0.1953 | +0.1950 | 0.0002 | +0.5212 | +0.6602 | 0.886 |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | Cluster 10 | +1 | +0.0876 | +0.1950 | +0.1949 | 0.0002 | +0.4123 | +0.6725 | 0.939 |
| `opening_drive_thrust_ratio` | Cluster 31 | +1 | +0.1384 | +0.1931 | +0.1922 | 0.0002 | +0.6281 | +0.7650 | 0.932 |
| `combo_min__max_up_ret__early_body_momentum` | Cluster 44 | +1 | +0.1109 | +0.1929 | +0.1925 | 0.0002 | +0.5050 | +0.6915 | 0.975 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 31 | +1 | +0.1344 | +0.1910 | +0.1907 | 0.0002 | +0.6656 | +0.7573 | 0.943 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 59 | +1 | +0.1237 | +0.1886 | +0.1880 | 0.0002 | +0.5076 | +0.6735 | 0.904 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 49 | +1 | +0.1055 | +0.1884 | +0.1888 | 0.0002 | +0.6440 | +0.7198 | 0.738 |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | Cluster 15 | +1 | +0.1137 | +0.1873 | +0.1876 | 0.0002 | +0.6496 | +0.7368 | 0.992 |
| `combo_min__net_volume_flow__first_bar_sentiment` | Cluster 52 | +1 | +0.1164 | +0.1870 | +0.1874 | 0.0002 | +0.5711 | +0.7311 | 0.946 |
| `early_order_flow_imbalance` | Cluster 0 | +1 | +0.0810 | +0.1856 | +0.1850 | 0.0002 | +0.4073 | +0.6746 | 0.808 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 43 | +1 | +0.1064 | +0.1853 | +0.1856 | 0.0002 | +0.5561 | +0.6781 | 0.942 |
| `combo_min__close_vs_open_range__first_bar_return` | Cluster 55 | +1 | +0.0937 | +0.1848 | +0.1852 | 0.0002 | +0.6155 | +0.7100 | 1.000 |
| `combo_sig_product__max_up_ret__first_bar_return` | Cluster 48 | +1 | +0.1181 | +0.1831 | +0.1835 | 0.0002 | +0.5083 | +0.7147 | 0.858 |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | Cluster 50 | +1 | +0.1000 | +0.1800 | +0.1806 | 0.0002 | +0.3936 | +0.6596 | 0.924 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 31 | +1 | +0.1277 | +0.1757 | +0.1753 | 0.0002 | +0.5999 | +0.7234 | 0.919 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | Cluster 6 | +1 | +0.1024 | +0.1751 | +0.1749 | 0.0002 | +0.4898 | +0.6740 | 0.976 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Cluster 29 | +1 | +0.0944 | +0.1747 | +0.1744 | 0.0002 | +0.3988 | +0.6586 | 0.710 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 36 | +1 | +0.0935 | +0.1740 | +0.1741 | 0.0006 | +0.7314 | +0.7429 | 0.885 |
| `combo_rank_max__early_body_momentum__max_down_ret` | Cluster 8 | +1 | +0.0929 | +0.1738 | +0.1735 | 0.0006 | +0.4817 | +0.6807 | 0.971 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Cluster 29 | +1 | +0.1104 | +0.1738 | +0.1732 | 0.0006 | +0.4085 | +0.6591 | 0.687 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 12 | +1 | +0.1256 | +0.1727 | +0.1712 | 0.0006 | +0.4735 | +0.6751 | 0.968 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 30 | +1 | +0.1144 | +0.1724 | +0.1720 | 0.0006 | +0.3106 | +0.6596 | 1.000 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Cluster 14 | +1 | +0.1072 | +0.1711 | +0.1716 | 0.0006 | +0.4557 | +0.7049 | 0.847 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 35 | +1 | +0.0825 | +0.1698 | +0.1698 | 0.0006 | +0.4848 | +0.6530 | 0.859 |
| `combo_diff__bar_ret_0__max_down_ret` | Cluster 27 | +1 | +0.0701 | +0.1682 | +0.1692 | 0.0008 | +0.3995 | +0.6550 | 0.482 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 36 | +1 | +0.0914 | +0.1679 | +0.1678 | 0.0008 | +0.6607 | +0.7198 | 0.933 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 12 | +1 | +0.1064 | +0.1674 | +0.1658 | 0.0008 | +0.6214 | +0.7357 | 0.874 |
| `combo_rank_max__close_vs_open_range__early_body_momentum` | Cluster 10 | +1 | +0.0877 | +0.1659 | +0.1661 | 0.0012 | +0.4017 | +0.6746 | 0.948 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 13 | +1 | +0.0906 | +0.1644 | +0.1637 | 0.0016 | +0.5177 | +0.7018 | 0.944 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | Cluster 13 | +1 | +0.1066 | +0.1638 | +0.1632 | 0.0016 | +0.4545 | +0.6607 | 0.963 |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 13 | +1 | +0.1062 | +0.1635 | +0.1628 | 0.0018 | +0.4219 | +0.6679 | 0.903 |
| `combo_sig_product__max_up_ret__body_size_progression` | Cluster 49 | +1 | +0.1032 | +0.1627 | +0.1620 | 0.0020 | +0.6112 | +0.6864 | 0.851 |
| `combo_max__net_volume_flow__max_down_ret` | Cluster 56 | +1 | +0.0958 | +0.1624 | +0.1621 | 0.0020 | +0.5475 | +0.7111 | 0.900 |
| `combo_min__early_body_momentum__max_down_ret` | Cluster 4 | +1 | +0.0938 | +0.1618 | +0.1614 | 0.0020 | +0.4869 | +0.6869 | 0.928 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 13 | +1 | +0.1003 | +0.1600 | +0.1594 | 0.0024 | +0.5056 | +0.7090 | 0.948 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Cluster 19 | +1 | +0.1243 | +0.1583 | +0.1587 | 0.0028 | +0.5563 | +0.6781 | 0.903 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 39 | +1 | +0.0965 | +0.1568 | +0.1564 | 0.0030 | +0.4363 | +0.6514 | 0.869 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Cluster 12 | +1 | +0.1162 | +0.1568 | +0.1566 | 0.0030 | +0.5826 | +0.6915 | 0.925 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 13 | +1 | +0.1178 | +0.1563 | +0.1555 | 0.0034 | +0.3712 | +0.6607 | 0.911 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 28 | +1 | +0.0592 | +0.1563 | +0.1574 | 0.0034 | +0.5870 | +0.6895 | 0.989 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 13 | +1 | +0.1000 | +0.1561 | +0.1555 | 0.0034 | +0.4245 | +0.6833 | 0.945 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 29 | +1 | +0.0912 | +0.1543 | +0.1535 | 0.0038 | +0.4950 | +0.6663 | 0.677 |
| `combo_min__close_vs_open_range__max_down_ret` | Cluster 7 | +1 | +0.0999 | +0.1540 | +0.1540 | 0.0038 | +0.5368 | +0.6956 | 0.946 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | Cluster 45 | +1 | +0.0989 | +0.1509 | +0.1512 | 0.0042 | +0.5130 | +0.6792 | 0.908 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Cluster 52 | +1 | +0.1036 | +0.1476 | +0.1482 | 0.0050 | +0.4521 | +0.6720 | 0.928 |
| `morning_volume_weighted_momentum` | Cluster 2 | +1 | +0.0958 | +0.1465 | +0.1464 | 0.0050 | +0.4710 | +0.6730 | 0.930 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__net_volume_flow` | Cluster 30 | +1 | +0.0843 | +0.1462 | +0.1464 | 0.0052 | +0.3982 | +0.6550 | 0.764 |
| `vwap_trend_channel_slope` | Cluster 1 | +1 | +0.0836 | +0.1436 | +0.1423 | 0.0058 | +0.4568 | +0.6530 | 0.793 |
| `open_to_current_return` | Cluster 2 | +1 | +0.0975 | +0.1415 | +0.1415 | 0.0068 | +0.5170 | +0.7085 | 1.000 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 31 | +1 | +0.1096 | +0.1410 | +0.1404 | 0.0074 | +0.5205 | +0.7054 | 0.904 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 31 | +1 | +0.1274 | +0.1368 | +0.1362 | 0.0082 | +0.5356 | +0.7219 | 0.966 |
| `combo_min__first_bar_sentiment__max_down_ret` | Cluster 15 | +1 | +0.1065 | +0.1321 | +0.1322 | 0.0094 | +0.5128 | +0.6730 | 0.830 |
| `combo_max__trend_bar_close_consistency__max_down_ret` | Cluster 8 | +1 | +0.0838 | +0.1319 | +0.1314 | 0.0094 | +0.3594 | +0.6602 | 0.937 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Cluster 39 | +1 | +0.0949 | +0.1311 | +0.1301 | 0.0096 | +0.4189 | +0.6694 | 0.789 |
| `trend_strength_intraday` | Cluster 0 | +1 | +0.0822 | +0.1217 | +0.1211 | 0.0154 | +0.3552 | +0.6653 | 0.841 |
| `combo_sig_product__trend_day_regime_conviction__max_down_ret` | Cluster 1 | +1 | +0.1025 | +0.1103 | +0.1100 | 0.0268 | +0.4182 | +0.6632 | 0.891 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 32 | +1 | +0.1446 | +0.3321 | +0.3316 | 0.0000 | +0.8369 | +0.8046 | 0.000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 24 | +1 | +0.1386 | +0.3042 | +0.3038 | 0.0000 | +0.8402 | +0.7871 | 0.920 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 19 | +1 | +0.1401 | +0.3031 | +0.3031 | 0.0000 | +0.7885 | +0.7830 | 0.944 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 24 | +1 | +0.1417 | +0.2964 | +0.2958 | 0.0000 | +0.7208 | +0.7635 | 0.948 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 18 | +1 | +0.1163 | +0.2933 | +0.2948 | 0.0000 | +0.7699 | +0.8231 | 0.394 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 36 | +1 | +0.1237 | +0.2883 | +0.2887 | 0.0000 | +0.8062 | +0.7825 | 0.815 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 19 | +1 | +0.1215 | +0.2816 | +0.2816 | 0.0000 | +0.7005 | +0.7326 | 0.948 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 36 | +1 | +0.1248 | +0.2816 | +0.2820 | 0.0000 | +0.8111 | +0.7969 | 0.925 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | Cluster 19 | +1 | +0.1298 | +0.2809 | +0.2804 | 0.0000 | +0.7499 | +0.7753 | 0.925 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 19 | +1 | +0.1376 | +0.2786 | +0.2786 | 0.0000 | +0.6377 | +0.7033 | 0.944 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 32 | +1 | +0.1364 | +0.2773 | +0.2770 | 0.0000 | +0.7041 | +0.7676 | 0.949 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1127 | +0.2752 | +0.2752 | 0.0000 | +0.9370 | +0.8329 | 0.876 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 19 | +1 | +0.1223 | +0.2717 | +0.2715 | 0.0000 | +0.7145 | +0.7604 | 0.941 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 26 | +1 | +0.1324 | +0.2684 | +0.2679 | 0.0000 | +0.5558 | +0.7398 | 0.940 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 31 | +1 | +0.1429 | +0.2656 | +0.2655 | 0.0000 | +0.5402 | +0.7378 | 0.945 |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | Cluster 36 | +1 | +0.1058 | +0.2630 | +0.2636 | 0.0000 | +0.7291 | +0.7697 | 0.947 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 29 | +1 | +0.1404 | +0.2626 | +0.2623 | 0.0000 | +0.6432 | +0.7296 | 0.953 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 31 | +1 | +0.1420 | +0.2614 | +0.2610 | 0.0000 | +0.5531 | +0.7157 | 0.975 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 20 | +1 | +0.1426 | +0.2609 | +0.2610 | 0.0000 | +0.6425 | +0.7465 | 0.890 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1154 | +0.2593 | +0.2594 | 0.0000 | +0.7718 | +0.7697 | 0.949 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Cluster 14 | +1 | +0.1196 | +0.2587 | +0.2576 | 0.0000 | +0.7205 | +0.7645 | 0.844 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 29 | +1 | +0.1289 | +0.2583 | +0.2585 | 0.0000 | +0.5497 | +0.6787 | 0.937 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 18 | +1 | +0.0876 | +0.2581 | +0.2602 | 0.0000 | +0.7167 | +0.7542 | 0.912 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 19 | +1 | +0.1290 | +0.2572 | +0.2565 | 0.0000 | +0.6767 | +0.7270 | 0.915 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 14 | +1 | +0.1211 | +0.2568 | +0.2560 | 0.0000 | +0.6197 | +0.7157 | 0.947 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 23 | +1 | +0.1141 | +0.2551 | +0.2551 | 0.0000 | +0.5473 | +0.7414 | 0.823 |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Cluster 9 | +1 | +0.1210 | +0.2550 | +0.2548 | 0.0000 | +0.5353 | +0.6925 | 0.979 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 18 | +1 | +0.0880 | +0.2538 | +0.2559 | 0.0000 | +0.6913 | +0.7537 | 0.841 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 32 | +1 | +0.1289 | +0.2534 | +0.2535 | 0.0000 | +0.5978 | +0.7496 | 0.945 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 23 | +1 | +0.1141 | +0.2527 | +0.2525 | 0.0000 | +0.5762 | +0.7501 | 0.931 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 19 | +1 | +0.1151 | +0.2508 | +0.2511 | 0.0000 | +0.7294 | +0.7630 | 0.940 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Cluster 33 | +1 | +0.1194 | +0.2499 | +0.2499 | 0.0000 | +0.4828 | +0.7018 | 0.883 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Cluster 33 | +1 | +0.1221 | +0.2493 | +0.2494 | 0.0000 | +0.4894 | +0.6992 | 0.890 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 20 | +1 | +0.1433 | +0.2473 | +0.2472 | 0.0000 | +0.6887 | +0.7733 | 0.912 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 16 | +1 | +0.1252 | +0.2465 | +0.2463 | 0.0000 | +0.5562 | +0.7090 | 0.970 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 19 | +1 | +0.1257 | +0.2439 | +0.2436 | 0.0000 | +0.6344 | +0.7450 | 0.930 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 37 | +1 | +0.1182 | +0.2437 | +0.2438 | 0.0000 | +0.6376 | +0.7434 | 0.765 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 19 | +1 | +0.1114 | +0.2434 | +0.2438 | 0.0000 | +0.6534 | +0.7116 | 0.934 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Cluster 11 | +1 | +0.1114 | +0.2406 | +0.2395 | 0.0000 | +0.5958 | +0.7229 | 0.912 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 10 | +1 | +0.1227 | +0.2392 | +0.2387 | 0.0000 | +0.5407 | +0.6977 | 0.931 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 36 | +1 | +0.1374 | +0.2370 | +0.2374 | 0.0000 | +0.4867 | +0.7141 | 0.855 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 4 | +1 | +0.1144 | +0.2366 | +0.2358 | 0.0000 | +0.6928 | +0.7635 | 0.962 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 18 | +1 | +0.1014 | +0.2348 | +0.2361 | 0.0000 | +0.7438 | +0.7650 | 0.850 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 19 | +1 | +0.1219 | +0.2330 | +0.2322 | 0.0000 | +0.5253 | +0.6797 | 0.902 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 13 | +1 | +0.1285 | +0.2323 | +0.2320 | 0.0000 | +0.5676 | +0.6967 | 0.970 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Cluster 26 | +1 | +0.1284 | +0.2314 | +0.2314 | 0.0000 | +0.5021 | +0.7162 | 0.977 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Cluster 30 | +1 | +0.1306 | +0.2314 | +0.2317 | 0.0000 | +0.5250 | +0.6823 | 1.000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 39 | +1 | +0.0943 | +0.2306 | +0.2298 | 0.0000 | +0.5865 | +0.7054 | 0.848 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 4 | +1 | +0.1233 | +0.2300 | +0.2294 | 0.0000 | +0.6147 | +0.7722 | 0.948 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 18 | +1 | +0.1074 | +0.2266 | +0.2283 | 0.0000 | +0.6850 | +0.7609 | 0.983 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 2 | +1 | +0.0822 | +0.2228 | +0.2222 | 0.0000 | +0.5674 | +0.7558 | 0.893 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 12 | +1 | +0.1245 | +0.2224 | +0.2216 | 0.0000 | +0.5352 | +0.7090 | 0.955 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 9 | +1 | +0.1154 | +0.2220 | +0.2210 | 0.0000 | +0.6021 | +0.7229 | 0.949 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 38 | +1 | +0.1019 | +0.2219 | +0.2223 | 0.0000 | +0.5745 | +0.7141 | 0.868 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 13 | +1 | +0.1304 | +0.2208 | +0.2205 | 0.0000 | +0.5473 | +0.7193 | 0.971 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 10 | +1 | +0.1155 | +0.2197 | +0.2191 | 0.0000 | +0.4703 | +0.6931 | 0.969 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 41 | +1 | +0.1341 | +0.2177 | +0.2174 | 0.0000 | +0.5316 | +0.6823 | 1.000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 41 | +1 | +0.1371 | +0.2173 | +0.2166 | 0.0000 | +0.5162 | +0.6674 | 0.946 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Cluster 16 | +1 | +0.1169 | +0.2171 | +0.2172 | 0.0000 | +0.4379 | +0.6869 | 0.970 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 39 | +1 | +0.1027 | +0.2161 | +0.2154 | 0.0000 | +0.5306 | +0.7198 | 0.886 |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 11 | +1 | +0.1152 | +0.2157 | +0.2144 | 0.0000 | +0.5459 | +0.7090 | 0.937 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 21 | +1 | +0.1093 | +0.2156 | +0.2151 | 0.0000 | +0.5120 | +0.7100 | 0.878 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 21 | +1 | +0.1108 | +0.2152 | +0.2145 | 0.0000 | +0.5275 | +0.7049 | 0.922 |
| `opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.1062 | +0.2148 | +0.2136 | 0.0000 | +0.5626 | +0.7054 | 0.920 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 28 | +1 | +0.1225 | +0.2142 | +0.2137 | 0.0000 | +0.4915 | +0.6946 | 0.926 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Cluster 11 | +1 | +0.1172 | +0.2139 | +0.2129 | 0.0000 | +0.5957 | +0.7290 | 0.962 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Cluster 14 | +1 | +0.1192 | +0.2133 | +0.2127 | 0.0000 | +0.4576 | +0.6658 | 0.948 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 4 | +1 | +0.1146 | +0.2133 | +0.2125 | 0.0000 | +0.5311 | +0.6997 | 0.940 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 41 | +1 | +0.1336 | +0.2131 | +0.2128 | 0.0000 | +0.4982 | +0.6602 | 0.890 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 0 | +1 | +0.0822 | +0.2131 | +0.2122 | 0.0000 | +0.6113 | +0.7445 | 0.918 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 9 | +1 | +0.1228 | +0.2126 | +0.2122 | 0.0000 | +0.5596 | +0.6694 | 0.923 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 18 | +1 | +0.0942 | +0.2124 | +0.2126 | 0.0000 | +0.5568 | +0.6848 | 0.767 |
| `combo_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position` | Cluster 36 | +1 | +0.0858 | +0.2118 | +0.2124 | 0.0000 | +0.6447 | +0.7501 | 0.855 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 8 | +1 | +0.1139 | +0.2099 | +0.2099 | 0.0002 | +0.3873 | +0.6735 | 0.896 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 41 | +1 | +0.1165 | +0.2097 | +0.2095 | 0.0002 | +0.5061 | +0.6853 | 0.917 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Cluster 40 | +1 | +0.0859 | +0.2096 | +0.2089 | 0.0002 | +0.6535 | +0.7177 | 0.740 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 41 | +1 | +0.1233 | +0.2073 | +0.2069 | 0.0002 | +0.4431 | +0.6514 | 0.936 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 38 | +1 | +0.0883 | +0.2066 | +0.2073 | 0.0002 | +0.4935 | +0.6715 | 0.908 |
| `max_up_ret` | Cluster 4 | +1 | +0.1123 | +0.2061 | +0.2058 | 0.0002 | +0.7080 | +0.7604 | 0.919 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Cluster 15 | +1 | +0.1029 | +0.2060 | +0.2057 | 0.0002 | +0.4730 | +0.6591 | 0.952 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | Cluster 12 | +1 | +0.1202 | +0.2055 | +0.2046 | 0.0002 | +0.5013 | +0.6987 | 0.943 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 18 | +1 | +0.1024 | +0.2033 | +0.2038 | 0.0002 | +0.4871 | +0.7039 | 0.906 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 41 | +1 | +0.1133 | +0.2020 | +0.2013 | 0.0002 | +0.4436 | +0.6550 | 0.924 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | Cluster 15 | +1 | +0.0864 | +0.2003 | +0.1996 | 0.0002 | +0.4419 | +0.7049 | 0.934 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 14 | +1 | +0.1172 | +0.1994 | +0.1984 | 0.0002 | +0.5191 | +0.6828 | 0.922 |
| `combo_max__max_up_ret__impulse_bar_dominance` | Cluster 6 | +1 | +0.0929 | +0.1981 | +0.1980 | 0.0002 | +0.6333 | +0.7450 | 0.862 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 25 | +1 | +0.1146 | +0.1965 | +0.1966 | 0.0002 | +0.4887 | +0.6679 | 0.897 |
| `combo_tri_max__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | Cluster 18 | +1 | +0.0973 | +0.1939 | +0.1944 | 0.0002 | +0.5835 | +0.7033 | 0.961 |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 18 | +1 | +0.0938 | +0.1936 | +0.1952 | 0.0002 | +0.4319 | +0.6776 | 0.918 |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 19 | +1 | +0.1000 | +0.1933 | +0.1933 | 0.0002 | +0.4887 | +0.6853 | 1.000 |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | Cluster 5 | +1 | +0.0816 | +0.1932 | +0.1931 | 0.0002 | +0.6138 | +0.7290 | 0.854 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | Cluster 19 | +1 | +0.0946 | +0.1899 | +0.1902 | 0.0002 | +0.5843 | +0.6797 | 0.946 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 41 | +1 | +0.1225 | +0.1877 | +0.1873 | 0.0002 | +0.4653 | +0.6535 | 0.938 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Cluster 41 | +1 | +0.1094 | +0.1871 | +0.1869 | 0.0002 | +0.5686 | +0.6776 | 0.872 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 0 | +1 | +0.1011 | +0.1870 | +0.1861 | 0.0002 | +0.4876 | +0.6956 | 0.919 |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 27 | +1 | +0.1018 | +0.1854 | +0.1852 | 0.0002 | +0.4445 | +0.6787 | 0.914 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Cluster 41 | +1 | +0.1153 | +0.1850 | +0.1843 | 0.0004 | +0.5192 | +0.6699 | 0.936 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Cluster 37 | +1 | +0.1016 | +0.1848 | +0.1848 | 0.0004 | +0.4947 | +0.6910 | 0.851 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Cluster 17 | +1 | +0.0727 | +0.1841 | +0.1841 | 0.0004 | +0.4847 | +0.6509 | 1.000 |
| `net_volume_flow` | Cluster 3 | +1 | +0.0770 | +0.1831 | +0.1824 | 0.0008 | +0.5974 | +0.7213 | 0.903 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 2 | +1 | +0.1031 | +0.1829 | +0.1825 | 0.0008 | +0.5183 | +0.7229 | 0.922 |
| `combo_max__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 34 | +1 | +0.0520 | +0.1805 | +0.1793 | 0.0010 | +0.4169 | +0.6617 | 0.357 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 11 | +1 | +0.1072 | +0.1798 | +0.1782 | 0.0010 | +0.4494 | +0.6725 | 0.948 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 17 | +1 | +0.0745 | +0.1782 | +0.1779 | 0.0010 | +0.5107 | +0.6776 | 0.839 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | Cluster 16 | +1 | +0.1103 | +0.1777 | +0.1776 | 0.0010 | +0.3683 | +0.6643 | 1.000 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 41 | +1 | +0.0974 | +0.1774 | +0.1767 | 0.0010 | +0.3693 | +0.6560 | 0.895 |
| `combo_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 17 | +1 | +0.0745 | +0.1774 | +0.1770 | 0.0010 | +0.5172 | +0.6889 | 0.949 |
| `combo_z_sum__limit_down_proximity_early__volume_weighted_price_position` | Cluster 36 | +1 | +0.1040 | +0.1757 | +0.1759 | 0.0010 | +0.3857 | +0.6617 | 0.894 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 5 | +1 | +0.0917 | +0.1754 | +0.1747 | 0.0010 | +0.5251 | +0.7167 | 0.957 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 7 | +1 | +0.0818 | +0.1747 | +0.1742 | 0.0012 | +0.5170 | +0.7116 | 0.877 |
| `combo_max__yesterday_first_30min_return__limit_down_proximity_early` | Cluster 18 | +1 | +0.0798 | +0.1746 | +0.1748 | 0.0012 | +0.5322 | +0.6864 | 0.922 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 4 | +1 | +0.1021 | +0.1712 | +0.1711 | 0.0012 | +0.6423 | +0.7424 | 0.913 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Cluster 34 | +1 | +0.0672 | +0.1678 | +0.1664 | 0.0016 | +0.4436 | +0.6607 | 0.532 |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | Cluster 8 | +1 | +0.0856 | +0.1675 | +0.1672 | 0.0016 | +0.4018 | +0.7090 | 0.908 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 39 | +1 | +0.0757 | +0.1664 | +0.1661 | 0.0018 | +0.4012 | +0.6586 | 0.884 |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | Cluster 41 | +1 | +0.1100 | +0.1534 | +0.1532 | 0.0032 | +0.4487 | +0.6766 | 1.000 |
| `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | Cluster 1 | +1 | +0.0731 | +0.1525 | +0.1522 | 0.0032 | +0.4787 | +0.7008 | 0.889 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 41 | +1 | +0.0916 | +0.1458 | +0.1452 | 0.0050 | +0.3306 | +0.6710 | 1.000 |
| `combo_sig_product__bar_body_rng_0__bar_ret_0` | Cluster 9 | +1 | +0.1169 | +0.1377 | +0.1376 | 0.0080 | +0.3811 | +0.6566 | 1.000 |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | Cluster 35 | +1 | +0.0719 | +0.1229 | +0.1239 | 0.0158 | +0.4388 | +0.6540 | 0.882 |
| `close_vs_open_range` | Cluster 1 | +1 | +0.0638 | +0.1148 | +0.1144 | 0.0230 | +0.5019 | +0.7208 | 0.860 |

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
| 300ETF | single | 89 | 44 | 0.2455 | `[7, 6, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, ... (44 clusters)]` |
| 500ETF | single | 144 | 60 | 0.2713 | `[12, 11, 11, 5, 5, 4, 4, 4, 3, 3, 3, 3, ... (60 clusters)]` |
| 159915ETF | single | 121 | 42 | 0.2347 | `[12, 12, 10, 6, 6, 4, 4, 4, 3, 3, 3, 3, ... (42 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 2 | 0.2455 | `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 1 | 3 | 0.2455 | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `combo_mean__max_up_ret__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 2 | 2 | 0.2455 | `combo_tri_max__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 3 | 2 | 0.2455 | `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 4 | 2 | 0.2455 | `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 300ETF | single | Cluster 5 | 7 | 0.2455 | `combo_sig_product__first_bar_return__bar_body_rng_0` | `combo_rank_max__bar_body_rng_0__volume_surge_direction`, `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`, `combo_max__first_bar_return__first_bar_sentiment`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_ratio__first_bar_return__volume_surge_direction`, `combo_rank_min__first_bar_return__first_bar_sentiment` |
| 300ETF | single | Cluster 6 | 1 | 0.2455 | `combo_sig_product__first_bar_return__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 7 | 3 | 0.2455 | `combo_rank_min__max_up_ret__first_bar_sentiment` | `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` |
| 300ETF | single | Cluster 8 | 2 | 0.2455 | `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 9 | 1 | 0.2455 | `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 10 | 2 | 0.2455 | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` |
| 300ETF | single | Cluster 11 | 2 | 0.2455 | `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 12 | 1 | 0.2455 | `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 13 | 1 | 0.2455 | `always_in_trend_persistence` | _(none)_ |
| 300ETF | single | Cluster 14 | 6 | 0.2455 | `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `max_up_ret`, `combo_rank_max__max_up_ret__opening_drive_thrust_ratio`, `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`, `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 15 | 2 | 0.2455 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 300ETF | single | Cluster 16 | 1 | 0.2455 | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 17 | 4 | 0.2455 | `combo_mean__max_up_ret__volume_surge_direction` | `combo_max__max_up_ret__volume_surge_direction`, `combo_rank_max__max_up_ret__volume_surge_direction`, `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` |
| 300ETF | single | Cluster 18 | 2 | 0.2455 | `combo_rank_max__max_up_ret__first_bar_return` | `combo_max__max_up_ret__first_bar_sentiment` |
| 300ETF | single | Cluster 19 | 1 | 0.2455 | `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 20 | 2 | 0.2455 | `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` |
| 300ETF | single | Cluster 21 | 2 | 0.2455 | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 22 | 1 | 0.2455 | `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 23 | 2 | 0.2455 | `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `combo_min__bar_body_rng_0__limit_down_proximity_early` |
| 300ETF | single | Cluster 24 | 2 | 0.2455 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `combo_mean__star50_limit_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 25 | 2 | 0.2455 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 26 | 2 | 0.2455 | `combo_diff__max_up_ret__early_vwap_acceleration` | `combo_rel_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 27 | 2 | 0.2455 | `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `early_order_flow_imbalance` |
| 300ETF | single | Cluster 28 | 2 | 0.2455 | `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | `combo_ratio__first_bar_sentiment__volume_weighted_price_position` |
| 300ETF | single | Cluster 29 | 3 | 0.2455 | `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `combo_rank_max__volume_weighted_price_position__bar_body_rng_0`, `combo_mean__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 30 | 1 | 0.2455 | `combo_tri_median__volume_weighted_momentum_acceleration__bar_ret_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 31 | 1 | 0.2455 | `combo_max__volume_weighted_price_position__volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 32 | 1 | 0.2455 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | _(none)_ |
| 300ETF | single | Cluster 33 | 2 | 0.2455 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 34 | 1 | 0.2455 | `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 35 | 3 | 0.2455 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 36 | 2 | 0.2455 | `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 37 | 1 | 0.2455 | `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | _(none)_ |
| 300ETF | single | Cluster 38 | 2 | 0.2455 | `net_volume_flow` | `first_30min_return` |
| 300ETF | single | Cluster 39 | 1 | 0.2455 | `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 40 | 2 | 0.2455 | `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_min__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 41 | 2 | 0.2455 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_mean__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 42 | 1 | 0.2455 | `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 43 | 2 | 0.2455 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` |
| 500ETF | single | Cluster 0 | 2 | 0.2713 | `early_order_flow_imbalance` | `trend_strength_intraday` |
| 500ETF | single | Cluster 1 | 2 | 0.2713 | `vwap_trend_channel_slope` | `combo_sig_product__trend_day_regime_conviction__max_down_ret` |
| 500ETF | single | Cluster 2 | 2 | 0.2713 | `morning_volume_weighted_momentum` | `open_to_current_return` |
| 500ETF | single | Cluster 3 | 1 | 0.2713 | `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 4 | 1 | 0.2713 | `combo_min__early_body_momentum__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 5 | 2 | 0.2713 | `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 6 | 1 | 0.2713 | `combo_mean__volatility_expansion_trend_vector__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 7 | 2 | 0.2713 | `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | `combo_min__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 8 | 2 | 0.2713 | `combo_rank_max__early_body_momentum__max_down_ret` | `combo_max__trend_bar_close_consistency__max_down_ret` |
| 500ETF | single | Cluster 9 | 2 | 0.2713 | `combo_rank_min__net_volume_flow__close_vs_open_range` | `combo_min__net_volume_flow__close_vs_open_range` |
| 500ETF | single | Cluster 10 | 2 | 0.2713 | `combo_sig_product__close_vs_open_range__early_body_momentum` | `combo_rank_max__close_vs_open_range__early_body_momentum` |
| 500ETF | single | Cluster 11 | 1 | 0.2713 | `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | _(none)_ |
| 500ETF | single | Cluster 12 | 12 | 0.2713 | `combo_clamp_diff__max_up_ret__body_size_progression` | `combo_rel_diff__max_up_ret__body_size_progression`, `combo_diff__max_up_ret__body_size_progression`, `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_rel_diff__max_up_ret__early_late_momentum_divergence`, `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`, `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` |
| 500ETF | single | Cluster 13 | 11 | 0.2713 | `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`, `combo_rank_max__net_volume_flow__star50_limit_proximity_early`, `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency`, `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_rank_max__star50_limit_proximity_early__close_vs_open_range`, `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_max__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 14 | 1 | 0.2713 | `combo_sig_product__first_bar_sentiment__early_body_momentum` | _(none)_ |
| 500ETF | single | Cluster 15 | 3 | 0.2713 | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment`, `combo_min__first_bar_sentiment__max_down_ret` |
| 500ETF | single | Cluster 16 | 4 | 0.2713 | `combo_rank_min__first_bar_sentiment__bar_ret_0` | `combo_rank_min__max_up_ret__first_bar_sentiment`, `combo_sig_product__first_bar_sentiment__bar_ret_0`, `combo_mean__first_bar_sentiment__bar_ret_0` |
| 500ETF | single | Cluster 17 | 2 | 0.2713 | `combo_rank_max__max_up_ret__first_bar_return` | `combo_mean__max_up_ret__first_bar_return` |
| 500ETF | single | Cluster 18 | 1 | 0.2713 | `combo_max__max_up_ret__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 19 | 2 | 0.2713 | `combo_max__bar_ret_0__max_down_ret` | `combo_rank_max__bar_ret_0__max_down_ret` |
| 500ETF | single | Cluster 20 | 1 | 0.2713 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 21 | 2 | 0.2713 | `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | `combo_max__opening_drive_thrust_ratio__close_vs_open_range` |
| 500ETF | single | Cluster 22 | 2 | 0.2713 | `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_min__opening_drive_thrust_ratio__close_vs_open_range` |
| 500ETF | single | Cluster 23 | 1 | 0.2713 | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 500ETF | single | Cluster 24 | 3 | 0.2713 | `combo_min__opening_drive_thrust_ratio__max_up_ret` | `combo_mean__opening_drive_thrust_ratio__max_up_ret`, `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` |
| 500ETF | single | Cluster 25 | 3 | 0.2713 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_day_regime_conviction`, `combo_mean__opening_drive_thrust_ratio__early_body_momentum` |
| 500ETF | single | Cluster 26 | 1 | 0.2713 | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 27 | 1 | 0.2713 | `combo_diff__bar_ret_0__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 28 | 1 | 0.2713 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration` | _(none)_ |
| 500ETF | single | Cluster 29 | 3 | 0.2713 | `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | `combo_sig_product__star50_limit_proximity_early__max_down_ret`, `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 30 | 2 | 0.2713 | `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `combo_sig_product__rbreaker_sell_setup_proximity_early__net_volume_flow` |
| 500ETF | single | Cluster 31 | 11 | 0.2713 | `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`, `combo_min__opening_drive_thrust_ratio__bar_ret_0`, `combo_mean__opening_drive_thrust_ratio__bar_ret_0`, `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`, `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`, `opening_drive_thrust_ratio`, `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_rank_max__opening_drive_thrust_ratio__max_down_ret`, `combo_mean__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 32 | 5 | 0.2713 | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_min__net_volume_flow__star50_limit_proximity_early`, `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`, `combo_mean__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 33 | 2 | 0.2713 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 34 | 1 | 0.2713 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | _(none)_ |
| 500ETF | single | Cluster 35 | 1 | 0.2713 | `combo_mean__star50_limit_proximity_early__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 36 | 2 | 0.2713 | `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `combo_min__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 37 | 2 | 0.2713 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 500ETF | single | Cluster 38 | 2 | 0.2713 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 39 | 2 | 0.2713 | `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` |
| 500ETF | single | Cluster 40 | 1 | 0.2713 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | _(none)_ |
| 500ETF | single | Cluster 41 | 2 | 0.2713 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `max_up_ret` |
| 500ETF | single | Cluster 42 | 2 | 0.2713 | `combo_mean__max_up_ret__volatility_expansion_trend_vector` | `combo_rank_max__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 43 | 1 | 0.2713 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | _(none)_ |
| 500ETF | single | Cluster 44 | 3 | 0.2713 | `combo_min__max_up_ret__volatility_expansion_trend_vector` | `combo_min__max_up_ret__close_vs_open_range`, `combo_min__max_up_ret__early_body_momentum` |
| 500ETF | single | Cluster 45 | 1 | 0.2713 | `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | _(none)_ |
| 500ETF | single | Cluster 46 | 2 | 0.2713 | `combo_rank_max__max_up_ret__early_body_momentum` | `combo_max__max_up_ret__early_body_momentum` |
| 500ETF | single | Cluster 47 | 1 | 0.2713 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 48 | 1 | 0.2713 | `combo_sig_product__max_up_ret__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 49 | 2 | 0.2713 | `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `combo_sig_product__max_up_ret__body_size_progression` |
| 500ETF | single | Cluster 50 | 4 | 0.2713 | `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `combo_sig_product__max_up_ret__net_volume_flow`, `combo_sig_product__max_up_ret__close_vs_open_range`, `combo_sig_product__max_up_ret__trend_bar_close_consistency` |
| 500ETF | single | Cluster 51 | 1 | 0.2713 | `combo_max__net_volume_flow__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 52 | 4 | 0.2713 | `combo_mean__close_vs_open_range__first_bar_sentiment` | `combo_mean__first_bar_sentiment__early_body_momentum`, `combo_min__net_volume_flow__first_bar_sentiment`, `combo_min__close_vs_open_range__first_bar_sentiment` |
| 500ETF | single | Cluster 53 | 2 | 0.2713 | `combo_max__close_vs_open_range__first_bar_return` | `combo_rank_max__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 54 | 1 | 0.2713 | `combo_min__net_volume_flow__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 55 | 2 | 0.2713 | `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | `combo_min__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 56 | 1 | 0.2713 | `combo_max__net_volume_flow__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 57 | 2 | 0.2713 | `combo_mean__net_volume_flow__first_bar_return` | `combo_mean__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 58 | 2 | 0.2713 | `combo_rank_max__early_body_momentum__bar_ret_0` | `combo_max__early_body_momentum__first_bar_return` |
| 500ETF | single | Cluster 59 | 5 | 0.2713 | `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`, `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` |
| 159915ETF | single | Cluster 0 | 2 | 0.2347 | `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 1 | 2 | 0.2347 | `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | `close_vs_open_range` |
| 159915ETF | single | Cluster 2 | 2 | 0.2347 | `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `combo_max__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 3 | 1 | 0.2347 | `net_volume_flow` | _(none)_ |
| 159915ETF | single | Cluster 4 | 6 | 0.2347 | `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `opening_drive_thrust_ratio`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`, `max_up_ret`, `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 5 | 2 | 0.2347 | `combo_rank_min__max_up_ret__impulse_bar_dominance` | `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` |
| 159915ETF | single | Cluster 6 | 1 | 0.2347 | `combo_max__max_up_ret__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 7 | 1 | 0.2347 | `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 8 | 2 | 0.2347 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 9 | 4 | 0.2347 | `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `combo_rank_min__max_up_ret__first_bar_sentiment`, `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`, `combo_sig_product__bar_body_rng_0__bar_ret_0` |
| 159915ETF | single | Cluster 10 | 2 | 0.2347 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` |
| 159915ETF | single | Cluster 11 | 4 | 0.2347 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`, `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` |
| 159915ETF | single | Cluster 12 | 2 | 0.2347 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 13 | 2 | 0.2347 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 14 | 4 | 0.2347 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`, `combo_rank_min__max_up_ret__bar_body_rng_0`, `combo_min__opening_drive_thrust_ratio__bar_ret_0` |
| 159915ETF | single | Cluster 15 | 2 | 0.2347 | `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 16 | 3 | 0.2347 | `combo_mean__max_up_ret__bar_body_rng_0` | `combo_rank_max__max_up_ret__bar_body_rng_0`, `combo_max__first_bar_return__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 17 | 3 | 0.2347 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`, `combo_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` |
| 159915ETF | single | Cluster 18 | 10 | 0.2347 | `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `combo_min__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_tri_mean__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`, `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_tri_max__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return`, `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`, `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`, `combo_max__yesterday_first_30min_return__limit_down_proximity_early` |
| 159915ETF | single | Cluster 19 | 12 | 0.2347 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`, `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`, `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`, `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`, `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_min__bar_ret_0__limit_down_proximity_early` |
| 159915ETF | single | Cluster 20 | 2 | 0.2347 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 21 | 2 | 0.2347 | `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 22 | 2 | 0.2347 | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 23 | 2 | 0.2347 | `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `combo_diff__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 24 | 2 | 0.2347 | `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` |
| 159915ETF | single | Cluster 25 | 1 | 0.2347 | `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 26 | 2 | 0.2347 | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_mean__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 27 | 1 | 0.2347 | `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 28 | 1 | 0.2347 | `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 29 | 2 | 0.2347 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `combo_mean__star50_limit_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 30 | 1 | 0.2347 | `combo_mean__star50_limit_proximity_early__bar_ret_0` | _(none)_ |
| 159915ETF | single | Cluster 31 | 2 | 0.2347 | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 32 | 3 | 0.2347 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 33 | 2 | 0.2347 | `combo_diff__first_bar_return__demark_setup_reversal_early` | `combo_rel_diff__first_bar_return__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 34 | 2 | 0.2347 | `combo_max__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 35 | 1 | 0.2347 | `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | _(none)_ |
| 159915ETF | single | Cluster 36 | 6 | 0.2347 | `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`, `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`, `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`, `combo_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`, `combo_z_sum__limit_down_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 37 | 2 | 0.2347 | `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 38 | 2 | 0.2347 | `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` |
| 159915ETF | single | Cluster 39 | 3 | 0.2347 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`, `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 40 | 1 | 0.2347 | `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 41 | 12 | 0.2347 | `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`, `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return`, `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`, `combo_rank_max__max_up_ret__star50_limit_proximity_early`, `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`, `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early`, `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `mean` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `rank_min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_max` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_surge_direction` | `mean` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_max__max_up_ret__volume_surge_direction` | `max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | `mean` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_sig_product__first_bar_return__bar_body_rng_0` | `sig_product` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__volume_surge_direction` | `rank_max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_rank_max__bar_body_rng_0__volume_surge_direction` | `rank_max` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_mean` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `rank_max` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_max__first_bar_return__first_bar_sentiment` | `max` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_body_rng_0` | `tri_median` | a=`volume_weighted_momentum_acceleration`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_min__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | `tri_min` | a=`star50_limit_proximity_early`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | `sig_product` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | `rank_max` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_max__volume_weighted_price_position__volume_surge_direction` | `max` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | `sig_product` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_tri_median__volume_weighted_momentum_acceleration__bar_ret_0__volume_weighted_price_position` | `tri_median` | a=`volume_weighted_momentum_acceleration`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | `sig_product` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | `rank_max` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`smooth_momentum_structure`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_ratio__first_bar_return__volume_surge_direction` | `ratio` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | `ratio` | a=`first_bar_sentiment`, b=`volume_weighted_price_position` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | `rank_min` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`volatility_expansion_trend_vector` |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | `rank_min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | `mean` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__net_volume_flow` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`net_volume_flow` |
| `combo_min__net_volume_flow__close_vs_open_range` | `min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | `rel_diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_day_regime_conviction` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`trend_day_regime_conviction` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_max__early_body_momentum__first_bar_return` | `max` | a=`early_body_momentum`, b=`first_bar_return` |
| `combo_max__max_up_ret__early_body_momentum` | `max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | `rank_min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_day_regime_conviction` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__net_volume_flow` | `sig_product` | a=`max_up_ret`, b=`net_volume_flow` |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`bar_ret_0` |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | `min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_mean` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_max__net_volume_flow__first_bar_sentiment` | `max` | a=`net_volume_flow`, b=`first_bar_sentiment` |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_mean__opening_drive_thrust_ratio__early_body_momentum` | `mean` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_min__net_volume_flow__first_bar_return` | `min` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_mean__net_volume_flow__first_bar_return` | `mean` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_max__close_vs_open_range__first_bar_return` | `max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_min__max_up_ret__volatility_expansion_trend_vector` | `min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | `min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__max_up_ret__first_bar_return` | `mean` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_max__close_vs_open_range__first_bar_return` | `rank_max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_mean__close_vs_open_range__first_bar_return` | `mean` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_max__max_up_ret__close_vs_open_range` | `rank_max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`smooth_momentum_structure` |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | `mean` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_median` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_mean__first_bar_sentiment__early_body_momentum` | `mean` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_min__max_up_ret__close_vs_open_range` | `min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`trend_day_regime_conviction` |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_sig_product__first_bar_sentiment__bar_ret_0` | `sig_product` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_mean__first_bar_sentiment__bar_ret_0` | `mean` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | `sig_product` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_min__max_up_ret__early_body_momentum` | `min` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`first_bar_sentiment` |
| `combo_min__net_volume_flow__first_bar_sentiment` | `min` | a=`net_volume_flow`, b=`first_bar_sentiment` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_momentum_acceleration` |
| `combo_min__close_vs_open_range__first_bar_return` | `min` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__first_bar_return` | `sig_product` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | `sig_product` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | `mean` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | `sig_product` | a=`star50_limit_proximity_early`, b=`early_body_momentum` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_max__early_body_momentum__max_down_ret` | `rank_max` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_diff__bar_ret_0__max_down_ret` | `diff` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__close_vs_open_range__early_body_momentum` | `rank_max` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | `rank_max` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | `rank_max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `max` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__net_volume_flow__max_down_ret` | `max` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_min__early_body_momentum__max_down_ret` | `min` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | `rank_max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`late_bar_momentum` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`trend_bar_close_consistency` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`net_volume_flow`, c=`volume_weighted_momentum_acceleration` |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | `max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `sig_product` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__close_vs_open_range__max_down_ret` | `min` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | `tri_median` | a=`max_up_ret`, b=`net_volume_flow`, c=`body_size_progression` |
| `combo_min__close_vs_open_range__first_bar_sentiment` | `min` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__net_volume_flow` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`net_volume_flow` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_min__first_bar_sentiment__max_down_ret` | `min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_max__trend_bar_close_consistency__max_down_ret` | `max` | a=`trend_bar_close_consistency`, b=`max_down_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_sig_product__trend_day_regime_conviction__max_down_ret` | `sig_product` | a=`trend_day_regime_conviction`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | `rank_min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | `diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | `rel_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `mean` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | `mean` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `rank_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | `rank_min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `min` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | `tri_median` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | `sig_product` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | `mean` | a=`bar_body_rng_0`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | `rank_min` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_max__max_up_ret__impulse_bar_dominance` | `max` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_tri_max__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | `tri_max` | a=`star50_limit_proximity_early`, b=`yesterday_early_momentum`, c=`yesterday_first_30min_return` |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_median` | a=`star50_limit_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | `rank_min` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_min__bar_ret_0__limit_down_proximity_early` | `min` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `rank_max` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | `max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_max__opening_drive_thrust_ratio__demark_setup_reversal_early` | `max` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | `max` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_z_sum__limit_down_proximity_early__volume_weighted_price_position` | `z_sum` | a=`limit_down_proximity_early`, b=`volume_weighted_price_position` |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | `min` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_max__yesterday_first_30min_return__limit_down_proximity_early` | `max` | a=`yesterday_first_30min_return`, b=`limit_down_proximity_early` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | `z_sum` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `min` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | `max` | a=`first_bar_return`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | `z_sum` | a=`impulse_bar_dominance`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_sig_product__bar_body_rng_0__bar_ret_0` | `sig_product` | a=`bar_body_rng_0`, b=`bar_ret_0` |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | `sig_product` | a=`yesterday_first_30min_return`, b=`yesterday_early_trend` |
