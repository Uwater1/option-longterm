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

### 300ETF — `single` (Full Model Lockbox IC: -0.0276, Sharpe: +0.0000)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.0742 | -0.0463 | -0.0463 | -2.3158 | 80.02 | -13.5 | -1.68x | -0.0175 | +0.8198 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.0874 | +0.0007 | +0.0007 | -1.2814 | 85.92 | -2.4 | -0.31x | +0.0116 | +0.0000 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.0880 | -0.0172 | -0.0172 | -1.4760 | 89.20 | -1.7 | -0.21x | +0.0024 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0352, Sharpe: -0.7475)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1070 | +0.0564 | +0.0564 | -1.6519 | 86.58 | -7.0 | -0.87x | +0.0087 | -0.7475 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0995 | -0.0041 | -0.0041 | -2.4279 | 91.83 | -21.9 | -2.73x | -0.0081 | -0.7475 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1323 | +0.0308 | +0.0308 | -2.1159 | 89.20 | -15.9 | -1.98x | -0.0063 | -0.0422 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1160 | +0.0404 | +0.0404 | -0.7263 | 80.68 | -0.8 | -0.10x | +0.0034 | -0.7475 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0926 | +0.0323 | +0.0323 | -0.6894 | 89.20 | +3.0 | 0.37x | +0.0021 | -0.7475 |
| `num_up_bars` | Other Technical | +1 | +0.0907 | +0.0459 | +0.0459 | -1.5665 | 87.89 | -8.4 | -1.05x | +0.0018 | -0.1641 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.0854, Sharpe: +0.0174)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1150 | +0.0792 | +0.0792 | -0.1046 | 89.20 | +12.6 | 1.58x | -0.0035 | -0.3093 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1114 | +0.0682 | +0.0682 | -0.9705 | 87.24 | -3.8 | -0.48x | -0.0105 | -0.4434 |
| `bar_body_rng_0` | Other Technical | +1 | +0.1040 | +0.0977 | +0.0977 | -0.3725 | 87.24 | +7.6 | 0.94x | +0.0114 | +0.0854 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 41.0% lock IC > 0, 7.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9408_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 179 | 30 | 50.0% | 6.7% | +0.0127 | -0.9830 |
| B2 Rolling Guard | 20 | 20 | 30.0% | 0.0% | +0.0024 | -0.4100 |
| BH-FDR Gate | 13 | 13 | 30.8% | 0.0% | -0.0119 | -1.0820 |
| B3 Composite Floor | 2 | 2 | 50.0% | 0.0% | -0.0166 | -1.2499 |
| B4 Correlation Gate | 2 | 2 | 100.0% | 0.0% | +0.0108 | -1.3506 |

**Admitted Pool Summary**: 3 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0209, Mean Lock Sharpe = -1.6911

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.0992, Lock IC=+0.0932, Lock Sharpe=+0.2652
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0992, Lock IC=+0.0932, Lock Sharpe=+0.2652

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 50.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9952_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 208 | 30 | 56.7% | 20.0% | +0.0061 | -0.8624 |
| B2 Rolling Guard | 22 | 22 | 18.2% | 0.0% | -0.0095 | -0.5657 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0266 | -1.6162 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma200_dist`: Train IC=+0.1387, Lock IC=+0.0286, Lock Sharpe=+0.7878
- `first_bar_volume`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.3869
- `bar_vol_0`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.3869
- `volume_surge_max`: Train IC=+0.1279, Lock IC=+0.0659, Lock Sharpe=+0.3869
- `volume_concentration`: Train IC=+0.1149, Lock IC=+0.0409, Lock Sharpe=+0.1878

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 56.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6150_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 200 | 30 | 70.0% | 26.7% | +0.0275 | -0.5324 |
| B2 Rolling Guard | 33 | 30 | 30.0% | 13.3% | -0.0039 | -0.2098 |
| BH-FDR Gate | 3 | 3 | 66.7% | 33.3% | +0.0375 | -0.3143 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_body_ratio`: Train IC=+0.0921, Lock IC=+0.0553, Lock Sharpe=+0.5891
- `star50_limit_proximity_early`: Train IC=+0.1240, Lock IC=+0.0960, Lock Sharpe=+0.5041
- `yesterday_am_return`: Train IC=+0.0762, Lock IC=+0.0566, Lock Sharpe=+0.5035
- `sma_distance_5d`: Train IC=+0.0809, Lock IC=+0.0703, Lock Sharpe=+0.4493
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1502, Lock IC=+0.0932, Lock Sharpe=+0.3848

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `pullback_depth_ratio`: Train IC=+0.0000, Lock IC=+0.0504, Lock Sharpe=+1.2109
- `double_bottom_bull_flag_early`: Train IC=+0.0000, Lock IC=+0.0395, Lock Sharpe=+0.8652
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0389, Lock Sharpe=+0.7726
- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.0018, Lock Sharpe=+0.7023

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `gap_pct`: Train IC=+0.1402, Lock IC=+0.1085, Lock Sharpe=+0.3084

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 48.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -1.2691_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 187 | 30 | 66.7% | 16.7% | +0.0166 | -0.9403 |
| B2 Rolling Guard | 20 | 20 | 30.0% | 0.0% | +0.0084 | -0.7531 |
| BH-FDR Gate | 7 | 7 | 14.3% | 0.0% | -0.0363 | -1.6042 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `coppock_curve_day`: Train IC=+0.1161, Lock IC=+0.0618, Lock Sharpe=+0.8134
- `limit_down_proximity_early`: Train IC=+0.1004, Lock IC=+0.0899, Lock Sharpe=+0.5951
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1004, Lock IC=+0.0898, Lock Sharpe=+0.5951
- `vol20`: Train IC=+0.0745, Lock IC=+0.0448, Lock Sharpe=+0.0567
- `iv`: Train IC=+0.0934, Lock IC=+0.0341, Lock Sharpe=+0.0408

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 3.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -1.2854_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 199 | 30 | 40.0% | 0.0% | -0.0073 | -1.7957 |
| B2 Rolling Guard | 24 | 24 | 16.7% | 4.2% | -0.0049 | -0.8130 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0367 | -2.1841 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bb_width`: Train IC=+0.0518, Lock IC=+0.1414, Lock Sharpe=+0.1829

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 53.0% lock IC > 0, 19.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6297_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 200 | 30 | 70.0% | 46.7% | +0.0346 | -0.0604 |
| B2 Rolling Guard | 35 | 30 | 30.0% | 16.7% | +0.0070 | -0.2418 |
| BH-FDR Gate | 2 | 2 | 100.0% | 50.0% | +0.0198 | -0.2242 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma20_dist`: Train IC=+0.1468, Lock IC=+0.1018, Lock Sharpe=+1.3678
- `macd_hist`: Train IC=+0.0894, Lock IC=+0.1028, Lock Sharpe=+1.2599
- `ema12_dist`: Train IC=+0.1221, Lock IC=+0.1201, Lock Sharpe=+1.0583
- `roc10`: Train IC=+0.1218, Lock IC=+0.0738, Lock Sharpe=+0.9516
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1886, Lock IC=+0.0898, Lock Sharpe=+0.9237

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.1163, Lock IC=+0.1636, Lock Sharpe=+1.6137
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0727, Lock Sharpe=+0.9495
- `close_vs_open_range`: Train IC=+0.0193, Lock IC=+0.0427, Lock Sharpe=+0.6242
- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0277, Lock Sharpe=+0.2254
- `roc5`: Train IC=+0.0684, Lock IC=+0.0977, Lock Sharpe=+0.1110

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1148, Lock IC=+0.0302, Lock Sharpe=+0.0428

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 54.0% lock IC > 0, 9.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7218_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 156 | 30 | 76.7% | 10.0% | +0.0263 | -0.6739 |
| B2 Rolling Guard | 28 | 28 | 39.3% | 14.3% | +0.0094 | -0.3460 |
| BH-FDR Gate | 6 | 6 | 0.0% | 0.0% | -0.0211 | -1.1015 |
| B3 Composite Floor | 8 | 8 | 75.0% | 0.0% | +0.0339 | -1.3584 |
| B4 Correlation Gate | 12 | 12 | 100.0% | 0.0% | +0.0458 | -0.9575 |

**Admitted Pool Summary**: 6 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0336, Mean Lock Sharpe = -1.5296

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_10_60`: Train IC=+0.0826, Lock IC=+0.0339, Lock Sharpe=+0.8531
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1293, Lock IC=+0.1243, Lock Sharpe=+0.3509
- `impulse_bar_dominance`: Train IC=+0.0838, Lock IC=+0.0696, Lock Sharpe=+0.2362

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `double_bottom_bull_flag_early`: Train IC=+0.0827, Lock IC=+0.0586, Lock Sharpe=+0.6526
- `vix_iv_ratio`: Train IC=+0.0665, Lock IC=+0.0599, Lock Sharpe=+0.3749
- `iv_diff_1d`: Train IC=+0.0902, Lock IC=+0.0868, Lock Sharpe=+0.1562
- `vix_iv_spread`: Train IC=-0.0004, Lock IC=+0.0707, Lock Sharpe=+0.0584

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5678_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 208 | 30 | 60.0% | 16.7% | +0.0073 | -0.5486 |
| B2 Rolling Guard | 22 | 22 | 31.8% | 18.2% | +0.0066 | -0.1871 |
| BH-FDR Gate | 5 | 5 | 60.0% | 20.0% | +0.0092 | -0.4535 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `max_down_ret`: Train IC=+0.0834, Lock IC=+0.0790, Lock Sharpe=+0.8525
- `shaved_bar_trend_conviction`: Train IC=+0.0928, Lock IC=+0.0469, Lock Sharpe=+0.5462
- `iv_diff_1d`: Train IC=+0.1163, Lock IC=+0.0868, Lock Sharpe=+0.4705
- `iv`: Train IC=+0.1061, Lock IC=+0.0251, Lock Sharpe=+0.1353
- `bar_rng_2`: Train IC=+0.1209, Lock IC=+0.0579, Lock Sharpe=+0.1342

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_iv_ratio`: Train IC=-0.0066, Lock IC=+0.0599, Lock Sharpe=+0.7432
- `volume_weighted_trend_strength_10d`: Train IC=+0.0000, Lock IC=+0.0602, Lock Sharpe=+0.4893
- `vix_iv_spread`: Train IC=-0.0091, Lock IC=+0.0707, Lock Sharpe=+0.4890
- `measured_move_proximity`: Train IC=+0.0000, Lock IC=+0.0769, Lock Sharpe=+0.3731

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `consecutive_higher_highs`: Train IC=+0.0559, Lock IC=+0.0050, Lock Sharpe=+0.5421

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 42.0% lock IC > 0, 11.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5608_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 199 | 30 | 73.3% | 16.7% | +0.0264 | -0.7408 |
| B2 Rolling Guard | 33 | 30 | 40.0% | 33.3% | +0.0048 | -0.1231 |
| BH-FDR Gate | 4 | 4 | 75.0% | 25.0% | +0.0315 | -1.1311 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.0784, Lock IC=+0.1243, Lock Sharpe=+0.5110
- `body_size_progression`: Train IC=+0.0935, Lock IC=+0.0625, Lock Sharpe=+0.4771
- `false_breakout_accumulation`: Train IC=+0.1489, Lock IC=+0.0315, Lock Sharpe=+0.2122
- `micro_gap_trend_continuation`: Train IC=+0.0820, Lock IC=+0.0729, Lock Sharpe=+0.1710
- `volatility_breakout_squeeze`: Train IC=+0.0859, Lock IC=+0.0375, Lock Sharpe=+0.1566

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `measured_move_proximity`: Train IC=+0.0000, Lock IC=+0.0769, Lock Sharpe=+0.6416
- `iv_diff_1d`: Train IC=+0.0334, Lock IC=+0.0868, Lock Sharpe=+0.6000
- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.0064, Lock Sharpe=+0.5415
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0456, Lock Sharpe=+0.5023
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0300, Lock Sharpe=+0.4246

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vwap_close_divergence_trend`: Train IC=+0.0805, Lock IC=+0.0323, Lock Sharpe=+0.0043

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 29.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3784_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 178 | 30 | 90.0% | 46.7% | +0.0676 | -0.1561 |
| B2 Rolling Guard | 21 | 21 | 33.3% | 19.0% | +0.0111 | -0.2836 |
| BH-FDR Gate | 13 | 13 | 69.2% | 0.0% | +0.0247 | -0.6301 |
| B3 Composite Floor | 6 | 6 | 100.0% | 16.7% | +0.0942 | -0.5831 |
| B4 Correlation Gate | 2 | 2 | 100.0% | 100.0% | +0.0748 | +0.4370 |

**Admitted Pool Summary**: 3 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0817, Mean Lock Sharpe = -0.4825

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_surge_direction`: Train IC=+0.1270, Lock IC=+0.1223, Lock Sharpe=+1.0579
- `yesterday_afternoon_momentum`: Train IC=+0.1273, Lock IC=+0.0912, Lock Sharpe=+0.9937
- `max_down_ret`: Train IC=+0.1243, Lock IC=+0.0913, Lock Sharpe=+0.7609
- `counter_trend_bar_weakness`: Train IC=+0.1169, Lock IC=+0.0744, Lock Sharpe=+0.4302
- `yesterday_lunch_gap`: Train IC=+0.1321, Lock IC=+0.0539, Lock Sharpe=+0.3756

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_10_60`: Train IC=+0.0509, Lock IC=+0.0521, Lock Sharpe=+0.9211
- `keltner_squeeze_width`: Train IC=+0.0808, Lock IC=+0.0365, Lock Sharpe=+0.8477
- `option_oi_growth`: Train IC=+0.0484, Lock IC=+0.0507, Lock Sharpe=+0.6472
- `bar_body_rng_1`: Train IC=+0.0666, Lock IC=+0.0293, Lock Sharpe=+0.6328

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volatility_expansion_trend_vector`: Train IC=+0.1817, Lock IC=+0.0926, Lock Sharpe=+0.0096

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_return`: Train IC=+0.1526, Lock IC=+0.0748, Lock Sharpe=+0.4370
- `bar_ret_0`: Train IC=+0.1526, Lock IC=+0.0748, Lock Sharpe=+0.4370

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 53.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3694_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 200 | 30 | 43.3% | 23.3% | +0.0066 | -0.4372 |
| B2 Rolling Guard | 25 | 25 | 28.0% | 4.0% | +0.0040 | -0.4163 |
| BH-FDR Gate | 10 | 10 | 90.0% | 40.0% | +0.0427 | -0.0150 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `counter_trend_bar_weakness`: Train IC=+0.0976, Lock IC=+0.0744, Lock Sharpe=+1.5962
- `volume_surge_direction`: Train IC=+0.1075, Lock IC=+0.1223, Lock Sharpe=+0.8521
- `vwap_close_divergence_trend`: Train IC=+0.1349, Lock IC=+0.0593, Lock Sharpe=+0.3891
- `or_fill_ratio`: Train IC=+0.1202, Lock IC=+0.0787, Lock Sharpe=+0.3058
- `intraday_close_position`: Train IC=+0.1202, Lock IC=+0.0787, Lock Sharpe=+0.3058

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_weighted_trend_strength_10d`: Train IC=+0.0000, Lock IC=+0.0194, Lock Sharpe=+0.3590

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `net_volume_flow`: Train IC=+0.1305, Lock IC=+0.0979, Lock Sharpe=+0.9281
- `opening_auction_imbalance`: Train IC=+0.1305, Lock IC=+0.0979, Lock Sharpe=+0.9281
- `intraday_slope`: Train IC=+0.1156, Lock IC=+0.0342, Lock Sharpe=+0.2250
- `early_trend`: Train IC=+0.1039, Lock IC=+0.0348, Lock Sharpe=+0.2250

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4625_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 197 | 30 | 73.3% | 23.3% | +0.0388 | -0.3067 |
| B2 Rolling Guard | 34 | 30 | 33.3% | 26.7% | +0.0067 | +0.0071 |
| BH-FDR Gate | 1 | 1 | 100.0% | 0.0% | +0.0926 | -0.2659 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_5_20`: Train IC=+0.0670, Lock IC=+0.0317, Lock Sharpe=+0.5783
- `gap_pct`: Train IC=+0.0662, Lock IC=+0.1187, Lock Sharpe=+0.4196
- `limit_down_proximity_early`: Train IC=+0.0645, Lock IC=+0.1323, Lock Sharpe=+0.2516
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0645, Lock IC=+0.1323, Lock Sharpe=+0.2516
- `high_beta_vol_ratio`: Train IC=+0.1059, Lock IC=+0.0237, Lock Sharpe=+0.2151

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0397, Lock Sharpe=+0.9086
- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.1050, Lock Sharpe=+0.5288
- `yesterday_close_position`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.4631
- `yesterday_day_close_pos`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.4631
- `opening_direction_stability`: Train IC=+0.0000, Lock IC=+0.0305, Lock Sharpe=+0.3428

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 26 | -0.0217 | 40.0% |
| 0.45 | 0.20 | 24 | -0.0217 | 40.0% |
| 0.45 | 0.30 | 20 | -0.0217 | 40.0% |
| 0.45 | 0.40 | 15 | -0.0218 | 40.0% |
| 0.45 | 0.50 | 8 | -0.0139 | 50.0% |
| 0.50 | 0.15 | 26 | -0.0217 | 40.0% |
| 0.50 | 0.25 | 21 | -0.0217 | 40.0% |
| 0.50 | 0.35 | 16 | -0.0218 | 40.0% |
| 0.50 | 0.45 | 12 | -0.0198 | 40.0% |
| 0.55 | 0.10 | 25 | -0.0217 | 40.0% |
| 0.55 | 0.20 | 24 | -0.0217 | 40.0% |
| 0.55 | 0.30 | 20 | -0.0217 | 40.0% |
| 0.55 | 0.40 | 15 | -0.0218 | 40.0% |
| 0.55 | 0.50 | 8 | -0.0139 | 50.0% |
| 0.60 | 0.15 | 21 | -0.0217 | 40.0% |
| 0.60 | 0.25 | 21 | -0.0217 | 40.0% |
| 0.60 | 0.35 | 16 | -0.0218 | 40.0% |
| 0.60 | 0.45 | 12 | -0.0198 | 40.0% |
| 0.65 | 0.10 | 13 | -0.0198 | 40.0% |
| 0.65 | 0.20 | 13 | -0.0198 | 40.0% |
| 0.65 | 0.30 | 13 | -0.0198 | 40.0% |
| 0.65 | 0.40 | 12 | -0.0198 | 40.0% |
| 0.65 | 0.50 | 8 | -0.0139 | 50.0% |
| 0.70 | 0.15 | 6 | -0.0069 | 66.7% |
| 0.70 | 0.25 | 6 | -0.0069 | 66.7% |
| 0.70 | 0.35 | 6 | -0.0069 | 66.7% |
| 0.70 | 0.45 | 6 | -0.0069 | 66.7% |
| 0.75 | 0.10 | 3 | +0.0005 | 100.0% |
| 0.75 | 0.20 | 3 | +0.0005 | 100.0% |
| 0.75 | 0.30 | 3 | +0.0005 | 100.0% |
| 0.75 | 0.40 | 3 | +0.0005 | 100.0% |
| 0.75 | 0.50 | 3 | +0.0005 | 100.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0005, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | -0.0207 | 33.3% |
| 0.45 | 0.20 | 6 | -0.0266 | 16.7% |
| 0.45 | 0.30 | 5 | -0.0224 | 20.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 7 | -0.0309 | 14.3% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 9 candidates, mean lock IC=-0.0207, 33.3% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 6 | +0.0280 | 66.7% |
| 0.45 | 0.20 | 2 | +0.0647 | 100.0% |
| 0.45 | 0.30 | 1 | +0.0209 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 4 | +0.0487 | 75.0% |
| 0.50 | 0.25 | 1 | +0.0209 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 3 | +0.0375 | 66.7% |
| 0.55 | 0.20 | 2 | +0.0647 | 100.0% |
| 0.55 | 0.30 | 1 | +0.0209 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | +0.0209 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0209 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 4 candidates, mean lock IC=+0.0487, 75.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 16 | -0.0268 | 30.0% |
| 0.45 | 0.20 | 14 | -0.0268 | 30.0% |
| 0.45 | 0.30 | 7 | -0.0363 | 14.3% |
| 0.45 | 0.40 | 1 | -0.0711 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 16 | -0.0268 | 30.0% |
| 0.50 | 0.25 | 8 | -0.0324 | 12.5% |
| 0.50 | 0.35 | 6 | -0.0387 | 16.7% |
| 0.50 | 0.45 | 1 | -0.0711 | 0.0% |
| 0.55 | 0.10 | 16 | -0.0268 | 30.0% |
| 0.55 | 0.20 | 14 | -0.0268 | 30.0% |
| 0.55 | 0.30 | 7 | -0.0363 | 14.3% |
| 0.55 | 0.40 | 1 | -0.0711 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 9 | -0.0249 | 22.2% |
| 0.60 | 0.25 | 8 | -0.0324 | 12.5% |
| 0.60 | 0.35 | 6 | -0.0387 | 16.7% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 9 candidates, mean lock IC=-0.0249, 22.2% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 7 | -0.0216 | 28.6% |
| 0.45 | 0.20 | 4 | -0.0402 | 25.0% |
| 0.45 | 0.30 | 4 | -0.0402 | 25.0% |
| 0.45 | 0.40 | 3 | -0.0591 | 0.0% |
| 0.45 | 0.50 | 2 | -0.0541 | 0.0% |
| 0.50 | 0.15 | 6 | -0.0367 | 16.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 7 candidates, mean lock IC=-0.0216, 28.6% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 4 | +0.0450 | 100.0% |
| 0.45 | 0.20 | 2 | +0.0198 | 100.0% |
| 0.45 | 0.30 | 1 | +0.0094 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 2 | +0.0198 | 100.0% |
| 0.50 | 0.25 | 1 | +0.0094 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 3 | +0.0458 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0458, 100.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 46 | +0.0301 | 80.0% |
| 0.45 | 0.20 | 41 | +0.0301 | 80.0% |
| 0.45 | 0.30 | 33 | +0.0301 | 80.0% |
| 0.45 | 0.40 | 24 | +0.0301 | 80.0% |
| 0.45 | 0.50 | 15 | +0.0270 | 70.0% |
| 0.50 | 0.15 | 42 | +0.0301 | 80.0% |
| 0.50 | 0.25 | 36 | +0.0301 | 80.0% |
| 0.50 | 0.35 | 30 | +0.0301 | 80.0% |
| 0.50 | 0.45 | 19 | +0.0270 | 70.0% |
| 0.55 | 0.10 | 44 | +0.0301 | 80.0% |
| 0.55 | 0.20 | 41 | +0.0301 | 80.0% |
| 0.55 | 0.30 | 33 | +0.0301 | 80.0% |
| 0.55 | 0.40 | 24 | +0.0301 | 80.0% |
| 0.55 | 0.50 | 15 | +0.0270 | 70.0% |
| 0.60 | 0.15 | 35 | +0.0301 | 80.0% |
| 0.60 | 0.25 | 34 | +0.0301 | 80.0% |
| 0.60 | 0.35 | 30 | +0.0301 | 80.0% |
| 0.60 | 0.45 | 19 | +0.0270 | 70.0% |
| 0.65 | 0.10 | 27 | +0.0301 | 80.0% |
| 0.65 | 0.20 | 27 | +0.0301 | 80.0% |
| 0.65 | 0.30 | 27 | +0.0301 | 80.0% |
| 0.65 | 0.40 | 24 | +0.0301 | 80.0% |
| 0.65 | 0.50 | 15 | +0.0270 | 70.0% |
| 0.70 | 0.15 | 14 | +0.0270 | 70.0% |
| 0.70 | 0.25 | 14 | +0.0270 | 70.0% |
| 0.70 | 0.35 | 14 | +0.0270 | 70.0% |
| 0.70 | 0.45 | 14 | +0.0270 | 70.0% |
| 0.75 | 0.10 | 4 | +0.0462 | 100.0% |
| 0.75 | 0.20 | 4 | +0.0462 | 100.0% |
| 0.75 | 0.30 | 4 | +0.0462 | 100.0% |
| 0.75 | 0.40 | 4 | +0.0462 | 100.0% |
| 0.75 | 0.50 | 4 | +0.0462 | 100.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 4 candidates, mean lock IC=+0.0462, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 7 | +0.0015 | 57.1% |
| 0.45 | 0.20 | 3 | +0.0106 | 33.3% |
| 0.45 | 0.30 | 1 | -0.0206 | 0.0% |
| 0.45 | 0.40 | 1 | -0.0206 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 5 | +0.0092 | 60.0% |
| 0.50 | 0.25 | 2 | +0.0179 | 50.0% |
| 0.50 | 0.35 | 1 | -0.0206 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 5 | +0.0092 | 60.0% |
| 0.55 | 0.20 | 3 | +0.0106 | 33.3% |
| 0.55 | 0.30 | 1 | -0.0206 | 0.0% |
| 0.55 | 0.40 | 1 | -0.0206 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | -0.0206 | 0.0% |
| 0.60 | 0.25 | 1 | -0.0206 | 0.0% |
| 0.60 | 0.35 | 1 | -0.0206 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 1 | -0.0206 | 0.0% |
| 0.65 | 0.20 | 1 | -0.0206 | 0.0% |
| 0.65 | 0.30 | 1 | -0.0206 | 0.0% |
| 0.65 | 0.40 | 1 | -0.0206 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 3 candidates, mean lock IC=+0.0106, 33.3% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 6 | +0.0122 | 66.7% |
| 0.45 | 0.20 | 3 | +0.0313 | 66.7% |
| 0.45 | 0.30 | 2 | +0.0490 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 4 | +0.0315 | 75.0% |
| 0.50 | 0.25 | 3 | +0.0313 | 66.7% |
| 0.50 | 0.35 | 2 | +0.0490 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 5 | +0.0332 | 80.0% |
| 0.55 | 0.20 | 3 | +0.0313 | 66.7% |
| 0.55 | 0.30 | 2 | +0.0490 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 3 | +0.0313 | 66.7% |
| 0.60 | 0.25 | 3 | +0.0313 | 66.7% |
| 0.60 | 0.35 | 2 | +0.0490 | 100.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 2 | +0.0490 | 100.0% |
| 0.65 | 0.20 | 2 | +0.0490 | 100.0% |
| 0.65 | 0.30 | 2 | +0.0490 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 5 candidates, mean lock IC=+0.0332, 80.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 30 | +0.0796 | 100.0% |
| 0.45 | 0.20 | 29 | +0.0796 | 100.0% |
| 0.45 | 0.30 | 24 | +0.0862 | 100.0% |
| 0.45 | 0.40 | 19 | +0.0862 | 100.0% |
| 0.45 | 0.50 | 13 | +0.0767 | 90.0% |
| 0.50 | 0.15 | 30 | +0.0796 | 100.0% |
| 0.50 | 0.25 | 27 | +0.0862 | 100.0% |
| 0.50 | 0.35 | 22 | +0.0862 | 100.0% |
| 0.50 | 0.45 | 15 | +0.0862 | 100.0% |
| 0.55 | 0.10 | 29 | +0.0796 | 100.0% |
| 0.55 | 0.20 | 29 | +0.0796 | 100.0% |
| 0.55 | 0.30 | 24 | +0.0862 | 100.0% |
| 0.55 | 0.40 | 19 | +0.0862 | 100.0% |
| 0.55 | 0.50 | 13 | +0.0767 | 90.0% |
| 0.60 | 0.15 | 27 | +0.0862 | 100.0% |
| 0.60 | 0.25 | 27 | +0.0862 | 100.0% |
| 0.60 | 0.35 | 22 | +0.0862 | 100.0% |
| 0.60 | 0.45 | 15 | +0.0862 | 100.0% |
| 0.65 | 0.10 | 18 | +0.0862 | 100.0% |
| 0.65 | 0.20 | 18 | +0.0862 | 100.0% |
| 0.65 | 0.30 | 18 | +0.0862 | 100.0% |
| 0.65 | 0.40 | 18 | +0.0862 | 100.0% |
| 0.65 | 0.50 | 13 | +0.0767 | 90.0% |
| 0.70 | 0.15 | 10 | +0.0882 | 100.0% |
| 0.70 | 0.25 | 10 | +0.0882 | 100.0% |
| 0.70 | 0.35 | 10 | +0.0882 | 100.0% |
| 0.70 | 0.45 | 10 | +0.0882 | 100.0% |
| 0.75 | 0.10 | 2 | +0.0737 | 100.0% |
| 0.75 | 0.20 | 2 | +0.0737 | 100.0% |
| 0.75 | 0.30 | 2 | +0.0737 | 100.0% |
| 0.75 | 0.40 | 2 | +0.0737 | 100.0% |
| 0.75 | 0.50 | 2 | +0.0737 | 100.0% |
| 0.80 | 0.15 | 1 | +0.0682 | 100.0% |
| 0.80 | 0.25 | 1 | +0.0682 | 100.0% |
| 0.80 | 0.35 | 1 | +0.0682 | 100.0% |
| 0.80 | 0.45 | 1 | +0.0682 | 100.0% |

**Optimal**: mono_thr=0.70, ir_thr=0.10 → 10 candidates, mean lock IC=+0.0882, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 16 | +0.0559 | 90.0% |
| 0.45 | 0.20 | 10 | +0.0427 | 90.0% |
| 0.45 | 0.30 | 5 | +0.0273 | 80.0% |
| 0.45 | 0.40 | 3 | +0.0225 | 66.7% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 12 | +0.0559 | 90.0% |
| 0.50 | 0.25 | 8 | +0.0431 | 87.5% |
| 0.50 | 0.35 | 4 | +0.0254 | 75.0% |
| 0.50 | 0.45 | 2 | +0.0178 | 50.0% |
| 0.55 | 0.10 | 10 | +0.0427 | 90.0% |
| 0.55 | 0.20 | 10 | +0.0427 | 90.0% |
| 0.55 | 0.30 | 5 | +0.0273 | 80.0% |
| 0.55 | 0.40 | 3 | +0.0225 | 66.7% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 7 | +0.0475 | 85.7% |
| 0.60 | 0.25 | 7 | +0.0475 | 85.7% |
| 0.60 | 0.35 | 4 | +0.0254 | 75.0% |
| 0.60 | 0.45 | 2 | +0.0178 | 50.0% |
| 0.65 | 0.10 | 3 | +0.0235 | 66.7% |
| 0.65 | 0.20 | 3 | +0.0235 | 66.7% |
| 0.65 | 0.30 | 3 | +0.0235 | 66.7% |
| 0.65 | 0.40 | 2 | +0.0178 | 50.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 16 candidates, mean lock IC=+0.0559, 90.0% positive

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
| `max_up_ret` | +0.1001 | +0.0000 | -0.0463 | -0.46x | 2015-02-06 |
| `first_bar_return` | +0.0871 | +0.0000 | +0.0007 | 0.01x | 2013-08-21 |
| `opening_drive_thrust_ratio` | +0.1116 | +0.0000 | -0.0172 | -0.15x | 2017-06-09 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volatility_expansion_trend_vector` | +0.1484 | +0.0000 | +0.0564 | 0.38x | 2016-11-01 |
| `early_order_flow_imbalance` | +0.1249 | +0.0000 | -0.0041 | -0.03x | 2016-11-01 |
| `max_up_ret` | +0.1829 | +0.0000 | +0.0308 | 0.17x | No decay |
| `first_bar_return` | +0.1382 | +0.0000 | +0.0404 | 0.29x | 2013-09-23 |
| `vwap_close_divergence_trend` | +0.1298 | +0.0000 | +0.0323 | 0.25x | 2016-11-01 |
| `num_up_bars` | +0.1234 | +0.0000 | +0.0459 | 0.37x | 2020-02-12 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `opening_drive_thrust_ratio` | +0.1447 | +0.0000 | +0.0792 | 0.55x | 2016-10-24 |
| `max_up_ret` | +0.1487 | +0.0000 | +0.0682 | 0.46x | 2017-01-20 |
| `bar_body_rng_0` | +0.1345 | +0.0000 | +0.0977 | 0.73x | 2017-02-27 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
2. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=-0.8624). Consider relaxing this gate.
3. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.5324). Consider relaxing this gate.
4. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 8.0%, mean lock Sharpe=-0.9403). Consider relaxing this gate.
5. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 19.0%, mean lock Sharpe=-0.0604). Consider relaxing this gate.
6. **500ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
7. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.7408). Consider relaxing this gate.
8. **500ETF `short` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.1231). Consider relaxing this gate.
9. **159915ETF `single` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 29.0%, mean lock Sharpe=-0.1561). Consider relaxing this gate.
10. **159915ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
11. **159915ETF `long` — BH-FDR Gate too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.0150). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
