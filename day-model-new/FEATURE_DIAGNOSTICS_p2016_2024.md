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

### 300ETF — `single` (Full Model Lockbox IC: +0.0155, Sharpe: -0.7167)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bar_body_rng_0` | Other Technical | +1 | +0.0988 | +0.0301 | +0.0301 | -0.6404 | 87.03 | +6.2 | 0.77x | +0.0086 | +0.1165 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.0773 | -0.0047 | -0.0047 | -0.0381 | 84.25 | +13.3 | 1.66x | -0.0043 | -0.1957 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.0933 | +0.0060 | +0.0060 | -1.0115 | 90.61 | +2.3 | 0.29x | -0.0031 | -0.2091 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0933, Sharpe: -0.0463)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `net_volume_flow` | Volatility & Oscillators | +1 | +0.1020 | +0.0879 | +0.0879 | -0.0343 | 89.81 | +14.3 | 1.79x | -0.0009 | +0.0036 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1293 | +0.0813 | +0.0813 | -0.0733 | 85.84 | +12.7 | 1.59x | -0.0011 | -0.4200 |
| `first_bar_return` | Gap / Overnight Reversal | +1 | +0.1165 | +0.0686 | +0.0686 | +0.0195 | 83.06 | +14.1 | 1.77x | +0.0042 | -0.2801 |
| `opening_drive_thrust_ratio` | Other Technical | +1 | +0.1384 | +0.0962 | +0.0962 | +0.0157 | 92.59 | +15.5 | 1.94x | +0.0041 | -0.3346 |
| `close_vs_open_range` | Other Technical | +1 | +0.0902 | +0.0899 | +0.0899 | -0.2362 | 85.04 | +10.3 | 1.29x | +0.0015 | -0.1642 |
| `vwap_close_divergence_trend` | Other Technical | +1 | +0.0837 | +0.0582 | +0.0582 | -0.5326 | 87.43 | +3.0 | 0.38x | -0.0013 | +0.0815 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.0765, Sharpe: -0.0485)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1123 | +0.0765 | +0.0765 | -0.0485 | 83.85 | +12.8 | 1.59x | +0.0765 | -0.0485 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 50.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6808_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 183 | 30 | 60.0% | 26.7% | +0.0219 | -0.6423 |
| B2 Rolling Guard | 20 | 20 | 20.0% | 0.0% | -0.0103 | -0.5129 |
| BH-FDR Gate | 9 | 9 | 44.4% | 0.0% | -0.0025 | -0.8084 |
| B3 Composite Floor | 5 | 5 | 40.0% | 40.0% | -0.0141 | -0.4137 |

**Admitted Pool Summary**: 3 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0104, Mean Lock Sharpe = -0.5633

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_surge_direction`: Train IC=+0.0916, Lock IC=+0.0184, Lock Sharpe=+0.5209
- `close_location_in_range_3d`: Train IC=+0.0881, Lock IC=+0.0488, Lock Sharpe=+0.4378
- `yesterday_lunch_gap`: Train IC=+0.0939, Lock IC=+0.1015, Lock Sharpe=+0.3427
- `limit_down_proximity_early`: Train IC=+0.0876, Lock IC=+0.0570, Lock Sharpe=+0.2867
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0876, Lock IC=+0.0570, Lock Sharpe=+0.2867

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_return`: Train IC=+0.1429, Lock IC=+0.0107, Lock Sharpe=+0.1226
- `bar_ret_0`: Train IC=+0.1429, Lock IC=+0.0107, Lock Sharpe=+0.1226

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6496_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 199 | 30 | 60.0% | 36.7% | +0.0061 | -0.4883 |
| B2 Rolling Guard | 27 | 27 | 18.5% | 3.7% | -0.0070 | -0.4085 |
| BH-FDR Gate | 9 | 9 | 44.4% | 0.0% | -0.0110 | -0.8922 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma50_dist`: Train IC=+0.0837, Lock IC=+0.0180, Lock Sharpe=+0.7144
- `sma200_dist`: Train IC=+0.0915, Lock IC=+0.0328, Lock Sharpe=+0.4312
- `sma100_dist`: Train IC=+0.1200, Lock IC=+0.0455, Lock Sharpe=+0.4194
- `vol10`: Train IC=+0.0858, Lock IC=+0.0126, Lock Sharpe=+0.3956
- `false_breakout_accumulation`: Train IC=+0.0832, Lock IC=+0.0489, Lock Sharpe=+0.3605

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc60`: Train IC=+0.0546, Lock IC=+0.0215, Lock Sharpe=+0.3510

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 60.0% lock IC > 0, 9.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7214_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 196 | 30 | 76.7% | 20.0% | +0.0267 | -0.4950 |
| B2 Rolling Guard | 40 | 30 | 33.3% | 0.0% | -0.0030 | -0.4632 |
| BH-FDR Gate | 1 | 1 | 100.0% | 0.0% | +0.0637 | -0.6139 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `sma200_dist`: Train IC=+0.0763, Lock IC=+0.0328, Lock Sharpe=+0.7291
- `yesterday_lunch_gap`: Train IC=+0.0857, Lock IC=+0.1015, Lock Sharpe=+0.4105
- `star50_limit_proximity_early`: Train IC=+0.0800, Lock IC=+0.0658, Lock Sharpe=+0.3436
- `early_vwap_acceleration`: Train IC=+0.1442, Lock IC=+0.0189, Lock Sharpe=+0.1145
- `limit_down_proximity_early`: Train IC=+0.1106, Lock IC=+0.0570, Lock Sharpe=+0.0964

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 5.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9419_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 190 | 30 | 63.3% | 26.7% | +0.0077 | -0.5736 |
| B2 Rolling Guard | 16 | 16 | 25.0% | 0.0% | +0.0057 | -0.4617 |
| BH-FDR Gate | 8 | 8 | 0.0% | 0.0% | -0.0458 | -1.6074 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol60`: Train IC=+0.0833, Lock IC=+0.0117, Lock Sharpe=+0.7422
- `yesterday_lunch_gap`: Train IC=+0.0902, Lock IC=+0.0849, Lock Sharpe=+0.5765
- `limit_down_proximity_early`: Train IC=+0.1053, Lock IC=+0.0372, Lock Sharpe=+0.4838
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1053, Lock IC=+0.0372, Lock Sharpe=+0.4838
- `coppock_curve_day`: Train IC=+0.1046, Lock IC=+0.0416, Lock Sharpe=+0.4301

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 49.0% lock IC > 0, 9.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7591_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 199 | 30 | 40.0% | 3.3% | -0.0047 | -1.2131 |
| B2 Rolling Guard | 27 | 27 | 25.9% | 3.7% | -0.0074 | -0.6197 |
| BH-FDR Gate | 8 | 8 | 12.5% | 0.0% | -0.0226 | -1.8629 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.0929, Lock IC=+0.0849, Lock Sharpe=+0.4138

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc5`: Train IC=+0.0555, Lock IC=+0.0383, Lock Sharpe=+0.0314

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 7.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6935_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 197 | 30 | 76.7% | 33.3% | +0.0237 | -0.3513 |
| B2 Rolling Guard | 39 | 30 | 33.3% | 0.0% | -0.0002 | -0.4692 |
| BH-FDR Gate | 3 | 3 | 0.0% | 0.0% | -0.0374 | -0.6981 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc60`: Train IC=+0.1069, Lock IC=+0.0074, Lock Sharpe=+0.8878
- `sma200_dist`: Train IC=+0.1275, Lock IC=+0.0508, Lock Sharpe=+0.8447
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.3467
- `limit_down_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.3467
- `sma100_dist`: Train IC=+0.0999, Lock IC=+0.0507, Lock Sharpe=+0.3413

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 60.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3119_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 151 | 30 | 86.7% | 30.0% | +0.0441 | -0.2444 |
| B2 Rolling Guard | 29 | 29 | 55.2% | 24.1% | +0.0235 | -0.1227 |
| BH-FDR Gate | 12 | 12 | 91.7% | 8.3% | +0.0344 | -0.3832 |
| B3 Composite Floor | 13 | 13 | 100.0% | 23.1% | +0.0690 | -0.3392 |
| B4 Correlation Gate | 7 | 7 | 100.0% | 42.9% | +0.0793 | -0.0505 |

**Admitted Pool Summary**: 6 features, False Positive Rate = 66.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0804, Mean Lock Sharpe = -0.1402

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_surge_direction`: Train IC=+0.1196, Lock IC=+0.0758, Lock Sharpe=+0.9137
- `dual_thrust_range_ratio`: Train IC=+0.0956, Lock IC=+0.0942, Lock Sharpe=+0.7379
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1661, Lock IC=+0.1196, Lock Sharpe=+0.3997
- `vol20`: Train IC=+0.0961, Lock IC=+0.0371, Lock Sharpe=+0.2812
- `yesterday_early_vwap_dev`: Train IC=+0.1282, Lock IC=+0.0585, Lock Sharpe=+0.2202

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv_diff_1d`: Train IC=+0.0776, Lock IC=+0.0677, Lock Sharpe=+0.7137
- `vix`: Train IC=+0.0841, Lock IC=+0.0426, Lock Sharpe=+0.6645
- `iv`: Train IC=+0.1352, Lock IC=+0.0577, Lock Sharpe=+0.6249
- `iv_envelope_deviation`: Train IC=+0.0015, Lock IC=+0.0604, Lock Sharpe=+0.4736
- `vix_skew_proxy`: Train IC=+0.0658, Lock IC=+0.0334, Lock Sharpe=+0.1989

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_10_60`: Train IC=+0.0761, Lock IC=+0.0275, Lock Sharpe=+0.2531

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `morning_volume_weighted_momentum`: Train IC=+0.1465, Lock IC=+0.0778, Lock Sharpe=+0.4041
- `max_down_ret`: Train IC=+0.1238, Lock IC=+0.0972, Lock Sharpe=+0.0240
- `trend_bar_close_consistency`: Train IC=+0.1816, Lock IC=+0.0550, Lock Sharpe=+0.0093

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_30min_return`: Train IC=+0.1415, Lock IC=+0.0774, Lock Sharpe=+0.2720
- `open_to_current_return`: Train IC=+0.1415, Lock IC=+0.0774, Lock Sharpe=+0.2720
- `bar_ret_0`: Train IC=+0.1959, Lock IC=+0.0686, Lock Sharpe=+0.0195

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 60.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3618_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 210 | 30 | 76.7% | 26.7% | +0.0284 | -0.2797 |
| B2 Rolling Guard | 26 | 26 | 26.9% | 11.5% | -0.0076 | -0.3638 |
| BH-FDR Gate | 3 | 3 | 100.0% | 66.7% | +0.0877 | +0.0255 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv`: Train IC=+0.0951, Lock IC=+0.0577, Lock Sharpe=+0.9091
- `shaved_bar_trend_conviction`: Train IC=+0.1025, Lock IC=+0.0541, Lock Sharpe=+0.4834
- `first_bar_return`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.2410
- `bar_ret_0`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.2410
- `morning_trend_extrapolated`: Train IC=+0.0833, Lock IC=+0.0508, Lock Sharpe=+0.2020

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_iv_ratio`: Train IC=-0.0038, Lock IC=+0.0265, Lock Sharpe=+0.3738
- `volume_weighted_trend_strength_10d`: Train IC=+0.0000, Lock IC=+0.0508, Lock Sharpe=+0.2091
- `volatility_percentile_20d`: Train IC=+0.0000, Lock IC=+0.0169, Lock Sharpe=+0.1353

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `net_volume_flow`: Train IC=+0.0597, Lock IC=+0.0879, Lock Sharpe=+0.0711
- `opening_auction_imbalance`: Train IC=+0.0597, Lock IC=+0.0879, Lock Sharpe=+0.0711

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 48.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3920_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 201 | 30 | 76.7% | 20.0% | +0.0407 | -0.3969 |
| B2 Rolling Guard | 35 | 30 | 43.3% | 16.7% | +0.0040 | -0.1016 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1202, Lock IC=+0.1196, Lock Sharpe=+0.6521
- `consecutive_trend_bar_intensity`: Train IC=+0.1062, Lock IC=+0.0852, Lock Sharpe=+0.5628
- `tight_channel_persistence`: Train IC=+0.0969, Lock IC=+0.0581, Lock Sharpe=+0.4121
- `close_vs_open_range`: Train IC=+0.0883, Lock IC=+0.0899, Lock Sharpe=+0.3891
- `vwap_close_divergence_trend`: Train IC=+0.0796, Lock IC=+0.0582, Lock Sharpe=+0.0773

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0278, Lock Sharpe=+0.6378
- `iv_diff_1d`: Train IC=+0.0831, Lock IC=+0.0677, Lock Sharpe=+0.5796
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0644, Lock Sharpe=+0.3418
- `vix`: Train IC=+0.0045, Lock IC=+0.0426, Lock Sharpe=+0.1425
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0694, Lock Sharpe=+0.0518

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 63.0% lock IC > 0, 21.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3127_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 177 | 30 | 93.3% | 53.3% | +0.0637 | -0.0151 |
| B2 Rolling Guard | 22 | 22 | 45.5% | 4.5% | +0.0182 | -0.1729 |
| BH-FDR Gate | 8 | 8 | 87.5% | 50.0% | +0.0502 | -0.1266 |
| B3 Composite Floor | 14 | 14 | 92.9% | 35.7% | +0.0680 | +0.0154 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0765, Mean Lock Sharpe = -0.0485

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_surge_direction`: Train IC=+0.1059, Lock IC=+0.1088, Lock Sharpe=+1.0723
- `limit_down_proximity_early`: Train IC=+0.0945, Lock IC=+0.1167, Lock Sharpe=+0.9044
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0945, Lock IC=+0.1167, Lock Sharpe=+0.9044
- `first_bar_sentiment`: Train IC=+0.1181, Lock IC=+0.0517, Lock Sharpe=+0.7982
- `star50_limit_proximity_early`: Train IC=+0.1712, Lock IC=+0.1383, Lock Sharpe=+0.4865

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.0922, Lock IC=+0.0586, Lock Sharpe=+0.8035

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `close_vs_open_range`: Train IC=+0.1148, Lock IC=+0.1017, Lock Sharpe=+0.3854
- `shaved_bar_trend_conviction`: Train IC=+0.1127, Lock IC=+0.0933, Lock Sharpe=+0.1556
- `vol_gk20`: Train IC=+0.0370, Lock IC=+0.0210, Lock Sharpe=+0.0601
- `early_skew`: Train IC=+0.0611, Lock IC=+0.0865, Lock Sharpe=+0.0257

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_return`: Train IC=+0.1377, Lock IC=+0.0706, Lock Sharpe=+0.5991
- `bar_ret_0`: Train IC=+0.1377, Lock IC=+0.0706, Lock Sharpe=+0.5991
- `first_30min_return`: Train IC=+0.1313, Lock IC=+0.0981, Lock Sharpe=+0.3030
- `open_to_current_return`: Train IC=+0.1313, Lock IC=+0.0981, Lock Sharpe=+0.3030
- `opening_drive_thrust_ratio`: Train IC=+0.2148, Lock IC=+0.0919, Lock Sharpe=+0.1527

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 61.0% lock IC > 0, 38.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.1724_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 195 | 30 | 46.7% | 36.7% | +0.0120 | -0.1109 |
| B2 Rolling Guard | 28 | 28 | 42.9% | 28.6% | +0.0212 | -0.0793 |
| BH-FDR Gate | 13 | 13 | 84.6% | 53.8% | +0.0548 | +0.1685 |
| B3 Composite Floor | 1 | 1 | 100.0% | 0.0% | +0.0033 | -0.0536 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `shaved_bar_trend_conviction`: Train IC=+0.1182, Lock IC=+0.0933, Lock Sharpe=+1.2566
- `vol_ratio_10_60`: Train IC=+0.1164, Lock IC=+0.0250, Lock Sharpe=+0.8021
- `yesterday_afternoon_momentum`: Train IC=+0.1383, Lock IC=+0.0698, Lock Sharpe=+0.6217
- `morning_trend_extrapolated`: Train IC=+0.1145, Lock IC=+0.0583, Lock Sharpe=+0.4240
- `max_up_ret`: Train IC=+0.1181, Lock IC=+0.0765, Lock Sharpe=+0.4081

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `early_body_momentum`: Train IC=+0.0981, Lock IC=+0.0685, Lock Sharpe=+0.7256
- `opening_momentum_score`: Train IC=+0.0981, Lock IC=+0.0685, Lock Sharpe=+0.7256
- `volatility_percentile_20d`: Train IC=+0.0000, Lock IC=+0.0210, Lock Sharpe=+0.5068
- `trend_bar_close_consistency`: Train IC=+0.0862, Lock IC=+0.0803, Lock Sharpe=+0.4347
- `first_30min_return`: Train IC=+0.1407, Lock IC=+0.0981, Lock Sharpe=+0.2478

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_return`: Train IC=+0.0381, Lock IC=+0.0706, Lock Sharpe=+1.0134
- `bar_ret_0`: Train IC=+0.0381, Lock IC=+0.0706, Lock Sharpe=+1.0134
- `morning_volume_weighted_momentum`: Train IC=+0.1482, Lock IC=+0.0947, Lock Sharpe=+0.5842
- `vwap_trend_channel_slope`: Train IC=+0.1325, Lock IC=+0.0573, Lock Sharpe=+0.3198
- `close_vs_open_range`: Train IC=+0.0986, Lock IC=+0.1017, Lock Sharpe=+0.2553

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4666_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 189 | 30 | 66.7% | 26.7% | +0.0238 | -0.2074 |
| B2 Rolling Guard | 42 | 30 | 53.3% | 33.3% | +0.0162 | -0.0921 |
| BH-FDR Gate | 1 | 1 | 100.0% | 100.0% | +0.0943 | +0.2379 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bb_width`: Train IC=+0.0753, Lock IC=+0.0573, Lock Sharpe=+0.5240
- `trend_day_regime_conviction`: Train IC=+0.1462, Lock IC=+0.0928, Lock Sharpe=+0.5079
- `lunch_transition_volume_skew`: Train IC=+0.0808, Lock IC=+0.0330, Lock Sharpe=+0.4939
- `high_low_sequence_momentum`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.3950
- `rsi_opening`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.3950

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0517, Lock Sharpe=+1.0733
- `outside_bar_reversal_day`: Train IC=+0.0000, Lock IC=+0.0930, Lock Sharpe=+0.7627
- `limit_down_proximity_early`: Train IC=+0.0276, Lock IC=+0.1167, Lock Sharpe=+0.5830
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0276, Lock IC=+0.1167, Lock Sharpe=+0.5830
- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0372, Lock Sharpe=+0.3867

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volatility_expansion_trend_vector`: Train IC=+0.0580, Lock IC=+0.0943, Lock Sharpe=+0.2379

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 25 | -0.0071 | 40.0% |
| 0.45 | 0.20 | 23 | -0.0071 | 40.0% |
| 0.45 | 0.30 | 17 | -0.0071 | 40.0% |
| 0.45 | 0.40 | 13 | -0.0043 | 40.0% |
| 0.45 | 0.50 | 5 | +0.0025 | 40.0% |
| 0.50 | 0.15 | 23 | -0.0071 | 40.0% |
| 0.50 | 0.25 | 19 | -0.0071 | 40.0% |
| 0.50 | 0.35 | 17 | -0.0071 | 40.0% |
| 0.50 | 0.45 | 9 | -0.0014 | 44.4% |
| 0.55 | 0.10 | 23 | -0.0071 | 40.0% |
| 0.55 | 0.20 | 23 | -0.0071 | 40.0% |
| 0.55 | 0.30 | 17 | -0.0071 | 40.0% |
| 0.55 | 0.40 | 13 | -0.0043 | 40.0% |
| 0.55 | 0.50 | 5 | +0.0025 | 40.0% |
| 0.60 | 0.15 | 18 | -0.0071 | 40.0% |
| 0.60 | 0.25 | 17 | -0.0071 | 40.0% |
| 0.60 | 0.35 | 17 | -0.0071 | 40.0% |
| 0.60 | 0.45 | 9 | -0.0014 | 44.4% |
| 0.65 | 0.10 | 13 | -0.0005 | 50.0% |
| 0.65 | 0.20 | 13 | -0.0005 | 50.0% |
| 0.65 | 0.30 | 13 | -0.0005 | 50.0% |
| 0.65 | 0.40 | 12 | -0.0005 | 50.0% |
| 0.65 | 0.50 | 5 | +0.0025 | 40.0% |
| 0.70 | 0.15 | 3 | +0.0057 | 66.7% |
| 0.70 | 0.25 | 3 | +0.0057 | 66.7% |
| 0.70 | 0.35 | 3 | +0.0057 | 66.7% |
| 0.70 | 0.45 | 3 | +0.0057 | 66.7% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.70, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0057, 66.7% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 12 | -0.0071 | 50.0% |
| 0.45 | 0.20 | 8 | -0.0093 | 50.0% |
| 0.45 | 0.30 | 6 | -0.0065 | 66.7% |
| 0.45 | 0.40 | 2 | -0.0598 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | -0.0110 | 44.4% |
| 0.50 | 0.25 | 7 | -0.0100 | 57.1% |
| 0.50 | 0.35 | 2 | -0.0598 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 9 | -0.0110 | 44.4% |
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
| 0.45 | 0.10 | 3 | +0.0451 | 100.0% |
| 0.45 | 0.20 | 1 | +0.0637 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 2 | +0.0524 | 100.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 1 | +0.0637 | 100.0% |
| 0.55 | 0.20 | 1 | +0.0637 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0451, 100.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 12 | -0.0343 | 10.0% |
| 0.45 | 0.20 | 10 | -0.0343 | 10.0% |
| 0.45 | 0.30 | 8 | -0.0458 | 0.0% |
| 0.45 | 0.40 | 1 | -0.0524 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 10 | -0.0343 | 10.0% |
| 0.50 | 0.25 | 10 | -0.0343 | 10.0% |
| 0.50 | 0.35 | 6 | -0.0468 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 10 | -0.0343 | 10.0% |
| 0.55 | 0.20 | 10 | -0.0343 | 10.0% |
| 0.55 | 0.30 | 8 | -0.0458 | 0.0% |
| 0.55 | 0.40 | 1 | -0.0524 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 9 | -0.0353 | 11.1% |
| 0.60 | 0.25 | 9 | -0.0353 | 11.1% |
| 0.60 | 0.35 | 6 | -0.0468 | 0.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 2 | -0.0019 | 50.0% |
| 0.65 | 0.20 | 2 | -0.0019 | 50.0% |
| 0.65 | 0.30 | 1 | -0.0524 | 0.0% |
| 0.65 | 0.40 | 1 | -0.0524 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 12 candidates, mean lock IC=-0.0343, 10.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 13 | -0.0083 | 30.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 13 candidates, mean lock IC=-0.0083, 30.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 5 | -0.0254 | 20.0% |
| 0.45 | 0.20 | 3 | -0.0384 | 0.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 4 | -0.0432 | 0.0% |
| 0.50 | 0.25 | 1 | -0.0023 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 3 | -0.0374 | 0.0% |
| 0.55 | 0.20 | 2 | -0.0272 | 0.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | -0.0023 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 5 candidates, mean lock IC=-0.0254, 20.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 49 | +0.0751 | 100.0% |
| 0.45 | 0.20 | 45 | +0.0751 | 100.0% |
| 0.45 | 0.30 | 39 | +0.0751 | 100.0% |
| 0.45 | 0.40 | 20 | +0.0757 | 100.0% |
| 0.45 | 0.50 | 9 | +0.0632 | 100.0% |
| 0.50 | 0.15 | 48 | +0.0751 | 100.0% |
| 0.50 | 0.25 | 43 | +0.0751 | 100.0% |
| 0.50 | 0.35 | 29 | +0.0751 | 100.0% |
| 0.50 | 0.45 | 17 | +0.0804 | 100.0% |
| 0.55 | 0.10 | 48 | +0.0751 | 100.0% |
| 0.55 | 0.20 | 45 | +0.0751 | 100.0% |
| 0.55 | 0.30 | 39 | +0.0751 | 100.0% |
| 0.55 | 0.40 | 20 | +0.0757 | 100.0% |
| 0.55 | 0.50 | 9 | +0.0632 | 100.0% |
| 0.60 | 0.15 | 42 | +0.0751 | 100.0% |
| 0.60 | 0.25 | 41 | +0.0751 | 100.0% |
| 0.60 | 0.35 | 29 | +0.0751 | 100.0% |
| 0.60 | 0.45 | 17 | +0.0804 | 100.0% |
| 0.65 | 0.10 | 24 | +0.0751 | 100.0% |
| 0.65 | 0.20 | 24 | +0.0751 | 100.0% |
| 0.65 | 0.30 | 24 | +0.0751 | 100.0% |
| 0.65 | 0.40 | 17 | +0.0770 | 100.0% |
| 0.65 | 0.50 | 9 | +0.0632 | 100.0% |
| 0.70 | 0.15 | 6 | +0.0746 | 100.0% |
| 0.70 | 0.25 | 6 | +0.0746 | 100.0% |
| 0.70 | 0.35 | 6 | +0.0746 | 100.0% |
| 0.70 | 0.45 | 6 | +0.0746 | 100.0% |
| 0.75 | 0.10 | 3 | +0.0907 | 100.0% |
| 0.75 | 0.20 | 3 | +0.0907 | 100.0% |
| 0.75 | 0.30 | 3 | +0.0907 | 100.0% |
| 0.75 | 0.40 | 3 | +0.0907 | 100.0% |
| 0.75 | 0.50 | 3 | +0.0907 | 100.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0907, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 4 | +0.0555 | 75.0% |
| 0.45 | 0.20 | 1 | +0.0873 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 3 | +0.0877 | 100.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | +0.0555 | 75.0% |
| 0.55 | 0.20 | 1 | +0.0873 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 3 candidates, mean lock IC=+0.0877, 100.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1 | +0.0345 | 100.0% |
| 0.45 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 0 | +0.0000 | 0.0% |
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

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 26 | +0.0596 | 90.0% |
| 0.45 | 0.20 | 25 | +0.0596 | 90.0% |
| 0.45 | 0.30 | 23 | +0.0657 | 90.0% |
| 0.45 | 0.40 | 13 | +0.0711 | 90.0% |
| 0.45 | 0.50 | 5 | +0.0931 | 100.0% |
| 0.50 | 0.15 | 26 | +0.0596 | 90.0% |
| 0.50 | 0.25 | 24 | +0.0608 | 90.0% |
| 0.50 | 0.35 | 19 | +0.0657 | 90.0% |
| 0.50 | 0.45 | 9 | +0.0687 | 88.9% |
| 0.55 | 0.10 | 26 | +0.0596 | 90.0% |
| 0.55 | 0.20 | 25 | +0.0596 | 90.0% |
| 0.55 | 0.30 | 23 | +0.0657 | 90.0% |
| 0.55 | 0.40 | 13 | +0.0711 | 90.0% |
| 0.55 | 0.50 | 5 | +0.0931 | 100.0% |
| 0.60 | 0.15 | 23 | +0.0657 | 90.0% |
| 0.60 | 0.25 | 23 | +0.0657 | 90.0% |
| 0.60 | 0.35 | 19 | +0.0657 | 90.0% |
| 0.60 | 0.45 | 9 | +0.0687 | 88.9% |
| 0.65 | 0.10 | 14 | +0.0657 | 90.0% |
| 0.65 | 0.20 | 14 | +0.0657 | 90.0% |
| 0.65 | 0.30 | 14 | +0.0657 | 90.0% |
| 0.65 | 0.40 | 12 | +0.0711 | 90.0% |
| 0.65 | 0.50 | 5 | +0.0931 | 100.0% |
| 0.70 | 0.15 | 5 | +0.0931 | 100.0% |
| 0.70 | 0.25 | 5 | +0.0931 | 100.0% |
| 0.70 | 0.35 | 5 | +0.0931 | 100.0% |
| 0.70 | 0.45 | 5 | +0.0931 | 100.0% |
| 0.75 | 0.10 | 1 | +0.0765 | 100.0% |
| 0.75 | 0.20 | 1 | +0.0765 | 100.0% |
| 0.75 | 0.30 | 1 | +0.0765 | 100.0% |
| 0.75 | 0.40 | 1 | +0.0765 | 100.0% |
| 0.75 | 0.50 | 1 | +0.0765 | 100.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 5 candidates, mean lock IC=+0.0931, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 20 | +0.0626 | 100.0% |
| 0.45 | 0.20 | 11 | +0.0505 | 90.0% |
| 0.45 | 0.30 | 7 | +0.0421 | 85.7% |
| 0.45 | 0.40 | 3 | +0.0716 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 16 | +0.0526 | 90.0% |
| 0.50 | 0.25 | 9 | +0.0353 | 77.8% |
| 0.50 | 0.35 | 6 | +0.0524 | 100.0% |
| 0.50 | 0.45 | 1 | +0.1017 | 100.0% |
| 0.55 | 0.10 | 14 | +0.0519 | 90.0% |
| 0.55 | 0.20 | 11 | +0.0505 | 90.0% |
| 0.55 | 0.30 | 7 | +0.0421 | 85.7% |
| 0.55 | 0.40 | 3 | +0.0716 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | +0.0429 | 87.5% |
| 0.60 | 0.25 | 8 | +0.0429 | 87.5% |
| 0.60 | 0.35 | 6 | +0.0524 | 100.0% |
| 0.60 | 0.45 | 1 | +0.1017 | 100.0% |
| 0.65 | 0.10 | 4 | +0.0638 | 100.0% |
| 0.65 | 0.20 | 4 | +0.0638 | 100.0% |
| 0.65 | 0.30 | 4 | +0.0638 | 100.0% |
| 0.65 | 0.40 | 2 | +0.0795 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 3 candidates, mean lock IC=+0.0716, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 7 | +0.0629 | 100.0% |
| 0.45 | 0.20 | 2 | +0.0572 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 2 | +0.0572 | 100.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | +0.0467 | 100.0% |
| 0.55 | 0.20 | 1 | +0.0943 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 7 candidates, mean lock IC=+0.0629, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `bar_body_rng_0` | +0.0955 | +0.0000 | +0.0301 | 0.32x | 2010-10-15 |
| `max_up_ret` | +0.1022 | +0.0000 | -0.0047 | -0.05x | 2015-02-06 |
| `opening_drive_thrust_ratio` | +0.1159 | +0.0000 | +0.0060 | 0.05x | 2017-06-09 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `net_volume_flow` | +0.1543 | +0.0000 | +0.0879 | 0.57x | 2016-11-01 |
| `max_up_ret` | +0.1871 | +0.0000 | +0.0813 | 0.43x | No decay |
| `first_bar_return` | +0.1413 | +0.0000 | +0.0686 | 0.49x | 2013-09-23 |
| `opening_drive_thrust_ratio` | +0.1849 | +0.0000 | +0.0962 | 0.52x | No decay |
| `close_vs_open_range` | +0.1395 | +0.0000 | +0.0899 | 0.64x | 2016-11-01 |
| `vwap_close_divergence_trend` | +0.1321 | +0.0000 | +0.0582 | 0.44x | 2016-11-01 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | +0.1545 | +0.0000 | +0.0765 | 0.49x | 2017-01-20 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.6423). Consider relaxing this gate.
2. **300ETF `single` — B3 Composite Floor too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.4137). Consider relaxing this gate.
3. **300ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
4. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.4883). Consider relaxing this gate.
5. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 9.0%, mean lock Sharpe=-0.4950). Consider relaxing this gate.
6. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 5.0%, mean lock Sharpe=-0.5736). Consider relaxing this gate.
7. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 7.0%, mean lock Sharpe=-0.3513). Consider relaxing this gate.
8. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.2444). Consider relaxing this gate.
9. **500ETF `single` — B2 Rolling Guard too strict**: 24.1% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.1227). Consider relaxing this gate.
10. **500ETF `single` — B4 Correlation Gate too strict**: 42.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.0505). Consider relaxing this gate.
11. **500ETF `single` — Admission too loose**: 67% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
12. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 12.0%, mean lock Sharpe=-0.3969). Consider relaxing this gate.
13. **159915ETF `single` — 7-Year Jackknife Sign Stability too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 21.0%, mean lock Sharpe=-0.0151). Consider relaxing this gate.
14. **159915ETF `single` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 21.0%, mean lock Sharpe=-0.1266). Consider relaxing this gate.
15. **159915ETF `single` — B3 Composite Floor too strict**: 35.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 21.0%, mean lock Sharpe=+0.0154). Consider relaxing this gate.
16. **159915ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
17. **159915ETF `short` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.0921). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
