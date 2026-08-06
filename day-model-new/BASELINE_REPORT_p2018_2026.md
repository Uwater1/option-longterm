# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2018_2026`

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

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted | Clusters | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 300ETF | single | 1,798 | 606 | 485 | 394 | 392 | 381 | 375 | 375 | 44 | 43 | 18 | `[10, 5, 4, 3, 2, 2, 2, 2, 2, 2, 2, 1, ... (18 clusters)]` |
| 50ETF | single | 985 | 182 | 110 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | - | `-` |
| 500ETF | single | 4,744 | 1,991 | 1,549 | 1,401 | 1,401 | 1,338 | 920 | 920 | 56 | 56 | 31 | `[4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (31 clusters)]` |
| 159915ETF | single | 2,974 | 1,024 | 778 | 683 | 680 | 568 | 476 | 476 | 146 | 146 | 62 | `[9, 7, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, ... (62 clusters)]` |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 43 | 18 | `[10, 5, 4, 3, 2, 2, 2, 2, 2, 2, 2, 1, ... (18 clusters)]` | +0.1148 | [+0.0682, +0.1606] | +0.2401 | [+0.1389, +0.3367] | +0.8667 | 5.67% | 1.5899 | 4.05% | 1.1562 | 2.5212 | 2.71% |
| 500ETF | single | 56 | 31 | `[4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (31 clusters)]` | +0.1463 | [+0.1023, +0.1896] | +0.2452 | [+0.1505, +0.3423] | +0.8788 | 7.51% | 1.6539 | 5.91% | 1.3190 | 2.6892 | 4.10% |
| 159915ETF | single | 146 | 62 | `[9, 7, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, ... (62 clusters)]` | +0.1566 | [+0.1169, +0.2043] | +0.3324 | [+0.2410, +0.4119] | +0.8424 | 9.69% | 1.9217 | 8.10% | 1.6285 | 4.0330 | 3.18% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 43 | 18 | `[10, 5, 4, 3, 2, 2, 2, 2, 2, 2, 2, 1, ... (18 clusters)]` | -0.1039* | [-0.3705, +0.0988] | -0.0113* | [-0.5887, +0.4052] | -0.2970 | -0.34% | -0.1175 | -1.80% | -0.6131 | -0.7482 | 2.85% |
| 500ETF | single | 56 | 31 | `[4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (31 clusters)]` | +0.0333* | [-0.1495, +0.1420] | -0.0696* | [-0.5263, +0.2027] | +0.0667 | -0.43% | -0.0950 | -1.91% | -0.4240 | -0.5594 | 4.13% |
| 159915ETF | single | 146 | 62 | `[9, 7, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, ... (62 clusters)]` | +0.0574* | [-0.2179, +0.2672] | -0.0687* | [-0.5679, +0.3513] | +0.2606 | -0.46% | -0.0874 | -1.84% | -0.3526 | -0.4694 | 4.59% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Clusters | Cluster Sizes | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1074 | +0.2637 | +0.2645 | 0.0000 | +0.7047 | +0.7477 | 0.000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 10 | +1 | +0.1039 | +0.2621 | +0.2635 | 0.0000 | +0.7588 | +0.7724 | 0.875 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Cluster 10 | +1 | +0.1034 | +0.2501 | +0.2501 | 0.0000 | +0.8571 | +0.8208 | 0.843 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | Cluster 10 | +1 | +0.1074 | +0.2454 | +0.2463 | 0.0000 | +0.7545 | +0.7621 | 0.924 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 10 | +1 | +0.0923 | +0.2353 | +0.2367 | 0.0000 | +0.6402 | +0.7436 | 0.944 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 3 | +1 | +0.0944 | +0.2303 | +0.2293 | 0.0000 | +0.8055 | +0.7858 | 0.911 |
| `combo_rank_max__max_up_ret__first_bar_return` | Cluster 7 | +1 | +0.0937 | +0.2301 | +0.2290 | 0.0000 | +0.7485 | +0.7559 | 0.883 |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 5 | +1 | +0.0996 | +0.2286 | +0.2282 | 0.0000 | +0.7092 | +0.7775 | 0.939 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 13 | +1 | +0.1002 | +0.2257 | +0.2261 | 0.0000 | +0.5684 | +0.7127 | 0.858 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Cluster 13 | +1 | +0.0851 | +0.2251 | +0.2262 | 0.0000 | +0.7366 | +0.7930 | 0.901 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Cluster 14 | +1 | +0.0961 | +0.2233 | +0.2238 | 0.0000 | +0.7261 | +0.7868 | 0.938 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Cluster 5 | +1 | +0.1008 | +0.2218 | +0.2214 | 0.0000 | +0.7626 | +0.7533 | 0.747 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | Cluster 0 | +1 | +0.1062 | +0.2207 | +0.2206 | 0.0000 | +0.6462 | +0.7219 | 0.838 |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Cluster 15 | +1 | +0.0942 | +0.2207 | +0.2205 | 0.0000 | +0.6285 | +0.7188 | 0.927 |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | Cluster 4 | +1 | +0.0985 | +0.2195 | +0.2191 | 0.0000 | +0.6511 | +0.7255 | 0.928 |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 10 | +1 | +0.1095 | +0.2192 | +0.2193 | 0.0000 | +0.6639 | +0.7152 | 0.939 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 8 | +1 | +0.1005 | +0.2166 | +0.2163 | 0.0000 | +0.7013 | +0.7570 | 0.956 |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 0 | +1 | +0.1125 | +0.2165 | +0.2165 | 0.0000 | +0.6151 | +0.6926 | 0.916 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1018 | +0.2156 | +0.2157 | 0.0000 | +0.5675 | +0.7420 | 0.940 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 0 | +1 | +0.0876 | +0.2146 | +0.2147 | 0.0000 | +0.5939 | +0.7523 | 0.923 |
| `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Cluster 14 | +1 | +0.0943 | +0.2144 | +0.2143 | 0.0000 | +0.6681 | +0.7745 | 0.937 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Cluster 16 | +1 | +0.0867 | +0.2138 | +0.2139 | 0.0000 | +0.7377 | +0.7678 | 0.872 |
| `combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum` | Cluster 17 | +1 | +0.0881 | +0.2124 | +0.2122 | 0.0000 | +0.6006 | +0.6982 | 0.872 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 10 | +1 | +0.0913 | +0.2116 | +0.2114 | 0.0000 | +0.5574 | +0.7137 | 0.948 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 10 | +1 | +0.0963 | +0.2113 | +0.2119 | 0.0000 | +0.5218 | +0.7147 | 0.945 |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | Cluster 15 | +1 | +0.0911 | +0.2113 | +0.2111 | 0.0000 | +0.5991 | +0.7271 | 0.942 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Cluster 10 | +1 | +0.0981 | +0.2084 | +0.2089 | 0.0000 | +0.5112 | +0.7065 | 0.805 |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Cluster 11 | +1 | +0.0886 | +0.2063 | +0.2057 | 0.0000 | +0.6074 | +0.7575 | 0.846 |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0` | Cluster 8 | +1 | +0.1065 | +0.2060 | +0.2059 | 0.0000 | +0.6044 | +0.7225 | 0.931 |
| `combo_mean__max_up_ret__morning_volume_weighted_momentum` | Cluster 1 | +1 | +0.0824 | +0.2059 | +0.2050 | 0.0000 | +0.7048 | +0.7611 | 0.876 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 3 | +1 | +0.0882 | +0.2038 | +0.2027 | 0.0000 | +0.9050 | +0.8234 | 0.900 |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | Cluster 6 | +1 | +0.0886 | +0.2037 | +0.2023 | 0.0000 | +0.6964 | +0.7364 | 0.899 |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | Cluster 15 | +1 | +0.0962 | +0.2017 | +0.2015 | 0.0000 | +0.6739 | +0.7487 | 0.911 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 2 | +1 | +0.0897 | +0.2011 | +0.2011 | 0.0000 | +0.6797 | +0.7554 | 0.874 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | Cluster 0 | +1 | +0.1017 | +0.2000 | +0.1999 | 0.0000 | +0.7136 | +0.7765 | 0.923 |
| `combo_rank_max__first_bar_return__morning_volume_weighted_momentum` | Cluster 6 | +1 | +0.0885 | +0.1982 | +0.1969 | 0.0000 | +0.6470 | +0.7420 | 0.934 |
| `combo_rank_max__first_bar_return__bar_body_rng_0` | Cluster 16 | +1 | +0.0936 | +0.1979 | +0.1979 | 0.0000 | +0.5846 | +0.7194 | 0.899 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 11 | +1 | +0.0937 | +0.1968 | +0.1971 | 0.0000 | +0.6028 | +0.7188 | 0.802 |
| `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Cluster 11 | +1 | +0.0910 | +0.1962 | +0.1952 | 0.0000 | +0.7457 | +0.7389 | 0.891 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 11 | +1 | +0.0918 | +0.1943 | +0.1946 | 0.0000 | +0.5187 | +0.6849 | 0.851 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Cluster 11 | +1 | +0.0871 | +0.1909 | +0.1902 | 0.0002 | +0.5697 | +0.7312 | 0.896 |
| `combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position` | Cluster 12 | +1 | +0.0771 | +0.1817 | +0.1814 | 0.0004 | +0.6709 | +0.7338 | 0.720 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 9 | +1 | +0.0917 | +0.1705 | +0.1703 | 0.0010 | +0.5429 | +0.6921 | 0.937 |

### 50ETF / single
No features admitted.

### 500ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | Cluster 25 | +1 | +0.1375 | +0.2920 | +0.2912 | 0.0000 | +0.6797 | +0.7384 | 0.000 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Cluster 14 | +1 | +0.1459 | +0.2776 | +0.2782 | 0.0000 | +0.7123 | +0.7518 | 0.693 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 22 | +1 | +0.1146 | +0.2590 | +0.2585 | 0.0000 | +0.8054 | +0.7503 | 0.727 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | Cluster 21 | +1 | +0.1325 | +0.2573 | +0.2569 | 0.0000 | +0.8883 | +0.8084 | 0.903 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 21 | +1 | +0.1302 | +0.2566 | +0.2568 | 0.0000 | +0.9224 | +0.8054 | 0.919 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 29 | +1 | +0.1220 | +0.2533 | +0.2535 | 0.0000 | +0.6544 | +0.7291 | 0.898 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 29 | +1 | +0.1281 | +0.2531 | +0.2531 | 0.0000 | +0.7343 | +0.7590 | 0.841 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 28 | +1 | +0.1178 | +0.2444 | +0.2450 | 0.0000 | +0.6889 | +0.7188 | 0.920 |
| `combo_min__net_volume_flow__first_bar_return` | Cluster 23 | +1 | +0.1136 | +0.2435 | +0.2432 | 0.0000 | +0.7199 | +0.7472 | 0.906 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 9 | +1 | +0.1355 | +0.2417 | +0.2420 | 0.0000 | +0.5960 | +0.6900 | 0.780 |
| `combo_mean__bar_ret_0__close_vs_open_range` | Cluster 1 | +1 | +0.1231 | +0.2414 | +0.2405 | 0.0000 | +0.8610 | +0.7945 | 0.877 |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | Cluster 15 | +1 | +0.1175 | +0.2411 | +0.2397 | 0.0000 | +0.7343 | +0.7925 | 0.853 |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | Cluster 15 | +1 | +0.1202 | +0.2402 | +0.2390 | 0.0000 | +0.7762 | +0.7492 | 0.928 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 9 | +1 | +0.1267 | +0.2390 | +0.2395 | 0.0000 | +0.5499 | +0.7008 | 0.909 |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Cluster 14 | +1 | +0.1156 | +0.2389 | +0.2402 | 0.0000 | +0.5302 | +0.7019 | 0.877 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Cluster 6 | +1 | +0.1033 | +0.2348 | +0.2340 | 0.0000 | +0.6755 | +0.7307 | 0.904 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | Cluster 18 | +1 | +0.1307 | +0.2328 | +0.2321 | 0.0000 | +0.7605 | +0.7770 | 0.833 |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 6 | +1 | +0.1026 | +0.2320 | +0.2306 | 0.0000 | +0.7232 | +0.7652 | 0.942 |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | Cluster 1 | +1 | +0.1335 | +0.2298 | +0.2291 | 0.0000 | +0.6426 | +0.7523 | 0.946 |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 7 | +1 | +0.1328 | +0.2287 | +0.2284 | 0.0000 | +0.6861 | +0.7374 | 0.910 |
| `combo_mean__first_bar_return__max_down_ret` | Cluster 30 | +1 | +0.1162 | +0.2258 | +0.2255 | 0.0000 | +0.7365 | +0.7461 | 0.904 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Cluster 4 | +1 | +0.1146 | +0.2253 | +0.2248 | 0.0000 | +0.7132 | +0.7523 | 0.928 |
| `combo_rank_min__net_volume_flow__bar_body_rng_0` | Cluster 23 | +1 | +0.1127 | +0.2253 | +0.2246 | 0.0000 | +0.5509 | +0.7178 | 0.922 |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | Cluster 10 | +1 | +0.1080 | +0.2248 | +0.2233 | 0.0000 | +0.7471 | +0.7657 | 0.840 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Cluster 6 | +1 | +0.1140 | +0.2243 | +0.2234 | 0.0000 | +0.6757 | +0.7631 | 0.906 |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Cluster 24 | +1 | +0.0702 | +0.2234 | +0.2223 | 0.0000 | +0.6670 | +0.7503 | 0.885 |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | Cluster 10 | +1 | +0.1057 | +0.2229 | +0.2221 | 0.0000 | +0.6095 | +0.7183 | 0.912 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | Cluster 18 | +1 | +0.1382 | +0.2228 | +0.2222 | 0.0000 | +0.8033 | +0.7750 | 0.923 |
| `combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0` | Cluster 0 | +1 | +0.1214 | +0.2227 | +0.2222 | 0.0000 | +0.7281 | +0.7508 | 0.943 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Cluster 17 | +1 | +0.1411 | +0.2205 | +0.2202 | 0.0000 | +0.8067 | +0.7894 | 0.918 |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | Cluster 2 | +1 | +0.1213 | +0.2197 | +0.2186 | 0.0000 | +0.6628 | +0.7158 | 0.925 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Cluster 19 | +1 | +0.1355 | +0.2192 | +0.2184 | 0.0000 | +0.7046 | +0.7755 | 0.903 |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | Cluster 2 | +1 | +0.1257 | +0.2187 | +0.2177 | 0.0000 | +0.6779 | +0.7327 | 0.933 |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | Cluster 25 | +1 | +0.1346 | +0.2185 | +0.2175 | 0.0000 | +0.6312 | +0.7564 | 0.935 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Cluster 12 | +1 | +0.1313 | +0.2178 | +0.2170 | 0.0000 | +0.6852 | +0.7667 | 0.881 |
| `combo_min__first_bar_return__bar_body_rng_0` | Cluster 27 | +1 | +0.1138 | +0.2178 | +0.2175 | 0.0000 | +0.6726 | +0.7405 | 0.896 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Cluster 29 | +1 | +0.1055 | +0.2157 | +0.2156 | 0.0000 | +0.5416 | +0.6782 | 0.938 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 16 | +1 | +0.1404 | +0.2152 | +0.2149 | 0.0000 | +0.6584 | +0.7441 | 0.924 |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | Cluster 23 | +1 | +0.1053 | +0.2151 | +0.2143 | 0.0000 | +0.6987 | +0.7389 | 0.946 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Cluster 18 | +1 | +0.1329 | +0.2149 | +0.2142 | 0.0000 | +0.6844 | +0.7358 | 0.945 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Cluster 8 | +1 | +0.1183 | +0.2094 | +0.2094 | 0.0000 | +0.5239 | +0.6725 | 0.913 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 4 | +1 | +0.1109 | +0.2092 | +0.2085 | 0.0000 | +0.5389 | +0.6833 | 0.899 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Cluster 9 | +1 | +0.1260 | +0.2085 | +0.2090 | 0.0000 | +0.4883 | +0.6766 | 0.940 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 7 | +1 | +0.1425 | +0.2031 | +0.2029 | 0.0000 | +0.7098 | +0.7858 | 0.906 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | Cluster 1 | +1 | +0.1224 | +0.2029 | +0.2020 | 0.0000 | +0.5552 | +0.7091 | 0.946 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Cluster 12 | +1 | +0.1217 | +0.2013 | +0.2009 | 0.0000 | +0.5470 | +0.7122 | 0.876 |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Cluster 6 | +1 | +0.0880 | +0.2011 | +0.1999 | 0.0000 | +0.4962 | +0.6833 | 0.938 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 17 | +1 | +0.1438 | +0.1953 | +0.1954 | 0.0000 | +0.6094 | +0.7049 | 0.925 |
| `combo_mean__max_up_ret__max_down_ret` | Cluster 3 | +1 | +0.1296 | +0.1869 | +0.1868 | 0.0000 | +0.6077 | +0.6952 | 0.929 |
| `combo_max__bar_ret_0__max_down_ret` | Cluster 30 | +1 | +0.1206 | +0.1859 | +0.1860 | 0.0000 | +0.6664 | +0.7590 | 0.927 |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | Cluster 5 | +1 | +0.1115 | +0.1847 | +0.1849 | 0.0000 | +0.7011 | +0.7384 | 0.801 |
| `combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend` | Cluster 26 | +1 | +0.0965 | +0.1839 | +0.1821 | 0.0000 | +0.6675 | +0.7585 | 0.858 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | Cluster 20 | +1 | +0.1038 | +0.1750 | +0.1753 | 0.0000 | +0.7182 | +0.7590 | 0.772 |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | Cluster 13 | +1 | +0.0911 | +0.1737 | +0.1729 | 0.0000 | +0.6807 | +0.7467 | 0.842 |
| `morning_volume_weighted_momentum` | Cluster 11 | +1 | +0.1111 | +0.1720 | +0.1705 | 0.0002 | +0.5776 | +0.7055 | 0.897 |
| `combo_sig_product__early_body_momentum__vwap_close_divergence_trend` | Cluster 13 | +1 | +0.0970 | +0.1710 | +0.1704 | 0.0002 | +0.6756 | +0.7513 | 0.949 |

### 159915ETF / single

| Feature | Cluster | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1574 | +0.3748 | +0.3754 | 0.0000 | +1.2328 | +0.8847 | 0.000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1565 | +0.3521 | +0.3534 | 0.0000 | +1.0413 | +0.8527 | 0.921 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 0 | +1 | +0.1510 | +0.3411 | +0.3412 | 0.0000 | +0.9988 | +0.8357 | 0.864 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1550 | +0.3351 | +0.3365 | 0.0000 | +1.0177 | +0.8316 | 0.940 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 3 | +1 | +0.1487 | +0.3339 | +0.3340 | 0.0000 | +1.1165 | +0.8527 | 0.838 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Cluster 3 | +1 | +0.1520 | +0.3325 | +0.3324 | 0.0000 | +1.1207 | +0.8666 | 0.933 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 56 | +1 | +0.1422 | +0.3231 | +0.3239 | 0.0000 | +1.0138 | +0.8347 | 0.753 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Cluster 56 | +1 | +0.1291 | +0.3107 | +0.3113 | 0.0000 | +1.0199 | +0.8239 | 0.867 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Cluster 3 | +1 | +0.1503 | +0.3099 | +0.3100 | 0.0000 | +1.0027 | +0.8424 | 0.917 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Cluster 10 | +1 | +0.1436 | +0.3076 | +0.3077 | 0.0000 | +0.8715 | +0.7884 | 0.941 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Cluster 0 | +1 | +0.1535 | +0.3045 | +0.3047 | 0.0000 | +0.8626 | +0.8007 | 0.915 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 10 | +1 | +0.1296 | +0.3014 | +0.3022 | 0.0000 | +0.8297 | +0.7894 | 0.947 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 61 | +1 | +0.1423 | +0.2982 | +0.2982 | 0.0000 | +0.9595 | +0.8491 | 0.880 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | Cluster 48 | +1 | +0.1163 | +0.2951 | +0.2959 | 0.0000 | +0.8378 | +0.7832 | 0.850 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 10 | +1 | +0.1403 | +0.2943 | +0.2957 | 0.0000 | +1.1038 | +0.8646 | 0.943 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Cluster 42 | +1 | +0.1213 | +0.2879 | +0.2881 | 0.0000 | +0.8411 | +0.7750 | 0.822 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Cluster 1 | +1 | +0.1387 | +0.2873 | +0.2878 | 0.0000 | +0.8460 | +0.7719 | 0.923 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | Cluster 10 | +1 | +0.1243 | +0.2872 | +0.2881 | 0.0000 | +0.8954 | +0.8352 | 0.880 |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 16 | +1 | +0.1187 | +0.2868 | +0.2873 | 0.0000 | +0.6637 | +0.7487 | 0.925 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 61 | +1 | +0.1373 | +0.2851 | +0.2849 | 0.0000 | +0.8684 | +0.8275 | 0.943 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Cluster 0 | +1 | +0.1448 | +0.2831 | +0.2836 | 0.0000 | +0.8263 | +0.8012 | 0.949 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Cluster 48 | +1 | +0.1267 | +0.2807 | +0.2813 | 0.0000 | +0.6932 | +0.7920 | 0.878 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Cluster 17 | +1 | +0.1249 | +0.2801 | +0.2805 | 0.0000 | +0.8505 | +0.8002 | 0.931 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Cluster 10 | +1 | +0.1447 | +0.2787 | +0.2803 | 0.0000 | +0.8794 | +0.8002 | 0.946 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 16 | +1 | +0.1382 | +0.2780 | +0.2786 | 0.0000 | +0.6382 | +0.7456 | 0.931 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Cluster 12 | +1 | +0.1336 | +0.2775 | +0.2775 | 0.0000 | +0.8686 | +0.7781 | 0.856 |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Cluster 4 | +1 | +0.1362 | +0.2724 | +0.2722 | 0.0000 | +0.5673 | +0.7122 | 0.861 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Cluster 14 | +1 | +0.1378 | +0.2722 | +0.2726 | 0.0000 | +0.8345 | +0.7657 | 0.937 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 45 | +1 | +0.1319 | +0.2639 | +0.2637 | 0.0000 | +0.8780 | +0.8229 | 0.824 |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | Cluster 57 | +1 | +0.1102 | +0.2634 | +0.2638 | 0.0000 | +0.7562 | +0.7688 | 0.866 |
| `opening_drive_thrust_ratio` | Cluster 20 | +1 | +0.1290 | +0.2628 | +0.2631 | 0.0000 | +0.9151 | +0.7894 | 0.932 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Cluster 5 | +1 | +0.1415 | +0.2595 | +0.2603 | 0.0000 | +0.7986 | +0.7848 | 0.908 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Cluster 23 | +1 | +0.1457 | +0.2591 | +0.2590 | 0.0000 | +0.8872 | +0.8012 | 0.890 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 60 | +1 | +0.1058 | +0.2588 | +0.2591 | 0.0000 | +0.8061 | +0.8023 | 0.898 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Cluster 27 | +1 | +0.1416 | +0.2583 | +0.2583 | 0.0000 | +0.7807 | +0.7817 | 0.898 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 20 | +1 | +0.1139 | +0.2567 | +0.2567 | 0.0000 | +0.8420 | +0.8223 | 0.922 |
| `combo_mean__volume_weighted_price_position__limit_down_proximity_early` | Cluster 58 | +1 | +0.1221 | +0.2565 | +0.2561 | 0.0000 | +0.7651 | +0.7698 | 0.926 |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | Cluster 10 | +1 | +0.1314 | +0.2564 | +0.2564 | 0.0000 | +0.7304 | +0.7868 | 0.941 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 13 | +1 | +0.1272 | +0.2562 | +0.2565 | 0.0000 | +0.7015 | +0.7775 | 0.938 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Cluster 23 | +1 | +0.1257 | +0.2554 | +0.2557 | 0.0000 | +1.0492 | +0.8254 | 0.940 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | Cluster 7 | +1 | +0.1317 | +0.2553 | +0.2552 | 0.0000 | +0.5794 | +0.7472 | 0.809 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Cluster 23 | +1 | +0.1332 | +0.2532 | +0.2535 | 0.0000 | +0.7679 | +0.7533 | 0.904 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Cluster 27 | +1 | +0.1411 | +0.2512 | +0.2511 | 0.0000 | +0.7922 | +0.7956 | 0.900 |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Cluster 46 | +1 | +0.1196 | +0.2485 | +0.2488 | 0.0000 | +0.6357 | +0.7070 | 0.838 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Cluster 21 | +1 | +0.1279 | +0.2483 | +0.2487 | 0.0000 | +0.8969 | +0.8038 | 0.922 |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Cluster 45 | +1 | +0.1321 | +0.2481 | +0.2479 | 0.0000 | +0.7927 | +0.7842 | 0.892 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Cluster 46 | +1 | +0.1188 | +0.2475 | +0.2477 | 0.0000 | +0.6557 | +0.7266 | 0.919 |
| `combo_min__max_up_ret__bar_body_rng_0` | Cluster 15 | +1 | +0.1259 | +0.2465 | +0.2477 | 0.0000 | +0.6445 | +0.7549 | 0.928 |
| `combo_max__opening_drive_thrust_ratio__rally_strength_max` | Cluster 26 | +1 | +0.1172 | +0.2462 | +0.2465 | 0.0000 | +0.6088 | +0.6771 | 0.897 |
| `combo_max__max_up_ret__volume_price_confirmation` | Cluster 54 | +1 | +0.1236 | +0.2441 | +0.2442 | 0.0000 | +0.7413 | +0.7369 | 0.909 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1159 | +0.2440 | +0.2438 | 0.0000 | +0.7524 | +0.8162 | 0.913 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | Cluster 5 | +1 | +0.1305 | +0.2440 | +0.2451 | 0.0000 | +0.6689 | +0.7683 | 0.856 |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | Cluster 26 | +1 | +0.1128 | +0.2430 | +0.2428 | 0.0000 | +0.7648 | +0.7796 | 0.898 |
| `combo_mean__max_up_ret__rally_strength_max` | Cluster 26 | +1 | +0.1134 | +0.2426 | +0.2427 | 0.0000 | +0.7005 | +0.7405 | 0.871 |
| `combo_max__bar_body_rng_0__rally_strength_max` | Cluster 41 | +1 | +0.1090 | +0.2422 | +0.2424 | 0.0000 | +0.5829 | +0.6946 | 0.854 |
| `combo_max__max_up_ret__bar_body_rng_0` | Cluster 12 | +1 | +0.1336 | +0.2417 | +0.2416 | 0.0000 | +0.8184 | +0.7575 | 0.943 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 2 | +1 | +0.1383 | +0.2416 | +0.2424 | 0.0000 | +0.6953 | +0.7564 | 0.919 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Cluster 58 | +1 | +0.1484 | +0.2412 | +0.2410 | 0.0000 | +0.8329 | +0.7770 | 0.832 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 34 | +1 | +0.1025 | +0.2406 | +0.2403 | 0.0000 | +0.6260 | +0.7451 | 0.460 |
| `combo_max__max_up_ret__rally_strength_max` | Cluster 26 | +1 | +0.1060 | +0.2401 | +0.2402 | 0.0000 | +0.5999 | +0.6957 | 0.943 |
| `combo_mean__bar_body_rng_0__rally_strength_max` | Cluster 44 | +1 | +0.1166 | +0.2393 | +0.2395 | 0.0000 | +0.7189 | +0.7487 | 0.937 |
| `combo_rank_min__bar_body_rng_0__rally_strength_max` | Cluster 44 | +1 | +0.1134 | +0.2386 | +0.2389 | 0.0000 | +0.9022 | +0.7827 | 0.902 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Cluster 2 | +1 | +0.1368 | +0.2372 | +0.2381 | 0.0000 | +0.7516 | +0.7837 | 0.948 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Cluster 14 | +1 | +0.1328 | +0.2371 | +0.2371 | 0.0000 | +0.6596 | +0.7255 | 0.947 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | Cluster 50 | +1 | +0.1335 | +0.2371 | +0.2377 | 0.0000 | +0.4211 | +0.6756 | 0.869 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 4 | +1 | +0.1315 | +0.2369 | +0.2367 | 0.0000 | +0.8296 | +0.7544 | 0.918 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Cluster 19 | +1 | +0.1278 | +0.2368 | +0.2369 | 0.0000 | +0.5973 | +0.7173 | 0.912 |
| `combo_rank_min__max_up_ret__gap_pct` | Cluster 9 | +1 | +0.1185 | +0.2344 | +0.2350 | 0.0000 | +0.6240 | +0.7461 | 0.876 |
| `combo_mean__volatility_expansion_trend_vector__rally_strength_max` | Cluster 26 | +1 | +0.1007 | +0.2340 | +0.2339 | 0.0000 | +0.7223 | +0.7801 | 0.918 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 59 | +1 | +0.1408 | +0.2337 | +0.2336 | 0.0000 | +0.7113 | +0.7554 | 0.894 |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 60 | +1 | +0.1038 | +0.2335 | +0.2340 | 0.0000 | +0.7030 | +0.7611 | 0.882 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1215 | +0.2332 | +0.2339 | 0.0000 | +0.7936 | +0.7667 | 0.922 |
| `combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0` | Cluster 38 | +1 | +0.1123 | +0.2318 | +0.2318 | 0.0000 | +0.6077 | +0.7250 | 0.894 |
| `combo_mean__rally_strength_max__volume_price_confirmation` | Cluster 43 | +1 | +0.1045 | +0.2288 | +0.2290 | 0.0000 | +0.5061 | +0.6756 | 0.918 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Cluster 47 | +1 | +0.1385 | +0.2279 | +0.2280 | 0.0000 | +0.5297 | +0.6874 | 0.887 |
| `combo_mean__max_up_ret__gap_pct` | Cluster 30 | +1 | +0.1572 | +0.2274 | +0.2271 | 0.0000 | +0.5852 | +0.7080 | 0.845 |
| `bar_body_rng_0` | Cluster 35 | +1 | +0.1231 | +0.2273 | +0.2279 | 0.0000 | +0.5838 | +0.7152 | 0.893 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | Cluster 17 | +1 | +0.1276 | +0.2264 | +0.2270 | 0.0000 | +0.6875 | +0.7559 | 0.910 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Cluster 19 | +1 | +0.1294 | +0.2261 | +0.2260 | 0.0000 | +0.6052 | +0.6982 | 0.852 |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | Cluster 54 | +1 | +0.1224 | +0.2259 | +0.2266 | 0.0000 | +0.5965 | +0.7137 | 0.904 |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | Cluster 54 | +1 | +0.1206 | +0.2257 | +0.2258 | 0.0000 | +0.5874 | +0.7065 | 0.930 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Cluster 22 | +1 | +0.1223 | +0.2254 | +0.2264 | 0.0000 | +0.8243 | +0.7915 | 0.931 |
| `combo_rank_min__rally_strength_max__volume_price_confirmation` | Cluster 43 | +1 | +0.0982 | +0.2254 | +0.2252 | 0.0000 | +0.5846 | +0.7291 | 0.876 |
| `combo_mean__volatility_expansion_trend_vector__directional_volume_signature` | Cluster 51 | +1 | +0.1062 | +0.2253 | +0.2255 | 0.0000 | +0.8351 | +0.7765 | 0.907 |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0` | Cluster 38 | +1 | +0.1120 | +0.2246 | +0.2251 | 0.0000 | +0.5845 | +0.7158 | 0.903 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | Cluster 25 | +1 | +0.1160 | +0.2239 | +0.2244 | 0.0002 | +0.7120 | +0.7714 | 0.943 |
| `combo_max__max_up_ret__directional_volume_signature` | Cluster 53 | +1 | +0.1056 | +0.2235 | +0.2233 | 0.0002 | +0.7346 | +0.7626 | 0.914 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Cluster 24 | +1 | +0.1177 | +0.2232 | +0.2238 | 0.0002 | +0.6886 | +0.7312 | 0.942 |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | Cluster 15 | +1 | +0.1288 | +0.2224 | +0.2232 | 0.0002 | +0.7171 | +0.7817 | 0.950 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Cluster 24 | +1 | +0.1191 | +0.2223 | +0.2230 | 0.0002 | +0.9772 | +0.8234 | 0.910 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Cluster 34 | +1 | +0.1173 | +0.2178 | +0.2171 | 0.0002 | +0.5604 | +0.7338 | 0.769 |
| `combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration` | Cluster 42 | +1 | +0.1131 | +0.2175 | +0.2176 | 0.0002 | +0.4764 | +0.6807 | 0.887 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | Cluster 8 | +1 | +0.1295 | +0.2170 | +0.2173 | 0.0002 | +0.6703 | +0.7178 | 0.866 |
| `combo_mean__max_up_ret__volume_price_confirmation` | Cluster 54 | +1 | +0.1233 | +0.2166 | +0.2172 | 0.0002 | +0.5960 | +0.7080 | 0.944 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | Cluster 33 | +1 | +0.1056 | +0.2163 | +0.2154 | 0.0002 | +0.4453 | +0.6601 | 0.649 |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | Cluster 49 | +1 | +0.0963 | +0.2159 | +0.2161 | 0.0002 | +0.6442 | +0.7286 | 0.874 |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | Cluster 9 | +1 | +0.1091 | +0.2111 | +0.2116 | 0.0002 | +0.3936 | +0.6761 | 0.696 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | Cluster 6 | +1 | +0.1238 | +0.2108 | +0.2101 | 0.0002 | +0.4595 | +0.7214 | 0.843 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Cluster 25 | +1 | +0.1184 | +0.2099 | +0.2097 | 0.0002 | +0.6855 | +0.7678 | 0.884 |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1255 | +0.2098 | +0.2088 | 0.0002 | +0.4964 | +0.6648 | 0.856 |
| `combo_z_sum__max_up_ret__directional_volume_signature` | Cluster 51 | +1 | +0.1134 | +0.2093 | +0.2096 | 0.0002 | +0.6050 | +0.7178 | 0.942 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | Cluster 50 | +1 | +0.1386 | +0.2086 | +0.2093 | 0.0002 | +0.4569 | +0.6880 | 0.895 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | Cluster 55 | +1 | +0.1138 | +0.2075 | +0.2076 | 0.0002 | +0.6499 | +0.7364 | 0.825 |
| `combo_rank_max__max_up_ret__directional_volume_signature` | Cluster 53 | +1 | +0.1055 | +0.2061 | +0.2061 | 0.0002 | +0.5830 | +0.7307 | 0.919 |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | Cluster 37 | +1 | +0.1155 | +0.2055 | +0.2056 | 0.0002 | +0.5435 | +0.7183 | 0.878 |
| `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation` | Cluster 47 | +1 | +0.1118 | +0.2052 | +0.2052 | 0.0002 | +0.4572 | +0.6622 | 0.927 |
| `combo_clamp_diff__first_bar_return__volume_weighted_momentum_acceleration` | Cluster 36 | +1 | +0.1205 | +0.2051 | +0.2057 | 0.0002 | +0.4509 | +0.6586 | 0.896 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | Cluster 34 | +1 | +0.1071 | +0.2047 | +0.2040 | 0.0002 | +0.4545 | +0.6838 | 0.788 |
| `combo_rank_min__max_up_ret__rally_strength_max` | Cluster 26 | +1 | +0.1121 | +0.2045 | +0.2046 | 0.0002 | +0.6349 | +0.7770 | 0.899 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1298 | +0.2041 | +0.2031 | 0.0002 | +0.4910 | +0.6586 | 0.856 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Cluster 59 | +1 | +0.1206 | +0.2039 | +0.2039 | 0.0002 | +0.7588 | +0.7827 | 0.935 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | Cluster 33 | +1 | +0.1109 | +0.2037 | +0.2029 | 0.0002 | +0.5081 | +0.6689 | 0.862 |
| `combo_min__max_up_ret__volume_weighted_price_position` | Cluster 42 | +1 | +0.1148 | +0.2037 | +0.2043 | 0.0002 | +0.5025 | +0.6880 | 0.930 |
| `combo_max__first_bar_return__rally_strength_max` | Cluster 41 | +1 | +0.1049 | +0.2035 | +0.2038 | 0.0002 | +0.5339 | +0.7024 | 0.911 |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | Cluster 24 | +1 | +0.1066 | +0.2014 | +0.2021 | 0.0002 | +0.6234 | +0.7379 | 0.863 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Cluster 13 | +1 | +0.1238 | +0.1980 | +0.1983 | 0.0002 | +0.5723 | +0.6787 | 0.942 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Cluster 28 | +1 | +0.1286 | +0.1980 | +0.1967 | 0.0002 | +0.6311 | +0.7173 | 0.913 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return` | Cluster 40 | +1 | +0.0876 | +0.1971 | +0.1982 | 0.0002 | +0.6557 | +0.7111 | 0.920 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Cluster 30 | +1 | +0.1295 | +0.1943 | +0.1942 | 0.0002 | +0.7027 | +0.7261 | 0.902 |
| `combo_rank_min__max_up_ret__directional_volume_signature` | Cluster 52 | +1 | +0.1031 | +0.1909 | +0.1916 | 0.0002 | +0.5811 | +0.7096 | 0.886 |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | Cluster 18 | +1 | +0.1081 | +0.1906 | +0.1909 | 0.0002 | +0.7332 | +0.7389 | 0.896 |
| `combo_min__max_up_ret__rally_strength_max` | Cluster 26 | +1 | +0.1150 | +0.1903 | +0.1903 | 0.0002 | +0.5864 | +0.7250 | 0.935 |
| `combo_mean__opening_drive_thrust_ratio__directional_volume_signature` | Cluster 51 | +1 | +0.1114 | +0.1895 | +0.1898 | 0.0002 | +0.6828 | +0.7389 | 0.926 |
| `combo_mean__first_bar_return__volume_weighted_price_position` | Cluster 37 | +1 | +0.1141 | +0.1890 | +0.1896 | 0.0002 | +0.4884 | +0.6777 | 0.935 |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | Cluster 33 | +1 | +0.1098 | +0.1887 | +0.1880 | 0.0002 | +0.4490 | +0.6555 | 0.944 |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 9 | +1 | +0.1340 | +0.1881 | +0.1876 | 0.0004 | +0.4478 | +0.6612 | 0.904 |
| `combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position` | Cluster 6 | +1 | +0.1111 | +0.1870 | +0.1866 | 0.0004 | +0.5671 | +0.7281 | 0.855 |
| `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return` | Cluster 35 | +1 | +0.1197 | +0.1857 | +0.1865 | 0.0004 | +0.5688 | +0.7214 | 0.948 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Cluster 31 | +1 | +0.1295 | +0.1855 | +0.1848 | 0.0004 | +0.6302 | +0.6962 | 0.875 |
| `combo_max__volatility_expansion_trend_vector__directional_volume_signature` | Cluster 53 | +1 | +0.0998 | +0.1848 | +0.1852 | 0.0004 | +0.5419 | +0.6828 | 0.917 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | Cluster 11 | +1 | +0.0917 | +0.1846 | +0.1857 | 0.0004 | +0.5150 | +0.7060 | 0.536 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Cluster 32 | +1 | +0.1117 | +0.1832 | +0.1827 | 0.0004 | +0.5927 | +0.7137 | 0.873 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Cluster 31 | +1 | +0.1227 | +0.1827 | +0.1822 | 0.0004 | +0.5474 | +0.6746 | 0.934 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Cluster 9 | +1 | +0.1370 | +0.1815 | +0.1809 | 0.0004 | +0.4673 | +0.6751 | 0.803 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | Cluster 55 | +1 | +0.1175 | +0.1788 | +0.1791 | 0.0006 | +0.5870 | +0.6972 | 0.941 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | Cluster 40 | +1 | +0.1027 | +0.1785 | +0.1790 | 0.0006 | +0.4615 | +0.6982 | 0.744 |
| `combo_min__max_up_ret__first_bar_return` | Cluster 15 | +1 | +0.1164 | +0.1766 | +0.1781 | 0.0006 | +0.6298 | +0.7734 | 0.945 |
| `combo_rank_min__bar_body_rng_0__directional_volume_signature` | Cluster 39 | +1 | +0.1027 | +0.1760 | +0.1764 | 0.0006 | +0.5062 | +0.6807 | 0.910 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Cluster 7 | +1 | +0.1236 | +0.1753 | +0.1755 | 0.0006 | +0.5580 | +0.6900 | 0.892 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | Cluster 11 | +1 | +0.1048 | +0.1722 | +0.1726 | 0.0010 | +0.5433 | +0.6704 | 0.873 |
| `combo_max__bar_ret_0__limit_down_proximity_early` | Cluster 29 | +1 | +0.1089 | +0.1650 | +0.1643 | 0.0014 | +0.5434 | +0.7122 | 0.871 |
| `first_bar_return` | Cluster 35 | +1 | +0.1140 | +0.1648 | +0.1657 | 0.0014 | +0.6037 | +0.7297 | 0.945 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Cluster 9 | +1 | +0.1077 | +0.1643 | +0.1655 | 0.0016 | +0.3960 | +0.6529 | 0.888 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Cluster 35 | +1 | +0.1121 | +0.1642 | +0.1650 | 0.0016 | +0.5547 | +0.7338 | 0.912 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret` | Cluster 34 | +1 | +0.1083 | +0.1516 | +0.1507 | 0.0038 | +0.5931 | +0.7147 | 0.591 |
| `combo_rel_diff__bar_ret_0__volume_weighted_momentum_acceleration` | Cluster 36 | +1 | +0.1184 | +0.1408 | +0.1411 | 0.0050 | +0.4743 | +0.6509 | 0.928 |


## 5b. ONC Feature Clusters Summary

Optimal Number of Clusters (ONC) feature groupings calculated on training data.
Enforces diversity downstream (max 1 feature per cluster selected per rebalance).

### Cluster Overview per ETF / Side

| ETF | Side | Total Features | Clusters | Avg Silhouette | Cluster Sizes |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 300ETF | single | 43 | 18 | 0.2308 | `[10, 5, 4, 3, 2, 2, 2, 2, 2, 2, 2, 1, ... (18 clusters)]` |
| 500ETF | single | 56 | 31 | 0.2358 | `[4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (31 clusters)]` |
| 159915ETF | single | 146 | 62 | 0.3111 | `[9, 7, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, ... (62 clusters)]` |

### Cluster Breakdown Details

| ETF | Side | Cluster ID | Features | Silhouette | Primary Feature | Other Members |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| 300ETF | single | Cluster 0 | 4 | 0.2308 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`, `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early`, `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` |
| 300ETF | single | Cluster 1 | 1 | 0.2308 | `combo_mean__max_up_ret__morning_volume_weighted_momentum` | _(none)_ |
| 300ETF | single | Cluster 2 | 1 | 0.2308 | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | _(none)_ |
| 300ETF | single | Cluster 3 | 2 | 0.2308 | `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `combo_rank_max__max_up_ret__volume_weighted_price_position` |
| 300ETF | single | Cluster 4 | 1 | 0.2308 | `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 5 | 2 | 0.2308 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 6 | 2 | 0.2308 | `combo_max__bar_ret_0__morning_volume_weighted_momentum` | `combo_rank_max__first_bar_return__morning_volume_weighted_momentum` |
| 300ETF | single | Cluster 7 | 1 | 0.2308 | `combo_rank_max__max_up_ret__first_bar_return` | _(none)_ |
| 300ETF | single | Cluster 8 | 2 | 0.2308 | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0` |
| 300ETF | single | Cluster 9 | 1 | 0.2308 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | _(none)_ |
| 300ETF | single | Cluster 10 | 10 | 0.2308 | `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`, `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return`, `combo_min__bar_body_rng_0__limit_down_proximity_early`, `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`, `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`, `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` |
| 300ETF | single | Cluster 11 | 5 | 0.2308 | `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`, `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`, `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`, `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` |
| 300ETF | single | Cluster 12 | 1 | 0.2308 | `combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position` | _(none)_ |
| 300ETF | single | Cluster 13 | 2 | 0.2308 | `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` |
| 300ETF | single | Cluster 14 | 2 | 0.2308 | `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 15 | 3 | 0.2308 | `combo_mean__bar_body_rng_0__volume_weighted_price_position` | `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position`, `combo_rank_max__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 16 | 2 | 0.2308 | `combo_rank_max__first_bar_return__bar_body_rng_0` | `combo_ratio__first_bar_return__volume_weighted_price_position` |
| 300ETF | single | Cluster 17 | 1 | 0.2308 | `combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum` | _(none)_ |
| 500ETF | single | Cluster 0 | 1 | 0.2358 | `combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 1 | 3 | 0.2358 | `combo_mean__bar_ret_0__close_vs_open_range` | `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0`, `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` |
| 500ETF | single | Cluster 2 | 2 | 0.2358 | `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | `combo_mean__bar_ret_0__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 3 | 1 | 0.2358 | `combo_mean__max_up_ret__max_down_ret` | _(none)_ |
| 500ETF | single | Cluster 4 | 2 | 0.2358 | `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `combo_mean__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 5 | 1 | 0.2358 | `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 6 | 4 | 0.2358 | `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`, `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`, `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` |
| 500ETF | single | Cluster 7 | 2 | 0.2358 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` |
| 500ETF | single | Cluster 8 | 1 | 0.2358 | `combo_rank_min__max_up_ret__bar_body_rng_0` | _(none)_ |
| 500ETF | single | Cluster 9 | 3 | 0.2358 | `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`, `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` |
| 500ETF | single | Cluster 10 | 2 | 0.2358 | `combo_rank_max__early_order_flow_imbalance__max_down_ret` | `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` |
| 500ETF | single | Cluster 11 | 1 | 0.2358 | `morning_volume_weighted_momentum` | _(none)_ |
| 500ETF | single | Cluster 12 | 2 | 0.2358 | `combo_rank_max__max_up_ret__bar_ret_0` | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` |
| 500ETF | single | Cluster 13 | 2 | 0.2358 | `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | `combo_sig_product__early_body_momentum__vwap_close_divergence_trend` |
| 500ETF | single | Cluster 14 | 2 | 0.2358 | `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` |
| 500ETF | single | Cluster 15 | 2 | 0.2358 | `combo_min__early_order_flow_imbalance__bar_body_rng_0` | `combo_min__bar_ret_0__early_order_flow_imbalance` |
| 500ETF | single | Cluster 16 | 1 | 0.2358 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 17 | 2 | 0.2358 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 18 | 3 | 0.2358 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`, `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` |
| 500ETF | single | Cluster 19 | 1 | 0.2358 | `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 20 | 1 | 0.2358 | `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 21 | 2 | 0.2358 | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` |
| 500ETF | single | Cluster 22 | 1 | 0.2358 | `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 23 | 3 | 0.2358 | `combo_min__net_volume_flow__first_bar_return` | `combo_rank_min__net_volume_flow__bar_body_rng_0`, `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` |
| 500ETF | single | Cluster 24 | 1 | 0.2358 | `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | _(none)_ |
| 500ETF | single | Cluster 25 | 2 | 0.2358 | `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` |
| 500ETF | single | Cluster 26 | 1 | 0.2358 | `combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend` | _(none)_ |
| 500ETF | single | Cluster 27 | 1 | 0.2358 | `combo_min__first_bar_return__bar_body_rng_0` | _(none)_ |
| 500ETF | single | Cluster 28 | 1 | 0.2358 | `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | _(none)_ |
| 500ETF | single | Cluster 29 | 3 | 0.2358 | `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_min__star50_limit_proximity_early__bar_ret_0` |
| 500ETF | single | Cluster 30 | 2 | 0.2358 | `combo_mean__first_bar_return__max_down_ret` | `combo_max__bar_ret_0__max_down_ret` |
| 159915ETF | single | Cluster 0 | 3 | 0.3111 | `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`, `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` |
| 159915ETF | single | Cluster 1 | 1 | 0.3111 | `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | _(none)_ |
| 159915ETF | single | Cluster 2 | 2 | 0.3111 | `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 3 | 3 | 0.3111 | `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`, `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 4 | 2 | 0.3111 | `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 5 | 2 | 0.3111 | `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 6 | 2 | 0.3111 | `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 7 | 2 | 0.3111 | `combo_sig_product__max_up_ret__bar_body_rng_0` | `combo_sig_product__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 8 | 1 | 0.3111 | `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | _(none)_ |
| 159915ETF | single | Cluster 9 | 5 | 0.3111 | `combo_rank_min__max_up_ret__gap_pct` | `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0`, `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`, `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`, `combo_sig_product__star50_limit_proximity_early__bar_ret_0` |
| 159915ETF | single | Cluster 10 | 9 | 0.3111 | `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`, `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`, `combo_mean__star50_limit_proximity_early__bar_body_rng_0`, `combo_min__bar_body_rng_0__limit_down_proximity_early`, `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`, `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`, `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` |
| 159915ETF | single | Cluster 11 | 2 | 0.3111 | `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` |
| 159915ETF | single | Cluster 12 | 2 | 0.3111 | `combo_rank_max__max_up_ret__bar_body_rng_0` | `combo_max__max_up_ret__bar_body_rng_0` |
| 159915ETF | single | Cluster 13 | 2 | 0.3111 | `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_max__opening_drive_thrust_ratio__bar_ret_0` |
| 159915ETF | single | Cluster 14 | 2 | 0.3111 | `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` |
| 159915ETF | single | Cluster 15 | 3 | 0.3111 | `combo_min__max_up_ret__bar_body_rng_0` | `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return`, `combo_min__max_up_ret__first_bar_return` |
| 159915ETF | single | Cluster 16 | 2 | 0.3111 | `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` |
| 159915ETF | single | Cluster 17 | 2 | 0.3111 | `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | `combo_max__first_bar_return__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 18 | 1 | 0.3111 | `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | _(none)_ |
| 159915ETF | single | Cluster 19 | 2 | 0.3111 | `combo_rank_max__max_up_ret__volume_weighted_price_position` | `combo_mean__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 20 | 2 | 0.3111 | `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `opening_drive_thrust_ratio` |
| 159915ETF | single | Cluster 21 | 1 | 0.3111 | `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | _(none)_ |
| 159915ETF | single | Cluster 22 | 3 | 0.3111 | `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `combo_max__max_up_ret__volatility_expansion_trend_vector`, `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 23 | 3 | 0.3111 | `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`, `combo_min__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 24 | 3 | 0.3111 | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `combo_ratio__max_up_ret__keltner_squeeze_width`, `combo_ratio__max_up_ret__volume_weighted_price_position` |
| 159915ETF | single | Cluster 25 | 2 | 0.3111 | `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` |
| 159915ETF | single | Cluster 26 | 7 | 0.3111 | `combo_mean__max_up_ret__rally_strength_max` | `combo_mean__volatility_expansion_trend_vector__rally_strength_max`, `combo_max__max_up_ret__rally_strength_max`, `combo_rank_min__max_up_ret__rally_strength_max`, `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max`, `combo_max__opening_drive_thrust_ratio__rally_strength_max`, `combo_min__max_up_ret__rally_strength_max` |
| 159915ETF | single | Cluster 27 | 2 | 0.3111 | `combo_diff__max_up_ret__demark_setup_reversal_early` | `combo_rel_diff__max_up_ret__demark_setup_reversal_early` |
| 159915ETF | single | Cluster 28 | 3 | 0.3111 | `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`, `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 29 | 1 | 0.3111 | `combo_max__bar_ret_0__limit_down_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 30 | 2 | 0.3111 | `combo_mean__max_up_ret__gap_pct` | `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 31 | 2 | 0.3111 | `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` |
| 159915ETF | single | Cluster 32 | 1 | 0.3111 | `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 33 | 3 | 0.3111 | `combo_rel_diff__max_up_ret__keltner_squeeze_width` | `combo_diff__max_up_ret__keltner_squeeze_width`, `combo_clamp_diff__max_up_ret__keltner_squeeze_width` |
| 159915ETF | single | Cluster 34 | 4 | 0.3111 | `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`, `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early`, `combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret` |
| 159915ETF | single | Cluster 35 | 4 | 0.3111 | `bar_body_rng_0` | `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return`, `first_bar_return`, `combo_ratio__bar_ret_0__volume_weighted_price_position` |
| 159915ETF | single | Cluster 36 | 2 | 0.3111 | `combo_clamp_diff__first_bar_return__volume_weighted_momentum_acceleration` | `combo_rel_diff__bar_ret_0__volume_weighted_momentum_acceleration` |
| 159915ETF | single | Cluster 37 | 2 | 0.3111 | `combo_min__bar_body_rng_0__volume_weighted_price_position` | `combo_mean__first_bar_return__volume_weighted_price_position` |
| 159915ETF | single | Cluster 38 | 2 | 0.3111 | `combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0` | `combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0` |
| 159915ETF | single | Cluster 39 | 1 | 0.3111 | `combo_rank_min__bar_body_rng_0__directional_volume_signature` | _(none)_ |
| 159915ETF | single | Cluster 40 | 2 | 0.3111 | `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return` |
| 159915ETF | single | Cluster 41 | 2 | 0.3111 | `combo_max__bar_body_rng_0__rally_strength_max` | `combo_max__first_bar_return__rally_strength_max` |
| 159915ETF | single | Cluster 42 | 3 | 0.3111 | `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `combo_min__max_up_ret__volume_weighted_price_position`, `combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration` |
| 159915ETF | single | Cluster 43 | 2 | 0.3111 | `combo_mean__rally_strength_max__volume_price_confirmation` | `combo_rank_min__rally_strength_max__volume_price_confirmation` |
| 159915ETF | single | Cluster 44 | 2 | 0.3111 | `combo_mean__bar_body_rng_0__rally_strength_max` | `combo_rank_min__bar_body_rng_0__rally_strength_max` |
| 159915ETF | single | Cluster 45 | 2 | 0.3111 | `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` |
| 159915ETF | single | Cluster 46 | 2 | 0.3111 | `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` |
| 159915ETF | single | Cluster 47 | 2 | 0.3111 | `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation` |
| 159915ETF | single | Cluster 48 | 2 | 0.3111 | `combo_min__star50_limit_proximity_early__volume_price_confirmation` | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` |
| 159915ETF | single | Cluster 49 | 1 | 0.3111 | `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | _(none)_ |
| 159915ETF | single | Cluster 50 | 2 | 0.3111 | `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | `combo_rel_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` |
| 159915ETF | single | Cluster 51 | 3 | 0.3111 | `combo_mean__volatility_expansion_trend_vector__directional_volume_signature` | `combo_mean__opening_drive_thrust_ratio__directional_volume_signature`, `combo_z_sum__max_up_ret__directional_volume_signature` |
| 159915ETF | single | Cluster 52 | 1 | 0.3111 | `combo_rank_min__max_up_ret__directional_volume_signature` | _(none)_ |
| 159915ETF | single | Cluster 53 | 3 | 0.3111 | `combo_max__max_up_ret__directional_volume_signature` | `combo_rank_max__max_up_ret__directional_volume_signature`, `combo_max__volatility_expansion_trend_vector__directional_volume_signature` |
| 159915ETF | single | Cluster 54 | 4 | 0.3111 | `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | `combo_max__max_up_ret__volume_price_confirmation`, `combo_mean__max_up_ret__volume_price_confirmation`, `combo_rank_max__max_up_ret__volume_price_confirmation` |
| 159915ETF | single | Cluster 55 | 2 | 0.3111 | `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` |
| 159915ETF | single | Cluster 56 | 2 | 0.3111 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_min__star50_limit_proximity_early__volume_weighted_price_position` |
| 159915ETF | single | Cluster 57 | 1 | 0.3111 | `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | _(none)_ |
| 159915ETF | single | Cluster 58 | 2 | 0.3111 | `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `combo_mean__volume_weighted_price_position__limit_down_proximity_early` |
| 159915ETF | single | Cluster 59 | 2 | 0.3111 | `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 60 | 2 | 0.3111 | `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` |
| 159915ETF | single | Cluster 61 | 2 | 0.3111 | `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` |

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.

| Feature | Op | Components |
| :--- | :--- | :--- |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | `rank_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`opening_drive_thrust_ratio`, c=`first_bar_return` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_rank_max__max_up_ret__first_bar_return` | `rank_max` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_mean` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | `tri_min` | a=`max_up_ret`, b=`bar_ret_0`, c=`bar_body_rng_0` |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | `tri_min` | a=`max_up_ret`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`volume_weighted_price_position` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`limit_down_proximity_early` |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | `tri_max` | a=`first_bar_return`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return`, c=`volume_weighted_price_position` |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_mean` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | `tri_median` | a=`star50_limit_proximity_early`, b=`opening_drive_thrust_ratio`, c=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | `tri_min` | a=`first_bar_return`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | `ratio` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum` | `rank_min` | a=`bar_body_rng_0`, b=`morning_volume_weighted_momentum` |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `mean` | a=`bar_body_rng_0`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | `rank_max` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`morning_volume_weighted_momentum` |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`first_bar_return`, c=`bar_body_rng_0` |
| `combo_mean__max_up_ret__morning_volume_weighted_momentum` | `mean` | a=`max_up_ret`, b=`morning_volume_weighted_momentum` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | `max` | a=`bar_ret_0`, b=`morning_volume_weighted_momentum` |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | `mean` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__first_bar_return__morning_volume_weighted_momentum` | `rank_max` | a=`first_bar_return`, b=`morning_volume_weighted_momentum` |
| `combo_rank_max__first_bar_return__bar_body_rng_0` | `rank_max` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`morning_volume_weighted_momentum` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`morning_volume_weighted_momentum` |
| `combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position` | `tri_median` | a=`smooth_momentum_structure`, b=`bar_body_rng_0`, c=`volume_weighted_price_position` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | `clamp_diff` | a=`first_bar_return`, b=`demark_setup_reversal_early` |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`max_up_ret`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`net_volume_flow` |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_min__net_volume_flow__first_bar_return` | `min` | a=`net_volume_flow`, b=`first_bar_return` |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `rel_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_mean__bar_ret_0__close_vs_open_range` | `mean` | a=`bar_ret_0`, b=`close_vs_open_range` |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | `min` | a=`early_order_flow_imbalance`, b=`bar_body_rng_0` |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | `min` | a=`bar_ret_0`, b=`early_order_flow_imbalance` |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | `clamp_diff` | a=`max_up_ret`, b=`early_late_momentum_divergence` |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | `tri_min` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`trend_bar_close_consistency` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum`, c=`bar_ret_0` |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_mean` | a=`trend_bar_close_consistency`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | `mean` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_mean__first_bar_return__max_down_ret` | `mean` | a=`first_bar_return`, b=`max_down_ret` |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_rank_min__net_volume_flow__bar_body_rng_0` | `rank_min` | a=`net_volume_flow`, b=`bar_body_rng_0` |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | `rank_max` | a=`early_order_flow_imbalance`, b=`max_down_ret` |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`early_body_momentum` |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`shaved_bar_trend_conviction` |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | `rank_max` | a=`volatility_expansion_trend_vector`, b=`max_down_ret` |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`net_volume_flow` |
| `combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0` | `tri_min` | a=`max_up_ret`, b=`trend_day_regime_conviction`, c=`bar_ret_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_ret_0` |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | `mean` | a=`vwap_close_divergence_trend`, b=`bar_body_rng_0` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector`, c=`bar_ret_0` |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | `mean` | a=`bar_ret_0`, b=`vwap_close_divergence_trend` |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | `rel_diff` | a=`bar_ret_0`, b=`demark_setup_reversal_early` |
| `combo_rank_max__max_up_ret__bar_ret_0` | `rank_max` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_min__first_bar_return__bar_body_rng_0` | `min` | a=`first_bar_return`, b=`bar_body_rng_0` |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | `min` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | `rank_min` | a=`volatility_expansion_trend_vector`, b=`bar_ret_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`early_body_momentum` |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | `rank_min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | `diff` | a=`star50_limit_proximity_early`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | `tri_mean` | a=`max_up_ret`, b=`trend_bar_close_consistency`, c=`bar_ret_0` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`smooth_momentum_structure` |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | `tri_min` | a=`trend_bar_close_consistency`, b=`volatility_expansion_trend_vector`, c=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`bar_ret_0` |
| `combo_mean__max_up_ret__max_down_ret` | `mean` | a=`max_up_ret`, b=`max_down_ret` |
| `combo_max__bar_ret_0__max_down_ret` | `max` | a=`bar_ret_0`, b=`max_down_ret` |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_up_ret`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend` | `sig_product` | a=`early_order_flow_imbalance`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | `sig_product` | a=`max_down_ret`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | `sig_product` | a=`trend_bar_close_consistency`, b=`vwap_close_divergence_trend` |
| `combo_sig_product__early_body_momentum__vwap_close_divergence_trend` | `sig_product` | a=`early_body_momentum`, b=`vwap_close_divergence_trend` |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | `min` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | `min` | a=`star50_limit_proximity_early`, b=`volume_weighted_price_position` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, cond=`gap_pct` |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | `mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | `min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | `min` | a=`star50_limit_proximity_early`, b=`volume_price_confirmation` |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_min` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`volume_weighted_price_position` |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | `rank_min` | a=`bar_body_rng_0`, b=`limit_down_proximity_early` |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | `mean` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_price_confirmation` |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | `mean` | a=`bar_body_rng_0`, b=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_ret_0` |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | `min` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | `rank_max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | `clamp_diff` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early` |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | `tri_mean` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_body_rng_0` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | `rank_min` | a=`volume_weighted_price_position`, b=`limit_down_proximity_early` |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | `rank_min` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`rbreaker_sell_setup_proximity_early`, c=`max_up_ret` |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `min` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | `rel_diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `min` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_mean__volume_weighted_price_position__limit_down_proximity_early` | `mean` | a=`volume_weighted_price_position`, b=`limit_down_proximity_early` |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | `mean` | a=`first_bar_return`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | `min` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | `sig_product` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | `diff` | a=`max_up_ret`, b=`demark_setup_reversal_early` |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`directional_volume_signature` |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`volatility_expansion_trend_vector` |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | `min` | a=`rbreaker_sell_setup_proximity_early`, b=`rally_strength_max` |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | `rank_min` | a=`rbreaker_sell_setup_proximity_early`, b=`directional_volume_signature` |
| `combo_min__max_up_ret__bar_body_rng_0` | `min` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_max__opening_drive_thrust_ratio__rally_strength_max` | `max` | a=`opening_drive_thrust_ratio`, b=`rally_strength_max` |
| `combo_max__max_up_ret__volume_price_confirmation` | `max` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | `rank_min` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | `ifelse` | a=`max_up_ret`, b=`star50_limit_proximity_early`, cond=`gap_pct` |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | `rank_min` | a=`opening_drive_thrust_ratio`, b=`rally_strength_max` |
| `combo_mean__max_up_ret__rally_strength_max` | `mean` | a=`max_up_ret`, b=`rally_strength_max` |
| `combo_max__bar_body_rng_0__rally_strength_max` | `max` | a=`bar_body_rng_0`, b=`rally_strength_max` |
| `combo_max__max_up_ret__bar_body_rng_0` | `max` | a=`max_up_ret`, b=`bar_body_rng_0` |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_weighted_price_position` |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_min` | a=`star50_limit_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_max__max_up_ret__rally_strength_max` | `max` | a=`max_up_ret`, b=`rally_strength_max` |
| `combo_mean__bar_body_rng_0__rally_strength_max` | `mean` | a=`bar_body_rng_0`, b=`rally_strength_max` |
| `combo_rank_min__bar_body_rng_0__rally_strength_max` | `rank_min` | a=`bar_body_rng_0`, b=`rally_strength_max` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`bar_ret_0` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`body_size_progression` |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `mean` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_mean__max_up_ret__volume_weighted_price_position` | `mean` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_rank_min__max_up_ret__gap_pct` | `rank_min` | a=`max_up_ret`, b=`gap_pct` |
| `combo_mean__volatility_expansion_trend_vector__rally_strength_max` | `mean` | a=`volatility_expansion_trend_vector`, b=`rally_strength_max` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | `rank_min` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | `max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`demark_setup_reversal_early`, c=`bar_body_rng_0` |
| `combo_mean__rally_strength_max__volume_price_confirmation` | `mean` | a=`rally_strength_max`, b=`volume_price_confirmation` |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | `mean` | a=`rbreaker_sell_setup_proximity_early`, b=`volume_price_confirmation` |
| `combo_mean__max_up_ret__gap_pct` | `mean` | a=`max_up_ret`, b=`gap_pct` |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | `max` | a=`first_bar_return`, b=`volatility_expansion_trend_vector` |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | `rank_max` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | `max` | a=`volatility_expansion_trend_vector`, b=`volume_price_confirmation` |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | `rank_max` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | `rank_max` | a=`max_up_ret`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__rally_strength_max__volume_price_confirmation` | `rank_min` | a=`rally_strength_max`, b=`volume_price_confirmation` |
| `combo_mean__volatility_expansion_trend_vector__directional_volume_signature` | `mean` | a=`volatility_expansion_trend_vector`, b=`directional_volume_signature` |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0` | `tri_median` | a=`max_up_ret`, b=`demark_setup_reversal_early`, c=`bar_body_rng_0` |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | `tri_median` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`demark_setup_reversal_early` |
| `combo_max__max_up_ret__directional_volume_signature` | `max` | a=`max_up_ret`, b=`directional_volume_signature` |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | `ratio` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | `tri_mean` | a=`max_up_ret`, b=`bar_body_rng_0`, c=`first_bar_return` |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | `clamp_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`gap_pct` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`yesterday_first_30min_return`, c=`yesterday_early_vwap_dev` |
| `combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`volume_weighted_price_position`, b=`volume_weighted_momentum_acceleration` |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | `tri_median` | a=`rbreaker_sell_setup_proximity_early`, b=`max_up_ret`, c=`demark_setup_reversal_early` |
| `combo_mean__max_up_ret__volume_price_confirmation` | `mean` | a=`max_up_ret`, b=`volume_price_confirmation` |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | `rel_diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | `rank_min` | a=`limit_down_proximity_early`, b=`volume_price_confirmation` |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`bar_body_rng_0` |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | `sig_product` | a=`opening_drive_thrust_ratio`, b=`max_up_ret` |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | `rank_max` | a=`star50_limit_proximity_early`, b=`bar_body_rng_0` |
| `combo_z_sum__max_up_ret__directional_volume_signature` | `z_sum` | a=`max_up_ret`, b=`directional_volume_signature` |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | `rel_diff` | a=`rbreaker_sell_setup_proximity_early`, b=`late_bar_momentum` |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | `tri_median` | a=`demark_setup_reversal_early`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_rank_max__max_up_ret__directional_volume_signature` | `rank_max` | a=`max_up_ret`, b=`directional_volume_signature` |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | `min` | a=`bar_body_rng_0`, b=`volume_weighted_price_position` |
| `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation` | `mean` | a=`rbreaker_buy_setup_proximity_early`, b=`volume_price_confirmation` |
| `combo_clamp_diff__first_bar_return__volume_weighted_momentum_acceleration` | `clamp_diff` | a=`first_bar_return`, b=`volume_weighted_momentum_acceleration` |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | `ifelse` | a=`yesterday_early_momentum`, b=`star50_limit_proximity_early`, cond=`gap_pct` |
| `combo_rank_min__max_up_ret__rally_strength_max` | `rank_min` | a=`max_up_ret`, b=`rally_strength_max` |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`bar_body_rng_0` |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | `mean` | a=`limit_down_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_diff__max_up_ret__keltner_squeeze_width` | `diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_min__max_up_ret__volume_weighted_price_position` | `min` | a=`max_up_ret`, b=`volume_weighted_price_position` |
| `combo_max__first_bar_return__rally_strength_max` | `max` | a=`first_bar_return`, b=`rally_strength_max` |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | `ratio` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | `max` | a=`opening_drive_thrust_ratio`, b=`bar_ret_0` |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | `tri_max` | a=`max_up_ret`, b=`star50_limit_proximity_early`, c=`bar_body_rng_0` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early`, c=`first_bar_return` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`volatility_expansion_trend_vector` |
| `combo_rank_min__max_up_ret__directional_volume_signature` | `rank_min` | a=`max_up_ret`, b=`directional_volume_signature` |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | `ifelse` | a=`max_up_ret`, b=`first_bar_return`, cond=`gap_pct` |
| `combo_min__max_up_ret__rally_strength_max` | `min` | a=`max_up_ret`, b=`rally_strength_max` |
| `combo_mean__opening_drive_thrust_ratio__directional_volume_signature` | `mean` | a=`opening_drive_thrust_ratio`, b=`directional_volume_signature` |
| `combo_mean__first_bar_return__volume_weighted_price_position` | `mean` | a=`first_bar_return`, b=`volume_weighted_price_position` |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | `clamp_diff` | a=`max_up_ret`, b=`keltner_squeeze_width` |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position` | `ifelse` | a=`max_up_ret`, b=`volume_weighted_price_position`, cond=`gap_pct` |
| `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return` | `ifelse` | a=`bar_body_rng_0`, b=`first_bar_return`, cond=`gap_pct` |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | `rank_max` | a=`max_up_ret`, b=`star50_limit_proximity_early` |
| `combo_max__volatility_expansion_trend_vector__directional_volume_signature` | `max` | a=`volatility_expansion_trend_vector`, b=`directional_volume_signature` |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | `ifelse` | a=`max_up_ret`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | `rank_max` | a=`opening_drive_thrust_ratio`, b=`rbreaker_buy_setup_proximity_early` |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | `tri_max` | a=`opening_drive_thrust_ratio`, b=`max_up_ret`, c=`star50_limit_proximity_early` |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | `rank_max` | a=`rbreaker_sell_setup_proximity_early`, b=`limit_down_proximity_early` |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | `tri_median` | a=`demark_setup_reversal_early`, b=`star50_limit_proximity_early`, c=`first_bar_return` |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | `tri_mean` | a=`rbreaker_sell_setup_proximity_early`, b=`demark_setup_reversal_early`, c=`bar_body_rng_0` |
| `combo_min__max_up_ret__first_bar_return` | `min` | a=`max_up_ret`, b=`first_bar_return` |
| `combo_rank_min__bar_body_rng_0__directional_volume_signature` | `rank_min` | a=`bar_body_rng_0`, b=`directional_volume_signature` |
| `combo_sig_product__max_up_ret__bar_ret_0` | `sig_product` | a=`max_up_ret`, b=`bar_ret_0` |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | `ifelse` | a=`opening_drive_thrust_ratio`, b=`yesterday_early_vwap_dev`, cond=`gap_pct` |
| `combo_max__bar_ret_0__limit_down_proximity_early` | `max` | a=`bar_ret_0`, b=`limit_down_proximity_early` |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | `sig_product` | a=`star50_limit_proximity_early`, b=`bar_ret_0` |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | `ratio` | a=`bar_ret_0`, b=`volume_weighted_price_position` |
| `combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret` | `ifelse` | a=`yesterday_early_momentum`, b=`max_up_ret`, cond=`gap_pct` |
| `combo_rel_diff__bar_ret_0__volume_weighted_momentum_acceleration` | `rel_diff` | a=`bar_ret_0`, b=`volume_weighted_momentum_acceleration` |
