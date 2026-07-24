# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2016_2024`

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

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 1,443 | 412 | 361 | 351 | 121 | 121 | 120 | 21 | 21 |
| 300ETF | long | 586 | 58 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 587 | 69 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 743 | 32 | 11 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 368 | 43 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 321 | 46 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 2,865 | 1,103 | 935 | 923 | 463 | 332 | 332 | 31 | 31 |
| 500ETF | long | 1,350 | 96 | 37 | 2 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 428 | 51 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 1,831 | 692 | 582 | 573 | 226 | 215 | 215 | 30 | 30 |
| 159915ETF | long | 1,120 | 214 | 130 | 11 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 299 | 52 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 21 | +0.1151 | [+0.0715, +0.1568] | +0.2372 | [+0.1396, +0.3385] | +0.8788 | 4.86% | 1.5781 | 1.75% | 0.5777 | 1.1079 | 6.09% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 31 | +0.1466 | [+0.1042, +0.1908] | +0.2375 | [+0.1543, +0.3385] | +0.8667 | 5.56% | 1.4079 | 2.67% | 0.6811 | 1.1463 | 4.99% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 30 | +0.1414 | [+0.0969, +0.1841] | +0.2794 | [+0.1835, +0.3707] | +0.7212 | 8.42% | 1.8859 | 5.60% | 1.2644 | 2.2045 | 5.04% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 21 | +0.0311* | [-0.0589, +0.1212] | +0.0722* | [-0.1181, +0.2228] | +0.5152 | 2.52% | 0.6842 | -0.58% | -0.1576 | -0.3320 | 5.91% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 31 | +0.1137 | [+0.0322, +0.1879] | +0.0888* | [-0.1017, +0.2333] | +0.8303 | 4.96% | 0.9300 | 2.29% | 0.4336 | 0.8010 | 5.48% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 30 | +0.1437 | [+0.0521, +0.2201] | +0.2663 | [+0.0307, +0.4887] | +0.7212 | 11.95% | 1.5045 | 9.43% | 1.1947 | 3.3180 | 7.41% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +1 | +0.1000 | +0.2637 | +0.2645 | 0.0000 | +0.6771 | +0.7285 | 0.000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +1 | +0.1024 | +0.2543 | +0.2540 | 0.0000 | +0.7278 | +0.7733 | 0.765 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +1 | +0.1013 | +0.2493 | +0.2494 | 0.0000 | +0.6618 | +0.7450 | 0.661 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | +1 | +0.0911 | +0.2421 | +0.2414 | 0.0000 | +0.6260 | +0.7152 | 0.786 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0952 | +0.2350 | +0.2352 | 0.0000 | +0.6025 | +0.7136 | 0.769 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +1 | +0.1006 | +0.2276 | +0.2278 | 0.0000 | +0.5787 | +0.6951 | 0.849 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | +1 | +0.0986 | +0.2231 | +0.2231 | 0.0000 | +0.7127 | +0.7553 | 0.780 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | +1 | +0.0998 | +0.2226 | +0.2227 | 0.0000 | +0.6215 | +0.7167 | 0.821 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +1 | +0.0845 | +0.2226 | +0.2229 | 0.0000 | +0.8085 | +0.8165 | 0.841 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0955 | +0.2167 | +0.2162 | 0.0000 | +0.6142 | +0.6982 | 0.847 |
| `combo_rank_max__bar_ret_0__first_bar_sentiment` | +1 | +0.0941 | +0.1993 | +0.1995 | 0.0000 | +0.4842 | +0.6720 | 0.805 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.0793 | +0.1982 | +0.1980 | 0.0000 | +0.5093 | +0.6910 | 0.847 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +1 | +0.0849 | +0.1940 | +0.1933 | 0.0002 | +0.5866 | +0.7260 | 0.709 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0916 | +0.1901 | +0.1901 | 0.0002 | +0.7117 | +0.7599 | 0.846 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | +1 | +0.0922 | +0.1828 | +0.1826 | 0.0002 | +0.5287 | +0.7167 | 0.786 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | +1 | +0.0884 | +0.1805 | +0.1801 | 0.0002 | +0.5938 | +0.7352 | 0.803 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +1 | +0.0918 | +0.1778 | +0.1777 | 0.0002 | +0.4384 | +0.6612 | 0.800 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +1 | +0.0957 | +0.1636 | +0.1640 | 0.0010 | +0.5224 | +0.6766 | 0.818 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +1 | +0.0719 | +0.1591 | +0.1593 | 0.0014 | +0.4843 | +0.6864 | 0.593 |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | +1 | +0.0832 | +0.1577 | +0.1580 | 0.0016 | +0.4377 | +0.6781 | 0.842 |
| `combo_mean__volume_weighted_price_position__double_bottom_bull_flag_early` | +1 | +0.0318 | +0.1249 | +0.1268 | 0.0120 | +0.4959 | +0.6792 | 0.541 |

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1412 | +0.2745 | +0.2746 | 0.0000 | +1.0155 | +0.8370 | 0.000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +1 | +0.1346 | +0.2743 | +0.2737 | 0.0000 | +0.7631 | +0.7758 | 0.665 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +1 | +0.1302 | +0.2717 | +0.2718 | 0.0000 | +0.7606 | +0.7429 | 0.844 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | +1 | +0.1384 | +0.2698 | +0.2695 | 0.0000 | +0.7336 | +0.7630 | 0.704 |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | +1 | +0.1177 | +0.2648 | +0.2657 | 0.0000 | +0.7438 | +0.7440 | 0.654 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | +1 | +0.1283 | +0.2615 | +0.2607 | 0.0000 | +0.8854 | +0.8077 | 0.777 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +1 | +0.1166 | +0.2535 | +0.2541 | 0.0000 | +0.7056 | +0.7522 | 0.828 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | +1 | +0.1404 | +0.2527 | +0.2518 | 0.0000 | +0.8499 | +0.7913 | 0.839 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +1 | +0.1232 | +0.2455 | +0.2461 | 0.0000 | +0.7204 | +0.7470 | 0.803 |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | +1 | +0.1029 | +0.2285 | +0.2290 | 0.0000 | +0.5745 | +0.6992 | 0.850 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | +1 | +0.1289 | +0.2280 | +0.2277 | 0.0000 | +0.7346 | +0.7373 | 0.824 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1244 | +0.2279 | +0.2288 | 0.0000 | +0.6265 | +0.7573 | 0.782 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +1 | +0.1223 | +0.2267 | +0.2275 | 0.0000 | +0.5688 | +0.7049 | 0.838 |
| `combo_min__volatility_expansion_trend_vector__close_vs_open_range` | +1 | +0.0941 | +0.2250 | +0.2248 | 0.0000 | +0.4374 | +0.6746 | 0.819 |
| `combo_max__close_vs_open_range__first_bar_return` | +1 | +0.1344 | +0.2195 | +0.2202 | 0.0000 | +0.6971 | +0.7666 | 0.843 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +1 | +0.1252 | +0.2155 | +0.2148 | 0.0000 | +0.5008 | +0.6951 | 0.842 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +1 | +0.1362 | +0.2076 | +0.2074 | 0.0000 | +0.7541 | +0.7548 | 0.818 |
| `combo_max__bar_ret_0__max_down_ret` | +1 | +0.1239 | +0.2061 | +0.2067 | 0.0000 | +0.5692 | +0.6879 | 0.823 |
| `max_up_ret` | +1 | +0.1293 | +0.2055 | +0.2058 | 0.0000 | +0.5418 | +0.6967 | 0.831 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | +1 | +0.1453 | +0.1967 | +0.1970 | 0.0000 | +0.6058 | +0.7434 | 0.843 |
| `combo_max__star50_limit_proximity_early__early_body_momentum` | +1 | +0.0887 | +0.1874 | +0.1869 | 0.0000 | +0.4469 | +0.6401 | 0.831 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | +1 | +0.1072 | +0.1837 | +0.1838 | 0.0000 | +0.5209 | +0.6792 | 0.824 |
| `combo_sig_product__max_up_ret__first_bar_return` | +1 | +0.1181 | +0.1831 | +0.1835 | 0.0000 | +0.5083 | +0.7147 | 0.782 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +1 | +0.1104 | +0.1738 | +0.1732 | 0.0006 | +0.4085 | +0.6591 | 0.581 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +1 | +0.0934 | +0.1732 | +0.1734 | 0.0006 | +0.7621 | +0.7548 | 0.832 |
| `combo_sig_product__opening_auction_imbalance__first_bar_return` | +1 | +0.0794 | +0.1720 | +0.1723 | 0.0006 | +0.3727 | +0.6252 | 0.843 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +1 | +0.0825 | +0.1698 | +0.1698 | 0.0006 | +0.4848 | +0.6530 | 0.827 |
| `vwap_close_divergence_trend` | +1 | +0.0837 | +0.1606 | +0.1592 | 0.0014 | +0.4241 | +0.6411 | 0.797 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | +1 | +0.1162 | +0.1568 | +0.1566 | 0.0024 | +0.5826 | +0.6915 | 0.832 |
| `combo_z_sum__opening_drive_thrust_ratio__max_down_ret` | +1 | +0.1274 | +0.1368 | +0.1362 | 0.0066 | +0.5356 | +0.7219 | 0.850 |
| `combo_z_sum__first_bar_sentiment__max_down_ret` | +1 | +0.1068 | +0.1241 | +0.1242 | 0.0138 | +0.4636 | +0.6571 | 0.849 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1446 | +0.3321 | +0.3316 | 0.0000 | +0.8369 | +0.8046 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +1 | +0.1163 | +0.2933 | +0.2948 | 0.0000 | +0.7699 | +0.8231 | 0.373 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1455 | +0.2928 | +0.2927 | 0.0000 | +0.7355 | +0.7758 | 0.820 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +1 | +0.1237 | +0.2883 | +0.2887 | 0.0000 | +0.8062 | +0.7825 | 0.811 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +1 | +0.0989 | +0.2652 | +0.2652 | 0.0000 | +0.7408 | +0.7769 | 0.845 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | +1 | +0.1415 | +0.2644 | +0.2645 | 0.0000 | +0.5130 | +0.6920 | 0.847 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +1 | +0.1141 | +0.2551 | +0.2551 | 0.0000 | +0.5473 | +0.7414 | 0.824 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0880 | +0.2540 | +0.2561 | 0.0000 | +0.6914 | +0.7548 | 0.787 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +1 | +0.1039 | +0.2524 | +0.2516 | 0.0000 | +0.7646 | +0.7887 | 0.766 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | +1 | +0.1221 | +0.2493 | +0.2494 | 0.0000 | +0.4894 | +0.6992 | 0.846 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.1182 | +0.2437 | +0.2438 | 0.0000 | +0.6376 | +0.7434 | 0.755 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | +1 | +0.1137 | +0.2421 | +0.2424 | 0.0000 | +0.6577 | +0.7275 | 0.847 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +1 | +0.1178 | +0.2369 | +0.2370 | 0.0000 | +0.5091 | +0.6982 | 0.844 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.1014 | +0.2348 | +0.2361 | 0.0000 | +0.7438 | +0.7650 | 0.810 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +1 | +0.0944 | +0.2314 | +0.2306 | 0.0000 | +0.6001 | +0.7090 | 0.835 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | +1 | +0.0976 | +0.2305 | +0.2310 | 0.0000 | +0.7555 | +0.7671 | 0.817 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +1 | +0.1019 | +0.2219 | +0.2223 | 0.0000 | +0.5745 | +0.7141 | 0.803 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +1 | +0.1265 | +0.2163 | +0.2164 | 0.0000 | +0.4161 | +0.6154 | 0.844 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +1 | +0.0942 | +0.2126 | +0.2128 | 0.0000 | +0.5345 | +0.6812 | 0.767 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +1 | +0.0613 | +0.2121 | +0.2131 | 0.0000 | +0.4743 | +0.6463 | 0.510 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | +1 | +0.1133 | +0.2117 | +0.2112 | 0.0000 | +0.5773 | +0.7121 | 0.838 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | +1 | +0.1165 | +0.2097 | +0.2095 | 0.0000 | +0.5061 | +0.6853 | 0.818 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +1 | +0.0984 | +0.2085 | +0.2084 | 0.0000 | +0.4538 | +0.6658 | 0.800 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +1 | +0.1142 | +0.2049 | +0.2041 | 0.0002 | +0.4084 | +0.6488 | 0.843 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +1 | +0.1056 | +0.1933 | +0.1929 | 0.0004 | +0.6237 | +0.7285 | 0.817 |
| `combo_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | +1 | +0.0635 | +0.1900 | +0.1922 | 0.0006 | +0.4998 | +0.6674 | 0.835 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | +1 | +0.1016 | +0.1848 | +0.1848 | 0.0006 | +0.4947 | +0.6910 | 0.843 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +1 | +0.0974 | +0.1774 | +0.1767 | 0.0010 | +0.3693 | +0.6560 | 0.823 |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | +1 | +0.1009 | +0.1752 | +0.1746 | 0.0010 | +0.4536 | +0.6308 | 0.824 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +1 | +0.0962 | +0.1453 | +0.1453 | 0.0046 | +0.3421 | +0.6422 | 0.729 |

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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | `min` | a=`max_up_ret`, b=`opening_drive_thrust_ratio` |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | `z_sum` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_max` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | `tri_max` | a=`first_bar_return`, b=`volume_weighted_price_position`, c=`bar_body_rng_0` |
| `combo_max__max_up_ret__volume_weighted_price_position` | `max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | `min` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__bar_ret_0__first_bar_sentiment` | `rank_max` | a=`bar_ret_0`, b=`first_bar_sentiment` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | `sig_product` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio` |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | `rank_max` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | `min` | a=`opening_drive_thrust_ratio`, b=`volume_surge_direction` |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | `sig_product` | a=`volume_weighted_price_position`, b=`opening_drive_thrust_ratio` |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`early_vwap_acceleration` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | `diff` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_vol_0` |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | `sig_product` | a=`bar_ret_0`, b=`opening_drive_thrust_ratio` |
| `combo_mean__volume_weighted_price_position__double_bottom_bull_flag_early` | `mean` | a=`volume_weighted_price_position`, b=`double_bottom_bull_flag_early` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_clamp_diff__max_up_ret__body_size_progression` | `clamp_diff` | a=`max_up_ret`, b=`body_size_progression` |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | `rank_max` | a=`first_bar_sentiment`, b=`bar_ret_0` |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | `rel_diff` | a=`opening_auction_imbalance`, b=`volume_weighted_momentum_acceleration` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | `rel_diff` | a=`max_up_ret`, b=`smooth_momentum_structure` |
| `combo_rank_max__early_body_momentum__bar_ret_0` | `rank_max` | a=`early_body_momentum`, b=`bar_ret_0` |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | `min` | a=`opening_auction_imbalance`, b=`star50_limit_proximity_early` |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | `min` | a=`opening_drive_thrust_ratio`, b=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__volatility_expansion_trend_vector__close_vs_open_range` | `min` | a=`volatility_expansion_trend_vector`, b=`close_vs_open_range` |
| `combo_max__close_vs_open_range__first_bar_return` | `max` | a=`close_vs_open_range`, b=`first_bar_return` |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | `rank_max` | a=`max_up_ret`, b=`first_bar_sentiment` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_max__star50_limit_proximity_early__early_body_momentum` | `max` | a=`star50_limit_proximity_early`, b=`early_body_momentum` |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__first_bar_return` | `sig_product` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | `sig_product` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | `rank_min` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_sig_product__opening_auction_imbalance__first_bar_return` | `sig_product` | a=`opening_auction_imbalance`, b=`first_bar_return` |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | `mean` | a=`star50_limit_proximity_early`, b=`max_down_ret` |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | `rel_diff` | a=`opening_drive_thrust_ratio`, b=`late_bar_momentum` |
| `combo_z_sum__opening_drive_thrust_ratio__max_down_ret` | `z_sum` | a=`opening_drive_thrust_ratio`, b=`max_down_ret` |
| `combo_z_sum__first_bar_sentiment__max_down_ret` | `z_sum` | a=`first_bar_sentiment`, b=`max_down_ret` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_early_vwap_dev`, c=`yesterday_first_30min_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`star50_limit_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | `rel_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `sig_product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_min__star50_limit_proximity_early__first_bar_return` | `min` | a=`star50_limit_proximity_early`, b=`first_bar_return` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | `mean` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | `rank_max` | a=`max_up_ret`, b=`impulse_bar_dominance` |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | `rank_max` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return` |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | `product` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | `rank_max` | a=`star50_limit_proximity_early`, b=`first_bar_sentiment` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`impulse_bar_dominance` |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early` |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | `ratio` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | `min` | a=`yesterday_first_30min_return`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`demark_setup_reversal_early` |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | `z_sum` | a=`first_bar_sentiment`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | `ratio` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
