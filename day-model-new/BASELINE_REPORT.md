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
| 300ETF | single | 1,087 | 161 | 41 | 0 | 0 |
| 300ETF | long | 2,668 | 204 | 11 | 0 | 0 |
| 300ETF | short | 531 | 119 | 5 | 0 | 0 |
| 50ETF | single | 1,273 | 151 | 12 | 0 | 0 |
| 50ETF | long | 1,597 | 195 | 2 | 0 | 0 |
| 50ETF | short | 1,956 | 264 | 14 | 0 | 0 |
| 500ETF | single | 1,415 | 479 | 326 | 271 | 26 |
| 500ETF | long | 700 | 149 | 21 | 0 | 0 |
| 500ETF | short | 1,190 | 222 | 2 | 0 | 0 |
| 588000ETF | single | 1,214 | 486 | 339 | 284 | 3 |
| 588000ETF | long | 492 | 144 | 39 | 2 | 0 |
| 588000ETF | short | 608 | 130 | 10 | 0 | 0 |
| 159915ETF | single | 871 | 170 | 24 | 9 | 0 |
| 159915ETF | long | 1,132 | 156 | 32 | 0 | 0 |
| 159915ETF | short | 593 | 132 | 10 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.1915 | [+0.1465, +0.2403] | +0.2954 | [+0.1900, +0.4009] | +0.8909 | 9.97% | 1.7263 | 7.11% | 1.2412 | 2.2733 | 5.15% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 3 | +0.1425 | [+0.0726, +0.2038] | +0.3226 | [+0.1509, +0.4701] | +0.8667 | 11.58% | 1.7111 | 9.61% | 1.4287 | 7.0280 | 3.55% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.0936 | [+0.0342, +0.1528] | +0.0646* | [-0.0790, +0.1774] | +0.9879 | 2.55% | 0.5615 | -0.11% | -0.0234 | -0.0382 | 10.01% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 3 | -0.0162* | [-0.1167, +0.0990] | +0.0381* | [-0.1698, +0.2258] | -0.3455 | 2.09% | 0.8635 | 1.54% | 0.6466 | 2.3696 | 0.98% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 11 | +0.0936 | [+0.0137, +0.1757] | +0.0403* | [-0.1476, +0.1683] | +0.8545 | 0.75% | 0.1900 | -2.05% | -0.5139 | -0.7361 | 10.74% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | single | 3 | -0.0433* | [-0.1671, +0.1026] | +0.0735* | [-0.2454, +0.3418] | -0.2848 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 588000ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single
No features admitted.

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
| `combo_clamp_diff__max_up_ret__cl_pos_in_range` | +1 | +0.1075 | +0.2964 | +0.2971 | 0.0000 | +0.4866 | +0.6639 | 0.000 |
| `combo_max__max_up_ret__bb_width` | +1 | +0.1486 | +0.2715 | +0.2731 | 0.0000 | +0.7698 | +0.7765 | 0.336 |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_ret_1` | +1 | +0.1862 | +0.2714 | +0.2707 | 0.0000 | +0.6705 | +0.7349 | 0.729 |
| `combo_tri_median__max_up_ret__num_up_bars__bar_ret_1` | +1 | +0.1492 | +0.2619 | +0.2610 | 0.0000 | +0.9851 | +0.8499 | 0.816 |
| `combo_tri_median__bar_ret_0__max_down_ret__bar_ret_1` | +1 | +0.1564 | +0.2567 | +0.2561 | 0.0000 | +0.5757 | +0.6739 | 0.672 |
| `combo_diff__max_up_ret__stoch_k` | +1 | +0.1060 | +0.2482 | +0.2488 | 0.0000 | +1.1920 | +0.8833 | 0.625 |
| `combo_ifelse__bb_width__bar_ret_0__bar_body_rng_0` | +1 | +0.1560 | +0.2431 | +0.2423 | 0.0000 | +0.6442 | +0.7191 | 0.591 |
| `combo_ratio__max_down_ret__bb_width` | +1 | +0.1303 | +0.2322 | +0.2303 | 0.0000 | +0.6685 | +0.7296 | 0.617 |
| `combo_ratio__max_up_ret__bb_width` | +1 | +0.1444 | +0.2271 | +0.2280 | 0.0000 | +0.6097 | +0.7443 | 0.620 |
| `combo_tri_max__max_up_ret__bar_body_rng_1__bar_ret_1` | +1 | +0.1347 | +0.2256 | +0.2257 | 0.0000 | +0.6806 | +0.7484 | 0.776 |
| `combo_max__max_up_ret__stoch_k` | +1 | +0.1161 | +0.2226 | +0.2214 | 0.0000 | +0.3272 | +0.6246 | 0.680 |
| `combo_ifelse__bb_width__max_up_ret__max_down_ret` | +1 | +0.1508 | +0.2198 | +0.2189 | 0.0000 | +0.5626 | +0.7238 | 0.819 |
| `combo_product__body_to_range_ratio__cl_pos_in_range` | +1 | +0.1315 | +0.2137 | +0.2143 | 0.0000 | +0.3435 | +0.6258 | 0.577 |
| `combo_mean__max_up_ret__roc5` | +1 | +0.1315 | +0.2080 | +0.2071 | 0.0000 | +0.4067 | +0.6563 | 0.661 |
| `combo_mean__max_up_ret__capital_sell_volume` | +1 | +0.1502 | +0.2028 | +0.2016 | 0.0000 | +0.6961 | +0.7378 | 0.660 |
| `combo_max__max_up_ret__yesterday_return` | +1 | +0.1236 | +0.2019 | +0.2025 | 0.0000 | +0.5641 | +0.6927 | 0.688 |
| `combo_ifelse__bb_width__first_bar_return__bar_vwap_dev_2` | +1 | +0.1260 | +0.2017 | +0.2010 | 0.0000 | +0.6544 | +0.7232 | 0.487 |
| `first_bar_return` | +1 | +0.1592 | +0.1937 | +0.1931 | 0.0000 | +0.5925 | +0.7109 | 0.826 |
| `combo_rank_max__max_up_ret__yesterday_return` | +1 | +0.1267 | +0.1909 | +0.1914 | 0.0000 | +0.3893 | +0.6141 | 0.786 |
| `combo_rank_max__max_up_ret__bb_width` | +1 | +0.1477 | +0.1882 | +0.1889 | 0.0002 | +0.6534 | +0.7425 | 0.681 |
| `combo_max__max_up_ret__roc5` | +1 | +0.1216 | +0.1807 | +0.1801 | 0.0006 | +0.4800 | +0.6481 | 0.829 |
| `combo_clamp_diff__max_down_ret__yesterday_return` | +1 | +0.0897 | +0.1710 | +0.1708 | 0.0012 | +0.4397 | +0.6680 | 0.474 |
| `combo_mean__body_to_range_ratio__cl_pos_in_range` | +1 | +0.0653 | +0.1697 | +0.1688 | 0.0016 | +0.6965 | +0.7894 | 0.486 |
| `combo_ifelse__bb_width__max_up_ret__first_30min_return` | +1 | +0.1256 | +0.1659 | +0.1652 | 0.0026 | +0.5322 | +0.7161 | 0.819 |
| `combo_mean__max_up_ret__bb_width` | +1 | +0.1340 | +0.1658 | +0.1670 | 0.0026 | +0.6836 | +0.7185 | 0.779 |
| `combo_ifelse__bb_width__num_up_bars__bar_body_rng_0` | +1 | +0.1324 | +0.1352 | +0.1343 | 0.0124 | +0.4237 | +0.6821 | 0.732 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 588000ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol5__bar_vwap_dev_2` | +1 | +0.1097 | +0.3073 | +0.3055 | 0.0000 | +0.8572 | +0.7759 | 0.000 |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_vwap_dev_2` | +1 | +0.1002 | +0.2608 | +0.2598 | 0.0002 | +0.8485 | +0.7779 | 0.639 |
| `max_up_ret` | +1 | +0.1040 | +0.1935 | +0.1934 | 0.0062 | +0.6051 | +0.7266 | 0.298 |

### 588000ETF / long
No features admitted.

### 588000ETF / short
No features admitted.

### 159915ETF / single
No features admitted.

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_clamp_diff__max_up_ret__cl_pos_in_range` | `clamp_diff` | a=`max_up_ret`, b=`cl_pos_in_range` |
| `combo_max__max_up_ret__bb_width` | `max` | a=`max_up_ret`, b=`bb_width` |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_ret_1` | `tri_mean` | a=`max_up_ret`, b=`first_bar_return`, c=`bar_ret_1` |
| `combo_tri_median__max_up_ret__num_up_bars__bar_ret_1` | `tri_median` | a=`max_up_ret`, b=`num_up_bars`, c=`bar_ret_1` |
| `combo_tri_median__bar_ret_0__max_down_ret__bar_ret_1` | `tri_median` | a=`bar_ret_0`, b=`max_down_ret`, c=`bar_ret_1` |
| `combo_diff__max_up_ret__stoch_k` | `diff` | a=`max_up_ret`, b=`stoch_k` |
| `combo_ifelse__bb_width__bar_ret_0__bar_body_rng_0` | `ifelse` | a=`bar_ret_0`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_ratio__max_down_ret__bb_width` | `ratio` | a=`max_down_ret`, b=`bb_width` |
| `combo_ratio__max_up_ret__bb_width` | `ratio` | a=`max_up_ret`, b=`bb_width` |
| `combo_tri_max__max_up_ret__bar_body_rng_1__bar_ret_1` | `tri_max` | a=`max_up_ret`, b=`bar_body_rng_1`, c=`bar_ret_1` |
| `combo_max__max_up_ret__stoch_k` | `max` | a=`max_up_ret`, b=`stoch_k` |
| `combo_ifelse__bb_width__max_up_ret__max_down_ret` | `ifelse` | a=`max_up_ret`, b=`max_down_ret`, cond=`bb_width` |
| `combo_product__body_to_range_ratio__cl_pos_in_range` | `product` | a=`body_to_range_ratio`, b=`cl_pos_in_range` |
| `combo_mean__max_up_ret__roc5` | `mean` | a=`max_up_ret`, b=`roc5` |
| `combo_mean__max_up_ret__capital_sell_volume` | `mean` | a=`max_up_ret`, b=`capital_sell_volume` |
| `combo_max__max_up_ret__yesterday_return` | `max` | a=`max_up_ret`, b=`yesterday_return` |
| `combo_ifelse__bb_width__first_bar_return__bar_vwap_dev_2` | `ifelse` | a=`first_bar_return`, b=`bar_vwap_dev_2`, cond=`bb_width` |
| `combo_rank_max__max_up_ret__yesterday_return` | `rank_max` | a=`max_up_ret`, b=`yesterday_return` |
| `combo_rank_max__max_up_ret__bb_width` | `rank_max` | a=`max_up_ret`, b=`bb_width` |
| `combo_max__max_up_ret__roc5` | `max` | a=`max_up_ret`, b=`roc5` |
| `combo_clamp_diff__max_down_ret__yesterday_return` | `clamp_diff` | a=`max_down_ret`, b=`yesterday_return` |
| `combo_mean__body_to_range_ratio__cl_pos_in_range` | `mean` | a=`body_to_range_ratio`, b=`cl_pos_in_range` |
| `combo_ifelse__bb_width__max_up_ret__first_30min_return` | `ifelse` | a=`max_up_ret`, b=`first_30min_return`, cond=`bb_width` |
| `combo_mean__max_up_ret__bb_width` | `mean` | a=`max_up_ret`, b=`bb_width` |
| `combo_ifelse__bb_width__num_up_bars__bar_body_rng_0` | `ifelse` | a=`num_up_bars`, b=`bar_body_rng_0`, cond=`bb_width` |
| `combo_tri_ifelse__vix__vol20__vix_skew_proxy__vol5__bar_vwap_dev_2` | `tri_ifelse` | a=`vix_skew_proxy`, b=`vol5`, c=`bar_vwap_dev_2`, cond=`vix`, cond2=`vol20` |
| `combo_tri_ifelse__vix__vol20__vix_rolling_percentile_60d__vol5__bar_vwap_dev_2` | `tri_ifelse` | a=`vix_rolling_percentile_60d`, b=`vol5`, c=`bar_vwap_dev_2`, cond=`vix`, cond2=`vol20` |
