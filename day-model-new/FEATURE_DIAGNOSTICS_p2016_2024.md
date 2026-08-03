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

### 300ETF — `single` (Full Model Lockbox IC: +0.0265, Sharpe: -0.1484)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1068 | +0.0383 | +0.0383 | -0.0697 | 0.79 | 1/8 | 0.86 | 3.04 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0008 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1045 | +0.0512 | +0.0512 | +0.6322 | 0.77 | 1/8 | 0.86 | 5.39 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0006 | +0.0000 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0939 | -0.0018 | -0.0018 | +0.1999 | 0.85 | 0/8 | 1.48 | 4.09 | `volume_weighted_price_position` (1.11) | -0.0004 | -0.0341 |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1007 | +0.0123 | +0.0123 | -0.4689 | 0.80 | 1/8 | 0.86 | 2.06 | `volume_weighted_price_position` (1.11) | +0.0001 | +0.0000 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0915 | -0.0131 | -0.0131 | -0.5701 | 0.90 | 2/8 | 1.54 | 6.91 | `volume_weighted_price_position` (1.11) | -0.0001 | -0.0268 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1019 | +0.0460 | +0.0460 | +0.1064 | 0.73 | 1/8 | 0.85 | 4.68 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0007 | +0.0000 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0886 | +0.0067 | +0.0067 | -0.2911 | 0.83 | 1/8 | 1.37 | 3.88 | `max_up_ret` (0.89) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0989 | +0.0340 | +0.0340 | -0.1960 | 0.93 | 1/8 | 1.02 | -14.03 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0009 | +0.0000 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0924 | +0.0084 | +0.0084 | -0.0883 | 0.71 | 1/8 | 0.87 | 1.96 | `max_up_ret` (0.89) | -0.0005 | +0.0167 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1013 | +0.0094 | +0.0094 | +0.1080 | 0.78 | 1/8 | 0.82 | 1.96 | `volume_weighted_price_position` (1.11) | -0.0008 | +0.0527 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0915 | -0.0023 | -0.0023 | -0.5759 | 0.82 | 0/8 | 1.74 | 3.10 | `volume_weighted_price_position` (1.11) | -0.0002 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0882 | +0.0655 | +0.0655 | +0.9697 | 0.82 | 1/8 | 0.80 | 8.68 | `rbreaker_buy_setup_proximity_early` (2.08) | +0.0008 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0828 | -0.0138 | -0.0138 | -0.3231 | 0.92 | 0/8 | 1.93 | 5.15 | `volume_weighted_price_position` (1.11) | -0.0004 | -0.0534 |
| `bar_body_rng_0` | Other Technical | +1 | +0.0988 | +0.0301 | +0.0301 | -0.1439 | 0.68 | 1/8 | 0.73 | 1.22 | — | +0.0004 | +0.0000 |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.0962 | +0.0069 | +0.0069 | -0.3876 | 0.76 | 1/8 | 0.92 | 1.72 | `volume_weighted_price_position` (1.11) | -0.0001 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1010 | +0.0317 | +0.0317 | +0.5329 | 0.80 | 1/8 | 1.12 | 5.24 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0003 | -0.0315 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0998 | +0.0045 | +0.0045 | -0.5240 | 0.71 | 1/8 | 0.94 | 1.74 | `volume_weighted_price_position` (1.11) | -0.0004 | -0.0534 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1008 | +0.0254 | +0.0254 | +0.4883 | 0.81 | 1/8 | 1.11 | 5.15 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0004 | +0.0167 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0955 | +0.0125 | +0.0125 | -0.4568 | 0.90 | 1/8 | 1.06 | 3.88 | `volume_weighted_price_position` (1.11) | -0.0001 | +0.0527 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1022 | +0.0351 | +0.0351 | +0.1736 | 0.87 | 1/8 | 1.13 | -40.14 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0005 | +0.0000 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0989 | +0.0057 | +0.0057 | -0.2202 | 0.85 | 1/8 | 1.03 | 3.29 | `volume_weighted_price_position` (1.11) | -0.0005 | +0.0527 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0909 | +0.0124 | +0.0124 | +0.1247 | 0.68 | 0/8 | 1.13 | 1.40 | `max_up_ret` (0.89) | +0.0005 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1045 | -0.0166 | -0.0166 | -0.3738 | 0.79 | 1/8 | 1.03 | 3.12 | `opening_drive_thrust_ratio` (0.83) | -0.0003 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0841 | +0.0193 | +0.0193 | +0.2919 | 0.85 | 1/8 | 1.27 | 7.30 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0003 | +0.0167 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.0881 | +0.0572 | +0.0572 | +0.6639 | 0.86 | 1/8 | 0.74 | 7.30 | `limit_down_proximity_early` (2.08) | +0.0014 | +0.1081 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1095 | +0.0329 | +0.0329 | +0.3820 | 0.63 | 1/8 | 0.94 | 1.81 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0006 | -0.0315 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1001 | +0.0183 | +0.0183 | -0.0646 | 0.69 | 0/8 | 0.96 | 1.64 | `max_up_ret` (0.89) | +0.0004 | +0.0000 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0929 | -0.0025 | -0.0025 | -0.2554 | 0.62 | 1/8 | 0.89 | 2.08 | `max_up_ret` (0.89) | -0.0004 | +0.0000 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0876 | +0.0013 | +0.0013 | -0.3332 | 0.89 | 1/8 | 1.95 | 6.25 | `volume_weighted_price_position` (1.11) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1098 | +0.0362 | +0.0362 | +0.3660 | 0.56 | 0/8 | 0.77 | 1.61 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0002 | +0.1081 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0989 | +0.0217 | +0.0217 | -0.2624 | 0.79 | 1/8 | 0.82 | 1.95 | `opening_drive_thrust_ratio` (0.83) | +0.0000 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1085 | +0.0362 | +0.0362 | +0.6343 | 0.68 | 1/8 | 0.87 | 2.26 | `star50_limit_proximity_early` (1.24) | +0.0006 | -0.0315 |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1102 | +0.0337 | +0.0337 | +0.2687 | 0.74 | 1/8 | 0.87 | 3.16 | `star50_limit_proximity_early` (1.24) | +0.0003 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1013 | +0.0496 | +0.0496 | +0.5363 | 0.59 | 1/8 | 0.75 | 1.63 | `star50_limit_proximity_early` (1.24) | +0.0006 | -0.0315 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0926 | +0.0134 | +0.0134 | +0.2457 | 0.66 | 0/8 | 1.20 | 1.53 | `max_up_ret` (0.89) | +0.0003 | -0.0534 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0899 | +0.0334 | +0.0334 | +0.9753 | 0.74 | 1/8 | 1.18 | 3.01 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0011 | +0.0000 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0953 | +0.0012 | +0.0012 | +0.0941 | 0.87 | 2/8 | 1.05 | 3.58 | `volume_weighted_price_position` (1.11) | -0.0005 | -0.0534 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.0933 | +0.0060 | +0.0060 | -0.4547 | 0.83 | 1/8 | 1.21 | 4.07 | — | -0.0001 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1022 | +0.0022 | +0.0022 | -0.4646 | 0.78 | 1/8 | 0.95 | 2.88 | `opening_drive_thrust_ratio` (0.83) | -0.0003 | +0.0000 |
| `combo_max__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1004 | +0.0220 | +0.0220 | +0.1568 | 0.60 | 0/8 | 0.66 | 1.18 | `bar_body_rng_0` (0.68) | -0.0000 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0952 | +0.0270 | +0.0270 | +0.5172 | 0.78 | 1/8 | 1.27 | 5.19 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0005 | -0.0315 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0807 | +0.0117 | +0.0117 | -0.3080 | 0.93 | 1/8 | 1.76 | 5.15 | `max_up_ret` (0.89) | -0.0000 | -0.0534 |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0992 | -0.0121 | -0.0121 | -0.4620 | 0.80 | 1/8 | 1.40 | 4.38 | `volume_weighted_price_position` (1.11) | -0.0005 | -0.0534 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1013 | +0.0215 | +0.0215 | +0.5132 | 0.84 | 1/8 | 0.97 | 5.06 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0005 | -0.0333 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0856 | +0.0449 | +0.0449 | +0.4220 | 0.97 | 1/8 | 1.04 | -6.11 | `rbreaker_buy_setup_proximity_early` (2.08) | +0.0003 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0924 | +0.0376 | +0.0376 | +0.6416 | 0.82 | 1/8 | 0.81 | 7.20 | `star50_limit_proximity_early` (1.24) | +0.0010 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0849 | +0.0427 | +0.0427 | -0.6213 | 0.77 | 1/8 | 1.27 | -59.25 | `star50_limit_proximity_early` (1.24) | +0.0005 | -0.0315 |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.1034 | +0.0071 | +0.0071 | +0.2288 | 0.75 | 0/8 | 1.01 | 2.79 | `volume_weighted_price_position` (1.11) | -0.0003 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.0773 | -0.0047 | -0.0047 | +0.3486 | 0.89 | 1/8 | 1.65 | 3.65 | — | +0.0000 | +0.0000 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0963 | +0.0168 | +0.0168 | +0.1329 | 0.64 | 0/8 | 0.64 | 1.22 | `star50_limit_proximity_early` (1.24) | +0.0004 | +0.1081 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0405 | -0.0158 | -0.0158 | -1.0471 | 0.88 | 1/8 | 0.77 | 20.36 | `volume_weighted_price_position` (1.11) | -0.0003 | -0.0268 |
| `combo_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0955 | +0.0000 | +0.0000 | +0.3515 | 0.76 | 0/8 | 1.14 | 2.94 | `max_up_ret` (0.89) | +0.0002 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0808 | +0.0306 | +0.0306 | -0.3020 | 0.63 | 1/8 | 1.41 | 1.24 | `rbreaker_sell_setup_proximity_early` (1.07) | -0.0001 | -0.0315 |
| `combo_rank_max__bar_body_rng_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0901 | +0.0189 | +0.0189 | +0.5330 | 0.74 | 1/8 | 0.52 | 1.64 | `volume_surge_direction` (0.95) | +0.0002 | +0.0000 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0918 | +0.0267 | +0.0267 | +0.3866 | 0.72 | 0/8 | 1.19 | 1.77 | `early_vwap_acceleration` (1.02) | +0.0005 | -0.0150 |
| `combo_mean__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0898 | +0.0161 | +0.0161 | +0.3850 | 0.75 | 1/8 | 1.04 | 4.63 | `volume_surge_direction` (0.95) | +0.0006 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0727 | +0.0225 | +0.0225 | +0.1191 | 0.90 | 1/8 | 1.82 | 8.85 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0005 | -0.0315 |
| `combo_max__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0764 | +0.0092 | +0.0092 | +0.3974 | 0.98 | 2/8 | 1.02 | 175.30 | `volume_surge_direction` (0.95) | +0.0006 | +0.0000 |
| `combo_ratio__bar_ret_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0898 | +0.0050 | +0.0050 | +0.2005 | 0.58 | 1/8 | 0.60 | 0.81 | `volume_surge_direction` (0.95) | +0.0000 | +0.0000 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0714 | -0.0006 | -0.0006 | -0.4264 | 0.88 | 1/8 | 2.09 | 6.50 | `max_up_ret` (0.89) | -0.0001 | +0.0167 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0931 | +0.0256 | +0.0256 | +0.0903 | 0.82 | 1/8 | 0.89 | 6.19 | `volume_surge_direction` (0.95) | +0.0000 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0791 | +0.0285 | +0.0285 | -0.0878 | 0.83 | 1/8 | 1.94 | 3.50 | `rbreaker_sell_setup_proximity_early` (1.07) | -0.0000 | -0.0315 |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0892 | -0.0116 | -0.0116 | -0.6265 | 0.80 | 1/8 | 0.66 | 1.83 | `volume_weighted_price_position` (1.11) | -0.0001 | -0.0268 |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0967 | +0.0081 | +0.0081 | +0.0717 | 0.74 | 1/8 | 0.87 | 3.14 | `max_up_ret` (0.89) | +0.0002 | -0.1698 |
| `combo_max__first_bar_return__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0962 | -0.0050 | -0.0050 | +0.4800 | 0.65 | 0/8 | 0.72 | 2.17 | `first_bar_sentiment` (0.69) | -0.0003 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.0937 | +0.0512 | +0.0512 | +0.0639 | 0.68 | 0/8 | 0.85 | 0.89 | `rbreaker_sell_setup_proximity_early` (1.07) | -0.0002 | -0.0315 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0652 | -0.0189 | -0.0189 | -0.4041 | 1.12 | 2/8 | 2.03 | 31.17 | — | -0.0002 | +0.0167 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0609 | +0.0374 | +0.0374 | -0.6001 | 0.87 | 2/8 | 2.34 | -4.74 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0005 | -0.0315 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0719 | +0.0288 | +0.0288 | -0.2338 | 0.74 | 1/8 | 1.21 | 1.24 | `bar_vol_0` (2.19) | +0.0008 | +0.1081 |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0976 | -0.0229 | -0.0229 | -1.8533 | 0.75 | 1/8 | 0.78 | 2.33 | `volume_weighted_price_position` (1.11) | -0.0003 | +0.0000 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0854 | +0.0225 | +0.0225 | -0.2686 | 0.82 | 0/8 | 1.14 | 2.01 | `early_vwap_acceleration` (1.02) | +0.0005 | -0.0268 |
| `first_30min_return` | Intraday Range Momentum | +1 | +0.0560 | +0.0077 | +0.0077 | +0.0592 | 1.38 | 1/8 | 5.90 | -3.05 | — | +0.0003 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.0673 | -0.0024 | -0.0024 | -0.6933 | 1.09 | 1/8 | 2.00 | 6.74 | — | +0.0002 | +0.0000 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0523 | +0.0203 | +0.0203 | +0.1467 | 0.65 | 1/8 | 0.64 | 1.19 | `smooth_momentum_structure` (0.77) | +0.0003 | +0.0000 |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0817 | -0.0364 | -0.0364 | -1.1617 | 0.73 | 1/8 | 0.68 | 1.70 | `volume_weighted_price_position` (1.11) | -0.0003 | +0.0000 |
| `always_in_trend_persistence` | Volatility & Oscillators | +1 | +0.0640 | -0.0421 | -0.0421 | -0.1859 | 0.92 | 2/8 | 1.78 | 4.11 | — | -0.0003 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0681 | +0.0530 | +0.0530 | +0.6589 | 0.82 | 2/8 | 0.96 | 1.47 | `bar_vol_0` (2.19) | +0.0005 | +0.0000 |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0912 | +0.0112 | +0.0112 | +0.1352 | 0.55 | 0/8 | 0.73 | 1.05 | `first_bar_sentiment` (0.69) | -0.0001 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1099, Sharpe: +0.7695)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | Intraday Range Momentum | +1 | +0.1174 | +0.0915 | +0.0915 | +0.4102 | 0.38 | 0/8 | 0.76 | 0.59 | `opening_drive_thrust_ratio` (0.40) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1302 | +0.0955 | +0.0955 | +0.5066 | 0.36 | 0/8 | 0.80 | 0.67 | `trend_bar_close_consistency` (0.66) | +0.0000 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1343 | +0.1127 | +0.1127 | +0.8107 | 0.39 | 0/8 | 0.69 | 0.51 | `star50_limit_proximity_early` (0.55) | +0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1304 | +0.0995 | +0.0995 | +0.1554 | 0.37 | 0/8 | 0.71 | 0.63 | `opening_drive_thrust_ratio` (0.40) | +0.0001 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1297 | +0.1084 | +0.1084 | +1.0418 | 0.28 | 0/8 | 0.88 | 0.58 | `rbreaker_sell_setup_proximity_early` (0.38) | +0.0007 | -0.0015 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1231 | +0.0586 | +0.0586 | -0.0789 | 0.35 | 0/8 | 0.74 | 0.67 | `bar_ret_0` (0.46) | -0.0001 | +0.0000 |
| `combo_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1192 | +0.0581 | +0.0581 | -0.3703 | 0.38 | 0/8 | 0.74 | 0.69 | `bar_ret_0` (0.46) | -0.0001 | +0.0000 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1202 | +0.0742 | +0.0742 | +0.1097 | 0.42 | 0/8 | 0.52 | 0.42 | `bar_ret_0` (0.46) | +0.0000 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1176 | +0.1023 | +0.1023 | +0.7538 | 0.29 | 0/8 | 0.79 | 0.71 | `rbreaker_sell_setup_proximity_early` (0.38) | +0.0001 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1412 | +0.1193 | +0.1193 | +0.5966 | 0.44 | 0/8 | 0.66 | 0.32 | `opening_drive_thrust_ratio` (0.40) | +0.0006 | -0.0015 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_day_regime_conviction` | Other Technical | +1 | +0.1367 | +0.1157 | +0.1157 | +0.6030 | 0.33 | 0/8 | 0.78 | 0.68 | `trend_day_regime_conviction` (0.46) | +0.0004 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1367 | +0.0949 | +0.0949 | +0.4145 | 0.34 | 0/8 | 0.77 | 0.59 | `opening_drive_thrust_ratio` (0.40) | -0.0000 | +0.0000 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1349 | +0.0747 | +0.0747 | +0.0706 | 0.35 | 0/8 | 0.70 | 0.51 | `body_size_progression` (0.60) | +0.0003 | +0.0000 |
| `combo_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1390 | +0.0842 | +0.0842 | +0.4912 | 0.34 | 0/8 | 0.71 | 0.55 | `body_size_progression` (0.60) | +0.0006 | -0.0218 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1433 | +0.0858 | +0.0858 | +0.9255 | 0.42 | 0/8 | 0.77 | 0.67 | `volume_weighted_momentum_acceleration` (0.62) | +0.0002 | +0.0000 |
| `combo_rank_max__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1349 | +0.0752 | +0.0752 | +0.1487 | 0.31 | 0/8 | 0.81 | 0.66 | `first_bar_return` (0.46) | -0.0000 | +0.0000 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1385 | +0.0855 | +0.0855 | +0.8416 | 0.33 | 0/8 | 0.72 | 0.58 | `body_size_progression` (0.60) | +0.0006 | -0.0218 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1289 | +0.1105 | +0.1105 | +0.9584 | 0.40 | 0/8 | 0.73 | 0.48 | `volatility_expansion_trend_vector` (0.41) | +0.0006 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1471 | +0.0937 | +0.0937 | -0.2836 | 0.34 | 0/8 | 0.79 | 0.59 | `opening_drive_thrust_ratio` (0.40) | +0.0001 | +0.0000 |
| `combo_max__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1073 | +0.0803 | +0.0803 | +0.5993 | 0.36 | 0/8 | 0.70 | 0.67 | `first_bar_sentiment` (0.43) | -0.0000 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1446 | +0.0905 | +0.0905 | +0.3245 | 0.41 | 0/8 | 0.63 | 0.53 | `first_bar_return` (0.46) | +0.0003 | +0.0000 |
| `combo_max__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1344 | +0.0749 | +0.0749 | +0.0494 | 0.33 | 0/8 | 0.82 | 0.66 | `first_bar_return` (0.46) | +0.0002 | +0.0000 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1496 | +0.0874 | +0.0874 | +0.8706 | 0.42 | 0/8 | 0.70 | 0.61 | `volume_weighted_momentum_acceleration` (0.62) | +0.0002 | -0.0218 |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1232 | +0.0841 | +0.0841 | +0.5556 | 0.32 | 0/8 | 0.86 | 0.70 | `volatility_expansion_trend_vector` (0.41) | +0.0000 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1022 | +0.0946 | +0.0946 | +0.4749 | 0.26 | 0/8 | 0.91 | 0.93 | `volume_weighted_momentum_acceleration` (0.62) | +0.0003 | +0.0000 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.0939 | +0.0890 | +0.0890 | +0.3159 | 0.37 | 0/8 | 0.71 | 0.70 | `close_vs_open_range` (0.42) | +0.0005 | +0.0000 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1239 | +0.0818 | +0.0818 | +0.0961 | 0.51 | 0/8 | 0.50 | 0.39 | `max_down_ret` (0.62) | +0.0003 | -0.0015 |
| `combo_mean__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1198 | +0.0871 | +0.0871 | +0.0841 | 0.36 | 0/8 | 0.64 | 0.63 | `first_bar_return` (0.46) | +0.0000 | +0.0000 |
| `combo_min__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.0954 | +0.0868 | +0.0868 | +0.2383 | 0.35 | 0/8 | 0.72 | 0.69 | `close_vs_open_range` (0.42) | +0.0004 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__early_body_momentum` | Intraday Range Momentum | +1 | +0.1212 | +0.0857 | +0.0857 | -0.2639 | 0.32 | 0/8 | 0.86 | 0.77 | `opening_drive_thrust_ratio` (0.40) | +0.0000 | +0.0000 |
| `combo_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1187 | +0.0735 | +0.0735 | +0.4772 | 0.39 | 0/8 | 0.80 | 0.83 | `early_body_momentum` (0.37) | +0.0002 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1162 | +0.1125 | +0.1125 | +1.2249 | 0.34 | 0/8 | 0.78 | 0.58 | `volatility_expansion_trend_vector` (0.41) | +0.0007 | +0.0028 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1327 | +0.0902 | +0.0902 | +0.1578 | 0.45 | 0/8 | 0.69 | 0.64 | `body_size_progression` (0.60) | +0.0003 | -0.0218 |
| `combo_min__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1045 | +0.0967 | +0.0967 | +0.4715 | 0.38 | 0/8 | 0.62 | 0.64 | `first_bar_return` (0.46) | +0.0004 | +0.0000 |
| `combo_mean__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1334 | +0.0784 | +0.0784 | +0.5697 | 0.34 | 0/8 | 0.68 | 0.66 | `first_bar_return` (0.46) | +0.0004 | -0.0015 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1003 | +0.0969 | +0.0969 | +0.9615 | 0.42 | 0/8 | 0.68 | 0.56 | `trend_bar_close_consistency` (0.66) | +0.0004 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1336 | +0.1052 | +0.1052 | +0.4780 | 0.31 | 0/8 | 0.75 | 0.62 | `rbreaker_sell_setup_proximity_early` (0.38) | +0.0000 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1016 | +0.1246 | +0.1246 | +1.3362 | 0.49 | 0/8 | 0.75 | 0.48 | `star50_limit_proximity_early` (0.55) | +0.0004 | +0.0348 |
| `combo_mean__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1215 | +0.0927 | +0.0927 | +0.2533 | 0.38 | 0/8 | 0.66 | 0.56 | `first_bar_return` (0.46) | +0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1218 | +0.0760 | +0.0760 | +0.3554 | 0.38 | 0/8 | 0.84 | 0.85 | `early_body_momentum` (0.37) | -0.0000 | +0.0000 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1351 | +0.0991 | +0.0991 | +0.4835 | 0.42 | 0/8 | 0.68 | 0.75 | `volume_weighted_momentum_acceleration` (0.62) | +0.0002 | +0.0000 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1350 | +0.0640 | +0.0640 | +0.0087 | 0.37 | 0/8 | 0.61 | 0.53 | `first_bar_sentiment` (0.43) | -0.0001 | +0.0000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1283 | +0.0889 | +0.0889 | +0.4004 | 0.45 | 0/8 | 0.70 | 0.67 | `volume_weighted_momentum_acceleration` (0.62) | +0.0003 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1165 | +0.0686 | +0.0686 | +0.2803 | 0.46 | 0/8 | 0.47 | 0.47 | — | +0.0004 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1378 | +0.0963 | +0.0963 | +0.3789 | 0.29 | 0/8 | 0.94 | 0.67 | `body_size_progression` (0.60) | +0.0002 | -0.0015 |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1012 | +0.0931 | +0.0931 | +0.2815 | 0.50 | 0/8 | 0.45 | 0.43 | `bar_ret_0` (0.46) | +0.0001 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1006 | +0.1182 | +0.1182 | +0.6219 | 0.42 | 0/8 | 0.68 | 0.48 | `star50_limit_proximity_early` (0.55) | +0.0004 | +0.0000 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1128 | +0.1133 | +0.1133 | +0.6694 | 0.35 | 0/8 | 0.70 | 0.50 | `star50_limit_proximity_early` (0.55) | +0.0004 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1502 | +0.1096 | +0.1096 | +0.7699 | 0.28 | 0/8 | 0.91 | 0.60 | `opening_drive_thrust_ratio` (0.40) | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1132 | +0.0802 | +0.0802 | +0.4497 | 0.22 | 0/8 | 0.88 | 0.88 | `volatility_expansion_trend_vector` (0.41) | +0.0000 | -0.0119 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1226 | +0.0881 | +0.0881 | +0.2537 | 0.31 | 0/8 | 0.90 | 0.82 | `volatility_expansion_trend_vector` (0.41) | -0.0000 | +0.0000 |
| `combo_mean__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1165 | +0.0686 | +0.0686 | +0.2803 | 0.46 | 0/8 | 0.47 | 0.47 | `bar_ret_0` (0.46) | +0.0001 | +0.0000 |
| `combo_rank_max__early_body_momentum__max_down_ret` | Intraday Range Momentum | +1 | +0.0929 | +0.0881 | +0.0881 | +0.3895 | 0.51 | 0/8 | 0.55 | 0.49 | `max_down_ret` (0.62) | +0.0003 | +0.0000 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1326 | +0.0856 | +0.0856 | +0.0926 | 0.30 | 0/8 | 0.78 | 0.62 | `first_bar_return` (0.46) | +0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1321 | +0.0880 | +0.0880 | -0.3280 | 0.33 | 0/8 | 0.72 | 0.61 | `first_bar_sentiment` (0.43) | +0.0001 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | Volatility & Oscillators | +1 | +0.1213 | +0.1215 | +0.1215 | +1.2167 | 0.37 | 0/8 | 0.75 | 0.47 | `rbreaker_sell_setup_proximity_early` (0.38) | +0.0004 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1211 | +0.0904 | +0.0904 | +0.2350 | 0.37 | 0/8 | 0.85 | 0.79 | `volatility_expansion_trend_vector` (0.41) | +0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1289 | +0.0905 | +0.0905 | +0.2004 | 0.50 | 0/8 | 0.50 | 0.41 | `bar_ret_0` (0.46) | +0.0005 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1242 | +0.0939 | +0.0939 | +0.9969 | 0.45 | 0/8 | 0.51 | 0.39 | `bar_ret_0` (0.46) | +0.0003 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1454 | +0.0885 | +0.0885 | +0.2644 | 0.35 | 0/8 | 0.74 | 0.61 | `bar_ret_0` (0.46) | +0.0003 | +0.0000 |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1220 | +0.0684 | +0.0684 | -0.4386 | 0.38 | 0/8 | 0.63 | 0.40 | `early_late_momentum_divergence` (0.60) | +0.0004 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1344 | +0.0919 | +0.0919 | +0.5194 | 0.35 | 0/8 | 0.68 | 0.59 | `first_bar_sentiment` (0.43) | +0.0001 | +0.0000 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1024 | +0.0969 | +0.0969 | +0.3003 | 0.46 | 0/8 | 0.66 | 0.51 | `max_down_ret` (0.62) | +0.0006 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1192 | +0.0774 | +0.0774 | +0.4480 | 0.44 | 0/8 | 0.75 | 0.70 | `opening_drive_thrust_ratio` (0.40) | +0.0002 | +0.0000 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1092 | +0.0916 | +0.0916 | +0.1735 | 0.30 | 0/8 | 0.73 | 0.62 | `first_bar_sentiment` (0.43) | -0.0002 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1389 | +0.0890 | +0.0890 | +0.2357 | 0.36 | 0/8 | 0.79 | 0.57 | `opening_drive_thrust_ratio` (0.40) | +0.0001 | +0.0000 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1489 | +0.0857 | +0.0857 | +0.4882 | 0.44 | 0/8 | 0.69 | 0.59 | `volume_weighted_momentum_acceleration` (0.62) | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1096 | +0.0933 | +0.0933 | +0.5076 | 0.31 | 0/8 | 0.79 | 0.69 | `net_volume_flow` (0.31) | +0.0001 | +0.0000 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1078 | +0.0961 | +0.0961 | +0.2697 | 0.49 | 0/8 | 0.68 | 0.51 | `max_down_ret` (0.62) | +0.0002 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1293 | +0.0813 | +0.0813 | +0.2357 | 0.30 | 0/8 | 0.93 | 0.64 | — | +0.0003 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1384 | +0.0962 | +0.0962 | +0.5296 | 0.40 | 0/8 | 0.76 | 0.57 | — | +0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1077 | +0.0778 | +0.0778 | +0.0854 | 0.31 | 0/8 | 0.89 | 0.80 | `close_vs_open_range` (0.42) | +0.0000 | +0.0000 |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1137 | +0.0835 | +0.0835 | +0.0570 | 0.39 | 0/8 | 0.52 | 0.41 | `first_bar_sentiment` (0.43) | +0.0000 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1277 | +0.1007 | +0.1007 | +0.6887 | 0.50 | 0/8 | 0.61 | 0.38 | `max_down_ret` (0.62) | +0.0002 | +0.0000 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1243 | +0.0922 | +0.0922 | +0.6593 | 0.50 | 0/8 | 0.51 | 0.39 | `max_down_ret` (0.62) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1223 | +0.0927 | +0.0927 | +0.9538 | 0.47 | 0/8 | 0.50 | 0.40 | `first_bar_return` (0.46) | +0.0010 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1035 | +0.0891 | +0.0891 | +0.9407 | 0.38 | 0/8 | 0.74 | 0.94 | `rbreaker_sell_setup_proximity_early` (0.38) | -0.0001 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1252 | +0.0607 | +0.0607 | +0.2343 | 0.39 | 0/8 | 0.84 | 0.79 | `volatility_expansion_trend_vector` (0.41) | +0.0002 | -0.0119 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1164 | +0.0946 | +0.0946 | +0.0682 | 0.39 | 0/8 | 0.78 | 0.63 | `close_vs_open_range` (0.42) | +0.0000 | +0.0000 |
| `combo_min__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1123 | +0.0885 | +0.0885 | +0.1705 | 0.27 | 0/8 | 1.04 | 0.85 | `volatility_expansion_trend_vector` (0.41) | +0.0002 | +0.0000 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1029 | +0.1235 | +0.1235 | +1.0733 | 0.46 | 0/8 | 0.69 | 0.50 | `star50_limit_proximity_early` (0.55) | +0.0008 | +0.0000 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1062 | +0.0775 | +0.0775 | +0.0450 | 0.29 | 0/8 | 0.78 | 0.83 | `first_bar_sentiment` (0.43) | -0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1181 | +0.0557 | +0.0557 | +0.2440 | 0.56 | 0/8 | 0.56 | 0.59 | `first_bar_return` (0.46) | +0.0002 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1106 | +0.0943 | +0.0943 | +0.6580 | 0.36 | 0/8 | 0.75 | 1.01 | `rbreaker_sell_setup_proximity_early` (0.38) | +0.0004 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0825 | +0.1093 | +0.1093 | +0.6791 | 0.66 | 0/8 | 0.55 | 0.37 | `max_down_ret` (0.62) | +0.0004 | +0.0000 |
| `combo_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1234 | +0.0811 | +0.0811 | +0.2357 | 0.45 | 0/8 | 0.77 | 0.69 | `first_bar_sentiment` (0.43) | +0.0001 | +0.0000 |
| `combo_max__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.0958 | +0.0913 | +0.0913 | -0.1427 | 0.47 | 0/8 | 0.53 | 0.42 | `max_down_ret` (0.62) | +0.0001 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1162 | +0.0877 | +0.0877 | +1.0117 | 0.47 | 0/8 | 0.69 | 0.57 | `late_bar_momentum` (0.60) | +0.0003 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1286 | +0.0668 | +0.0668 | -0.1367 | 0.40 | 0/8 | 1.05 | 0.86 | `opening_drive_thrust_ratio` (0.40) | +0.0002 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.0942 | +0.0934 | +0.0934 | +0.4700 | 0.40 | 0/8 | 0.78 | 0.71 | `smooth_momentum_structure` (0.62) | +0.0005 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1266 | +0.0998 | +0.0998 | +0.6467 | 0.42 | 0/8 | 0.82 | 0.54 | `close_vs_open_range` (0.42) | +0.0005 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1330 | +0.0898 | +0.0898 | +1.0714 | 0.42 | 0/8 | 0.85 | 0.75 | `smooth_momentum_structure` (0.62) | +0.0001 | +0.0000 |
| `combo_rank_max__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.0877 | +0.0793 | +0.0793 | +0.6809 | 0.38 | 0/8 | 0.90 | 0.79 | `close_vs_open_range` (0.42) | +0.0002 | +0.0000 |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0982 | +0.0816 | +0.0816 | +0.1952 | 0.41 | 0/8 | 0.76 | 0.75 | `trend_bar_close_consistency` (0.66) | +0.0003 | +0.0000 |
| `combo_min__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0937 | +0.1023 | +0.1023 | +0.4955 | 0.50 | 0/8 | 0.43 | 0.43 | `first_bar_return` (0.46) | +0.0002 | +0.0000 |
| `combo_min__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1034 | +0.1016 | +0.1016 | +0.5225 | 0.36 | 0/8 | 0.78 | 0.69 | `max_down_ret` (0.62) | +0.0007 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1104 | +0.1566 | +0.1566 | +0.5389 | 0.44 | 0/8 | 0.51 | 0.67 | `max_down_ret` (0.62) | +0.0005 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1192 | +0.1170 | +0.1170 | +1.0936 | 0.47 | 0/8 | 0.68 | 0.39 | `star50_limit_proximity_early` (0.55) | +0.0008 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1237 | +0.0540 | +0.0540 | -0.2136 | 0.36 | 0/8 | 0.88 | 0.83 | `close_vs_open_range` (0.42) | +0.0001 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0935 | +0.0994 | +0.0994 | +0.6418 | 0.55 | 0/8 | 0.57 | 0.40 | `max_down_ret` (0.62) | +0.0005 | +0.0348 |
| `open_to_current_return` | Intraday Range Momentum | +1 | +0.0975 | +0.0774 | +0.0774 | +0.5603 | 0.41 | 0/8 | 0.88 | 0.73 | — | +0.0002 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1228 | +0.1294 | +0.1294 | +1.0283 | 0.48 | 0/8 | 0.74 | 0.49 | `star50_limit_proximity_early` (0.55) | +0.0005 | +0.0348 |
| `combo_min__close_vs_open_range__max_down_ret` | Intraday Range Momentum | +1 | +0.0999 | +0.1016 | +0.1016 | +0.1701 | 0.48 | 0/8 | 0.71 | 0.56 | `max_down_ret` (0.62) | +0.0005 | +0.0000 |
| `combo_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1042 | +0.0977 | +0.0977 | +0.0827 | 0.28 | 0/8 | 1.09 | 0.73 | `close_vs_open_range` (0.42) | +0.0001 | +0.0000 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | Intraday Range Momentum | +1 | +0.0989 | +0.0770 | +0.0770 | +0.3299 | 0.21 | 0/8 | 1.13 | 1.23 | `body_size_progression` (0.60) | +0.0001 | +0.0000 |
| `combo_min__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1065 | +0.0905 | +0.0905 | +0.2175 | 0.38 | 0/8 | 0.55 | 0.43 | `max_down_ret` (0.62) | +0.0005 | +0.0000 |
| `combo_rank_max__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1302 | +0.0785 | +0.0785 | +0.5109 | 0.35 | 0/8 | 0.81 | 0.68 | `close_vs_open_range` (0.42) | -0.0001 | +0.0000 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.0836 | +0.0712 | +0.0712 | -0.3626 | 0.51 | 0/8 | 1.11 | 0.90 | — | +0.0003 | +0.0000 |
| `combo_min__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1109 | +0.0739 | +0.0739 | -0.4096 | 0.25 | 0/8 | 1.11 | 0.97 | `early_body_momentum` (0.37) | -0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1237 | +0.0836 | +0.0836 | -0.0273 | 0.52 | 0/8 | 0.46 | 0.40 | `bar_ret_0` (0.46) | -0.0001 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1274 | +0.1011 | +0.1011 | +0.3129 | 0.43 | 0/8 | 0.72 | 0.55 | `max_down_ret` (0.62) | +0.0005 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.0934 | +0.0994 | +0.0994 | +0.6449 | 0.54 | 0/8 | 0.65 | 0.48 | `smooth_momentum_structure` (0.62) | +0.0003 | +0.0000 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0914 | +0.1019 | +0.1019 | +0.5491 | 0.53 | 0/8 | 0.64 | 0.54 | `max_down_ret` (0.62) | +0.0009 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.0906 | +0.0840 | +0.0840 | +0.6564 | 0.50 | 0/8 | 0.86 | 1.16 | `trend_bar_close_consistency` (0.66) | +0.0002 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1124 | +0.0730 | +0.0730 | +0.1410 | 0.48 | 0/8 | 0.85 | 0.90 | `trend_bar_close_consistency` (0.66) | -0.0000 | +0.0000 |
| `early_body_momentum` | Intraday Range Momentum | +1 | +0.0818 | +0.0648 | +0.0648 | -0.2198 | 0.37 | 0/8 | 0.99 | 1.16 | — | +0.0001 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.0592 | +0.0705 | +0.0705 | +0.5535 | 0.93 | 1/8 | 0.63 | 0.79 | `volume_weighted_momentum_acceleration` (0.62) | +0.0001 | +0.0000 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1066 | +0.1033 | +0.1033 | +0.2208 | 0.38 | 0/8 | 0.73 | 0.89 | `star50_limit_proximity_early` (0.55) | +0.0003 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1257 | +0.0876 | +0.0876 | +0.6874 | 0.48 | 0/8 | 0.83 | 0.65 | `smooth_momentum_structure` (0.62) | +0.0001 | +0.0000 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1072 | +0.0595 | +0.0595 | +0.5616 | 0.31 | 0/8 | 0.85 | 0.82 | `first_bar_sentiment` (0.43) | +0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0965 | +0.1418 | +0.1418 | +1.1539 | 0.60 | 0/8 | 0.61 | 0.46 | `max_down_ret` (0.62) | +0.0005 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1229 | +0.1094 | +0.1094 | +0.5292 | 0.39 | 0/8 | 0.71 | 0.74 | `volatility_expansion_trend_vector` (0.41) | +0.0002 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1188 | +0.0579 | +0.0579 | +0.2946 | 0.44 | 0/8 | 0.92 | 0.68 | `trend_bar_close_consistency` (0.66) | +0.0001 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1064 | +0.0678 | +0.0678 | +0.0596 | 0.48 | 0/8 | 1.09 | 0.72 | `volume_weighted_momentum_acceleration` (0.62) | +0.0001 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1144 | +0.0794 | +0.0794 | +0.3571 | 0.29 | 0/8 | 0.70 | 0.84 | `first_bar_return` (0.46) | +0.0001 | +0.0348 |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1062 | +0.1124 | +0.1124 | +0.4201 | 0.49 | 0/8 | 0.65 | 0.58 | `star50_limit_proximity_early` (0.55) | +0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1096 | +0.0988 | +0.0988 | +0.3362 | 0.48 | 0/8 | 0.68 | 0.55 | `max_down_ret` (0.62) | +0.0003 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1003 | +0.1136 | +0.1136 | +0.5275 | 0.49 | 0/8 | 0.70 | 0.81 | `star50_limit_proximity_early` (0.55) | +0.0005 | +0.0000 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0958 | +0.0778 | +0.0778 | +0.6660 | 0.42 | 0/8 | 0.96 | 0.79 | — | +0.0003 | +0.0000 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1055 | +0.0934 | +0.0934 | +1.2539 | 0.49 | 0/8 | 0.64 | 0.35 | `volume_weighted_momentum_acceleration` (0.62) | +0.0003 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.0949 | +0.1236 | +0.1236 | -0.0797 | 0.46 | 0/8 | 0.88 | 0.84 | `body_size_progression` (0.60) | +0.0004 | +0.0000 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1000 | +0.1108 | +0.1108 | +0.2764 | 0.51 | 0/8 | 0.67 | 0.69 | `star50_limit_proximity_early` (0.55) | +0.0001 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.0944 | +0.1148 | +0.1148 | -0.0882 | 0.57 | 0/8 | 0.84 | 0.54 | `star50_limit_proximity_early` (0.55) | +0.0004 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1178 | +0.0883 | +0.0883 | +0.7016 | 0.46 | 0/8 | 0.79 | 0.60 | `trend_bar_close_consistency` (0.66) | -0.0002 | +0.0000 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1036 | +0.0828 | +0.0828 | +0.1020 | 0.38 | 0/8 | 0.61 | 0.44 | `first_bar_sentiment` (0.43) | -0.0001 | +0.0000 |
| `combo_min__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1164 | +0.0882 | +0.0882 | +0.3496 | 0.26 | 0/8 | 0.71 | 0.69 | `first_bar_sentiment` (0.43) | -0.0000 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1064 | +0.0815 | +0.0815 | +0.4854 | 0.58 | 1/8 | 0.91 | 0.79 | `volume_weighted_momentum_acceleration` (0.62) | +0.0000 | +0.0000 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0810 | +0.0431 | +0.0431 | -0.4332 | 0.68 | 1/8 | 1.29 | 4.35 | — | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1000 | +0.0826 | +0.0826 | +0.6025 | 0.42 | 0/8 | 0.69 | 0.52 | `trend_bar_close_consistency` (0.66) | +0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1032 | +0.0895 | +0.0895 | +0.9555 | 0.31 | 0/8 | 0.60 | 0.47 | `body_size_progression` (0.60) | +0.0004 | +0.0000 |
| `combo_diff__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.0701 | +0.0120 | +0.0120 | -0.8026 | 0.95 | 0/8 | 0.34 | 0.22 | `max_down_ret` (0.62) | -0.0001 | -0.1130 |
| `combo_max__trend_bar_close_consistency__max_down_ret` | Intraday Range Momentum | +1 | +0.0838 | +0.0635 | +0.0635 | +0.4032 | 0.62 | 0/8 | 0.87 | 0.66 | `trend_bar_close_consistency` (0.66) | +0.0002 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.0912 | +0.1529 | +0.1529 | +0.4587 | 0.72 | 1/8 | 0.54 | 0.41 | `volume_weighted_momentum_acceleration` (0.62) | +0.0005 | +0.0348 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__net_volume_flow` | Volatility & Oscillators | +1 | +0.0843 | +0.0762 | +0.0762 | +0.3899 | 0.35 | 0/8 | 1.17 | 1.08 | `rbreaker_sell_setup_proximity_early` (0.38) | +0.0003 | +0.0348 |
| `trend_strength_intraday` | Other Technical | +1 | +0.0822 | +0.0894 | +0.0894 | +0.1836 | 0.36 | 0/8 | 0.93 | 1.36 | — | +0.0001 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1364, Sharpe: +1.1795)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1401 | +0.1277 | +0.1277 | +1.2801 | 0.54 | 1/8 | 1.04 | 2.19 | `bar_body_rng_0` (0.54) | +0.0000 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1446 | +0.1235 | +0.1235 | +0.8704 | 0.52 | 1/8 | 1.10 | 2.97 | `bar_body_rng_0` (0.54) | -0.0002 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1417 | +0.1103 | +0.1103 | +1.0913 | 0.48 | 1/8 | 1.26 | 3.67 | `opening_drive_thrust_ratio` (0.53) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1429 | +0.1164 | +0.1164 | +1.2316 | 0.39 | 0/8 | 1.23 | 1.73 | `bar_body_rng_0` (0.54) | -0.0002 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1275 | +0.1267 | +0.1267 | +1.2245 | 0.39 | 0/8 | 1.38 | 2.86 | `star50_limit_proximity_early` (0.68) | -0.0000 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1404 | +0.1190 | +0.1190 | +1.6230 | 0.49 | 1/8 | 1.01 | 1.64 | `first_bar_sentiment` (0.76) | -0.0001 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1376 | +0.1248 | +0.1248 | +1.0992 | 0.52 | 1/8 | 1.14 | 2.47 | `bar_body_rng_0` (0.54) | -0.0002 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1364 | +0.1187 | +0.1187 | +0.9339 | 0.50 | 1/8 | 1.08 | 3.43 | `opening_drive_thrust_ratio` (0.53) | -0.0004 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1386 | +0.1258 | +0.1258 | +1.4182 | 0.48 | 0/8 | 1.17 | 3.10 | `opening_drive_thrust_ratio` (0.53) | +0.0003 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1163 | +0.0911 | +0.0911 | +0.5434 | 0.62 | 1/8 | 1.30 | 4.55 | `yesterday_early_vwap_dev` (1.10) | +0.0004 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1248 | +0.1283 | +0.1283 | +1.6959 | 0.57 | 1/8 | 1.04 | 1.71 | `volume_weighted_price_position` (0.77) | -0.0003 | -0.0833 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1284 | +0.1327 | +0.1327 | +0.9738 | 0.39 | 0/8 | 1.62 | 3.11 | `star50_limit_proximity_early` (0.68) | +0.0002 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1298 | +0.1068 | +0.1068 | +1.2738 | 0.56 | 1/8 | 1.02 | 2.80 | `first_bar_sentiment` (0.76) | -0.0003 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1058 | +0.1409 | +0.1409 | +1.7299 | 0.74 | 1/8 | 1.13 | 4.05 | `volume_weighted_price_position` (0.77) | -0.0003 | -0.0833 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1223 | +0.1211 | +0.1211 | +1.8009 | 0.69 | 1/8 | 1.00 | 2.95 | `first_bar_sentiment` (0.76) | -0.0004 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1289 | +0.1241 | +0.1241 | +1.6362 | 0.53 | 1/8 | 1.09 | 2.52 | `star50_limit_proximity_early` (0.68) | +0.0000 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1237 | +0.1316 | +0.1316 | +1.5821 | 0.59 | 0/8 | 0.94 | 1.51 | `volume_weighted_price_position` (0.77) | -0.0001 | -0.1186 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1154 | +0.1291 | +0.1291 | +1.1684 | 0.49 | 1/8 | 1.95 | 3.70 | `volatility_expansion_trend_vector` (0.74) | +0.0006 | +0.0000 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1252 | +0.0846 | +0.0846 | +0.2222 | 0.42 | 0/8 | 1.27 | 1.80 | `bar_body_rng_0` (0.54) | -0.0002 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1420 | +0.1262 | +0.1262 | +1.6796 | 0.43 | 0/8 | 1.09 | 1.90 | `bar_body_rng_0` (0.54) | -0.0002 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1308 | +0.1167 | +0.1167 | +1.0752 | 0.52 | 1/8 | 1.02 | 2.55 | `rbreaker_sell_setup_proximity_early` (0.43) | -0.0002 | +0.0000 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1215 | +0.1330 | +0.1330 | +1.4975 | 0.58 | 1/8 | 1.11 | 2.58 | `star50_limit_proximity_early` (0.68) | +0.0004 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1433 | +0.1191 | +0.1191 | +1.3989 | 0.41 | 0/8 | 1.44 | 2.17 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0001 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1144 | +0.0853 | +0.0853 | +0.3259 | 0.43 | 0/8 | 1.55 | 2.67 | `opening_drive_thrust_ratio` (0.53) | -0.0005 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1426 | +0.1231 | +0.1231 | +1.3859 | 0.38 | 0/8 | 1.34 | 1.76 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0003 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1127 | +0.1321 | +0.1321 | +1.4384 | 0.52 | 1/8 | 1.90 | 3.73 | `volatility_expansion_trend_vector` (0.74) | +0.0007 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1257 | +0.0989 | +0.0989 | +1.0037 | 0.59 | 1/8 | 0.84 | 1.33 | `first_bar_sentiment` (0.76) | -0.0006 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1374 | +0.1301 | +0.1301 | +1.0434 | 0.41 | 0/8 | 1.03 | 1.21 | `volume_weighted_price_position` (0.77) | -0.0001 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1290 | +0.0983 | +0.0983 | +1.4193 | 0.57 | 1/8 | 0.78 | 1.01 | `first_bar_sentiment` (0.76) | -0.0002 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1306 | +0.1191 | +0.1191 | +1.5664 | 0.45 | 0/8 | 1.14 | 2.90 | `star50_limit_proximity_early` (0.68) | -0.0003 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1225 | +0.1315 | +0.1315 | +1.4786 | 0.46 | 0/8 | 1.23 | 3.43 | `star50_limit_proximity_early` (0.68) | +0.0002 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1304 | +0.0976 | +0.0976 | +0.8959 | 0.37 | 0/8 | 1.37 | 1.88 | `star50_limit_proximity_early` (0.68) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1233 | +0.1118 | +0.1118 | +0.8851 | 0.44 | 0/8 | 1.87 | 2.88 | `opening_drive_thrust_ratio` (0.53) | -0.0003 | +0.0000 |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1210 | +0.0866 | +0.0866 | +0.0893 | 0.52 | 1/8 | 0.95 | 1.50 | `first_bar_sentiment` (0.76) | -0.0002 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1196 | +0.0759 | +0.0759 | +0.6053 | 0.43 | 0/8 | 0.98 | 1.91 | `first_bar_sentiment` (0.76) | -0.0007 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1169 | +0.0861 | +0.0861 | +0.4034 | 0.45 | 0/8 | 1.46 | 1.85 | `bar_body_rng_0` (0.54) | -0.0002 | -0.0127 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1151 | +0.1290 | +0.1290 | +1.5409 | 0.70 | 1/8 | 1.13 | 5.27 | `star50_limit_proximity_early` (0.68) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1114 | +0.0891 | +0.0891 | +0.8097 | 0.43 | 0/8 | 1.26 | 1.98 | `first_bar_sentiment` (0.76) | -0.0003 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0943 | +0.1204 | +0.1204 | +1.1103 | 0.81 | 2/8 | 1.49 | -9.71 | `rbreaker_buy_setup_proximity_early` (1.12) | +0.0001 | +0.0000 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1154 | +0.0702 | +0.0702 | +0.6069 | 0.43 | 0/8 | 0.88 | 1.29 | `first_bar_sentiment` (0.76) | -0.0004 | +0.0000 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0876 | +0.1119 | +0.1119 | +0.4883 | 0.81 | 1/8 | 1.67 | -68.28 | `yesterday_first_30min_return` (0.92) | +0.0003 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0880 | +0.1109 | +0.1109 | +0.3355 | 0.82 | 1/8 | 1.76 | -34.61 | `yesterday_first_30min_return` (0.92) | +0.0003 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1227 | +0.0781 | +0.0781 | +0.0786 | 0.42 | 0/8 | 1.43 | 2.01 | `opening_drive_thrust_ratio` (0.53) | -0.0003 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1114 | +0.1247 | +0.1247 | +1.4204 | 0.66 | 1/8 | 1.08 | 4.36 | `star50_limit_proximity_early` (0.68) | -0.0004 | +0.0000 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1141 | +0.0985 | +0.0985 | +0.8687 | 0.52 | 0/8 | 2.01 | 5.46 | `demark_setup_reversal_early` (0.76) | -0.0003 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Other Technical | +1 | +0.1027 | +0.1270 | +0.1270 | +0.8942 | 0.73 | 1/8 | 1.27 | 48.39 | `limit_down_proximity_early` (1.12) | +0.0003 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1133 | +0.1244 | +0.1244 | +0.2717 | 0.38 | 0/8 | 1.65 | 2.48 | `opening_drive_thrust_ratio` (0.53) | -0.0005 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1211 | +0.0922 | +0.0922 | -0.0879 | 0.46 | 0/8 | 1.26 | 2.77 | `bar_body_rng_0` (0.54) | -0.0007 | -0.0196 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1024 | +0.1088 | +0.1088 | +0.4427 | 0.72 | 1/8 | 1.83 | 5.08 | `yesterday_early_vwap_dev` (1.10) | +0.0001 | -0.0401 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1285 | +0.1028 | +0.1028 | +1.0956 | 0.39 | 0/8 | 1.38 | 1.93 | `star50_limit_proximity_early` (0.68) | -0.0001 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1233 | +0.1026 | +0.1026 | +0.2266 | 0.32 | 0/8 | 1.49 | 1.85 | `opening_drive_thrust_ratio` (0.53) | -0.0004 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1146 | +0.1250 | +0.1250 | +1.0832 | 0.41 | 0/8 | 2.08 | 3.62 | `impulse_bar_dominance` (1.04) | +0.0004 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1182 | +0.1236 | +0.1236 | +0.8328 | 0.37 | 0/8 | 1.49 | 2.06 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0005 | -0.0016 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1000 | +0.1399 | +0.1399 | +1.6539 | 0.82 | 1/8 | 1.11 | 12.14 | `limit_down_proximity_early` (1.12) | +0.0004 | +0.0000 |
| `combo_tri_max__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0973 | +0.1054 | +0.1054 | +0.5945 | 0.60 | 1/8 | 1.45 | 2.92 | `yesterday_early_momentum` (1.06) | +0.0002 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1019 | +0.1284 | +0.1284 | +1.2074 | 0.40 | 0/8 | 1.61 | 2.48 | `impulse_bar_dominance` (1.04) | +0.0008 | +0.0000 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1165 | +0.0874 | +0.0874 | +0.4131 | 0.38 | 0/8 | 1.69 | 2.54 | `star50_limit_proximity_early` (0.68) | -0.0004 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1341 | +0.1084 | +0.1084 | +0.1964 | 0.30 | 0/8 | 1.32 | 1.43 | `rbreaker_sell_setup_proximity_early` (0.43) | -0.0001 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1172 | +0.0834 | +0.0834 | +0.2125 | 0.49 | 0/8 | 1.39 | 2.63 | `first_bar_sentiment` (0.76) | -0.0004 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1074 | +0.1005 | +0.1005 | +0.4995 | 0.74 | 1/8 | 1.24 | 5.28 | `yesterday_early_vwap_dev` (1.10) | +0.0002 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0942 | +0.1242 | +0.1242 | +0.6361 | 0.62 | 1/8 | 1.59 | 4.28 | `yesterday_first_30min_return` (0.92) | +0.0003 | -0.0940 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1326 | +0.1230 | +0.1230 | +1.4125 | 0.36 | 0/8 | 1.38 | 1.64 | `first_bar_sentiment` (0.76) | -0.0001 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1336 | +0.1099 | +0.1099 | +0.2013 | 0.30 | 0/8 | 1.37 | 1.53 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0003 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1155 | +0.0909 | +0.0909 | +0.8829 | 0.52 | 0/8 | 1.08 | 1.69 | `bar_body_rng_0` (0.54) | -0.0005 | +0.0000 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0822 | +0.0966 | +0.0966 | +0.6825 | 0.69 | 0/8 | 3.54 | 6.25 | `volatility_expansion_trend_vector` (0.74) | -0.0002 | -0.0196 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1142 | +0.1088 | +0.1088 | +0.9171 | 0.51 | 0/8 | 1.87 | 4.15 | `demark_setup_reversal_early` (0.76) | +0.0002 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1245 | +0.1249 | +0.1249 | +1.2583 | 0.46 | 0/8 | 1.23 | 2.00 | `bar_body_rng_0` (0.54) | -0.0003 | +0.0000 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1228 | +0.1018 | +0.1018 | +0.4840 | 0.40 | 0/8 | 0.85 | 1.16 | `first_bar_sentiment` (0.76) | +0.0001 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1371 | +0.1056 | +0.1056 | +0.1964 | 0.33 | 0/8 | 1.15 | 1.33 | `first_bar_sentiment` (0.76) | -0.0001 | +0.0000 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1221 | +0.1093 | +0.1093 | +0.9727 | 0.46 | 0/8 | 1.30 | 3.22 | `demark_setup_reversal_early` (0.76) | -0.0003 | +0.0000 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1194 | +0.1062 | +0.1062 | +1.1247 | 0.47 | 0/8 | 1.52 | 4.78 | `demark_setup_reversal_early` (0.76) | -0.0004 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1123 | +0.0765 | +0.0765 | +0.2136 | 0.38 | 0/8 | 2.01 | 2.24 | — | -0.0004 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1014 | +0.1330 | +0.1330 | +1.0200 | 0.78 | 1/8 | 1.49 | 10.17 | `yesterday_first_30min_return` (0.92) | +0.0004 | +0.0000 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1094 | +0.0964 | +0.0964 | +0.0936 | 0.48 | 0/8 | 2.26 | 3.83 | `star50_limit_proximity_early` (0.68) | +0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1219 | +0.0954 | +0.0954 | +1.4524 | 0.63 | 1/8 | 0.85 | 1.33 | `first_bar_sentiment` (0.76) | -0.0007 | +0.0000 |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.0816 | +0.0702 | +0.0702 | +0.3954 | 0.63 | 0/8 | 3.42 | 4.61 | `impulse_bar_dominance` (1.04) | -0.0001 | -0.0401 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0974 | +0.1273 | +0.1273 | +0.3112 | 0.43 | 0/8 | 2.10 | 3.36 | `volatility_expansion_trend_vector` (0.74) | -0.0000 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1146 | +0.0866 | +0.0866 | +0.4183 | 0.48 | 0/8 | 1.91 | 2.92 | `opening_drive_thrust_ratio` (0.53) | -0.0003 | -0.0196 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1172 | +0.0926 | +0.0926 | +0.6024 | 0.38 | 0/8 | 1.12 | 2.11 | `opening_drive_thrust_ratio` (0.53) | -0.0008 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1018 | +0.1385 | +0.1385 | +1.1011 | 0.47 | 0/8 | 1.80 | 4.33 | `volatility_expansion_trend_vector` (0.74) | +0.0003 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1225 | +0.1267 | +0.1267 | +0.4263 | 0.54 | 1/8 | 1.18 | 1.70 | `first_bar_sentiment` (0.76) | +0.0002 | +0.0000 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0757 | +0.1167 | +0.1167 | +0.9419 | 0.75 | 0/8 | 2.18 | 15.45 | `limit_down_proximity_early` (1.12) | +0.0004 | +0.0000 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1153 | +0.0831 | +0.0831 | +0.6530 | 0.44 | 0/8 | 1.52 | 2.62 | `first_bar_sentiment` (0.76) | -0.0004 | +0.0000 |
| `combo_max__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.0929 | +0.0673 | +0.0673 | +0.2240 | 0.47 | 0/8 | 2.90 | 3.31 | `impulse_bar_dominance` (1.04) | +0.0001 | -0.0127 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0916 | +0.1042 | +0.1042 | +1.2122 | 0.53 | 0/8 | 1.46 | 4.49 | `rbreaker_buy_setup_proximity_early` (1.12) | -0.0003 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1011 | +0.0961 | +0.0961 | +0.5743 | 0.53 | 0/8 | 1.73 | 3.52 | `volatility_expansion_trend_vector` (0.74) | -0.0002 | +0.0000 |
| `combo_min__first_bar_return__limit_down_proximity_early` | Gap / Overnight Reversal | +1 | +0.0947 | +0.1269 | +0.1269 | +1.4730 | 0.78 | 1/8 | 1.02 | 6.36 | `limit_down_proximity_early` (1.12) | +0.0001 | +0.0000 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1108 | +0.1109 | +0.1109 | +0.9996 | 0.59 | 0/8 | 1.70 | 11.98 | `demark_setup_reversal_early` (0.76) | -0.0002 | +0.0000 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0859 | +0.0677 | +0.0677 | -0.1117 | 0.63 | 0/8 | 1.66 | 3.03 | `volume_weighted_price_position` (0.77) | -0.0006 | -0.0833 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1202 | +0.1214 | +0.1214 | +0.9475 | 0.46 | 0/8 | 0.99 | 1.56 | `first_bar_sentiment` (0.76) | -0.0002 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0822 | +0.0987 | +0.0987 | +0.6482 | 0.71 | 0/8 | 2.37 | 8.28 | `volatility_expansion_trend_vector` (0.74) | -0.0007 | +0.0000 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1192 | +0.0810 | +0.0810 | +0.8246 | 0.39 | 0/8 | 1.31 | 1.96 | `bar_body_rng_0` (0.54) | -0.0002 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1021 | +0.0789 | +0.0789 | +0.4086 | 0.45 | 0/8 | 1.23 | 2.17 | `opening_drive_thrust_ratio` (0.53) | -0.0005 | +0.0000 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1029 | +0.0988 | +0.0988 | +0.3616 | 0.50 | 0/8 | 1.54 | 2.67 | `volatility_expansion_trend_vector` (0.74) | -0.0002 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1016 | +0.1298 | +0.1298 | +0.0321 | 0.69 | 2/8 | 1.97 | -14.53 | `demark_setup_reversal_early` (0.76) | +0.0003 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0883 | +0.0941 | +0.0941 | +0.8986 | 0.62 | 0/8 | 2.23 | 3.60 | `impulse_bar_dominance` (1.04) | +0.0006 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1062 | +0.0919 | +0.0919 | +0.4669 | 0.53 | 0/8 | 1.41 | 3.77 | — | -0.0007 | +0.0000 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.0864 | +0.0944 | +0.0944 | +0.4751 | 0.57 | 0/8 | 1.37 | 2.79 | `volatility_expansion_trend_vector` (0.74) | -0.0003 | +0.0000 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.1103 | +0.0856 | +0.0856 | +0.3018 | 0.37 | 0/8 | 1.77 | 1.83 | `volatility_expansion_trend_vector` (0.74) | -0.0003 | +0.0000 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1031 | +0.0770 | +0.0770 | +0.0324 | 0.46 | 0/8 | 2.11 | 2.69 | `volatility_expansion_trend_vector` (0.74) | -0.0004 | +0.0000 |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1100 | +0.0792 | +0.0792 | +0.7948 | 0.41 | 0/8 | 1.23 | 2.25 | `rbreaker_buy_setup_proximity_early` (1.12) | -0.0002 | +0.0000 |
| `combo_z_sum__limit_down_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1040 | +0.1254 | +0.1254 | +1.0792 | 0.64 | 0/8 | 0.85 | 1.62 | `limit_down_proximity_early` (1.12) | -0.0001 | +0.0000 |
| `combo_max__yesterday_first_30min_return__limit_down_proximity_early` | Intraday Range Momentum | +1 | +0.0798 | +0.0974 | +0.0974 | +0.4494 | 0.74 | 1/8 | 1.32 | 6.94 | `limit_down_proximity_early` (1.12) | +0.0002 | +0.0000 |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0938 | +0.0898 | +0.0898 | +0.1198 | 0.90 | 1/8 | 1.25 | 5.52 | `yesterday_early_vwap_dev` (1.10) | -0.0000 | -0.0401 |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1152 | +0.0818 | +0.0818 | +0.4668 | 0.49 | 0/8 | 1.15 | 2.32 | `first_bar_sentiment` (0.76) | -0.0004 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0727 | +0.0258 | +0.0258 | +0.0683 | 0.28 | 0/8 | 1.63 | 1.21 | `rbreaker_buy_setup_proximity_early` (1.12) | -0.0002 | +0.0000 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1139 | +0.0883 | +0.0883 | +0.8073 | 0.52 | 0/8 | 1.27 | 1.44 | `volume_weighted_price_position` (0.77) | -0.0005 | -0.0401 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1072 | +0.0890 | +0.0890 | +0.3617 | 0.55 | 0/8 | 1.07 | 2.10 | `first_bar_sentiment` (0.76) | -0.0002 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.0770 | +0.0976 | +0.0976 | -0.0344 | 0.75 | 1/8 | 2.23 | 6.70 | — | -0.0002 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | Other Technical | +1 | +0.0917 | +0.0659 | +0.0659 | +0.5416 | 0.59 | 0/8 | 2.24 | 6.60 | `impulse_bar_dominance` (1.04) | -0.0003 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Other Technical | +1 | +0.0745 | +0.0196 | +0.0196 | +0.3480 | 0.42 | 0/8 | 1.36 | 1.18 | `limit_down_proximity_early` (1.12) | -0.0004 | +0.0000 |
| `combo_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Other Technical | +1 | +0.0745 | +0.0200 | +0.0200 | +0.3480 | 0.42 | 0/8 | 1.36 | 1.19 | `limit_down_proximity_early` (1.12) | -0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0818 | +0.1188 | +0.1188 | +0.0236 | 0.73 | 1/8 | 2.85 | 6.13 | `volatility_expansion_trend_vector` (0.74) | +0.0001 | +0.0000 |
| `close_vs_open_range` | Other Technical | +1 | +0.0638 | +0.1017 | +0.1017 | +0.6838 | 0.72 | 0/8 | 3.56 | 3.79 | — | -0.0000 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1170 | +0.0706 | +0.0706 | +0.8068 | 0.42 | 0/8 | 0.93 | 1.22 | — | -0.0005 | +0.0000 |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0856 | +0.0925 | +0.0925 | +0.5763 | 0.76 | 0/8 | 1.84 | 2.65 | `volume_weighted_price_position` (0.77) | -0.0003 | +0.0000 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0672 | -0.0273 | -0.0273 | +0.1690 | 0.52 | 0/8 | 0.75 | 0.64 | `volatility_expansion_trend_vector` (0.74) | -0.0006 | +0.0000 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 28.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3465_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1049 | 30 | 80.0% | 40.0% | +0.0135 | -0.0770 |
| B2 Rolling Guard | 123 | 30 | 90.0% | 26.7% | +0.0123 | -0.1601 |
| BH-FDR Gate | 11 | 11 | 27.3% | 9.1% | -0.0111 | -0.6346 |
| B3 Composite Floor | 2 | 2 | 100.0% | 0.0% | +0.0102 | -0.3704 |
| B4 Correlation Gate | 146 | 30 | 86.7% | 46.7% | +0.0154 | -0.0248 |

**Admitted Pool Summary**: 80 features, False Positive Rate = 52.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0161, Mean Lock Sharpe = -0.0138

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1884, Lock IC=+0.0396, Lock Sharpe=+1.1659
- `combo_z_sum__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1884, Lock IC=+0.0396, Lock Sharpe=+1.1659
- `combo_rank_max__bar_ret_0__volume_surge_direction`: Train IC=+0.1903, Lock IC=+0.0333, Lock Sharpe=+1.1576
- `combo_rank_max__first_bar_return__volume_surge_direction`: Train IC=+0.1902, Lock IC=+0.0333, Lock Sharpe=+1.1576
- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Lock Sharpe=+0.5188

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1676, Lock IC=+0.0217, Lock Sharpe=+0.2437
- `combo_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1674, Lock IC=+0.0242, Lock Sharpe=+0.1912
- `combo_z_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1674, Lock IC=+0.0242, Lock Sharpe=+0.1912
- `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`: Train IC=+0.1707, Lock IC=+0.0091, Lock Sharpe=+0.1498
- `combo_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1719, Lock IC=+0.0140, Lock Sharpe=+0.1415

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Lock Sharpe=+0.1611

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2291, Lock IC=+0.0645, Lock Sharpe=+0.9458
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Lock Sharpe=+0.5172
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2341, Lock IC=+0.0362, Lock Sharpe=+0.3660
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2341, Lock IC=+0.0362, Lock Sharpe=+0.3660
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2338, Lock IC=+0.0362, Lock Sharpe=+0.3660

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 38.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5346_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 528 | 30 | 83.3% | 26.7% | +0.0227 | -0.2260 |
| B2 Rolling Guard | 48 | 30 | 20.0% | 6.7% | -0.0071 | -0.4064 |
| BH-FDR Gate | 10 | 10 | 40.0% | 0.0% | -0.0141 | -0.5828 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__willr14__sma100_dist`: Train IC=+0.1249, Lock IC=+0.0527, Lock Sharpe=+0.6597
- `combo_sig_product__donchian_breakout_ratio_20d__sma100_dist`: Train IC=+0.1221, Lock IC=+0.0363, Lock Sharpe=+0.3227
- `combo_sig_product__donchian_breakout_proximity_20d__sma100_dist`: Train IC=+0.1221, Lock IC=+0.0363, Lock Sharpe=+0.3227
- `bar_rng_0`: Train IC=+0.0996, Lock IC=+0.0131, Lock Sharpe=+0.2514
- `combo_min__sma100_dist__wavetrend_osc_day`: Train IC=+0.1061, Lock IC=+0.0346, Lock Sharpe=+0.2110

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__roc60__wavetrend_osc_day`: Train IC=+0.0642, Lock IC=+0.0295, Lock Sharpe=+0.2578
- `combo_min__roc60__yesterday_wavetrend_osc`: Train IC=+0.0642, Lock IC=+0.0295, Lock Sharpe=+0.2578

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5090_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 70.0% | 30.0% | +0.0073 | -0.3172 |
| B2 Rolling Guard | 62 | 30 | 40.0% | 6.7% | -0.0025 | -0.6486 |
| BH-FDR Gate | 7 | 7 | 85.7% | 14.3% | +0.0353 | -0.1555 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1333, Lock IC=+0.0340, Lock Sharpe=+0.5556
- `early_vwap_acceleration`: Train IC=+0.1442, Lock IC=+0.0189, Lock Sharpe=+0.4977
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1373, Lock IC=+0.0627, Lock Sharpe=+0.4572
- `yesterday_body_ratio`: Train IC=+0.1295, Lock IC=+0.0571, Lock Sharpe=+0.4507
- `limit_down_proximity_early`: Train IC=+0.1106, Lock IC=+0.0570, Lock Sharpe=+0.4461

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0750, Lock IC=+0.0665, Lock Sharpe=+0.4292
- `combo_sig_product__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0510, Lock IC=+0.0272, Lock Sharpe=+0.2801

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1580, Lock IC=+0.0543, Lock Sharpe=+0.5842

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 69.0% lock IC > 0, 27.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3057_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 902 | 30 | 96.7% | 60.0% | +0.0436 | +0.1673 |
| B2 Rolling Guard | 40 | 30 | 43.3% | 10.0% | -0.0072 | -0.6304 |
| BH-FDR Gate | 3 | 3 | 33.3% | 0.0% | -0.0180 | -0.5838 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__roc60__wavetrend_osc_day`: Train IC=+0.1330, Lock IC=+0.0470, Lock Sharpe=+0.9851
- `combo_min__iv_corridor_width__wavetrend_osc_day`: Train IC=+0.1441, Lock IC=+0.0566, Lock Sharpe=+0.8007
- `combo_max__bar_vol_4__rsi21`: Train IC=+0.1324, Lock IC=+0.0699, Lock Sharpe=+0.7614
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.1278, Lock IC=+0.0492, Lock Sharpe=+0.7197
- `combo_mean__bar_vol_4__bar_vol_0`: Train IC=+0.1278, Lock IC=+0.0443, Lock Sharpe=+0.5812

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__bar_vol_4__bar_vol_0`: Train IC=+0.1157, Lock IC=+0.0211, Lock Sharpe=+0.1892
- `combo_product__bar_vol_4__first_bar_volume`: Train IC=+0.1157, Lock IC=+0.0211, Lock Sharpe=+0.1892
- `vix_iv_ratio`: Train IC=+0.0824, Lock IC=+0.0464, Lock Sharpe=+0.0580

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 7.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5980_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 325 | 30 | 63.3% | 16.7% | +0.0135 | -0.7170 |
| B2 Rolling Guard | 35 | 30 | 33.3% | 0.0% | -0.0059 | -0.5010 |
| BH-FDR Gate | 8 | 8 | 12.5% | 0.0% | -0.0226 | -1.3760 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.0929, Lock IC=+0.0849, Lock Sharpe=+0.7485
- `combo_sig_product__yesterday_wavetrend_osc__donchian_breakout_ratio_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034
- `combo_sig_product__yesterday_wavetrend_osc__donchian_breakout_proximity_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034
- `combo_sig_product__wavetrend_osc_day__donchian_breakout_ratio_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034
- `combo_sig_product__wavetrend_osc_day__donchian_breakout_proximity_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5499_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 275 | 30 | 73.3% | 40.0% | +0.0304 | -0.1383 |
| B2 Rolling Guard | 42 | 30 | 33.3% | 6.7% | -0.0001 | -0.4341 |
| BH-FDR Gate | 4 | 4 | 0.0% | 0.0% | -0.0376 | -0.4551 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.7549
- `limit_down_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.7549
- `gap_pct`: Train IC=+0.1134, Lock IC=+0.0703, Lock Sharpe=+0.5557
- `sma200_dist`: Train IC=+0.1275, Lock IC=+0.0508, Lock Sharpe=+0.5161
- `combo_mean__bar_vol_4__mfi14`: Train IC=+0.1427, Lock IC=+0.0752, Lock Sharpe=+0.4001

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `close_vs_open_range`: Train IC=+0.0929, Lock IC=+0.0458, Lock Sharpe=+0.4047
- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0445, Lock Sharpe=+0.0389

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 78.0% lock IC > 0, 50.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0827_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1791 | 30 | 96.7% | 93.3% | +0.0964 | +0.5995 |
| B2 Rolling Guard | 347 | 30 | 100.0% | 90.0% | +0.0824 | +0.4802 |
| BH-FDR Gate | 6 | 6 | 83.3% | 0.0% | +0.0160 | -0.4326 |
| B3 Composite Floor | 6 | 6 | 100.0% | 100.0% | +0.0476 | +0.2939 |
| B4 Correlation Gate | 575 | 30 | 100.0% | 100.0% | +0.1004 | +0.5636 |

**Admitted Pool Summary**: 146 features, False Positive Rate = 11.6% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0902, Mean Lock Sharpe = +0.4012

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Lock Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Lock Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Lock Sharpe=+1.1505
- `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2142, Lock IC=+0.1160, Lock Sharpe=+1.1034
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2618, Lock IC=+0.1189, Lock Sharpe=+1.0221

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Lock Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Lock Sharpe=+1.2071
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Lock Sharpe=+1.1213
- `combo_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.1870, Lock IC=+0.1042, Lock Sharpe=+1.0918
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Lock Sharpe=+0.7913

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Lock Sharpe=+0.5788
- `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1912, Lock IC=+0.0954, Lock Sharpe=+0.5787
- `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression`: Train IC=+0.1969, Lock IC=+0.0548, Lock Sharpe=+0.2617
- `combo_tri_min__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1666, Lock IC=+0.0188, Lock Sharpe=+0.1635
- `combo_tri_max__max_up_ret__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.1667, Lock IC=+0.0128, Lock Sharpe=+0.0903

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.2594, Lock IC=+0.1176, Lock Sharpe=+1.2041
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2594, Lock IC=+0.1176, Lock Sharpe=+1.2041
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2670, Lock IC=+0.1103, Lock Sharpe=+1.1260
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.2777, Lock IC=+0.1084, Lock Sharpe=+1.0418
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2538, Lock IC=+0.1120, Lock Sharpe=+0.8451

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 67.0% lock IC > 0, 22.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2720_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1254 | 30 | 50.0% | 33.3% | +0.0259 | -0.1255 |
| B2 Rolling Guard | 59 | 30 | 83.3% | 10.0% | +0.0360 | -0.3263 |
| BH-FDR Gate | 35 | 30 | 33.3% | 16.7% | -0.0069 | -0.2579 |
| B3 Composite Floor | 2 | 2 | 100.0% | 100.0% | +0.1070 | +0.4649 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_return`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.4456
- `bar_ret_0`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.4456
- `combo_mean__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.3726
- `combo_z_sum__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.3726
- `combo_mean__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.3726

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__false_breakout_accumulation__consecutive_higher_highs`: Train IC=+0.0610, Lock IC=+0.0411, Lock Sharpe=+0.3851
- `combo_rel_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.0419, Lock IC=+0.0139, Lock Sharpe=+0.1319
- `combo_rel_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.0419, Lock IC=+0.0139, Lock Sharpe=+0.1319

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1051, Lock IC=+0.1561, Lock Sharpe=+1.1881
- `combo_abs_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.0894, Lock IC=+0.0391, Lock Sharpe=+0.8542
- `combo_abs_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.0894, Lock IC=+0.0391, Lock Sharpe=+0.8542
- `volatility_expansion_trend_vector`: Train IC=+0.0806, Lock IC=+0.0873, Lock Sharpe=+0.2303
- `combo_min__early_body_momentum__morning_trend_extrapolated`: Train IC=+0.0765, Lock IC=+0.0612, Lock Sharpe=+0.0227

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_trend_extrapolated`: Train IC=+0.2095, Lock IC=+0.1061, Lock Sharpe=+0.5616
- `combo_rank_min__star50_limit_proximity_early__morning_trend_extrapolated`: Train IC=+0.2432, Lock IC=+0.1079, Lock Sharpe=+0.3682

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2789_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 377 | 30 | 50.0% | 30.0% | +0.0159 | -0.1880 |
| B2 Rolling Guard | 43 | 30 | 50.0% | 16.7% | +0.0021 | -0.1277 |
| BH-FDR Gate | 8 | 8 | 87.5% | 75.0% | +0.0758 | +0.1756 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1538, Lock IC=+0.1176, Lock Sharpe=+1.0733
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1538, Lock IC=+0.1176, Lock Sharpe=+1.0733
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1202, Lock IC=+0.1196, Lock Sharpe=+0.9515
- `consecutive_trend_bar_intensity`: Train IC=+0.1062, Lock IC=+0.0852, Lock Sharpe=+0.8713
- `combo_min__body_to_range_ratio__net_volume_flow`: Train IC=+0.1316, Lock IC=+0.0829, Lock Sharpe=+0.4421

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv_diff_1d`: Train IC=+0.0831, Lock IC=+0.0677, Lock Sharpe=+0.8717
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0644, Lock Sharpe=+0.4764
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0278, Lock Sharpe=+0.3337
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0694, Lock Sharpe=+0.3203
- `micro_gap_trend_continuation`: Train IC=+0.0587, Lock IC=+0.0708, Lock Sharpe=+0.0776

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1694, Lock IC=+0.1248, Lock Sharpe=+1.0490
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1694, Lock IC=+0.1248, Lock Sharpe=+1.0490
- `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1416, Lock IC=+0.0921, Lock Sharpe=+0.3653
- `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1416, Lock IC=+0.0921, Lock Sharpe=+0.3653
- `combo_ifelse__gap_pct__yesterday_early_vwap_dev__net_volume_flow`: Train IC=+0.1503, Lock IC=+0.0875, Lock Sharpe=+0.0257

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 59.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.2275_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1161 | 30 | 93.3% | 80.0% | +0.0930 | +0.4916 |
| B2 Rolling Guard | 229 | 30 | 100.0% | 100.0% | +0.0981 | +0.6425 |
| BH-FDR Gate | 7 | 7 | 100.0% | 71.4% | +0.0713 | +0.1712 |
| B3 Composite Floor | 78 | 30 | 100.0% | 100.0% | +0.0885 | +0.5932 |
| B4 Correlation Gate | 231 | 30 | 100.0% | 100.0% | +0.1205 | +1.3428 |

**Admitted Pool Summary**: 118 features, False Positive Rate = 3.4% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1036, Mean Lock Sharpe = +0.8026

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Lock Sharpe=+1.4951
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Lock Sharpe=+1.4951
- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.1924, Lock IC=+0.1128, Lock Sharpe=+1.2866
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Lock Sharpe=+1.0349
- `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Lock Sharpe=+1.0349

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Lock Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Lock Sharpe=+1.3322
- `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.1883, Lock IC=+0.1273, Lock Sharpe=+1.0683
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.1883, Lock IC=+0.1273, Lock Sharpe=+1.0683
- `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.1833, Lock IC=+0.1115, Lock Sharpe=+0.9311

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__volume_weighted_price_position__impulse_bar_dominance`: Train IC=+0.0973, Lock IC=+0.0572, Lock Sharpe=+0.5988
- `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance`: Train IC=+0.0986, Lock IC=+0.0840, Lock Sharpe=+0.3214
- `combo_rank_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.0986, Lock IC=+0.0840, Lock Sharpe=+0.3214
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0763, Lock IC=+0.1143, Lock Sharpe=+0.2104
- `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector`: Train IC=+0.0869, Lock IC=+0.0809, Lock Sharpe=+0.1650

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2047, Lock IC=+0.1185, Lock Sharpe=+1.3299
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2019, Lock IC=+0.1192, Lock Sharpe=+1.1310
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2110, Lock IC=+0.0899, Lock Sharpe=+1.0542
- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.1928, Lock IC=+0.0882, Lock Sharpe=+0.9124
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2273, Lock IC=+0.1072, Lock Sharpe=+0.9076

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Lock Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Lock Sharpe=+1.8009
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2614, Lock IC=+0.1262, Lock Sharpe=+1.6796
- `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2583, Lock IC=+0.1241, Lock Sharpe=+1.6362
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2626, Lock IC=+0.1190, Lock Sharpe=+1.6230

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 53.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0833_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 906 | 30 | 96.7% | 76.7% | +0.0802 | +0.3278 |
| B2 Rolling Guard | 84 | 30 | 96.7% | 86.7% | +0.1005 | +0.6794 |
| BH-FDR Gate | 119 | 30 | 100.0% | 93.3% | +0.1014 | +0.6624 |
| B3 Composite Floor | 11 | 11 | 100.0% | 90.9% | +0.0921 | +0.6774 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1708, Lock IC=+0.1017, Lock Sharpe=+1.2036
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1693, Lock IC=+0.1305, Lock Sharpe=+1.1546
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__trend_strength_intraday`: Train IC=+0.1807, Lock IC=+0.0953, Lock Sharpe=+1.0258
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__counter_trend_bar_weakness`: Train IC=+0.1717, Lock IC=+0.0907, Lock Sharpe=+0.9302
- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1772, Lock IC=+0.1258, Lock Sharpe=+0.8461

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1316, Lock IC=+0.1108, Lock Sharpe=+1.3365
- `combo_rank_min__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1316, Lock IC=+0.1108, Lock Sharpe=+1.3365
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1461, Lock IC=+0.1314, Lock Sharpe=+1.3188
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1461, Lock IC=+0.1314, Lock Sharpe=+1.3188
- `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.1181, Lock IC=+0.0964, Lock Sharpe=+1.2137

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1380, Lock IC=+0.1040, Lock Sharpe=+1.0977
- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1380, Lock IC=+0.1040, Lock Sharpe=+1.0977
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1324, Lock IC=+0.1159, Lock Sharpe=+1.0048
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1324, Lock IC=+0.1159, Lock Sharpe=+1.0048
- `combo_tri_median__rbreaker_sell_setup_proximity_early__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1735, Lock IC=+0.1298, Lock Sharpe=+0.8619

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1828, Lock IC=+0.0959, Lock Sharpe=+0.9059
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1828, Lock IC=+0.0959, Lock Sharpe=+0.9059
- `combo_tri_mean__opening_drive_thrust_ratio__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.8130
- `combo_tri_z_mean__opening_drive_thrust_ratio__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.8130
- `combo_tri_mean__opening_drive_thrust_ratio__first_30min_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.8130

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 44.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3745_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 247 | 30 | 76.7% | 46.7% | +0.0301 | -0.1996 |
| B2 Rolling Guard | 50 | 30 | 63.3% | 40.0% | +0.0232 | +0.0101 |
| BH-FDR Gate | 2 | 2 | 50.0% | 50.0% | +0.0352 | +0.0084 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `trend_day_regime_conviction`: Train IC=+0.1462, Lock IC=+0.0928, Lock Sharpe=+0.7840
- `high_low_sequence_momentum`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.6845
- `rsi_opening`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.6845
- `lunch_transition_volume_skew`: Train IC=+0.0808, Lock IC=+0.0330, Lock Sharpe=+0.6751
- `combo_mean__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0748, Lock IC=+0.0639, Lock Sharpe=+0.3991

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0517, Lock Sharpe=+1.1801
- `combo_rank_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0792, Lock IC=+0.0809, Lock Sharpe=+0.8982
- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0609, Lock IC=+0.0815, Lock Sharpe=+0.8238
- `limit_down_proximity_early`: Train IC=+0.0276, Lock IC=+0.1167, Lock Sharpe=+0.7619
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0276, Lock IC=+0.1167, Lock Sharpe=+0.7619

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volatility_expansion_trend_vector`: Train IC=+0.0580, Lock IC=+0.0943, Lock Sharpe=+0.5003

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 508 | +0.0267 | 80.0% |
| 0.45 | 0.20 | 501 | +0.0267 | 80.0% |
| 0.45 | 0.30 | 482 | +0.0267 | 80.0% |
| 0.45 | 0.40 | 405 | +0.0267 | 80.0% |
| 0.45 | 0.50 | 265 | +0.0267 | 80.0% |
| 0.50 | 0.15 | 503 | +0.0267 | 80.0% |
| 0.50 | 0.25 | 494 | +0.0267 | 80.0% |
| 0.50 | 0.35 | 453 | +0.0267 | 80.0% |
| 0.50 | 0.45 | 335 | +0.0267 | 80.0% |
| 0.55 | 0.10 | 503 | +0.0267 | 80.0% |
| 0.55 | 0.20 | 501 | +0.0267 | 80.0% |
| 0.55 | 0.30 | 482 | +0.0267 | 80.0% |
| 0.55 | 0.40 | 405 | +0.0267 | 80.0% |
| 0.55 | 0.50 | 265 | +0.0267 | 80.0% |
| 0.60 | 0.15 | 479 | +0.0267 | 80.0% |
| 0.60 | 0.25 | 478 | +0.0267 | 80.0% |
| 0.60 | 0.35 | 452 | +0.0267 | 80.0% |
| 0.60 | 0.45 | 335 | +0.0267 | 80.0% |
| 0.65 | 0.10 | 397 | +0.0267 | 80.0% |
| 0.65 | 0.20 | 397 | +0.0267 | 80.0% |
| 0.65 | 0.30 | 397 | +0.0267 | 80.0% |
| 0.65 | 0.40 | 380 | +0.0267 | 80.0% |
| 0.65 | 0.50 | 265 | +0.0267 | 80.0% |
| 0.70 | 0.15 | 202 | +0.0267 | 80.0% |
| 0.70 | 0.25 | 202 | +0.0267 | 80.0% |
| 0.70 | 0.35 | 202 | +0.0267 | 80.0% |
| 0.70 | 0.45 | 202 | +0.0267 | 80.0% |
| 0.75 | 0.10 | 48 | +0.0187 | 70.0% |
| 0.75 | 0.20 | 48 | +0.0187 | 70.0% |
| 0.75 | 0.30 | 48 | +0.0187 | 70.0% |
| 0.75 | 0.40 | 48 | +0.0187 | 70.0% |
| 0.75 | 0.50 | 48 | +0.0187 | 70.0% |
| 0.80 | 0.15 | 20 | +0.0125 | 60.0% |
| 0.80 | 0.25 | 20 | +0.0125 | 60.0% |
| 0.80 | 0.35 | 20 | +0.0125 | 60.0% |
| 0.80 | 0.45 | 20 | +0.0125 | 60.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 508 candidates, mean lock IC=+0.0267, 80.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 19 | -0.0073 | 50.0% |
| 0.45 | 0.20 | 8 | -0.0093 | 50.0% |
| 0.45 | 0.30 | 6 | -0.0065 | 66.7% |
| 0.45 | 0.40 | 2 | -0.0598 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 12 | -0.0073 | 50.0% |
| 0.50 | 0.25 | 7 | -0.0100 | 57.1% |
| 0.50 | 0.35 | 2 | -0.0598 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 10 | -0.0141 | 40.0% |
| 0.55 | 0.20 | 8 | -0.0093 | 50.0% |
| 0.55 | 0.30 | 6 | -0.0065 | 66.7% |
| 0.55 | 0.40 | 2 | -0.0598 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 6 | -0.0178 | 50.0% |
| 0.60 | 0.25 | 6 | -0.0178 | 50.0% |
| 0.60 | 0.35 | 2 | -0.0598 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.30 → 6 candidates, mean lock IC=-0.0065, 66.7% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 18 | +0.0079 | 40.0% |
| 0.45 | 0.20 | 6 | +0.0303 | 83.3% |
| 0.45 | 0.30 | 2 | +0.0254 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | +0.0271 | 77.8% |
| 0.50 | 0.25 | 5 | +0.0236 | 80.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 11 | +0.0146 | 50.0% |
| 0.55 | 0.20 | 6 | +0.0303 | 83.3% |
| 0.55 | 0.30 | 2 | +0.0254 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 3 | +0.0351 | 100.0% |
| 0.60 | 0.25 | 3 | +0.0351 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.15 → 7 candidates, mean lock IC=+0.0353, 85.7% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 329 | +0.0557 | 100.0% |
| 0.45 | 0.20 | 325 | +0.0557 | 100.0% |
| 0.45 | 0.30 | 321 | +0.0557 | 100.0% |
| 0.45 | 0.40 | 304 | +0.0557 | 100.0% |
| 0.45 | 0.50 | 295 | +0.0557 | 100.0% |
| 0.50 | 0.15 | 325 | +0.0557 | 100.0% |
| 0.50 | 0.25 | 324 | +0.0557 | 100.0% |
| 0.50 | 0.35 | 313 | +0.0557 | 100.0% |
| 0.50 | 0.45 | 299 | +0.0557 | 100.0% |
| 0.55 | 0.10 | 328 | +0.0557 | 100.0% |
| 0.55 | 0.20 | 325 | +0.0557 | 100.0% |
| 0.55 | 0.30 | 321 | +0.0557 | 100.0% |
| 0.55 | 0.40 | 304 | +0.0557 | 100.0% |
| 0.55 | 0.50 | 295 | +0.0557 | 100.0% |
| 0.60 | 0.15 | 323 | +0.0557 | 100.0% |
| 0.60 | 0.25 | 322 | +0.0557 | 100.0% |
| 0.60 | 0.35 | 313 | +0.0557 | 100.0% |
| 0.60 | 0.45 | 299 | +0.0557 | 100.0% |
| 0.65 | 0.10 | 304 | +0.0557 | 100.0% |
| 0.65 | 0.20 | 304 | +0.0557 | 100.0% |
| 0.65 | 0.30 | 302 | +0.0557 | 100.0% |
| 0.65 | 0.40 | 300 | +0.0557 | 100.0% |
| 0.65 | 0.50 | 294 | +0.0557 | 100.0% |
| 0.70 | 0.15 | 291 | +0.0557 | 100.0% |
| 0.70 | 0.25 | 291 | +0.0557 | 100.0% |
| 0.70 | 0.35 | 291 | +0.0557 | 100.0% |
| 0.70 | 0.45 | 291 | +0.0557 | 100.0% |
| 0.75 | 0.10 | 245 | +0.0557 | 100.0% |
| 0.75 | 0.20 | 245 | +0.0557 | 100.0% |
| 0.75 | 0.30 | 245 | +0.0557 | 100.0% |
| 0.75 | 0.40 | 245 | +0.0557 | 100.0% |
| 0.75 | 0.50 | 245 | +0.0557 | 100.0% |
| 0.80 | 0.15 | 191 | +0.0394 | 100.0% |
| 0.80 | 0.25 | 191 | +0.0394 | 100.0% |
| 0.80 | 0.35 | 191 | +0.0394 | 100.0% |
| 0.80 | 0.45 | 191 | +0.0394 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 329 candidates, mean lock IC=+0.0557, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 15 | -0.0083 | 30.0% |
| 0.45 | 0.20 | 10 | -0.0083 | 30.0% |
| 0.45 | 0.30 | 6 | -0.0297 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 10 | -0.0083 | 30.0% |
| 0.50 | 0.25 | 8 | -0.0226 | 12.5% |
| 0.50 | 0.35 | 6 | -0.0297 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 9 | -0.0190 | 22.2% |
| 0.55 | 0.20 | 8 | -0.0226 | 12.5% |
| 0.55 | 0.30 | 6 | -0.0297 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 7 | -0.0232 | 14.3% |
| 0.60 | 0.25 | 7 | -0.0232 | 14.3% |
| 0.60 | 0.35 | 6 | -0.0297 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 15 candidates, mean lock IC=-0.0083, 30.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 6 | -0.0276 | 16.7% |
| 0.45 | 0.20 | 4 | -0.0384 | 0.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 5 | -0.0423 | 0.0% |
| 0.50 | 0.25 | 1 | -0.0023 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | -0.0376 | 0.0% |
| 0.55 | 0.20 | 3 | -0.0309 | 0.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | -0.0203 | 0.0% |
| 0.60 | 0.25 | 1 | -0.0023 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 6 candidates, mean lock IC=-0.0276, 16.7% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1225 | +0.1003 | 100.0% |
| 0.45 | 0.20 | 1204 | +0.1003 | 100.0% |
| 0.45 | 0.30 | 1103 | +0.1003 | 100.0% |
| 0.45 | 0.40 | 910 | +0.1003 | 100.0% |
| 0.45 | 0.50 | 684 | +0.1003 | 100.0% |
| 0.50 | 0.15 | 1218 | +0.1003 | 100.0% |
| 0.50 | 0.25 | 1154 | +0.1003 | 100.0% |
| 0.50 | 0.35 | 1022 | +0.1003 | 100.0% |
| 0.50 | 0.45 | 822 | +0.1003 | 100.0% |
| 0.55 | 0.10 | 1213 | +0.1003 | 100.0% |
| 0.55 | 0.20 | 1202 | +0.1003 | 100.0% |
| 0.55 | 0.30 | 1103 | +0.1003 | 100.0% |
| 0.55 | 0.40 | 910 | +0.1003 | 100.0% |
| 0.55 | 0.50 | 684 | +0.1003 | 100.0% |
| 0.60 | 0.15 | 1133 | +0.1003 | 100.0% |
| 0.60 | 0.25 | 1116 | +0.1003 | 100.0% |
| 0.60 | 0.35 | 1020 | +0.1003 | 100.0% |
| 0.60 | 0.45 | 822 | +0.1003 | 100.0% |
| 0.65 | 0.10 | 899 | +0.1003 | 100.0% |
| 0.65 | 0.20 | 899 | +0.1003 | 100.0% |
| 0.65 | 0.30 | 899 | +0.1003 | 100.0% |
| 0.65 | 0.40 | 861 | +0.1003 | 100.0% |
| 0.65 | 0.50 | 679 | +0.1003 | 100.0% |
| 0.70 | 0.15 | 566 | +0.1003 | 100.0% |
| 0.70 | 0.25 | 566 | +0.1003 | 100.0% |
| 0.70 | 0.35 | 566 | +0.1003 | 100.0% |
| 0.70 | 0.45 | 566 | +0.1003 | 100.0% |
| 0.75 | 0.10 | 244 | +0.0997 | 100.0% |
| 0.75 | 0.20 | 244 | +0.0997 | 100.0% |
| 0.75 | 0.30 | 244 | +0.0997 | 100.0% |
| 0.75 | 0.40 | 244 | +0.0997 | 100.0% |
| 0.75 | 0.50 | 244 | +0.0997 | 100.0% |
| 0.80 | 0.15 | 92 | +0.1004 | 100.0% |
| 0.80 | 0.25 | 92 | +0.1004 | 100.0% |
| 0.80 | 0.35 | 92 | +0.1004 | 100.0% |
| 0.80 | 0.45 | 92 | +0.1004 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 92 candidates, mean lock IC=+0.1004, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 46 | -0.0031 | 30.0% |
| 0.45 | 0.20 | 35 | -0.0031 | 30.0% |
| 0.45 | 0.30 | 7 | +0.0393 | 71.4% |
| 0.45 | 0.40 | 2 | -0.0125 | 0.0% |
| 0.45 | 0.50 | 2 | -0.0125 | 0.0% |
| 0.50 | 0.15 | 37 | -0.0031 | 30.0% |
| 0.50 | 0.25 | 29 | -0.0031 | 30.0% |
| 0.50 | 0.35 | 6 | +0.0282 | 66.7% |
| 0.50 | 0.45 | 2 | -0.0125 | 0.0% |
| 0.55 | 0.10 | 38 | -0.0031 | 30.0% |
| 0.55 | 0.20 | 35 | -0.0031 | 30.0% |
| 0.55 | 0.30 | 7 | +0.0393 | 71.4% |
| 0.55 | 0.40 | 2 | -0.0125 | 0.0% |
| 0.55 | 0.50 | 2 | -0.0125 | 0.0% |
| 0.60 | 0.15 | 14 | -0.0031 | 30.0% |
| 0.60 | 0.25 | 14 | -0.0031 | 30.0% |
| 0.60 | 0.35 | 6 | +0.0282 | 66.7% |
| 0.60 | 0.45 | 2 | -0.0125 | 0.0% |
| 0.65 | 0.10 | 2 | -0.0125 | 0.0% |
| 0.65 | 0.20 | 2 | -0.0125 | 0.0% |
| 0.65 | 0.30 | 2 | -0.0125 | 0.0% |
| 0.65 | 0.40 | 2 | -0.0125 | 0.0% |
| 0.65 | 0.50 | 2 | -0.0125 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.30 → 7 candidates, mean lock IC=+0.0393, 71.4% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 11 | +0.0459 | 70.0% |
| 0.45 | 0.20 | 5 | +0.0812 | 80.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | +0.0758 | 87.5% |
| 0.50 | 0.25 | 3 | +0.0522 | 66.7% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 8 | +0.0758 | 87.5% |
| 0.55 | 0.20 | 5 | +0.0812 | 80.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 5 candidates, mean lock IC=+0.0812, 80.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 701 | +0.1169 | 100.0% |
| 0.45 | 0.20 | 671 | +0.1169 | 100.0% |
| 0.45 | 0.30 | 616 | +0.1169 | 100.0% |
| 0.45 | 0.40 | 469 | +0.1169 | 100.0% |
| 0.45 | 0.50 | 304 | +0.1169 | 100.0% |
| 0.50 | 0.15 | 687 | +0.1169 | 100.0% |
| 0.50 | 0.25 | 645 | +0.1169 | 100.0% |
| 0.50 | 0.35 | 562 | +0.1169 | 100.0% |
| 0.50 | 0.45 | 394 | +0.1169 | 100.0% |
| 0.55 | 0.10 | 687 | +0.1169 | 100.0% |
| 0.55 | 0.20 | 670 | +0.1169 | 100.0% |
| 0.55 | 0.30 | 616 | +0.1169 | 100.0% |
| 0.55 | 0.40 | 469 | +0.1169 | 100.0% |
| 0.55 | 0.50 | 304 | +0.1169 | 100.0% |
| 0.60 | 0.15 | 638 | +0.1169 | 100.0% |
| 0.60 | 0.25 | 635 | +0.1169 | 100.0% |
| 0.60 | 0.35 | 562 | +0.1169 | 100.0% |
| 0.60 | 0.45 | 394 | +0.1169 | 100.0% |
| 0.65 | 0.10 | 497 | +0.1169 | 100.0% |
| 0.65 | 0.20 | 497 | +0.1169 | 100.0% |
| 0.65 | 0.30 | 497 | +0.1169 | 100.0% |
| 0.65 | 0.40 | 441 | +0.1169 | 100.0% |
| 0.65 | 0.50 | 303 | +0.1169 | 100.0% |
| 0.70 | 0.15 | 255 | +0.1169 | 100.0% |
| 0.70 | 0.25 | 255 | +0.1169 | 100.0% |
| 0.70 | 0.35 | 255 | +0.1169 | 100.0% |
| 0.70 | 0.45 | 250 | +0.1169 | 100.0% |
| 0.75 | 0.10 | 75 | +0.1169 | 100.0% |
| 0.75 | 0.20 | 75 | +0.1169 | 100.0% |
| 0.75 | 0.30 | 75 | +0.1169 | 100.0% |
| 0.75 | 0.40 | 75 | +0.1169 | 100.0% |
| 0.75 | 0.50 | 75 | +0.1169 | 100.0% |
| 0.80 | 0.15 | 13 | +0.0373 | 40.0% |
| 0.80 | 0.25 | 13 | +0.0373 | 40.0% |
| 0.80 | 0.35 | 13 | +0.0373 | 40.0% |
| 0.80 | 0.45 | 13 | +0.0373 | 40.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 701 candidates, mean lock IC=+0.1169, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 164 | +0.0917 | 100.0% |
| 0.45 | 0.20 | 117 | +0.0917 | 100.0% |
| 0.45 | 0.30 | 49 | +0.0835 | 100.0% |
| 0.45 | 0.40 | 24 | +0.0988 | 100.0% |
| 0.45 | 0.50 | 4 | +0.0923 | 100.0% |
| 0.50 | 0.15 | 140 | +0.0917 | 100.0% |
| 0.50 | 0.25 | 82 | +0.0917 | 100.0% |
| 0.50 | 0.35 | 34 | +0.0867 | 100.0% |
| 0.50 | 0.45 | 5 | +0.0942 | 100.0% |
| 0.55 | 0.10 | 133 | +0.0917 | 100.0% |
| 0.55 | 0.20 | 115 | +0.0917 | 100.0% |
| 0.55 | 0.30 | 49 | +0.0835 | 100.0% |
| 0.55 | 0.40 | 24 | +0.0988 | 100.0% |
| 0.55 | 0.50 | 4 | +0.0923 | 100.0% |
| 0.60 | 0.15 | 56 | +0.0835 | 100.0% |
| 0.60 | 0.25 | 54 | +0.0835 | 100.0% |
| 0.60 | 0.35 | 34 | +0.0867 | 100.0% |
| 0.60 | 0.45 | 5 | +0.0942 | 100.0% |
| 0.65 | 0.10 | 24 | +0.0969 | 100.0% |
| 0.65 | 0.20 | 24 | +0.0969 | 100.0% |
| 0.65 | 0.30 | 24 | +0.0969 | 100.0% |
| 0.65 | 0.40 | 19 | +0.0969 | 100.0% |
| 0.65 | 0.50 | 3 | +0.0888 | 100.0% |
| 0.70 | 0.15 | 2 | +0.0086 | 100.0% |
| 0.70 | 0.25 | 2 | +0.0086 | 100.0% |
| 0.70 | 0.35 | 2 | +0.0086 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 24 candidates, mean lock IC=+0.0988, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 8 | +0.0521 | 87.5% |
| 0.45 | 0.20 | 3 | +0.0302 | 66.7% |
| 0.45 | 0.30 | 1 | -0.0238 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 3 | +0.0302 | 66.7% |
| 0.50 | 0.25 | 1 | -0.0238 | 0.0% |
| 0.50 | 0.35 | 1 | -0.0238 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 5 | +0.0326 | 80.0% |
| 0.55 | 0.20 | 2 | +0.0352 | 50.0% |
| 0.55 | 0.30 | 1 | -0.0238 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | -0.0238 | 0.0% |
| 0.60 | 0.25 | 1 | -0.0238 | 0.0% |
| 0.60 | 0.35 | 1 | -0.0238 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 8 candidates, mean lock IC=+0.0521, 87.5% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1301 | +0.0000 | +0.0383 | 0.29x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1171 | +0.0000 | +0.0516 | 0.44x | 2016-08-24 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1162 | +0.0000 | -0.0018 | -0.02x | 2015-02-06 |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | +0.1093 | +0.0000 | +0.0123 | 0.11x | 2015-02-06 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1149 | +0.0000 | -0.0134 | -0.12x | 2017-07-10 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1181 | +0.0000 | +0.0460 | 0.39x | 2016-08-24 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | +0.1168 | +0.0000 | +0.0067 | 0.06x | 2017-06-09 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1298 | +0.0000 | +0.0340 | 0.26x | 2016-08-24 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1071 | +0.0000 | +0.0084 | 0.08x | 2015-03-16 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +0.1167 | +0.0000 | +0.0094 | 0.08x | 2015-03-16 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.1037 | +0.0000 | -0.0023 | -0.02x | 2015-02-06 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0971 | +0.0000 | +0.0638 | 0.66x | 2013-08-21 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1082 | +0.0000 | -0.0120 | -0.11x | 2015-02-06 |
| `bar_body_rng_0` | +0.0955 | +0.0000 | +0.0301 | 0.32x | 2010-10-15 |
| `combo_rank_max__volume_weighted_price_position__bar_body_rng_0` | +0.0978 | +0.0000 | +0.0066 | 0.07x | 2015-02-06 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1276 | +0.0000 | +0.0317 | 0.25x | 2017-06-09 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | +0.0976 | +0.0000 | +0.0045 | 0.05x | 2013-08-21 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1094 | +0.0000 | +0.0254 | 0.23x | 2014-08-04 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1156 | +0.0000 | +0.0125 | 0.11x | 2017-07-10 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1310 | +0.0000 | +0.0352 | 0.27x | 2016-08-24 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1182 | +0.0000 | +0.0057 | 0.05x | 2017-07-10 |
| `combo_max__max_up_ret__bar_ret_0` | +0.1023 | +0.0000 | +0.0124 | 0.12x | 2014-07-04 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1111 | +0.0000 | -0.0166 | -0.15x | 2015-01-08 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +0.1167 | +0.0000 | +0.0193 | 0.16x | 2017-04-07 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.0950 | +0.0000 | +0.0572 | 0.60x | 2016-07-26 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1215 | +0.0000 | +0.0329 | 0.27x | 2017-07-10 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1094 | +0.0000 | +0.0183 | 0.17x | 2015-02-06 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.0960 | +0.0000 | -0.0025 | -0.03x | 2013-08-21 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1155 | +0.0000 | +0.0013 | 0.01x | 2015-03-16 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1164 | +0.0000 | +0.0362 | 0.31x | 2015-02-06 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1113 | +0.0000 | +0.0217 | 0.19x | 2017-08-08 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1250 | +0.0000 | +0.0362 | 0.29x | 2017-07-10 |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1175 | +0.0000 | +0.0337 | 0.29x | 2015-02-06 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | +0.1106 | +0.0000 | +0.0496 | 0.45x | 2017-08-08 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1038 | +0.0000 | +0.0136 | 0.13x | 2014-07-04 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1210 | +0.0000 | +0.0334 | 0.28x | 2017-05-09 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +0.1128 | +0.0000 | +0.0012 | 0.01x | 2015-01-08 |
| `opening_drive_thrust_ratio` | +0.1159 | +0.0000 | +0.0060 | 0.05x | 2017-06-09 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1117 | +0.0000 | +0.0022 | 0.02x | 2015-02-06 |
| `combo_max__bar_ret_0__bar_body_rng_0` | +0.0916 | +0.0000 | +0.0220 | 0.24x | 2013-08-21 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1145 | +0.0000 | +0.0270 | 0.24x | 2017-05-09 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | +0.1095 | +0.0000 | +0.0132 | 0.12x | 2015-02-06 |
| `combo_tri_max__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1114 | +0.0000 | -0.0121 | -0.11x | 2017-07-10 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1093 | +0.0000 | +0.0215 | 0.20x | 2014-08-04 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1144 | +0.0000 | +0.0440 | 0.38x | 2016-08-24 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | +0.1208 | +0.0000 | +0.0376 | 0.31x | 2016-08-24 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0963 | +0.0000 | +0.0427 | 0.44x | 2016-08-24 |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1215 | +0.0000 | +0.0071 | 0.06x | 2017-07-10 |
| `max_up_ret` | +0.1022 | +0.0000 | -0.0047 | -0.05x | 2015-02-06 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | +0.0932 | +0.0000 | +0.0168 | 0.18x | 2013-08-21 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0348 | +0.0000 | -0.0158 | -0.45x | 2010-10-15 |
| `combo_max__max_up_ret__first_bar_sentiment` | +0.1026 | +0.0000 | +0.0000 | 0.00x | 2015-01-08 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.0954 | +0.0000 | +0.0306 | 0.32x | 2014-07-04 |
| `combo_rank_max__bar_body_rng_0__volume_surge_direction` | +0.0874 | +0.0000 | +0.0172 | 0.20x | 2013-08-21 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | +0.1176 | +0.0000 | +0.0267 | 0.23x | 2017-02-06 |
| `combo_mean__max_up_ret__volume_surge_direction` | +0.1003 | +0.0000 | +0.0161 | 0.16x | 2014-07-04 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.0894 | +0.0000 | +0.0235 | 0.26x | 2014-07-04 |
| `combo_max__max_up_ret__volume_surge_direction` | +0.0892 | +0.0000 | +0.0092 | 0.10x | 2014-07-04 |
| `combo_ratio__bar_ret_0__volume_surge_direction` | +0.0836 | +0.0000 | +0.0050 | 0.06x | 2010-10-15 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | +0.0967 | +0.0000 | -0.0006 | -0.01x | 2015-03-16 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction` | +0.1030 | +0.0000 | +0.0260 | 0.25x | 2015-02-06 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +0.1012 | +0.0000 | +0.0285 | 0.28x | 2015-02-06 |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | +0.0926 | +0.0000 | -0.0116 | -0.13x | 2015-01-08 |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | +0.1129 | +0.0000 | +0.0081 | 0.07x | 2017-06-09 |
| `combo_max__first_bar_return__first_bar_sentiment` | +0.0885 | +0.0000 | -0.0050 | -0.06x | 2013-07-23 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.0983 | +0.0000 | +0.0512 | 0.52x | 2015-02-06 |
| `early_order_flow_imbalance` | +0.0512 | +0.0000 | -0.0189 | -0.37x | 2010-12-14 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.0862 | +0.0000 | +0.0374 | 0.43x | 2014-07-04 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +0.0743 | +0.0000 | +0.0288 | 0.39x | 2017-10-12 |
| `combo_rank_max__volume_weighted_price_position__first_bar_sentiment` | +0.0906 | +0.0000 | -0.0229 | -0.25x | 2010-12-14 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | +0.1152 | +0.0000 | +0.0225 | 0.20x | 2016-12-29 |
| `first_30min_return` | +0.0708 | +0.0000 | +0.0077 | 0.11x | 2015-02-06 |
| `net_volume_flow` | +0.0673 | +0.0000 | -0.0024 | -0.03x | 2015-01-08 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | +0.0358 | +0.0000 | +0.0203 | 0.57x | 2010-10-15 |
| `combo_ratio__first_bar_sentiment__volume_weighted_price_position` | +0.0613 | +0.0000 | -0.0364 | -0.59x | 2010-10-15 |
| `always_in_trend_persistence` | +0.0452 | +0.0000 | -0.0421 | -0.93x | 2012-06-05 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +0.0735 | +0.0000 | +0.0530 | 0.72x | 2017-09-06 |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | +0.0848 | +0.0000 | +0.0112 | 0.13x | 2013-08-21 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | +0.1804 | +0.0000 | +0.0923 | 0.51x | 2016-11-30 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1881 | +0.0000 | +0.0955 | 0.51x | 2021-07-28 |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | +0.1912 | +0.0000 | +0.1127 | 0.59x | 2016-11-01 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1938 | +0.0000 | +0.0995 | 0.51x | 2016-11-30 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | +0.1868 | +0.0000 | +0.1084 | 0.58x | No decay |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +0.1669 | +0.0000 | +0.0590 | 0.35x | 2020-01-06 |
| `combo_max__early_body_momentum__bar_ret_0` | +0.1655 | +0.0000 | +0.0581 | 0.35x | 2026-04-07 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | +0.1382 | +0.0000 | +0.0742 | 0.54x | 2013-09-23 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1712 | +0.0000 | +0.1023 | 0.60x | 2021-07-28 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1931 | +0.0000 | +0.1193 | 0.62x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_day_regime_conviction` | +0.1931 | +0.0000 | +0.1157 | 0.60x | No decay |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1929 | +0.0000 | +0.0949 | 0.49x | No decay |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1673 | +0.0000 | +0.0747 | 0.45x | 2019-12-05 |
| `combo_diff__max_up_ret__body_size_progression` | +0.1743 | +0.0000 | +0.0842 | 0.48x | 2025-07-24 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1826 | +0.0000 | +0.0858 | 0.47x | No decay |
| `combo_rank_max__close_vs_open_range__first_bar_return` | +0.1676 | +0.0000 | +0.0746 | 0.44x | No decay |
| `combo_clamp_diff__max_up_ret__body_size_progression` | +0.1746 | +0.0000 | +0.0855 | 0.49x | 2025-07-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1803 | +0.0000 | +0.1105 | 0.61x | No decay |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | +0.2027 | +0.0000 | +0.0937 | 0.46x | No decay |
| `combo_max__net_volume_flow__first_bar_sentiment` | +0.1512 | +0.0000 | +0.0803 | 0.53x | 2020-01-06 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | +0.1871 | +0.0000 | +0.0905 | 0.48x | No decay |
| `combo_max__close_vs_open_range__first_bar_return` | +0.1680 | +0.0000 | +0.0749 | 0.45x | No decay |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1897 | +0.0000 | +0.0874 | 0.46x | 2025-07-24 |
| `combo_mean__max_up_ret__volatility_expansion_trend_vector` | +0.1790 | +0.0000 | +0.0841 | 0.47x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1541 | +0.0000 | +0.0946 | 0.61x | 2016-11-01 |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | +0.1449 | +0.0000 | +0.0887 | 0.61x | 2016-11-01 |
| `combo_max__bar_ret_0__max_down_ret` | +0.1604 | +0.0000 | +0.0818 | 0.51x | 2016-11-30 |
| `combo_mean__net_volume_flow__first_bar_return` | +0.1686 | +0.0000 | +0.0871 | 0.52x | No decay |
| `combo_min__net_volume_flow__close_vs_open_range` | +0.1456 | +0.0000 | +0.0868 | 0.60x | 2016-11-01 |
| `combo_mean__opening_drive_thrust_ratio__early_body_momentum` | +0.1802 | +0.0000 | +0.0857 | 0.48x | 2016-11-30 |
| `combo_max__max_up_ret__early_body_momentum` | +0.1781 | +0.0000 | +0.0735 | 0.41x | 2016-11-30 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1707 | +0.0000 | +0.1125 | 0.66x | No decay |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1614 | +0.0000 | +0.0902 | 0.56x | 2016-12-29 |
| `combo_min__net_volume_flow__first_bar_return` | +0.1467 | +0.0000 | +0.0967 | 0.66x | No decay |
| `combo_mean__max_up_ret__first_bar_return` | +0.1812 | +0.0000 | +0.0784 | 0.43x | No decay |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1580 | +0.0000 | +0.0969 | 0.61x | 2016-09-26 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | +0.1908 | +0.0000 | +0.1052 | 0.55x | No decay |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1546 | +0.0000 | +0.1220 | 0.79x | 2016-09-26 |
| `combo_mean__close_vs_open_range__first_bar_return` | +0.1651 | +0.0000 | +0.0927 | 0.56x | No decay |
| `combo_rank_max__max_up_ret__early_body_momentum` | +0.1797 | +0.0000 | +0.0757 | 0.42x | 2016-11-30 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1845 | +0.0000 | +0.0991 | 0.54x | No decay |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.1670 | +0.0000 | +0.0640 | 0.38x | 2020-01-06 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1760 | +0.0000 | +0.0889 | 0.51x | No decay |
| `first_bar_return` | +0.1413 | +0.0000 | +0.0686 | 0.49x | 2013-09-23 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | +0.1943 | +0.0000 | +0.0963 | 0.50x | No decay |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | +0.1465 | +0.0000 | +0.0932 | 0.64x | 2020-02-12 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1572 | +0.0000 | +0.1182 | 0.75x | 2016-09-26 |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | +0.1698 | +0.0000 | +0.1133 | 0.67x | 2019-12-05 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.2090 | +0.0000 | +0.1096 | 0.52x | No decay |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1682 | +0.0000 | +0.0802 | 0.48x | 2020-01-06 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | +0.1775 | +0.0000 | +0.0881 | 0.50x | 2020-01-06 |
| `combo_mean__first_bar_sentiment__bar_ret_0` | +0.1413 | +0.0000 | +0.0686 | 0.49x | 2013-09-23 |
| `combo_rank_max__early_body_momentum__max_down_ret` | +0.1528 | +0.0000 | +0.0875 | 0.57x | 2016-11-01 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1725 | +0.0000 | +0.0849 | 0.49x | No decay |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1687 | +0.0000 | +0.0880 | 0.52x | 2020-01-06 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | +0.1778 | +0.0000 | +0.1222 | 0.69x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1711 | +0.0000 | +0.0905 | 0.53x | 2016-11-01 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1687 | +0.0000 | +0.0905 | 0.54x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1670 | +0.0000 | +0.0942 | 0.56x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1840 | +0.0000 | +0.0891 | 0.48x | 2020-01-06 |
| `combo_rel_diff__max_up_ret__early_late_momentum_divergence` | +0.1658 | +0.0000 | +0.0684 | 0.41x | 2014-06-05 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1740 | +0.0000 | +0.0919 | 0.53x | 2020-01-06 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | +0.1565 | +0.0000 | +0.0969 | 0.62x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | +0.1723 | +0.0000 | +0.0774 | 0.45x | 2016-12-29 |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | +0.1530 | +0.0000 | +0.0916 | 0.60x | 2020-01-06 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1963 | +0.0000 | +0.0890 | 0.45x | 2016-11-30 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1890 | +0.0000 | +0.0857 | 0.45x | 2025-07-24 |
| `combo_sig_product__max_up_ret__net_volume_flow` | +0.1712 | +0.0000 | +0.0933 | 0.54x | 2020-01-06 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | +0.1551 | +0.0000 | +0.0962 | 0.62x | 2016-11-01 |
| `max_up_ret` | +0.1871 | +0.0000 | +0.0813 | 0.43x | No decay |
| `opening_drive_thrust_ratio` | +0.1849 | +0.0000 | +0.0962 | 0.52x | No decay |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1647 | +0.0000 | +0.0778 | 0.47x | 2020-01-06 |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | +0.1484 | +0.0000 | +0.0835 | 0.56x | 2020-02-12 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +0.1703 | +0.0000 | +0.0999 | 0.59x | 2016-11-30 |
| `combo_rank_max__bar_ret_0__max_down_ret` | +0.1619 | +0.0000 | +0.0923 | 0.57x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1661 | +0.0000 | +0.0927 | 0.56x | No decay |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1569 | +0.0000 | +0.0891 | 0.57x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1696 | +0.0000 | +0.0607 | 0.36x | 2016-12-29 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | +0.1656 | +0.0000 | +0.0946 | 0.57x | 2016-11-01 |
| `combo_min__max_up_ret__volatility_expansion_trend_vector` | +0.1679 | +0.0000 | +0.0885 | 0.53x | 2020-02-12 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | +0.1615 | +0.0000 | +0.1235 | 0.76x | 2016-09-26 |
| `combo_mean__first_bar_sentiment__early_body_momentum` | +0.1521 | +0.0000 | +0.0775 | 0.51x | 2020-01-06 |
| `combo_sig_product__max_up_ret__first_bar_return` | +0.1566 | +0.0000 | +0.0557 | 0.36x | No decay |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1638 | +0.0000 | +0.0932 | 0.57x | 2016-09-26 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1438 | +0.0000 | +0.1093 | 0.76x | 2016-09-26 |
| `combo_max__max_up_ret__first_bar_sentiment` | +0.1666 | +0.0000 | +0.0811 | 0.49x | 2020-01-06 |
| `combo_max__net_volume_flow__max_down_ret` | +0.1536 | +0.0000 | +0.0913 | 0.59x | 2016-11-01 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | +0.1553 | +0.0000 | +0.0877 | 0.57x | 2016-12-29 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1830 | +0.0000 | +0.0668 | 0.36x | 2016-12-29 |
| `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__trend_day_regime_conviction` | +0.1431 | +0.0000 | +0.0934 | 0.65x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | +0.1805 | +0.0000 | +0.0998 | 0.55x | 2016-11-30 |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1634 | +0.0000 | +0.0898 | 0.55x | No decay |
| `combo_rank_max__close_vs_open_range__early_body_momentum` | +0.1442 | +0.0000 | +0.0801 | 0.56x | 2016-11-01 |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1517 | +0.0000 | +0.0816 | 0.54x | 2016-11-01 |
| `combo_min__close_vs_open_range__first_bar_return` | +0.1406 | +0.0000 | +0.1023 | 0.73x | 2020-01-06 |
| `combo_min__net_volume_flow__max_down_ret` | +0.1512 | +0.0000 | +0.1016 | 0.67x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1420 | +0.0000 | +0.1566 | 1.10x | 2016-09-26 |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | +0.1734 | +0.0000 | +0.1170 | 0.67x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1650 | +0.0000 | +0.0540 | 0.33x | 2016-12-29 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1421 | +0.0000 | +0.0996 | 0.70x | 2016-09-26 |
| `open_to_current_return` | +0.1473 | +0.0000 | +0.0774 | 0.53x | 2016-11-01 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1730 | +0.0000 | +0.1289 | 0.74x | 2016-08-24 |
| `combo_min__close_vs_open_range__max_down_ret` | +0.1496 | +0.0000 | +0.1016 | 0.68x | 2016-09-26 |
| `combo_min__max_up_ret__close_vs_open_range` | +0.1624 | +0.0000 | +0.0977 | 0.60x | 2020-01-06 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | +0.1475 | +0.0000 | +0.0770 | 0.52x | 2016-11-01 |
| `combo_min__first_bar_sentiment__max_down_ret` | +0.1416 | +0.0000 | +0.0905 | 0.64x | No decay |
| `combo_rank_max__max_up_ret__close_vs_open_range` | +0.1791 | +0.0000 | +0.0774 | 0.43x | 2016-11-01 |
| `vwap_trend_channel_slope` | +0.1469 | +0.0000 | +0.0712 | 0.48x | 2016-11-01 |
| `combo_min__max_up_ret__early_body_momentum` | +0.1609 | +0.0000 | +0.0739 | 0.46x | 2020-02-12 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1653 | +0.0000 | +0.0829 | 0.50x | No decay |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | +0.1761 | +0.0000 | +0.1011 | 0.57x | 2016-11-30 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1371 | +0.0000 | +0.0994 | 0.73x | 2016-09-26 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1418 | +0.0000 | +0.1019 | 0.72x | 2016-08-24 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1494 | +0.0000 | +0.0836 | 0.56x | 2016-09-26 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1658 | +0.0000 | +0.0730 | 0.44x | 2016-09-26 |
| `early_body_momentum` | +0.1341 | +0.0000 | +0.0648 | 0.48x | 2016-11-01 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration` | +0.0879 | +0.0000 | +0.0705 | 0.80x | 2012-05-07 |
| `combo_rank_max__net_volume_flow__star50_limit_proximity_early` | +0.1631 | +0.0000 | +0.1031 | 0.63x | 2021-01-19 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1594 | +0.0000 | +0.0876 | 0.55x | 2022-12-15 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +0.1277 | +0.0000 | +0.0595 | 0.47x | 2017-08-08 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | +0.1463 | +0.0000 | +0.1409 | 0.96x | 2011-10-26 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1737 | +0.0000 | +0.1082 | 0.62x | 2021-05-28 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1650 | +0.0000 | +0.0579 | 0.35x | 2016-12-29 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | +0.1543 | +0.0000 | +0.0678 | 0.44x | 2021-07-28 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1504 | +0.0000 | +0.0794 | 0.53x | No decay |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1595 | +0.0000 | +0.1124 | 0.70x | 2016-09-26 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | +0.1639 | +0.0000 | +0.0992 | 0.61x | 2016-09-26 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | +0.1539 | +0.0000 | +0.1133 | 0.74x | 2016-09-26 |
| `morning_volume_weighted_momentum` | +0.1396 | +0.0000 | +0.0778 | 0.56x | 2016-11-01 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1507 | +0.0000 | +0.0934 | 0.62x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | +0.1615 | +0.0000 | +0.1236 | 0.77x | 2016-08-24 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | +0.1525 | +0.0000 | +0.1108 | 0.73x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | +0.1391 | +0.0000 | +0.1148 | 0.82x | 2016-08-24 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1749 | +0.0000 | +0.0883 | 0.51x | 2016-11-01 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | +0.1451 | +0.0000 | +0.0828 | 0.57x | 2020-01-06 |
| `combo_min__net_volume_flow__first_bar_sentiment` | +0.1519 | +0.0000 | +0.0882 | 0.58x | 2020-02-12 |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1488 | +0.0000 | +0.0815 | 0.55x | 2016-11-30 |
| `early_order_flow_imbalance` | +0.1256 | +0.0000 | +0.0431 | 0.34x | 2016-11-01 |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | +0.1581 | +0.0000 | +0.0826 | 0.52x | 2019-12-05 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1372 | +0.0000 | +0.0895 | 0.65x | 2020-12-18 |
| `combo_diff__bar_ret_0__max_down_ret` | +0.0372 | +0.0000 | +0.0120 | 0.32x | 2010-10-15 |
| `combo_max__trend_bar_close_consistency__max_down_ret` | +0.1395 | +0.0000 | +0.0635 | 0.46x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1261 | +0.0000 | +0.1529 | 1.21x | 2016-06-27 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__net_volume_flow` | +0.1445 | +0.0000 | +0.0762 | 0.53x | 2016-09-26 |
| `trend_strength_intraday` | +0.1206 | +0.0000 | +0.0894 | 0.74x | 2020-02-12 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1599 | +0.0000 | +0.1277 | 0.80x | 2017-04-28 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1618 | +0.0000 | +0.1235 | 0.76x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1664 | +0.0000 | +0.1102 | 0.66x | 2016-12-21 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1725 | +0.0000 | +0.1164 | 0.68x | 2017-02-27 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1672 | +0.0000 | +0.1267 | 0.76x | 2016-12-21 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1667 | +0.0000 | +0.1190 | 0.71x | 2017-02-27 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1589 | +0.0000 | +0.1243 | 0.78x | 2011-11-16 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1614 | +0.0000 | +0.1187 | 0.74x | 2016-12-21 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1639 | +0.0000 | +0.1258 | 0.77x | 2016-10-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1165 | +0.0000 | +0.0911 | 0.78x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1511 | +0.0000 | +0.1279 | 0.85x | 2017-01-20 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | +0.1642 | +0.0000 | +0.1327 | 0.81x | 2017-01-20 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | +0.1548 | +0.0000 | +0.1068 | 0.69x | 2011-10-18 |
| `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position` | +0.1415 | +0.0000 | +0.1384 | 0.98x | 2016-10-24 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1453 | +0.0000 | +0.1211 | 0.83x | 2011-10-18 |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | +0.1557 | +0.0000 | +0.1241 | 0.80x | 2017-02-27 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1510 | +0.0000 | +0.1316 | 0.87x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1550 | +0.0000 | +0.1282 | 0.83x | 2016-10-24 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1623 | +0.0000 | +0.0846 | 0.52x | 2017-01-20 |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1726 | +0.0000 | +0.1262 | 0.73x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1592 | +0.0000 | +0.1167 | 0.73x | 2011-10-18 |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | +0.1546 | +0.0000 | +0.1330 | 0.86x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1759 | +0.0000 | +0.1173 | 0.67x | 2017-01-20 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | +0.1578 | +0.0000 | +0.0853 | 0.54x | 2016-12-21 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1750 | +0.0000 | +0.1231 | 0.70x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1531 | +0.0000 | +0.1321 | 0.86x | 2016-10-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1538 | +0.0000 | +0.0989 | 0.64x | 2011-10-18 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1680 | +0.0000 | +0.1301 | 0.77x | 2017-01-20 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1598 | +0.0000 | +0.0983 | 0.62x | 2017-04-28 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | +0.1603 | +0.0000 | +0.1191 | 0.74x | 2017-01-20 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1588 | +0.0000 | +0.1315 | 0.83x | 2016-10-24 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | +0.1650 | +0.0000 | +0.0976 | 0.59x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1640 | +0.0000 | +0.1118 | 0.68x | 2016-10-24 |
| `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0` | +0.1474 | +0.0000 | +0.0866 | 0.59x | 2017-02-27 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | +0.1515 | +0.0000 | +0.0759 | 0.50x | 2017-01-20 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +0.1552 | +0.0000 | +0.0864 | 0.56x | 2017-02-27 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1402 | +0.0000 | +0.1290 | 0.92x | 2011-10-18 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | +0.1557 | +0.0000 | +0.0891 | 0.57x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1398 | +0.0000 | +0.1203 | 0.86x | 2016-09-14 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.1528 | +0.0000 | +0.0702 | 0.46x | 2017-04-28 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1035 | +0.0000 | +0.1119 | 1.08x | 2011-10-18 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1046 | +0.0000 | +0.1097 | 1.05x | 2011-10-18 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | +0.1624 | +0.0000 | +0.0781 | 0.48x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1408 | +0.0000 | +0.1241 | 0.88x | 2011-10-18 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | +0.1564 | +0.0000 | +0.0985 | 0.63x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | +0.1408 | +0.0000 | +0.1270 | 0.90x | 2011-10-18 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1552 | +0.0000 | +0.1244 | 0.80x | 2016-10-24 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | +0.1501 | +0.0000 | +0.0922 | 0.61x | 2017-01-20 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1238 | +0.0000 | +0.1088 | 0.88x | 2017-02-27 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | +0.1622 | +0.0000 | +0.1028 | 0.63x | 2017-01-20 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1624 | +0.0000 | +0.1026 | 0.63x | 2017-01-20 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1430 | +0.0000 | +0.1250 | 0.87x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1489 | +0.0000 | +0.1236 | 0.83x | 2016-09-14 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.1254 | +0.0000 | +0.1399 | 1.12x | 2011-10-18 |
| `combo_tri_max__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | +0.1196 | +0.0000 | +0.1054 | 0.88x | 2017-02-27 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1278 | +0.0000 | +0.1284 | 1.00x | 2017-02-27 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | +0.1518 | +0.0000 | +0.0874 | 0.58x | 2017-01-20 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1604 | +0.0000 | +0.1084 | 0.68x | 2017-02-27 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | +0.1612 | +0.0000 | +0.0834 | 0.52x | 2017-01-20 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1188 | +0.0000 | +0.1005 | 0.85x | 2017-02-27 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1211 | +0.0000 | +0.1270 | 1.05x | 2017-01-20 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1670 | +0.0000 | +0.1230 | 0.74x | 2017-01-20 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1598 | +0.0000 | +0.1109 | 0.69x | 2017-02-27 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1598 | +0.0000 | +0.0909 | 0.57x | 2017-01-20 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | +0.1380 | +0.0000 | +0.0959 | 0.70x | 2016-10-24 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1574 | +0.0000 | +0.1088 | 0.69x | 2016-10-24 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1642 | +0.0000 | +0.1249 | 0.76x | 2017-01-20 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | +0.1549 | +0.0000 | +0.1018 | 0.66x | 2017-04-28 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1600 | +0.0000 | +0.1056 | 0.66x | 2017-03-28 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | +0.1575 | +0.0000 | +0.1093 | 0.69x | 2017-01-20 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | +0.1577 | +0.0000 | +0.1062 | 0.67x | 2016-10-24 |
| `max_up_ret` | +0.1545 | +0.0000 | +0.0765 | 0.49x | 2017-01-20 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1194 | +0.0000 | +0.1330 | 1.11x | 2011-10-18 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | +0.1464 | +0.0000 | +0.0989 | 0.68x | 2016-10-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1564 | +0.0000 | +0.0954 | 0.61x | 2017-04-28 |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | +0.1203 | +0.0000 | +0.0715 | 0.59x | 2017-01-20 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1468 | +0.0000 | +0.1273 | 0.87x | 2016-09-14 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1606 | +0.0000 | +0.0865 | 0.54x | 2016-12-21 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1483 | +0.0000 | +0.0926 | 0.62x | 2017-01-20 |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1498 | +0.0000 | +0.1385 | 0.92x | 2016-09-14 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1502 | +0.0000 | +0.1267 | 0.84x | 2017-03-28 |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1280 | +0.0000 | +0.1167 | 0.91x | 2011-10-18 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | +0.1451 | +0.0000 | +0.0831 | 0.57x | 2017-04-28 |
| `combo_max__max_up_ret__impulse_bar_dominance` | +0.1304 | +0.0000 | +0.0673 | 0.52x | 2016-10-24 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1317 | +0.0000 | +0.1079 | 0.82x | 2016-09-14 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1544 | +0.0000 | +0.0962 | 0.62x | 2016-10-24 |
| `combo_min__first_bar_return__limit_down_proximity_early` | +0.1258 | +0.0000 | +0.1269 | 1.01x | 2011-10-18 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1507 | +0.0000 | +0.1109 | 0.74x | 2016-09-14 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1192 | +0.0000 | +0.0677 | 0.57x | 2016-10-24 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | +0.1582 | +0.0000 | +0.1214 | 0.77x | 2017-01-20 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1329 | +0.0000 | +0.0987 | 0.74x | 2016-10-24 |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | +0.1553 | +0.0000 | +0.0808 | 0.52x | 2017-01-20 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1351 | +0.0000 | +0.0789 | 0.58x | 2014-03-25 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | +0.1510 | +0.0000 | +0.0988 | 0.65x | 2017-01-20 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | +0.1380 | +0.0000 | +0.1298 | 0.94x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1213 | +0.0000 | +0.0930 | 0.77x | 2011-12-15 |
| `opening_drive_thrust_ratio` | +0.1464 | +0.0000 | +0.0919 | 0.63x | 2016-10-24 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | +0.1339 | +0.0000 | +0.0933 | 0.70x | 2016-10-24 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | +0.1603 | +0.0000 | +0.0856 | 0.53x | 2017-01-20 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | +0.1545 | +0.0000 | +0.0770 | 0.50x | 2016-10-24 |
| `combo_max__first_bar_return__rbreaker_buy_setup_proximity_early` | +0.1442 | +0.0000 | +0.0792 | 0.55x | 2017-01-20 |
| `combo_z_sum__limit_down_proximity_early__volume_weighted_price_position` | +0.1419 | +0.0000 | +0.1254 | 0.88x | 2016-10-24 |
| `combo_max__yesterday_first_30min_return__limit_down_proximity_early` | +0.1011 | +0.0000 | +0.0974 | 0.96x | 2017-01-20 |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1027 | +0.0000 | +0.0898 | 0.87x | 2013-04-09 |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1539 | +0.0000 | +0.0818 | 0.53x | 2017-01-20 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | +0.0708 | +0.0000 | +0.0258 | 0.37x | 2011-04-13 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1582 | +0.0000 | +0.0883 | 0.56x | 2017-01-20 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1529 | +0.0000 | +0.0890 | 0.58x | 2017-01-20 |
| `net_volume_flow` | +0.1367 | +0.0000 | +0.0976 | 0.71x | 2014-03-25 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | +0.1324 | +0.0000 | +0.0659 | 0.50x | 2017-01-20 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +0.0792 | +0.0000 | +0.0196 | 0.25x | 2014-08-25 |
| `combo_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +0.0791 | +0.0000 | +0.0200 | 0.25x | 2014-08-25 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1403 | +0.0000 | +0.1188 | 0.85x | 2016-10-24 |
| `close_vs_open_range` | +0.1256 | +0.0000 | +0.1017 | 0.81x | 2014-03-25 |
| `first_bar_return` | +0.1446 | +0.0000 | +0.0706 | 0.49x | 2017-04-28 |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1377 | +0.0000 | +0.0925 | 0.67x | 2016-10-24 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0645 | +0.0000 | -0.0273 | -0.42x | 2012-01-17 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — B4 Correlation Gate too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=-0.0248). Consider relaxing this gate.
2. **300ETF `single` — Admission too loose**: 52% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
3. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2260). Consider relaxing this gate.
4. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.3172). Consider relaxing this gate.
5. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 27.0%, mean lock Sharpe=+0.1673). Consider relaxing this gate.
6. **50ETF `long` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 7.0%, mean lock Sharpe=-0.7170). Consider relaxing this gate.
7. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.1383). Consider relaxing this gate.
8. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.5995). Consider relaxing this gate.
9. **500ETF `single` — B2 Rolling Guard too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.4802). Consider relaxing this gate.
10. **500ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.2939). Consider relaxing this gate.
11. **500ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.5636). Consider relaxing this gate.
12. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 22.0%, mean lock Sharpe=-0.1255). Consider relaxing this gate.
13. **500ETF `short` — BH-FDR Gate too strict**: 75.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.1756). Consider relaxing this gate.
14. **159915ETF `single` — B2 Rolling Guard too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+0.6425). Consider relaxing this gate.
15. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+0.5932). Consider relaxing this gate.
16. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+1.3428). Consider relaxing this gate.
17. **159915ETF `long` — B2 Rolling Guard too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6794). Consider relaxing this gate.
18. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6624). Consider relaxing this gate.
19. **159915ETF `long` — B3 Composite Floor too strict**: 90.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6774). Consider relaxing this gate.
20. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.1996). Consider relaxing this gate.
21. **159915ETF `short` — B2 Rolling Guard too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=+0.0101). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
