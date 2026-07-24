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
| 300ETF | single | 1,369 | 327 | 249 | 237 | 41 | 41 | 40 | 13 | 13 |
| 300ETF | long | 579 | 40 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 586 | 93 | 26 | 5 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 737 | 33 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 361 | 46 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 317 | 39 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 2,836 | 1,156 | 1,052 | 1,043 | 609 | 493 | 493 | 32 | 32 |
| 500ETF | long | 1,360 | 108 | 62 | 29 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 426 | 54 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,742 | 623 | 449 | 445 | 166 | 166 | 166 | 25 | 25 |
| 159915ETF | long | 1,121 | 108 | 48 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 302 | 47 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 13 | +0.1230 | [+0.0794, +0.1657] | +0.2715 | [+0.1598, +0.3635] | +0.9879 | 7.66% | 1.7894 | 4.57% | 1.0814 | 2.2164 | 6.34% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 32 | +0.1968 | [+0.1528, +0.2434] | +0.3187 | [+0.2274, +0.4089] | +0.9636 | 10.41% | 2.0223 | 7.53% | 1.4759 | 3.0649 | 4.76% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 25 | +0.1663 | [+0.1197, +0.2110] | +0.2697 | [+0.1915, +0.3601] | +0.9636 | 9.01% | 1.6274 | 6.20% | 1.1238 | 1.7748 | 9.92% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 13 | +0.0691* | [-0.0023, +0.1353] | +0.1448* | [-0.0268, +0.3088] | +0.7939 | 3.31% | 0.8005 | 0.29% | 0.0702 | 0.1137 | 4.70% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 32 | +0.1230 | [+0.0476, +0.1901] | +0.1329* | [-0.0194, +0.2688] | +0.7818 | 4.67% | 0.9634 | 2.00% | 0.4153 | 0.7853 | 5.65% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 25 | +0.1472 | [+0.0657, +0.2140] | +0.2807 | [+0.0986, +0.4535] | +0.6848 | 10.12% | 1.5168 | 7.55% | 1.1382 | 2.9536 | 6.93% |
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
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | +1 | +0.1716 | +0.3006 | +0.3024 | 0.0000 | +1.2000 | +0.8896 | 0.824 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1850 | +0.2963 | +0.2976 | 0.0000 | +0.8309 | +0.7858 | 0.733 |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | +1 | +0.1310 | +0.2956 | +0.2974 | 0.0000 | +0.7405 | +0.7406 | 0.842 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1712 | +0.2881 | +0.2898 | 0.0000 | +0.6248 | +0.7345 | 0.833 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1458 | +0.2828 | +0.2845 | 0.0000 | +0.5522 | +0.6913 | 0.806 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | +1 | +0.1590 | +0.2814 | +0.2830 | 0.0000 | +0.9932 | +0.8356 | 0.837 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1685 | +0.2784 | +0.2795 | 0.0000 | +0.8171 | +0.7771 | 0.835 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +1 | +0.1585 | +0.2753 | +0.2774 | 0.0000 | +0.8773 | +0.7925 | 0.849 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1484 | +0.2722 | +0.2732 | 0.0000 | +0.7569 | +0.7494 | 0.598 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1206 | +0.2718 | +0.2735 | 0.0000 | +0.6700 | +0.7339 | 0.832 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +1 | +0.1602 | +0.2716 | +0.2730 | 0.0000 | +0.6443 | +0.7339 | 0.819 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | +1 | +0.1795 | +0.2710 | +0.2723 | 0.0000 | +0.8204 | +0.7576 | 0.809 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +1 | +0.1722 | +0.2634 | +0.2648 | 0.0000 | +0.8527 | +0.7463 | 0.827 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1405 | +0.2602 | +0.2611 | 0.0000 | +0.7573 | +0.7524 | 0.808 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +1 | +0.1749 | +0.2498 | +0.2510 | 0.0000 | +1.0192 | +0.7910 | 0.840 |
| `combo_min__max_up_ret__first_bar_sentiment` | +1 | +0.1702 | +0.2494 | +0.2501 | 0.0000 | +0.8348 | +0.7920 | 0.829 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1269 | +0.2448 | +0.2467 | 0.0000 | +0.7120 | +0.7350 | 0.837 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +1 | +0.1401 | +0.2373 | +0.2394 | 0.0000 | +0.6639 | +0.7278 | 0.848 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +1 | +0.1595 | +0.2337 | +0.2357 | 0.0000 | +0.5864 | +0.7581 | 0.837 |
| `combo_max__max_up_ret__first_bar_sentiment` | +1 | +0.1626 | +0.2336 | +0.2356 | 0.0000 | +0.5429 | +0.7370 | 0.842 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | +1 | +0.1362 | +0.2270 | +0.2286 | 0.0000 | +0.5799 | +0.7108 | 0.823 |
| `combo_min__first_bar_sentiment__bar_ret_0` | +1 | +0.1456 | +0.2246 | +0.2260 | 0.0000 | +0.7255 | +0.7483 | 0.837 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +1 | +0.1323 | +0.2100 | +0.2111 | 0.0000 | +0.4841 | +0.7026 | 0.813 |
| `combo_max__bar_ret_0__max_down_ret` | +1 | +0.1553 | +0.2082 | +0.2102 | 0.0000 | +0.6159 | +0.7093 | 0.812 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1369 | +0.2008 | +0.2010 | 0.0000 | +0.3612 | +0.6595 | 0.642 |
| `combo_sig_product__max_up_ret__body_size_progression` | +1 | +0.1454 | +0.1907 | +0.1915 | 0.0004 | +0.7799 | +0.7447 | 0.837 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +1 | +0.1603 | +0.1690 | +0.1706 | 0.0008 | +0.5264 | +0.7201 | 0.692 |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | +1 | +0.1119 | +0.1425 | +0.1442 | 0.0042 | +0.3291 | +0.6523 | 0.092 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | +1 | +0.1495 | +0.3073 | +0.3087 | 0.0000 | +0.6968 | +0.7524 | 0.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1603 | +0.2856 | +0.2869 | 0.0000 | +0.7388 | +0.7637 | 0.621 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | +1 | +0.1430 | +0.2817 | +0.2823 | 0.0000 | +0.6313 | +0.7031 | 0.778 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +1 | +0.1201 | +0.2807 | +0.2815 | 0.0000 | +0.7668 | +0.7596 | 0.764 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1072 | +0.2737 | +0.2745 | 0.0000 | +0.6264 | +0.7252 | 0.537 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1649 | +0.2700 | +0.2713 | 0.0000 | +0.5602 | +0.6857 | 0.817 |
| `combo_min__max_up_ret__impulse_bar_dominance` | +1 | +0.0909 | +0.2696 | +0.2710 | 0.0000 | +0.3947 | +0.6513 | 0.742 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1078 | +0.2695 | +0.2704 | 0.0000 | +0.6281 | +0.7396 | 0.826 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | +1 | +0.1414 | +0.2667 | +0.2676 | 0.0000 | +0.6223 | +0.7268 | 0.832 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +1 | +0.1383 | +0.2594 | +0.2608 | 0.0000 | +0.4770 | +0.6872 | 0.836 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +1 | +0.1388 | +0.2579 | +0.2588 | 0.0000 | +0.6302 | +0.7216 | 0.837 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.1209 | +0.2521 | +0.2540 | 0.0000 | +0.6452 | +0.7524 | 0.820 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1449 | +0.2469 | +0.2484 | 0.0000 | +0.5975 | +0.7124 | 0.839 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | +1 | +0.1227 | +0.2414 | +0.2425 | 0.0000 | +0.7115 | +0.7447 | 0.818 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1277 | +0.2309 | +0.2327 | 0.0000 | +0.6392 | +0.7781 | 0.845 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | +1 | +0.1333 | +0.2304 | +0.2324 | 0.0000 | +0.4497 | +0.6872 | 0.817 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | +1 | +0.1082 | +0.2293 | +0.2309 | 0.0000 | +0.6863 | +0.7365 | 0.828 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.1455 | +0.2279 | +0.2282 | 0.0000 | +0.6028 | +0.7011 | 0.746 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1127 | +0.2132 | +0.2142 | 0.0000 | +0.5873 | +0.6959 | 0.726 |
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
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `rank_min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`opening_auction_imbalance` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | `min` | a=`opening_auction_imbalance`, b=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | `rel_diff` | a=`opening_auction_imbalance`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | `rank_min` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_max__close_vs_open_range__first_bar_sentiment` | `max` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_min__first_bar_sentiment__bar_ret_0` | `min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | `ratio` | a=`bar_ret_0`, b=`opening_auction_imbalance` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__impulse_bar_dominance` | `min` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__star50_limit_proximity_early__first_bar_return` | `min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | `min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`yesterday_early_momentum`, c=`yesterday_first_30min_return` |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | `rank_max` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | `ratio` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`first_bar_sentiment`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | `clamp_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | `z_sum` | a=`rbreaker_buy_setup_proximity_early`, b=`impulse_bar_dominance` |
