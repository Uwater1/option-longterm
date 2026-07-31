# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2018_2026`

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
| 300ETF | single | 1,593 | 572 | 469 | 392 | 390 | 383 | 382 | 381 | 123 | 99 | 26 | `[17, 10, 9, 8, 7, 4, 3, 3, 3, 3, 3, 2, ... (26 clusters)]` |
| 50ETF | single | 1,244 | 435 | 360 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 3,059 | 1,138 | 882 | 781 | 779 | 723 | 541 | 541 | 148 | 126 | 50 | `[9, 8, 7, 6, 5, 5, 4, 3, 3, 3, 3, 3, ... (50 clusters)]` |
| 159915ETF | single | 1,919 | 840 | 661 | 619 | 618 | 548 | 483 | 483 | 178 | 146 | 53 | `[12, 10, 8, 8, 7, 7, 6, 6, 5, 4, 3, 2, ... (53 clusters)]` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 99 | 26 | `[17, 10, 9, 8, 7, 4, 3, 3, 3, 3, 3, 2, ... (26 clusters)]` | +0.1101 | [+0.0633, +0.1564] | +0.2551 | [+0.1546, +0.3562] | +0.8545 | 5.77% | 1.6754 | 4.23% | 1.2505 | 2.8761 | 2.55% |
| 500ETF | single | 126 | 50 | `[9, 8, 7, 6, 5, 5, 4, 3, 3, 3, 3, 3, ... (50 clusters)]` | +0.1423 | [+0.0978, +0.1849] | +0.2386 | [+0.1454, +0.3379] | +0.8182 | 5.99% | 1.5652 | 4.43% | 1.1681 | 2.1006 | 3.09% |
| 159915ETF | single | 146 | 53 | `[12, 10, 8, 8, 7, 7, 6, 6, 5, 4, 3, 2, ... (53 clusters)]` | +0.1552 | [+0.1151, +0.2029] | +0.3198 | [+0.2322, +0.3989] | +0.8182 | 9.28% | 1.8912 | 7.72% | 1.5957 | 3.8764 | 2.21% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 99 | 26 | `[17, 10, 9, 8, 7, 4, 3, 3, 3, 3, 3, 2, ... (26 clusters)]` | -0.1046* | [-0.3517, +0.0826] | -0.1183* | [-0.6637, +0.2192] | -0.4909 | -2.67% | -1.1366 | -3.99% | -1.6643 | -1.9176 | 3.74% |
| 500ETF | single | 126 | 50 | `[9, 8, 7, 6, 5, 5, 4, 3, 3, 3, 3, 3, ... (50 clusters)]` | +0.0110* | [-0.1703, +0.1155] | -0.0948* | [-0.4817, +0.2409] | -0.0909 | -0.22% | -0.0524 | -1.62% | -0.3896 | -0.5145 | 3.62% |
| 159915ETF | single | 146 | 53 | `[12, 10, 8, 8, 7, 7, 6, 6, 5, 4, 3, 2, ... (53 clusters)]` | +0.0378* | [-0.2525, +0.2756] | -0.1470* | [-0.7166, +0.2418] | +0.1515 | -3.29% | -0.6114 | -4.72% | -0.8772 | -1.1344 | 5.67% |

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
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1074 | +0.2637 | +0.2645 | 0.0000 | +0.7047 | +0.7477 | 0.974 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 9 | +1 | +0.1039 | +0.2621 | +0.2635 | 0.0000 | +0.7588 | +0.7724 | 1.000 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Cluster 6 | +1 | +0.0945 | +0.2509 | +0.2514 | 0.0000 | +0.7715 | +0.7683 | 0.973 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 6 | +1 | +0.1034 | +0.2501 | +0.2501 | 0.0000 | +0.8571 | +0.8208 | 1.000 |
| `combo_max__bar_ret_0__volume_surge_direction` | Cluster 6 | +1 | +0.0860 | +0.2473 | +0.2480 | 0.0000 | +0.8672 | +0.8033 | 0.870 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1074 | +0.2454 | +0.2463 | 0.0000 | +0.7545 | +0.7621 | 0.924 |
| `combo_rank_max__first_bar_return__volume_surge_direction` | Cluster 6 | +1 | +0.0809 | +0.2445 | +0.2454 | 0.0000 | +0.8031 | +0.8033 | 0.926 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 9 | +1 | +0.0923 | +0.2353 | +0.2367 | 0.0000 | +0.6402 | +0.7436 | 0.944 |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 0 | +1 | +0.1032 | +0.2345 | +0.2349 | 0.0000 | +0.8240 | +0.7961 | 0.871 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 1 | +1 | +0.0974 | +0.2339 | +0.2337 | 0.0000 | +0.6081 | +0.7415 | 0.858 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 2 | +1 | +0.0944 | +0.2303 | +0.2293 | 0.0000 | +0.8055 | +0.7858 | 1.000 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 21 | +1 | +0.0937 | +0.2301 | +0.2290 | 0.0000 | +0.7485 | +0.7559 | 0.821 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.1002 | +0.2257 | +0.2261 | 0.0000 | +0.5684 | +0.7127 | 0.999 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 6 | +1 | +0.0851 | +0.2251 | +0.2262 | 0.0000 | +0.7366 | +0.7930 | 0.866 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 6 | +1 | +0.0971 | +0.2235 | +0.2233 | 0.0000 | +0.7346 | +0.7781 | 0.950 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 5 | +1 | +0.0961 | +0.2233 | +0.2238 | 0.0000 | +0.7261 | +0.7868 | 1.000 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0904 | +0.2228 | +0.2225 | 0.0000 | +0.6862 | +0.7832 | 0.657 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.1000 | +0.2224 | +0.2226 | 0.0000 | +0.6458 | +0.7276 | 0.906 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | Cluster 0 | +1 | +0.0837 | +0.2219 | +0.2217 | 0.0000 | +0.7849 | +0.7533 | 0.910 |
| `combo_tri_mean__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1008 | +0.2218 | +0.2214 | 0.0000 | +0.7626 | +0.7533 | 0.950 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 0 | +1 | +0.0938 | +0.2212 | +0.2216 | 0.0000 | +0.8566 | +0.7997 | 0.907 |
| `combo_max__first_bar_return__bar_body_rng_0` | Cluster 6 | +1 | +0.0923 | +0.2212 | +0.2212 | 0.0000 | +0.7112 | +0.7817 | 0.938 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 11 | +1 | +0.0942 | +0.2207 | +0.2205 | 0.0000 | +0.6285 | +0.7188 | 0.944 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0985 | +0.2195 | +0.2191 | 0.0000 | +0.6511 | +0.7255 | 0.928 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 20 | +1 | +0.1030 | +0.2194 | +0.2192 | 0.0000 | +0.6144 | +0.7667 | 0.917 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 17 | +1 | +0.1095 | +0.2192 | +0.2193 | 0.0000 | +0.6639 | +0.7152 | 0.994 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 20 | +1 | +0.1033 | +0.2181 | +0.2181 | 0.0000 | +0.6035 | +0.7400 | 0.950 |
| `combo_max__max_up_ret__volume_surge_direction` | Cluster 0 | +1 | +0.0844 | +0.2178 | +0.2176 | 0.0000 | +0.7444 | +0.7441 | 0.948 |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Cluster 20 | +1 | +0.1005 | +0.2166 | +0.2163 | 0.0000 | +0.7013 | +0.7570 | 0.949 |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 22 | +1 | +0.1125 | +0.2165 | +0.2165 | 0.0000 | +0.6151 | +0.6926 | 0.994 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1018 | +0.2156 | +0.2157 | 0.0000 | +0.5675 | +0.7420 | 0.940 |
| `combo_tri_median__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0956 | +0.2155 | +0.2156 | 0.0000 | +0.6827 | +0.7415 | 1.000 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Cluster 16 | +1 | +0.0876 | +0.2146 | +0.2147 | 0.0000 | +0.5939 | +0.7523 | 0.908 |
| `combo_tri_min__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Cluster 10 | +1 | +0.0943 | +0.2142 | +0.2141 | 0.0000 | +0.6646 | +0.7724 | 0.950 |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | Cluster 25 | +1 | +0.0817 | +0.2142 | +0.2140 | 0.0000 | +0.8127 | +0.8208 | 0.796 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 6 | +1 | +0.0867 | +0.2138 | +0.2139 | 0.0000 | +0.7377 | +0.7678 | 0.875 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1048 | +0.2135 | +0.2135 | 0.0000 | +0.6151 | +0.7255 | 0.919 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 0 | +1 | +0.0977 | +0.2133 | +0.2139 | 0.0000 | +0.8173 | +0.7904 | 0.941 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Cluster 9 | +1 | +0.0913 | +0.2116 | +0.2114 | 0.0000 | +0.5574 | +0.7137 | 0.948 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 9 | +1 | +0.0963 | +0.2113 | +0.2119 | 0.0000 | +0.5218 | +0.7147 | 0.918 |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | Cluster 11 | +1 | +0.0911 | +0.2113 | +0.2111 | 0.0000 | +0.5991 | +0.7271 | 0.942 |
| `combo_max__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 0 | +1 | +0.0975 | +0.2104 | +0.2107 | 0.0000 | +0.7304 | +0.7312 | 0.970 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 17 | +1 | +0.1034 | +0.2099 | +0.2098 | 0.0000 | +0.6253 | +0.7384 | 0.928 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 21 | +1 | +0.0972 | +0.2092 | +0.2083 | 0.0000 | +0.6724 | +0.7513 | 0.948 |
| `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.1000 | +0.2090 | +0.2095 | 0.0000 | +0.7667 | +0.7858 | 0.940 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 22 | +1 | +0.1099 | +0.2078 | +0.2076 | 0.0000 | +0.5938 | +0.7513 | 1.000 |
| `combo_mean__max_up_ret__bar_ret_0` | Cluster 21 | +1 | +0.0922 | +0.2048 | +0.2045 | 0.0000 | +0.6366 | +0.7173 | 1.000 |
| `combo_tri_mean__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1029 | +0.2040 | +0.2039 | 0.0000 | +0.7996 | +0.7904 | 0.942 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 2 | +1 | +0.0882 | +0.2038 | +0.2027 | 0.0000 | +0.9050 | +0.8234 | 0.900 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1050 | +0.2009 | +0.2009 | 0.0000 | +0.5688 | +0.7019 | 0.950 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 5 | +1 | +0.1005 | +0.2009 | +0.2012 | 0.0000 | +0.7022 | +0.7667 | 0.947 |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.0866 | +0.2001 | +0.2005 | 0.0000 | +0.7275 | +0.7729 | 0.862 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0941 | +0.1986 | +0.1980 | 0.0000 | +0.6913 | +0.7564 | 0.912 |
| `opening_drive_thrust_ratio` | Cluster 16 | +1 | +0.0982 | +0.1983 | +0.1985 | 0.0000 | +0.6753 | +0.7580 | 0.928 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0945 | +0.1976 | +0.1966 | 0.0000 | +0.7579 | +0.7899 | 0.940 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0937 | +0.1968 | +0.1971 | 0.0000 | +0.6028 | +0.7188 | 0.802 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 1 | +1 | +0.0918 | +0.1943 | +0.1946 | 0.0000 | +0.5187 | +0.6849 | 0.850 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | Cluster 14 | +1 | +0.0713 | +0.1930 | +0.1922 | 0.0000 | +0.5977 | +0.7173 | 0.820 |
| `combo_rank_min__max_up_ret__first_bar_return` | Cluster 6 | +1 | +0.0802 | +0.1919 | +0.1927 | 0.0000 | +0.5219 | +0.7271 | 0.949 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 3 | +1 | +0.0941 | +0.1910 | +0.1908 | 0.0002 | +0.7407 | +0.7312 | 0.939 |
| `combo_rank_min__max_up_ret__volume_surge_direction` | Cluster 0 | +1 | +0.0880 | +0.1903 | +0.1911 | 0.0002 | +0.5746 | +0.7060 | 0.912 |
| `combo_max__first_bar_return__first_bar_sentiment` | Cluster 6 | +1 | +0.0874 | +0.1903 | +0.1903 | 0.0002 | +0.6211 | +0.7533 | 0.972 |
| `combo_min__max_up_ret__volume_surge_direction` | Cluster 0 | +1 | +0.0889 | +0.1895 | +0.1903 | 0.0002 | +0.5544 | +0.6854 | 0.929 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0958 | +0.1891 | +0.1890 | 0.0002 | +0.5914 | +0.7199 | 0.950 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 6 | +1 | +0.0894 | +0.1875 | +0.1880 | 0.0004 | +0.5795 | +0.7209 | 0.921 |
| `combo_min__bar_ret_0__volume_surge_direction` | Cluster 6 | +1 | +0.0837 | +0.1874 | +0.1875 | 0.0004 | +0.5746 | +0.6859 | 0.947 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0866 | +0.1853 | +0.1848 | 0.0004 | +0.5632 | +0.7039 | 1.000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0937 | +0.1844 | +0.1844 | 0.0004 | +0.4872 | +0.6859 | 1.000 |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | Cluster 13 | +1 | +0.0771 | +0.1817 | +0.1814 | 0.0004 | +0.6709 | +0.7338 | 0.989 |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | Cluster 14 | +1 | +0.1053 | +0.1814 | +0.1819 | 0.0004 | +0.4878 | +0.6612 | 0.780 |
| `combo_rank_max__volume_weighted_price_position__volume_surge_direction` | Cluster 12 | +1 | +0.0866 | +0.1808 | +0.1813 | 0.0004 | +0.6919 | +0.7497 | 0.892 |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | Cluster 13 | +1 | +0.0775 | +0.1781 | +0.1776 | 0.0008 | +0.6859 | +0.7693 | 0.857 |
| `volume_weighted_price_position` | Cluster 14 | +1 | +0.0854 | +0.1779 | +0.1774 | 0.0008 | +0.6715 | +0.7662 | 0.861 |
| `combo_tri_mean__volume_weighted_momentum_acceleration__max_up_ret__first_bar_return` | Cluster 7 | +1 | +0.0385 | +0.1770 | +0.1764 | 0.0008 | +0.4340 | +0.6571 | 0.838 |
| `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_ret_0` | Cluster 24 | +1 | +0.0640 | +0.1724 | +0.1722 | 0.0010 | +0.3951 | +0.6607 | 0.923 |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | Cluster 12 | +1 | +0.1010 | +0.1724 | +0.1724 | 0.0010 | +0.6191 | +0.7225 | 0.917 |
| `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 19 | +1 | +0.0917 | +0.1705 | +0.1703 | 0.0010 | +0.5429 | +0.6921 | 0.937 |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | Cluster 10 | +1 | +0.0983 | +0.1700 | +0.1699 | 0.0010 | +0.7281 | +0.7873 | 0.958 |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0986 | +0.1684 | +0.1681 | 0.0010 | +0.6604 | +0.7322 | 0.948 |
| `combo_sig_product__max_up_ret__first_bar_return` | Cluster 25 | +1 | +0.0713 | +0.1653 | +0.1649 | 0.0010 | +0.5202 | +0.6838 | 0.864 |
| `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 9 | +1 | +0.0809 | +0.1651 | +0.1639 | 0.0010 | +0.4599 | +0.6977 | 0.919 |
| `morning_volume_weighted_momentum` | Cluster 23 | +1 | +0.0747 | +0.1634 | +0.1619 | 0.0014 | +0.5607 | +0.7111 | 0.775 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0819 | +0.1628 | +0.1625 | 0.0014 | +0.5446 | +0.6941 | 0.937 |
| `always_in_trend_persistence` | Cluster 7 | +1 | +0.0613 | +0.1511 | +0.1496 | 0.0034 | +0.5015 | +0.6998 | 0.683 |
| `early_order_flow_imbalance` | Cluster 14 | +1 | +0.0707 | +0.1502 | +0.1488 | 0.0034 | +0.4906 | +0.6637 | 0.895 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 6 | +1 | +0.0898 | +0.1500 | +0.1500 | 0.0034 | +0.5344 | +0.7137 | 0.942 |
| `combo_sig_product__bar_body_rng_0__volume_surge_direction` | Cluster 15 | +1 | +0.0756 | +0.1495 | +0.1502 | 0.0034 | +0.5430 | +0.6560 | 0.908 |
| `combo_mean__first_bar_sentiment__volume_surge_direction` | Cluster 15 | +1 | +0.0781 | +0.1445 | +0.1453 | 0.0050 | +0.5512 | +0.6668 | 0.944 |
| `combo_min__first_bar_return__first_bar_sentiment` | Cluster 6 | +1 | +0.0804 | +0.1429 | +0.1430 | 0.0054 | +0.5066 | +0.7008 | 0.934 |
| `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio` | Cluster 23 | +1 | +0.0732 | +0.1400 | +0.1391 | 0.0060 | +0.5074 | +0.6807 | 0.868 |
| `net_volume_flow` | Cluster 23 | +1 | +0.0774 | +0.1397 | +0.1394 | 0.0060 | +0.4492 | +0.6591 | 0.879 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 8 | +1 | +0.0664 | +0.1379 | +0.1378 | 0.0066 | +0.3596 | +0.6900 | 0.755 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0852 | +0.1334 | +0.1332 | 0.0076 | +0.4460 | +0.6874 | 0.940 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 19 | +1 | +0.0951 | +0.1299 | +0.1306 | 0.0094 | +0.4720 | +0.6782 | 0.931 |
| `combo_ratio__volume_surge_direction__volume_weighted_price_position` | Cluster 15 | +1 | +0.0801 | +0.1246 | +0.1255 | 0.0114 | +0.6502 | +0.7019 | 0.942 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Cluster 6 | +1 | +0.0770 | +0.1217 | +0.1214 | 0.0130 | +0.3718 | +0.6916 | 0.032 |
| `trend_bar_close_consistency` | Cluster 7 | +1 | +0.0540 | +0.1205 | +0.1196 | 0.0134 | +0.3198 | +0.6730 | 0.898 |
| `combo_ratio__max_up_ret__bar_vol_0` | Cluster 24 | +1 | +0.0832 | +0.1121 | +0.1122 | 0.0220 | +0.4973 | +0.6807 | 0.780 |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | Cluster 6 | +1 | +0.0795 | +0.1000 | +0.0998 | 0.0440 | +0.5672 | +0.7132 | 0.948 |

### 50ETF / single
No features admitted.

### 500ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__net_volume_flow__first_bar_sentiment` | Cluster 22 | +1 | +0.1194 | +0.2859 | +0.2850 | 0.0000 | +0.7197 | +0.7678 | 0.000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 3 | +1 | +0.1328 | +0.2805 | +0.2807 | 0.0000 | +1.0200 | +0.8265 | 0.750 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 3 | +1 | +0.1395 | +0.2799 | +0.2799 | 0.0000 | +1.0253 | +0.8460 | 0.899 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 16 | +1 | +0.1459 | +0.2776 | +0.2782 | 0.0000 | +0.7123 | +0.7518 | 0.918 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Cluster 10 | +1 | +0.1325 | +0.2573 | +0.2569 | 0.0000 | +0.8883 | +0.8084 | 0.976 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression` | Cluster 47 | +1 | +0.1168 | +0.2469 | +0.2461 | 0.0000 | +0.7568 | +0.8146 | 0.871 |
| `combo_min__net_volume_flow__bar_ret_0` | Cluster 25 | +1 | +0.1136 | +0.2435 | +0.2432 | 0.0000 | +0.7209 | +0.7472 | 0.925 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1355 | +0.2417 | +0.2420 | 0.0000 | +0.5960 | +0.6900 | 0.780 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Cluster 21 | +1 | +0.1231 | +0.2414 | +0.2405 | 0.0000 | +0.8610 | +0.7945 | 0.977 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1267 | +0.2390 | +0.2395 | 0.0000 | +0.5499 | +0.7008 | 0.909 |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Cluster 16 | +1 | +0.1156 | +0.2389 | +0.2402 | 0.0000 | +0.5302 | +0.7019 | 0.877 |
| `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` | Cluster 22 | +1 | +0.1171 | +0.2381 | +0.2373 | 0.0000 | +0.5929 | +0.7225 | 0.943 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 47 | +1 | +0.1117 | +0.2357 | +0.2348 | 0.0000 | +0.6864 | +0.7662 | 0.927 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 32 | +1 | +0.1164 | +0.2351 | +0.2355 | 0.0000 | +0.6134 | +0.7065 | 0.767 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 29 | +1 | +0.1033 | +0.2348 | +0.2340 | 0.0000 | +0.6755 | +0.7307 | 0.968 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 2 | +1 | +0.1315 | +0.2336 | +0.2334 | 0.0000 | +0.7023 | +0.7673 | 0.904 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1026 | +0.2320 | +0.2306 | 0.0000 | +0.7232 | +0.7652 | 0.937 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 16 | +1 | +0.1235 | +0.2305 | +0.2316 | 0.0000 | +0.5482 | +0.6998 | 0.898 |
| `combo_rank_min__net_volume_flow__bar_ret_0` | Cluster 25 | +1 | +0.1119 | +0.2291 | +0.2288 | 0.0000 | +0.6543 | +0.7261 | 0.949 |
| `volatility_expansion_trend_vector` | Cluster 44 | +1 | +0.1054 | +0.2278 | +0.2263 | 0.0000 | +0.5785 | +0.7158 | 0.930 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 32 | +1 | +0.1181 | +0.2277 | +0.2280 | 0.0000 | +0.6672 | +0.7456 | 0.832 |
| `combo_mean__first_bar_return__max_down_ret` | Cluster 36 | +1 | +0.1162 | +0.2258 | +0.2255 | 0.0000 | +0.7365 | +0.7461 | 0.886 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 30 | +1 | +0.1140 | +0.2243 | +0.2234 | 0.0000 | +0.6757 | +0.7631 | 0.942 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Cluster 49 | +1 | +0.1361 | +0.2238 | +0.2230 | 0.0000 | +0.5885 | +0.7127 | 0.851 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 35 | +1 | +0.1177 | +0.2235 | +0.2236 | 0.0000 | +0.6567 | +0.7492 | 0.885 |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | Cluster 4 | +1 | +0.1057 | +0.2229 | +0.2221 | 0.0000 | +0.6095 | +0.7183 | 0.926 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Cluster 48 | +1 | +0.1382 | +0.2228 | +0.2222 | 0.0000 | +0.8033 | +0.7750 | 0.976 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 16 | +1 | +0.1354 | +0.2226 | +0.2235 | 0.0000 | +0.5722 | +0.7106 | 0.944 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Cluster 15 | +1 | +0.1122 | +0.2208 | +0.2205 | 0.0000 | +0.6223 | +0.7204 | 0.848 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Cluster 49 | +1 | +0.1357 | +0.2196 | +0.2187 | 0.0000 | +0.7464 | +0.7863 | 0.926 |
| `early_order_flow_imbalance` | Cluster 41 | +1 | +0.1002 | +0.2192 | +0.2174 | 0.0000 | +0.5784 | +0.7369 | 0.795 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Cluster 0 | +1 | +0.1392 | +0.2190 | +0.2189 | 0.0000 | +0.7575 | +0.7647 | 0.923 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 38 | +1 | +0.1313 | +0.2178 | +0.2170 | 0.0000 | +0.6852 | +0.7667 | 0.849 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1356 | +0.2174 | +0.2172 | 0.0000 | +0.8569 | +0.7868 | 0.864 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 32 | +1 | +0.1262 | +0.2160 | +0.2157 | 0.0000 | +0.6370 | +0.7116 | 1.000 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 35 | +1 | +0.1196 | +0.2158 | +0.2159 | 0.0000 | +0.5741 | +0.7183 | 0.946 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | Cluster 10 | +1 | +0.1167 | +0.2157 | +0.2148 | 0.0000 | +0.5067 | +0.6910 | 0.949 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 0 | +1 | +0.1264 | +0.2152 | +0.2154 | 0.0000 | +0.7303 | +0.7750 | 1.000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 48 | +1 | +0.1344 | +0.2144 | +0.2135 | 0.0000 | +0.7900 | +0.7492 | 0.927 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Cluster 24 | +1 | +0.0907 | +0.2118 | +0.2112 | 0.0000 | +0.6032 | +0.6854 | 0.950 |
| `combo_min__trend_bar_close_consistency__first_bar_return` | Cluster 24 | +1 | +0.0925 | +0.2116 | +0.2109 | 0.0000 | +0.6509 | +0.6982 | 1.000 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | Cluster 4 | +1 | +0.1079 | +0.2111 | +0.2104 | 0.0000 | +0.7140 | +0.7559 | 0.926 |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 44 | +1 | +0.1083 | +0.2109 | +0.2098 | 0.0000 | +0.5725 | +0.6988 | 0.933 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 13 | +1 | +0.1260 | +0.2085 | +0.2090 | 0.0000 | +0.4883 | +0.6766 | 0.940 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | Cluster 46 | +1 | +0.1227 | +0.2058 | +0.2050 | 0.0000 | +0.6900 | +0.7585 | 0.925 |
| `combo_rank_min__max_up_ret__bar_ret_0` | Cluster 37 | +1 | +0.1151 | +0.2046 | +0.2049 | 0.0000 | +0.4925 | +0.6854 | 0.914 |
| `combo_mean__max_up_ret__first_bar_return` | Cluster 37 | +1 | +0.1295 | +0.2044 | +0.2043 | 0.0000 | +0.5898 | +0.7240 | 0.897 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 27 | +1 | +0.1336 | +0.2029 | +0.2025 | 0.0000 | +0.6297 | +0.7497 | 0.922 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 27 | +1 | +0.1372 | +0.2028 | +0.2029 | 0.0000 | +0.6085 | +0.7343 | 0.923 |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | Cluster 38 | +1 | +0.1273 | +0.2028 | +0.2021 | 0.0000 | +0.7276 | +0.7580 | 0.913 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 1 | +1 | +0.1407 | +0.2027 | +0.2022 | 0.0000 | +0.7147 | +0.7889 | 0.928 |
| `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 28 | +1 | +0.0880 | +0.2011 | +0.1999 | 0.0000 | +0.4962 | +0.6833 | 0.938 |
| `combo_min__close_vs_open_range__first_bar_return` | Cluster 21 | +1 | +0.1035 | +0.2002 | +0.1992 | 0.0000 | +0.6697 | +0.7400 | 1.000 |
| `combo_min__bar_ret_0__max_down_ret` | Cluster 36 | +1 | +0.1026 | +0.1987 | +0.1982 | 0.0000 | +0.6750 | +0.7348 | 0.935 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 26 | +1 | +0.1243 | +0.1983 | +0.1983 | 0.0000 | +0.7163 | +0.7873 | 0.905 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Cluster 40 | +1 | +0.1206 | +0.1982 | +0.1985 | 0.0000 | +0.5049 | +0.7008 | 0.847 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression` | Cluster 33 | +1 | +0.0675 | +0.1973 | +0.1952 | 0.0000 | +0.5926 | +0.7158 | 0.895 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 46 | +1 | +0.1357 | +0.1965 | +0.1957 | 0.0000 | +0.6887 | +0.8064 | 0.990 |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 16 | +1 | +0.1349 | +0.1960 | +0.1967 | 0.0000 | +0.7338 | +0.7642 | 0.932 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | Cluster 11 | +1 | +0.0956 | +0.1947 | +0.1927 | 0.0000 | +0.6113 | +0.7291 | 0.926 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Cluster 36 | +1 | +0.0966 | +0.1947 | +0.1943 | 0.0000 | +0.6412 | +0.7286 | 0.900 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Cluster 4 | +1 | +0.1066 | +0.1946 | +0.1942 | 0.0000 | +0.6759 | +0.7441 | 0.909 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 20 | +1 | +0.1009 | +0.1923 | +0.1918 | 0.0000 | +0.5224 | +0.6771 | 0.824 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 35 | +1 | +0.1106 | +0.1914 | +0.1914 | 0.0000 | +0.4894 | +0.6895 | 0.932 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 31 | +1 | +0.0988 | +0.1908 | +0.1895 | 0.0000 | +0.5274 | +0.6622 | 0.851 |
| `opening_drive_thrust_ratio` | Cluster 26 | +1 | +0.1349 | +0.1901 | +0.1901 | 0.0000 | +0.6761 | +0.7734 | 0.936 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 31 | +1 | +0.0993 | +0.1885 | +0.1872 | 0.0000 | +0.4893 | +0.6818 | 0.944 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 11 | +1 | +0.0763 | +0.1880 | +0.1866 | 0.0000 | +0.5532 | +0.6926 | 0.918 |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 17 | +1 | +0.1097 | +0.1877 | +0.1868 | 0.0000 | +0.5682 | +0.7230 | 0.872 |
| `combo_max__bar_ret_0__max_down_ret` | Cluster 36 | +1 | +0.1206 | +0.1859 | +0.1860 | 0.0000 | +0.6664 | +0.7590 | 1.000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 29 | +1 | +0.0989 | +0.1845 | +0.1832 | 0.0000 | +0.5602 | +0.6766 | 0.923 |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | Cluster 39 | +1 | +0.1068 | +0.1833 | +0.1815 | 0.0000 | +0.5268 | +0.7219 | 0.978 |
| `combo_max__net_volume_flow__max_down_ret` | Cluster 4 | +1 | +0.1090 | +0.1832 | +0.1826 | 0.0000 | +0.6839 | +0.7559 | 0.930 |
| `first_30min_return` | Cluster 44 | +1 | +0.1098 | +0.1826 | +0.1808 | 0.0000 | +0.6753 | +0.7575 | 0.886 |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | Cluster 15 | +1 | +0.1041 | +0.1819 | +0.1817 | 0.0000 | +0.5509 | +0.7008 | 0.946 |
| `first_bar_return` | Cluster 15 | +1 | +0.1110 | +0.1817 | +0.1816 | 0.0000 | +0.5334 | +0.7101 | 0.944 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 1 | +1 | +0.1265 | +0.1801 | +0.1802 | 0.0000 | +0.5222 | +0.7060 | 0.928 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | Cluster 33 | +1 | +0.0732 | +0.1801 | +0.1782 | 0.0000 | +0.5274 | +0.6797 | 0.888 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | Cluster 44 | +1 | +0.1102 | +0.1797 | +0.1789 | 0.0000 | +0.5550 | +0.6967 | 0.915 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Cluster 8 | +1 | +0.1198 | +0.1786 | +0.1773 | 0.0000 | +0.6694 | +0.7436 | 0.856 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 26 | +1 | +0.1258 | +0.1783 | +0.1784 | 0.0000 | +0.6536 | +0.7271 | 0.971 |
| `combo_min__early_body_momentum__max_down_ret` | Cluster 44 | +1 | +0.0998 | +0.1779 | +0.1777 | 0.0000 | +0.5643 | +0.7353 | 0.938 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 26 | +1 | +0.1139 | +0.1772 | +0.1772 | 0.0000 | +0.5725 | +0.6869 | 0.916 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Cluster 7 | +1 | +0.0862 | +0.1763 | +0.1758 | 0.0000 | +0.4762 | +0.6601 | 0.865 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 5 | +1 | +0.1158 | +0.1758 | +0.1761 | 0.0000 | +0.6079 | +0.6972 | 0.754 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Cluster 45 | +1 | +0.1038 | +0.1748 | +0.1748 | 0.0000 | +0.4473 | +0.6993 | 0.818 |
| `combo_min__close_vs_open_range__early_body_momentum` | Cluster 44 | +1 | +0.0972 | +0.1744 | +0.1732 | 0.0000 | +0.4249 | +0.6504 | 0.956 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 6 | +1 | +0.0624 | +0.1735 | +0.1725 | 0.0000 | +0.5585 | +0.7219 | 0.629 |
| `always_in_trend_persistence` | Cluster 43 | +1 | +0.0861 | +0.1730 | +0.1705 | 0.0000 | +0.5354 | +0.7235 | 0.954 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 42 | +1 | +0.0877 | +0.1726 | +0.1721 | 0.0002 | +0.6259 | +0.7085 | 0.827 |
| `combo_max__close_vs_open_range__early_body_momentum` | Cluster 44 | +1 | +0.0977 | +0.1723 | +0.1708 | 0.0002 | +0.3762 | +0.6560 | 0.946 |
| `morning_volume_weighted_momentum` | Cluster 44 | +1 | +0.1111 | +0.1720 | +0.1705 | 0.0002 | +0.5776 | +0.7055 | 0.937 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 40 | +1 | +0.1150 | +0.1709 | +0.1713 | 0.0002 | +0.5711 | +0.7415 | 1.000 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Cluster 36 | +1 | +0.1205 | +0.1703 | +0.1704 | 0.0002 | +0.6027 | +0.7240 | 0.906 |
| `combo_max__first_bar_sentiment__bar_ret_0` | Cluster 15 | +1 | +0.1142 | +0.1689 | +0.1688 | 0.0004 | +0.4706 | +0.6668 | 0.912 |
| `combo_mean__first_bar_sentiment__max_down_ret` | Cluster 36 | +1 | +0.1105 | +0.1673 | +0.1673 | 0.0004 | +0.6314 | +0.7111 | 0.902 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 42 | +1 | +0.0957 | +0.1667 | +0.1668 | 0.0004 | +0.6718 | +0.7240 | 0.868 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 42 | +1 | +0.0964 | +0.1660 | +0.1662 | 0.0004 | +0.5682 | +0.6885 | 0.885 |
| `combo_max__close_vs_open_range__max_down_ret` | Cluster 4 | +1 | +0.1031 | +0.1657 | +0.1651 | 0.0004 | +0.4885 | +0.6740 | 0.912 |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 16 | +1 | +0.1218 | +0.1637 | +0.1645 | 0.0006 | +0.4510 | +0.6843 | 0.847 |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | Cluster 15 | +1 | +0.1051 | +0.1635 | +0.1628 | 0.0006 | +0.5510 | +0.7188 | 0.949 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 12 | +1 | +0.1062 | +0.1625 | +0.1614 | 0.0006 | +0.4162 | +0.6797 | 0.927 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 19 | +1 | +0.1114 | +0.1619 | +0.1612 | 0.0008 | +0.4344 | +0.6813 | 0.956 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 17 | +1 | +0.1029 | +0.1612 | +0.1601 | 0.0008 | +0.4648 | +0.6890 | 0.917 |
| `vwap_close_divergence_trend` | Cluster 14 | +1 | +0.0936 | +0.1609 | +0.1597 | 0.0008 | +0.6298 | +0.7333 | 0.880 |
| `combo_max__first_bar_sentiment__high_low_sequence_momentum` | Cluster 23 | +1 | +0.1120 | +0.1573 | +0.1572 | 0.0012 | +0.4582 | +0.6643 | 0.986 |
| `max_down_ret` | Cluster 8 | +1 | +0.0968 | +0.1554 | +0.1554 | 0.0016 | +0.5908 | +0.7055 | 0.945 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | Cluster 16 | +1 | +0.1078 | +0.1535 | +0.1548 | 0.0018 | +0.4370 | +0.6637 | 0.926 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Cluster 15 | +1 | +0.1132 | +0.1520 | +0.1512 | 0.0020 | +0.6100 | +0.7214 | 0.949 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 35 | +1 | +0.1159 | +0.1519 | +0.1521 | 0.0020 | +0.4913 | +0.6694 | 0.929 |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | Cluster 18 | +1 | +0.1075 | +0.1513 | +0.1502 | 0.0022 | +0.4001 | +0.6663 | 0.937 |
| `volume_surge_direction` | Cluster 45 | +1 | +0.0999 | +0.1500 | +0.1495 | 0.0022 | +0.4769 | +0.6787 | 0.880 |
| `combo_sig_product__max_up_ret__body_size_progression` | Cluster 5 | +1 | +0.1065 | +0.1472 | +0.1485 | 0.0028 | +0.5183 | +0.6735 | 0.854 |
| `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range` | Cluster 6 | +1 | +0.0544 | +0.1441 | +0.1435 | 0.0040 | +0.6171 | +0.7513 | 0.485 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Cluster 15 | +1 | +0.1007 | +0.1365 | +0.1357 | 0.0060 | +0.4419 | +0.6607 | 0.922 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Cluster 34 | +1 | +0.0844 | +0.1351 | +0.1332 | 0.0070 | +0.3186 | +0.6643 | 0.708 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Cluster 35 | +1 | +0.1155 | +0.1317 | +0.1313 | 0.0084 | +0.4833 | +0.6627 | 0.898 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 15 | +1 | +0.1213 | +0.1315 | +0.1314 | 0.0086 | +0.4788 | +0.6993 | 0.991 |
| `combo_sig_product__net_volume_flow__max_down_ret` | Cluster 8 | +1 | +0.0904 | +0.1308 | +0.1306 | 0.0090 | +0.4823 | +0.6607 | 0.889 |
| `vwap_trend_channel_slope` | Cluster 14 | +1 | +0.0893 | +0.1273 | +0.1271 | 0.0100 | +0.5682 | +0.6890 | 0.942 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Cluster 5 | +1 | +0.1185 | +0.1271 | +0.1284 | 0.0100 | +0.4718 | +0.6689 | 0.949 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 19 | +1 | +0.1259 | +0.1266 | +0.1261 | 0.0104 | +0.4262 | +0.6967 | 0.942 |
| `num_up_bars` | Cluster 41 | +1 | +0.0993 | +0.1263 | +0.1254 | 0.0110 | +0.3943 | +0.6674 | 0.833 |
| `bar_body_rng_0` | Cluster 15 | +1 | +0.1081 | +0.1260 | +0.1257 | 0.0116 | +0.4340 | +0.6715 | 0.921 |
| `micro_gap_trend_continuation` | Cluster 43 | +1 | +0.0693 | +0.1137 | +0.1129 | 0.0228 | +0.3643 | +0.6550 | 0.785 |
| `combo_max__star50_limit_proximity_early__max_down_ret` | Cluster 20 | +1 | +0.0920 | +0.1083 | +0.1076 | 0.0290 | +0.3633 | +0.6648 | 0.854 |

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 6 | +1 | +0.1574 | +0.3748 | +0.3754 | 0.0000 | +1.2328 | +0.8847 | 0.977 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 51 | +1 | +0.1565 | +0.3521 | +0.3534 | 0.0000 | +1.0413 | +0.8527 | 0.975 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 6 | +1 | +0.1485 | +0.3411 | +0.3414 | 0.0000 | +1.2042 | +0.8646 | 0.932 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 3 | +1 | +0.1510 | +0.3411 | +0.3412 | 0.0000 | +0.9988 | +0.8357 | 0.864 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 51 | +1 | +0.1550 | +0.3351 | +0.3365 | 0.0000 | +1.0177 | +0.8316 | 0.940 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 49 | +1 | +0.1487 | +0.3339 | +0.3340 | 0.0000 | +1.1165 | +0.8527 | 0.838 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 51 | +1 | +0.1411 | +0.3337 | +0.3345 | 0.0000 | +1.0372 | +0.8502 | 0.940 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 49 | +1 | +0.1520 | +0.3325 | +0.3324 | 0.0000 | +1.1207 | +0.8666 | 0.916 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 52 | +1 | +0.1422 | +0.3231 | +0.3239 | 0.0000 | +1.0138 | +0.8347 | 0.814 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 2 | +1 | +0.1502 | +0.3108 | +0.3111 | 0.0000 | +1.0229 | +0.8548 | 0.992 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Cluster 52 | +1 | +0.1291 | +0.3107 | +0.3113 | 0.0000 | +1.0199 | +0.8239 | 0.968 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 4 | +1 | +0.1436 | +0.3076 | +0.3077 | 0.0000 | +0.8715 | +0.7884 | 0.941 |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | Cluster 5 | +1 | +0.1445 | +0.3020 | +0.3020 | 0.0000 | +0.9304 | +0.8193 | 0.847 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 51 | +1 | +0.1296 | +0.3014 | +0.3022 | 0.0000 | +0.8297 | +0.7894 | 0.943 |
| `combo_diff__bar_body_rng_0__demark_setup_reversal_early` | Cluster 5 | +1 | +0.1460 | +0.3003 | +0.3003 | 0.0000 | +0.9089 | +0.8079 | 0.933 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 48 | +1 | +0.1423 | +0.2982 | +0.2982 | 0.0000 | +0.9595 | +0.8491 | 0.856 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 51 | +1 | +0.1449 | +0.2979 | +0.2987 | 0.0000 | +0.8025 | +0.7745 | 0.950 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 51 | +1 | +0.1403 | +0.2943 | +0.2957 | 0.0000 | +1.1038 | +0.8646 | 0.947 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 11 | +1 | +0.1213 | +0.2879 | +0.2881 | 0.0000 | +0.8411 | +0.7750 | 0.823 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 17 | +1 | +0.1387 | +0.2873 | +0.2878 | 0.0000 | +0.8460 | +0.7719 | 0.923 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 51 | +1 | +0.1243 | +0.2872 | +0.2881 | 0.0000 | +0.8954 | +0.8352 | 0.880 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 48 | +1 | +0.1373 | +0.2851 | +0.2849 | 0.0000 | +0.8684 | +0.8275 | 0.943 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 4 | +1 | +0.1448 | +0.2831 | +0.2836 | 0.0000 | +0.8263 | +0.8012 | 0.949 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 51 | +1 | +0.1364 | +0.2804 | +0.2815 | 0.0000 | +0.8444 | +0.8064 | 0.934 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Cluster 26 | +1 | +0.1249 | +0.2801 | +0.2805 | 0.0000 | +0.8505 | +0.8002 | 0.903 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 51 | +1 | +0.1447 | +0.2787 | +0.2803 | 0.0000 | +0.8794 | +0.8002 | 1.000 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Cluster 21 | +1 | +0.1336 | +0.2775 | +0.2775 | 0.0000 | +0.8686 | +0.7781 | 0.910 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 16 | +1 | +0.1378 | +0.2722 | +0.2726 | 0.0000 | +0.8345 | +0.7657 | 0.950 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 42 | +1 | +0.1130 | +0.2722 | +0.2723 | 0.0000 | +0.8361 | +0.7884 | 0.819 |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0` | Cluster 16 | +1 | +0.1331 | +0.2718 | +0.2721 | 0.0000 | +0.6491 | +0.7364 | 0.954 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 23 | +1 | +0.1239 | +0.2695 | +0.2701 | 0.0000 | +0.7681 | +0.7719 | 0.937 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 35 | +1 | +0.1421 | +0.2680 | +0.2679 | 0.0000 | +0.8798 | +0.8028 | 0.896 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 36 | +1 | +0.1300 | +0.2666 | +0.2666 | 0.0000 | +0.6617 | +0.7327 | 0.855 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 35 | +1 | +0.1400 | +0.2661 | +0.2659 | 0.0000 | +0.8763 | +0.8028 | 0.922 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 17 | +1 | +0.1440 | +0.2638 | +0.2641 | 0.0000 | +0.8518 | +0.7966 | 0.946 |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | Cluster 52 | +1 | +0.1102 | +0.2634 | +0.2638 | 0.0000 | +0.7562 | +0.7688 | 0.866 |
| `opening_drive_thrust_ratio` | Cluster 42 | +1 | +0.1290 | +0.2628 | +0.2631 | 0.0000 | +0.9151 | +0.7894 | 0.909 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Cluster 45 | +1 | +0.1415 | +0.2595 | +0.2603 | 0.0000 | +0.7986 | +0.7848 | 0.908 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 44 | +1 | +0.1457 | +0.2591 | +0.2590 | 0.0000 | +0.8872 | +0.8012 | 0.930 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 46 | +1 | +0.1058 | +0.2588 | +0.2591 | 0.0000 | +0.8061 | +0.8023 | 0.898 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 31 | +1 | +0.1416 | +0.2583 | +0.2583 | 0.0000 | +0.7807 | +0.7817 | 0.886 |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | Cluster 4 | +1 | +0.1314 | +0.2564 | +0.2564 | 0.0000 | +0.7304 | +0.7868 | 1.000 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 19 | +1 | +0.1272 | +0.2562 | +0.2565 | 0.0000 | +0.7015 | +0.7775 | 0.998 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 14 | +1 | +0.1141 | +0.2556 | +0.2552 | 0.0000 | +0.6614 | +0.7487 | 0.555 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 42 | +1 | +0.1257 | +0.2554 | +0.2557 | 0.0000 | +1.0492 | +0.8254 | 0.940 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | Cluster 13 | +1 | +0.1317 | +0.2553 | +0.2552 | 0.0000 | +0.5794 | +0.7472 | 0.820 |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Cluster 2 | +1 | +0.1489 | +0.2535 | +0.2534 | 0.0000 | +0.8781 | +0.8239 | 0.970 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 44 | +1 | +0.1332 | +0.2532 | +0.2535 | 0.0000 | +0.7679 | +0.7533 | 0.937 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 31 | +1 | +0.1411 | +0.2512 | +0.2511 | 0.0000 | +0.7922 | +0.7956 | 0.914 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 14 | +1 | +0.1073 | +0.2506 | +0.2503 | 0.0000 | +0.6673 | +0.7693 | 0.827 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | Cluster 29 | +1 | +0.1333 | +0.2503 | +0.2510 | 0.0000 | +0.7633 | +0.7992 | 0.944 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 42 | +1 | +0.1279 | +0.2483 | +0.2487 | 0.0000 | +0.8969 | +0.8038 | 0.977 |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 42 | +1 | +0.1129 | +0.2477 | +0.2477 | 0.0000 | +0.8383 | +0.8048 | 0.920 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 22 | +1 | +0.1259 | +0.2465 | +0.2477 | 0.0000 | +0.6445 | +0.7549 | 0.960 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 44 | +1 | +0.1159 | +0.2440 | +0.2438 | 0.0000 | +0.7524 | +0.8162 | 0.922 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 37 | +1 | +0.1205 | +0.2423 | +0.2431 | 0.0000 | +0.6141 | +0.7472 | 0.922 |
| `combo_max__max_up_ret__bar_body_rng_0` | Cluster 21 | +1 | +0.1336 | +0.2417 | +0.2416 | 0.0000 | +0.8184 | +0.7575 | 0.973 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 24 | +1 | +0.1383 | +0.2416 | +0.2424 | 0.0000 | +0.6953 | +0.7564 | 0.982 |
| `combo_max__impulse_bar_dominance__volatility_expansion_trend_vector` | Cluster 39 | +1 | +0.1031 | +0.2414 | +0.2412 | 0.0000 | +0.6505 | +0.7400 | 0.871 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 14 | +1 | +0.1092 | +0.2412 | +0.2410 | 0.0000 | +0.6174 | +0.7518 | 0.870 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 52 | +1 | +0.1484 | +0.2412 | +0.2410 | 0.0000 | +0.8329 | +0.7770 | 0.982 |
| `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector` | Cluster 39 | +1 | +0.0980 | +0.2411 | +0.2415 | 0.0000 | +0.6110 | +0.7441 | 0.896 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 14 | +1 | +0.1025 | +0.2406 | +0.2403 | 0.0000 | +0.6260 | +0.7451 | 0.974 |
| `combo_min__bar_body_rng_0__impulse_bar_dominance` | Cluster 8 | +1 | +0.1190 | +0.2381 | +0.2381 | 0.0000 | +0.5169 | +0.6998 | 0.852 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 24 | +1 | +0.1368 | +0.2373 | +0.2381 | 0.0000 | +0.7514 | +0.7832 | 0.947 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 47 | +1 | +0.1315 | +0.2369 | +0.2367 | 0.0000 | +0.8296 | +0.7544 | 1.000 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 10 | +1 | +0.1278 | +0.2368 | +0.2369 | 0.0000 | +0.5973 | +0.7173 | 0.901 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 18 | +1 | +0.1328 | +0.2366 | +0.2366 | 0.0000 | +0.6468 | +0.7188 | 0.946 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 23 | +1 | +0.1193 | +0.2346 | +0.2348 | 0.0000 | +0.6541 | +0.7338 | 0.934 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 34 | +1 | +0.1408 | +0.2337 | +0.2336 | 0.0000 | +0.7113 | +0.7554 | 0.867 |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 46 | +1 | +0.1038 | +0.2335 | +0.2340 | 0.0000 | +0.7030 | +0.7611 | 0.882 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 44 | +1 | +0.1215 | +0.2332 | +0.2339 | 0.0000 | +0.7936 | +0.7667 | 0.894 |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | Cluster 37 | +1 | +0.1076 | +0.2328 | +0.2335 | 0.0000 | +0.6450 | +0.7446 | 0.838 |
| `max_up_ret` | Cluster 44 | +1 | +0.1267 | +0.2319 | +0.2324 | 0.0000 | +0.8184 | +0.7858 | 0.937 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 37 | +1 | +0.1244 | +0.2301 | +0.2305 | 0.0000 | +0.7367 | +0.7513 | 0.989 |
| `combo_mean__first_bar_sentiment__limit_down_proximity_early` | Cluster 51 | +1 | +0.1161 | +0.2284 | +0.2282 | 0.0000 | +0.5817 | +0.6648 | 0.930 |
| `bar_body_rng_0` | Cluster 37 | +1 | +0.1231 | +0.2273 | +0.2279 | 0.0000 | +0.5838 | +0.7152 | 0.949 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | Cluster 28 | +1 | +0.1276 | +0.2264 | +0.2270 | 0.0000 | +0.6875 | +0.7559 | 1.000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 10 | +1 | +0.1294 | +0.2261 | +0.2260 | 0.0000 | +0.6052 | +0.6982 | 0.912 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 44 | +1 | +0.1223 | +0.2254 | +0.2264 | 0.0000 | +0.8243 | +0.7915 | 0.931 |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | Cluster 9 | +1 | +0.1118 | +0.2248 | +0.2248 | 0.0000 | +0.6371 | +0.7338 | 0.917 |
| `combo_min__first_bar_sentiment__volatility_expansion_trend_vector` | Cluster 20 | +1 | +0.1002 | +0.2245 | +0.2249 | 0.0000 | +0.5222 | +0.7168 | 0.912 |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | Cluster 27 | +1 | +0.1288 | +0.2224 | +0.2232 | 0.0002 | +0.7171 | +0.7817 | 0.950 |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | Cluster 15 | +1 | +0.1183 | +0.2224 | +0.2227 | 0.0002 | +0.6113 | +0.7523 | 0.931 |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | Cluster 7 | +1 | +0.1097 | +0.2211 | +0.2215 | 0.0002 | +0.6304 | +0.7281 | 0.924 |
| `combo_mean__max_up_ret__impulse_bar_dominance` | Cluster 44 | +1 | +0.1212 | +0.2192 | +0.2194 | 0.0002 | +0.8123 | +0.7801 | 0.907 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 14 | +1 | +0.1173 | +0.2178 | +0.2171 | 0.0002 | +0.5604 | +0.7338 | 0.914 |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | Cluster 39 | +1 | +0.1025 | +0.2173 | +0.2174 | 0.0002 | +0.6754 | +0.7580 | 0.908 |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 42 | +1 | +0.1181 | +0.2168 | +0.2172 | 0.0002 | +0.7038 | +0.7570 | 0.900 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 39 | +1 | +0.1158 | +0.2159 | +0.2157 | 0.0002 | +0.7032 | +0.7796 | 0.888 |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | Cluster 9 | +1 | +0.0939 | +0.2141 | +0.2141 | 0.0002 | +0.7117 | +0.7528 | 0.943 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 43 | +1 | +0.1217 | +0.2139 | +0.2137 | 0.0002 | +0.6901 | +0.7750 | 0.891 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Cluster 27 | +1 | +0.1276 | +0.2137 | +0.2143 | 0.0002 | +0.7401 | +0.7698 | 0.939 |
| `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector` | Cluster 39 | +1 | +0.1026 | +0.2136 | +0.2140 | 0.0002 | +0.7090 | +0.7817 | 0.943 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Cluster 1 | +1 | +0.1155 | +0.2112 | +0.2115 | 0.0002 | +0.6773 | +0.7261 | 0.774 |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | Cluster 38 | +1 | +0.1091 | +0.2111 | +0.2116 | 0.0002 | +0.3936 | +0.6761 | 0.698 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 12 | +1 | +0.1238 | +0.2108 | +0.2101 | 0.0002 | +0.4595 | +0.7214 | 0.843 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 43 | +1 | +0.1184 | +0.2099 | +0.2097 | 0.0002 | +0.6855 | +0.7678 | 0.898 |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | Cluster 40 | +1 | +0.1255 | +0.2098 | +0.2088 | 0.0002 | +0.4964 | +0.6648 | 0.873 |
| `net_volume_flow` | Cluster 44 | +1 | +0.1081 | +0.2076 | +0.2077 | 0.0002 | +0.6497 | +0.7430 | 0.917 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | Cluster 20 | +1 | +0.1037 | +0.2066 | +0.2073 | 0.0002 | +0.5337 | +0.7441 | 0.940 |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | Cluster 37 | +1 | +0.1155 | +0.2055 | +0.2056 | 0.0002 | +0.5435 | +0.7183 | 0.878 |
| `combo_max__first_bar_sentiment__volatility_expansion_trend_vector` | Cluster 25 | +1 | +0.1171 | +0.2041 | +0.2044 | 0.0002 | +0.5813 | +0.7183 | 0.903 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 40 | +1 | +0.1298 | +0.2041 | +0.2031 | 0.0002 | +0.4910 | +0.6586 | 0.856 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 50 | +1 | +0.1206 | +0.2039 | +0.2039 | 0.0002 | +0.7588 | +0.7827 | 0.935 |
| `combo_min__max_up_ret__volume_weighted_price_position` | Cluster 11 | +1 | +0.1148 | +0.2037 | +0.2043 | 0.0002 | +0.5025 | +0.6880 | 0.967 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 36 | +1 | +0.1352 | +0.2000 | +0.1994 | 0.0002 | +0.5543 | +0.7132 | 0.895 |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | Cluster 37 | +1 | +0.1206 | +0.1989 | +0.1995 | 0.0002 | +0.4585 | +0.7029 | 0.871 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 19 | +1 | +0.1238 | +0.1980 | +0.1983 | 0.0002 | +0.5723 | +0.6787 | 0.958 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 40 | +1 | +0.1286 | +0.1980 | +0.1967 | 0.0002 | +0.6311 | +0.7173 | 0.913 |
| `trend_bar_close_consistency` | Cluster 0 | +1 | +0.0897 | +0.1956 | +0.1955 | 0.0002 | +0.6074 | +0.7533 | 0.907 |
| `combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | Cluster 36 | +1 | +0.1043 | +0.1928 | +0.1928 | 0.0002 | +0.6000 | +0.7425 | 0.901 |
| `combo_mean__first_bar_return__volume_weighted_price_position` | Cluster 37 | +1 | +0.1141 | +0.1890 | +0.1896 | 0.0002 | +0.4884 | +0.6777 | 0.935 |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 38 | +1 | +0.1340 | +0.1881 | +0.1876 | 0.0004 | +0.4478 | +0.6612 | 0.974 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Cluster 33 | +1 | +0.1295 | +0.1855 | +0.1848 | 0.0004 | +0.6302 | +0.6962 | 0.902 |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 40 | +1 | +0.1054 | +0.1835 | +0.1829 | 0.0004 | +0.4415 | +0.6802 | 1.000 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 32 | +1 | +0.1117 | +0.1832 | +0.1827 | 0.0004 | +0.5927 | +0.7137 | 1.000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 33 | +1 | +0.1227 | +0.1827 | +0.1822 | 0.0004 | +0.5474 | +0.6746 | 0.934 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 41 | +1 | +0.0639 | +0.1824 | +0.1822 | 0.0004 | +0.5156 | +0.6612 | 0.460 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 38 | +1 | +0.1370 | +0.1815 | +0.1809 | 0.0004 | +0.4673 | +0.6751 | 0.803 |
| `combo_max__bar_ret_0__impulse_bar_dominance` | Cluster 7 | +1 | +0.0989 | +0.1797 | +0.1798 | 0.0004 | +0.6248 | +0.7415 | 1.000 |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | Cluster 39 | +1 | +0.1104 | +0.1796 | +0.1797 | 0.0004 | +0.6826 | +0.7430 | 0.927 |
| `combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return` | Cluster 37 | +1 | +0.1155 | +0.1789 | +0.1799 | 0.0006 | +0.5557 | +0.7441 | 0.930 |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 38 | +1 | +0.0907 | +0.1785 | +0.1782 | 0.0006 | +0.5078 | +0.6792 | 0.796 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 36 | +1 | +0.1130 | +0.1784 | +0.1782 | 0.0006 | +0.4839 | +0.6864 | 0.912 |
| `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 40 | +1 | +0.1213 | +0.1780 | +0.1771 | 0.0006 | +0.5256 | +0.6890 | 0.919 |
| `combo_min__max_up_ret__first_bar_return` | Cluster 22 | +1 | +0.1164 | +0.1766 | +0.1781 | 0.0006 | +0.6298 | +0.7734 | 0.945 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 13 | +1 | +0.1236 | +0.1753 | +0.1755 | 0.0006 | +0.5580 | +0.6900 | 1.000 |
| `combo_diff__limit_down_proximity_early__demark_setup_reversal_early` | Cluster 38 | +1 | +0.1178 | +0.1750 | +0.1746 | 0.0006 | +0.4694 | +0.6586 | 0.891 |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early` | Cluster 38 | +1 | +0.1158 | +0.1744 | +0.1740 | 0.0006 | +0.4724 | +0.6529 | 0.854 |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1214 | +0.1741 | +0.1738 | 0.0008 | +0.6191 | +0.7096 | 0.971 |
| `combo_max__first_bar_sentiment__first_bar_return` | Cluster 37 | +1 | +0.1150 | +0.1740 | +0.1750 | 0.0008 | +0.6064 | +0.7348 | 0.927 |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | Cluster 36 | +1 | +0.1071 | +0.1661 | +0.1658 | 0.0012 | +0.5660 | +0.6910 | 0.932 |
| `combo_max__bar_ret_0__limit_down_proximity_early` | Cluster 40 | +1 | +0.1089 | +0.1650 | +0.1643 | 0.0014 | +0.5434 | +0.7122 | 0.935 |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | Cluster 37 | +1 | +0.1135 | +0.1648 | +0.1657 | 0.0014 | +0.6037 | +0.7297 | 1.000 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Cluster 38 | +1 | +0.1077 | +0.1643 | +0.1655 | 0.0016 | +0.3960 | +0.6529 | 0.888 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Cluster 37 | +1 | +0.1121 | +0.1642 | +0.1650 | 0.0016 | +0.5547 | +0.7338 | 0.912 |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 38 | +1 | +0.0656 | +0.1624 | +0.1627 | 0.0022 | +0.4080 | +0.6632 | 0.822 |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | Cluster 40 | +1 | +0.1118 | +0.1602 | +0.1592 | 0.0028 | +0.4237 | +0.6519 | 0.943 |
| `shaved_bar_trend_conviction` | Cluster 0 | +1 | +0.0847 | +0.1554 | +0.1556 | 0.0032 | +0.5697 | +0.6859 | 0.820 |
| `close_vs_open_range` | Cluster 39 | +1 | +0.0979 | +0.1374 | +0.1374 | 0.0058 | +0.5917 | +0.7297 | 0.884 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Cluster 12 | +1 | +0.1124 | +0.1335 | +0.1328 | 0.0072 | +0.3977 | +0.6668 | 1.000 |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1122 | +0.1317 | +0.1313 | 0.0084 | +0.4453 | +0.6658 | 0.895 |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | Cluster 41 | +1 | +0.0697 | +0.1262 | +0.1256 | 0.0116 | +0.5067 | +0.6689 | 0.805 |
| `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance` | Cluster 36 | +1 | +0.0877 | +0.1184 | +0.1184 | 0.0182 | +0.4224 | +0.6735 | 0.910 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Cluster 37 | +1 | +0.1010 | +0.1130 | +0.1133 | 0.0242 | +0.3613 | +0.6504 | 0.924 |


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

### Cluster Overview per ETF / Side

| ETF | Side | Total Features | Clusters | Avg Silhouette | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 300ETF | single | 99 | 26 | 0.1965 | `[17, 10, 9, 8, 7, 4, 3, 3, 3, 3, 3, 2, ... (26 clusters)]` |
| 500ETF | single | 126 | 50 | 0.2717 | `[9, 8, 7, 6, 5, 5, 4, 3, 3, 3, 3, 3, ... (50 clusters)]` |
| 159915ETF | single | 146 | 53 | 0.2630 | `[12, 10, 8, 8, 7, 7, 6, 6, 5, 4, 3, 2, ... (53 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 9 | 0.1965 | `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | `combo_max__opening_drive_thrust_ratio__volume_surge_direction`, `combo_rank_max__max_up_ret__volume_surge_direction`, `combo_mean__max_up_ret__volume_surge_direction`, `combo_max__max_up_ret__volume_surge_direction`, `combo_min__opening_drive_thrust_ratio__volume_surge_direction`, `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_rank_min__max_up_ret__volume_surge_direction`, `combo_min__max_up_ret__volume_surge_direction` |
| 300ETF | single | Cluster 1 | 10 | 0.1965 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`, `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 2 | 7 | 0.1965 | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `combo_tri_mean__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_max__max_up_ret__volume_weighted_price_position`, `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 3 | 2 | 0.1965 | `combo_tri_mean__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 4 | 1 | 0.1965 | `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 5 | 2 | 0.1965 | `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | `combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 6 | 17 | 0.1965 | `combo_min__bar_body_rng_0__volume_surge_direction` | `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_max__bar_ret_0__volume_surge_direction`, `combo_rank_max__first_bar_return__volume_surge_direction`, `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`, `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0`, `combo_max__first_bar_return__bar_body_rng_0`, `combo_tri_median__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_max__first_bar_return__first_bar_sentiment`, `combo_rank_min__max_up_ret__first_bar_return`, `combo_min__max_up_ret__first_bar_sentiment`, `combo_min__bar_ret_0__volume_surge_direction`, `combo_ratio__bar_body_rng_0__volume_weighted_price_position`, `combo_min__first_bar_return__first_bar_sentiment`, `combo_ratio__first_bar_return__volume_surge_direction`, `combo_rank_min__first_bar_return__first_bar_sentiment` |
| 300ETF | single | Cluster 7 | 3 | 0.1965 | `combo_tri_mean__volume_weighted_momentum_acceleration__max_up_ret__first_bar_return` | `always_in_trend_persistence`, `trend_bar_close_consistency` |
| 300ETF | single | Cluster 8 | 2 | 0.1965 | `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction` |
| 300ETF | single | Cluster 9 | 8 | 0.1965 | `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_mean__bar_body_rng_0__limit_down_proximity_early`, `combo_min__bar_body_rng_0__limit_down_proximity_early`, `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` |
| 300ETF | single | Cluster 10 | 2 | 0.1965 | `combo_tri_min__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `combo_min__volume_weighted_price_position__volume_surge_direction` |
| 300ETF | single | Cluster 11 | 2 | 0.1965 | `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `combo_rank_max__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 12 | 2 | 0.1965 | `combo_rank_max__volume_weighted_price_position__volume_surge_direction` | `combo_mean__volume_weighted_price_position__volume_surge_direction` |
| 300ETF | single | Cluster 13 | 2 | 0.1965 | `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | `combo_sig_product__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 14 | 4 | 0.1965 | `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | `combo_sig_product__volume_weighted_price_position__bar_body_rng_0`, `volume_weighted_price_position`, `early_order_flow_imbalance` |
| 300ETF | single | Cluster 15 | 3 | 0.1965 | `combo_sig_product__bar_body_rng_0__volume_surge_direction` | `combo_mean__first_bar_sentiment__volume_surge_direction`, `combo_ratio__volume_surge_direction__volume_weighted_price_position` |
| 300ETF | single | Cluster 16 | 2 | 0.1965 | `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 17 | 2 | 0.1965 | `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 18 | 2 | 0.1965 | `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 19 | 2 | 0.1965 | `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` |
| 300ETF | single | Cluster 20 | 3 | 0.1965 | `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | `combo_max__first_bar_return__opening_drive_thrust_ratio`, `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 21 | 3 | 0.1965 | `combo_rank_max__max_up_ret__first_bar_return` | `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`, `combo_mean__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 22 | 2 | 0.1965 | `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 23 | 3 | 0.1965 | `morning_volume_weighted_momentum` | `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio`, `net_volume_flow` |
| 300ETF | single | Cluster 24 | 2 | 0.1965 | `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_ret_0` | `combo_ratio__max_up_ret__bar_vol_0` |
| 300ETF | single | Cluster 25 | 2 | 0.1965 | `combo_sig_product__max_up_ret__volume_weighted_price_position` | `combo_sig_product__max_up_ret__first_bar_return` |
| 500ETF | single | Cluster 0 | 2 | 0.2717 | `combo_mean__opening_drive_thrust_ratio__first_bar_return` | `combo_min__opening_drive_thrust_ratio__bar_ret_0` |
| 500ETF | single | Cluster 1 | 2 | 0.2717 | `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` |
| 500ETF | single | Cluster 2 | 1 | 0.2717 | `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 3 | 2 | 0.2717 | `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 4 | 5 | 0.2717 | `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | `combo_mean__volatility_expansion_trend_vector__max_down_ret`, `combo_rank_min__volatility_expansion_trend_vector__max_down_ret`, `combo_max__net_volume_flow__max_down_ret`, `combo_max__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 5 | 3 | 0.2717 | `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `combo_sig_product__max_up_ret__body_size_progression`, `combo_sig_product__max_up_ret__early_late_momentum_divergence` |
| 500ETF | single | Cluster 6 | 2 | 0.2717 | `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range` |
| 500ETF | single | Cluster 7 | 1 | 0.2717 | `combo_sig_product__net_volume_flow__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 8 | 3 | 0.2717 | `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | `max_down_ret`, `combo_sig_product__net_volume_flow__max_down_ret` |
| 500ETF | single | Cluster 9 | 1 | 0.2717 | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | _(none)_ |
| 500ETF | single | Cluster 10 | 2 | 0.2717 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` |
| 500ETF | single | Cluster 11 | 2 | 0.2717 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` |
| 500ETF | single | Cluster 12 | 1 | 0.2717 | `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | _(none)_ |
| 500ETF | single | Cluster 13 | 3 | 0.2717 | `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 14 | 2 | 0.2717 | `vwap_close_divergence_trend` | `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 15 | 9 | 0.2717 | `combo_min__first_bar_sentiment__bar_ret_0` | `combo_rank_max__net_volume_flow__first_bar_sentiment`, `first_bar_return`, `combo_rank_min__max_up_ret__first_bar_sentiment`, `combo_max__first_bar_sentiment__bar_ret_0`, `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment`, `combo_rank_min__first_bar_sentiment__bar_ret_0`, `combo_rank_min__first_bar_sentiment__max_down_ret`, `bar_body_rng_0` |
| 500ETF | single | Cluster 16 | 7 | 0.2717 | `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_clamp_diff__max_up_ret__early_late_momentum_divergence`, `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`, `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`, `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` |
| 500ETF | single | Cluster 17 | 2 | 0.2717 | `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `combo_max__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 18 | 1 | 0.2717 | `combo_max__net_volume_flow__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 19 | 2 | 0.2717 | `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 500ETF | single | Cluster 20 | 2 | 0.2717 | `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `combo_max__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 21 | 2 | 0.2717 | `combo_mean__close_vs_open_range__bar_ret_0` | `combo_min__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 22 | 2 | 0.2717 | `combo_min__net_volume_flow__first_bar_sentiment` | `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` |
| 500ETF | single | Cluster 23 | 1 | 0.2717 | `combo_max__first_bar_sentiment__high_low_sequence_momentum` | _(none)_ |
| 500ETF | single | Cluster 24 | 2 | 0.2717 | `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | `combo_min__trend_bar_close_consistency__first_bar_return` |
| 500ETF | single | Cluster 25 | 2 | 0.2717 | `combo_min__net_volume_flow__bar_ret_0` | `combo_rank_min__net_volume_flow__bar_ret_0` |
| 500ETF | single | Cluster 26 | 4 | 0.2717 | `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `opening_drive_thrust_ratio`, `combo_mean__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 27 | 2 | 0.2717 | `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 28 | 1 | 0.2717 | `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | _(none)_ |
| 500ETF | single | Cluster 29 | 2 | 0.2717 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` |
| 500ETF | single | Cluster 30 | 2 | 0.2717 | `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` |
| 500ETF | single | Cluster 31 | 2 | 0.2717 | `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `combo_min__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 32 | 3 | 0.2717 | `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 33 | 2 | 0.2717 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` |
| 500ETF | single | Cluster 34 | 1 | 0.2717 | `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | _(none)_ |
| 500ETF | single | Cluster 35 | 5 | 0.2717 | `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`, `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 36 | 6 | 0.2717 | `combo_mean__first_bar_return__max_down_ret` | `combo_min__bar_ret_0__max_down_ret`, `combo_rank_min__bar_ret_0__max_down_ret`, `combo_max__bar_ret_0__max_down_ret`, `combo_rank_max__bar_ret_0__max_down_ret`, `combo_mean__first_bar_sentiment__max_down_ret` |
| 500ETF | single | Cluster 37 | 2 | 0.2717 | `combo_rank_min__max_up_ret__bar_ret_0` | `combo_mean__max_up_ret__first_bar_return` |
| 500ETF | single | Cluster 38 | 2 | 0.2717 | `combo_rank_max__max_up_ret__bar_ret_0` | `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` |
| 500ETF | single | Cluster 39 | 1 | 0.2717 | `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | _(none)_ |
| 500ETF | single | Cluster 40 | 2 | 0.2717 | `combo_sig_product__max_up_ret__early_body_momentum` | `combo_sig_product__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 41 | 2 | 0.2717 | `early_order_flow_imbalance` | `num_up_bars` |
| 500ETF | single | Cluster 42 | 3 | 0.2717 | `combo_mean__star50_limit_proximity_early__max_down_ret` | `combo_rank_min__star50_limit_proximity_early__max_down_ret`, `combo_min__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 43 | 2 | 0.2717 | `always_in_trend_persistence` | `micro_gap_trend_continuation` |
| 500ETF | single | Cluster 44 | 8 | 0.2717 | `volatility_expansion_trend_vector` | `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector`, `first_30min_return`, `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression`, `combo_min__close_vs_open_range__early_body_momentum`, `combo_min__early_body_momentum__max_down_ret`, `combo_max__close_vs_open_range__early_body_momentum`, `morning_volume_weighted_momentum` |
| 500ETF | single | Cluster 45 | 2 | 0.2717 | `combo_sig_product__first_bar_sentiment__early_body_momentum` | `volume_surge_direction` |
| 500ETF | single | Cluster 46 | 2 | 0.2717 | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | `combo_max__opening_drive_thrust_ratio__early_body_momentum` |
| 500ETF | single | Cluster 47 | 2 | 0.2717 | `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression` | `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 48 | 2 | 0.2717 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 49 | 2 | 0.2717 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` |
| 159915ETF | single | Cluster 0 | 2 | 0.2630 | `trend_bar_close_consistency` | `shaved_bar_trend_conviction` |
| 159915ETF | single | Cluster 1 | 1 | 0.2630 | `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 2 | 2 | 0.2630 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 3 | 1 | 0.2630 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | _(none)_ |
| 159915ETF | single | Cluster 4 | 3 | 0.2630 | `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 5 | 2 | 0.2630 | `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | `combo_diff__bar_body_rng_0__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 6 | 2 | 0.2630 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 7 | 2 | 0.2630 | `combo_max__bar_body_rng_0__impulse_bar_dominance` | `combo_max__bar_ret_0__impulse_bar_dominance` |
| 159915ETF | single | Cluster 8 | 1 | 0.2630 | `combo_min__bar_body_rng_0__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 9 | 2 | 0.2630 | `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 10 | 2 | 0.2630 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 11 | 2 | 0.2630 | `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_min__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 12 | 2 | 0.2630 | `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` |
| 159915ETF | single | Cluster 13 | 2 | 0.2630 | `combo_sig_product__max_up_ret__bar_body_rng_0` | `combo_sig_product__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 14 | 5 | 0.2630 | `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `combo_min__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`, `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` |
| 159915ETF | single | Cluster 15 | 1 | 0.2630 | `combo_mean__bar_body_rng_0__impulse_bar_dominance` | _(none)_ |
| 159915ETF | single | Cluster 16 | 2 | 0.2630 | `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0` | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 17 | 2 | 0.2630 | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 18 | 1 | 0.2630 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | _(none)_ |
| 159915ETF | single | Cluster 19 | 2 | 0.2630 | `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_max__opening_drive_thrust_ratio__bar_ret_0` |
| 159915ETF | single | Cluster 20 | 2 | 0.2630 | `combo_min__first_bar_sentiment__volatility_expansion_trend_vector` | `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 21 | 2 | 0.2630 | `combo_rank_max__max_up_ret__bar_body_rng_0` | `combo_max__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 22 | 2 | 0.2630 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_min__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 23 | 2 | 0.2630 | `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` |
| 159915ETF | single | Cluster 24 | 2 | 0.2630 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 25 | 1 | 0.2630 | `combo_max__first_bar_sentiment__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 26 | 1 | 0.2630 | `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 27 | 2 | 0.2630 | `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | `combo_mean__max_up_ret__first_bar_sentiment` |
| 159915ETF | single | Cluster 28 | 1 | 0.2630 | `combo_max__first_bar_return__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 29 | 1 | 0.2630 | `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | _(none)_ |
| 159915ETF | single | Cluster 30 | 2 | 0.2630 | `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 31 | 2 | 0.2630 | `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `combo_diff__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 32 | 1 | 0.2630 | `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 33 | 2 | 0.2630 | `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 34 | 1 | 0.2630 | `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 35 | 2 | 0.2630 | `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 36 | 6 | 0.2630 | `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`, `combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`, `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`, `combo_mean__limit_down_proximity_early__impulse_bar_dominance`, `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance` |
| 159915ETF | single | Cluster 37 | 12 | 0.2630 | `combo_min__max_up_ret__first_bar_sentiment` | `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`, `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector`, `bar_body_rng_0`, `combo_min__bar_body_rng_0__volume_weighted_price_position`, `combo_rank_max__bar_body_rng_0__volume_weighted_price_position`, `combo_mean__first_bar_return__volume_weighted_price_position`, `combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return`, `combo_max__first_bar_sentiment__first_bar_return`, `combo_sig_product__first_bar_sentiment__first_bar_return`, `combo_ratio__bar_ret_0__volume_weighted_price_position`, `combo_rank_max__max_up_ret__first_bar_sentiment` |
| 159915ETF | single | Cluster 38 | 8 | 0.2630 | `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`, `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`, `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_diff__limit_down_proximity_early__demark_setup_reversal_early`, `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early`, `combo_sig_product__star50_limit_proximity_early__bar_ret_0`, `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 39 | 7 | 0.2630 | `combo_max__impulse_bar_dominance__volatility_expansion_trend_vector` | `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector`, `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position`, `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`, `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector`, `combo_rank_min__max_up_ret__impulse_bar_dominance`, `close_vs_open_range` |
| 159915ETF | single | Cluster 40 | 7 | 0.2630 | `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`, `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`, `combo_max__bar_ret_0__limit_down_proximity_early`, `combo_max__star50_limit_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 41 | 2 | 0.2630 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` |
| 159915ETF | single | Cluster 42 | 6 | 0.2630 | `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | `opening_drive_thrust_ratio`, `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_min__opening_drive_thrust_ratio__max_up_ret`, `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` |
| 159915ETF | single | Cluster 43 | 2 | 0.2630 | `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 44 | 8 | 0.2630 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`, `combo_rank_min__max_up_ret__volatility_expansion_trend_vector`, `combo_max__max_up_ret__volatility_expansion_trend_vector`, `max_up_ret`, `combo_rank_max__max_up_ret__volatility_expansion_trend_vector`, `combo_mean__max_up_ret__impulse_bar_dominance`, `net_volume_flow` |
| 159915ETF | single | Cluster 45 | 1 | 0.2630 | `combo_rank_min__max_up_ret__star50_limit_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 46 | 2 | 0.2630 | `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 47 | 1 | 0.2630 | `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 48 | 2 | 0.2630 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 49 | 2 | 0.2630 | `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 50 | 1 | 0.2630 | `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 51 | 10 | 0.2630 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`, `combo_min__bar_body_rng_0__limit_down_proximity_early`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`, `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`, `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`, `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_mean__first_bar_sentiment__limit_down_proximity_early` |
| 159915ETF | single | Cluster 52 | 4 | 0.2630 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_min__star50_limit_proximity_early__volume_weighted_price_position`, `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`, `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_min__bar_body_rng_0__volume_surge_direction` | `min` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_max__bar_ret_0__volume_surge_direction` | `max` | a=`bar_ret_0`, b=`volume_surge_direction` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__first_bar_return__volume_surge_direction` | `rank_max` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | `mean` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | `min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_mean` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__max_up_ret__volume_surge_direction` | `rank_max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_mean__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_mean` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_surge_direction` | `mean` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_max__first_bar_return__bar_body_rng_0` | `max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | `rank_max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | `max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_max__max_up_ret__volume_surge_direction` | `max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_median__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`first_bar_return`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `rank_max` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | `rank_max` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_max__opening_drive_thrust_ratio__volume_surge_direction` | `max` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`first_bar_return`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `tri_median` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__bar_ret_0` | `mean` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_mean__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_mean` | a=`volume_weighted_price_position`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_min` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | `sig_product` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_rank_min__max_up_ret__first_bar_return` | `rank_min` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_rank_min__max_up_ret__volume_surge_direction` | `rank_min` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_max__first_bar_return__first_bar_sentiment` | `max` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_min__max_up_ret__volume_surge_direction` | `min` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__bar_ret_0__volume_surge_direction` | `min` | a=`bar_ret_0`, b=`volume_surge_direction` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`opening_drive_thrust_ratio` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | `tri_median` | a=`smooth_momentum_structure`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | `sig_product` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_rank_max__volume_weighted_price_position__volume_surge_direction` | `rank_max` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | `sig_product` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_tri_mean__volume_weighted_momentum_acceleration__max_up_ret__first_bar_return` | `tri_mean` | a=`volume_weighted_momentum_acceleration`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_ret_0` | `tri_median` | a=`volume_weighted_momentum_acceleration`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | `mean` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | `min` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_max` | a=`volume_weighted_price_position`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_sig_product__max_up_ret__first_bar_return` | `sig_product` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | `tri_max` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_sig_product__bar_body_rng_0__volume_surge_direction` | `sig_product` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_mean__first_bar_sentiment__volume_surge_direction` | `mean` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_min__first_bar_return__first_bar_sentiment` | `min` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio` | `tri_mean` | a=`volume_weighted_momentum_acceleration`, b=`bar_ret_0`, c=`opening_drive_thrust_ratio` |
| `combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_ratio__volume_surge_direction__volume_weighted_price_position` | `ratio` | a=`volume_surge_direction`, b=`volume_weighted_price_position` |
| `combo_ratio__first_bar_return__volume_surge_direction` | `ratio` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_ratio__max_up_ret__bar_vol_0` | `ratio` | a=`max_up_ret`, b=`bar_vol_0` |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | `rank_min` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_min__net_volume_flow__first_bar_sentiment` | `min` | a=`net_volume_flow`, b=`first_bar_sentiment` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`net_volume_flow` |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`body_size_progression` |
| `combo_min__net_volume_flow__bar_ret_0` | `min` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__close_vs_open_range__bar_ret_0` | `mean` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | `clamp_diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` | `mean` | a=`volatility_expansion_trend_vector`, b=`first_bar_sentiment` |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_mean` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_rank_min__net_volume_flow__bar_ret_0` | `rank_min` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_mean__first_bar_return__max_down_ret` | `mean` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | `rank_max` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`net_volume_flow` |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_min__first_bar_sentiment__bar_ret_0` | `min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`trend_day_regime_conviction` |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | `rank_min` | a=`trend_bar_close_consistency`, b=`bar_ret_0` |
| `combo_min__trend_bar_close_consistency__first_bar_return` | `min` | a=`trend_bar_close_consistency`, b=`first_bar_return` |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | `mean` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_min` | a=`max_up_ret`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | `max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_rank_min__max_up_ret__bar_ret_0` | `rank_min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_mean__max_up_ret__first_bar_return` | `mean` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | `rank_max` | a=`volatility_expansion_trend_vector`, b=`bar_ret_0` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_min` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_min__close_vs_open_range__first_bar_return` | `min` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_min__bar_ret_0__max_down_ret` | `min` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__early_body_momentum` | `sig_product` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`net_volume_flow`, c=`body_size_progression` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`trend_bar_close_consistency` |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`body_size_progression` |
| `combo_rank_min__bar_ret_0__max_down_ret` | `rank_min` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | `min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`smooth_momentum_structure` |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_max` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | `sig_product` | a=`volatility_expansion_trend_vector`, b=`first_bar_return` |
| `combo_max__net_volume_flow__max_down_ret` | `max` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | `rank_max` | a=`net_volume_flow`, b=`first_bar_sentiment` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | `tri_median` | a=`max_up_ret`, b=`net_volume_flow`, c=`body_size_progression` |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | `sig_product` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_min__early_body_momentum__max_down_ret` | `min` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_sig_product__net_volume_flow__first_bar_return` | `sig_product` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_min__close_vs_open_range__early_body_momentum` | `min` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `min` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_max__close_vs_open_range__early_body_momentum` | `max` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_max__first_bar_sentiment__bar_ret_0` | `max` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_mean__first_bar_sentiment__max_down_ret` | `mean` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_max__close_vs_open_range__max_down_ret` | `max` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`first_bar_sentiment` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | `max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_max__first_bar_sentiment__high_low_sequence_momentum` | `max` | a=`first_bar_sentiment`, b=`high_low_sequence_momentum` |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`early_late_momentum_divergence` |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | `rank_min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | `max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range` | `rel_diff` | a=`volatility_expansion_trend_vector`, b=`close_vs_open_range` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | `sig_product` | a=`star50_limit_proximity_early`, b=`early_body_momentum` |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_sig_product__net_volume_flow__max_down_ret` | `sig_product` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | `sig_product` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_max__star50_limit_proximity_early__max_down_ret` | `max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | `min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | `rel_diff` | a=`bar_body_rng_0`, b=`demark_setup_reversal_early` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_diff__bar_body_rng_0__demark_setup_reversal_early` | `diff` | a=`bar_body_rng_0`, b=`demark_setup_reversal_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | `mean` | a=`bar_body_rng_0`, b=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | `min` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | `rank_min` | a=`limit_down_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `min` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | `mean` | a=`first_bar_return`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `mean` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | `sig_product` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | `tri_mean` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `rank_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_max__max_up_ret__bar_body_rng_0` | `max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_max__impulse_bar_dominance__volatility_expansion_trend_vector` | `max` | a=`impulse_bar_dominance`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector` | `min` | a=`impulse_bar_dominance`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`star50_limit_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_min__bar_body_rng_0__impulse_bar_dominance` | `min` | a=`bar_body_rng_0`, b=`impulse_bar_dominance` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | `max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | `sig_product` | a=`bar_body_rng_0`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | `tri_median` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_mean__first_bar_sentiment__limit_down_proximity_early` | `mean` | a=`first_bar_sentiment`, b=`limit_down_proximity_early` |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | `max` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | `rank_max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | `mean` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_min__first_bar_sentiment__volatility_expansion_trend_vector` | `min` | a=`first_bar_sentiment`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | `mean` | a=`bar_body_rng_0`, b=`impulse_bar_dominance` |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | `max` | a=`bar_body_rng_0`, b=`impulse_bar_dominance` |
| `combo_mean__max_up_ret__impulse_bar_dominance` | `mean` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | `ratio` | a=`volatility_expansion_trend_vector`, b=`volume_weighted_price_position` |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | `max` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | `rank_min` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_mean__max_up_ret__first_bar_sentiment` | `mean` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector` | `sig_product` | a=`impulse_bar_dominance`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | `sig_product` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | `rank_max` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | `rank_min` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | `min` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_max__first_bar_sentiment__volatility_expansion_trend_vector` | `max` | a=`first_bar_sentiment`, b=`volatility_expansion_trend_vector` |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__max_up_ret__volume_weighted_price_position` | `min` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | `rank_max` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_buy_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_mean__first_bar_return__volume_weighted_price_position` | `mean` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `rank_max` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `max` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_max__bar_ret_0__impulse_bar_dominance` | `max` | a=`bar_ret_0`, b=`impulse_bar_dominance` |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | `rank_min` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return` | `tri_min` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | `sig_product` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | `tri_max` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_min__max_up_ret__first_bar_return` | `min` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_diff__limit_down_proximity_early__demark_setup_reversal_early` | `diff` | a=`limit_down_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early` | `rel_diff` | a=`rbreaker_buy_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_max` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_max__first_bar_sentiment__first_bar_return` | `max` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | `mean` | a=`limit_down_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__bar_ret_0__limit_down_proximity_early` | `max` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | `sig_product` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | `sig_product` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | `max` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | `max` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | `sig_product` | a=`yesterday_first_30min_return`, b=`yesterday_early_trend` |
| `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance` | `rank_min` | a=`limit_down_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
