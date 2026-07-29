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

### 300ETF — `single` (Full Model Lockbox IC: +0.0031, Sharpe: -0.2455)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0923 | +0.0083 | +0.0083 | -0.0883 | 0.71 | 1/8 | 0.87 | 1.96 | `max_up_ret` (0.89) | +0.0221 | -0.3082 |
| `early_order_flow_imbalance` | Volatility & Oscillators | +1 | +0.0652 | -0.0189 | -0.0189 | -0.4041 | 1.12 | 2/8 | 2.03 | 31.17 | — | -0.0052 | -0.1572 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1252, Sharpe: +0.8092)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1202 | +0.0742 | +0.0742 | +0.1097 | 0.42 | 0/8 | 0.52 | 0.42 | `first_bar_return` (0.46) | -0.0021 | +0.0596 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1412 | +0.1193 | +0.1193 | +0.5966 | 0.44 | 0/8 | 0.66 | 0.32 | `opening_drive_thrust_ratio` (0.40) | +0.0053 | +0.0279 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1346 | +0.0910 | +0.0910 | +0.5264 | 0.37 | 0/8 | 0.81 | 0.69 | `trend_bar_close_consistency` (0.66) | -0.0015 | +0.0964 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1350 | +0.0747 | +0.0747 | +0.2436 | 0.35 | 0/8 | 0.70 | 0.51 | `body_size_progression` (0.60) | -0.0024 | +0.0995 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1239 | +0.0818 | +0.0818 | +0.0961 | 0.51 | 0/8 | 0.50 | 0.39 | `max_down_ret` (0.62) | -0.0004 | -0.1358 |
| `combo_rank_min__star50_limit_proximity_early__opening_momentum_score` | Intraday Range Momentum | +1 | +0.0987 | +0.1213 | +0.1213 | +1.2788 | 0.47 | 0/8 | 0.82 | 0.56 | `star50_limit_proximity_early` (0.55) | +0.0043 | +0.1721 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1055 | +0.0934 | +0.0934 | +1.2539 | 0.49 | 0/8 | 0.64 | 0.35 | `volume_weighted_momentum_acceleration` (0.62) | -0.0008 | +0.0865 |
| `combo_min__net_volume_flow__max_down_ret` | Intraday Range Momentum | +1 | +0.1034 | +0.1016 | +0.1016 | +0.5225 | 0.36 | 0/8 | 0.78 | 0.69 | `max_down_ret` (0.62) | +0.0034 | +0.3991 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Intraday Range Momentum | +1 | +0.1257 | +0.0875 | +0.0875 | +0.5745 | 0.49 | 0/8 | 0.83 | 0.65 | `smooth_momentum_structure` (0.62) | -0.0011 | -0.2601 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1000 | +0.1108 | +0.1108 | +0.2764 | 0.51 | 0/8 | 0.67 | 0.69 | `star50_limit_proximity_early` (0.55) | +0.0013 | +0.0034 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.0912 | +0.1529 | +0.1529 | +0.4587 | 0.72 | 1/8 | 0.54 | 0.41 | `volume_weighted_momentum_acceleration` (0.62) | +0.0061 | -0.0044 |
| `trend_strength_intraday` | Other Technical | +1 | +0.0822 | +0.0894 | +0.0894 | +0.1836 | 0.36 | 0/8 | 0.93 | 1.36 | — | -0.0001 | +0.1557 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1335, Sharpe: +1.4497)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1446 | +0.1235 | +0.1235 | +0.8704 | 0.52 | 1/8 | 1.10 | 2.98 | `bar_body_rng_0` (0.54) | +0.0083 | +0.2153 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0876 | +0.1119 | +0.1119 | +0.4883 | 0.81 | 1/8 | 1.67 | -68.28 | `yesterday_first_30min_return` (0.92) | +0.0128 | +0.2994 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Intraday Range Momentum | +1 | +0.1142 | +0.1085 | +0.1085 | +0.9171 | 0.50 | 0/8 | 1.86 | 4.00 | `demark_setup_reversal_early` (0.76) | -0.0004 | +0.0126 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1182 | +0.1236 | +0.1236 | +0.8328 | 0.37 | 0/8 | 1.49 | 2.06 | `rbreaker_sell_setup_proximity_early` (0.43) | +0.0060 | -0.1095 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1227 | +0.0781 | +0.0781 | +0.0786 | 0.42 | 0/8 | 1.43 | 2.01 | `opening_drive_thrust_ratio` (0.53) | -0.0061 | -0.1481 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0942 | +0.1242 | +0.1242 | +0.6361 | 0.62 | 1/8 | 1.59 | 4.28 | `yesterday_first_30min_return` (0.92) | +0.0106 | -0.0335 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0859 | +0.0677 | +0.0677 | -0.1117 | 0.63 | 0/8 | 1.66 | 3.03 | `volume_weighted_price_position` (0.77) | +0.0008 | +0.2197 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1225 | +0.1267 | +0.1267 | +0.4263 | 0.54 | 1/8 | 1.18 | 1.70 | `first_bar_sentiment` (0.76) | -0.0009 | +0.2172 |
| `consecutive_higher_highs` | Other Technical | +1 | +0.0463 | -0.0251 | -0.0251 | +0.2560 | 1.78 | 2/8 | 7.95 | 4.04 | — | -0.0068 | +0.0006 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0672 | -0.0273 | -0.0273 | +0.1690 | 0.52 | 0/8 | 0.75 | 0.64 | `volatility_expansion_trend_vector` (0.74) | -0.0045 | +0.1024 |
| `early_range` | Other Technical | +1 | +0.0616 | +0.0033 | +0.0033 | +0.0118 | 0.51 | 0/8 | 1.29 | 1.01 | — | -0.0049 | -0.0357 |
| `close_vs_open_range` | Other Technical | +1 | +0.0638 | +0.1017 | +0.1017 | +0.6838 | 0.72 | 0/8 | 3.56 | 3.79 | — | -0.0005 | -0.1266 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 65.0% lock IC > 0, 29.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3425_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 875 | 30 | 86.7% | 43.3% | +0.0169 | -0.1338 |
| B2 Rolling Guard | 106 | 30 | 90.0% | 26.7% | +0.0135 | -0.1313 |
| BH-FDR Gate | 11 | 11 | 27.3% | 9.1% | -0.0111 | -0.6346 |
| B3 Composite Floor | 1 | 1 | 100.0% | 0.0% | +0.0068 | -0.5939 |
| B4 Correlation Gate | 59 | 30 | 86.7% | 36.7% | +0.0146 | -0.0567 |

**Admitted Pool Summary**: 2 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0053, Mean Lock Sharpe = -0.2462

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Lock Sharpe=+0.5188
- `combo_z_sum__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Lock Sharpe=+0.5188
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1840, Lock IC=+0.0477, Lock Sharpe=+0.4999
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.1834, Lock IC=+0.0477, Lock Sharpe=+0.4999
- `combo_rank_min__max_up_ret__bar_ret_0`: Train IC=+0.1872, Lock IC=+0.0024, Lock Sharpe=+0.4080

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__smooth_momentum_structure__bar_ret_0`: Train IC=+0.1684, Lock IC=+0.0118, Lock Sharpe=+0.3357
- `combo_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1674, Lock IC=+0.0242, Lock Sharpe=+0.1912
- `combo_z_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1674, Lock IC=+0.0242, Lock Sharpe=+0.1912
- `combo_rel_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1668, Lock IC=+0.0217, Lock Sharpe=+0.1912
- `combo_rel_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1721, Lock IC=+0.0138, Lock Sharpe=+0.1415

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Lock Sharpe=+0.1611

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__max_up_ret__first_bar_sentiment`: Train IC=+0.1850, Lock IC=+0.0000, Lock Sharpe=+0.3515
- `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`: Train IC=+0.1924, Lock IC=+0.0095, Lock Sharpe=+0.2579
- `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`: Train IC=+0.1917, Lock IC=+0.0096, Lock Sharpe=+0.2579
- `combo_rank_max__max_up_ret__bar_ret_0`: Train IC=+0.2224, Lock IC=+0.0109, Lock Sharpe=+0.1585
- `combo_rank_max__max_up_ret__first_bar_return`: Train IC=+0.2224, Lock IC=+0.0109, Lock Sharpe=+0.1585

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 38.0% lock IC > 0, 14.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5346_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 528 | 30 | 83.3% | 26.7% | +0.0227 | -0.2260 |
| B2 Rolling Guard | 48 | 30 | 20.0% | 6.7% | -0.0071 | -0.4064 |
| BH-FDR Gate | 10 | 10 | 40.0% | 0.0% | -0.0141 | -0.5828 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__willr14__sma100_dist`: Train IC=+0.1249, Lock IC=+0.0527, Lock Sharpe=+0.6597
- `combo_sig_product__donchian_breakout_ratio_20d__sma100_dist`: Train IC=+0.1221, Lock IC=+0.0363, Lock Sharpe=+0.3227
- `combo_sig_product__donchian_breakout_proximity_20d__sma100_dist`: Train IC=+0.1221, Lock IC=+0.0363, Lock Sharpe=+0.3227
- `bar_rng_0`: Train IC=+0.0996, Lock IC=+0.0131, Lock Sharpe=+0.2514
- `combo_min__sma100_dist__wavetrend_osc_day`: Train IC=+0.1061, Lock IC=+0.0346, Lock Sharpe=+0.2110

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__roc60__wavetrend_osc_day`: Train IC=+0.0642, Lock IC=+0.0295, Lock Sharpe=+0.2578
- `combo_min__roc60__yesterday_wavetrend_osc`: Train IC=+0.0642, Lock IC=+0.0295, Lock Sharpe=+0.2578

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 13.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5447_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 70.0% | 30.0% | +0.0073 | -0.3172 |
| B2 Rolling Guard | 62 | 30 | 43.3% | 6.7% | -0.0021 | -0.6935 |
| BH-FDR Gate | 7 | 7 | 100.0% | 14.3% | +0.0381 | -0.0574 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1333, Lock IC=+0.0340, Lock Sharpe=+0.5556
- `early_vwap_acceleration`: Train IC=+0.1442, Lock IC=+0.0189, Lock Sharpe=+0.4977
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1373, Lock IC=+0.0627, Lock Sharpe=+0.4572
- `yesterday_body_ratio`: Train IC=+0.1295, Lock IC=+0.0571, Lock Sharpe=+0.4507
- `limit_down_proximity_early`: Train IC=+0.1106, Lock IC=+0.0570, Lock Sharpe=+0.4461

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.0750, Lock IC=+0.0665, Lock Sharpe=+0.4292
- `combo_sig_product__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0510, Lock IC=+0.0272, Lock Sharpe=+0.2801

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1580, Lock IC=+0.0543, Lock Sharpe=+0.5842

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 73.0% lock IC > 0, 29.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2793_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 884 | 30 | 96.7% | 66.7% | +0.0417 | +0.2210 |
| B2 Rolling Guard | 37 | 30 | 43.3% | 10.0% | -0.0047 | -0.5903 |
| BH-FDR Gate | 3 | 3 | 33.3% | 0.0% | -0.0180 | -0.6054 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__roc60__wavetrend_osc_day`: Train IC=+0.1330, Lock IC=+0.0470, Lock Sharpe=+0.9851
- `combo_max__roc60__yesterday_wavetrend_osc`: Train IC=+0.1330, Lock IC=+0.0470, Lock Sharpe=+0.9851
- `combo_min__iv_corridor_width__wavetrend_osc_day`: Train IC=+0.1441, Lock IC=+0.0566, Lock Sharpe=+0.8007
- `combo_min__iv_corridor_width__yesterday_wavetrend_osc`: Train IC=+0.1441, Lock IC=+0.0566, Lock Sharpe=+0.8007
- `combo_max__bar_vol_4__rsi21`: Train IC=+0.1324, Lock IC=+0.0699, Lock Sharpe=+0.7614

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__bar_vol_4__first_bar_volume`: Train IC=+0.1157, Lock IC=+0.0211, Lock Sharpe=+0.1892
- `combo_product__bar_vol_4__bar_vol_0`: Train IC=+0.1157, Lock IC=+0.0211, Lock Sharpe=+0.1892
- `vix_iv_ratio`: Train IC=+0.0824, Lock IC=+0.0464, Lock Sharpe=+0.0580

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 7.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5980_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 325 | 30 | 63.3% | 16.7% | +0.0135 | -0.7170 |
| B2 Rolling Guard | 35 | 30 | 33.3% | 0.0% | -0.0059 | -0.5010 |
| BH-FDR Gate | 8 | 8 | 12.5% | 0.0% | -0.0226 | -1.3760 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.0929, Lock IC=+0.0849, Lock Sharpe=+0.7485
- `combo_sig_product__yesterday_wavetrend_osc__donchian_breakout_ratio_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034
- `combo_sig_product__yesterday_wavetrend_osc__donchian_breakout_proximity_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034
- `combo_sig_product__wavetrend_osc_day__donchian_breakout_ratio_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034
- `combo_sig_product__wavetrend_osc_day__donchian_breakout_proximity_20d`: Train IC=+0.1426, Lock IC=+0.0577, Lock Sharpe=+0.1034

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5499_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 275 | 30 | 73.3% | 40.0% | +0.0304 | -0.1384 |
| B2 Rolling Guard | 42 | 30 | 33.3% | 6.7% | -0.0001 | -0.4341 |
| BH-FDR Gate | 4 | 4 | 0.0% | 0.0% | -0.0376 | -0.4551 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.7549
- `limit_down_proximity_early`: Train IC=+0.1463, Lock IC=+0.0372, Lock Sharpe=+0.7549
- `gap_pct`: Train IC=+0.1134, Lock IC=+0.0703, Lock Sharpe=+0.5557
- `sma200_dist`: Train IC=+0.1275, Lock IC=+0.0508, Lock Sharpe=+0.5161
- `combo_mean__bar_vol_4__mfi14`: Train IC=+0.1427, Lock IC=+0.0752, Lock Sharpe=+0.4001

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `close_vs_open_range`: Train IC=+0.0929, Lock IC=+0.0458, Lock Sharpe=+0.4047
- `early_bearish_engulfing_count`: Train IC=+0.0000, Lock IC=+0.0445, Lock Sharpe=+0.0389

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 77.0% lock IC > 0, 50.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0134_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1883 | 30 | 96.7% | 96.7% | +0.1009 | +0.6809 |
| B2 Rolling Guard | 405 | 30 | 100.0% | 90.0% | +0.0808 | +0.4364 |
| BH-FDR Gate | 7 | 7 | 85.7% | 0.0% | +0.0168 | -0.4558 |
| B3 Composite Floor | 6 | 6 | 100.0% | 100.0% | +0.0625 | +0.6393 |
| B4 Correlation Gate | 529 | 30 | 100.0% | 100.0% | +0.0964 | +0.5817 |

**Admitted Pool Summary**: 12 features, False Positive Rate = 0.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0997, Mean Lock Sharpe = +0.5074

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Lock Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2343, Lock IC=+0.1237, Lock Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Lock Sharpe=+1.1505
- `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2142, Lock IC=+0.1160, Lock Sharpe=+1.1034
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2639, Lock IC=+0.1189, Lock Sharpe=+1.0221

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Lock Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Lock Sharpe=+1.2071
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Lock Sharpe=+1.1213
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Lock Sharpe=+0.7913
- `combo_tri_z_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Lock Sharpe=+0.7913

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.1552, Lock IC=+0.0576, Lock Sharpe=+1.1266
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.1552, Lock IC=+0.0576, Lock Sharpe=+1.1266
- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Lock Sharpe=+0.5788
- `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1912, Lock IC=+0.0954, Lock Sharpe=+0.5787
- `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression`: Train IC=+0.1969, Lock IC=+0.0548, Lock Sharpe=+0.2617

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2665, Lock IC=+0.1105, Lock Sharpe=+0.9584
- `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2575, Lock IC=+0.0857, Lock Sharpe=+0.8706
- `combo_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2513, Lock IC=+0.0874, Lock Sharpe=+0.8706
- `combo_z_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2513, Lock IC=+0.0874, Lock Sharpe=+0.8706
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2538, Lock IC=+0.1120, Lock Sharpe=+0.8451

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 68.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2655_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1254 | 30 | 56.7% | 33.3% | +0.0283 | -0.0987 |
| B2 Rolling Guard | 59 | 30 | 83.3% | 10.0% | +0.0360 | -0.3263 |
| BH-FDR Gate | 35 | 30 | 40.0% | 16.7% | -0.0040 | -0.2582 |
| B3 Composite Floor | 2 | 2 | 100.0% | 100.0% | +0.1070 | +0.4649 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_return`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.4456
- `bar_ret_0`: Train IC=+0.2113, Lock IC=+0.0686, Lock Sharpe=+0.4456
- `combo_mean__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.3726
- `combo_z_sum__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.3726
- `combo_mean__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.1981, Lock IC=+0.0575, Lock Sharpe=+0.3726

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__false_breakout_accumulation__consecutive_higher_highs`: Train IC=+0.0610, Lock IC=+0.0411, Lock Sharpe=+0.3851
- `combo_rel_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.0419, Lock IC=+0.0139, Lock Sharpe=+0.1319
- `combo_rel_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.0419, Lock IC=+0.0139, Lock Sharpe=+0.1319

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1051, Lock IC=+0.1561, Lock Sharpe=+1.1881
- `combo_abs_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.0894, Lock IC=+0.0391, Lock Sharpe=+0.8542
- `combo_abs_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.0894, Lock IC=+0.0391, Lock Sharpe=+0.8542
- `volatility_expansion_trend_vector`: Train IC=+0.0806, Lock IC=+0.0873, Lock Sharpe=+0.2303
- `combo_min__early_body_momentum__morning_trend_extrapolated`: Train IC=+0.0765, Lock IC=+0.0612, Lock Sharpe=+0.0227

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_trend_extrapolated`: Train IC=+0.2095, Lock IC=+0.1061, Lock Sharpe=+0.5616
- `combo_rank_min__star50_limit_proximity_early__morning_trend_extrapolated`: Train IC=+0.2432, Lock IC=+0.1079, Lock Sharpe=+0.3682

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2789_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 377 | 30 | 50.0% | 30.0% | +0.0159 | -0.1880 |
| B2 Rolling Guard | 43 | 30 | 50.0% | 16.7% | +0.0021 | -0.1277 |
| BH-FDR Gate | 8 | 8 | 87.5% | 75.0% | +0.0758 | +0.1756 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1538, Lock IC=+0.1176, Lock Sharpe=+1.0733
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1538, Lock IC=+0.1176, Lock Sharpe=+1.0733
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1202, Lock IC=+0.1196, Lock Sharpe=+0.9515
- `consecutive_trend_bar_intensity`: Train IC=+0.1062, Lock IC=+0.0852, Lock Sharpe=+0.8713
- `combo_min__body_to_range_ratio__net_volume_flow`: Train IC=+0.1316, Lock IC=+0.0829, Lock Sharpe=+0.4421

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv_diff_1d`: Train IC=+0.0831, Lock IC=+0.0677, Lock Sharpe=+0.8717
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0644, Lock Sharpe=+0.4764
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0278, Lock Sharpe=+0.3337
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0694, Lock Sharpe=+0.3203
- `micro_gap_trend_continuation`: Train IC=+0.0587, Lock IC=+0.0708, Lock Sharpe=+0.0776

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1694, Lock IC=+0.1248, Lock Sharpe=+1.0490
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1694, Lock IC=+0.1248, Lock Sharpe=+1.0490
- `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1416, Lock IC=+0.0921, Lock Sharpe=+0.3653
- `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1416, Lock IC=+0.0921, Lock Sharpe=+0.3653
- `combo_ifelse__gap_pct__yesterday_early_vwap_dev__net_volume_flow`: Train IC=+0.1503, Lock IC=+0.0875, Lock Sharpe=+0.0257

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 57.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.2655_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1189 | 30 | 100.0% | 83.3% | +0.0980 | +0.4890 |
| B2 Rolling Guard | 221 | 30 | 100.0% | 100.0% | +0.0981 | +0.6281 |
| BH-FDR Gate | 2 | 2 | 100.0% | 0.0% | +0.0392 | -0.2091 |
| B3 Composite Floor | 90 | 30 | 100.0% | 100.0% | +0.0901 | +0.6055 |
| B4 Correlation Gate | 255 | 30 | 100.0% | 100.0% | +0.1229 | +1.3191 |

**Admitted Pool Summary**: 12 features, False Positive Rate = 25.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0764, Mean Lock Sharpe = +0.4515

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Lock Sharpe=+1.4951
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Lock Sharpe=+1.4951
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2329, Lock IC=+0.1019, Lock Sharpe=+1.4711
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.1917, Lock IC=+0.1128, Lock Sharpe=+1.2866
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Lock Sharpe=+1.0349

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Lock Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Lock Sharpe=+1.3322
- `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.1883, Lock IC=+0.1273, Lock Sharpe=+1.0683
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.1883, Lock IC=+0.1273, Lock Sharpe=+1.0683
- `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.1833, Lock IC=+0.1115, Lock Sharpe=+0.9311

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2080, Lock IC=+0.1414, Lock Sharpe=+1.4883
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2047, Lock IC=+0.1185, Lock Sharpe=+1.3299
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2019, Lock IC=+0.1192, Lock Sharpe=+1.1310
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2110, Lock IC=+0.0899, Lock Sharpe=+1.0542
- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.1928, Lock IC=+0.0882, Lock Sharpe=+0.9124

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Lock Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Lock Sharpe=+1.8009
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2717, Lock IC=+0.1211, Lock Sharpe=+1.8009
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2724, Lock IC=+0.1237, Lock Sharpe=+1.5940
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.2724, Lock IC=+0.1237, Lock Sharpe=+1.5940

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 53.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0833_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 906 | 30 | 96.7% | 76.7% | +0.0802 | +0.3278 |
| B2 Rolling Guard | 84 | 30 | 96.7% | 86.7% | +0.1005 | +0.6794 |
| BH-FDR Gate | 119 | 30 | 100.0% | 93.3% | +0.1014 | +0.6624 |
| B3 Composite Floor | 11 | 11 | 100.0% | 90.9% | +0.0921 | +0.6774 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1708, Lock IC=+0.1017, Lock Sharpe=+1.2036
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1693, Lock IC=+0.1305, Lock Sharpe=+1.1546
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__trend_strength_intraday`: Train IC=+0.1807, Lock IC=+0.0953, Lock Sharpe=+1.0258
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__counter_trend_bar_weakness`: Train IC=+0.1717, Lock IC=+0.0907, Lock Sharpe=+0.9302
- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1772, Lock IC=+0.1258, Lock Sharpe=+0.8461

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1316, Lock IC=+0.1108, Lock Sharpe=+1.3365
- `combo_rank_min__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1316, Lock IC=+0.1108, Lock Sharpe=+1.3365
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1461, Lock IC=+0.1314, Lock Sharpe=+1.3188
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1461, Lock IC=+0.1314, Lock Sharpe=+1.3188
- `combo_sig_product__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.1181, Lock IC=+0.0964, Lock Sharpe=+1.2137

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1380, Lock IC=+0.1040, Lock Sharpe=+1.0977
- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1380, Lock IC=+0.1040, Lock Sharpe=+1.0977
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1324, Lock IC=+0.1159, Lock Sharpe=+1.0048
- `combo_tri_median__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1324, Lock IC=+0.1159, Lock Sharpe=+1.0048
- `combo_tri_median__rbreaker_sell_setup_proximity_early__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1735, Lock IC=+0.1298, Lock Sharpe=+0.8619

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1828, Lock IC=+0.0959, Lock Sharpe=+0.9059
- `combo_tri_median__micro_gap_trend_continuation__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.1828, Lock IC=+0.0959, Lock Sharpe=+0.9059
- `combo_tri_mean__opening_drive_thrust_ratio__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.8130
- `combo_tri_z_mean__opening_drive_thrust_ratio__open_to_current_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.8130
- `combo_tri_mean__opening_drive_thrust_ratio__first_30min_return__counter_trend_bar_weakness`: Train IC=+0.1846, Lock IC=+0.1049, Lock Sharpe=+0.8130

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 44.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3745_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 247 | 30 | 76.7% | 46.7% | +0.0301 | -0.1996 |
| B2 Rolling Guard | 50 | 30 | 63.3% | 40.0% | +0.0232 | +0.0101 |
| BH-FDR Gate | 2 | 2 | 50.0% | 50.0% | +0.0352 | +0.0084 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `trend_day_regime_conviction`: Train IC=+0.1462, Lock IC=+0.0928, Lock Sharpe=+0.7840
- `high_low_sequence_momentum`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.6845
- `rsi_opening`: Train IC=+0.0895, Lock IC=+0.0912, Lock Sharpe=+0.6845
- `lunch_transition_volume_skew`: Train IC=+0.0808, Lock IC=+0.0330, Lock Sharpe=+0.6751
- `combo_mean__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0748, Lock IC=+0.0639, Lock Sharpe=+0.3991

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0517, Lock Sharpe=+1.1801
- `combo_rank_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0792, Lock IC=+0.0809, Lock Sharpe=+0.8982
- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0609, Lock IC=+0.0815, Lock Sharpe=+0.8238
- `limit_down_proximity_early`: Train IC=+0.0276, Lock IC=+0.1167, Lock Sharpe=+0.7619
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0276, Lock IC=+0.1167, Lock Sharpe=+0.7619

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volatility_expansion_trend_vector`: Train IC=+0.0580, Lock IC=+0.0943, Lock Sharpe=+0.5003

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 398 | +0.0209 | 70.0% |
| 0.45 | 0.20 | 393 | +0.0209 | 70.0% |
| 0.45 | 0.30 | 374 | +0.0209 | 70.0% |
| 0.45 | 0.40 | 311 | +0.0209 | 70.0% |
| 0.45 | 0.50 | 202 | +0.0209 | 70.0% |
| 0.50 | 0.15 | 394 | +0.0209 | 70.0% |
| 0.50 | 0.25 | 386 | +0.0209 | 70.0% |
| 0.50 | 0.35 | 353 | +0.0209 | 70.0% |
| 0.50 | 0.45 | 256 | +0.0209 | 70.0% |
| 0.55 | 0.10 | 394 | +0.0209 | 70.0% |
| 0.55 | 0.20 | 393 | +0.0209 | 70.0% |
| 0.55 | 0.30 | 374 | +0.0209 | 70.0% |
| 0.55 | 0.40 | 311 | +0.0209 | 70.0% |
| 0.55 | 0.50 | 202 | +0.0209 | 70.0% |
| 0.60 | 0.15 | 373 | +0.0209 | 70.0% |
| 0.60 | 0.25 | 372 | +0.0209 | 70.0% |
| 0.60 | 0.35 | 352 | +0.0209 | 70.0% |
| 0.60 | 0.45 | 256 | +0.0209 | 70.0% |
| 0.65 | 0.10 | 304 | +0.0209 | 70.0% |
| 0.65 | 0.20 | 304 | +0.0209 | 70.0% |
| 0.65 | 0.30 | 304 | +0.0209 | 70.0% |
| 0.65 | 0.40 | 292 | +0.0209 | 70.0% |
| 0.65 | 0.50 | 202 | +0.0209 | 70.0% |
| 0.70 | 0.15 | 152 | +0.0207 | 70.0% |
| 0.70 | 0.25 | 152 | +0.0207 | 70.0% |
| 0.70 | 0.35 | 152 | +0.0207 | 70.0% |
| 0.70 | 0.45 | 152 | +0.0207 | 70.0% |
| 0.75 | 0.10 | 40 | +0.0141 | 60.0% |
| 0.75 | 0.20 | 40 | +0.0141 | 60.0% |
| 0.75 | 0.30 | 40 | +0.0141 | 60.0% |
| 0.75 | 0.40 | 40 | +0.0141 | 60.0% |
| 0.75 | 0.50 | 40 | +0.0141 | 60.0% |
| 0.80 | 0.15 | 19 | +0.0142 | 60.0% |
| 0.80 | 0.25 | 19 | +0.0142 | 60.0% |
| 0.80 | 0.35 | 19 | +0.0142 | 60.0% |
| 0.80 | 0.45 | 19 | +0.0142 | 60.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 398 candidates, mean lock IC=+0.0209, 70.0% positive

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
| 0.45 | 0.10 | 333 | +0.0573 | 100.0% |
| 0.45 | 0.20 | 331 | +0.0573 | 100.0% |
| 0.45 | 0.30 | 328 | +0.0573 | 100.0% |
| 0.45 | 0.40 | 312 | +0.0573 | 100.0% |
| 0.45 | 0.50 | 304 | +0.0573 | 100.0% |
| 0.50 | 0.15 | 331 | +0.0573 | 100.0% |
| 0.50 | 0.25 | 331 | +0.0573 | 100.0% |
| 0.50 | 0.35 | 321 | +0.0573 | 100.0% |
| 0.50 | 0.45 | 307 | +0.0573 | 100.0% |
| 0.55 | 0.10 | 332 | +0.0573 | 100.0% |
| 0.55 | 0.20 | 331 | +0.0573 | 100.0% |
| 0.55 | 0.30 | 328 | +0.0573 | 100.0% |
| 0.55 | 0.40 | 312 | +0.0573 | 100.0% |
| 0.55 | 0.50 | 304 | +0.0573 | 100.0% |
| 0.60 | 0.15 | 330 | +0.0573 | 100.0% |
| 0.60 | 0.25 | 330 | +0.0573 | 100.0% |
| 0.60 | 0.35 | 321 | +0.0573 | 100.0% |
| 0.60 | 0.45 | 307 | +0.0573 | 100.0% |
| 0.65 | 0.10 | 312 | +0.0573 | 100.0% |
| 0.65 | 0.20 | 312 | +0.0573 | 100.0% |
| 0.65 | 0.30 | 310 | +0.0573 | 100.0% |
| 0.65 | 0.40 | 308 | +0.0573 | 100.0% |
| 0.65 | 0.50 | 303 | +0.0573 | 100.0% |
| 0.70 | 0.15 | 300 | +0.0573 | 100.0% |
| 0.70 | 0.25 | 300 | +0.0573 | 100.0% |
| 0.70 | 0.35 | 300 | +0.0573 | 100.0% |
| 0.70 | 0.45 | 300 | +0.0573 | 100.0% |
| 0.75 | 0.10 | 258 | +0.0573 | 100.0% |
| 0.75 | 0.20 | 258 | +0.0573 | 100.0% |
| 0.75 | 0.30 | 258 | +0.0573 | 100.0% |
| 0.75 | 0.40 | 258 | +0.0573 | 100.0% |
| 0.75 | 0.50 | 258 | +0.0573 | 100.0% |
| 0.80 | 0.15 | 210 | +0.0367 | 100.0% |
| 0.80 | 0.25 | 210 | +0.0367 | 100.0% |
| 0.80 | 0.35 | 210 | +0.0367 | 100.0% |
| 0.80 | 0.45 | 210 | +0.0367 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 333 candidates, mean lock IC=+0.0573, 100.0% positive

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
| 0.45 | 0.10 | 1317 | +0.0929 | 100.0% |
| 0.45 | 0.20 | 1283 | +0.0929 | 100.0% |
| 0.45 | 0.30 | 1167 | +0.0929 | 100.0% |
| 0.45 | 0.40 | 947 | +0.0929 | 100.0% |
| 0.45 | 0.50 | 694 | +0.0929 | 100.0% |
| 0.50 | 0.15 | 1305 | +0.0929 | 100.0% |
| 0.50 | 0.25 | 1226 | +0.0929 | 100.0% |
| 0.50 | 0.35 | 1073 | +0.0929 | 100.0% |
| 0.50 | 0.45 | 848 | +0.0929 | 100.0% |
| 0.55 | 0.10 | 1298 | +0.0929 | 100.0% |
| 0.55 | 0.20 | 1281 | +0.0929 | 100.0% |
| 0.55 | 0.30 | 1167 | +0.0929 | 100.0% |
| 0.55 | 0.40 | 947 | +0.0929 | 100.0% |
| 0.55 | 0.50 | 694 | +0.0929 | 100.0% |
| 0.60 | 0.15 | 1202 | +0.0929 | 100.0% |
| 0.60 | 0.25 | 1183 | +0.0929 | 100.0% |
| 0.60 | 0.35 | 1071 | +0.0929 | 100.0% |
| 0.60 | 0.45 | 848 | +0.0929 | 100.0% |
| 0.65 | 0.10 | 934 | +0.0929 | 100.0% |
| 0.65 | 0.20 | 934 | +0.0929 | 100.0% |
| 0.65 | 0.30 | 934 | +0.0929 | 100.0% |
| 0.65 | 0.40 | 891 | +0.0929 | 100.0% |
| 0.65 | 0.50 | 689 | +0.0929 | 100.0% |
| 0.70 | 0.15 | 574 | +0.0929 | 100.0% |
| 0.70 | 0.25 | 574 | +0.0929 | 100.0% |
| 0.70 | 0.35 | 574 | +0.0929 | 100.0% |
| 0.70 | 0.45 | 574 | +0.0929 | 100.0% |
| 0.75 | 0.10 | 249 | +0.0960 | 100.0% |
| 0.75 | 0.20 | 249 | +0.0960 | 100.0% |
| 0.75 | 0.30 | 249 | +0.0960 | 100.0% |
| 0.75 | 0.40 | 249 | +0.0960 | 100.0% |
| 0.75 | 0.50 | 249 | +0.0960 | 100.0% |
| 0.80 | 0.15 | 92 | +0.1004 | 100.0% |
| 0.80 | 0.25 | 92 | +0.1004 | 100.0% |
| 0.80 | 0.35 | 92 | +0.1004 | 100.0% |
| 0.80 | 0.45 | 92 | +0.1004 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 92 candidates, mean lock IC=+0.1004, 100.0% positive

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
| 0.45 | 0.10 | 689 | +0.1169 | 100.0% |
| 0.45 | 0.20 | 660 | +0.1169 | 100.0% |
| 0.45 | 0.30 | 604 | +0.1169 | 100.0% |
| 0.45 | 0.40 | 459 | +0.1169 | 100.0% |
| 0.45 | 0.50 | 301 | +0.1169 | 100.0% |
| 0.50 | 0.15 | 675 | +0.1169 | 100.0% |
| 0.50 | 0.25 | 637 | +0.1169 | 100.0% |
| 0.50 | 0.35 | 550 | +0.1169 | 100.0% |
| 0.50 | 0.45 | 386 | +0.1169 | 100.0% |
| 0.55 | 0.10 | 675 | +0.1169 | 100.0% |
| 0.55 | 0.20 | 659 | +0.1169 | 100.0% |
| 0.55 | 0.30 | 604 | +0.1169 | 100.0% |
| 0.55 | 0.40 | 459 | +0.1169 | 100.0% |
| 0.55 | 0.50 | 301 | +0.1169 | 100.0% |
| 0.60 | 0.15 | 628 | +0.1169 | 100.0% |
| 0.60 | 0.25 | 625 | +0.1169 | 100.0% |
| 0.60 | 0.35 | 550 | +0.1169 | 100.0% |
| 0.60 | 0.45 | 386 | +0.1169 | 100.0% |
| 0.65 | 0.10 | 491 | +0.1169 | 100.0% |
| 0.65 | 0.20 | 491 | +0.1169 | 100.0% |
| 0.65 | 0.30 | 491 | +0.1169 | 100.0% |
| 0.65 | 0.40 | 433 | +0.1169 | 100.0% |
| 0.65 | 0.50 | 300 | +0.1169 | 100.0% |
| 0.70 | 0.15 | 248 | +0.1169 | 100.0% |
| 0.70 | 0.25 | 248 | +0.1169 | 100.0% |
| 0.70 | 0.35 | 248 | +0.1169 | 100.0% |
| 0.70 | 0.45 | 243 | +0.1169 | 100.0% |
| 0.75 | 0.10 | 73 | +0.1169 | 100.0% |
| 0.75 | 0.20 | 73 | +0.1169 | 100.0% |
| 0.75 | 0.30 | 73 | +0.1169 | 100.0% |
| 0.75 | 0.40 | 73 | +0.1169 | 100.0% |
| 0.75 | 0.50 | 73 | +0.1169 | 100.0% |
| 0.80 | 0.15 | 13 | +0.0375 | 50.0% |
| 0.80 | 0.25 | 13 | +0.0375 | 50.0% |
| 0.80 | 0.35 | 13 | +0.0375 | 50.0% |
| 0.80 | 0.45 | 13 | +0.0375 | 50.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 689 candidates, mean lock IC=+0.1169, 100.0% positive

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
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1070 | +0.0000 | +0.0083 | 0.08x | 2015-03-16 |
| `early_order_flow_imbalance` | +0.0512 | +0.0000 | -0.0189 | -0.37x | 2010-12-14 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | +0.1382 | +0.0000 | +0.0742 | 0.54x | 2013-09-23 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1931 | +0.0000 | +0.1193 | 0.62x | No decay |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | +0.1937 | +0.0000 | +0.0910 | 0.47x | 2016-11-30 |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1673 | +0.0000 | +0.0747 | 0.45x | 2019-12-05 |
| `combo_max__bar_ret_0__max_down_ret` | +0.1604 | +0.0000 | +0.0818 | 0.51x | 2016-11-30 |
| `combo_rank_min__star50_limit_proximity_early__opening_momentum_score` | +0.1496 | +0.0000 | +0.1201 | 0.80x | 2016-09-26 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1507 | +0.0000 | +0.0934 | 0.62x | No decay |
| `combo_min__net_volume_flow__max_down_ret` | +0.1512 | +0.0000 | +0.1016 | 0.67x | 2016-09-26 |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | +0.1593 | +0.0000 | +0.0875 | 0.55x | 2022-12-15 |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | +0.1525 | +0.0000 | +0.1108 | 0.73x | 2016-09-26 |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1261 | +0.0000 | +0.1529 | 1.21x | 2016-06-27 |
| `trend_strength_intraday` | +0.1206 | +0.0000 | +0.0894 | 0.74x | 2020-02-12 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1618 | +0.0000 | +0.1235 | 0.76x | 2017-01-20 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1035 | +0.0000 | +0.1119 | 1.08x | 2011-10-18 |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | +0.1575 | +0.0000 | +0.1085 | 0.69x | 2016-10-24 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1489 | +0.0000 | +0.1236 | 0.83x | 2016-09-14 |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | +0.1624 | +0.0000 | +0.0781 | 0.48x | 2017-01-20 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1211 | +0.0000 | +0.1270 | 1.05x | 2017-01-20 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1192 | +0.0000 | +0.0677 | 0.57x | 2016-10-24 |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | +0.1502 | +0.0000 | +0.1267 | 0.84x | 2017-03-28 |
| `consecutive_higher_highs` | +0.0813 | +0.0000 | -0.0251 | -0.31x | 2014-03-25 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0645 | +0.0000 | -0.0273 | -0.42x | 2012-01-17 |
| `early_range` | +0.0633 | +0.0000 | +0.0033 | 0.05x | 2011-04-13 |
| `close_vs_open_range` | +0.1256 | +0.0000 | +0.1017 | 0.81x | 2014-03-25 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
2. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2260). Consider relaxing this gate.
3. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.3172). Consider relaxing this gate.
4. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 29.0%, mean lock Sharpe=+0.2210). Consider relaxing this gate.
5. **50ETF `long` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 7.0%, mean lock Sharpe=-0.7170). Consider relaxing this gate.
6. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.1384). Consider relaxing this gate.
7. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.6809). Consider relaxing this gate.
8. **500ETF `single` — B2 Rolling Guard too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.4364). Consider relaxing this gate.
9. **500ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.6393). Consider relaxing this gate.
10. **500ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.5817). Consider relaxing this gate.
11. **500ETF `short` — BH-FDR Gate too strict**: 75.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.1756). Consider relaxing this gate.
12. **159915ETF `single` — B2 Rolling Guard too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 57.0%, mean lock Sharpe=+0.6281). Consider relaxing this gate.
13. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 57.0%, mean lock Sharpe=+0.6055). Consider relaxing this gate.
14. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 57.0%, mean lock Sharpe=+1.3191). Consider relaxing this gate.
15. **159915ETF `long` — B2 Rolling Guard too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6794). Consider relaxing this gate.
16. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6624). Consider relaxing this gate.
17. **159915ETF `long` — B3 Composite Floor too strict**: 90.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6774). Consider relaxing this gate.
18. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.1996). Consider relaxing this gate.
19. **159915ETF `short` — B2 Rolling Guard too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=+0.0101). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
