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

### 300ETF — `single` (Full Model Lockbox IC: +0.0265, Sharpe: -0.1431)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1248 | +0.0650 | +0.0290 | +0.0482 | 0.64 | 0/8 | 0.91 | 0.51 | `rbreaker_sell_setup_proximity_early` (1.16) | +0.0002 | -0.3384 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.1265 | +0.0517 | +0.0166 | +0.3013 | 0.78 | 1/8 | 1.24 | 0.85 | `rbreaker_sell_setup_proximity_early` (1.16) | -0.0007 | -0.3336 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1161 | +0.0603 | +0.0344 | +1.0755 | 0.86 | 1/8 | 0.87 | 0.72 | `rbreaker_sell_setup_proximity_early` (1.16) | +0.0005 | -0.3136 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1145 | +0.0771 | +0.0527 | +0.4796 | 0.79 | 1/8 | 1.39 | 0.66 | `rbreaker_sell_setup_proximity_early` (1.16) | +0.0018 | -0.0875 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1189 | +0.0652 | +0.0332 | -0.0508 | 0.88 | 1/8 | 1.38 | 0.82 | `rbreaker_sell_setup_proximity_early` (1.16) | +0.0009 | -0.0031 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1056 | +0.0604 | +0.0194 | +0.4526 | 0.88 | 1/8 | 1.24 | 0.98 | `rbreaker_sell_setup_proximity_early` (1.16) | -0.0007 | -0.1287 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1141 | +0.0720 | +0.0405 | +0.0985 | 0.77 | 1/8 | 1.16 | 0.54 | `rbreaker_sell_setup_proximity_early` (1.16) | +0.0028 | -0.3384 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1114 | +0.0658 | +0.0216 | +0.3524 | 0.85 | 1/8 | 1.36 | 0.88 | `rbreaker_sell_setup_proximity_early` (1.16) | -0.0009 | -0.1287 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0883 | +0.0728 | +0.0616 | +0.2757 | 1.16 | 1/8 | 0.91 | 0.58 | — | -0.0006 | -0.3086 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0932 | +0.0558 | -0.0031 | -0.2655 | 0.64 | 1/8 | 1.15 | 0.69 | `max_up_ret` (0.89) | -0.0006 | -0.4275 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1150 | +0.0632 | +0.0209 | +0.2426 | 0.75 | 1/8 | 1.22 | 1.01 | `rbreaker_sell_setup_proximity_early` (1.16) | +0.0003 | -0.3326 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0757 | +0.0537 | -0.0101 | -0.3294 | 0.83 | 0/8 | 1.62 | 1.66 | `volume_weighted_price_position` (1.26) | +0.0006 | -0.3998 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1170 | +0.0715 | +0.0381 | +0.3102 | 0.67 | 0/8 | 1.18 | 0.76 | `rbreaker_sell_setup_proximity_early` (1.16) | +0.0006 | -0.3439 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0797 | +0.0560 | -0.0128 | -0.2036 | 0.90 | 1/8 | 1.47 | 1.21 | `volume_weighted_price_position` (1.26) | -0.0000 | -0.7069 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1092 | +0.0751 | +0.0489 | +0.3040 | 0.76 | 1/8 | 1.26 | 0.52 | `star50_limit_proximity_early` (1.14) | +0.0017 | -0.3384 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0911 | +0.0472 | +0.0120 | +0.2477 | 0.64 | 1/8 | 1.68 | 1.16 | `volume_weighted_price_position` (1.26) | +0.0009 | -0.4275 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0707 | +0.0488 | -0.0210 | -0.4391 | 0.90 | 1/8 | 1.44 | 1.34 | `volume_weighted_price_position` (1.26) | -0.0010 | -0.6081 |
| `combo_mean__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0792 | +0.0541 | +0.0113 | +0.3021 | 1.02 | 2/8 | 2.09 | 2.12 | `volume_surge_direction` (1.58) | +0.0011 | -0.4028 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0829 | +0.0426 | -0.0146 | -0.8370 | 0.77 | 1/8 | 2.45 | 1.71 | `volume_weighted_price_position` (1.26) | -0.0003 | -0.2380 |
| `star50_limit_proximity_early` | Other Technical | +1 | +0.0853 | +0.0720 | +0.0650 | +0.2250 | 1.14 | 1/8 | 0.97 | 0.58 | — | +0.0008 | -0.3051 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0927 | +0.0558 | +0.0183 | +0.4197 | 0.67 | 0/8 | 1.40 | 1.43 | `early_vwap_acceleration` (0.89) | +0.0004 | -0.3078 |
| `combo_max__bar_body_rng_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0744 | +0.0597 | +0.0185 | +0.3941 | 1.02 | 2/8 | 1.48 | 0.54 | `volume_surge_direction` (1.58) | +0.0012 | -0.4275 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1138, Sharpe: +0.7686)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.2031 | +0.1030 | +0.1176 | +0.2436 | 0.30 | 0/8 | 0.76 | 0.58 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1957 | +0.1016 | +0.1215 | +1.2786 | 0.27 | 0/8 | 0.60 | 0.64 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.2033 | +0.1007 | +0.1183 | +0.7959 | 0.31 | 0/8 | 0.72 | 0.58 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | -0.0183 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1922 | +0.1028 | +0.1250 | +1.1820 | 0.39 | 0/8 | 0.94 | 0.66 | `star50_limit_proximity_early` (0.60) | -0.0000 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1971 | +0.1144 | +0.1219 | +0.6272 | 0.32 | 0/8 | 0.65 | 0.55 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0004 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1780 | +0.1047 | +0.1291 | +1.1812 | 0.40 | 0/8 | 0.73 | 0.55 | `star50_limit_proximity_early` (0.60) | +0.0001 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1912 | +0.0896 | +0.1148 | +0.9912 | 0.37 | 0/8 | 0.88 | 0.61 | `star50_limit_proximity_early` (0.60) | +0.0002 | +0.0223 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.2023 | +0.0856 | +0.0800 | +0.5240 | 0.31 | 0/8 | 0.93 | 0.70 | `volume_weighted_momentum_acceleration` (0.42) | +0.0001 | -0.0183 |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1658 | +0.0983 | +0.0897 | +0.0875 | 0.34 | 0/8 | 0.73 | 0.60 | `volatility_expansion_trend_vector` (0.41) | -0.0001 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1724 | +0.1023 | +0.1111 | +0.9518 | 0.27 | 0/8 | 0.81 | 0.68 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.2054 | +0.1119 | +0.1077 | +0.9000 | 0.30 | 0/8 | 0.65 | 0.60 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0000 | +0.0396 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1710 | +0.0937 | +0.0821 | +0.4522 | 0.37 | 0/8 | 0.60 | 0.50 | `smooth_momentum_structure` (0.43) | -0.0001 | +0.0396 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1828 | +0.0980 | +0.0886 | -0.2268 | 0.29 | 0/8 | 0.76 | 0.59 | `opening_drive_thrust_ratio` (0.33) | -0.0001 | +0.0396 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1932 | +0.0802 | +0.0988 | +0.9085 | 0.37 | 0/8 | 0.67 | 0.44 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0396 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1636 | +0.1022 | +0.1066 | +1.0420 | 0.25 | 0/8 | 0.67 | 0.70 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.2170 | +0.1084 | +0.1134 | +0.4269 | 0.28 | 0/8 | 0.73 | 0.62 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0005 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1926 | +0.1076 | +0.1250 | +1.2362 | 0.30 | 0/8 | 0.59 | 0.60 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0000 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1794 | +0.0868 | +0.0827 | +0.7466 | 0.37 | 0/8 | 0.84 | 0.69 | `body_size_progression` (0.58) | +0.0000 | -0.0183 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1885 | +0.1082 | +0.1078 | +0.2774 | 0.32 | 0/8 | 0.66 | 0.55 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0002 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.1542 | +0.0711 | +0.0683 | -0.5433 | 0.30 | 0/8 | 1.21 | 1.02 | `double_bottom_bull_flag_early` (0.65) | +0.0004 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1916 | +0.0803 | +0.0966 | +0.9307 | 0.41 | 0/8 | 0.65 | 0.39 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | +0.0396 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1582 | +0.1030 | +0.1192 | +1.1926 | 0.32 | 0/8 | 0.64 | 0.63 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | +0.0151 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1713 | +0.0781 | +0.0660 | -0.4519 | 0.33 | 0/8 | 0.77 | 0.58 | `first_bar_sentiment` (0.45) | -0.0000 | +0.0396 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1665 | +0.0839 | +0.0786 | -1.2258 | 0.34 | 0/8 | 1.08 | 0.84 | `smooth_momentum_structure` (0.43) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1780 | +0.0847 | +0.1023 | +0.6485 | 0.36 | 0/8 | 0.67 | 0.54 | `first_bar_sentiment` (0.45) | +0.0005 | +0.0000 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1813 | +0.0937 | +0.0941 | +0.2151 | 0.33 | 0/8 | 0.98 | 0.65 | `volume_weighted_momentum_acceleration` (0.42) | -0.0000 | +0.0396 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1906 | +0.0896 | +0.1148 | +0.9912 | 0.36 | 0/8 | 0.89 | 0.61 | `star50_limit_proximity_early` (0.60) | +0.0001 | +0.0000 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1341 | +0.0953 | +0.0945 | +0.7180 | 0.34 | 0/8 | 0.58 | 0.61 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1795 | +0.0859 | +0.0840 | +0.2880 | 0.31 | 0/8 | 1.03 | 0.73 | `volume_weighted_momentum_acceleration` (0.42) | -0.0000 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1650 | +0.0830 | +0.1104 | +1.3116 | 0.42 | 0/8 | 0.66 | 0.40 | `star50_limit_proximity_early` (0.60) | +0.0001 | +0.0396 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1773 | +0.0749 | +0.0805 | -0.4292 | 0.39 | 0/8 | 0.79 | 0.43 | `opening_drive_thrust_ratio` (0.33) | -0.0003 | +0.0396 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1794 | +0.0994 | +0.0842 | +0.4157 | 0.34 | 0/8 | 0.67 | 0.49 | `trend_bar_close_consistency` (0.76) | -0.0001 | +0.0000 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1472 | +0.1098 | +0.1327 | +1.3131 | 0.41 | 0/8 | 0.65 | 0.55 | `star50_limit_proximity_early` (0.60) | +0.0002 | +0.0000 |
| `combo_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1793 | +0.0845 | +0.0768 | +0.1212 | 0.35 | 0/8 | 0.84 | 0.71 | `body_size_progression` (0.58) | -0.0001 | -0.0183 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1895 | +0.1025 | +0.1094 | +0.5985 | 0.34 | 0/8 | 0.73 | 0.56 | `star50_limit_proximity_early` (0.60) | -0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1403 | +0.1099 | +0.0943 | +0.4604 | 0.49 | 0/8 | 0.62 | 0.63 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1701 | +0.1110 | +0.1261 | +0.8321 | 0.41 | 0/8 | 0.48 | 0.38 | — | -0.0003 | +0.0000 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1510 | +0.0702 | +0.0890 | +0.7110 | 0.39 | 0/8 | 0.74 | 0.51 | `max_down_ret` (0.51) | +0.0001 | +0.0396 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1352 | +0.1025 | +0.1186 | +1.4646 | 0.40 | 0/8 | 0.60 | 0.51 | `star50_limit_proximity_early` (0.60) | +0.0002 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1840 | +0.1006 | +0.0885 | -0.1432 | 0.32 | 0/8 | 0.73 | 0.60 | `net_volume_flow` (0.35) | -0.0003 | +0.0396 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1956 | +0.1048 | +0.1222 | +0.5472 | 0.35 | 0/8 | 0.69 | 0.56 | `star50_limit_proximity_early` (0.60) | -0.0001 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1342 | +0.1034 | +0.1332 | +1.4206 | 0.45 | 0/8 | 0.55 | 0.55 | `star50_limit_proximity_early` (0.60) | -0.0000 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1295 | +0.0954 | +0.1060 | +0.7947 | 0.45 | 0/8 | 0.54 | 0.47 | `trend_bar_close_consistency` (0.76) | +0.0002 | +0.0261 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1756 | +0.1053 | +0.0965 | +0.4918 | 0.42 | 0/8 | 0.71 | 0.47 | `trend_bar_close_consistency` (0.76) | +0.0000 | +0.0000 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1935 | +0.0853 | +0.0854 | +0.6577 | 0.30 | 0/8 | 0.96 | 0.75 | `smooth_momentum_structure` (0.43) | +0.0002 | +0.0000 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1738 | +0.0709 | +0.0740 | -0.4319 | 0.44 | 0/8 | 0.73 | 0.63 | `late_bar_momentum` (0.62) | -0.0000 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1942 | +0.0970 | +0.1091 | +0.6641 | 0.32 | 0/8 | 0.67 | 0.53 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0001 | +0.0000 |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1342 | +0.0773 | +0.0761 | -0.1628 | 0.34 | 0/8 | 0.74 | 0.49 | `early_body_momentum` (0.51) | -0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | Intraday Range Momentum | +1 | +0.1712 | +0.0942 | +0.0866 | +0.4004 | 0.38 | 0/8 | 0.62 | 0.54 | `early_body_momentum` (0.51) | -0.0002 | +0.0396 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1670 | +0.0873 | +0.0864 | -0.2545 | 0.40 | 0/8 | 1.03 | 0.70 | `body_size_progression` (0.58) | +0.0004 | +0.0000 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1324 | +0.1019 | +0.1289 | +1.3996 | 0.45 | 0/8 | 0.54 | 0.52 | `star50_limit_proximity_early` (0.60) | +0.0002 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1700 | +0.1015 | +0.0950 | +0.4793 | 0.41 | 0/8 | 0.67 | 0.62 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1746 | +0.1079 | +0.1174 | +0.7335 | 0.34 | 0/8 | 0.60 | 0.51 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0001 | +0.0000 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1763 | +0.0933 | +0.0824 | +0.2486 | 0.31 | 0/8 | 0.72 | 0.59 | `first_bar_sentiment` (0.45) | -0.0004 | +0.0396 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1651 | +0.0989 | +0.0916 | +0.3599 | 0.34 | 0/8 | 0.75 | 0.62 | `close_vs_open_range` (0.44) | +0.0000 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1334 | +0.0858 | +0.0713 | -0.0632 | 0.46 | 0/8 | 0.78 | 0.56 | `trend_bar_close_consistency` (0.76) | -0.0004 | +0.0000 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.2024 | +0.0867 | +0.0808 | +0.6165 | 0.30 | 0/8 | 0.93 | 0.71 | `volume_weighted_momentum_acceleration` (0.42) | -0.0001 | -0.0183 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1641 | +0.1165 | +0.1126 | +0.0039 | 0.59 | 0/8 | 0.37 | 0.27 | `body_size_progression` (0.58) | -0.0002 | +0.0151 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1765 | +0.0813 | +0.0759 | +0.1748 | 0.35 | 0/8 | 0.86 | 0.75 | `body_size_progression` (0.58) | -0.0001 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1600 | +0.0940 | +0.1188 | +1.5685 | 0.49 | 0/8 | 0.83 | 0.53 | `star50_limit_proximity_early` (0.60) | +0.0000 | -0.0183 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1481 | +0.0837 | +0.1100 | +1.0815 | 0.50 | 0/8 | 0.64 | 0.53 | `max_down_ret` (0.51) | +0.0003 | +0.0583 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.0649 | +0.0209 | -0.0015 | +0.5631 | 1.16 | 2/8 | 0.87 | 1.44 | `trend_bar_close_consistency` (0.76) | +0.0000 | +0.0396 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1887 | +0.1113 | +0.1177 | +0.4883 | 0.34 | 0/8 | 0.60 | 0.55 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0005 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1427 | +0.0849 | +0.1099 | +0.8095 | 0.50 | 0/8 | 0.58 | 0.41 | `star50_limit_proximity_early` (0.60) | -0.0002 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1607 | +0.0882 | +0.1136 | +1.3878 | 0.47 | 0/8 | 0.75 | 0.46 | `star50_limit_proximity_early` (0.60) | +0.0003 | +0.0223 |
| `combo_mean__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1427 | +0.0860 | +0.0655 | +0.3973 | 0.44 | 0/8 | 0.59 | 0.50 | `trend_bar_close_consistency` (0.76) | -0.0004 | +0.0396 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1616 | +0.0973 | +0.0783 | -0.1654 | 0.27 | 0/8 | 0.88 | 0.71 | `net_volume_flow` (0.35) | -0.0003 | +0.0000 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1645 | +0.0993 | +0.1125 | +0.5975 | 0.35 | 0/8 | 0.65 | 0.50 | `star50_limit_proximity_early` (0.60) | -0.0001 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1538 | +0.1030 | +0.1227 | +0.5969 | 0.47 | 0/8 | 0.49 | 0.39 | `star50_limit_proximity_early` (0.60) | +0.0001 | +0.0000 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1409 | +0.0930 | +0.1102 | +0.5424 | 0.55 | 0/8 | 0.51 | 0.35 | `star50_limit_proximity_early` (0.60) | +0.0002 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1812 | +0.0956 | +0.0870 | +0.0581 | 0.33 | 0/8 | 0.82 | 0.66 | — | -0.0001 | +0.0396 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1935 | +0.0939 | +0.0811 | +0.0002 | 0.31 | 0/8 | 0.74 | 0.68 | `opening_drive_thrust_ratio` (0.33) | -0.0003 | +0.0396 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1553 | +0.0932 | +0.0845 | +0.6576 | 0.35 | 0/8 | 0.62 | 0.63 | `early_body_momentum` (0.51) | +0.0001 | +0.0000 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1213 | +0.0896 | +0.0843 | +0.1036 | 0.38 | 0/8 | 0.62 | 0.48 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1463 | +0.0884 | +0.1081 | +1.4937 | 0.39 | 0/8 | 0.74 | 0.56 | `volume_weighted_momentum_acceleration` (0.42) | +0.0003 | +0.0619 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1692 | +0.0942 | +0.0788 | -0.5540 | 0.32 | 0/8 | 0.80 | 0.65 | `first_bar_sentiment` (0.45) | -0.0000 | +0.0396 |
| `combo_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1569 | +0.0890 | +0.0706 | +0.0803 | 0.42 | 0/8 | 0.62 | 0.43 | `early_body_momentum` (0.51) | -0.0002 | +0.0396 |
| `combo_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1333 | +0.0993 | +0.0919 | +0.0514 | 0.31 | 0/8 | 0.61 | 0.68 | `close_vs_open_range` (0.44) | -0.0000 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1718 | +0.0923 | +0.0909 | +0.3624 | 0.33 | 0/8 | 0.87 | 0.60 | `first_bar_sentiment` (0.45) | -0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1811 | +0.0846 | +0.0915 | -0.0085 | 0.34 | 0/8 | 0.84 | 0.51 | `opening_drive_thrust_ratio` (0.33) | -0.0003 | +0.0396 |
| `combo_min__close_vs_open_range__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1179 | +0.0897 | +0.0809 | -0.0454 | 0.46 | 0/8 | 0.55 | 0.44 | `high_low_sequence_momentum` (0.48) | -0.0002 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1728 | +0.0936 | +0.0778 | +0.1313 | 0.28 | 0/8 | 0.66 | 0.63 | — | -0.0004 | +0.0396 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1610 | +0.0942 | +0.0737 | +0.3750 | 0.41 | 0/8 | 0.62 | 0.45 | `early_body_momentum` (0.51) | +0.0002 | +0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1463 | +0.0895 | +0.0537 | +0.0071 | 0.37 | 0/8 | 0.89 | 0.72 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1527 | +0.0957 | +0.0723 | +0.3991 | 0.40 | 0/8 | 0.85 | 0.66 | `net_volume_flow` (0.35) | -0.0001 | +0.0000 |
| `combo_mean__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1575 | +0.0980 | +0.0821 | +0.0638 | 0.34 | 0/8 | 0.64 | 0.59 | `close_vs_open_range` (0.44) | -0.0000 | +0.0396 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1890 | +0.0995 | +0.0824 | +0.1434 | 0.33 | 0/8 | 0.71 | 0.63 | `opening_drive_thrust_ratio` (0.33) | -0.0000 | +0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1508 | +0.0845 | +0.0656 | +0.3922 | 0.45 | 0/8 | 0.73 | 0.65 | `trend_bar_close_consistency` (0.76) | -0.0001 | +0.0000 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1705 | +0.0849 | +0.0972 | +0.2946 | 0.36 | 0/8 | 0.81 | 0.53 | `max_down_ret` (0.51) | -0.0002 | +0.0396 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1324 | +0.0842 | +0.0997 | +0.3462 | 0.43 | 0/8 | 0.66 | 0.31 | `close_vs_open_range` (0.44) | -0.0001 | +0.0396 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1346 | +0.0871 | +0.0754 | -0.1482 | 0.31 | 0/8 | 0.74 | 0.53 | `early_body_momentum` (0.51) | -0.0002 | +0.0000 |
| `combo_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1705 | +0.0950 | +0.0764 | -0.0026 | 0.37 | 0/8 | 0.68 | 0.52 | `close_vs_open_range` (0.44) | -0.0002 | +0.0396 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1445 | +0.0921 | +0.1128 | +1.0888 | 0.34 | 0/8 | 0.73 | 0.92 | `early_late_momentum_divergence` (0.62) | -0.0001 | -0.0183 |
| `combo_min__max_up_ret__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1342 | +0.1021 | +0.0849 | +0.0211 | 0.31 | 0/8 | 0.68 | 0.66 | `high_low_sequence_momentum` (0.48) | -0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1506 | +0.0931 | +0.0876 | +0.6961 | 0.32 | 0/8 | 0.83 | 0.63 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1597 | +0.0869 | +0.1120 | +1.3878 | 0.47 | 0/8 | 0.77 | 0.47 | `star50_limit_proximity_early` (0.60) | +0.0003 | +0.0151 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Other Technical | +1 | +0.1196 | +0.0776 | +0.0870 | -0.0833 | 0.50 | 0/8 | 0.71 | 0.28 | `trend_bar_close_consistency` (0.76) | -0.0001 | +0.0396 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.0498 | +0.0201 | +0.0049 | +0.4883 | 1.31 | 1/8 | 0.78 | 1.58 | `early_body_momentum` (0.51) | +0.0000 | +0.0548 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1253 | +0.0860 | +0.0891 | +0.6744 | 0.42 | 0/8 | 1.03 | 0.53 | `star50_limit_proximity_early` (0.60) | +0.0001 | +0.0000 |
| `combo_min__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1320 | +0.0858 | +0.1017 | +0.4023 | 0.42 | 0/8 | 0.67 | 0.32 | `close_vs_open_range` (0.44) | -0.0000 | +0.0396 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1706 | +0.0863 | +0.0938 | +0.7040 | 0.39 | 0/8 | 0.78 | 0.62 | `max_down_ret` (0.51) | -0.0001 | +0.0396 |
| `combo_mean__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1802 | +0.0875 | +0.0779 | +0.4297 | 0.31 | 0/8 | 0.74 | 0.58 | `first_bar_return` (0.33) | -0.0002 | +0.0396 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1693 | +0.0799 | +0.0798 | +0.0121 | 0.34 | 0/8 | 1.08 | 0.79 | `smooth_momentum_structure` (0.43) | +0.0002 | +0.0000 |
| `combo_mean__volatility_expansion_trend_vector__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1228 | +0.0927 | +0.0862 | +0.5339 | 0.40 | 0/8 | 0.59 | 0.51 | `close_vs_open_range` (0.44) | -0.0003 | +0.0000 |
| `combo_min__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1386 | +0.0959 | +0.0950 | +0.5069 | 0.35 | 0/8 | 0.78 | 0.48 | `net_volume_flow` (0.35) | -0.0003 | +0.0396 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1693 | +0.0936 | +0.0741 | +0.1719 | 0.35 | 0/8 | 0.66 | 0.55 | `close_vs_open_range` (0.44) | +0.0002 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.1303 | +0.0930 | +0.0847 | +0.3991 | 0.35 | 0/8 | 0.73 | 0.54 | — | -0.0004 | +0.0000 |
| `combo_rank_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1750 | +0.0702 | +0.0672 | +0.2409 | 0.36 | 0/8 | 0.71 | 0.45 | `bar_ret_0` (0.33) | -0.0002 | +0.0396 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1928 | +0.0929 | +0.0892 | +0.0637 | 0.31 | 0/8 | 0.83 | 0.63 | `opening_drive_thrust_ratio` (0.33) | -0.0002 | +0.0396 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1740 | +0.0839 | +0.0648 | +0.2544 | 0.41 | 0/8 | 0.61 | 0.57 | `trend_bar_close_consistency` (0.76) | -0.0002 | +0.0396 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1455 | +0.1084 | +0.0902 | +0.4860 | 0.35 | 0/8 | 0.75 | 0.71 | `volatility_expansion_trend_vector` (0.41) | -0.0001 | +0.0000 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1533 | +0.0726 | +0.0782 | +0.6224 | 0.33 | 0/8 | 0.82 | 0.53 | `first_bar_sentiment` (0.45) | -0.0001 | +0.0396 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1840 | +0.0972 | +0.0866 | +0.0098 | 0.28 | 0/8 | 0.84 | 0.73 | `opening_drive_thrust_ratio` (0.33) | -0.0002 | +0.0396 |
| `combo_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1711 | +0.0842 | +0.0754 | -0.3958 | 0.30 | 0/8 | 0.81 | 0.67 | `first_bar_return` (0.33) | -0.0006 | +0.0396 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1663 | +0.0926 | +0.0936 | +0.1266 | 0.41 | 0/8 | 0.76 | 0.59 | `max_down_ret` (0.51) | -0.0001 | +0.0396 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1471 | +0.0870 | +0.1143 | +0.5420 | 0.62 | 0/8 | 0.45 | 0.30 | `star50_limit_proximity_early` (0.60) | +0.0000 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1828 | +0.1101 | +0.1128 | +0.5689 | 0.42 | 0/8 | 0.60 | 0.48 | `star50_limit_proximity_early` (0.60) | -0.0004 | +0.0000 |
| `combo_max__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1425 | +0.0807 | +0.0759 | -0.1251 | 0.31 | 0/8 | 0.79 | 0.56 | `first_bar_sentiment` (0.45) | -0.0002 | +0.0000 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1712 | +0.0930 | +0.0841 | -0.0433 | 0.25 | 0/8 | 0.76 | 0.73 | `first_bar_return` (0.33) | -0.0002 | +0.0396 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1642 | +0.1044 | +0.1051 | +0.3776 | 0.36 | 0/8 | 0.63 | 0.44 | `star50_limit_proximity_early` (0.60) | -0.0002 | +0.0000 |
| `combo_mean__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1589 | +0.0913 | +0.0861 | -0.2315 | 0.31 | 0/8 | 0.76 | 0.53 | `net_volume_flow` (0.35) | -0.0003 | +0.0396 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1579 | +0.1072 | +0.0935 | +0.4180 | 0.53 | 0/8 | 0.47 | 0.24 | `early_body_momentum` (0.51) | -0.0003 | +0.0000 |
| `star50_limit_proximity_early` | Other Technical | +1 | +0.1441 | +0.1129 | +0.1379 | +0.3067 | 0.60 | 0/8 | 0.42 | 0.25 | — | -0.0001 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.0871 | +0.0307 | +0.0422 | +0.1933 | 0.63 | 0/8 | 1.59 | 1.02 | `trend_bar_close_consistency` (0.76) | +0.0002 | +0.0396 |
| `combo_ratio__max_down_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1330 | +0.0543 | +0.1213 | +0.1422 | 0.44 | 0/8 | 0.61 | 0.40 | `max_down_ret` (0.51) | -0.0002 | +0.0000 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1410 | +0.0760 | +0.0850 | -0.0243 | 0.38 | 0/8 | 0.68 | 0.48 | `first_bar_sentiment` (0.45) | +0.0000 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1500 | +0.0727 | +0.0766 | +0.5826 | 0.46 | 1/8 | 1.26 | 0.88 | `volume_weighted_momentum_acceleration` (0.42) | +0.0000 | +0.0396 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1851 | +0.1195 | +0.1198 | +1.1268 | 0.35 | 0/8 | 0.56 | 0.47 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0000 | +0.0151 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1530 | +0.0713 | +0.0760 | +0.0220 | 0.29 | 0/8 | 0.86 | 0.71 | `first_bar_sentiment` (0.45) | -0.0000 | +0.0396 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1399 | +0.0933 | +0.0885 | +0.0993 | 0.36 | 0/8 | 0.70 | 0.53 | `first_bar_sentiment` (0.45) | -0.0001 | +0.0000 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1162 | +0.0872 | +0.0826 | -0.0109 | 0.44 | 0/8 | 0.54 | 0.49 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1475 | +0.0965 | +0.0900 | +0.6728 | 0.52 | 0/8 | 0.51 | 0.27 | `early_body_momentum` (0.51) | -0.0007 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1677 | +0.1016 | +0.1102 | +0.4840 | 0.44 | 0/8 | 0.51 | 0.34 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0005 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1504 | +0.1165 | +0.1246 | -0.1885 | 0.64 | 0/8 | 0.44 | 0.30 | `star50_limit_proximity_early` (0.60) | -0.0001 | +0.0000 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1407 | +0.0479 | +0.0995 | +0.5483 | 0.49 | 0/8 | 0.66 | 0.36 | `max_down_ret` (0.51) | -0.0003 | +0.0000 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1436 | +0.0688 | +0.0863 | +0.1572 | 0.41 | 0/8 | 0.68 | 0.38 | `max_down_ret` (0.51) | -0.0003 | +0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1498 | +0.0924 | +0.0592 | -0.0614 | 0.38 | 0/8 | 0.92 | 0.70 | `volatility_expansion_trend_vector` (0.41) | -0.0001 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1582 | +0.0760 | +0.0851 | +0.7374 | 0.44 | 0/8 | 0.93 | 0.67 | `late_bar_momentum` (0.62) | +0.0001 | +0.0000 |
| `combo_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1782 | +0.0801 | +0.0725 | +0.4731 | 0.34 | 0/8 | 0.67 | 0.48 | `bar_ret_0` (0.33) | -0.0002 | +0.0396 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1520 | +0.1149 | +0.1478 | +0.9759 | 0.58 | 0/8 | 0.50 | 0.32 | `star50_limit_proximity_early` (0.60) | -0.0001 | +0.0000 |
| `combo_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1466 | +0.0733 | +0.0943 | +0.2463 | 0.39 | 0/8 | 0.72 | 0.42 | `max_down_ret` (0.51) | +0.0001 | +0.0396 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1346 | +0.0828 | +0.1042 | +1.0014 | 0.47 | 0/8 | 0.64 | 0.61 | `body_size_progression` (0.58) | -0.0000 | +0.0223 |
| `combo_max__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1670 | +0.0905 | +0.0732 | -0.2236 | 0.29 | 0/8 | 0.79 | 0.72 | `close_vs_open_range` (0.44) | -0.0004 | +0.0000 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1405 | +0.1019 | +0.1298 | +0.7773 | 0.60 | 0/8 | 0.44 | 0.25 | `star50_limit_proximity_early` (0.60) | -0.0002 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1871 | +0.1009 | +0.0943 | +0.2902 | 0.35 | 0/8 | 0.64 | 0.52 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0006 | +0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1377 | +0.0861 | +0.0697 | -0.3722 | 0.52 | 1/8 | 0.96 | 0.76 | `body_size_progression` (0.58) | +0.0000 | +0.0223 |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1669 | +0.0910 | +0.0734 | -0.0821 | 0.29 | 0/8 | 0.79 | 0.73 | `close_vs_open_range` (0.44) | -0.0002 | +0.0000 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1393 | +0.0879 | +0.0766 | +0.0796 | 0.37 | 0/8 | 0.80 | 0.63 | `first_bar_sentiment` (0.45) | -0.0002 | +0.0000 |
| `combo_sig_product__close_vs_open_range__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1136 | +0.0887 | +0.0815 | -0.1448 | 0.48 | 0/8 | 0.58 | 0.44 | `high_low_sequence_momentum` (0.48) | -0.0001 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1684 | +0.1055 | +0.0903 | +0.4040 | 0.41 | 0/8 | 0.57 | 0.39 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0002 | +0.0151 |
| `combo_rank_max__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1646 | +0.0797 | +0.0672 | -0.5118 | 0.28 | 0/8 | 0.77 | 0.59 | `net_volume_flow` (0.35) | -0.0002 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1634 | +0.1061 | +0.1083 | +0.4064 | 0.27 | 0/8 | 0.64 | 0.55 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0002 | +0.0151 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1772 | +0.1172 | +0.1155 | +0.9797 | 0.47 | 0/8 | 0.51 | 0.35 | `star50_limit_proximity_early` (0.60) | -0.0001 | +0.0000 |
| `combo_max__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1659 | +0.0801 | +0.0856 | +0.2376 | 0.38 | 0/8 | 0.78 | 0.56 | `max_down_ret` (0.51) | -0.0003 | +0.0000 |
| `combo_rank_min__close_vs_open_range__max_down_ret` | Intraday Range Momentum | +1 | +0.1349 | +0.0959 | +0.1080 | +0.2915 | 0.52 | 0/8 | 0.58 | 0.42 | `max_down_ret` (0.51) | -0.0001 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1651 | +0.0812 | +0.0610 | -0.2641 | 0.42 | 0/8 | 1.28 | 1.04 | `opening_drive_thrust_ratio` (0.33) | -0.0005 | +0.0396 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1720 | +0.1069 | +0.0929 | +0.3241 | 0.40 | 0/8 | 0.60 | 0.41 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0005 | +0.0396 |
| `combo_max__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.1101 | +0.0857 | +0.0747 | +0.3373 | 0.47 | 0/8 | 0.54 | 0.46 | `early_body_momentum` (0.51) | -0.0003 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1504 | +0.1249 | +0.1702 | +0.8680 | 0.36 | 0/8 | 0.80 | 0.52 | `star50_limit_proximity_early` (0.60) | -0.0001 | +0.0000 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1589 | +0.0939 | +0.0923 | -0.2314 | 0.34 | 0/8 | 0.73 | 0.56 | `close_vs_open_range` (0.44) | -0.0001 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1737 | +0.0939 | +0.0912 | +0.2300 | 0.44 | 0/8 | 0.53 | 0.34 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0004 | +0.0396 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1596 | +0.0918 | +0.1039 | +0.4415 | 0.44 | 0/8 | 0.72 | 0.51 | `max_down_ret` (0.51) | +0.0001 | +0.0396 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1863 | +0.0946 | +0.0801 | -0.1957 | 0.29 | 0/8 | 0.86 | 0.75 | `opening_drive_thrust_ratio` (0.33) | -0.0002 | +0.0396 |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.1111 | +0.0725 | +0.0567 | -0.3559 | 0.42 | 0/8 | 0.58 | 0.50 | `early_body_momentum` (0.51) | -0.0003 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1537 | +0.1226 | +0.1448 | +0.4546 | 0.40 | 0/8 | 0.65 | 0.48 | `star50_limit_proximity_early` (0.60) | -0.0001 | +0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1352 | +0.0856 | +0.0607 | -0.4289 | 0.43 | 0/8 | 0.95 | 0.80 | `early_late_momentum_divergence` (0.62) | -0.0002 | +0.0396 |
| `combo_min__close_vs_open_range__max_down_ret` | Intraday Range Momentum | +1 | +0.1326 | +0.0978 | +0.1067 | +0.1463 | 0.52 | 0/8 | 0.55 | 0.40 | `max_down_ret` (0.51) | -0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1644 | +0.1063 | +0.1041 | +0.2138 | 0.37 | 0/8 | 0.61 | 0.42 | `star50_limit_proximity_early` (0.60) | -0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1729 | +0.0971 | +0.0994 | +0.3465 | 0.38 | 0/8 | 0.79 | 0.60 | `max_down_ret` (0.51) | -0.0001 | +0.0000 |
| `combo_max__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1628 | +0.0781 | +0.0678 | -0.8544 | 0.31 | 0/8 | 0.78 | 0.55 | `net_volume_flow` (0.35) | -0.0003 | +0.0000 |
| `combo_mean__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1416 | +0.0937 | +0.0980 | -0.0542 | 0.38 | 0/8 | 0.69 | 0.46 | `max_down_ret` (0.51) | -0.0002 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.0779 | +0.0256 | +0.0339 | +0.3804 | 0.65 | 0/8 | 1.53 | 0.95 | `trend_bar_close_consistency` (0.76) | +0.0002 | +0.0396 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1568 | +0.0680 | +0.0690 | +0.2253 | 0.33 | 0/8 | 0.86 | 0.52 | — | -0.0002 | +0.0396 |
| `combo_max__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1487 | +0.0768 | +0.0680 | +0.1788 | 0.38 | 0/8 | 0.97 | 0.58 | `first_bar_sentiment` (0.45) | -0.0003 | +0.0000 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1309 | +0.0706 | +0.0542 | +0.1181 | 0.38 | 0/8 | 0.85 | 0.66 | `early_body_momentum` (0.51) | +0.0000 | +0.0000 |
| `combo_mean__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1505 | +0.0844 | +0.1024 | +0.6095 | 0.40 | 0/8 | 0.77 | 0.48 | `max_down_ret` (0.51) | -0.0002 | +0.0000 |
| `combo_clamp_diff__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.0534 | -0.0020 | -0.0123 | -0.1547 | 1.82 | 2/8 | 1.48 | 6.65 | `trend_bar_close_consistency` (0.76) | -0.0002 | +0.0619 |
| `combo_diff__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.0534 | -0.0017 | -0.0119 | -0.1547 | 1.82 | 2/8 | 1.49 | 6.71 | `trend_bar_close_consistency` (0.76) | -0.0001 | +0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1579 | +0.0801 | +0.0750 | +0.4048 | 0.42 | 0/8 | 0.88 | 0.74 | `opening_drive_thrust_ratio` (0.33) | -0.0002 | +0.0396 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1628 | +0.0813 | +0.0785 | +0.5545 | 0.44 | 0/8 | 1.09 | 0.73 | `body_size_progression` (0.58) | +0.0001 | +0.0000 |
| `combo_rank_max__trend_bar_close_consistency__close_vs_open_range` | Other Technical | +1 | +0.1064 | +0.0784 | +0.0660 | +0.6108 | 0.52 | 0/8 | 0.52 | 0.50 | `trend_bar_close_consistency` (0.76) | -0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1587 | +0.0671 | +0.0635 | -0.0086 | 0.41 | 0/8 | 0.81 | 0.59 | `bar_ret_0` (0.33) | -0.0001 | +0.0396 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1209 | +0.0540 | +0.0508 | -0.1785 | 0.45 | 0/8 | 0.93 | 0.50 | `net_volume_flow` (0.35) | -0.0004 | +0.0396 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1428 | +0.1004 | +0.0861 | +0.7531 | 0.70 | 0/8 | 0.39 | 0.19 | `trend_bar_close_consistency` (0.76) | -0.0003 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.0902 | +0.0658 | +0.0877 | -0.2578 | 0.76 | 1/8 | 0.69 | 0.44 | `double_bottom_bull_flag_early` (0.65) | -0.0001 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` | Intraday Range Momentum | +1 | +0.0893 | +0.0329 | +0.0482 | +0.0422 | 0.70 | 1/8 | 1.90 | 1.30 | `early_body_momentum` (0.51) | +0.0001 | +0.0000 |
| `combo_max__early_body_momentum__max_down_ret` | Intraday Range Momentum | +1 | +0.1250 | +0.0694 | +0.0740 | -0.3282 | 0.47 | 0/8 | 0.61 | 0.43 | `early_body_momentum` (0.51) | -0.0004 | +0.0000 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.1054 | +0.0822 | +0.0602 | -0.5999 | 0.48 | 0/8 | 0.60 | 0.60 | — | +0.0001 | +0.0396 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1689 | +0.0913 | +0.1108 | +0.4655 | 0.38 | 0/8 | 0.90 | 0.74 | `max_down_ret` (0.51) | -0.0000 | +0.0000 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.1191 | +0.0893 | +0.0726 | +0.4138 | 0.41 | 0/8 | 0.70 | 0.58 | — | -0.0002 | +0.0396 |
| `open_to_current_return` | Intraday Range Momentum | +1 | +0.1229 | +0.0884 | +0.0708 | +0.4514 | 0.40 | 0/8 | 0.65 | 0.56 | — | -0.0002 | +0.0396 |
| `bar_body_rng_0` | Other Technical | +1 | +0.1470 | +0.0756 | +0.0799 | +0.1818 | 0.27 | 0/8 | 0.88 | 0.57 | — | -0.0002 | +0.0396 |
| `or_fill_ratio` | Other Technical | +1 | +0.0836 | +0.0805 | +0.0708 | +0.3666 | 0.54 | 0/8 | 0.50 | 0.39 | — | -0.0001 | +0.0000 |

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

### 159915ETF — `single` (Full Model Lockbox IC: +0.1452, Sharpe: +1.6978)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1455 | +0.1369 | +0.1414 | +1.4151 | 0.53 | 0/8 | 1.08 | 0.70 | `star50_limit_proximity_early` (0.71) | +0.0010 | +0.0643 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1719 | +0.0959 | +0.1151 | +1.4823 | 0.47 | 1/8 | 0.92 | 0.74 | `first_bar_sentiment` (0.64) | -0.0014 | +0.0780 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1522 | +0.1153 | +0.1314 | +0.6220 | 0.51 | 1/8 | 0.92 | 0.68 | `first_bar_sentiment` (0.64) | +0.0002 | +0.0000 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1553 | +0.1222 | +0.1412 | +1.8782 | 0.58 | 1/8 | 1.09 | 0.72 | `star50_limit_proximity_early` (0.71) | +0.0011 | +0.0531 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1627 | +0.1067 | +0.1236 | +0.7709 | 0.45 | 0/8 | 0.72 | 0.53 | `first_bar_sentiment` (0.64) | +0.0000 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1416 | +0.0964 | +0.0755 | +0.2775 | 0.43 | 0/8 | 0.93 | 0.66 | `first_bar_sentiment` (0.64) | -0.0020 | +0.0000 |
| `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1615 | +0.1202 | +0.1347 | +1.6997 | 0.49 | 1/8 | 1.09 | 0.75 | `star50_limit_proximity_early` (0.71) | +0.0006 | -0.0501 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1433 | +0.1336 | +0.1321 | +1.3123 | 0.60 | 1/8 | 1.02 | 0.64 | `star50_limit_proximity_early` (0.71) | +0.0013 | +0.1000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1747 | +0.1199 | +0.1289 | +1.3884 | 0.43 | 1/8 | 0.95 | 0.73 | `bar_body_rng_0` (0.47) | +0.0001 | +0.0106 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1706 | +0.1157 | +0.1287 | +1.0208 | 0.51 | 1/8 | 0.89 | 0.62 | `rbreaker_sell_setup_proximity_early` (0.45) | +0.0008 | +0.0110 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1740 | +0.1320 | +0.1291 | +1.5083 | 0.39 | 0/8 | 0.92 | 0.72 | `opening_drive_thrust_ratio` (0.50) | -0.0003 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1700 | +0.1155 | +0.1283 | +1.2013 | 0.50 | 1/8 | 0.87 | 0.61 | `rbreaker_sell_setup_proximity_early` (0.45) | +0.0001 | +0.0482 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1463 | +0.1186 | +0.1348 | +1.3879 | 0.64 | 1/8 | 0.88 | 0.54 | `star50_limit_proximity_early` (0.71) | +0.0013 | +0.0643 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0957 | +0.1263 | +0.1190 | +0.4784 | 0.80 | 1/8 | 0.80 | 0.44 | `yesterday_first_30min_return` (0.93) | +0.0006 | +0.2686 |
| `combo_min__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1534 | +0.0936 | +0.1256 | +1.6400 | 0.59 | 1/8 | 1.04 | 0.70 | `star50_limit_proximity_early` (0.71) | +0.0005 | +0.0643 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1569 | +0.1317 | +0.1335 | +0.8612 | 0.37 | 0/8 | 1.01 | 0.86 | `rbreaker_sell_setup_proximity_early` (0.45) | +0.0006 | +0.0450 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1153 | +0.1420 | +0.1422 | +1.2951 | 0.79 | 1/8 | 0.76 | 0.42 | `yesterday_first_30min_return` (0.93) | +0.0013 | +0.2024 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1663 | +0.1227 | +0.1308 | +1.7741 | 0.47 | 0/8 | 0.92 | 0.65 | `star50_limit_proximity_early` (0.71) | +0.0004 | +0.0045 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1546 | +0.1047 | +0.0930 | -0.0651 | 0.42 | 0/8 | 0.83 | 0.72 | `bar_body_rng_0` (0.47) | -0.0004 | -0.1427 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1504 | +0.1020 | +0.0873 | +0.0419 | 0.38 | 0/8 | 0.77 | 0.80 | `first_bar_return` (0.39) | -0.0004 | -0.0639 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1430 | +0.1241 | +0.1119 | +1.1642 | 0.54 | 0/8 | 0.93 | 0.62 | `demark_setup_reversal_early` (0.76) | +0.0002 | +0.0110 |
| `combo_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1499 | +0.1011 | +0.0848 | -0.0049 | 0.35 | 0/8 | 0.81 | 0.79 | `first_bar_return` (0.39) | -0.0001 | -0.0432 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1347 | +0.1128 | +0.0865 | +0.2848 | 0.42 | 0/8 | 0.81 | 0.71 | `opening_drive_thrust_ratio` (0.50) | -0.0006 | -0.0432 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1294 | +0.1225 | +0.1025 | +0.9142 | 0.55 | 0/8 | 0.97 | 0.72 | `demark_setup_reversal_early` (0.76) | +0.0000 | -0.1316 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1487 | +0.0982 | +0.0837 | +0.2006 | 0.43 | 0/8 | 0.75 | 0.62 | `opening_drive_thrust_ratio` (0.50) | -0.0009 | -0.0901 |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | Gap / Overnight Reversal | +1 | +0.1436 | +0.0932 | +0.1177 | +1.6439 | 0.65 | 1/8 | 1.06 | 0.57 | `limit_down_proximity_early` (1.05) | -0.0001 | +0.0270 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1076 | +0.1152 | +0.1311 | +1.1520 | 0.67 | 0/8 | 0.84 | 0.42 | `star50_limit_proximity_early` (0.71) | +0.0003 | +0.0000 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 26.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3639_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1277 | 30 | 80.0% | 53.3% | +0.0200 | +0.0624 |
| B2 Rolling Guard | 211 | 30 | 83.3% | 20.0% | +0.0072 | -0.2587 |
| BH-FDR Gate | 6 | 6 | 83.3% | 33.3% | +0.0086 | -0.1401 |
| B3 Composite Floor | 9 | 9 | 66.7% | 11.1% | +0.0096 | -0.2599 |
| B4 Correlation Gate | 51 | 30 | 83.3% | 73.3% | +0.0255 | +0.1518 |

**Admitted Pool Summary**: 37 features, False Positive Rate = 43.2% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0237, Mean Lock Sharpe = +0.0065

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1822, Lock IC=+0.0379, Lock Sharpe=+1.0599
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1847, Lock IC=+0.0531, Lock Sharpe=+0.8100
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1847, Lock IC=+0.0531, Lock Sharpe=+0.8100
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1978, Lock IC=+0.0522, Lock Sharpe=+0.7840
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1957, Lock IC=+0.0391, Lock Sharpe=+0.5390

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1785, Lock IC=+0.0018, Lock Sharpe=+0.5869
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.1926, Lock IC=+0.0211, Lock Sharpe=+0.3967
- `combo_tri_median__max_up_ret__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1686, Lock IC=+0.0255, Lock Sharpe=+0.2704
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.1796, Lock IC=+0.0134, Lock Sharpe=+0.2036
- `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.1771, Lock IC=+0.0252, Lock Sharpe=+0.0681

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1188, Lock IC=+0.0182, Lock Sharpe=+0.4197
- `combo_z_diff__max_up_ret__early_vwap_acceleration`: Train IC=+0.1188, Lock IC=+0.0182, Lock Sharpe=+0.4197

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.1595, Lock IC=+0.0248, Lock Sharpe=+0.1073

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2178, Lock IC=+0.0660, Lock Sharpe=+0.7636
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.2089, Lock IC=+0.0343, Lock Sharpe=+0.5613
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.2088, Lock IC=+0.0343, Lock Sharpe=+0.5613
- `combo_rel_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1971, Lock IC=+0.0760, Lock Sharpe=+0.4680
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2220, Lock IC=+0.0347, Lock Sharpe=+0.4582

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 37.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5996_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 555 | 30 | 73.3% | 3.3% | +0.0148 | -0.4876 |
| B2 Rolling Guard | 59 | 30 | 40.0% | 10.0% | -0.0058 | -0.6844 |
| BH-FDR Gate | 9 | 9 | 0.0% | 0.0% | -0.0266 | -0.4061 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__willr14__sma100_dist`: Train IC=+0.1400, Lock IC=+0.0526, Lock Sharpe=+0.2861

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `range_expansion_ratio`: Train IC=+0.0895, Lock IC=+0.0645, Lock Sharpe=+0.1756
- `intraday_slope`: Train IC=+0.1254, Lock IC=+0.0621, Lock Sharpe=+0.0417
- `early_trend`: Train IC=+0.1309, Lock IC=+0.0621, Lock Sharpe=+0.0255

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 54.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4274_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 373 | 30 | 40.0% | 10.0% | -0.0109 | -0.5906 |
| B2 Rolling Guard | 57 | 30 | 46.7% | 13.3% | +0.0005 | -0.5710 |
| BH-FDR Gate | 14 | 14 | 85.7% | 42.9% | +0.0287 | -0.0755 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1097, Lock IC=+0.0214, Lock Sharpe=+0.4179
- `volume_surge_direction`: Train IC=+0.1060, Lock IC=+0.0217, Lock Sharpe=+0.2779
- `combo_abs_diff__vix__iv`: Train IC=+0.1144, Lock IC=+0.0006, Lock Sharpe=+0.0180

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__iv__growth_momentum_ratio`: Train IC=+0.0200, Lock IC=+0.0579, Lock Sharpe=+0.4394
- `combo_ifelse__vix__rbreaker_sell_setup_proximity_early__inside_bar_failure_bull`: Train IC=+0.0965, Lock IC=+0.0107, Lock Sharpe=+0.3475
- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0027, Lock Sharpe=+0.1377
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1898, Lock IC=+0.0578, Lock Sharpe=+0.1214

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `star50_limit_proximity_early`: Train IC=+0.0741, Lock IC=+0.0650, Lock Sharpe=+1.0348
- `gap_pct`: Train IC=+0.1531, Lock IC=+0.0795, Lock Sharpe=+0.7643
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0876, Lock IC=+0.0350, Lock Sharpe=+0.5535
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1883, Lock IC=+0.0616, Lock Sharpe=+0.4395
- `combo_diff__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1968, Lock IC=+0.0579, Lock Sharpe=+0.1214

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 67.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5147_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 739 | 30 | 100.0% | 43.3% | +0.0398 | +0.0201 |
| B2 Rolling Guard | 65 | 30 | 76.7% | 40.0% | +0.0308 | +0.0032 |
| BH-FDR Gate | 1 | 1 | 100.0% | 100.0% | +0.0135 | +0.4734 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1728, Lock IC=+0.0772, Lock Sharpe=+0.9161
- `combo_max__bar_vol_4__stoch_k`: Train IC=+0.1730, Lock IC=+0.0683, Lock Sharpe=+0.5164
- `combo_max__bar_vol_4__willr14`: Train IC=+0.1690, Lock IC=+0.0892, Lock Sharpe=+0.4745
- `combo_mean__iv_corridor_width__multi_ema_alignment_5_20_50`: Train IC=+0.1652, Lock IC=+0.0491, Lock Sharpe=+0.4507
- `combo_z_sum__iv_corridor_width__multi_ema_alignment_5_20_50`: Train IC=+0.1652, Lock IC=+0.0491, Lock Sharpe=+0.4507

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.1206, Lock IC=+0.0431, Lock Sharpe=+0.9119
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1206, Lock IC=+0.0431, Lock Sharpe=+0.9119
- `combo_tri_min__bar_vol_4__volume_surge_max__yesterday_body_ratio`: Train IC=+0.1169, Lock IC=+0.0657, Lock Sharpe=+0.8959
- `star50_limit_proximity_early`: Train IC=+0.1203, Lock IC=+0.0239, Lock Sharpe=+0.6822
- `combo_tri_median__bar_vol_4__volume_surge_max__yesterday_body_ratio`: Train IC=+0.1741, Lock IC=+0.0625, Lock Sharpe=+0.6535

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ratio__star50_limit_proximity_early__bar_vol_4`: Train IC=+0.1251, Lock IC=+0.0135, Lock Sharpe=+0.4734

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.1% lock IC > 0, 13.3% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7213_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 451 | 10 | 30.0% | 0.0% | -0.0176 | -0.7672 |
| B2 Rolling Guard | 66 | 11 | 54.5% | 18.2% | +0.0154 | -0.4584 |
| BH-FDR Gate | 7 | 6 | 0.0% | 0.0% | -0.0484 | -1.7936 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bar_vol_4`: Train IC=+0.0880, Lock IC=+0.0834, Lock Sharpe=+0.3081
- `roc20`: Train IC=+0.0576, Lock IC=+0.0709, Lock Sharpe=+0.0586

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2946_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 277 | 30 | 63.3% | 53.3% | +0.0268 | -0.0535 |
| B2 Rolling Guard | 47 | 30 | 26.7% | 0.0% | -0.0048 | -0.4313 |
| BH-FDR Gate | 6 | 6 | 33.3% | 16.7% | -0.0212 | -0.5549 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1124, Lock IC=+0.0772, Lock Sharpe=+1.0118
- `gap_pct`: Train IC=+0.1368, Lock IC=+0.0756, Lock Sharpe=+0.9755
- `combo_mean__sma50_dist__bar_vol_4`: Train IC=+0.1659, Lock IC=+0.0916, Lock Sharpe=+0.6196
- `combo_z_sum__sma50_dist__bar_vol_4`: Train IC=+0.1659, Lock IC=+0.0916, Lock Sharpe=+0.6196
- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0861, Lock Sharpe=+0.5769

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1622, Lock IC=+0.0130, Lock Sharpe=+0.5948

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 79.0% lock IC > 0, 49.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0052_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2306 | 30 | 100.0% | 76.7% | +0.0869 | +0.2436 |
| B2 Rolling Guard | 303 | 30 | 96.7% | 70.0% | +0.0747 | +0.1821 |
| BH-FDR Gate | 2 | 2 | 0.0% | 0.0% | -0.0051 | -1.0508 |
| B3 Composite Floor | 406 | 30 | 100.0% | 63.3% | +0.0965 | +0.2162 |
| B4 Correlation Gate | 1101 | 30 | 100.0% | 90.0% | +0.1030 | +0.6299 |

**Admitted Pool Summary**: 379 features, False Positive Rate = 29.8% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0860, Mean Lock Sharpe = +0.2560

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2686, Lock IC=+0.1112, Lock Sharpe=+1.5645
- `combo_mean__late_bar_momentum__demark_setup_reversal_early`: Train IC=+0.2417, Lock IC=+0.1189, Lock Sharpe=+0.9639
- `combo_z_sum__late_bar_momentum__demark_setup_reversal_early`: Train IC=+0.2417, Lock IC=+0.1189, Lock Sharpe=+0.9639
- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2773, Lock IC=+0.0859, Lock Sharpe=+0.8391
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2786, Lock IC=+0.0891, Lock Sharpe=+0.8043

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.1846, Lock IC=+0.0339, Lock Sharpe=+0.9260
- `combo_sig_product__demark_setup_reversal_early__max_down_ret`: Train IC=+0.2097, Lock IC=+0.1540, Lock Sharpe=+0.7754
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1953, Lock IC=+0.1083, Lock Sharpe=+0.5995
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1953, Lock IC=+0.1083, Lock Sharpe=+0.5995
- `combo_clamp_diff__demark_setup_reversal_early__close_vs_open_range`: Train IC=+0.1948, Lock IC=+0.1249, Lock Sharpe=+0.5788

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2922, Lock IC=+0.1095, Lock Sharpe=+0.9375
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2922, Lock IC=+0.1095, Lock Sharpe=+0.9375
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2922, Lock IC=+0.1095, Lock Sharpe=+0.9375
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2922, Lock IC=+0.1095, Lock Sharpe=+0.9375
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2905, Lock IC=+0.1039, Lock Sharpe=+0.7576

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.3185, Lock IC=+0.1052, Lock Sharpe=+1.2118
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.3241, Lock IC=+0.1143, Lock Sharpe=+1.1531
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.3241, Lock IC=+0.1143, Lock Sharpe=+1.1531
- `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.3391, Lock IC=+0.1285, Lock Sharpe=+1.1219
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.3138, Lock IC=+0.1015, Lock Sharpe=+1.0848

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 75.0% lock IC > 0, 36.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2633_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 954 | 30 | 100.0% | 83.3% | +0.0694 | +0.0635 |
| B2 Rolling Guard | 97 | 30 | 80.0% | 23.3% | +0.0532 | -0.3792 |
| BH-FDR Gate | 53 | 30 | 96.7% | 60.0% | +0.0702 | -0.0784 |
| B3 Composite Floor | 36 | 30 | 100.0% | 40.0% | +0.0514 | -0.0327 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_buy_setup_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0775, Lock Sharpe=+0.4921
- `combo_min__rbreaker_buy_setup_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0775, Lock Sharpe=+0.4921
- `combo_min__rbreaker_buy_setup_proximity_early__limit_down_proximity_day`: Train IC=+0.2604, Lock IC=+0.0775, Lock Sharpe=+0.4921
- `combo_min__limit_down_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0775, Lock Sharpe=+0.4921
- `combo_min__limit_down_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0775, Lock Sharpe=+0.4921

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_day_vwap_dev`: Train IC=+0.1074, Lock IC=+0.0692, Lock Sharpe=+0.3684
- `bar_vol_4`: Train IC=+0.0794, Lock IC=+0.0045, Lock Sharpe=+0.2622
- `combo_diff__donchian_breakout_proximity_20d__yesterday_return`: Train IC=+0.0495, Lock IC=+0.0702, Lock Sharpe=+0.1229
- `combo_z_diff__donchian_breakout_proximity_20d__yesterday_return`: Train IC=+0.0495, Lock IC=+0.0702, Lock Sharpe=+0.1229
- `combo_diff__donchian_breakout_proximity_20d__limit_up_proximity_day`: Train IC=+0.0495, Lock IC=+0.0702, Lock Sharpe=+0.1229

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_buy_setup_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.8136
- `combo_rank_min__limit_down_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.8136
- `first_30min_return`: Train IC=+0.1012, Lock IC=+0.0708, Lock Sharpe=+0.1899
- `open_to_current_return`: Train IC=+0.1012, Lock IC=+0.0708, Lock Sharpe=+0.1899
- `combo_mean__opening_momentum_score__star50_limit_proximity_early`: Train IC=+0.1292, Lock IC=+0.1045, Lock Sharpe=+0.1559

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1742, Lock IC=+0.1042, Lock Sharpe=+1.2414
- `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2116, Lock IC=+0.1196, Lock Sharpe=+1.2060
- `combo_rank_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1842, Lock IC=+0.1130, Lock Sharpe=+0.9668
- `combo_rank_min__yesterday_return__star50_limit_proximity_early`: Train IC=+0.2061, Lock IC=+0.0988, Lock Sharpe=+0.4535
- `combo_rank_min__limit_up_proximity_day__star50_limit_proximity_early`: Train IC=+0.2061, Lock IC=+0.0988, Lock Sharpe=+0.4535

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 56.0% lock IC > 0, 34.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2295_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 356 | 30 | 46.7% | 43.3% | +0.0116 | -0.3121 |
| B2 Rolling Guard | 66 | 30 | 56.7% | 26.7% | +0.0158 | -0.3082 |
| BH-FDR Gate | 6 | 6 | 66.7% | 66.7% | +0.0734 | +0.1586 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1907, Lock IC=+0.1261, Lock Sharpe=+0.7706
- `combo_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0711, Lock Sharpe=+0.7164
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0710, Lock Sharpe=+0.7164
- `combo_z_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0711, Lock Sharpe=+0.7164
- `gap_pct`: Train IC=+0.1160, Lock IC=+0.0889, Lock Sharpe=+0.4908

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1375, Lock IC=+0.0869, Lock Sharpe=+0.5888
- `close_vs_open_range`: Train IC=+0.0789, Lock IC=+0.0872, Lock Sharpe=+0.4868
- `combo_min__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1062, Lock IC=+0.1186, Lock Sharpe=+0.3869
- `donchian_width_atr_ratio_20d`: Train IC=+0.0254, Lock IC=+0.0944, Lock Sharpe=+0.3236
- `trend_bar_close_consistency`: Train IC=+0.0828, Lock IC=+0.0529, Lock Sharpe=+0.3042

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+1.0439
- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+1.0439
- `combo_mean__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.4994
- `combo_z_sum__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.4994

### 588000ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 23.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8293_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 615 | 30 | 83.3% | 60.0% | +0.0298 | +0.2329 |
| B2 Rolling Guard | 351 | 30 | 36.7% | 36.7% | -0.0224 | -0.3049 |
| BH-FDR Gate | 40 | 30 | 16.7% | 6.7% | -0.0524 | -0.8951 |
| B3 Composite Floor | 437 | 30 | 3.3% | 3.3% | -0.0415 | -0.5462 |
| B4 Correlation Gate | 24 | 24 | 20.8% | 20.8% | -0.0465 | -0.5852 |

**Admitted Pool Summary**: 12 features, False Positive Rate = 66.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0390, Mean Lock Sharpe = -0.3959

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__impulse_bar_dominance__volume_weighted_momentum_acceleration`: Train IC=+0.2144, Lock IC=+0.0006, Lock Sharpe=+1.1755
- `combo_sig_product__directional_volume_signature__volume_weighted_momentum_acceleration`: Train IC=+0.2270, Lock IC=+0.0182, Lock Sharpe=+0.9905
- `volume_weighted_momentum_acceleration`: Train IC=+0.2216, Lock IC=+0.0363, Lock Sharpe=+0.9905
- `combo_min__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.2023, Lock IC=+0.0414, Lock Sharpe=+0.6246
- `combo_rel_diff__smooth_momentum_structure__opening_drive_thrust_ratio`: Train IC=+0.2624, Lock IC=+0.0133, Lock Sharpe=+0.4587

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

_Null Baseline (un-gated candidate pool): 75.0% lock IC > 0, 63.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.2912_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2151 | 30 | 100.0% | 80.0% | +0.1115 | +0.8869 |
| B2 Rolling Guard | 444 | 30 | 100.0% | 100.0% | +0.1158 | +0.9996 |
| BH-FDR Gate | 12 | 12 | 91.7% | 41.7% | +0.0559 | +0.2368 |
| B3 Composite Floor | 284 | 30 | 100.0% | 100.0% | +0.1171 | +1.1607 |
| B4 Correlation Gate | 22 | 22 | 100.0% | 95.5% | +0.0861 | +0.7336 |

**Admitted Pool Summary**: 31 features, False Positive Rate = 3.2% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0942, Mean Lock Sharpe = +0.7621

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2183, Lock IC=+0.1519, Lock Sharpe=+2.0257
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2393, Lock IC=+0.1293, Lock Sharpe=+1.8642
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2323, Lock IC=+0.1481, Lock Sharpe=+1.8030
- `combo_min__rbreaker_buy_setup_proximity_early__volume_price_confirmation`: Train IC=+0.2151, Lock IC=+0.1383, Lock Sharpe=+1.7656
- `combo_min__limit_down_proximity_early__volume_price_confirmation`: Train IC=+0.2151, Lock IC=+0.1383, Lock Sharpe=+1.7656

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2169, Lock IC=+0.1315, Lock Sharpe=+1.6378
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2169, Lock IC=+0.1315, Lock Sharpe=+1.6378
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2456, Lock IC=+0.1292, Lock Sharpe=+1.5083
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.2456, Lock IC=+0.1292, Lock Sharpe=+1.5083
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2454, Lock IC=+0.1291, Lock Sharpe=+1.5083

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1128, Lock IC=+0.0563, Lock Sharpe=+1.0973
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1128, Lock IC=+0.0563, Lock Sharpe=+1.0973
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1091, Lock IC=+0.0570, Lock Sharpe=+1.0973
- `close_vs_open_range`: Train IC=+0.0811, Lock IC=+0.0988, Lock Sharpe=+0.7603
- `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1127, Lock IC=+0.1224, Lock Sharpe=+0.6114

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2403, Lock IC=+0.1433, Lock Sharpe=+2.2148
- `combo_min__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2754, Lock IC=+0.1374, Lock Sharpe=+2.1399
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2603, Lock IC=+0.1364, Lock Sharpe=+1.7552
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0`: Train IC=+0.2601, Lock IC=+0.1363, Lock Sharpe=+1.7552
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2487, Lock IC=+0.1408, Lock Sharpe=+1.5108

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_z_sum__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2158, Lock IC=+0.1214, Lock Sharpe=+1.7502
- `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.2016, Lock IC=+0.1177, Lock Sharpe=+1.6439
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.1901, Lock IC=+0.0820, Lock Sharpe=+1.2127
- `combo_tri_min__yesterday_early_momentum__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2608, Lock IC=+0.1030, Lock Sharpe=+1.0626
- `combo_z_sum__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1596, Lock IC=+0.0702, Lock Sharpe=+0.9720

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 71.0% lock IC > 0, 45.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0303_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 651 | 30 | 80.0% | 60.0% | +0.0750 | +0.3318 |
| B2 Rolling Guard | 67 | 30 | 96.7% | 90.0% | +0.0865 | +0.6465 |
| BH-FDR Gate | 24 | 24 | 91.7% | 70.8% | +0.0661 | +0.4274 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1406, Lock IC=+0.1675, Lock Sharpe=+1.2090
- `combo_tri_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1450, Lock IC=+0.1556, Lock Sharpe=+1.0392
- `combo_tri_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1450, Lock IC=+0.1556, Lock Sharpe=+1.0392
- `combo_mean__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1398, Lock IC=+0.1467, Lock Sharpe=+0.9504
- `combo_z_sum__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1398, Lock IC=+0.1467, Lock Sharpe=+0.9504

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1336, Lock IC=+0.1017, Lock Sharpe=+1.2574
- `combo_tri_min__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1093, Lock IC=+0.1156, Lock Sharpe=+1.0081
- `combo_tri_min__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1093, Lock IC=+0.1156, Lock Sharpe=+1.0081
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1103, Lock IC=+0.0981, Lock Sharpe=+0.9588
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1103, Lock IC=+0.0981, Lock Sharpe=+0.9588

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `net_volume_flow`: Train IC=+0.0152, Lock IC=+0.1008, Lock Sharpe=+1.6234
- `opening_auction_imbalance`: Train IC=+0.0152, Lock IC=+0.1008, Lock Sharpe=+1.6234
- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1514, Lock IC=+0.1359, Lock Sharpe=+1.3524
- `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.0240, Lock IC=+0.1013, Lock Sharpe=+1.1572
- `combo_z_sum__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.0240, Lock IC=+0.1013, Lock Sharpe=+1.1572

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 37.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4769_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 286 | 30 | 53.3% | 30.0% | +0.0014 | -0.3800 |
| B2 Rolling Guard | 67 | 30 | 53.3% | 36.7% | +0.0109 | -0.2081 |
| BH-FDR Gate | 3 | 3 | 100.0% | 66.7% | +0.1026 | +0.5571 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.1709, Lock IC=+0.0829, Lock Sharpe=+0.8402
- `yesterday_pm_return`: Train IC=+0.1096, Lock IC=+0.0803, Lock Sharpe=+0.7355
- `combo_mean__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.2129, Lock IC=+0.0701, Lock Sharpe=+0.4459
- `combo_z_sum__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.2129, Lock IC=+0.0701, Lock Sharpe=+0.4459
- `early_realized_vol`: Train IC=+0.0947, Lock IC=+0.0234, Lock Sharpe=+0.4184

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__morning_volume_weighted_momentum__failed_breakout_reversal_early`: Train IC=+0.0039, Lock IC=+0.0704, Lock Sharpe=+1.2240
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
| 0.45 | 0.10 | 541 | +0.0289 | 100.0% |
| 0.45 | 0.20 | 528 | +0.0289 | 100.0% |
| 0.45 | 0.30 | 460 | +0.0289 | 100.0% |
| 0.45 | 0.40 | 337 | +0.0289 | 100.0% |
| 0.45 | 0.50 | 214 | +0.0269 | 100.0% |
| 0.50 | 0.15 | 534 | +0.0289 | 100.0% |
| 0.50 | 0.25 | 506 | +0.0289 | 100.0% |
| 0.50 | 0.35 | 397 | +0.0289 | 100.0% |
| 0.50 | 0.45 | 279 | +0.0269 | 100.0% |
| 0.55 | 0.10 | 535 | +0.0289 | 100.0% |
| 0.55 | 0.20 | 527 | +0.0289 | 100.0% |
| 0.55 | 0.30 | 460 | +0.0289 | 100.0% |
| 0.55 | 0.40 | 337 | +0.0289 | 100.0% |
| 0.55 | 0.50 | 214 | +0.0269 | 100.0% |
| 0.60 | 0.15 | 489 | +0.0289 | 100.0% |
| 0.60 | 0.25 | 485 | +0.0289 | 100.0% |
| 0.60 | 0.35 | 395 | +0.0289 | 100.0% |
| 0.60 | 0.45 | 279 | +0.0269 | 100.0% |
| 0.65 | 0.10 | 351 | +0.0289 | 100.0% |
| 0.65 | 0.20 | 351 | +0.0289 | 100.0% |
| 0.65 | 0.30 | 351 | +0.0289 | 100.0% |
| 0.65 | 0.40 | 315 | +0.0289 | 100.0% |
| 0.65 | 0.50 | 213 | +0.0269 | 100.0% |
| 0.70 | 0.15 | 171 | +0.0279 | 100.0% |
| 0.70 | 0.25 | 171 | +0.0279 | 100.0% |
| 0.70 | 0.35 | 171 | +0.0279 | 100.0% |
| 0.70 | 0.45 | 169 | +0.0279 | 100.0% |
| 0.75 | 0.10 | 30 | +0.0205 | 90.0% |
| 0.75 | 0.20 | 30 | +0.0205 | 90.0% |
| 0.75 | 0.30 | 30 | +0.0205 | 90.0% |
| 0.75 | 0.40 | 30 | +0.0205 | 90.0% |
| 0.75 | 0.50 | 30 | +0.0205 | 90.0% |
| 0.80 | 0.15 | 5 | +0.0255 | 100.0% |
| 0.80 | 0.25 | 5 | +0.0255 | 100.0% |
| 0.80 | 0.35 | 5 | +0.0255 | 100.0% |
| 0.80 | 0.45 | 5 | +0.0255 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 541 candidates, mean lock IC=+0.0289, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 16 | -0.0286 | 0.0% |
| 0.45 | 0.20 | 10 | -0.0244 | 0.0% |
| 0.45 | 0.30 | 5 | -0.0269 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 11 | -0.0286 | 0.0% |
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
| 0.45 | 0.10 | 20 | +0.0355 | 100.0% |
| 0.45 | 0.20 | 10 | +0.0261 | 80.0% |
| 0.45 | 0.30 | 7 | +0.0252 | 85.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 15 | +0.0290 | 90.0% |
| 0.50 | 0.25 | 8 | +0.0231 | 87.5% |
| 0.50 | 0.35 | 4 | +0.0201 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 15 | +0.0338 | 90.0% |
| 0.55 | 0.20 | 10 | +0.0261 | 80.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 20 candidates, mean lock IC=+0.0355, 100.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 233 | +0.0466 | 100.0% |
| 0.45 | 0.20 | 224 | +0.0466 | 100.0% |
| 0.45 | 0.30 | 202 | +0.0466 | 100.0% |
| 0.45 | 0.40 | 188 | +0.0466 | 100.0% |
| 0.45 | 0.50 | 156 | +0.0392 | 100.0% |
| 0.50 | 0.15 | 229 | +0.0466 | 100.0% |
| 0.50 | 0.25 | 221 | +0.0466 | 100.0% |
| 0.50 | 0.35 | 196 | +0.0466 | 100.0% |
| 0.50 | 0.45 | 164 | +0.0466 | 100.0% |
| 0.55 | 0.10 | 230 | +0.0466 | 100.0% |
| 0.55 | 0.20 | 224 | +0.0466 | 100.0% |
| 0.55 | 0.30 | 202 | +0.0466 | 100.0% |
| 0.55 | 0.40 | 188 | +0.0466 | 100.0% |
| 0.55 | 0.50 | 156 | +0.0392 | 100.0% |
| 0.60 | 0.15 | 208 | +0.0466 | 100.0% |
| 0.60 | 0.25 | 208 | +0.0466 | 100.0% |
| 0.60 | 0.35 | 196 | +0.0466 | 100.0% |
| 0.60 | 0.45 | 164 | +0.0466 | 100.0% |
| 0.65 | 0.10 | 181 | +0.0466 | 100.0% |
| 0.65 | 0.20 | 181 | +0.0466 | 100.0% |
| 0.65 | 0.30 | 181 | +0.0466 | 100.0% |
| 0.65 | 0.40 | 179 | +0.0466 | 100.0% |
| 0.65 | 0.50 | 156 | +0.0392 | 100.0% |
| 0.70 | 0.15 | 144 | +0.0392 | 100.0% |
| 0.70 | 0.25 | 144 | +0.0392 | 100.0% |
| 0.70 | 0.35 | 144 | +0.0392 | 100.0% |
| 0.70 | 0.45 | 144 | +0.0392 | 100.0% |
| 0.75 | 0.10 | 87 | +0.0365 | 100.0% |
| 0.75 | 0.20 | 87 | +0.0365 | 100.0% |
| 0.75 | 0.30 | 87 | +0.0365 | 100.0% |
| 0.75 | 0.40 | 87 | +0.0365 | 100.0% |
| 0.75 | 0.50 | 87 | +0.0365 | 100.0% |
| 0.80 | 0.15 | 55 | +0.0309 | 100.0% |
| 0.80 | 0.25 | 55 | +0.0309 | 100.0% |
| 0.80 | 0.35 | 55 | +0.0309 | 100.0% |
| 0.80 | 0.45 | 55 | +0.0309 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 233 candidates, mean lock IC=+0.0466, 100.0% positive

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
| 0.45 | 0.10 | 10 | -0.0041 | 50.0% |
| 0.45 | 0.20 | 7 | +0.0089 | 57.1% |
| 0.45 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | -0.0092 | 44.4% |
| 0.50 | 0.25 | 3 | -0.0020 | 66.7% |
| 0.50 | 0.35 | 3 | -0.0020 | 66.7% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | -0.0122 | 42.9% |
| 0.55 | 0.20 | 5 | -0.0070 | 40.0% |
| 0.55 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 4 | -0.0075 | 50.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 7 candidates, mean lock IC=+0.0089, 57.1% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 2409 | +0.1140 | 100.0% |
| 0.45 | 0.20 | 2383 | +0.1140 | 100.0% |
| 0.45 | 0.30 | 2322 | +0.1140 | 100.0% |
| 0.45 | 0.40 | 2194 | +0.1140 | 100.0% |
| 0.45 | 0.50 | 1935 | +0.1140 | 100.0% |
| 0.50 | 0.15 | 2404 | +0.1140 | 100.0% |
| 0.50 | 0.25 | 2359 | +0.1140 | 100.0% |
| 0.50 | 0.35 | 2263 | +0.1140 | 100.0% |
| 0.50 | 0.45 | 2102 | +0.1140 | 100.0% |
| 0.55 | 0.10 | 2404 | +0.1140 | 100.0% |
| 0.55 | 0.20 | 2383 | +0.1140 | 100.0% |
| 0.55 | 0.30 | 2322 | +0.1140 | 100.0% |
| 0.55 | 0.40 | 2194 | +0.1140 | 100.0% |
| 0.55 | 0.50 | 1935 | +0.1140 | 100.0% |
| 0.60 | 0.15 | 2319 | +0.1140 | 100.0% |
| 0.60 | 0.25 | 2313 | +0.1140 | 100.0% |
| 0.60 | 0.35 | 2258 | +0.1140 | 100.0% |
| 0.60 | 0.45 | 2102 | +0.1140 | 100.0% |
| 0.65 | 0.10 | 2137 | +0.1140 | 100.0% |
| 0.65 | 0.20 | 2137 | +0.1140 | 100.0% |
| 0.65 | 0.30 | 2135 | +0.1140 | 100.0% |
| 0.65 | 0.40 | 2110 | +0.1140 | 100.0% |
| 0.65 | 0.50 | 1930 | +0.1140 | 100.0% |
| 0.70 | 0.15 | 1742 | +0.1140 | 100.0% |
| 0.70 | 0.25 | 1742 | +0.1140 | 100.0% |
| 0.70 | 0.35 | 1742 | +0.1140 | 100.0% |
| 0.70 | 0.45 | 1738 | +0.1140 | 100.0% |
| 0.75 | 0.10 | 960 | +0.1140 | 100.0% |
| 0.75 | 0.20 | 960 | +0.1140 | 100.0% |
| 0.75 | 0.30 | 960 | +0.1140 | 100.0% |
| 0.75 | 0.40 | 960 | +0.1140 | 100.0% |
| 0.75 | 0.50 | 960 | +0.1140 | 100.0% |
| 0.80 | 0.15 | 293 | +0.1161 | 100.0% |
| 0.80 | 0.25 | 293 | +0.1161 | 100.0% |
| 0.80 | 0.35 | 293 | +0.1161 | 100.0% |
| 0.80 | 0.45 | 293 | +0.1161 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 293 candidates, mean lock IC=+0.1161, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 110 | +0.0496 | 100.0% |
| 0.45 | 0.20 | 85 | +0.0496 | 100.0% |
| 0.45 | 0.30 | 45 | +0.0358 | 100.0% |
| 0.45 | 0.40 | 8 | +0.0522 | 87.5% |
| 0.45 | 0.50 | 2 | +0.1075 | 100.0% |
| 0.50 | 0.15 | 90 | +0.0496 | 100.0% |
| 0.50 | 0.25 | 63 | +0.0669 | 100.0% |
| 0.50 | 0.35 | 19 | +0.0512 | 100.0% |
| 0.50 | 0.45 | 4 | +0.0784 | 100.0% |
| 0.55 | 0.10 | 101 | +0.0496 | 100.0% |
| 0.55 | 0.20 | 84 | +0.0496 | 100.0% |
| 0.55 | 0.30 | 45 | +0.0358 | 100.0% |
| 0.55 | 0.40 | 8 | +0.0522 | 87.5% |
| 0.55 | 0.50 | 2 | +0.1075 | 100.0% |
| 0.60 | 0.15 | 56 | +0.0358 | 100.0% |
| 0.60 | 0.25 | 55 | +0.0358 | 100.0% |
| 0.60 | 0.35 | 19 | +0.0512 | 100.0% |
| 0.60 | 0.45 | 4 | +0.0784 | 100.0% |
| 0.65 | 0.10 | 4 | +0.0784 | 100.0% |
| 0.65 | 0.20 | 4 | +0.0784 | 100.0% |
| 0.65 | 0.30 | 4 | +0.0784 | 100.0% |
| 0.65 | 0.40 | 4 | +0.0784 | 100.0% |
| 0.65 | 0.50 | 2 | +0.1075 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.45 → 4 candidates, mean lock IC=+0.0784, 100.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 15 | +0.0578 | 80.0% |
| 0.45 | 0.20 | 3 | -0.0164 | 33.3% |
| 0.45 | 0.30 | 1 | -0.0233 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | +0.0584 | 77.8% |
| 0.50 | 0.25 | 1 | -0.0233 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0734 | 66.7% |
| 0.55 | 0.20 | 2 | -0.0261 | 0.0% |
| 0.55 | 0.30 | 1 | -0.0233 | 0.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 6 candidates, mean lock IC=+0.0734, 66.7% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1031 | -0.0553 | 0.0% |
| 0.45 | 0.20 | 969 | -0.0553 | 0.0% |
| 0.45 | 0.30 | 849 | -0.0553 | 0.0% |
| 0.45 | 0.40 | 752 | -0.0553 | 0.0% |
| 0.45 | 0.50 | 639 | -0.0553 | 0.0% |
| 0.50 | 0.15 | 1002 | -0.0553 | 0.0% |
| 0.50 | 0.25 | 906 | -0.0553 | 0.0% |
| 0.50 | 0.35 | 803 | -0.0553 | 0.0% |
| 0.50 | 0.45 | 684 | -0.0553 | 0.0% |
| 0.55 | 0.10 | 990 | -0.0553 | 0.0% |
| 0.55 | 0.20 | 952 | -0.0553 | 0.0% |
| 0.55 | 0.30 | 849 | -0.0553 | 0.0% |
| 0.55 | 0.40 | 752 | -0.0553 | 0.0% |
| 0.55 | 0.50 | 639 | -0.0553 | 0.0% |
| 0.60 | 0.15 | 880 | -0.0553 | 0.0% |
| 0.60 | 0.25 | 850 | -0.0553 | 0.0% |
| 0.60 | 0.35 | 793 | -0.0553 | 0.0% |
| 0.60 | 0.45 | 684 | -0.0553 | 0.0% |
| 0.65 | 0.10 | 748 | -0.0553 | 0.0% |
| 0.65 | 0.20 | 748 | -0.0553 | 0.0% |
| 0.65 | 0.30 | 745 | -0.0553 | 0.0% |
| 0.65 | 0.40 | 724 | -0.0553 | 0.0% |
| 0.65 | 0.50 | 637 | -0.0553 | 0.0% |
| 0.70 | 0.15 | 607 | -0.0553 | 0.0% |
| 0.70 | 0.25 | 607 | -0.0553 | 0.0% |
| 0.70 | 0.35 | 607 | -0.0553 | 0.0% |
| 0.70 | 0.45 | 601 | -0.0553 | 0.0% |
| 0.75 | 0.10 | 425 | -0.0553 | 0.0% |
| 0.75 | 0.20 | 425 | -0.0553 | 0.0% |
| 0.75 | 0.30 | 425 | -0.0553 | 0.0% |
| 0.75 | 0.40 | 425 | -0.0553 | 0.0% |
| 0.75 | 0.50 | 425 | -0.0553 | 0.0% |
| 0.80 | 0.15 | 160 | -0.0468 | 0.0% |
| 0.80 | 0.25 | 160 | -0.0468 | 0.0% |
| 0.80 | 0.35 | 160 | -0.0468 | 0.0% |
| 0.80 | 0.45 | 160 | -0.0468 | 0.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 160 candidates, mean lock IC=-0.0468, 0.0% positive

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
| 0.45 | 0.10 | 986 | +0.1296 | 100.0% |
| 0.45 | 0.20 | 959 | +0.1296 | 100.0% |
| 0.45 | 0.30 | 868 | +0.1296 | 100.0% |
| 0.45 | 0.40 | 587 | +0.1296 | 100.0% |
| 0.45 | 0.50 | 278 | +0.1296 | 100.0% |
| 0.50 | 0.15 | 983 | +0.1296 | 100.0% |
| 0.50 | 0.25 | 921 | +0.1296 | 100.0% |
| 0.50 | 0.35 | 758 | +0.1296 | 100.0% |
| 0.50 | 0.45 | 425 | +0.1296 | 100.0% |
| 0.55 | 0.10 | 978 | +0.1296 | 100.0% |
| 0.55 | 0.20 | 955 | +0.1296 | 100.0% |
| 0.55 | 0.30 | 868 | +0.1296 | 100.0% |
| 0.55 | 0.40 | 587 | +0.1296 | 100.0% |
| 0.55 | 0.50 | 278 | +0.1296 | 100.0% |
| 0.60 | 0.15 | 894 | +0.1296 | 100.0% |
| 0.60 | 0.25 | 879 | +0.1296 | 100.0% |
| 0.60 | 0.35 | 755 | +0.1296 | 100.0% |
| 0.60 | 0.45 | 425 | +0.1296 | 100.0% |
| 0.65 | 0.10 | 579 | +0.1296 | 100.0% |
| 0.65 | 0.20 | 579 | +0.1296 | 100.0% |
| 0.65 | 0.30 | 579 | +0.1296 | 100.0% |
| 0.65 | 0.40 | 507 | +0.1296 | 100.0% |
| 0.65 | 0.50 | 277 | +0.1296 | 100.0% |
| 0.70 | 0.15 | 172 | +0.1268 | 100.0% |
| 0.70 | 0.25 | 172 | +0.1268 | 100.0% |
| 0.70 | 0.35 | 172 | +0.1268 | 100.0% |
| 0.70 | 0.45 | 169 | +0.1268 | 100.0% |
| 0.75 | 0.10 | 23 | +0.1240 | 100.0% |
| 0.75 | 0.20 | 23 | +0.1240 | 100.0% |
| 0.75 | 0.30 | 23 | +0.1240 | 100.0% |
| 0.75 | 0.40 | 23 | +0.1240 | 100.0% |
| 0.75 | 0.50 | 23 | +0.1240 | 100.0% |
| 0.80 | 0.15 | 5 | +0.0164 | 20.0% |
| 0.80 | 0.25 | 5 | +0.0164 | 20.0% |
| 0.80 | 0.35 | 5 | +0.0164 | 20.0% |
| 0.80 | 0.45 | 5 | +0.0164 | 20.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 986 candidates, mean lock IC=+0.1296, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 43 | +0.0748 | 100.0% |
| 0.45 | 0.20 | 28 | +0.0777 | 100.0% |
| 0.45 | 0.30 | 12 | +0.0605 | 90.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 33 | +0.0739 | 100.0% |
| 0.50 | 0.25 | 15 | +0.0752 | 100.0% |
| 0.50 | 0.35 | 2 | +0.1002 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 28 | +0.0711 | 100.0% |
| 0.55 | 0.20 | 22 | +0.0711 | 100.0% |
| 0.55 | 0.30 | 12 | +0.0605 | 90.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 11 | +0.0532 | 90.0% |
| 0.60 | 0.25 | 11 | +0.0532 | 90.0% |
| 0.60 | 0.35 | 1 | +0.0645 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 28 candidates, mean lock IC=+0.0777, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | +0.0687 | 88.9% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1307 | +0.0965 | +0.0290 | 0.22x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +0.1386 | +0.0751 | +0.0166 | 0.12x | 2017-06-09 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1258 | +0.0752 | +0.0344 | 0.27x | 2017-06-09 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1182 | +0.0975 | +0.0517 | 0.44x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1353 | +0.0868 | +0.0337 | 0.25x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1170 | +0.0917 | +0.0194 | 0.17x | 2017-05-09 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1182 | +0.0975 | +0.0405 | 0.34x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1312 | +0.0961 | +0.0216 | 0.16x | 2017-06-09 |
| `rbreaker_sell_setup_proximity_early` | +0.0953 | +0.0781 | +0.0616 | 0.65x | 2016-08-24 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1067 | +0.1135 | -0.0031 | -0.03x | 2015-03-16 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1233 | +0.0993 | +0.0209 | 0.17x | 2015-02-06 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.0985 | +0.1158 | -0.0101 | -0.10x | 2015-02-06 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1182 | +0.0958 | +0.0381 | 0.32x | 2017-08-08 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1123 | +0.1250 | -0.0128 | -0.11x | 2015-02-06 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1102 | +0.0948 | +0.0489 | 0.44x | 2016-08-24 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +0.0899 | +0.0831 | +0.0120 | 0.13x | 2010-10-15 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1046 | +0.1154 | -0.0220 | -0.21x | 2015-02-06 |
| `combo_mean__max_up_ret__volume_surge_direction` | +0.0989 | +0.0955 | +0.0113 | 0.11x | 2014-07-04 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1169 | +0.0957 | -0.0146 | -0.12x | 2017-06-09 |
| `star50_limit_proximity_early` | +0.0893 | +0.0629 | +0.0650 | 0.73x | 2011-09-20 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +0.1198 | +0.0924 | +0.0183 | 0.15x | 2017-02-06 |
| `combo_max__bar_body_rng_0__volume_surge_direction` | +0.0827 | +0.1032 | +0.0185 | 0.22x | 2013-08-21 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.2095 | +0.0731 | +0.1176 | 0.56x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2074 | +0.0609 | +0.1215 | 0.59x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.2070 | +0.0656 | +0.1200 | 0.58x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1770 | +0.0687 | +0.1250 | 0.71x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2078 | +0.0859 | +0.1219 | 0.59x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1868 | +0.0650 | +0.1297 | 0.69x | 2016-08-24 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1749 | +0.0545 | +0.1148 | 0.66x | 2022-12-15 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.2020 | +0.0840 | +0.0800 | 0.40x | 2025-07-24 |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1927 | +0.1002 | +0.0897 | 0.47x | 2016-11-01 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1950 | +0.0821 | +0.1111 | 0.57x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.2219 | +0.1045 | +0.1077 | 0.49x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +0.1968 | +0.0944 | +0.0821 | 0.42x | No decay |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.2065 | +0.0956 | +0.0886 | 0.43x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1814 | +0.0513 | +0.0990 | 0.55x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | +0.1918 | +0.0863 | +0.1066 | 0.56x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.2259 | +0.0912 | +0.1134 | 0.50x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2040 | +0.0702 | +0.1253 | 0.61x | No decay |
| `combo_clamp_diff__max_up_ret__body_size_progression` | +0.1831 | +0.0853 | +0.0827 | 0.45x | 2025-06-25 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | +0.2038 | +0.0957 | +0.1078 | 0.53x | No decay |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.1609 | +0.0698 | +0.0683 | 0.42x | 2022-09-09 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1801 | +0.0527 | +0.0966 | 0.54x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1833 | +0.0722 | +0.1184 | 0.65x | No decay |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.1764 | +0.0853 | +0.0660 | 0.37x | 2020-01-06 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1723 | +0.0839 | +0.0786 | 0.46x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1691 | +0.0550 | +0.1023 | 0.61x | No decay |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.2009 | +0.0877 | +0.0941 | 0.47x | No decay |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1742 | +0.0543 | +0.1148 | 0.66x | 2022-12-15 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +0.1713 | +0.0886 | +0.0949 | 0.55x | 2020-02-12 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1966 | +0.0800 | +0.0840 | 0.43x | No decay |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | +0.1557 | +0.0429 | +0.1111 | 0.71x | 2016-08-24 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1817 | +0.0598 | +0.0802 | 0.44x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1977 | +0.1056 | +0.0842 | 0.43x | 2021-07-28 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | +0.1717 | +0.0707 | +0.1324 | 0.77x | 2016-09-26 |
| `combo_diff__max_up_ret__body_size_progression` | +0.1827 | +0.0850 | +0.0768 | 0.42x | 2025-06-25 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | +0.2080 | +0.0834 | +0.1094 | 0.53x | 2016-11-30 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1704 | +0.1253 | +0.0943 | 0.55x | 2019-12-05 |
| `rbreaker_sell_setup_proximity_early` | +0.1745 | +0.0776 | +0.1261 | 0.72x | 2021-07-28 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | +0.1516 | +0.0424 | +0.0890 | 0.59x | 2020-01-06 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1633 | +0.0764 | +0.1186 | 0.73x | 2016-09-26 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.2097 | +0.1043 | +0.0885 | 0.42x | 2016-11-30 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.2019 | +0.0740 | +0.1222 | 0.61x | No decay |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +0.1587 | +0.0556 | +0.1330 | 0.84x | 2016-09-26 |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | +0.1652 | +0.0725 | +0.1060 | 0.64x | 2021-09-28 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1968 | +0.1034 | +0.0965 | 0.49x | 2016-11-01 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | +0.1977 | +0.0764 | +0.0854 | 0.43x | 2022-12-15 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +0.1821 | +0.0610 | +0.0740 | 0.41x | 2014-06-05 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1925 | +0.0737 | +0.1091 | 0.57x | No decay |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | +0.1449 | +0.0732 | +0.0761 | 0.53x | 2020-02-12 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | +0.1962 | +0.0959 | +0.0866 | 0.44x | 2016-11-30 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1728 | +0.0834 | +0.0864 | 0.50x | 2016-12-29 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | +0.1591 | +0.0603 | +0.1289 | 0.81x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +0.1924 | +0.1023 | +0.0950 | 0.49x | 2016-11-30 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1886 | +0.0860 | +0.1174 | 0.62x | No decay |
| `combo_mean__max_up_ret__first_bar_sentiment` | +0.1901 | +0.0954 | +0.0824 | 0.43x | 2020-01-06 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | +0.1918 | +0.0974 | +0.0916 | 0.48x | 2016-11-01 |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1680 | +0.0939 | +0.0713 | 0.42x | 2016-11-01 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.2022 | +0.0847 | +0.0808 | 0.40x | 2025-07-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | +0.1841 | +0.1088 | +0.1126 | 0.61x | 2016-09-26 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1809 | +0.0798 | +0.0759 | 0.42x | 2014-06-05 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +0.1517 | +0.0593 | +0.1188 | 0.78x | 2016-11-01 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +0.1543 | +0.0490 | +0.1100 | 0.71x | 2011-09-20 |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | +0.0487 | +0.0383 | -0.0015 | -0.03x | 2010-10-15 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1995 | +0.0953 | +0.1177 | 0.59x | No decay |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1534 | +0.0538 | +0.1082 | 0.71x | 2016-09-26 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | +0.1531 | +0.0511 | +0.1136 | 0.74x | 2020-12-18 |
| `combo_mean__max_up_ret__trend_bar_close_consistency` | +0.1754 | +0.1011 | +0.0655 | 0.37x | 2016-11-01 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1897 | +0.1106 | +0.0783 | 0.41x | 2026-04-07 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | +0.1836 | +0.0723 | +0.1125 | 0.61x | No decay |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1679 | +0.0686 | +0.1227 | 0.73x | 2016-09-26 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1511 | +0.0726 | +0.1102 | 0.73x | 2016-08-24 |
| `opening_drive_thrust_ratio` | +0.1970 | +0.0973 | +0.0870 | 0.44x | No decay |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | +0.2098 | +0.0994 | +0.0811 | 0.39x | No decay |
| `combo_sig_product__max_up_ret__early_body_momentum` | +0.1834 | +0.1045 | +0.0845 | 0.46x | 2021-07-28 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | +0.1527 | +0.0894 | +0.0849 | 0.56x | 2016-11-01 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1562 | +0.0622 | +0.1081 | 0.69x | No decay |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1779 | +0.1062 | +0.0788 | 0.44x | 2020-01-06 |
| `combo_max__max_up_ret__early_body_momentum` | +0.1838 | +0.1023 | +0.0706 | 0.38x | 2016-11-01 |
| `combo_min__max_up_ret__close_vs_open_range` | +0.1713 | +0.0969 | +0.0919 | 0.54x | 2020-01-06 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1739 | +0.0881 | +0.0909 | 0.52x | No decay |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | +0.1870 | +0.0685 | +0.0915 | 0.49x | No decay |
| `combo_min__close_vs_open_range__high_low_sequence_momentum` | +0.1485 | +0.0935 | +0.0809 | 0.54x | 2016-11-01 |
| `max_up_ret` | +0.1971 | +0.0995 | +0.0778 | 0.39x | No decay |
| `combo_rank_max__max_up_ret__early_body_momentum` | +0.1877 | +0.1103 | +0.0738 | 0.39x | 2016-11-30 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1751 | +0.1287 | +0.0537 | 0.31x | 2016-12-29 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | +0.1880 | +0.1202 | +0.0723 | 0.38x | 2016-12-29 |
| `combo_mean__max_up_ret__close_vs_open_range` | +0.1839 | +0.1051 | +0.0821 | 0.45x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.2070 | +0.1118 | +0.0816 | 0.39x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1812 | +0.1052 | +0.0656 | 0.36x | 2016-12-29 |
| `combo_rank_max__bar_ret_0__max_down_ret` | +0.1754 | +0.0656 | +0.0972 | 0.55x | No decay |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +0.1524 | +0.0567 | +0.1011 | 0.66x | 2020-01-06 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | +0.1584 | +0.0998 | +0.0754 | 0.48x | 2020-01-06 |
| `combo_max__max_up_ret__close_vs_open_range` | +0.1879 | +0.1075 | +0.0764 | 0.41x | 2016-11-01 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | +0.1551 | +0.0640 | +0.1128 | 0.73x | 2014-05-06 |
| `combo_min__max_up_ret__high_low_sequence_momentum` | +0.1727 | +0.1148 | +0.0849 | 0.49x | 2020-01-06 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | +0.1783 | +0.0874 | +0.0876 | 0.49x | 2016-11-01 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | +0.1517 | +0.0495 | +0.1120 | 0.74x | 2020-12-18 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | +0.1410 | +0.0591 | +0.0861 | 0.61x | 2016-11-01 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | +0.0244 | +0.0287 | +0.0049 | 0.20x | 2010-10-15 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | +0.1325 | +0.0738 | +0.0891 | 0.67x | 2017-05-09 |
| `combo_min__close_vs_open_range__bar_ret_0` | +0.1522 | +0.0569 | +0.1017 | 0.67x | 2020-01-06 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +0.1854 | +0.0700 | +0.0938 | 0.51x | 2016-11-30 |
| `combo_mean__max_up_ret__first_bar_return` | +0.1922 | +0.0908 | +0.0779 | 0.41x | No decay |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1737 | +0.0739 | +0.0798 | 0.46x | 2022-12-15 |
| `combo_mean__volatility_expansion_trend_vector__close_vs_open_range` | +0.1526 | +0.0948 | +0.0862 | 0.56x | 2016-11-01 |
| `combo_min__net_volume_flow__bar_ret_0` | +0.1571 | +0.0874 | +0.0950 | 0.60x | 2016-11-01 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | +0.1876 | +0.1062 | +0.0737 | 0.39x | 2016-11-01 |
| `net_volume_flow` | +0.1624 | +0.0989 | +0.0847 | 0.52x | 2016-11-01 |
| `combo_rank_min__max_up_ret__bar_ret_0` | +0.1862 | +0.0688 | +0.0694 | 0.37x | No decay |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | +0.2020 | +0.0898 | +0.0892 | 0.44x | No decay |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +0.1950 | +0.0973 | +0.0648 | 0.33x | 2016-11-01 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1761 | +0.1295 | +0.0902 | 0.51x | No decay |
| `combo_min__first_bar_sentiment__bar_ret_0` | +0.1479 | +0.0591 | +0.0782 | 0.53x | 2013-09-23 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1940 | +0.1034 | +0.0859 | 0.44x | 2020-01-06 |
| `combo_max__max_up_ret__first_bar_return` | +0.1807 | +0.0821 | +0.0754 | 0.42x | No decay |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +0.1842 | +0.0817 | +0.0936 | 0.51x | 2020-01-06 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1564 | +0.0480 | +0.1143 | 0.73x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1905 | +0.0963 | +0.1128 | 0.59x | No decay |
| `combo_max__net_volume_flow__first_bar_sentiment` | +0.1619 | +0.0845 | +0.0759 | 0.47x | 2020-01-06 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1831 | +0.0886 | +0.0827 | 0.45x | No decay |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +0.1721 | +0.0890 | +0.1051 | 0.61x | 2021-05-28 |
| `combo_mean__net_volume_flow__bar_ret_0` | +0.1804 | +0.0911 | +0.0861 | 0.48x | No decay |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1683 | +0.1187 | +0.0936 | 0.56x | 2016-09-26 |
| `star50_limit_proximity_early` | +0.1480 | +0.0713 | +0.1379 | 0.93x | 2016-08-24 |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.0743 | +0.0187 | +0.0422 | 0.57x | 2011-10-26 |
| `combo_ratio__max_down_ret__net_volume_flow` | +0.1319 | -0.0332 | +0.1213 | 0.92x | 2021-02-24 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | +0.1575 | +0.0581 | +0.0850 | 0.54x | 2020-02-12 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1689 | +0.0629 | +0.0766 | 0.45x | 2016-11-30 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1954 | +0.1109 | +0.1190 | 0.61x | No decay |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | +0.1489 | +0.0586 | +0.0760 | 0.51x | 2013-09-23 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | +0.1601 | +0.0953 | +0.0885 | 0.55x | 2020-01-06 |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | +0.1552 | +0.0862 | +0.0826 | 0.53x | 2016-11-01 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1608 | +0.0987 | +0.0900 | 0.56x | 2016-11-01 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1757 | +0.0827 | +0.1102 | 0.63x | 2021-05-28 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | +0.1696 | +0.0905 | +0.1246 | 0.73x | 2016-08-24 |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | +0.1401 | -0.0210 | +0.0995 | 0.71x | 2016-11-30 |
| `combo_rank_min__bar_ret_0__max_down_ret` | +0.1484 | +0.0365 | +0.0873 | 0.59x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1819 | +0.1279 | +0.0592 | 0.33x | 2016-12-29 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | +0.1713 | +0.0646 | +0.0851 | 0.50x | 2016-12-29 |
| `combo_min__max_up_ret__bar_ret_0` | +0.1893 | +0.0813 | +0.0725 | 0.38x | No decay |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | +0.1570 | +0.0652 | +0.1480 | 0.94x | 2011-10-26 |
| `combo_min__bar_ret_0__max_down_ret` | +0.1475 | +0.0406 | +0.0943 | 0.64x | 2021-01-19 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1451 | +0.0509 | +0.1042 | 0.72x | 2014-05-06 |
| `combo_max__close_vs_open_range__bar_ret_0` | +0.1757 | +0.1058 | +0.0732 | 0.42x | No decay |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1280 | +0.0570 | +0.1298 | 1.01x | 2011-10-26 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1993 | +0.0979 | +0.0943 | 0.47x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | +0.1558 | +0.1046 | +0.0697 | 0.45x | 2016-11-01 |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | +0.1755 | +0.1057 | +0.0723 | 0.41x | No decay |
| `combo_max__close_vs_open_range__first_bar_sentiment` | +0.1525 | +0.0990 | +0.0766 | 0.50x | 2017-05-09 |
| `combo_sig_product__close_vs_open_range__high_low_sequence_momentum` | +0.1463 | +0.0903 | +0.0815 | 0.56x | 2016-11-01 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1841 | +0.1120 | +0.0915 | 0.50x | 2019-12-05 |
| `combo_rank_max__net_volume_flow__first_bar_return` | +0.1824 | +0.0891 | +0.0677 | 0.37x | No decay |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1750 | +0.0899 | +0.1094 | 0.63x | 2019-12-05 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1831 | +0.1088 | +0.1154 | 0.63x | No decay |
| `combo_max__first_bar_return__max_down_ret` | +0.1752 | +0.0646 | +0.0856 | 0.49x | 2016-11-01 |
| `combo_rank_min__close_vs_open_range__max_down_ret` | +0.1583 | +0.0739 | +0.1076 | 0.68x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1978 | +0.0928 | +0.0610 | 0.31x | 2016-11-30 |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1852 | +0.1101 | +0.0929 | 0.50x | 2019-12-05 |
| `combo_max__close_vs_open_range__early_body_momentum` | +0.1473 | +0.0915 | +0.0747 | 0.51x | 2016-11-01 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1519 | +0.0635 | +0.1702 | 1.12x | 2016-09-26 |
| `combo_mean__close_vs_open_range__bar_ret_0` | +0.1755 | +0.0868 | +0.0923 | 0.53x | No decay |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | +0.1832 | +0.0866 | +0.0912 | 0.50x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | +0.1760 | +0.0715 | +0.1034 | 0.59x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1986 | +0.1047 | +0.0801 | 0.40x | 2020-01-06 |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | +0.1406 | +0.0887 | +0.0567 | 0.40x | 2016-11-01 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1433 | +0.0895 | +0.1448 | 1.01x | 2011-12-23 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | +0.1521 | +0.1111 | +0.0607 | 0.40x | 2016-11-30 |
| `combo_min__close_vs_open_range__max_down_ret` | +0.1585 | +0.0800 | +0.1067 | 0.67x | 2016-11-01 |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | +0.1720 | +0.0948 | +0.1055 | 0.61x | 2021-05-28 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | +0.1897 | +0.0872 | +0.0994 | 0.52x | 2016-11-30 |
| `combo_max__net_volume_flow__bar_ret_0` | +0.1818 | +0.0845 | +0.0678 | 0.37x | 2020-02-12 |
| `combo_mean__net_volume_flow__max_down_ret` | +0.1702 | +0.0801 | +0.0980 | 0.58x | 2016-11-01 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.0618 | +0.0161 | +0.0339 | 0.55x | 2010-10-15 |
| `first_bar_return` | +0.1524 | +0.0604 | +0.0690 | 0.45x | 2013-09-23 |
| `combo_max__first_bar_sentiment__bar_ret_0` | +0.1466 | +0.0817 | +0.0680 | 0.46x | 2020-12-18 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +0.1320 | +0.0879 | +0.0542 | 0.41x | 2020-01-06 |
| `combo_mean__first_bar_sentiment__max_down_ret` | +0.1567 | +0.0588 | +0.1024 | 0.65x | No decay |
| `combo_clamp_diff__max_up_ret__trend_bar_close_consistency` | +0.0331 | +0.0054 | -0.0123 | -0.37x | 2010-10-15 |
| `combo_diff__max_up_ret__trend_bar_close_consistency` | +0.0331 | +0.0056 | -0.0119 | -0.36x | 2010-10-15 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | +0.1764 | +0.0864 | +0.0750 | 0.43x | 2022-11-16 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1681 | +0.0802 | +0.0785 | 0.47x | 2016-12-29 |
| `combo_rank_max__trend_bar_close_consistency__close_vs_open_range` | +0.1423 | +0.0846 | +0.0656 | 0.46x | 2016-09-26 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1682 | +0.0681 | +0.0635 | 0.38x | No decay |
| `combo_sig_product__net_volume_flow__first_bar_return` | +0.1374 | +0.0513 | +0.0508 | 0.37x | 2016-11-01 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1539 | +0.1103 | +0.0862 | 0.56x | 2016-09-26 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.1073 | +0.0351 | +0.0877 | 0.82x | 2016-08-24 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` | +0.0660 | +0.0164 | +0.0482 | 0.73x | 2010-12-14 |
| `combo_max__early_body_momentum__max_down_ret` | +0.1547 | +0.0553 | +0.0740 | 0.48x | 2016-11-01 |
| `vwap_trend_channel_slope` | +0.1524 | +0.1037 | +0.0602 | 0.39x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | +0.1861 | +0.0652 | +0.1108 | 0.60x | 2016-11-30 |
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
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1551 | +0.1271 | +0.1414 | 0.91x | 2016-10-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1683 | +0.0666 | +0.1151 | 0.68x | 2017-04-28 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1542 | +0.0924 | +0.1314 | 0.85x | 2017-02-27 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1480 | +0.0978 | +0.1412 | 0.95x | 2011-10-18 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1633 | +0.0819 | +0.1236 | 0.76x | 2017-02-27 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1489 | +0.1188 | +0.0755 | 0.51x | 2017-01-20 |
| `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0` | +0.1603 | +0.0989 | +0.1347 | 0.84x | 2017-02-27 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1525 | +0.1314 | +0.1339 | 0.88x | 2016-09-14 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | +0.1706 | +0.1073 | +0.1289 | 0.76x | 2017-02-27 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1623 | +0.0946 | +0.1287 | 0.79x | 2011-10-18 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1784 | +0.1316 | +0.1291 | 0.72x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1620 | +0.0936 | +0.1288 | 0.80x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1406 | +0.0973 | +0.1356 | 0.96x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0916 | +0.1276 | +0.1190 | 1.30x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__first_bar_sentiment` | +0.1472 | +0.0528 | +0.1256 | 0.85x | 2011-10-18 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1669 | +0.1191 | +0.1335 | 0.80x | 2017-01-20 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1115 | +0.1303 | +0.1422 | 1.28x | 2011-10-18 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | +0.1641 | +0.1112 | +0.1308 | 0.80x | 2017-01-20 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1648 | +0.1118 | +0.0930 | 0.56x | 2017-02-27 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1606 | +0.1122 | +0.0868 | 0.54x | 2017-01-20 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +0.1545 | +0.1371 | +0.1119 | 0.72x | 2016-10-24 |
| `combo_max__max_up_ret__first_bar_return` | +0.1581 | +0.1132 | +0.0848 | 0.54x | 2017-04-28 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +0.1560 | +0.1368 | +0.0865 | 0.55x | 2016-12-21 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | +0.1506 | +0.1375 | +0.1025 | 0.68x | 2016-10-24 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | +0.1603 | +0.1110 | +0.0840 | 0.52x | 2017-01-20 |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | +0.1452 | +0.0640 | +0.1177 | 0.81x | 2011-10-18 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1029 | +0.0965 | +0.1311 | 1.27x | 2011-10-18 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=+0.0624). Consider relaxing this gate.
2. **300ETF `single` — B4 Correlation Gate too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=+0.1518). Consider relaxing this gate.
3. **300ETF `short` — BH-FDR Gate too strict**: 42.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.0755). Consider relaxing this gate.
4. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=+0.0201). Consider relaxing this gate.
5. **50ETF `single` — B2 Rolling Guard too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=+0.0032). Consider relaxing this gate.
6. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=-0.0535). Consider relaxing this gate.
7. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 76.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 49.0%, mean lock Sharpe=+0.2436). Consider relaxing this gate.
8. **500ETF `single` — B4 Correlation Gate too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 49.0%, mean lock Sharpe=+0.6299). Consider relaxing this gate.
9. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 83.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 36.0%, mean lock Sharpe=+0.0635). Consider relaxing this gate.
10. **500ETF `long` — BH-FDR Gate too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 36.0%, mean lock Sharpe=-0.0784). Consider relaxing this gate.
11. **500ETF `short` — BH-FDR Gate too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.1586). Consider relaxing this gate.
12. **588000ETF `single` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=+0.2329). Consider relaxing this gate.
13. **588000ETF `single` — B2 Rolling Guard too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.3049). Consider relaxing this gate.
14. **588000ETF `single` — Admission too loose**: 67% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
15. **588000ETF `short` — B3 Composite Floor too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.3303). Consider relaxing this gate.
16. **159915ETF `single` — B2 Rolling Guard too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 63.0%, mean lock Sharpe=+0.9996). Consider relaxing this gate.
17. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 63.0%, mean lock Sharpe=+1.1607). Consider relaxing this gate.
18. **159915ETF `single` — B4 Correlation Gate too strict**: 95.5% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 63.0%, mean lock Sharpe=+0.7336). Consider relaxing this gate.
19. **159915ETF `long` — B2 Rolling Guard too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 45.0%, mean lock Sharpe=+0.6465). Consider relaxing this gate.
20. **159915ETF `long` — BH-FDR Gate too strict**: 70.8% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 45.0%, mean lock Sharpe=+0.4274). Consider relaxing this gate.
21. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.3800). Consider relaxing this gate.
22. **159915ETF `short` — B2 Rolling Guard too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.2081). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
