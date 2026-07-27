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
| 300ETF | single | 1,569 | 530 | 403 | 57 | 37 | 27 | 27 | 27 | 11 | 11 |
| 50ETF | single | 1,244 | 514 | 463 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,037 | 1,547 | 1,406 | 1,087 | 1,072 | 751 | 537 | 535 | 43 | 43 |
| 588000ETF | single | 1,583 | 1,016 | 768 | 475 | 427 | 29 | 29 | 29 | 5 | 5 |
| 159915ETF | single | 1,887 | 759 | 528 | 209 | 192 | 22 | 22 | 22 | 8 | 8 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.1343 | [+0.0813, +0.1833] | +0.2713 | [+0.1430, +0.3798] | +0.8909 | 8.51% | 1.7430 | 6.95% | 1.4459 | 3.1432 | 5.46% |
| 500ETF | single | 43 | +0.2178 | [+0.1720, +0.2646] | +0.3143 | [+0.2140, +0.4156] | +0.9636 | 9.87% | 2.0222 | 8.26% | 1.7144 | 3.5179 | 4.12% |
| 588000ETF | single | 5 | +0.1349 | [+0.0687, +0.1987] | +0.3388 | [+0.1895, +0.4335] | +0.9152 | 7.99% | 1.6882 | 6.50% | 1.3918 | 3.1882 | 3.29% |
| 159915ETF | single | 8 | +0.1698 | [+0.1219, +0.2142] | +0.2552 | [+0.1663, +0.3496] | +0.9515 | 7.81% | 1.2027 | 6.26% | 0.9689 | 1.3295 | 13.45% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0642* | [-0.0019, +0.1232] | +0.1856 | [+0.0259, +0.3134] | +0.9152 | 4.28% | 1.0661 | 2.68% | 0.6744 | 1.2221 | 4.11% |
| 500ETF | single | 43 | +0.1175 | [+0.0581, +0.1750] | +0.1233* | [-0.0216, +0.2405] | +0.8788 | 3.65% | 0.9074 | 2.26% | 0.5656 | 0.9784 | 3.47% |
| 588000ETF | single | 5 | -0.0014* | [-0.0993, +0.0806] | -0.1012* | [-0.3187, +0.1600] | +0.0667 | -2.37% | -0.4313 | -3.89% | -0.7028 | -0.9320 | 11.32% |
| 159915ETF | single | 8 | +0.1390 | [+0.0701, +0.1956] | +0.2994 | [+0.1310, +0.4277] | +0.6606 | 9.38% | 1.6147 | 8.00% | 1.3937 | 3.3359 | 7.09% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0290* | [-0.0663, +0.1176] | +0.1887* | [-0.0285, +0.3782] | +0.4788 | 5.12% | 1.0480 | 3.63% | 0.7518 | 1.4700 | 3.79% |
| 500ETF | single | 43 | +0.1286 | [+0.0471, +0.2067] | +0.0308* | [-0.1606, +0.2094] | +0.8424 | 2.85% | 0.7476 | 1.45% | 0.3797 | 0.6387 | 2.95% |
| 588000ETF | single | 5 | -0.0365* | [-0.1413, +0.0803] | -0.1101* | [-0.3543, +0.2096] | +0.0667 | -3.28% | -0.5661 | -4.79% | -0.8233 | -1.0984 | 9.94% |
| 159915ETF | single | 8 | +0.1442 | [+0.0518, +0.2318] | +0.2848 | [+0.0409, +0.5092] | +0.6727 | 11.82% | 1.6280 | 10.45% | 1.4543 | 3.7311 | 6.90% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1267 | +0.2690 | +0.2689 | 0.0000 | +0.5307 | +0.6968 | 0.000 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.824 |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | +1 | +0.0571 | +0.2100 | +0.2110 | 0.0000 | +0.5628 | +0.7349 | 0.337 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0208 | +0.2042 | +0.2034 | 0.0000 | +0.4802 | +0.6346 | 0.584 |
| `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio` | +1 | +0.0421 | +0.2002 | +0.2033 | 0.0000 | +0.6265 | +0.7144 | 0.106 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0538 | +0.1928 | +0.1935 | 0.0000 | +0.6003 | +0.7349 | 0.784 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +1 | +0.0999 | +0.1898 | +0.1897 | 0.0000 | +0.6533 | +0.7496 | 0.376 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +1 | +0.0777 | +0.1863 | +0.1849 | 0.0004 | +0.7183 | +0.7760 | 0.653 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +1 | +0.0859 | +0.1833 | +0.1834 | 0.0006 | +0.3817 | +0.6827 | 0.808 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +1 | +0.0993 | +0.1570 | +0.1561 | 0.0036 | +0.5103 | +0.6786 | 0.608 |
| `combo_min__max_up_ret__first_bar_sentiment` | +1 | +0.0941 | +0.1550 | +0.1534 | 0.0040 | +0.3542 | +0.6246 | 0.749 |

### 50ETF / single
No features admitted.

### 500ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1864 | +0.3278 | +0.3273 | 0.0000 | +0.7514 | +0.7625 | 0.000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1783 | +0.3277 | +0.3272 | 0.0000 | +0.8682 | +0.7842 | 0.673 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.2028 | +0.3177 | +0.3175 | 0.0000 | +0.8965 | +0.7965 | 0.735 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | +1 | +0.1712 | +0.3133 | +0.3127 | 0.0000 | +0.9506 | +0.8170 | 0.743 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1881 | +0.3068 | +0.3067 | 0.0000 | +0.6128 | +0.7326 | 0.660 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.1605 | +0.2977 | +0.2979 | 0.0000 | +0.7506 | +0.7806 | 0.770 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1611 | +0.2965 | +0.2961 | 0.0000 | +0.5518 | +0.6962 | 0.777 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.1777 | +0.2955 | +0.2949 | 0.0000 | +0.9529 | +0.8416 | 0.813 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1800 | +0.2907 | +0.2900 | 0.0000 | +0.8748 | +0.7959 | 0.831 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | +1 | +0.1395 | +0.2846 | +0.2837 | 0.0000 | +0.7432 | +0.7455 | 0.794 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +1 | +0.1884 | +0.2844 | +0.2839 | 0.0000 | +0.8363 | +0.7548 | 0.821 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1500 | +0.2835 | +0.2832 | 0.0000 | +0.8380 | +0.7607 | 0.605 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.1618 | +0.2832 | +0.2831 | 0.0000 | +0.6705 | +0.7337 | 0.701 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | +1 | +0.1560 | +0.2819 | +0.2805 | 0.0000 | +0.7803 | +0.7760 | 0.693 |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | +1 | +0.1360 | +0.2742 | +0.2735 | 0.0000 | +0.7025 | +0.7566 | 0.836 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +1 | +0.1702 | +0.2721 | +0.2709 | 0.0000 | +0.8193 | +0.7912 | 0.768 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +1 | +0.1915 | +0.2673 | +0.2666 | 0.0000 | +1.0490 | +0.8047 | 0.836 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +1 | +0.1640 | +0.2669 | +0.2662 | 0.0000 | +0.6667 | +0.7331 | 0.772 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +1 | +0.1499 | +0.2642 | +0.2624 | 0.0000 | +0.9245 | +0.8188 | 0.232 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | +1 | +0.0827 | +0.2636 | +0.2642 | 0.0000 | +0.6985 | +0.7478 | 0.427 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1312 | +0.2591 | +0.2586 | 0.0000 | +0.7790 | +0.7619 | 0.833 |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | +1 | +0.1472 | +0.2569 | +0.2566 | 0.0000 | +0.6376 | +0.7496 | 0.763 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1583 | +0.2552 | +0.2542 | 0.0000 | +0.7886 | +0.7695 | 0.725 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +1 | +0.1721 | +0.2550 | +0.2539 | 0.0000 | +0.6969 | +0.7701 | 0.750 |
| `combo_max__max_up_ret__early_body_momentum` | +1 | +0.1472 | +0.2549 | +0.2541 | 0.0000 | +0.9093 | +0.8047 | 0.818 |
| `combo_max__max_up_ret__first_bar_sentiment` | +1 | +0.1691 | +0.2505 | +0.2503 | 0.0000 | +0.6434 | +0.7754 | 0.800 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +1 | +0.1713 | +0.2386 | +0.2377 | 0.0000 | +0.7053 | +0.7449 | 0.825 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +1 | +0.1692 | +0.2377 | +0.2372 | 0.0000 | +0.6377 | +0.7308 | 0.846 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1828 | +0.2298 | +0.2291 | 0.0000 | +0.5203 | +0.7208 | 0.744 |
| `combo_mean__bar_ret_0__max_down_ret` | +1 | +0.1535 | +0.2271 | +0.2263 | 0.0002 | +0.5667 | +0.6481 | 0.841 |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.1001 | +0.2248 | +0.2252 | 0.0002 | +0.6393 | +0.7067 | 0.676 |
| `combo_ratio__max_down_ret__net_volume_flow` | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0002 | +0.8478 | +0.7883 | 0.094 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | +1 | +0.1384 | +0.2185 | +0.2177 | 0.0004 | +0.7354 | +0.7525 | 0.099 |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | +1 | +0.1333 | +0.2106 | +0.2106 | 0.0006 | +0.6393 | +0.7243 | 0.848 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0006 | +0.3439 | +0.6633 | 0.646 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1415 | +0.2006 | +0.2013 | 0.0006 | +0.3379 | +0.6129 | 0.649 |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1618 | +0.1990 | +0.1985 | 0.0006 | +0.6783 | +0.7150 | 0.821 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | +1 | +0.1154 | +0.1784 | +0.1792 | 0.0014 | +0.4236 | +0.6276 | 0.765 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.0772 | +0.1732 | +0.1723 | 0.0016 | +0.4734 | +0.6551 | 0.642 |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1085 | +0.1724 | +0.1727 | 0.0016 | +0.4426 | +0.6270 | 0.744 |
| `vwap_trend_channel_slope` | +1 | +0.1023 | +0.1640 | +0.1634 | 0.0028 | +0.4395 | +0.6727 | 0.718 |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | +1 | +0.0933 | +0.1580 | +0.1569 | 0.0044 | +0.4111 | +0.6076 | 0.645 |
| `combo_sig_product__trend_day_regime_conviction__bar_ret_0` | +1 | +0.0875 | +0.1417 | +0.1411 | 0.0106 | +0.3058 | +0.6240 | 0.714 |

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__high_low_sequence_momentum__smooth_momentum_structure` | +1 | +0.1393 | +0.3260 | +0.3248 | 0.0000 | +1.1114 | +0.8578 | 0.000 |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.705 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0002 | +0.8649 | +0.7779 | 0.675 |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | +1 | +0.0645 | +0.2645 | +0.2642 | 0.0002 | +0.6275 | +0.7512 | 0.808 |
| `max_up_ret` | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0046 | +0.6051 | +0.7266 | 0.704 |

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1766 | +0.2917 | +0.2894 | 0.0000 | +0.6974 | +0.7384 | 0.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1502 | +0.2885 | +0.2864 | 0.0000 | +0.5040 | +0.6598 | 0.738 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +1 | +0.1504 | +0.2731 | +0.2716 | 0.0000 | +0.6783 | +0.7683 | 0.811 |
| `combo_z_sum__bar_body_rng_0__limit_down_proximity_early` | +1 | +0.1406 | +0.2548 | +0.2527 | 0.0000 | +0.6352 | +0.6927 | 0.798 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0909 | +0.2510 | +0.2513 | 0.0000 | +0.5263 | +0.6962 | 0.564 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1286 | +0.2150 | +0.2131 | 0.0000 | +0.6017 | +0.7736 | 0.684 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | +1 | +0.1256 | +0.2110 | +0.2093 | 0.0000 | +0.4011 | +0.6540 | 0.832 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1034 | +0.1683 | +0.1674 | 0.0024 | +0.4694 | +0.6950 | 0.100 |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | `rel_diff` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio` | `product` | a=`smooth_momentum_structure`, b=`opening_drive_thrust_ratio` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`trend_bar_close_consistency` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | `rank_min` | a=`net_volume_flow`, b=`star50_limit_proximity_early` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | `rank_min` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `rel_diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | `sig_product` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_max__max_up_ret__early_body_momentum` | `max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_ratio__max_down_ret__net_volume_flow` | `ratio` | a=`max_down_ret`, b=`net_volume_flow` |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | `ratio` | a=`max_down_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`body_size_progression` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | `rank_max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | `sig_product` | a=`star50_limit_proximity_early`, b=`early_body_momentum` |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `min` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | `sig_product` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | `sig_product` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_sig_product__trend_day_regime_conviction__bar_ret_0` | `sig_product` | a=`trend_day_regime_conviction`, b=`bar_ret_0` |
| `combo_rel_diff__high_low_sequence_momentum__smooth_momentum_structure` | `rel_diff` | a=`high_low_sequence_momentum`, b=`smooth_momentum_structure` |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | `diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | `sig_product` | a=`high_low_sequence_momentum`, b=`vwap_trend_channel_slope` |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | `sig_product` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_z_sum__bar_body_rng_0__limit_down_proximity_early` | `z_sum` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | `clamp_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
