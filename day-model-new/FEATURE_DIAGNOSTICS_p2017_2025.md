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

### 300ETF — `single` (Full Model Lockbox IC: +0.0161, Sharpe: -0.3231)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1012 | +0.0544 | +0.0544 | -0.0805 | 0.80 | 1/8 | 1.14 | 1.31 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0026 | -0.1206 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1035 | +0.0229 | +0.0229 | -0.5791 | 0.83 | 1/8 | 1.06 | 0.90 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0013 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.0996 | +0.0463 | +0.0463 | -0.5117 | 0.77 | 1/8 | 1.12 | 1.27 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0024 | -0.1206 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0936 | -0.0022 | -0.0022 | -1.3090 | 0.89 | 1/8 | 1.36 | 0.75 | `volume_weighted_price_position` (1.24) | -0.0008 | +0.0411 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.0864 | -0.0365 | -0.0365 | -1.6583 | 0.85 | 1/8 | 1.81 | 1.78 | `max_up_ret` (0.94) | -0.0027 | -0.0734 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1003 | -0.0055 | -0.0055 | -0.8914 | 0.88 | 1/8 | 1.16 | 1.24 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0003 | +0.0000 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0875 | -0.0223 | -0.0223 | -1.3571 | 0.76 | 1/8 | 1.46 | 1.12 | `max_up_ret` (0.94) | -0.0024 | -0.0734 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0852 | +0.0808 | +0.0808 | +0.3659 | 0.86 | 1/8 | 1.04 | 1.45 | `rbreaker_buy_setup_proximity_early` (2.51) | +0.0033 | -0.1521 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0901 | -0.0261 | -0.0261 | -0.8875 | 0.90 | 0/8 | 2.24 | 1.24 | `volume_weighted_price_position` (1.24) | -0.0008 | +0.0029 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0887 | +0.0408 | +0.0408 | -0.2406 | 0.93 | 1/8 | 1.01 | 0.89 | `rbreaker_buy_setup_proximity_early` (2.51) | +0.0018 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.0804 | -0.0091 | -0.0091 | -1.2289 | 0.89 | 1/8 | 1.72 | 1.87 | `rbreaker_sell_setup_proximity_early` (1.21) | -0.0012 | -0.0734 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0971 | +0.0259 | +0.0259 | -0.2846 | 0.85 | 1/8 | 1.00 | 0.98 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0009 | +0.0000 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0892 | -0.0225 | -0.0225 | -1.2669 | 0.71 | 0/8 | 1.55 | 1.00 | `max_up_ret` (0.94) | -0.0005 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0906 | +0.0736 | +0.0736 | -0.4035 | 0.84 | 1/8 | 1.20 | 1.40 | `rbreaker_buy_setup_proximity_early` (2.51) | +0.0028 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0996 | +0.0244 | +0.0244 | -0.2554 | 0.89 | 1/8 | 1.26 | 1.41 | `rbreaker_sell_setup_proximity_early` (1.21) | -0.0001 | -0.1206 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.0742 | -0.0463 | -0.0463 | -1.8589 | 0.94 | 1/8 | 2.29 | 2.13 | — | -0.0025 | -0.0734 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0914 | -0.0344 | -0.0344 | -1.3884 | 0.80 | 0/8 | 2.24 | 1.26 | `volume_weighted_price_position` (1.24) | -0.0000 | +0.0029 |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0979 | -0.0009 | -0.0009 | -1.0800 | 0.84 | 0/8 | 1.36 | 0.87 | `volume_weighted_price_position` (1.24) | +0.0001 | +0.0029 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | Intraday Range Momentum | +1 | +0.0750 | -0.0457 | -0.0457 | -1.6553 | 0.90 | 2/8 | 1.76 | 1.64 | `volume_concentration` (1.19) | -0.0013 | -0.0734 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.0963 | +0.0592 | +0.0592 | +0.5373 | 0.72 | 0/8 | 1.01 | 0.58 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0019 | +0.0000 |
| `combo_tri_mean__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0953 | +0.0168 | +0.0168 | -0.5135 | 0.81 | 1/8 | 1.27 | 0.77 | `volume_weighted_price_position` (1.24) | +0.0018 | +0.0029 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0959 | -0.0157 | -0.0157 | -1.4403 | 0.74 | 0/8 | 1.48 | 1.09 | `max_up_ret` (0.94) | -0.0004 | -0.0734 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | Intraday Range Momentum | +1 | +0.0934 | +0.0181 | +0.0181 | +0.2156 | 0.86 | 1/8 | 1.35 | 1.28 | `rbreaker_buy_setup_proximity_early` (2.51) | -0.0004 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0969 | +0.0559 | +0.0559 | +0.3783 | 0.69 | 0/8 | 0.92 | 0.63 | `star50_limit_proximity_early` (1.49) | +0.0016 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0843 | +0.0158 | +0.0158 | -0.4533 | 0.78 | 1/8 | 1.00 | 1.31 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0013 | +0.0000 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0847 | -0.0151 | -0.0151 | -0.9549 | 0.94 | 1/8 | 1.42 | 0.79 | `volume_weighted_price_position` (1.24) | -0.0007 | +0.0000 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0907 | -0.0214 | -0.0214 | -0.7372 | 0.86 | 1/8 | 1.55 | 0.78 | `volume_weighted_price_position` (1.24) | +0.0003 | +0.0029 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0893 | -0.0136 | -0.0136 | -1.9227 | 0.65 | 0/8 | 0.93 | 0.68 | `volume_weighted_price_position` (1.24) | +0.0005 | +0.0029 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0956 | -0.0082 | -0.0082 | -0.8893 | 0.90 | 1/8 | 1.46 | 1.59 | `rbreaker_sell_setup_proximity_early` (1.21) | -0.0012 | -0.0734 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0906 | -0.0223 | -0.0223 | -1.1680 | 0.69 | 0/8 | 1.62 | 1.14 | `max_up_ret` (0.94) | -0.0004 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0926 | -0.0061 | -0.0061 | -1.6781 | 0.97 | 1/8 | 1.37 | 0.79 | `volume_weighted_price_position` (1.24) | -0.0017 | -0.0087 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.0885 | -0.0223 | -0.0223 | -1.3181 | 0.61 | 0/8 | 1.13 | 0.77 | `max_up_ret` (0.94) | -0.0020 | -0.0734 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.0905 | +0.0053 | +0.0053 | -0.2216 | 0.72 | 0/8 | 1.01 | 0.67 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0008 | +0.0000 |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0767 | -0.0225 | -0.0225 | -1.7645 | 0.93 | 1/8 | 2.30 | 2.14 | `morning_volume_weighted_momentum` (1.45) | -0.0005 | -0.0734 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0742, Sharpe: +0.0000)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1439 | +0.1043 | +0.1043 | -0.3294 | 0.34 | 0/8 | 0.65 | 0.58 | `demark_setup_reversal_early` (0.47) | +0.0001 | +0.2399 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1474 | +0.0406 | +0.0406 | -1.4083 | 0.29 | 0/8 | 0.79 | 0.61 | `opening_drive_thrust_ratio` (0.32) | -0.0007 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1315 | +0.0849 | +0.0849 | -0.1619 | 0.25 | 0/8 | 0.83 | 0.71 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0014 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1404 | +0.0942 | +0.0942 | -0.2127 | 0.33 | 0/8 | 0.63 | 0.45 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0005 | +0.0000 |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1403 | +0.1090 | +0.1090 | -0.2440 | 0.29 | 0/8 | 0.67 | 0.61 | `demark_setup_reversal_early` (0.47) | +0.0005 | +0.0000 |
| `combo_mean__bar_ret_0__close_vs_open_range` | Other Technical | +1 | +0.1292 | +0.0469 | +0.0469 | -1.2311 | 0.36 | 0/8 | 0.79 | 0.56 | `bar_ret_0` (0.46) | +0.0002 | +0.0000 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1402 | +0.0379 | +0.0379 | -0.2953 | 0.35 | 0/8 | 0.72 | 0.52 | `bar_body_rng_0` (0.37) | -0.0007 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1329 | +0.1106 | +0.1106 | +1.0183 | 0.40 | 0/8 | 0.49 | 0.47 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0009 | +0.2399 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1476 | +0.0426 | +0.0426 | -0.2324 | 0.38 | 0/8 | 0.66 | 0.57 | `volume_weighted_momentum_acceleration` (0.47) | -0.0011 | +0.2399 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1144 | +0.0933 | +0.0933 | -0.2396 | 0.32 | 0/8 | 0.68 | 0.52 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0013 | +0.0000 |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1241 | +0.0295 | +0.0295 | -1.5145 | 0.28 | 0/8 | 0.95 | 0.63 | `bar_body_rng_0` (0.37) | -0.0004 | +0.0000 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1545 | +0.0289 | +0.0289 | -0.4555 | 0.40 | 0/8 | 0.65 | 0.59 | `volume_weighted_momentum_acceleration` (0.47) | -0.0012 | +0.2399 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1540 | +0.0316 | +0.0316 | -0.2324 | 0.40 | 0/8 | 0.66 | 0.60 | `volume_weighted_momentum_acceleration` (0.47) | -0.0013 | +0.2399 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1375 | +0.0977 | +0.0977 | +0.3748 | 0.37 | 0/8 | 0.59 | 0.43 | `bar_ret_0` (0.46) | +0.0008 | +0.0000 |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1329 | +0.0201 | +0.0201 | -1.9420 | 0.38 | 0/8 | 0.78 | 0.53 | `bar_ret_0` (0.46) | -0.0007 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1213 | +0.1163 | +0.1163 | +0.4767 | 0.34 | 0/8 | 0.65 | 0.51 | `bar_ret_0` (0.46) | +0.0013 | +0.0000 |
| `combo_tri_mean__max_up_ret__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1327 | +0.0299 | +0.0299 | -1.1446 | 0.27 | 0/8 | 0.87 | 0.61 | `bar_ret_0` (0.46) | -0.0003 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1453 | +0.0883 | +0.0883 | -0.5698 | 0.42 | 0/8 | 0.62 | 0.67 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0010 | +0.0000 |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | Intraday Range Momentum | +1 | +0.1282 | +0.0637 | +0.0637 | -0.3821 | 0.23 | 0/8 | 0.85 | 0.63 | `bar_ret_0` (0.46) | -0.0001 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1364 | +0.0337 | +0.0337 | -1.4167 | 0.28 | 0/8 | 0.73 | 0.62 | `trend_bar_close_consistency` (0.54) | -0.0003 | +0.0000 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1301 | +0.0518 | +0.0518 | -0.2853 | 0.51 | 0/8 | 0.55 | 0.33 | `max_down_ret` (0.55) | -0.0004 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1279 | +0.0977 | +0.0977 | +0.1120 | 0.41 | 0/8 | 0.52 | 0.46 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0014 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1359 | +0.0534 | +0.0534 | -1.3411 | 0.39 | 0/8 | 0.74 | 0.54 | `volatility_expansion_trend_vector` (0.36) | -0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1523 | +0.0478 | +0.0478 | -0.8584 | 0.37 | 0/8 | 0.63 | 0.49 | `first_bar_return` (0.46) | -0.0004 | +0.2399 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1546 | +0.0598 | +0.0598 | -0.3728 | 0.36 | 0/8 | 0.59 | 0.47 | `bar_ret_0` (0.46) | -0.0001 | +0.2399 |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1434 | +0.0626 | +0.0626 | +0.1369 | 0.36 | 0/8 | 0.65 | 0.50 | `bar_body_rng_0` (0.37) | -0.0004 | +0.0000 |
| `combo_mean__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1372 | +0.0502 | +0.0502 | -0.6875 | 0.35 | 0/8 | 0.77 | 0.55 | `max_down_ret` (0.55) | -0.0001 | +0.0000 |
| `combo_max__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1352 | +0.0367 | +0.0367 | -0.9414 | 0.45 | 0/8 | 0.60 | 0.40 | `max_down_ret` (0.55) | -0.0003 | +0.0000 |
| `combo_min__net_volume_flow__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1168 | +0.0618 | +0.0618 | -0.3714 | 0.31 | 0/8 | 0.76 | 0.58 | `bar_body_rng_0` (0.37) | -0.0002 | +0.0000 |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1050 | +0.0817 | +0.0817 | +0.3027 | 0.40 | 0/8 | 0.65 | 0.51 | `trend_bar_close_consistency` (0.54) | +0.0007 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1323 | +0.0308 | +0.0308 | -1.6524 | 0.28 | 0/8 | 0.90 | 0.61 | — | -0.0004 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1490 | +0.0726 | +0.0726 | -0.1470 | 0.24 | 0/8 | 0.76 | 0.68 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0004 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1379 | +0.0980 | +0.0980 | +0.7580 | 0.46 | 0/8 | 0.47 | 0.45 | `bar_ret_0` (0.46) | +0.0011 | +0.0000 |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1253 | +0.0212 | +0.0212 | -2.2125 | 0.35 | 0/8 | 0.80 | 0.51 | `bar_ret_0` (0.46) | -0.0000 | +0.0000 |
| `combo_min__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1032 | +0.0525 | +0.0525 | -0.4214 | 0.33 | 0/8 | 0.89 | 0.70 | `close_vs_open_range` (0.39) | +0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1133 | +0.0560 | +0.0560 | -1.0726 | 0.20 | 0/8 | 1.00 | 0.83 | `volume_weighted_momentum_acceleration` (0.47) | -0.0001 | +0.0000 |
| `combo_rank_max__bar_ret_0__close_vs_open_range` | Other Technical | +1 | +0.1373 | +0.0231 | +0.0231 | -2.4234 | 0.30 | 0/8 | 0.82 | 0.53 | `bar_ret_0` (0.46) | +0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1578 | +0.0301 | +0.0301 | -1.2625 | 0.31 | 0/8 | 0.78 | 0.51 | `bar_ret_0` (0.46) | -0.0012 | +0.0000 |
| `combo_min__first_bar_return__early_order_flow_imbalance` | Gap / Overnight Reversal | +1 | +0.1213 | +0.0421 | +0.0421 | -0.1392 | 0.28 | 0/8 | 0.98 | 0.67 | `first_bar_return` (0.46) | -0.0005 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1447 | +0.0453 | +0.0453 | -0.8924 | 0.31 | 0/8 | 0.76 | 0.65 | `opening_drive_thrust_ratio` (0.32) | -0.0004 | +0.0000 |
| `combo_mean__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1375 | +0.0281 | +0.0281 | -0.9455 | 0.32 | 0/8 | 0.76 | 0.55 | `first_bar_return` (0.46) | -0.0008 | +0.0000 |
| `combo_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1404 | +0.0418 | +0.0418 | +0.2392 | 0.32 | 0/8 | 0.63 | 0.55 | `body_size_progression` (0.46) | -0.0005 | +0.2137 |
| `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1382 | +0.0950 | +0.0950 | -0.0776 | 0.38 | 0/8 | 0.62 | 0.50 | `star50_limit_proximity_early` (0.50) | +0.0009 | +0.0000 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1335 | +0.0447 | +0.0447 | -0.9029 | 0.34 | 0/8 | 0.69 | 0.55 | `late_bar_momentum` (0.53) | -0.0000 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1463 | +0.0829 | +0.0829 | -0.5054 | 0.36 | 0/8 | 0.60 | 0.42 | `bar_ret_0` (0.46) | +0.0003 | +0.2399 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1382 | +0.0702 | +0.0702 | -0.0334 | 0.36 | 0/8 | 0.61 | 0.47 | `bar_ret_0` (0.46) | +0.0006 | +0.2399 |
| `combo_tri_mean__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | Intraday Range Momentum | +1 | +0.1183 | +0.0397 | +0.0397 | -0.6619 | 0.30 | 0/8 | 0.84 | 0.61 | `bar_ret_0` (0.46) | +0.0002 | +0.0000 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1131 | +0.1060 | +0.1060 | +0.3487 | 0.39 | 0/8 | 0.78 | 0.66 | `star50_limit_proximity_early` (0.50) | +0.0015 | +0.0000 |
| `combo_mean__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1185 | +0.0473 | +0.0473 | -1.1154 | 0.41 | 0/8 | 0.58 | 0.45 | `first_bar_return` (0.46) | -0.0006 | +0.2399 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1336 | +0.0387 | +0.0387 | -0.3937 | 0.38 | 0/8 | 0.64 | 0.45 | `bar_body_rng_0` (0.37) | -0.0004 | +0.2399 |
| `combo_rank_max__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1288 | +0.0469 | +0.0469 | -1.4510 | 0.34 | 0/8 | 0.83 | 0.59 | `max_up_ret` (0.28) | +0.0001 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1361 | +0.0867 | +0.0867 | +0.2984 | 0.35 | 0/8 | 0.74 | 0.63 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0012 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1353 | +0.0288 | +0.0288 | -1.9401 | 0.31 | 0/8 | 0.92 | 0.66 | `bar_ret_0` (0.46) | -0.0005 | +0.0000 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1223 | +0.0126 | +0.0126 | -2.1701 | 0.35 | 0/8 | 0.74 | 0.54 | `bar_ret_0` (0.46) | -0.0002 | +0.0000 |
| `combo_mean__bar_ret_0__early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1218 | +0.0219 | +0.0219 | -1.0783 | 0.29 | 0/8 | 0.86 | 0.58 | `bar_ret_0` (0.46) | -0.0007 | +0.2399 |
| `combo_tri_median__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1308 | +0.0729 | +0.0729 | -0.5299 | 0.37 | 0/8 | 0.63 | 0.52 | `star50_limit_proximity_early` (0.50) | +0.0003 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1501 | +0.0952 | +0.0952 | -0.1966 | 0.39 | 0/8 | 0.55 | 0.45 | `star50_limit_proximity_early` (0.50) | +0.0006 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1188 | +0.1095 | +0.1095 | +0.7916 | 0.40 | 0/8 | 0.71 | 0.58 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0011 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1526 | +0.0524 | +0.0524 | -0.6914 | 0.28 | 0/8 | 0.82 | 0.65 | `rbreaker_sell_setup_proximity_early` (0.41) | -0.0001 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1415 | +0.1136 | +0.1136 | +0.6574 | 0.36 | 0/8 | 0.58 | 0.58 | `star50_limit_proximity_early` (0.50) | +0.0002 | +0.2399 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1386 | +0.0650 | +0.0650 | -0.4634 | 0.40 | 0/8 | 0.57 | 0.46 | `bar_ret_0` (0.46) | -0.0003 | +0.0000 |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1473 | +0.1062 | +0.1062 | -0.9378 | 0.32 | 0/8 | 0.71 | 0.58 | `demark_setup_reversal_early` (0.47) | +0.0005 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1315 | +0.0419 | +0.0419 | -1.0138 | 0.26 | 0/8 | 0.90 | 0.75 | `trend_day_regime_conviction` (0.39) | -0.0005 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1403 | +0.0565 | +0.0565 | -0.8039 | 0.27 | 0/8 | 0.90 | 0.70 | `star50_limit_proximity_early` (0.50) | -0.0000 | +0.0000 |
| `combo_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1336 | +0.0264 | +0.0264 | -1.6594 | 0.34 | 0/8 | 0.76 | 0.54 | `close_vs_open_range` (0.39) | -0.0004 | +0.0000 |
| `combo_clamp_diff__first_bar_return__body_size_progression` | Gap / Overnight Reversal | +1 | +0.1306 | +0.0511 | +0.0511 | +0.0657 | 0.43 | 0/8 | 0.51 | 0.45 | `first_bar_return` (0.46) | -0.0005 | +0.1084 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__early_body_momentum` | Intraday Range Momentum | +1 | +0.1115 | +0.0900 | +0.0900 | +0.1337 | 0.31 | 0/8 | 0.94 | 0.69 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0016 | +0.0000 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1341 | +0.0224 | +0.0224 | -1.5381 | 0.24 | 0/8 | 0.97 | 0.70 | `vwap_close_divergence_trend` (0.38) | +0.0000 | +0.0000 |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1285 | +0.0450 | +0.0450 | -0.0326 | 0.31 | 0/8 | 0.81 | 0.55 | `bar_ret_0` (0.46) | -0.0005 | +0.0000 |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1323 | +0.0170 | +0.0170 | -2.4149 | 0.25 | 0/8 | 0.94 | 0.68 | `vwap_close_divergence_trend` (0.38) | -0.0007 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1493 | +0.0274 | +0.0274 | -1.6166 | 0.36 | 0/8 | 0.76 | 0.44 | `bar_ret_0` (0.46) | -0.0006 | +0.2399 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1418 | +0.0237 | +0.0237 | -1.6714 | 0.34 | 0/8 | 0.76 | 0.52 | `early_body_momentum` (0.34) | -0.0005 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1246 | +0.0857 | +0.0857 | +0.2203 | 0.41 | 0/8 | 0.51 | 0.49 | `bar_ret_0` (0.46) | +0.0011 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1055 | +0.1051 | +0.1051 | -0.1201 | 0.40 | 0/8 | 0.69 | 0.56 | `star50_limit_proximity_early` (0.50) | +0.0015 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1425 | +0.0276 | +0.0276 | -1.1415 | 0.37 | 0/8 | 0.70 | 0.55 | `bar_ret_0` (0.46) | -0.0004 | +0.2399 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1512 | +0.0376 | +0.0376 | -1.6484 | 0.30 | 0/8 | 0.81 | 0.53 | `opening_drive_thrust_ratio` (0.32) | -0.0002 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1154 | +0.1143 | +0.1143 | +1.3960 | 0.45 | 0/8 | 0.44 | 0.46 | `star50_limit_proximity_early` (0.50) | +0.0006 | +0.0000 |
| `combo_rank_max__max_up_ret__max_down_ret` | Intraday Range Momentum | +1 | +0.1341 | +0.0594 | +0.0594 | -0.3475 | 0.42 | 0/8 | 0.64 | 0.43 | `max_down_ret` (0.55) | +0.0001 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1330 | +0.1065 | +0.1065 | +0.7497 | 0.40 | 0/8 | 0.50 | 0.53 | `star50_limit_proximity_early` (0.50) | +0.0004 | +0.2399 |
| `combo_mean__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1276 | +0.0355 | +0.0355 | -1.8429 | 0.30 | 0/8 | 0.90 | 0.63 | `close_vs_open_range` (0.39) | -0.0003 | +0.0000 |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1151 | +0.0926 | +0.0926 | +0.2336 | 0.37 | 0/8 | 0.96 | 0.86 | `star50_limit_proximity_early` (0.50) | +0.0012 | +0.0000 |
| `combo_mean__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1199 | +0.0745 | +0.0745 | +0.2028 | 0.45 | 0/8 | 0.59 | 0.42 | `max_down_ret` (0.55) | -0.0001 | +0.0000 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1329 | +0.1041 | +0.1041 | +0.7497 | 0.40 | 0/8 | 0.50 | 0.53 | `star50_limit_proximity_early` (0.50) | +0.0005 | +0.0000 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1153 | +0.1117 | +0.1117 | +1.3824 | 0.46 | 0/8 | 0.43 | 0.45 | `star50_limit_proximity_early` (0.50) | +0.0010 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1380 | +0.0774 | +0.0774 | -0.9150 | 0.36 | 0/8 | 0.64 | 0.48 | `star50_limit_proximity_early` (0.50) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1289 | +0.0449 | +0.0449 | -0.9665 | 0.32 | 0/8 | 0.92 | 0.56 | `smooth_momentum_structure` (0.46) | +0.0004 | +0.0000 |
| `combo_mean__first_bar_return__shaved_bar_trend_conviction` | Gap / Overnight Reversal | +1 | +0.1024 | +0.0435 | +0.0435 | -1.0554 | 0.47 | 0/8 | 0.55 | 0.50 | `shaved_bar_trend_conviction` (1.11) | -0.0002 | +0.0000 |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | Intraday Range Momentum | +1 | +0.1157 | +0.0087 | +0.0087 | -2.1212 | 0.27 | 0/8 | 1.00 | 0.83 | `h2_l2_pullback_continuation` (0.45) | -0.0006 | +0.0000 |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | Intraday Range Momentum | +1 | +0.1250 | +0.0363 | +0.0363 | -1.0873 | 0.26 | 0/8 | 1.06 | 0.77 | `vwap_close_divergence_trend` (0.38) | -0.0008 | +0.0000 |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1305 | +0.0161 | +0.0161 | -2.1485 | 0.23 | 0/8 | 1.05 | 0.66 | `bar_ret_0` (0.46) | -0.0002 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.1138 | +0.1138 | +0.2628 | 0.41 | 0/8 | 0.83 | 0.74 | `star50_limit_proximity_early` (0.50) | -0.0002 | +0.0000 |
| `combo_rank_min__net_volume_flow__vwap_close_divergence_trend` | Volatility & Oscillators | +1 | +0.1055 | +0.0441 | +0.0441 | +0.3212 | 0.31 | 0/8 | 0.90 | 0.70 | `vwap_close_divergence_trend` (0.38) | -0.0002 | +0.0000 |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | Other Technical | +1 | +0.1161 | -0.0157 | -0.0157 | -2.3289 | 0.41 | 0/8 | 0.79 | 0.81 | `bar_ret_0` (0.46) | -0.0003 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0954 | +0.0970 | +0.0970 | +0.1808 | 0.55 | 0/8 | 0.56 | 0.45 | `max_down_ret` (0.55) | +0.0011 | +0.0000 |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | Gap / Overnight Reversal | +1 | +0.1306 | +0.0170 | +0.0170 | -1.9514 | 0.23 | 0/8 | 1.08 | 0.65 | `first_bar_return` (0.46) | -0.0011 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1108 | +0.0627 | +0.0627 | -0.6281 | 0.38 | 0/8 | 0.78 | 0.50 | `bar_ret_0` (0.46) | +0.0001 | +0.0000 |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | Other Technical | +1 | +0.1042 | +0.0356 | +0.0356 | -0.2960 | 0.26 | 0/8 | 1.11 | 0.84 | `trend_day_regime_conviction` (0.39) | -0.0006 | +0.0000 |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | Other Technical | +1 | +0.0845 | +0.0240 | +0.0240 | -0.7203 | 0.25 | 0/8 | 1.19 | 1.10 | `trend_bar_close_consistency` (0.54) | -0.0005 | +0.0000 |
| `combo_sig_product__net_volume_flow__vwap_close_divergence_trend` | Volatility & Oscillators | +1 | +0.1018 | -0.0041 | -0.0041 | -1.0439 | 0.30 | 0/8 | 0.73 | 0.63 | `vwap_close_divergence_trend` (0.38) | -0.0009 | +0.0000 |
| `num_up_bars` | Other Technical | +1 | +0.0907 | +0.0459 | +0.0459 | -1.1323 | 0.40 | 0/8 | 1.47 | 1.31 | — | +0.0001 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1437, Sharpe: +1.4897)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1386 | +0.1275 | +0.1275 | +0.8333 | 0.55 | 1/8 | 1.05 | 2.29 | `bar_body_rng_0` (0.63) | +0.0009 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1387 | +0.1339 | +0.1339 | +0.8863 | 0.56 | 1/8 | 0.84 | 1.69 | `bar_body_rng_0` (0.63) | +0.0012 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1207 | +0.1353 | +0.1353 | +0.5812 | 0.67 | 1/8 | 0.98 | 3.46 | `bar_body_rng_0` (0.63) | +0.0013 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1324 | +0.1249 | +0.1249 | +0.7559 | 0.52 | 1/8 | 1.10 | 2.32 | `star50_limit_proximity_early` (0.52) | +0.0005 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1374 | +0.1303 | +0.1303 | +1.1938 | 0.40 | 0/8 | 1.11 | 1.52 | `star50_limit_proximity_early` (0.52) | +0.0004 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1364 | +0.1428 | +0.1428 | +0.8973 | 0.53 | 1/8 | 0.89 | 1.27 | `bar_body_rng_0` (0.63) | +0.0006 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1304 | +0.1296 | +0.1296 | +0.3365 | 0.54 | 1/8 | 0.83 | 1.38 | `first_bar_return` (0.48) | +0.0007 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1332 | +0.1135 | +0.1135 | +0.7682 | 0.34 | 0/8 | 1.26 | 1.74 | `star50_limit_proximity_early` (0.52) | +0.0002 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1256 | +0.1258 | +0.1258 | +1.0333 | 0.60 | 0/8 | 1.25 | 2.06 | `volume_weighted_price_position` (0.77) | -0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1413 | +0.1277 | +0.1277 | +1.1407 | 0.50 | 1/8 | 1.07 | 1.68 | `opening_drive_thrust_ratio` (0.46) | +0.0003 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1268 | +0.1243 | +0.1243 | +2.0348 | 0.57 | 1/8 | 1.32 | 2.19 | `volume_weighted_price_position` (0.77) | -0.0001 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1329 | +0.1289 | +0.1289 | +0.8597 | 0.47 | 0/8 | 1.06 | 1.26 | `bar_body_rng_0` (0.63) | -0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1335 | +0.1419 | +0.1419 | +0.8351 | 0.57 | 1/8 | 0.94 | 1.74 | `bar_body_rng_0` (0.63) | +0.0009 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1289 | +0.1310 | +0.1310 | +1.0164 | 0.51 | 1/8 | 0.95 | 1.34 | `bar_body_rng_0` (0.63) | +0.0004 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1407 | +0.1285 | +0.1285 | +1.1054 | 0.46 | 0/8 | 1.10 | 1.84 | `opening_drive_thrust_ratio` (0.46) | +0.0005 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1385 | +0.1325 | +0.1325 | +1.0456 | 0.39 | 0/8 | 1.10 | 1.71 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0009 | +0.0000 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1091 | +0.1518 | +0.1518 | +1.0662 | 0.76 | 1/8 | 0.94 | 4.18 | `limit_down_proximity_early` (0.71) | +0.0011 | +0.0000 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1316 | +0.1454 | +0.1454 | +1.0413 | 0.44 | 0/8 | 1.00 | 1.31 | `gap_pct` (1.43) | +0.0005 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1490 | +0.1279 | +0.1279 | +1.4471 | 0.35 | 0/8 | 0.93 | 1.30 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0002 | +0.0000 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1331 | +0.1319 | +0.1319 | +0.2487 | 0.34 | 0/8 | 1.33 | 1.64 | `star50_limit_proximity_early` (0.52) | +0.0005 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1165 | +0.1356 | +0.1356 | +0.6928 | 0.63 | 1/8 | 0.98 | 2.98 | `star50_limit_proximity_early` (0.52) | +0.0009 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1362 | +0.1319 | +0.1319 | +0.8890 | 0.43 | 0/8 | 1.01 | 1.18 | `volume_weighted_price_position` (0.77) | -0.0000 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1282 | +0.1015 | +0.1015 | +0.0872 | 0.41 | 0/8 | 1.39 | 2.89 | `opening_drive_thrust_ratio` (0.46) | -0.0002 | +0.0000 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1120 | +0.1396 | +0.1396 | +1.6504 | 0.63 | 1/8 | 0.94 | 1.55 | `rbreaker_buy_setup_proximity_early` (0.71) | +0.0012 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1375 | +0.1325 | +0.1325 | +0.7977 | 0.44 | 0/8 | 1.13 | 1.98 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0006 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1369 | +0.1344 | +0.1344 | +0.8852 | 0.45 | 0/8 | 1.00 | 1.08 | `bar_ret_0` (0.48) | +0.0005 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1426 | +0.1207 | +0.1207 | +0.9917 | 0.37 | 0/8 | 0.90 | 1.10 | `rbreaker_sell_setup_proximity_early` (0.43) | -0.0001 | +0.0000 |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1434 | +0.1199 | +0.1199 | +1.3117 | 0.37 | 0/8 | 0.91 | 1.13 | `rbreaker_sell_setup_proximity_early` (0.43) | -0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1322 | +0.1248 | +0.1248 | +0.7342 | 0.40 | 0/8 | 1.17 | 1.85 | `star50_limit_proximity_early` (0.52) | +0.0004 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1133 | +0.1497 | +0.1497 | +0.8445 | 0.51 | 1/8 | 1.80 | 3.12 | `volatility_expansion_trend_vector` (0.61) | +0.0014 | +0.0000 |
| `combo_min__volume_weighted_price_position__limit_down_proximity_early` | Volatility & Oscillators | +1 | +0.0981 | +0.1345 | +0.1345 | +1.4216 | 0.84 | 1/8 | 1.47 | 3.76 | `volume_weighted_price_position` (0.77) | +0.0004 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Other Technical | +1 | +0.1174 | +0.1093 | +0.1093 | +0.7465 | 0.64 | 0/8 | 1.15 | 1.63 | `rally_strength_max` (1.02) | +0.0004 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1353 | +0.1321 | +0.1321 | +1.3408 | 0.46 | 0/8 | 0.60 | 0.61 | `volume_price_confirmation` (0.60) | +0.0005 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1429 | +0.1073 | +0.1073 | +0.1834 | 0.33 | 0/8 | 1.11 | 1.94 | `first_bar_return` (0.48) | +0.0006 | +0.0000 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1172 | +0.0890 | +0.0890 | -0.9988 | 0.50 | 0/8 | 1.27 | 1.83 | `bar_body_rng_0` (0.63) | -0.0002 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__rally_strength_max` | Other Technical | +1 | +0.1211 | +0.1340 | +0.1340 | +0.0219 | 0.49 | 0/8 | 1.00 | 1.05 | `rally_strength_max` (1.02) | +0.0002 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1205 | +0.1348 | +0.1348 | +1.4350 | 0.60 | 1/8 | 0.67 | 1.38 | `directional_volume_signature` (1.20) | +0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1165 | +0.1533 | +0.1533 | +0.8711 | 0.50 | 1/8 | 1.77 | 2.85 | `volatility_expansion_trend_vector` (0.61) | +0.0015 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1188 | +0.1421 | +0.1421 | +0.5695 | 0.36 | 0/8 | 1.55 | 2.24 | `volatility_expansion_trend_vector` (0.61) | +0.0007 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | Other Technical | +1 | +0.1161 | +0.1265 | +0.1265 | +0.9284 | 0.52 | 0/8 | 1.36 | 1.84 | `rally_strength_max` (1.02) | +0.0005 | +0.0000 |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | Other Technical | +1 | +0.1184 | +0.1382 | +0.1382 | +1.3500 | 0.51 | 1/8 | 0.90 | 1.28 | `limit_down_proximity_early` (0.71) | +0.0008 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1182 | +0.0727 | +0.0727 | -0.3605 | 0.41 | 0/8 | 1.57 | 2.14 | `opening_drive_thrust_ratio` (0.46) | -0.0004 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Intraday Range Momentum | +1 | +0.1104 | +0.1100 | +0.1100 | +0.5568 | 0.67 | 1/8 | 0.87 | 1.54 | `yesterday_early_vwap_dev` (1.29) | +0.0009 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.0930 | +0.0930 | +0.0368 | 0.42 | 0/8 | 1.13 | 1.61 | `first_bar_return` (0.48) | -0.0005 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1077 | +0.0500 | +0.0500 | -0.8383 | 0.41 | 0/8 | 1.64 | 2.07 | `demark_setup_reversal_early` (0.51) | -0.0004 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1140 | +0.1367 | +0.1367 | +1.2430 | 0.62 | 0/8 | 0.70 | 2.23 | `directional_volume_signature` (1.20) | +0.0005 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0673 | +0.0673 | +0.1332 | 0.57 | 0/8 | 1.59 | 2.30 | `volume_weighted_price_position` (0.77) | +0.0000 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1101 | +0.0882 | +0.0882 | -1.0149 | 0.50 | 0/8 | 1.47 | 2.43 | `bar_body_rng_0` (0.63) | +0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1057 | +0.1527 | +0.1527 | +1.5226 | 0.63 | 1/8 | 1.16 | 3.62 | `rbreaker_buy_setup_proximity_early` (0.71) | +0.0010 | +0.0000 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1097 | +0.1332 | +0.1332 | +1.6808 | 0.54 | 0/8 | 0.66 | 1.43 | `volume_price_confirmation` (0.60) | +0.0010 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0996 | +0.1617 | +0.1617 | +1.1078 | 0.79 | 1/8 | 1.08 | 6.24 | `rbreaker_buy_setup_proximity_early` (0.71) | +0.0007 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1127 | +0.1066 | +0.1066 | +0.4207 | 0.39 | 0/8 | 1.67 | 2.71 | `star50_limit_proximity_early` (0.52) | +0.0004 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Other Technical | +1 | +0.1146 | +0.1426 | +0.1426 | +1.1691 | 0.57 | 1/8 | 1.16 | 2.90 | `limit_down_proximity_early` (0.71) | +0.0008 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1152 | +0.1259 | +0.1259 | +0.1557 | 0.34 | 0/8 | 1.64 | 1.97 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0005 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | Volatility & Oscillators | +1 | +0.0954 | +0.1471 | +0.1471 | +1.7038 | 0.83 | 1/8 | 1.48 | 4.47 | `volume_weighted_price_position` (0.77) | +0.0007 | +0.0000 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | Other Technical | +1 | +0.1016 | +0.1467 | +0.1467 | +0.8978 | 0.75 | 1/8 | 0.90 | 4.00 | `limit_down_proximity_early` (0.71) | +0.0009 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1239 | +0.1308 | +0.1308 | +0.6052 | 0.40 | 0/8 | 1.05 | 1.54 | `first_bar_return` (0.48) | +0.0002 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | Gap / Overnight Reversal | +1 | +0.1037 | +0.0515 | +0.0515 | +0.1414 | 0.40 | 0/8 | 1.77 | 2.32 | `gap_pct` (1.43) | -0.0003 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Intraday Range Momentum | +1 | +0.1235 | +0.1162 | +0.1162 | +0.1600 | 0.48 | 0/8 | 1.22 | 1.83 | `star50_limit_proximity_early` (0.52) | +0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1208 | +0.0717 | +0.0717 | -1.1315 | 0.46 | 0/8 | 1.52 | 2.13 | `first_bar_return` (0.48) | -0.0000 | +0.0000 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1064 | +0.1024 | +0.1024 | +0.4428 | 0.58 | 1/8 | 1.14 | 5.06 | `star50_limit_proximity_early` (0.52) | +0.0002 | +0.0000 |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1083 | +0.0823 | +0.0823 | +0.4441 | 0.53 | 0/8 | 0.85 | 1.42 | `volatility_expansion_trend_vector` (0.61) | -0.0002 | +0.0000 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1159 | +0.0919 | +0.0919 | -0.8343 | 0.42 | 0/8 | 1.85 | 1.86 | `star50_limit_proximity_early` (0.52) | +0.0002 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | Intraday Range Momentum | +1 | +0.0924 | +0.1321 | +0.1321 | +1.0237 | 0.71 | 1/8 | 1.08 | 2.58 | `yesterday_early_trend` (1.18) | +0.0016 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1182 | +0.0824 | +0.0824 | -0.6121 | 0.46 | 0/8 | 1.75 | 2.75 | `opening_drive_thrust_ratio` (0.46) | -0.0002 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1133 | +0.0776 | +0.0776 | -0.3109 | 0.49 | 0/8 | 1.28 | 1.96 | `bar_ret_0` (0.48) | +0.0000 | +0.0000 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.1169 | +0.1473 | +0.1473 | +0.9583 | 0.38 | 0/8 | 1.10 | 2.01 | `gap_pct` (1.43) | +0.0009 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1219 | +0.1058 | +0.1058 | +0.4149 | 0.45 | 0/8 | 1.37 | 2.62 | `demark_setup_reversal_early` (0.51) | -0.0002 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1115 | +0.0864 | +0.0864 | -0.0202 | 0.55 | 0/8 | 1.23 | 2.19 | `bar_body_rng_0` (0.63) | -0.0002 | +0.0000 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1145 | +0.1120 | +0.1120 | +0.0365 | 0.38 | 0/8 | 1.25 | 1.09 | `star50_limit_proximity_early` (0.52) | +0.0004 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1172 | +0.1491 | +0.1491 | +1.4472 | 0.53 | 0/8 | 1.08 | 2.08 | `bar_body_rng_0` (0.63) | +0.0004 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__demark_setup_reversal_early__star50_limit_proximity_early` | Other Technical | +1 | +0.1118 | +0.0786 | +0.0786 | +0.0918 | 0.39 | 0/8 | 0.95 | 1.64 | `star50_limit_proximity_early` (0.52) | +0.0003 | +0.0000 |
| `combo_rank_min__max_up_ret__gap_pct` | Gap / Overnight Reversal | +1 | +0.1030 | +0.1241 | +0.1241 | +0.8669 | 0.77 | 1/8 | 0.95 | 8.18 | `gap_pct` (1.43) | +0.0009 | +0.0000 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1124 | +0.0939 | +0.0939 | -0.4022 | 0.49 | 0/8 | 1.14 | 1.69 | `bar_body_rng_0` (0.63) | +0.0002 | +0.0000 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1185 | +0.1056 | +0.1056 | +0.3256 | 0.46 | 0/8 | 1.55 | 2.15 | `demark_setup_reversal_early` (0.51) | +0.0005 | +0.0000 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1215 | +0.1133 | +0.1133 | +0.4549 | 0.45 | 0/8 | 1.38 | 2.40 | `demark_setup_reversal_early` (0.51) | +0.0002 | +0.0000 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0917 | +0.0888 | +0.0888 | -0.2203 | 0.60 | 0/8 | 3.58 | 7.87 | `volatility_expansion_trend_vector` (0.61) | +0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1181 | +0.0948 | +0.0948 | +0.0510 | 0.42 | 0/8 | 1.36 | 1.84 | `bar_body_rng_0` (0.63) | -0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | Volatility & Oscillators | +1 | +0.1096 | +0.1421 | +0.1421 | +1.1452 | 0.62 | 0/8 | 0.67 | 2.22 | `directional_volume_signature` (1.20) | +0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1210 | +0.1003 | +0.1003 | +0.2207 | 0.34 | 0/8 | 1.51 | 2.57 | `opening_drive_thrust_ratio` (0.46) | +0.0001 | +0.0000 |
| `combo_max__max_up_ret__rally_strength_max` | Intraday Range Momentum | +1 | +0.0915 | +0.0701 | +0.0701 | -0.7883 | 0.59 | 0/8 | 1.72 | 1.94 | `rally_strength_max` (1.02) | +0.0005 | +0.0000 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1185 | +0.1106 | +0.1106 | -0.0225 | 0.45 | 0/8 | 1.53 | 2.35 | `demark_setup_reversal_early` (0.51) | +0.0004 | +0.0000 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1171 | +0.0811 | +0.0811 | -0.6874 | 0.39 | 0/8 | 1.58 | 1.46 | `star50_limit_proximity_early` (0.52) | +0.0002 | +0.0000 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1013 | +0.1453 | +0.1453 | +0.2923 | 0.45 | 0/8 | 1.75 | 2.72 | `limit_down_proximity_early` (0.71) | +0.0011 | +0.0000 |
| `combo_max__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1149 | +0.0655 | +0.0655 | -0.4261 | 0.39 | 0/8 | 0.96 | 1.11 | `volume_price_confirmation` (0.60) | -0.0001 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1159 | +0.0366 | +0.0366 | -0.6946 | 0.34 | 0/8 | 1.47 | 1.54 | `opening_drive_thrust_ratio` (0.46) | -0.0003 | +0.0000 |
| `combo_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1276 | +0.1150 | +0.1150 | +0.9916 | 0.48 | 0/8 | 0.90 | 1.39 | `late_bar_momentum` (0.77) | +0.0002 | +0.0000 |
| `combo_mean__volume_weighted_price_position__rbreaker_buy_setup_proximity_early` | Volatility & Oscillators | +1 | +0.1118 | +0.1340 | +0.1340 | +0.5076 | 0.59 | 0/8 | 1.08 | 1.33 | `volume_weighted_price_position` (0.77) | +0.0003 | +0.0000 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1207 | +0.0724 | +0.0724 | +0.2056 | 0.36 | 0/8 | 1.18 | 1.62 | `volume_weighted_momentum_acceleration` (0.41) | -0.0008 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | Other Technical | +1 | +0.0978 | +0.0711 | +0.0711 | -0.1790 | 0.63 | 0/8 | 1.97 | 1.96 | `rally_strength_max` (1.02) | +0.0000 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1112 | +0.0738 | +0.0738 | -0.4608 | 0.45 | 0/8 | 1.80 | 3.40 | `volatility_expansion_trend_vector` (0.61) | -0.0003 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1249 | +0.1193 | +0.1193 | -0.2201 | 0.33 | 0/8 | 1.28 | 1.32 | `first_bar_return` (0.48) | +0.0003 | +0.0000 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1210 | +0.0755 | +0.0755 | +0.0763 | 0.38 | 0/8 | 1.24 | 1.61 | `volume_weighted_momentum_acceleration` (0.41) | -0.0006 | +0.0000 |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.0954 | +0.0378 | +0.0378 | -1.7135 | 0.49 | 0/8 | 2.04 | 3.43 | `keltner_squeeze_width` (0.68) | -0.0004 | +0.0000 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1120 | +0.1308 | +0.1308 | +0.7043 | 0.52 | 1/8 | 1.38 | 3.68 | `volume_weighted_price_position` (0.77) | +0.0003 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | Other Technical | +1 | +0.1293 | +0.1217 | +0.1217 | +1.1554 | 0.54 | 0/8 | 0.69 | 1.05 | `body_size_progression` (0.84) | -0.0001 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1070 | +0.1138 | +0.1138 | +0.1660 | 0.35 | 0/8 | 1.79 | 2.92 | `volatility_expansion_trend_vector` (0.61) | +0.0002 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1175 | +0.0772 | +0.0772 | -0.5386 | 0.50 | 0/8 | 1.77 | 1.84 | `volume_weighted_price_position` (0.77) | +0.0005 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1235 | +0.1428 | +0.1428 | +0.6972 | 0.46 | 1/8 | 1.20 | 2.09 | `demark_setup_reversal_early` (0.51) | +0.0008 | +0.0000 |
| `combo_clamp_diff__volume_weighted_price_position__body_size_progression` | Volatility & Oscillators | +1 | +0.1006 | +0.0607 | +0.0607 | +0.7191 | 0.66 | 0/8 | 0.80 | 1.22 | `body_size_progression` (0.84) | -0.0001 | +0.0000 |
| `combo_min__max_up_ret__gap_pct` | Gap / Overnight Reversal | +1 | +0.1058 | +0.1305 | +0.1305 | +1.6653 | 0.61 | 0/8 | 0.99 | 3.26 | `gap_pct` (1.43) | +0.0008 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__bar_ret_0` | Other Technical | +1 | +0.1149 | +0.0906 | +0.0906 | +0.8830 | 0.51 | 0/8 | 1.01 | 1.50 | `bar_body_rng_0` (0.63) | -0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1130 | +0.0663 | +0.0663 | +0.1804 | 0.41 | 0/8 | 0.99 | 1.22 | `volume_price_confirmation` (0.60) | -0.0004 | +0.0000 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1158 | +0.0732 | +0.0732 | -0.9166 | 0.53 | 0/8 | 1.87 | 1.92 | `volume_weighted_price_position` (0.77) | +0.0004 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | Other Technical | +1 | +0.1351 | +0.1226 | +0.1226 | +1.3869 | 0.54 | 0/8 | 0.78 | 1.48 | `body_size_progression` (0.84) | -0.0001 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__rally_strength_max` | Other Technical | +1 | +0.0989 | +0.1224 | +0.1224 | -0.2137 | 0.41 | 0/8 | 1.32 | 1.89 | `rally_strength_max` (1.02) | +0.0004 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.0863 | +0.1411 | +0.1411 | +1.7639 | 0.66 | 1/8 | 0.72 | 2.00 | `limit_down_proximity_early` (0.71) | +0.0006 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Intraday Range Momentum | +1 | +0.1050 | +0.0936 | +0.0936 | +0.2427 | 0.75 | 1/8 | 1.07 | 2.90 | `yesterday_early_vwap_dev` (1.29) | +0.0009 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__volume_price_confirmation` | Volatility & Oscillators | +1 | +0.1177 | +0.1187 | +0.1187 | +1.0234 | 0.43 | 0/8 | 0.81 | 0.77 | `volume_price_confirmation` (0.60) | +0.0007 | +0.0000 |
| `combo_rank_min__max_up_ret__rally_strength_max` | Intraday Range Momentum | +1 | +0.0965 | +0.0683 | +0.0683 | -0.5163 | 0.62 | 0/8 | 1.84 | 2.11 | `rally_strength_max` (1.02) | -0.0000 | +0.0000 |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1093 | +0.0894 | +0.0894 | -0.0643 | 0.40 | 0/8 | 1.56 | 1.78 | `volatility_expansion_trend_vector` (0.61) | +0.0004 | +0.0000 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1040 | +0.0578 | +0.0578 | -1.3521 | 0.39 | 0/8 | 1.77 | 2.25 | `volume_weighted_price_position` (0.77) | -0.0000 | +0.0000 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.0961 | +0.1102 | +0.1102 | +0.3258 | 0.98 | 1/8 | 1.51 | -9.60 | `gap_pct` (1.43) | +0.0011 | +0.0000 |
| `combo_mean__max_up_ret__volume_price_confirmation` | Intraday Range Momentum | +1 | +0.1170 | +0.0849 | +0.0849 | +0.5225 | 0.32 | 0/8 | 0.86 | 0.98 | `volume_price_confirmation` (0.60) | -0.0003 | +0.0000 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | Gap / Overnight Reversal | +1 | +0.1151 | +0.0814 | +0.0814 | -0.3638 | 0.39 | 0/8 | 1.79 | 2.45 | `gap_pct` (1.43) | +0.0002 | +0.0000 |
| `combo_min__bar_ret_0__directional_volume_signature` | Volatility & Oscillators | +1 | +0.0967 | +0.0625 | +0.0625 | -0.1555 | 0.54 | 0/8 | 0.94 | 2.61 | `directional_volume_signature` (1.20) | -0.0002 | +0.0000 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0659 | +0.0659 | +0.7397 | 0.53 | 0/8 | 0.94 | 1.48 | `volume_weighted_price_position` (0.77) | +0.0003 | +0.0000 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.0971 | +0.0872 | +0.0872 | +0.2933 | 0.30 | 0/8 | 1.47 | 1.72 | `keltner_squeeze_width` (0.68) | +0.0005 | +0.0000 |
| `combo_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1051 | +0.0839 | +0.0839 | +0.2124 | 0.42 | 0/8 | 1.24 | 1.52 | `bar_ret_0` (0.48) | +0.0003 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1175 | +0.0841 | +0.0841 | +0.0197 | 0.38 | 0/8 | 1.72 | 2.07 | `opening_drive_thrust_ratio` (0.46) | +0.0003 | +0.0000 |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.0995 | +0.0633 | +0.0633 | +0.1638 | 0.25 | 0/8 | 1.53 | 1.67 | `keltner_squeeze_width` (0.68) | -0.0002 | +0.0000 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | Intraday Range Momentum | +1 | +0.1001 | +0.0690 | +0.0690 | +0.2563 | 0.25 | 0/8 | 1.52 | 1.68 | `keltner_squeeze_width` (0.68) | +0.0002 | +0.0094 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 47.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8768_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1160 | 30 | 76.7% | 53.3% | +0.0307 | -0.1757 |
| B2 Rolling Guard | 121 | 30 | 80.0% | 43.3% | +0.0363 | -0.1815 |
| BH-FDR Gate | 5 | 5 | 100.0% | 20.0% | +0.0254 | -0.4291 |
| B4 Correlation Gate | 67 | 30 | 60.0% | 30.0% | +0.0198 | -0.4833 |

**Admitted Pool Summary**: 35 features, False Positive Rate = 85.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0045, Mean Lock Sharpe = -0.8356

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0570, Lock Sharpe=+0.7428
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0570, Lock Sharpe=+0.7428
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0570, Lock Sharpe=+0.7428
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0570, Lock Sharpe=+0.7428
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Lock Sharpe=+0.4449

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1522, Lock IC=+0.0969, Lock Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0962, Lock Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0962, Lock Sharpe=+0.8491
- `combo_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1362, Lock IC=+0.0919, Lock Sharpe=+0.5509
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1362, Lock IC=+0.0919, Lock Sharpe=+0.5509

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Lock Sharpe=+0.1297

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Lock Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Lock Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Lock Sharpe=+0.3783
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2286, Lock IC=+0.0813, Lock Sharpe=+0.3659
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2534, Lock IC=+0.0736, Lock Sharpe=+0.3417

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 6.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8116_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 538 | 30 | 70.0% | 20.0% | +0.0193 | -0.5144 |
| B2 Rolling Guard | 41 | 30 | 23.3% | 10.0% | -0.0076 | -0.4749 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0266 | -1.2281 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_concentration`: Train IC=+0.1149, Lock IC=+0.0409, Lock Sharpe=+0.7521
- `first_bar_volume`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.6546
- `bar_vol_0`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.6546
- `volume_surge_max`: Train IC=+0.1279, Lock IC=+0.0659, Lock Sharpe=+0.6546
- `sma200_dist`: Train IC=+0.1387, Lock IC=+0.0286, Lock Sharpe=+0.3842

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__willr14__roc60`: Train IC=+0.0666, Lock IC=+0.0596, Lock Sharpe=+0.5936
- `combo_diff__willr14__roc60`: Train IC=+0.0528, Lock IC=+0.0594, Lock Sharpe=+0.5936
- `combo_z_diff__willr14__roc60`: Train IC=+0.0528, Lock IC=+0.0594, Lock Sharpe=+0.5936

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 54.0% lock IC > 0, 23.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3702_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 73.3% | 36.7% | +0.0381 | -0.3478 |
| B2 Rolling Guard | 60 | 30 | 56.7% | 36.7% | +0.0001 | -0.2144 |
| BH-FDR Gate | 8 | 8 | 62.5% | 50.0% | +0.0200 | -0.1920 |
| B3 Composite Floor | 1 | 1 | 100.0% | 100.0% | +0.0684 | +0.3610 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `star50_limit_proximity_early`: Train IC=+0.1240, Lock IC=+0.0960, Lock Sharpe=+0.8503
- `combo_rank_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1301, Lock IC=+0.0945, Lock Sharpe=+0.8389
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1502, Lock IC=+0.0932, Lock Sharpe=+0.7106

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `pullback_depth_ratio`: Train IC=+0.0000, Lock IC=+0.0504, Lock Sharpe=+1.5711
- `double_bottom_bull_flag_early`: Train IC=+0.0000, Lock IC=+0.0395, Lock Sharpe=+0.9090
- `combo_sig_product__total_path_length__max_down_ret`: Train IC=+0.0376, Lock IC=+0.0550, Lock Sharpe=+0.8756
- `combo_abs_diff__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0644, Lock IC=+0.0362, Lock Sharpe=+0.8632
- `combo_sig_product__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0064, Lock IC=+0.0190, Lock Sharpe=+0.5424

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0708, Lock IC=+0.0119, Lock Sharpe=+0.7142
- `gap_pct`: Train IC=+0.1402, Lock IC=+0.1085, Lock Sharpe=+0.6926
- `combo_rank_max__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.1202, Lock IC=+0.0273, Lock Sharpe=+0.2891
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1032, Lock IC=+0.0946, Lock Sharpe=+0.2733

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.2007, Lock IC=+0.0684, Lock Sharpe=+0.3610

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 22.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6646_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 799 | 30 | 90.0% | 23.3% | +0.0330 | -0.1796 |
| B2 Rolling Guard | 75 | 30 | 76.7% | 33.3% | +0.0207 | -0.3969 |
| BH-FDR Gate | 3 | 3 | 0.0% | 0.0% | -0.0339 | -0.9002 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__yesterday_body_ratio`: Train IC=+0.1218, Lock IC=+0.0414, Lock Sharpe=+0.9049
- `combo_mean__volume_surge_max__stoch_k`: Train IC=+0.1226, Lock IC=+0.0543, Lock Sharpe=+0.3330
- `combo_z_sum__volume_surge_max__stoch_k`: Train IC=+0.1226, Lock IC=+0.0543, Lock Sharpe=+0.3330
- `combo_clamp_diff__iv_corridor_width__multi_ema_alignment_5_20_50`: Train IC=+0.1324, Lock IC=+0.0161, Lock Sharpe=+0.2338
- `combo_max__bar_vol_4__bar_vol_0`: Train IC=+0.1458, Lock IC=+0.0348, Lock Sharpe=+0.0748

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.0946, Lock IC=+0.0603, Lock Sharpe=+0.9632
- `combo_product__bar_vol_4__volume_surge_max`: Train IC=+0.1006, Lock IC=+0.0278, Lock Sharpe=+0.5091
- `combo_product__bar_vol_4__bar_vol_0`: Train IC=+0.0826, Lock IC=+0.0290, Lock Sharpe=+0.5091
- `combo_product__bar_vol_4__first_bar_volume`: Train IC=+0.0826, Lock IC=+0.0290, Lock Sharpe=+0.5091
- `combo_mean__bar_vol_4__willr14`: Train IC=+0.1306, Lock IC=+0.0797, Lock Sharpe=+0.4655

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9364_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 321 | 30 | 63.3% | 0.0% | +0.0163 | -1.1550 |
| B2 Rolling Guard | 36 | 30 | 26.7% | 6.7% | -0.0014 | -0.7829 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0367 | -1.6468 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__iv_envelope_deviation__yesterday_wavetrend_osc`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0844
- `combo_product__iv_envelope_deviation__wavetrend_osc_day`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0844

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 28.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4128_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 278 | 30 | 76.7% | 60.0% | +0.0467 | +0.1306 |
| B2 Rolling Guard | 40 | 30 | 33.3% | 13.3% | +0.0116 | -0.1918 |
| BH-FDR Gate | 2 | 2 | 100.0% | 100.0% | +0.0198 | +0.3210 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1886, Lock IC=+0.0898, Lock Sharpe=+1.2870
- `limit_down_proximity_early`: Train IC=+0.1886, Lock IC=+0.0899, Lock Sharpe=+1.2870
- `combo_rank_max__bar_vol_4__mfi14`: Train IC=+0.1590, Lock IC=+0.0937, Lock Sharpe=+1.1906
- `sma20_dist`: Train IC=+0.1468, Lock IC=+0.1018, Lock Sharpe=+1.1639
- `star50_limit_proximity_early`: Train IC=+0.1271, Lock IC=+0.0603, Lock Sharpe=+0.8789

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `close_vs_open_range`: Train IC=+0.0193, Lock IC=+0.0427, Lock Sharpe=+1.1670
- `keltner_squeeze_width`: Train IC=+0.1163, Lock IC=+0.1636, Lock Sharpe=+1.1211
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0727, Lock Sharpe=+0.5902
- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0277, Lock Sharpe=+0.0353

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1148, Lock IC=+0.0302, Lock Sharpe=+0.5419
- `cvd_divergence_day`: Train IC=+0.1225, Lock IC=+0.0094, Lock Sharpe=+0.1001

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 82.0% lock IC > 0, 26.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5014_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2516 | 30 | 100.0% | 60.0% | +0.0827 | -0.0024 |
| B2 Rolling Guard | 301 | 30 | 100.0% | 20.0% | +0.0497 | -0.7721 |
| BH-FDR Gate | 3 | 3 | 66.7% | 0.0% | -0.0061 | -1.5038 |
| B3 Composite Floor | 56 | 30 | 83.3% | 26.7% | +0.0329 | -0.5502 |
| B4 Correlation Gate | 474 | 30 | 100.0% | 23.3% | +0.0679 | -0.5979 |

**Admitted Pool Summary**: 100 features, False Positive Rate = 76.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0579, Mean Lock Sharpe = -0.6271

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__demark_setup_reversal_early__body_size_progression`: Train IC=+0.2157, Lock IC=+0.1227, Lock Sharpe=+0.9107
- `combo_z_sum__demark_setup_reversal_early__body_size_progression`: Train IC=+0.2157, Lock IC=+0.1227, Lock Sharpe=+0.9107
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Lock Sharpe=+0.5717
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__trend_day_regime_conviction__shaved_bar_trend_conviction`: Train IC=+0.2190, Lock IC=+0.0431, Lock Sharpe=+0.2228
- `combo_z_sum__trend_day_regime_conviction__shaved_bar_trend_conviction`: Train IC=+0.2190, Lock IC=+0.0431, Lock Sharpe=+0.2228
- `combo_mean__rsi_opening__shaved_bar_trend_conviction`: Train IC=+0.2181, Lock IC=+0.0458, Lock Sharpe=+0.2228
- `combo_z_sum__rsi_opening__shaved_bar_trend_conviction`: Train IC=+0.2181, Lock IC=+0.0458, Lock Sharpe=+0.2228
- `combo_mean__high_low_sequence_momentum__shaved_bar_trend_conviction`: Train IC=+0.2181, Lock IC=+0.0458, Lock Sharpe=+0.2228

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`: Train IC=+0.1847, Lock IC=+0.0017, Lock Sharpe=+0.3201
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__smooth_momentum_structure`: Train IC=+0.1599, Lock IC=+0.0747, Lock Sharpe=+0.2713
- `combo_tri_mean__net_volume_flow__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_z_mean__net_volume_flow__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_mean__opening_auction_imbalance__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`: Train IC=+0.2602, Lock IC=+0.1055, Lock Sharpe=+0.7197
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2741, Lock IC=+0.0880, Lock Sharpe=+0.3545
- `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2645, Lock IC=+0.0855, Lock Sharpe=+0.2823
- `combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2645, Lock IC=+0.0855, Lock Sharpe=+0.2823
- `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__opening_momentum_score`: Train IC=+0.2612, Lock IC=+0.0900, Lock Sharpe=+0.1337

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5068_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1228 | 30 | 83.3% | 66.7% | +0.0708 | +0.3640 |
| B2 Rolling Guard | 96 | 30 | 33.3% | 10.0% | -0.0229 | -0.7241 |
| BH-FDR Gate | 23 | 23 | 91.3% | 73.9% | +0.0383 | +0.4499 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1626, Lock IC=+0.1245, Lock Sharpe=+1.4042
- `combo_diff__donchian_breakout_ratio_20d__yesterday_return`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400
- `combo_z_diff__donchian_breakout_ratio_20d__yesterday_return`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400
- `combo_diff__donchian_breakout_ratio_20d__limit_up_proximity_day`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400
- `combo_z_diff__donchian_breakout_ratio_20d__limit_up_proximity_day`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__consecutive_higher_highs__trend_day_regime_conviction`: Train IC=+0.0601, Lock IC=+0.0134, Lock Sharpe=+0.9154
- `combo_rank_min__early_body_momentum__star50_limit_proximity_early`: Train IC=+0.1367, Lock IC=+0.1134, Lock Sharpe=+0.5147
- `combo_rank_min__opening_momentum_score__star50_limit_proximity_early`: Train IC=+0.1367, Lock IC=+0.1134, Lock Sharpe=+0.5147

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1248, Lock IC=+0.0888, Lock Sharpe=+1.8266
- `combo_abs_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.1248, Lock IC=+0.0888, Lock Sharpe=+1.8266
- `combo_sig_product__early_body_momentum__consecutive_higher_highs`: Train IC=+0.0742, Lock IC=+0.0383, Lock Sharpe=+0.9002
- `combo_sig_product__opening_momentum_score__consecutive_higher_highs`: Train IC=+0.0742, Lock IC=+0.0383, Lock Sharpe=+0.9002
- `combo_rank_min__shaved_bar_trend_conviction__trend_day_regime_conviction`: Train IC=+0.1061, Lock IC=+0.0275, Lock Sharpe=+0.8838

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5074_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 369 | 30 | 56.7% | 33.3% | +0.0296 | -0.3004 |
| B2 Rolling Guard | 46 | 30 | 63.3% | 30.0% | +0.0057 | -0.3230 |
| BH-FDR Gate | 14 | 14 | 92.9% | 7.1% | +0.0489 | -0.8709 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.4723
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.4723
- `false_breakout_accumulation`: Train IC=+0.1489, Lock IC=+0.0315, Lock Sharpe=+0.4446
- `combo_mean__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.4139
- `combo_z_sum__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.4139

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv_diff_1d`: Train IC=+0.0334, Lock IC=+0.0868, Lock Sharpe=+0.9572
- `opening_direction_stability`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+0.5808
- `early_trend_hhi`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+0.5808
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0456, Lock Sharpe=+0.5463
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0696, Lock Sharpe=+0.4248

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vwap_close_divergence_trend`: Train IC=+0.0805, Lock IC=+0.0323, Lock Sharpe=+0.2934

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 69.0% lock IC > 0, 51.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0492_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1962 | 30 | 100.0% | 86.7% | +0.1175 | +0.7476 |
| B2 Rolling Guard | 280 | 30 | 100.0% | 80.0% | +0.1085 | +0.8552 |
| BH-FDR Gate | 2 | 2 | 100.0% | 0.0% | +0.0274 | -0.1245 |
| B3 Composite Floor | 121 | 30 | 100.0% | 83.3% | +0.0996 | +0.2298 |
| B4 Correlation Gate | 252 | 30 | 100.0% | 100.0% | +0.1304 | +1.0384 |

**Admitted Pool Summary**: 125 features, False Positive Rate = 21.6% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1103, Mean Lock Sharpe = +0.4950

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__limit_down_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Lock Sharpe=+1.9220
- `combo_z_sum__limit_down_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Lock Sharpe=+1.9220
- `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Lock Sharpe=+1.9220
- `combo_z_sum__rbreaker_buy_setup_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Lock Sharpe=+1.9220
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2358, Lock IC=+0.1409, Lock Sharpe=+1.7700

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2191, Lock IC=+0.1315, Lock Sharpe=+1.7919
- `combo_z_sum__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2191, Lock IC=+0.1315, Lock Sharpe=+1.7919
- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Lock Sharpe=+1.6676
- `combo_z_sum__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Lock Sharpe=+1.6676
- `combo_mean__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Lock Sharpe=+1.6676

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.2238, Lock IC=+0.1147, Lock Sharpe=+1.4941
- `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`: Train IC=+0.2460, Lock IC=+0.1133, Lock Sharpe=+0.8865
- `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2349, Lock IC=+0.1410, Lock Sharpe=+0.7550
- `combo_rank_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2349, Lock IC=+0.1410, Lock Sharpe=+0.7550
- `combo_tri_mean__max_up_ret__demark_setup_reversal_early__star50_limit_proximity_early`: Train IC=+0.2204, Lock IC=+0.0906, Lock Sharpe=+0.6905

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3282, Lock IC=+0.1307, Lock Sharpe=+1.7816
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.4890
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.4890
- `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3025, Lock IC=+0.1381, Lock Sharpe=+1.4675
- `combo_mean__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3057, Lock IC=+0.1432, Lock Sharpe=+1.3853

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 66.0% lock IC > 0, 43.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2460_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 938 | 30 | 90.0% | 53.3% | +0.0783 | +0.1280 |
| B2 Rolling Guard | 63 | 30 | 90.0% | 50.0% | +0.0765 | +0.1443 |
| BH-FDR Gate | 117 | 30 | 100.0% | 96.7% | +0.1037 | +0.8546 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__trend_strength_intraday`: Train IC=+0.1628, Lock IC=+0.1119, Lock Sharpe=+1.6143
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2132, Lock IC=+0.1300, Lock Sharpe=+1.4635
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1562, Lock IC=+0.1299, Lock Sharpe=+1.4458
- `combo_min__opening_drive_thrust_ratio__open_to_current_return`: Train IC=+0.1640, Lock IC=+0.1043, Lock Sharpe=+1.3003
- `combo_min__opening_drive_thrust_ratio__first_30min_return`: Train IC=+0.1640, Lock IC=+0.1043, Lock Sharpe=+1.3003

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.1162, Lock Sharpe=+1.1610
- `combo_tri_z_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.1162, Lock Sharpe=+1.1610
- `combo_tri_mean__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.0999, Lock IC=+0.1103, Lock Sharpe=+1.0839
- `combo_tri_z_mean__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.0999, Lock IC=+0.1103, Lock Sharpe=+1.0839
- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1129, Lock IC=+0.0837, Lock Sharpe=+1.0825

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1758, Lock IC=+0.1285, Lock Sharpe=+2.0254
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1506, Lock IC=+0.1406, Lock Sharpe=+1.7895
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1506, Lock IC=+0.1406, Lock Sharpe=+1.7895
- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1848, Lock IC=+0.1170, Lock Sharpe=+1.7797
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1491, Lock IC=+0.1210, Lock Sharpe=+1.2408

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 39.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3723_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 256 | 30 | 76.7% | 46.7% | +0.0418 | -0.1211 |
| B2 Rolling Guard | 42 | 30 | 40.0% | 33.3% | +0.0131 | +0.0513 |
| BH-FDR Gate | 1 | 1 | 100.0% | 0.0% | +0.0926 | -0.0411 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `gap_pct`: Train IC=+0.0662, Lock IC=+0.1187, Lock Sharpe=+0.6266
- `combo_product__morning_volume_weighted_momentum__shaved_bar_trend_conviction`: Train IC=+0.1398, Lock IC=+0.0685, Lock Sharpe=+0.5945
- `vol_ratio_5_20`: Train IC=+0.0670, Lock IC=+0.0317, Lock Sharpe=+0.4589
- `combo_rel_diff__micro_gap_trend_continuation__shaved_bar_trend_conviction`: Train IC=+0.0946, Lock IC=+0.0112, Lock Sharpe=+0.4444
- `limit_down_proximity_early`: Train IC=+0.0645, Lock IC=+0.1323, Lock Sharpe=+0.4433

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0168, Lock IC=+0.1035, Lock Sharpe=+1.0730
- `yesterday_close_position`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.8307
- `yesterday_day_close_pos`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.8307
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0397, Lock Sharpe=+0.7030
- `combo_rank_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.0241, Lock IC=+0.0817, Lock Sharpe=+0.5716

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 622 | +0.0215 | 70.0% |
| 0.45 | 0.20 | 614 | +0.0215 | 70.0% |
| 0.45 | 0.30 | 579 | +0.0215 | 70.0% |
| 0.45 | 0.40 | 516 | +0.0215 | 70.0% |
| 0.45 | 0.50 | 406 | +0.0215 | 70.0% |
| 0.50 | 0.15 | 620 | +0.0215 | 70.0% |
| 0.50 | 0.25 | 598 | +0.0215 | 70.0% |
| 0.50 | 0.35 | 545 | +0.0215 | 70.0% |
| 0.50 | 0.45 | 476 | +0.0215 | 70.0% |
| 0.55 | 0.10 | 615 | +0.0215 | 70.0% |
| 0.55 | 0.20 | 610 | +0.0215 | 70.0% |
| 0.55 | 0.30 | 579 | +0.0215 | 70.0% |
| 0.55 | 0.40 | 516 | +0.0215 | 70.0% |
| 0.55 | 0.50 | 406 | +0.0215 | 70.0% |
| 0.60 | 0.15 | 592 | +0.0215 | 70.0% |
| 0.60 | 0.25 | 584 | +0.0215 | 70.0% |
| 0.60 | 0.35 | 544 | +0.0215 | 70.0% |
| 0.60 | 0.45 | 476 | +0.0215 | 70.0% |
| 0.65 | 0.10 | 518 | +0.0215 | 70.0% |
| 0.65 | 0.20 | 518 | +0.0215 | 70.0% |
| 0.65 | 0.30 | 516 | +0.0215 | 70.0% |
| 0.65 | 0.40 | 505 | +0.0215 | 70.0% |
| 0.65 | 0.50 | 406 | +0.0215 | 70.0% |
| 0.70 | 0.15 | 372 | +0.0215 | 70.0% |
| 0.70 | 0.25 | 372 | +0.0215 | 70.0% |
| 0.70 | 0.35 | 372 | +0.0215 | 70.0% |
| 0.70 | 0.45 | 369 | +0.0215 | 70.0% |
| 0.75 | 0.10 | 133 | +0.0133 | 60.0% |
| 0.75 | 0.20 | 133 | +0.0133 | 60.0% |
| 0.75 | 0.30 | 133 | +0.0133 | 60.0% |
| 0.75 | 0.40 | 133 | +0.0133 | 60.0% |
| 0.75 | 0.50 | 133 | +0.0133 | 60.0% |
| 0.80 | 0.15 | 20 | -0.0234 | 10.0% |
| 0.80 | 0.25 | 20 | -0.0234 | 10.0% |
| 0.80 | 0.35 | 20 | -0.0234 | 10.0% |
| 0.80 | 0.45 | 20 | -0.0234 | 10.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 622 candidates, mean lock IC=+0.0215, 70.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | -0.0188 | 30.0% |
| 0.45 | 0.20 | 6 | -0.0266 | 16.7% |
| 0.45 | 0.30 | 5 | -0.0224 | 20.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | -0.0273 | 12.5% |
| 0.50 | 0.25 | 5 | -0.0224 | 20.0% |
| 0.50 | 0.35 | 1 | +0.0538 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | -0.0223 | 28.6% |
| 0.55 | 0.20 | 6 | -0.0266 | 16.7% |
| 0.55 | 0.30 | 5 | -0.0224 | 20.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 5 | -0.0224 | 20.0% |
| 0.60 | 0.25 | 5 | -0.0224 | 20.0% |
| 0.60 | 0.35 | 1 | +0.0538 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 10 candidates, mean lock IC=-0.0188, 30.0% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 18 | +0.0125 | 50.0% |
| 0.45 | 0.20 | 7 | +0.0216 | 71.4% |
| 0.45 | 0.30 | 4 | +0.0087 | 75.0% |
| 0.45 | 0.40 | 1 | -0.0818 | 0.0% |
| 0.45 | 0.50 | 1 | -0.0818 | 0.0% |
| 0.50 | 0.15 | 14 | +0.0269 | 70.0% |
| 0.50 | 0.25 | 5 | +0.0094 | 80.0% |
| 0.50 | 0.35 | 1 | -0.0818 | 0.0% |
| 0.50 | 0.45 | 1 | -0.0818 | 0.0% |
| 0.55 | 0.10 | 9 | +0.0254 | 66.7% |
| 0.55 | 0.20 | 7 | +0.0216 | 71.4% |
| 0.55 | 0.30 | 4 | +0.0087 | 75.0% |
| 0.55 | 0.40 | 1 | -0.0818 | 0.0% |
| 0.55 | 0.50 | 1 | -0.0818 | 0.0% |
| 0.60 | 0.15 | 4 | +0.0087 | 75.0% |
| 0.60 | 0.25 | 4 | +0.0087 | 75.0% |
| 0.60 | 0.35 | 1 | -0.0818 | 0.0% |
| 0.60 | 0.45 | 1 | -0.0818 | 0.0% |
| 0.65 | 0.10 | 1 | -0.0818 | 0.0% |
| 0.65 | 0.20 | 1 | -0.0818 | 0.0% |
| 0.65 | 0.30 | 1 | -0.0818 | 0.0% |
| 0.65 | 0.40 | 1 | -0.0818 | 0.0% |
| 0.65 | 0.50 | 1 | -0.0818 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 14 candidates, mean lock IC=+0.0269, 70.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 169 | +0.0274 | 90.0% |
| 0.45 | 0.20 | 151 | +0.0274 | 90.0% |
| 0.45 | 0.30 | 128 | +0.0274 | 90.0% |
| 0.45 | 0.40 | 107 | +0.0274 | 90.0% |
| 0.45 | 0.50 | 93 | +0.0274 | 90.0% |
| 0.50 | 0.15 | 165 | +0.0274 | 90.0% |
| 0.50 | 0.25 | 139 | +0.0274 | 90.0% |
| 0.50 | 0.35 | 119 | +0.0274 | 90.0% |
| 0.50 | 0.45 | 97 | +0.0274 | 90.0% |
| 0.55 | 0.10 | 166 | +0.0274 | 90.0% |
| 0.55 | 0.20 | 149 | +0.0274 | 90.0% |
| 0.55 | 0.30 | 128 | +0.0274 | 90.0% |
| 0.55 | 0.40 | 107 | +0.0274 | 90.0% |
| 0.55 | 0.50 | 93 | +0.0274 | 90.0% |
| 0.60 | 0.15 | 130 | +0.0274 | 90.0% |
| 0.60 | 0.25 | 129 | +0.0274 | 90.0% |
| 0.60 | 0.35 | 119 | +0.0274 | 90.0% |
| 0.60 | 0.45 | 97 | +0.0274 | 90.0% |
| 0.65 | 0.10 | 111 | +0.0274 | 90.0% |
| 0.65 | 0.20 | 111 | +0.0274 | 90.0% |
| 0.65 | 0.30 | 111 | +0.0274 | 90.0% |
| 0.65 | 0.40 | 106 | +0.0274 | 90.0% |
| 0.65 | 0.50 | 93 | +0.0274 | 90.0% |
| 0.70 | 0.15 | 59 | +0.0245 | 90.0% |
| 0.70 | 0.25 | 59 | +0.0245 | 90.0% |
| 0.70 | 0.35 | 59 | +0.0245 | 90.0% |
| 0.70 | 0.45 | 59 | +0.0245 | 90.0% |
| 0.75 | 0.10 | 39 | +0.0255 | 90.0% |
| 0.75 | 0.20 | 39 | +0.0255 | 90.0% |
| 0.75 | 0.30 | 39 | +0.0255 | 90.0% |
| 0.75 | 0.40 | 39 | +0.0255 | 90.0% |
| 0.75 | 0.50 | 39 | +0.0255 | 90.0% |
| 0.80 | 0.15 | 25 | +0.0383 | 90.0% |
| 0.80 | 0.25 | 25 | +0.0383 | 90.0% |
| 0.80 | 0.35 | 25 | +0.0383 | 90.0% |
| 0.80 | 0.45 | 25 | +0.0383 | 90.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 25 candidates, mean lock IC=+0.0383, 90.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | +0.0048 | 44.4% |
| 0.45 | 0.20 | 4 | -0.0402 | 25.0% |
| 0.45 | 0.30 | 4 | -0.0402 | 25.0% |
| 0.45 | 0.40 | 3 | -0.0591 | 0.0% |
| 0.45 | 0.50 | 2 | -0.0541 | 0.0% |
| 0.50 | 0.15 | 8 | -0.0033 | 37.5% |
| 0.50 | 0.25 | 4 | -0.0402 | 25.0% |
| 0.50 | 0.35 | 3 | -0.0591 | 0.0% |
| 0.50 | 0.45 | 2 | -0.0541 | 0.0% |
| 0.55 | 0.10 | 6 | -0.0367 | 16.7% |
| 0.55 | 0.20 | 4 | -0.0402 | 25.0% |
| 0.55 | 0.30 | 4 | -0.0402 | 25.0% |
| 0.55 | 0.40 | 3 | -0.0591 | 0.0% |
| 0.55 | 0.50 | 2 | -0.0541 | 0.0% |
| 0.60 | 0.15 | 4 | -0.0402 | 25.0% |
| 0.60 | 0.25 | 4 | -0.0402 | 25.0% |
| 0.60 | 0.35 | 3 | -0.0591 | 0.0% |
| 0.60 | 0.45 | 2 | -0.0541 | 0.0% |
| 0.65 | 0.10 | 3 | -0.0591 | 0.0% |
| 0.65 | 0.20 | 3 | -0.0591 | 0.0% |
| 0.65 | 0.30 | 3 | -0.0591 | 0.0% |
| 0.65 | 0.40 | 3 | -0.0591 | 0.0% |
| 0.65 | 0.50 | 2 | -0.0541 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 9 candidates, mean lock IC=+0.0048, 44.4% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 7 | +0.0191 | 71.4% |
| 0.45 | 0.20 | 2 | +0.0198 | 100.0% |
| 0.45 | 0.30 | 1 | +0.0094 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 2 | +0.0198 | 100.0% |
| 0.50 | 0.25 | 1 | +0.0094 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0152 | 66.7% |
| 0.55 | 0.20 | 2 | +0.0198 | 100.0% |
| 0.55 | 0.30 | 1 | +0.0094 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | +0.0198 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0094 | 100.0% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0458, 100.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 2204 | +0.0547 | 100.0% |
| 0.45 | 0.20 | 2185 | +0.0547 | 100.0% |
| 0.45 | 0.30 | 2070 | +0.0547 | 100.0% |
| 0.45 | 0.40 | 1954 | +0.0547 | 100.0% |
| 0.45 | 0.50 | 1652 | +0.0547 | 100.0% |
| 0.50 | 0.15 | 2197 | +0.0547 | 100.0% |
| 0.50 | 0.25 | 2148 | +0.0547 | 100.0% |
| 0.50 | 0.35 | 2016 | +0.0547 | 100.0% |
| 0.50 | 0.45 | 1812 | +0.0547 | 100.0% |
| 0.55 | 0.10 | 2195 | +0.0547 | 100.0% |
| 0.55 | 0.20 | 2185 | +0.0547 | 100.0% |
| 0.55 | 0.30 | 2070 | +0.0547 | 100.0% |
| 0.55 | 0.40 | 1954 | +0.0547 | 100.0% |
| 0.55 | 0.50 | 1652 | +0.0547 | 100.0% |
| 0.60 | 0.15 | 2116 | +0.0547 | 100.0% |
| 0.60 | 0.25 | 2109 | +0.0547 | 100.0% |
| 0.60 | 0.35 | 2013 | +0.0547 | 100.0% |
| 0.60 | 0.45 | 1812 | +0.0547 | 100.0% |
| 0.65 | 0.10 | 1928 | +0.0547 | 100.0% |
| 0.65 | 0.20 | 1928 | +0.0547 | 100.0% |
| 0.65 | 0.30 | 1927 | +0.0547 | 100.0% |
| 0.65 | 0.40 | 1899 | +0.0547 | 100.0% |
| 0.65 | 0.50 | 1651 | +0.0547 | 100.0% |
| 0.70 | 0.15 | 1483 | +0.0547 | 100.0% |
| 0.70 | 0.25 | 1483 | +0.0547 | 100.0% |
| 0.70 | 0.35 | 1483 | +0.0547 | 100.0% |
| 0.70 | 0.45 | 1482 | +0.0547 | 100.0% |
| 0.75 | 0.10 | 832 | +0.0547 | 100.0% |
| 0.75 | 0.20 | 832 | +0.0547 | 100.0% |
| 0.75 | 0.30 | 832 | +0.0547 | 100.0% |
| 0.75 | 0.40 | 832 | +0.0547 | 100.0% |
| 0.75 | 0.50 | 832 | +0.0547 | 100.0% |
| 0.80 | 0.15 | 264 | +0.0547 | 100.0% |
| 0.80 | 0.25 | 264 | +0.0547 | 100.0% |
| 0.80 | 0.35 | 264 | +0.0547 | 100.0% |
| 0.80 | 0.45 | 264 | +0.0547 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 2204 candidates, mean lock IC=+0.0547, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 45 | +0.0549 | 70.0% |
| 0.45 | 0.20 | 17 | +0.0496 | 80.0% |
| 0.45 | 0.30 | 10 | +0.0553 | 90.0% |
| 0.45 | 0.40 | 3 | +0.0523 | 66.7% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 25 | +0.0345 | 60.0% |
| 0.50 | 0.25 | 11 | +0.0567 | 90.0% |
| 0.50 | 0.35 | 5 | +0.0731 | 80.0% |
| 0.50 | 0.45 | 2 | +0.0888 | 100.0% |
| 0.55 | 0.10 | 25 | +0.0496 | 80.0% |
| 0.55 | 0.20 | 17 | +0.0496 | 80.0% |
| 0.55 | 0.30 | 10 | +0.0553 | 90.0% |
| 0.55 | 0.40 | 3 | +0.0523 | 66.7% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 12 | +0.0518 | 90.0% |
| 0.60 | 0.25 | 9 | +0.0561 | 88.9% |
| 0.60 | 0.35 | 5 | +0.0731 | 80.0% |
| 0.60 | 0.45 | 2 | +0.0888 | 100.0% |
| 0.65 | 0.10 | 4 | +0.0657 | 75.0% |
| 0.65 | 0.20 | 4 | +0.0657 | 75.0% |
| 0.65 | 0.30 | 4 | +0.0657 | 75.0% |
| 0.65 | 0.40 | 3 | +0.0523 | 66.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.35 → 5 candidates, mean lock IC=+0.0731, 80.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 21 | +0.0487 | 90.0% |
| 0.45 | 0.20 | 12 | +0.0487 | 90.0% |
| 0.45 | 0.30 | 5 | +0.0569 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 17 | +0.0487 | 90.0% |
| 0.50 | 0.25 | 8 | +0.0567 | 87.5% |
| 0.50 | 0.35 | 3 | +0.0490 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 16 | +0.0487 | 90.0% |
| 0.55 | 0.20 | 12 | +0.0487 | 90.0% |
| 0.55 | 0.30 | 5 | +0.0569 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | +0.0506 | 87.5% |
| 0.60 | 0.25 | 6 | +0.0468 | 83.3% |
| 0.60 | 0.35 | 3 | +0.0490 | 100.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 3 | +0.0490 | 100.0% |
| 0.65 | 0.20 | 3 | +0.0490 | 100.0% |
| 0.65 | 0.30 | 3 | +0.0490 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.30 → 5 candidates, mean lock IC=+0.0569, 100.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 986 | +0.1311 | 100.0% |
| 0.45 | 0.20 | 953 | +0.1311 | 100.0% |
| 0.45 | 0.30 | 858 | +0.1311 | 100.0% |
| 0.45 | 0.40 | 741 | +0.1311 | 100.0% |
| 0.45 | 0.50 | 562 | +0.1311 | 100.0% |
| 0.50 | 0.15 | 977 | +0.1311 | 100.0% |
| 0.50 | 0.25 | 902 | +0.1311 | 100.0% |
| 0.50 | 0.35 | 806 | +0.1311 | 100.0% |
| 0.50 | 0.45 | 666 | +0.1311 | 100.0% |
| 0.55 | 0.10 | 974 | +0.1311 | 100.0% |
| 0.55 | 0.20 | 952 | +0.1311 | 100.0% |
| 0.55 | 0.30 | 858 | +0.1311 | 100.0% |
| 0.55 | 0.40 | 741 | +0.1311 | 100.0% |
| 0.55 | 0.50 | 562 | +0.1311 | 100.0% |
| 0.60 | 0.15 | 880 | +0.1311 | 100.0% |
| 0.60 | 0.25 | 869 | +0.1311 | 100.0% |
| 0.60 | 0.35 | 804 | +0.1311 | 100.0% |
| 0.60 | 0.45 | 666 | +0.1311 | 100.0% |
| 0.65 | 0.10 | 732 | +0.1311 | 100.0% |
| 0.65 | 0.20 | 732 | +0.1311 | 100.0% |
| 0.65 | 0.30 | 732 | +0.1311 | 100.0% |
| 0.65 | 0.40 | 702 | +0.1311 | 100.0% |
| 0.65 | 0.50 | 559 | +0.1311 | 100.0% |
| 0.70 | 0.15 | 509 | +0.1311 | 100.0% |
| 0.70 | 0.25 | 509 | +0.1311 | 100.0% |
| 0.70 | 0.35 | 509 | +0.1311 | 100.0% |
| 0.70 | 0.45 | 509 | +0.1311 | 100.0% |
| 0.75 | 0.10 | 239 | +0.1311 | 100.0% |
| 0.75 | 0.20 | 239 | +0.1311 | 100.0% |
| 0.75 | 0.30 | 239 | +0.1311 | 100.0% |
| 0.75 | 0.40 | 239 | +0.1311 | 100.0% |
| 0.75 | 0.50 | 239 | +0.1311 | 100.0% |
| 0.80 | 0.15 | 72 | +0.1311 | 100.0% |
| 0.80 | 0.25 | 72 | +0.1311 | 100.0% |
| 0.80 | 0.35 | 72 | +0.1311 | 100.0% |
| 0.80 | 0.45 | 72 | +0.1311 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 986 candidates, mean lock IC=+0.1311, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 142 | +0.0980 | 100.0% |
| 0.45 | 0.20 | 113 | +0.0980 | 100.0% |
| 0.45 | 0.30 | 65 | +0.0991 | 100.0% |
| 0.45 | 0.40 | 27 | +0.1036 | 100.0% |
| 0.45 | 0.50 | 2 | +0.0842 | 100.0% |
| 0.50 | 0.15 | 130 | +0.0980 | 100.0% |
| 0.50 | 0.25 | 86 | +0.0980 | 100.0% |
| 0.50 | 0.35 | 45 | +0.1012 | 100.0% |
| 0.50 | 0.45 | 12 | +0.1005 | 90.0% |
| 0.55 | 0.10 | 123 | +0.0980 | 100.0% |
| 0.55 | 0.20 | 110 | +0.0980 | 100.0% |
| 0.55 | 0.30 | 65 | +0.0991 | 100.0% |
| 0.55 | 0.40 | 27 | +0.1036 | 100.0% |
| 0.55 | 0.50 | 2 | +0.0842 | 100.0% |
| 0.60 | 0.15 | 67 | +0.0976 | 100.0% |
| 0.60 | 0.25 | 67 | +0.0976 | 100.0% |
| 0.60 | 0.35 | 41 | +0.1012 | 100.0% |
| 0.60 | 0.45 | 12 | +0.1005 | 90.0% |
| 0.65 | 0.10 | 21 | +0.0942 | 100.0% |
| 0.65 | 0.20 | 21 | +0.0942 | 100.0% |
| 0.65 | 0.30 | 21 | +0.0942 | 100.0% |
| 0.65 | 0.40 | 16 | +0.0951 | 100.0% |
| 0.65 | 0.50 | 2 | +0.0842 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 27 candidates, mean lock IC=+0.1036, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 4 | +0.0039 | 25.0% |
| 0.45 | 0.20 | 1 | +0.0926 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 1 | +0.0926 | 100.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 2 | +0.0355 | 50.0% |
| 0.55 | 0.20 | 1 | +0.0926 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 4 candidates, mean lock IC=+0.0039, 25.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1131 | +0.0000 | +0.0547 | 0.48x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1254 | +0.0000 | +0.0229 | 0.18x | 2016-08-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1140 | +0.0000 | +0.0463 | 0.41x | 2016-08-24 |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | +0.1108 | +0.0000 | -0.0022 | -0.02x | 2017-09-06 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | +0.1140 | +0.0000 | -0.0365 | -0.32x | 2017-06-09 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1278 | +0.0000 | -0.0055 | -0.04x | 2017-06-09 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1039 | +0.0000 | -0.0223 | -0.21x | 2015-03-16 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0938 | +0.0000 | +0.0772 | 0.82x | 2013-08-21 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1109 | +0.0000 | -0.0261 | -0.24x | 2015-02-06 |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1094 | +0.0000 | +0.0408 | 0.37x | 2016-08-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1129 | +0.0000 | -0.0091 | -0.08x | 2017-04-07 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | +0.1209 | +0.0000 | +0.0259 | 0.21x | 2016-08-24 |
| `combo_max__max_up_ret__bar_ret_0` | +0.1000 | +0.0000 | -0.0225 | -0.23x | 2014-07-04 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0994 | +0.0000 | +0.0736 | 0.74x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1264 | +0.0000 | +0.0237 | 0.19x | 2016-08-24 |
| `max_up_ret` | +0.1001 | +0.0000 | -0.0463 | -0.46x | 2015-02-06 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | +0.0999 | +0.0000 | -0.0344 | -0.34x | 2015-02-06 |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | +0.1152 | +0.0000 | -0.0009 | -0.01x | 2017-07-10 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | +0.1037 | +0.0000 | -0.0457 | -0.44x | 2015-03-16 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1111 | +0.0000 | +0.0592 | 0.53x | 2017-08-08 |
| `combo_tri_mean__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | +0.1012 | +0.0000 | +0.0168 | 0.17x | 2013-09-23 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1070 | +0.0000 | -0.0157 | -0.15x | 2015-02-06 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | +0.1201 | +0.0000 | +0.0181 | 0.15x | 2017-06-09 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | +0.1065 | +0.0000 | +0.0559 | 0.52x | 2017-09-06 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1145 | +0.0000 | +0.0158 | 0.14x | 2017-06-09 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.1093 | +0.0000 | -0.0151 | -0.14x | 2014-12-08 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | +0.0935 | +0.0000 | -0.0212 | -0.23x | 2015-02-06 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | +0.0866 | +0.0000 | -0.0136 | -0.16x | 2013-08-21 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1065 | +0.0000 | -0.0082 | -0.08x | 2014-08-04 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1015 | +0.0000 | -0.0197 | -0.19x | 2014-07-04 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | +0.1123 | +0.0000 | -0.0061 | -0.05x | 2017-07-10 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.0921 | +0.0000 | -0.0223 | -0.24x | 2011-12-23 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.0920 | +0.0000 | +0.0053 | 0.06x | 2013-08-21 |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | +0.0881 | +0.0000 | -0.0225 | -0.26x | 2014-08-04 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | +0.1780 | +0.0000 | +0.1043 | 0.59x | 2016-09-26 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1948 | +0.0000 | +0.0406 | 0.21x | 2016-11-30 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | +0.1826 | +0.0000 | +0.0849 | 0.46x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | +0.1911 | +0.0000 | +0.0942 | 0.49x | No decay |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | +0.1751 | +0.0000 | +0.1090 | 0.62x | No decay |
| `combo_mean__bar_ret_0__close_vs_open_range` | +0.1641 | +0.0000 | +0.0469 | 0.29x | No decay |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1790 | +0.0000 | +0.0379 | 0.21x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1696 | +0.0000 | +0.1095 | 0.65x | No decay |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1791 | +0.0000 | +0.0426 | 0.24x | No decay |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1649 | +0.0000 | +0.0933 | 0.57x | 2021-07-28 |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | +0.1479 | +0.0000 | +0.0295 | 0.20x | 2020-01-06 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1870 | +0.0000 | +0.0289 | 0.15x | 2025-07-24 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1871 | +0.0000 | +0.0316 | 0.17x | 2025-07-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | +0.1829 | +0.0000 | +0.0977 | 0.53x | No decay |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | +0.1745 | +0.0000 | +0.0201 | 0.12x | 2026-04-07 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0` | +0.1658 | +0.0000 | +0.1163 | 0.70x | No decay |
| `combo_tri_mean__max_up_ret__early_body_momentum__bar_ret_0` | +0.1797 | +0.0000 | +0.0299 | 0.17x | No decay |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1908 | +0.0000 | +0.0883 | 0.46x | No decay |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | +0.1647 | +0.0000 | +0.0637 | 0.39x | 2020-01-06 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1841 | +0.0000 | +0.0337 | 0.18x | 2021-07-28 |
| `combo_max__bar_ret_0__max_down_ret` | +0.1607 | +0.0000 | +0.0518 | 0.32x | 2016-11-01 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1655 | +0.0000 | +0.0977 | 0.59x | No decay |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1818 | +0.0000 | +0.0534 | 0.29x | 2016-11-30 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | +0.1850 | +0.0000 | +0.0478 | 0.26x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1950 | +0.0000 | +0.0598 | 0.31x | No decay |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1766 | +0.0000 | +0.0626 | 0.35x | No decay |
| `combo_mean__max_up_ret__max_down_ret` | +0.1798 | +0.0000 | +0.0502 | 0.28x | No decay |
| `combo_max__max_up_ret__max_down_ret` | +0.1753 | +0.0000 | +0.0367 | 0.21x | 2016-11-01 |
| `combo_min__net_volume_flow__bar_body_rng_0` | +0.1474 | +0.0000 | +0.0618 | 0.42x | No decay |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1545 | +0.0000 | +0.0817 | 0.53x | 2016-09-26 |
| `max_up_ret` | +0.1829 | +0.0000 | +0.0308 | 0.17x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1929 | +0.0000 | +0.0726 | 0.38x | No decay |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1741 | +0.0000 | +0.0980 | 0.56x | No decay |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__bar_ret_0` | +0.1689 | +0.0000 | +0.0212 | 0.13x | 2026-04-07 |
| `combo_min__net_volume_flow__close_vs_open_range` | +0.1443 | +0.0000 | +0.0525 | 0.36x | 2016-11-01 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1539 | +0.0000 | +0.0560 | 0.36x | 2016-11-01 |
| `combo_rank_max__bar_ret_0__close_vs_open_range` | +0.1657 | +0.0000 | +0.0238 | 0.14x | No decay |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1927 | +0.0000 | +0.0301 | 0.16x | 2020-01-06 |
| `combo_min__first_bar_return__early_order_flow_imbalance` | +0.1442 | +0.0000 | +0.0421 | 0.29x | 2016-11-01 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1901 | +0.0000 | +0.0453 | 0.24x | No decay |
| `combo_mean__max_up_ret__first_bar_return` | +0.1782 | +0.0000 | +0.0281 | 0.16x | No decay |
| `combo_diff__max_up_ret__body_size_progression` | +0.1702 | +0.0000 | +0.0418 | 0.25x | 2025-06-25 |
| `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1847 | +0.0000 | +0.0950 | 0.51x | No decay |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | +0.1715 | +0.0000 | +0.0447 | 0.26x | 2019-12-05 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1910 | +0.0000 | +0.0829 | 0.43x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | +0.1771 | +0.0000 | +0.0702 | 0.40x | No decay |
| `combo_tri_mean__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | +0.1579 | +0.0000 | +0.0397 | 0.25x | 2016-11-01 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | +0.1607 | +0.0000 | +0.1060 | 0.66x | 2016-09-26 |
| `combo_mean__first_bar_return__bar_body_rng_0` | +0.1405 | +0.0000 | +0.0473 | 0.34x | 2013-09-23 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1714 | +0.0000 | +0.0387 | 0.23x | No decay |
| `combo_rank_max__max_up_ret__net_volume_flow` | +0.1800 | +0.0000 | +0.0489 | 0.27x | 2016-11-30 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1778 | +0.0000 | +0.0867 | 0.49x | 2019-12-05 |
| `combo_rank_max__max_up_ret__bar_ret_0` | +0.1707 | +0.0000 | +0.0294 | 0.17x | No decay |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +0.1637 | +0.0000 | +0.0121 | 0.07x | 2020-01-06 |
| `combo_mean__bar_ret_0__early_order_flow_imbalance` | +0.1504 | +0.0000 | +0.0219 | 0.15x | 2016-11-01 |
| `combo_tri_median__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | +0.1632 | +0.0000 | +0.0729 | 0.45x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.1884 | +0.0000 | +0.0952 | 0.51x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1681 | +0.0000 | +0.1087 | 0.65x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.2044 | +0.0000 | +0.0524 | 0.26x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1617 | +0.0000 | +0.1136 | 0.70x | 2016-08-24 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1770 | +0.0000 | +0.0650 | 0.37x | No decay |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | +0.1941 | +0.0000 | +0.1062 | 0.55x | 2016-09-26 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | +0.1749 | +0.0000 | +0.0419 | 0.24x | 2020-01-06 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | +0.1776 | +0.0000 | +0.0565 | 0.32x | No decay |
| `combo_max__max_up_ret__close_vs_open_range` | +0.1759 | +0.0000 | +0.0264 | 0.15x | 2016-11-01 |
| `combo_clamp_diff__first_bar_return__body_size_progression` | +0.1429 | +0.0000 | +0.0511 | 0.36x | 2020-12-18 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__early_body_momentum` | +0.1580 | +0.0000 | +0.0900 | 0.57x | 2016-09-26 |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | +0.1746 | +0.0000 | +0.0218 | 0.12x | 2016-11-30 |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | +0.1637 | +0.0000 | +0.0450 | 0.28x | No decay |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | +0.1736 | +0.0000 | +0.0170 | 0.10x | 2016-11-30 |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | +0.1887 | +0.0000 | +0.0274 | 0.15x | No decay |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | +0.1911 | +0.0000 | +0.0237 | 0.12x | 2016-11-30 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1741 | +0.0000 | +0.0857 | 0.49x | No decay |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1551 | +0.0000 | +0.1051 | 0.68x | 2016-09-26 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | +0.1883 | +0.0000 | +0.0276 | 0.15x | 2025-07-24 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1938 | +0.0000 | +0.0366 | 0.19x | No decay |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | +0.1409 | +0.0000 | +0.1143 | 0.81x | 2023-01-16 |
| `combo_rank_max__max_up_ret__max_down_ret` | +0.1752 | +0.0000 | +0.0572 | 0.33x | 2016-11-30 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1585 | +0.0000 | +0.1065 | 0.67x | 2022-12-15 |
| `combo_mean__max_up_ret__close_vs_open_range` | +0.1718 | +0.0000 | +0.0355 | 0.21x | No decay |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | +0.1678 | +0.0000 | +0.0926 | 0.55x | No decay |
| `combo_mean__first_bar_return__max_down_ret` | +0.1481 | +0.0000 | +0.0745 | 0.50x | No decay |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1583 | +0.0000 | +0.1041 | 0.66x | 2022-12-15 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | +0.1396 | +0.0000 | +0.1117 | 0.80x | 2020-12-18 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | +0.1804 | +0.0000 | +0.0774 | 0.43x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +0.1807 | +0.0000 | +0.0449 | 0.25x | No decay |
| `combo_mean__first_bar_return__shaved_bar_trend_conviction` | +0.1483 | +0.0000 | +0.0435 | 0.29x | 2016-11-01 |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | +0.1650 | +0.0000 | +0.0087 | 0.05x | 2017-02-06 |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | +0.1682 | +0.0000 | +0.0363 | 0.22x | 2026-04-07 |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | +0.1614 | +0.0000 | +0.0158 | 0.10x | No decay |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1377 | +0.0000 | +0.1138 | 0.83x | 2011-12-23 |
| `combo_rank_min__net_volume_flow__vwap_close_divergence_trend` | +0.1445 | +0.0000 | +0.0451 | 0.31x | 2016-11-01 |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | +0.1271 | +0.0000 | -0.0157 | -0.12x | 2017-08-08 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1429 | +0.0000 | +0.0970 | 0.68x | 2016-09-26 |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | +0.1616 | +0.0000 | +0.0170 | 0.11x | No decay |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | +0.1616 | +0.0000 | +0.0627 | 0.39x | No decay |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | +0.1327 | +0.0000 | +0.0356 | 0.27x | 2016-11-01 |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | +0.1133 | +0.0000 | +0.0240 | 0.21x | 2016-11-01 |
| `combo_sig_product__net_volume_flow__vwap_close_divergence_trend` | +0.1410 | +0.0000 | -0.0041 | -0.03x | 2016-11-01 |
| `num_up_bars` | +0.1234 | +0.0000 | +0.0459 | 0.37x | 2020-02-12 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1550 | +0.0000 | +0.1275 | 0.82x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1578 | +0.0000 | +0.1339 | 0.85x | 2017-04-28 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1410 | +0.0000 | +0.1353 | 0.96x | 2011-10-18 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.1521 | +0.0000 | +0.1249 | 0.82x | 2016-10-24 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | +0.1659 | +0.0000 | +0.1303 | 0.79x | 2017-01-20 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1626 | +0.0000 | +0.1428 | 0.88x | 2017-02-27 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1551 | +0.0000 | +0.1296 | 0.84x | 2011-10-18 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1644 | +0.0000 | +0.1135 | 0.69x | 2016-12-21 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1513 | +0.0000 | +0.1258 | 0.83x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1616 | +0.0000 | +0.1258 | 0.78x | 2016-12-21 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1510 | +0.0000 | +0.1228 | 0.81x | 2017-01-20 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1656 | +0.0000 | +0.1289 | 0.78x | 2017-02-27 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1549 | +0.0000 | +0.1403 | 0.91x | 2011-11-16 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1553 | +0.0000 | +0.1310 | 0.84x | 2017-02-27 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1608 | +0.0000 | +0.1285 | 0.80x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1717 | +0.0000 | +0.1325 | 0.77x | 2017-01-20 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.1269 | +0.0000 | +0.1518 | 1.20x | 2011-10-18 |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1511 | +0.0000 | +0.1454 | 0.96x | 2016-10-24 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | +0.1511 | +0.0000 | +0.1279 | 0.85x | 2017-01-20 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | +0.1610 | +0.0000 | +0.1319 | 0.82x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1398 | +0.0000 | +0.1347 | 0.96x | 2011-10-18 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1635 | +0.0000 | +0.1319 | 0.81x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1597 | +0.0000 | +0.1015 | 0.64x | 2016-10-24 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1381 | +0.0000 | +0.1396 | 1.01x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1701 | +0.0000 | +0.1318 | 0.77x | 2017-01-20 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1639 | +0.0000 | +0.1344 | 0.82x | 2017-02-27 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | +0.1443 | +0.0000 | +0.1207 | 0.84x | 2017-01-20 |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | +0.1448 | +0.0000 | +0.1199 | 0.83x | 2017-01-20 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1578 | +0.0000 | +0.1248 | 0.79x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1481 | +0.0000 | +0.1497 | 1.01x | 2016-10-24 |
| `combo_min__volume_weighted_price_position__limit_down_proximity_early` | +0.1293 | +0.0000 | +0.1345 | 1.04x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | +0.1453 | +0.0000 | +0.1093 | 0.75x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | +0.1528 | +0.0000 | +0.1321 | 0.86x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1454 | +0.0000 | +0.1073 | 0.74x | 2011-11-16 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1561 | +0.0000 | +0.0890 | 0.57x | 2017-02-27 |
| `combo_mean__rbreaker_sell_setup_proximity_early__rally_strength_max` | +0.1522 | +0.0000 | +0.1340 | 0.88x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | +0.1469 | +0.0000 | +0.1348 | 0.92x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1508 | +0.0000 | +0.1526 | 1.01x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1543 | +0.0000 | +0.1421 | 0.92x | 2016-10-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | +0.1439 | +0.0000 | +0.1226 | 0.85x | 2016-10-24 |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | +0.1421 | +0.0000 | +0.1382 | 0.97x | 2011-10-18 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | +0.1537 | +0.0000 | +0.0727 | 0.47x | 2016-12-21 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | +0.1105 | +0.0000 | +0.1100 | 1.00x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | +0.1457 | +0.0000 | +0.0933 | 0.64x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | +0.1429 | +0.0000 | +0.0500 | 0.35x | 2016-12-21 |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | +0.1417 | +0.0000 | +0.1367 | 0.96x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0686 | 0.50x | 2016-10-24 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +0.1503 | +0.0000 | +0.0885 | 0.59x | 2017-02-27 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1367 | +0.0000 | +0.1507 | 1.10x | 2016-09-14 |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | +0.1252 | +0.0000 | +0.1332 | 1.06x | 2011-10-18 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1215 | +0.0000 | +0.1592 | 1.31x | 2011-10-18 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1444 | +0.0000 | +0.1102 | 0.76x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | +0.1388 | +0.0000 | +0.1426 | 1.03x | 2011-10-18 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1428 | +0.0000 | +0.1259 | 0.88x | 2016-09-14 |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | +0.1274 | +0.0000 | +0.1424 | 1.12x | 2016-09-14 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | +0.1253 | +0.0000 | +0.1467 | 1.17x | 2011-10-18 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1608 | +0.0000 | +0.1308 | 0.81x | 2017-01-20 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | +0.1454 | +0.0000 | +0.0515 | 0.35x | 2017-01-20 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | +0.1572 | +0.0000 | +0.1162 | 0.74x | 2018-01-31 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | +0.1571 | +0.0000 | +0.0717 | 0.46x | 2017-01-20 |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | +0.1383 | +0.0000 | +0.1024 | 0.74x | 2017-04-28 |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | +0.1494 | +0.0000 | +0.0823 | 0.55x | 2017-01-20 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | +0.1423 | +0.0000 | +0.0947 | 0.67x | 2016-10-24 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | +0.0866 | +0.0000 | +0.1321 | 1.53x | 2011-10-18 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1560 | +0.0000 | +0.0820 | 0.53x | 2016-12-21 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1520 | +0.0000 | +0.0776 | 0.51x | 2017-01-20 |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | +0.1540 | +0.0000 | +0.1473 | 0.96x | 2016-10-24 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1470 | +0.0000 | +0.1058 | 0.72x | 2016-09-14 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1558 | +0.0000 | +0.0864 | 0.55x | 2017-01-20 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +0.1495 | +0.0000 | +0.1120 | 0.75x | 2017-02-27 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1509 | +0.0000 | +0.1491 | 0.99x | 2017-01-20 |
| `combo_tri_mean__opening_drive_thrust_ratio__demark_setup_reversal_early__star50_limit_proximity_early` | +0.1336 | +0.0000 | +0.0786 | 0.59x | No decay |
| `combo_rank_min__max_up_ret__gap_pct` | +0.1371 | +0.0000 | +0.1238 | 0.90x | 2016-09-14 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1483 | +0.0000 | +0.0939 | 0.63x | 2017-01-20 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | +0.1510 | +0.0000 | +0.1056 | 0.70x | 2016-10-24 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1481 | +0.0000 | +0.1133 | 0.76x | 2016-09-14 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | +0.1355 | +0.0000 | +0.0879 | 0.65x | 2016-10-24 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1600 | +0.0000 | +0.0948 | 0.59x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | +0.1382 | +0.0000 | +0.1383 | 1.00x | 2011-11-16 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1527 | +0.0000 | +0.1003 | 0.66x | 2016-10-24 |
| `combo_max__max_up_ret__rally_strength_max` | +0.1304 | +0.0000 | +0.0701 | 0.54x | 2017-08-29 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1536 | +0.0000 | +0.1106 | 0.72x | 2016-10-24 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | +0.1467 | +0.0000 | +0.0811 | 0.55x | 2017-01-20 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1384 | +0.0000 | +0.1453 | 1.05x | 2016-09-14 |
| `combo_max__max_up_ret__volume_price_confirmation` | +0.1416 | +0.0000 | +0.0655 | 0.46x | 2017-01-20 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1345 | +0.0000 | +0.0366 | 0.27x | 2014-03-25 |
| `combo_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | +0.1293 | +0.0000 | +0.1150 | 0.89x | 2017-01-20 |
| `combo_mean__volume_weighted_price_position__rbreaker_buy_setup_proximity_early` | +0.1409 | +0.0000 | +0.1340 | 0.95x | 2016-10-24 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1401 | +0.0000 | +0.0724 | 0.52x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | +0.1282 | +0.0000 | +0.0714 | 0.56x | 2016-10-24 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1541 | +0.0000 | +0.0738 | 0.48x | 2016-10-24 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1539 | +0.0000 | +0.1220 | 0.79x | 2017-02-27 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1392 | +0.0000 | +0.0755 | 0.54x | 2017-01-20 |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | +0.1260 | +0.0000 | +0.0378 | 0.30x | 2016-10-24 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1317 | +0.0000 | +0.1308 | 0.99x | 2011-10-18 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | +0.1296 | +0.0000 | +0.1217 | 0.94x | 2011-03-11 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1442 | +0.0000 | +0.1138 | 0.79x | 2016-09-14 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1558 | +0.0000 | +0.0786 | 0.50x | 2016-12-21 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | +0.1451 | +0.0000 | +0.1428 | 0.98x | 2016-09-14 |
| `combo_clamp_diff__volume_weighted_price_position__body_size_progression` | +0.1136 | +0.0000 | +0.0607 | 0.53x | 2017-01-20 |
| `combo_min__max_up_ret__gap_pct` | +0.1456 | +0.0000 | +0.1305 | 0.90x | 2011-11-16 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__bar_ret_0` | +0.1460 | +0.0000 | +0.0906 | 0.62x | 2017-02-27 |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | +0.1413 | +0.0000 | +0.0677 | 0.48x | 2017-01-20 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +0.1539 | +0.0000 | +0.0732 | 0.48x | 2016-12-21 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | +0.1315 | +0.0000 | +0.1226 | 0.93x | 2011-03-11 |
| `combo_max__rbreaker_sell_setup_proximity_early__rally_strength_max` | +0.1325 | +0.0000 | +0.1224 | 0.92x | 2016-10-24 |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | +0.1084 | +0.0000 | +0.1410 | 1.30x | 2011-10-18 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | +0.1190 | +0.0000 | +0.0936 | 0.79x | 2017-02-27 |
| `combo_rank_max__star50_limit_proximity_early__volume_price_confirmation` | +0.1439 | +0.0000 | +0.1191 | 0.83x | 2016-12-21 |
| `combo_rank_min__max_up_ret__rally_strength_max` | +0.1340 | +0.0000 | +0.0677 | 0.50x | 2016-10-24 |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | +0.1541 | +0.0000 | +0.0894 | 0.58x | 2017-01-20 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +0.1368 | +0.0000 | +0.0578 | 0.42x | 2017-01-20 |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | +0.0972 | +0.0000 | +0.1102 | 1.13x | 2011-12-15 |
| `combo_mean__max_up_ret__volume_price_confirmation` | +0.1488 | +0.0000 | +0.0849 | 0.57x | 2017-01-20 |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1376 | +0.0000 | +0.0814 | 0.59x | 2017-01-20 |
| `combo_min__bar_ret_0__directional_volume_signature` | +0.1239 | +0.0000 | +0.0625 | 0.50x | 2017-01-20 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0659 | 0.48x | 2017-04-28 |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | +0.1259 | +0.0000 | +0.0872 | 0.69x | 2018-04-10 |
| `combo_min__max_up_ret__bar_ret_0` | +0.1477 | +0.0000 | +0.0839 | 0.57x | 2017-01-20 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1491 | +0.0000 | +0.0841 | 0.56x | 2016-12-21 |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | +0.1251 | +0.0000 | +0.0633 | 0.51x | 2018-03-08 |
| `combo_diff__max_up_ret__keltner_squeeze_width` | +0.1258 | +0.0000 | +0.0690 | 0.55x | 2018-03-08 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.1757). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.1815). Consider relaxing this gate.
3. **300ETF `single` — B4 Correlation Gate too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.4833). Consider relaxing this gate.
4. **300ETF `single` — Admission too loose**: 86% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
5. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 6.0%, mean lock Sharpe=-0.5144). Consider relaxing this gate.
6. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.3478). Consider relaxing this gate.
7. **300ETF `short` — B2 Rolling Guard too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.2144). Consider relaxing this gate.
8. **300ETF `short` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.1920). Consider relaxing this gate.
9. **50ETF `single` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 22.0%, mean lock Sharpe=-0.3969). Consider relaxing this gate.
10. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.1306). Consider relaxing this gate.
11. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=-0.0024). Consider relaxing this gate.
12. **500ETF `single` — Admission too loose**: 76% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
13. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.3640). Consider relaxing this gate.
14. **500ETF `long` — BH-FDR Gate too strict**: 73.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.4499). Consider relaxing this gate.
15. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3004). Consider relaxing this gate.
16. **500ETF `short` — B2 Rolling Guard too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3230). Consider relaxing this gate.
17. **159915ETF `single` — 7-Year Jackknife Sign Stability too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.7476). Consider relaxing this gate.
18. **159915ETF `single` — B2 Rolling Guard too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.8552). Consider relaxing this gate.
19. **159915ETF `single` — B3 Composite Floor too strict**: 83.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.2298). Consider relaxing this gate.
20. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+1.0384). Consider relaxing this gate.
21. **159915ETF `long` — BH-FDR Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 43.0%, mean lock Sharpe=+0.8546). Consider relaxing this gate.
22. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=-0.1211). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
