# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2017_2025`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._
_Note: Cost metrics incorporate 8 bps (0.0008) transaction cost per position state transition (realistic for liquid ETFs). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted | Clusters | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 300ETF | single | 1,598 | 637 | 523 | 412 | 410 | 410 | 394 | 391 | 139 | 110 | 39 | `[11, 9, 8, 8, 6, 6, 4, 3, 3, 3, 3, 3, ... (39 clusters)]` |
| 300ETF | long | 585 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 587 | 69 | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 110 | 39 | `[11, 9, 8, 8, 6, 6, 4, 3, 3, 3, 3, 3, ... (39 clusters)]` | +0.1032 | [+0.0606, +0.1453] | +0.2492 | [+0.1552, +0.3443] | +0.7939 | 5.77% | 1.6476 | 4.21% | 1.2231 | 2.7759 | 2.53% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 110 | 39 | `[11, 9, 8, 8, 6, 6, 4, 3, 3, 3, 3, 3, ... (39 clusters)]` | +0.0105* | [-0.1238, +0.1108] | +0.0397* | [-0.2759, +0.2585] | +0.2242 | 0.58% | 0.2506 | -1.01% | -0.4314 | -0.5971 | 5.03% |
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
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 12 | +1 | +0.0996 | +0.2881 | +0.2875 | 0.0000 | +0.8325 | +0.7694 | 0.973 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.1035 | +0.2826 | +0.2824 | 0.0000 | +0.6965 | +0.7571 | 0.937 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 12 | +1 | +0.1012 | +0.2766 | +0.2766 | 0.0000 | +0.6959 | +0.7375 | 0.913 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 15 | +1 | +0.1003 | +0.2709 | +0.2714 | 0.0000 | +0.7164 | +0.7576 | 0.907 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 33 | +1 | +0.0875 | +0.2655 | +0.2657 | 0.0000 | +0.8219 | +0.7566 | 0.782 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 15 | +1 | +0.0996 | +0.2628 | +0.2633 | 0.0000 | +0.7808 | +0.7885 | 0.899 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0864 | +0.2523 | +0.2529 | 0.0000 | +0.8743 | +0.8003 | 0.827 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 17 | +1 | +0.0936 | +0.2499 | +0.2501 | 0.0000 | +0.6698 | +0.7761 | 0.904 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 32 | +1 | +0.0957 | +0.2456 | +0.2452 | 0.0000 | +0.6495 | +0.7185 | 0.874 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.0971 | +0.2430 | +0.2433 | 0.0000 | +0.7080 | +0.7560 | 0.947 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0926 | +0.2384 | +0.2392 | 0.0000 | +0.6527 | +0.7391 | 0.908 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 12 | +1 | +0.0843 | +0.2365 | +0.2367 | 0.0000 | +0.5135 | +0.7097 | 1.000 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Cluster 13 | +1 | +0.0875 | +0.2339 | +0.2334 | 0.0000 | +0.7192 | +0.7468 | 0.820 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 38 | +1 | +0.0969 | +0.2333 | +0.2327 | 0.0000 | +0.6480 | +0.7916 | 0.994 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Cluster 11 | +1 | +0.0914 | +0.2318 | +0.2326 | 0.0000 | +0.8216 | +0.8029 | 1.000 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 29 | +1 | +0.0906 | +0.2309 | +0.2312 | 0.0000 | +0.7847 | +0.7571 | 0.864 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 12 | +1 | +0.0852 | +0.2286 | +0.2287 | 0.0000 | +0.4841 | +0.6778 | 1.000 |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 3 | +1 | +0.0923 | +0.2284 | +0.2274 | 0.0000 | +0.6106 | +0.7488 | 0.862 |
| `combo_max__first_bar_return__volume_surge_direction` | Cluster 13 | +1 | +0.0790 | +0.2280 | +0.2267 | 0.0002 | +0.7009 | +0.7669 | 0.865 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 15 | +1 | +0.0858 | +0.2260 | +0.2253 | 0.0002 | +0.5785 | +0.7180 | 0.843 |
| `combo_rank_max__first_bar_return__volume_surge_direction` | Cluster 13 | +1 | +0.0762 | +0.2246 | +0.2232 | 0.0002 | +0.7177 | +0.7782 | 0.925 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 6 | +1 | +0.0925 | +0.2232 | +0.2229 | 0.0002 | +0.6634 | +0.7344 | 0.873 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 19 | +1 | +0.0934 | +0.2221 | +0.2230 | 0.0002 | +0.6061 | +0.7257 | 0.913 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 4 | +1 | +0.0851 | +0.2219 | +0.2207 | 0.0002 | +0.7889 | +0.7669 | 0.904 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 17 | +1 | +0.0903 | +0.2219 | +0.2221 | 0.0002 | +0.6850 | +0.7792 | 0.945 |
| `combo_max__max_up_ret__volume_surge_direction` | Cluster 6 | +1 | +0.0732 | +0.2210 | +0.2198 | 0.0002 | +0.7910 | +0.7643 | 0.946 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 11 | +1 | +0.0901 | +0.2199 | +0.2204 | 0.0002 | +0.7998 | +0.7833 | 0.964 |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Cluster 23 | +1 | +0.0953 | +0.2186 | +0.2190 | 0.0002 | +0.6989 | +0.7658 | 1.000 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0932 | +0.2167 | +0.2178 | 0.0002 | +0.6191 | +0.7133 | 0.931 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 29 | +1 | +0.0959 | +0.2163 | +0.2166 | 0.0002 | +0.6930 | +0.7277 | 0.960 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Cluster 19 | +1 | +0.0907 | +0.2155 | +0.2166 | 0.0002 | +0.5717 | +0.7138 | 0.943 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 29 | +1 | +0.0892 | +0.2147 | +0.2148 | 0.0002 | +0.7471 | +0.7617 | 0.954 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0979 | +0.2124 | +0.2130 | 0.0002 | +0.7324 | +0.7787 | 1.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0804 | +0.2119 | +0.2119 | 0.0002 | +0.6780 | +0.7545 | 0.945 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | Cluster 6 | +1 | +0.0722 | +0.2113 | +0.2101 | 0.0002 | +0.7967 | +0.7679 | 0.901 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 31 | +1 | +0.1028 | +0.2112 | +0.2105 | 0.0002 | +0.6170 | +0.7236 | 0.973 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 38 | +1 | +0.0893 | +0.2095 | +0.2097 | 0.0002 | +0.7133 | +0.7499 | 1.000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0927 | +0.2066 | +0.2062 | 0.0002 | +0.6739 | +0.7149 | 0.939 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 17 | +1 | +0.0902 | +0.2062 | +0.2060 | 0.0002 | +0.6930 | +0.7910 | 0.949 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 15 | +1 | +0.0807 | +0.2054 | +0.2055 | 0.0002 | +0.5406 | +0.7226 | 0.911 |
| `max_up_ret` | Cluster 8 | +1 | +0.0742 | +0.2051 | +0.2056 | 0.0002 | +0.6225 | +0.7216 | 0.937 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 32 | +1 | +0.0951 | +0.2045 | +0.2038 | 0.0002 | +0.6024 | +0.7375 | 0.930 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 11 | +1 | +0.0805 | +0.2042 | +0.2050 | 0.0002 | +0.8858 | +0.8322 | 0.904 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 12 | +1 | +0.0963 | +0.2034 | +0.2025 | 0.0002 | +0.5403 | +0.7241 | 0.941 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0834 | +0.2033 | +0.2039 | 0.0002 | +0.7770 | +0.8024 | 0.940 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 38 | +1 | +0.0905 | +0.2028 | +0.2027 | 0.0002 | +0.6456 | +0.7777 | 0.965 |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Cluster 27 | +1 | +0.0924 | +0.2012 | +0.2019 | 0.0002 | +0.6164 | +0.7437 | 1.000 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 30 | +1 | +0.1039 | +0.2012 | +0.2009 | 0.0002 | +0.5110 | +0.7205 | 1.000 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 25 | +1 | +0.0992 | +0.2005 | +0.2011 | 0.0002 | +0.4677 | +0.7195 | 0.912 |
| `combo_rank_min__max_up_ret__volume_surge_direction` | Cluster 4 | +1 | +0.0815 | +0.2000 | +0.1994 | 0.0002 | +0.4369 | +0.6758 | 0.901 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_body_rng_0` | Cluster 2 | +1 | +0.0684 | +0.1999 | +0.2000 | 0.0002 | +0.5497 | +0.6891 | 0.988 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 24 | +1 | +0.0847 | +0.1997 | +0.1998 | 0.0002 | +0.6211 | +0.6974 | 1.000 |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 27 | +1 | +0.0932 | +0.1995 | +0.1997 | 0.0002 | +0.5166 | +0.6768 | 0.893 |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 6 | +1 | +0.0846 | +0.1995 | +0.1983 | 0.0002 | +0.6159 | +0.7411 | 0.930 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 33 | +1 | +0.0790 | +0.1994 | +0.1999 | 0.0002 | +0.4588 | +0.7349 | 0.921 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0768 | +0.1986 | +0.1991 | 0.0002 | +0.5819 | +0.7210 | 0.714 |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 12 | +1 | +0.0854 | +0.1985 | +0.1982 | 0.0002 | +0.4670 | +0.6783 | 1.000 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 25 | +1 | +0.0985 | +0.1959 | +0.1967 | 0.0002 | +0.4688 | +0.6938 | 1.000 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | Cluster 36 | +1 | +0.0634 | +0.1954 | +0.1963 | 0.0002 | +0.6150 | +0.7133 | 0.851 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0848 | +0.1930 | +0.1936 | 0.0002 | +0.6691 | +0.7329 | 0.907 |
| `first_bar_return` | Cluster 38 | +1 | +0.0874 | +0.1925 | +0.1926 | 0.0002 | +0.6512 | +0.7524 | 0.949 |
| `combo_mean__first_bar_return__first_bar_sentiment` | Cluster 38 | +1 | +0.0874 | +0.1925 | +0.1926 | 0.0002 | +0.6512 | +0.7524 | 0.947 |
| `combo_min__first_bar_return__bar_body_rng_0` | Cluster 38 | +1 | +0.0891 | +0.1923 | +0.1926 | 0.0002 | +0.6256 | +0.7375 | 0.950 |
| `combo_sig_product__bar_ret_0__bar_body_rng_0` | Cluster 38 | +1 | +0.0927 | +0.1921 | +0.1925 | 0.0002 | +0.6657 | +0.7221 | 1.000 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0910 | +0.1910 | +0.1915 | 0.0002 | +0.5273 | +0.7005 | 0.933 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 10 | +1 | +0.0732 | +0.1899 | +0.1894 | 0.0002 | +0.6872 | +0.7735 | 0.876 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Cluster 3 | +1 | +0.0840 | +0.1898 | +0.1891 | 0.0002 | +0.5697 | +0.7123 | 0.968 |
| `combo_tri_min__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0929 | +0.1895 | +0.1898 | 0.0002 | +0.6344 | +0.7293 | 1.000 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0762 | +0.1886 | +0.1891 | 0.0002 | +0.5094 | +0.7262 | 0.946 |
| `combo_min__max_up_ret__volume_surge_direction` | Cluster 4 | +1 | +0.0854 | +0.1881 | +0.1872 | 0.0002 | +0.4516 | +0.6526 | 0.925 |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 30 | +1 | +0.1031 | +0.1879 | +0.1880 | 0.0002 | +0.5934 | +0.6799 | 0.939 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0712 | +0.1875 | +0.1876 | 0.0002 | +0.5021 | +0.7108 | 0.930 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 24 | +1 | +0.0870 | +0.1844 | +0.1846 | 0.0004 | +0.5295 | +0.7005 | 0.937 |
| `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 25 | +1 | +0.0984 | +0.1816 | +0.1821 | 0.0004 | +0.6208 | +0.7452 | 0.940 |
| `combo_product__max_up_ret__opening_drive_thrust_ratio` | Cluster 14 | +1 | +0.0364 | +0.1814 | +0.1800 | 0.0004 | +0.4952 | +0.6536 | 0.488 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 15 | +1 | +0.0827 | +0.1811 | +0.1817 | 0.0004 | +0.5828 | +0.7118 | 1.000 |
| `combo_min__first_bar_return__volume_surge_direction` | Cluster 13 | +1 | +0.0812 | +0.1784 | +0.1778 | 0.0006 | +0.5580 | +0.6948 | 1.000 |
| `combo_max__volume_weighted_price_position__first_bar_sentiment` | Cluster 16 | +1 | +0.0829 | +0.1778 | +0.1772 | 0.0008 | +0.5604 | +0.7319 | 0.924 |
| `volume_weighted_price_position` | Cluster 36 | +1 | +0.0791 | +0.1777 | +0.1783 | 0.0008 | +0.6336 | +0.7535 | 0.871 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0` | Cluster 2 | +1 | +0.0662 | +0.1770 | +0.1774 | 0.0008 | +0.4040 | +0.6783 | 0.923 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 36 | +1 | +0.0868 | +0.1766 | +0.1782 | 0.0008 | +0.5792 | +0.7123 | 0.825 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 5 | +1 | +0.0858 | +0.1756 | +0.1752 | 0.0008 | +0.5438 | +0.7066 | 0.921 |
| `combo_max__volume_weighted_price_position__volume_surge_direction` | Cluster 16 | +1 | +0.0754 | +0.1755 | +0.1750 | 0.0008 | +0.6122 | +0.7118 | 0.957 |
| `combo_mean__volume_weighted_price_position__first_bar_sentiment` | Cluster 22 | +1 | +0.0855 | +0.1745 | +0.1740 | 0.0008 | +0.5993 | +0.7586 | 0.949 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 8 | +1 | +0.0887 | +0.1738 | +0.1743 | 0.0010 | +0.5990 | +0.7283 | 0.906 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 28 | +1 | +0.0904 | +0.1731 | +0.1727 | 0.0010 | +0.5593 | +0.7344 | 0.943 |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | Cluster 18 | +1 | +0.0812 | +0.1727 | +0.1722 | 0.0010 | +0.6644 | +0.7648 | 0.881 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0589 | +0.1714 | +0.1712 | 0.0010 | +0.5584 | +0.6742 | 0.827 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0805 | +0.1702 | +0.1701 | 0.0012 | +0.4800 | +0.6840 | 0.922 |
| `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | Cluster 20 | +1 | +0.0743 | +0.1693 | +0.1698 | 0.0012 | +0.5537 | +0.6814 | 0.894 |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | Cluster 22 | +1 | +0.0918 | +0.1680 | +0.1672 | 0.0012 | +0.5785 | +0.7015 | 0.941 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 15 | +1 | +0.0836 | +0.1680 | +0.1686 | 0.0012 | +0.4024 | +0.6557 | 1.000 |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | Cluster 21 | +1 | +0.0888 | +0.1673 | +0.1660 | 0.0012 | +0.5857 | +0.7216 | 0.932 |
| `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0677 | +0.1663 | +0.1665 | 0.0014 | +0.5386 | +0.6958 | 0.892 |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 11 | +1 | +0.0943 | +0.1647 | +0.1656 | 0.0014 | +0.6586 | +0.7370 | 0.937 |
| `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 26 | +1 | +0.0851 | +0.1624 | +0.1631 | 0.0014 | +0.5215 | +0.6861 | 0.938 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 37 | +1 | +0.0964 | +0.1614 | +0.1623 | 0.0014 | +0.5990 | +0.7174 | 0.841 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | Cluster 34 | +1 | +0.0469 | +0.1561 | +0.1565 | 0.0020 | +0.6094 | +0.7051 | 0.835 |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | Cluster 7 | +1 | +0.0779 | +0.1557 | +0.1552 | 0.0020 | +0.4840 | +0.6948 | 0.893 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__volume_weighted_price_position` | Cluster 34 | +1 | +0.0466 | +0.1519 | +0.1528 | 0.0028 | +0.5446 | +0.7236 | 0.853 |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | Cluster 14 | +1 | +0.0534 | +0.1451 | +0.1460 | 0.0042 | +0.4351 | +0.6665 | 0.320 |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | Cluster 35 | +1 | +0.0717 | +0.1434 | +0.1427 | 0.0048 | +0.4977 | +0.6644 | 0.914 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 37 | +1 | +0.0889 | +0.1362 | +0.1369 | 0.0064 | +0.5725 | +0.7154 | 0.875 |
| `morning_volume_weighted_momentum` | Cluster 9 | +1 | +0.0585 | +0.1340 | +0.1348 | 0.0078 | +0.4580 | +0.6788 | 0.812 |
| `always_in_trend_persistence` | Cluster 0 | +1 | +0.0546 | +0.1335 | +0.1341 | 0.0078 | +0.4601 | +0.6845 | 0.673 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Cluster 38 | +1 | +0.0796 | +0.1306 | +0.1312 | 0.0094 | +0.3195 | +0.6577 | 0.033 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Cluster 0 | +1 | +0.0528 | +0.1264 | +0.1276 | 0.0124 | +0.4721 | +0.6629 | 0.577 |
| `combo_ratio__max_up_ret__bar_vol_0` | Cluster 8 | +1 | +0.0827 | +0.1253 | +0.1260 | 0.0130 | +0.5632 | +0.6963 | 0.824 |
| `combo_ratio__volume_surge_direction__volume_weighted_price_position` | Cluster 13 | +1 | +0.0725 | +0.1128 | +0.1108 | 0.0250 | +0.5035 | +0.6531 | 0.891 |
| `combo_max__first_bar_sentiment__volume_surge_direction` | Cluster 13 | +1 | +0.0750 | +0.1068 | +0.1051 | 0.0324 | +0.4097 | +0.6516 | 0.916 |

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
| 300ETF | single | 110 | 39 | 0.2477 | `[11, 9, 8, 8, 6, 6, 4, 3, 3, 3, 3, 3, ... (39 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 2 | 0.2477 | `always_in_trend_persistence` | `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` |
| 300ETF | single | Cluster 1 | 2 | 0.2477 | `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 2 | 2 | 0.2477 | `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_body_rng_0` | `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 3 | 2 | 0.2477 | `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | `combo_min__opening_drive_thrust_ratio__volume_surge_direction` |
| 300ETF | single | Cluster 4 | 3 | 0.2477 | `combo_mean__max_up_ret__volume_surge_direction` | `combo_rank_min__max_up_ret__volume_surge_direction`, `combo_min__max_up_ret__volume_surge_direction` |
| 300ETF | single | Cluster 5 | 1 | 0.2477 | `combo_min__max_up_ret__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 6 | 4 | 0.2477 | `combo_max__max_up_ret__first_bar_sentiment` | `combo_max__max_up_ret__volume_surge_direction`, `combo_rank_max__max_up_ret__volume_surge_direction`, `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` |
| 300ETF | single | Cluster 7 | 1 | 0.2477 | `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 8 | 9 | 0.2477 | `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`, `max_up_ret`, `combo_rank_max__max_up_ret__opening_drive_thrust_ratio`, `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio`, `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`, `combo_sig_product__max_up_ret__opening_drive_thrust_ratio`, `combo_ratio__max_up_ret__bar_vol_0` |
| 300ETF | single | Cluster 9 | 1 | 0.2477 | `morning_volume_weighted_momentum` | _(none)_ |
| 300ETF | single | Cluster 10 | 2 | 0.2477 | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 11 | 11 | 0.2477 | `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | `combo_mean__max_up_ret__volume_weighted_price_position`, `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`, `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_max__max_up_ret__volume_weighted_price_position`, `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_tri_min__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 12 | 8 | 0.2477 | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 13 | 6 | 0.2477 | `combo_min__bar_body_rng_0__volume_surge_direction` | `combo_max__first_bar_return__volume_surge_direction`, `combo_rank_max__first_bar_return__volume_surge_direction`, `combo_min__first_bar_return__volume_surge_direction`, `combo_ratio__volume_surge_direction__volume_weighted_price_position`, `combo_max__first_bar_sentiment__volume_surge_direction` |
| 300ETF | single | Cluster 14 | 2 | 0.2477 | `combo_product__max_up_ret__opening_drive_thrust_ratio` | `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` |
| 300ETF | single | Cluster 15 | 6 | 0.2477 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 16 | 2 | 0.2477 | `combo_max__volume_weighted_price_position__volume_surge_direction` | `combo_max__volume_weighted_price_position__first_bar_sentiment` |
| 300ETF | single | Cluster 17 | 3 | 0.2477 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 18 | 1 | 0.2477 | `combo_sig_product__first_bar_return__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 19 | 2 | 0.2477 | `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `combo_rank_max__bar_ret_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 20 | 1 | 0.2477 | `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 21 | 1 | 0.2477 | `combo_min__volume_weighted_price_position__volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 22 | 2 | 0.2477 | `combo_mean__volume_weighted_price_position__first_bar_sentiment` | `combo_mean__volume_weighted_price_position__volume_surge_direction` |
| 300ETF | single | Cluster 23 | 1 | 0.2477 | `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 24 | 2 | 0.2477 | `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 25 | 3 | 0.2477 | `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | `combo_max__first_bar_return__opening_drive_thrust_ratio`, `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 26 | 1 | 0.2477 | `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 27 | 2 | 0.2477 | `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 28 | 1 | 0.2477 | `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 29 | 3 | 0.2477 | `combo_rank_max__max_up_ret__first_bar_return` | `combo_mean__max_up_ret__bar_body_rng_0`, `combo_max__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 30 | 2 | 0.2477 | `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 31 | 1 | 0.2477 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 32 | 2 | 0.2477 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 33 | 2 | 0.2477 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_min__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 34 | 2 | 0.2477 | `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | `combo_tri_mean__smooth_momentum_structure__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 35 | 1 | 0.2477 | `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 36 | 3 | 0.2477 | `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | `volume_weighted_price_position`, `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 37 | 2 | 0.2477 | `combo_diff__max_up_ret__early_vwap_acceleration` | `combo_rel_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 38 | 8 | 0.2477 | `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_min__first_bar_return__bar_body_rng_0`, `first_bar_return`, `combo_mean__first_bar_return__first_bar_sentiment`, `combo_sig_product__bar_ret_0__bar_body_rng_0`, `combo_ratio__first_bar_return__volume_surge_direction` |

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
| `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_body_rng_0` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_median` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `rank_min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | `max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_mean__first_bar_return__first_bar_sentiment` | `mean` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_min__first_bar_return__bar_body_rng_0` | `min` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_sig_product__bar_ret_0__bar_body_rng_0` | `sig_product` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_tri_min__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | `tri_min` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `rank_max` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__volume_surge_direction` | `min` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_max` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_product__max_up_ret__opening_drive_thrust_ratio` | `product` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__first_bar_return__volume_surge_direction` | `min` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_max__volume_weighted_price_position__first_bar_sentiment` | `max` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
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
| `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_median` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`smooth_momentum_structure`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | `sig_product` | a=`bar_ret_0`, b=`opening_drive_thrust_ratio` |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__volume_weighted_price_position` | `tri_mean` | a=`smooth_momentum_structure`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | `ratio` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_concentration` |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | `ratio` | a=`first_bar_sentiment`, b=`volume_weighted_price_position` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_ratio__first_bar_return__volume_surge_direction` | `ratio` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_ratio__max_up_ret__bar_vol_0` | `ratio` | a=`max_up_ret`, b=`bar_vol_0` |
| `combo_ratio__volume_surge_direction__volume_weighted_price_position` | `ratio` | a=`volume_surge_direction`, b=`volume_weighted_price_position` |
| `combo_max__first_bar_sentiment__volume_surge_direction` | `max` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
