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
| 300ETF | single | 344 | 122 | 31 | 29 | 3 |
| 300ETF | long | 626 | 113 | 4 | 0 | 0 |
| 300ETF | short | 320 | 92 | 3 | 0 | 0 |
| 50ETF | single | 523 | 106 | 6 | 0 | 0 |
| 50ETF | long | 491 | 111 | 3 | 0 | 0 |
| 50ETF | short | 582 | 108 | 8 | 0 | 0 |
| 500ETF | single | 825 | 410 | 308 | 283 | 67 |
| 500ETF | long | 395 | 110 | 13 | 0 | 0 |
| 500ETF | short | 273 | 102 | 1 | 0 | 0 |
| 588000ETF | single | 743 | 366 | 237 | 157 | 33 |
| 588000ETF | long | 334 | 129 | 26 | 3 | 0 |
| 588000ETF | short | 253 | 86 | 6 | 0 | 0 |
| 159915ETF | single | 850 | 278 | 105 | 82 | 20 |
| 159915ETF | long | 454 | 101 | 6 | 0 | 0 |
| 159915ETF | short | 222 | 93 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | +0.1186 | [+0.0728, +0.1624] | +0.1594 | [+0.0619, +0.2626] | +0.8788 | 4.52% | 0.9556 | 1.78% | 0.3779 | 0.6404 | 5.09% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 4 | +0.1736 | [+0.1292, +0.2237] | +0.3012 | [+0.2005, +0.3970] | +0.9636 | 9.59% | 1.5114 | 6.58% | 1.0435 | 1.7550 | 6.86% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 2 | +0.1313 | [+0.0662, +0.1903] | +0.2665 | [+0.1335, +0.3973] | +0.7697 | 11.30% | 1.7788 | 8.54% | 1.3508 | 4.1811 | 3.27% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 4 | +0.1830 | [+0.1292, +0.2266] | +0.2907 | [+0.2050, +0.3747] | +0.9273 | 11.35% | 1.9473 | 8.65% | 1.4951 | 2.7444 | 4.45% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | +0.0594* | [-0.0082, +0.1277] | +0.1154* | [-0.0450, +0.2745] | +0.7818 | 3.47% | 0.9179 | 0.65% | 0.1746 | 0.3522 | 9.64% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 4 | +0.1035 | [+0.0392, +0.1604] | +0.1605 | [+0.0060, +0.3117] | +0.8061 | 5.32% | 0.9963 | 2.11% | 0.3969 | 0.6949 | 8.94% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 2 | +0.0077* | [-0.0886, +0.1087] | -0.1385* | [-0.3632, +0.1485] | -0.2121 | -0.63% | -0.3252 | -1.96% | -1.0130 | -1.2231 | 4.98% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 4 | +0.1343 | [+0.0636, +0.1914] | +0.2759 | [+0.1257, +0.3954] | +0.6606 | 10.40% | 1.5456 | 7.77% | 1.1589 | 2.6819 | 5.48% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | +0.0067* | [-0.0844, +0.0885] | -0.0428* | [-0.2593, +0.1698] | +0.3576 | 1.08% | 0.4366 | -0.18% | -0.0749 | -0.1556 | 5.33% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 4 | +0.1279 | [+0.0441, +0.2080] | +0.2245* | [-0.0068, +0.4233] | +0.6970 | 7.97% | 1.3025 | 4.60% | 0.7570 | 1.5554 | 8.45% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 2 | -0.0023* | [-0.0983, +0.1296] | -0.1213* | [-0.4073, +0.1962] | -0.3091 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 4 | +0.1485 | [+0.0524, +0.2306] | +0.2804 | [+0.0505, +0.4588] | +0.8303 | 11.75% | 1.4638 | 9.05% | 1.1302 | 2.8999 | 5.55% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__max_up_ret__bar_body_rng_0` | +1 | +0.0976 | +0.2285 | +0.2280 | 0.0000 | +0.5377 | +0.6516 | 0.000 |
| `combo_max__first_bar_return__bar_body_rng_0` | +1 | +0.1002 | +0.1830 | +0.1824 | 0.0006 | +0.5123 | +0.7050 | 0.843 |
| `combo_diff__short_sell_quantity__roc60` | +1 | +0.0323 | +0.1514 | +0.1507 | 0.0032 | +0.7141 | +0.7848 | 0.057 |

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
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1875 | +0.2997 | +0.2999 | 0.0000 | +0.7675 | +0.7419 | 0.000 |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | +1 | +0.1477 | +0.2898 | +0.2901 | 0.0000 | +0.6922 | +0.7320 | 0.492 |
| `combo_rank_min__max_up_ret__gap_pct` | +1 | +0.1196 | +0.2816 | +0.2810 | 0.0000 | +0.4766 | +0.6463 | 0.675 |
| `combo_ifelse__gap_pct__max_up_ret__bar_vwap_dev_2` | +1 | +0.1425 | +0.2786 | +0.2781 | 0.0000 | +0.5209 | +0.6962 | 0.641 |
| `combo_min__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.1247 | +0.2645 | +0.2637 | 0.0000 | +0.6687 | +0.7695 | 0.434 |
| `combo_min__max_up_ret__bar_body_rng_0` | +1 | +0.1787 | +0.2617 | +0.2613 | 0.0000 | +0.9237 | +0.8223 | 0.525 |
| `combo_ifelse__gap_pct__bar_ret_0__max_down_ret` | +1 | +0.1509 | +0.2581 | +0.2577 | 0.0000 | +0.4885 | +0.6158 | 0.852 |
| `combo_tri_max__max_up_ret__bar_ret_0__max_down_ret` | +1 | +0.1858 | +0.2528 | +0.2526 | 0.0000 | +0.8277 | +0.7736 | 0.697 |
| `combo_rank_min__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.1191 | +0.2527 | +0.2520 | 0.0000 | +0.6522 | +0.7367 | 0.875 |
| `combo_rank_min__max_up_ret__bar_vwap_dev_2` | +1 | +0.1308 | +0.2519 | +0.2525 | 0.0000 | +0.5124 | +0.6616 | 0.642 |
| `combo_max__max_up_ret__bar_body_rng_1` | +1 | +0.1318 | +0.2482 | +0.2482 | 0.0000 | +0.6333 | +0.7296 | 0.746 |
| `combo_max__max_up_ret__num_up_bars` | +1 | +0.1516 | +0.2480 | +0.2469 | 0.0000 | +0.7467 | +0.7736 | 0.829 |
| `combo_ifelse__gap_pct__max_up_ret__num_up_bars` | +1 | +0.1319 | +0.2459 | +0.2446 | 0.0000 | +0.5192 | +0.6933 | 0.769 |
| `combo_mean__max_up_ret__body_to_range_ratio` | +1 | +0.1504 | +0.2447 | +0.2443 | 0.0000 | +0.9315 | +0.8164 | 0.694 |
| `combo_ifelse__gap_pct__first_bar_return__bar_vwap_dev_2` | +1 | +0.1458 | +0.2428 | +0.2414 | 0.0000 | +0.4668 | +0.6147 | 0.859 |
| `combo_rank_min__max_up_ret__body_to_range_ratio` | +1 | +0.1333 | +0.2415 | +0.2419 | 0.0000 | +0.7845 | +0.7836 | 0.808 |
| `combo_min__max_up_ret__gap_pct` | +1 | +0.1457 | +0.2396 | +0.2390 | 0.0000 | +0.4746 | +0.6411 | 0.704 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.0893 | +0.2390 | +0.2377 | 0.0000 | +0.7971 | +0.7636 | 0.706 |
| `combo_rank_min__max_up_ret__num_up_bars` | +1 | +0.1176 | +0.2380 | +0.2374 | 0.0000 | +0.5666 | +0.7331 | 0.792 |
| `combo_min__bar_ret_0__bar_body_rng_0` | +1 | +0.1588 | +0.2365 | +0.2357 | 0.0000 | +0.6569 | +0.7079 | 0.860 |
| `combo_mean__max_up_ret__bar_vwap_dev_2` | +1 | +0.1589 | +0.2364 | +0.2361 | 0.0000 | +0.6560 | +0.7466 | 0.808 |
| `combo_rank_max__max_up_ret__first_30min_return` | +1 | +0.1650 | +0.2356 | +0.2351 | 0.0000 | +0.8259 | +0.7789 | 0.846 |
| `combo_max__max_up_ret__gap_pct` | +1 | +0.1624 | +0.2314 | +0.2315 | 0.0000 | +0.7603 | +0.8065 | 0.750 |
| `combo_tri_median__max_up_ret__first_bar_return__max_down_ret` | +1 | +0.1677 | +0.2314 | +0.2301 | 0.0000 | +0.4853 | +0.6370 | 0.826 |
| `combo_tri_min__max_up_ret__max_down_ret__num_up_bars` | +1 | +0.1367 | +0.2310 | +0.2298 | 0.0000 | +0.5596 | +0.7185 | 0.761 |
| `combo_rank_max__bar_ret_0__first_30min_return` | +1 | +0.1655 | +0.2297 | +0.2288 | 0.0000 | +0.7898 | +0.8065 | 0.882 |
| `combo_min__max_down_ret__bar_body_rng_1` | +1 | +0.1096 | +0.2287 | +0.2285 | 0.0000 | +0.6228 | +0.7267 | 0.757 |
| `combo_max__bar_ret_0__first_30min_return` | +1 | +0.1651 | +0.2283 | +0.2274 | 0.0000 | +0.7701 | +0.7965 | 0.892 |
| `combo_ifelse__gap_pct__bar_ret_0__num_up_bars` | +1 | +0.1316 | +0.2278 | +0.2260 | 0.0000 | +0.4595 | +0.6809 | 0.840 |
| `combo_mean__bar_ret_0__max_down_ret` | +1 | +0.1535 | +0.2271 | +0.2263 | 0.0000 | +0.5667 | +0.6481 | 0.865 |
| `combo_mean__max_down_ret__bar_vwap_dev_2` | +1 | +0.1270 | +0.2260 | +0.2257 | 0.0000 | +0.5402 | +0.7630 | 0.778 |
| `combo_tri_max__max_up_ret__max_down_ret__bar_vwap_dev_2` | +1 | +0.1674 | +0.2247 | +0.2236 | 0.0000 | +0.7836 | +0.7718 | 0.864 |
| `combo_ifelse__gap_pct__max_up_ret__first_30min_return` | +1 | +0.1432 | +0.2241 | +0.2238 | 0.0000 | +0.7080 | +0.7701 | 0.788 |
| `combo_max__first_30min_return__bar_body_rng_0` | +1 | +0.1530 | +0.2230 | +0.2219 | 0.0000 | +0.6842 | +0.7296 | 0.899 |
| `combo_product__num_up_bars__body_to_range_ratio` | +1 | +0.1004 | +0.2225 | +0.2243 | 0.0000 | +0.4594 | +0.6856 | 0.555 |
| `combo_rank_max__bar_ret_0__max_down_ret` | +1 | +0.1697 | +0.2215 | +0.2208 | 0.0000 | +0.6003 | +0.7109 | 0.832 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | +1 | +0.0928 | +0.2200 | +0.2180 | 0.0000 | +0.5425 | +0.6903 | 0.824 |
| `combo_rank_min__bar_ret_0__max_down_ret` | +1 | +0.1422 | +0.2192 | +0.2184 | 0.0000 | +0.5356 | +0.6663 | 0.820 |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | +1 | +0.1544 | +0.2191 | +0.2192 | 0.0000 | +0.8249 | +0.7736 | 0.854 |
| `combo_max__bar_vwap_dev_2__bar_body_rng_1` | +1 | +0.0985 | +0.2155 | +0.2152 | 0.0000 | +0.5725 | +0.6657 | 0.702 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | +1 | +0.1122 | +0.2154 | +0.2144 | 0.0000 | +0.4769 | +0.6762 | 0.446 |
| `combo_tri_median__max_up_ret__bar_ret_0__num_up_bars` | +1 | +0.1631 | +0.2149 | +0.2143 | 0.0000 | +0.6016 | +0.7073 | 0.898 |
| `combo_min__max_up_ret__bar_vwap_dev_2` | +1 | +0.1349 | +0.2105 | +0.2108 | 0.0000 | +0.5031 | +0.7085 | 0.869 |
| `combo_mean__first_30min_return__gap_pct` | +1 | +0.1338 | +0.2072 | +0.2069 | 0.0000 | +0.6276 | +0.6909 | 0.816 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_vwap_dev_2` | +1 | +0.1067 | +0.2066 | +0.2078 | 0.0000 | +0.4080 | +0.6012 | 0.634 |
| `combo_rank_max__max_down_ret__bar_vwap_dev_2` | +1 | +0.1541 | +0.2035 | +0.2017 | 0.0000 | +0.7611 | +0.7818 | 0.712 |
| `combo_ifelse__gap_pct__first_bar_return__first_30min_return` | +1 | +0.1497 | +0.2024 | +0.2016 | 0.0000 | +0.5935 | +0.6915 | 0.859 |
| `combo_mean__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.1325 | +0.2022 | +0.2024 | 0.0000 | +0.7858 | +0.7801 | 0.843 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | +1 | +0.0972 | +0.2014 | +0.2019 | 0.0000 | +0.4144 | +0.6393 | 0.641 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +1 | +0.1670 | +0.1999 | +0.1988 | 0.0000 | +0.5598 | +0.6962 | 0.892 |
| `combo_rank_min__max_down_ret__first_30min_return` | +1 | +0.1435 | +0.1984 | +0.1976 | 0.0000 | +0.5673 | +0.7132 | 0.873 |
| `combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0` | +1 | +0.1535 | +0.1983 | +0.1980 | 0.0000 | +0.6183 | +0.6985 | 0.836 |
| `combo_rank_min__max_down_ret__bar_vwap_dev_2` | +1 | +0.1074 | +0.1980 | +0.1987 | 0.0000 | +0.3757 | +0.6551 | 0.729 |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | +1 | +0.1151 | +0.1972 | +0.1973 | 0.0000 | +0.4947 | +0.6686 | 0.591 |
| `combo_rank_min__num_up_bars__body_to_range_ratio` | +1 | +0.1178 | +0.1936 | +0.1930 | 0.0000 | +0.6879 | +0.7331 | 0.860 |
| `combo_mean__num_up_bars__bar_vwap_dev_2` | +1 | +0.1062 | +0.1930 | +0.1919 | 0.0000 | +0.4601 | +0.6762 | 0.813 |
| `combo_mean__max_down_ret__first_30min_return` | +1 | +0.1394 | +0.1893 | +0.1888 | 0.0000 | +0.5429 | +0.7032 | 0.896 |
| `combo_ifelse__gap_pct__first_30min_return__bar_vwap_dev_2` | +1 | +0.1126 | +0.1851 | +0.1838 | 0.0004 | +0.3048 | +0.6575 | 0.893 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__first_30min_return` | +1 | +0.1127 | +0.1778 | +0.1795 | 0.0006 | +0.3964 | +0.6962 | 0.823 |
| `combo_rank_max__max_up_ret__bar_vwap_dev_2` | +1 | +0.1641 | +0.1746 | +0.1735 | 0.0008 | +0.6182 | +0.7519 | 0.790 |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | +1 | +0.1531 | +0.1687 | +0.1680 | 0.0016 | +0.6136 | +0.7413 | 0.900 |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | +1 | +0.0782 | +0.1640 | +0.1654 | 0.0030 | +0.5690 | +0.6839 | 0.368 |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | +1 | +0.0689 | +0.1637 | +0.1655 | 0.0032 | +0.5923 | +0.7038 | 0.898 |
| `combo_max__max_down_ret__yesterday_illiquidity_amihud` | +1 | +0.1240 | +0.1594 | +0.1585 | 0.0034 | +0.4836 | +0.7367 | 0.788 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud` | +1 | +0.0642 | +0.1569 | +0.1570 | 0.0042 | +0.4607 | +0.6358 | 0.566 |
| `combo_ifelse__gap_pct__first_30min_return__yesterday_illiquidity_amihud` | +1 | +0.0595 | +0.1565 | +0.1545 | 0.0042 | +0.5874 | +0.7120 | 0.867 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_body_rng_0` | +1 | +0.1191 | +0.1549 | +0.1564 | 0.0046 | +0.3391 | +0.6070 | 0.739 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rank_max__max_up_ret__vol5` | +1 | +0.1215 | +0.3060 | +0.3059 | 0.0000 | +0.8956 | +0.8144 | 0.000 |
| `combo_max__max_up_ret__vol5` | +1 | +0.1224 | +0.2926 | +0.2926 | 0.0000 | +0.8472 | +0.8026 | 0.743 |
| `combo_abs_diff__max_up_ret__vol_gk10` | +1 | +0.1074 | +0.2902 | +0.2924 | 0.0000 | +0.9459 | +0.8322 | 0.674 |
| `combo_mean__vix_diff_1d__max_up_ret` | +1 | +0.1398 | +0.2875 | +0.2873 | 0.0000 | +0.6737 | +0.7641 | 0.472 |
| `combo_ifelse__vix__vix_skew_proxy__bar_ret_0` | +1 | +0.1277 | +0.2846 | +0.2823 | 0.0000 | +0.8798 | +0.7670 | 0.756 |
| `combo_min__vix_skew_proxy__vix` | +1 | +0.0933 | +0.2766 | +0.2766 | 0.0000 | +0.3610 | +0.6229 | 0.621 |
| `combo_rank_max__first_30min_return__max_up_ret` | +1 | +0.1169 | +0.2710 | +0.2708 | 0.0000 | +0.7124 | +0.7868 | 0.546 |
| `combo_max__first_30min_return__max_up_ret` | +1 | +0.1224 | +0.2625 | +0.2623 | 0.0000 | +0.7543 | +0.7690 | 0.870 |
| `combo_mean__vix_skew_proxy__vix` | +1 | +0.0932 | +0.2587 | +0.2590 | 0.0002 | +0.3147 | +0.6120 | 0.711 |
| `combo_rank_max__max_up_ret__num_up_bars` | +1 | +0.1122 | +0.2579 | +0.2566 | 0.0002 | +0.7640 | +0.7552 | 0.882 |
| `combo_rank_max__max_up_ret__vol_gk10` | +1 | +0.1122 | +0.2575 | +0.2596 | 0.0002 | +0.8299 | +0.8026 | 0.737 |
| `combo_max__max_up_ret__yesterday_day_realized_vol` | +1 | +0.0943 | +0.2535 | +0.2543 | 0.0002 | +0.8430 | +0.7739 | 0.842 |
| `combo_ifelse__vix__vix_skew_proxy__max_up_ret` | +1 | +0.1384 | +0.2511 | +0.2503 | 0.0002 | +0.6869 | +0.7463 | 0.900 |
| `combo_max__max_up_ret__vol_gk10` | +1 | +0.1151 | +0.2477 | +0.2498 | 0.0002 | +0.9245 | +0.8174 | 0.858 |
| `combo_rank_max__max_up_ret__yesterday_day_realized_vol` | +1 | +0.0904 | +0.2476 | +0.2484 | 0.0002 | +0.8489 | +0.7660 | 0.848 |
| `combo_mean__max_up_ret__bar_body_rng_1` | +1 | +0.1307 | +0.2472 | +0.2465 | 0.0002 | +0.7543 | +0.7759 | 0.796 |
| `combo_ifelse__vix__vix_rolling_percentile_60d__first_bar_return` | +1 | +0.1168 | +0.2377 | +0.2362 | 0.0008 | +0.8603 | +0.7670 | 0.698 |
| `combo_rank_max__max_up_ret__first_bar_return` | +1 | +0.1056 | +0.2351 | +0.2347 | 0.0010 | +0.8085 | +0.7976 | 0.890 |
| `combo_rank_max__max_up_ret__vix` | +1 | +0.1132 | +0.2338 | +0.2345 | 0.0010 | +0.7849 | +0.7710 | 0.773 |
| `combo_ifelse__vix__max_up_ret__first_bar_return` | +1 | +0.0963 | +0.2307 | +0.2291 | 0.0014 | +0.8377 | +0.7660 | 0.792 |
| `combo_max__first_30min_return__bar_ret_0` | +1 | +0.1187 | +0.2286 | +0.2278 | 0.0014 | +0.6654 | +0.6950 | 0.865 |
| `combo_rank_max__vix_rolling_percentile_60d__vol5` | +1 | +0.0505 | +0.2280 | +0.2282 | 0.0016 | +0.4547 | +0.6950 | 0.535 |
| `combo_ifelse__vix__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.1113 | +0.2267 | +0.2247 | 0.0016 | +0.7270 | +0.7384 | 0.721 |
| `combo_max__first_30min_return__bar_ret_1` | +1 | +0.1211 | +0.2262 | +0.2251 | 0.0016 | +0.9899 | +0.8213 | 0.852 |
| `combo_max__max_up_ret__vix` | +1 | +0.1087 | +0.2185 | +0.2193 | 0.0018 | +0.7481 | +0.7838 | 0.869 |
| `combo_rank_max__vix_skew_proxy__vix` | +1 | +0.0729 | +0.2121 | +0.2144 | 0.0026 | +0.3144 | +0.6239 | 0.565 |
| `combo_ratio__max_up_ret__vol_gk10` | +1 | +0.1070 | +0.2089 | +0.2085 | 0.0028 | +0.6954 | +0.7739 | 0.875 |
| `combo_rank_min__vix_diff_1d__max_up_ret` | +1 | +0.1247 | +0.2037 | +0.2041 | 0.0036 | +0.4140 | +0.6486 | 0.645 |
| `combo_rank_min__vix_rolling_percentile_60d__vix` | +1 | +0.0693 | +0.1969 | +0.1973 | 0.0050 | +0.3003 | +0.6091 | 0.557 |
| `combo_mean__vol5__yesterday_day_realized_vol` | +1 | +0.0431 | +0.1940 | +0.1944 | 0.0062 | +0.4486 | +0.7177 | 0.780 |
| `combo_max__vix_rolling_percentile_60d__vol5` | +1 | +0.0542 | +0.1934 | +0.1937 | 0.0062 | +0.4484 | +0.7048 | 0.783 |
| `combo_mean__vix_rolling_percentile_60d__yesterday_day_realized_vol` | +1 | +0.0469 | +0.1892 | +0.1903 | 0.0070 | +0.3821 | +0.6051 | 0.805 |
| `combo_ifelse__vix__vol5__bar_ret_0` | +1 | +0.1075 | +0.1869 | +0.1857 | 0.0082 | +0.7347 | +0.7394 | 0.838 |

### 588000ETF / long
No features admitted.

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0` | +1 | +0.1388 | +0.2699 | +0.2682 | 0.0000 | +0.4522 | +0.6704 | 0.000 |
| `combo_rank_min__max_up_ret__gap_pct` | +1 | +0.1316 | +0.2542 | +0.2525 | 0.0000 | +0.4470 | +0.6393 | 0.263 |
| `combo_ifelse__bb_width__max_up_ret__bar_body_rng_0` | +1 | +0.1510 | +0.2402 | +0.2379 | 0.0000 | +0.4801 | +0.6604 | 0.698 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +1 | +0.1507 | +0.2332 | +0.2310 | 0.0000 | +0.4553 | +0.6815 | 0.843 |
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1519 | +0.2287 | +0.2278 | 0.0000 | +0.6019 | +0.7185 | 0.707 |
| `combo_rank_max__max_up_ret__first_30min_return` | +1 | +0.1225 | +0.2205 | +0.2189 | 0.0000 | +0.5743 | +0.7419 | 0.837 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | +1 | +0.1390 | +0.2190 | +0.2182 | 0.0000 | +0.4880 | +0.6991 | 0.435 |
| `combo_max__max_up_ret__first_30min_return` | +1 | +0.1136 | +0.2095 | +0.2080 | 0.0000 | +0.5486 | +0.7191 | 0.866 |
| `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_first_30min_return` | +1 | +0.1302 | +0.2077 | +0.2062 | 0.0000 | +0.5842 | +0.7097 | 0.721 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | +1 | +0.1185 | +0.2030 | +0.2005 | 0.0002 | +0.3393 | +0.6434 | 0.741 |
| `combo_min__bar_body_rng_0__bar_ret_0` | +1 | +0.1460 | +0.1947 | +0.1921 | 0.0002 | +0.3374 | +0.6147 | 0.824 |
| `combo_ifelse__gap_pct__max_up_ret__early_range` | +1 | +0.1319 | +0.1928 | +0.1916 | 0.0004 | +0.9726 | +0.8111 | 0.721 |
| `combo_ifelse__gap_pct__max_up_ret__bar_vol_5` | +1 | +0.1339 | +0.1885 | +0.1886 | 0.0004 | +0.5958 | +0.6956 | 0.610 |
| `combo_ifelse__gap_pct__bar_body_rng_0__bar_vol_5` | +1 | +0.1255 | +0.1842 | +0.1837 | 0.0006 | +0.3525 | +0.6317 | 0.801 |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | +1 | +0.1122 | +0.1825 | +0.1826 | 0.0006 | +0.6162 | +0.7120 | 0.516 |
| `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_early_vwap_dev` | +1 | +0.1304 | +0.1810 | +0.1797 | 0.0006 | +0.3949 | +0.6117 | 0.896 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_trend` | +1 | +0.1410 | +0.1790 | +0.1770 | 0.0010 | +0.4642 | +0.6622 | 0.869 |
| `combo_ifelse__gap_pct__first_bar_return__early_range` | +1 | +0.1267 | +0.1728 | +0.1708 | 0.0014 | +0.5853 | +0.7167 | 0.849 |
| `combo_diff__early_range__yesterday_day_vwap_dev` | +1 | +0.1118 | +0.1696 | +0.1697 | 0.0014 | +0.6322 | +0.7279 | 0.884 |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | +1 | +0.1054 | +0.1520 | +0.1510 | 0.0038 | +0.4390 | +0.6874 | 0.842 |

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
| `combo_max__first_bar_return__bar_body_rng_0` | `max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_diff__short_sell_quantity__roc60` | `diff` | a=`short_sell_quantity`, b=`roc60` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_rank_min__max_up_ret__gap_pct` | `rank_min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__bar_vwap_dev_2` | `ifelse` | a=`max_up_ret`, b=`bar_vwap_dev_2`, cond=`gap_pct` |
| `combo_min__max_up_ret__yesterday_illiquidity_amihud` | `min` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_ifelse__gap_pct__bar_ret_0__max_down_ret` | `ifelse` | a=`bar_ret_0`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_tri_max__max_up_ret__bar_ret_0__max_down_ret` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`max_down_ret` |
| `combo_rank_min__max_up_ret__yesterday_illiquidity_amihud` | `rank_min` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_rank_min__max_up_ret__bar_vwap_dev_2` | `rank_min` | a=`max_up_ret`, b=`bar_vwap_dev_2` |
| `combo_max__max_up_ret__bar_body_rng_1` | `max` | a=`max_up_ret`, b=`bar_body_rng_1` |
| `combo_max__max_up_ret__num_up_bars` | `max` | a=`max_up_ret`, b=`num_up_bars` |
| `combo_ifelse__gap_pct__max_up_ret__num_up_bars` | `ifelse` | a=`max_up_ret`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_mean__max_up_ret__body_to_range_ratio` | `mean` | a=`max_up_ret`, b=`body_to_range_ratio` |
| `combo_ifelse__gap_pct__first_bar_return__bar_vwap_dev_2` | `ifelse` | a=`first_bar_return`, b=`bar_vwap_dev_2`, cond=`gap_pct` |
| `combo_rank_min__max_up_ret__body_to_range_ratio` | `rank_min` | a=`max_up_ret`, b=`body_to_range_ratio` |
| `combo_min__max_up_ret__gap_pct` | `min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_illiquidity_amihud` | `ifelse` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_rank_min__max_up_ret__num_up_bars` | `rank_min` | a=`max_up_ret`, b=`num_up_bars` |
| `combo_min__bar_ret_0__bar_body_rng_0` | `min` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__bar_vwap_dev_2` | `mean` | a=`max_up_ret`, b=`bar_vwap_dev_2` |
| `combo_rank_max__max_up_ret__first_30min_return` | `rank_max` | a=`max_up_ret`, b=`first_30min_return` |
| `combo_max__max_up_ret__gap_pct` | `max` | a=`max_up_ret`, b=`gap_pct` |
| `combo_tri_median__max_up_ret__first_bar_return__max_down_ret` | `tri_median` | a=`max_up_ret`, b=`first_bar_return`, c=`max_down_ret` |
| `combo_tri_min__max_up_ret__max_down_ret__num_up_bars` | `tri_min` | a=`max_up_ret`, b=`max_down_ret`, c=`num_up_bars` |
| `combo_rank_max__bar_ret_0__first_30min_return` | `rank_max` | a=`bar_ret_0`, b=`first_30min_return` |
| `combo_min__max_down_ret__bar_body_rng_1` | `min` | a=`max_down_ret`, b=`bar_body_rng_1` |
| `combo_max__bar_ret_0__first_30min_return` | `max` | a=`bar_ret_0`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__bar_ret_0__num_up_bars` | `ifelse` | a=`bar_ret_0`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_mean__bar_ret_0__max_down_ret` | `mean` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_mean__max_down_ret__bar_vwap_dev_2` | `mean` | a=`max_down_ret`, b=`bar_vwap_dev_2` |
| `combo_tri_max__max_up_ret__max_down_ret__bar_vwap_dev_2` | `tri_max` | a=`max_up_ret`, b=`max_down_ret`, c=`bar_vwap_dev_2` |
| `combo_ifelse__gap_pct__max_up_ret__first_30min_return` | `ifelse` | a=`max_up_ret`, b=`first_30min_return`, cond=`gap_pct` |
| `combo_max__first_30min_return__bar_body_rng_0` | `max` | a=`first_30min_return`, b=`bar_body_rng_0` |
| `combo_product__num_up_bars__body_to_range_ratio` | `product` | a=`num_up_bars`, b=`body_to_range_ratio` |
| `combo_rank_max__bar_ret_0__max_down_ret` | `rank_max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | `ifelse` | a=`first_bar_return`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_rank_min__bar_ret_0__max_down_ret` | `rank_min` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | `ifelse` | a=`max_up_ret`, b=`bar_ret_0`, cond=`gap_pct` |
| `combo_max__bar_vwap_dev_2__bar_body_rng_1` | `max` | a=`bar_vwap_dev_2`, b=`bar_body_rng_1` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | `ifelse` | a=`first_bar_return`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_tri_median__max_up_ret__bar_ret_0__num_up_bars` | `tri_median` | a=`max_up_ret`, b=`bar_ret_0`, c=`num_up_bars` |
| `combo_min__max_up_ret__bar_vwap_dev_2` | `min` | a=`max_up_ret`, b=`bar_vwap_dev_2` |
| `combo_mean__first_30min_return__gap_pct` | `mean` | a=`first_30min_return`, b=`gap_pct` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_vwap_dev_2` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`bar_vwap_dev_2`, cond=`gap_pct` |
| `combo_rank_max__max_down_ret__bar_vwap_dev_2` | `rank_max` | a=`max_down_ret`, b=`bar_vwap_dev_2` |
| `combo_ifelse__gap_pct__first_bar_return__first_30min_return` | `ifelse` | a=`first_bar_return`, b=`first_30min_return`, cond=`gap_pct` |
| `combo_mean__max_up_ret__yesterday_illiquidity_amihud` | `mean` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_min__max_down_ret__first_30min_return` | `rank_min` | a=`max_down_ret`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0` | `ifelse` | a=`max_up_ret`, b=`bar_body_rng_0`, cond=`gap_pct` |
| `combo_rank_min__max_down_ret__bar_vwap_dev_2` | `rank_min` | a=`max_down_ret`, b=`bar_vwap_dev_2` |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | `diff` | a=`max_down_ret`, b=`yesterday_day_vwap_dev` |
| `combo_rank_min__num_up_bars__body_to_range_ratio` | `rank_min` | a=`num_up_bars`, b=`body_to_range_ratio` |
| `combo_mean__num_up_bars__bar_vwap_dev_2` | `mean` | a=`num_up_bars`, b=`bar_vwap_dev_2` |
| `combo_mean__max_down_ret__first_30min_return` | `mean` | a=`max_down_ret`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__first_30min_return__bar_vwap_dev_2` | `ifelse` | a=`first_30min_return`, b=`bar_vwap_dev_2`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__first_30min_return` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`first_30min_return`, cond=`gap_pct` |
| `combo_rank_max__max_up_ret__bar_vwap_dev_2` | `rank_max` | a=`max_up_ret`, b=`bar_vwap_dev_2` |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | `rank_max` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | `diff` | a=`yesterday_early_momentum`, b=`yesterday_day_skew` |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | `clamp_diff` | a=`yesterday_early_vwap_dev`, b=`yesterday_day_skew` |
| `combo_max__max_down_ret__yesterday_illiquidity_amihud` | `max` | a=`max_down_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud` | `ifelse` | a=`yesterday_early_momentum`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_30min_return__yesterday_illiquidity_amihud` | `ifelse` | a=`first_30min_return`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__bar_body_rng_0` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`bar_body_rng_0`, cond=`gap_pct` |
| `combo_rank_max__max_up_ret__vol5` | `rank_max` | a=`max_up_ret`, b=`vol5` |
| `combo_max__max_up_ret__vol5` | `max` | a=`max_up_ret`, b=`vol5` |
| `combo_abs_diff__max_up_ret__vol_gk10` | `abs_diff` | a=`max_up_ret`, b=`vol_gk10` |
| `combo_mean__vix_diff_1d__max_up_ret` | `mean` | a=`vix_diff_1d`, b=`max_up_ret` |
| `combo_ifelse__vix__vix_skew_proxy__bar_ret_0` | `ifelse` | a=`vix_skew_proxy`, b=`bar_ret_0`, cond=`vix` |
| `combo_min__vix_skew_proxy__vix` | `min` | a=`vix_skew_proxy`, b=`vix` |
| `combo_rank_max__first_30min_return__max_up_ret` | `rank_max` | a=`first_30min_return`, b=`max_up_ret` |
| `combo_max__first_30min_return__max_up_ret` | `max` | a=`first_30min_return`, b=`max_up_ret` |
| `combo_mean__vix_skew_proxy__vix` | `mean` | a=`vix_skew_proxy`, b=`vix` |
| `combo_rank_max__max_up_ret__num_up_bars` | `rank_max` | a=`max_up_ret`, b=`num_up_bars` |
| `combo_rank_max__max_up_ret__vol_gk10` | `rank_max` | a=`max_up_ret`, b=`vol_gk10` |
| `combo_max__max_up_ret__yesterday_day_realized_vol` | `max` | a=`max_up_ret`, b=`yesterday_day_realized_vol` |
| `combo_ifelse__vix__vix_skew_proxy__max_up_ret` | `ifelse` | a=`vix_skew_proxy`, b=`max_up_ret`, cond=`vix` |
| `combo_max__max_up_ret__vol_gk10` | `max` | a=`max_up_ret`, b=`vol_gk10` |
| `combo_rank_max__max_up_ret__yesterday_day_realized_vol` | `rank_max` | a=`max_up_ret`, b=`yesterday_day_realized_vol` |
| `combo_mean__max_up_ret__bar_body_rng_1` | `mean` | a=`max_up_ret`, b=`bar_body_rng_1` |
| `combo_ifelse__vix__vix_rolling_percentile_60d__first_bar_return` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`first_bar_return`, cond=`vix` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__vix` | `rank_max` | a=`max_up_ret`, b=`vix` |
| `combo_ifelse__vix__max_up_ret__first_bar_return` | `ifelse` | a=`max_up_ret`, b=`first_bar_return`, cond=`vix` |
| `combo_max__first_30min_return__bar_ret_0` | `max` | a=`first_30min_return`, b=`bar_ret_0` |
| `combo_rank_max__vix_rolling_percentile_60d__vol5` | `rank_max` | a=`vix_rolling_percentile_60d`, b=`vol5` |
| `combo_ifelse__vix__vix_rolling_percentile_60d__bar_body_rng_1` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_body_rng_1`, cond=`vix` |
| `combo_max__first_30min_return__bar_ret_1` | `max` | a=`first_30min_return`, b=`bar_ret_1` |
| `combo_max__max_up_ret__vix` | `max` | a=`max_up_ret`, b=`vix` |
| `combo_rank_max__vix_skew_proxy__vix` | `rank_max` | a=`vix_skew_proxy`, b=`vix` |
| `combo_ratio__max_up_ret__vol_gk10` | `ratio` | a=`max_up_ret`, b=`vol_gk10` |
| `combo_rank_min__vix_diff_1d__max_up_ret` | `rank_min` | a=`vix_diff_1d`, b=`max_up_ret` |
| `combo_rank_min__vix_rolling_percentile_60d__vix` | `rank_min` | a=`vix_rolling_percentile_60d`, b=`vix` |
| `combo_mean__vol5__yesterday_day_realized_vol` | `mean` | a=`vol5`, b=`yesterday_day_realized_vol` |
| `combo_max__vix_rolling_percentile_60d__vol5` | `max` | a=`vix_rolling_percentile_60d`, b=`vol5` |
| `combo_mean__vix_rolling_percentile_60d__yesterday_day_realized_vol` | `mean` | a=`vix_rolling_percentile_60d`, b=`yesterday_day_realized_vol` |
| `combo_ifelse__vix__vol5__bar_ret_0` | `ifelse` | a=`vol5`, b=`bar_ret_0`, cond=`vix` |
| `combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0` | `ifelse` | a=`yesterday_early_momentum`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_rank_min__max_up_ret__gap_pct` | `rank_min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__bb_width__max_up_ret__bar_body_rng_0` | `ifelse` | a=`max_up_ret`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_mean__max_up_ret__bar_body_rng_0` | `mean` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_rank_max__max_up_ret__first_30min_return` | `rank_max` | a=`max_up_ret`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_max__max_up_ret__first_30min_return` | `max` | a=`max_up_ret`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_first_30min_return` | `ifelse` | a=`bar_body_rng_0`, b=`yesterday_first_30min_return`, cond=`gap_pct` |
| `combo_diff__max_up_ret__keltner_squeeze_width` | `diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_min__bar_body_rng_0__bar_ret_0` | `min` | a=`bar_body_rng_0`, b=`bar_ret_0` |
| `combo_ifelse__gap_pct__max_up_ret__early_range` | `ifelse` | a=`max_up_ret`, b=`early_range`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__bar_vol_5` | `ifelse` | a=`max_up_ret`, b=`bar_vol_5`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__bar_body_rng_0__bar_vol_5` | `ifelse` | a=`bar_body_rng_0`, b=`bar_vol_5`, cond=`gap_pct` |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | `clamp_diff` | a=`early_range`, b=`yesterday_day_vwap_dev` |
| `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_early_vwap_dev` | `ifelse` | a=`bar_body_rng_0`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_trend` | `ifelse` | a=`first_bar_return`, b=`yesterday_early_trend`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_bar_return__early_range` | `ifelse` | a=`first_bar_return`, b=`early_range`, cond=`gap_pct` |
| `combo_diff__early_range__yesterday_day_vwap_dev` | `diff` | a=`early_range`, b=`yesterday_day_vwap_dev` |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | `ratio` | a=`max_up_ret`, b=`keltner_squeeze_width` |
