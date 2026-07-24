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

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1,446 | 404 | 326 | 314 | 46 | 46 | 45 | 14 | 14 |
| 300ETF | long | 579 | 40 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 586 | 93 | 26 | 5 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 738 | 34 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 361 | 46 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 317 | 39 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 2,865 | 1,185 | 1,081 | 1,071 | 614 | 497 | 497 | 32 | 32 |
| 500ETF | long | 1,360 | 108 | 62 | 29 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 426 | 54 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,830 | 710 | 537 | 530 | 198 | 198 | 198 | 27 | 27 |
| 159915ETF | long | 1,121 | 108 | 48 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 302 | 47 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 14 | +0.1230 | [+0.0798, +0.1660] | +0.2631 | [+0.1513, +0.3549] | +1.0000 | 7.60% | 1.7534 | 4.52% | 1.0542 | 2.1817 | 6.45% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 32 | +0.1974 | [+0.1530, +0.2439] | +0.3155 | [+0.2287, +0.4029] | +0.9515 | 10.29% | 2.0769 | 7.36% | 1.4993 | 3.1331 | 4.93% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 27 | +0.1688 | [+0.1229, +0.2130] | +0.2724 | [+0.1920, +0.3639] | +0.8909 | 8.66% | 1.5691 | 5.90% | 1.0731 | 1.6603 | 10.20% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 14 | +0.0701* | [-0.0023, +0.1370] | +0.1500* | [-0.0234, +0.3099] | +0.7697 | 3.33% | 0.7883 | 0.32% | 0.0755 | 0.1209 | 4.68% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 32 | +0.1232 | [+0.0481, +0.1892] | +0.1211* | [-0.0358, +0.2618] | +0.7818 | 4.80% | 1.0847 | 2.13% | 0.4830 | 0.8958 | 4.25% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 27 | +0.1446 | [+0.0623, +0.2109] | +0.2839 | [+0.0965, +0.4528] | +0.6970 | 10.34% | 1.5519 | 7.84% | 1.1833 | 3.1252 | 6.98% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +1 | +0.1225 | +0.2852 | +0.2860 | 0.0000 | +0.7955 | +0.7966 | 0.000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1151 | +0.2780 | +0.2785 | 0.0000 | +0.5798 | +0.7129 | 0.832 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1119 | +0.2634 | +0.2636 | 0.0000 | +0.6357 | +0.7155 | 0.814 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1133 | +0.2620 | +0.2629 | 0.0000 | +0.6530 | +0.6965 | 0.823 |
| `combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | +1 | +0.1130 | +0.2358 | +0.2372 | 0.0000 | +0.8119 | +0.7663 | 0.848 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +1 | +0.0872 | +0.2244 | +0.2251 | 0.0000 | +0.7215 | +0.7571 | 0.643 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0965 | +0.2243 | +0.2248 | 0.0000 | +0.5652 | +0.7360 | 0.797 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +1 | +0.0742 | +0.1929 | +0.1930 | 0.0004 | +0.4284 | +0.6718 | 0.520 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0660 | +0.1858 | +0.1864 | 0.0004 | +0.6574 | +0.7488 | 0.592 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +1 | +0.0917 | +0.1836 | +0.1849 | 0.0006 | +0.5672 | +0.7304 | 0.730 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | +1 | +0.0833 | +0.1830 | +0.1846 | 0.0006 | +0.6883 | +0.7576 | 0.729 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | +1 | +0.1095 | +0.1599 | +0.1610 | 0.0016 | +0.4455 | +0.6769 | 0.817 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +1 | +0.0680 | +0.1333 | +0.1336 | 0.0102 | +0.5209 | +0.7216 | 0.060 |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +1 | +0.0386 | +0.1171 | +0.1177 | 0.0248 | +0.4654 | +0.6918 | 0.427 |

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

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1763 | +0.3308 | +0.3324 | 0.0000 | +1.1222 | +0.8567 | 0.000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1544 | +0.3080 | +0.3099 | 0.0000 | +0.9530 | +0.8187 | 0.810 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +1 | +0.1634 | +0.3074 | +0.3082 | 0.0000 | +0.9093 | +0.7966 | 0.721 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1736 | +0.3067 | +0.3077 | 0.0000 | +0.7113 | +0.7483 | 0.807 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +1 | +0.1641 | +0.3025 | +0.3043 | 0.0000 | +0.7337 | +0.7807 | 0.646 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | +1 | +0.1716 | +0.3006 | +0.3024 | 0.0000 | +1.2000 | +0.8896 | 0.824 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1850 | +0.2963 | +0.2976 | 0.0000 | +0.8309 | +0.7858 | 0.757 |
| `combo_min__max_up_ret__first_bar_sentiment` | +1 | +0.1702 | +0.2962 | +0.2969 | 0.0000 | +0.8348 | +0.7920 | 0.734 |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | +1 | +0.1310 | +0.2956 | +0.2974 | 0.0000 | +0.7405 | +0.7406 | 0.842 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1685 | +0.2912 | +0.2924 | 0.0000 | +0.8171 | +0.7771 | 0.800 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.1444 | +0.2888 | +0.2898 | 0.0000 | +0.7221 | +0.7720 | 0.774 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1712 | +0.2881 | +0.2898 | 0.0000 | +0.6248 | +0.7345 | 0.835 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1458 | +0.2828 | +0.2845 | 0.0000 | +0.5522 | +0.6913 | 0.806 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | +1 | +0.1590 | +0.2814 | +0.2830 | 0.0000 | +0.9932 | +0.8356 | 0.837 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +1 | +0.1585 | +0.2753 | +0.2774 | 0.0000 | +0.8773 | +0.7925 | 0.849 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1484 | +0.2722 | +0.2732 | 0.0000 | +0.7569 | +0.7494 | 0.598 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1206 | +0.2718 | +0.2735 | 0.0000 | +0.6700 | +0.7339 | 0.832 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +1 | +0.1602 | +0.2716 | +0.2730 | 0.0000 | +0.6443 | +0.7339 | 0.819 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | +1 | +0.1795 | +0.2710 | +0.2723 | 0.0000 | +0.8204 | +0.7576 | 0.809 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +1 | +0.1722 | +0.2634 | +0.2648 | 0.0000 | +0.8527 | +0.7463 | 0.827 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1405 | +0.2602 | +0.2611 | 0.0000 | +0.7573 | +0.7524 | 0.808 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +1 | +0.1749 | +0.2498 | +0.2510 | 0.0000 | +1.0192 | +0.7910 | 0.840 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1269 | +0.2448 | +0.2467 | 0.0000 | +0.7120 | +0.7350 | 0.837 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +1 | +0.1401 | +0.2373 | +0.2394 | 0.0000 | +0.6639 | +0.7278 | 0.848 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +1 | +0.1595 | +0.2337 | +0.2357 | 0.0000 | +0.5864 | +0.7581 | 0.837 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | +1 | +0.1362 | +0.2270 | +0.2286 | 0.0000 | +0.5799 | +0.7108 | 0.823 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +1 | +0.1323 | +0.2100 | +0.2111 | 0.0000 | +0.4841 | +0.7026 | 0.813 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1369 | +0.2008 | +0.2010 | 0.0000 | +0.3612 | +0.6595 | 0.642 |
| `combo_sig_product__max_up_ret__body_size_progression` | +1 | +0.1454 | +0.1907 | +0.1915 | 0.0004 | +0.7799 | +0.7447 | 0.837 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +1 | +0.1603 | +0.1690 | +0.1706 | 0.0008 | +0.5264 | +0.7201 | 0.692 |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | +1 | +0.1119 | +0.1425 | +0.1442 | 0.0042 | +0.3291 | +0.6523 | 0.092 |
| `combo_sig_product__rsi_opening__max_down_ret` | +1 | +0.1200 | +0.1380 | +0.1398 | 0.0060 | +0.4859 | +0.6929 | 0.821 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | +1 | +0.1495 | +0.3073 | +0.3087 | 0.0000 | +0.6968 | +0.7524 | 0.000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1569 | +0.2946 | +0.2960 | 0.0000 | +0.7050 | +0.7519 | 0.742 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1603 | +0.2856 | +0.2869 | 0.0000 | +0.7388 | +0.7637 | 0.841 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | +1 | +0.1430 | +0.2817 | +0.2823 | 0.0000 | +0.6313 | +0.7031 | 0.778 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1072 | +0.2737 | +0.2745 | 0.0000 | +0.6264 | +0.7252 | 0.537 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1449 | +0.2723 | +0.2738 | 0.0000 | +0.5975 | +0.7124 | 0.770 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1535 | +0.2700 | +0.2715 | 0.0000 | +0.5912 | +0.6816 | 0.847 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1078 | +0.2695 | +0.2704 | 0.0000 | +0.6281 | +0.7396 | 0.826 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | +1 | +0.1414 | +0.2667 | +0.2676 | 0.0000 | +0.6223 | +0.7268 | 0.832 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +1 | +0.1201 | +0.2628 | +0.2636 | 0.0000 | +0.7668 | +0.7596 | 0.764 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +1 | +0.1617 | +0.2610 | +0.2618 | 0.0000 | +0.6758 | +0.7797 | 0.843 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +1 | +0.1383 | +0.2594 | +0.2608 | 0.0000 | +0.4770 | +0.6872 | 0.848 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1695 | +0.2560 | +0.2568 | 0.0000 | +0.6178 | +0.7124 | 0.847 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.1209 | +0.2521 | +0.2540 | 0.0000 | +0.6452 | +0.7524 | 0.820 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | +1 | +0.1227 | +0.2414 | +0.2425 | 0.0000 | +0.7115 | +0.7447 | 0.818 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.1379 | +0.2318 | +0.2337 | 0.0000 | +0.6385 | +0.7309 | 0.837 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1277 | +0.2309 | +0.2327 | 0.0000 | +0.6392 | +0.7781 | 0.848 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | +1 | +0.1082 | +0.2293 | +0.2309 | 0.0000 | +0.6863 | +0.7365 | 0.828 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.1455 | +0.2279 | +0.2282 | 0.0000 | +0.6028 | +0.7011 | 0.796 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1127 | +0.2132 | +0.2142 | 0.0000 | +0.5873 | +0.6959 | 0.726 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +1 | +0.1175 | +0.2049 | +0.2070 | 0.0000 | +0.4553 | +0.6888 | 0.841 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +1 | +0.1211 | +0.2014 | +0.2022 | 0.0000 | +0.5715 | +0.7016 | 0.841 |
| `combo_min__max_up_ret__bar_body_rng_0` | +1 | +0.1380 | +0.1996 | +0.2007 | 0.0000 | +0.3699 | +0.6420 | 0.839 |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | +1 | +0.1212 | +0.1984 | +0.2000 | 0.0000 | +0.4217 | +0.6713 | 0.834 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1275 | +0.1899 | +0.1909 | 0.0002 | +0.4426 | +0.6117 | 0.814 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | +1 | +0.1201 | +0.1799 | +0.1813 | 0.0004 | +0.3379 | +0.6235 | 0.820 |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | +1 | +0.1010 | +0.1423 | +0.1439 | 0.0042 | +0.3506 | +0.6636 | 0.850 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `rank_min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`opening_auction_imbalance` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | `min` | a=`opening_auction_imbalance`, b=`star50_limit_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | `rel_diff` | a=`opening_auction_imbalance`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_max__close_vs_open_range__first_bar_sentiment` | `max` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | `ratio` | a=`bar_ret_0`, b=`opening_auction_imbalance` |
| `combo_sig_product__rsi_opening__max_down_ret` | `sig_product` | a=`rsi_opening`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__star50_limit_proximity_early__first_bar_return` | `min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | `min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`yesterday_early_momentum`, c=`yesterday_first_30min_return` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | `rank_max` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | `ratio` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`first_bar_sentiment`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | `clamp_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | `z_sum` | a=`rbreaker_buy_setup_proximity_early`, b=`impulse_bar_dominance` |
