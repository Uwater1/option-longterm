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

### 300ETF — `single` (Full Model Lockbox IC: +0.0691, Sharpe: +0.5212)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.1225 | +0.0632 | +0.0632 | +0.3639 | 87.22 | +12.9 | 1.61x | -0.0015 | +0.0723 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1113 | +0.0679 | +0.0679 | +1.0056 | 82.95 | +22.7 | 2.83x | -0.0006 | +0.1608 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1119 | +0.0543 | +0.0543 | +0.3473 | 86.37 | +13.2 | 1.64x | -0.0029 | +0.0182 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1132 | +0.0876 | +0.0876 | +0.7186 | 86.94 | +18.0 | 2.24x | +0.0031 | +0.0465 |
| `combo_rank_min__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1129 | +0.0728 | +0.0728 | +0.2811 | 86.37 | +11.7 | 1.46x | +0.0010 | +0.0731 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0872 | +0.0567 | +0.0567 | +0.4294 | 86.37 | +12.8 | 1.60x | +0.0018 | +0.1850 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0965 | +0.0662 | +0.0662 | +0.0044 | 84.09 | +8.1 | 1.01x | -0.0044 | +0.0491 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0742 | +0.0529 | +0.0529 | +0.5709 | 81.81 | +14.3 | 1.79x | -0.0004 | +0.2514 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0660 | +0.0417 | +0.0417 | -0.0329 | 82.38 | +7.5 | 0.94x | +0.0002 | +0.1210 |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0917 | +0.0524 | +0.0524 | +0.2193 | 84.09 | +10.7 | 1.33x | +0.0017 | +0.0465 |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0833 | +0.0444 | +0.0444 | -0.2618 | 88.93 | +4.8 | 0.61x | -0.0005 | +0.0781 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0680 | +0.0048 | +0.0048 | -0.5873 | 75.25 | +3.0 | 0.38x | +0.0000 | +0.0000 |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | -0.0541 | +0.0082 | +0.0082 | -0.3794 | 68.41 | +4.0 | 0.50x | +0.0002 | +0.0073 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1230, Sharpe: +0.7669)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1749 | +0.0868 | +0.0868 | +0.4062 | 86.65 | +14.1 | 1.76x | -0.0002 | +0.0526 |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1795 | +0.1000 | +0.1000 | +0.5841 | 85.23 | +19.8 | 2.47x | +0.0002 | -0.3713 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1544 | +0.1215 | +0.1215 | +0.9205 | 88.65 | +23.6 | 2.96x | +0.0013 | +0.0341 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1763 | +0.1217 | +0.1217 | +0.8196 | 89.22 | +21.2 | 2.65x | +0.0012 | +0.1170 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1634 | +0.0936 | +0.0936 | +0.4546 | 87.22 | +16.3 | 2.03x | -0.0001 | -0.0148 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1711 | +0.0913 | +0.0913 | +0.8496 | 81.24 | +25.4 | 3.18x | -0.0004 | -0.1265 |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1310 | +0.1134 | +0.1134 | +1.1317 | 87.51 | +28.6 | 3.57x | +0.0010 | +0.1662 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1850 | +0.0916 | +0.0916 | +0.6369 | 85.23 | +18.2 | 2.27x | -0.0000 | -0.0898 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | Volatility & Oscillators | +1 | +0.1716 | +0.1099 | +0.1099 | +0.6820 | 90.64 | +17.8 | 2.22x | +0.0002 | +0.0620 |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Other Technical | +1 | +0.1585 | +0.0823 | +0.0823 | +0.1403 | 86.94 | +10.3 | 1.29x | -0.0009 | +0.0085 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1484 | +0.1175 | +0.1175 | +0.4851 | 85.51 | +15.0 | 1.87x | +0.0016 | -0.0058 |
| `combo_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1702 | +0.0726 | +0.0726 | -0.7944 | 68.98 | -4.1 | -0.51x | -0.0003 | +0.0084 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1602 | +0.0884 | +0.0884 | +0.4616 | 88.36 | +15.8 | 1.98x | +0.0000 | -0.0366 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1685 | +0.0893 | +0.0893 | +0.1304 | 74.40 | +10.5 | 1.32x | +0.0005 | +0.0588 |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1207 | +0.1199 | +0.1199 | +1.1425 | 84.66 | +28.0 | 3.50x | +0.0008 | +0.0341 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1269 | +0.0958 | +0.0958 | +0.2125 | 80.10 | +12.1 | 1.51x | +0.0009 | +0.0043 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1458 | +0.0948 | +0.0948 | +0.9751 | 79.53 | +28.1 | 3.51x | +0.0006 | +0.0164 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1720 | +0.1216 | +0.1216 | +0.9299 | 84.09 | +26.5 | 3.31x | +0.0009 | -0.0479 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1456 | +0.0787 | +0.0787 | +0.4560 | 78.39 | +16.3 | 2.04x | +0.0005 | -0.0067 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | Intraday Range Momentum | +1 | +0.1595 | +0.0936 | +0.0936 | +0.0056 | 91.50 | +8.1 | 1.01x | -0.0003 | -0.0501 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1722 | +0.0840 | +0.0840 | +0.5104 | 87.22 | +16.4 | 2.06x | +0.0001 | -0.0408 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Other Technical | +1 | +0.1401 | +0.0836 | +0.0836 | +0.2749 | 86.65 | +11.9 | 1.49x | +0.0003 | -0.0058 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1405 | +0.1069 | +0.1069 | +0.5237 | 86.94 | +18.3 | 2.28x | +0.0003 | -0.0222 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1590 | +0.0909 | +0.0909 | +0.6878 | 89.79 | +16.6 | 2.08x | -0.0007 | +0.0355 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1553 | +0.0789 | +0.0789 | +0.3856 | 75.54 | +16.0 | 1.99x | -0.0003 | -0.0877 |
| `combo_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1626 | +0.0765 | +0.0765 | +0.4322 | 84.37 | +15.8 | 1.98x | -0.0002 | -0.0636 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1362 | +0.0768 | +0.0768 | +0.3491 | 84.37 | +12.8 | 1.60x | -0.0002 | +0.0012 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | Gap / Overnight Reversal | +1 | +0.1323 | +0.0654 | +0.0654 | +0.3641 | 88.36 | +13.0 | 1.63x | -0.0000 | +0.0604 |
| `combo_sig_product__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1454 | +0.1031 | +0.1031 | +0.6726 | 89.50 | +17.2 | 2.15x | +0.0005 | -0.0598 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1603 | +0.0792 | +0.0792 | +0.3953 | 81.24 | +15.8 | 1.97x | +0.0002 | -0.0341 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1369 | +0.1223 | +0.1223 | +0.4818 | 82.38 | +17.5 | 2.19x | +0.0010 | -0.0898 |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | Volatility & Oscillators | +1 | +0.1119 | +0.0500 | +0.0500 | +0.3938 | 83.52 | +16.0 | 2.00x | +0.0004 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1472, Sharpe: +1.4412)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1495 | +0.1158 | +0.1158 | +1.5577 | 87.51 | +37.7 | 4.71x | -0.0004 | +0.0031 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1603 | +0.1260 | +0.1260 | +1.3254 | 81.24 | +37.4 | 4.67x | +0.0001 | -0.0057 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1415 | +0.1345 | +0.1345 | +1.2143 | 83.52 | +35.4 | 4.42x | +0.0001 | -0.0955 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1201 | +0.1316 | +0.1316 | +1.2548 | 76.11 | +39.2 | 4.90x | +0.0009 | +0.0123 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1072 | +0.1075 | +0.1075 | +0.3554 | 80.10 | +16.3 | 2.04x | +0.0000 | -0.0685 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1649 | +0.1220 | +0.1220 | +1.3232 | 85.80 | +38.0 | 4.75x | -0.0011 | +0.0452 |
| `combo_min__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.0909 | +0.0985 | +0.0985 | +0.5273 | 77.82 | +19.8 | 2.47x | +0.0002 | -0.0009 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1078 | +0.1077 | +0.1077 | +0.3400 | 80.67 | +15.9 | 1.99x | +0.0008 | +0.0356 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1414 | +0.1261 | +0.1261 | +0.9894 | 80.67 | +31.7 | 3.97x | +0.0003 | +0.0597 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1383 | +0.1176 | +0.1176 | +1.3628 | 86.37 | +39.3 | 4.92x | -0.0005 | -0.0157 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1388 | +0.1268 | +0.1268 | +1.0353 | 80.10 | +32.9 | 4.12x | -0.0002 | +0.0597 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1209 | +0.1375 | +0.1375 | +1.5481 | 86.94 | +38.7 | 4.84x | +0.0010 | +0.0716 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1187 | +0.0763 | +0.0763 | +0.4953 | 70.98 | +16.6 | 2.08x | -0.0010 | -0.0101 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1227 | +0.1048 | +0.1048 | +0.4833 | 78.96 | +19.4 | 2.42x | +0.0003 | -0.0696 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1277 | +0.1126 | +0.1126 | +0.7612 | 84.37 | +23.9 | 2.99x | +0.0000 | -0.0135 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Other Technical | +1 | +0.1333 | +0.1104 | +0.1104 | +1.1839 | 90.64 | +30.1 | 3.76x | -0.0005 | +0.0476 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.0800 | +0.0791 | +0.0791 | -0.4350 | 74.97 | +1.6 | 0.19x | -0.0004 | -0.0314 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1455 | +0.1309 | +0.1309 | +0.9097 | 82.95 | +29.3 | 3.66x | +0.0000 | -0.0786 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1127 | +0.1302 | +0.1302 | +0.6763 | 83.52 | +22.4 | 2.80x | +0.0021 | -0.0642 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1211 | +0.0928 | +0.0928 | +0.3022 | 81.81 | +14.4 | 1.79x | -0.0000 | -0.0622 |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1379 | +0.1116 | +0.1116 | +0.7844 | 88.65 | +23.3 | 2.91x | +0.0004 | +0.0035 |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | Gap / Overnight Reversal | +1 | +0.1191 | +0.0641 | +0.0641 | +0.3448 | 68.70 | +14.4 | 1.80x | -0.0019 | +0.0620 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1275 | +0.1111 | +0.1111 | +0.1333 | 78.39 | +11.0 | 1.37x | -0.0001 | -0.0380 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1201 | +0.1069 | +0.1069 | +0.9698 | 86.08 | +27.6 | 3.44x | +0.0000 | +0.0883 |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | Other Technical | +1 | +0.1010 | +0.1043 | +0.1043 | +0.6683 | 83.52 | +23.1 | 2.88x | +0.0001 | +0.0709 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 70.0% lock IC > 0, 26.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3809_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1042 | 30 | 100.0% | 83.3% | +0.0586 | +0.2412 |
| B2 Rolling Guard | 78 | 30 | 90.0% | 56.7% | +0.0358 | -0.0426 |
| BH-FDR Gate | 12 | 12 | 75.0% | 16.7% | +0.0233 | -0.3393 |
| B3 Composite Floor | 196 | 30 | 100.0% | 100.0% | +0.0653 | +0.4178 |
| B4 Correlation Gate | 27 | 27 | 100.0% | 96.3% | +0.0659 | +0.3760 |

**Admitted Pool Summary**: 13 features, False Positive Rate = 30.8% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0518, Mean Lock Sharpe = +0.2344

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.1991, Lock IC=+0.0524, Lock Sharpe=+0.7239
- `combo_mean__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Lock Sharpe=+0.5376
- `combo_z_sum__first_bar_return__bar_body_rng_0`: Train IC=+0.1820, Lock IC=+0.0610, Lock Sharpe=+0.5376
- `combo_mean__bar_ret_0__bar_body_rng_0`: Train IC=+0.1818, Lock IC=+0.0611, Lock Sharpe=+0.5376
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Lock Sharpe=+0.5289

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1331, Lock IC=+0.0625, Lock Sharpe=+0.5170
- `combo_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1322, Lock IC=+0.0684, Lock Sharpe=+0.5170
- `combo_z_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1322, Lock IC=+0.0684, Lock Sharpe=+0.5170
- `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__opening_drive_thrust_ratio`: Train IC=+0.1344, Lock IC=+0.0481, Lock Sharpe=+0.4805
- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1502, Lock IC=+0.0543, Lock Sharpe=+0.4621

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.0951, Lock IC=+0.0600, Lock Sharpe=+0.6245
- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.0951, Lock IC=+0.0600, Lock Sharpe=+0.6245

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2370, Lock IC=+0.0693, Lock Sharpe=+0.5695
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2370, Lock IC=+0.0693, Lock Sharpe=+0.5695
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2366, Lock IC=+0.0693, Lock Sharpe=+0.5695
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2366, Lock IC=+0.0693, Lock Sharpe=+0.5695
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Lock Sharpe=+0.5292

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0937, Lock Sharpe=+1.0629
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2691, Lock IC=+0.0706, Lock Sharpe=+0.8555
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1929, Lock IC=+0.0529, Lock Sharpe=+0.5709
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.0755, Lock Sharpe=+0.5654
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`: Train IC=+0.2664, Lock IC=+0.0723, Lock Sharpe=+0.4930

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

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4730_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 493 | 30 | 56.7% | 36.7% | +0.0189 | -0.2417 |
| B2 Rolling Guard | 67 | 30 | 53.3% | 10.0% | -0.0040 | -0.3708 |
| BH-FDR Gate | 21 | 21 | 95.2% | 85.7% | +0.0575 | +0.2273 |
| B3 Composite Floor | 5 | 5 | 80.0% | 40.0% | +0.0296 | -0.1028 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__volume_weighted_momentum_acceleration__max_down_ret`: Train IC=+0.1031, Lock IC=+0.0668, Lock Sharpe=+0.4578
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1299, Lock IC=+0.0763, Lock Sharpe=+0.4489
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1215, Lock IC=+0.0581, Lock Sharpe=+0.3630
- `limit_down_proximity_early`: Train IC=+0.1147, Lock IC=+0.0401, Lock Sharpe=+0.3409
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1147, Lock IC=+0.0401, Lock Sharpe=+0.3409

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__opening_drive_thrust_ratio__max_down_ret`: Train IC=+0.0394, Lock IC=+0.0505, Lock Sharpe=+0.6099
- `combo_clamp_diff__volume_surge_direction__volume_weighted_momentum_acceleration`: Train IC=+0.0369, Lock IC=+0.0598, Lock Sharpe=+0.2599
- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0258, Lock Sharpe=+0.2046

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1154, Lock IC=+0.0716, Lock Sharpe=+0.5842
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0686, Lock IC=+0.0655, Lock Sharpe=+0.5501
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0648, Lock IC=+0.0618, Lock Sharpe=+0.4934
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0648, Lock IC=+0.0618, Lock Sharpe=+0.4934
- `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0896, Lock IC=+0.0585, Lock Sharpe=+0.4808

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1819, Lock IC=+0.0504, Lock Sharpe=+0.1424
- `combo_z_sum__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1819, Lock IC=+0.0504, Lock Sharpe=+0.1424

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5552_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 704 | 30 | 100.0% | 76.7% | +0.0295 | +0.1679 |
| B2 Rolling Guard | 31 | 30 | 36.7% | 6.7% | +0.0006 | -0.3922 |
| BH-FDR Gate | 2 | 2 | 50.0% | 0.0% | +0.0015 | -0.2219 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1396, Lock IC=+0.0321, Lock Sharpe=+0.5189
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.1615, Lock IC=+0.0418, Lock Sharpe=+0.4378
- `combo_max__bar_vol_4__rsi21`: Train IC=+0.1374, Lock IC=+0.0353, Lock Sharpe=+0.4070
- `combo_mean__bar_vol_4__first_bar_volume`: Train IC=+0.1418, Lock IC=+0.0144, Lock Sharpe=+0.3220
- `combo_z_sum__bar_vol_4__first_bar_volume`: Train IC=+0.1418, Lock IC=+0.0144, Lock Sharpe=+0.3220

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.1441, Lock IC=+0.0059, Lock Sharpe=+0.1981
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1441, Lock IC=+0.0059, Lock Sharpe=+0.1981

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

_Null Baseline (un-gated candidate pool): 73.0% lock IC > 0, 48.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0420_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1680 | 30 | 100.0% | 100.0% | +0.0914 | +0.5687 |
| B2 Rolling Guard | 104 | 30 | 83.3% | 53.3% | +0.0362 | -0.0150 |
| BH-FDR Gate | 9 | 9 | 88.9% | 0.0% | +0.0161 | -0.5768 |
| B3 Composite Floor | 434 | 30 | 100.0% | 100.0% | +0.1032 | +0.5522 |
| B4 Correlation Gate | 432 | 30 | 100.0% | 100.0% | +0.1073 | +0.7132 |

**Admitted Pool Summary**: 32 features, False Positive Rate = 3.1% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0937, Mean Lock Sharpe = +0.4900

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2312, Lock IC=+0.1016, Lock Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Lock Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Lock Sharpe=+0.9464
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.2819, Lock IC=+0.1134, Lock Sharpe=+0.8586
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2910, Lock IC=+0.1185, Lock Sharpe=+0.8115

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__max_up_ret__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1298, Lock IC=+0.0164, Lock Sharpe=+0.4949
- `combo_tri_min__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.1705, Lock IC=+0.0264, Lock Sharpe=+0.3458
- `combo_tri_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.1508, Lock IC=+0.0731, Lock Sharpe=+0.2561
- `combo_tri_z_mean__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__trend_day_regime_conviction`: Train IC=+0.1508, Lock IC=+0.0731, Lock Sharpe=+0.2561
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1668, Lock IC=+0.0995, Lock Sharpe=+0.1837

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Lock Sharpe=+1.1317
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2863, Lock IC=+0.1160, Lock Sharpe=+1.0243
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.3150, Lock IC=+0.1141, Lock Sharpe=+0.9327

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 74.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4394_

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

_Null Baseline (un-gated candidate pool): 71.0% lock IC > 0, 59.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.2145_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1119 | 30 | 100.0% | 83.3% | +0.0861 | +0.5148 |
| B2 Rolling Guard | 174 | 30 | 96.7% | 73.3% | +0.0831 | +0.4496 |
| BH-FDR Gate | 4 | 4 | 0.0% | 0.0% | -0.0153 | +0.1952 |
| B3 Composite Floor | 279 | 30 | 100.0% | 100.0% | +0.1191 | +1.0165 |
| B4 Correlation Gate | 141 | 30 | 100.0% | 100.0% | +0.1279 | +1.3719 |

**Admitted Pool Summary**: 25 features, False Positive Rate = 4.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1116, Mean Lock Sharpe = +0.8087

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Lock Sharpe=+1.3789
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2180, Lock IC=+0.1373, Lock Sharpe=+1.3789
- `combo_min__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.1810, Lock IC=+0.0962, Lock Sharpe=+1.2658
- `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.2197, Lock IC=+0.0920, Lock Sharpe=+1.0913
- `combo_rank_min__opening_drive_thrust_ratio__bar_body_rng_0`: Train IC=+0.2007, Lock IC=+0.1168, Lock Sharpe=+0.7399

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.2001, Lock IC=+0.1023, Lock Sharpe=+1.2236
- `combo_mean__bar_ret_0__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+1.0264
- `combo_z_sum__bar_ret_0__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+1.0264
- `combo_mean__first_bar_return__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+1.0264
- `combo_z_sum__first_bar_return__volatility_expansion_trend_vector`: Train IC=+0.1785, Lock IC=+0.1153, Lock Sharpe=+1.0264

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2646, Lock IC=+0.1269, Lock Sharpe=+1.6324
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2777, Lock IC=+0.1338, Lock Sharpe=+1.4166
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Lock Sharpe=+1.4133
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2419, Lock IC=+0.1373, Lock Sharpe=+1.3304
- `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2517, Lock IC=+0.1333, Lock Sharpe=+1.3096

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Lock Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Lock Sharpe=+1.6742
- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Lock Sharpe=+1.6287
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Lock Sharpe=+1.6287
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2840, Lock IC=+0.1129, Lock Sharpe=+1.5874

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
- `combo_rel_diff__morning_volume_weighted_momentum__shaved_bar_trend_conviction`: Train IC=+0.0703, Lock IC=+0.0149, Lock Sharpe=+0.3049
- `combo_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.1417, Lock IC=+0.0622, Lock Sharpe=+0.2941

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
| 0.45 | 0.10 | 305 | +0.0687 | 100.0% |
| 0.45 | 0.20 | 289 | +0.0687 | 100.0% |
| 0.45 | 0.30 | 253 | +0.0687 | 100.0% |
| 0.45 | 0.40 | 216 | +0.0687 | 100.0% |
| 0.45 | 0.50 | 146 | +0.0687 | 100.0% |
| 0.50 | 0.15 | 296 | +0.0687 | 100.0% |
| 0.50 | 0.25 | 278 | +0.0687 | 100.0% |
| 0.50 | 0.35 | 238 | +0.0687 | 100.0% |
| 0.50 | 0.45 | 191 | +0.0687 | 100.0% |
| 0.55 | 0.10 | 295 | +0.0687 | 100.0% |
| 0.55 | 0.20 | 289 | +0.0687 | 100.0% |
| 0.55 | 0.30 | 253 | +0.0687 | 100.0% |
| 0.55 | 0.40 | 216 | +0.0687 | 100.0% |
| 0.55 | 0.50 | 146 | +0.0687 | 100.0% |
| 0.60 | 0.15 | 262 | +0.0687 | 100.0% |
| 0.60 | 0.25 | 261 | +0.0687 | 100.0% |
| 0.60 | 0.35 | 238 | +0.0687 | 100.0% |
| 0.60 | 0.45 | 191 | +0.0687 | 100.0% |
| 0.65 | 0.10 | 220 | +0.0687 | 100.0% |
| 0.65 | 0.20 | 220 | +0.0687 | 100.0% |
| 0.65 | 0.30 | 220 | +0.0687 | 100.0% |
| 0.65 | 0.40 | 209 | +0.0687 | 100.0% |
| 0.65 | 0.50 | 146 | +0.0687 | 100.0% |
| 0.70 | 0.15 | 119 | +0.0685 | 100.0% |
| 0.70 | 0.25 | 119 | +0.0685 | 100.0% |
| 0.70 | 0.35 | 119 | +0.0685 | 100.0% |
| 0.70 | 0.45 | 119 | +0.0685 | 100.0% |
| 0.75 | 0.10 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.20 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.30 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.40 | 19 | +0.0662 | 100.0% |
| 0.75 | 0.50 | 19 | +0.0662 | 100.0% |
| 0.80 | 0.15 | 1 | +0.0716 | 100.0% |
| 0.80 | 0.25 | 1 | +0.0716 | 100.0% |
| 0.80 | 0.35 | 1 | +0.0716 | 100.0% |
| 0.80 | 0.45 | 1 | +0.0716 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 305 candidates, mean lock IC=+0.0687, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | -0.0035 | 55.6% |
| 0.45 | 0.20 | 5 | -0.0032 | 80.0% |
| 0.45 | 0.30 | 2 | +0.0057 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | +0.0007 | 62.5% |
| 0.50 | 0.25 | 3 | -0.0064 | 66.7% |
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
| 0.45 | 0.10 | 19 | +0.0025 | 70.0% |
| 0.45 | 0.20 | 12 | +0.0085 | 70.0% |
| 0.45 | 0.30 | 2 | +0.0015 | 50.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 16 | +0.0013 | 60.0% |
| 0.50 | 0.25 | 8 | -0.0026 | 50.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 17 | +0.0013 | 60.0% |
| 0.55 | 0.20 | 12 | +0.0085 | 70.0% |
| 0.55 | 0.30 | 2 | +0.0015 | 50.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 7 | +0.0226 | 85.7% |
| 0.60 | 0.25 | 4 | +0.0037 | 75.0% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 7 candidates, mean lock IC=+0.0226, 85.7% positive

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
| 0.45 | 0.10 | 1130 | +0.1149 | 100.0% |
| 0.45 | 0.20 | 1107 | +0.1149 | 100.0% |
| 0.45 | 0.30 | 1062 | +0.1149 | 100.0% |
| 0.45 | 0.40 | 960 | +0.1149 | 100.0% |
| 0.45 | 0.50 | 782 | +0.1149 | 100.0% |
| 0.50 | 0.15 | 1123 | +0.1149 | 100.0% |
| 0.50 | 0.25 | 1091 | +0.1149 | 100.0% |
| 0.50 | 0.35 | 1023 | +0.1149 | 100.0% |
| 0.50 | 0.45 | 886 | +0.1149 | 100.0% |
| 0.55 | 0.10 | 1127 | +0.1149 | 100.0% |
| 0.55 | 0.20 | 1107 | +0.1149 | 100.0% |
| 0.55 | 0.30 | 1062 | +0.1149 | 100.0% |
| 0.55 | 0.40 | 960 | +0.1149 | 100.0% |
| 0.55 | 0.50 | 782 | +0.1149 | 100.0% |
| 0.60 | 0.15 | 1082 | +0.1149 | 100.0% |
| 0.60 | 0.25 | 1076 | +0.1149 | 100.0% |
| 0.60 | 0.35 | 1022 | +0.1149 | 100.0% |
| 0.60 | 0.45 | 886 | +0.1149 | 100.0% |
| 0.65 | 0.10 | 962 | +0.1149 | 100.0% |
| 0.65 | 0.20 | 962 | +0.1149 | 100.0% |
| 0.65 | 0.30 | 962 | +0.1149 | 100.0% |
| 0.65 | 0.40 | 929 | +0.1149 | 100.0% |
| 0.65 | 0.50 | 782 | +0.1149 | 100.0% |
| 0.70 | 0.15 | 695 | +0.1149 | 100.0% |
| 0.70 | 0.25 | 695 | +0.1149 | 100.0% |
| 0.70 | 0.35 | 695 | +0.1149 | 100.0% |
| 0.70 | 0.45 | 695 | +0.1149 | 100.0% |
| 0.75 | 0.10 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.20 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.30 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.40 | 342 | +0.1149 | 100.0% |
| 0.75 | 0.50 | 342 | +0.1149 | 100.0% |
| 0.80 | 0.15 | 106 | +0.1106 | 100.0% |
| 0.80 | 0.25 | 106 | +0.1106 | 100.0% |
| 0.80 | 0.35 | 106 | +0.1106 | 100.0% |
| 0.80 | 0.45 | 106 | +0.1106 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1130 candidates, mean lock IC=+0.1149, 100.0% positive

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
| 0.45 | 0.10 | 594 | +0.1330 | 100.0% |
| 0.45 | 0.20 | 565 | +0.1330 | 100.0% |
| 0.45 | 0.30 | 465 | +0.1330 | 100.0% |
| 0.45 | 0.40 | 331 | +0.1330 | 100.0% |
| 0.45 | 0.50 | 202 | +0.1330 | 100.0% |
| 0.50 | 0.15 | 591 | +0.1330 | 100.0% |
| 0.50 | 0.25 | 528 | +0.1330 | 100.0% |
| 0.50 | 0.35 | 391 | +0.1330 | 100.0% |
| 0.50 | 0.45 | 275 | +0.1330 | 100.0% |
| 0.55 | 0.10 | 586 | +0.1330 | 100.0% |
| 0.55 | 0.20 | 565 | +0.1330 | 100.0% |
| 0.55 | 0.30 | 465 | +0.1330 | 100.0% |
| 0.55 | 0.40 | 331 | +0.1330 | 100.0% |
| 0.55 | 0.50 | 202 | +0.1330 | 100.0% |
| 0.60 | 0.15 | 518 | +0.1330 | 100.0% |
| 0.60 | 0.25 | 499 | +0.1330 | 100.0% |
| 0.60 | 0.35 | 388 | +0.1330 | 100.0% |
| 0.60 | 0.45 | 275 | +0.1330 | 100.0% |
| 0.65 | 0.10 | 328 | +0.1330 | 100.0% |
| 0.65 | 0.20 | 328 | +0.1330 | 100.0% |
| 0.65 | 0.30 | 328 | +0.1330 | 100.0% |
| 0.65 | 0.40 | 303 | +0.1330 | 100.0% |
| 0.65 | 0.50 | 201 | +0.1330 | 100.0% |
| 0.70 | 0.15 | 140 | +0.1330 | 100.0% |
| 0.70 | 0.25 | 140 | +0.1330 | 100.0% |
| 0.70 | 0.35 | 140 | +0.1330 | 100.0% |
| 0.70 | 0.45 | 139 | +0.1330 | 100.0% |
| 0.75 | 0.10 | 32 | +0.1214 | 100.0% |
| 0.75 | 0.20 | 32 | +0.1214 | 100.0% |
| 0.75 | 0.30 | 32 | +0.1214 | 100.0% |
| 0.75 | 0.40 | 32 | +0.1214 | 100.0% |
| 0.75 | 0.50 | 32 | +0.1214 | 100.0% |
| 0.80 | 0.15 | 2 | +0.1298 | 100.0% |
| 0.80 | 0.25 | 2 | +0.1298 | 100.0% |
| 0.80 | 0.35 | 2 | +0.1298 | 100.0% |
| 0.80 | 0.45 | 2 | +0.1298 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 594 candidates, mean lock IC=+0.1330, 100.0% positive

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
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +0.0571 | +0.0000 | +0.0048 | 0.08x | 2010-10-15 |
| `combo_rank_min__volume_weighted_price_position__double_bottom_bull_flag_early` | -0.0447 | +0.0000 | +0.0073 | -0.16x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1729 | +0.0000 | +0.0868 | 0.50x | No decay |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1841 | +0.0000 | +0.1000 | 0.54x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1772 | +0.0000 | +0.1217 | 0.69x | 2016-08-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1976 | +0.0000 | +0.1217 | 0.62x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1914 | +0.0000 | +0.0936 | 0.49x | 2021-07-28 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1717 | +0.0000 | +0.0911 | 0.53x | No decay |
| `combo_min__opening_auction_imbalance__star50_limit_proximity_early` | +0.1687 | +0.0000 | +0.1134 | 0.67x | 2016-09-26 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1907 | +0.0000 | +0.0916 | 0.48x | 2025-07-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance` | +0.2000 | +0.0000 | +0.1099 | 0.55x | No decay |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | +0.1719 | +0.0000 | +0.0798 | 0.46x | No decay |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1692 | +0.0000 | +0.1175 | 0.69x | 2020-01-06 |
| `combo_min__max_up_ret__first_bar_sentiment` | +0.1707 | +0.0000 | +0.0726 | 0.43x | 2020-01-06 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | +0.1898 | +0.0000 | +0.0884 | 0.47x | No decay |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1627 | +0.0000 | +0.0893 | 0.55x | No decay |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | +0.1513 | +0.0000 | +0.1191 | 0.79x | 2016-09-26 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1473 | +0.0000 | +0.0958 | 0.65x | 2016-08-24 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +0.1473 | +0.0000 | +0.0948 | 0.64x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1940 | +0.0000 | +0.1210 | 0.62x | No decay |
| `combo_min__first_bar_sentiment__bar_ret_0` | +0.1401 | +0.0000 | +0.0787 | 0.56x | 2013-09-23 |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | +0.1786 | +0.0000 | +0.0936 | 0.52x | 2020-01-06 |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | +0.1744 | +0.0000 | +0.0840 | 0.48x | 2019-12-05 |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | +0.1692 | +0.0000 | +0.0836 | 0.49x | 2016-12-29 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1625 | +0.0000 | +0.1069 | 0.66x | 2016-09-26 |
| `combo_rel_diff__opening_auction_imbalance__volume_weighted_momentum_acceleration` | +0.1854 | +0.0000 | +0.0909 | 0.49x | No decay |
| `combo_max__bar_ret_0__max_down_ret` | +0.1688 | +0.0000 | +0.0789 | 0.47x | 2016-11-01 |
| `combo_max__max_up_ret__first_bar_sentiment` | +0.1704 | +0.0000 | +0.0765 | 0.45x | 2017-05-09 |
| `combo_max__close_vs_open_range__first_bar_sentiment` | +0.1503 | +0.0000 | +0.0768 | 0.51x | 2017-05-09 |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | +0.1302 | +0.0000 | +0.0654 | 0.50x | 2020-01-06 |
| `combo_sig_product__max_up_ret__body_size_progression` | +0.1456 | +0.0000 | +0.1031 | 0.71x | 2020-12-18 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1680 | +0.0000 | +0.0792 | 0.47x | 2017-04-07 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1398 | +0.0000 | +0.1223 | 0.88x | 2011-12-23 |
| `combo_ratio__bar_ret_0__opening_auction_imbalance` | +0.1031 | +0.0000 | +0.0500 | 0.49x | 2013-09-23 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment` | +0.1569 | +0.0000 | +0.1158 | 0.74x | 2017-01-20 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1666 | +0.0000 | +0.1260 | 0.76x | 2017-01-20 |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | +0.1583 | +0.0000 | +0.1347 | 0.85x | 2016-10-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | +0.1265 | +0.0000 | +0.1316 | 1.04x | 2017-02-27 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1021 | +0.0000 | +0.1075 | 1.05x | 2011-10-18 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1681 | +0.0000 | +0.1220 | 0.73x | 2017-02-27 |
| `combo_min__max_up_ret__impulse_bar_dominance` | +0.1111 | +0.0000 | +0.0985 | 0.89x | 2017-01-20 |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1052 | +0.0000 | +0.1074 | 1.02x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__first_bar_return` | +0.1399 | +0.0000 | +0.1261 | 0.90x | 2011-10-18 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +0.1554 | +0.0000 | +0.1176 | 0.76x | 2016-10-24 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1391 | +0.0000 | +0.1271 | 0.91x | 2011-10-18 |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | +0.1401 | +0.0000 | +0.1375 | 0.98x | 2016-10-24 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1305 | +0.0000 | +0.0763 | 0.59x | 2017-04-28 |
| `combo_tri_mean__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | +0.1132 | +0.0000 | +0.1048 | 0.93x | 2011-10-18 |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | +0.1531 | +0.0000 | +0.1126 | 0.74x | 2016-12-21 |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | +0.1572 | +0.0000 | +0.1104 | 0.70x | 2017-01-20 |
| `combo_rank_max__max_up_ret__impulse_bar_dominance` | +0.1067 | +0.0000 | +0.0792 | 0.74x | 2016-09-14 |
| `rbreaker_sell_setup_proximity_early` | +0.1526 | +0.0000 | +0.1309 | 0.86x | 2016-12-21 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1186 | +0.0000 | +0.1312 | 1.11x | 2017-01-20 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +0.1398 | +0.0000 | +0.0928 | 0.66x | 2017-01-20 |
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1511 | +0.0000 | +0.1116 | 0.74x | 2017-01-20 |
| `combo_rank_max__first_bar_sentiment__rbreaker_buy_setup_proximity_early` | +0.1287 | +0.0000 | +0.0661 | 0.51x | 2017-04-28 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1428 | +0.0000 | +0.1124 | 0.79x | 2016-12-21 |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | +0.1227 | +0.0000 | +0.1069 | 0.87x | 2017-01-20 |
| `combo_z_sum__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | +0.1172 | +0.0000 | +0.1043 | 0.89x | 2011-10-18 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 83.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=+0.2412). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=-0.0426). Consider relaxing this gate.
3. **300ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=+0.4178). Consider relaxing this gate.
4. **300ETF `single` — B4 Correlation Gate too strict**: 96.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 26.0%, mean lock Sharpe=+0.3760). Consider relaxing this gate.
5. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2417). Consider relaxing this gate.
6. **300ETF `short` — BH-FDR Gate too strict**: 85.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=+0.2273). Consider relaxing this gate.
7. **300ETF `short` — B3 Composite Floor too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.1028). Consider relaxing this gate.
8. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 76.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=+0.1679). Consider relaxing this gate.
9. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.2106). Consider relaxing this gate.
10. **50ETF `short` — BH-FDR Gate too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.5453). Consider relaxing this gate.
11. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 48.0%, mean lock Sharpe=+0.5687). Consider relaxing this gate.
12. **500ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 48.0%, mean lock Sharpe=+0.5522). Consider relaxing this gate.
13. **500ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 48.0%, mean lock Sharpe=+0.7132). Consider relaxing this gate.
14. **500ETF `long` — BH-FDR Gate too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.1712). Consider relaxing this gate.
15. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.1404). Consider relaxing this gate.
16. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+1.0165). Consider relaxing this gate.
17. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+1.3719). Consider relaxing this gate.
18. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+0.6527). Consider relaxing this gate.
19. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.1320). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
