# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `(none)`

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

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1,572 | 533 | 293 | 169 | 167 | 110 | 110 | 110 | 44 | 41 |
| 50ETF | single | 1,244 | 514 | 437 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,092 | 1,602 | 1,292 | 1,037 | 1,026 | 776 | 770 | 770 | 248 | 193 |
| 588000ETF | single | 1,586 | 1,019 | 694 | 540 | 502 | 32 | 32 | 32 | 11 | 8 |
| 159915ETF | single | 1,889 | 761 | 379 | 338 | 333 | 65 | 65 | 65 | 29 | 27 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 41 | +0.1381 | [+0.0921, +0.1827] | +0.2362 | [+0.1066, +0.3454] | +0.8061 | 6.58% | 1.5204 | 4.95% | 1.1605 | 2.2821 | 5.27% |
| 500ETF | single | 193 | +0.2067 | [+0.1609, +0.2548] | +0.2974 | [+0.2060, +0.3934] | +0.9515 | 8.86% | 1.8349 | 7.25% | 1.5174 | 2.8209 | 4.17% |
| 588000ETF | single | 8 | +0.1340 | [+0.0694, +0.1933] | +0.3536 | [+0.2106, +0.4477] | +0.8061 | 7.82% | 2.2008 | 6.38% | 1.8279 | 3.7105 | 2.01% |
| 159915ETF | single | 27 | +0.1714 | [+0.1257, +0.2160] | +0.2606 | [+0.1712, +0.3505] | +0.9152 | 8.51% | 1.4610 | 6.93% | 1.1981 | 1.8163 | 8.80% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 41 | +0.0725 | [+0.0041, +0.1382] | +0.1923 | [+0.0425, +0.3308] | +0.8061 | 4.33% | 1.2006 | 2.72% | 0.7645 | 1.5139 | 2.98% |
| 500ETF | single | 193 | +0.1102 | [+0.0513, +0.1695] | +0.1384 | [+0.0037, +0.2497] | +0.8182 | 4.36% | 1.0121 | 2.91% | 0.6814 | 1.2768 | 3.69% |
| 588000ETF | single | 8 | +0.0059* | [-0.0930, +0.0830] | -0.1255* | [-0.3423, +0.1175] | +0.4788 | -1.94% | -0.3988 | -3.41% | -0.6974 | -0.9470 | 8.84% |
| 159915ETF | single | 27 | +0.1378 | [+0.0680, +0.1937] | +0.2609 | [+0.1055, +0.3928] | +0.7939 | 9.68% | 1.5838 | 8.31% | 1.3762 | 3.6955 | 5.31% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 41 | +0.0249* | [-0.0696, +0.1187] | +0.1069* | [-0.1424, +0.2943] | +0.6727 | 3.51% | 0.8398 | 1.92% | 0.4642 | 0.9927 | 4.35% |
| 500ETF | single | 193 | +0.1141 | [+0.0299, +0.1923] | +0.0256* | [-0.1533, +0.1866] | +0.9152 | 3.39% | 0.8004 | 1.95% | 0.4629 | 0.8827 | 3.92% |
| 588000ETF | single | 8 | -0.0125* | [-0.1129, +0.1013] | -0.1301* | [-0.3634, +0.1942] | +0.1152 | -1.88% | -0.3639 | -3.33% | -0.6403 | -0.8778 | 8.44% |
| 159915ETF | single | 27 | +0.1449 | [+0.0485, +0.2303] | +0.2666 | [+0.0391, +0.4716] | +0.6606 | 12.47% | 1.6124 | 11.09% | 1.4489 | 4.2571 | 6.46% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 9 | +1 | +0.1299 | +0.2949 | +0.2950 | 0.0000 | +0.7632 | +0.7279 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1365 | +0.2874 | +0.2868 | 0.0000 | +0.8181 | +0.8088 | 0.858 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 9 | +1 | +0.1313 | +0.2713 | +0.2711 | 0.0000 | +0.7429 | +0.7560 | 0.944 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 3 | +1 | +0.1267 | +0.2690 | +0.2689 | 0.0000 | +0.5307 | +0.6968 | 0.907 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1222 | +0.2667 | +0.2669 | 0.0000 | +0.6787 | +0.7103 | 0.863 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1275 | +0.2662 | +0.2660 | 0.0000 | +0.8452 | +0.8094 | 0.875 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 2 | +1 | +0.1164 | +0.2660 | +0.2658 | 0.0000 | +0.6109 | +0.7003 | 0.816 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.1277 | +0.2603 | +0.2593 | 0.0000 | +0.6140 | +0.7067 | 0.854 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 6 | +1 | +0.1053 | +0.2522 | +0.2513 | 0.0000 | +0.6153 | +0.7138 | 0.825 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 9 | +1 | +0.1206 | +0.2394 | +0.2393 | 0.0000 | +0.5672 | +0.6833 | 0.927 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 9 | +1 | +0.1260 | +0.2361 | +0.2360 | 0.0000 | +0.4976 | +0.6897 | 1.000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 0 | +1 | +0.1203 | +0.2354 | +0.2346 | 0.0000 | +0.7231 | +0.7683 | 0.895 |
| `rbreaker_sell_setup_proximity_early` | Cluster 11 | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.824 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 6 | +1 | +0.0976 | +0.2285 | +0.2280 | 0.0000 | +0.5377 | +0.6516 | 0.941 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 4 | +1 | +0.1274 | +0.2257 | +0.2252 | 0.0000 | +0.5875 | +0.7255 | 0.918 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 7 | +1 | +0.0829 | +0.2240 | +0.2229 | 0.0000 | +0.8024 | +0.7894 | 0.779 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1282 | +0.2194 | +0.2197 | 0.0000 | +0.5702 | +0.7255 | 0.938 |
| `combo_z_sum__max_up_ret__opening_drive_thrust_ratio` | Cluster 10 | +1 | +0.0947 | +0.2145 | +0.2131 | 0.0000 | +0.6910 | +0.7531 | 0.856 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 7 | +1 | +0.0883 | +0.2124 | +0.2111 | 0.0000 | +0.6660 | +0.7396 | 0.922 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1140 | +0.2121 | +0.2118 | 0.0000 | +0.6539 | +0.7132 | 0.935 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1200 | +0.2119 | +0.2110 | 0.0000 | +0.6448 | +0.7044 | 0.931 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Cluster 13 | +1 | +0.0874 | +0.2066 | +0.2055 | 0.0000 | +0.6472 | +0.7232 | 0.806 |
| `combo_min__max_up_ret__volume_weighted_price_position` | Cluster 7 | +1 | +0.0900 | +0.2051 | +0.2042 | 0.0000 | +0.5549 | +0.6933 | 0.899 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Cluster 13 | +1 | +0.0924 | +0.1981 | +0.1972 | 0.0000 | +0.5933 | +0.7091 | 0.925 |
| `combo_mean__bar_ret_0__volume_weighted_price_position` | Cluster 13 | +1 | +0.0899 | +0.1969 | +0.1956 | 0.0000 | +0.5084 | +0.6862 | 1.000 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 12 | +1 | +0.0999 | +0.1898 | +0.1897 | 0.0000 | +0.6533 | +0.7496 | 0.843 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 7 | +1 | +0.0777 | +0.1863 | +0.1849 | 0.0004 | +0.7183 | +0.7760 | 0.885 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 9 | +1 | +0.0959 | +0.1836 | +0.1831 | 0.0004 | +0.4816 | +0.6716 | 0.876 |
| `combo_max__first_bar_return__bar_body_rng_0` | Cluster 12 | +1 | +0.1002 | +0.1830 | +0.1824 | 0.0006 | +0.5123 | +0.7050 | 0.900 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 5 | +1 | +0.0944 | +0.1816 | +0.1804 | 0.0006 | +0.6499 | +0.7284 | 0.823 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 10 | +1 | +0.0888 | +0.1816 | +0.1799 | 0.0006 | +0.6717 | +0.7566 | 0.861 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 6 | +1 | +0.1045 | +0.1747 | +0.1741 | 0.0016 | +0.4368 | +0.6563 | 0.921 |
| `combo_z_sum__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.1057 | +0.1746 | +0.1733 | 0.0016 | +0.6235 | +0.7185 | 1.000 |
| `star50_limit_proximity_early` | Cluster 11 | +1 | +0.0880 | +0.1745 | +0.1743 | 0.0016 | +0.4855 | +0.7050 | 0.942 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 12 | +1 | +0.1014 | +0.1624 | +0.1615 | 0.0024 | +0.4599 | +0.6522 | 0.878 |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | Cluster 14 | +1 | +0.0839 | +0.1600 | +0.1586 | 0.0026 | +0.4471 | +0.6680 | 0.836 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Cluster 16 | +1 | +0.0993 | +0.1570 | +0.1561 | 0.0036 | +0.5103 | +0.6786 | 0.785 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 8 | +1 | +0.0720 | +0.1466 | +0.1457 | 0.0058 | +0.5884 | +0.7349 | 0.733 |
| `combo_max__bar_body_rng_0__volume_surge_direction` | Cluster 12 | +1 | +0.0889 | +0.1408 | +0.1400 | 0.0070 | +0.5001 | +0.6680 | 0.860 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Cluster 16 | +1 | +0.0988 | +0.1327 | +0.1318 | 0.0114 | +0.5558 | +0.7120 | 0.946 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Cluster 15 | +1 | +0.0702 | +0.1277 | +0.1278 | 0.0154 | +0.6295 | +0.7455 | 0.064 |

### 50ETF / single
No features admitted.

### 500ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 16 | +1 | +0.1956 | +0.3331 | +0.3327 | 0.0000 | +1.0031 | +0.8235 | 0.980 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 18 | +1 | +0.1926 | +0.3310 | +0.3310 | 0.0000 | +0.8368 | +0.7941 | 0.850 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 16 | +1 | +0.1956 | +0.3306 | +0.3300 | 0.0000 | +1.1154 | +0.8352 | 0.873 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1864 | +0.3278 | +0.3273 | 0.0000 | +0.7514 | +0.7625 | 0.723 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 41 | +1 | +0.1948 | +0.3226 | +0.3228 | 0.0000 | +0.9807 | +0.8264 | 0.837 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 14 | +1 | +0.1688 | +0.3197 | +0.3192 | 0.0000 | +0.9257 | +0.7988 | 0.949 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1896 | +0.3190 | +0.3187 | 0.0000 | +0.8073 | +0.7806 | 0.906 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 36 | +1 | +0.2028 | +0.3177 | +0.3175 | 0.0000 | +0.8965 | +0.7965 | 0.771 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 34 | +1 | +0.2024 | +0.3136 | +0.3128 | 0.0000 | +0.9057 | +0.8399 | 0.857 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 17 | +1 | +0.1881 | +0.3068 | +0.3067 | 0.0000 | +0.6128 | +0.7326 | 0.797 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 34 | +1 | +0.2156 | +0.3040 | +0.3040 | 0.0000 | +1.0319 | +0.8381 | 0.926 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 18 | +1 | +0.1871 | +0.3032 | +0.3033 | 0.0000 | +0.8367 | +0.7630 | 0.870 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 29 | +1 | +0.1819 | +0.2983 | +0.2980 | 0.0000 | +1.0424 | +0.8510 | 0.966 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 36 | +1 | +0.1605 | +0.2977 | +0.2979 | 0.0000 | +0.7506 | +0.7806 | 0.770 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 17 | +1 | +0.1855 | +0.2950 | +0.2950 | 0.0000 | +0.6047 | +0.6950 | 0.959 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 10 | +1 | +0.1685 | +0.2940 | +0.2932 | 0.0000 | +0.7752 | +0.7988 | 0.959 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 36 | +1 | +0.1712 | +0.2915 | +0.2911 | 0.0000 | +0.6571 | +0.7413 | 0.893 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Cluster 11 | +1 | +0.1800 | +0.2907 | +0.2900 | 0.0000 | +0.8748 | +0.7959 | 0.831 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 19 | +1 | +0.1597 | +0.2905 | +0.2900 | 0.0000 | +0.8567 | +0.7865 | 0.950 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 31 | +1 | +0.1755 | +0.2901 | +0.2895 | 0.0000 | +0.9650 | +0.8323 | 0.878 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Cluster 36 | +1 | +0.1911 | +0.2897 | +0.2894 | 0.0000 | +0.8054 | +0.7818 | 0.968 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 15 | +1 | +0.1667 | +0.2881 | +0.2877 | 0.0000 | +0.8854 | +0.8135 | 0.975 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 8 | +1 | +0.1887 | +0.2871 | +0.2867 | 0.0000 | +0.7018 | +0.7226 | 0.939 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Cluster 10 | +1 | +0.1303 | +0.2869 | +0.2863 | 0.0000 | +0.7326 | +0.7754 | 0.873 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Cluster 31 | +1 | +0.1736 | +0.2868 | +0.2858 | 0.0000 | +0.9687 | +0.8276 | 0.901 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Cluster 1 | +1 | +0.1585 | +0.2868 | +0.2865 | 0.0000 | +0.5707 | +0.6669 | 0.942 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Cluster 27 | +1 | +0.1738 | +0.2867 | +0.2865 | 0.0000 | +0.8769 | +0.7877 | 0.890 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 10 | +1 | +0.1758 | +0.2853 | +0.2845 | 0.0000 | +0.7706 | +0.7848 | 0.915 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 19 | +1 | +0.1533 | +0.2848 | +0.2842 | 0.0000 | +0.8479 | +0.7877 | 0.960 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Cluster 21 | +1 | +0.1395 | +0.2846 | +0.2837 | 0.0000 | +0.7432 | +0.7455 | 0.915 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Cluster 0 | +1 | +0.1500 | +0.2835 | +0.2832 | 0.0000 | +0.8380 | +0.7607 | 0.652 |
| `rbreaker_sell_setup_proximity_early` | Cluster 7 | +1 | +0.1618 | +0.2832 | +0.2831 | 0.0000 | +0.6705 | +0.7337 | 0.870 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Cluster 11 | +1 | +0.1560 | +0.2819 | +0.2805 | 0.0000 | +0.7803 | +0.7760 | 0.810 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 21 | +1 | +0.1285 | +0.2808 | +0.2797 | 0.0000 | +0.5617 | +0.7026 | 0.937 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 24 | +1 | +0.1784 | +0.2798 | +0.2791 | 0.0000 | +1.0795 | +0.8651 | 0.925 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 10 | +1 | +0.1847 | +0.2792 | +0.2789 | 0.0000 | +0.8739 | +0.7865 | 0.985 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 21 | +1 | +0.1300 | +0.2789 | +0.2783 | 0.0000 | +0.6204 | +0.7126 | 0.947 |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Cluster 20 | +1 | +0.1186 | +0.2777 | +0.2764 | 0.0000 | +0.7105 | +0.7513 | 0.932 |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1594 | +0.2776 | +0.2768 | 0.0000 | +0.8565 | +0.8018 | 0.953 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 10 | +1 | +0.1629 | +0.2769 | +0.2760 | 0.0000 | +0.8756 | +0.8399 | 0.919 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | Cluster 36 | +1 | +0.1953 | +0.2768 | +0.2765 | 0.0000 | +1.0438 | +0.8299 | 0.923 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Cluster 11 | +1 | +0.1790 | +0.2759 | +0.2752 | 0.0000 | +0.8669 | +0.8029 | 0.994 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Cluster 35 | +1 | +0.1830 | +0.2756 | +0.2750 | 0.0000 | +0.9042 | +0.7935 | 0.985 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Cluster 36 | +1 | +0.1889 | +0.2752 | +0.2746 | 0.0000 | +0.9765 | +0.7777 | 0.896 |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | Cluster 11 | +1 | +0.1360 | +0.2742 | +0.2735 | 0.0000 | +0.7025 | +0.7566 | 0.861 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 40 | +1 | +0.1934 | +0.2734 | +0.2732 | 0.0000 | +0.8351 | +0.7707 | 0.966 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 36 | +1 | +0.1757 | +0.2728 | +0.2724 | 0.0000 | +0.6779 | +0.7425 | 0.934 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Cluster 21 | +1 | +0.1280 | +0.2726 | +0.2717 | 0.0000 | +0.5962 | +0.6886 | 0.946 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 30 | +1 | +0.1702 | +0.2721 | +0.2709 | 0.0000 | +0.8193 | +0.7912 | 0.814 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Cluster 37 | +1 | +0.1788 | +0.2708 | +0.2703 | 0.0000 | +0.6957 | +0.7771 | 0.915 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 14 | +1 | +0.1926 | +0.2694 | +0.2690 | 0.0000 | +0.7558 | +0.7449 | 0.967 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 30 | +1 | +0.1624 | +0.2692 | +0.2684 | 0.0000 | +0.8072 | +0.7965 | 0.936 |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 10 | +1 | +0.1219 | +0.2682 | +0.2675 | 0.0000 | +0.7453 | +0.7642 | 0.932 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 36 | +1 | +0.2016 | +0.2676 | +0.2674 | 0.0000 | +0.9507 | +0.8082 | 0.949 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | Cluster 38 | +1 | +0.1452 | +0.2674 | +0.2672 | 0.0000 | +0.7101 | +0.7566 | 0.779 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Cluster 36 | +1 | +0.1915 | +0.2673 | +0.2666 | 0.0000 | +1.0490 | +0.8047 | 0.929 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Cluster 2 | +1 | +0.1640 | +0.2669 | +0.2662 | 0.0000 | +0.6667 | +0.7331 | 0.788 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Cluster 4 | +1 | +0.1499 | +0.2642 | +0.2624 | 0.0000 | +0.9245 | +0.8188 | 0.238 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | Cluster 45 | +1 | +0.0827 | +0.2636 | +0.2642 | 0.0000 | +0.6985 | +0.7478 | 0.437 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 39 | +1 | +0.1894 | +0.2634 | +0.2630 | 0.0000 | +0.6383 | +0.7114 | 0.866 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Cluster 1 | +1 | +0.1338 | +0.2631 | +0.2626 | 0.0000 | +0.8252 | +0.7736 | 0.870 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | Cluster 2 | +1 | +0.1679 | +0.2618 | +0.2614 | 0.0000 | +0.7281 | +0.7636 | 0.900 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | Cluster 30 | +1 | +0.1630 | +0.2602 | +0.2591 | 0.0000 | +0.9227 | +0.8188 | 0.985 |
| `combo_mean__max_up_ret__trend_bar_close_consistency` | Cluster 10 | +1 | +0.1328 | +0.2597 | +0.2588 | 0.0000 | +0.7998 | +0.7736 | 0.921 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Cluster 29 | +1 | +0.1575 | +0.2596 | +0.2590 | 0.0000 | +0.7756 | +0.7660 | 0.945 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | Cluster 22 | +1 | +0.1549 | +0.2596 | +0.2589 | 0.0000 | +0.7743 | +0.7484 | 0.944 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Cluster 22 | +1 | +0.1476 | +0.2595 | +0.2588 | 0.0000 | +0.7485 | +0.7507 | 0.889 |
| `combo_diff__max_up_ret__body_size_progression` | Cluster 36 | +1 | +0.1908 | +0.2593 | +0.2590 | 0.0000 | +0.9312 | +0.7830 | 0.973 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Cluster 1 | +1 | +0.1312 | +0.2591 | +0.2586 | 0.0000 | +0.7790 | +0.7619 | 0.797 |
| `opening_drive_thrust_ratio` | Cluster 32 | +1 | +0.1796 | +0.2584 | +0.2578 | 0.0000 | +0.7576 | +0.8000 | 0.931 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 24 | +1 | +0.1893 | +0.2581 | +0.2574 | 0.0000 | +0.6916 | +0.7683 | 0.911 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1583 | +0.2552 | +0.2542 | 0.0000 | +0.7886 | +0.7695 | 0.755 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 26 | +1 | +0.1721 | +0.2550 | +0.2539 | 0.0000 | +0.6969 | +0.7701 | 0.838 |
| `combo_max__max_up_ret__early_body_momentum` | Cluster 10 | +1 | +0.1472 | +0.2549 | +0.2541 | 0.0000 | +0.9093 | +0.8047 | 0.946 |
| `combo_min__max_up_ret__close_vs_open_range` | Cluster 10 | +1 | +0.1327 | +0.2543 | +0.2535 | 0.0000 | +0.7631 | +0.8012 | 0.880 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 27 | +1 | +0.1772 | +0.2535 | +0.2526 | 0.0000 | +0.7390 | +0.7660 | 0.931 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Cluster 27 | +1 | +0.1773 | +0.2531 | +0.2529 | 0.0000 | +0.8527 | +0.7566 | 0.897 |
| `max_up_ret` | Cluster 37 | +1 | +0.1709 | +0.2500 | +0.2496 | 0.0000 | +0.7454 | +0.7789 | 0.898 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 28 | +1 | +0.1456 | +0.2493 | +0.2494 | 0.0000 | +0.7628 | +0.7718 | 0.850 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Cluster 28 | +1 | +0.1466 | +0.2488 | +0.2487 | 0.0000 | +0.7057 | +0.7519 | 0.873 |
| `combo_mean__max_up_ret__close_vs_open_range` | Cluster 10 | +1 | +0.1558 | +0.2481 | +0.2472 | 0.0000 | +0.8829 | +0.8006 | 0.909 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 24 | +1 | +0.1863 | +0.2480 | +0.2473 | 0.0000 | +0.7885 | +0.7648 | 0.912 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 0 | +1 | +0.1433 | +0.2470 | +0.2471 | 0.0000 | +0.6194 | +0.7214 | 0.929 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Cluster 0 | +1 | +0.1592 | +0.2469 | +0.2464 | 0.0000 | +0.5667 | +0.7138 | 0.964 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 23 | +1 | +0.1672 | +0.2468 | +0.2465 | 0.0000 | +0.6416 | +0.7021 | 0.959 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Cluster 11 | +1 | +0.1710 | +0.2453 | +0.2445 | 0.0000 | +0.6363 | +0.7015 | 0.848 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Cluster 10 | +1 | +0.1134 | +0.2443 | +0.2433 | 0.0000 | +0.6521 | +0.7437 | 0.964 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Cluster 10 | +1 | +0.1535 | +0.2441 | +0.2432 | 0.0000 | +0.9327 | +0.8006 | 0.978 |
| `combo_max__max_up_ret__close_vs_open_range` | Cluster 10 | +1 | +0.1670 | +0.2438 | +0.2430 | 0.0000 | +0.8274 | +0.7519 | 0.936 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Cluster 0 | +1 | +0.1624 | +0.2431 | +0.2424 | 0.0000 | +0.8882 | +0.7912 | 0.806 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Cluster 30 | +1 | +0.1458 | +0.2427 | +0.2424 | 0.0000 | +0.7458 | +0.7894 | 0.927 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | Cluster 2 | +1 | +0.1677 | +0.2426 | +0.2421 | 0.0000 | +0.6339 | +0.7191 | 0.938 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Cluster 37 | +1 | +0.1286 | +0.2418 | +0.2411 | 0.0000 | +0.7757 | +0.7672 | 0.991 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Cluster 37 | +1 | +0.1109 | +0.2408 | +0.2402 | 0.0000 | +0.5954 | +0.6897 | 0.946 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | Cluster 45 | +1 | +0.0687 | +0.2407 | +0.2417 | 0.0000 | +0.6395 | +0.7067 | 0.926 |
| `combo_min__max_up_ret__high_low_sequence_momentum` | Cluster 10 | +1 | +0.1305 | +0.2400 | +0.2388 | 0.0000 | +0.7500 | +0.7666 | 0.999 |
| `combo_min__close_vs_open_range__high_low_sequence_momentum` | Cluster 10 | +1 | +0.1117 | +0.2399 | +0.2387 | 0.0000 | +0.5760 | +0.7132 | 0.999 |
| `combo_min__close_vs_open_range__bar_ret_0` | Cluster 37 | +1 | +0.1290 | +0.2398 | +0.2389 | 0.0000 | +0.7122 | +0.7367 | 0.813 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 25 | +1 | +0.1713 | +0.2386 | +0.2377 | 0.0000 | +0.7053 | +0.7449 | 0.909 |
| `combo_mean__max_up_ret__first_bar_return` | Cluster 37 | +1 | +0.1817 | +0.2383 | +0.2376 | 0.0000 | +0.6903 | +0.7367 | 0.883 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Cluster 36 | +1 | +0.1692 | +0.2377 | +0.2372 | 0.0000 | +0.6377 | +0.7308 | 0.941 |
| `combo_min__net_volume_flow__bar_ret_0` | Cluster 37 | +1 | +0.1338 | +0.2366 | +0.2356 | 0.0000 | +0.6949 | +0.7501 | 1.000 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Cluster 10 | +1 | +0.1670 | +0.2359 | +0.2353 | 0.0000 | +0.8403 | +0.7689 | 0.946 |
| `net_volume_flow` | Cluster 10 | +1 | +0.1203 | +0.2354 | +0.2345 | 0.0000 | +0.6801 | +0.7572 | 0.950 |
| `combo_rank_min__max_up_ret__bar_ret_0` | Cluster 37 | +1 | +0.1723 | +0.2350 | +0.2347 | 0.0000 | +0.5758 | +0.7062 | 0.934 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | Cluster 27 | +1 | +0.1912 | +0.2348 | +0.2342 | 0.0000 | +0.6995 | +0.7314 | 1.000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Cluster 10 | +1 | +0.1643 | +0.2343 | +0.2332 | 0.0000 | +0.8108 | +0.7906 | 0.940 |
| `combo_mean__volatility_expansion_trend_vector__close_vs_open_range` | Cluster 10 | +1 | +0.1172 | +0.2342 | +0.2333 | 0.0000 | +0.5249 | +0.7167 | 0.977 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Cluster 0 | +1 | +0.1505 | +0.2335 | +0.2332 | 0.0000 | +0.5531 | +0.6833 | 0.918 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Cluster 11 | +1 | +0.1593 | +0.2335 | +0.2326 | 0.0000 | +0.7104 | +0.7402 | 0.838 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 26 | +1 | +0.1871 | +0.2325 | +0.2313 | 0.0000 | +0.7171 | +0.7683 | 0.915 |
| `combo_max__max_up_ret__first_bar_return` | Cluster 37 | +1 | +0.1761 | +0.2307 | +0.2300 | 0.0000 | +0.7780 | +0.7666 | 1.000 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Cluster 25 | +1 | +0.1680 | +0.2305 | +0.2301 | 0.0000 | +0.5623 | +0.7578 | 0.947 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Cluster 13 | +1 | +0.1385 | +0.2305 | +0.2298 | 0.0000 | +0.5846 | +0.7032 | 0.934 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 39 | +1 | +0.1828 | +0.2298 | +0.2291 | 0.0000 | +0.5203 | +0.7208 | 0.943 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 37 | +1 | +0.1751 | +0.2284 | +0.2276 | 0.0000 | +0.8251 | +0.7801 | 0.871 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 44 | +1 | +0.1431 | +0.2252 | +0.2249 | 0.0002 | +0.4900 | +0.6739 | 0.807 |
| `star50_limit_proximity_early` | Cluster 6 | +1 | +0.1323 | +0.2250 | +0.2247 | 0.0002 | +0.6124 | +0.7132 | 0.917 |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 45 | +1 | +0.1001 | +0.2248 | +0.2252 | 0.0002 | +0.6393 | +0.7067 | 0.676 |
| `combo_mean__net_volume_flow__bar_ret_0` | Cluster 37 | +1 | +0.1522 | +0.2246 | +0.2240 | 0.0002 | +0.5543 | +0.7097 | 0.973 |
| `combo_ratio__max_down_ret__net_volume_flow` | Cluster 3 | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0002 | +0.8478 | +0.7883 | 0.095 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Cluster 37 | +1 | +0.1442 | +0.2239 | +0.2233 | 0.0002 | +0.6815 | +0.7560 | 0.886 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Cluster 39 | +1 | +0.1834 | +0.2231 | +0.2228 | 0.0002 | +0.5385 | +0.6569 | 0.896 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Cluster 11 | +1 | +0.1601 | +0.2217 | +0.2206 | 0.0002 | +0.8729 | +0.7959 | 0.929 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | Cluster 37 | +1 | +0.1425 | +0.2212 | +0.2205 | 0.0004 | +0.5742 | +0.7150 | 0.909 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | Cluster 10 | +1 | +0.1122 | +0.2210 | +0.2199 | 0.0004 | +0.5904 | +0.7255 | 0.912 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | Cluster 37 | +1 | +0.1297 | +0.2207 | +0.2199 | 0.0004 | +0.5614 | +0.7537 | 0.987 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | Cluster 11 | +1 | +0.1294 | +0.2204 | +0.2200 | 0.0004 | +0.3998 | +0.6592 | 0.969 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 44 | +1 | +0.1337 | +0.2202 | +0.2199 | 0.0004 | +0.4781 | +0.6710 | 0.884 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 42 | +1 | +0.1601 | +0.2191 | +0.2189 | 0.0004 | +0.4774 | +0.6551 | 0.939 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Cluster 12 | +1 | +0.1317 | +0.2190 | +0.2185 | 0.0004 | +0.6178 | +0.7437 | 0.918 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | Cluster 3 | +1 | +0.1384 | +0.2185 | +0.2177 | 0.0004 | +0.7354 | +0.7525 | 0.099 |
| `combo_max__net_volume_flow__first_bar_sentiment` | Cluster 37 | +1 | +0.1357 | +0.2182 | +0.2180 | 0.0004 | +0.5514 | +0.7120 | 0.956 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Cluster 11 | +1 | +0.1422 | +0.2174 | +0.2166 | 0.0004 | +0.5200 | +0.6692 | 0.911 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 28 | +1 | +0.1473 | +0.2168 | +0.2169 | 0.0004 | +0.5346 | +0.7079 | 0.936 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Cluster 36 | +1 | +0.1661 | +0.2166 | +0.2160 | 0.0004 | +0.7341 | +0.7314 | 0.920 |
| `combo_min__max_up_ret__bar_ret_0` | Cluster 37 | +1 | +0.1754 | +0.2151 | +0.2146 | 0.0004 | +0.4721 | +0.6721 | 1.000 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Cluster 13 | +1 | +0.1459 | +0.2149 | +0.2142 | 0.0004 | +0.5608 | +0.6839 | 0.805 |
| `combo_min__bar_ret_0__max_down_ret` | Cluster 11 | +1 | +0.1471 | +0.2145 | +0.2135 | 0.0006 | +0.5821 | +0.6985 | 0.810 |
| `combo_sig_product__max_up_ret__body_size_progression` | Cluster 0 | +1 | +0.1546 | +0.2143 | +0.2133 | 0.0006 | +0.7984 | +0.7554 | 0.942 |
| `combo_max__close_vs_open_range__bar_ret_0` | Cluster 37 | +1 | +0.1697 | +0.2135 | +0.2128 | 0.0006 | +0.7067 | +0.7625 | 0.878 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 6 | +1 | +0.1294 | +0.2129 | +0.2127 | 0.0006 | +0.6430 | +0.7443 | 0.910 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Cluster 39 | +1 | +0.1856 | +0.2115 | +0.2110 | 0.0006 | +0.6287 | +0.7185 | 0.890 |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | Cluster 36 | +1 | +0.1333 | +0.2106 | +0.2106 | 0.0006 | +0.6393 | +0.7243 | 0.848 |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | Cluster 37 | +1 | +0.1699 | +0.2103 | +0.2096 | 0.0006 | +0.7151 | +0.7537 | 0.880 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | Cluster 11 | +1 | +0.1396 | +0.2095 | +0.2087 | 0.0006 | +0.5586 | +0.7038 | 0.893 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 41 | +1 | +0.1638 | +0.2091 | +0.2087 | 0.0006 | +0.6844 | +0.7408 | 0.859 |
| `combo_rank_max__net_volume_flow__first_bar_return` | Cluster 37 | +1 | +0.1601 | +0.2090 | +0.2083 | 0.0006 | +0.6707 | +0.7531 | 0.946 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 40 | +1 | +0.1640 | +0.2088 | +0.2083 | 0.0006 | +0.7280 | +0.7226 | 0.841 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 39 | +1 | +0.1741 | +0.2083 | +0.2076 | 0.0006 | +0.4733 | +0.7103 | 0.949 |
| `combo_max__first_bar_return__max_down_ret` | Cluster 11 | +1 | +0.1655 | +0.2082 | +0.2077 | 0.0006 | +0.6208 | +0.7144 | 1.000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 28 | +1 | +0.1641 | +0.2072 | +0.2079 | 0.0006 | +0.5193 | +0.7032 | 0.848 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Cluster 36 | +1 | +0.1520 | +0.2072 | +0.2067 | 0.0006 | +0.7501 | +0.7677 | 0.975 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 41 | +1 | +0.1692 | +0.2066 | +0.2061 | 0.0006 | +0.7149 | +0.7812 | 0.927 |
| `combo_max__close_vs_open_range__early_body_momentum` | Cluster 10 | +1 | +0.1011 | +0.2065 | +0.2055 | 0.0006 | +0.5690 | +0.7355 | 0.927 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Cluster 9 | +1 | +0.1432 | +0.2059 | +0.2050 | 0.0006 | +0.5352 | +0.6674 | 0.843 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Cluster 37 | +1 | +0.1585 | +0.2051 | +0.2044 | 0.0006 | +0.6976 | +0.7630 | 1.000 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Cluster 25 | +1 | +0.1535 | +0.2041 | +0.2034 | 0.0006 | +0.5946 | +0.7443 | 0.886 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 26 | +1 | +0.1885 | +0.2038 | +0.2027 | 0.0006 | +0.5312 | +0.7273 | 0.929 |
| `combo_rank_min__close_vs_open_range__max_down_ret` | Cluster 10 | +1 | +0.1325 | +0.2016 | +0.2007 | 0.0006 | +0.4967 | +0.6921 | 0.954 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Cluster 42 | +1 | +0.1647 | +0.2011 | +0.2008 | 0.0006 | +0.5445 | +0.6886 | 0.966 |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | Cluster 10 | +1 | +0.1017 | +0.2008 | +0.2002 | 0.0006 | +0.4601 | +0.7032 | 0.939 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Cluster 9 | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0006 | +0.3439 | +0.6633 | 0.628 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | Cluster 36 | +1 | +0.1332 | +0.2006 | +0.2007 | 0.0006 | +0.5822 | +0.6979 | 0.945 |
| `combo_min__close_vs_open_range__max_down_ret` | Cluster 10 | +1 | +0.1290 | +0.1991 | +0.1980 | 0.0006 | +0.5237 | +0.6815 | 0.866 |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | Cluster 40 | +1 | +0.1618 | +0.1990 | +0.1985 | 0.0006 | +0.6783 | +0.7150 | 0.950 |
| `combo_sig_product__close_vs_open_range__high_low_sequence_momentum` | Cluster 10 | +1 | +0.1051 | +0.1985 | +0.1975 | 0.0006 | +0.4136 | +0.6628 | 0.999 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Cluster 25 | +1 | +0.1710 | +0.1979 | +0.1973 | 0.0006 | +0.6340 | +0.7630 | 0.922 |
| `combo_max__net_volume_flow__bar_ret_0` | Cluster 37 | +1 | +0.1567 | +0.1965 | +0.1959 | 0.0008 | +0.5662 | +0.7109 | 0.932 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Cluster 40 | +1 | +0.1623 | +0.1951 | +0.1946 | 0.0008 | +0.7260 | +0.7214 | 0.953 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 45 | +1 | +0.0926 | +0.1951 | +0.1951 | 0.0008 | +0.7041 | +0.7525 | 0.916 |
| `combo_mean__net_volume_flow__max_down_ret` | Cluster 10 | +1 | +0.1334 | +0.1947 | +0.1940 | 0.0008 | +0.5809 | +0.7126 | 0.971 |
| `first_bar_return` | Cluster 11 | +1 | +0.1592 | +0.1937 | +0.1931 | 0.0008 | +0.5925 | +0.7109 | 0.949 |
| `combo_max__first_bar_sentiment__bar_ret_0` | Cluster 11 | +1 | +0.1507 | +0.1927 | +0.1926 | 0.0010 | +0.5474 | +0.6938 | 0.881 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Cluster 11 | +1 | +0.1365 | +0.1927 | +0.1931 | 0.0010 | +0.4562 | +0.6856 | 0.848 |
| `combo_mean__first_bar_sentiment__max_down_ret` | Cluster 11 | +1 | +0.1520 | +0.1916 | +0.1909 | 0.0010 | +0.5020 | +0.6563 | 0.878 |
| `combo_clamp_diff__max_up_ret__trend_bar_close_consistency` | Cluster 45 | +1 | +0.0740 | +0.1864 | +0.1868 | 0.0010 | +0.4873 | +0.6774 | 0.879 |
| `combo_diff__max_up_ret__trend_bar_close_consistency` | Cluster 45 | +1 | +0.0740 | +0.1863 | +0.1867 | 0.0010 | +0.4781 | +0.6692 | 0.949 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Cluster 36 | +1 | +0.1518 | +0.1848 | +0.1844 | 0.0012 | +0.4502 | +0.6639 | 1.000 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | Cluster 36 | +1 | +0.1704 | +0.1832 | +0.1824 | 0.0014 | +0.6774 | +0.7672 | 0.944 |
| `combo_rank_max__trend_bar_close_consistency__close_vs_open_range` | Cluster 10 | +1 | +0.0978 | +0.1810 | +0.1802 | 0.0014 | +0.4296 | +0.7009 | 0.942 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 0 | +1 | +0.1645 | +0.1805 | +0.1805 | 0.0014 | +0.6474 | +0.7431 | 1.000 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Cluster 11 | +1 | +0.1104 | +0.1789 | +0.1778 | 0.0014 | +0.4558 | +0.6657 | 1.000 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Cluster 43 | +1 | +0.1252 | +0.1753 | +0.1750 | 0.0014 | +0.4446 | +0.6510 | 0.928 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 5 | +1 | +0.0772 | +0.1732 | +0.1723 | 0.0016 | +0.4734 | +0.6551 | 0.669 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` | Cluster 45 | +1 | +0.1044 | +0.1685 | +0.1689 | 0.0018 | +0.5198 | +0.6997 | 0.940 |
| `combo_max__early_body_momentum__max_down_ret` | Cluster 10 | +1 | +0.1118 | +0.1669 | +0.1666 | 0.0026 | +0.4026 | +0.6751 | 0.897 |
| `vwap_trend_channel_slope` | Cluster 0 | +1 | +0.1023 | +0.1640 | +0.1634 | 0.0028 | +0.4395 | +0.6727 | 0.743 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Cluster 33 | +1 | +0.1645 | +0.1596 | +0.1592 | 0.0044 | +0.5278 | +0.6897 | 0.857 |
| `morning_volume_weighted_momentum` | Cluster 10 | +1 | +0.1126 | +0.1488 | +0.1481 | 0.0076 | +0.4334 | +0.6557 | 0.908 |
| `open_to_current_return` | Cluster 10 | +1 | +0.1167 | +0.1461 | +0.1453 | 0.0086 | +0.4680 | +0.6979 | 1.000 |
| `bar_body_rng_0` | Cluster 11 | +1 | +0.1464 | +0.1321 | +0.1314 | 0.0152 | +0.5533 | +0.6862 | 0.912 |
| `or_fill_ratio` | Cluster 10 | +1 | +0.0791 | +0.1288 | +0.1281 | 0.0172 | +0.5065 | +0.7273 | 0.939 |

### 588000ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | Cluster 0 | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.789 |
| `combo_rel_diff__directional_volume_signature__smooth_momentum_structure` | Cluster 0 | +1 | +0.1078 | +0.3011 | +0.2999 | 0.0000 | +0.7892 | +0.7651 | 0.897 |
| `combo_diff__directional_volume_signature__early_vwap_acceleration` | Cluster 0 | +1 | +0.1087 | +0.2917 | +0.2905 | 0.0000 | +0.7855 | +0.7838 | 0.903 |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | Cluster 2 | +1 | +0.1329 | +0.2836 | +0.2825 | 0.0000 | +0.8900 | +0.7947 | 0.999 |
| `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | Cluster 2 | +1 | +0.1389 | +0.2830 | +0.2820 | 0.0000 | +0.8709 | +0.7927 | 0.992 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | Cluster 1 | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0002 | +0.8649 | +0.7779 | 0.730 |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | Cluster 0 | +1 | +0.0645 | +0.2645 | +0.2642 | 0.0002 | +0.6275 | +0.7512 | 0.808 |
| `max_up_ret` | Cluster 3 | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0046 | +0.6051 | +0.7266 | 0.728 |

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 0 | +1 | +0.1383 | +0.2945 | +0.2928 | 0.0000 | +0.6026 | +0.7202 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 0 | +1 | +0.1766 | +0.2917 | +0.2894 | 0.0000 | +0.6974 | +0.7384 | 0.781 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 0 | +1 | +0.1502 | +0.2885 | +0.2864 | 0.0000 | +0.5040 | +0.6598 | 0.738 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1535 | +0.2841 | +0.2818 | 0.0000 | +0.5821 | +0.6804 | 0.876 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Cluster 0 | +1 | +0.1592 | +0.2707 | +0.2678 | 0.0000 | +0.6708 | +0.7026 | 0.933 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Cluster 0 | +1 | +0.1372 | +0.2664 | +0.2647 | 0.0000 | +0.5384 | +0.7050 | 0.836 |
| `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1569 | +0.2647 | +0.2627 | 0.0000 | +0.6548 | +0.7097 | 0.920 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 0 | +1 | +0.1345 | +0.2645 | +0.2631 | 0.0000 | +0.6316 | +0.7226 | 0.891 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 0 | +1 | +0.1701 | +0.2638 | +0.2615 | 0.0000 | +0.5328 | +0.6968 | 0.931 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 0 | +1 | +0.1678 | +0.2557 | +0.2535 | 0.0000 | +0.4950 | +0.6563 | 0.936 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 0 | +1 | +0.1666 | +0.2542 | +0.2517 | 0.0000 | +0.5811 | +0.7367 | 0.868 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Cluster 0 | +1 | +0.1416 | +0.2540 | +0.2515 | 0.0000 | +0.5473 | +0.6933 | 0.943 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 1 | +1 | +0.0909 | +0.2510 | +0.2513 | 0.0000 | +0.5263 | +0.6962 | 0.610 |
| `combo_min__star50_limit_proximity_early__first_bar_sentiment` | Cluster 0 | +1 | +0.1532 | +0.2509 | +0.2487 | 0.0000 | +0.5675 | +0.6985 | 0.937 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 0 | +1 | +0.1678 | +0.2476 | +0.2451 | 0.0000 | +0.5605 | +0.7384 | 0.960 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 0 | +1 | +0.1533 | +0.2455 | +0.2443 | 0.0000 | +0.5912 | +0.7331 | 0.829 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 1 | +1 | +0.1075 | +0.2449 | +0.2443 | 0.0000 | +0.7396 | +0.7818 | 0.871 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Cluster 0 | +1 | +0.1601 | +0.2443 | +0.2423 | 0.0000 | +0.6470 | +0.7126 | 0.934 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Cluster 0 | +1 | +0.1507 | +0.2332 | +0.2310 | 0.0000 | +0.4553 | +0.6815 | 0.966 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 0 | +1 | +0.1441 | +0.2252 | +0.2233 | 0.0000 | +0.4877 | +0.6956 | 0.921 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Cluster 0 | +1 | +0.1349 | +0.2232 | +0.2213 | 0.0000 | +0.4124 | +0.6745 | 0.869 |
| `combo_max__max_up_ret__first_bar_return` | Cluster 0 | +1 | +0.1444 | +0.2224 | +0.2203 | 0.0000 | +0.5050 | +0.7062 | 0.927 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | Cluster 0 | +1 | +0.1286 | +0.2150 | +0.2131 | 0.0000 | +0.6017 | +0.7736 | 0.888 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Cluster 0 | +1 | +0.1256 | +0.2110 | +0.2093 | 0.0000 | +0.4011 | +0.6540 | 0.896 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Cluster 0 | +1 | +0.1409 | +0.2105 | +0.2079 | 0.0000 | +0.4730 | +0.6604 | 0.892 |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | Cluster 0 | +1 | +0.1383 | +0.2093 | +0.2069 | 0.0000 | +0.5332 | +0.6880 | 0.925 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 2 | +1 | +0.1034 | +0.1683 | +0.1674 | 0.0024 | +0.4694 | +0.6950 | 0.105 |


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 2 | 0.3088 | `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_z_sum__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 1 | 1 | 0.3088 | `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 2 | 2 | 0.3088 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 3 | 3 | 0.3088 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 4 | 1 | 0.3088 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | _(none)_ |
| 300ETF | single | Cluster 5 | 1 | 0.3088 | `combo_mean__max_up_ret__volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 6 | 3 | 0.3088 | `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_min__max_up_ret__bar_body_rng_0`, `combo_mean__max_up_ret__bar_body_rng_0` |
| 300ETF | single | Cluster 7 | 4 | 0.3088 | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `combo_mean__max_up_ret__volume_weighted_price_position`, `combo_min__max_up_ret__volume_weighted_price_position`, `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 8 | 1 | 0.3088 | `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | _(none)_ |
| 300ETF | single | Cluster 9 | 8 | 0.3088 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_min__star50_limit_proximity_early__bar_body_rng_0`, `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` |
| 300ETF | single | Cluster 10 | 2 | 0.3088 | `combo_z_sum__max_up_ret__opening_drive_thrust_ratio` | `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` |
| 300ETF | single | Cluster 11 | 2 | 0.3088 | `rbreaker_sell_setup_proximity_early` | `star50_limit_proximity_early` |
| 300ETF | single | Cluster 12 | 4 | 0.3088 | `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `combo_max__first_bar_return__bar_body_rng_0`, `combo_ratio__first_bar_return__volume_weighted_price_position`, `combo_max__bar_body_rng_0__volume_surge_direction` |
| 300ETF | single | Cluster 13 | 3 | 0.3088 | `combo_rank_max__bar_ret_0__volume_weighted_price_position` | `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`, `combo_mean__bar_ret_0__volume_weighted_price_position` |
| 300ETF | single | Cluster 14 | 1 | 0.3088 | `combo_min__volume_weighted_price_position__volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 15 | 1 | 0.3088 | `combo_ratio__first_bar_sentiment__volume_surge_direction` | _(none)_ |
| 300ETF | single | Cluster 16 | 2 | 0.3088 | `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `combo_diff__max_up_ret__early_vwap_acceleration` |
| 500ETF | single | Cluster 0 | 9 | 0.2355 | `combo_sig_product__max_up_ret__close_vs_open_range` | `combo_sig_product__max_up_ret__early_body_momentum`, `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`, `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_sig_product__max_up_ret__early_late_momentum_divergence`, `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`, `combo_sig_product__max_up_ret__body_size_progression`, `combo_sig_product__max_up_ret__bar_ret_0`, `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 1 | 3 | 0.2355 | `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | `combo_rank_min__star50_limit_proximity_early__max_down_ret`, `combo_min__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 2 | 3 | 0.2355 | `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`, `combo_diff__star50_limit_proximity_early__body_size_progression` |
| 500ETF | single | Cluster 3 | 2 | 0.2355 | `combo_ratio__max_down_ret__net_volume_flow` | `combo_ratio__max_down_ret__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 4 | 1 | 0.2355 | `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | _(none)_ |
| 500ETF | single | Cluster 5 | 1 | 0.2355 | `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | _(none)_ |
| 500ETF | single | Cluster 6 | 2 | 0.2355 | `star50_limit_proximity_early` | `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 7 | 1 | 0.2355 | `rbreaker_sell_setup_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 8 | 3 | 0.2355 | `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 9 | 2 | 0.2355 | `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `combo_sig_product__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 10 | 31 | 0.2355 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`, `combo_rank_min__max_up_ret__close_vs_open_range`, `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`, `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`, `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_mean__max_up_ret__trend_bar_close_consistency`, `combo_rank_min__net_volume_flow__close_vs_open_range`, `combo_max__max_up_ret__early_body_momentum`, `combo_min__max_up_ret__close_vs_open_range`, `combo_min__close_vs_open_range__high_low_sequence_momentum`, `combo_rank_max__max_up_ret__early_body_momentum`, `combo_mean__max_up_ret__close_vs_open_range`, `combo_max__max_up_ret__close_vs_open_range`, `combo_min__max_up_ret__high_low_sequence_momentum`, `combo_mean__volatility_expansion_trend_vector__close_vs_open_range`, `combo_rank_max__max_up_ret__close_vs_open_range`, `net_volume_flow`, `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`, `combo_sig_product__net_volume_flow__close_vs_open_range`, `combo_sig_product__close_vs_open_range__high_low_sequence_momentum`, `combo_rank_min__close_vs_open_range__max_down_ret`, `combo_max__close_vs_open_range__early_body_momentum`, `combo_sig_product__close_vs_open_range__early_body_momentum`, `combo_min__close_vs_open_range__max_down_ret`, `combo_mean__net_volume_flow__max_down_ret`, `combo_rank_max__trend_bar_close_consistency__close_vs_open_range`, `combo_max__early_body_momentum__max_down_ret`, `morning_volume_weighted_momentum`, `open_to_current_return`, `or_fill_ratio` |
| 500ETF | single | Cluster 11 | 18 | 0.2355 | `combo_rank_min__max_up_ret__first_bar_sentiment` | `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`, `combo_rank_min__first_bar_sentiment__max_down_ret`, `combo_rank_min__first_bar_sentiment__early_body_momentum`, `combo_rank_max__bar_ret_0__max_down_ret`, `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment`, `combo_min__first_bar_sentiment__bar_ret_0`, `combo_rank_min__first_bar_sentiment__bar_ret_0`, `combo_rank_min__bar_ret_0__max_down_ret`, `combo_min__bar_ret_0__max_down_ret`, `combo_max__close_vs_open_range__first_bar_sentiment`, `combo_max__first_bar_return__max_down_ret`, `first_bar_return`, `combo_max__first_bar_sentiment__bar_ret_0`, `combo_sig_product__first_bar_sentiment__early_body_momentum`, `combo_mean__first_bar_sentiment__max_down_ret`, `combo_sig_product__net_volume_flow__first_bar_return`, `bar_body_rng_0` |
| 500ETF | single | Cluster 12 | 1 | 0.2355 | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | _(none)_ |
| 500ETF | single | Cluster 13 | 2 | 0.2355 | `combo_mean__star50_limit_proximity_early__max_down_ret` | `combo_rank_max__star50_limit_proximity_early__max_down_ret` |
| 500ETF | single | Cluster 14 | 2 | 0.2355 | `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 500ETF | single | Cluster 15 | 1 | 0.2355 | `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | _(none)_ |
| 500ETF | single | Cluster 16 | 2 | 0.2355 | `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` |
| 500ETF | single | Cluster 17 | 2 | 0.2355 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` |
| 500ETF | single | Cluster 18 | 2 | 0.2355 | `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 19 | 2 | 0.2355 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 20 | 1 | 0.2355 | `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 21 | 4 | 0.2355 | `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`, `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`, `combo_min__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 22 | 2 | 0.2355 | `combo_mean__net_volume_flow__star50_limit_proximity_early` | `combo_mean__star50_limit_proximity_early__close_vs_open_range` |
| 500ETF | single | Cluster 23 | 1 | 0.2355 | `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | _(none)_ |
| 500ETF | single | Cluster 24 | 3 | 0.2355 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `combo_max__opening_drive_thrust_ratio__max_up_ret`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 25 | 4 | 0.2355 | `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `combo_max__opening_drive_thrust_ratio__max_down_ret`, `combo_rank_min__opening_drive_thrust_ratio__max_down_ret`, `combo_mean__opening_drive_thrust_ratio__max_down_ret` |
| 500ETF | single | Cluster 26 | 3 | 0.2355 | `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`, `combo_max__opening_drive_thrust_ratio__bar_ret_0` |
| 500ETF | single | Cluster 27 | 4 | 0.2355 | `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `combo_min__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_min__opening_drive_thrust_ratio__first_bar_return`, `combo_mean__opening_drive_thrust_ratio__bar_ret_0` |
| 500ETF | single | Cluster 28 | 4 | 0.2355 | `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`, `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`, `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 29 | 2 | 0.2355 | `combo_min__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` |
| 500ETF | single | Cluster 30 | 5 | 0.2355 | `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `combo_max__opening_drive_thrust_ratio__early_body_momentum`, `combo_max__opening_drive_thrust_ratio__close_vs_open_range`, `combo_mean__opening_drive_thrust_ratio__close_vs_open_range`, `combo_min__opening_drive_thrust_ratio__close_vs_open_range` |
| 500ETF | single | Cluster 31 | 2 | 0.2355 | `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 32 | 1 | 0.2355 | `opening_drive_thrust_ratio` | _(none)_ |
| 500ETF | single | Cluster 33 | 1 | 0.2355 | `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 34 | 2 | 0.2355 | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` |
| 500ETF | single | Cluster 35 | 1 | 0.2355 | `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | _(none)_ |
| 500ETF | single | Cluster 36 | 17 | 0.2355 | `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_clamp_diff__max_up_ret__body_size_progression`, `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`, `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_diff__max_up_ret__body_size_progression`, `combo_rel_diff__max_up_ret__smooth_momentum_structure`, `combo_rel_diff__max_up_ret__late_bar_momentum`, `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`, `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`, `combo_rel_diff__max_up_ret__body_size_progression`, `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`, `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`, `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`, `combo_sig_product__opening_drive_thrust_ratio__body_size_progression`, `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence`, `combo_sig_product__opening_drive_thrust_ratio__first_bar_return`, `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` |
| 500ETF | single | Cluster 37 | 21 | 0.2355 | `combo_mean__max_up_ret__first_bar_sentiment` | `max_up_ret`, `combo_rank_min__close_vs_open_range__bar_ret_0`, `combo_mean__first_bar_sentiment__early_body_momentum`, `combo_rank_min__trend_bar_close_consistency__bar_ret_0`, `combo_min__close_vs_open_range__bar_ret_0`, `combo_mean__max_up_ret__first_bar_return`, `combo_min__net_volume_flow__bar_ret_0`, `combo_rank_min__max_up_ret__bar_ret_0`, `combo_max__max_up_ret__first_bar_return`, `combo_max__net_volume_flow__first_bar_sentiment`, `combo_rank_max__max_up_ret__first_bar_return`, `combo_mean__net_volume_flow__bar_ret_0`, `combo_min__close_vs_open_range__first_bar_sentiment`, `combo_mean__close_vs_open_range__first_bar_sentiment`, `combo_min__max_up_ret__bar_ret_0`, `combo_max__close_vs_open_range__bar_ret_0`, `combo_rank_max__close_vs_open_range__bar_ret_0`, `combo_rank_max__net_volume_flow__first_bar_return`, `combo_mean__close_vs_open_range__bar_ret_0`, `combo_max__net_volume_flow__bar_ret_0` |
| 500ETF | single | Cluster 38 | 1 | 0.2355 | `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | _(none)_ |
| 500ETF | single | Cluster 39 | 5 | 0.2355 | `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`, `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`, `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 500ETF | single | Cluster 40 | 4 | 0.2355 | `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | `combo_max__star50_limit_proximity_early__bar_ret_0`, `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_rank_max__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 41 | 3 | 0.2355 | `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` |
| 500ETF | single | Cluster 42 | 2 | 0.2355 | `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 43 | 1 | 0.2355 | `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | _(none)_ |
| 500ETF | single | Cluster 44 | 2 | 0.2355 | `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` |
| 500ETF | single | Cluster 45 | 7 | 0.2355 | `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `combo_rel_diff__max_up_ret__early_body_momentum`, `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`, `combo_clamp_diff__max_up_ret__trend_bar_close_consistency`, `combo_diff__max_up_ret__trend_bar_close_consistency`, `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` |
| 588000ETF | single | Cluster 0 | 4 | 0.3860 | `combo_diff__directional_volume_signature__smooth_momentum_structure` | `combo_rel_diff__directional_volume_signature__smooth_momentum_structure`, `combo_diff__directional_volume_signature__early_vwap_acceleration`, `combo_sig_product__directional_volume_signature__smooth_momentum_structure` |
| 588000ETF | single | Cluster 1 | 1 | 0.3860 | `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | _(none)_ |
| 588000ETF | single | Cluster 2 | 2 | 0.3860 | `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` |
| 588000ETF | single | Cluster 3 | 1 | 0.3860 | `max_up_ret` | _(none)_ |
| 159915ETF | single | Cluster 0 | 24 | 0.3447 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`, `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`, `combo_min__star50_limit_proximity_early__bar_body_rng_0`, `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`, `combo_min__opening_drive_thrust_ratio__first_bar_sentiment`, `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0`, `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`, `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_rank_min__star50_limit_proximity_early__first_bar_return`, `combo_min__star50_limit_proximity_early__first_bar_sentiment`, `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`, `combo_mean__star50_limit_proximity_early__bar_ret_0`, `combo_mean__max_up_ret__bar_body_rng_0`, `combo_rank_max__max_up_ret__first_bar_return`, `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early`, `combo_max__max_up_ret__first_bar_return`, `combo_z_sum__opening_drive_thrust_ratio__max_up_ret`, `combo_clamp_diff__max_up_ret__demark_setup_reversal_early`, `combo_rank_max__opening_drive_thrust_ratio__first_bar_return`, `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` |
| 159915ETF | single | Cluster 1 | 2 | 0.3447 | `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` |
| 159915ETF | single | Cluster 2 | 1 | 0.3447 | `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | _(none)_ |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | `tri_mean` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_z_sum__max_up_ret__opening_drive_thrust_ratio` | `z_sum` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | `rank_max` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_min__max_up_ret__volume_weighted_price_position` | `min` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_mean__bar_ret_0__volume_weighted_price_position` | `mean` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_max__first_bar_return__bar_body_rng_0` | `max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__volume_surge_direction` | `mean` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_z_sum__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | `min` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_max__bar_body_rng_0__volume_surge_direction` | `max` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`volatility_expansion_trend_vector` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__max_up_ret__close_vs_open_range` | `rank_min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | `rel_diff` | a=`net_volume_flow`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | `rank_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `mean` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`trend_bar_close_consistency` |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | `rel_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | `rank_min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow`, c=`star50_limit_proximity_early` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | `rank_min` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | `min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_mean__max_up_ret__first_bar_sentiment` | `mean` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | `mean` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | `min` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`body_size_progression` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `rel_diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | `max` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_mean__max_up_ret__trend_bar_close_consistency` | `mean` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | `mean` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_diff__max_up_ret__body_size_progression` | `diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_max__max_up_ret__early_body_momentum` | `max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_min__max_up_ret__close_vs_open_range` | `min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`net_volume_flow` |
| `combo_mean__max_up_ret__close_vs_open_range` | `mean` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__early_body_momentum` | `sig_product` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | `rank_min` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_max__max_up_ret__close_vs_open_range` | `max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | `sig_product` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | `min` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | `diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | `rank_min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | `rank_min` | a=`trend_bar_close_consistency`, b=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__early_body_momentum` | `rel_diff` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_min__max_up_ret__high_low_sequence_momentum` | `min` | a=`max_up_ret`, b=`high_low_sequence_momentum` |
| `combo_min__close_vs_open_range__high_low_sequence_momentum` | `min` | a=`close_vs_open_range`, b=`high_low_sequence_momentum` |
| `combo_min__close_vs_open_range__bar_ret_0` | `min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_mean__max_up_ret__first_bar_return` | `mean` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_min__net_volume_flow__bar_ret_0` | `min` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_rank_max__max_up_ret__close_vs_open_range` | `rank_max` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__max_up_ret__bar_ret_0` | `rank_min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_mean__volatility_expansion_trend_vector__close_vs_open_range` | `mean` | a=`volatility_expansion_trend_vector`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | `sig_product` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_min__first_bar_sentiment__bar_ret_0` | `min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_max__max_up_ret__first_bar_return` | `max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_mean__net_volume_flow__bar_ret_0` | `mean` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_ratio__max_down_ret__net_volume_flow` | `ratio` | a=`max_down_ret`, b=`net_volume_flow` |
| `combo_min__close_vs_open_range__first_bar_sentiment` | `min` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | `rank_min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | `mean` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | `sig_product` | a=`net_volume_flow`, b=`close_vs_open_range` |
| `combo_mean__first_bar_sentiment__early_body_momentum` | `mean` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | `rank_max` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | `ratio` | a=`max_down_ret`, b=`volatility_expansion_trend_vector` |
| `combo_max__net_volume_flow__first_bar_sentiment` | `max` | a=`net_volume_flow`, b=`first_bar_sentiment` |
| `combo_rank_min__bar_ret_0__max_down_ret` | `rank_min` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`late_bar_momentum` |
| `combo_min__max_up_ret__bar_ret_0` | `min` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | `rank_max` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__bar_ret_0__max_down_ret` | `min` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__close_vs_open_range__bar_ret_0` | `max` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | `rank_max` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_max__close_vs_open_range__first_bar_sentiment` | `max` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__net_volume_flow__first_bar_return` | `rank_max` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_max__first_bar_return__max_down_ret` | `max` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__close_vs_open_range__early_body_momentum` | `max` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_mean__close_vs_open_range__bar_ret_0` | `mean` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_min__close_vs_open_range__max_down_ret` | `rank_min` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volatility_expansion_trend_vector` |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | `sig_product` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`early_late_momentum_divergence` |
| `combo_min__close_vs_open_range__max_down_ret` | `min` | a=`close_vs_open_range`, b=`max_down_ret` |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | `rank_max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__close_vs_open_range__high_low_sequence_momentum` | `sig_product` | a=`close_vs_open_range`, b=`high_low_sequence_momentum` |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | `mean` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_max__net_volume_flow__bar_ret_0` | `max` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_mean__net_volume_flow__max_down_ret` | `mean` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_max__first_bar_sentiment__bar_ret_0` | `max` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_mean__first_bar_sentiment__max_down_ret` | `mean` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_clamp_diff__max_up_ret__trend_bar_close_consistency` | `clamp_diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_diff__max_up_ret__trend_bar_close_consistency` | `diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_rank_max__trend_bar_close_consistency__close_vs_open_range` | `rank_max` | a=`trend_bar_close_consistency`, b=`close_vs_open_range` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_sig_product__net_volume_flow__first_bar_return` | `sig_product` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | `rank_max` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `min` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`early_body_momentum` |
| `combo_max__early_body_momentum__max_down_ret` | `max` | a=`early_body_momentum`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | `diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_rel_diff__directional_volume_signature__smooth_momentum_structure` | `rel_diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_diff__directional_volume_signature__early_vwap_acceleration` | `diff` | a=`directional_volume_signature`, b=`early_vwap_acceleration` |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `diff` | a=`trend_day_regime_conviction`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `rel_diff` | a=`trend_day_regime_conviction`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | `sig_product` | a=`high_low_sequence_momentum`, b=`vwap_trend_channel_slope` |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | `sig_product` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`first_bar_return` |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0` | `z_sum` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__star50_limit_proximity_early__first_bar_sentiment` | `min` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | `z_sum` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | `z_sum` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_max__max_up_ret__first_bar_return` | `max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | `clamp_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | `z_sum` | a=`first_bar_sentiment`, b=`limit_down_proximity_early` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
