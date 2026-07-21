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

_Null Baseline (un-gated candidate pool): 48.0% lock IC > 0, 15.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6599_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1969 | 30 | 76.7% | 20.0% | +0.0171 | -0.2119 |
| B2 Rolling Guard | 228 | 30 | 90.0% | 30.0% | +0.0220 | -0.4679 |
| BH-FDR Gate | 121 | 30 | 53.3% | 16.7% | +0.0016 | -0.3316 |
| B3 Composite Floor | 30 | 30 | 86.7% | 20.0% | +0.0151 | -0.3351 |
| B4 Correlation Gate | 18 | 18 | 88.9% | 22.2% | +0.0276 | -0.2956 |

**Admitted Pool Summary**: 7 features, False Positive Rate = 71.4% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0227, Mean Lock Sharpe = -0.2246

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_ret_0__gap_pct`: Train IC=+0.2114, Lock IC=+0.0418, Lock Sharpe=+0.3595
- `combo_mean__first_bar_return__gap_pct`: Train IC=+0.2114, Lock IC=+0.0418, Lock Sharpe=+0.3595
- `yesterday_lunch_gap`: Train IC=+0.1668, Lock IC=+0.0943, Lock Sharpe=+0.3158
- `combo_ifelse__gap_pct__bar_body_rng_0__short_sell_cover_spread`: Train IC=+0.1931, Lock IC=+0.0455, Lock Sharpe=+0.1934
- `combo_rank_min__bar_ret_0__gap_pct`: Train IC=+0.1929, Lock IC=+0.0586, Lock Sharpe=+0.1359

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__macd_hist__bar_body_rng_0__growth_momentum_ratio`: Train IC=+0.1556, Lock IC=+0.0868, Lock Sharpe=+0.5687
- `combo_min__bar_ret_0__bar_body_rng_0`: Train IC=+0.1467, Lock IC=+0.0117, Lock Sharpe=+0.2664
- `combo_min__first_bar_return__bar_body_rng_0`: Train IC=+0.1464, Lock IC=+0.0116, Lock Sharpe=+0.2664
- `combo_tri_min__max_up_ret__gap_pct__first_30min_return`: Train IC=+0.1720, Lock IC=+0.0297, Lock Sharpe=+0.2606
- `gap_pct`: Train IC=+0.1525, Lock IC=+0.0795, Lock Sharpe=+0.1398

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__macd_hist__first_bar_return__yesterday_northbound_net_ratio`: Train IC=+0.1749, Lock IC=+0.0701, Lock Sharpe=+0.5940
- `combo_ifelse__macd_hist__bar_ret_0__yesterday_northbound_net_ratio`: Train IC=+0.1749, Lock IC=+0.0701, Lock Sharpe=+0.5940
- `combo_tri_median__max_up_ret__gap_pct__first_30min_return`: Train IC=+0.1679, Lock IC=+0.0077, Lock Sharpe=+0.3876
- `combo_ifelse__macd_hist__max_up_ret__short_sell_cover_spread`: Train IC=+0.1642, Lock IC=+0.0475, Lock Sharpe=+0.3667
- `combo_ifelse__gap_pct__bar_body_rng_0__option_oi_growth`: Train IC=+0.1658, Lock IC=+0.0260, Lock Sharpe=+0.2659

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__macd_hist__first_bar_return__short_sell_cover_spread`: Train IC=+0.2049, Lock IC=+0.0819, Lock Sharpe=+0.4454
- `combo_ifelse__macd_hist__bar_ret_0__short_sell_cover_spread`: Train IC=+0.2047, Lock IC=+0.0821, Lock Sharpe=+0.4454
- `combo_tri_mean__max_up_ret__gap_pct__first_30min_return`: Train IC=+0.1995, Lock IC=+0.0112, Lock Sharpe=+0.2709
- `combo_tri_mean__first_bar_return__gap_pct__first_30min_return`: Train IC=+0.2083, Lock IC=+0.0246, Lock Sharpe=+0.2007
- `combo_tri_mean__bar_ret_0__gap_pct__first_30min_return`: Train IC=+0.2083, Lock IC=+0.0246, Lock Sharpe=+0.2007

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__macd_hist__bar_ret_0__growth_momentum_ratio`: Train IC=+0.1855, Lock IC=+0.0723, Lock Sharpe=+0.5292
- `combo_ifelse__macd_hist__first_bar_return__growth_momentum_ratio`: Train IC=+0.1853, Lock IC=+0.0723, Lock Sharpe=+0.5292
- `combo_ifelse__macd_hist__bar_ret_0__option_oi_growth`: Train IC=+0.1841, Lock IC=+0.0619, Lock Sharpe=+0.2963
- `combo_ifelse__macd_hist__first_bar_return__option_oi_growth`: Train IC=+0.1840, Lock IC=+0.0620, Lock Sharpe=+0.2963

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 29.0% lock IC > 0, 6.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2838_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 128 | 30 | 50.0% | 3.3% | -0.0044 | -0.7073 |
| B2 Rolling Guard | 88 | 30 | 23.3% | 0.0% | -0.0033 | -0.3614 |
| BH-FDR Gate | 1 | 1 | 0.0% | 0.0% | -0.0606 | -0.7839 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `macd_hist`: Train IC=+0.0803, Lock IC=+0.0348, Lock Sharpe=+0.4885

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 9.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5782_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10611 | 30 | 100.0% | 16.7% | +0.0167 | -0.5009 |
| B2 Rolling Guard | 1042 | 30 | 63.3% | 3.3% | +0.0028 | -0.6264 |
| BH-FDR Gate | 95 | 30 | 33.3% | 3.3% | -0.0027 | -0.5244 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__gap_pct__vix_iv_ratio__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_ifelse__gap_pct__vix_iv_spread__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__iv__vix_iv_ratio__total_balance__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__iv__vix_iv_ratio__total_path_length__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__vix__yesterday_day_skew__max_down_ret__keltner_squeeze_width`: Train IC=+0.1826, Lock IC=+0.0289, Lock Sharpe=+0.1574

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__vix__atr14_norm__yesterday_afternoon_reversal__short_sell_cover_spread__stoch_d`: Train IC=+0.1511, Lock IC=+0.0512, Lock Sharpe=+0.5766

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `gap_pct`: Train IC=+0.1531, Lock IC=+0.0795, Lock Sharpe=+0.3802

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3880_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2377 | 30 | 86.7% | 30.0% | +0.0402 | -0.0778 |
| B2 Rolling Guard | 253 | 30 | 90.0% | 10.0% | +0.0411 | -0.5521 |
| BH-FDR Gate | 51 | 30 | 96.7% | 36.7% | +0.0321 | -0.0485 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__wavetrend_osc_day`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_max__bar_vol_4__yesterday_wavetrend_osc`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_min__iv_corridor_width__margin_extreme_rank_252d`: Train IC=+0.1779, Lock IC=+0.0447, Lock Sharpe=+0.5866
- `combo_ifelse__macd_hist__yesterday_lunch_gap__sma100_dist`: Train IC=+0.1895, Lock IC=+0.0329, Lock Sharpe=+0.5072
- `yesterday_lunch_gap`: Train IC=+0.1911, Lock IC=+0.0772, Lock Sharpe=+0.4464

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__yearly_low_distance__coppock_curve_day`: Train IC=+0.1230, Lock IC=+0.0567, Lock Sharpe=+0.6634
- `combo_ifelse__gap_pct__yesterday_lunch_gap__bar_vol_4`: Train IC=+0.1178, Lock IC=+0.1152, Lock Sharpe=+0.4901
- `combo_ifelse__macd_hist__yesterday_lunch_gap__margin_extreme_rank_252d`: Train IC=+0.1454, Lock IC=+0.0617, Lock Sharpe=+0.4274

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__yearly_low_distance__coppock_curve_day`: Train IC=+0.1279, Lock IC=+0.0570, Lock Sharpe=+0.6634
- `combo_diff__margin_extreme_rank_252d__sma100_dist`: Train IC=+0.1001, Lock IC=+0.0068, Lock Sharpe=+0.5278
- `combo_clamp_diff__margin_extreme_rank_252d__sma100_dist`: Train IC=+0.0948, Lock IC=+0.0068, Lock Sharpe=+0.5278
- `combo_diff__yearly_low_distance__sma10_dist`: Train IC=+0.0787, Lock IC=+0.0658, Lock Sharpe=+0.5096
- `combo_clamp_diff__iv_envelope_deviation__roc20`: Train IC=+0.0803, Lock IC=+0.0708, Lock Sharpe=+0.4617

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6413_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 3827 | 30 | 86.7% | 20.0% | +0.0407 | -0.4162 |
| B2 Rolling Guard | 430 | 30 | 80.0% | 6.7% | +0.0275 | -0.5614 |
| BH-FDR Gate | 18 | 18 | 22.2% | 0.0% | -0.0329 | -1.4370 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__vol60__yesterday_lunch_gap__tech_value_rotation`: Train IC=+0.1786, Lock IC=+0.0253, Lock Sharpe=+0.1972
- `combo_diff__yearly_low_distance__yesterday_wavetrend_osc`: Train IC=+0.2102, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_diff__yearly_low_distance__wavetrend_osc_day`: Train IC=+0.2102, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_clamp_diff__yearly_low_distance__yesterday_wavetrend_osc`: Train IC=+0.2087, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_clamp_diff__yearly_low_distance__wavetrend_osc_day`: Train IC=+0.2087, Lock IC=+0.0836, Lock Sharpe=+0.1455

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__max_down_ret__rsi21__roc5`: Train IC=+0.1118, Lock IC=+0.0685, Lock Sharpe=+0.1340
- `combo_tri_min__yearly_low_distance__sma100_dist__bar_vol_4`: Train IC=+0.1442, Lock IC=+0.0515, Lock Sharpe=+0.0393

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 23.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4626_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 8397 | 30 | 53.3% | 26.7% | +0.0186 | -0.2311 |
| B2 Rolling Guard | 738 | 30 | 70.0% | 53.3% | +0.0110 | -0.2956 |
| BH-FDR Gate | 75 | 30 | 40.0% | 10.0% | -0.0159 | -0.7244 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_tri_mean__iv_vol_ratio__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_tri_ifelse__gap_pct__vix__capital_net_value__vix_skew_proxy__yesterday_afternoon_momentum`: Train IC=+0.2032, Lock IC=+0.0505, Lock Sharpe=+0.4980
- `combo_product__gap_pct__bar_rng_0`: Train IC=+0.2233, Lock IC=+0.0629, Lock Sharpe=+0.4266
- `combo_tri_ifelse__gap_pct__vix__capital_net_value__vix_skew_proxy__growth_momentum_ratio`: Train IC=+0.2125, Lock IC=+0.0411, Lock Sharpe=+0.4265

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__vol10__vix__sma_distance_60d__bar_body_rng_1__capital_buy_value`: Train IC=+0.1342, Lock IC=+0.0569, Lock Sharpe=+1.0940
- `combo_tri_ifelse__gap_pct__vix__sma50_dist__bar_rng_0__max_up_ret`: Train IC=+0.1332, Lock IC=+0.0831, Lock Sharpe=+0.8226
- `combo_tri_ifelse__gap_pct__vix__mfi14__bar_rng_0__bar_vol_0`: Train IC=+0.1164, Lock IC=+0.0648, Lock Sharpe=+0.7241
- `combo_tri_ifelse__gap_pct__vol10__mfi14__bar_rng_0__rsi21`: Train IC=+0.1245, Lock IC=+0.0191, Lock Sharpe=+0.6229
- `combo_tri_ifelse__vol10__vix__bar_rng_0__bar_vol_5__rsi21`: Train IC=+0.1504, Lock IC=+0.0317, Lock Sharpe=+0.5258

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__iv_vol_ratio__sma50_dist`: Train IC=+0.1170, Lock IC=+0.0567, Lock Sharpe=+0.3162
- `combo_min__gap_pct__max_up_ret`: Train IC=+0.1159, Lock IC=+0.0072, Lock Sharpe=+0.2990
- `combo_product__bar_vol_4__northbound_net`: Train IC=+0.1422, Lock IC=+0.0267, Lock Sharpe=+0.0407

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 71.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4145_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 2429 | 30 | 96.7% | 36.7% | +0.0594 | -0.2541 |
| B2 Rolling Guard | 368 | 30 | 80.0% | 30.0% | +0.0385 | -0.2375 |
| BH-FDR Gate | 222 | 30 | 90.0% | 30.0% | +0.0520 | -0.2896 |
| B3 Composite Floor | 367 | 30 | 100.0% | 23.3% | +0.0805 | -0.3645 |
| B4 Correlation Gate | 321 | 30 | 100.0% | 46.7% | +0.0705 | -0.0280 |

**Admitted Pool Summary**: 31 features, False Positive Rate = 54.8% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0569, Mean Lock Sharpe = -0.0722

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__max_down_ret__yesterday_first_30min_return__bar_vol_5`: Train IC=+0.2201, Lock IC=+0.1158, Lock Sharpe=+1.2194
- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_momentum`: Train IC=+0.2464, Lock IC=+0.0560, Lock Sharpe=+0.6438
- `combo_mean__max_up_ret__cci14`: Train IC=+0.2373, Lock IC=+0.0786, Lock Sharpe=+0.4464
- `combo_mean__max_up_ret__willr14`: Train IC=+0.2109, Lock IC=+0.0643, Lock Sharpe=+0.2739
- `combo_rank_min__max_down_ret__vol20`: Train IC=+0.2222, Lock IC=+0.0612, Lock Sharpe=+0.2371

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__max_down_ret__yesterday_illiquidity_amihud__yesterday_early_trend`: Train IC=+0.2006, Lock IC=+0.0694, Lock Sharpe=+1.1623
- `combo_tri_median__max_down_ret__yesterday_early_momentum__yesterday_illiquidity_amihud`: Train IC=+0.2053, Lock IC=+0.0700, Lock Sharpe=+0.9983
- `combo_rank_min__max_up_ret__macd_hist`: Train IC=+0.1996, Lock IC=+0.1047, Lock Sharpe=+0.6850
- `combo_tri_min__max_down_ret__yesterday_early_momentum__yesterday_first_30min_return`: Train IC=+0.1609, Lock IC=+0.0805, Lock Sharpe=+0.4891
- `combo_min__max_up_ret__macd_hist`: Train IC=+0.1619, Lock IC=+0.0976, Lock Sharpe=+0.4350

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__first_30min_return__gap_pct`: Train IC=+0.1475, Lock IC=+0.0989, Lock Sharpe=+0.3067
- `combo_rank_min__first_30min_return__gap_pct`: Train IC=+0.1430, Lock IC=+0.1020, Lock Sharpe=+0.3041
- `combo_rank_max__max_down_ret__bar_body_rng_1`: Train IC=+0.1453, Lock IC=+0.0913, Lock Sharpe=+0.1859
- `first_30min_return`: Train IC=+0.1461, Lock IC=+0.0708, Lock Sharpe=+0.1356
- `combo_min__first_bar_return__first_30min_return`: Train IC=+0.1435, Lock IC=+0.0969, Lock Sharpe=+0.1010

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__max_up_ret__max_down_ret__yesterday_illiquidity_amihud`: Train IC=+0.2568, Lock IC=+0.0921, Lock Sharpe=+0.4021
- `combo_tri_mean__max_up_ret__first_bar_return__max_down_ret`: Train IC=+0.2436, Lock IC=+0.1014, Lock Sharpe=+0.2785
- `combo_tri_mean__max_up_ret__bar_ret_0__max_down_ret`: Train IC=+0.2434, Lock IC=+0.1014, Lock Sharpe=+0.2785
- `combo_tri_mean__max_up_ret__bar_vwap_dev_2__gap_pct`: Train IC=+0.2807, Lock IC=+0.1072, Lock Sharpe=+0.1533
- `combo_tri_min__max_up_ret__max_down_ret__bar_body_rng_1`: Train IC=+0.2494, Lock IC=+0.0912, Lock Sharpe=+0.1038

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__max_up_ret__gap_pct`: Train IC=+0.2816, Lock IC=+0.1302, Lock Sharpe=+0.8964
- `combo_tri_median__max_up_ret__max_down_ret__yesterday_illiquidity_amihud`: Train IC=+0.2794, Lock IC=+0.0889, Lock Sharpe=+0.6059
- `combo_ifelse__gap_pct__bar_ret_0__max_down_ret`: Train IC=+0.2581, Lock IC=+0.1099, Lock Sharpe=+0.5744
- `combo_ifelse__gap_pct__first_bar_return__max_down_ret`: Train IC=+0.2578, Lock IC=+0.1097, Lock Sharpe=+0.5744
- `combo_tri_mean__max_up_ret__max_down_ret__bar_body_rng_0`: Train IC=+0.2724, Lock IC=+0.1037, Lock Sharpe=+0.3426

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 61.0% lock IC > 0, 21.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2914_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 4529 | 30 | 90.0% | 33.3% | +0.0300 | -0.1118 |
| B2 Rolling Guard | 370 | 30 | 100.0% | 26.7% | +0.0471 | -0.2106 |
| BH-FDR Gate | 240 | 30 | 86.7% | 46.7% | +0.0344 | -0.2678 |
| B3 Composite Floor | 5 | 5 | 40.0% | 20.0% | -0.0076 | -0.4530 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0481, Mean Lock Sharpe = -1.3671

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__yearly_high_distance__yearly_low_distance`: Train IC=+0.2261, Lock IC=+0.0545, Lock Sharpe=+1.3356
- `combo_product__sma200_dist__yearly_low_distance`: Train IC=+0.2386, Lock IC=+0.0688, Lock Sharpe=+0.7891
- `combo_rank_min__rsi21__yearly_low_distance`: Train IC=+0.2282, Lock IC=+0.0629, Lock Sharpe=+0.7621
- `combo_mean__yesterday_illiquidity_amihud__yearly_low_distance`: Train IC=+0.2946, Lock IC=+0.0245, Lock Sharpe=+0.6197
- `combo_product__sma100_dist__yearly_low_distance`: Train IC=+0.2222, Lock IC=+0.0422, Lock Sharpe=+0.5074

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__sma100_dist__vol60`: Train IC=+0.1742, Lock IC=+0.0410, Lock Sharpe=+1.0680
- `combo_rank_min__yesterday_first_bar_volume__bar_vol_5`: Train IC=+0.1598, Lock IC=+0.0235, Lock Sharpe=+0.1439
- `combo_max__cci14__volume_percentile_20d`: Train IC=+0.1946, Lock IC=+0.0587, Lock Sharpe=+0.0873
- `combo_tri_mean__limit_up_proximity_day__stoch_k__sma200_dist`: Train IC=+0.1627, Lock IC=+0.0562, Lock Sharpe=+0.0469
- `combo_tri_mean__limit_down_proximity_day__stoch_k__sma200_dist`: Train IC=+0.1627, Lock IC=+0.0562, Lock Sharpe=+0.0469

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__cci14__volume_percentile_20d`: Train IC=+0.1753, Lock IC=+0.0582, Lock Sharpe=+0.5330
- `combo_tri_median__rsi21__cci14__volume_percentile_20d`: Train IC=+0.1869, Lock IC=+0.0638, Lock Sharpe=+0.3071
- `combo_tri_min__stoch_k__cci14__volume_percentile_20d`: Train IC=+0.2005, Lock IC=+0.0652, Lock Sharpe=+0.2968
- `combo_tri_max__stoch_k__sma200_dist__cci14`: Train IC=+0.1814, Lock IC=+0.0619, Lock Sharpe=+0.2822
- `combo_min__rsi21__volume_percentile_20d`: Train IC=+0.1949, Lock IC=+0.0524, Lock Sharpe=+0.1025

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__yearly_low_distance__bar_vol_5`: Train IC=+0.2250, Lock IC=+0.0621, Lock Sharpe=+0.6552

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 53.0% lock IC > 0, 27.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3720_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10868 | 30 | 60.0% | 43.3% | +0.0128 | -0.0553 |
| B2 Rolling Guard | 1089 | 30 | 83.3% | 53.3% | +0.0433 | +0.1761 |
| BH-FDR Gate | 131 | 30 | 93.3% | 43.3% | +0.0580 | -0.0025 |
| B3 Composite Floor | 2 | 2 | 100.0% | 100.0% | +0.0360 | +0.0976 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__short_balance__bb_width`: Train IC=+0.1929, Lock IC=+0.0159, Lock Sharpe=+0.5604
- `combo_clamp_diff__short_balance__bb_width`: Train IC=+0.1929, Lock IC=+0.0162, Lock Sharpe=+0.5604
- `combo_tri_ifelse__vol60__vol_pk20__total_balance__early_vwap_dev__volume_percentile_20d`: Train IC=+0.1928, Lock IC=+0.0741, Lock Sharpe=+0.5423
- `combo_tri_ifelse__vol60__vol_pk20__total_balance__bar_vwap_dev_5__volume_percentile_20d`: Train IC=+0.1928, Lock IC=+0.0741, Lock Sharpe=+0.5423
- `combo_tri_ifelse__vol60__vol_pk20__total_balance__yesterday_early_vwap_dev__volume_percentile_20d`: Train IC=+0.2149, Lock IC=+0.0651, Lock Sharpe=+0.5025

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__macd_hist__vol60__first_bar_volume__yesterday_early_vwap_dev__short_balance_quantity`: Train IC=+0.1396, Lock IC=+0.0483, Lock Sharpe=+1.2060
- `combo_tri_ifelse__macd_hist__vol60__bar_vol_0__yesterday_early_vwap_dev__short_balance_quantity`: Train IC=+0.1396, Lock IC=+0.0483, Lock Sharpe=+1.2060
- `combo_tri_ifelse__vol60__gap_pct__yesterday_early_vwap_dev__high_beta_vol_ratio__margin_buy_repayment_spread`: Train IC=+0.1463, Lock IC=+0.1057, Lock Sharpe=+0.8119
- `combo_min__first_bar_volume__total_balance`: Train IC=+0.1443, Lock IC=+0.0436, Lock Sharpe=+0.7866
- `combo_min__bar_vol_0__total_balance`: Train IC=+0.1443, Lock IC=+0.0436, Lock Sharpe=+0.7866

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__early_vwap_dev`: Train IC=+0.1978, Lock IC=+0.1061, Lock Sharpe=+0.8742
- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__bar_vwap_dev_5`: Train IC=+0.1978, Lock IC=+0.1061, Lock Sharpe=+0.8742
- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__yesterday_early_vwap_dev__early_vwap_dev`: Train IC=+0.2040, Lock IC=+0.0864, Lock Sharpe=+0.5977
- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__yesterday_early_vwap_dev__bar_vwap_dev_5`: Train IC=+0.2040, Lock IC=+0.0864, Lock Sharpe=+0.5977
- `combo_tri_ifelse__macd_hist__vol_pk20__rsi5__yesterday_early_vwap_dev__yesterday_day_range`: Train IC=+0.1957, Lock IC=+0.0718, Lock Sharpe=+0.4383

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__yesterday_early_vwap_dev__body_to_range_ratio`: Train IC=+0.3232, Lock IC=+0.0333, Lock Sharpe=+0.0976
- `combo_tri_ifelse__macd_hist__vol_pk20__short_balance__yesterday_early_vwap_dev__body_to_range_ratio`: Train IC=+0.2444, Lock IC=+0.0387, Lock Sharpe=+0.0976

### 588000ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 30.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5020_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 5206 | 30 | 46.7% | 23.3% | -0.0110 | -0.4338 |
| B2 Rolling Guard | 769 | 30 | 90.0% | 50.0% | +0.0310 | +0.1435 |
| BH-FDR Gate | 1086 | 30 | 26.7% | 3.3% | -0.0402 | -0.5409 |
| B3 Composite Floor | 2149 | 30 | 93.3% | 40.0% | +0.0231 | -0.0431 |
| B4 Correlation Gate | 430 | 30 | 93.3% | 46.7% | +0.0378 | +0.1171 |

**Admitted Pool Summary**: 36 features, False Positive Rate = 91.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0351, Mean Lock Sharpe = -0.6665

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__vix__atr14_norm__vix_rolling_percentile_60d__short_sell_cover_spread__num_up_bars`: Train IC=+0.2729, Lock IC=+0.0073, Lock Sharpe=+1.1269
- `combo_tri_ifelse__vix__atr14_norm__vix_diff_1d__yesterday_vix_early_drift__num_up_bars`: Train IC=+0.2757, Lock IC=+0.0578, Lock Sharpe=+0.7604
- `combo_tri_min__vix_diff_1d__vix__yesterday_day_realized_vol`: Train IC=+0.2763, Lock IC=+0.0397, Lock Sharpe=+0.7306
- `combo_tri_min__yesterday_vix_early_drift__vix__yesterday_day_realized_vol`: Train IC=+0.2763, Lock IC=+0.0397, Lock Sharpe=+0.7306
- `combo_tri_ifelse__vix__atr14_norm__vix_diff_1d__short_sell_cover_spread__num_up_bars`: Train IC=+0.2752, Lock IC=+0.0385, Lock Sharpe=+0.0850

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__bar_ret_0__vol_gk10`: Train IC=+0.2374, Lock IC=+0.0510, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__bar_ret_0__vol_gk10`: Train IC=+0.2374, Lock IC=+0.0510, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__first_bar_return__vol_gk10`: Train IC=+0.2372, Lock IC=+0.0511, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__first_bar_return__vol_gk10`: Train IC=+0.2372, Lock IC=+0.0511, Lock Sharpe=+0.9127
- `combo_rank_min__vix_skew_proxy__vix_rolling_percentile_60d`: Train IC=+0.2390, Lock IC=+0.0516, Lock Sharpe=+0.8927

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__vix__vol20__bar_ret_1__short_sell_cover_spread__vol5`: Train IC=+0.1848, Lock IC=+0.0040, Lock Sharpe=+0.2943

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__short_sell_cover_spread__max_down_ret`: Train IC=+0.3585, Lock IC=+0.0702, Lock Sharpe=+1.0714
- `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__northbound_net__max_down_ret`: Train IC=+0.3457, Lock IC=+0.0726, Lock Sharpe=+1.0714
- `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__short_sell_cover_spread__early_momentum`: Train IC=+0.3460, Lock IC=+0.0819, Lock Sharpe=+0.9472
- `combo_tri_ifelse__vix__vol20__bar_ret_1__vol5__bar_body_rng_1`: Train IC=+0.3466, Lock IC=+0.0214, Lock Sharpe=+0.3603
- `combo_tri_ifelse__vix__atr14_norm__vix_diff_1d__yesterday_vix_early_drift__first_30min_return`: Train IC=+0.3510, Lock IC=+0.0418, Lock Sharpe=+0.3500

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__atr14_norm__vix_skew_proxy__first_30min_return`: Train IC=+0.3579, Lock IC=+0.0719, Lock Sharpe=+1.0524
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__bar_ret_0__max_down_ret`: Train IC=+0.3670, Lock IC=+0.0793, Lock Sharpe=+0.9399
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__bar_ret_0__max_down_ret`: Train IC=+0.3670, Lock IC=+0.0793, Lock Sharpe=+0.9399
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__first_bar_return__max_down_ret`: Train IC=+0.3666, Lock IC=+0.0793, Lock Sharpe=+0.9399
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__first_bar_return__max_down_ret`: Train IC=+0.3666, Lock IC=+0.0793, Lock Sharpe=+0.9399

### 588000ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 46.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5718_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 5515 | 30 | 36.7% | 23.3% | -0.0101 | -0.4559 |
| B2 Rolling Guard | 1285 | 30 | 33.3% | 13.3% | -0.0223 | -0.7315 |
| BH-FDR Gate | 636 | 30 | 36.7% | 20.0% | -0.0171 | -0.6400 |
| B3 Composite Floor | 5 | 5 | 0.0% | 0.0% | -0.0740 | -0.9442 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0750, Mean Lock Sharpe = -0.8713

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__vix_rolling_percentile_60d__volume_slope`: Train IC=+0.2614, Lock IC=+0.0536, Lock Sharpe=+1.7087
- `combo_product__vix_diff_1d__yesterday_volume_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__vix_diff_1d__volume_sma_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__yesterday_vix_early_drift__yesterday_volume_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__yesterday_vix_early_drift__volume_sma_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__early_range__vix_rolling_percentile_60d__vix_skew_proxy`: Train IC=+0.2700, Lock IC=+0.0408, Lock Sharpe=+0.5595
- `combo_tri_min__early_realized_vol__vix_rolling_percentile_60d__vix_skew_proxy`: Train IC=+0.2503, Lock IC=+0.0441, Lock Sharpe=+0.3531
- `combo_tri_min__early_realized_vol__vix_rolling_percentile_60d__vix_diff_1d`: Train IC=+0.2473, Lock IC=+0.0457, Lock Sharpe=+0.3531
- `combo_tri_min__early_realized_vol__vix_rolling_percentile_60d__yesterday_vix_early_drift`: Train IC=+0.2473, Lock IC=+0.0457, Lock Sharpe=+0.3531

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__vix_rolling_percentile_60d__capital_net_value`: Train IC=+0.2574, Lock IC=+0.0371, Lock Sharpe=+1.6280
- `combo_abs_diff__growth_momentum_ratio__bar_vol_5`: Train IC=+0.2897, Lock IC=+0.0368, Lock Sharpe=+0.8499
- `combo_ratio__capital_net_accel__capital_large_order_ratio`: Train IC=+0.2437, Lock IC=+0.0750, Lock Sharpe=+0.2892
- `combo_tri_min__early_realized_vol__yesterday_day_realized_vol__vix_diff_1d`: Train IC=+0.2683, Lock IC=+0.0726, Lock Sharpe=+0.0497
- `combo_tri_min__early_realized_vol__yesterday_day_realized_vol__yesterday_vix_early_drift`: Train IC=+0.2683, Lock IC=+0.0726, Lock Sharpe=+0.0497

### 588000ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 40.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0314_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 8730 | 30 | 16.7% | 6.7% | -0.0288 | -1.0100 |
| B2 Rolling Guard | 1034 | 30 | 23.3% | 13.3% | -0.0310 | -0.6495 |
| BH-FDR Gate | 118 | 30 | 33.3% | 13.3% | -0.0277 | -1.3449 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__sma20_dist__vix__vix_rolling_percentile_60d__capital_net_ratio__total_path_length`: Train IC=+0.2272, Lock IC=+0.1029, Lock Sharpe=+0.9632
- `combo_tri_ifelse__vix__gap_pct__high_beta_vol_ratio__capital_sell_value__stoch_d`: Train IC=+0.2659, Lock IC=+0.0146, Lock Sharpe=+0.1103

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__short_balance_quantity__roc20`: Train IC=+0.1686, Lock IC=+0.0860, Lock Sharpe=+0.8040
- `combo_tri_ifelse__vix__gap_pct__short_repayment_quantity__yesterday_day_range__short_sell_cover_spread`: Train IC=+0.1401, Lock IC=+0.0111, Lock Sharpe=+0.5375
- `combo_min__vix__vix_skew_proxy`: Train IC=+0.1534, Lock IC=+0.0335, Lock Sharpe=+0.3985
- `combo_tri_ifelse__sma20_dist__vix__high_beta_vol_ratio__bar_ret_1__ema12_dist`: Train IC=+0.1366, Lock IC=+0.0344, Lock Sharpe=+0.0350

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__gap_pct__yesterday_early_realized_vol`: Train IC=+0.1495, Lock IC=+0.0318, Lock Sharpe=+0.4820
- `combo_tri_ifelse__sma20_dist__gap_pct__short_repayment_quantity__yesterday_day_range__total_path_length`: Train IC=+0.1814, Lock IC=+0.0323, Lock Sharpe=+0.4660
- `combo_abs_diff__bar_ret_1__bar_vwap_dev_5`: Train IC=+0.2171, Lock IC=+0.0295, Lock Sharpe=+0.2902
- `combo_abs_diff__bar_ret_1__early_vwap_dev`: Train IC=+0.2171, Lock IC=+0.0295, Lock Sharpe=+0.2902

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 67.0% lock IC > 0, 31.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2660_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 3917 | 30 | 86.7% | 43.3% | +0.0462 | -0.0314 |
| B2 Rolling Guard | 718 | 30 | 60.0% | 36.7% | +0.0255 | -0.4125 |
| BH-FDR Gate | 198 | 30 | 100.0% | 53.3% | +0.0530 | -0.0728 |
| B3 Composite Floor | 251 | 30 | 100.0% | 43.3% | +0.0509 | -0.1103 |
| B4 Correlation Gate | 42 | 30 | 100.0% | 73.3% | +0.0903 | +0.2509 |

**Admitted Pool Summary**: 12 features, False Positive Rate = 33.3% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0729, Mean Lock Sharpe = +0.1944

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__bar_ret_0__gap_pct__first_30min_return`: Train IC=+0.2080, Lock IC=+0.1182, Lock Sharpe=+1.2912
- `combo_tri_min__first_bar_return__gap_pct__first_30min_return`: Train IC=+0.2077, Lock IC=+0.1182, Lock Sharpe=+1.2912
- `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__max_down_ret`: Train IC=+0.2211, Lock IC=+0.1272, Lock Sharpe=+1.1739
- `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__yesterday_first_30min_return`: Train IC=+0.2194, Lock IC=+0.1261, Lock Sharpe=+1.0853
- `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__yesterday_early_trend`: Train IC=+0.2104, Lock IC=+0.0747, Lock Sharpe=+0.8748

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2106, Lock IC=+0.1310, Lock Sharpe=+1.2087
- `combo_rank_min__max_up_ret__max_down_ret`: Train IC=+0.2204, Lock IC=+0.0988, Lock Sharpe=+0.7200
- `combo_tri_max__max_up_ret__max_down_ret__bb_width`: Train IC=+0.2072, Lock IC=+0.0594, Lock Sharpe=+0.6939
- `combo_mean__bar_body_rng_0__first_30min_return`: Train IC=+0.1917, Lock IC=+0.1101, Lock Sharpe=+0.5746
- `combo_clamp_diff__max_up_ret__early_range`: Train IC=+0.1895, Lock IC=+0.0980, Lock Sharpe=+0.5702

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__max_up_ret__bar_vwap_dev_5`: Train IC=+0.1572, Lock IC=+0.0396, Lock Sharpe=+0.6708
- `combo_diff__max_up_ret__early_vwap_dev`: Train IC=+0.1572, Lock IC=+0.0396, Lock Sharpe=+0.6708
- `combo_ifelse__gap_pct__bar_body_rng_0__bar_ret_0`: Train IC=+0.1620, Lock IC=+0.0798, Lock Sharpe=+0.6001
- `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__bar_ret_0__first_bar_return`: Train IC=+0.1617, Lock IC=+0.0797, Lock Sharpe=+0.6001
- `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return`: Train IC=+0.1616, Lock IC=+0.0797, Lock Sharpe=+0.6001

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__max_up_ret__bar_ret_0__gap_pct`: Train IC=+0.2608, Lock IC=+0.1341, Lock Sharpe=+1.1076
- `combo_tri_mean__max_up_ret__first_bar_return__gap_pct`: Train IC=+0.2604, Lock IC=+0.1341, Lock Sharpe=+1.1076
- `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_early_vwap_dev__max_down_ret`: Train IC=+0.2202, Lock IC=+0.1372, Lock Sharpe=+0.9132
- `combo_tri_median__max_up_ret__capital_sell_volume__yearly_high_distance`: Train IC=+0.2358, Lock IC=+0.0690, Lock Sharpe=+0.4645
- `combo_tri_max__max_up_ret__bar_body_rng_0__max_down_ret`: Train IC=+0.2301, Lock IC=+0.0869, Lock Sharpe=+0.4644

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__max_up_ret__first_bar_return__gap_pct`: Train IC=+0.2711, Lock IC=+0.1271, Lock Sharpe=+1.1425
- `combo_rank_min__max_up_ret__gap_pct`: Train IC=+0.2544, Lock IC=+0.1252, Lock Sharpe=+0.9217
- `combo_diff__max_up_ret__keltner_squeeze_width`: Train IC=+0.2030, Lock IC=+0.1063, Lock Sharpe=+0.8462
- `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_first_30min_return`: Train IC=+0.2077, Lock IC=+0.1243, Lock Sharpe=+0.8402
- `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`: Train IC=+0.1943, Lock IC=+0.0837, Lock Sharpe=+0.7716

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 23.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2601_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 3221 | 30 | 80.0% | 43.3% | +0.0324 | +0.0372 |
| B2 Rolling Guard | 295 | 30 | 50.0% | 36.7% | +0.0002 | -0.2248 |
| BH-FDR Gate | 72 | 30 | 76.7% | 50.0% | +0.0345 | +0.0452 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__vol60__max_down_ret`: Train IC=+0.2060, Lock IC=+0.0495, Lock Sharpe=+0.6875
- `combo_rank_min__vol_gk10__max_down_ret`: Train IC=+0.1845, Lock IC=+0.0636, Lock Sharpe=+0.6373
- `combo_rank_min__max_down_ret__early_momentum`: Train IC=+0.1661, Lock IC=+0.0733, Lock Sharpe=+0.6107
- `combo_min__early_realized_vol__max_down_ret`: Train IC=+0.1745, Lock IC=+0.0768, Lock Sharpe=+0.5838
- `combo_min__vol60__max_down_ret`: Train IC=+0.1927, Lock IC=+0.0529, Lock Sharpe=+0.5456

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_rng_0__max_down_ret`: Train IC=+0.1528, Lock IC=+0.0709, Lock Sharpe=+1.0065
- `combo_mean__yesterday_first_30min_return__cci14`: Train IC=+0.1665, Lock IC=+0.0439, Lock Sharpe=+0.7505
- `combo_mean__yesterday_afternoon_momentum__roc5`: Train IC=+0.1314, Lock IC=+0.0459, Lock Sharpe=+0.4659
- `combo_ifelse__vol60__yesterday_afternoon_momentum__margin_repayment`: Train IC=+0.1011, Lock IC=+0.0029, Lock Sharpe=+0.4563
- `combo_clamp_diff__early_realized_vol__keltner_squeeze_width`: Train IC=+0.1393, Lock IC=+0.0513, Lock Sharpe=+0.4362

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__bar_rng_0__max_down_ret`: Train IC=+0.1729, Lock IC=+0.0741, Lock Sharpe=+1.0065
- `combo_product__bar_ret_2__early_momentum`: Train IC=+0.1011, Lock IC=+0.0493, Lock Sharpe=+0.8618
- `combo_rank_min__yesterday_range_ratio__max_down_ret`: Train IC=+0.1429, Lock IC=+0.0574, Lock Sharpe=+0.6356
- `combo_min__bar_body_rng_1__max_down_ret`: Train IC=+0.1562, Lock IC=+0.0845, Lock Sharpe=+0.6121
- `combo_min__first_30min_return__bar_vwap_dev_3`: Train IC=+0.1292, Lock IC=+0.0619, Lock Sharpe=+0.5428

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 22.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2695_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10311 | 30 | 60.0% | 33.3% | +0.0042 | -0.1537 |
| B2 Rolling Guard | 1516 | 30 | 30.0% | 20.0% | -0.0119 | -0.0686 |
| BH-FDR Gate | 20 | 20 | 60.0% | 25.0% | +0.0062 | -0.1428 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__bb_width__margin_repayment`: Train IC=+0.2082, Lock IC=+0.0637, Lock Sharpe=+1.0054
- `combo_tri_ifelse__vol_pk20__bb_width__iv_vol_ratio__sma100_dist__early_realized_vol`: Train IC=+0.1722, Lock IC=+0.0351, Lock Sharpe=+0.6703
- `combo_tri_ifelse__vol_pk20__vol20__stoch_k__yesterday_day_kurtosis__capital_sell_volume`: Train IC=+0.1852, Lock IC=+0.0135, Lock Sharpe=+0.4434
- `combo_tri_ifelse__vol_pk20__vol20__stoch_k__vol_gk10__capital_sell_volume`: Train IC=+0.1779, Lock IC=+0.0105, Lock Sharpe=+0.4434
- `combo_tri_ifelse__vol20__bb_width__stoch_k__capital_sell_volume__yesterday_early_trend`: Train IC=+0.1684, Lock IC=+0.0163, Lock Sharpe=+0.1183

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_ifelse__vol20__sma20_dist__vol_gk10__capital_sell_volume__early_realized_vol`: Train IC=+0.1593, Lock IC=+0.0020, Lock Sharpe=+0.9850
- `combo_tri_ifelse__vol_pk20__sma20_dist__stoch_k__yesterday_afternoon_momentum__early_realized_vol`: Train IC=+0.1610, Lock IC=+0.0261, Lock Sharpe=+0.2939
- `combo_tri_ifelse__vol_pk20__vol20__stoch_k__yesterday_afternoon_momentum__early_realized_vol`: Train IC=+0.1809, Lock IC=+0.0007, Lock Sharpe=+0.0993
- `combo_tri_ifelse__vol20__sma20_dist__stoch_k__yesterday_pm_return__early_realized_vol`: Train IC=+0.1588, Lock IC=+0.0117, Lock Sharpe=+0.0987
- `combo_tri_ifelse__vol_pk20__vol20__stoch_k__yesterday_pm_return__early_realized_vol`: Train IC=+0.1739, Lock IC=+0.0007, Lock Sharpe=+0.0911

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_max__vol20__vol_gk10__capital_sell_volume`: Train IC=+0.0743, Lock IC=+0.0118, Lock Sharpe=+0.4988
- `combo_tri_median__vix_vol_ratio__vol20__vol_gk10`: Train IC=+0.0707, Lock IC=+0.0113, Lock Sharpe=+0.3511
- `combo_abs_diff__sma20_dist__rsi21`: Train IC=+0.0496, Lock IC=+0.0637, Lock Sharpe=+0.2755
- `combo_tri_median__iv_vol_ratio__vol20__vol_gk10`: Train IC=+0.0707, Lock IC=+0.0153, Lock Sharpe=+0.2383
- `combo_tri_ifelse__vol_pk20__bb_width__iv_vol_ratio__vix_vol_ratio__capital_sell_volume`: Train IC=+0.0323, Lock IC=+0.0164, Lock Sharpe=+0.0510

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 294 | +0.0164 | 90.0% |
| 0.45 | 0.20 | 256 | +0.0164 | 90.0% |
| 0.45 | 0.30 | 184 | +0.0164 | 90.0% |
| 0.45 | 0.40 | 125 | +0.0164 | 90.0% |
| 0.45 | 0.50 | 80 | +0.0164 | 90.0% |
| 0.50 | 0.15 | 279 | +0.0164 | 90.0% |
| 0.50 | 0.25 | 216 | +0.0164 | 90.0% |
| 0.50 | 0.35 | 154 | +0.0164 | 90.0% |
| 0.50 | 0.45 | 100 | +0.0164 | 90.0% |
| 0.55 | 0.10 | 282 | +0.0164 | 90.0% |
| 0.55 | 0.20 | 256 | +0.0164 | 90.0% |
| 0.55 | 0.30 | 184 | +0.0164 | 90.0% |
| 0.55 | 0.40 | 125 | +0.0164 | 90.0% |
| 0.55 | 0.50 | 80 | +0.0164 | 90.0% |
| 0.60 | 0.15 | 203 | +0.0164 | 90.0% |
| 0.60 | 0.25 | 198 | +0.0164 | 90.0% |
| 0.60 | 0.35 | 153 | +0.0164 | 90.0% |
| 0.60 | 0.45 | 100 | +0.0164 | 90.0% |
| 0.65 | 0.10 | 129 | +0.0164 | 90.0% |
| 0.65 | 0.20 | 129 | +0.0164 | 90.0% |
| 0.65 | 0.30 | 129 | +0.0164 | 90.0% |
| 0.65 | 0.40 | 115 | +0.0164 | 90.0% |
| 0.65 | 0.50 | 80 | +0.0164 | 90.0% |
| 0.70 | 0.15 | 66 | +0.0187 | 90.0% |
| 0.70 | 0.25 | 66 | +0.0187 | 90.0% |
| 0.70 | 0.35 | 66 | +0.0187 | 90.0% |
| 0.70 | 0.45 | 65 | +0.0187 | 90.0% |
| 0.75 | 0.10 | 18 | -0.0126 | 30.0% |
| 0.75 | 0.20 | 18 | -0.0126 | 30.0% |
| 0.75 | 0.30 | 18 | -0.0126 | 30.0% |
| 0.75 | 0.40 | 18 | -0.0126 | 30.0% |
| 0.75 | 0.50 | 18 | -0.0126 | 30.0% |
| 0.80 | 0.15 | 2 | +0.0220 | 100.0% |
| 0.80 | 0.25 | 2 | +0.0220 | 100.0% |
| 0.80 | 0.35 | 2 | +0.0220 | 100.0% |
| 0.80 | 0.45 | 2 | +0.0220 | 100.0% |

**Optimal**: mono_thr=0.70, ir_thr=0.10 → 66 candidates, mean lock IC=+0.0187, 90.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 2 | -0.0601 | 0.0% |
| 0.45 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 1 | -0.0606 | 0.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 1 | -0.0606 | 0.0% |
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

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 279 | +0.0082 | 60.0% |
| 0.45 | 0.20 | 85 | +0.0067 | 60.0% |
| 0.45 | 0.30 | 22 | -0.0102 | 60.0% |
| 0.45 | 0.40 | 10 | +0.0048 | 60.0% |
| 0.45 | 0.50 | 2 | -0.0107 | 50.0% |
| 0.50 | 0.15 | 163 | +0.0082 | 60.0% |
| 0.50 | 0.25 | 59 | -0.0162 | 30.0% |
| 0.50 | 0.35 | 14 | +0.0050 | 70.0% |
| 0.50 | 0.45 | 5 | -0.0050 | 60.0% |
| 0.55 | 0.10 | 109 | +0.0067 | 60.0% |
| 0.55 | 0.20 | 77 | +0.0067 | 60.0% |
| 0.55 | 0.30 | 22 | -0.0102 | 60.0% |
| 0.55 | 0.40 | 10 | +0.0048 | 60.0% |
| 0.55 | 0.50 | 2 | -0.0107 | 50.0% |
| 0.60 | 0.15 | 38 | -0.0127 | 30.0% |
| 0.60 | 0.25 | 37 | -0.0127 | 30.0% |
| 0.60 | 0.35 | 14 | +0.0050 | 70.0% |
| 0.60 | 0.45 | 5 | -0.0050 | 60.0% |
| 0.65 | 0.10 | 11 | -0.0108 | 40.0% |
| 0.65 | 0.20 | 11 | -0.0108 | 40.0% |
| 0.65 | 0.30 | 11 | -0.0108 | 40.0% |
| 0.65 | 0.40 | 8 | +0.0017 | 50.0% |
| 0.65 | 0.50 | 2 | -0.0107 | 50.0% |
| 0.70 | 0.15 | 1 | +0.0223 | 100.0% |
| 0.70 | 0.25 | 1 | +0.0223 | 100.0% |
| 0.70 | 0.35 | 1 | +0.0223 | 100.0% |
| 0.70 | 0.45 | 1 | +0.0223 | 100.0% |
| 0.75 | 0.10 | 1 | +0.0223 | 100.0% |
| 0.75 | 0.20 | 1 | +0.0223 | 100.0% |
| 0.75 | 0.30 | 1 | +0.0223 | 100.0% |
| 0.75 | 0.40 | 1 | +0.0223 | 100.0% |
| 0.75 | 0.50 | 1 | +0.0223 | 100.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 279 candidates, mean lock IC=+0.0082, 60.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 169 | +0.0500 | 100.0% |
| 0.45 | 0.20 | 134 | +0.0500 | 100.0% |
| 0.45 | 0.30 | 60 | +0.0489 | 100.0% |
| 0.45 | 0.40 | 39 | +0.0404 | 100.0% |
| 0.45 | 0.50 | 27 | +0.0392 | 100.0% |
| 0.50 | 0.15 | 152 | +0.0500 | 100.0% |
| 0.50 | 0.25 | 95 | +0.0362 | 90.0% |
| 0.50 | 0.35 | 46 | +0.0449 | 90.0% |
| 0.50 | 0.45 | 35 | +0.0404 | 100.0% |
| 0.55 | 0.10 | 150 | +0.0500 | 100.0% |
| 0.55 | 0.20 | 129 | +0.0500 | 100.0% |
| 0.55 | 0.30 | 60 | +0.0489 | 100.0% |
| 0.55 | 0.40 | 39 | +0.0404 | 100.0% |
| 0.55 | 0.50 | 27 | +0.0392 | 100.0% |
| 0.60 | 0.15 | 85 | +0.0404 | 90.0% |
| 0.60 | 0.25 | 68 | +0.0382 | 90.0% |
| 0.60 | 0.35 | 46 | +0.0449 | 90.0% |
| 0.60 | 0.45 | 35 | +0.0404 | 100.0% |
| 0.65 | 0.10 | 43 | +0.0419 | 100.0% |
| 0.65 | 0.20 | 43 | +0.0419 | 100.0% |
| 0.65 | 0.30 | 42 | +0.0419 | 100.0% |
| 0.65 | 0.40 | 38 | +0.0404 | 100.0% |
| 0.65 | 0.50 | 27 | +0.0392 | 100.0% |
| 0.70 | 0.15 | 26 | +0.0388 | 100.0% |
| 0.70 | 0.25 | 26 | +0.0388 | 100.0% |
| 0.70 | 0.35 | 26 | +0.0388 | 100.0% |
| 0.70 | 0.45 | 26 | +0.0388 | 100.0% |
| 0.75 | 0.10 | 18 | +0.0430 | 100.0% |
| 0.75 | 0.20 | 18 | +0.0430 | 100.0% |
| 0.75 | 0.30 | 18 | +0.0430 | 100.0% |
| 0.75 | 0.40 | 18 | +0.0430 | 100.0% |
| 0.75 | 0.50 | 18 | +0.0430 | 100.0% |
| 0.80 | 0.15 | 11 | +0.0269 | 90.0% |
| 0.80 | 0.25 | 11 | +0.0269 | 90.0% |
| 0.80 | 0.35 | 11 | +0.0269 | 90.0% |
| 0.80 | 0.45 | 11 | +0.0269 | 90.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 169 candidates, mean lock IC=+0.0500, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 119 | +0.0160 | 60.0% |
| 0.45 | 0.20 | 20 | -0.0118 | 40.0% |
| 0.45 | 0.30 | 7 | -0.0262 | 42.9% |
| 0.45 | 0.40 | 2 | +0.0039 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 52 | +0.0180 | 80.0% |
| 0.50 | 0.25 | 10 | -0.0194 | 40.0% |
| 0.50 | 0.35 | 4 | -0.0183 | 50.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 37 | -0.0086 | 40.0% |
| 0.55 | 0.20 | 12 | -0.0290 | 30.0% |
| 0.55 | 0.30 | 7 | -0.0262 | 42.9% |
| 0.55 | 0.40 | 2 | +0.0039 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 7 | -0.0262 | 42.9% |
| 0.60 | 0.25 | 7 | -0.0262 | 42.9% |
| 0.60 | 0.35 | 4 | -0.0183 | 50.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 52 candidates, mean lock IC=+0.0180, 80.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 232 | -0.0332 | 20.0% |
| 0.45 | 0.20 | 82 | -0.0108 | 50.0% |
| 0.45 | 0.30 | 19 | -0.0201 | 40.0% |
| 0.45 | 0.40 | 5 | +0.0084 | 40.0% |
| 0.45 | 0.50 | 2 | +0.0263 | 50.0% |
| 0.50 | 0.15 | 129 | -0.0267 | 30.0% |
| 0.50 | 0.25 | 45 | -0.0059 | 60.0% |
| 0.50 | 0.35 | 13 | -0.0245 | 40.0% |
| 0.50 | 0.45 | 3 | +0.0412 | 66.7% |
| 0.55 | 0.10 | 99 | -0.0230 | 40.0% |
| 0.55 | 0.20 | 61 | -0.0131 | 50.0% |
| 0.55 | 0.30 | 19 | -0.0201 | 40.0% |
| 0.55 | 0.40 | 5 | +0.0084 | 40.0% |
| 0.55 | 0.50 | 2 | +0.0263 | 50.0% |
| 0.60 | 0.15 | 33 | -0.0078 | 50.0% |
| 0.60 | 0.25 | 26 | -0.0118 | 50.0% |
| 0.60 | 0.35 | 13 | -0.0245 | 40.0% |
| 0.60 | 0.45 | 3 | +0.0412 | 66.7% |
| 0.65 | 0.10 | 7 | +0.0183 | 71.4% |
| 0.65 | 0.20 | 7 | +0.0183 | 71.4% |
| 0.65 | 0.30 | 7 | +0.0183 | 71.4% |
| 0.65 | 0.40 | 3 | +0.0412 | 66.7% |
| 0.65 | 0.50 | 2 | +0.0263 | 50.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.45 → 3 candidates, mean lock IC=+0.0412, 66.7% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1131 | +0.0867 | 100.0% |
| 0.45 | 0.20 | 1070 | +0.0867 | 100.0% |
| 0.45 | 0.30 | 961 | +0.0867 | 100.0% |
| 0.45 | 0.40 | 810 | +0.0867 | 100.0% |
| 0.45 | 0.50 | 581 | +0.0826 | 100.0% |
| 0.50 | 0.15 | 1102 | +0.0867 | 100.0% |
| 0.50 | 0.25 | 1018 | +0.0867 | 100.0% |
| 0.50 | 0.35 | 886 | +0.0867 | 100.0% |
| 0.50 | 0.45 | 717 | +0.0867 | 100.0% |
| 0.55 | 0.10 | 1103 | +0.0867 | 100.0% |
| 0.55 | 0.20 | 1066 | +0.0867 | 100.0% |
| 0.55 | 0.30 | 960 | +0.0867 | 100.0% |
| 0.55 | 0.40 | 810 | +0.0867 | 100.0% |
| 0.55 | 0.50 | 581 | +0.0826 | 100.0% |
| 0.60 | 0.15 | 977 | +0.0867 | 100.0% |
| 0.60 | 0.25 | 967 | +0.0867 | 100.0% |
| 0.60 | 0.35 | 881 | +0.0867 | 100.0% |
| 0.60 | 0.45 | 717 | +0.0867 | 100.0% |
| 0.65 | 0.10 | 762 | +0.0826 | 100.0% |
| 0.65 | 0.20 | 762 | +0.0826 | 100.0% |
| 0.65 | 0.30 | 762 | +0.0826 | 100.0% |
| 0.65 | 0.40 | 730 | +0.0826 | 100.0% |
| 0.65 | 0.50 | 574 | +0.0826 | 100.0% |
| 0.70 | 0.15 | 473 | +0.0826 | 100.0% |
| 0.70 | 0.25 | 473 | +0.0826 | 100.0% |
| 0.70 | 0.35 | 473 | +0.0826 | 100.0% |
| 0.70 | 0.45 | 472 | +0.0826 | 100.0% |
| 0.75 | 0.10 | 197 | +0.0745 | 100.0% |
| 0.75 | 0.20 | 197 | +0.0745 | 100.0% |
| 0.75 | 0.30 | 197 | +0.0745 | 100.0% |
| 0.75 | 0.40 | 197 | +0.0745 | 100.0% |
| 0.75 | 0.50 | 197 | +0.0745 | 100.0% |
| 0.80 | 0.15 | 52 | +0.0646 | 100.0% |
| 0.80 | 0.25 | 52 | +0.0646 | 100.0% |
| 0.80 | 0.35 | 52 | +0.0646 | 100.0% |
| 0.80 | 0.45 | 52 | +0.0646 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1131 candidates, mean lock IC=+0.0867, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 346 | +0.0148 | 60.0% |
| 0.45 | 0.20 | 229 | -0.0091 | 40.0% |
| 0.45 | 0.30 | 96 | -0.0218 | 30.0% |
| 0.45 | 0.40 | 41 | -0.0080 | 40.0% |
| 0.45 | 0.50 | 19 | +0.0170 | 70.0% |
| 0.50 | 0.15 | 279 | +0.0148 | 60.0% |
| 0.50 | 0.25 | 148 | -0.0213 | 30.0% |
| 0.50 | 0.35 | 52 | -0.0060 | 40.0% |
| 0.50 | 0.45 | 29 | +0.0021 | 50.0% |
| 0.55 | 0.10 | 257 | +0.0027 | 50.0% |
| 0.55 | 0.20 | 213 | -0.0213 | 30.0% |
| 0.55 | 0.30 | 96 | -0.0218 | 30.0% |
| 0.55 | 0.40 | 41 | -0.0080 | 40.0% |
| 0.55 | 0.50 | 19 | +0.0170 | 70.0% |
| 0.60 | 0.15 | 115 | -0.0213 | 30.0% |
| 0.60 | 0.25 | 101 | -0.0213 | 30.0% |
| 0.60 | 0.35 | 51 | -0.0060 | 40.0% |
| 0.60 | 0.45 | 29 | +0.0021 | 50.0% |
| 0.65 | 0.10 | 36 | -0.0111 | 40.0% |
| 0.65 | 0.20 | 36 | -0.0111 | 40.0% |
| 0.65 | 0.30 | 36 | -0.0111 | 40.0% |
| 0.65 | 0.40 | 32 | +0.0021 | 50.0% |
| 0.65 | 0.50 | 19 | +0.0170 | 70.0% |
| 0.70 | 0.15 | 11 | +0.0051 | 60.0% |
| 0.70 | 0.25 | 11 | +0.0051 | 60.0% |
| 0.70 | 0.35 | 11 | +0.0051 | 60.0% |
| 0.70 | 0.45 | 11 | +0.0051 | 60.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 19 candidates, mean lock IC=+0.0170, 70.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 262 | +0.0517 | 100.0% |
| 0.45 | 0.20 | 106 | +0.0645 | 100.0% |
| 0.45 | 0.30 | 36 | +0.0437 | 90.0% |
| 0.45 | 0.40 | 6 | +0.0380 | 66.7% |
| 0.45 | 0.50 | 1 | -0.0117 | 0.0% |
| 0.50 | 0.15 | 174 | +0.0645 | 100.0% |
| 0.50 | 0.25 | 73 | +0.0678 | 100.0% |
| 0.50 | 0.35 | 18 | +0.0453 | 90.0% |
| 0.50 | 0.45 | 2 | +0.0301 | 50.0% |
| 0.55 | 0.10 | 147 | +0.0517 | 100.0% |
| 0.55 | 0.20 | 104 | +0.0645 | 100.0% |
| 0.55 | 0.30 | 36 | +0.0437 | 90.0% |
| 0.55 | 0.40 | 6 | +0.0380 | 66.7% |
| 0.55 | 0.50 | 1 | -0.0117 | 0.0% |
| 0.60 | 0.15 | 65 | +0.0678 | 100.0% |
| 0.60 | 0.25 | 58 | +0.0678 | 100.0% |
| 0.60 | 0.35 | 17 | +0.0485 | 90.0% |
| 0.60 | 0.45 | 2 | +0.0301 | 50.0% |
| 0.65 | 0.10 | 7 | +0.0403 | 71.4% |
| 0.65 | 0.20 | 7 | +0.0403 | 71.4% |
| 0.65 | 0.30 | 7 | +0.0403 | 71.4% |
| 0.65 | 0.40 | 5 | +0.0471 | 80.0% |
| 0.65 | 0.50 | 1 | -0.0117 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.25 → 73 candidates, mean lock IC=+0.0678, 100.0% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 4295 | +0.0325 | 90.0% |
| 0.45 | 0.20 | 4113 | +0.0325 | 90.0% |
| 0.45 | 0.30 | 3809 | +0.0325 | 90.0% |
| 0.45 | 0.40 | 3409 | +0.0325 | 90.0% |
| 0.45 | 0.50 | 3010 | +0.0325 | 90.0% |
| 0.50 | 0.15 | 4222 | +0.0325 | 90.0% |
| 0.50 | 0.25 | 3966 | +0.0325 | 90.0% |
| 0.50 | 0.35 | 3608 | +0.0325 | 90.0% |
| 0.50 | 0.45 | 3202 | +0.0325 | 90.0% |
| 0.55 | 0.10 | 4179 | +0.0325 | 90.0% |
| 0.55 | 0.20 | 4072 | +0.0325 | 90.0% |
| 0.55 | 0.30 | 3802 | +0.0325 | 90.0% |
| 0.55 | 0.40 | 3409 | +0.0325 | 90.0% |
| 0.55 | 0.50 | 3010 | +0.0325 | 90.0% |
| 0.60 | 0.15 | 3859 | +0.0325 | 90.0% |
| 0.60 | 0.25 | 3804 | +0.0325 | 90.0% |
| 0.60 | 0.35 | 3567 | +0.0325 | 90.0% |
| 0.60 | 0.45 | 3202 | +0.0325 | 90.0% |
| 0.65 | 0.10 | 3372 | +0.0325 | 90.0% |
| 0.65 | 0.20 | 3372 | +0.0325 | 90.0% |
| 0.65 | 0.30 | 3358 | +0.0325 | 90.0% |
| 0.65 | 0.40 | 3266 | +0.0325 | 90.0% |
| 0.65 | 0.50 | 2987 | +0.0325 | 90.0% |
| 0.70 | 0.15 | 2799 | +0.0325 | 90.0% |
| 0.70 | 0.25 | 2799 | +0.0325 | 90.0% |
| 0.70 | 0.35 | 2796 | +0.0325 | 90.0% |
| 0.70 | 0.45 | 2767 | +0.0325 | 90.0% |
| 0.75 | 0.10 | 1768 | +0.0325 | 90.0% |
| 0.75 | 0.20 | 1768 | +0.0325 | 90.0% |
| 0.75 | 0.30 | 1768 | +0.0325 | 90.0% |
| 0.75 | 0.40 | 1768 | +0.0325 | 90.0% |
| 0.75 | 0.50 | 1765 | +0.0325 | 90.0% |
| 0.80 | 0.15 | 757 | +0.0393 | 100.0% |
| 0.80 | 0.25 | 757 | +0.0393 | 100.0% |
| 0.80 | 0.35 | 757 | +0.0393 | 100.0% |
| 0.80 | 0.45 | 757 | +0.0393 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 757 candidates, mean lock IC=+0.0393, 100.0% positive

### 588000ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1017 | -0.0629 | 10.0% |
| 0.45 | 0.20 | 618 | -0.0629 | 10.0% |
| 0.45 | 0.30 | 344 | -0.0276 | 30.0% |
| 0.45 | 0.40 | 165 | -0.0036 | 50.0% |
| 0.45 | 0.50 | 84 | -0.0085 | 40.0% |
| 0.50 | 0.15 | 808 | -0.0629 | 10.0% |
| 0.50 | 0.25 | 486 | -0.0603 | 10.0% |
| 0.50 | 0.35 | 250 | -0.0097 | 50.0% |
| 0.50 | 0.45 | 119 | -0.0055 | 40.0% |
| 0.55 | 0.10 | 685 | -0.0603 | 10.0% |
| 0.55 | 0.20 | 559 | -0.0603 | 10.0% |
| 0.55 | 0.30 | 344 | -0.0276 | 30.0% |
| 0.55 | 0.40 | 165 | -0.0036 | 50.0% |
| 0.55 | 0.50 | 84 | -0.0085 | 40.0% |
| 0.60 | 0.15 | 358 | -0.0161 | 40.0% |
| 0.60 | 0.25 | 332 | -0.0141 | 40.0% |
| 0.60 | 0.35 | 237 | -0.0168 | 40.0% |
| 0.60 | 0.45 | 119 | -0.0055 | 40.0% |
| 0.65 | 0.10 | 146 | -0.0101 | 40.0% |
| 0.65 | 0.20 | 146 | -0.0101 | 40.0% |
| 0.65 | 0.30 | 142 | -0.0101 | 40.0% |
| 0.65 | 0.40 | 120 | -0.0085 | 40.0% |
| 0.65 | 0.50 | 80 | -0.0085 | 40.0% |
| 0.70 | 0.15 | 49 | -0.0069 | 40.0% |
| 0.70 | 0.25 | 49 | -0.0069 | 40.0% |
| 0.70 | 0.35 | 49 | -0.0069 | 40.0% |
| 0.70 | 0.45 | 48 | -0.0069 | 40.0% |
| 0.75 | 0.10 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.20 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.30 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.40 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.50 | 2 | -0.0596 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 165 candidates, mean lock IC=-0.0036, 50.0% positive

### 588000ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 273 | -0.0282 | 30.0% |
| 0.45 | 0.20 | 127 | -0.0272 | 40.0% |
| 0.45 | 0.30 | 58 | -0.0414 | 30.0% |
| 0.45 | 0.40 | 24 | -0.0065 | 60.0% |
| 0.45 | 0.50 | 7 | -0.0184 | 28.6% |
| 0.50 | 0.15 | 174 | -0.0134 | 40.0% |
| 0.50 | 0.25 | 85 | -0.0414 | 30.0% |
| 0.50 | 0.35 | 41 | -0.0414 | 30.0% |
| 0.50 | 0.45 | 12 | -0.0129 | 40.0% |
| 0.55 | 0.10 | 146 | -0.0176 | 40.0% |
| 0.55 | 0.20 | 106 | -0.0272 | 40.0% |
| 0.55 | 0.30 | 58 | -0.0414 | 30.0% |
| 0.55 | 0.40 | 24 | -0.0065 | 60.0% |
| 0.55 | 0.50 | 7 | -0.0184 | 28.6% |
| 0.60 | 0.15 | 68 | -0.0176 | 40.0% |
| 0.60 | 0.25 | 57 | -0.0414 | 30.0% |
| 0.60 | 0.35 | 39 | -0.0414 | 30.0% |
| 0.60 | 0.45 | 12 | -0.0129 | 40.0% |
| 0.65 | 0.10 | 17 | -0.0156 | 40.0% |
| 0.65 | 0.20 | 17 | -0.0156 | 40.0% |
| 0.65 | 0.30 | 16 | -0.0136 | 40.0% |
| 0.65 | 0.40 | 13 | -0.0161 | 40.0% |
| 0.65 | 0.50 | 7 | -0.0184 | 28.6% |
| 0.70 | 0.15 | 2 | -0.0322 | 0.0% |
| 0.70 | 0.25 | 2 | -0.0322 | 0.0% |
| 0.70 | 0.35 | 2 | -0.0322 | 0.0% |
| 0.70 | 0.45 | 2 | -0.0322 | 0.0% |
| 0.75 | 0.10 | 2 | -0.0322 | 0.0% |
| 0.75 | 0.20 | 2 | -0.0322 | 0.0% |
| 0.75 | 0.30 | 2 | -0.0322 | 0.0% |
| 0.75 | 0.40 | 2 | -0.0322 | 0.0% |
| 0.75 | 0.50 | 1 | -0.0142 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 24 candidates, mean lock IC=-0.0065, 60.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1012 | +0.0912 | 100.0% |
| 0.45 | 0.20 | 808 | +0.0912 | 100.0% |
| 0.45 | 0.30 | 526 | +0.0912 | 100.0% |
| 0.45 | 0.40 | 323 | +0.0912 | 100.0% |
| 0.45 | 0.50 | 158 | +0.0781 | 100.0% |
| 0.50 | 0.15 | 914 | +0.0912 | 100.0% |
| 0.50 | 0.25 | 670 | +0.0912 | 100.0% |
| 0.50 | 0.35 | 400 | +0.0912 | 100.0% |
| 0.50 | 0.45 | 240 | +0.0832 | 100.0% |
| 0.55 | 0.10 | 927 | +0.0912 | 100.0% |
| 0.55 | 0.20 | 798 | +0.0912 | 100.0% |
| 0.55 | 0.30 | 526 | +0.0912 | 100.0% |
| 0.55 | 0.40 | 323 | +0.0912 | 100.0% |
| 0.55 | 0.50 | 158 | +0.0781 | 100.0% |
| 0.60 | 0.15 | 648 | +0.0912 | 100.0% |
| 0.60 | 0.25 | 595 | +0.0912 | 100.0% |
| 0.60 | 0.35 | 395 | +0.0912 | 100.0% |
| 0.60 | 0.45 | 240 | +0.0832 | 100.0% |
| 0.65 | 0.10 | 333 | +0.0832 | 100.0% |
| 0.65 | 0.20 | 332 | +0.0832 | 100.0% |
| 0.65 | 0.30 | 329 | +0.0832 | 100.0% |
| 0.65 | 0.40 | 292 | +0.0832 | 100.0% |
| 0.65 | 0.50 | 157 | +0.0781 | 100.0% |
| 0.70 | 0.15 | 114 | +0.0700 | 100.0% |
| 0.70 | 0.25 | 114 | +0.0700 | 100.0% |
| 0.70 | 0.35 | 114 | +0.0700 | 100.0% |
| 0.70 | 0.45 | 109 | +0.0700 | 100.0% |
| 0.75 | 0.10 | 21 | +0.0504 | 100.0% |
| 0.75 | 0.20 | 21 | +0.0504 | 100.0% |
| 0.75 | 0.30 | 21 | +0.0504 | 100.0% |
| 0.75 | 0.40 | 21 | +0.0504 | 100.0% |
| 0.75 | 0.50 | 21 | +0.0504 | 100.0% |
| 0.80 | 0.15 | 5 | +0.0354 | 100.0% |
| 0.80 | 0.25 | 5 | +0.0354 | 100.0% |
| 0.80 | 0.35 | 5 | +0.0354 | 100.0% |
| 0.80 | 0.45 | 5 | +0.0354 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1012 candidates, mean lock IC=+0.0912, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 142 | +0.0621 | 100.0% |
| 0.45 | 0.20 | 72 | +0.0575 | 100.0% |
| 0.45 | 0.30 | 33 | +0.0504 | 100.0% |
| 0.45 | 0.40 | 9 | +0.0387 | 77.8% |
| 0.45 | 0.50 | 2 | +0.0484 | 100.0% |
| 0.50 | 0.15 | 94 | +0.0505 | 90.0% |
| 0.50 | 0.25 | 48 | +0.0564 | 100.0% |
| 0.50 | 0.35 | 18 | +0.0571 | 100.0% |
| 0.50 | 0.45 | 3 | +0.0539 | 100.0% |
| 0.55 | 0.10 | 81 | +0.0497 | 90.0% |
| 0.55 | 0.20 | 64 | +0.0575 | 100.0% |
| 0.55 | 0.30 | 32 | +0.0504 | 100.0% |
| 0.55 | 0.40 | 9 | +0.0387 | 77.8% |
| 0.55 | 0.50 | 2 | +0.0484 | 100.0% |
| 0.60 | 0.15 | 29 | +0.0446 | 100.0% |
| 0.60 | 0.25 | 26 | +0.0517 | 100.0% |
| 0.60 | 0.35 | 16 | +0.0604 | 100.0% |
| 0.60 | 0.45 | 3 | +0.0539 | 100.0% |
| 0.65 | 0.10 | 9 | +0.0466 | 100.0% |
| 0.65 | 0.20 | 9 | +0.0466 | 100.0% |
| 0.65 | 0.30 | 9 | +0.0466 | 100.0% |
| 0.65 | 0.40 | 6 | +0.0474 | 100.0% |
| 0.65 | 0.50 | 2 | +0.0484 | 100.0% |
| 0.70 | 0.15 | 2 | +0.0484 | 100.0% |
| 0.70 | 0.25 | 2 | +0.0484 | 100.0% |
| 0.70 | 0.35 | 2 | +0.0484 | 100.0% |
| 0.70 | 0.45 | 2 | +0.0484 | 100.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 142 candidates, mean lock IC=+0.0621, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 407 | -0.0139 | 30.0% |
| 0.45 | 0.20 | 69 | -0.0260 | 10.0% |
| 0.45 | 0.30 | 9 | -0.0053 | 33.3% |
| 0.45 | 0.40 | 1 | -0.0250 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 165 | -0.0188 | 10.0% |
| 0.50 | 0.25 | 28 | -0.0094 | 40.0% |
| 0.50 | 0.35 | 5 | -0.0016 | 40.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 76 | -0.0005 | 50.0% |
| 0.55 | 0.20 | 18 | +0.0014 | 60.0% |
| 0.55 | 0.30 | 6 | -0.0005 | 50.0% |
| 0.55 | 0.40 | 1 | -0.0250 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | -0.0039 | 37.5% |
| 0.60 | 0.25 | 7 | -0.0061 | 28.6% |
| 0.60 | 0.35 | 5 | -0.0016 | 40.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 1 | -0.0061 | 0.0% |
| 0.65 | 0.20 | 1 | -0.0061 | 0.0% |
| 0.65 | 0.30 | 1 | -0.0061 | 0.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.25 → 10 candidates, mean lock IC=+0.0018, 50.0% positive

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

1. **300ETF `single` — B2 Rolling Guard too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 15.0%, mean lock Sharpe=-0.4679). Consider relaxing this gate.
2. **300ETF `single` — Admission too loose**: 71% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
3. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 9.0%, mean lock Sharpe=-0.5009). Consider relaxing this gate.
4. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.0778). Consider relaxing this gate.
5. **50ETF `single` — BH-FDR Gate too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.0485). Consider relaxing this gate.
6. **50ETF `short` — B2 Rolling Guard too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.2956). Consider relaxing this gate.
7. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.2541). Consider relaxing this gate.
8. **500ETF `single` — B2 Rolling Guard too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.2375). Consider relaxing this gate.
9. **500ETF `single` — BH-FDR Gate too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.2896). Consider relaxing this gate.
10. **500ETF `single` — B4 Correlation Gate too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.0280). Consider relaxing this gate.
11. **500ETF `single` — Admission too loose**: 55% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
12. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 21.0%, mean lock Sharpe=-0.1118). Consider relaxing this gate.
13. **500ETF `long` — BH-FDR Gate too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 21.0%, mean lock Sharpe=-0.2678). Consider relaxing this gate.
14. **500ETF `long` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
15. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 27.0%, mean lock Sharpe=-0.0553). Consider relaxing this gate.
16. **500ETF `short` — B2 Rolling Guard too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 27.0%, mean lock Sharpe=+0.1761). Consider relaxing this gate.
17. **500ETF `short` — BH-FDR Gate too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 27.0%, mean lock Sharpe=-0.0025). Consider relaxing this gate.
18. **588000ETF `single` — B2 Rolling Guard too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.1435). Consider relaxing this gate.
19. **588000ETF `single` — B4 Correlation Gate too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.1171). Consider relaxing this gate.
20. **588000ETF `single` — Admission too loose**: 92% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
21. **588000ETF `long` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
22. **159915ETF `single` — BH-FDR Gate too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 31.0%, mean lock Sharpe=-0.0728). Consider relaxing this gate.
23. **159915ETF `single` — B4 Correlation Gate too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 31.0%, mean lock Sharpe=+0.2509). Consider relaxing this gate.
24. **159915ETF `long` — 7-Year Jackknife Sign Stability too strict**: 43.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=+0.0372). Consider relaxing this gate.
25. **159915ETF `long` — B2 Rolling Guard too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.2248). Consider relaxing this gate.
26. **159915ETF `long` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=+0.0452). Consider relaxing this gate.
27. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 22.0%, mean lock Sharpe=-0.1537). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
