# Day-Model Rewrite v3 — Admitted Feature Diagnostic Analysis

Detailed standalone and Leave-One-Out (LOO) diagnostic evaluation of all admitted feature pools.
Cost assumption: **8 bps (0.0008)** per position state transition.

---

## Executive Summary

### Key Findings:
1. **Star Performer (159915ETF single)**: Both admitted features (`yesterday_afternoon_momentum` and `max_up_ret`) display strong positive standalone Lockbox IC (+0.134 and +0.206) and friction efficiency > 2.0x, producing net positive Lockbox Sharpe (+0.60).
2. **Turnover Traps (300ETF & 500ETF single)**: Standalone features maintain positive raw IC OOS (+0.05 to +0.26), but trade frequency produces ~2.5 to 3.8 annual position transitions. Average trade return (\mu_{\text{trade}} \approx 3\text{--}6 \text{ bps}) fails to cover 8 bps friction.
3. **Alpha Family Dominance**: **Gap / Overnight Reversal** (`gap_pct`, `first_bar_return`) combined with **Options Market Flow** (`option_oi_growth`, `short_sell_cover_spread`) form the highest quality signal pairs.

---

## Per-ETF Feature Diagnostics

### 300ETF — `single` (Full Model Lockbox IC: +0.0261, Sharpe: -0.1431)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1299 | +0.0650 | +0.0281 | +0.0482 | 0.65 | 0/7 | 0.81 | 0.50 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0002 | -0.4046 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.1365 | +0.0513 | +0.0157 | +0.3013 | 0.73 | 1/7 | 1.06 | 0.74 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0011 | -0.3136 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1267 | +0.0602 | +0.0342 | +1.2516 | 0.78 | 1/7 | 0.77 | 0.57 | `rbreaker_sell_setup_proximity_early` (1.14) | +0.0006 | -0.3078 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1222 | +0.0763 | +0.0511 | +0.4796 | 0.76 | 1/7 | 1.08 | 0.63 | `rbreaker_sell_setup_proximity_early` (1.14) | +0.0021 | -0.0910 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1275 | +0.0653 | +0.0334 | -0.0663 | 0.86 | 1/7 | 1.11 | 0.79 | `rbreaker_sell_setup_proximity_early` (1.14) | +0.0010 | -0.1283 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1164 | +0.0602 | +0.0189 | +0.4526 | 0.82 | 1/7 | 1.02 | 0.74 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0010 | -0.1287 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1206 | +0.0724 | +0.0403 | +0.1246 | 0.77 | 1/7 | 0.93 | 0.57 | `rbreaker_sell_setup_proximity_early` (1.14) | +0.0026 | -0.3126 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1203 | +0.0656 | +0.0210 | +0.3642 | 0.82 | 1/7 | 1.05 | 0.72 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0009 | -0.2325 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0953 | +0.0728 | +0.0616 | +0.2757 | 1.14 | 1/7 | 0.62 | 0.50 | — | -0.0008 | -0.3086 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0976 | +0.0559 | -0.0030 | -0.2655 | 0.67 | 1/7 | 1.07 | 0.63 | `max_up_ret` (0.81) | -0.0006 | -0.4275 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1274 | +0.0632 | +0.0207 | +0.2426 | 0.66 | 1/7 | 0.96 | 0.73 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0004 | -0.3126 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0829 | +0.0534 | -0.0103 | -0.3294 | 0.79 | 0/7 | 1.62 | 1.67 | `volume_weighted_price_position` (1.30) | +0.0004 | -0.3998 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1282 | +0.0715 | +0.0379 | +0.2895 | 0.60 | 0/7 | 0.87 | 0.58 | `rbreaker_sell_setup_proximity_early` (1.14) | +0.0008 | -0.3322 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0883 | +0.0561 | -0.0129 | -0.2036 | 0.86 | 1/7 | 1.26 | 1.03 | `volume_weighted_price_position` (1.30) | -0.0001 | -0.3998 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1140 | +0.0750 | +0.0480 | +0.3040 | 0.77 | 1/7 | 0.99 | 0.54 | `star50_limit_proximity_early` (1.21) | +0.0020 | -0.3126 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0999 | +0.0472 | +0.0120 | +0.2477 | 0.58 | 1/7 | 1.19 | 0.77 | `volume_weighted_price_position` (1.30) | +0.0011 | -0.0404 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0777 | +0.0486 | -0.0212 | -0.4391 | 0.87 | 1/7 | 1.53 | 1.28 | `volume_weighted_price_position` (1.30) | -0.0011 | -0.3998 |
| `combo_mean__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0944 | +0.0540 | +0.0110 | +0.3021 | 0.74 | 1/7 | 1.31 | 0.94 | `volume_surge_direction` (1.02) | +0.0008 | -0.4028 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0888 | +0.0426 | -0.0146 | -0.8370 | 0.75 | 1/7 | 2.05 | 1.27 | `volume_weighted_price_position` (1.30) | -0.0008 | -0.0521 |
| `star50_limit_proximity_early` | Other Technical | +1 | +0.0880 | +0.0720 | +0.0650 | +0.2250 | 1.21 | 1/7 | 0.74 | 0.59 | — | +0.0005 | -0.3078 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0994 | +0.0555 | +0.0184 | +0.3625 | 0.64 | 0/7 | 1.30 | 1.25 | `early_vwap_acceleration` (0.99) | +0.0001 | -0.3078 |
| `combo_max__bar_body_rng_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0889 | +0.0602 | +0.0197 | +0.3941 | 0.72 | 1/7 | 0.81 | 0.19 | `volume_surge_direction` (1.02) | +0.0009 | -0.4028 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1141, Sharpe: +0.7138)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1956 | +0.1034 | +0.1174 | +0.2763 | 0.30 | 0/7 | 0.80 | 0.85 | `rbreaker_sell_setup_proximity_early` (0.40) | +0.0003 | -0.0548 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1926 | +0.1014 | +0.1208 | +1.2786 | 0.28 | 0/7 | 0.65 | 0.75 | `rbreaker_sell_setup_proximity_early` (0.40) | +0.0003 | -0.0396 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1956 | +0.1008 | +0.1174 | +0.5655 | 0.31 | 0/7 | 0.78 | 0.81 | `rbreaker_sell_setup_proximity_early` (0.40) | +0.0001 | -0.0731 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1864 | +0.1029 | +0.1255 | +1.1820 | 0.42 | 0/7 | 1.09 | 1.10 | `star50_limit_proximity_early` (0.62) | +0.0002 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1948 | +0.1142 | +0.1215 | +0.6272 | 0.33 | 0/7 | 0.62 | 0.69 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0003 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1688 | +0.1042 | +0.1274 | +1.0672 | 0.41 | 0/7 | 0.85 | 0.92 | `star50_limit_proximity_early` (0.62) | +0.0003 | -0.0548 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1896 | +0.0882 | +0.1135 | +0.9912 | 0.39 | 0/7 | 0.95 | 0.85 | `star50_limit_proximity_early` (0.62) | +0.0002 | -0.0325 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.2028 | +0.0858 | +0.0810 | -0.4849 | 0.33 | 0/7 | 0.99 | 0.89 | `volume_weighted_momentum_acceleration` (0.46) | -0.0003 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1594 | +0.0984 | +0.0898 | +0.0875 | 0.36 | 0/7 | 0.84 | 0.89 | `volatility_expansion_trend_vector` (0.43) | -0.0000 | -0.0548 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1667 | +0.1036 | +0.1114 | +0.7803 | 0.29 | 0/7 | 0.81 | 0.99 | `volatility_expansion_trend_vector` (0.43) | +0.0003 | -0.0548 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.2024 | +0.1115 | +0.1081 | +0.9335 | 0.31 | 0/7 | 0.71 | 0.79 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1685 | +0.0925 | +0.0808 | +0.1835 | 0.39 | 0/7 | 0.67 | 0.66 | `smooth_momentum_structure` (0.46) | -0.0002 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1819 | +0.0977 | +0.0879 | -0.1797 | 0.31 | 0/7 | 0.86 | 0.77 | `opening_drive_thrust_ratio` (0.36) | +0.0000 | -0.0152 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1881 | +0.0805 | +0.0991 | +1.0237 | 0.40 | 0/7 | 0.70 | 0.59 | `rbreaker_sell_setup_proximity_early` (0.40) | +0.0000 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1597 | +0.1029 | +0.1058 | +0.9485 | 0.26 | 0/7 | 0.69 | 0.87 | `volatility_expansion_trend_vector` (0.43) | +0.0003 | -0.0396 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.2156 | +0.1081 | +0.1124 | +0.4309 | 0.30 | 0/7 | 0.72 | 0.78 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1871 | +0.1082 | +0.1254 | +1.2748 | 0.31 | 0/7 | 0.66 | 0.75 | `rbreaker_sell_setup_proximity_early` (0.40) | +0.0002 | -0.0396 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1911 | +0.0840 | +0.0794 | +0.7938 | 0.36 | 0/7 | 0.85 | 0.72 | `body_size_progression` (0.54) | -0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1847 | +0.1075 | +0.1065 | +0.2154 | 0.33 | 0/7 | 0.65 | 0.69 | `volatility_expansion_trend_vector` (0.43) | -0.0000 | -0.0396 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.1605 | +0.0715 | +0.0685 | -0.4390 | 0.31 | 0/7 | 1.42 | 1.32 | `double_bottom_bull_flag_early` (0.69) | -0.0000 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1855 | +0.0803 | +0.0965 | +0.9550 | 0.43 | 0/7 | 0.67 | 0.54 | `rbreaker_sell_setup_proximity_early` (0.40) | +0.0003 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1533 | +0.1035 | +0.1190 | +1.2660 | 0.34 | 0/7 | 0.63 | 0.83 | `volatility_expansion_trend_vector` (0.43) | +0.0001 | -0.0396 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1790 | +0.0781 | +0.0660 | -0.1778 | 0.33 | 0/7 | 0.72 | 0.55 | `first_bar_sentiment` (0.44) | -0.0004 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1712 | +0.0847 | +0.0801 | -0.9141 | 0.35 | 0/7 | 1.22 | 1.17 | `smooth_momentum_structure` (0.46) | +0.0000 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1800 | +0.0791 | +0.0907 | +0.3450 | 0.39 | 0/7 | 0.63 | 0.60 | `first_bar_sentiment` (0.44) | +0.0001 | -0.0396 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1755 | +0.0934 | +0.0944 | +0.3126 | 0.34 | 0/7 | 1.13 | 1.06 | `volume_weighted_momentum_acceleration` (0.46) | -0.0000 | -0.0152 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1887 | +0.0883 | +0.1135 | +0.9912 | 0.39 | 0/7 | 0.95 | 0.87 | `star50_limit_proximity_early` (0.62) | +0.0002 | -0.0396 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1303 | +0.0958 | +0.0945 | +0.9027 | 0.35 | 0/7 | 0.66 | 0.79 | `close_vs_open_range` (0.48) | -0.0002 | +0.0000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1736 | +0.0855 | +0.0839 | +0.2943 | 0.33 | 0/7 | 1.17 | 1.18 | `volume_weighted_momentum_acceleration` (0.46) | -0.0000 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1585 | +0.0830 | +0.1106 | +1.3239 | 0.45 | 0/7 | 0.72 | 0.59 | `star50_limit_proximity_early` (0.62) | +0.0002 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1738 | +0.0756 | +0.0818 | -0.4758 | 0.41 | 0/7 | 0.79 | 0.59 | `opening_drive_thrust_ratio` (0.36) | +0.0000 | -0.0152 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1758 | +0.0997 | +0.0851 | +0.3170 | 0.37 | 0/7 | 0.65 | 0.64 | `trend_bar_close_consistency` (0.73) | -0.0004 | -0.0396 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1395 | +0.1098 | +0.1321 | +1.3027 | 0.43 | 0/7 | 0.77 | 0.84 | `star50_limit_proximity_early` (0.62) | +0.0002 | -0.0548 |
| `combo_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1908 | +0.0833 | +0.0760 | +0.1987 | 0.34 | 0/7 | 0.85 | 0.73 | `body_size_progression` (0.54) | +0.0001 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1830 | +0.1025 | +0.1090 | +0.5709 | 0.36 | 0/7 | 0.79 | 0.81 | `star50_limit_proximity_early` (0.62) | -0.0000 | -0.0548 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1500 | +0.1164 | +0.1001 | +0.4564 | 0.44 | 0/7 | 0.69 | 0.56 | `close_vs_open_range` (0.48) | -0.0002 | -0.0548 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1618 | +0.1110 | +0.1261 | +0.8321 | 0.40 | 0/7 | 0.47 | 0.49 | — | -0.0004 | -0.0396 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1560 | +0.0702 | +0.0890 | +0.2574 | 0.40 | 0/7 | 0.72 | 0.51 | `max_down_ret` (0.55) | -0.0001 | +0.0000 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1285 | +0.1023 | +0.1169 | +1.2623 | 0.42 | 0/7 | 0.61 | 0.70 | `star50_limit_proximity_early` (0.62) | +0.0001 | -0.0396 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1784 | +0.1005 | +0.0884 | -0.1432 | 0.34 | 0/7 | 0.80 | 0.87 | `opening_drive_thrust_ratio` (0.36) | -0.0001 | -0.0152 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1926 | +0.1047 | +0.1213 | +0.5246 | 0.37 | 0/7 | 0.74 | 0.78 | `star50_limit_proximity_early` (0.62) | +0.0002 | -0.0548 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1300 | +0.1040 | +0.1326 | +1.4616 | 0.49 | 0/7 | 0.57 | 0.71 | `star50_limit_proximity_early` (0.62) | +0.0001 | -0.0396 |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1186 | +0.0958 | +0.1058 | +0.7365 | 0.43 | 0/7 | 0.53 | 0.72 | `trend_bar_close_consistency` (0.73) | +0.0001 | -0.0792 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1629 | +0.1046 | +0.0953 | +0.4120 | 0.41 | 0/7 | 0.79 | 0.83 | `trend_bar_close_consistency` (0.73) | -0.0001 | -0.0548 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1953 | +0.0867 | +0.0870 | +0.7090 | 0.33 | 0/7 | 1.08 | 1.03 | `smooth_momentum_structure` (0.46) | -0.0002 | +0.0000 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1889 | +0.0722 | +0.0735 | -0.4531 | 0.40 | 0/7 | 0.76 | 0.62 | `late_bar_momentum` (0.56) | -0.0001 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1934 | +0.0969 | +0.1091 | +0.6641 | 0.34 | 0/7 | 0.67 | 0.65 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0000 | -0.0396 |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1360 | +0.0773 | +0.0761 | -0.7472 | 0.36 | 0/7 | 0.71 | 0.50 | `first_bar_sentiment` (0.44) | -0.0000 | -0.0396 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | Intraday Range Momentum | +1 | +0.1630 | +0.0942 | +0.0865 | +0.4004 | 0.40 | 0/7 | 0.69 | 0.75 | `early_body_momentum` (0.39) | -0.0001 | -0.0152 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1755 | +0.0877 | +0.0867 | +0.3119 | 0.41 | 0/7 | 1.08 | 0.90 | `body_size_progression` (0.54) | +0.0000 | +0.0000 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1280 | +0.1023 | +0.1274 | +1.2558 | 0.49 | 0/7 | 0.56 | 0.67 | `star50_limit_proximity_early` (0.62) | +0.0003 | -0.0396 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1702 | +0.1014 | +0.0948 | +0.4283 | 0.43 | 0/7 | 0.73 | 0.74 | `close_vs_open_range` (0.48) | -0.0002 | -0.0548 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1672 | +0.1073 | +0.1163 | +0.7295 | 0.35 | 0/7 | 0.59 | 0.66 | `volatility_expansion_trend_vector` (0.43) | -0.0003 | -0.0396 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1788 | +0.0934 | +0.0826 | +0.2486 | 0.33 | 0/7 | 0.71 | 0.65 | `first_bar_sentiment` (0.44) | -0.0001 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1624 | +0.0988 | +0.0916 | +0.3599 | 0.37 | 0/7 | 0.84 | 0.84 | `close_vs_open_range` (0.48) | -0.0001 | -0.0548 |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1219 | +0.0858 | +0.0725 | +0.1089 | 0.41 | 0/7 | 0.96 | 1.23 | `trend_bar_close_consistency` (0.73) | -0.0002 | -0.0548 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.2016 | +0.0866 | +0.0811 | +0.6534 | 0.33 | 0/7 | 1.00 | 0.92 | `volume_weighted_momentum_acceleration` (0.46) | -0.0001 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1452 | +0.1160 | +0.1117 | +0.0670 | 0.54 | 0/7 | 0.41 | 0.43 | `body_size_progression` (0.54) | -0.0003 | -0.0396 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1915 | +0.0824 | +0.0773 | +0.0073 | 0.32 | 0/7 | 0.89 | 0.76 | `body_size_progression` (0.54) | -0.0001 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1640 | +0.0928 | +0.1183 | +1.6160 | 0.51 | 0/7 | 0.88 | 0.75 | `star50_limit_proximity_early` (0.62) | +0.0002 | -0.0580 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1499 | +0.0837 | +0.1100 | +1.0815 | 0.52 | 0/7 | 0.67 | 0.56 | `max_down_ret` (0.55) | +0.0005 | -0.0110 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.0827 | +0.0236 | +0.0020 | +0.7523 | 0.68 | 1/7 | 0.61 | 0.39 | `trend_bar_close_consistency` (0.73) | +0.0000 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1894 | +0.1102 | +0.1164 | +0.5702 | 0.37 | 0/7 | 0.63 | 0.65 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0008 | -0.0396 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1338 | +0.0854 | +0.1095 | +0.5438 | 0.54 | 0/7 | 0.68 | 0.61 | `star50_limit_proximity_early` (0.62) | +0.0001 | -0.0548 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1679 | +0.0867 | +0.1109 | +1.3542 | 0.48 | 0/7 | 0.76 | 0.54 | `star50_limit_proximity_early` (0.62) | +0.0003 | -0.0396 |
| `combo_mean__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1328 | +0.0859 | +0.0653 | +0.3607 | 0.45 | 0/7 | 0.65 | 0.78 | `trend_bar_close_consistency` (0.73) | -0.0003 | -0.0152 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1575 | +0.0973 | +0.0780 | -0.1976 | 0.27 | 0/7 | 1.00 | 1.07 | `opening_drive_thrust_ratio` (0.36) | +0.0001 | -0.0152 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1549 | +0.0993 | +0.1124 | +0.6138 | 0.34 | 0/7 | 0.72 | 0.72 | `star50_limit_proximity_early` (0.62) | -0.0002 | -0.0548 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1476 | +0.1024 | +0.1219 | +0.5797 | 0.50 | 0/7 | 0.52 | 0.51 | `star50_limit_proximity_early` (0.62) | -0.0002 | -0.0396 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1312 | +0.0939 | +0.1114 | +0.4728 | 0.60 | 0/7 | 0.58 | 0.53 | `star50_limit_proximity_early` (0.62) | +0.0004 | -0.0548 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1796 | +0.0956 | +0.0870 | +0.0581 | 0.36 | 0/7 | 0.90 | 0.91 | — | -0.0000 | -0.0152 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1893 | +0.0935 | +0.0809 | +0.1429 | 0.33 | 0/7 | 0.79 | 0.93 | `opening_drive_thrust_ratio` (0.36) | -0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1592 | +0.1053 | +0.0913 | +0.7789 | 0.32 | 0/7 | 0.77 | 0.65 | `early_body_momentum` (0.39) | -0.0000 | -0.0548 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1134 | +0.0898 | +0.0847 | +0.5290 | 0.39 | 0/7 | 0.68 | 0.69 | `close_vs_open_range` (0.48) | -0.0002 | -0.0152 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1583 | +0.0972 | +0.1139 | +1.4937 | 0.39 | 0/7 | 0.73 | 0.66 | `volume_weighted_momentum_acceleration` (0.46) | -0.0000 | +0.0071 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1721 | +0.0930 | +0.0808 | -0.5540 | 0.35 | 0/7 | 0.79 | 0.71 | `first_bar_sentiment` (0.44) | +0.0000 | +0.0000 |
| `combo_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1472 | +0.0867 | +0.0693 | +0.1614 | 0.43 | 0/7 | 0.67 | 0.58 | `early_body_momentum` (0.39) | -0.0002 | -0.0152 |
| `combo_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1327 | +0.0998 | +0.0916 | +0.0977 | 0.33 | 0/7 | 0.70 | 0.85 | `close_vs_open_range` (0.48) | -0.0001 | -0.0396 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1772 | +0.0905 | +0.0900 | +0.5700 | 0.34 | 0/7 | 0.80 | 0.68 | `first_bar_sentiment` (0.44) | +0.0002 | -0.0152 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1773 | +0.0854 | +0.0924 | +0.0770 | 0.36 | 0/7 | 0.85 | 0.73 | `opening_drive_thrust_ratio` (0.36) | +0.0001 | -0.0152 |
| `combo_min__close_vs_open_range__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1117 | +0.0897 | +0.0810 | -0.0454 | 0.50 | 0/7 | 0.61 | 0.60 | `high_low_sequence_momentum` (0.50) | -0.0002 | -0.0396 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1709 | +0.0936 | +0.0778 | +0.1313 | 0.30 | 0/7 | 0.73 | 0.78 | — | -0.0002 | +0.0000 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1535 | +0.0930 | +0.0728 | +0.2807 | 0.44 | 0/7 | 0.65 | 0.58 | `early_body_momentum` (0.39) | -0.0002 | -0.0152 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1456 | +0.0899 | +0.0540 | +0.0071 | 0.41 | 0/7 | 0.91 | 0.84 | `close_vs_open_range` (0.48) | -0.0001 | -0.0548 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1466 | +0.0959 | +0.0723 | +0.3991 | 0.44 | 0/7 | 0.99 | 0.98 | `opening_drive_thrust_ratio` (0.36) | +0.0001 | -0.0152 |
| `combo_mean__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1558 | +0.0980 | +0.0821 | +0.0418 | 0.37 | 0/7 | 0.69 | 0.73 | `close_vs_open_range` (0.48) | -0.0002 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1863 | +0.0992 | +0.0822 | +0.3860 | 0.36 | 0/7 | 0.73 | 0.83 | `opening_drive_thrust_ratio` (0.36) | -0.0003 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1433 | +0.0849 | +0.0651 | +0.6012 | 0.49 | 0/7 | 0.91 | 1.00 | `trend_bar_close_consistency` (0.73) | +0.0001 | -0.0548 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1710 | +0.0853 | +0.0976 | +0.2946 | 0.39 | 0/7 | 0.80 | 0.64 | `max_down_ret` (0.55) | -0.0002 | -0.0152 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1286 | +0.0852 | +0.1007 | +0.4324 | 0.46 | 0/7 | 0.63 | 0.40 | `close_vs_open_range` (0.48) | -0.0000 | +0.0000 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1297 | +0.0870 | +0.0753 | -0.1482 | 0.32 | 0/7 | 0.75 | 0.66 | `first_bar_sentiment` (0.44) | -0.0001 | -0.0548 |
| `combo_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1670 | +0.0940 | +0.0758 | +0.0132 | 0.40 | 0/7 | 0.71 | 0.65 | `close_vs_open_range` (0.48) | -0.0001 | -0.0152 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1624 | +0.1018 | +0.1181 | +0.9110 | 0.21 | 0/7 | 0.82 | 0.78 | `early_late_momentum_divergence` (0.56) | -0.0002 | +0.0000 |
| `combo_min__max_up_ret__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1305 | +0.1017 | +0.0846 | +0.0725 | 0.32 | 0/7 | 0.79 | 0.94 | `high_low_sequence_momentum` (0.50) | -0.0002 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1458 | +0.0931 | +0.0876 | +0.6961 | 0.33 | 0/7 | 0.95 | 0.97 | `close_vs_open_range` (0.48) | -0.0001 | -0.0548 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1677 | +0.0852 | +0.1093 | +1.3542 | 0.48 | 0/7 | 0.77 | 0.56 | `star50_limit_proximity_early` (0.62) | +0.0002 | -0.0396 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Other Technical | +1 | +0.1109 | +0.0778 | +0.0870 | +0.2040 | 0.52 | 0/7 | 0.68 | 0.46 | `trend_bar_close_consistency` (0.73) | -0.0001 | +0.0000 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.0687 | +0.0159 | +0.0027 | +0.5710 | 0.64 | 0/7 | 0.54 | 0.36 | `early_body_momentum` (0.39) | -0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1294 | +0.0860 | +0.0891 | +0.6744 | 0.44 | 0/7 | 0.95 | 0.59 | `star50_limit_proximity_early` (0.62) | -0.0000 | +0.0000 |
| `combo_min__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1290 | +0.0864 | +0.1022 | +0.2825 | 0.45 | 0/7 | 0.64 | 0.42 | `close_vs_open_range` (0.48) | -0.0002 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1713 | +0.0863 | +0.0943 | +0.8842 | 0.42 | 0/7 | 0.86 | 0.78 | `max_down_ret` (0.55) | -0.0001 | -0.0152 |
| `combo_mean__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1817 | +0.0876 | +0.0779 | +0.4297 | 0.33 | 0/7 | 0.78 | 0.69 | `first_bar_return` (0.35) | -0.0003 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1692 | +0.0799 | +0.0795 | +0.1268 | 0.37 | 0/7 | 1.25 | 1.20 | `smooth_momentum_structure` (0.46) | +0.0003 | +0.0000 |
| `combo_mean__volatility_expansion_trend_vector__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1172 | +0.0928 | +0.0862 | +0.5339 | 0.43 | 0/7 | 0.66 | 0.68 | `close_vs_open_range` (0.48) | -0.0000 | -0.0396 |
| `combo_min__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1338 | +0.0955 | +0.0945 | +0.4915 | 0.36 | 0/7 | 0.82 | 0.69 | `bar_ret_0` (0.35) | +0.0000 | -0.0152 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1670 | +0.0933 | +0.0743 | +0.3024 | 0.39 | 0/7 | 0.71 | 0.67 | `close_vs_open_range` (0.48) | -0.0004 | -0.0548 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.1203 | +0.0930 | +0.0847 | +0.3991 | 0.32 | 0/7 | 0.82 | 0.90 | — | -0.0001 | -0.0152 |
| `combo_rank_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1723 | +0.0708 | +0.0679 | +0.2061 | 0.39 | 0/7 | 0.72 | 0.61 | `bar_ret_0` (0.35) | -0.0003 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1912 | +0.0934 | +0.0898 | +0.0637 | 0.33 | 0/7 | 0.86 | 0.85 | `opening_drive_thrust_ratio` (0.36) | -0.0000 | -0.0152 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1643 | +0.0832 | +0.0639 | +0.3192 | 0.43 | 0/7 | 0.66 | 0.82 | `trend_bar_close_consistency` (0.73) | -0.0003 | -0.0152 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1505 | +0.1190 | +0.0968 | +0.4860 | 0.36 | 0/7 | 0.90 | 0.76 | `volatility_expansion_trend_vector` (0.43) | -0.0000 | -0.0396 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1593 | +0.0754 | +0.0763 | +0.6216 | 0.33 | 0/7 | 0.79 | 0.54 | `first_bar_sentiment` (0.44) | -0.0002 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1871 | +0.0973 | +0.0854 | +0.2194 | 0.30 | 0/7 | 0.89 | 0.88 | `opening_drive_thrust_ratio` (0.36) | -0.0003 | +0.0000 |
| `combo_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1761 | +0.0836 | +0.0748 | -0.2388 | 0.32 | 0/7 | 0.79 | 0.69 | `first_bar_return` (0.35) | -0.0004 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1680 | +0.0932 | +0.0941 | +0.1702 | 0.43 | 0/7 | 0.86 | 0.72 | `max_down_ret` (0.55) | -0.0001 | -0.0152 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1385 | +0.0870 | +0.1143 | +0.5420 | 0.68 | 0/7 | 0.51 | 0.47 | `star50_limit_proximity_early` (0.62) | +0.0003 | -0.0396 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1828 | +0.1096 | +0.1115 | +0.4562 | 0.45 | 0/7 | 0.65 | 0.60 | `star50_limit_proximity_early` (0.62) | -0.0005 | +0.0000 |
| `combo_max__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1357 | +0.0815 | +0.0756 | -0.1251 | 0.30 | 0/7 | 0.86 | 0.75 | `first_bar_sentiment` (0.44) | -0.0001 | -0.0152 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1751 | +0.0926 | +0.0837 | -0.0026 | 0.27 | 0/7 | 0.79 | 0.75 | `first_bar_return` (0.35) | -0.0002 | +0.0000 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1623 | +0.1046 | +0.1053 | +0.3612 | 0.38 | 0/7 | 0.62 | 0.56 | `star50_limit_proximity_early` (0.62) | -0.0003 | -0.0396 |
| `combo_mean__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1522 | +0.0914 | +0.0855 | -0.1857 | 0.32 | 0/7 | 0.80 | 0.73 | `bar_ret_0` (0.35) | -0.0001 | -0.0152 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1431 | +0.1056 | +0.0916 | +0.5551 | 0.48 | 0/7 | 0.46 | 0.35 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0003 | -0.0548 |
| `star50_limit_proximity_early` | Other Technical | +1 | +0.1323 | +0.1129 | +0.1379 | +0.3067 | 0.62 | 0/7 | 0.45 | 0.42 | — | -0.0001 | -0.0396 |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1001 | +0.0317 | +0.0439 | +0.1933 | 0.53 | 0/7 | 1.55 | 0.96 | `trend_bar_close_consistency` (0.73) | -0.0001 | +0.0000 |
| `combo_ratio__max_down_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1323 | +0.0543 | +0.1213 | +0.1422 | 0.47 | 0/7 | 0.64 | 0.42 | `max_down_ret` (0.55) | -0.0002 | +0.0000 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1442 | +0.0766 | +0.0847 | -0.0243 | 0.41 | 0/7 | 0.60 | 0.42 | `close_vs_open_range` (0.48) | -0.0002 | -0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1520 | +0.0730 | +0.0767 | +0.5826 | 0.49 | 1/7 | 1.31 | 1.38 | `volume_weighted_momentum_acceleration` (0.46) | -0.0002 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1834 | +0.1194 | +0.1199 | +1.0038 | 0.37 | 0/7 | 0.57 | 0.57 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0002 | +0.0000 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1601 | +0.0713 | +0.0760 | -0.3028 | 0.28 | 0/7 | 0.80 | 0.64 | `first_bar_sentiment` (0.44) | -0.0001 | +0.0000 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1425 | +0.0933 | +0.0886 | +0.0993 | 0.38 | 0/7 | 0.68 | 0.56 | `close_vs_open_range` (0.48) | -0.0003 | -0.0396 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1122 | +0.0872 | +0.0832 | -0.0109 | 0.50 | 0/7 | 0.60 | 0.64 | `close_vs_open_range` (0.48) | -0.0002 | -0.0548 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1337 | +0.0949 | +0.0889 | +0.6883 | 0.49 | 0/7 | 0.50 | 0.39 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0007 | -0.0548 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1601 | +0.1009 | +0.1089 | +0.5497 | 0.46 | 0/7 | 0.55 | 0.45 | `volatility_expansion_trend_vector` (0.43) | -0.0006 | -0.0396 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1317 | +0.1161 | +0.1243 | -0.1522 | 0.59 | 0/7 | 0.50 | 0.58 | `star50_limit_proximity_early` (0.62) | -0.0000 | -0.0396 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1384 | +0.0479 | +0.0995 | +0.5483 | 0.53 | 0/7 | 0.63 | 0.44 | `max_down_ret` (0.55) | -0.0001 | -0.0152 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1422 | +0.0693 | +0.0872 | +0.0606 | 0.44 | 0/7 | 0.74 | 0.45 | `max_down_ret` (0.55) | -0.0001 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1473 | +0.0924 | +0.0589 | -0.0614 | 0.42 | 0/7 | 0.98 | 0.93 | `volatility_expansion_trend_vector` (0.43) | +0.0000 | -0.0396 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1661 | +0.0766 | +0.0858 | +0.7374 | 0.44 | 0/7 | 1.01 | 0.85 | `late_bar_momentum` (0.56) | +0.0000 | +0.0000 |
| `combo_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1754 | +0.0809 | +0.0732 | +0.4565 | 0.36 | 0/7 | 0.72 | 0.64 | `bar_ret_0` (0.35) | -0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1459 | +0.1137 | +0.1471 | +0.9685 | 0.63 | 0/7 | 0.54 | 0.46 | `star50_limit_proximity_early` (0.62) | +0.0001 | +0.0000 |
| `combo_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1471 | +0.0740 | +0.0944 | +0.2850 | 0.41 | 0/7 | 0.78 | 0.50 | `max_down_ret` (0.55) | +0.0003 | +0.0000 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1546 | +0.0924 | +0.1120 | +0.8178 | 0.36 | 0/7 | 0.66 | 0.59 | `body_size_progression` (0.54) | -0.0001 | -0.0396 |
| `combo_max__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1697 | +0.0904 | +0.0729 | -0.2363 | 0.31 | 0/7 | 0.81 | 0.79 | `close_vs_open_range` (0.48) | -0.0002 | -0.0548 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1294 | +0.1019 | +0.1298 | +0.7773 | 0.61 | 0/7 | 0.48 | 0.41 | `star50_limit_proximity_early` (0.62) | -0.0003 | -0.0396 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1856 | +0.1001 | +0.0934 | +0.2942 | 0.37 | 0/7 | 0.64 | 0.67 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0006 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1333 | +0.0870 | +0.0701 | -0.5739 | 0.58 | 1/7 | 1.20 | 1.41 | `body_size_progression` (0.54) | -0.0001 | -0.0396 |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1699 | +0.0908 | +0.0729 | -0.1753 | 0.31 | 0/7 | 0.81 | 0.79 | `close_vs_open_range` (0.48) | -0.0003 | -0.0548 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1396 | +0.0859 | +0.0751 | +0.0796 | 0.35 | 0/7 | 0.82 | 0.61 | `close_vs_open_range` (0.48) | -0.0001 | -0.0548 |
| `combo_sig_product__close_vs_open_range__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1051 | +0.0887 | +0.0814 | -0.1448 | 0.50 | 0/7 | 0.69 | 0.73 | `high_low_sequence_momentum` (0.50) | -0.0001 | -0.0396 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1638 | +0.1054 | +0.0902 | +0.5017 | 0.42 | 0/7 | 0.56 | 0.52 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0003 | +0.0000 |
| `combo_rank_max__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1601 | +0.0800 | +0.0675 | -0.4587 | 0.29 | 0/7 | 0.81 | 0.73 | `first_bar_return` (0.35) | -0.0003 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1640 | +0.1059 | +0.1084 | +0.4064 | 0.28 | 0/7 | 0.62 | 0.60 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0003 | -0.0396 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1741 | +0.1166 | +0.1152 | +1.0169 | 0.50 | 0/7 | 0.55 | 0.47 | `star50_limit_proximity_early` (0.62) | -0.0002 | -0.0396 |
| `combo_max__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1655 | +0.0799 | +0.0855 | +0.2376 | 0.40 | 0/7 | 0.78 | 0.64 | `max_down_ret` (0.55) | -0.0002 | -0.0152 |
| `combo_rank_min__close_vs_open_range__max_down_ret` | Intraday Range Momentum | +1 | +0.1325 | +0.0965 | +0.1086 | +0.3739 | 0.57 | 0/7 | 0.68 | 0.51 | `max_down_ret` (0.55) | -0.0001 | -0.0152 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1641 | +0.0793 | +0.0583 | -0.2641 | 0.44 | 0/7 | 1.27 | 1.68 | `opening_drive_thrust_ratio` (0.36) | -0.0003 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1692 | +0.1074 | +0.0936 | +0.3241 | 0.42 | 0/7 | 0.58 | 0.53 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0005 | +0.0000 |
| `combo_max__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.1011 | +0.0857 | +0.0748 | +0.3373 | 0.47 | 0/7 | 0.59 | 0.70 | `close_vs_open_range` (0.48) | -0.0001 | -0.0548 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1432 | +0.1231 | +0.1703 | +1.1170 | 0.38 | 0/7 | 0.85 | 0.85 | `star50_limit_proximity_early` (0.62) | +0.0001 | -0.0152 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1585 | +0.0944 | +0.0921 | -0.0397 | 0.36 | 0/7 | 0.73 | 0.65 | `close_vs_open_range` (0.48) | -0.0002 | -0.0396 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1647 | +0.0932 | +0.0910 | +0.2300 | 0.46 | 0/7 | 0.55 | 0.45 | `volatility_expansion_trend_vector` (0.43) | -0.0004 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1535 | +0.0927 | +0.1040 | +0.4351 | 0.48 | 0/7 | 0.86 | 0.76 | `max_down_ret` (0.55) | +0.0001 | -0.0152 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1885 | +0.0943 | +0.0793 | -0.0337 | 0.32 | 0/7 | 0.92 | 0.96 | `opening_drive_thrust_ratio` (0.36) | -0.0003 | +0.0000 |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.1017 | +0.0727 | +0.0568 | -0.3559 | 0.41 | 0/7 | 0.64 | 0.76 | `close_vs_open_range` (0.48) | -0.0001 | -0.0548 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1436 | +0.1254 | +0.1504 | +0.5807 | 0.38 | 0/7 | 0.79 | 0.76 | `star50_limit_proximity_early` (0.62) | +0.0002 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1332 | +0.0862 | +0.0607 | -0.4162 | 0.47 | 0/7 | 1.15 | 1.18 | `early_late_momentum_divergence` (0.56) | -0.0001 | +0.0000 |
| `combo_min__close_vs_open_range__max_down_ret` | Intraday Range Momentum | +1 | +0.1290 | +0.0984 | +0.1071 | +0.2946 | 0.57 | 0/7 | 0.65 | 0.49 | `max_down_ret` (0.55) | +0.0001 | -0.0152 |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1618 | +0.1063 | +0.1039 | +0.2943 | 0.39 | 0/7 | 0.60 | 0.54 | `star50_limit_proximity_early` (0.62) | -0.0003 | -0.0396 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1710 | +0.0974 | +0.0993 | +0.3374 | 0.41 | 0/7 | 0.90 | 0.82 | `max_down_ret` (0.55) | +0.0002 | -0.0152 |
| `combo_max__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1567 | +0.0784 | +0.0677 | -0.7440 | 0.32 | 0/7 | 0.80 | 0.72 | `bar_ret_0` (0.35) | -0.0002 | +0.0000 |
| `combo_mean__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1334 | +0.0939 | +0.0977 | +0.0089 | 0.41 | 0/7 | 0.80 | 0.64 | `max_down_ret` (0.55) | +0.0001 | -0.0152 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.0926 | +0.0279 | +0.0356 | +0.4291 | 0.55 | 0/7 | 1.46 | 0.86 | `trend_bar_close_consistency` (0.73) | -0.0000 | +0.0071 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1592 | +0.0680 | +0.0690 | +0.2253 | 0.35 | 0/7 | 0.81 | 0.58 | — | +0.0000 | +0.0000 |
| `combo_max__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1507 | +0.0768 | +0.0648 | +0.2253 | 0.41 | 0/7 | 0.90 | 0.68 | `first_bar_sentiment` (0.44) | -0.0000 | +0.0000 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1365 | +0.0707 | +0.0538 | +0.1090 | 0.38 | 0/7 | 0.88 | 0.60 | `first_bar_sentiment` (0.44) | -0.0001 | -0.0548 |
| `combo_mean__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1520 | +0.0844 | +0.1023 | +0.6095 | 0.42 | 0/7 | 0.80 | 0.54 | `max_down_ret` (0.55) | +0.0000 | -0.0152 |
| `combo_clamp_diff__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.0740 | -0.0051 | -0.0149 | -0.0081 | 1.04 | 1/7 | 0.88 | 0.29 | `trend_bar_close_consistency` (0.73) | -0.0001 | +0.0000 |
| `combo_diff__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.0740 | -0.0049 | -0.0146 | -0.0081 | 1.04 | 1/7 | 0.88 | 0.29 | `trend_bar_close_consistency` (0.73) | -0.0000 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1518 | +0.0808 | +0.0756 | +0.4048 | 0.44 | 0/7 | 1.04 | 1.13 | `opening_drive_thrust_ratio` (0.36) | +0.0002 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1703 | +0.0816 | +0.0791 | +0.5933 | 0.44 | 0/7 | 1.16 | 0.98 | `body_size_progression` (0.54) | +0.0000 | +0.0000 |
| `combo_rank_max__trend_bar_close_consistency__close_vs_open_range` | Other Technical | +1 | +0.0978 | +0.0779 | +0.0658 | +0.6592 | 0.55 | 0/7 | 0.58 | 0.79 | `trend_bar_close_consistency` (0.73) | -0.0002 | -0.0548 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1645 | +0.0882 | +0.0782 | +0.3070 | 0.43 | 0/7 | 0.79 | 0.81 | `bar_ret_0` (0.35) | -0.0001 | +0.0000 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1104 | +0.0566 | +0.0569 | -0.1137 | 0.47 | 0/7 | 0.98 | 1.03 | `first_bar_return` (0.35) | +0.0000 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1252 | +0.0997 | +0.0854 | +0.6539 | 0.68 | 0/7 | 0.40 | 0.34 | `trend_bar_close_consistency` (0.73) | -0.0001 | -0.0548 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.0772 | +0.0677 | +0.0913 | -0.2578 | 0.78 | 1/7 | 0.96 | 1.62 | `double_bottom_bull_flag_early` (0.69) | -0.0002 | -0.0152 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` | Intraday Range Momentum | +1 | +0.1044 | +0.0332 | +0.0481 | +0.0435 | 0.59 | 1/7 | 1.89 | 1.39 | `early_body_momentum` (0.39) | +0.0000 | +0.0000 |
| `combo_max__early_body_momentum__max_down_ret` | Intraday Range Momentum | +1 | +0.1118 | +0.0689 | +0.0734 | -0.3815 | 0.47 | 0/7 | 0.67 | 0.76 | `max_down_ret` (0.55) | -0.0002 | -0.0548 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.1023 | +0.0822 | +0.0602 | -0.5999 | 0.52 | 0/7 | 0.87 | 0.99 | — | +0.0001 | -0.0152 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1645 | +0.0923 | +0.1118 | +0.5878 | 0.42 | 0/7 | 1.01 | 1.05 | `max_down_ret` (0.55) | +0.0003 | -0.0152 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.1126 | +0.0893 | +0.0726 | +0.4138 | 0.42 | 0/7 | 0.79 | 1.04 | — | -0.0002 | +0.0000 |
| `open_to_current_return` | Intraday Range Momentum | +1 | +0.1167 | +0.0884 | +0.0708 | +0.4514 | 0.41 | 0/7 | 0.72 | 0.88 | — | -0.0002 | +0.0000 |
| `bar_body_rng_0` | Other Technical | +1 | +0.1463 | +0.0756 | +0.0799 | +0.1818 | 0.28 | 0/7 | 0.94 | 0.68 | — | -0.0002 | +0.0000 |
| `or_fill_ratio` | Other Technical | +1 | +0.0791 | +0.0805 | +0.0708 | +0.3666 | 0.59 | 0/7 | 0.60 | 0.55 | — | -0.0001 | -0.0548 |

### 588000ETF — `single` (Full Model Lockbox IC: -0.0125, Sharpe: +0.5122)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1388 | +0.0112 | -0.0358 | -0.9563 | 0.55 | 0/5 | 0.91 | 0.57 | `trend_day_regime_conviction` (0.73) | -0.0015 | +0.3936 |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1329 | +0.0030 | -0.0400 | -0.9563 | 0.55 | 0/5 | 0.88 | 0.56 | `trend_day_regime_conviction` (0.73) | -0.0064 | +0.2040 |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1055 | +0.0232 | +0.0282 | +0.1859 | 0.57 | 0/5 | 0.82 | 0.62 | `smooth_momentum_structure` (0.61) | +0.0118 | +0.1596 |
| `combo_rel_diff__directional_volume_signature__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1079 | +0.0243 | +0.0298 | +0.3474 | 0.55 | 0/5 | 0.88 | 0.63 | `smooth_momentum_structure` (0.61) | +0.0058 | +0.0000 |
| `combo_diff__directional_volume_signature__early_vwap_acceleration` | Volatility & Oscillators | +1 | +0.1087 | +0.0148 | +0.0549 | +0.9909 | 0.74 | 0/5 | 0.76 | 0.77 | `early_vwap_acceleration` (0.89) | +0.0179 | -0.0313 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | Intraday Range Momentum | +1 | +0.1493 | -0.0578 | -0.1208 | -1.2126 | 0.59 | 0/5 | 0.91 | 0.54 | `high_low_sequence_momentum` (0.75) | -0.0125 | +0.4889 |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.0645 | -0.0057 | +0.0139 | +0.2213 | 0.57 | 0/5 | 1.10 | 0.53 | `smooth_momentum_structure` (0.61) | +0.0047 | +0.0973 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1040 | -0.0093 | -0.0537 | -0.4510 | 0.68 | 0/5 | 1.02 | 0.51 | — | -0.0072 | +0.3619 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1449, Sharpe: +1.6707)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1383 | +0.1379 | +0.1423 | +1.5511 | 0.58 | 0/7 | 1.42 | 1.13 | `star50_limit_proximity_early` (0.77) | +0.0007 | +0.0373 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1766 | +0.0993 | +0.1147 | +1.6792 | 0.50 | 1/7 | 1.09 | 0.74 | `first_bar_sentiment` (0.70) | -0.0009 | +0.1315 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1502 | +0.1160 | +0.1297 | +0.5252 | 0.55 | 1/7 | 1.22 | 0.64 | `first_bar_sentiment` (0.70) | +0.0000 | +0.0000 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1535 | +0.1228 | +0.1419 | +1.8188 | 0.64 | 1/7 | 1.44 | 0.91 | `star50_limit_proximity_early` (0.77) | +0.0013 | +0.0373 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1592 | +0.1073 | +0.1230 | +0.2691 | 0.48 | 0/7 | 1.04 | 0.60 | `first_bar_sentiment` (0.70) | +0.0003 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1372 | +0.0982 | +0.0783 | +0.3481 | 0.45 | 0/7 | 1.46 | 0.81 | `first_bar_sentiment` (0.70) | -0.0019 | -0.0270 |
| `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1569 | +0.1201 | +0.1340 | +1.6914 | 0.54 | 1/7 | 1.45 | 0.92 | `star50_limit_proximity_early` (0.77) | +0.0005 | -0.0832 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1345 | +0.1333 | +0.1313 | +1.1028 | 0.64 | 1/7 | 1.42 | 1.09 | `star50_limit_proximity_early` (0.77) | +0.0012 | +0.0730 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1701 | +0.1197 | +0.1284 | +1.2722 | 0.46 | 1/7 | 1.26 | 0.83 | `bar_body_rng_0` (0.51) | -0.0002 | +0.0194 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1678 | +0.1162 | +0.1293 | +1.0208 | 0.56 | 1/7 | 1.05 | 0.77 | `rbreaker_sell_setup_proximity_early` (0.47) | +0.0010 | -0.0174 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1678 | +0.1322 | +0.1292 | +1.4375 | 0.41 | 0/7 | 1.23 | 0.94 | `opening_drive_thrust_ratio` (0.52) | -0.0004 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1666 | +0.1157 | +0.1291 | +1.3213 | 0.55 | 1/7 | 1.06 | 0.76 | `rbreaker_sell_setup_proximity_early` (0.47) | -0.0000 | +0.0158 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1416 | +0.1185 | +0.1349 | +1.3879 | 0.71 | 1/7 | 1.22 | 0.75 | `star50_limit_proximity_early` (0.77) | +0.0010 | +0.0803 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0909 | +0.1263 | +0.1192 | +0.6699 | 0.90 | 1/7 | 0.89 | 0.61 | `yesterday_first_30min_return` (1.04) | +0.0006 | +0.2285 |
| `combo_min__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1532 | +0.0935 | +0.1242 | +1.8505 | 0.65 | 1/7 | 1.32 | 0.85 | `star50_limit_proximity_early` (0.77) | +0.0004 | +0.0645 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1533 | +0.1317 | +0.1338 | +0.9177 | 0.39 | 0/7 | 1.26 | 1.09 | `rbreaker_sell_setup_proximity_early` (0.47) | +0.0008 | +0.0216 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1075 | +0.1414 | +0.1410 | +1.2951 | 0.88 | 1/7 | 0.76 | 0.51 | `yesterday_first_30min_return` (1.04) | +0.0013 | +0.2137 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1601 | +0.1228 | +0.1309 | +1.7939 | 0.50 | 0/7 | 1.17 | 0.91 | `star50_limit_proximity_early` (0.77) | +0.0004 | +0.0281 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1507 | +0.1047 | +0.0931 | -0.0046 | 0.46 | 0/7 | 1.29 | 0.78 | `bar_body_rng_0` (0.51) | -0.0004 | -0.0483 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1441 | +0.1018 | +0.0874 | -0.0146 | 0.38 | 0/7 | 1.37 | 0.94 | `max_up_ret` (0.41) | -0.0003 | -0.0909 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1349 | +0.1238 | +0.1109 | +0.3405 | 0.58 | 0/7 | 1.29 | 0.97 | `demark_setup_reversal_early` (0.85) | +0.0003 | +0.0085 |
| `combo_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1444 | +0.1009 | +0.0844 | -0.0622 | 0.37 | 0/7 | 1.37 | 0.93 | `max_up_ret` (0.41) | -0.0004 | -0.0028 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1286 | +0.1129 | +0.0866 | +0.2848 | 0.44 | 0/7 | 1.32 | 1.02 | `opening_drive_thrust_ratio` (0.52) | -0.0006 | -0.0028 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1256 | +0.1222 | +0.1021 | +0.6179 | 0.60 | 0/7 | 1.36 | 1.12 | `demark_setup_reversal_early` (0.85) | +0.0002 | +0.0195 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1409 | +0.0977 | +0.0832 | +0.3748 | 0.45 | 0/7 | 1.30 | 0.80 | `opening_drive_thrust_ratio` (0.52) | -0.0008 | -0.0076 |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | Gap / Overnight Reversal | +1 | +0.1383 | +0.0938 | +0.1182 | +1.6439 | 0.71 | 1/7 | 1.56 | 0.85 | `limit_down_proximity_early` (1.21) | +0.0006 | +0.0024 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1034 | +0.1152 | +0.1311 | +1.1520 | 0.73 | 0/7 | 0.82 | 0.73 | `star50_limit_proximity_early` (0.77) | +0.0000 | +0.0000 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4029_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1039 | 30 | 73.3% | 30.0% | +0.0125 | -0.2595 |
| B2 Rolling Guard | 240 | 30 | 76.7% | 23.3% | +0.0040 | -0.1929 |
| BH-FDR Gate | 4 | 4 | 50.0% | 50.0% | -0.0029 | -0.2249 |
| B3 Composite Floor | 14 | 14 | 35.7% | 28.6% | -0.0069 | -0.2770 |
| B4 Correlation Gate | 10 | 10 | 80.0% | 80.0% | +0.0188 | +0.1528 |

**Admitted Pool Summary**: 18 features, False Positive Rate = 33.3% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0196, Mean Lock Sharpe = +0.1240

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0379, Lock Sharpe=+1.0599
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Lock Sharpe=+0.8717
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Lock Sharpe=+0.8717
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.1992, Lock IC=+0.0050, Lock Sharpe=+0.4905
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2064, Lock IC=+0.0446, Lock Sharpe=+0.3476

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2064, Lock IC=+0.0264, Lock Sharpe=+0.8994
- `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2042, Lock IC=+0.0016, Lock Sharpe=+0.5869
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Train IC=+0.1796, Lock IC=+0.0141, Lock Sharpe=+0.2036
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.1892, Lock IC=+0.0238, Lock Sharpe=+0.0677
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.1891, Lock IC=+0.0237, Lock Sharpe=+0.0677

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1327, Lock IC=+0.0184, Lock Sharpe=+0.3625
- `combo_z_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1327, Lock IC=+0.0184, Lock Sharpe=+0.3625

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.2194, Lock IC=+0.0039, Lock Sharpe=+0.1295
- `combo_tri_z_mean__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.2194, Lock IC=+0.0039, Lock Sharpe=+0.1295
- `combo_tri_mean__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.2193, Lock IC=+0.0040, Lock Sharpe=+0.1295
- `combo_tri_z_mean__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.2193, Lock IC=+0.0040, Lock Sharpe=+0.1295

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2660, Lock IC=+0.0189, Lock Sharpe=+0.4526
- `combo_z_sum__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2194, Lock IC=+0.0379, Lock Sharpe=+0.2895
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2095, Lock IC=+0.0251, Lock Sharpe=+0.2759
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2095, Lock IC=+0.0251, Lock Sharpe=+0.2759
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`: Train IC=+0.2257, Lock IC=+0.0207, Lock Sharpe=+0.2426

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 38.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6045_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 555 | 30 | 73.3% | 3.3% | +0.0149 | -0.4762 |
| B2 Rolling Guard | 59 | 30 | 40.0% | 10.0% | -0.0056 | -0.6606 |
| BH-FDR Gate | 9 | 9 | 0.0% | 0.0% | -0.0266 | -0.4050 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__willr14__sma100_dist`: Train IC=+0.1400, Lock IC=+0.0526, Lock Sharpe=+0.2861

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `range_expansion_ratio`: Train IC=+0.0895, Lock IC=+0.0645, Lock Sharpe=+0.1756
- `intraday_slope`: Train IC=+0.1254, Lock IC=+0.0621, Lock Sharpe=+0.0417
- `early_trend`: Train IC=+0.1309, Lock IC=+0.0621, Lock Sharpe=+0.0255

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4224_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 373 | 30 | 36.7% | 6.7% | -0.0111 | -0.5859 |
| B2 Rolling Guard | 57 | 30 | 46.7% | 13.3% | +0.0006 | -0.5383 |
| BH-FDR Gate | 14 | 14 | 85.7% | 42.9% | +0.0293 | -0.0662 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1097, Lock IC=+0.0217, Lock Sharpe=+0.4434
- `volume_surge_direction`: Train IC=+0.1060, Lock IC=+0.0217, Lock Sharpe=+0.2779

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__vix__rbreaker_sell_setup_proximity_early__inside_bar_failure_bull`: Train IC=+0.0965, Lock IC=+0.0032, Lock Sharpe=+1.0253
- `combo_abs_diff__iv__growth_momentum_ratio`: Train IC=+0.0200, Lock IC=+0.0582, Lock Sharpe=+0.5647
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1898, Lock IC=+0.0587, Lock Sharpe=+0.1412
- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0027, Lock Sharpe=+0.1377

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `star50_limit_proximity_early`: Train IC=+0.0741, Lock IC=+0.0650, Lock Sharpe=+1.0348
- `gap_pct`: Train IC=+0.1531, Lock IC=+0.0795, Lock Sharpe=+0.7643
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0876, Lock IC=+0.0350, Lock Sharpe=+0.5535
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1883, Lock IC=+0.0616, Lock Sharpe=+0.4395
- `combo_diff__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1968, Lock IC=+0.0587, Lock Sharpe=+0.1412

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 73.0% lock IC > 0, 39.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2409_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 730 | 30 | 90.0% | 33.3% | +0.0359 | -0.1814 |
| B2 Rolling Guard | 77 | 30 | 83.3% | 43.3% | +0.0228 | +0.0073 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__wavetrend_osc_day`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.9731
- `yesterday_lunch_gap`: Train IC=+0.1911, Lock IC=+0.0772, Lock Sharpe=+0.9161
- `combo_mean__bar_vol_4__roc10`: Train IC=+0.1425, Lock IC=+0.0859, Lock Sharpe=+0.7392
- `combo_z_sum__bar_vol_4__roc10`: Train IC=+0.1425, Lock IC=+0.0859, Lock Sharpe=+0.7392
- `combo_rank_max__bar_vol_4__bar_vol_0`: Train IC=+0.1590, Lock IC=+0.0527, Lock Sharpe=+0.4950

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.1361, Lock IC=+0.0431, Lock Sharpe=+0.9119
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.0431, Lock Sharpe=+0.9119
- `star50_limit_proximity_early`: Train IC=+0.1363, Lock IC=+0.0239, Lock Sharpe=+0.6822
- `combo_max__bar_vol_4__yesterday_body_ratio`: Train IC=+0.1823, Lock IC=+0.0712, Lock Sharpe=+0.6677
- `combo_product__bar_vol_4__bar_vol_0`: Train IC=+0.0898, Lock IC=+0.0492, Lock Sharpe=+0.5444

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.1% lock IC > 0, 13.3% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7286_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 451 | 10 | 30.0% | 0.0% | -0.0176 | -0.7672 |
| B2 Rolling Guard | 66 | 11 | 54.5% | 18.2% | +0.0154 | -0.4584 |
| BH-FDR Gate | 7 | 6 | 0.0% | 0.0% | -0.0484 | -1.7936 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bar_vol_4`: Train IC=+0.0880, Lock IC=+0.0834, Lock Sharpe=+0.3081
- `roc20`: Train IC=+0.0576, Lock IC=+0.0709, Lock Sharpe=+0.0586

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2834_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 277 | 30 | 63.3% | 50.0% | +0.0269 | -0.0553 |
| B2 Rolling Guard | 47 | 30 | 26.7% | 10.0% | -0.0050 | -0.2659 |
| BH-FDR Gate | 6 | 6 | 33.3% | 16.7% | -0.0207 | -0.5533 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1124, Lock IC=+0.0772, Lock Sharpe=+1.0118
- `gap_pct`: Train IC=+0.1368, Lock IC=+0.0756, Lock Sharpe=+0.9755
- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.7008
- `combo_z_sum__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.7008
- `combo_mean__sma50_dist__bar_vol_4`: Train IC=+0.1659, Lock IC=+0.0918, Lock Sharpe=+0.6053

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `double_bottom_bull_flag_early`: Train IC=+0.0000, Lock IC=+0.0753, Lock Sharpe=+0.4768
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0364, Lock Sharpe=+0.2740
- `combo_product__sma50_dist__volume_differential_10d`: Train IC=+0.0682, Lock IC=+0.0090, Lock Sharpe=+0.0404

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1622, Lock IC=+0.0130, Lock Sharpe=+0.5948

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 71.0% lock IC > 0, 45.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0514_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1491 | 30 | 100.0% | 90.0% | +0.0864 | +0.3591 |
| B2 Rolling Guard | 310 | 30 | 96.7% | 76.7% | +0.0794 | +0.4069 |
| BH-FDR Gate | 11 | 11 | 0.0% | 0.0% | -0.0113 | -0.7696 |
| B3 Composite Floor | 251 | 30 | 100.0% | 93.3% | +0.1037 | +0.7247 |
| B4 Correlation Gate | 517 | 30 | 100.0% | 80.0% | +0.1030 | +0.5429 |

**Admitted Pool Summary**: 190 features, False Positive Rate = 19.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0909, Mean Lock Sharpe = +0.3604

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2426, Lock IC=+0.0857, Lock Sharpe=+0.8245
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Lock Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Lock Sharpe=+0.7897
- `combo_clamp_diff__max_up_ret__smooth_momentum_structure`: Train IC=+0.2887, Lock IC=+0.0793, Lock Sharpe=+0.7838
- `combo_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2635, Lock IC=+0.1118, Lock Sharpe=+0.7373

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__first_bar_sentiment__early_body_momentum`: Train IC=+0.1912, Lock IC=+0.0630, Lock Sharpe=+1.1475
- `combo_rank_max__first_bar_sentiment__opening_momentum_score`: Train IC=+0.1912, Lock IC=+0.0630, Lock Sharpe=+1.1475
- `combo_rank_max__trend_bar_close_consistency__first_bar_sentiment`: Train IC=+0.2157, Lock IC=+0.0624, Lock Sharpe=+0.9635
- `combo_mean__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Lock Sharpe=+0.7111
- `combo_z_sum__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Lock Sharpe=+0.7111

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_day_regime_conviction`: Train IC=+0.2819, Lock IC=+0.1041, Lock Sharpe=+1.2212
- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2806, Lock IC=+0.1172, Lock Sharpe=+1.1947
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2806, Lock IC=+0.1172, Lock Sharpe=+1.1947
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.2681, Lock IC=+0.1240, Lock Sharpe=+1.1822
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2945, Lock IC=+0.1037, Lock Sharpe=+1.1804

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2965, Lock IC=+0.1083, Lock Sharpe=+1.3443
- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Lock Sharpe=+1.3443
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3068, Lock IC=+0.1015, Lock Sharpe=+1.0848
- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2950, Lock IC=+0.1281, Lock Sharpe=+0.9915
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2950, Lock IC=+0.1281, Lock Sharpe=+0.9915

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 36.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2644_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 954 | 30 | 100.0% | 30.0% | +0.0693 | +0.0390 |
| B2 Rolling Guard | 97 | 30 | 80.0% | 23.3% | +0.0527 | -0.3180 |
| BH-FDR Gate | 53 | 30 | 96.7% | 60.0% | +0.0674 | -0.0635 |
| B3 Composite Floor | 36 | 30 | 100.0% | 40.0% | +0.0517 | -0.0234 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_buy_setup_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__rbreaker_buy_setup_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__rbreaker_buy_setup_proximity_early__limit_down_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__limit_down_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__limit_down_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_day_vwap_dev`: Train IC=+0.1074, Lock IC=+0.0692, Lock Sharpe=+0.3684
- `bar_vol_4`: Train IC=+0.0794, Lock IC=+0.0045, Lock Sharpe=+0.2622
- `combo_diff__donchian_breakout_proximity_20d__yesterday_return`: Train IC=+0.0495, Lock IC=+0.0708, Lock Sharpe=+0.0834
- `combo_z_diff__donchian_breakout_proximity_20d__yesterday_return`: Train IC=+0.0495, Lock IC=+0.0708, Lock Sharpe=+0.0834
- `combo_diff__donchian_breakout_proximity_20d__limit_up_proximity_day`: Train IC=+0.0495, Lock IC=+0.0708, Lock Sharpe=+0.0834

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_buy_setup_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.8136
- `combo_rank_min__limit_down_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.8136
- `first_30min_return`: Train IC=+0.1012, Lock IC=+0.0708, Lock Sharpe=+0.1899
- `open_to_current_return`: Train IC=+0.1012, Lock IC=+0.0708, Lock Sharpe=+0.1899
- `combo_mean__opening_momentum_score__star50_limit_proximity_early`: Train IC=+0.1292, Lock IC=+0.1027, Lock Sharpe=+0.1848

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1742, Lock IC=+0.1046, Lock Sharpe=+1.2349
- `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2116, Lock IC=+0.1196, Lock Sharpe=+1.2060
- `combo_rank_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1842, Lock IC=+0.1130, Lock Sharpe=+0.9668
- `combo_min__opening_momentum_score__rbreaker_sell_setup_proximity_early`: Train IC=+0.1819, Lock IC=+0.1072, Lock Sharpe=+0.5261
- `combo_min__early_body_momentum__rbreaker_sell_setup_proximity_early`: Train IC=+0.1819, Lock IC=+0.1072, Lock Sharpe=+0.5261

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 33.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2357_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 356 | 30 | 46.7% | 43.3% | +0.0117 | -0.2319 |
| B2 Rolling Guard | 66 | 30 | 56.7% | 26.7% | +0.0158 | -0.2361 |
| BH-FDR Gate | 6 | 6 | 66.7% | 66.7% | +0.0726 | +0.1698 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1907, Lock IC=+0.1261, Lock Sharpe=+0.7706
- `gap_pct`: Train IC=+0.1160, Lock IC=+0.0889, Lock Sharpe=+0.4908
- `combo_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0719, Lock Sharpe=+0.4810
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0719, Lock Sharpe=+0.4810
- `combo_z_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0719, Lock Sharpe=+0.4810

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1375, Lock IC=+0.0868, Lock Sharpe=+0.5950
- `close_vs_open_range`: Train IC=+0.0789, Lock IC=+0.0872, Lock Sharpe=+0.4868
- `combo_min__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1062, Lock IC=+0.1197, Lock Sharpe=+0.3869
- `donchian_width_atr_ratio_20d`: Train IC=+0.0254, Lock IC=+0.0944, Lock Sharpe=+0.3236
- `trend_bar_close_consistency`: Train IC=+0.0828, Lock IC=+0.0529, Lock Sharpe=+0.3042

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+1.0439
- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+1.0439
- `combo_mean__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.4994
- `combo_z_sum__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.4994

### 588000ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 23.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7087_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 567 | 30 | 96.7% | 73.3% | +0.0474 | +0.1538 |
| B2 Rolling Guard | 325 | 30 | 36.7% | 36.7% | -0.0216 | -0.2399 |
| BH-FDR Gate | 38 | 30 | 6.7% | 6.7% | -0.0681 | -1.1132 |
| B3 Composite Floor | 386 | 30 | 3.3% | 3.3% | -0.0532 | -0.7547 |
| B4 Correlation Gate | 21 | 21 | 23.8% | 23.8% | -0.0388 | -0.5222 |

**Admitted Pool Summary**: 8 features, False Positive Rate = 50.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0154, Mean Lock Sharpe = -0.2288

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__directional_volume_signature__volume_weighted_momentum_acceleration`: Train IC=+0.2270, Lock IC=+0.0182, Lock Sharpe=+0.9905
- `volume_weighted_momentum_acceleration`: Train IC=+0.2216, Lock IC=+0.0363, Lock Sharpe=+0.9905
- `combo_min__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.2023, Lock IC=+0.0414, Lock Sharpe=+0.6246
- `combo_rel_diff__smooth_momentum_structure__opening_drive_thrust_ratio`: Train IC=+0.2624, Lock IC=+0.0133, Lock Sharpe=+0.4587
- `combo_max__smooth_momentum_structure__early_vwap_acceleration`: Train IC=+0.2063, Lock IC=+0.0786, Lock Sharpe=+0.4001

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_rolling_percentile_60d`: Train IC=+0.1732, Lock IC=+0.0189, Lock Sharpe=+1.3113
- `bar_body_rng_1`: Train IC=+0.1664, Lock IC=+0.0226, Lock Sharpe=+0.8813
- `combo_tri_min__net_volume_flow__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.1668, Lock IC=+0.0198, Lock Sharpe=+0.7037
- `combo_tri_min__opening_auction_imbalance__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.1668, Lock IC=+0.0198, Lock Sharpe=+0.7037
- `vix_diff_1d`: Train IC=+0.2318, Lock IC=+0.0453, Lock Sharpe=+0.6705

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__high_low_sequence_momentum__pullback_depth_ratio`: Train IC=+0.1280, Lock IC=+0.0585, Lock Sharpe=+1.1745
- `combo_product__rsi_opening__pullback_depth_ratio`: Train IC=+0.1280, Lock IC=+0.0585, Lock Sharpe=+1.1745

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__directional_volume_signature__opening_drive_thrust_ratio`: Train IC=+0.3064, Lock IC=+0.0010, Lock Sharpe=+0.1702

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_z_diff__directional_volume_signature__early_vwap_acceleration`: Train IC=+0.2917, Lock IC=+0.0549, Lock Sharpe=+0.9909
- `combo_z_diff__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.3037, Lock IC=+0.0282, Lock Sharpe=+0.1859
- `combo_rel_diff__directional_volume_signature__volume_weighted_momentum_acceleration`: Train IC=+0.2586, Lock IC=+0.0294, Lock Sharpe=+0.1768
- `combo_diff__directional_volume_signature__volume_weighted_momentum_acceleration`: Train IC=+0.2660, Lock IC=+0.0255, Lock Sharpe=+0.1034
- `combo_z_diff__directional_volume_signature__volume_weighted_momentum_acceleration`: Train IC=+0.2660, Lock IC=+0.0255, Lock Sharpe=+0.1034

### 588000ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 30.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4552_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 421 | 30 | 26.7% | 16.7% | -0.0361 | -0.5709 |
| B2 Rolling Guard | 197 | 30 | 53.3% | 20.0% | -0.0030 | -0.5633 |
| BH-FDR Gate | 26 | 26 | 11.5% | 7.7% | -0.0593 | -0.8176 |
| B3 Composite Floor | 3 | 3 | 0.0% | 0.0% | -0.0509 | -0.7630 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_rolling_percentile_60d`: Train IC=+0.2034, Lock IC=+0.0189, Lock Sharpe=+1.5524
- `vix_realized_spread`: Train IC=+0.1995, Lock IC=+0.0695, Lock Sharpe=+1.3777
- `combo_clamp_diff__vix_rolling_percentile_60d__vol5`: Train IC=+0.1964, Lock IC=+0.1052, Lock Sharpe=+1.0313
- `combo_mean__vix_skew_proxy__vix_iv_spread`: Train IC=+0.2519, Lock IC=+0.0492, Lock Sharpe=+0.4210
- `combo_z_sum__vix_skew_proxy__vix_iv_spread`: Train IC=+0.2519, Lock IC=+0.0492, Lock Sharpe=+0.4210

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__iv_envelope_deviation__vix_skew_proxy`: Train IC=+0.2856, Lock IC=+0.0271, Lock Sharpe=+0.1605
- `combo_z_sum__iv_envelope_deviation__vix_skew_proxy`: Train IC=+0.2856, Lock IC=+0.0271, Lock Sharpe=+0.1605
- `combo_mean__iv_envelope_deviation__vix_diff_1d`: Train IC=+0.2414, Lock IC=+0.0346, Lock Sharpe=+0.0660
- `combo_z_sum__iv_envelope_deviation__vix_diff_1d`: Train IC=+0.2414, Lock IC=+0.0346, Lock Sharpe=+0.0660
- `combo_mean__iv_envelope_deviation__yesterday_vix_early_drift`: Train IC=+0.2414, Lock IC=+0.0346, Lock Sharpe=+0.0660

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `lunch_transition_volume_skew`: Train IC=+0.0244, Lock IC=+0.0560, Lock Sharpe=+0.7736
- `combo_abs_diff__vol5__yesterday_day_realized_vol`: Train IC=+0.2014, Lock IC=+0.0186, Lock Sharpe=+0.0524

### 588000ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 37.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2320_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 485 | 30 | 13.3% | 10.0% | -0.0401 | -0.1466 |
| B2 Rolling Guard | 223 | 30 | 16.7% | 3.3% | -0.0443 | -0.1321 |
| BH-FDR Gate | 52 | 30 | 26.7% | 23.3% | -0.0090 | +0.1053 |
| B3 Composite Floor | 12 | 12 | 50.0% | 50.0% | +0.0159 | +0.3303 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__pullback_depth_ratio__opening_drive_thrust_ratio`: Train IC=+0.2129, Lock IC=+0.1599, Lock Sharpe=+0.8991
- `combo_diff__early_vwap_acceleration__directional_volume_signature`: Train IC=+0.2665, Lock IC=+0.0549, Lock Sharpe=+0.7615
- `combo_z_diff__early_vwap_acceleration__directional_volume_signature`: Train IC=+0.2665, Lock IC=+0.0549, Lock Sharpe=+0.7615

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__early_vwap_acceleration__bar_ret_1`: Train IC=+0.2092, Lock IC=+0.0257, Lock Sharpe=+0.3886

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__directional_volume_signature__rbreaker_buy_setup_proximity_early`: Train IC=+0.1138, Lock IC=+0.0176, Lock Sharpe=+1.2122
- `combo_rank_max__directional_volume_signature__limit_down_proximity_early`: Train IC=+0.1138, Lock IC=+0.0176, Lock Sharpe=+1.2122
- `combo_min__opening_drive_thrust_ratio__directional_volume_signature`: Train IC=+0.1711, Lock IC=+0.0010, Lock Sharpe=+1.1356
- `combo_rank_min__pullback_depth_ratio__bar_ret_1`: Train IC=+0.1668, Lock IC=+0.1831, Lock Sharpe=+0.6416
- `bar_vwap_dev_1`: Train IC=+0.1205, Lock IC=+0.0191, Lock Sharpe=+0.5955

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__pullback_depth_ratio__opening_drive_thrust_ratio`: Train IC=+0.2417, Lock IC=+0.0719, Lock Sharpe=+2.2598
- `combo_rank_min__pullback_depth_ratio__tight_channel_persistence`: Train IC=+0.2595, Lock IC=+0.1475, Lock Sharpe=+0.7472
- `combo_mean__directional_volume_signature__bar_ret_1`: Train IC=+0.2562, Lock IC=+0.0284, Lock Sharpe=+0.6247
- `combo_z_sum__directional_volume_signature__bar_ret_1`: Train IC=+0.2562, Lock IC=+0.0284, Lock Sharpe=+0.6247
- `combo_min__pullback_depth_ratio__opening_auction_imbalance`: Train IC=+0.3116, Lock IC=+0.1096, Lock Sharpe=+0.5279

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 73.0% lock IC > 0, 51.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.1793_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1128 | 30 | 100.0% | 66.7% | +0.0931 | +0.5098 |
| B2 Rolling Guard | 382 | 30 | 100.0% | 96.7% | +0.1066 | +0.7239 |
| BH-FDR Gate | 8 | 8 | 87.5% | 50.0% | +0.0507 | +0.2702 |
| B3 Composite Floor | 148 | 30 | 100.0% | 96.7% | +0.1154 | +0.9671 |
| B4 Correlation Gate | 8 | 8 | 100.0% | 87.5% | +0.1090 | +0.9980 |

**Admitted Pool Summary**: 16 features, False Positive Rate = 6.2% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1105, Mean Lock Sharpe = +0.8175

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Lock Sharpe=+1.6125
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Lock Sharpe=+1.6125
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2770, Lock IC=+0.1091, Lock Sharpe=+1.5826
- `combo_rank_min__first_bar_sentiment__limit_down_proximity_early`: Train IC=+0.2419, Lock IC=+0.1134, Lock Sharpe=+1.3320
- `combo_rank_min__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.2419, Lock IC=+0.1134, Lock Sharpe=+1.3320

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Lock Sharpe=+1.7191
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Lock Sharpe=+1.7191
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2801, Lock IC=+0.1413, Lock Sharpe=+1.4595
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2361, Lock IC=+0.1495, Lock Sharpe=+1.4034
- `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.2189, Lock IC=+0.0878, Lock Sharpe=+1.2104

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Lock Sharpe=+1.0460
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Lock Sharpe=+1.0460
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Lock Sharpe=+1.0460
- `close_vs_open_range`: Train IC=+0.0863, Lock IC=+0.0988, Lock Sharpe=+0.7603

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Lock Sharpe=+2.0165
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Lock Sharpe=+2.0165
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2851, Lock IC=+0.1377, Lock Sharpe=+1.6346
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2633, Lock IC=+0.1163, Lock Sharpe=+1.5527
- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2765, Lock IC=+0.1110, Lock Sharpe=+1.4200

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Lock Sharpe=+2.0165
- `combo_z_sum__first_bar_sentiment__limit_down_proximity_early`: Train IC=+0.2093, Lock IC=+0.1182, Lock Sharpe=+1.6439
- `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.2093, Lock IC=+0.1182, Lock Sharpe=+1.6439
- `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2616, Lock IC=+0.1249, Lock Sharpe=+1.3300
- `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2735, Lock IC=+0.1258, Lock Sharpe=+0.7925

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 70.0% lock IC > 0, 46.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0366_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 651 | 30 | 80.0% | 60.0% | +0.0756 | +0.3444 |
| B2 Rolling Guard | 67 | 30 | 96.7% | 96.7% | +0.0862 | +0.6461 |
| BH-FDR Gate | 24 | 24 | 91.7% | 70.8% | +0.0664 | +0.4617 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1406, Lock IC=+0.1688, Lock Sharpe=+1.0747
- `combo_tri_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1450, Lock IC=+0.1570, Lock Sharpe=+1.0547
- `combo_tri_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1450, Lock IC=+0.1570, Lock Sharpe=+1.0547
- `combo_mean__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1398, Lock IC=+0.1469, Lock Sharpe=+0.9504
- `combo_z_sum__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1398, Lock IC=+0.1469, Lock Sharpe=+0.9504

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1336, Lock IC=+0.1014, Lock Sharpe=+1.3455
- `combo_tri_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.0383, Lock IC=+0.0968, Lock Sharpe=+1.0630
- `combo_tri_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.0383, Lock IC=+0.0968, Lock Sharpe=+1.0630
- `combo_min__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1197, Lock IC=+0.1425, Lock Sharpe=+0.9201
- `combo_min__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1197, Lock IC=+0.1425, Lock Sharpe=+0.9201

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `net_volume_flow`: Train IC=+0.0152, Lock IC=+0.1008, Lock Sharpe=+1.6234
- `opening_auction_imbalance`: Train IC=+0.0152, Lock IC=+0.1008, Lock Sharpe=+1.6234
- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1514, Lock IC=+0.1369, Lock Sharpe=+1.4077
- `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.0240, Lock IC=+0.1014, Lock Sharpe=+1.1343
- `combo_z_sum__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.0240, Lock IC=+0.1014, Lock Sharpe=+1.1343

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 37.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4645_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 286 | 30 | 50.0% | 30.0% | -0.0026 | -0.3342 |
| B2 Rolling Guard | 67 | 30 | 50.0% | 33.3% | +0.0060 | -0.2346 |
| BH-FDR Gate | 3 | 3 | 100.0% | 66.7% | +0.1026 | +0.5571 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.1709, Lock IC=+0.0830, Lock Sharpe=+0.9042
- `yesterday_pm_return`: Train IC=+0.1096, Lock IC=+0.0803, Lock Sharpe=+0.7355
- `early_realized_vol`: Train IC=+0.0947, Lock IC=+0.0234, Lock Sharpe=+0.4184
- `yesterday_afternoon_momentum`: Train IC=+0.1068, Lock IC=+0.0755, Lock Sharpe=+0.3907
- `combo_mean__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.2129, Lock IC=+0.0695, Lock Sharpe=+0.3893

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__morning_volume_weighted_momentum__failed_breakout_reversal_early`: Train IC=+0.0039, Lock IC=+0.0717, Lock Sharpe=+1.1309
- `gap_pct`: Train IC=+0.0358, Lock IC=+0.1182, Lock Sharpe=+0.6561
- `yesterday_day_realized_vol`: Train IC=+0.0376, Lock IC=+0.0061, Lock Sharpe=+0.4932
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0619, Lock Sharpe=+0.4303
- `volatility_expansion_trend_vector`: Train IC=+0.0202, Lock IC=+0.0923, Lock Sharpe=+0.3957

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0206, Lock IC=+0.1272, Lock Sharpe=+0.9699
- `limit_down_proximity_early`: Train IC=+0.0205, Lock IC=+0.1272, Lock Sharpe=+0.9699

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 508 | +0.0300 | 100.0% |
| 0.45 | 0.20 | 487 | +0.0300 | 100.0% |
| 0.45 | 0.30 | 421 | +0.0300 | 100.0% |
| 0.45 | 0.40 | 302 | +0.0300 | 100.0% |
| 0.45 | 0.50 | 187 | +0.0300 | 100.0% |
| 0.50 | 0.15 | 498 | +0.0300 | 100.0% |
| 0.50 | 0.25 | 465 | +0.0300 | 100.0% |
| 0.50 | 0.35 | 360 | +0.0300 | 100.0% |
| 0.50 | 0.45 | 253 | +0.0300 | 100.0% |
| 0.55 | 0.10 | 497 | +0.0300 | 100.0% |
| 0.55 | 0.20 | 486 | +0.0300 | 100.0% |
| 0.55 | 0.30 | 421 | +0.0300 | 100.0% |
| 0.55 | 0.40 | 302 | +0.0300 | 100.0% |
| 0.55 | 0.50 | 187 | +0.0300 | 100.0% |
| 0.60 | 0.15 | 433 | +0.0300 | 100.0% |
| 0.60 | 0.25 | 432 | +0.0300 | 100.0% |
| 0.60 | 0.35 | 360 | +0.0300 | 100.0% |
| 0.60 | 0.45 | 253 | +0.0300 | 100.0% |
| 0.65 | 0.10 | 292 | +0.0300 | 100.0% |
| 0.65 | 0.20 | 292 | +0.0300 | 100.0% |
| 0.65 | 0.30 | 290 | +0.0300 | 100.0% |
| 0.65 | 0.40 | 280 | +0.0300 | 100.0% |
| 0.65 | 0.50 | 187 | +0.0300 | 100.0% |
| 0.70 | 0.15 | 145 | +0.0290 | 100.0% |
| 0.70 | 0.25 | 145 | +0.0290 | 100.0% |
| 0.70 | 0.35 | 145 | +0.0290 | 100.0% |
| 0.70 | 0.45 | 145 | +0.0290 | 100.0% |
| 0.75 | 0.10 | 31 | +0.0215 | 80.0% |
| 0.75 | 0.20 | 31 | +0.0215 | 80.0% |
| 0.75 | 0.30 | 31 | +0.0215 | 80.0% |
| 0.75 | 0.40 | 31 | +0.0215 | 80.0% |
| 0.75 | 0.50 | 31 | +0.0215 | 80.0% |
| 0.80 | 0.15 | 11 | +0.0262 | 100.0% |
| 0.80 | 0.25 | 11 | +0.0262 | 100.0% |
| 0.80 | 0.35 | 11 | +0.0262 | 100.0% |
| 0.80 | 0.45 | 11 | +0.0262 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 508 candidates, mean lock IC=+0.0300, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 16 | -0.0287 | 0.0% |
| 0.45 | 0.20 | 10 | -0.0244 | 0.0% |
| 0.45 | 0.30 | 5 | -0.0269 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 11 | -0.0287 | 0.0% |
| 0.50 | 0.25 | 8 | -0.0223 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 9 | -0.0266 | 0.0% |
| 0.55 | 0.20 | 8 | -0.0223 | 0.0% |
| 0.55 | 0.30 | 5 | -0.0269 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.25 → 8 candidates, mean lock IC=-0.0223, 0.0% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 20 | +0.0365 | 100.0% |
| 0.45 | 0.20 | 10 | +0.0268 | 80.0% |
| 0.45 | 0.30 | 7 | +0.0252 | 85.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 15 | +0.0298 | 90.0% |
| 0.50 | 0.25 | 8 | +0.0240 | 87.5% |
| 0.50 | 0.35 | 4 | +0.0201 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 15 | +0.0348 | 90.0% |
| 0.55 | 0.20 | 10 | +0.0268 | 80.0% |
| 0.55 | 0.30 | 7 | +0.0252 | 85.7% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 7 | +0.0252 | 85.7% |
| 0.60 | 0.25 | 7 | +0.0252 | 85.7% |
| 0.60 | 0.35 | 4 | +0.0201 | 100.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 20 candidates, mean lock IC=+0.0365, 100.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 501 | +0.0498 | 100.0% |
| 0.45 | 0.20 | 488 | +0.0498 | 100.0% |
| 0.45 | 0.30 | 464 | +0.0498 | 100.0% |
| 0.45 | 0.40 | 437 | +0.0498 | 100.0% |
| 0.45 | 0.50 | 417 | +0.0508 | 100.0% |
| 0.50 | 0.15 | 495 | +0.0498 | 100.0% |
| 0.50 | 0.25 | 478 | +0.0498 | 100.0% |
| 0.50 | 0.35 | 451 | +0.0498 | 100.0% |
| 0.50 | 0.45 | 431 | +0.0498 | 100.0% |
| 0.55 | 0.10 | 495 | +0.0498 | 100.0% |
| 0.55 | 0.20 | 488 | +0.0498 | 100.0% |
| 0.55 | 0.30 | 464 | +0.0498 | 100.0% |
| 0.55 | 0.40 | 437 | +0.0498 | 100.0% |
| 0.55 | 0.50 | 417 | +0.0508 | 100.0% |
| 0.60 | 0.15 | 469 | +0.0498 | 100.0% |
| 0.60 | 0.25 | 468 | +0.0498 | 100.0% |
| 0.60 | 0.35 | 451 | +0.0498 | 100.0% |
| 0.60 | 0.45 | 431 | +0.0498 | 100.0% |
| 0.65 | 0.10 | 437 | +0.0498 | 100.0% |
| 0.65 | 0.20 | 437 | +0.0498 | 100.0% |
| 0.65 | 0.30 | 437 | +0.0498 | 100.0% |
| 0.65 | 0.40 | 433 | +0.0498 | 100.0% |
| 0.65 | 0.50 | 417 | +0.0508 | 100.0% |
| 0.70 | 0.15 | 403 | +0.0498 | 100.0% |
| 0.70 | 0.25 | 403 | +0.0498 | 100.0% |
| 0.70 | 0.35 | 403 | +0.0498 | 100.0% |
| 0.70 | 0.45 | 403 | +0.0498 | 100.0% |
| 0.75 | 0.10 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.20 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.30 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.40 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.50 | 361 | +0.0394 | 100.0% |
| 0.80 | 0.15 | 267 | +0.0469 | 100.0% |
| 0.80 | 0.25 | 267 | +0.0469 | 100.0% |
| 0.80 | 0.35 | 267 | +0.0469 | 100.0% |
| 0.80 | 0.45 | 267 | +0.0469 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 417 candidates, mean lock IC=+0.0508, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 26 | -0.0446 | 0.0% |
| 0.45 | 0.20 | 8 | -0.0314 | 14.3% |
| 0.45 | 0.30 | 6 | -0.0484 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 15 | -0.0446 | 0.0% |
| 0.50 | 0.25 | 7 | -0.0484 | 0.0% |
| 0.50 | 0.35 | 5 | -0.0447 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 9 | -0.0416 | 0.0% |
| 0.55 | 0.20 | 6 | -0.0484 | 0.0% |
| 0.55 | 0.30 | 6 | -0.0484 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 6 | -0.0484 | 0.0% |
| 0.60 | 0.25 | 6 | -0.0484 | 0.0% |
| 0.60 | 0.35 | 5 | -0.0447 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 8 candidates, mean lock IC=-0.0314, 14.3% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | -0.0044 | 50.0% |
| 0.45 | 0.20 | 7 | +0.0095 | 57.1% |
| 0.45 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | -0.0095 | 44.4% |
| 0.50 | 0.25 | 3 | -0.0020 | 66.7% |
| 0.50 | 0.35 | 3 | -0.0020 | 66.7% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | -0.0118 | 42.9% |
| 0.55 | 0.20 | 5 | -0.0064 | 40.0% |
| 0.55 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 4 | -0.0068 | 50.0% |
| 0.60 | 0.25 | 3 | -0.0020 | 66.7% |
| 0.60 | 0.35 | 3 | -0.0020 | 66.7% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 7 candidates, mean lock IC=+0.0095, 57.1% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1517 | +0.1210 | 100.0% |
| 0.45 | 0.20 | 1485 | +0.1210 | 100.0% |
| 0.45 | 0.30 | 1416 | +0.1210 | 100.0% |
| 0.45 | 0.40 | 1251 | +0.1210 | 100.0% |
| 0.45 | 0.50 | 998 | +0.1210 | 100.0% |
| 0.50 | 0.15 | 1508 | +0.1210 | 100.0% |
| 0.50 | 0.25 | 1471 | +0.1210 | 100.0% |
| 0.50 | 0.35 | 1340 | +0.1210 | 100.0% |
| 0.50 | 0.45 | 1129 | +0.1210 | 100.0% |
| 0.55 | 0.10 | 1512 | +0.1210 | 100.0% |
| 0.55 | 0.20 | 1485 | +0.1210 | 100.0% |
| 0.55 | 0.30 | 1416 | +0.1210 | 100.0% |
| 0.55 | 0.40 | 1251 | +0.1210 | 100.0% |
| 0.55 | 0.50 | 998 | +0.1210 | 100.0% |
| 0.60 | 0.15 | 1454 | +0.1210 | 100.0% |
| 0.60 | 0.25 | 1444 | +0.1210 | 100.0% |
| 0.60 | 0.35 | 1337 | +0.1210 | 100.0% |
| 0.60 | 0.45 | 1129 | +0.1210 | 100.0% |
| 0.65 | 0.10 | 1240 | +0.1210 | 100.0% |
| 0.65 | 0.20 | 1240 | +0.1210 | 100.0% |
| 0.65 | 0.30 | 1236 | +0.1210 | 100.0% |
| 0.65 | 0.40 | 1198 | +0.1210 | 100.0% |
| 0.65 | 0.50 | 992 | +0.1210 | 100.0% |
| 0.70 | 0.15 | 865 | +0.1210 | 100.0% |
| 0.70 | 0.25 | 865 | +0.1210 | 100.0% |
| 0.70 | 0.35 | 865 | +0.1210 | 100.0% |
| 0.70 | 0.45 | 857 | +0.1210 | 100.0% |
| 0.75 | 0.10 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.20 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.30 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.40 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.50 | 454 | +0.1210 | 100.0% |
| 0.80 | 0.15 | 161 | +0.1058 | 100.0% |
| 0.80 | 0.25 | 161 | +0.1058 | 100.0% |
| 0.80 | 0.35 | 161 | +0.1058 | 100.0% |
| 0.80 | 0.45 | 161 | +0.1058 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1517 candidates, mean lock IC=+0.1210, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 110 | +0.0497 | 100.0% |
| 0.45 | 0.20 | 85 | +0.0497 | 100.0% |
| 0.45 | 0.30 | 45 | +0.0362 | 100.0% |
| 0.45 | 0.40 | 8 | +0.0521 | 87.5% |
| 0.45 | 0.50 | 2 | +0.1072 | 100.0% |
| 0.50 | 0.15 | 90 | +0.0497 | 100.0% |
| 0.50 | 0.25 | 63 | +0.0670 | 100.0% |
| 0.50 | 0.35 | 19 | +0.0511 | 100.0% |
| 0.50 | 0.45 | 4 | +0.0783 | 100.0% |
| 0.55 | 0.10 | 101 | +0.0497 | 100.0% |
| 0.55 | 0.20 | 84 | +0.0497 | 100.0% |
| 0.55 | 0.30 | 45 | +0.0362 | 100.0% |
| 0.55 | 0.40 | 8 | +0.0521 | 87.5% |
| 0.55 | 0.50 | 2 | +0.1072 | 100.0% |
| 0.60 | 0.15 | 56 | +0.0362 | 100.0% |
| 0.60 | 0.25 | 55 | +0.0362 | 100.0% |
| 0.60 | 0.35 | 19 | +0.0511 | 100.0% |
| 0.60 | 0.45 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.10 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.20 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.30 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.40 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.50 | 2 | +0.1072 | 100.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.45 → 4 candidates, mean lock IC=+0.0783, 100.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 15 | +0.0574 | 80.0% |
| 0.45 | 0.20 | 3 | -0.0177 | 33.3% |
| 0.45 | 0.30 | 1 | -0.0236 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | +0.0579 | 77.8% |
| 0.50 | 0.25 | 1 | -0.0236 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0726 | 66.7% |
| 0.55 | 0.20 | 2 | -0.0281 | 0.0% |
| 0.55 | 0.30 | 1 | -0.0236 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | +0.1180 | 100.0% |
| 0.60 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 6 candidates, mean lock IC=+0.0726, 66.7% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 954 | -0.0254 | 0.0% |
| 0.45 | 0.20 | 900 | -0.0254 | 0.0% |
| 0.45 | 0.30 | 796 | -0.0254 | 0.0% |
| 0.45 | 0.40 | 697 | -0.0254 | 0.0% |
| 0.45 | 0.50 | 595 | -0.0254 | 0.0% |
| 0.50 | 0.15 | 925 | -0.0254 | 0.0% |
| 0.50 | 0.25 | 840 | -0.0254 | 0.0% |
| 0.50 | 0.35 | 748 | -0.0254 | 0.0% |
| 0.50 | 0.45 | 634 | -0.0254 | 0.0% |
| 0.55 | 0.10 | 912 | -0.0254 | 0.0% |
| 0.55 | 0.20 | 883 | -0.0254 | 0.0% |
| 0.55 | 0.30 | 796 | -0.0254 | 0.0% |
| 0.55 | 0.40 | 697 | -0.0254 | 0.0% |
| 0.55 | 0.50 | 595 | -0.0254 | 0.0% |
| 0.60 | 0.15 | 817 | -0.0254 | 0.0% |
| 0.60 | 0.25 | 785 | -0.0254 | 0.0% |
| 0.60 | 0.35 | 737 | -0.0254 | 0.0% |
| 0.60 | 0.45 | 634 | -0.0254 | 0.0% |
| 0.65 | 0.10 | 694 | -0.0254 | 0.0% |
| 0.65 | 0.20 | 694 | -0.0254 | 0.0% |
| 0.65 | 0.30 | 691 | -0.0254 | 0.0% |
| 0.65 | 0.40 | 670 | -0.0254 | 0.0% |
| 0.65 | 0.50 | 593 | -0.0254 | 0.0% |
| 0.70 | 0.15 | 569 | -0.0254 | 0.0% |
| 0.70 | 0.25 | 569 | -0.0254 | 0.0% |
| 0.70 | 0.35 | 569 | -0.0254 | 0.0% |
| 0.70 | 0.45 | 563 | -0.0254 | 0.0% |
| 0.75 | 0.10 | 403 | -0.0254 | 0.0% |
| 0.75 | 0.20 | 403 | -0.0254 | 0.0% |
| 0.75 | 0.30 | 403 | -0.0254 | 0.0% |
| 0.75 | 0.40 | 403 | -0.0254 | 0.0% |
| 0.75 | 0.50 | 403 | -0.0254 | 0.0% |
| 0.80 | 0.15 | 161 | -0.0254 | 0.0% |
| 0.80 | 0.25 | 161 | -0.0254 | 0.0% |
| 0.80 | 0.35 | 161 | -0.0254 | 0.0% |
| 0.80 | 0.45 | 161 | -0.0254 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 954 candidates, mean lock IC=-0.0254, 0.0% positive

### 588000ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 62 | -0.0396 | 20.0% |
| 0.45 | 0.20 | 28 | -0.0374 | 10.0% |
| 0.45 | 0.30 | 20 | -0.0392 | 10.0% |
| 0.45 | 0.40 | 13 | -0.0346 | 10.0% |
| 0.45 | 0.50 | 10 | -0.0346 | 10.0% |
| 0.50 | 0.15 | 36 | -0.0374 | 10.0% |
| 0.50 | 0.25 | 25 | -0.0366 | 10.0% |
| 0.50 | 0.35 | 16 | -0.0392 | 10.0% |
| 0.50 | 0.45 | 11 | -0.0346 | 10.0% |
| 0.55 | 0.10 | 33 | -0.0374 | 10.0% |
| 0.55 | 0.20 | 27 | -0.0374 | 10.0% |
| 0.55 | 0.30 | 20 | -0.0392 | 10.0% |
| 0.55 | 0.40 | 13 | -0.0346 | 10.0% |
| 0.55 | 0.50 | 10 | -0.0346 | 10.0% |
| 0.60 | 0.15 | 22 | -0.0376 | 10.0% |
| 0.60 | 0.25 | 22 | -0.0376 | 10.0% |
| 0.60 | 0.35 | 16 | -0.0392 | 10.0% |
| 0.60 | 0.45 | 11 | -0.0346 | 10.0% |
| 0.65 | 0.10 | 15 | -0.0379 | 10.0% |
| 0.65 | 0.20 | 15 | -0.0379 | 10.0% |
| 0.65 | 0.30 | 15 | -0.0379 | 10.0% |
| 0.65 | 0.40 | 13 | -0.0346 | 10.0% |
| 0.65 | 0.50 | 10 | -0.0346 | 10.0% |
| 0.70 | 0.15 | 2 | -0.0545 | 0.0% |
| 0.70 | 0.25 | 2 | -0.0545 | 0.0% |
| 0.70 | 0.35 | 2 | -0.0545 | 0.0% |
| 0.70 | 0.45 | 2 | -0.0545 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.50, ir_thr=0.10 → 59 candidates, mean lock IC=-0.0318, 30.0% positive

### 588000ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 128 | +0.0198 | 60.0% |
| 0.45 | 0.20 | 74 | +0.0198 | 60.0% |
| 0.45 | 0.30 | 42 | +0.0230 | 60.0% |
| 0.45 | 0.40 | 19 | +0.0368 | 50.0% |
| 0.45 | 0.50 | 7 | +0.0322 | 42.9% |
| 0.50 | 0.15 | 84 | +0.0198 | 60.0% |
| 0.50 | 0.25 | 51 | +0.0198 | 60.0% |
| 0.50 | 0.35 | 28 | +0.0269 | 40.0% |
| 0.50 | 0.45 | 12 | +0.0262 | 60.0% |
| 0.55 | 0.10 | 71 | +0.0198 | 60.0% |
| 0.55 | 0.20 | 61 | +0.0198 | 60.0% |
| 0.55 | 0.30 | 42 | +0.0230 | 60.0% |
| 0.55 | 0.40 | 19 | +0.0368 | 50.0% |
| 0.55 | 0.50 | 7 | +0.0322 | 42.9% |
| 0.60 | 0.15 | 39 | +0.0003 | 40.0% |
| 0.60 | 0.25 | 32 | +0.0005 | 40.0% |
| 0.60 | 0.35 | 24 | +0.0234 | 40.0% |
| 0.60 | 0.45 | 12 | +0.0262 | 60.0% |
| 0.65 | 0.10 | 17 | +0.0267 | 50.0% |
| 0.65 | 0.20 | 17 | +0.0267 | 50.0% |
| 0.65 | 0.30 | 17 | +0.0267 | 50.0% |
| 0.65 | 0.40 | 13 | +0.0043 | 40.0% |
| 0.65 | 0.50 | 7 | +0.0322 | 42.9% |
| 0.70 | 0.15 | 4 | +0.0169 | 25.0% |
| 0.70 | 0.25 | 4 | +0.0169 | 25.0% |
| 0.70 | 0.35 | 4 | +0.0169 | 25.0% |
| 0.70 | 0.45 | 4 | +0.0169 | 25.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 19 candidates, mean lock IC=+0.0368, 50.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 714 | +0.1299 | 100.0% |
| 0.45 | 0.20 | 679 | +0.1299 | 100.0% |
| 0.45 | 0.30 | 537 | +0.1299 | 100.0% |
| 0.45 | 0.40 | 391 | +0.1299 | 100.0% |
| 0.45 | 0.50 | 215 | +0.1299 | 100.0% |
| 0.50 | 0.15 | 696 | +0.1299 | 100.0% |
| 0.50 | 0.25 | 613 | +0.1299 | 100.0% |
| 0.50 | 0.35 | 461 | +0.1299 | 100.0% |
| 0.50 | 0.45 | 315 | +0.1299 | 100.0% |
| 0.55 | 0.10 | 699 | +0.1299 | 100.0% |
| 0.55 | 0.20 | 672 | +0.1299 | 100.0% |
| 0.55 | 0.30 | 537 | +0.1299 | 100.0% |
| 0.55 | 0.40 | 391 | +0.1299 | 100.0% |
| 0.55 | 0.50 | 215 | +0.1299 | 100.0% |
| 0.60 | 0.15 | 611 | +0.1299 | 100.0% |
| 0.60 | 0.25 | 574 | +0.1299 | 100.0% |
| 0.60 | 0.35 | 455 | +0.1299 | 100.0% |
| 0.60 | 0.45 | 315 | +0.1299 | 100.0% |
| 0.65 | 0.10 | 380 | +0.1299 | 100.0% |
| 0.65 | 0.20 | 380 | +0.1299 | 100.0% |
| 0.65 | 0.30 | 377 | +0.1299 | 100.0% |
| 0.65 | 0.40 | 345 | +0.1299 | 100.0% |
| 0.65 | 0.50 | 210 | +0.1299 | 100.0% |
| 0.70 | 0.15 | 148 | +0.1264 | 100.0% |
| 0.70 | 0.25 | 148 | +0.1264 | 100.0% |
| 0.70 | 0.35 | 148 | +0.1264 | 100.0% |
| 0.70 | 0.45 | 145 | +0.1264 | 100.0% |
| 0.75 | 0.10 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.20 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.30 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.40 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.50 | 19 | +0.1295 | 100.0% |
| 0.80 | 0.15 | 4 | -0.0044 | 0.0% |
| 0.80 | 0.25 | 4 | -0.0044 | 0.0% |
| 0.80 | 0.35 | 4 | -0.0044 | 0.0% |
| 0.80 | 0.45 | 4 | -0.0044 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 714 candidates, mean lock IC=+0.1299, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 43 | +0.0757 | 100.0% |
| 0.45 | 0.20 | 28 | +0.0785 | 100.0% |
| 0.45 | 0.30 | 12 | +0.0614 | 90.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 33 | +0.0748 | 100.0% |
| 0.50 | 0.25 | 15 | +0.0761 | 100.0% |
| 0.50 | 0.35 | 2 | +0.1005 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 28 | +0.0719 | 100.0% |
| 0.55 | 0.20 | 22 | +0.0719 | 100.0% |
| 0.55 | 0.30 | 12 | +0.0614 | 90.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 11 | +0.0542 | 90.0% |
| 0.60 | 0.25 | 11 | +0.0542 | 90.0% |
| 0.60 | 0.35 | 1 | +0.0641 | 100.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 28 candidates, mean lock IC=+0.0785, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | +0.0688 | 88.9% |
| 0.45 | 0.20 | 1 | +0.0532 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 5 | +0.0842 | 100.0% |
| 0.50 | 0.25 | 1 | +0.0532 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | +0.0944 | 100.0% |
| 0.55 | 0.20 | 1 | +0.0532 | 100.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | +0.0532 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0532 | 100.0% |
| 0.60 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.70 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.55, ir_thr=0.15 → 3 candidates, mean lock IC=+0.1026, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1304 | +0.0983 | +0.0281 | 0.22x | 2017-07-10 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +0.1386 | +0.0760 | +0.0157 | 0.11x | 2017-06-09 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1259 | +0.0769 | +0.0342 | 0.27x | 2017-06-09 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1182 | +0.0975 | +0.0517 | 0.44x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1353 | +0.0868 | +0.0337 | 0.25x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1169 | +0.0920 | +0.0189 | 0.16x | 2017-05-09 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1179 | +0.0987 | +0.0403 | 0.34x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1314 | +0.0963 | +0.0210 | 0.16x | 2017-06-09 |
| `rbreaker_sell_setup_proximity_early` | +0.0953 | +0.0781 | +0.0616 | 0.65x | 2016-08-24 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1068 | +0.1138 | -0.0030 | -0.03x | 2015-03-16 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1231 | +0.0991 | +0.0207 | 0.17x | 2015-02-06 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.0983 | +0.1152 | -0.0103 | -0.10x | 2015-02-06 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1182 | +0.0960 | +0.0379 | 0.32x | 2017-08-08 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1123 | +0.1251 | -0.0129 | -0.11x | 2015-02-06 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1100 | +0.0960 | +0.0480 | 0.44x | 2016-08-24 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +0.0899 | +0.0831 | +0.0120 | 0.13x | 2010-10-15 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1046 | +0.1154 | -0.0220 | -0.21x | 2015-02-06 |
| `combo_mean__max_up_ret__volume_surge_direction` | +0.0991 | +0.0955 | +0.0110 | 0.11x | 2014-07-04 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1169 | +0.0957 | -0.0146 | -0.12x | 2017-06-09 |
| `star50_limit_proximity_early` | +0.0893 | +0.0629 | +0.0650 | 0.73x | 2011-09-20 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +0.1193 | +0.0915 | +0.0184 | 0.15x | 2017-02-06 |
| `combo_max__bar_body_rng_0__volume_surge_direction` | +0.0825 | +0.1030 | +0.0197 | 0.24x | 2013-08-21 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.2092 | +0.0746 | +0.1174 | 0.56x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2080 | +0.0598 | +0.1208 | 0.58x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.2070 | +0.0656 | +0.1200 | 0.58x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1763 | +0.0683 | +0.1255 | 0.71x | No decay |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2079 | +0.0861 | +0.1215 | 0.58x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1868 | +0.0650 | +0.1297 | 0.69x | 2016-08-24 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1736 | +0.0539 | +0.1135 | 0.65x | 2022-12-15 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.2007 | +0.0828 | +0.0810 | 0.40x | 2025-07-24 |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1928 | +0.1003 | +0.0898 | 0.47x | 2016-11-01 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1948 | +0.0841 | +0.1114 | 0.57x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.2221 | +0.1033 | +0.1081 | 0.49x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +0.1967 | +0.0924 | +0.0808 | 0.41x | No decay |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.2063 | +0.0954 | +0.0879 | 0.43x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1814 | +0.0513 | +0.0990 | 0.55x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | +0.1917 | +0.0886 | +0.1058 | 0.55x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.2259 | +0.0912 | +0.1124 | 0.50x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2040 | +0.0702 | +0.1253 | 0.61x | No decay |
| `combo_clamp_diff__max_up_ret__body_size_progression` | +0.1805 | +0.0837 | +0.0794 | 0.44x | 2025-06-25 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | +0.2034 | +0.0961 | +0.1065 | 0.52x | No decay |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.1614 | +0.0707 | +0.0685 | 0.42x | 2022-09-09 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1801 | +0.0529 | +0.0965 | 0.54x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1833 | +0.0722 | +0.1184 | 0.65x | No decay |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.1764 | +0.0853 | +0.0660 | 0.37x | 2020-01-06 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1735 | +0.0840 | +0.0801 | 0.46x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1698 | +0.0576 | +0.0907 | 0.53x | No decay |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.2007 | +0.0874 | +0.0944 | 0.47x | No decay |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1733 | +0.0537 | +0.1135 | 0.65x | 2022-12-15 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +0.1713 | +0.0886 | +0.0949 | 0.55x | 2020-02-12 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1962 | +0.0789 | +0.0839 | 0.43x | No decay |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | +0.1557 | +0.0429 | +0.1111 | 0.71x | 2016-08-24 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1817 | +0.0598 | +0.0802 | 0.44x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1980 | +0.1056 | +0.0851 | 0.43x | 2021-07-28 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | +0.1717 | +0.0707 | +0.1324 | 0.77x | 2016-09-26 |
| `combo_diff__max_up_ret__body_size_progression` | +0.1803 | +0.0847 | +0.0760 | 0.42x | 2025-06-25 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | +0.2085 | +0.0842 | +0.1090 | 0.52x | 2016-11-30 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1721 | +0.1324 | +0.1001 | 0.58x | No decay |
| `rbreaker_sell_setup_proximity_early` | +0.1745 | +0.0776 | +0.1261 | 0.72x | 2021-07-28 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | +0.1516 | +0.0424 | +0.0890 | 0.59x | 2020-01-06 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1632 | +0.0776 | +0.1169 | 0.72x | 2016-09-26 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.2095 | +0.1042 | +0.0884 | 0.42x | 2016-11-30 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.2027 | +0.0752 | +0.1213 | 0.60x | No decay |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +0.1587 | +0.0556 | +0.1330 | 0.84x | 2016-09-26 |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | +0.1655 | +0.0733 | +0.1058 | 0.64x | 2021-09-28 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1965 | +0.1027 | +0.0953 | 0.48x | 2016-11-01 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | +0.1977 | +0.0774 | +0.0870 | 0.44x | 2022-12-15 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +0.1831 | +0.0650 | +0.0735 | 0.40x | 2014-06-05 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1923 | +0.0733 | +0.1091 | 0.57x | No decay |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | +0.1449 | +0.0732 | +0.0761 | 0.53x | 2020-02-12 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | +0.1962 | +0.0960 | +0.0865 | 0.44x | 2016-11-30 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1724 | +0.0837 | +0.0867 | 0.50x | 2016-12-29 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | +0.1593 | +0.0626 | +0.1274 | 0.80x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +0.1924 | +0.1024 | +0.0948 | 0.49x | 2016-11-30 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1883 | +0.0858 | +0.1163 | 0.62x | No decay |
| `combo_mean__max_up_ret__first_bar_sentiment` | +0.1900 | +0.0953 | +0.0826 | 0.43x | 2020-01-06 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | +0.1919 | +0.0973 | +0.0916 | 0.48x | 2016-11-01 |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1687 | +0.0926 | +0.0725 | 0.43x | 2016-11-01 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.2006 | +0.0838 | +0.0811 | 0.40x | 2025-07-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | +0.1832 | +0.1093 | +0.1117 | 0.61x | 2016-09-26 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1813 | +0.0811 | +0.0773 | 0.43x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +0.1498 | +0.0575 | +0.1183 | 0.79x | 2025-06-25 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +0.1543 | +0.0490 | +0.1100 | 0.71x | 2011-09-20 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | +0.0436 | +0.0419 | +0.0020 | 0.05x | 2010-10-15 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.2003 | +0.0943 | +0.1164 | 0.58x | No decay |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1534 | +0.0538 | +0.1082 | 0.71x | 2016-09-26 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | +0.1510 | +0.0524 | +0.1109 | 0.73x | 2020-12-18 |
| `combo_mean__max_up_ret__trend_bar_close_consistency` | +0.1745 | +0.1011 | +0.0653 | 0.37x | 2016-11-01 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1896 | +0.1108 | +0.0780 | 0.41x | 2026-04-07 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | +0.1837 | +0.0726 | +0.1124 | 0.61x | No decay |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1680 | +0.0685 | +0.1219 | 0.73x | 2016-09-26 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1511 | +0.0727 | +0.1114 | 0.74x | 2016-08-24 |
| `opening_drive_thrust_ratio` | +0.1970 | +0.0973 | +0.0870 | 0.44x | No decay |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | +0.2089 | +0.0980 | +0.0809 | 0.39x | No decay |
| `combo_sig_product__max_up_ret__early_body_momentum` | +0.1855 | +0.1228 | +0.0913 | 0.49x | No decay |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | +0.1527 | +0.0894 | +0.0849 | 0.56x | 2016-11-01 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1601 | +0.0741 | +0.1139 | 0.71x | No decay |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1767 | +0.1012 | +0.0808 | 0.46x | 2020-01-06 |
| `combo_max__max_up_ret__early_body_momentum` | +0.1820 | +0.0991 | +0.0693 | 0.38x | 2016-11-01 |
| `combo_min__max_up_ret__close_vs_open_range` | +0.1716 | +0.0984 | +0.0916 | 0.53x | 2020-01-06 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1745 | +0.0857 | +0.0900 | 0.52x | No decay |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | +0.1871 | +0.0688 | +0.0924 | 0.49x | No decay |
| `combo_min__close_vs_open_range__high_low_sequence_momentum` | +0.1485 | +0.0935 | +0.0810 | 0.55x | 2016-11-01 |
| `max_up_ret` | +0.1971 | +0.0995 | +0.0778 | 0.39x | No decay |
| `combo_rank_max__max_up_ret__early_body_momentum` | +0.1877 | +0.1103 | +0.0738 | 0.39x | 2016-11-30 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1736 | +0.1299 | +0.0540 | 0.31x | 2016-12-29 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | +0.1860 | +0.1205 | +0.0723 | 0.39x | 2016-12-29 |
| `combo_mean__max_up_ret__close_vs_open_range` | +0.1832 | +0.1048 | +0.0821 | 0.45x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.2070 | +0.1118 | +0.0816 | 0.39x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1791 | +0.1065 | +0.0651 | 0.36x | 2016-12-29 |
| `combo_rank_max__bar_ret_0__max_down_ret` | +0.1754 | +0.0656 | +0.0972 | 0.55x | No decay |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +0.1524 | +0.0567 | +0.1011 | 0.66x | 2020-01-06 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | +0.1585 | +0.0997 | +0.0753 | 0.48x | 2020-01-06 |
| `combo_max__max_up_ret__close_vs_open_range` | +0.1863 | +0.1051 | +0.0758 | 0.41x | 2016-11-01 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | +0.1615 | +0.0787 | +0.1181 | 0.73x | No decay |
| `combo_min__max_up_ret__high_low_sequence_momentum` | +0.1732 | +0.1147 | +0.0846 | 0.49x | 2020-01-06 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | +0.1784 | +0.0872 | +0.0876 | 0.49x | 2016-11-01 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | +0.1498 | +0.0504 | +0.1093 | 0.73x | 2020-12-18 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | +0.1410 | +0.0591 | +0.0861 | 0.61x | 2016-11-01 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | +0.0195 | +0.0240 | +0.0027 | 0.14x | 2010-10-15 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | +0.1325 | +0.0738 | +0.0891 | 0.67x | 2017-05-09 |
| `combo_min__close_vs_open_range__bar_ret_0` | +0.1519 | +0.0578 | +0.1022 | 0.67x | 2020-01-06 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +0.1854 | +0.0700 | +0.0938 | 0.51x | 2016-11-30 |
| `combo_mean__max_up_ret__first_bar_return` | +0.1922 | +0.0908 | +0.0779 | 0.41x | No decay |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1729 | +0.0738 | +0.0795 | 0.46x | 2022-12-15 |
| `combo_mean__volatility_expansion_trend_vector__close_vs_open_range` | +0.1526 | +0.0948 | +0.0862 | 0.56x | 2016-11-01 |
| `combo_min__net_volume_flow__bar_ret_0` | +0.1569 | +0.0878 | +0.0945 | 0.60x | 2016-11-01 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | +0.1876 | +0.1062 | +0.0737 | 0.39x | 2016-11-01 |
| `net_volume_flow` | +0.1624 | +0.0989 | +0.0847 | 0.52x | 2016-11-01 |
| `combo_rank_min__max_up_ret__bar_ret_0` | +0.1862 | +0.0688 | +0.0694 | 0.37x | No decay |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | +0.2023 | +0.0903 | +0.0898 | 0.44x | No decay |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +0.1936 | +0.0963 | +0.0639 | 0.33x | 2016-11-01 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1759 | +0.1452 | +0.0968 | 0.55x | No decay |
| `combo_min__first_bar_sentiment__bar_ret_0` | +0.1474 | +0.0681 | +0.0763 | 0.52x | 2013-09-23 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1940 | +0.1034 | +0.0859 | 0.44x | 2020-01-06 |
| `combo_max__max_up_ret__first_bar_return` | +0.1801 | +0.0812 | +0.0748 | 0.42x | No decay |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +0.1842 | +0.0818 | +0.0941 | 0.51x | 2020-01-06 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1564 | +0.0479 | +0.1143 | 0.73x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1915 | +0.0963 | +0.1115 | 0.58x | No decay |
| `combo_max__net_volume_flow__first_bar_sentiment` | +0.1624 | +0.0869 | +0.0756 | 0.47x | 2020-01-06 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1831 | +0.0886 | +0.0827 | 0.45x | No decay |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +0.1723 | +0.0893 | +0.1053 | 0.61x | 2021-05-28 |
| `combo_mean__net_volume_flow__bar_ret_0` | +0.1803 | +0.0913 | +0.0855 | 0.47x | No decay |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1683 | +0.1187 | +0.0936 | 0.56x | 2016-09-26 |
| `star50_limit_proximity_early` | +0.1480 | +0.0713 | +0.1379 | 0.93x | 2016-08-24 |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.0760 | +0.0190 | +0.0439 | 0.58x | 2011-10-26 |
| `combo_ratio__max_down_ret__net_volume_flow` | +0.1319 | -0.0332 | +0.1213 | 0.92x | 2021-02-24 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | +0.1562 | +0.0599 | +0.0847 | 0.54x | 2020-02-12 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1675 | +0.0636 | +0.0767 | 0.46x | 2016-11-30 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1954 | +0.1109 | +0.1190 | 0.61x | No decay |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | +0.1489 | +0.0586 | +0.0760 | 0.51x | 2013-09-23 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | +0.1601 | +0.0953 | +0.0886 | 0.55x | 2020-01-06 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | +0.1558 | +0.0848 | +0.0832 | 0.53x | 2016-11-01 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1596 | +0.0963 | +0.0889 | 0.56x | 2016-11-01 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1758 | +0.0816 | +0.1089 | 0.62x | 2021-05-28 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | +0.1697 | +0.0893 | +0.1243 | 0.73x | 2016-08-24 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | +0.1401 | -0.0210 | +0.0995 | 0.71x | 2016-11-30 |
| `combo_rank_min__bar_ret_0__max_down_ret` | +0.1484 | +0.0365 | +0.0873 | 0.59x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1803 | +0.1285 | +0.0589 | 0.33x | 2016-12-29 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | +0.1709 | +0.0651 | +0.0858 | 0.50x | 2016-12-29 |
| `combo_min__max_up_ret__bar_ret_0` | +0.1899 | +0.0832 | +0.0732 | 0.39x | No decay |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | +0.1570 | +0.0652 | +0.1480 | 0.94x | 2011-10-26 |
| `combo_min__bar_ret_0__max_down_ret` | +0.1471 | +0.0422 | +0.0944 | 0.64x | 2021-01-19 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1513 | +0.0626 | +0.1120 | 0.74x | 2023-01-16 |
| `combo_max__close_vs_open_range__bar_ret_0` | +0.1757 | +0.1060 | +0.0729 | 0.41x | No decay |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1280 | +0.0570 | +0.1298 | 1.01x | 2011-10-26 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1997 | +0.0971 | +0.0934 | 0.47x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | +0.1539 | +0.1065 | +0.0701 | 0.46x | 2016-11-01 |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | +0.1755 | +0.1057 | +0.0723 | 0.41x | No decay |
| `combo_max__close_vs_open_range__first_bar_sentiment` | +0.1506 | +0.0962 | +0.0751 | 0.50x | 2017-05-09 |
| `combo_sig_product__close_vs_open_range__high_low_sequence_momentum` | +0.1461 | +0.0903 | +0.0814 | 0.56x | 2016-11-01 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1841 | +0.1120 | +0.0915 | 0.50x | 2019-12-05 |
| `combo_rank_max__net_volume_flow__first_bar_return` | +0.1824 | +0.0891 | +0.0677 | 0.37x | No decay |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1750 | +0.0899 | +0.1094 | 0.63x | 2019-12-05 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1831 | +0.1088 | +0.1154 | 0.63x | No decay |
| `combo_max__first_bar_return__max_down_ret` | +0.1755 | +0.0645 | +0.0855 | 0.49x | 2016-11-01 |
| `combo_rank_min__close_vs_open_range__max_down_ret` | +0.1583 | +0.0739 | +0.1076 | 0.68x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1944 | +0.0915 | +0.0583 | 0.30x | 2016-11-30 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1853 | +0.1104 | +0.0936 | 0.51x | No decay |
| `combo_max__close_vs_open_range__early_body_momentum` | +0.1473 | +0.0915 | +0.0748 | 0.51x | 2016-11-01 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1527 | +0.0596 | +0.1703 | 1.12x | 2016-08-24 |
| `combo_mean__close_vs_open_range__bar_ret_0` | +0.1753 | +0.0877 | +0.0921 | 0.53x | No decay |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | +0.1824 | +0.0847 | +0.0910 | 0.50x | 2023-01-16 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | +0.1760 | +0.0715 | +0.1034 | 0.59x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1988 | +0.1059 | +0.0793 | 0.40x | 2020-01-06 |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | +0.1399 | +0.0892 | +0.0568 | 0.41x | 2016-11-01 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1450 | +0.0886 | +0.1504 | 1.04x | 2016-08-24 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | +0.1505 | +0.1124 | +0.0607 | 0.40x | 2016-11-30 |
| `combo_min__close_vs_open_range__max_down_ret` | +0.1584 | +0.0814 | +0.1071 | 0.68x | 2016-11-01 |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | +0.1720 | +0.0948 | +0.1055 | 0.61x | 2021-05-28 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | +0.1901 | +0.0880 | +0.0993 | 0.52x | 2016-11-30 |
| `combo_max__net_volume_flow__bar_ret_0` | +0.1819 | +0.0852 | +0.0677 | 0.37x | 2020-02-12 |
| `combo_mean__net_volume_flow__max_down_ret` | +0.1700 | +0.0809 | +0.0977 | 0.57x | 2016-11-01 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.0656 | +0.0185 | +0.0356 | 0.54x | 2010-10-15 |
| `first_bar_return` | +0.1524 | +0.0604 | +0.0690 | 0.45x | 2013-09-23 |
| `combo_max__first_bar_sentiment__bar_ret_0` | +0.1459 | +0.0857 | +0.0648 | 0.44x | 2020-12-18 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +0.1321 | +0.0881 | +0.0538 | 0.41x | 2020-01-06 |
| `combo_mean__first_bar_sentiment__max_down_ret` | +0.1569 | +0.0588 | +0.1023 | 0.65x | No decay |
| `combo_clamp_diff__max_up_ret__trend_bar_close_consistency` | +0.0279 | +0.0021 | -0.0149 | -0.53x | 2010-10-15 |
| `combo_diff__max_up_ret__trend_bar_close_consistency` | +0.0279 | +0.0022 | -0.0146 | -0.52x | 2010-10-15 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | +0.1738 | +0.0877 | +0.0756 | 0.44x | 2022-11-16 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1674 | +0.0801 | +0.0791 | 0.47x | 2016-12-29 |
| `combo_rank_max__trend_bar_close_consistency__close_vs_open_range` | +0.1423 | +0.0846 | +0.0656 | 0.46x | 2016-09-26 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1704 | +0.0974 | +0.0782 | 0.46x | 2017-04-07 |
| `combo_sig_product__net_volume_flow__first_bar_return` | +0.1349 | +0.0486 | +0.0569 | 0.42x | 2016-11-01 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1539 | +0.1103 | +0.0862 | 0.56x | 2016-09-26 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.1074 | +0.0351 | +0.0913 | 0.85x | 2016-08-24 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` | +0.0668 | +0.0172 | +0.0481 | 0.72x | 2010-12-14 |
| `combo_max__early_body_momentum__max_down_ret` | +0.1539 | +0.0547 | +0.0734 | 0.48x | 2016-11-01 |
| `vwap_trend_channel_slope` | +0.1524 | +0.1037 | +0.0602 | 0.39x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | +0.1835 | +0.0664 | +0.1118 | 0.61x | 2016-11-30 |
| `morning_volume_weighted_momentum` | +0.1459 | +0.1013 | +0.0726 | 0.50x | 2016-11-01 |
| `open_to_current_return` | +0.1532 | +0.1025 | +0.0708 | 0.46x | 2016-11-01 |
| `bar_body_rng_0` | +0.1454 | +0.0662 | +0.0799 | 0.55x | No decay |
| `or_fill_ratio` | +0.1208 | +0.0903 | +0.0708 | 0.59x | 2016-11-01 |

### 588000ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rel_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | +0.1364 | +0.1645 | -0.0358 | -0.26x | 2026-03-10 |
| `combo_diff__trend_day_regime_conviction__volume_weighted_momentum_acceleration` | +0.1301 | +0.1448 | -0.0400 | -0.31x | 2026-03-10 |
| `combo_diff__directional_volume_signature__smooth_momentum_structure` | +0.1008 | +0.0345 | +0.0282 | 0.28x | 2024-07-12 |
| `combo_rel_diff__directional_volume_signature__smooth_momentum_structure` | +0.1043 | +0.0271 | +0.0298 | 0.29x | 2024-07-12 |
| `combo_diff__directional_volume_signature__early_vwap_acceleration` | +0.1042 | -0.0721 | +0.0549 | 0.53x | 2022-12-19 |
| `combo_sig_product__high_low_sequence_momentum__vwap_trend_channel_slope` | +0.1500 | +0.1525 | -0.1208 | -0.81x | 2022-11-18 |
| `combo_sig_product__directional_volume_signature__smooth_momentum_structure` | +0.0628 | -0.0201 | +0.0139 | 0.22x | 2021-04-28 |
| `max_up_ret` | +0.1036 | +0.1269 | -0.0537 | -0.52x | No decay |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1553 | +0.1285 | +0.1423 | 0.92x | 2016-10-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1697 | +0.0747 | +0.1147 | 0.68x | 2017-04-28 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1519 | +0.0955 | +0.1297 | 0.85x | 2017-02-27 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1486 | +0.0981 | +0.1419 | 0.95x | 2011-10-18 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1635 | +0.0834 | +0.1230 | 0.75x | 2017-02-27 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1517 | +0.1194 | +0.0783 | 0.52x | 2017-01-20 |
| `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0` | +0.1603 | +0.0994 | +0.1340 | 0.84x | 2017-02-27 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1525 | +0.1314 | +0.1339 | 0.88x | 2016-09-14 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | +0.1702 | +0.1075 | +0.1284 | 0.75x | 2017-02-27 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1622 | +0.0945 | +0.1293 | 0.80x | 2011-10-18 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1781 | +0.1316 | +0.1292 | 0.73x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1620 | +0.0936 | +0.1288 | 0.80x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1406 | +0.0973 | +0.1356 | 0.96x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0914 | +0.1274 | +0.1192 | 1.30x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__first_bar_sentiment` | +0.1482 | +0.0539 | +0.1242 | 0.84x | 2011-10-18 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1669 | +0.1191 | +0.1338 | 0.80x | 2017-01-20 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1108 | +0.1302 | +0.1410 | 1.27x | 2011-10-18 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | +0.1641 | +0.1111 | +0.1309 | 0.80x | 2017-01-20 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1647 | +0.1120 | +0.0931 | 0.56x | 2017-02-27 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1606 | +0.1122 | +0.0868 | 0.54x | 2017-01-20 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +0.1541 | +0.1366 | +0.1109 | 0.72x | 2016-10-24 |
| `combo_max__max_up_ret__first_bar_return` | +0.1577 | +0.1137 | +0.0844 | 0.54x | 2017-04-28 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +0.1558 | +0.1370 | +0.0866 | 0.56x | 2016-12-21 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | +0.1513 | +0.1376 | +0.1021 | 0.67x | 2016-10-24 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | +0.1603 | +0.1110 | +0.0840 | 0.52x | 2017-01-20 |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | +0.1454 | +0.0649 | +0.1182 | 0.81x | 2011-10-18 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1029 | +0.0965 | +0.1311 | 1.27x | 2011-10-18 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — B4 Correlation Gate too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.1528). Consider relaxing this gate.
2. **300ETF `short` — BH-FDR Gate too strict**: 42.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.0662). Consider relaxing this gate.
3. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.0553). Consider relaxing this gate.
4. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 45.0%, mean lock Sharpe=+0.3591). Consider relaxing this gate.
5. **500ETF `single` — B2 Rolling Guard too strict**: 76.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 45.0%, mean lock Sharpe=+0.4069). Consider relaxing this gate.
6. **500ETF `single` — B3 Composite Floor too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 45.0%, mean lock Sharpe=+0.7247). Consider relaxing this gate.
7. **500ETF `single` — B4 Correlation Gate too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 45.0%, mean lock Sharpe=+0.5429). Consider relaxing this gate.
8. **500ETF `long` — BH-FDR Gate too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 36.0%, mean lock Sharpe=-0.0635). Consider relaxing this gate.
9. **500ETF `short` — BH-FDR Gate too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 33.0%, mean lock Sharpe=+0.1698). Consider relaxing this gate.
10. **588000ETF `single` — 7-Year Jackknife Sign Stability too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=+0.1538). Consider relaxing this gate.
11. **588000ETF `single` — B2 Rolling Guard too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.2399). Consider relaxing this gate.
12. **588000ETF `single` — B4 Correlation Gate too strict**: 23.8% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.5222). Consider relaxing this gate.
13. **588000ETF `short` — B3 Composite Floor too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.3303). Consider relaxing this gate.
14. **159915ETF `single` — B2 Rolling Guard too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.7239). Consider relaxing this gate.
15. **159915ETF `single` — B3 Composite Floor too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.9671). Consider relaxing this gate.
16. **159915ETF `single` — B4 Correlation Gate too strict**: 87.5% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.9980). Consider relaxing this gate.
17. **159915ETF `long` — B2 Rolling Guard too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 46.0%, mean lock Sharpe=+0.6461). Consider relaxing this gate.
18. **159915ETF `long` — BH-FDR Gate too strict**: 70.8% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 46.0%, mean lock Sharpe=+0.4617). Consider relaxing this gate.
19. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3342). Consider relaxing this gate.
20. **159915ETF `short` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.2346). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
