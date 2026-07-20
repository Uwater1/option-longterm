# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `(none)`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **50ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **500ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **588000ETF**: Train `2020-11-01` → `2025-01-01` | Holdout OOS from `2025-01-01` | Lockbox from `2025-07-01`
- **159915ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | Split-Half Pass | B2 Rolling Guard | BH-FDR Pass | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 2,528 | 1,187 | 335 | 66 | 9 |
| 300ETF | long | 221 | 102 | 4 | 4 | 2 |
| 300ETF | short | 11,803 | 2,936 | 372 | 0 | 0 |
| 50ETF | single | 5,318 | 3,666 | 2,767 | 684 | 9 |
| 50ETF | long | 4,610 | 1,419 | 599 | 4 | 0 |
| 50ETF | short | 9,413 | 2,478 | 719 | 37 | 4 |
| 500ETF | single | 3,880 | 2,263 | 672 | 537 | 14 |
| 500ETF | long | 5,170 | 1,572 | 544 | 73 | 7 |
| 500ETF | short | 12,257 | 2,947 | 522 | 3 | 0 |
| 588000ETF | single | 9,761 | 5,797 | 3,120 | 2,772 | 17 |
| 588000ETF | long | 7,477 | 2,694 | 934 | 125 | 5 |
| 588000ETF | short | 10,163 | 2,738 | 655 | 0 | 0 |
| 159915ETF | single | 5,347 | 2,972 | 292 | 181 | 13 |
| 159915ETF | long | 3,621 | 813 | 185 | 0 | 0 |
| 159915ETF | short | 12,470 | 4,982 | 1,607 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 300ETF | single | 9 | +0.1449 | [+0.0990, +0.1862] | +0.3343 | [+0.2397, +0.4380] | +0.9030 | 9.33% | 1.1130 | 2.0726 | 6.44% |
| 300ETF | long | 2 | +0.0438 | [+0.0015, +0.0912] | +0.1381 | [+0.0305, +0.2565] | +0.0788 | 2.60% | 0.3087 | 0.4758 | 14.10% |
| 300ETF | short | 0 | +0.0000* | [-0.0408, +0.0401] | +0.0000* | [-0.1117, +0.1150] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 9 | +0.1322 | [+0.0890, +0.1805] | +0.2967 | [+0.1946, +0.4042] | +0.6242 | 5.25% | 0.5348 | 0.8575 | 15.77% |
| 50ETF | long | 0 | +0.0000* | [-0.0399, +0.0425] | +0.0000* | [-0.1106, +0.1117] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 4 | +0.1007 | [+0.0530, +0.1469] | +0.1517 | [+0.0210, +0.2928] | +0.6121 | 2.97% | 0.3949 | 0.5971 | 13.90% |
| 500ETF | single | 14 | +0.2033 | [+0.1578, +0.2509] | +0.3714 | [+0.2671, +0.4723] | +0.8667 | 13.17% | 1.3789 | 2.2364 | 15.46% |
| 500ETF | long | 7 | +0.1486 | [+0.0972, +0.1990] | +0.1198* | [-0.0069, +0.2407] | +0.8424 | 7.91% | 0.8933 | 1.4326 | 12.64% |
| 500ETF | short | 0 | +0.0000* | [-0.0432, +0.0418] | +0.0000* | [-0.1194, +0.1129] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 17 | +0.2312 | [+0.1694, +0.2845] | +0.5054 | [+0.3793, +0.6158] | +0.8667 | 28.79% | 2.3161 | 8.3048 | 3.90% |
| 588000ETF | long | 5 | +0.1240 | [+0.0677, +0.1811] | +0.2395 | [+0.0857, +0.4066] | +0.5636 | 13.72% | 1.1238 | 3.0892 | 8.38% |
| 588000ETF | short | 0 | +0.0000* | [-0.0595, +0.0634] | +0.0000* | [-0.1584, +0.1506] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.1881 | [+0.1343, +0.2306] | +0.3498 | [+0.2301, +0.4606] | +0.9152 | 20.21% | 1.6173 | 2.9234 | 14.81% |
| 159915ETF | long | 0 | +0.0000* | [-0.0415, +0.0379] | +0.0000* | [-0.1052, +0.1097] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [-0.0415, +0.0379] | +0.0000* | [-0.1109, +0.1090] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 300ETF | single | 9 | +0.0485* | [-0.0089, +0.1050] | +0.1516 | [+0.0100, +0.2763] | +0.4061 | -3.05% | -0.4334 | -0.6324 | 20.77% |
| 300ETF | long | 2 | +0.0307* | [-0.0337, +0.0913] | +0.0413* | [-0.1125, +0.2005] | +0.5636 | -3.20% | -0.5754 | -0.8345 | 19.07% |
| 300ETF | short | 0 | +0.0000* | [-0.0517, +0.0533] | +0.0000* | [-0.1474, +0.1368] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 9 | +0.0218* | [-0.0328, +0.0720] | +0.0653* | [-0.0659, +0.1897] | +0.4788 | -4.46% | -0.6971 | -0.9820 | 29.76% |
| 50ETF | long | 0 | +0.0000* | [-0.0506, +0.0520] | +0.0000* | [-0.1412, +0.1505] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 4 | +0.0151* | [-0.0425, +0.0694] | +0.0476* | [-0.1457, +0.1792] | +0.5636 | -2.35% | -0.4209 | -0.5902 | 18.43% |
| 500ETF | single | 14 | +0.1035 | [+0.0497, +0.1585] | +0.0757* | [-0.0548, +0.1981] | +0.8303 | 3.30% | 0.3742 | 0.6565 | 9.57% |
| 500ETF | long | 7 | +0.0654 | [+0.0049, +0.1197] | -0.1142* | [-0.2666, +0.0526] | +0.6242 | -0.79% | -0.1044 | -0.1667 | 14.55% |
| 500ETF | short | 0 | +0.0000* | [-0.0563, +0.0610] | +0.0000* | [-0.1433, +0.1413] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 17 | +0.0366* | [-0.0547, +0.1450] | +0.0466* | [-0.1230, +0.2861] | +0.2121 | -6.84% | -0.5499 | -0.7508 | 21.02% |
| 588000ETF | long | 5 | +0.0034* | [-0.0899, +0.1107] | +0.2207* | [-0.2261, +0.3847] | -0.2121 | -18.01% | -1.2885 | -1.5826 | 32.24% |
| 588000ETF | short | 0 | +0.0000* | [-0.0848, +0.0901] | +0.0000* | [-0.2363, +0.2478] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.0486* | [-0.0101, +0.1135] | -0.0293* | [-0.1644, +0.1145] | +0.6727 | -0.16% | -0.0150 | -0.0245 | 17.60% |
| 159915ETF | long | 0 | +0.0000* | [-0.0519, +0.0538] | +0.0000* | [-0.1467, +0.1429] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [-0.0519, +0.0538] | +0.0000* | [-0.1421, +0.1378] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 300ETF | single | 9 | +0.0032* | [-0.0817, +0.0728] | +0.0547* | [-0.1293, +0.2142] | +0.3697 | -8.31% | -1.0304 | -1.4965 | 24.88% |
| 300ETF | long | 2 | +0.0220* | [-0.0602, +0.1138] | +0.0747* | [-0.1569, +0.3325] | +0.4667 | -2.11% | -0.4542 | -0.6733 | 9.56% |
| 300ETF | short | 0 | +0.0000* | [-0.0716, +0.0706] | +0.0000* | [-0.1973, +0.1928] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 9 | +0.0622* | [-0.0022, +0.1354] | +0.0705* | [-0.0733, +0.2072] | +0.7091 | -5.32% | -0.8147 | -1.1229 | 16.57% |
| 50ETF | long | 0 | +0.0000* | [-0.0704, +0.0780] | +0.0000* | [-0.1930, +0.1981] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 4 | +0.0887 | [+0.0168, +0.1688] | -0.0171* | [-0.2717, +0.2150] | +0.5152 | 2.20% | 0.3442 | 0.5263 | 6.36% |
| 500ETF | single | 14 | +0.0967 | [+0.0215, +0.1739] | +0.0669* | [-0.1182, +0.2265] | +0.7455 | 6.70% | 0.6798 | 1.2568 | 6.28% |
| 500ETF | long | 7 | +0.0580* | [-0.0263, +0.1372] | -0.1202* | [-0.2871, +0.2013] | +0.3333 | -4.28% | -0.5402 | -0.7986 | 18.46% |
| 500ETF | short | 0 | +0.0000* | [-0.0758, +0.0748] | +0.0000* | [-0.1924, +0.1893] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 17 | +0.0284* | [-0.0955, +0.1780] | -0.0503* | [-0.2878, +0.2671] | +0.0303 | -7.55% | -0.5747 | -0.7933 | 15.13% |
| 588000ETF | long | 5 | -0.0367* | [-0.1441, +0.0880] | -0.0183* | [-0.3505, +0.4436] | -0.1879 | -3.04% | -0.2237 | -0.3002 | 17.78% |
| 588000ETF | short | 0 | +0.0000* | [-0.0980, +0.0973] | +0.0000* | [-0.2835, +0.2820] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 13 | +0.0663* | [-0.0183, +0.1506] | -0.0104* | [-0.2051, +0.2028] | +0.5879 | 4.09% | 0.3451 | 0.5974 | 13.87% |
| 159915ETF | long | 0 | +0.0000* | [-0.0778, +0.0773] | +0.0000* | [-0.1922, +0.1879] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [-0.0778, +0.0773] | +0.0000* | [-0.2026, +0.1923] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1150 | +0.2638 | +0.2640 | 0.0000 | +0.7128 | +0.7091 | 0.000 |
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | +1 | +0.0848 | +0.2403 | +0.2412 | 0.0000 | +0.5228 | +0.7009 | 0.134 |
| `combo_ifelse__macd_hist__max_up_ret__option_oi_growth` | +1 | +0.0915 | +0.2144 | +0.2135 | 0.0000 | +0.7339 | +0.7801 | 0.282 |
| `combo_ifelse__gap_pct__max_up_ret__growth_momentum_ratio` | +1 | +0.0677 | +0.2050 | +0.2040 | 0.0000 | +0.6067 | +0.7167 | 0.329 |
| `combo_ifelse__macd_hist__first_bar_return__yesterday_northbound_net_ratio` | +1 | +0.0911 | +0.1749 | +0.1766 | 0.0010 | +0.6295 | +0.7132 | 0.261 |
| `combo_rank_max__early_range__margin_extreme_rank_252d` | +1 | +0.0454 | +0.1633 | +0.1635 | 0.0020 | +0.6334 | +0.7531 | 0.271 |
| `combo_rank_max__max_up_ret__yesterday_gap_pct` | +1 | +0.0790 | +0.1593 | +0.1598 | 0.0022 | +0.7115 | +0.7543 | 0.349 |
| `combo_diff__short_sell_quantity__roc60` | +1 | +0.0323 | +0.1514 | +0.1507 | 0.0032 | +0.7141 | +0.7848 | 0.264 |
| `combo_min__yesterday_day_skew__rsi21` | -1 | +0.0421 | +0.1444 | +0.1446 | 0.0044 | +0.9896 | +0.8029 | 0.300 |

### 300ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `option_oi_growth` | +1 | +0.0458 | +0.1486 | +0.1494 | 0.0094 | +0.1572 | +0.5578 | 0.000 |
| `sma100_dist` | -1 | +0.0102 | +0.1353 | +0.1360 | 0.0172 | +0.4190 | +0.6475 | 0.022 |

### 300ETF / short
No features admitted.

### 50ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_mean__iv_corridor_width__capital_buy_value__rsi21` | -1 | +0.0916 | +0.2312 | +0.2307 | 0.0000 | +0.9105 | +0.7777 | 0.000 |
| `combo_tri_median__bar_vol_4__bar_vol_0__wavetrend_osc_day` | -1 | +0.0531 | +0.2148 | +0.2143 | 0.0000 | +0.7567 | +0.7795 | 0.341 |
| `combo_ifelse__macd_hist__yesterday_body_ratio__sma100_dist` | -1 | +0.0893 | +0.2041 | +0.2041 | 0.0000 | +0.6593 | +0.7548 | 0.278 |
| `combo_ifelse__macd_hist__yesterday_lunch_gap__capital_buy_volume` | -1 | +0.0592 | +0.1927 | +0.1922 | 0.0002 | +0.6507 | +0.7343 | 0.154 |
| `combo_product__roc60__capital_sell_value` | -1 | +0.0471 | +0.1593 | +0.1592 | 0.0022 | +0.6564 | +0.7660 | 0.287 |
| `combo_product__bar_vol_4__coppock_curve_day` | -1 | +0.0362 | +0.1552 | +0.1556 | 0.0024 | +0.7749 | +0.7718 | 0.269 |
| `combo_ifelse__gap_pct__roc60__margin_extreme_rank_252d` | -1 | +0.0728 | +0.1550 | +0.1555 | 0.0024 | +0.7928 | +0.7490 | 0.336 |
| `combo_clamp_diff__short_balance_quantity__sma20_dist` | +1 | +0.0104 | +0.1498 | +0.1502 | 0.0030 | +0.8821 | +0.7930 | 0.302 |
| `combo_diff__roc10__yearly_low_distance` | -1 | +0.0439 | +0.1495 | +0.1505 | 0.0030 | +0.9203 | +0.8358 | 0.333 |

### 50ETF / long
No features admitted.

### 50ETF / short

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_product__gap_pct__bar_rng_0` | +1 | +0.0076 | +0.2233 | +0.2225 | 0.0000 | +0.3396 | +0.6299 | 0.000 |
| `combo_tri_mean__sma_distance_60d__capital_buy_value__bar_vol_0` | -1 | +0.0775 | +0.1907 | +0.1903 | 0.0006 | +0.3608 | +0.6475 | 0.026 |
| `combo_min__yesterday_lunch_gap__limit_up_proximity_day` | -1 | +0.0336 | +0.1815 | +0.1811 | 0.0010 | +0.2078 | +0.5718 | 0.035 |
| `combo_tri_ifelse__gap_pct__vix__bar_vol_4__yesterday_lunch_gap__max_up_ret` | -1 | +0.0423 | +0.1806 | +0.1797 | 0.0012 | +0.2933 | +0.5672 | 0.324 |

### 500ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__max_up_ret__willr14` | +1 | +0.1032 | +0.3162 | +0.3164 | 0.0000 | +1.2688 | +0.8991 | 0.000 |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | +1 | +0.1477 | +0.2898 | +0.2901 | 0.0000 | +0.6922 | +0.7320 | 0.276 |
| `combo_diff__yesterday_afternoon_momentum__bar_vol_4` | -1 | +0.0976 | +0.2422 | +0.2435 | 0.0000 | +0.6801 | +0.7173 | 0.046 |
| `combo_rank_min__num_up_bars__bar_body_rng_1` | +1 | +0.0948 | +0.2200 | +0.2194 | 0.0000 | +0.5609 | +0.7243 | 0.349 |
| `combo_mean__gap_pct__early_range` | +1 | +0.1229 | +0.2090 | +0.2092 | 0.0000 | +0.5517 | +0.7038 | 0.247 |
| `combo_ifelse__gap_pct__total_balance__short_balance` | -1 | +0.0383 | +0.2025 | +0.2008 | 0.0000 | +0.5575 | +0.7167 | 0.215 |
| `combo_product__yesterday_illiquidity_amihud__early_range` | +1 | +0.0575 | +0.1970 | +0.1966 | 0.0000 | +0.5070 | +0.7050 | 0.340 |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | +1 | +0.1099 | +0.1777 | +0.1770 | 0.0006 | +0.4480 | +0.7032 | 0.276 |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | +1 | +0.0689 | +0.1637 | +0.1655 | 0.0032 | +0.5923 | +0.7038 | 0.322 |
| `combo_max__vol_ratio_10_60__volatility_percentile_20d` | +1 | +0.0699 | +0.1513 | +0.1494 | 0.0058 | +0.5480 | +0.7097 | 0.272 |
| `combo_ratio__bar_body_rng_0__northbound_volume_share` | +1 | +0.1390 | +0.1429 | +0.1421 | 0.0084 | +0.6980 | +0.7249 | 0.035 |
| `combo_rank_max__yesterday_early_momentum__yesterday_illiquidity_amihud` | +1 | +0.0751 | +0.1378 | +0.1381 | 0.0106 | +0.5856 | +0.7185 | 0.293 |
| `combo_tri_min__max_up_ret__yesterday_illiquidity_amihud__northbound_volume_share` | +1 | +0.0079 | +0.1280 | +0.1297 | 0.0152 | +0.6089 | +0.7390 | 0.293 |
| `combo_rank_min__yesterday_lunch_gap__yesterday_afternoon_reversal` | -1 | +0.0812 | +0.1233 | +0.1240 | 0.0204 | +0.5421 | +0.7120 | 0.257 |

### 500ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_abs_diff__willr14__max_up_ret` | +1 | +0.0224 | +0.3177 | +0.3168 | 0.0000 | +0.4204 | +0.6440 | 0.000 |
| `combo_rank_min__yearly_low_distance__max_up_ret` | +1 | +0.0827 | +0.2313 | +0.2302 | 0.0000 | +0.1517 | +0.5642 | 0.178 |
| `combo_min__first_30min_return__bar_body_rng_2` | +1 | +0.0719 | +0.2273 | +0.2275 | 0.0000 | +0.3452 | +0.6129 | 0.256 |
| `combo_product__limit_up_proximity_day__rsi21` | +1 | +0.0452 | +0.1947 | +0.1942 | 0.0012 | +0.1971 | +0.5877 | 0.272 |
| `combo_tri_max__stoch_k__cci14__volume_percentile_20d` | +1 | +0.0202 | +0.1886 | +0.1891 | 0.0018 | +0.1963 | +0.5560 | 0.158 |
| `combo_product__limit_up_proximity_day__bar_vol_5` | +1 | +0.0267 | +0.1775 | +0.1782 | 0.0024 | +0.3081 | +0.6235 | 0.148 |
| `combo_min__body_to_range_ratio__max_up_ret` | +1 | +0.1253 | +0.1733 | +0.1736 | 0.0034 | +0.2975 | +0.6035 | 0.340 |

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | +1 | +0.1720 | +0.4122 | +0.4109 | 0.0000 | +1.1922 | +0.8539 | 0.000 |
| `combo_tri_ifelse__vix__vol20__max_up_ret__vol5__bar_body_rng_1` | +1 | +0.0953 | +0.3585 | +0.3559 | 0.0000 | +1.1887 | +0.8490 | 0.329 |
| `combo_tri_ifelse__vix__vol20__bar_vwap_dev_1__short_sell_cover_spread__max_down_ret` | +1 | +0.1180 | +0.3439 | +0.3432 | 0.0000 | +0.9633 | +0.8312 | 0.242 |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol5__first_bar_return` | +1 | +0.1321 | +0.3265 | +0.3251 | 0.0000 | +0.8332 | +0.7552 | 0.338 |
| `combo_rank_max__first_bar_return__num_up_bars` | +1 | +0.0947 | +0.3055 | +0.3033 | 0.0000 | +0.9874 | +0.8184 | 0.305 |
| `combo_tri_ifelse__atr14_norm__vol20__short_sell_cover_spread__bar_ret_0__early_momentum` | +1 | +0.0745 | +0.3039 | +0.3033 | 0.0000 | +0.8717 | +0.8213 | 0.284 |
| `combo_ifelse__gap_pct__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.1077 | +0.2425 | +0.2421 | 0.0002 | +0.7223 | +0.7354 | 0.313 |
| `combo_max__max_up_ret__early_skew` | +1 | +0.0825 | +0.2350 | +0.2390 | 0.0010 | +0.8351 | +0.8085 | 0.350 |
| `combo_rank_max__vix_diff_1d__bar_vol_4` | +1 | +0.0896 | +0.2306 | +0.2307 | 0.0014 | +0.5371 | +0.7019 | 0.140 |
| `combo_tri_min__vix_diff_1d__vix__max_down_ret` | +1 | +0.1141 | +0.2093 | +0.2075 | 0.0028 | +0.7890 | +0.7641 | 0.296 |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | +1 | +0.0580 | +0.2078 | +0.2084 | 0.0032 | +0.5389 | +0.7216 | 0.185 |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | +1 | +0.0461 | +0.2029 | +0.2029 | 0.0038 | +0.9300 | +0.8045 | 0.343 |
| `yesterday_close_position` | -1 | +0.0479 | +0.1959 | +0.1965 | 0.0054 | +0.5536 | +0.7058 | 0.119 |
| `combo_min__vix__bar_rng_5` | +1 | +0.0600 | +0.1859 | +0.1856 | 0.0084 | +0.6309 | +0.7137 | 0.349 |
| `combo_clamp_diff__vol_gk10__stoch_d` | +1 | +0.0130 | +0.1761 | +0.1770 | 0.0122 | +0.9358 | +0.7937 | 0.318 |
| `combo_ratio__yesterday_range_ratio__vol5` | -1 | +0.0337 | +0.1759 | +0.1751 | 0.0122 | +0.7956 | +0.7493 | 0.192 |
| `combo_product__max_up_ret__vix_vol_ratio` | +1 | +0.1099 | +0.1713 | +0.1730 | 0.0140 | +0.4973 | +0.7098 | 0.263 |

### 588000ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_max__vol5__bar_rng_3` | +1 | +0.0287 | +0.3428 | +0.3432 | 0.0000 | +0.3000 | +0.5913 | 0.000 |
| `combo_abs_diff__growth_momentum_ratio__bar_vol_5` | +1 | +0.0387 | +0.2897 | +0.2906 | 0.0002 | +0.3542 | +0.5824 | 0.335 |
| `combo_tri_min__vix_rolling_percentile_60d__yesterday_day_realized_vol__vix_skew_proxy` | +1 | +0.0800 | +0.2884 | +0.2887 | 0.0002 | +0.2922 | +0.6041 | 0.190 |
| `combo_rank_max__bar_vol_4__vix_skew_proxy` | +1 | +0.0850 | +0.2534 | +0.2530 | 0.0008 | +0.4250 | +0.6308 | 0.198 |
| `first_30min_return` | +1 | +0.1243 | +0.2184 | +0.2176 | 0.0036 | +0.2749 | +0.6239 | 0.069 |

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__margin_buy_repayment_spread` | +1 | +0.1437 | +0.2707 | +0.2687 | 0.0000 | +0.6130 | +0.7056 | 0.000 |
| `combo_diff__max_up_ret__bar_body_rng_1` | +1 | +0.0933 | +0.2322 | +0.2312 | 0.0000 | +0.6740 | +0.7513 | 0.284 |
| `combo_tri_mean__yesterday_afternoon_momentum__yesterday_afternoon_reversal__yesterday_day_vwap_dev` | -1 | +0.1008 | +0.2284 | +0.2288 | 0.0000 | +0.5142 | +0.7050 | 0.139 |
| `combo_abs_diff__early_range__bar_rng_5` | +1 | +0.0451 | +0.1975 | +0.1974 | 0.0002 | +0.6266 | +0.7343 | 0.292 |
| `combo_tri_max__yesterday_first_30min_return__yesterday_early_trend__gap_pct` | +1 | +0.0973 | +0.1953 | +0.1950 | 0.0002 | +0.5302 | +0.7021 | 0.201 |
| `combo_rank_max__max_up_ret__bb_width` | +1 | +0.0712 | +0.1711 | +0.1715 | 0.0014 | +0.4742 | +0.7249 | 0.310 |
| `combo_rank_max__willr14__roc10` | -1 | +0.0005 | +0.1677 | +0.1685 | 0.0014 | +1.3226 | +0.8985 | 0.194 |
| `combo_tri_ifelse__gap_pct__bb_width__first_bar_return__early_range__keltner_squeeze_width` | +1 | +0.1302 | +0.1615 | +0.1594 | 0.0022 | +0.4362 | +0.7173 | 0.336 |
| `combo_diff__bar_vol_4__limit_up_proximity_day` | +1 | +0.0598 | +0.1506 | +0.1518 | 0.0040 | +0.6619 | +0.7202 | 0.347 |
| `combo_ratio__yesterday_day_vwap_dev__bar_vol_4` | -1 | +0.0864 | +0.1434 | +0.1436 | 0.0060 | +0.5127 | +0.7032 | 0.084 |
| `combo_product__willr14__roc10` | +1 | +0.0465 | +0.1339 | +0.1336 | 0.0106 | +0.8185 | +0.7695 | 0.290 |
| `combo_diff__coppock_curve_day__roc10` | +1 | +0.0511 | +0.1311 | +0.1305 | 0.0128 | +0.8634 | +0.8399 | 0.308 |
| `combo_tri_ifelse__gap_pct__bb_width__yearly_high_distance__margin_buy_repayment_spread__stoch_k` | -1 | -0.0221 | +0.1248 | +0.1244 | 0.0166 | +0.7150 | +0.7249 | 0.321 |

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
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | `ifelse` | a=`first_bar_return`, b=`short_sell_cover_spread`, cond=`gap_pct` |
| `combo_ifelse__macd_hist__max_up_ret__option_oi_growth` | `ifelse` | a=`max_up_ret`, b=`option_oi_growth`, cond=`macd_hist` |
| `combo_ifelse__gap_pct__max_up_ret__growth_momentum_ratio` | `ifelse` | a=`max_up_ret`, b=`growth_momentum_ratio`, cond=`gap_pct` |
| `combo_ifelse__macd_hist__first_bar_return__yesterday_northbound_net_ratio` | `ifelse` | a=`first_bar_return`, b=`yesterday_northbound_net_ratio`, cond=`macd_hist` |
| `combo_rank_max__early_range__margin_extreme_rank_252d` | `rank_max` | a=`early_range`, b=`margin_extreme_rank_252d` |
| `combo_rank_max__max_up_ret__yesterday_gap_pct` | `rank_max` | a=`max_up_ret`, b=`yesterday_gap_pct` |
| `combo_diff__short_sell_quantity__roc60` | `diff` | a=`short_sell_quantity`, b=`roc60` |
| `combo_min__yesterday_day_skew__rsi21` | `min` | a=`yesterday_day_skew`, b=`rsi21` |
| `combo_tri_mean__iv_corridor_width__capital_buy_value__rsi21` | `tri_mean` | a=`iv_corridor_width`, b=`capital_buy_value`, c=`rsi21` |
| `combo_tri_median__bar_vol_4__bar_vol_0__wavetrend_osc_day` | `tri_median` | a=`bar_vol_4`, b=`bar_vol_0`, c=`wavetrend_osc_day` |
| `combo_ifelse__macd_hist__yesterday_body_ratio__sma100_dist` | `ifelse` | a=`yesterday_body_ratio`, b=`sma100_dist`, cond=`macd_hist` |
| `combo_ifelse__macd_hist__yesterday_lunch_gap__capital_buy_volume` | `ifelse` | a=`yesterday_lunch_gap`, b=`capital_buy_volume`, cond=`macd_hist` |
| `combo_product__roc60__capital_sell_value` | `product` | a=`roc60`, b=`capital_sell_value` |
| `combo_product__bar_vol_4__coppock_curve_day` | `product` | a=`bar_vol_4`, b=`coppock_curve_day` |
| `combo_ifelse__gap_pct__roc60__margin_extreme_rank_252d` | `ifelse` | a=`roc60`, b=`margin_extreme_rank_252d`, cond=`gap_pct` |
| `combo_clamp_diff__short_balance_quantity__sma20_dist` | `clamp_diff` | a=`short_balance_quantity`, b=`sma20_dist` |
| `combo_diff__roc10__yearly_low_distance` | `diff` | a=`roc10`, b=`yearly_low_distance` |
| `combo_product__gap_pct__bar_rng_0` | `product` | a=`gap_pct`, b=`bar_rng_0` |
| `combo_tri_mean__sma_distance_60d__capital_buy_value__bar_vol_0` | `tri_mean` | a=`sma_distance_60d`, b=`capital_buy_value`, c=`bar_vol_0` |
| `combo_min__yesterday_lunch_gap__limit_up_proximity_day` | `min` | a=`yesterday_lunch_gap`, b=`limit_up_proximity_day` |
| `combo_tri_ifelse__gap_pct__vix__bar_vol_4__yesterday_lunch_gap__max_up_ret` | `tri_ifelse` | a=`bar_vol_4`, b=`yesterday_lunch_gap`, c=`max_up_ret`, cond=`gap_pct`, cond2=`vix` |
| `combo_diff__max_up_ret__willr14` | `diff` | a=`max_up_ret`, b=`willr14` |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_diff__yesterday_afternoon_momentum__bar_vol_4` | `diff` | a=`yesterday_afternoon_momentum`, b=`bar_vol_4` |
| `combo_rank_min__num_up_bars__bar_body_rng_1` | `rank_min` | a=`num_up_bars`, b=`bar_body_rng_1` |
| `combo_mean__gap_pct__early_range` | `mean` | a=`gap_pct`, b=`early_range` |
| `combo_ifelse__gap_pct__total_balance__short_balance` | `ifelse` | a=`total_balance`, b=`short_balance`, cond=`gap_pct` |
| `combo_product__yesterday_illiquidity_amihud__early_range` | `product` | a=`yesterday_illiquidity_amihud`, b=`early_range` |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | `ifelse` | a=`bar_ret_0`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | `clamp_diff` | a=`yesterday_early_vwap_dev`, b=`yesterday_day_skew` |
| `combo_max__vol_ratio_10_60__volatility_percentile_20d` | `max` | a=`vol_ratio_10_60`, b=`volatility_percentile_20d` |
| `combo_ratio__bar_body_rng_0__northbound_volume_share` | `ratio` | a=`bar_body_rng_0`, b=`northbound_volume_share` |
| `combo_rank_max__yesterday_early_momentum__yesterday_illiquidity_amihud` | `rank_max` | a=`yesterday_early_momentum`, b=`yesterday_illiquidity_amihud` |
| `combo_tri_min__max_up_ret__yesterday_illiquidity_amihud__northbound_volume_share` | `tri_min` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud`, c=`northbound_volume_share` |
| `combo_rank_min__yesterday_lunch_gap__yesterday_afternoon_reversal` | `rank_min` | a=`yesterday_lunch_gap`, b=`yesterday_afternoon_reversal` |
| `combo_abs_diff__willr14__max_up_ret` | `abs_diff` | a=`willr14`, b=`max_up_ret` |
| `combo_rank_min__yearly_low_distance__max_up_ret` | `rank_min` | a=`yearly_low_distance`, b=`max_up_ret` |
| `combo_min__first_30min_return__bar_body_rng_2` | `min` | a=`first_30min_return`, b=`bar_body_rng_2` |
| `combo_product__limit_up_proximity_day__rsi21` | `product` | a=`limit_up_proximity_day`, b=`rsi21` |
| `combo_tri_max__stoch_k__cci14__volume_percentile_20d` | `tri_max` | a=`stoch_k`, b=`cci14`, c=`volume_percentile_20d` |
| `combo_product__limit_up_proximity_day__bar_vol_5` | `product` | a=`limit_up_proximity_day`, b=`bar_vol_5` |
| `combo_min__body_to_range_ratio__max_up_ret` | `min` | a=`body_to_range_ratio`, b=`max_up_ret` |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | `tri_ifelse` | a=`vix_skew_proxy`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__max_up_ret__vol5__bar_body_rng_1` | `tri_ifelse` | a=`max_up_ret`, b=`vol5`, c=`bar_body_rng_1`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__bar_vwap_dev_1__short_sell_cover_spread__max_down_ret` | `tri_ifelse` | a=`bar_vwap_dev_1`, b=`short_sell_cover_spread`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol5__first_bar_return` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol5`, c=`first_bar_return`, cond=`vix`, cond2=`atr14_norm` |
| `combo_rank_max__first_bar_return__num_up_bars` | `rank_max` | a=`first_bar_return`, b=`num_up_bars` |
| `combo_tri_ifelse__atr14_norm__vol20__short_sell_cover_spread__bar_ret_0__early_momentum` | `tri_ifelse` | a=`short_sell_cover_spread`, b=`bar_ret_0`, c=`early_momentum`, cond=`atr14_norm`, cond2=`vol20` |
| `combo_ifelse__gap_pct__vix_rolling_percentile_60d__bar_body_rng_1` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_body_rng_1`, cond=`gap_pct` |
| `combo_max__max_up_ret__early_skew` | `max` | a=`max_up_ret`, b=`early_skew` |
| `combo_rank_max__vix_diff_1d__bar_vol_4` | `rank_max` | a=`vix_diff_1d`, b=`bar_vol_4` |
| `combo_tri_min__vix_diff_1d__vix__max_down_ret` | `tri_min` | a=`vix_diff_1d`, b=`vix`, c=`max_down_ret` |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | `clamp_diff` | a=`yesterday_range_ratio`, b=`outside_bar_reversal_day` |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | `rank_max` | a=`yesterday_day_realized_vol`, b=`vol_ratio_5_20` |
| `combo_min__vix__bar_rng_5` | `min` | a=`vix`, b=`bar_rng_5` |
| `combo_clamp_diff__vol_gk10__stoch_d` | `clamp_diff` | a=`vol_gk10`, b=`stoch_d` |
| `combo_ratio__yesterday_range_ratio__vol5` | `ratio` | a=`yesterday_range_ratio`, b=`vol5` |
| `combo_product__max_up_ret__vix_vol_ratio` | `product` | a=`max_up_ret`, b=`vix_vol_ratio` |
| `combo_max__vol5__bar_rng_3` | `max` | a=`vol5`, b=`bar_rng_3` |
| `combo_abs_diff__growth_momentum_ratio__bar_vol_5` | `abs_diff` | a=`growth_momentum_ratio`, b=`bar_vol_5` |
| `combo_tri_min__vix_rolling_percentile_60d__yesterday_day_realized_vol__vix_skew_proxy` | `tri_min` | a=`vix_rolling_percentile_60d`, b=`yesterday_day_realized_vol`, c=`vix_skew_proxy` |
| `combo_rank_max__bar_vol_4__vix_skew_proxy` | `rank_max` | a=`bar_vol_4`, b=`vix_skew_proxy` |
| `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__margin_buy_repayment_spread` | `tri_ifelse` | a=`max_up_ret`, b=`yesterday_early_vwap_dev`, c=`margin_buy_repayment_spread`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_diff__max_up_ret__bar_body_rng_1` | `diff` | a=`max_up_ret`, b=`bar_body_rng_1` |
| `combo_tri_mean__yesterday_afternoon_momentum__yesterday_afternoon_reversal__yesterday_day_vwap_dev` | `tri_mean` | a=`yesterday_afternoon_momentum`, b=`yesterday_afternoon_reversal`, c=`yesterday_day_vwap_dev` |
| `combo_abs_diff__early_range__bar_rng_5` | `abs_diff` | a=`early_range`, b=`bar_rng_5` |
| `combo_tri_max__yesterday_first_30min_return__yesterday_early_trend__gap_pct` | `tri_max` | a=`yesterday_first_30min_return`, b=`yesterday_early_trend`, c=`gap_pct` |
| `combo_rank_max__max_up_ret__bb_width` | `rank_max` | a=`max_up_ret`, b=`bb_width` |
| `combo_rank_max__willr14__roc10` | `rank_max` | a=`willr14`, b=`roc10` |
| `combo_tri_ifelse__gap_pct__bb_width__first_bar_return__early_range__keltner_squeeze_width` | `tri_ifelse` | a=`first_bar_return`, b=`early_range`, c=`keltner_squeeze_width`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_diff__bar_vol_4__limit_up_proximity_day` | `diff` | a=`bar_vol_4`, b=`limit_up_proximity_day` |
| `combo_ratio__yesterday_day_vwap_dev__bar_vol_4` | `ratio` | a=`yesterday_day_vwap_dev`, b=`bar_vol_4` |
| `combo_product__willr14__roc10` | `product` | a=`willr14`, b=`roc10` |
| `combo_diff__coppock_curve_day__roc10` | `diff` | a=`coppock_curve_day`, b=`roc10` |
| `combo_tri_ifelse__gap_pct__bb_width__yearly_high_distance__margin_buy_repayment_spread__stoch_k` | `tri_ifelse` | a=`yearly_high_distance`, b=`margin_buy_repayment_spread`, c=`stoch_k`, cond=`gap_pct`, cond2=`bb_width` |
