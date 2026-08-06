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
| 300ETF | single | 1,797 | 580 | 439 | 318 | 305 | 303 | 250 | 250 | 37 | 37 | 17 | `[4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, ... (17 clusters)]` |
| 300ETF | long | 586 | 58 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 587 | 69 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | single | 985 | 145 | 100 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | long | 368 | 43 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | short | 321 | 46 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 4,744 | 2,116 | 1,603 | 1,454 | 1,448 | 1,430 | 1,401 | 1,401 | 111 | 111 | 41 | `[8, 8, 7, 6, 6, 6, 5, 4, 4, 3, 3, 3, ... (41 clusters)]` |
| 500ETF | long | 1,350 | 96 | 37 | 37 | 2 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | short | 428 | 51 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | single | 2,975 | 910 | 574 | 491 | 488 | 365 | 360 | 360 | 100 | 99 | 43 | `[5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 2, ... (43 clusters)]` |
| 159915ETF | long | 1,120 | 214 | 130 | 130 | 11 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | short | 299 | 52 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 37 | 17 | `[4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, ... (17 clusters)]` | +0.1147 | [+0.0721, +0.1576] | +0.2326 | [+0.1338, +0.3387] | +0.7939 | 5.47% | 1.6844 | 3.84% | 1.2037 | 2.3987 | 3.60% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 111 | 41 | `[8, 8, 7, 6, 6, 6, 5, 4, 4, 3, 3, 3, ... (41 clusters)]` | +0.1455 | [+0.1039, +0.1888] | +0.2516 | [+0.1654, +0.3445] | +0.9273 | 6.82% | 1.6537 | 5.20% | 1.2761 | 2.2701 | 4.14% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 99 | 43 | `[5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 2, ... (43 clusters)]` | +0.1457 | [+0.1029, +0.1866] | +0.2650 | [+0.1760, +0.3522] | +0.6727 | 8.37% | 1.8378 | 6.72% | 1.4958 | 2.5702 | 5.26% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 37 | 17 | `[4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, ... (17 clusters)]` | +0.0361* | [-0.0528, +0.1314] | +0.1193* | [-0.0897, +0.2877] | +0.6242 | 3.21% | 0.8164 | 1.58% | 0.4041 | 0.8503 | 4.68% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 111 | 41 | `[8, 8, 7, 6, 6, 6, 5, 4, 4, 3, 3, 3, ... (41 clusters)]` | +0.1110 | [+0.0273, +0.1887] | +0.0768* | [-0.1237, +0.2149] | +0.8424 | 4.31% | 0.7628 | 2.82% | 0.5013 | 0.9394 | 5.44% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 99 | 43 | `[5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 2, ... (43 clusters)]` | +0.1420 | [+0.0500, +0.2200] | +0.2801 | [+0.0701, +0.4838] | +0.7333 | 12.63% | 1.6137 | 11.16% | 1.4418 | 4.1237 | 5.66% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 10 | +1 | +0.1068 | +0.2602 | +0.2602 | 0.0000 | +0.6687 | +0.7568 | 0.000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 16 | +1 | +0.1019 | +0.2599 | +0.2605 | 0.0000 | +0.7393 | +0.7640 | 0.939 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 6 | +1 | +0.1023 | +0.2592 | +0.2591 | 0.0000 | +0.6578 | +0.7532 | 0.916 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Cluster 14 | +1 | +0.0989 | +0.2566 | +0.2561 | 0.0000 | +0.7056 | +0.7496 | 0.948 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 0 | +1 | +0.0915 | +0.2524 | +0.2527 | 0.0000 | +0.8557 | +0.8123 | 0.935 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.1022 | +0.2509 | +0.2505 | 0.0000 | +0.7382 | +0.7810 | 0.896 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 16 | +1 | +0.1045 | +0.2502 | +0.2509 | 0.0000 | +0.6504 | +0.7244 | 0.860 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Cluster 12 | +1 | +0.1013 | +0.2493 | +0.2494 | 0.0000 | +0.6618 | +0.7450 | 0.908 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 12 | +1 | +0.0924 | +0.2468 | +0.2470 | 0.0000 | +0.6402 | +0.6946 | 0.903 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 9 | +1 | +0.0886 | +0.2419 | +0.2414 | 0.0000 | +0.7478 | +0.7548 | 0.888 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 1 | +1 | +0.0939 | +0.2395 | +0.2396 | 0.0000 | +0.7820 | +0.7856 | 0.586 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 15 | +1 | +0.1098 | +0.2341 | +0.2347 | 0.0000 | +0.5858 | +0.7368 | 0.876 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 4 | +1 | +0.1008 | +0.2251 | +0.2250 | 0.0000 | +0.4935 | +0.6545 | 0.860 |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Cluster 13 | +1 | +0.0998 | +0.2226 | +0.2227 | 0.0000 | +0.6215 | +0.7167 | 0.925 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Cluster 2 | +1 | +0.0876 | +0.2168 | +0.2168 | 0.0000 | +0.7633 | +0.8087 | 0.939 |
| `combo_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 14 | +1 | +0.0955 | +0.2167 | +0.2162 | 0.0000 | +0.6142 | +0.6982 | 0.869 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 11 | +1 | +0.0909 | +0.2167 | +0.2167 | 0.0000 | +0.7077 | +0.7311 | 0.924 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 6 | +1 | +0.0899 | +0.2155 | +0.2160 | 0.0000 | +0.4379 | +0.6545 | 0.928 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 1 | +1 | +0.0828 | +0.2116 | +0.2119 | 0.0000 | +0.8349 | +0.8231 | 0.898 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 16 | +1 | +0.0882 | +0.2082 | +0.2081 | 0.0000 | +0.5333 | +0.6766 | 0.896 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | Cluster 8 | +1 | +0.0795 | +0.2060 | +0.2054 | 0.0000 | +0.6536 | +0.7111 | 0.924 |
| `combo_tri_median__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 4 | +1 | +0.1032 | +0.2055 | +0.2052 | 0.0000 | +0.5159 | +0.6699 | 0.938 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 3 | +1 | +0.1095 | +0.2034 | +0.2038 | 0.0000 | +0.5295 | +0.6869 | 0.939 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | Cluster 9 | +1 | +0.0985 | +0.2033 | +0.2027 | 0.0000 | +0.6787 | +0.7481 | 0.897 |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | Cluster 13 | +1 | +0.1007 | +0.2003 | +0.2006 | 0.0000 | +0.6771 | +0.7368 | 0.855 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | Cluster 9 | +1 | +0.0886 | +0.1989 | +0.1979 | 0.0000 | +0.5454 | +0.7352 | 0.936 |
| `combo_tri_median__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Cluster 11 | +1 | +0.0953 | +0.1982 | +0.1987 | 0.0000 | +0.4731 | +0.6668 | 0.925 |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 5 | +1 | +0.1102 | +0.1930 | +0.1928 | 0.0000 | +0.5957 | +0.6961 | 0.884 |
| `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 2 | +1 | +0.0915 | +0.1892 | +0.1892 | 0.0002 | +0.7145 | +0.7635 | 0.851 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 9 | +1 | +0.0841 | +0.1871 | +0.1864 | 0.0002 | +0.4842 | +0.6941 | 0.949 |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 5 | +1 | +0.1085 | +0.1857 | +0.1856 | 0.0002 | +0.5117 | +0.6859 | 0.934 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 16 | +1 | +0.0881 | +0.1812 | +0.1812 | 0.0004 | +0.5050 | +0.6812 | 0.944 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 15 | +1 | +0.1013 | +0.1786 | +0.1792 | 0.0006 | +0.4619 | +0.7111 | 0.937 |
| `combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0` | Cluster 10 | +1 | +0.0925 | +0.1773 | +0.1770 | 0.0006 | +0.5099 | +0.6787 | 0.941 |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | Cluster 13 | +1 | +0.0962 | +0.1743 | +0.1744 | 0.0008 | +0.6924 | +0.7342 | 0.948 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 10 | +1 | +0.0919 | +0.1694 | +0.1691 | 0.0010 | +0.4220 | +0.6550 | 0.931 |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Cluster 7 | +1 | +0.0814 | +0.1673 | +0.1669 | 0.0010 | +0.5393 | +0.7188 | 0.863 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 35 | +1 | +0.1297 | +0.2777 | +0.2783 | 0.0000 | +0.9524 | +0.8190 | 0.836 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 8 | +1 | +0.1277 | +0.2753 | +0.2761 | 0.0000 | +0.8950 | +0.7923 | 0.890 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 6 | +1 | +0.1412 | +0.2745 | +0.2746 | 0.0000 | +1.0155 | +0.8370 | 0.916 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 27 | +1 | +0.1304 | +0.2721 | +0.2714 | 0.0000 | +0.9682 | +0.8509 | 0.893 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 3 | +1 | +0.1302 | +0.2717 | +0.2718 | 0.0000 | +0.7606 | +0.7429 | 0.000 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Cluster 0 | +1 | +0.1384 | +0.2698 | +0.2695 | 0.0000 | +0.7336 | +0.7630 | 0.946 |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | Cluster 5 | +1 | +0.1315 | +0.2685 | +0.2690 | 0.0000 | +0.7788 | +0.7578 | 0.828 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Cluster 0 | +1 | +0.1350 | +0.2676 | +0.2677 | 0.0000 | +0.9482 | +0.7856 | 0.682 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 34 | +1 | +0.1289 | +0.2665 | +0.2668 | 0.0000 | +0.7864 | +0.7666 | 0.948 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 0 | +1 | +0.1390 | +0.2593 | +0.2590 | 0.0000 | +0.8755 | +0.7784 | 0.853 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1433 | +0.2566 | +0.2561 | 0.0000 | +0.9772 | +0.8283 | 0.842 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 1 | +1 | +0.1391 | +0.2549 | +0.2538 | 0.0000 | +0.8602 | +0.8108 | 0.936 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 9 | +1 | +0.1176 | +0.2532 | +0.2532 | 0.0000 | +0.7250 | +0.7491 | 0.932 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 21 | +1 | +0.1162 | +0.2524 | +0.2531 | 0.0000 | +0.6638 | +0.7162 | 0.948 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 31 | +1 | +0.1391 | +0.2518 | +0.2523 | 0.0000 | +0.6963 | +0.7630 | 0.928 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1496 | +0.2513 | +0.2506 | 0.0000 | +0.8829 | +0.8072 | 0.924 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 24 | +1 | +0.1496 | +0.2511 | +0.2517 | 0.0000 | +0.6513 | +0.7147 | 0.915 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 0 | +1 | +0.1327 | +0.2505 | +0.2497 | 0.0000 | +0.6147 | +0.7352 | 0.909 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__bar_ret_0` | Cluster 3 | +1 | +0.1269 | +0.2503 | +0.2509 | 0.0000 | +0.7383 | +0.7573 | 0.936 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 27 | +1 | +0.1367 | +0.2494 | +0.2489 | 0.0000 | +0.8916 | +0.8242 | 0.922 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Cluster 2 | +1 | +0.1309 | +0.2455 | +0.2452 | 0.0000 | +0.6473 | +0.7445 | 0.913 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 8 | +1 | +0.1350 | +0.2451 | +0.2458 | 0.0000 | +0.7819 | +0.7614 | 0.805 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Cluster 5 | +1 | +0.1231 | +0.2446 | +0.2452 | 0.0000 | +0.7011 | +0.7398 | 0.830 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 6 | +1 | +0.1314 | +0.2428 | +0.2429 | 0.0000 | +0.7686 | +0.7558 | 0.909 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 7 | +1 | +0.1257 | +0.2425 | +0.2437 | 0.0000 | +0.6176 | +0.7044 | 0.937 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 31 | +1 | +0.1329 | +0.2424 | +0.2435 | 0.0000 | +0.7537 | +0.7620 | 0.927 |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | Cluster 16 | +1 | +0.1232 | +0.2423 | +0.2424 | 0.0000 | +0.7620 | +0.7820 | 0.916 |
| `combo_clamp_diff__bar_ret_0__body_size_progression` | Cluster 0 | +1 | +0.1272 | +0.2421 | +0.2423 | 0.0000 | +0.5676 | +0.6925 | 0.890 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 27 | +1 | +0.1502 | +0.2410 | +0.2404 | 0.0000 | +0.6713 | +0.7733 | 0.927 |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | Cluster 5 | +1 | +0.1417 | +0.2405 | +0.2406 | 0.0000 | +0.6983 | +0.7589 | 0.949 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure` | Cluster 29 | +1 | +0.1034 | +0.2400 | +0.2396 | 0.0000 | +0.7828 | +0.8046 | 0.916 |
| `combo_min__net_volume_flow__close_vs_open_range` | Cluster 29 | +1 | +0.0954 | +0.2381 | +0.2379 | 0.0000 | +0.6002 | +0.7316 | 0.931 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 36 | +1 | +0.1087 | +0.2377 | +0.2386 | 0.0000 | +0.6523 | +0.7177 | 0.917 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 27 | +1 | +0.1350 | +0.2372 | +0.2372 | 0.0000 | +0.7689 | +0.7548 | 0.950 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 27 | +1 | +0.1467 | +0.2354 | +0.2355 | 0.0000 | +0.6763 | +0.7290 | 0.946 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | Cluster 35 | +1 | +0.1213 | +0.2346 | +0.2350 | 0.0000 | +0.8492 | +0.8123 | 0.923 |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | Cluster 30 | +1 | +0.1213 | +0.2344 | +0.2341 | 0.0000 | +0.6801 | +0.7321 | 0.941 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | Cluster 25 | +1 | +0.1374 | +0.2343 | +0.2343 | 0.0000 | +0.6414 | +0.7465 | 0.939 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Cluster 12 | +1 | +0.1373 | +0.2340 | +0.2337 | 0.0000 | +0.8024 | +0.7625 | 0.929 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | Cluster 9 | +1 | +0.1128 | +0.2335 | +0.2337 | 0.0000 | +0.7086 | +0.7486 | 0.949 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 23 | +1 | +0.1550 | +0.2331 | +0.2334 | 0.0000 | +0.6772 | +0.7316 | 0.931 |
| `combo_max__early_body_momentum__first_bar_return` | Cluster 5 | +1 | +0.1192 | +0.2327 | +0.2333 | 0.0000 | +0.7129 | +0.7501 | 0.938 |
| `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 20 | +1 | +0.1016 | +0.2317 | +0.2320 | 0.0000 | +0.6309 | +0.7085 | 0.870 |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | Cluster 0 | +1 | +0.1472 | +0.2316 | +0.2307 | 0.0000 | +0.6335 | +0.7347 | 0.935 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Cluster 29 | +1 | +0.0939 | +0.2313 | +0.2310 | 0.0000 | +0.6055 | +0.7486 | 0.948 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Cluster 22 | +1 | +0.1335 | +0.2294 | +0.2297 | 0.0000 | +0.5799 | +0.7265 | 0.777 |
| `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | Cluster 32 | +1 | +0.0928 | +0.2291 | +0.2281 | 0.0000 | +0.5559 | +0.7069 | 0.853 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 1 | +1 | +0.1343 | +0.2290 | +0.2289 | 0.0000 | +0.8276 | +0.7995 | 0.855 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 31 | +1 | +0.1326 | +0.2288 | +0.2293 | 0.0000 | +0.6973 | +0.7717 | 0.905 |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | Cluster 30 | +1 | +0.1012 | +0.2285 | +0.2289 | 0.0000 | +0.6139 | +0.7290 | 0.946 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Cluster 15 | +1 | +0.1218 | +0.2283 | +0.2286 | 0.0000 | +0.7052 | +0.7337 | 0.894 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 4 | +1 | +0.1429 | +0.2279 | +0.2277 | 0.0000 | +0.5868 | +0.6843 | 0.911 |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Cluster 9 | +1 | +0.1198 | +0.2271 | +0.2273 | 0.0000 | +0.6648 | +0.7398 | 0.939 |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | Cluster 12 | +1 | +0.1174 | +0.2266 | +0.2259 | 0.0000 | +0.8901 | +0.8062 | 0.749 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Cluster 22 | +1 | +0.1356 | +0.2258 | +0.2262 | 0.0000 | +0.5710 | +0.7219 | 0.905 |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Cluster 21 | +1 | +0.1114 | +0.2256 | +0.2262 | 0.0000 | +0.5673 | +0.6997 | 0.929 |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | Cluster 11 | +1 | +0.1073 | +0.2253 | +0.2245 | 0.0000 | +0.6375 | +0.7188 | 0.842 |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | Cluster 40 | +1 | +0.1197 | +0.2252 | +0.2255 | 0.0000 | +0.6984 | +0.7249 | 0.874 |
| `combo_mean__net_volume_flow__first_bar_return` | Cluster 40 | +1 | +0.1198 | +0.2230 | +0.2235 | 0.0000 | +0.5086 | +0.6689 | 0.940 |
| `combo_min__volatility_expansion_trend_vector__bar_ret_0` | Cluster 30 | +1 | +0.1010 | +0.2226 | +0.2229 | 0.0000 | +0.6210 | +0.7147 | 0.942 |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | Cluster 36 | +1 | +0.1008 | +0.2217 | +0.2224 | 0.0000 | +0.6346 | +0.7111 | 0.946 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | Cluster 35 | +1 | +0.1081 | +0.2217 | +0.2224 | 0.0000 | +0.6022 | +0.7219 | 0.945 |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | Cluster 40 | +1 | +0.1335 | +0.2204 | +0.2203 | 0.0000 | +0.5849 | +0.7028 | 0.943 |
| `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | Cluster 40 | +1 | +0.1249 | +0.2204 | +0.2201 | 0.0000 | +0.7572 | +0.7769 | 0.950 |
| `combo_max__first_bar_return__close_vs_open_range` | Cluster 5 | +1 | +0.1344 | +0.2195 | +0.2202 | 0.0000 | +0.6971 | +0.7666 | 0.937 |
| `combo_tri_median__max_up_ret__net_volume_flow__bar_ret_0` | Cluster 40 | +1 | +0.1231 | +0.2190 | +0.2195 | 0.0000 | +0.5150 | +0.7141 | 0.912 |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | Cluster 29 | +1 | +0.0982 | +0.2186 | +0.2179 | 0.0000 | +0.5412 | +0.6967 | 0.923 |
| `combo_tri_max__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 15 | +1 | +0.1219 | +0.2181 | +0.2183 | 0.0000 | +0.6952 | +0.7707 | 0.946 |
| `combo_max__max_up_ret__first_bar_return` | Cluster 31 | +1 | +0.1314 | +0.2180 | +0.2185 | 0.0000 | +0.6418 | +0.7393 | 0.933 |
| `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 10 | +1 | +0.1219 | +0.2179 | +0.2173 | 0.0000 | +0.7361 | +0.7542 | 0.910 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | Cluster 28 | +1 | +0.1178 | +0.2176 | +0.2179 | 0.0000 | +0.5993 | +0.6982 | 0.934 |
| `combo_tri_median__volatility_expansion_trend_vector__star50_limit_proximity_early__bar_ret_0` | Cluster 25 | +1 | +0.1303 | +0.2168 | +0.2169 | 0.0000 | +0.6749 | +0.7347 | 0.923 |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 2 | +1 | +0.1277 | +0.2165 | +0.2163 | 0.0000 | +0.6500 | +0.7481 | 0.944 |
| `combo_rank_max__first_bar_return__close_vs_open_range` | Cluster 5 | +1 | +0.1349 | +0.2161 | +0.2169 | 0.0000 | +0.7060 | +0.7640 | 0.943 |
| `combo_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 18 | +1 | +0.1063 | +0.2153 | +0.2147 | 0.0000 | +0.7405 | +0.7404 | 0.907 |
| `combo_tri_mean__early_body_momentum__star50_limit_proximity_early__trend_day_regime_conviction` | Cluster 9 | +1 | +0.1049 | +0.2121 | +0.2121 | 0.0000 | +0.5557 | +0.7039 | 0.942 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Cluster 28 | +1 | +0.1149 | +0.2104 | +0.2102 | 0.0000 | +0.6221 | +0.7013 | 0.878 |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | Cluster 37 | +1 | +0.1158 | +0.2091 | +0.2092 | 0.0000 | +0.5925 | +0.6715 | 0.800 |
| `combo_mean__first_bar_return__close_vs_open_range` | Cluster 40 | +1 | +0.1215 | +0.2087 | +0.2093 | 0.0000 | +0.6712 | +0.7455 | 0.949 |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | Cluster 32 | +1 | +0.0943 | +0.2069 | +0.2061 | 0.0002 | +0.6279 | +0.7280 | 0.915 |
| `combo_max__max_up_ret__max_down_ret` | Cluster 26 | +1 | +0.1295 | +0.2069 | +0.2068 | 0.0002 | +0.7411 | +0.7563 | 0.903 |
| `combo_max__first_bar_return__early_order_flow_imbalance` | Cluster 17 | +1 | +0.1030 | +0.2063 | +0.2063 | 0.0002 | +0.4964 | +0.7080 | 0.915 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 23 | +1 | +0.1474 | +0.2062 | +0.2059 | 0.0002 | +0.6518 | +0.6915 | 0.916 |
| `combo_max__bar_ret_0__max_down_ret` | Cluster 33 | +1 | +0.1239 | +0.2061 | +0.2067 | 0.0002 | +0.5692 | +0.6879 | 0.863 |
| `combo_mean__max_up_ret__max_down_ret` | Cluster 27 | +1 | +0.1253 | +0.2057 | +0.2058 | 0.0002 | +0.6389 | +0.7162 | 0.886 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Cluster 18 | +1 | +0.1064 | +0.2056 | +0.2051 | 0.0002 | +0.7310 | +0.7388 | 0.901 |
| `max_up_ret` | Cluster 27 | +1 | +0.1293 | +0.2055 | +0.2058 | 0.0002 | +0.5418 | +0.6967 | 0.947 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 24 | +1 | +0.1381 | +0.2031 | +0.2036 | 0.0002 | +0.4159 | +0.6617 | 0.935 |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | Cluster 11 | +1 | +0.0947 | +0.2025 | +0.2013 | 0.0002 | +0.5587 | +0.6889 | 0.911 |
| `combo_mean__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Cluster 14 | +1 | +0.1203 | +0.2011 | +0.1998 | 0.0002 | +0.7666 | +0.7810 | 0.928 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 31 | +1 | +0.1454 | +0.1983 | +0.1986 | 0.0002 | +0.6091 | +0.7434 | 0.907 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Cluster 29 | +1 | +0.1078 | +0.1977 | +0.1978 | 0.0002 | +0.5549 | +0.6889 | 0.939 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 38 | +1 | +0.1286 | +0.1967 | +0.1957 | 0.0002 | +0.4497 | +0.6746 | 0.906 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | Cluster 13 | +1 | +0.1303 | +0.1952 | +0.1954 | 0.0002 | +0.6465 | +0.7116 | 0.907 |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | Cluster 32 | +1 | +0.1020 | +0.1951 | +0.1943 | 0.0002 | +0.5853 | +0.7213 | 0.854 |
| `combo_sig_product__first_bar_return__vwap_close_divergence_trend` | Cluster 39 | +1 | +0.1194 | +0.1948 | +0.1955 | 0.0002 | +0.5930 | +0.7265 | 0.713 |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | Cluster 32 | +1 | +0.1008 | +0.1920 | +0.1909 | 0.0002 | +0.5678 | +0.6807 | 0.769 |
| `combo_mean__first_bar_return__bar_body_rng_0` | Cluster 33 | +1 | +0.1187 | +0.1901 | +0.1909 | 0.0002 | +0.4700 | +0.6622 | 0.911 |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | Cluster 14 | +1 | +0.1134 | +0.1900 | +0.1885 | 0.0002 | +0.5594 | +0.6956 | 0.902 |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Cluster 13 | +1 | +0.1302 | +0.1896 | +0.1896 | 0.0002 | +0.7192 | +0.7527 | 0.912 |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | Cluster 14 | +1 | +0.1167 | +0.1889 | +0.1874 | 0.0002 | +0.5750 | +0.7003 | 0.895 |
| `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 30 | +1 | +0.0926 | +0.1871 | +0.1865 | 0.0002 | +0.4931 | +0.6540 | 0.871 |
| `combo_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 31 | +1 | +0.1482 | +0.1854 | +0.1856 | 0.0002 | +0.4382 | +0.6725 | 0.946 |
| `combo_sig_product__max_up_ret__first_bar_return` | Cluster 37 | +1 | +0.1181 | +0.1831 | +0.1835 | 0.0002 | +0.5083 | +0.7147 | 0.825 |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | Cluster 32 | +1 | +0.0973 | +0.1797 | +0.1783 | 0.0002 | +0.5613 | +0.7208 | 0.941 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | Cluster 29 | +1 | +0.1024 | +0.1751 | +0.1749 | 0.0002 | +0.4898 | +0.6740 | 0.910 |
| `combo_min__max_up_ret__max_down_ret` | Cluster 27 | +1 | +0.1170 | +0.1741 | +0.1743 | 0.0004 | +0.5132 | +0.6658 | 0.915 |
| `combo_rank_max__early_body_momentum__max_down_ret` | Cluster 29 | +1 | +0.0929 | +0.1738 | +0.1735 | 0.0006 | +0.4817 | +0.6807 | 0.903 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | Cluster 39 | +1 | +0.1004 | +0.1737 | +0.1729 | 0.0006 | +0.5541 | +0.6889 | 0.790 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 19 | +1 | +0.0825 | +0.1698 | +0.1698 | 0.0006 | +0.4848 | +0.6530 | 0.843 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Cluster 33 | +1 | +0.1243 | +0.1583 | +0.1587 | 0.0028 | +0.5563 | +0.6781 | 0.903 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 34 | +1 | +0.1446 | +0.3321 | +0.3316 | 0.0000 | +0.8369 | +0.8046 | 0.000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 18 | +1 | +0.1386 | +0.3042 | +0.3038 | 0.0000 | +0.8402 | +0.7871 | 0.948 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 32 | +1 | +0.1401 | +0.3031 | +0.3031 | 0.0000 | +0.7885 | +0.7830 | 0.944 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 18 | +1 | +0.1417 | +0.2964 | +0.2958 | 0.0000 | +0.7208 | +0.7635 | 0.880 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 6 | +1 | +0.1163 | +0.2933 | +0.2948 | 0.0000 | +0.7699 | +0.8231 | 0.394 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 30 | +1 | +0.1237 | +0.2883 | +0.2887 | 0.0000 | +0.8062 | +0.7825 | 0.925 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 31 | +1 | +0.1215 | +0.2816 | +0.2816 | 0.0000 | +0.7005 | +0.7326 | 0.948 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 30 | +1 | +0.1248 | +0.2816 | +0.2820 | 0.0000 | +0.8111 | +0.7969 | 0.829 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 32 | +1 | +0.1376 | +0.2786 | +0.2786 | 0.0000 | +0.6377 | +0.7033 | 0.944 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 18 | +1 | +0.1337 | +0.2780 | +0.2774 | 0.0000 | +0.9029 | +0.7907 | 0.939 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 34 | +1 | +0.1364 | +0.2778 | +0.2774 | 0.0000 | +0.7079 | +0.7728 | 0.948 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 29 | +1 | +0.1127 | +0.2752 | +0.2752 | 0.0000 | +0.9370 | +0.8329 | 0.949 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 11 | +1 | +0.1429 | +0.2656 | +0.2655 | 0.0000 | +0.5402 | +0.7378 | 0.828 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 40 | +1 | +0.1275 | +0.2633 | +0.2628 | 0.0000 | +0.5904 | +0.7285 | 0.932 |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | Cluster 30 | +1 | +0.1058 | +0.2630 | +0.2636 | 0.0000 | +0.7291 | +0.7697 | 0.947 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 11 | +1 | +0.1420 | +0.2614 | +0.2610 | 0.0000 | +0.5531 | +0.7157 | 0.946 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 17 | +1 | +0.1426 | +0.2609 | +0.2610 | 0.0000 | +0.6425 | +0.7465 | 0.912 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 33 | +1 | +0.1463 | +0.2595 | +0.2596 | 0.0000 | +0.5746 | +0.7023 | 0.942 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 29 | +1 | +0.1154 | +0.2593 | +0.2594 | 0.0000 | +0.7718 | +0.7697 | 0.880 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | Cluster 6 | +1 | +0.0893 | +0.2591 | +0.2613 | 0.0000 | +0.5949 | +0.7260 | 0.937 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 33 | +1 | +0.1429 | +0.2576 | +0.2579 | 0.0000 | +0.5650 | +0.7085 | 0.946 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 3 | +1 | +0.1211 | +0.2568 | +0.2560 | 0.0000 | +0.6197 | +0.7157 | 0.918 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 40 | +1 | +0.1141 | +0.2551 | +0.2551 | 0.0000 | +0.5473 | +0.7414 | 0.890 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 31 | +1 | +0.1289 | +0.2534 | +0.2535 | 0.0000 | +0.5981 | +0.7496 | 0.945 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 40 | +1 | +0.1141 | +0.2527 | +0.2525 | 0.0000 | +0.5762 | +0.7501 | 0.918 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0` | Cluster 8 | +1 | +0.1150 | +0.2504 | +0.2508 | 0.0000 | +0.7306 | +0.7630 | 0.940 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 17 | +1 | +0.1433 | +0.2473 | +0.2472 | 0.0000 | +0.6887 | +0.7733 | 0.908 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 4 | +1 | +0.1252 | +0.2465 | +0.2463 | 0.0000 | +0.5562 | +0.7090 | 0.921 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 33 | +1 | +0.1338 | +0.2465 | +0.2466 | 0.0000 | +0.5695 | +0.7136 | 0.935 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 7 | +1 | +0.1182 | +0.2437 | +0.2438 | 0.0000 | +0.6376 | +0.7434 | 0.765 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 8 | +1 | +0.1114 | +0.2434 | +0.2438 | 0.0000 | +0.6534 | +0.7116 | 0.934 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 23 | +1 | +0.1451 | +0.2412 | +0.2405 | 0.0000 | +0.5424 | +0.6853 | 0.925 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 4 | +1 | +0.1226 | +0.2391 | +0.2387 | 0.0000 | +0.5410 | +0.6982 | 0.943 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | Cluster 9 | +1 | +0.1113 | +0.2382 | +0.2378 | 0.0000 | +0.6681 | +0.7532 | 0.732 |
| `combo_mean__max_up_ret__gap_pct` | Cluster 7 | +1 | +0.1335 | +0.2374 | +0.2374 | 0.0000 | +0.5531 | +0.7105 | 0.944 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 30 | +1 | +0.1374 | +0.2370 | +0.2374 | 0.0000 | +0.4867 | +0.7141 | 0.854 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1316 | +0.2367 | +0.2367 | 0.0000 | +0.5131 | +0.7111 | 0.784 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Cluster 21 | +1 | +0.1144 | +0.2366 | +0.2358 | 0.0000 | +0.6928 | +0.7635 | 0.915 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Cluster 23 | +1 | +0.1466 | +0.2347 | +0.2333 | 0.0000 | +0.4665 | +0.6586 | 0.789 |
| `combo_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Cluster 27 | +1 | +0.1055 | +0.2328 | +0.2327 | 0.0000 | +0.8515 | +0.7959 | 0.912 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1285 | +0.2323 | +0.2320 | 0.0000 | +0.5676 | +0.6967 | 0.947 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Cluster 40 | +1 | +0.1284 | +0.2314 | +0.2314 | 0.0000 | +0.5021 | +0.7162 | 0.947 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0943 | +0.2306 | +0.2298 | 0.0000 | +0.5865 | +0.7054 | 0.858 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 21 | +1 | +0.1233 | +0.2300 | +0.2294 | 0.0000 | +0.6147 | +0.7722 | 0.934 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Cluster 38 | +1 | +0.1164 | +0.2292 | +0.2297 | 0.0000 | +0.5163 | +0.6961 | 0.850 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | Cluster 29 | +1 | +0.1202 | +0.2291 | +0.2294 | 0.0000 | +0.5616 | +0.7193 | 0.939 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | Cluster 27 | +1 | +0.1111 | +0.2283 | +0.2273 | 0.0000 | +0.6396 | +0.7429 | 0.929 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 41 | +1 | +0.1096 | +0.2273 | +0.2273 | 0.0000 | +0.6639 | +0.7568 | 0.816 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 6 | +1 | +0.1074 | +0.2266 | +0.2283 | 0.0000 | +0.6850 | +0.7609 | 0.844 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.0822 | +0.2228 | +0.2222 | 0.0000 | +0.5674 | +0.7558 | 0.893 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 12 | +1 | +0.1245 | +0.2224 | +0.2216 | 0.0000 | +0.5352 | +0.7090 | 0.939 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Cluster 37 | +1 | +0.1358 | +0.2219 | +0.2208 | 0.0000 | +0.6322 | +0.7044 | 0.792 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 10 | +1 | +0.1304 | +0.2209 | +0.2206 | 0.0000 | +0.5474 | +0.7193 | 0.907 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 8 | +1 | +0.1113 | +0.2208 | +0.2210 | 0.0000 | +0.5476 | +0.6889 | 0.933 |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Cluster 38 | +1 | +0.1105 | +0.2202 | +0.2198 | 0.0000 | +0.5264 | +0.6864 | 0.847 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 4 | +1 | +0.1155 | +0.2197 | +0.2191 | 0.0000 | +0.4703 | +0.6931 | 0.910 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 24 | +1 | +0.1341 | +0.2177 | +0.2174 | 0.0000 | +0.5316 | +0.6823 | 0.936 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Cluster 4 | +1 | +0.1169 | +0.2171 | +0.2172 | 0.0000 | +0.4379 | +0.6869 | 0.926 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 35 | +1 | +0.1198 | +0.2164 | +0.2150 | 0.0000 | +0.6634 | +0.7234 | 0.828 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 1 | +1 | +0.1027 | +0.2161 | +0.2154 | 0.0000 | +0.5306 | +0.7198 | 0.886 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 19 | +1 | +0.1225 | +0.2142 | +0.2137 | 0.0000 | +0.4915 | +0.6946 | 0.937 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 21 | +1 | +0.1146 | +0.2133 | +0.2125 | 0.0000 | +0.5311 | +0.6997 | 0.940 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 24 | +1 | +0.1336 | +0.2131 | +0.2128 | 0.0000 | +0.4982 | +0.6602 | 0.890 |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 41 | +1 | +0.1126 | +0.2122 | +0.2120 | 0.0000 | +0.5807 | +0.7265 | 0.894 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 35 | +1 | +0.1202 | +0.2120 | +0.2109 | 0.0000 | +0.6500 | +0.7126 | 0.927 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Cluster 24 | +1 | +0.1166 | +0.2096 | +0.2094 | 0.0002 | +0.5049 | +0.6843 | 0.899 |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__star50_limit_proximity_early` | Cluster 26 | +1 | +0.0969 | +0.2088 | +0.2082 | 0.0002 | +0.5324 | +0.6961 | 0.852 |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Cluster 39 | +1 | +0.1230 | +0.2075 | +0.2073 | 0.0002 | +0.5591 | +0.7275 | 0.856 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 24 | +1 | +0.1233 | +0.2067 | +0.2063 | 0.0002 | +0.4414 | +0.6514 | 0.925 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Cluster 39 | +1 | +0.1406 | +0.2053 | +0.2055 | 0.0002 | +0.3945 | +0.6550 | 0.891 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Cluster 25 | +1 | +0.1100 | +0.2049 | +0.2033 | 0.0002 | +0.6088 | +0.7388 | 0.851 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 28 | +1 | +0.1024 | +0.2033 | +0.2038 | 0.0002 | +0.4871 | +0.7039 | 0.620 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 14 | +1 | +0.1133 | +0.2020 | +0.2013 | 0.0002 | +0.4436 | +0.6550 | 0.882 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | Cluster 23 | +1 | +0.1286 | +0.2013 | +0.2015 | 0.0002 | +0.4080 | +0.6622 | 0.871 |
| `combo_rank_min__max_up_ret__gap_pct` | Cluster 0 | +1 | +0.0974 | +0.2010 | +0.2004 | 0.0002 | +0.5232 | +0.7111 | 0.810 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | Cluster 42 | +1 | +0.1204 | +0.2005 | +0.1997 | 0.0002 | +0.5668 | +0.6874 | 0.779 |
| `combo_max__max_up_ret__volume_price_confirmation` | Cluster 36 | +1 | +0.1185 | +0.1997 | +0.1993 | 0.0002 | +0.6937 | +0.7234 | 0.879 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 3 | +1 | +0.1172 | +0.1994 | +0.1984 | 0.0002 | +0.5191 | +0.6828 | 0.922 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | Cluster 16 | +1 | +0.0990 | +0.1941 | +0.1945 | 0.0002 | +0.4687 | +0.6972 | 0.938 |
| `combo_tri_max__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 28 | +1 | +0.0973 | +0.1939 | +0.1944 | 0.0002 | +0.5835 | +0.7033 | 0.942 |
| `combo_tri_median__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 6 | +1 | +0.0938 | +0.1936 | +0.1952 | 0.0002 | +0.4319 | +0.6776 | 0.918 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | Cluster 16 | +1 | +0.1068 | +0.1935 | +0.1935 | 0.0002 | +0.5257 | +0.7249 | 0.601 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 8 | +1 | +0.1000 | +0.1933 | +0.1933 | 0.0002 | +0.4887 | +0.6853 | 1.000 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | Cluster 42 | +1 | +0.1040 | +0.1926 | +0.1920 | 0.0002 | +0.5388 | +0.6864 | 0.948 |
| `combo_mean__first_bar_return__limit_down_proximity_early` | Cluster 33 | +1 | +0.1180 | +0.1912 | +0.1915 | 0.0002 | +0.5125 | +0.6771 | 0.946 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | Cluster 8 | +1 | +0.0946 | +0.1899 | +0.1902 | 0.0002 | +0.5843 | +0.6797 | 0.946 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 15 | +1 | +0.1100 | +0.1884 | +0.1879 | 0.0002 | +0.5029 | +0.6684 | 0.941 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | Cluster 20 | +1 | +0.0984 | +0.1884 | +0.1897 | 0.0002 | +0.5443 | +0.7039 | 0.754 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | Cluster 26 | +1 | +0.1073 | +0.1875 | +0.1867 | 0.0002 | +0.5970 | +0.7193 | 0.948 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Cluster 15 | +1 | +0.1094 | +0.1871 | +0.1869 | 0.0002 | +0.5686 | +0.6776 | 0.872 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1011 | +0.1870 | +0.1861 | 0.0002 | +0.4876 | +0.6956 | 0.919 |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 29 | +1 | +0.1018 | +0.1854 | +0.1852 | 0.0002 | +0.4445 | +0.6787 | 0.914 |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | Cluster 20 | +1 | +0.0978 | +0.1847 | +0.1859 | 0.0004 | +0.4947 | +0.6905 | 0.940 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | Cluster 5 | +1 | +0.1103 | +0.1777 | +0.1776 | 0.0010 | +0.3683 | +0.6643 | 0.890 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 13 | +1 | +0.0974 | +0.1774 | +0.1767 | 0.0010 | +0.3693 | +0.6560 | 0.895 |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 36 | +1 | +0.1093 | +0.1684 | +0.1678 | 0.0016 | +0.3993 | +0.6864 | 0.829 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 2 | +1 | +0.0757 | +0.1664 | +0.1661 | 0.0018 | +0.4012 | +0.6586 | 0.884 |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | Cluster 24 | +1 | +0.1100 | +0.1534 | +0.1532 | 0.0032 | +0.4487 | +0.6766 | 0.884 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 14 | +1 | +0.0916 | +0.1458 | +0.1452 | 0.0050 | +0.3306 | +0.6710 | 0.876 |

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
| 300ETF | single | 37 | 17 | 0.2366 | `[4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, ... (17 clusters)]` |
| 500ETF | single | 111 | 41 | 0.2278 | `[8, 8, 7, 6, 6, 6, 5, 4, 4, 3, 3, 3, ... (41 clusters)]` |
| 159915ETF | single | 99 | 43 | 0.3217 | `[5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 2, ... (43 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 1 | 0.2366 | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 1 | 2 | 0.2366 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 2 | 2 | 0.2366 | `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 3 | 1 | 0.2366 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 4 | 2 | 0.2366 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_median__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 5 | 2 | 0.2366 | `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` |
| 300ETF | single | Cluster 6 | 3 | 0.2366 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 300ETF | single | Cluster 7 | 1 | 0.2366 | `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | _(none)_ |
| 300ETF | single | Cluster 8 | 1 | 0.2366 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | _(none)_ |
| 300ETF | single | Cluster 9 | 4 | 0.2366 | `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early`, `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` |
| 300ETF | single | Cluster 10 | 3 | 0.2366 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0` |
| 300ETF | single | Cluster 11 | 2 | 0.2366 | `combo_max__max_up_ret__bar_ret_0` | `combo_tri_median__max_up_ret__bar_body_rng_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 12 | 2 | 0.2366 | `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | `combo_min__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 13 | 3 | 0.2366 | `combo_mean__bar_body_rng_0__volume_weighted_price_position` | `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position`, `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 14 | 2 | 0.2366 | `combo_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 15 | 2 | 0.2366 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `combo_mean__star50_limit_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 16 | 4 | 0.2366 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_min__bar_body_rng_0__limit_down_proximity_early` |
| 500ETF | single | Cluster 0 | 8 | 0.2278 | `combo_rel_diff__max_up_ret__body_size_progression` | `combo_diff__max_up_ret__body_size_progression`, `combo_clamp_diff__max_up_ret__body_size_progression`, `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_clamp_diff__bar_ret_0__body_size_progression`, `combo_clamp_diff__max_up_ret__smooth_momentum_structure` |
| 500ETF | single | Cluster 1 | 2 | 0.2278 | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` |
| 500ETF | single | Cluster 2 | 2 | 0.2278 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` |
| 500ETF | single | Cluster 3 | 2 | 0.2278 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__bar_ret_0` |
| 500ETF | single | Cluster 4 | 1 | 0.2278 | `combo_diff__max_up_ret__demark_setup_reversal_early` | _(none)_ |
| 500ETF | single | Cluster 5 | 6 | 0.2278 | `combo_rank_max__early_body_momentum__bar_ret_0` | `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0`, `combo_max__early_body_momentum__first_bar_return`, `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0`, `combo_rank_max__first_bar_return__close_vs_open_range`, `combo_max__first_bar_return__close_vs_open_range` |
| 500ETF | single | Cluster 6 | 2 | 0.2278 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 7 | 1 | 0.2278 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 8 | 2 | 0.2278 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 500ETF | single | Cluster 9 | 4 | 0.2278 | `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_tri_mean__early_body_momentum__star50_limit_proximity_early__trend_day_regime_conviction`, `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range`, `combo_mean__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 10 | 1 | 0.2278 | `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 11 | 2 | 0.2278 | `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | `combo_min__max_up_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 12 | 2 | 0.2278 | `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` |
| 500ETF | single | Cluster 13 | 2 | 0.2278 | `combo_max__max_up_ret__vwap_close_divergence_trend` | `combo_rank_max__max_up_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 14 | 3 | 0.2278 | `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation`, `combo_mean__opening_drive_thrust_ratio__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 15 | 2 | 0.2278 | `combo_rank_max__max_up_ret__early_body_momentum` | `combo_tri_max__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 16 | 1 | 0.2278 | `combo_mean__max_up_ret__volatility_expansion_trend_vector` | _(none)_ |
| 500ETF | single | Cluster 17 | 1 | 0.2278 | `combo_max__first_bar_return__early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 18 | 2 | 0.2278 | `combo_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 19 | 1 | 0.2278 | `combo_mean__star50_limit_proximity_early__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 20 | 1 | 0.2278 | `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 21 | 2 | 0.2278 | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 22 | 2 | 0.2278 | `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | `combo_diff__first_bar_return__demark_setup_reversal_early` |
| 500ETF | single | Cluster 23 | 2 | 0.2278 | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 24 | 2 | 0.2278 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 25 | 2 | 0.2278 | `combo_tri_median__volatility_expansion_trend_vector__star50_limit_proximity_early__bar_ret_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` |
| 500ETF | single | Cluster 26 | 1 | 0.2278 | `combo_max__max_up_ret__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 27 | 8 | 0.2278 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `combo_min__opening_drive_thrust_ratio__max_up_ret`, `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`, `combo_mean__max_up_ret__max_down_ret`, `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`, `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_min__max_up_ret__max_down_ret`, `max_up_ret` |
| 500ETF | single | Cluster 28 | 2 | 0.2278 | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` |
| 500ETF | single | Cluster 29 | 7 | 0.2278 | `combo_min__net_volume_flow__vwap_close_divergence_trend` | `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure`, `combo_rank_min__net_volume_flow__close_vs_open_range`, `combo_min__net_volume_flow__close_vs_open_range`, `combo_rank_max__early_body_momentum__max_down_ret`, `combo_mean__volatility_expansion_trend_vector__max_down_ret`, `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` |
| 500ETF | single | Cluster 30 | 4 | 0.2278 | `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | `combo_min__volatility_expansion_trend_vector__bar_ret_0`, `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0`, `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` |
| 500ETF | single | Cluster 31 | 6 | 0.2278 | `combo_mean__max_up_ret__bar_body_rng_0` | `combo_min__max_up_ret__bar_body_rng_0`, `combo_max__max_up_ret__first_bar_return`, `combo_rank_max__max_up_ret__first_bar_return`, `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`, `combo_max__opening_drive_thrust_ratio__first_bar_return` |
| 500ETF | single | Cluster 32 | 5 | 0.2278 | `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | `combo_min__max_down_ret__vwap_close_divergence_trend`, `combo_min__close_vs_open_range__vwap_close_divergence_trend`, `combo_rank_min__max_down_ret__vwap_close_divergence_trend`, `combo_mean__max_down_ret__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 33 | 3 | 0.2278 | `combo_max__bar_ret_0__max_down_ret` | `combo_mean__first_bar_return__bar_body_rng_0`, `combo_rank_max__bar_ret_0__max_down_ret` |
| 500ETF | single | Cluster 34 | 1 | 0.2278 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 500ETF | single | Cluster 35 | 3 | 0.2278 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`, `combo_tri_min__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` |
| 500ETF | single | Cluster 36 | 2 | 0.2278 | `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 37 | 2 | 0.2278 | `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | `combo_sig_product__max_up_ret__first_bar_return` |
| 500ETF | single | Cluster 38 | 1 | 0.2278 | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 500ETF | single | Cluster 39 | 2 | 0.2278 | `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | `combo_sig_product__first_bar_return__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 40 | 6 | 0.2278 | `combo_tri_median__max_up_ret__net_volume_flow__bar_ret_0` | `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0`, `combo_mean__net_volume_flow__first_bar_return`, `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0`, `combo_mean__first_bar_return__close_vs_open_range`, `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` |
| 159915ETF | single | Cluster 0 | 1 | 0.3217 | `combo_rank_min__max_up_ret__gap_pct` | _(none)_ |
| 159915ETF | single | Cluster 1 | 2 | 0.3217 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 159915ETF | single | Cluster 2 | 1 | 0.3217 | `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 3 | 2 | 0.3217 | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `combo_min__opening_drive_thrust_ratio__bar_ret_0` |
| 159915ETF | single | Cluster 4 | 4 | 0.3217 | `combo_mean__max_up_ret__bar_body_rng_0` | `combo_rank_max__max_up_ret__bar_body_rng_0`, `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`, `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` |
| 159915ETF | single | Cluster 5 | 1 | 0.3217 | `combo_max__first_bar_return__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 6 | 4 | 0.3217 | `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `combo_tri_mean__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`, `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend`, `combo_tri_median__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` |
| 159915ETF | single | Cluster 7 | 2 | 0.3217 | `combo_mean__max_up_ret__gap_pct` | `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 8 | 5 | 0.3217 | `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0` | `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_min__bar_body_rng_0__limit_down_proximity_early`, `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_min__bar_ret_0__limit_down_proximity_early` |
| 159915ETF | single | Cluster 9 | 2 | 0.3217 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 10 | 2 | 0.3217 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 11 | 2 | 0.3217 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 12 | 1 | 0.3217 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | _(none)_ |
| 159915ETF | single | Cluster 13 | 1 | 0.3217 | `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 14 | 2 | 0.3217 | `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 15 | 2 | 0.3217 | `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 16 | 2 | 0.3217 | `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` |
| 159915ETF | single | Cluster 17 | 2 | 0.3217 | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 18 | 3 | 0.3217 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` |
| 159915ETF | single | Cluster 19 | 1 | 0.3217 | `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 20 | 2 | 0.3217 | `combo_diff__max_up_ret__keltner_squeeze_width` | `combo_clamp_diff__max_up_ret__keltner_squeeze_width` |
| 159915ETF | single | Cluster 21 | 3 | 0.3217 | `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 22 | 2 | 0.3217 | `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 23 | 3 | 0.3217 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`, `combo_clamp_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` |
| 159915ETF | single | Cluster 24 | 5 | 0.3217 | `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0`, `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 25 | 1 | 0.3217 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | _(none)_ |
| 159915ETF | single | Cluster 26 | 2 | 0.3217 | `combo_tri_median__max_up_ret__demark_setup_reversal_early__star50_limit_proximity_early` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 27 | 2 | 0.3217 | `combo_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 28 | 2 | 0.3217 | `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `combo_tri_max__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return` |
| 159915ETF | single | Cluster 29 | 4 | 0.3217 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early`, `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 30 | 4 | 0.3217 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`, `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`, `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 31 | 2 | 0.3217 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 32 | 2 | 0.3217 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 33 | 4 | 0.3217 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_mean__first_bar_return__limit_down_proximity_early` |
| 159915ETF | single | Cluster 34 | 2 | 0.3217 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` |
| 159915ETF | single | Cluster 35 | 2 | 0.3217 | `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` |
| 159915ETF | single | Cluster 36 | 2 | 0.3217 | `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | `combo_max__max_up_ret__volume_price_confirmation` |
| 159915ETF | single | Cluster 37 | 1 | 0.3217 | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | _(none)_ |
| 159915ETF | single | Cluster 38 | 2 | 0.3217 | `combo_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` |
| 159915ETF | single | Cluster 39 | 2 | 0.3217 | `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` |
| 159915ETF | single | Cluster 40 | 4 | 0.3217 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `combo_mean__max_up_ret__star50_limit_proximity_early`, `combo_diff__max_up_ret__demark_setup_reversal_early`, `combo_rel_diff__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 41 | 2 | 0.3217 | `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` |
| 159915ETF | single | Cluster 42 | 2 | 0.3217 | `combo_tri_median__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | `tri_max` | a=`first_bar_return`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_concentration` |
| `combo_tri_median__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_median` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | `mean` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`limit_down_proximity_early` |
| `combo_tri_median__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | `tri_median` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_median` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_ret_0` |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | `rank_max` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`morning_volume_weighted_momentum` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | `tri_max` | a=`max_up_ret`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`early_body_momentum` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency`, c=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | `mean` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_clamp_diff__bar_ret_0__body_size_progression` | `clamp_diff` | a=`bar_ret_0`, b=`body_size_progression` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`smooth_momentum_structure` |
| `combo_min__net_volume_flow__close_vs_open_range` | `min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`net_volume_flow` |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | `mean` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_max__early_body_momentum__first_bar_return` | `max` | a=`early_body_momentum`, b=`first_bar_return` |
| `combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | `clamp_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | `rank_min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | `rel_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_rank_min__volatility_expansion_trend_vector__vwap_close_divergence_trend` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`vwap_close_divergence_trend` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`bar_ret_0` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | `diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | `rel_diff` | a=`max_up_ret`, b=`h2_l2_pullback_continuation` |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | `tri_min` | a=`max_up_ret`, b=`net_volume_flow`, c=`bar_ret_0` |
| `combo_mean__net_volume_flow__first_bar_return` | `mean` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_min__volatility_expansion_trend_vector__bar_ret_0` | `min` | a=`volatility_expansion_trend_vector`, b=`bar_ret_0` |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | `tri_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | `tri_min` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`trend_day_regime_conviction` |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__early_body_momentum__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_max__first_bar_return__close_vs_open_range` | `max` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_tri_median__max_up_ret__net_volume_flow__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`net_volume_flow`, c=`bar_ret_0` |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | `min` | a=`net_volume_flow`, b=`vwap_close_divergence_trend` |
| `combo_tri_max__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_max` | a=`max_up_ret`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_max__max_up_ret__first_bar_return` | `max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_mean__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_tri_median__volatility_expansion_trend_vector__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`volatility_expansion_trend_vector`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_median` | a=`max_up_ret`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_rank_max__first_bar_return__close_vs_open_range` | `rank_max` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_tri_mean__early_body_momentum__star50_limit_proximity_early__trend_day_regime_conviction` | `tri_mean` | a=`early_body_momentum`, b=`star50_limit_proximity_early`, c=`trend_day_regime_conviction` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__first_bar_return__close_vs_open_range` | `mean` | a=`first_bar_return`, b=`close_vs_open_range` |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | `min` | a=`close_vs_open_range`, b=`vwap_close_divergence_trend` |
| `combo_max__max_up_ret__max_down_ret` | `max` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_max__first_bar_return__early_order_flow_imbalance` | `max` | a=`first_bar_return`, b=`early_order_flow_imbalance` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_mean__max_up_ret__max_down_ret` | `mean` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`vwap_close_divergence_trend` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | `min` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__opening_drive_thrust_ratio__vwap_close_divergence_trend` | `mean` | a=`opening_drive_thrust_ratio`, b=`vwap_close_divergence_trend` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | `rank_max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | `rank_min` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__first_bar_return__vwap_close_divergence_trend` | `sig_product` | a=`first_bar_return`, b=`vwap_close_divergence_trend` |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | `min` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__first_bar_return__bar_body_rng_0` | `mean` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`h2_l2_pullback_continuation` |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | `max` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | `diff` | a=`opening_drive_thrust_ratio`, b=`h2_l2_pullback_continuation` |
| `combo_rank_min__vwap_close_divergence_trend__bar_body_rng_0` | `rank_min` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_max__opening_drive_thrust_ratio__first_bar_return` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__first_bar_return` | `sig_product` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | `mean` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | `mean` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_min__max_up_ret__max_down_ret` | `min` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_rank_max__early_body_momentum__max_down_ret` | `rank_max` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, cond=`gap_pct` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | `rank_min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | `tri_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_trend` |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`demark_setup_reversal_early` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early`, c=`bar_body_rng_0` |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`gap_pct` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | `mean` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_price_confirmation` |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | `ifelse` | a=`max_up_ret`, b=`star50_limit_proximity_early`, cond=`gap_pct` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`demark_setup_reversal_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_mean` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `rank_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`demark_setup_reversal_early` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`directional_volume_signature` |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__star50_limit_proximity_early` | `tri_median` | a=`max_up_ret`, b=`demark_setup_reversal_early`, c=`star50_limit_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`directional_volume_signature` |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_price_confirmation` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`demark_setup_reversal_early` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`late_bar_momentum` |
| `combo_rank_min__max_up_ret__gap_pct` | `rank_min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early`, c=`bar_body_rng_0` |
| `combo_max__max_up_ret__volume_price_confirmation` | `max` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_tri_max__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return` | `tri_max` | a=`yesterday_early_momentum`, b=`star50_limit_proximity_early`, c=`yesterday_first_30min_return` |
| `combo_tri_median__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_median` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_trend`, cond=`gap_pct` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`demark_setup_reversal_early`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_mean__first_bar_return__limit_down_proximity_early` | `mean` | a=`first_bar_return`, b=`limit_down_proximity_early` |
| `combo_min__bar_ret_0__limit_down_proximity_early` | `min` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | `ifelse` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, cond=`gap_pct` |
| `combo_diff__max_up_ret__keltner_squeeze_width` | `diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`demark_setup_reversal_early` |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `rank_max` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | `clamp_diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | `max` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | `rank_max` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `min` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | `max` | a=`first_bar_return`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
