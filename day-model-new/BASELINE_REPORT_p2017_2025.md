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
| 300ETF | single | 1,765 | 651 | 530 | 408 | 404 | 401 | 388 | 385 | 25 | 14 |
| 300ETF | long | 585 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 587 | 69 | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 1,231 | 416 | 340 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 363 | 42 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 320 | 42 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,246 | 1,444 | 1,227 | 1,016 | 1,011 | 955 | 589 | 588 | 29 | 12 |
| 500ETF | long | 1,347 | 119 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 429 | 60 | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,720 | 750 | 605 | 569 | 566 | 445 | 443 | 443 | 30 | 13 |
| 159915ETF | long | 1,118 | 180 | 117 | 117 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 299 | 43 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 14 | +0.1140 | [+0.0702, +0.1563] | +0.2830 | [+0.1892, +0.3742] | +0.7455 | 6.70% | 1.8037 | 5.13% | 1.4074 | 3.4656 | 2.81% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 12 | +0.1593 | [+0.1136, +0.2009] | +0.2388 | [+0.1454, +0.3207] | +0.9758 | 6.46% | 1.4764 | 4.91% | 1.1354 | 2.3246 | 3.86% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.1517 | [+0.1084, +0.1942] | +0.3532 | [+0.2648, +0.4453] | +0.7455 | 11.31% | 2.0228 | 9.69% | 1.7595 | 4.4454 | 2.20% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 14 | +0.0330* | [-0.0947, +0.1208] | +0.0579* | [-0.2362, +0.2819] | +0.4303 | 0.78% | 0.3217 | -0.84% | -0.3488 | -0.4829 | 4.71% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 12 | +0.0923* | [-0.0182, +0.1734] | -0.0013* | [-0.2134, +0.1587] | +0.6727 | 0.86% | 0.2328 | -0.66% | -0.1762 | -0.2466 | 3.59% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.1540 | [+0.0191, +0.2514] | +0.2039* | [-0.1185, +0.3870] | +0.6242 | 8.55% | 1.4766 | 7.09% | 1.2382 | 2.2513 | 6.22% |
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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1012 | +0.2766 | +0.2766 | 0.0000 | +0.6959 | +0.7375 | 0.913 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.0976 | +0.2578 | +0.2581 | 0.0000 | +0.7324 | +0.7715 | 0.738 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +1 | +0.0936 | +0.2499 | +0.2501 | 0.0000 | +0.6698 | +0.7761 | 0.785 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +1 | +0.0957 | +0.2456 | +0.2452 | 0.0000 | +0.6495 | +0.7185 | 0.874 |
| `combo_max__first_bar_return__volume_surge_direction` | +1 | +0.0790 | +0.2280 | +0.2267 | 0.0002 | +0.7009 | +0.7669 | 0.865 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +1 | +0.0768 | +0.1986 | +0.1991 | 0.0002 | +0.5819 | +0.7210 | 0.651 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | +1 | +0.0840 | +0.1898 | +0.1891 | 0.0002 | +0.5697 | +0.7123 | 0.968 |
| `combo_tri_max__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0` | +1 | +0.0904 | +0.1895 | +0.1896 | 0.0002 | +0.6179 | +0.7308 | 0.805 |
| `combo_min__bar_body_rng_0__demark_setup_reversal_early` | +1 | +0.0464 | +0.1682 | +0.1694 | 0.0012 | +0.4966 | +0.6763 | 0.404 |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | +1 | +0.0364 | +0.1637 | +0.1628 | 0.0014 | +0.7518 | +0.7267 | 0.776 |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | +1 | +0.0534 | +0.1451 | +0.1460 | 0.0042 | +0.4351 | +0.6665 | 0.248 |
| `combo_ratio__first_bar_return__volume_surge_direction` | +1 | +0.0796 | +0.1306 | +0.1312 | 0.0094 | +0.3195 | +0.6577 | 0.033 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +1 | +0.0528 | +0.1264 | +0.1276 | 0.0124 | +0.4721 | +0.6629 | 0.500 |
| `combo_abs_diff__max_up_ret__first_bar_sentiment` | +1 | +0.0443 | +0.1050 | +0.1065 | 0.0358 | +0.4662 | +0.6989 | 0.417 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1453 | +0.2689 | +0.2675 | 0.0000 | +1.0684 | +0.8286 | 0.672 |
| `combo_mean__close_vs_open_range__bar_ret_0` | +1 | +0.1292 | +0.2594 | +0.2588 | 0.0000 | +0.9535 | +0.8183 | 0.857 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +1 | +0.1364 | +0.2577 | +0.2564 | 0.0000 | +0.8679 | +0.8080 | 0.785 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1473 | +0.2524 | +0.2516 | 0.0000 | +0.9968 | +0.8224 | 0.931 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +1 | +0.1050 | +0.2502 | +0.2492 | 0.0000 | +0.7010 | +0.7581 | 0.956 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1228 | +0.2267 | +0.2261 | 0.0000 | +0.7036 | +0.7828 | 0.826 |
| `combo_max__max_up_ret__first_bar_sentiment` | +1 | +0.1279 | +0.2006 | +0.1998 | 0.0000 | +0.5017 | +0.7005 | 0.783 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1090 | +0.1843 | +0.1829 | 0.0002 | +0.5820 | +0.6938 | 0.646 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +1 | +0.1186 | +0.1819 | +0.1803 | 0.0002 | +0.4240 | +0.6696 | 0.680 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.0634 | +0.1767 | +0.1756 | 0.0002 | +0.5581 | +0.7087 | 0.617 |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | +1 | +0.1061 | +0.1662 | +0.1640 | 0.0012 | +0.5196 | +0.6804 | 0.857 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +1 | +0.1022 | +0.1469 | +0.1469 | 0.0040 | +0.5005 | +0.6675 | 0.118 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0` | +1 | +0.1272 | +0.3534 | +0.3528 | 0.0000 | +1.1038 | +0.8554 | 0.895 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +1 | +0.1256 | +0.3197 | +0.3193 | 0.0000 | +1.0333 | +0.8435 | 0.963 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1320 | +0.2967 | +0.2960 | 0.0000 | +0.8626 | +0.7921 | 0.918 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +1 | +0.1332 | +0.2885 | +0.2871 | 0.0000 | +0.9380 | +0.8039 | 0.841 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +1 | +0.1304 | +0.2847 | +0.2842 | 0.0000 | +0.8442 | +0.8085 | 1.000 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1060 | +0.2750 | +0.2737 | 0.0000 | +0.8977 | +0.8080 | 0.839 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +1 | +0.1104 | +0.2297 | +0.2299 | 0.0000 | +0.7790 | +0.8065 | 0.943 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0864 | +0.2028 | +0.2020 | 0.0000 | +0.4631 | +0.6778 | 0.558 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0983 | +0.1987 | +0.1960 | 0.0000 | +0.5182 | +0.6855 | 0.722 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +1 | +0.0883 | +0.1940 | +0.1952 | 0.0002 | +0.6258 | +0.7118 | 0.765 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | +1 | +0.1429 | +0.1852 | +0.1839 | 0.0004 | +0.5265 | +0.6794 | 1.000 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.1120 | +0.1819 | +0.1803 | 0.0004 | +0.4602 | +0.6799 | 0.726 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +1 | +0.0557 | +0.1698 | +0.1696 | 0.0012 | +0.5148 | +0.6505 | 0.376 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_max__first_bar_return__volume_surge_direction` | `max` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_tri_max__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_sentiment`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_min__bar_body_rng_0__demark_setup_reversal_early` | `min` | a=`bar_body_rng_0`, b=`demark_setup_reversal_early` |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | `tri_sig_max` | a=`volume_weighted_momentum_acceleration`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | `ratio` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_concentration` |
| `combo_ratio__first_bar_return__volume_surge_direction` | `ratio` | a=`first_bar_return`, b=`volume_surge_direction` |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | `min` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_abs_diff__max_up_ret__first_bar_sentiment` | `abs_diff` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_mean__close_vs_open_range__bar_ret_0` | `mean` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | `rel_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | `tri_mean` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency`, c=`volatility_expansion_trend_vector` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_max__max_up_ret__first_bar_sentiment` | `max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | `sig_product` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`impulse_bar_dominance`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | `sig_product` | a=`volume_weighted_price_position`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | `ratio` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | `abs_diff` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
