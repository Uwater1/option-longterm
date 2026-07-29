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
| 300ETF | single | 1,763 | 558 | 354 | 280 | 275 | 240 | 239 | 239 | 20 | 11 |
| 300ETF | long | 579 | 40 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 586 | 93 | 26 | 26 | 5 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 1,231 | 394 | 348 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 361 | 46 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 317 | 39 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,254 | 1,431 | 1,210 | 1,079 | 1,072 | 922 | 757 | 757 | 43 | 18 |
| 500ETF | long | 1,360 | 108 | 62 | 62 | 29 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 426 | 54 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,715 | 671 | 413 | 389 | 387 | 226 | 226 | 226 | 22 | 10 |
| 159915ETF | long | 1,121 | 108 | 48 | 48 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 302 | 47 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.1253 | [+0.0819, +0.1679] | +0.2726 | [+0.1641, +0.3606] | +0.9394 | 7.54% | 1.7868 | 5.95% | 1.4311 | 2.8279 | 6.05% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 18 | +0.2018 | [+0.1599, +0.2476] | +0.3204 | [+0.2279, +0.4124] | +0.9030 | 9.47% | 1.9687 | 7.83% | 1.6484 | 3.2300 | 4.43% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 10 | +0.1796 | [+0.1332, +0.2225] | +0.2771 | [+0.1868, +0.3708] | +0.8788 | 9.44% | 1.4759 | 7.84% | 1.2355 | 1.8505 | 14.00% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0709* | [-0.0023, +0.1384] | +0.1705 | [+0.0022, +0.3280] | +0.8545 | 3.17% | 0.7845 | 1.61% | 0.4002 | 0.6633 | 2.91% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 18 | +0.1178 | [+0.0459, +0.1840] | +0.1055* | [-0.0595, +0.2437] | +0.8788 | 4.30% | 0.8820 | 2.89% | 0.5964 | 1.1670 | 3.98% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 10 | +0.1481 | [+0.0670, +0.2162] | +0.2663 | [+0.0672, +0.4400] | +0.6242 | 10.04% | 1.4144 | 8.68% | 1.2361 | 3.0652 | 5.93% |
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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.1188 | +0.2764 | +0.2775 | 0.0000 | +0.8678 | +0.8074 | 0.732 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1156 | +0.2691 | +0.2697 | 0.0000 | +0.5471 | +0.7072 | 0.872 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1132 | +0.2593 | +0.2602 | 0.0000 | +0.6700 | +0.7042 | 0.791 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1216 | +0.2417 | +0.2421 | 0.0000 | +0.5923 | +0.6970 | 0.787 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +1 | +0.0872 | +0.2244 | +0.2251 | 0.0000 | +0.7215 | +0.7571 | 0.853 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.0999 | +0.2226 | +0.2238 | 0.0000 | +0.5179 | +0.6816 | 0.849 |
| `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | +1 | +0.0931 | +0.2047 | +0.2058 | 0.0000 | +0.4870 | +0.7283 | 1.000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +1 | +0.0742 | +0.1929 | +0.1930 | 0.0002 | +0.4284 | +0.6718 | 0.524 |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | +1 | +0.0665 | +0.1925 | +0.1927 | 0.0002 | +0.5928 | +0.7401 | 0.610 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +1 | +0.0680 | +0.1333 | +0.1336 | 0.0092 | +0.5209 | +0.7216 | 0.806 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +1 | +0.0354 | +0.1107 | +0.1113 | 0.0288 | +0.4657 | +0.6641 | 0.546 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1759 | +0.3158 | +0.3165 | 0.0000 | +0.9888 | +0.8243 | 0.905 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1544 | +0.3075 | +0.3095 | 0.0000 | +0.9528 | +0.8197 | 0.950 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +1 | +0.1641 | +0.3025 | +0.3043 | 0.0000 | +0.7337 | +0.7807 | 0.785 |
| `combo_min__max_up_ret__first_bar_sentiment` | +1 | +0.1702 | +0.2962 | +0.2969 | 0.0000 | +0.8348 | +0.7920 | 0.821 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1484 | +0.2722 | +0.2732 | 0.0000 | +0.7569 | +0.7494 | 0.609 |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | +1 | +0.1624 | +0.2705 | +0.2722 | 0.0000 | +0.7158 | +0.7571 | 0.967 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +1 | +0.1709 | +0.2551 | +0.2562 | 0.0000 | +0.9313 | +0.7802 | 0.924 |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.1440 | +0.2526 | +0.2535 | 0.0000 | +0.6405 | +0.7514 | 0.695 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.0773 | +0.2446 | +0.2447 | 0.0000 | +0.8140 | +0.7966 | 0.776 |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | +1 | +0.1524 | +0.2347 | +0.2360 | 0.0000 | +0.6128 | +0.7786 | 0.965 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1489 | +0.2233 | +0.2239 | 0.0000 | +0.7037 | +0.7437 | 0.657 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +1 | +0.1369 | +0.2006 | +0.2008 | 0.0000 | +0.3657 | +0.6697 | 1.000 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +1 | +0.1322 | +0.2005 | +0.2021 | 0.0000 | +0.4868 | +0.6569 | 0.770 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | +1 | +0.0947 | +0.1933 | +0.1943 | 0.0000 | +0.5294 | +0.6662 | 0.706 |
| `combo_sig_product__first_bar_sentiment__close_vs_open_range` | +1 | +0.1316 | +0.1815 | +0.1822 | 0.0000 | +0.5300 | +0.6959 | 0.778 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.0671 | +0.1728 | +0.1759 | 0.0000 | +0.4477 | +0.6502 | 0.600 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +1 | +0.1603 | +0.1690 | +0.1706 | 0.0002 | +0.5264 | +0.7201 | 0.692 |
| `combo_ratio__bar_ret_0__net_volume_flow` | +1 | +0.1119 | +0.1425 | +0.1442 | 0.0062 | +0.3291 | +0.6523 | 0.088 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1376 | +0.3068 | +0.3083 | 0.0000 | +0.6713 | +0.7483 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1650 | +0.2842 | +0.2846 | 0.0000 | +0.7080 | +0.7365 | 0.786 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +1 | +0.1299 | +0.2655 | +0.2665 | 0.0000 | +0.7819 | +0.7992 | 0.917 |
| `combo_tri_median__max_up_ret__first_bar_sentiment__star50_limit_proximity_early` | +1 | +0.1535 | +0.2629 | +0.2644 | 0.0000 | +0.6050 | +0.7062 | 0.888 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1532 | +0.2510 | +0.2517 | 0.0000 | +0.5328 | +0.7191 | 0.799 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1562 | +0.2431 | +0.2440 | 0.0000 | +0.5808 | +0.7006 | 0.830 |
| `combo_max__max_up_ret__bar_ret_0` | +1 | +0.1416 | +0.2273 | +0.2288 | 0.0000 | +0.5309 | +0.7103 | 1.000 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1127 | +0.2140 | +0.2149 | 0.0000 | +0.6132 | +0.7006 | 0.559 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1095 | +0.1551 | +0.1554 | 0.0018 | +0.4801 | +0.6959 | 0.126 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +1 | +0.0591 | +0.1499 | +0.1520 | 0.0022 | +0.4729 | +0.7052 | 0.401 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | `rel_diff` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | `max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_min__max_up_ret__first_bar_sentiment` | `min` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | `mean` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volume_weighted_momentum_acceleration` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | `abs_diff` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_sig_product__first_bar_sentiment__close_vs_open_range` | `sig_product` | a=`first_bar_sentiment`, b=`close_vs_open_range` |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `min` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_ratio__bar_ret_0__net_volume_flow` | `ratio` | a=`bar_ret_0`, b=`net_volume_flow` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_tri_median__max_up_ret__first_bar_sentiment__star50_limit_proximity_early` | `tri_median` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`star50_limit_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `ratio` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
