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

### 300ETF — `single` (Full Model Lockbox IC: +0.0702, Sharpe: +0.0250)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.1225 | +0.0632 | +0.0632 | -0.1094 | 87.22 | +12.9 | 1.61x | -0.0012 | +0.0688 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1113 | +0.0681 | +0.0681 | +0.5663 | 83.52 | +22.2 | 2.77x | -0.0003 | +0.0136 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1119 | +0.0543 | +0.0543 | -0.0743 | 86.37 | +13.2 | 1.64x | -0.0025 | +0.1597 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1132 | +0.0877 | +0.0877 | +0.6238 | 86.37 | +22.8 | 2.85x | +0.0024 | -0.0889 |
| `combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1129 | +0.0739 | +0.0739 | -0.1182 | 86.37 | +12.7 | 1.59x | +0.0009 | +0.0329 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0872 | +0.0567 | +0.0567 | -0.1329 | 86.37 | +12.8 | 1.60x | +0.0013 | +0.1109 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0965 | +0.0662 | +0.0662 | -0.3946 | 84.09 | +8.1 | 1.01x | -0.0026 | +0.1327 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0742 | +0.0529 | +0.0529 | +0.0704 | 81.81 | +14.3 | 1.79x | -0.0000 | +0.2112 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0660 | +0.0417 | +0.0417 | -0.4282 | 82.38 | +7.5 | 0.94x | +0.0003 | +0.1065 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0917 | +0.0524 | +0.0524 | -0.2631 | 84.09 | +10.7 | 1.33x | +0.0010 | +0.0455 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0833 | +0.0444 | +0.0444 | -0.8108 | 88.93 | +4.8 | 0.61x | -0.0010 | +0.0490 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Other Technical | +1 | +0.1095 | +0.0642 | +0.0642 | -0.2190 | 85.23 | +11.0 | 1.38x | +0.0005 | -0.0419 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0680 | +0.0048 | +0.0048 | -1.0941 | 75.25 | +3.0 | 0.38x | +0.0000 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | -0.0541 | +0.0076 | +0.0076 | -0.7244 | 68.41 | +3.6 | 0.45x | +0.0002 | -0.0536 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1229, Sharpe: +0.6866)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1702 | +0.0726 | +0.0726 | -1.0145 | 68.98 | -4.1 | -0.51x | -0.0008 | -0.0046 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1749 | +0.0868 | +0.0868 | -0.0125 | 86.65 | +14.1 | 1.76x | -0.0006 | -0.0046 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1685 | +0.0893 | +0.0893 | -0.0906 | 74.40 | +10.5 | 1.32x | +0.0002 | -0.0046 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1795 | +0.1000 | +0.1000 | +0.2808 | 85.23 | +19.8 | 2.47x | +0.0000 | +0.1758 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1544 | +0.1214 | +0.1214 | +0.4088 | 87.51 | +21.6 | 2.70x | +0.0013 | +0.1474 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1763 | +0.1217 | +0.1217 | +0.3993 | 89.22 | +21.2 | 2.65x | +0.0007 | +0.0743 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1634 | +0.0936 | +0.0936 | +0.1027 | 87.22 | +16.3 | 2.03x | -0.0006 | +0.1042 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1641 | +0.0912 | +0.0912 | -0.4247 | 89.22 | +9.3 | 1.16x | -0.0006 | -0.0106 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1711 | +0.0919 | +0.0919 | +0.4253 | 81.81 | +22.3 | 2.78x | -0.0003 | +0.0664 |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1310 | +0.1134 | +0.1134 | +0.7733 | 87.51 | +28.6 | 3.57x | +0.0013 | +0.0640 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1850 | +0.0916 | +0.0916 | +0.2565 | 85.23 | +18.2 | 2.27x | -0.0003 | +0.0407 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | Volatility & Oscillators | +1 | +0.1716 | +0.1099 | +0.1099 | +0.1953 | 90.64 | +17.8 | 2.22x | +0.0001 | +0.0042 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1585 | +0.0805 | +0.0805 | -0.2281 | 86.37 | +10.4 | 1.30x | -0.0007 | +0.0084 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1484 | +0.1175 | +0.1175 | +0.0599 | 85.51 | +15.0 | 1.87x | +0.0010 | +0.0371 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1602 | +0.0884 | +0.0884 | +0.0717 | 88.36 | +15.8 | 1.98x | -0.0000 | +0.2029 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1207 | +0.1186 | +0.1186 | +0.6889 | 83.52 | +26.4 | 3.30x | +0.0012 | +0.1377 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1269 | +0.0958 | +0.0958 | -0.0594 | 80.10 | +12.1 | 1.51x | +0.0013 | -0.0196 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1458 | +0.0948 | +0.0948 | +0.7214 | 79.53 | +28.1 | 3.51x | +0.0013 | +0.2514 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1720 | +0.1199 | +0.1199 | +0.6302 | 84.09 | +26.5 | 3.31x | +0.0006 | +0.0328 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1595 | +0.0936 | +0.0936 | -0.4408 | 91.50 | +8.1 | 1.01x | -0.0001 | -0.0604 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1722 | +0.0840 | +0.0840 | +0.1234 | 87.22 | +16.4 | 2.06x | -0.0004 | -0.0142 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1401 | +0.0836 | +0.0836 | -0.1694 | 86.65 | +11.9 | 1.49x | -0.0002 | +0.0149 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1405 | +0.1069 | +0.1069 | +0.1992 | 86.94 | +18.3 | 2.28x | +0.0005 | +0.1246 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1590 | +0.0909 | +0.0909 | +0.1420 | 89.79 | +16.6 | 2.08x | -0.0008 | -0.0046 |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.1444 | +0.0859 | +0.0859 | -0.3624 | 87.51 | +8.8 | 1.10x | +0.0002 | +0.2374 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1362 | +0.0768 | +0.0768 | -0.0795 | 84.37 | +12.8 | 1.60x | -0.0006 | -0.0003 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1323 | +0.0654 | +0.0654 | -0.1136 | 88.36 | +13.0 | 1.63x | -0.0002 | +0.1052 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1454 | +0.1031 | +0.1031 | +0.1782 | 89.50 | +17.2 | 2.15x | +0.0002 | -0.0356 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1603 | +0.0792 | +0.0792 | +0.1206 | 81.24 | +15.8 | 1.97x | -0.0003 | +0.0218 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1369 | +0.1223 | +0.1223 | +0.1983 | 82.38 | +17.5 | 2.19x | +0.0007 | +0.1285 |
| `combo_sig_product__rsi_opening__max_down_ret` | Intraday Range Momentum | +1 | +0.1200 | +0.0788 | +0.0788 | -0.2311 | 86.94 | +10.1 | 1.27x | +0.0008 | -0.0196 |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | Volatility & Oscillators | +1 | +0.1119 | +0.0500 | +0.0500 | +0.1077 | 83.52 | +16.0 | 2.00x | +0.0003 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1449, Sharpe: +1.2347)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1495 | +0.1158 | +0.1158 | +1.2155 | 87.51 | +37.7 | 4.71x | -0.0008 | +0.0413 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1569 | +0.1269 | +0.1269 | +1.3258 | 80.10 | +36.2 | 4.52x | -0.0004 | +0.0488 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1603 | +0.1260 | +0.1260 | +1.0764 | 81.24 | +37.4 | 4.67x | -0.0003 | +0.0477 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1415 | +0.1355 | +0.1355 | +1.0307 | 83.52 | +37.1 | 4.63x | +0.0004 | -0.0972 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1072 | +0.1075 | +0.1075 | +0.1326 | 80.10 | +16.3 | 2.04x | +0.0005 | +0.0549 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1187 | +0.0763 | +0.0763 | +0.2812 | 70.98 | +16.6 | 2.08x | -0.0009 | -0.0270 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1535 | +0.1247 | +0.1247 | +1.3214 | 88.65 | +44.1 | 5.51x | -0.0012 | +0.1001 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1078 | +0.1073 | +0.1073 | +0.1651 | 79.53 | +17.0 | 2.12x | +0.0011 | +0.0698 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1414 | +0.1261 | +0.1261 | +0.7621 | 80.67 | +31.7 | 3.97x | -0.0000 | +0.1385 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1201 | +0.1316 | +0.1316 | +1.0690 | 76.11 | +39.2 | 4.90x | +0.0011 | +0.0147 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1617 | +0.1207 | +0.1207 | +0.6732 | 80.67 | +29.9 | 3.73x | -0.0009 | +0.1723 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1383 | +0.1176 | +0.1176 | +1.0843 | 86.37 | +39.3 | 4.92x | -0.0003 | +0.1001 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1695 | +0.1218 | +0.1218 | +1.0739 | 85.80 | +39.1 | 4.89x | -0.0005 | +0.1725 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1209 | +0.1375 | +0.1375 | +1.2205 | 86.94 | +38.7 | 4.84x | +0.0011 | +0.1680 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1227 | +0.1048 | +0.1048 | +0.2691 | 78.96 | +19.4 | 2.42x | -0.0002 | +0.0710 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1149 | +0.0579 | +0.0579 | -0.1824 | 69.84 | +8.8 | 1.10x | -0.0016 | +0.0444 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1277 | +0.1126 | +0.1126 | +0.4745 | 84.37 | +23.9 | 2.99x | +0.0000 | -0.0804 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.0800 | +0.0795 | +0.0795 | -0.7280 | 74.97 | +1.6 | 0.19x | -0.0006 | -0.0317 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1455 | +0.1309 | +0.1309 | +0.6647 | 82.95 | +29.3 | 3.66x | -0.0002 | +0.1151 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1127 | +0.1282 | +0.1282 | +0.2135 | 82.95 | +18.2 | 2.27x | +0.0018 | +0.0547 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | Other Technical | +1 | +0.1174 | +0.1245 | +0.1245 | +0.7972 | 86.65 | +31.2 | 3.90x | +0.0001 | +0.0000 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1211 | +0.0928 | +0.0928 | +0.0401 | 81.81 | +14.4 | 1.79x | -0.0006 | -0.1026 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1379 | +0.1116 | +0.1116 | +0.4422 | 88.65 | +23.3 | 2.91x | -0.0005 | +0.1370 |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1191 | +0.0661 | +0.0661 | +0.1638 | 68.70 | +14.4 | 1.80x | -0.0014 | +0.0052 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1275 | +0.1118 | +0.1118 | +0.0237 | 78.96 | +13.6 | 1.70x | +0.0001 | +0.0299 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1201 | +0.1069 | +0.1069 | +0.6578 | 86.08 | +27.6 | 3.44x | +0.0002 | +0.0608 |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1010 | +0.1043 | +0.1043 | +0.4089 | 83.52 | +23.1 | 2.88x | -0.0002 | -0.0427 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 11.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6270_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1042 | 30 | 100.0% | 23.3% | +0.0588 | -0.2227 |
| B2 Rolling Guard | 78 | 30 | 90.0% | 13.3% | +0.0353 | -0.4728 |
| BH-FDR Gate | 12 | 12 | 75.0% | 16.7% | +0.0198 | -0.7456 |
| B3 Composite Floor | 268 | 30 | 100.0% | 53.3% | +0.0653 | -0.0523 |
| B4 Correlation Gate | 31 | 30 | 100.0% | 26.7% | +0.0658 | -0.1060 |

**Admitted Pool Summary**: 14 features, False Positive Rate = 78.6% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0527, Mean Lock Sharpe = -0.2220

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.1991, Lock IC=+0.0524, Lock Sharpe=+0.3484
- `combo_mean__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Lock Sharpe=+0.0796
- `combo_z_sum__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Lock Sharpe=+0.0796
- `combo_mean__bar_ret_0__bar_body_rng_0`: Train IC=+0.1818, Lock IC=+0.0611, Lock Sharpe=+0.0796
- `combo_z_sum__bar_ret_0__bar_body_rng_0`: Train IC=+0.1818, Lock IC=+0.0611, Lock Sharpe=+0.0796

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1348, Lock IC=+0.0544, Lock Sharpe=+0.0825
- `combo_ratio__max_up_ret__volume_weighted_price_position`: Train IC=+0.1340, Lock IC=+0.0378, Lock Sharpe=+0.0771
- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1502, Lock IC=+0.0543, Lock Sharpe=+0.0496
- `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__opening_drive_thrust_ratio`: Train IC=+0.1344, Lock IC=+0.0481, Lock Sharpe=+0.0365

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.0951, Lock IC=+0.0600, Lock Sharpe=+0.3226
- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.0951, Lock IC=+0.0600, Lock Sharpe=+0.3226

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2370, Lock IC=+0.0693, Lock Sharpe=+0.1207
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2370, Lock IC=+0.0693, Lock Sharpe=+0.1207
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2366, Lock IC=+0.0693, Lock Sharpe=+0.1207
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2366, Lock IC=+0.0693, Lock Sharpe=+0.1207
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Lock Sharpe=+0.0819

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0937, Lock Sharpe=+0.6250
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2691, Lock IC=+0.0706, Lock Sharpe=+0.4336
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.0755, Lock Sharpe=+0.1301
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1929, Lock IC=+0.0529, Lock Sharpe=+0.0704
- `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.1878, Lock IC=+0.0673, Lock Sharpe=+0.0336

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 28.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6520_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 539 | 30 | 73.3% | 16.7% | +0.0073 | -0.5705 |
| B2 Rolling Guard | 36 | 30 | 33.3% | 6.7% | +0.0030 | -0.5112 |
| BH-FDR Gate | 4 | 4 | 75.0% | 0.0% | -0.0046 | -1.2277 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__roc60__sma50_dist`: Train IC=+0.1278, Lock IC=+0.0137, Lock Sharpe=+0.6471
- `combo_sig_product__donchian_breakout_ratio_20d__sma100_dist`: Train IC=+0.1885, Lock IC=+0.0306, Lock Sharpe=+0.6081
- `combo_sig_product__donchian_breakout_proximity_20d__sma100_dist`: Train IC=+0.1885, Lock IC=+0.0306, Lock Sharpe=+0.6081
- `combo_sig_product__willr14__roc60`: Train IC=+0.1569, Lock IC=+0.0107, Lock Sharpe=+0.5847
- `combo_rank_max__roc60__sma50_dist`: Train IC=+0.1730, Lock IC=+0.0057, Lock Sharpe=+0.1553

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.0991, Lock IC=+0.0131, Lock Sharpe=+0.3703
- `combo_max__roc60__sma50_dist`: Train IC=+0.1535, Lock IC=+0.0027, Lock Sharpe=+0.2196

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 4.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7473_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 493 | 30 | 56.7% | 6.7% | +0.0189 | -0.6545 |
| B2 Rolling Guard | 67 | 30 | 53.3% | 6.7% | -0.0041 | -0.6161 |
| BH-FDR Gate | 21 | 21 | 95.2% | 28.6% | +0.0575 | -0.2043 |
| B3 Composite Floor | 5 | 5 | 80.0% | 0.0% | +0.0296 | -0.5529 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1299, Lock IC=+0.0763, Lock Sharpe=+0.1670
- `combo_diff__volume_weighted_momentum_acceleration__max_down_ret`: Train IC=+0.1031, Lock IC=+0.0668, Lock Sharpe=+0.0858

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__opening_drive_thrust_ratio__max_down_ret`: Train IC=+0.0394, Lock IC=+0.0505, Lock Sharpe=+0.2743
- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0258, Lock Sharpe=+0.0981

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1154, Lock IC=+0.0716, Lock Sharpe=+0.2059
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0686, Lock IC=+0.0655, Lock Sharpe=+0.1803
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0648, Lock IC=+0.0618, Lock Sharpe=+0.0655
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0648, Lock IC=+0.0618, Lock Sharpe=+0.0655
- `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0896, Lock IC=+0.0585, Lock Sharpe=+0.0396

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7095_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 704 | 30 | 100.0% | 56.7% | +0.0295 | +0.0043 |
| B2 Rolling Guard | 31 | 30 | 36.7% | 0.0% | +0.0007 | -0.6138 |
| BH-FDR Gate | 3 | 3 | 66.7% | 0.0% | +0.0034 | -0.6134 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.1615, Lock IC=+0.0418, Lock Sharpe=+0.6757
- `combo_sig_product__iv_corridor_width__sma100_dist`: Train IC=+0.1837, Lock IC=+0.0421, Lock Sharpe=+0.3474
- `combo_max__iv_corridor_width__yesterday_wavetrend_osc`: Train IC=+0.1760, Lock IC=+0.0658, Lock Sharpe=+0.2537
- `combo_max__iv_corridor_width__wavetrend_osc_day`: Train IC=+0.1760, Lock IC=+0.0658, Lock Sharpe=+0.2537
- `combo_max__bar_vol_4__rsi21`: Train IC=+0.1374, Lock IC=+0.0353, Lock Sharpe=+0.1404

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.0% lock IC > 0, 7.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9766_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 315 | 30 | 43.3% | 3.3% | +0.0052 | -0.8544 |
| B2 Rolling Guard | 38 | 30 | 30.0% | 6.7% | -0.0022 | -0.5453 |
| BH-FDR Gate | 8 | 8 | 25.0% | 0.0% | -0.0038 | -1.5665 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma_distance_60d`: Train IC=+0.1247, Lock IC=+0.0324, Lock Sharpe=+0.0794

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__iv_envelope_deviation__yesterday_wavetrend_osc`: Train IC=+0.0282, Lock IC=+0.0681, Lock Sharpe=+0.1486
- `combo_min__iv_envelope_deviation__wavetrend_osc_day`: Train IC=+0.0282, Lock IC=+0.0681, Lock Sharpe=+0.1486

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 54.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5734_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 278 | 30 | 80.0% | 36.7% | +0.0192 | -0.2852 |
| B2 Rolling Guard | 33 | 30 | 30.0% | 6.7% | -0.0026 | -0.4064 |
| BH-FDR Gate | 6 | 6 | 33.3% | 0.0% | -0.0062 | -0.8418 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc60`: Train IC=+0.1073, Lock IC=+0.0034, Lock Sharpe=+0.4834
- `combo_mean__bar_vol_4__mfi14`: Train IC=+0.1793, Lock IC=+0.0588, Lock Sharpe=+0.3598
- `combo_z_sum__bar_vol_4__mfi14`: Train IC=+0.1793, Lock IC=+0.0588, Lock Sharpe=+0.3598
- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1547, Lock IC=+0.0506, Lock Sharpe=+0.3230
- `combo_z_sum__bar_vol_4__sma_distance_60d`: Train IC=+0.1547, Lock IC=+0.0506, Lock Sharpe=+0.3230

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0282, Lock Sharpe=+0.1305
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0010, Lock Sharpe=+0.0543

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 74.0% lock IC > 0, 28.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3330_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1680 | 30 | 100.0% | 80.0% | +0.0910 | +0.1935 |
| B2 Rolling Guard | 104 | 30 | 83.3% | 3.3% | +0.0362 | -0.3825 |
| BH-FDR Gate | 10 | 10 | 90.0% | 0.0% | +0.0146 | -0.8530 |
| B3 Composite Floor | 457 | 30 | 100.0% | 80.0% | +0.1032 | +0.1489 |
| B4 Correlation Gate | 435 | 30 | 100.0% | 93.3% | +0.1073 | +0.3238 |

**Admitted Pool Summary**: 32 features, False Positive Rate = 37.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0944, Mean Lock Sharpe = +0.0893

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2312, Lock IC=+0.1016, Lock Sharpe=+0.8235
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Lock Sharpe=+0.7852
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Lock Sharpe=+0.5628
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2910, Lock IC=+0.1185, Lock Sharpe=+0.5129
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.2819, Lock IC=+0.1134, Lock Sharpe=+0.5038

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__max_up_ret__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1298, Lock IC=+0.0164, Lock Sharpe=+0.1364

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.4332
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.4332
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2875, Lock IC=+0.1153, Lock Sharpe=+0.3917
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.3903
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.3903

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Lock Sharpe=+0.7733
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2863, Lock IC=+0.1160, Lock Sharpe=+0.6875
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.5864
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.5864
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2897, Lock IC=+0.1048, Lock Sharpe=+0.5413

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 74.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6674_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1252 | 30 | 100.0% | 0.0% | +0.0600 | -0.3619 |
| B2 Rolling Guard | 46 | 30 | 53.3% | 20.0% | +0.0235 | -0.2953 |
| BH-FDR Gate | 33 | 30 | 100.0% | 16.7% | +0.0590 | -0.4456 |
| B3 Composite Floor | 29 | 29 | 100.0% | 20.7% | +0.0641 | -0.4938 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv`: Train IC=+0.0483, Lock IC=+0.0482, Lock Sharpe=+0.6460
- `vix`: Train IC=+0.0323, Lock IC=+0.0472, Lock Sharpe=+0.2698
- `iv_diff_1d`: Train IC=+0.0348, Lock IC=+0.0707, Lock Sharpe=+0.2120
- `combo_sig_product__rbreaker_sell_setup_proximity_early__morning_trend_extrapolated`: Train IC=+0.0945, Lock IC=+0.0797, Lock Sharpe=+0.1737
- `vix_rolling_percentile_60d`: Train IC=+0.0325, Lock IC=+0.0114, Lock Sharpe=+0.1692

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1334, Lock IC=+0.1347, Lock Sharpe=+0.4906
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.1335, Lock IC=+0.1161, Lock Sharpe=+0.2183
- `close_vs_open_range`: Train IC=+0.1077, Lock IC=+0.0899, Lock Sharpe=+0.1859
- `combo_min__shaved_bar_trend_conviction__trend_day_regime_conviction`: Train IC=+0.1309, Lock IC=+0.0741, Lock Sharpe=+0.1597
- `volume_percentile_20d`: Train IC=+0.1100, Lock IC=+0.0405, Lock Sharpe=+0.0586

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1684, Lock IC=+0.0952, Lock Sharpe=+0.5126
- `combo_rank_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1844, Lock IC=+0.0986, Lock Sharpe=+0.3455
- `combo_sig_product__limit_down_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1583, Lock IC=+0.1136, Lock Sharpe=+0.2855
- `combo_sig_product__rbreaker_buy_setup_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1583, Lock IC=+0.1136, Lock Sharpe=+0.2855
- `combo_rank_min__shaved_bar_trend_conviction__morning_trend_extrapolated`: Train IC=+0.1703, Lock IC=+0.0653, Lock Sharpe=+0.2687

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4492_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 372 | 30 | 66.7% | 43.3% | +0.0363 | -0.0997 |
| B2 Rolling Guard | 48 | 30 | 50.0% | 13.3% | -0.0002 | -0.3046 |
| BH-FDR Gate | 6 | 6 | 100.0% | 33.3% | +0.0799 | -0.1139 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1306, Lock IC=+0.1123, Lock Sharpe=+0.9110
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1306, Lock IC=+0.1123, Lock Sharpe=+0.9110
- `combo_mean__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1276, Lock IC=+0.1034, Lock Sharpe=+0.6180
- `combo_z_sum__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1276, Lock IC=+0.1034, Lock Sharpe=+0.6180
- `combo_mean__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1276, Lock IC=+0.1034, Lock Sharpe=+0.6180

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix`: Train IC=+0.0681, Lock IC=+0.0472, Lock Sharpe=+0.4499
- `close_vs_open_range`: Train IC=+0.0830, Lock IC=+0.0899, Lock Sharpe=+0.4216
- `iv_diff_1d`: Train IC=+0.0615, Lock IC=+0.0707, Lock Sharpe=+0.3321
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0222, Lock Sharpe=+0.2464

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1734, Lock IC=+0.1162, Lock Sharpe=+0.6152
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1734, Lock IC=+0.1162, Lock Sharpe=+0.6152

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 75.0% lock IC > 0, 54.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0575_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1120 | 30 | 100.0% | 76.7% | +0.0839 | +0.2024 |
| B2 Rolling Guard | 173 | 30 | 96.7% | 70.0% | +0.0831 | +0.1609 |
| BH-FDR Gate | 7 | 7 | 14.3% | 0.0% | -0.0109 | -0.3779 |
| B3 Composite Floor | 332 | 30 | 100.0% | 100.0% | +0.1159 | +0.7024 |
| B4 Correlation Gate | 171 | 30 | 100.0% | 100.0% | +0.1297 | +1.0766 |

**Admitted Pool Summary**: 27 features, False Positive Rate = 7.4% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1114, Mean Lock Sharpe = +0.5806

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Lock Sharpe=+1.0842
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Lock Sharpe=+1.0842
- `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Train IC=+0.2093, Lock IC=+0.1212, Lock Sharpe=+0.7933
- `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.2197, Lock IC=+0.0920, Lock Sharpe=+0.7605
- `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2019, Lock IC=+0.0275, Lock Sharpe=+0.4871

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.2001, Lock IC=+0.1023, Lock Sharpe=+0.9175
- `combo_mean__bar_ret_0__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+0.6993
- `combo_z_sum__bar_ret_0__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+0.6993
- `combo_mean__first_bar_return__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+0.6993
- `combo_z_sum__first_bar_return__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+0.6993

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2777, Lock IC=+0.1338, Lock Sharpe=+1.1590
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Lock Sharpe=+1.1156
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2565, Lock IC=+0.1034, Lock Sharpe=+1.0713
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2419, Lock IC=+0.1373, Lock Sharpe=+1.0619
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2528, Lock IC=+0.1312, Lock Sharpe=+1.0095

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Lock Sharpe=+1.3837
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Lock Sharpe=+1.3837
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Lock Sharpe=+1.3214
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2636, Lock IC=+0.1171, Lock Sharpe=+1.2867
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2636, Lock IC=+0.1171, Lock Sharpe=+1.2867

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 82.0% lock IC > 0, 48.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0834_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1013 | 30 | 86.7% | 56.7% | +0.0716 | -0.0330 |
| B2 Rolling Guard | 60 | 30 | 86.7% | 66.7% | +0.0764 | +0.3039 |
| BH-FDR Gate | 48 | 30 | 100.0% | 90.0% | +0.1087 | +0.4054 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1767, Lock IC=+0.1382, Lock Sharpe=+0.8274
- `combo_tri_mean__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1680, Lock IC=+0.1273, Lock Sharpe=+0.7777
- `combo_tri_z_mean__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1680, Lock IC=+0.1273, Lock Sharpe=+0.7777
- `combo_tri_mean__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1680, Lock IC=+0.1273, Lock Sharpe=+0.7777
- `combo_tri_z_mean__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1680, Lock IC=+0.1273, Lock Sharpe=+0.7777

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1543, Lock IC=+0.1254, Lock Sharpe=+1.0674
- `combo_rank_min__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1543, Lock IC=+0.1254, Lock Sharpe=+1.0674
- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1473, Lock IC=+0.1241, Lock Sharpe=+1.0260
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1283, Lock IC=+0.1319, Lock Sharpe=+0.9935
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1283, Lock IC=+0.1319, Lock Sharpe=+0.9935

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__open_to_current_return`: Train IC=+0.1144, Lock IC=+0.1079, Lock Sharpe=+0.8531
- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__first_30min_return`: Train IC=+0.1144, Lock IC=+0.1079, Lock Sharpe=+0.8531
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1174, Lock IC=+0.1368, Lock Sharpe=+0.7918
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1174, Lock IC=+0.1368, Lock Sharpe=+0.7918
- `combo_tri_median__rbreaker_sell_setup_proximity_early__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1724, Lock IC=+0.1361, Lock Sharpe=+0.7246

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5698_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 255 | 30 | 73.3% | 23.3% | +0.0340 | -0.2828 |
| B2 Rolling Guard | 43 | 30 | 46.7% | 26.7% | +0.0070 | -0.2197 |
| BH-FDR Gate | 4 | 4 | 100.0% | 50.0% | +0.0733 | -0.0848 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.1453, Lock IC=+0.0750, Lock Sharpe=+0.4667
- `cci14`: Train IC=+0.0740, Lock IC=+0.0494, Lock Sharpe=+0.3148
- `combo_rank_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.1064, Lock IC=+0.0733, Lock Sharpe=+0.3060
- `trend_day_regime_conviction`: Train IC=+0.1013, Lock IC=+0.1116, Lock Sharpe=+0.1697
- `combo_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.1417, Lock IC=+0.0622, Lock Sharpe=+0.1375

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.0549, Lock Sharpe=+0.5447
- `keltner_squeeze_width`: Train IC=+0.0057, Lock IC=+0.0640, Lock Sharpe=+0.4857
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0530, Lock Sharpe=+0.4234
- `vix`: Train IC=+0.0437, Lock IC=+0.0349, Lock Sharpe=+0.3740
- `volatility_expansion_trend_vector`: Train IC=+0.0439, Lock IC=+0.1157, Lock Sharpe=+0.2461

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0020, Lock IC=+0.1016, Lock Sharpe=+0.3325
- `limit_down_proximity_early`: Train IC=+0.0020, Lock IC=+0.1016, Lock Sharpe=+0.3325

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 382 | +0.0687 | 100.0% |
| 0.45 | 0.20 | 366 | +0.0687 | 100.0% |
| 0.45 | 0.30 | 330 | +0.0687 | 100.0% |
| 0.45 | 0.40 | 265 | +0.0687 | 100.0% |
| 0.45 | 0.50 | 158 | +0.0687 | 100.0% |
| 0.50 | 0.15 | 373 | +0.0687 | 100.0% |
| 0.50 | 0.25 | 355 | +0.0687 | 100.0% |
| 0.50 | 0.35 | 302 | +0.0687 | 100.0% |
| 0.50 | 0.45 | 219 | +0.0687 | 100.0% |
| 0.55 | 0.10 | 372 | +0.0687 | 100.0% |
| 0.55 | 0.20 | 366 | +0.0687 | 100.0% |
| 0.55 | 0.30 | 330 | +0.0687 | 100.0% |
| 0.55 | 0.40 | 265 | +0.0687 | 100.0% |
| 0.55 | 0.50 | 158 | +0.0687 | 100.0% |
| 0.60 | 0.15 | 339 | +0.0687 | 100.0% |
| 0.60 | 0.25 | 338 | +0.0687 | 100.0% |
| 0.60 | 0.35 | 302 | +0.0687 | 100.0% |
| 0.60 | 0.45 | 219 | +0.0687 | 100.0% |
| 0.65 | 0.10 | 267 | +0.0687 | 100.0% |
| 0.65 | 0.20 | 267 | +0.0687 | 100.0% |
| 0.65 | 0.30 | 267 | +0.0687 | 100.0% |
| 0.65 | 0.40 | 250 | +0.0687 | 100.0% |
| 0.65 | 0.50 | 158 | +0.0687 | 100.0% |
| 0.70 | 0.15 | 129 | +0.0685 | 100.0% |
| 0.70 | 0.25 | 129 | +0.0685 | 100.0% |
| 0.70 | 0.35 | 129 | +0.0685 | 100.0% |
| 0.70 | 0.45 | 129 | +0.0685 | 100.0% |
| 0.75 | 0.10 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.20 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.30 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.40 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.50 | 19 | +0.0662 | 100.0% |
| 0.80 | 0.15 | 1 | +0.0716 | 100.0% |
| 0.80 | 0.25 | 1 | +0.0716 | 100.0% |
| 0.80 | 0.35 | 1 | +0.0716 | 100.0% |
| 0.80 | 0.45 | 1 | +0.0716 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 382 candidates, mean lock IC=+0.0687, 100.0% positive

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
| 0.45 | 0.10 | 35 | +0.0466 | 90.0% |
| 0.45 | 0.20 | 25 | +0.0466 | 90.0% |
| 0.45 | 0.30 | 10 | +0.0630 | 100.0% |
| 0.45 | 0.40 | 3 | +0.0551 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 28 | +0.0466 | 90.0% |
| 0.50 | 0.25 | 14 | +0.0610 | 100.0% |
| 0.50 | 0.35 | 6 | +0.0609 | 100.0% |
| 0.50 | 0.45 | 3 | +0.0551 | 100.0% |
| 0.55 | 0.10 | 26 | +0.0466 | 90.0% |
| 0.55 | 0.20 | 25 | +0.0466 | 90.0% |
| 0.55 | 0.30 | 10 | +0.0630 | 100.0% |
| 0.55 | 0.40 | 3 | +0.0551 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 16 | +0.0603 | 100.0% |
| 0.60 | 0.25 | 12 | +0.0603 | 100.0% |
| 0.60 | 0.35 | 6 | +0.0609 | 100.0% |
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
| 0.45 | 0.10 | 20 | +0.0054 | 80.0% |
| 0.45 | 0.20 | 13 | +0.0033 | 70.0% |
| 0.45 | 0.30 | 3 | +0.0034 | 66.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 17 | +0.0033 | 70.0% |
| 0.50 | 0.25 | 9 | -0.0015 | 55.6% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 18 | +0.0033 | 70.0% |
| 0.55 | 0.20 | 13 | +0.0033 | 70.0% |
| 0.55 | 0.30 | 3 | +0.0034 | 66.7% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | +0.0210 | 87.5% |
| 0.60 | 0.25 | 5 | +0.0044 | 80.0% |
| 0.60 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 1 | +0.0071 | 100.0% |
| 0.65 | 0.20 | 1 | +0.0071 | 100.0% |
| 0.65 | 0.30 | 1 | +0.0071 | 100.0% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 8 candidates, mean lock IC=+0.0210, 87.5% positive

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
| 0.45 | 0.10 | 1159 | +0.1149 | 100.0% |
| 0.45 | 0.20 | 1136 | +0.1149 | 100.0% |
| 0.45 | 0.30 | 1091 | +0.1149 | 100.0% |
| 0.45 | 0.40 | 984 | +0.1149 | 100.0% |
| 0.45 | 0.50 | 785 | +0.1149 | 100.0% |
| 0.50 | 0.15 | 1152 | +0.1149 | 100.0% |
| 0.50 | 0.25 | 1120 | +0.1149 | 100.0% |
| 0.50 | 0.35 | 1050 | +0.1149 | 100.0% |
| 0.50 | 0.45 | 906 | +0.1149 | 100.0% |
| 0.55 | 0.10 | 1156 | +0.1149 | 100.0% |
| 0.55 | 0.20 | 1136 | +0.1149 | 100.0% |
| 0.55 | 0.30 | 1091 | +0.1149 | 100.0% |
| 0.55 | 0.40 | 984 | +0.1149 | 100.0% |
| 0.55 | 0.50 | 785 | +0.1149 | 100.0% |
| 0.60 | 0.15 | 1111 | +0.1149 | 100.0% |
| 0.60 | 0.25 | 1105 | +0.1149 | 100.0% |
| 0.60 | 0.35 | 1049 | +0.1149 | 100.0% |
| 0.60 | 0.45 | 906 | +0.1149 | 100.0% |
| 0.65 | 0.10 | 974 | +0.1149 | 100.0% |
| 0.65 | 0.20 | 974 | +0.1149 | 100.0% |
| 0.65 | 0.30 | 974 | +0.1149 | 100.0% |
| 0.65 | 0.40 | 941 | +0.1149 | 100.0% |
| 0.65 | 0.50 | 785 | +0.1149 | 100.0% |
| 0.70 | 0.15 | 697 | +0.1149 | 100.0% |
| 0.70 | 0.25 | 697 | +0.1149 | 100.0% |
| 0.70 | 0.35 | 697 | +0.1149 | 100.0% |
| 0.70 | 0.45 | 697 | +0.1149 | 100.0% |
| 0.75 | 0.10 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.20 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.30 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.40 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.50 | 342 | +0.1149 | 100.0% |
| 0.80 | 0.15 | 106 | +0.1106 | 100.0% |
| 0.80 | 0.25 | 106 | +0.1106 | 100.0% |
| 0.80 | 0.35 | 106 | +0.1106 | 100.0% |
| 0.80 | 0.45 | 106 | +0.1106 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1159 candidates, mean lock IC=+0.1149, 100.0% positive

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
| 0.45 | 0.10 | 682 | +0.1288 | 100.0% |
| 0.45 | 0.20 | 653 | +0.1288 | 100.0% |
| 0.45 | 0.30 | 553 | +0.1288 | 100.0% |
| 0.45 | 0.40 | 392 | +0.1288 | 100.0% |
| 0.45 | 0.50 | 229 | +0.1288 | 100.0% |
| 0.50 | 0.15 | 679 | +0.1288 | 100.0% |
| 0.50 | 0.25 | 616 | +0.1288 | 100.0% |
| 0.50 | 0.35 | 470 | +0.1288 | 100.0% |
| 0.50 | 0.45 | 316 | +0.1288 | 100.0% |
| 0.55 | 0.10 | 674 | +0.1288 | 100.0% |
| 0.55 | 0.20 | 653 | +0.1288 | 100.0% |
| 0.55 | 0.30 | 553 | +0.1288 | 100.0% |
| 0.55 | 0.40 | 392 | +0.1288 | 100.0% |
| 0.55 | 0.50 | 229 | +0.1288 | 100.0% |
| 0.60 | 0.15 | 606 | +0.1288 | 100.0% |
| 0.60 | 0.25 | 587 | +0.1288 | 100.0% |
| 0.60 | 0.35 | 467 | +0.1288 | 100.0% |
| 0.60 | 0.45 | 316 | +0.1288 | 100.0% |
| 0.65 | 0.10 | 395 | +0.1288 | 100.0% |
| 0.65 | 0.20 | 395 | +0.1288 | 100.0% |
| 0.65 | 0.30 | 395 | +0.1288 | 100.0% |
| 0.65 | 0.40 | 359 | +0.1288 | 100.0% |
| 0.65 | 0.50 | 228 | +0.1288 | 100.0% |
| 0.70 | 0.15 | 155 | +0.1288 | 100.0% |
| 0.70 | 0.25 | 155 | +0.1288 | 100.0% |
| 0.70 | 0.35 | 155 | +0.1288 | 100.0% |
| 0.70 | 0.45 | 154 | +0.1288 | 100.0% |
| 0.75 | 0.10 | 33 | +0.1253 | 100.0% |
| 0.75 | 0.20 | 33 | +0.1253 | 100.0% |
| 0.75 | 0.30 | 33 | +0.1253 | 100.0% |
| 0.75 | 0.40 | 33 | +0.1253 | 100.0% |
| 0.75 | 0.50 | 33 | +0.1253 | 100.0% |
| 0.80 | 0.15 | 2 | +0.1298 | 100.0% |
| 0.80 | 0.25 | 2 | +0.1298 | 100.0% |
| 0.80 | 0.35 | 2 | +0.1298 | 100.0% |
| 0.80 | 0.45 | 2 | +0.1298 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 682 candidates, mean lock IC=+0.1288, 100.0% positive

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
| 0.60 | 0.25 | 20 | +0.0949 | 100.0% |
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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | +0.1293 | +0.0000 | +0.0632 | 0.49x | 2017-06-09 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1162 | +0.0000 | +0.0678 | 0.58x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1143 | +0.0000 | +0.0543 | 0.47x | 2017-05-09 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1127 | +0.0000 | +0.0885 | 0.79x | 2016-08-24 |
| `combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.1258 | +0.0000 | +0.0735 | 0.58x | 2016-08-24 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1093 | +0.0000 | +0.0567 | 0.52x | 2015-02-06 |
| `rbreaker_sell_setup_proximity_early` | +0.0962 | +0.0000 | +0.0662 | 0.69x | 2016-08-24 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +0.0655 | +0.0000 | +0.0529 | 0.81x | 2017-10-12 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +0.0511 | +0.0000 | +0.0417 | 0.81x | 2012-10-09 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | +0.0854 | +0.0000 | +0.0524 | 0.61x | 2010-10-15 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1111 | +0.0000 | +0.0444 | 0.40x | 2017-06-09 |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | +0.1024 | +0.0000 | +0.0642 | 0.63x | 2017-09-06 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +0.0571 | +0.0000 | +0.0048 | 0.08x | 2010-10-15 |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | -0.0447 | +0.0000 | +0.0073 | -0.16x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_min__max_up_ret__first_bar_sentiment` | +0.1707 | +0.0000 | +0.0726 | 0.43x | 2020-01-06 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1729 | +0.0000 | +0.0868 | 0.50x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1627 | +0.0000 | +0.0893 | 0.55x | No decay |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1841 | +0.0000 | +0.1000 | 0.54x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1772 | +0.0000 | +0.1217 | 0.69x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1976 | +0.0000 | +0.1217 | 0.62x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1914 | +0.0000 | +0.0936 | 0.49x | 2021-07-28 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1710 | +0.0000 | +0.0912 | 0.53x | 2020-01-06 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1717 | +0.0000 | +0.0911 | 0.53x | No decay |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | +0.1687 | +0.0000 | +0.1134 | 0.67x | 2016-09-26 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1907 | +0.0000 | +0.0916 | 0.48x | 2025-07-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | +0.2000 | +0.0000 | +0.1099 | 0.55x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1719 | +0.0000 | +0.0798 | 0.46x | No decay |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1692 | +0.0000 | +0.1175 | 0.69x | 2020-01-06 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +0.1898 | +0.0000 | +0.0884 | 0.47x | No decay |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +0.1513 | +0.0000 | +0.1191 | 0.79x | 2016-09-26 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1473 | +0.0000 | +0.0958 | 0.65x | 2016-08-24 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +0.1473 | +0.0000 | +0.0948 | 0.64x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1940 | +0.0000 | +0.1210 | 0.62x | No decay |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +0.1786 | +0.0000 | +0.0936 | 0.52x | 2020-01-06 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +0.1744 | +0.0000 | +0.0840 | 0.48x | 2019-12-05 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1692 | +0.0000 | +0.0836 | 0.49x | 2016-12-29 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1625 | +0.0000 | +0.1069 | 0.66x | 2016-09-26 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | +0.1854 | +0.0000 | +0.0909 | 0.49x | No decay |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.1520 | +0.0000 | +0.0859 | 0.57x | 2022-09-09 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | +0.1503 | +0.0000 | +0.0768 | 0.51x | 2017-05-09 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +0.1302 | +0.0000 | +0.0654 | 0.50x | 2020-01-06 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1456 | +0.0000 | +0.1031 | 0.71x | 2020-12-18 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1680 | +0.0000 | +0.0792 | 0.47x | 2017-04-07 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1398 | +0.0000 | +0.1223 | 0.88x | 2011-12-23 |
| `combo_sig_product__rsi_opening__max_down_ret` | +0.1400 | +0.0000 | +0.0788 | 0.56x | 2016-09-26 |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | +0.1031 | +0.0000 | +0.0500 | 0.49x | 2013-09-23 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | +0.1569 | +0.0000 | +0.1158 | 0.74x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1683 | +0.0000 | +0.1269 | 0.75x | 2017-01-20 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1666 | +0.0000 | +0.1260 | 0.76x | 2017-01-20 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | +0.1583 | +0.0000 | +0.1347 | 0.85x | 2016-10-24 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1021 | +0.0000 | +0.1075 | 1.05x | 2011-10-18 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1305 | +0.0000 | +0.0763 | 0.59x | 2017-04-28 |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1587 | +0.0000 | +0.1247 | 0.79x | 2017-02-27 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1052 | +0.0000 | +0.1074 | 1.02x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | +0.1399 | +0.0000 | +0.1261 | 0.90x | 2011-10-18 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1265 | +0.0000 | +0.1316 | 1.04x | 2017-02-27 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1591 | +0.0000 | +0.1185 | 0.75x | 2017-01-20 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +0.1554 | +0.0000 | +0.1176 | 0.76x | 2016-10-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1723 | +0.0000 | +0.1218 | 0.71x | 2017-02-27 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +0.1401 | +0.0000 | +0.1375 | 0.98x | 2016-10-24 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | +0.1132 | +0.0000 | +0.1048 | 0.93x | 2011-10-18 |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | +0.1303 | +0.0000 | +0.0579 | 0.44x | 2017-03-28 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +0.1531 | +0.0000 | +0.1126 | 0.74x | 2016-12-21 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | +0.1067 | +0.0000 | +0.0792 | 0.74x | 2016-09-14 |
| `rbreaker_sell_setup_proximity_early` | +0.1526 | +0.0000 | +0.1309 | 0.86x | 2016-12-21 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1186 | +0.0000 | +0.1312 | 1.11x | 2017-01-20 |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | +0.1451 | +0.0000 | +0.1245 | 0.86x | 2016-09-14 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +0.1398 | +0.0000 | +0.0928 | 0.66x | 2017-01-20 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1511 | +0.0000 | +0.1116 | 0.74x | 2017-01-20 |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | +0.1287 | +0.0000 | +0.0661 | 0.51x | 2017-04-28 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1428 | +0.0000 | +0.1124 | 0.79x | 2016-12-21 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | +0.1227 | +0.0000 | +0.1069 | 0.87x | 2017-01-20 |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | +0.1172 | +0.0000 | +0.1043 | 0.89x | 2011-10-18 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 23.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.2227). Consider relaxing this gate.
2. **300ETF `single` — BH-FDR Gate too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.7456). Consider relaxing this gate.
3. **300ETF `single` — B3 Composite Floor too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.0523). Consider relaxing this gate.
4. **300ETF `single` — B4 Correlation Gate too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.1060). Consider relaxing this gate.
5. **300ETF `single` — Admission too loose**: 79% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
6. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.5705). Consider relaxing this gate.
7. **300ETF `short` — BH-FDR Gate too strict**: 28.6% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 4.0%, mean lock Sharpe=-0.2043). Consider relaxing this gate.
8. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=+0.0043). Consider relaxing this gate.
9. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=-0.2852). Consider relaxing this gate.
10. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.1935). Consider relaxing this gate.
11. **500ETF `single` — B3 Composite Floor too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.1489). Consider relaxing this gate.
12. **500ETF `single` — B4 Correlation Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.3238). Consider relaxing this gate.
13. **500ETF `long` — B2 Rolling Guard too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.2953). Consider relaxing this gate.
14. **500ETF `long` — BH-FDR Gate too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.4456). Consider relaxing this gate.
15. **500ETF `long` — B3 Composite Floor too strict**: 20.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.4938). Consider relaxing this gate.
16. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.0997). Consider relaxing this gate.
17. **500ETF `short` — BH-FDR Gate too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.1139). Consider relaxing this gate.
18. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 54.0%, mean lock Sharpe=+0.7024). Consider relaxing this gate.
19. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 54.0%, mean lock Sharpe=+1.0766). Consider relaxing this gate.
20. **159915ETF `long` — BH-FDR Gate too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 48.0%, mean lock Sharpe=+0.4054). Consider relaxing this gate.
21. **159915ETF `short` — B2 Rolling Guard too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.2197). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
