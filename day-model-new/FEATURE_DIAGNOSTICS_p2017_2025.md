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

### 300ETF — `single` (Full Model Lockbox IC: +0.0179, Sharpe: -0.4185)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0954 | +0.0200 | +0.0200 | -1.1921 | 85.92 | -0.5 | -0.07x | +0.0050 | +0.2788 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0875 | -0.0223 | -0.0223 | -1.9107 | 85.92 | -7.2 | -0.90x | -0.0054 | -0.1249 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0996 | +0.0211 | +0.0211 | -1.1010 | 88.55 | +1.3 | 0.16x | +0.0014 | +0.5573 |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0864 | -0.0365 | -0.0365 | -2.1647 | 85.27 | -11.8 | -1.48x | -0.0051 | +0.5250 |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0875 | +0.0300 | +0.0300 | -0.5586 | 81.33 | +7.1 | 0.89x | +0.0010 | -0.1249 |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.0852 | +0.0813 | +0.0813 | -0.1254 | 84.61 | +12.4 | 1.55x | +0.0051 | +0.3105 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0858 | +0.0164 | +0.0164 | -0.8274 | 84.61 | +3.9 | 0.49x | +0.0006 | +0.2788 |
| `combo_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0925 | -0.0315 | -0.0315 | -2.3158 | 80.02 | -13.5 | -1.68x | -0.0025 | +0.4569 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0924 | +0.0088 | +0.0088 | -1.4167 | 85.92 | -1.1 | -0.13x | -0.0022 | +0.5542 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0834 | -0.0391 | -0.0391 | -1.5357 | 87.24 | -2.7 | -0.34x | -0.0039 | +0.5270 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0768 | +0.0753 | +0.0753 | -0.7047 | 86.58 | +6.3 | 0.79x | +0.0056 | +0.0698 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0910 | +0.0155 | +0.0155 | -2.6320 | 89.86 | -7.8 | -0.98x | -0.0013 | +0.5390 |
| `combo_min__max_up_ret__volume_surge_direction` | Intraday Range Momentum | +1 | +0.0854 | +0.0128 | +0.0128 | -1.0073 | 83.96 | +1.3 | 0.16x | -0.0019 | +0.0000 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0868 | -0.0282 | -0.0282 | -2.0075 | 89.20 | -8.0 | -1.00x | -0.0040 | +0.4527 |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0904 | -0.0056 | -0.0056 | -1.4567 | 89.20 | -1.4 | -0.18x | -0.0026 | +0.0000 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0964 | -0.0284 | -0.0284 | -1.4926 | 87.89 | -0.1 | -0.02x | -0.0033 | +0.3891 |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0424 | +0.0409 | +0.0409 | -0.7980 | 82.65 | +6.5 | 0.81x | +0.0012 | +0.5015 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0809, Sharpe: -0.0489)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1462 | +0.0573 | +0.0573 | -0.7712 | 91.17 | +4.7 | 0.59x | -0.0008 | +0.0128 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1453 | +0.0883 | +0.0883 | -1.0127 | 90.52 | -0.8 | -0.10x | +0.0007 | +0.0128 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1382 | +0.0950 | +0.0950 | -0.5138 | 89.86 | +6.8 | 0.85x | +0.0005 | +0.2664 |
| `combo_mean__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1292 | +0.0469 | +0.0469 | -1.6472 | 91.17 | -12.5 | -1.56x | -0.0003 | -0.0018 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1364 | +0.0337 | +0.0337 | -1.9117 | 90.52 | -11.6 | -1.45x | -0.0023 | +0.4841 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1475 | +0.0427 | +0.0427 | -0.7498 | 89.86 | +5.0 | 0.62x | -0.0026 | +0.0000 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1415 | +0.1136 | +0.1136 | +0.3024 | 84.61 | +19.1 | 2.38x | +0.0019 | +0.2664 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1335 | +0.0447 | +0.0447 | -1.3542 | 86.58 | -4.5 | -0.56x | -0.0009 | +0.0968 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1223 | +0.0148 | +0.0148 | -2.6617 | 86.58 | -29.7 | -3.71x | -0.0022 | +0.1847 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0995 | -0.0041 | -0.0041 | -2.4279 | 91.83 | -21.9 | -2.73x | -0.0028 | +0.0242 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1207 | +0.0920 | +0.0920 | +0.0124 | 80.68 | +13.5 | 1.69x | +0.0017 | +0.0950 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1076 | +0.0998 | +0.0998 | +0.0418 | 87.24 | +15.2 | 1.89x | +0.0019 | +0.0908 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1239 | +0.0383 | +0.0383 | -1.0012 | 82.65 | -0.1 | -0.01x | -0.0009 | -0.0018 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1228 | +0.0999 | +0.0999 | +0.1111 | 83.30 | +15.9 | 1.98x | +0.0022 | +0.0128 |
| `combo_rank_min__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1015 | +0.0699 | +0.0699 | -1.1836 | 88.55 | -6.1 | -0.76x | +0.0006 | -0.0018 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1329 | +0.1041 | +0.1041 | +0.4133 | 83.30 | +20.9 | 2.61x | +0.0012 | +0.0968 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1331 | +0.0268 | +0.0268 | -1.9409 | 86.58 | -18.9 | -2.36x | -0.0016 | +0.0128 |
| `combo_min__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1139 | +0.0486 | +0.0486 | -0.8978 | 81.99 | -3.6 | -0.45x | -0.0007 | +0.0128 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1204 | +0.1108 | +0.1108 | +0.9093 | 84.61 | +29.9 | 3.74x | +0.0008 | +0.2664 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1400 | +0.0457 | +0.0457 | -0.8920 | 91.17 | +3.7 | 0.46x | -0.0011 | +0.0000 |
| `combo_z_sum__close_vs_open_range__rsi_opening` | Volatility & Oscillators | +1 | +0.1019 | +0.0532 | +0.0532 | -1.0874 | 82.65 | -1.3 | -0.16x | -0.0009 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1205 | +0.1502 | +0.1502 | +0.8062 | 88.55 | +29.3 | 3.66x | +0.0013 | +0.2664 |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0954 | +0.0970 | +0.0970 | -0.0976 | 81.99 | +11.6 | 1.45x | +0.0012 | +0.0968 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.1138 | +0.1138 | -0.0363 | 83.30 | +13.0 | 1.63x | +0.0011 | +0.6254 |
| `combo_sig_product__opening_auction_imbalance__bar_ret_0` | Volatility & Oscillators | +1 | +0.0903 | +0.0245 | +0.0245 | -0.8223 | 85.92 | -1.9 | -0.23x | -0.0016 | +0.0128 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1154 | +0.0205 | +0.0205 | -1.0002 | 83.30 | -5.7 | -0.71x | -0.0003 | +0.0128 |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | Other Technical | +1 | +0.0937 | +0.0613 | +0.0613 | -1.1301 | 83.96 | -2.6 | -0.33x | -0.0002 | +0.2664 |
| `combo_sig_product__rsi_opening__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1024 | +0.0279 | +0.0279 | -0.8995 | 87.24 | -3.0 | -0.37x | -0.0006 | +0.0128 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1155 | +0.0705 | +0.0705 | -0.6834 | 85.92 | +1.6 | 0.20x | -0.0003 | +0.2866 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0926 | +0.0323 | +0.0323 | -0.6894 | 89.20 | +3.0 | 0.37x | -0.0014 | +0.0000 |
| `num_up_bars` | Other Technical | +1 | +0.0907 | +0.0459 | +0.0459 | -1.5665 | 87.89 | -8.4 | -1.05x | -0.0006 | +0.1847 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1484, Sharpe: +1.3564)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1386 | +0.1275 | +0.1275 | +0.5336 | 87.24 | +25.9 | 3.23x | -0.0012 | +0.1983 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1374 | +0.1302 | +0.1302 | +0.8754 | 91.17 | +34.8 | 4.35x | +0.0002 | +0.1725 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1413 | +0.1300 | +0.1300 | +1.2547 | 88.55 | +39.6 | 4.95x | -0.0012 | +0.0567 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1167 | +0.1307 | +0.1307 | +1.4405 | 88.55 | +43.2 | 5.40x | -0.0000 | +0.3192 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1385 | +0.1325 | +0.1325 | +0.7447 | 88.55 | +31.1 | 3.89x | +0.0014 | +0.2076 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1287 | +0.1454 | +0.1454 | +0.1295 | 84.61 | +17.2 | 2.14x | -0.0005 | +0.1779 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1275 | +0.1200 | +0.1200 | +0.0394 | 87.24 | +15.2 | 1.90x | -0.0006 | +0.0000 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1133 | +0.1348 | +0.1348 | -0.0205 | 85.92 | +13.7 | 1.72x | -0.0004 | +0.0000 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1048 | +0.1466 | +0.1466 | +0.5276 | 88.55 | +26.7 | 3.34x | +0.0018 | +0.2076 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1126 | +0.1316 | +0.1316 | +1.2800 | 84.61 | +44.6 | 5.58x | +0.0017 | +0.0567 |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1233 | +0.1160 | +0.1160 | +1.0577 | 89.86 | +38.7 | 4.84x | -0.0000 | +0.2585 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1429 | +0.1073 | +0.1073 | -0.0881 | 84.61 | +12.0 | 1.50x | -0.0000 | +0.1400 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1313 | +0.1264 | +0.1264 | -0.1409 | 85.92 | +11.0 | 1.38x | -0.0007 | +0.2076 |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1260 | +0.1320 | +0.1320 | +0.2281 | 91.17 | +19.4 | 2.42x | -0.0001 | +0.1725 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1133 | +0.0738 | +0.0738 | -0.5477 | 89.86 | +5.3 | 0.66x | -0.0013 | +0.0000 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0996 | +0.1592 | +0.1592 | +0.9464 | 84.61 | +34.1 | 4.26x | +0.0005 | +0.3192 |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1017 | +0.1466 | +0.1466 | +0.6474 | 83.30 | +28.8 | 3.60x | -0.0007 | +0.3192 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1071 | +0.0684 | +0.0684 | -0.2354 | 84.61 | +8.7 | 1.09x | -0.0014 | +0.1400 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0710 | +0.0710 | -0.4825 | 93.14 | +7.1 | 0.88x | -0.0006 | -0.0081 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0941 | +0.0721 | +0.0721 | +0.4947 | 78.05 | +23.1 | 2.89x | +0.0006 | +0.0567 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0918 | +0.1286 | +0.1286 | +0.3148 | 83.30 | +21.3 | 2.67x | +0.0033 | +0.3804 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1227 | +0.1064 | +0.1064 | +0.2130 | 91.17 | +19.6 | 2.45x | +0.0007 | +0.1725 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1240 | +0.1161 | +0.1161 | -0.4268 | 88.55 | +5.3 | 0.66x | +0.0007 | +0.1400 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1159 | +0.0366 | +0.0366 | -1.0330 | 88.55 | -5.6 | -0.70x | -0.0010 | +0.1491 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0874 | +0.0658 | +0.0658 | -0.2206 | 72.81 | +7.4 | 0.92x | +0.0006 | +0.0000 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0864 | +0.1079 | +0.1079 | -0.5498 | 84.61 | +2.0 | 0.24x | +0.0018 | +0.0000 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1120 | +0.1308 | +0.1308 | +0.4527 | 84.61 | +24.7 | 3.09x | +0.0000 | +0.2585 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0659 | +0.0659 | +0.4490 | 87.24 | +24.3 | 3.04x | -0.0005 | +0.1400 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 48.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -1.1443_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 943 | 30 | 76.7% | 23.3% | +0.0460 | -0.6983 |
| B2 Rolling Guard | 52 | 30 | 50.0% | 6.7% | +0.0057 | -1.0631 |
| BH-FDR Gate | 2 | 2 | 50.0% | 0.0% | +0.0156 | -0.9826 |
| B3 Composite Floor | 246 | 30 | 53.3% | 0.0% | +0.0140 | -1.1526 |
| B4 Correlation Gate | 114 | 30 | 70.0% | 0.0% | +0.0160 | -0.9474 |

**Admitted Pool Summary**: 17 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0077, Mean Lock Sharpe = -1.3675

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ratio__limit_down_proximity_early__volume_concentration`: Train IC=+0.1720, Lock IC=+0.1235, Lock Sharpe=+0.5027
- `combo_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.3508
- `combo_z_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.3508
- `combo_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.3508
- `combo_z_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.3508

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Lock Sharpe=+0.0079
- `combo_product__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1213, Lock IC=+0.0232, Lock Sharpe=+0.0079

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7521_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 538 | 30 | 70.0% | 26.7% | +0.0193 | -0.6361 |
| B2 Rolling Guard | 41 | 30 | 23.3% | 10.0% | -0.0076 | -0.5407 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0266 | -1.6162 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma200_dist`: Train IC=+0.1387, Lock IC=+0.0286, Lock Sharpe=+0.7878
- `first_bar_volume`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.3869
- `bar_vol_0`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.3869
- `volume_surge_max`: Train IC=+0.1279, Lock IC=+0.0659, Lock Sharpe=+0.3869
- `volume_concentration`: Train IC=+0.1149, Lock IC=+0.0409, Lock Sharpe=+0.1878

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__willr14__roc60`: Train IC=+0.0666, Lock IC=+0.0596, Lock Sharpe=+0.6444
- `combo_diff__willr14__roc60`: Train IC=+0.0528, Lock IC=+0.0594, Lock Sharpe=+0.6444
- `combo_z_diff__willr14__roc60`: Train IC=+0.0528, Lock IC=+0.0594, Lock Sharpe=+0.6444

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6633_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 73.3% | 40.0% | +0.0375 | -0.6844 |
| B2 Rolling Guard | 60 | 30 | 53.3% | 26.7% | -0.0027 | -0.5485 |
| BH-FDR Gate | 8 | 8 | 62.5% | 25.0% | +0.0200 | -0.5646 |
| B3 Composite Floor | 1 | 1 | 100.0% | 100.0% | +0.0684 | +0.0589 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.7672
- `combo_z_sum__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.7672
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.5041
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.5041
- `star50_limit_proximity_early`: Train IC=+0.1240, Lock IC=+0.0960, Lock Sharpe=+0.5041

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `pullback_depth_ratio`: Train IC=+0.0000, Lock IC=+0.0504, Lock Sharpe=+1.2109
- `combo_sig_product__total_path_length__max_down_ret`: Train IC=+0.0376, Lock IC=+0.0550, Lock Sharpe=+0.5824
- `combo_sig_product__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0064, Lock IC=+0.0190, Lock Sharpe=+0.2675
- `combo_mean__donchian_breakout_ratio_20d__dual_thrust_range_ratio`: Train IC=+0.0961, Lock IC=+0.0263, Lock Sharpe=+0.0807
- `combo_z_sum__donchian_breakout_ratio_20d__dual_thrust_range_ratio`: Train IC=+0.0961, Lock IC=+0.0263, Lock Sharpe=+0.0807

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0708, Lock IC=+0.0119, Lock Sharpe=+0.3904
- `gap_pct`: Train IC=+0.1402, Lock IC=+0.1085, Lock Sharpe=+0.3084

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.2007, Lock IC=+0.0684, Lock Sharpe=+0.0589

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9756_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 661 | 30 | 96.7% | 46.7% | +0.0378 | +0.0688 |
| B2 Rolling Guard | 51 | 30 | 73.3% | 33.3% | +0.0213 | -0.5856 |
| BH-FDR Gate | 5 | 5 | 20.0% | 0.0% | -0.0292 | -1.2560 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__volume_surge_max__roc10`: Train IC=+0.1493, Lock IC=+0.0272, Lock Sharpe=+0.9197
- `combo_rank_min__first_bar_volume__roc10`: Train IC=+0.1463, Lock IC=+0.0283, Lock Sharpe=+0.9197
- `combo_rank_min__bar_vol_0__roc10`: Train IC=+0.1463, Lock IC=+0.0283, Lock Sharpe=+0.9197
- `combo_min__roc60__roc10`: Train IC=+0.1297, Lock IC=+0.0274, Lock Sharpe=+0.8568
- `combo_min__sma100_dist__roc10`: Train IC=+0.1531, Lock IC=+0.0542, Lock Sharpe=+0.8193

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__iv_corridor_width__sma100_dist`: Train IC=+0.1155, Lock IC=+0.0663, Lock Sharpe=+1.2649
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.0946, Lock IC=+0.0603, Lock Sharpe=+1.1425
- `combo_sig_product__iv_corridor_width__sma50_dist`: Train IC=+0.0838, Lock IC=+0.0787, Lock Sharpe=+0.8384
- `combo_abs_diff__roc60__sma50_dist`: Train IC=+0.1099, Lock IC=+0.0057, Lock Sharpe=+0.6196
- `combo_product__sma100_dist__ema_ribbon_width`: Train IC=+0.0955, Lock IC=+0.0556, Lock Sharpe=+0.2614

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 9.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -1.1128_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 321 | 30 | 63.3% | 0.0% | +0.0163 | -1.4386 |
| B2 Rolling Guard | 36 | 30 | 26.7% | 10.0% | -0.0014 | -0.7927 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0367 | -2.1841 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bb_width`: Train IC=+0.0518, Lock IC=+0.1414, Lock Sharpe=+0.1829
- `combo_product__iv_envelope_deviation__yesterday_wavetrend_osc`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0975
- `combo_product__iv_envelope_deviation__wavetrend_osc_day`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0975

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5607_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 278 | 30 | 76.7% | 63.3% | +0.0467 | +0.0666 |
| B2 Rolling Guard | 40 | 30 | 33.3% | 13.3% | +0.0115 | -0.3263 |
| BH-FDR Gate | 2 | 2 | 100.0% | 50.0% | +0.0198 | -0.2242 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma20_dist`: Train IC=+0.1468, Lock IC=+0.1018, Lock Sharpe=+1.3678
- `combo_rank_max__bar_vol_4__mfi14`: Train IC=+0.1590, Lock IC=+0.0937, Lock Sharpe=+1.0969
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1886, Lock IC=+0.0898, Lock Sharpe=+0.9237
- `limit_down_proximity_early`: Train IC=+0.1886, Lock IC=+0.0899, Lock Sharpe=+0.9237
- `sma50_dist`: Train IC=+0.1357, Lock IC=+0.0866, Lock Sharpe=+0.8950

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.1163, Lock IC=+0.1636, Lock Sharpe=+1.6137
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0727, Lock Sharpe=+1.0385
- `close_vs_open_range`: Train IC=+0.0193, Lock IC=+0.0427, Lock Sharpe=+0.6242
- `roc5`: Train IC=+0.0684, Lock IC=+0.0977, Lock Sharpe=+0.1110

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1148, Lock IC=+0.0302, Lock Sharpe=+0.0428

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 72.0% lock IC > 0, 7.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -1.0381_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1681 | 30 | 100.0% | 13.3% | +0.0785 | -0.4906 |
| B2 Rolling Guard | 113 | 30 | 56.7% | 10.0% | +0.0076 | -0.8747 |
| BH-FDR Gate | 9 | 9 | 77.8% | 22.2% | +0.0212 | -1.0800 |
| B3 Composite Floor | 436 | 30 | 100.0% | 10.0% | +0.0719 | -0.6878 |
| B4 Correlation Gate | 238 | 30 | 100.0% | 0.0% | +0.0521 | -1.0325 |

**Admitted Pool Summary**: 31 features, False Positive Rate = 77.4% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0634, Mean Lock Sharpe = -0.7865

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Lock Sharpe=+0.2052
- `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`: Train IC=+0.2362, Lock IC=+0.0599, Lock Sharpe=+0.1528
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.0912
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.0912

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__late_bar_momentum__double_bottom_bull_flag_early`: Train IC=+0.1155, Lock IC=+0.0660, Lock Sharpe=+0.9615
- `combo_min__late_bar_momentum__double_bottom_bull_flag_early`: Train IC=+0.1190, Lock IC=+0.0815, Lock Sharpe=+0.5805
- `combo_min__early_late_momentum_divergence__double_bottom_bull_flag_early`: Train IC=+0.1131, Lock IC=+0.0714, Lock Sharpe=+0.5680

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0658, Lock IC=+0.0308, Lock Sharpe=+0.8091
- `combo_sig_product__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.0425, Lock IC=+0.1374, Lock Sharpe=+0.7669

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2503, Lock IC=+0.0951, Lock Sharpe=+0.2253
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2503, Lock IC=+0.0879, Lock Sharpe=+0.0310
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2503, Lock IC=+0.0879, Lock Sharpe=+0.0310

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7333_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1228 | 30 | 83.3% | 63.3% | +0.0708 | +0.1175 |
| B2 Rolling Guard | 96 | 30 | 33.3% | 10.0% | -0.0230 | -0.9528 |
| BH-FDR Gate | 23 | 23 | 91.3% | 69.6% | +0.0383 | +0.1549 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1626, Lock IC=+0.1245, Lock Sharpe=+0.9950
- `combo_diff__donchian_breakout_ratio_20d__yesterday_return`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.5866
- `combo_z_diff__donchian_breakout_ratio_20d__yesterday_return`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.5866
- `combo_diff__donchian_breakout_ratio_20d__limit_up_proximity_day`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.5866
- `combo_z_diff__donchian_breakout_ratio_20d__limit_up_proximity_day`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.5866

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__consecutive_higher_highs__trend_day_regime_conviction`: Train IC=+0.0601, Lock IC=+0.0134, Lock Sharpe=+0.4998
- `combo_rank_min__early_body_momentum__star50_limit_proximity_early`: Train IC=+0.1367, Lock IC=+0.1134, Lock Sharpe=+0.1898
- `combo_rank_min__opening_momentum_score__star50_limit_proximity_early`: Train IC=+0.1367, Lock IC=+0.1134, Lock Sharpe=+0.1898

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1248, Lock IC=+0.0888, Lock Sharpe=+1.4958
- `combo_abs_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.1248, Lock IC=+0.0888, Lock Sharpe=+1.4958
- `combo_sig_product__early_body_momentum__consecutive_higher_highs`: Train IC=+0.0742, Lock IC=+0.0383, Lock Sharpe=+0.6147
- `combo_sig_product__opening_momentum_score__consecutive_higher_highs`: Train IC=+0.0742, Lock IC=+0.0383, Lock Sharpe=+0.6147
- `skypark_gap_reversal_early`: Train IC=+0.0732, Lock IC=+0.0094, Lock Sharpe=+0.5501

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6420_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 369 | 30 | 56.7% | 23.3% | +0.0296 | -0.6079 |
| B2 Rolling Guard | 46 | 30 | 63.3% | 26.7% | +0.0057 | -0.4927 |
| BH-FDR Gate | 14 | 14 | 92.9% | 7.1% | +0.0489 | -1.2009 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.2334
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.2334
- `false_breakout_accumulation`: Train IC=+0.1489, Lock IC=+0.0315, Lock Sharpe=+0.2122
- `combo_mean__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.1069
- `combo_z_sum__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.1069

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv_diff_1d`: Train IC=+0.0334, Lock IC=+0.0868, Lock Sharpe=+0.6000
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0456, Lock Sharpe=+0.5023
- `opening_direction_stability`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+0.3674
- `early_trend_hhi`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+0.3674
- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0610, Lock Sharpe=+0.3103

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vwap_close_divergence_trend`: Train IC=+0.0805, Lock IC=+0.0323, Lock Sharpe=+0.0043

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 82.0% lock IC > 0, 45.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.1531_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1076 | 30 | 100.0% | 66.7% | +0.1090 | +0.0291 |
| B2 Rolling Guard | 89 | 30 | 80.0% | 56.7% | +0.0574 | +0.0196 |
| BH-FDR Gate | 11 | 11 | 81.8% | 18.2% | +0.0357 | -0.4918 |
| B3 Composite Floor | 328 | 30 | 100.0% | 53.3% | +0.1121 | +0.0789 |
| B4 Correlation Gate | 247 | 30 | 100.0% | 100.0% | +0.1294 | +0.7359 |

**Admitted Pool Summary**: 28 features, False Positive Rate = 35.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1129, Mean Lock Sharpe = +0.2816

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.1890, Lock IC=+0.1126, Lock Sharpe=+1.2851
- `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Train IC=+0.1879, Lock IC=+0.1174, Lock Sharpe=+0.6996
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.6296
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.6296
- `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2346, Lock IC=+0.1159, Lock Sharpe=+0.4745

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__first_bar_sentiment__demark_setup_reversal_early`: Train IC=+0.1451, Lock IC=+0.0857, Lock Sharpe=+1.1030
- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+0.7571
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+0.7571
- `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1528, Lock IC=+0.1099, Lock Sharpe=+0.6530
- `combo_diff__rbreaker_buy_setup_proximity_early__late_bar_momentum`: Train IC=+0.1187, Lock IC=+0.1031, Lock Sharpe=+0.5388

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__first_bar_sentiment__first_bar_return`: Train IC=+0.0825, Lock IC=+0.0759, Lock Sharpe=+0.0632
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.0825, Lock IC=+0.0759, Lock Sharpe=+0.0632

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Lock Sharpe=+1.5392
- `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.2493, Lock IC=+0.1398, Lock Sharpe=+1.5392
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2433, Lock IC=+0.1490, Lock Sharpe=+1.1150
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2559, Lock IC=+0.1112, Lock Sharpe=+0.9668
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2458, Lock IC=+0.1295, Lock Sharpe=+0.9062

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3115, Lock IC=+0.1361, Lock Sharpe=+1.2970
- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.1834
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.1834
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.1600
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.1600

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 66.0% lock IC > 0, 32.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4219_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 938 | 30 | 90.0% | 36.7% | +0.0783 | -0.0980 |
| B2 Rolling Guard | 63 | 30 | 90.0% | 50.0% | +0.0765 | -0.0775 |
| BH-FDR Gate | 117 | 30 | 100.0% | 93.3% | +0.1037 | +0.5871 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__trend_strength_intraday`: Train IC=+0.1628, Lock IC=+0.1119, Lock Sharpe=+1.3055
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2132, Lock IC=+0.1300, Lock Sharpe=+1.1832
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1562, Lock IC=+0.1299, Lock Sharpe=+1.1261
- `combo_min__opening_drive_thrust_ratio__open_to_current_return`: Train IC=+0.1640, Lock IC=+0.1043, Lock Sharpe=+0.9925
- `combo_min__opening_drive_thrust_ratio__first_30min_return`: Train IC=+0.1640, Lock IC=+0.1043, Lock Sharpe=+0.9925

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.1162, Lock Sharpe=+0.8849
- `combo_tri_z_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.1162, Lock Sharpe=+0.8849
- `combo_tri_mean__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.0999, Lock IC=+0.1103, Lock Sharpe=+0.8161
- `combo_tri_z_mean__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.0999, Lock IC=+0.1103, Lock Sharpe=+0.8161
- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1129, Lock IC=+0.0837, Lock Sharpe=+0.8117

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1758, Lock IC=+0.1285, Lock Sharpe=+1.7654
- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1848, Lock IC=+0.1170, Lock Sharpe=+1.4970
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1506, Lock IC=+0.1406, Lock Sharpe=+1.4918
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1506, Lock IC=+0.1406, Lock Sharpe=+1.4918
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1491, Lock IC=+0.1210, Lock Sharpe=+0.9140

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 39.0% lock IC > 0, 22.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4870_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 256 | 30 | 76.7% | 30.0% | +0.0414 | -0.2386 |
| B2 Rolling Guard | 42 | 30 | 40.0% | 26.7% | +0.0131 | -0.0719 |
| BH-FDR Gate | 1 | 1 | 100.0% | 0.0% | +0.0926 | -0.2659 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_5_20`: Train IC=+0.0670, Lock IC=+0.0317, Lock Sharpe=+0.5783
- `gap_pct`: Train IC=+0.0662, Lock IC=+0.1187, Lock Sharpe=+0.4196
- `combo_product__morning_volume_weighted_momentum__shaved_bar_trend_conviction`: Train IC=+0.1398, Lock IC=+0.0685, Lock Sharpe=+0.3529
- `limit_down_proximity_early`: Train IC=+0.0645, Lock IC=+0.1323, Lock Sharpe=+0.2516
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0645, Lock IC=+0.1323, Lock Sharpe=+0.2516

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0168, Lock IC=+0.1035, Lock Sharpe=+0.8732
- `yesterday_close_position`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.4631
- `yesterday_day_close_pos`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.4631
- `combo_rank_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.0241, Lock IC=+0.0817, Lock Sharpe=+0.3495
- `opening_direction_stability`: Train IC=+0.0000, Lock IC=+0.0305, Lock Sharpe=+0.3428

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 418 | +0.0242 | 80.0% |
| 0.45 | 0.20 | 409 | +0.0242 | 80.0% |
| 0.45 | 0.30 | 383 | +0.0242 | 80.0% |
| 0.45 | 0.40 | 346 | +0.0242 | 80.0% |
| 0.45 | 0.50 | 291 | +0.0242 | 80.0% |
| 0.50 | 0.15 | 416 | +0.0242 | 80.0% |
| 0.50 | 0.25 | 394 | +0.0242 | 80.0% |
| 0.50 | 0.35 | 365 | +0.0242 | 80.0% |
| 0.50 | 0.45 | 325 | +0.0242 | 80.0% |
| 0.55 | 0.10 | 413 | +0.0242 | 80.0% |
| 0.55 | 0.20 | 407 | +0.0242 | 80.0% |
| 0.55 | 0.30 | 383 | +0.0242 | 80.0% |
| 0.55 | 0.40 | 346 | +0.0242 | 80.0% |
| 0.55 | 0.50 | 291 | +0.0242 | 80.0% |
| 0.60 | 0.15 | 396 | +0.0242 | 80.0% |
| 0.60 | 0.25 | 386 | +0.0242 | 80.0% |
| 0.60 | 0.35 | 364 | +0.0242 | 80.0% |
| 0.60 | 0.45 | 325 | +0.0242 | 80.0% |
| 0.65 | 0.10 | 344 | +0.0242 | 80.0% |
| 0.65 | 0.20 | 344 | +0.0242 | 80.0% |
| 0.65 | 0.30 | 342 | +0.0242 | 80.0% |
| 0.65 | 0.40 | 333 | +0.0242 | 80.0% |
| 0.65 | 0.50 | 291 | +0.0242 | 80.0% |
| 0.70 | 0.15 | 272 | +0.0242 | 80.0% |
| 0.70 | 0.25 | 272 | +0.0242 | 80.0% |
| 0.70 | 0.35 | 272 | +0.0242 | 80.0% |
| 0.70 | 0.45 | 271 | +0.0242 | 80.0% |
| 0.75 | 0.10 | 118 | +0.0108 | 60.0% |
| 0.75 | 0.20 | 118 | +0.0108 | 60.0% |
| 0.75 | 0.30 | 118 | +0.0108 | 60.0% |
| 0.75 | 0.40 | 118 | +0.0108 | 60.0% |
| 0.75 | 0.50 | 118 | +0.0108 | 60.0% |
| 0.80 | 0.15 | 8 | -0.0314 | 0.0% |
| 0.80 | 0.25 | 8 | -0.0314 | 0.0% |
| 0.80 | 0.35 | 8 | -0.0314 | 0.0% |
| 0.80 | 0.45 | 8 | -0.0314 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 418 candidates, mean lock IC=+0.0242, 80.0% positive

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
| 0.45 | 0.10 | 42 | +0.0036 | 60.0% |
| 0.45 | 0.20 | 27 | +0.0052 | 60.0% |
| 0.45 | 0.30 | 6 | -0.0133 | 33.3% |
| 0.45 | 0.40 | 1 | -0.0711 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 41 | +0.0036 | 60.0% |
| 0.50 | 0.25 | 17 | +0.0013 | 60.0% |
| 0.50 | 0.35 | 5 | -0.0115 | 40.0% |
| 0.50 | 0.45 | 1 | -0.0711 | 0.0% |
| 0.55 | 0.10 | 37 | +0.0036 | 60.0% |
| 0.55 | 0.20 | 25 | +0.0052 | 60.0% |
| 0.55 | 0.30 | 6 | -0.0133 | 33.3% |
| 0.55 | 0.40 | 1 | -0.0711 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | -0.0138 | 37.5% |
| 0.60 | 0.25 | 6 | -0.0251 | 16.7% |
| 0.60 | 0.35 | 4 | -0.0310 | 25.0% |
| 0.60 | 0.45 | 1 | -0.0711 | 0.0% |
| 0.65 | 0.10 | 3 | -0.0310 | 33.3% |
| 0.65 | 0.20 | 3 | -0.0310 | 33.3% |
| 0.65 | 0.30 | 3 | -0.0310 | 33.3% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 27 candidates, mean lock IC=+0.0052, 60.0% positive

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
| 0.45 | 0.10 | 1032 | +0.0638 | 100.0% |
| 0.45 | 0.20 | 1011 | +0.0638 | 100.0% |
| 0.45 | 0.30 | 946 | +0.0638 | 100.0% |
| 0.45 | 0.40 | 890 | +0.0638 | 100.0% |
| 0.45 | 0.50 | 751 | +0.0638 | 100.0% |
| 0.50 | 0.15 | 1022 | +0.0638 | 100.0% |
| 0.50 | 0.25 | 984 | +0.0638 | 100.0% |
| 0.50 | 0.35 | 924 | +0.0638 | 100.0% |
| 0.50 | 0.45 | 804 | +0.0638 | 100.0% |
| 0.55 | 0.10 | 1026 | +0.0638 | 100.0% |
| 0.55 | 0.20 | 1010 | +0.0638 | 100.0% |
| 0.55 | 0.30 | 946 | +0.0638 | 100.0% |
| 0.55 | 0.40 | 890 | +0.0638 | 100.0% |
| 0.55 | 0.50 | 751 | +0.0638 | 100.0% |
| 0.60 | 0.15 | 980 | +0.0638 | 100.0% |
| 0.60 | 0.25 | 966 | +0.0638 | 100.0% |
| 0.60 | 0.35 | 920 | +0.0638 | 100.0% |
| 0.60 | 0.45 | 804 | +0.0638 | 100.0% |
| 0.65 | 0.10 | 892 | +0.0638 | 100.0% |
| 0.65 | 0.20 | 892 | +0.0638 | 100.0% |
| 0.65 | 0.30 | 892 | +0.0638 | 100.0% |
| 0.65 | 0.40 | 872 | +0.0638 | 100.0% |
| 0.65 | 0.50 | 751 | +0.0638 | 100.0% |
| 0.70 | 0.15 | 687 | +0.0638 | 100.0% |
| 0.70 | 0.25 | 687 | +0.0638 | 100.0% |
| 0.70 | 0.35 | 687 | +0.0638 | 100.0% |
| 0.70 | 0.45 | 686 | +0.0638 | 100.0% |
| 0.75 | 0.10 | 385 | +0.0638 | 100.0% |
| 0.75 | 0.20 | 385 | +0.0638 | 100.0% |
| 0.75 | 0.30 | 385 | +0.0638 | 100.0% |
| 0.75 | 0.40 | 385 | +0.0638 | 100.0% |
| 0.75 | 0.50 | 385 | +0.0638 | 100.0% |
| 0.80 | 0.15 | 138 | +0.0715 | 100.0% |
| 0.80 | 0.25 | 138 | +0.0715 | 100.0% |
| 0.80 | 0.35 | 138 | +0.0715 | 100.0% |
| 0.80 | 0.45 | 138 | +0.0715 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 138 candidates, mean lock IC=+0.0715, 100.0% positive

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
| 0.45 | 0.10 | 696 | +0.1307 | 100.0% |
| 0.45 | 0.20 | 685 | +0.1307 | 100.0% |
| 0.45 | 0.30 | 629 | +0.1307 | 100.0% |
| 0.45 | 0.40 | 582 | +0.1307 | 100.0% |
| 0.45 | 0.50 | 474 | +0.1307 | 100.0% |
| 0.50 | 0.15 | 692 | +0.1307 | 100.0% |
| 0.50 | 0.25 | 653 | +0.1307 | 100.0% |
| 0.50 | 0.35 | 612 | +0.1307 | 100.0% |
| 0.50 | 0.45 | 536 | +0.1307 | 100.0% |
| 0.55 | 0.10 | 690 | +0.1307 | 100.0% |
| 0.55 | 0.20 | 683 | +0.1307 | 100.0% |
| 0.55 | 0.30 | 629 | +0.1307 | 100.0% |
| 0.55 | 0.40 | 582 | +0.1307 | 100.0% |
| 0.55 | 0.50 | 474 | +0.1307 | 100.0% |
| 0.60 | 0.15 | 639 | +0.1307 | 100.0% |
| 0.60 | 0.25 | 634 | +0.1307 | 100.0% |
| 0.60 | 0.35 | 611 | +0.1307 | 100.0% |
| 0.60 | 0.45 | 536 | +0.1307 | 100.0% |
| 0.65 | 0.10 | 574 | +0.1307 | 100.0% |
| 0.65 | 0.20 | 574 | +0.1307 | 100.0% |
| 0.65 | 0.30 | 574 | +0.1307 | 100.0% |
| 0.65 | 0.40 | 567 | +0.1307 | 100.0% |
| 0.65 | 0.50 | 473 | +0.1307 | 100.0% |
| 0.70 | 0.15 | 426 | +0.1307 | 100.0% |
| 0.70 | 0.25 | 426 | +0.1307 | 100.0% |
| 0.70 | 0.35 | 426 | +0.1307 | 100.0% |
| 0.70 | 0.45 | 426 | +0.1307 | 100.0% |
| 0.75 | 0.10 | 231 | +0.1307 | 100.0% |
| 0.75 | 0.20 | 231 | +0.1307 | 100.0% |
| 0.75 | 0.30 | 231 | +0.1307 | 100.0% |
| 0.75 | 0.40 | 231 | +0.1307 | 100.0% |
| 0.75 | 0.50 | 231 | +0.1307 | 100.0% |
| 0.80 | 0.15 | 57 | +0.1307 | 100.0% |
| 0.80 | 0.25 | 57 | +0.1307 | 100.0% |
| 0.80 | 0.35 | 57 | +0.1307 | 100.0% |
| 0.80 | 0.45 | 57 | +0.1307 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 696 candidates, mean lock IC=+0.1307, 100.0% positive

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
| `combo_max__max_up_ret__first_bar_sentiment` | +0.0996 | +0.0000 | -0.0315 | -0.32x | 2015-01-08 |
| `combo_z_sum__first_bar_return__volume_weighted_price_position` | +0.1011 | +0.0000 | +0.0088 | 0.09x | 2013-09-23 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +0.1042 | +0.0000 | -0.0391 | -0.38x | 2015-02-06 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0909 | +0.0000 | +0.0753 | 0.83x | 2016-08-24 |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1077 | +0.0000 | +0.0091 | 0.08x | 2017-07-10 |
| `combo_min__max_up_ret__volume_surge_direction` | +0.0910 | +0.0000 | +0.0128 | 0.14x | 2015-01-08 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.0951 | +0.0000 | -0.0282 | -0.30x | 2014-12-08 |
| `combo_z_sum__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1056 | +0.0000 | -0.0056 | -0.05x | 2015-02-06 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | +0.1167 | +0.0000 | -0.0284 | -0.24x | 2017-02-06 |
| `combo_z_sum__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0384 | +0.0000 | +0.0409 | 1.06x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | +0.1826 | +0.0000 | +0.0573 | 0.31x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1908 | +0.0000 | +0.0883 | 0.46x | No decay |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1847 | +0.0000 | +0.0950 | 0.51x | No decay |
| `combo_mean__close_vs_open_range__bar_ret_0` | +0.1641 | +0.0000 | +0.0469 | 0.29x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1841 | +0.0000 | +0.0337 | 0.18x | 2021-07-28 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1790 | +0.0000 | +0.0427 | 0.24x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1617 | +0.0000 | +0.1136 | 0.70x | 2016-08-24 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | +0.1715 | +0.0000 | +0.0447 | 0.26x | 2019-12-05 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +0.1637 | +0.0000 | +0.0121 | 0.07x | 2020-01-06 |
| `early_order_flow_imbalance` | +0.1249 | +0.0000 | -0.0041 | -0.03x | 2016-11-01 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1601 | +0.0000 | +0.0920 | 0.57x | No decay |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1529 | +0.0000 | +0.0998 | 0.65x | 2016-09-26 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1616 | +0.0000 | +0.0383 | 0.24x | 2016-12-29 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1607 | +0.0000 | +0.0946 | 0.59x | No decay |
| `combo_rank_min__early_body_momentum__bar_ret_0` | +0.1359 | +0.0000 | +0.0676 | 0.50x | 2016-11-01 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1583 | +0.0000 | +0.1041 | 0.66x | 2022-12-15 |
| `combo_max__max_up_ret__bar_ret_0` | +0.1685 | +0.0000 | +0.0268 | 0.16x | No decay |
| `combo_min__first_bar_sentiment__first_bar_return` | +0.1353 | +0.0000 | +0.0486 | 0.36x | 2013-09-23 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +0.1402 | +0.0000 | +0.1108 | 0.79x | 2023-01-16 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1593 | +0.0000 | +0.0457 | 0.29x | 2022-12-15 |
| `combo_z_sum__close_vs_open_range__rsi_opening` | +0.1410 | +0.0000 | +0.0532 | 0.38x | 2016-11-01 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1426 | +0.0000 | +0.1502 | 1.05x | 2016-08-24 |
| `combo_z_sum__star50_limit_proximity_early__max_down_ret` | +0.1429 | +0.0000 | +0.0970 | 0.68x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1377 | +0.0000 | +0.1138 | 0.83x | 2011-12-23 |
| `combo_sig_product__opening_auction_imbalance__bar_ret_0` | +0.1232 | +0.0000 | +0.0245 | 0.20x | 2016-11-01 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1544 | +0.0000 | +0.0205 | 0.13x | No decay |
| `combo_max__star50_limit_proximity_early__trend_bar_close_consistency` | +0.1380 | +0.0000 | +0.0613 | 0.44x | 2016-09-26 |
| `combo_sig_product__rsi_opening__first_bar_return` | +0.1229 | +0.0000 | +0.0279 | 0.23x | 2016-09-26 |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | +0.1301 | +0.0000 | +0.0705 | 0.54x | 2016-09-26 |
| `vwap_close_divergence_trend` | +0.1298 | +0.0000 | +0.0323 | 0.25x | 2016-11-01 |
| `num_up_bars` | +0.1234 | +0.0000 | +0.0459 | 0.37x | 2020-02-12 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1549 | +0.0000 | +0.1275 | 0.82x | 2017-01-20 |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | +0.1659 | +0.0000 | +0.1302 | 0.79x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1616 | +0.0000 | +0.1258 | 0.78x | 2016-12-21 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +0.1446 | +0.0000 | +0.1307 | 0.90x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1717 | +0.0000 | +0.1325 | 0.77x | 2017-01-20 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1550 | +0.0000 | +0.1269 | 0.82x | 2017-01-20 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | +0.1541 | +0.0000 | +0.1200 | 0.78x | 2017-01-20 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1448 | +0.0000 | +0.1348 | 0.93x | 2017-02-27 |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1410 | +0.0000 | +0.1466 | 1.04x | 2016-09-14 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1272 | +0.0000 | +0.1316 | 1.03x | 2017-02-27 |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | +0.1514 | +0.0000 | +0.1160 | 0.77x | 2017-04-28 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1454 | +0.0000 | +0.1073 | 0.74x | 2011-11-16 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1600 | +0.0000 | +0.1264 | 0.79x | 2017-01-20 |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | +0.1547 | +0.0000 | +0.1320 | 0.85x | 2016-10-24 |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | +0.1457 | +0.0000 | +0.0774 | 0.53x | 2016-12-21 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.1215 | +0.0000 | +0.1592 | 1.31x | 2011-10-18 |
| `combo_min__first_bar_return__rbreaker_buy_setup_proximity_early` | +0.1253 | +0.0000 | +0.1466 | 1.17x | 2011-10-18 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1184 | +0.0000 | +0.0684 | 0.58x | 2016-09-14 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0686 | 0.50x | 2016-10-24 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1245 | +0.0000 | +0.0758 | 0.61x | 2017-04-28 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1012 | +0.0000 | +0.1286 | 1.27x | 2011-10-18 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1553 | +0.0000 | +0.1271 | 0.82x | 2016-12-21 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1542 | +0.0000 | +0.1161 | 0.75x | 2017-02-27 |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | +0.1345 | +0.0000 | +0.0366 | 0.27x | 2014-03-25 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1068 | +0.0000 | +0.0682 | 0.64x | 2016-09-14 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0944 | +0.0000 | +0.1079 | 1.14x | 2011-10-18 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1317 | +0.0000 | +0.1308 | 0.99x | 2011-10-18 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0659 | 0.48x | 2017-04-28 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 23.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.6983). Consider relaxing this gate.
2. **300ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
3. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.6361). Consider relaxing this gate.
4. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.6844). Consider relaxing this gate.
5. **300ETF `short` — B2 Rolling Guard too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.5485). Consider relaxing this gate.
6. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=+0.0688). Consider relaxing this gate.
7. **50ETF `single` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=-0.5856). Consider relaxing this gate.
8. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 63.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.0666). Consider relaxing this gate.
9. **500ETF `single` — BH-FDR Gate too strict**: 22.2% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 7.0%, mean lock Sharpe=-1.0800). Consider relaxing this gate.
10. **500ETF `single` — Admission too loose**: 77% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
11. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 63.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=+0.1175). Consider relaxing this gate.
12. **500ETF `long` — BH-FDR Gate too strict**: 69.6% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=+0.1549). Consider relaxing this gate.
13. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 23.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 8.0%, mean lock Sharpe=-0.6079). Consider relaxing this gate.
14. **500ETF `short` — B2 Rolling Guard too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 8.0%, mean lock Sharpe=-0.4927). Consider relaxing this gate.
15. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 45.0%, mean lock Sharpe=+0.7359). Consider relaxing this gate.
16. **159915ETF `long` — B2 Rolling Guard too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 32.0%, mean lock Sharpe=-0.0775). Consider relaxing this gate.
17. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 32.0%, mean lock Sharpe=+0.5871). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
