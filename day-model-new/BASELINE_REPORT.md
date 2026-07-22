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

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | BH-FDR Pass | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 896 | 353 | 264 | 261 | 10 |
| 300ETF | long | 253 | 43 | 7 | 0 | 0 |
| 300ETF | short | 423 | 75 | 27 | 7 | 0 |
| 50ETF | single | 267 | 38 | 3 | 0 | 0 |
| 50ETF | long | 258 | 33 | 6 | 0 | 0 |
| 50ETF | short | 245 | 43 | 5 | 0 | 0 |
| 500ETF | single | 2,289 | 1,111 | 1,010 | 984 | 48 |
| 500ETF | long | 697 | 115 | 60 | 20 | 0 |
| 500ETF | short | 394 | 58 | 6 | 0 | 0 |
| 588000ETF | single | 209 | 62 | 38 | 20 | 2 |
| 588000ETF | long | 439 | 81 | 30 | 6 | 1 |
| 588000ETF | short | 451 | 52 | 12 | 2 | 0 |
| 159915ETF | single | 1,510 | 647 | 432 | 429 | 11 |
| 159915ETF | long | 447 | 62 | 17 | 6 | 0 |
| 159915ETF | short | 240 | 50 | 3 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 5 | +0.1252 | [+0.0786, +0.1699] | +0.2590 | [+0.1310, +0.3714] | +0.8909 | 6.62% | 1.5205 | 4.39% | 1.0197 | 2.1609 | 6.97% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.1868 | [+0.1387, +0.2332] | +0.2710 | [+0.1679, +0.3662] | +0.9152 | 6.62% | 1.3936 | 4.13% | 0.8787 | 1.5071 | 4.53% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 2 | +0.1138 | [+0.0609, +0.1590] | +0.2131 | [+0.0758, +0.3297] | +0.7333 | 9.14% | 1.3230 | 7.12% | 1.0368 | 3.1758 | 4.46% |
| 588000ETF | long | 1 | +0.0815 | [+0.0127, +0.1277] | +0.2516 | [+0.0387, +0.4087] | +0.5758 | 6.85% | 1.1060 | 6.16% | 0.9995 | 5.2673 | 1.94% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 3 | +0.1579 | [+0.1105, +0.2028] | +0.2654 | [+0.1734, +0.3719] | +0.7576 | 7.54% | 1.1755 | 4.72% | 0.7391 | 1.0418 | 9.29% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 5 | +0.0801 | [+0.0088, +0.1459] | +0.2187 | [+0.0751, +0.3509] | +0.7333 | 4.27% | 1.2169 | 1.71% | 0.4930 | 1.1221 | 3.83% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.1063 | [+0.0382, +0.1678] | +0.0929* | [-0.0701, +0.2271] | +0.9636 | 4.36% | 0.8312 | 1.72% | 0.3291 | 0.6277 | 11.92% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 2 | +0.0131* | [-0.0768, +0.1097] | -0.0377* | [-0.2944, +0.2489] | -0.1152 | 0.83% | 0.8833 | 0.34% | 0.3597 | 0.5872 | 1.28% |
| 588000ETF | long | 1 | +0.0202* | [-0.0757, +0.1076] | -0.1338* | [-0.3429, +0.2818] | +0.1758 | 0.12% | 0.0481 | -0.81% | -0.3207 | -0.4835 | 4.91% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 3 | +0.1496 | [+0.0802, +0.2054] | +0.3082 | [+0.1220, +0.4479] | +0.8424 | 9.46% | 1.5483 | 6.76% | 1.1131 | 2.3775 | 11.80% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 5 | +0.0444* | [-0.0513, +0.1316] | +0.0959* | [-0.1332, +0.2781] | +0.8182 | 3.75% | 0.9446 | 1.46% | 0.3698 | 0.9679 | 4.33% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.1129 | [+0.0187, +0.1915] | +0.0246* | [-0.2143, +0.2052] | +0.9273 | 4.16% | 0.7592 | 1.27% | 0.2321 | 0.4514 | 11.40% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 2 | -0.0298* | [-0.1365, +0.1019] | -0.1131* | [-0.4113, +0.2254] | -0.2727 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 1 | +0.0364* | [-0.0748, +0.1302] | +0.1163* | [-0.3306, +0.4354] | +0.0667 | 3.03% | 0.8385 | 1.38% | 0.3874 | 0.7306 | 3.11% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 3 | +0.1470 | [+0.0568, +0.2304] | +0.3429 | [+0.0983, +0.5783] | +0.6970 | 12.29% | 1.5848 | 9.51% | 1.2333 | 2.7831 | 12.06% |
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
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment` | +1 | +0.1083 | +0.2386 | +0.2387 | 0.0000 | +0.5428 | +0.6903 | 0.691 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0953 | +0.2294 | +0.2299 | 0.0000 | +0.5550 | +0.7413 | 0.794 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1146 | +0.2267 | +0.2265 | 0.0000 | +0.5952 | +0.6698 | 0.820 |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | +1 | +0.0883 | +0.2124 | +0.2111 | 0.0000 | +0.6660 | +0.7396 | 0.640 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0208 | +0.2042 | +0.2034 | 0.0000 | +0.4802 | +0.6346 | 0.447 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +1 | +0.0538 | +0.1928 | +0.1935 | 0.0004 | +0.6003 | +0.7349 | 0.574 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +1 | +0.0702 | +0.1277 | +0.1278 | 0.0114 | +0.6295 | +0.7455 | 0.065 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +1 | +0.1906 | +0.3435 | +0.3430 | 0.0000 | +1.0529 | +0.8358 | 0.000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | +1 | +0.1808 | +0.3190 | +0.3181 | 0.0000 | +0.8001 | +0.7789 | 0.673 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1881 | +0.3072 | +0.3071 | 0.0000 | +0.6262 | +0.7314 | 0.813 |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | +1 | +0.1794 | +0.3028 | +0.3022 | 0.0000 | +0.7520 | +0.7654 | 0.838 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1611 | +0.2965 | +0.2961 | 0.0000 | +0.5518 | +0.6962 | 0.770 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | +1 | +0.1870 | +0.2937 | +0.2935 | 0.0000 | +1.0535 | +0.8287 | 0.788 |
| `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1304 | +0.2914 | +0.2903 | 0.0000 | +0.6385 | +0.7390 | 0.750 |
| `combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early` | +1 | +0.1395 | +0.2850 | +0.2841 | 0.0000 | +0.7264 | +0.7355 | 0.806 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +1 | +0.1500 | +0.2835 | +0.2832 | 0.0000 | +0.8380 | +0.7607 | 0.696 |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.1618 | +0.2832 | +0.2831 | 0.0000 | +0.6705 | +0.7337 | 0.714 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | +1 | +0.1882 | +0.2800 | +0.2795 | 0.0000 | +0.7672 | +0.7601 | 0.559 |
| `combo_z_sum__max_up_ret__early_order_flow_imbalance` | +1 | +0.1430 | +0.2700 | +0.2687 | 0.0000 | +0.8526 | +0.7918 | 0.776 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | +1 | +0.1649 | +0.2670 | +0.2669 | 0.0000 | +0.6727 | +0.7132 | 0.802 |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | +1 | +0.1554 | +0.2656 | +0.2649 | 0.0000 | +0.6328 | +0.7314 | 0.767 |
| `combo_tri_mean__max_up_ret__close_vs_open_range__first_bar_sentiment` | +1 | +0.1678 | +0.2635 | +0.2627 | 0.0000 | +0.8226 | +0.7713 | 0.847 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +1 | +0.1294 | +0.2607 | +0.2600 | 0.0000 | +0.7362 | +0.7871 | 0.838 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +1 | +0.1476 | +0.2595 | +0.2588 | 0.0000 | +0.7485 | +0.7507 | 0.838 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.1312 | +0.2591 | +0.2586 | 0.0000 | +0.7790 | +0.7619 | 0.833 |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | +1 | +0.0830 | +0.2547 | +0.2554 | 0.0000 | +0.6510 | +0.7238 | 0.333 |
| `combo_rank_min__bar_ret_0__limit_down_proximity_early` | +1 | +0.1306 | +0.2542 | +0.2534 | 0.0000 | +0.4654 | +0.6323 | 0.847 |
| `combo_tri_max__max_up_ret__close_vs_open_range__early_body_momentum` | +1 | +0.1510 | +0.2443 | +0.2434 | 0.0000 | +0.8203 | +0.7578 | 0.843 |
| `combo_rank_max__max_up_ret__early_body_momentum` | +1 | +0.1534 | +0.2443 | +0.2435 | 0.0000 | +0.9504 | +0.8111 | 0.842 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +1 | +0.1286 | +0.2426 | +0.2419 | 0.0000 | +0.7706 | +0.7630 | 0.826 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | +1 | +0.0687 | +0.2407 | +0.2417 | 0.0000 | +0.6395 | +0.7067 | 0.682 |
| `combo_min__close_vs_open_range__bar_ret_0` | +1 | +0.1290 | +0.2398 | +0.2389 | 0.0000 | +0.7122 | +0.7367 | 0.813 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +1 | +0.1454 | +0.2367 | +0.2366 | 0.0000 | +0.6475 | +0.7290 | 0.827 |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | +1 | +0.1323 | +0.2240 | +0.2235 | 0.0000 | +0.8478 | +0.7883 | 0.094 |
| `combo_z_sum__close_vs_open_range__early_body_momentum` | +1 | +0.0990 | +0.2238 | +0.2227 | 0.0000 | +0.5003 | +0.7091 | 0.822 |
| `combo_rank_min__opening_auction_imbalance__max_down_ret` | +1 | +0.1324 | +0.2094 | +0.2081 | 0.0000 | +0.5903 | +0.7091 | 0.847 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1639 | +0.2083 | +0.2078 | 0.0000 | +0.6710 | +0.7284 | 0.776 |
| `combo_diff__max_up_ret__early_order_flow_imbalance` | +1 | +0.0615 | +0.2073 | +0.2080 | 0.0000 | +0.4208 | +0.6563 | 0.813 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1692 | +0.2066 | +0.2061 | 0.0000 | +0.7149 | +0.7812 | 0.813 |
| `combo_rank_min__close_vs_open_range__early_order_flow_imbalance` | +1 | +0.0960 | +0.2063 | +0.2052 | 0.0000 | +0.5696 | +0.7191 | 0.847 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +1 | +0.1432 | +0.2059 | +0.2050 | 0.0000 | +0.5352 | +0.6674 | 0.783 |
| `combo_sig_product__max_up_ret__rsi_opening` | +1 | +0.1400 | +0.2053 | +0.2046 | 0.0000 | +0.4992 | +0.6891 | 0.819 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1436 | +0.2007 | +0.1999 | 0.0000 | +0.3439 | +0.6633 | 0.646 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1415 | +0.2006 | +0.2013 | 0.0000 | +0.3379 | +0.6129 | 0.708 |
| `combo_z_sum__bar_ret_0__early_order_flow_imbalance` | +1 | +0.1284 | +0.1990 | +0.1983 | 0.0000 | +0.5498 | +0.6481 | 0.846 |
| `combo_min__first_bar_sentiment__max_down_ret` | +1 | +0.1537 | +0.1963 | +0.1950 | 0.0000 | +0.5838 | +0.6956 | 0.732 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +1 | +0.1623 | +0.1951 | +0.1946 | 0.0000 | +0.7260 | +0.7214 | 0.777 |
| `combo_z_sum__opening_auction_imbalance__max_down_ret` | +1 | +0.1334 | +0.1947 | +0.1940 | 0.0000 | +0.5809 | +0.7126 | 0.843 |
| `first_bar_return` | +1 | +0.1592 | +0.1937 | +0.1931 | 0.0000 | +0.5925 | +0.7109 | 0.847 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +1 | +0.1365 | +0.1927 | +0.1931 | 0.0000 | +0.4562 | +0.6856 | 0.752 |
| `combo_max__first_bar_sentiment__limit_down_proximity_early` | +1 | +0.1335 | +0.1901 | +0.1893 | 0.0000 | +0.4099 | +0.6698 | 0.763 |
| `combo_rel_diff__max_down_ret__early_vwap_acceleration` | +1 | +0.1078 | +0.1882 | +0.1874 | 0.0002 | +0.4978 | +0.6804 | 0.583 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | +1 | +0.1458 | +0.1803 | +0.1792 | 0.0006 | +0.3761 | +0.6475 | 0.845 |
| `combo_diff__max_down_ret__early_vwap_acceleration` | +1 | +0.1105 | +0.1743 | +0.1741 | 0.0008 | +0.4158 | +0.6393 | 0.775 |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | +1 | +0.1064 | +0.1614 | +0.1618 | 0.0034 | +0.4571 | +0.6716 | 0.075 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `max_up_ret` | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0062 | +0.6051 | +0.7266 | 0.000 |
| `vix_rolling_percentile_60d` | +1 | +0.0431 | +0.1912 | +0.1923 | 0.0064 | +0.3379 | +0.6288 | 0.115 |

### 588000ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_z_sum__vix_skew_proxy__vix_iv_spread` | +1 | +0.0815 | +0.2516 | +0.2532 | 0.0008 | +0.1912 | +0.5597 | 0.000 |

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | +1 | +0.1597 | +0.2895 | +0.2872 | 0.0000 | +0.6249 | +0.7097 | 0.000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1659 | +0.2696 | +0.2675 | 0.0000 | +0.5631 | +0.6528 | 0.844 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1739 | +0.2614 | +0.2594 | 0.0000 | +0.7322 | +0.7390 | 0.826 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +1 | +0.1435 | +0.2593 | +0.2577 | 0.0000 | +0.5680 | +0.6921 | 0.739 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0909 | +0.2510 | +0.2513 | 0.0000 | +0.5263 | +0.6962 | 0.543 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_range` | +1 | +0.1357 | +0.2502 | +0.2498 | 0.0000 | +0.5421 | +0.6856 | 0.585 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1533 | +0.2455 | +0.2443 | 0.0000 | +0.5912 | +0.7331 | 0.843 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +1 | +0.1349 | +0.2232 | +0.2213 | 0.0000 | +0.4124 | +0.6745 | 0.844 |
| `combo_rank_max__max_up_ret__opening_auction_imbalance` | +1 | +0.1173 | +0.2199 | +0.2186 | 0.0000 | +0.6600 | +0.7818 | 0.762 |
| `combo_z_sum__max_up_ret__first_bar_sentiment` | +1 | +0.1522 | +0.2154 | +0.2129 | 0.0000 | +0.5452 | +0.7079 | 0.812 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +1 | +0.1220 | +0.1949 | +0.1935 | 0.0002 | +0.5324 | +0.6997 | 0.785 |

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
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_sentiment` |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | `z_sum` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | `ratio` | a=`limit_down_proximity_early`, b=`volume_concentration` |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | `ratio` | a=`first_bar_sentiment`, b=`volume_surge_direction` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`first_bar_sentiment` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`close_vs_open_range`, c=`first_bar_sentiment` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | `clamp_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`close_vs_open_range` |
| `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__close_vs_open_range` | `tri_min` | a=`opening_auction_imbalance`, b=`star50_limit_proximity_early`, c=`close_vs_open_range` |
| `combo_rank_min__opening_auction_imbalance__star50_limit_proximity_early` | `rank_min` | a=`opening_auction_imbalance`, b=`star50_limit_proximity_early` |
| `combo_sig_product__max_up_ret__close_vs_open_range` | `sig_product` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | `clamp_diff` | a=`max_up_ret`, b=`late_bar_momentum` |
| `combo_z_sum__max_up_ret__early_order_flow_imbalance` | `z_sum` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | `rank_max` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_tri_mean__max_up_ret__close_vs_open_range__first_bar_sentiment` | `tri_mean` | a=`max_up_ret`, b=`close_vs_open_range`, c=`first_bar_sentiment` |
| `combo_rank_min__max_up_ret__close_vs_open_range` | `rank_min` | a=`max_up_ret`, b=`close_vs_open_range` |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | `mean` | a=`star50_limit_proximity_early`, b=`close_vs_open_range` |
| `combo_min__star50_limit_proximity_early__max_down_ret` | `min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | `rel_diff` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_rank_min__bar_ret_0__limit_down_proximity_early` | `rank_min` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_tri_max__max_up_ret__close_vs_open_range__early_body_momentum` | `tri_max` | a=`max_up_ret`, b=`close_vs_open_range`, c=`early_body_momentum` |
| `combo_rank_max__max_up_ret__early_body_momentum` | `rank_max` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | `rank_min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rel_diff__max_up_ret__early_body_momentum` | `rel_diff` | a=`max_up_ret`, b=`early_body_momentum` |
| `combo_min__close_vs_open_range__bar_ret_0` | `min` | a=`close_vs_open_range`, b=`bar_ret_0` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_ratio__max_down_ret__opening_auction_imbalance` | `ratio` | a=`max_down_ret`, b=`opening_auction_imbalance` |
| `combo_z_sum__close_vs_open_range__early_body_momentum` | `z_sum` | a=`close_vs_open_range`, b=`early_body_momentum` |
| `combo_rank_min__opening_auction_imbalance__max_down_ret` | `rank_min` | a=`opening_auction_imbalance`, b=`max_down_ret` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_diff__max_up_ret__early_order_flow_imbalance` | `diff` | a=`max_up_ret`, b=`early_order_flow_imbalance` |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__close_vs_open_range__early_order_flow_imbalance` | `rank_min` | a=`close_vs_open_range`, b=`early_order_flow_imbalance` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__rsi_opening` | `sig_product` | a=`max_up_ret`, b=`rsi_opening` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_z_sum__bar_ret_0__early_order_flow_imbalance` | `z_sum` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_min__first_bar_sentiment__max_down_ret` | `min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | `max` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_z_sum__opening_auction_imbalance__max_down_ret` | `z_sum` | a=`opening_auction_imbalance`, b=`max_down_ret` |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | `sig_product` | a=`first_bar_sentiment`, b=`early_body_momentum` |
| `combo_max__first_bar_sentiment__limit_down_proximity_early` | `max` | a=`first_bar_sentiment`, b=`limit_down_proximity_early` |
| `combo_rel_diff__max_down_ret__early_vwap_acceleration` | `rel_diff` | a=`max_down_ret`, b=`early_vwap_acceleration` |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | `rank_min` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_diff__max_down_ret__early_vwap_acceleration` | `diff` | a=`max_down_ret`, b=`early_vwap_acceleration` |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | `ratio` | a=`max_down_ret`, b=`early_order_flow_imbalance` |
| `combo_z_sum__vix_skew_proxy__vix_iv_spread` | `z_sum` | a=`vix_skew_proxy`, b=`vix_iv_spread` |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | `tri_min` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`first_bar_sentiment` |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | `min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_range` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_range` |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | `clamp_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_rank_max__max_up_ret__opening_auction_imbalance` | `rank_max` | a=`max_up_ret`, b=`opening_auction_imbalance` |
| `combo_z_sum__max_up_ret__first_bar_sentiment` | `z_sum` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | `ratio` | a=`max_up_ret`, b=`volume_weighted_price_position` |
