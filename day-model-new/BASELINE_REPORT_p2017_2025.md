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
| 300ETF | single | 1,754 | 644 | 592 | 413 | 408 | 140 | 140 | 139 | 19 | 19 |
| 300ETF | long | 585 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 587 | 69 | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 717 | 56 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 363 | 42 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 320 | 42 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 3,229 | 1,432 | 1,313 | 1,032 | 1,023 | 507 | 265 | 265 | 30 | 30 |
| 500ETF | long | 1,347 | 119 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 429 | 60 | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,703 | 730 | 649 | 581 | 570 | 248 | 247 | 247 | 33 | 33 |
| 159915ETF | long | 1,118 | 180 | 117 | 117 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 299 | 43 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 17 | +0.1078 | [+0.0650, +0.1499] | +0.2459 | [+0.1567, +0.3404] | +0.7939 | 5.64% | 1.6220 | 2.65% | 0.7729 | 1.7014 | 3.24% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 31 | +0.1575 | [+0.1127, +0.1996] | +0.2564 | [+0.1627, +0.3394] | +0.9758 | 6.29% | 1.4328 | 3.37% | 0.7750 | 1.5021 | 4.77% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 28 | +0.1423 | [+0.1002, +0.1843] | +0.3196 | [+0.2250, +0.4120] | +0.6242 | 10.16% | 1.9178 | 7.33% | 1.4005 | 3.4663 | 2.61% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 17 | +0.0184* | [-0.1165, +0.1158] | +0.0498* | [-0.2555, +0.2646] | +0.1636 | 0.91% | 0.5083 | -0.59% | -0.3276 | -0.4513 | 2.77% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 31 | +0.0812* | [-0.0392, +0.1632] | +0.0236* | [-0.2268, +0.2014] | +0.5515 | 1.49% | 0.3836 | -0.14% | -0.0359 | -0.0567 | 5.70% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 28 | +0.1484 | [+0.0070, +0.2458] | +0.1754* | [-0.1569, +0.3683] | +0.7333 | 7.69% | 1.3344 | 5.02% | 0.8733 | 1.5722 | 7.87% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +1 | +0.0954 | +0.2900 | +0.2899 | 0.0000 | +0.7713 | +0.7375 | 0.000 |
| `combo_min__max_up_ret__bar_body_rng_0` | +1 | +0.0875 | +0.2655 | +0.2657 | 0.0000 | +0.8219 | +0.7566 | 0.762 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.0997 | +0.2648 | +0.2653 | 0.0000 | +0.7748 | +0.7838 | 0.762 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | +1 | +0.0864 | +0.2523 | +0.2529 | 0.0000 | +0.8743 | +0.8003 | 0.827 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | +1 | +0.0875 | +0.2339 | +0.2334 | 0.0000 | +0.7192 | +0.7468 | 0.820 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | +1 | +0.0853 | +0.2314 | +0.2315 | 0.0000 | +0.4875 | +0.6824 | 0.792 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0858 | +0.2260 | +0.2253 | 0.0000 | +0.5785 | +0.7180 | 0.760 |
| `combo_max__max_up_ret__volume_surge_direction` | +1 | +0.0732 | +0.2210 | +0.2198 | 0.0000 | +0.7910 | +0.7643 | 0.820 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | +1 | +0.0924 | +0.2202 | +0.2207 | 0.0000 | +0.7464 | +0.7808 | 0.804 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +1 | +0.0834 | +0.2074 | +0.2081 | 0.0000 | +0.8331 | +0.8039 | 0.848 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | +1 | +0.0850 | +0.2052 | +0.2056 | 0.0000 | +0.5657 | +0.7236 | 0.810 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +1 | +0.0768 | +0.1986 | +0.1991 | 0.0000 | +0.5819 | +0.7210 | 0.714 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +1 | +0.0751 | +0.1980 | +0.1981 | 0.0000 | +0.4716 | +0.6752 | 0.799 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0910 | +0.1915 | +0.1920 | 0.0004 | +0.5268 | +0.7010 | 0.824 |
| `combo_min__max_up_ret__volume_surge_direction` | +1 | +0.0854 | +0.1881 | +0.1872 | 0.0004 | +0.4516 | +0.6526 | 0.850 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0868 | +0.1766 | +0.1782 | 0.0006 | +0.5792 | +0.7123 | 0.825 |
| `combo_sig_product__first_bar_sentiment__opening_drive_thrust_ratio` | +1 | +0.0894 | +0.1733 | +0.1726 | 0.0006 | +0.5265 | +0.7159 | 0.808 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | +1 | +0.0964 | +0.1614 | +0.1623 | 0.0012 | +0.5990 | +0.7174 | 0.841 |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | +1 | +0.0424 | +0.1200 | +0.1215 | 0.0152 | +0.4051 | +0.6372 | 0.592 |

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
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1382 | +0.2668 | +0.2654 | 0.0000 | +0.8524 | +0.8209 | 0.843 |
| `combo_mean__close_vs_open_range__bar_ret_0` | +1 | +0.1292 | +0.2594 | +0.2588 | 0.0000 | +0.9535 | +0.8183 | 0.811 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +1 | +0.1364 | +0.2577 | +0.2564 | 0.0000 | +0.8679 | +0.8080 | 0.786 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1414 | +0.2472 | +0.2458 | 0.0000 | +0.6286 | +0.7087 | 0.781 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +1 | +0.1224 | +0.2451 | +0.2448 | 0.0000 | +0.7995 | +0.7787 | 0.850 |
| `early_order_flow_imbalance` | +1 | +0.0995 | +0.2348 | +0.2351 | 0.0000 | +0.5819 | +0.7334 | 0.748 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1207 | +0.2329 | +0.2322 | 0.0000 | +0.6705 | +0.7303 | 0.769 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +1 | +0.1332 | +0.2318 | +0.2311 | 0.0000 | +0.8226 | +0.7514 | 0.846 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1076 | +0.2309 | +0.2298 | 0.0000 | +0.6110 | +0.7488 | 0.844 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | +1 | +0.1347 | +0.2308 | +0.2303 | 0.0000 | +0.7832 | +0.7638 | 0.836 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.1239 | +0.2273 | +0.2272 | 0.0000 | +0.5862 | +0.7169 | 0.746 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1227 | +0.2266 | +0.2259 | 0.0000 | +0.6986 | +0.7777 | 0.826 |
| `combo_rank_min__early_body_momentum__bar_ret_0` | +1 | +0.1015 | +0.2247 | +0.2246 | 0.0000 | +0.6351 | +0.7308 | 0.846 |
| `combo_min__first_bar_sentiment__bar_ret_0` | +1 | +0.1139 | +0.2200 | +0.2202 | 0.0000 | +0.6467 | +0.7267 | 0.830 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1329 | +0.2181 | +0.2169 | 0.0000 | +0.5428 | +0.6943 | 0.828 |
| `combo_max__max_up_ret__bar_ret_0` | +1 | +0.1331 | +0.2171 | +0.2168 | 0.0000 | +0.7488 | +0.7658 | 0.825 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +1 | +0.1203 | +0.2116 | +0.2101 | 0.0000 | +0.6243 | +0.7164 | 0.805 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +1 | +0.1399 | +0.2088 | +0.2081 | 0.0000 | +0.6924 | +0.7380 | 0.833 |
| `combo_z_sum__close_vs_open_range__high_low_sequence_momentum` | +1 | +0.1019 | +0.1903 | +0.1897 | 0.0000 | +0.4913 | +0.6876 | 0.850 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +1 | +0.1205 | +0.1888 | +0.1873 | 0.0000 | +0.4556 | +0.6752 | 0.651 |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | +1 | +0.0954 | +0.1833 | +0.1822 | 0.0000 | +0.6465 | +0.7169 | 0.820 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +1 | +0.1186 | +0.1819 | +0.1803 | 0.0000 | +0.4240 | +0.6696 | 0.680 |
| `combo_sig_product__net_volume_flow__bar_ret_0` | +1 | +0.0903 | +0.1810 | +0.1810 | 0.0000 | +0.5385 | +0.6650 | 0.799 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +1 | +0.1154 | +0.1743 | +0.1739 | 0.0004 | +0.6045 | +0.7679 | 0.849 |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | +1 | +0.0937 | +0.1682 | +0.1672 | 0.0008 | +0.4859 | +0.6588 | 0.771 |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | +1 | +0.1024 | +0.1638 | +0.1646 | 0.0008 | +0.4435 | +0.6747 | 0.841 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | +1 | +0.1155 | +0.1543 | +0.1543 | 0.0022 | +0.5723 | +0.7051 | 0.721 |
| `vwap_close_divergence_trend` | +1 | +0.0926 | +0.1534 | +0.1529 | 0.0024 | +0.5998 | +0.7046 | 0.813 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1386 | +0.3801 | +0.3803 | 0.0000 | +1.2371 | +0.8770 | 0.000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +1 | +0.1282 | +0.3414 | +0.3404 | 0.0000 | +1.1689 | +0.8610 | 0.815 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.1167 | +0.3282 | +0.3282 | 0.0000 | +1.0927 | +0.8677 | 0.798 |
| `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1264 | +0.3147 | +0.3142 | 0.0000 | +0.8284 | +0.7916 | 0.819 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1396 | +0.3141 | +0.3124 | 0.0000 | +0.8984 | +0.8070 | 0.825 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1069 | +0.2953 | +0.2939 | 0.0000 | +0.9638 | +0.8317 | 0.850 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1287 | +0.2944 | +0.2939 | 0.0000 | +0.7760 | +0.8008 | 0.847 |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | +1 | +0.1057 | +0.2942 | +0.2941 | 0.0000 | +0.8155 | +0.7782 | 0.839 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +1 | +0.1401 | +0.2823 | +0.2807 | 0.0000 | +0.9296 | +0.8132 | 0.821 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +1 | +0.1229 | +0.2809 | +0.2800 | 0.0000 | +0.8832 | +0.8049 | 0.815 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1280 | +0.2639 | +0.2628 | 0.0000 | +0.8041 | +0.7936 | 0.843 |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.1260 | +0.2625 | +0.2627 | 0.0000 | +0.7900 | +0.7607 | 0.838 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +1 | +0.1106 | +0.2543 | +0.2542 | 0.0000 | +0.7834 | +0.7627 | 0.843 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +1 | +0.1185 | +0.2534 | +0.2542 | 0.0000 | +0.7526 | +0.7885 | 0.812 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +1 | +0.0998 | +0.2490 | +0.2494 | 0.0000 | +0.7204 | +0.7828 | 0.849 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +1 | +0.1064 | +0.2481 | +0.2490 | 0.0000 | +0.6414 | +0.7247 | 0.849 |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | +1 | +0.1017 | +0.2472 | +0.2474 | 0.0000 | +0.6892 | +0.7447 | 0.840 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0918 | +0.2467 | +0.2465 | 0.0000 | +0.7058 | +0.7648 | 0.500 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0988 | +0.2407 | +0.2389 | 0.0000 | +0.7062 | +0.7787 | 0.822 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +1 | +0.1176 | +0.2331 | +0.2336 | 0.0000 | +0.6143 | +0.6984 | 0.835 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1214 | +0.2227 | +0.2223 | 0.0000 | +0.7996 | +0.7514 | 0.850 |
| `combo_rank_max__first_bar_sentiment__star50_limit_proximity_early` | +1 | +0.1181 | +0.2177 | +0.2170 | 0.0000 | +0.7114 | +0.7447 | 0.834 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +1 | +0.1151 | +0.2091 | +0.2080 | 0.0000 | +0.6228 | +0.7288 | 0.767 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | +1 | +0.1159 | +0.2034 | +0.2019 | 0.0000 | +0.7580 | +0.7303 | 0.819 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0864 | +0.2028 | +0.2020 | 0.0000 | +0.4631 | +0.6778 | 0.559 |
| `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` | +1 | +0.1126 | +0.1956 | +0.1935 | 0.0002 | +0.5590 | +0.7144 | 0.848 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | +1 | +0.1240 | +0.1924 | +0.1914 | 0.0002 | +0.6358 | +0.7092 | 0.779 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | +1 | +0.1175 | +0.1912 | +0.1910 | 0.0002 | +0.4525 | +0.6835 | 0.774 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1429 | +0.1853 | +0.1840 | 0.0002 | +0.5204 | +0.6758 | 0.627 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1071 | +0.1836 | +0.1830 | 0.0002 | +0.3939 | +0.6418 | 0.786 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.1120 | +0.1819 | +0.1803 | 0.0002 | +0.4602 | +0.6799 | 0.749 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | +1 | +0.1080 | +0.1783 | +0.1799 | 0.0004 | +0.4256 | +0.6619 | 0.842 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +1 | +0.1064 | +0.1602 | +0.1611 | 0.0022 | +0.5019 | +0.7298 | 0.833 |

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
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | `mean` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_min__bar_body_rng_0__volume_surge_direction` | `min` | a=`bar_body_rng_0`, b=`volume_surge_direction` |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | `z_sum` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_max__max_up_ret__volume_surge_direction` | `max` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | `z_sum` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | `diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_min__max_up_ret__volume_surge_direction` | `min` | a=`max_up_ret`, b=`volume_surge_direction` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_sig_product__first_bar_sentiment__opening_drive_thrust_ratio` | `sig_product` | a=`first_bar_sentiment`, b=`opening_drive_thrust_ratio` |
| `combo_diff__max_up_ret__early_vwap_acceleration` | `diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | `z_sum` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`volatility_expansion_trend_vector` |
| `combo_mean__close_vs_open_range__bar_ret_0` | `mean` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`trend_bar_close_consistency` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__early_body_momentum__bar_ret_0` | `rank_min` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_min__first_bar_sentiment__bar_ret_0` | `min` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_max__max_up_ret__bar_ret_0` | `max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_z_sum__close_vs_open_range__high_low_sequence_momentum` | `z_sum` | a=`close_vs_open_range`, b=`high_low_sequence_momentum` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | `z_sum` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__net_volume_flow__bar_ret_0` | `sig_product` | a=`net_volume_flow`, b=`bar_ret_0` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | `max` | a=`star50_limit_proximity_early`, b=`trend_bar_close_consistency` |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | `sig_product` | a=`high_low_sequence_momentum`, b=`first_bar_return` |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | `sig_product` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`impulse_bar_dominance` |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | `min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | `tri_mean` | a=`first_bar_sentiment`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`limit_down_proximity_early` |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`impulse_bar_dominance` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | `mean` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | `min` | a=`first_bar_return`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | `z_sum` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__first_bar_sentiment__star50_limit_proximity_early` | `rank_max` | a=`first_bar_sentiment`, b=`star50_limit_proximity_early` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `rank_max` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | `sig_product` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` | `mean` | a=`star50_limit_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_return` |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | `sig_product` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | `ratio` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | `z_sum` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
