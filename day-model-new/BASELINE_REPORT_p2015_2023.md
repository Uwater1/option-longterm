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
| 300ETF | single | 1,285 | 402 | 253 | 165 | 158 | 145 | 132 | 132 | 51 | 51 | 26 | `[5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (26 clusters)]` |
| 300ETF | long | 579 | 40 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 586 | 93 | 26 | 26 | 5 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | single | 1,244 | 391 | 339 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | long | 361 | 46 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 50ETF | short | 317 | 39 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 3,222 | 1,397 | 1,157 | 1,032 | 1,026 | 868 | 853 | 853 | 215 | 215 | 73 | `[14, 13, 13, 10, 7, 7, 6, 6, 5, 5, 5, 5, ... (73 clusters)]` |
| 500ETF | long | 1,360 | 108 | 62 | 62 | 29 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | short | 426 | 54 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | single | 1,888 | 726 | 417 | 312 | 312 | 198 | 196 | 196 | 79 | 78 | 26 | `[15, 6, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2, ... (26 clusters)]` |
| 159915ETF | long | 1,121 | 108 | 48 | 48 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 159915ETF | short | 302 | 47 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 51 | 26 | `[5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (26 clusters)]` | +0.1259 | [+0.0830, +0.1684] | +0.2315 | [+0.1102, +0.3281] | +0.8909 | 5.92% | 1.5075 | 4.28% | 1.1048 | 2.0765 | 5.08% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 215 | 73 | `[14, 13, 13, 10, 7, 7, 6, 6, 5, 5, 5, 5, ... (73 clusters)]` | +0.1795 | [+0.1382, +0.2235] | +0.2897 | [+0.1924, +0.3806] | +0.9758 | 8.23% | 1.7502 | 6.61% | 1.4215 | 2.6390 | 3.75% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 78 | 26 | `[15, 6, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2, ... (26 clusters)]` | +0.1682 | [+0.1227, +0.2124] | +0.2691 | [+0.1865, +0.3578] | +0.9030 | 8.65% | 1.6055 | 7.04% | 1.3187 | 2.1064 | 8.93% |
| 159915ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 51 | 26 | `[5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (26 clusters)]` | +0.0758 | [+0.0024, +0.1511] | +0.1425* | [-0.0287, +0.3044] | +0.7939 | 3.37% | 0.9785 | 1.76% | 0.5176 | 0.9955 | 3.05% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 215 | 73 | `[14, 13, 13, 10, 7, 7, 6, 6, 5, 5, 5, 5, ... (73 clusters)]` | +0.1117 | [+0.0344, +0.1816] | +0.1035* | [-0.0350, +0.2426] | +0.8909 | 4.06% | 0.9464 | 2.59% | 0.6077 | 1.0861 | 4.31% |
| 500ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 78 | 26 | `[15, 6, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2, ... (26 clusters)]` | +0.1434 | [+0.0616, +0.2126] | +0.2830 | [+0.1068, +0.4563] | +0.7333 | 10.54% | 1.5641 | 9.14% | 1.3716 | 3.7201 | 5.88% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 8 | +1 | +0.1187 | +0.2800 | +0.2807 | 0.0000 | +0.7370 | +0.7191 | 0.872 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1188 | +0.2764 | +0.2775 | 0.0000 | +0.8678 | +0.8074 | 0.000 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 2 | +1 | +0.1156 | +0.2691 | +0.2697 | 0.0000 | +0.5471 | +0.7072 | 0.773 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1153 | +0.2658 | +0.2670 | 0.0000 | +0.8242 | +0.7884 | 0.905 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 19 | +1 | +0.1119 | +0.2634 | +0.2636 | 0.0000 | +0.6357 | +0.7155 | 0.822 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 15 | +1 | +0.1132 | +0.2593 | +0.2602 | 0.0000 | +0.6700 | +0.7042 | 0.791 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 7 | +1 | +0.1197 | +0.2426 | +0.2433 | 0.0000 | +0.5789 | +0.7129 | 0.941 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 20 | +1 | +0.0941 | +0.2409 | +0.2417 | 0.0000 | +0.5785 | +0.7062 | 0.853 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1165 | +0.2329 | +0.2342 | 0.0000 | +0.7329 | +0.7678 | 0.883 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 17 | +1 | +0.0872 | +0.2244 | +0.2251 | 0.0000 | +0.7215 | +0.7571 | 0.749 |
| `rbreaker_sell_setup_proximity_early` | Cluster 22 | +1 | +0.0965 | +0.2243 | +0.2248 | 0.0000 | +0.5652 | +0.7360 | 0.818 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 7 | +1 | +0.1235 | +0.2218 | +0.2227 | 0.0000 | +0.6181 | +0.7427 | 0.873 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 21 | +1 | +0.0995 | +0.2197 | +0.2208 | 0.0000 | +0.5241 | +0.6769 | 0.920 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 20 | +1 | +0.0912 | +0.2181 | +0.2193 | 0.0000 | +0.5315 | +0.6533 | 0.895 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 17 | +1 | +0.0811 | +0.2172 | +0.2175 | 0.0000 | +0.7860 | +0.7750 | 0.924 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 15 | +1 | +0.1074 | +0.2134 | +0.2144 | 0.0000 | +0.6836 | +0.7191 | 0.935 |
| `combo_tri_mean__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 14 | +1 | +0.0980 | +0.2134 | +0.2142 | 0.0000 | +0.5718 | +0.7155 | 0.949 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.0859 | +0.2129 | +0.2140 | 0.0000 | +0.6572 | +0.7483 | 0.943 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 21 | +1 | +0.1222 | +0.2128 | +0.2133 | 0.0000 | +0.5504 | +0.7062 | 0.921 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.0898 | +0.2103 | +0.2113 | 0.0002 | +0.5473 | +0.7083 | 0.880 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 13 | +1 | +0.0935 | +0.2101 | +0.2106 | 0.0002 | +0.6761 | +0.7432 | 0.904 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 13 | +1 | +0.0890 | +0.2083 | +0.2087 | 0.0002 | +0.5712 | +0.6918 | 0.873 |
| `combo_min__max_up_ret__volume_weighted_price_position` | Cluster 18 | +1 | +0.0878 | +0.2076 | +0.2080 | 0.0002 | +0.6010 | +0.7185 | 0.922 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 20 | +1 | +0.0893 | +0.2054 | +0.2064 | 0.0002 | +0.3937 | +0.6636 | 0.938 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 0 | +1 | +0.0947 | +0.2018 | +0.2028 | 0.0002 | +0.4961 | +0.6831 | 0.942 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 23 | +1 | +0.0963 | +0.2000 | +0.2009 | 0.0002 | +0.5073 | +0.6882 | 0.919 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 25 | +1 | +0.0908 | +0.1980 | +0.1997 | 0.0002 | +0.4755 | +0.6733 | 0.872 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 17 | +1 | +0.0754 | +0.1940 | +0.1950 | 0.0002 | +0.7475 | +0.7807 | 0.885 |
| `combo_max__first_bar_return__bar_body_rng_0` | Cluster 23 | +1 | +0.0944 | +0.1938 | +0.1949 | 0.0002 | +0.5724 | +0.7191 | 0.939 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | Cluster 12 | +1 | +0.0742 | +0.1929 | +0.1930 | 0.0002 | +0.4284 | +0.6718 | 0.592 |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | Cluster 3 | +1 | +0.0665 | +0.1925 | +0.1927 | 0.0002 | +0.5928 | +0.7401 | 0.795 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Cluster 3 | +1 | +0.0660 | +0.1858 | +0.1864 | 0.0004 | +0.6574 | +0.7488 | 0.742 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 25 | +1 | +0.0872 | +0.1852 | +0.1865 | 0.0004 | +0.5869 | +0.7057 | 0.938 |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Cluster 1 | +1 | +0.0902 | +0.1839 | +0.1847 | 0.0004 | +0.5811 | +0.7026 | 0.906 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 23 | +1 | +0.0917 | +0.1836 | +0.1849 | 0.0004 | +0.5672 | +0.7304 | 0.747 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 6 | +1 | +0.0833 | +0.1830 | +0.1846 | 0.0004 | +0.6883 | +0.7576 | 0.768 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 16 | +1 | +0.0910 | +0.1818 | +0.1831 | 0.0004 | +0.5267 | +0.6780 | 0.880 |
| `combo_mean__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0842 | +0.1748 | +0.1761 | 0.0006 | +0.7139 | +0.7442 | 0.948 |
| `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` | Cluster 3 | +1 | +0.0619 | +0.1738 | +0.1741 | 0.0006 | +0.4638 | +0.6965 | 0.910 |
| `star50_limit_proximity_early` | Cluster 22 | +1 | +0.0915 | +0.1720 | +0.1727 | 0.0012 | +0.4589 | +0.6954 | 0.945 |
| `max_up_ret` | Cluster 5 | +1 | +0.0767 | +0.1676 | +0.1683 | 0.0018 | +0.3955 | +0.6549 | 0.901 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0803 | +0.1660 | +0.1672 | 0.0018 | +0.6402 | +0.7191 | 0.879 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0777 | +0.1660 | +0.1670 | 0.0018 | +0.6048 | +0.7381 | 0.802 |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 2 | +1 | +0.1032 | +0.1643 | +0.1656 | 0.0018 | +0.6259 | +0.7160 | 0.919 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 23 | +1 | +0.0929 | +0.1632 | +0.1640 | 0.0018 | +0.4797 | +0.6564 | 0.889 |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | Cluster 24 | +1 | +0.0901 | +0.1492 | +0.1501 | 0.0030 | +0.5479 | +0.7016 | 0.878 |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | Cluster 1 | +1 | +0.0848 | +0.1476 | +0.1484 | 0.0036 | +0.6663 | +0.7149 | 0.931 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Cluster 9 | +1 | +0.0894 | +0.1467 | +0.1473 | 0.0040 | +0.4503 | +0.6646 | 0.947 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 19 | +1 | +0.0757 | +0.1356 | +0.1361 | 0.0080 | +0.4172 | +0.6888 | 0.792 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 9 | +1 | +0.0768 | +0.1267 | +0.1277 | 0.0146 | +0.5022 | +0.6805 | 0.927 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 9 | +1 | +0.0890 | +0.1262 | +0.1270 | 0.0152 | +0.4936 | +0.6841 | 0.834 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 2 | +1 | +0.1763 | +0.3308 | +0.3324 | 0.0000 | +1.1222 | +0.8567 | 0.944 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 45 | +1 | +0.1603 | +0.3202 | +0.3220 | 0.0000 | +0.8630 | +0.7925 | 0.837 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 45 | +1 | +0.1776 | +0.3148 | +0.3165 | 0.0000 | +1.1131 | +0.8377 | 0.950 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 45 | +1 | +0.1544 | +0.3075 | +0.3095 | 0.0000 | +0.9528 | +0.8197 | 0.859 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 38 | +1 | +0.1240 | +0.3062 | +0.3081 | 0.0000 | +0.7219 | +0.7560 | 0.943 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Cluster 38 | +1 | +0.1605 | +0.3026 | +0.3035 | 0.0000 | +1.1008 | +0.8279 | 0.936 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 26 | +1 | +0.1641 | +0.3025 | +0.3043 | 0.0000 | +0.7337 | +0.7807 | 0.817 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 43 | +1 | +0.1702 | +0.2962 | +0.2969 | 0.0000 | +0.8348 | +0.7920 | 0.840 |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 33 | +1 | +0.1407 | +0.2956 | +0.2976 | 0.0000 | +0.7345 | +0.7987 | 0.942 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Cluster 38 | +1 | +0.1310 | +0.2956 | +0.2974 | 0.0000 | +0.7405 | +0.7406 | 0.872 |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | Cluster 66 | +1 | +0.1817 | +0.2952 | +0.2964 | 0.0000 | +0.8010 | +0.7807 | 0.941 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 38 | +1 | +0.1531 | +0.2943 | +0.2960 | 0.0000 | +0.9313 | +0.8264 | 0.916 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 57 | +1 | +0.1685 | +0.2912 | +0.2924 | 0.0000 | +0.8171 | +0.7771 | 0.780 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 3 | +1 | +0.1713 | +0.2906 | +0.2921 | 0.0000 | +0.9437 | +0.8095 | 0.862 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 3 | +1 | +0.1596 | +0.2893 | +0.2907 | 0.0000 | +0.8691 | +0.8120 | 0.937 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | Cluster 3 | +1 | +0.1664 | +0.2882 | +0.2898 | 0.0000 | +0.8508 | +0.7853 | 0.927 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 57 | +1 | +0.1711 | +0.2877 | +0.2893 | 0.0000 | +0.6299 | +0.7355 | 0.834 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 19 | +1 | +0.1629 | +0.2850 | +0.2868 | 0.0000 | +0.9770 | +0.8356 | 0.928 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 34 | +1 | +0.1672 | +0.2845 | +0.2863 | 0.0000 | +1.0054 | +0.8444 | 0.892 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 3 | +1 | +0.1687 | +0.2841 | +0.2851 | 0.0000 | +0.9359 | +0.8320 | 0.945 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Cluster 38 | +1 | +0.1317 | +0.2835 | +0.2853 | 0.0000 | +0.7668 | +0.7576 | 0.945 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 55 | +1 | +0.1765 | +0.2827 | +0.2841 | 0.0000 | +0.8713 | +0.7761 | 0.854 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 19 | +1 | +0.1590 | +0.2814 | +0.2830 | 0.0000 | +0.9932 | +0.8356 | 0.901 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 38 | +1 | +0.1410 | +0.2807 | +0.2818 | 0.0000 | +0.7409 | +0.7463 | 0.944 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 57 | +1 | +0.1697 | +0.2790 | +0.2806 | 0.0000 | +0.6106 | +0.7155 | 0.905 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 55 | +1 | +0.1677 | +0.2765 | +0.2774 | 0.0000 | +0.7535 | +0.7838 | 0.911 |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 38 | +1 | +0.1136 | +0.2763 | +0.2769 | 0.0000 | +0.6910 | +0.7643 | 0.947 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Cluster 66 | +1 | +0.1754 | +0.2762 | +0.2774 | 0.0000 | +0.7731 | +0.7668 | 0.950 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 2 | +1 | +0.1720 | +0.2752 | +0.2762 | 0.0000 | +0.7229 | +0.7345 | 0.874 |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 3 | +1 | +0.1354 | +0.2739 | +0.2751 | 0.0000 | +0.9157 | +0.8511 | 0.950 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 25 | +1 | +0.1585 | +0.2737 | +0.2758 | 0.0000 | +0.8841 | +0.7920 | 0.908 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 38 | +1 | +0.1207 | +0.2737 | +0.2753 | 0.0000 | +0.6781 | +0.7401 | 0.832 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 57 | +1 | +0.1447 | +0.2736 | +0.2754 | 0.0000 | +0.5541 | +0.6703 | 0.945 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 38 | +1 | +0.1202 | +0.2722 | +0.2729 | 0.0000 | +0.7559 | +0.7776 | 0.949 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Cluster 39 | +1 | +0.1484 | +0.2722 | +0.2732 | 0.0000 | +0.7569 | +0.7494 | 0.766 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 38 | +1 | +0.1429 | +0.2720 | +0.2731 | 0.0000 | +0.8170 | +0.7797 | 0.944 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 54 | +1 | +0.1602 | +0.2716 | +0.2730 | 0.0000 | +0.6443 | +0.7339 | 0.904 |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | Cluster 57 | +1 | +0.1624 | +0.2705 | +0.2722 | 0.0000 | +0.7158 | +0.7571 | 0.555 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 3 | +1 | +0.1643 | +0.2677 | +0.2692 | 0.0000 | +0.7719 | +0.7756 | 0.932 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 38 | +1 | +0.1191 | +0.2676 | +0.2691 | 0.0000 | +0.6455 | +0.7119 | 0.915 |
| `combo_rank_min__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 38 | +1 | +0.1041 | +0.2661 | +0.2673 | 0.0000 | +0.6435 | +0.7206 | 0.947 |
| `combo_min__opening_drive_thrust_ratio__high_low_sequence_momentum` | Cluster 3 | +1 | +0.1351 | +0.2659 | +0.2677 | 0.0000 | +0.6530 | +0.7355 | 0.932 |
| `combo_max__opening_drive_thrust_ratio__opening_momentum_score` | Cluster 3 | +1 | +0.1574 | +0.2658 | +0.2668 | 0.0000 | +0.9146 | +0.8136 | 0.943 |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | Cluster 3 | +1 | +0.1437 | +0.2649 | +0.2672 | 0.0000 | +0.7841 | +0.7771 | 0.948 |
| `combo_mean__max_up_ret__net_volume_flow` | Cluster 49 | +1 | +0.1544 | +0.2642 | +0.2659 | 0.0000 | +1.0014 | +0.8326 | 0.899 |
| `combo_rank_min__close_vs_open_range__first_bar_sentiment` | Cluster 43 | +1 | +0.1391 | +0.2639 | +0.2648 | 0.0000 | +0.7718 | +0.7946 | 0.874 |
| `opening_drive_thrust_ratio` | Cluster 29 | +1 | +0.1682 | +0.2632 | +0.2649 | 0.0000 | +0.7902 | +0.8084 | 0.905 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 3 | +1 | +0.1535 | +0.2626 | +0.2641 | 0.0000 | +0.8366 | +0.7961 | 0.907 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 26 | +1 | +0.1691 | +0.2621 | +0.2638 | 0.0000 | +0.8295 | +0.8007 | 0.940 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 66 | +1 | +0.1804 | +0.2620 | +0.2630 | 0.0000 | +0.9544 | +0.8038 | 0.859 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 58 | +1 | +0.1598 | +0.2613 | +0.2624 | 0.0000 | +0.6663 | +0.7108 | 0.939 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Cluster 38 | +1 | +0.1405 | +0.2602 | +0.2611 | 0.0000 | +0.7573 | +0.7524 | 0.891 |
| `combo_mean__star50_limit_proximity_early__opening_momentum_score` | Cluster 38 | +1 | +0.1313 | +0.2601 | +0.2609 | 0.0000 | +0.7447 | +0.7632 | 0.901 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 1 | +1 | +0.1782 | +0.2597 | +0.2611 | 0.0000 | +0.7347 | +0.7417 | 0.943 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 3 | +1 | +0.1490 | +0.2589 | +0.2608 | 0.0000 | +0.7877 | +0.7653 | 0.947 |
| `combo_min__net_volume_flow__impulse_bar_dominance` | Cluster 36 | +1 | +0.1047 | +0.2587 | +0.2603 | 0.0000 | +0.7012 | +0.7560 | 0.932 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 30 | +1 | +0.1418 | +0.2581 | +0.2597 | 0.0000 | +0.7611 | +0.7745 | 0.937 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 66 | +1 | +0.1842 | +0.2575 | +0.2589 | 0.0000 | +0.8809 | +0.8043 | 0.850 |
| `combo_mean__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 33 | +1 | +0.1351 | +0.2569 | +0.2586 | 0.0000 | +0.7503 | +0.7843 | 0.892 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Cluster 52 | +1 | +0.1243 | +0.2568 | +0.2574 | 0.0000 | +0.6319 | +0.7483 | 0.905 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | Cluster 17 | +1 | +0.1446 | +0.2567 | +0.2569 | 0.0000 | +0.6597 | +0.7339 | 0.796 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Cluster 66 | +1 | +0.1709 | +0.2551 | +0.2562 | 0.0000 | +0.9313 | +0.7802 | 0.933 |
| `combo_sig_product__max_up_ret__opening_momentum_score` | Cluster 39 | +1 | +0.1546 | +0.2543 | +0.2549 | 0.0000 | +0.5488 | +0.7026 | 0.755 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 14 | +1 | +0.1580 | +0.2540 | +0.2552 | 0.0000 | +0.6084 | +0.7242 | 0.921 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 31 | +1 | +0.1799 | +0.2530 | +0.2544 | 0.0000 | +0.8288 | +0.7699 | 0.916 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Cluster 66 | +1 | +0.1749 | +0.2498 | +0.2510 | 0.0000 | +1.0192 | +0.7910 | 0.000 |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | Cluster 9 | +1 | +0.1423 | +0.2497 | +0.2512 | 0.0000 | +0.5443 | +0.6975 | 0.877 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 14 | +1 | +0.1626 | +0.2494 | +0.2513 | 0.0000 | +0.6742 | +0.7483 | 0.936 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 25 | +1 | +0.1619 | +0.2487 | +0.2510 | 0.0000 | +0.9078 | +0.7802 | 0.943 |
| `net_volume_flow` | Cluster 72 | +1 | +0.1188 | +0.2475 | +0.2493 | 0.0000 | +0.7388 | +0.7756 | 0.949 |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Cluster 72 | +1 | +0.1173 | +0.2471 | +0.2478 | 0.0000 | +0.5524 | +0.7206 | 0.947 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 47 | +1 | +0.1258 | +0.2462 | +0.2482 | 0.0000 | +0.7698 | +0.7514 | 0.872 |
| `combo_max__max_up_ret__opening_momentum_score` | Cluster 51 | +1 | +0.1440 | +0.2456 | +0.2473 | 0.0000 | +0.8651 | +0.8017 | 0.943 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 47 | +1 | +0.1269 | +0.2448 | +0.2467 | 0.0000 | +0.7120 | +0.7350 | 0.778 |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | Cluster 72 | +1 | +0.1116 | +0.2448 | +0.2463 | 0.0000 | +0.4780 | +0.7011 | 0.929 |
| `combo_diff__max_up_ret__impulse_bar_dominance` | Cluster 4 | +1 | +0.0860 | +0.2440 | +0.2431 | 0.0000 | +0.4677 | +0.6667 | 0.945 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.1820 | +0.2437 | +0.2446 | 0.0000 | +0.6067 | +0.7211 | 0.947 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 66 | +1 | +0.1750 | +0.2436 | +0.2448 | 0.0000 | +0.9014 | +0.7761 | 0.914 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 31 | +1 | +0.1796 | +0.2426 | +0.2440 | 0.0000 | +0.6256 | +0.7447 | 0.891 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Cluster 72 | +1 | +0.1097 | +0.2423 | +0.2441 | 0.0000 | +0.6350 | +0.7458 | 0.924 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 39 | +1 | +0.1511 | +0.2415 | +0.2427 | 0.0000 | +0.5920 | +0.7103 | 0.920 |
| `combo_rank_max__max_up_ret__opening_momentum_score` | Cluster 51 | +1 | +0.1501 | +0.2412 | +0.2430 | 0.0000 | +0.8954 | +0.7966 | 0.890 |
| `combo_min__net_volume_flow__bar_ret_0` | Cluster 5 | +1 | +0.1279 | +0.2395 | +0.2414 | 0.0000 | +0.7200 | +0.7643 | 0.937 |
| `combo_clamp_diff__max_up_ret__impulse_bar_dominance` | Cluster 4 | +1 | +0.0858 | +0.2390 | +0.2381 | 0.0000 | +0.4653 | +0.6697 | 0.505 |
| `combo_rank_min__trend_bar_close_consistency__first_bar_return` | Cluster 5 | +1 | +0.1054 | +0.2390 | +0.2404 | 0.0000 | +0.6328 | +0.7155 | 0.946 |
| `combo_mean__net_volume_flow__close_vs_open_range` | Cluster 72 | +1 | +0.1170 | +0.2389 | +0.2406 | 0.0000 | +0.5893 | +0.7072 | 0.918 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 3 | +1 | +0.1351 | +0.2378 | +0.2396 | 0.0000 | +0.7319 | +0.7709 | 0.937 |
| `combo_mean__first_bar_sentiment__opening_momentum_score` | Cluster 6 | +1 | +0.1285 | +0.2378 | +0.2393 | 0.0000 | +0.5810 | +0.7524 | 0.909 |
| `combo_min__max_up_ret__close_vs_open_range` | Cluster 52 | +1 | +0.1283 | +0.2377 | +0.2385 | 0.0000 | +0.7087 | +0.7735 | 0.887 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 30 | +1 | +0.1401 | +0.2373 | +0.2394 | 0.0000 | +0.6639 | +0.7278 | 0.846 |
| `combo_mean__max_up_ret__close_vs_open_range` | Cluster 49 | +1 | +0.1503 | +0.2364 | +0.2379 | 0.0000 | +0.7792 | +0.7740 | 0.937 |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | Cluster 44 | +1 | +0.1468 | +0.2363 | +0.2374 | 0.0000 | +0.8415 | +0.7843 | 0.909 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 40 | +1 | +0.1373 | +0.2358 | +0.2368 | 0.0000 | +0.5414 | +0.6970 | 0.926 |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | Cluster 3 | +1 | +0.1524 | +0.2347 | +0.2360 | 0.0000 | +0.6128 | +0.7786 | 0.594 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 27 | +1 | +0.1595 | +0.2337 | +0.2357 | 0.0000 | +0.5864 | +0.7581 | 0.891 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 18 | +1 | +0.1626 | +0.2336 | +0.2356 | 0.0000 | +0.5429 | +0.7370 | 0.907 |
| `combo_min__max_up_ret__high_low_sequence_momentum` | Cluster 52 | +1 | +0.1291 | +0.2334 | +0.2342 | 0.0000 | +0.6834 | +0.7442 | 0.942 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | Cluster 24 | +1 | +0.1781 | +0.2334 | +0.2353 | 0.0000 | +0.6913 | +0.7319 | 0.908 |
| `combo_max__max_up_ret__close_vs_open_range` | Cluster 56 | +1 | +0.1616 | +0.2333 | +0.2353 | 0.0000 | +0.7526 | +0.7391 | 0.879 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | Cluster 6 | +1 | +0.1379 | +0.2333 | +0.2348 | 0.0000 | +0.5756 | +0.7072 | 0.905 |
| `combo_mean__net_volume_flow__first_bar_return` | Cluster 11 | +1 | +0.1453 | +0.2322 | +0.2340 | 0.0000 | +0.6074 | +0.7252 | 0.911 |
| `max_up_ret` | Cluster 54 | +1 | +0.1619 | +0.2317 | +0.2328 | 0.0000 | +0.6107 | +0.7370 | 0.948 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 18 | +1 | +0.1639 | +0.2309 | +0.2323 | 0.0000 | +0.7465 | +0.7756 | 0.829 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Cluster 16 | +1 | +0.1089 | +0.2306 | +0.2314 | 0.0000 | +0.5900 | +0.7242 | 0.899 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 22 | +1 | +0.1764 | +0.2301 | +0.2316 | 0.0000 | +0.7031 | +0.7761 | 0.920 |
| `combo_max__first_bar_sentiment__opening_momentum_score` | Cluster 10 | +1 | +0.1304 | +0.2299 | +0.2313 | 0.0000 | +0.6076 | +0.7334 | 0.944 |
| `combo_rank_max__first_bar_return__max_down_ret` | Cluster 20 | +1 | +0.1606 | +0.2295 | +0.2317 | 0.0000 | +0.6319 | +0.7103 | 0.877 |
| `combo_mean__max_up_ret__bar_ret_0` | Cluster 18 | +1 | +0.1709 | +0.2289 | +0.2302 | 0.0000 | +0.6458 | +0.7206 | 0.929 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | Cluster 72 | +1 | +0.1117 | +0.2287 | +0.2301 | 0.0000 | +0.5667 | +0.7334 | 0.943 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Cluster 56 | +1 | +0.1611 | +0.2286 | +0.2307 | 0.0000 | +0.8236 | +0.7781 | 0.947 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 18 | +1 | +0.1639 | +0.2285 | +0.2300 | 0.0000 | +0.7050 | +0.7678 | 0.822 |
| `combo_max__max_up_ret__impulse_bar_dominance` | Cluster 71 | +1 | +0.1337 | +0.2280 | +0.2294 | 0.0000 | +0.5274 | +0.7257 | 0.855 |
| `combo_min__close_vs_open_range__first_bar_return` | Cluster 12 | +1 | +0.1185 | +0.2276 | +0.2295 | 0.0000 | +0.7442 | +0.7524 | 0.906 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_momentum_score` | Cluster 58 | +1 | +0.1441 | +0.2275 | +0.2284 | 0.0000 | +0.5344 | +0.6913 | 0.930 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 16 | +1 | +0.1183 | +0.2274 | +0.2283 | 0.0000 | +0.5771 | +0.6888 | 0.912 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | Cluster 9 | +1 | +0.1362 | +0.2270 | +0.2286 | 0.0000 | +0.5799 | +0.7108 | 0.895 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Cluster 53 | +1 | +0.1589 | +0.2267 | +0.2277 | 0.0000 | +0.7850 | +0.7899 | 0.939 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 0 | +1 | +0.1760 | +0.2247 | +0.2256 | 0.0000 | +0.5212 | +0.7021 | 0.866 |
| `combo_rank_min__close_vs_open_range__first_bar_return` | Cluster 12 | +1 | +0.1185 | +0.2241 | +0.2260 | 0.0000 | +0.7916 | +0.7684 | 0.902 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 39 | +1 | +0.1489 | +0.2233 | +0.2239 | 0.0000 | +0.7037 | +0.7437 | 0.753 |
| `combo_min__bar_ret_0__impulse_bar_dominance` | Cluster 69 | +1 | +0.0995 | +0.2233 | +0.2251 | 0.0000 | +0.6152 | +0.7227 | 0.932 |
| `trend_bar_close_consistency` | Cluster 72 | +1 | +0.0765 | +0.2230 | +0.2235 | 0.0000 | +0.4448 | +0.6918 | 0.950 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | Cluster 72 | +1 | +0.1076 | +0.2226 | +0.2243 | 0.0000 | +0.5686 | +0.7206 | 0.922 |
| `combo_mean__bar_ret_0__max_down_ret` | Cluster 21 | +1 | +0.1425 | +0.2220 | +0.2243 | 0.0000 | +0.5490 | +0.6518 | 0.845 |
| `combo_max__close_vs_open_range__impulse_bar_dominance` | Cluster 37 | +1 | +0.0879 | +0.2213 | +0.2226 | 0.0000 | +0.5649 | +0.7134 | 0.857 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 27 | +1 | +0.1590 | +0.2210 | +0.2237 | 0.0000 | +0.6806 | +0.7427 | 0.949 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1422 | +0.2208 | +0.2227 | 0.0000 | +0.5242 | +0.7124 | 0.876 |
| `combo_rank_max__opening_momentum_score__first_bar_return` | Cluster 13 | +1 | +0.1480 | +0.2208 | +0.2221 | 0.0000 | +0.7142 | +0.7401 | 0.938 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 46 | +1 | +0.1305 | +0.2203 | +0.2218 | 0.0000 | +0.5629 | +0.6795 | 0.933 |
| `combo_mean__volatility_expansion_trend_vector__impulse_bar_dominance` | Cluster 36 | +1 | +0.1052 | +0.2198 | +0.2213 | 0.0000 | +0.4795 | +0.6939 | 0.919 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 14 | +1 | +0.1542 | +0.2176 | +0.2187 | 0.0000 | +0.5720 | +0.7175 | 0.939 |
| `combo_rank_max__close_vs_open_range__first_bar_return` | Cluster 8 | +1 | +0.1631 | +0.2155 | +0.2168 | 0.0000 | +0.7266 | +0.7704 | 0.910 |
| `combo_max__close_vs_open_range__first_bar_return` | Cluster 8 | +1 | +0.1634 | +0.2151 | +0.2165 | 0.0000 | +0.7342 | +0.7766 | 0.750 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_momentum_score` | Cluster 58 | +1 | +0.1328 | +0.2150 | +0.2161 | 0.0000 | +0.4780 | +0.6687 | 0.926 |
| `combo_sig_product__close_vs_open_range__opening_momentum_score` | Cluster 72 | +1 | +0.1012 | +0.2149 | +0.2163 | 0.0000 | +0.4602 | +0.6959 | 0.938 |
| `combo_mean__close_vs_open_range__first_bar_return` | Cluster 11 | +1 | +0.1498 | +0.2132 | +0.2150 | 0.0000 | +0.7345 | +0.7766 | 0.911 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 0 | +1 | +0.1795 | +0.2126 | +0.2135 | 0.0000 | +0.6781 | +0.7406 | 0.889 |
| `combo_mean__net_volume_flow__max_down_ret` | Cluster 61 | +1 | +0.1285 | +0.2123 | +0.2142 | 0.0000 | +0.6531 | +0.7360 | 0.849 |
| `combo_mean__close_vs_open_range__impulse_bar_dominance` | Cluster 36 | +1 | +0.0986 | +0.2111 | +0.2126 | 0.0000 | +0.5092 | +0.7114 | 0.938 |
| `combo_rank_min__trend_bar_close_consistency__max_down_ret` | Cluster 62 | +1 | +0.1068 | +0.2101 | +0.2123 | 0.0000 | +0.5233 | +0.6898 | 0.947 |
| `combo_sig_product__first_bar_sentiment__opening_momentum_score` | Cluster 42 | +1 | +0.1323 | +0.2100 | +0.2111 | 0.0000 | +0.4841 | +0.7026 | 0.836 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 28 | +1 | +0.1611 | +0.2099 | +0.2116 | 0.0000 | +0.6553 | +0.7678 | 0.923 |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Cluster 16 | +1 | +0.1057 | +0.2093 | +0.2107 | 0.0000 | +0.5429 | +0.6569 | 0.940 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 28 | +1 | +0.1453 | +0.2093 | +0.2107 | 0.0000 | +0.6419 | +0.7720 | 0.889 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 0 | +1 | +0.1705 | +0.2091 | +0.2099 | 0.0000 | +0.4839 | +0.7129 | 0.928 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Cluster 17 | +1 | +0.1280 | +0.2083 | +0.2087 | 0.0000 | +0.5525 | +0.7108 | 0.923 |
| `combo_rank_min__close_vs_open_range__max_down_ret` | Cluster 65 | +1 | +0.1278 | +0.2083 | +0.2107 | 0.0000 | +0.5384 | +0.7031 | 0.867 |
| `combo_max__first_bar_return__max_down_ret` | Cluster 20 | +1 | +0.1553 | +0.2082 | +0.2102 | 0.0000 | +0.6162 | +0.7093 | 0.891 |
| `combo_rank_min__first_bar_return__max_down_ret` | Cluster 23 | +1 | +0.1276 | +0.2082 | +0.2105 | 0.0000 | +0.5260 | +0.6882 | 0.909 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 48 | +1 | +0.1405 | +0.2082 | +0.2096 | 0.0000 | +0.5216 | +0.6821 | 0.872 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Cluster 7 | +1 | +0.1361 | +0.2076 | +0.2092 | 0.0000 | +0.6319 | +0.7427 | 0.928 |
| `combo_max__opening_momentum_score__impulse_bar_dominance` | Cluster 37 | +1 | +0.0909 | +0.2062 | +0.2072 | 0.0000 | +0.5241 | +0.7329 | 0.914 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 59 | +1 | +0.1657 | +0.2060 | +0.2069 | 0.0000 | +0.6661 | +0.7678 | 0.930 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 59 | +1 | +0.1609 | +0.2059 | +0.2067 | 0.0000 | +0.6144 | +0.7232 | 0.806 |
| `combo_max__close_vs_open_range__opening_momentum_score` | Cluster 72 | +1 | +0.1020 | +0.2053 | +0.2064 | 0.0000 | +0.5463 | +0.7232 | 0.945 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 59 | +1 | +0.1578 | +0.2048 | +0.2053 | 0.0000 | +0.6479 | +0.7170 | 0.846 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 18 | +1 | +0.1641 | +0.2045 | +0.2055 | 0.0000 | +0.4603 | +0.6703 | 0.948 |
| `combo_min__close_vs_open_range__max_down_ret` | Cluster 65 | +1 | +0.1254 | +0.2037 | +0.2059 | 0.0000 | +0.5772 | +0.7052 | 0.910 |
| `combo_rank_max__opening_momentum_score__max_down_ret` | Cluster 60 | +1 | +0.1203 | +0.2028 | +0.2041 | 0.0000 | +0.5737 | +0.7165 | 0.891 |
| `combo_min__max_up_ret__impulse_bar_dominance` | Cluster 68 | +1 | +0.1035 | +0.2027 | +0.2039 | 0.0000 | +0.6431 | +0.7293 | 0.872 |
| `early_order_flow_imbalance` | Cluster 41 | +1 | +0.0858 | +0.2021 | +0.2032 | 0.0000 | +0.4667 | +0.6846 | 0.844 |
| `combo_min__first_bar_return__max_down_ret` | Cluster 23 | +1 | +0.1327 | +0.2016 | +0.2038 | 0.0000 | +0.5563 | +0.6975 | 0.941 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | Cluster 58 | +1 | +0.1432 | +0.2007 | +0.2015 | 0.0000 | +0.5244 | +0.6821 | 0.876 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Cluster 67 | +1 | +0.1369 | +0.2006 | +0.2008 | 0.0000 | +0.3657 | +0.6697 | 0.637 |
| `combo_rank_max__close_vs_open_range__opening_momentum_score` | Cluster 72 | +1 | +0.1067 | +0.2002 | +0.2012 | 0.0000 | +0.5342 | +0.7278 | 0.945 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 50 | +1 | +0.1297 | +0.1987 | +0.2003 | 0.0000 | +0.6855 | +0.7401 | 0.934 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 58 | +1 | +0.1589 | +0.1973 | +0.1988 | 0.0000 | +0.5426 | +0.6852 | 0.937 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 22 | +1 | +0.1788 | +0.1971 | +0.1984 | 0.0000 | +0.5185 | +0.7334 | 0.932 |
| `combo_min__trend_bar_close_consistency__max_down_ret` | Cluster 62 | +1 | +0.0976 | +0.1967 | +0.1983 | 0.0000 | +0.5251 | +0.6826 | 0.942 |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 0 | +1 | +0.1649 | +0.1956 | +0.1963 | 0.0000 | +0.4333 | +0.6826 | 0.946 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 32 | +1 | +0.1530 | +0.1937 | +0.1948 | 0.0000 | +0.4332 | +0.6703 | 0.853 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 43 | +1 | +0.1672 | +0.1937 | +0.1948 | 0.0000 | +0.7073 | +0.7622 | 0.931 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | Cluster 4 | +1 | +0.0947 | +0.1933 | +0.1943 | 0.0000 | +0.5294 | +0.6662 | 0.706 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 58 | +1 | +0.1280 | +0.1931 | +0.1932 | 0.0000 | +0.5135 | +0.6821 | 0.947 |
| `first_bar_return` | Cluster 44 | +1 | +0.1457 | +0.1931 | +0.1945 | 0.0000 | +0.6014 | +0.7180 | 0.940 |
| `combo_mean__first_bar_sentiment__first_bar_return` | Cluster 44 | +1 | +0.1457 | +0.1931 | +0.1945 | 0.0000 | +0.6014 | +0.7180 | 0.935 |
| `combo_mean__bar_ret_0__impulse_bar_dominance` | Cluster 69 | +1 | +0.1166 | +0.1929 | +0.1947 | 0.0000 | +0.5217 | +0.6893 | 0.854 |
| `combo_max__net_volume_flow__first_bar_return` | Cluster 13 | +1 | +0.1489 | +0.1927 | +0.1942 | 0.0000 | +0.5515 | +0.7114 | 0.935 |
| `combo_max__star50_limit_proximity_early__first_bar_return` | Cluster 59 | +1 | +0.1562 | +0.1916 | +0.1924 | 0.0000 | +0.6772 | +0.7144 | 0.822 |
| `combo_mean__close_vs_open_range__max_down_ret` | Cluster 61 | +1 | +0.1278 | +0.1908 | +0.1925 | 0.0000 | +0.4766 | +0.6646 | 0.927 |
| `combo_min__close_vs_open_range__impulse_bar_dominance` | Cluster 36 | +1 | +0.0956 | +0.1907 | +0.1924 | 0.0000 | +0.4640 | +0.6857 | 0.932 |
| `combo_sig_product__max_up_ret__body_size_progression` | Cluster 39 | +1 | +0.1454 | +0.1907 | +0.1915 | 0.0000 | +0.7799 | +0.7447 | 0.837 |
| `combo_max__net_volume_flow__max_down_ret` | Cluster 60 | +1 | +0.1223 | +0.1903 | +0.1919 | 0.0000 | +0.5420 | +0.7031 | 0.913 |
| `combo_max__star50_limit_proximity_early__impulse_bar_dominance` | Cluster 15 | +1 | +0.1061 | +0.1902 | +0.1915 | 0.0000 | +0.4232 | +0.6739 | 0.814 |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | Cluster 58 | +1 | +0.1398 | +0.1898 | +0.1908 | 0.0000 | +0.4713 | +0.6954 | 0.939 |
| `combo_rank_min__impulse_bar_dominance__max_down_ret` | Cluster 70 | +1 | +0.1014 | +0.1869 | +0.1889 | 0.0000 | +0.5649 | +0.7149 | 0.835 |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 58 | +1 | +0.1469 | +0.1867 | +0.1876 | 0.0000 | +0.4895 | +0.6615 | 0.948 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | Cluster 14 | +1 | +0.1484 | +0.1857 | +0.1873 | 0.0000 | +0.6888 | +0.7540 | 0.920 |
| `combo_rank_max__close_vs_open_range__max_down_ret` | Cluster 64 | +1 | +0.1247 | +0.1851 | +0.1867 | 0.0000 | +0.5096 | +0.6995 | 0.947 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Cluster 43 | +1 | +0.1447 | +0.1846 | +0.1865 | 0.0000 | +0.7050 | +0.7550 | 0.902 |
| `combo_min__first_bar_sentiment__max_down_ret` | Cluster 43 | +1 | +0.1437 | +0.1841 | +0.1863 | 0.0000 | +0.5824 | +0.6934 | 0.904 |
| `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` | Cluster 15 | +1 | +0.1167 | +0.1819 | +0.1831 | 0.0000 | +0.4451 | +0.6934 | 0.861 |
| `combo_rank_min__close_vs_open_range__impulse_bar_dominance` | Cluster 36 | +1 | +0.0944 | +0.1818 | +0.1833 | 0.0000 | +0.5071 | +0.6959 | 0.926 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | Cluster 42 | +1 | +0.1262 | +0.1816 | +0.1828 | 0.0000 | +0.4172 | +0.6662 | 0.822 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | Cluster 58 | +1 | +0.1532 | +0.1800 | +0.1809 | 0.0000 | +0.4993 | +0.6949 | 0.942 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Cluster 58 | +1 | +0.1407 | +0.1798 | +0.1805 | 0.0000 | +0.5327 | +0.7155 | 0.945 |
| `combo_max__close_vs_open_range__max_down_ret` | Cluster 64 | +1 | +0.1253 | +0.1777 | +0.1790 | 0.0000 | +0.4249 | +0.6857 | 0.897 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 14 | +1 | +0.1361 | +0.1753 | +0.1762 | 0.0000 | +0.6395 | +0.7422 | 0.872 |
| `max_down_ret` | Cluster 63 | +1 | +0.1248 | +0.1750 | +0.1774 | 0.0000 | +0.5100 | +0.6590 | 0.927 |
| `combo_max__bar_ret_0__impulse_bar_dominance` | Cluster 71 | +1 | +0.1197 | +0.1732 | +0.1746 | 0.0000 | +0.4977 | +0.6703 | 0.917 |
| `combo_sig_product__max_up_ret__impulse_bar_dominance` | Cluster 39 | +1 | +0.1487 | +0.1711 | +0.1723 | 0.0000 | +0.5180 | +0.6944 | 0.847 |
| `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 4 | +1 | +0.1298 | +0.1704 | +0.1708 | 0.0000 | +0.7237 | +0.7442 | 0.637 |
| `combo_rel_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 4 | +1 | +0.1238 | +0.1702 | +0.1704 | 0.0000 | +0.7131 | +0.7468 | 0.950 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 39 | +1 | +0.1603 | +0.1690 | +0.1706 | 0.0002 | +0.5264 | +0.7201 | 0.787 |
| `combo_mean__impulse_bar_dominance__max_down_ret` | Cluster 63 | +1 | +0.1078 | +0.1651 | +0.1671 | 0.0006 | +0.5186 | +0.6733 | 0.864 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Cluster 17 | +1 | +0.1208 | +0.1645 | +0.1654 | 0.0006 | +0.4439 | +0.6754 | 0.916 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 14 | +1 | +0.1556 | +0.1636 | +0.1651 | 0.0006 | +0.6321 | +0.7381 | 0.946 |
| `morning_volume_weighted_momentum` | Cluster 72 | +1 | +0.1104 | +0.1578 | +0.1586 | 0.0014 | +0.4396 | +0.6579 | 0.909 |
| `combo_rel_diff__bar_ret_0__impulse_bar_dominance` | Cluster 4 | +1 | +0.0541 | +0.1569 | +0.1563 | 0.0016 | +0.4743 | +0.7031 | 0.742 |
| `open_to_current_return` | Cluster 72 | +1 | +0.1142 | +0.1557 | +0.1567 | 0.0018 | +0.4824 | +0.6954 | 0.846 |
| `vwap_trend_channel_slope` | Cluster 40 | +1 | +0.0991 | +0.1543 | +0.1549 | 0.0020 | +0.4231 | +0.6564 | 0.742 |
| `combo_ratio__first_bar_return__net_volume_flow` | Cluster 44 | +1 | +0.1120 | +0.1421 | +0.1439 | 0.0064 | +0.3299 | +0.6523 | 0.101 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 67 | +1 | +0.1424 | +0.1417 | +0.1413 | 0.0064 | +0.3671 | +0.6662 | 0.622 |
| `or_fill_ratio` | Cluster 35 | +1 | +0.0805 | +0.1332 | +0.1342 | 0.0100 | +0.4954 | +0.7180 | 0.935 |
| `bar_body_rng_0` | Cluster 44 | +1 | +0.1360 | +0.1298 | +0.1322 | 0.0118 | +0.5355 | +0.6754 | 0.913 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 4 | +1 | +0.1376 | +0.3068 | +0.3083 | 0.0000 | +0.6713 | +0.7483 | 0.703 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 6 | +1 | +0.1461 | +0.3059 | +0.3073 | 0.0000 | +0.6470 | +0.7437 | 0.929 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 6 | +1 | +0.1585 | +0.2840 | +0.2852 | 0.0000 | +0.7025 | +0.7632 | 0.930 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 22 | +1 | +0.1201 | +0.2807 | +0.2815 | 0.0000 | +0.7668 | +0.7596 | 0.830 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Cluster 6 | +1 | +0.1404 | +0.2802 | +0.2815 | 0.0000 | +0.6570 | +0.7478 | 0.944 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 6 | +1 | +0.1504 | +0.2800 | +0.2810 | 0.0000 | +0.6266 | +0.7134 | 0.923 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 6 | +1 | +0.1441 | +0.2777 | +0.2788 | 0.0000 | +0.6415 | +0.7288 | 0.947 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 4 | +1 | +0.1458 | +0.2773 | +0.2784 | 0.0000 | +0.7403 | +0.7833 | 0.934 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 1 | +1 | +0.1072 | +0.2737 | +0.2745 | 0.0000 | +0.6264 | +0.7252 | 0.917 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 3 | +1 | +0.1647 | +0.2710 | +0.2713 | 0.0000 | +0.6711 | +0.7370 | 0.914 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 1 | +1 | +0.1078 | +0.2703 | +0.2712 | 0.0000 | +0.6304 | +0.7345 | 0.826 |
| `combo_min__max_up_ret__impulse_bar_dominance` | Cluster 15 | +1 | +0.0909 | +0.2696 | +0.2710 | 0.0000 | +0.3947 | +0.6513 | 0.784 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 6 | +1 | +0.1670 | +0.2677 | +0.2687 | 0.0000 | +0.5756 | +0.6718 | 0.934 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 4 | +1 | +0.1519 | +0.2672 | +0.2686 | 0.0000 | +0.7041 | +0.7612 | 0.869 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Cluster 1 | +1 | +0.1299 | +0.2655 | +0.2665 | 0.0000 | +0.7819 | +0.7992 | 0.316 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 18 | +1 | +0.1569 | +0.2646 | +0.2660 | 0.0000 | +0.7050 | +0.7519 | 0.878 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 0 | +1 | +0.1415 | +0.2638 | +0.2654 | 0.0000 | +0.4818 | +0.6692 | 0.935 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 20 | +1 | +0.1676 | +0.2636 | +0.2646 | 0.0000 | +0.6272 | +0.7206 | 0.923 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 6 | +1 | +0.1647 | +0.2634 | +0.2639 | 0.0000 | +0.6946 | +0.7509 | 0.920 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 6 | +1 | +0.1617 | +0.2607 | +0.2614 | 0.0000 | +0.6710 | +0.7786 | 0.913 |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 20 | +1 | +0.1620 | +0.2602 | +0.2612 | 0.0000 | +0.5313 | +0.7057 | 0.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 0 | +1 | +0.1515 | +0.2598 | +0.2610 | 0.0000 | +0.6885 | +0.7345 | 0.939 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 11 | +1 | +0.1188 | +0.2597 | +0.2609 | 0.0000 | +0.8228 | +0.8038 | 0.869 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Cluster 19 | +1 | +0.1383 | +0.2594 | +0.2608 | 0.0000 | +0.4770 | +0.6872 | 0.872 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 6 | +1 | +0.1687 | +0.2583 | +0.2595 | 0.0000 | +0.5300 | +0.6867 | 0.937 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 6 | +1 | +0.1388 | +0.2580 | +0.2589 | 0.0000 | +0.6265 | +0.7268 | 0.946 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return` | Cluster 6 | +1 | +0.1437 | +0.2575 | +0.2579 | 0.0000 | +0.5477 | +0.7072 | 0.888 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 20 | +1 | +0.1572 | +0.2557 | +0.2570 | 0.0000 | +0.6130 | +0.7365 | 0.907 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 6 | +1 | +0.1648 | +0.2557 | +0.2563 | 0.0000 | +0.7233 | +0.7560 | 0.943 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Cluster 3 | +1 | +0.1415 | +0.2548 | +0.2555 | 0.0000 | +0.6451 | +0.7607 | 0.883 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 24 | +1 | +0.1153 | +0.2517 | +0.2530 | 0.0000 | +0.6115 | +0.7052 | 0.880 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 2 | +1 | +0.1532 | +0.2510 | +0.2517 | 0.0000 | +0.5328 | +0.7191 | 0.915 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 20 | +1 | +0.1670 | +0.2492 | +0.2504 | 0.0000 | +0.5781 | +0.7119 | 0.928 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | Cluster 6 | +1 | +0.1236 | +0.2454 | +0.2463 | 0.0000 | +0.6026 | +0.6898 | 0.950 |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 8 | +1 | +0.1346 | +0.2447 | +0.2468 | 0.0000 | +0.5327 | +0.7026 | 0.928 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Cluster 20 | +1 | +0.1535 | +0.2439 | +0.2454 | 0.0000 | +0.6050 | +0.7062 | 0.934 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 7 | +1 | +0.1402 | +0.2438 | +0.2456 | 0.0000 | +0.4463 | +0.6600 | 0.856 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Cluster 6 | +1 | +0.1562 | +0.2431 | +0.2440 | 0.0000 | +0.5808 | +0.7006 | 0.924 |
| `opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.1143 | +0.2418 | +0.2438 | 0.0000 | +0.5411 | +0.7016 | 0.907 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 18 | +1 | +0.1487 | +0.2369 | +0.2383 | 0.0000 | +0.4898 | +0.6918 | 0.925 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 24 | +1 | +0.1155 | +0.2361 | +0.2375 | 0.0000 | +0.5942 | +0.7062 | 0.949 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Cluster 9 | +1 | +0.1495 | +0.2360 | +0.2379 | 0.0000 | +0.4509 | +0.6846 | 0.898 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 5 | +1 | +0.1315 | +0.2355 | +0.2365 | 0.0000 | +0.6505 | +0.7262 | 0.875 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 9 | +1 | +0.1406 | +0.2286 | +0.2301 | 0.0000 | +0.4719 | +0.6795 | 0.898 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 10 | +1 | +0.1418 | +0.2283 | +0.2295 | 0.0000 | +0.5990 | +0.7555 | 0.933 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Cluster 18 | +1 | +0.1563 | +0.2277 | +0.2291 | 0.0000 | +0.4677 | +0.6574 | 0.935 |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | Cluster 9 | +1 | +0.1489 | +0.2273 | +0.2292 | 0.0000 | +0.4921 | +0.6795 | 0.949 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 9 | +1 | +0.1416 | +0.2273 | +0.2288 | 0.0000 | +0.5309 | +0.7103 | 0.948 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Cluster 8 | +1 | +0.1413 | +0.2271 | +0.2289 | 0.0000 | +0.5107 | +0.6913 | 0.948 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 21 | +1 | +0.1530 | +0.2269 | +0.2290 | 0.0000 | +0.5759 | +0.6882 | 0.866 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Cluster 7 | +1 | +0.1402 | +0.2241 | +0.2258 | 0.0000 | +0.4478 | +0.6888 | 0.940 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Cluster 2 | +1 | +0.1296 | +0.2180 | +0.2196 | 0.0000 | +0.4506 | +0.6795 | 0.899 |
| `combo_max__max_up_ret__bar_body_rng_0` | Cluster 9 | +1 | +0.1381 | +0.2168 | +0.2188 | 0.0000 | +0.4918 | +0.6867 | 0.947 |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 17 | +1 | +0.1348 | +0.2142 | +0.2150 | 0.0000 | +0.5075 | +0.6857 | 0.813 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 11 | +1 | +0.1127 | +0.2140 | +0.2149 | 0.0000 | +0.6132 | +0.7006 | 0.773 |
| `max_up_ret` | Cluster 10 | +1 | +0.1282 | +0.2136 | +0.2148 | 0.0000 | +0.5942 | +0.7165 | 0.942 |
| `combo_z_sum__opening_drive_thrust_ratio__impulse_bar_dominance` | Cluster 12 | +1 | +0.1053 | +0.2131 | +0.2151 | 0.0000 | +0.5028 | +0.7144 | 0.905 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 23 | +1 | +0.1243 | +0.2094 | +0.2090 | 0.0000 | +0.4687 | +0.6739 | 0.763 |
| `combo_mean__first_bar_sentiment__limit_down_proximity_early` | Cluster 6 | +1 | +0.1364 | +0.2075 | +0.2092 | 0.0000 | +0.5321 | +0.6795 | 0.914 |
| `combo_max__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 11 | +1 | +0.1113 | +0.2067 | +0.2077 | 0.0000 | +0.5718 | +0.7298 | 0.885 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 7 | +1 | +0.1288 | +0.2025 | +0.2048 | 0.0000 | +0.3580 | +0.7083 | 0.934 |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | Cluster 0 | +1 | +0.1374 | +0.2021 | +0.2033 | 0.0000 | +0.4381 | +0.6636 | 0.927 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Cluster 17 | +1 | +0.1187 | +0.2017 | +0.2029 | 0.0000 | +0.5439 | +0.7036 | 0.906 |
| `combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Cluster 0 | +1 | +0.1453 | +0.2012 | +0.2023 | 0.0000 | +0.3972 | +0.6636 | 0.943 |
| `combo_mean__max_up_ret__impulse_bar_dominance` | Cluster 15 | +1 | +0.1130 | +0.1984 | +0.2000 | 0.0002 | +0.5658 | +0.7191 | 0.935 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Cluster 17 | +1 | +0.1370 | +0.1971 | +0.1978 | 0.0002 | +0.4809 | +0.6713 | 0.865 |
| `combo_diff__max_up_ret__late_bar_momentum` | Cluster 16 | +1 | +0.1218 | +0.1949 | +0.1963 | 0.0002 | +0.4571 | +0.6934 | 0.827 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Cluster 16 | +1 | +0.1211 | +0.1884 | +0.1896 | 0.0002 | +0.4226 | +0.6872 | 0.870 |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | Cluster 9 | +1 | +0.1314 | +0.1882 | +0.1900 | 0.0002 | +0.3714 | +0.6533 | 0.908 |
| `combo_rank_max__yesterday_first_30min_return__limit_down_proximity_early` | Cluster 11 | +1 | +0.0991 | +0.1872 | +0.1885 | 0.0002 | +0.6005 | +0.7062 | 1.000 |
| `combo_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Cluster 22 | +1 | +0.1193 | +0.1871 | +0.1889 | 0.0002 | +0.3994 | +0.6667 | 0.774 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Cluster 14 | +1 | +0.1261 | +0.1849 | +0.1866 | 0.0002 | +0.3769 | +0.6564 | 0.870 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 7 | +1 | +0.1350 | +0.1837 | +0.1855 | 0.0002 | +0.4576 | +0.6605 | 0.911 |
| `combo_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | Cluster 21 | +1 | +0.1311 | +0.1706 | +0.1725 | 0.0006 | +0.4649 | +0.6610 | 0.857 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 13 | +1 | +0.1182 | +0.1684 | +0.1702 | 0.0008 | +0.5036 | +0.7242 | 0.905 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 13 | +1 | +0.0958 | +0.1628 | +0.1639 | 0.0012 | +0.4227 | +0.6918 | 0.832 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 17 | +1 | +0.1095 | +0.1551 | +0.1554 | 0.0018 | +0.4801 | +0.6959 | 0.135 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Cluster 25 | +1 | +0.0591 | +0.1499 | +0.1520 | 0.0022 | +0.4729 | +0.7052 | 0.434 |

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
| 300ETF | single | 51 | 26 | 0.3549 | `[5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (26 clusters)]` |
| 500ETF | single | 215 | 73 | 0.2682 | `[14, 13, 13, 10, 7, 7, 6, 6, 5, 5, 5, 5, ... (73 clusters)]` |
| 159915ETF | single | 78 | 26 | 0.2496 | `[15, 6, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2, ... (26 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 1 | 0.3549 | `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 1 | 2 | 0.3549 | `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 2 | 5 | 0.3549 | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 300ETF | single | Cluster 3 | 3 | 0.3549 | `combo_ratio__limit_down_proximity_early__volume_concentration` | `combo_rel_diff__limit_down_proximity_early__volume_concentration`, `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` |
| 300ETF | single | Cluster 4 | 2 | 0.3549 | `combo_min__max_up_ret__opening_drive_thrust_ratio` | `combo_mean__max_up_ret__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 5 | 1 | 0.3549 | `max_up_ret` | _(none)_ |
| 300ETF | single | Cluster 6 | 1 | 0.3549 | `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 7 | 2 | 0.3549 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 8 | 1 | 0.3549 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 9 | 3 | 0.3549 | `combo_diff__max_up_ret__early_vwap_acceleration` | `combo_clamp_diff__max_up_ret__early_vwap_acceleration`, `combo_rel_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 10 | 2 | 0.3549 | `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_mean__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 11 | 1 | 0.3549 | `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 12 | 1 | 0.3549 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | _(none)_ |
| 300ETF | single | Cluster 13 | 2 | 0.3549 | `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `combo_rank_max__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 14 | 1 | 0.3549 | `combo_tri_mean__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 15 | 2 | 0.3549 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__star50_limit_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 16 | 1 | 0.3549 | `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | _(none)_ |
| 300ETF | single | Cluster 17 | 3 | 0.3549 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 18 | 1 | 0.3549 | `combo_min__max_up_ret__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 19 | 2 | 0.3549 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 300ETF | single | Cluster 20 | 3 | 0.3549 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `combo_min__max_up_ret__bar_body_rng_0`, `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 21 | 2 | 0.3549 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 22 | 2 | 0.3549 | `rbreaker_sell_setup_proximity_early` | `star50_limit_proximity_early` |
| 300ETF | single | Cluster 23 | 4 | 0.3549 | `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_max__first_bar_return__bar_body_rng_0`, `combo_ratio__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 24 | 1 | 0.3549 | `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 25 | 2 | 0.3549 | `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` |
| 500ETF | single | Cluster 0 | 5 | 0.2682 | `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`, `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` |
| 500ETF | single | Cluster 1 | 1 | 0.2682 | `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 2 | 2 | 0.2682 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 3 | 13 | 0.2682 | `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`, `combo_mean__opening_drive_thrust_ratio__close_vs_open_range`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector`, `combo_min__opening_drive_thrust_ratio__high_low_sequence_momentum`, `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_max__opening_drive_thrust_ratio__opening_momentum_score`, `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`, `combo_min__opening_drive_thrust_ratio__close_vs_open_range`, `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_max__opening_drive_thrust_ratio__close_vs_open_range`, `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` |
| 500ETF | single | Cluster 4 | 6 | 0.2682 | `combo_clamp_diff__max_up_ret__impulse_bar_dominance` | `combo_diff__max_up_ret__impulse_bar_dominance`, `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance`, `combo_rel_diff__opening_drive_thrust_ratio__impulse_bar_dominance`, `combo_abs_diff__max_up_ret__close_vs_open_range`, `combo_rel_diff__bar_ret_0__impulse_bar_dominance` |
| 500ETF | single | Cluster 5 | 2 | 0.2682 | `combo_min__net_volume_flow__bar_ret_0` | `combo_rank_min__trend_bar_close_consistency__first_bar_return` |
| 500ETF | single | Cluster 6 | 2 | 0.2682 | `combo_mean__first_bar_sentiment__opening_momentum_score` | `combo_mean__close_vs_open_range__first_bar_sentiment` |
| 500ETF | single | Cluster 7 | 1 | 0.2682 | `combo_min__close_vs_open_range__first_bar_sentiment` | _(none)_ |
| 500ETF | single | Cluster 8 | 2 | 0.2682 | `combo_max__close_vs_open_range__first_bar_return` | `combo_rank_max__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 9 | 2 | 0.2682 | `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | `combo_max__close_vs_open_range__first_bar_sentiment` |
| 500ETF | single | Cluster 10 | 1 | 0.2682 | `combo_max__first_bar_sentiment__opening_momentum_score` | _(none)_ |
| 500ETF | single | Cluster 11 | 2 | 0.2682 | `combo_mean__net_volume_flow__first_bar_return` | `combo_mean__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 12 | 2 | 0.2682 | `combo_rank_min__close_vs_open_range__first_bar_return` | `combo_min__close_vs_open_range__first_bar_return` |
| 500ETF | single | Cluster 13 | 2 | 0.2682 | `combo_rank_max__opening_momentum_score__first_bar_return` | `combo_max__net_volume_flow__first_bar_return` |
| 500ETF | single | Cluster 14 | 6 | 0.2682 | `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence`, `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 15 | 2 | 0.2682 | `combo_max__star50_limit_proximity_early__impulse_bar_dominance` | `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` |
| 500ETF | single | Cluster 16 | 3 | 0.2682 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression`, `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` |
| 500ETF | single | Cluster 17 | 3 | 0.2682 | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression`, `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` |
| 500ETF | single | Cluster 18 | 5 | 0.2682 | `combo_rank_max__max_up_ret__first_bar_return` | `combo_max__max_up_ret__bar_ret_0`, `combo_mean__max_up_ret__bar_ret_0`, `combo_min__max_up_ret__bar_ret_0`, `combo_max__max_up_ret__first_bar_sentiment` |
| 500ETF | single | Cluster 19 | 2 | 0.2682 | `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 20 | 2 | 0.2682 | `combo_max__first_bar_return__max_down_ret` | `combo_rank_max__first_bar_return__max_down_ret` |
| 500ETF | single | Cluster 21 | 1 | 0.2682 | `combo_mean__bar_ret_0__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 22 | 2 | 0.2682 | `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `combo_max__opening_drive_thrust_ratio__bar_ret_0` |
| 500ETF | single | Cluster 23 | 2 | 0.2682 | `combo_min__first_bar_return__max_down_ret` | `combo_rank_min__first_bar_return__max_down_ret` |
| 500ETF | single | Cluster 24 | 1 | 0.2682 | `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 25 | 2 | 0.2682 | `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | `combo_min__opening_drive_thrust_ratio__first_bar_return` |
| 500ETF | single | Cluster 26 | 2 | 0.2682 | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` |
| 500ETF | single | Cluster 27 | 2 | 0.2682 | `combo_max__opening_drive_thrust_ratio__max_down_ret` | `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 28 | 2 | 0.2682 | `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 29 | 1 | 0.2682 | `opening_drive_thrust_ratio` | _(none)_ |
| 500ETF | single | Cluster 30 | 3 | 0.2682 | `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` |
| 500ETF | single | Cluster 31 | 2 | 0.2682 | `combo_max__opening_drive_thrust_ratio__max_up_ret` | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 32 | 1 | 0.2682 | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 500ETF | single | Cluster 33 | 2 | 0.2682 | `combo_mean__opening_drive_thrust_ratio__impulse_bar_dominance` | `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` |
| 500ETF | single | Cluster 34 | 1 | 0.2682 | `combo_min__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 500ETF | single | Cluster 35 | 1 | 0.2682 | `or_fill_ratio` | _(none)_ |
| 500ETF | single | Cluster 36 | 5 | 0.2682 | `combo_mean__volatility_expansion_trend_vector__impulse_bar_dominance` | `combo_mean__close_vs_open_range__impulse_bar_dominance`, `combo_min__close_vs_open_range__impulse_bar_dominance`, `combo_min__net_volume_flow__impulse_bar_dominance`, `combo_rank_min__close_vs_open_range__impulse_bar_dominance` |
| 500ETF | single | Cluster 37 | 2 | 0.2682 | `combo_max__close_vs_open_range__impulse_bar_dominance` | `combo_max__opening_momentum_score__impulse_bar_dominance` |
| 500ETF | single | Cluster 38 | 14 | 0.2682 | `combo_min__net_volume_flow__star50_limit_proximity_early` | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`, `combo_rank_min__net_volume_flow__star50_limit_proximity_early`, `combo_mean__star50_limit_proximity_early__opening_momentum_score`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`, `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_mean__star50_limit_proximity_early__close_vs_open_range`, `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`, `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`, `combo_min__star50_limit_proximity_early__close_vs_open_range`, `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`, `combo_rank_min__star50_limit_proximity_early__trend_bar_close_consistency`, `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` |
| 500ETF | single | Cluster 39 | 7 | 0.2682 | `combo_sig_product__max_up_ret__close_vs_open_range` | `combo_sig_product__max_up_ret__opening_momentum_score`, `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`, `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`, `combo_sig_product__max_up_ret__body_size_progression`, `combo_sig_product__max_up_ret__impulse_bar_dominance`, `combo_sig_product__max_up_ret__bar_ret_0` |
| 500ETF | single | Cluster 40 | 2 | 0.2682 | `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 41 | 1 | 0.2682 | `early_order_flow_imbalance` | _(none)_ |
| 500ETF | single | Cluster 42 | 2 | 0.2682 | `combo_sig_product__first_bar_sentiment__opening_momentum_score` | `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` |
| 500ETF | single | Cluster 43 | 5 | 0.2682 | `combo_min__max_up_ret__first_bar_sentiment` | `combo_rank_min__close_vs_open_range__first_bar_sentiment`, `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_rank_min__first_bar_sentiment__max_down_ret`, `combo_min__first_bar_sentiment__max_down_ret` |
| 500ETF | single | Cluster 44 | 5 | 0.2682 | `combo_rank_min__first_bar_sentiment__first_bar_return` | `first_bar_return`, `combo_mean__first_bar_sentiment__first_bar_return`, `combo_ratio__first_bar_return__net_volume_flow`, `bar_body_rng_0` |
| 500ETF | single | Cluster 45 | 3 | 0.2682 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 500ETF | single | Cluster 46 | 1 | 0.2682 | `combo_mean__star50_limit_proximity_early__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 47 | 2 | 0.2682 | `combo_min__star50_limit_proximity_early__max_down_ret` | `combo_rank_min__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 48 | 1 | 0.2682 | `combo_rank_max__star50_limit_proximity_early__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 49 | 2 | 0.2682 | `combo_mean__max_up_ret__net_volume_flow` | `combo_mean__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 50 | 1 | 0.2682 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | _(none)_ |
| 500ETF | single | Cluster 51 | 2 | 0.2682 | `combo_rank_max__max_up_ret__opening_momentum_score` | `combo_max__max_up_ret__opening_momentum_score` |
| 500ETF | single | Cluster 52 | 3 | 0.2682 | `combo_rank_min__max_up_ret__close_vs_open_range` | `combo_min__max_up_ret__close_vs_open_range`, `combo_min__max_up_ret__high_low_sequence_momentum` |
| 500ETF | single | Cluster 53 | 1 | 0.2682 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 54 | 2 | 0.2682 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `max_up_ret` |
| 500ETF | single | Cluster 55 | 2 | 0.2682 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` |
| 500ETF | single | Cluster 56 | 2 | 0.2682 | `combo_rank_max__max_up_ret__close_vs_open_range` | `combo_max__max_up_ret__close_vs_open_range` |
| 500ETF | single | Cluster 57 | 5 | 0.2682 | `combo_mean__star50_limit_proximity_early__first_bar_return` | `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`, `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_rank_min__star50_limit_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 58 | 10 | 0.2682 | `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`, `combo_rank_max__net_volume_flow__star50_limit_proximity_early`, `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency`, `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_momentum_score`, `combo_max__net_volume_flow__star50_limit_proximity_early`, `combo_max__rbreaker_sell_setup_proximity_early__opening_momentum_score`, `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_rank_max__star50_limit_proximity_early__close_vs_open_range`, `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` |
| 500ETF | single | Cluster 59 | 4 | 0.2682 | `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_max__star50_limit_proximity_early__first_bar_return`, `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 60 | 2 | 0.2682 | `combo_rank_max__opening_momentum_score__max_down_ret` | `combo_max__net_volume_flow__max_down_ret` |
| 500ETF | single | Cluster 61 | 2 | 0.2682 | `combo_mean__net_volume_flow__max_down_ret` | `combo_mean__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 62 | 2 | 0.2682 | `combo_rank_min__trend_bar_close_consistency__max_down_ret` | `combo_min__trend_bar_close_consistency__max_down_ret` |
| 500ETF | single | Cluster 63 | 2 | 0.2682 | `max_down_ret` | `combo_mean__impulse_bar_dominance__max_down_ret` |
| 500ETF | single | Cluster 64 | 2 | 0.2682 | `combo_max__close_vs_open_range__max_down_ret` | `combo_rank_max__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 65 | 2 | 0.2682 | `combo_rank_min__close_vs_open_range__max_down_ret` | `combo_min__close_vs_open_range__max_down_ret` |
| 500ETF | single | Cluster 66 | 7 | 0.2682 | `combo_rel_diff__max_up_ret__body_size_progression` | `combo_rel_diff__max_up_ret__late_bar_momentum`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_diff__max_up_ret__body_size_progression`, `combo_clamp_diff__max_up_ret__smooth_momentum_structure`, `combo_clamp_diff__max_up_ret__body_size_progression` |
| 500ETF | single | Cluster 67 | 2 | 0.2682 | `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 68 | 1 | 0.2682 | `combo_min__max_up_ret__impulse_bar_dominance` | _(none)_ |
| 500ETF | single | Cluster 69 | 2 | 0.2682 | `combo_mean__bar_ret_0__impulse_bar_dominance` | `combo_min__bar_ret_0__impulse_bar_dominance` |
| 500ETF | single | Cluster 70 | 1 | 0.2682 | `combo_rank_min__impulse_bar_dominance__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 71 | 2 | 0.2682 | `combo_max__max_up_ret__impulse_bar_dominance` | `combo_max__bar_ret_0__impulse_bar_dominance` |
| 500ETF | single | Cluster 72 | 13 | 0.2682 | `combo_mean__net_volume_flow__close_vs_open_range` | `combo_rank_min__net_volume_flow__close_vs_open_range`, `combo_sig_product__net_volume_flow__close_vs_open_range`, `combo_max__close_vs_open_range__opening_momentum_score`, `combo_min__trend_day_regime_conviction__close_vs_open_range`, `combo_rank_max__close_vs_open_range__opening_momentum_score`, `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction`, `net_volume_flow`, `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`, `combo_sig_product__close_vs_open_range__opening_momentum_score`, `open_to_current_return`, `morning_volume_weighted_momentum`, `trend_bar_close_consistency` |
| 159915ETF | single | Cluster 0 | 4 | 0.2496 | `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`, `combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0`, `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` |
| 159915ETF | single | Cluster 1 | 3 | 0.2496 | `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `combo_min__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` |
| 159915ETF | single | Cluster 2 | 2 | 0.2496 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 3 | 2 | 0.2496 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 4 | 3 | 0.2496 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 159915ETF | single | Cluster 5 | 1 | 0.2496 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 6 | 15 | 0.2496 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_mean__star50_limit_proximity_early__bar_ret_0`, `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`, `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`, `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return`, `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`, `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`, `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_mean__first_bar_sentiment__limit_down_proximity_early`, `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`, `combo_min__bar_ret_0__limit_down_proximity_early` |
| 159915ETF | single | Cluster 7 | 4 | 0.2496 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__first_bar_return`, `combo_rank_max__opening_drive_thrust_ratio__first_bar_return`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 8 | 2 | 0.2496 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` |
| 159915ETF | single | Cluster 9 | 6 | 0.2496 | `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `combo_rank_max__max_up_ret__first_bar_return`, `combo_max__max_up_ret__bar_ret_0`, `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return`, `combo_max__max_up_ret__bar_body_rng_0`, `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 10 | 2 | 0.2496 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `max_up_ret` |
| 159915ETF | single | Cluster 11 | 4 | 0.2496 | `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_max__star50_limit_proximity_early__yesterday_first_30min_return`, `combo_rank_max__yesterday_first_30min_return__limit_down_proximity_early` |
| 159915ETF | single | Cluster 12 | 2 | 0.2496 | `opening_drive_thrust_ratio` | `combo_z_sum__opening_drive_thrust_ratio__impulse_bar_dominance` |
| 159915ETF | single | Cluster 13 | 2 | 0.2496 | `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 14 | 1 | 0.2496 | `combo_max__max_up_ret__volume_weighted_price_position` | _(none)_ |
| 159915ETF | single | Cluster 15 | 2 | 0.2496 | `combo_min__max_up_ret__impulse_bar_dominance` | `combo_mean__max_up_ret__impulse_bar_dominance` |
| 159915ETF | single | Cluster 16 | 2 | 0.2496 | `combo_diff__max_up_ret__late_bar_momentum` | `combo_rel_diff__max_up_ret__late_bar_momentum` |
| 159915ETF | single | Cluster 17 | 4 | 0.2496 | `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`, `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 18 | 3 | 0.2496 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`, `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 19 | 1 | 0.2496 | `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | _(none)_ |
| 159915ETF | single | Cluster 20 | 5 | 0.2496 | `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`, `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` |
| 159915ETF | single | Cluster 21 | 2 | 0.2496 | `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `combo_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 22 | 2 | 0.2496 | `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `combo_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` |
| 159915ETF | single | Cluster 23 | 1 | 0.2496 | `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | _(none)_ |
| 159915ETF | single | Cluster 24 | 2 | 0.2496 | `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 25 | 1 | 0.2496 | `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | _(none)_ |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
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
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__max_up_ret__volume_weighted_price_position` | `min` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_mean` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | `min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__first_bar_return__bar_body_rng_0` | `max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_volume` |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | `rel_diff` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__volume_weighted_price_position__opening_drive_thrust_ratio` | `mean` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` | `clamp_diff` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_concentration` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | `rank_max` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | `rank_max` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`trend_bar_close_consistency` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | `max` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | `min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | `clamp_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`trend_bar_close_consistency` |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | `rank_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | `mean` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | `mean` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | `min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rank_min__star50_limit_proximity_early__trend_bar_close_consistency` | `rank_min` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_min__opening_drive_thrust_ratio__high_low_sequence_momentum` | `min` | a=`opening_drive_thrust_ratio`, b=`high_low_sequence_momentum` |
| `combo_max__opening_drive_thrust_ratio__opening_momentum_score` | `max` | a=`opening_drive_thrust_ratio`, b=`opening_momentum_score` |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_mean__max_up_ret__net_volume_flow` | `mean` | a=`max_up_ret`, b=`net_volume_flow` |
| `combo_rank_min__close_vs_open_range__first_bar_sentiment` | `rank_min` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | `mean` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_mean__star50_limit_proximity_early__opening_momentum_score` | `mean` | a=`star50_limit_proximity_early`, b=`opening_momentum_score` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_min__net_volume_flow__impulse_bar_dominance` | `min` | a=`net_volume_flow`, b=`impulse_bar_dominance` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__opening_drive_thrust_ratio__impulse_bar_dominance` | `mean` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_rank_min__max_up_ret__close_vs_open_range` | `rank_min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`body_size_progression` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_sig_product__max_up_ret__opening_momentum_score` | `sig_product` | a=`max_up_ret`, b=`opening_momentum_score` |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | `max` | a=`volatility_expansion_trend_vector`, b=`first_bar_sentiment` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_median` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_max__max_up_ret__opening_momentum_score` | `max` | a=`max_up_ret`, b=`opening_momentum_score` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | `min` | a=`trend_day_regime_conviction`, b=`close_vs_open_range` |
| `combo_diff__max_up_ret__impulse_bar_dominance` | `diff` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | `rank_min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__opening_momentum_score` | `rank_max` | a=`max_up_ret`, b=`opening_momentum_score` |
| `combo_min__net_volume_flow__bar_ret_0` | `min` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_clamp_diff__max_up_ret__impulse_bar_dominance` | `clamp_diff` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_rank_min__trend_bar_close_consistency__first_bar_return` | `rank_min` | a=`trend_bar_close_consistency`, b=`first_bar_return` |
| `combo_mean__net_volume_flow__close_vs_open_range` | `mean` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | `min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__first_bar_sentiment__opening_momentum_score` | `mean` | a=`first_bar_sentiment`, b=`opening_momentum_score` |
| `combo_min__max_up_ret__close_vs_open_range` | `min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__max_up_ret__close_vs_open_range` | `mean` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | `rank_min` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__max_up_ret__high_low_sequence_momentum` | `min` | a=`max_up_ret`, b=`high_low_sequence_momentum` |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_max__max_up_ret__close_vs_open_range` | `max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | `mean` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_mean__net_volume_flow__first_bar_return` | `mean` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_max__first_bar_sentiment__opening_momentum_score` | `max` | a=`first_bar_sentiment`, b=`opening_momentum_score` |
| `combo_rank_max__first_bar_return__max_down_ret` | `rank_max` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_mean__max_up_ret__bar_ret_0` | `mean` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`trend_day_regime_conviction` |
| `combo_rank_max__max_up_ret__close_vs_open_range` | `rank_max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_max__max_up_ret__impulse_bar_dominance` | `max` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_min__close_vs_open_range__first_bar_return` | `min` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_momentum_score` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_momentum_score` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`volume_weighted_momentum_acceleration` |
| `combo_max__close_vs_open_range__first_bar_sentiment` | `max` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__close_vs_open_range__first_bar_return` | `rank_min` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__bar_ret_0__impulse_bar_dominance` | `min` | a=`bar_ret_0`, b=`impulse_bar_dominance` |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | `sig_product` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_max__close_vs_open_range__impulse_bar_dominance` | `max` | a=`close_vs_open_range`, b=`impulse_bar_dominance` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__opening_momentum_score__first_bar_return` | `rank_max` | a=`opening_momentum_score`, b=`first_bar_return` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_mean__volatility_expansion_trend_vector__impulse_bar_dominance` | `mean` | a=`volatility_expansion_trend_vector`, b=`impulse_bar_dominance` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_rank_max__close_vs_open_range__first_bar_return` | `rank_max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_max__close_vs_open_range__first_bar_return` | `max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_momentum_score` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_momentum_score` |
| `combo_sig_product__close_vs_open_range__opening_momentum_score` | `sig_product` | a=`close_vs_open_range`, b=`opening_momentum_score` |
| `combo_mean__close_vs_open_range__first_bar_return` | `mean` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_mean__net_volume_flow__max_down_ret` | `mean` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_mean__close_vs_open_range__impulse_bar_dominance` | `mean` | a=`close_vs_open_range`, b=`impulse_bar_dominance` |
| `combo_rank_min__trend_bar_close_consistency__max_down_ret` | `rank_min` | a=`trend_bar_close_consistency`, b=`max_down_ret` |
| `combo_sig_product__first_bar_sentiment__opening_momentum_score` | `sig_product` | a=`first_bar_sentiment`, b=`opening_momentum_score` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_rank_min__close_vs_open_range__max_down_ret` | `rank_min` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_max__first_bar_return__max_down_ret` | `max` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_min__first_bar_return__max_down_ret` | `rank_min` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__close_vs_open_range__first_bar_sentiment` | `min` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_max__opening_momentum_score__impulse_bar_dominance` | `max` | a=`opening_momentum_score`, b=`impulse_bar_dominance` |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__close_vs_open_range__opening_momentum_score` | `max` | a=`close_vs_open_range`, b=`opening_momentum_score` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__close_vs_open_range__max_down_ret` | `min` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_rank_max__opening_momentum_score__max_down_ret` | `rank_max` | a=`opening_momentum_score`, b=`max_down_ret` |
| `combo_min__max_up_ret__impulse_bar_dominance` | `min` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_min__first_bar_return__max_down_ret` | `min` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | `rank_max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rank_max__close_vs_open_range__opening_momentum_score` | `rank_max` | a=`close_vs_open_range`, b=`opening_momentum_score` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_min__trend_bar_close_consistency__max_down_ret` | `min` | a=`trend_bar_close_consistency`, b=`max_down_ret` |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | `abs_diff` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | `rank_max` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_mean__first_bar_sentiment__first_bar_return` | `mean` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_mean__bar_ret_0__impulse_bar_dominance` | `mean` | a=`bar_ret_0`, b=`impulse_bar_dominance` |
| `combo_max__net_volume_flow__first_bar_return` | `max` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_max__star50_limit_proximity_early__first_bar_return` | `max` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_mean__close_vs_open_range__max_down_ret` | `mean` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_min__close_vs_open_range__impulse_bar_dominance` | `min` | a=`close_vs_open_range`, b=`impulse_bar_dominance` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__net_volume_flow__max_down_ret` | `max` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_max__star50_limit_proximity_early__impulse_bar_dominance` | `max` | a=`star50_limit_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | `max` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_rank_min__impulse_bar_dominance__max_down_ret` | `rank_min` | a=`impulse_bar_dominance`, b=`max_down_ret` |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | `max` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`early_late_momentum_divergence` |
| `combo_rank_max__close_vs_open_range__max_down_ret` | `rank_max` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_min__first_bar_sentiment__max_down_ret` | `min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` | `mean` | a=`star50_limit_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rank_min__close_vs_open_range__impulse_bar_dominance` | `rank_min` | a=`close_vs_open_range`, b=`impulse_bar_dominance` |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | `rank_max` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_day_regime_conviction` |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | `rank_max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_max__close_vs_open_range__max_down_ret` | `max` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__bar_ret_0__impulse_bar_dominance` | `max` | a=`bar_ret_0`, b=`impulse_bar_dominance` |
| `combo_sig_product__max_up_ret__impulse_bar_dominance` | `sig_product` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | `diff` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_rel_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_mean__impulse_bar_dominance__max_down_ret` | `mean` | a=`impulse_bar_dominance`, b=`max_down_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_rel_diff__bar_ret_0__impulse_bar_dominance` | `rel_diff` | a=`bar_ret_0`, b=`impulse_bar_dominance` |
| `combo_ratio__first_bar_return__net_volume_flow` | `ratio` | a=`first_bar_return`, b=`net_volume_flow` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__max_up_ret__impulse_bar_dominance` | `min` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_mean` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `mean` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_min` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_min__bar_ret_0__limit_down_proximity_early` | `min` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | `tri_max` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | `clamp_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_max__max_up_ret__bar_body_rng_0` | `max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_z_sum__opening_drive_thrust_ratio__impulse_bar_dominance` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__first_bar_sentiment__limit_down_proximity_early` | `mean` | a=`first_bar_sentiment`, b=`limit_down_proximity_early` |
| `combo_max__star50_limit_proximity_early__yesterday_first_30min_return` | `max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | `tri_min` | a=`first_bar_sentiment`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__impulse_bar_dominance` | `mean` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_diff__max_up_ret__late_bar_momentum` | `diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | `rank_max` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__yesterday_first_30min_return__limit_down_proximity_early` | `rank_max` | a=`yesterday_first_30min_return`, b=`limit_down_proximity_early` |
| `combo_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | `max` | a=`first_bar_sentiment`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | `rank_max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
