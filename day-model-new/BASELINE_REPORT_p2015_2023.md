# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2015_2023`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._
_Note: Cost metrics incorporate 8 bps (0.0008) transaction cost per position state transition (realistic for liquid ETFs). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted | Clusters | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 300ETF | single | 1,584 | 522 | 341 | 277 | 272 | 219 | 219 | 219 | 93 | 78 | 25 | `[9, 7, 7, 7, 5, 4, 3, 3, 3, 3, 3, 3, ... (25 clusters)]` |
| 300ETF | long | 579 | 40 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 586 | 93 | 26 | 26 | 5 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 78 | 25 | `[9, 7, 7, 7, 5, 4, 3, 3, 3, 3, 3, 3, ... (25 clusters)]` | +0.1235 | [+0.0809, +0.1656] | +0.2213 | [+0.1001, +0.3191] | +0.8667 | 5.49% | 1.4278 | 3.89% | 1.0240 | 1.8976 | 5.71% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 78 | 25 | `[9, 7, 7, 7, 5, 4, 3, 3, 3, 3, 3, 3, ... (25 clusters)]` | +0.0761 | [+0.0004, +0.1530] | +0.1580* | [-0.0195, +0.3197] | +0.6848 | 3.40% | 0.9906 | 1.84% | 0.5421 | 1.0575 | 3.25% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1225 | +0.2852 | +0.2860 | 0.0000 | +0.7955 | +0.7966 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 1 | +1 | +0.1187 | +0.2800 | +0.2807 | 0.0000 | +0.7370 | +0.7191 | 0.862 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1188 | +0.2764 | +0.2775 | 0.0000 | +0.8678 | +0.8074 | 0.881 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 9 | +1 | +0.1156 | +0.2691 | +0.2697 | 0.0000 | +0.5471 | +0.7072 | 0.912 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1193 | +0.2664 | +0.2674 | 0.0000 | +0.7162 | +0.7524 | 0.945 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 12 | +1 | +0.1119 | +0.2634 | +0.2636 | 0.0000 | +0.6357 | +0.7155 | 0.822 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 1 | +1 | +0.1132 | +0.2593 | +0.2602 | 0.0000 | +0.6700 | +0.7042 | 0.867 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 23 | +1 | +0.1197 | +0.2426 | +0.2433 | 0.0000 | +0.5789 | +0.7129 | 1.000 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 5 | +1 | +0.0941 | +0.2409 | +0.2417 | 0.0000 | +0.5785 | +0.7062 | 0.768 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0967 | +0.2335 | +0.2348 | 0.0000 | +0.5436 | +0.7016 | 0.877 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1165 | +0.2329 | +0.2342 | 0.0000 | +0.7329 | +0.7678 | 0.898 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.0927 | +0.2276 | +0.2285 | 0.0000 | +0.5897 | +0.7088 | 0.888 |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1111 | +0.2261 | +0.2276 | 0.0000 | +0.7574 | +0.7643 | 0.948 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 0 | +1 | +0.0872 | +0.2244 | +0.2251 | 0.0000 | +0.7215 | +0.7571 | 0.956 |
| `rbreaker_sell_setup_proximity_early` | Cluster 17 | +1 | +0.0965 | +0.2243 | +0.2248 | 0.0000 | +0.5652 | +0.7360 | 0.818 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 1 | +1 | +0.1235 | +0.2218 | +0.2227 | 0.0000 | +0.6181 | +0.7427 | 0.941 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 24 | +1 | +0.0995 | +0.2197 | +0.2208 | 0.0000 | +0.5241 | +0.6769 | 0.903 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 8 | +1 | +0.0912 | +0.2181 | +0.2193 | 0.0000 | +0.5315 | +0.6533 | 0.944 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 0 | +1 | +0.0811 | +0.2172 | +0.2175 | 0.0000 | +0.7860 | +0.7750 | 1.000 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 1 | +1 | +0.1074 | +0.2134 | +0.2144 | 0.0000 | +0.6836 | +0.7191 | 0.935 |
| `combo_tri_mean__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 5 | +1 | +0.0980 | +0.2134 | +0.2142 | 0.0000 | +0.5718 | +0.7155 | 0.949 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.0859 | +0.2129 | +0.2140 | 0.0000 | +0.6572 | +0.7483 | 0.873 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 23 | +1 | +0.1222 | +0.2128 | +0.2133 | 0.0000 | +0.5504 | +0.7062 | 0.964 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.0898 | +0.2103 | +0.2113 | 0.0000 | +0.5473 | +0.7083 | 0.943 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 14 | +1 | +0.0935 | +0.2101 | +0.2106 | 0.0000 | +0.6761 | +0.7432 | 0.904 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 14 | +1 | +0.0890 | +0.2083 | +0.2087 | 0.0000 | +0.5712 | +0.6918 | 0.873 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.1131 | +0.2066 | +0.2074 | 0.0000 | +0.6498 | +0.7088 | 0.934 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 8 | +1 | +0.0893 | +0.2054 | +0.2064 | 0.0000 | +0.3937 | +0.6636 | 0.938 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 21 | +1 | +0.0947 | +0.2018 | +0.2028 | 0.0000 | +0.4961 | +0.6831 | 0.973 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 10 | +1 | +0.0963 | +0.2000 | +0.2009 | 0.0002 | +0.5073 | +0.6882 | 0.923 |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Cluster 14 | +1 | +0.0914 | +0.1995 | +0.2002 | 0.0002 | +0.5245 | +0.7103 | 0.943 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.0795 | +0.1991 | +0.2002 | 0.0002 | +0.6744 | +0.7658 | 0.933 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0908 | +0.1980 | +0.1997 | 0.0002 | +0.4755 | +0.6733 | 0.945 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 23 | +1 | +0.1232 | +0.1957 | +0.1970 | 0.0002 | +0.6911 | +0.7360 | 0.955 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 20 | +1 | +0.0897 | +0.1955 | +0.1964 | 0.0002 | +0.4870 | +0.6733 | 0.938 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 0 | +1 | +0.0754 | +0.1940 | +0.1950 | 0.0002 | +0.7475 | +0.7807 | 0.885 |
| `combo_max__first_bar_return__bar_body_rng_0` | Cluster 10 | +1 | +0.0944 | +0.1938 | +0.1949 | 0.0002 | +0.5724 | +0.7191 | 0.939 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Cluster 2 | +1 | +0.0742 | +0.1929 | +0.1930 | 0.0002 | +0.4284 | +0.6718 | 0.494 |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | Cluster 2 | +1 | +0.0665 | +0.1925 | +0.1927 | 0.0002 | +0.5928 | +0.7401 | 0.610 |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 9 | +1 | +0.1000 | +0.1864 | +0.1881 | 0.0002 | +0.7547 | +0.7535 | 0.891 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Cluster 2 | +1 | +0.0660 | +0.1858 | +0.1864 | 0.0002 | +0.6574 | +0.7488 | 0.795 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 7 | +1 | +0.0872 | +0.1852 | +0.1865 | 0.0002 | +0.5869 | +0.7057 | 0.938 |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Cluster 22 | +1 | +0.0902 | +0.1839 | +0.1847 | 0.0002 | +0.5811 | +0.7026 | 0.936 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 10 | +1 | +0.0917 | +0.1836 | +0.1849 | 0.0002 | +0.5672 | +0.7304 | 0.901 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 3 | +1 | +0.0833 | +0.1830 | +0.1846 | 0.0002 | +0.6883 | +0.7576 | 0.880 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 1 | +1 | +0.0910 | +0.1818 | +0.1831 | 0.0002 | +0.5267 | +0.6780 | 1.000 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.0828 | +0.1817 | +0.1829 | 0.0002 | +0.4753 | +0.6528 | 0.985 |
| `combo_max__max_up_ret__volume_surge_direction` | Cluster 16 | +1 | +0.0754 | +0.1797 | +0.1806 | 0.0002 | +0.6226 | +0.7504 | 0.884 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 13 | +1 | +0.0866 | +0.1780 | +0.1799 | 0.0002 | +0.4991 | +0.6888 | 0.981 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | Cluster 16 | +1 | +0.0745 | +0.1780 | +0.1791 | 0.0002 | +0.5990 | +0.7314 | 0.899 |
| `combo_rank_min__bar_body_rng_0__volume_surge_direction` | Cluster 10 | +1 | +0.0754 | +0.1769 | +0.1783 | 0.0002 | +0.5397 | +0.6923 | 0.886 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 4 | +1 | +0.0893 | +0.1747 | +0.1759 | 0.0004 | +0.4218 | +0.6651 | 0.933 |
| `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` | Cluster 2 | +1 | +0.0619 | +0.1738 | +0.1741 | 0.0004 | +0.4638 | +0.6965 | 1.000 |
| `star50_limit_proximity_early` | Cluster 17 | +1 | +0.0915 | +0.1720 | +0.1727 | 0.0008 | +0.4589 | +0.6954 | 0.945 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 16 | +1 | +0.0868 | +0.1690 | +0.1699 | 0.0010 | +0.6099 | +0.6949 | 0.943 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 24 | +1 | +0.1062 | +0.1686 | +0.1706 | 0.0010 | +0.4878 | +0.6615 | 0.917 |
| `max_up_ret` | Cluster 4 | +1 | +0.0767 | +0.1676 | +0.1683 | 0.0010 | +0.3955 | +0.6549 | 0.909 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 15 | +1 | +0.0979 | +0.1676 | +0.1678 | 0.0010 | +0.4518 | +0.6723 | 0.934 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.0803 | +0.1660 | +0.1672 | 0.0010 | +0.6402 | +0.7191 | 0.879 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0777 | +0.1660 | +0.1670 | 0.0010 | +0.6048 | +0.7381 | 0.783 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Cluster 10 | +1 | +0.0928 | +0.1657 | +0.1664 | 0.0010 | +0.4785 | +0.7021 | 1.000 |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | Cluster 9 | +1 | +0.1032 | +0.1643 | +0.1656 | 0.0010 | +0.6259 | +0.7160 | 0.919 |
| `combo_z_sum__first_bar_return__first_bar_sentiment` | Cluster 10 | +1 | +0.0921 | +0.1635 | +0.1643 | 0.0010 | +0.4150 | +0.6636 | 0.938 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 10 | +1 | +0.0929 | +0.1632 | +0.1640 | 0.0010 | +0.4797 | +0.6564 | 0.962 |
| `combo_rank_max__bar_body_rng_0__volume_surge_direction` | Cluster 10 | +1 | +0.0852 | +0.1619 | +0.1635 | 0.0012 | +0.4940 | +0.6790 | 0.978 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 17 | +1 | +0.0830 | +0.1612 | +0.1619 | 0.0012 | +0.4948 | +0.6949 | 0.802 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Cluster 1 | +1 | +0.1095 | +0.1599 | +0.1610 | 0.0012 | +0.4455 | +0.6769 | 0.919 |
| `combo_rank_min__first_bar_return__volume_weighted_price_position` | Cluster 20 | +1 | +0.0878 | +0.1583 | +0.1593 | 0.0014 | +0.4863 | +0.6965 | 0.934 |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | Cluster 10 | +1 | +0.0901 | +0.1492 | +0.1501 | 0.0026 | +0.5479 | +0.7016 | 0.878 |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | Cluster 22 | +1 | +0.0848 | +0.1476 | +0.1484 | 0.0028 | +0.6663 | +0.7149 | 0.972 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Cluster 18 | +1 | +0.0894 | +0.1467 | +0.1473 | 0.0036 | +0.4503 | +0.6646 | 0.789 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 12 | +1 | +0.0767 | +0.1416 | +0.1421 | 0.0050 | +0.5120 | +0.7088 | 0.880 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 12 | +1 | +0.0757 | +0.1356 | +0.1361 | 0.0080 | +0.4172 | +0.6888 | 0.813 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Cluster 11 | +1 | +0.0680 | +0.1333 | +0.1336 | 0.0092 | +0.5209 | +0.7216 | 0.806 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 18 | +1 | +0.0768 | +0.1267 | +0.1277 | 0.0122 | +0.5022 | +0.6805 | 0.927 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 18 | +1 | +0.0890 | +0.1262 | +0.1270 | 0.0132 | +0.4936 | +0.6841 | 0.947 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 13 | +1 | +0.0909 | +0.1159 | +0.1163 | 0.0210 | +0.4236 | +0.6610 | 0.909 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Cluster 19 | +1 | +0.0354 | +0.1107 | +0.1113 | 0.0288 | +0.4657 | +0.6641 | 0.546 |

### 300ETF / long
No features admitted.

### 300ETF / short
No features admitted.


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

### Cluster Overview per ETF / Side

| ETF | Side | Total Features | Clusters | Avg Silhouette | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 300ETF | single | 78 | 25 | 0.2852 | `[9, 7, 7, 7, 5, 4, 3, 3, 3, 3, 3, 3, ... (25 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 7 | 0.2852 | `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_mean__max_up_ret__volume_weighted_price_position`, `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_max__max_up_ret__volume_weighted_price_position`, `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 1 | 7 | 0.2852 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_min__star50_limit_proximity_early__bar_body_rng_0`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_mean__bar_body_rng_0__limit_down_proximity_early` |
| 300ETF | single | Cluster 2 | 4 | 0.2852 | `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `combo_rel_diff__limit_down_proximity_early__volume_concentration`, `combo_ratio__limit_down_proximity_early__volume_concentration`, `combo_clamp_diff__rbreaker_buy_setup_proximity_early__volume_concentration` |
| 300ETF | single | Cluster 3 | 1 | 0.2852 | `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 4 | 5 | 0.2852 | `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `combo_min__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `max_up_ret` |
| 300ETF | single | Cluster 5 | 2 | 0.2852 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_mean__max_up_ret__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 6 | 2 | 0.2852 | `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 7 | 1 | 0.2852 | `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 8 | 2 | 0.2852 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 9 | 7 | 0.2852 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio`, `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`, `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` |
| 300ETF | single | Cluster 10 | 9 | 0.2852 | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `combo_max__first_bar_return__bar_body_rng_0`, `combo_ratio__bar_body_rng_0__volume_weighted_price_position`, `combo_rank_min__bar_body_rng_0__volume_surge_direction`, `combo_ratio__first_bar_return__volume_surge_direction`, `combo_rank_max__bar_body_rng_0__volume_surge_direction`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_z_sum__first_bar_return__first_bar_sentiment`, `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` |
| 300ETF | single | Cluster 11 | 2 | 0.2852 | `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_ratio__first_bar_sentiment__volume_surge_direction` |
| 300ETF | single | Cluster 12 | 3 | 0.2852 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 300ETF | single | Cluster 13 | 2 | 0.2852 | `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `combo_rank_min__max_up_ret__first_bar_sentiment` |
| 300ETF | single | Cluster 14 | 3 | 0.2852 | `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `combo_rank_max__max_up_ret__first_bar_return`, `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 15 | 1 | 0.2852 | `combo_max__max_up_ret__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 16 | 3 | 0.2852 | `combo_max__max_up_ret__volume_surge_direction` | `combo_rank_max__max_up_ret__volume_surge_direction`, `combo_mean__max_up_ret__volume_surge_direction` |
| 300ETF | single | Cluster 17 | 3 | 0.2852 | `rbreaker_sell_setup_proximity_early` | `star50_limit_proximity_early`, `combo_rank_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` |
| 300ETF | single | Cluster 18 | 3 | 0.2852 | `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `combo_rel_diff__max_up_ret__early_vwap_acceleration`, `combo_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 19 | 1 | 0.2852 | `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | _(none)_ |
| 300ETF | single | Cluster 20 | 2 | 0.2852 | `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `combo_rank_min__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 21 | 1 | 0.2852 | `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 22 | 2 | 0.2852 | `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_max__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 23 | 3 | 0.2852 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 24 | 2 | 0.2852 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` |

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
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | `rank_max` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | `rank_max` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
