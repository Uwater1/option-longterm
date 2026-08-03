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
| 300ETF | single | 1,285 | 461 | 363 | 223 | 220 | 220 | 181 | 181 | 50 | 50 | 25 | `[6, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, ... (25 clusters)]` |
| 300ETF | long | 585 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 587 | 69 | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 50 | 25 | `[6, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, ... (25 clusters)]` | +0.1061 | [+0.0620, +0.1483] | +0.2310 | [+0.1400, +0.3260] | +0.7697 | 5.38% | 1.5466 | 3.78% | 1.1077 | 2.4434 | 2.99% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 50 | 25 | `[6, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, ... (25 clusters)]` | +0.0134* | [-0.1223, +0.1093] | +0.0636* | [-0.2524, +0.2983] | +0.1879 | 0.41% | 0.1652 | -1.25% | -0.4979 | -0.6929 | 5.50% |
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
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 15 | +1 | +0.0996 | +0.2881 | +0.2875 | 0.0000 | +0.8325 | +0.7694 | 0.913 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 15 | +1 | +0.1012 | +0.2766 | +0.2766 | 0.0000 | +0.6959 | +0.7375 | 0.000 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 10 | +1 | +0.0875 | +0.2655 | +0.2657 | 0.0000 | +0.8219 | +0.7566 | 0.904 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.0996 | +0.2628 | +0.2633 | 0.0000 | +0.7808 | +0.7885 | 0.917 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.0976 | +0.2578 | +0.2581 | 0.0000 | +0.7324 | +0.7715 | 0.807 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.0864 | +0.2523 | +0.2529 | 0.0000 | +0.8743 | +0.8003 | 0.785 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 24 | +1 | +0.0936 | +0.2499 | +0.2501 | 0.0000 | +0.6698 | +0.7761 | 0.702 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 16 | +1 | +0.0843 | +0.2365 | +0.2367 | 0.0000 | +0.5135 | +0.7097 | 0.895 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 20 | +1 | +0.0969 | +0.2333 | +0.2327 | 0.0000 | +0.6480 | +0.7916 | 0.941 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Cluster 13 | +1 | +0.0914 | +0.2318 | +0.2326 | 0.0000 | +0.8216 | +0.8029 | 0.936 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 17 | +1 | +0.0906 | +0.2309 | +0.2312 | 0.0000 | +0.7847 | +0.7571 | 0.922 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.0852 | +0.2286 | +0.2287 | 0.0000 | +0.4841 | +0.6778 | 0.895 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 3 | +1 | +0.0858 | +0.2260 | +0.2253 | 0.0002 | +0.5785 | +0.7180 | 0.843 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 18 | +1 | +0.0925 | +0.2232 | +0.2229 | 0.0002 | +0.6634 | +0.7344 | 0.842 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 24 | +1 | +0.0903 | +0.2219 | +0.2221 | 0.0002 | +0.6850 | +0.7792 | 0.945 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 13 | +1 | +0.0901 | +0.2199 | +0.2204 | 0.0002 | +0.7998 | +0.7833 | 0.890 |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Cluster 7 | +1 | +0.0953 | +0.2186 | +0.2190 | 0.0002 | +0.6989 | +0.7658 | 0.911 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 19 | +1 | +0.0956 | +0.2183 | +0.2179 | 0.0002 | +0.5874 | +0.7283 | 0.916 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 17 | +1 | +0.0959 | +0.2163 | +0.2166 | 0.0002 | +0.6930 | +0.7277 | 0.944 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Cluster 5 | +1 | +0.0907 | +0.2155 | +0.2166 | 0.0002 | +0.5717 | +0.7138 | 0.927 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 17 | +1 | +0.0892 | +0.2147 | +0.2148 | 0.0002 | +0.7471 | +0.7617 | 0.917 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 7 | +1 | +0.0893 | +0.2095 | +0.2097 | 0.0002 | +0.7133 | +0.7499 | 0.882 |
| `combo_max__first_bar_return__volume_weighted_price_position` | Cluster 5 | +1 | +0.0896 | +0.2093 | +0.2104 | 0.0002 | +0.6036 | +0.7267 | 0.939 |
| `max_up_ret` | Cluster 8 | +1 | +0.0742 | +0.2051 | +0.2056 | 0.0002 | +0.6225 | +0.7216 | 0.937 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 19 | +1 | +0.0951 | +0.2045 | +0.2038 | 0.0002 | +0.6024 | +0.7375 | 0.942 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 13 | +1 | +0.0805 | +0.2042 | +0.2050 | 0.0002 | +0.8858 | +0.8322 | 0.904 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 20 | +1 | +0.0963 | +0.2034 | +0.2025 | 0.0002 | +0.5403 | +0.7241 | 0.862 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 7 | +1 | +0.0905 | +0.2028 | +0.2027 | 0.0002 | +0.6456 | +0.7777 | 0.930 |
| `combo_rank_max__bar_ret_0__opening_drive_thrust_ratio` | Cluster 22 | +1 | +0.0992 | +0.2005 | +0.2011 | 0.0002 | +0.4677 | +0.7195 | 0.949 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 23 | +1 | +0.0847 | +0.1997 | +0.1998 | 0.0002 | +0.6211 | +0.6974 | 0.919 |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0932 | +0.1995 | +0.1997 | 0.0002 | +0.5166 | +0.6768 | 0.890 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 10 | +1 | +0.0790 | +0.1994 | +0.1999 | 0.0002 | +0.4588 | +0.7349 | 0.901 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0768 | +0.1986 | +0.1991 | 0.0002 | +0.5819 | +0.7210 | 0.715 |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.0854 | +0.1985 | +0.1982 | 0.0002 | +0.4670 | +0.6783 | 0.929 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 22 | +1 | +0.0985 | +0.1959 | +0.1967 | 0.0002 | +0.4688 | +0.6938 | 0.902 |
| `first_bar_return` | Cluster 7 | +1 | +0.0874 | +0.1925 | +0.1926 | 0.0002 | +0.6512 | +0.7524 | 0.949 |
| `combo_mean__bar_ret_0__first_bar_sentiment` | Cluster 7 | +1 | +0.0874 | +0.1925 | +0.1926 | 0.0002 | +0.6512 | +0.7524 | 0.945 |
| `bar_body_rng_0` | Cluster 7 | +1 | +0.0921 | +0.1921 | +0.1925 | 0.0002 | +0.6655 | +0.7210 | 0.924 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 3 | +1 | +0.0732 | +0.1899 | +0.1894 | 0.0002 | +0.6872 | +0.7735 | 0.876 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 12 | +1 | +0.0827 | +0.1811 | +0.1817 | 0.0004 | +0.5828 | +0.7118 | 0.900 |
| `volume_weighted_price_position` | Cluster 14 | +1 | +0.0791 | +0.1777 | +0.1783 | 0.0008 | +0.6336 | +0.7535 | 0.857 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 11 | +1 | +0.0858 | +0.1756 | +0.1752 | 0.0008 | +0.5438 | +0.7066 | 0.921 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 9 | +1 | +0.0887 | +0.1738 | +0.1743 | 0.0010 | +0.5990 | +0.7283 | 0.883 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 1 | +1 | +0.0904 | +0.1731 | +0.1727 | 0.0010 | +0.5593 | +0.7344 | 0.921 |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | Cluster 21 | +1 | +0.0812 | +0.1727 | +0.1722 | 0.0010 | +0.6644 | +0.7648 | 0.856 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0589 | +0.1714 | +0.1712 | 0.0010 | +0.5584 | +0.6742 | 0.827 |
| `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | Cluster 21 | +1 | +0.0743 | +0.1693 | +0.1698 | 0.0012 | +0.5537 | +0.6814 | 0.894 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 4 | +1 | +0.0964 | +0.1614 | +0.1623 | 0.0014 | +0.5990 | +0.7174 | 0.841 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 4 | +1 | +0.0889 | +0.1362 | +0.1369 | 0.0064 | +0.5725 | +0.7154 | 0.875 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Cluster 6 | +1 | +0.0528 | +0.1264 | +0.1276 | 0.0124 | +0.4721 | +0.6629 | 0.538 |

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
| 300ETF | single | 50 | 25 | 0.3612 | `[6, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, ... (25 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 2 | 0.3612 | `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 1 | 2 | 0.3612 | `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` |
| 300ETF | single | Cluster 2 | 2 | 0.3612 | `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 3 | 2 | 0.3612 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 4 | 2 | 0.3612 | `combo_diff__max_up_ret__early_vwap_acceleration` | `combo_rel_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 5 | 2 | 0.3612 | `combo_rank_max__bar_ret_0__volume_weighted_price_position` | `combo_max__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 6 | 1 | 0.3612 | `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | _(none)_ |
| 300ETF | single | Cluster 7 | 6 | 0.3612 | `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `combo_ratio__first_bar_return__volume_weighted_price_position`, `bar_body_rng_0`, `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `first_bar_return`, `combo_mean__bar_ret_0__first_bar_sentiment` |
| 300ETF | single | Cluster 8 | 1 | 0.3612 | `max_up_ret` | _(none)_ |
| 300ETF | single | Cluster 9 | 2 | 0.3612 | `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` |
| 300ETF | single | Cluster 10 | 2 | 0.3612 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_min__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 11 | 1 | 0.3612 | `combo_min__max_up_ret__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 12 | 3 | 0.3612 | `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 13 | 3 | 0.3612 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 14 | 1 | 0.3612 | `volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 15 | 2 | 0.3612 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 16 | 1 | 0.3612 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | _(none)_ |
| 300ETF | single | Cluster 17 | 3 | 0.3612 | `combo_max__max_up_ret__bar_ret_0` | `combo_mean__max_up_ret__bar_body_rng_0`, `combo_rank_max__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 18 | 1 | 0.3612 | `combo_max__max_up_ret__first_bar_sentiment` | _(none)_ |
| 300ETF | single | Cluster 19 | 2 | 0.3612 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 20 | 2 | 0.3612 | `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` |
| 300ETF | single | Cluster 21 | 2 | 0.3612 | `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | `combo_sig_product__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 22 | 2 | 0.3612 | `combo_max__first_bar_return__opening_drive_thrust_ratio` | `combo_rank_max__bar_ret_0__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 23 | 1 | 0.3612 | `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 24 | 2 | 0.3612 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `mean` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | `tri_mean` | a=`bar_ret_0`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | `rank_max` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_max__first_bar_return__volume_weighted_price_position` | `max` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_rank_max__bar_ret_0__opening_drive_thrust_ratio` | `rank_max` | a=`bar_ret_0`, b=`opening_drive_thrust_ratio` |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_median` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `rank_min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | `max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_mean__bar_ret_0__first_bar_sentiment` | `mean` | a=`bar_ret_0`, b=`first_bar_sentiment` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | `sig_product` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | `tri_median` | a=`smooth_momentum_structure`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
