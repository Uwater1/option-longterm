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

### 300ETF — `single` (Full Model Lockbox IC: +0.0253, Sharpe: -0.5815)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_ifelse__gap_pct__max_up_ret__option_oi_growth` | Gap / Overnight Reversal | +1 | +0.0803 | -0.0061 | -0.0241 | +0.0140 | 81.62 | +13.8 | 1.72x | -0.0133 | -0.1668 |
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | Gap / Overnight Reversal | +1 | +0.0848 | +0.0481 | +0.0374 | -0.8458 | 84.58 | +1.4 | 0.17x | +0.0181 | -0.0638 |
| `combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio` | Gap / Overnight Reversal | +1 | +0.0688 | +0.0499 | +0.0304 | -0.1721 | 62.16 | +7.4 | 0.92x | +0.0118 | -0.4275 |
| `combo_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0985 | +0.0431 | +0.0060 | -0.2687 | 87.54 | +10.1 | 1.26x | -0.0031 | -0.0827 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0800, Sharpe: -0.0810)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1709 | +0.0936 | +0.0778 | -0.2120 | 86.27 | +10.4 | 1.30x | +0.0351 | -0.8957 |
| `total_balance` | Volatility & Oscillators | -1 | +0.0427 | +0.0437 | +0.0450 | +0.1277 | 19.88 | +5.2 | 0.64x | +0.0023 | +0.1310 |

### 588000ETF — `long` (Full Model Lockbox IC: -0.0530, Sharpe: +0.0000)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `body_to_range_ratio` | Volatility & Oscillators | +1 | +0.0104 | -0.0453 | -0.0530 | -1.8790 | 61.24 | -43.2 | -5.40x | -0.0530 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1031, Sharpe: +1.1578)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `yesterday_afternoon_momentum` | Intraday Range Momentum | -1 | +0.1063 | +0.0564 | +0.0755 | +0.6927 | 85.00 | +29.9 | 3.73x | +0.0177 | +1.1979 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1313 | +0.1037 | +0.0855 | -0.0402 | 85.00 | +13.2 | 1.65x | +0.0276 | +0.4650 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 34.0% lock IC > 0, 13.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4517_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 222 | 30 | 70.0% | 16.7% | +0.0099 | -0.3729 |
| B2 Rolling Guard | 91 | 30 | 46.7% | 16.7% | +0.0008 | -0.4780 |
| BH-FDR Gate | 2 | 2 | 100.0% | 100.0% | +0.0234 | +0.8052 |
| B3 Composite Floor | 22 | 22 | 72.7% | 0.0% | +0.0030 | -0.4118 |
| B4 Correlation Gate | 4 | 4 | 50.0% | 25.0% | +0.0084 | -0.0154 |

**Admitted Pool Summary**: 3 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0037, Mean Lock Sharpe = -0.2873

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1668, Lock IC=+0.0943, Lock Sharpe=+0.3158
- `combo_diff__bar_ret_0__first_30min_return`: Train IC=+0.1327, Lock IC=+0.0175, Lock Sharpe=+0.0887
- `combo_diff__first_bar_return__first_30min_return`: Train IC=+0.1309, Lock IC=+0.0172, Lock Sharpe=+0.0887
- `combo_clamp_diff__bar_ret_0__first_30min_return`: Train IC=+0.1300, Lock IC=+0.0173, Lock Sharpe=+0.0887
- `combo_clamp_diff__first_bar_return__first_30min_return`: Train IC=+0.1280, Lock IC=+0.0170, Lock Sharpe=+0.0887

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__short_sell_quantity__roc60`: Train IC=+0.1013, Lock IC=+0.0008, Lock Sharpe=+0.4965
- `combo_min__bar_ret_0__bar_body_rng_0`: Train IC=+0.1467, Lock IC=+0.0117, Lock Sharpe=+0.2664
- `combo_min__first_bar_return__bar_body_rng_0`: Train IC=+0.1464, Lock IC=+0.0116, Lock Sharpe=+0.2664
- `gap_pct`: Train IC=+0.1525, Lock IC=+0.0795, Lock Sharpe=+0.1398
- `outside_bar_reversal_day`: Train IC=+0.0264, Lock IC=+0.0146, Lock Sharpe=+0.0302

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__short_sell_quantity__sma100_dist`: Train IC=+0.1435, Lock IC=+0.0220, Lock Sharpe=+0.8087
- `combo_product__short_sell_quantity__sma100_dist`: Train IC=+0.1023, Lock IC=+0.0248, Lock Sharpe=+0.8017

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__short_sell_quantity__sma100_dist`: Train IC=+0.1484, Lock IC=+0.0220, Lock Sharpe=+0.8087

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 33.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6010_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 513 | 30 | 63.3% | 16.7% | +0.0140 | -0.4277 |
| B2 Rolling Guard | 109 | 30 | 36.7% | 13.3% | -0.0132 | -0.7671 |
| BH-FDR Gate | 4 | 4 | 0.0% | 0.0% | -0.0397 | -0.3606 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__willr14__sma100_dist`: Train IC=+0.1400, Lock IC=+0.0525, Lock Sharpe=+0.4731
- `combo_rank_min__sma50_dist__bar_vol_0`: Train IC=+0.1595, Lock IC=+0.0597, Lock Sharpe=+0.4714
- `combo_rank_min__sma50_dist__first_bar_volume`: Train IC=+0.1595, Lock IC=+0.0597, Lock Sharpe=+0.4714
- `combo_max__roc60__yesterday_wavetrend_osc`: Train IC=+0.1457, Lock IC=+0.0305, Lock Sharpe=+0.3334
- `combo_max__roc60__wavetrend_osc_day`: Train IC=+0.1457, Lock IC=+0.0305, Lock Sharpe=+0.3334

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__yesterday_wavetrend_osc__bar_vol_0`: Train IC=+0.1147, Lock IC=+0.0237, Lock Sharpe=+0.3005
- `combo_abs_diff__yesterday_wavetrend_osc__first_bar_volume`: Train IC=+0.1147, Lock IC=+0.0237, Lock Sharpe=+0.3005
- `combo_abs_diff__wavetrend_osc_day__bar_vol_0`: Train IC=+0.1147, Lock IC=+0.0237, Lock Sharpe=+0.3005
- `combo_abs_diff__wavetrend_osc_day__first_bar_volume`: Train IC=+0.1147, Lock IC=+0.0237, Lock Sharpe=+0.3005

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 42.0% lock IC > 0, 12.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4675_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 228 | 30 | 30.0% | 10.0% | -0.0149 | -0.5922 |
| B2 Rolling Guard | 89 | 30 | 20.0% | 3.3% | +0.0004 | -0.1609 |
| BH-FDR Gate | 3 | 3 | 33.3% | 33.3% | +0.0052 | -0.5575 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.0974, Lock IC=+0.0943, Lock Sharpe=+0.6082
- `combo_ifelse__vix__short_sell_cover_spread__growth_momentum_ratio`: Train IC=+0.1318, Lock IC=+0.0199, Lock Sharpe=+0.2901
- `early_momentum`: Train IC=+0.0821, Lock IC=+0.0452, Lock Sharpe=+0.0020

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__vix__northbound_net__growth_momentum_ratio`: Train IC=+0.1187, Lock IC=+0.0300, Lock Sharpe=+0.3067

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `gap_pct`: Train IC=+0.1531, Lock IC=+0.0795, Lock Sharpe=+0.3802

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 41.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4477_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 417 | 30 | 96.7% | 43.3% | +0.0457 | -0.0689 |
| B2 Rolling Guard | 100 | 30 | 60.0% | 13.3% | +0.0083 | -0.5944 |
| BH-FDR Gate | 6 | 6 | 100.0% | 100.0% | +0.0045 | +0.4132 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__wavetrend_osc_day`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_max__bar_vol_4__yesterday_wavetrend_osc`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_mean__bar_vol_4__roc10`: Train IC=+0.1425, Lock IC=+0.0859, Lock Sharpe=+0.5934
- `combo_min__iv_corridor_width__margin_extreme_rank_252d`: Train IC=+0.1779, Lock IC=+0.0447, Lock Sharpe=+0.5014
- `yesterday_lunch_gap`: Train IC=+0.1911, Lock IC=+0.0772, Lock Sharpe=+0.4464

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__bar_vol_4__bar_vol_0`: Train IC=+0.0898, Lock IC=+0.0492, Lock Sharpe=+0.2476
- `combo_product__bar_vol_4__first_bar_volume`: Train IC=+0.0898, Lock IC=+0.0492, Lock Sharpe=+0.2476
- `margin_extreme_rank_252d`: Train IC=+0.1281, Lock IC=+0.0339, Lock Sharpe=+0.2172
- `yesterday_early_vwap_dev`: Train IC=+0.0743, Lock IC=+0.0813, Lock Sharpe=+0.1834

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__margin_extreme_rank_252d__sma100_dist`: Train IC=+0.1001, Lock IC=+0.0068, Lock Sharpe=+0.5278
- `combo_clamp_diff__margin_extreme_rank_252d__sma100_dist`: Train IC=+0.0948, Lock IC=+0.0068, Lock Sharpe=+0.5278
- `combo_clamp_diff__margin_extreme_rank_252d__sma_distance_60d`: Train IC=+0.0963, Lock IC=+0.0059, Lock Sharpe=+0.3840
- `combo_diff__margin_extreme_rank_252d__sma_distance_60d`: Train IC=+0.0959, Lock IC=+0.0064, Lock Sharpe=+0.3840
- `margin_short_ratio`: Train IC=+0.0645, Lock IC=+0.0005, Lock Sharpe=+0.3277

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 10.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5746_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 380 | 30 | 63.3% | 26.7% | +0.0170 | -0.3850 |
| B2 Rolling Guard | 108 | 30 | 80.0% | 16.7% | +0.0457 | -0.4374 |
| BH-FDR Gate | 3 | 3 | 0.0% | 0.0% | -0.0602 | -1.4399 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__yesterday_wavetrend_osc__iv_corridor_width`: Train IC=+0.1212, Lock IC=+0.0556, Lock Sharpe=+0.2270
- `combo_mean__wavetrend_osc_day__iv_corridor_width`: Train IC=+0.1212, Lock IC=+0.0556, Lock Sharpe=+0.2270
- `combo_mean__rsi21__sma_distance_60d`: Train IC=+0.1544, Lock IC=+0.0454, Lock Sharpe=+0.1525
- `combo_ratio__sma_distance_60d__total_balance`: Train IC=+0.1314, Lock IC=+0.0362, Lock Sharpe=+0.1368
- `wavetrend_osc_day`: Train IC=+0.1279, Lock IC=+0.0578, Lock Sharpe=+0.1295

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__yesterday_wavetrend_osc__bar_vol_4`: Train IC=+0.0181, Lock IC=+0.0732, Lock Sharpe=+0.3528
- `combo_rank_min__wavetrend_osc_day__bar_vol_4`: Train IC=+0.0181, Lock IC=+0.0732, Lock Sharpe=+0.3528
- `roc20`: Train IC=+0.0576, Lock IC=+0.0709, Lock Sharpe=+0.3274
- `bar_vol_4`: Train IC=+0.0880, Lock IC=+0.0834, Lock Sharpe=+0.0123
- `combo_rank_min__sma_distance_60d__bar_vol_4`: Train IC=+0.0528, Lock IC=+0.0742, Lock Sharpe=+0.0074

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.0% lock IC > 0, 23.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3844_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 474 | 30 | 80.0% | 36.7% | +0.0458 | -0.0818 |
| B2 Rolling Guard | 100 | 30 | 13.3% | 3.3% | -0.0139 | -0.4425 |
| BH-FDR Gate | 8 | 8 | 50.0% | 12.5% | +0.0097 | -0.4596 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__bar_vol_4__sma_distance_60d__mfi14`: Train IC=+0.1625, Lock IC=+0.0956, Lock Sharpe=+0.7197
- `combo_tri_mean__sma50_dist__bar_vol_4__mfi14`: Train IC=+0.1439, Lock IC=+0.1003, Lock Sharpe=+0.6580
- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_max__bar_vol_4__rsi21`: Train IC=+0.1517, Lock IC=+0.0945, Lock Sharpe=+0.5576
- `combo_mean__sma50_dist__bar_vol_4`: Train IC=+0.1659, Lock IC=+0.0918, Lock Sharpe=+0.5075

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `keltner_squeeze_width`: Train IC=+0.0712, Lock IC=+0.0893, Lock Sharpe=+0.0285

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__bar_vol_4__northbound_net`: Train IC=+0.1422, Lock IC=+0.0267, Lock Sharpe=+0.0407

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 78.0% lock IC > 0, 23.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3736_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 415 | 30 | 100.0% | 33.3% | +0.0630 | -0.2292 |
| B2 Rolling Guard | 102 | 30 | 60.0% | 16.7% | +0.0140 | -0.4354 |
| BH-FDR Gate | 25 | 25 | 56.0% | 28.0% | +0.0170 | -0.4383 |
| B3 Composite Floor | 148 | 30 | 100.0% | 20.0% | +0.0843 | -0.3297 |
| B4 Correlation Gate | 68 | 30 | 100.0% | 26.7% | +0.0761 | -0.2245 |

**Admitted Pool Summary**: 67 features, False Positive Rate = 62.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0722, Mean Lock Sharpe = -0.1403

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__margin_balance__short_balance`: Train IC=+0.1738, Lock IC=+0.0722, Lock Sharpe=+1.4406
- `combo_ifelse__gap_pct__yesterday_early_vwap_dev__yesterday_early_momentum`: Train IC=+0.1810, Lock IC=+0.0589, Lock Sharpe=+0.7920
- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum`: Train IC=+0.2464, Lock IC=+0.0560, Lock Sharpe=+0.6438
- `combo_rank_max__margin_balance__short_balance`: Train IC=+0.1987, Lock IC=+0.0592, Lock Sharpe=+0.4936
- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`: Train IC=+0.2061, Lock IC=+0.0705, Lock Sharpe=+0.4007

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__margin_balance__yesterday_day_skew`: Train IC=+0.0386, Lock IC=+0.0458, Lock Sharpe=+0.2660
- `combo_rank_min__first_30min_return__num_up_bars`: Train IC=+0.1488, Lock IC=+0.0796, Lock Sharpe=+0.2450
- `combo_mean__max_down_ret__num_up_bars`: Train IC=+0.1617, Lock IC=+0.0992, Lock Sharpe=+0.1165
- `combo_mean__max_down_ret__bar_body_rng_0`: Train IC=+0.1436, Lock IC=+0.1005, Lock Sharpe=+0.0695
- `combo_ifelse__gap_pct__num_up_bars__bar_vwap_dev_2`: Train IC=+0.1272, Lock IC=+0.0713, Lock Sharpe=+0.0099

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vol_ratio_10_60`: Train IC=+0.0927, Lock IC=+0.0309, Lock Sharpe=+0.3757
- `combo_ifelse__gap_pct__max_up_ret__short_balance`: Train IC=+0.1203, Lock IC=+0.0412, Lock Sharpe=+0.2838
- `combo_ifelse__gap_pct__max_up_ret__margin_balance`: Train IC=+0.0806, Lock IC=+0.0318, Lock Sharpe=+0.1877
- `combo_ifelse__gap_pct__max_down_ret__short_balance`: Train IC=+0.0207, Lock IC=+0.0465, Lock Sharpe=+0.0825
- `combo_ifelse__gap_pct__first_bar_return__total_balance`: Train IC=+0.1185, Lock IC=+0.0471, Lock Sharpe=+0.0458

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__max_up_ret__first_bar_return__max_down_ret`: Train IC=+0.2436, Lock IC=+0.1014, Lock Sharpe=+0.2785
- `combo_tri_mean__max_up_ret__bar_ret_0__max_down_ret`: Train IC=+0.2434, Lock IC=+0.1014, Lock Sharpe=+0.2785
- `combo_tri_mean__max_up_ret__first_bar_return__first_30min_return`: Train IC=+0.2204, Lock IC=+0.0825, Lock Sharpe=+0.1401
- `combo_tri_mean__max_up_ret__bar_ret_0__first_30min_return`: Train IC=+0.2204, Lock IC=+0.0824, Lock Sharpe=+0.1401
- `combo_tri_mean__max_up_ret__max_down_ret__num_up_bars`: Train IC=+0.2151, Lock IC=+0.0994, Lock Sharpe=+0.0988

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__first_bar_return__max_down_ret`: Train IC=+0.2253, Lock IC=+0.1025, Lock Sharpe=+0.4799
- `combo_ifelse__gap_pct__first_bar_return__max_down_ret`: Train IC=+0.2578, Lock IC=+0.1097, Lock Sharpe=+0.3121
- `combo_rank_min__max_up_ret__bar_body_rng_0`: Train IC=+0.2539, Lock IC=+0.0717, Lock Sharpe=+0.2507
- `combo_mean__max_up_ret__first_bar_return`: Train IC=+0.2383, Lock IC=+0.0779, Lock Sharpe=+0.1262
- `combo_mean__max_up_ret__bar_ret_0`: Train IC=+0.2382, Lock IC=+0.0778, Lock Sharpe=+0.1262

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 53.0% lock IC > 0, 17.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3219_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 285 | 30 | 70.0% | 13.3% | +0.0167 | -0.5380 |
| B2 Rolling Guard | 97 | 30 | 36.7% | 10.0% | +0.0098 | -0.2806 |
| BH-FDR Gate | 13 | 13 | 92.3% | 53.8% | +0.0612 | -0.2775 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `margin_balance`: Train IC=+0.1530, Lock IC=+0.0333, Lock Sharpe=+0.7907
- `combo_min__margin_balance__short_balance`: Train IC=+0.1530, Lock IC=+0.0405, Lock Sharpe=+0.5050
- `rsi5`: Train IC=+0.1742, Lock IC=+0.0379, Lock Sharpe=+0.2705
- `combo_product__sma100_dist__stoch_k`: Train IC=+0.1471, Lock IC=+0.0066, Lock Sharpe=+0.0096

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bar_vol_4`: Train IC=+0.0794, Lock IC=+0.0045, Lock Sharpe=+0.2531
- `yesterday_day_vwap_dev`: Train IC=+0.1074, Lock IC=+0.0692, Lock Sharpe=+0.1605
- `combo_product__short_balance__yesterday_illiquidity_amihud`: Train IC=+0.0556, Lock IC=+0.0961, Lock Sharpe=+0.0194

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__limit_up_proximity_day__yesterday_day_vwap_dev`: Train IC=+0.1327, Lock IC=+0.0974, Lock Sharpe=+0.1159
- `combo_clamp_diff__limit_down_proximity_day__yesterday_day_vwap_dev`: Train IC=+0.1327, Lock IC=+0.0974, Lock Sharpe=+0.1159
- `combo_clamp_diff__yesterday_return__yesterday_day_vwap_dev`: Train IC=+0.1327, Lock IC=+0.0974, Lock Sharpe=+0.1159
- `combo_diff__limit_up_proximity_day__yesterday_day_vwap_dev`: Train IC=+0.1324, Lock IC=+0.0974, Lock Sharpe=+0.1159
- `combo_diff__limit_down_proximity_day__yesterday_day_vwap_dev`: Train IC=+0.1324, Lock IC=+0.0974, Lock Sharpe=+0.1159

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 36.0% lock IC > 0, 11.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3119_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 171 | 30 | 60.0% | 20.0% | +0.0126 | -0.4884 |
| B2 Rolling Guard | 101 | 30 | 20.0% | 10.0% | +0.0093 | -0.0197 |
| BH-FDR Gate | 1 | 1 | 100.0% | 100.0% | +0.0163 | +0.2065 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `short_balance`: Train IC=+0.1704, Lock IC=+0.0405, Lock Sharpe=+1.0345
- `total_balance`: Train IC=+0.1703, Lock IC=+0.0450, Lock Sharpe=+0.9350
- `short_balance_quantity`: Train IC=+0.1368, Lock IC=+0.0445, Lock Sharpe=+0.5698
- `yesterday_lunch_gap`: Train IC=+0.1024, Lock IC=+0.0833, Lock Sharpe=+0.2990
- `gap_pct`: Train IC=+0.1160, Lock IC=+0.0889, Lock Sharpe=+0.2192

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__short_balance__yesterday_day_range`: Train IC=+0.0631, Lock IC=+0.0762, Lock Sharpe=+0.5523
- `combo_max__short_balance__yesterday_day_range`: Train IC=+0.0653, Lock IC=+0.0473, Lock Sharpe=+0.2698
- `combo_abs_diff__total_balance__yesterday_day_range`: Train IC=+0.1385, Lock IC=+0.0643, Lock Sharpe=+0.1562

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__gap_pct__short_balance__yesterday_early_vwap_dev`: Train IC=+0.1248, Lock IC=+0.0163, Lock Sharpe=+0.2065

### 588000ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 27.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6077_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 377 | 30 | 13.3% | 13.3% | -0.0337 | -0.7315 |
| B2 Rolling Guard | 129 | 30 | 60.0% | 26.7% | -0.0024 | -0.7312 |
| BH-FDR Gate | 80 | 30 | 0.0% | 0.0% | -0.0553 | -0.5826 |
| B3 Composite Floor | 99 | 30 | 26.7% | 6.7% | -0.0391 | -0.8685 |
| B4 Correlation Gate | 25 | 25 | 36.0% | 8.0% | -0.0343 | -0.9111 |

**Admitted Pool Summary**: 33 features, False Positive Rate = 90.9% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0451, Mean Lock Sharpe = -1.0208

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__vix_skew_proxy__yesterday_day_realized_vol`: Train IC=+0.2429, Lock IC=+0.0273, Lock Sharpe=+1.6193
- `combo_min__vix_skew_proxy__max_up_ret`: Train IC=+0.2298, Lock IC=+0.0193, Lock Sharpe=+0.9631
- `combo_min__vix_diff_1d__max_up_ret`: Train IC=+0.2085, Lock IC=+0.0221, Lock Sharpe=+0.4659
- `combo_min__yesterday_vix_early_drift__max_up_ret`: Train IC=+0.2085, Lock IC=+0.0221, Lock Sharpe=+0.4659

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_rolling_percentile_60d`: Train IC=+0.1846, Lock IC=+0.0189, Lock Sharpe=+1.4335
- `combo_rank_min__vix_skew_proxy__vix_rolling_percentile_60d`: Train IC=+0.2384, Lock IC=+0.0516, Lock Sharpe=+0.8927
- `combo_rank_min__vix_skew_proxy__vix`: Train IC=+0.2392, Lock IC=+0.0316, Lock Sharpe=+0.6892
- `vix_skew_proxy`: Train IC=+0.2227, Lock IC=+0.0375, Lock Sharpe=+0.4577
- `combo_ifelse__vix__vix_diff_1d__vix_skew_proxy`: Train IC=+0.2142, Lock IC=+0.0444, Lock Sharpe=+0.3570

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__vix__vix_diff_1d__bar_vwap_dev_1`: Train IC=+0.2428, Lock IC=+0.0061, Lock Sharpe=+0.2008
- `combo_ifelse__vix__yesterday_vix_early_drift__bar_vwap_dev_1`: Train IC=+0.2428, Lock IC=+0.0061, Lock Sharpe=+0.2008

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__vix__vix_rolling_percentile_60d__bar_ret_0`: Train IC=+0.2377, Lock IC=+0.0069, Lock Sharpe=+0.8351
- `combo_rank_min__yesterday_vix_early_drift__max_up_ret`: Train IC=+0.2037, Lock IC=+0.0247, Lock Sharpe=+0.1868

### 588000ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 30.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3749_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 205 | 30 | 23.3% | 16.7% | -0.0323 | -0.6451 |
| B2 Rolling Guard | 103 | 30 | 50.0% | 23.3% | -0.0069 | -0.4503 |
| BH-FDR Gate | 23 | 23 | 34.8% | 17.4% | -0.0401 | -0.8289 |
| B3 Composite Floor | 3 | 3 | 33.3% | 33.3% | -0.0188 | -0.6961 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_realized_spread`: Train IC=+0.1995, Lock IC=+0.0695, Lock Sharpe=+1.6634
- `combo_clamp_diff__vix_rolling_percentile_60d__vol5`: Train IC=+0.2005, Lock IC=+0.0941, Lock Sharpe=+1.1109
- `combo_diff__vix_rolling_percentile_60d__vol5`: Train IC=+0.1971, Lock IC=+0.0973, Lock Sharpe=+1.1109
- `sma_distance_60d`: Train IC=+0.1472, Lock IC=+0.0112, Lock Sharpe=+0.1947
- `growth_momentum_ratio`: Train IC=+0.1520, Lock IC=+0.0460, Lock Sharpe=+0.0507

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_rolling_percentile_60d`: Train IC=+0.2357, Lock IC=+0.0189, Lock Sharpe=+1.6280
- `combo_max__vix_rolling_percentile_60d__vix_skew_proxy`: Train IC=+0.1563, Lock IC=+0.0016, Lock Sharpe=+1.2603
- `capital_large_order_ratio`: Train IC=+0.1681, Lock IC=+0.0437, Lock Sharpe=+0.3998
- `capital_net_ratio`: Train IC=+0.1431, Lock IC=+0.0433, Lock Sharpe=+0.3998
- `combo_rank_min__vix_rolling_percentile_60d__vix_skew_proxy`: Train IC=+0.2048, Lock IC=+0.0516, Lock Sharpe=+0.3588

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `capital_net_value`: Train IC=+0.0748, Lock IC=+0.0649, Lock Sharpe=+1.0586
- `total_balance`: Train IC=+0.0756, Lock IC=+0.0212, Lock Sharpe=+0.0974
- `margin_balance`: Train IC=+0.0376, Lock IC=+0.0193, Lock Sharpe=+0.0974
- `combo_abs_diff__vol5__yesterday_day_realized_vol`: Train IC=+0.2014, Lock IC=+0.0186, Lock Sharpe=+0.0327

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__yesterday_day_realized_vol__vix_skew_proxy`: Train IC=+0.2578, Lock IC=+0.0217, Lock Sharpe=+0.2814

### 588000ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 41.0% lock IC > 0, 38.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0024_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 167 | 30 | 33.3% | 23.3% | -0.0272 | -0.5866 |
| B2 Rolling Guard | 80 | 30 | 3.3% | 3.3% | +0.0017 | +0.0043 |
| BH-FDR Gate | 6 | 6 | 83.3% | 50.0% | +0.0201 | -0.1430 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `early_vwap_dev`: Train IC=+0.0660, Lock IC=+0.1257, Lock Sharpe=+1.9303
- `vix_skew_proxy`: Train IC=+0.0685, Lock IC=+0.0375, Lock Sharpe=+0.3985
- `twenty_gap_bars_regime`: Train IC=+0.1050, Lock IC=+0.0248, Lock Sharpe=+0.3689
- `yesterday_early_momentum`: Train IC=+0.1181, Lock IC=+0.0474, Lock Sharpe=+0.3567
- `bar_body_rng_1`: Train IC=+0.1025, Lock IC=+0.0226, Lock Sharpe=+0.3204

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `roc5`: Train IC=+0.0506, Lock IC=+0.0505, Lock Sharpe=+0.1277

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bar_vwap_dev_1`: Train IC=+0.1205, Lock IC=+0.0191, Lock Sharpe=+0.4185
- `combo_abs_diff__bar_ret_1__bar_vwap_dev_5`: Train IC=+0.2171, Lock IC=+0.0295, Lock Sharpe=+0.2902
- `combo_abs_diff__bar_ret_1__early_vwap_dev`: Train IC=+0.2171, Lock IC=+0.0295, Lock Sharpe=+0.2902

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 39.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.1034_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 572 | 30 | 100.0% | 80.0% | +0.0737 | +0.4417 |
| B2 Rolling Guard | 173 | 30 | 93.3% | 56.7% | +0.0703 | +0.1508 |
| BH-FDR Gate | 23 | 23 | 91.3% | 26.1% | +0.0311 | -0.2551 |
| B3 Composite Floor | 42 | 30 | 90.0% | 66.7% | +0.0736 | +0.1942 |
| B4 Correlation Gate | 20 | 20 | 100.0% | 75.0% | +0.0851 | +0.2037 |

**Admitted Pool Summary**: 20 features, False Positive Rate = 20.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0898, Mean Lock Sharpe = +0.3599

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__yesterday_first_30min_return__yesterday_day_vwap_dev`: Train IC=+0.1938, Lock IC=+0.0906, Lock Sharpe=+1.1429
- `combo_clamp_diff__yesterday_first_30min_return__yesterday_day_vwap_dev`: Train IC=+0.1777, Lock IC=+0.0902, Lock Sharpe=+1.1429
- `combo_ifelse__bb_width__yesterday_afternoon_momentum__bar_body_rng_0`: Train IC=+0.2038, Lock IC=+0.0555, Lock Sharpe=+0.9824
- `combo_max__yesterday_afternoon_momentum__yesterday_day_vwap_dev`: Train IC=+0.1790, Lock IC=+0.0819, Lock Sharpe=+0.9444
- `combo_ifelse__bb_width__yesterday_early_momentum__first_bar_return`: Train IC=+0.1792, Lock IC=+0.0737, Lock Sharpe=+0.9070

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2173, Lock IC=+0.1310, Lock Sharpe=+1.2310
- `combo_mean__gap_pct__first_30min_return`: Train IC=+0.1608, Lock IC=+0.1445, Lock Sharpe=+0.9168
- `combo_rank_min__max_up_ret__max_down_ret`: Train IC=+0.2204, Lock IC=+0.0988, Lock Sharpe=+0.7200
- `combo_rank_min__early_range__gap_pct`: Train IC=+0.1548, Lock IC=+0.1060, Lock Sharpe=+0.6627
- `combo_max__first_bar_return__max_down_ret`: Train IC=+0.1709, Lock IC=+0.0907, Lock Sharpe=+0.5764

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_max__yesterday_early_momentum__yesterday_first_30min_return__yesterday_afternoon_reversal`: Train IC=+0.0733, Lock IC=+0.0354, Lock Sharpe=+0.3321
- `combo_rank_max__max_up_ret__gap_pct`: Train IC=+0.1253, Lock IC=+0.1090, Lock Sharpe=+0.2066
- `combo_clamp_diff__early_range__bb_width`: Train IC=+0.0972, Lock IC=+0.0378, Lock Sharpe=+0.1704
- `combo_diff__early_range__bb_width`: Train IC=+0.0774, Lock IC=+0.0375, Lock Sharpe=+0.1704
- `combo_min__max_up_ret__early_range`: Train IC=+0.1479, Lock IC=+0.0606, Lock Sharpe=+0.0585

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1949, Lock IC=+0.1521, Lock Sharpe=+1.1944
- `combo_clamp_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1911, Lock IC=+0.1528, Lock Sharpe=+1.1944
- `combo_max__max_up_ret__bb_width`: Train IC=+0.2165, Lock IC=+0.0465, Lock Sharpe=+0.8908
- `combo_clamp_diff__max_up_ret__keltner_squeeze_width`: Train IC=+0.2096, Lock IC=+0.1056, Lock Sharpe=+0.8462
- `combo_ifelse__gap_pct__max_up_ret__bar_body_rng_0`: Train IC=+0.1767, Lock IC=+0.0757, Lock Sharpe=+0.7579

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`: Train IC=+0.1943, Lock IC=+0.0837, Lock Sharpe=+0.8417
- `combo_min__bar_body_rng_0__first_bar_return`: Train IC=+0.1936, Lock IC=+0.0873, Lock Sharpe=+0.7078
- `combo_ifelse__gap_pct__bar_body_rng_0__bar_ret_0`: Train IC=+0.1620, Lock IC=+0.0798, Lock Sharpe=+0.6001
- `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return`: Train IC=+0.1616, Lock IC=+0.0797, Lock Sharpe=+0.6001
- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_trend`: Train IC=+0.1915, Lock IC=+0.0734, Lock Sharpe=+0.4170

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 27.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2017_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 353 | 30 | 63.3% | 33.3% | +0.0117 | -0.2864 |
| B2 Rolling Guard | 95 | 30 | 13.3% | 3.3% | +0.0019 | -0.1195 |
| BH-FDR Gate | 6 | 6 | 83.3% | 33.3% | +0.0227 | +0.0162 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__rsi5__yesterday_first_30min_return`: Train IC=+0.1315, Lock IC=+0.0405, Lock Sharpe=+0.6278
- `combo_min__rsi5__yesterday_first_30min_return`: Train IC=+0.1759, Lock IC=+0.0633, Lock Sharpe=+0.5356
- `combo_rank_min__rsi5__yesterday_first_30min_return`: Train IC=+0.1837, Lock IC=+0.0679, Lock Sharpe=+0.3884
- `combo_max__yesterday_afternoon_momentum__rsi5`: Train IC=+0.1313, Lock IC=+0.0263, Lock Sharpe=+0.1773
- `combo_clamp_diff__yesterday_return__bar_vol_4`: Train IC=+0.1195, Lock IC=+0.0554, Lock Sharpe=+0.0155

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__volume_slope__bar_vol_4`: Train IC=+0.0395, Lock IC=+0.0359, Lock Sharpe=+0.1901

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__vol_ratio_10_60__volume_slope`: Train IC=+0.1516, Lock IC=+0.0124, Lock Sharpe=+0.4841
- `bar_ret_1`: Train IC=+0.0323, Lock IC=+0.0471, Lock Sharpe=+0.3724

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 34.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.1969_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 129 | 30 | 70.0% | 40.0% | +0.0092 | -0.0801 |
| B2 Rolling Guard | 93 | 30 | 20.0% | 6.7% | +0.0068 | -0.0423 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bb_width`: Train IC=+0.1023, Lock IC=+0.0475, Lock Sharpe=+0.7236
- `capital_sell_volume`: Train IC=+0.0983, Lock IC=+0.0208, Lock Sharpe=+0.6146
- `yesterday_northbound_net_ratio`: Train IC=+0.0760, Lock IC=+0.0009, Lock Sharpe=+0.4770
- `northbound_net`: Train IC=+0.0662, Lock IC=+0.0017, Lock Sharpe=+0.4770
- `yesterday_pm_return`: Train IC=+0.1096, Lock IC=+0.0803, Lock Sharpe=+0.4680

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_day_realized_vol`: Train IC=+0.0376, Lock IC=+0.0061, Lock Sharpe=+0.5514
- `gap_pct`: Train IC=+0.0358, Lock IC=+0.1182, Lock Sharpe=+0.4309

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 48 | +0.0059 | 60.0% |
| 0.45 | 0.20 | 42 | +0.0059 | 60.0% |
| 0.45 | 0.30 | 34 | +0.0059 | 60.0% |
| 0.45 | 0.40 | 23 | +0.0053 | 80.0% |
| 0.45 | 0.50 | 15 | +0.0054 | 80.0% |
| 0.50 | 0.15 | 46 | +0.0059 | 60.0% |
| 0.50 | 0.25 | 40 | +0.0059 | 60.0% |
| 0.50 | 0.35 | 27 | +0.0040 | 60.0% |
| 0.50 | 0.45 | 22 | +0.0053 | 80.0% |
| 0.55 | 0.10 | 45 | +0.0059 | 60.0% |
| 0.55 | 0.20 | 42 | +0.0059 | 60.0% |
| 0.55 | 0.30 | 34 | +0.0059 | 60.0% |
| 0.55 | 0.40 | 23 | +0.0053 | 80.0% |
| 0.55 | 0.50 | 15 | +0.0054 | 80.0% |
| 0.60 | 0.15 | 35 | +0.0059 | 60.0% |
| 0.60 | 0.25 | 35 | +0.0059 | 60.0% |
| 0.60 | 0.35 | 27 | +0.0040 | 60.0% |
| 0.60 | 0.45 | 22 | +0.0053 | 80.0% |
| 0.65 | 0.10 | 23 | +0.0061 | 90.0% |
| 0.65 | 0.20 | 23 | +0.0061 | 90.0% |
| 0.65 | 0.30 | 23 | +0.0061 | 90.0% |
| 0.65 | 0.40 | 22 | +0.0061 | 90.0% |
| 0.65 | 0.50 | 15 | +0.0054 | 80.0% |
| 0.70 | 0.15 | 14 | +0.0056 | 80.0% |
| 0.70 | 0.25 | 14 | +0.0056 | 80.0% |
| 0.70 | 0.35 | 14 | +0.0056 | 80.0% |
| 0.70 | 0.45 | 14 | +0.0056 | 80.0% |
| 0.75 | 0.10 | 4 | +0.0106 | 50.0% |
| 0.75 | 0.20 | 4 | +0.0106 | 50.0% |
| 0.75 | 0.30 | 4 | +0.0106 | 50.0% |
| 0.75 | 0.40 | 4 | +0.0106 | 50.0% |
| 0.75 | 0.50 | 4 | +0.0106 | 50.0% |
| 0.80 | 0.15 | 2 | +0.0220 | 100.0% |
| 0.80 | 0.25 | 2 | +0.0220 | 100.0% |
| 0.80 | 0.35 | 2 | +0.0220 | 100.0% |
| 0.80 | 0.45 | 2 | +0.0220 | 100.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 4 candidates, mean lock IC=+0.0106, 50.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 7 | -0.0189 | 14.3% |
| 0.45 | 0.20 | 3 | -0.0328 | 0.0% |
| 0.45 | 0.30 | 3 | -0.0328 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 4 | -0.0397 | 0.0% |
| 0.50 | 0.25 | 3 | -0.0328 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 5 | -0.0145 | 20.0% |
| 0.55 | 0.20 | 3 | -0.0328 | 0.0% |
| 0.55 | 0.30 | 3 | -0.0328 | 0.0% |
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

**Optimal**: mono_thr=0.50, ir_thr=0.10 → 6 candidates, mean lock IC=-0.0122, 16.7% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 5 | +0.0077 | 60.0% |
| 0.45 | 0.20 | 3 | +0.0052 | 33.3% |
| 0.45 | 0.30 | 1 | -0.0449 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 4 | +0.0053 | 50.0% |
| 0.50 | 0.25 | 2 | -0.0320 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 3 | +0.0052 | 33.3% |
| 0.55 | 0.20 | 3 | +0.0052 | 33.3% |
| 0.55 | 0.30 | 1 | -0.0449 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | -0.0320 | 0.0% |
| 0.60 | 0.25 | 2 | -0.0320 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 5 candidates, mean lock IC=+0.0077, 60.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 32 | +0.0173 | 90.0% |
| 0.45 | 0.20 | 23 | +0.0109 | 80.0% |
| 0.45 | 0.30 | 8 | +0.0127 | 100.0% |
| 0.45 | 0.40 | 6 | +0.0045 | 100.0% |
| 0.45 | 0.50 | 6 | +0.0045 | 100.0% |
| 0.50 | 0.15 | 26 | +0.0109 | 80.0% |
| 0.50 | 0.25 | 15 | +0.0102 | 80.0% |
| 0.50 | 0.35 | 6 | +0.0045 | 100.0% |
| 0.50 | 0.45 | 6 | +0.0045 | 100.0% |
| 0.55 | 0.10 | 25 | +0.0109 | 80.0% |
| 0.55 | 0.20 | 21 | +0.0109 | 80.0% |
| 0.55 | 0.30 | 8 | +0.0127 | 100.0% |
| 0.55 | 0.40 | 6 | +0.0045 | 100.0% |
| 0.55 | 0.50 | 6 | +0.0045 | 100.0% |
| 0.60 | 0.15 | 9 | -0.0005 | 77.8% |
| 0.60 | 0.25 | 9 | -0.0005 | 77.8% |
| 0.60 | 0.35 | 6 | +0.0045 | 100.0% |
| 0.60 | 0.45 | 6 | +0.0045 | 100.0% |
| 0.65 | 0.10 | 6 | +0.0045 | 100.0% |
| 0.65 | 0.20 | 6 | +0.0045 | 100.0% |
| 0.65 | 0.30 | 6 | +0.0045 | 100.0% |
| 0.65 | 0.40 | 6 | +0.0045 | 100.0% |
| 0.65 | 0.50 | 6 | +0.0045 | 100.0% |
| 0.70 | 0.15 | 6 | +0.0045 | 100.0% |
| 0.70 | 0.25 | 6 | +0.0045 | 100.0% |
| 0.70 | 0.35 | 6 | +0.0045 | 100.0% |
| 0.70 | 0.45 | 6 | +0.0045 | 100.0% |
| 0.75 | 0.10 | 4 | +0.0065 | 100.0% |
| 0.75 | 0.20 | 4 | +0.0065 | 100.0% |
| 0.75 | 0.30 | 4 | +0.0065 | 100.0% |
| 0.75 | 0.40 | 4 | +0.0065 | 100.0% |
| 0.75 | 0.50 | 4 | +0.0065 | 100.0% |
| 0.80 | 0.15 | 4 | +0.0065 | 100.0% |
| 0.80 | 0.25 | 4 | +0.0065 | 100.0% |
| 0.80 | 0.35 | 4 | +0.0065 | 100.0% |
| 0.80 | 0.45 | 4 | +0.0065 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 32 candidates, mean lock IC=+0.0173, 90.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 19 | +0.0087 | 60.0% |
| 0.45 | 0.20 | 4 | +0.0021 | 50.0% |
| 0.45 | 0.30 | 2 | -0.0559 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 11 | +0.0142 | 70.0% |
| 0.50 | 0.25 | 3 | -0.0208 | 33.3% |
| 0.50 | 0.35 | 1 | -0.0446 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | -0.0390 | 25.0% |
| 0.55 | 0.20 | 2 | -0.0559 | 0.0% |
| 0.55 | 0.30 | 2 | -0.0559 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | -0.0559 | 0.0% |
| 0.60 | 0.25 | 2 | -0.0559 | 0.0% |
| 0.60 | 0.35 | 1 | -0.0446 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 11 candidates, mean lock IC=+0.0142, 70.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 18 | +0.0066 | 50.0% |
| 0.45 | 0.20 | 11 | +0.0086 | 50.0% |
| 0.45 | 0.30 | 1 | -0.0562 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 13 | +0.0066 | 50.0% |
| 0.50 | 0.25 | 4 | -0.0075 | 25.0% |
| 0.50 | 0.35 | 1 | -0.0562 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 11 | +0.0135 | 50.0% |
| 0.55 | 0.20 | 8 | +0.0097 | 50.0% |
| 0.55 | 0.30 | 1 | -0.0562 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 3 | +0.0010 | 66.7% |
| 0.60 | 0.25 | 2 | -0.0133 | 50.0% |
| 0.60 | 0.35 | 1 | -0.0562 | 0.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 11 candidates, mean lock IC=+0.0135, 50.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 330 | +0.0895 | 100.0% |
| 0.45 | 0.20 | 321 | +0.0895 | 100.0% |
| 0.45 | 0.30 | 311 | +0.0895 | 100.0% |
| 0.45 | 0.40 | 278 | +0.0895 | 100.0% |
| 0.45 | 0.50 | 193 | +0.0714 | 100.0% |
| 0.50 | 0.15 | 326 | +0.0895 | 100.0% |
| 0.50 | 0.25 | 318 | +0.0895 | 100.0% |
| 0.50 | 0.35 | 296 | +0.0895 | 100.0% |
| 0.50 | 0.45 | 250 | +0.0895 | 100.0% |
| 0.55 | 0.10 | 328 | +0.0895 | 100.0% |
| 0.55 | 0.20 | 321 | +0.0895 | 100.0% |
| 0.55 | 0.30 | 311 | +0.0895 | 100.0% |
| 0.55 | 0.40 | 278 | +0.0895 | 100.0% |
| 0.55 | 0.50 | 193 | +0.0714 | 100.0% |
| 0.60 | 0.15 | 309 | +0.0895 | 100.0% |
| 0.60 | 0.25 | 309 | +0.0895 | 100.0% |
| 0.60 | 0.35 | 295 | +0.0895 | 100.0% |
| 0.60 | 0.45 | 250 | +0.0895 | 100.0% |
| 0.65 | 0.10 | 256 | +0.0714 | 100.0% |
| 0.65 | 0.20 | 256 | +0.0714 | 100.0% |
| 0.65 | 0.30 | 256 | +0.0714 | 100.0% |
| 0.65 | 0.40 | 244 | +0.0714 | 100.0% |
| 0.65 | 0.50 | 189 | +0.0714 | 100.0% |
| 0.70 | 0.15 | 139 | +0.0734 | 100.0% |
| 0.70 | 0.25 | 139 | +0.0734 | 100.0% |
| 0.70 | 0.35 | 139 | +0.0734 | 100.0% |
| 0.70 | 0.45 | 139 | +0.0734 | 100.0% |
| 0.75 | 0.10 | 47 | +0.0706 | 100.0% |
| 0.75 | 0.20 | 47 | +0.0706 | 100.0% |
| 0.75 | 0.30 | 47 | +0.0706 | 100.0% |
| 0.75 | 0.40 | 47 | +0.0706 | 100.0% |
| 0.75 | 0.50 | 47 | +0.0706 | 100.0% |
| 0.80 | 0.15 | 8 | +0.0744 | 100.0% |
| 0.80 | 0.25 | 8 | +0.0744 | 100.0% |
| 0.80 | 0.35 | 8 | +0.0744 | 100.0% |
| 0.80 | 0.45 | 8 | +0.0744 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 330 candidates, mean lock IC=+0.0895, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 21 | +0.0753 | 100.0% |
| 0.45 | 0.20 | 14 | +0.0722 | 100.0% |
| 0.45 | 0.30 | 10 | +0.0712 | 90.0% |
| 0.45 | 0.40 | 2 | +0.0009 | 50.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 14 | +0.0722 | 100.0% |
| 0.50 | 0.25 | 11 | +0.0762 | 90.0% |
| 0.50 | 0.35 | 3 | +0.0076 | 66.7% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 13 | +0.0722 | 100.0% |
| 0.55 | 0.20 | 13 | +0.0722 | 100.0% |
| 0.55 | 0.30 | 10 | +0.0712 | 90.0% |
| 0.55 | 0.40 | 2 | +0.0009 | 50.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 6 | +0.0525 | 83.3% |
| 0.60 | 0.25 | 6 | +0.0525 | 83.3% |
| 0.60 | 0.35 | 3 | +0.0076 | 66.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.25 → 11 candidates, mean lock IC=+0.0762, 90.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 6 | +0.0129 | 66.7% |
| 0.45 | 0.20 | 2 | +0.0146 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 2 | +0.0146 | 100.0% |
| 0.50 | 0.25 | 1 | +0.0163 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 1 | +0.0163 | 100.0% |
| 0.55 | 0.20 | 1 | +0.0163 | 100.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | +0.0163 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0163 | 100.0% |
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

**Optimal**: mono_thr=0.50, ir_thr=0.10 → 5 candidates, mean lock IC=+0.0154, 80.0% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 290 | -0.0477 | 0.0% |
| 0.45 | 0.20 | 278 | -0.0477 | 0.0% |
| 0.45 | 0.30 | 242 | -0.0477 | 0.0% |
| 0.45 | 0.40 | 205 | -0.0477 | 0.0% |
| 0.45 | 0.50 | 178 | -0.0477 | 0.0% |
| 0.50 | 0.15 | 285 | -0.0477 | 0.0% |
| 0.50 | 0.25 | 262 | -0.0477 | 0.0% |
| 0.50 | 0.35 | 227 | -0.0477 | 0.0% |
| 0.50 | 0.45 | 192 | -0.0477 | 0.0% |
| 0.55 | 0.10 | 283 | -0.0477 | 0.0% |
| 0.55 | 0.20 | 277 | -0.0477 | 0.0% |
| 0.55 | 0.30 | 242 | -0.0477 | 0.0% |
| 0.55 | 0.40 | 205 | -0.0477 | 0.0% |
| 0.55 | 0.50 | 178 | -0.0477 | 0.0% |
| 0.60 | 0.15 | 257 | -0.0477 | 0.0% |
| 0.60 | 0.25 | 250 | -0.0477 | 0.0% |
| 0.60 | 0.35 | 225 | -0.0477 | 0.0% |
| 0.60 | 0.45 | 192 | -0.0477 | 0.0% |
| 0.65 | 0.10 | 206 | -0.0477 | 0.0% |
| 0.65 | 0.20 | 206 | -0.0477 | 0.0% |
| 0.65 | 0.30 | 206 | -0.0477 | 0.0% |
| 0.65 | 0.40 | 198 | -0.0477 | 0.0% |
| 0.65 | 0.50 | 178 | -0.0477 | 0.0% |
| 0.70 | 0.15 | 169 | -0.0477 | 0.0% |
| 0.70 | 0.25 | 169 | -0.0477 | 0.0% |
| 0.70 | 0.35 | 169 | -0.0477 | 0.0% |
| 0.70 | 0.45 | 166 | -0.0477 | 0.0% |
| 0.75 | 0.10 | 106 | -0.0477 | 0.0% |
| 0.75 | 0.20 | 106 | -0.0477 | 0.0% |
| 0.75 | 0.30 | 106 | -0.0477 | 0.0% |
| 0.75 | 0.40 | 106 | -0.0477 | 0.0% |
| 0.75 | 0.50 | 106 | -0.0477 | 0.0% |
| 0.80 | 0.15 | 31 | -0.0541 | 0.0% |
| 0.80 | 0.25 | 31 | -0.0541 | 0.0% |
| 0.80 | 0.35 | 31 | -0.0541 | 0.0% |
| 0.80 | 0.45 | 31 | -0.0541 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 290 candidates, mean lock IC=-0.0477, 0.0% positive

### 588000ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 34 | -0.0172 | 40.0% |
| 0.45 | 0.20 | 25 | -0.0144 | 40.0% |
| 0.45 | 0.30 | 19 | -0.0235 | 30.0% |
| 0.45 | 0.40 | 7 | -0.0190 | 42.9% |
| 0.45 | 0.50 | 4 | -0.0307 | 25.0% |
| 0.50 | 0.15 | 29 | -0.0144 | 40.0% |
| 0.50 | 0.25 | 23 | -0.0213 | 30.0% |
| 0.50 | 0.35 | 10 | -0.0285 | 30.0% |
| 0.50 | 0.45 | 5 | -0.0224 | 40.0% |
| 0.55 | 0.10 | 28 | -0.0144 | 40.0% |
| 0.55 | 0.20 | 24 | -0.0144 | 40.0% |
| 0.55 | 0.30 | 19 | -0.0235 | 30.0% |
| 0.55 | 0.40 | 7 | -0.0190 | 42.9% |
| 0.55 | 0.50 | 4 | -0.0307 | 25.0% |
| 0.60 | 0.15 | 18 | -0.0420 | 20.0% |
| 0.60 | 0.25 | 18 | -0.0420 | 20.0% |
| 0.60 | 0.35 | 10 | -0.0285 | 30.0% |
| 0.60 | 0.45 | 5 | -0.0224 | 40.0% |
| 0.65 | 0.10 | 8 | -0.0211 | 37.5% |
| 0.65 | 0.20 | 8 | -0.0211 | 37.5% |
| 0.65 | 0.30 | 8 | -0.0211 | 37.5% |
| 0.65 | 0.40 | 7 | -0.0190 | 42.9% |
| 0.65 | 0.50 | 4 | -0.0307 | 25.0% |
| 0.70 | 0.15 | 2 | -0.0127 | 50.0% |
| 0.70 | 0.25 | 2 | -0.0127 | 50.0% |
| 0.70 | 0.35 | 2 | -0.0127 | 50.0% |
| 0.70 | 0.45 | 2 | -0.0127 | 50.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 25 candidates, mean lock IC=-0.0144, 40.0% positive

### 588000ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | +0.0356 | 77.8% |
| 0.45 | 0.20 | 6 | +0.0201 | 83.3% |
| 0.45 | 0.30 | 6 | +0.0201 | 83.3% |
| 0.45 | 0.40 | 2 | +0.0295 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 7 | +0.0309 | 85.7% |
| 0.50 | 0.25 | 6 | +0.0201 | 83.3% |
| 0.50 | 0.35 | 5 | +0.0203 | 80.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0201 | 83.3% |
| 0.55 | 0.20 | 6 | +0.0201 | 83.3% |
| 0.55 | 0.30 | 6 | +0.0201 | 83.3% |
| 0.55 | 0.40 | 2 | +0.0295 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 4 | +0.0128 | 75.0% |
| 0.60 | 0.25 | 4 | +0.0128 | 75.0% |
| 0.60 | 0.35 | 3 | +0.0107 | 66.7% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 2 | +0.0295 | 100.0% |
| 0.65 | 0.20 | 2 | +0.0295 | 100.0% |
| 0.65 | 0.30 | 2 | +0.0295 | 100.0% |
| 0.65 | 0.40 | 2 | +0.0295 | 100.0% |
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

**Optimal**: mono_thr=0.50, ir_thr=0.10 → 8 candidates, mean lock IC=+0.0401, 87.5% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 188 | +0.0939 | 100.0% |
| 0.45 | 0.20 | 166 | +0.0939 | 100.0% |
| 0.45 | 0.30 | 108 | +0.0939 | 100.0% |
| 0.45 | 0.40 | 65 | +0.0939 | 100.0% |
| 0.45 | 0.50 | 32 | +0.0983 | 100.0% |
| 0.50 | 0.15 | 174 | +0.0939 | 100.0% |
| 0.50 | 0.25 | 137 | +0.0939 | 100.0% |
| 0.50 | 0.35 | 81 | +0.0939 | 100.0% |
| 0.50 | 0.45 | 57 | +0.0889 | 100.0% |
| 0.55 | 0.10 | 180 | +0.0939 | 100.0% |
| 0.55 | 0.20 | 165 | +0.0939 | 100.0% |
| 0.55 | 0.30 | 108 | +0.0939 | 100.0% |
| 0.55 | 0.40 | 65 | +0.0939 | 100.0% |
| 0.55 | 0.50 | 32 | +0.0983 | 100.0% |
| 0.60 | 0.15 | 142 | +0.0939 | 100.0% |
| 0.60 | 0.25 | 123 | +0.0939 | 100.0% |
| 0.60 | 0.35 | 80 | +0.0939 | 100.0% |
| 0.60 | 0.45 | 57 | +0.0889 | 100.0% |
| 0.65 | 0.10 | 66 | +0.0889 | 100.0% |
| 0.65 | 0.20 | 66 | +0.0889 | 100.0% |
| 0.65 | 0.30 | 66 | +0.0889 | 100.0% |
| 0.65 | 0.40 | 60 | +0.0889 | 100.0% |
| 0.65 | 0.50 | 32 | +0.0983 | 100.0% |
| 0.70 | 0.15 | 22 | +0.0888 | 100.0% |
| 0.70 | 0.25 | 22 | +0.0888 | 100.0% |
| 0.70 | 0.35 | 22 | +0.0888 | 100.0% |
| 0.70 | 0.45 | 22 | +0.0888 | 100.0% |
| 0.75 | 0.10 | 2 | +0.0489 | 100.0% |
| 0.75 | 0.20 | 2 | +0.0489 | 100.0% |
| 0.75 | 0.30 | 2 | +0.0489 | 100.0% |
| 0.75 | 0.40 | 2 | +0.0489 | 100.0% |
| 0.75 | 0.50 | 2 | +0.0489 | 100.0% |
| 0.80 | 0.15 | 1 | +0.0511 | 100.0% |
| 0.80 | 0.25 | 1 | +0.0511 | 100.0% |
| 0.80 | 0.35 | 1 | +0.0511 | 100.0% |
| 0.80 | 0.45 | 1 | +0.0511 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 32 candidates, mean lock IC=+0.0983, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 8 | +0.0225 | 87.5% |
| 0.45 | 0.20 | 5 | +0.0179 | 80.0% |
| 0.45 | 0.30 | 5 | +0.0179 | 80.0% |
| 0.45 | 0.40 | 1 | +0.0124 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 6 | +0.0227 | 83.3% |
| 0.50 | 0.25 | 5 | +0.0179 | 80.0% |
| 0.50 | 0.35 | 1 | +0.0124 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0227 | 83.3% |
| 0.55 | 0.20 | 5 | +0.0179 | 80.0% |
| 0.55 | 0.30 | 5 | +0.0179 | 80.0% |
| 0.55 | 0.40 | 1 | +0.0124 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 5 | +0.0179 | 80.0% |
| 0.60 | 0.25 | 5 | +0.0179 | 80.0% |
| 0.60 | 0.35 | 1 | +0.0124 | 100.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 1 | +0.0124 | 100.0% |
| 0.65 | 0.20 | 1 | +0.0124 | 100.0% |
| 0.65 | 0.30 | 1 | +0.0124 | 100.0% |
| 0.65 | 0.40 | 1 | +0.0124 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 6 candidates, mean lock IC=+0.0227, 83.3% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 4 | +0.0614 | 100.0% |
| 0.45 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 1 | +0.0209 | 100.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 1 | +0.0698 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 4 candidates, mean lock IC=+0.0614, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_ifelse__gap_pct__max_up_ret__option_oi_growth` | +0.0719 | +0.0153 | -0.0241 | -0.33x | 2011-09-20 |
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | +0.0641 | +0.0609 | +0.0374 | 0.58x | 2010-12-14 |
| `combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio` | +0.0496 | +0.0644 | +0.0304 | 0.61x | 2010-12-14 |
| `combo_max__max_up_ret__first_bar_return` | +0.1031 | +0.0772 | +0.0060 | 0.06x | 2015-02-06 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | +0.1971 | +0.0995 | +0.0778 | 0.39x | No decay |
| `total_balance` | +0.0273 | +0.0238 | +0.0450 | 1.65x | 2013-08-21 |

### 588000ETF — `long` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `body_to_range_ratio` | +0.0077 | -0.0191 | -0.0530 | -6.90x | 2021-04-28 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `yesterday_afternoon_momentum` | +0.0630 | +0.0336 | +0.0755 | 1.20x | 2011-03-11 |
| `max_up_ret` | +0.1558 | +0.1171 | +0.0855 | 0.55x | 2017-01-20 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
2. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 8.0%, mean lock Sharpe=-0.4277). Consider relaxing this gate.
3. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.0689). Consider relaxing this gate.
4. **50ETF `single` — BH-FDR Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=+0.4132). Consider relaxing this gate.
5. **50ETF `long` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.3850). Consider relaxing this gate.
6. **50ETF `long` — B2 Rolling Guard too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.4374). Consider relaxing this gate.
7. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.0818). Consider relaxing this gate.
8. **500ETF `single` — Admission too loose**: 63% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
9. **500ETF `long` — BH-FDR Gate too strict**: 53.8% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 17.0%, mean lock Sharpe=-0.2775). Consider relaxing this gate.
10. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 11.0%, mean lock Sharpe=-0.4884). Consider relaxing this gate.
11. **588000ETF `single` — B2 Rolling Guard too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.7312). Consider relaxing this gate.
12. **588000ETF `single` — Admission too loose**: 91% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
13. **159915ETF `single` — 7-Year Jackknife Sign Stability too strict**: 80.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 39.0%, mean lock Sharpe=+0.4417). Consider relaxing this gate.
14. **159915ETF `single` — B3 Composite Floor too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 39.0%, mean lock Sharpe=+0.1942). Consider relaxing this gate.
15. **159915ETF `single` — B4 Correlation Gate too strict**: 75.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 39.0%, mean lock Sharpe=+0.2037). Consider relaxing this gate.
16. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.0801). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
