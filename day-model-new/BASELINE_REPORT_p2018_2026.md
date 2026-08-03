# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2018_2026`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._
_Note: Cost metrics incorporate 8 bps (0.0008) transaction cost per position state transition (realistic for liquid ETFs). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted | Clusters | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 300ETF | single | 1,286 | 400 | 315 | 238 | 235 | 233 | 229 | 229 | 63 | 62 | 19 | `[9, 9, 7, 7, 5, 3, 3, 2, 2, 2, 2, 2, ... (19 clusters)]` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 62 | 19 | `[9, 9, 7, 7, 5, 3, 3, 2, 2, 2, 2, 2, ... (19 clusters)]` | +0.1114 | [+0.0649, +0.1572] | +0.2466 | [+0.1495, +0.3474] | +0.8909 | 5.55% | 1.6333 | 3.94% | 1.1820 | 2.6252 | 2.80% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 62 | 19 | `[9, 9, 7, 7, 5, 3, 3, 2, 2, 2, 2, 2, ... (19 clusters)]` | -0.1080* | [-0.3571, +0.0826] | -0.0522* | [-0.6305, +0.3141] | -0.6000 | -2.22% | -0.9155 | -3.61% | -1.4692 | -1.7155 | 3.60% |

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
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 3 | +1 | +0.1074 | +0.2637 | +0.2645 | 0.0000 | +0.7047 | +0.7477 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 3 | +1 | +0.1039 | +0.2621 | +0.2635 | 0.0000 | +0.7588 | +0.7724 | 0.865 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 3 | +1 | +0.1034 | +0.2501 | +0.2501 | 0.0000 | +0.8571 | +0.8208 | 0.843 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 3 | +1 | +0.0923 | +0.2353 | +0.2367 | 0.0000 | +0.6402 | +0.7436 | 0.944 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 2 | +1 | +0.0974 | +0.2339 | +0.2337 | 0.0000 | +0.6081 | +0.7415 | 0.892 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 1 | +1 | +0.0944 | +0.2303 | +0.2293 | 0.0000 | +0.8055 | +0.7858 | 0.938 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 4 | +1 | +0.0937 | +0.2301 | +0.2290 | 0.0000 | +0.7485 | +0.7559 | 0.917 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 7 | +1 | +0.1002 | +0.2257 | +0.2261 | 0.0000 | +0.5684 | +0.7127 | 0.850 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 0 | +1 | +0.0851 | +0.2251 | +0.2262 | 0.0000 | +0.7366 | +0.7930 | 0.901 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 11 | +1 | +0.0961 | +0.2233 | +0.2238 | 0.0000 | +0.7261 | +0.7868 | 0.938 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Cluster 18 | +1 | +0.0904 | +0.2228 | +0.2225 | 0.0000 | +0.6862 | +0.7832 | 0.710 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1000 | +0.2224 | +0.2226 | 0.0000 | +0.6458 | +0.7276 | 0.867 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 11 | +1 | +0.0942 | +0.2207 | +0.2205 | 0.0000 | +0.6285 | +0.7188 | 0.927 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.1030 | +0.2194 | +0.2192 | 0.0000 | +0.6144 | +0.7667 | 0.947 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.1033 | +0.2181 | +0.2181 | 0.0000 | +0.6035 | +0.7400 | 0.878 |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_body_rng_0` | Cluster 0 | +1 | +0.0970 | +0.2174 | +0.2174 | 0.0000 | +0.6637 | +0.7667 | 0.938 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 3 | +1 | +0.1018 | +0.2156 | +0.2157 | 0.0000 | +0.5675 | +0.7420 | 0.940 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Cluster 15 | +1 | +0.0876 | +0.2146 | +0.2147 | 0.0000 | +0.5939 | +0.7523 | 0.863 |
| `combo_max__max_up_ret__bar_ret_0` | Cluster 4 | +1 | +0.0911 | +0.2145 | +0.2135 | 0.0000 | +0.7033 | +0.7564 | 0.923 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 11 | +1 | +0.0943 | +0.2144 | +0.2143 | 0.0000 | +0.6681 | +0.7745 | 0.937 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 1 | +1 | +0.0965 | +0.2143 | +0.2137 | 0.0000 | +0.7387 | +0.7734 | 0.793 |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | Cluster 14 | +1 | +0.0817 | +0.2142 | +0.2140 | 0.0000 | +0.8127 | +0.8208 | 0.801 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 0 | +1 | +0.0867 | +0.2138 | +0.2139 | 0.0000 | +0.7377 | +0.7678 | 0.872 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1048 | +0.2135 | +0.2135 | 0.0000 | +0.6151 | +0.7255 | 0.854 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Cluster 3 | +1 | +0.0913 | +0.2116 | +0.2114 | 0.0000 | +0.5574 | +0.7137 | 0.948 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 3 | +1 | +0.0963 | +0.2113 | +0.2119 | 0.0000 | +0.5218 | +0.7147 | 0.918 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Cluster 11 | +1 | +0.0911 | +0.2113 | +0.2111 | 0.0000 | +0.5991 | +0.7271 | 0.942 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Cluster 3 | +1 | +0.1034 | +0.2099 | +0.2098 | 0.0000 | +0.6253 | +0.7384 | 0.928 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 1 | +1 | +0.0882 | +0.2038 | +0.2027 | 0.0000 | +0.9050 | +0.8234 | 0.902 |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | Cluster 11 | +1 | +0.0962 | +0.2017 | +0.2015 | 0.0000 | +0.6739 | +0.7487 | 0.911 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 5 | +1 | +0.0994 | +0.2011 | +0.2014 | 0.0000 | +0.7284 | +0.7770 | 0.926 |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0866 | +0.2001 | +0.2005 | 0.0000 | +0.7275 | +0.7729 | 0.911 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0941 | +0.1986 | +0.1980 | 0.0000 | +0.6913 | +0.7564 | 0.855 |
| `opening_drive_thrust_ratio` | Cluster 15 | +1 | +0.0982 | +0.1983 | +0.1985 | 0.0000 | +0.6753 | +0.7580 | 0.928 |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | Cluster 0 | +1 | +0.0936 | +0.1979 | +0.1979 | 0.0000 | +0.5846 | +0.7194 | 0.899 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 2 | +1 | +0.0937 | +0.1968 | +0.1971 | 0.0000 | +0.6028 | +0.7188 | 0.799 |
| `first_bar_return` | Cluster 0 | +1 | +0.0868 | +0.1961 | +0.1962 | 0.0000 | +0.7296 | +0.7945 | 0.942 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 2 | +1 | +0.0918 | +0.1943 | +0.1946 | 0.0000 | +0.5187 | +0.6849 | 0.804 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | Cluster 13 | +1 | +0.0713 | +0.1930 | +0.1922 | 0.0000 | +0.5977 | +0.7173 | 0.856 |
| `combo_rank_min__max_up_ret__bar_ret_0` | Cluster 0 | +1 | +0.0802 | +0.1919 | +0.1927 | 0.0000 | +0.5219 | +0.7271 | 0.949 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Cluster 9 | +1 | +0.0941 | +0.1910 | +0.1908 | 0.0002 | +0.7407 | +0.7312 | 0.926 |
| `combo_max__first_bar_return__first_bar_sentiment` | Cluster 0 | +1 | +0.0874 | +0.1903 | +0.1903 | 0.0002 | +0.6211 | +0.7533 | 0.916 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 2 | +1 | +0.0958 | +0.1891 | +0.1890 | 0.0002 | +0.5914 | +0.7199 | 0.950 |
| `combo_min__max_up_ret__first_bar_sentiment` | Cluster 0 | +1 | +0.0894 | +0.1875 | +0.1880 | 0.0004 | +0.5795 | +0.7209 | 0.922 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 2 | +1 | +0.0937 | +0.1844 | +0.1844 | 0.0004 | +0.4872 | +0.6859 | 0.862 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Cluster 9 | +1 | +0.0934 | +0.1838 | +0.1840 | 0.0004 | +0.6484 | +0.7405 | 0.858 |
| `combo_min__first_bar_return__opening_drive_thrust_ratio` | Cluster 7 | +1 | +0.0970 | +0.1819 | +0.1822 | 0.0004 | +0.7164 | +0.7863 | 0.939 |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | Cluster 11 | +1 | +0.0771 | +0.1817 | +0.1814 | 0.0004 | +0.6709 | +0.7338 | 0.720 |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | Cluster 16 | +1 | +0.1053 | +0.1814 | +0.1819 | 0.0004 | +0.4878 | +0.6612 | 0.792 |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | Cluster 11 | +1 | +0.0756 | +0.1781 | +0.1776 | 0.0008 | +0.6856 | +0.7693 | 0.999 |
| `volume_weighted_price_position` | Cluster 16 | +1 | +0.0854 | +0.1779 | +0.1774 | 0.0008 | +0.6715 | +0.7662 | 0.899 |
| `combo_sig_product__max_up_ret__first_bar_return` | Cluster 14 | +1 | +0.0713 | +0.1653 | +0.1649 | 0.0010 | +0.5202 | +0.6838 | 0.830 |
| `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Cluster 3 | +1 | +0.0809 | +0.1651 | +0.1639 | 0.0010 | +0.4599 | +0.6977 | 0.854 |
| `morning_volume_weighted_momentum` | Cluster 12 | +1 | +0.0747 | +0.1634 | +0.1619 | 0.0014 | +0.5607 | +0.7111 | 0.764 |
| `always_in_trend_persistence` | Cluster 10 | +1 | +0.0613 | +0.1511 | +0.1496 | 0.0034 | +0.5015 | +0.6998 | 0.895 |
| `early_order_flow_imbalance` | Cluster 12 | +1 | +0.0707 | +0.1502 | +0.1488 | 0.0034 | +0.4906 | +0.6637 | 0.728 |
| `volume_surge_direction` | Cluster 17 | +1 | +0.0779 | +0.1445 | +0.1453 | 0.0050 | +0.5515 | +0.6668 | 0.842 |
| `combo_min__first_bar_return__first_bar_sentiment` | Cluster 0 | +1 | +0.0804 | +0.1429 | +0.1430 | 0.0054 | +0.5066 | +0.7008 | 0.933 |
| `net_volume_flow` | Cluster 12 | +1 | +0.0774 | +0.1397 | +0.1394 | 0.0060 | +0.4492 | +0.6591 | 0.879 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.0852 | +0.1334 | +0.1332 | 0.0076 | +0.4460 | +0.6874 | 0.884 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 5 | +1 | +0.0951 | +0.1299 | +0.1306 | 0.0094 | +0.4720 | +0.6782 | 0.947 |
| `combo_ratio__max_up_ret__first_bar_volume` | Cluster 15 | +1 | +0.0832 | +0.1121 | +0.1122 | 0.0220 | +0.4973 | +0.6807 | 0.779 |


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

### Cluster Overview per ETF / Side

| ETF | Side | Total Features | Clusters | Avg Silhouette | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 300ETF | single | 62 | 19 | 0.2513 | `[9, 9, 7, 7, 5, 3, 3, 2, 2, 2, 2, 2, ... (19 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 9 | 0.2513 | `combo_rank_max__bar_ret_0__bar_body_rng_0` | `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_min__max_up_ret__first_bar_sentiment`, `combo_tri_mean__max_up_ret__first_bar_return__bar_body_rng_0`, `first_bar_return`, `combo_max__first_bar_return__first_bar_sentiment`, `combo_rank_min__max_up_ret__bar_ret_0`, `combo_min__first_bar_return__first_bar_sentiment` |
| 300ETF | single | Cluster 1 | 5 | 0.2513 | `combo_mean__max_up_ret__volume_weighted_price_position` | `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`, `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position`, `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 2 | 7 | 0.2513 | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 3 | 9 | 0.2513 | `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_min__bar_body_rng_0__limit_down_proximity_early`, `combo_mean__bar_body_rng_0__limit_down_proximity_early`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`, `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` |
| 300ETF | single | Cluster 4 | 2 | 0.2513 | `combo_max__max_up_ret__bar_ret_0` | `combo_rank_max__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 5 | 2 | 0.2513 | `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` |
| 300ETF | single | Cluster 6 | 2 | 0.2513 | `combo_max__first_bar_return__opening_drive_thrust_ratio` | `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 7 | 2 | 0.2513 | `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_min__first_bar_return__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 8 | 1 | 0.2513 | `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 9 | 2 | 0.2513 | `combo_mean__max_up_ret__first_bar_sentiment` | `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` |
| 300ETF | single | Cluster 10 | 1 | 0.2513 | `always_in_trend_persistence` | _(none)_ |
| 300ETF | single | Cluster 11 | 7 | 0.2513 | `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | `combo_mean__volume_weighted_price_position__bar_body_rng_0`, `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`, `combo_rank_max__bar_ret_0__volume_weighted_price_position`, `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0`, `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`, `combo_sig_product__bar_ret_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 12 | 3 | 0.2513 | `morning_volume_weighted_momentum` | `early_order_flow_imbalance`, `net_volume_flow` |
| 300ETF | single | Cluster 13 | 1 | 0.2513 | `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 14 | 2 | 0.2513 | `combo_sig_product__max_up_ret__volume_weighted_price_position` | `combo_sig_product__max_up_ret__first_bar_return` |
| 300ETF | single | Cluster 15 | 3 | 0.2513 | `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `opening_drive_thrust_ratio`, `combo_ratio__max_up_ret__first_bar_volume` |
| 300ETF | single | Cluster 16 | 2 | 0.2513 | `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | `volume_weighted_price_position` |
| 300ETF | single | Cluster 17 | 1 | 0.2513 | `volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 18 | 1 | 0.2513 | `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | _(none)_ |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | `min` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | `rank_max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | `max` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`max_up_ret`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | `rank_max` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | `rank_max` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | `mean` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | `mean` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | `sig_product` | a=`bar_body_rng_0`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | `rank_max` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | `tri_median` | a=`smooth_momentum_structure`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_rank_min__max_up_ret__bar_ret_0` | `rank_min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_max__first_bar_return__first_bar_sentiment` | `max` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__first_bar_sentiment` | `mean` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__first_bar_return__opening_drive_thrust_ratio` | `min` | a=`first_bar_return`, b=`opening_drive_thrust_ratio` |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | `tri_median` | a=`smooth_momentum_structure`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | `sig_product` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | `sig_product` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_sig_product__max_up_ret__first_bar_return` | `sig_product` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | `tri_max` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_min__first_bar_return__first_bar_sentiment` | `min` | a=`first_bar_return`, b=`first_bar_sentiment` |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_ratio__max_up_ret__first_bar_volume` | `ratio` | a=`max_up_ret`, b=`first_bar_volume` |
