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
| 300ETF | single | 1,754 | 572 | 318 | 186 | 183 | 123 | 123 | 123 | 12 | 12 |
| 50ETF | single | 1,231 | 515 | 441 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,229 | 1,646 | 1,324 | 1,075 | 1,064 | 788 | 537 | 537 | 20 | 20 |
| 588000ETF | single | 1,562 | 1,001 | 673 | 505 | 465 | 29 | 29 | 29 | 4 | 4 |
| 159915ETF | single | 1,703 | 690 | 366 | 320 | 315 | 58 | 58 | 58 | 8 | 8 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | +0.1410 | [+0.0914, +0.1882] | +0.2663 | [+0.1473, +0.3701] | +0.8909 | 7.55% | 1.7137 | 5.93% | 1.3653 | 2.7107 | 5.60% |
| 500ETF | single | 20 | +0.2180 | [+0.1714, +0.2637] | +0.3425 | [+0.2368, +0.4427] | +0.9030 | 10.51% | 2.2195 | 8.98% | 1.9236 | 4.2698 | 3.74% |
| 588000ETF | single | 4 | +0.1451 | [+0.0810, +0.2037] | +0.3177 | [+0.1627, +0.4281] | +0.8909 | 7.50% | 1.4836 | 6.10% | 1.2195 | 2.9066 | 5.73% |
| 159915ETF | single | 8 | +0.1771 | [+0.1306, +0.2223] | +0.2781 | [+0.1902, +0.3750] | +0.9758 | 8.38% | 1.1750 | 6.86% | 0.9662 | 1.3168 | 12.63% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | +0.0660 | [+0.0004, +0.1264] | +0.1827 | [+0.0195, +0.3148] | +0.7333 | 3.76% | 0.9510 | 2.17% | 0.5537 | 0.9118 | 3.38% |
| 500ETF | single | 20 | +0.1130 | [+0.0527, +0.1695] | +0.0930* | [-0.0530, +0.2098] | +0.8667 | 1.86% | 0.5245 | 0.79% | 0.2245 | 0.3565 | 4.27% |
| 588000ETF | single | 4 | -0.0035* | [-0.1079, +0.0804] | -0.0178* | [-0.2699, +0.2277] | +0.2242 | -2.60% | -0.4523 | -4.11% | -0.7111 | -0.9630 | 12.15% |
| 159915ETF | single | 8 | +0.1373 | [+0.0647, +0.1960] | +0.2766 | [+0.1125, +0.3972] | +0.6606 | 9.72% | 1.5516 | 8.38% | 1.3529 | 3.4747 | 7.02% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | +0.0218* | [-0.0702, +0.1107] | +0.0970* | [-0.1240, +0.2904] | +0.6606 | 2.91% | 0.6014 | 1.34% | 0.2778 | 0.4546 | 4.10% |
| 500ETF | single | 20 | +0.1294 | [+0.0497, +0.2011] | +0.0565* | [-0.1376, +0.2245] | +0.9152 | 1.54% | 0.4697 | 0.48% | 0.1451 | 0.2294 | 2.75% |
| 588000ETF | single | 4 | -0.0490* | [-0.1589, +0.0752] | +0.0150* | [-0.2733, +0.2967] | -0.2606 | -1.97% | -0.3275 | -3.50% | -0.5795 | -0.7963 | 9.44% |
| 159915ETF | single | 8 | +0.1486 | [+0.0498, +0.2345] | +0.2969 | [+0.0460, +0.4950] | +0.5879 | 12.86% | 1.6418 | 11.57% | 1.4936 | 4.3219 | 6.43% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +1 | +0.1299 | +0.2949 | +0.2950 | 0.0000 | +0.7632 | +0.7279 | 0.000 |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1075 | +0.2754 | +0.2751 | 0.0000 | +0.4882 | +0.6891 | 0.651 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.1275 | +0.2662 | +0.2660 | 0.0000 | +0.8452 | +0.8094 | 0.724 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1164 | +0.2660 | +0.2658 | 0.0000 | +0.6109 | +0.7003 | 0.698 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.794 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +1 | +0.0829 | +0.2240 | +0.2229 | 0.0000 | +0.8024 | +0.7894 | 0.656 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +1 | +0.0897 | +0.2054 | +0.2038 | 0.0000 | +0.7701 | +0.8035 | 0.799 |
| `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio` | +1 | +0.0421 | +0.2002 | +0.2033 | 0.0000 | +0.6265 | +0.7144 | 0.124 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0538 | +0.1928 | +0.1935 | 0.0000 | +0.6003 | +0.7349 | 0.784 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +1 | +0.0993 | +0.1570 | +0.1561 | 0.0036 | +0.5103 | +0.6786 | 0.734 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0720 | +0.1466 | +0.1457 | 0.0058 | +0.5884 | +0.7349 | 0.723 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +1 | +0.0702 | +0.1277 | +0.1278 | 0.0154 | +0.6295 | +0.7455 | 0.067 |

### 50ETF / single
No features admitted.

### 500ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1906 | +0.3397 | +0.3393 | 0.0000 | +1.0529 | +0.8358 | 0.000 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.2028 | +0.3327 | +0.3325 | 0.0000 | +0.8965 | +0.7965 | 0.485 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1864 | +0.3278 | +0.3273 | 0.0000 | +0.7514 | +0.7625 | 0.735 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | +1 | +0.1560 | +0.3274 | +0.3260 | 0.0000 | +0.7803 | +0.7760 | 0.647 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1300 | +0.2789 | +0.2783 | 0.0000 | +0.6204 | +0.7126 | 0.762 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +1 | +0.1889 | +0.2749 | +0.2743 | 0.0000 | +0.9765 | +0.7777 | 0.800 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +1 | +0.1702 | +0.2721 | +0.2709 | 0.0000 | +0.8193 | +0.7912 | 0.768 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +1 | +0.1640 | +0.2664 | +0.2657 | 0.0000 | +0.6667 | +0.7331 | 0.772 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +1 | +0.1499 | +0.2642 | +0.2624 | 0.0000 | +0.9245 | +0.8188 | 0.233 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | +1 | +0.0827 | +0.2636 | +0.2642 | 0.0000 | +0.6985 | +0.7478 | 0.420 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1583 | +0.2552 | +0.2542 | 0.0000 | +0.7886 | +0.7695 | 0.725 |
| `combo_max__max_up_ret__early_body_momentum` | +1 | +0.1472 | +0.2549 | +0.2541 | 0.0000 | +0.9093 | +0.8047 | 0.788 |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.1001 | +0.2254 | +0.2258 | 0.0002 | +0.6393 | +0.7067 | 0.603 |
| `combo_ratio__max_down_ret__net_volume_flow` | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0002 | +0.8478 | +0.7883 | 0.094 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | +1 | +0.1384 | +0.2185 | +0.2177 | 0.0004 | +0.7354 | +0.7525 | 0.085 |
| `combo_max__bar_ret_0__max_down_ret` | +1 | +0.1655 | +0.2083 | +0.2078 | 0.0006 | +0.6179 | +0.7144 | 0.710 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +1 | +0.1432 | +0.2059 | +0.2050 | 0.0006 | +0.5352 | +0.6674 | 0.651 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0006 | +0.3439 | +0.6633 | 0.646 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.0772 | +0.1732 | +0.1723 | 0.0016 | +0.4734 | +0.6551 | 0.604 |
| `vwap_trend_channel_slope` | +1 | +0.1023 | +0.1640 | +0.1634 | 0.0028 | +0.4395 | +0.6727 | 0.718 |

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__high_low_sequence_momentum__volume_weighted_momentum_acceleration` | +1 | +0.1393 | +0.3122 | +0.3111 | 0.0000 | +0.9238 | +0.8203 | 0.000 |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.720 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0002 | +0.8649 | +0.7779 | 0.657 |
| `max_up_ret` | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0046 | +0.6051 | +0.7266 | 0.704 |

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1383 | +0.2945 | +0.2928 | 0.0000 | +0.6026 | +0.7202 | 0.000 |
| `combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1457 | +0.2920 | +0.2899 | 0.0000 | +0.4787 | +0.6628 | 0.541 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1452 | +0.2637 | +0.2612 | 0.0000 | +0.5523 | +0.6962 | 0.799 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1739 | +0.2614 | +0.2594 | 0.0000 | +0.7322 | +0.7390 | 0.793 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1769 | +0.2559 | +0.2535 | 0.0000 | +0.7561 | +0.7654 | 0.790 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0909 | +0.2510 | +0.2513 | 0.0000 | +0.5263 | +0.6962 | 0.610 |
| `combo_rank_max__max_up_ret__bar_ret_0` | +1 | +0.1441 | +0.2252 | +0.2233 | 0.0000 | +0.4877 | +0.6956 | 0.788 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1034 | +0.1683 | +0.1674 | 0.0024 | +0.4694 | +0.6950 | 0.100 |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio` | `product` | a=`smooth_momentum_structure`, b=`opening_drive_thrust_ratio` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `rel_diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__max_up_ret__early_body_momentum` | `max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_ratio__max_down_ret__net_volume_flow` | `ratio` | a=`max_down_ret`, b=`net_volume_flow` |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | `ratio` | a=`max_down_ret`, b=`volatility_expansion_trend_vector` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `min` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_rel_diff__high_low_sequence_momentum__volume_weighted_momentum_acceleration` | `rel_diff` | a=`high_low_sequence_momentum`, b=`volume_weighted_momentum_acceleration` |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | `diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | `sig_product` | a=`high_low_sequence_momentum`, b=`vwap_trend_channel_slope` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`first_bar_sentiment`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
