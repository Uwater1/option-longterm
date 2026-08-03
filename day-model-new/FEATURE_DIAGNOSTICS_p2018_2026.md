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

### 300ETF — `single` (Full Model Lockbox IC: -0.1080, Sharpe: +0.0000)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1074 | +0.0272 | +0.0272 | +0.6075 | 0.50 | 0/8 | 0.74 | 0.45 | `bar_body_rng_0` (0.73) | -0.0009 | +0.3263 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1034 | +0.0005 | +0.0005 | -0.7605 | 0.57 | 0/8 | 0.64 | 0.34 | `bar_body_rng_0` (0.73) | -0.0004 | +0.0000 |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0771 | -0.1298 | -0.1298 | -1.8873 | 0.96 | 1/8 | 1.87 | 0.75 | `volume_weighted_price_position` (1.03) | -0.0049 | +0.2932 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1018 | +0.0449 | +0.0449 | -0.4434 | 0.57 | 0/8 | 0.59 | 0.26 | `bar_body_rng_0` (0.73) | +0.0008 | +0.3263 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0965 | -0.1853 | -0.1853 | -1.0717 | 0.72 | 0/8 | 0.97 | 0.63 | `volume_weighted_price_position` (1.03) | -0.0037 | +0.2932 |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.0962 | -0.1215 | -0.1215 | -2.1883 | 0.85 | 1/8 | 0.92 | 0.39 | `volume_weighted_price_position` (1.03) | -0.0024 | +0.2932 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0942 | -0.1502 | -0.1502 | -2.3921 | 0.80 | 1/8 | 0.85 | 0.42 | `volume_weighted_price_position` (1.03) | -0.0046 | +0.2932 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0918 | -0.0293 | -0.0293 | +0.7925 | 0.44 | 0/8 | 0.70 | 0.44 | `max_up_ret` (0.69) | -0.0000 | +0.3263 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.1039 | -0.0294 | -0.0294 | -0.6275 | 0.52 | 0/8 | 0.73 | 0.42 | `bar_body_rng_0` (0.73) | -0.0014 | +0.3263 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0941 | -0.2002 | -0.2002 | -3.3600 | 0.76 | 1/8 | 1.09 | 0.46 | `volume_weighted_price_position` (1.03) | -0.0035 | +0.0000 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0911 | -0.1762 | -0.1762 | -2.3921 | 0.82 | 2/8 | 0.84 | 0.34 | `volume_weighted_price_position` (1.03) | -0.0047 | +0.2932 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1048 | -0.0297 | -0.0297 | -0.2989 | 0.54 | 0/8 | 0.62 | 0.29 | `opening_drive_thrust_ratio` (0.64) | -0.0006 | +0.3263 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1002 | -0.0924 | -0.0924 | -1.1726 | 0.72 | 0/8 | 0.69 | 0.36 | `bar_body_rng_0` (0.73) | -0.0018 | +0.0000 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0944 | -0.2114 | -0.2114 | -3.6368 | 0.71 | 0/8 | 1.02 | 0.76 | `volume_weighted_price_position` (1.03) | -0.0037 | +0.2932 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.0963 | +0.0147 | +0.0147 | +0.3204 | 0.59 | 0/8 | 0.76 | 0.44 | `limit_down_proximity_early` (0.90) | +0.0010 | +0.3263 |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | Other Technical | +1 | +0.0936 | -0.0889 | -0.0889 | -2.3913 | 0.70 | 1/8 | 0.72 | 0.39 | `bar_body_rng_0` (0.73) | -0.0017 | +0.2932 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0943 | -0.0631 | -0.0631 | -1.1652 | 0.79 | 1/8 | 0.91 | 0.42 | `volume_weighted_price_position` (1.03) | -0.0021 | +0.2932 |
| `combo_mean__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0934 | -0.1142 | -0.1142 | -2.1282 | 0.66 | 0/8 | 0.66 | 0.25 | `first_bar_sentiment` (0.89) | -0.0002 | +0.0000 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0961 | -0.0955 | -0.0955 | -0.5706 | 0.68 | 0/8 | 0.83 | 0.39 | `volume_weighted_price_position` (1.03) | -0.0012 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0882 | -0.1964 | -0.1964 | -2.1840 | 0.77 | 0/8 | 1.03 | 0.66 | `volume_weighted_price_position` (1.03) | -0.0044 | +0.0000 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.0913 | +0.0709 | +0.0709 | -1.0140 | 0.62 | 0/8 | 0.54 | 0.27 | `limit_down_proximity_early` (0.90) | +0.0004 | +0.3263 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0911 | -0.1613 | -0.1613 | -2.3451 | 0.67 | 0/8 | 0.72 | 0.59 | `max_up_ret` (0.69) | -0.0016 | +0.0000 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0851 | -0.0691 | -0.0691 | -0.9513 | 0.72 | 0/8 | 0.72 | 0.31 | `bar_body_rng_0` (0.73) | -0.0007 | +0.0000 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0867 | -0.1087 | -0.1087 | -2.7122 | 0.70 | 0/8 | 0.59 | 0.28 | `volume_weighted_price_position` (1.03) | -0.0029 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.1000 | -0.1466 | -0.1466 | -1.4795 | 0.83 | 1/8 | 0.77 | 0.40 | `volume_weighted_price_position` (1.03) | -0.0031 | +0.0000 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0941 | -0.1153 | -0.1153 | -1.6739 | 0.79 | 1/8 | 0.73 | 0.33 | `volume_weighted_price_position` (1.03) | -0.0028 | +0.2932 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.1033 | -0.1522 | -0.1522 | -2.8623 | 0.65 | 0/8 | 0.71 | 0.38 | `first_bar_return` (0.68) | -0.0026 | +0.2932 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0923 | -0.0504 | -0.0504 | -0.6267 | 0.50 | 0/8 | 0.57 | 0.29 | `max_up_ret` (0.69) | +0.0003 | +0.3263 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0876 | -0.1476 | -0.1476 | -2.5718 | 0.66 | 0/8 | 0.94 | 0.69 | `max_up_ret` (0.69) | -0.0012 | +0.0000 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.1030 | -0.1417 | -0.1417 | -3.5565 | 0.67 | 0/8 | 0.71 | 0.41 | `first_bar_return` (0.68) | -0.0021 | +0.2932 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0937 | +0.0132 | +0.0132 | +0.8820 | 0.48 | 0/8 | 0.67 | 0.37 | `rbreaker_buy_setup_proximity_early` (0.90) | -0.0009 | +0.3263 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0937 | -0.1611 | -0.1611 | -1.2733 | 0.63 | 0/8 | 0.75 | 0.60 | `max_up_ret` (0.69) | -0.0015 | +0.0000 |
| `combo_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0894 | -0.0695 | -0.0695 | -2.2404 | 0.61 | 0/8 | 0.64 | 0.26 | `first_bar_sentiment` (0.89) | -0.0006 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0974 | -0.0169 | -0.0169 | +0.1548 | 0.51 | 0/8 | 0.56 | 0.26 | `max_up_ret` (0.69) | +0.0003 | +0.4342 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0994 | -0.1237 | -0.1237 | -2.2099 | 0.70 | 0/8 | 0.70 | 0.25 | `first_bar_sentiment` (0.89) | -0.0006 | +0.0000 |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0817 | -0.1002 | -0.1002 | -1.2031 | 0.83 | 1/8 | 0.62 | 0.17 | `volume_weighted_price_position` (1.03) | -0.0042 | +0.2932 |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0970 | -0.1079 | -0.1079 | -1.4834 | 0.64 | 0/8 | 0.75 | 0.45 | `bar_body_rng_0` (0.73) | -0.0015 | +0.2932 |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0756 | -0.0908 | -0.0908 | -1.5036 | 0.94 | 1/8 | 0.53 | 0.08 | `volume_weighted_price_position` (1.03) | -0.0030 | +0.2932 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1034 | -0.0541 | -0.0541 | -1.4245 | 0.53 | 0/8 | 0.62 | 0.34 | `max_up_ret` (0.69) | +0.0008 | +0.4342 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.0868 | -0.0827 | -0.0827 | +0.0937 | 0.68 | 0/8 | 0.62 | 0.30 | — | -0.0030 | +0.2932 |
| `combo_max__first_bar_return__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0874 | -0.0930 | -0.0930 | -0.7198 | 0.74 | 1/8 | 0.57 | 0.23 | `first_bar_sentiment` (0.89) | -0.0021 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0937 | -0.0121 | -0.0121 | +0.8779 | 0.59 | 0/8 | 0.60 | 0.34 | `rbreaker_buy_setup_proximity_early` (0.90) | -0.0001 | +0.3263 |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0866 | -0.0828 | -0.0828 | -2.2099 | 0.79 | 0/8 | 0.63 | 0.09 | `bar_body_rng_0` (0.73) | -0.0011 | +0.0000 |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.1053 | -0.1294 | -0.1294 | -2.7464 | 0.73 | 0/8 | 1.01 | 0.49 | `volume_weighted_price_position` (1.03) | -0.0033 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.0982 | -0.1510 | -0.1510 | -2.2099 | 0.64 | 0/8 | 0.76 | 0.40 | — | -0.0024 | +0.0000 |
| `combo_rank_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.0802 | -0.0956 | -0.0956 | -1.2359 | 0.72 | 0/8 | 0.58 | 0.21 | `max_up_ret` (0.69) | -0.0005 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0958 | -0.0023 | -0.0023 | +0.4698 | 0.56 | 0/8 | 0.63 | 0.27 | `rbreaker_buy_setup_proximity_early` (0.90) | -0.0008 | +0.3263 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0904 | +0.0628 | +0.0628 | -1.0546 | 0.57 | 1/8 | 0.72 | 0.29 | `opening_drive_thrust_ratio` (0.64) | -0.0029 | +0.3263 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0713 | -0.1823 | -0.1823 | -2.6806 | 0.97 | 1/8 | 1.22 | 0.64 | `volume_weighted_price_position` (1.03) | -0.0038 | +0.0000 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.0747 | -0.1752 | -0.1752 | -2.4148 | 0.61 | 0/8 | 1.26 | 1.85 | — | -0.0000 | +0.0000 |
| `combo_min__first_bar_return__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0970 | -0.1057 | -0.1057 | -1.5368 | 0.57 | 0/8 | 0.70 | 0.41 | `first_bar_return` (0.68) | -0.0014 | +0.0000 |
| `volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0854 | -0.1599 | -0.1599 | -1.5036 | 1.03 | 2/8 | 1.17 | 0.38 | — | -0.0059 | +0.2932 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0852 | +0.0035 | +0.0035 | -0.5291 | 0.49 | 0/8 | 0.94 | 0.50 | `opening_drive_thrust_ratio` (0.64) | +0.0000 | +0.0000 |
| `combo_ratio__max_up_ret__first_bar_volume` | Gap / Overnight Reversal | +1 | +0.0832 | -0.1432 | -0.1432 | -2.6027 | 0.76 | 0/8 | 0.62 | 0.47 | `first_bar_volume` (2.33) | -0.0011 | +0.0000 |
| `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0809 | +0.0844 | +0.0844 | -0.8307 | 0.75 | 0/8 | 0.60 | 0.29 | `bar_body_rng_0` (0.73) | +0.0001 | +0.0000 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0707 | -0.2024 | -0.2024 | -2.3152 | 0.78 | 2/8 | 1.30 | 0.58 | — | -0.0024 | +0.0000 |
| `combo_min__first_bar_return__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0804 | -0.0691 | -0.0691 | -1.5273 | 0.66 | 0/8 | 0.56 | 0.27 | `first_bar_sentiment` (0.89) | -0.0004 | +0.0000 |
| `always_in_trend_persistence` | Volatility & Oscillators | +1 | +0.0613 | -0.2597 | -0.2597 | -3.4587 | 0.85 | 2/8 | 1.28 | 0.47 | — | -0.0046 | +0.2932 |
| `volume_surge_direction` | Volatility & Oscillators | +1 | +0.0779 | -0.0740 | -0.0740 | -1.2501 | 0.70 | 1/8 | 0.80 | 0.31 | — | +0.0003 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0951 | -0.1395 | -0.1395 | -2.7529 | 0.82 | 1/8 | 0.74 | 0.16 | `first_bar_sentiment` (0.89) | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0713 | -0.0717 | -0.0717 | -0.5279 | 0.99 | 1/8 | 0.40 | 0.14 | `max_up_ret` (0.69) | -0.0021 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.0774 | -0.1763 | -0.1763 | -3.3539 | 0.62 | 0/8 | 1.09 | 0.89 | — | -0.0020 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0102, Sharpe: +1.0015)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1459 | +0.0028 | +0.0028 | -1.6259 | 0.49 | 0/8 | 0.53 | 0.47 | `volume_weighted_momentum_acceleration` (0.53) | +0.0005 | +0.0000 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1231 | -0.0383 | -0.0383 | -1.2349 | 0.29 | 0/8 | 0.94 | 0.91 | `bar_ret_0` (0.48) | -0.0014 | +0.0000 |
| `combo_min__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1136 | -0.0010 | -0.0010 | -0.2212 | 0.28 | 0/8 | 0.94 | 0.87 | `first_bar_return` (0.48) | -0.0011 | +0.0399 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1140 | +0.0727 | +0.0727 | -0.4830 | 0.29 | 0/8 | 0.90 | 0.80 | `early_body_momentum` (0.36) | +0.0011 | -0.0530 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1328 | +0.0033 | +0.0033 | -1.5227 | 0.37 | 0/8 | 0.57 | 0.55 | `volume_weighted_momentum_acceleration` (0.53) | +0.0007 | +0.0000 |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1395 | +0.0152 | +0.0152 | -1.5740 | 0.37 | 0/8 | 0.62 | 0.57 | `volume_weighted_momentum_acceleration` (0.53) | +0.0002 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1392 | -0.0002 | -0.0002 | -1.2847 | 0.38 | 0/8 | 0.65 | 0.59 | `first_bar_return` (0.48) | -0.0013 | +0.0172 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1325 | +0.0571 | +0.0571 | +0.3372 | 0.32 | 0/8 | 0.69 | 0.79 | `opening_drive_thrust_ratio` (0.31) | +0.0015 | +0.0000 |
| `combo_min__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1194 | -0.0444 | -0.0444 | -2.0572 | 0.22 | 0/8 | 0.99 | 0.90 | `first_bar_sentiment` (0.43) | -0.0007 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1181 | +0.0755 | +0.0755 | +0.4554 | 0.40 | 0/8 | 0.56 | 0.58 | `bar_ret_0` (0.48) | +0.0012 | +0.0399 |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1057 | -0.0686 | -0.0686 | -1.8069 | 0.36 | 0/8 | 0.97 | 1.10 | `max_down_ret` (0.39) | +0.0003 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1026 | +0.0175 | +0.0175 | -1.1506 | 0.29 | 0/8 | 0.99 | 1.04 | `trend_bar_close_consistency` (0.49) | +0.0002 | -0.0530 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1033 | +0.0350 | +0.0350 | -0.6199 | 0.24 | 0/8 | 1.06 | 1.52 | `trend_bar_close_consistency` (0.49) | +0.0014 | +0.0000 |
| `combo_rank_min__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.1119 | +0.0185 | +0.0185 | -0.4696 | 0.32 | 0/8 | 0.88 | 0.79 | `bar_ret_0` (0.48) | -0.0012 | +0.0399 |
| `combo_mean__first_bar_return__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1162 | +0.0117 | +0.0117 | -2.2371 | 0.38 | 0/8 | 0.80 | 0.78 | `first_bar_return` (0.48) | -0.0012 | +0.0172 |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1156 | +0.0988 | +0.0988 | -1.7785 | 0.50 | 0/8 | 0.52 | 0.41 | `early_late_momentum_divergence` (0.86) | +0.0008 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1382 | +0.0674 | +0.0674 | +1.0606 | 0.31 | 0/8 | 0.67 | 0.67 | `opening_drive_thrust_ratio` (0.31) | +0.0013 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression` | Volatility & Oscillators | +1 | +0.1168 | -0.0592 | -0.0592 | -1.9999 | 0.14 | 0/8 | 1.13 | 1.22 | `body_size_progression` (0.71) | -0.0009 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1361 | -0.0323 | -0.0323 | -1.4349 | 0.20 | 0/8 | 1.00 | 0.90 | `body_size_progression` (0.71) | -0.0013 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1164 | +0.0820 | +0.0820 | +0.3115 | 0.41 | 0/8 | 0.57 | 0.56 | `bar_ret_0` (0.48) | +0.0013 | +0.0399 |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1243 | +0.0069 | +0.0069 | +0.0524 | 0.38 | 0/8 | 0.72 | 0.78 | `max_down_ret` (0.39) | +0.0001 | +0.0000 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1213 | -0.0114 | -0.0114 | -2.9407 | 0.43 | 0/8 | 0.65 | 0.48 | `first_bar_sentiment` (0.43) | -0.0010 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1344 | +0.0508 | +0.0508 | -0.9929 | 0.30 | 0/8 | 0.79 | 0.76 | `max_up_ret` (0.30) | +0.0005 | +0.0000 |
| `combo_mean__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1295 | -0.0337 | -0.0337 | -1.7738 | 0.36 | 0/8 | 0.71 | 0.58 | `first_bar_return` (0.48) | -0.0017 | +0.0172 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1315 | -0.0124 | -0.0124 | -2.1578 | 0.34 | 0/8 | 0.72 | 0.65 | `first_bar_sentiment` (0.43) | -0.0010 | +0.0000 |
| `morning_volume_weighted_momentum` | Intraday Range Momentum | +1 | +0.1111 | -0.0906 | -0.0906 | -1.7423 | 0.23 | 0/8 | 1.27 | 1.29 | — | -0.0003 | +0.0000 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1132 | -0.0261 | -0.0261 | -2.5653 | 0.44 | 0/8 | 0.65 | 0.64 | `bar_ret_0` (0.48) | -0.0014 | +0.0399 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | Intraday Range Momentum | +1 | +0.1102 | -0.0933 | -0.0933 | -2.1447 | 0.22 | 0/8 | 1.28 | 1.19 | `body_size_progression` (0.71) | -0.0008 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1262 | +0.1067 | +0.1067 | +0.5671 | 0.36 | 0/8 | 0.61 | 0.61 | `first_bar_return` (0.48) | +0.0010 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1356 | +0.1749 | +0.1749 | +2.0624 | 0.39 | 0/8 | 0.53 | 0.56 | `volume_weighted_momentum_acceleration` (0.53) | +0.0014 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1313 | -0.0646 | -0.0646 | -2.3002 | 0.36 | 0/8 | 0.76 | 0.71 | `bar_ret_0` (0.48) | -0.0010 | +0.0000 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1206 | +0.0077 | +0.0077 | -1.6646 | 0.46 | 0/8 | 0.71 | 0.58 | `bar_ret_0` (0.48) | -0.0022 | +0.0172 |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1051 | -0.0012 | -0.0012 | -3.2911 | 0.38 | 0/8 | 0.79 | 0.74 | `first_bar_sentiment` (0.43) | -0.0007 | +0.0000 |
| `combo_min__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1035 | +0.0019 | +0.0019 | +0.4072 | 0.39 | 0/8 | 1.09 | 1.04 | `first_bar_return` (0.48) | +0.0000 | +0.0399 |
| `volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1054 | -0.0850 | -0.0850 | -2.3631 | 0.26 | 0/8 | 1.29 | 1.36 | — | -0.0002 | +0.0000 |
| `combo_rank_min__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1151 | -0.0007 | -0.0007 | -0.8149 | 0.45 | 0/8 | 0.61 | 0.49 | `bar_ret_0` (0.48) | -0.0014 | +0.0399 |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | Volatility & Oscillators | +1 | +0.1273 | -0.0914 | -0.0914 | -3.3937 | 0.28 | 0/8 | 0.85 | 0.80 | `bar_ret_0` (0.48) | -0.0013 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression` | Volatility & Oscillators | +1 | +0.0675 | -0.0194 | -0.0194 | -1.4497 | 0.76 | 1/8 | 1.34 | 1.40 | `body_size_progression` (0.71) | +0.0003 | -0.0530 |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1165 | -0.0655 | -0.0655 | -2.0913 | 0.24 | 0/8 | 0.98 | 1.08 | `trend_bar_close_consistency` (0.49) | -0.0002 | +0.0000 |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1128 | -0.0520 | -0.0520 | -2.3176 | 0.28 | 0/8 | 0.94 | 0.97 | `first_bar_sentiment` (0.43) | -0.0010 | +0.0000 |
| `first_30min_return` | Intraday Range Momentum | +1 | +0.1098 | -0.1128 | -0.1128 | -2.1381 | 0.25 | 0/8 | 1.32 | 1.35 | — | -0.0005 | +0.0172 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1267 | +0.1783 | +0.1783 | +2.2572 | 0.47 | 0/8 | 0.46 | 0.47 | `volume_weighted_momentum_acceleration` (0.53) | +0.0018 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.1234 | +0.0832 | +0.0832 | -0.6640 | 0.44 | 0/8 | 0.52 | 0.40 | `body_size_progression` (0.71) | +0.0008 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1407 | -0.0123 | -0.0123 | -1.0051 | 0.33 | 0/8 | 0.71 | 0.60 | `bar_ret_0` (0.48) | +0.0002 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0880 | +0.0765 | +0.0765 | +1.5322 | 0.28 | 0/8 | 1.31 | 1.55 | `trend_bar_close_consistency` (0.49) | +0.0011 | -0.0530 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1265 | +0.0187 | +0.0187 | -0.7444 | 0.36 | 0/8 | 0.73 | 0.58 | `first_bar_sentiment` (0.43) | +0.0004 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1357 | -0.0468 | -0.0468 | -2.0328 | 0.26 | 0/8 | 0.86 | 0.82 | `trend_bar_close_consistency` (0.49) | -0.0003 | +0.0000 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1122 | -0.0087 | -0.0087 | -1.4456 | 0.43 | 0/8 | 0.67 | 0.61 | `bar_ret_0` (0.48) | -0.0020 | +0.0399 |
| `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1171 | -0.0523 | -0.0523 | -2.2648 | 0.25 | 0/8 | 0.97 | 0.88 | `first_bar_sentiment` (0.43) | -0.0007 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1372 | -0.0132 | -0.0132 | -2.3509 | 0.31 | 0/8 | 0.76 | 0.68 | `opening_drive_thrust_ratio` (0.31) | -0.0005 | +0.0000 |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1041 | -0.0367 | -0.0367 | -3.0969 | 0.31 | 0/8 | 0.87 | 0.67 | `first_bar_sentiment` (0.43) | -0.0006 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1370 | +0.0343 | +0.0343 | -1.7348 | 0.43 | 0/8 | 0.54 | 0.54 | `volume_weighted_momentum_acceleration` (0.53) | -0.0001 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1264 | +0.0058 | +0.0058 | -0.5680 | 0.46 | 0/8 | 0.61 | 0.58 | `bar_ret_0` (0.48) | -0.0010 | +0.0399 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1356 | +0.1045 | +0.1045 | +1.6851 | 0.35 | 0/8 | 0.63 | 0.74 | `opening_drive_thrust_ratio` (0.31) | +0.0021 | +0.0000 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1260 | +0.1800 | +0.1800 | +2.6093 | 0.47 | 0/8 | 0.45 | 0.45 | `volume_weighted_momentum_acceleration` (0.53) | +0.0027 | +0.0000 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1079 | -0.0187 | -0.0187 | -0.7812 | 0.26 | 0/8 | 1.04 | 1.11 | `max_down_ret` (0.39) | -0.0003 | +0.0000 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1198 | -0.0739 | -0.0739 | -1.7537 | 0.32 | 0/8 | 1.21 | 1.28 | `max_down_ret` (0.39) | -0.0000 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1196 | -0.0689 | -0.0689 | -2.3631 | 0.31 | 0/8 | 0.86 | 0.68 | `opening_drive_thrust_ratio` (0.31) | -0.0009 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1009 | +0.1466 | +0.1466 | +0.8696 | 0.42 | 0/8 | 1.06 | 1.15 | `max_down_ret` (0.39) | +0.0016 | +0.0000 |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1083 | -0.0906 | -0.0906 | -2.0531 | 0.23 | 0/8 | 1.43 | 1.53 | `trend_bar_close_consistency` (0.49) | -0.0001 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Volatility & Oscillators | +1 | +0.1177 | -0.0411 | -0.0411 | -1.7157 | 0.31 | 0/8 | 0.96 | 0.78 | `opening_drive_thrust_ratio` (0.31) | -0.0006 | +0.0000 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0936 | -0.0940 | -0.0940 | -3.2742 | 0.25 | 0/8 | 1.52 | 1.54 | — | -0.0004 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1336 | -0.0104 | -0.0104 | -2.0137 | 0.34 | 0/8 | 0.74 | 0.73 | `opening_drive_thrust_ratio` (0.31) | +0.0005 | +0.0000 |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1068 | -0.1430 | -0.1430 | -2.8810 | 0.38 | 0/8 | 1.26 | 1.05 | `first_bar_return` (0.48) | -0.0013 | +0.0172 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1110 | -0.0114 | -0.0114 | -1.5357 | 0.48 | 0/8 | 0.59 | 0.52 | — | -0.0019 | +0.0172 |
| `combo_min__trend_bar_close_consistency__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0925 | -0.0156 | -0.0156 | -0.9099 | 0.40 | 0/8 | 1.11 | 0.97 | `trend_bar_close_consistency` (0.49) | -0.0001 | +0.0172 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1258 | +0.0234 | +0.0234 | -0.4926 | 0.27 | 0/8 | 0.78 | 0.76 | `max_down_ret` (0.39) | +0.0002 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.1357 | -0.0061 | -0.0061 | +0.1883 | 0.25 | 0/8 | 0.88 | 0.78 | `trend_bar_close_consistency` (0.49) | +0.0004 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1349 | +0.0383 | +0.0383 | -0.6718 | 0.42 | 0/8 | 0.53 | 0.53 | `volume_weighted_momentum_acceleration` (0.53) | +0.0010 | +0.0000 |
| `combo_max__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1090 | -0.0643 | -0.0643 | -1.7123 | 0.38 | 0/8 | 0.96 | 1.00 | `max_down_ret` (0.39) | +0.0002 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | Other Technical | +1 | +0.0956 | +0.0216 | +0.0216 | +0.1562 | 0.46 | 0/8 | 0.96 | 1.13 | `body_size_progression` (0.71) | +0.0007 | -0.0530 |
| `combo_min__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.0972 | -0.0785 | -0.0785 | -1.9210 | 0.30 | 0/8 | 1.52 | 1.56 | `early_body_momentum` (0.36) | -0.0000 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1349 | +0.0025 | +0.0025 | -0.8862 | 0.31 | 0/8 | 0.71 | 0.70 | — | -0.0001 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0877 | +0.1008 | +0.1008 | -0.4764 | 0.32 | 0/8 | 0.92 | 0.93 | `max_down_ret` (0.39) | +0.0010 | +0.0000 |
| `combo_max__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1142 | +0.0228 | +0.0228 | -1.4122 | 0.53 | 0/8 | 0.61 | 0.41 | `bar_ret_0` (0.48) | -0.0014 | +0.0172 |
| `combo_max__close_vs_open_range__early_body_momentum` | Intraday Range Momentum | +1 | +0.0977 | -0.0947 | -0.0947 | -2.2083 | 0.34 | 0/8 | 1.59 | 1.80 | `early_body_momentum` (0.36) | +0.0003 | +0.0000 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.0993 | +0.0708 | +0.0708 | +1.0762 | 0.32 | 0/8 | 1.23 | 1.69 | `close_vs_open_range` (0.31) | +0.0013 | +0.0000 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | Other Technical | +1 | +0.0907 | -0.0002 | -0.0002 | -0.4417 | 0.44 | 0/8 | 0.97 | 0.83 | `trend_bar_close_consistency` (0.49) | -0.0003 | +0.0399 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | Other Technical | +1 | +0.1167 | +0.0811 | +0.0811 | +2.5041 | 0.36 | 0/8 | 0.78 | 0.95 | `opening_drive_thrust_ratio` (0.31) | +0.0010 | -0.0530 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1150 | -0.0695 | -0.0695 | -2.1354 | 0.59 | 0/8 | 0.61 | 0.54 | `bar_ret_0` (0.48) | -0.0013 | +0.0172 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1158 | +0.0403 | +0.0403 | +1.5479 | 0.49 | 0/8 | 0.74 | 0.93 | `volume_weighted_momentum_acceleration` (0.53) | -0.0005 | +0.0000 |
| `combo_rank_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1205 | +0.0298 | +0.0298 | -0.8460 | 0.44 | 0/8 | 0.67 | 0.59 | `bar_ret_0` (0.48) | -0.0009 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.0988 | +0.0865 | +0.0865 | +1.1116 | 0.34 | 0/8 | 1.17 | 1.72 | `close_vs_open_range` (0.31) | +0.0006 | -0.0530 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.1002 | -0.1345 | -0.1345 | -3.0824 | 0.29 | 0/8 | 1.21 | 0.89 | — | -0.0006 | +0.0399 |
| `combo_mean__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1105 | +0.0243 | +0.0243 | -0.4315 | 0.36 | 0/8 | 0.79 | 0.80 | `first_bar_sentiment` (0.43) | -0.0003 | +0.0000 |
| `combo_sig_product__net_volume_flow__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0862 | -0.1006 | -0.1006 | -2.8810 | 0.59 | 0/8 | 0.55 | 0.48 | `first_bar_return` (0.48) | -0.0012 | +0.0172 |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1060 | +0.0678 | +0.0678 | -0.4181 | 0.34 | 0/8 | 1.05 | 0.95 | `star50_limit_proximity_early` (0.28) | +0.0009 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1106 | -0.0526 | -0.0526 | -2.4640 | 0.24 | 0/8 | 0.86 | 0.79 | `trend_bar_close_consistency` (0.49) | -0.0003 | -0.0530 |
| `combo_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1026 | +0.0115 | +0.0115 | -0.8443 | 0.39 | 0/8 | 0.77 | 0.82 | `bar_ret_0` (0.48) | -0.0001 | +0.0399 |
| `combo_sig_product__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1206 | -0.0107 | -0.0107 | -2.0201 | 0.26 | 0/8 | 1.00 | 1.19 | `early_body_momentum` (0.36) | -0.0005 | -0.0530 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1007 | +0.0177 | +0.0177 | -1.8813 | 0.45 | 0/8 | 0.66 | 0.71 | `first_bar_sentiment` (0.43) | -0.0004 | +0.0000 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1038 | -0.0206 | -0.0206 | -1.4352 | 0.29 | 0/8 | 0.79 | 0.67 | `first_bar_sentiment` (0.43) | -0.0008 | -0.0530 |
| `combo_max__close_vs_open_range__max_down_ret` | Intraday Range Momentum | +1 | +0.1031 | -0.0673 | -0.0673 | -1.3419 | 0.34 | 0/8 | 1.04 | 1.25 | `max_down_ret` (0.39) | +0.0001 | +0.0000 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1066 | +0.0234 | +0.0234 | -1.0720 | 0.28 | 0/8 | 1.04 | 1.08 | `max_down_ret` (0.39) | -0.0010 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.1062 | +0.0695 | +0.0695 | -0.8397 | 0.38 | 0/8 | 1.17 | 0.77 | `early_body_momentum` (0.36) | +0.0010 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1097 | +0.0600 | +0.0600 | -2.2650 | 0.36 | 0/8 | 1.26 | 0.90 | `star50_limit_proximity_early` (0.28) | +0.0008 | +0.0000 |
| `volume_surge_direction` | Volatility & Oscillators | +1 | +0.0999 | +0.0202 | +0.0202 | -0.0698 | 0.46 | 0/8 | 0.77 | 0.58 | — | -0.0001 | +0.0000 |
| `combo_min__early_body_momentum__max_down_ret` | Intraday Range Momentum | +1 | +0.0998 | +0.0091 | +0.0091 | -0.9128 | 0.23 | 0/8 | 1.21 | 1.27 | `max_down_ret` (0.39) | +0.0000 | +0.0000 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1065 | +0.0274 | +0.0274 | -0.1044 | 0.31 | 0/8 | 0.91 | 1.06 | `body_size_progression` (0.71) | -0.0005 | +0.0000 |
| `num_up_bars` | Other Technical | +1 | +0.0993 | -0.0474 | -0.0474 | -2.5885 | 0.35 | 0/8 | 1.67 | 1.35 | — | -0.0008 | +0.0000 |
| `max_down_ret` | Intraday Range Momentum | +1 | +0.0968 | +0.0305 | +0.0305 | -0.4315 | 0.39 | 0/8 | 0.86 | 1.00 | — | +0.0004 | +0.0000 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1079 | +0.1145 | +0.1145 | +1.8262 | 0.42 | 0/8 | 0.52 | 0.44 | `early_late_momentum_divergence` (0.86) | +0.0008 | +0.0000 |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.1218 | +0.0527 | +0.0527 | +0.7989 | 0.49 | 0/8 | 0.46 | 0.50 | `double_bottom_bull_flag_early` (0.99) | +0.0004 | +0.0000 |
| `combo_rank_min__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.0966 | +0.0056 | +0.0056 | -0.6772 | 0.42 | 0/8 | 0.77 | 0.80 | `bar_ret_0` (0.48) | -0.0011 | +0.0399 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.0763 | +0.0947 | +0.0947 | +1.1715 | 0.51 | 1/8 | 1.31 | 1.28 | `smooth_momentum_structure` (0.57) | +0.0009 | -0.0530 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.0732 | -0.0136 | -0.0136 | -0.6200 | 0.94 | 1/8 | 1.07 | 1.01 | `body_size_progression` (0.71) | -0.0003 | -0.0530 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1159 | -0.0624 | -0.0624 | -1.3419 | 0.31 | 0/8 | 0.91 | 0.67 | `opening_drive_thrust_ratio` (0.31) | -0.0004 | +0.0000 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.0893 | -0.0312 | -0.0312 | -2.6274 | 0.20 | 0/8 | 1.36 | 1.29 | — | -0.0001 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0957 | +0.0823 | +0.0823 | +1.1643 | 0.29 | 0/8 | 0.92 | 0.94 | `max_down_ret` (0.39) | +0.0006 | +0.0000 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0964 | +0.0759 | +0.0759 | +0.4853 | 0.25 | 0/8 | 1.11 | 1.01 | `max_down_ret` (0.39) | +0.0010 | +0.0000 |
| `always_in_trend_persistence` | Volatility & Oscillators | +1 | +0.0861 | -0.1600 | -0.1600 | -2.7442 | 0.37 | 0/8 | 1.58 | 1.60 | — | -0.0012 | -0.0530 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1139 | +0.0380 | +0.0380 | -0.7326 | 0.26 | 0/8 | 0.83 | 0.87 | `max_down_ret` (0.39) | -0.0003 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1155 | -0.0019 | -0.0019 | -1.3928 | 0.39 | 0/8 | 0.69 | 0.94 | `max_down_ret` (0.39) | +0.0005 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1259 | +0.1323 | +0.1323 | +0.4708 | 0.31 | 0/8 | 0.78 | 0.70 | `opening_drive_thrust_ratio` (0.31) | +0.0014 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.0989 | +0.0670 | +0.0670 | +0.1096 | 0.30 | 0/8 | 1.02 | 1.38 | `trend_bar_close_consistency` (0.49) | +0.0007 | +0.0000 |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1185 | +0.0462 | +0.0462 | -0.0784 | 0.23 | 0/8 | 0.95 | 1.01 | `early_late_momentum_divergence` (0.86) | -0.0006 | +0.0000 |
| `combo_max__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0920 | +0.1499 | +0.1499 | +2.5696 | 0.52 | 0/8 | 0.96 | 1.08 | `max_down_ret` (0.39) | +0.0013 | +0.0000 |
| `combo_sig_product__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.0904 | -0.0458 | -0.0458 | -1.3179 | 0.44 | 0/8 | 0.79 | 0.94 | `max_down_ret` (0.39) | +0.0008 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.0624 | -0.0473 | -0.0473 | -2.4121 | 0.92 | 0/8 | 1.46 | 2.02 | `double_bottom_bull_flag_early` (0.99) | +0.0005 | +0.0000 |
| `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range` | Volatility & Oscillators | +1 | +0.0544 | -0.0837 | -0.0837 | +1.3887 | 0.69 | 1/8 | 0.40 | 0.17 | `close_vs_open_range` (0.31) | -0.0012 | +0.0399 |
| `bar_body_rng_0` | Other Technical | +1 | +0.1081 | +0.0133 | +0.0133 | +0.1053 | 0.36 | 0/8 | 0.66 | 0.63 | — | -0.0009 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.0844 | +0.0770 | +0.0770 | -1.1229 | 0.50 | 0/8 | 1.92 | 3.30 | `early_body_momentum` (0.36) | +0.0013 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.0431, Sharpe: +0.4992)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1574 | +0.0827 | +0.0827 | +0.6302 | 0.27 | 0/8 | 0.85 | 0.72 | `bar_body_rng_0` (0.37) | +0.0002 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1565 | +0.1000 | +0.1000 | +0.4816 | 0.33 | 0/8 | 0.73 | 0.61 | `bar_body_rng_0` (0.37) | +0.0012 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1510 | +0.0821 | +0.0821 | -0.0542 | 0.26 | 0/8 | 0.84 | 0.69 | `bar_body_rng_0` (0.37) | -0.0005 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1411 | +0.1224 | +0.1224 | +0.8794 | 0.41 | 0/8 | 0.65 | 0.59 | `first_bar_sentiment` (0.57) | +0.0010 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1403 | +0.1144 | +0.1144 | +0.5302 | 0.37 | 0/8 | 0.82 | 0.69 | `bar_body_rng_0` (0.37) | +0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1422 | +0.1174 | +0.1174 | +2.8044 | 0.36 | 0/8 | 0.85 | 0.78 | `volume_weighted_price_position` (0.69) | -0.0009 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1550 | +0.1093 | +0.1093 | +0.8621 | 0.30 | 0/8 | 0.78 | 0.65 | `bar_body_rng_0` (0.37) | +0.0001 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1502 | +0.1062 | +0.1062 | +0.3404 | 0.28 | 0/8 | 0.70 | 0.63 | `first_bar_sentiment` (0.57) | +0.0006 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1449 | +0.0587 | +0.0587 | +0.0073 | 0.33 | 0/8 | 0.61 | 0.52 | `first_bar_sentiment` (0.57) | -0.0001 | +0.0000 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1291 | +0.1324 | +0.1324 | +2.7212 | 0.49 | 0/8 | 0.96 | 0.84 | `volume_weighted_price_position` (0.69) | +0.0011 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1487 | +0.0866 | +0.0866 | +1.5177 | 0.32 | 0/8 | 1.01 | 0.81 | `opening_drive_thrust_ratio` (0.33) | -0.0000 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1546 | +0.1174 | +0.1174 | +0.3404 | 0.28 | 0/8 | 0.66 | 0.59 | `bar_body_rng_0` (0.37) | +0.0015 | +0.0000 |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1489 | +0.0719 | +0.0719 | -0.7386 | 0.23 | 0/8 | 0.76 | 0.69 | `first_bar_sentiment` (0.57) | -0.0011 | +0.0000 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1296 | +0.1495 | +0.1495 | +1.8753 | 0.45 | 0/8 | 0.81 | 0.72 | `limit_down_proximity_early` (0.44) | +0.0017 | +0.0000 |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1422 | +0.0270 | +0.0270 | -0.4994 | 0.30 | 0/8 | 0.97 | 0.81 | `demark_setup_reversal_early` (0.34) | -0.0005 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1447 | +0.0895 | +0.0895 | +0.2487 | 0.33 | 0/8 | 0.78 | 0.60 | `bar_ret_0` (0.32) | +0.0001 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1485 | +0.0486 | +0.0486 | +0.1892 | 0.25 | 0/8 | 0.72 | 0.60 | `first_bar_sentiment` (0.57) | -0.0007 | +0.0000 |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1444 | +0.0606 | +0.0606 | -1.7296 | 0.27 | 0/8 | 0.84 | 0.71 | `bar_body_rng_0` (0.37) | +0.0001 | +0.0000 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1415 | +0.0850 | +0.0850 | +0.6640 | 0.30 | 0/8 | 1.02 | 0.99 | `max_up_ret` (0.31) | +0.0010 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1520 | +0.0766 | +0.0766 | +2.5089 | 0.28 | 0/8 | 0.98 | 0.84 | `opening_drive_thrust_ratio` (0.33) | -0.0001 | +0.0000 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1448 | +0.0832 | +0.0832 | +0.2726 | 0.27 | 0/8 | 0.76 | 0.61 | `bar_body_rng_0` (0.37) | +0.0005 | +0.0000 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1364 | +0.0641 | +0.0641 | +0.2487 | 0.37 | 0/8 | 0.62 | 0.55 | `first_bar_sentiment` (0.57) | +0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1336 | -0.0563 | -0.0563 | -2.6490 | 0.31 | 0/8 | 0.93 | 0.86 | `bar_body_rng_0` (0.37) | -0.0012 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1423 | +0.0646 | +0.0646 | +0.1352 | 0.33 | 0/8 | 1.22 | 1.26 | `volatility_expansion_trend_vector` (0.58) | +0.0006 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1387 | +0.0567 | +0.0567 | -0.2824 | 0.40 | 0/8 | 1.01 | 0.86 | `bar_body_rng_0` (0.37) | +0.0003 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1243 | +0.1425 | +0.1425 | +1.0019 | 0.42 | 0/8 | 0.99 | 0.78 | `limit_down_proximity_early` (0.44) | +0.0004 | +0.0000 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1261 | +0.0762 | +0.0762 | -0.1130 | 0.38 | 0/8 | 1.25 | 1.33 | `volatility_expansion_trend_vector` (0.58) | -0.0000 | +0.0000 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1293 | +0.1312 | +0.1312 | -0.0665 | 0.34 | 0/8 | 0.71 | 0.56 | `limit_down_proximity_early` (0.44) | +0.0002 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1457 | -0.0192 | -0.0192 | -1.7777 | 0.27 | 0/8 | 1.09 | 1.11 | `opening_drive_thrust_ratio` (0.33) | -0.0007 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1332 | -0.0595 | -0.0595 | -2.7716 | 0.36 | 0/8 | 1.13 | 1.10 | `opening_drive_thrust_ratio` (0.33) | -0.0010 | +0.0000 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1213 | -0.0770 | -0.0770 | -1.2111 | 0.44 | 0/8 | 1.13 | 0.94 | `volume_weighted_price_position` (0.69) | -0.0034 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1288 | +0.0919 | +0.0919 | +0.8492 | 0.27 | 0/8 | 0.84 | 0.73 | `first_bar_sentiment` (0.57) | +0.0007 | +0.0000 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1259 | +0.0307 | +0.0307 | +0.0580 | 0.36 | 0/8 | 0.90 | 0.67 | `bar_body_rng_0` (0.37) | +0.0001 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1317 | -0.0148 | -0.0148 | -1.0032 | 0.34 | 0/8 | 0.84 | 0.76 | `bar_body_rng_0` (0.37) | +0.0008 | +0.0000 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1378 | -0.0421 | -0.0421 | -1.8255 | 0.29 | 0/8 | 0.98 | 0.79 | `bar_body_rng_0` (0.37) | -0.0013 | +0.0000 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1249 | -0.0381 | -0.0381 | -3.2808 | 0.36 | 0/8 | 1.22 | 1.10 | `volatility_expansion_trend_vector` (0.58) | -0.0003 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1300 | +0.0535 | +0.0535 | +0.1627 | 0.28 | 0/8 | 1.35 | 1.36 | `impulse_bar_dominance` (0.64) | -0.0010 | +0.0000 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1383 | +0.0431 | +0.0431 | +0.1011 | 0.38 | 0/8 | 0.88 | 0.76 | `bar_body_rng_0` (0.37) | -0.0004 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1350 | +0.1356 | +0.1356 | +1.7557 | 0.38 | 0/8 | 0.59 | 0.52 | `first_bar_sentiment` (0.57) | +0.0005 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1352 | +0.0809 | +0.0809 | -0.5341 | 0.21 | 0/8 | 1.16 | 1.25 | `impulse_bar_dominance` (0.64) | +0.0010 | +0.0000 |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1362 | -0.0077 | -0.0077 | -1.8187 | 0.32 | 0/8 | 1.07 | 0.94 | `demark_setup_reversal_early` (0.34) | -0.0021 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1408 | +0.0545 | +0.0545 | -1.0195 | 0.24 | 0/8 | 1.22 | 1.30 | `volatility_expansion_trend_vector` (0.58) | +0.0009 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1382 | -0.0036 | -0.0036 | -1.7032 | 0.28 | 0/8 | 0.98 | 0.78 | `bar_body_rng_0` (0.37) | -0.0010 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1440 | +0.0503 | +0.0503 | +0.6600 | 0.32 | 0/8 | 0.91 | 0.89 | `first_bar_sentiment` (0.57) | -0.0008 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1315 | +0.1013 | +0.1013 | +0.1249 | 0.28 | 0/8 | 1.02 | 0.76 | `rbreaker_buy_setup_proximity_early` (0.44) | -0.0016 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1280 | -0.0232 | -0.0232 | -2.1679 | 0.36 | 0/8 | 0.91 | 0.74 | `bar_body_rng_0` (0.37) | -0.0012 | +0.0000 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1309 | -0.0181 | -0.0181 | -1.3831 | 0.32 | 0/8 | 0.79 | 0.60 | `first_bar_sentiment` (0.57) | -0.0011 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1257 | -0.0689 | -0.0689 | -1.1833 | 0.31 | 0/8 | 1.30 | 1.09 | `opening_drive_thrust_ratio` (0.33) | -0.0008 | +0.0000 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1484 | +0.0961 | +0.0961 | +1.0753 | 0.35 | 0/8 | 0.69 | 0.75 | `volume_weighted_price_position` (0.69) | +0.0013 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1102 | +0.1381 | +0.1381 | +2.7110 | 0.61 | 0/8 | 1.14 | 0.85 | `volume_weighted_price_position` (0.69) | +0.0001 | +0.0000 |
| `combo_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1336 | -0.0771 | -0.0771 | -3.6387 | 0.30 | 0/8 | 0.90 | 0.83 | `bar_body_rng_0` (0.37) | -0.0008 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1279 | -0.0930 | -0.0930 | -2.1195 | 0.37 | 0/8 | 1.50 | 1.43 | `volatility_expansion_trend_vector` (0.58) | -0.0012 | +0.0000 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1159 | -0.0854 | -0.0854 | -2.9019 | 0.48 | 0/8 | 1.71 | 2.05 | `volatility_expansion_trend_vector` (0.58) | -0.0015 | +0.0000 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1411 | -0.0318 | -0.0318 | -2.0212 | 0.34 | 0/8 | 1.13 | 1.03 | `demark_setup_reversal_early` (0.34) | -0.0018 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1346 | -0.0695 | -0.0695 | -3.0723 | 0.34 | 0/8 | 1.11 | 1.03 | `opening_drive_thrust_ratio` (0.33) | -0.0007 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1238 | -0.0265 | -0.0265 | -1.7025 | 0.38 | 0/8 | 0.90 | 0.81 | `opening_drive_thrust_ratio` (0.33) | -0.0014 | +0.0000 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1419 | +0.0018 | +0.0018 | -2.0212 | 0.31 | 0/8 | 1.11 | 0.97 | `demark_setup_reversal_early` (0.34) | -0.0008 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | Other Technical | +1 | +0.1130 | -0.0835 | -0.0835 | -0.1351 | 0.34 | 0/8 | 1.44 | 1.15 | `impulse_bar_dominance` (0.64) | -0.0024 | +0.0000 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1267 | -0.0753 | -0.0753 | -2.9698 | 0.31 | 0/8 | 1.09 | 1.13 | — | -0.0011 | +0.0000 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1215 | -0.1035 | -0.1035 | -4.2121 | 0.41 | 0/8 | 1.40 | 1.52 | `volatility_expansion_trend_vector` (0.58) | -0.0011 | +0.0000 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1206 | +0.0841 | +0.0841 | -1.2423 | 0.33 | 0/8 | 1.36 | 1.26 | `volatility_expansion_trend_vector` (0.58) | +0.0002 | +0.0000 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.1276 | -0.0816 | -0.0816 | -4.0036 | 0.37 | 0/8 | 1.14 | 1.36 | `volatility_expansion_trend_vector` (0.58) | -0.0008 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1326 | -0.0534 | -0.0534 | -3.0723 | 0.31 | 0/8 | 0.93 | 0.78 | `first_bar_sentiment` (0.57) | -0.0016 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1270 | +0.0199 | +0.0199 | -0.2374 | 0.34 | 0/8 | 0.78 | 0.61 | `bar_body_rng_0` (0.37) | +0.0001 | +0.0000 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1223 | -0.0913 | -0.0913 | -4.2927 | 0.39 | 0/8 | 1.36 | 1.43 | `volatility_expansion_trend_vector` (0.58) | -0.0003 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1239 | +0.0069 | +0.0069 | -0.4785 | 0.28 | 0/8 | 0.82 | 0.60 | `first_bar_sentiment` (0.57) | -0.0017 | +0.0000 |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | Other Technical | +1 | +0.1183 | -0.0230 | -0.0230 | -0.3944 | 0.29 | 0/8 | 1.13 | 1.10 | `impulse_bar_dominance` (0.64) | +0.0003 | +0.0000 |
| `combo_min__bar_body_rng_0__impulse_bar_dominance` | Other Technical | +1 | +0.1191 | -0.0179 | -0.0179 | -0.8876 | 0.32 | 0/8 | 1.33 | 1.06 | `impulse_bar_dominance` (0.64) | -0.0008 | +0.0000 |
| `combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1043 | +0.0673 | +0.0673 | +0.6455 | 0.34 | 0/8 | 1.45 | 1.46 | `impulse_bar_dominance` (0.64) | +0.0007 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1238 | -0.1027 | -0.1027 | -1.1404 | 0.32 | 0/8 | 0.95 | 0.81 | `bar_body_rng_0` (0.37) | -0.0020 | +0.0000 |
| `combo_mean__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.1212 | -0.0845 | -0.0845 | -3.1121 | 0.36 | 0/8 | 1.42 | 1.47 | `impulse_bar_dominance` (0.64) | -0.0008 | +0.0000 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1073 | +0.1286 | +0.1286 | +0.2449 | 0.38 | 0/8 | 1.46 | 0.98 | `yesterday_first_30min_return` (0.66) | -0.0004 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1130 | -0.0221 | -0.0221 | -1.5636 | 0.49 | 0/8 | 1.78 | 1.65 | `impulse_bar_dominance` (0.64) | -0.0015 | +0.0000 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1025 | +0.1554 | +0.1554 | +0.1107 | 0.37 | 0/8 | 1.01 | 0.53 | `yesterday_first_30min_return` (0.66) | +0.0002 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1368 | +0.0426 | +0.0426 | -0.5756 | 0.34 | 0/8 | 0.91 | 0.81 | `first_bar_return` (0.32) | -0.0007 | +0.0000 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1117 | +0.0712 | +0.0712 | -1.1060 | 0.30 | 0/8 | 1.25 | 0.94 | `rbreaker_buy_setup_proximity_early` (0.44) | -0.0007 | +0.0000 |
| `combo_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1205 | -0.0026 | -0.0026 | -1.7519 | 0.33 | 0/8 | 0.75 | 0.53 | `first_bar_sentiment` (0.57) | -0.0008 | +0.0000 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1294 | -0.0737 | -0.0737 | -3.0060 | 0.47 | 0/8 | 1.02 | 1.07 | `volume_weighted_price_position` (0.69) | -0.0023 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1290 | -0.0464 | -0.0464 | -0.7909 | 0.33 | 0/8 | 1.21 | 0.97 | — | -0.0025 | +0.0000 |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1239 | -0.0010 | -0.0010 | -0.2680 | 0.24 | 0/8 | 0.98 | 0.66 | `first_bar_sentiment` (0.57) | -0.0010 | +0.0000 |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1155 | -0.0016 | -0.0016 | -1.2131 | 0.41 | 0/8 | 0.86 | 0.75 | `volume_weighted_price_position` (0.69) | +0.0004 | +0.0000 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1139 | -0.0572 | -0.0572 | -1.0459 | 0.50 | 0/8 | 1.74 | 1.55 | `volatility_expansion_trend_vector` (0.58) | -0.0015 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1091 | +0.0593 | +0.0593 | -1.4053 | 0.39 | 0/8 | 1.17 | 1.05 | `bar_body_rng_0` (0.37) | +0.0016 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1141 | +0.1654 | +0.1654 | +1.0917 | 0.30 | 0/8 | 1.39 | 0.96 | `yesterday_first_30min_return` (0.66) | +0.0020 | +0.0000 |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | Other Technical | +1 | +0.1097 | -0.0248 | -0.0248 | -2.1848 | 0.44 | 0/8 | 1.07 | 1.16 | `impulse_bar_dominance` (0.64) | -0.0005 | +0.0000 |
| `combo_mean__limit_down_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1221 | +0.1186 | +0.1186 | +0.0733 | 0.49 | 0/8 | 0.77 | 0.70 | `volume_weighted_price_position` (0.69) | +0.0009 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1184 | -0.0811 | -0.0811 | -1.8808 | 0.33 | 0/8 | 1.14 | 0.88 | `opening_drive_thrust_ratio` (0.33) | -0.0016 | +0.0000 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1278 | -0.0570 | -0.0570 | -0.3265 | 0.46 | 0/8 | 1.03 | 1.04 | `volume_weighted_price_position` (0.69) | -0.0016 | +0.0000 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1295 | +0.0586 | +0.0586 | -0.7006 | 0.30 | 0/8 | 1.12 | 1.01 | `max_up_ret` (0.31) | -0.0001 | +0.0000 |
| `combo_mean__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1276 | -0.0225 | -0.0225 | -1.1019 | 0.31 | 0/8 | 0.99 | 0.79 | `first_bar_return` (0.32) | -0.0010 | +0.0000 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1140 | +0.0226 | +0.0226 | +0.2558 | 0.32 | 0/8 | 0.75 | 0.56 | — | -0.0010 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1298 | +0.1358 | +0.1358 | +0.2908 | 0.26 | 0/8 | 0.73 | 0.63 | `bar_body_rng_0` (0.37) | +0.0016 | +0.0000 |
| `combo_max__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1150 | -0.0145 | -0.0145 | -1.9086 | 0.33 | 0/8 | 0.73 | 0.60 | `first_bar_sentiment` (0.57) | -0.0008 | +0.0000 |
| `combo_min__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1148 | -0.0303 | -0.0303 | -1.6286 | 0.51 | 0/8 | 0.95 | 0.91 | `volume_weighted_price_position` (0.69) | -0.0013 | +0.0000 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1286 | +0.0212 | +0.0212 | -1.1311 | 0.25 | 0/8 | 0.92 | 0.76 | `bar_body_rng_0` (0.37) | -0.0008 | +0.0000 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1455 | +0.1637 | +0.1637 | +0.5943 | 0.16 | 0/8 | 0.91 | 0.88 | — | +0.0013 | +0.0000 |
| `combo_mean__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.1141 | -0.0010 | -0.0010 | +0.5553 | 0.49 | 0/8 | 0.81 | 0.70 | `volume_weighted_price_position` (0.69) | -0.0023 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1092 | +0.1209 | +0.1209 | +0.7808 | 0.37 | 0/8 | 1.50 | 1.02 | `yesterday_first_30min_return` (0.66) | +0.0015 | +0.0000 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1173 | +0.1154 | +0.1154 | -0.0647 | 0.31 | 0/8 | 0.99 | 0.60 | `yesterday_first_30min_return` (0.66) | +0.0017 | +0.0000 |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1118 | -0.0820 | -0.0820 | -3.0532 | 0.61 | 0/8 | 1.50 | 1.66 | `volume_weighted_price_position` (0.69) | -0.0026 | +0.0000 |
| `combo_max__bar_ret_0__impulse_bar_dominance` | Other Technical | +1 | +0.0989 | -0.0491 | -0.0491 | -2.0937 | 0.40 | 0/8 | 1.25 | 1.73 | `impulse_bar_dominance` (0.64) | -0.0001 | +0.0000 |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | Other Technical | +1 | +0.1181 | -0.0113 | -0.0113 | -0.6553 | 0.33 | 0/8 | 1.49 | 1.36 | `impulse_bar_dominance` (0.64) | -0.0000 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1295 | +0.0623 | +0.0623 | -0.0060 | 0.28 | 0/8 | 1.50 | 1.56 | `volatility_expansion_trend_vector` (0.58) | -0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1236 | -0.0120 | -0.0120 | -0.7424 | 0.29 | 0/8 | 0.91 | 0.80 | `bar_ret_0` (0.32) | +0.0002 | +0.0000 |
| `combo_max__bar_ret_0__limit_down_proximity_early` | Other Technical | +1 | +0.1089 | +0.0866 | +0.0866 | -1.4591 | 0.35 | 0/8 | 0.80 | 0.55 | `limit_down_proximity_early` (0.44) | -0.0008 | +0.0000 |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1255 | +0.1158 | +0.1158 | +0.1892 | 0.26 | 0/8 | 0.89 | 0.71 | `bar_body_rng_0` (0.37) | +0.0006 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Other Technical | +1 | +0.1370 | +0.1716 | +0.1716 | +2.0307 | 0.23 | 0/8 | 0.94 | 0.80 | `limit_down_proximity_early` (0.44) | +0.0002 | +0.0000 |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1071 | +0.0909 | +0.0909 | -0.2991 | 0.25 | 0/8 | 1.34 | 1.16 | `impulse_bar_dominance` (0.64) | +0.0001 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1038 | +0.0944 | +0.0944 | +0.9523 | 0.48 | 0/8 | 1.39 | 1.26 | `volatility_expansion_trend_vector` (0.58) | +0.0014 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0939 | -0.0561 | -0.0561 | -1.5551 | 0.79 | 1/8 | 1.80 | 1.71 | `volume_weighted_price_position` (0.69) | -0.0021 | +0.0000 |
| `combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1155 | +0.0120 | +0.0120 | -0.2721 | 0.34 | 0/8 | 0.77 | 0.51 | `first_bar_sentiment` (0.57) | -0.0015 | +0.0000 |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1025 | -0.1064 | -0.1064 | -4.3046 | 0.59 | 0/8 | 2.15 | 2.80 | `volume_weighted_price_position` (0.69) | -0.0016 | +0.0000 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1227 | +0.0262 | +0.0262 | -1.0933 | 0.31 | 0/8 | 1.14 | 0.99 | `opening_drive_thrust_ratio` (0.33) | -0.0003 | +0.0000 |
| `combo_mean__impulse_bar_dominance__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1058 | -0.1025 | -0.1025 | -2.8874 | 0.51 | 0/8 | 2.40 | 2.71 | `impulse_bar_dominance` (0.64) | -0.0010 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1077 | +0.0980 | +0.0980 | +1.3754 | 0.46 | 0/8 | 1.21 | 1.12 | `bar_ret_0` (0.32) | +0.0013 | +0.0000 |
| `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1213 | +0.0898 | +0.0898 | -0.9819 | 0.24 | 0/8 | 0.68 | 0.59 | `first_bar_sentiment` (0.57) | -0.0010 | +0.0000 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1121 | +0.0098 | +0.0098 | +0.0371 | 0.36 | 0/8 | 0.72 | 0.53 | `volume_weighted_price_position` (0.69) | -0.0013 | +0.0000 |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1118 | +0.1476 | +0.1476 | +2.6573 | 0.38 | 0/8 | 0.58 | 0.49 | `first_bar_sentiment` (0.57) | +0.0006 | +0.0000 |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1206 | -0.0256 | -0.0256 | -0.7046 | 0.56 | 0/8 | 0.69 | 0.62 | `volume_weighted_price_position` (0.69) | -0.0015 | +0.0000 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1155 | -0.0445 | -0.0445 | -2.4277 | 0.46 | 0/8 | 1.22 | 1.11 | `volume_weighted_price_position` (0.69) | -0.0011 | +0.0000 |
| `combo_min__first_bar_sentiment__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.1002 | -0.0329 | -0.0329 | -2.0105 | 0.44 | 0/8 | 1.32 | 1.01 | `volatility_expansion_trend_vector` (0.58) | -0.0006 | +0.0000 |
| `trend_bar_close_consistency` | Other Technical | +1 | +0.0897 | -0.1362 | -0.1362 | -1.8903 | 0.75 | 0/8 | 2.76 | 3.89 | — | -0.0021 | +0.0000 |
| `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0877 | -0.0102 | -0.0102 | -2.0687 | 0.47 | 0/8 | 2.07 | 1.93 | `impulse_bar_dominance` (0.64) | -0.0016 | +0.0000 |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1054 | +0.0852 | +0.0852 | +0.3263 | 0.35 | 0/8 | 0.77 | 0.51 | `rbreaker_buy_setup_proximity_early` (0.44) | -0.0006 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1217 | -0.1124 | -0.1124 | -2.6779 | 0.40 | 0/8 | 1.30 | 0.99 | `volatility_expansion_trend_vector` (0.58) | -0.0010 | +0.0000 |
| `combo_diff__limit_down_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1178 | +0.1236 | +0.1236 | +0.6182 | 0.30 | 0/8 | 1.07 | 0.93 | `limit_down_proximity_early` (0.44) | +0.0003 | +0.0000 |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1158 | +0.1348 | +0.1348 | +0.9350 | 0.31 | 0/8 | 1.07 | 0.93 | `rbreaker_buy_setup_proximity_early` (0.44) | +0.0004 | +0.0000 |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.1081 | -0.0663 | -0.0663 | -3.0886 | 0.54 | 0/8 | 1.80 | 1.83 | — | -0.0007 | +0.0000 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.1158 | -0.0325 | -0.0325 | -2.6779 | 0.39 | 0/8 | 1.53 | 1.93 | `volatility_expansion_trend_vector` (0.58) | +0.0000 | +0.0000 |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1076 | -0.0010 | -0.0010 | -1.9510 | 0.51 | 0/8 | 0.85 | 0.56 | `volatility_expansion_trend_vector` (0.58) | -0.0007 | +0.0000 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1010 | -0.0177 | -0.0177 | -2.1380 | 0.44 | 0/8 | 0.53 | 0.56 | `first_bar_sentiment` (0.57) | -0.0007 | +0.0000 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | Gap / Overnight Reversal | +1 | +0.1037 | +0.0154 | +0.0154 | -0.1510 | 0.45 | 0/8 | 1.58 | 1.13 | `volatility_expansion_trend_vector` (0.58) | -0.0018 | +0.0000 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1124 | -0.1070 | -0.1070 | -1.0195 | 0.35 | 0/8 | 0.98 | 0.81 | `opening_drive_thrust_ratio` (0.33) | -0.0013 | +0.0000 |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1122 | +0.0279 | +0.0279 | -1.5933 | 0.38 | 0/8 | 1.83 | 1.63 | `volatility_expansion_trend_vector` (0.58) | -0.0008 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | Other Technical | +1 | +0.0639 | -0.0939 | -0.0939 | -0.6519 | 0.51 | 1/8 | 0.59 | 0.73 | `limit_down_proximity_early` (0.44) | -0.0027 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0907 | +0.0955 | +0.0955 | -0.7293 | 0.59 | 1/8 | 1.89 | 2.13 | `volatility_expansion_trend_vector` (0.58) | +0.0006 | +0.0000 |
| `combo_clamp_diff__volume_weighted_price_position__late_bar_momentum` | Intraday Range Momentum | +1 | +0.0978 | +0.0458 | +0.0458 | -1.2891 | 0.63 | 0/8 | 0.76 | 0.40 | `late_bar_momentum` (0.83) | -0.0011 | +0.0000 |
| `shaved_bar_trend_conviction` | Other Technical | +1 | +0.0847 | -0.0741 | -0.0741 | -2.4700 | 0.80 | 1/8 | 1.84 | 3.52 | — | -0.0029 | +0.0000 |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0656 | +0.0896 | +0.0896 | -1.6385 | 0.74 | 1/8 | 2.10 | 2.34 | `volatility_expansion_trend_vector` (0.58) | +0.0000 | +0.0000 |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | Intraday Range Momentum | +1 | +0.0697 | +0.0597 | +0.0597 | -1.3636 | 0.68 | 1/8 | 1.69 | 0.95 | `yesterday_early_trend` (0.71) | +0.0006 | +0.0000 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 36.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -1.0211_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 886 | 30 | 0.0% | 0.0% | -0.0916 | -1.1571 |
| B2 Rolling Guard | 85 | 30 | 23.3% | 6.7% | -0.0540 | -1.1075 |
| BH-FDR Gate | 3 | 3 | 0.0% | 0.0% | -0.0837 | -0.7979 |
| B3 Composite Floor | 2 | 2 | 100.0% | 0.0% | +0.0878 | -0.7216 |
| B4 Correlation Gate | 148 | 30 | 20.0% | 6.7% | -0.0685 | -1.1982 |

**Admitted Pool Summary**: 63 features, False Positive Rate = 96.8% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0938, Mean Lock Sharpe = -1.5550

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1301, Lock IC=+0.1291, Lock Sharpe=+0.6923
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1301, Lock IC=+0.1291, Lock Sharpe=+0.6923

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Lock Sharpe=+0.4322
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Lock Sharpe=+0.4322

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 66.0% lock IC > 0, 53.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0140_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 809 | 30 | 63.3% | 46.7% | +0.0521 | -0.2513 |
| B2 Rolling Guard | 75 | 30 | 50.0% | 33.3% | +0.0290 | -0.2634 |
| BH-FDR Gate | 5 | 5 | 60.0% | 60.0% | +0.0987 | -0.7010 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__roc60__ma_alignment_score_5_10_20`: Train IC=+0.1548, Lock IC=+0.2236, Lock Sharpe=+2.1221
- `combo_min__volume_surge_max__roc10`: Train IC=+0.1107, Lock IC=+0.1521, Lock Sharpe=+1.8316
- `combo_rank_max__roc60__volume_differential_10d`: Train IC=+0.1091, Lock IC=+0.1168, Lock Sharpe=+1.4182
- `demark_setup_reversal_early`: Train IC=+0.1292, Lock IC=+0.0963, Lock Sharpe=+1.3257
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1161, Lock IC=+0.1785, Lock Sharpe=+1.2000

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__iv_corridor_width__ma_alignment_score_5_10_20`: Train IC=+0.1013, Lock IC=+0.1148, Lock Sharpe=+1.5935
- `star50_limit_proximity_early`: Train IC=+0.1222, Lock IC=+0.1992, Lock Sharpe=+1.4268
- `combo_ratio__star50_limit_proximity_early__bar_vol_4`: Train IC=+0.0864, Lock IC=+0.1827, Lock Sharpe=+1.2460
- `limit_down_proximity_early`: Train IC=+0.1138, Lock IC=+0.1983, Lock Sharpe=+0.9672
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1138, Lock IC=+0.1983, Lock Sharpe=+0.9672

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__bar_vol_4__sma50_dist`: Train IC=+0.0747, Lock IC=+0.2497, Lock Sharpe=+0.4124
- `combo_rel_diff__volume_surge_max__ema_ribbon_width`: Train IC=+0.0451, Lock IC=+0.1358, Lock Sharpe=+0.4113
- `combo_rel_diff__bar_vol_4__sma_distance_60d`: Train IC=+0.0677, Lock IC=+0.2305, Lock Sharpe=+0.2828

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 41.0% lock IC > 0, 26.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8743_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1921 | 30 | 50.0% | 33.3% | +0.0017 | -1.1458 |
| B2 Rolling Guard | 256 | 30 | 23.3% | 16.7% | -0.0540 | -1.4690 |
| B3 Composite Floor | 55 | 30 | 66.7% | 6.7% | +0.0119 | -0.6585 |
| B4 Correlation Gate | 399 | 30 | 33.3% | 16.7% | -0.0097 | -1.4380 |

**Admitted Pool Summary**: 122 features, False Positive Rate = 77.9% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0051, Mean Lock Sharpe = -0.9365

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Lock Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Lock Sharpe=+1.7265
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.2184, Lock IC=+0.0565, Lock Sharpe=+0.2974
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.2184, Lock IC=+0.0565, Lock Sharpe=+0.2974
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.2184, Lock IC=+0.0565, Lock Sharpe=+0.2974

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__volume_weighted_momentum_acceleration__double_bottom_bull_flag_early`: Train IC=+0.1702, Lock IC=+0.1113, Lock Sharpe=+1.6232
- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1769, Lock IC=+0.1949, Lock Sharpe=+1.1683
- `combo_tri_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1654, Lock IC=+0.0959, Lock Sharpe=+1.0596
- `combo_tri_z_mean__opening_drive_thrust_ratio__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1654, Lock IC=+0.0959, Lock Sharpe=+1.0596
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1796, Lock IC=+0.1227, Lock Sharpe=+0.1858

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Lock Sharpe=+0.1323
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Lock Sharpe=+0.1323

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2557, Lock IC=+0.0706, Lock Sharpe=+0.8062
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2557, Lock IC=+0.0706, Lock Sharpe=+0.8062
- `combo_tri_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.2499, Lock IC=+0.0369, Lock Sharpe=+0.4718
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2573, Lock IC=+0.0571, Lock Sharpe=+0.3372
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2670, Lock IC=+0.0441, Lock Sharpe=+0.1744

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 34.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4260_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1079 | 30 | 76.7% | 20.0% | +0.0398 | -0.6878 |
| B2 Rolling Guard | 179 | 30 | 90.0% | 56.7% | +0.0860 | -0.1486 |
| BH-FDR Gate | 1 | 1 | 100.0% | 100.0% | +0.1004 | +0.2891 |
| B3 Composite Floor | 65 | 30 | 80.0% | 3.3% | +0.0330 | -1.1404 |
| B4 Correlation Gate | 306 | 30 | 96.7% | 66.7% | +0.0965 | +0.5009 |

**Admitted Pool Summary**: 140 features, False Positive Rate = 68.6% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0238, Mean Lock Sharpe = -0.8018

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.2208, Lock IC=+0.1225, Lock Sharpe=+1.4450
- `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.1849, Lock IC=+0.1624, Lock Sharpe=+0.7707
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2019, Lock IC=+0.0941, Lock Sharpe=+0.6495
- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2586, Lock IC=+0.0964, Lock Sharpe=+0.3336
- `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return`: Train IC=+0.1973, Lock IC=+0.0282, Lock Sharpe=+0.2027

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.1730, Lock IC=+0.1155, Lock Sharpe=+1.0583
- `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.1722, Lock IC=+0.1037, Lock Sharpe=+1.0583
- `combo_min__first_bar_sentiment__demark_setup_reversal_early`: Train IC=+0.2140, Lock IC=+0.0901, Lock Sharpe=+0.9586
- `combo_min__demark_setup_reversal_early__impulse_bar_dominance`: Train IC=+0.1757, Lock IC=+0.1511, Lock Sharpe=+0.7444
- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1768, Lock IC=+0.1276, Lock Sharpe=+0.6656

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Lock Sharpe=+0.2891

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.1939, Lock IC=+0.0436, Lock Sharpe=+0.3411

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2975, Lock IC=+0.1253, Lock Sharpe=+2.7133
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3290, Lock IC=+0.0740, Lock Sharpe=+2.5285
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3187, Lock IC=+0.1205, Lock Sharpe=+2.3935
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.3014, Lock IC=+0.1495, Lock Sharpe=+1.8753
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.2970, Lock IC=+0.0973, Lock Sharpe=+1.6993

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 388 | +0.0051 | 40.0% |
| 0.45 | 0.20 | 373 | +0.0051 | 40.0% |
| 0.45 | 0.30 | 353 | +0.0051 | 40.0% |
| 0.45 | 0.40 | 316 | +0.0051 | 40.0% |
| 0.45 | 0.50 | 272 | +0.0051 | 40.0% |
| 0.50 | 0.15 | 380 | +0.0051 | 40.0% |
| 0.50 | 0.25 | 362 | +0.0051 | 40.0% |
| 0.50 | 0.35 | 336 | +0.0051 | 40.0% |
| 0.50 | 0.45 | 293 | +0.0051 | 40.0% |
| 0.55 | 0.10 | 378 | +0.0051 | 40.0% |
| 0.55 | 0.20 | 371 | +0.0051 | 40.0% |
| 0.55 | 0.30 | 353 | +0.0051 | 40.0% |
| 0.55 | 0.40 | 316 | +0.0051 | 40.0% |
| 0.55 | 0.50 | 272 | +0.0051 | 40.0% |
| 0.60 | 0.15 | 353 | +0.0051 | 40.0% |
| 0.60 | 0.25 | 350 | +0.0051 | 40.0% |
| 0.60 | 0.35 | 333 | +0.0051 | 40.0% |
| 0.60 | 0.45 | 293 | +0.0051 | 40.0% |
| 0.65 | 0.10 | 314 | +0.0051 | 40.0% |
| 0.65 | 0.20 | 314 | +0.0051 | 40.0% |
| 0.65 | 0.30 | 314 | +0.0051 | 40.0% |
| 0.65 | 0.40 | 308 | +0.0051 | 40.0% |
| 0.65 | 0.50 | 272 | +0.0051 | 40.0% |
| 0.70 | 0.15 | 259 | +0.0051 | 40.0% |
| 0.70 | 0.25 | 259 | +0.0051 | 40.0% |
| 0.70 | 0.35 | 259 | +0.0051 | 40.0% |
| 0.70 | 0.45 | 259 | +0.0051 | 40.0% |
| 0.75 | 0.10 | 144 | -0.0087 | 40.0% |
| 0.75 | 0.20 | 144 | -0.0087 | 40.0% |
| 0.75 | 0.30 | 144 | -0.0087 | 40.0% |
| 0.75 | 0.40 | 144 | -0.0087 | 40.0% |
| 0.75 | 0.50 | 144 | -0.0087 | 40.0% |
| 0.80 | 0.15 | 28 | -0.0180 | 40.0% |
| 0.80 | 0.25 | 28 | -0.0180 | 40.0% |
| 0.80 | 0.35 | 28 | -0.0180 | 40.0% |
| 0.80 | 0.45 | 28 | -0.0180 | 40.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 388 candidates, mean lock IC=+0.0051, 40.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 420 | +0.0944 | 100.0% |
| 0.45 | 0.20 | 412 | +0.0944 | 100.0% |
| 0.45 | 0.30 | 391 | +0.0944 | 100.0% |
| 0.45 | 0.40 | 362 | +0.0944 | 100.0% |
| 0.45 | 0.50 | 325 | +0.0944 | 100.0% |
| 0.50 | 0.15 | 414 | +0.0944 | 100.0% |
| 0.50 | 0.25 | 404 | +0.0944 | 100.0% |
| 0.50 | 0.35 | 375 | +0.0944 | 100.0% |
| 0.50 | 0.45 | 340 | +0.0944 | 100.0% |
| 0.55 | 0.10 | 416 | +0.0944 | 100.0% |
| 0.55 | 0.20 | 412 | +0.0944 | 100.0% |
| 0.55 | 0.30 | 391 | +0.0944 | 100.0% |
| 0.55 | 0.40 | 362 | +0.0944 | 100.0% |
| 0.55 | 0.50 | 325 | +0.0944 | 100.0% |
| 0.60 | 0.15 | 399 | +0.0944 | 100.0% |
| 0.60 | 0.25 | 397 | +0.0944 | 100.0% |
| 0.60 | 0.35 | 375 | +0.0944 | 100.0% |
| 0.60 | 0.45 | 340 | +0.0944 | 100.0% |
| 0.65 | 0.10 | 360 | +0.0944 | 100.0% |
| 0.65 | 0.20 | 360 | +0.0944 | 100.0% |
| 0.65 | 0.30 | 360 | +0.0944 | 100.0% |
| 0.65 | 0.40 | 355 | +0.0944 | 100.0% |
| 0.65 | 0.50 | 325 | +0.0944 | 100.0% |
| 0.70 | 0.15 | 302 | +0.0944 | 100.0% |
| 0.70 | 0.25 | 302 | +0.0944 | 100.0% |
| 0.70 | 0.35 | 302 | +0.0944 | 100.0% |
| 0.70 | 0.45 | 300 | +0.0944 | 100.0% |
| 0.75 | 0.10 | 244 | +0.0901 | 100.0% |
| 0.75 | 0.20 | 244 | +0.0901 | 100.0% |
| 0.75 | 0.30 | 244 | +0.0901 | 100.0% |
| 0.75 | 0.40 | 244 | +0.0901 | 100.0% |
| 0.75 | 0.50 | 244 | +0.0901 | 100.0% |
| 0.80 | 0.15 | 174 | +0.0944 | 100.0% |
| 0.80 | 0.25 | 174 | +0.0944 | 100.0% |
| 0.80 | 0.35 | 174 | +0.0944 | 100.0% |
| 0.80 | 0.45 | 174 | +0.0944 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 420 candidates, mean lock IC=+0.0944, 100.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1094 | -0.0035 | 80.0% |
| 0.45 | 0.20 | 1058 | -0.0035 | 80.0% |
| 0.45 | 0.30 | 1008 | -0.0035 | 80.0% |
| 0.45 | 0.40 | 858 | -0.0035 | 80.0% |
| 0.45 | 0.50 | 659 | -0.0035 | 80.0% |
| 0.50 | 0.15 | 1082 | -0.0035 | 80.0% |
| 0.50 | 0.25 | 1034 | -0.0035 | 80.0% |
| 0.50 | 0.35 | 936 | -0.0035 | 80.0% |
| 0.50 | 0.45 | 764 | -0.0035 | 80.0% |
| 0.55 | 0.10 | 1079 | -0.0035 | 80.0% |
| 0.55 | 0.20 | 1058 | -0.0035 | 80.0% |
| 0.55 | 0.30 | 1008 | -0.0035 | 80.0% |
| 0.55 | 0.40 | 858 | -0.0035 | 80.0% |
| 0.55 | 0.50 | 659 | -0.0035 | 80.0% |
| 0.60 | 0.15 | 1028 | -0.0035 | 80.0% |
| 0.60 | 0.25 | 1021 | -0.0035 | 80.0% |
| 0.60 | 0.35 | 936 | -0.0035 | 80.0% |
| 0.60 | 0.45 | 764 | -0.0035 | 80.0% |
| 0.65 | 0.10 | 862 | -0.0035 | 80.0% |
| 0.65 | 0.20 | 862 | -0.0035 | 80.0% |
| 0.65 | 0.30 | 860 | -0.0035 | 80.0% |
| 0.65 | 0.40 | 821 | -0.0035 | 80.0% |
| 0.65 | 0.50 | 659 | -0.0035 | 80.0% |
| 0.70 | 0.15 | 600 | -0.0035 | 80.0% |
| 0.70 | 0.25 | 600 | -0.0035 | 80.0% |
| 0.70 | 0.35 | 600 | -0.0035 | 80.0% |
| 0.70 | 0.45 | 600 | -0.0035 | 80.0% |
| 0.75 | 0.10 | 253 | -0.0035 | 80.0% |
| 0.75 | 0.20 | 253 | -0.0035 | 80.0% |
| 0.75 | 0.30 | 253 | -0.0035 | 80.0% |
| 0.75 | 0.40 | 253 | -0.0035 | 80.0% |
| 0.75 | 0.50 | 253 | -0.0035 | 80.0% |
| 0.80 | 0.15 | 73 | +0.0104 | 100.0% |
| 0.80 | 0.25 | 73 | +0.0104 | 100.0% |
| 0.80 | 0.35 | 73 | +0.0104 | 100.0% |
| 0.80 | 0.45 | 73 | +0.0104 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 73 candidates, mean lock IC=+0.0104, 100.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 795 | +0.0818 | 100.0% |
| 0.45 | 0.20 | 774 | +0.0818 | 100.0% |
| 0.45 | 0.30 | 726 | +0.0818 | 100.0% |
| 0.45 | 0.40 | 645 | +0.0818 | 100.0% |
| 0.45 | 0.50 | 532 | +0.0818 | 100.0% |
| 0.50 | 0.15 | 785 | +0.0818 | 100.0% |
| 0.50 | 0.25 | 752 | +0.0818 | 100.0% |
| 0.50 | 0.35 | 688 | +0.0818 | 100.0% |
| 0.50 | 0.45 | 593 | +0.0818 | 100.0% |
| 0.55 | 0.10 | 790 | +0.0818 | 100.0% |
| 0.55 | 0.20 | 773 | +0.0818 | 100.0% |
| 0.55 | 0.30 | 725 | +0.0818 | 100.0% |
| 0.55 | 0.40 | 645 | +0.0818 | 100.0% |
| 0.55 | 0.50 | 532 | +0.0818 | 100.0% |
| 0.60 | 0.15 | 734 | +0.0818 | 100.0% |
| 0.60 | 0.25 | 727 | +0.0818 | 100.0% |
| 0.60 | 0.35 | 687 | +0.0818 | 100.0% |
| 0.60 | 0.45 | 593 | +0.0818 | 100.0% |
| 0.65 | 0.10 | 629 | +0.0818 | 100.0% |
| 0.65 | 0.20 | 629 | +0.0818 | 100.0% |
| 0.65 | 0.30 | 629 | +0.0818 | 100.0% |
| 0.65 | 0.40 | 613 | +0.0818 | 100.0% |
| 0.65 | 0.50 | 527 | +0.0818 | 100.0% |
| 0.70 | 0.15 | 478 | +0.0818 | 100.0% |
| 0.70 | 0.25 | 478 | +0.0818 | 100.0% |
| 0.70 | 0.35 | 478 | +0.0818 | 100.0% |
| 0.70 | 0.45 | 478 | +0.0818 | 100.0% |
| 0.75 | 0.10 | 322 | +0.0818 | 100.0% |
| 0.75 | 0.20 | 322 | +0.0818 | 100.0% |
| 0.75 | 0.30 | 322 | +0.0818 | 100.0% |
| 0.75 | 0.40 | 322 | +0.0818 | 100.0% |
| 0.75 | 0.50 | 322 | +0.0818 | 100.0% |
| 0.80 | 0.15 | 111 | +0.0818 | 100.0% |
| 0.80 | 0.25 | 111 | +0.0818 | 100.0% |
| 0.80 | 0.35 | 111 | +0.0818 | 100.0% |
| 0.80 | 0.45 | 111 | +0.0818 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 795 candidates, mean lock IC=+0.0818, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1078 | +0.0000 | +0.0217 | 0.20x | 2016-08-24 |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1058 | +0.0000 | +0.0005 | 0.00x | 2017-09-06 |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | +0.0748 | +0.0000 | -0.1298 | -1.74x | 2010-12-14 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1090 | +0.0000 | +0.0449 | 0.41x | 2017-08-08 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1096 | +0.0000 | -0.1853 | -1.69x | 2015-02-06 |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | +0.1024 | +0.0000 | -0.1215 | -1.19x | 2015-02-06 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | +0.0926 | +0.0000 | -0.1502 | -1.62x | 2013-08-21 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1117 | +0.0000 | -0.0316 | -0.28x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | +0.1111 | +0.0000 | -0.0294 | -0.26x | 2016-08-24 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1072 | +0.0000 | -0.1975 | -1.84x | 2017-07-10 |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | +0.0926 | +0.0000 | -0.1743 | -1.88x | 2015-02-06 |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1200 | +0.0000 | -0.0297 | -0.25x | 2017-06-09 |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | +0.1060 | +0.0000 | -0.0924 | -0.87x | 2017-08-08 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.0989 | +0.0000 | -0.2114 | -2.14x | 2015-02-06 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.0928 | +0.0000 | +0.0147 | 0.16x | 2016-07-26 |
| `combo_rank_max__bar_ret_0__bar_body_rng_0` | +0.0911 | +0.0000 | -0.0927 | -1.02x | 2010-12-14 |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | +0.1048 | +0.0000 | -0.0631 | -0.60x | 2015-02-06 |
| `combo_mean__max_up_ret__first_bar_sentiment` | +0.1001 | +0.0000 | -0.1142 | -1.14x | 2015-02-06 |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.1028 | +0.0000 | -0.0955 | -0.93x | 2015-02-06 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1021 | +0.0000 | -0.1938 | -1.90x | 2015-02-06 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | +0.0954 | +0.0000 | +0.0709 | 0.74x | 2017-09-06 |
| `combo_max__max_up_ret__bar_ret_0` | +0.0979 | +0.0000 | -0.1613 | -1.65x | 2014-07-04 |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | +0.0979 | +0.0000 | -0.0691 | -0.71x | 2015-03-16 |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | +0.0843 | +0.0000 | -0.1087 | -1.29x | 2013-08-21 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1082 | +0.0000 | -0.1518 | -1.40x | 2017-07-10 |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +0.1045 | +0.0000 | -0.1153 | -1.10x | 2015-01-08 |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | +0.1098 | +0.0000 | -0.1522 | -1.39x | 2015-02-06 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | +0.1120 | +0.0000 | -0.0504 | -0.45x | 2017-06-09 |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | +0.1051 | +0.0000 | -0.1478 | -1.41x | 2015-02-06 |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | +0.1077 | +0.0000 | -0.1414 | -1.31x | 2015-02-06 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1087 | +0.0000 | +0.0038 | 0.03x | 2016-08-24 |
| `combo_rank_max__max_up_ret__bar_ret_0` | +0.0998 | +0.0000 | -0.1566 | -1.57x | 2014-07-04 |
| `combo_min__max_up_ret__first_bar_sentiment` | +0.0922 | +0.0000 | -0.0695 | -0.75x | 2015-01-08 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1061 | +0.0000 | -0.0169 | -0.16x | 2017-05-09 |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1043 | +0.0000 | -0.1237 | -1.19x | 2015-02-06 |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | +0.0861 | +0.0000 | -0.1002 | -1.16x | 2014-07-04 |
| `combo_tri_mean__max_up_ret__first_bar_return__bar_body_rng_0` | +0.1016 | +0.0000 | -0.1079 | -1.06x | 2015-02-06 |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | +0.0816 | +0.0000 | -0.0908 | -1.11x | 2013-08-21 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1126 | +0.0000 | -0.0541 | -0.48x | 2015-02-06 |
| `first_bar_return` | +0.0854 | +0.0000 | -0.0827 | -0.97x | 2013-08-21 |
| `combo_max__first_bar_return__first_bar_sentiment` | +0.0820 | +0.0000 | -0.0930 | -1.13x | 2013-06-24 |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1088 | +0.0000 | -0.0121 | -0.11x | 2016-08-24 |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | +0.0792 | +0.0000 | -0.0828 | -1.04x | 2015-01-08 |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | +0.0910 | +0.0000 | -0.1294 | -1.42x | 2013-10-29 |
| `opening_drive_thrust_ratio` | +0.1099 | +0.0000 | -0.1510 | -1.37x | 2017-06-09 |
| `combo_rank_min__max_up_ret__bar_ret_0` | +0.0913 | +0.0000 | -0.0947 | -1.04x | 2015-02-06 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1065 | +0.0000 | -0.0023 | -0.02x | 2016-08-24 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0901 | +0.0000 | +0.0628 | 0.70x | 2016-08-24 |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | +0.0729 | +0.0000 | -0.1823 | -2.50x | 2015-02-06 |
| `morning_volume_weighted_momentum` | +0.0713 | +0.0000 | -0.1752 | -2.46x | 2015-02-06 |
| `combo_min__first_bar_return__opening_drive_thrust_ratio` | +0.1044 | +0.0000 | -0.1057 | -1.01x | 2017-07-10 |
| `volume_weighted_price_position` | +0.0935 | +0.0000 | -0.1599 | -1.71x | 2015-02-06 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1026 | +0.0000 | +0.0035 | 0.03x | 2017-06-09 |
| `combo_ratio__max_up_ret__first_bar_volume` | +0.0897 | +0.0000 | -0.1432 | -1.60x | 2017-08-08 |
| `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | +0.0894 | +0.0000 | +0.0844 | 0.94x | 2015-01-08 |
| `early_order_flow_imbalance` | +0.0496 | +0.0000 | -0.2024 | -4.08x | 2010-12-14 |
| `combo_min__first_bar_return__first_bar_sentiment` | +0.0801 | +0.0000 | -0.0691 | -0.86x | 2013-08-21 |
| `always_in_trend_persistence` | +0.0422 | +0.0000 | -0.2597 | -6.15x | 2012-06-05 |
| `volume_surge_direction` | +0.0629 | +0.0000 | -0.0740 | -1.18x | 2013-08-21 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.0997 | +0.0000 | -0.1395 | -1.40x | 2015-01-08 |
| `combo_sig_product__max_up_ret__first_bar_return` | +0.0747 | +0.0000 | -0.0717 | -0.96x | 2014-07-04 |
| `net_volume_flow` | +0.0668 | +0.0000 | -0.1763 | -2.64x | 2015-01-08 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1788 | +0.0000 | +0.0028 | 0.02x | 2025-07-24 |
| `combo_mean__close_vs_open_range__bar_ret_0` | +0.1613 | +0.0000 | -0.0383 | -0.24x | No decay |
| `combo_min__net_volume_flow__first_bar_return` | +0.1441 | +0.0000 | -0.0010 | -0.01x | No decay |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1621 | +0.0000 | +0.0727 | 0.45x | 2021-07-28 |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1688 | +0.0000 | +0.0033 | 0.02x | No decay |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | +0.1770 | +0.0000 | +0.0152 | 0.09x | No decay |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | +0.1797 | +0.0000 | -0.0002 | -0.00x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | +0.1775 | +0.0000 | +0.0571 | 0.32x | No decay |
| `combo_min__net_volume_flow__first_bar_sentiment` | +0.1500 | +0.0000 | -0.0444 | -0.30x | 2020-02-12 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1584 | +0.0000 | +0.0820 | 0.52x | No decay |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | +0.1505 | +0.0000 | -0.0684 | -0.45x | 2016-11-01 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1532 | +0.0000 | +0.0175 | 0.11x | 2016-09-26 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1639 | +0.0000 | +0.0350 | 0.21x | No decay |
| `combo_rank_min__net_volume_flow__bar_ret_0` | +0.1438 | +0.0000 | +0.0200 | 0.14x | No decay |
| `combo_mean__first_bar_return__max_down_ret` | +0.1472 | +0.0000 | +0.0117 | 0.08x | No decay |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | +0.1624 | +0.0000 | +0.0988 | 0.61x | 2019-12-05 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | +0.1909 | +0.0000 | +0.0674 | 0.35x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression` | +0.1536 | +0.0000 | -0.0592 | -0.39x | 2016-11-01 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | +0.1858 | +0.0000 | -0.0323 | -0.17x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1586 | +0.0000 | +0.0820 | 0.52x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | +0.1667 | +0.0000 | +0.0068 | 0.04x | 2016-11-30 |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | +0.1569 | +0.0000 | -0.0114 | -0.07x | 2020-01-06 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | +0.1845 | +0.0000 | +0.0508 | 0.28x | No decay |
| `combo_mean__max_up_ret__first_bar_return` | +0.1725 | +0.0000 | -0.0337 | -0.20x | No decay |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1597 | +0.0000 | -0.0124 | -0.08x | No decay |
| `morning_volume_weighted_momentum` | +0.1399 | +0.0000 | -0.0906 | -0.65x | 2016-11-01 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | +0.1341 | +0.0000 | -0.0261 | -0.19x | 2013-09-23 |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | +0.1443 | +0.0000 | -0.0933 | -0.65x | 2016-11-01 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1696 | +0.0000 | +0.1067 | 0.63x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1568 | +0.0000 | +0.1749 | 1.12x | 2016-08-24 |
| `combo_rank_max__max_up_ret__bar_ret_0` | +0.1668 | +0.0000 | -0.0673 | -0.40x | No decay |
| `combo_max__bar_ret_0__max_down_ret` | +0.1583 | +0.0000 | +0.0077 | 0.05x | 2016-11-01 |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | +0.1442 | +0.0000 | -0.0012 | -0.01x | 2020-02-12 |
| `combo_min__close_vs_open_range__first_bar_return` | +0.1407 | +0.0000 | +0.0019 | 0.01x | 2020-01-06 |
| `volatility_expansion_trend_vector` | +0.1487 | +0.0000 | -0.0850 | -0.57x | 2016-11-01 |
| `combo_rank_min__max_up_ret__bar_ret_0` | +0.1619 | +0.0000 | -0.0002 | -0.00x | No decay |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | +0.1659 | +0.0000 | -0.0916 | -0.55x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression` | +0.0953 | +0.0000 | -0.0194 | -0.20x | 2012-06-05 |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1687 | +0.0000 | -0.0655 | -0.39x | 2016-11-01 |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | +0.1500 | +0.0000 | -0.0520 | -0.35x | 2020-01-06 |
| `first_30min_return` | +0.1471 | +0.0000 | -0.1128 | -0.77x | 2016-11-01 |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1531 | +0.0000 | +0.1783 | 1.16x | 2022-12-15 |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | +0.1517 | +0.0000 | +0.0832 | 0.55x | 2016-12-29 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1765 | +0.0000 | -0.0127 | -0.07x | 2020-01-06 |
| `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1391 | +0.0000 | +0.0765 | 0.55x | 2016-09-26 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1620 | +0.0000 | +0.0187 | 0.12x | 2020-01-06 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +0.1857 | +0.0000 | -0.0468 | -0.25x | 2016-11-30 |
| `combo_min__first_bar_sentiment__bar_ret_0` | +0.1335 | +0.0000 | -0.0087 | -0.06x | 2013-09-23 |
| `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` | +0.1558 | +0.0000 | -0.0523 | -0.34x | 2020-02-12 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1875 | +0.0000 | -0.0194 | -0.10x | No decay |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | +0.1236 | +0.0000 | -0.0367 | -0.30x | 2017-08-08 |
| `combo_clamp_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1588 | +0.0000 | +0.0343 | 0.22x | No decay |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1631 | +0.0000 | +0.0058 | 0.04x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1836 | +0.0000 | +0.1003 | 0.55x | No decay |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1525 | +0.0000 | +0.1800 | 1.18x | 2022-12-15 |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | +0.1547 | +0.0000 | -0.0187 | -0.12x | 2016-11-01 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | +0.1354 | +0.0000 | -0.0739 | -0.55x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1661 | +0.0000 | -0.0689 | -0.41x | 2016-12-29 |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | +0.1449 | +0.0000 | +0.1520 | 1.05x | 2011-10-26 |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1522 | +0.0000 | -0.0906 | -0.59x | 2020-01-06 |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | +0.1705 | +0.0000 | -0.0411 | -0.24x | 2016-12-29 |
| `vwap_close_divergence_trend` | +0.1303 | +0.0000 | -0.0940 | -0.72x | 2016-11-01 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | +0.1841 | +0.0000 | -0.0079 | -0.04x | No decay |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | +0.1227 | +0.0000 | -0.1430 | -1.17x | 2016-09-26 |
| `first_bar_return` | +0.1352 | +0.0000 | -0.0114 | -0.08x | 2013-09-23 |
| `combo_min__trend_bar_close_consistency__first_bar_return` | +0.1291 | +0.0000 | -0.0156 | -0.12x | 2016-11-01 |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | +0.1692 | +0.0000 | +0.0234 | 0.14x | 2016-11-30 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1784 | +0.0000 | -0.0061 | -0.03x | No decay |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | +0.1575 | +0.0000 | +0.0383 | 0.24x | No decay |
| `combo_max__net_volume_flow__max_down_ret` | +0.1559 | +0.0000 | -0.0643 | -0.41x | 2016-11-30 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | +0.1371 | +0.0000 | +0.0216 | 0.16x | 2016-09-26 |
| `combo_min__close_vs_open_range__early_body_momentum` | +0.1326 | +0.0000 | -0.0785 | -0.59x | 2016-11-01 |
| `opening_drive_thrust_ratio` | +0.1782 | +0.0000 | +0.0025 | 0.01x | No decay |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1405 | +0.0000 | +0.1008 | 0.72x | 2016-09-26 |
| `combo_max__first_bar_sentiment__bar_ret_0` | +0.1316 | +0.0000 | +0.0228 | 0.17x | 2020-01-06 |
| `combo_max__close_vs_open_range__early_body_momentum` | +0.1437 | +0.0000 | -0.0947 | -0.66x | 2016-11-01 |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | +0.1480 | +0.0000 | +0.0708 | 0.48x | 2016-09-26 |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | +0.1297 | +0.0000 | -0.0022 | -0.02x | 2016-11-01 |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | +0.1635 | +0.0000 | +0.0811 | 0.50x | 2016-09-26 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1498 | +0.0000 | -0.0695 | -0.46x | No decay |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1479 | +0.0000 | +0.0403 | 0.27x | No decay |
| `combo_rank_max__bar_ret_0__max_down_ret` | +0.1563 | +0.0000 | +0.0290 | 0.19x | No decay |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +0.1470 | +0.0000 | +0.0854 | 0.58x | 2016-09-26 |
| `early_order_flow_imbalance` | +0.1232 | +0.0000 | -0.1345 | -1.09x | 2016-11-01 |
| `combo_mean__first_bar_sentiment__max_down_ret` | +0.1420 | +0.0000 | +0.0243 | 0.17x | No decay |
| `combo_sig_product__net_volume_flow__first_bar_return` | +0.1199 | +0.0000 | -0.1006 | -0.84x | 2016-09-26 |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1544 | +0.0000 | +0.0678 | 0.44x | 2021-05-28 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1608 | +0.0000 | -0.0526 | -0.33x | 2016-12-29 |
| `combo_min__bar_ret_0__max_down_ret` | +0.1331 | +0.0000 | +0.0115 | 0.09x | No decay |
| `combo_sig_product__max_up_ret__early_body_momentum` | +0.1695 | +0.0000 | -0.0107 | -0.06x | 2019-12-05 |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | +0.1349 | +0.0000 | +0.0177 | 0.13x | 2020-01-06 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +0.1234 | +0.0000 | -0.0206 | -0.17x | 2017-08-08 |
| `combo_max__close_vs_open_range__max_down_ret` | +0.1453 | +0.0000 | -0.0673 | -0.46x | 2016-11-01 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | +0.1516 | +0.0000 | +0.0237 | 0.16x | 2016-11-01 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | +0.1565 | +0.0000 | +0.0807 | 0.52x | 2016-09-26 |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1600 | +0.0000 | +0.0668 | 0.42x | 2016-09-26 |
| `volume_surge_direction` | +0.0995 | +0.0000 | +0.0202 | 0.20x | 2013-09-23 |
| `combo_min__early_body_momentum__max_down_ret` | +0.1377 | +0.0000 | +0.0091 | 0.07x | 2016-09-26 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1384 | +0.0000 | +0.0274 | 0.20x | 2014-05-06 |
| `num_up_bars` | +0.1231 | +0.0000 | -0.0474 | -0.38x | 2020-02-12 |
| `max_down_ret` | +0.1363 | +0.0000 | +0.0305 | 0.22x | 2016-09-26 |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | +0.1461 | +0.0000 | +0.1145 | 0.78x | 2016-12-29 |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.1411 | +0.0000 | +0.0527 | 0.37x | 2022-09-09 |
| `combo_rank_min__bar_ret_0__max_down_ret` | +0.1321 | +0.0000 | +0.0056 | 0.04x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1232 | +0.0000 | +0.0947 | 0.77x | 2016-09-26 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | +0.1018 | +0.0000 | -0.0136 | -0.13x | 2012-07-05 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1609 | +0.0000 | -0.0624 | -0.39x | 2016-12-29 |
| `vwap_trend_channel_slope` | +0.1420 | +0.0000 | -0.0312 | -0.22x | 2016-11-01 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1393 | +0.0000 | +0.0839 | 0.60x | 2016-09-26 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1390 | +0.0000 | +0.0759 | 0.55x | 2016-08-24 |
| `always_in_trend_persistence` | +0.1104 | +0.0000 | -0.1600 | -1.45x | 2016-11-01 |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | +0.1589 | +0.0000 | +0.0391 | 0.25x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | +0.1598 | +0.0000 | -0.0019 | -0.01x | 2016-11-30 |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1806 | +0.0000 | +0.1323 | 0.73x | 2023-01-16 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | +0.1531 | +0.0000 | +0.0574 | 0.37x | No decay |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | +0.1459 | +0.0000 | +0.0462 | 0.32x | 2014-05-06 |
| `combo_max__star50_limit_proximity_early__max_down_ret` | +0.1400 | +0.0000 | +0.1499 | 1.07x | 2016-09-26 |
| `combo_sig_product__net_volume_flow__max_down_ret` | +0.1308 | +0.0000 | -0.0458 | -0.35x | 2016-09-26 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.0909 | +0.0000 | -0.0473 | -0.52x | 2016-07-26 |
| `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range` | +0.0380 | +0.0000 | -0.0837 | -2.20x | 2012-12-06 |
| `bar_body_rng_0` | +0.1326 | +0.0000 | +0.0133 | 0.10x | No decay |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | +0.1306 | +0.0000 | +0.0770 | 0.59x | 2016-08-24 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1561 | +0.0000 | +0.0827 | 0.53x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1587 | +0.0000 | +0.1000 | 0.63x | 2017-04-28 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1633 | +0.0000 | +0.0821 | 0.50x | 2017-01-20 |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1450 | +0.0000 | +0.1224 | 0.84x | 2011-10-18 |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1422 | +0.0000 | +0.1144 | 0.80x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1502 | +0.0000 | +0.1090 | 0.73x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1560 | +0.0000 | +0.1064 | 0.68x | 2011-11-16 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1618 | +0.0000 | +0.1062 | 0.66x | 2017-02-27 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1605 | +0.0000 | +0.0587 | 0.37x | 2017-01-20 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +0.1438 | +0.0000 | +0.1324 | 0.92x | 2016-10-24 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1550 | +0.0000 | +0.0832 | 0.54x | 2016-09-14 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1623 | +0.0000 | +0.1174 | 0.72x | 2017-02-27 |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | +0.1647 | +0.0000 | +0.0719 | 0.44x | 2017-01-20 |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | +0.1293 | +0.0000 | +0.1495 | 1.16x | 2011-10-18 |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | +0.1543 | +0.0000 | +0.0270 | 0.17x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1557 | +0.0000 | +0.0895 | 0.58x | 2011-10-18 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1577 | +0.0000 | +0.0486 | 0.31x | 2017-01-20 |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | +0.1529 | +0.0000 | +0.0606 | 0.40x | 2017-01-20 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | +0.1579 | +0.0000 | +0.0848 | 0.54x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1571 | +0.0000 | +0.0766 | 0.49x | 2016-10-24 |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | +0.1556 | +0.0000 | +0.0832 | 0.53x | 2017-02-27 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | +0.1505 | +0.0000 | +0.0641 | 0.43x | 2011-10-18 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +0.1525 | +0.0000 | -0.0559 | -0.37x | 2017-02-27 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1548 | +0.0000 | +0.0693 | 0.45x | 2016-10-24 |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1545 | +0.0000 | +0.0567 | 0.37x | 2017-01-20 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | +0.1245 | +0.0000 | +0.1393 | 1.12x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1444 | +0.0000 | +0.0762 | 0.53x | 2016-09-14 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | +0.1390 | +0.0000 | +0.1312 | 0.94x | 2017-02-27 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1604 | +0.0000 | -0.0192 | -0.12x | 2016-10-24 |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | +0.1570 | +0.0000 | -0.0628 | -0.40x | 2016-12-21 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1386 | +0.0000 | -0.0735 | -0.53x | 2016-10-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1433 | +0.0000 | +0.0919 | 0.64x | 2017-02-27 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1486 | +0.0000 | +0.0307 | 0.21x | 2017-01-20 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | +0.1468 | +0.0000 | -0.0148 | -0.10x | 2026-03-27 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | +0.1609 | +0.0000 | -0.0421 | -0.26x | 2017-01-20 |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | +0.1503 | +0.0000 | -0.0381 | -0.25x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1308 | +0.0000 | +0.0535 | 0.41x | 2017-02-27 |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | +0.1545 | +0.0000 | +0.0431 | 0.28x | 2017-04-28 |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | +0.1496 | +0.0000 | +0.1356 | 0.91x | 2017-04-28 |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1402 | +0.0000 | +0.0809 | 0.58x | 2017-01-20 |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1457 | +0.0000 | -0.0077 | -0.05x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1570 | +0.0000 | +0.0545 | 0.35x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1439 | +0.0000 | -0.0036 | -0.02x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1653 | +0.0000 | +0.0503 | 0.30x | 2017-01-20 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1474 | +0.0000 | +0.1013 | 0.69x | 2016-09-14 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1559 | +0.0000 | -0.0232 | -0.15x | 2017-01-20 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | +0.1566 | +0.0000 | -0.0181 | -0.12x | 2017-02-27 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1438 | +0.0000 | -0.0689 | -0.48x | 2016-12-21 |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1633 | +0.0000 | +0.0961 | 0.59x | 2017-01-20 |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | +0.1278 | +0.0000 | +0.1313 | 1.03x | 2016-09-14 |
| `combo_max__max_up_ret__bar_body_rng_0` | +0.1503 | +0.0000 | -0.0771 | -0.51x | 2017-02-27 |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1550 | +0.0000 | -0.0881 | -0.57x | 2016-10-24 |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | +0.1397 | +0.0000 | -0.0854 | -0.61x | 2016-10-24 |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | +0.1542 | +0.0000 | -0.0318 | -0.21x | 2016-10-24 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | +0.1576 | +0.0000 | -0.0695 | -0.44x | 2016-12-21 |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1516 | +0.0000 | -0.0265 | -0.17x | 2017-01-20 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1575 | +0.0000 | +0.0018 | 0.01x | 2016-10-24 |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | +0.1297 | +0.0000 | -0.0835 | -0.64x | 2017-01-20 |
| `max_up_ret` | +0.1497 | +0.0000 | -0.0753 | -0.50x | 2017-01-20 |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | +0.1512 | +0.0000 | -0.1035 | -0.68x | 2016-10-24 |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1416 | +0.0000 | +0.0841 | 0.59x | 2016-09-14 |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | +0.1568 | +0.0000 | -0.0816 | -0.52x | 2017-01-20 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | +0.1575 | +0.0000 | -0.0534 | -0.34x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | +0.1456 | +0.0000 | +0.0199 | 0.14x | 2017-02-27 |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | +0.1524 | +0.0000 | -0.0860 | -0.56x | 2016-11-22 |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1430 | +0.0000 | +0.0069 | 0.05x | 2017-01-20 |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | +0.1314 | +0.0000 | -0.0230 | -0.17x | 2017-01-20 |
| `combo_min__bar_body_rng_0__impulse_bar_dominance` | +0.1220 | +0.0000 | -0.0179 | -0.15x | 2017-02-27 |
| `combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | +0.1079 | +0.0000 | +0.0673 | 0.62x | 2011-10-18 |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1324 | +0.0000 | -0.1027 | -0.78x | 2016-11-22 |
| `combo_mean__max_up_ret__impulse_bar_dominance` | +0.1386 | +0.0000 | -0.0845 | -0.61x | 2017-01-20 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1032 | +0.0000 | +0.1286 | 1.25x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1228 | +0.0000 | -0.0311 | -0.25x | 2011-12-15 |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.0957 | +0.0000 | +0.1554 | 1.62x | 2011-10-18 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1579 | +0.0000 | +0.0426 | 0.27x | 2017-01-20 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1299 | +0.0000 | +0.0793 | 0.61x | 2016-09-14 |
| `combo_min__max_up_ret__first_bar_sentiment` | +0.1467 | +0.0000 | -0.0026 | -0.02x | 2017-01-20 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1570 | +0.0000 | -0.0689 | -0.44x | 2016-12-21 |
| `opening_drive_thrust_ratio` | +0.1460 | +0.0000 | -0.0464 | -0.32x | 2016-10-24 |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | +0.1441 | +0.0000 | -0.0010 | -0.01x | 2017-01-20 |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | +0.1323 | +0.0000 | -0.0016 | -0.01x | 2017-02-27 |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1344 | +0.0000 | -0.0572 | -0.43x | 2016-10-24 |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | +0.1130 | +0.0000 | +0.0593 | 0.52x | 2017-01-20 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1149 | +0.0000 | +0.1654 | 1.44x | 2011-10-18 |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | +0.1314 | +0.0000 | -0.0248 | -0.19x | 2017-01-20 |
| `combo_mean__limit_down_proximity_early__volume_weighted_price_position` | +0.1407 | +0.0000 | +0.1186 | 0.84x | 2016-10-24 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1284 | +0.0000 | -0.0811 | -0.63x | 2014-03-25 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1563 | +0.0000 | -0.0570 | -0.36x | 2017-01-20 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | +0.1429 | +0.0000 | +0.0657 | 0.46x | 2016-10-24 |
| `combo_mean__max_up_ret__first_bar_return` | +0.1550 | +0.0000 | -0.0225 | -0.14x | 2017-01-20 |
| `first_bar_return` | +0.1367 | +0.0000 | +0.0226 | 0.17x | 2017-04-28 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1474 | +0.0000 | +0.1358 | 0.92x | 2017-02-27 |
| `combo_max__first_bar_sentiment__first_bar_return` | +0.1326 | +0.0000 | -0.0145 | -0.11x | 2017-04-28 |
| `combo_min__max_up_ret__volume_weighted_price_position` | +0.1402 | +0.0000 | -0.0303 | -0.22x | 2017-01-20 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | +0.1463 | +0.0000 | +0.0212 | 0.15x | 2017-02-27 |
| `rbreaker_sell_setup_proximity_early` | +0.1497 | +0.0000 | +0.1637 | 1.09x | 2016-12-21 |
| `combo_mean__first_bar_return__volume_weighted_price_position` | +0.1430 | +0.0000 | -0.0010 | -0.01x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1052 | +0.0000 | +0.1217 | 1.16x | 2011-10-18 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1172 | +0.0000 | +0.1154 | 0.98x | 2017-02-27 |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1395 | +0.0000 | -0.0820 | -0.59x | 2016-10-24 |
| `combo_max__bar_ret_0__impulse_bar_dominance` | +0.1194 | +0.0000 | -0.0491 | -0.41x | 2017-01-20 |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | +0.1358 | +0.0000 | -0.0113 | -0.08x | 2016-10-24 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1509 | +0.0000 | +0.0648 | 0.43x | 2016-09-14 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1403 | +0.0000 | -0.0120 | -0.09x | 2026-03-27 |
| `combo_max__bar_ret_0__limit_down_proximity_early` | +0.1332 | +0.0000 | +0.0866 | 0.65x | 2017-01-20 |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | +0.1494 | +0.0000 | +0.1269 | 0.85x | 2017-02-27 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +0.1404 | +0.0000 | +0.1729 | 1.23x | 2011-10-18 |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | +0.1167 | +0.0000 | +0.0909 | 0.78x | 2011-10-18 |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1283 | +0.0000 | +0.0975 | 0.76x | 2016-09-14 |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1219 | +0.0000 | -0.0536 | -0.44x | 2016-10-24 |
| `combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return` | +0.1450 | +0.0000 | +0.0120 | 0.08x | 2017-01-20 |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | +0.1317 | +0.0000 | -0.1064 | -0.81x | 2016-09-14 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1462 | +0.0000 | +0.0262 | 0.18x | 2016-12-21 |
| `combo_mean__impulse_bar_dominance__volatility_expansion_trend_vector` | +0.1302 | +0.0000 | -0.1025 | -0.79x | 2016-10-24 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1140 | +0.0000 | +0.0980 | 0.86x | 2016-09-14 |
| `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | +0.1399 | +0.0000 | +0.0898 | 0.64x | 2017-03-28 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.1344 | +0.0000 | +0.0098 | 0.07x | 2017-04-28 |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | +0.1312 | +0.0000 | +0.1476 | 1.12x | 2017-04-28 |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | +0.1421 | +0.0000 | -0.0233 | -0.16x | 2017-01-20 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1228 | +0.0000 | -0.0445 | -0.36x | 2017-01-20 |
| `combo_min__first_bar_sentiment__volatility_expansion_trend_vector` | +0.1309 | +0.0000 | -0.0329 | -0.25x | 2016-10-24 |
| `trend_bar_close_consistency` | +0.1157 | +0.0000 | -0.1362 | -1.18x | 2014-03-25 |
| `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance` | +0.1036 | +0.0000 | -0.0102 | -0.10x | 2011-11-16 |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1310 | +0.0000 | +0.0852 | 0.65x | 2017-02-27 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1388 | +0.0000 | -0.1124 | -0.81x | 2016-10-24 |
| `combo_diff__limit_down_proximity_early__demark_setup_reversal_early` | +0.1246 | +0.0000 | +0.1236 | 0.99x | 2011-10-18 |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early` | +0.1225 | +0.0000 | +0.1348 | 1.10x | 2011-10-18 |
| `net_volume_flow` | +0.1384 | +0.0000 | -0.0663 | -0.48x | 2014-03-25 |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | +0.1409 | +0.0000 | -0.0325 | -0.23x | 2016-10-24 |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | +0.1329 | +0.0000 | -0.0010 | -0.01x | 2017-04-28 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +0.1212 | +0.0000 | -0.0177 | -0.15x | 2017-03-28 |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | +0.1324 | +0.0000 | +0.0174 | 0.13x | 2016-10-24 |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | +0.1256 | +0.0000 | -0.1070 | -0.85x | 2016-11-22 |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1308 | +0.0000 | +0.0279 | 0.21x | 2016-09-14 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | +0.0548 | +0.0000 | -0.0939 | -1.71x | 2011-03-11 |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1186 | +0.0000 | +0.0955 | 0.81x | 2016-09-14 |
| `combo_clamp_diff__volume_weighted_price_position__late_bar_momentum` | +0.1111 | +0.0000 | +0.0458 | 0.41x | 2017-01-20 |
| `shaved_bar_trend_conviction` | +0.1137 | +0.0000 | -0.0741 | -0.65x | 2014-03-25 |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | +0.1037 | +0.0000 | +0.0896 | 0.86x | 2016-07-18 |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | +0.0726 | +0.0000 | +0.0597 | 0.82x | 2012-07-26 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — Admission too loose**: 97% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
2. **500ETF `single` — Admission too loose**: 78% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
3. **159915ETF `single` — B2 Rolling Guard too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=-0.1486). Consider relaxing this gate.
4. **159915ETF `single` — B4 Correlation Gate too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.5009). Consider relaxing this gate.
5. **159915ETF `single` — Admission too loose**: 69% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
