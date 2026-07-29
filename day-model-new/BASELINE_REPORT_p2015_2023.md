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

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1,754 | 549 | 345 | 271 | 266 | 231 | 230 | 230 | 12 | 12 |
| 300ETF | long | 579 | 40 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 586 | 93 | 26 | 26 | 5 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 1,231 | 394 | 348 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 361 | 46 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 317 | 39 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,222 | 1,399 | 1,157 | 1,040 | 1,033 | 877 | 647 | 647 | 13 | 13 |
| 500ETF | long | 1,360 | 108 | 62 | 62 | 29 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 426 | 54 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,901 | 720 | 408 | 379 | 377 | 229 | 182 | 182 | 10 | 10 |
| 159915ETF | long | 1,121 | 108 | 48 | 48 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 302 | 47 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | +0.1331 | [+0.0898, +0.1764] | +0.2656 | [+0.1516, +0.3525] | +0.9273 | 7.46% | 1.7118 | 5.84% | 1.3586 | 2.6384 | 5.43% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 13 | +0.2017 | [+0.1577, +0.2470] | +0.3275 | [+0.2298, +0.4270] | +0.9394 | 11.15% | 2.1009 | 9.47% | 1.8079 | 3.8001 | 4.88% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 10 | +0.1739 | [+0.1285, +0.2168] | +0.2791 | [+0.1926, +0.3689] | +0.8545 | 8.51% | 1.4175 | 6.92% | 1.1607 | 1.6491 | 14.07% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | +0.0727 | [+0.0010, +0.1417] | +0.1669* | [-0.0066, +0.3313] | +0.6364 | 3.21% | 0.7441 | 1.59% | 0.3715 | 0.5713 | 3.84% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 13 | +0.1271 | [+0.0473, +0.1958] | +0.1163* | [-0.0471, +0.2551] | +0.7818 | 4.43% | 0.8677 | 2.96% | 0.5820 | 1.1046 | 5.75% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 10 | +0.1608 | [+0.0761, +0.2266] | +0.3143 | [+0.1122, +0.4770] | +0.8909 | 11.70% | 1.6668 | 10.26% | 1.4787 | 3.9676 | 6.07% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +1 | +0.1187 | +0.2800 | +0.2807 | 0.0000 | +0.7370 | +0.7191 | 0.000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.1188 | +0.2764 | +0.2775 | 0.0000 | +0.8678 | +0.8074 | 0.732 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1119 | +0.2634 | +0.2636 | 0.0000 | +0.6357 | +0.7155 | 0.711 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +1 | +0.0941 | +0.2409 | +0.2417 | 0.0000 | +0.5785 | +0.7062 | 0.627 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0965 | +0.2243 | +0.2248 | 0.0000 | +0.5652 | +0.7360 | 0.797 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.0999 | +0.2226 | +0.2238 | 0.0000 | +0.5179 | +0.6816 | 0.782 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | +1 | +0.0811 | +0.2172 | +0.2176 | 0.0000 | +0.7838 | +0.7750 | 0.711 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +1 | +0.0742 | +0.1929 | +0.1930 | 0.0002 | +0.4284 | +0.6718 | 0.524 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0660 | +0.1858 | +0.1864 | 0.0002 | +0.6574 | +0.7488 | 0.795 |
| `combo_ratio__bar_ret_0__volume_surge_direction` | +1 | +0.0928 | +0.1657 | +0.1665 | 0.0010 | +0.4783 | +0.7031 | 0.050 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +1 | +0.0894 | +0.1467 | +0.1473 | 0.0036 | +0.4503 | +0.6646 | 0.782 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +1 | +0.0354 | +0.1107 | +0.1113 | 0.0288 | +0.4657 | +0.6641 | 0.534 |

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
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +1 | +0.1650 | +0.3105 | +0.3121 | 0.0000 | +1.1681 | +0.8726 | 0.663 |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | +1 | +0.1725 | +0.2919 | +0.2933 | 0.0000 | +0.7576 | +0.7576 | 0.679 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +1 | +0.1447 | +0.2736 | +0.2754 | 0.0000 | +0.5541 | +0.6703 | 0.687 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1484 | +0.2722 | +0.2732 | 0.0000 | +0.7569 | +0.7494 | 0.623 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1269 | +0.2448 | +0.2467 | 0.0000 | +0.7120 | +0.7350 | 0.669 |
| `combo_min__first_bar_sentiment__first_bar_return` | +1 | +0.1456 | +0.2349 | +0.2363 | 0.0000 | +0.7255 | +0.7483 | 0.662 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1489 | +0.2233 | +0.2239 | 0.0000 | +0.7037 | +0.7437 | 0.646 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1369 | +0.2008 | +0.2010 | 0.0000 | +0.3612 | +0.6595 | 0.606 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | +1 | +0.0947 | +0.1933 | +0.1943 | 0.0000 | +0.5294 | +0.6662 | 0.407 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1562 | +0.1917 | +0.1925 | 0.0000 | +0.6775 | +0.7144 | 0.660 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +1 | +0.1603 | +0.1690 | +0.1706 | 0.0002 | +0.5264 | +0.7201 | 0.630 |
| `combo_ratio__bar_ret_0__net_volume_flow` | +1 | +0.1119 | +0.1425 | +0.1442 | 0.0062 | +0.3291 | +0.6523 | 0.092 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1376 | +0.3068 | +0.3083 | 0.0000 | +0.6713 | +0.7483 | 0.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1603 | +0.2762 | +0.2775 | 0.0000 | +0.7388 | +0.7637 | 0.601 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1072 | +0.2737 | +0.2745 | 0.0000 | +0.6264 | +0.7252 | 0.577 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1127 | +0.2140 | +0.2149 | 0.0000 | +0.6132 | +0.7006 | 0.456 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1243 | +0.2094 | +0.2090 | 0.0000 | +0.4687 | +0.6739 | 0.670 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +1 | +0.1211 | +0.1886 | +0.1898 | 0.0002 | +0.4226 | +0.6872 | 0.668 |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | +1 | +0.1374 | +0.1863 | +0.1875 | 0.0002 | +0.4381 | +0.6636 | 0.682 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1095 | +0.1551 | +0.1554 | 0.0018 | +0.4801 | +0.6959 | 0.100 |
| `volatility_expansion_trend_vector` | +1 | +0.0795 | +0.1531 | +0.1550 | 0.0020 | +0.3923 | +0.6667 | 0.685 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +1 | +0.0591 | +0.1499 | +0.1520 | 0.0022 | +0.4729 | +0.7052 | 0.244 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`volume_weighted_price_position` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__bar_ret_0__volume_surge_direction` | `ratio` | a=`bar_ret_0`, b=`volume_surge_direction` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`net_volume_flow` |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | `clamp_diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_min__first_bar_sentiment__first_bar_return` | `min` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | `abs_diff` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_ratio__bar_ret_0__net_volume_flow` | `ratio` | a=`bar_ret_0`, b=`net_volume_flow` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | `tri_min` | a=`first_bar_sentiment`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
