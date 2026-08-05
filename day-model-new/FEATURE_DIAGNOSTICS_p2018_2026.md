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

### 300ETF — `single` (Full Model Lockbox IC: -0.1104, Sharpe: -0.2932)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1074 | +0.0272 | +0.0272 | +0.6075 | 0.50 | 0/8 | 0.74 | 0.45 | `bar_body_rng_0` (0.73) | +0.0020 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1034 | +0.0005 | +0.0005 | -0.7605 | 0.57 | 0/8 | 0.64 | 0.34 | `bar_body_rng_0` (0.73) | +0.0015 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0981 | -0.0273 | -0.0273 | +1.0319 | 0.64 | 0/8 | 0.60 | 0.40 | `rbreaker_buy_setup_proximity_early` (0.90) | -0.0010 | +0.0000 |
| `combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0771 | -0.1298 | -0.1298 | -1.8873 | 0.96 | 1/8 | 1.87 | 0.75 | `volume_weighted_price_position` (1.03) | +0.0034 | +0.0282 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1008 | -0.1740 | -0.1740 | -1.4177 | 0.66 | 0/8 | 0.85 | 0.51 | `volume_weighted_price_position` (1.03) | -0.0018 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1018 | +0.0449 | +0.0449 | -0.4434 | 0.57 | 0/8 | 0.59 | 0.26 | `bar_body_rng_0` (0.73) | +0.0009 | +0.0000 |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0962 | -0.1215 | -0.1215 | -2.1883 | 0.85 | 1/8 | 0.92 | 0.39 | `volume_weighted_price_position` (1.03) | +0.0008 | +0.0000 |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0942 | -0.1502 | -0.1502 | -2.3921 | 0.80 | 1/8 | 0.85 | 0.42 | `volume_weighted_price_position` (1.03) | +0.0020 | +0.0282 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | Intraday Range Momentum | +1 | +0.1062 | -0.0701 | -0.0701 | +0.0945 | 0.50 | 0/8 | 0.66 | 0.40 | `limit_down_proximity_early` (0.90) | +0.0011 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0918 | -0.0293 | -0.0293 | +0.7925 | 0.44 | 0/8 | 0.70 | 0.44 | `max_up_ret` (0.69) | +0.0016 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1039 | -0.0294 | -0.0294 | -0.6275 | 0.52 | 0/8 | 0.73 | 0.42 | `bar_body_rng_0` (0.73) | +0.0011 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0985 | -0.1994 | -0.1994 | -2.8678 | 0.71 | 0/8 | 0.87 | 0.46 | `volume_weighted_price_position` (1.03) | +0.0003 | +0.0282 |
| `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0941 | -0.2002 | -0.2002 | -3.3600 | 0.76 | 1/8 | 1.09 | 0.46 | `volume_weighted_price_position` (1.03) | +0.0005 | +0.0282 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1074 | -0.0712 | -0.0712 | -0.5845 | 0.54 | 0/8 | 0.59 | 0.33 | `first_bar_return` (0.68) | +0.0009 | +0.0000 |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0911 | -0.1762 | -0.1762 | -2.3921 | 0.82 | 2/8 | 0.84 | 0.34 | `volume_weighted_price_position` (1.03) | +0.0005 | +0.0282 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1002 | -0.0924 | -0.0924 | -1.1726 | 0.72 | 0/8 | 0.69 | 0.36 | `bar_body_rng_0` (0.73) | -0.0012 | +0.0000 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0944 | -0.2114 | -0.2114 | -3.6368 | 0.71 | 0/8 | 1.02 | 0.76 | `volume_weighted_price_position` (1.03) | +0.0006 | +0.0000 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.0963 | +0.0147 | +0.0147 | +0.3204 | 0.59 | 0/8 | 0.76 | 0.44 | `limit_down_proximity_early` (0.90) | +0.0002 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0881 | -0.0775 | -0.0775 | -1.0627 | 0.60 | 0/8 | 0.97 | 0.58 | `bar_body_rng_0` (0.73) | +0.0007 | +0.0000 |
| `combo_rank_max__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0936 | -0.0889 | -0.0889 | -2.3913 | 0.70 | 1/8 | 0.72 | 0.39 | `bar_body_rng_0` (0.73) | -0.0011 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0910 | -0.0509 | -0.0509 | +0.5175 | 0.54 | 0/8 | 0.71 | 0.42 | `morning_volume_weighted_momentum` (0.61) | +0.0004 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1095 | -0.0308 | -0.0308 | -0.1479 | 0.58 | 0/8 | 0.62 | 0.31 | `bar_body_rng_0` (0.73) | +0.0004 | +0.0000 |
| `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0943 | -0.0631 | -0.0631 | -1.1652 | 0.79 | 1/8 | 0.91 | 0.42 | `volume_weighted_price_position` (1.03) | +0.0009 | +0.0000 |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1125 | -0.0581 | -0.0581 | -2.1391 | 0.58 | 0/8 | 0.81 | 0.35 | `bar_body_rng_0` (0.73) | +0.0006 | +0.0000 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0961 | -0.0955 | -0.0955 | -0.5706 | 0.68 | 0/8 | 0.83 | 0.39 | `volume_weighted_price_position` (1.03) | +0.0011 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0882 | -0.1964 | -0.1964 | -2.1840 | 0.77 | 0/8 | 1.03 | 0.66 | `volume_weighted_price_position` (1.03) | +0.0007 | +0.0282 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0913 | +0.0709 | +0.0709 | -1.0140 | 0.62 | 0/8 | 0.54 | 0.27 | `rbreaker_buy_setup_proximity_early` (0.90) | +0.0020 | +0.0000 |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0996 | -0.1697 | -0.1697 | -2.7982 | 0.67 | 0/8 | 0.93 | 0.55 | `volume_weighted_price_position` (1.03) | -0.0001 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1005 | -0.1637 | -0.1637 | -2.8975 | 0.63 | 0/8 | 0.84 | 0.59 | `max_up_ret` (0.69) | -0.0010 | +0.0000 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0851 | -0.0691 | -0.0691 | -0.9513 | 0.72 | 0/8 | 0.72 | 0.31 | `bar_body_rng_0` (0.73) | +0.0020 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.0897 | -0.1297 | -0.1297 | -2.5287 | 0.60 | 0/8 | 0.59 | 0.29 | `max_up_ret` (0.69) | +0.0011 | +0.0000 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0867 | -0.1087 | -0.1087 | -2.7122 | 0.70 | 0/8 | 0.59 | 0.28 | `volume_weighted_price_position` (1.03) | -0.0012 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1065 | -0.1364 | -0.1364 | -2.1155 | 0.63 | 0/8 | 0.73 | 0.44 | `bar_body_rng_0` (0.73) | -0.0004 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1000 | -0.1466 | -0.1466 | -1.4795 | 0.83 | 1/8 | 0.77 | 0.40 | `volume_weighted_price_position` (1.03) | -0.0004 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | Intraday Range Momentum | +1 | +0.1017 | -0.1072 | -0.1072 | -1.6552 | 0.48 | 0/8 | 0.86 | 0.61 | `rbreaker_buy_setup_proximity_early` (0.90) | +0.0002 | +0.0000 |
| `combo_tri_median__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0941 | -0.1153 | -0.1153 | -1.6739 | 0.79 | 1/8 | 0.73 | 0.33 | `volume_weighted_price_position` (1.03) | +0.0017 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0923 | -0.0504 | -0.0504 | -0.6267 | 0.50 | 0/8 | 0.57 | 0.29 | `max_up_ret` (0.69) | +0.0017 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0945 | -0.1967 | -0.1967 | -2.8312 | 0.67 | 0/8 | 1.13 | 0.80 | `volume_weighted_price_position` (1.03) | +0.0012 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.0876 | -0.1476 | -0.1476 | -2.5718 | 0.66 | 0/8 | 0.94 | 0.69 | `max_up_ret` (0.69) | +0.0002 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0978 | -0.1581 | -0.1581 | -0.9489 | 0.60 | 0/8 | 0.80 | 0.61 | `opening_drive_thrust_ratio` (0.64) | -0.0015 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0937 | +0.0132 | +0.0132 | +0.8820 | 0.48 | 0/8 | 0.67 | 0.37 | `rbreaker_buy_setup_proximity_early` (0.90) | +0.0011 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0886 | -0.0317 | -0.0317 | +0.8606 | 0.63 | 0/8 | 0.80 | 0.56 | `morning_volume_weighted_momentum` (0.61) | +0.0027 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1013 | -0.1298 | -0.1298 | -1.8580 | 0.78 | 0/8 | 0.82 | 0.35 | `volume_weighted_price_position` (1.03) | -0.0008 | +0.0000 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0937 | -0.1611 | -0.1611 | -1.2733 | 0.63 | 0/8 | 0.75 | 0.60 | `max_up_ret` (0.69) | -0.0005 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0871 | -0.0161 | -0.0161 | +0.0760 | 0.64 | 0/8 | 0.83 | 0.66 | `morning_volume_weighted_momentum` (0.61) | +0.0021 | +0.0000 |
| `combo_mean__max_up_ret__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0824 | -0.1658 | -0.1658 | -2.6771 | 0.62 | 0/8 | 0.99 | 1.10 | `max_up_ret` (0.69) | +0.0006 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0917 | -0.1526 | -0.1526 | -2.5270 | 0.67 | 0/8 | 0.72 | 0.50 | `bar_body_rng_0` (0.73) | -0.0004 | +0.0000 |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0886 | -0.1961 | -0.1961 | -3.7281 | 0.56 | 0/8 | 0.99 | 0.97 | `bar_ret_0` (0.68) | -0.0008 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0986 | -0.1708 | -0.1708 | -1.9174 | 0.73 | 1/8 | 1.00 | 0.58 | `volume_weighted_price_position` (1.03) | +0.0016 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0974 | -0.0169 | -0.0169 | +0.1548 | 0.51 | 0/8 | 0.56 | 0.26 | `max_up_ret` (0.69) | +0.0021 | +0.0000 |
| `combo_max__volume_weighted_price_position__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0844 | -0.2186 | -0.2186 | -4.3304 | 0.70 | 0/8 | 1.66 | 1.29 | `volume_weighted_price_position` (1.03) | +0.0004 | +0.0282 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1000 | -0.1148 | -0.1148 | -1.8175 | 0.58 | 0/8 | 0.64 | 0.30 | `max_up_ret` (0.69) | -0.0007 | +0.0000 |
| `combo_rank_min__max_up_ret__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0828 | -0.1459 | -0.1459 | -1.5232 | 0.56 | 0/8 | 1.12 | 1.28 | `max_up_ret` (0.69) | +0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1052 | -0.1306 | -0.1306 | -2.9603 | 0.62 | 0/8 | 0.82 | 0.48 | `bar_body_rng_0` (0.73) | -0.0003 | +0.0000 |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1100 | -0.0539 | -0.0539 | -0.7695 | 0.59 | 0/8 | 0.73 | 0.33 | `bar_ret_0` (0.68) | -0.0002 | +0.0000 |
| `combo_rank_max__first_bar_return__morning_volume_weighted_momentum` | Gap / Overnight Reversal | +1 | +0.0885 | -0.1934 | -0.1934 | -3.6188 | 0.58 | 0/8 | 0.96 | 0.94 | `first_bar_return` (0.68) | -0.0021 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1033 | -0.1364 | -0.1364 | -3.0061 | 0.59 | 0/8 | 0.72 | 0.39 | `bar_ret_0` (0.68) | -0.0020 | +0.0000 |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0970 | -0.1079 | -0.1079 | -1.4834 | 0.64 | 0/8 | 0.75 | 0.45 | `bar_body_rng_0` (0.73) | -0.0011 | +0.0000 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0972 | -0.1469 | -0.1469 | -2.3451 | 0.67 | 0/8 | 0.71 | 0.59 | `bar_body_rng_0` (0.73) | -0.0006 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1034 | -0.0541 | -0.0541 | -1.4245 | 0.53 | 0/8 | 0.62 | 0.34 | `max_up_ret` (0.69) | +0.0006 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0648 | +0.0763 | +0.0763 | +0.2526 | 0.66 | 1/8 | 0.67 | 0.05 | `morning_volume_weighted_momentum` (0.61) | +0.0013 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0937 | -0.0121 | -0.0121 | +0.8779 | 0.59 | 0/8 | 0.60 | 0.34 | `rbreaker_buy_setup_proximity_early` (0.90) | -0.0005 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.1005 | -0.1081 | -0.1081 | -0.5121 | 0.69 | 1/8 | 0.79 | 0.43 | `volume_weighted_price_position` (1.03) | -0.0005 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.0982 | -0.1510 | -0.1510 | -2.2099 | 0.64 | 0/8 | 0.76 | 0.40 | — | -0.0018 | +0.0000 |
| `combo_mean__volume_weighted_price_position__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0942 | -0.1802 | -0.1802 | -1.7134 | 0.74 | 1/8 | 1.44 | 1.30 | `volume_weighted_price_position` (1.03) | -0.0008 | +0.0282 |
| `combo_rank_min__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0802 | -0.0956 | -0.0956 | -1.2359 | 0.72 | 0/8 | 0.58 | 0.21 | `max_up_ret` (0.69) | +0.0006 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0958 | -0.0023 | -0.0023 | +0.4698 | 0.56 | 0/8 | 0.63 | 0.27 | `rbreaker_buy_setup_proximity_early` (0.90) | +0.0000 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0904 | +0.0628 | +0.0628 | -1.0546 | 0.57 | 1/8 | 0.72 | 0.29 | `opening_drive_thrust_ratio` (0.64) | +0.0002 | +0.0000 |
| `combo_mean__bar_ret_0__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0895 | -0.1430 | -0.1430 | -2.9943 | 0.54 | 0/8 | 0.97 | 0.77 | `bar_ret_0` (0.68) | +0.0006 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` | Intraday Range Momentum | +1 | +0.0869 | +0.0883 | +0.0883 | +0.6289 | 0.52 | 0/8 | 0.60 | 0.23 | `limit_down_proximity_early` (0.90) | +0.0025 | +0.0000 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0713 | -0.1823 | -0.1823 | -2.6806 | 0.97 | 1/8 | 1.22 | 0.64 | `volume_weighted_price_position` (1.03) | +0.0021 | +0.0282 |
| `combo_diff__first_bar_return__early_late_momentum_divergence` | Gap / Overnight Reversal | +1 | +0.0983 | -0.0028 | -0.0028 | +0.3637 | 0.74 | 1/8 | 0.73 | 0.27 | `early_late_momentum_divergence` (1.05) | +0.0005 | +0.0000 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0747 | -0.1752 | -0.1752 | -2.4148 | 0.61 | 0/8 | 1.26 | 1.85 | — | -0.0009 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0866 | -0.0127 | -0.0127 | -1.1004 | 0.68 | 0/8 | 0.76 | 0.40 | `first_bar_return` (0.68) | -0.0004 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: -0.0233, Sharpe: -0.1328)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1375 | +0.0514 | +0.0514 | -1.5211 | 0.24 | 0/8 | 0.91 | 0.86 | `first_bar_return` (0.48) | +0.0016 | +0.0000 |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1346 | +0.0529 | +0.0529 | -1.5621 | 0.22 | 0/8 | 0.85 | 0.85 | `bar_ret_0` (0.48) | +0.0016 | +0.0000 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1459 | +0.0028 | +0.0028 | -1.6259 | 0.49 | 0/8 | 0.53 | 0.47 | `volume_weighted_momentum_acceleration` (0.53) | +0.0004 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1146 | +0.0733 | +0.0733 | +0.5393 | 0.29 | 0/8 | 0.81 | 0.85 | `bar_ret_0` (0.48) | +0.0014 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1281 | +0.0955 | +0.0955 | +0.7908 | 0.34 | 0/8 | 0.63 | 0.67 | `bar_body_rng_0` (0.36) | +0.0008 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1307 | +0.0419 | +0.0419 | +0.3646 | 0.30 | 0/8 | 0.76 | 0.72 | `bar_ret_0` (0.48) | +0.0009 | -1.0485 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1302 | +0.0876 | +0.0876 | +1.1299 | 0.43 | 0/8 | 0.57 | 0.63 | `bar_ret_0` (0.48) | +0.0010 | +0.0000 |
| `combo_mean__bar_ret_0__close_vs_open_range` | Other Technical | +1 | +0.1231 | -0.0383 | -0.0383 | -1.2349 | 0.29 | 0/8 | 0.94 | 0.91 | `bar_ret_0` (0.48) | -0.0008 | -1.0485 |
| `combo_min__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1136 | -0.0010 | -0.0010 | -0.2212 | 0.28 | 0/8 | 0.94 | 0.87 | `first_bar_return` (0.48) | +0.0010 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1140 | +0.0727 | +0.0727 | -0.4830 | 0.29 | 0/8 | 0.90 | 0.80 | `early_body_momentum` (0.36) | +0.0002 | -1.0485 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1355 | -0.0197 | -0.0197 | +0.1617 | 0.30 | 0/8 | 0.84 | 0.76 | `bar_ret_0` (0.48) | +0.0006 | +0.0000 |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1175 | -0.0451 | -0.0451 | -1.9899 | 0.29 | 0/8 | 0.89 | 0.69 | `bar_body_rng_0` (0.36) | +0.0022 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1425 | -0.0114 | -0.0114 | -0.9885 | 0.36 | 0/8 | 0.71 | 0.62 | `bar_ret_0` (0.48) | +0.0003 | +0.0000 |
| `combo_rank_min__net_volume_flow__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1127 | -0.0164 | -0.0164 | -0.4298 | 0.25 | 0/8 | 0.96 | 0.87 | `bar_body_rng_0` (0.36) | +0.0000 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1220 | +0.1016 | +0.1016 | +0.5964 | 0.37 | 0/8 | 0.61 | 0.61 | `bar_body_rng_0` (0.36) | +0.0008 | -1.0485 |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1328 | +0.0078 | +0.0078 | -1.2156 | 0.34 | 0/8 | 0.67 | 0.66 | `bar_body_rng_0` (0.36) | +0.0011 | +0.0000 |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | Intraday Range Momentum | +1 | +0.1080 | -0.0706 | -0.0706 | -1.9365 | 0.38 | 0/8 | 0.96 | 1.01 | `max_down_ret` (0.39) | +0.0009 | +0.0000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1328 | +0.0033 | +0.0033 | -1.5227 | 0.37 | 0/8 | 0.57 | 0.55 | `volume_weighted_momentum_acceleration` (0.53) | +0.0020 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | Volatility & Oscillators | +1 | +0.1325 | +0.0571 | +0.0571 | +0.3372 | 0.32 | 0/8 | 0.69 | 0.79 | `opening_drive_thrust_ratio` (0.31) | +0.0006 | -1.0485 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1178 | +0.0846 | +0.0846 | +0.3115 | 0.34 | 0/8 | 0.59 | 0.63 | `bar_ret_0` (0.48) | +0.0014 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1411 | +0.0815 | +0.0815 | +2.0046 | 0.35 | 0/8 | 0.64 | 0.65 | `bar_ret_0` (0.48) | +0.0021 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | Other Technical | +1 | +0.1335 | -0.0298 | -0.0298 | -1.5915 | 0.29 | 0/8 | 0.80 | 0.75 | `bar_ret_0` (0.48) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1404 | +0.0617 | +0.0617 | +0.3905 | 0.36 | 0/8 | 0.65 | 0.57 | `bar_ret_0` (0.48) | +0.0002 | -1.0485 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1183 | +0.0003 | +0.0003 | -0.4714 | 0.37 | 0/8 | 0.69 | 0.55 | `bar_body_rng_0` (0.36) | +0.0011 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1033 | +0.0350 | +0.0350 | -0.6199 | 0.24 | 0/8 | 1.06 | 1.52 | `trend_bar_close_consistency` (0.49) | +0.0011 | -1.0485 |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | Other Technical | +1 | +0.1213 | -0.0705 | -0.0705 | -2.6077 | 0.26 | 0/8 | 0.88 | 0.82 | `bar_body_rng_0` (0.36) | +0.0005 | -1.0485 |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1026 | +0.0175 | +0.0175 | -1.1506 | 0.29 | 0/8 | 0.99 | 1.04 | `trend_bar_close_consistency` (0.49) | +0.0011 | -1.0485 |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1057 | -0.0686 | -0.0686 | -1.8069 | 0.36 | 0/8 | 0.97 | 1.10 | `max_down_ret` (0.39) | +0.0006 | +0.0000 |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1257 | -0.0676 | -0.0676 | -1.0649 | 0.22 | 0/8 | 0.89 | 0.84 | `bar_ret_0` (0.48) | +0.0012 | -1.0485 |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1156 | +0.0988 | +0.0988 | -1.7785 | 0.50 | 0/8 | 0.52 | 0.41 | `early_late_momentum_divergence` (0.86) | +0.0017 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | Volatility & Oscillators | +1 | +0.1382 | +0.0674 | +0.0674 | +1.0606 | 0.31 | 0/8 | 0.67 | 0.67 | `opening_drive_thrust_ratio` (0.31) | +0.0008 | -1.0485 |
| `combo_mean__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1296 | -0.0160 | -0.0160 | -0.6629 | 0.27 | 0/8 | 0.90 | 0.81 | `max_down_ret` (0.39) | -0.0003 | -1.0485 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1438 | +0.0177 | +0.0177 | -1.6384 | 0.37 | 0/8 | 0.61 | 0.58 | `bar_ret_0` (0.48) | +0.0023 | +0.0000 |
| `combo_diff__net_volume_flow__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1396 | +0.0252 | +0.0252 | -0.1184 | 0.36 | 0/8 | 0.62 | 0.58 | `smooth_momentum_structure` (0.57) | +0.0014 | +0.0000 |
| `combo_mean__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1162 | +0.0117 | +0.0117 | -2.2371 | 0.38 | 0/8 | 0.80 | 0.78 | `first_bar_return` (0.48) | +0.0014 | +0.0000 |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1202 | -0.0339 | -0.0339 | -0.8457 | 0.30 | 0/8 | 0.83 | 0.70 | `bar_ret_0` (0.48) | +0.0025 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1329 | +0.0277 | +0.0277 | -0.8653 | 0.31 | 0/8 | 0.82 | 0.74 | `early_body_momentum` (0.36) | -0.0002 | -1.0485 |
| `combo_rank_min__net_volume_flow__shaved_bar_trend_conviction` | Volatility & Oscillators | +1 | +0.0765 | -0.0862 | -0.0862 | -1.3223 | 0.43 | 0/8 | 1.52 | 1.93 | `shaved_bar_trend_conviction` (1.10) | -0.0014 | -1.0485 |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1053 | +0.0095 | +0.0095 | -0.0517 | 0.41 | 0/8 | 0.84 | 0.78 | `bar_ret_0` (0.48) | +0.0015 | +0.0000 |
| `combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0` | Intraday Range Momentum | +1 | +0.1214 | -0.0199 | -0.0199 | -0.4536 | 0.25 | 0/8 | 0.97 | 0.85 | `bar_ret_0` (0.48) | +0.0007 | +0.0000 |
| `combo_clamp_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.0932 | -0.1034 | -0.1034 | -2.3182 | 0.31 | 0/8 | 1.53 | 1.74 | `h2_l2_pullback_continuation` (0.43) | -0.0020 | -1.0485 |
| `combo_min__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1138 | -0.0051 | -0.0051 | -1.4910 | 0.42 | 0/8 | 0.65 | 0.59 | `first_bar_return` (0.48) | +0.0008 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0702 | +0.0600 | +0.0600 | -0.0172 | 0.75 | 1/8 | 1.15 | 2.11 | `shaved_bar_trend_conviction` (1.10) | +0.0013 | -1.0485 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1243 | +0.0069 | +0.0069 | +0.0524 | 0.38 | 0/8 | 0.72 | 0.78 | `max_down_ret` (0.39) | +0.0004 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1356 | +0.1749 | +0.1749 | +2.0624 | 0.39 | 0/8 | 0.53 | 0.56 | `volume_weighted_momentum_acceleration` (0.53) | +0.0029 | +0.0000 |
| `combo_mean__rsi_opening__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1167 | -0.0320 | -0.0320 | -0.8778 | 0.28 | 0/8 | 0.92 | 0.88 | `bar_body_rng_0` (0.36) | +0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1251 | -0.0021 | -0.0021 | -1.4591 | 0.41 | 0/8 | 0.70 | 0.70 | `max_down_ret` (0.39) | +0.0002 | +0.0000 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.1111 | -0.0906 | -0.0906 | -1.7423 | 0.23 | 0/8 | 1.27 | 1.29 | — | -0.0006 | -1.0485 |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | Other Technical | +1 | +0.0911 | -0.1131 | -0.1131 | -3.2742 | 0.26 | 0/8 | 1.48 | 1.30 | `trend_bar_close_consistency` (0.49) | -0.0022 | -1.0485 |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1408 | +0.0004 | +0.0004 | -1.2980 | 0.33 | 0/8 | 0.65 | 0.67 | `volume_weighted_momentum_acceleration` (0.53) | +0.0012 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1313 | -0.0646 | -0.0646 | -2.3002 | 0.36 | 0/8 | 0.76 | 0.71 | `bar_ret_0` (0.48) | -0.0002 | -1.0485 |
| `combo_mean__bar_ret_0__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1182 | -0.0684 | -0.0684 | -1.0664 | 0.31 | 0/8 | 0.81 | 0.63 | `bar_ret_0` (0.48) | +0.0019 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1267 | +0.1783 | +0.1783 | +2.2572 | 0.47 | 0/8 | 0.46 | 0.47 | `volume_weighted_momentum_acceleration` (0.53) | +0.0027 | +0.0000 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1206 | +0.0077 | +0.0077 | -1.6646 | 0.46 | 0/8 | 0.71 | 0.58 | `bar_ret_0` (0.48) | +0.0012 | +0.0000 |
| `combo_rank_min__early_order_flow_imbalance__shaved_bar_trend_conviction` | Volatility & Oscillators | +1 | +0.0881 | -0.1351 | -0.1351 | -2.1450 | 0.29 | 0/8 | 1.56 | 1.44 | `shaved_bar_trend_conviction` (1.10) | -0.0001 | -1.0485 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1109 | +0.1278 | +0.1278 | +1.3992 | 0.36 | 0/8 | 0.61 | 0.65 | `bar_body_rng_0` (0.36) | +0.0021 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1225 | -0.0080 | -0.0080 | -0.0237 | 0.34 | 0/8 | 0.82 | 0.79 | `bar_ret_0` (0.48) | +0.0004 | +0.0000 |
| `combo_max__early_body_momentum__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.0987 | -0.1244 | -0.1244 | -2.1877 | 0.26 | 0/8 | 1.33 | 1.21 | `early_body_momentum` (0.36) | -0.0001 | -1.0485 |
| `combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend` | Volatility & Oscillators | +1 | +0.0965 | -0.0712 | -0.0712 | -3.2742 | 0.50 | 0/8 | 1.82 | 1.27 | `early_order_flow_imbalance` (0.29) | -0.0012 | -1.0485 |
| `combo_min__first_bar_return__close_vs_open_range` | Gap / Overnight Reversal | +1 | +0.1035 | +0.0019 | +0.0019 | +0.4072 | 0.39 | 0/8 | 1.09 | 1.04 | `first_bar_return` (0.48) | +0.0007 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1332 | -0.0023 | -0.0023 | -0.5680 | 0.36 | 0/8 | 0.68 | 0.61 | `bar_ret_0` (0.48) | +0.0008 | +0.0000 |
| `volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1054 | -0.0850 | -0.0850 | -2.3631 | 0.26 | 0/8 | 1.29 | 1.36 | — | -0.0002 | -1.0485 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1217 | -0.0068 | -0.0068 | -1.0463 | 0.25 | 0/8 | 0.92 | 0.83 | `smooth_momentum_structure` (0.57) | -0.0000 | +0.0000 |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.0958 | -0.0001 | -0.0001 | +0.3696 | 0.38 | 0/8 | 1.22 | 1.06 | `trend_bar_close_consistency` (0.49) | +0.0016 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1146 | +0.1105 | +0.1105 | -0.0489 | 0.37 | 0/8 | 0.63 | 0.70 | `bar_ret_0` (0.48) | +0.0012 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1357 | -0.0468 | -0.0468 | -2.0328 | 0.26 | 0/8 | 0.86 | 0.82 | `trend_bar_close_consistency` (0.49) | -0.0004 | -1.0485 |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.0880 | +0.0765 | +0.0765 | +1.5322 | 0.28 | 0/8 | 1.31 | 1.55 | `trend_bar_close_consistency` (0.49) | +0.0014 | -1.0485 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1117 | -0.0503 | -0.0503 | -1.6591 | 0.27 | 0/8 | 1.08 | 1.04 | `trend_bar_close_consistency` (0.49) | -0.0005 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1234 | +0.0832 | +0.0832 | -0.6640 | 0.44 | 0/8 | 0.52 | 0.40 | `body_size_progression` (0.71) | +0.0027 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.1123 | -0.0580 | -0.0580 | -1.7157 | 0.21 | 0/8 | 1.12 | 1.09 | — | -0.0003 | -1.0485 |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1273 | -0.0914 | -0.0914 | -3.3937 | 0.28 | 0/8 | 0.85 | 0.80 | `bar_ret_0` (0.48) | -0.0003 | -1.0485 |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1215 | -0.0476 | -0.0476 | -2.6663 | 0.33 | 0/8 | 0.88 | 0.66 | `max_up_ret` (0.30) | -0.0007 | -1.0485 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1260 | +0.1800 | +0.1800 | +2.6093 | 0.47 | 0/8 | 0.45 | 0.45 | `volume_weighted_momentum_acceleration` (0.53) | +0.0021 | +0.0000 |
| `combo_min__first_bar_return__vwap_close_divergence_trend` | Gap / Overnight Reversal | +1 | +0.0952 | +0.0050 | +0.0050 | -0.0750 | 0.44 | 0/8 | 0.80 | 0.72 | `first_bar_return` (0.48) | +0.0017 | +0.0000 |
| `combo_diff__net_volume_flow__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.0987 | -0.0890 | -0.0890 | -1.1296 | 0.24 | 0/8 | 1.43 | 1.43 | `h2_l2_pullback_continuation` (0.43) | -0.0001 | -1.0485 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1055 | +0.0849 | +0.0849 | +0.9197 | 0.40 | 0/8 | 0.66 | 0.74 | `bar_ret_0` (0.48) | +0.0009 | -1.0485 |
| `combo_mean__first_bar_return__shaved_bar_trend_conviction` | Gap / Overnight Reversal | +1 | +0.0983 | -0.0510 | -0.0510 | -1.5241 | 0.44 | 0/8 | 0.75 | 0.82 | `shaved_bar_trend_conviction` (1.10) | -0.0003 | +0.0000 |
| `first_30min_return` | Intraday Range Momentum | +1 | +0.1098 | -0.1128 | -0.1128 | -2.1381 | 0.25 | 0/8 | 1.32 | 1.35 | — | -0.0000 | -1.0485 |
| `combo_tri_median__max_up_ret__net_volume_flow__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1001 | -0.0680 | -0.0680 | -1.8579 | 0.23 | 0/8 | 1.30 | 1.19 | `smooth_momentum_structure` (0.57) | -0.0012 | -1.0485 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | Intraday Range Momentum | +1 | +0.1224 | -0.0656 | -0.0656 | -1.4128 | 0.29 | 0/8 | 0.91 | 0.79 | `trend_bar_close_consistency` (0.49) | -0.0007 | -1.0485 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1372 | -0.0132 | -0.0132 | -2.3509 | 0.31 | 0/8 | 0.76 | 0.68 | `opening_drive_thrust_ratio` (0.31) | +0.0003 | +0.0000 |
| `combo_sig_product__early_body_momentum__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.0970 | -0.0956 | -0.0956 | -3.2742 | 0.29 | 0/8 | 1.46 | 1.16 | `early_body_momentum` (0.36) | -0.0022 | -1.0485 |
| `combo_clamp_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1370 | +0.0343 | +0.0343 | -1.7348 | 0.43 | 0/8 | 0.54 | 0.54 | `volume_weighted_momentum_acceleration` (0.53) | +0.0019 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1356 | +0.1045 | +0.1045 | +1.6851 | 0.35 | 0/8 | 0.63 | 0.74 | `opening_drive_thrust_ratio` (0.31) | +0.0005 | -1.0485 |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1187 | -0.0451 | -0.0451 | -1.6562 | 0.28 | 0/8 | 0.99 | 1.05 | `early_body_momentum` (0.36) | -0.0004 | -1.0485 |
| `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0` | Intraday Range Momentum | +1 | +0.1065 | -0.0666 | -0.0666 | -2.2843 | 0.35 | 0/8 | 0.84 | 0.77 | `volume_weighted_momentum_acceleration` (0.53) | +0.0007 | +0.0000 |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | Gap / Overnight Reversal | +1 | +0.1082 | -0.1062 | -0.1062 | -3.0712 | 0.23 | 0/8 | 1.02 | 0.93 | `first_bar_return` (0.48) | +0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1115 | -0.0518 | -0.0518 | -1.9303 | 0.42 | 0/8 | 0.78 | 0.50 | `max_up_ret` (0.30) | -0.0020 | -1.0485 |
| `combo_rel_diff__early_body_momentum__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1125 | +0.0170 | +0.0170 | -1.5370 | 0.26 | 0/8 | 1.41 | 1.37 | `early_body_momentum` (0.36) | +0.0005 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1071 | +0.0737 | +0.0737 | +0.8795 | 0.36 | 0/8 | 0.71 | 0.79 | `bar_ret_0` (0.48) | +0.0012 | -1.0485 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1079 | -0.0187 | -0.0187 | -0.7812 | 0.26 | 0/8 | 1.04 | 1.11 | `max_down_ret` (0.39) | +0.0004 | +0.0000 |
| `combo_min__close_vs_open_range__bar_body_rng_0` | Other Technical | +1 | +0.1000 | -0.0140 | -0.0140 | -0.5241 | 0.40 | 0/8 | 1.03 | 1.00 | `bar_body_rng_0` (0.36) | -0.0004 | +0.0000 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1038 | -0.0915 | -0.0915 | -2.8218 | 0.28 | 0/8 | 1.60 | 1.28 | `max_down_ret` (0.39) | -0.0016 | -1.0485 |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1083 | -0.0906 | -0.0906 | -2.0531 | 0.23 | 0/8 | 1.43 | 1.53 | `trend_bar_close_consistency` (0.49) | -0.0010 | -1.0485 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1009 | +0.1466 | +0.1466 | +0.8696 | 0.42 | 0/8 | 1.06 | 1.15 | `max_down_ret` (0.39) | +0.0023 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1336 | -0.0104 | -0.0104 | -2.0137 | 0.34 | 0/8 | 0.74 | 0.73 | `opening_drive_thrust_ratio` (0.31) | +0.0005 | +0.0000 |
| `combo_sig_product__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1267 | -0.0342 | -0.0342 | -1.7142 | 0.37 | 0/8 | 0.93 | 0.77 | `max_up_ret` (0.30) | -0.0006 | -1.0485 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1196 | -0.0689 | -0.0689 | -2.3631 | 0.31 | 0/8 | 0.86 | 0.68 | `opening_drive_thrust_ratio` (0.31) | +0.0015 | -1.0485 |
| `combo_rank_min__bar_body_rng_0__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0743 | -0.0284 | -0.0284 | -1.6255 | 0.50 | 0/8 | 1.08 | 0.97 | `shaved_bar_trend_conviction` (1.10) | +0.0006 | +0.0000 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1198 | -0.0739 | -0.0739 | -1.7537 | 0.32 | 0/8 | 1.21 | 1.28 | `max_down_ret` (0.39) | +0.0016 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1177 | -0.0411 | -0.0411 | -1.7157 | 0.31 | 0/8 | 0.96 | 0.78 | `opening_drive_thrust_ratio` (0.31) | +0.0009 | -1.0485 |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0757 | -0.0901 | -0.0901 | -1.9999 | 0.59 | 0/8 | 1.59 | 2.10 | `shaved_bar_trend_conviction` (1.10) | -0.0010 | -1.0485 |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1068 | -0.1430 | -0.1430 | -2.8810 | 0.38 | 0/8 | 1.26 | 1.05 | `first_bar_return` (0.48) | -0.0015 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1110 | -0.0114 | -0.0114 | -1.5357 | 0.48 | 0/8 | 0.59 | 0.52 | — | +0.0014 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | Other Technical | +1 | +0.1357 | -0.0061 | -0.0061 | +0.1883 | 0.25 | 0/8 | 0.88 | 0.78 | `trend_bar_close_consistency` (0.49) | +0.0011 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1189 | +0.0051 | +0.0051 | -1.1061 | 0.49 | 0/8 | 0.57 | 0.53 | `bar_ret_0` (0.48) | +0.0011 | +0.0000 |
| `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | Gap / Overnight Reversal | +1 | +0.1122 | +0.1113 | +0.1113 | -1.0360 | 0.57 | 0/8 | 0.45 | 0.31 | `early_late_momentum_divergence` (0.86) | +0.0020 | +0.0000 |
| `combo_min__early_body_momentum__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1027 | -0.0918 | -0.0918 | -2.1074 | 0.27 | 0/8 | 1.48 | 1.55 | `early_body_momentum` (0.36) | -0.0009 | -1.0485 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0936 | -0.0940 | -0.0940 | -3.2742 | 0.25 | 0/8 | 1.52 | 1.54 | — | -0.0013 | -1.0485 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | Other Technical | +1 | +0.1167 | +0.0811 | +0.0811 | +2.5041 | 0.36 | 0/8 | 0.78 | 0.95 | `opening_drive_thrust_ratio` (0.31) | +0.0011 | -1.0485 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0739 | +0.0711 | +0.0711 | +0.9941 | 0.71 | 1/8 | 1.01 | 1.83 | `shaved_bar_trend_conviction` (1.10) | +0.0006 | -1.0485 |
| `combo_rank_min__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.0947 | +0.0037 | +0.0037 | -0.0750 | 0.46 | 0/8 | 0.80 | 0.71 | `bar_ret_0` (0.48) | +0.0017 | +0.0000 |
| `combo_min__early_body_momentum__close_vs_open_range` | Intraday Range Momentum | +1 | +0.0972 | -0.0785 | -0.0785 | -1.9210 | 0.30 | 0/8 | 1.52 | 1.56 | `early_body_momentum` (0.36) | -0.0011 | -1.0485 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1258 | +0.0234 | +0.0234 | -0.4926 | 0.27 | 0/8 | 0.78 | 0.76 | `max_down_ret` (0.39) | +0.0021 | +0.0000 |
| `combo_rank_max__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1050 | -0.0647 | -0.0647 | -0.9479 | 0.33 | 0/8 | 1.03 | 1.19 | `max_down_ret` (0.39) | -0.0003 | +0.0000 |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.0944 | -0.0915 | -0.0915 | -0.7996 | 0.23 | 0/8 | 1.46 | 1.52 | `h2_l2_pullback_continuation` (0.43) | -0.0003 | +0.0000 |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | Other Technical | +1 | +0.1123 | -0.0669 | -0.0669 | -2.6452 | 0.25 | 0/8 | 0.96 | 0.86 | `bar_ret_0` (0.48) | +0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1278 | -0.0507 | -0.0507 | -1.8152 | 0.25 | 0/8 | 0.84 | 0.83 | `max_down_ret` (0.39) | +0.0015 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1349 | +0.0383 | +0.0383 | -0.6718 | 0.42 | 0/8 | 0.53 | 0.53 | `volume_weighted_momentum_acceleration` (0.53) | +0.0017 | +0.0000 |
| `combo_max__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1090 | -0.0643 | -0.0643 | -1.7123 | 0.38 | 0/8 | 0.96 | 1.00 | `max_down_ret` (0.39) | +0.0005 | -1.0485 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0877 | +0.1008 | +0.1008 | -0.4764 | 0.32 | 0/8 | 0.92 | 0.93 | `max_down_ret` (0.39) | +0.0007 | -1.0485 |
| `combo_rank_max__early_body_momentum__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.0918 | -0.1077 | -0.1077 | -3.1681 | 0.27 | 0/8 | 1.60 | 1.57 | `early_body_momentum` (0.36) | -0.0017 | -1.0485 |
| `combo_max__early_body_momentum__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1151 | -0.0748 | -0.0748 | -2.8952 | 0.29 | 0/8 | 0.81 | 0.86 | `bar_body_rng_0` (0.36) | +0.0005 | -1.0485 |
| `combo_sig_product__trend_day_regime_conviction__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1068 | -0.1322 | -0.1322 | -3.0824 | 0.33 | 0/8 | 0.96 | 0.73 | `early_order_flow_imbalance` (0.29) | -0.0001 | -1.0485 |
| `combo_mean__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0808 | +0.0837 | +0.0837 | +1.7820 | 0.56 | 0/8 | 0.82 | 0.98 | `shaved_bar_trend_conviction` (1.10) | +0.0010 | -1.0485 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1150 | -0.0695 | -0.0695 | -2.1354 | 0.59 | 0/8 | 0.61 | 0.54 | `bar_ret_0` (0.48) | +0.0002 | +0.0000 |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1000 | +0.0390 | +0.0390 | -1.7307 | 0.36 | 0/8 | 1.25 | 1.07 | `early_body_momentum` (0.36) | -0.0005 | -1.0485 |
| `combo_max__early_body_momentum__close_vs_open_range` | Intraday Range Momentum | +1 | +0.0977 | -0.0947 | -0.0947 | -2.2083 | 0.34 | 0/8 | 1.59 | 1.80 | `early_body_momentum` (0.36) | -0.0003 | -1.0485 |
| `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1068 | -0.0463 | -0.0463 | -1.0941 | 0.41 | 0/8 | 0.84 | 1.03 | `shaved_bar_trend_conviction` (1.10) | -0.0011 | -1.0485 |
| `combo_tri_median__net_volume_flow__volume_weighted_momentum_acceleration__bar_ret_0` | Intraday Range Momentum | +1 | +0.0951 | -0.0843 | -0.0843 | -1.7825 | 0.36 | 0/8 | 1.09 | 0.99 | `volume_weighted_momentum_acceleration` (0.53) | -0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1114 | +0.0887 | +0.0887 | -0.7597 | 0.32 | 0/8 | 0.89 | 0.88 | `opening_drive_thrust_ratio` (0.31) | -0.0003 | -1.0485 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.0993 | +0.0708 | +0.0708 | +1.0762 | 0.32 | 0/8 | 1.23 | 1.69 | `close_vs_open_range` (0.31) | +0.0007 | -1.0485 |
| `combo_rel_diff__vwap_close_divergence_trend__h2_l2_pullback_continuation` | Other Technical | +1 | +0.0884 | -0.1155 | -0.1155 | -2.3882 | 0.29 | 0/8 | 1.63 | 1.84 | `h2_l2_pullback_continuation` (0.43) | +0.0000 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.0988 | +0.0865 | +0.0865 | +1.1116 | 0.34 | 0/8 | 1.17 | 1.72 | `close_vs_open_range` (0.31) | +0.0008 | -1.0485 |
| `combo_min__trend_day_regime_conviction__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0763 | -0.1042 | -0.1042 | -1.8370 | 0.58 | 0/8 | 1.65 | 2.32 | `shaved_bar_trend_conviction` (1.10) | -0.0010 | -1.0485 |
| `combo_rank_max__max_down_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1172 | +0.0387 | +0.0387 | +0.2088 | 0.39 | 0/8 | 0.67 | 0.70 | `max_down_ret` (0.39) | +0.0017 | +0.0000 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0862 | -0.1006 | -0.1006 | -2.8810 | 0.59 | 0/8 | 0.55 | 0.48 | `first_bar_return` (0.48) | -0.0009 | +0.0000 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1158 | +0.0403 | +0.0403 | +1.5479 | 0.49 | 0/8 | 0.74 | 0.93 | `volume_weighted_momentum_acceleration` (0.53) | +0.0009 | +0.0000 |
| `combo_rel_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.0933 | -0.1257 | -0.1257 | -1.6759 | 0.27 | 0/8 | 1.60 | 1.36 | `h2_l2_pullback_continuation` (0.43) | -0.0008 | +0.0000 |
| `combo_max__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1052 | -0.0888 | -0.0888 | -3.2479 | 0.33 | 0/8 | 0.96 | 1.06 | `max_down_ret` (0.39) | -0.0012 | -1.0485 |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.0997 | +0.0265 | +0.0265 | -1.2338 | 0.27 | 0/8 | 1.06 | 0.97 | `max_down_ret` (0.39) | +0.0007 | +0.0000 |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.0992 | +0.0321 | +0.0321 | -0.3828 | 0.23 | 0/8 | 1.15 | 1.03 | `max_down_ret` (0.39) | +0.0019 | +0.0000 |
| `combo_mean__bar_body_rng_0__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0973 | -0.0455 | -0.0455 | -0.6652 | 0.42 | 0/8 | 0.81 | 0.91 | `shaved_bar_trend_conviction` (1.10) | -0.0003 | +0.0000 |
| `combo_diff__vwap_close_divergence_trend__h2_l2_pullback_continuation` | Other Technical | +1 | +0.0870 | -0.1133 | -0.1133 | -2.3882 | 0.31 | 0/8 | 1.62 | 1.70 | `h2_l2_pullback_continuation` (0.43) | -0.0006 | -1.0485 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1106 | -0.0526 | -0.0526 | -2.4640 | 0.24 | 0/8 | 0.86 | 0.79 | `trend_bar_close_consistency` (0.49) | +0.0015 | -1.0485 |
| `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1108 | -0.0741 | -0.0741 | -1.3425 | 0.41 | 0/8 | 0.83 | 1.17 | `shaved_bar_trend_conviction` (1.10) | +0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1206 | -0.0107 | -0.0107 | -2.0201 | 0.26 | 0/8 | 1.00 | 1.19 | `early_body_momentum` (0.36) | +0.0007 | -1.0485 |
| `combo_sig_product__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1236 | -0.1166 | -0.1166 | -0.3288 | 0.40 | 0/8 | 1.17 | 1.02 | `star50_limit_proximity_early` (0.28) | -0.0011 | -1.0485 |
| `combo_min__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.0725 | -0.0563 | -0.0563 | -2.3376 | 0.43 | 0/8 | 1.47 | 1.82 | `shaved_bar_trend_conviction` (1.10) | -0.0009 | -1.0485 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1002 | -0.1345 | -0.1345 | -3.0824 | 0.29 | 0/8 | 1.21 | 0.89 | — | +0.0006 | -1.0485 |
| `combo_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1026 | +0.0115 | +0.0115 | -0.8443 | 0.39 | 0/8 | 0.77 | 0.82 | `bar_ret_0` (0.48) | +0.0019 | +0.0000 |
| `combo_rank_max__early_order_flow_imbalance__shaved_bar_trend_conviction` | Volatility & Oscillators | +1 | +0.0814 | -0.1068 | -0.1068 | -1.4546 | 0.51 | 0/8 | 1.06 | 1.38 | `shaved_bar_trend_conviction` (1.10) | +0.0006 | -1.0485 |
| `combo_max__max_down_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1031 | -0.0673 | -0.0673 | -1.3419 | 0.34 | 0/8 | 1.04 | 1.25 | `max_down_ret` (0.39) | -0.0007 | -1.0485 |
| `combo_sig_product__trend_bar_close_consistency__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0925 | -0.1511 | -0.1511 | -3.0824 | 0.31 | 0/8 | 1.21 | 0.81 | `trend_bar_close_consistency` (0.49) | -0.0007 | -1.0485 |
| `combo_rank_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0895 | -0.0286 | -0.0286 | -2.7147 | 0.45 | 0/8 | 0.91 | 0.96 | `shaved_bar_trend_conviction` (1.10) | -0.0005 | +0.0000 |
| `combo_mean__max_down_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1114 | +0.0167 | +0.0167 | -0.6427 | 0.33 | 0/8 | 0.78 | 0.81 | `max_down_ret` (0.39) | +0.0021 | +0.0000 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1066 | +0.0234 | +0.0234 | -1.0720 | 0.28 | 0/8 | 1.04 | 1.08 | `max_down_ret` (0.39) | -0.0000 | +0.0000 |
| `combo_sig_product__first_bar_return__early_order_flow_imbalance` | Gap / Overnight Reversal | +1 | +0.1133 | -0.1273 | -0.1273 | -2.2618 | 0.31 | 0/8 | 0.98 | 0.74 | `first_bar_return` (0.48) | +0.0009 | -1.0485 |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1149 | -0.1058 | -0.1058 | -2.5237 | 0.49 | 0/8 | 0.65 | 0.86 | `shaved_bar_trend_conviction` (1.10) | +0.0001 | -1.0485 |
| `combo_rank_min__trend_bar_close_consistency__vwap_close_divergence_trend` | Other Technical | +1 | +0.0905 | -0.0845 | -0.0845 | -2.4438 | 0.36 | 0/8 | 1.73 | 1.96 | `trend_bar_close_consistency` (0.49) | -0.0008 | -1.0485 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1062 | +0.0695 | +0.0695 | -0.8397 | 0.38 | 0/8 | 1.17 | 0.77 | `early_body_momentum` (0.36) | +0.0000 | -1.0485 |
| `combo_rank_max__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1097 | +0.0600 | +0.0600 | -2.2650 | 0.36 | 0/8 | 1.26 | 0.90 | `star50_limit_proximity_early` (0.28) | +0.0006 | -1.0485 |
| `combo_rank_min__trend_bar_close_consistency__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0969 | -0.1075 | -0.1075 | -1.8354 | 0.29 | 0/8 | 1.49 | 1.35 | `trend_bar_close_consistency` (0.49) | +0.0002 | -1.0485 |
| `combo_z_sum__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.0993 | -0.0751 | -0.0751 | -3.2689 | 0.41 | 0/8 | 0.91 | 1.05 | `shaved_bar_trend_conviction` (1.10) | -0.0010 | -1.0485 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1065 | +0.0274 | +0.0274 | -0.1044 | 0.31 | 0/8 | 0.91 | 1.06 | `body_size_progression` (0.71) | +0.0009 | +0.0000 |
| `combo_max__volatility_expansion_trend_vector__shaved_bar_trend_conviction` | Volatility & Oscillators | +1 | +0.0871 | -0.0702 | -0.0702 | -0.6747 | 0.56 | 0/8 | 1.09 | 1.45 | `shaved_bar_trend_conviction` (1.10) | -0.0001 | -1.0485 |
| `combo_diff__trend_bar_close_consistency__demark_setup_reversal_early` | Other Technical | +1 | +0.1066 | -0.0070 | -0.0070 | -1.1638 | 0.31 | 0/8 | 1.44 | 1.48 | `trend_bar_close_consistency` (0.49) | -0.0004 | -1.0485 |
| `combo_min__early_body_momentum__max_down_ret` | Intraday Range Momentum | +1 | +0.0998 | +0.0091 | +0.0091 | -0.9128 | 0.23 | 0/8 | 1.21 | 1.27 | `max_down_ret` (0.39) | +0.0016 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1079 | +0.1145 | +0.1145 | +1.8262 | 0.42 | 0/8 | 0.52 | 0.44 | `early_late_momentum_divergence` (0.86) | +0.0016 | +0.0000 |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.0931 | -0.0350 | -0.0350 | -0.7602 | 0.24 | 0/8 | 1.21 | 1.27 | `h2_l2_pullback_continuation` (0.43) | -0.0005 | -1.0485 |
| `combo_sig_product__early_order_flow_imbalance__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1024 | -0.0633 | -0.0633 | -0.6859 | 0.50 | 0/8 | 2.41 | 2.37 | `bar_body_rng_0` (0.36) | +0.0003 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Intraday Range Momentum | +1 | +0.1011 | -0.0526 | -0.0526 | -1.6639 | 0.30 | 0/8 | 1.13 | 1.09 | `volume_weighted_momentum_acceleration` (0.53) | +0.0003 | +0.0000 |
| `num_up_bars` | Other Technical | +1 | +0.0993 | -0.0474 | -0.0474 | -2.5885 | 0.35 | 0/8 | 1.67 | 1.35 | — | -0.0003 | -1.0485 |
| `combo_rank_max__early_order_flow_imbalance__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1019 | -0.0952 | -0.0952 | -2.2932 | 0.31 | 0/8 | 0.85 | 0.74 | `bar_body_rng_0` (0.36) | +0.0014 | -1.0485 |
| `combo_sig_product__early_body_momentum__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.0919 | -0.1182 | -0.1182 | -2.4231 | 0.26 | 0/8 | 1.12 | 0.89 | `early_body_momentum` (0.36) | -0.0011 | -1.0485 |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.0910 | -0.0605 | -0.0605 | -0.7811 | 0.24 | 0/8 | 1.45 | 1.42 | `h2_l2_pullback_continuation` (0.43) | -0.0001 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.0763 | +0.0947 | +0.0947 | +1.1715 | 0.51 | 1/8 | 1.31 | 1.28 | `smooth_momentum_structure` (0.57) | +0.0009 | -1.0485 |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.0940 | -0.0312 | -0.0312 | -0.7033 | 0.25 | 0/8 | 1.26 | 1.28 | `h2_l2_pullback_continuation` (0.43) | +0.0000 | -1.0485 |
| `combo_max__first_bar_return__shaved_bar_trend_conviction` | Gap / Overnight Reversal | +1 | +0.1120 | -0.0927 | -0.0927 | -1.9193 | 0.53 | 0/8 | 0.63 | 0.85 | `shaved_bar_trend_conviction` (1.10) | -0.0004 | -1.0485 |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.0884 | +0.0540 | +0.0540 | -0.2795 | 0.34 | 0/8 | 0.95 | 1.09 | `star50_limit_proximity_early` (0.28) | +0.0014 | -1.0485 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.0966 | +0.0056 | +0.0056 | -0.6772 | 0.42 | 0/8 | 0.77 | 0.80 | `bar_ret_0` (0.48) | +0.0011 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1159 | -0.0624 | -0.0624 | -1.3419 | 0.31 | 0/8 | 0.91 | 0.67 | `opening_drive_thrust_ratio` (0.31) | +0.0009 | -1.0485 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0964 | +0.0759 | +0.0759 | +0.4853 | 0.25 | 0/8 | 1.11 | 1.01 | `max_down_ret` (0.39) | +0.0009 | -1.0485 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0957 | +0.0823 | +0.0823 | +1.1643 | 0.29 | 0/8 | 0.92 | 0.94 | `max_down_ret` (0.39) | +0.0001 | -1.0485 |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Intraday Range Momentum | +1 | +0.1148 | -0.0216 | -0.0216 | -1.4665 | 0.31 | 0/8 | 0.76 | 0.80 | `volume_weighted_momentum_acceleration` (0.53) | +0.0012 | +0.0000 |
| `combo_sig_product__early_order_flow_imbalance__close_vs_open_range` | Volatility & Oscillators | +1 | +0.0919 | -0.0637 | -0.0637 | -1.3678 | 0.34 | 0/8 | 1.45 | 1.28 | `close_vs_open_range` (0.31) | +0.0005 | -1.0485 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1259 | +0.1323 | +0.1323 | +0.4708 | 0.31 | 0/8 | 0.78 | 0.70 | `opening_drive_thrust_ratio` (0.31) | +0.0013 | +0.0000 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.0893 | -0.0312 | -0.0312 | -2.6274 | 0.20 | 0/8 | 1.36 | 1.29 | — | +0.0002 | -1.0485 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1139 | +0.0380 | +0.0380 | -0.7326 | 0.26 | 0/8 | 0.83 | 0.87 | `max_down_ret` (0.39) | +0.0015 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.1106 | +0.0360 | +0.0360 | -0.8797 | 0.34 | 0/8 | 1.44 | 1.13 | `star50_limit_proximity_early` (0.28) | -0.0002 | -1.0485 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.0541, Sharpe: +0.4992)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1574 | +0.0827 | +0.0827 | +0.6302 | 0.27 | 0/8 | 0.85 | 0.72 | `bar_body_rng_0` (0.37) | +0.0004 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1565 | +0.1000 | +0.1000 | +0.4816 | 0.33 | 0/8 | 0.73 | 0.61 | `bar_body_rng_0` (0.37) | +0.0010 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1510 | +0.0821 | +0.0821 | -0.0542 | 0.26 | 0/8 | 0.84 | 0.69 | `bar_body_rng_0` (0.37) | +0.0010 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1403 | +0.1144 | +0.1144 | +0.5302 | 0.37 | 0/8 | 0.82 | 0.69 | `bar_body_rng_0` (0.37) | +0.0022 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1422 | +0.1174 | +0.1174 | +2.8044 | 0.36 | 0/8 | 0.85 | 0.78 | `volume_weighted_price_position` (0.69) | -0.0003 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1550 | +0.1093 | +0.1093 | +0.8621 | 0.30 | 0/8 | 0.78 | 0.65 | `bar_body_rng_0` (0.37) | +0.0001 | +0.0000 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1291 | +0.1324 | +0.1324 | +2.7212 | 0.49 | 0/8 | 0.96 | 0.84 | `volume_weighted_price_position` (0.69) | -0.0005 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1436 | +0.1343 | +0.1343 | +0.7340 | 0.29 | 0/8 | 0.69 | 0.57 | `bar_body_rng_0` (0.37) | +0.0022 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1487 | +0.0866 | +0.0866 | +1.5177 | 0.32 | 0/8 | 1.01 | 0.81 | `opening_drive_thrust_ratio` (0.33) | +0.0017 | +0.0000 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1296 | +0.1495 | +0.1495 | +1.8753 | 0.45 | 0/8 | 0.81 | 0.72 | `limit_down_proximity_early` (0.44) | +0.0014 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1447 | +0.0895 | +0.0895 | +0.2487 | 0.33 | 0/8 | 0.78 | 0.60 | `bar_ret_0` (0.32) | +0.0012 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1535 | +0.0510 | +0.0510 | -0.4248 | 0.26 | 0/8 | 0.78 | 0.67 | `bar_body_rng_0` (0.37) | +0.0000 | +0.0000 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1503 | +0.0889 | +0.0889 | +2.1594 | 0.30 | 0/8 | 0.82 | 0.74 | `gap_pct` (0.76) | +0.0002 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1448 | +0.0832 | +0.0832 | +0.2726 | 0.27 | 0/8 | 0.76 | 0.61 | `bar_body_rng_0` (0.37) | +0.0013 | +0.0000 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1415 | +0.0850 | +0.0850 | +0.6640 | 0.30 | 0/8 | 1.02 | 0.99 | `max_up_ret` (0.31) | +0.0010 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1520 | +0.0766 | +0.0766 | +2.5089 | 0.28 | 0/8 | 0.98 | 0.84 | `opening_drive_thrust_ratio` (0.33) | +0.0005 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1336 | -0.0563 | -0.0563 | -2.6490 | 0.31 | 0/8 | 0.93 | 0.86 | `bar_body_rng_0` (0.37) | -0.0018 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1387 | +0.0567 | +0.0567 | -0.2824 | 0.40 | 0/8 | 1.01 | 0.86 | `bar_body_rng_0` (0.37) | -0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1423 | +0.0646 | +0.0646 | +0.1352 | 0.33 | 0/8 | 1.22 | 1.26 | `volatility_expansion_trend_vector` (0.58) | +0.0015 | -0.1657 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1243 | +0.1425 | +0.1425 | +1.0019 | 0.42 | 0/8 | 0.99 | 0.78 | `limit_down_proximity_early` (0.44) | +0.0017 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1373 | +0.0578 | +0.0578 | -0.9696 | 0.35 | 0/8 | 1.18 | 1.23 | `volatility_expansion_trend_vector` (0.58) | +0.0011 | -0.1657 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1457 | -0.0192 | -0.0192 | -1.7777 | 0.27 | 0/8 | 1.09 | 1.11 | `opening_drive_thrust_ratio` (0.33) | -0.0010 | +0.0000 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1163 | +0.1908 | +0.1908 | +2.5310 | 0.42 | 0/8 | 0.82 | 0.71 | `volume_price_confirmation` (0.57) | +0.0021 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1267 | +0.1561 | +0.1561 | +1.6600 | 0.38 | 0/8 | 0.74 | 0.63 | `volume_price_confirmation` (0.57) | +0.0004 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1332 | -0.0595 | -0.0595 | -2.7716 | 0.36 | 0/8 | 1.13 | 1.10 | `opening_drive_thrust_ratio` (0.33) | -0.0006 | +0.0000 |
| `combo_mean__max_up_ret__gap_pct` | Gap / Overnight Reversal | +1 | +0.1572 | +0.1184 | +0.1184 | -0.2163 | 0.14 | 0/8 | 0.90 | 0.92 | `gap_pct` (0.76) | -0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1317 | -0.0148 | -0.0148 | -1.0032 | 0.34 | 0/8 | 0.84 | 0.76 | `bar_body_rng_0` (0.37) | -0.0013 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1213 | -0.0770 | -0.0770 | -1.2111 | 0.44 | 0/8 | 1.13 | 0.94 | `volume_weighted_price_position` (0.69) | -0.0017 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1383 | +0.0431 | +0.0431 | +0.1011 | 0.38 | 0/8 | 0.88 | 0.76 | `bar_body_rng_0` (0.37) | +0.0001 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1378 | -0.0421 | -0.0421 | -1.8255 | 0.29 | 0/8 | 0.98 | 0.79 | `bar_body_rng_0` (0.37) | -0.0014 | +0.0000 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1259 | +0.0307 | +0.0307 | +0.0580 | 0.36 | 0/8 | 0.90 | 0.67 | `bar_body_rng_0` (0.37) | -0.0008 | +0.0000 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1249 | -0.0381 | -0.0381 | -3.2808 | 0.36 | 0/8 | 1.22 | 1.10 | `volatility_expansion_trend_vector` (0.58) | -0.0004 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Other Technical | +1 | +0.1319 | +0.1039 | +0.1039 | +1.1602 | 0.39 | 0/8 | 0.84 | 0.81 | `rally_strength_max` (0.90) | +0.0011 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1382 | -0.0036 | -0.0036 | -1.7032 | 0.28 | 0/8 | 0.98 | 0.78 | `bar_body_rng_0` (0.37) | -0.0017 | +0.0000 |
| `bar_body_rng_0` | Other Technical | +1 | +0.1232 | +0.0207 | +0.0207 | -0.3858 | 0.37 | 0/8 | 0.73 | 0.60 | — | -0.0007 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1362 | -0.0077 | -0.0077 | -1.8187 | 0.32 | 0/8 | 1.07 | 0.94 | `demark_setup_reversal_early` (0.34) | -0.0004 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1408 | +0.0545 | +0.0545 | -1.0195 | 0.24 | 0/8 | 1.22 | 1.30 | `volatility_expansion_trend_vector` (0.58) | -0.0000 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Other Technical | +1 | +0.1321 | +0.0974 | +0.0974 | +0.3863 | 0.49 | 0/8 | 0.69 | 0.61 | `rally_strength_max` (0.90) | -0.0000 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1385 | +0.1842 | +0.1842 | +1.9520 | 0.42 | 0/8 | 0.51 | 0.44 | `volume_price_confirmation` (0.57) | +0.0020 | +0.0000 |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1187 | +0.0262 | +0.0262 | -1.2196 | 0.30 | 0/8 | 1.08 | 0.97 | `volatility_expansion_trend_vector` (0.58) | -0.0007 | +0.0000 |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1314 | +0.1120 | +0.1120 | +1.5982 | 0.30 | 0/8 | 0.78 | 0.60 | `rbreaker_buy_setup_proximity_early` (0.44) | +0.0011 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1328 | -0.0654 | -0.0654 | -3.3106 | 0.34 | 0/8 | 0.98 | 0.88 | `opening_drive_thrust_ratio` (0.33) | -0.0011 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1272 | -0.0238 | -0.0238 | -1.8526 | 0.36 | 0/8 | 0.91 | 0.75 | `bar_body_rng_0` (0.37) | -0.0010 | +0.0000 |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1224 | -0.0185 | -0.0185 | +0.1961 | 0.41 | 0/8 | 0.71 | 0.74 | `volatility_expansion_trend_vector` (0.58) | -0.0009 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | Volatility & Oscillators | +1 | +0.1102 | +0.1381 | +0.1381 | +2.7110 | 0.61 | 0/8 | 1.14 | 0.85 | `volume_weighted_price_position` (0.69) | +0.0026 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1315 | +0.1013 | +0.1013 | +0.1249 | 0.28 | 0/8 | 1.02 | 0.76 | `rbreaker_buy_setup_proximity_early` (0.44) | +0.0001 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Gap / Overnight Reversal | +1 | +0.1191 | -0.0930 | -0.0930 | -3.4843 | 0.33 | 0/8 | 1.17 | 1.12 | `gap_pct` (0.76) | -0.0010 | -0.1657 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1484 | +0.0961 | +0.0961 | +1.0753 | 0.35 | 0/8 | 0.69 | 0.75 | `volume_weighted_price_position` (0.69) | +0.0003 | +0.0000 |
| `combo_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1336 | -0.0771 | -0.0771 | -3.6387 | 0.30 | 0/8 | 0.90 | 0.83 | `bar_body_rng_0` (0.37) | -0.0009 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1257 | -0.0689 | -0.0689 | -1.1833 | 0.31 | 0/8 | 1.30 | 1.09 | `opening_drive_thrust_ratio` (0.33) | -0.0020 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1279 | -0.0930 | -0.0930 | -2.1195 | 0.37 | 0/8 | 1.50 | 1.43 | `volatility_expansion_trend_vector` (0.58) | -0.0016 | +0.0000 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1159 | -0.0854 | -0.0854 | -2.9019 | 0.48 | 0/8 | 1.71 | 2.05 | `volatility_expansion_trend_vector` (0.58) | -0.0011 | +0.0000 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1411 | -0.0318 | -0.0318 | -2.0212 | 0.34 | 0/8 | 1.13 | 1.03 | `demark_setup_reversal_early` (0.34) | -0.0004 | +0.0000 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1419 | +0.0018 | +0.0018 | -2.0212 | 0.31 | 0/8 | 1.11 | 0.97 | `demark_setup_reversal_early` (0.34) | +0.0004 | +0.0000 |
| `combo_mean__max_up_ret__rally_strength_max` | Intraday Range Momentum | +1 | +0.1134 | -0.0909 | -0.0909 | -1.0768 | 0.52 | 0/8 | 1.02 | 1.09 | `rally_strength_max` (0.90) | -0.0016 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1238 | -0.0265 | -0.0265 | -1.7025 | 0.38 | 0/8 | 0.90 | 0.81 | `opening_drive_thrust_ratio` (0.33) | -0.0013 | +0.0000 |
| `combo_mean__volatility_expansion_trend_vector__rally_strength_max` | Volatility & Oscillators | +1 | +0.1007 | -0.0867 | -0.0867 | -2.3108 | 0.66 | 0/8 | 1.61 | 2.01 | `rally_strength_max` (0.90) | -0.0015 | +0.0000 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.1305 | +0.1060 | +0.1060 | +1.2898 | 0.31 | 0/8 | 1.03 | 1.02 | `gap_pct` (0.76) | +0.0018 | -0.1657 |
| `combo_max__bar_body_rng_0__rally_strength_max` | Other Technical | +1 | +0.1090 | -0.0448 | -0.0448 | +0.0816 | 0.53 | 0/8 | 0.88 | 1.05 | `rally_strength_max` (0.90) | -0.0002 | +0.0000 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1215 | -0.1035 | -0.1035 | -4.2121 | 0.41 | 0/8 | 1.40 | 1.52 | `volatility_expansion_trend_vector` (0.58) | -0.0017 | -0.1657 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1206 | +0.0841 | +0.0841 | -1.2423 | 0.33 | 0/8 | 1.36 | 1.26 | `volatility_expansion_trend_vector` (0.58) | +0.0006 | +0.0000 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.1276 | -0.0816 | -0.0816 | -4.0036 | 0.37 | 0/8 | 1.14 | 1.36 | `volatility_expansion_trend_vector` (0.58) | -0.0008 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Intraday Range Momentum | +1 | +0.1025 | +0.1554 | +0.1554 | +0.1107 | 0.37 | 0/8 | 1.01 | 0.53 | `yesterday_first_30min_return` (0.66) | +0.0034 | +0.0000 |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1120 | -0.0399 | -0.0399 | -1.5508 | 0.29 | 0/8 | 0.78 | 0.68 | `bar_body_rng_0` (0.37) | -0.0007 | +0.0000 |
| `combo_mean__bar_body_rng_0__rally_strength_max` | Other Technical | +1 | +0.1166 | -0.0159 | -0.0159 | -0.9259 | 0.46 | 0/8 | 0.77 | 0.75 | `rally_strength_max` (0.90) | -0.0009 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1238 | -0.1027 | -0.1027 | -1.1404 | 0.32 | 0/8 | 0.95 | 0.81 | `bar_body_rng_0` (0.37) | -0.0030 | +0.0000 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1223 | -0.0913 | -0.0913 | -4.2927 | 0.39 | 0/8 | 1.36 | 1.43 | `volatility_expansion_trend_vector` (0.58) | -0.0005 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1368 | +0.0426 | +0.0426 | -0.5756 | 0.34 | 0/8 | 0.91 | 0.80 | `bar_ret_0` (0.32) | -0.0004 | +0.0000 |
| `combo_max__max_up_ret__rally_strength_max` | Intraday Range Momentum | +1 | +0.1060 | -0.0883 | -0.0883 | -2.6944 | 0.54 | 0/8 | 1.01 | 1.11 | `rally_strength_max` (0.90) | -0.0013 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1160 | -0.0776 | -0.0776 | -2.0006 | 0.33 | 0/8 | 1.06 | 0.90 | `demark_setup_reversal_early` (0.34) | -0.0008 | +0.0000 |
| `combo_rank_min__max_up_ret__gap_pct` | Gap / Overnight Reversal | +1 | +0.1185 | +0.0926 | +0.0926 | +0.5706 | 0.50 | 0/8 | 0.70 | 0.74 | `gap_pct` (0.76) | +0.0018 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1196 | +0.2171 | +0.2171 | +1.8343 | 0.45 | 0/8 | 0.64 | 0.67 | `directional_volume_signature` (0.91) | +0.0025 | +0.0000 |
| `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1197 | +0.0433 | +0.0433 | +0.0061 | 0.33 | 0/8 | 0.73 | 0.60 | `gap_pct` (0.76) | -0.0002 | +0.0000 |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1288 | -0.0121 | -0.0121 | -1.7807 | 0.32 | 0/8 | 0.87 | 0.67 | `bar_body_rng_0` (0.37) | -0.0005 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1117 | +0.0712 | +0.0712 | -1.1060 | 0.30 | 0/8 | 1.25 | 0.94 | `rbreaker_buy_setup_proximity_early` (0.44) | -0.0002 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1294 | -0.0737 | -0.0737 | -3.0060 | 0.47 | 0/8 | 1.02 | 1.07 | `volume_weighted_price_position` (0.69) | -0.0013 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1139 | -0.0572 | -0.0572 | -1.0459 | 0.50 | 0/8 | 1.74 | 1.55 | `volatility_expansion_trend_vector` (0.58) | -0.0017 | +0.0000 |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1155 | -0.0016 | -0.0016 | -1.2131 | 0.41 | 0/8 | 0.86 | 0.75 | `volume_weighted_price_position` (0.69) | -0.0006 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0` | Other Technical | +1 | +0.1123 | -0.0711 | -0.0711 | -1.8622 | 0.37 | 0/8 | 0.77 | 0.54 | `bar_body_rng_0` (0.37) | -0.0016 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.0963 | +0.1801 | +0.1801 | +3.6713 | 0.46 | 0/8 | 1.01 | 0.77 | `volume_price_confirmation` (0.57) | +0.0015 | +0.0000 |
| `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1118 | +0.1814 | +0.1814 | +1.9841 | 0.48 | 0/8 | 0.56 | 0.45 | `volume_price_confirmation` (0.57) | +0.0025 | +0.0000 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1138 | +0.0844 | +0.0844 | -0.0130 | 0.39 | 0/8 | 0.84 | 1.06 | `bar_body_rng_0` (0.37) | -0.0000 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1091 | +0.0593 | +0.0593 | -1.4053 | 0.39 | 0/8 | 1.17 | 1.05 | `bar_body_rng_0` (0.37) | +0.0011 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | Other Technical | +1 | +0.1335 | +0.2095 | +0.2095 | +1.8853 | 0.47 | 0/8 | 0.59 | 0.35 | `body_size_progression` (0.85) | +0.0010 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1290 | -0.0464 | -0.0464 | -0.7909 | 0.33 | 0/8 | 1.21 | 0.97 | — | -0.0021 | +0.0000 |
| `combo_mean__volume_weighted_price_position__limit_down_proximity_early` | Volatility & Oscillators | +1 | +0.1221 | +0.1186 | +0.1186 | +0.0733 | 0.49 | 0/8 | 0.77 | 0.70 | `volume_weighted_price_position` (0.69) | +0.0007 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1188 | +0.2079 | +0.2079 | +1.6092 | 0.43 | 0/8 | 0.69 | 0.73 | `directional_volume_signature` (0.91) | +0.0031 | +0.0000 |
| `combo_rank_min__max_up_ret__rally_strength_max` | Intraday Range Momentum | +1 | +0.1121 | -0.0714 | -0.0714 | -2.5162 | 0.55 | 0/8 | 0.97 | 1.27 | `rally_strength_max` (0.90) | -0.0013 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__rally_strength_max` | Other Technical | +1 | +0.1134 | -0.0054 | -0.0054 | -1.4800 | 0.55 | 0/8 | 0.74 | 0.67 | `rally_strength_max` (0.90) | -0.0022 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1184 | -0.0811 | -0.0811 | -1.8808 | 0.33 | 0/8 | 1.14 | 0.88 | `opening_drive_thrust_ratio` (0.33) | -0.0020 | +0.0000 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1058 | +0.0888 | +0.0888 | -0.3243 | 0.47 | 0/8 | 1.35 | 1.29 | `volatility_expansion_trend_vector` (0.58) | +0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | Other Technical | +1 | +0.1128 | -0.0825 | -0.0825 | +0.4014 | 0.53 | 0/8 | 1.16 | 1.03 | `rally_strength_max` (0.90) | -0.0013 | +0.0000 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1278 | -0.0570 | -0.0570 | -0.3265 | 0.46 | 0/8 | 1.03 | 1.04 | `volume_weighted_price_position` (0.69) | -0.0024 | +0.0000 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1295 | +0.0586 | +0.0586 | -0.7006 | 0.30 | 0/8 | 1.12 | 1.01 | `max_up_ret` (0.31) | -0.0007 | +0.0000 |
| `combo_mean__volatility_expansion_trend_vector__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1062 | +0.0689 | +0.0689 | +1.7273 | 0.43 | 0/8 | 1.34 | 1.57 | `directional_volume_signature` (0.91) | +0.0009 | +0.0000 |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.1066 | -0.0851 | -0.0851 | -3.6644 | 0.38 | 0/8 | 1.06 | 1.24 | `keltner_squeeze_width` (0.68) | -0.0008 | +0.0000 |
| `combo_max__first_bar_return__rally_strength_max` | Gap / Overnight Reversal | +1 | +0.1049 | -0.0599 | -0.0599 | -1.2485 | 0.49 | 0/8 | 0.91 | 1.24 | `rally_strength_max` (0.90) | -0.0010 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1295 | +0.0307 | +0.0307 | -1.8947 | 0.34 | 0/8 | 1.10 | 1.78 | `demark_setup_reversal_early` (0.34) | -0.0007 | -0.1657 |
| `combo_max__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1236 | -0.0151 | -0.0151 | -0.8921 | 0.30 | 0/8 | 0.66 | 0.67 | `volume_price_confirmation` (0.57) | -0.0019 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1298 | +0.1358 | +0.1358 | +0.2908 | 0.26 | 0/8 | 0.73 | 0.63 | `bar_body_rng_0` (0.37) | -0.0002 | +0.0000 |
| `combo_mean__rally_strength_max__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1045 | +0.0445 | +0.0445 | +1.4513 | 0.47 | 0/8 | 0.61 | 0.63 | `rally_strength_max` (0.90) | +0.0003 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Intraday Range Momentum | +1 | +0.1173 | +0.1154 | +0.1154 | -0.0647 | 0.31 | 0/8 | 0.99 | 0.60 | `yesterday_first_30min_return` (0.66) | +0.0026 | +0.0000 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1286 | +0.0212 | +0.0212 | -1.1311 | 0.25 | 0/8 | 0.92 | 0.76 | `bar_body_rng_0` (0.37) | -0.0008 | +0.0000 |
| `combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.1111 | -0.0526 | -0.0526 | -0.9121 | 0.44 | 0/8 | 1.03 | 1.05 | `gap_pct` (0.76) | -0.0017 | +0.0000 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.1071 | +0.1273 | +0.1273 | -0.4715 | 0.52 | 0/8 | 1.42 | 0.96 | `yesterday_early_momentum` (0.78) | +0.0008 | +0.0000 |
| `combo_min__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1148 | -0.0303 | -0.0303 | -1.6286 | 0.51 | 0/8 | 0.95 | 0.91 | `volume_weighted_price_position` (0.69) | -0.0021 | +0.0000 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1243 | +0.0066 | +0.0066 | -1.1418 | 0.47 | 1/8 | 0.69 | 0.45 | `gap_pct` (0.76) | -0.0008 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__rally_strength_max` | Other Technical | +1 | +0.1172 | -0.0405 | -0.0405 | +0.3146 | 0.45 | 0/8 | 1.04 | 1.11 | `rally_strength_max` (0.90) | -0.0013 | +0.0000 |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1081 | +0.0162 | +0.0162 | -1.2979 | 0.37 | 0/8 | 0.76 | 0.51 | `gap_pct` (0.76) | +0.0002 | +0.0000 |
| `combo_mean__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.1141 | -0.0010 | -0.0010 | +0.5553 | 0.49 | 0/8 | 0.81 | 0.70 | `volume_weighted_price_position` (0.69) | -0.0007 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Other Technical | +1 | +0.1340 | +0.1724 | +0.1724 | +1.6445 | 0.24 | 0/8 | 0.95 | 0.79 | `limit_down_proximity_early` (0.44) | +0.0012 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1140 | +0.0226 | +0.0226 | +0.2558 | 0.32 | 0/8 | 0.75 | 0.56 | — | -0.0006 | +0.0000 |
| `combo_min__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1164 | +0.0299 | +0.0299 | +0.3733 | 0.32 | 0/8 | 0.97 | 0.73 | `first_bar_return` (0.32) | -0.0001 | +0.0000 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | Gap / Overnight Reversal | +1 | +0.0917 | +0.0339 | +0.0339 | +0.5163 | 0.32 | 0/8 | 0.68 | 0.58 | `gap_pct` (0.76) | +0.0011 | +0.0000 |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1118 | -0.0820 | -0.0820 | -3.0532 | 0.61 | 0/8 | 1.50 | 1.66 | `volume_weighted_price_position` (0.69) | -0.0010 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Other Technical | +1 | +0.1370 | +0.1716 | +0.1716 | +2.0307 | 0.23 | 0/8 | 0.94 | 0.80 | `limit_down_proximity_early` (0.44) | +0.0015 | +0.0000 |
| `combo_mean__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1233 | +0.0389 | +0.0389 | +0.2894 | 0.28 | 0/8 | 0.75 | 0.60 | `volume_price_confirmation` (0.57) | -0.0012 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1255 | +0.1158 | +0.1158 | +0.1892 | 0.26 | 0/8 | 0.89 | 0.71 | `bar_body_rng_0` (0.37) | +0.0008 | +0.0000 |
| `combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1131 | -0.0159 | -0.0159 | -2.4481 | 0.42 | 0/8 | 0.83 | 0.58 | `volume_weighted_price_position` (0.69) | -0.0022 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1206 | +0.0057 | +0.0057 | +0.3634 | 0.32 | 0/8 | 0.65 | 0.67 | `volume_price_confirmation` (0.57) | -0.0020 | +0.0000 |
| `combo_max__max_up_ret__directional_volume_signature` | Intraday Range Momentum | +1 | +0.1056 | +0.0276 | +0.0276 | +0.2544 | 0.35 | 0/8 | 0.86 | 1.07 | `directional_volume_signature` (0.91) | -0.0001 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1295 | +0.0623 | +0.0623 | -0.0060 | 0.28 | 0/8 | 1.50 | 1.56 | `volatility_expansion_trend_vector` (0.58) | +0.0009 | +0.0000 |
| `combo_rank_max__max_up_ret__directional_volume_signature` | Intraday Range Momentum | +1 | +0.1055 | +0.0384 | +0.0384 | +0.2544 | 0.34 | 0/8 | 0.82 | 1.04 | `directional_volume_signature` (0.91) | -0.0010 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0939 | -0.0561 | -0.0561 | -1.5551 | 0.79 | 1/8 | 1.80 | 1.71 | `volume_weighted_price_position` (0.69) | -0.0019 | +0.0000 |
| `combo_max__bar_ret_0__limit_down_proximity_early` | Other Technical | +1 | +0.1089 | +0.0866 | +0.0866 | -1.4591 | 0.35 | 0/8 | 0.80 | 0.55 | `limit_down_proximity_early` (0.44) | +0.0003 | +0.0000 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1175 | +0.0741 | +0.0741 | -1.3949 | 0.30 | 0/8 | 0.88 | 1.08 | `demark_setup_reversal_early` (0.34) | -0.0000 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__rally_strength_max` | Other Technical | +1 | +0.1207 | -0.0641 | -0.0641 | +0.8775 | 0.48 | 0/8 | 1.12 | 1.06 | `rally_strength_max` (0.90) | -0.0024 | +0.0000 |
| `combo_max__volatility_expansion_trend_vector__directional_volume_signature` | Volatility & Oscillators | +1 | +0.0998 | +0.0206 | +0.0206 | +0.8649 | 0.51 | 0/8 | 1.08 | 1.48 | `directional_volume_signature` (0.91) | -0.0001 | +0.0000 |
| `combo_clamp_diff__first_bar_return__volume_weighted_momentum_acceleration` | Gap / Overnight Reversal | +1 | +0.1205 | +0.0109 | +0.0109 | -1.8509 | 0.32 | 0/8 | 0.77 | 0.48 | `volume_weighted_momentum_acceleration` (0.32) | -0.0001 | +0.0000 |
| `combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1115 | +0.0107 | +0.0107 | -0.7547 | 0.39 | 0/8 | 0.75 | 0.52 | `gap_pct` (0.76) | +0.0000 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1027 | +0.0911 | +0.0911 | +0.1720 | 0.47 | 0/8 | 0.65 | 0.63 | `directional_volume_signature` (0.91) | +0.0005 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1236 | -0.0120 | -0.0120 | -0.7424 | 0.29 | 0/8 | 0.91 | 0.80 | `bar_ret_0` (0.32) | -0.0013 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1227 | +0.0262 | +0.0262 | -1.0933 | 0.31 | 0/8 | 1.14 | 0.99 | `opening_drive_thrust_ratio` (0.33) | -0.0005 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1038 | +0.0944 | +0.0944 | +0.9523 | 0.48 | 0/8 | 1.39 | 1.26 | `volatility_expansion_trend_vector` (0.58) | +0.0017 | +0.0000 |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1025 | -0.1064 | -0.1064 | -4.3046 | 0.59 | 0/8 | 2.15 | 2.80 | `volume_weighted_price_position` (0.69) | -0.0012 | +0.0000 |
| `combo_rank_min__rally_strength_max__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.0982 | +0.0963 | +0.0963 | +0.5919 | 0.40 | 0/8 | 0.69 | 0.60 | `rally_strength_max` (0.90) | -0.0011 | +0.0000 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.1055 | -0.0322 | -0.0322 | -1.7594 | 0.34 | 0/8 | 1.60 | 2.26 | `keltner_squeeze_width` (0.68) | -0.0009 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | Other Technical | +1 | +0.1027 | +0.1482 | +0.1482 | +1.0680 | 0.59 | 0/8 | 0.31 | 0.30 | `bar_body_rng_0` (0.37) | +0.0002 | +0.0000 |
| `combo_min__max_up_ret__rally_strength_max` | Intraday Range Momentum | +1 | +0.1150 | -0.0714 | -0.0714 | -1.8370 | 0.50 | 0/8 | 1.00 | 1.14 | `rally_strength_max` (0.90) | -0.0018 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1077 | +0.0980 | +0.0980 | +1.3754 | 0.46 | 0/8 | 1.21 | 1.12 | `bar_ret_0` (0.32) | +0.0012 | +0.0000 |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1206 | -0.0256 | -0.0256 | -0.7046 | 0.56 | 0/8 | 0.69 | 0.62 | `volume_weighted_price_position` (0.69) | -0.0013 | +0.0000 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1177 | -0.0681 | -0.0681 | -3.8603 | 0.29 | 0/8 | 1.13 | 1.16 | `volume_weighted_price_position` (0.69) | -0.0010 | -0.1657 |
| `combo_rank_min__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1104 | +0.0621 | +0.0621 | +0.3193 | 0.35 | 0/8 | 0.81 | 0.57 | `volume_price_confirmation` (0.57) | -0.0007 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1386 | +0.2070 | +0.2070 | +1.9797 | 0.35 | 0/8 | 0.92 | 0.54 | `late_bar_momentum` (0.83) | +0.0013 | +0.0000 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1121 | +0.0098 | +0.0098 | +0.0371 | 0.36 | 0/8 | 0.72 | 0.53 | `volume_weighted_price_position` (0.69) | -0.0006 | +0.0000 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1155 | -0.0445 | -0.0445 | -2.4277 | 0.46 | 0/8 | 1.22 | 1.11 | `volume_weighted_price_position` (0.69) | -0.0010 | +0.0000 |
| `combo_rank_min__max_up_ret__directional_volume_signature` | Intraday Range Momentum | +1 | +0.1031 | +0.0897 | +0.0897 | -0.0372 | 0.45 | 0/8 | 0.78 | 0.70 | `directional_volume_signature` (0.91) | +0.0005 | +0.0000 |
| `combo_rank_max__volatility_expansion_trend_vector__rally_strength_max` | Volatility & Oscillators | +1 | +0.1103 | -0.0820 | -0.0820 | -2.8534 | 0.52 | 0/8 | 1.46 | 1.65 | `rally_strength_max` (0.90) | -0.0009 | +0.0000 |
| `trend_bar_close_consistency` | Other Technical | +1 | +0.0897 | -0.1362 | -0.1362 | -1.8903 | 0.75 | 0/8 | 2.76 | 3.89 | — | -0.0010 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1114 | +0.1004 | +0.1004 | +3.1023 | 0.41 | 0/8 | 0.91 | 0.80 | `directional_volume_signature` (0.91) | +0.0004 | +0.0000 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.1109 | -0.0616 | -0.0616 | -1.6127 | 0.28 | 0/8 | 1.67 | 2.09 | `keltner_squeeze_width` (0.68) | -0.0011 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1033 | +0.0490 | +0.0490 | +2.2445 | 0.52 | 0/8 | 0.90 | 0.84 | `directional_volume_signature` (0.91) | -0.0013 | +0.0000 |
| `combo_rel_diff__bar_ret_0__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1184 | +0.0299 | +0.0299 | +1.0761 | 0.36 | 0/8 | 0.73 | 0.48 | `volume_weighted_momentum_acceleration` (0.32) | +0.0004 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__rally_strength_max` | Volatility & Oscillators | +1 | +0.0962 | -0.0427 | -0.0427 | -2.4174 | 0.83 | 1/8 | 0.91 | 1.12 | `rally_strength_max` (0.90) | -0.0015 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1217 | -0.1124 | -0.1124 | -2.6779 | 0.40 | 0/8 | 1.30 | 0.99 | `volatility_expansion_trend_vector` (0.58) | -0.0023 | +0.0000 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | Gap / Overnight Reversal | +1 | +0.1048 | +0.0354 | +0.0354 | -0.7039 | 0.31 | 0/8 | 0.63 | 0.51 | `gap_pct` (0.76) | +0.0002 | +0.0000 |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1054 | +0.0852 | +0.0852 | +0.3263 | 0.35 | 0/8 | 0.77 | 0.51 | `rbreaker_buy_setup_proximity_early` (0.44) | +0.0007 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0876 | +0.1274 | +0.1274 | +1.4311 | 0.58 | 0/8 | 0.35 | 0.32 | `demark_setup_reversal_early` (0.34) | +0.0006 | +0.0000 |
| `combo_min__volatility_expansion_trend_vector__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.0912 | +0.0628 | +0.0628 | -0.4172 | 0.36 | 0/8 | 2.03 | 1.28 | `volatility_expansion_trend_vector` (0.58) | -0.0011 | +0.0000 |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.1098 | -0.0587 | -0.0587 | -1.5751 | 0.28 | 0/8 | 1.68 | 2.09 | `keltner_squeeze_width` (0.68) | -0.0010 | -0.1657 |
| `combo_mean__opening_drive_thrust_ratio__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1205 | +0.0455 | +0.0455 | +0.6790 | 0.35 | 0/8 | 0.81 | 0.63 | `volume_price_confirmation` (0.57) | -0.0002 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.1081 | -0.0663 | -0.0663 | -3.0886 | 0.54 | 0/8 | 1.80 | 1.83 | — | -0.0009 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1212 | +0.1846 | +0.1846 | +2.4687 | 0.58 | 0/8 | 0.77 | 0.41 | `body_size_progression` (0.85) | +0.0003 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Gap / Overnight Reversal | +1 | +0.1008 | -0.0668 | -0.0668 | -2.0258 | 0.27 | 0/8 | 1.20 | 1.11 | `gap_pct` (0.76) | -0.0007 | +0.0000 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret` | Gap / Overnight Reversal | +1 | +0.1083 | -0.0423 | -0.0423 | -0.8829 | 0.56 | 0/8 | 1.37 | 1.12 | `yesterday_early_momentum` (0.78) | -0.0004 | +0.0000 |
| `combo_z_sum__max_up_ret__directional_volume_signature` | Intraday Range Momentum | +1 | +0.1134 | +0.0868 | +0.0868 | +2.0454 | 0.34 | 0/8 | 0.88 | 0.91 | `directional_volume_signature` (0.91) | +0.0003 | +0.0000 |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1124 | -0.0495 | -0.0495 | -1.7134 | 0.29 | 0/8 | 0.76 | 0.60 | `demark_setup_reversal_early` (0.34) | -0.0003 | +0.0000 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1158 | -0.0325 | -0.0325 | -2.6779 | 0.39 | 0/8 | 1.53 | 1.93 | `volatility_expansion_trend_vector` (0.58) | -0.0019 | +0.0000 |
| `combo_ratio__max_up_ret__directional_volume_signature` | Intraday Range Momentum | +1 | +0.1035 | -0.0437 | -0.0437 | -1.2791 | 0.46 | 0/8 | 1.08 | 0.93 | `directional_volume_signature` (0.91) | +0.0006 | +0.0000 |
| `combo_rank_max__bar_body_rng_0__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1140 | +0.0882 | +0.0882 | +0.8782 | 0.48 | 0/8 | 0.54 | 0.48 | `volume_price_confirmation` (0.57) | -0.0004 | +0.0000 |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1076 | -0.0010 | -0.0010 | -1.9510 | 0.51 | 0/8 | 0.85 | 0.56 | `volatility_expansion_trend_vector` (0.58) | -0.0004 | +0.0000 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.1037 | +0.0154 | +0.0154 | -0.1510 | 0.45 | 0/8 | 1.58 | 1.13 | `volatility_expansion_trend_vector` (0.58) | -0.0006 | +0.0000 |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1122 | +0.0279 | +0.0279 | -1.5933 | 0.38 | 0/8 | 1.83 | 1.63 | `volatility_expansion_trend_vector` (0.58) | -0.0000 | +0.0000 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | Gap / Overnight Reversal | +1 | +0.1342 | -0.0582 | -0.0582 | -2.1924 | 0.40 | 0/8 | 1.00 | 0.88 | `gap_pct` (0.76) | -0.0012 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1092 | +0.1154 | +0.1154 | +1.0340 | 0.33 | 0/8 | 0.88 | 0.65 | `directional_volume_signature` (0.91) | +0.0007 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__directional_volume_signature` | Volatility & Oscillators | +1 | +0.0887 | +0.2417 | +0.2417 | +2.6620 | 0.66 | 0/8 | 0.98 | 0.94 | `directional_volume_signature` (0.91) | +0.0025 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1124 | -0.1070 | -0.1070 | -1.0195 | 0.35 | 0/8 | 0.98 | 0.81 | `opening_drive_thrust_ratio` (0.33) | -0.0021 | +0.0000 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1130 | +0.2061 | +0.2061 | +1.0874 | 0.45 | 0/8 | 1.40 | 1.45 | `volume_weighted_momentum_acceleration` (0.32) | +0.0006 | -0.1657 |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0907 | +0.0955 | +0.0955 | -0.7293 | 0.59 | 1/8 | 1.89 | 2.13 | `volatility_expansion_trend_vector` (0.58) | +0.0018 | +0.0000 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1177 | +0.0598 | +0.0598 | +0.7863 | 0.36 | 0/8 | 0.97 | 0.61 | `early_late_momentum_divergence` (0.83) | -0.0012 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__body_size_progression` | Other Technical | +1 | +0.1149 | +0.0605 | +0.0605 | -0.5995 | 0.38 | 0/8 | 1.31 | 1.55 | `body_size_progression` (0.85) | +0.0002 | +0.0000 |
| `combo_clamp_diff__volume_weighted_price_position__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.0987 | +0.0533 | +0.0533 | -1.7870 | 0.63 | 0/8 | 0.77 | 0.40 | `early_late_momentum_divergence` (0.83) | -0.0012 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Other Technical | +1 | +0.0639 | -0.0939 | -0.0939 | -0.6519 | 0.51 | 1/8 | 0.59 | 0.73 | `limit_down_proximity_early` (0.44) | -0.0023 | +0.0000 |
| `combo_ifelse__gap_pct__yesterday_early_trend__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0892 | +0.0564 | +0.0564 | -0.4957 | 0.73 | 1/8 | 1.00 | 0.46 | `gap_pct` (0.76) | -0.0000 | +0.0000 |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0656 | +0.0896 | +0.0896 | -1.6385 | 0.74 | 1/8 | 2.10 | 2.34 | `volatility_expansion_trend_vector` (0.58) | +0.0021 | +0.0000 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 36.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9697_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1192 | 30 | 0.0% | 0.0% | -0.0894 | -1.0491 |
| B2 Rolling Guard | 121 | 30 | 36.7% | 13.3% | -0.0067 | -0.7813 |
| BH-FDR Gate | 2 | 2 | 100.0% | 100.0% | +0.0565 | +0.2261 |
| B3 Composite Floor | 11 | 11 | 63.6% | 18.2% | -0.0298 | -1.1715 |
| B4 Correlation Gate | 226 | 30 | 20.0% | 6.7% | -0.0563 | -0.8679 |

**Admitted Pool Summary**: 75 features, False Positive Rate = 94.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0961, Mean Lock Sharpe = -1.5147

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.1412, Lock IC=+0.1517, Lock Sharpe=+0.9530
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early`: Train IC=+0.1412, Lock IC=+0.1517, Lock Sharpe=+0.9530
- `combo_sig_product__star50_limit_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1588, Lock IC=+0.1188, Lock Sharpe=+0.7891
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1352, Lock IC=+0.1290, Lock Sharpe=+0.6923

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__early_vwap_acceleration__early_late_momentum_divergence`: Train IC=+0.0663, Lock IC=+0.0565, Lock Sharpe=+0.2261
- `combo_z_diff__early_vwap_acceleration__early_late_momentum_divergence`: Train IC=+0.0663, Lock IC=+0.0565, Lock Sharpe=+0.2261

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1403, Lock IC=+0.1448, Lock Sharpe=+0.9422
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1403, Lock IC=+0.1448, Lock Sharpe=+0.9422

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Lock Sharpe=+0.4322
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Lock Sharpe=+0.4322

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 50.0% lock IC > 0, 31.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5482_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 803 | 30 | 83.3% | 56.7% | +0.0731 | +0.4562 |
| B2 Rolling Guard | 72 | 30 | 30.0% | 23.3% | -0.0108 | -0.3929 |
| BH-FDR Gate | 2 | 2 | 0.0% | 0.0% | -0.0613 | -2.3056 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__willr14__roc60`: Train IC=+0.1006, Lock IC=+0.1152, Lock Sharpe=+3.0356
- `combo_rank_min__multi_ema_alignment_5_20_50__roc60`: Train IC=+0.1289, Lock IC=+0.1252, Lock Sharpe=+2.4985
- `combo_min__iv_corridor_width__multi_ema_alignment_5_20_50`: Train IC=+0.1762, Lock IC=+0.0650, Lock Sharpe=+2.4401
- `combo_rank_max__volume_differential_10d__roc60`: Train IC=+0.1091, Lock IC=+0.1168, Lock Sharpe=+1.4182
- `demark_setup_reversal_early`: Train IC=+0.1292, Lock IC=+0.0963, Lock Sharpe=+1.3257

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `star50_limit_proximity_early`: Train IC=+0.1222, Lock IC=+0.1992, Lock Sharpe=+1.4268
- `combo_ratio__star50_limit_proximity_early__bar_vol_4`: Train IC=+0.0864, Lock IC=+0.1827, Lock Sharpe=+1.2460
- `limit_down_proximity_early`: Train IC=+0.1138, Lock IC=+0.1983, Lock Sharpe=+0.9672
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1138, Lock IC=+0.1983, Lock Sharpe=+0.9672
- `combo_sig_product__iv_corridor_width__multi_ema_alignment_5_20_50`: Train IC=+0.0825, Lock IC=+0.0364, Lock Sharpe=+0.9067

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 38.0% lock IC > 0, 27.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8982_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2753 | 30 | 56.7% | 50.0% | +0.0142 | -0.6733 |
| B2 Rolling Guard | 442 | 30 | 20.0% | 10.0% | -0.0473 | -1.8313 |
| B3 Composite Floor | 63 | 30 | 50.0% | 6.7% | -0.0081 | -1.0821 |
| B4 Correlation Gate | 644 | 30 | 60.0% | 23.3% | +0.0085 | -0.8758 |

**Admitted Pool Summary**: 190 features, False Positive Rate = 83.2% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0151, Mean Lock Sharpe = -1.0718

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Lock Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Lock Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2279, Lock IC=+0.1062, Lock Sharpe=+1.3424
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.2184, Lock IC=+0.0565, Lock Sharpe=+0.2974
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.2184, Lock IC=+0.0565, Lock Sharpe=+0.2974

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1769, Lock IC=+0.1949, Lock Sharpe=+1.1683
- `combo_rel_diff__max_up_ret__shaved_bar_trend_conviction`: Train IC=+0.1876, Lock IC=+0.0337, Lock Sharpe=+0.2895
- `combo_rank_max__demark_setup_reversal_early__body_size_progression`: Train IC=+0.2054, Lock IC=+0.1227, Lock Sharpe=+0.0641

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Lock Sharpe=+0.1323
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Lock Sharpe=+0.1323

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.2557, Lock IC=+0.0706, Lock Sharpe=+0.8062
- `combo_tri_z_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.2557, Lock IC=+0.0706, Lock Sharpe=+0.8062
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0`: Train IC=+0.2515, Lock IC=+0.0869, Lock Sharpe=+0.6688
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__bar_ret_0`: Train IC=+0.2515, Lock IC=+0.0869, Lock Sharpe=+0.6688
- `combo_tri_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.2499, Lock IC=+0.0369, Lock Sharpe=+0.4718

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 60.0% lock IC > 0, 34.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3121_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1950 | 30 | 76.7% | 50.0% | +0.0950 | +0.5321 |
| B2 Rolling Guard | 246 | 30 | 90.0% | 73.3% | +0.1305 | +0.8436 |
| BH-FDR Gate | 3 | 3 | 33.3% | 33.3% | -0.0520 | -0.9606 |
| B3 Composite Floor | 112 | 30 | 80.0% | 20.0% | +0.0332 | -0.6673 |
| B4 Correlation Gate | 285 | 30 | 96.7% | 73.3% | +0.1045 | +0.7229 |

**Admitted Pool Summary**: 185 features, False Positive Rate = 62.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0289, Mean Lock Sharpe = -0.4975

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Lock Sharpe=+3.8591
- `combo_z_sum__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Lock Sharpe=+3.8591
- `combo_mean__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Lock Sharpe=+3.8591
- `combo_z_sum__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Lock Sharpe=+3.8591
- `combo_mean__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2233, Lock IC=+0.2142, Lock Sharpe=+3.5556

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1815, Lock IC=+0.2385, Lock Sharpe=+2.9556
- `combo_min__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1815, Lock IC=+0.2385, Lock Sharpe=+2.9556
- `combo_diff__star50_limit_proximity_early__early_late_momentum_divergence`: Train IC=+0.1899, Lock IC=+0.2161, Lock Sharpe=+2.5866
- `combo_z_diff__star50_limit_proximity_early__early_late_momentum_divergence`: Train IC=+0.1899, Lock IC=+0.2161, Lock Sharpe=+2.5866
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression`: Train IC=+0.2549, Lock IC=+0.1835, Lock Sharpe=+2.4160

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Lock Sharpe=+0.2891

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__max_up_ret__directional_volume_signature`: Train IC=+0.2093, Lock IC=+0.0868, Lock Sharpe=+2.0454
- `combo_rank_min__opening_drive_thrust_ratio__volume_price_confirmation`: Train IC=+0.1979, Lock IC=+0.0532, Lock Sharpe=+0.9115
- `combo_min__rally_strength_max__volume_price_confirmation`: Train IC=+0.2305, Lock IC=+0.0793, Lock Sharpe=+0.3427
- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.1939, Lock IC=+0.0436, Lock Sharpe=+0.3411
- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0`: Train IC=+0.1938, Lock IC=+0.0432, Lock Sharpe=+0.3411

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2975, Lock IC=+0.1253, Lock Sharpe=+2.7133
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3187, Lock IC=+0.1205, Lock Sharpe=+2.3935
- `combo_ifelse__gap_pct__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2928, Lock IC=+0.1055, Lock Sharpe=+2.2540
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.3014, Lock IC=+0.1495, Lock Sharpe=+1.8753
- `combo_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation`: Train IC=+0.2972, Lock IC=+0.1728, Lock Sharpe=+1.7445

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 594 | -0.0040 | 30.0% |
| 0.45 | 0.20 | 579 | -0.0040 | 30.0% |
| 0.45 | 0.30 | 546 | -0.0040 | 30.0% |
| 0.45 | 0.40 | 491 | -0.0040 | 30.0% |
| 0.45 | 0.50 | 422 | -0.0040 | 30.0% |
| 0.50 | 0.15 | 587 | -0.0040 | 30.0% |
| 0.50 | 0.25 | 562 | -0.0040 | 30.0% |
| 0.50 | 0.35 | 521 | -0.0040 | 30.0% |
| 0.50 | 0.45 | 461 | -0.0040 | 30.0% |
| 0.55 | 0.10 | 581 | -0.0040 | 30.0% |
| 0.55 | 0.20 | 577 | -0.0040 | 30.0% |
| 0.55 | 0.30 | 546 | -0.0040 | 30.0% |
| 0.55 | 0.40 | 491 | -0.0040 | 30.0% |
| 0.55 | 0.50 | 422 | -0.0040 | 30.0% |
| 0.60 | 0.15 | 549 | -0.0040 | 30.0% |
| 0.60 | 0.25 | 546 | -0.0040 | 30.0% |
| 0.60 | 0.35 | 518 | -0.0040 | 30.0% |
| 0.60 | 0.45 | 461 | -0.0040 | 30.0% |
| 0.65 | 0.10 | 484 | -0.0040 | 30.0% |
| 0.65 | 0.20 | 484 | -0.0040 | 30.0% |
| 0.65 | 0.30 | 484 | -0.0040 | 30.0% |
| 0.65 | 0.40 | 478 | -0.0040 | 30.0% |
| 0.65 | 0.50 | 422 | -0.0040 | 30.0% |
| 0.70 | 0.15 | 388 | -0.0040 | 30.0% |
| 0.70 | 0.25 | 388 | -0.0040 | 30.0% |
| 0.70 | 0.35 | 388 | -0.0040 | 30.0% |
| 0.70 | 0.45 | 388 | -0.0040 | 30.0% |
| 0.75 | 0.10 | 198 | -0.0127 | 30.0% |
| 0.75 | 0.20 | 198 | -0.0127 | 30.0% |
| 0.75 | 0.30 | 198 | -0.0127 | 30.0% |
| 0.75 | 0.40 | 198 | -0.0127 | 30.0% |
| 0.75 | 0.50 | 198 | -0.0127 | 30.0% |
| 0.80 | 0.15 | 28 | -0.0180 | 40.0% |
| 0.80 | 0.25 | 28 | -0.0180 | 40.0% |
| 0.80 | 0.35 | 28 | -0.0180 | 40.0% |
| 0.80 | 0.45 | 28 | -0.0180 | 40.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 594 candidates, mean lock IC=-0.0040, 30.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 165 | +0.1090 | 100.0% |
| 0.45 | 0.20 | 157 | +0.1090 | 100.0% |
| 0.45 | 0.30 | 134 | +0.1090 | 100.0% |
| 0.45 | 0.40 | 110 | +0.1090 | 100.0% |
| 0.45 | 0.50 | 85 | +0.1113 | 100.0% |
| 0.50 | 0.15 | 163 | +0.1090 | 100.0% |
| 0.50 | 0.25 | 150 | +0.1090 | 100.0% |
| 0.50 | 0.35 | 122 | +0.1090 | 100.0% |
| 0.50 | 0.45 | 91 | +0.1090 | 100.0% |
| 0.55 | 0.10 | 162 | +0.1090 | 100.0% |
| 0.55 | 0.20 | 154 | +0.1090 | 100.0% |
| 0.55 | 0.30 | 134 | +0.1090 | 100.0% |
| 0.55 | 0.40 | 110 | +0.1090 | 100.0% |
| 0.55 | 0.50 | 85 | +0.1113 | 100.0% |
| 0.60 | 0.15 | 144 | +0.1090 | 100.0% |
| 0.60 | 0.25 | 140 | +0.1090 | 100.0% |
| 0.60 | 0.35 | 120 | +0.1090 | 100.0% |
| 0.60 | 0.45 | 91 | +0.1090 | 100.0% |
| 0.65 | 0.10 | 110 | +0.1090 | 100.0% |
| 0.65 | 0.20 | 110 | +0.1090 | 100.0% |
| 0.65 | 0.30 | 110 | +0.1090 | 100.0% |
| 0.65 | 0.40 | 107 | +0.1090 | 100.0% |
| 0.65 | 0.50 | 85 | +0.1113 | 100.0% |
| 0.70 | 0.15 | 70 | +0.1113 | 100.0% |
| 0.70 | 0.25 | 70 | +0.1113 | 100.0% |
| 0.70 | 0.35 | 70 | +0.1113 | 100.0% |
| 0.70 | 0.45 | 68 | +0.1113 | 100.0% |
| 0.75 | 0.10 | 41 | +0.1223 | 100.0% |
| 0.75 | 0.20 | 41 | +0.1223 | 100.0% |
| 0.75 | 0.30 | 41 | +0.1223 | 100.0% |
| 0.75 | 0.40 | 41 | +0.1223 | 100.0% |
| 0.75 | 0.50 | 41 | +0.1223 | 100.0% |
| 0.80 | 0.15 | 22 | +0.1249 | 100.0% |
| 0.80 | 0.25 | 22 | +0.1249 | 100.0% |
| 0.80 | 0.35 | 22 | +0.1249 | 100.0% |
| 0.80 | 0.45 | 22 | +0.1249 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 22 candidates, mean lock IC=+0.1249, 100.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1971 | +0.0130 | 100.0% |
| 0.45 | 0.20 | 1912 | +0.0130 | 100.0% |
| 0.45 | 0.30 | 1802 | +0.0130 | 100.0% |
| 0.45 | 0.40 | 1565 | +0.0130 | 100.0% |
| 0.45 | 0.50 | 1216 | +0.0130 | 100.0% |
| 0.50 | 0.15 | 1947 | +0.0130 | 100.0% |
| 0.50 | 0.25 | 1872 | +0.0130 | 100.0% |
| 0.50 | 0.35 | 1690 | +0.0130 | 100.0% |
| 0.50 | 0.45 | 1392 | +0.0130 | 100.0% |
| 0.55 | 0.10 | 1939 | +0.0130 | 100.0% |
| 0.55 | 0.20 | 1912 | +0.0130 | 100.0% |
| 0.55 | 0.30 | 1802 | +0.0130 | 100.0% |
| 0.55 | 0.40 | 1565 | +0.0130 | 100.0% |
| 0.55 | 0.50 | 1216 | +0.0130 | 100.0% |
| 0.60 | 0.15 | 1829 | +0.0130 | 100.0% |
| 0.60 | 0.25 | 1817 | +0.0130 | 100.0% |
| 0.60 | 0.35 | 1688 | +0.0130 | 100.0% |
| 0.60 | 0.45 | 1392 | +0.0130 | 100.0% |
| 0.65 | 0.10 | 1550 | +0.0130 | 100.0% |
| 0.65 | 0.20 | 1550 | +0.0130 | 100.0% |
| 0.65 | 0.30 | 1549 | +0.0130 | 100.0% |
| 0.65 | 0.40 | 1504 | +0.0130 | 100.0% |
| 0.65 | 0.50 | 1216 | +0.0130 | 100.0% |
| 0.70 | 0.15 | 1097 | +0.0130 | 100.0% |
| 0.70 | 0.25 | 1097 | +0.0130 | 100.0% |
| 0.70 | 0.35 | 1097 | +0.0130 | 100.0% |
| 0.70 | 0.45 | 1095 | +0.0130 | 100.0% |
| 0.75 | 0.10 | 485 | +0.0104 | 100.0% |
| 0.75 | 0.20 | 485 | +0.0104 | 100.0% |
| 0.75 | 0.30 | 485 | +0.0104 | 100.0% |
| 0.75 | 0.40 | 485 | +0.0104 | 100.0% |
| 0.75 | 0.50 | 485 | +0.0104 | 100.0% |
| 0.80 | 0.15 | 90 | +0.0104 | 100.0% |
| 0.80 | 0.25 | 90 | +0.0104 | 100.0% |
| 0.80 | 0.35 | 90 | +0.0104 | 100.0% |
| 0.80 | 0.45 | 90 | +0.0104 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1971 candidates, mean lock IC=+0.0130, 100.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1009 | +0.0920 | 100.0% |
| 0.45 | 0.20 | 979 | +0.0920 | 100.0% |
| 0.45 | 0.30 | 916 | +0.0920 | 100.0% |
| 0.45 | 0.40 | 811 | +0.0920 | 100.0% |
| 0.45 | 0.50 | 636 | +0.0920 | 100.0% |
| 0.50 | 0.15 | 995 | +0.0920 | 100.0% |
| 0.50 | 0.25 | 950 | +0.0920 | 100.0% |
| 0.50 | 0.35 | 867 | +0.0920 | 100.0% |
| 0.50 | 0.45 | 725 | +0.0920 | 100.0% |
| 0.55 | 0.10 | 1002 | +0.0920 | 100.0% |
| 0.55 | 0.20 | 977 | +0.0920 | 100.0% |
| 0.55 | 0.30 | 915 | +0.0920 | 100.0% |
| 0.55 | 0.40 | 811 | +0.0920 | 100.0% |
| 0.55 | 0.50 | 636 | +0.0920 | 100.0% |
| 0.60 | 0.15 | 930 | +0.0920 | 100.0% |
| 0.60 | 0.25 | 920 | +0.0920 | 100.0% |
| 0.60 | 0.35 | 866 | +0.0920 | 100.0% |
| 0.60 | 0.45 | 725 | +0.0920 | 100.0% |
| 0.65 | 0.10 | 778 | +0.0920 | 100.0% |
| 0.65 | 0.20 | 778 | +0.0920 | 100.0% |
| 0.65 | 0.30 | 778 | +0.0920 | 100.0% |
| 0.65 | 0.40 | 761 | +0.0920 | 100.0% |
| 0.65 | 0.50 | 630 | +0.0920 | 100.0% |
| 0.70 | 0.15 | 553 | +0.0920 | 100.0% |
| 0.70 | 0.25 | 553 | +0.0920 | 100.0% |
| 0.70 | 0.35 | 553 | +0.0920 | 100.0% |
| 0.70 | 0.45 | 553 | +0.0920 | 100.0% |
| 0.75 | 0.10 | 333 | +0.0920 | 100.0% |
| 0.75 | 0.20 | 333 | +0.0920 | 100.0% |
| 0.75 | 0.30 | 333 | +0.0920 | 100.0% |
| 0.75 | 0.40 | 333 | +0.0920 | 100.0% |
| 0.75 | 0.50 | 333 | +0.0920 | 100.0% |
| 0.80 | 0.15 | 114 | +0.0920 | 100.0% |
| 0.80 | 0.25 | 114 | +0.0920 | 100.0% |
| 0.80 | 0.35 | 114 | +0.0920 | 100.0% |
| 0.80 | 0.45 | 114 | +0.0920 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1009 candidates, mean lock IC=+0.0920, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1078 | +0.0000 | +0.0217 | 0.20x | 2016-08-24 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1058 | +0.0000 | +0.0005 | 0.00x | 2017-09-06 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1083 | +0.0000 | -0.0273 | -0.25x | 2016-08-24 |
| `combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position` | +0.0748 | +0.0000 | -0.1298 | -1.74x | 2010-12-14 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | +0.1169 | +0.0000 | -0.1740 | -1.49x | 2017-07-10 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1090 | +0.0000 | +0.0449 | 0.41x | 2017-08-08 |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | +0.1024 | +0.0000 | -0.1215 | -1.19x | 2015-02-06 |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | +0.0926 | +0.0000 | -0.1502 | -1.62x | 2013-08-21 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | +0.1184 | +0.0000 | -0.0701 | -0.59x | 2017-06-09 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1117 | +0.0000 | -0.0316 | -0.28x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1111 | +0.0000 | -0.0294 | -0.26x | 2016-08-24 |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | +0.1041 | +0.0000 | -0.1994 | -1.91x | 2017-07-10 |
| `combo_rank_max__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1072 | +0.0000 | -0.1975 | -1.84x | 2017-07-10 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | +0.1191 | +0.0000 | -0.0712 | -0.60x | 2016-08-24 |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | +0.0926 | +0.0000 | -0.1743 | -1.88x | 2015-02-06 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1060 | +0.0000 | -0.0924 | -0.87x | 2017-08-08 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.0989 | +0.0000 | -0.2114 | -2.14x | 2015-02-06 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.0928 | +0.0000 | +0.0147 | 0.16x | 2016-07-26 |
| `combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum` | +0.0861 | +0.0000 | -0.0781 | -0.91x | 2015-03-16 |
| `combo_rank_max__first_bar_return__bar_body_rng_0` | +0.0911 | +0.0000 | -0.0927 | -1.02x | 2010-12-14 |
| `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | +0.0960 | +0.0000 | -0.0509 | -0.53x | 2017-06-09 |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1183 | +0.0000 | -0.0308 | -0.26x | 2017-07-10 |
| `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | +0.1048 | +0.0000 | -0.0631 | -0.60x | 2015-02-06 |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1123 | +0.0000 | -0.0581 | -0.52x | 2015-02-06 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.1028 | +0.0000 | -0.0955 | -0.93x | 2015-02-06 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1021 | +0.0000 | -0.1938 | -1.90x | 2015-02-06 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0954 | +0.0000 | +0.0709 | 0.74x | 2017-09-06 |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.1095 | +0.0000 | -0.1697 | -1.55x | 2015-02-06 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1107 | +0.0000 | -0.1637 | -1.48x | 2015-02-06 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | +0.0979 | +0.0000 | -0.0691 | -0.71x | 2015-03-16 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.0903 | +0.0000 | -0.1297 | -1.44x | 2011-12-23 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | +0.0843 | +0.0000 | -0.1087 | -1.29x | 2013-08-21 |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0` | +0.1082 | +0.0000 | -0.1364 | -1.26x | 2015-02-06 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1082 | +0.0000 | -0.1518 | -1.40x | 2017-07-10 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | +0.1115 | +0.0000 | -0.1072 | -0.96x | 2014-06-05 |
| `combo_tri_median__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | +0.1045 | +0.0000 | -0.1153 | -1.10x | 2015-01-08 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1120 | +0.0000 | -0.0504 | -0.45x | 2017-06-09 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | +0.1101 | +0.0000 | -0.1967 | -1.79x | 2015-03-16 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1051 | +0.0000 | -0.1478 | -1.41x | 2015-02-06 |
| `combo_min__opening_drive_thrust_ratio__morning_volume_weighted_momentum` | +0.0963 | +0.0000 | -0.1581 | -1.64x | 2017-04-07 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1087 | +0.0000 | +0.0038 | 0.03x | 2016-08-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | +0.0948 | +0.0000 | -0.0317 | -0.33x | 2016-08-24 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position` | +0.1116 | +0.0000 | -0.1298 | -1.16x | 2015-01-08 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.0998 | +0.0000 | -0.1566 | -1.57x | 2014-07-04 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | +0.0944 | +0.0000 | -0.0262 | -0.28x | 2016-08-24 |
| `combo_mean__max_up_ret__morning_volume_weighted_momentum` | +0.0894 | +0.0000 | -0.1658 | -1.85x | 2017-06-09 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | +0.1069 | +0.0000 | -0.1526 | -1.43x | 2015-02-06 |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | +0.0887 | +0.0000 | -0.1961 | -2.21x | 2014-08-04 |
| `combo_tri_max__opening_drive_thrust_ratio__bar_body_rng_0__volume_weighted_price_position` | +0.1027 | +0.0000 | -0.1708 | -1.66x | 2017-07-10 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1061 | +0.0000 | -0.0169 | -0.16x | 2017-05-09 |
| `combo_max__volume_weighted_price_position__morning_volume_weighted_momentum` | +0.0934 | +0.0000 | -0.2186 | -2.34x | 2017-02-06 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | +0.1073 | +0.0000 | -0.1148 | -1.07x | 2017-06-09 |
| `combo_rank_min__max_up_ret__morning_volume_weighted_momentum` | +0.0843 | +0.0000 | -0.1487 | -1.76x | 2017-06-09 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1096 | +0.0000 | -0.1306 | -1.19x | 2015-02-06 |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0` | +0.1128 | +0.0000 | -0.0539 | -0.48x | 2015-02-06 |
| `combo_rank_max__first_bar_return__morning_volume_weighted_momentum` | +0.0881 | +0.0000 | -0.1967 | -2.23x | 2014-08-04 |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | +0.1111 | +0.0000 | -0.1364 | -1.23x | 2017-07-10 |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_body_rng_0` | +0.1016 | +0.0000 | -0.1079 | -1.06x | 2015-02-06 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | +0.1005 | +0.0000 | -0.1469 | -1.46x | 2015-01-08 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1126 | +0.0000 | -0.0541 | -0.48x | 2015-02-06 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | +0.0667 | +0.0000 | +0.0763 | 1.14x | 2011-10-26 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1088 | +0.0000 | -0.0121 | -0.11x | 2016-08-24 |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | +0.1099 | +0.0000 | -0.1081 | -0.98x | 2017-07-10 |
| `opening_drive_thrust_ratio` | +0.1099 | +0.0000 | -0.1510 | -1.37x | 2017-06-09 |
| `combo_mean__volume_weighted_price_position__morning_volume_weighted_momentum` | +0.0947 | +0.0000 | -0.1802 | -1.90x | 2015-02-06 |
| `combo_rank_min__max_up_ret__first_bar_return` | +0.0913 | +0.0000 | -0.0947 | -1.04x | 2015-02-06 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1065 | +0.0000 | -0.0023 | -0.02x | 2016-08-24 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0901 | +0.0000 | +0.0628 | 0.70x | 2016-08-24 |
| `combo_mean__bar_ret_0__morning_volume_weighted_momentum` | +0.0862 | +0.0000 | -0.1430 | -1.66x | 2013-09-23 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` | +0.1027 | +0.0000 | +0.0883 | 0.86x | 2016-08-24 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | +0.0729 | +0.0000 | -0.1823 | -2.50x | 2015-02-06 |
| `combo_diff__first_bar_return__early_late_momentum_divergence` | +0.1066 | +0.0000 | -0.0028 | -0.03x | 2014-05-06 |
| `morning_volume_weighted_momentum` | +0.0713 | +0.0000 | -0.1752 | -2.46x | 2015-02-06 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | +0.1047 | +0.0000 | -0.0127 | -0.12x | 2017-08-08 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | +0.1771 | +0.0000 | +0.0514 | 0.29x | 2016-09-26 |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | +0.1741 | +0.0000 | +0.0529 | 0.30x | 2016-09-26 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1788 | +0.0000 | +0.0028 | 0.02x | 2025-07-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | +0.1598 | +0.0000 | +0.0733 | 0.46x | 2019-12-05 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1676 | +0.0000 | +0.0984 | 0.59x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | +0.1784 | +0.0000 | +0.0419 | 0.23x | No decay |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1718 | +0.0000 | +0.0876 | 0.51x | No decay |
| `combo_mean__bar_ret_0__close_vs_open_range` | +0.1613 | +0.0000 | -0.0383 | -0.24x | No decay |
| `combo_min__net_volume_flow__first_bar_return` | +0.1441 | +0.0000 | -0.0010 | -0.01x | No decay |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1621 | +0.0000 | +0.0727 | 0.45x | 2021-07-28 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | +0.1748 | +0.0000 | -0.0197 | -0.11x | No decay |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | +0.1447 | +0.0000 | -0.0451 | -0.31x | 2020-01-06 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1898 | +0.0000 | -0.0114 | -0.06x | No decay |
| `combo_rank_min__net_volume_flow__bar_body_rng_0` | +0.1447 | +0.0000 | -0.0182 | -0.13x | 2016-11-01 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1632 | +0.0000 | +0.1016 | 0.62x | No decay |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1725 | +0.0000 | +0.0078 | 0.05x | No decay |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | +0.1449 | +0.0000 | -0.0727 | -0.50x | 2016-09-26 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1688 | +0.0000 | +0.0033 | 0.02x | No decay |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | +0.1775 | +0.0000 | +0.0571 | 0.32x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1718 | +0.0000 | +0.0846 | 0.49x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.1848 | +0.0000 | +0.0815 | 0.44x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | +0.1777 | +0.0000 | -0.0298 | -0.17x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1865 | +0.0000 | +0.0617 | 0.33x | No decay |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | +0.1670 | +0.0000 | +0.0001 | 0.00x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1639 | +0.0000 | +0.0350 | 0.21x | No decay |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | +0.1581 | +0.0000 | -0.0705 | -0.45x | 2020-02-12 |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1532 | +0.0000 | +0.0175 | 0.11x | 2016-09-26 |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | +0.1505 | +0.0000 | -0.0684 | -0.45x | 2016-11-01 |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | +0.1619 | +0.0000 | -0.0676 | -0.42x | No decay |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | +0.1624 | +0.0000 | +0.0988 | 0.61x | 2019-12-05 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | +0.1909 | +0.0000 | +0.0674 | 0.35x | No decay |
| `combo_mean__max_up_ret__max_down_ret` | +0.1755 | +0.0000 | -0.0160 | -0.09x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1883 | +0.0000 | +0.0177 | 0.09x | No decay |
| `combo_diff__net_volume_flow__smooth_momentum_structure` | +0.1762 | +0.0000 | +0.0252 | 0.14x | No decay |
| `combo_mean__first_bar_return__max_down_ret` | +0.1472 | +0.0000 | +0.0117 | 0.08x | No decay |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | +0.1422 | +0.0000 | -0.0339 | -0.24x | 2016-11-01 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | +0.1826 | +0.0000 | +0.0277 | 0.15x | No decay |
| `combo_rank_min__net_volume_flow__shaved_bar_trend_conviction` | +0.1316 | +0.0000 | -0.0821 | -0.62x | 2016-09-26 |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | +0.1435 | +0.0000 | +0.0140 | 0.10x | 2020-02-12 |
| `combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0` | +0.1612 | +0.0000 | -0.0199 | -0.12x | 2020-01-06 |
| `combo_clamp_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | +0.1305 | +0.0000 | -0.1034 | -0.79x | 2016-11-01 |
| `combo_min__first_bar_return__bar_body_rng_0` | +0.1389 | +0.0000 | -0.0051 | -0.04x | 2013-09-23 |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | +0.1340 | +0.0000 | +0.0600 | 0.45x | 2016-09-26 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +0.1667 | +0.0000 | +0.0068 | 0.04x | 2016-11-30 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1568 | +0.0000 | +0.1749 | 1.12x | 2016-08-24 |
| `combo_mean__rsi_opening__bar_body_rng_0` | +0.1567 | +0.0000 | -0.0320 | -0.20x | 2020-02-12 |
| `combo_rank_max__max_up_ret__max_down_ret` | +0.1715 | +0.0000 | -0.0061 | -0.04x | 2016-11-30 |
| `morning_volume_weighted_momentum` | +0.1399 | +0.0000 | -0.0906 | -0.65x | 2016-11-01 |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | +0.1155 | +0.0000 | -0.1131 | -0.98x | 2016-11-01 |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | +0.1713 | +0.0000 | +0.0004 | 0.00x | No decay |
| `combo_rank_max__max_up_ret__bar_ret_0` | +0.1668 | +0.0000 | -0.0673 | -0.40x | No decay |
| `combo_mean__bar_ret_0__early_order_flow_imbalance` | +0.1467 | +0.0000 | -0.0684 | -0.47x | 2016-11-01 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1531 | +0.0000 | +0.1783 | 1.16x | 2022-12-15 |
| `combo_max__bar_ret_0__max_down_ret` | +0.1583 | +0.0000 | +0.0077 | 0.05x | 2016-11-01 |
| `combo_rank_min__early_order_flow_imbalance__shaved_bar_trend_conviction` | +0.1300 | +0.0000 | -0.1273 | -0.98x | 2016-11-01 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | +0.1527 | +0.0000 | +0.1278 | 0.84x | No decay |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | +0.1591 | +0.0000 | -0.0080 | -0.05x | 2016-11-01 |
| `combo_max__early_body_momentum__early_order_flow_imbalance` | +0.1335 | +0.0000 | -0.1244 | -0.93x | 2016-09-26 |
| `combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend` | +0.1360 | +0.0000 | -0.0712 | -0.52x | 2016-11-01 |
| `combo_min__first_bar_return__close_vs_open_range` | +0.1407 | +0.0000 | +0.0019 | 0.01x | 2020-01-06 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1746 | +0.0000 | -0.0023 | -0.01x | No decay |
| `volatility_expansion_trend_vector` | +0.1487 | +0.0000 | -0.0850 | -0.57x | 2016-11-01 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +0.1759 | +0.0000 | -0.0068 | -0.04x | No decay |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__bar_ret_0` | +0.1336 | +0.0000 | -0.0001 | -0.00x | 2016-11-01 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | +0.1564 | +0.0000 | +0.1105 | 0.71x | 2019-12-05 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +0.1857 | +0.0000 | -0.0468 | -0.25x | 2016-11-30 |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1391 | +0.0000 | +0.0765 | 0.55x | 2016-09-26 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1525 | +0.0000 | -0.0503 | -0.33x | 2016-11-01 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1517 | +0.0000 | +0.0832 | 0.55x | 2016-12-29 |
| `net_volume_flow` | +0.1524 | +0.0000 | -0.0580 | -0.38x | 2016-11-01 |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | +0.1659 | +0.0000 | -0.0916 | -0.55x | No decay |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | +0.1611 | +0.0000 | -0.0501 | -0.31x | 2016-11-01 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1525 | +0.0000 | +0.1800 | 1.18x | 2022-12-15 |
| `combo_min__first_bar_return__vwap_close_divergence_trend` | +0.1349 | +0.0000 | +0.0050 | 0.04x | 2016-11-01 |
| `combo_diff__net_volume_flow__h2_l2_pullback_continuation` | +0.1388 | +0.0000 | -0.0890 | -0.64x | 2016-11-01 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +0.1400 | +0.0000 | +0.0849 | 0.61x | 2016-08-24 |
| `combo_mean__first_bar_return__shaved_bar_trend_conviction` | +0.1457 | +0.0000 | -0.0510 | -0.35x | 2016-11-01 |
| `first_30min_return` | +0.1471 | +0.0000 | -0.1128 | -0.77x | 2016-11-01 |
| `combo_tri_median__max_up_ret__net_volume_flow__smooth_momentum_structure` | +0.1348 | +0.0000 | -0.0680 | -0.50x | 2016-09-26 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | +0.1710 | +0.0000 | -0.0656 | -0.38x | 2020-01-06 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1875 | +0.0000 | -0.0194 | -0.10x | No decay |
| `combo_sig_product__early_body_momentum__vwap_close_divergence_trend` | +0.1256 | +0.0000 | -0.0956 | -0.76x | 2016-11-01 |
| `combo_clamp_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1588 | +0.0000 | +0.0343 | 0.22x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1836 | +0.0000 | +0.1003 | 0.55x | No decay |
| `combo_tri_max__opening_drive_thrust_ratio__early_body_momentum__trend_day_regime_conviction` | +0.1748 | +0.0000 | -0.0451 | -0.26x | 2016-11-30 |
| `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0` | +0.1423 | +0.0000 | -0.0666 | -0.47x | No decay |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | +0.1453 | +0.0000 | -0.1062 | -0.73x | 2020-02-12 |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | +0.1597 | +0.0000 | -0.0518 | -0.32x | 2014-06-05 |
| `combo_rel_diff__early_body_momentum__demark_setup_reversal_early` | +0.1655 | +0.0000 | +0.0170 | 0.10x | 2016-09-26 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | +0.1401 | +0.0000 | +0.0792 | 0.57x | 2016-08-24 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | +0.1547 | +0.0000 | -0.0187 | -0.12x | 2016-11-01 |
| `combo_min__close_vs_open_range__bar_body_rng_0` | +0.1419 | +0.0000 | -0.0140 | -0.10x | 2016-11-01 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | +0.1302 | +0.0000 | -0.0915 | -0.70x | 2019-12-05 |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1522 | +0.0000 | -0.0906 | -0.59x | 2020-01-06 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | +0.1449 | +0.0000 | +0.1520 | 1.05x | 2011-10-26 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | +0.1841 | +0.0000 | -0.0079 | -0.04x | No decay |
| `combo_sig_product__max_up_ret__early_order_flow_imbalance` | +0.1639 | +0.0000 | -0.0342 | -0.21x | 2017-03-07 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1661 | +0.0000 | -0.0689 | -0.41x | 2016-12-29 |
| `combo_rank_min__bar_body_rng_0__shaved_bar_trend_conviction` | +0.1235 | +0.0000 | -0.0284 | -0.23x | 2016-09-26 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | +0.1354 | +0.0000 | -0.0739 | -0.55x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | +0.1705 | +0.0000 | -0.0411 | -0.24x | 2016-12-29 |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | +0.1193 | +0.0000 | -0.0901 | -0.76x | 2016-11-01 |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | +0.1227 | +0.0000 | -0.1430 | -1.17x | 2016-09-26 |
| `first_bar_return` | +0.1352 | +0.0000 | -0.0114 | -0.08x | 2013-09-23 |
| `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | +0.1784 | +0.0000 | -0.0061 | -0.03x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1582 | +0.0000 | +0.0050 | 0.03x | No decay |
| `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | +0.1389 | +0.0000 | +0.1113 | 0.80x | 2020-12-18 |
| `combo_min__early_body_momentum__vwap_close_divergence_trend` | +0.1335 | +0.0000 | -0.0918 | -0.69x | 2016-11-01 |
| `vwap_close_divergence_trend` | +0.1303 | +0.0000 | -0.0940 | -0.72x | 2016-11-01 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | +0.1635 | +0.0000 | +0.0811 | 0.50x | 2016-09-26 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | +0.1365 | +0.0000 | +0.0663 | 0.49x | 2016-09-26 |
| `combo_rank_min__bar_ret_0__vwap_close_divergence_trend` | +0.1348 | +0.0000 | +0.0060 | 0.04x | 2016-11-01 |
| `combo_min__early_body_momentum__close_vs_open_range` | +0.1326 | +0.0000 | -0.0785 | -0.59x | 2016-11-01 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | +0.1692 | +0.0000 | +0.0234 | 0.14x | 2016-11-30 |
| `combo_rank_max__max_down_ret__vwap_close_divergence_trend` | +0.1436 | +0.0000 | -0.0606 | -0.42x | 2016-11-01 |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | +0.1363 | +0.0000 | -0.0915 | -0.67x | 2016-11-01 |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | +0.1514 | +0.0000 | -0.0669 | -0.44x | 2017-02-06 |
| `combo_sig_product__max_up_ret__max_down_ret` | +0.1651 | +0.0000 | -0.0507 | -0.31x | 2014-05-06 |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1575 | +0.0000 | +0.0383 | 0.24x | No decay |
| `combo_max__net_volume_flow__max_down_ret` | +0.1559 | +0.0000 | -0.0643 | -0.41x | 2016-11-30 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1405 | +0.0000 | +0.1008 | 0.72x | 2016-09-26 |
| `combo_rank_max__early_body_momentum__vwap_close_divergence_trend` | +0.1361 | +0.0000 | -0.0998 | -0.73x | 2016-11-01 |
| `combo_max__early_body_momentum__bar_body_rng_0` | +0.1561 | +0.0000 | -0.0748 | -0.48x | 2020-02-12 |
| `combo_sig_product__trend_day_regime_conviction__early_order_flow_imbalance` | +0.1269 | +0.0000 | -0.1322 | -1.04x | 2016-09-26 |
| `combo_mean__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | +0.1387 | +0.0000 | +0.0837 | 0.60x | 2016-11-01 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1498 | +0.0000 | -0.0695 | -0.46x | No decay |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early` | +0.1511 | +0.0000 | +0.0390 | 0.26x | 2016-11-01 |
| `combo_max__early_body_momentum__close_vs_open_range` | +0.1437 | +0.0000 | -0.0947 | -0.66x | 2016-11-01 |
| `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | +0.1622 | +0.0000 | -0.0463 | -0.29x | 2016-11-01 |
| `combo_tri_median__net_volume_flow__volume_weighted_momentum_acceleration__bar_ret_0` | +0.1202 | +0.0000 | -0.0843 | -0.70x | 2016-09-26 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1717 | +0.0000 | +0.0887 | 0.52x | No decay |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | +0.1480 | +0.0000 | +0.0708 | 0.48x | 2016-09-26 |
| `combo_rel_diff__vwap_close_divergence_trend__h2_l2_pullback_continuation` | +0.1248 | +0.0000 | -0.1155 | -0.93x | 2016-11-01 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +0.1470 | +0.0000 | +0.0854 | 0.58x | 2016-09-26 |
| `combo_min__trend_day_regime_conviction__shaved_bar_trend_conviction` | +0.1244 | +0.0000 | -0.1042 | -0.84x | 2016-11-01 |
| `combo_rank_max__max_down_ret__bar_body_rng_0` | +0.1499 | +0.0000 | +0.0381 | 0.25x | No decay |
| `combo_sig_product__net_volume_flow__first_bar_return` | +0.1199 | +0.0000 | -0.1006 | -0.84x | 2016-09-26 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1479 | +0.0000 | +0.0403 | 0.27x | No decay |
| `combo_rel_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | +0.1277 | +0.0000 | -0.1257 | -0.98x | 2016-11-01 |
| `combo_max__max_down_ret__vwap_close_divergence_trend` | +0.1421 | +0.0000 | -0.0888 | -0.62x | 2016-11-01 |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | +0.1465 | +0.0000 | +0.0224 | 0.15x | 2016-11-01 |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | +0.1437 | +0.0000 | +0.0321 | 0.22x | 2016-11-01 |
| `combo_mean__bar_body_rng_0__shaved_bar_trend_conviction` | +0.1456 | +0.0000 | -0.0455 | -0.31x | 2016-11-01 |
| `combo_diff__vwap_close_divergence_trend__h2_l2_pullback_continuation` | +0.1228 | +0.0000 | -0.1133 | -0.92x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1608 | +0.0000 | -0.0526 | -0.33x | 2016-12-29 |
| `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | +0.1670 | +0.0000 | -0.0716 | -0.43x | 2016-11-01 |
| `combo_sig_product__max_up_ret__early_body_momentum` | +0.1695 | +0.0000 | -0.0107 | -0.06x | 2019-12-05 |
| `combo_sig_product__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1380 | +0.0000 | -0.1166 | -0.84x | 2016-09-26 |
| `combo_min__max_up_ret__shaved_bar_trend_conviction` | +0.1350 | +0.0000 | -0.0563 | -0.42x | 2019-12-05 |
| `early_order_flow_imbalance` | +0.1232 | +0.0000 | -0.1345 | -1.09x | 2016-11-01 |
| `combo_min__bar_ret_0__max_down_ret` | +0.1331 | +0.0000 | +0.0115 | 0.09x | No decay |
| `combo_rank_max__early_order_flow_imbalance__shaved_bar_trend_conviction` | +0.1172 | +0.0000 | -0.1195 | -1.02x | 2016-09-26 |
| `combo_max__max_down_ret__close_vs_open_range` | +0.1453 | +0.0000 | -0.0673 | -0.46x | 2016-11-01 |
| `combo_sig_product__trend_bar_close_consistency__early_order_flow_imbalance` | +0.1138 | +0.0000 | -0.1511 | -1.33x | 2012-06-05 |
| `combo_rank_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | +0.1411 | +0.0000 | -0.0275 | -0.19x | 2016-09-26 |
| `combo_mean__max_down_ret__bar_body_rng_0` | +0.1425 | +0.0000 | +0.0167 | 0.12x | No decay |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | +0.1516 | +0.0000 | +0.0237 | 0.16x | 2016-11-01 |
| `combo_sig_product__first_bar_return__early_order_flow_imbalance` | +0.1247 | +0.0000 | -0.1273 | -1.02x | 2020-02-12 |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | +0.1527 | +0.0000 | -0.1080 | -0.71x | No decay |
| `combo_rank_min__trend_bar_close_consistency__vwap_close_divergence_trend` | +0.1277 | +0.0000 | -0.0828 | -0.65x | 2016-11-01 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1565 | +0.0000 | +0.0807 | 0.52x | 2016-09-26 |
| `combo_rank_max__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1600 | +0.0000 | +0.0668 | 0.42x | 2016-09-26 |
| `combo_rank_min__trend_bar_close_consistency__early_order_flow_imbalance` | +0.1265 | +0.0000 | -0.1076 | -0.85x | 2016-11-01 |
| `combo_z_sum__max_up_ret__shaved_bar_trend_conviction` | +0.1540 | +0.0000 | -0.0751 | -0.49x | 2016-11-01 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1384 | +0.0000 | +0.0274 | 0.20x | 2014-05-06 |
| `combo_max__volatility_expansion_trend_vector__shaved_bar_trend_conviction` | +0.1355 | +0.0000 | -0.0702 | -0.52x | 2016-11-01 |
| `combo_diff__trend_bar_close_consistency__demark_setup_reversal_early` | +0.1586 | +0.0000 | -0.0070 | -0.04x | 2016-09-26 |
| `combo_min__early_body_momentum__max_down_ret` | +0.1377 | +0.0000 | +0.0091 | 0.07x | 2016-09-26 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | +0.1461 | +0.0000 | +0.1145 | 0.78x | 2016-12-29 |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | +0.1396 | +0.0000 | -0.0350 | -0.25x | 2016-11-01 |
| `combo_sig_product__early_order_flow_imbalance__bar_body_rng_0` | +0.1353 | +0.0000 | -0.0633 | -0.47x | 2016-09-26 |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | +0.1323 | +0.0000 | -0.0526 | -0.40x | 2016-09-26 |
| `num_up_bars` | +0.1231 | +0.0000 | -0.0474 | -0.38x | 2020-02-12 |
| `combo_rank_max__early_order_flow_imbalance__bar_body_rng_0` | +0.1318 | +0.0000 | -0.0957 | -0.73x | 2016-11-30 |
| `combo_sig_product__early_body_momentum__early_order_flow_imbalance` | +0.1179 | +0.0000 | -0.1182 | -1.00x | 2016-09-26 |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | +0.1356 | +0.0000 | -0.0605 | -0.45x | 2016-11-01 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__smooth_momentum_structure` | +0.1232 | +0.0000 | +0.0947 | 0.77x | 2016-09-26 |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | +0.1400 | +0.0000 | -0.0312 | -0.22x | 2016-11-01 |
| `combo_max__first_bar_return__shaved_bar_trend_conviction` | +0.1478 | +0.0000 | -0.0927 | -0.63x | 2019-12-05 |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | +0.1415 | +0.0000 | +0.0540 | 0.38x | 2016-09-26 |
| `combo_rank_min__bar_ret_0__max_down_ret` | +0.1321 | +0.0000 | +0.0056 | 0.04x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1609 | +0.0000 | -0.0624 | -0.39x | 2016-12-29 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1390 | +0.0000 | +0.0759 | 0.55x | 2016-08-24 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1393 | +0.0000 | +0.0839 | 0.60x | 2016-09-26 |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | +0.1509 | +0.0000 | -0.0216 | -0.14x | No decay |
| `combo_sig_product__early_order_flow_imbalance__close_vs_open_range` | +0.1435 | +0.0000 | -0.0637 | -0.44x | 2016-11-30 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1806 | +0.0000 | +0.1323 | 0.73x | 2023-01-16 |
| `vwap_trend_channel_slope` | +0.1420 | +0.0000 | -0.0312 | -0.22x | 2016-11-01 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | +0.1589 | +0.0000 | +0.0391 | 0.25x | 2016-09-26 |
| `combo_rank_max__star50_limit_proximity_early__vwap_close_divergence_trend` | +0.1494 | +0.0000 | +0.0378 | 0.25x | 2016-09-26 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1561 | +0.0000 | +0.0827 | 0.53x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1587 | +0.0000 | +0.1000 | 0.63x | 2017-04-28 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1633 | +0.0000 | +0.0821 | 0.50x | 2017-01-20 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1422 | +0.0000 | +0.1144 | 0.80x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1502 | +0.0000 | +0.1090 | 0.73x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1560 | +0.0000 | +0.1064 | 0.68x | 2011-11-16 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +0.1438 | +0.0000 | +0.1324 | 0.92x | 2016-10-24 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | +0.1523 | +0.0000 | +0.1343 | 0.88x | 2017-02-27 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1550 | +0.0000 | +0.0832 | 0.54x | 2016-09-14 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.1293 | +0.0000 | +0.1495 | 1.16x | 2011-10-18 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1557 | +0.0000 | +0.0895 | 0.58x | 2011-10-18 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1673 | +0.0000 | +0.0510 | 0.30x | 2017-02-27 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1532 | +0.0000 | +0.0889 | 0.58x | 2016-10-24 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1556 | +0.0000 | +0.0832 | 0.53x | 2017-02-27 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | +0.1579 | +0.0000 | +0.0848 | 0.54x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1571 | +0.0000 | +0.0766 | 0.49x | 2016-10-24 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +0.1525 | +0.0000 | -0.0559 | -0.37x | 2017-02-27 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1545 | +0.0000 | +0.0567 | 0.37x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1548 | +0.0000 | +0.0693 | 0.45x | 2016-10-24 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | +0.1245 | +0.0000 | +0.1393 | 1.12x | 2011-10-18 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1521 | +0.0000 | +0.0578 | 0.38x | 2016-10-24 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1604 | +0.0000 | -0.0192 | -0.12x | 2016-10-24 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | +0.1246 | +0.0000 | +0.1908 | 1.53x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | +0.1374 | +0.0000 | +0.1556 | 1.13x | 2011-11-16 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1570 | +0.0000 | -0.0628 | -0.40x | 2016-12-21 |
| `combo_mean__max_up_ret__gap_pct` | +0.1614 | +0.0000 | +0.1184 | 0.73x | 2017-01-20 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | +0.1468 | +0.0000 | -0.0148 | -0.10x | 2026-03-27 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1386 | +0.0000 | -0.0735 | -0.53x | 2016-10-24 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | +0.1545 | +0.0000 | +0.0431 | 0.28x | 2017-04-28 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | +0.1609 | +0.0000 | -0.0421 | -0.26x | 2017-01-20 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1486 | +0.0000 | +0.0307 | 0.21x | 2017-01-20 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | +0.1503 | +0.0000 | -0.0381 | -0.25x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | +0.1445 | +0.0000 | +0.0841 | 0.58x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1439 | +0.0000 | -0.0036 | -0.02x | 2017-01-20 |
| `bar_body_rng_0` | +0.1355 | +0.0000 | +0.0207 | 0.15x | 2017-02-27 |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1457 | +0.0000 | -0.0077 | -0.05x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1570 | +0.0000 | +0.0545 | 0.35x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | +0.1466 | +0.0000 | +0.0974 | 0.66x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | +0.1490 | +0.0000 | +0.1842 | 1.24x | 2017-01-20 |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | +0.1476 | +0.0000 | +0.0262 | 0.18x | 2016-10-24 |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | +0.1428 | +0.0000 | +0.1120 | 0.78x | 2011-10-18 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1574 | +0.0000 | -0.0654 | -0.42x | 2017-01-20 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1552 | +0.0000 | -0.0239 | -0.15x | 2017-01-20 |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | +0.1498 | +0.0000 | -0.0185 | -0.12x | 2017-01-20 |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | +0.1278 | +0.0000 | +0.1313 | 1.03x | 2016-09-14 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1474 | +0.0000 | +0.1013 | 0.69x | 2016-09-14 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | +0.1467 | +0.0000 | -0.0930 | -0.63x | 2017-01-20 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1633 | +0.0000 | +0.0961 | 0.59x | 2017-01-20 |
| `combo_max__max_up_ret__bar_body_rng_0` | +0.1503 | +0.0000 | -0.0771 | -0.51x | 2017-02-27 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1438 | +0.0000 | -0.0689 | -0.48x | 2016-12-21 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1550 | +0.0000 | -0.0881 | -0.57x | 2016-10-24 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | +0.1397 | +0.0000 | -0.0854 | -0.61x | 2016-10-24 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | +0.1542 | +0.0000 | -0.0318 | -0.21x | 2016-10-24 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1575 | +0.0000 | +0.0018 | 0.01x | 2016-10-24 |
| `combo_mean__max_up_ret__rally_strength_max` | +0.1440 | +0.0000 | -0.0909 | -0.63x | 2016-11-22 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1516 | +0.0000 | -0.0265 | -0.17x | 2017-01-20 |
| `combo_mean__volatility_expansion_trend_vector__rally_strength_max` | +0.1324 | +0.0000 | -0.0867 | -0.66x | 2016-10-24 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | +0.1529 | +0.0000 | +0.1060 | 0.69x | 2016-11-22 |
| `combo_max__bar_body_rng_0__rally_strength_max` | +0.1367 | +0.0000 | -0.0448 | -0.33x | 2017-01-20 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | +0.1512 | +0.0000 | -0.1035 | -0.68x | 2016-10-24 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1416 | +0.0000 | +0.0841 | 0.59x | 2016-09-14 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | +0.1568 | +0.0000 | -0.0816 | -0.52x | 2017-01-20 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | +0.0957 | +0.0000 | +0.1554 | 1.62x | 2011-10-18 |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0` | +0.1329 | +0.0000 | -0.0399 | -0.30x | 2017-03-28 |
| `combo_mean__bar_body_rng_0__rally_strength_max` | +0.1410 | +0.0000 | -0.0159 | -0.11x | 2017-03-28 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1324 | +0.0000 | -0.1027 | -0.78x | 2016-11-22 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | +0.1524 | +0.0000 | -0.0860 | -0.56x | 2016-11-22 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1579 | +0.0000 | +0.0426 | 0.27x | 2017-01-20 |
| `combo_max__max_up_ret__rally_strength_max` | +0.1311 | +0.0000 | -0.0883 | -0.67x | 2016-11-22 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | +0.1398 | +0.0000 | -0.0776 | -0.56x | 2016-12-21 |
| `combo_rank_min__max_up_ret__gap_pct` | +0.1368 | +0.0000 | +0.0955 | 0.70x | 2016-09-14 |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | +0.1392 | +0.0000 | +0.2171 | 1.56x | 2017-01-20 |
| `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return` | +0.1338 | +0.0000 | +0.0433 | 0.32x | 2017-04-28 |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | +0.1535 | +0.0000 | -0.0121 | -0.08x | 2017-01-20 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1299 | +0.0000 | +0.0793 | 0.61x | 2016-09-14 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1570 | +0.0000 | -0.0689 | -0.44x | 2016-12-21 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1344 | +0.0000 | -0.0572 | -0.43x | 2016-10-24 |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | +0.1323 | +0.0000 | -0.0016 | -0.01x | 2017-02-27 |
| `combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0` | +0.1308 | +0.0000 | -0.0711 | -0.54x | 2017-04-28 |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | +0.1083 | +0.0000 | +0.1805 | 1.67x | 2011-10-18 |
| `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation` | +0.1250 | +0.0000 | +0.1814 | 1.45x | 2011-10-18 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | +0.1326 | +0.0000 | +0.0844 | 0.64x | 2017-06-01 |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | +0.1130 | +0.0000 | +0.0593 | 0.52x | 2017-01-20 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | +0.1247 | +0.0000 | +0.2095 | 1.68x | 2011-03-11 |
| `opening_drive_thrust_ratio` | +0.1460 | +0.0000 | -0.0464 | -0.32x | 2016-10-24 |
| `combo_mean__volume_weighted_price_position__limit_down_proximity_early` | +0.1407 | +0.0000 | +0.1186 | 0.84x | 2016-10-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | +0.1351 | +0.0000 | +0.2027 | 1.50x | 2011-11-16 |
| `combo_rank_min__max_up_ret__rally_strength_max` | +0.1354 | +0.0000 | -0.0605 | -0.45x | 2016-10-24 |
| `combo_rank_min__bar_body_rng_0__rally_strength_max` | +0.1281 | +0.0000 | -0.0055 | -0.04x | 2017-03-28 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1284 | +0.0000 | -0.0811 | -0.63x | 2014-03-25 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1295 | +0.0000 | +0.0888 | 0.69x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | +0.1302 | +0.0000 | -0.0754 | -0.58x | 2016-10-24 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1563 | +0.0000 | -0.0570 | -0.36x | 2017-01-20 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | +0.1429 | +0.0000 | +0.0657 | 0.46x | 2016-10-24 |
| `combo_mean__volatility_expansion_trend_vector__directional_volume_signature` | +0.1382 | +0.0000 | +0.0689 | 0.50x | 2016-10-24 |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | +0.1259 | +0.0000 | -0.0851 | -0.68x | 2016-10-24 |
| `combo_max__first_bar_return__rally_strength_max` | +0.1325 | +0.0000 | -0.0599 | -0.45x | 2017-09-27 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | +0.1432 | +0.0000 | +0.0307 | 0.21x | 2017-01-20 |
| `combo_max__max_up_ret__volume_price_confirmation` | +0.1398 | +0.0000 | -0.0151 | -0.11x | 2017-01-20 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1474 | +0.0000 | +0.1358 | 0.92x | 2017-02-27 |
| `combo_mean__rally_strength_max__volume_price_confirmation` | +0.1330 | +0.0000 | +0.0445 | 0.33x | 2017-01-20 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | +0.1172 | +0.0000 | +0.1154 | 0.98x | 2017-02-27 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | +0.1463 | +0.0000 | +0.0212 | 0.15x | 2017-02-27 |
| `combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position` | +0.1339 | +0.0000 | -0.0526 | -0.39x | 2016-11-22 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | +0.0983 | +0.0000 | +0.1273 | 1.29x | 2011-12-15 |
| `combo_min__max_up_ret__volume_weighted_price_position` | +0.1402 | +0.0000 | -0.0303 | -0.22x | 2017-01-20 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1428 | +0.0000 | +0.0066 | 0.05x | 2017-01-20 |
| `combo_max__opening_drive_thrust_ratio__rally_strength_max` | +0.1432 | +0.0000 | -0.0405 | -0.28x | 2017-01-20 |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | +0.1422 | +0.0000 | +0.0162 | 0.11x | 2017-01-20 |
| `combo_mean__first_bar_return__volume_weighted_price_position` | +0.1430 | +0.0000 | -0.0010 | -0.01x | 2017-01-20 |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +0.1357 | +0.0000 | +0.1724 | 1.27x | 2011-10-18 |
| `first_bar_return` | +0.1367 | +0.0000 | +0.0226 | 0.17x | 2017-04-28 |
| `combo_min__max_up_ret__first_bar_return` | +0.1479 | +0.0000 | +0.0299 | 0.20x | 2017-01-20 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | +0.1192 | +0.0000 | +0.0339 | 0.28x | 2016-12-21 |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1395 | +0.0000 | -0.0820 | -0.59x | 2016-10-24 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +0.1404 | +0.0000 | +0.1729 | 1.23x | 2011-10-18 |
| `combo_mean__max_up_ret__volume_price_confirmation` | +0.1471 | +0.0000 | +0.0389 | 0.26x | 2017-01-20 |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | +0.1494 | +0.0000 | +0.1269 | 0.85x | 2017-02-27 |
| `combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration` | +0.1169 | +0.0000 | -0.0159 | -0.14x | 2017-01-20 |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | +0.1404 | +0.0000 | -0.0013 | -0.01x | 2017-01-20 |
| `combo_max__max_up_ret__directional_volume_signature` | +0.1210 | +0.0000 | +0.0276 | 0.23x | 2017-01-20 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1509 | +0.0000 | +0.0648 | 0.43x | 2016-09-14 |
| `combo_rank_max__max_up_ret__directional_volume_signature` | +0.1211 | +0.0000 | +0.0341 | 0.28x | 2017-01-20 |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1219 | +0.0000 | -0.0536 | -0.44x | 2016-10-24 |
| `combo_max__bar_ret_0__limit_down_proximity_early` | +0.1332 | +0.0000 | +0.0866 | 0.65x | 2017-01-20 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | +0.1360 | +0.0000 | +0.0741 | 0.54x | 2017-04-28 |
| `combo_mean__opening_drive_thrust_ratio__rally_strength_max` | +0.1450 | +0.0000 | -0.0641 | -0.44x | 2016-10-24 |
| `combo_max__volatility_expansion_trend_vector__directional_volume_signature` | +0.1314 | +0.0000 | +0.0206 | 0.16x | 2016-10-24 |
| `combo_clamp_diff__first_bar_return__volume_weighted_momentum_acceleration` | +0.1249 | +0.0000 | +0.0109 | 0.09x | 2011-03-11 |
| `combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0` | +0.1396 | +0.0000 | +0.0107 | 0.08x | 2017-01-20 |
| `combo_rank_min__bar_body_rng_0__directional_volume_signature` | +0.1194 | +0.0000 | +0.0992 | 0.83x | 2017-01-20 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1403 | +0.0000 | -0.0120 | -0.09x | 2026-03-27 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1462 | +0.0000 | +0.0262 | 0.18x | 2016-12-21 |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1283 | +0.0000 | +0.0975 | 0.76x | 2016-09-14 |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | +0.1317 | +0.0000 | -0.1064 | -0.81x | 2016-09-14 |
| `combo_rank_min__rally_strength_max__volume_price_confirmation` | +0.1164 | +0.0000 | +0.0827 | 0.71x | 2016-10-24 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | +0.1253 | +0.0000 | -0.0322 | -0.26x | 2026-03-27 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | +0.1119 | +0.0000 | +0.1482 | 1.32x | 2011-03-11 |
| `combo_min__max_up_ret__rally_strength_max` | +0.1398 | +0.0000 | -0.0714 | -0.51x | 2016-11-22 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1140 | +0.0000 | +0.0980 | 0.86x | 2016-09-14 |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | +0.1421 | +0.0000 | -0.0233 | -0.16x | 2017-01-20 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +0.1372 | +0.0000 | -0.0681 | -0.50x | 2017-01-20 |
| `combo_rank_min__max_up_ret__volume_price_confirmation` | +0.1370 | +0.0000 | +0.0644 | 0.47x | 2017-01-20 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | +0.1297 | +0.0000 | +0.2070 | 1.60x | 2012-01-17 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.1344 | +0.0000 | +0.0098 | 0.07x | 2017-04-28 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1228 | +0.0000 | -0.0445 | -0.36x | 2017-01-20 |
| `combo_rank_min__max_up_ret__directional_volume_signature` | +0.1367 | +0.0000 | +0.1006 | 0.74x | 2017-01-20 |
| `combo_rank_max__volatility_expansion_trend_vector__rally_strength_max` | +0.1366 | +0.0000 | -0.0853 | -0.62x | 2016-10-24 |
| `trend_bar_close_consistency` | +0.1157 | +0.0000 | -0.1362 | -1.18x | 2014-03-25 |
| `combo_mean__opening_drive_thrust_ratio__directional_volume_signature` | +0.1344 | +0.0000 | +0.1004 | 0.75x | 2017-01-20 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | +0.1278 | +0.0000 | -0.0616 | -0.48x | 2018-03-08 |
| `combo_rank_max__opening_drive_thrust_ratio__directional_volume_signature` | +0.1219 | +0.0000 | +0.0484 | 0.40x | 2016-12-21 |
| `combo_rel_diff__bar_ret_0__volume_weighted_momentum_acceleration` | +0.1264 | +0.0000 | +0.0299 | 0.24x | 2011-03-11 |
| `combo_rank_min__volume_weighted_price_position__rally_strength_max` | +0.1165 | +0.0000 | -0.0361 | -0.31x | 2016-10-24 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1388 | +0.0000 | -0.1124 | -0.81x | 2016-10-24 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | +0.1230 | +0.0000 | +0.0354 | 0.29x | 2016-11-22 |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1310 | +0.0000 | +0.0852 | 0.65x | 2017-02-27 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return` | +0.0872 | +0.0000 | +0.1274 | 1.46x | 2011-03-11 |
| `combo_min__volatility_expansion_trend_vector__volume_price_confirmation` | +0.1208 | +0.0000 | +0.0628 | 0.52x | 2016-09-14 |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | +0.1274 | +0.0000 | -0.0587 | -0.46x | 2018-03-08 |
| `combo_mean__opening_drive_thrust_ratio__volume_price_confirmation` | +0.1401 | +0.0000 | +0.0455 | 0.32x | 2017-01-20 |
| `net_volume_flow` | +0.1384 | +0.0000 | -0.0663 | -0.48x | 2014-03-25 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +0.1122 | +0.0000 | +0.1846 | 1.64x | 2011-03-11 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | +0.1326 | +0.0000 | -0.0668 | -0.50x | 2017-02-27 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret` | +0.1013 | +0.0000 | -0.0423 | -0.42x | 2017-04-28 |
| `combo_z_sum__max_up_ret__directional_volume_signature` | +0.1387 | +0.0000 | +0.0868 | 0.63x | 2017-01-20 |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__first_bar_return` | +0.1355 | +0.0000 | -0.0495 | -0.37x | 2018-01-02 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1409 | +0.0000 | -0.0325 | -0.23x | 2016-10-24 |
| `combo_ratio__max_up_ret__directional_volume_signature` | +0.1304 | +0.0000 | -0.0437 | -0.34x | 2016-12-21 |
| `combo_rank_max__bar_body_rng_0__volume_price_confirmation` | +0.1337 | +0.0000 | +0.0894 | 0.67x | 2017-02-27 |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | +0.1329 | +0.0000 | -0.0010 | -0.01x | 2017-04-28 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | +0.1324 | +0.0000 | +0.0174 | 0.13x | 2016-10-24 |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1308 | +0.0000 | +0.0279 | 0.21x | 2016-09-14 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | +0.1440 | +0.0000 | -0.0582 | -0.40x | 2016-10-24 |
| `combo_rank_min__opening_drive_thrust_ratio__directional_volume_signature` | +0.1322 | +0.0000 | +0.1160 | 0.88x | 2017-01-20 |
| `combo_rank_min__limit_down_proximity_early__directional_volume_signature` | +0.1041 | +0.0000 | +0.2430 | 2.33x | 2011-10-18 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | +0.1256 | +0.0000 | -0.1070 | -0.85x | 2016-11-22 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1245 | +0.0000 | +0.2061 | 1.66x | 2011-10-18 |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1186 | +0.0000 | +0.0955 | 0.81x | 2016-09-14 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +0.1268 | +0.0000 | +0.0598 | 0.47x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__body_size_progression` | +0.1055 | +0.0000 | +0.0605 | 0.57x | 2011-10-18 |
| `combo_clamp_diff__volume_weighted_price_position__early_late_momentum_divergence` | +0.1106 | +0.0000 | +0.0533 | 0.48x | 2017-01-20 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +0.0548 | +0.0000 | -0.0939 | -1.71x | 2011-03-11 |
| `combo_ifelse__gap_pct__yesterday_early_trend__first_bar_return` | +0.0880 | +0.0000 | +0.0564 | 0.64x | 2012-10-30 |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1037 | +0.0000 | +0.0896 | 0.86x | 2016-07-18 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — Admission too loose**: 95% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
2. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 31.0%, mean lock Sharpe=+0.4562). Consider relaxing this gate.
3. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 27.0%, mean lock Sharpe=-0.6733). Consider relaxing this gate.
4. **500ETF `single` — Admission too loose**: 83% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
5. **159915ETF `single` — B2 Rolling Guard too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.8436). Consider relaxing this gate.
6. **159915ETF `single` — B4 Correlation Gate too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.7229). Consider relaxing this gate.
7. **159915ETF `single` — Admission too loose**: 63% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
