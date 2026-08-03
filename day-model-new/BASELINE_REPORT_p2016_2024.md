# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2016_2024`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._
_Note: Cost metrics incorporate 8 bps (0.0008) transaction cost per position state transition (realistic for liquid ETFs). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted | Clusters | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 300ETF | single | 1,287 | 413 | 306 | 209 | 197 | 195 | 169 | 169 | 62 | 60 | 28 | `[4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (28 clusters)]` |
| 300ETF | long | 586 | 58 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 300ETF | short | 587 | 69 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 60 | 28 | `[4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (28 clusters)]` | +0.1132 | [+0.0702, +0.1543] | +0.2191 | [+0.1185, +0.3144] | +0.8545 | 4.74% | 1.5413 | 3.16% | 1.0448 | 2.0182 | 3.25% |
| 300ETF | long | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | - | `-` | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 60 | 28 | `[4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (28 clusters)]` | +0.0253* | [-0.0615, +0.1133] | +0.0697* | [-0.1359, +0.2334] | +0.5636 | 2.31% | 0.6134 | 0.75% | 0.2003 | 0.4272 | 4.45% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 26 | +1 | +0.1000 | +0.2637 | +0.2645 | 0.0000 | +0.6771 | +0.7285 | 0.000 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 24 | +1 | +0.0915 | +0.2524 | +0.2527 | 0.0000 | +0.8557 | +0.8123 | 0.935 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.0989 | +0.2515 | +0.2511 | 0.0000 | +0.6807 | +0.7707 | 0.851 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 12 | +1 | +0.1022 | +0.2509 | +0.2505 | 0.0000 | +0.7382 | +0.7810 | 0.915 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 26 | +1 | +0.1045 | +0.2502 | +0.2509 | 0.0000 | +0.6504 | +0.7244 | 0.880 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 4 | +1 | +0.1013 | +0.2493 | +0.2494 | 0.0000 | +0.6618 | +0.7450 | 0.908 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 3 | +1 | +0.0924 | +0.2468 | +0.2470 | 0.0000 | +0.6402 | +0.6946 | 0.903 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Cluster 20 | +1 | +0.0886 | +0.2419 | +0.2414 | 0.0000 | +0.7478 | +0.7548 | 0.888 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 6 | +1 | +0.0939 | +0.2395 | +0.2396 | 0.0000 | +0.7820 | +0.7856 | 0.586 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 0 | +1 | +0.0952 | +0.2350 | +0.2352 | 0.0000 | +0.6025 | +0.7136 | 0.926 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 25 | +1 | +0.1098 | +0.2341 | +0.2347 | 0.0000 | +0.5858 | +0.7368 | 0.889 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 27 | +1 | +0.1008 | +0.2251 | +0.2250 | 0.0000 | +0.4935 | +0.6545 | 0.860 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 24 | +1 | +0.0998 | +0.2226 | +0.2227 | 0.0000 | +0.6215 | +0.7167 | 0.925 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 22 | +1 | +0.0926 | +0.2224 | +0.2225 | 0.0000 | +0.6399 | +0.7028 | 0.915 |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 5 | +1 | +0.0995 | +0.2176 | +0.2173 | 0.0000 | +0.5767 | +0.7126 | 0.889 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0955 | +0.2167 | +0.2162 | 0.0000 | +0.6142 | +0.6982 | 0.869 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 22 | +1 | +0.0909 | +0.2167 | +0.2167 | 0.0000 | +0.7077 | +0.7311 | 0.924 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 13 | +1 | +0.0899 | +0.2155 | +0.2160 | 0.0000 | +0.4379 | +0.6545 | 0.895 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 6 | +1 | +0.0828 | +0.2116 | +0.2119 | 0.0000 | +0.8349 | +0.8231 | 0.898 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 10 | +1 | +0.0882 | +0.2082 | +0.2081 | 0.0000 | +0.5333 | +0.6766 | 0.896 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 3 | +1 | +0.1001 | +0.2075 | +0.2076 | 0.0000 | +0.5693 | +0.6915 | 0.944 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 15 | +1 | +0.1010 | +0.2067 | +0.2064 | 0.0000 | +0.6578 | +0.7326 | 0.895 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 27 | +1 | +0.1095 | +0.2034 | +0.2038 | 0.0000 | +0.5295 | +0.6869 | 0.939 |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | Cluster 24 | +1 | +0.1007 | +0.2003 | +0.2006 | 0.0000 | +0.6771 | +0.7368 | 0.855 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 2 | +1 | +0.0953 | +0.1982 | +0.1987 | 0.0000 | +0.4731 | +0.6668 | 0.925 |
| `bar_body_rng_0` | Cluster 16 | +1 | +0.0989 | +0.1976 | +0.1979 | 0.0000 | +0.6275 | +0.7054 | 0.894 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 21 | +1 | +0.0849 | +0.1940 | +0.1933 | 0.0000 | +0.5866 | +0.7260 | 0.715 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 17 | +1 | +0.0929 | +0.1930 | +0.1935 | 0.0000 | +0.5031 | +0.6869 | 0.912 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 27 | +1 | +0.1013 | +0.1925 | +0.1925 | 0.0000 | +0.5461 | +0.6961 | 0.950 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 16 | +1 | +0.0972 | +0.1917 | +0.1921 | 0.0000 | +0.5346 | +0.7008 | 0.946 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 1 | +1 | +0.0808 | +0.1915 | +0.1915 | 0.0000 | +0.6276 | +0.7445 | 0.865 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.0915 | +0.1892 | +0.1892 | 0.0002 | +0.7145 | +0.7635 | 0.851 |
| `combo_max__max_up_ret__first_bar_sentiment` | Cluster 22 | +1 | +0.0955 | +0.1850 | +0.1847 | 0.0002 | +0.5382 | +0.6807 | 0.923 |
| `max_up_ret` | Cluster 20 | +1 | +0.0773 | +0.1850 | +0.1850 | 0.0002 | +0.4645 | +0.6740 | 0.936 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Cluster 20 | +1 | +0.0807 | +0.1835 | +0.1832 | 0.0002 | +0.4425 | +0.6905 | 0.939 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 10 | +1 | +0.0881 | +0.1812 | +0.1812 | 0.0004 | +0.5050 | +0.6812 | 0.872 |
| `combo_max__bar_ret_0__first_bar_sentiment` | Cluster 16 | +1 | +0.0962 | +0.1804 | +0.1804 | 0.0004 | +0.4409 | +0.6617 | 0.921 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 1 | +1 | +0.0937 | +0.1797 | +0.1800 | 0.0006 | +0.5541 | +0.7368 | 0.907 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 25 | +1 | +0.1013 | +0.1786 | +0.1792 | 0.0006 | +0.4619 | +0.7111 | 0.937 |
| `opening_drive_thrust_ratio` | Cluster 20 | +1 | +0.0933 | +0.1783 | +0.1775 | 0.0006 | +0.5398 | +0.7234 | 0.967 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Cluster 19 | +1 | +0.0918 | +0.1778 | +0.1777 | 0.0006 | +0.4384 | +0.6612 | 0.804 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 5 | +1 | +0.1022 | +0.1776 | +0.1774 | 0.0006 | +0.5254 | +0.7239 | 0.917 |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | Cluster 24 | +1 | +0.0962 | +0.1743 | +0.1744 | 0.0008 | +0.6924 | +0.7342 | 0.948 |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | Cluster 18 | +1 | +0.0892 | +0.1733 | +0.1741 | 0.0008 | +0.7161 | +0.7553 | 0.869 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 14 | +1 | +0.0856 | +0.1702 | +0.1694 | 0.0010 | +0.5890 | +0.7229 | 1.000 |
| `early_order_flow_imbalance` | Cluster 23 | +1 | +0.0652 | +0.1648 | +0.1646 | 0.0012 | +0.6152 | +0.7090 | 0.708 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 0 | +1 | +0.0727 | +0.1643 | +0.1641 | 0.0012 | +0.5736 | +0.6776 | 0.820 |
| `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | Cluster 8 | +1 | +0.0719 | +0.1591 | +0.1593 | 0.0016 | +0.4843 | +0.6864 | 0.639 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 21 | +1 | +0.0609 | +0.1557 | +0.1559 | 0.0022 | +0.4904 | +0.6638 | 0.803 |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | Cluster 17 | +1 | +0.0976 | +0.1512 | +0.1511 | 0.0026 | +0.5730 | +0.7018 | 0.887 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | Cluster 9 | +1 | +0.0523 | +0.1476 | +0.1485 | 0.0036 | +0.5459 | +0.6879 | 0.832 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | Cluster 8 | +1 | +0.0681 | +0.1458 | +0.1458 | 0.0040 | +0.4134 | +0.6638 | 0.791 |
| `combo_rank_min__bar_ret_0__first_bar_sentiment` | Cluster 16 | +1 | +0.0912 | +0.1450 | +0.1456 | 0.0040 | +0.4432 | +0.6674 | 0.935 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Cluster 19 | +1 | +0.0854 | +0.1449 | +0.1449 | 0.0040 | +0.4847 | +0.6848 | 0.930 |
| `always_in_trend_persistence` | Cluster 23 | +1 | +0.0640 | +0.1369 | +0.1365 | 0.0072 | +0.4691 | +0.6900 | 0.906 |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | Cluster 9 | +1 | +0.0817 | +0.1326 | +0.1330 | 0.0098 | +0.4283 | +0.6602 | 0.935 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Cluster 11 | +1 | +0.0405 | +0.1287 | +0.1304 | 0.0110 | +0.5507 | +0.7059 | 0.571 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 5 | +1 | +0.1045 | +0.1276 | +0.1271 | 0.0126 | +0.3689 | +0.6576 | 0.943 |
| `net_volume_flow` | Cluster 7 | +1 | +0.0673 | +0.1211 | +0.1204 | 0.0166 | +0.5337 | +0.6977 | 0.854 |
| `combo_rank_min__volume_weighted_price_position__first_bar_sentiment` | Cluster 17 | +1 | +0.0838 | +0.1196 | +0.1201 | 0.0172 | +0.4045 | +0.6694 | 0.887 |

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
| 300ETF | single | 60 | 28 | 0.2693 | `[4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (28 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 2 | 0.2693 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 300ETF | single | Cluster 1 | 2 | 0.2693 | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 2 | 1 | 0.2693 | `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 3 | 2 | 0.2693 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_mean__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 4 | 1 | 0.2693 | `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 5 | 3 | 0.2693 | `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` |
| 300ETF | single | Cluster 6 | 4 | 0.2693 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 7 | 1 | 0.2693 | `net_volume_flow` | _(none)_ |
| 300ETF | single | Cluster 8 | 2 | 0.2693 | `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` |
| 300ETF | single | Cluster 9 | 2 | 0.2693 | `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | `combo_ratio__first_bar_sentiment__volume_weighted_price_position` |
| 300ETF | single | Cluster 10 | 2 | 0.2693 | `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `combo_min__bar_body_rng_0__limit_down_proximity_early` |
| 300ETF | single | Cluster 11 | 1 | 0.2693 | `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | _(none)_ |
| 300ETF | single | Cluster 12 | 2 | 0.2693 | `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 13 | 1 | 0.2693 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | _(none)_ |
| 300ETF | single | Cluster 14 | 1 | 0.2693 | `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | _(none)_ |
| 300ETF | single | Cluster 15 | 1 | 0.2693 | `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 16 | 4 | 0.2693 | `bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`, `combo_max__bar_ret_0__first_bar_sentiment`, `combo_rank_min__bar_ret_0__first_bar_sentiment` |
| 300ETF | single | Cluster 17 | 3 | 0.2693 | `combo_rank_min__max_up_ret__first_bar_sentiment` | `combo_rank_max__volume_weighted_price_position__first_bar_sentiment`, `combo_rank_min__volume_weighted_price_position__first_bar_sentiment` |
| 300ETF | single | Cluster 18 | 1 | 0.2693 | `combo_sig_product__bar_ret_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 19 | 2 | 0.2693 | `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `combo_rel_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 20 | 4 | 0.2693 | `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `combo_rank_max__max_up_ret__opening_drive_thrust_ratio`, `opening_drive_thrust_ratio`, `max_up_ret` |
| 300ETF | single | Cluster 21 | 2 | 0.2693 | `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 22 | 3 | 0.2693 | `combo_max__max_up_ret__bar_ret_0` | `combo_rank_max__max_up_ret__bar_ret_0`, `combo_max__max_up_ret__first_bar_sentiment` |
| 300ETF | single | Cluster 23 | 2 | 0.2693 | `early_order_flow_imbalance` | `always_in_trend_persistence` |
| 300ETF | single | Cluster 24 | 4 | 0.2693 | `combo_mean__volume_weighted_price_position__bar_body_rng_0` | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`, `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 25 | 2 | 0.2693 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `combo_mean__star50_limit_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 26 | 2 | 0.2693 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` |
| 300ETF | single | Cluster 27 | 3 | 0.2693 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `mean` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | `rank_min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | `mean` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `rank_max` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_max__bar_ret_0__first_bar_sentiment` | `max` | a=`bar_ret_0`, b=`first_bar_sentiment` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | `rank_max` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | `sig_product` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_volume` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | `rank_max` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`smooth_momentum_structure`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_volume` |
| `combo_rank_min__bar_ret_0__first_bar_sentiment` | `rank_min` | a=`bar_ret_0`, b=`first_bar_sentiment` |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | `rel_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | `ratio` | a=`first_bar_sentiment`, b=`volume_weighted_price_position` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_rank_min__volume_weighted_price_position__first_bar_sentiment` | `rank_min` | a=`volume_weighted_price_position`, b=`first_bar_sentiment` |
