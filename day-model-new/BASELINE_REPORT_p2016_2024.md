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
| 300ETF | single | 1,285 | 410 | 304 | 232 | 221 | 220 | 61 | 61 | 2 | 2 |
| 300ETF | long | 586 | 58 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 587 | 69 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 1,231 | 347 | 310 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 368 | 43 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 321 | 46 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,222 | 1,339 | 934 | 813 | 806 | 800 | 541 | 541 | 12 | 12 |
| 500ETF | long | 1,350 | 96 | 37 | 37 | 2 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 428 | 51 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,901 | 712 | 491 | 456 | 454 | 364 | 267 | 267 | 12 | 12 |
| 159915ETF | long | 1,120 | 214 | 130 | 130 | 11 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 299 | 52 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 2 | +0.0909 | [+0.0481, +0.1323] | +0.2372 | [+0.1433, +0.3286] | +0.8788 | 4.84% | 1.6009 | 3.26% | 1.0949 | 2.0849 | 4.92% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 12 | +0.1477 | [+0.1067, +0.1919] | +0.2284 | [+0.1484, +0.3305] | +0.8788 | 4.91% | 1.3848 | 3.34% | 0.9506 | 1.6123 | 4.26% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 12 | +0.1495 | [+0.1043, +0.1920] | +0.3293 | [+0.2435, +0.4132] | +0.8303 | 10.20% | 2.3275 | 8.64% | 2.0103 | 4.4738 | 2.61% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 2 | +0.0031* | [-0.0852, +0.0896] | -0.0419* | [-0.2544, +0.1459] | +0.3939 | 1.36% | 0.4448 | -0.32% | -0.1054 | -0.1990 | 7.50% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 12 | +0.1252 | [+0.0431, +0.1977] | +0.0809* | [-0.1084, +0.2439] | +0.8667 | 3.72% | 0.8789 | 2.30% | 0.5461 | 0.9171 | 4.20% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 12 | +0.1335 | [+0.0437, +0.2088] | +0.2446 | [+0.0503, +0.4133] | +0.8424 | 11.25% | 1.4566 | 9.78% | 1.2795 | 3.4564 | 6.59% |
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
| `combo_min__max_up_ret__bar_body_rng_0` | +1 | +0.0924 | +0.2468 | +0.2470 | 0.0000 | +0.6402 | +0.6946 | 0.000 |
| `early_order_flow_imbalance` | +1 | +0.0652 | +0.1648 | +0.1646 | 0.0012 | +0.6152 | +0.7090 | 0.597 |

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
| `combo_rank_min__first_bar_sentiment__first_bar_return` | +1 | +0.1202 | +0.2767 | +0.2776 | 0.0000 | +0.8057 | +0.7733 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1412 | +0.2745 | +0.2746 | 0.0000 | +1.0155 | +0.8370 | 0.494 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +1 | +0.1346 | +0.2714 | +0.2708 | 0.0000 | +0.7631 | +0.7758 | 0.665 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +1 | +0.1350 | +0.2673 | +0.2673 | 0.0000 | +0.9482 | +0.7856 | 0.648 |
| `combo_max__bar_ret_0__max_down_ret` | +1 | +0.1239 | +0.2061 | +0.2067 | 0.0002 | +0.5692 | +0.6879 | 0.685 |
| `combo_rank_min__star50_limit_proximity_early__opening_momentum_score` | +1 | +0.0987 | +0.2051 | +0.2050 | 0.0002 | +0.5655 | +0.7157 | 0.689 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1055 | +0.1884 | +0.1888 | 0.0002 | +0.6440 | +0.7198 | 0.668 |
| `combo_min__net_volume_flow__max_down_ret` | +1 | +0.1034 | +0.1787 | +0.1786 | 0.0002 | +0.5798 | +0.6982 | 0.678 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +1 | +0.1256 | +0.1729 | +0.1715 | 0.0006 | +0.4735 | +0.6751 | 0.685 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1000 | +0.1561 | +0.1555 | 0.0034 | +0.4245 | +0.6833 | 0.691 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.0912 | +0.1543 | +0.1535 | 0.0038 | +0.4950 | +0.6663 | 0.577 |
| `trend_strength_intraday` | +1 | +0.0822 | +0.1304 | +0.1297 | 0.0100 | +0.3552 | +0.6653 | 0.683 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1446 | +0.3321 | +0.3316 | 0.0000 | +0.8369 | +0.8046 | 0.000 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0876 | +0.2581 | +0.2602 | 0.0000 | +0.7167 | +0.7542 | 0.432 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +1 | +0.1141 | +0.2538 | +0.2538 | 0.0000 | +0.5473 | +0.7414 | 0.680 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1182 | +0.2437 | +0.2438 | 0.0000 | +0.6376 | +0.7434 | 0.635 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | +1 | +0.1227 | +0.2392 | +0.2387 | 0.0000 | +0.5407 | +0.6977 | 0.687 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0942 | +0.2124 | +0.2126 | 0.0000 | +0.5568 | +0.6848 | 0.460 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +1 | +0.0859 | +0.2096 | +0.2089 | 0.0002 | +0.6535 | +0.7177 | 0.595 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1225 | +0.1877 | +0.1873 | 0.0002 | +0.4653 | +0.6535 | 0.601 |
| `consecutive_higher_highs` | +1 | +0.0463 | +0.1851 | +0.1834 | 0.0002 | +0.4744 | +0.6838 | 0.473 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +1 | +0.0672 | +0.1678 | +0.1664 | 0.0016 | +0.4436 | +0.6607 | 0.412 |
| `early_range` | +1 | +0.0616 | +0.1526 | +0.1524 | 0.0032 | +0.4735 | +0.6607 | 0.342 |
| `close_vs_open_range` | +1 | +0.0638 | +0.1148 | +0.1144 | 0.0230 | +0.5019 | +0.7208 | 0.657 |

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
| `combo_rank_min__first_bar_sentiment__first_bar_return` | `rank_min` | a=`first_bar_sentiment`, b=`first_bar_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_min__star50_limit_proximity_early__opening_momentum_score` | `rank_min` | a=`star50_limit_proximity_early`, b=`opening_momentum_score` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__net_volume_flow__max_down_ret` | `min` | a=`net_volume_flow`, b=`max_down_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | `max` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `sig_product` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`first_bar_return` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | `sig_product` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
