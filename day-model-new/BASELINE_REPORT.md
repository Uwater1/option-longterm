# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `(none)`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **50ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **500ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **588000ETF**: Train `2020-11-01` → `2025-01-01` | Holdout OOS from `2025-01-01` | Lockbox from `2025-07-01`
- **159915ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._
_Note: Cost metrics incorporate 15 bps (0.0015) transaction cost per position state transition (entry/turnover). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | Split-Half Pass | B2 Rolling Guard | BH-FDR Pass | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 2,528 | 1,192 | 335 | 162 | 8 |
| 300ETF | long | 221 | 102 | 4 | 4 | 2 |
| 300ETF | short | 11,803 | 2,963 | 372 | 182 | 1 |
| 50ETF | single | 5,318 | 3,656 | 2,765 | 902 | 9 |
| 50ETF | long | 4,610 | 1,422 | 600 | 40 | 1 |
| 50ETF | short | 9,413 | 2,476 | 718 | 241 | 0 |
| 500ETF | single | 3,880 | 2,270 | 672 | 596 | 11 |
| 500ETF | long | 5,170 | 1,570 | 544 | 125 | 7 |
| 500ETF | short | 12,257 | 2,944 | 521 | 334 | 0 |
| 588000ETF | single | 9,761 | 5,812 | 3,120 | 2,812 | 13 |
| 588000ETF | long | 7,477 | 2,701 | 936 | 286 | 4 |
| 588000ETF | short | 10,163 | 2,740 | 652 | 208 | 0 |
| 159915ETF | single | 5,347 | 2,972 | 292 | 222 | 8 |
| 159915ETF | long | 3,621 | 806 | 185 | 40 | 0 |
| 159915ETF | short | 12,470 | 4,972 | 1,616 | 1,338 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 8 | +0.1403 | [+0.0957, +0.1811] | +0.3119 | [+0.2196, +0.4163] | +0.8667 | 17.27% | 1.9856 | 5.25% | 0.6072 | 1.1766 | 12.43% |
| 300ETF | long | 2 | +0.0438 | [+0.0015, +0.0912] | +0.1381 | [+0.0305, +0.2565] | +0.0788 | 8.07% | 0.9498 | 4.94% | 0.5824 | 0.9624 | 8.41% |
| 300ETF | short | 1 | +0.0602 | [+0.0102, +0.1045] | +0.2088 | [+0.0366, +0.3090] | +0.3212 | 4.54% | 0.5871 | -1.51% | -0.1964 | -0.3028 | 29.99% |
| 50ETF | single | 9 | +0.1322 | [+0.0890, +0.1805] | +0.2967 | [+0.1946, +0.4042] | +0.6242 | 12.34% | 1.2424 | 5.60% | 0.5618 | 0.9484 | 15.83% |
| 50ETF | long | 1 | +0.0552 | [+0.0116, +0.0987] | +0.2102 | [+0.0068, +0.3192] | +0.4303 | 0.90% | 0.1688 | -0.60% | -0.1110 | -0.1642 | 20.45% |
| 50ETF | short | 0 | +0.0000* | [-0.0399, +0.0425] | +0.0000* | [-0.0974, +0.1105] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.1958 | [+0.1509, +0.2464] | +0.3762 | [+0.2747, +0.4754] | +0.8061 | 21.32% | 2.0946 | 10.24% | 1.0174 | 1.7545 | 20.12% |
| 500ETF | long | 7 | +0.1505 | [+0.0932, +0.1988] | +0.1761 | [+0.0546, +0.2808] | +0.9273 | 13.02% | 1.4357 | 6.02% | 0.6673 | 1.1106 | 11.27% |
| 500ETF | short | 0 | +0.0000* | [-0.0432, +0.0418] | +0.0000* | [-0.1194, +0.1129] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 13 | +0.2165 | [+0.1559, +0.2724] | +0.5412 | [+0.4148, +0.6467] | +0.8909 | 33.62% | 2.6627 | 21.88% | 1.7458 | 6.1660 | 6.18% |
| 588000ETF | long | 4 | +0.0657 | [+0.0027, +0.1295] | +0.2698 | [+0.0694, +0.4223] | +0.3091 | 16.01% | 1.2262 | 10.66% | 0.8142 | 2.1813 | 10.34% |
| 588000ETF | short | 0 | +0.0000* | [-0.0595, +0.0634] | +0.0000* | [-0.1584, +0.1506] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.1784 | [+0.1238, +0.2256] | +0.3667 | [+0.2560, +0.4700] | +0.9636 | 27.70% | 2.3074 | 16.11% | 1.3554 | 2.6124 | 9.87% |
| 159915ETF | long | 0 | +0.0000* | [-0.0415, +0.0379] | +0.0000* | [-0.1052, +0.1097] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [-0.0415, +0.0379] | +0.0000* | [-0.1109, +0.1090] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 8 | +0.0469* | [-0.0100, +0.1023] | +0.0998* | [-0.0396, +0.2229] | +0.6242 | 1.86% | 0.2930 | -3.54% | -0.5564 | -0.8493 | 18.38% |
| 300ETF | long | 2 | +0.0307* | [-0.0337, +0.0913] | +0.0413* | [-0.1125, +0.2005] | +0.5636 | 2.16% | 0.3895 | -4.00% | -0.7118 | -1.1019 | 23.03% |
| 300ETF | short | 1 | +0.0510* | [-0.0119, +0.1063] | +0.0150* | [-0.1590, +0.1752] | +0.3818 | 1.29% | 0.2839 | -5.27% | -1.1355 | -1.5686 | 31.59% |
| 50ETF | single | 9 | +0.0218* | [-0.0328, +0.0720] | +0.0653* | [-0.0659, +0.1897] | +0.4788 | 2.61% | 0.4093 | -5.46% | -0.8436 | -1.2715 | 34.71% |
| 50ETF | long | 1 | +0.0450* | [-0.0145, +0.1054] | -0.0469* | [-0.2050, +0.1352] | +0.3818 | 0.63% | 0.1822 | -0.77% | -0.2229 | -0.3150 | 8.21% |
| 50ETF | short | 0 | +0.0000* | [-0.0506, +0.0520] | +0.0000* | [-0.1493, +0.1373] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.0862 | [+0.0323, +0.1425] | +0.0616* | [-0.0642, +0.1863] | +0.9152 | 10.88% | 1.1717 | 0.12% | 0.0125 | 0.0220 | 20.65% |
| 500ETF | long | 7 | +0.0658 | [+0.0075, +0.1229] | -0.0547* | [-0.2065, +0.1120] | +0.6121 | 1.01% | 0.1377 | -5.92% | -0.8003 | -1.2027 | 32.66% |
| 500ETF | short | 0 | +0.0000* | [-0.0563, +0.0610] | +0.0000* | [-0.1433, +0.1413] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 13 | +0.0255* | [-0.0696, +0.1336] | +0.0634* | [-0.1256, +0.2990] | +0.0788 | 6.20% | 1.1295 | 0.30% | 0.0554 | 0.0927 | 6.22% |
| 588000ETF | long | 4 | -0.0269* | [-0.1173, +0.0806] | -0.0992* | [-0.4136, +0.1899] | -0.2970 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [-0.0848, +0.0901] | +0.0000* | [-0.2363, +0.2478] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.0563* | [-0.0065, +0.1147] | +0.0038* | [-0.1352, +0.1460] | +0.7091 | 7.83% | 0.7564 | -3.97% | -0.3803 | -0.6285 | 22.94% |
| 159915ETF | long | 0 | +0.0000* | [-0.0519, +0.0538] | +0.0000* | [-0.1467, +0.1429] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [-0.0519, +0.0538] | +0.0000* | [-0.1421, +0.1378] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 8 | -0.0068* | [-0.0899, +0.0640] | +0.0016* | [-0.1779, +0.1623] | +0.1030 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | long | 2 | +0.0220* | [-0.0602, +0.1138] | +0.0747* | [-0.1569, +0.3325] | +0.4667 | 3.28% | 0.7033 | -3.13% | -0.6672 | -1.0449 | 11.36% |
| 300ETF | short | 1 | +0.0567* | [-0.0426, +0.1355] | +0.0820* | [-0.1637, +0.3086] | +0.4788 | 1.13% | 0.2475 | -4.39% | -0.9510 | -1.3262 | 15.08% |
| 50ETF | single | 9 | +0.0622* | [-0.0022, +0.1354] | +0.0705* | [-0.0733, +0.2072] | +0.7091 | 2.08% | 0.3420 | -1.73% | -0.2829 | -0.4209 | 9.62% |
| 50ETF | long | 1 | +0.0836 | [+0.0245, +0.1564] | -0.0677* | [-0.2275, +0.1795] | +0.6848 | 1.02% | 0.2721 | 0.13% | 0.0355 | 0.0501 | 4.43% |
| 50ETF | short | 0 | +0.0000* | [-0.0704, +0.0780] | +0.0000* | [-0.2133, +0.1984] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.0846 | [+0.0109, +0.1610] | +0.1164* | [-0.0522, +0.2816] | +0.6848 | 13.20% | 1.2482 | 1.97% | 0.1867 | 0.3421 | 16.42% |
| 500ETF | long | 7 | +0.0590* | [-0.0251, +0.1404] | -0.0686* | [-0.2866, +0.1419] | +0.4788 | 0.25% | 0.0320 | -6.86% | -0.8849 | -1.3477 | 22.97% |
| 500ETF | short | 0 | +0.0000* | [-0.0758, +0.0748] | +0.0000* | [-0.1924, +0.1893] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 13 | +0.0065* | [-0.1151, +0.1592] | +0.0292* | [-0.2533, +0.3219] | +0.1636 | 2.02% | 0.1526 | -9.75% | -0.7334 | -1.0318 | 15.88% |
| 588000ETF | long | 4 | -0.0621* | [-0.1749, +0.0678] | -0.0485* | [-0.3267, +0.3134] | -0.4424 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [-0.0980, +0.0973] | +0.0000* | [-0.2835, +0.2820] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 8 | +0.0698* | [-0.0192, +0.1456] | +0.0694* | [-0.1289, +0.2733] | +0.6727 | 12.13% | 1.0390 | -0.18% | -0.0152 | -0.0261 | 16.19% |
| 159915ETF | long | 0 | +0.0000* | [-0.0778, +0.0773] | +0.0000* | [-0.1922, +0.1879] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [-0.0778, +0.0773] | +0.0000* | [-0.2026, +0.1923] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

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

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__gap_pct__total_path_length__atr14_norm` | +1 | +0.0602 | +0.2088 | +0.2083 | 0.0004 | +0.2541 | +0.5806 | 0.000 |

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

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__yearly_low_distance__yesterday_wavetrend_osc` | +1 | +0.0552 | +0.2102 | +0.2117 | 0.0000 | +0.2373 | +0.5724 | 0.000 |

### 50ETF / short
No features admitted.

### 500ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__max_up_ret__willr14` | +1 | +0.1032 | +0.3162 | +0.3164 | 0.0000 | +1.2688 | +0.8991 | 0.000 |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | +1 | +0.1477 | +0.2898 | +0.2901 | 0.0000 | +0.6922 | +0.7320 | 0.276 |
| `combo_diff__yesterday_afternoon_momentum__bar_vol_4` | -1 | +0.0976 | +0.2422 | +0.2435 | 0.0000 | +0.6801 | +0.7173 | 0.046 |
| `combo_mean__gap_pct__early_range` | +1 | +0.1229 | +0.2090 | +0.2092 | 0.0000 | +0.5517 | +0.7038 | 0.247 |
| `combo_ifelse__gap_pct__total_balance__short_balance` | -1 | +0.0383 | +0.2025 | +0.2008 | 0.0000 | +0.5575 | +0.7167 | 0.215 |
| `combo_product__yesterday_illiquidity_amihud__early_range` | +1 | +0.0575 | +0.1970 | +0.1966 | 0.0000 | +0.5070 | +0.7050 | 0.340 |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | +1 | +0.1099 | +0.1777 | +0.1770 | 0.0006 | +0.4480 | +0.7032 | 0.276 |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | +1 | +0.0689 | +0.1637 | +0.1655 | 0.0032 | +0.5923 | +0.7038 | 0.322 |
| `combo_max__vol_ratio_10_60__volatility_percentile_20d` | +1 | +0.0699 | +0.1513 | +0.1494 | 0.0058 | +0.5480 | +0.7097 | 0.272 |
| `combo_ratio__bar_body_rng_0__northbound_volume_share` | +1 | +0.1390 | +0.1429 | +0.1421 | 0.0084 | +0.6980 | +0.7249 | 0.035 |
| `combo_tri_min__max_up_ret__yesterday_illiquidity_amihud__northbound_volume_share` | +1 | +0.0079 | +0.1280 | +0.1297 | 0.0152 | +0.6089 | +0.7390 | 0.293 |

### 500ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_abs_diff__willr14__max_up_ret` | +1 | +0.0224 | +0.3177 | +0.3168 | 0.0000 | +0.4204 | +0.6440 | 0.000 |
| `combo_rank_min__yearly_low_distance__max_up_ret` | +1 | +0.0827 | +0.2313 | +0.2302 | 0.0000 | +0.1517 | +0.5642 | 0.178 |
| `combo_min__first_30min_return__bar_body_rng_2` | +1 | +0.0719 | +0.2273 | +0.2275 | 0.0000 | +0.3452 | +0.6129 | 0.256 |
| `combo_tri_median__limit_up_proximity_day__rsi21__cci14` | +1 | +0.0045 | +0.2055 | +0.2049 | 0.0006 | +0.2722 | +0.6141 | 0.310 |
| `combo_product__limit_up_proximity_day__rsi21` | +1 | +0.0452 | +0.1947 | +0.1942 | 0.0012 | +0.1971 | +0.5877 | 0.272 |
| `combo_min__body_to_range_ratio__max_up_ret` | +1 | +0.1253 | +0.1733 | +0.1736 | 0.0034 | +0.2975 | +0.6035 | 0.340 |
| `combo_product__sma50_dist__bar_vol_5` | +1 | +0.0023 | +0.1707 | +0.1705 | 0.0044 | +0.2053 | +0.5836 | 0.244 |

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
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_body_rng_1__early_momentum` | +1 | +0.1253 | +0.2708 | +0.2706 | 0.0000 | +1.0330 | +0.8381 | 0.349 |
| `combo_max__max_up_ret__early_skew` | +1 | +0.0825 | +0.2350 | +0.2390 | 0.0010 | +0.8351 | +0.8085 | 0.350 |
| `combo_rank_max__vix_diff_1d__bar_vol_4` | +1 | +0.0896 | +0.2306 | +0.2307 | 0.0014 | +0.5371 | +0.7019 | 0.140 |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | +1 | +0.0580 | +0.2078 | +0.2084 | 0.0032 | +0.5389 | +0.7216 | 0.185 |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | +1 | +0.0461 | +0.2029 | +0.2029 | 0.0038 | +0.9300 | +0.8045 | 0.343 |
| `combo_clamp_diff__vol_gk10__stoch_d` | +1 | +0.0130 | +0.1761 | +0.1770 | 0.0122 | +0.9358 | +0.7937 | 0.249 |
| `combo_product__max_up_ret__vix_vol_ratio` | +1 | +0.1099 | +0.1713 | +0.1730 | 0.0140 | +0.4973 | +0.7098 | 0.263 |
| `combo_tri_min__vix_diff_1d__vix__max_down_ret` | +1 | +0.1141 | +0.1680 | +0.1662 | 0.0168 | +0.7890 | +0.7641 | 0.296 |

### 588000ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_max__vol5__bar_rng_3` | +1 | +0.0287 | +0.3428 | +0.3432 | 0.0000 | +0.3000 | +0.5913 | 0.000 |
| `combo_abs_diff__growth_momentum_ratio__bar_vol_5` | +1 | +0.0387 | +0.2897 | +0.2906 | 0.0002 | +0.3542 | +0.5824 | 0.335 |
| `combo_tri_min__bar_vol_4__yesterday_day_realized_vol__vix_diff_1d` | +1 | +0.0418 | +0.2734 | +0.2714 | 0.0004 | +0.1570 | +0.5568 | 0.137 |
| `combo_clamp_diff__bar_vol_4__sma_distance_60d` | +1 | +0.0401 | +0.2482 | +0.2460 | 0.0008 | +0.3196 | +0.6199 | 0.268 |

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__margin_buy_repayment_spread` | +1 | +0.1437 | +0.2707 | +0.2687 | 0.0000 | +0.6130 | +0.7056 | 0.000 |
| `combo_diff__max_up_ret__bar_body_rng_1` | +1 | +0.0933 | +0.2322 | +0.2312 | 0.0000 | +0.6740 | +0.7513 | 0.284 |
| `combo_tri_mean__yesterday_afternoon_momentum__yesterday_afternoon_reversal__yesterday_day_vwap_dev` | -1 | +0.1008 | +0.2284 | +0.2288 | 0.0000 | +0.5142 | +0.7050 | 0.139 |
| `combo_rank_max__max_up_ret__bb_width` | +1 | +0.0712 | +0.1711 | +0.1715 | 0.0014 | +0.4742 | +0.7249 | 0.310 |
| `combo_rank_max__willr14__roc10` | -1 | +0.0005 | +0.1677 | +0.1685 | 0.0014 | +1.3226 | +0.8985 | 0.194 |
| `combo_tri_ifelse__gap_pct__bb_width__first_bar_return__early_range__keltner_squeeze_width` | +1 | +0.1302 | +0.1615 | +0.1594 | 0.0022 | +0.4362 | +0.7173 | 0.336 |
| `combo_product__willr14__roc10` | +1 | +0.0465 | +0.1339 | +0.1336 | 0.0106 | +0.8185 | +0.7695 | 0.233 |
| `combo_diff__coppock_curve_day__roc10` | +1 | +0.0511 | +0.1311 | +0.1305 | 0.0128 | +0.8634 | +0.8399 | 0.308 |

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
| `combo_rank_max__early_range__margin_extreme_rank_252d` | `rank_max` | a=`early_range`, b=`margin_extreme_rank_252d` |
| `combo_rank_max__max_up_ret__yesterday_gap_pct` | `rank_max` | a=`max_up_ret`, b=`yesterday_gap_pct` |
| `combo_diff__short_sell_quantity__roc60` | `diff` | a=`short_sell_quantity`, b=`roc60` |
| `combo_min__yesterday_day_skew__rsi21` | `min` | a=`yesterday_day_skew`, b=`rsi21` |
| `combo_tri_min__gap_pct__total_path_length__atr14_norm` | `tri_min` | a=`gap_pct`, b=`total_path_length`, c=`atr14_norm` |
| `combo_tri_mean__iv_corridor_width__capital_buy_value__rsi21` | `tri_mean` | a=`iv_corridor_width`, b=`capital_buy_value`, c=`rsi21` |
| `combo_tri_median__bar_vol_4__bar_vol_0__wavetrend_osc_day` | `tri_median` | a=`bar_vol_4`, b=`bar_vol_0`, c=`wavetrend_osc_day` |
| `combo_ifelse__macd_hist__yesterday_body_ratio__sma100_dist` | `ifelse` | a=`yesterday_body_ratio`, b=`sma100_dist`, cond=`macd_hist` |
| `combo_ifelse__macd_hist__yesterday_lunch_gap__capital_buy_volume` | `ifelse` | a=`yesterday_lunch_gap`, b=`capital_buy_volume`, cond=`macd_hist` |
| `combo_product__roc60__capital_sell_value` | `product` | a=`roc60`, b=`capital_sell_value` |
| `combo_product__bar_vol_4__coppock_curve_day` | `product` | a=`bar_vol_4`, b=`coppock_curve_day` |
| `combo_ifelse__gap_pct__roc60__margin_extreme_rank_252d` | `ifelse` | a=`roc60`, b=`margin_extreme_rank_252d`, cond=`gap_pct` |
| `combo_clamp_diff__short_balance_quantity__sma20_dist` | `clamp_diff` | a=`short_balance_quantity`, b=`sma20_dist` |
| `combo_diff__roc10__yearly_low_distance` | `diff` | a=`roc10`, b=`yearly_low_distance` |
| `combo_diff__yearly_low_distance__yesterday_wavetrend_osc` | `diff` | a=`yearly_low_distance`, b=`yesterday_wavetrend_osc` |
| `combo_diff__max_up_ret__willr14` | `diff` | a=`max_up_ret`, b=`willr14` |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_diff__yesterday_afternoon_momentum__bar_vol_4` | `diff` | a=`yesterday_afternoon_momentum`, b=`bar_vol_4` |
| `combo_mean__gap_pct__early_range` | `mean` | a=`gap_pct`, b=`early_range` |
| `combo_ifelse__gap_pct__total_balance__short_balance` | `ifelse` | a=`total_balance`, b=`short_balance`, cond=`gap_pct` |
| `combo_product__yesterday_illiquidity_amihud__early_range` | `product` | a=`yesterday_illiquidity_amihud`, b=`early_range` |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | `ifelse` | a=`bar_ret_0`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | `clamp_diff` | a=`yesterday_early_vwap_dev`, b=`yesterday_day_skew` |
| `combo_max__vol_ratio_10_60__volatility_percentile_20d` | `max` | a=`vol_ratio_10_60`, b=`volatility_percentile_20d` |
| `combo_ratio__bar_body_rng_0__northbound_volume_share` | `ratio` | a=`bar_body_rng_0`, b=`northbound_volume_share` |
| `combo_tri_min__max_up_ret__yesterday_illiquidity_amihud__northbound_volume_share` | `tri_min` | a=`max_up_ret`, b=`yesterday_illiquidity_amihud`, c=`northbound_volume_share` |
| `combo_abs_diff__willr14__max_up_ret` | `abs_diff` | a=`willr14`, b=`max_up_ret` |
| `combo_rank_min__yearly_low_distance__max_up_ret` | `rank_min` | a=`yearly_low_distance`, b=`max_up_ret` |
| `combo_min__first_30min_return__bar_body_rng_2` | `min` | a=`first_30min_return`, b=`bar_body_rng_2` |
| `combo_tri_median__limit_up_proximity_day__rsi21__cci14` | `tri_median` | a=`limit_up_proximity_day`, b=`rsi21`, c=`cci14` |
| `combo_product__limit_up_proximity_day__rsi21` | `product` | a=`limit_up_proximity_day`, b=`rsi21` |
| `combo_min__body_to_range_ratio__max_up_ret` | `min` | a=`body_to_range_ratio`, b=`max_up_ret` |
| `combo_product__sma50_dist__bar_vol_5` | `product` | a=`sma50_dist`, b=`bar_vol_5` |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | `tri_ifelse` | a=`vix_skew_proxy`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__max_up_ret__vol5__bar_body_rng_1` | `tri_ifelse` | a=`max_up_ret`, b=`vol5`, c=`bar_body_rng_1`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__bar_vwap_dev_1__short_sell_cover_spread__max_down_ret` | `tri_ifelse` | a=`bar_vwap_dev_1`, b=`short_sell_cover_spread`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__vol5__first_bar_return` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol5`, c=`first_bar_return`, cond=`vix`, cond2=`atr14_norm` |
| `combo_rank_max__first_bar_return__num_up_bars` | `rank_max` | a=`first_bar_return`, b=`num_up_bars` |
| `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__bar_body_rng_1__early_momentum` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_body_rng_1`, c=`early_momentum`, cond=`vix`, cond2=`atr14_norm` |
| `combo_max__max_up_ret__early_skew` | `max` | a=`max_up_ret`, b=`early_skew` |
| `combo_rank_max__vix_diff_1d__bar_vol_4` | `rank_max` | a=`vix_diff_1d`, b=`bar_vol_4` |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | `clamp_diff` | a=`yesterday_range_ratio`, b=`outside_bar_reversal_day` |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | `rank_max` | a=`yesterday_day_realized_vol`, b=`vol_ratio_5_20` |
| `combo_clamp_diff__vol_gk10__stoch_d` | `clamp_diff` | a=`vol_gk10`, b=`stoch_d` |
| `combo_product__max_up_ret__vix_vol_ratio` | `product` | a=`max_up_ret`, b=`vix_vol_ratio` |
| `combo_tri_min__vix_diff_1d__vix__max_down_ret` | `tri_min` | a=`vix_diff_1d`, b=`vix`, c=`max_down_ret` |
| `combo_max__vol5__bar_rng_3` | `max` | a=`vol5`, b=`bar_rng_3` |
| `combo_abs_diff__growth_momentum_ratio__bar_vol_5` | `abs_diff` | a=`growth_momentum_ratio`, b=`bar_vol_5` |
| `combo_tri_min__bar_vol_4__yesterday_day_realized_vol__vix_diff_1d` | `tri_min` | a=`bar_vol_4`, b=`yesterday_day_realized_vol`, c=`vix_diff_1d` |
| `combo_clamp_diff__bar_vol_4__sma_distance_60d` | `clamp_diff` | a=`bar_vol_4`, b=`sma_distance_60d` |
| `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__margin_buy_repayment_spread` | `tri_ifelse` | a=`max_up_ret`, b=`yesterday_early_vwap_dev`, c=`margin_buy_repayment_spread`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_diff__max_up_ret__bar_body_rng_1` | `diff` | a=`max_up_ret`, b=`bar_body_rng_1` |
| `combo_tri_mean__yesterday_afternoon_momentum__yesterday_afternoon_reversal__yesterday_day_vwap_dev` | `tri_mean` | a=`yesterday_afternoon_momentum`, b=`yesterday_afternoon_reversal`, c=`yesterday_day_vwap_dev` |
| `combo_rank_max__max_up_ret__bb_width` | `rank_max` | a=`max_up_ret`, b=`bb_width` |
| `combo_rank_max__willr14__roc10` | `rank_max` | a=`willr14`, b=`roc10` |
| `combo_tri_ifelse__gap_pct__bb_width__first_bar_return__early_range__keltner_squeeze_width` | `tri_ifelse` | a=`first_bar_return`, b=`early_range`, c=`keltner_squeeze_width`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_product__willr14__roc10` | `product` | a=`willr14`, b=`roc10` |
| `combo_diff__coppock_curve_day__roc10` | `diff` | a=`coppock_curve_day`, b=`roc10` |
