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
| 300ETF | single | 2,356 | 1,012 | 164 | 110 | 4 |
| 300ETF | long | 218 | 101 | 1 | 0 | 0 |
| 300ETF | short | 11,750 | 2,860 | 319 | 177 | 0 |
| 50ETF | single | 2,725 | 1,059 | 167 | 145 | 0 |
| 50ETF | long | 4,089 | 894 | 77 | 40 | 1 |
| 50ETF | short | 9,086 | 2,135 | 390 | 241 | 0 |
| 500ETF | single | 3,796 | 2,176 | 587 | 465 | 6 |
| 500ETF | long | 5,116 | 1,515 | 490 | 58 | 3 |
| 500ETF | short | 12,191 | 2,881 | 449 | 329 | 0 |
| 588000ETF | single | 9,719 | 5,743 | 3,089 | 2,300 | 8 |
| 588000ETF | long | 7,445 | 2,702 | 905 | 138 | 1 |
| 588000ETF | short | 9,908 | 2,467 | 393 | 205 | 0 |
| 159915ETF | single | 5,236 | 2,859 | 184 | 99 | 1 |
| 159915ETF | long | 3,578 | 770 | 143 | 38 | 0 |
| 159915ETF | short | 12,244 | 4,777 | 1,381 | 1,334 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 4 | +0.1451 | [+0.0935, +0.1937] | +0.2848 | [+0.1792, +0.3909] | +0.9515 | 15.36% | 1.8602 | 2.44% | 0.2973 | 0.5660 | 23.00% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 1 | +0.0552 | [+0.0116, +0.0987] | +0.2102 | [+0.0068, +0.3192] | +0.4303 | 0.90% | 0.1688 | -0.60% | -0.1110 | -0.1642 | 20.45% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.1835 | [+0.1381, +0.2310] | +0.3605 | [+0.2589, +0.4477] | +0.8667 | 17.86% | 1.9168 | 6.92% | 0.7464 | 1.3017 | 20.30% |
| 500ETF | long | 3 | +0.1220 | [+0.0694, +0.1720] | +0.1680 | [+0.0691, +0.3340] | +0.8667 | 10.31% | 1.2376 | 1.55% | 0.1865 | 0.2763 | 15.20% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 8 | +0.1951 | [+0.1417, +0.2459] | +0.4146 | [+0.2988, +0.5111] | +0.7939 | 26.24% | 2.0644 | 16.67% | 1.3146 | 3.5261 | 9.06% |
| 588000ETF | long | 1 | +0.0287* | [-0.0318, +0.0988] | +0.3428 | [+0.0741, +0.4520] | -0.0182 | 7.98% | 0.6347 | 2.63% | 0.2088 | 0.4634 | 21.61% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 1 | +0.1749 | [+0.1248, +0.2209] | +0.2608 | [+0.1711, +0.3527] | +0.9636 | 21.96% | 1.7596 | 9.73% | 0.7857 | 1.2457 | 12.69% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 4 | +0.0671 | [+0.0062, +0.1265] | +0.0502* | [-0.0765, +0.1771] | +0.8909 | 2.88% | 0.3895 | -8.72% | -1.1724 | -1.7626 | 40.34% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 1 | +0.0450* | [-0.0145, +0.1054] | -0.0469* | [-0.2050, +0.1352] | +0.3818 | 0.63% | 0.1822 | -0.77% | -0.2229 | -0.3150 | 8.21% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.0807 | [+0.0268, +0.1361] | +0.0692* | [-0.0578, +0.1910] | +0.8424 | 7.13% | 0.8078 | -5.27% | -0.5949 | -0.9491 | 29.71% |
| 500ETF | long | 3 | +0.0622* | [-0.0006, +0.1181] | -0.0254* | [-0.2021, +0.1170] | +0.7576 | 2.20% | 0.3132 | -6.34% | -0.9018 | -1.3814 | 31.69% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 8 | -0.0050* | [-0.0883, +0.1100] | +0.0744* | [-0.0980, +0.3185] | -0.3333 | 4.73% | 0.9235 | 0.20% | 0.0395 | 0.0602 | 7.52% |
| 588000ETF | long | 1 | -0.0323* | [-0.1127, +0.0655] | -0.2221* | [-0.4031, +0.2846] | -0.1030 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 1 | +0.1285 | [+0.0590, +0.1844] | +0.2275 | [+0.0743, +0.3424] | +0.7697 | 19.12% | 1.8139 | 6.29% | 0.5984 | 1.0381 | 15.44% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 4 | +0.0182* | [-0.0773, +0.0921] | -0.0292* | [-0.1889, +0.1271] | +0.2848 | 1.64% | 0.4877 | -4.57% | -1.3248 | -1.9652 | 12.51% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 1 | +0.0836 | [+0.0245, +0.1564] | -0.0677* | [-0.2275, +0.1795] | +0.6848 | 1.02% | 0.2721 | 0.13% | 0.0355 | 0.0501 | 4.43% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.0753* | [-0.0067, +0.1553] | +0.0872* | [-0.1026, +0.2706] | +0.6121 | 5.97% | 0.6220 | -7.10% | -0.7377 | -1.1588 | 24.49% |
| 500ETF | long | 3 | +0.0418* | [-0.0449, +0.1307] | -0.1136* | [-0.2720, +0.1513] | +0.6606 | 0.57% | 0.0910 | -8.19% | -1.3048 | -1.7938 | 19.75% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 8 | -0.0495* | [-0.1564, +0.0783] | +0.0489* | [-0.2784, +0.3659] | -0.5758 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 1 | -0.0797* | [-0.1855, +0.0429] | -0.2299* | [-0.5028, +0.3691] | -0.4788 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 1 | +0.1341 | [+0.0380, +0.2180] | +0.2537 | [+0.0280, +0.4329] | +0.8061 | 20.69% | 1.6827 | 7.43% | 0.6029 | 1.0581 | 16.15% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

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

### 300ETF / long
No features admitted.

### 300ETF / short
No features admitted.

### 50ETF / single
No features admitted.

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
| `combo_mean__gap_pct__early_range` | +1 | +0.1229 | +0.2090 | +0.2092 | 0.0000 | +0.5517 | +0.7038 | 0.247 |
| `combo_product__yesterday_illiquidity_amihud__early_range` | +1 | +0.0575 | +0.1970 | +0.1966 | 0.0000 | +0.5070 | +0.7050 | 0.340 |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | +1 | +0.1099 | +0.1777 | +0.1770 | 0.0006 | +0.4480 | +0.7032 | 0.276 |
| `combo_ratio__vix_realized_spread__total_balance` | +1 | +0.0427 | +0.1773 | +0.1754 | 0.0006 | +0.6015 | +0.7226 | 0.191 |

### 500ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_abs_diff__willr14__max_up_ret` | +1 | +0.0224 | +0.3177 | +0.3168 | 0.0000 | +0.4204 | +0.6440 | 0.000 |
| `combo_rank_min__yearly_low_distance__max_up_ret` | +1 | +0.0827 | +0.2313 | +0.2302 | 0.0000 | +0.1517 | +0.5642 | 0.178 |
| `combo_min__first_30min_return__bar_body_rng_2` | +1 | +0.0719 | +0.2273 | +0.2275 | 0.0000 | +0.3452 | +0.6129 | 0.256 |

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | +1 | +0.1720 | +0.4122 | +0.4109 | 0.0000 | +1.1922 | +0.8539 | 0.000 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_body_rng_1` | +1 | +0.1160 | +0.3384 | +0.3359 | 0.0000 | +1.1746 | +0.8480 | 0.268 |
| `combo_tri_median__first_30min_return__max_up_ret__early_skew` | +1 | +0.1263 | +0.3049 | +0.3055 | 0.0000 | +0.9033 | +0.8312 | 0.300 |
| `combo_tri_ifelse__atr14_norm__vol20__vix_rolling_percentile_60d__num_up_bars__early_skew` | +1 | +0.0578 | +0.2522 | +0.2519 | 0.0002 | +0.6185 | +0.7621 | 0.335 |
| `combo_rank_max__vix_diff_1d__bar_vol_4` | +1 | +0.0896 | +0.2306 | +0.2307 | 0.0014 | +0.5371 | +0.7019 | 0.174 |
| `combo_max__yesterday_day_realized_vol__max_down_ret` | +1 | +0.1325 | +0.2281 | +0.2277 | 0.0016 | +0.7511 | +0.7127 | 0.350 |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | +1 | +0.0580 | +0.2078 | +0.2084 | 0.0032 | +0.5389 | +0.7216 | 0.316 |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | +1 | +0.0461 | +0.2006 | +0.2007 | 0.0042 | +0.9300 | +0.8045 | 0.343 |

### 588000ETF / long

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_max__vol5__bar_rng_3` | +1 | +0.0287 | +0.3428 | +0.3432 | 0.0000 | +0.3000 | +0.5913 | 0.000 |

### 588000ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_mean__max_up_ret__bar_ret_0__gap_pct` | +1 | +0.1749 | +0.2608 | +0.2589 | 0.0000 | +0.6199 | +0.7208 | 0.000 |

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
| `combo_diff__yearly_low_distance__yesterday_wavetrend_osc` | `diff` | a=`yearly_low_distance`, b=`yesterday_wavetrend_osc` |
| `combo_diff__max_up_ret__willr14` | `diff` | a=`max_up_ret`, b=`willr14` |
| `combo_ifelse__gap_pct__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`gap_pct` |
| `combo_mean__gap_pct__early_range` | `mean` | a=`gap_pct`, b=`early_range` |
| `combo_product__yesterday_illiquidity_amihud__early_range` | `product` | a=`yesterday_illiquidity_amihud`, b=`early_range` |
| `combo_ifelse__gap_pct__bar_ret_0__yesterday_early_vwap_dev` | `ifelse` | a=`bar_ret_0`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_ratio__vix_realized_spread__total_balance` | `ratio` | a=`vix_realized_spread`, b=`total_balance` |
| `combo_abs_diff__willr14__max_up_ret` | `abs_diff` | a=`willr14`, b=`max_up_ret` |
| `combo_rank_min__yearly_low_distance__max_up_ret` | `rank_min` | a=`yearly_low_distance`, b=`max_up_ret` |
| `combo_min__first_30min_return__bar_body_rng_2` | `min` | a=`first_30min_return`, b=`bar_body_rng_2` |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol_gk10__max_down_ret` | `tri_ifelse` | a=`vix_skew_proxy`, b=`vol_gk10`, c=`max_down_ret`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_body_rng_1` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol5`, c=`bar_body_rng_1`, cond=`vix`, cond2=`vol20` |
| `combo_tri_median__first_30min_return__max_up_ret__early_skew` | `tri_median` | a=`first_30min_return`, b=`max_up_ret`, c=`early_skew` |
| `combo_tri_ifelse__atr14_norm__vol20__vix_rolling_percentile_60d__num_up_bars__early_skew` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`num_up_bars`, c=`early_skew`, cond=`atr14_norm`, cond2=`vol20` |
| `combo_rank_max__vix_diff_1d__bar_vol_4` | `rank_max` | a=`vix_diff_1d`, b=`bar_vol_4` |
| `combo_max__yesterday_day_realized_vol__max_down_ret` | `max` | a=`yesterday_day_realized_vol`, b=`max_down_ret` |
| `combo_clamp_diff__yesterday_range_ratio__outside_bar_reversal_day` | `clamp_diff` | a=`yesterday_range_ratio`, b=`outside_bar_reversal_day` |
| `combo_rank_max__yesterday_day_realized_vol__vol_ratio_5_20` | `rank_max` | a=`yesterday_day_realized_vol`, b=`vol_ratio_5_20` |
| `combo_max__vol5__bar_rng_3` | `max` | a=`vol5`, b=`bar_rng_3` |
| `combo_tri_mean__max_up_ret__bar_ret_0__gap_pct` | `tri_mean` | a=`max_up_ret`, b=`bar_ret_0`, c=`gap_pct` |
