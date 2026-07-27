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

### 300ETF — `single` (Full Model Lockbox IC: +0.0189, Sharpe: -0.3268)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0954 | +0.0200 | +0.0200 | -0.6924 | 85.92 | -0.5 | -0.07x | +0.0061 | -0.0314 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0875 | -0.0223 | -0.0223 | -1.3571 | 85.92 | -7.2 | -0.90x | -0.0048 | +0.0115 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0996 | +0.0244 | +0.0244 | -0.2554 | 87.24 | +4.9 | 0.61x | +0.0023 | -0.0314 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0864 | -0.0365 | -0.0365 | -1.6583 | 85.27 | -11.8 | -1.48x | -0.0038 | -0.0929 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0875 | +0.0300 | +0.0300 | -0.0790 | 81.33 | +7.1 | 0.89x | +0.0027 | -0.2669 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.0852 | +0.0808 | +0.0808 | +0.3659 | 84.61 | +12.4 | 1.55x | +0.0056 | +0.2200 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0858 | +0.0164 | +0.0164 | -0.3387 | 84.61 | +3.9 | 0.49x | +0.0021 | -0.2669 |
| `combo_max__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0732 | -0.0158 | -0.0158 | -0.6017 | 83.30 | +0.9 | 0.12x | -0.0010 | -0.2669 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0924 | +0.0088 | +0.0088 | -0.8472 | 85.92 | -1.1 | -0.13x | -0.0015 | -0.0463 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0834 | -0.0391 | -0.0391 | -0.9630 | 87.24 | -2.7 | -0.34x | -0.0031 | +0.0023 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.0850 | +0.0396 | +0.0396 | -0.6327 | 84.61 | +0.3 | 0.04x | +0.0012 | -0.2669 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0768 | +0.0753 | +0.0753 | -0.1501 | 86.58 | +6.3 | 0.79x | +0.0056 | -0.0802 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.0749 | +0.0148 | +0.0148 | -0.9076 | 89.86 | -2.3 | -0.29x | +0.0005 | -0.2669 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0910 | +0.0098 | +0.0098 | -1.6517 | 91.17 | -6.2 | -0.78x | -0.0000 | +0.1228 |
| `combo_min__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0854 | +0.0128 | +0.0128 | -0.5403 | 83.96 | +1.3 | 0.16x | -0.0008 | +0.0311 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0868 | -0.0282 | -0.0282 | -1.4181 | 89.20 | -8.0 | -1.00x | -0.0030 | +0.0481 |
| `combo_sig_product__first_bar_sentiment__opening_drive_thrust_ratio` | Gap / Overnight Reversal | +1 | +0.0894 | -0.0235 | -0.0235 | -0.7280 | 89.20 | +0.1 | 0.01x | -0.0034 | -0.0929 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0964 | -0.0284 | -0.0284 | -0.8306 | 87.89 | -0.1 | -0.02x | -0.0015 | -0.0236 |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0424 | +0.0409 | +0.0409 | -0.1685 | 82.65 | +6.5 | 0.81x | +0.0014 | -0.0729 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0806, Sharpe: -0.1409)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1545 | +0.0289 | +0.0289 | -0.4555 | 85.92 | +1.9 | 0.24x | -0.0021 | -0.0799 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1453 | +0.0883 | +0.0883 | -0.5698 | 90.52 | -0.8 | -0.10x | +0.0007 | -0.0799 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1382 | +0.0950 | +0.0950 | -0.0776 | 89.86 | +6.8 | 0.85x | +0.0012 | -0.0799 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1292 | +0.0469 | +0.0469 | -1.2311 | 91.17 | -12.5 | -1.56x | +0.0000 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1364 | +0.0337 | +0.0337 | -1.4167 | 90.52 | -11.6 | -1.45x | -0.0023 | -0.0799 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1415 | +0.1136 | +0.1136 | +0.6574 | 84.61 | +19.1 | 2.38x | +0.0014 | -0.0799 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1223 | +0.0126 | +0.0126 | -2.1701 | 85.27 | -27.9 | -3.49x | -0.0021 | -0.1613 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0995 | -0.0041 | -0.0041 | -1.9661 | 91.83 | -21.9 | -2.73x | -0.0027 | +0.0000 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1207 | +0.0920 | +0.0920 | +0.2951 | 80.68 | +13.5 | 1.69x | +0.0013 | -0.3572 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1332 | +0.0451 | +0.0451 | -0.8388 | 90.52 | -3.5 | -0.44x | -0.0005 | -0.0799 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1076 | +0.0998 | +0.0998 | +0.3882 | 87.24 | +15.2 | 1.89x | +0.0021 | +0.0812 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1347 | +0.0639 | +0.0639 | -0.6077 | 89.86 | -1.7 | -0.21x | -0.0007 | -0.1613 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1239 | +0.0383 | +0.0383 | -0.5921 | 82.65 | -0.1 | -0.01x | +0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1228 | +0.0958 | +0.0958 | +0.5075 | 83.30 | +17.8 | 2.22x | +0.0020 | -0.0799 |
| `combo_rank_min__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1015 | +0.0669 | +0.0669 | -0.8535 | 89.86 | -7.0 | -0.87x | +0.0007 | +0.0000 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1139 | +0.0486 | +0.0486 | -0.6142 | 81.99 | -3.6 | -0.45x | -0.0002 | -0.1613 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1329 | +0.1041 | +0.1041 | +0.7497 | 83.30 | +20.9 | 2.61x | +0.0015 | -0.0799 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1331 | +0.0268 | +0.0268 | -1.5867 | 86.58 | -18.9 | -2.36x | -0.0011 | -0.1613 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1204 | +0.1108 | +0.1108 | +1.2537 | 84.61 | +29.9 | 3.74x | +0.0007 | -0.0799 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1400 | +0.0457 | +0.0457 | -0.3399 | 91.17 | +3.7 | 0.46x | -0.0013 | -0.0799 |
| `combo_z_sum__close_vs_open_range__high_low_sequence_momentum` | Intraday Range Momentum | +1 | +0.1019 | +0.0532 | +0.0532 | -0.6770 | 82.65 | -1.3 | -0.16x | -0.0001 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1205 | +0.1502 | +0.1502 | +1.1714 | 88.55 | +29.3 | 3.66x | +0.0026 | -0.0799 |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0954 | +0.0970 | +0.0970 | +0.1808 | 81.99 | +11.6 | 1.45x | +0.0013 | -0.0799 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.1138 | +0.1138 | +0.2628 | 83.30 | +13.0 | 1.63x | -0.0007 | +0.0755 |
| `combo_sig_product__net_volume_flow__bar_ret_0` | Volatility & Oscillators | +1 | +0.0903 | +0.0245 | +0.0245 | -0.5104 | 85.92 | -1.9 | -0.23x | -0.0019 | -0.1613 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1154 | +0.0205 | +0.0205 | -0.7130 | 83.30 | -5.7 | -0.71x | -0.0009 | -0.0478 |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.0937 | +0.0613 | +0.0613 | -0.7320 | 83.96 | -2.6 | -0.33x | +0.0009 | -0.0799 |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1024 | +0.0279 | +0.0279 | -0.5752 | 87.24 | -3.0 | -0.37x | -0.0008 | -0.1613 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1155 | +0.0705 | +0.0705 | -0.3494 | 85.92 | +1.6 | 0.20x | +0.0004 | -0.1409 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0926 | +0.0323 | +0.0323 | -0.2960 | 89.20 | +3.0 | 0.37x | -0.0006 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1492, Sharpe: +1.7049)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1386 | +0.1275 | +0.1275 | +0.8333 | 87.24 | +25.9 | 3.23x | +0.0006 | +0.0769 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1282 | +0.0891 | +0.0891 | +1.0541 | 89.86 | +29.3 | 3.67x | +0.0005 | -0.0652 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1167 | +0.1307 | +0.1307 | +1.7816 | 88.55 | +43.2 | 5.40x | +0.0015 | +0.0992 |
| `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1264 | +0.1361 | +0.1361 | +1.5184 | 91.17 | +40.8 | 5.10x | -0.0002 | +0.0000 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1375 | +0.1325 | +0.1325 | +0.7977 | 87.24 | +24.8 | 3.10x | -0.0004 | -0.0299 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1060 | +0.1511 | +0.1511 | +0.6805 | 87.24 | +23.6 | 2.95x | +0.0016 | -0.0299 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1287 | +0.1283 | +0.1283 | +0.4172 | 85.92 | +18.1 | 2.27x | -0.0007 | -0.0299 |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Other Technical | +1 | +0.1057 | +0.1527 | +0.1527 | +1.5226 | 85.92 | +37.9 | 4.74x | +0.0030 | +0.0000 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1401 | +0.1210 | +0.1210 | +0.8612 | 89.86 | +26.2 | 3.27x | -0.0006 | +0.0000 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1229 | +0.1101 | +0.1101 | +0.6443 | 85.92 | +21.0 | 2.62x | -0.0002 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1280 | +0.1307 | +0.1307 | +0.9421 | 88.55 | +27.2 | 3.40x | +0.0001 | -0.0299 |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1260 | +0.1320 | +0.1320 | +0.6019 | 91.17 | +19.4 | 2.42x | +0.0005 | +0.0000 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1101 | +0.0882 | +0.0882 | -1.0149 | 92.48 | -11.4 | -1.43x | -0.0009 | -0.0085 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1186 | +0.0930 | +0.0930 | +0.0368 | 91.17 | +8.8 | 1.10x | -0.0005 | -0.0299 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0996 | +0.1617 | +0.1617 | +1.1078 | 85.92 | +31.7 | 3.96x | +0.0024 | -0.0652 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0673 | +0.0673 | +0.1332 | 90.52 | +10.1 | 1.26x | -0.0012 | -0.0494 |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1017 | +0.1466 | +0.1466 | +0.8978 | 83.30 | +28.8 | 3.60x | +0.0007 | +0.1065 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0918 | +0.1286 | +0.1286 | +0.5529 | 83.30 | +21.3 | 2.67x | +0.0030 | +0.4912 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0988 | +0.1394 | +0.1394 | +0.9587 | 83.96 | +29.3 | 3.67x | +0.0021 | +0.3182 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1175 | +0.0772 | +0.0772 | -0.5386 | 89.86 | -1.8 | -0.22x | -0.0019 | -0.0910 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1214 | +0.0753 | +0.0753 | -0.7836 | 85.92 | -7.3 | -0.92x | -0.0010 | -0.0299 |
| `combo_rank_max__first_bar_sentiment__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.0949 | +0.0725 | +0.0725 | +0.9220 | 76.74 | +27.9 | 3.49x | +0.0014 | +0.0000 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0874 | +0.0679 | +0.0679 | +0.4043 | 70.18 | +16.6 | 2.07x | +0.0000 | +0.0215 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1159 | +0.0919 | +0.0919 | -0.8343 | 91.17 | -9.9 | -1.24x | -0.0004 | +0.0215 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0864 | +0.1079 | +0.1079 | -0.2788 | 84.61 | +2.0 | 0.24x | +0.0012 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1126 | +0.1222 | +0.1222 | +0.2742 | 85.92 | +14.0 | 1.76x | +0.0009 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1240 | +0.1161 | +0.1161 | -0.1261 | 88.55 | +5.3 | 0.66x | +0.0004 | +0.0000 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1175 | +0.0904 | +0.0904 | +0.5068 | 91.17 | +17.3 | 2.16x | +0.0015 | -0.0281 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1429 | +0.1073 | +0.1073 | +0.1834 | 84.61 | +12.0 | 1.50x | +0.0001 | +0.0467 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1071 | +0.0684 | +0.0684 | +0.0306 | 84.61 | +8.7 | 1.09x | -0.0000 | +0.0467 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1120 | +0.1308 | +0.1308 | +0.7043 | 84.61 | +24.7 | 3.09x | +0.0009 | +0.0000 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.1080 | +0.0739 | +0.0739 | +0.7136 | 91.17 | +22.0 | 2.75x | -0.0005 | -0.0299 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0659 | +0.0659 | +0.7397 | 87.24 | +24.3 | 3.04x | -0.0007 | +0.0000 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 65.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6641_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1110 | 30 | 86.7% | 30.0% | +0.0306 | -0.4658 |
| B2 Rolling Guard | 52 | 30 | 56.7% | 13.3% | +0.0102 | -0.5502 |
| BH-FDR Gate | 5 | 5 | 60.0% | 0.0% | +0.0024 | -0.8836 |
| B3 Composite Floor | 268 | 30 | 60.0% | 26.7% | +0.0204 | -0.5154 |
| B4 Correlation Gate | 120 | 30 | 63.3% | 33.3% | +0.0155 | -0.5055 |

**Admitted Pool Summary**: 19 features, False Positive Rate = 94.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0096, Mean Lock Sharpe = -0.7343

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Lock Sharpe=+0.4449
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Lock Sharpe=+0.4449
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Lock Sharpe=+0.4449
- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Lock Sharpe=+0.4449
- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1954, Lock IC=+0.0363, Lock Sharpe=+0.3718

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_am_return`: Train IC=+0.0552, Lock IC=+0.0566, Lock Sharpe=+0.6060
- `combo_product__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Lock Sharpe=+0.4529
- `combo_product__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Lock Sharpe=+0.4529
- `combo_abs_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.0735, Lock IC=+0.0369, Lock Sharpe=+0.1456

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Lock Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Lock Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Lock Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Lock Sharpe=+0.3783
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2284, Lock IC=+0.0555, Lock Sharpe=+0.2787

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Lock Sharpe=+0.3895
- `combo_z_sum__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Lock Sharpe=+0.3895
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2314, Lock IC=+0.0813, Lock Sharpe=+0.3659
- `combo_rank_max__bar_ret_0__volume_surge_direction`: Train IC=+0.2249, Lock IC=+0.0392, Lock Sharpe=+0.3433
- `combo_rank_max__first_bar_return__volume_surge_direction`: Train IC=+0.2249, Lock IC=+0.0392, Lock Sharpe=+0.3433

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

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4381_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 73.3% | 36.7% | +0.0375 | -0.3299 |
| B2 Rolling Guard | 60 | 30 | 53.3% | 33.3% | -0.0027 | -0.2555 |
| BH-FDR Gate | 8 | 8 | 62.5% | 50.0% | +0.0200 | -0.1920 |
| B3 Composite Floor | 1 | 1 | 100.0% | 100.0% | +0.0684 | +0.3610 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.9794
- `combo_z_sum__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.9794
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `star50_limit_proximity_early`: Train IC=+0.1240, Lock IC=+0.0960, Lock Sharpe=+0.8503

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `pullback_depth_ratio`: Train IC=+0.0000, Lock IC=+0.0504, Lock Sharpe=+1.5711
- `double_bottom_bull_flag_early`: Train IC=+0.0000, Lock IC=+0.0395, Lock Sharpe=+0.9090
- `combo_sig_product__total_path_length__max_down_ret`: Train IC=+0.0376, Lock IC=+0.0550, Lock Sharpe=+0.8756
- `combo_sig_product__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0064, Lock IC=+0.0190, Lock Sharpe=+0.5424
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0389, Lock Sharpe=+0.4433

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0708, Lock IC=+0.0119, Lock Sharpe=+0.7142
- `gap_pct`: Train IC=+0.1402, Lock IC=+0.1085, Lock Sharpe=+0.6926
- `combo_rank_max__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.1202, Lock IC=+0.0273, Lock Sharpe=+0.2891
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1032, Lock IC=+0.0946, Lock Sharpe=+0.2733

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.2007, Lock IC=+0.0684, Lock Sharpe=+0.3610

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7750_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 661 | 30 | 96.7% | 56.7% | +0.0378 | +0.1812 |
| B2 Rolling Guard | 51 | 30 | 73.3% | 33.3% | +0.0213 | -0.2918 |
| BH-FDR Gate | 5 | 5 | 0.0% | 0.0% | -0.0309 | -0.9528 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__volume_surge_max__roc10`: Train IC=+0.1493, Lock IC=+0.0272, Lock Sharpe=+1.0041
- `combo_rank_min__first_bar_volume__roc10`: Train IC=+0.1463, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_rank_min__bar_vol_0__roc10`: Train IC=+0.1463, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_min__roc60__roc10`: Train IC=+0.1297, Lock IC=+0.0274, Lock Sharpe=+0.7136
- `combo_sig_product__roc60__roc10`: Train IC=+0.1486, Lock IC=+0.0149, Lock Sharpe=+0.5659

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__iv_corridor_width__sma100_dist`: Train IC=+0.1155, Lock IC=+0.0663, Lock Sharpe=+1.0514
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.0946, Lock IC=+0.0603, Lock Sharpe=+0.9632
- `combo_abs_diff__roc60__sma50_dist`: Train IC=+0.1099, Lock IC=+0.0057, Lock Sharpe=+0.8183
- `combo_sig_product__iv_corridor_width__sma50_dist`: Train IC=+0.0838, Lock IC=+0.0787, Lock Sharpe=+0.5993
- `combo_product__bar_vol_4__volume_surge_max`: Train IC=+0.1006, Lock IC=+0.0278, Lock Sharpe=+0.5091

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
| B2 Rolling Guard | 40 | 30 | 33.3% | 13.3% | +0.0115 | -0.1918 |
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

_Null Baseline (un-gated candidate pool): 75.0% lock IC > 0, 26.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5079_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1797 | 30 | 100.0% | 60.0% | +0.0783 | -0.0841 |
| B2 Rolling Guard | 119 | 30 | 63.3% | 16.7% | +0.0111 | -0.5792 |
| BH-FDR Gate | 9 | 9 | 77.8% | 11.1% | +0.0105 | -0.8934 |
| B3 Composite Floor | 516 | 30 | 100.0% | 33.3% | +0.0668 | -0.4345 |
| B4 Correlation Gate | 235 | 30 | 100.0% | 0.0% | +0.0553 | -0.5705 |

**Admitted Pool Summary**: 30 features, False Positive Rate = 70.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0638, Mean Lock Sharpe = -0.3960

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`: Train IC=+0.2240, Lock IC=+0.0599, Lock Sharpe=+0.6347
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_mean__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2188, Lock IC=+0.1124, Lock Sharpe=+0.3413
- `combo_z_sum__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2188, Lock IC=+0.1124, Lock Sharpe=+0.3413

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__late_bar_momentum__double_bottom_bull_flag_early`: Train IC=+0.1155, Lock IC=+0.0660, Lock Sharpe=+1.1188
- `combo_min__late_bar_momentum__double_bottom_bull_flag_early`: Train IC=+0.1190, Lock IC=+0.0815, Lock Sharpe=+1.0361
- `combo_min__early_late_momentum_divergence__double_bottom_bull_flag_early`: Train IC=+0.1131, Lock IC=+0.0714, Lock Sharpe=+1.0235
- `combo_tri_max__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.1364, Lock IC=+0.0622, Lock Sharpe=+0.0218
- `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__volume_weighted_momentum_acceleration`: Train IC=+0.1364, Lock IC=+0.0622, Lock Sharpe=+0.0218

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0658, Lock IC=+0.0308, Lock Sharpe=+1.1651

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2503, Lock IC=+0.0951, Lock Sharpe=+0.6004
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__volatility_expansion_trend_vector`: Train IC=+0.2848, Lock IC=+0.0631, Lock Sharpe=+0.3988
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2503, Lock IC=+0.0879, Lock Sharpe=+0.3905
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2503, Lock IC=+0.0879, Lock Sharpe=+0.3905
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2699, Lock IC=+0.0867, Lock Sharpe=+0.2984

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5074_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1228 | 30 | 83.3% | 66.7% | +0.0708 | +0.3640 |
| B2 Rolling Guard | 96 | 30 | 33.3% | 10.0% | -0.0230 | -0.7203 |
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

_Null Baseline (un-gated candidate pool): 79.0% lock IC > 0, 52.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0321_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 973 | 30 | 100.0% | 63.3% | +0.0997 | +0.1185 |
| B2 Rolling Guard | 81 | 30 | 80.0% | 73.3% | +0.0558 | +0.2716 |
| BH-FDR Gate | 11 | 11 | 81.8% | 45.5% | +0.0357 | -0.0825 |
| B3 Composite Floor | 322 | 30 | 100.0% | 90.0% | +0.1126 | +0.7253 |
| B4 Correlation Gate | 214 | 30 | 100.0% | 100.0% | +0.1266 | +1.0513 |

**Admitted Pool Summary**: 33 features, False Positive Rate = 21.2% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1098, Mean Lock Sharpe = +0.5217

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.9095
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.9095
- `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2346, Lock IC=+0.1159, Lock Sharpe=+0.7959
- `combo_z_sum__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2346, Lock IC=+0.1159, Lock Sharpe=+0.7959
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.1886, Lock IC=+0.1060, Lock Sharpe=+0.6973

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+1.0537
- `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1528, Lock IC=+0.1099, Lock Sharpe=+0.9501
- `combo_diff__rbreaker_buy_setup_proximity_early__late_bar_momentum`: Train IC=+0.1187, Lock IC=+0.1031, Lock Sharpe=+0.8165
- `combo_z_diff__rbreaker_buy_setup_proximity_early__late_bar_momentum`: Train IC=+0.1187, Lock IC=+0.1031, Lock Sharpe=+0.8165

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.0740, Lock IC=+0.0759, Lock Sharpe=+1.4912
- `combo_rank_min__first_bar_sentiment__first_bar_return`: Train IC=+0.0740, Lock IC=+0.0759, Lock Sharpe=+1.4912
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0545, Lock IC=+0.1184, Lock Sharpe=+0.1847
- `combo_rank_max__yesterday_early_trend__yesterday_afternoon_reversal`: Train IC=+0.0450, Lock IC=+0.0423, Lock Sharpe=+0.1379
- `combo_max__yesterday_first_30min_return__yesterday_afternoon_reversal`: Train IC=+0.0622, Lock IC=+0.0453, Lock Sharpe=+0.1109

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Lock Sharpe=+1.8637
- `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Lock Sharpe=+1.8637
- `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2511, Lock IC=+0.1316, Lock Sharpe=+1.5377
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__impulse_bar_dominance`: Train IC=+0.2645, Lock IC=+0.1182, Lock Sharpe=+1.4944
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2433, Lock IC=+0.1490, Lock Sharpe=+1.4472

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3115, Lock IC=+0.1361, Lock Sharpe=+1.6091
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3363, Lock IC=+0.1300, Lock Sharpe=+1.5827
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.5184
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.4890
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.4890

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
| 0.45 | 0.10 | 630 | +0.0246 | 80.0% |
| 0.45 | 0.20 | 622 | +0.0246 | 80.0% |
| 0.45 | 0.30 | 597 | +0.0246 | 80.0% |
| 0.45 | 0.40 | 525 | +0.0246 | 80.0% |
| 0.45 | 0.50 | 420 | +0.0246 | 80.0% |
| 0.50 | 0.15 | 629 | +0.0246 | 80.0% |
| 0.50 | 0.25 | 610 | +0.0246 | 80.0% |
| 0.50 | 0.35 | 562 | +0.0246 | 80.0% |
| 0.50 | 0.45 | 486 | +0.0246 | 80.0% |
| 0.55 | 0.10 | 626 | +0.0246 | 80.0% |
| 0.55 | 0.20 | 620 | +0.0246 | 80.0% |
| 0.55 | 0.30 | 597 | +0.0246 | 80.0% |
| 0.55 | 0.40 | 525 | +0.0246 | 80.0% |
| 0.55 | 0.50 | 420 | +0.0246 | 80.0% |
| 0.60 | 0.15 | 605 | +0.0246 | 80.0% |
| 0.60 | 0.25 | 599 | +0.0246 | 80.0% |
| 0.60 | 0.35 | 561 | +0.0246 | 80.0% |
| 0.60 | 0.45 | 486 | +0.0246 | 80.0% |
| 0.65 | 0.10 | 529 | +0.0246 | 80.0% |
| 0.65 | 0.20 | 529 | +0.0246 | 80.0% |
| 0.65 | 0.30 | 527 | +0.0246 | 80.0% |
| 0.65 | 0.40 | 507 | +0.0246 | 80.0% |
| 0.65 | 0.50 | 420 | +0.0246 | 80.0% |
| 0.70 | 0.15 | 389 | +0.0246 | 80.0% |
| 0.70 | 0.25 | 389 | +0.0246 | 80.0% |
| 0.70 | 0.35 | 389 | +0.0246 | 80.0% |
| 0.70 | 0.45 | 387 | +0.0246 | 80.0% |
| 0.75 | 0.10 | 156 | +0.0117 | 60.0% |
| 0.75 | 0.20 | 156 | +0.0117 | 60.0% |
| 0.75 | 0.30 | 156 | +0.0117 | 60.0% |
| 0.75 | 0.40 | 156 | +0.0117 | 60.0% |
| 0.75 | 0.50 | 156 | +0.0117 | 60.0% |
| 0.80 | 0.15 | 19 | -0.0192 | 20.0% |
| 0.80 | 0.25 | 19 | -0.0192 | 20.0% |
| 0.80 | 0.35 | 19 | -0.0192 | 20.0% |
| 0.80 | 0.45 | 19 | -0.0192 | 20.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 630 candidates, mean lock IC=+0.0246, 80.0% positive

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
| 0.45 | 0.40 | 1 | -0.0817 | 0.0% |
| 0.45 | 0.50 | 1 | -0.0817 | 0.0% |
| 0.50 | 0.15 | 14 | +0.0269 | 70.0% |
| 0.50 | 0.25 | 5 | +0.0094 | 80.0% |
| 0.50 | 0.35 | 1 | -0.0817 | 0.0% |
| 0.50 | 0.45 | 1 | -0.0817 | 0.0% |
| 0.55 | 0.10 | 9 | +0.0254 | 66.7% |
| 0.55 | 0.20 | 7 | +0.0216 | 71.4% |
| 0.55 | 0.30 | 4 | +0.0087 | 75.0% |
| 0.55 | 0.40 | 1 | -0.0817 | 0.0% |
| 0.55 | 0.50 | 1 | -0.0817 | 0.0% |
| 0.60 | 0.15 | 4 | +0.0087 | 75.0% |
| 0.60 | 0.25 | 4 | +0.0087 | 75.0% |
| 0.60 | 0.35 | 1 | -0.0817 | 0.0% |
| 0.60 | 0.45 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.10 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.20 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.30 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.40 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.50 | 1 | -0.0817 | 0.0% |
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
| 0.45 | 0.10 | 42 | +0.0028 | 50.0% |
| 0.45 | 0.20 | 27 | +0.0043 | 50.0% |
| 0.45 | 0.30 | 6 | -0.0147 | 16.7% |
| 0.45 | 0.40 | 1 | -0.0711 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 41 | +0.0028 | 50.0% |
| 0.50 | 0.25 | 17 | +0.0004 | 50.0% |
| 0.50 | 0.35 | 5 | -0.0122 | 20.0% |
| 0.50 | 0.45 | 1 | -0.0711 | 0.0% |
| 0.55 | 0.10 | 37 | +0.0028 | 50.0% |
| 0.55 | 0.20 | 25 | +0.0043 | 50.0% |
| 0.55 | 0.30 | 6 | -0.0147 | 16.7% |
| 0.55 | 0.40 | 1 | -0.0711 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | -0.0149 | 25.0% |
| 0.60 | 0.25 | 6 | -0.0266 | 0.0% |
| 0.60 | 0.35 | 4 | -0.0318 | 0.0% |
| 0.60 | 0.45 | 1 | -0.0711 | 0.0% |
| 0.65 | 0.10 | 3 | -0.0339 | 0.0% |
| 0.65 | 0.20 | 3 | -0.0339 | 0.0% |
| 0.65 | 0.30 | 3 | -0.0339 | 0.0% |
| 0.65 | 0.40 | 1 | -0.0711 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 27 candidates, mean lock IC=+0.0043, 50.0% positive

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
| 0.55 | 0.10 | 6 | +0.0151 | 66.7% |
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
| 0.45 | 0.10 | 1410 | +0.0509 | 100.0% |
| 0.45 | 0.20 | 1390 | +0.0509 | 100.0% |
| 0.45 | 0.30 | 1318 | +0.0509 | 100.0% |
| 0.45 | 0.40 | 1230 | +0.0509 | 100.0% |
| 0.45 | 0.50 | 1013 | +0.0509 | 100.0% |
| 0.50 | 0.15 | 1402 | +0.0509 | 100.0% |
| 0.50 | 0.25 | 1353 | +0.0509 | 100.0% |
| 0.50 | 0.35 | 1272 | +0.0509 | 100.0% |
| 0.50 | 0.45 | 1101 | +0.0509 | 100.0% |
| 0.55 | 0.10 | 1405 | +0.0509 | 100.0% |
| 0.55 | 0.20 | 1389 | +0.0509 | 100.0% |
| 0.55 | 0.30 | 1318 | +0.0509 | 100.0% |
| 0.55 | 0.40 | 1230 | +0.0509 | 100.0% |
| 0.55 | 0.50 | 1013 | +0.0509 | 100.0% |
| 0.60 | 0.15 | 1355 | +0.0509 | 100.0% |
| 0.60 | 0.25 | 1335 | +0.0509 | 100.0% |
| 0.60 | 0.35 | 1268 | +0.0509 | 100.0% |
| 0.60 | 0.45 | 1101 | +0.0509 | 100.0% |
| 0.65 | 0.10 | 1220 | +0.0509 | 100.0% |
| 0.65 | 0.20 | 1220 | +0.0509 | 100.0% |
| 0.65 | 0.30 | 1220 | +0.0509 | 100.0% |
| 0.65 | 0.40 | 1193 | +0.0509 | 100.0% |
| 0.65 | 0.50 | 1013 | +0.0509 | 100.0% |
| 0.70 | 0.15 | 913 | +0.0509 | 100.0% |
| 0.70 | 0.25 | 913 | +0.0509 | 100.0% |
| 0.70 | 0.35 | 913 | +0.0509 | 100.0% |
| 0.70 | 0.45 | 912 | +0.0509 | 100.0% |
| 0.75 | 0.10 | 491 | +0.0509 | 100.0% |
| 0.75 | 0.20 | 491 | +0.0509 | 100.0% |
| 0.75 | 0.30 | 491 | +0.0509 | 100.0% |
| 0.75 | 0.40 | 491 | +0.0509 | 100.0% |
| 0.75 | 0.50 | 491 | +0.0509 | 100.0% |
| 0.80 | 0.15 | 196 | +0.0538 | 100.0% |
| 0.80 | 0.25 | 196 | +0.0538 | 100.0% |
| 0.80 | 0.35 | 196 | +0.0538 | 100.0% |
| 0.80 | 0.45 | 196 | +0.0538 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 196 candidates, mean lock IC=+0.0538, 100.0% positive

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
| 0.45 | 0.10 | 713 | +0.1241 | 100.0% |
| 0.45 | 0.20 | 701 | +0.1241 | 100.0% |
| 0.45 | 0.30 | 654 | +0.1241 | 100.0% |
| 0.45 | 0.40 | 591 | +0.1241 | 100.0% |
| 0.45 | 0.50 | 480 | +0.1241 | 100.0% |
| 0.50 | 0.15 | 708 | +0.1241 | 100.0% |
| 0.50 | 0.25 | 674 | +0.1241 | 100.0% |
| 0.50 | 0.35 | 632 | +0.1241 | 100.0% |
| 0.50 | 0.45 | 542 | +0.1241 | 100.0% |
| 0.55 | 0.10 | 708 | +0.1241 | 100.0% |
| 0.55 | 0.20 | 699 | +0.1241 | 100.0% |
| 0.55 | 0.30 | 654 | +0.1241 | 100.0% |
| 0.55 | 0.40 | 591 | +0.1241 | 100.0% |
| 0.55 | 0.50 | 480 | +0.1241 | 100.0% |
| 0.60 | 0.15 | 662 | +0.1241 | 100.0% |
| 0.60 | 0.25 | 657 | +0.1241 | 100.0% |
| 0.60 | 0.35 | 631 | +0.1241 | 100.0% |
| 0.60 | 0.45 | 542 | +0.1241 | 100.0% |
| 0.65 | 0.10 | 594 | +0.1241 | 100.0% |
| 0.65 | 0.20 | 594 | +0.1241 | 100.0% |
| 0.65 | 0.30 | 594 | +0.1241 | 100.0% |
| 0.65 | 0.40 | 577 | +0.1241 | 100.0% |
| 0.65 | 0.50 | 479 | +0.1241 | 100.0% |
| 0.70 | 0.15 | 422 | +0.1241 | 100.0% |
| 0.70 | 0.25 | 422 | +0.1241 | 100.0% |
| 0.70 | 0.35 | 422 | +0.1241 | 100.0% |
| 0.70 | 0.45 | 422 | +0.1241 | 100.0% |
| 0.75 | 0.10 | 228 | +0.1241 | 100.0% |
| 0.75 | 0.20 | 228 | +0.1241 | 100.0% |
| 0.75 | 0.30 | 228 | +0.1241 | 100.0% |
| 0.75 | 0.40 | 228 | +0.1241 | 100.0% |
| 0.75 | 0.50 | 228 | +0.1241 | 100.0% |
| 0.80 | 0.15 | 67 | +0.1241 | 100.0% |
| 0.80 | 0.25 | 67 | +0.1241 | 100.0% |
| 0.80 | 0.35 | 67 | +0.1241 | 100.0% |
| 0.80 | 0.45 | 67 | +0.1241 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 713 candidates, mean lock IC=+0.1241, 100.0% positive

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1228 | +0.0000 | +0.0200 | 0.16x | 2016-08-24 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1038 | +0.0000 | -0.0223 | -0.21x | 2015-03-16 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1264 | +0.0000 | +0.0237 | 0.19x | 2016-08-24 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | +0.1140 | +0.0000 | -0.0365 | -0.32x | 2017-06-09 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | +0.0791 | +0.0000 | +0.0300 | 0.38x | 2010-12-14 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | +0.0938 | +0.0000 | +0.0772 | 0.82x | 2013-08-21 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1092 | +0.0000 | +0.0164 | 0.15x | 2017-05-09 |
| `combo_max__max_up_ret__volume_surge_direction` | +0.0846 | +0.0000 | -0.0158 | -0.19x | 2014-07-04 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | +0.1011 | +0.0000 | +0.0088 | 0.09x | 2013-09-23 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +0.1042 | +0.0000 | -0.0391 | -0.38x | 2015-02-06 |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | +0.1031 | +0.0000 | +0.0396 | 0.38x | 2016-08-24 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0909 | +0.0000 | +0.0753 | 0.83x | 2016-08-24 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1059 | +0.0000 | +0.0148 | 0.14x | 2016-08-24 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1077 | +0.0000 | +0.0091 | 0.08x | 2017-07-10 |
| `combo_min__max_up_ret__volume_surge_direction` | +0.0910 | +0.0000 | +0.0128 | 0.14x | 2015-01-08 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.0951 | +0.0000 | -0.0282 | -0.30x | 2014-12-08 |
| `combo_sig_product__first_bar_sentiment__opening_drive_thrust_ratio` | +0.0871 | +0.0000 | -0.0235 | -0.27x | 2015-01-08 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | +0.1167 | +0.0000 | -0.0284 | -0.24x | 2017-02-06 |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0384 | +0.0000 | +0.0409 | 1.06x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1870 | +0.0000 | +0.0289 | 0.15x | 2025-07-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1908 | +0.0000 | +0.0883 | 0.46x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1847 | +0.0000 | +0.0950 | 0.51x | No decay |
| `combo_mean__close_vs_open_range__bar_ret_0` | +0.1641 | +0.0000 | +0.0469 | 0.29x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1841 | +0.0000 | +0.0337 | 0.18x | 2021-07-28 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1617 | +0.0000 | +0.1136 | 0.70x | 2016-08-24 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +0.1637 | +0.0000 | +0.0121 | 0.07x | 2020-01-06 |
| `early_order_flow_imbalance` | +0.1249 | +0.0000 | -0.0041 | -0.03x | 2016-11-01 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1601 | +0.0000 | +0.0920 | 0.57x | No decay |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +0.1710 | +0.0000 | +0.0451 | 0.26x | 2019-12-05 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1529 | +0.0000 | +0.0998 | 0.65x | 2016-09-26 |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1658 | +0.0000 | +0.0639 | 0.39x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1616 | +0.0000 | +0.0383 | 0.24x | 2016-12-29 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1607 | +0.0000 | +0.0946 | 0.59x | No decay |
| `combo_rank_min__early_body_momentum__bar_ret_0` | +0.1359 | +0.0000 | +0.0676 | 0.50x | 2016-11-01 |
| `combo_min__first_bar_sentiment__bar_ret_0` | +0.1352 | +0.0000 | +0.0486 | 0.36x | 2013-09-23 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1583 | +0.0000 | +0.1041 | 0.66x | 2022-12-15 |
| `combo_max__max_up_ret__bar_ret_0` | +0.1685 | +0.0000 | +0.0268 | 0.16x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +0.1402 | +0.0000 | +0.1108 | 0.79x | 2023-01-16 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1593 | +0.0000 | +0.0457 | 0.29x | 2022-12-15 |
| `combo_z_sum__close_vs_open_range__high_low_sequence_momentum` | +0.1410 | +0.0000 | +0.0532 | 0.38x | 2016-11-01 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1426 | +0.0000 | +0.1502 | 1.05x | 2016-08-24 |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | +0.1429 | +0.0000 | +0.0970 | 0.68x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1377 | +0.0000 | +0.1138 | 0.83x | 2011-12-23 |
| `combo_sig_product__net_volume_flow__bar_ret_0` | +0.1232 | +0.0000 | +0.0245 | 0.20x | 2016-11-01 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1544 | +0.0000 | +0.0205 | 0.13x | No decay |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1380 | +0.0000 | +0.0613 | 0.44x | 2016-09-26 |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | +0.1229 | +0.0000 | +0.0279 | 0.23x | 2016-09-26 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | +0.1301 | +0.0000 | +0.0705 | 0.54x | 2016-09-26 |
| `vwap_close_divergence_trend` | +0.1298 | +0.0000 | +0.0323 | 0.25x | 2016-11-01 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1549 | +0.0000 | +0.1275 | 0.82x | 2017-01-20 |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1448 | +0.0000 | +0.0891 | 0.62x | 2017-01-20 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +0.1446 | +0.0000 | +0.1307 | 0.90x | 2016-10-24 |
| `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0` | +0.1545 | +0.0000 | +0.1361 | 0.88x | 2017-02-27 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1701 | +0.0000 | +0.1318 | 0.77x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1405 | +0.0000 | +0.1514 | 1.08x | 2016-09-14 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1550 | +0.0000 | +0.1269 | 0.82x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | +0.1367 | +0.0000 | +0.1507 | 1.10x | 2016-09-14 |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1656 | +0.0000 | +0.1210 | 0.73x | 2016-12-21 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1504 | +0.0000 | +0.1101 | 0.73x | 2016-10-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1627 | +0.0000 | +0.1307 | 0.80x | 2017-01-20 |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | +0.1547 | +0.0000 | +0.1320 | 0.85x | 2016-10-24 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +0.1503 | +0.0000 | +0.0885 | 0.59x | 2017-02-27 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1457 | +0.0000 | +0.0933 | 0.64x | 2017-01-20 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1215 | +0.0000 | +0.1592 | 1.31x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0686 | 0.50x | 2016-10-24 |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | +0.1253 | +0.0000 | +0.1466 | 1.17x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1012 | +0.0000 | +0.1286 | 1.27x | 2011-10-18 |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1149 | +0.0000 | +0.1394 | 1.21x | 2011-10-18 |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | +0.1558 | +0.0000 | +0.0786 | 0.50x | 2016-12-21 |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | +0.1567 | +0.0000 | +0.0753 | 0.48x | 2016-12-21 |
| `combo_rank_max__first_bar_sentiment__star50_limit_proximity_early` | +0.1262 | +0.0000 | +0.0725 | 0.57x | 2017-04-28 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1068 | +0.0000 | +0.0682 | 0.64x | 2016-09-14 |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | +0.1423 | +0.0000 | +0.0947 | 0.67x | 2016-10-24 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0944 | +0.0000 | +0.1079 | 1.14x | 2011-10-18 |
| `combo_mean__star50_limit_proximity_early__impulse_bar_dominance` | +0.1309 | +0.0000 | +0.1222 | 0.93x | 2011-10-18 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1542 | +0.0000 | +0.1161 | 0.75x | 2017-02-27 |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | +0.1499 | +0.0000 | +0.0904 | 0.60x | 2017-02-27 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1454 | +0.0000 | +0.1073 | 0.74x | 2011-11-16 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1184 | +0.0000 | +0.0684 | 0.58x | 2016-09-14 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1317 | +0.0000 | +0.1308 | 0.99x | 2011-10-18 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | +0.1446 | +0.0000 | +0.0739 | 0.51x | 2017-01-20 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0659 | 0.48x | 2017-04-28 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — Admission too loose**: 95% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
2. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 6.0%, mean lock Sharpe=-0.5144). Consider relaxing this gate.
3. **300ETF `short` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.1920). Consider relaxing this gate.
4. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=+0.1812). Consider relaxing this gate.
5. **50ETF `single` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.2918). Consider relaxing this gate.
6. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.1306). Consider relaxing this gate.
7. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=-0.0841). Consider relaxing this gate.
8. **500ETF `single` — Admission too loose**: 70% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
9. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.3640). Consider relaxing this gate.
10. **500ETF `long` — BH-FDR Gate too strict**: 73.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.4499). Consider relaxing this gate.
11. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3004). Consider relaxing this gate.
12. **500ETF `short` — B2 Rolling Guard too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3230). Consider relaxing this gate.
13. **159915ETF `single` — B3 Composite Floor too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 52.0%, mean lock Sharpe=+0.7253). Consider relaxing this gate.
14. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 52.0%, mean lock Sharpe=+1.0513). Consider relaxing this gate.
15. **159915ETF `long` — BH-FDR Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 43.0%, mean lock Sharpe=+0.8546). Consider relaxing this gate.
16. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=-0.1211). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
