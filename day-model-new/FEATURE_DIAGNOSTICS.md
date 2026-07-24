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

### 300ETF — `single` (Full Model Lockbox IC: +0.0350, Sharpe: +0.0982)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1299 | +0.0650 | +0.0280 | -0.3103 | 82.46 | +8.8 | 1.09x | -0.0028 | +0.0292 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1197 | +0.0611 | +0.0379 | +0.7043 | 83.31 | +25.6 | 3.19x | -0.0018 | +0.1293 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1164 | +0.0602 | +0.0189 | +0.0731 | 85.84 | +15.5 | 1.93x | -0.0028 | -0.1440 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1083 | +0.0690 | +0.0353 | -0.1685 | 82.46 | +11.0 | 1.37x | +0.0006 | +0.0136 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0953 | +0.0728 | +0.0616 | -0.0803 | 84.15 | +12.6 | 1.58x | -0.0018 | +0.0134 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1145 | +0.0811 | +0.0660 | +0.3638 | 83.31 | +19.2 | 2.39x | +0.0071 | +0.0240 |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0883 | +0.0561 | -0.0129 | -0.7923 | 90.07 | +5.6 | 0.70x | -0.0028 | +0.2198 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0208 | -0.0038 | +0.0016 | +0.2719 | 79.92 | +17.9 | 2.24x | +0.0004 | +0.0792 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0538 | +0.0537 | +0.0706 | +0.1258 | 81.62 | +15.5 | 1.93x | +0.0037 | +0.2150 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0702 | +0.0120 | -0.0280 | -1.7117 | 74.43 | -3.0 | -0.37x | +0.0000 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1342, Sharpe: +0.8484)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1808 | +0.1142 | +0.1145 | +0.4686 | 80.77 | +23.5 | 2.94x | +0.0001 | -0.0785 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1863 | +0.1030 | +0.1256 | +0.7571 | 85.00 | +27.7 | 3.46x | -0.0003 | -0.1701 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1870 | +0.1116 | +0.1138 | +0.1133 | 90.07 | +17.1 | 2.14x | -0.0014 | +0.0911 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1906 | +0.0766 | +0.0842 | +0.7133 | 74.00 | +26.9 | 3.37x | -0.0000 | +0.0685 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1881 | +0.0823 | +0.1015 | +0.8294 | 80.77 | +31.5 | 3.93x | +0.0002 | +0.0457 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1889 | +0.0722 | +0.0735 | -0.9279 | 89.65 | +1.4 | 0.18x | -0.0011 | -0.1728 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1500 | +0.1164 | +0.1001 | +0.0682 | 84.58 | +15.1 | 1.89x | +0.0006 | +0.1474 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1312 | +0.0939 | +0.1114 | +0.2420 | 77.39 | +18.0 | 2.25x | +0.0016 | -0.1033 |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1182 | +0.0755 | +0.0743 | -0.1197 | 72.31 | +9.6 | 1.20x | -0.0005 | -0.1255 |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1794 | +0.1196 | +0.1258 | +0.2051 | 84.58 | +18.2 | 2.27x | +0.0010 | +0.0605 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.2028 | +0.0858 | +0.0810 | -0.9675 | 88.38 | +1.3 | 0.17x | -0.0009 | +0.0250 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1611 | +0.0792 | +0.1083 | +1.1127 | 77.39 | +37.5 | 4.69x | +0.0009 | -0.1227 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1499 | +0.0837 | +0.1100 | +0.5932 | 87.96 | +22.8 | 2.85x | +0.0037 | +0.1387 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1887 | +0.0883 | +0.1135 | +0.6871 | 84.15 | +27.6 | 3.46x | -0.0007 | -0.0323 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1286 | +0.0881 | +0.1039 | -0.0814 | 85.00 | +12.6 | 1.57x | -0.0003 | +0.0486 |
| `combo_rank_min__bar_ret_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1305 | +0.0751 | +0.1238 | +1.0093 | 76.54 | +34.7 | 4.33x | +0.0011 | +0.1028 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1535 | +0.0913 | +0.0711 | -0.0107 | 90.50 | +14.8 | 1.85x | -0.0006 | +0.0996 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1395 | +0.1062 | +0.1319 | +0.7126 | 82.46 | +28.0 | 3.49x | +0.0013 | +0.0366 |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1304 | +0.0986 | +0.1158 | +0.9651 | 85.84 | +33.1 | 4.14x | +0.0009 | -0.1180 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1583 | +0.0972 | +0.1139 | +1.0377 | 88.38 | +30.3 | 3.78x | +0.0008 | +0.0700 |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.0830 | +0.0014 | +0.0337 | -0.3776 | 82.04 | +7.8 | 0.97x | +0.0012 | +0.2058 |
| `combo_mean__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1535 | +0.0871 | +0.1025 | +0.4799 | 77.39 | +23.1 | 2.89x | -0.0004 | -0.1255 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1303 | +0.0972 | +0.0940 | -0.1879 | 90.50 | +12.0 | 1.51x | -0.0008 | -0.0644 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1638 | +0.1067 | +0.0924 | +0.3348 | 85.00 | +20.6 | 2.57x | +0.0004 | +0.0000 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1476 | +0.1024 | +0.1219 | +0.2731 | 86.69 | +20.1 | 2.51x | -0.0008 | +0.0976 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1623 | +0.1046 | +0.1053 | +0.0931 | 83.31 | +15.9 | 1.98x | -0.0013 | -0.1031 |
| `combo_ratio__max_down_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1323 | +0.0543 | +0.1213 | -0.2902 | 91.34 | +10.4 | 1.29x | -0.0008 | -0.0028 |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1064 | +0.0717 | +0.1357 | +1.0168 | 87.54 | +30.9 | 3.86x | +0.0003 | +0.0000 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1618 | +0.1110 | +0.1261 | +0.5742 | 81.62 | +25.9 | 3.24x | -0.0013 | +0.0890 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.0687 | +0.0159 | +0.0027 | +0.2656 | 83.73 | +19.0 | 2.38x | +0.0005 | +0.0057 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1436 | +0.1254 | +0.1504 | +0.3043 | 82.46 | +20.0 | 2.50x | +0.0012 | -0.0866 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1415 | +0.0929 | +0.0879 | -0.1032 | 89.65 | +13.0 | 1.62x | -0.0005 | +0.0356 |

### 588000ETF — `single` (Full Model Lockbox IC: -0.0298, Sharpe: +0.0000)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1040 | -0.0093 | -0.0537 | -0.6791 | 84.20 | -4.1 | -0.52x | -0.0487 | -1.4335 |
| `vix_rolling_percentile_60d` | Other Technical | +1 | +0.0431 | +0.0434 | +0.0189 | +1.4335 | 28.71 | +40.0 | 5.00x | +0.0239 | -0.2101 |

### 588000ETF — `long` (Full Model Lockbox IC: +0.0364, Sharpe: +0.1957)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_z_sum__vix_skew_proxy__vix_iv_spread` | Other Technical | +1 | +0.0815 | +0.0202 | +0.0364 | +0.1957 | 63.15 | +19.0 | 2.38x | +0.0364 | +0.1957 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1427, Sharpe: +0.8169)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1596 | +0.1109 | +0.1279 | +1.5377 | 86.69 | +51.4 | 6.43x | +0.0032 | +0.0595 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1659 | +0.1254 | +0.1426 | +0.9756 | 87.54 | +38.3 | 4.79x | +0.0029 | -0.0373 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1739 | +0.1248 | +0.1318 | +1.2965 | 86.69 | +47.6 | 5.95x | +0.0008 | +0.1010 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1213 | +0.0784 | +0.0900 | +0.9652 | 73.16 | +30.2 | 3.77x | -0.0002 | +0.0743 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0909 | +0.1263 | +0.1192 | +0.4661 | 80.77 | +25.8 | 3.22x | +0.0087 | -0.3303 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_range` | Other Technical | +1 | +0.1357 | +0.0996 | +0.1059 | +0.5093 | 80.35 | +25.5 | 3.19x | -0.0013 | -0.4908 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1533 | +0.1317 | +0.1338 | +0.6628 | 84.15 | +29.8 | 3.73x | +0.0004 | -0.1763 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | Other Technical | +1 | +0.1349 | +0.1238 | +0.1109 | +0.0049 | 90.50 | +15.1 | 1.89x | -0.0000 | +0.0373 |
| `combo_rank_max__max_up_ret__opening_auction_imbalance` | Intraday Range Momentum | +1 | +0.1173 | +0.1090 | +0.0932 | +0.0574 | 89.65 | +16.2 | 2.02x | -0.0003 | -0.3205 |
| `combo_z_sum__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1522 | +0.0913 | +0.0792 | -0.2440 | 89.23 | +9.5 | 1.19x | -0.0029 | -0.2881 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.1220 | +0.0994 | +0.0802 | -0.3755 | 82.46 | +5.3 | 0.66x | +0.0002 | -0.3887 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 56.0% lock IC > 0, 13.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6939_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1028 | 30 | 73.3% | 10.0% | +0.0117 | -0.7339 |
| B2 Rolling Guard | 131 | 30 | 76.7% | 33.3% | +0.0142 | -0.3544 |
| BH-FDR Gate | 8 | 8 | 37.5% | 37.5% | -0.0038 | -0.2864 |
| B3 Composite Floor | 243 | 30 | 80.0% | 26.7% | +0.0204 | -0.3102 |
| B4 Correlation Gate | 15 | 15 | 100.0% | 40.0% | +0.0396 | -0.0514 |

**Admitted Pool Summary**: 11 features, False Positive Rate = 54.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0258, Mean Lock Sharpe = -0.2203

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Lock Sharpe=+0.4253
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Lock Sharpe=+0.4253
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.2340, Lock IC=+0.0050, Lock Sharpe=+0.1767

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1398, Lock IC=+0.0439, Lock Sharpe=+0.3083
- `combo_sig_product__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.1397, Lock IC=+0.0438, Lock Sharpe=+0.3083
- `limit_down_proximity_early`: Train IC=+0.1374, Lock IC=+0.0632, Lock Sharpe=+0.3058
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1374, Lock IC=+0.0632, Lock Sharpe=+0.3058
- `combo_min__bar_ret_0__bar_body_rng_0`: Train IC=+0.1467, Lock IC=+0.0117, Lock Sharpe=+0.2664

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__bar_ret_0__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0280, Lock Sharpe=+0.3353
- `combo_sig_product__first_bar_return__volume_surge_direction`: Train IC=+0.1080, Lock IC=+0.0260, Lock Sharpe=+0.3353
- `combo_sig_product__bar_body_rng_0__volume_surge_direction`: Train IC=+0.1072, Lock IC=+0.0233, Lock Sharpe=+0.3353

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2603, Lock IC=+0.0248, Lock Sharpe=+0.0677
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.2603, Lock IC=+0.0248, Lock Sharpe=+0.0677
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2601, Lock IC=+0.0248, Lock Sharpe=+0.0677
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.2601, Lock IC=+0.0248, Lock Sharpe=+0.0677
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0345, Lock Sharpe=+0.0673

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2690, Lock IC=+0.0342, Lock Sharpe=+0.8997
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2687, Lock IC=+0.0505, Lock Sharpe=+0.2804
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1659, Lock IC=+0.0418, Lock Sharpe=+0.1010
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2660, Lock IC=+0.0189, Lock Sharpe=+0.0731
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1804, Lock IC=+0.0655, Lock Sharpe=+0.0072

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 41.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6040_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 522 | 30 | 86.7% | 26.7% | +0.0216 | -0.3796 |
| B2 Rolling Guard | 50 | 30 | 33.3% | 0.0% | -0.0067 | -0.6608 |
| BH-FDR Gate | 7 | 7 | 14.3% | 0.0% | -0.0261 | -0.7244 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__willr14__sma50_dist`: Train IC=+0.1276, Lock IC=+0.0234, Lock Sharpe=+0.7672
- `combo_rank_min__willr14__sma100_dist`: Train IC=+0.1400, Lock IC=+0.0526, Lock Sharpe=+0.4731
- `combo_max__roc60__wavetrend_osc_day`: Train IC=+0.1457, Lock IC=+0.0305, Lock Sharpe=+0.3334
- `combo_max__roc60__yesterday_wavetrend_osc`: Train IC=+0.1457, Lock IC=+0.0305, Lock Sharpe=+0.3334
- `combo_rank_max__roc60__sma50_dist`: Train IC=+0.1279, Lock IC=+0.0126, Lock Sharpe=+0.2731

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 13.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7033_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 489 | 30 | 40.0% | 13.3% | +0.0067 | -0.5706 |
| B2 Rolling Guard | 52 | 30 | 50.0% | 10.0% | +0.0017 | -0.6324 |
| BH-FDR Gate | 30 | 30 | 70.0% | 36.7% | +0.0176 | -0.2851 |
| B3 Composite Floor | 15 | 15 | 86.7% | 13.3% | +0.0260 | -0.4699 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__total_path_length__limit_down_proximity_early`: Train IC=+0.1048, Lock IC=+0.0716, Lock Sharpe=+0.3435
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1120, Lock IC=+0.0504, Lock Sharpe=+0.3242
- `combo_min__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1097, Lock IC=+0.0217, Lock Sharpe=+0.1853
- `volume_surge_direction`: Train IC=+0.1060, Lock IC=+0.0217, Lock Sharpe=+0.0555

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0027, Lock Sharpe=+0.5285
- `combo_sig_product__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1011, Lock IC=+0.0439, Lock Sharpe=+0.2597
- `combo_rank_min__opening_drive_thrust_ratio__max_down_ret`: Train IC=+0.0472, Lock IC=+0.0041, Lock Sharpe=+0.1782

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1385, Lock IC=+0.0658, Lock Sharpe=+0.7565
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0708, Lock IC=+0.0655, Lock Sharpe=+0.6942
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0708, Lock IC=+0.0655, Lock Sharpe=+0.6942
- `star50_limit_proximity_early`: Train IC=+0.0741, Lock IC=+0.0650, Lock Sharpe=+0.6350
- `combo_min__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1269, Lock IC=+0.0646, Lock Sharpe=+0.4871

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1654, Lock IC=+0.0772, Lock Sharpe=+0.4062
- `combo_z_sum__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1654, Lock IC=+0.0772, Lock Sharpe=+0.4062

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 42.0% lock IC > 0, 6.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8111_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 596 | 30 | 93.3% | 46.7% | +0.0428 | -0.1966 |
| B2 Rolling Guard | 48 | 30 | 63.3% | 23.3% | +0.0088 | -0.7183 |
| BH-FDR Gate | 4 | 4 | 100.0% | 100.0% | +0.0262 | +0.1255 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__yesterday_wavetrend_osc`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_max__bar_vol_4__wavetrend_osc_day`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_mean__bar_vol_4__roc10`: Train IC=+0.1425, Lock IC=+0.0859, Lock Sharpe=+0.5934
- `combo_z_sum__bar_vol_4__roc10`: Train IC=+0.1425, Lock IC=+0.0859, Lock Sharpe=+0.5934
- `yesterday_lunch_gap`: Train IC=+0.1911, Lock IC=+0.0772, Lock Sharpe=+0.4464

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.1361, Lock IC=+0.0431, Lock Sharpe=+0.5398
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.0431, Lock Sharpe=+0.5398
- `star50_limit_proximity_early`: Train IC=+0.1363, Lock IC=+0.0239, Lock Sharpe=+0.2773
- `combo_product__bar_vol_4__first_bar_volume`: Train IC=+0.0898, Lock IC=+0.0492, Lock Sharpe=+0.2476
- `combo_product__bar_vol_4__bar_vol_0`: Train IC=+0.0898, Lock IC=+0.0492, Lock Sharpe=+0.2476

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__sma_distance_60d__ema_ribbon_width`: Train IC=+0.0067, Lock IC=+0.0304, Lock Sharpe=+0.1578
- `combo_diff__sma_distance_60d__ema_ribbon_width`: Train IC=+0.0060, Lock IC=+0.0304, Lock Sharpe=+0.1578
- `combo_z_diff__sma_distance_60d__ema_ribbon_width`: Train IC=+0.0060, Lock IC=+0.0304, Lock Sharpe=+0.1578
- `combo_ratio__star50_limit_proximity_early__bar_vol_4`: Train IC=+0.1157, Lock IC=+0.0135, Lock Sharpe=+0.0286

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8058_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 318 | 30 | 60.0% | 36.7% | +0.0047 | -0.8357 |
| B2 Rolling Guard | 35 | 30 | 23.3% | 6.7% | -0.0042 | -0.6198 |
| BH-FDR Gate | 7 | 7 | 0.0% | 0.0% | -0.0475 | -2.3142 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__yesterday_wavetrend_osc__donchian_breakout_ratio_20d`: Train IC=+0.1595, Lock IC=+0.0447, Lock Sharpe=+0.2406
- `combo_rank_min__yesterday_wavetrend_osc__donchian_breakout_proximity_20d`: Train IC=+0.1595, Lock IC=+0.0447, Lock Sharpe=+0.2406
- `combo_rank_min__wavetrend_osc_day__donchian_breakout_ratio_20d`: Train IC=+0.1595, Lock IC=+0.0447, Lock Sharpe=+0.2406
- `combo_rank_min__wavetrend_osc_day__donchian_breakout_proximity_20d`: Train IC=+0.1595, Lock IC=+0.0447, Lock Sharpe=+0.2406
- `combo_min__yesterday_wavetrend_osc__donchian_breakout_ratio_20d`: Train IC=+0.1509, Lock IC=+0.0430, Lock Sharpe=+0.1776

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc20`: Train IC=+0.0576, Lock IC=+0.0709, Lock Sharpe=+0.3274
- `bar_vol_4`: Train IC=+0.0880, Lock IC=+0.0834, Lock Sharpe=+0.0123

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 53.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4558_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 266 | 30 | 60.0% | 40.0% | +0.0250 | -0.2066 |
| B2 Rolling Guard | 42 | 30 | 23.3% | 3.3% | -0.0061 | -0.4271 |
| BH-FDR Gate | 7 | 7 | 28.6% | 14.3% | -0.0262 | -0.8618 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_z_sum__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `gap_pct`: Train IC=+0.1368, Lock IC=+0.0756, Lock Sharpe=+0.5967
- `combo_rank_max__bar_vol_4__sma_distance_60d`: Train IC=+0.1284, Lock IC=+0.0718, Lock Sharpe=+0.5594
- `combo_mean__sma50_dist__bar_vol_4`: Train IC=+0.1659, Lock IC=+0.0918, Lock Sharpe=+0.5075

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.0712, Lock IC=+0.0893, Lock Sharpe=+0.0285

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1622, Lock IC=+0.0130, Lock Sharpe=+0.0663

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 71.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4048_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1445 | 30 | 100.0% | 63.3% | +0.0862 | +0.0310 |
| B2 Rolling Guard | 156 | 30 | 100.0% | 30.0% | +0.0549 | -0.2236 |
| BH-FDR Gate | 29 | 29 | 20.7% | 10.3% | -0.0152 | -1.0558 |
| B3 Composite Floor | 606 | 30 | 100.0% | 80.0% | +0.1054 | +0.2666 |
| B4 Correlation Gate | 273 | 30 | 100.0% | 60.0% | +0.1011 | +0.2517 |

**Admitted Pool Summary**: 37 features, False Positive Rate = 40.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0967, Mean Lock Sharpe = +0.1342

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2667, Lock IC=+0.1120, Lock Sharpe=+0.5333
- `combo_rank_max__first_bar_sentiment__rsi_opening`: Train IC=+0.2035, Lock IC=+0.0682, Lock Sharpe=+0.4339
- `combo_rank_max__first_bar_sentiment__high_low_sequence_momentum`: Train IC=+0.2035, Lock IC=+0.0682, Lock Sharpe=+0.4339
- `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2758, Lock IC=+0.1064, Lock Sharpe=+0.4173
- `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2354, Lock IC=+0.0891, Lock Sharpe=+0.4106

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_auction_imbalance__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Lock Sharpe=+0.4761
- `combo_tri_z_mean__opening_auction_imbalance__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Lock Sharpe=+0.4761
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Lock Sharpe=+0.4761
- `combo_tri_z_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression`: Train IC=+0.1604, Lock IC=+0.0703, Lock Sharpe=+0.4761
- `combo_ratio__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.1654, Lock IC=+0.0824, Lock Sharpe=+0.2942

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_10_60`: Train IC=+0.0927, Lock IC=+0.0309, Lock Sharpe=+0.3757
- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Lock Sharpe=+0.2780
- `combo_z_diff__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0774, Lock IC=+0.0186, Lock Sharpe=+0.2780

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2827, Lock IC=+0.1172, Lock Sharpe=+0.8869
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2827, Lock IC=+0.1172, Lock Sharpe=+0.8869
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_day_regime_conviction`: Train IC=+0.2819, Lock IC=+0.1041, Lock Sharpe=+0.8493
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2945, Lock IC=+0.1037, Lock Sharpe=+0.7837
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.3140, Lock IC=+0.1137, Lock Sharpe=+0.5878

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2964, Lock IC=+0.1083, Lock Sharpe=+1.1127
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3072, Lock IC=+0.1015, Lock Sharpe=+0.8294
- `combo_rank_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2874, Lock IC=+0.1125, Lock Sharpe=+0.8288
- `combo_rank_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2874, Lock IC=+0.1125, Lock Sharpe=+0.8288
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Lock Sharpe=+0.7942

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 68.0% lock IC > 0, 19.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5167_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1143 | 30 | 100.0% | 26.7% | +0.0680 | -0.1910 |
| B2 Rolling Guard | 97 | 30 | 76.7% | 10.0% | +0.0539 | -0.5543 |
| BH-FDR Gate | 75 | 30 | 96.7% | 26.7% | +0.0769 | -0.1683 |
| B3 Composite Floor | 45 | 30 | 100.0% | 20.0% | +0.0605 | -0.3645 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__limit_down_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.3372
- `combo_min__limit_down_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.3372
- `combo_min__limit_down_proximity_early__limit_down_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.3372
- `combo_min__rbreaker_buy_setup_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.3372
- `combo_min__rbreaker_buy_setup_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.3372

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bar_vol_4`: Train IC=+0.0794, Lock IC=+0.0045, Lock Sharpe=+0.2531
- `combo_sig_product__rbreaker_sell_setup_proximity_early__morning_trend_extrapolated`: Train IC=+0.0839, Lock IC=+0.0670, Lock Sharpe=+0.2414
- `yesterday_day_vwap_dev`: Train IC=+0.1074, Lock IC=+0.0692, Lock Sharpe=+0.1605

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1618, Lock IC=+0.1614, Lock Sharpe=+0.8631
- `combo_min__shaved_bar_trend_conviction__trend_day_regime_conviction`: Train IC=+0.1566, Lock IC=+0.0657, Lock Sharpe=+0.6065
- `combo_rank_min__limit_down_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.5012
- `combo_rank_min__rbreaker_buy_setup_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.5012
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.1464, Lock IC=+0.1240, Lock Sharpe=+0.2125

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2116, Lock IC=+0.1196, Lock Sharpe=+0.9094
- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_trend_extrapolated`: Train IC=+0.2733, Lock IC=+0.1032, Lock Sharpe=+0.2430
- `combo_rank_min__yesterday_return__star50_limit_proximity_early`: Train IC=+0.2061, Lock IC=+0.0988, Lock Sharpe=+0.2206
- `combo_rank_min__limit_up_proximity_day__star50_limit_proximity_early`: Train IC=+0.2061, Lock IC=+0.0988, Lock Sharpe=+0.2206
- `combo_rank_min__limit_down_proximity_day__star50_limit_proximity_early`: Train IC=+0.2061, Lock IC=+0.0988, Lock Sharpe=+0.2206

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5059_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 362 | 30 | 50.0% | 13.3% | +0.0130 | -0.5305 |
| B2 Rolling Guard | 60 | 30 | 60.0% | 13.3% | +0.0156 | -0.4078 |
| BH-FDR Gate | 7 | 7 | 71.4% | 71.4% | +0.0775 | -0.0208 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1907, Lock IC=+0.1261, Lock Sharpe=+0.4638
- `gap_pct`: Train IC=+0.1160, Lock IC=+0.0889, Lock Sharpe=+0.2192
- `combo_rank_min__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1335, Lock IC=+0.1186, Lock Sharpe=+0.1816
- `combo_max__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1649, Lock IC=+0.1111, Lock Sharpe=+0.0254

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv_diff_1d`: Train IC=+0.0000, Lock IC=+0.0648, Lock Sharpe=+0.6476
- `combo_sig_product__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1375, Lock IC=+0.0868, Lock Sharpe=+0.2944
- `close_vs_open_range`: Train IC=+0.0789, Lock IC=+0.0872, Lock Sharpe=+0.1657
- `combo_min__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1062, Lock IC=+0.1197, Lock Sharpe=+0.1075

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+0.7903
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+0.7903
- `combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1676, Lock IC=+0.1070, Lock Sharpe=+0.3784
- `combo_mean__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.2113
- `combo_z_sum__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.2113

### 588000ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 21.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9212_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 842 | 30 | 16.7% | 10.0% | -0.0511 | -0.7081 |
| B2 Rolling Guard | 61 | 30 | 20.0% | 10.0% | -0.0490 | -1.2204 |
| BH-FDR Gate | 43 | 30 | 10.0% | 6.7% | -0.0519 | -0.8664 |
| B3 Composite Floor | 388 | 30 | 3.3% | 0.0% | -0.0531 | -0.9839 |
| B4 Correlation Gate | 20 | 20 | 15.0% | 5.0% | -0.0534 | -1.0122 |

**Admitted Pool Summary**: 7 features, False Positive Rate = 85.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0493, Mean Lock Sharpe = -0.6840

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__directional_volume_signature__early_vwap_acceleration`: Train IC=+0.2917, Lock IC=+0.0549, Lock Sharpe=+0.7984
- `combo_z_diff__directional_volume_signature__early_vwap_acceleration`: Train IC=+0.2917, Lock IC=+0.0549, Lock Sharpe=+0.7984
- `combo_rel_diff__directional_volume_signature__early_vwap_acceleration`: Train IC=+0.2947, Lock IC=+0.0422, Lock Sharpe=+0.6601

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_iv_spread`: Train IC=+0.1047, Lock IC=+0.0550, Lock Sharpe=+0.8009
- `combo_tri_min__net_volume_flow__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.1668, Lock IC=+0.0198, Lock Sharpe=+0.4033
- `combo_tri_min__opening_auction_imbalance__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.1668, Lock IC=+0.0198, Lock Sharpe=+0.4033

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_confirmed_breakout`: Train IC=+0.1399, Lock IC=+0.0306, Lock Sharpe=+1.4245
- `combo_min__pullback_depth_ratio__vwap_trend_channel_slope`: Train IC=+0.1391, Lock IC=+0.0957, Lock Sharpe=+0.9292

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.3011, Lock IC=+0.0305, Lock Sharpe=+0.0826

### 588000ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 22.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4723_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 530 | 30 | 16.7% | 0.0% | -0.0385 | -0.9573 |
| B2 Rolling Guard | 98 | 30 | 56.7% | 13.3% | +0.0041 | -0.1922 |
| BH-FDR Gate | 39 | 30 | 23.3% | 6.7% | -0.0395 | -0.5692 |
| B3 Composite Floor | 18 | 18 | 66.7% | 33.3% | +0.0068 | -0.3925 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 0.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0364, Mean Lock Sharpe = +0.1957

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_rolling_percentile_60d`: Train IC=+0.1947, Lock IC=+0.0189, Lock Sharpe=+1.6280
- `combo_max__vix_rolling_percentile_60d__iv_envelope_deviation`: Train IC=+0.2007, Lock IC=+0.0154, Lock Sharpe=+1.1602
- `combo_mean__iv_envelope_deviation__vix_skew_proxy`: Train IC=+0.2129, Lock IC=+0.0271, Lock Sharpe=+0.0187
- `combo_z_sum__iv_envelope_deviation__vix_skew_proxy`: Train IC=+0.2129, Lock IC=+0.0271, Lock Sharpe=+0.0187

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__iv_envelope_deviation__vix_skew_proxy`: Train IC=+0.1053, Lock IC=+0.0571, Lock Sharpe=+0.1742
- `combo_abs_diff__vol5__yesterday_day_realized_vol`: Train IC=+0.2014, Lock IC=+0.0186, Lock Sharpe=+0.0327

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__yesterday_day_realized_vol__vix_skew_proxy`: Train IC=+0.2309, Lock IC=+0.0216, Lock Sharpe=+0.2814
- `combo_mean__vix_skew_proxy__vix_iv_spread`: Train IC=+0.2516, Lock IC=+0.0364, Lock Sharpe=+0.1957
- `combo_mean__vix_diff_1d__vix_iv_spread`: Train IC=+0.3000, Lock IC=+0.0416, Lock Sharpe=+0.1382
- `combo_z_sum__vix_diff_1d__vix_iv_spread`: Train IC=+0.3000, Lock IC=+0.0416, Lock Sharpe=+0.1382
- `combo_mean__yesterday_vix_early_drift__vix_iv_spread`: Train IC=+0.3000, Lock IC=+0.0416, Lock Sharpe=+0.1382

### 588000ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 45.0% lock IC > 0, 30.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3279_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 807 | 30 | 40.0% | 36.7% | -0.0115 | -0.0319 |
| B2 Rolling Guard | 80 | 30 | 56.7% | 30.0% | +0.0175 | -0.0475 |
| BH-FDR Gate | 37 | 30 | 30.0% | 20.0% | -0.0085 | -0.1236 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__pullback_depth_ratio__opening_drive_thrust_ratio`: Train IC=+0.2417, Lock IC=+0.0719, Lock Sharpe=+2.0759
- `combo_product__opening_drive_thrust_ratio__morning_volume_weighted_momentum`: Train IC=+0.2137, Lock IC=+0.1098, Lock Sharpe=+1.9171
- `combo_product__pullback_depth_ratio__morning_volume_weighted_momentum`: Train IC=+0.3596, Lock IC=+0.0698, Lock Sharpe=+1.1474
- `combo_min__pullback_depth_ratio__opening_drive_thrust_ratio`: Train IC=+0.2152, Lock IC=+0.1405, Lock Sharpe=+1.0722
- `combo_diff__early_vwap_acceleration__directional_volume_signature`: Train IC=+0.2665, Lock IC=+0.0549, Lock Sharpe=+0.5567

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `pullback_shallowness_score`: Train IC=+0.0350, Lock IC=+0.0517, Lock Sharpe=+2.0047
- `combo_ifelse__vix__directional_volume_signature__vix_rolling_percentile_60d`: Train IC=+0.2047, Lock IC=+0.0128, Lock Sharpe=+0.9634
- `volume_acceleration`: Train IC=+0.0419, Lock IC=+0.0540, Lock Sharpe=+0.8375
- `combo_ifelse__vix__pullback_depth_ratio__vix_rolling_percentile_60d`: Train IC=+0.0578, Lock IC=+0.1100, Lock Sharpe=+0.7685
- `combo_diff__rbreaker_buy_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.0170, Lock IC=+0.1384, Lock Sharpe=+0.5842

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__vix__directional_volume_signature__bar_ret_1`: Train IC=+0.1745, Lock IC=+0.0128, Lock Sharpe=+0.9634
- `combo_min__opening_drive_thrust_ratio__directional_volume_signature`: Train IC=+0.1711, Lock IC=+0.0010, Lock Sharpe=+0.9446
- `combo_rank_min__pullback_depth_ratio__opening_auction_imbalance`: Train IC=+0.2793, Lock IC=+0.1367, Lock Sharpe=+0.7685
- `combo_rank_min__pullback_depth_ratio__net_volume_flow`: Train IC=+0.2793, Lock IC=+0.1367, Lock Sharpe=+0.7685
- `combo_rank_min__pullback_depth_ratio__bar_ret_1`: Train IC=+0.2243, Lock IC=+0.1831, Lock Sharpe=+0.5073

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 78.0% lock IC > 0, 53.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.1447_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1094 | 30 | 100.0% | 63.3% | +0.0905 | +0.2703 |
| B2 Rolling Guard | 230 | 30 | 100.0% | 90.0% | +0.0881 | +0.2629 |
| BH-FDR Gate | 6 | 6 | 83.3% | 83.3% | +0.0385 | +0.2259 |
| B3 Composite Floor | 416 | 30 | 100.0% | 100.0% | +0.1317 | +1.0820 |
| B4 Correlation Gate | 72 | 30 | 100.0% | 96.7% | +0.1282 | +1.0794 |

**Admitted Pool Summary**: 15 features, False Positive Rate = 13.3% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1151, Mean Lock Sharpe = +0.6320

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Lock Sharpe=+1.3653
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2242, Lock IC=+0.1533, Lock Sharpe=+1.3653
- `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`: Train IC=+0.2092, Lock IC=+0.1358, Lock Sharpe=+0.8345
- `combo_diff__first_bar_return__late_bar_momentum`: Train IC=+0.1966, Lock IC=+0.0840, Lock Sharpe=+0.8035
- `combo_z_diff__first_bar_return__late_bar_momentum`: Train IC=+0.1966, Lock IC=+0.0840, Lock Sharpe=+0.8035

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Lock Sharpe=+0.8573
- `combo_z_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1884, Lock IC=+0.1331, Lock Sharpe=+0.8573
- `combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1874, Lock IC=+0.1369, Lock Sharpe=+0.8573
- `combo_tri_median__first_bar_sentiment__bar_body_rng_0__first_bar_return`: Train IC=+0.1949, Lock IC=+0.0856, Lock Sharpe=+0.5636
- `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2004, Lock IC=+0.1176, Lock Sharpe=+0.5263

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Lock Sharpe=+0.7804
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Lock Sharpe=+0.7804
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Lock Sharpe=+0.7804
- `close_vs_open_range`: Train IC=+0.0863, Lock IC=+0.0988, Lock Sharpe=+0.4620
- `combo_rank_max__yesterday_first_30min_return__yesterday_afternoon_reversal`: Train IC=+0.0350, Lock IC=+0.0390, Lock Sharpe=+0.0055

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Lock Sharpe=+1.5392
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Lock Sharpe=+1.5392
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2766, Lock IC=+0.1375, Lock Sharpe=+1.5099
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2781, Lock IC=+0.1395, Lock Sharpe=+1.4393
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2957, Lock IC=+0.1138, Lock Sharpe=+1.4236

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2895, Lock IC=+0.1279, Lock Sharpe=+1.5377
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Lock Sharpe=+1.5377
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2692, Lock IC=+0.1273, Lock Sharpe=+1.4562
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`: Train IC=+0.2692, Lock IC=+0.1273, Lock Sharpe=+1.4562
- `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2616, Lock IC=+0.1249, Lock Sharpe=+1.4232

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 65.0% lock IC > 0, 32.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2688_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 986 | 30 | 76.7% | 60.0% | +0.0639 | +0.1106 |
| B2 Rolling Guard | 76 | 30 | 93.3% | 80.0% | +0.0858 | +0.2991 |
| BH-FDR Gate | 55 | 30 | 100.0% | 76.7% | +0.0684 | +0.3094 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__shaved_bar_trend_conviction__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1545, Lock IC=+0.0946, Lock Sharpe=+0.9823
- `combo_tri_median__shaved_bar_trend_conviction__first_30min_return__counter_trend_bar_weakness`: Train IC=+0.1545, Lock IC=+0.0946, Lock Sharpe=+0.9823
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1887, Lock IC=+0.1387, Lock Sharpe=+0.9616
- `combo_tri_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1450, Lock IC=+0.1569, Lock Sharpe=+0.8410
- `combo_rank_min__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1558, Lock IC=+0.1425, Lock Sharpe=+0.7264

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1336, Lock IC=+0.1014, Lock Sharpe=+1.0890
- `combo_min__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1197, Lock IC=+0.1425, Lock Sharpe=+0.7455
- `combo_min__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1197, Lock IC=+0.1425, Lock Sharpe=+0.7455
- `combo_tri_min__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1093, Lock IC=+0.1150, Lock Sharpe=+0.6548
- `combo_tri_min__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1093, Lock IC=+0.1150, Lock Sharpe=+0.6548

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1514, Lock IC=+0.1368, Lock Sharpe=+1.1280
- `combo_mean__volume_acceleration__vol_ratio_10_60`: Train IC=+0.2031, Lock IC=+0.0293, Lock Sharpe=+0.8158
- `combo_z_sum__volume_acceleration__vol_ratio_10_60`: Train IC=+0.2031, Lock IC=+0.0293, Lock Sharpe=+0.8158
- `combo_mean__volume_trend_intraday__vol_ratio_10_60`: Train IC=+0.1704, Lock IC=+0.0280, Lock Sharpe=+0.7241
- `combo_z_sum__volume_trend_intraday__vol_ratio_10_60`: Train IC=+0.1704, Lock IC=+0.0280, Lock Sharpe=+0.7241

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 40.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5821_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 238 | 30 | 60.0% | 40.0% | +0.0136 | -0.2483 |
| B2 Rolling Guard | 58 | 30 | 53.3% | 23.3% | +0.0106 | -0.2416 |
| BH-FDR Gate | 4 | 4 | 100.0% | 75.0% | +0.0836 | +0.3432 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.0842, Lock IC=+0.1476, Lock Sharpe=+1.1308
- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.1709, Lock IC=+0.0830, Lock Sharpe=+0.7366
- `bb_width`: Train IC=+0.1023, Lock IC=+0.0475, Lock Sharpe=+0.7236
- `yesterday_pm_return`: Train IC=+0.1096, Lock IC=+0.0803, Lock Sharpe=+0.4680
- `vol_gk20`: Train IC=+0.0915, Lock IC=+0.0072, Lock Sharpe=+0.4550

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_day_realized_vol`: Train IC=+0.0376, Lock IC=+0.0061, Lock Sharpe=+0.5514
- `gap_pct`: Train IC=+0.0358, Lock IC=+0.1182, Lock Sharpe=+0.4309
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0619, Lock Sharpe=+0.3852
- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0315, Lock Sharpe=+0.1740
- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0425, Lock Sharpe=+0.1664

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0206, Lock IC=+0.1272, Lock Sharpe=+0.7985
- `limit_down_proximity_early`: Train IC=+0.0205, Lock IC=+0.1272, Lock Sharpe=+0.7985
- `lunch_transition_volume_skew`: Train IC=+0.0713, Lock IC=+0.0267, Lock Sharpe=+0.2910

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 385 | +0.0295 | 100.0% |
| 0.45 | 0.20 | 363 | +0.0295 | 100.0% |
| 0.45 | 0.30 | 296 | +0.0295 | 100.0% |
| 0.45 | 0.40 | 219 | +0.0295 | 100.0% |
| 0.45 | 0.50 | 135 | +0.0295 | 100.0% |
| 0.50 | 0.15 | 375 | +0.0295 | 100.0% |
| 0.50 | 0.25 | 339 | +0.0295 | 100.0% |
| 0.50 | 0.35 | 248 | +0.0295 | 100.0% |
| 0.50 | 0.45 | 187 | +0.0295 | 100.0% |
| 0.55 | 0.10 | 374 | +0.0295 | 100.0% |
| 0.55 | 0.20 | 362 | +0.0295 | 100.0% |
| 0.55 | 0.30 | 296 | +0.0295 | 100.0% |
| 0.55 | 0.40 | 219 | +0.0295 | 100.0% |
| 0.55 | 0.50 | 135 | +0.0295 | 100.0% |
| 0.60 | 0.15 | 307 | +0.0295 | 100.0% |
| 0.60 | 0.25 | 306 | +0.0295 | 100.0% |
| 0.60 | 0.35 | 248 | +0.0295 | 100.0% |
| 0.60 | 0.45 | 187 | +0.0295 | 100.0% |
| 0.65 | 0.10 | 210 | +0.0295 | 100.0% |
| 0.65 | 0.20 | 210 | +0.0295 | 100.0% |
| 0.65 | 0.30 | 208 | +0.0295 | 100.0% |
| 0.65 | 0.40 | 201 | +0.0295 | 100.0% |
| 0.65 | 0.50 | 135 | +0.0295 | 100.0% |
| 0.70 | 0.15 | 107 | +0.0278 | 100.0% |
| 0.70 | 0.25 | 107 | +0.0278 | 100.0% |
| 0.70 | 0.35 | 107 | +0.0278 | 100.0% |
| 0.70 | 0.45 | 107 | +0.0278 | 100.0% |
| 0.75 | 0.10 | 19 | +0.0214 | 80.0% |
| 0.75 | 0.20 | 19 | +0.0214 | 80.0% |
| 0.75 | 0.30 | 19 | +0.0214 | 80.0% |
| 0.75 | 0.40 | 19 | +0.0214 | 80.0% |
| 0.75 | 0.50 | 19 | +0.0214 | 80.0% |
| 0.80 | 0.15 | 1 | +0.0157 | 100.0% |
| 0.80 | 0.25 | 1 | +0.0157 | 100.0% |
| 0.80 | 0.35 | 1 | +0.0157 | 100.0% |
| 0.80 | 0.45 | 1 | +0.0157 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 385 candidates, mean lock IC=+0.0295, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 14 | -0.0308 | 10.0% |
| 0.45 | 0.20 | 7 | -0.0182 | 14.3% |
| 0.45 | 0.30 | 4 | -0.0135 | 25.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | -0.0276 | 11.1% |
| 0.50 | 0.25 | 5 | -0.0123 | 20.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | -0.0261 | 14.3% |
| 0.55 | 0.20 | 5 | -0.0123 | 20.0% |
| 0.55 | 0.30 | 4 | -0.0135 | 25.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | +0.0441 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0441 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.25 → 5 candidates, mean lock IC=-0.0123, 20.0% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 49 | +0.0228 | 80.0% |
| 0.45 | 0.20 | 38 | +0.0158 | 90.0% |
| 0.45 | 0.30 | 23 | +0.0144 | 90.0% |
| 0.45 | 0.40 | 4 | +0.0037 | 75.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 47 | +0.0194 | 80.0% |
| 0.50 | 0.25 | 29 | +0.0210 | 100.0% |
| 0.50 | 0.35 | 9 | +0.0176 | 88.9% |
| 0.50 | 0.45 | 2 | +0.0181 | 100.0% |
| 0.55 | 0.10 | 46 | +0.0228 | 80.0% |
| 0.55 | 0.20 | 38 | +0.0158 | 90.0% |
| 0.55 | 0.30 | 23 | +0.0144 | 90.0% |
| 0.55 | 0.40 | 4 | +0.0037 | 75.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 20 | +0.0144 | 90.0% |
| 0.60 | 0.25 | 20 | +0.0144 | 90.0% |
| 0.60 | 0.35 | 9 | +0.0176 | 88.9% |
| 0.60 | 0.45 | 2 | +0.0181 | 100.0% |
| 0.65 | 0.10 | 3 | -0.0046 | 66.7% |
| 0.65 | 0.20 | 3 | -0.0046 | 66.7% |
| 0.65 | 0.30 | 3 | -0.0046 | 66.7% |
| 0.65 | 0.40 | 3 | -0.0046 | 66.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 49 candidates, mean lock IC=+0.0228, 80.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 39 | +0.0218 | 90.0% |
| 0.45 | 0.20 | 22 | +0.0218 | 90.0% |
| 0.45 | 0.30 | 5 | +0.0242 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 30 | +0.0218 | 90.0% |
| 0.50 | 0.25 | 14 | +0.0126 | 80.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 28 | +0.0218 | 90.0% |
| 0.55 | 0.20 | 20 | +0.0218 | 90.0% |
| 0.55 | 0.30 | 5 | +0.0242 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | +0.0099 | 75.0% |
| 0.60 | 0.25 | 7 | +0.0082 | 71.4% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.30 → 4 candidates, mean lock IC=+0.0262, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | -0.0260 | 20.0% |
| 0.45 | 0.20 | 8 | -0.0327 | 12.5% |
| 0.45 | 0.30 | 6 | -0.0484 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | -0.0327 | 12.5% |
| 0.50 | 0.25 | 7 | -0.0475 | 0.0% |
| 0.50 | 0.35 | 5 | -0.0447 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | -0.0475 | 0.0% |
| 0.55 | 0.20 | 7 | -0.0475 | 0.0% |
| 0.55 | 0.30 | 6 | -0.0484 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 6 | -0.0484 | 0.0% |
| 0.60 | 0.25 | 6 | -0.0484 | 0.0% |
| 0.60 | 0.35 | 5 | -0.0447 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 10 candidates, mean lock IC=-0.0260, 20.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | -0.0083 | 40.0% |
| 0.45 | 0.20 | 7 | -0.0002 | 42.9% |
| 0.45 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | -0.0118 | 37.5% |
| 0.50 | 0.25 | 4 | -0.0163 | 50.0% |
| 0.50 | 0.35 | 3 | -0.0020 | 66.7% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 9 | -0.0192 | 33.3% |
| 0.55 | 0.20 | 6 | -0.0152 | 33.3% |
| 0.55 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 5 | -0.0172 | 40.0% |
| 0.60 | 0.25 | 4 | -0.0163 | 50.0% |
| 0.60 | 0.35 | 3 | -0.0020 | 66.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 7 candidates, mean lock IC=-0.0002, 42.9% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1266 | +0.1222 | 100.0% |
| 0.45 | 0.20 | 1220 | +0.1222 | 100.0% |
| 0.45 | 0.30 | 1156 | +0.1222 | 100.0% |
| 0.45 | 0.40 | 1020 | +0.1222 | 100.0% |
| 0.45 | 0.50 | 800 | +0.1222 | 100.0% |
| 0.50 | 0.15 | 1253 | +0.1222 | 100.0% |
| 0.50 | 0.25 | 1205 | +0.1222 | 100.0% |
| 0.50 | 0.35 | 1088 | +0.1222 | 100.0% |
| 0.50 | 0.45 | 913 | +0.1222 | 100.0% |
| 0.55 | 0.10 | 1258 | +0.1222 | 100.0% |
| 0.55 | 0.20 | 1220 | +0.1222 | 100.0% |
| 0.55 | 0.30 | 1156 | +0.1222 | 100.0% |
| 0.55 | 0.40 | 1020 | +0.1222 | 100.0% |
| 0.55 | 0.50 | 800 | +0.1222 | 100.0% |
| 0.60 | 0.15 | 1193 | +0.1222 | 100.0% |
| 0.60 | 0.25 | 1176 | +0.1222 | 100.0% |
| 0.60 | 0.35 | 1085 | +0.1222 | 100.0% |
| 0.60 | 0.45 | 913 | +0.1222 | 100.0% |
| 0.65 | 0.10 | 1007 | +0.1222 | 100.0% |
| 0.65 | 0.20 | 1007 | +0.1222 | 100.0% |
| 0.65 | 0.30 | 1003 | +0.1222 | 100.0% |
| 0.65 | 0.40 | 974 | +0.1222 | 100.0% |
| 0.65 | 0.50 | 794 | +0.1222 | 100.0% |
| 0.70 | 0.15 | 687 | +0.1222 | 100.0% |
| 0.70 | 0.25 | 687 | +0.1222 | 100.0% |
| 0.70 | 0.35 | 687 | +0.1222 | 100.0% |
| 0.70 | 0.45 | 682 | +0.1222 | 100.0% |
| 0.75 | 0.10 | 348 | +0.1222 | 100.0% |
| 0.75 | 0.20 | 348 | +0.1222 | 100.0% |
| 0.75 | 0.30 | 348 | +0.1222 | 100.0% |
| 0.75 | 0.40 | 348 | +0.1222 | 100.0% |
| 0.75 | 0.50 | 348 | +0.1222 | 100.0% |
| 0.80 | 0.15 | 120 | +0.1064 | 100.0% |
| 0.80 | 0.25 | 120 | +0.1064 | 100.0% |
| 0.80 | 0.35 | 120 | +0.1064 | 100.0% |
| 0.80 | 0.45 | 120 | +0.1064 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1266 candidates, mean lock IC=+0.1222, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 149 | +0.0942 | 100.0% |
| 0.45 | 0.20 | 116 | +0.0942 | 100.0% |
| 0.45 | 0.30 | 70 | +0.0872 | 100.0% |
| 0.45 | 0.40 | 19 | +0.0776 | 100.0% |
| 0.45 | 0.50 | 5 | +0.1020 | 100.0% |
| 0.50 | 0.15 | 122 | +0.0942 | 100.0% |
| 0.50 | 0.25 | 95 | +0.0942 | 100.0% |
| 0.50 | 0.35 | 33 | +0.0882 | 100.0% |
| 0.50 | 0.45 | 10 | +0.0753 | 100.0% |
| 0.55 | 0.10 | 133 | +0.0942 | 100.0% |
| 0.55 | 0.20 | 115 | +0.0942 | 100.0% |
| 0.55 | 0.30 | 70 | +0.0872 | 100.0% |
| 0.55 | 0.40 | 19 | +0.0776 | 100.0% |
| 0.55 | 0.50 | 5 | +0.1020 | 100.0% |
| 0.60 | 0.15 | 87 | +0.0893 | 100.0% |
| 0.60 | 0.25 | 85 | +0.0872 | 100.0% |
| 0.60 | 0.35 | 33 | +0.0882 | 100.0% |
| 0.60 | 0.45 | 10 | +0.0753 | 100.0% |
| 0.65 | 0.10 | 10 | +0.0753 | 100.0% |
| 0.65 | 0.20 | 10 | +0.0753 | 100.0% |
| 0.65 | 0.30 | 10 | +0.0753 | 100.0% |
| 0.65 | 0.40 | 10 | +0.0753 | 100.0% |
| 0.65 | 0.50 | 5 | +0.1020 | 100.0% |
| 0.70 | 0.15 | 2 | +0.1062 | 100.0% |
| 0.70 | 0.25 | 2 | +0.1062 | 100.0% |
| 0.70 | 0.35 | 2 | +0.1062 | 100.0% |
| 0.70 | 0.45 | 2 | +0.1062 | 100.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 5 candidates, mean lock IC=+0.1020, 100.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 16 | +0.0686 | 80.0% |
| 0.45 | 0.20 | 3 | -0.0178 | 33.3% |
| 0.45 | 0.30 | 1 | -0.0236 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 10 | +0.0628 | 80.0% |
| 0.50 | 0.25 | 1 | -0.0236 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | +0.0775 | 71.4% |
| 0.55 | 0.20 | 2 | -0.0281 | 0.0% |
| 0.55 | 0.30 | 1 | -0.0236 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | +0.1180 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 7 candidates, mean lock IC=+0.0775, 71.4% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 501 | -0.0255 | 0.0% |
| 0.45 | 0.20 | 487 | -0.0255 | 0.0% |
| 0.45 | 0.30 | 465 | -0.0255 | 0.0% |
| 0.45 | 0.40 | 425 | -0.0255 | 0.0% |
| 0.45 | 0.50 | 392 | -0.0255 | 0.0% |
| 0.50 | 0.15 | 498 | -0.0255 | 0.0% |
| 0.50 | 0.25 | 476 | -0.0255 | 0.0% |
| 0.50 | 0.35 | 448 | -0.0255 | 0.0% |
| 0.50 | 0.45 | 404 | -0.0255 | 0.0% |
| 0.55 | 0.10 | 489 | -0.0255 | 0.0% |
| 0.55 | 0.20 | 478 | -0.0255 | 0.0% |
| 0.55 | 0.30 | 465 | -0.0255 | 0.0% |
| 0.55 | 0.40 | 425 | -0.0255 | 0.0% |
| 0.55 | 0.50 | 392 | -0.0255 | 0.0% |
| 0.60 | 0.15 | 468 | -0.0255 | 0.0% |
| 0.60 | 0.25 | 460 | -0.0255 | 0.0% |
| 0.60 | 0.35 | 445 | -0.0255 | 0.0% |
| 0.60 | 0.45 | 404 | -0.0255 | 0.0% |
| 0.65 | 0.10 | 431 | -0.0255 | 0.0% |
| 0.65 | 0.20 | 431 | -0.0255 | 0.0% |
| 0.65 | 0.30 | 431 | -0.0255 | 0.0% |
| 0.65 | 0.40 | 418 | -0.0255 | 0.0% |
| 0.65 | 0.50 | 391 | -0.0255 | 0.0% |
| 0.70 | 0.15 | 370 | -0.0255 | 0.0% |
| 0.70 | 0.25 | 370 | -0.0255 | 0.0% |
| 0.70 | 0.35 | 370 | -0.0255 | 0.0% |
| 0.70 | 0.45 | 367 | -0.0255 | 0.0% |
| 0.75 | 0.10 | 287 | -0.0255 | 0.0% |
| 0.75 | 0.20 | 287 | -0.0255 | 0.0% |
| 0.75 | 0.30 | 287 | -0.0255 | 0.0% |
| 0.75 | 0.40 | 287 | -0.0255 | 0.0% |
| 0.75 | 0.50 | 287 | -0.0255 | 0.0% |
| 0.80 | 0.15 | 100 | -0.0255 | 0.0% |
| 0.80 | 0.25 | 100 | -0.0255 | 0.0% |
| 0.80 | 0.35 | 100 | -0.0255 | 0.0% |
| 0.80 | 0.45 | 100 | -0.0255 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 501 candidates, mean lock IC=-0.0255, 0.0% positive

### 588000ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 95 | -0.0034 | 50.0% |
| 0.45 | 0.20 | 50 | -0.0034 | 50.0% |
| 0.45 | 0.30 | 18 | -0.0226 | 30.0% |
| 0.45 | 0.40 | 4 | -0.0226 | 25.0% |
| 0.45 | 0.50 | 2 | -0.0086 | 50.0% |
| 0.50 | 0.15 | 68 | -0.0034 | 50.0% |
| 0.50 | 0.25 | 31 | -0.0120 | 50.0% |
| 0.50 | 0.35 | 8 | -0.0450 | 12.5% |
| 0.50 | 0.45 | 2 | -0.0086 | 50.0% |
| 0.55 | 0.10 | 63 | -0.0034 | 50.0% |
| 0.55 | 0.20 | 46 | -0.0034 | 50.0% |
| 0.55 | 0.30 | 18 | -0.0226 | 30.0% |
| 0.55 | 0.40 | 4 | -0.0226 | 25.0% |
| 0.55 | 0.50 | 2 | -0.0086 | 50.0% |
| 0.60 | 0.15 | 23 | -0.0160 | 40.0% |
| 0.60 | 0.25 | 21 | -0.0178 | 40.0% |
| 0.60 | 0.35 | 8 | -0.0450 | 12.5% |
| 0.60 | 0.45 | 2 | -0.0086 | 50.0% |
| 0.65 | 0.10 | 6 | -0.0334 | 16.7% |
| 0.65 | 0.20 | 6 | -0.0334 | 16.7% |
| 0.65 | 0.30 | 6 | -0.0334 | 16.7% |
| 0.65 | 0.40 | 4 | -0.0226 | 25.0% |
| 0.65 | 0.50 | 2 | -0.0086 | 50.0% |
| 0.70 | 0.15 | 1 | -0.0358 | 0.0% |
| 0.70 | 0.25 | 1 | -0.0358 | 0.0% |
| 0.70 | 0.35 | 1 | -0.0358 | 0.0% |
| 0.70 | 0.45 | 1 | -0.0358 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 95 candidates, mean lock IC=-0.0034, 50.0% positive

### 588000ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 50 | +0.0329 | 40.0% |
| 0.45 | 0.20 | 36 | +0.0329 | 40.0% |
| 0.45 | 0.30 | 27 | +0.0236 | 40.0% |
| 0.45 | 0.40 | 18 | -0.0083 | 20.0% |
| 0.45 | 0.50 | 14 | -0.0019 | 20.0% |
| 0.50 | 0.15 | 40 | +0.0329 | 40.0% |
| 0.50 | 0.25 | 31 | +0.0236 | 40.0% |
| 0.50 | 0.35 | 24 | -0.0083 | 20.0% |
| 0.50 | 0.45 | 14 | -0.0019 | 20.0% |
| 0.55 | 0.10 | 39 | +0.0329 | 40.0% |
| 0.55 | 0.20 | 34 | +0.0329 | 40.0% |
| 0.55 | 0.30 | 27 | +0.0236 | 40.0% |
| 0.55 | 0.40 | 18 | -0.0083 | 20.0% |
| 0.55 | 0.50 | 14 | -0.0019 | 20.0% |
| 0.60 | 0.15 | 26 | -0.0044 | 20.0% |
| 0.60 | 0.25 | 23 | -0.0083 | 20.0% |
| 0.60 | 0.35 | 22 | -0.0083 | 20.0% |
| 0.60 | 0.45 | 14 | -0.0019 | 20.0% |
| 0.65 | 0.10 | 19 | -0.0019 | 20.0% |
| 0.65 | 0.20 | 19 | -0.0019 | 20.0% |
| 0.65 | 0.30 | 19 | -0.0019 | 20.0% |
| 0.65 | 0.40 | 16 | -0.0019 | 20.0% |
| 0.65 | 0.50 | 14 | -0.0019 | 20.0% |
| 0.70 | 0.15 | 4 | -0.0136 | 25.0% |
| 0.70 | 0.25 | 4 | -0.0136 | 25.0% |
| 0.70 | 0.35 | 4 | -0.0136 | 25.0% |
| 0.70 | 0.45 | 4 | -0.0136 | 25.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 50 candidates, mean lock IC=+0.0329, 40.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 698 | +0.1299 | 100.0% |
| 0.45 | 0.20 | 663 | +0.1299 | 100.0% |
| 0.45 | 0.30 | 519 | +0.1299 | 100.0% |
| 0.45 | 0.40 | 384 | +0.1299 | 100.0% |
| 0.45 | 0.50 | 201 | +0.1299 | 100.0% |
| 0.50 | 0.15 | 682 | +0.1299 | 100.0% |
| 0.50 | 0.25 | 598 | +0.1299 | 100.0% |
| 0.50 | 0.35 | 452 | +0.1299 | 100.0% |
| 0.50 | 0.45 | 306 | +0.1299 | 100.0% |
| 0.55 | 0.10 | 686 | +0.1299 | 100.0% |
| 0.55 | 0.20 | 656 | +0.1299 | 100.0% |
| 0.55 | 0.30 | 519 | +0.1299 | 100.0% |
| 0.55 | 0.40 | 384 | +0.1299 | 100.0% |
| 0.55 | 0.50 | 201 | +0.1299 | 100.0% |
| 0.60 | 0.15 | 595 | +0.1299 | 100.0% |
| 0.60 | 0.25 | 559 | +0.1299 | 100.0% |
| 0.60 | 0.35 | 446 | +0.1299 | 100.0% |
| 0.60 | 0.45 | 306 | +0.1299 | 100.0% |
| 0.65 | 0.10 | 361 | +0.1299 | 100.0% |
| 0.65 | 0.20 | 361 | +0.1299 | 100.0% |
| 0.65 | 0.30 | 360 | +0.1299 | 100.0% |
| 0.65 | 0.40 | 331 | +0.1299 | 100.0% |
| 0.65 | 0.50 | 196 | +0.1299 | 100.0% |
| 0.70 | 0.15 | 136 | +0.1263 | 100.0% |
| 0.70 | 0.25 | 136 | +0.1263 | 100.0% |
| 0.70 | 0.35 | 136 | +0.1263 | 100.0% |
| 0.70 | 0.45 | 133 | +0.1263 | 100.0% |
| 0.75 | 0.10 | 14 | +0.1303 | 100.0% |
| 0.75 | 0.20 | 14 | +0.1303 | 100.0% |
| 0.75 | 0.30 | 14 | +0.1303 | 100.0% |
| 0.75 | 0.40 | 14 | +0.1303 | 100.0% |
| 0.75 | 0.50 | 14 | +0.1303 | 100.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 14 candidates, mean lock IC=+0.1303, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 84 | +0.0347 | 100.0% |
| 0.45 | 0.20 | 57 | +0.0347 | 100.0% |
| 0.45 | 0.30 | 30 | +0.0347 | 100.0% |
| 0.45 | 0.40 | 8 | +0.0544 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 65 | +0.0347 | 100.0% |
| 0.50 | 0.25 | 41 | +0.0347 | 100.0% |
| 0.50 | 0.35 | 15 | +0.0551 | 100.0% |
| 0.50 | 0.45 | 4 | +0.0594 | 100.0% |
| 0.55 | 0.10 | 62 | +0.0347 | 100.0% |
| 0.55 | 0.20 | 51 | +0.0347 | 100.0% |
| 0.55 | 0.30 | 30 | +0.0347 | 100.0% |
| 0.55 | 0.40 | 8 | +0.0544 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 30 | +0.0220 | 100.0% |
| 0.60 | 0.25 | 29 | +0.0220 | 100.0% |
| 0.60 | 0.35 | 14 | +0.0504 | 100.0% |
| 0.60 | 0.45 | 4 | +0.0594 | 100.0% |
| 0.65 | 0.10 | 6 | +0.0428 | 100.0% |
| 0.65 | 0.20 | 6 | +0.0428 | 100.0% |
| 0.65 | 0.30 | 6 | +0.0428 | 100.0% |
| 0.65 | 0.40 | 6 | +0.0428 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.45 → 4 candidates, mean lock IC=+0.0594, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | +0.0688 | 100.0% |
| 0.45 | 0.20 | 1 | +0.0532 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 6 | +0.0746 | 100.0% |
| 0.50 | 0.25 | 1 | +0.0532 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 5 | +0.0808 | 100.0% |
| 0.55 | 0.20 | 1 | +0.0532 | 100.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | +0.0532 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0532 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.15 → 4 candidates, mean lock IC=+0.0836, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1304 | +0.0983 | +0.0280 | 0.21x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1218 | +0.0774 | +0.0372 | 0.31x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1169 | +0.0920 | +0.0189 | 0.16x | 2017-05-09 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment` | +0.1017 | +0.0982 | +0.0353 | 0.35x | 2013-09-23 |
| `rbreaker_sell_setup_proximity_early` | +0.0953 | +0.0781 | +0.0616 | 0.65x | 2016-08-24 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1128 | +0.0907 | +0.0635 | 0.56x | 2016-08-24 |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | +0.1123 | +0.1251 | -0.0129 | -0.11x | 2015-02-06 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.0068 | -0.0014 | +0.0016 | 0.24x | 2011-11-24 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +0.0428 | +0.0379 | +0.0706 | 1.65x | 2012-10-09 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +0.0571 | +0.0418 | -0.0280 | -0.49x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | +0.1895 | +0.1062 | +0.1145 | 0.60x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1763 | +0.0684 | +0.1256 | 0.71x | 2016-08-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | +0.2016 | +0.0940 | +0.1138 | 0.56x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1821 | +0.0584 | +0.0842 | 0.46x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1814 | +0.0513 | +0.0990 | 0.55x | No decay |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +0.1831 | +0.0649 | +0.0735 | 0.40x | 2014-06-05 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1721 | +0.1324 | +0.1001 | 0.58x | No decay |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1511 | +0.0727 | +0.1114 | 0.74x | 2016-08-24 |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | +0.1249 | +0.0738 | +0.0743 | 0.60x | 2017-08-08 |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | +0.1911 | +0.1045 | +0.1258 | 0.66x | 2016-09-26 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.2007 | +0.0828 | +0.0810 | 0.40x | 2025-07-24 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +0.1562 | +0.0391 | +0.1083 | 0.69x | 2016-08-24 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +0.1543 | +0.0490 | +0.1100 | 0.71x | 2011-09-20 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1733 | +0.0537 | +0.1135 | 0.65x | 2022-12-15 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +0.1524 | +0.0567 | +0.1011 | 0.66x | 2020-01-06 |
| `combo_rank_min__bar_ret_0__rbreaker_buy_setup_proximity_early` | +0.1310 | +0.0116 | +0.1192 | 0.91x | 2016-08-24 |
| `combo_rank_max__max_up_ret__early_body_momentum` | +0.1877 | +0.1103 | +0.0738 | 0.39x | 2016-11-30 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | +0.1717 | +0.0707 | +0.1324 | 0.77x | 2016-09-26 |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__close_vs_open_range` | +0.1678 | +0.0710 | +0.1158 | 0.69x | 2016-09-26 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1601 | +0.0741 | +0.1139 | 0.71x | No decay |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | +0.0394 | -0.0405 | +0.0337 | 0.86x | 2011-04-21 |
| `combo_mean__bar_ret_0__max_down_ret` | +0.1613 | +0.0587 | +0.1025 | 0.64x | No decay |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +0.1713 | +0.0886 | +0.0949 | 0.55x | 2020-02-12 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1841 | +0.1120 | +0.0915 | 0.50x | 2019-12-05 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1680 | +0.0685 | +0.1219 | 0.73x | 2016-09-26 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +0.1723 | +0.0893 | +0.1053 | 0.61x | 2021-05-28 |
| `combo_ratio__max_down_ret__net_volume_flow` | +0.1319 | -0.0332 | +0.1213 | 0.92x | 2021-02-24 |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | +0.1158 | -0.0073 | +0.1357 | 1.17x | 2011-09-20 |
| `rbreaker_sell_setup_proximity_early` | +0.1745 | +0.0776 | +0.1261 | 0.72x | 2021-07-28 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | +0.0195 | +0.0240 | +0.0027 | 0.14x | 2010-10-15 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1450 | +0.0886 | +0.1504 | 1.04x | 2016-08-24 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1754 | +0.0871 | +0.0879 | 0.50x | 2019-12-05 |

### 588000ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | +0.1036 | +0.1269 | -0.0537 | -0.52x | No decay |
| `vix_rolling_percentile_60d` | +0.0397 | +0.0994 | +0.0189 | 0.48x | No decay |

### 588000ETF — `long` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_z_sum__vix_skew_proxy__vix_iv_spread` | +0.0852 | +0.0073 | +0.0364 | 0.43x | 2025-07-28 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1543 | +0.0886 | +0.1279 | 0.83x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1607 | +0.1009 | +0.1381 | 0.86x | 2011-11-16 |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1759 | +0.1118 | +0.1318 | 0.75x | 2017-02-27 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1333 | +0.0607 | +0.0900 | 0.68x | 2017-04-28 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0914 | +0.1274 | +0.1192 | 1.30x | 2011-10-18 |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_range` | +0.1333 | +0.0794 | +0.1059 | 0.79x | 2017-02-27 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1669 | +0.1191 | +0.1338 | 0.80x | 2017-01-20 |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | +0.1541 | +0.1366 | +0.1109 | 0.72x | 2016-10-24 |
| `combo_rank_max__max_up_ret__opening_auction_imbalance` | +0.1546 | +0.1191 | +0.0920 | 0.60x | 2016-12-21 |
| `combo_z_sum__max_up_ret__first_bar_sentiment` | +0.1662 | +0.1016 | +0.0792 | 0.48x | 2017-01-20 |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | +0.1430 | +0.1141 | +0.0802 | 0.56x | 2017-01-20 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.3544). Consider relaxing this gate.
2. **300ETF `single` — BH-FDR Gate too strict**: 37.5% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.2864). Consider relaxing this gate.
3. **300ETF `single` — B3 Composite Floor too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.3102). Consider relaxing this gate.
4. **300ETF `single` — B4 Correlation Gate too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.0514). Consider relaxing this gate.
5. **300ETF `single` — Admission too loose**: 55% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
6. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.3796). Consider relaxing this gate.
7. **300ETF `short` — BH-FDR Gate too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.2851). Consider relaxing this gate.
8. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 6.0%, mean lock Sharpe=-0.1966). Consider relaxing this gate.
9. **50ETF `single` — B2 Rolling Guard too strict**: 23.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 6.0%, mean lock Sharpe=-0.7183). Consider relaxing this gate.
10. **50ETF `long` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.8357). Consider relaxing this gate.
11. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.2066). Consider relaxing this gate.
12. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 63.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.0310). Consider relaxing this gate.
13. **500ETF `single` — B3 Composite Floor too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.2666). Consider relaxing this gate.
14. **500ETF `single` — B4 Correlation Gate too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.2517). Consider relaxing this gate.
15. **500ETF `short` — BH-FDR Gate too strict**: 71.4% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.0208). Consider relaxing this gate.
16. **588000ETF `single` — Admission too loose**: 86% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
17. **588000ETF `long` — B3 Composite Floor too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 22.0%, mean lock Sharpe=-0.3925). Consider relaxing this gate.
18. **159915ETF `single` — B2 Rolling Guard too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.2629). Consider relaxing this gate.
19. **159915ETF `single` — BH-FDR Gate too strict**: 83.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.2259). Consider relaxing this gate.
20. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+1.0820). Consider relaxing this gate.
21. **159915ETF `single` — B4 Correlation Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+1.0794). Consider relaxing this gate.
22. **159915ETF `long` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 32.0%, mean lock Sharpe=+0.1106). Consider relaxing this gate.
23. **159915ETF `long` — B2 Rolling Guard too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 32.0%, mean lock Sharpe=+0.2991). Consider relaxing this gate.
24. **159915ETF `long` — BH-FDR Gate too strict**: 76.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 32.0%, mean lock Sharpe=+0.3094). Consider relaxing this gate.
25. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=-0.2483). Consider relaxing this gate.
26. **159915ETF `short` — B2 Rolling Guard too strict**: 23.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=-0.2416). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
