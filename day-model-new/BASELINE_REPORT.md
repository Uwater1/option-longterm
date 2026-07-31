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
| 300ETF | single | 1,573 | 534 | 294 | 170 | 168 | 111 | 111 | 111 | 17 | 13 |
| 300ETF | long | 623 | 68 | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 444 | 71 | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 1,244 | 514 | 437 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 524 | 73 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 330 | 53 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,061 | 1,571 | 1,261 | 1,006 | 995 | 745 | 527 | 527 | 43 | 19 |
| 500ETF | long | 1,140 | 186 | 89 | 89 | 36 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 428 | 72 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 588000ETF | single | 1,585 | 1,018 | 693 | 539 | 501 | 31 | 31 | 31 | 6 | 4 |
| 588000ETF | long | 647 | 226 | 29 | 29 | 3 | 0 | 0 | 0 | 0 | 0 |
| 588000ETF | short | 772 | 287 | 64 | 64 | 12 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,888 | 760 | 378 | 337 | 332 | 64 | 64 | 64 | 9 | 8 |
| 159915ETF | long | 742 | 91 | 24 | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 356 | 70 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 13 | +0.1370 | [+0.0907, +0.1813] | +0.2178 | [+0.0934, +0.3258] | +0.9152 | 6.16% | 1.5418 | 4.47% | 1.1339 | 2.0660 | 5.22% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 19 | +0.2182 | [+0.1710, +0.2622] | +0.3299 | [+0.2240, +0.4381] | +0.9394 | 10.34% | 2.0282 | 8.81% | 1.7490 | 3.8249 | 4.47% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 4 | +0.1435 | [+0.0808, +0.2043] | +0.3393 | [+0.1938, +0.4389] | +0.8909 | 8.90% | 1.7154 | 7.27% | 1.4207 | 3.3250 | 5.10% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.1776 | [+0.1311, +0.2210] | +0.2663 | [+0.1819, +0.3571] | +0.9879 | 8.47% | 1.2102 | 6.91% | 0.9913 | 1.3497 | 13.99% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 13 | +0.0688 | [+0.0008, +0.1327] | +0.1744 | [+0.0179, +0.3016] | +0.6727 | 3.77% | 1.0834 | 2.13% | 0.6179 | 1.1581 | 3.22% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 19 | +0.1170 | [+0.0555, +0.1707] | +0.0902* | [-0.0488, +0.2019] | +0.8667 | 2.12% | 0.5724 | 1.14% | 0.3079 | 0.5024 | 4.55% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 4 | -0.0068* | [-0.1105, +0.0775] | -0.0230* | [-0.2659, +0.2163] | -0.0182 | -2.41% | -0.4120 | -4.04% | -0.6867 | -0.9244 | 12.62% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.1407 | [+0.0698, +0.1997] | +0.2770 | [+0.1178, +0.4056] | +0.7333 | 10.20% | 1.6040 | 8.84% | 1.4062 | 3.6946 | 5.70% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 13 | +0.0215* | [-0.0705, +0.1172] | +0.0658* | [-0.1447, +0.2452] | +0.3939 | 2.91% | 0.7186 | 1.29% | 0.3203 | 0.6375 | 4.15% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 19 | +0.1301 | [+0.0514, +0.2020] | +0.0467* | [-0.1438, +0.2248] | +0.8424 | 2.13% | 0.5928 | 1.15% | 0.3197 | 0.5572 | 2.93% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 4 | -0.0531* | [-0.1599, +0.0669] | -0.0072* | [-0.2822, +0.2911] | -0.0788 | -2.27% | -0.3697 | -3.92% | -0.6343 | -0.8603 | 9.80% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.1480 | [+0.0503, +0.2345] | +0.2986 | [+0.0600, +0.4944] | +0.5152 | 13.54% | 1.6982 | 12.21% | 1.5491 | 4.6012 | 6.00% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Cluster 3 | +1 | +0.1365 | +0.2874 | +0.2868 | 0.0000 | +0.8181 | +0.8088 | 0.858 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 3 | +1 | +0.1222 | +0.2667 | +0.2669 | 0.0000 | +0.6787 | +0.7103 | 0.711 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 3 | +1 | +0.1164 | +0.2660 | +0.2658 | 0.0000 | +0.6109 | +0.7003 | 0.703 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Cluster 2 | +1 | +0.1053 | +0.2522 | +0.2513 | 0.0000 | +0.6153 | +0.7138 | 0.709 |
| `rbreaker_sell_setup_proximity_early` | Cluster 3 | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.794 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Cluster 2 | +1 | +0.0999 | +0.1898 | +0.1897 | 0.0000 | +0.6533 | +0.7496 | 0.815 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 1 | +1 | +0.0777 | +0.1863 | +0.1849 | 0.0004 | +0.7183 | +0.7760 | 0.744 |
| `combo_mean__max_up_ret__volume_surge_direction` | Cluster 2 | +1 | +0.0944 | +0.1816 | +0.1804 | 0.0006 | +0.6499 | +0.7284 | 0.788 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 0 | +1 | +0.0888 | +0.1816 | +0.1799 | 0.0006 | +0.6717 | +0.7566 | 0.787 |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | Cluster 2 | +1 | +0.0839 | +0.1600 | +0.1586 | 0.0026 | +0.4471 | +0.6680 | 0.715 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Cluster 0 | +1 | +0.0993 | +0.1570 | +0.1561 | 0.0036 | +0.5103 | +0.6786 | 0.734 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Cluster 1 | +1 | +0.0720 | +0.1466 | +0.1457 | 0.0058 | +0.5884 | +0.7349 | 0.733 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Cluster 2 | +1 | +0.0702 | +0.1277 | +0.1278 | 0.0154 | +0.6295 | +0.7455 | 0.064 |

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

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 3 | +1 | +0.1864 | +0.3278 | +0.3273 | 0.0000 | +0.7514 | +0.7625 | 0.000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 1 | +1 | +0.1685 | +0.2940 | +0.2932 | 0.0000 | +0.7752 | +0.7988 | 0.959 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Cluster 1 | +1 | +0.1500 | +0.2835 | +0.2832 | 0.0000 | +0.8380 | +0.7607 | 0.622 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | Cluster 1 | +1 | +0.1953 | +0.2768 | +0.2765 | 0.0000 | +1.0438 | +0.8299 | 0.923 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Cluster 1 | +1 | +0.1889 | +0.2752 | +0.2746 | 0.0000 | +0.9765 | +0.7777 | 0.797 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Cluster 3 | +1 | +0.1770 | +0.2748 | +0.2744 | 0.0000 | +0.7230 | +0.7507 | 0.905 |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | Cluster 0 | +1 | +0.1360 | +0.2742 | +0.2735 | 0.0000 | +0.7025 | +0.7566 | 0.836 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Cluster 3 | +1 | +0.1640 | +0.2669 | +0.2662 | 0.0000 | +0.6667 | +0.7331 | 0.772 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Cluster 0 | +1 | +0.1499 | +0.2642 | +0.2624 | 0.0000 | +0.9245 | +0.8188 | 0.232 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | Cluster 4 | +1 | +0.0827 | +0.2636 | +0.2642 | 0.0000 | +0.6985 | +0.7478 | 0.420 |
| `combo_ratio__max_down_ret__net_volume_flow` | Cluster 0 | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0002 | +0.8478 | +0.7883 | 0.093 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Cluster 3 | +1 | +0.1317 | +0.2190 | +0.2185 | 0.0004 | +0.6178 | +0.7437 | 0.918 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | Cluster 0 | +1 | +0.1384 | +0.2185 | +0.2177 | 0.0004 | +0.7354 | +0.7525 | 0.099 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Cluster 3 | +1 | +0.1432 | +0.2059 | +0.2050 | 0.0006 | +0.5352 | +0.6674 | 0.783 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Cluster 3 | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0006 | +0.3439 | +0.6633 | 0.628 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Cluster 4 | +1 | +0.0926 | +0.1951 | +0.1951 | 0.0008 | +0.7041 | +0.7525 | 0.916 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Cluster 1 | +1 | +0.1518 | +0.1848 | +0.1844 | 0.0012 | +0.4502 | +0.6639 | 1.000 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Cluster 2 | +1 | +0.0772 | +0.1732 | +0.1723 | 0.0016 | +0.4734 | +0.6551 | 0.642 |
| `vwap_trend_channel_slope` | Cluster 1 | +1 | +0.1023 | +0.1640 | +0.1634 | 0.0028 | +0.4395 | +0.6727 | 0.709 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | Cluster 0 | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.720 |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | Cluster 1 | +1 | +0.1329 | +0.2836 | +0.2825 | 0.0000 | +0.8900 | +0.7947 | 0.915 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | Cluster 1 | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0002 | +0.8649 | +0.7779 | 0.730 |
| `max_up_ret` | Cluster 1 | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0046 | +0.6051 | +0.7266 | 0.728 |

### 588000ETF / long
No features admitted.

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 0 | +1 | +0.1383 | +0.2945 | +0.2928 | 0.0000 | +0.6026 | +0.7202 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Cluster 0 | +1 | +0.1766 | +0.2917 | +0.2894 | 0.0000 | +0.6974 | +0.7384 | 0.781 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Cluster 0 | +1 | +0.1502 | +0.2885 | +0.2864 | 0.0000 | +0.5040 | +0.6598 | 0.738 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Cluster 0 | +1 | +0.1452 | +0.2637 | +0.2612 | 0.0000 | +0.5523 | +0.6962 | 0.799 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Cluster 0 | +1 | +0.1678 | +0.2557 | +0.2535 | 0.0000 | +0.4950 | +0.6563 | 0.793 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | Cluster 1 | +1 | +0.1075 | +0.2449 | +0.2443 | 0.0000 | +0.7396 | +0.7818 | 0.871 |
| `combo_max__max_up_ret__first_bar_return` | Cluster 0 | +1 | +0.1444 | +0.2224 | +0.2203 | 0.0000 | +0.5050 | +0.7062 | 0.751 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Cluster 1 | +1 | +0.1034 | +0.1683 | +0.1674 | 0.0024 | +0.4694 | +0.6950 | 0.105 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 2 | 0.1585 | `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_clamp_diff__max_up_ret__early_vwap_acceleration` |
| 300ETF | single | Cluster 1 | 2 | 0.1585 | `combo_rank_max__max_up_ret__volume_weighted_price_position` | `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` |
| 300ETF | single | Cluster 2 | 5 | 0.1585 | `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `combo_ratio__bar_body_rng_0__volume_weighted_price_position`, `combo_mean__max_up_ret__volume_surge_direction`, `combo_min__volume_weighted_price_position__volume_surge_direction`, `combo_ratio__first_bar_sentiment__volume_surge_direction` |
| 300ETF | single | Cluster 3 | 4 | 0.1585 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`, `rbreaker_sell_setup_proximity_early` |
| 500ETF | single | Cluster 0 | 4 | 0.2161 | `combo_rank_min__first_bar_sentiment__early_body_momentum` | `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`, `combo_ratio__max_down_ret__net_volume_flow`, `combo_ratio__max_down_ret__volatility_expansion_trend_vector` |
| 500ETF | single | Cluster 1 | 6 | 0.2161 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `combo_rel_diff__max_up_ret__smooth_momentum_structure`, `combo_rel_diff__max_up_ret__late_bar_momentum`, `combo_sig_product__max_up_ret__close_vs_open_range`, `combo_sig_product__opening_drive_thrust_ratio__first_bar_return`, `vwap_trend_channel_slope` |
| 500ETF | single | Cluster 2 | 1 | 0.2161 | `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | _(none)_ |
| 500ETF | single | Cluster 3 | 6 | 0.2161 | `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `combo_rel_diff__star50_limit_proximity_early__body_size_progression`, `combo_mean__star50_limit_proximity_early__bar_ret_0`, `combo_sig_product__star50_limit_proximity_early__max_down_ret`, `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression`, `combo_sig_product__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 4 | 2 | 0.2161 | `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` |
| 588000ETF | single | Cluster 0 | 1 | 0.1544 | `combo_diff__directional_volume_signature__smooth_momentum_structure` | _(none)_ |
| 588000ETF | single | Cluster 1 | 3 | 0.1544 | `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope`, `max_up_ret` |
| 159915ETF | single | Cluster 0 | 6 | 0.3466 | `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`, `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`, `combo_min__star50_limit_proximity_early__bar_ret_0`, `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`, `combo_max__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 1 | 2 | 0.3466 | `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`opening_drive_thrust_ratio` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`opening_drive_thrust_ratio` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_mean__max_up_ret__volume_surge_direction` | `mean` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | `ratio` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | `min` | a=`volume_weighted_price_position`, b=`volume_surge_direction` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | `rel_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | `rank_min` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `rel_diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_ratio__max_down_ret__net_volume_flow` | `ratio` | a=`max_down_ret`, b=`net_volume_flow` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`body_size_progression` |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | `ratio` | a=`max_down_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
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
