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
| 300ETF | single | 2,528 | 1,507 | 343 | 286 | 21 |
| 300ETF | long | 221 | 144 | 13 | 10 | 3 |
| 300ETF | short | 11,803 | 6,179 | 724 | 162 | 9 |
| 50ETF | single | 5,318 | 4,305 | 2,867 | 2,831 | 25 |
| 50ETF | long | 4,610 | 2,532 | 974 | 499 | 18 |
| 50ETF | short | 9,413 | 5,275 | 1,411 | 570 | 19 |
| 500ETF | single | 3,880 | 2,975 | 678 | 647 | 32 |
| 500ETF | long | 5,170 | 3,187 | 951 | 744 | 31 |
| 500ETF | short | 12,257 | 6,641 | 1,043 | 237 | 3 |
| 588000ETF | single | 9,761 | 7,733 | 3,307 | 3,290 | 40 |
| 588000ETF | long | 7,477 | 5,079 | 1,680 | 1,303 | 37 |
| 588000ETF | short | 10,163 | 5,499 | 1,073 | 47 | 0 |
| 159915ETF | single | 5,347 | 3,927 | 321 | 272 | 22 |
| 159915ETF | long | 3,621 | 1,951 | 395 | 219 | 6 |
| 159915ETF | short | 12,470 | 7,542 | 2,131 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 300ETF | single | 21 | +0.1603 | [+0.1167, +0.2020] | +0.2976 | [+0.2076, +0.3931] | +0.9636 | 9.20% | 1.0499 | 1.8691 | 8.67% |
| 300ETF | long | 3 | +0.0305* | [-0.0152, +0.0822] | +0.0558* | [-0.0671, +0.1887] | +0.4667 | 0.05% | 0.0059 | 0.0085 | 23.76% |
| 300ETF | short | 9 | +0.1595 | [+0.1114, +0.2035] | +0.1359* | [-0.0162, +0.2492] | +0.8545 | 4.98% | 0.6592 | 1.0725 | 13.50% |
| 50ETF | single | 25 | +0.1254 | [+0.0812, +0.1747] | +0.2475 | [+0.1509, +0.3495] | +0.6485 | 4.94% | 0.4695 | 0.7401 | 13.66% |
| 50ETF | long | 18 | +0.0931 | [+0.0466, +0.1422] | +0.0616* | [-0.0560, +0.2077] | +0.8545 | 2.95% | 0.3002 | 0.4483 | 18.47% |
| 50ETF | short | 19 | +0.1106 | [+0.0586, +0.1603] | +0.1911 | [+0.0440, +0.3204] | +0.7576 | 1.79% | 0.1846 | 0.2657 | 14.56% |
| 500ETF | single | 32 | +0.2183 | [+0.1729, +0.2666] | +0.3610 | [+0.2536, +0.4590] | +0.9152 | 15.25% | 1.7799 | 3.8272 | 8.30% |
| 500ETF | long | 31 | +0.1936 | [+0.1429, +0.2420] | +0.2006 | [+0.0727, +0.3277] | +0.9758 | 13.21% | 1.3730 | 2.3155 | 8.96% |
| 500ETF | short | 3 | +0.0971 | [+0.0473, +0.1483] | +0.1747 | [+0.0489, +0.3037] | +0.5515 | 2.73% | 0.3539 | 0.5768 | 18.77% |
| 588000ETF | single | 40 | +0.2099 | [+0.1525, +0.2539] | +0.4090 | [+0.2990, +0.5222] | +0.9515 | 21.94% | 1.7648 | 5.2258 | 6.74% |
| 588000ETF | long | 37 | +0.1204 | [+0.0666, +0.1751] | +0.2007 | [+0.0519, +0.3717] | +0.6364 | 12.79% | 1.0058 | 2.6072 | 6.73% |
| 588000ETF | short | 0 | +0.0000* | [-0.0595, +0.0634] | +0.0000* | [-0.1584, +0.1506] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 22 | +0.1987 | [+0.1460, +0.2435] | +0.3511 | [+0.2152, +0.4656] | +0.9758 | 20.69% | 1.6441 | 3.0045 | 16.15% |
| 159915ETF | long | 6 | +0.1069 | [+0.0560, +0.1573] | +0.1700 | [+0.0553, +0.2950] | +0.8545 | 9.19% | 1.0453 | 1.8135 | 15.27% |
| 159915ETF | short | 0 | +0.0000* | [-0.0415, +0.0379] | +0.0000* | [-0.1109, +0.1090] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 300ETF | single | 21 | +0.0506* | [-0.0084, +0.1129] | +0.1446 | [+0.0064, +0.2838] | +0.6848 | -0.50% | -0.0798 | -0.1264 | 15.61% |
| 300ETF | long | 3 | +0.0021* | [-0.0597, +0.0631] | +0.0332* | [-0.1144, +0.1943] | +0.2242 | -6.50% | -1.1045 | -1.5071 | 32.02% |
| 300ETF | short | 9 | +0.0457* | [-0.0145, +0.1024] | +0.1062* | [-0.0581, +0.2662] | +0.5152 | -1.44% | -0.2999 | -0.4373 | 18.19% |
| 50ETF | single | 25 | +0.0329* | [-0.0216, +0.0864] | +0.0951* | [-0.0458, +0.2100] | +0.4909 | -3.44% | -0.5059 | -0.7272 | 24.46% |
| 50ETF | long | 18 | +0.0507* | [-0.0104, +0.1085] | +0.1300* | [-0.0314, +0.2650] | +0.7333 | -3.72% | -0.6765 | -0.9755 | 18.71% |
| 50ETF | short | 19 | +0.0456* | [-0.0140, +0.0913] | +0.0427* | [-0.1036, +0.1612] | +0.7212 | -3.10% | -0.5310 | -0.7065 | 23.29% |
| 500ETF | single | 32 | +0.0965 | [+0.0463, +0.1493] | +0.1138* | [-0.0226, +0.2374] | +0.7455 | 4.46% | 0.5555 | 0.9647 | 8.18% |
| 500ETF | long | 31 | +0.0606* | [-0.0001, +0.1115] | -0.0123* | [-0.1094, +0.1625] | +0.7333 | -3.68% | -0.4360 | -0.6497 | 19.65% |
| 500ETF | short | 3 | +0.0493* | [-0.0043, +0.1074] | +0.0155* | [-0.1777, +0.1628] | +0.5273 | -1.70% | -0.3129 | -0.4404 | 23.85% |
| 588000ETF | single | 40 | +0.0178* | [-0.0734, +0.1167] | -0.0483* | [-0.2534, +0.2341] | +0.2727 | -7.98% | -0.6150 | -0.8363 | 26.54% |
| 588000ETF | long | 37 | -0.0026* | [-0.0816, +0.1171] | -0.0902* | [-0.4033, +0.1976] | -0.2242 | -16.53% | -1.1870 | -1.5086 | 25.22% |
| 588000ETF | short | 0 | +0.0000* | [-0.0848, +0.0901] | +0.0000* | [-0.2363, +0.2478] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 22 | +0.0915 | [+0.0342, +0.1472] | +0.0889* | [-0.0429, +0.2233] | +0.7939 | 7.21% | 0.6771 | 1.1989 | 10.25% |
| 159915ETF | long | 6 | +0.0667 | [+0.0077, +0.1196] | -0.0877* | [-0.2048, +0.0658] | +0.8424 | -2.68% | -0.3460 | -0.5364 | 22.07% |
| 159915ETF | short | 0 | +0.0000* | [-0.0519, +0.0538] | +0.0000* | [-0.1421, +0.1378] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 300ETF | single | 21 | +0.0335* | [-0.0511, +0.1143] | +0.0768* | [-0.1187, +0.2813] | +0.4667 | -0.29% | -0.0391 | -0.0748 | 15.23% |
| 300ETF | long | 3 | +0.0321* | [-0.0688, +0.1374] | -0.0397* | [-0.2551, +0.1686] | +0.5758 | -3.56% | -0.5909 | -0.8880 | 12.56% |
| 300ETF | short | 9 | +0.0522* | [-0.0339, +0.1322] | +0.0402* | [-0.2062, +0.2690] | +0.3818 | 0.75% | 0.1447 | 0.2301 | 11.03% |
| 50ETF | single | 25 | +0.0608* | [-0.0111, +0.1422] | +0.1006* | [-0.0653, +0.2383] | +0.4303 | -3.15% | -0.4406 | -0.6559 | 13.80% |
| 50ETF | long | 18 | +0.0507* | [-0.0184, +0.1300] | +0.0014* | [-0.2875, +0.1692] | +0.5152 | -4.67% | -1.0400 | -1.5223 | 13.60% |
| 50ETF | short | 19 | +0.0661* | [-0.0133, +0.1355] | +0.0004* | [-0.2037, +0.2478] | +0.4545 | 0.18% | 0.0296 | 0.0423 | 7.57% |
| 500ETF | single | 32 | +0.0958 | [+0.0187, +0.1747] | +0.1208* | [-0.0849, +0.2711] | +0.7939 | 1.65% | 0.1974 | 0.3322 | 11.95% |
| 500ETF | long | 31 | +0.0538* | [-0.0312, +0.1314] | +0.0103* | [-0.2691, +0.2042] | +0.5879 | -4.28% | -0.4705 | -0.6968 | 16.60% |
| 500ETF | short | 3 | +0.0924 | [+0.0184, +0.1880] | +0.0919* | [-0.1844, +0.3045] | +0.5394 | -0.18% | -0.0317 | -0.0465 | 13.25% |
| 588000ETF | single | 40 | -0.0120* | [-0.1286, +0.1261] | -0.1708* | [-0.4127, +0.1909] | -0.0788 | -24.49% | -1.7864 | -2.1745 | 33.19% |
| 588000ETF | long | 37 | -0.0355* | [-0.1357, +0.1047] | -0.2546* | [-0.4297, +0.3459] | -0.2364 | -13.76% | -1.0243 | -1.2476 | 23.36% |
| 588000ETF | short | 0 | +0.0000* | [-0.0980, +0.0973] | +0.0000* | [-0.2835, +0.2820] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 22 | +0.1186 | [+0.0320, +0.1967] | +0.1196* | [-0.0386, +0.3470] | +0.8303 | 15.25% | 1.2795 | 2.5114 | 8.97% |
| 159915ETF | long | 6 | +0.0741* | [-0.0073, +0.1489] | -0.1969* | [-0.3644, +0.0502] | +0.6000 | -0.61% | -0.0837 | -0.1386 | 10.96% |
| 159915ETF | short | 0 | +0.0000* | [-0.0778, +0.0773] | +0.0000* | [-0.2026, +0.1923] | +0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1150 | +0.2638 | +0.9365 | 0.0000 | +0.7128 | +0.7091 | 0.000 |
| `combo_ifelse__gap_pct__max_up_ret__option_oi_growth` | +1 | +0.0803 | +0.2474 | +0.8949 | 0.0000 | +0.6845 | +0.7402 | 0.412 |
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | +1 | +0.0848 | +0.2403 | +0.8979 | 0.0000 | +0.5228 | +0.7009 | 0.268 |
| `combo_ifelse__macd_hist__max_up_ret__option_oi_growth` | +1 | +0.0915 | +0.2144 | +0.8660 | 0.0000 | +0.7339 | +0.7801 | 0.481 |
| `combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio` | +1 | +0.0688 | +0.2104 | +0.8527 | 0.0000 | +0.6433 | +0.7185 | 0.458 |
| `combo_ifelse__macd_hist__bar_ret_0__bar_body_rng_0` | +1 | +0.0961 | +0.1992 | +0.8556 | 0.0000 | +0.5026 | +0.7191 | 0.396 |
| `combo_ifelse__macd_hist__bar_body_rng_0__short_sell_cover_spread` | +1 | +0.1041 | +0.1986 | +0.8660 | 0.0000 | +0.6207 | +0.7326 | 0.477 |
| `combo_max__max_up_ret__yesterday_gap_pct` | +1 | +0.0853 | +0.1927 | +0.8612 | 0.0004 | +0.7205 | +0.7765 | 0.421 |
| `combo_ifelse__macd_hist__max_up_ret__growth_momentum_ratio` | +1 | +0.0750 | +0.1915 | +0.8578 | 0.0004 | +0.5472 | +0.7443 | 0.386 |
| `combo_clamp_diff__max_up_ret__willr14` | +1 | +0.0705 | +0.1769 | +0.8349 | 0.0010 | +0.5724 | +0.7161 | 0.390 |
| `combo_ifelse__macd_hist__first_bar_return__yesterday_northbound_net_ratio` | +1 | +0.0911 | +0.1749 | +0.8482 | 0.0010 | +0.6295 | +0.7132 | 0.424 |
| `combo_rank_max__early_range__margin_extreme_rank_252d` | +1 | +0.0454 | +0.1633 | +0.8247 | 0.0020 | +0.6334 | +0.7531 | 0.348 |
| `combo_diff__short_sell_quantity__roc60` | +1 | +0.0323 | +0.1514 | +0.8175 | 0.0032 | +0.7141 | +0.7848 | 0.264 |
| `combo_rank_min__yesterday_day_skew__sma100_dist` | -1 | +0.0329 | +0.1478 | +0.7952 | 0.0036 | +0.8972 | +0.7842 | 0.360 |
| `combo_rank_min__roc60__twenty_gap_bars_regime` | -1 | +0.0327 | +0.1329 | +0.8116 | 0.0088 | +1.2228 | +0.8610 | 0.495 |
| `combo_rank_max__first_30min_return__bar_vwap_dev_2` | +1 | +0.0378 | +0.1286 | +0.7666 | 0.0112 | +0.6045 | +0.7595 | 0.427 |
| `first_bar_volume` | -1 | +0.0158 | +0.1238 | +0.7846 | 0.0146 | +0.6047 | +0.7484 | 0.215 |
| `combo_product__short_sell_quantity__wavetrend_osc_day` | +1 | +0.0522 | +0.1090 | +0.7930 | 0.0338 | +0.5293 | +0.7349 | 0.255 |
| `combo_abs_diff__short_sell_quantity__early_range` | +1 | +0.0425 | +0.1054 | +0.7874 | 0.0392 | +0.5336 | +0.7419 | 0.479 |
| `combo_diff__max_up_ret__total_balance` | +1 | +0.0415 | +0.0823 | +0.7545 | 0.0974 | +0.4419 | +0.7009 | 0.446 |
| `combo_rank_min__early_range__twenty_gap_bars_regime` | -1 | +0.0241 | +0.0738 | +0.7518 | 0.1348 | +0.5557 | +0.7220 | 0.496 |

### 300ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sma100_dist` | -1 | +0.0102 | +0.1353 | +0.7852 | 0.0172 | +0.4190 | +0.6475 | 0.000 |
| `early_vwap_dev` | -1 | +0.0062 | +0.1342 | +0.7835 | 0.0178 | +0.1668 | +0.5654 | 0.016 |
| `cvd_divergence_day` | -1 | +0.0093 | +0.0712 | +0.7152 | 0.1464 | +0.2828 | +0.6211 | 0.039 |

### 300ETF / short

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__gap_pct__total_path_length__atr14_norm` | +1 | +0.0602 | +0.2088 | +0.9005 | 0.0004 | +0.2541 | +0.5806 | 0.000 |
| `combo_abs_diff__bar_vol_4__volume_sma_ratio` | +1 | +0.0684 | +0.1737 | +0.8649 | 0.0030 | +0.4893 | +0.6880 | 0.021 |
| `combo_tri_ifelse__gap_pct__atr14_norm__total_balance__yesterday_day_skew__margin_balance` | +1 | +0.0197 | +0.1394 | +0.8303 | 0.0146 | +0.3810 | +0.6393 | 0.205 |
| `combo_ifelse__sma20_dist__total_balance__short_sell_cover_spread` | +1 | +0.0650 | +0.1133 | +0.8011 | 0.0370 | +0.2984 | +0.6059 | 0.355 |
| `combo_rank_min__short_sell_cover_spread__yesterday_gap` | +1 | +0.0519 | +0.1092 | +0.8057 | 0.0424 | +0.2650 | +0.6082 | 0.334 |
| `combo_diff__max_down_ret__sma20_dist` | +1 | +0.0546 | +0.1063 | +0.8009 | 0.0466 | +0.2982 | +0.6317 | 0.196 |
| `combo_max__gap_pct__first_bar_return` | +1 | +0.0867 | +0.1054 | +0.7964 | 0.0480 | +0.1610 | +0.5806 | 0.171 |
| `combo_tri_ifelse__gap_pct__atr14_norm__northbound_net__yesterday_day_skew__mfi14` | +1 | +0.0486 | +0.0989 | +0.8146 | 0.0608 | +0.2321 | +0.5818 | 0.236 |
| `yesterday_lunch_gap` | -1 | +0.0510 | +0.0974 | +0.7850 | 0.0642 | +0.1978 | +0.5947 | 0.269 |

### 50ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_mean__iv_corridor_width__capital_buy_value__rsi21` | -1 | +0.0916 | +0.2312 | +0.8763 | 0.0000 | +0.9105 | +0.7777 | 0.000 |
| `combo_tri_median__bar_vol_4__bar_vol_0__wavetrend_osc_day` | -1 | +0.0531 | +0.2148 | +0.8575 | 0.0000 | +0.7567 | +0.7795 | 0.341 |
| `combo_ifelse__macd_hist__yesterday_body_ratio__sma100_dist` | -1 | +0.0893 | +0.2041 | +0.8523 | 0.0000 | +0.6593 | +0.7548 | 0.278 |
| `combo_ifelse__macd_hist__yesterday_lunch_gap__capital_buy_volume` | -1 | +0.0592 | +0.1927 | +0.8510 | 0.0002 | +0.6507 | +0.7343 | 0.154 |
| `combo_min__iv_corridor_width__margin_net_buy` | -1 | +0.0701 | +0.1829 | +0.8377 | 0.0004 | +0.5836 | +0.7396 | 0.492 |
| `combo_ifelse__gap_pct__capital_buy_value__bar_vol_0` | -1 | +0.0813 | +0.1751 | +0.8265 | 0.0008 | +0.6877 | +0.7408 | 0.435 |
| `combo_tri_min__bar_vol_4__sma100_dist__yearly_low_distance` | -1 | +0.0353 | +0.1704 | +0.8206 | 0.0010 | +0.8545 | +0.8147 | 0.498 |
| `combo_clamp_diff__willr14__yesterday_stoch_rsi_cross` | -1 | +0.0702 | +0.1699 | +0.8307 | 0.0010 | +0.6640 | +0.7519 | 0.351 |
| `combo_ifelse__macd_hist__yesterday_lunch_gap__sma_distance_60d` | -1 | +0.0627 | +0.1682 | +0.8517 | 0.0010 | +0.5282 | +0.7144 | 0.498 |
| `combo_diff__sma100_dist__short_balance_quantity` | -1 | +0.0138 | +0.1618 | +0.7946 | 0.0016 | +0.7880 | +0.7543 | 0.458 |
| `combo_product__roc60__capital_sell_value` | -1 | +0.0471 | +0.1593 | +0.8122 | 0.0022 | +0.6564 | +0.7660 | 0.287 |
| `combo_ifelse__macd_hist__margin_extreme_rank_252d__sma100_dist` | -1 | +0.0465 | +0.1568 | +0.8209 | 0.0024 | +0.7205 | +0.7701 | 0.473 |
| `combo_product__bar_vol_4__coppock_curve_day` | -1 | +0.0362 | +0.1552 | +0.8199 | 0.0024 | +0.7749 | +0.7718 | 0.269 |
| `combo_diff__roc10__yearly_low_distance` | -1 | +0.0439 | +0.1495 | +0.8305 | 0.0030 | +0.9203 | +0.8358 | 0.273 |
| `combo_max__short_balance_quantity__sma20_dist` | -1 | +0.0436 | +0.1483 | +0.7994 | 0.0032 | +0.8151 | +0.7572 | 0.440 |
| `combo_rank_min__roc60__margin_buy_repayment_spread` | -1 | +0.0225 | +0.1441 | +0.7837 | 0.0042 | +0.6964 | +0.7320 | 0.496 |
| `combo_min__willr14__sma10_dist` | -1 | +0.0328 | +0.1427 | +0.7949 | 0.0046 | +0.7166 | +0.7619 | 0.464 |
| `combo_mean__roc10__bar_rng_5` | -1 | +0.0677 | +0.1324 | +0.7689 | 0.0098 | +0.8396 | +0.8012 | 0.482 |
| `combo_ifelse__macd_hist__iv_corridor_width__margin_extreme_rank_252d` | -1 | +0.0626 | +0.1265 | +0.7794 | 0.0126 | +0.6222 | +0.7630 | 0.439 |
| `combo_ratio__yesterday_body_ratio__bar_vol_5` | -1 | +0.0259 | +0.1212 | +0.7792 | 0.0170 | +0.4498 | +0.7097 | 0.307 |
| `combo_rank_max__roc10__margin_buy_repayment_spread` | -1 | +0.0765 | +0.1161 | +0.7528 | 0.0210 | +0.7862 | +0.7836 | 0.497 |
| `combo_ratio__roc20__bar_vol_4` | -1 | +0.0474 | +0.1037 | +0.7620 | 0.0384 | +0.6159 | +0.7249 | 0.167 |
| `combo_ifelse__sma20_dist__iv_corridor_width__yesterday_body_ratio` | -1 | +0.0621 | +0.0990 | +0.7390 | 0.0462 | +0.5128 | +0.7167 | 0.410 |
| `combo_mean__sma200_dist__vix_rolling_percentile_60d` | -1 | +0.0646 | +0.0989 | +0.7464 | 0.0466 | +0.7858 | +0.7777 | 0.469 |
| `combo_clamp_diff__sma_distance_60d__sma200_dist` | -1 | +0.0372 | +0.0532 | +0.6962 | 0.2564 | +1.0586 | +0.8575 | 0.472 |

### 50ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_median__tech_value_rotation__rsi21__iv_corridor_width` | -1 | +0.0568 | +0.2002 | +0.8708 | 0.0004 | +0.2732 | +0.6199 | 0.000 |
| `combo_tri_min__margin_net_buy__tech_value_rotation__sma100_dist` | -1 | +0.0204 | +0.1887 | +0.8335 | 0.0012 | +0.4617 | +0.6915 | 0.347 |
| `combo_product__yesterday_day_realized_vol__iv_corridor_width` | -1 | +0.0408 | +0.1846 | +0.8652 | 0.0018 | +0.1707 | +0.5619 | 0.268 |
| `combo_rank_max__margin_net_buy__iv_corridor_width` | -1 | +0.0475 | +0.1840 | +0.8321 | 0.0022 | +0.2975 | +0.6182 | 0.475 |
| `combo_rank_min__sma_distance_60d__total_balance` | -1 | +0.0392 | +0.1801 | +0.8440 | 0.0028 | +0.2701 | +0.6346 | 0.353 |
| `combo_tri_min__yearly_low_distance__roc10__bar_vol_4` | -1 | +0.0210 | +0.1477 | +0.8074 | 0.0118 | +0.3365 | +0.6328 | 0.461 |
| `combo_mean__max_down_ret__num_up_bars` | +1 | +0.0296 | +0.1477 | +0.8095 | 0.0118 | +0.2384 | +0.6223 | 0.136 |
| `combo_clamp_diff__capital_buy_value__yesterday_day_realized_vol` | -1 | +0.0546 | +0.1416 | +0.7986 | 0.0148 | +0.2257 | +0.5584 | 0.237 |
| `combo_ifelse__vol60__yesterday_wavetrend_osc__yesterday_lunch_gap` | -1 | +0.0689 | +0.1353 | +0.8058 | 0.0192 | +0.2288 | +0.5754 | 0.421 |
| `combo_ratio__yearly_low_distance__yesterday_day_realized_vol` | -1 | -0.0057 | +0.1166 | +0.7890 | 0.0408 | +0.2977 | +0.6076 | 0.452 |
| `combo_tri_mean__yesterday_wavetrend_osc__max_down_ret__yesterday_early_range` | +1 | -0.0112 | +0.1163 | +0.7817 | 0.0412 | +0.2275 | +0.5730 | 0.465 |
| `combo_min__roc5__yesterday_day_realized_vol` | -1 | +0.0063 | +0.0977 | +0.7632 | 0.0718 | +0.2378 | +0.5513 | 0.439 |
| `combo_abs_diff__max_up_ret__num_up_bars` | +1 | +0.0063 | +0.0966 | +0.7500 | 0.0742 | +0.2549 | +0.5982 | 0.161 |
| `combo_abs_diff__yesterday_early_trend__limit_up_proximity_day` | +1 | +0.0003 | +0.0921 | +0.7494 | 0.0836 | +0.2200 | +0.6065 | 0.335 |
| `combo_rank_min__margin_net_buy__margin_repayment` | -1 | +0.0361 | +0.0911 | +0.7757 | 0.0864 | +0.3074 | +0.5982 | 0.416 |
| `combo_tri_mean__margin_net_buy__early_range__roc10` | -1 | +0.0703 | +0.0896 | +0.7349 | 0.0884 | +0.2092 | +0.5578 | 0.454 |
| `combo_min__yearly_low_distance__capital_buy_volume` | -1 | +0.0357 | +0.0873 | +0.7480 | 0.0934 | +0.2314 | +0.6152 | 0.462 |
| `combo_product__tech_value_rotation__yesterday_day_realized_vol` | +1 | +0.0492 | +0.0798 | +0.7480 | 0.1184 | +0.3284 | +0.6475 | 0.437 |

### 50ETF / short

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_product__gap_pct__bar_rng_0` | +1 | +0.0076 | +0.2233 | +0.8642 | 0.0000 | +0.3396 | +0.6299 | 0.000 |
| `combo_tri_median__bar_vol_4__rsi21__bar_vol_0` | -1 | +0.0495 | +0.2134 | +0.8605 | 0.0000 | +0.3919 | +0.6411 | 0.056 |
| `combo_tri_mean__gap_pct__vol10__iv_vol_ratio` | +1 | +0.0088 | +0.1851 | +0.8409 | 0.0008 | +0.4804 | +0.6716 | 0.426 |
| `combo_tri_ifelse__gap_pct__vol10__mfi14__bar_rng_0__bar_vol_5` | -1 | +0.0573 | +0.1754 | +0.8239 | 0.0020 | +0.2220 | +0.5642 | 0.424 |
| `combo_diff__rsi21__yearly_low_distance` | -1 | +0.0504 | +0.1676 | +0.8282 | 0.0026 | +0.2621 | +0.6182 | 0.269 |
| `combo_tri_ifelse__gap_pct__vix__sma50_dist__bar_body_rng_1__bar_rng_0` | -1 | +0.0906 | +0.1592 | +0.8080 | 0.0050 | +0.3414 | +0.6117 | 0.384 |
| `combo_tri_ifelse__gap_pct__vol10__northbound_net__max_up_ret__bar_vol_5` | +1 | +0.0404 | +0.1478 | +0.8066 | 0.0114 | +0.3584 | +0.6223 | 0.460 |
| `combo_tri_ifelse__vol10__vix__yesterday_lunch_gap__bar_vol_5__rsi21` | -1 | +0.0400 | +0.1463 | +0.8047 | 0.0128 | +0.2267 | +0.5660 | 0.231 |
| `combo_tri_mean__sma_distance_60d__rsi21__capital_buy_value` | -1 | +0.0606 | +0.1390 | +0.7844 | 0.0162 | +0.3225 | +0.6264 | 0.497 |
| `combo_clamp_diff__gap_pct__bar_rng_0` | +1 | +0.0205 | +0.1307 | +0.7902 | 0.0230 | +0.1558 | +0.5695 | 0.324 |
| `combo_tri_ifelse__gap_pct__vix__yesterday_lunch_gap__sma_distance_60d__bar_rng_0` | -1 | +0.0461 | +0.1171 | +0.7581 | 0.0394 | +0.1930 | +0.5595 | 0.284 |
| `combo_clamp_diff__northbound_net__bar_vol_0` | +1 | +0.0718 | +0.1166 | +0.7784 | 0.0400 | +0.2025 | +0.5701 | 0.469 |
| `combo_tri_ifelse__gap_pct__vol10__bar_vol_4__yesterday_lunch_gap__growth_momentum_ratio` | -1 | +0.0425 | +0.1149 | +0.7496 | 0.0416 | +0.2914 | +0.5683 | 0.478 |
| `combo_tri_ifelse__gap_pct__vix__mfi14__yesterday_afternoon_momentum__bar_rng_0` | -1 | +0.0928 | +0.1105 | +0.7510 | 0.0490 | +0.2168 | +0.5648 | 0.466 |
| `combo_diff__sma50_dist__bar_vol_4` | -1 | -0.0175 | +0.1093 | +0.7868 | 0.0500 | +0.2382 | +0.5760 | 0.497 |
| `combo_tri_ifelse__gap_pct__vix__yesterday_early_realized_vol__vix_skew_proxy__bar_body_rng_1` | +1 | +0.0368 | +0.1040 | +0.7172 | 0.0582 | +0.3070 | +0.6106 | 0.297 |
| `combo_tri_mean__gap_pct__yesterday_afternoon_reversal__northbound_net` | +1 | +0.0159 | +0.1024 | +0.7570 | 0.0620 | +0.2542 | +0.5947 | 0.436 |
| `combo_max__bar_rng_0__yearly_low_distance` | -1 | -0.0152 | +0.0975 | +0.7348 | 0.0710 | +0.2037 | +0.5648 | 0.491 |
| `combo_tri_ifelse__gap_pct__vol10__capital_net_value__sma50_dist__yesterday_afternoon_momentum` | +1 | -0.0452 | +0.0916 | +0.7466 | 0.0858 | +0.2008 | +0.5900 | 0.428 |

### 500ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__max_up_ret__willr14` | +1 | +0.1032 | +0.3162 | +0.8557 | 0.0000 | +1.2688 | +0.8991 | 0.000 |
| `combo_mean__max_up_ret__gap_pct` | +1 | +0.1875 | +0.2997 | +0.8686 | 0.0000 | +0.7675 | +0.7419 | 0.451 |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | +1 | +0.1477 | +0.2898 | +0.8350 | 0.0000 | +0.6922 | +0.7320 | 0.492 |
| `combo_tri_median__num_up_bars__bar_body_rng_0__body_to_range_ratio` | +1 | +0.1410 | +0.2844 | +0.8379 | 0.0000 | +0.7215 | +0.7349 | 0.441 |
| `combo_tri_median__max_up_ret__bar_vwap_dev_2__bar_body_rng_1` | +1 | +0.1552 | +0.2597 | +0.8101 | 0.0000 | +0.7126 | +0.7490 | 0.478 |
| `combo_diff__yesterday_afternoon_momentum__bar_vol_4` | -1 | +0.0976 | +0.2422 | +0.8169 | 0.0000 | +0.6801 | +0.7173 | 0.048 |
| `combo_diff__max_up_ret__vol20` | +1 | +0.1349 | +0.2294 | +0.8142 | 0.0000 | +0.7270 | +0.7730 | 0.442 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__northbound_volume_share` | +1 | +0.0783 | +0.2133 | +0.7717 | 0.0000 | +0.6191 | +0.7408 | 0.492 |
| `combo_clamp_diff__max_up_ret__first_30min_return` | +1 | +0.0986 | +0.2114 | +0.7688 | 0.0000 | +0.6686 | +0.7384 | 0.458 |
| `combo_ifelse__gap_pct__total_balance__short_balance` | -1 | +0.0383 | +0.2025 | +0.7475 | 0.0000 | +0.5575 | +0.7167 | 0.276 |
| `combo_product__yesterday_illiquidity_amihud__early_range` | +1 | +0.0575 | +0.1970 | +0.7607 | 0.0000 | +0.5070 | +0.7050 | 0.215 |
| `combo_abs_diff__num_up_bars__body_to_range_ratio` | -1 | +0.0978 | +0.1897 | +0.7492 | 0.0000 | +0.6023 | +0.7249 | 0.363 |
| `combo_ifelse__vol20__first_bar_return__yesterday_early_vwap_dev` | +1 | +0.1312 | +0.1804 | +0.7305 | 0.0006 | +0.4867 | +0.7062 | 0.385 |
| `combo_rank_min__body_to_range_ratio__early_range` | +1 | +0.0851 | +0.1799 | +0.7342 | 0.0006 | +0.6120 | +0.7238 | 0.465 |
| `combo_ifelse__gap_pct__total_balance__yesterday_afternoon_momentum` | -1 | +0.0935 | +0.1796 | +0.7280 | 0.0006 | +0.7983 | +0.7795 | 0.462 |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | +1 | +0.1099 | +0.1777 | +0.7220 | 0.0006 | +0.4480 | +0.7032 | 0.445 |
| `combo_ratio__vix_realized_spread__total_balance` | +1 | +0.0427 | +0.1773 | +0.7244 | 0.0006 | +0.6015 | +0.7226 | 0.443 |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | +1 | +0.0689 | +0.1637 | +0.7313 | 0.0032 | +0.5923 | +0.7038 | 0.322 |
| `combo_rank_min__early_range__volatility_percentile_20d` | +1 | +0.0733 | +0.1567 | +0.7102 | 0.0042 | +0.7088 | +0.7343 | 0.472 |
| `combo_ifelse__gap_pct__first_30min_return__yesterday_illiquidity_amihud` | +1 | +0.0595 | +0.1565 | +0.7029 | 0.0042 | +0.5874 | +0.7120 | 0.480 |
| `combo_rank_min__yesterday_illiquidity_amihud__atr14_norm` | +1 | +0.0473 | +0.1528 | +0.6993 | 0.0054 | +0.6421 | +0.7496 | 0.442 |
| `combo_ifelse__gap_pct__max_up_ret__total_balance` | +1 | +0.0893 | +0.1494 | +0.6987 | 0.0060 | +0.7619 | +0.7355 | 0.461 |
| `combo_rank_max__max_down_ret__atr14_norm` | +1 | +0.1030 | +0.1481 | +0.6835 | 0.0066 | +0.9115 | +0.8065 | 0.468 |
| `combo_ratio__bar_body_rng_0__northbound_volume_share` | +1 | +0.1390 | +0.1429 | +0.7084 | 0.0084 | +0.6980 | +0.7249 | 0.035 |
| `combo_diff__bar_vol_5__willr14` | +1 | +0.0514 | +0.1394 | +0.7059 | 0.0096 | +0.7630 | +0.7900 | 0.472 |
| `combo_rank_min__yesterday_lunch_gap__yesterday_afternoon_reversal` | -1 | +0.0812 | +0.1233 | +0.6879 | 0.0204 | +0.5421 | +0.7120 | 0.257 |
| `combo_clamp_diff__max_up_ret__bar_ret_2` | +1 | +0.0875 | +0.1227 | +0.6919 | 0.0216 | +0.5700 | +0.7179 | 0.488 |
| `combo_rank_max__bar_body_rng_0__northbound_volume_share` | +1 | +0.1118 | +0.1222 | +0.6766 | 0.0218 | +0.7997 | +0.8094 | 0.464 |
| `combo_min__yesterday_illiquidity_amihud__vol_ratio_10_60` | +1 | +0.0562 | +0.1115 | +0.6737 | 0.0386 | +0.5708 | +0.7138 | 0.498 |
| `yesterday_lunch_gap` | -1 | +0.0439 | +0.1099 | +0.6782 | 0.0414 | +0.5306 | +0.7056 | 0.293 |
| `combo_ifelse__gap_pct__first_bar_return__margin_balance` | +1 | +0.0498 | +0.0863 | +0.6507 | 0.1014 | +0.6123 | +0.7150 | 0.492 |
| `combo_rank_max__yesterday_day_vwap_dev__macd_hist` | -1 | +0.0293 | +0.0859 | +0.6647 | 0.1036 | +0.7439 | +0.7308 | 0.413 |

### 500ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_abs_diff__willr14__max_up_ret` | +1 | +0.0224 | +0.3177 | +0.8245 | 0.0000 | +0.4204 | +0.6440 | 0.000 |
| `combo_rank_min__yearly_low_distance__max_up_ret` | +1 | +0.0827 | +0.2313 | +0.7106 | 0.0000 | +0.1517 | +0.5642 | 0.178 |
| `combo_min__first_30min_return__bar_body_rng_2` | +1 | +0.0719 | +0.2273 | +0.7213 | 0.0000 | +0.3452 | +0.6129 | 0.256 |
| `combo_diff__willr14__max_up_ret` | -1 | +0.1032 | +0.2179 | +0.7112 | 0.0002 | +0.3440 | +0.5918 | 0.440 |
| `combo_diff__vol60__max_up_ret` | -1 | +0.1496 | +0.2139 | +0.7118 | 0.0006 | +0.2740 | +0.5812 | 0.411 |
| `combo_tri_max__rsi21__stoch_k__yesterday_day_vwap_dev` | -1 | +0.0306 | +0.2073 | +0.7091 | 0.0006 | +0.3387 | +0.6264 | 0.461 |
| `combo_product__body_to_range_ratio__max_up_ret` | +1 | +0.0344 | +0.2011 | +0.6903 | 0.0010 | +0.1870 | +0.5636 | 0.469 |
| `combo_product__limit_up_proximity_day__rsi21` | +1 | +0.0452 | +0.1947 | +0.6901 | 0.0012 | +0.1971 | +0.5877 | 0.272 |
| `combo_product__limit_up_proximity_day__bar_vol_5` | +1 | +0.0267 | +0.1775 | +0.6649 | 0.0024 | +0.3081 | +0.6235 | 0.148 |
| `combo_max__yearly_low_distance__bar_vol_4` | +1 | +0.0526 | +0.1740 | +0.6768 | 0.0032 | +0.3203 | +0.5971 | 0.448 |
| `combo_ifelse__vol60__bar_ret_2__northbound_volume_share` | +1 | +0.0864 | +0.1659 | +0.6545 | 0.0050 | +0.2008 | +0.5554 | 0.390 |
| `combo_product__stoch_k__sma200_dist` | +1 | +0.0252 | +0.1641 | +0.6514 | 0.0064 | +0.2169 | +0.5636 | 0.216 |
| `volume_percentile_20d` | +1 | +0.0193 | +0.1622 | +0.6615 | 0.0076 | +0.4284 | +0.6393 | 0.399 |
| `combo_product__bar_vwap_dev_5__bar_body_rng_2` | +1 | +0.0112 | +0.1539 | +0.6436 | 0.0098 | +0.2729 | +0.6240 | 0.114 |
| `combo_product__bar_vol_4__bar_vol_5` | +1 | -0.0043 | +0.1538 | +0.6490 | 0.0098 | +0.5753 | +0.6710 | 0.433 |
| `combo_product__yesterday_illiquidity_amihud__vol_gk10` | +1 | +0.0230 | +0.1515 | +0.6221 | 0.0100 | +0.1633 | +0.5654 | 0.241 |
| `combo_rank_min__limit_up_proximity_day__max_up_ret` | +1 | +0.0440 | +0.1509 | +0.6316 | 0.0102 | +0.2708 | +0.5683 | 0.421 |
| `combo_product__yesterday_first_bar_volume__sma50_dist` | +1 | +0.0154 | +0.1457 | +0.6230 | 0.0124 | +0.2717 | +0.6076 | 0.348 |
| `combo_abs_diff__sma50_dist__bar_vol_4` | +1 | +0.0256 | +0.1372 | +0.6400 | 0.0186 | +0.5090 | +0.6786 | 0.371 |
| `combo_rank_min__yesterday_illiquidity_amihud__vol_gk10` | +1 | +0.0575 | +0.1309 | +0.6049 | 0.0230 | +0.3015 | +0.5695 | 0.441 |
| `combo_ifelse__vol60__margin_balance__sma100_dist` | -1 | +0.0836 | +0.1224 | +0.6053 | 0.0330 | +0.3444 | +0.5754 | 0.160 |
| `combo_abs_diff__yesterday_first_bar_volume__bar_vol_5` | +1 | +0.0235 | +0.1213 | +0.6211 | 0.0342 | +0.3714 | +0.6493 | 0.242 |
| `combo_abs_diff__bar_vwap_dev_5__max_up_ret` | +1 | +0.0474 | +0.1208 | +0.5983 | 0.0346 | +0.2737 | +0.5906 | 0.348 |
| `combo_mean__stoch_k__max_up_ret` | +1 | +0.1106 | +0.1072 | +0.5958 | 0.0528 | +0.2681 | +0.5730 | 0.457 |
| `combo_tri_min__sma100_dist__stoch_k__vol60` | -1 | +0.0060 | +0.1064 | +0.5921 | 0.0542 | +0.2338 | +0.5701 | 0.493 |
| `combo_clamp_diff__body_to_range_ratio__max_up_ret` | -1 | +0.0548 | +0.1010 | +0.5718 | 0.0638 | +0.1748 | +0.5601 | 0.365 |
| `combo_tri_max__yesterday_illiquidity_amihud__stoch_k__sma200_dist` | +1 | +0.0340 | +0.0942 | +0.5757 | 0.0796 | +0.3296 | +0.5789 | 0.453 |
| `combo_clamp_diff__yesterday_illiquidity_amihud__short_sell_quantity` | +1 | +0.0395 | +0.0837 | +0.5506 | 0.1074 | +0.2149 | +0.5584 | 0.467 |
| `combo_product__volume_percentile_20d__yesterday_wavetrend_osc` | +1 | +0.0628 | +0.0820 | +0.5593 | 0.1124 | +0.3768 | +0.6710 | 0.425 |
| `combo_clamp_diff__first_30min_return__bar_vwap_dev_5` | +1 | +0.1851 | +0.0809 | +0.5631 | 0.1170 | +0.3358 | +0.5765 | 0.362 |
| `combo_diff__yesterday_day_vwap_dev__bar_vol_5` | -1 | +0.0739 | +0.0720 | +0.5793 | 0.1428 | +0.3490 | +0.6340 | 0.402 |

### 500ETF / short

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__macd_hist__vol_pk20__rsi5__yesterday_early_vwap_dev__body_to_range_ratio` | +1 | +0.0398 | +0.2082 | +0.8567 | 0.0004 | +0.3752 | +0.6463 | 0.000 |
| `combo_diff__gap_pct__yesterday_day_vwap_dev` | +1 | +0.0938 | +0.1488 | +0.8092 | 0.0084 | +0.2530 | +0.6041 | 0.116 |
| `combo_abs_diff__macd_hist__early_range` | +1 | +0.0297 | +0.1289 | +0.7667 | 0.0248 | +0.4061 | +0.6516 | 0.068 |

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | +1 | +0.1720 | +0.4122 | +0.8756 | 0.0000 | +1.1922 | +0.8539 | 0.000 |
| `combo_tri_ifelse__vix__vol20__max_up_ret__vol5__bar_body_rng_1` | +1 | +0.0953 | +0.3585 | +0.8205 | 0.0000 | +1.1887 | +0.8490 | 0.329 |
| `combo_tri_ifelse__vix__vol20__bar_vwap_dev_1__vol_gk10__max_down_ret` | +1 | +0.1557 | +0.3468 | +0.8353 | 0.0000 | +0.9362 | +0.8085 | 0.405 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__short_sell_cover_spread__max_down_ret` | +1 | +0.1295 | +0.3375 | +0.7989 | 0.0000 | +1.1612 | +0.8717 | 0.463 |
| `combo_tri_max__max_up_ret__vol5__max_down_ret` | +1 | +0.1505 | +0.3161 | +0.7879 | 0.0000 | +1.2134 | +0.8944 | 0.492 |
| `combo_rank_max__first_bar_return__num_up_bars` | +1 | +0.0947 | +0.3055 | +0.7739 | 0.0000 | +0.9874 | +0.8184 | 0.384 |
| `combo_tri_ifelse__atr14_norm__vol20__short_sell_cover_spread__bar_ret_0__early_momentum` | +1 | +0.0745 | +0.3039 | +0.7711 | 0.0000 | +0.8717 | +0.8213 | 0.284 |
| `combo_rank_max__max_down_ret__bar_rng_3` | +1 | +0.1129 | +0.3023 | +0.7902 | 0.0000 | +1.0578 | +0.8322 | 0.460 |
| `combo_tri_ifelse__vix__vol20__first_30min_return__vol5__first_bar_return` | +1 | +0.0992 | +0.3000 | +0.7381 | 0.0000 | +0.6677 | +0.7364 | 0.490 |
| `combo_tri_ifelse__vix__atr14_norm__short_sell_cover_spread__yesterday_day_realized_vol__max_down_ret` | +1 | +0.1352 | +0.2924 | +0.7726 | 0.0000 | +0.8472 | +0.8253 | 0.499 |
| `combo_min__max_up_ret__early_skew` | +1 | +0.1148 | +0.2878 | +0.8236 | 0.0000 | +0.6133 | +0.7621 | 0.397 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__early_skew` | +1 | +0.0673 | +0.2780 | +0.7541 | 0.0000 | +0.7627 | +0.7937 | 0.488 |
| `combo_tri_ifelse__atr14_norm__vol20__bar_vwap_dev_1__max_up_ret__early_momentum` | +1 | +0.1313 | +0.2754 | +0.7973 | 0.0000 | +0.9831 | +0.8144 | 0.495 |
| `combo_ifelse__gap_pct__vol5__bar_body_rng_1` | +1 | +0.1086 | +0.2579 | +0.7399 | 0.0002 | +0.9017 | +0.7769 | 0.442 |
| `combo_rank_max__max_down_ret__bar_vol_4` | +1 | +0.1097 | +0.2533 | +0.7140 | 0.0002 | +0.8272 | +0.7739 | 0.460 |
| `combo_tri_ifelse__vix__atr14_norm__max_up_ret__vol_gk10__num_up_bars` | +1 | +0.1036 | +0.2504 | +0.7452 | 0.0002 | +0.6855 | +0.7364 | 0.497 |
| `combo_ifelse__vol10__vix_rolling_percentile_60d__bar_body_rng_1` | +1 | +0.0925 | +0.2454 | +0.7232 | 0.0002 | +0.7846 | +0.7868 | 0.467 |
| `combo_ifelse__gap_pct__vix_rolling_percentile_60d__first_bar_return` | +1 | +0.0598 | +0.2378 | +0.7200 | 0.0008 | +0.6266 | +0.7423 | 0.403 |
| `combo_rank_max__vix_diff_1d__max_up_ret` | +1 | +0.1300 | +0.2345 | +0.7237 | 0.0010 | +0.8186 | +0.8144 | 0.479 |
| `combo_ifelse__vol10__short_sell_cover_spread__first_bar_return` | +1 | +0.0730 | +0.2303 | +0.7063 | 0.0014 | +0.7289 | +0.7680 | 0.394 |
| `combo_tri_ifelse__vix__atr14_norm__bar_vwap_dev_1__bar_ret_0__early_momentum` | +1 | +0.1070 | +0.2273 | +0.7671 | 0.0016 | +0.7199 | +0.7404 | 0.482 |
| `combo_tri_median__vix_skew_proxy__vix_rolling_percentile_60d__max_down_ret` | +1 | +0.1209 | +0.2126 | +0.6988 | 0.0026 | +0.6276 | +0.7552 | 0.473 |
| `combo_tri_ifelse__vix__vol20__max_up_ret__bar_body_rng_1__max_down_ret` | +1 | +0.1241 | +0.2102 | +0.6973 | 0.0028 | +0.7220 | +0.7443 | 0.498 |
| `combo_min__max_up_ret__bar_rng_5` | +1 | +0.0838 | +0.2101 | +0.7139 | 0.0028 | +0.7177 | +0.7315 | 0.484 |
| `combo_tri_min__vix_diff_1d__vix__max_down_ret` | +1 | +0.1141 | +0.2093 | +0.6924 | 0.0028 | +0.7890 | +0.7641 | 0.325 |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | +1 | +0.0580 | +0.2078 | +0.7244 | 0.0032 | +0.5389 | +0.7216 | 0.264 |
| `combo_rank_max__yesterday_day_realized_vol__bar_vol_4` | +1 | +0.0644 | +0.2058 | +0.7001 | 0.0034 | +0.6490 | +0.7601 | 0.365 |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | +1 | +0.0461 | +0.2029 | +0.6746 | 0.0038 | +0.9300 | +0.8045 | 0.483 |
| `yesterday_close_position` | -1 | +0.0479 | +0.1959 | +0.7119 | 0.0054 | +0.5536 | +0.7058 | 0.267 |
| `combo_tri_mean__vix_rolling_percentile_60d__atr14_norm__max_down_ret` | +1 | +0.1036 | +0.1894 | +0.6961 | 0.0068 | +0.5463 | +0.7275 | 0.491 |
| `combo_product__yesterday_day_realized_vol__total_path_length` | +1 | +0.0761 | +0.1842 | +0.7161 | 0.0090 | +0.7052 | +0.7315 | 0.445 |
| `combo_clamp_diff__vol_gk10__stoch_d` | +1 | +0.0130 | +0.1761 | +0.6915 | 0.0122 | +0.9358 | +0.7937 | 0.391 |
| `combo_ratio__yesterday_range_ratio__vol5` | -1 | +0.0337 | +0.1759 | +0.7028 | 0.0122 | +0.7956 | +0.7493 | 0.193 |
| `combo_ifelse__vol10__bar_ret_0__bar_body_rng_1` | +1 | +0.0842 | +0.1729 | +0.6358 | 0.0130 | +0.8774 | +0.7828 | 0.467 |
| `combo_product__max_up_ret__vol10` | -1 | +0.0766 | +0.1725 | +0.6738 | 0.0130 | +0.6807 | +0.7404 | 0.420 |
| `combo_rank_max__yesterday_day_range__vol_pk20` | +1 | +0.0214 | +0.1668 | +0.6687 | 0.0174 | +0.3748 | +0.7088 | 0.493 |
| `combo_mean__first_30min_return__gap_pct` | +1 | +0.0920 | +0.1663 | +0.6390 | 0.0176 | +0.7775 | +0.7502 | 0.467 |
| `combo_abs_diff__yesterday_range_ratio__early_range` | +1 | +0.0301 | +0.1544 | +0.6425 | 0.0312 | +0.6860 | +0.7226 | 0.461 |
| `combo_abs_diff__yesterday_day_realized_vol__vol10` | +1 | +0.0125 | +0.1389 | +0.6612 | 0.0576 | +0.4778 | +0.7088 | 0.382 |
| `capital_sell_volume` | +1 | +0.0076 | +0.0728 | +0.5877 | 0.2828 | +0.6306 | +0.7206 | 0.477 |

### 588000ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_max__vol5__bar_rng_3` | +1 | +0.0287 | +0.3428 | +1.2026 | 0.0000 | +0.3000 | +0.5913 | 0.000 |
| `combo_rank_max__bar_vol_4__vol5` | +1 | +0.0663 | +0.2977 | +1.1103 | 0.0002 | +0.2713 | +0.5884 | 0.437 |
| `combo_abs_diff__growth_momentum_ratio__bar_vol_5` | +1 | +0.0387 | +0.2897 | +1.1369 | 0.0002 | +0.3542 | +0.5824 | 0.335 |
| `combo_tri_min__vix_rolling_percentile_60d__yesterday_day_realized_vol__vix_skew_proxy` | +1 | +0.0800 | +0.2884 | +1.1445 | 0.0002 | +0.2922 | +0.6041 | 0.190 |
| `combo_rank_max__bar_vol_4__vix_diff_1d` | +1 | +0.0896 | +0.2574 | +1.0661 | 0.0004 | +0.4110 | +0.6446 | 0.439 |
| `combo_diff__bar_vol_4__sma_distance_60d` | +1 | +0.0407 | +0.2512 | +1.0620 | 0.0008 | +0.2874 | +0.5972 | 0.370 |
| `combo_ifelse__gap_pct__vol5__vix_skew_proxy` | +1 | +0.0611 | +0.2482 | +1.0463 | 0.0008 | +0.2677 | +0.6308 | 0.479 |
| `first_30min_return` | +1 | +0.1243 | +0.2184 | +1.0654 | 0.0036 | +0.2749 | +0.6239 | 0.073 |
| `combo_abs_diff__bar_vol_4__buy_on_margin_value` | +1 | +0.0309 | +0.2172 | +1.0881 | 0.0036 | +0.2475 | +0.6269 | 0.459 |
| `combo_mean__early_range__volume_slope` | +1 | +0.0223 | +0.2126 | +1.0897 | 0.0060 | +0.5676 | +0.6811 | 0.317 |
| `combo_product__yesterday_day_realized_vol__bar_rng_0` | +1 | +0.0852 | +0.2106 | +1.0790 | 0.0070 | +0.2139 | +0.5568 | 0.470 |
| `combo_rank_max__vix_rolling_percentile_60d__max_down_ret` | +1 | +0.1021 | +0.2056 | +1.0164 | 0.0082 | +0.1994 | +0.5972 | 0.454 |
| `combo_product__bar_vol_4__capital_net_value` | +1 | +0.0574 | +0.2024 | +1.0503 | 0.0094 | +0.2881 | +0.5953 | 0.429 |
| `combo_abs_diff__buy_on_margin_value__growth_momentum_ratio` | +1 | +0.0608 | +0.1981 | +1.0341 | 0.0108 | +0.3274 | +0.6130 | 0.382 |
| `combo_rank_min__vol_gk10__bar_rng_0` | +1 | +0.0220 | +0.1862 | +1.0567 | 0.0162 | +0.1837 | +0.6288 | 0.493 |
| `combo_clamp_diff__vix_diff_1d__capital_buy_value` | +1 | +0.0675 | +0.1859 | +1.0305 | 0.0162 | +0.5074 | +0.6831 | 0.421 |
| `combo_rank_max__bar_vol_4__max_down_ret` | +1 | +0.1097 | +0.1832 | +0.9784 | 0.0170 | +0.2870 | +0.6229 | 0.487 |
| `combo_product__capital_net_accel__capital_large_order_ratio` | +1 | +0.0441 | +0.1824 | +1.0360 | 0.0172 | +0.4439 | +0.6515 | 0.470 |
| `combo_rank_max__bar_rng_3__yesterday_volume_ratio` | +1 | +0.0402 | +0.1803 | +1.0699 | 0.0182 | +0.3832 | +0.6318 | 0.481 |
| `combo_tri_max__body_to_range_ratio__early_range__bar_vol_4` | +1 | +0.0350 | +0.1739 | +0.9928 | 0.0224 | +0.2258 | +0.5765 | 0.492 |
| `combo_tri_median__iv_envelope_deviation__vix_diff_1d__gap_pct` | +1 | +0.0880 | +0.1707 | +1.0187 | 0.0242 | +0.1517 | +0.5518 | 0.422 |
| `combo_ratio__vix_skew_proxy__capital_net_value` | +1 | +0.0984 | +0.1674 | +0.9624 | 0.0274 | +0.1847 | +0.5716 | 0.243 |
| `combo_rank_max__bar_rng_3__capital_sell_volume` | +1 | +0.0253 | +0.1594 | +1.0483 | 0.0342 | +0.3826 | +0.6140 | 0.495 |
| `combo_clamp_diff__vix_skew_proxy__gap_pct` | +1 | +0.0789 | +0.1495 | +0.9797 | 0.0438 | +0.3034 | +0.5666 | 0.412 |
| `combo_rank_max__vol5__capital_net_value` | +1 | +0.0027 | +0.1422 | +0.9760 | 0.0524 | +0.2898 | +0.5568 | 0.373 |
| `combo_abs_diff__early_range__buy_on_margin_value` | +1 | +0.0215 | +0.1315 | +1.0102 | 0.0706 | +0.2684 | +0.5716 | 0.415 |
| `combo_tri_min__vol5__yesterday_day_realized_vol__gap_pct` | +1 | +0.0072 | +0.1314 | +0.9644 | 0.0706 | +0.1825 | +0.5844 | 0.475 |
| `combo_mean__vix_skew_proxy__yesterday_pm_am_vol_ratio` | +1 | +0.0753 | +0.1224 | +0.9642 | 0.0864 | +0.2105 | +0.5775 | 0.498 |
| `combo_clamp_diff__bar_vol_5__yesterday_day_close_pos` | +1 | +0.0745 | +0.1219 | +0.9484 | 0.0872 | +0.2654 | +0.5775 | 0.300 |
| `combo_max__vix_rolling_percentile_60d__capital_sell_volume` | +1 | +0.0045 | +0.1184 | +0.9750 | 0.0936 | +0.2974 | +0.5785 | 0.494 |
| `combo_rank_max__bar_vol_5__capital_buy_value` | +1 | +0.0306 | +0.1161 | +0.9688 | 0.0998 | +0.2322 | +0.5884 | 0.497 |
| `combo_rank_max__vix_rolling_percentile_60d__vol_ratio_10_60` | +1 | +0.0111 | +0.1133 | +0.9723 | 0.1062 | +0.1685 | +0.5755 | 0.402 |
| `combo_abs_diff__yesterday_day_realized_vol__yesterday_volume_ratio` | +1 | +0.0409 | +0.1057 | +0.9421 | 0.1240 | +0.3815 | +0.6397 | 0.410 |
| `combo_abs_diff__total_path_length__vol_ratio_10_60` | +1 | +0.0083 | +0.1002 | +0.9462 | 0.1352 | +0.2733 | +0.6101 | 0.468 |
| `combo_abs_diff__early_realized_vol__growth_momentum_ratio` | +1 | +0.0446 | +0.0982 | +0.9565 | 0.1394 | +0.2209 | +0.5864 | 0.433 |
| `combo_rank_max__early_range__short_balance` | +1 | +0.0029 | +0.0954 | +0.9584 | 0.1476 | +0.2834 | +0.5805 | 0.481 |
| `combo_tri_min__sma_distance_60d__bar_vol_5__yesterday_day_close_pos` | -1 | +0.0424 | +0.0852 | +0.9229 | 0.1820 | +0.5144 | +0.7137 | 0.355 |

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__margin_buy_repayment_spread` | +1 | +0.1437 | +0.2707 | +0.6731 | 0.0000 | +0.6130 | +0.7056 | 0.000 |
| `combo_tri_mean__max_up_ret__early_range__gap_pct` | +1 | +0.1414 | +0.2636 | +0.6755 | 0.0000 | +0.6828 | +0.7079 | 0.457 |
| `combo_diff__max_up_ret__bar_body_rng_1` | +1 | +0.0933 | +0.2322 | +0.6521 | 0.0000 | +0.6740 | +0.7513 | 0.492 |
| `combo_tri_mean__yesterday_afternoon_momentum__yesterday_afternoon_reversal__yesterday_day_vwap_dev` | -1 | +0.1008 | +0.2284 | +0.6567 | 0.0000 | +0.5142 | +0.7050 | 0.139 |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_early_vwap_dev__max_down_ret` | +1 | +0.1393 | +0.2202 | +0.6356 | 0.0000 | +0.4895 | +0.7067 | 0.452 |
| `combo_abs_diff__early_range__bar_rng_5` | +1 | +0.0451 | +0.1975 | +0.6207 | 0.0002 | +0.6266 | +0.7343 | 0.459 |
| `combo_tri_max__yesterday_first_30min_return__yesterday_early_trend__gap_pct` | +1 | +0.0973 | +0.1953 | +0.6082 | 0.0002 | +0.5302 | +0.7021 | 0.398 |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_early_vwap_dev__early_range` | +1 | +0.1273 | +0.1891 | +0.6064 | 0.0004 | +0.6850 | +0.7296 | 0.450 |
| `combo_clamp_diff__yesterday_day_vwap_dev__limit_up_proximity_day` | -1 | +0.0692 | +0.1746 | +0.6202 | 0.0014 | +0.3740 | +0.7079 | 0.483 |
| `combo_rank_max__max_up_ret__bb_width` | +1 | +0.0712 | +0.1711 | +0.5963 | 0.0014 | +0.4742 | +0.7249 | 0.371 |
| `combo_rank_max__willr14__roc10` | -1 | +0.0005 | +0.1677 | +0.5895 | 0.0014 | +1.3226 | +0.8985 | 0.194 |
| `combo_tri_ifelse__gap_pct__bb_width__first_bar_return__early_range__keltner_squeeze_width` | +1 | +0.1302 | +0.1615 | +0.5701 | 0.0022 | +0.4362 | +0.7173 | 0.440 |
| `combo_tri_ifelse__gap_pct__bb_width__yesterday_afternoon_momentum__keltner_squeeze_width__stoch_k` | -1 | +0.0733 | +0.1519 | +0.5805 | 0.0038 | +0.6174 | +0.7150 | 0.444 |
| `combo_diff__bar_vol_4__limit_up_proximity_day` | +1 | +0.0598 | +0.1506 | +0.6039 | 0.0040 | +0.6619 | +0.7202 | 0.347 |
| `combo_ratio__yesterday_day_vwap_dev__bar_vol_4` | -1 | +0.0864 | +0.1434 | +0.5954 | 0.0060 | +0.5127 | +0.7032 | 0.238 |
| `combo_product__willr14__roc10` | +1 | +0.0465 | +0.1339 | +0.5643 | 0.0106 | +0.8185 | +0.7695 | 0.353 |
| `combo_diff__coppock_curve_day__roc10` | +1 | +0.0511 | +0.1311 | +0.5599 | 0.0128 | +0.8634 | +0.8399 | 0.308 |
| `combo_tri_ifelse__gap_pct__bb_width__yearly_high_distance__margin_buy_repayment_spread__stoch_k` | -1 | -0.0221 | +0.1248 | +0.5622 | 0.0166 | +0.7150 | +0.7249 | 0.321 |
| `combo_tri_max__early_range__keltner_squeeze_width__bb_width` | +1 | +0.0029 | +0.1148 | +0.5517 | 0.0286 | +0.5081 | +0.7443 | 0.491 |
| `combo_clamp_diff__bar_vol_4__roc10` | +1 | +0.0420 | +0.1027 | +0.5566 | 0.0508 | +0.5869 | +0.7267 | 0.490 |
| `combo_rank_min__keltner_squeeze_width__sma100_dist` | -1 | +0.0488 | +0.0902 | +0.5234 | 0.0852 | +0.5799 | +0.7050 | 0.344 |
| `combo_diff__yesterday_afternoon_momentum__yesterday_afternoon_reversal` | -1 | +0.0525 | +0.0841 | +0.5131 | 0.1082 | +0.6090 | +0.7578 | 0.425 |

### 159915ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rank_max__yesterday_afternoon_momentum__roc10` | -1 | +0.0411 | +0.1964 | +0.6186 | 0.0008 | +0.3616 | +0.6152 | 0.000 |
| `combo_min__early_realized_vol__max_down_ret` | +1 | +0.0642 | +0.1745 | +0.5740 | 0.0018 | +0.1596 | +0.5613 | 0.077 |
| `combo_product__bar_rng_0__yearly_high_distance` | -1 | +0.0541 | +0.1512 | +0.5958 | 0.0088 | +0.1649 | +0.5754 | 0.160 |
| `combo_diff__early_trend__max_down_ret` | -1 | +0.0485 | +0.1042 | +0.5050 | 0.0534 | +0.2646 | +0.6147 | 0.369 |
| `combo_min__yesterday_afternoon_momentum__early_realized_vol` | -1 | +0.0572 | +0.0867 | +0.5024 | 0.0910 | +0.3583 | +0.6240 | 0.471 |
| `combo_rank_min__bar_body_rng_1__max_down_ret` | +1 | +0.0549 | +0.0784 | +0.4800 | 0.1166 | +0.2540 | +0.5795 | 0.368 |

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
| `combo_ifelse__macd_hist__max_up_ret__option_oi_growth` | `ifelse` | a=`max_up_ret`, b=`option_oi_growth`, cond=`macd_hist` |
| `combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio` | `ifelse` | a=`first_bar_return`, b=`growth_momentum_ratio`, cond=`gap_pct` |
| `combo_ifelse__macd_hist__bar_ret_0__bar_body_rng_0` | `ifelse` | a=`bar_ret_0`, b=`bar_body_rng_0`, cond=`macd_hist` |
| `combo_ifelse__macd_hist__bar_body_rng_0__short_sell_cover_spread` | `ifelse` | a=`bar_body_rng_0`, b=`short_sell_cover_spread`, cond=`macd_hist` |
| `combo_max__max_up_ret__yesterday_gap_pct` | `max` | a=`max_up_ret`, b=`yesterday_gap_pct` |
| `combo_ifelse__macd_hist__max_up_ret__growth_momentum_ratio` | `ifelse` | a=`max_up_ret`, b=`growth_momentum_ratio`, cond=`macd_hist` |
| `combo_clamp_diff__max_up_ret__willr14` | `clamp_diff` | a=`max_up_ret`, b=`willr14` |
| `combo_ifelse__macd_hist__first_bar_return__yesterday_northbound_net_ratio` | `ifelse` | a=`first_bar_return`, b=`yesterday_northbound_net_ratio`, cond=`macd_hist` |
| `combo_rank_max__early_range__margin_extreme_rank_252d` | `rank_max` | a=`early_range`, b=`margin_extreme_rank_252d` |
| `combo_diff__short_sell_quantity__roc60` | `diff` | a=`short_sell_quantity`, b=`roc60` |
| `combo_rank_min__yesterday_day_skew__sma100_dist` | `rank_min` | a=`yesterday_day_skew`, b=`sma100_dist` |
| `combo_rank_min__roc60__twenty_gap_bars_regime` | `rank_min` | a=`roc60`, b=`twenty_gap_bars_regime` |
| `combo_rank_max__first_30min_return__bar_vwap_dev_2` | `rank_max` | a=`first_30min_return`, b=`bar_vwap_dev_2` |
| `combo_product__short_sell_quantity__wavetrend_osc_day` | `product` | a=`short_sell_quantity`, b=`wavetrend_osc_day` |
| `combo_abs_diff__short_sell_quantity__early_range` | `abs_diff` | a=`short_sell_quantity`, b=`early_range` |
| `combo_diff__max_up_ret__total_balance` | `diff` | a=`max_up_ret`, b=`total_balance` |
| `combo_rank_min__early_range__twenty_gap_bars_regime` | `rank_min` | a=`early_range`, b=`twenty_gap_bars_regime` |
| `combo_tri_min__gap_pct__total_path_length__atr14_norm` | `tri_min` | a=`gap_pct`, b=`total_path_length`, c=`atr14_norm` |
| `combo_abs_diff__bar_vol_4__volume_sma_ratio` | `abs_diff` | a=`bar_vol_4`, b=`volume_sma_ratio` |
| `combo_tri_ifelse__gap_pct__atr14_norm__total_balance__yesterday_day_skew__margin_balance` | `tri_ifelse` | a=`total_balance`, b=`yesterday_day_skew`, c=`margin_balance`, cond=`gap_pct`, cond2=`atr14_norm` |
| `combo_ifelse__sma20_dist__total_balance__short_sell_cover_spread` | `ifelse` | a=`total_balance`, b=`short_sell_cover_spread`, cond=`sma20_dist` |
| `combo_rank_min__short_sell_cover_spread__yesterday_gap` | `rank_min` | a=`short_sell_cover_spread`, b=`yesterday_gap` |
| `combo_diff__max_down_ret__sma20_dist` | `diff` | a=`max_down_ret`, b=`sma20_dist` |
| `combo_max__gap_pct__first_bar_return` | `max` | a=`gap_pct`, b=`first_bar_return` |
| `combo_tri_ifelse__gap_pct__atr14_norm__northbound_net__yesterday_day_skew__mfi14` | `tri_ifelse` | a=`northbound_net`, b=`yesterday_day_skew`, c=`mfi14`, cond=`gap_pct`, cond2=`atr14_norm` |
| `combo_tri_mean__iv_corridor_width__capital_buy_value__rsi21` | `tri_mean` | a=`iv_corridor_width`, b=`capital_buy_value`, c=`rsi21` |
| `combo_tri_median__bar_vol_4__bar_vol_0__wavetrend_osc_day` | `tri_median` | a=`bar_vol_4`, b=`bar_vol_0`, c=`wavetrend_osc_day` |
| `combo_ifelse__macd_hist__yesterday_body_ratio__sma100_dist` | `ifelse` | a=`yesterday_body_ratio`, b=`sma100_dist`, cond=`macd_hist` |
| `combo_ifelse__macd_hist__yesterday_lunch_gap__capital_buy_volume` | `ifelse` | a=`yesterday_lunch_gap`, b=`capital_buy_volume`, cond=`macd_hist` |
| `combo_min__iv_corridor_width__margin_net_buy` | `min` | a=`iv_corridor_width`, b=`margin_net_buy` |
| `combo_ifelse__gap_pct__capital_buy_value__bar_vol_0` | `ifelse` | a=`capital_buy_value`, b=`bar_vol_0`, cond=`gap_pct` |
| `combo_tri_min__bar_vol_4__sma100_dist__yearly_low_distance` | `tri_min` | a=`bar_vol_4`, b=`sma100_dist`, c=`yearly_low_distance` |
| `combo_clamp_diff__willr14__yesterday_stoch_rsi_cross` | `clamp_diff` | a=`willr14`, b=`yesterday_stoch_rsi_cross` |
| `combo_ifelse__macd_hist__yesterday_lunch_gap__sma_distance_60d` | `ifelse` | a=`yesterday_lunch_gap`, b=`sma_distance_60d`, cond=`macd_hist` |
| `combo_diff__sma100_dist__short_balance_quantity` | `diff` | a=`sma100_dist`, b=`short_balance_quantity` |
| `combo_product__roc60__capital_sell_value` | `product` | a=`roc60`, b=`capital_sell_value` |
| `combo_ifelse__macd_hist__margin_extreme_rank_252d__sma100_dist` | `ifelse` | a=`margin_extreme_rank_252d`, b=`sma100_dist`, cond=`macd_hist` |
| `combo_product__bar_vol_4__coppock_curve_day` | `product` | a=`bar_vol_4`, b=`coppock_curve_day` |
| `combo_diff__roc10__yearly_low_distance` | `diff` | a=`roc10`, b=`yearly_low_distance` |
| `combo_max__short_balance_quantity__sma20_dist` | `max` | a=`short_balance_quantity`, b=`sma20_dist` |
| `combo_rank_min__roc60__margin_buy_repayment_spread` | `rank_min` | a=`roc60`, b=`margin_buy_repayment_spread` |
| `combo_min__willr14__sma10_dist` | `min` | a=`willr14`, b=`sma10_dist` |
| `combo_mean__roc10__bar_rng_5` | `mean` | a=`roc10`, b=`bar_rng_5` |
| `combo_ifelse__macd_hist__iv_corridor_width__margin_extreme_rank_252d` | `ifelse` | a=`iv_corridor_width`, b=`margin_extreme_rank_252d`, cond=`macd_hist` |
| `combo_ratio__yesterday_body_ratio__bar_vol_5` | `ratio` | a=`yesterday_body_ratio`, b=`bar_vol_5` |
| `combo_rank_max__roc10__margin_buy_repayment_spread` | `rank_max` | a=`roc10`, b=`margin_buy_repayment_spread` |
| `combo_ratio__roc20__bar_vol_4` | `ratio` | a=`roc20`, b=`bar_vol_4` |
| `combo_ifelse__sma20_dist__iv_corridor_width__yesterday_body_ratio` | `ifelse` | a=`iv_corridor_width`, b=`yesterday_body_ratio`, cond=`sma20_dist` |
| `combo_mean__sma200_dist__vix_rolling_percentile_60d` | `mean` | a=`sma200_dist`, b=`vix_rolling_percentile_60d` |
| `combo_clamp_diff__sma_distance_60d__sma200_dist` | `clamp_diff` | a=`sma_distance_60d`, b=`sma200_dist` |
| `combo_tri_median__tech_value_rotation__rsi21__iv_corridor_width` | `tri_median` | a=`tech_value_rotation`, b=`rsi21`, c=`iv_corridor_width` |
| `combo_tri_min__margin_net_buy__tech_value_rotation__sma100_dist` | `tri_min` | a=`margin_net_buy`, b=`tech_value_rotation`, c=`sma100_dist` |
| `combo_product__yesterday_day_realized_vol__iv_corridor_width` | `product` | a=`yesterday_day_realized_vol`, b=`iv_corridor_width` |
| `combo_rank_max__margin_net_buy__iv_corridor_width` | `rank_max` | a=`margin_net_buy`, b=`iv_corridor_width` |
| `combo_rank_min__sma_distance_60d__total_balance` | `rank_min` | a=`sma_distance_60d`, b=`total_balance` |
| `combo_tri_min__yearly_low_distance__roc10__bar_vol_4` | `tri_min` | a=`yearly_low_distance`, b=`roc10`, c=`bar_vol_4` |
| `combo_mean__max_down_ret__num_up_bars` | `mean` | a=`max_down_ret`, b=`num_up_bars` |
| `combo_clamp_diff__capital_buy_value__yesterday_day_realized_vol` | `clamp_diff` | a=`capital_buy_value`, b=`yesterday_day_realized_vol` |
| `combo_ifelse__vol60__yesterday_wavetrend_osc__yesterday_lunch_gap` | `ifelse` | a=`yesterday_wavetrend_osc`, b=`yesterday_lunch_gap`, cond=`vol60` |
| `combo_ratio__yearly_low_distance__yesterday_day_realized_vol` | `ratio` | a=`yearly_low_distance`, b=`yesterday_day_realized_vol` |
| `combo_tri_mean__yesterday_wavetrend_osc__max_down_ret__yesterday_early_range` | `tri_mean` | a=`yesterday_wavetrend_osc`, b=`max_down_ret`, c=`yesterday_early_range` |
| `combo_min__roc5__yesterday_day_realized_vol` | `min` | a=`roc5`, b=`yesterday_day_realized_vol` |
| `combo_abs_diff__max_up_ret__num_up_bars` | `abs_diff` | a=`max_up_ret`, b=`num_up_bars` |
| `combo_abs_diff__yesterday_early_trend__limit_up_proximity_day` | `abs_diff` | a=`yesterday_early_trend`, b=`limit_up_proximity_day` |
| `combo_rank_min__margin_net_buy__margin_repayment` | `rank_min` | a=`margin_net_buy`, b=`margin_repayment` |
| `combo_tri_mean__margin_net_buy__early_range__roc10` | `tri_mean` | a=`margin_net_buy`, b=`early_range`, c=`roc10` |
| `combo_min__yearly_low_distance__capital_buy_volume` | `min` | a=`yearly_low_distance`, b=`capital_buy_volume` |
| `combo_product__tech_value_rotation__yesterday_day_realized_vol` | `product` | a=`tech_value_rotation`, b=`yesterday_day_realized_vol` |
| `combo_product__gap_pct__bar_rng_0` | `product` | a=`gap_pct`, b=`bar_rng_0` |
| `combo_tri_median__bar_vol_4__rsi21__bar_vol_0` | `tri_median` | a=`bar_vol_4`, b=`rsi21`, c=`bar_vol_0` |
| `combo_tri_mean__gap_pct__vol10__iv_vol_ratio` | `tri_mean` | a=`gap_pct`, b=`vol10`, c=`iv_vol_ratio` |
| `combo_tri_ifelse__gap_pct__vol10__mfi14__bar_rng_0__bar_vol_5` | `tri_ifelse` | a=`mfi14`, b=`bar_rng_0`, c=`bar_vol_5`, cond=`gap_pct`, cond2=`vol10` |
| `combo_diff__rsi21__yearly_low_distance` | `diff` | a=`rsi21`, b=`yearly_low_distance` |
| `combo_tri_ifelse__gap_pct__vix__sma50_dist__bar_body_rng_1__bar_rng_0` | `tri_ifelse` | a=`sma50_dist`, b=`bar_body_rng_1`, c=`bar_rng_0`, cond=`gap_pct`, cond2=`vix` |
| `combo_tri_ifelse__gap_pct__vol10__northbound_net__max_up_ret__bar_vol_5` | `tri_ifelse` | a=`northbound_net`, b=`max_up_ret`, c=`bar_vol_5`, cond=`gap_pct`, cond2=`vol10` |
| `combo_tri_ifelse__vol10__vix__yesterday_lunch_gap__bar_vol_5__rsi21` | `tri_ifelse` | a=`yesterday_lunch_gap`, b=`bar_vol_5`, c=`rsi21`, cond=`vol10`, cond2=`vix` |
| `combo_tri_mean__sma_distance_60d__rsi21__capital_buy_value` | `tri_mean` | a=`sma_distance_60d`, b=`rsi21`, c=`capital_buy_value` |
| `combo_clamp_diff__gap_pct__bar_rng_0` | `clamp_diff` | a=`gap_pct`, b=`bar_rng_0` |
| `combo_tri_ifelse__gap_pct__vix__yesterday_lunch_gap__sma_distance_60d__bar_rng_0` | `tri_ifelse` | a=`yesterday_lunch_gap`, b=`sma_distance_60d`, c=`bar_rng_0`, cond=`gap_pct`, cond2=`vix` |
| `combo_clamp_diff__northbound_net__bar_vol_0` | `clamp_diff` | a=`northbound_net`, b=`bar_vol_0` |
| `combo_tri_ifelse__gap_pct__vol10__bar_vol_4__yesterday_lunch_gap__growth_momentum_ratio` | `tri_ifelse` | a=`bar_vol_4`, b=`yesterday_lunch_gap`, c=`growth_momentum_ratio`, cond=`gap_pct`, cond2=`vol10` |
| `combo_tri_ifelse__gap_pct__vix__mfi14__yesterday_afternoon_momentum__bar_rng_0` | `tri_ifelse` | a=`mfi14`, b=`yesterday_afternoon_momentum`, c=`bar_rng_0`, cond=`gap_pct`, cond2=`vix` |
| `combo_diff__sma50_dist__bar_vol_4` | `diff` | a=`sma50_dist`, b=`bar_vol_4` |
| `combo_tri_ifelse__gap_pct__vix__yesterday_early_realized_vol__vix_skew_proxy__bar_body_rng_1` | `tri_ifelse` | a=`yesterday_early_realized_vol`, b=`vix_skew_proxy`, c=`bar_body_rng_1`, cond=`gap_pct`, cond2=`vix` |
| `combo_tri_mean__gap_pct__yesterday_afternoon_reversal__northbound_net` | `tri_mean` | a=`gap_pct`, b=`yesterday_afternoon_reversal`, c=`northbound_net` |
| `combo_max__bar_rng_0__yearly_low_distance` | `max` | a=`bar_rng_0`, b=`yearly_low_distance` |
| `combo_tri_ifelse__gap_pct__vol10__capital_net_value__sma50_dist__yesterday_afternoon_momentum` | `tri_ifelse` | a=`capital_net_value`, b=`sma50_dist`, c=`yesterday_afternoon_momentum`, cond=`gap_pct`, cond2=`vol10` |
| `combo_diff__max_up_ret__willr14` | `diff` | a=`max_up_ret`, b=`willr14` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_tri_median__num_up_bars__bar_body_rng_0__body_to_range_ratio` | `tri_median` | a=`num_up_bars`, b=`bar_body_rng_0`, c=`body_to_range_ratio` |
| `combo_tri_median__max_up_ret__bar_vwap_dev_2__bar_body_rng_1` | `tri_median` | a=`max_up_ret`, b=`bar_vwap_dev_2`, c=`bar_body_rng_1` |
| `combo_diff__yesterday_afternoon_momentum__bar_vol_4` | `diff` | a=`yesterday_afternoon_momentum`, b=`bar_vol_4` |
| `combo_diff__max_up_ret__vol20` | `diff` | a=`max_up_ret`, b=`vol20` |
| `combo_tri_min__max_up_ret__bar_body_rng_0__northbound_volume_share` | `tri_min` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`northbound_volume_share` |
| `combo_clamp_diff__max_up_ret__first_30min_return` | `clamp_diff` | a=`max_up_ret`, b=`first_30min_return` |
| `combo_ifelse__gap_pct__total_balance__short_balance` | `ifelse` | a=`total_balance`, b=`short_balance`, cond=`gap_pct` |
| `combo_product__yesterday_illiquidity_amihud__early_range` | `product` | a=`yesterday_illiquidity_amihud`, b=`early_range` |
| `combo_abs_diff__num_up_bars__body_to_range_ratio` | `abs_diff` | a=`num_up_bars`, b=`body_to_range_ratio` |
| `combo_ifelse__vol20__first_bar_return__yesterday_early_vwap_dev` | `ifelse` | a=`first_bar_return`, b=`yesterday_early_vwap_dev`, cond=`vol20` |
| `combo_rank_min__body_to_range_ratio__early_range` | `rank_min` | a=`body_to_range_ratio`, b=`early_range` |
| `combo_ifelse__gap_pct__total_balance__yesterday_afternoon_momentum` | `ifelse` | a=`total_balance`, b=`yesterday_afternoon_momentum`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | `ifelse` | a=`bar_ret_0`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_ratio__vix_realized_spread__total_balance` | `ratio` | a=`vix_realized_spread`, b=`total_balance` |
| `combo_clamp_diff__yesterday_early_vwap_dev__yesterday_day_skew` | `clamp_diff` | a=`yesterday_early_vwap_dev`, b=`yesterday_day_skew` |
| `combo_rank_min__early_range__volatility_percentile_20d` | `rank_min` | a=`early_range`, b=`volatility_percentile_20d` |
| `combo_ifelse__gap_pct__first_30min_return__yesterday_illiquidity_amihud` | `ifelse` | a=`first_30min_return`, b=`yesterday_illiquidity_amihud`, cond=`gap_pct` |
| `combo_rank_min__yesterday_illiquidity_amihud__atr14_norm` | `rank_min` | a=`yesterday_illiquidity_amihud`, b=`atr14_norm` |
| `combo_ifelse__gap_pct__max_up_ret__total_balance` | `ifelse` | a=`max_up_ret`, b=`total_balance`, cond=`gap_pct` |
| `combo_rank_max__max_down_ret__atr14_norm` | `rank_max` | a=`max_down_ret`, b=`atr14_norm` |
| `combo_ratio__bar_body_rng_0__northbound_volume_share` | `ratio` | a=`bar_body_rng_0`, b=`northbound_volume_share` |
| `combo_diff__bar_vol_5__willr14` | `diff` | a=`bar_vol_5`, b=`willr14` |
| `combo_rank_min__yesterday_lunch_gap__yesterday_afternoon_reversal` | `rank_min` | a=`yesterday_lunch_gap`, b=`yesterday_afternoon_reversal` |
| `combo_clamp_diff__max_up_ret__bar_ret_2` | `clamp_diff` | a=`max_up_ret`, b=`bar_ret_2` |
| `combo_rank_max__bar_body_rng_0__northbound_volume_share` | `rank_max` | a=`bar_body_rng_0`, b=`northbound_volume_share` |
| `combo_min__yesterday_illiquidity_amihud__vol_ratio_10_60` | `min` | a=`yesterday_illiquidity_amihud`, b=`vol_ratio_10_60` |
| `combo_ifelse__gap_pct__first_bar_return__margin_balance` | `ifelse` | a=`first_bar_return`, b=`margin_balance`, cond=`gap_pct` |
| `combo_rank_max__yesterday_day_vwap_dev__macd_hist` | `rank_max` | a=`yesterday_day_vwap_dev`, b=`macd_hist` |
| `combo_abs_diff__willr14__max_up_ret` | `abs_diff` | a=`willr14`, b=`max_up_ret` |
| `combo_rank_min__yearly_low_distance__max_up_ret` | `rank_min` | a=`yearly_low_distance`, b=`max_up_ret` |
| `combo_min__first_30min_return__bar_body_rng_2` | `min` | a=`first_30min_return`, b=`bar_body_rng_2` |
| `combo_diff__willr14__max_up_ret` | `diff` | a=`willr14`, b=`max_up_ret` |
| `combo_diff__vol60__max_up_ret` | `diff` | a=`vol60`, b=`max_up_ret` |
| `combo_tri_max__rsi21__stoch_k__yesterday_day_vwap_dev` | `tri_max` | a=`rsi21`, b=`stoch_k`, c=`yesterday_day_vwap_dev` |
| `combo_product__body_to_range_ratio__max_up_ret` | `product` | a=`body_to_range_ratio`, b=`max_up_ret` |
| `combo_product__limit_up_proximity_day__rsi21` | `product` | a=`limit_up_proximity_day`, b=`rsi21` |
| `combo_product__limit_up_proximity_day__bar_vol_5` | `product` | a=`limit_up_proximity_day`, b=`bar_vol_5` |
| `combo_max__yearly_low_distance__bar_vol_4` | `max` | a=`yearly_low_distance`, b=`bar_vol_4` |
| `combo_ifelse__vol60__bar_ret_2__northbound_volume_share` | `ifelse` | a=`bar_ret_2`, b=`northbound_volume_share`, cond=`vol60` |
| `combo_product__stoch_k__sma200_dist` | `product` | a=`stoch_k`, b=`sma200_dist` |
| `combo_product__bar_vwap_dev_5__bar_body_rng_2` | `product` | a=`bar_vwap_dev_5`, b=`bar_body_rng_2` |
| `combo_product__bar_vol_4__bar_vol_5` | `product` | a=`bar_vol_4`, b=`bar_vol_5` |
| `combo_product__yesterday_illiquidity_amihud__vol_gk10` | `product` | a=`yesterday_illiquidity_amihud`, b=`vol_gk10` |
| `combo_rank_min__limit_up_proximity_day__max_up_ret` | `rank_min` | a=`limit_up_proximity_day`, b=`max_up_ret` |
| `combo_product__yesterday_first_bar_volume__sma50_dist` | `product` | a=`yesterday_first_bar_volume`, b=`sma50_dist` |
| `combo_abs_diff__sma50_dist__bar_vol_4` | `abs_diff` | a=`sma50_dist`, b=`bar_vol_4` |
| `combo_rank_min__yesterday_illiquidity_amihud__vol_gk10` | `rank_min` | a=`yesterday_illiquidity_amihud`, b=`vol_gk10` |
| `combo_ifelse__vol60__margin_balance__sma100_dist` | `ifelse` | a=`margin_balance`, b=`sma100_dist`, cond=`vol60` |
| `combo_abs_diff__yesterday_first_bar_volume__bar_vol_5` | `abs_diff` | a=`yesterday_first_bar_volume`, b=`bar_vol_5` |
| `combo_abs_diff__bar_vwap_dev_5__max_up_ret` | `abs_diff` | a=`bar_vwap_dev_5`, b=`max_up_ret` |
| `combo_mean__stoch_k__max_up_ret` | `mean` | a=`stoch_k`, b=`max_up_ret` |
| `combo_tri_min__sma100_dist__stoch_k__vol60` | `tri_min` | a=`sma100_dist`, b=`stoch_k`, c=`vol60` |
| `combo_clamp_diff__body_to_range_ratio__max_up_ret` | `clamp_diff` | a=`body_to_range_ratio`, b=`max_up_ret` |
| `combo_tri_max__yesterday_illiquidity_amihud__stoch_k__sma200_dist` | `tri_max` | a=`yesterday_illiquidity_amihud`, b=`stoch_k`, c=`sma200_dist` |
| `combo_clamp_diff__yesterday_illiquidity_amihud__short_sell_quantity` | `clamp_diff` | a=`yesterday_illiquidity_amihud`, b=`short_sell_quantity` |
| `combo_product__volume_percentile_20d__yesterday_wavetrend_osc` | `product` | a=`volume_percentile_20d`, b=`yesterday_wavetrend_osc` |
| `combo_clamp_diff__first_30min_return__bar_vwap_dev_5` | `clamp_diff` | a=`first_30min_return`, b=`bar_vwap_dev_5` |
| `combo_diff__yesterday_day_vwap_dev__bar_vol_5` | `diff` | a=`yesterday_day_vwap_dev`, b=`bar_vol_5` |
| `combo_tri_ifelse__macd_hist__vol_pk20__rsi5__yesterday_early_vwap_dev__body_to_range_ratio` | `tri_ifelse` | a=`rsi5`, b=`yesterday_early_vwap_dev`, c=`body_to_range_ratio`, cond=`macd_hist`, cond2=`vol_pk20` |
| `combo_diff__gap_pct__yesterday_day_vwap_dev` | `diff` | a=`gap_pct`, b=`yesterday_day_vwap_dev` |
| `combo_abs_diff__macd_hist__early_range` | `abs_diff` | a=`macd_hist`, b=`early_range` |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | `tri_ifelse` | a=`vix_skew_proxy`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__max_up_ret__vol5__bar_body_rng_1` | `tri_ifelse` | a=`max_up_ret`, b=`vol5`, c=`bar_body_rng_1`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__bar_vwap_dev_1__vol_gk10__max_down_ret` | `tri_ifelse` | a=`bar_vwap_dev_1`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__short_sell_cover_spread__max_down_ret` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`short_sell_cover_spread`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_max__max_up_ret__vol5__max_down_ret` | `tri_max` | a=`max_up_ret`, b=`vol5`, c=`max_down_ret` |
| `combo_rank_max__first_bar_return__num_up_bars` | `rank_max` | a=`first_bar_return`, b=`num_up_bars` |
| `combo_tri_ifelse__atr14_norm__vol20__short_sell_cover_spread__bar_ret_0__early_momentum` | `tri_ifelse` | a=`short_sell_cover_spread`, b=`bar_ret_0`, c=`early_momentum`, cond=`atr14_norm`, cond2=`vol20` |
| `combo_rank_max__max_down_ret__bar_rng_3` | `rank_max` | a=`max_down_ret`, b=`bar_rng_3` |
| `combo_tri_ifelse__vix__vol20__first_30min_return__vol5__first_bar_return` | `tri_ifelse` | a=`first_30min_return`, b=`vol5`, c=`first_bar_return`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__atr14_norm__short_sell_cover_spread__yesterday_day_realized_vol__max_down_ret` | `tri_ifelse` | a=`short_sell_cover_spread`, b=`yesterday_day_realized_vol`, c=`max_down_ret`, cond=`vix`, cond2=`atr14_norm` |
| `combo_min__max_up_ret__early_skew` | `min` | a=`max_up_ret`, b=`early_skew` |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__early_skew` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol5`, c=`early_skew`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__atr14_norm__vol20__bar_vwap_dev_1__max_up_ret__early_momentum` | `tri_ifelse` | a=`bar_vwap_dev_1`, b=`max_up_ret`, c=`early_momentum`, cond=`atr14_norm`, cond2=`vol20` |
| `combo_ifelse__gap_pct__vol5__bar_body_rng_1` | `ifelse` | a=`vol5`, b=`bar_body_rng_1`, cond=`gap_pct` |
| `combo_rank_max__max_down_ret__bar_vol_4` | `rank_max` | a=`max_down_ret`, b=`bar_vol_4` |
| `combo_tri_ifelse__vix__atr14_norm__max_up_ret__vol_gk10__num_up_bars` | `tri_ifelse` | a=`max_up_ret`, b=`vol_gk10`, c=`num_up_bars`, cond=`vix`, cond2=`atr14_norm` |
| `combo_ifelse__vol10__vix_rolling_percentile_60d__bar_body_rng_1` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`bar_body_rng_1`, cond=`vol10` |
| `combo_ifelse__gap_pct__vix_rolling_percentile_60d__first_bar_return` | `ifelse` | a=`vix_rolling_percentile_60d`, b=`first_bar_return`, cond=`gap_pct` |
| `combo_rank_max__vix_diff_1d__max_up_ret` | `rank_max` | a=`vix_diff_1d`, b=`max_up_ret` |
| `combo_ifelse__vol10__short_sell_cover_spread__first_bar_return` | `ifelse` | a=`short_sell_cover_spread`, b=`first_bar_return`, cond=`vol10` |
| `combo_tri_ifelse__vix__atr14_norm__bar_vwap_dev_1__bar_ret_0__early_momentum` | `tri_ifelse` | a=`bar_vwap_dev_1`, b=`bar_ret_0`, c=`early_momentum`, cond=`vix`, cond2=`atr14_norm` |
| `combo_tri_median__vix_skew_proxy__vix_rolling_percentile_60d__max_down_ret` | `tri_median` | a=`vix_skew_proxy`, b=`vix_rolling_percentile_60d`, c=`max_down_ret` |
| `combo_tri_ifelse__vix__vol20__max_up_ret__bar_body_rng_1__max_down_ret` | `tri_ifelse` | a=`max_up_ret`, b=`bar_body_rng_1`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_min__max_up_ret__bar_rng_5` | `min` | a=`max_up_ret`, b=`bar_rng_5` |
| `combo_tri_min__vix_diff_1d__vix__max_down_ret` | `tri_min` | a=`vix_diff_1d`, b=`vix`, c=`max_down_ret` |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | `clamp_diff` | a=`yesterday_range_ratio`, b=`outside_bar_reversal_day` |
| `combo_rank_max__yesterday_day_realized_vol__bar_vol_4` | `rank_max` | a=`yesterday_day_realized_vol`, b=`bar_vol_4` |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | `rank_max` | a=`yesterday_day_realized_vol`, b=`vol_ratio_5_20` |
| `combo_tri_mean__vix_rolling_percentile_60d__atr14_norm__max_down_ret` | `tri_mean` | a=`vix_rolling_percentile_60d`, b=`atr14_norm`, c=`max_down_ret` |
| `combo_product__yesterday_day_realized_vol__total_path_length` | `product` | a=`yesterday_day_realized_vol`, b=`total_path_length` |
| `combo_clamp_diff__vol_gk10__stoch_d` | `clamp_diff` | a=`vol_gk10`, b=`stoch_d` |
| `combo_ratio__yesterday_range_ratio__vol5` | `ratio` | a=`yesterday_range_ratio`, b=`vol5` |
| `combo_ifelse__vol10__bar_ret_0__bar_body_rng_1` | `ifelse` | a=`bar_ret_0`, b=`bar_body_rng_1`, cond=`vol10` |
| `combo_product__max_up_ret__vol10` | `product` | a=`max_up_ret`, b=`vol10` |
| `combo_rank_max__yesterday_day_range__vol_pk20` | `rank_max` | a=`yesterday_day_range`, b=`vol_pk20` |
| `combo_mean__first_30min_return__gap_pct` | `mean` | a=`first_30min_return`, b=`gap_pct` |
| `combo_abs_diff__yesterday_range_ratio__early_range` | `abs_diff` | a=`yesterday_range_ratio`, b=`early_range` |
| `combo_abs_diff__yesterday_day_realized_vol__vol10` | `abs_diff` | a=`yesterday_day_realized_vol`, b=`vol10` |
| `combo_max__vol5__bar_rng_3` | `max` | a=`vol5`, b=`bar_rng_3` |
| `combo_rank_max__bar_vol_4__vol5` | `rank_max` | a=`bar_vol_4`, b=`vol5` |
| `combo_abs_diff__growth_momentum_ratio__bar_vol_5` | `abs_diff` | a=`growth_momentum_ratio`, b=`bar_vol_5` |
| `combo_tri_min__vix_rolling_percentile_60d__yesterday_day_realized_vol__vix_skew_proxy` | `tri_min` | a=`vix_rolling_percentile_60d`, b=`yesterday_day_realized_vol`, c=`vix_skew_proxy` |
| `combo_rank_max__bar_vol_4__vix_diff_1d` | `rank_max` | a=`bar_vol_4`, b=`vix_diff_1d` |
| `combo_diff__bar_vol_4__sma_distance_60d` | `diff` | a=`bar_vol_4`, b=`sma_distance_60d` |
| `combo_ifelse__gap_pct__vol5__vix_skew_proxy` | `ifelse` | a=`vol5`, b=`vix_skew_proxy`, cond=`gap_pct` |
| `combo_abs_diff__bar_vol_4__buy_on_margin_value` | `abs_diff` | a=`bar_vol_4`, b=`buy_on_margin_value` |
| `combo_mean__early_range__volume_slope` | `mean` | a=`early_range`, b=`volume_slope` |
| `combo_product__yesterday_day_realized_vol__bar_rng_0` | `product` | a=`yesterday_day_realized_vol`, b=`bar_rng_0` |
| `combo_rank_max__vix_rolling_percentile_60d__max_down_ret` | `rank_max` | a=`vix_rolling_percentile_60d`, b=`max_down_ret` |
| `combo_product__bar_vol_4__capital_net_value` | `product` | a=`bar_vol_4`, b=`capital_net_value` |
| `combo_abs_diff__buy_on_margin_value__growth_momentum_ratio` | `abs_diff` | a=`buy_on_margin_value`, b=`growth_momentum_ratio` |
| `combo_rank_min__vol_gk10__bar_rng_0` | `rank_min` | a=`vol_gk10`, b=`bar_rng_0` |
| `combo_clamp_diff__vix_diff_1d__capital_buy_value` | `clamp_diff` | a=`vix_diff_1d`, b=`capital_buy_value` |
| `combo_rank_max__bar_vol_4__max_down_ret` | `rank_max` | a=`bar_vol_4`, b=`max_down_ret` |
| `combo_product__capital_net_accel__capital_large_order_ratio` | `product` | a=`capital_net_accel`, b=`capital_large_order_ratio` |
| `combo_rank_max__bar_rng_3__yesterday_volume_ratio` | `rank_max` | a=`bar_rng_3`, b=`yesterday_volume_ratio` |
| `combo_tri_max__body_to_range_ratio__early_range__bar_vol_4` | `tri_max` | a=`body_to_range_ratio`, b=`early_range`, c=`bar_vol_4` |
| `combo_tri_median__iv_envelope_deviation__vix_diff_1d__gap_pct` | `tri_median` | a=`iv_envelope_deviation`, b=`vix_diff_1d`, c=`gap_pct` |
| `combo_ratio__vix_skew_proxy__capital_net_value` | `ratio` | a=`vix_skew_proxy`, b=`capital_net_value` |
| `combo_rank_max__bar_rng_3__capital_sell_volume` | `rank_max` | a=`bar_rng_3`, b=`capital_sell_volume` |
| `combo_clamp_diff__vix_skew_proxy__gap_pct` | `clamp_diff` | a=`vix_skew_proxy`, b=`gap_pct` |
| `combo_rank_max__vol5__capital_net_value` | `rank_max` | a=`vol5`, b=`capital_net_value` |
| `combo_abs_diff__early_range__buy_on_margin_value` | `abs_diff` | a=`early_range`, b=`buy_on_margin_value` |
| `combo_tri_min__vol5__yesterday_day_realized_vol__gap_pct` | `tri_min` | a=`vol5`, b=`yesterday_day_realized_vol`, c=`gap_pct` |
| `combo_mean__vix_skew_proxy__yesterday_pm_am_vol_ratio` | `mean` | a=`vix_skew_proxy`, b=`yesterday_pm_am_vol_ratio` |
| `combo_clamp_diff__bar_vol_5__yesterday_day_close_pos` | `clamp_diff` | a=`bar_vol_5`, b=`yesterday_day_close_pos` |
| `combo_max__vix_rolling_percentile_60d__capital_sell_volume` | `max` | a=`vix_rolling_percentile_60d`, b=`capital_sell_volume` |
| `combo_rank_max__bar_vol_5__capital_buy_value` | `rank_max` | a=`bar_vol_5`, b=`capital_buy_value` |
| `combo_rank_max__vix_rolling_percentile_60d__vol_ratio_10_60` | `rank_max` | a=`vix_rolling_percentile_60d`, b=`vol_ratio_10_60` |
| `combo_abs_diff__yesterday_day_realized_vol__yesterday_volume_ratio` | `abs_diff` | a=`yesterday_day_realized_vol`, b=`yesterday_volume_ratio` |
| `combo_abs_diff__total_path_length__vol_ratio_10_60` | `abs_diff` | a=`total_path_length`, b=`vol_ratio_10_60` |
| `combo_abs_diff__early_realized_vol__growth_momentum_ratio` | `abs_diff` | a=`early_realized_vol`, b=`growth_momentum_ratio` |
| `combo_rank_max__early_range__short_balance` | `rank_max` | a=`early_range`, b=`short_balance` |
| `combo_tri_min__sma_distance_60d__bar_vol_5__yesterday_day_close_pos` | `tri_min` | a=`sma_distance_60d`, b=`bar_vol_5`, c=`yesterday_day_close_pos` |
| `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__margin_buy_repayment_spread` | `tri_ifelse` | a=`max_up_ret`, b=`yesterday_early_vwap_dev`, c=`margin_buy_repayment_spread`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_tri_mean__max_up_ret__early_range__gap_pct` | `tri_mean` | a=`max_up_ret`, b=`early_range`, c=`gap_pct` |
| `combo_diff__max_up_ret__bar_body_rng_1` | `diff` | a=`max_up_ret`, b=`bar_body_rng_1` |
| `combo_tri_mean__yesterday_afternoon_momentum__yesterday_afternoon_reversal__yesterday_day_vwap_dev` | `tri_mean` | a=`yesterday_afternoon_momentum`, b=`yesterday_afternoon_reversal`, c=`yesterday_day_vwap_dev` |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_early_vwap_dev__max_down_ret` | `tri_ifelse` | a=`bar_body_rng_0`, b=`yesterday_early_vwap_dev`, c=`max_down_ret`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_abs_diff__early_range__bar_rng_5` | `abs_diff` | a=`early_range`, b=`bar_rng_5` |
| `combo_tri_max__yesterday_first_30min_return__yesterday_early_trend__gap_pct` | `tri_max` | a=`yesterday_first_30min_return`, b=`yesterday_early_trend`, c=`gap_pct` |
| `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_early_vwap_dev__early_range` | `tri_ifelse` | a=`bar_body_rng_0`, b=`yesterday_early_vwap_dev`, c=`early_range`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_clamp_diff__yesterday_day_vwap_dev__limit_up_proximity_day` | `clamp_diff` | a=`yesterday_day_vwap_dev`, b=`limit_up_proximity_day` |
| `combo_rank_max__max_up_ret__bb_width` | `rank_max` | a=`max_up_ret`, b=`bb_width` |
| `combo_rank_max__willr14__roc10` | `rank_max` | a=`willr14`, b=`roc10` |
| `combo_tri_ifelse__gap_pct__bb_width__first_bar_return__early_range__keltner_squeeze_width` | `tri_ifelse` | a=`first_bar_return`, b=`early_range`, c=`keltner_squeeze_width`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_tri_ifelse__gap_pct__bb_width__yesterday_afternoon_momentum__keltner_squeeze_width__stoch_k` | `tri_ifelse` | a=`yesterday_afternoon_momentum`, b=`keltner_squeeze_width`, c=`stoch_k`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_diff__bar_vol_4__limit_up_proximity_day` | `diff` | a=`bar_vol_4`, b=`limit_up_proximity_day` |
| `combo_ratio__yesterday_day_vwap_dev__bar_vol_4` | `ratio` | a=`yesterday_day_vwap_dev`, b=`bar_vol_4` |
| `combo_product__willr14__roc10` | `product` | a=`willr14`, b=`roc10` |
| `combo_diff__coppock_curve_day__roc10` | `diff` | a=`coppock_curve_day`, b=`roc10` |
| `combo_tri_ifelse__gap_pct__bb_width__yearly_high_distance__margin_buy_repayment_spread__stoch_k` | `tri_ifelse` | a=`yearly_high_distance`, b=`margin_buy_repayment_spread`, c=`stoch_k`, cond=`gap_pct`, cond2=`bb_width` |
| `combo_tri_max__early_range__keltner_squeeze_width__bb_width` | `tri_max` | a=`early_range`, b=`keltner_squeeze_width`, c=`bb_width` |
| `combo_clamp_diff__bar_vol_4__roc10` | `clamp_diff` | a=`bar_vol_4`, b=`roc10` |
| `combo_rank_min__keltner_squeeze_width__sma100_dist` | `rank_min` | a=`keltner_squeeze_width`, b=`sma100_dist` |
| `combo_diff__yesterday_afternoon_momentum__yesterday_afternoon_reversal` | `diff` | a=`yesterday_afternoon_momentum`, b=`yesterday_afternoon_reversal` |
| `combo_rank_max__yesterday_afternoon_momentum__roc10` | `rank_max` | a=`yesterday_afternoon_momentum`, b=`roc10` |
| `combo_min__early_realized_vol__max_down_ret` | `min` | a=`early_realized_vol`, b=`max_down_ret` |
| `combo_product__bar_rng_0__yearly_high_distance` | `product` | a=`bar_rng_0`, b=`yearly_high_distance` |
| `combo_diff__early_trend__max_down_ret` | `diff` | a=`early_trend`, b=`max_down_ret` |
| `combo_min__yesterday_afternoon_momentum__early_realized_vol` | `min` | a=`yesterday_afternoon_momentum`, b=`early_realized_vol` |
| `combo_rank_min__bar_body_rng_1__max_down_ret` | `rank_min` | a=`bar_body_rng_1`, b=`max_down_ret` |
