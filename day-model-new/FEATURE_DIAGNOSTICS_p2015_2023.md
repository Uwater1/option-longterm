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

### 300ETF — `single` (Full Model Lockbox IC: +0.0744, Sharpe: +0.2534)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1188 | +0.0703 | +0.0703 | +0.3240 | 0.90 | 1/8 | 0.73 | 0.73 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0000 | +0.0546 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1225 | +0.0632 | +0.0632 | +0.3639 | 0.84 | 1/8 | 0.61 | 0.56 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0003 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1132 | +0.0876 | +0.0876 | +0.7186 | 0.79 | 1/8 | 0.71 | 0.71 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0005 | -0.0038 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1156 | +0.0706 | +0.0706 | +0.8555 | 0.84 | 1/8 | 0.59 | 0.47 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0000 | -0.0440 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1119 | +0.0543 | +0.0543 | +0.3473 | 0.77 | 1/8 | 0.75 | 0.80 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0006 | +0.0362 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1165 | +0.0622 | +0.0622 | +0.2186 | 0.80 | 1/8 | 0.69 | 0.76 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0006 | +0.0110 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1193 | +0.0723 | +0.0723 | +0.4930 | 0.81 | 1/8 | 0.63 | 0.72 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0001 | +0.0261 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1187 | +0.0756 | +0.0756 | +0.5654 | 0.70 | 0/8 | 0.53 | 0.48 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0001 | -0.0226 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1235 | +0.0694 | +0.0694 | +0.4182 | 0.60 | 0/8 | 0.61 | 0.70 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0003 | +0.0110 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` | Intraday Range Momentum | +1 | +0.1109 | +0.0619 | +0.0619 | +0.4938 | 0.83 | 1/8 | 0.66 | 0.65 | `limit_down_proximity_early` (1.45) | -0.0006 | +0.0110 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0917 | +0.0524 | +0.0524 | +0.2193 | 0.65 | 1/8 | 0.63 | 0.92 | `volume_weighted_price_position` (1.18) | +0.0005 | +0.0404 |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0958 | +0.0524 | +0.0524 | +0.3920 | 0.99 | 1/8 | 1.21 | 1.26 | `morning_volume_weighted_momentum` (2.01) | +0.0003 | +0.0569 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1131 | +0.0588 | +0.0588 | +0.3446 | 0.77 | 1/8 | 0.69 | 0.81 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0003 | +0.0362 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1222 | +0.0660 | +0.0660 | +0.4096 | 0.63 | 1/8 | 0.62 | 0.77 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0005 | +0.0362 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0965 | +0.0662 | +0.0662 | +0.0044 | 1.02 | 1/8 | 0.66 | 0.75 | — | -0.0008 | -0.2165 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1197 | +0.0682 | +0.0682 | +0.3507 | 0.57 | 0/8 | 0.59 | 0.70 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0001 | +0.0362 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1091 | +0.0640 | +0.0640 | +0.4387 | 0.84 | 1/8 | 0.70 | 0.74 | `rbreaker_buy_setup_proximity_early` (1.45) | -0.0005 | +0.0546 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0872 | +0.0567 | +0.0567 | +0.4294 | 0.84 | 1/8 | 0.72 | 1.37 | `volume_weighted_price_position` (1.18) | +0.0004 | -0.0397 |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1111 | +0.0742 | +0.0742 | +0.1837 | 1.00 | 1/8 | 0.68 | 0.63 | `star50_limit_proximity_early` (1.09) | +0.0001 | +0.0546 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1232 | +0.0678 | +0.0678 | +0.5240 | 0.69 | 1/8 | 0.64 | 0.70 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0005 | +0.0110 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0941 | +0.0566 | +0.0566 | +0.3084 | 0.79 | 1/8 | 0.51 | 1.10 | `volume_weighted_price_position` (1.18) | +0.0001 | -0.0397 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.0963 | +0.0520 | +0.0520 | +0.6190 | 0.62 | 0/8 | 0.54 | 0.81 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0000 | +0.0759 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0995 | +0.0761 | +0.0761 | +0.8091 | 0.82 | 1/8 | 0.76 | 1.03 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0000 | +0.0741 |
| `combo_max__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0944 | +0.0572 | +0.0572 | -0.0542 | 0.62 | 0/8 | 0.61 | 0.88 | `bar_body_rng_0` (0.69) | +0.0003 | -0.0040 |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0980 | +0.0637 | +0.0637 | +0.1613 | 0.73 | 1/8 | 0.64 | 1.11 | `volume_weighted_price_position` (1.18) | +0.0005 | -0.0397 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0912 | +0.0592 | +0.0592 | +0.4308 | 0.68 | 1/8 | 0.57 | 0.87 | `max_up_ret` (0.90) | -0.0001 | +0.0194 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1034 | +0.0675 | +0.0675 | +0.3265 | 0.91 | 1/8 | 0.62 | 0.62 | `rbreaker_buy_setup_proximity_early` (1.45) | -0.0001 | +0.0506 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0811 | +0.0540 | +0.0540 | +0.0387 | 0.80 | 0/8 | 0.87 | 1.95 | `volume_weighted_price_position` (1.18) | +0.0006 | -0.0040 |
| `combo_tri_max__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0902 | +0.0538 | +0.0538 | -0.2305 | 0.72 | 1/8 | 0.63 | 1.35 | `volume_weighted_price_position` (1.18) | +0.0005 | -0.0440 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0754 | +0.0521 | +0.0521 | +0.3504 | 0.88 | 0/8 | 0.86 | 1.55 | `volume_weighted_price_position` (1.18) | +0.0003 | -0.0040 |
| `star50_limit_proximity_early` | Other Technical | +1 | +0.0915 | +0.0606 | +0.0606 | +0.0343 | 1.09 | 1/8 | 0.76 | 0.81 | — | -0.0006 | +0.0110 |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | Volatility & Oscillators | +1 | +0.0840 | +0.0368 | +0.0368 | -0.3026 | 0.73 | 1/8 | 0.58 | 1.10 | `volume_surge_max` (1.98) | -0.0000 | +0.0000 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0893 | +0.0587 | +0.0587 | +0.5249 | 0.66 | 0/8 | 0.57 | 0.82 | `max_up_ret` (0.90) | +0.0004 | +0.0279 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1074 | +0.0839 | +0.0839 | +0.6572 | 0.81 | 1/8 | 0.70 | 0.60 | `star50_limit_proximity_early` (1.09) | +0.0005 | +0.0322 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0910 | +0.0843 | +0.0843 | +0.7153 | 0.82 | 1/8 | 0.86 | 0.71 | `rbreaker_buy_setup_proximity_early` (1.45) | +0.0006 | -0.0156 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0660 | +0.0417 | +0.0417 | -0.0329 | 0.79 | 1/8 | 1.45 | 1.93 | `limit_down_proximity_early` (1.45) | -0.0003 | +0.0281 |
| `combo_tri_mean__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0947 | +0.0629 | +0.0629 | +0.5008 | 0.72 | 1/8 | 0.60 | 1.05 | `volume_weighted_price_position` (1.18) | +0.0008 | -0.0040 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1169 | +0.0677 | +0.0677 | +0.2304 | 0.66 | 1/8 | 0.62 | 0.68 | `rbreaker_buy_setup_proximity_early` (1.45) | -0.0003 | +0.0110 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.0893 | +0.0684 | +0.0684 | +0.5896 | 0.87 | 1/8 | 0.67 | 0.76 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0001 | +0.0741 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0967 | +0.0573 | +0.0573 | +0.1800 | 0.78 | 0/8 | 0.68 | 1.16 | `max_up_ret` (0.90) | -0.0002 | +0.0194 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early` | Intraday Range Momentum | +1 | +0.1047 | +0.0708 | +0.0708 | +0.5931 | 0.77 | 1/8 | 0.66 | 0.50 | `rbreaker_buy_setup_proximity_early` (1.45) | -0.0002 | +0.0362 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0935 | +0.0596 | +0.0596 | +0.0022 | 0.71 | 0/8 | 0.69 | 1.02 | `max_up_ret` (0.90) | +0.0003 | -0.0040 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | Volatility & Oscillators | +1 | +0.0745 | +0.0521 | +0.0521 | +0.5457 | 0.73 | 1/8 | 0.58 | 0.88 | `volume_surge_max` (1.98) | +0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.0898 | +0.0448 | +0.0448 | -0.2936 | 0.91 | 2/8 | 0.70 | 0.95 | `max_up_ret` (0.90) | -0.0006 | +0.0194 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | Intraday Range Momentum | +1 | +0.0763 | +0.0560 | +0.0560 | +0.4156 | 0.87 | 2/8 | 0.74 | 0.87 | `volume_concentration` (1.15) | +0.0000 | +0.0741 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Intraday Range Momentum | +1 | +0.1044 | +0.0743 | +0.0743 | +0.6390 | 0.72 | 0/8 | 0.50 | 0.45 | `rbreaker_buy_setup_proximity_early` (1.45) | -0.0001 | +0.0574 |
| `combo_sig_product__first_bar_return__morning_volume_weighted_momentum` | Gap / Overnight Reversal | +1 | +0.0835 | +0.0290 | +0.0290 | -0.2006 | 0.84 | 1/8 | 0.49 | 0.71 | `morning_volume_weighted_momentum` (2.01) | -0.0001 | +0.0270 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1108, Sharpe: +0.7168)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1753 | +0.1101 | +0.1101 | +0.8958 | 0.50 | 0/8 | 0.56 | 0.40 | `opening_drive_thrust_ratio` (0.42) | +0.0004 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1884 | +0.1089 | +0.1089 | +0.4243 | 0.42 | 0/8 | 0.58 | 0.50 | `star50_limit_proximity_early` (0.61) | +0.0002 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | Other Technical | +1 | +0.1524 | +0.0889 | +0.0889 | +0.2828 | 0.47 | 0/8 | 0.59 | 0.54 | `trend_day_regime_conviction` (0.44) | -0.0001 | +0.0000 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1749 | +0.0869 | +0.0869 | +0.4098 | 0.39 | 0/8 | 0.61 | 0.51 | `body_size_progression` (0.64) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1760 | +0.1061 | +0.1061 | +0.5929 | 0.38 | 0/8 | 0.53 | 0.50 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1929 | +0.1034 | +0.1034 | +0.3676 | 0.36 | 0/8 | 0.53 | 0.52 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1418 | +0.1152 | +0.1152 | +1.1416 | 0.47 | 0/8 | 0.52 | 0.49 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0004 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1682 | +0.0993 | +0.0993 | +0.3094 | 0.42 | 0/8 | 0.66 | 0.63 | — | +0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1672 | +0.1050 | +0.1050 | +0.3978 | 0.39 | 0/8 | 0.60 | 0.51 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1503 | +0.1126 | +0.1126 | +1.0957 | 0.33 | 0/8 | 0.74 | 0.66 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1624 | +0.0992 | +0.0992 | +0.5697 | 0.47 | 0/8 | 0.51 | 0.39 | `star50_limit_proximity_early` (0.61) | +0.0003 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1603 | +0.1205 | +0.1205 | +0.6397 | 0.52 | 0/8 | 0.63 | 0.48 | `star50_limit_proximity_early` (0.61) | +0.0003 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1713 | +0.1053 | +0.1053 | +0.6127 | 0.40 | 0/8 | 0.63 | 0.55 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1701 | +0.1132 | +0.1132 | +0.2639 | 0.36 | 0/8 | 0.66 | 0.61 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1709 | +0.0779 | +0.0779 | +0.1500 | 0.49 | 0/8 | 0.50 | 0.42 | `late_bar_momentum` (0.70) | +0.0002 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1848 | +0.0977 | +0.0977 | +0.3280 | 0.37 | 0/8 | 0.57 | 0.64 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1544 | +0.1215 | +0.1215 | +0.9205 | 0.53 | 0/8 | 0.69 | 0.52 | `star50_limit_proximity_early` (0.61) | +0.0002 | +0.0000 |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1596 | +0.0727 | +0.0727 | +0.1480 | 0.37 | 0/8 | 0.57 | 0.70 | `bar_ret_0` (0.41) | -0.0001 | +0.0000 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1842 | +0.0934 | +0.0934 | +0.7611 | 0.43 | 0/8 | 0.64 | 0.60 | `volume_weighted_momentum_acceleration` (0.57) | +0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1873 | +0.0851 | +0.0851 | +0.2287 | 0.33 | 0/8 | 0.63 | 0.79 | `opening_drive_thrust_ratio` (0.42) | +0.0000 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1646 | +0.1026 | +0.1026 | +0.4610 | 0.40 | 0/8 | 0.59 | 0.65 | `trend_day_regime_conviction` (0.44) | +0.0001 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1535 | +0.1004 | +0.1004 | +0.6046 | 0.41 | 0/8 | 0.66 | 0.62 | `close_vs_open_range` (0.47) | +0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1711 | +0.0913 | +0.0913 | +0.8496 | 0.50 | 0/8 | 0.52 | 0.34 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | +0.0000 |
| `combo_min__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1456 | +0.0799 | +0.0799 | +0.7594 | 0.40 | 0/8 | 0.51 | 0.57 | `first_bar_return` (0.41) | +0.0002 | -0.0007 |
| `combo_tri_mean__max_up_ret__net_volume_flow__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1764 | +0.1040 | +0.1040 | +0.6683 | 0.34 | 0/8 | 0.59 | 0.56 | `star50_limit_proximity_early` (0.61) | +0.0002 | +0.0000 |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1271 | +0.0873 | +0.0873 | +0.3829 | 0.58 | 0/8 | 0.66 | 0.38 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1765 | +0.1015 | +0.1015 | +0.6089 | 0.36 | 0/8 | 0.52 | 0.42 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0000 | +0.0000 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1804 | +0.0946 | +0.0946 | +0.8755 | 0.40 | 0/8 | 0.70 | 0.68 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1764 | +0.0959 | +0.0959 | +0.8981 | 0.51 | 0/8 | 0.51 | 0.37 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0000 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1683 | +0.1261 | +0.1261 | +0.9460 | 0.47 | 0/8 | 0.55 | 0.52 | `demark_setup_reversal_early` (0.64) | +0.0003 | +0.0000 |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1817 | +0.0933 | +0.0933 | +0.5494 | 0.43 | 0/8 | 0.67 | 0.58 | `smooth_momentum_structure` (0.60) | +0.0002 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1580 | +0.0933 | +0.0933 | -0.0259 | 0.45 | 0/8 | 0.82 | 0.64 | `smooth_momentum_structure` (0.60) | +0.0003 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1585 | +0.0823 | +0.0823 | +0.1403 | 0.49 | 0/8 | 0.51 | 0.40 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1689 | +0.1267 | +0.1267 | +0.8006 | 0.47 | 0/8 | 0.55 | 0.50 | `demark_setup_reversal_early` (0.64) | +0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1484 | +0.1175 | +0.1175 | +0.4851 | 0.42 | 0/8 | 0.58 | 0.52 | `close_vs_open_range` (0.47) | +0.0000 | +0.0000 |
| `combo_max__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1650 | +0.0820 | +0.0820 | +0.4153 | 0.46 | 0/8 | 0.52 | 0.53 | `max_down_ret` (0.60) | +0.0000 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1531 | +0.1166 | +0.1166 | +0.9210 | 0.39 | 0/8 | 0.62 | 0.68 | `opening_drive_thrust_ratio` (0.42) | +0.0002 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1626 | +0.0934 | +0.0934 | +0.2455 | 0.49 | 0/8 | 0.73 | 0.54 | `body_size_progression` (0.64) | +0.0002 | +0.0000 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1754 | +0.0911 | +0.0911 | +0.5122 | 0.43 | 0/8 | 0.58 | 0.48 | `body_size_progression` (0.64) | +0.0002 | +0.0000 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1660 | +0.1224 | +0.1224 | +0.8206 | 0.42 | 0/8 | 0.57 | 0.49 | `demark_setup_reversal_early` (0.64) | +0.0001 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1207 | +0.1199 | +0.1199 | +1.1425 | 0.56 | 0/8 | 0.55 | 0.43 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1545 | +0.1086 | +0.1086 | +0.4017 | 0.42 | 0/8 | 0.56 | 0.51 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1750 | +0.0893 | +0.0893 | +0.5003 | 0.42 | 0/8 | 0.58 | 0.50 | `body_size_progression` (0.64) | +0.0001 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1763 | +0.1217 | +0.1217 | +0.8196 | 0.44 | 0/8 | 0.60 | 0.39 | `opening_drive_thrust_ratio` (0.42) | +0.0003 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1776 | +0.1177 | +0.1177 | +0.6330 | 0.45 | 0/8 | 0.61 | 0.46 | `opening_drive_thrust_ratio` (0.42) | +0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1687 | +0.0974 | +0.0974 | +0.8110 | 0.39 | 0/8 | 0.61 | 0.56 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_min__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1552 | +0.1077 | +0.1077 | +0.1595 | 0.45 | 0/8 | 0.63 | 0.61 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1226 | +0.0908 | +0.0908 | +0.2900 | 0.58 | 0/8 | 0.70 | 0.45 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1631 | +0.0814 | +0.0814 | +0.5897 | 0.42 | 0/8 | 0.48 | 0.46 | `bar_body_rng_0` (0.36) | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1546 | +0.1052 | +0.1052 | +0.4585 | 0.33 | 0/8 | 0.57 | 0.51 | `early_body_momentum` (0.37) | +0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__rsi_opening` | Volatility & Oscillators | +1 | +0.1351 | +0.0993 | +0.0993 | +0.7283 | 0.41 | 0/8 | 0.69 | 0.81 | `rsi_opening` (0.47) | +0.0000 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1596 | +0.1096 | +0.1096 | +0.7682 | 0.43 | 0/8 | 0.64 | 0.56 | `star50_limit_proximity_early` (0.61) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1602 | +0.0884 | +0.0884 | +0.4616 | 0.41 | 0/8 | 0.54 | 0.61 | `smooth_momentum_structure` (0.60) | +0.0001 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1401 | +0.0836 | +0.0836 | +0.2749 | 0.40 | 0/8 | 0.73 | 0.65 | `close_vs_open_range` (0.47) | -0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1639 | +0.0928 | +0.0928 | +0.0552 | 0.32 | 0/8 | 0.55 | 0.68 | `bar_ret_0` (0.41) | -0.0000 | -0.0007 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1639 | +0.0830 | +0.0830 | +0.2163 | 0.36 | 0/8 | 0.52 | 0.65 | `bar_ret_0` (0.41) | -0.0000 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1595 | +0.0936 | +0.0936 | +0.0056 | 0.47 | 0/8 | 0.61 | 0.50 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_mean__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1709 | +0.0854 | +0.0854 | +0.4811 | 0.35 | 0/8 | 0.54 | 0.66 | `bar_ret_0` (0.41) | +0.0001 | +0.0000 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1744 | +0.0908 | +0.0908 | +0.4830 | 0.36 | 0/8 | 0.51 | 0.56 | `bar_body_rng_0` (0.36) | +0.0001 | +0.0000 |
| `combo_rank_min__first_bar_return__close_vs_open_range` | Gap / Overnight Reversal | +1 | +0.1185 | +0.0969 | +0.0969 | +0.6560 | 0.52 | 0/8 | 0.44 | 0.35 | `close_vs_open_range` (0.47) | +0.0002 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1616 | +0.0960 | +0.0960 | +0.3514 | 0.34 | 0/8 | 0.63 | 0.72 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1317 | +0.1205 | +0.1205 | +1.2069 | 0.47 | 0/8 | 0.72 | 0.60 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1701 | +0.0954 | +0.0954 | +0.5296 | 0.39 | 0/8 | 0.58 | 0.49 | `opening_drive_thrust_ratio` (0.42) | +0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1782 | +0.1136 | +0.1136 | +0.4793 | 0.44 | 0/8 | 0.59 | 0.48 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1447 | +0.0976 | +0.0976 | +0.9250 | 0.54 | 0/8 | 0.56 | 0.35 | `star50_limit_proximity_early` (0.61) | +0.0003 | +0.0000 |
| `combo_mean__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1425 | +0.0916 | +0.0916 | +0.6450 | 0.41 | 0/8 | 0.56 | 0.48 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1533 | +0.0835 | +0.0835 | +0.1550 | 0.31 | 0/8 | 0.63 | 0.63 | `volatility_expansion_trend_vector` (0.41) | -0.0002 | -0.0007 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1458 | +0.0948 | +0.0948 | +0.9751 | 0.54 | 0/8 | 0.55 | 0.34 | `star50_limit_proximity_early` (0.61) | +0.0003 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1490 | +0.0982 | +0.0982 | +0.2007 | 0.30 | 0/8 | 0.74 | 0.85 | `opening_drive_thrust_ratio` (0.42) | +0.0000 | +0.0000 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1511 | +0.1141 | +0.1141 | +0.8262 | 0.34 | 0/8 | 0.71 | 0.72 | `volatility_expansion_trend_vector` (0.41) | +0.0001 | +0.0000 |
| `combo_mean__early_body_momentum__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1313 | +0.0923 | +0.0923 | +0.4385 | 0.36 | 0/8 | 0.60 | 0.54 | `star50_limit_proximity_early` (0.61) | -0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1725 | +0.1040 | +0.1040 | +1.0270 | 0.47 | 0/8 | 0.49 | 0.45 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1685 | +0.1045 | +0.1045 | +0.5644 | 0.35 | 0/8 | 0.53 | 0.51 | `star50_limit_proximity_early` (0.61) | +0.0002 | +0.0000 |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | Intraday Range Momentum | +1 | +0.1518 | +0.0818 | +0.0818 | +0.2746 | 0.46 | 0/8 | 0.46 | 0.55 | `volatility_expansion_trend_vector` (0.41) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1410 | +0.1134 | +0.1134 | +0.8964 | 0.36 | 0/8 | 0.59 | 0.67 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | +0.0000 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1629 | +0.0993 | +0.0993 | +0.6878 | 0.41 | 0/8 | 0.73 | 0.74 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0000 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1269 | +0.0958 | +0.0958 | +0.2125 | 0.61 | 0/8 | 0.58 | 0.47 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | Intraday Range Momentum | +1 | +0.1574 | +0.0880 | +0.0880 | +0.4480 | 0.40 | 0/8 | 0.60 | 0.62 | `opening_drive_thrust_ratio` (0.42) | -0.0000 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1641 | +0.0977 | +0.0977 | +0.5571 | 0.37 | 0/8 | 0.63 | 0.71 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1580 | +0.1117 | +0.1117 | +0.9540 | 0.41 | 0/8 | 0.51 | 0.43 | `close_vs_open_range` (0.47) | +0.0000 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.2012 | +0.1108 | +0.1108 | +0.6987 | 0.36 | 0/8 | 0.56 | 0.53 | `opening_drive_thrust_ratio` (0.42) | +0.0001 | +0.0000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1590 | +0.0908 | +0.0908 | +0.7297 | 0.41 | 0/8 | 0.78 | 0.81 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1598 | +0.1078 | +0.1078 | +0.7630 | 0.37 | 0/8 | 0.54 | 0.49 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1720 | +0.1216 | +0.1216 | +0.9299 | 0.41 | 0/8 | 0.60 | 0.46 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | +0.0000 |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | Other Technical | +1 | +0.1403 | +0.0897 | +0.0897 | +0.6542 | 0.37 | 0/8 | 0.63 | 0.56 | `h2_l2_pullback_continuation` (0.47) | +0.0002 | +0.0064 |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | Gap / Overnight Reversal | +1 | +0.1311 | +0.0714 | +0.0714 | -0.1819 | 0.36 | 0/8 | 0.57 | 0.54 | `h2_l2_pullback_continuation` (0.47) | +0.0000 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1351 | +0.1018 | +0.1018 | +0.4421 | 0.41 | 0/8 | 0.67 | 0.63 | `close_vs_open_range` (0.47) | +0.0001 | +0.0000 |
| `combo_mean__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1170 | +0.0911 | +0.0911 | +0.3935 | 0.36 | 0/8 | 0.66 | 0.76 | `close_vs_open_range` (0.47) | -0.0001 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1258 | +0.0906 | +0.0906 | +0.2518 | 0.59 | 0/8 | 0.59 | 0.41 | `star50_limit_proximity_early` (0.61) | +0.0000 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1815 | +0.1039 | +0.1039 | +0.7125 | 0.37 | 0/8 | 0.59 | 0.50 | `star50_limit_proximity_early` (0.61) | +0.0002 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1590 | +0.0922 | +0.0922 | +0.9091 | 0.50 | 0/8 | 0.62 | 0.44 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_max__first_bar_return__close_vs_open_range` | Gap / Overnight Reversal | +1 | +0.1634 | +0.0794 | +0.0794 | +0.2412 | 0.32 | 0/8 | 0.62 | 0.73 | `close_vs_open_range` (0.47) | -0.0001 | +0.0000 |
| `combo_rank_min__close_vs_open_range__vwap_close_divergence_trend` | Other Technical | +1 | +0.1086 | +0.0881 | +0.0881 | +0.3843 | 0.43 | 0/8 | 0.70 | 0.73 | `vwap_close_divergence_trend` (0.50) | +0.0000 | +0.0000 |
| `combo_rank_min__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1420 | +0.0764 | +0.0764 | +0.1600 | 0.39 | 0/8 | 0.53 | 0.47 | `bar_ret_0` (0.41) | +0.0001 | -0.0007 |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1420 | +0.0843 | +0.0843 | -0.2363 | 0.41 | 0/8 | 0.85 | 1.23 | `early_order_flow_imbalance` (0.67) | -0.0000 | +0.0000 |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1361 | +0.0805 | +0.0805 | -0.0723 | 0.35 | 0/8 | 0.56 | 0.57 | `h2_l2_pullback_continuation` (0.47) | +0.0001 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1429 | +0.1153 | +0.1153 | +1.1001 | 0.40 | 0/8 | 0.58 | 0.58 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | +0.0000 |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | Other Technical | +1 | +0.1082 | +0.0900 | +0.0900 | +0.2723 | 0.43 | 0/8 | 0.73 | 0.80 | `vwap_close_divergence_trend` (0.50) | +0.0001 | +0.0000 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1097 | +0.0918 | +0.0918 | +0.6021 | 0.39 | 0/8 | 0.58 | 0.60 | `close_vs_open_range` (0.47) | -0.0001 | +0.0000 |
| `combo_mean__net_volume_flow__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1415 | +0.0894 | +0.0894 | +0.7399 | 0.34 | 0/8 | 0.60 | 0.65 | `bar_body_rng_0` (0.36) | -0.0001 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | Other Technical | +1 | +0.1240 | +0.1061 | +0.1061 | +0.5479 | 0.51 | 0/8 | 0.60 | 0.50 | `trend_bar_close_consistency` (0.66) | +0.0002 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1643 | +0.0953 | +0.0953 | +0.5051 | 0.44 | 0/8 | 0.64 | 0.60 | `close_vs_open_range` (0.47) | -0.0000 | +0.0000 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1769 | +0.1311 | +0.1311 | +0.9144 | 0.43 | 0/8 | 0.53 | 0.47 | `demark_setup_reversal_early` (0.64) | +0.0003 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1542 | +0.0906 | +0.0906 | +0.4864 | 0.48 | 0/8 | 0.83 | 0.66 | `smooth_momentum_structure` (0.60) | +0.0001 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1619 | +0.0920 | +0.0920 | +0.4322 | 0.33 | 0/8 | 0.57 | 0.66 | — | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1588 | +0.1062 | +0.1062 | +0.6289 | 0.40 | 0/8 | 0.55 | 0.51 | `h2_l2_pullback_continuation` (0.47) | +0.0002 | +0.0064 |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1543 | +0.0893 | +0.0893 | +0.2451 | 0.45 | 0/8 | 0.53 | 0.38 | `vwap_close_divergence_trend` (0.50) | +0.0000 | +0.0000 |
| `combo_max__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1553 | +0.0789 | +0.0789 | +0.3856 | 0.43 | 0/8 | 0.55 | 0.51 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_min__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1279 | +0.0962 | +0.0962 | +0.7432 | 0.37 | 0/8 | 0.62 | 0.66 | `bar_ret_0` (0.41) | +0.0001 | +0.0000 |
| `combo_tri_median__trend_bar_close_consistency__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1499 | +0.0970 | +0.0970 | +0.4794 | 0.40 | 0/8 | 0.54 | 0.51 | `trend_bar_close_consistency` (0.66) | +0.0001 | +0.0000 |
| `combo_mean__trend_day_regime_conviction__bar_ret_0` | Other Technical | +1 | +0.1408 | +0.0886 | +0.0886 | +0.3333 | 0.38 | 0/8 | 0.57 | 0.66 | `trend_day_regime_conviction` (0.44) | +0.0001 | +0.0000 |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.1107 | +0.0907 | +0.0907 | +0.8442 | 0.68 | 0/8 | 0.66 | 0.42 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1501 | +0.0813 | +0.0813 | +0.4751 | 0.42 | 0/8 | 0.53 | 0.56 | `early_body_momentum` (0.37) | -0.0001 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1799 | +0.0913 | +0.0913 | +0.4100 | 0.36 | 0/8 | 0.61 | 0.77 | `opening_drive_thrust_ratio` (0.42) | +0.0000 | +0.0000 |
| `combo_mean__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1285 | +0.0937 | +0.0937 | +0.2553 | 0.41 | 0/8 | 0.64 | 0.56 | `max_down_ret` (0.60) | +0.0000 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1801 | +0.0893 | +0.0893 | -0.0123 | 0.42 | 0/8 | 0.50 | 0.51 | `star50_limit_proximity_early` (0.61) | -0.0001 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1436 | +0.0872 | +0.0872 | +0.0379 | 0.48 | 0/8 | 0.69 | 0.97 | `early_order_flow_imbalance` (0.67) | +0.0000 | -0.0346 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1305 | +0.0933 | +0.0933 | +0.4158 | 0.71 | 0/8 | 0.46 | 0.31 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1708 | +0.0922 | +0.0922 | -0.1324 | 0.40 | 0/8 | 0.48 | 0.62 | `star50_limit_proximity_early` (0.61) | -0.0001 | +0.0000 |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.0984 | +0.1041 | +0.1041 | +1.3062 | 0.53 | 0/8 | 0.54 | 0.48 | `trend_bar_close_consistency` (0.66) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1411 | +0.1178 | +0.1178 | +0.8065 | 0.44 | 0/8 | 0.54 | 0.53 | `close_vs_open_range` (0.47) | +0.0002 | +0.0000 |
| `combo_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1641 | +0.0798 | +0.0798 | +0.5993 | 0.39 | 0/8 | 0.53 | 0.54 | `bar_ret_0` (0.41) | +0.0003 | +0.0000 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | Intraday Range Momentum | +1 | +0.1501 | +0.0841 | +0.0841 | +0.4215 | 0.39 | 0/8 | 0.54 | 0.73 | `trend_bar_close_consistency` (0.66) | +0.0000 | +0.0000 |
| `combo_max__early_body_momentum__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1433 | +0.0715 | +0.0715 | +0.4327 | 0.28 | 0/8 | 0.63 | 0.60 | `early_body_momentum` (0.37) | -0.0002 | -0.0007 |
| `combo_rank_min__max_down_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1278 | +0.0988 | +0.0988 | +0.2415 | 0.58 | 0/8 | 0.56 | 0.33 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_sig_product__early_body_momentum__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1013 | +0.0775 | +0.0775 | +0.1341 | 0.41 | 0/8 | 0.68 | 0.67 | `close_vs_open_range` (0.47) | -0.0001 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | Other Technical | +1 | +0.1696 | +0.0961 | +0.0961 | +0.6661 | 0.37 | 0/8 | 0.55 | 0.51 | `trend_day_regime_conviction` (0.44) | +0.0002 | +0.0000 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Other Technical | +1 | +0.1054 | +0.0829 | +0.0829 | +0.4277 | 0.52 | 0/8 | 0.47 | 0.59 | `trend_bar_close_consistency` (0.66) | +0.0000 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1611 | +0.1002 | +0.1002 | +0.2632 | 0.45 | 0/8 | 0.67 | 0.57 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1457 | +0.0699 | +0.0699 | +0.4640 | 0.41 | 0/8 | 0.52 | 0.50 | — | +0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1787 | +0.0774 | +0.0774 | +0.0400 | 0.36 | 0/8 | 0.66 | 0.80 | `opening_drive_thrust_ratio` (0.42) | -0.0001 | +0.0000 |
| `combo_sig_product__max_down_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.0945 | +0.0608 | +0.0608 | -0.1007 | 0.51 | 0/8 | 0.78 | 0.47 | `max_down_ret` (0.60) | +0.0000 | +0.0064 |
| `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | Gap / Overnight Reversal | +1 | +0.1604 | +0.0777 | +0.0777 | +0.5035 | 0.49 | 0/8 | 0.63 | 0.50 | `early_late_momentum_divergence` (0.70) | +0.0000 | +0.0000 |
| `combo_mean__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1624 | +0.1024 | +0.1024 | +0.7530 | 0.43 | 0/8 | 0.57 | 0.66 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | Other Technical | +1 | +0.1380 | +0.0864 | +0.0864 | +0.7260 | 0.38 | 0/8 | 0.67 | 0.61 | `h2_l2_pullback_continuation` (0.47) | +0.0001 | +0.0000 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1606 | +0.0831 | +0.0831 | +0.2070 | 0.42 | 0/8 | 0.58 | 0.54 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_tri_max__max_up_ret__early_body_momentum__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1447 | +0.0781 | +0.0781 | +0.6799 | 0.40 | 0/8 | 0.51 | 0.53 | `trend_day_regime_conviction` (0.44) | +0.0000 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1389 | +0.0987 | +0.0987 | +0.5514 | 0.42 | 0/8 | 0.61 | 0.67 | `opening_drive_thrust_ratio` (0.42) | +0.0003 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1691 | +0.0976 | +0.0976 | +0.4983 | 0.37 | 0/8 | 0.53 | 0.54 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1764 | +0.0954 | +0.0954 | +0.3172 | 0.35 | 0/8 | 0.64 | 0.74 | `opening_drive_thrust_ratio` (0.42) | +0.0002 | -0.0007 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1256 | +0.1048 | +0.1048 | +0.9028 | 0.39 | 0/8 | 0.57 | 0.60 | `trend_bar_close_consistency` (0.66) | +0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1354 | +0.0873 | +0.0873 | +0.2699 | 0.45 | 0/8 | 0.64 | 0.75 | `trend_bar_close_consistency` (0.66) | -0.0001 | +0.0000 |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.1033 | +0.0749 | +0.0749 | +0.6891 | 0.37 | 0/8 | 0.64 | 0.65 | `h2_l2_pullback_continuation` (0.47) | -0.0000 | +0.0000 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1489 | +0.1058 | +0.1058 | +1.1405 | 0.42 | 0/8 | 0.56 | 0.59 | `volume_weighted_momentum_acceleration` (0.57) | +0.0003 | +0.0000 |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1219 | +0.0788 | +0.0788 | +0.4742 | 0.42 | 0/8 | 0.99 | 1.69 | `early_order_flow_imbalance` (0.67) | +0.0000 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1760 | +0.1040 | +0.1040 | -0.0012 | 0.45 | 0/8 | 0.56 | 0.47 | `star50_limit_proximity_early` (0.61) | -0.0000 | +0.0000 |
| `combo_tri_min__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1211 | +0.1097 | +0.1097 | +0.9163 | 0.47 | 0/8 | 0.62 | 0.52 | `star50_limit_proximity_early` (0.61) | +0.0003 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1676 | +0.0791 | +0.0791 | +0.4862 | 0.35 | 0/8 | 0.60 | 0.68 | `opening_drive_thrust_ratio` (0.42) | +0.0000 | +0.0000 |
| `combo_max__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1366 | +0.0709 | +0.0709 | +0.1776 | 0.42 | 0/8 | 0.66 | 0.81 | `early_order_flow_imbalance` (0.67) | -0.0001 | +0.0000 |
| `combo_mean__first_bar_return__close_vs_open_range` | Gap / Overnight Reversal | +1 | +0.1498 | +0.0936 | +0.0936 | +0.3680 | 0.38 | 0/8 | 0.55 | 0.60 | `close_vs_open_range` (0.47) | +0.0002 | +0.0000 |
| `combo_min__early_order_flow_imbalance__max_down_ret` | Intraday Range Momentum | +1 | +0.1169 | +0.0695 | +0.0695 | +0.4002 | 0.45 | 0/8 | 1.14 | 1.30 | `early_order_flow_imbalance` (0.67) | +0.0001 | -0.0346 |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | Intraday Range Momentum | +1 | +0.1378 | +0.1064 | +0.1064 | +0.7637 | 0.32 | 0/8 | 0.63 | 0.77 | `volatility_expansion_trend_vector` (0.41) | +0.0003 | +0.0000 |
| `combo_min__first_bar_return__close_vs_open_range` | Gap / Overnight Reversal | +1 | +0.1185 | +0.0979 | +0.0979 | +0.4302 | 0.51 | 0/8 | 0.45 | 0.36 | `close_vs_open_range` (0.47) | +0.0003 | +0.0000 |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1439 | +0.0745 | +0.0745 | +0.2995 | 0.42 | 0/8 | 0.62 | 0.77 | `early_order_flow_imbalance` (0.67) | -0.0001 | +0.0000 |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1310 | +0.0815 | +0.0815 | +0.6738 | 0.34 | 0/8 | 0.60 | 0.60 | `h2_l2_pullback_continuation` (0.47) | +0.0002 | +0.0070 |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.1011 | +0.0781 | +0.0781 | +0.7031 | 0.38 | 0/8 | 0.61 | 0.61 | `h2_l2_pullback_continuation` (0.47) | +0.0001 | +0.0064 |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1503 | +0.0825 | +0.0825 | +0.1565 | 0.50 | 0/8 | 0.44 | 0.49 | `star50_limit_proximity_early` (0.61) | -0.0000 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1437 | +0.0950 | +0.0950 | +0.3896 | 0.35 | 0/8 | 0.74 | 0.85 | `opening_drive_thrust_ratio` (0.42) | +0.0000 | +0.0000 |
| `combo_rank_max__trend_day_regime_conviction__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1001 | +0.0704 | +0.0704 | -0.0750 | 0.43 | 0/8 | 0.98 | 1.39 | `early_order_flow_imbalance` (0.67) | -0.0002 | +0.0000 |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1599 | +0.0960 | +0.0960 | +0.7037 | 0.40 | 0/8 | 0.76 | 0.78 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0000 |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1522 | +0.0840 | +0.0840 | +0.4024 | 0.30 | 0/8 | 0.64 | 0.68 | `vwap_close_divergence_trend` (0.50) | +0.0000 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.1145 | +0.0933 | +0.0933 | +0.5933 | 0.68 | 0/8 | 0.69 | 0.49 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | Volatility & Oscillators | +1 | +0.0998 | +0.0719 | +0.0719 | -0.1114 | 0.38 | 0/8 | 0.94 | 1.62 | `early_order_flow_imbalance` (0.67) | -0.0000 | +0.0000 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1243 | +0.1013 | +0.1013 | +0.6416 | 0.37 | 0/8 | 0.60 | 0.69 | `close_vs_open_range` (0.47) | +0.0002 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1422 | +0.0869 | +0.0869 | +0.5783 | 0.40 | 0/8 | 0.75 | 0.71 | `opening_drive_thrust_ratio` (0.42) | -0.0001 | +0.0000 |
| `combo_mean__max_down_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1278 | +0.0920 | +0.0920 | +0.5487 | 0.52 | 0/8 | 0.58 | 0.42 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_min__max_down_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1254 | +0.0988 | +0.0988 | +0.0640 | 0.56 | 0/8 | 0.56 | 0.39 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1683 | +0.1249 | +0.1249 | +0.4168 | 0.46 | 0/8 | 0.63 | 0.54 | `demark_setup_reversal_early` (0.64) | +0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1783 | +0.0961 | +0.0961 | +0.2777 | 0.35 | 0/8 | 0.57 | 0.65 | `star50_limit_proximity_early` (0.61) | +0.0000 | +0.0000 |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | Other Technical | +1 | +0.1041 | +0.1088 | +0.1088 | +0.9778 | 0.61 | 0/8 | 0.57 | 0.49 | `trend_bar_close_consistency` (0.66) | +0.0002 | +0.0000 |
| `combo_max__early_body_momentum__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1020 | +0.0793 | +0.0793 | +0.1117 | 0.43 | 0/8 | 0.57 | 0.74 | `close_vs_open_range` (0.47) | -0.0001 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1609 | +0.0938 | +0.0938 | +0.0240 | 0.40 | 0/8 | 0.48 | 0.59 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0000 | +0.0000 |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1381 | +0.0420 | +0.0420 | -0.5395 | 0.37 | 0/8 | 0.78 | 0.67 | `vwap_close_divergence_trend` (0.50) | -0.0001 | +0.0000 |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1456 | +0.0733 | +0.0733 | +0.0937 | 0.34 | 0/8 | 0.81 | 1.21 | `early_order_flow_imbalance` (0.67) | -0.0001 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.1439 | +0.1064 | +0.1064 | +0.4728 | 0.47 | 0/8 | 0.54 | 0.49 | `star50_limit_proximity_early` (0.61) | +0.0000 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1453 | +0.0954 | +0.0954 | +0.5791 | 0.51 | 0/8 | 0.66 | 0.54 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1444 | +0.0841 | +0.0841 | +0.2138 | 0.56 | 0/8 | 0.57 | 0.48 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0064 |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | Other Technical | +1 | +0.1116 | +0.0833 | +0.0833 | +0.2334 | 0.46 | 0/8 | 0.57 | 0.60 | `close_vs_open_range` (0.47) | -0.0000 | +0.0000 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1793 | +0.1257 | +0.1257 | +0.9262 | 0.43 | 0/8 | 0.56 | 0.55 | `demark_setup_reversal_early` (0.64) | +0.0000 | +0.0000 |
| `combo_min__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1327 | +0.0836 | +0.0836 | +0.2902 | 0.50 | 0/8 | 0.52 | 0.35 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1687 | +0.1257 | +0.1257 | +0.4863 | 0.49 | 0/8 | 0.62 | 0.52 | `demark_setup_reversal_early` (0.64) | +0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1297 | +0.0753 | +0.0753 | -0.0440 | 0.36 | 0/8 | 1.09 | 1.62 | `early_order_flow_imbalance` (0.67) | +0.0000 | +0.0000 |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | Other Technical | +1 | +0.1438 | +0.0958 | +0.0958 | +0.6571 | 0.40 | 0/8 | 0.55 | 0.54 | `close_vs_open_range` (0.47) | -0.0000 | +0.0000 |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1333 | +0.0942 | +0.0942 | +0.4728 | 0.39 | 0/8 | 0.73 | 1.01 | `vwap_close_divergence_trend` (0.50) | +0.0000 | +0.0000 |
| `combo_max__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1562 | +0.0991 | +0.0991 | +0.1521 | 0.37 | 0/8 | 0.51 | 0.53 | `star50_limit_proximity_early` (0.61) | -0.0000 | +0.0000 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1611 | +0.0854 | +0.0854 | +0.4781 | 0.39 | 0/8 | 0.57 | 0.58 | `close_vs_open_range` (0.47) | -0.0002 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1578 | +0.1017 | +0.1017 | +0.4703 | 0.28 | 0/8 | 0.51 | 0.55 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | +0.0000 |
| `max_down_ret` | Intraday Range Momentum | +1 | +0.1248 | +0.0828 | +0.0828 | +0.1693 | 0.60 | 0/8 | 0.61 | 0.36 | — | +0.0001 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1416 | +0.1238 | +0.1238 | +0.1525 | 0.63 | 0/8 | 0.50 | 0.36 | `demark_setup_reversal_early` (0.64) | +0.0002 | +0.0000 |
| `combo_max__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1489 | +0.0731 | +0.0731 | -0.3903 | 0.34 | 0/8 | 0.58 | 0.67 | `first_bar_return` (0.41) | -0.0000 | +0.0000 |
| `combo_rank_max__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1510 | +0.0744 | +0.0744 | +0.0795 | 0.31 | 0/8 | 0.58 | 0.68 | `bar_ret_0` (0.41) | -0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1565 | +0.1262 | +0.1262 | +0.5466 | 0.50 | 1/8 | 0.72 | 0.45 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1537 | +0.0894 | +0.0894 | +0.4449 | 0.30 | 0/8 | 0.65 | 0.69 | `vwap_close_divergence_trend` (0.50) | -0.0000 | +0.0000 |
| `combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.0743 | -0.0030 | -0.0030 | +0.5284 | 1.00 | 2/8 | 0.95 | 0.85 | `shaved_bar_trend_conviction` (1.17) | +0.0003 | +0.0000 |
| `combo_diff__first_bar_return__early_late_momentum_divergence` | Gap / Overnight Reversal | +1 | +0.1589 | +0.0786 | +0.0786 | +0.4874 | 0.49 | 0/8 | 0.63 | 0.52 | `early_late_momentum_divergence` (0.70) | +0.0001 | +0.0000 |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1321 | +0.0778 | +0.0778 | +0.1204 | 0.34 | 0/8 | 0.59 | 0.60 | `h2_l2_pullback_continuation` (0.47) | +0.0001 | +0.0064 |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.1504 | +0.0805 | +0.0805 | +0.2751 | 0.47 | 0/8 | 0.54 | 0.58 | `shaved_bar_trend_conviction` (1.17) | +0.0000 | +0.0064 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1454 | +0.1031 | +0.1031 | +0.6726 | 0.41 | 0/8 | 0.57 | 0.41 | `body_size_progression` (0.64) | +0.0001 | +0.0000 |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | Other Technical | +1 | +0.1344 | +0.0828 | +0.0828 | -0.1066 | 0.32 | 0/8 | 0.56 | 0.53 | `h2_l2_pullback_continuation` (0.47) | +0.0000 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1705 | +0.1101 | +0.1101 | +0.4988 | 0.48 | 0/8 | 0.53 | 0.46 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1117 | +0.0934 | +0.0934 | +0.4880 | 0.40 | 0/8 | 0.61 | 0.71 | `smooth_momentum_structure` (0.60) | -0.0001 | +0.0000 |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1213 | +0.0782 | +0.0782 | +0.6383 | 0.45 | 1/8 | 1.08 | 1.97 | `early_order_flow_imbalance` (0.67) | +0.0001 | -0.0346 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1485 | +0.0871 | +0.0871 | +0.9219 | 0.55 | 0/8 | 0.67 | 0.52 | `early_late_momentum_divergence` (0.70) | +0.0002 | +0.0000 |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | Intraday Range Momentum | +1 | +0.1199 | +0.0695 | +0.0695 | -0.0684 | 0.42 | 0/8 | 1.03 | 0.91 | `early_order_flow_imbalance` (0.67) | +0.0001 | +0.0000 |
| `combo_rank_max__early_body_momentum__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1067 | +0.0820 | +0.0820 | +0.6056 | 0.40 | 0/8 | 0.59 | 0.71 | `close_vs_open_range` (0.47) | -0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.1304 | +0.0972 | +0.0972 | +0.3472 | 0.53 | 0/8 | 0.64 | 0.60 | `vwap_close_divergence_trend` (0.50) | +0.0002 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Other Technical | +1 | +0.1547 | +0.0844 | +0.0844 | -0.1714 | 0.40 | 0/8 | 0.69 | 0.81 | `vwap_close_divergence_trend` (0.50) | -0.0001 | +0.0000 |
| `combo_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1283 | +0.1011 | +0.1011 | +0.4084 | 0.33 | 0/8 | 0.63 | 0.78 | `close_vs_open_range` (0.47) | +0.0001 | +0.0000 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1142 | +0.0697 | +0.0697 | +0.4152 | 0.23 | 0/8 | 0.89 | 0.80 | `max_down_ret` (0.60) | +0.0000 | +0.0064 |
| `combo_rank_max__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1673 | +0.0865 | +0.0865 | +0.7342 | 0.44 | 0/8 | 0.54 | 0.59 | `max_down_ret` (0.60) | +0.0000 | +0.0000 |
| `combo_rank_max__early_body_momentum__max_down_ret` | Intraday Range Momentum | +1 | +0.1203 | +0.0776 | +0.0776 | +0.4425 | 0.46 | 0/8 | 0.57 | 0.62 | `max_down_ret` (0.60) | -0.0001 | +0.0000 |
| `combo_max__bar_ret_0__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1216 | +0.0535 | +0.0535 | -0.4023 | 0.41 | 0/8 | 0.64 | 0.77 | `early_order_flow_imbalance` (0.67) | -0.0001 | +0.0000 |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | Gap / Overnight Reversal | +1 | +0.1280 | +0.0687 | +0.0687 | +0.0726 | 0.40 | 0/8 | 0.84 | 1.30 | `early_order_flow_imbalance` (0.67) | +0.0000 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend` | Other Technical | +1 | +0.1224 | +0.0912 | +0.0912 | +0.0122 | 0.44 | 0/8 | 0.77 | 0.83 | `vwap_close_divergence_trend` (0.50) | +0.0001 | +0.0000 |
| `combo_tri_median__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | Intraday Range Momentum | +1 | +0.1115 | +0.0809 | +0.0809 | +0.3003 | 0.39 | 0/8 | 0.65 | 0.85 | `trend_day_regime_conviction` (0.44) | -0.0000 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1057 | +0.0837 | +0.0837 | +0.5987 | 0.75 | 0/8 | 0.34 | 0.08 | `shaved_bar_trend_conviction` (1.17) | -0.0003 | +0.0000 |
| `combo_rank_min__early_order_flow_imbalance__close_vs_open_range` | Volatility & Oscillators | +1 | +0.0971 | +0.0779 | +0.0779 | +0.2912 | 0.39 | 0/8 | 0.83 | 1.49 | `early_order_flow_imbalance` (0.67) | -0.0000 | +0.0000 |
| `combo_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1616 | +0.0860 | +0.0860 | +0.4491 | 0.40 | 0/8 | 0.56 | 0.56 | `close_vs_open_range` (0.47) | +0.0000 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1616 | +0.0904 | +0.0904 | +0.2926 | 0.34 | 0/8 | 0.50 | 0.53 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1405 | +0.1178 | +0.1178 | +0.8307 | 0.62 | 0/8 | 0.53 | 0.36 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_rel_diff__net_volume_flow__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.1055 | +0.0737 | +0.0737 | +0.4824 | 0.31 | 0/8 | 0.69 | 0.74 | `h2_l2_pullback_continuation` (0.47) | +0.0000 | +0.0000 |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | Other Technical | +1 | +0.1321 | +0.0830 | +0.0830 | +0.0754 | 0.33 | 0/8 | 0.56 | 0.55 | `h2_l2_pullback_continuation` (0.47) | +0.0003 | +0.0064 |
| `combo_sig_product__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1002 | +0.0726 | +0.0726 | +0.6092 | 0.37 | 0/8 | 0.70 | 0.57 | `max_down_ret` (0.60) | +0.0001 | +0.0064 |
| `combo_rel_diff__bar_ret_0__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1489 | +0.0672 | +0.0672 | +0.3283 | 0.59 | 0/8 | 0.52 | 0.41 | `late_bar_momentum` (0.70) | +0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1202 | +0.1041 | +0.1041 | +0.8851 | 0.46 | 0/8 | 0.52 | 0.56 | `trend_bar_close_consistency` (0.66) | +0.0001 | +0.0000 |
| `combo_rank_min__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1444 | +0.0995 | +0.0995 | +0.1901 | 0.51 | 0/8 | 0.57 | 0.41 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1276 | +0.0797 | +0.0797 | +0.2390 | 0.55 | 0/8 | 0.48 | 0.27 | `max_down_ret` (0.60) | +0.0000 | +0.0000 |
| `combo_mean__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1503 | +0.0939 | +0.0939 | +0.7756 | 0.37 | 0/8 | 0.58 | 0.65 | `close_vs_open_range` (0.47) | +0.0001 | +0.0000 |
| `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0` | Intraday Range Momentum | +1 | +0.1399 | +0.0649 | +0.0649 | +0.3923 | 0.36 | 0/8 | 0.51 | 0.60 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0000 |
| `combo_max__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1223 | +0.0851 | +0.0851 | -0.0023 | 0.42 | 0/8 | 0.56 | 0.49 | `max_down_ret` (0.60) | -0.0002 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1820 | +0.1064 | +0.1064 | +0.4742 | 0.37 | 0/8 | 0.56 | 0.49 | `opening_drive_thrust_ratio` (0.42) | -0.0000 | +0.0000 |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.1425 | +0.0806 | +0.0806 | +0.2085 | 0.53 | 0/8 | 0.52 | 0.46 | `shaved_bar_trend_conviction` (1.17) | -0.0000 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1556 | +0.0872 | +0.0872 | +0.7049 | 0.52 | 0/8 | 0.77 | 0.59 | `body_size_progression` (0.64) | +0.0001 | +0.0000 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1432 | +0.0990 | +0.0990 | +0.5523 | 0.47 | 0/8 | 0.52 | 0.51 | `star50_limit_proximity_early` (0.61) | -0.0000 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0926 | +0.1048 | +0.1048 | +1.1248 | 0.90 | 1/8 | 0.41 | 0.06 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | Intraday Range Momentum | +1 | +0.1162 | +0.0811 | +0.0811 | +0.2779 | 0.59 | 1/8 | 0.65 | 0.73 | `early_order_flow_imbalance` (0.67) | -0.0001 | +0.0000 |
| `combo_rank_min__trend_bar_close_consistency__max_down_ret` | Intraday Range Momentum | +1 | +0.1068 | +0.0855 | +0.0855 | +0.2616 | 0.66 | 0/8 | 0.52 | 0.30 | `trend_bar_close_consistency` (0.66) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Intraday Range Momentum | +1 | +0.1404 | +0.0932 | +0.0932 | +0.0468 | 0.42 | 0/8 | 0.55 | 0.53 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1183 | +0.0951 | +0.0951 | +0.2989 | 0.62 | 1/8 | 0.37 | 0.29 | `volume_weighted_momentum_acceleration` (0.57) | -0.0000 | +0.0064 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1418 | +0.0889 | +0.0889 | +0.4280 | 0.42 | 0/8 | 0.72 | 0.81 | `opening_drive_thrust_ratio` (0.42) | -0.0003 | +0.0000 |
| `combo_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.0902 | +0.0653 | +0.0653 | +0.0097 | 0.36 | 0/8 | 0.92 | 1.30 | `early_order_flow_imbalance` (0.67) | -0.0000 | +0.0064 |
| `combo_rel_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.0862 | +0.0619 | +0.0619 | +0.0984 | 0.42 | 0/8 | 1.07 | 1.64 | `early_order_flow_imbalance` (0.67) | -0.0000 | +0.0000 |
| `combo_max__max_down_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1253 | +0.0831 | +0.0831 | +0.3714 | 0.52 | 0/8 | 0.61 | 0.47 | `max_down_ret` (0.60) | -0.0000 | +0.0000 |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | Other Technical | +1 | +0.0956 | +0.0746 | +0.0746 | +0.6466 | 0.45 | 0/8 | 0.60 | 0.54 | `h2_l2_pullback_continuation` (0.47) | +0.0001 | +0.0064 |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.1351 | +0.1258 | +0.1258 | +0.8365 | 0.56 | 0/8 | 0.43 | 0.32 | `shaved_bar_trend_conviction` (1.17) | +0.0000 | -0.0172 |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1161 | +0.0885 | +0.0885 | +0.1366 | 0.42 | 0/8 | 0.76 | 1.13 | `vwap_close_divergence_trend` (0.50) | +0.0001 | +0.0000 |
| `combo_min__max_up_ret__rsi_opening` | Intraday Range Momentum | +1 | +0.1291 | +0.0971 | +0.0971 | +0.6507 | 0.31 | 0/8 | 0.67 | 0.95 | `rsi_opening` (0.47) | +0.0001 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1649 | +0.0963 | +0.0963 | +0.3050 | 0.46 | 0/8 | 0.52 | 0.47 | `star50_limit_proximity_early` (0.61) | -0.0001 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1428 | +0.1220 | +0.1220 | +0.3484 | 0.61 | 0/8 | 0.50 | 0.38 | `demark_setup_reversal_early` (0.64) | +0.0003 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | Intraday Range Momentum | +1 | +0.1253 | +0.0788 | +0.0788 | -0.0583 | 0.45 | 0/8 | 0.53 | 0.68 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0064 |
| `combo_min__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1372 | +0.0736 | +0.0736 | +0.2013 | 0.39 | 0/8 | 1.09 | 2.13 | `early_order_flow_imbalance` (0.67) | +0.0000 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1361 | +0.0851 | +0.0851 | +0.6624 | 0.59 | 1/8 | 0.82 | 0.84 | `volume_weighted_momentum_acceleration` (0.57) | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1581 | +0.1030 | +0.1030 | -0.1287 | 0.39 | 0/8 | 0.87 | 1.21 | `early_order_flow_imbalance` (0.67) | +0.0001 | -0.0346 |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | Volatility & Oscillators | +1 | +0.1090 | +0.0864 | +0.0864 | +0.4303 | 0.38 | 0/8 | 0.77 | 1.07 | `vwap_close_divergence_trend` (0.50) | -0.0001 | +0.0000 |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1222 | +0.0833 | +0.0833 | +0.2002 | 0.51 | 0/8 | 0.64 | 0.65 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_z_sum__vwap_close_divergence_trend__bar_body_rng_0` | Other Technical | +1 | +0.1428 | +0.0883 | +0.0883 | +0.1362 | 0.34 | 0/8 | 0.62 | 0.67 | `vwap_close_divergence_trend` (0.50) | +0.0000 | +0.0000 |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1131 | +0.0801 | +0.0801 | +0.5713 | 0.60 | 0/8 | 0.56 | 0.42 | `vwap_close_divergence_trend` (0.50) | +0.0001 | +0.0000 |
| `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1416 | +0.1246 | +0.1246 | +0.3320 | 0.61 | 0/8 | 0.49 | 0.35 | `demark_setup_reversal_early` (0.64) | +0.0001 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1441 | +0.0905 | +0.0905 | +0.7330 | 0.45 | 0/8 | 0.49 | 0.51 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0000 | +0.0000 |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1277 | +0.0573 | +0.0573 | -0.2389 | 0.39 | 0/8 | 0.63 | 0.75 | `early_order_flow_imbalance` (0.67) | -0.0002 | +0.0000 |
| `combo_rank_max__trend_bar_close_consistency__star50_limit_proximity_early` | Other Technical | +1 | +0.1280 | +0.0839 | +0.0839 | +0.3605 | 0.62 | 0/8 | 0.49 | 0.50 | `trend_bar_close_consistency` (0.66) | +0.0001 | +0.0000 |
| `combo_sig_product__rsi_opening__h2_l2_pullback_continuation` | Volatility & Oscillators | +1 | +0.1008 | +0.0727 | +0.0727 | +0.1402 | 0.41 | 0/8 | 0.49 | 0.50 | `rsi_opening` (0.47) | +0.0000 | +0.0064 |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1070 | +0.0757 | +0.0757 | +0.5266 | 0.48 | 0/8 | 0.59 | 0.45 | `max_down_ret` (0.60) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0926 | +0.0952 | +0.0952 | +1.1424 | 0.90 | 1/8 | 0.31 | 0.00 | `shaved_bar_trend_conviction` (1.17) | +0.0001 | -0.0172 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1369 | +0.1223 | +0.1223 | +0.4818 | 0.39 | 0/8 | 0.73 | 0.83 | `star50_limit_proximity_early` (0.61) | +0.0002 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1057 | +0.0820 | +0.0820 | +0.6587 | 0.66 | 0/8 | 0.39 | 0.31 | `star50_limit_proximity_early` (0.61) | +0.0000 | +0.0064 |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1496 | +0.0950 | +0.0950 | +0.1326 | 0.37 | 0/8 | 0.56 | 0.42 | `star50_limit_proximity_early` (0.61) | -0.0001 | +0.0000 |
| `combo_sig_product__bar_ret_0__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1256 | +0.0619 | +0.0619 | -0.1117 | 0.45 | 0/8 | 0.66 | 0.88 | `early_order_flow_imbalance` (0.67) | -0.0001 | -0.0346 |
| `combo_sig_product__early_order_flow_imbalance__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.0859 | +0.0945 | +0.0945 | +0.6559 | 0.84 | 1/8 | 1.32 | 2.58 | `early_order_flow_imbalance` (0.67) | +0.0000 | +0.0000 |
| `combo_rank_max__trend_day_regime_conviction__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0926 | +0.0777 | +0.0777 | +0.0427 | 0.67 | 0/8 | 0.51 | 0.39 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0064 |
| `combo_mean__early_order_flow_imbalance__max_down_ret` | Intraday Range Momentum | +1 | +0.1086 | +0.0717 | +0.0717 | +0.0640 | 0.50 | 1/8 | 0.95 | 1.11 | `early_order_flow_imbalance` (0.67) | -0.0000 | +0.0000 |
| `combo_mean__net_volume_flow__shaved_bar_trend_conviction` | Volatility & Oscillators | +1 | +0.0965 | +0.0770 | +0.0770 | +0.7110 | 0.55 | 0/8 | 0.53 | 0.48 | `shaved_bar_trend_conviction` (1.17) | -0.0002 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1530 | +0.0729 | +0.0729 | +0.0143 | 0.43 | 0/8 | 0.86 | 1.32 | `opening_drive_thrust_ratio` (0.42) | -0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1003 | +0.0975 | +0.0975 | +1.0302 | 0.82 | 1/8 | 0.34 | 0.07 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1440 | +0.0695 | +0.0695 | +0.0693 | 0.45 | 0/8 | 0.53 | 0.57 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1082 | +0.0814 | +0.0814 | +0.6836 | 0.50 | 0/8 | 0.56 | 0.39 | `max_down_ret` (0.60) | +0.0002 | +0.0064 |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1503 | +0.0812 | +0.0812 | -0.0084 | 0.25 | 0/8 | 0.67 | 0.90 | `vwap_close_divergence_trend` (0.50) | -0.0001 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1248 | +0.0789 | +0.0789 | +0.2580 | 0.51 | 0/8 | 0.51 | 0.62 | `volume_weighted_momentum_acceleration` (0.57) | +0.0000 | +0.0064 |
| `combo_max__close_vs_open_range__bar_body_rng_0` | Other Technical | +1 | +0.1514 | +0.0858 | +0.0858 | +0.4695 | 0.30 | 0/8 | 0.68 | 0.64 | `close_vs_open_range` (0.47) | -0.0002 | +0.0000 |
| `combo_abs_diff__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.0754 | +0.0360 | +0.0360 | -0.5187 | 0.96 | 2/8 | 0.77 | 0.27 | `shaved_bar_trend_conviction` (1.17) | +0.0002 | +0.0064 |
| `combo_diff__net_volume_flow__demark_setup_reversal_early` | Volatility & Oscillators | +1 | +0.1452 | +0.1198 | +0.1198 | +0.7584 | 0.43 | 0/8 | 0.63 | 0.67 | `demark_setup_reversal_early` (0.64) | +0.0001 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1535 | +0.0977 | +0.0977 | +0.3369 | 0.30 | 0/8 | 0.53 | 0.45 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0000 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1603 | +0.0792 | +0.0792 | +0.3953 | 0.43 | 0/8 | 0.52 | 0.66 | `bar_ret_0` (0.41) | +0.0001 | +0.0000 |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1083 | +0.0788 | +0.0788 | +0.5668 | 0.49 | 0/8 | 0.56 | 0.38 | `max_down_ret` (0.60) | +0.0001 | +0.0064 |
| `combo_max__early_body_momentum__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.0947 | +0.0585 | +0.0585 | -0.0383 | 0.41 | 0/8 | 1.06 | 1.73 | `early_order_flow_imbalance` (0.67) | -0.0002 | +0.0000 |
| `combo_rank_min__close_vs_open_range__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0872 | +0.0723 | +0.0723 | +0.6918 | 0.68 | 0/8 | 0.41 | 0.29 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_min__trend_bar_close_consistency__max_down_ret` | Intraday Range Momentum | +1 | +0.0976 | +0.0870 | +0.0870 | +0.2373 | 0.60 | 0/8 | 0.54 | 0.43 | `trend_bar_close_consistency` (0.66) | +0.0000 | +0.0000 |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1398 | +0.0978 | +0.0978 | +0.2106 | 0.43 | 0/8 | 0.54 | 0.52 | `star50_limit_proximity_early` (0.61) | -0.0002 | +0.0000 |
| `combo_rank_max__max_down_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1247 | +0.0837 | +0.0837 | +0.5254 | 0.51 | 0/8 | 0.60 | 0.53 | `max_down_ret` (0.60) | -0.0000 | +0.0000 |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0778 | +0.0741 | +0.0741 | +0.5169 | 0.66 | 0/8 | 0.53 | 0.43 | `shaved_bar_trend_conviction` (1.17) | -0.0000 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1328 | +0.0840 | +0.0840 | +0.6202 | 0.46 | 0/8 | 0.48 | 0.46 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0002 | +0.0000 |
| `combo_min__max_down_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.0882 | +0.0768 | +0.0768 | +0.2589 | 0.98 | 2/8 | 0.38 | -0.04 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_ratio__bar_ret_0__net_volume_flow` | Volatility & Oscillators | +1 | +0.1119 | +0.0500 | +0.0500 | +0.3938 | 0.52 | 0/8 | 0.53 | 0.67 | `bar_ret_0` (0.41) | +0.0000 | +0.0000 |
| `combo_rel_diff__net_volume_flow__demark_setup_reversal_early` | Volatility & Oscillators | +1 | +0.1409 | +0.1192 | +0.1192 | +0.7283 | 0.43 | 0/8 | 0.60 | 0.66 | `demark_setup_reversal_early` (0.64) | +0.0002 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1373 | +0.0857 | +0.0857 | +0.4571 | 0.49 | 0/8 | 0.66 | 0.76 | `trend_bar_close_consistency` (0.66) | -0.0000 | +0.0000 |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0752 | +0.0736 | +0.0736 | +0.4467 | 0.72 | 0/8 | 0.46 | 0.39 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_tri_max__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | Volatility & Oscillators | +1 | +0.1566 | +0.0881 | +0.0881 | +0.0286 | 0.34 | 0/8 | 0.54 | 0.62 | `star50_limit_proximity_early` (0.61) | -0.0001 | +0.0000 |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | Other Technical | +1 | +0.1029 | +0.0802 | +0.0802 | -0.3656 | 0.42 | 0/8 | 0.74 | 0.87 | `vwap_close_divergence_trend` (0.50) | -0.0001 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1648 | +0.0875 | +0.0875 | +0.7974 | 0.42 | 0/8 | 0.50 | 0.47 | `opening_drive_thrust_ratio` (0.42) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1208 | +0.1053 | +0.1053 | -0.3095 | 0.74 | 0/8 | 0.40 | 0.50 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_rel_diff__early_order_flow_imbalance__demark_setup_reversal_early` | Volatility & Oscillators | +1 | +0.1336 | +0.1089 | +0.1089 | +0.2476 | 0.45 | 0/8 | 0.78 | 1.01 | `early_order_flow_imbalance` (0.67) | +0.0002 | +0.0000 |
| `combo_max__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1502 | +0.0811 | +0.0811 | -0.0987 | 0.25 | 0/8 | 0.68 | 0.94 | `vwap_close_divergence_trend` (0.50) | -0.0000 | +0.0000 |
| `combo_max__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1469 | +0.1001 | +0.1001 | +0.2217 | 0.50 | 0/8 | 0.50 | 0.42 | `star50_limit_proximity_early` (0.61) | -0.0002 | +0.0000 |
| `combo_min__close_vs_open_range__bar_body_rng_0` | Other Technical | +1 | +0.1224 | +0.0936 | +0.0936 | +0.3042 | 0.51 | 0/8 | 0.45 | 0.42 | `close_vs_open_range` (0.47) | +0.0002 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1086 | +0.0849 | +0.0849 | +0.4967 | 0.58 | 0/8 | 0.54 | 0.40 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_rank_max__max_down_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1163 | +0.0836 | +0.0836 | +0.3480 | 0.48 | 0/8 | 0.66 | 0.79 | `max_down_ret` (0.60) | -0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1407 | +0.1051 | +0.1051 | +0.4203 | 0.57 | 0/8 | 0.52 | 0.44 | `star50_limit_proximity_early` (0.61) | +0.0001 | +0.0000 |
| `combo_min__max_up_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.0913 | +0.0707 | +0.0707 | +0.3479 | 0.63 | 0/8 | 0.32 | 0.40 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_sig_product__volatility_expansion_trend_vector__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1116 | +0.0499 | +0.0499 | -0.2163 | 0.53 | 1/8 | 1.09 | 3.38 | `early_order_flow_imbalance` (0.67) | -0.0001 | -0.0346 |
| `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1395 | +0.1075 | +0.1075 | +0.3795 | 0.41 | 0/8 | 0.76 | 0.72 | `shaved_bar_trend_conviction` (1.17) | -0.0000 | -0.0172 |
| `combo_sig_product__opening_drive_thrust_ratio__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1231 | +0.0657 | +0.0657 | -0.2310 | 0.51 | 1/8 | 0.94 | 1.57 | `early_order_flow_imbalance` (0.67) | -0.0002 | -0.0346 |
| `early_body_momentum` | Intraday Range Momentum | +1 | +0.0917 | +0.0713 | +0.0713 | -0.2871 | 0.37 | 0/8 | 0.69 | 1.06 | — | -0.0001 | +0.0000 |
| `combo_mean__close_vs_open_range__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0872 | +0.0758 | +0.0758 | +0.1990 | 0.71 | 0/8 | 0.45 | 0.28 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.0991 | +0.0839 | +0.0839 | +0.1758 | 0.52 | 0/8 | 0.73 | 0.93 | — | +0.0000 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | Other Technical | +1 | +0.1532 | +0.0961 | +0.0961 | +0.4422 | 0.46 | 0/8 | 0.51 | 0.42 | `trend_day_regime_conviction` (0.44) | +0.0000 | +0.0000 |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | Other Technical | +1 | +0.1257 | +0.0877 | +0.0877 | +0.2021 | 0.48 | 0/8 | 0.58 | 0.63 | `vwap_close_divergence_trend` (0.50) | +0.0001 | +0.0000 |
| `combo_rank_max__max_down_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.0884 | +0.0117 | +0.0117 | -0.4010 | 0.68 | 1/8 | 0.30 | 0.06 | `max_down_ret` (0.60) | +0.0000 | +0.0000 |
| `combo_sig_product__bar_ret_0__close_vs_open_range` | Other Technical | +1 | +0.1244 | +0.0673 | +0.0673 | -0.5202 | 0.40 | 0/8 | 0.69 | 0.45 | `close_vs_open_range` (0.47) | -0.0000 | +0.0000 |
| `open_to_current_return` | Intraday Range Momentum | +1 | +0.1142 | +0.0851 | +0.0851 | +0.2899 | 0.40 | 0/8 | 0.64 | 0.90 | — | +0.0000 | +0.0000 |
| `combo_max__first_bar_return__shaved_bar_trend_conviction` | Gap / Overnight Reversal | +1 | +0.1396 | +0.0667 | +0.0667 | +0.0059 | 0.49 | 0/8 | 0.55 | 0.61 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_min__close_vs_open_range__shaved_bar_trend_conviction` | Other Technical | +1 | +0.0832 | +0.0681 | +0.0681 | +0.4679 | 0.79 | 1/8 | 0.35 | 0.19 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_mean__bar_body_rng_0__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1239 | +0.0788 | +0.0788 | +0.7732 | 0.51 | 0/8 | 0.46 | 0.41 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1217 | +0.0852 | +0.0852 | +0.4144 | 0.63 | 0/8 | 0.39 | 0.35 | `shaved_bar_trend_conviction` (1.17) | +0.0000 | +0.0000 |
| `combo_mean__max_down_ret__shaved_bar_trend_conviction` | Intraday Range Momentum | +1 | +0.0980 | +0.0768 | +0.0768 | +0.2864 | 0.76 | 0/8 | 0.45 | 0.17 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` | Other Technical | +1 | +0.0856 | +0.0692 | +0.0692 | +0.0074 | 0.49 | 0/8 | 0.76 | 1.23 | `trend_bar_close_consistency` (0.66) | -0.0001 | +0.0000 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.0947 | -0.0211 | -0.0211 | -0.4893 | 0.85 | 1/8 | 0.50 | 0.17 | `close_vs_open_range` (0.47) | -0.0001 | +0.0000 |
| `combo_min__max_down_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1357 | +0.0842 | +0.0842 | +0.6357 | 0.51 | 0/8 | 0.55 | 0.46 | `max_down_ret` (0.60) | +0.0002 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.1434 | +0.1035 | +0.1035 | +0.3387 | 0.40 | 0/8 | 0.62 | 0.54 | `vwap_close_divergence_trend` (0.50) | -0.0000 | +0.0000 |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | Other Technical | +1 | +0.1212 | +0.0798 | +0.0798 | +0.5325 | 0.59 | 0/8 | 0.39 | 0.33 | `shaved_bar_trend_conviction` (1.17) | -0.0001 | +0.0000 |
| `combo_max__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1409 | +0.0698 | +0.0698 | +0.1367 | 0.36 | 0/8 | 0.59 | 0.53 | `first_bar_return` (0.41) | +0.0000 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | Other Technical | +1 | +0.1447 | +0.1054 | +0.1054 | +0.1415 | 0.40 | 0/8 | 0.60 | 0.54 | `vwap_close_divergence_trend` (0.50) | +0.0000 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1489, Sharpe: +1.7798)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1619 | +0.1313 | +0.1313 | +1.2050 | 0.42 | 0/8 | 0.92 | 0.88 | `star50_limit_proximity_early` (0.69) | -0.0003 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0` | Other Technical | +1 | +0.1649 | +0.1211 | +0.1211 | +1.0186 | 0.46 | 1/8 | 0.95 | 0.71 | `bar_body_rng_0` (0.54) | -0.0003 | +0.0000 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1466 | +0.1045 | +0.1045 | +0.5197 | 0.46 | 0/8 | 0.95 | 0.68 | `bar_body_rng_0` (0.54) | -0.0005 | -0.0263 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1572 | +0.1181 | +0.1181 | +1.1200 | 0.39 | 0/8 | 1.06 | 0.80 | `bar_body_rng_0` (0.54) | -0.0003 | -0.0263 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Intraday Range Momentum | +1 | +0.1299 | +0.0937 | +0.0937 | +0.6050 | 0.61 | 1/8 | 1.14 | 0.91 | `yesterday_early_vwap_dev` (1.10) | +0.0007 | -0.0874 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1376 | +0.1458 | +0.1458 | +1.3138 | 0.56 | 0/8 | 1.26 | 1.00 | `star50_limit_proximity_early` (0.69) | +0.0003 | -0.0263 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1461 | +0.1423 | +0.1423 | +1.5753 | 0.57 | 1/8 | 1.24 | 0.87 | `star50_limit_proximity_early` (0.69) | +0.0002 | -0.0263 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1562 | +0.1219 | +0.1219 | +1.3598 | 0.48 | 0/8 | 0.95 | 0.87 | `star50_limit_proximity_early` (0.69) | -0.0000 | +0.0000 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1470 | +0.1365 | +0.1365 | +1.6742 | 0.68 | 1/8 | 1.17 | 0.58 | `star50_limit_proximity_early` (0.69) | +0.0004 | -0.0263 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1519 | +0.1295 | +0.1295 | +1.2978 | 0.48 | 1/8 | 1.16 | 0.98 | `opening_drive_thrust_ratio` (0.51) | -0.0002 | -0.0263 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1563 | +0.1361 | +0.1361 | +1.5551 | 0.44 | 0/8 | 0.96 | 0.87 | `star50_limit_proximity_early` (0.69) | -0.0003 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1402 | +0.1031 | +0.1031 | +0.3991 | 0.43 | 0/8 | 1.05 | 0.95 | `opening_drive_thrust_ratio` (0.51) | -0.0003 | -0.0263 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1184 | +0.1314 | +0.1314 | +1.0098 | 0.46 | 0/8 | 1.24 | 0.87 | `demark_setup_reversal_early` (0.76) | +0.0002 | -0.0270 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1438 | +0.1292 | +0.1292 | +0.9902 | 0.57 | 0/8 | 0.89 | 0.56 | `star50_limit_proximity_early` (0.69) | +0.0003 | -0.0370 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1406 | +0.0991 | +0.0991 | +0.6764 | 0.37 | 0/8 | 1.06 | 0.90 | `first_bar_return` (0.44) | -0.0005 | -0.0263 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1402 | +0.1106 | +0.1106 | +0.5865 | 0.44 | 0/8 | 0.93 | 0.87 | `opening_drive_thrust_ratio` (0.51) | -0.0005 | -0.0263 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1403 | +0.1368 | +0.1368 | +1.3236 | 0.57 | 1/8 | 1.18 | 0.88 | `star50_limit_proximity_early` (0.69) | +0.0006 | -0.0263 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1416 | +0.0960 | +0.0960 | +0.2321 | 0.35 | 0/8 | 1.04 | 0.89 | `bar_ret_0` (0.44) | -0.0003 | -0.0263 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1627 | +0.1362 | +0.1362 | +1.4190 | 0.52 | 0/8 | 0.92 | 0.56 | `bar_body_rng_0` (0.54) | -0.0001 | -0.0263 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1485 | +0.1267 | +0.1267 | +1.3544 | 0.43 | 0/8 | 1.21 | 1.13 | `gap_pct` (1.18) | +0.0001 | -0.0773 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1617 | +0.1187 | +0.1187 | +0.9375 | 0.54 | 1/8 | 0.93 | 0.65 | `rbreaker_sell_setup_proximity_early` (0.44) | -0.0003 | -0.0263 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1458 | +0.1354 | +0.1354 | +1.5192 | 0.43 | 0/8 | 1.00 | 0.79 | `opening_drive_thrust_ratio` (0.51) | -0.0002 | -0.0263 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1487 | +0.1323 | +0.1323 | +1.4436 | 0.42 | 0/8 | 1.06 | 1.04 | `star50_limit_proximity_early` (0.69) | -0.0004 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | Intraday Range Momentum | +1 | +0.0957 | +0.1094 | +0.1094 | +0.4547 | 0.75 | 1/8 | 1.32 | 1.09 | `yesterday_early_trend` (1.01) | +0.0010 | -0.0773 |
| `combo_max__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1436 | +0.0793 | +0.0793 | +1.0689 | 0.40 | 0/8 | 1.03 | 0.70 | `volume_price_confirmation` (0.61) | -0.0005 | -0.0263 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1532 | +0.1260 | +0.1260 | +1.0555 | 0.36 | 0/8 | 1.19 | 1.11 | `rbreaker_sell_setup_proximity_early` (0.44) | -0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1647 | +0.1300 | +0.1300 | +1.4067 | 0.38 | 0/8 | 1.02 | 0.78 | `rbreaker_sell_setup_proximity_early` (0.44) | +0.0000 | -0.0263 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1388 | +0.1268 | +0.1268 | +1.0353 | 0.70 | 1/8 | 1.05 | 0.61 | `star50_limit_proximity_early` (0.69) | +0.0001 | -0.0263 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1542 | +0.1208 | +0.1208 | +1.4577 | 0.52 | 1/8 | 1.11 | 0.76 | `star50_limit_proximity_early` (0.69) | -0.0002 | +0.0000 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1345 | +0.1056 | +0.1056 | +0.8986 | 0.38 | 0/8 | 1.01 | 0.88 | `volume_weighted_momentum_acceleration` (0.48) | -0.0003 | -0.0263 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1418 | +0.1273 | +0.1273 | +1.2414 | 0.47 | 0/8 | 1.20 | 0.99 | `opening_drive_thrust_ratio` (0.51) | -0.0003 | -0.0263 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | Gap / Overnight Reversal | +1 | +0.1271 | +0.0619 | +0.0619 | +0.4262 | 0.56 | 0/8 | 0.65 | 0.33 | `gap_pct` (1.18) | +0.0001 | -0.0109 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1350 | +0.1046 | +0.1046 | +0.6295 | 0.49 | 0/8 | 0.91 | 0.68 | `opening_drive_thrust_ratio` (0.51) | -0.0005 | -0.0263 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1415 | +0.1345 | +0.1345 | +1.2143 | 0.58 | 0/8 | 1.23 | 0.81 | `star50_limit_proximity_early` (0.69) | +0.0001 | -0.0263 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | Gap / Overnight Reversal | +1 | +0.1350 | +0.0519 | +0.0519 | +0.0925 | 0.53 | 0/8 | 0.50 | 0.26 | `gap_pct` (1.18) | +0.0001 | -0.0109 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1351 | +0.1228 | +0.1228 | +1.5130 | 0.54 | 0/8 | 0.85 | 0.37 | `volume_price_confirmation` (0.61) | -0.0003 | -0.0263 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1288 | +0.1129 | +0.1129 | +0.7706 | 0.54 | 0/8 | 0.99 | 0.67 | `bar_body_rng_0` (0.54) | -0.0006 | +0.0129 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1347 | +0.1086 | +0.1086 | +1.0439 | 0.35 | 0/8 | 0.92 | 0.77 | `volume_weighted_momentum_acceleration` (0.48) | -0.0003 | -0.0263 |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1357 | +0.0890 | +0.0890 | +0.8526 | 0.55 | 0/8 | 1.02 | 0.54 | `volatility_expansion_trend_vector` (0.69) | -0.0005 | -0.0263 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1315 | +0.1402 | +0.1402 | +1.1873 | 0.50 | 1/8 | 1.21 | 1.23 | `volatility_expansion_trend_vector` (0.69) | +0.0002 | -0.0263 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1194 | +0.1287 | +0.1287 | +1.6490 | 0.60 | 0/8 | 0.92 | 0.33 | `star50_limit_proximity_early` (0.69) | +0.0005 | -0.0263 |
| `combo_min__first_bar_return__limit_down_proximity_early` | Gap / Overnight Reversal | +1 | +0.1236 | +0.1216 | +0.1216 | +1.1418 | 0.76 | 1/8 | 1.10 | 0.52 | `limit_down_proximity_early` (1.06) | +0.0005 | -0.0370 |
| `combo_max__rbreaker_sell_setup_proximity_early__gap_pct` | Gap / Overnight Reversal | +1 | +0.1218 | +0.1139 | +0.1139 | +0.1910 | 0.60 | 1/8 | 1.10 | 1.22 | `gap_pct` (1.18) | +0.0001 | -0.0048 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1380 | +0.1033 | +0.1033 | +0.8765 | 0.44 | 0/8 | 0.94 | 0.70 | `bar_body_rng_0` (0.54) | -0.0004 | +0.0129 |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1340 | +0.0903 | +0.0903 | +0.6870 | 0.47 | 0/8 | 1.02 | 0.65 | `bar_body_rng_0` (0.54) | -0.0006 | -0.0263 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1297 | +0.1122 | +0.1122 | +0.9216 | 0.55 | 0/8 | 1.32 | 1.45 | `demark_setup_reversal_early` (0.76) | -0.0004 | -0.0263 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1282 | +0.1014 | +0.1014 | +0.5632 | 0.39 | 0/8 | 1.13 | 1.08 | — | -0.0002 | -0.0263 |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1228 | +0.1165 | +0.1165 | +1.0610 | 0.48 | 0/8 | 1.00 | 0.60 | `volatility_expansion_trend_vector` (0.69) | -0.0002 | -0.0263 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1153 | +0.1333 | +0.1333 | +1.3096 | 0.66 | 1/8 | 1.32 | 1.17 | `star50_limit_proximity_early` (0.69) | +0.0002 | -0.0263 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1155 | +0.1385 | +0.1385 | +1.2999 | 0.66 | 1/8 | 1.37 | 1.20 | `star50_limit_proximity_early` (0.69) | +0.0001 | -0.0263 |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.1314 | +0.1051 | +0.1051 | +0.5856 | 0.39 | 0/8 | 1.05 | 0.95 | `volatility_expansion_trend_vector` (0.69) | -0.0004 | -0.0263 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.1105 | +0.1130 | +0.1130 | +0.6257 | 0.36 | 0/8 | 0.66 | 0.62 | `keltner_squeeze_width` (0.62) | +0.0010 | -0.0510 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1261 | +0.1021 | +0.1021 | +0.7660 | 0.54 | 0/8 | 1.12 | 1.20 | `volume_weighted_price_position` (0.83) | +0.0001 | +0.0000 |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1412 | +0.0817 | +0.0817 | +0.6895 | 0.34 | 0/8 | 0.71 | 0.61 | `gap_pct` (1.18) | -0.0005 | -0.0263 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | Gap / Overnight Reversal | +1 | +0.1263 | +0.0909 | +0.0909 | +0.6701 | 0.45 | 0/8 | 0.53 | 0.29 | `gap_pct` (1.18) | +0.0004 | -0.0291 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1223 | +0.1076 | +0.1076 | +1.0604 | 0.50 | 0/8 | 1.08 | 0.69 | `early_late_momentum_divergence` (0.83) | -0.0000 | -0.0263 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1143 | +0.1176 | +0.1176 | +1.1307 | 0.51 | 0/8 | 1.21 | 0.99 | — | -0.0002 | -0.0263 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.1157 | +0.1151 | +0.1151 | +0.5953 | 0.32 | 0/8 | 0.72 | 0.70 | `keltner_squeeze_width` (0.62) | +0.0005 | -0.0195 |
| `combo_z_sum__max_up_ret__gap_pct` | Gap / Overnight Reversal | +1 | +0.1537 | +0.1357 | +0.1357 | +0.6634 | 0.41 | 0/8 | 1.18 | 1.10 | `gap_pct` (1.18) | -0.0000 | -0.0048 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.1433 | +0.1272 | +0.1272 | +0.9212 | 0.50 | 0/8 | 0.93 | 0.56 | `gap_pct` (1.18) | +0.0002 | -0.0263 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | Gap / Overnight Reversal | +1 | +0.1195 | +0.0981 | +0.0981 | +0.7118 | 0.32 | 0/8 | 0.75 | 0.52 | `gap_pct` (1.18) | +0.0005 | -0.0874 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1370 | +0.1229 | +0.1229 | +0.4385 | 0.56 | 1/8 | 1.33 | 1.44 | `rbreaker_buy_setup_proximity_early` (1.06) | +0.0002 | +0.0206 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | Gap / Overnight Reversal | +1 | +0.1220 | +0.1038 | +0.1038 | +0.3582 | 0.52 | 1/8 | 1.42 | 1.72 | `gap_pct` (1.18) | -0.0003 | -0.0773 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1182 | +0.1083 | +0.1083 | +0.5114 | 0.42 | 0/8 | 1.14 | 1.07 | `volatility_expansion_trend_vector` (0.69) | -0.0003 | -0.0263 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | Gap / Overnight Reversal | +1 | +0.1220 | +0.0701 | +0.0701 | +0.4317 | 0.43 | 0/8 | 0.87 | 0.66 | `gap_pct` (1.18) | +0.0002 | -0.0619 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Gap / Overnight Reversal | +1 | +0.1112 | +0.0822 | +0.0822 | +0.5914 | 0.29 | 0/8 | 0.81 | 0.86 | `gap_pct` (1.18) | -0.0004 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct` | Gap / Overnight Reversal | +1 | +0.1214 | +0.1197 | +0.1197 | +0.4214 | 0.55 | 1/8 | 1.12 | 1.29 | `gap_pct` (1.18) | +0.0005 | +0.0206 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.1282 | +0.1344 | +0.1344 | +0.9145 | 0.52 | 1/8 | 1.20 | 0.92 | `gap_pct` (1.18) | +0.0001 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1243 | +0.1277 | +0.1277 | +1.0889 | 0.38 | 0/8 | 1.18 | 1.34 | `rbreaker_sell_setup_proximity_early` (0.44) | +0.0002 | -0.0048 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev` | Gap / Overnight Reversal | +1 | +0.1204 | +0.0720 | +0.0720 | +0.0140 | 0.54 | 1/8 | 0.74 | 0.51 | `gap_pct` (1.18) | +0.0000 | +0.0107 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | Gap / Overnight Reversal | +1 | +0.1285 | +0.0634 | +0.0634 | +0.3043 | 0.37 | 0/8 | 0.71 | 0.51 | `gap_pct` (1.18) | +0.0001 | -0.0619 |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1212 | +0.1187 | +0.1187 | +0.7449 | 0.48 | 0/8 | 1.05 | 0.69 | `early_late_momentum_divergence` (0.83) | +0.0002 | -0.0263 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0958 | +0.1097 | +0.1097 | +0.5964 | 0.52 | 0/8 | 1.25 | 1.18 | `volatility_expansion_trend_vector` (0.69) | -0.0003 | -0.0263 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | Gap / Overnight Reversal | +1 | +0.1204 | +0.1034 | +0.1034 | +0.3154 | 0.34 | 0/8 | 0.62 | 0.44 | `gap_pct` (1.18) | +0.0001 | -0.0339 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1633 | +0.1220 | +0.1220 | +1.4110 | 0.35 | 0/8 | 1.04 | 0.88 | `volume_weighted_momentum_acceleration` (0.48) | -0.0007 | -0.0410 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1095 | +0.1090 | +0.1090 | +0.3724 | 0.66 | 0/8 | 1.03 | 1.15 | `star50_limit_proximity_early` (0.69) | -0.0000 | +0.0000 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1364 | +0.0884 | +0.0884 | +0.6934 | 0.32 | 0/8 | 0.95 | 1.05 | `gap_pct` (1.18) | -0.0005 | -0.0773 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0591 | -0.0132 | -0.0132 | -0.5256 | 0.84 | 2/8 | 0.53 | 0.98 | `volatility_expansion_trend_vector` (0.69) | +0.0000 | -0.0263 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 74.0% lock IC > 0, 41.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2479_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1212 | 30 | 100.0% | 83.3% | +0.0592 | +0.2235 |
| B2 Rolling Guard | 206 | 30 | 100.0% | 93.3% | +0.0577 | +0.3246 |
| BH-FDR Gate | 13 | 13 | 92.3% | 23.1% | +0.0337 | -0.4051 |
| B3 Composite Floor | 44 | 30 | 100.0% | 86.7% | +0.0613 | +0.2946 |
| B4 Correlation Gate | 86 | 30 | 100.0% | 96.7% | +0.0676 | +0.4623 |

**Admitted Pool Summary**: 47 features, False Positive Rate = 14.9% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0620, Mean Lock Sharpe = +0.3367

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Lock Sharpe=+0.9639
- `combo_mean__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Lock Sharpe=+0.5376
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Lock Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Lock Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.2141, Lock IC=+0.0651, Lock Sharpe=+0.4681

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Lock Sharpe=+0.7446
- `combo_tri_median__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.1758, Lock IC=+0.0545, Lock Sharpe=+0.7446
- `combo_min__bar_ret_0__bar_body_rng_0`: Train IC=+0.1635, Lock IC=+0.0604, Lock Sharpe=+0.6749
- `combo_min__first_bar_return__bar_body_rng_0`: Train IC=+0.1633, Lock IC=+0.0604, Lock Sharpe=+0.6749
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Train IC=+0.1710, Lock IC=+0.0652, Lock Sharpe=+0.5621

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1027, Lock IC=+0.0707, Lock Sharpe=+0.3328
- `combo_z_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1027, Lock IC=+0.0707, Lock Sharpe=+0.3328
- `combo_rel_diff__max_up_ret__early_late_momentum_divergence`: Train IC=+0.1028, Lock IC=+0.0730, Lock Sharpe=+0.1567

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0590, Lock Sharpe=+0.7052
- `combo_tri_z_mean__opening_drive_thrust_ratio__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0590, Lock Sharpe=+0.7052
- `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0591, Lock Sharpe=+0.7052
- `combo_tri_z_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Train IC=+0.1938, Lock IC=+0.0591, Lock Sharpe=+0.7052
- `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`: Train IC=+0.2052, Lock IC=+0.0587, Lock Sharpe=+0.5249

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2265, Lock IC=+0.0937, Lock Sharpe=+1.0629
- `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__first_bar_return`: Train IC=+0.2370, Lock IC=+0.0693, Lock Sharpe=+0.5695
- `combo_tri_z_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__first_bar_return`: Train IC=+0.2370, Lock IC=+0.0693, Lock Sharpe=+0.5695
- `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.2366, Lock IC=+0.0693, Lock Sharpe=+0.5695
- `combo_tri_z_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.2366, Lock IC=+0.0693, Lock Sharpe=+0.5695

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 28.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7016_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 539 | 30 | 73.3% | 13.3% | +0.0073 | -0.5382 |
| B2 Rolling Guard | 36 | 30 | 33.3% | 3.3% | +0.0030 | -0.4517 |
| BH-FDR Gate | 4 | 4 | 75.0% | 0.0% | -0.0046 | -0.8578 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__donchian_breakout_ratio_20d__sma100_dist`: Train IC=+0.1885, Lock IC=+0.0306, Lock Sharpe=+0.3187
- `combo_sig_product__donchian_breakout_proximity_20d__sma100_dist`: Train IC=+0.1885, Lock IC=+0.0306, Lock Sharpe=+0.3187
- `combo_sig_product__roc60__sma50_dist`: Train IC=+0.1278, Lock IC=+0.0137, Lock Sharpe=+0.2951
- `combo_sig_product__willr14__roc60`: Train IC=+0.1569, Lock IC=+0.0107, Lock Sharpe=+0.1846

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.0991, Lock IC=+0.0131, Lock Sharpe=+0.0320

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 56.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4495_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 493 | 30 | 56.7% | 36.7% | +0.0188 | -0.2013 |
| B2 Rolling Guard | 67 | 30 | 53.3% | 20.0% | -0.0022 | -0.3002 |
| BH-FDR Gate | 21 | 21 | 100.0% | 85.7% | +0.0602 | +0.2747 |
| B3 Composite Floor | 5 | 5 | 80.0% | 40.0% | +0.0255 | -0.0234 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__volume_weighted_momentum_acceleration__max_down_ret`: Train IC=+0.1031, Lock IC=+0.0668, Lock Sharpe=+0.4578
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1299, Lock IC=+0.0763, Lock Sharpe=+0.4489
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1215, Lock IC=+0.0581, Lock Sharpe=+0.3630
- `limit_down_proximity_early`: Train IC=+0.1147, Lock IC=+0.0401, Lock Sharpe=+0.3409
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1147, Lock IC=+0.0401, Lock Sharpe=+0.3409

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__opening_drive_thrust_ratio__max_down_ret`: Train IC=+0.0394, Lock IC=+0.0505, Lock Sharpe=+0.6099
- `combo_diff__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0396, Lock IC=+0.0401, Lock Sharpe=+0.3409
- `combo_z_diff__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0396, Lock IC=+0.0401, Lock Sharpe=+0.3409
- `combo_clamp_diff__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0071, Lock IC=+0.0401, Lock Sharpe=+0.3409
- `combo_clamp_diff__volume_surge_direction__volume_weighted_momentum_acceleration`: Train IC=+0.0369, Lock IC=+0.0598, Lock Sharpe=+0.2599

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1154, Lock IC=+0.0716, Lock Sharpe=+0.5842
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0686, Lock IC=+0.0655, Lock Sharpe=+0.5501
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0648, Lock IC=+0.0618, Lock Sharpe=+0.4934
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0648, Lock IC=+0.0618, Lock Sharpe=+0.4934
- `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0896, Lock IC=+0.0585, Lock Sharpe=+0.4808

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1819, Lock IC=+0.0401, Lock Sharpe=+0.3409
- `combo_z_sum__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1819, Lock IC=+0.0401, Lock Sharpe=+0.3409

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 71.0% lock IC > 0, 11.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4818_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 771 | 30 | 90.0% | 36.7% | +0.0209 | -0.0834 |
| B2 Rolling Guard | 69 | 30 | 33.3% | 6.7% | -0.0079 | -0.4863 |
| BH-FDR Gate | 1 | 1 | 100.0% | 100.0% | +0.0071 | +0.0067 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__stoch_k__roc60`: Train IC=+0.1732, Lock IC=+0.0449, Lock Sharpe=+0.5031
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.1615, Lock IC=+0.0418, Lock Sharpe=+0.4378
- `combo_max__iv_corridor_width__multi_ema_alignment_5_20_50`: Train IC=+0.1725, Lock IC=+0.0588, Lock Sharpe=+0.3082
- `combo_max__bar_vol_4__yesterday_body_ratio`: Train IC=+0.1608, Lock IC=+0.0364, Lock Sharpe=+0.2832
- `combo_min__iv_corridor_width__multi_ema_alignment_5_20_50`: Train IC=+0.1688, Lock IC=+0.0490, Lock Sharpe=+0.2567

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.1441, Lock IC=+0.0059, Lock Sharpe=+0.1981
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1441, Lock IC=+0.0059, Lock Sharpe=+0.1981

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `star50_limit_proximity_early`: Train IC=+0.1457, Lock IC=+0.0071, Lock Sharpe=+0.0067

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.0% lock IC > 0, 3.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8126_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 315 | 30 | 43.3% | 0.0% | +0.0052 | -0.6665 |
| B2 Rolling Guard | 38 | 30 | 30.0% | 0.0% | -0.0022 | -0.5704 |
| BH-FDR Gate | 8 | 8 | 25.0% | 0.0% | -0.0038 | -1.1231 |

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 54.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4674_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 278 | 30 | 80.0% | 30.0% | +0.0192 | -0.2106 |
| B2 Rolling Guard | 33 | 30 | 30.0% | 3.3% | -0.0026 | -0.3733 |
| BH-FDR Gate | 6 | 6 | 33.3% | 16.7% | -0.0062 | -0.5453 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1547, Lock IC=+0.0506, Lock Sharpe=+0.4086
- `combo_z_sum__bar_vol_4__sma_distance_60d`: Train IC=+0.1547, Lock IC=+0.0506, Lock Sharpe=+0.4086
- `combo_mean__bar_vol_4__mfi14`: Train IC=+0.1793, Lock IC=+0.0588, Lock Sharpe=+0.4007
- `combo_z_sum__bar_vol_4__mfi14`: Train IC=+0.1793, Lock IC=+0.0588, Lock Sharpe=+0.4007
- `combo_rank_max__bar_vol_4__sma_distance_60d`: Train IC=+0.0966, Lock IC=+0.0237, Lock Sharpe=+0.2471

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0282, Lock Sharpe=+0.1917

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__bar_vol_4__sma_distance_60d`: Train IC=+0.0486, Lock IC=+0.0187, Lock Sharpe=+0.0284

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 78.0% lock IC > 0, 47.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0438_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2453 | 30 | 100.0% | 96.7% | +0.1060 | +0.7404 |
| B2 Rolling Guard | 372 | 30 | 100.0% | 76.7% | +0.0816 | +0.1512 |
| BH-FDR Gate | 8 | 8 | 100.0% | 0.0% | +0.0203 | -0.4153 |
| B3 Composite Floor | 262 | 30 | 100.0% | 100.0% | +0.0988 | +0.5836 |
| B4 Correlation Gate | 1076 | 30 | 100.0% | 100.0% | +0.1061 | +0.6237 |

**Admitted Pool Summary**: 332 features, False Positive Rate = 11.4% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0898, Mean Lock Sharpe = +0.3964

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2312, Lock IC=+0.1016, Lock Sharpe=+1.2136
- `combo_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2539, Lock IC=+0.0972, Lock Sharpe=+1.1933
- `combo_rel_diff__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.2431, Lock IC=+0.1135, Lock Sharpe=+1.1899
- `combo_rel_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.2456, Lock IC=+0.0932, Lock Sharpe=+1.1142
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2899, Lock IC=+0.1070, Lock Sharpe=+1.0919

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Lock Sharpe=+0.3984
- `combo_tri_z_mean__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Lock Sharpe=+0.3984
- `combo_tri_mean__opening_drive_thrust_ratio__opening_auction_imbalance__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Lock Sharpe=+0.3984
- `combo_tri_z_mean__opening_drive_thrust_ratio__opening_auction_imbalance__volume_weighted_momentum_acceleration`: Train IC=+0.2072, Lock IC=+0.0780, Lock Sharpe=+0.3984
- `combo_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`: Train IC=+0.2056, Lock IC=+0.0739, Lock Sharpe=+0.3906

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.3103, Lock IC=+0.1126, Lock Sharpe=+1.0957
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3026, Lock IC=+0.1078, Lock Sharpe=+0.9888
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3026, Lock IC=+0.1078, Lock Sharpe=+0.9888

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 73.0% lock IC > 0, 19.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4410_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1252 | 30 | 100.0% | 0.0% | +0.0600 | -0.1764 |
| B2 Rolling Guard | 46 | 30 | 53.3% | 20.0% | +0.0233 | -0.2231 |
| BH-FDR Gate | 33 | 30 | 100.0% | 30.0% | +0.0590 | -0.1712 |
| B3 Composite Floor | 29 | 29 | 100.0% | 24.1% | +0.0641 | -0.2343 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv`: Train IC=+0.0483, Lock IC=+0.0482, Lock Sharpe=+0.5364
- `combo_sig_product__rbreaker_sell_setup_proximity_early__morning_trend_extrapolated`: Train IC=+0.0945, Lock IC=+0.0797, Lock Sharpe=+0.4915
- `iv_diff_1d`: Train IC=+0.0348, Lock IC=+0.0707, Lock Sharpe=+0.4862
- `vix`: Train IC=+0.0323, Lock IC=+0.0472, Lock Sharpe=+0.0940
- `iv_envelope_deviation`: Train IC=+0.0406, Lock IC=+0.0407, Lock Sharpe=+0.0685

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1334, Lock IC=+0.1347, Lock Sharpe=+0.7888
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.1335, Lock IC=+0.1161, Lock Sharpe=+0.5368
- `combo_min__shaved_bar_trend_conviction__trend_day_regime_conviction`: Train IC=+0.1309, Lock IC=+0.0741, Lock Sharpe=+0.5204
- `close_vs_open_range`: Train IC=+0.1077, Lock IC=+0.0899, Lock Sharpe=+0.4665
- `combo_sig_product__consecutive_higher_highs__morning_trend_extrapolated`: Train IC=+0.1097, Lock IC=+0.0599, Lock Sharpe=+0.2716

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1684, Lock IC=+0.0952, Lock Sharpe=+0.7962
- `combo_rank_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1844, Lock IC=+0.0986, Lock Sharpe=+0.6527
- `combo_sig_product__limit_down_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1583, Lock IC=+0.1136, Lock Sharpe=+0.5935
- `combo_sig_product__rbreaker_buy_setup_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1583, Lock IC=+0.1136, Lock Sharpe=+0.5935
- `combo_rank_min__shaved_bar_trend_conviction__morning_trend_extrapolated`: Train IC=+0.1703, Lock IC=+0.0653, Lock Sharpe=+0.5401

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2841_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 372 | 30 | 66.7% | 56.7% | +0.0363 | +0.1404 |
| B2 Rolling Guard | 48 | 30 | 50.0% | 16.7% | -0.0001 | -0.2241 |
| BH-FDR Gate | 6 | 6 | 100.0% | 33.3% | +0.0799 | +0.1849 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1306, Lock IC=+0.1123, Lock Sharpe=+1.2596
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1306, Lock IC=+0.1123, Lock Sharpe=+1.2596
- `combo_mean__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1276, Lock IC=+0.1034, Lock Sharpe=+0.9662
- `combo_z_sum__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1276, Lock IC=+0.1034, Lock Sharpe=+0.9662
- `combo_mean__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1276, Lock IC=+0.1034, Lock Sharpe=+0.9662

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `close_vs_open_range`: Train IC=+0.0830, Lock IC=+0.0899, Lock Sharpe=+0.7547
- `iv_diff_1d`: Train IC=+0.0615, Lock IC=+0.0707, Lock Sharpe=+0.6515
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0670, Lock Sharpe=+0.1840
- `combo_sig_product__failed_breakout_reversal_early__net_volume_flow`: Train IC=+0.0641, Lock IC=+0.0009, Lock Sharpe=+0.0123
- `combo_sig_product__failed_breakout_reversal_early__opening_auction_imbalance`: Train IC=+0.0641, Lock IC=+0.0009, Lock Sharpe=+0.0123

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1734, Lock IC=+0.1162, Lock Sharpe=+0.8891
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1734, Lock IC=+0.1162, Lock Sharpe=+0.8891

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 75.0% lock IC > 0, 55.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.2198_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2039 | 30 | 100.0% | 90.0% | +0.1005 | +0.8878 |
| B2 Rolling Guard | 468 | 30 | 100.0% | 90.0% | +0.1085 | +0.7932 |
| BH-FDR Gate | 4 | 4 | 50.0% | 50.0% | -0.0225 | -0.2589 |
| B3 Composite Floor | 153 | 30 | 100.0% | 100.0% | +0.1087 | +0.7746 |
| B4 Correlation Gate | 129 | 30 | 100.0% | 100.0% | +0.1294 | +1.2305 |

**Admitted Pool Summary**: 78 features, False Positive Rate = 1.3% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1114, Mean Lock Sharpe = +0.8778

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Lock Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Lock Sharpe=+1.8587
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2154, Lock IC=+0.1298, Lock Sharpe=+1.4980
- `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2005, Lock IC=+0.1212, Lock Sharpe=+1.4310
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2005, Lock IC=+0.1212, Lock Sharpe=+1.4310

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2340, Lock IC=+0.1332, Lock Sharpe=+1.4122
- `combo_rank_min__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2251, Lock IC=+0.1287, Lock Sharpe=+1.4106
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Lock Sharpe=+1.3582
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression`: Train IC=+0.2296, Lock IC=+0.1314, Lock Sharpe=+1.2753
- `combo_diff__demark_setup_reversal_early__first_bar_return`: Train IC=+0.2299, Lock IC=+0.1187, Lock Sharpe=+1.1602

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__max_up_ret__keltner_squeeze_width`: Train IC=+0.1054, Lock IC=+0.0291, Lock Sharpe=+0.0947
- `combo_z_sum__max_up_ret__keltner_squeeze_width`: Train IC=+0.1054, Lock IC=+0.0291, Lock Sharpe=+0.0947

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Lock Sharpe=+1.4133
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2419, Lock IC=+0.1373, Lock Sharpe=+1.3304
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2344, Lock IC=+0.1306, Lock Sharpe=+1.3039
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2528, Lock IC=+0.1312, Lock Sharpe=+1.2701
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0`: Train IC=+0.2526, Lock IC=+0.1311, Lock Sharpe=+1.2701

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2562, Lock IC=+0.1283, Lock Sharpe=+1.4907
- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2813, Lock IC=+0.1406, Lock Sharpe=+1.4794
- `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2575, Lock IC=+0.1208, Lock Sharpe=+1.4577
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2777, Lock IC=+0.1338, Lock Sharpe=+1.4166
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__bar_ret_0`: Train IC=+0.2775, Lock IC=+0.1337, Lock Sharpe=+1.4166

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 82.0% lock IC > 0, 59.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.1015_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1013 | 30 | 86.7% | 56.7% | +0.0716 | +0.2031 |
| B2 Rolling Guard | 60 | 30 | 86.7% | 73.3% | +0.0764 | +0.4878 |
| BH-FDR Gate | 48 | 30 | 100.0% | 93.3% | +0.1087 | +0.6527 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1767, Lock IC=+0.1382, Lock Sharpe=+1.1394
- `combo_tri_median__shaved_bar_trend_conviction__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1688, Lock IC=+0.1147, Lock Sharpe=+0.9866
- `combo_tri_median__shaved_bar_trend_conviction__first_30min_return__counter_trend_bar_weakness`: Train IC=+0.1688, Lock IC=+0.1147, Lock Sharpe=+0.9866
- `combo_tri_mean__shaved_bar_trend_conviction__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1644, Lock IC=+0.1212, Lock Sharpe=+0.9746
- `combo_tri_z_mean__shaved_bar_trend_conviction__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1644, Lock IC=+0.1212, Lock Sharpe=+0.9746

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1543, Lock IC=+0.1254, Lock Sharpe=+1.3259
- `combo_rank_min__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1543, Lock IC=+0.1254, Lock Sharpe=+1.3259
- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1473, Lock IC=+0.1241, Lock Sharpe=+1.2672
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1283, Lock IC=+0.1319, Lock Sharpe=+1.1958
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1283, Lock IC=+0.1319, Lock Sharpe=+1.1958

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__open_to_current_return`: Train IC=+0.1144, Lock IC=+0.1079, Lock Sharpe=+1.1081
- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__first_30min_return`: Train IC=+0.1144, Lock IC=+0.1079, Lock Sharpe=+1.1081
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1174, Lock IC=+0.1368, Lock Sharpe=+1.0380
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1174, Lock IC=+0.1368, Lock Sharpe=+1.0380
- `combo_tri_median__rbreaker_sell_setup_proximity_early__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1724, Lock IC=+0.1361, Lock Sharpe=+0.9205

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4856_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 255 | 30 | 73.3% | 50.0% | +0.0331 | -0.1320 |
| B2 Rolling Guard | 43 | 30 | 46.7% | 23.3% | +0.0072 | -0.2419 |
| BH-FDR Gate | 4 | 4 | 100.0% | 50.0% | +0.0733 | +0.1287 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.1453, Lock IC=+0.0750, Lock Sharpe=+0.6221
- `combo_rank_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.1064, Lock IC=+0.0733, Lock Sharpe=+0.5012
- `trend_day_regime_conviction`: Train IC=+0.1013, Lock IC=+0.1116, Lock Sharpe=+0.4826
- `combo_rel_diff__morning_volume_weighted_momentum__shaved_bar_trend_conviction`: Train IC=+0.0703, Lock IC=+0.0150, Lock Sharpe=+0.3049
- `combo_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.1417, Lock IC=+0.0623, Lock Sharpe=+0.2941

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volatility_expansion_trend_vector`: Train IC=+0.0439, Lock IC=+0.1157, Lock Sharpe=+0.5367
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0530, Lock Sharpe=+0.4984
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0771, Lock Sharpe=+0.3581
- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.0549, Lock Sharpe=+0.2067
- `keltner_squeeze_width`: Train IC=+0.0057, Lock IC=+0.0640, Lock Sharpe=+0.1926

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0020, Lock IC=+0.1016, Lock Sharpe=+0.5266
- `limit_down_proximity_early`: Train IC=+0.0020, Lock IC=+0.1016, Lock Sharpe=+0.5266

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 565 | +0.0704 | 100.0% |
| 0.45 | 0.20 | 545 | +0.0704 | 100.0% |
| 0.45 | 0.30 | 498 | +0.0704 | 100.0% |
| 0.45 | 0.40 | 372 | +0.0704 | 100.0% |
| 0.45 | 0.50 | 231 | +0.0704 | 100.0% |
| 0.50 | 0.15 | 558 | +0.0704 | 100.0% |
| 0.50 | 0.25 | 532 | +0.0704 | 100.0% |
| 0.50 | 0.35 | 434 | +0.0704 | 100.0% |
| 0.50 | 0.45 | 310 | +0.0704 | 100.0% |
| 0.55 | 0.10 | 552 | +0.0704 | 100.0% |
| 0.55 | 0.20 | 545 | +0.0704 | 100.0% |
| 0.55 | 0.30 | 498 | +0.0704 | 100.0% |
| 0.55 | 0.40 | 372 | +0.0704 | 100.0% |
| 0.55 | 0.50 | 231 | +0.0704 | 100.0% |
| 0.60 | 0.15 | 505 | +0.0704 | 100.0% |
| 0.60 | 0.25 | 503 | +0.0704 | 100.0% |
| 0.60 | 0.35 | 434 | +0.0704 | 100.0% |
| 0.60 | 0.45 | 310 | +0.0704 | 100.0% |
| 0.65 | 0.10 | 379 | +0.0704 | 100.0% |
| 0.65 | 0.20 | 379 | +0.0704 | 100.0% |
| 0.65 | 0.30 | 379 | +0.0704 | 100.0% |
| 0.65 | 0.40 | 351 | +0.0704 | 100.0% |
| 0.65 | 0.50 | 231 | +0.0704 | 100.0% |
| 0.70 | 0.15 | 202 | +0.0704 | 100.0% |
| 0.70 | 0.25 | 202 | +0.0704 | 100.0% |
| 0.70 | 0.35 | 202 | +0.0704 | 100.0% |
| 0.70 | 0.45 | 201 | +0.0704 | 100.0% |
| 0.75 | 0.10 | 40 | +0.0662 | 100.0% |
| 0.75 | 0.20 | 40 | +0.0662 | 100.0% |
| 0.75 | 0.30 | 40 | +0.0662 | 100.0% |
| 0.75 | 0.40 | 40 | +0.0662 | 100.0% |
| 0.75 | 0.50 | 40 | +0.0662 | 100.0% |
| 0.80 | 0.15 | 14 | +0.0263 | 100.0% |
| 0.80 | 0.25 | 14 | +0.0263 | 100.0% |
| 0.80 | 0.35 | 14 | +0.0263 | 100.0% |
| 0.80 | 0.45 | 14 | +0.0263 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 565 candidates, mean lock IC=+0.0704, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | -0.0035 | 55.6% |
| 0.45 | 0.20 | 5 | -0.0032 | 80.0% |
| 0.45 | 0.30 | 2 | +0.0057 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | +0.0007 | 62.5% |
| 0.50 | 0.25 | 3 | -0.0063 | 66.7% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 5 | -0.0111 | 60.0% |
| 0.55 | 0.20 | 4 | -0.0046 | 75.0% |
| 0.55 | 0.30 | 2 | +0.0057 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | +0.0057 | 100.0% |
| 0.60 | 0.25 | 2 | +0.0057 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 8 candidates, mean lock IC=+0.0007, 62.5% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 35 | +0.0445 | 90.0% |
| 0.45 | 0.20 | 25 | +0.0445 | 90.0% |
| 0.45 | 0.30 | 10 | +0.0630 | 100.0% |
| 0.45 | 0.40 | 3 | +0.0551 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 28 | +0.0445 | 90.0% |
| 0.50 | 0.25 | 14 | +0.0610 | 100.0% |
| 0.50 | 0.35 | 6 | +0.0608 | 100.0% |
| 0.50 | 0.45 | 3 | +0.0551 | 100.0% |
| 0.55 | 0.10 | 26 | +0.0445 | 90.0% |
| 0.55 | 0.20 | 25 | +0.0445 | 90.0% |
| 0.55 | 0.30 | 10 | +0.0630 | 100.0% |
| 0.55 | 0.40 | 3 | +0.0551 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 16 | +0.0603 | 100.0% |
| 0.60 | 0.25 | 12 | +0.0603 | 100.0% |
| 0.60 | 0.35 | 6 | +0.0608 | 100.0% |
| 0.60 | 0.45 | 3 | +0.0551 | 100.0% |
| 0.65 | 0.10 | 5 | +0.0604 | 100.0% |
| 0.65 | 0.20 | 5 | +0.0604 | 100.0% |
| 0.65 | 0.30 | 5 | +0.0604 | 100.0% |
| 0.65 | 0.40 | 3 | +0.0551 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.30 → 10 candidates, mean lock IC=+0.0630, 100.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 199 | +0.0422 | 100.0% |
| 0.45 | 0.20 | 179 | +0.0422 | 100.0% |
| 0.45 | 0.30 | 162 | +0.0422 | 100.0% |
| 0.45 | 0.40 | 147 | +0.0422 | 100.0% |
| 0.45 | 0.50 | 136 | +0.0422 | 100.0% |
| 0.50 | 0.15 | 188 | +0.0422 | 100.0% |
| 0.50 | 0.25 | 175 | +0.0422 | 100.0% |
| 0.50 | 0.35 | 152 | +0.0422 | 100.0% |
| 0.50 | 0.45 | 138 | +0.0422 | 100.0% |
| 0.55 | 0.10 | 185 | +0.0422 | 100.0% |
| 0.55 | 0.20 | 179 | +0.0422 | 100.0% |
| 0.55 | 0.30 | 162 | +0.0422 | 100.0% |
| 0.55 | 0.40 | 147 | +0.0422 | 100.0% |
| 0.55 | 0.50 | 136 | +0.0422 | 100.0% |
| 0.60 | 0.15 | 167 | +0.0422 | 100.0% |
| 0.60 | 0.25 | 165 | +0.0422 | 100.0% |
| 0.60 | 0.35 | 152 | +0.0422 | 100.0% |
| 0.60 | 0.45 | 138 | +0.0422 | 100.0% |
| 0.65 | 0.10 | 146 | +0.0422 | 100.0% |
| 0.65 | 0.20 | 146 | +0.0422 | 100.0% |
| 0.65 | 0.30 | 145 | +0.0422 | 100.0% |
| 0.65 | 0.40 | 143 | +0.0422 | 100.0% |
| 0.65 | 0.50 | 136 | +0.0422 | 100.0% |
| 0.70 | 0.15 | 123 | +0.0291 | 80.0% |
| 0.70 | 0.25 | 123 | +0.0291 | 80.0% |
| 0.70 | 0.35 | 123 | +0.0291 | 80.0% |
| 0.70 | 0.45 | 123 | +0.0291 | 80.0% |
| 0.75 | 0.10 | 79 | +0.0172 | 60.0% |
| 0.75 | 0.20 | 79 | +0.0172 | 60.0% |
| 0.75 | 0.30 | 79 | +0.0172 | 60.0% |
| 0.75 | 0.40 | 79 | +0.0172 | 60.0% |
| 0.75 | 0.50 | 79 | +0.0172 | 60.0% |
| 0.80 | 0.15 | 58 | +0.0110 | 50.0% |
| 0.80 | 0.25 | 58 | +0.0110 | 50.0% |
| 0.80 | 0.35 | 58 | +0.0110 | 50.0% |
| 0.80 | 0.45 | 58 | +0.0110 | 50.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 199 candidates, mean lock IC=+0.0422, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 14 | -0.0039 | 20.0% |
| 0.45 | 0.20 | 8 | -0.0038 | 25.0% |
| 0.45 | 0.30 | 7 | -0.0059 | 14.3% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 10 | +0.0106 | 40.0% |
| 0.50 | 0.25 | 8 | -0.0038 | 25.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 8 | -0.0038 | 25.0% |
| 0.55 | 0.20 | 8 | -0.0038 | 25.0% |
| 0.55 | 0.30 | 7 | -0.0059 | 14.3% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 7 | -0.0059 | 14.3% |
| 0.60 | 0.25 | 7 | -0.0059 | 14.3% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 10 candidates, mean lock IC=+0.0106, 40.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 8 | -0.0104 | 25.0% |
| 0.45 | 0.20 | 4 | -0.0000 | 50.0% |
| 0.45 | 0.30 | 2 | +0.0026 | 50.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 6 | -0.0062 | 33.3% |
| 0.50 | 0.25 | 2 | +0.0026 | 50.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | -0.0062 | 33.3% |
| 0.55 | 0.20 | 4 | -0.0000 | 50.0% |
| 0.55 | 0.30 | 2 | +0.0026 | 50.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 3 | +0.0045 | 66.7% |
| 0.60 | 0.25 | 1 | +0.0187 | 100.0% |
| 0.60 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 1 | +0.0187 | 100.0% |
| 0.65 | 0.20 | 1 | +0.0187 | 100.0% |
| 0.65 | 0.30 | 1 | +0.0187 | 100.0% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0045, 66.7% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 2265 | +0.1142 | 100.0% |
| 0.45 | 0.20 | 2237 | +0.1142 | 100.0% |
| 0.45 | 0.30 | 2157 | +0.1142 | 100.0% |
| 0.45 | 0.40 | 1951 | +0.1142 | 100.0% |
| 0.45 | 0.50 | 1528 | +0.1142 | 100.0% |
| 0.50 | 0.15 | 2253 | +0.1142 | 100.0% |
| 0.50 | 0.25 | 2206 | +0.1142 | 100.0% |
| 0.50 | 0.35 | 2071 | +0.1142 | 100.0% |
| 0.50 | 0.45 | 1766 | +0.1142 | 100.0% |
| 0.55 | 0.10 | 2257 | +0.1142 | 100.0% |
| 0.55 | 0.20 | 2237 | +0.1142 | 100.0% |
| 0.55 | 0.30 | 2157 | +0.1142 | 100.0% |
| 0.55 | 0.40 | 1951 | +0.1142 | 100.0% |
| 0.55 | 0.50 | 1528 | +0.1142 | 100.0% |
| 0.60 | 0.15 | 2188 | +0.1142 | 100.0% |
| 0.60 | 0.25 | 2176 | +0.1142 | 100.0% |
| 0.60 | 0.35 | 2069 | +0.1142 | 100.0% |
| 0.60 | 0.45 | 1766 | +0.1142 | 100.0% |
| 0.65 | 0.10 | 1919 | +0.1142 | 100.0% |
| 0.65 | 0.20 | 1919 | +0.1142 | 100.0% |
| 0.65 | 0.30 | 1919 | +0.1142 | 100.0% |
| 0.65 | 0.40 | 1866 | +0.1142 | 100.0% |
| 0.65 | 0.50 | 1528 | +0.1142 | 100.0% |
| 0.70 | 0.15 | 1356 | +0.1142 | 100.0% |
| 0.70 | 0.25 | 1356 | +0.1142 | 100.0% |
| 0.70 | 0.35 | 1356 | +0.1142 | 100.0% |
| 0.70 | 0.45 | 1355 | +0.1142 | 100.0% |
| 0.75 | 0.10 | 636 | +0.1142 | 100.0% |
| 0.75 | 0.20 | 636 | +0.1142 | 100.0% |
| 0.75 | 0.30 | 636 | +0.1142 | 100.0% |
| 0.75 | 0.40 | 636 | +0.1142 | 100.0% |
| 0.75 | 0.50 | 636 | +0.1142 | 100.0% |
| 0.80 | 0.15 | 188 | +0.1109 | 100.0% |
| 0.80 | 0.25 | 188 | +0.1109 | 100.0% |
| 0.80 | 0.35 | 188 | +0.1109 | 100.0% |
| 0.80 | 0.45 | 188 | +0.1109 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 2265 candidates, mean lock IC=+0.1142, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 72 | +0.0793 | 100.0% |
| 0.45 | 0.20 | 62 | +0.0793 | 100.0% |
| 0.45 | 0.30 | 31 | +0.0788 | 100.0% |
| 0.45 | 0.40 | 5 | +0.0760 | 100.0% |
| 0.45 | 0.50 | 2 | +0.1021 | 100.0% |
| 0.50 | 0.15 | 63 | +0.0793 | 100.0% |
| 0.50 | 0.25 | 54 | +0.0793 | 100.0% |
| 0.50 | 0.35 | 12 | +0.0733 | 100.0% |
| 0.50 | 0.45 | 3 | +0.0714 | 100.0% |
| 0.55 | 0.10 | 62 | +0.0793 | 100.0% |
| 0.55 | 0.20 | 62 | +0.0793 | 100.0% |
| 0.55 | 0.30 | 31 | +0.0788 | 100.0% |
| 0.55 | 0.40 | 5 | +0.0760 | 100.0% |
| 0.55 | 0.50 | 2 | +0.1021 | 100.0% |
| 0.60 | 0.15 | 40 | +0.0846 | 100.0% |
| 0.60 | 0.25 | 39 | +0.0846 | 100.0% |
| 0.60 | 0.35 | 12 | +0.0733 | 100.0% |
| 0.60 | 0.45 | 3 | +0.0714 | 100.0% |
| 0.65 | 0.10 | 5 | +0.0673 | 100.0% |
| 0.65 | 0.20 | 5 | +0.0673 | 100.0% |
| 0.65 | 0.30 | 5 | +0.0673 | 100.0% |
| 0.65 | 0.40 | 3 | +0.0714 | 100.0% |
| 0.65 | 0.50 | 2 | +0.1021 | 100.0% |
| 0.70 | 0.15 | 2 | +0.1021 | 100.0% |
| 0.70 | 0.25 | 2 | +0.1021 | 100.0% |
| 0.70 | 0.35 | 2 | +0.1021 | 100.0% |
| 0.70 | 0.45 | 2 | +0.1021 | 100.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 40 candidates, mean lock IC=+0.0846, 100.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 12 | +0.0441 | 70.0% |
| 0.45 | 0.20 | 2 | +0.0589 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | +0.0534 | 75.0% |
| 0.50 | 0.25 | 2 | +0.0589 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0799 | 100.0% |
| 0.55 | 0.20 | 2 | +0.0589 | 100.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | +0.0589 | 100.0% |
| 0.60 | 0.25 | 2 | +0.0589 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 6 candidates, mean lock IC=+0.0799, 100.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 904 | +0.1366 | 100.0% |
| 0.45 | 0.20 | 859 | +0.1366 | 100.0% |
| 0.45 | 0.30 | 720 | +0.1366 | 100.0% |
| 0.45 | 0.40 | 460 | +0.1366 | 100.0% |
| 0.45 | 0.50 | 241 | +0.1366 | 100.0% |
| 0.50 | 0.15 | 892 | +0.1366 | 100.0% |
| 0.50 | 0.25 | 812 | +0.1366 | 100.0% |
| 0.50 | 0.35 | 586 | +0.1366 | 100.0% |
| 0.50 | 0.45 | 341 | +0.1366 | 100.0% |
| 0.55 | 0.10 | 890 | +0.1366 | 100.0% |
| 0.55 | 0.20 | 858 | +0.1366 | 100.0% |
| 0.55 | 0.30 | 720 | +0.1366 | 100.0% |
| 0.55 | 0.40 | 460 | +0.1366 | 100.0% |
| 0.55 | 0.50 | 241 | +0.1366 | 100.0% |
| 0.60 | 0.15 | 763 | +0.1366 | 100.0% |
| 0.60 | 0.25 | 744 | +0.1366 | 100.0% |
| 0.60 | 0.35 | 580 | +0.1366 | 100.0% |
| 0.60 | 0.45 | 341 | +0.1366 | 100.0% |
| 0.65 | 0.10 | 467 | +0.1366 | 100.0% |
| 0.65 | 0.20 | 467 | +0.1366 | 100.0% |
| 0.65 | 0.30 | 467 | +0.1366 | 100.0% |
| 0.65 | 0.40 | 411 | +0.1366 | 100.0% |
| 0.65 | 0.50 | 241 | +0.1366 | 100.0% |
| 0.70 | 0.15 | 157 | +0.1362 | 100.0% |
| 0.70 | 0.25 | 157 | +0.1362 | 100.0% |
| 0.70 | 0.35 | 157 | +0.1362 | 100.0% |
| 0.70 | 0.45 | 155 | +0.1362 | 100.0% |
| 0.75 | 0.10 | 34 | +0.1269 | 100.0% |
| 0.75 | 0.20 | 34 | +0.1269 | 100.0% |
| 0.75 | 0.30 | 34 | +0.1269 | 100.0% |
| 0.75 | 0.40 | 34 | +0.1269 | 100.0% |
| 0.75 | 0.50 | 34 | +0.1269 | 100.0% |
| 0.80 | 0.15 | 4 | -0.0024 | 50.0% |
| 0.80 | 0.25 | 4 | -0.0024 | 50.0% |
| 0.80 | 0.35 | 4 | -0.0024 | 50.0% |
| 0.80 | 0.45 | 4 | -0.0024 | 50.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 904 candidates, mean lock IC=+0.1366, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 66 | +0.1086 | 100.0% |
| 0.45 | 0.20 | 41 | +0.1122 | 100.0% |
| 0.45 | 0.30 | 20 | +0.1011 | 100.0% |
| 0.45 | 0.40 | 9 | +0.0849 | 100.0% |
| 0.45 | 0.50 | 1 | +0.1101 | 100.0% |
| 0.50 | 0.15 | 54 | +0.1086 | 100.0% |
| 0.50 | 0.25 | 29 | +0.1059 | 100.0% |
| 0.50 | 0.35 | 12 | +0.0863 | 100.0% |
| 0.50 | 0.45 | 5 | +0.1056 | 100.0% |
| 0.55 | 0.10 | 51 | +0.1122 | 100.0% |
| 0.55 | 0.20 | 41 | +0.1122 | 100.0% |
| 0.55 | 0.30 | 20 | +0.1011 | 100.0% |
| 0.55 | 0.40 | 9 | +0.0849 | 100.0% |
| 0.55 | 0.50 | 1 | +0.1101 | 100.0% |
| 0.60 | 0.15 | 23 | +0.1105 | 100.0% |
| 0.60 | 0.25 | 20 | +0.0950 | 100.0% |
| 0.60 | 0.35 | 12 | +0.0863 | 100.0% |
| 0.60 | 0.45 | 5 | +0.1056 | 100.0% |
| 0.65 | 0.10 | 5 | +0.0688 | 100.0% |
| 0.65 | 0.20 | 5 | +0.0688 | 100.0% |
| 0.65 | 0.30 | 5 | +0.0688 | 100.0% |
| 0.65 | 0.40 | 5 | +0.0688 | 100.0% |
| 0.65 | 0.50 | 1 | +0.1101 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 41 candidates, mean lock IC=+0.1122, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | +0.0452 | 66.7% |
| 0.45 | 0.20 | 2 | +0.0450 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 6 | +0.0666 | 83.3% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | +0.0733 | 100.0% |
| 0.55 | 0.20 | 2 | +0.0450 | 100.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 4 candidates, mean lock IC=+0.0733, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1294 | +0.0000 | +0.0711 | 0.55x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1293 | +0.0000 | +0.0632 | 0.49x | 2017-06-09 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1127 | +0.0000 | +0.0885 | 0.79x | 2016-08-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1193 | +0.0000 | +0.0706 | 0.59x | 2017-06-09 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1143 | +0.0000 | +0.0543 | 0.47x | 2017-05-09 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1280 | +0.0000 | +0.0622 | 0.49x | 2017-06-09 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1277 | +0.0000 | +0.0723 | 0.57x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1236 | +0.0000 | +0.0756 | 0.61x | 2017-07-10 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1158 | +0.0000 | +0.0694 | 0.60x | 2017-08-08 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__limit_down_proximity_early` | +0.1108 | +0.0000 | +0.0619 | 0.56x | 2016-08-24 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +0.0854 | +0.0000 | +0.0524 | 0.61x | 2010-10-15 |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | +0.0989 | +0.0000 | +0.0524 | 0.53x | 2016-08-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1258 | +0.0000 | +0.0588 | 0.47x | 2017-06-09 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1198 | +0.0000 | +0.0660 | 0.55x | 2015-02-06 |
| `rbreaker_sell_setup_proximity_early` | +0.0962 | +0.0000 | +0.0662 | 0.69x | 2016-08-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1131 | +0.0000 | +0.0682 | 0.60x | 2015-02-06 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1173 | +0.0000 | +0.0640 | 0.55x | 2016-08-24 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1093 | +0.0000 | +0.0567 | 0.52x | 2015-02-06 |
| `combo_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.1249 | +0.0000 | +0.0742 | 0.59x | 2016-08-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1283 | +0.0000 | +0.0678 | 0.53x | 2017-07-10 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | +0.1103 | +0.0000 | +0.0566 | 0.51x | 2015-03-16 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.0911 | +0.0000 | +0.0520 | 0.57x | 2013-09-23 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1023 | +0.0000 | +0.0761 | 0.74x | 2014-07-04 |
| `combo_max__first_bar_return__bar_body_rng_0` | +0.0870 | +0.0000 | +0.0572 | 0.66x | 2013-08-21 |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | +0.1122 | +0.0000 | +0.0637 | 0.57x | 2015-02-06 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1023 | +0.0000 | +0.0592 | 0.58x | 2015-03-16 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1132 | +0.0000 | +0.0675 | 0.60x | 2016-08-24 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.0955 | +0.0000 | +0.0540 | 0.57x | 2015-02-06 |
| `combo_tri_max__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | +0.0909 | +0.0000 | +0.0538 | 0.59x | 2013-08-21 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1007 | +0.0000 | +0.0507 | 0.50x | 2015-02-06 |
| `star50_limit_proximity_early` | +0.0913 | +0.0000 | +0.0606 | 0.66x | 2011-09-20 |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | +0.0666 | +0.0000 | +0.0368 | 0.55x | 2017-11-10 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | +0.1008 | +0.0000 | +0.0587 | 0.58x | 2015-03-16 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1060 | +0.0000 | +0.0839 | 0.79x | 2016-08-24 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0942 | +0.0000 | +0.0852 | 0.90x | 2013-08-21 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +0.0511 | +0.0000 | +0.0417 | 0.81x | 2012-10-09 |
| `combo_tri_mean__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | +0.1011 | +0.0000 | +0.0629 | 0.62x | 2013-09-23 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1100 | +0.0000 | +0.0677 | 0.62x | 2017-07-10 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1129 | +0.0000 | +0.0684 | 0.61x | 2017-04-07 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | +0.1123 | +0.0000 | +0.0573 | 0.51x | 2017-07-10 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early` | +0.1096 | +0.0000 | +0.0708 | 0.65x | 2017-06-09 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | +0.0979 | +0.0000 | +0.0596 | 0.61x | 2015-01-08 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max` | +0.0650 | +0.0000 | +0.0521 | 0.80x | 2017-10-12 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1106 | +0.0000 | +0.0448 | 0.41x | 2017-04-07 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | +0.1030 | +0.0000 | +0.0560 | 0.54x | 2017-06-09 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1094 | +0.0000 | +0.0743 | 0.68x | 2016-08-24 |
| `combo_sig_product__first_bar_return__morning_volume_weighted_momentum` | +0.0746 | +0.0000 | +0.0290 | 0.39x | 2010-12-14 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1855 | +0.0000 | +0.1101 | 0.59x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.2000 | +0.0000 | +0.1089 | 0.54x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | +0.1798 | +0.0000 | +0.0890 | 0.49x | 2016-11-30 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1729 | +0.0000 | +0.0869 | 0.50x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | +0.1930 | +0.0000 | +0.1061 | 0.55x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.2020 | +0.0000 | +0.1034 | 0.51x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | +0.1661 | +0.0000 | +0.1152 | 0.69x | 2019-12-05 |
| `opening_drive_thrust_ratio` | +0.1895 | +0.0000 | +0.0993 | 0.52x | No decay |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1955 | +0.0000 | +0.1050 | 0.54x | No decay |
| `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early` | +0.1829 | +0.0000 | +0.1126 | 0.62x | No decay |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | +0.1690 | +0.0000 | +0.0992 | 0.59x | 2019-12-05 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1844 | +0.0000 | +0.1205 | 0.65x | 2016-09-26 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | +0.1997 | +0.0000 | +0.1053 | 0.53x | 2016-11-01 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.2001 | +0.0000 | +0.1132 | 0.57x | No decay |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +0.1730 | +0.0000 | +0.0779 | 0.45x | 2014-06-05 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.2041 | +0.0000 | +0.0977 | 0.48x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1772 | +0.0000 | +0.1217 | 0.69x | 2016-08-24 |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | +0.1805 | +0.0000 | +0.0727 | 0.40x | 2026-04-07 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1908 | +0.0000 | +0.0934 | 0.49x | 2025-07-24 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1998 | +0.0000 | +0.0851 | 0.43x | 2020-01-06 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | +0.1928 | +0.0000 | +0.1026 | 0.53x | No decay |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | +0.1846 | +0.0000 | +0.1004 | 0.54x | 2016-11-01 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1717 | +0.0000 | +0.0911 | 0.53x | No decay |
| `combo_min__first_bar_return__bar_body_rng_0` | +0.1467 | +0.0000 | +0.0799 | 0.54x | 2013-09-23 |
| `combo_tri_mean__max_up_ret__net_volume_flow__star50_limit_proximity_early` | +0.2004 | +0.0000 | +0.1040 | 0.52x | No decay |
| `combo_rank_min__max_down_ret__vwap_close_divergence_trend` | +0.1565 | +0.0000 | +0.0871 | 0.56x | 2016-11-01 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1788 | +0.0000 | +0.1015 | 0.57x | No decay |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1884 | +0.0000 | +0.0946 | 0.50x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1870 | +0.0000 | +0.0959 | 0.51x | No decay |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | +0.1841 | +0.0000 | +0.1261 | 0.69x | 2016-09-26 |
| `combo_clamp_diff__max_up_ret__smooth_momentum_structure` | +0.1874 | +0.0000 | +0.0933 | 0.50x | 2025-07-24 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1663 | +0.0000 | +0.0933 | 0.56x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1719 | +0.0000 | +0.0798 | 0.46x | No decay |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +0.1841 | +0.0000 | +0.1267 | 0.69x | 2016-09-26 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1692 | +0.0000 | +0.1175 | 0.69x | 2020-01-06 |
| `combo_max__max_up_ret__max_down_ret` | +0.1833 | +0.0000 | +0.0820 | 0.45x | 2016-11-01 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1845 | +0.0000 | +0.1166 | 0.63x | No decay |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1654 | +0.0000 | +0.0934 | 0.56x | 2016-12-29 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | +0.1728 | +0.0000 | +0.0911 | 0.53x | 2025-06-25 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | +0.1827 | +0.0000 | +0.1224 | 0.67x | 2016-09-26 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +0.1513 | +0.0000 | +0.1191 | 0.79x | 2016-09-26 |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | +0.1816 | +0.0000 | +0.1086 | 0.60x | 2020-01-06 |
| `combo_diff__max_up_ret__body_size_progression` | +0.1725 | +0.0000 | +0.0893 | 0.52x | 2025-06-25 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1976 | +0.0000 | +0.1217 | 0.62x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1955 | +0.0000 | +0.1183 | 0.60x | No decay |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1842 | +0.0000 | +0.0974 | 0.53x | No decay |
| `combo_min__max_up_ret__max_down_ret` | +0.1810 | +0.0000 | +0.1077 | 0.60x | No decay |
| `combo_min__max_down_ret__vwap_close_divergence_trend` | +0.1530 | +0.0000 | +0.0908 | 0.59x | 2016-11-01 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | +0.1815 | +0.0000 | +0.0824 | 0.45x | No decay |
| `combo_sig_product__max_up_ret__early_body_momentum` | +0.1796 | +0.0000 | +0.1052 | 0.59x | No decay |
| `combo_min__opening_drive_thrust_ratio__rsi_opening` | +0.1729 | +0.0000 | +0.0993 | 0.57x | 2016-11-01 |
| `combo_tri_median__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1902 | +0.0000 | +0.1096 | 0.58x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +0.1898 | +0.0000 | +0.0884 | 0.47x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1692 | +0.0000 | +0.0836 | 0.49x | 2016-12-29 |
| `combo_rank_max__max_up_ret__bar_ret_0` | +0.1755 | +0.0000 | +0.0919 | 0.52x | No decay |
| `combo_max__max_up_ret__bar_ret_0` | +0.1724 | +0.0000 | +0.0830 | 0.48x | No decay |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +0.1786 | +0.0000 | +0.0936 | 0.52x | 2020-01-06 |
| `combo_mean__max_up_ret__bar_ret_0` | +0.1848 | +0.0000 | +0.0854 | 0.46x | No decay |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1843 | +0.0000 | +0.0908 | 0.49x | No decay |
| `combo_rank_min__first_bar_return__close_vs_open_range` | +0.1444 | +0.0000 | +0.0965 | 0.67x | 2020-01-06 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | +0.1982 | +0.0000 | +0.0960 | 0.48x | 2016-11-30 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | +0.1644 | +0.0000 | +0.1192 | 0.73x | 2016-09-26 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1885 | +0.0000 | +0.0954 | 0.51x | No decay |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1935 | +0.0000 | +0.1136 | 0.59x | No decay |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | +0.1475 | +0.0000 | +0.0972 | 0.66x | 2016-08-24 |
| `combo_mean__bar_ret_0__max_down_ret` | +0.1541 | +0.0000 | +0.0916 | 0.59x | No decay |
| `combo_max__volatility_expansion_trend_vector__bar_body_rng_0` | +0.1676 | +0.0000 | +0.0835 | 0.50x | No decay |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +0.1473 | +0.0000 | +0.0948 | 0.64x | 2016-08-24 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1818 | +0.0000 | +0.0982 | 0.54x | 2026-04-07 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1742 | +0.0000 | +0.1141 | 0.65x | No decay |
| `combo_mean__early_body_momentum__star50_limit_proximity_early` | +0.1647 | +0.0000 | +0.0923 | 0.56x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1738 | +0.0000 | +0.1040 | 0.60x | No decay |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | +0.1854 | +0.0000 | +0.1045 | 0.56x | No decay |
| `combo_tri_median__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | +0.1790 | +0.0000 | +0.0818 | 0.46x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1729 | +0.0000 | +0.1134 | 0.66x | 2016-09-26 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1914 | +0.0000 | +0.0993 | 0.52x | No decay |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1473 | +0.0000 | +0.0958 | 0.65x | 2016-08-24 |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | +0.1912 | +0.0000 | +0.0880 | 0.46x | 2016-11-30 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__bar_ret_0` | +0.1947 | +0.0000 | +0.0977 | 0.50x | 2016-11-30 |
| `combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range` | +0.1758 | +0.0000 | +0.1117 | 0.64x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2168 | +0.0000 | +0.1108 | 0.51x | No decay |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1853 | +0.0000 | +0.0908 | 0.49x | No decay |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1824 | +0.0000 | +0.1078 | 0.59x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1940 | +0.0000 | +0.1210 | 0.62x | No decay |
| `combo_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | +0.1758 | +0.0000 | +0.0897 | 0.51x | 2016-11-30 |
| `combo_rel_diff__first_bar_return__h2_l2_pullback_continuation` | +0.1523 | +0.0000 | +0.0714 | 0.47x | 2020-02-12 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | +0.1698 | +0.0000 | +0.1018 | 0.60x | 2016-11-01 |
| `combo_mean__net_volume_flow__close_vs_open_range` | +0.1533 | +0.0000 | +0.0911 | 0.59x | 2016-11-01 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1476 | +0.0000 | +0.0898 | 0.61x | 2016-09-26 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.1965 | +0.0000 | +0.1039 | 0.53x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +0.1774 | +0.0000 | +0.0922 | 0.52x | 2016-11-30 |
| `combo_max__first_bar_return__close_vs_open_range` | +0.1719 | +0.0000 | +0.0794 | 0.46x | No decay |
| `combo_rank_min__close_vs_open_range__vwap_close_divergence_trend` | +0.1441 | +0.0000 | +0.0888 | 0.62x | 2016-11-01 |
| `combo_rank_min__bar_ret_0__bar_body_rng_0` | +0.1438 | +0.0000 | +0.0759 | 0.53x | 2013-09-23 |
| `combo_mean__opening_drive_thrust_ratio__early_order_flow_imbalance` | +0.1809 | +0.0000 | +0.0843 | 0.47x | 2016-11-30 |
| `combo_rel_diff__max_up_ret__h2_l2_pullback_continuation` | +0.1679 | +0.0000 | +0.0805 | 0.48x | 2017-02-06 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1751 | +0.0000 | +0.1150 | 0.66x | No decay |
| `combo_min__close_vs_open_range__vwap_close_divergence_trend` | +0.1428 | +0.0000 | +0.0900 | 0.63x | 2016-11-01 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | +0.1479 | +0.0000 | +0.0915 | 0.62x | 2016-11-01 |
| `combo_mean__net_volume_flow__bar_body_rng_0` | +0.1685 | +0.0000 | +0.0894 | 0.53x | 2020-02-12 |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early` | +0.1664 | +0.0000 | +0.1061 | 0.64x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +0.1880 | +0.0000 | +0.0953 | 0.51x | 2016-11-30 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.2043 | +0.0000 | +0.1311 | 0.64x | No decay |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1645 | +0.0000 | +0.0906 | 0.55x | 2022-12-15 |
| `max_up_ret` | +0.1899 | +0.0000 | +0.0920 | 0.48x | No decay |
| `combo_sig_product__max_up_ret__h2_l2_pullback_continuation` | +0.1813 | +0.0000 | +0.1062 | 0.59x | No decay |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | +0.1728 | +0.0000 | +0.0893 | 0.52x | 2014-06-05 |
| `combo_max__first_bar_return__max_down_ret` | +0.1688 | +0.0000 | +0.0789 | 0.47x | 2016-11-01 |
| `combo_min__net_volume_flow__bar_ret_0` | +0.1511 | +0.0000 | +0.0962 | 0.64x | 2016-11-01 |
| `combo_tri_median__trend_bar_close_consistency__star50_limit_proximity_early__bar_ret_0` | +0.1661 | +0.0000 | +0.0970 | 0.58x | No decay |
| `combo_mean__trend_day_regime_conviction__bar_ret_0` | +0.1658 | +0.0000 | +0.0886 | 0.53x | No decay |
| `combo_min__star50_limit_proximity_early__vwap_close_divergence_trend` | +0.1484 | +0.0000 | +0.0907 | 0.61x | 2016-09-26 |
| `combo_rank_max__max_up_ret__early_body_momentum` | +0.1841 | +0.0000 | +0.0825 | 0.45x | 2016-11-30 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.2020 | +0.0000 | +0.0907 | 0.45x | No decay |
| `combo_mean__net_volume_flow__max_down_ret` | +0.1646 | +0.0000 | +0.0937 | 0.57x | 2016-11-01 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1943 | +0.0000 | +0.0893 | 0.46x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__early_order_flow_imbalance` | +0.1738 | +0.0000 | +0.0870 | 0.50x | 2016-09-26 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1503 | +0.0000 | +0.0933 | 0.62x | 2016-09-26 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_ret_0` | +0.1798 | +0.0000 | +0.0922 | 0.51x | No decay |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1429 | +0.0000 | +0.1041 | 0.73x | 2016-09-26 |
| `combo_min__rbreaker_sell_setup_proximity_early__close_vs_open_range` | +0.1709 | +0.0000 | +0.1178 | 0.69x | No decay |
| `combo_min__max_up_ret__bar_ret_0` | +0.1818 | +0.0000 | +0.0798 | 0.44x | No decay |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | +0.1810 | +0.0000 | +0.0841 | 0.46x | 2020-01-06 |
| `combo_max__early_body_momentum__bar_body_rng_0` | +0.1659 | +0.0000 | +0.0715 | 0.43x | 2020-02-12 |
| `combo_rank_min__max_down_ret__close_vs_open_range` | +0.1535 | +0.0000 | +0.0978 | 0.64x | 2016-11-01 |
| `combo_sig_product__early_body_momentum__close_vs_open_range` | +0.1456 | +0.0000 | +0.0775 | 0.53x | 2016-11-01 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction__bar_ret_0` | +0.1848 | +0.0000 | +0.0961 | 0.52x | No decay |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | +0.1353 | +0.0000 | +0.0821 | 0.61x | 2016-11-01 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | +0.1831 | +0.0000 | +0.1002 | 0.55x | 2016-11-30 |
| `first_bar_return` | +0.1446 | +0.0000 | +0.0699 | 0.48x | 2013-09-23 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | +0.1973 | +0.0000 | +0.0774 | 0.39x | No decay |
| `combo_sig_product__max_down_ret__close_vs_open_range` | +0.1280 | +0.0000 | +0.0608 | 0.47x | 2016-09-26 |
| `combo_clamp_diff__first_bar_return__early_late_momentum_divergence` | +0.1530 | +0.0000 | +0.0777 | 0.51x | 2020-12-18 |
| `combo_mean__max_up_ret__max_down_ret` | +0.1881 | +0.0000 | +0.1024 | 0.54x | No decay |
| `combo_rel_diff__opening_drive_thrust_ratio__h2_l2_pullback_continuation` | +0.1752 | +0.0000 | +0.0864 | 0.49x | 2016-11-01 |
| `combo_rank_max__bar_ret_0__max_down_ret` | +0.1690 | +0.0000 | +0.0827 | 0.49x | No decay |
| `combo_tri_max__max_up_ret__early_body_momentum__trend_day_regime_conviction` | +0.1749 | +0.0000 | +0.0781 | 0.45x | 2016-11-01 |
| `combo_tri_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | +0.1687 | +0.0000 | +0.0987 | 0.59x | 2016-11-01 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | +0.1945 | +0.0000 | +0.0976 | 0.50x | 2026-04-07 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | +0.1871 | +0.0000 | +0.0960 | 0.51x | 2020-01-06 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1699 | +0.0000 | +0.1048 | 0.62x | No decay |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1787 | +0.0000 | +0.0873 | 0.49x | 2016-11-01 |
| `combo_rel_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | +0.1396 | +0.0000 | +0.0749 | 0.54x | 2016-11-01 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1531 | +0.0000 | +0.1058 | 0.69x | No decay |
| `combo_rank_min__early_order_flow_imbalance__bar_body_rng_0` | +0.1521 | +0.0000 | +0.0783 | 0.51x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1874 | +0.0000 | +0.1040 | 0.55x | No decay |
| `combo_tri_min__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | +0.1511 | +0.0000 | +0.1097 | 0.73x | 2016-09-26 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | +0.1974 | +0.0000 | +0.0791 | 0.40x | 2016-11-30 |
| `combo_max__max_up_ret__early_order_flow_imbalance` | +0.1661 | +0.0000 | +0.0709 | 0.43x | 2016-11-01 |
| `combo_mean__first_bar_return__close_vs_open_range` | +0.1692 | +0.0000 | +0.0936 | 0.55x | No decay |
| `combo_min__early_order_flow_imbalance__max_down_ret` | +0.1517 | +0.0000 | +0.0695 | 0.46x | 2016-11-01 |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__bar_ret_0` | +0.1672 | +0.0000 | +0.1064 | 0.64x | 2020-01-06 |
| `combo_min__first_bar_return__close_vs_open_range` | +0.1439 | +0.0000 | +0.0979 | 0.68x | 2020-01-06 |
| `combo_rank_max__max_up_ret__early_order_flow_imbalance` | +0.1733 | +0.0000 | +0.0748 | 0.43x | 2016-11-01 |
| `combo_clamp_diff__max_up_ret__h2_l2_pullback_continuation` | +0.1642 | +0.0000 | +0.0815 | 0.50x | 2017-02-06 |
| `combo_diff__volatility_expansion_trend_vector__h2_l2_pullback_continuation` | +0.1380 | +0.0000 | +0.0781 | 0.57x | 2016-11-01 |
| `combo_tri_max__max_up_ret__early_body_momentum__star50_limit_proximity_early` | +0.1735 | +0.0000 | +0.0825 | 0.48x | 2016-11-01 |
| `combo_rank_min__opening_drive_thrust_ratio__net_volume_flow` | +0.1768 | +0.0000 | +0.0939 | 0.53x | 2016-11-30 |
| `combo_rank_max__trend_day_regime_conviction__early_order_flow_imbalance` | +0.1407 | +0.0000 | +0.0702 | 0.50x | 2016-09-26 |
| `combo_rel_diff__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration` | +0.1826 | +0.0000 | +0.0960 | 0.53x | No decay |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | +0.1770 | +0.0000 | +0.0840 | 0.47x | 2016-11-30 |
| `combo_rank_min__star50_limit_proximity_early__vwap_close_divergence_trend` | +0.1514 | +0.0000 | +0.0932 | 0.62x | 2016-09-26 |
| `combo_min__early_order_flow_imbalance__close_vs_open_range` | +0.1381 | +0.0000 | +0.0719 | 0.52x | 2016-11-01 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +0.1646 | +0.0000 | +0.1015 | 0.62x | 2020-02-12 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1758 | +0.0000 | +0.0869 | 0.49x | 2016-12-29 |
| `combo_mean__max_down_ret__close_vs_open_range` | +0.1557 | +0.0000 | +0.0920 | 0.59x | 2016-11-01 |
| `combo_min__max_down_ret__close_vs_open_range` | +0.1540 | +0.0000 | +0.0988 | 0.64x | 2016-11-01 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1958 | +0.0000 | +0.1249 | 0.64x | 2016-09-26 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.1904 | +0.0000 | +0.0961 | 0.50x | No decay |
| `combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early` | +0.1433 | +0.0000 | +0.1087 | 0.76x | 2016-09-26 |
| `combo_max__early_body_momentum__close_vs_open_range` | +0.1450 | +0.0000 | +0.0793 | 0.55x | 2016-11-01 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1809 | +0.0000 | +0.0944 | 0.52x | 2019-12-05 |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | +0.1345 | +0.0000 | +0.0420 | 0.31x | 2024-08-08 |
| `combo_mean__max_up_ret__early_order_flow_imbalance` | +0.1799 | +0.0000 | +0.0733 | 0.41x | 2016-11-01 |
| `combo_mean__star50_limit_proximity_early__vwap_close_divergence_trend` | +0.1730 | +0.0000 | +0.1064 | 0.62x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | +0.1698 | +0.0000 | +0.0946 | 0.56x | 2016-09-26 |
| `combo_rank_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | +0.1762 | +0.0000 | +0.0849 | 0.48x | 2016-11-01 |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | +0.1460 | +0.0000 | +0.0833 | 0.57x | 2016-11-01 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | +0.2019 | +0.0000 | +0.1257 | 0.62x | 2016-09-26 |
| `combo_min__first_bar_return__max_down_ret` | +0.1385 | +0.0000 | +0.0836 | 0.60x | 2021-01-19 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1944 | +0.0000 | +0.1257 | 0.65x | 2016-09-26 |
| `combo_rank_min__opening_drive_thrust_ratio__early_order_flow_imbalance` | +0.1696 | +0.0000 | +0.0744 | 0.44x | 2016-11-30 |
| `combo_mean__close_vs_open_range__bar_body_rng_0` | +0.1626 | +0.0000 | +0.0958 | 0.59x | 2020-01-06 |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | +0.1708 | +0.0000 | +0.0942 | 0.55x | 2026-04-07 |
| `combo_max__star50_limit_proximity_early__first_bar_return` | +0.1678 | +0.0000 | +0.0991 | 0.59x | 2021-05-28 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | +0.1830 | +0.0000 | +0.0850 | 0.46x | 2016-11-01 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1702 | +0.0000 | +0.1021 | 0.60x | 2019-12-05 |
| `max_down_ret` | +0.1449 | +0.0000 | +0.0828 | 0.57x | 2016-09-26 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | +0.1636 | +0.0000 | +0.1238 | 0.76x | 2016-09-26 |
| `combo_max__net_volume_flow__first_bar_return` | +0.1757 | +0.0000 | +0.0731 | 0.42x | 2020-02-12 |
| `combo_rank_max__net_volume_flow__bar_ret_0` | +0.1755 | +0.0000 | +0.0742 | 0.42x | No decay |
| `combo_sig_product__max_up_ret__max_down_ret` | +0.1677 | +0.0000 | +0.1262 | 0.75x | 2014-06-05 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | +0.1796 | +0.0000 | +0.0894 | 0.50x | 2016-11-30 |
| `combo_clamp_diff__max_up_ret__shaved_bar_trend_conviction` | +0.0238 | +0.0000 | -0.0030 | -0.13x | 2010-10-15 |
| `combo_diff__first_bar_return__early_late_momentum_divergence` | +0.1521 | +0.0000 | +0.0786 | 0.52x | 2020-12-18 |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | +0.1652 | +0.0000 | +0.0778 | 0.47x | 2017-02-06 |
| `combo_rank_max__max_up_ret__shaved_bar_trend_conviction` | +0.1780 | +0.0000 | +0.0820 | 0.46x | 2016-11-01 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1456 | +0.0000 | +0.1031 | 0.71x | 2020-12-18 |
| `combo_clamp_diff__bar_body_rng_0__h2_l2_pullback_continuation` | +0.1572 | +0.0000 | +0.0828 | 0.53x | 2020-02-12 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1807 | +0.0000 | +0.1103 | 0.61x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | +0.1468 | +0.0000 | +0.0934 | 0.64x | 2016-09-26 |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | +0.1502 | +0.0000 | +0.0782 | 0.52x | 2016-11-01 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | +0.1602 | +0.0000 | +0.0871 | 0.54x | 2016-12-29 |
| `combo_rank_min__early_order_flow_imbalance__max_down_ret` | +0.1513 | +0.0000 | +0.0698 | 0.46x | 2016-11-01 |
| `combo_rank_max__early_body_momentum__close_vs_open_range` | +0.1473 | +0.0000 | +0.0820 | 0.56x | 2016-11-01 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | +0.1655 | +0.0000 | +0.0973 | 0.59x | No decay |
| `combo_max__opening_drive_thrust_ratio__vwap_close_divergence_trend` | +0.1795 | +0.0000 | +0.0844 | 0.47x | 2016-11-30 |
| `combo_min__max_up_ret__close_vs_open_range` | +0.1660 | +0.0000 | +0.1011 | 0.61x | 2020-01-06 |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | +0.1298 | +0.0000 | +0.0697 | 0.54x | 2026-04-07 |
| `combo_rank_max__max_up_ret__max_down_ret` | +0.1849 | +0.0000 | +0.0867 | 0.47x | 2016-11-30 |
| `combo_rank_max__early_body_momentum__max_down_ret` | +0.1603 | +0.0000 | +0.0778 | 0.49x | 2016-11-01 |
| `combo_max__bar_ret_0__early_order_flow_imbalance` | +0.1452 | +0.0000 | +0.0535 | 0.37x | 2016-11-30 |
| `combo_mean__first_bar_return__early_order_flow_imbalance` | +0.1563 | +0.0000 | +0.0687 | 0.44x | 2016-11-01 |
| `combo_rank_min__opening_drive_thrust_ratio__vwap_close_divergence_trend` | +0.1645 | +0.0000 | +0.0912 | 0.55x | 2016-11-01 |
| `combo_tri_median__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | +0.1495 | +0.0000 | +0.0809 | 0.54x | 2016-11-01 |
| `combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction` | +0.1395 | +0.0000 | +0.0837 | 0.60x | 2016-09-26 |
| `combo_rank_min__early_order_flow_imbalance__close_vs_open_range` | +0.1367 | +0.0000 | +0.0772 | 0.56x | 2016-11-01 |
| `combo_max__max_up_ret__close_vs_open_range` | +0.1818 | +0.0000 | +0.0860 | 0.47x | 2016-11-01 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | +0.1760 | +0.0000 | +0.0904 | 0.51x | No decay |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | +0.1531 | +0.0000 | +0.1192 | 0.78x | 2011-10-26 |
| `combo_rel_diff__net_volume_flow__h2_l2_pullback_continuation` | +0.1439 | +0.0000 | +0.0737 | 0.51x | 2016-11-01 |
| `combo_diff__bar_ret_0__h2_l2_pullback_continuation` | +0.1571 | +0.0000 | +0.0830 | 0.53x | 2017-02-06 |
| `combo_sig_product__max_down_ret__h2_l2_pullback_continuation` | +0.1235 | +0.0000 | +0.0726 | 0.59x | 2016-11-01 |
| `combo_rel_diff__bar_ret_0__late_bar_momentum` | +0.1416 | +0.0000 | +0.0672 | 0.47x | 2020-12-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | +0.1616 | +0.0000 | +0.1039 | 0.64x | No decay |
| `combo_rank_min__max_up_ret__max_down_ret` | +0.1753 | +0.0000 | +0.0999 | 0.57x | 2020-01-06 |
| `combo_rank_min__bar_ret_0__max_down_ret` | +0.1392 | +0.0000 | +0.0794 | 0.57x | No decay |
| `combo_mean__max_up_ret__close_vs_open_range` | +0.1780 | +0.0000 | +0.0939 | 0.53x | No decay |
| `combo_tri_median__max_up_ret__volume_weighted_momentum_acceleration__bar_ret_0` | +0.1501 | +0.0000 | +0.0649 | 0.43x | No decay |
| `combo_max__net_volume_flow__max_down_ret` | +0.1583 | +0.0000 | +0.0851 | 0.54x | 2016-11-30 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1956 | +0.0000 | +0.1064 | 0.54x | No decay |
| `combo_max__max_up_ret__shaved_bar_trend_conviction` | +0.1691 | +0.0000 | +0.0806 | 0.48x | 2016-11-01 |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1590 | +0.0000 | +0.0872 | 0.55x | 2016-12-29 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | +0.1679 | +0.0000 | +0.1000 | 0.60x | 2021-01-19 |
| `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction` | +0.1321 | +0.0000 | +0.1044 | 0.79x | 2016-09-26 |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | +0.1502 | +0.0000 | +0.0816 | 0.54x | 2016-09-26 |
| `combo_rank_min__trend_bar_close_consistency__max_down_ret` | +0.1388 | +0.0000 | +0.0846 | 0.61x | 2016-09-26 |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | +0.1559 | +0.0000 | +0.0932 | 0.60x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | +0.1353 | +0.0000 | +0.0951 | 0.70x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | +0.1818 | +0.0000 | +0.0889 | 0.49x | 2016-12-29 |
| `combo_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | +0.1285 | +0.0000 | +0.0653 | 0.51x | 2016-11-01 |
| `combo_rel_diff__early_order_flow_imbalance__h2_l2_pullback_continuation` | +0.1293 | +0.0000 | +0.0619 | 0.48x | 2016-11-01 |
| `combo_max__max_down_ret__close_vs_open_range` | +0.1498 | +0.0000 | +0.0831 | 0.56x | 2016-11-01 |
| `combo_diff__close_vs_open_range__h2_l2_pullback_continuation` | +0.1296 | +0.0000 | +0.0746 | 0.58x | 2016-11-01 |
| `combo_sig_product__max_up_ret__shaved_bar_trend_conviction` | +0.1686 | +0.0000 | +0.1258 | 0.75x | 2018-02-08 |
| `combo_min__max_up_ret__vwap_close_divergence_trend` | +0.1597 | +0.0000 | +0.0885 | 0.55x | No decay |
| `combo_min__max_up_ret__rsi_opening` | +0.1695 | +0.0000 | +0.0971 | 0.57x | 2020-01-06 |
| `combo_tri_max__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | +0.1885 | +0.0000 | +0.0963 | 0.51x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early` | +0.1631 | +0.0000 | +0.1220 | 0.75x | 2016-09-26 |
| `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__bar_ret_0` | +0.1385 | +0.0000 | +0.0788 | 0.57x | No decay |
| `combo_min__max_up_ret__early_order_flow_imbalance` | +0.1760 | +0.0000 | +0.0736 | 0.42x | 2020-02-12 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1579 | +0.0000 | +0.0851 | 0.54x | 2016-08-24 |
| `combo_sig_product__max_up_ret__early_order_flow_imbalance` | +0.1811 | +0.0000 | +0.1030 | 0.57x | 2017-03-07 |
| `combo_min__net_volume_flow__vwap_close_divergence_trend` | +0.1498 | +0.0000 | +0.0864 | 0.58x | 2016-11-01 |
| `combo_mean__max_down_ret__vwap_close_divergence_trend` | +0.1562 | +0.0000 | +0.0833 | 0.53x | 2016-11-01 |
| `combo_z_sum__vwap_close_divergence_trend__bar_body_rng_0` | +0.1646 | +0.0000 | +0.0883 | 0.54x | 2020-02-12 |
| `combo_min__bar_ret_0__vwap_close_divergence_trend` | +0.1427 | +0.0000 | +0.0801 | 0.56x | 2016-11-01 |
| `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early` | +0.1624 | +0.0000 | +0.1246 | 0.77x | 2016-09-26 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1678 | +0.0000 | +0.0929 | 0.55x | 2016-09-26 |
| `combo_rank_max__bar_ret_0__early_order_flow_imbalance` | +0.1477 | +0.0000 | +0.0575 | 0.39x | 2016-11-30 |
| `combo_rank_max__trend_bar_close_consistency__star50_limit_proximity_early` | +0.1539 | +0.0000 | +0.0843 | 0.55x | 2016-09-26 |
| `combo_sig_product__rsi_opening__h2_l2_pullback_continuation` | +0.1380 | +0.0000 | +0.0727 | 0.53x | 2016-11-01 |
| `combo_rel_diff__max_down_ret__h2_l2_pullback_continuation` | +0.1375 | +0.0000 | +0.0757 | 0.55x | 2016-11-01 |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | +0.1394 | +0.0000 | +0.0952 | 0.68x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1397 | +0.0000 | +0.1223 | 0.88x | 2011-12-23 |
| `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | +0.1243 | +0.0000 | +0.0820 | 0.66x | 2016-09-26 |
| `combo_max__star50_limit_proximity_early__bar_body_rng_0` | +0.1566 | +0.0000 | +0.0950 | 0.61x | 2025-07-24 |
| `combo_sig_product__bar_ret_0__early_order_flow_imbalance` | +0.1283 | +0.0000 | +0.0619 | 0.48x | 2020-02-12 |
| `combo_sig_product__early_order_flow_imbalance__bar_body_rng_0` | +0.1250 | +0.0000 | +0.0945 | 0.76x | 2016-08-24 |
| `combo_rank_max__trend_day_regime_conviction__shaved_bar_trend_conviction` | +0.1359 | +0.0000 | +0.0786 | 0.58x | 2016-09-26 |
| `combo_mean__early_order_flow_imbalance__max_down_ret` | +0.1470 | +0.0000 | +0.0717 | 0.49x | 2016-09-26 |
| `combo_mean__net_volume_flow__shaved_bar_trend_conviction` | +0.1400 | +0.0000 | +0.0770 | 0.55x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1855 | +0.0000 | +0.0729 | 0.39x | 2016-11-01 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | +0.1443 | +0.0000 | +0.0974 | 0.67x | 2016-09-26 |
| `combo_rank_max__bar_ret_0__shaved_bar_trend_conviction` | +0.1613 | +0.0000 | +0.0690 | 0.43x | No decay |
| `combo_diff__max_down_ret__h2_l2_pullback_continuation` | +0.1395 | +0.0000 | +0.0814 | 0.58x | 2016-11-01 |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | +0.1657 | +0.0000 | +0.0813 | 0.49x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | +0.1509 | +0.0000 | +0.0789 | 0.52x | 2021-07-28 |
| `combo_max__close_vs_open_range__bar_body_rng_0` | +0.1597 | +0.0000 | +0.0858 | 0.54x | No decay |
| `combo_abs_diff__max_up_ret__shaved_bar_trend_conviction` | +0.0467 | +0.0000 | +0.0360 | 0.77x | 2010-10-15 |
| `combo_diff__net_volume_flow__demark_setup_reversal_early` | +0.1809 | +0.0000 | +0.1198 | 0.66x | 2016-09-26 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1605 | +0.0000 | +0.0977 | 0.61x | No decay |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1680 | +0.0000 | +0.0792 | 0.47x | 2017-04-07 |
| `combo_clamp_diff__max_down_ret__h2_l2_pullback_continuation` | +0.1394 | +0.0000 | +0.0788 | 0.57x | 2016-11-01 |
| `combo_max__early_body_momentum__early_order_flow_imbalance` | +0.1398 | +0.0000 | +0.0585 | 0.42x | 2016-09-26 |
| `combo_rank_min__close_vs_open_range__shaved_bar_trend_conviction` | +0.1255 | +0.0000 | +0.0722 | 0.58x | 2016-11-01 |
| `combo_min__trend_bar_close_consistency__max_down_ret` | +0.1353 | +0.0000 | +0.0870 | 0.64x | 2016-09-26 |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | +0.1620 | +0.0000 | +0.0978 | 0.60x | 2016-11-01 |
| `combo_rank_max__max_down_ret__close_vs_open_range` | +0.1524 | +0.0000 | +0.0841 | 0.55x | 2016-11-01 |
| `combo_rank_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | +0.1222 | +0.0000 | +0.0750 | 0.61x | 2016-11-01 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1576 | +0.0000 | +0.0840 | 0.53x | 2016-11-01 |
| `combo_min__max_down_ret__shaved_bar_trend_conviction` | +0.1269 | +0.0000 | +0.0768 | 0.61x | 2016-09-26 |
| `combo_ratio__bar_ret_0__net_volume_flow` | +0.1031 | +0.0000 | +0.0500 | 0.49x | 2013-09-23 |
| `combo_rel_diff__net_volume_flow__demark_setup_reversal_early` | +0.1793 | +0.0000 | +0.1192 | 0.66x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1733 | +0.0000 | +0.0857 | 0.49x | 2016-12-29 |
| `combo_min__vwap_close_divergence_trend__shaved_bar_trend_conviction` | +0.1210 | +0.0000 | +0.0736 | 0.61x | 2016-11-01 |
| `combo_tri_max__net_volume_flow__star50_limit_proximity_early__bar_ret_0` | +0.1802 | +0.0000 | +0.0881 | 0.49x | No decay |
| `combo_mean__close_vs_open_range__vwap_close_divergence_trend` | +0.1397 | +0.0000 | +0.0802 | 0.57x | 2016-11-01 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1888 | +0.0000 | +0.0875 | 0.46x | 2016-11-30 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early` | +0.1503 | +0.0000 | +0.1053 | 0.70x | 2016-08-24 |
| `combo_rel_diff__early_order_flow_imbalance__demark_setup_reversal_early` | +0.1760 | +0.0000 | +0.1089 | 0.62x | 2016-09-26 |
| `combo_max__bar_ret_0__vwap_close_divergence_trend` | +0.1658 | +0.0000 | +0.0811 | 0.49x | No decay |
| `combo_max__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1655 | +0.0000 | +0.1001 | 0.60x | 2023-02-21 |
| `combo_min__close_vs_open_range__bar_body_rng_0` | +0.1476 | +0.0000 | +0.0936 | 0.63x | 2020-01-06 |
| `combo_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | +0.1527 | +0.0000 | +0.0849 | 0.56x | 2016-11-01 |
| `combo_rank_max__max_down_ret__vwap_close_divergence_trend` | +0.1478 | +0.0000 | +0.0824 | 0.56x | 2016-11-01 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | +0.1586 | +0.0000 | +0.1048 | 0.66x | 2016-09-26 |
| `combo_min__max_up_ret__shaved_bar_trend_conviction` | +0.1412 | +0.0000 | +0.0707 | 0.50x | 2019-12-05 |
| `combo_sig_product__volatility_expansion_trend_vector__early_order_flow_imbalance` | +0.1416 | +0.0000 | +0.0499 | 0.35x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction` | +0.1762 | +0.0000 | +0.1075 | 0.61x | 2016-12-29 |
| `combo_sig_product__opening_drive_thrust_ratio__early_order_flow_imbalance` | +0.1641 | +0.0000 | +0.0657 | 0.40x | 2016-11-30 |
| `early_body_momentum` | +0.1368 | +0.0000 | +0.0713 | 0.52x | 2016-11-01 |
| `combo_mean__close_vs_open_range__shaved_bar_trend_conviction` | +0.1283 | +0.0000 | +0.0758 | 0.59x | 2016-09-26 |
| `vwap_trend_channel_slope` | +0.1472 | +0.0000 | +0.0839 | 0.57x | 2016-11-01 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction` | +0.1731 | +0.0000 | +0.0960 | 0.55x | 2016-09-26 |
| `combo_min__vwap_close_divergence_trend__bar_body_rng_0` | +0.1505 | +0.0000 | +0.0877 | 0.58x | 2016-11-01 |
| `combo_rank_max__max_down_ret__h2_l2_pullback_continuation` | +0.0517 | +0.0000 | +0.0109 | 0.21x | 2010-10-15 |
| `combo_sig_product__bar_ret_0__close_vs_open_range` | +0.1369 | +0.0000 | +0.0673 | 0.49x | 2020-02-12 |
| `open_to_current_return` | +0.1490 | +0.0000 | +0.0851 | 0.57x | 2016-11-01 |
| `combo_max__first_bar_return__shaved_bar_trend_conviction` | +0.1575 | +0.0000 | +0.0667 | 0.42x | 2019-12-05 |
| `combo_min__close_vs_open_range__shaved_bar_trend_conviction` | +0.1241 | +0.0000 | +0.0681 | 0.55x | 2016-11-01 |
| `combo_mean__bar_body_rng_0__shaved_bar_trend_conviction` | +0.1538 | +0.0000 | +0.0788 | 0.51x | 2016-11-01 |
| `combo_rank_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | +0.1484 | +0.0000 | +0.0875 | 0.59x | 2016-09-26 |
| `combo_mean__max_down_ret__shaved_bar_trend_conviction` | +0.1358 | +0.0000 | +0.0768 | 0.57x | 2016-09-26 |
| `combo_mean__trend_bar_close_consistency__vwap_close_divergence_trend` | +0.1294 | +0.0000 | +0.0692 | 0.53x | 2016-11-01 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | +0.0641 | +0.0000 | -0.0211 | -0.33x | 2010-10-15 |
| `combo_min__max_down_ret__bar_body_rng_0` | +0.1432 | +0.0000 | +0.0842 | 0.59x | No decay |
| `combo_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | +0.1647 | +0.0000 | +0.1035 | 0.63x | No decay |
| `combo_max__star50_limit_proximity_early__shaved_bar_trend_conviction` | +0.1436 | +0.0000 | +0.0798 | 0.56x | 2016-09-26 |
| `combo_max__first_bar_return__bar_body_rng_0` | +0.1413 | +0.0000 | +0.0698 | 0.49x | 2013-09-23 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__vwap_close_divergence_trend` | +0.1663 | +0.0000 | +0.1057 | 0.64x | No decay |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_ret_0` | +0.1712 | +0.0000 | +0.1313 | 0.77x | 2017-01-20 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__bar_ret_0` | +0.1667 | +0.0000 | +0.1211 | 0.73x | 2017-02-27 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1606 | +0.0000 | +0.1045 | 0.65x | 2017-02-27 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1653 | +0.0000 | +0.1181 | 0.71x | 2017-01-20 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | +0.1188 | +0.0000 | +0.0937 | 0.79x | 2011-10-18 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1538 | +0.0000 | +0.1458 | 0.95x | 2016-10-24 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1538 | +0.0000 | +0.1423 | 0.93x | 2017-01-20 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | +0.1609 | +0.0000 | +0.1219 | 0.76x | 2017-01-20 |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1450 | +0.0000 | +0.1365 | 0.94x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1629 | +0.0000 | +0.1297 | 0.80x | 2016-12-21 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | +0.1683 | +0.0000 | +0.1361 | 0.81x | 2017-01-20 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1594 | +0.0000 | +0.1031 | 0.65x | 2017-01-20 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | +0.1396 | +0.0000 | +0.1314 | 0.94x | 2017-01-20 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_ret_0` | +0.1534 | +0.0000 | +0.1292 | 0.84x | 2017-01-20 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1562 | +0.0000 | +0.0990 | 0.63x | 2017-01-20 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1612 | +0.0000 | +0.1106 | 0.69x | 2017-01-20 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.1509 | +0.0000 | +0.1368 | 0.91x | 2016-10-24 |
| `combo_max__max_up_ret__bar_ret_0` | +0.1537 | +0.0000 | +0.0960 | 0.62x | 2017-04-28 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1652 | +0.0000 | +0.1362 | 0.82x | 2017-01-20 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1534 | +0.0000 | +0.1267 | 0.83x | 2016-10-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1591 | +0.0000 | +0.1185 | 0.75x | 2017-01-20 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1598 | +0.0000 | +0.1354 | 0.85x | 2016-12-21 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1661 | +0.0000 | +0.1323 | 0.80x | 2016-12-21 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | +0.0866 | +0.0000 | +0.1094 | 1.26x | 2011-10-18 |
| `combo_max__max_up_ret__volume_price_confirmation` | +0.1460 | +0.0000 | +0.0793 | 0.54x | 2017-01-20 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1649 | +0.0000 | +0.1260 | 0.76x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1747 | +0.0000 | +0.1300 | 0.74x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1391 | +0.0000 | +0.1271 | 0.91x | 2011-10-18 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | +0.1583 | +0.0000 | +0.1208 | 0.76x | 2017-02-27 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1364 | +0.0000 | +0.1056 | 0.77x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1601 | +0.0000 | +0.1273 | 0.80x | 2016-12-21 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | +0.1262 | +0.0000 | +0.0619 | 0.49x | 2017-02-27 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | +0.1552 | +0.0000 | +0.1038 | 0.67x | 2017-01-20 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | +0.1583 | +0.0000 | +0.1347 | 0.85x | 2016-10-24 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend` | +0.1268 | +0.0000 | +0.0519 | 0.41x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | +0.1402 | +0.0000 | +0.1231 | 0.88x | 2011-11-16 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | +0.1539 | +0.0000 | +0.1129 | 0.73x | 2017-01-20 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1393 | +0.0000 | +0.1086 | 0.78x | 2017-01-20 |
| `combo_rank_max__volatility_expansion_trend_vector__volume_price_confirmation` | +0.1542 | +0.0000 | +0.0887 | 0.58x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1524 | +0.0000 | +0.1393 | 0.91x | 2016-10-24 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | +0.1234 | +0.0000 | +0.1287 | 1.04x | 2011-10-18 |
| `combo_min__first_bar_return__limit_down_proximity_early` | +0.1274 | +0.0000 | +0.1216 | 0.95x | 2011-10-18 |
| `combo_max__rbreaker_sell_setup_proximity_early__gap_pct` | +0.1141 | +0.0000 | +0.1139 | 1.00x | 2011-09-09 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | +0.1529 | +0.0000 | +0.1034 | 0.68x | 2017-01-20 |
| `combo_clamp_diff__bar_body_rng_0__volume_weighted_momentum_acceleration` | +0.1317 | +0.0000 | +0.0903 | 0.69x | 2011-03-11 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | +0.1518 | +0.0000 | +0.1122 | 0.74x | 2016-10-24 |
| `max_up_ret` | +0.1512 | +0.0000 | +0.1014 | 0.67x | 2017-01-20 |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | +0.1476 | +0.0000 | +0.1165 | 0.79x | 2016-10-24 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1419 | +0.0000 | +0.1333 | 0.94x | 2016-09-14 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1405 | +0.0000 | +0.1385 | 0.99x | 2016-09-14 |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | +0.1627 | +0.0000 | +0.1038 | 0.64x | 2017-01-20 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | +0.1172 | +0.0000 | +0.1130 | 0.96x | 2026-03-27 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +0.1544 | +0.0000 | +0.1021 | 0.66x | 2016-12-21 |
| `combo_ifelse__gap_pct__max_up_ret__bar_ret_0` | +0.1537 | +0.0000 | +0.0817 | 0.53x | 2017-01-20 |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_first_30min_return` | +0.1179 | +0.0000 | +0.0909 | 0.77x | 2011-06-14 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +0.1244 | +0.0000 | +0.1076 | 0.86x | 2017-01-20 |
| `opening_drive_thrust_ratio` | +0.1417 | +0.0000 | +0.1176 | 0.83x | 2016-10-24 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | +0.1186 | +0.0000 | +0.1151 | 0.97x | 2022-01-24 |
| `combo_z_sum__max_up_ret__gap_pct` | +0.1618 | +0.0000 | +0.1357 | 0.84x | 2017-01-20 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | +0.1527 | +0.0000 | +0.1272 | 0.83x | 2017-01-20 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_first_30min_return` | +0.1183 | +0.0000 | +0.0981 | 0.83x | 2016-11-22 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | +0.1429 | +0.0000 | +0.1243 | 0.87x | 2011-10-18 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__max_up_ret` | +0.1424 | +0.0000 | +0.1038 | 0.73x | 2016-10-24 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | +0.1511 | +0.0000 | +0.1077 | 0.71x | 2016-11-22 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | +0.1280 | +0.0000 | +0.0701 | 0.55x | 2016-11-22 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__gap_pct` | +0.1337 | +0.0000 | +0.0822 | 0.61x | 2017-01-20 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct` | +0.1154 | +0.0000 | +0.1191 | 1.03x | 2011-09-09 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__star50_limit_proximity_early` | +0.1413 | +0.0000 | +0.1344 | 0.95x | 2011-10-18 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1417 | +0.0000 | +0.1277 | 0.90x | 2017-01-20 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev` | +0.1237 | +0.0000 | +0.0720 | 0.58x | 2017-02-27 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_trend` | +0.1287 | +0.0000 | +0.0634 | 0.49x | 2016-11-22 |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | +0.1248 | +0.0000 | +0.1187 | 0.95x | 2011-03-11 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1328 | +0.0000 | +0.1097 | 0.83x | 2016-10-24 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return` | +0.1121 | +0.0000 | +0.1034 | 0.92x | 2017-01-20 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | +0.1477 | +0.0000 | +0.1220 | 0.83x | 2017-01-20 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1067 | +0.0000 | +0.1090 | 1.02x | 2011-10-18 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__first_bar_return` | +0.1477 | +0.0000 | +0.0884 | 0.60x | 2016-10-24 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0622 | +0.0000 | -0.0132 | -0.21x | 2012-02-22 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 83.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 41.0%, mean lock Sharpe=+0.2235). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 41.0%, mean lock Sharpe=+0.3246). Consider relaxing this gate.
3. **300ETF `single` — B3 Composite Floor too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 41.0%, mean lock Sharpe=+0.2946). Consider relaxing this gate.
4. **300ETF `single` — B4 Correlation Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 41.0%, mean lock Sharpe=+0.4623). Consider relaxing this gate.
5. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2013). Consider relaxing this gate.
6. **300ETF `short` — BH-FDR Gate too strict**: 85.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=+0.2747). Consider relaxing this gate.
7. **300ETF `short` — B3 Composite Floor too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.0234). Consider relaxing this gate.
8. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.0834). Consider relaxing this gate.
9. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.2106). Consider relaxing this gate.
10. **50ETF `short` — BH-FDR Gate too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.5453). Consider relaxing this gate.
11. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 47.0%, mean lock Sharpe=+0.7404). Consider relaxing this gate.
12. **500ETF `single` — B2 Rolling Guard too strict**: 76.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 47.0%, mean lock Sharpe=+0.1512). Consider relaxing this gate.
13. **500ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 47.0%, mean lock Sharpe=+0.5836). Consider relaxing this gate.
14. **500ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 47.0%, mean lock Sharpe=+0.6237). Consider relaxing this gate.
15. **500ETF `long` — BH-FDR Gate too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 19.0%, mean lock Sharpe=-0.1712). Consider relaxing this gate.
16. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.1404). Consider relaxing this gate.
17. **159915ETF `single` — 7-Year Jackknife Sign Stability too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 55.0%, mean lock Sharpe=+0.8878). Consider relaxing this gate.
18. **159915ETF `single` — B2 Rolling Guard too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 55.0%, mean lock Sharpe=+0.7932). Consider relaxing this gate.
19. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 55.0%, mean lock Sharpe=+0.7746). Consider relaxing this gate.
20. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 55.0%, mean lock Sharpe=+1.2305). Consider relaxing this gate.
21. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+0.6527). Consider relaxing this gate.
22. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.1320). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
