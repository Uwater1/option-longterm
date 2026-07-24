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

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1,436 | 408 | 277 | 269 | 26 | 26 | 26 | 11 | 11 |
| 300ETF | long | 579 | 57 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 586 | 97 | 45 | 15 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 648 | 52 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 360 | 42 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 315 | 49 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 2,743 | 1,298 | 1,142 | 1,113 | 507 | 333 | 333 | 37 | 37 |
| 500ETF | long | 1,360 | 217 | 120 | 45 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 429 | 67 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 588000ETF | single | 1,361 | 519 | 458 | 415 | 27 | 27 | 27 | 7 | 7 |
| 588000ETF | long | 686 | 156 | 58 | 19 | 1 | 1 | 1 | 1 | 1 |
| 588000ETF | short | 924 | 117 | 37 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,833 | 739 | 509 | 503 | 87 | 87 | 87 | 15 | 15 |
| 159915ETF | long | 1,117 | 131 | 55 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 300 | 62 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.1334 | [+0.0815, +0.1825] | +0.2635 | [+0.1345, +0.3717] | +0.9394 | 8.26% | 1.6349 | 5.47% | 1.0949 | 2.4244 | 6.88% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 37 | +0.2201 | [+0.1746, +0.2680] | +0.3255 | [+0.2298, +0.4204] | +0.9394 | 10.18% | 2.0486 | 7.27% | 1.4788 | 3.0222 | 4.76% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 7 | +0.1610 | [+0.1027, +0.2149] | +0.2754 | [+0.1376, +0.3733] | +0.9515 | 8.64% | 1.4858 | 6.17% | 1.0683 | 2.9499 | 6.00% |
| 588000ETF | long | 1 | +0.0815 | [+0.0127, +0.1277] | +0.2516 | [+0.0387, +0.4087] | +0.6848 | 6.85% | 1.1060 | 6.16% | 0.9995 | 5.2673 | 1.94% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 15 | +0.1738 | [+0.1274, +0.2178] | +0.2686 | [+0.1867, +0.3646] | +0.9394 | 8.17% | 1.4623 | 5.54% | 0.9939 | 1.5200 | 7.36% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0679* | [-0.0012, +0.1269] | +0.1942 | [+0.0334, +0.3190] | +0.6848 | 4.59% | 1.1037 | 1.63% | 0.3966 | 0.7020 | 3.94% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 37 | +0.1125 | [+0.0542, +0.1685] | +0.1134* | [-0.0292, +0.2259] | +0.9152 | 4.12% | 0.9286 | 1.59% | 0.3604 | 0.6765 | 4.13% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 7 | +0.0013* | [-0.1034, +0.0951] | -0.1240* | [-0.3424, +0.1610] | +0.2606 | 0.57% | 0.2982 | -0.61% | -0.3175 | -0.4370 | 2.96% |
| 588000ETF | long | 1 | +0.0202* | [-0.0757, +0.1076] | -0.1338* | [-0.3429, +0.2818] | +0.1758 | 0.12% | 0.0481 | -0.81% | -0.3207 | -0.4835 | 4.91% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 15 | +0.1367 | [+0.0678, +0.1938] | +0.2670 | [+0.1111, +0.3987] | +0.7091 | 9.46% | 1.5801 | 7.05% | 1.1854 | 3.1472 | 7.06% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0322* | [-0.0672, +0.1188] | +0.1159* | [-0.1162, +0.3102] | +0.5758 | 3.67% | 0.7370 | 0.87% | 0.1765 | 0.3116 | 4.43% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 37 | +0.1246 | [+0.0439, +0.2028] | +0.0516* | [-0.1427, +0.2203] | +0.6242 | 4.90% | 1.0637 | 2.28% | 0.4949 | 0.9902 | 4.53% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 7 | -0.0559* | [-0.1641, +0.0799] | -0.1680* | [-0.4166, +0.2133] | -0.3576 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 1 | +0.0364* | [-0.0748, +0.1302] | +0.1163* | [-0.3306, +0.4354] | +0.0667 | 3.03% | 0.8385 | 1.38% | 0.3874 | 0.7306 | 3.11% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 15 | +0.1450 | [+0.0492, +0.2327] | +0.2791 | [+0.0581, +0.4782] | +0.6000 | 12.78% | 1.6772 | 10.25% | 1.3521 | 3.9106 | 6.64% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +1 | +0.1299 | +0.2949 | +0.2950 | 0.0000 | +0.7632 | +0.7279 | 0.000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1242 | +0.2939 | +0.2939 | 0.0000 | +0.5738 | +0.7126 | 0.769 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1164 | +0.2660 | +0.2658 | 0.0000 | +0.6109 | +0.7003 | 0.808 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.1262 | +0.2657 | +0.2653 | 0.0000 | +0.8130 | +0.7912 | 0.829 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.794 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1146 | +0.2267 | +0.2265 | 0.0000 | +0.5952 | +0.6698 | 0.820 |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | +1 | +0.0883 | +0.2124 | +0.2111 | 0.0000 | +0.6660 | +0.7396 | 0.640 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0208 | +0.2042 | +0.2034 | 0.0000 | +0.4802 | +0.6346 | 0.447 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0538 | +0.1928 | +0.1935 | 0.0004 | +0.6003 | +0.7349 | 0.619 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +1 | +0.0999 | +0.1898 | +0.1897 | 0.0004 | +0.6533 | +0.7496 | 0.725 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +1 | +0.0702 | +0.1277 | +0.1278 | 0.0114 | +0.6295 | +0.7455 | 0.064 |

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
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1864 | +0.3278 | +0.3273 | 0.0000 | +0.7514 | +0.7625 | 0.000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1783 | +0.3277 | +0.3272 | 0.0000 | +0.8682 | +0.7842 | 0.673 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.2028 | +0.3177 | +0.3175 | 0.0000 | +0.8965 | +0.7965 | 0.735 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | +1 | +0.1712 | +0.3133 | +0.3127 | 0.0000 | +0.9506 | +0.8170 | 0.743 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +1 | +0.1684 | +0.3087 | +0.3084 | 0.0000 | +0.9521 | +0.8170 | 0.801 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1881 | +0.3072 | +0.3071 | 0.0000 | +0.6262 | +0.7314 | 0.661 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.1605 | +0.2977 | +0.2979 | 0.0000 | +0.7506 | +0.7806 | 0.770 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1611 | +0.2965 | +0.2961 | 0.0000 | +0.5518 | +0.6962 | 0.777 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.1777 | +0.2955 | +0.2949 | 0.0000 | +0.9529 | +0.8416 | 0.839 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1800 | +0.2907 | +0.2900 | 0.0000 | +0.8748 | +0.7959 | 0.832 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1887 | +0.2871 | +0.2867 | 0.0000 | +0.7018 | +0.7226 | 0.844 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +1 | +0.1884 | +0.2844 | +0.2839 | 0.0000 | +0.8363 | +0.7548 | 0.821 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1500 | +0.2835 | +0.2832 | 0.0000 | +0.8380 | +0.7607 | 0.605 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.1618 | +0.2832 | +0.2831 | 0.0000 | +0.6705 | +0.7337 | 0.701 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +1 | +0.1702 | +0.2721 | +0.2709 | 0.0000 | +0.8193 | +0.7912 | 0.768 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +1 | +0.1915 | +0.2673 | +0.2666 | 0.0000 | +1.0490 | +0.8047 | 0.836 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +1 | +0.1640 | +0.2669 | +0.2662 | 0.0000 | +0.6667 | +0.7331 | 0.772 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.1695 | +0.2654 | +0.2649 | 0.0000 | +0.7979 | +0.7724 | 0.769 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +1 | +0.1499 | +0.2642 | +0.2624 | 0.0000 | +0.9245 | +0.8188 | 0.232 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | +1 | +0.0827 | +0.2636 | +0.2642 | 0.0000 | +0.6985 | +0.7478 | 0.427 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | +1 | +0.1681 | +0.2631 | +0.2621 | 0.0000 | +0.6724 | +0.7625 | 0.847 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1476 | +0.2595 | +0.2588 | 0.0000 | +0.7485 | +0.7507 | 0.761 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1312 | +0.2591 | +0.2586 | 0.0000 | +0.7790 | +0.7619 | 0.833 |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | +1 | +0.1472 | +0.2569 | +0.2566 | 0.0000 | +0.6376 | +0.7496 | 0.750 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1583 | +0.2552 | +0.2542 | 0.0000 | +0.7886 | +0.7695 | 0.725 |
| `max_up_ret` | +1 | +0.1709 | +0.2500 | +0.2496 | 0.0000 | +0.7454 | +0.7789 | 0.819 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | +1 | +0.1740 | +0.2498 | +0.2491 | 0.0000 | +0.6807 | +0.7396 | 0.802 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +1 | +0.1286 | +0.2426 | +0.2419 | 0.0000 | +0.7706 | +0.7630 | 0.789 |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | +1 | +0.1561 | +0.2385 | +0.2374 | 0.0000 | +0.7945 | +0.7630 | 0.830 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +1 | +0.1713 | +0.2362 | +0.2354 | 0.0000 | +0.6739 | +0.7601 | 0.828 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1828 | +0.2298 | +0.2291 | 0.0000 | +0.5203 | +0.7208 | 0.745 |
| `combo_mean__bar_ret_0__max_down_ret` | +1 | +0.1535 | +0.2271 | +0.2263 | 0.0000 | +0.5667 | +0.6481 | 0.841 |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0000 | +0.8478 | +0.7883 | 0.094 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | +1 | +0.1384 | +0.2185 | +0.2177 | 0.0000 | +0.7354 | +0.7525 | 0.099 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0000 | +0.3439 | +0.6633 | 0.646 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1415 | +0.2006 | +0.2013 | 0.0000 | +0.3379 | +0.6129 | 0.709 |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1618 | +0.1996 | +0.1990 | 0.0000 | +0.6810 | +0.7126 | 0.776 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__rsi_opening__smooth_momentum_structure` | +1 | +0.1393 | +0.3260 | +0.3248 | 0.0000 | +1.1114 | +0.8578 | 0.000 |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.705 |
| `combo_sig_product__rsi_opening__pullback_depth_ratio` | +1 | +0.1122 | +0.2856 | +0.2848 | 0.0000 | +0.6832 | +0.7374 | 0.602 |
| `combo_sig_product__rsi_opening__vwap_trend_channel_slope` | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0000 | +0.8649 | +0.7779 | 0.749 |
| `max_up_ret` | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0062 | +0.6051 | +0.7266 | 0.704 |
| `vix_rolling_percentile_60d` | +1 | +0.0431 | +0.1918 | +0.1929 | 0.0064 | +0.3379 | +0.6288 | 0.115 |
| `vix` | +1 | +0.0304 | +0.1545 | +0.1530 | 0.0312 | +0.4225 | +0.6575 | 0.349 |

### 588000ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_z_sum__vix_skew_proxy__vix_iv_spread` | +1 | +0.0815 | +0.2516 | +0.2532 | 0.0008 | +0.1912 | +0.5597 | 0.000 |

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1383 | +0.2945 | +0.2928 | 0.0000 | +0.6026 | +0.7202 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1766 | +0.2917 | +0.2894 | 0.0000 | +0.6974 | +0.7384 | 0.781 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | +1 | +0.1526 | +0.2900 | +0.2879 | 0.0000 | +0.5805 | +0.7085 | 0.736 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1502 | +0.2885 | +0.2864 | 0.0000 | +0.5040 | +0.6598 | 0.823 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1659 | +0.2696 | +0.2675 | 0.0000 | +0.5631 | +0.6528 | 0.850 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1452 | +0.2637 | +0.2612 | 0.0000 | +0.5523 | +0.6962 | 0.799 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1739 | +0.2614 | +0.2594 | 0.0000 | +0.7322 | +0.7390 | 0.826 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1435 | +0.2536 | +0.2520 | 0.0000 | +0.5680 | +0.6921 | 0.739 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0909 | +0.2510 | +0.2513 | 0.0000 | +0.5263 | +0.6962 | 0.610 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1533 | +0.2455 | +0.2443 | 0.0000 | +0.5912 | +0.7331 | 0.843 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.1364 | +0.2317 | +0.2298 | 0.0000 | +0.6078 | +0.7191 | 0.811 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1288 | +0.2267 | +0.2248 | 0.0000 | +0.5061 | +0.7179 | 0.838 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +1 | +0.1349 | +0.2232 | +0.2213 | 0.0000 | +0.4124 | +0.6745 | 0.844 |
| `combo_max__max_up_ret__first_bar_return` | +1 | +0.1444 | +0.2224 | +0.2203 | 0.0000 | +0.5050 | +0.7062 | 0.803 |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | +1 | +0.1383 | +0.2093 | +0.2069 | 0.0000 | +0.5332 | +0.6880 | 0.827 |

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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | `z_sum` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`trend_bar_close_consistency` |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `rel_diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | `sig_product` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_sentiment` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment` |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | `rank_min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | `rank_max` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | `max` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | `ratio` | a=`max_down_ret`, b=`opening_auction_imbalance` |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | `ratio` | a=`max_down_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | `rank_max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rel_diff__rsi_opening__smooth_momentum_structure` | `rel_diff` | a=`rsi_opening`, b=`smooth_momentum_structure` |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | `diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_sig_product__rsi_opening__pullback_depth_ratio` | `sig_product` | a=`rsi_opening`, b=`pullback_depth_ratio` |
| `combo_sig_product__rsi_opening__vwap_trend_channel_slope` | `sig_product` | a=`rsi_opening`, b=`vwap_trend_channel_slope` |
| `combo_z_sum__vix_skew_proxy__vix_iv_spread` | `z_sum` | a=`vix_skew_proxy`, b=`vix_iv_spread` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_max__max_up_ret__first_bar_return` | `max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | `z_sum` | a=`first_bar_sentiment`, b=`rbreaker_buy_setup_proximity_early` |
