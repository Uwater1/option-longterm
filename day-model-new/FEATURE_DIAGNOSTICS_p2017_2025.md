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

### 300ETF — `single` (Full Model Lockbox IC: +0.0122, Sharpe: -0.2948)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1012 | +0.0544 | +0.0544 | -0.0805 | 0.80 | 1/8 | 1.14 | 1.31 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0007 | -0.0846 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1035 | +0.0229 | +0.0229 | -0.5791 | 0.83 | 1/8 | 1.06 | 0.90 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0002 | -0.2278 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.0996 | +0.0463 | +0.0463 | -0.5117 | 0.77 | 1/8 | 1.12 | 1.27 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0008 | -0.2278 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0864 | -0.0365 | -0.0365 | -1.6583 | 0.85 | 1/8 | 1.81 | 1.78 | `max_up_ret` (0.94) | -0.0007 | +0.0613 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0976 | +0.0164 | +0.0164 | -0.7568 | 0.95 | 1/8 | 1.15 | 1.25 | `rbreaker_sell_setup_proximity_early` (1.21) | -0.0002 | -0.2278 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0875 | -0.0223 | -0.0223 | -1.3571 | 0.76 | 1/8 | 1.46 | 1.12 | `max_up_ret` (0.94) | -0.0009 | +0.0613 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0936 | -0.0022 | -0.0022 | -1.3090 | 0.89 | 1/8 | 1.36 | 0.75 | `volume_weighted_price_position` (1.24) | -0.0003 | -0.0176 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0901 | -0.0261 | -0.0261 | -0.8875 | 0.90 | 0/8 | 2.24 | 1.24 | `volume_weighted_price_position` (1.24) | +0.0000 | -0.0176 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0852 | +0.0808 | +0.0808 | +0.3659 | 0.86 | 1/8 | 1.04 | 1.45 | `rbreaker_buy_setup_proximity_early` (2.51) | +0.0011 | -0.0846 |
| `combo_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0925 | -0.0315 | -0.0315 | -1.8589 | 0.78 | 0/8 | 1.36 | 0.99 | `first_bar_sentiment` (1.06) | +0.0000 | +0.0613 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0892 | -0.0225 | -0.0225 | -1.2669 | 0.71 | 0/8 | 1.55 | 1.00 | `max_up_ret` (0.94) | +0.0003 | -0.0176 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0804 | -0.0091 | -0.0091 | -1.2289 | 0.89 | 1/8 | 1.72 | 1.87 | `rbreaker_sell_setup_proximity_early` (1.21) | -0.0000 | +0.0613 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0971 | +0.0259 | +0.0259 | -0.2846 | 0.85 | 1/8 | 1.00 | 0.98 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0003 | -0.0846 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0996 | +0.0244 | +0.0244 | -0.2554 | 0.89 | 1/8 | 1.26 | 1.41 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0000 | -0.0846 |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0854 | +0.0685 | +0.0685 | -0.2790 | 0.93 | 1/8 | 1.11 | 1.40 | `rbreaker_buy_setup_proximity_early` (2.51) | +0.0011 | -0.0846 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0914 | -0.0344 | -0.0344 | -1.3884 | 0.80 | 0/8 | 2.24 | 1.26 | `volume_weighted_price_position` (1.24) | -0.0001 | -0.0637 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.0742 | -0.0463 | -0.0463 | -1.8589 | 0.94 | 1/8 | 2.29 | 2.13 | — | -0.0007 | +0.0613 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.0963 | +0.0592 | +0.0592 | +0.5373 | 0.72 | 0/8 | 1.01 | 0.58 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0011 | +0.0000 |
| `combo_max__first_bar_return__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0790 | +0.0104 | +0.0104 | -0.1272 | 0.99 | 2/8 | 0.80 | 1.03 | `volume_surge_direction` (1.10) | +0.0001 | -0.0176 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0979 | -0.0009 | -0.0009 | -1.0800 | 0.84 | 0/8 | 1.36 | 0.87 | `volume_weighted_price_position` (1.24) | +0.0005 | -0.0637 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0907 | -0.0214 | -0.0214 | -0.7372 | 0.86 | 1/8 | 1.55 | 0.78 | `volume_weighted_price_position` (1.24) | -0.0002 | -0.0637 |
| `combo_max__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0732 | -0.0158 | -0.0158 | -0.6017 | 1.00 | 2/8 | 1.63 | 1.61 | `volume_surge_direction` (1.10) | +0.0001 | +0.0613 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0959 | -0.0157 | -0.0157 | -1.4403 | 0.74 | 0/8 | 1.48 | 1.09 | `max_up_ret` (0.94) | -0.0000 | -0.0176 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0847 | -0.0151 | -0.0151 | -0.9549 | 0.94 | 1/8 | 1.42 | 0.79 | `volume_weighted_price_position` (1.24) | +0.0002 | -0.0637 |
| `combo_max__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0896 | -0.0191 | -0.0191 | -0.9779 | 0.90 | 2/8 | 1.57 | 0.80 | `volume_weighted_price_position` (1.24) | -0.0001 | -0.0637 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0953 | +0.0168 | +0.0168 | -0.5135 | 0.81 | 1/8 | 1.27 | 0.77 | `volume_weighted_price_position` (1.24) | -0.0001 | -0.0637 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0893 | -0.0136 | -0.0136 | -1.9227 | 0.65 | 0/8 | 0.93 | 0.68 | `volume_weighted_price_position` (1.24) | -0.0003 | +0.0000 |
| `combo_rank_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0906 | -0.0223 | -0.0223 | -1.1680 | 0.69 | 0/8 | 1.62 | 1.14 | `max_up_ret` (0.94) | +0.0003 | -0.0176 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0805 | -0.0388 | -0.0388 | -0.9976 | 0.95 | 0/8 | 2.70 | 1.68 | `volume_weighted_price_position` (1.24) | -0.0003 | -0.0176 |
| `bar_body_rng_0` | Other Technical | +1 | +0.0921 | +0.0209 | +0.0209 | -0.8416 | 0.77 | 1/8 | 1.22 | 0.81 | — | +0.0005 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0843 | +0.0158 | +0.0158 | -0.4533 | 0.78 | 1/8 | 1.00 | 1.31 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0002 | -0.2278 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0932 | -0.0275 | -0.0275 | -0.8062 | 0.90 | 1/8 | 1.78 | 1.30 | `volume_weighted_price_position` (1.24) | -0.0002 | +0.0000 |
| `combo_max__bar_body_rng_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0806 | +0.0347 | +0.0347 | -0.0398 | 0.80 | 1/8 | 0.96 | 0.89 | `volume_surge_direction` (1.10) | +0.0005 | -0.0176 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0969 | +0.0559 | +0.0559 | +0.3783 | 0.69 | 0/8 | 0.92 | 0.63 | `star50_limit_proximity_early` (1.49) | +0.0012 | +0.0000 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0926 | -0.0061 | -0.0061 | -1.6781 | 0.97 | 1/8 | 1.37 | 0.79 | `volume_weighted_price_position` (1.24) | -0.0003 | -0.0176 |
| `combo_mean__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0851 | -0.0027 | -0.0027 | -0.4291 | 0.78 | 1/8 | 1.52 | 1.29 | `volume_surge_direction` (1.10) | -0.0005 | +0.0613 |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0923 | +0.0113 | +0.0113 | -0.6406 | 0.90 | 1/8 | 1.18 | 1.21 | `volume_surge_direction` (1.10) | -0.0001 | +0.0613 |
| `combo_min__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0854 | +0.0128 | +0.0128 | -0.5403 | 0.79 | 1/8 | 1.32 | 1.09 | `volume_surge_direction` (1.10) | -0.0001 | +0.0613 |
| `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.0894 | +0.0077 | +0.0077 | -0.4907 | 0.73 | 0/8 | 1.00 | 0.69 | `star50_limit_proximity_early` (1.49) | +0.0001 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0956 | -0.0082 | -0.0082 | -0.8893 | 0.90 | 1/8 | 1.46 | 1.59 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0000 | +0.0613 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0827 | +0.0463 | +0.0463 | -0.4058 | 1.00 | 1/8 | 1.24 | 1.88 | `rbreaker_buy_setup_proximity_early` (2.51) | +0.0003 | -0.0846 |
| `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0903 | +0.0073 | +0.0073 | -0.4890 | 0.90 | 2/8 | 1.31 | 0.92 | `volume_weighted_price_position` (1.24) | -0.0001 | -0.0176 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0875 | +0.0300 | +0.0300 | -0.0790 | 0.85 | 1/8 | 1.16 | 0.97 | `volume_surge_direction` (1.10) | +0.0001 | +0.0613 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0834 | -0.0217 | -0.0217 | -1.1078 | 0.95 | 1/8 | 2.87 | 2.38 | `volume_weighted_price_position` (1.24) | -0.0002 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0858 | +0.0164 | +0.0164 | -0.3387 | 0.93 | 1/8 | 1.41 | 1.28 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0002 | +0.0613 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0927 | +0.0040 | +0.0040 | -0.9717 | 0.88 | 1/8 | 1.28 | 0.85 | `opening_drive_thrust_ratio` (0.93) | -0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0927 | +0.0081 | +0.0081 | +0.1648 | 0.89 | 1/8 | 1.35 | 1.02 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0002 | +0.0613 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0985 | -0.0211 | -0.0211 | -0.9725 | 0.83 | 1/8 | 1.37 | 1.26 | `opening_drive_thrust_ratio` (0.93) | -0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1028 | +0.0326 | +0.0326 | +0.1677 | 0.80 | 1/8 | 1.10 | 0.75 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0006 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.0874 | +0.0007 | +0.0007 | -0.8124 | 0.67 | 0/8 | 0.93 | 0.68 | — | +0.0000 | -0.0637 |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0924 | -0.0176 | -0.0176 | -1.2814 | 0.81 | 1/8 | 1.16 | 1.15 | `max_up_ret` (0.94) | -0.0008 | +0.0613 |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0918 | +0.0258 | +0.0258 | -0.9326 | 0.96 | 2/8 | 1.24 | 0.86 | `volume_weighted_price_position` (1.24) | +0.0004 | -0.0176 |
| `combo_max__opening_drive_thrust_ratio__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0872 | -0.0044 | -0.0044 | +0.2788 | 0.97 | 1/8 | 1.33 | 1.57 | `volume_surge_direction` (1.10) | +0.0002 | +0.0613 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0840 | +0.0303 | +0.0303 | -0.4943 | 0.99 | 1/8 | 1.07 | 0.93 | `volume_surge_direction` (1.10) | +0.0004 | +0.0613 |
| `combo_mean__first_bar_return__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0874 | +0.0007 | +0.0007 | -0.8124 | 0.67 | 0/8 | 0.93 | 0.68 | `first_bar_sentiment` (1.06) | -0.0002 | -0.0637 |
| `combo_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0790 | -0.0256 | -0.0256 | -1.1985 | 0.80 | 1/8 | 1.24 | 1.22 | `max_up_ret` (0.94) | -0.0004 | +0.0613 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0951 | +0.0185 | +0.0185 | -0.4405 | 0.77 | 1/8 | 1.21 | 0.89 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0004 | +0.0613 |
| `combo_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0858 | -0.0154 | -0.0154 | -1.0675 | 0.75 | 1/8 | 1.65 | 1.25 | `first_bar_sentiment` (1.06) | -0.0005 | +0.0613 |
| `combo_min__first_bar_return__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0812 | +0.0184 | +0.0184 | -0.4276 | 0.74 | 1/8 | 0.98 | 0.57 | `volume_surge_direction` (1.10) | -0.0002 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0722 | -0.0117 | -0.0117 | -0.5740 | 0.99 | 2/8 | 1.59 | 1.67 | `volume_surge_direction` (1.10) | +0.0002 | +0.0613 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0964 | -0.0284 | -0.0284 | -0.8306 | 0.67 | 0/8 | 1.60 | 1.23 | `max_up_ret` (0.94) | -0.0002 | +0.0613 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0992 | -0.0123 | -0.0123 | -1.3041 | 0.82 | 1/8 | 1.35 | 1.21 | `opening_drive_thrust_ratio` (0.93) | +0.0003 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0904 | -0.0056 | -0.0056 | -0.8552 | 0.96 | 1/8 | 1.38 | 1.09 | `first_bar_sentiment` (1.06) | +0.0001 | +0.0000 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0887 | -0.0374 | -0.0374 | -2.5227 | 0.88 | 1/8 | 1.47 | 1.36 | `volume_weighted_price_position` (1.24) | -0.0001 | +0.0613 |
| `combo_tri_median__smooth_momentum_structure__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0744 | -0.0269 | -0.0269 | -0.8830 | 0.93 | 1/8 | 4.11 | 1.47 | `volume_weighted_price_position` (1.24) | +0.0000 | -0.0637 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.1039 | +0.0133 | +0.0133 | -0.4840 | 0.78 | 1/8 | 1.10 | 1.15 | `star50_limit_proximity_early` (1.49) | +0.0004 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0768 | +0.0753 | +0.0753 | -0.1501 | 0.98 | 2/8 | 1.48 | 0.96 | `star50_limit_proximity_early` (1.49) | +0.0009 | -0.0846 |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0943 | +0.0006 | +0.0006 | -0.8981 | 0.82 | 1/8 | 1.75 | 1.02 | `volume_weighted_price_position` (1.24) | +0.0001 | +0.0000 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0712 | -0.0410 | -0.0410 | -2.2126 | 0.88 | 1/8 | 2.77 | 2.89 | `max_up_ret` (0.94) | -0.0007 | +0.0613 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0528 | -0.0133 | -0.0133 | -1.5530 | 0.65 | 0/8 | 0.75 | 0.49 | `double_bottom_bull_flag_early` (1.91) | -0.0003 | -0.1923 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0732 | +0.0205 | +0.0205 | -0.8741 | 0.75 | 1/8 | 1.79 | 0.65 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0005 | -0.0176 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0589 | +0.0244 | +0.0244 | -0.8744 | 0.87 | 1/8 | 2.02 | 1.52 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0001 | -0.0846 |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0812 | -0.0077 | -0.0077 | -0.7220 | 0.96 | 2/8 | 1.11 | 0.58 | `volume_weighted_price_position` (1.24) | -0.0000 | -0.0637 |
| `volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0791 | +0.0000 | +0.0000 | -0.4047 | 1.24 | 2/8 | 2.38 | 0.88 | — | +0.0006 | -0.0637 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0805 | +0.0217 | +0.0217 | -0.2987 | 0.92 | 2/8 | 1.83 | 1.00 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0004 | +0.0000 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0889 | -0.0338 | -0.0338 | -1.4374 | 0.78 | 0/8 | 1.70 | 1.41 | `max_up_ret` (0.94) | -0.0005 | +0.0613 |
| `combo_ratio__bar_ret_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0796 | -0.0090 | -0.0090 | -0.5472 | 0.71 | 1/8 | 1.09 | 0.60 | `volume_surge_direction` (1.10) | +0.0000 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0757, Sharpe: +0.2645)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1474 | +0.0406 | +0.0406 | -1.4083 | 0.29 | 0/8 | 0.79 | 0.61 | `opening_drive_thrust_ratio` (0.32) | -0.0002 | +0.0945 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1315 | +0.0849 | +0.0849 | -0.1619 | 0.25 | 0/8 | 0.83 | 0.71 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.1689 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1404 | +0.0942 | +0.0942 | -0.2127 | 0.33 | 0/8 | 0.63 | 0.45 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0945 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1292 | +0.0469 | +0.0469 | -1.2311 | 0.36 | 0/8 | 0.79 | 0.56 | `bar_ret_0` (0.46) | +0.0002 | +0.1328 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1476 | +0.0426 | +0.0426 | -0.2324 | 0.38 | 0/8 | 0.66 | 0.57 | `volume_weighted_momentum_acceleration` (0.47) | -0.0000 | +0.0000 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1540 | +0.0316 | +0.0316 | -0.2324 | 0.40 | 0/8 | 0.66 | 0.60 | `volume_weighted_momentum_acceleration` (0.47) | -0.0001 | -0.0149 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1144 | +0.0933 | +0.0933 | -0.2396 | 0.32 | 0/8 | 0.68 | 0.52 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0007 | +0.0751 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1545 | +0.0289 | +0.0289 | -0.4555 | 0.40 | 0/8 | 0.65 | 0.59 | `volume_weighted_momentum_acceleration` (0.47) | -0.0004 | +0.0000 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1301 | +0.0518 | +0.0518 | -0.2853 | 0.51 | 0/8 | 0.55 | 0.33 | `max_down_ret` (0.55) | -0.0001 | +0.2267 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1359 | +0.0534 | +0.0534 | -1.3411 | 0.39 | 0/8 | 0.74 | 0.54 | `volatility_expansion_trend_vector` (0.36) | -0.0000 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1523 | +0.0478 | +0.0478 | -0.8584 | 0.37 | 0/8 | 0.63 | 0.49 | `first_bar_return` (0.46) | +0.0000 | +0.1328 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1453 | +0.0883 | +0.0883 | -0.5698 | 0.42 | 0/8 | 0.62 | 0.67 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0004 | -0.0812 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1364 | +0.0337 | +0.0337 | -1.4167 | 0.28 | 0/8 | 0.73 | 0.62 | `trend_bar_close_consistency` (0.54) | -0.0003 | +0.0000 |
| `combo_min__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1151 | +0.0647 | +0.0647 | -0.2556 | 0.33 | 0/8 | 0.76 | 0.59 | `first_bar_return` (0.46) | +0.0002 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1323 | +0.0308 | +0.0308 | -1.6524 | 0.28 | 0/8 | 0.90 | 0.61 | — | -0.0001 | +0.1193 |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1373 | +0.0231 | +0.0231 | -2.4234 | 0.30 | 0/8 | 0.82 | 0.53 | `bar_ret_0` (0.46) | -0.0002 | +0.0000 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1388 | +0.0527 | +0.0527 | -0.1565 | 0.34 | 0/8 | 0.65 | 0.55 | `volume_weighted_momentum_acceleration` (0.47) | +0.0001 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1248 | +0.0390 | +0.0390 | -0.6507 | 0.35 | 0/8 | 0.81 | 0.64 | `trend_bar_close_consistency` (0.54) | -0.0003 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1050 | +0.0817 | +0.0817 | +0.3027 | 0.40 | 0/8 | 0.65 | 0.51 | `trend_bar_close_consistency` (0.54) | +0.0006 | +0.0751 |
| `combo_min__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1032 | +0.0525 | +0.0525 | -0.4214 | 0.33 | 0/8 | 0.89 | 0.70 | `close_vs_open_range` (0.39) | -0.0001 | +0.0945 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1447 | +0.0453 | +0.0453 | -0.8924 | 0.31 | 0/8 | 0.76 | 0.65 | `opening_drive_thrust_ratio` (0.32) | -0.0000 | +0.0945 |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1141 | +0.0503 | +0.0503 | -1.5796 | 0.30 | 0/8 | 0.95 | 0.52 | `first_bar_sentiment` (0.43) | -0.0002 | +0.0000 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1355 | +0.0297 | +0.0297 | -1.4140 | 0.31 | 0/8 | 0.82 | 0.56 | `first_bar_sentiment` (0.43) | +0.0001 | +0.0945 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1496 | +0.0719 | +0.0719 | -0.4456 | 0.27 | 0/8 | 0.71 | 0.61 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0945 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1133 | +0.0560 | +0.0560 | -1.0726 | 0.20 | 0/8 | 1.00 | 0.83 | `volume_weighted_momentum_acceleration` (0.47) | -0.0000 | +0.0945 |
| `combo_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1404 | +0.0418 | +0.0418 | +0.2392 | 0.32 | 0/8 | 0.63 | 0.55 | `body_size_progression` (0.46) | -0.0001 | +0.1193 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1462 | +0.0573 | +0.0573 | -0.2479 | 0.33 | 0/8 | 0.67 | 0.59 | `volume_weighted_momentum_acceleration` (0.47) | +0.0002 | +0.0626 |
| `combo_mean__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1375 | +0.0281 | +0.0281 | -0.9455 | 0.32 | 0/8 | 0.76 | 0.55 | `first_bar_return` (0.46) | -0.0002 | +0.0248 |
| `combo_max__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1359 | +0.0235 | +0.0235 | -2.7519 | 0.31 | 0/8 | 0.80 | 0.51 | `first_bar_return` (0.46) | -0.0005 | -0.0077 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1406 | +0.0419 | +0.0419 | +0.0059 | 0.31 | 0/8 | 0.63 | 0.58 | `body_size_progression` (0.46) | -0.0003 | +0.0945 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1475 | +0.0857 | +0.0857 | +0.3857 | 0.34 | 0/8 | 0.60 | 0.48 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.1689 |
| `combo_mean__trend_bar_close_consistency__bar_ret_0` | Other Technical | +1 | +0.1128 | +0.0378 | +0.0378 | -0.8881 | 0.35 | 0/8 | 0.75 | 0.55 | `trend_bar_close_consistency` (0.54) | -0.0000 | -0.0319 |
| `combo_rank_max__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1288 | +0.0469 | +0.0469 | -1.4510 | 0.34 | 0/8 | 0.83 | 0.59 | `max_up_ret` (0.28) | +0.0003 | +0.0945 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1353 | +0.0288 | +0.0288 | -1.9401 | 0.31 | 0/8 | 0.92 | 0.66 | `bar_ret_0` (0.46) | -0.0002 | +0.0945 |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1131 | +0.1060 | +0.1060 | +0.3487 | 0.39 | 0/8 | 0.78 | 0.66 | `star50_limit_proximity_early` (0.50) | +0.0009 | +0.1689 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1160 | +0.0404 | +0.0404 | -0.4576 | 0.46 | 0/8 | 0.55 | 0.43 | — | +0.0001 | +0.0248 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1271 | +0.0550 | +0.0550 | -0.9817 | 0.32 | 0/8 | 0.82 | 0.69 | `close_vs_open_range` (0.39) | -0.0001 | +0.0945 |
| `combo_rank_max__trend_bar_close_consistency__bar_ret_0` | Other Technical | +1 | +0.1192 | +0.0084 | +0.0084 | -2.1446 | 0.35 | 0/8 | 0.76 | 0.57 | `trend_bar_close_consistency` (0.54) | -0.0001 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1228 | +0.0958 | +0.0958 | +0.5075 | 0.45 | 0/8 | 0.41 | 0.41 | `bar_ret_0` (0.46) | +0.0002 | +0.0751 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1529 | +0.0388 | +0.0388 | -1.1420 | 0.30 | 0/8 | 0.81 | 0.55 | `bar_ret_0` (0.46) | -0.0003 | +0.0000 |
| `combo_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1180 | +0.0186 | +0.0186 | -2.2632 | 0.37 | 0/8 | 0.74 | 0.49 | `bar_ret_0` (0.46) | -0.0005 | +0.1002 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1361 | +0.0867 | +0.0867 | +0.2984 | 0.35 | 0/8 | 0.74 | 0.63 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0001 | -0.0812 |
| `combo_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1206 | +0.0254 | +0.0254 | -1.5318 | 0.38 | 0/8 | 0.80 | 0.59 | `early_body_momentum` (0.34) | +0.0000 | +0.1002 |
| `combo_rank_min__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1137 | +0.0706 | +0.0706 | -0.6439 | 0.36 | 0/8 | 0.71 | 0.54 | `first_bar_return` (0.46) | -0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1188 | +0.1095 | +0.1095 | +0.7916 | 0.40 | 0/8 | 0.71 | 0.58 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0008 | +0.0751 |
| `combo_mean__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1160 | +0.0404 | +0.0404 | -0.4576 | 0.46 | 0/8 | 0.55 | 0.43 | `bar_ret_0` (0.46) | +0.0005 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1347 | +0.0639 | +0.0639 | -0.6077 | 0.46 | 0/8 | 0.49 | 0.41 | `first_bar_return` (0.46) | +0.0003 | +0.0945 |
| `combo_mean__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1186 | +0.0519 | +0.0519 | -0.8017 | 0.27 | 0/8 | 0.83 | 0.60 | `first_bar_sentiment` (0.43) | +0.0002 | +0.1689 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1526 | +0.0524 | +0.0524 | -0.6914 | 0.28 | 0/8 | 0.82 | 0.65 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0003 | +0.0945 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1415 | +0.1136 | +0.1136 | +0.6574 | 0.36 | 0/8 | 0.58 | 0.58 | `star50_limit_proximity_early` (0.50) | +0.0005 | +0.0751 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1315 | +0.0419 | +0.0419 | -1.0138 | 0.26 | 0/8 | 0.90 | 0.75 | `trend_day_regime_conviction` (0.39) | -0.0002 | +0.0945 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1415 | +0.0589 | +0.0589 | -0.5615 | 0.34 | 0/8 | 0.57 | 0.55 | `body_size_progression` (0.46) | +0.0002 | +0.0945 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1512 | +0.0376 | +0.0376 | -1.6484 | 0.30 | 0/8 | 0.81 | 0.53 | `opening_drive_thrust_ratio` (0.32) | -0.0002 | +0.0945 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1055 | +0.1051 | +0.1051 | -0.1201 | 0.40 | 0/8 | 0.69 | 0.56 | `star50_limit_proximity_early` (0.50) | +0.0010 | -0.0324 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1151 | +0.0336 | +0.0336 | -1.0604 | 0.33 | 0/8 | 0.89 | 0.63 | `trend_bar_close_consistency` (0.54) | -0.0001 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1444 | +0.0393 | +0.0393 | -1.9156 | 0.33 | 0/8 | 0.74 | 0.53 | `opening_drive_thrust_ratio` (0.32) | -0.0003 | +0.1941 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1205 | +0.0959 | +0.0959 | +0.4192 | 0.31 | 0/8 | 0.84 | 0.66 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0007 | +0.0751 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1395 | +0.0550 | +0.0550 | +0.1707 | 0.44 | 0/8 | 0.61 | 0.50 | `max_down_ret` (0.55) | +0.0002 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1154 | +0.1143 | +0.1143 | +1.3960 | 0.45 | 0/8 | 0.44 | 0.46 | `star50_limit_proximity_early` (0.50) | +0.0007 | +0.0945 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1421 | +0.0525 | +0.0525 | -0.9776 | 0.28 | 0/8 | 0.95 | 0.60 | `body_size_progression` (0.46) | +0.0001 | +0.0945 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1263 | +0.0480 | +0.0480 | -0.2807 | 0.41 | 0/8 | 0.67 | 0.47 | `opening_drive_thrust_ratio` (0.32) | +0.0001 | +0.0626 |
| `combo_mean__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1199 | +0.0745 | +0.0745 | +0.2028 | 0.45 | 0/8 | 0.59 | 0.42 | `max_down_ret` (0.55) | +0.0000 | +0.0000 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1330 | +0.1065 | +0.1065 | +0.7497 | 0.40 | 0/8 | 0.50 | 0.53 | `star50_limit_proximity_early` (0.50) | +0.0008 | +0.0751 |
| `combo_rank_min__opening_drive_thrust_ratio__trend_day_regime_conviction` | Other Technical | +1 | +0.1316 | +0.0457 | +0.0457 | -0.2159 | 0.31 | 0/8 | 0.84 | 0.66 | `trend_day_regime_conviction` (0.39) | -0.0001 | +0.0945 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1129 | +0.0531 | +0.0531 | +0.0725 | 0.44 | 0/8 | 0.54 | 0.42 | `bar_ret_0` (0.46) | +0.0002 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1250 | +0.0700 | +0.0700 | +0.3994 | 0.36 | 0/8 | 0.61 | 0.53 | `late_bar_momentum` (0.53) | +0.0003 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1398 | +0.0541 | +0.0541 | -0.5111 | 0.32 | 0/8 | 0.74 | 0.51 | `first_bar_sentiment` (0.43) | +0.0003 | +0.0945 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1153 | +0.1117 | +0.1117 | +1.3824 | 0.46 | 0/8 | 0.43 | 0.45 | `star50_limit_proximity_early` (0.50) | +0.0005 | +0.0945 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1207 | +0.0921 | +0.0921 | +0.3192 | 0.46 | 0/8 | 0.40 | 0.39 | `first_bar_return` (0.46) | +0.0005 | +0.0751 |
| `combo_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1452 | +0.0498 | +0.0498 | -0.3399 | 0.33 | 0/8 | 0.68 | 0.66 | `smooth_momentum_structure` (0.46) | +0.0002 | +0.0945 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1329 | +0.1041 | +0.1041 | +0.7497 | 0.40 | 0/8 | 0.50 | 0.53 | `star50_limit_proximity_early` (0.50) | +0.0008 | +0.0751 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_day_regime_conviction` | Other Technical | +1 | +0.1277 | +0.0287 | +0.0287 | -0.6970 | 0.35 | 0/8 | 0.65 | 0.55 | `trend_day_regime_conviction` (0.39) | -0.0001 | +0.0000 |
| `combo_rank_max__early_body_momentum__max_down_ret` | Intraday Range Momentum | +1 | +0.1047 | +0.0580 | +0.0580 | -0.1094 | 0.43 | 0/8 | 0.68 | 0.48 | `max_down_ret` (0.55) | +0.0003 | +0.0000 |
| `combo_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1127 | +0.0594 | +0.0594 | -0.8629 | 0.27 | 0/8 | 1.20 | 0.85 | `close_vs_open_range` (0.39) | -0.0001 | +0.0945 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1399 | +0.0458 | +0.0458 | -0.3399 | 0.35 | 0/8 | 0.66 | 0.66 | `smooth_momentum_structure` (0.46) | +0.0002 | +0.0000 |
| `combo_min__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1038 | +0.0798 | +0.0798 | -0.2027 | 0.45 | 0/8 | 0.70 | 0.61 | `first_bar_return` (0.46) | +0.0004 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0954 | +0.0970 | +0.0970 | +0.1808 | 0.55 | 0/8 | 0.56 | 0.45 | `max_down_ret` (0.55) | +0.0007 | +0.0751 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1239 | +0.0383 | +0.0383 | -0.5921 | 0.40 | 0/8 | 0.69 | 0.52 | `trend_bar_close_consistency` (0.54) | -0.0001 | -0.0319 |
| `combo_rank_max__net_volume_flow__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1128 | +0.0538 | +0.0538 | -1.1112 | 0.29 | 0/8 | 1.00 | 0.68 | `close_vs_open_range` (0.39) | -0.0000 | +0.0000 |
| `combo_rank_min__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1223 | +0.0429 | +0.0429 | -0.2027 | 0.46 | 0/8 | 0.52 | 0.39 | `first_bar_return` (0.46) | -0.0002 | -0.0395 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.1138 | +0.1138 | +0.2628 | 0.41 | 0/8 | 0.83 | 0.74 | `star50_limit_proximity_early` (0.50) | +0.0007 | +0.0675 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1276 | +0.0593 | +0.0593 | -0.7951 | 0.49 | 0/8 | 0.46 | 0.38 | `bar_ret_0` (0.46) | +0.0000 | +0.0000 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1172 | +0.1093 | +0.1093 | +0.3039 | 0.41 | 0/8 | 0.77 | 0.72 | `star50_limit_proximity_early` (0.50) | +0.0009 | +0.1689 |
| `combo_mean__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1136 | +0.0666 | +0.0666 | -0.3458 | 0.34 | 0/8 | 0.74 | 0.57 | `max_down_ret` (0.55) | +0.0002 | +0.1689 |
| `combo_min__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1142 | +0.1001 | +0.1001 | -0.0297 | 0.34 | 0/8 | 0.82 | 0.62 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0007 | +0.0751 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1203 | +0.1107 | +0.1107 | +1.2537 | 0.40 | 0/8 | 0.50 | 0.50 | `star50_limit_proximity_early` (0.50) | +0.0004 | +0.0751 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1289 | +0.0715 | +0.0715 | +0.4915 | 0.48 | 0/8 | 0.56 | 0.32 | `max_down_ret` (0.55) | -0.0000 | +0.0000 |
| `combo_max__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.0958 | +0.0413 | +0.0413 | -0.2764 | 0.37 | 0/8 | 1.11 | 0.76 | `close_vs_open_range` (0.39) | -0.0002 | +0.0751 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.0998 | +0.0636 | +0.0636 | -0.1214 | 0.40 | 0/8 | 0.79 | 0.65 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0002 | -0.0319 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1086 | +0.0610 | +0.0610 | -0.3371 | 0.31 | 0/8 | 1.13 | 0.80 | `close_vs_open_range` (0.39) | -0.0001 | +0.0945 |
| `combo_min__trend_bar_close_consistency__bar_ret_0` | Other Technical | +1 | +0.0936 | +0.0619 | +0.0619 | -0.1417 | 0.43 | 0/8 | 0.76 | 0.63 | `trend_bar_close_consistency` (0.54) | +0.0003 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1154 | +0.0205 | +0.0205 | -0.7130 | 0.57 | 0/8 | 0.65 | 0.35 | `bar_ret_0` (0.46) | -0.0004 | +0.0248 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1260 | +0.0219 | +0.0219 | -1.0362 | 0.36 | 0/8 | 0.70 | 0.60 | `close_vs_open_range` (0.39) | -0.0001 | -0.0324 |
| `open_to_current_return` | Intraday Range Momentum | +1 | +0.1077 | +0.0435 | +0.0435 | -0.2385 | 0.34 | 0/8 | 0.97 | 0.64 | — | -0.0002 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction` | Intraday Range Momentum | +1 | +0.1021 | +0.0538 | +0.0538 | -0.3178 | 0.38 | 0/8 | 0.91 | 0.72 | `volume_weighted_momentum_acceleration` (0.47) | -0.0003 | +0.0000 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1250 | +0.0435 | +0.0435 | +0.0483 | 0.42 | 0/8 | 0.55 | 0.37 | `first_bar_sentiment` (0.43) | +0.0002 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1081 | +0.0706 | +0.0706 | -0.3313 | 0.37 | 0/8 | 0.85 | 0.69 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0004 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1205 | +0.1502 | +0.1502 | +1.1714 | 0.35 | 0/8 | 0.72 | 0.86 | `max_down_ret` (0.55) | +0.0008 | +0.0751 |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1023 | +0.0313 | +0.0313 | -1.0053 | 0.32 | 0/8 | 1.07 | 0.69 | `first_bar_sentiment` (0.43) | +0.0001 | +0.0945 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1125 | +0.0290 | +0.0290 | -0.5714 | 0.31 | 0/8 | 0.92 | 0.80 | `early_body_momentum` (0.34) | -0.0004 | -0.0319 |
| `combo_min__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1028 | +0.0291 | +0.0291 | -0.6661 | 0.31 | 0/8 | 1.20 | 0.80 | `trend_bar_close_consistency` (0.54) | -0.0005 | +0.0945 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.1068 | +0.0484 | +0.0484 | -0.3058 | 0.32 | 0/8 | 0.97 | 0.64 | — | +0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1368 | +0.0707 | +0.0707 | +0.2615 | 0.36 | 0/8 | 0.67 | 0.50 | `max_down_ret` (0.55) | +0.0002 | +0.0945 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0903 | +0.0246 | +0.0246 | -0.5104 | 0.55 | 0/8 | 0.41 | 0.34 | `first_bar_return` (0.46) | -0.0001 | +0.0248 |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1064 | +0.0528 | +0.0528 | -0.4408 | 0.33 | 0/8 | 0.79 | 0.60 | `trend_bar_close_consistency` (0.54) | -0.0002 | +0.0000 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | Intraday Range Momentum | +1 | +0.1028 | +0.0438 | +0.0438 | -0.8237 | 0.20 | 0/8 | 1.36 | 0.96 | `body_size_progression` (0.46) | -0.0002 | +0.0945 |
| `combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1208 | +0.0471 | +0.0471 | -0.3148 | 0.28 | 0/8 | 0.71 | 0.63 | `smooth_momentum_structure` (0.46) | +0.0004 | +0.0945 |
| `num_up_bars` | Other Technical | +1 | +0.0907 | +0.0459 | +0.0459 | -1.1323 | 0.40 | 0/8 | 1.47 | 1.31 | — | +0.0001 | +0.0945 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1074 | +0.0923 | +0.0923 | -0.6750 | 0.46 | 0/8 | 0.65 | 0.48 | `star50_limit_proximity_early` (0.50) | +0.0000 | -0.0324 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1088 | +0.0938 | +0.0938 | -0.4554 | 0.46 | 0/8 | 0.73 | 0.54 | `star50_limit_proximity_early` (0.50) | +0.0007 | +0.0000 |
| `combo_max__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1114 | +0.0486 | +0.0486 | -0.2505 | 0.44 | 0/8 | 0.68 | 0.51 | `max_down_ret` (0.55) | -0.0004 | +0.0626 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1087 | +0.1327 | +0.1327 | +0.9157 | 0.54 | 0/8 | 0.62 | 0.54 | `max_down_ret` (0.55) | +0.0008 | +0.0000 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0995 | -0.0041 | -0.0041 | -1.9661 | 0.29 | 0/8 | 1.40 | 0.96 | — | -0.0005 | -0.0713 |
| `combo_mean__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1113 | +0.0829 | +0.0829 | +0.2652 | 0.41 | 0/8 | 0.62 | 0.40 | `max_down_ret` (0.55) | +0.0001 | +0.0000 |
| `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression` | Volatility & Oscillators | +1 | +0.0487 | +0.0730 | +0.0730 | +0.4368 | 0.71 | 1/8 | 0.67 | 0.42 | `star50_limit_proximity_early` (0.50) | +0.0003 | +0.0751 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.0822 | +0.1006 | +0.1006 | +0.1239 | 0.60 | 0/8 | 0.58 | 0.44 | `smooth_momentum_structure` (0.46) | +0.0010 | +0.0751 |
| `combo_min__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1029 | +0.0600 | +0.0600 | -1.2291 | 0.22 | 0/8 | 1.03 | 0.73 | `first_bar_sentiment` (0.43) | +0.0002 | +0.0000 |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1024 | +0.0279 | +0.0279 | -0.5752 | 0.41 | 0/8 | 0.95 | 0.56 | `first_bar_return` (0.46) | +0.0002 | +0.1328 |
| `combo_min__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1111 | +0.0883 | +0.0883 | -0.0326 | 0.40 | 0/8 | 0.73 | 0.56 | `max_down_ret` (0.55) | +0.0004 | +0.0000 |
| `combo_max__close_vs_open_range__max_down_ret` | Intraday Range Momentum | +1 | +0.1039 | +0.0557 | +0.0557 | -0.2026 | 0.44 | 0/8 | 0.71 | 0.52 | `max_down_ret` (0.55) | -0.0003 | -0.0324 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.0967 | +0.0654 | +0.0654 | -0.4161 | 0.45 | 0/8 | 0.80 | 0.64 | `trend_bar_close_consistency` (0.54) | +0.0005 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1011 | +0.0944 | +0.0944 | -0.6509 | 0.54 | 0/8 | 1.10 | 1.03 | `star50_limit_proximity_early` (0.50) | +0.0005 | +0.0573 |
| `combo_max__trend_day_regime_conviction__max_down_ret` | Intraday Range Momentum | +1 | +0.1033 | +0.0497 | +0.0497 | -0.7292 | 0.47 | 0/8 | 0.69 | 0.52 | `max_down_ret` (0.55) | -0.0001 | +0.0000 |
| `combo_tri_max__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0978 | +0.0756 | +0.0756 | -0.7698 | 0.47 | 0/8 | 0.65 | 0.52 | `trend_bar_close_consistency` (0.54) | +0.0003 | -0.0319 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1090 | +0.0661 | +0.0661 | +1.4473 | 0.48 | 1/8 | 0.80 | 0.38 | `volume_weighted_momentum_acceleration` (0.47) | -0.0003 | -0.0395 |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1064 | +0.0290 | +0.0290 | -0.9127 | 0.34 | 0/8 | 1.05 | 0.75 | `first_bar_sentiment` (0.43) | -0.0000 | +0.0000 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1155 | +0.0705 | +0.0705 | -0.3494 | 0.30 | 0/8 | 0.81 | 0.65 | `max_down_ret` (0.55) | +0.0005 | +0.0000 |
| `combo_sig_product__max_up_ret__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1076 | +0.0281 | +0.0281 | -0.8940 | 0.30 | 0/8 | 1.03 | 1.05 | `high_low_sequence_momentum` (0.43) | -0.0005 | +0.0000 |
| `combo_min__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1016 | +0.0728 | +0.0728 | +0.2061 | 0.43 | 0/8 | 0.54 | 0.47 | `max_down_ret` (0.55) | +0.0001 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1036 | +0.1371 | +0.1371 | +0.1462 | 0.50 | 0/8 | 0.81 | 0.93 | `star50_limit_proximity_early` (0.50) | +0.0008 | +0.0356 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0926 | +0.0323 | +0.0323 | -0.2960 | 0.38 | 0/8 | 1.19 | 0.83 | — | +0.0001 | +0.0000 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1130 | +0.0801 | +0.0801 | -0.0633 | 0.45 | 0/8 | 0.68 | 0.51 | `max_down_ret` (0.55) | +0.0003 | +0.0000 |
| `max_down_ret` | Intraday Range Momentum | +1 | +0.1028 | +0.0790 | +0.0790 | +0.1275 | 0.55 | 0/8 | 0.55 | 0.39 | — | +0.0003 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1061 | +0.1335 | +0.1335 | +0.1748 | 0.61 | 1/8 | 1.41 | 1.86 | `star50_limit_proximity_early` (0.50) | +0.0008 | +0.1689 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1035 | +0.0695 | +0.0695 | -0.6436 | 0.34 | 0/8 | 0.94 | 0.63 | `body_size_progression` (0.46) | +0.0001 | +0.0751 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.0953 | +0.0398 | +0.0398 | -0.3845 | 0.38 | 0/8 | 1.12 | 0.88 | — | +0.0005 | +0.0945 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1237 | +0.0937 | +0.0937 | -0.1678 | 0.49 | 0/8 | 0.59 | 0.40 | `star50_limit_proximity_early` (0.50) | +0.0002 | +0.0000 |
| `combo_min__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1042 | +0.0754 | +0.0754 | +0.4070 | 0.36 | 0/8 | 0.70 | 0.57 | `first_bar_sentiment` (0.43) | +0.0004 | +0.0000 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1031 | +0.0291 | +0.0291 | +0.0988 | 0.29 | 0/8 | 0.81 | 0.73 | `first_bar_sentiment` (0.43) | +0.0002 | -0.0319 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0993 | +0.0982 | +0.0982 | +0.3922 | 0.47 | 0/8 | 0.68 | 0.47 | `max_down_ret` (0.55) | +0.0006 | +0.0751 |
| `range_progression_trend` | Other Technical | +1 | +0.0797 | -0.0206 | -0.0206 | -1.6976 | 0.45 | 0/8 | 1.91 | 1.13 | — | -0.0002 | -0.0319 |
| `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression` | Other Technical | +1 | +0.0811 | +0.0189 | +0.0189 | -0.2323 | 0.38 | 0/8 | 1.30 | 1.07 | `trend_bar_close_consistency` (0.54) | -0.0002 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1092 | +0.0212 | +0.0212 | -1.5281 | 0.47 | 0/8 | 1.03 | 0.68 | `volume_weighted_momentum_acceleration` (0.47) | +0.0000 | +0.0945 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1201 | +0.0805 | +0.0805 | +0.0712 | 0.39 | 0/8 | 0.66 | 0.49 | `max_down_ret` (0.55) | +0.0005 | +0.0945 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1016 | +0.0995 | +0.0995 | +1.2591 | 0.50 | 0/8 | 0.58 | 0.42 | `max_down_ret` (0.55) | +0.0007 | +0.0751 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1292 | +0.1068 | +0.1068 | +0.6164 | 0.41 | 0/8 | 0.65 | 0.49 | `star50_limit_proximity_early` (0.50) | +0.0003 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1195 | +0.0813 | +0.0813 | -0.8506 | 0.47 | 0/8 | 0.57 | 0.58 | `max_down_ret` (0.55) | +0.0003 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1070 | +0.0675 | +0.0675 | -0.7673 | 0.52 | 0/8 | 0.66 | 0.41 | `trend_bar_close_consistency` (0.54) | +0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1015 | +0.0505 | +0.0505 | +1.1989 | 0.33 | 0/8 | 0.86 | 0.71 | `body_size_progression` (0.46) | +0.0001 | +0.0945 |
| `combo_rank_min__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1017 | +0.0648 | +0.0648 | +0.0498 | 0.44 | 0/8 | 0.54 | 0.40 | `first_bar_sentiment` (0.43) | +0.0003 | +0.0000 |
| `combo_rank_min__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.0994 | +0.0630 | +0.0630 | +0.1498 | 0.50 | 0/8 | 0.52 | 0.44 | `max_down_ret` (0.55) | +0.0003 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1004 | +0.0838 | +0.0838 | -0.6184 | 0.53 | 0/8 | 1.04 | 0.90 | `star50_limit_proximity_early` (0.50) | +0.0003 | +0.0751 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1022 | +0.1034 | +0.1034 | +1.0177 | 0.50 | 0/8 | 0.50 | 0.34 | `max_down_ret` (0.55) | +0.0002 | +0.0000 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1111 | +0.0553 | +0.0553 | +0.1769 | 0.24 | 0/8 | 1.01 | 0.74 | `early_late_momentum_divergence` (0.53) | -0.0001 | +0.0945 |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1139 | +0.0630 | +0.0630 | +0.0335 | 0.38 | 0/8 | 0.75 | 0.67 | `body_size_progression` (0.46) | +0.0005 | +0.0945 |
| `bar_body_rng_0` | Other Technical | +1 | +0.1136 | +0.0572 | +0.0572 | -0.7848 | 0.37 | 0/8 | 0.62 | 0.48 | — | -0.0001 | +0.1689 |
| `combo_sig_product__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.0967 | +0.0521 | +0.0521 | -0.6353 | 0.49 | 0/8 | 0.48 | 0.50 | `max_down_ret` (0.55) | +0.0000 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.0634 | +0.0335 | +0.0335 | +0.3145 | 0.77 | 1/8 | 0.59 | 0.61 | `trend_bar_close_consistency` (0.54) | +0.0002 | -0.0395 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_day_regime_conviction` | Other Technical | +1 | +0.0532 | +0.0163 | +0.0163 | -1.2828 | 0.95 | 1/8 | 0.53 | 0.28 | `trend_day_regime_conviction` (0.39) | +0.0005 | +0.1689 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1085 | +0.0533 | +0.0533 | +0.0477 | 0.33 | 0/8 | 0.83 | 0.71 | `early_late_momentum_divergence` (0.53) | +0.0001 | +0.0945 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1433, Sharpe: +1.0402)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1386 | +0.1275 | +0.1275 | +0.8333 | 0.55 | 1/8 | 1.05 | 2.29 | `bar_body_rng_0` (0.63) | -0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1387 | +0.1339 | +0.1339 | +0.8863 | 0.56 | 1/8 | 0.84 | 1.69 | `bar_body_rng_0` (0.63) | -0.0003 | -0.2552 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1258 | +0.1203 | +0.1203 | +1.1190 | 0.68 | 1/8 | 0.88 | 2.56 | `first_bar_sentiment` (0.86) | -0.0007 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1207 | +0.1353 | +0.1353 | +0.5812 | 0.67 | 1/8 | 0.98 | 3.46 | `bar_body_rng_0` (0.63) | -0.0002 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1324 | +0.1250 | +0.1250 | +0.7559 | 0.52 | 1/8 | 1.10 | 2.31 | `star50_limit_proximity_early` (0.52) | -0.0000 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1320 | +0.1337 | +0.1337 | +0.9648 | 0.54 | 1/8 | 0.88 | 1.53 | `first_bar_sentiment` (0.86) | -0.0003 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1364 | +0.1428 | +0.1428 | +0.8973 | 0.53 | 1/8 | 0.89 | 1.27 | `bar_body_rng_0` (0.63) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1256 | +0.1258 | +0.1258 | +1.0333 | 0.60 | 0/8 | 1.25 | 2.06 | `volume_weighted_price_position` (0.77) | +0.0000 | -0.1901 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1304 | +0.1296 | +0.1296 | +0.3365 | 0.54 | 1/8 | 0.83 | 1.38 | `first_bar_return` (0.48) | -0.0003 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1413 | +0.1277 | +0.1277 | +1.1407 | 0.50 | 1/8 | 1.07 | 1.68 | `opening_drive_thrust_ratio` (0.46) | -0.0000 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1340 | +0.1346 | +0.1346 | +1.4890 | 0.48 | 0/8 | 1.03 | 1.62 | `bar_body_rng_0` (0.63) | -0.0006 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1332 | +0.1135 | +0.1135 | +0.7682 | 0.34 | 0/8 | 1.26 | 1.74 | `star50_limit_proximity_early` (0.52) | -0.0003 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1235 | +0.0997 | +0.0997 | +0.3365 | 0.62 | 1/8 | 0.79 | 1.43 | `first_bar_sentiment` (0.86) | -0.0006 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1268 | +0.1243 | +0.1243 | +2.0348 | 0.57 | 1/8 | 1.32 | 2.19 | `volume_weighted_price_position` (0.77) | -0.0000 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1335 | +0.1419 | +0.1419 | +0.8351 | 0.57 | 1/8 | 0.94 | 1.74 | `bar_body_rng_0` (0.63) | +0.0002 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1365 | +0.0985 | +0.0985 | +1.0115 | 0.52 | 1/8 | 0.88 | 1.39 | `first_bar_sentiment` (0.86) | -0.0007 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1329 | +0.1289 | +0.1289 | +0.8597 | 0.47 | 0/8 | 1.06 | 1.26 | `bar_body_rng_0` (0.63) | -0.0005 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1289 | +0.1310 | +0.1310 | +1.0164 | 0.51 | 1/8 | 0.95 | 1.34 | `bar_body_rng_0` (0.63) | -0.0000 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1407 | +0.1285 | +0.1285 | +1.1054 | 0.46 | 0/8 | 1.10 | 1.84 | `opening_drive_thrust_ratio` (0.46) | -0.0002 | -0.1900 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1385 | +0.1325 | +0.1325 | +1.0456 | 0.39 | 0/8 | 1.10 | 1.71 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0003 | -0.0669 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1091 | +0.1518 | +0.1518 | +1.0662 | 0.76 | 1/8 | 0.94 | 4.18 | `limit_down_proximity_early` (0.71) | +0.0002 | +0.0000 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1331 | +0.1319 | +0.1319 | +0.2487 | 0.34 | 0/8 | 1.33 | 1.64 | `star50_limit_proximity_early` (0.52) | +0.0004 | +0.0000 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1274 | +0.1198 | +0.1198 | +0.3623 | 0.42 | 0/8 | 1.19 | 1.57 | `demark_setup_reversal_early` (0.51) | -0.0002 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1362 | +0.1319 | +0.1319 | +0.8890 | 0.43 | 0/8 | 1.01 | 1.18 | `volume_weighted_price_position` (0.77) | -0.0003 | -0.0560 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1165 | +0.1356 | +0.1356 | +0.6928 | 0.63 | 1/8 | 0.98 | 2.98 | `star50_limit_proximity_early` (0.52) | +0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1375 | +0.1325 | +0.1325 | +0.7977 | 0.44 | 0/8 | 1.13 | 1.98 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0000 | +0.0000 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1120 | +0.1396 | +0.1396 | +1.6504 | 0.63 | 1/8 | 0.94 | 1.55 | `rbreaker_buy_setup_proximity_early` (0.71) | +0.0002 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1282 | +0.1015 | +0.1015 | +0.0872 | 0.41 | 0/8 | 1.39 | 2.89 | `opening_drive_thrust_ratio` (0.46) | -0.0003 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1369 | +0.1344 | +0.1344 | +0.8852 | 0.45 | 0/8 | 1.00 | 1.08 | `bar_ret_0` (0.48) | -0.0000 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1322 | +0.1248 | +0.1248 | +0.7342 | 0.40 | 0/8 | 1.17 | 1.85 | `star50_limit_proximity_early` (0.52) | +0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1133 | +0.1497 | +0.1497 | +0.8445 | 0.51 | 1/8 | 1.80 | 3.12 | `volatility_expansion_trend_vector` (0.61) | +0.0002 | +0.0000 |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1225 | +0.1293 | +0.1293 | +0.4551 | 0.45 | 0/8 | 1.27 | 1.55 | `demark_setup_reversal_early` (0.51) | +0.0005 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1233 | +0.1160 | +0.1160 | +1.3698 | 0.62 | 1/8 | 0.78 | 1.40 | `first_bar_sentiment` (0.86) | +0.0001 | +0.0000 |
| `combo_min__limit_down_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0981 | +0.1345 | +0.1345 | +1.4216 | 0.84 | 1/8 | 1.47 | 3.76 | `volume_weighted_price_position` (0.77) | +0.0006 | +0.0000 |
| `combo_mean__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1172 | +0.0890 | +0.0890 | -0.9988 | 0.50 | 0/8 | 1.27 | 1.83 | `bar_body_rng_0` (0.63) | -0.0002 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1429 | +0.1073 | +0.1073 | +0.1834 | 0.33 | 0/8 | 1.11 | 1.94 | `first_bar_return` (0.48) | -0.0001 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1217 | +0.1197 | +0.1197 | +1.2382 | 0.66 | 1/8 | 0.65 | 1.20 | `first_bar_sentiment` (0.86) | -0.0005 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1188 | +0.1421 | +0.1421 | +0.5695 | 0.36 | 0/8 | 1.55 | 2.24 | `volatility_expansion_trend_vector` (0.61) | -0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1165 | +0.1533 | +0.1533 | +0.8711 | 0.50 | 1/8 | 1.77 | 2.85 | `volatility_expansion_trend_vector` (0.61) | +0.0005 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1182 | +0.0727 | +0.0727 | -0.3605 | 0.41 | 0/8 | 1.57 | 2.14 | `opening_drive_thrust_ratio` (0.46) | -0.0005 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1126 | +0.1316 | +0.1316 | +1.5377 | 0.38 | 0/8 | 2.02 | 1.82 | `impulse_bar_dominance` (0.77) | +0.0011 | +0.0000 |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | Other Technical | +1 | +0.1184 | +0.1382 | +0.1382 | +1.3500 | 0.51 | 1/8 | 0.90 | 1.28 | `limit_down_proximity_early` (0.71) | +0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.0930 | +0.0930 | +0.0368 | 0.42 | 0/8 | 1.13 | 1.61 | `first_bar_return` (0.48) | -0.0005 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1101 | +0.0882 | +0.0882 | -1.0149 | 0.50 | 0/8 | 1.47 | 2.43 | `bar_body_rng_0` (0.63) | -0.0004 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0996 | +0.1617 | +0.1617 | +1.1078 | 0.79 | 1/8 | 1.08 | 6.24 | `rbreaker_buy_setup_proximity_early` (0.71) | +0.0003 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1057 | +0.1527 | +0.1527 | +1.5226 | 0.63 | 1/8 | 1.16 | 3.62 | `rbreaker_buy_setup_proximity_early` (0.71) | +0.0003 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Other Technical | +1 | +0.1146 | +0.1426 | +0.1426 | +1.1691 | 0.57 | 1/8 | 1.16 | 2.90 | `limit_down_proximity_early` (0.71) | -0.0001 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0673 | +0.0673 | +0.1332 | 0.57 | 0/8 | 1.59 | 2.30 | `volume_weighted_price_position` (0.77) | -0.0003 | -0.0442 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1104 | +0.1100 | +0.1100 | +0.5568 | 0.67 | 1/8 | 0.87 | 1.54 | `yesterday_early_vwap_dev` (1.29) | +0.0009 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1127 | +0.1066 | +0.1066 | +0.4207 | 0.39 | 0/8 | 1.67 | 2.71 | `star50_limit_proximity_early` (0.52) | +0.0002 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0954 | +0.1471 | +0.1471 | +1.7038 | 0.83 | 1/8 | 1.48 | 4.47 | `volume_weighted_price_position` (0.77) | +0.0008 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1152 | +0.1259 | +0.1259 | +0.1557 | 0.34 | 0/8 | 1.64 | 1.97 | `rbreaker_sell_setup_proximity_early` (0.43) | -0.0002 | -0.1580 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1283 | +0.1295 | +0.1295 | +1.1328 | 0.49 | 0/8 | 1.01 | 2.24 | `first_bar_sentiment` (0.86) | -0.0005 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1239 | +0.1308 | +0.1308 | +0.6052 | 0.40 | 0/8 | 1.05 | 1.54 | `first_bar_return` (0.48) | -0.0003 | +0.0000 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | Other Technical | +1 | +0.1016 | +0.1467 | +0.1467 | +0.8978 | 0.75 | 1/8 | 0.90 | 4.00 | `limit_down_proximity_early` (0.71) | +0.0005 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1196 | +0.1216 | +0.1216 | +0.4111 | 0.38 | 0/8 | 1.65 | 1.89 | `impulse_bar_dominance` (0.77) | +0.0001 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1236 | +0.1161 | +0.1161 | +0.1600 | 0.47 | 0/8 | 1.22 | 1.83 | `star50_limit_proximity_early` (0.52) | -0.0003 | +0.0000 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1159 | +0.0919 | +0.0919 | -0.8343 | 0.42 | 0/8 | 1.85 | 1.86 | `star50_limit_proximity_early` (0.52) | -0.0003 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1230 | +0.1269 | +0.1269 | +0.7270 | 0.43 | 0/8 | 1.19 | 1.59 | `bar_body_rng_0` (0.63) | -0.0001 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1114 | +0.0682 | +0.0682 | -0.6312 | 0.39 | 0/8 | 1.68 | 2.15 | — | -0.0007 | +0.0000 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0918 | +0.1286 | +0.1286 | +0.5529 | 0.75 | 1/8 | 1.22 | 5.34 | `yesterday_first_30min_return` (0.99) | +0.0013 | +0.0743 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1182 | +0.0824 | +0.0824 | -0.6121 | 0.46 | 0/8 | 1.75 | 2.75 | `opening_drive_thrust_ratio` (0.46) | -0.0007 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1208 | +0.0717 | +0.0717 | -1.1315 | 0.46 | 0/8 | 1.52 | 2.13 | `first_bar_return` (0.48) | -0.0006 | +0.0000 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1145 | +0.1120 | +0.1120 | +0.0365 | 0.38 | 0/8 | 1.25 | 1.09 | `star50_limit_proximity_early` (0.52) | +0.0005 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0941 | +0.1197 | +0.1197 | +0.9323 | 0.78 | 1/8 | 1.01 | 3.02 | `yesterday_early_momentum` (1.24) | +0.0012 | +0.0743 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1133 | +0.0776 | +0.0776 | -0.3109 | 0.49 | 0/8 | 1.28 | 1.96 | `bar_ret_0` (0.48) | -0.0002 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1115 | +0.0864 | +0.0864 | -0.0202 | 0.55 | 0/8 | 1.23 | 2.19 | `bar_body_rng_0` (0.63) | -0.0004 | +0.0000 |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.0893 | +0.0887 | +0.0887 | -0.3901 | 0.56 | 0/8 | 0.95 | 2.28 | `demark_setup_reversal_early` (0.51) | +0.0002 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0864 | +0.1079 | +0.1079 | -0.2788 | 0.88 | 1/8 | 2.54 | -8.81 | `yesterday_first_30min_return` (0.99) | +0.0004 | +0.0000 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0893 | +0.0450 | +0.0450 | -0.2526 | 0.70 | 1/8 | 1.02 | 2.97 | `first_bar_sentiment` (0.86) | -0.0006 | +0.0000 |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1110 | +0.0976 | +0.0976 | +0.4955 | 0.57 | 1/8 | 1.05 | 1.42 | `first_bar_sentiment` (0.86) | -0.0001 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1176 | +0.0761 | +0.0761 | -0.7836 | 0.51 | 0/8 | 1.39 | 2.51 | `first_bar_sentiment` (0.86) | -0.0006 | +0.0000 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1124 | +0.0939 | +0.0939 | -0.4022 | 0.49 | 0/8 | 1.14 | 1.69 | `bar_body_rng_0` (0.63) | -0.0006 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1219 | +0.1058 | +0.1058 | +0.4149 | 0.45 | 0/8 | 1.37 | 2.62 | `demark_setup_reversal_early` (0.51) | -0.0001 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1172 | +0.1491 | +0.1491 | +1.4472 | 0.53 | 0/8 | 1.08 | 2.08 | `bar_body_rng_0` (0.63) | -0.0004 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1128 | +0.1213 | +0.1213 | +0.2173 | 0.48 | 0/8 | 0.92 | 1.31 | `first_bar_sentiment` (0.86) | -0.0000 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1145 | +0.0725 | +0.0725 | +0.4339 | 0.45 | 0/8 | 1.18 | 1.53 | `first_bar_sentiment` (0.86) | -0.0006 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1181 | +0.0948 | +0.0948 | +0.0510 | 0.42 | 0/8 | 1.36 | 1.84 | `bar_body_rng_0` (0.63) | +0.0000 | +0.0000 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1215 | +0.1133 | +0.1133 | +0.4549 | 0.45 | 0/8 | 1.38 | 2.40 | `demark_setup_reversal_early` (0.51) | +0.0003 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1132 | +0.0770 | +0.0770 | +0.1170 | 0.49 | 0/8 | 1.03 | 1.65 | `first_bar_sentiment` (0.86) | -0.0008 | +0.0000 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1185 | +0.1056 | +0.1056 | +0.3256 | 0.46 | 0/8 | 1.55 | 2.15 | `demark_setup_reversal_early` (0.51) | -0.0001 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1159 | +0.0366 | +0.0366 | -0.6946 | 0.34 | 0/8 | 1.47 | 1.54 | `opening_drive_thrust_ratio` (0.46) | -0.0009 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0926 | +0.1271 | +0.1271 | +0.5469 | 0.76 | 1/8 | 1.32 | 8.02 | `yesterday_first_30min_return` (0.99) | +0.0018 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1210 | +0.1003 | +0.1003 | +0.2207 | 0.34 | 0/8 | 1.51 | 2.57 | `opening_drive_thrust_ratio` (0.46) | -0.0002 | +0.0000 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0917 | +0.0888 | +0.0888 | -0.2203 | 0.60 | 0/8 | 3.58 | 7.87 | `volatility_expansion_trend_vector` (0.61) | -0.0003 | +0.0000 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1013 | +0.1453 | +0.1453 | +0.2923 | 0.45 | 0/8 | 1.75 | 2.72 | `limit_down_proximity_early` (0.71) | -0.0002 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1254 | +0.1055 | +0.1055 | -0.1261 | 0.42 | 0/8 | 1.05 | 1.29 | `first_bar_sentiment` (0.86) | -0.0004 | +0.0000 |
| `combo_mean__rbreaker_buy_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1118 | +0.1340 | +0.1340 | +0.5076 | 0.59 | 0/8 | 1.08 | 1.33 | `volume_weighted_price_position` (0.77) | +0.0003 | -0.0560 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1136 | +0.0757 | +0.0757 | +0.0427 | 0.43 | 0/8 | 1.30 | 2.06 | `first_bar_sentiment` (0.86) | -0.0007 | +0.0000 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1185 | +0.1106 | +0.1106 | -0.0225 | 0.45 | 0/8 | 1.53 | 2.35 | `demark_setup_reversal_early` (0.51) | -0.0001 | +0.0000 |
| `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1201 | +0.1338 | +0.1338 | -0.1673 | 0.53 | 1/8 | 1.22 | 1.90 | `bar_body_rng_0` (0.63) | -0.0001 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1182 | +0.0860 | +0.0860 | +0.0650 | 0.53 | 1/8 | 1.07 | 1.78 | `first_bar_sentiment` (0.86) | -0.0005 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1249 | +0.1193 | +0.1193 | -0.2201 | 0.33 | 0/8 | 1.28 | 1.32 | `first_bar_return` (0.48) | +0.0001 | +0.0000 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1171 | +0.0811 | +0.0811 | -0.6874 | 0.39 | 0/8 | 1.58 | 1.46 | `star50_limit_proximity_early` (0.52) | +0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1112 | +0.0738 | +0.0738 | -0.4608 | 0.45 | 0/8 | 1.80 | 3.40 | `volatility_expansion_trend_vector` (0.61) | -0.0004 | +0.0000 |
| `combo_max__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.1001 | +0.0516 | +0.0516 | -0.9575 | 0.39 | 0/8 | 2.11 | 1.96 | `impulse_bar_dominance` (0.77) | -0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | Other Technical | +1 | +0.1030 | +0.0441 | +0.0441 | +1.1853 | 0.45 | 0/8 | 2.23 | 2.72 | `impulse_bar_dominance` (0.77) | -0.0002 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1070 | +0.1138 | +0.1138 | +0.1660 | 0.35 | 0/8 | 1.79 | 2.92 | `volatility_expansion_trend_vector` (0.61) | -0.0001 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0988 | +0.1394 | +0.1394 | +0.9587 | 0.79 | 1/8 | 1.44 | 6.15 | `yesterday_first_30min_return` (0.99) | +0.0012 | +0.0563 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1120 | +0.1308 | +0.1308 | +0.7043 | 0.52 | 1/8 | 1.38 | 3.68 | `volume_weighted_price_position` (0.77) | +0.0001 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0983 | +0.1124 | +0.1124 | +0.3952 | 0.61 | 1/8 | 1.60 | 4.45 | `yesterday_first_30min_return` (0.99) | +0.0004 | -0.0669 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1022 | +0.1065 | +0.1065 | -0.2278 | 0.53 | 0/8 | 1.68 | 3.09 | `bar_body_rng_0` (0.63) | -0.0002 | +0.0000 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1235 | +0.1428 | +0.1428 | +0.6972 | 0.46 | 1/8 | 1.20 | 2.09 | `demark_setup_reversal_early` (0.51) | +0.0008 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1175 | +0.0772 | +0.0772 | -0.5386 | 0.50 | 0/8 | 1.77 | 1.84 | `volume_weighted_price_position` (0.77) | -0.0007 | +0.0118 |
| `combo_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0877 | +0.1386 | +0.1386 | +0.6223 | 0.60 | 0/8 | 1.91 | 4.91 | `rbreaker_buy_setup_proximity_early` (0.71) | +0.0002 | +0.0000 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1158 | +0.0732 | +0.0732 | -0.9166 | 0.53 | 0/8 | 1.87 | 1.92 | `volume_weighted_price_position` (0.77) | -0.0007 | -0.1900 |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0975 | +0.1145 | +0.1145 | +0.1225 | 0.45 | 0/8 | 1.80 | 2.24 | `impulse_bar_dominance` (0.77) | +0.0002 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1132 | +0.0827 | +0.0827 | -0.0240 | 0.49 | 0/8 | 1.00 | 1.42 | `first_bar_sentiment` (0.86) | -0.0007 | +0.0000 |
| `bar_body_rng_0` | Other Technical | +1 | +0.1040 | +0.0977 | +0.0977 | -0.0244 | 0.63 | 1/8 | 0.99 | 1.55 | — | -0.0000 | +0.0000 |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1226 | +0.0636 | +0.0636 | -1.2636 | 0.44 | 0/8 | 1.22 | 1.73 | `first_bar_sentiment` (0.86) | -0.0006 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0915 | +0.1028 | +0.1028 | +0.3412 | 0.60 | 0/8 | 2.47 | 4.05 | `volatility_expansion_trend_vector` (0.61) | -0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1175 | +0.0906 | +0.0906 | +0.5068 | 0.45 | 0/8 | 1.19 | 1.73 | `bar_body_rng_0` (0.63) | +0.0001 | +0.0000 |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1093 | +0.0894 | +0.0894 | -0.0643 | 0.40 | 0/8 | 1.56 | 1.78 | `volatility_expansion_trend_vector` (0.61) | -0.0004 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1050 | +0.0936 | +0.0936 | +0.2427 | 0.75 | 1/8 | 1.07 | 2.90 | `yesterday_early_vwap_dev` (1.29) | +0.0009 | -0.0669 |
| `combo_min__limit_down_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0950 | +0.1106 | +0.1106 | +0.2142 | 0.48 | 0/8 | 2.28 | 4.61 | `impulse_bar_dominance` (0.77) | +0.0007 | +0.0000 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0659 | +0.0659 | +0.7397 | 0.53 | 0/8 | 0.94 | 1.48 | `volume_weighted_price_position` (0.77) | -0.0000 | -0.1901 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0947 | +0.0934 | +0.0934 | +0.2719 | 0.57 | 0/8 | 3.10 | 2.47 | `impulse_bar_dominance` (0.77) | +0.0002 | +0.0000 |
| `combo_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1051 | +0.0839 | +0.0839 | +0.2124 | 0.42 | 0/8 | 1.24 | 1.52 | `bar_ret_0` (0.48) | -0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | Other Technical | +1 | +0.1032 | +0.0968 | +0.0968 | +0.5705 | 0.45 | 0/8 | 1.86 | 2.83 | `impulse_bar_dominance` (0.77) | +0.0003 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1150 | +0.0792 | +0.0792 | +0.2360 | 0.46 | 0/8 | 1.44 | 2.54 | — | -0.0005 | +0.0000 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1139 | +0.0785 | +0.0785 | +0.0183 | 0.47 | 1/8 | 1.31 | 1.59 | `first_bar_sentiment` (0.86) | -0.0004 | +0.0000 |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | Other Technical | +1 | +0.1001 | +0.0960 | +0.0960 | +0.3067 | 0.44 | 0/8 | 1.65 | 2.21 | `impulse_bar_dominance` (0.77) | -0.0002 | +0.0000 |
| `combo_min__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1064 | +0.0874 | +0.0874 | +0.9830 | 0.53 | 0/8 | 1.04 | 1.57 | `bar_body_rng_0` (0.63) | +0.0000 | +0.0000 |
| `combo_mean__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1080 | +0.0739 | +0.0739 | +0.7136 | 0.55 | 0/8 | 1.22 | 1.50 | `volume_weighted_price_position` (0.77) | -0.0000 | -0.1901 |
| `combo_max__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.0942 | +0.1023 | +0.1023 | +0.5185 | 0.61 | 1/8 | 1.19 | 0.94 | `limit_down_proximity_early` (0.71) | +0.0003 | +0.0000 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1015 | +0.0743 | +0.0743 | +0.0905 | 0.50 | 0/8 | 0.88 | 1.37 | `first_bar_sentiment` (0.86) | -0.0003 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1166 | +0.0366 | +0.0366 | -0.2937 | 0.39 | 0/8 | 1.15 | 1.38 | `bar_body_rng_0` (0.63) | -0.0004 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1175 | +0.0841 | +0.0841 | +0.0197 | 0.38 | 0/8 | 1.72 | 2.07 | `opening_drive_thrust_ratio` (0.46) | -0.0004 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1080 | +0.0748 | +0.0748 | +0.7040 | 0.48 | 0/8 | 0.95 | 1.34 | — | -0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1088 | +0.0764 | +0.0764 | -0.0635 | 0.55 | 0/8 | 1.10 | 2.59 | `first_bar_sentiment` (0.86) | -0.0005 | +0.0000 |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | Other Technical | +1 | +0.0888 | +0.1036 | +0.1036 | +0.2192 | 0.61 | 1/8 | 1.65 | 1.80 | `impulse_bar_dominance` (0.77) | +0.0003 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0921 | +0.1108 | +0.1108 | +0.6963 | 0.58 | 0/8 | 2.06 | 3.49 | `bar_body_rng_0` (0.63) | -0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1188 | +0.0786 | +0.0786 | +0.2167 | 0.40 | 0/8 | 1.24 | 1.62 | `first_bar_return` (0.48) | -0.0001 | +0.0000 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0883 | +0.0813 | +0.0813 | -0.1094 | 0.61 | 0/8 | 2.36 | 4.52 | `volume_weighted_price_position` (0.77) | -0.0001 | -0.1901 |
| `combo_rank_min__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1028 | +0.0656 | +0.0656 | +0.3295 | 0.57 | 0/8 | 1.51 | 2.43 | `volume_weighted_price_position` (0.77) | -0.0001 | +0.0000 |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0941 | +0.0893 | +0.0893 | +0.0953 | 0.68 | 0/8 | 2.47 | 3.92 | `volume_weighted_price_position` (0.77) | -0.0003 | +0.0118 |
| `combo_max__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1078 | +0.0775 | +0.0775 | +0.6742 | 0.52 | 0/8 | 0.85 | 1.28 | `first_bar_sentiment` (0.86) | -0.0001 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.0815 | +0.0979 | +0.0979 | -0.7750 | 0.72 | 1/8 | 2.98 | 14.17 | — | -0.0004 | -0.0560 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0906 | +0.1031 | +0.1031 | -0.6008 | 0.63 | 1/8 | 2.21 | 53.82 | `volatility_expansion_trend_vector` (0.61) | -0.0002 | +0.0000 |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0858 | +0.0936 | +0.0936 | -0.3130 | 0.95 | 1/8 | 1.25 | 6.95 | `yesterday_early_vwap_dev` (1.29) | +0.0008 | +0.0000 |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0962 | +0.0759 | +0.0759 | +1.4912 | 0.53 | 1/8 | 0.91 | 1.45 | `first_bar_sentiment` (0.86) | -0.0004 | +0.0000 |
| `combo_max__bar_ret_0__impulse_bar_dominance` | Other Technical | +1 | +0.0908 | +0.0681 | +0.0681 | +0.8101 | 0.49 | 0/8 | 1.87 | 2.05 | `impulse_bar_dominance` (0.77) | +0.0003 | +0.0000 |
| `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0854 | +0.0796 | +0.0796 | -0.0979 | 0.58 | 0/8 | 3.92 | 5.61 | `impulse_bar_dominance` (0.77) | +0.0001 | +0.0000 |
| `combo_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1100 | +0.0739 | +0.0739 | +0.1559 | 0.48 | 0/8 | 1.20 | 2.31 | `late_bar_momentum` (0.77) | -0.0006 | -0.1900 |
| `volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0820 | +0.0926 | +0.0926 | +0.3605 | 0.61 | 0/8 | 3.52 | 6.66 | — | -0.0004 | +0.0000 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0557 | -0.0153 | -0.0153 | -0.1443 | 0.97 | 1/8 | 0.26 | 0.12 | `volatility_expansion_trend_vector` (0.61) | +0.0002 | -0.1900 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1104 | +0.0278 | +0.0278 | -0.5804 | 0.37 | 0/8 | 1.09 | 1.24 | `first_bar_return` (0.48) | -0.0002 | +0.0000 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 48.0% lock IC > 0, 11.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8008_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 960 | 30 | 76.7% | 50.0% | +0.0443 | -0.1641 |
| B2 Rolling Guard | 115 | 30 | 70.0% | 26.7% | +0.0184 | -0.4187 |
| BH-FDR Gate | 4 | 4 | 75.0% | 25.0% | +0.0215 | -0.5464 |
| B4 Correlation Gate | 190 | 30 | 56.7% | 26.7% | +0.0153 | -0.6290 |

**Admitted Pool Summary**: 82 features, False Positive Rate = 91.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0030, Mean Lock Sharpe = -0.7616

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ratio__limit_down_proximity_early__volume_concentration`: Train IC=+0.1720, Lock IC=+0.1235, Lock Sharpe=+0.9843
- `combo_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611
- `combo_z_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611
- `combo_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611
- `combo_z_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0962, Lock Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0962, Lock Sharpe=+0.8491
- `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353
- `combo_z_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353
- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Lock Sharpe=+0.1297

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Lock Sharpe=+0.3895
- `combo_z_sum__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Lock Sharpe=+0.3895
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Lock Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Lock Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Lock Sharpe=+0.3783

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

_Null Baseline (un-gated candidate pool): 62.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5622_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 841 | 30 | 96.7% | 50.0% | +0.0404 | +0.1022 |
| B2 Rolling Guard | 77 | 30 | 90.0% | 46.7% | +0.0495 | +0.0918 |
| BH-FDR Gate | 3 | 3 | 0.0% | 0.0% | -0.0339 | -0.9002 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__volume_surge_max__roc10`: Train IC=+0.1513, Lock IC=+0.0272, Lock Sharpe=+1.0041
- `combo_rank_min__first_bar_volume__roc10`: Train IC=+0.1467, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_rank_min__bar_vol_0__roc10`: Train IC=+0.1467, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_min__roc60__roc10`: Train IC=+0.1297, Lock IC=+0.0274, Lock Sharpe=+0.7136
- `combo_sig_product__roc60__roc10`: Train IC=+0.1486, Lock IC=+0.0149, Lock Sharpe=+0.5659

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__sma50_dist`: Train IC=+0.1129, Lock IC=+0.0768, Lock Sharpe=+1.2013
- `combo_sig_product__iv_corridor_width__sma100_dist`: Train IC=+0.1155, Lock IC=+0.0663, Lock Sharpe=+1.0514
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.0946, Lock IC=+0.0603, Lock Sharpe=+0.9632
- `combo_rank_max__bar_vol_4__roc10`: Train IC=+0.1007, Lock IC=+0.0813, Lock Sharpe=+0.9300
- `combo_max__bar_vol_4__yesterday_wavetrend_osc`: Train IC=+0.0830, Lock IC=+0.0958, Lock Sharpe=+0.8260

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

_Null Baseline (un-gated candidate pool): 66.0% lock IC > 0, 26.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6280_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1699 | 30 | 100.0% | 56.7% | +0.0791 | -0.1073 |
| B2 Rolling Guard | 207 | 30 | 90.0% | 6.7% | +0.0335 | -0.8422 |
| BH-FDR Gate | 4 | 4 | 75.0% | 0.0% | +0.0034 | -1.3580 |
| B3 Composite Floor | 52 | 30 | 83.3% | 26.7% | +0.0292 | -0.6567 |
| B4 Correlation Gate | 643 | 30 | 100.0% | 10.0% | +0.0627 | -0.6339 |

**Admitted Pool Summary**: 160 features, False Positive Rate = 68.1% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0610, Mean Lock Sharpe = -0.3691

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Lock Sharpe=+0.5717
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_mean__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2188, Lock IC=+0.1124, Lock Sharpe=+0.3413
- `combo_z_sum__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2188, Lock IC=+0.1124, Lock Sharpe=+0.3413

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__early_late_momentum_divergence__first_bar_sentiment`: Train IC=+0.1855, Lock IC=+0.0659, Lock Sharpe=+0.3681
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2239, Lock IC=+0.0978, Lock Sharpe=+0.0194

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1847, Lock IC=+0.0017, Lock Sharpe=+0.3201
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.1599, Lock IC=+0.0747, Lock Sharpe=+0.2713
- `combo_tri_mean__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_z_mean__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_mean__smooth_momentum_structure__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2741, Lock IC=+0.0880, Lock Sharpe=+0.3545
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2627, Lock IC=+0.0843, Lock Sharpe=+0.0822
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2627, Lock IC=+0.0843, Lock Sharpe=+0.0822

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

_Null Baseline (un-gated candidate pool): 82.0% lock IC > 0, 52.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0214_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1089 | 30 | 100.0% | 70.0% | +0.1079 | +0.2611 |
| B2 Rolling Guard | 172 | 30 | 100.0% | 66.7% | +0.0946 | +0.3173 |
| BH-FDR Gate | 4 | 4 | 100.0% | 25.0% | +0.0525 | -0.1452 |
| B3 Composite Floor | 98 | 30 | 100.0% | 90.0% | +0.1079 | +0.3832 |
| B4 Correlation Gate | 307 | 30 | 100.0% | 100.0% | +0.1288 | +1.0483 |

**Admitted Pool Summary**: 150 features, False Positive Rate = 26.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1054, Mean Lock Sharpe = +0.3857

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2018, Lock IC=+0.1126, Lock Sharpe=+1.5724
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.9095
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.9095
- `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2346, Lock IC=+0.1159, Lock Sharpe=+0.7959
- `combo_z_sum__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2346, Lock IC=+0.1159, Lock Sharpe=+0.7959

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+1.0537
- `combo_rank_max__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1830, Lock IC=+0.0792, Lock Sharpe=+0.8691
- `combo_rel_diff__limit_down_proximity_early__demark_setup_reversal_early`: Train IC=+0.1712, Lock IC=+0.1393, Lock Sharpe=+0.7803
- `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.1712, Lock IC=+0.1393, Lock Sharpe=+0.7803

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0396, Lock IC=+0.1184, Lock Sharpe=+0.1847

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2227, Lock IC=+0.1193, Lock Sharpe=+1.3049
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2417, Lock IC=+0.1107, Lock Sharpe=+1.2956
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2268, Lock IC=+0.1295, Lock Sharpe=+1.2146
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2559, Lock IC=+0.1307, Lock Sharpe=+0.9421
- `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`: Train IC=+0.2460, Lock IC=+0.1133, Lock Sharpe=+0.8865

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3282, Lock IC=+0.1307, Lock Sharpe=+1.7816
- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.5184
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.5184
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.4890
- `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3025, Lock IC=+0.1381, Lock Sharpe=+1.4675

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
| 0.45 | 0.10 | 594 | +0.0242 | 80.0% |
| 0.45 | 0.20 | 586 | +0.0242 | 80.0% |
| 0.45 | 0.30 | 560 | +0.0242 | 80.0% |
| 0.45 | 0.40 | 493 | +0.0242 | 80.0% |
| 0.45 | 0.50 | 401 | +0.0242 | 80.0% |
| 0.50 | 0.15 | 592 | +0.0242 | 80.0% |
| 0.50 | 0.25 | 572 | +0.0242 | 80.0% |
| 0.50 | 0.35 | 529 | +0.0242 | 80.0% |
| 0.50 | 0.45 | 456 | +0.0242 | 80.0% |
| 0.55 | 0.10 | 589 | +0.0242 | 80.0% |
| 0.55 | 0.20 | 584 | +0.0242 | 80.0% |
| 0.55 | 0.30 | 560 | +0.0242 | 80.0% |
| 0.55 | 0.40 | 493 | +0.0242 | 80.0% |
| 0.55 | 0.50 | 401 | +0.0242 | 80.0% |
| 0.60 | 0.15 | 573 | +0.0242 | 80.0% |
| 0.60 | 0.25 | 563 | +0.0242 | 80.0% |
| 0.60 | 0.35 | 528 | +0.0242 | 80.0% |
| 0.60 | 0.45 | 456 | +0.0242 | 80.0% |
| 0.65 | 0.10 | 496 | +0.0242 | 80.0% |
| 0.65 | 0.20 | 496 | +0.0242 | 80.0% |
| 0.65 | 0.30 | 494 | +0.0242 | 80.0% |
| 0.65 | 0.40 | 477 | +0.0242 | 80.0% |
| 0.65 | 0.50 | 401 | +0.0242 | 80.0% |
| 0.70 | 0.15 | 365 | +0.0242 | 80.0% |
| 0.70 | 0.25 | 365 | +0.0242 | 80.0% |
| 0.70 | 0.35 | 365 | +0.0242 | 80.0% |
| 0.70 | 0.45 | 362 | +0.0242 | 80.0% |
| 0.75 | 0.10 | 142 | +0.0108 | 60.0% |
| 0.75 | 0.20 | 142 | +0.0108 | 60.0% |
| 0.75 | 0.30 | 142 | +0.0108 | 60.0% |
| 0.75 | 0.40 | 142 | +0.0108 | 60.0% |
| 0.75 | 0.50 | 142 | +0.0108 | 60.0% |
| 0.80 | 0.15 | 19 | -0.0194 | 20.0% |
| 0.80 | 0.25 | 19 | -0.0194 | 20.0% |
| 0.80 | 0.35 | 19 | -0.0194 | 20.0% |
| 0.80 | 0.45 | 19 | -0.0194 | 20.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 594 candidates, mean lock IC=+0.0242, 80.0% positive

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
| 0.45 | 0.10 | 386 | +0.0545 | 100.0% |
| 0.45 | 0.20 | 371 | +0.0545 | 100.0% |
| 0.45 | 0.30 | 344 | +0.0545 | 100.0% |
| 0.45 | 0.40 | 325 | +0.0545 | 100.0% |
| 0.45 | 0.50 | 304 | +0.0545 | 100.0% |
| 0.50 | 0.15 | 385 | +0.0545 | 100.0% |
| 0.50 | 0.25 | 360 | +0.0545 | 100.0% |
| 0.50 | 0.35 | 337 | +0.0545 | 100.0% |
| 0.50 | 0.45 | 316 | +0.0545 | 100.0% |
| 0.55 | 0.10 | 382 | +0.0545 | 100.0% |
| 0.55 | 0.20 | 369 | +0.0545 | 100.0% |
| 0.55 | 0.30 | 344 | +0.0545 | 100.0% |
| 0.55 | 0.40 | 325 | +0.0545 | 100.0% |
| 0.55 | 0.50 | 304 | +0.0545 | 100.0% |
| 0.60 | 0.15 | 351 | +0.0545 | 100.0% |
| 0.60 | 0.25 | 348 | +0.0545 | 100.0% |
| 0.60 | 0.35 | 336 | +0.0545 | 100.0% |
| 0.60 | 0.45 | 316 | +0.0545 | 100.0% |
| 0.65 | 0.10 | 327 | +0.0545 | 100.0% |
| 0.65 | 0.20 | 327 | +0.0545 | 100.0% |
| 0.65 | 0.30 | 326 | +0.0545 | 100.0% |
| 0.65 | 0.40 | 321 | +0.0545 | 100.0% |
| 0.65 | 0.50 | 304 | +0.0545 | 100.0% |
| 0.70 | 0.15 | 283 | +0.0545 | 100.0% |
| 0.70 | 0.25 | 283 | +0.0545 | 100.0% |
| 0.70 | 0.35 | 283 | +0.0545 | 100.0% |
| 0.70 | 0.45 | 283 | +0.0545 | 100.0% |
| 0.75 | 0.10 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.20 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.30 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.40 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.50 | 219 | +0.0534 | 100.0% |
| 0.80 | 0.15 | 172 | +0.0450 | 100.0% |
| 0.80 | 0.25 | 172 | +0.0450 | 100.0% |
| 0.80 | 0.35 | 172 | +0.0450 | 100.0% |
| 0.80 | 0.45 | 172 | +0.0450 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 386 candidates, mean lock IC=+0.0545, 100.0% positive

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
| 0.45 | 0.10 | 1315 | +0.0547 | 100.0% |
| 0.45 | 0.20 | 1296 | +0.0547 | 100.0% |
| 0.45 | 0.30 | 1229 | +0.0547 | 100.0% |
| 0.45 | 0.40 | 1139 | +0.0547 | 100.0% |
| 0.45 | 0.50 | 940 | +0.0547 | 100.0% |
| 0.50 | 0.15 | 1306 | +0.0547 | 100.0% |
| 0.50 | 0.25 | 1269 | +0.0547 | 100.0% |
| 0.50 | 0.35 | 1184 | +0.0547 | 100.0% |
| 0.50 | 0.45 | 1019 | +0.0547 | 100.0% |
| 0.55 | 0.10 | 1309 | +0.0547 | 100.0% |
| 0.55 | 0.20 | 1295 | +0.0547 | 100.0% |
| 0.55 | 0.30 | 1229 | +0.0547 | 100.0% |
| 0.55 | 0.40 | 1139 | +0.0547 | 100.0% |
| 0.55 | 0.50 | 940 | +0.0547 | 100.0% |
| 0.60 | 0.15 | 1263 | +0.0547 | 100.0% |
| 0.60 | 0.25 | 1251 | +0.0547 | 100.0% |
| 0.60 | 0.35 | 1180 | +0.0547 | 100.0% |
| 0.60 | 0.45 | 1019 | +0.0547 | 100.0% |
| 0.65 | 0.10 | 1131 | +0.0547 | 100.0% |
| 0.65 | 0.20 | 1131 | +0.0547 | 100.0% |
| 0.65 | 0.30 | 1131 | +0.0547 | 100.0% |
| 0.65 | 0.40 | 1105 | +0.0547 | 100.0% |
| 0.65 | 0.50 | 940 | +0.0547 | 100.0% |
| 0.70 | 0.15 | 848 | +0.0547 | 100.0% |
| 0.70 | 0.25 | 848 | +0.0547 | 100.0% |
| 0.70 | 0.35 | 848 | +0.0547 | 100.0% |
| 0.70 | 0.45 | 847 | +0.0547 | 100.0% |
| 0.75 | 0.10 | 461 | +0.0547 | 100.0% |
| 0.75 | 0.20 | 461 | +0.0547 | 100.0% |
| 0.75 | 0.30 | 461 | +0.0547 | 100.0% |
| 0.75 | 0.40 | 461 | +0.0547 | 100.0% |
| 0.75 | 0.50 | 461 | +0.0547 | 100.0% |
| 0.80 | 0.15 | 175 | +0.0547 | 100.0% |
| 0.80 | 0.25 | 175 | +0.0547 | 100.0% |
| 0.80 | 0.35 | 175 | +0.0547 | 100.0% |
| 0.80 | 0.45 | 175 | +0.0547 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1315 candidates, mean lock IC=+0.0547, 100.0% positive

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
| 0.45 | 0.10 | 780 | +0.1307 | 100.0% |
| 0.45 | 0.20 | 768 | +0.1307 | 100.0% |
| 0.45 | 0.30 | 700 | +0.1307 | 100.0% |
| 0.45 | 0.40 | 627 | +0.1307 | 100.0% |
| 0.45 | 0.50 | 497 | +0.1307 | 100.0% |
| 0.50 | 0.15 | 776 | +0.1307 | 100.0% |
| 0.50 | 0.25 | 729 | +0.1307 | 100.0% |
| 0.50 | 0.35 | 672 | +0.1307 | 100.0% |
| 0.50 | 0.45 | 570 | +0.1307 | 100.0% |
| 0.55 | 0.10 | 774 | +0.1307 | 100.0% |
| 0.55 | 0.20 | 766 | +0.1307 | 100.0% |
| 0.55 | 0.30 | 700 | +0.1307 | 100.0% |
| 0.55 | 0.40 | 627 | +0.1307 | 100.0% |
| 0.55 | 0.50 | 497 | +0.1307 | 100.0% |
| 0.60 | 0.15 | 716 | +0.1307 | 100.0% |
| 0.60 | 0.25 | 707 | +0.1307 | 100.0% |
| 0.60 | 0.35 | 671 | +0.1307 | 100.0% |
| 0.60 | 0.45 | 570 | +0.1307 | 100.0% |
| 0.65 | 0.10 | 626 | +0.1307 | 100.0% |
| 0.65 | 0.20 | 626 | +0.1307 | 100.0% |
| 0.65 | 0.30 | 626 | +0.1307 | 100.0% |
| 0.65 | 0.40 | 608 | +0.1307 | 100.0% |
| 0.65 | 0.50 | 496 | +0.1307 | 100.0% |
| 0.70 | 0.15 | 448 | +0.1307 | 100.0% |
| 0.70 | 0.25 | 448 | +0.1307 | 100.0% |
| 0.70 | 0.35 | 448 | +0.1307 | 100.0% |
| 0.70 | 0.45 | 448 | +0.1307 | 100.0% |
| 0.75 | 0.10 | 234 | +0.1307 | 100.0% |
| 0.75 | 0.20 | 234 | +0.1307 | 100.0% |
| 0.75 | 0.30 | 234 | +0.1307 | 100.0% |
| 0.75 | 0.40 | 234 | +0.1307 | 100.0% |
| 0.75 | 0.50 | 234 | +0.1307 | 100.0% |
| 0.80 | 0.15 | 63 | +0.1307 | 100.0% |
| 0.80 | 0.25 | 63 | +0.1307 | 100.0% |
| 0.80 | 0.35 | 63 | +0.1307 | 100.0% |
| 0.80 | 0.45 | 63 | +0.1307 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 780 candidates, mean lock IC=+0.1307, 100.0% positive

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1254 | +0.0000 | +0.0229 | 0.18x | 2016-08-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1140 | +0.0000 | +0.0463 | 0.41x | 2016-08-24 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | +0.1140 | +0.0000 | -0.0365 | -0.32x | 2017-06-09 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1253 | +0.0000 | +0.0164 | 0.13x | 2016-08-24 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1039 | +0.0000 | -0.0223 | -0.21x | 2015-03-16 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +0.1108 | +0.0000 | -0.0022 | -0.02x | 2017-09-06 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1109 | +0.0000 | -0.0261 | -0.24x | 2015-02-06 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0938 | +0.0000 | +0.0772 | 0.82x | 2013-08-21 |
| `combo_max__max_up_ret__first_bar_sentiment` | +0.0996 | +0.0000 | -0.0315 | -0.32x | 2015-01-08 |
| `combo_max__max_up_ret__bar_ret_0` | +0.1000 | +0.0000 | -0.0225 | -0.23x | 2014-07-04 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +0.1129 | +0.0000 | -0.0091 | -0.08x | 2017-04-07 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | +0.1209 | +0.0000 | +0.0259 | 0.21x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1264 | +0.0000 | +0.0237 | 0.19x | 2016-08-24 |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0922 | +0.0000 | +0.0685 | 0.74x | 2016-07-26 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | +0.0999 | +0.0000 | -0.0344 | -0.34x | 2015-02-06 |
| `max_up_ret` | +0.1001 | +0.0000 | -0.0463 | -0.46x | 2015-02-06 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1111 | +0.0000 | +0.0592 | 0.53x | 2017-08-08 |
| `combo_max__first_bar_return__volume_surge_direction` | +0.0802 | +0.0000 | +0.0104 | 0.13x | 2013-08-21 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1152 | +0.0000 | -0.0009 | -0.01x | 2017-07-10 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | +0.0935 | +0.0000 | -0.0212 | -0.23x | 2015-02-06 |
| `combo_max__max_up_ret__volume_surge_direction` | +0.0846 | +0.0000 | -0.0158 | -0.19x | 2014-07-04 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1070 | +0.0000 | -0.0157 | -0.15x | 2015-02-06 |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.1093 | +0.0000 | -0.0151 | -0.14x | 2014-12-08 |
| `combo_max__first_bar_return__volume_weighted_price_position` | +0.0935 | +0.0000 | -0.0191 | -0.20x | 2015-02-06 |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | +0.1012 | +0.0000 | +0.0168 | 0.17x | 2013-09-23 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | +0.0866 | +0.0000 | -0.0136 | -0.16x | 2013-08-21 |
| `combo_rank_max__max_up_ret__first_bar_return` | +0.1015 | +0.0000 | -0.0197 | -0.19x | 2014-07-04 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1031 | +0.0000 | -0.0364 | -0.35x | 2015-02-06 |
| `bar_body_rng_0` | +0.0924 | +0.0000 | +0.0209 | 0.23x | 2010-10-15 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1145 | +0.0000 | +0.0158 | 0.14x | 2017-06-09 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1054 | +0.0000 | -0.0275 | -0.26x | 2017-07-10 |
| `combo_max__bar_body_rng_0__volume_surge_direction` | +0.0801 | +0.0000 | +0.0347 | 0.43x | 2013-08-21 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | +0.1065 | +0.0000 | +0.0559 | 0.52x | 2017-09-06 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1123 | +0.0000 | -0.0061 | -0.05x | 2017-07-10 |
| `combo_mean__max_up_ret__volume_surge_direction` | +0.0957 | +0.0000 | -0.0027 | -0.03x | 2014-07-04 |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | +0.1050 | +0.0000 | +0.0113 | 0.11x | 2015-01-08 |
| `combo_min__max_up_ret__volume_surge_direction` | +0.0910 | +0.0000 | +0.0128 | 0.14x | 2015-01-08 |
| `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | +0.0898 | +0.0000 | +0.0077 | 0.09x | 2013-08-21 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1065 | +0.0000 | -0.0082 | -0.08x | 2014-08-04 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1107 | +0.0000 | +0.0432 | 0.39x | 2016-08-24 |
| `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position` | +0.1037 | +0.0000 | +0.0073 | 0.07x | 2015-02-06 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | +0.0791 | +0.0000 | +0.0300 | 0.38x | 2010-12-14 |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1106 | +0.0000 | -0.0217 | -0.20x | 2015-03-16 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1092 | +0.0000 | +0.0164 | 0.15x | 2017-05-09 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1071 | +0.0000 | +0.0040 | 0.04x | 2015-03-16 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +0.1208 | +0.0000 | +0.0081 | 0.07x | 2017-06-09 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | +0.1117 | +0.0000 | -0.0211 | -0.19x | 2015-02-06 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1240 | +0.0000 | +0.0326 | 0.26x | 2017-07-10 |
| `first_bar_return` | +0.0871 | +0.0000 | +0.0007 | 0.01x | 2013-08-21 |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | +0.1094 | +0.0000 | -0.0176 | -0.16x | 2017-06-09 |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | +0.0961 | +0.0000 | +0.0258 | 0.27x | 2015-01-08 |
| `combo_max__opening_drive_thrust_ratio__volume_surge_direction` | +0.0975 | +0.0000 | -0.0044 | -0.05x | 2015-01-08 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | +0.0994 | +0.0000 | +0.0303 | 0.30x | 2015-03-16 |
| `combo_mean__first_bar_return__first_bar_sentiment` | +0.0871 | +0.0000 | +0.0007 | 0.01x | 2013-08-21 |
| `combo_min__max_up_ret__bar_ret_0` | +0.0968 | +0.0000 | -0.0256 | -0.26x | 2015-02-06 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1152 | +0.0000 | +0.0185 | 0.16x | 2015-02-06 |
| `combo_min__max_up_ret__first_bar_sentiment` | +0.0958 | +0.0000 | -0.0154 | -0.16x | 2015-01-08 |
| `combo_min__first_bar_return__volume_surge_direction` | +0.0719 | +0.0000 | +0.0184 | 0.26x | 2010-12-14 |
| `combo_rank_max__max_up_ret__volume_surge_direction` | +0.0854 | +0.0000 | -0.0111 | -0.13x | 2014-07-04 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | +0.1167 | +0.0000 | -0.0284 | -0.24x | 2017-02-06 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | +0.1097 | +0.0000 | -0.0128 | -0.12x | 2015-02-06 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1056 | +0.0000 | -0.0056 | -0.05x | 2015-02-06 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1110 | +0.0000 | -0.0374 | -0.34x | 2017-06-09 |
| `combo_tri_median__smooth_momentum_structure__first_bar_return__volume_weighted_price_position` | +0.0722 | +0.0000 | -0.0269 | -0.37x | 2013-08-21 |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | +0.1150 | +0.0000 | +0.0133 | 0.12x | 2015-02-06 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0909 | +0.0000 | +0.0753 | 0.83x | 2016-08-24 |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1026 | +0.0000 | +0.0006 | 0.01x | 2017-07-10 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | +0.0950 | +0.0000 | -0.0410 | -0.43x | 2015-03-16 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0366 | +0.0000 | -0.0133 | -0.36x | 2010-10-15 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.0921 | +0.0000 | +0.0205 | 0.22x | 2014-07-04 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.0789 | +0.0000 | +0.0244 | 0.31x | 2014-07-04 |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | +0.0881 | +0.0000 | -0.0077 | -0.09x | 2015-01-08 |
| `volume_weighted_price_position` | +0.0929 | +0.0000 | +0.0000 | 0.00x | 2015-02-06 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | +0.1068 | +0.0000 | +0.0217 | 0.20x | 2017-08-08 |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | +0.1146 | +0.0000 | -0.0338 | -0.30x | 2016-12-29 |
| `combo_ratio__bar_ret_0__volume_surge_direction` | +0.0811 | +0.0000 | -0.0090 | -0.11x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1948 | +0.0000 | +0.0406 | 0.21x | 2016-11-30 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | +0.1826 | +0.0000 | +0.0849 | 0.46x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | +0.1911 | +0.0000 | +0.0942 | 0.49x | No decay |
| `combo_mean__close_vs_open_range__bar_ret_0` | +0.1641 | +0.0000 | +0.0469 | 0.29x | No decay |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1791 | +0.0000 | +0.0426 | 0.24x | No decay |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1871 | +0.0000 | +0.0316 | 0.17x | 2025-07-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1649 | +0.0000 | +0.0933 | 0.57x | 2021-07-28 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1870 | +0.0000 | +0.0289 | 0.15x | 2025-07-24 |
| `combo_max__bar_ret_0__max_down_ret` | +0.1607 | +0.0000 | +0.0518 | 0.32x | 2016-11-01 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1818 | +0.0000 | +0.0534 | 0.29x | 2016-11-30 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | +0.1850 | +0.0000 | +0.0478 | 0.26x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1908 | +0.0000 | +0.0883 | 0.46x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1841 | +0.0000 | +0.0337 | 0.18x | 2021-07-28 |
| `combo_min__net_volume_flow__first_bar_return` | +0.1455 | +0.0000 | +0.0647 | 0.44x | No decay |
| `max_up_ret` | +0.1829 | +0.0000 | +0.0308 | 0.17x | No decay |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | +0.1657 | +0.0000 | +0.0238 | 0.14x | No decay |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1736 | +0.0000 | +0.0527 | 0.30x | No decay |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1717 | +0.0000 | +0.0390 | 0.23x | 2016-11-01 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1545 | +0.0000 | +0.0817 | 0.53x | 2016-09-26 |
| `combo_min__net_volume_flow__close_vs_open_range` | +0.1443 | +0.0000 | +0.0525 | 0.36x | 2016-11-01 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1901 | +0.0000 | +0.0453 | 0.24x | No decay |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | +0.1517 | +0.0000 | +0.0503 | 0.33x | 2020-01-06 |
| `combo_mean__max_up_ret__first_bar_sentiment` | +0.1784 | +0.0000 | +0.0297 | 0.17x | 2020-01-06 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | +0.1921 | +0.0000 | +0.0719 | 0.37x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1539 | +0.0000 | +0.0560 | 0.36x | 2016-11-01 |
| `combo_diff__max_up_ret__body_size_progression` | +0.1702 | +0.0000 | +0.0418 | 0.25x | 2025-06-25 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1826 | +0.0000 | +0.0573 | 0.31x | No decay |
| `combo_mean__max_up_ret__first_bar_return` | +0.1782 | +0.0000 | +0.0281 | 0.16x | No decay |
| `combo_max__close_vs_open_range__first_bar_return` | +0.1647 | +0.0000 | +0.0235 | 0.14x | No decay |
| `combo_clamp_diff__max_up_ret__body_size_progression` | +0.1710 | +0.0000 | +0.0419 | 0.25x | 2025-07-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | +0.1957 | +0.0000 | +0.0857 | 0.44x | No decay |
| `combo_mean__trend_bar_close_consistency__bar_ret_0` | +0.1532 | +0.0000 | +0.0378 | 0.25x | 2016-11-01 |
| `combo_rank_max__max_up_ret__net_volume_flow` | +0.1800 | +0.0000 | +0.0489 | 0.27x | 2016-11-30 |
| `combo_rank_max__max_up_ret__bar_ret_0` | +0.1707 | +0.0000 | +0.0294 | 0.17x | No decay |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | +0.1607 | +0.0000 | +0.1060 | 0.66x | 2016-09-26 |
| `first_bar_return` | +0.1382 | +0.0000 | +0.0404 | 0.29x | 2013-09-23 |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | +0.1636 | +0.0000 | +0.0550 | 0.34x | 2016-11-01 |
| `combo_rank_max__trend_bar_close_consistency__bar_ret_0` | +0.1555 | +0.0000 | +0.0085 | 0.05x | 2020-01-06 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1607 | +0.0000 | +0.0946 | 0.59x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1820 | +0.0000 | +0.0399 | 0.22x | 2020-01-06 |
| `combo_max__early_body_momentum__bar_ret_0` | +0.1609 | +0.0000 | +0.0186 | 0.12x | 2020-02-12 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1778 | +0.0000 | +0.0867 | 0.49x | 2019-12-05 |
| `combo_max__max_up_ret__early_body_momentum` | +0.1735 | +0.0000 | +0.0254 | 0.15x | 2016-11-01 |
| `combo_rank_min__net_volume_flow__first_bar_return` | +0.1453 | +0.0000 | +0.0705 | 0.49x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1681 | +0.0000 | +0.1087 | 0.65x | No decay |
| `combo_mean__first_bar_sentiment__bar_ret_0` | +0.1382 | +0.0000 | +0.0404 | 0.29x | 2013-09-23 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | +0.1658 | +0.0000 | +0.0639 | 0.39x | No decay |
| `combo_mean__net_volume_flow__first_bar_sentiment` | +0.1552 | +0.0000 | +0.0519 | 0.33x | 2020-01-06 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.2044 | +0.0000 | +0.0524 | 0.26x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1617 | +0.0000 | +0.1136 | 0.70x | 2016-08-24 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | +0.1749 | +0.0000 | +0.0419 | 0.24x | 2020-01-06 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1594 | +0.0000 | +0.0589 | 0.37x | 2016-12-29 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1938 | +0.0000 | +0.0366 | 0.19x | No decay |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1551 | +0.0000 | +0.1051 | 0.68x | 2016-09-26 |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1621 | +0.0000 | +0.0336 | 0.21x | 2016-11-01 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1933 | +0.0000 | +0.0393 | 0.20x | 2016-11-30 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1681 | +0.0000 | +0.0959 | 0.57x | 2016-09-26 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +0.1707 | +0.0000 | +0.0552 | 0.32x | 2016-11-30 |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | +0.1409 | +0.0000 | +0.1143 | 0.81x | 2023-01-16 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | +0.1900 | +0.0000 | +0.0525 | 0.28x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | +0.1702 | +0.0000 | +0.0480 | 0.28x | 2016-12-29 |
| `combo_mean__first_bar_return__max_down_ret` | +0.1481 | +0.0000 | +0.0745 | 0.50x | No decay |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1585 | +0.0000 | +0.1065 | 0.67x | 2022-12-15 |
| `combo_rank_min__opening_drive_thrust_ratio__trend_day_regime_conviction` | +0.1681 | +0.0000 | +0.0473 | 0.28x | 2016-11-01 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | +0.1351 | +0.0000 | +0.0531 | 0.39x | 2013-09-23 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | +0.1531 | +0.0000 | +0.0700 | 0.46x | 2016-12-29 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1723 | +0.0000 | +0.0541 | 0.31x | 2020-01-06 |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | +0.1396 | +0.0000 | +0.1117 | 0.80x | 2020-12-18 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1600 | +0.0000 | +0.0921 | 0.58x | No decay |
| `combo_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1627 | +0.0000 | +0.0498 | 0.31x | No decay |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1583 | +0.0000 | +0.1041 | 0.66x | 2022-12-15 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_day_regime_conviction` | +0.1621 | +0.0000 | +0.0287 | 0.18x | 2016-12-29 |
| `combo_rank_max__early_body_momentum__max_down_ret` | +0.1521 | +0.0000 | +0.0566 | 0.37x | 2016-11-01 |
| `combo_min__max_up_ret__close_vs_open_range` | +0.1604 | +0.0000 | +0.0594 | 0.37x | 2020-01-06 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1592 | +0.0000 | +0.0458 | 0.29x | 2022-12-15 |
| `combo_min__close_vs_open_range__first_bar_return` | +0.1406 | +0.0000 | +0.0798 | 0.57x | 2020-01-06 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1429 | +0.0000 | +0.0970 | 0.68x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1616 | +0.0000 | +0.0383 | 0.24x | 2016-12-29 |
| `combo_rank_max__net_volume_flow__close_vs_open_range` | +0.1526 | +0.0000 | +0.0528 | 0.35x | 2016-11-01 |
| `combo_rank_min__max_up_ret__first_bar_return` | +0.1668 | +0.0000 | +0.0432 | 0.26x | No decay |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1377 | +0.0000 | +0.1138 | 0.83x | 2011-12-23 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1619 | +0.0000 | +0.0583 | 0.36x | No decay |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | +0.1592 | +0.0000 | +0.1076 | 0.68x | 2016-09-26 |
| `combo_mean__net_volume_flow__max_down_ret` | +0.1576 | +0.0000 | +0.0666 | 0.42x | 2016-11-01 |
| `combo_min__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1641 | +0.0000 | +0.1001 | 0.61x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +0.1402 | +0.0000 | +0.1107 | 0.79x | 2023-01-16 |
| `combo_rank_max__bar_ret_0__max_down_ret` | +0.1592 | +0.0000 | +0.0684 | 0.43x | No decay |
| `combo_max__close_vs_open_range__early_body_momentum` | +0.1435 | +0.0000 | +0.0413 | 0.29x | 2016-11-01 |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1502 | +0.0000 | +0.0636 | 0.42x | 2016-11-01 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +0.1608 | +0.0000 | +0.0608 | 0.38x | 2020-02-12 |
| `combo_min__trend_bar_close_consistency__bar_ret_0` | +0.1297 | +0.0000 | +0.0619 | 0.48x | 2016-11-01 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1544 | +0.0000 | +0.0205 | 0.13x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1621 | +0.0000 | +0.0219 | 0.13x | 2016-12-29 |
| `open_to_current_return` | +0.1457 | +0.0000 | +0.0435 | 0.30x | 2016-11-01 |
| `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction` | +0.1410 | +0.0000 | +0.0538 | 0.38x | 2016-09-26 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.1607 | +0.0000 | +0.0435 | 0.27x | 2020-01-06 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1600 | +0.0000 | +0.0714 | 0.45x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1426 | +0.0000 | +0.1502 | 1.05x | 2016-08-24 |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | +0.1266 | +0.0000 | +0.0313 | 0.25x | 2017-08-08 |
| `combo_sig_product__max_up_ret__early_body_momentum` | +0.1700 | +0.0000 | +0.0290 | 0.17x | 2019-12-05 |
| `combo_min__max_up_ret__trend_bar_close_consistency` | +0.1529 | +0.0000 | +0.0291 | 0.19x | 2020-01-06 |
| `morning_volume_weighted_momentum` | +0.1381 | +0.0000 | +0.0484 | 0.35x | 2016-11-01 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | +0.1729 | +0.0000 | +0.0707 | 0.41x | 2016-11-30 |
| `combo_sig_product__net_volume_flow__first_bar_return` | +0.1232 | +0.0000 | +0.0246 | 0.20x | 2016-11-01 |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1484 | +0.0000 | +0.0528 | 0.36x | 2016-11-01 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | +0.1447 | +0.0000 | +0.0438 | 0.30x | 2016-11-01 |
| `combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1497 | +0.0000 | +0.0471 | 0.31x | 2016-11-30 |
| `num_up_bars` | +0.1234 | +0.0000 | +0.0459 | 0.37x | 2020-02-12 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | +0.1497 | +0.0000 | +0.0923 | 0.62x | 2016-09-26 |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | +0.1524 | +0.0000 | +0.0931 | 0.61x | 2016-09-26 |
| `combo_max__net_volume_flow__max_down_ret` | +0.1571 | +0.0000 | +0.0486 | 0.31x | 2016-11-30 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | +0.1468 | +0.0000 | +0.1318 | 0.90x | 2011-10-26 |
| `early_order_flow_imbalance` | +0.1249 | +0.0000 | -0.0041 | -0.03x | 2016-11-01 |
| `combo_mean__first_bar_sentiment__max_down_ret` | +0.1427 | +0.0000 | +0.0829 | 0.58x | No decay |
| `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression` | +0.0912 | +0.0000 | +0.0730 | 0.80x | 2012-06-05 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1274 | +0.0000 | +0.1006 | 0.79x | 2016-09-26 |
| `combo_min__first_bar_sentiment__early_body_momentum` | +0.1398 | +0.0000 | +0.0600 | 0.43x | 2020-02-12 |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | +0.1229 | +0.0000 | +0.0279 | 0.23x | 2016-09-26 |
| `combo_min__volatility_expansion_trend_vector__max_down_ret` | +0.1511 | +0.0000 | +0.0883 | 0.58x | 2016-09-26 |
| `combo_max__close_vs_open_range__max_down_ret` | +0.1450 | +0.0000 | +0.0557 | 0.38x | 2016-11-01 |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1457 | +0.0000 | +0.0659 | 0.45x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | +0.1350 | +0.0000 | +0.0944 | 0.70x | 2016-08-24 |
| `combo_max__trend_day_regime_conviction__max_down_ret` | +0.1423 | +0.0000 | +0.0497 | 0.35x | 2016-11-01 |
| `combo_tri_max__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1470 | +0.0000 | +0.0756 | 0.51x | 2016-09-26 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1501 | +0.0000 | +0.0661 | 0.44x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1324 | +0.0000 | +0.0290 | 0.22x | 2017-08-08 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | +0.1301 | +0.0000 | +0.0705 | 0.54x | 2016-09-26 |
| `combo_sig_product__max_up_ret__high_low_sequence_momentum` | +0.1607 | +0.0000 | +0.0281 | 0.17x | 2018-03-16 |
| `combo_min__first_bar_return__max_down_ret` | +0.1326 | +0.0000 | +0.0728 | 0.55x | No decay |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1266 | +0.0000 | +0.1371 | 1.08x | 2016-06-27 |
| `vwap_close_divergence_trend` | +0.1298 | +0.0000 | +0.0323 | 0.25x | 2016-11-01 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | +0.1528 | +0.0000 | +0.0799 | 0.52x | 2016-11-01 |
| `max_down_ret` | +0.1371 | +0.0000 | +0.0790 | 0.58x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | +0.1085 | +0.0000 | +0.1335 | 1.23x | 2016-06-27 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | +0.1550 | +0.0000 | +0.0695 | 0.45x | 2021-07-28 |
| `vwap_trend_channel_slope` | +0.1446 | +0.0000 | +0.0398 | 0.28x | 2016-11-01 |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1749 | +0.0000 | +0.0937 | 0.54x | No decay |
| `combo_min__close_vs_open_range__first_bar_sentiment` | +0.1439 | +0.0000 | +0.0754 | 0.52x | 2020-01-06 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +0.1263 | +0.0000 | +0.0291 | 0.23x | 2017-08-08 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1392 | +0.0000 | +0.0982 | 0.71x | 2016-08-24 |
| `range_progression_trend` | +0.1120 | +0.0000 | -0.0206 | -0.18x | 2016-09-26 |
| `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression` | +0.1224 | +0.0000 | +0.0189 | 0.15x | 2016-09-26 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | +0.1509 | +0.0000 | +0.0212 | 0.14x | 2021-07-28 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | +0.1614 | +0.0000 | +0.0794 | 0.49x | 2016-09-26 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1398 | +0.0000 | +0.0986 | 0.70x | 2016-09-26 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1722 | +0.0000 | +0.1088 | 0.63x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | +0.1590 | +0.0000 | +0.0813 | 0.51x | 2016-11-30 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1563 | +0.0000 | +0.0675 | 0.43x | 2016-09-26 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1384 | +0.0000 | +0.0505 | 0.36x | 2020-12-18 |
| `combo_rank_min__close_vs_open_range__first_bar_sentiment` | +0.1403 | +0.0000 | +0.0648 | 0.46x | 2020-01-06 |
| `combo_rank_min__first_bar_return__max_down_ret` | +0.1327 | +0.0000 | +0.0622 | 0.47x | No decay |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | +0.1385 | +0.0000 | +0.0838 | 0.61x | 2016-08-24 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +0.1392 | +0.0000 | +0.1034 | 0.74x | 2011-09-20 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | +0.1439 | +0.0000 | +0.0553 | 0.38x | 2020-12-18 |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | +0.1407 | +0.0000 | +0.0630 | 0.45x | 2016-11-01 |
| `bar_body_rng_0` | +0.1346 | +0.0000 | +0.0572 | 0.42x | No decay |
| `combo_sig_product__net_volume_flow__max_down_ret` | +0.1303 | +0.0000 | +0.0521 | 0.40x | 2016-09-26 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.0594 | +0.0000 | +0.0335 | 0.56x | 2010-10-15 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_day_regime_conviction` | +0.0563 | +0.0000 | +0.0163 | 0.29x | 2010-10-15 |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | +0.1362 | +0.0000 | +0.0533 | 0.39x | 2016-11-30 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1550 | +0.0000 | +0.1275 | 0.82x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1578 | +0.0000 | +0.1339 | 0.85x | 2017-04-28 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1459 | +0.0000 | +0.1203 | 0.82x | 2011-10-18 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1410 | +0.0000 | +0.1353 | 0.96x | 2011-10-18 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | +0.1521 | +0.0000 | +0.1250 | 0.82x | 2016-10-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1620 | +0.0000 | +0.1337 | 0.82x | 2017-02-27 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1626 | +0.0000 | +0.1428 | 0.88x | 2017-02-27 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1513 | +0.0000 | +0.1258 | 0.83x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1551 | +0.0000 | +0.1296 | 0.84x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1616 | +0.0000 | +0.1258 | 0.78x | 2016-12-21 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1628 | +0.0000 | +0.1346 | 0.83x | 2017-01-20 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1644 | +0.0000 | +0.1135 | 0.69x | 2016-12-21 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1520 | +0.0000 | +0.0997 | 0.66x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1510 | +0.0000 | +0.1228 | 0.81x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1549 | +0.0000 | +0.1403 | 0.91x | 2011-11-16 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1585 | +0.0000 | +0.0985 | 0.62x | 2017-01-20 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1656 | +0.0000 | +0.1289 | 0.78x | 2017-02-27 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1553 | +0.0000 | +0.1310 | 0.84x | 2017-02-27 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1608 | +0.0000 | +0.1285 | 0.80x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1717 | +0.0000 | +0.1325 | 0.77x | 2017-01-20 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.1269 | +0.0000 | +0.1518 | 1.20x | 2011-10-18 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | +0.1610 | +0.0000 | +0.1319 | 0.82x | 2017-01-20 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | +0.1540 | +0.0000 | +0.1198 | 0.78x | 2017-01-20 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1635 | +0.0000 | +0.1319 | 0.81x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1398 | +0.0000 | +0.1347 | 0.96x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1701 | +0.0000 | +0.1318 | 0.77x | 2017-01-20 |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1381 | +0.0000 | +0.1396 | 1.01x | 2011-10-18 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1597 | +0.0000 | +0.1015 | 0.64x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1639 | +0.0000 | +0.1344 | 0.82x | 2017-02-27 |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1578 | +0.0000 | +0.1248 | 0.79x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1481 | +0.0000 | +0.1497 | 1.01x | 2016-10-24 |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | +0.1518 | +0.0000 | +0.1293 | 0.85x | 2016-10-24 |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | +0.1514 | +0.0000 | +0.1160 | 0.77x | 2017-04-28 |
| `combo_min__limit_down_proximity_early__volume_weighted_price_position` | +0.1293 | +0.0000 | +0.1345 | 1.04x | 2016-10-24 |
| `combo_mean__max_up_ret__bar_body_rng_0` | +0.1561 | +0.0000 | +0.0890 | 0.57x | 2017-02-27 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1454 | +0.0000 | +0.1073 | 0.74x | 2011-11-16 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1524 | +0.0000 | +0.1197 | 0.79x | 2017-04-28 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1543 | +0.0000 | +0.1421 | 0.92x | 2016-10-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1508 | +0.0000 | +0.1526 | 1.01x | 2016-10-24 |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | +0.1537 | +0.0000 | +0.0727 | 0.47x | 2016-12-21 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1272 | +0.0000 | +0.1316 | 1.03x | 2017-02-27 |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | +0.1421 | +0.0000 | +0.1382 | 0.97x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | +0.1457 | +0.0000 | +0.0933 | 0.64x | 2017-01-20 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +0.1503 | +0.0000 | +0.0885 | 0.59x | 2017-02-27 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1215 | +0.0000 | +0.1592 | 1.31x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1367 | +0.0000 | +0.1507 | 1.10x | 2016-09-14 |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | +0.1388 | +0.0000 | +0.1426 | 1.03x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0686 | 0.50x | 2016-10-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1105 | +0.0000 | +0.1100 | 1.00x | 2011-10-18 |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1444 | +0.0000 | +0.1102 | 0.76x | 2016-10-24 |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | +0.1274 | +0.0000 | +0.1424 | 1.12x | 2016-09-14 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1428 | +0.0000 | +0.1259 | 0.88x | 2016-09-14 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1653 | +0.0000 | +0.1295 | 0.78x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1608 | +0.0000 | +0.1308 | 0.81x | 2017-01-20 |
| `combo_min__bar_ret_0__limit_down_proximity_early` | +0.1253 | +0.0000 | +0.1467 | 1.17x | 2011-10-18 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1388 | +0.0000 | +0.1216 | 0.88x | 2017-01-20 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | +0.1573 | +0.0000 | +0.1161 | 0.74x | 2018-01-31 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | +0.1423 | +0.0000 | +0.0947 | 0.67x | 2016-10-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1584 | +0.0000 | +0.1269 | 0.80x | 2017-01-20 |
| `max_up_ret` | +0.1487 | +0.0000 | +0.0682 | 0.46x | 2017-01-20 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1012 | +0.0000 | +0.1286 | 1.27x | 2011-10-18 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1560 | +0.0000 | +0.0820 | 0.53x | 2016-12-21 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | +0.1571 | +0.0000 | +0.0717 | 0.46x | 2017-01-20 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +0.1495 | +0.0000 | +0.1120 | 0.75x | 2017-02-27 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | +0.0940 | +0.0000 | +0.1197 | 1.27x | 2011-10-18 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1520 | +0.0000 | +0.0776 | 0.51x | 2017-01-20 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1558 | +0.0000 | +0.0864 | 0.55x | 2017-01-20 |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | +0.1196 | +0.0000 | +0.0887 | 0.74x | 2017-04-28 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0944 | +0.0000 | +0.1079 | 1.14x | 2011-10-18 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +0.1239 | +0.0000 | +0.0450 | 0.36x | 2017-03-28 |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | +0.1397 | +0.0000 | +0.0976 | 0.70x | 2017-04-28 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | +0.1577 | +0.0000 | +0.0761 | 0.48x | 2017-01-20 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1483 | +0.0000 | +0.0939 | 0.63x | 2017-01-20 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1470 | +0.0000 | +0.1058 | 0.72x | 2016-09-14 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1509 | +0.0000 | +0.1491 | 0.99x | 2017-01-20 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1506 | +0.0000 | +0.1213 | 0.81x | 2017-02-27 |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | +0.1449 | +0.0000 | +0.0725 | 0.50x | 2017-01-20 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1600 | +0.0000 | +0.0948 | 0.59x | 2017-01-20 |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1481 | +0.0000 | +0.1133 | 0.76x | 2016-09-14 |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | +0.1464 | +0.0000 | +0.0770 | 0.53x | 2017-01-20 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | +0.1510 | +0.0000 | +0.1056 | 0.70x | 2016-10-24 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1345 | +0.0000 | +0.0366 | 0.27x | 2014-03-25 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1032 | +0.0000 | +0.1254 | 1.22x | 2011-10-18 |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1527 | +0.0000 | +0.1003 | 0.66x | 2016-10-24 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | +0.1355 | +0.0000 | +0.0879 | 0.65x | 2016-10-24 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1384 | +0.0000 | +0.1453 | 1.05x | 2016-09-14 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1511 | +0.0000 | +0.1055 | 0.70x | 2017-03-28 |
| `combo_mean__rbreaker_buy_setup_proximity_early__volume_weighted_price_position` | +0.1409 | +0.0000 | +0.1340 | 0.95x | 2016-10-24 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | +0.1530 | +0.0000 | +0.0757 | 0.49x | 2017-01-20 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1536 | +0.0000 | +0.1106 | 0.72x | 2016-10-24 |
| `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early` | +0.1474 | +0.0000 | +0.1338 | 0.91x | 2017-01-20 |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0` | +0.1526 | +0.0000 | +0.0860 | 0.56x | 2017-01-20 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1539 | +0.0000 | +0.1220 | 0.79x | 2017-02-27 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | +0.1467 | +0.0000 | +0.0811 | 0.55x | 2017-01-20 |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1541 | +0.0000 | +0.0738 | 0.48x | 2016-10-24 |
| `combo_max__max_up_ret__impulse_bar_dominance` | +0.1276 | +0.0000 | +0.0516 | 0.40x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | +0.1294 | +0.0000 | +0.0441 | 0.34x | 2017-01-20 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1442 | +0.0000 | +0.1138 | 0.79x | 2016-09-14 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1149 | +0.0000 | +0.1394 | 1.21x | 2011-10-18 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1317 | +0.0000 | +0.1308 | 0.99x | 2011-10-18 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1219 | +0.0000 | +0.1155 | 0.95x | 2017-01-20 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | +0.1471 | +0.0000 | +0.1065 | 0.72x | 2017-01-20 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | +0.1451 | +0.0000 | +0.1428 | 0.98x | 2016-09-14 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1558 | +0.0000 | +0.0786 | 0.50x | 2016-12-21 |
| `combo_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector` | +0.1265 | +0.0000 | +0.1386 | 1.10x | 2011-10-18 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +0.1539 | +0.0000 | +0.0732 | 0.48x | 2016-12-21 |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | +0.1163 | +0.0000 | +0.1145 | 0.98x | 2011-10-18 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1438 | +0.0000 | +0.0827 | 0.57x | 2017-01-20 |
| `bar_body_rng_0` | +0.1345 | +0.0000 | +0.0977 | 0.73x | 2017-02-27 |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | +0.1491 | +0.0000 | +0.0636 | 0.43x | 2017-03-28 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1300 | +0.0000 | +0.1028 | 0.79x | 2016-10-24 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | +0.1500 | +0.0000 | +0.0906 | 0.60x | 2017-02-27 |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | +0.1541 | +0.0000 | +0.0894 | 0.58x | 2017-01-20 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1190 | +0.0000 | +0.0936 | 0.79x | 2017-02-27 |
| `combo_min__limit_down_proximity_early__impulse_bar_dominance` | +0.1078 | +0.0000 | +0.1106 | 1.03x | 2011-10-18 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0659 | 0.48x | 2017-04-28 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1195 | +0.0000 | +0.0913 | 0.76x | 2011-12-15 |
| `combo_min__max_up_ret__bar_ret_0` | +0.1477 | +0.0000 | +0.0839 | 0.57x | 2017-01-20 |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | +0.1337 | +0.0000 | +0.0968 | 0.72x | 2016-10-24 |
| `opening_drive_thrust_ratio` | +0.1447 | +0.0000 | +0.0792 | 0.55x | 2016-10-24 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1405 | +0.0000 | +0.0785 | 0.56x | 2014-03-25 |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | +0.1290 | +0.0000 | +0.0960 | 0.74x | 2017-01-20 |
| `combo_min__bar_body_rng_0__first_bar_return` | +0.1392 | +0.0000 | +0.0874 | 0.63x | 2017-02-27 |
| `combo_mean__bar_ret_0__volume_weighted_price_position` | +0.1445 | +0.0000 | +0.0739 | 0.51x | 2017-01-20 |
| `combo_max__bar_body_rng_0__limit_down_proximity_early` | +0.1331 | +0.0000 | +0.1023 | 0.77x | 2017-02-27 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.1462 | +0.0000 | +0.0743 | 0.51x | 2017-04-28 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1330 | +0.0000 | +0.0366 | 0.28x | 2016-11-22 |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1491 | +0.0000 | +0.0841 | 0.56x | 2016-12-21 |
| `first_bar_return` | +0.1391 | +0.0000 | +0.0748 | 0.54x | 2017-04-28 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1507 | +0.0000 | +0.0764 | 0.51x | 2017-01-20 |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | +0.1294 | +0.0000 | +0.1036 | 0.80x | 2017-01-20 |
| `combo_rank_min__bar_body_rng_0__volatility_expansion_trend_vector` | +0.1293 | +0.0000 | +0.1097 | 0.85x | 2016-10-24 |
| `combo_sig_product__max_up_ret__first_bar_return` | +0.1455 | +0.0000 | +0.0786 | 0.54x | 2018-01-31 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1172 | +0.0000 | +0.0813 | 0.69x | 2016-10-24 |
| `combo_rank_min__max_up_ret__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0645 | 0.47x | 2017-01-20 |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1360 | +0.0000 | +0.0893 | 0.66x | 2016-10-24 |
| `combo_max__first_bar_sentiment__bar_ret_0` | +0.1340 | +0.0000 | +0.0775 | 0.58x | 2017-04-28 |
| `net_volume_flow` | +0.1340 | +0.0000 | +0.0979 | 0.73x | 2014-03-25 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1422 | +0.0000 | +0.1031 | 0.72x | 2016-10-24 |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.0993 | +0.0000 | +0.0936 | 0.94x | 2013-04-09 |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | +0.1357 | +0.0000 | +0.0759 | 0.56x | 2017-04-28 |
| `combo_max__bar_ret_0__impulse_bar_dominance` | +0.1223 | +0.0000 | +0.0681 | 0.56x | 2017-01-20 |
| `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | +0.1263 | +0.0000 | +0.0796 | 0.63x | 2016-10-24 |
| `combo_diff__max_up_ret__late_bar_momentum` | +0.1289 | +0.0000 | +0.0739 | 0.57x | 2017-01-20 |
| `volatility_expansion_trend_vector` | +0.1290 | +0.0000 | +0.0926 | 0.72x | 2016-10-24 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0604 | +0.0000 | -0.0153 | -0.25x | 2012-01-17 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | +0.1273 | +0.0000 | +0.0278 | 0.22x | 2016-12-21 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.1641). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.4187). Consider relaxing this gate.
3. **300ETF `single` — B4 Correlation Gate too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.6290). Consider relaxing this gate.
4. **300ETF `single` — Admission too loose**: 91% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
5. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 6.0%, mean lock Sharpe=-0.5144). Consider relaxing this gate.
6. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.3478). Consider relaxing this gate.
7. **300ETF `short` — B2 Rolling Guard too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.2144). Consider relaxing this gate.
8. **300ETF `short` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.1920). Consider relaxing this gate.
9. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.1022). Consider relaxing this gate.
10. **50ETF `single` — B2 Rolling Guard too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.0918). Consider relaxing this gate.
11. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.1306). Consider relaxing this gate.
12. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=-0.1073). Consider relaxing this gate.
13. **500ETF `single` — Admission too loose**: 68% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
14. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.3640). Consider relaxing this gate.
15. **500ETF `long` — BH-FDR Gate too strict**: 73.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.4499). Consider relaxing this gate.
16. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3004). Consider relaxing this gate.
17. **500ETF `short` — B2 Rolling Guard too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3230). Consider relaxing this gate.
18. **159915ETF `single` — B3 Composite Floor too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 52.0%, mean lock Sharpe=+0.3832). Consider relaxing this gate.
19. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 52.0%, mean lock Sharpe=+1.0483). Consider relaxing this gate.
20. **159915ETF `long` — BH-FDR Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 43.0%, mean lock Sharpe=+0.8546). Consider relaxing this gate.
21. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=-0.1211). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
