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
| 300ETF | single | 1,574 | 535 | 295 | 171 | 169 | 112 | 112 | 112 | 16 | 11 |
| 50ETF | single | 1,244 | 514 | 437 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,229 | 1,646 | 1,324 | 1,075 | 1,064 | 788 | 537 | 537 | 20 | 20 |
| 588000ETF | single | 1,585 | 1,018 | 693 | 539 | 501 | 31 | 31 | 31 | 6 | 4 |
| 159915ETF | single | 1,888 | 760 | 378 | 337 | 332 | 64 | 64 | 64 | 9 | 8 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.1391 | [+0.0902, +0.1849] | +0.2604 | [+0.1410, +0.3617] | +0.9636 | 7.66% | 1.7372 | 5.96% | 1.3725 | 2.8094 | 6.32% |
| 500ETF | single | 20 | +0.2180 | [+0.1714, +0.2637] | +0.3425 | [+0.2368, +0.4427] | +0.9030 | 10.51% | 2.2195 | 8.98% | 1.9236 | 4.2698 | 3.74% |
| 588000ETF | single | 4 | +0.1435 | [+0.0808, +0.2043] | +0.3393 | [+0.1938, +0.4389] | +0.8909 | 8.90% | 1.7154 | 7.27% | 1.4207 | 3.3250 | 5.10% |
| 159915ETF | single | 8 | +0.1776 | [+0.1311, +0.2210] | +0.2663 | [+0.1819, +0.3571] | +0.9879 | 8.47% | 1.2102 | 6.91% | 0.9913 | 1.3497 | 13.99% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0600* | [-0.0079, +0.1204] | +0.1555 | [+0.0058, +0.2893] | +0.6970 | 3.32% | 0.8431 | 1.63% | 0.4176 | 0.6626 | 4.23% |
| 500ETF | single | 20 | +0.1130 | [+0.0527, +0.1695] | +0.0930* | [-0.0530, +0.2098] | +0.8667 | 1.86% | 0.5245 | 0.79% | 0.2245 | 0.3565 | 4.27% |
| 588000ETF | single | 4 | -0.0068* | [-0.1105, +0.0775] | -0.0230* | [-0.2659, +0.2163] | -0.0182 | -2.41% | -0.4120 | -4.04% | -0.6867 | -0.9244 | 12.62% |
| 159915ETF | single | 8 | +0.1407 | [+0.0698, +0.1997] | +0.2770 | [+0.1178, +0.4056] | +0.7333 | 10.20% | 1.6040 | 8.84% | 1.4062 | 3.6946 | 5.70% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0167* | [-0.0776, +0.1009] | +0.0542* | [-0.1577, +0.2460] | +0.3939 | 2.03% | 0.4168 | 0.34% | 0.0712 | 0.1130 | 5.90% |
| 500ETF | single | 20 | +0.1294 | [+0.0497, +0.2011] | +0.0565* | [-0.1376, +0.2245] | +0.9152 | 1.54% | 0.4697 | 0.48% | 0.1451 | 0.2294 | 2.75% |
| 588000ETF | single | 4 | -0.0531* | [-0.1599, +0.0669] | -0.0072* | [-0.2822, +0.2911] | -0.0788 | -2.27% | -0.3697 | -3.92% | -0.6343 | -0.8603 | 9.80% |
| 159915ETF | single | 8 | +0.1480 | [+0.0503, +0.2345] | +0.2986 | [+0.0600, +0.4944] | +0.5152 | 13.54% | 1.6982 | 12.21% | 1.5491 | 4.6012 | 6.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +1 | +0.1365 | +0.2874 | +0.2868 | 0.0000 | +0.8181 | +0.8088 | 0.858 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1222 | +0.2667 | +0.2669 | 0.0000 | +0.6787 | +0.7103 | 0.711 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1164 | +0.2660 | +0.2658 | 0.0000 | +0.6109 | +0.7003 | 0.703 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | +1 | +0.1053 | +0.2522 | +0.2513 | 0.0000 | +0.6153 | +0.7138 | 0.709 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.794 |
| `combo_product__volume_weighted_momentum_acceleration__opening_drive_thrust_ratio` | +1 | +0.0390 | +0.1992 | +0.2027 | 0.0000 | +0.6601 | +0.7050 | 0.975 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0538 | +0.1928 | +0.1935 | 0.0000 | +0.6003 | +0.7349 | 0.784 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +1 | +0.0999 | +0.1898 | +0.1897 | 0.0000 | +0.6533 | +0.7496 | 0.815 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | +1 | +0.0888 | +0.1816 | +0.1799 | 0.0006 | +0.6717 | +0.7566 | 0.787 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0720 | +0.1466 | +0.1457 | 0.0058 | +0.5884 | +0.7349 | 0.733 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +1 | +0.0702 | +0.1277 | +0.1278 | 0.0154 | +0.6295 | +0.7455 | 0.064 |

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
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.720 |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | +1 | +0.1329 | +0.2836 | +0.2825 | 0.0000 | +0.8900 | +0.7947 | 0.915 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0002 | +0.8649 | +0.7779 | 0.730 |
| `max_up_ret` | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0046 | +0.6051 | +0.7266 | 0.728 |

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1383 | +0.2945 | +0.2928 | 0.0000 | +0.6026 | +0.7202 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1766 | +0.2917 | +0.2894 | 0.0000 | +0.6974 | +0.7384 | 0.781 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1502 | +0.2885 | +0.2864 | 0.0000 | +0.5040 | +0.6598 | 0.738 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1452 | +0.2637 | +0.2612 | 0.0000 | +0.5523 | +0.6962 | 0.799 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | +1 | +0.1678 | +0.2557 | +0.2535 | 0.0000 | +0.4950 | +0.6563 | 0.793 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1075 | +0.2449 | +0.2443 | 0.0000 | +0.7396 | +0.7818 | 0.871 |
| `combo_max__max_up_ret__first_bar_return` | +1 | +0.1444 | +0.2224 | +0.2203 | 0.0000 | +0.5050 | +0.7062 | 0.751 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1034 | +0.1683 | +0.1674 | 0.0024 | +0.4694 | +0.6950 | 0.105 |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_product__volume_weighted_momentum_acceleration__opening_drive_thrust_ratio` | `product` | a=`volume_weighted_momentum_acceleration`, b=`opening_drive_thrust_ratio` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
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
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | `diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `diff` | a=`trend_day_regime_conviction`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | `sig_product` | a=`high_low_sequence_momentum`, b=`vwap_trend_channel_slope` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_return` |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | `z_sum` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_max__max_up_ret__first_bar_return` | `max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
