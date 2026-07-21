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

| ETF | Side | Total Candidates | Split-Half Pass | B2 Rolling Guard | BH-FDR Pass | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 2,409 | 438 | 212 | 97 | 7 |
| 300ETF | long | 217 | 89 | 1 | 0 | 0 |
| 300ETF | short | 11,784 | 1,181 | 131 | 74 | 0 |
| 50ETF | single | 2,813 | 436 | 183 | 139 | 0 |
| 50ETF | long | 4,287 | 460 | 30 | 18 | 0 |
| 50ETF | short | 9,259 | 863 | 125 | 86 | 0 |
| 500ETF | single | 3,784 | 1,355 | 987 | 803 | 18 |
| 500ETF | long | 5,148 | 620 | 249 | 22 | 1 |
| 500ETF | short | 12,175 | 1,307 | 218 | 149 | 0 |
| 588000ETF | single | 9,704 | 4,495 | 3,729 | 2,720 | 20 |
| 588000ETF | long | 7,451 | 1,930 | 646 | 81 | 1 |
| 588000ETF | short | 9,981 | 1,261 | 222 | 131 | 0 |
| 159915ETF | single | 5,177 | 1,260 | 542 | 360 | 8 |
| 159915ETF | long | 3,596 | 366 | 77 | 11 | 0 |
| 159915ETF | short | 12,368 | 2,040 | 535 | 524 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.1542 | [+0.1036, +0.1993] | +0.2956 | [+0.1835, +0.4019] | +0.9636 | 10.76% | 1.8925 | 6.63% | 1.1807 | 2.6740 | 9.09% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 18 | +0.2164 | [+0.1708, +0.2642] | +0.3567 | [+0.2556, +0.4562] | +0.9879 | 17.12% | 2.0885 | 13.16% | 1.6201 | 3.0984 | 7.03% |
| 500ETF | long | 1 | +0.0353* | [-0.0096, +0.0847] | +0.2319 | [+0.1018, +0.3762] | -0.1273 | 8.17% | 1.3379 | 6.09% | 1.0081 | 2.0317 | 5.47% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 19 | +0.2066 | [+0.1520, +0.2526] | +0.4054 | [+0.2595, +0.5320] | +0.8909 | 20.21% | 2.0955 | 16.58% | 1.7270 | 7.8536 | 3.51% |
| 588000ETF | long | 1 | +0.0668 | [+0.0078, +0.1244] | +0.3153 | [+0.0998, +0.4386] | +0.4061 | 10.85% | 1.2795 | 9.92% | 1.1718 | 4.4590 | 3.34% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.1988 | [+0.1513, +0.2400] | +0.3867 | [+0.2770, +0.4793] | +0.8182 | 19.28% | 2.5590 | 14.97% | 2.0075 | 4.6595 | 6.48% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.0665 | [+0.0021, +0.1295] | +0.0760* | [-0.0841, +0.2196] | +0.7333 | 3.66% | 0.7405 | -0.39% | -0.0783 | -0.1385 | 11.50% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 18 | +0.1191 | [+0.0583, +0.1815] | +0.1747 | [+0.0442, +0.3001] | +0.7212 | 7.93% | 1.2321 | 3.72% | 0.5820 | 1.1199 | 6.16% |
| 500ETF | long | 1 | -0.0263* | [-0.0823, +0.0316] | -0.0632* | [-0.1935, +0.1095] | -0.3697 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 19 | +0.0012* | [-0.0936, +0.1071] | +0.0999* | [-0.1309, +0.2992] | -0.0667 | 2.44% | 1.0394 | 0.90% | 0.3907 | 0.6080 | 2.95% |
| 588000ETF | long | 1 | -0.0219* | [-0.1101, +0.0808] | +0.1035* | [-0.3352, +0.2614] | -0.2242 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.1075 | [+0.0415, +0.1605] | +0.1302* | [-0.0085, +0.2464] | +0.8909 | 11.02% | 1.2987 | 6.53% | 0.7690 | 1.6308 | 10.25% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 7 | +0.0426* | [-0.0477, +0.1194] | +0.0348* | [-0.1894, +0.2313] | +0.6848 | 3.55% | 0.7303 | 1.71% | 0.3537 | 0.7543 | 4.72% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 18 | +0.1207 | [+0.0366, +0.2085] | +0.1728* | [-0.0392, +0.3706] | +0.8909 | 10.68% | 1.5369 | 6.19% | 0.8950 | 2.0313 | 5.07% |
| 500ETF | long | 1 | -0.0481* | [-0.1274, +0.0273] | -0.0789* | [-0.3253, +0.1177] | -0.4303 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 19 | -0.0390* | [-0.1622, +0.0985] | +0.0968* | [-0.1643, +0.3657] | -0.4545 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 1 | -0.0750* | [-0.1781, +0.0527] | -0.1581* | [-0.3505, +0.3213] | -0.2242 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.1193 | [+0.0305, +0.1915] | +0.0922* | [-0.1488, +0.2784] | +0.8667 | 13.68% | 1.3680 | 9.18% | 0.9163 | 2.1402 | 7.82% |
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
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | +1 | +0.1477 | +0.2898 | +0.2901 | 0.0000 | +0.6922 | +0.7320 | 0.492 |
| `combo_rank_min__max_up_ret__bar_vwap_dev_2` | +1 | +0.1308 | +0.2519 | +0.2525 | 0.0000 | +0.5124 | +0.6616 | 0.457 |
| `combo_rank_min__bar_ret_0__bar_body_rng_0` | +1 | +0.1551 | +0.2349 | +0.2342 | 0.0000 | +0.4919 | +0.6264 | 0.470 |
| `combo_product__max_down_ret__early_range` | +1 | +0.0708 | +0.2333 | +0.2334 | 0.0000 | +0.3594 | +0.6387 | 0.480 |
| `combo_ifelse__macd_hist__max_up_ret__yesterday_early_momentum` | +1 | +0.1247 | +0.2299 | +0.2319 | 0.0000 | +0.3877 | +0.6604 | 0.304 |
| `combo_diff__max_up_ret__vol20` | +1 | +0.1349 | +0.2294 | +0.2303 | 0.0000 | +0.7270 | +0.7730 | 0.428 |
| `combo_product__num_up_bars__body_to_range_ratio` | +1 | +0.1004 | +0.2225 | +0.2243 | 0.0000 | +0.4594 | +0.6856 | 0.458 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | +1 | +0.0928 | +0.2200 | +0.2180 | 0.0000 | +0.5425 | +0.6903 | 0.471 |
| `combo_rank_min__max_down_ret__bar_ret_1` | +1 | +0.1139 | +0.2154 | +0.2150 | 0.0000 | +0.5166 | +0.6938 | 0.477 |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | +1 | +0.1122 | +0.2154 | +0.2144 | 0.0000 | +0.4769 | +0.6762 | 0.484 |
| `combo_abs_diff__vol_ratio_10_60__volatility_percentile_20d` | +1 | +0.0926 | +0.2115 | +0.2087 | 0.0000 | +0.4320 | +0.6827 | 0.087 |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | +1 | +0.0972 | +0.2067 | +0.2071 | 0.0000 | +0.4144 | +0.6393 | 0.446 |
| `combo_max__max_up_ret__cci14` | +1 | +0.1330 | +0.2034 | +0.2034 | 0.0000 | +0.3922 | +0.6557 | 0.431 |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | +1 | +0.1151 | +0.1972 | +0.1973 | 0.0000 | +0.4947 | +0.6686 | 0.464 |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | +1 | +0.0782 | +0.1640 | +0.1654 | 0.0030 | +0.5690 | +0.6839 | 0.400 |
| `combo_max__max_down_ret__yesterday_illiquidity_amihud` | +1 | +0.1240 | +0.1594 | +0.1585 | 0.0034 | +0.4836 | +0.7367 | 0.466 |

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
| `combo_tri_max__max_up_ret__vol5__max_down_ret` | +1 | +0.1505 | +0.3161 | +0.3153 | 0.0000 | +1.2134 | +0.8944 | 0.445 |
| `combo_rank_max__first_bar_return__num_up_bars` | +1 | +0.0947 | +0.3055 | +0.3033 | 0.0000 | +0.9874 | +0.8184 | 0.384 |
| `combo_rank_max__max_down_ret__bar_rng_3` | +1 | +0.1129 | +0.3023 | +0.3013 | 0.0000 | +1.0578 | +0.8322 | 0.460 |
| `combo_diff__vix_skew_proxy__gap_pct` | +1 | +0.0793 | +0.2887 | +0.2905 | 0.0000 | +0.5736 | +0.6989 | 0.383 |
| `combo_min__max_up_ret__early_skew` | +1 | +0.1148 | +0.2878 | +0.2895 | 0.0000 | +0.6133 | +0.7621 | 0.397 |
| `combo_tri_ifelse__atr14_norm__vol20__vix_rolling_percentile_60d__bar_ret_0__max_down_ret` | +1 | +0.1442 | +0.2713 | +0.2687 | 0.0000 | +1.1342 | +0.8657 | 0.492 |
| `combo_tri_mean__vix_diff_1d__vix_rolling_percentile_60d__yesterday_day_realized_vol` | +1 | +0.0651 | +0.2609 | +0.2619 | 0.0002 | +0.5000 | +0.6229 | 0.491 |
| `combo_ifelse__gap_pct__vol5__bar_body_rng_1` | +1 | +0.1086 | +0.2579 | +0.2566 | 0.0002 | +0.9017 | +0.7769 | 0.480 |
| `combo_rank_max__vix_diff_1d__vix_iv_spread` | +1 | +0.1069 | +0.2475 | +0.2482 | 0.0002 | +0.3034 | +0.6367 | 0.396 |
| `combo_rank_min__vix_diff_1d__bar_rng_5` | +1 | +0.1041 | +0.2455 | +0.2447 | 0.0002 | +0.5318 | +0.6634 | 0.435 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_ret_0__early_momentum` | +1 | +0.1129 | +0.2453 | +0.2454 | 0.0002 | +0.8362 | +0.7838 | 0.484 |
| `combo_ifelse__gap_pct__vix_rolling_percentile_60d__first_bar_return` | +1 | +0.0598 | +0.2378 | +0.2369 | 0.0008 | +0.6266 | +0.7423 | 0.445 |
| `combo_max__first_30min_return__bar_ret_1` | +1 | +0.1211 | +0.2262 | +0.2251 | 0.0016 | +0.9899 | +0.8213 | 0.480 |
| `combo_rank_min__vix_diff_1d__max_up_ret` | +1 | +0.1247 | +0.2128 | +0.2133 | 0.0026 | +0.4140 | +0.6486 | 0.485 |
| `combo_min__max_up_ret__bar_rng_5` | +1 | +0.0838 | +0.2101 | +0.2085 | 0.0028 | +0.7177 | +0.7315 | 0.491 |
| `combo_rank_max__yesterday_day_realized_vol__bar_vol_4` | +1 | +0.0644 | +0.2058 | +0.2056 | 0.0034 | +0.6490 | +0.7601 | 0.367 |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | +1 | +0.0461 | +0.2029 | +0.2029 | 0.0038 | +0.9300 | +0.8045 | 0.483 |

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
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | +1 | +0.1390 | +0.2190 | +0.2182 | 0.0000 | +0.4880 | +0.6991 | 0.361 |
| `combo_max__max_up_ret__vol_ratio_10_60` | +1 | +0.1129 | +0.2032 | +0.2014 | 0.0002 | +0.6927 | +0.7783 | 0.462 |
| `combo_ifelse__gap_pct__max_up_ret__bar_vol_5` | +1 | +0.1339 | +0.1885 | +0.1886 | 0.0004 | +0.5958 | +0.6956 | 0.460 |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | +1 | +0.1122 | +0.1825 | +0.1826 | 0.0006 | +0.6162 | +0.7120 | 0.366 |

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
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_rank_min__max_up_ret__bar_vwap_dev_2` | `rank_min` | a=`max_up_ret`, b=`bar_vwap_dev_2` |
| `combo_rank_min__bar_ret_0__bar_body_rng_0` | `rank_min` | a=`bar_ret_0`, b=`bar_body_rng_0` |
| `combo_product__max_down_ret__early_range` | `product` | a=`max_down_ret`, b=`early_range` |
| `combo_ifelse__macd_hist__max_up_ret__yesterday_early_momentum` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_momentum`, cond=`macd_hist` |
| `combo_diff__max_up_ret__vol20` | `diff` | a=`max_up_ret`, b=`vol20` |
| `combo_product__num_up_bars__body_to_range_ratio` | `product` | a=`num_up_bars`, b=`body_to_range_ratio` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_illiquidity_amihud` | `ifelse` | a=`first_bar_return`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_rank_min__max_down_ret__bar_ret_1` | `rank_min` | a=`max_down_ret`, b=`bar_ret_1` |
| `combo_ifelse__gap_pct__first_bar_return__yesterday_early_momentum` | `ifelse` | a=`first_bar_return`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_abs_diff__vol_ratio_10_60__volatility_percentile_20d` | `abs_diff` | a=`vol_ratio_10_60`, b=`volatility_percentile_20d` |
| `combo_ifelse__gap_pct__yesterday_early_vwap_dev__num_up_bars` | `ifelse` | a=`yesterday_early_vwap_dev`, b=`num_up_bars`, cond=`gap_pct` |
| `combo_max__max_up_ret__cci14` | `max` | a=`max_up_ret`, b=`cci14` |
| `combo_diff__max_down_ret__yesterday_day_vwap_dev` | `diff` | a=`max_down_ret`, b=`yesterday_day_vwap_dev` |
| `combo_diff__yesterday_early_momentum__yesterday_day_skew` | `diff` | a=`yesterday_early_momentum`, b=`yesterday_day_skew` |
| `combo_max__max_down_ret__yesterday_illiquidity_amihud` | `max` | a=`max_down_ret`, b=`yesterday_illiquidity_amihud` |
| `combo_abs_diff__cci14__max_up_ret` | `abs_diff` | a=`cci14`, b=`max_up_ret` |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | `tri_ifelse` | a=`vix_skew_proxy`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_body_rng_1` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol5`, c=`bar_body_rng_1`, cond=`vix`, cond2=`vol20` |
| `combo_tri_max__max_up_ret__vol5__max_down_ret` | `tri_max` | a=`max_up_ret`, b=`vol5`, c=`max_down_ret` |
| `combo_rank_max__first_bar_return__num_up_bars` | `rank_max` | a=`first_bar_return`, b=`num_up_bars` |
| `combo_rank_max__max_down_ret__bar_rng_3` | `rank_max` | a=`max_down_ret`, b=`bar_rng_3` |
| `combo_diff__vix_skew_proxy__gap_pct` | `diff` | a=`vix_skew_proxy`, b=`gap_pct` |
| `combo_min__max_up_ret__early_skew` | `min` | a=`max_up_ret`, b=`early_skew` |
| `combo_tri_ifelse__atr14_norm__vol20__vix_rolling_percentile_60d__bar_ret_0__max_down_ret` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_ret_0`, c=`max_down_ret`, cond=`atr14_norm`, cond2=`vol20` |
| `combo_tri_mean__vix_diff_1d__vix_rolling_percentile_60d__yesterday_day_realized_vol` | `tri_mean` | a=`vix_diff_1d`, b=`vix_rolling_percentile_60d`, c=`yesterday_day_realized_vol` |
| `combo_ifelse__gap_pct__vol5__bar_body_rng_1` | `ifelse` | a=`vol5`, b=`bar_body_rng_1`, cond=`gap_pct` |
| `combo_rank_max__vix_diff_1d__vix_iv_spread` | `rank_max` | a=`vix_diff_1d`, b=`vix_iv_spread` |
| `combo_rank_min__vix_diff_1d__bar_rng_5` | `rank_min` | a=`vix_diff_1d`, b=`bar_rng_5` |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_ret_0__early_momentum` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_ret_0`, c=`early_momentum`, cond=`vix`, cond2=`atr14_norm` |
| `combo_ifelse__gap_pct__vix_rolling_percentile_60d__first_bar_return` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`first_bar_return`, cond=`gap_pct` |
| `combo_max__first_30min_return__bar_ret_1` | `max` | a=`first_30min_return`, b=`bar_ret_1` |
| `combo_rank_min__vix_diff_1d__max_up_ret` | `rank_min` | a=`vix_diff_1d`, b=`max_up_ret` |
| `combo_min__max_up_ret__bar_rng_5` | `min` | a=`max_up_ret`, b=`bar_rng_5` |
| `combo_rank_max__yesterday_day_realized_vol__bar_vol_4` | `rank_max` | a=`yesterday_day_realized_vol`, b=`bar_vol_4` |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | `rank_max` | a=`yesterday_day_realized_vol`, b=`vol_ratio_5_20` |
| `combo_max__bar_vol_4__vol5` | `max` | a=`bar_vol_4`, b=`vol5` |
| `combo_tri_min__max_up_ret__bar_ret_0__gap_pct` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`gap_pct` |
| `combo_ifelse__bb_width__yesterday_early_momentum__bar_body_rng_0` | `ifelse` | a=`yesterday_early_momentum`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_tri_median__max_up_ret__max_down_ret__yearly_high_distance` | `tri_median` | a=`max_up_ret`, b=`max_down_ret`, c=`yearly_high_distance` |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__capital_sell_volume__margin_buy_repayment_spread` | `tri_ifelse` | a=`bar_body_rng_0`, b=`capital_sell_volume`, c=`margin_buy_repayment_spread`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_momentum`, cond=`gap_pct` |
| `combo_max__max_up_ret__vol_ratio_10_60` | `max` | a=`max_up_ret`, b=`vol_ratio_10_60` |
| `combo_ifelse__gap_pct__max_up_ret__bar_vol_5` | `ifelse` | a=`max_up_ret`, b=`bar_vol_5`, cond=`gap_pct` |
| `combo_clamp_diff__early_range__yesterday_day_vwap_dev` | `clamp_diff` | a=`early_range`, b=`yesterday_day_vwap_dev` |
