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

### 300ETF — `single` (Full Model Lockbox IC: +0.0707, Sharpe: -0.1341)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0965 | +0.0662 | +0.0662 | -0.3946 | 84.09 | +8.1 | 1.01x | +0.0041 | -0.0580 |
| `bar_body_rng_0` | Other Technical | +1 | +0.0910 | +0.0666 | +0.0666 | -0.0761 | 86.37 | +13.4 | 1.67x | +0.0045 | +0.2605 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1027, Sharpe: +0.5088)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1682 | +0.0993 | +0.0993 | -0.2306 | 90.93 | +12.0 | 1.50x | +0.0054 | +0.1096 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1619 | +0.0920 | +0.0920 | +0.1044 | 84.37 | +15.8 | 1.98x | +0.0021 | +0.3864 |
| `volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1151 | +0.0894 | +0.0894 | +0.0972 | 87.22 | +15.8 | 1.98x | -0.0021 | +0.0583 |
| `close_vs_open_range` | Other Technical | +1 | +0.1100 | +0.0899 | +0.0899 | -0.2788 | 84.37 | +9.9 | 1.24x | -0.0008 | -0.1076 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1457 | +0.0699 | +0.0699 | +0.1945 | 80.67 | +17.2 | 2.15x | +0.0020 | +0.0868 |
| `max_down_ret` | Intraday Range Momentum | +1 | +0.1248 | +0.0828 | +0.0828 | -0.1758 | 85.80 | +11.0 | 1.38x | +0.0023 | -0.0669 |
| `first_30min_return` | Intraday Range Momentum | +1 | +0.1142 | +0.0851 | +0.0851 | +0.0010 | 82.95 | +13.7 | 1.71x | -0.0013 | +0.1749 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1266, Sharpe: +0.9070)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1455 | +0.1309 | +0.1309 | +0.6647 | 82.95 | +29.3 | 3.66x | +0.0252 | +0.6297 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1282 | +0.1014 | +0.1014 | +0.2773 | 84.09 | +19.6 | 2.46x | -0.0043 | +0.2423 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6944_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 181 | 30 | 80.0% | 10.0% | +0.0214 | -0.6678 |
| B2 Rolling Guard | 28 | 28 | 42.9% | 0.0% | -0.0013 | -0.5938 |
| BH-FDR Gate | 5 | 5 | 100.0% | 0.0% | +0.0410 | -0.6949 |
| B3 Composite Floor | 4 | 4 | 100.0% | 25.0% | +0.0498 | -0.1489 |
| B4 Correlation Gate | 1 | 1 | 100.0% | 0.0% | +0.0606 | -0.3885 |

**Admitted Pool Summary**: 2 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0664, Mean Lock Sharpe = -0.2353

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1285, Lock IC=+0.0650, Lock Sharpe=+0.4548
- `volume_surge_direction`: Train IC=+0.1031, Lock IC=+0.0498, Lock Sharpe=+0.2960
- `close_location_in_range_3d`: Train IC=+0.0900, Lock IC=+0.0457, Lock Sharpe=+0.2518

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `max_up_ret`: Train IC=+0.1676, Lock IC=+0.0460, Lock Sharpe=+0.0930

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 7.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8573_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 204 | 30 | 70.0% | 10.0% | +0.0103 | -0.9686 |
| B2 Rolling Guard | 29 | 29 | 34.5% | 3.4% | +0.0053 | -0.5127 |
| BH-FDR Gate | 3 | 3 | 100.0% | 0.0% | +0.0040 | -1.3727 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma50_dist`: Train IC=+0.1113, Lock IC=+0.0223, Lock Sharpe=+0.6620
- `first_bar_return`: Train IC=+0.1136, Lock IC=+0.0483, Lock Sharpe=+0.0754
- `bar_ret_0`: Train IC=+0.1136, Lock IC=+0.0483, Lock Sharpe=+0.0754

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.0991, Lock IC=+0.0131, Lock Sharpe=+0.3703

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 50.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6431_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 192 | 30 | 63.3% | 6.7% | +0.0157 | -0.6487 |
| B2 Rolling Guard | 41 | 30 | 33.3% | 6.7% | -0.0029 | -0.3350 |
| BH-FDR Gate | 2 | 2 | 100.0% | 0.0% | +0.0634 | -0.1276 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.0637, Lock IC=+0.0650, Lock Sharpe=+0.2637
- `yesterday_first_30min_return`: Train IC=+0.0685, Lock IC=+0.0646, Lock Sharpe=+0.2376

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0258, Lock Sharpe=+0.0981
- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.0153, Lock Sharpe=+0.0947

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 3.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9281_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 186 | 30 | 60.0% | 13.3% | +0.0116 | -0.7642 |
| B2 Rolling Guard | 25 | 25 | 32.0% | 0.0% | +0.0011 | -0.5407 |
| BH-FDR Gate | 2 | 2 | 100.0% | 0.0% | +0.0069 | -0.5724 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rsi21`: Train IC=+0.0780, Lock IC=+0.0434, Lock Sharpe=+0.5995
- `coppock_curve_day`: Train IC=+0.0917, Lock IC=+0.0403, Lock Sharpe=+0.4875
- `roc20`: Train IC=+0.0671, Lock IC=+0.0542, Lock Sharpe=+0.0775
- `yesterday_lunch_gap`: Train IC=+0.1396, Lock IC=+0.0321, Lock Sharpe=+0.0282

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 54.0% lock IC > 0, 5.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9324_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 194 | 30 | 36.7% | 13.3% | +0.0014 | -1.0078 |
| B2 Rolling Guard | 25 | 25 | 20.0% | 0.0% | -0.0097 | -0.7227 |
| BH-FDR Gate | 8 | 8 | 25.0% | 0.0% | -0.0038 | -1.5665 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `wavetrend_osc_day`: Train IC=+0.0976, Lock IC=+0.0469, Lock Sharpe=+0.2279
- `yesterday_wavetrend_osc`: Train IC=+0.0976, Lock IC=+0.0469, Lock Sharpe=+0.2279
- `yesterday_lunch_gap`: Train IC=+0.0833, Lock IC=+0.0321, Lock Sharpe=+0.1763
- `sma_distance_60d`: Train IC=+0.1247, Lock IC=+0.0324, Lock Sharpe=+0.0794

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6304_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 203 | 30 | 66.7% | 16.7% | +0.0076 | -0.5324 |
| B2 Rolling Guard | 32 | 30 | 33.3% | 6.7% | -0.0010 | -0.4103 |
| BH-FDR Gate | 2 | 2 | 0.0% | 0.0% | -0.0088 | -0.7909 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc60`: Train IC=+0.1073, Lock IC=+0.0034, Lock Sharpe=+0.4834
- `sma100_dist`: Train IC=+0.0810, Lock IC=+0.0437, Lock Sharpe=+0.3443
- `sma50_dist`: Train IC=+0.1088, Lock IC=+0.0400, Lock Sharpe=+0.2415
- `yesterday_lunch_gap`: Train IC=+0.0929, Lock IC=+0.0321, Lock Sharpe=+0.0812
- `sma_distance_60d`: Train IC=+0.0963, Lock IC=+0.0324, Lock Sharpe=+0.0553

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0282, Lock Sharpe=+0.1305
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0010, Lock Sharpe=+0.0543

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 81.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4630_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 169 | 30 | 96.7% | 16.7% | +0.0698 | -0.3404 |
| B2 Rolling Guard | 29 | 29 | 51.7% | 13.8% | +0.0174 | -0.2030 |
| BH-FDR Gate | 4 | 4 | 75.0% | 25.0% | +0.0010 | -0.6062 |
| B3 Composite Floor | 13 | 13 | 92.3% | 15.4% | +0.0626 | -0.3193 |
| B4 Correlation Gate | 6 | 6 | 100.0% | 33.3% | +0.0781 | -0.1638 |

**Admitted Pool Summary**: 7 features, False Positive Rate = 42.9% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0869, Mean Lock Sharpe = -0.0411

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_surge_direction`: Train IC=+0.1332, Lock IC=+0.0677, Lock Sharpe=+0.7072
- `yesterday_early_vwap_dev`: Train IC=+0.1581, Lock IC=+0.0555, Lock Sharpe=+0.3534
- `yesterday_early_momentum`: Train IC=+0.1455, Lock IC=+0.0434, Lock Sharpe=+0.0930
- `star50_limit_proximity_early`: Train IC=+0.1953, Lock IC=+0.1184, Lock Sharpe=+0.0205
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.2466, Lock IC=+0.1136, Lock Sharpe=+0.0070

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv`: Train IC=+0.0738, Lock IC=+0.0482, Lock Sharpe=+0.5765
- `iv_diff_1d`: Train IC=+0.0355, Lock IC=+0.0707, Lock Sharpe=+0.5676
- `iv_envelope_deviation`: Train IC=+0.0552, Lock IC=+0.0407, Lock Sharpe=+0.4264
- `vix`: Train IC=+0.0585, Lock IC=+0.0472, Lock Sharpe=+0.4049

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_10_60`: Train IC=+0.0962, Lock IC=+0.0274, Lock Sharpe=+0.3927

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `morning_volume_weighted_momentum`: Train IC=+0.1578, Lock IC=+0.0856, Lock Sharpe=+0.2563
- `trend_bar_close_consistency`: Train IC=+0.2230, Lock IC=+0.0642, Lock Sharpe=+0.0032

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bar_ret_0`: Train IC=+0.1931, Lock IC=+0.0699, Lock Sharpe=+0.1945
- `open_to_current_return`: Train IC=+0.1557, Lock IC=+0.0851, Lock Sharpe=+0.0010

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5170_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 201 | 30 | 86.7% | 16.7% | +0.0407 | -0.4375 |
| B2 Rolling Guard | 30 | 30 | 43.3% | 16.7% | +0.0118 | -0.1892 |
| BH-FDR Gate | 7 | 7 | 100.0% | 42.9% | +0.0728 | -0.1926 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma50_dist`: Train IC=+0.1256, Lock IC=+0.0480, Lock Sharpe=+0.2886
- `adx_trend_direction_14d`: Train IC=+0.1110, Lock IC=+0.0194, Lock Sharpe=+0.2106
- `rsi21`: Train IC=+0.1463, Lock IC=+0.0423, Lock Sharpe=+0.1717
- `sma_distance_60d`: Train IC=+0.1010, Lock IC=+0.0446, Lock Sharpe=+0.0332
- `shaved_bar_trend_conviction`: Train IC=+0.1205, Lock IC=+0.0629, Lock Sharpe=+0.0146

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv`: Train IC=+0.0483, Lock IC=+0.0482, Lock Sharpe=+0.6460
- `vix`: Train IC=+0.0323, Lock IC=+0.0472, Lock Sharpe=+0.2698
- `iv_diff_1d`: Train IC=+0.0348, Lock IC=+0.0707, Lock Sharpe=+0.2120
- `vix_rolling_percentile_60d`: Train IC=+0.0325, Lock IC=+0.0114, Lock Sharpe=+0.1692
- `iv_envelope_deviation`: Train IC=+0.0406, Lock IC=+0.0407, Lock Sharpe=+0.1659

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_surge_direction`: Train IC=+0.0046, Lock IC=+0.0677, Lock Sharpe=+0.2364
- `close_vs_open_range`: Train IC=+0.1077, Lock IC=+0.0899, Lock Sharpe=+0.1859
- `volume_percentile_20d`: Train IC=+0.1100, Lock IC=+0.0405, Lock Sharpe=+0.0586

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 54.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3317_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 195 | 30 | 83.3% | 33.3% | +0.0398 | -0.2476 |
| B2 Rolling Guard | 41 | 30 | 43.3% | 13.3% | +0.0040 | -0.2164 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_pk20`: Train IC=+0.0713, Lock IC=+0.0317, Lock Sharpe=+0.3981
- `atr14_norm`: Train IC=+0.0791, Lock IC=+0.0288, Lock Sharpe=+0.3495
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1596, Lock IC=+0.1136, Lock Sharpe=+0.2505
- `net_volume_flow`: Train IC=+0.1389, Lock IC=+0.0892, Lock Sharpe=+0.2119
- `opening_auction_imbalance`: Train IC=+0.1389, Lock IC=+0.0892, Lock Sharpe=+0.2119

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix`: Train IC=+0.0681, Lock IC=+0.0472, Lock Sharpe=+0.4499
- `close_vs_open_range`: Train IC=+0.0830, Lock IC=+0.0899, Lock Sharpe=+0.4216
- `iv_diff_1d`: Train IC=+0.0615, Lock IC=+0.0707, Lock Sharpe=+0.3321
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0222, Lock Sharpe=+0.2464

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 69.0% lock IC > 0, 27.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2544_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 180 | 30 | 93.3% | 56.7% | +0.0666 | +0.0709 |
| B2 Rolling Guard | 32 | 30 | 56.7% | 30.0% | +0.0344 | +0.0020 |
| BH-FDR Gate | 4 | 4 | 75.0% | 50.0% | +0.0545 | -0.0824 |
| B3 Composite Floor | 10 | 10 | 100.0% | 90.0% | +0.0962 | +0.2863 |

**Admitted Pool Summary**: 2 features, False Positive Rate = 0.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1161, Mean Lock Sharpe = +0.4710

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_surge_direction`: Train IC=+0.1127, Lock IC=+0.1108, Lock Sharpe=+1.1372
- `morning_volume_weighted_momentum`: Train IC=+0.1002, Lock IC=+0.1119, Lock Sharpe=+0.6047
- `trend_day_regime_conviction`: Train IC=+0.1107, Lock IC=+0.1116, Lock Sharpe=+0.5538
- `bar_body_rng_0`: Train IC=+0.1594, Lock IC=+0.0968, Lock Sharpe=+0.5503
- `max_down_ret`: Train IC=+0.1145, Lock IC=+0.1046, Lock Sharpe=+0.5403

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.1380, Lock IC=+0.0640, Lock Sharpe=+0.8000
- `first_bar_return`: Train IC=+0.1458, Lock IC=+0.0872, Lock Sharpe=+0.6789
- `bar_ret_0`: Train IC=+0.1458, Lock IC=+0.0872, Lock Sharpe=+0.6789
- `early_body_momentum`: Train IC=+0.0958, Lock IC=+0.0960, Lock Sharpe=+0.5022
- `opening_momentum_score`: Train IC=+0.0958, Lock IC=+0.0960, Lock Sharpe=+0.5022

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `close_vs_open_range`: Train IC=+0.1106, Lock IC=+0.1197, Lock Sharpe=+0.5916
- `shaved_bar_trend_conviction`: Train IC=+0.0990, Lock IC=+0.1148, Lock Sharpe=+0.4006

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `opening_drive_thrust_ratio`: Train IC=+0.2418, Lock IC=+0.1176, Lock Sharpe=+0.7695
- `volatility_expansion_trend_vector`: Train IC=+0.1531, Lock IC=+0.1157, Lock Sharpe=+0.6581
- `star50_limit_proximity_early`: Train IC=+0.1849, Lock IC=+0.1286, Lock Sharpe=+0.5989
- `limit_down_proximity_early`: Train IC=+0.1321, Lock IC=+0.1016, Lock Sharpe=+0.2202
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1321, Lock IC=+0.1016, Lock Sharpe=+0.2202

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 37.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3257_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 206 | 30 | 76.7% | 40.0% | +0.0357 | -0.2099 |
| B2 Rolling Guard | 31 | 30 | 50.0% | 30.0% | +0.0257 | -0.0549 |
| BH-FDR Gate | 1 | 1 | 0.0% | 0.0% | -0.0104 | -0.3562 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `shaved_bar_trend_conviction`: Train IC=+0.1139, Lock IC=+0.1148, Lock Sharpe=+1.1278
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1124, Lock IC=+0.1309, Lock Sharpe=+0.8075
- `opening_drive_thrust_ratio`: Train IC=+0.1332, Lock IC=+0.1176, Lock Sharpe=+0.5544
- `vol_ratio_10_60`: Train IC=+0.1065, Lock IC=+0.0244, Lock Sharpe=+0.5264
- `counter_trend_bar_weakness`: Train IC=+0.1211, Lock IC=+0.0900, Lock Sharpe=+0.4986

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volatility_expansion_trend_vector`: Train IC=+0.0450, Lock IC=+0.1157, Lock Sharpe=+0.6234
- `morning_volume_weighted_momentum`: Train IC=+0.0268, Lock IC=+0.1119, Lock Sharpe=+0.5110
- `trend_bar_close_consistency`: Train IC=+0.0463, Lock IC=+0.1024, Lock Sharpe=+0.5059
- `iv`: Train IC=+0.0542, Lock IC=+0.0127, Lock Sharpe=+0.4483
- `vix_rolling_percentile_60d`: Train IC=+0.0251, Lock IC=+0.0039, Lock Sharpe=+0.3295

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4842_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 193 | 30 | 80.0% | 16.7% | +0.0403 | -0.1615 |
| B2 Rolling Guard | 39 | 30 | 46.7% | 26.7% | +0.0070 | -0.2197 |
| BH-FDR Gate | 4 | 4 | 100.0% | 50.0% | +0.0733 | -0.0848 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_gk20`: Train IC=+0.0558, Lock IC=+0.0268, Lock Sharpe=+0.5846
- `cci14`: Train IC=+0.0740, Lock IC=+0.0494, Lock Sharpe=+0.3148
- `vol_gk10`: Train IC=+0.0699, Lock IC=+0.0285, Lock Sharpe=+0.2136
- `trend_day_regime_conviction`: Train IC=+0.1013, Lock IC=+0.1116, Lock Sharpe=+0.1697
- `yesterday_pm_return`: Train IC=+0.0652, Lock IC=+0.0807, Lock Sharpe=+0.0355

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
| 0.45 | 0.10 | 27 | +0.0505 | 100.0% |
| 0.45 | 0.20 | 20 | +0.0429 | 90.0% |
| 0.45 | 0.30 | 14 | +0.0483 | 100.0% |
| 0.45 | 0.40 | 8 | +0.0533 | 100.0% |
| 0.45 | 0.50 | 1 | +0.0662 | 100.0% |
| 0.50 | 0.15 | 22 | +0.0505 | 100.0% |
| 0.50 | 0.25 | 18 | +0.0429 | 90.0% |
| 0.50 | 0.35 | 9 | +0.0525 | 100.0% |
| 0.50 | 0.45 | 5 | +0.0547 | 100.0% |
| 0.55 | 0.10 | 22 | +0.0505 | 100.0% |
| 0.55 | 0.20 | 20 | +0.0429 | 90.0% |
| 0.55 | 0.30 | 14 | +0.0483 | 100.0% |
| 0.55 | 0.40 | 8 | +0.0533 | 100.0% |
| 0.55 | 0.50 | 1 | +0.0662 | 100.0% |
| 0.60 | 0.15 | 14 | +0.0429 | 90.0% |
| 0.60 | 0.25 | 13 | +0.0429 | 90.0% |
| 0.60 | 0.35 | 9 | +0.0525 | 100.0% |
| 0.60 | 0.45 | 5 | +0.0547 | 100.0% |
| 0.65 | 0.10 | 9 | +0.0525 | 100.0% |
| 0.65 | 0.20 | 9 | +0.0525 | 100.0% |
| 0.65 | 0.30 | 9 | +0.0525 | 100.0% |
| 0.65 | 0.40 | 8 | +0.0533 | 100.0% |
| 0.65 | 0.50 | 1 | +0.0662 | 100.0% |
| 0.70 | 0.15 | 1 | +0.0662 | 100.0% |
| 0.70 | 0.25 | 1 | +0.0662 | 100.0% |
| 0.70 | 0.35 | 1 | +0.0662 | 100.0% |
| 0.70 | 0.45 | 1 | +0.0662 | 100.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.45 → 5 candidates, mean lock IC=+0.0547, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 5 | +0.0082 | 80.0% |
| 0.45 | 0.20 | 3 | +0.0040 | 100.0% |
| 0.45 | 0.30 | 2 | +0.0057 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 4 | +0.0195 | 100.0% |
| 0.50 | 0.25 | 2 | +0.0057 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | -0.0063 | 75.0% |
| 0.55 | 0.20 | 3 | +0.0040 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 4 candidates, mean lock IC=+0.0195, 100.0% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 4 | +0.0150 | 50.0% |
| 0.45 | 0.20 | 2 | +0.0634 | 100.0% |
| 0.45 | 0.30 | 1 | +0.0662 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 3 | +0.0405 | 66.7% |
| 0.50 | 0.25 | 1 | +0.0662 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 2 | +0.0634 | 100.0% |
| 0.55 | 0.20 | 2 | +0.0634 | 100.0% |
| 0.55 | 0.30 | 1 | +0.0662 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | +0.0634 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0662 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 3 candidates, mean lock IC=+0.0405, 66.7% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 15 | -0.0012 | 60.0% |
| 0.45 | 0.20 | 9 | +0.0102 | 66.7% |
| 0.45 | 0.30 | 2 | +0.0069 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 13 | +0.0005 | 50.0% |
| 0.50 | 0.25 | 7 | -0.0047 | 57.1% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 13 | +0.0005 | 50.0% |
| 0.55 | 0.20 | 9 | +0.0102 | 66.7% |
| 0.55 | 0.30 | 2 | +0.0069 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 6 | +0.0251 | 100.0% |
| 0.60 | 0.25 | 4 | +0.0064 | 100.0% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 6 candidates, mean lock IC=+0.0251, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | -0.0109 | 20.0% |
| 0.45 | 0.20 | 8 | -0.0038 | 25.0% |
| 0.45 | 0.30 | 7 | -0.0059 | 14.3% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | -0.0038 | 25.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 8 candidates, mean lock IC=-0.0038, 25.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 3 | -0.0059 | 0.0% |
| 0.45 | 0.20 | 1 | -0.0134 | 0.0% |
| 0.45 | 0.30 | 1 | -0.0134 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 2 | -0.0088 | 0.0% |
| 0.50 | 0.25 | 1 | -0.0134 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 2 | -0.0088 | 0.0% |
| 0.55 | 0.20 | 1 | -0.0134 | 0.0% |
| 0.55 | 0.30 | 1 | -0.0134 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 3 candidates, mean lock IC=-0.0059, 0.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 37 | +0.0841 | 100.0% |
| 0.45 | 0.20 | 35 | +0.0841 | 100.0% |
| 0.45 | 0.30 | 31 | +0.0841 | 100.0% |
| 0.45 | 0.40 | 22 | +0.0810 | 100.0% |
| 0.45 | 0.50 | 10 | +0.0764 | 100.0% |
| 0.50 | 0.15 | 35 | +0.0841 | 100.0% |
| 0.50 | 0.25 | 33 | +0.0841 | 100.0% |
| 0.50 | 0.35 | 28 | +0.0841 | 100.0% |
| 0.50 | 0.45 | 17 | +0.0826 | 100.0% |
| 0.55 | 0.10 | 35 | +0.0841 | 100.0% |
| 0.55 | 0.20 | 35 | +0.0841 | 100.0% |
| 0.55 | 0.30 | 31 | +0.0841 | 100.0% |
| 0.55 | 0.40 | 22 | +0.0810 | 100.0% |
| 0.55 | 0.50 | 10 | +0.0764 | 100.0% |
| 0.60 | 0.15 | 31 | +0.0841 | 100.0% |
| 0.60 | 0.25 | 31 | +0.0841 | 100.0% |
| 0.60 | 0.35 | 28 | +0.0841 | 100.0% |
| 0.60 | 0.45 | 17 | +0.0826 | 100.0% |
| 0.65 | 0.10 | 22 | +0.0810 | 100.0% |
| 0.65 | 0.20 | 22 | +0.0810 | 100.0% |
| 0.65 | 0.30 | 22 | +0.0810 | 100.0% |
| 0.65 | 0.40 | 22 | +0.0810 | 100.0% |
| 0.65 | 0.50 | 10 | +0.0764 | 100.0% |
| 0.70 | 0.15 | 11 | +0.0844 | 100.0% |
| 0.70 | 0.25 | 11 | +0.0844 | 100.0% |
| 0.70 | 0.35 | 11 | +0.0844 | 100.0% |
| 0.70 | 0.45 | 11 | +0.0844 | 100.0% |
| 0.75 | 0.10 | 3 | +0.0925 | 100.0% |
| 0.75 | 0.20 | 3 | +0.0925 | 100.0% |
| 0.75 | 0.30 | 3 | +0.0925 | 100.0% |
| 0.75 | 0.40 | 3 | +0.0925 | 100.0% |
| 0.75 | 0.50 | 3 | +0.0925 | 100.0% |
| 0.80 | 0.15 | 1 | +0.0993 | 100.0% |
| 0.80 | 0.25 | 1 | +0.0993 | 100.0% |
| 0.80 | 0.35 | 1 | +0.0993 | 100.0% |
| 0.80 | 0.45 | 1 | +0.0993 | 100.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0925, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 8 | +0.0616 | 87.5% |
| 0.45 | 0.20 | 7 | +0.0728 | 100.0% |
| 0.45 | 0.30 | 1 | +0.0405 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 7 | +0.0728 | 100.0% |
| 0.50 | 0.25 | 7 | +0.0728 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | +0.0728 | 100.0% |
| 0.55 | 0.20 | 7 | +0.0728 | 100.0% |
| 0.55 | 0.30 | 1 | +0.0405 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 6 | +0.0712 | 100.0% |
| 0.60 | 0.25 | 6 | +0.0712 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 7 candidates, mean lock IC=+0.0728, 100.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 3 | +0.0174 | 33.3% |
| 0.45 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 1 | -0.0376 | 0.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.20 | 0 | +0.0000 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0174, 33.3% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 27 | +0.0912 | 100.0% |
| 0.45 | 0.20 | 24 | +0.0977 | 100.0% |
| 0.45 | 0.30 | 17 | +0.0990 | 100.0% |
| 0.45 | 0.40 | 9 | +0.0908 | 88.9% |
| 0.45 | 0.50 | 3 | +0.1166 | 100.0% |
| 0.50 | 0.15 | 27 | +0.0912 | 100.0% |
| 0.50 | 0.25 | 22 | +0.0977 | 100.0% |
| 0.50 | 0.35 | 13 | +0.0990 | 100.0% |
| 0.50 | 0.45 | 6 | +0.1028 | 100.0% |
| 0.55 | 0.10 | 27 | +0.0912 | 100.0% |
| 0.55 | 0.20 | 24 | +0.0977 | 100.0% |
| 0.55 | 0.30 | 17 | +0.0990 | 100.0% |
| 0.55 | 0.40 | 9 | +0.0908 | 88.9% |
| 0.55 | 0.50 | 3 | +0.1166 | 100.0% |
| 0.60 | 0.15 | 22 | +0.0912 | 100.0% |
| 0.60 | 0.25 | 19 | +0.0977 | 100.0% |
| 0.60 | 0.35 | 13 | +0.0990 | 100.0% |
| 0.60 | 0.45 | 6 | +0.1028 | 100.0% |
| 0.65 | 0.10 | 9 | +0.1089 | 100.0% |
| 0.65 | 0.20 | 9 | +0.1089 | 100.0% |
| 0.65 | 0.30 | 9 | +0.1089 | 100.0% |
| 0.65 | 0.40 | 8 | +0.1081 | 100.0% |
| 0.65 | 0.50 | 3 | +0.1166 | 100.0% |
| 0.70 | 0.15 | 3 | +0.1166 | 100.0% |
| 0.70 | 0.25 | 3 | +0.1166 | 100.0% |
| 0.70 | 0.35 | 3 | +0.1166 | 100.0% |
| 0.70 | 0.45 | 3 | +0.1166 | 100.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 3 candidates, mean lock IC=+0.1166, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 5 | +0.0490 | 80.0% |
| 0.45 | 0.20 | 1 | -0.0104 | 0.0% |
| 0.45 | 0.30 | 1 | -0.0104 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 3 | +0.0562 | 66.7% |
| 0.50 | 0.25 | 1 | -0.0104 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 2 | +0.0292 | 50.0% |
| 0.55 | 0.20 | 1 | -0.0104 | 0.0% |
| 0.55 | 0.30 | 1 | -0.0104 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | -0.0104 | 0.0% |
| 0.60 | 0.25 | 1 | -0.0104 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 3 candidates, mean lock IC=+0.0562, 66.7% positive

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
| `rbreaker_sell_setup_proximity_early` | +0.0962 | +0.0000 | +0.0662 | 0.69x | 2016-08-24 |
| `bar_body_rng_0` | +0.0907 | +0.0000 | +0.0666 | 0.73x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `opening_drive_thrust_ratio` | +0.1895 | +0.0000 | +0.0993 | 0.52x | No decay |
| `max_up_ret` | +0.1899 | +0.0000 | +0.0920 | 0.48x | No decay |
| `volatility_expansion_trend_vector` | +0.1525 | +0.0000 | +0.0894 | 0.59x | 2016-11-01 |
| `close_vs_open_range` | +0.1423 | +0.0000 | +0.0899 | 0.63x | 2016-11-01 |
| `first_bar_return` | +0.1446 | +0.0000 | +0.0699 | 0.48x | 2013-09-23 |
| `max_down_ret` | +0.1449 | +0.0000 | +0.0828 | 0.57x | 2016-09-26 |
| `first_30min_return` | +0.1490 | +0.0000 | +0.0851 | 0.57x | 2016-11-01 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `rbreaker_sell_setup_proximity_early` | +0.1526 | +0.0000 | +0.1309 | 0.86x | 2016-12-21 |
| `max_up_ret` | +0.1512 | +0.0000 | +0.1014 | 0.67x | 2017-01-20 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
2. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 8.0%, mean lock Sharpe=-0.5324). Consider relaxing this gate.
3. **500ETF `single` — B4 Correlation Gate too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.1638). Consider relaxing this gate.
4. **500ETF `long` — BH-FDR Gate too strict**: 42.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.1926). Consider relaxing this gate.
5. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.2476). Consider relaxing this gate.
6. **159915ETF `single` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 27.0%, mean lock Sharpe=+0.0709). Consider relaxing this gate.
7. **159915ETF `single` — B3 Composite Floor too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 27.0%, mean lock Sharpe=+0.2863). Consider relaxing this gate.
8. **159915ETF `short` — B2 Rolling Guard too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2197). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
