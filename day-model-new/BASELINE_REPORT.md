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
| 300ETF | single | 344 | 121 | 31 | 29 | 1 |
| 300ETF | long | 626 | 113 | 4 | 0 | 0 |
| 300ETF | short | 11,748 | 1,145 | 95 | 0 | 0 |
| 50ETF | single | 2,681 | 304 | 51 | 0 | 0 |
| 50ETF | long | 4,275 | 448 | 18 | 0 | 0 |
| 50ETF | short | 9,209 | 813 | 75 | 0 | 0 |
| 500ETF | single | 3,738 | 1,309 | 941 | 719 | 89 |
| 500ETF | long | 5,145 | 617 | 246 | 6 | 1 |
| 500ETF | short | 12,090 | 1,222 | 133 | 2 | 0 |
| 588000ETF | single | 9,676 | 4,467 | 3,701 | 2,618 | 90 |
| 588000ETF | long | 7,442 | 1,921 | 637 | 6 | 0 |
| 588000ETF | short | 9,881 | 1,161 | 122 | 0 | 0 |
| 159915ETF | single | 5,138 | 1,221 | 503 | 305 | 19 |
| 159915ETF | long | 3,590 | 360 | 71 | 0 | 0 |
| 159915ETF | short | 11,853 | 1,525 | 20 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1 | +0.0323* | [-0.0136, +0.0801] | +0.1514 | [+0.0363, +0.2638] | +0.4182 | 4.33% | 0.6678 | 3.74% | 0.5768 | 0.8857 | 13.85% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 10 | +0.2158 | [+0.1655, +0.2660] | +0.3229 | [+0.2244, +0.4177] | +0.9636 | 10.11% | 1.4539 | 7.62% | 1.1005 | 1.7284 | 8.31% |
| 500ETF | long | 1 | +0.0353* | [-0.0096, +0.0847] | +0.2319 | [+0.1018, +0.3762] | -0.1273 | 6.41% | 1.2361 | 5.20% | 1.0156 | 2.0377 | 5.21% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 6 | +0.1609 | [+0.0986, +0.2159] | +0.3108 | [+0.1743, +0.4272] | +0.9636 | 12.53% | 1.8633 | 9.54% | 1.4301 | 5.3073 | 5.13% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 10 | +0.1857 | [+0.1338, +0.2275] | +0.3330 | [+0.2275, +0.4305] | +0.7333 | 12.14% | 2.0598 | 9.41% | 1.6053 | 3.0204 | 4.29% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1 | +0.0056* | [-0.0452, +0.0580] | +0.1239 | [+0.0119, +0.2232] | +0.2121 | 3.06% | 0.8054 | 2.56% | 0.6749 | 1.2345 | 3.04% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 10 | +0.1156 | [+0.0557, +0.1754] | +0.1957 | [+0.0539, +0.3284] | +0.8303 | 6.36% | 1.1866 | 3.59% | 0.6742 | 1.2897 | 5.43% |
| 500ETF | long | 1 | -0.0263* | [-0.0823, +0.0316] | -0.0632* | [-0.1935, +0.1095] | -0.3697 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 6 | -0.0053* | [-0.1122, +0.0845] | +0.0075* | [-0.2458, +0.1749] | +0.2727 | 1.76% | 0.3347 | -1.20% | -0.2289 | -0.3579 | 5.58% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 10 | +0.1130 | [+0.0470, +0.1683] | +0.1427* | [-0.0168, +0.2592] | +0.8061 | 7.50% | 1.1158 | 4.83% | 0.7182 | 1.6451 | 7.87% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1 | -0.0007* | [-0.0653, +0.0787] | +0.1120* | [-0.0214, +0.2635] | +0.1273 | 3.29% | 1.1257 | 2.93% | 1.0094 | 1.9803 | 1.48% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 10 | +0.1308 | [+0.0486, +0.2172] | +0.2330 | [+0.0198, +0.4134] | +0.7939 | 9.95% | 1.5870 | 7.04% | 1.1305 | 2.8795 | 5.69% |
| 500ETF | long | 1 | -0.0481* | [-0.1274, +0.0273] | -0.0789* | [-0.3253, +0.1177] | -0.4303 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 6 | -0.0495* | [-0.1743, +0.0617] | +0.0000* | [-0.2839, +0.2435] | -0.0667 | 2.81% | 0.6376 | 1.30% | 0.2957 | 0.4595 | 2.46% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 10 | +0.1117 | [+0.0203, +0.1929] | +0.0732* | [-0.1701, +0.2448] | +0.7576 | 7.16% | 0.8994 | 4.34% | 0.5451 | 1.2981 | 9.38% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__short_sell_quantity__roc60` | +1 | +0.0323 | +0.1514 | +0.1507 | 0.0032 | +0.7141 | +0.7848 | 0.000 |

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
| `combo_diff__max_up_ret__willr14` | +1 | +0.1032 | +0.3162 | +0.3164 | 0.0000 | +1.2688 | +0.8991 | 0.000 |
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1875 | +0.2997 | +0.2999 | 0.0000 | +0.7675 | +0.7419 | 0.451 |
| `combo_tri_median__max_up_ret__bar_vwap_dev_2__gap_pct` | +1 | +0.1874 | +0.2922 | +0.2912 | 0.0000 | +0.8389 | +0.8493 | 0.590 |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | +1 | +0.1477 | +0.2898 | +0.2901 | 0.0000 | +0.6922 | +0.7320 | 0.492 |
| `combo_rank_min__max_down_ret__early_range` | +1 | +0.1396 | +0.2858 | +0.2851 | 0.0000 | +0.6766 | +0.7226 | 0.585 |
| `combo_rank_min__max_up_ret__gap_pct` | +1 | +0.1196 | +0.2816 | +0.2810 | 0.0000 | +0.4766 | +0.6463 | 0.675 |
| `combo_tri_median__max_up_ret__max_down_ret__yesterday_illiquidity_amihud` | +1 | +0.1563 | +0.2794 | +0.2796 | 0.0000 | +1.0285 | +0.8211 | 0.647 |
| `combo_ifelse__gap_pct__max_up_ret__bar_vwap_dev_2` | +1 | +0.1425 | +0.2786 | +0.2781 | 0.0000 | +0.5209 | +0.6962 | 0.745 |
| `combo_tri_median__max_up_ret__num_up_bars__bar_body_rng_0` | +1 | +0.1642 | +0.2751 | +0.2747 | 0.0000 | +0.6851 | +0.7578 | 0.664 |
| `combo_tri_mean__max_up_ret__max_down_ret__bar_body_rng_0` | +1 | +0.1762 | +0.2724 | +0.2716 | 0.0000 | +0.6844 | +0.7114 | 0.828 |
| `combo_ratio__max_up_ret__vol60` | +1 | +0.1758 | +0.2718 | +0.2718 | 0.0000 | +0.6855 | +0.7677 | 0.740 |
| `combo_ifelse__vol20__max_up_ret__bar_ret_0` | +1 | +0.1829 | +0.2674 | +0.2668 | 0.0000 | +0.8542 | +0.8141 | 0.768 |
| `combo_min__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.1247 | +0.2645 | +0.2637 | 0.0000 | +0.6687 | +0.7695 | 0.829 |
| `combo_ifelse__atr14_norm__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.1167 | +0.2643 | +0.2645 | 0.0000 | +0.9474 | +0.7701 | 0.835 |
| `combo_tri_max__max_up_ret__max_down_ret__bar_body_rng_1` | +1 | +0.1312 | +0.2579 | +0.2577 | 0.0000 | +0.6398 | +0.7038 | 0.765 |
| `combo_ifelse__vol60__max_up_ret__yesterday_early_vwap_dev` | +1 | +0.1511 | +0.2562 | +0.2566 | 0.0000 | +0.6705 | +0.7625 | 0.794 |
| `combo_ratio__max_up_ret__vol_ratio_10_60` | +1 | +0.1541 | +0.2532 | +0.2528 | 0.0000 | +0.6389 | +0.7279 | 0.795 |
| `combo_mean__max_up_ret__bar_vwap_dev_1` | +1 | +0.1563 | +0.2529 | +0.2523 | 0.0000 | +0.8233 | +0.7777 | 0.835 |
| `combo_rank_min__max_up_ret__bar_vwap_dev_2` | +1 | +0.1308 | +0.2519 | +0.2525 | 0.0000 | +0.5124 | +0.6616 | 0.706 |
| `combo_tri_max__max_up_ret__max_down_ret__num_up_bars` | +1 | +0.1506 | +0.2517 | +0.2508 | 0.0000 | +0.6346 | +0.7273 | 0.844 |
| `combo_tri_median__max_up_ret__bar_ret_0__body_to_range_ratio` | +1 | +0.1800 | +0.2497 | +0.2491 | 0.0000 | +0.7496 | +0.7396 | 0.841 |
| `combo_min__max_up_ret__gap_pct` | +1 | +0.1457 | +0.2485 | +0.2478 | 0.0000 | +0.4746 | +0.6411 | 0.704 |
| `combo_mean__max_up_ret__bar_ret_2` | +1 | +0.1451 | +0.2480 | +0.2480 | 0.0000 | +0.6455 | +0.7144 | 0.755 |
| `combo_tri_mean__max_up_ret__max_down_ret__bar_body_rng_1` | +1 | +0.1500 | +0.2479 | +0.2479 | 0.0000 | +0.7118 | +0.7619 | 0.849 |
| `combo_rank_min__max_up_ret__vix_realized_spread` | +1 | +0.1306 | +0.2466 | +0.2454 | 0.0000 | +0.3374 | +0.6411 | 0.721 |
| `combo_ifelse__atr14_norm__max_up_ret__bar_vwap_dev_2` | +1 | +0.1723 | +0.2459 | +0.2454 | 0.0000 | +0.6421 | +0.7548 | 0.832 |
| `combo_mean__max_up_ret__body_to_range_ratio` | +1 | +0.1504 | +0.2447 | +0.2443 | 0.0000 | +0.9315 | +0.8164 | 0.807 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.0893 | +0.2390 | +0.2377 | 0.0000 | +0.7971 | +0.7636 | 0.706 |
| `combo_abs_diff__max_up_ret__vix_realized_spread` | +1 | +0.0733 | +0.2360 | +0.2376 | 0.0000 | +0.7173 | +0.7396 | 0.733 |
| `combo_rank_min__max_down_ret__atr14_norm` | +1 | +0.1059 | +0.2348 | +0.2343 | 0.0000 | +0.4407 | +0.6346 | 0.779 |
| `combo_min__max_down_ret__early_range` | +1 | +0.1332 | +0.2337 | +0.2334 | 0.0000 | +0.5174 | +0.7179 | 0.700 |
| `combo_product__max_down_ret__early_range` | +1 | +0.0708 | +0.2333 | +0.2334 | 0.0000 | +0.3594 | +0.6387 | 0.829 |
| `combo_ifelse__macd_hist__max_up_ret__max_down_ret` | +1 | +0.1483 | +0.2326 | +0.2322 | 0.0000 | +0.5031 | +0.6364 | 0.744 |
| `combo_rank_max__max_up_ret__vix_realized_spread` | +1 | +0.1743 | +0.2318 | +0.2306 | 0.0000 | +0.8797 | +0.7982 | 0.820 |
| `combo_max__max_up_ret__gap_pct` | +1 | +0.1624 | +0.2314 | +0.2315 | 0.0000 | +0.7603 | +0.8065 | 0.753 |
| `combo_ifelse__macd_hist__max_up_ret__yesterday_early_momentum` | +1 | +0.1247 | +0.2299 | +0.2319 | 0.0000 | +0.3877 | +0.6604 | 0.482 |
| `combo_diff__max_up_ret__vol20` | +1 | +0.1349 | +0.2294 | +0.2303 | 0.0000 | +0.7270 | +0.7730 | 0.738 |
| `combo_clamp_diff__max_up_ret__vol60` | +1 | +0.1496 | +0.2279 | +0.2287 | 0.0000 | +0.6415 | +0.7466 | 0.832 |
| `combo_ratio__max_down_ret__bar_vol_5` | +1 | +0.1388 | +0.2276 | +0.2269 | 0.0000 | +0.4691 | +0.6575 | 0.732 |
| `combo_mean__max_down_ret__bar_vwap_dev_2` | +1 | +0.1270 | +0.2260 | +0.2257 | 0.0000 | +0.5402 | +0.7630 | 0.795 |
| `combo_ifelse__gap_pct__bar_ret_0__num_up_bars` | +1 | +0.1316 | +0.2254 | +0.2236 | 0.0000 | +0.4595 | +0.6809 | 0.748 |
| `combo_tri_median__max_up_ret__bar_body_rng_0__northbound_volume_share` | +1 | +0.1630 | +0.2251 | +0.2256 | 0.0000 | +0.9340 | +0.8229 | 0.806 |
| `combo_ifelse__gap_pct__max_up_ret__first_30min_return` | +1 | +0.1432 | +0.2241 | +0.2238 | 0.0000 | +0.7080 | +0.7701 | 0.788 |
| `combo_ifelse__macd_hist__max_up_ret__bar_body_rng_0` | +1 | +0.1526 | +0.2234 | +0.2225 | 0.0000 | +0.5325 | +0.7009 | 0.780 |
| `combo_product__num_up_bars__body_to_range_ratio` | +1 | +0.1004 | +0.2225 | +0.2243 | 0.0000 | +0.4594 | +0.6856 | 0.553 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | +1 | +0.0928 | +0.2200 | +0.2180 | 0.0000 | +0.5425 | +0.6903 | 0.824 |
| `combo_ifelse__atr14_norm__max_up_ret__yesterday_afternoon_momentum` | +1 | +0.1177 | +0.2191 | +0.2184 | 0.0000 | +0.5716 | +0.6845 | 0.845 |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | +1 | +0.1544 | +0.2191 | +0.2192 | 0.0000 | +0.8249 | +0.7736 | 0.795 |
| `combo_rank_min__max_up_ret__atr14_norm` | +1 | +0.1179 | +0.2186 | +0.2185 | 0.0000 | +1.0259 | +0.8287 | 0.778 |
| `combo_rank_min__max_down_ret__bar_ret_1` | +1 | +0.1139 | +0.2154 | +0.2150 | 0.0000 | +0.5166 | +0.6938 | 0.744 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | +1 | +0.1122 | +0.2154 | +0.2144 | 0.0000 | +0.4769 | +0.6762 | 0.484 |
| `combo_rank_max__max_down_ret__bar_body_rng_0` | +1 | +0.1619 | +0.2150 | +0.2142 | 0.0000 | +0.6006 | +0.6868 | 0.840 |
| `combo_min__max_down_ret__bar_ret_1` | +1 | +0.1007 | +0.2133 | +0.2130 | 0.0000 | +0.3841 | +0.6457 | 0.830 |
| `combo_abs_diff__vol_ratio_10_60__volatility_percentile_20d` | +1 | +0.0926 | +0.2115 | +0.2087 | 0.0000 | +0.4320 | +0.6827 | 0.112 |
| `combo_rank_min__max_up_ret__yesterday_range_ratio` | +1 | +0.1221 | +0.2107 | +0.2104 | 0.0000 | +0.7661 | +0.7736 | 0.846 |
| `combo_ifelse__macd_hist__max_up_ret__bar_vwap_dev_2` | +1 | +0.1375 | +0.2099 | +0.2109 | 0.0000 | +0.4974 | +0.7173 | 0.727 |
| `combo_min__max_down_ret__bar_vwap_dev_3` | +1 | +0.0916 | +0.2086 | +0.2087 | 0.0000 | +0.5507 | +0.6868 | 0.845 |
| `combo_max__bar_ret_0__max_down_ret` | +1 | +0.1655 | +0.2083 | +0.2078 | 0.0000 | +0.6179 | +0.7144 | 0.815 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | +1 | +0.0972 | +0.2067 | +0.2071 | 0.0000 | +0.4144 | +0.6393 | 0.591 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_vwap_dev_2` | +1 | +0.1067 | +0.2066 | +0.2078 | 0.0000 | +0.4080 | +0.6012 | 0.641 |
| `combo_mean__max_up_ret__bar_vwap_dev_3` | +1 | +0.1284 | +0.2057 | +0.2046 | 0.0000 | +0.7915 | +0.7830 | 0.835 |
| `combo_mean__max_up_ret__vol_ratio_10_60` | +1 | +0.1385 | +0.2050 | +0.2044 | 0.0000 | +1.0079 | +0.8182 | 0.721 |
| `combo_rank_min__max_down_ret__bar_vwap_dev_3` | +1 | +0.0970 | +0.2044 | +0.2047 | 0.0000 | +0.5646 | +0.7097 | 0.691 |
| `combo_max__max_up_ret__cci14` | +1 | +0.1330 | +0.2034 | +0.2034 | 0.0000 | +0.3922 | +0.6557 | 0.701 |
| `combo_mean__max_up_ret__macd_hist` | +1 | +0.1520 | +0.2033 | +0.2026 | 0.0000 | +0.5227 | +0.6944 | 0.675 |
| `combo_diff__max_up_ret__yesterday_day_range` | +1 | +0.1456 | +0.2029 | +0.2028 | 0.0000 | +0.5388 | +0.6780 | 0.673 |
| `combo_rank_min__max_down_ret__first_30min_return` | +1 | +0.1435 | +0.1987 | +0.1979 | 0.0000 | +0.5673 | +0.7132 | 0.791 |
| `combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0` | +1 | +0.1535 | +0.1983 | +0.1980 | 0.0000 | +0.6183 | +0.6985 | 0.836 |
| `combo_ratio__max_down_ret__vol60` | +1 | +0.1275 | +0.1975 | +0.1963 | 0.0000 | +0.5189 | +0.6645 | 0.741 |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | +1 | +0.1151 | +0.1972 | +0.1973 | 0.0000 | +0.4947 | +0.6686 | 0.541 |
| `combo_rank_min__max_up_ret__vol_ratio_10_60` | +1 | +0.1071 | +0.1929 | +0.1932 | 0.0000 | +0.6155 | +0.7208 | 0.812 |
| `combo_ifelse__vol60__first_bar_return__yesterday_illiquidity_amihud` | +1 | +0.1085 | +0.1895 | +0.1897 | 0.0000 | +0.5180 | +0.6698 | 0.794 |
| `combo_ifelse__gap_pct__first_bar_return__bar_body_rng_0` | +1 | +0.1539 | +0.1860 | +0.1853 | 0.0002 | +0.5115 | +0.7073 | 0.840 |
| `combo_clamp_diff__max_down_ret__vix_realized_spread` | +1 | +0.1335 | +0.1855 | +0.1848 | 0.0004 | +0.4833 | +0.6452 | 0.825 |
| `combo_ifelse__vol60__first_bar_return__yesterday_early_momentum` | +1 | +0.1376 | +0.1814 | +0.1826 | 0.0006 | +0.3514 | +0.6416 | 0.818 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__first_30min_return` | +1 | +0.1127 | +0.1778 | +0.1795 | 0.0006 | +0.3964 | +0.6962 | 0.823 |
| `combo_rank_max__max_up_ret__bar_vwap_dev_1` | +1 | +0.1395 | +0.1766 | +0.1766 | 0.0006 | +0.6985 | +0.7613 | 0.771 |
| `combo_ifelse__macd_hist__bar_ret_0__num_up_bars` | +1 | +0.1226 | +0.1721 | +0.1705 | 0.0010 | +0.4984 | +0.7091 | 0.756 |
| `combo_ifelse__gap_pct__first_30min_return__num_up_bars` | +1 | +0.0992 | +0.1713 | +0.1693 | 0.0012 | +0.3880 | +0.6575 | 0.849 |
| `combo_ifelse__atr14_norm__first_bar_return__bar_vwap_dev_2` | +1 | +0.1586 | +0.1706 | +0.1706 | 0.0014 | +0.4211 | +0.6880 | 0.833 |
| `combo_ifelse__macd_hist__bar_ret_0__first_30min_return` | +1 | +0.1430 | +0.1703 | +0.1689 | 0.0014 | +0.5841 | +0.7067 | 0.833 |
| `combo_rank_min__bar_body_rng_0__northbound_volume_share` | +1 | +0.0692 | +0.1642 | +0.1652 | 0.0030 | +0.4372 | +0.6745 | 0.619 |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | +1 | +0.0782 | +0.1640 | +0.1654 | 0.0030 | +0.5690 | +0.6839 | 0.400 |
| `combo_ifelse__vol20__first_30min_return__yesterday_illiquidity_amihud` | +1 | +0.0590 | +0.1616 | +0.1618 | 0.0034 | +0.5196 | +0.6798 | 0.768 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud` | +1 | +0.0642 | +0.1569 | +0.1570 | 0.0042 | +0.4607 | +0.6358 | 0.566 |
| `combo_abs_diff__max_up_ret__cci14` | +1 | +0.0353 | +0.1556 | +0.1553 | 0.0042 | +0.3059 | +0.6082 | 0.768 |
| `combo_ifelse__vol20__first_30min_return__yesterday_early_momentum` | +1 | +0.1070 | +0.1549 | +0.1555 | 0.0046 | +0.3568 | +0.6176 | 0.825 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_body_rng_0` | +1 | +0.1191 | +0.1549 | +0.1564 | 0.0046 | +0.3391 | +0.6070 | 0.739 |
| `combo_ifelse__vol60__first_bar_return__yesterday_afternoon_momentum` | +1 | +0.1002 | +0.1525 | +0.1522 | 0.0054 | +0.3535 | +0.6246 | 0.843 |

### 500ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_abs_diff__cci14__max_up_ret` | +1 | +0.0353 | +0.2319 | +0.2316 | 0.0000 | +0.4572 | +0.6581 | 0.000 |

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | +1 | +0.1720 | +0.4122 | +0.4109 | 0.0000 | +1.1922 | +0.8539 | 0.000 |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol5__bar_body_rng_1` | +1 | +0.1235 | +0.3896 | +0.3863 | 0.0000 | +1.1815 | +0.8480 | 0.697 |
| `combo_tri_ifelse__vix__atr14_norm__vix_skew_proxy__vol5__first_bar_return` | +1 | +0.1429 | +0.3848 | +0.3826 | 0.0000 | +0.8705 | +0.7552 | 0.791 |
| `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__bar_ret_0__max_down_ret` | +1 | +0.1584 | +0.3840 | +0.3812 | 0.0000 | +1.0851 | +0.8588 | 0.811 |
| `combo_tri_ifelse__vix__vol20__vix_diff_1d__short_sell_cover_spread__first_bar_return` | +1 | +0.1109 | +0.3502 | +0.3495 | 0.0000 | +0.7898 | +0.7927 | 0.835 |
| `combo_tri_ifelse__vix__atr14_norm__vix_diff_1d__yesterday_day_realized_vol__max_down_ret` | +1 | +0.1714 | +0.3455 | +0.3445 | 0.0000 | +1.1364 | +0.8796 | 0.842 |
| `combo_tri_ifelse__vix__atr14_norm__vix_skew_proxy__vol5__num_up_bars` | +1 | +0.1498 | +0.3420 | +0.3408 | 0.0000 | +0.8704 | +0.7828 | 0.806 |
| `combo_tri_ifelse__vix__atr14_norm__vix_skew_proxy__vol_gk10__early_momentum` | +1 | +0.1272 | +0.3407 | +0.3419 | 0.0000 | +1.1476 | +0.8697 | 0.800 |
| `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__bar_ret_0__early_momentum` | +1 | +0.1322 | +0.3405 | +0.3398 | 0.0000 | +1.0799 | +0.8588 | 0.842 |
| `combo_tri_mean__vix_diff_1d__vix__max_down_ret` | +1 | +0.1737 | +0.3390 | +0.3374 | 0.0000 | +1.1034 | +0.8036 | 0.652 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_body_rng_1` | +1 | +0.1160 | +0.3384 | +0.3359 | 0.0000 | +1.1746 | +0.8480 | 0.685 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__short_sell_cover_spread__max_down_ret` | +1 | +0.1295 | +0.3375 | +0.3356 | 0.0000 | +1.1612 | +0.8717 | 0.540 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__first_bar_return` | +1 | +0.1243 | +0.3366 | +0.3352 | 0.0000 | +0.7621 | +0.7374 | 0.741 |
| `combo_tri_mean__vix_diff_1d__max_up_ret__vix` | +1 | +0.1325 | +0.3345 | +0.3345 | 0.0000 | +0.6427 | +0.7493 | 0.834 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol5__early_momentum` | +1 | +0.1275 | +0.3282 | +0.3284 | 0.0000 | +1.1824 | +0.8657 | 0.693 |
| `combo_ifelse__vol10__vix_skew_proxy__first_30min_return` | +1 | +0.1473 | +0.3280 | +0.3266 | 0.0000 | +1.2494 | +0.8806 | 0.829 |
| `combo_tri_ifelse__vix__vol20__max_up_ret__vol_gk10__max_down_ret` | +1 | +0.1433 | +0.3234 | +0.3229 | 0.0000 | +1.0391 | +0.8332 | 0.677 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol5__num_up_bars` | +1 | +0.1396 | +0.3218 | +0.3213 | 0.0000 | +0.8631 | +0.7848 | 0.845 |
| `combo_tri_max__max_up_ret__vol5__max_down_ret` | +1 | +0.1505 | +0.3161 | +0.3153 | 0.0000 | +1.2134 | +0.8944 | 0.614 |
| `combo_tri_mean__vix_skew_proxy__yesterday_day_realized_vol__max_down_ret` | +1 | +0.1716 | +0.3142 | +0.3140 | 0.0000 | +1.0057 | +0.8282 | 0.820 |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__max_up_ret__max_down_ret` | +1 | +0.1673 | +0.3092 | +0.3076 | 0.0000 | +0.9815 | +0.8371 | 0.803 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol5__max_down_ret` | +1 | +0.1514 | +0.3071 | +0.3056 | 0.0000 | +1.0280 | +0.8361 | 0.810 |
| `combo_rank_max__max_up_ret__vol5` | +1 | +0.1215 | +0.3060 | +0.3059 | 0.0000 | +0.8956 | +0.8144 | 0.626 |
| `combo_tri_median__first_30min_return__max_up_ret__early_skew` | +1 | +0.1263 | +0.3049 | +0.3055 | 0.0000 | +0.9033 | +0.8312 | 0.604 |
| `combo_ifelse__vol20__vol5__bar_body_rng_1` | +1 | +0.1050 | +0.3011 | +0.2991 | 0.0000 | +0.9938 | +0.8016 | 0.820 |
| `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.1118 | +0.3010 | +0.2995 | 0.0000 | +0.7289 | +0.7947 | 0.797 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol_gk10__max_down_ret` | +1 | +0.1475 | +0.3001 | +0.3007 | 0.0000 | +0.9814 | +0.8401 | 0.827 |
| `combo_ifelse__atr14_norm__vol5__bar_ret_0` | +1 | +0.1234 | +0.2943 | +0.2931 | 0.0000 | +0.6600 | +0.7029 | 0.778 |
| `combo_ifelse__vol10__vix_skew_proxy__bar_body_rng_1` | +1 | +0.1144 | +0.2928 | +0.2897 | 0.0000 | +1.0705 | +0.8569 | 0.814 |
| `combo_abs_diff__max_up_ret__vol_gk10` | +1 | +0.1074 | +0.2902 | +0.2924 | 0.0000 | +0.9459 | +0.8322 | 0.646 |
| `combo_tri_max__max_up_ret__vol_gk10__max_down_ret` | +1 | +0.1486 | +0.2898 | +0.2915 | 0.0000 | +1.0978 | +0.8342 | 0.830 |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vix_rolling_percentile_60d__max_down_ret` | +1 | +0.1544 | +0.2887 | +0.2859 | 0.0000 | +0.9575 | +0.8302 | 0.834 |
| `combo_diff__vix_skew_proxy__gap_pct` | +1 | +0.0793 | +0.2887 | +0.2905 | 0.0000 | +0.5736 | +0.6989 | 0.486 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__short_sell_cover_spread__first_bar_return` | +1 | +0.0963 | +0.2887 | +0.2877 | 0.0000 | +0.7521 | +0.7749 | 0.800 |
| `combo_tri_ifelse__vix__vol20__vol5__vol_gk10__max_down_ret` | +1 | +0.1522 | +0.2885 | +0.2884 | 0.0000 | +0.9743 | +0.8144 | 0.760 |
| `combo_abs_diff__max_up_ret__vol10` | +1 | +0.1155 | +0.2882 | +0.2914 | 0.0000 | +0.9051 | +0.8006 | 0.841 |
| `combo_min__max_up_ret__early_skew` | +1 | +0.1148 | +0.2878 | +0.2895 | 0.0000 | +0.6133 | +0.7621 | 0.684 |
| `combo_max__max_down_ret__vol10` | +1 | +0.1438 | +0.2871 | +0.2863 | 0.0000 | +1.4708 | +0.9279 | 0.798 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_ret_0__num_up_bars` | +1 | +0.1191 | +0.2870 | +0.2866 | 0.0000 | +0.7416 | +0.7384 | 0.693 |
| `combo_ifelse__vix__vix_skew_proxy__bar_ret_0` | +1 | +0.1277 | +0.2846 | +0.2823 | 0.0000 | +0.8798 | +0.7670 | 0.840 |
| `combo_tri_median__vix_diff_1d__vix__max_down_ret` | +1 | +0.1586 | +0.2823 | +0.2822 | 0.0000 | +0.7411 | +0.7552 | 0.796 |
| `combo_rank_max__vol5__max_down_ret` | +1 | +0.1271 | +0.2820 | +0.2803 | 0.0000 | +0.9555 | +0.7858 | 0.790 |
| `combo_clamp_diff__vix_skew_proxy__gap_pct` | +1 | +0.0789 | +0.2813 | +0.2831 | 0.0000 | +0.5667 | +0.6851 | 0.836 |
| `combo_rank_max__max_up_ret__bar_rng_3` | +1 | +0.1075 | +0.2809 | +0.2814 | 0.0000 | +0.6715 | +0.7818 | 0.614 |
| `combo_ifelse__gap_pct__vix_skew_proxy__bar_ret_1` | +1 | +0.1378 | +0.2801 | +0.2803 | 0.0000 | +0.8544 | +0.7878 | 0.666 |
| `combo_min__vix_skew_proxy__vix` | +1 | +0.0933 | +0.2792 | +0.2792 | 0.0000 | +0.3610 | +0.6229 | 0.691 |
| `combo_max__atr14_norm__max_down_ret` | +1 | +0.1386 | +0.2764 | +0.2775 | 0.0000 | +1.3167 | +0.8835 | 0.808 |
| `combo_tri_ifelse__atr14_norm__vol20__vol_gk10__num_up_bars__max_down_ret` | +1 | +0.1411 | +0.2759 | +0.2771 | 0.0000 | +0.8547 | +0.7828 | 0.821 |
| `combo_tri_max__first_30min_return__bar_ret_0__early_skew` | +1 | +0.0957 | +0.2745 | +0.2767 | 0.0000 | +0.9187 | +0.7897 | 0.784 |
| `combo_tri_ifelse__atr14_norm__vol20__vix_rolling_percentile_60d__bar_ret_0__max_down_ret` | +1 | +0.1442 | +0.2713 | +0.2687 | 0.0000 | +1.1342 | +0.8657 | 0.800 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_body_rng_1__early_momentum` | +1 | +0.1253 | +0.2708 | +0.2706 | 0.0000 | +1.0330 | +0.8381 | 0.658 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__early_skew__max_down_ret` | +1 | +0.1384 | +0.2704 | +0.2719 | 0.0000 | +0.7719 | +0.8036 | 0.699 |
| `combo_ifelse__gap_pct__vix_skew_proxy__first_30min_return` | +1 | +0.1327 | +0.2687 | +0.2698 | 0.0000 | +0.8353 | +0.7818 | 0.736 |
| `combo_tri_ifelse__atr14_norm__vol20__yesterday_day_realized_vol__northbound_net__max_down_ret` | +1 | +0.1388 | +0.2686 | +0.2679 | 0.0000 | +1.2187 | +0.8885 | 0.707 |
| `combo_tri_ifelse__vix__atr14_norm__vol5__yesterday_day_realized_vol__max_down_ret` | +1 | +0.1516 | +0.2647 | +0.2648 | 0.0000 | +0.8306 | +0.8322 | 0.830 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__bar_ret_0__max_down_ret` | +1 | +0.1377 | +0.2638 | +0.2619 | 0.0000 | +1.2632 | +0.8717 | 0.804 |
| `combo_tri_mean__vix_diff_1d__vix_rolling_percentile_60d__yesterday_day_realized_vol` | +1 | +0.0651 | +0.2609 | +0.2619 | 0.0002 | +0.5000 | +0.6229 | 0.711 |
| `combo_ifelse__gap_pct__vol5__bar_body_rng_1` | +1 | +0.1086 | +0.2579 | +0.2566 | 0.0002 | +0.9017 | +0.7769 | 0.574 |
| `combo_ifelse__gap_pct__vix_skew_proxy__first_bar_return` | +1 | +0.0821 | +0.2577 | +0.2573 | 0.0002 | +0.6630 | +0.7384 | 0.844 |
| `combo_rank_max__max_up_ret__vol_gk10` | +1 | +0.1122 | +0.2575 | +0.2596 | 0.0002 | +0.8299 | +0.8026 | 0.737 |
| `combo_max__max_up_ret__yesterday_day_realized_vol` | +1 | +0.0943 | +0.2535 | +0.2543 | 0.0002 | +0.8430 | +0.7739 | 0.801 |
| `combo_rank_max__max_down_ret__vol10` | +1 | +0.1076 | +0.2527 | +0.2518 | 0.0002 | +1.0917 | +0.8569 | 0.817 |
| `combo_ifelse__vol20__vix_diff_1d__bar_ret_1` | +1 | +0.1201 | +0.2507 | +0.2485 | 0.0002 | +1.0524 | +0.8016 | 0.849 |
| `combo_rank_min__vix_diff_1d__bar_rng_5` | +1 | +0.1041 | +0.2455 | +0.2447 | 0.0002 | +0.5318 | +0.6634 | 0.494 |
| `combo_ifelse__vol10__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.0925 | +0.2454 | +0.2433 | 0.0002 | +0.7846 | +0.7868 | 0.627 |
| `combo_ifelse__gap_pct__vol5__bar_ret_0` | +1 | +0.0637 | +0.2383 | +0.2368 | 0.0008 | +0.5101 | +0.6940 | 0.612 |
| `combo_ifelse__gap_pct__vix_rolling_percentile_60d__first_bar_return` | +1 | +0.0598 | +0.2378 | +0.2369 | 0.0008 | +0.6266 | +0.7423 | 0.666 |
| `combo_rank_max__max_up_ret__first_bar_return` | +1 | +0.1056 | +0.2351 | +0.2347 | 0.0010 | +0.8085 | +0.7976 | 0.817 |
| `combo_ifelse__atr14_norm__vix_diff_1d__vix_skew_proxy` | +1 | +0.1053 | +0.2333 | +0.2326 | 0.0012 | +0.3327 | +0.6426 | 0.801 |
| `combo_ifelse__vix__max_up_ret__first_bar_return` | +1 | +0.0963 | +0.2307 | +0.2291 | 0.0014 | +0.8377 | +0.7660 | 0.765 |
| `combo_ifelse__vol20__max_up_ret__first_bar_return` | +1 | +0.1144 | +0.2295 | +0.2286 | 0.0014 | +0.7992 | +0.7483 | 0.846 |
| `combo_ifelse__vol20__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.1030 | +0.2293 | +0.2270 | 0.0014 | +0.6079 | +0.7354 | 0.807 |
| `combo_rank_min__vix_rolling_percentile_60d__vix` | +1 | +0.0693 | +0.2282 | +0.2286 | 0.0016 | +0.3003 | +0.6091 | 0.540 |
| `combo_rank_max__vix_rolling_percentile_60d__vol5` | +1 | +0.0505 | +0.2280 | +0.2282 | 0.0016 | +0.4547 | +0.6950 | 0.535 |
| `combo_min__vix_diff_1d__bar_rng_5` | +1 | +0.0958 | +0.2276 | +0.2259 | 0.0016 | +0.4995 | +0.6387 | 0.748 |
| `combo_ifelse__vix__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.1113 | +0.2267 | +0.2247 | 0.0016 | +0.7270 | +0.7384 | 0.814 |
| `combo_ifelse__atr14_norm__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.0963 | +0.2245 | +0.2225 | 0.0016 | +0.7214 | +0.7423 | 0.797 |
| `combo_tri_min__vix_rolling_percentile_60d__vol5__vix` | +1 | +0.0692 | +0.2207 | +0.2217 | 0.0016 | +0.5915 | +0.6989 | 0.799 |
| `combo_tri_median__max_up_ret__vix_rolling_percentile_60d__vol20` | +1 | +0.0899 | +0.2206 | +0.2223 | 0.0016 | +0.7312 | +0.7512 | 0.757 |
| `combo_ratio__max_up_ret__vol10` | +1 | +0.1106 | +0.2198 | +0.2197 | 0.0018 | +1.0137 | +0.8342 | 0.831 |
| `combo_max__max_up_ret__vix` | +1 | +0.1087 | +0.2185 | +0.2193 | 0.0018 | +0.7481 | +0.7838 | 0.838 |
| `combo_tri_max__vix_rolling_percentile_60d__vol5__max_down_ret` | +1 | +0.1326 | +0.2147 | +0.2138 | 0.0020 | +0.7439 | +0.7562 | 0.768 |
| `combo_ifelse__vol10__vix_rolling_percentile_60d__first_bar_return` | +1 | +0.0925 | +0.2147 | +0.2154 | 0.0020 | +0.6718 | +0.7394 | 0.648 |
| `combo_rank_min__vix_diff_1d__max_up_ret` | +1 | +0.1247 | +0.2128 | +0.2133 | 0.0026 | +0.4140 | +0.6486 | 0.644 |
| `combo_ifelse__vol20__vix_rolling_percentile_60d__first_bar_return` | +1 | +0.1057 | +0.2119 | +0.2115 | 0.0026 | +0.6307 | +0.7502 | 0.800 |
| `combo_min__max_up_ret__bar_rng_5` | +1 | +0.0838 | +0.2101 | +0.2085 | 0.0028 | +0.7177 | +0.7315 | 0.647 |
| `combo_rank_min__vol5__bar_rng_5` | +1 | +0.0673 | +0.2071 | +0.2062 | 0.0034 | +0.6247 | +0.7730 | 0.572 |
| `combo_ifelse__vol10__vix_skew_proxy__vol5` | +1 | +0.0579 | +0.2025 | +0.2019 | 0.0038 | +0.6822 | +0.7838 | 0.831 |
| `combo_ifelse__vol20__max_up_ret__vix_rolling_percentile_60d` | +1 | +0.0363 | +0.1887 | +0.1896 | 0.0074 | +0.3811 | +0.6683 | 0.673 |
| `combo_ifelse__vix__vol5__bar_ret_0` | +1 | +0.1075 | +0.1869 | +0.1857 | 0.0082 | +0.7347 | +0.7394 | 0.773 |

### 588000ETF / long
No features admitted.

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__max_up_ret__bar_ret_0__gap_pct` | +1 | +0.1392 | +0.2714 | +0.2686 | 0.0000 | +0.5300 | +0.6657 | 0.000 |
| `combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0` | +1 | +0.1388 | +0.2699 | +0.2682 | 0.0000 | +0.4522 | +0.6704 | 0.312 |
| `combo_tri_median__max_up_ret__max_down_ret__yearly_high_distance` | +1 | +0.1217 | +0.2463 | +0.2455 | 0.0000 | +0.4118 | +0.6698 | 0.419 |
| `combo_ifelse__bb_width__max_up_ret__bar_body_rng_0` | +1 | +0.1510 | +0.2402 | +0.2379 | 0.0000 | +0.4801 | +0.6604 | 0.698 |
| `combo_tri_max__max_up_ret__first_bar_return__first_30min_return` | +1 | +0.1352 | +0.2376 | +0.2357 | 0.0000 | +0.5395 | +0.7255 | 0.710 |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__capital_sell_volume__margin_buy_repayment_spread` | +1 | +0.1250 | +0.2373 | +0.2351 | 0.0000 | +0.4275 | +0.6416 | 0.447 |
| `combo_tri_median__max_up_ret__bar_vol_5__max_down_ret` | +1 | +0.1184 | +0.2297 | +0.2290 | 0.0000 | +0.3724 | +0.6188 | 0.760 |
| `combo_rank_max__max_up_ret__first_30min_return` | +1 | +0.1225 | +0.2205 | +0.2189 | 0.0000 | +0.5743 | +0.7419 | 0.837 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | +1 | +0.1390 | +0.2190 | +0.2182 | 0.0000 | +0.4880 | +0.6991 | 0.396 |
| `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_first_30min_return` | +1 | +0.1302 | +0.2077 | +0.2062 | 0.0000 | +0.5842 | +0.7097 | 0.721 |
| `combo_max__max_up_ret__vol_ratio_10_60` | +1 | +0.1129 | +0.2032 | +0.2014 | 0.0002 | +0.6927 | +0.7783 | 0.680 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | +1 | +0.1185 | +0.2030 | +0.2005 | 0.0002 | +0.3393 | +0.6434 | 0.725 |
| `combo_mean__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.1203 | +0.1939 | +0.1927 | 0.0002 | +0.5364 | +0.6581 | 0.742 |
| `combo_ifelse__gap_pct__max_up_ret__early_range` | +1 | +0.1319 | +0.1928 | +0.1916 | 0.0004 | +0.9726 | +0.8111 | 0.703 |
| `combo_ifelse__gap_pct__max_up_ret__bar_vol_5` | +1 | +0.1339 | +0.1885 | +0.1886 | 0.0004 | +0.5958 | +0.6956 | 0.610 |
| `combo_ifelse__gap_pct__bar_body_rng_0__bar_vol_5` | +1 | +0.1255 | +0.1842 | +0.1837 | 0.0006 | +0.3525 | +0.6317 | 0.801 |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | +1 | +0.1122 | +0.1825 | +0.1826 | 0.0006 | +0.6162 | +0.7120 | 0.516 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_trend` | +1 | +0.1410 | +0.1790 | +0.1770 | 0.0010 | +0.4642 | +0.6622 | 0.844 |
| `combo_ifelse__gap_pct__first_bar_return__early_range` | +1 | +0.1267 | +0.1728 | +0.1708 | 0.0014 | +0.5853 | +0.7167 | 0.849 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_diff__short_sell_quantity__roc60` | `diff` | a=`short_sell_quantity`, b=`roc60` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_rank_min__max_up_ret__gap_pct` | `rank_min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__bar_vwap_dev_2` | `ifelse` | a=`max_up_ret`, b=`bar_vwap_dev_2`, cond=`gap_pct` |
| `combo_min__max_up_ret__yesterday_illiquidity_amihud` | `min` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_rank_min__max_up_ret__bar_vwap_dev_2` | `rank_min` | a=`max_up_ret`, b=`bar_vwap_dev_2` |
| `combo_tri_max__max_up_ret__max_down_ret__num_up_bars` | `tri_max` | a=`max_up_ret`, b=`max_down_ret`, c=`num_up_bars` |
| `combo_min__max_up_ret__gap_pct` | `min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_mean__max_up_ret__body_to_range_ratio` | `mean` | a=`max_up_ret`, b=`body_to_range_ratio` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_illiquidity_amihud` | `ifelse` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_max__max_up_ret__gap_pct` | `max` | a=`max_up_ret`, b=`gap_pct` |
| `combo_mean__max_down_ret__bar_vwap_dev_2` | `mean` | a=`max_down_ret`, b=`bar_vwap_dev_2` |
| `combo_ifelse__gap_pct__bar_ret_0__num_up_bars` | `ifelse` | a=`bar_ret_0`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__first_30min_return` | `ifelse` | a=`max_up_ret`, b=`first_30min_return`, cond=`gap_pct` |
| `combo_product__num_up_bars__body_to_range_ratio` | `product` | a=`num_up_bars`, b=`body_to_range_ratio` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | `ifelse` | a=`first_bar_return`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | `ifelse` | a=`max_up_ret`, b=`bar_ret_0`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | `ifelse` | a=`first_bar_return`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_rank_max__max_down_ret__bar_body_rng_0` | `rank_max` | a=`max_down_ret`, b=`bar_body_rng_0` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_vwap_dev_2` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`bar_vwap_dev_2`, cond=`gap_pct` |
| `combo_rank_min__max_down_ret__first_30min_return` | `rank_min` | a=`max_down_ret`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0` | `ifelse` | a=`max_up_ret`, b=`bar_body_rng_0`, cond=`gap_pct` |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | `diff` | a=`max_down_ret`, b=`yesterday_day_vwap_dev` |
| `combo_ifelse__gap_pct__first_bar_return__bar_body_rng_0` | `ifelse` | a=`first_bar_return`, b=`bar_body_rng_0`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__first_30min_return` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`first_30min_return`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_30min_return__num_up_bars` | `ifelse` | a=`first_30min_return`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | `diff` | a=`yesterday_early_momentum`, b=`yesterday_day_skew` |
| `combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud` | `ifelse` | a=`yesterday_early_momentum`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_body_rng_0` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`bar_body_rng_0`, cond=`gap_pct` |
| `combo_rank_max__max_up_ret__vol5` | `rank_max` | a=`max_up_ret`, b=`vol5` |
| `combo_abs_diff__max_up_ret__vol_gk10` | `abs_diff` | a=`max_up_ret`, b=`vol_gk10` |
| `combo_ifelse__vix__vix_skew_proxy__bar_ret_0` | `ifelse` | a=`vix_skew_proxy`, b=`bar_ret_0`, cond=`vix` |
| `combo_min__vix_skew_proxy__vix` | `min` | a=`vix_skew_proxy`, b=`vix` |
| `combo_rank_max__max_up_ret__vol_gk10` | `rank_max` | a=`max_up_ret`, b=`vol_gk10` |
| `combo_max__max_up_ret__yesterday_day_realized_vol` | `max` | a=`max_up_ret`, b=`yesterday_day_realized_vol` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_ifelse__vix__max_up_ret__first_bar_return` | `ifelse` | a=`max_up_ret`, b=`first_bar_return`, cond=`vix` |
| `combo_rank_min__vix_rolling_percentile_60d__vix` | `rank_min` | a=`vix_rolling_percentile_60d`, b=`vix` |
| `combo_rank_max__vix_rolling_percentile_60d__vol5` | `rank_max` | a=`vix_rolling_percentile_60d`, b=`vol5` |
| `combo_ifelse__vix__vix_rolling_percentile_60d__bar_body_rng_1` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_body_rng_1`, cond=`vix` |
| `combo_max__max_up_ret__vix` | `max` | a=`max_up_ret`, b=`vix` |
| `combo_rank_min__vix_diff_1d__max_up_ret` | `rank_min` | a=`vix_diff_1d`, b=`max_up_ret` |
| `combo_ifelse__vix__vol5__bar_ret_0` | `ifelse` | a=`vol5`, b=`bar_ret_0`, cond=`vix` |
| `combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0` | `ifelse` | a=`yesterday_early_momentum`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_ifelse__bb_width__max_up_ret__bar_body_rng_0` | `ifelse` | a=`max_up_ret`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_rank_max__max_up_ret__first_30min_return` | `rank_max` | a=`max_up_ret`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_first_30min_return` | `ifelse` | a=`bar_body_rng_0`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_diff__max_up_ret__keltner_squeeze_width` | `diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_ifelse__gap_pct__max_up_ret__early_range` | `ifelse` | a=`max_up_ret`, b=`early_range`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__bar_vol_5` | `ifelse` | a=`max_up_ret`, b=`bar_vol_5`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__bar_body_rng_0__bar_vol_5` | `ifelse` | a=`bar_body_rng_0`, b=`bar_vol_5`, cond=`gap_pct` |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | `clamp_diff` | a=`early_range`, b=`yesterday_day_vwap_dev` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_trend` | `ifelse` | a=`first_bar_return`, b=`yesterday_early_trend`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_bar_return__early_range` | `ifelse` | a=`first_bar_return`, b=`early_range`, cond=`gap_pct` |
