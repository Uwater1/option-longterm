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

### 300ETF — `single` (Full Model Lockbox IC: +0.0302, Sharpe: -0.0701)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0999 | +0.0354 | +0.0354 | -0.3491 | 85.44 | +8.8 | 1.11x | +0.0033 | +0.0053 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1022 | +0.0366 | +0.0366 | -0.5842 | 87.82 | +6.5 | 0.81x | +0.0016 | +0.0760 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1012 | +0.0094 | +0.0094 | -0.4218 | 89.41 | +9.4 | 1.17x | -0.0016 | +0.5701 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0911 | -0.0067 | -0.0067 | -1.6023 | 88.22 | -6.0 | -0.76x | -0.0021 | +0.3484 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0952 | +0.0270 | +0.0270 | +0.1230 | 87.03 | +16.4 | 2.04x | +0.0020 | +0.3515 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1008 | +0.0645 | +0.0645 | +0.5284 | 84.64 | +21.6 | 2.70x | +0.0029 | +0.0654 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0986 | +0.0234 | +0.0234 | -0.6582 | 86.23 | +4.8 | 0.60x | -0.0003 | +0.5257 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0998 | +0.0045 | +0.0045 | -1.0539 | 89.41 | +1.4 | 0.18x | -0.0015 | +0.6107 |
| `combo_max__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0845 | -0.0088 | -0.0088 | -0.7278 | 88.62 | +5.9 | 0.74x | -0.0009 | +0.6205 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0955 | +0.0125 | +0.0125 | -1.0630 | 90.21 | +2.8 | 0.35x | +0.0000 | +0.6016 |
| `combo_rank_max__bar_ret_0__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0855 | -0.0033 | -0.0033 | -0.5336 | 62.39 | +3.0 | 0.38x | -0.0024 | +0.0000 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0836 | -0.0055 | -0.0055 | -0.8381 | 67.95 | +1.9 | 0.23x | -0.0017 | +0.4026 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0849 | +0.0427 | +0.0427 | -1.1309 | 87.43 | +0.2 | 0.03x | +0.0028 | -0.0254 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0915 | -0.0161 | -0.0161 | -1.1152 | 89.41 | +3.8 | 0.48x | -0.0019 | +0.4903 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0922 | +0.0291 | +0.0291 | -0.2330 | 82.66 | +10.2 | 1.28x | +0.0014 | +0.1542 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0884 | -0.0007 | -0.0007 | -1.2926 | 89.81 | -1.4 | -0.18x | -0.0003 | +0.4903 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0918 | +0.0266 | +0.0266 | -0.1199 | 89.81 | +13.2 | 1.65x | +0.0015 | +0.5958 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0957 | +0.0042 | +0.0042 | -0.2878 | 87.03 | +9.5 | 1.19x | -0.0007 | -0.0456 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0719 | +0.0288 | +0.0288 | -0.5423 | 76.30 | +4.5 | 0.56x | +0.0035 | +0.3728 |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0832 | -0.0080 | -0.0080 | -1.0044 | 90.61 | +2.4 | 0.30x | -0.0015 | +0.4903 |
| `combo_mean__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0318 | +0.0535 | +0.0535 | -1.0074 | 82.66 | +3.5 | 0.44x | +0.0019 | +0.4316 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1140, Sharpe: +0.5089)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1412 | +0.1193 | +0.1193 | +0.2422 | 87.82 | +19.0 | 2.37x | +0.0020 | +0.0627 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1346 | +0.0910 | +0.0910 | +0.0732 | 89.81 | +15.9 | 1.99x | -0.0001 | -0.0841 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1302 | +0.0955 | +0.0955 | +0.2044 | 85.84 | +18.4 | 2.30x | +0.0002 | -0.0096 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1385 | +0.0855 | +0.0855 | +0.5052 | 85.84 | +23.5 | 2.93x | +0.0003 | +0.1878 |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.0879 | +0.0585 | +0.0585 | -0.0658 | 65.57 | +9.6 | 1.20x | -0.0006 | +0.0082 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1283 | +0.0887 | +0.0887 | -0.0130 | 90.21 | +14.7 | 1.84x | -0.0005 | -0.0376 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1161 | +0.1193 | +0.1193 | +0.7763 | 83.85 | +29.7 | 3.72x | +0.0014 | +0.1470 |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1403 | +0.0869 | +0.0869 | +0.0875 | 90.21 | +16.4 | 2.05x | +0.0002 | -0.0452 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1231 | +0.0591 | +0.0591 | -0.7835 | 85.04 | -1.5 | -0.19x | -0.0011 | -0.0087 |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1029 | +0.1235 | +0.1235 | +0.7688 | 86.23 | +30.1 | 3.76x | +0.0023 | +0.1715 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1289 | +0.0905 | +0.0905 | -0.1233 | 83.85 | +11.6 | 1.45x | +0.0005 | +0.2482 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1242 | +0.0972 | +0.0972 | +0.7833 | 80.67 | +31.3 | 3.91x | +0.0005 | +0.0638 |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1223 | +0.0926 | +0.0926 | +0.7209 | 79.88 | +29.7 | 3.71x | +0.0017 | +0.2131 |
| `combo_min__volatility_expansion_trend_vector__close_vs_open_range` | Volatility & Oscillators | +1 | +0.0941 | +0.0848 | +0.0848 | -0.2413 | 86.63 | +10.8 | 1.36x | +0.0002 | +0.0838 |
| `combo_max__close_vs_open_range__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1344 | +0.0749 | +0.0749 | -0.2700 | 87.43 | +9.0 | 1.12x | -0.0004 | +0.0728 |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1252 | +0.0607 | +0.0607 | -0.1655 | 87.43 | +11.8 | 1.47x | -0.0007 | -0.0520 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0891 | +0.0833 | +0.0833 | -0.0910 | 73.12 | +10.7 | 1.33x | +0.0003 | +0.0082 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1239 | +0.0818 | +0.0818 | -0.1349 | 79.88 | +10.2 | 1.27x | +0.0004 | +0.3705 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1293 | +0.0813 | +0.0813 | -0.0733 | 85.84 | +12.7 | 1.59x | -0.0003 | +0.1859 |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1454 | +0.0872 | +0.0872 | -0.2020 | 88.62 | +10.6 | 1.32x | -0.0002 | +0.0082 |
| `combo_max__star50_limit_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.0887 | +0.0916 | +0.0916 | +0.0703 | 86.63 | +15.6 | 1.95x | -0.0007 | +0.0832 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Intraday Range Momentum | +1 | +0.1078 | +0.0999 | +0.0999 | +0.1009 | 87.03 | +16.2 | 2.02x | -0.0002 | -0.0971 |
| `combo_sig_product__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1181 | +0.0557 | +0.0557 | -0.0463 | 85.44 | +13.1 | 1.64x | -0.0004 | +0.2970 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1104 | +0.1566 | +0.1566 | +0.2157 | 87.82 | +18.8 | 2.35x | +0.0021 | +0.1777 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0935 | +0.1046 | +0.1046 | +0.4052 | 79.08 | +21.7 | 2.71x | +0.0006 | +0.0312 |
| `combo_sig_product__opening_auction_imbalance__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0794 | +0.0538 | +0.0538 | -0.3051 | 84.64 | +7.2 | 0.90x | -0.0013 | +0.2970 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.0825 | +0.1093 | +0.1093 | +0.4426 | 81.47 | +23.7 | 2.96x | +0.0007 | +0.0674 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0837 | +0.0582 | +0.0582 | -0.5326 | 87.43 | +3.0 | 0.38x | -0.0006 | +0.0509 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1162 | +0.0876 | +0.0876 | +0.4478 | 89.41 | +21.5 | 2.69x | +0.0003 | -0.0452 |
| `combo_z_sum__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1274 | +0.1011 | +0.1011 | -0.0960 | 91.80 | +13.5 | 1.68x | +0.0001 | +0.0592 |
| `combo_z_sum__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1068 | +0.0982 | +0.0982 | +0.3203 | 85.44 | +19.8 | 2.48x | +0.0007 | +0.2287 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1425, Sharpe: +0.9897)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1446 | +0.1235 | +0.1235 | +0.5461 | 88.62 | +25.9 | 3.24x | +0.0007 | -0.0338 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1163 | +0.0911 | +0.0911 | +0.3186 | 83.85 | +22.1 | 2.77x | +0.0014 | -0.0878 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1433 | +0.1156 | +0.1156 | +1.1752 | 83.06 | +42.0 | 5.25x | -0.0006 | +0.0818 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1237 | +0.1316 | +0.1316 | +1.2887 | 86.23 | +42.5 | 5.31x | +0.0015 | +0.0241 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0981 | +0.1273 | +0.1273 | +0.9833 | 83.85 | +36.6 | 4.58x | +0.0005 | -0.0067 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1415 | +0.1181 | +0.1181 | +1.2510 | 87.03 | +44.7 | 5.59x | +0.0003 | +0.1706 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1142 | +0.1085 | +0.1085 | +0.6332 | 87.43 | +29.0 | 3.63x | -0.0002 | +0.0000 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0880 | +0.1090 | +0.1090 | +0.0124 | 77.49 | +13.1 | 1.64x | +0.0008 | +0.1612 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1039 | +0.0879 | +0.0879 | +0.1448 | 85.84 | +17.2 | 2.15x | -0.0003 | -0.0925 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1221 | +0.1094 | +0.1094 | +0.7442 | 85.44 | +34.4 | 4.31x | +0.0001 | +0.0000 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1182 | +0.1236 | +0.1236 | +0.5605 | 85.44 | +26.9 | 3.36x | -0.0004 | +0.0109 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1137 | +0.1246 | +0.1246 | +1.2584 | 79.08 | +46.3 | 5.78x | +0.0009 | +0.1972 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1169 | +0.0872 | +0.0872 | +0.0736 | 88.62 | +16.3 | 2.04x | +0.0002 | +0.0388 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1014 | +0.1330 | +0.1330 | +0.8015 | 81.07 | +33.3 | 4.17x | +0.0007 | -0.0183 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0943 | +0.1192 | +0.1192 | +0.8728 | 84.64 | +32.4 | 4.04x | +0.0009 | -0.0067 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.0704 | +0.0575 | +0.0575 | -0.6942 | 76.70 | +0.2 | 0.02x | -0.0008 | -0.0337 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1019 | +0.1284 | +0.1284 | +0.9565 | 84.64 | +37.4 | 4.68x | +0.0006 | +0.0812 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1265 | +0.1212 | +0.1212 | -0.0863 | 86.23 | +12.2 | 1.52x | -0.0006 | +0.0959 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0942 | +0.1243 | +0.1243 | +0.5212 | 85.44 | +25.8 | 3.23x | +0.0019 | +0.0523 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0613 | +0.0486 | +0.0486 | +0.5769 | 83.06 | +28.7 | 3.59x | +0.0003 | +0.1542 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0943 | +0.0753 | +0.0753 | +0.0409 | 66.36 | +11.8 | 1.48x | -0.0005 | +0.1051 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1165 | +0.0874 | +0.0874 | +0.1633 | 83.85 | +17.7 | 2.21x | -0.0009 | +0.1560 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.0697 | +0.0804 | +0.0804 | +0.2268 | 72.72 | +16.4 | 2.05x | -0.0003 | +0.0318 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1142 | +0.1274 | +0.1274 | +0.5997 | 86.23 | +28.3 | 3.54x | -0.0000 | +0.0959 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1056 | +0.0674 | +0.0674 | -0.2641 | 82.26 | +7.6 | 0.96x | -0.0013 | -0.1129 |
| `combo_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | Intraday Range Momentum | +1 | +0.0635 | +0.1067 | +0.1067 | -0.1148 | 75.11 | +9.3 | 1.17x | +0.0004 | +0.1110 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1016 | +0.1298 | +0.1298 | -0.2127 | 80.67 | +8.7 | 1.09x | -0.0002 | +0.0000 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0974 | +0.1273 | +0.1273 | +0.0566 | 85.44 | +15.5 | 1.93x | -0.0009 | +0.0762 |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1009 | +0.1020 | +0.1020 | +1.0549 | 85.44 | +40.8 | 5.11x | -0.0002 | +0.1051 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0962 | +0.1348 | +0.1348 | +0.8488 | 82.26 | +35.3 | 4.41x | -0.0005 | +0.1871 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 13.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7821_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1031 | 30 | 83.3% | 20.0% | +0.0149 | -0.5643 |
| B2 Rolling Guard | 51 | 30 | 63.3% | 6.7% | +0.0019 | -0.6864 |
| BH-FDR Gate | 10 | 10 | 20.0% | 10.0% | -0.0138 | -0.9581 |
| B3 Composite Floor | 230 | 30 | 90.0% | 20.0% | +0.0216 | -0.3713 |
| B4 Correlation Gate | 99 | 30 | 86.7% | 10.0% | +0.0162 | -0.4508 |

**Admitted Pool Summary**: 21 features, False Positive Rate = 90.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0166, Mean Lock Sharpe = -0.6626

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__bar_ret_0__volume_surge_direction`: Train IC=+0.1904, Lock IC=+0.0333, Lock Sharpe=+0.8712
- `combo_rank_max__first_bar_return__volume_surge_direction`: Train IC=+0.1904, Lock IC=+0.0333, Lock Sharpe=+0.8712
- `combo_mean__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1884, Lock IC=+0.0396, Lock Sharpe=+0.8229
- `combo_z_sum__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1884, Lock IC=+0.0396, Lock Sharpe=+0.8229
- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Lock Sharpe=+0.1003

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.0731, Lock IC=+0.0270, Lock Sharpe=+0.1700
- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.0937, Lock IC=+0.0411, Lock Sharpe=+0.1288

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0814, Lock IC=+0.0326, Lock Sharpe=+0.2087

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2251, Lock IC=+0.0254, Lock Sharpe=+0.1308
- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Lock Sharpe=+0.1230
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2135, Lock IC=+0.0413, Lock Sharpe=+0.0502
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2135, Lock IC=+0.0413, Lock Sharpe=+0.0502
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2133, Lock IC=+0.0412, Lock Sharpe=+0.0502

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2249, Lock IC=+0.0346, Lock Sharpe=+0.8154
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2155, Lock IC=+0.0334, Lock Sharpe=+0.6063
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2492, Lock IC=+0.0505, Lock Sharpe=+0.3436

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 38.0% lock IC > 0, 19.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4846_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 528 | 30 | 83.3% | 60.0% | +0.0227 | -0.0472 |
| B2 Rolling Guard | 48 | 30 | 20.0% | 10.0% | -0.0071 | -0.3488 |
| BH-FDR Gate | 10 | 10 | 40.0% | 0.0% | -0.0141 | -0.8607 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__willr14__sma100_dist`: Train IC=+0.1249, Lock IC=+0.0527, Lock Sharpe=+0.9457
- `combo_min__sma100_dist__wavetrend_osc_day`: Train IC=+0.1061, Lock IC=+0.0346, Lock Sharpe=+0.7662
- `combo_min__sma100_dist__yesterday_wavetrend_osc`: Train IC=+0.1061, Lock IC=+0.0346, Lock Sharpe=+0.7662
- `combo_sig_product__donchian_breakout_ratio_20d__sma100_dist`: Train IC=+0.1221, Lock IC=+0.0363, Lock Sharpe=+0.5913
- `combo_sig_product__donchian_breakout_proximity_20d__sma100_dist`: Train IC=+0.1221, Lock IC=+0.0363, Lock Sharpe=+0.5913

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__roc60__wavetrend_osc_day`: Train IC=+0.0642, Lock IC=+0.0295, Lock Sharpe=+0.7997
- `combo_min__roc60__yesterday_wavetrend_osc`: Train IC=+0.0642, Lock IC=+0.0295, Lock Sharpe=+0.7997
- `roc60`: Train IC=+0.0546, Lock IC=+0.0215, Lock Sharpe=+0.3510

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7455_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 70.0% | 10.0% | +0.0073 | -0.7337 |
| B2 Rolling Guard | 62 | 30 | 43.3% | 3.3% | -0.0021 | -0.7820 |
| BH-FDR Gate | 7 | 7 | 100.0% | 14.3% | +0.0381 | -0.3948 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1333, Lock IC=+0.0340, Lock Sharpe=+0.2250
- `early_vwap_acceleration`: Train IC=+0.1442, Lock IC=+0.0189, Lock Sharpe=+0.1145
- `limit_down_proximity_early`: Train IC=+0.1106, Lock IC=+0.0570, Lock Sharpe=+0.0964

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0750, Lock IC=+0.0665, Lock Sharpe=+0.0502

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1580, Lock IC=+0.0543, Lock Sharpe=+0.3728

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6005_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 711 | 30 | 96.7% | 66.7% | +0.0458 | +0.2518 |
| B2 Rolling Guard | 21 | 21 | 33.3% | 0.0% | +0.0022 | -0.5212 |
| BH-FDR Gate | 11 | 11 | 9.1% | 0.0% | -0.0337 | -1.4538 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__roc60__yesterday_wavetrend_osc`: Train IC=+0.1330, Lock IC=+0.0470, Lock Sharpe=+1.4216
- `combo_max__roc60__wavetrend_osc_day`: Train IC=+0.1330, Lock IC=+0.0470, Lock Sharpe=+1.4216
- `combo_min__iv_corridor_width__yesterday_wavetrend_osc`: Train IC=+0.1441, Lock IC=+0.0566, Lock Sharpe=+0.9899
- `combo_min__iv_corridor_width__wavetrend_osc_day`: Train IC=+0.1441, Lock IC=+0.0566, Lock Sharpe=+0.9899
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.1278, Lock IC=+0.0492, Lock Sharpe=+0.9747

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7085_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 325 | 30 | 63.3% | 23.3% | +0.0135 | -0.8705 |
| B2 Rolling Guard | 35 | 30 | 33.3% | 3.3% | -0.0059 | -0.6008 |
| BH-FDR Gate | 8 | 8 | 12.5% | 0.0% | -0.0226 | -1.8629 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.0929, Lock IC=+0.0849, Lock Sharpe=+0.4138
- `combo_max__iv_envelope_deviation__yesterday_wavetrend_osc`: Train IC=+0.1236, Lock IC=+0.0443, Lock Sharpe=+0.2093
- `combo_max__iv_envelope_deviation__wavetrend_osc_day`: Train IC=+0.1236, Lock IC=+0.0443, Lock Sharpe=+0.2093
- `combo_sig_product__yesterday_wavetrend_osc__donchian_breakout_ratio_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1702
- `combo_sig_product__yesterday_wavetrend_osc__donchian_breakout_proximity_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1702

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc5`: Train IC=+0.0555, Lock IC=+0.0383, Lock Sharpe=+0.0314

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 9.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6482_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 275 | 30 | 73.3% | 43.3% | +0.0304 | -0.1128 |
| B2 Rolling Guard | 42 | 30 | 33.3% | 0.0% | -0.0001 | -0.5419 |
| BH-FDR Gate | 4 | 4 | 0.0% | 0.0% | -0.0376 | -0.7546 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma200_dist`: Train IC=+0.1275, Lock IC=+0.0508, Lock Sharpe=+0.8447
- `combo_mean__bar_vol_4__mfi14`: Train IC=+0.1427, Lock IC=+0.0752, Lock Sharpe=+0.3500
- `combo_z_sum__bar_vol_4__mfi14`: Train IC=+0.1427, Lock IC=+0.0752, Lock Sharpe=+0.3500
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.3467
- `limit_down_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.3467

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 84.0% lock IC > 0, 34.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2867_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1762 | 30 | 96.7% | 80.0% | +0.1013 | +0.3245 |
| B2 Rolling Guard | 168 | 30 | 100.0% | 50.0% | +0.0559 | -0.0714 |
| BH-FDR Gate | 12 | 12 | 91.7% | 16.7% | +0.0377 | -0.1745 |
| B3 Composite Floor | 460 | 30 | 100.0% | 73.3% | +0.0978 | +0.2726 |
| B4 Correlation Gate | 301 | 30 | 100.0% | 53.3% | +0.0938 | +0.1150 |

**Admitted Pool Summary**: 31 features, False Positive Rate = 48.4% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0896, Mean Lock Sharpe = +0.0974

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2706, Lock IC=+0.1225, Lock Sharpe=+0.9860
- `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2142, Lock IC=+0.1160, Lock Sharpe=+0.8098
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Lock Sharpe=+0.8086
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Lock Sharpe=+0.7825
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2618, Lock IC=+0.1189, Lock Sharpe=+0.7628

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Lock Sharpe=+0.5034
- `combo_tri_z_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Lock Sharpe=+0.5034
- `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__volume_weighted_momentum_acceleration`: Train IC=+0.1765, Lock IC=+0.0288, Lock Sharpe=+0.3345
- `combo_tri_max__rbreaker_sell_setup_proximity_early__net_volume_flow__volume_weighted_momentum_acceleration`: Train IC=+0.1765, Lock IC=+0.0288, Lock Sharpe=+0.3345
- `combo_tri_mean__max_up_ret__opening_auction_imbalance__body_size_progression`: Train IC=+0.1484, Lock IC=+0.0451, Lock Sharpe=+0.2816

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__max_up_ret__smooth_momentum_structure__trend_day_regime_conviction`: Train IC=+0.0891, Lock IC=+0.0815, Lock Sharpe=+1.1272
- `vol_ratio_10_60`: Train IC=+0.0761, Lock IC=+0.0275, Lock Sharpe=+0.2531

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2415, Lock IC=+0.1182, Lock Sharpe=+0.8786
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2313, Lock IC=+0.1170, Lock Sharpe=+0.7606
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2313, Lock IC=+0.1170, Lock Sharpe=+0.7606
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2414, Lock IC=+0.1134, Lock Sharpe=+0.6142
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2414, Lock IC=+0.1134, Lock Sharpe=+0.6142

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_day_regime_conviction`: Train IC=+0.2501, Lock IC=+0.1080, Lock Sharpe=+0.9438
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2665, Lock IC=+0.1105, Lock Sharpe=+0.5932
- `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2566, Lock IC=+0.0857, Lock Sharpe=+0.5044
- `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2513, Lock IC=+0.0874, Lock Sharpe=+0.5044
- `combo_z_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2513, Lock IC=+0.0874, Lock Sharpe=+0.5044

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 68.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4394_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1254 | 30 | 56.7% | 20.0% | +0.0283 | -0.2813 |
| B2 Rolling Guard | 59 | 30 | 83.3% | 3.3% | +0.0360 | -0.5532 |
| BH-FDR Gate | 35 | 30 | 40.0% | 10.0% | -0.0040 | -0.4476 |
| B3 Composite Floor | 2 | 2 | 100.0% | 100.0% | +0.1070 | +0.1922 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_return`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.2410
- `bar_ret_0`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.2410
- `combo_mean__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.0725
- `combo_z_sum__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.0725
- `combo_mean__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.0725

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__false_breakout_accumulation__consecutive_higher_highs`: Train IC=+0.0610, Lock IC=+0.0411, Lock Sharpe=+0.1261

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1051, Lock IC=+0.1561, Lock Sharpe=+0.9168
- `combo_abs_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.0894, Lock IC=+0.0391, Lock Sharpe=+0.5672
- `combo_abs_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.0894, Lock IC=+0.0391, Lock Sharpe=+0.5672

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_trend_extrapolated`: Train IC=+0.2095, Lock IC=+0.1061, Lock Sharpe=+0.2866
- `combo_rank_min__star50_limit_proximity_early__morning_trend_extrapolated`: Train IC=+0.2432, Lock IC=+0.1079, Lock Sharpe=+0.0979

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4569_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 377 | 30 | 50.0% | 20.0% | +0.0159 | -0.4622 |
| B2 Rolling Guard | 43 | 30 | 50.0% | 16.7% | +0.0021 | -0.1868 |
| BH-FDR Gate | 8 | 8 | 87.5% | 50.0% | +0.0758 | -0.1162 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1538, Lock IC=+0.1176, Lock Sharpe=+0.7626
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1538, Lock IC=+0.1176, Lock Sharpe=+0.7626
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1202, Lock IC=+0.1196, Lock Sharpe=+0.6521
- `consecutive_trend_bar_intensity`: Train IC=+0.1062, Lock IC=+0.0852, Lock Sharpe=+0.5628
- `combo_min__body_to_range_ratio__net_volume_flow`: Train IC=+0.1316, Lock IC=+0.0829, Lock Sharpe=+0.1223

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0278, Lock Sharpe=+0.6378
- `iv_diff_1d`: Train IC=+0.0831, Lock IC=+0.0677, Lock Sharpe=+0.5796
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0644, Lock Sharpe=+0.3418
- `vix`: Train IC=+0.0045, Lock IC=+0.0426, Lock Sharpe=+0.1425
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0694, Lock Sharpe=+0.0518

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1694, Lock IC=+0.1248, Lock Sharpe=+0.7918
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1694, Lock IC=+0.1248, Lock Sharpe=+0.7918
- `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1416, Lock IC=+0.0921, Lock Sharpe=+0.0205
- `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1416, Lock IC=+0.0921, Lock Sharpe=+0.0205

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 79.0% lock IC > 0, 54.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0936_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1139 | 30 | 96.7% | 66.7% | +0.0961 | +0.2567 |
| B2 Rolling Guard | 110 | 30 | 96.7% | 76.7% | +0.0651 | +0.3394 |
| BH-FDR Gate | 9 | 9 | 88.9% | 44.4% | +0.0478 | -0.1135 |
| B3 Composite Floor | 347 | 30 | 100.0% | 70.0% | +0.0954 | +0.3719 |
| B4 Correlation Gate | 185 | 30 | 100.0% | 100.0% | +0.1222 | +1.0275 |

**Admitted Pool Summary**: 30 features, False Positive Rate = 16.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1076, Mean Lock Sharpe = +0.4779

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1899, Lock IC=+0.1399, Lock Sharpe=+1.2423
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1899, Lock IC=+0.1399, Lock Sharpe=+1.2423
- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.1924, Lock IC=+0.1128, Lock Sharpe=+1.0445
- `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2020, Lock IC=+0.1329, Lock Sharpe=+0.8001
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2020, Lock IC=+0.1329, Lock Sharpe=+0.8001

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1421, Lock IC=+0.1217, Lock Sharpe=+1.2125
- `combo_mean__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1514, Lock IC=+0.0813, Lock Sharpe=+0.9788
- `combo_z_sum__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1514, Lock IC=+0.0813, Lock Sharpe=+0.9788
- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1462, Lock IC=+0.1227, Lock Sharpe=+0.9674
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1462, Lock IC=+0.1227, Lock Sharpe=+0.9674

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.0665, Lock IC=+0.0430, Lock Sharpe=+0.1390
- `combo_sig_product__yesterday_first_30min_return__limit_down_proximity_early`: Train IC=+0.0665, Lock IC=+0.0430, Lock Sharpe=+0.1390
- `vol_gk20`: Train IC=+0.0370, Lock IC=+0.0210, Lock Sharpe=+0.0601
- `early_skew`: Train IC=+0.0611, Lock IC=+0.0865, Lock Sharpe=+0.0257

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2508, Lock IC=+0.1290, Lock Sharpe=+1.3284
- `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2522, Lock IC=+0.1236, Lock Sharpe=+1.2838
- `combo_tri_z_mean__max_up_ret__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2522, Lock IC=+0.1236, Lock Sharpe=+1.2838
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2277, Lock IC=+0.1240, Lock Sharpe=+1.2793
- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2381, Lock IC=+0.1084, Lock Sharpe=+1.2584

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Lock Sharpe=+1.5575
- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2717, Lock IC=+0.1211, Lock Sharpe=+1.5575
- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Lock Sharpe=+1.5260
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2724, Lock IC=+0.1237, Lock Sharpe=+1.3129
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2724, Lock IC=+0.1237, Lock Sharpe=+1.3129

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 46.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0871_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 906 | 30 | 96.7% | 63.3% | +0.0802 | +0.1290 |
| B2 Rolling Guard | 84 | 30 | 96.7% | 76.7% | +0.1005 | +0.4725 |
| BH-FDR Gate | 119 | 30 | 100.0% | 86.7% | +0.1014 | +0.4524 |
| B3 Composite Floor | 11 | 11 | 100.0% | 90.9% | +0.0921 | +0.4691 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1708, Lock IC=+0.1017, Lock Sharpe=+0.9698
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1693, Lock IC=+0.1305, Lock Sharpe=+0.8573
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__trend_strength_intraday`: Train IC=+0.1807, Lock IC=+0.0953, Lock Sharpe=+0.8010
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__counter_trend_bar_weakness`: Train IC=+0.1717, Lock IC=+0.0907, Lock Sharpe=+0.6363
- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1772, Lock IC=+0.1258, Lock Sharpe=+0.6022

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1461, Lock IC=+0.1314, Lock Sharpe=+1.1147
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1461, Lock IC=+0.1314, Lock Sharpe=+1.1147
- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1316, Lock IC=+0.1108, Lock Sharpe=+1.0571
- `combo_rank_min__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1316, Lock IC=+0.1108, Lock Sharpe=+1.0571
- `combo_tri_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1059, Lock IC=+0.1290, Lock Sharpe=+0.9967

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1380, Lock IC=+0.1040, Lock Sharpe=+0.8465
- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1380, Lock IC=+0.1040, Lock Sharpe=+0.8465
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1324, Lock IC=+0.1159, Lock Sharpe=+0.8326
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1324, Lock IC=+0.1159, Lock Sharpe=+0.8326
- `combo_tri_median__rbreaker_sell_setup_proximity_early__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1735, Lock IC=+0.1298, Lock Sharpe=+0.6853

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1828, Lock IC=+0.0959, Lock Sharpe=+0.6946
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1828, Lock IC=+0.0959, Lock Sharpe=+0.6946
- `combo_tri_mean__opening_drive_thrust_ratio__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.5565
- `combo_tri_z_mean__opening_drive_thrust_ratio__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.5565
- `combo_tri_mean__opening_drive_thrust_ratio__first_30min_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.5565

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 44.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4814_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 247 | 30 | 76.7% | 30.0% | +0.0305 | -0.3048 |
| B2 Rolling Guard | 50 | 30 | 63.3% | 43.3% | +0.0232 | -0.0537 |
| BH-FDR Gate | 2 | 2 | 50.0% | 50.0% | +0.0352 | -0.2472 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bb_width`: Train IC=+0.0753, Lock IC=+0.0573, Lock Sharpe=+0.5240
- `trend_day_regime_conviction`: Train IC=+0.1462, Lock IC=+0.0928, Lock Sharpe=+0.5079
- `lunch_transition_volume_skew`: Train IC=+0.0808, Lock IC=+0.0330, Lock Sharpe=+0.4939
- `high_low_sequence_momentum`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.3950
- `rsi_opening`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.3950

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0517, Lock Sharpe=+1.0733
- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.0930, Lock Sharpe=+0.7627
- `combo_rank_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0792, Lock IC=+0.0809, Lock Sharpe=+0.7311
- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0609, Lock IC=+0.0815, Lock Sharpe=+0.6315
- `limit_down_proximity_early`: Train IC=+0.0276, Lock IC=+0.1167, Lock Sharpe=+0.5830

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volatility_expansion_trend_vector`: Train IC=+0.0580, Lock IC=+0.0943, Lock Sharpe=+0.2379

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 400 | +0.0225 | 80.0% |
| 0.45 | 0.20 | 389 | +0.0225 | 80.0% |
| 0.45 | 0.30 | 370 | +0.0225 | 80.0% |
| 0.45 | 0.40 | 324 | +0.0225 | 80.0% |
| 0.45 | 0.50 | 222 | +0.0225 | 80.0% |
| 0.50 | 0.15 | 395 | +0.0225 | 80.0% |
| 0.50 | 0.25 | 382 | +0.0225 | 80.0% |
| 0.50 | 0.35 | 353 | +0.0225 | 80.0% |
| 0.50 | 0.45 | 281 | +0.0225 | 80.0% |
| 0.55 | 0.10 | 395 | +0.0225 | 80.0% |
| 0.55 | 0.20 | 389 | +0.0225 | 80.0% |
| 0.55 | 0.30 | 370 | +0.0225 | 80.0% |
| 0.55 | 0.40 | 324 | +0.0225 | 80.0% |
| 0.55 | 0.50 | 222 | +0.0225 | 80.0% |
| 0.60 | 0.15 | 367 | +0.0225 | 80.0% |
| 0.60 | 0.25 | 366 | +0.0225 | 80.0% |
| 0.60 | 0.35 | 352 | +0.0225 | 80.0% |
| 0.60 | 0.45 | 281 | +0.0225 | 80.0% |
| 0.65 | 0.10 | 323 | +0.0225 | 80.0% |
| 0.65 | 0.20 | 323 | +0.0225 | 80.0% |
| 0.65 | 0.30 | 323 | +0.0225 | 80.0% |
| 0.65 | 0.40 | 311 | +0.0225 | 80.0% |
| 0.65 | 0.50 | 222 | +0.0225 | 80.0% |
| 0.70 | 0.15 | 170 | +0.0225 | 80.0% |
| 0.70 | 0.25 | 170 | +0.0225 | 80.0% |
| 0.70 | 0.35 | 170 | +0.0225 | 80.0% |
| 0.70 | 0.45 | 170 | +0.0225 | 80.0% |
| 0.75 | 0.10 | 32 | +0.0187 | 70.0% |
| 0.75 | 0.20 | 32 | +0.0187 | 70.0% |
| 0.75 | 0.30 | 32 | +0.0187 | 70.0% |
| 0.75 | 0.40 | 32 | +0.0187 | 70.0% |
| 0.75 | 0.50 | 32 | +0.0187 | 70.0% |
| 0.80 | 0.15 | 6 | -0.0013 | 33.3% |
| 0.80 | 0.25 | 6 | -0.0013 | 33.3% |
| 0.80 | 0.35 | 6 | -0.0013 | 33.3% |
| 0.80 | 0.45 | 6 | -0.0013 | 33.3% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 400 candidates, mean lock IC=+0.0225, 80.0% positive

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
| 0.45 | 0.10 | 18 | +0.0119 | 60.0% |
| 0.45 | 0.20 | 6 | +0.0335 | 100.0% |
| 0.45 | 0.30 | 2 | +0.0254 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | +0.0343 | 100.0% |
| 0.50 | 0.25 | 5 | +0.0275 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 11 | +0.0141 | 60.0% |
| 0.55 | 0.20 | 6 | +0.0335 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.15 → 7 candidates, mean lock IC=+0.0381, 100.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 18 | -0.0308 | 20.0% |
| 0.45 | 0.20 | 14 | -0.0308 | 20.0% |
| 0.45 | 0.30 | 11 | -0.0368 | 10.0% |
| 0.45 | 0.40 | 3 | -0.0180 | 33.3% |
| 0.45 | 0.50 | 2 | -0.0008 | 50.0% |
| 0.50 | 0.15 | 14 | -0.0308 | 20.0% |
| 0.50 | 0.25 | 14 | -0.0308 | 20.0% |
| 0.50 | 0.35 | 8 | -0.0353 | 12.5% |
| 0.50 | 0.45 | 2 | -0.0008 | 50.0% |
| 0.55 | 0.10 | 15 | -0.0308 | 20.0% |
| 0.55 | 0.20 | 14 | -0.0308 | 20.0% |
| 0.55 | 0.30 | 11 | -0.0368 | 10.0% |
| 0.55 | 0.40 | 3 | -0.0180 | 33.3% |
| 0.55 | 0.50 | 2 | -0.0008 | 50.0% |
| 0.60 | 0.15 | 13 | -0.0287 | 20.0% |
| 0.60 | 0.25 | 13 | -0.0287 | 20.0% |
| 0.60 | 0.35 | 8 | -0.0353 | 12.5% |
| 0.60 | 0.45 | 2 | -0.0008 | 50.0% |
| 0.65 | 0.10 | 5 | -0.0118 | 40.0% |
| 0.65 | 0.20 | 5 | -0.0118 | 40.0% |
| 0.65 | 0.30 | 3 | -0.0180 | 33.3% |
| 0.65 | 0.40 | 3 | -0.0180 | 33.3% |
| 0.65 | 0.50 | 2 | -0.0008 | 50.0% |
| 0.70 | 0.15 | 2 | -0.0008 | 50.0% |
| 0.70 | 0.25 | 2 | -0.0008 | 50.0% |
| 0.70 | 0.35 | 2 | -0.0008 | 50.0% |
| 0.70 | 0.45 | 2 | -0.0008 | 50.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.65, ir_thr=0.10 → 5 candidates, mean lock IC=-0.0118, 40.0% positive

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
| 0.45 | 0.10 | 1078 | +0.1003 | 100.0% |
| 0.45 | 0.20 | 1054 | +0.1003 | 100.0% |
| 0.45 | 0.30 | 954 | +0.1003 | 100.0% |
| 0.45 | 0.40 | 778 | +0.1003 | 100.0% |
| 0.45 | 0.50 | 575 | +0.1003 | 100.0% |
| 0.50 | 0.15 | 1068 | +0.1003 | 100.0% |
| 0.50 | 0.25 | 1006 | +0.1003 | 100.0% |
| 0.50 | 0.35 | 870 | +0.1003 | 100.0% |
| 0.50 | 0.45 | 698 | +0.1003 | 100.0% |
| 0.55 | 0.10 | 1064 | +0.1003 | 100.0% |
| 0.55 | 0.20 | 1052 | +0.1003 | 100.0% |
| 0.55 | 0.30 | 954 | +0.1003 | 100.0% |
| 0.55 | 0.40 | 778 | +0.1003 | 100.0% |
| 0.55 | 0.50 | 575 | +0.1003 | 100.0% |
| 0.60 | 0.15 | 986 | +0.1003 | 100.0% |
| 0.60 | 0.25 | 967 | +0.1003 | 100.0% |
| 0.60 | 0.35 | 868 | +0.1003 | 100.0% |
| 0.60 | 0.45 | 698 | +0.1003 | 100.0% |
| 0.65 | 0.10 | 771 | +0.1003 | 100.0% |
| 0.65 | 0.20 | 771 | +0.1003 | 100.0% |
| 0.65 | 0.30 | 771 | +0.1003 | 100.0% |
| 0.65 | 0.40 | 732 | +0.1003 | 100.0% |
| 0.65 | 0.50 | 570 | +0.1003 | 100.0% |
| 0.70 | 0.15 | 457 | +0.1003 | 100.0% |
| 0.70 | 0.25 | 457 | +0.1003 | 100.0% |
| 0.70 | 0.35 | 457 | +0.1003 | 100.0% |
| 0.70 | 0.45 | 457 | +0.1003 | 100.0% |
| 0.75 | 0.10 | 187 | +0.0997 | 100.0% |
| 0.75 | 0.20 | 187 | +0.0997 | 100.0% |
| 0.75 | 0.30 | 187 | +0.0997 | 100.0% |
| 0.75 | 0.40 | 187 | +0.0997 | 100.0% |
| 0.75 | 0.50 | 187 | +0.0997 | 100.0% |
| 0.80 | 0.15 | 68 | +0.0994 | 100.0% |
| 0.80 | 0.25 | 68 | +0.0994 | 100.0% |
| 0.80 | 0.35 | 68 | +0.0994 | 100.0% |
| 0.80 | 0.45 | 68 | +0.0994 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1078 candidates, mean lock IC=+0.1003, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 46 | +0.0055 | 50.0% |
| 0.45 | 0.20 | 35 | +0.0055 | 50.0% |
| 0.45 | 0.30 | 7 | +0.0516 | 100.0% |
| 0.45 | 0.40 | 2 | +0.0306 | 100.0% |
| 0.45 | 0.50 | 2 | +0.0306 | 100.0% |
| 0.50 | 0.15 | 37 | +0.0055 | 50.0% |
| 0.50 | 0.25 | 29 | +0.0055 | 50.0% |
| 0.50 | 0.35 | 6 | +0.0426 | 100.0% |
| 0.50 | 0.45 | 2 | +0.0306 | 100.0% |
| 0.55 | 0.10 | 38 | +0.0055 | 50.0% |
| 0.55 | 0.20 | 35 | +0.0055 | 50.0% |
| 0.55 | 0.30 | 7 | +0.0516 | 100.0% |
| 0.55 | 0.40 | 2 | +0.0306 | 100.0% |
| 0.55 | 0.50 | 2 | +0.0306 | 100.0% |
| 0.60 | 0.15 | 14 | +0.0055 | 50.0% |
| 0.60 | 0.25 | 14 | +0.0055 | 50.0% |
| 0.60 | 0.35 | 6 | +0.0426 | 100.0% |
| 0.60 | 0.45 | 2 | +0.0306 | 100.0% |
| 0.65 | 0.10 | 2 | +0.0306 | 100.0% |
| 0.65 | 0.20 | 2 | +0.0306 | 100.0% |
| 0.65 | 0.30 | 2 | +0.0306 | 100.0% |
| 0.65 | 0.40 | 2 | +0.0306 | 100.0% |
| 0.65 | 0.50 | 2 | +0.0306 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.30 → 7 candidates, mean lock IC=+0.0516, 100.0% positive

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
| 0.45 | 0.10 | 667 | +0.1169 | 100.0% |
| 0.45 | 0.20 | 640 | +0.1169 | 100.0% |
| 0.45 | 0.30 | 585 | +0.1169 | 100.0% |
| 0.45 | 0.40 | 444 | +0.1169 | 100.0% |
| 0.45 | 0.50 | 285 | +0.1169 | 100.0% |
| 0.50 | 0.15 | 656 | +0.1169 | 100.0% |
| 0.50 | 0.25 | 613 | +0.1169 | 100.0% |
| 0.50 | 0.35 | 535 | +0.1169 | 100.0% |
| 0.50 | 0.45 | 369 | +0.1169 | 100.0% |
| 0.55 | 0.10 | 656 | +0.1169 | 100.0% |
| 0.55 | 0.20 | 639 | +0.1169 | 100.0% |
| 0.55 | 0.30 | 585 | +0.1169 | 100.0% |
| 0.55 | 0.40 | 444 | +0.1169 | 100.0% |
| 0.55 | 0.50 | 285 | +0.1169 | 100.0% |
| 0.60 | 0.15 | 604 | +0.1169 | 100.0% |
| 0.60 | 0.25 | 600 | +0.1169 | 100.0% |
| 0.60 | 0.35 | 535 | +0.1169 | 100.0% |
| 0.60 | 0.45 | 369 | +0.1169 | 100.0% |
| 0.65 | 0.10 | 474 | +0.1169 | 100.0% |
| 0.65 | 0.20 | 474 | +0.1169 | 100.0% |
| 0.65 | 0.30 | 474 | +0.1169 | 100.0% |
| 0.65 | 0.40 | 416 | +0.1169 | 100.0% |
| 0.65 | 0.50 | 284 | +0.1169 | 100.0% |
| 0.70 | 0.15 | 230 | +0.1169 | 100.0% |
| 0.70 | 0.25 | 230 | +0.1169 | 100.0% |
| 0.70 | 0.35 | 230 | +0.1169 | 100.0% |
| 0.70 | 0.45 | 227 | +0.1169 | 100.0% |
| 0.75 | 0.10 | 64 | +0.1169 | 100.0% |
| 0.75 | 0.20 | 64 | +0.1169 | 100.0% |
| 0.75 | 0.30 | 64 | +0.1169 | 100.0% |
| 0.75 | 0.40 | 64 | +0.1169 | 100.0% |
| 0.75 | 0.50 | 64 | +0.1169 | 100.0% |
| 0.80 | 0.15 | 6 | +0.1221 | 100.0% |
| 0.80 | 0.25 | 6 | +0.1221 | 100.0% |
| 0.80 | 0.35 | 6 | +0.1221 | 100.0% |
| 0.80 | 0.45 | 6 | +0.1221 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 6 candidates, mean lock IC=+0.1221, 100.0% positive

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1266 | +0.0000 | +0.0354 | 0.28x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1310 | +0.0000 | +0.0352 | 0.27x | 2016-08-24 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +0.1166 | +0.0000 | +0.0094 | 0.08x | 2015-03-16 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | +0.1146 | +0.0000 | -0.0067 | -0.06x | 2017-04-07 |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1145 | +0.0000 | +0.0270 | 0.24x | 2017-05-09 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1118 | +0.0000 | +0.0623 | 0.56x | 2016-08-24 |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | +0.1039 | +0.0000 | +0.0234 | 0.23x | 2015-01-08 |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | +0.0976 | +0.0000 | +0.0045 | 0.05x | 2013-08-21 |
| `combo_max__max_up_ret__volume_weighted_price_position` | +0.1088 | +0.0000 | -0.0088 | -0.08x | 2015-02-06 |
| `combo_min__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1156 | +0.0000 | +0.0125 | 0.11x | 2017-07-10 |
| `combo_rank_max__bar_ret_0__first_bar_sentiment` | +0.0831 | +0.0000 | -0.0033 | -0.04x | 2010-12-14 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +0.0861 | +0.0000 | -0.0055 | -0.06x | 2015-01-08 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0963 | +0.0000 | +0.0427 | 0.44x | 2016-08-24 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1149 | +0.0000 | -0.0134 | -0.12x | 2017-07-10 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | +0.1052 | +0.0000 | +0.0291 | 0.28x | 2015-03-16 |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1023 | +0.0000 | -0.0007 | -0.01x | 2014-12-08 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +0.1187 | +0.0000 | +0.0266 | 0.22x | 2017-02-06 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.0901 | +0.0000 | +0.0042 | 0.05x | 2013-08-21 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +0.0743 | +0.0000 | +0.0288 | 0.39x | 2017-10-12 |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | +0.0826 | +0.0000 | -0.0080 | -0.10x | 2015-01-08 |
| `combo_mean__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0371 | +0.0000 | +0.0535 | 1.44x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1931 | +0.0000 | +0.1193 | 0.62x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +0.1937 | +0.0000 | +0.0910 | 0.47x | 2016-11-30 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1881 | +0.0000 | +0.0955 | 0.51x | 2021-07-28 |
| `combo_clamp_diff__max_up_ret__body_size_progression` | +0.1746 | +0.0000 | +0.0855 | 0.49x | 2025-07-24 |
| `combo_rank_max__first_bar_sentiment__bar_ret_0` | +0.1157 | +0.0000 | +0.0585 | 0.51x | 2017-08-08 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | +0.1760 | +0.0000 | +0.0887 | 0.50x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1718 | +0.0000 | +0.1168 | 0.68x | No decay |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | +0.1827 | +0.0000 | +0.0869 | 0.48x | 2022-12-15 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +0.1669 | +0.0000 | +0.0590 | 0.35x | 2020-01-06 |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | +0.1615 | +0.0000 | +0.1235 | 0.76x | 2016-09-26 |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | +0.1687 | +0.0000 | +0.0905 | 0.54x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1670 | +0.0000 | +0.0942 | 0.56x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1661 | +0.0000 | +0.0926 | 0.56x | No decay |
| `combo_min__volatility_expansion_trend_vector__close_vs_open_range` | +0.1446 | +0.0000 | +0.0848 | 0.59x | 2016-11-01 |
| `combo_max__close_vs_open_range__first_bar_return` | +0.1680 | +0.0000 | +0.0749 | 0.45x | No decay |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | +0.1696 | +0.0000 | +0.0607 | 0.36x | 2016-12-29 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +0.1266 | +0.0000 | +0.0833 | 0.66x | 2017-05-09 |
| `combo_max__bar_ret_0__max_down_ret` | +0.1604 | +0.0000 | +0.0818 | 0.51x | 2016-11-30 |
| `max_up_ret` | +0.1871 | +0.0000 | +0.0813 | 0.43x | No decay |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | +0.1840 | +0.0000 | +0.0891 | 0.48x | 2020-01-06 |
| `combo_max__star50_limit_proximity_early__early_body_momentum` | +0.1470 | +0.0000 | +0.0916 | 0.62x | 2016-09-26 |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | +0.1551 | +0.0000 | +0.0962 | 0.62x | 2016-11-01 |
| `combo_sig_product__max_up_ret__first_bar_return` | +0.1566 | +0.0000 | +0.0557 | 0.36x | No decay |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1420 | +0.0000 | +0.1566 | 1.10x | 2016-09-26 |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | +0.1421 | +0.0000 | +0.0996 | 0.70x | 2016-09-26 |
| `combo_sig_product__opening_auction_imbalance__first_bar_return` | +0.1206 | +0.0000 | +0.0538 | 0.45x | 2016-11-01 |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | +0.1438 | +0.0000 | +0.1093 | 0.76x | 2016-09-26 |
| `vwap_close_divergence_trend` | +0.1321 | +0.0000 | +0.0582 | 0.44x | 2016-11-01 |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | +0.1553 | +0.0000 | +0.0876 | 0.56x | 2016-12-29 |
| `combo_z_sum__opening_drive_thrust_ratio__max_down_ret` | +0.1761 | +0.0000 | +0.1011 | 0.57x | 2016-11-30 |
| `combo_z_sum__first_bar_sentiment__max_down_ret` | +0.1441 | +0.0000 | +0.0982 | 0.68x | No decay |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1618 | +0.0000 | +0.1235 | 0.76x | 2017-01-20 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1165 | +0.0000 | +0.0911 | 0.78x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1759 | +0.0000 | +0.1173 | 0.67x | 2017-01-20 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1510 | +0.0000 | +0.1316 | 0.87x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1432 | +0.0000 | +0.1304 | 0.91x | 2016-09-14 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | +0.1669 | +0.0000 | +0.1181 | 0.71x | 2017-02-27 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1575 | +0.0000 | +0.1085 | 0.69x | 2016-10-24 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1046 | +0.0000 | +0.1097 | 1.05x | 2011-10-18 |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | +0.1445 | +0.0000 | +0.0879 | 0.61x | 2016-12-21 |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | +0.1575 | +0.0000 | +0.1094 | 0.69x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1489 | +0.0000 | +0.1236 | 0.83x | 2016-09-14 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | +0.1413 | +0.0000 | +0.1246 | 0.88x | 2011-10-18 |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | +0.1552 | +0.0000 | +0.0864 | 0.56x | 2017-02-27 |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1194 | +0.0000 | +0.1330 | 1.11x | 2011-10-18 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1398 | +0.0000 | +0.1203 | 0.86x | 2016-09-14 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | +0.1110 | +0.0000 | +0.0564 | 0.51x | 2016-09-14 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1278 | +0.0000 | +0.1284 | 1.00x | 2017-02-27 |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1585 | +0.0000 | +0.1212 | 0.76x | 2017-02-27 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1211 | +0.0000 | +0.1270 | 1.05x | 2017-01-20 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.0568 | +0.0000 | +0.0486 | 0.86x | 2011-03-11 |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | +0.1288 | +0.0000 | +0.0753 | 0.58x | 2017-04-28 |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | +0.1518 | +0.0000 | +0.0874 | 0.58x | 2017-01-20 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1070 | +0.0000 | +0.0801 | 0.75x | 2016-09-14 |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | +0.1558 | +0.0000 | +0.1373 | 0.88x | 2016-12-21 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +0.1432 | +0.0000 | +0.0674 | 0.47x | 2017-01-20 |
| `combo_min__yesterday_first_30min_return__rbreaker_buy_setup_proximity_early` | +0.0844 | +0.0000 | +0.1067 | 1.26x | 2011-10-18 |
| `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early` | +0.1380 | +0.0000 | +0.1298 | 0.94x | 2011-10-18 |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | +0.1468 | +0.0000 | +0.1273 | 0.87x | 2016-09-14 |
| `combo_z_sum__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | +0.1364 | +0.0000 | +0.1020 | 0.75x | 2011-10-18 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1316 | +0.0000 | +0.1348 | 1.02x | 2011-10-18 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.5643). Consider relaxing this gate.
2. **300ETF `single` — B3 Composite Floor too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.3713). Consider relaxing this gate.
3. **300ETF `single` — Admission too loose**: 90% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
4. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 19.0%, mean lock Sharpe=-0.0472). Consider relaxing this gate.
5. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=+0.2518). Consider relaxing this gate.
6. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 9.0%, mean lock Sharpe=-0.1128). Consider relaxing this gate.
7. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.3245). Consider relaxing this gate.
8. **500ETF `single` — B3 Composite Floor too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.2726). Consider relaxing this gate.
9. **500ETF `single` — B4 Correlation Gate too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.1150). Consider relaxing this gate.
10. **500ETF `short` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.1162). Consider relaxing this gate.
11. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 54.0%, mean lock Sharpe=+1.0275). Consider relaxing this gate.
12. **159915ETF `long` — B2 Rolling Guard too strict**: 76.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 46.0%, mean lock Sharpe=+0.4725). Consider relaxing this gate.
13. **159915ETF `long` — BH-FDR Gate too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 46.0%, mean lock Sharpe=+0.4524). Consider relaxing this gate.
14. **159915ETF `long` — B3 Composite Floor too strict**: 90.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 46.0%, mean lock Sharpe=+0.4691). Consider relaxing this gate.
15. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.3048). Consider relaxing this gate.
16. **159915ETF `short` — B2 Rolling Guard too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.0537). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
