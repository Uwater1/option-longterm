# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2016_2024`

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
| 300ETF | single | 1,761 | 565 | 422 | 327 | 315 | 313 | 295 | 295 | 19 | 12 |
| 300ETF | long | 586 | 58 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 587 | 69 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 1,231 | 347 | 310 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 368 | 43 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 321 | 46 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,247 | 1,344 | 987 | 854 | 846 | 831 | 601 | 601 | 29 | 11 |
| 500ETF | long | 1,350 | 96 | 37 | 37 | 2 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 428 | 51 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,709 | 687 | 471 | 444 | 440 | 363 | 353 | 353 | 17 | 11 |
| 159915ETF | long | 1,120 | 214 | 130 | 130 | 11 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 299 | 52 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | +0.1149 | [+0.0723, +0.1576] | +0.2375 | [+0.1434, +0.3354] | +0.7576 | 5.31% | 1.6462 | 3.68% | 1.1601 | 2.2901 | 3.54% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.1553 | [+0.1145, +0.1989] | +0.2680 | [+0.1834, +0.3683] | +0.8909 | 6.77% | 1.6882 | 5.18% | 1.3076 | 2.4090 | 4.58% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 11 | +0.1540 | [+0.1134, +0.1950] | +0.2877 | [+0.2050, +0.3799] | +0.8182 | 9.08% | 2.1189 | 7.50% | 1.7834 | 3.5750 | 3.77% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 12 | +0.0306* | [-0.0575, +0.1202] | +0.1044* | [-0.0904, +0.2767] | +0.6727 | 3.66% | 0.9058 | 1.97% | 0.4922 | 1.0597 | 5.66% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.1127 | [+0.0287, +0.1870] | +0.0623* | [-0.1422, +0.2158] | +0.7576 | 4.38% | 0.7851 | 2.93% | 0.5280 | 1.0276 | 4.80% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 11 | +0.1366 | [+0.0500, +0.2131] | +0.2795 | [+0.0522, +0.4768] | +0.8061 | 11.49% | 1.4868 | 10.01% | 1.3079 | 3.6434 | 5.40% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +1 | +0.1000 | +0.2637 | +0.2645 | 0.0000 | +0.6771 | +0.7285 | 0.943 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +1 | +0.0915 | +0.2524 | +0.2527 | 0.0000 | +0.8557 | +0.8123 | 0.519 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.1022 | +0.2509 | +0.2505 | 0.0000 | +0.7382 | +0.7810 | 0.765 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | +1 | +0.0911 | +0.2421 | +0.2414 | 0.0000 | +0.6260 | +0.7152 | 0.787 |
| `combo_rank_min__volume_weighted_price_position__bar_body_rng_0` | +1 | +0.0999 | +0.2157 | +0.2161 | 0.0000 | +0.6784 | +0.7460 | 0.915 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +1 | +0.0882 | +0.2082 | +0.2081 | 0.0000 | +0.5333 | +0.6766 | 1.000 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0915 | +0.1892 | +0.1892 | 0.0002 | +0.7145 | +0.7635 | 0.793 |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | +1 | +0.0324 | +0.1604 | +0.1602 | 0.0014 | +0.6125 | +0.6956 | 0.389 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +1 | +0.0719 | +0.1591 | +0.1593 | 0.0016 | +0.4843 | +0.6864 | 0.593 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | +1 | +0.0523 | +0.1476 | +0.1485 | 0.0036 | +0.5459 | +0.6879 | 0.791 |
| `combo_ratio__first_bar_return__volume_surge_direction` | +1 | +0.0898 | +0.1402 | +0.1408 | 0.0062 | +0.4259 | +0.6853 | 1.000 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +1 | +0.0405 | +0.1287 | +0.1304 | 0.0110 | +0.5507 | +0.7059 | 0.543 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1412 | +0.2745 | +0.2746 | 0.0000 | +1.0155 | +0.8370 | 0.660 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +1 | +0.1302 | +0.2717 | +0.2718 | 0.0000 | +0.7606 | +0.7429 | 0.844 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +1 | +0.1350 | +0.2676 | +0.2677 | 0.0000 | +0.9482 | +0.7856 | 0.928 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | +1 | +0.1202 | +0.2644 | +0.2653 | 0.0000 | +0.8057 | +0.7733 | 0.625 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1496 | +0.2513 | +0.2506 | 0.0000 | +0.8829 | +0.8072 | 0.872 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +1 | +0.1231 | +0.2446 | +0.2452 | 0.0000 | +0.7011 | +0.7398 | 0.859 |
| `combo_max__bar_ret_0__max_down_ret` | +1 | +0.1239 | +0.2061 | +0.2067 | 0.0002 | +0.5692 | +0.6879 | 0.821 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | +1 | +0.0944 | +0.1747 | +0.1744 | 0.0002 | +0.3988 | +0.6586 | 0.710 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +1 | +0.1104 | +0.1738 | +0.1732 | 0.0006 | +0.4085 | +0.6591 | 0.743 |
| `combo_diff__bar_ret_0__max_down_ret` | +1 | +0.0701 | +0.1682 | +0.1692 | 0.0008 | +0.3995 | +0.6550 | 0.441 |
| `vwap_trend_channel_slope` | +1 | +0.0836 | +0.1436 | +0.1423 | 0.0058 | +0.4568 | +0.6530 | 0.747 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1446 | +0.3321 | +0.3316 | 0.0000 | +0.8369 | +0.8046 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +1 | +0.1163 | +0.2933 | +0.2948 | 0.0000 | +0.7699 | +0.8231 | 0.373 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +1 | +0.1248 | +0.2816 | +0.2820 | 0.0000 | +0.8111 | +0.7969 | 0.782 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__impulse_bar_dominance` | +1 | +0.1052 | +0.2643 | +0.2641 | 0.0000 | +0.6466 | +0.7362 | 0.695 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1262 | +0.2465 | +0.2461 | 0.0000 | +0.5563 | +0.7100 | 0.966 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | +1 | +0.1284 | +0.2314 | +0.2314 | 0.0000 | +0.5021 | +0.7162 | 0.832 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +1 | +0.0943 | +0.2306 | +0.2298 | 0.0000 | +0.5865 | +0.7054 | 0.792 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +1 | +0.0859 | +0.2096 | +0.2089 | 0.0002 | +0.6535 | +0.7177 | 0.635 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +1 | +0.1024 | +0.2033 | +0.2038 | 0.0002 | +0.4871 | +0.7039 | 0.783 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | +1 | +0.0727 | +0.1841 | +0.1841 | 0.0004 | +0.4847 | +0.6509 | 0.494 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +1 | +0.0672 | +0.1678 | +0.1664 | 0.0016 | +0.4436 | +0.6607 | 0.391 |

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
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | `min` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__volume_weighted_price_position__bar_body_rng_0` | `rank_min` | a=`volume_weighted_price_position`, b=`bar_body_rng_0` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | `tri_sig_max` | a=`volume_weighted_momentum_acceleration`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | `tri_mean` | a=`smooth_momentum_structure`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_ratio__first_bar_return__volume_surge_direction` | `ratio` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | `rank_min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | `diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | `sig_product` | a=`star50_limit_proximity_early`, b=`early_body_momentum` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_diff__bar_ret_0__max_down_ret` | `diff` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__impulse_bar_dominance` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`impulse_bar_dominance` |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | `mean` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | `sig_product` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_max` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
