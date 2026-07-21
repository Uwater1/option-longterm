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
| 300ETF | single | 2,373 | 404 | 176 | 55 | 7 |
| 300ETF | long | 217 | 89 | 1 | 0 | 0 |
| 300ETF | short | 11,748 | 1,137 | 95 | 0 | 0 |
| 50ETF | single | 2,681 | 304 | 51 | 0 | 0 |
| 50ETF | long | 4,275 | 448 | 18 | 0 | 0 |
| 50ETF | short | 9,210 | 813 | 75 | 0 | 0 |
| 500ETF | single | 3,738 | 1,309 | 941 | 719 | 31 |
| 500ETF | long | 5,145 | 616 | 246 | 6 | 1 |
| 500ETF | short | 12,090 | 1,222 | 133 | 2 | 0 |
| 588000ETF | single | 9,678 | 4,472 | 3,703 | 2,617 | 36 |
| 588000ETF | long | 7,442 | 1,927 | 642 | 6 | 1 |
| 588000ETF | short | 9,882 | 1,152 | 118 | 0 | 0 |
| 159915ETF | single | 5,138 | 1,221 | 503 | 305 | 12 |
| 159915ETF | long | 3,588 | 367 | 72 | 0 | 0 |
| 159915ETF | short | 11,847 | 1,536 | 20 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.1542 | [+0.1036, +0.1993] | +0.2956 | [+0.1835, +0.4019] | +0.9636 | 8.38% | 1.8706 | 5.76% | 1.3069 | 3.4717 | 5.45% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 28 | +0.2116 | [+0.1648, +0.2600] | +0.3517 | [+0.2573, +0.4478] | +0.9758 | 12.64% | 1.8288 | 10.07% | 1.4675 | 2.6145 | 7.39% |
| 500ETF | long | 1 | +0.0353* | [-0.0096, +0.0847] | +0.2319 | [+0.1018, +0.3762] | -0.1273 | 6.41% | 1.2361 | 5.20% | 1.0156 | 2.0377 | 5.21% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 27 | +0.1965 | [+0.1441, +0.2413] | +0.3534 | [+0.2532, +0.4528] | +0.9636 | 15.48% | 1.7864 | 13.30% | 1.5410 | 8.2747 | 2.79% |
| 588000ETF | long | 1 | +0.0668 | [+0.0078, +0.1244] | +0.3153 | [+0.0998, +0.4386] | +0.4061 | 8.50% | 1.2148 | 8.03% | 1.1499 | 4.4886 | 2.62% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 12 | +0.1874 | [+0.1382, +0.2288] | +0.3476 | [+0.2412, +0.4399] | +0.9152 | 11.88% | 2.1364 | 9.23% | 1.6720 | 3.1369 | 4.53% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.0665 | [+0.0021, +0.1295] | +0.0760* | [-0.0841, +0.2196] | +0.7333 | 2.64% | 0.6846 | 0.12% | 0.0308 | 0.0582 | 7.60% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 28 | +0.1154 | [+0.0532, +0.1774] | +0.1267* | [-0.0147, +0.2450] | +0.8545 | 5.13% | 0.9255 | 2.40% | 0.4356 | 0.8485 | 7.27% |
| 500ETF | long | 1 | -0.0263* | [-0.0823, +0.0316] | -0.0632* | [-0.1935, +0.1095] | -0.3697 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 27 | -0.0038* | [-0.0905, +0.0967] | +0.0577* | [-0.1536, +0.2619] | -0.1273 | 1.91% | 1.4236 | 0.96% | 0.7431 | 1.5451 | 1.04% |
| 588000ETF | long | 1 | -0.0219* | [-0.1101, +0.0808] | +0.1035* | [-0.3352, +0.2614] | -0.2242 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 12 | +0.1129 | [+0.0501, +0.1673] | +0.1493 | [+0.0071, +0.2660] | +0.8788 | 6.74% | 1.1090 | 4.03% | 0.6637 | 1.5309 | 6.67% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.0426* | [-0.0477, +0.1194] | +0.0348* | [-0.1894, +0.2313] | +0.6848 | 2.63% | 0.6708 | 1.53% | 0.3905 | 0.9033 | 2.85% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 28 | +0.1135 | [+0.0267, +0.1998] | +0.0975* | [-0.1088, +0.2778] | +0.9273 | 6.28% | 1.0392 | 3.27% | 0.5434 | 1.2317 | 6.54% |
| 500ETF | long | 1 | -0.0481* | [-0.1274, +0.0273] | -0.0789* | [-0.3253, +0.1177] | -0.4303 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 27 | -0.0637* | [-0.1760, +0.0636] | -0.0306* | [-0.2790, +0.2852] | -0.6970 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 1 | -0.0750* | [-0.1781, +0.0527] | -0.1581* | [-0.3505, +0.3213] | -0.2242 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 12 | +0.1267 | [+0.0389, +0.2012] | +0.1185* | [-0.1249, +0.2937] | +0.7818 | 7.95% | 1.0711 | 5.11% | 0.6869 | 1.8003 | 6.27% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1150 | +0.2638 | +0.2640 | 0.0000 | +0.7128 | +0.7091 | 0.000 |
| `combo_ifelse__gap_pct__max_up_ret__option_oi_growth` | +1 | +0.0803 | +0.2474 | +0.2463 | 0.0000 | +0.6845 | +0.7402 | 0.412 |
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | +1 | +0.0848 | +0.2403 | +0.2412 | 0.0000 | +0.5228 | +0.7009 | 0.268 |
| `combo_ifelse__gap_pct__bar_ret_0__bar_body_rng_0` | +1 | +0.1027 | +0.2340 | +0.2338 | 0.0000 | +0.5595 | +0.6880 | 0.436 |
| `combo_ifelse__macd_hist__max_up_ret__option_oi_growth` | +1 | +0.0915 | +0.2144 | +0.2135 | 0.0000 | +0.7339 | +0.7801 | 0.481 |
| `combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio` | +1 | +0.0688 | +0.2104 | +0.2089 | 0.0000 | +0.6433 | +0.7185 | 0.458 |
| `combo_ifelse__macd_hist__max_up_ret__growth_momentum_ratio` | +1 | +0.0750 | +0.1915 | +0.1912 | 0.0004 | +0.5472 | +0.7443 | 0.386 |

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
| `combo_tri_max__max_up_ret__max_down_ret__bar_body_rng_1` | +1 | +0.1312 | +0.2579 | +0.2577 | 0.0000 | +0.6398 | +0.7038 | 0.600 |
| `combo_rank_max__max_down_ret__vix_realized_spread` | +1 | +0.1393 | +0.2532 | +0.2521 | 0.0000 | +0.5912 | +0.7056 | 0.436 |
| `combo_rank_min__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.1191 | +0.2527 | +0.2520 | 0.0000 | +0.6522 | +0.7367 | 0.555 |
| `combo_ifelse__gap_pct__first_bar_return__bar_vwap_dev_2` | +1 | +0.1458 | +0.2428 | +0.2414 | 0.0000 | +0.4668 | +0.6147 | 0.594 |
| `combo_min__bar_ret_0__bar_body_rng_0` | +1 | +0.1588 | +0.2365 | +0.2357 | 0.0000 | +0.6569 | +0.7079 | 0.525 |
| `combo_product__max_down_ret__early_range` | +1 | +0.0708 | +0.2333 | +0.2334 | 0.0000 | +0.3594 | +0.6387 | 0.480 |
| `combo_ifelse__macd_hist__max_up_ret__yesterday_early_momentum` | +1 | +0.1247 | +0.2299 | +0.2319 | 0.0000 | +0.3877 | +0.6604 | 0.361 |
| `combo_diff__max_up_ret__vol20` | +1 | +0.1349 | +0.2294 | +0.2303 | 0.0000 | +0.7270 | +0.7730 | 0.517 |
| `combo_ratio__max_down_ret__bar_vol_5` | +1 | +0.1388 | +0.2276 | +0.2269 | 0.0000 | +0.4691 | +0.6575 | 0.597 |
| `combo_product__num_up_bars__body_to_range_ratio` | +1 | +0.1004 | +0.2225 | +0.2243 | 0.0000 | +0.4594 | +0.6856 | 0.467 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | +1 | +0.0928 | +0.2200 | +0.2180 | 0.0000 | +0.5425 | +0.6903 | 0.525 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | +1 | +0.1122 | +0.2154 | +0.2144 | 0.0000 | +0.4769 | +0.6762 | 0.484 |
| `combo_abs_diff__vol_ratio_10_60__volatility_percentile_20d` | +1 | +0.0926 | +0.2115 | +0.2087 | 0.0000 | +0.4320 | +0.6827 | 0.104 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | +1 | +0.0972 | +0.2067 | +0.2071 | 0.0000 | +0.4144 | +0.6393 | 0.446 |
| `combo_rank_max__max_up_ret__vol_ratio_10_60` | +1 | +0.1467 | +0.2055 | +0.2043 | 0.0000 | +0.7067 | +0.7713 | 0.571 |
| `combo_mean__max_up_ret__macd_hist` | +1 | +0.1520 | +0.2033 | +0.2026 | 0.0000 | +0.5227 | +0.6944 | 0.553 |
| `combo_rank_max__max_up_ret__bar_vwap_dev_3` | +1 | +0.1519 | +0.1975 | +0.1958 | 0.0000 | +0.7676 | +0.7630 | 0.600 |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | +1 | +0.1151 | +0.1972 | +0.1973 | 0.0000 | +0.4947 | +0.6686 | 0.490 |
| `combo_ifelse__macd_hist__bar_ret_0__num_up_bars` | +1 | +0.1226 | +0.1721 | +0.1705 | 0.0010 | +0.4984 | +0.7091 | 0.595 |
| `combo_rank_min__bar_body_rng_0__northbound_volume_share` | +1 | +0.0692 | +0.1642 | +0.1652 | 0.0030 | +0.4372 | +0.6745 | 0.546 |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | +1 | +0.0782 | +0.1640 | +0.1654 | 0.0030 | +0.5690 | +0.6839 | 0.400 |
| `combo_ifelse__vol20__first_30min_return__yesterday_illiquidity_amihud` | +1 | +0.0590 | +0.1616 | +0.1618 | 0.0034 | +0.5196 | +0.6798 | 0.566 |
| `combo_max__max_down_ret__yesterday_illiquidity_amihud` | +1 | +0.1240 | +0.1594 | +0.1585 | 0.0034 | +0.4836 | +0.7367 | 0.484 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud` | +1 | +0.0642 | +0.1569 | +0.1570 | 0.0042 | +0.4607 | +0.6358 | 0.555 |
| `combo_abs_diff__max_up_ret__cci14` | +1 | +0.0353 | +0.1556 | +0.1553 | 0.0042 | +0.3059 | +0.6082 | 0.540 |
| `combo_rank_max__yesterday_illiquidity_amihud__cci14` | +1 | +0.0522 | +0.1490 | +0.1488 | 0.0062 | +0.3985 | +0.6733 | 0.365 |

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
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_body_rng_1` | +1 | +0.1160 | +0.3384 | +0.3359 | 0.0000 | +1.1746 | +0.8480 | 0.268 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__short_sell_cover_spread__max_down_ret` | +1 | +0.1295 | +0.3375 | +0.3356 | 0.0000 | +1.1612 | +0.8717 | 0.540 |
| `combo_tri_mean__vix_diff_1d__max_up_ret__vix` | +1 | +0.1325 | +0.3345 | +0.3345 | 0.0000 | +0.6427 | +0.7493 | 0.568 |
| `combo_tri_ifelse__vix__vol20__first_30min_return__vol_gk10__max_down_ret` | +1 | +0.1376 | +0.3196 | +0.3186 | 0.0000 | +1.0515 | +0.8203 | 0.520 |
| `combo_rank_max__max_up_ret__vol5` | +1 | +0.1215 | +0.3060 | +0.3059 | 0.0000 | +0.8956 | +0.8144 | 0.459 |
| `combo_rank_max__first_bar_return__num_up_bars` | +1 | +0.0947 | +0.3055 | +0.3033 | 0.0000 | +0.9874 | +0.8184 | 0.423 |
| `combo_rank_max__max_down_ret__bar_rng_3` | +1 | +0.1129 | +0.3023 | +0.3013 | 0.0000 | +1.0578 | +0.8322 | 0.460 |
| `combo_ifelse__atr14_norm__vol5__bar_ret_0` | +1 | +0.1234 | +0.2943 | +0.2931 | 0.0000 | +0.6600 | +0.7029 | 0.507 |
| `combo_abs_diff__max_up_ret__vol_gk10` | +1 | +0.1074 | +0.2902 | +0.2924 | 0.0000 | +0.9459 | +0.8322 | 0.556 |
| `combo_diff__vix_skew_proxy__gap_pct` | +1 | +0.0793 | +0.2887 | +0.2905 | 0.0000 | +0.5736 | +0.6989 | 0.412 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol_gk10__num_up_bars` | +1 | +0.1258 | +0.2882 | +0.2893 | 0.0000 | +0.7032 | +0.7384 | 0.565 |
| `combo_min__max_up_ret__early_skew` | +1 | +0.1148 | +0.2878 | +0.2895 | 0.0000 | +0.6133 | +0.7621 | 0.397 |
| `combo_mean__max_down_ret__bar_rng_5` | +1 | +0.1279 | +0.2874 | +0.2856 | 0.0000 | +1.0203 | +0.8085 | 0.560 |
| `combo_ifelse__gap_pct__vix_skew_proxy__bar_ret_1` | +1 | +0.1378 | +0.2801 | +0.2803 | 0.0000 | +0.8544 | +0.7878 | 0.536 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_body_rng_1__early_momentum` | +1 | +0.1253 | +0.2708 | +0.2706 | 0.0000 | +1.0330 | +0.8381 | 0.574 |
| `combo_max__first_30min_return__early_skew` | +1 | +0.0927 | +0.2662 | +0.2687 | 0.0000 | +0.7915 | +0.7759 | 0.599 |
| `combo_ifelse__gap_pct__vol5__bar_body_rng_1` | +1 | +0.1086 | +0.2579 | +0.2566 | 0.0002 | +0.9017 | +0.7769 | 0.532 |
| `combo_ifelse__gap_pct__vix_skew_proxy__first_bar_return` | +1 | +0.0821 | +0.2577 | +0.2573 | 0.0002 | +0.6630 | +0.7384 | 0.599 |
| `combo_rank_max__vix_diff_1d__vix_iv_spread` | +1 | +0.1069 | +0.2475 | +0.2482 | 0.0002 | +0.3034 | +0.6367 | 0.396 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_ret_0__early_momentum` | +1 | +0.1129 | +0.2453 | +0.2454 | 0.0002 | +0.8362 | +0.7838 | 0.571 |
| `combo_ifelse__gap_pct__vol5__bar_ret_0` | +1 | +0.0637 | +0.2383 | +0.2368 | 0.0008 | +0.5101 | +0.6940 | 0.580 |
| `combo_rank_min__vix_diff_1d__bar_rng_5` | +1 | +0.1041 | +0.2367 | +0.2359 | 0.0008 | +0.5318 | +0.6634 | 0.408 |
| `combo_rank_max__vix_rolling_percentile_60d__vol5` | +1 | +0.0505 | +0.2280 | +0.2282 | 0.0016 | +0.4547 | +0.6950 | 0.535 |
| `combo_rank_min__vix_rolling_percentile_60d__vix` | +1 | +0.0693 | +0.2266 | +0.2270 | 0.0016 | +0.3003 | +0.6091 | 0.486 |
| `combo_mean__vol5__max_down_ret` | +1 | +0.1313 | +0.2218 | +0.2200 | 0.0016 | +0.7479 | +0.7542 | 0.593 |
| `combo_rank_max__max_down_ret__vol_pk20` | +1 | +0.1219 | +0.2205 | +0.2218 | 0.0016 | +0.9497 | +0.7957 | 0.578 |
| `combo_mean__yesterday_day_realized_vol__vol_ratio_5_20` | +1 | +0.0454 | +0.2192 | +0.2185 | 0.0018 | +0.6403 | +0.7078 | 0.578 |
| `combo_ifelse__vol10__vix_rolling_percentile_60d__first_bar_return` | +1 | +0.0925 | +0.2147 | +0.2154 | 0.0020 | +0.6718 | +0.7394 | 0.558 |
| `combo_rank_max__yesterday_day_realized_vol__bar_vol_4` | +1 | +0.0644 | +0.2058 | +0.2056 | 0.0034 | +0.6490 | +0.7601 | 0.448 |
| `combo_rank_max__vix_diff_1d__total_path_length` | +1 | +0.0805 | +0.2005 | +0.2025 | 0.0042 | +0.4065 | +0.6259 | 0.555 |
| `combo_min__vol_gk10__bar_rng_5` | +1 | +0.0542 | +0.1964 | +0.1963 | 0.0050 | +0.5167 | +0.6969 | 0.526 |
| `combo_rank_max__yesterday_day_realized_vol__yesterday_day_range` | +1 | +0.0309 | +0.1908 | +0.1910 | 0.0066 | +0.4797 | +0.6851 | 0.581 |
| `combo_ifelse__vol20__max_up_ret__vix_rolling_percentile_60d` | +1 | +0.0363 | +0.1887 | +0.1896 | 0.0074 | +0.3811 | +0.6683 | 0.573 |

### 588000ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_max__bar_vol_4__vol5` | +1 | +0.0668 | +0.3153 | +0.3138 | 0.0000 | +0.2751 | +0.5972 | 0.000 |

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__max_up_ret__bar_ret_0__gap_pct` | +1 | +0.1392 | +0.2714 | +0.2686 | 0.0000 | +0.5300 | +0.6657 | 0.000 |
| `combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0` | +1 | +0.1388 | +0.2699 | +0.2682 | 0.0000 | +0.4522 | +0.6704 | 0.312 |
| `combo_tri_median__max_up_ret__max_down_ret__yearly_high_distance` | +1 | +0.1217 | +0.2463 | +0.2455 | 0.0000 | +0.4118 | +0.6698 | 0.419 |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__capital_sell_volume__margin_buy_repayment_spread` | +1 | +0.1250 | +0.2373 | +0.2351 | 0.0000 | +0.4275 | +0.6416 | 0.353 |
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1519 | +0.2287 | +0.2278 | 0.0000 | +0.6019 | +0.7185 | 0.544 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | +1 | +0.1390 | +0.2190 | +0.2182 | 0.0000 | +0.4880 | +0.6991 | 0.407 |
| `combo_max__max_up_ret__bar_body_rng_1` | +1 | +0.0589 | +0.2186 | +0.2171 | 0.0000 | +0.5173 | +0.6950 | 0.568 |
| `combo_min__max_up_ret__yesterday_illiquidity_amihud` | +1 | +0.0940 | +0.2032 | +0.2020 | 0.0002 | +0.4193 | +0.6780 | 0.559 |
| `combo_rank_max__max_up_ret__vol_ratio_10_60` | +1 | +0.1169 | +0.1951 | +0.1933 | 0.0002 | +0.6481 | +0.7355 | 0.544 |
| `combo_ifelse__gap_pct__max_up_ret__early_range` | +1 | +0.1319 | +0.1928 | +0.1916 | 0.0004 | +0.9726 | +0.8111 | 0.600 |
| `combo_ifelse__gap_pct__bar_body_rng_0__bar_vol_5` | +1 | +0.1255 | +0.1842 | +0.1837 | 0.0006 | +0.3525 | +0.6317 | 0.519 |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | +1 | +0.1122 | +0.1825 | +0.1826 | 0.0006 | +0.6162 | +0.7120 | 0.516 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__option_oi_growth` | `ifelse` | a=`max_up_ret`, b=`option_oi_growth`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | `ifelse` | a=`first_bar_return`, b=`short_sell_cover_spread`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__bar_ret_0__bar_body_rng_0` | `ifelse` | a=`bar_ret_0`, b=`bar_body_rng_0`, cond=`gap_pct` |
| `combo_ifelse__macd_hist__max_up_ret__option_oi_growth` | `ifelse` | a=`max_up_ret`, b=`option_oi_growth`, cond=`macd_hist` |
| `combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio` | `ifelse` | a=`first_bar_return`, b=`growth_momentum_ratio`, cond=`gap_pct` |
| `combo_ifelse__macd_hist__max_up_ret__growth_momentum_ratio` | `ifelse` | a=`max_up_ret`, b=`growth_momentum_ratio`, cond=`macd_hist` |
| `combo_diff__max_up_ret__willr14` | `diff` | a=`max_up_ret`, b=`willr14` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_tri_median__max_up_ret__bar_vwap_dev_2__gap_pct` | `tri_median` | a=`max_up_ret`, b=`bar_vwap_dev_2`, c=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_rank_min__max_down_ret__early_range` | `rank_min` | a=`max_down_ret`, b=`early_range` |
| `combo_tri_max__max_up_ret__max_down_ret__bar_body_rng_1` | `tri_max` | a=`max_up_ret`, b=`max_down_ret`, c=`bar_body_rng_1` |
| `combo_rank_max__max_down_ret__vix_realized_spread` | `rank_max` | a=`max_down_ret`, b=`vix_realized_spread` |
| `combo_rank_min__max_up_ret__yesterday_illiquidity_amihud` | `rank_min` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_ifelse__gap_pct__first_bar_return__bar_vwap_dev_2` | `ifelse` | a=`first_bar_return`, b=`bar_vwap_dev_2`, cond=`gap_pct` |
| `combo_min__bar_ret_0__bar_body_rng_0` | `min` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_product__max_down_ret__early_range` | `product` | a=`max_down_ret`, b=`early_range` |
| `combo_ifelse__macd_hist__max_up_ret__yesterday_early_momentum` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_momentum`, cond=`macd_hist` |
| `combo_diff__max_up_ret__vol20` | `diff` | a=`max_up_ret`, b=`vol20` |
| `combo_ratio__max_down_ret__bar_vol_5` | `ratio` | a=`max_down_ret`, b=`bar_vol_5` |
| `combo_product__num_up_bars__body_to_range_ratio` | `product` | a=`num_up_bars`, b=`body_to_range_ratio` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | `ifelse` | a=`first_bar_return`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | `ifelse` | a=`first_bar_return`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_abs_diff__vol_ratio_10_60__volatility_percentile_20d` | `abs_diff` | a=`vol_ratio_10_60`, b=`volatility_percentile_20d` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_rank_max__max_up_ret__vol_ratio_10_60` | `rank_max` | a=`max_up_ret`, b=`vol_ratio_10_60` |
| `combo_mean__max_up_ret__macd_hist` | `mean` | a=`max_up_ret`, b=`macd_hist` |
| `combo_rank_max__max_up_ret__bar_vwap_dev_3` | `rank_max` | a=`max_up_ret`, b=`bar_vwap_dev_3` |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | `diff` | a=`max_down_ret`, b=`yesterday_day_vwap_dev` |
| `combo_ifelse__macd_hist__bar_ret_0__num_up_bars` | `ifelse` | a=`bar_ret_0`, b=`num_up_bars`, cond=`macd_hist` |
| `combo_rank_min__bar_body_rng_0__northbound_volume_share` | `rank_min` | a=`bar_body_rng_0`, b=`northbound_volume_share` |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | `diff` | a=`yesterday_early_momentum`, b=`yesterday_day_skew` |
| `combo_ifelse__vol20__first_30min_return__yesterday_illiquidity_amihud` | `ifelse` | a=`first_30min_return`, b=`yesterday_illiquidity_amihud`, cond=`vol20` |
| `combo_max__max_down_ret__yesterday_illiquidity_amihud` | `max` | a=`max_down_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_ifelse__gap_pct__yesterday_early_momentum__yesterday_illiquidity_amihud` | `ifelse` | a=`yesterday_early_momentum`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_abs_diff__max_up_ret__cci14` | `abs_diff` | a=`max_up_ret`, b=`cci14` |
| `combo_rank_max__yesterday_illiquidity_amihud__cci14` | `rank_max` | a=`yesterday_illiquidity_amihud`, b=`cci14` |
| `combo_abs_diff__cci14__max_up_ret` | `abs_diff` | a=`cci14`, b=`max_up_ret` |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | `tri_ifelse` | a=`vix_skew_proxy`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_body_rng_1` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol5`, c=`bar_body_rng_1`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__short_sell_cover_spread__max_down_ret` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`short_sell_cover_spread`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_mean__vix_diff_1d__max_up_ret__vix` | `tri_mean` | a=`vix_diff_1d`, b=`max_up_ret`, c=`vix` |
| `combo_tri_ifelse__vix__vol20__first_30min_return__vol_gk10__max_down_ret` | `tri_ifelse` | a=`first_30min_return`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_rank_max__max_up_ret__vol5` | `rank_max` | a=`max_up_ret`, b=`vol5` |
| `combo_rank_max__first_bar_return__num_up_bars` | `rank_max` | a=`first_bar_return`, b=`num_up_bars` |
| `combo_rank_max__max_down_ret__bar_rng_3` | `rank_max` | a=`max_down_ret`, b=`bar_rng_3` |
| `combo_ifelse__atr14_norm__vol5__bar_ret_0` | `ifelse` | a=`vol5`, b=`bar_ret_0`, cond=`atr14_norm` |
| `combo_abs_diff__max_up_ret__vol_gk10` | `abs_diff` | a=`max_up_ret`, b=`vol_gk10` |
| `combo_diff__vix_skew_proxy__gap_pct` | `diff` | a=`vix_skew_proxy`, b=`gap_pct` |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol_gk10__num_up_bars` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol_gk10`, c=`num_up_bars`, cond=`vix`, cond2=`atr14_norm` |
| `combo_min__max_up_ret__early_skew` | `min` | a=`max_up_ret`, b=`early_skew` |
| `combo_mean__max_down_ret__bar_rng_5` | `mean` | a=`max_down_ret`, b=`bar_rng_5` |
| `combo_ifelse__gap_pct__vix_skew_proxy__bar_ret_1` | `ifelse` | a=`vix_skew_proxy`, b=`bar_ret_1`, cond=`gap_pct` |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_body_rng_1__early_momentum` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_body_rng_1`, c=`early_momentum`, cond=`vix`, cond2=`atr14_norm` |
| `combo_max__first_30min_return__early_skew` | `max` | a=`first_30min_return`, b=`early_skew` |
| `combo_ifelse__gap_pct__vol5__bar_body_rng_1` | `ifelse` | a=`vol5`, b=`bar_body_rng_1`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__vix_skew_proxy__first_bar_return` | `ifelse` | a=`vix_skew_proxy`, b=`first_bar_return`, cond=`gap_pct` |
| `combo_rank_max__vix_diff_1d__vix_iv_spread` | `rank_max` | a=`vix_diff_1d`, b=`vix_iv_spread` |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_ret_0__early_momentum` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_ret_0`, c=`early_momentum`, cond=`vix`, cond2=`atr14_norm` |
| `combo_ifelse__gap_pct__vol5__bar_ret_0` | `ifelse` | a=`vol5`, b=`bar_ret_0`, cond=`gap_pct` |
| `combo_rank_min__vix_diff_1d__bar_rng_5` | `rank_min` | a=`vix_diff_1d`, b=`bar_rng_5` |
| `combo_rank_max__vix_rolling_percentile_60d__vol5` | `rank_max` | a=`vix_rolling_percentile_60d`, b=`vol5` |
| `combo_rank_min__vix_rolling_percentile_60d__vix` | `rank_min` | a=`vix_rolling_percentile_60d`, b=`vix` |
| `combo_mean__vol5__max_down_ret` | `mean` | a=`vol5`, b=`max_down_ret` |
| `combo_rank_max__max_down_ret__vol_pk20` | `rank_max` | a=`max_down_ret`, b=`vol_pk20` |
| `combo_mean__yesterday_day_realized_vol__vol_ratio_5_20` | `mean` | a=`yesterday_day_realized_vol`, b=`vol_ratio_5_20` |
| `combo_ifelse__vol10__vix_rolling_percentile_60d__first_bar_return` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`first_bar_return`, cond=`vol10` |
| `combo_rank_max__yesterday_day_realized_vol__bar_vol_4` | `rank_max` | a=`yesterday_day_realized_vol`, b=`bar_vol_4` |
| `combo_rank_max__vix_diff_1d__total_path_length` | `rank_max` | a=`vix_diff_1d`, b=`total_path_length` |
| `combo_min__vol_gk10__bar_rng_5` | `min` | a=`vol_gk10`, b=`bar_rng_5` |
| `combo_rank_max__yesterday_day_realized_vol__yesterday_day_range` | `rank_max` | a=`yesterday_day_realized_vol`, b=`yesterday_day_range` |
| `combo_ifelse__vol20__max_up_ret__vix_rolling_percentile_60d` | `ifelse` | a=`max_up_ret`, b=`vix_rolling_percentile_60d`, cond=`vol20` |
| `combo_max__bar_vol_4__vol5` | `max` | a=`bar_vol_4`, b=`vol5` |
| `combo_tri_min__max_up_ret__bar_ret_0__gap_pct` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`gap_pct` |
| `combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0` | `ifelse` | a=`yesterday_early_momentum`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_tri_median__max_up_ret__max_down_ret__yearly_high_distance` | `tri_median` | a=`max_up_ret`, b=`max_down_ret`, c=`yearly_high_distance` |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__capital_sell_volume__margin_buy_repayment_spread` | `tri_ifelse` | a=`bar_body_rng_0`, b=`capital_sell_volume`, c=`margin_buy_repayment_spread`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_max__max_up_ret__bar_body_rng_1` | `max` | a=`max_up_ret`, b=`bar_body_rng_1` |
| `combo_min__max_up_ret__yesterday_illiquidity_amihud` | `min` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_rank_max__max_up_ret__vol_ratio_10_60` | `rank_max` | a=`max_up_ret`, b=`vol_ratio_10_60` |
| `combo_ifelse__gap_pct__max_up_ret__early_range` | `ifelse` | a=`max_up_ret`, b=`early_range`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__bar_body_rng_0__bar_vol_5` | `ifelse` | a=`bar_body_rng_0`, b=`bar_vol_5`, cond=`gap_pct` |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | `clamp_diff` | a=`early_range`, b=`yesterday_day_vwap_dev` |
