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
| 300ETF | single | 1,158 | 377 | 257 | 253 | 27 | 27 | 27 | 11 | 11 |
| 300ETF | long | 607 | 76 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 549 | 83 | 25 | 2 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 620 | 70 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 349 | 51 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 330 | 62 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 2,574 | 1,205 | 1,056 | 1,018 | 400 | 284 | 284 | 51 | 51 |
| 500ETF | long | 878 | 159 | 76 | 29 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 438 | 76 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 588000ETF | single | 1,318 | 451 | 387 | 348 | 28 | 28 | 28 | 8 | 8 |
| 588000ETF | long | 650 | 176 | 62 | 19 | 1 | 1 | 1 | 1 | 1 |
| 588000ETF | short | 522 | 77 | 14 | 2 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,733 | 725 | 466 | 461 | 82 | 82 | 82 | 13 | 13 |
| 159915ETF | long | 640 | 80 | 19 | 2 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 289 | 65 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.1328 | [+0.0823, +0.1817] | +0.2524 | [+0.1220, +0.3636] | +0.9636 | 7.91% | 1.5601 | 5.15% | 1.0254 | 2.2817 | 6.83% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 51 | +0.2059 | [+0.1578, +0.2553] | +0.3046 | [+0.2106, +0.3955] | +0.9515 | 9.83% | 1.8944 | 6.98% | 1.3558 | 2.5864 | 4.19% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 8 | +0.1640 | [+0.1056, +0.2132] | +0.3763 | [+0.2330, +0.4950] | +0.7455 | 10.98% | 1.7451 | 8.65% | 1.3834 | 5.8422 | 4.87% |
| 588000ETF | long | 1 | +0.0815 | [+0.0127, +0.1277] | +0.2516 | [+0.0387, +0.4087] | +0.6848 | 6.85% | 1.1060 | 6.16% | 0.9995 | 5.2673 | 1.94% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.1776 | [+0.1292, +0.2219] | +0.2681 | [+0.1818, +0.3599] | +0.9758 | 9.38% | 1.6433 | 6.68% | 1.1750 | 1.9226 | 7.86% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0697* | [-0.0015, +0.1305] | +0.2031 | [+0.0411, +0.3245] | +0.7091 | 4.60% | 1.0651 | 1.73% | 0.4044 | 0.6917 | 4.17% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 51 | +0.1176 | [+0.0568, +0.1728] | +0.1250* | [-0.0165, +0.2433] | +0.8182 | 4.63% | 0.9610 | 1.97% | 0.4104 | 0.7796 | 5.70% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 8 | -0.0041* | [-0.1171, +0.1017] | -0.1001* | [-0.3425, +0.1352] | +0.1515 | 0.26% | 0.1406 | -0.84% | -0.4486 | -0.6229 | 2.98% |
| 588000ETF | long | 1 | +0.0202* | [-0.0757, +0.1076] | -0.1338* | [-0.3429, +0.2818] | +0.1758 | 0.12% | 0.0481 | -0.81% | -0.3207 | -0.4835 | 4.91% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.1347 | [+0.0659, +0.1945] | +0.2554 | [+0.0939, +0.3902] | +0.6606 | 9.33% | 1.4818 | 6.86% | 1.0951 | 2.7258 | 6.40% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 11 | +0.0337* | [-0.0656, +0.1207] | +0.1263* | [-0.1157, +0.3025] | +0.5515 | 3.87% | 0.7405 | 1.24% | 0.2392 | 0.4061 | 4.94% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 51 | +0.1291 | [+0.0437, +0.2088] | +0.0998* | [-0.1089, +0.2746] | +0.7818 | 5.23% | 1.0294 | 2.56% | 0.5043 | 1.0454 | 6.07% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 8 | -0.0549* | [-0.1717, +0.0914] | -0.1382* | [-0.4336, +0.2006] | -0.2606 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 1 | +0.0364* | [-0.0748, +0.1302] | +0.1163* | [-0.3306, +0.4354] | +0.0667 | 3.03% | 0.8385 | 1.38% | 0.3874 | 0.7306 | 3.11% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.1433 | [+0.0488, +0.2297] | +0.2862 | [+0.0670, +0.4891] | +0.8424 | 12.31% | 1.5637 | 9.76% | 1.2459 | 3.4537 | 6.66% |
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
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.794 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1146 | +0.2267 | +0.2265 | 0.0000 | +0.5952 | +0.6698 | 0.820 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__first_bar_sentiment` | +1 | +0.1186 | +0.2205 | +0.2202 | 0.0000 | +0.5493 | +0.7320 | 0.824 |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | +1 | +0.0883 | +0.2124 | +0.2111 | 0.0000 | +0.6660 | +0.7396 | 0.640 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0208 | +0.2042 | +0.2034 | 0.0000 | +0.4802 | +0.6346 | 0.447 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0538 | +0.1928 | +0.1935 | 0.0004 | +0.6003 | +0.7349 | 0.574 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +1 | +0.0999 | +0.1898 | +0.1897 | 0.0004 | +0.6533 | +0.7496 | 0.822 |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1906 | +0.3349 | +0.3344 | 0.0000 | +1.0529 | +0.8358 | 0.000 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1864 | +0.3278 | +0.3273 | 0.0000 | +0.7514 | +0.7625 | 0.511 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | +1 | +0.1808 | +0.3190 | +0.3181 | 0.0000 | +0.8001 | +0.7789 | 0.673 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.2028 | +0.3177 | +0.3175 | 0.0000 | +0.8965 | +0.7965 | 0.735 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1881 | +0.3072 | +0.3071 | 0.0000 | +0.6262 | +0.7314 | 0.813 |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | +1 | +0.1794 | +0.3028 | +0.3022 | 0.0000 | +0.7520 | +0.7654 | 0.838 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1611 | +0.2965 | +0.2961 | 0.0000 | +0.5518 | +0.6962 | 0.770 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | +1 | +0.1870 | +0.2937 | +0.2935 | 0.0000 | +1.0535 | +0.8287 | 0.788 |
| `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1304 | +0.2914 | +0.2903 | 0.0000 | +0.6385 | +0.7390 | 0.750 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1887 | +0.2871 | +0.2867 | 0.0000 | +0.7018 | +0.7226 | 0.824 |
| `combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early` | +1 | +0.1395 | +0.2850 | +0.2841 | 0.0000 | +0.7264 | +0.7355 | 0.806 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1500 | +0.2835 | +0.2832 | 0.0000 | +0.8380 | +0.7607 | 0.696 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.1618 | +0.2832 | +0.2831 | 0.0000 | +0.6705 | +0.7337 | 0.714 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +1 | +0.1889 | +0.2752 | +0.2746 | 0.0000 | +0.9765 | +0.7777 | 0.800 |
| `combo_z_sum__max_up_ret__early_order_flow_imbalance` | +1 | +0.1430 | +0.2700 | +0.2687 | 0.0000 | +0.8526 | +0.7918 | 0.776 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | +1 | +0.1649 | +0.2670 | +0.2669 | 0.0000 | +0.6727 | +0.7132 | 0.802 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.1695 | +0.2654 | +0.2649 | 0.0000 | +0.7979 | +0.7724 | 0.761 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +1 | +0.1499 | +0.2642 | +0.2624 | 0.0000 | +0.9245 | +0.8188 | 0.225 |
| `combo_tri_min__max_up_ret__close_vs_open_range__first_bar_sentiment` | +1 | +0.1577 | +0.2636 | +0.2628 | 0.0000 | +0.7815 | +0.7830 | 0.775 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +1 | +0.1294 | +0.2607 | +0.2600 | 0.0000 | +0.7362 | +0.7871 | 0.821 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1476 | +0.2595 | +0.2588 | 0.0000 | +0.7485 | +0.7507 | 0.838 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1312 | +0.2591 | +0.2586 | 0.0000 | +0.7790 | +0.7619 | 0.833 |
| `combo_rank_max__close_vs_open_range__first_bar_sentiment` | +1 | +0.1429 | +0.2583 | +0.2582 | 0.0000 | +0.5417 | +0.7009 | 0.844 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.1583 | +0.2552 | +0.2542 | 0.0000 | +0.7886 | +0.7695 | 0.632 |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | +1 | +0.0830 | +0.2547 | +0.2554 | 0.0000 | +0.6510 | +0.7238 | 0.325 |
| `combo_rank_min__bar_ret_0__limit_down_proximity_early` | +1 | +0.1306 | +0.2542 | +0.2534 | 0.0000 | +0.4654 | +0.6323 | 0.847 |
| `combo_tri_max__max_up_ret__close_vs_open_range__early_body_momentum` | +1 | +0.1510 | +0.2443 | +0.2434 | 0.0000 | +0.8203 | +0.7578 | 0.812 |
| `combo_rank_max__max_up_ret__early_body_momentum` | +1 | +0.1534 | +0.2443 | +0.2435 | 0.0000 | +0.9504 | +0.8111 | 0.842 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +1 | +0.1286 | +0.2426 | +0.2419 | 0.0000 | +0.7706 | +0.7630 | 0.845 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | +1 | +0.0687 | +0.2407 | +0.2417 | 0.0000 | +0.6395 | +0.7067 | 0.682 |
| `combo_min__close_vs_open_range__bar_ret_0` | +1 | +0.1290 | +0.2398 | +0.2389 | 0.0000 | +0.7122 | +0.7367 | 0.813 |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | +1 | +0.1561 | +0.2385 | +0.2374 | 0.0000 | +0.7945 | +0.7630 | 0.804 |
| `combo_z_sum__opening_auction_imbalance__close_vs_open_range` | +1 | +0.1191 | +0.2370 | +0.2360 | 0.0000 | +0.6454 | +0.7320 | 0.846 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +1 | +0.1454 | +0.2367 | +0.2366 | 0.0000 | +0.6475 | +0.7290 | 0.827 |
| `combo_mean__bar_ret_0__max_down_ret` | +1 | +0.1535 | +0.2271 | +0.2263 | 0.0000 | +0.5667 | +0.6481 | 0.841 |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0000 | +0.8478 | +0.7883 | 0.094 |
| `combo_rank_min__opening_auction_imbalance__max_down_ret` | +1 | +0.1324 | +0.2094 | +0.2081 | 0.0000 | +0.5903 | +0.7091 | 0.847 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1639 | +0.2083 | +0.2078 | 0.0000 | +0.6710 | +0.7284 | 0.776 |
| `combo_diff__max_up_ret__early_order_flow_imbalance` | +1 | +0.0615 | +0.2073 | +0.2080 | 0.0000 | +0.4208 | +0.6563 | 0.813 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1692 | +0.2066 | +0.2061 | 0.0000 | +0.7149 | +0.7812 | 0.813 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +1 | +0.1432 | +0.2059 | +0.2050 | 0.0000 | +0.5352 | +0.6674 | 0.783 |
| `combo_sig_product__max_up_ret__rsi_opening` | +1 | +0.1400 | +0.2053 | +0.2046 | 0.0000 | +0.4992 | +0.6891 | 0.819 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0000 | +0.3439 | +0.6633 | 0.646 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1415 | +0.2006 | +0.2013 | 0.0000 | +0.3379 | +0.6129 | 0.708 |
| `combo_z_sum__bar_ret_0__early_order_flow_imbalance` | +1 | +0.1284 | +0.1990 | +0.1983 | 0.0000 | +0.5498 | +0.6481 | 0.846 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1623 | +0.1951 | +0.1946 | 0.0000 | +0.7260 | +0.7214 | 0.777 |
| `combo_z_sum__opening_auction_imbalance__max_down_ret` | +1 | +0.1334 | +0.1947 | +0.1940 | 0.0000 | +0.5809 | +0.7126 | 0.844 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +1 | +0.1365 | +0.1927 | +0.1931 | 0.0000 | +0.4562 | +0.6856 | 0.787 |
| `combo_max__first_bar_sentiment__limit_down_proximity_early` | +1 | +0.1335 | +0.1872 | +0.1863 | 0.0002 | +0.4099 | +0.6698 | 0.743 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | +1 | +0.1458 | +0.1803 | +0.1792 | 0.0006 | +0.3761 | +0.6475 | 0.845 |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | +1 | +0.1064 | +0.1614 | +0.1618 | 0.0034 | +0.4571 | +0.6716 | 0.075 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__rsi_opening__volume_weighted_momentum_acceleration` | +1 | +0.1393 | +0.3108 | +0.3097 | 0.0000 | +0.9238 | +0.8203 | 0.000 |
| `combo_z_sum__rsi_opening__max_up_ret` | +1 | +0.1255 | +0.2972 | +0.2972 | 0.0000 | +0.5508 | +0.7088 | 0.758 |
| `combo_z_sum__vix_diff_1d__max_up_ret` | +1 | +0.1403 | +0.2920 | +0.2917 | 0.0000 | +0.7144 | +0.7749 | 0.664 |
| `combo_sig_product__rsi_opening__pullback_depth_ratio` | +1 | +0.1122 | +0.2856 | +0.2848 | 0.0000 | +0.6832 | +0.7374 | 0.757 |
| `combo_rank_max__open_to_current_return__volume_weighted_price_position` | +1 | +0.1485 | +0.2796 | +0.2795 | 0.0000 | +0.9317 | +0.8193 | 0.818 |
| `combo_rank_min__vix_diff_1d__max_up_ret` | +1 | +0.1240 | +0.2175 | +0.2180 | 0.0018 | +0.4469 | +0.6584 | 0.585 |
| `vix_rolling_percentile_60d` | +1 | +0.0431 | +0.1918 | +0.1929 | 0.0064 | +0.3379 | +0.6288 | 0.163 |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1766 | +0.2917 | +0.2894 | 0.0000 | +0.6974 | +0.7384 | 0.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1502 | +0.2885 | +0.2864 | 0.0000 | +0.5040 | +0.6598 | 0.738 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1659 | +0.2696 | +0.2675 | 0.0000 | +0.5631 | +0.6528 | 0.850 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1452 | +0.2637 | +0.2612 | 0.0000 | +0.5523 | +0.6962 | 0.785 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1739 | +0.2614 | +0.2594 | 0.0000 | +0.7322 | +0.7390 | 0.826 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1435 | +0.2536 | +0.2520 | 0.0000 | +0.5680 | +0.6921 | 0.739 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0909 | +0.2510 | +0.2513 | 0.0000 | +0.5263 | +0.6962 | 0.610 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_range` | +1 | +0.1357 | +0.2502 | +0.2498 | 0.0000 | +0.5421 | +0.6856 | 0.585 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1533 | +0.2455 | +0.2443 | 0.0000 | +0.5912 | +0.7331 | 0.843 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.1364 | +0.2317 | +0.2298 | 0.0000 | +0.6078 | +0.7191 | 0.811 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +1 | +0.1349 | +0.2232 | +0.2213 | 0.0000 | +0.4124 | +0.6745 | 0.844 |
| `combo_max__max_up_ret__first_bar_return` | +1 | +0.1444 | +0.2224 | +0.2203 | 0.0000 | +0.5050 | +0.7062 | 0.803 |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | +1 | +0.1383 | +0.2093 | +0.2069 | 0.0000 | +0.5332 | +0.6880 | 0.827 |

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
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__first_bar_sentiment` | `tri_mean` | a=`star50_limit_proximity_early`, b=`first_bar_return`, c=`first_bar_sentiment` |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | `z_sum` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | `ratio` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range`, c=`first_bar_sentiment` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | `clamp_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`close_vs_open_range` |
| `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__close_vs_open_range` | `tri_min` | a=`opening_auction_imbalance`, b=`star50_limit_proximity_early`, c=`close_vs_open_range` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early` | `rank_min` | a=`opening_auction_imbalance`, b=`star50_limit_proximity_early` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | `rel_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_z_sum__max_up_ret__early_order_flow_imbalance` | `z_sum` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__max_up_ret__close_vs_open_range__first_bar_sentiment` | `tri_min` | a=`max_up_ret`, b=`close_vs_open_range`, c=`first_bar_sentiment` |
| `combo_rank_min__max_up_ret__close_vs_open_range` | `rank_min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_max__close_vs_open_range__first_bar_sentiment` | `rank_max` | a=`close_vs_open_range`, b=`first_bar_sentiment` |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | `sig_product` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | `rel_diff` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rank_min__bar_ret_0__limit_down_proximity_early` | `rank_min` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_tri_max__max_up_ret__close_vs_open_range__early_body_momentum` | `tri_max` | a=`max_up_ret`, b=`close_vs_open_range`, c=`early_body_momentum` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | `rank_min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__early_body_momentum` | `rel_diff` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_min__close_vs_open_range__bar_ret_0` | `min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | `rank_max` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_z_sum__opening_auction_imbalance__close_vs_open_range` | `z_sum` | a=`opening_auction_imbalance`, b=`close_vs_open_range` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | `ratio` | a=`max_down_ret`, b=`opening_auction_imbalance` |
| `combo_rank_min__opening_auction_imbalance__max_down_ret` | `rank_min` | a=`opening_auction_imbalance`, b=`max_down_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_diff__max_up_ret__early_order_flow_imbalance` | `diff` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__rsi_opening` | `sig_product` | a=`max_up_ret`, b=`rsi_opening` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_z_sum__bar_ret_0__early_order_flow_imbalance` | `z_sum` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_z_sum__opening_auction_imbalance__max_down_ret` | `z_sum` | a=`opening_auction_imbalance`, b=`max_down_ret` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_max__first_bar_sentiment__limit_down_proximity_early` | `max` | a=`first_bar_sentiment`, b=`limit_down_proximity_early` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | `ratio` | a=`max_down_ret`, b=`early_order_flow_imbalance` |
| `combo_rel_diff__rsi_opening__volume_weighted_momentum_acceleration` | `rel_diff` | a=`rsi_opening`, b=`volume_weighted_momentum_acceleration` |
| `combo_z_sum__rsi_opening__max_up_ret` | `z_sum` | a=`rsi_opening`, b=`max_up_ret` |
| `combo_z_sum__vix_diff_1d__max_up_ret` | `z_sum` | a=`vix_diff_1d`, b=`max_up_ret` |
| `combo_sig_product__rsi_opening__pullback_depth_ratio` | `sig_product` | a=`rsi_opening`, b=`pullback_depth_ratio` |
| `combo_rank_max__open_to_current_return__volume_weighted_price_position` | `rank_max` | a=`open_to_current_return`, b=`volume_weighted_price_position` |
| `combo_rank_min__vix_diff_1d__max_up_ret` | `rank_min` | a=`vix_diff_1d`, b=`max_up_ret` |
| `combo_z_sum__vix_skew_proxy__vix_iv_spread` | `z_sum` | a=`vix_skew_proxy`, b=`vix_iv_spread` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_range` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_range` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_max__max_up_ret__first_bar_return` | `max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | `z_sum` | a=`first_bar_sentiment`, b=`limit_down_proximity_early` |
