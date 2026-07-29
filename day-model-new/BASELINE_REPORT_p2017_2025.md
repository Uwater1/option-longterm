# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2017_2025`

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
| 300ETF | single | 1,285 | 461 | 363 | 260 | 257 | 257 | 76 | 74 | 4 | 4 |
| 300ETF | long | 585 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 587 | 69 | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 1,231 | 416 | 340 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 363 | 42 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 320 | 42 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,222 | 1,441 | 1,191 | 974 | 969 | 915 | 582 | 581 | 12 | 12 |
| 500ETF | long | 1,347 | 119 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 429 | 60 | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,901 | 752 | 604 | 557 | 553 | 446 | 422 | 422 | 11 | 11 |
| 159915ETF | long | 1,118 | 180 | 117 | 117 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 299 | 43 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 4 | +0.0971 | [+0.0519, +0.1386] | +0.2200 | [+0.1283, +0.3134] | +0.6848 | 5.29% | 1.4918 | 3.61% | 1.0346 | 2.0318 | 4.24% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 12 | +0.1720 | [+0.1264, +0.2139] | +0.2646 | [+0.1674, +0.3428] | +0.9879 | 5.70% | 1.5611 | 4.18% | 1.1597 | 2.1547 | 3.69% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 11 | +0.1481 | [+0.1072, +0.1901] | +0.3237 | [+0.2334, +0.4182] | +0.7091 | 10.58% | 1.9547 | 8.93% | 1.6734 | 4.0654 | 2.21% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 4 | -0.0226* | [-0.1517, +0.0792] | +0.0000* | [-0.2920, +0.1907] | +0.0061 | 0.08% | 0.0338 | -1.66% | -0.6984 | -0.9806 | 5.16% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 12 | +0.0842* | [-0.0182, +0.1598] | -0.0390* | [-0.2343, +0.1257] | +0.3455 | -0.80% | -0.2284 | -2.31% | -0.6511 | -0.8509 | 5.62% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 11 | +0.1607 | [+0.0228, +0.2554] | +0.2136* | [-0.1404, +0.3832] | +0.9030 | 8.57% | 1.4362 | 7.07% | 1.1972 | 2.1402 | 7.96% |
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
| `combo_min__max_up_ret__bar_body_rng_0` | +1 | +0.0875 | +0.2655 | +0.2657 | 0.0000 | +0.8219 | +0.7566 | 0.000 |
| `volume_weighted_price_position` | +1 | +0.0791 | +0.1777 | +0.1783 | 0.0008 | +0.6336 | +0.7535 | 0.596 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | +1 | +0.0964 | +0.1614 | +0.1623 | 0.0014 | +0.5990 | +0.7174 | 0.566 |
| `first_30min_return` | +1 | +0.0582 | +0.1189 | +0.1197 | 0.0188 | +0.4529 | +0.6855 | 0.664 |

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
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1545 | +0.3042 | +0.3034 | 0.0000 | +0.8177 | +0.7838 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1453 | +0.2689 | +0.2675 | 0.0000 | +1.0684 | +0.8286 | 0.672 |
| `combo_min__net_volume_flow__impulse_bar_dominance` | +1 | +0.1002 | +0.2687 | +0.2690 | 0.0000 | +0.7557 | +0.7679 | 0.589 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.1239 | +0.2273 | +0.2272 | 0.0000 | +0.5862 | +0.7169 | 0.690 |
| `combo_min__first_bar_sentiment__bar_ret_0` | +1 | +0.1139 | +0.2200 | +0.2202 | 0.0000 | +0.6467 | +0.7267 | 0.684 |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1011 | +0.2134 | +0.2111 | 0.0000 | +0.5497 | +0.6655 | 0.579 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +1 | +0.1203 | +0.2116 | +0.2101 | 0.0000 | +0.6243 | +0.7164 | 0.672 |
| `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | +1 | +0.1122 | +0.1999 | +0.1991 | 0.0000 | +0.7081 | +0.7540 | 0.461 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +1 | +0.1186 | +0.1819 | +0.1803 | 0.0002 | +0.4240 | +0.6696 | 0.680 |
| `combo_diff__max_up_ret__impulse_bar_dominance` | +1 | +0.0745 | +0.1786 | +0.1768 | 0.0002 | +0.5143 | +0.6953 | 0.603 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.0634 | +0.1767 | +0.1756 | 0.0002 | +0.5581 | +0.7087 | 0.575 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +1 | +0.1022 | +0.1469 | +0.1469 | 0.0040 | +0.5005 | +0.6675 | 0.111 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1386 | +0.3801 | +0.3803 | 0.0000 | +1.2371 | +0.8770 | 0.000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +1 | +0.1340 | +0.2722 | +0.2710 | 0.0000 | +0.8115 | +0.7941 | 0.693 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +1 | +0.1064 | +0.2480 | +0.2489 | 0.0000 | +0.6380 | +0.7221 | 0.650 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | +1 | +0.1233 | +0.2473 | +0.2454 | 0.0000 | +0.5834 | +0.7133 | 0.678 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0918 | +0.2467 | +0.2465 | 0.0000 | +0.7058 | +0.7648 | 0.441 |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | +1 | +0.0893 | +0.2007 | +0.1997 | 0.0000 | +0.4704 | +0.6794 | 0.610 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0983 | +0.1987 | +0.1960 | 0.0000 | +0.5182 | +0.6855 | 0.595 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1429 | +0.1853 | +0.1840 | 0.0004 | +0.5204 | +0.6758 | 0.639 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.1120 | +0.1819 | +0.1803 | 0.0004 | +0.4602 | +0.6799 | 0.693 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +1 | +0.1064 | +0.1602 | +0.1611 | 0.0022 | +0.5019 | +0.7298 | 0.651 |
| `trend_bar_close_consistency` | +1 | +0.0595 | +0.1553 | +0.1549 | 0.0028 | +0.4516 | +0.6758 | 0.585 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_min__net_volume_flow__impulse_bar_dominance` | `min` | a=`net_volume_flow`, b=`impulse_bar_dominance` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_min__first_bar_sentiment__bar_ret_0` | `min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | `sig_product` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | `diff` | a=`opening_drive_thrust_ratio`, b=`impulse_bar_dominance` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_diff__max_up_ret__impulse_bar_dominance` | `diff` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | `sig_product` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | `ratio` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
