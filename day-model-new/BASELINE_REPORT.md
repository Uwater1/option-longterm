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
| 300ETF | single | 1,397 | 223 | 77 | 58 | 21 | 21 | 21 | 7 | 7 |
| 300ETF | long | 623 | 68 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 444 | 71 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 764 | 54 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 524 | 73 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 330 | 53 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 2,915 | 1,362 | 1,202 | 1,186 | 530 | 340 | 340 | 30 | 30 |
| 500ETF | long | 1,140 | 186 | 89 | 36 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 428 | 72 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 588000ETF | single | 1,251 | 728 | 457 | 402 | 30 | 30 | 30 | 5 | 5 |
| 588000ETF | long | 647 | 226 | 29 | 3 | 0 | 0 | 0 | 0 | 0 |
| 588000ETF | short | 772 | 287 | 64 | 12 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,405 | 406 | 201 | 190 | 31 | 31 | 31 | 11 | 11 |
| 159915ETF | long | 742 | 91 | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 356 | 70 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.1270 | [+0.0751, +0.1742] | +0.2610 | [+0.1346, +0.3717] | +0.9394 | 7.63% | 1.4675 | 5.41% | 1.0527 | 2.2363 | 6.62% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 30 | +0.2216 | [+0.1737, +0.2689] | +0.3293 | [+0.2312, +0.4263] | +0.9758 | 10.17% | 2.1063 | 7.33% | 1.5344 | 3.3029 | 4.61% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 5 | +0.1352 | [+0.0691, +0.1977] | +0.3377 | [+0.1872, +0.4336] | +0.8545 | 7.97% | 1.6790 | 5.31% | 1.1325 | 2.6095 | 3.87% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 11 | +0.1724 | [+0.1253, +0.2176] | +0.2525 | [+0.1653, +0.3491] | +0.9515 | 8.59% | 1.4993 | 5.94% | 1.0402 | 1.5475 | 11.15% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.0713 | [+0.0015, +0.1300] | +0.1832 | [+0.0210, +0.3012] | +0.8182 | 4.51% | 1.0125 | 2.10% | 0.4760 | 0.8315 | 4.68% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 30 | +0.1145 | [+0.0536, +0.1731] | +0.1016* | [-0.0373, +0.2173] | +0.8545 | 3.10% | 0.8069 | 0.71% | 0.1849 | 0.3130 | 4.60% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 5 | -0.0049* | [-0.1033, +0.0764] | -0.0898* | [-0.3240, +0.1436] | +0.1879 | 1.97% | 0.6768 | 0.63% | 0.2159 | 0.3926 | 3.91% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 11 | +0.1371 | [+0.0696, +0.1939] | +0.2788 | [+0.1152, +0.4090] | +0.8303 | 9.40% | 1.6260 | 6.97% | 1.2137 | 3.0159 | 7.34% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.0375* | [-0.0593, +0.1285] | +0.1677* | [-0.0701, +0.3432] | +0.5030 | 4.71% | 0.8750 | 2.60% | 0.4879 | 0.8582 | 3.52% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 30 | +0.1248 | [+0.0446, +0.2039] | +0.0029* | [-0.1886, +0.1836] | +0.7697 | 2.31% | 0.6314 | -0.21% | -0.0561 | -0.0918 | 4.95% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 5 | -0.0406* | [-0.1459, +0.0754] | -0.1010* | [-0.3601, +0.1926] | +0.0182 | 2.53% | 0.8031 | 1.18% | 0.3764 | 0.7124 | 3.52% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 11 | +0.1445 | [+0.0538, +0.2277] | +0.2871 | [+0.0621, +0.4960] | +0.7576 | 11.23% | 1.5638 | 8.72% | 1.2200 | 3.1823 | 7.98% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1075 | +0.2754 | +0.2751 | 0.0000 | +0.4882 | +0.6891 | 0.000 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1267 | +0.2747 | +0.2746 | 0.0000 | +0.5307 | +0.6968 | 0.412 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1192 | +0.2571 | +0.2562 | 0.0000 | +0.5164 | +0.6839 | 0.849 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.824 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0208 | +0.2042 | +0.2034 | 0.0000 | +0.4802 | +0.6346 | 0.584 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | +1 | +0.0939 | +0.2020 | +0.2021 | 0.0000 | +0.4561 | +0.6522 | 0.636 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0538 | +0.1928 | +0.1935 | 0.0004 | +0.6003 | +0.7349 | 0.574 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1906 | +0.3397 | +0.3393 | 0.0000 | +1.0529 | +0.8358 | 0.000 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +1 | +0.2028 | +0.3327 | +0.3325 | 0.0000 | +0.8965 | +0.7965 | 0.485 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +1 | +0.1864 | +0.3278 | +0.3273 | 0.0000 | +0.7514 | +0.7625 | 0.735 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +1 | +0.1783 | +0.3277 | +0.3272 | 0.0000 | +0.8682 | +0.7842 | 0.769 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | +1 | +0.1712 | +0.3133 | +0.3127 | 0.0000 | +0.9506 | +0.8170 | 0.743 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +1 | +0.1684 | +0.3087 | +0.3084 | 0.0000 | +0.9521 | +0.8170 | 0.801 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1881 | +0.3072 | +0.3071 | 0.0000 | +0.6262 | +0.7314 | 0.813 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1611 | +0.2965 | +0.2961 | 0.0000 | +0.5518 | +0.6962 | 0.777 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | +1 | +0.1777 | +0.2955 | +0.2949 | 0.0000 | +0.9529 | +0.8416 | 0.839 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +1 | +0.1605 | +0.2877 | +0.2879 | 0.0000 | +0.7506 | +0.7806 | 0.770 |
| `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early` | +1 | +0.1942 | +0.2856 | +0.2844 | 0.0000 | +0.7711 | +0.7918 | 0.785 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +1 | +0.1884 | +0.2844 | +0.2839 | 0.0000 | +0.8363 | +0.7548 | 0.821 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1500 | +0.2835 | +0.2832 | 0.0000 | +0.8380 | +0.7607 | 0.605 |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | +1 | +0.1554 | +0.2751 | +0.2743 | 0.0000 | +0.6328 | +0.7314 | 0.835 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +1 | +0.1702 | +0.2721 | +0.2709 | 0.0000 | +0.8193 | +0.7912 | 0.768 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.1695 | +0.2713 | +0.2708 | 0.0000 | +0.7979 | +0.7724 | 0.769 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +1 | +0.1915 | +0.2692 | +0.2685 | 0.0000 | +1.0490 | +0.8047 | 0.836 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +1 | +0.1640 | +0.2664 | +0.2657 | 0.0000 | +0.6667 | +0.7331 | 0.772 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +1 | +0.1499 | +0.2642 | +0.2624 | 0.0000 | +0.9245 | +0.8188 | 0.232 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | +1 | +0.0827 | +0.2636 | +0.2642 | 0.0000 | +0.6985 | +0.7478 | 0.427 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1312 | +0.2591 | +0.2586 | 0.0000 | +0.7790 | +0.7619 | 0.833 |
| `max_up_ret` | +1 | +0.1709 | +0.2500 | +0.2496 | 0.0000 | +0.7454 | +0.7789 | 0.819 |
| `combo_rank_max__max_up_ret__early_body_momentum` | +1 | +0.1534 | +0.2443 | +0.2435 | 0.0000 | +0.9504 | +0.8111 | 0.849 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +1 | +0.1286 | +0.2418 | +0.2411 | 0.0000 | +0.7706 | +0.7630 | 0.787 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +1 | +0.1692 | +0.2390 | +0.2385 | 0.0000 | +0.6377 | +0.7308 | 0.846 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +1 | +0.1680 | +0.2305 | +0.2301 | 0.0000 | +0.5623 | +0.7578 | 0.828 |
| `combo_ratio__max_down_ret__net_volume_flow` | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0000 | +0.8478 | +0.7883 | 0.094 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | +1 | +0.1384 | +0.2185 | +0.2177 | 0.0000 | +0.7354 | +0.7525 | 0.086 |
| `combo_sig_product__max_up_ret__body_size_progression` | +1 | +0.1546 | +0.2143 | +0.2133 | 0.0000 | +0.7984 | +0.7554 | 0.832 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0000 | +0.3439 | +0.6633 | 0.646 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__high_low_sequence_momentum__volume_weighted_momentum_acceleration` | +1 | +0.1393 | +0.3122 | +0.3111 | 0.0000 | +0.9238 | +0.8203 | 0.000 |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | +1 | +0.1055 | +0.3037 | +0.3025 | 0.0000 | +0.7795 | +0.7601 | 0.720 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | +1 | +0.1493 | +0.2660 | +0.2656 | 0.0000 | +0.8649 | +0.7779 | 0.657 |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | +1 | +0.0645 | +0.2645 | +0.2642 | 0.0000 | +0.6275 | +0.7512 | 0.808 |
| `max_up_ret` | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0062 | +0.6051 | +0.7266 | 0.704 |

### 588000ETF / long
No features admitted.

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1597 | +0.2895 | +0.2872 | 0.0000 | +0.6249 | +0.7097 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance` | +1 | +0.1603 | +0.2852 | +0.2829 | 0.0000 | +0.8019 | +0.7783 | 0.823 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1502 | +0.2775 | +0.2754 | 0.0000 | +0.5040 | +0.6598 | 0.770 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +1 | +0.1504 | +0.2731 | +0.2716 | 0.0000 | +0.6783 | +0.7683 | 0.779 |
| `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early` | +1 | +0.1526 | +0.2711 | +0.2690 | 0.0000 | +0.5805 | +0.7085 | 0.823 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1435 | +0.2653 | +0.2637 | 0.0000 | +0.5680 | +0.6921 | 0.728 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0909 | +0.2510 | +0.2513 | 0.0000 | +0.5263 | +0.6962 | 0.543 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1286 | +0.2150 | +0.2131 | 0.0000 | +0.6017 | +0.7736 | 0.813 |
| `combo_z_sum__max_up_ret__star50_limit_proximity_early` | +1 | +0.1509 | +0.2105 | +0.2090 | 0.0000 | +0.5582 | +0.7249 | 0.810 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +1 | +0.1220 | +0.1949 | +0.1935 | 0.0002 | +0.5324 | +0.6997 | 0.836 |
| `combo_sig_product__max_up_ret__impulse_bar_dominance` | +1 | +0.1211 | +0.1853 | +0.1840 | 0.0006 | +0.3372 | +0.6246 | 0.771 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`body_size_progression` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`trend_bar_close_consistency` |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`double_bottom_bull_flag_early` |
| `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment`, c=`star50_limit_proximity_early` |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | `diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | `rank_max` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | `max` | a=`opening_drive_thrust_ratio`, b=`close_vs_open_range` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_rel_diff__max_up_ret__body_size_progression` | `rel_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | `rel_diff` | a=`star50_limit_proximity_early`, b=`body_size_progression` |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | `ratio` | a=`max_down_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | `rel_diff` | a=`max_up_ret`, b=`trend_bar_close_consistency` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | `rank_min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`smooth_momentum_structure` |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | `max` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_ratio__max_down_ret__net_volume_flow` | `ratio` | a=`max_down_ret`, b=`net_volume_flow` |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | `ratio` | a=`max_down_ret`, b=`volatility_expansion_trend_vector` |
| `combo_sig_product__max_up_ret__body_size_progression` | `sig_product` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rel_diff__high_low_sequence_momentum__volume_weighted_momentum_acceleration` | `rel_diff` | a=`high_low_sequence_momentum`, b=`volume_weighted_momentum_acceleration` |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | `diff` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | `sig_product` | a=`high_low_sequence_momentum`, b=`vwap_trend_channel_slope` |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | `sig_product` | a=`directional_volume_signature`, b=`smooth_momentum_structure` |
| `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`first_bar_sentiment`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`impulse_bar_dominance` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`first_bar_sentiment`, c=`star50_limit_proximity_early` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_z_sum__max_up_ret__star50_limit_proximity_early` | `z_sum` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | `ratio` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_sig_product__max_up_ret__impulse_bar_dominance` | `sig_product` | a=`max_up_ret`, b=`impulse_bar_dominance` |
