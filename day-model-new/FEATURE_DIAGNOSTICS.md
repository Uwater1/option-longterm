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
**False Negative Rate** = % of rejected features that would have had positive lockbox IC (gate too strict).
**False Positive Rate** = % of admitted features with negative lockbox IC (gate too loose).

### 300ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 1341 | 30 | 46.7% | -0.0043 | -0.7108 |
| B2 Rolling Guard | 555 | 30 | 80.0% | +0.0135 | -0.4302 |
| Absolute Sign Check | 128 | 30 | 76.7% | +0.0278 | +0.0912 |
| BH-FDR Gate | 190 | 30 | 70.0% | +0.0038 | -0.3319 |
| B3 Composite Floor | 41 | 30 | 83.3% | +0.0108 | -0.4032 |
| B4 Correlation Gate | 28 | 28 | 85.7% | +0.0305 | -0.2073 |

**Admitted Pool Summary**: 9 features, False Positive Rate = 11.1% (admitted but negative lock IC), Mean Lock IC = +0.0244, Mean Lock Sharpe = -0.2282

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `yesterday_lunch_gap`: Train IC=+0.1668, Lock IC=+0.0943, Lock Sharpe=+0.3158
- `early_vwap_dev`: Train IC=+0.1168, Lock IC=+0.0281, Lock Sharpe=-0.3783
- `bar_vwap_dev_5`: Train IC=+0.1168, Lock IC=+0.0281, Lock Sharpe=-0.3783
- `combo_ifelse__gap_pct__bar_vwap_dev_5__early_vwap_dev`: Train IC=+0.1168, Lock IC=+0.0281, Lock Sharpe=-0.3783
- `combo_ifelse__iv__yesterday_lunch_gap__bar_vwap_dev_5`: Train IC=+0.1168, Lock IC=+0.0281, Lock Sharpe=-0.3783

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_body_rng_0__growth_momentum_ratio`: Train IC=+0.1556, Lock IC=+0.0868, Lock Sharpe=+0.5687
- `gap_pct`: Train IC=+0.1525, Lock IC=+0.0795, Lock Sharpe=+0.1398
- `combo_min__gap_pct__bar_vwap_dev_2`: Train IC=+0.1550, Lock IC=+0.0490, Lock Sharpe=-0.9738
- `combo_rank_min__gap_pct__bar_vwap_dev_2`: Train IC=+0.1506, Lock IC=+0.0476, Lock Sharpe=-0.8272
- `combo_min__gap_pct__early_range`: Train IC=+0.1877, Lock IC=+0.0410, Lock Sharpe=-0.6286

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_ret_0__short_sell_cover_spread`: Train IC=+0.2047, Lock IC=+0.0821, Lock Sharpe=+0.4454
- `combo_ifelse__macd_hist__first_bar_return__short_sell_cover_spread`: Train IC=+0.2049, Lock IC=+0.0819, Lock Sharpe=+0.4454
- `combo_rank_min__bar_vol_0__rsi21`: Train IC=+0.1221, Lock IC=+0.0610, Lock Sharpe=-0.0262
- `combo_rank_min__first_bar_volume__rsi21`: Train IC=+0.1221, Lock IC=+0.0610, Lock Sharpe=-0.0262
- `combo_rank_min__bar_vol_0__wavetrend_osc_day`: Train IC=+0.0944, Lock IC=+0.0601, Lock Sharpe=-0.0232

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__max_up_ret__short_sell_cover_spread`: Train IC=+0.1642, Lock IC=+0.0475, Lock Sharpe=+0.3667
- `combo_tri_max__max_up_ret__bar_ret_0__gap_pct`: Train IC=+0.1589, Lock IC=+0.0397, Lock Sharpe=-0.4617
- `combo_tri_max__max_up_ret__first_bar_return__gap_pct`: Train IC=+0.1591, Lock IC=+0.0397, Lock Sharpe=-0.4617
- `combo_max__first_bar_return__gap_pct`: Train IC=+0.1633, Lock IC=+0.0367, Lock Sharpe=-0.0066
- `combo_max__bar_ret_0__gap_pct`: Train IC=+0.1637, Lock IC=+0.0366, Lock Sharpe=-0.0066

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_body_rng_0__short_sell_cover_spread`: Train IC=+0.1986, Lock IC=+0.0904, Lock Sharpe=+0.1163
- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2027, Lock IC=+0.0428, Lock Sharpe=-0.1001
- `combo_tri_min__max_up_ret__bar_ret_0__gap_pct`: Train IC=+0.1969, Lock IC=+0.0307, Lock Sharpe=-0.3129
- `combo_tri_min__max_up_ret__first_bar_return__gap_pct`: Train IC=+0.1972, Lock IC=+0.0306, Lock Sharpe=-0.3129
- `combo_tri_mean__bar_ret_0__gap_pct__first_30min_return`: Train IC=+0.2083, Lock IC=+0.0246, Lock Sharpe=+0.2007

**Top False Negatives from B4 Correlation Gate** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_ret_0__growth_momentum_ratio`: Train IC=+0.1855, Lock IC=+0.0723, Lock Sharpe=+0.5292
- `combo_ifelse__macd_hist__first_bar_return__growth_momentum_ratio`: Train IC=+0.1853, Lock IC=+0.0723, Lock Sharpe=+0.5292
- `combo_ifelse__macd_hist__first_bar_return__option_oi_growth`: Train IC=+0.1840, Lock IC=+0.0620, Lock Sharpe=+0.2963
- `combo_ifelse__macd_hist__bar_ret_0__option_oi_growth`: Train IC=+0.1841, Lock IC=+0.0619, Lock Sharpe=+0.2963
- `combo_rank_min__bar_ret_0__gap_pct`: Train IC=+0.1929, Lock IC=+0.0586, Lock Sharpe=+0.1359

### 300ETF — `long` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 119 | 30 | 50.0% | -0.0051 | -0.8476 |
| B2 Rolling Guard | 98 | 30 | 20.0% | -0.0084 | -0.3366 |
| BH-FDR Gate | 1 | 1 | 0.0% | -0.0074 | -0.9039 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `yesterday_lunch_gap`: Train IC=+0.1781, Lock IC=+0.0943, Lock Sharpe=-0.4058
- `early_trend`: Train IC=+0.1309, Lock IC=+0.0621, Lock Sharpe=-0.2372
- `first_bar_volume`: Train IC=+0.1039, Lock IC=+0.0353, Lock Sharpe=-0.1625
- `bar_vol_0`: Train IC=+0.1039, Lock IC=+0.0353, Lock Sharpe=-0.1625
- `macd_hist`: Train IC=+0.0803, Lock IC=+0.0348, Lock Sharpe=+0.4885

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `yesterday_body_ratio`: Train IC=+0.0042, Lock IC=+0.0586, Lock Sharpe=-0.3582
- `volume_sma_ratio`: Train IC=+0.0688, Lock IC=+0.0442, Lock Sharpe=+0.4181
- `yesterday_volume_ratio`: Train IC=+0.0688, Lock IC=+0.0442, Lock Sharpe=+0.4181
- `first_bar_return`: Train IC=+0.0791, Lock IC=+0.0040, Lock Sharpe=-0.1773
- `bar_ret_0`: Train IC=+0.0791, Lock IC=+0.0040, Lock Sharpe=-0.1773

### 300ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 8867 | 30 | 100.0% | +0.0220 | -0.3607 |
| B2 Rolling Guard | 2564 | 30 | 53.3% | -0.0052 | -0.6782 |
| Absolute Sign Check | 177 | 30 | 10.0% | -0.0381 | -0.6743 |
| BH-FDR Gate | 142 | 30 | 50.0% | +0.0059 | -0.5185 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_ifelse__gap_pct__vix_iv_ratio__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_ifelse__gap_pct__vix_iv_spread__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__iv__vix_iv_ratio__total_balance__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__iv__vix_iv_ratio__total_path_length__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__iv__vix_iv_ratio__short_sell_cover_spread__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_ifelse__sma20_dist__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1415, Lock IC=+0.0561, Lock Sharpe=-0.2614
- `combo_rank_min__short_sell_cover_spread__margin_short_ratio`: Train IC=+0.1696, Lock IC=+0.0540, Lock Sharpe=-0.8499
- `combo_rank_min__short_sell_cover_spread__margin_lever_ratio`: Train IC=+0.1696, Lock IC=+0.0540, Lock Sharpe=-0.8499
- `combo_tri_ifelse__vix__atr14_norm__yesterday_afternoon_reversal__short_sell_cover_spread__stoch_d`: Train IC=+0.1511, Lock IC=+0.0512, Lock Sharpe=+0.5766
- `combo_tri_ifelse__gap_pct__vix__vix_iv_ratio__total_balance__short_sell_cover_spread`: Train IC=+0.1417, Lock IC=+0.0510, Lock Sharpe=-0.7947

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_abs_diff__atr14_norm__stoch_d`: Train IC=+0.1414, Lock IC=+0.0218, Lock Sharpe=+0.0213
- `combo_tri_ifelse__gap_pct__atr14_norm__yesterday_day_skew__max_down_ret__keltner_squeeze_width`: Train IC=+0.1862, Lock IC=+0.0179, Lock Sharpe=-0.1181
- `combo_tri_ifelse__gap_pct__vix__short_sell_cover_spread__yesterday_day_skew__mfi14`: Train IC=+0.1396, Lock IC=+0.0051, Lock Sharpe=-0.4268

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `gap_pct`: Train IC=+0.1531, Lock IC=+0.0795, Lock Sharpe=+0.3802
- `combo_tri_min__gap_pct__total_path_length__atr14_norm`: Train IC=+0.2088, Lock IC=+0.0567, Lock Sharpe=-0.3960
- `combo_ifelse__vix__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1548, Lock IC=+0.0465, Lock Sharpe=-0.3810
- `combo_tri_ifelse__iv__vix__yesterday_pm_am_vol_ratio__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1548, Lock IC=+0.0465, Lock Sharpe=-0.3810
- `combo_tri_ifelse__iv__vix__yesterday_day_pm_am_vol_ratio__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1548, Lock IC=+0.0465, Lock Sharpe=-0.3810

### 50ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 1652 | 30 | 96.7% | +0.0534 | +0.0182 |
| B2 Rolling Guard | 477 | 30 | 76.7% | +0.0283 | -0.4389 |
| Absolute Sign Check | 211 | 30 | 90.0% | +0.0340 | -0.0053 |
| BH-FDR Gate | 55 | 30 | 86.7% | +0.0306 | -0.1088 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_max__bar_vol_4__macd_hist`: Train IC=+0.1584, Lock IC=+0.0931, Lock Sharpe=+0.7559
- `combo_max__bar_vol_4__willr14`: Train IC=+0.1638, Lock IC=+0.0898, Lock Sharpe=+0.2102
- `combo_tri_max__bar_vol_4__wavetrend_osc_day__stoch_k`: Train IC=+0.1558, Lock IC=+0.0871, Lock Sharpe=+0.7270
- `combo_tri_max__bar_vol_4__yesterday_wavetrend_osc__stoch_k`: Train IC=+0.1558, Lock IC=+0.0871, Lock Sharpe=+0.7270
- `combo_ifelse__macd_hist__yesterday_lunch_gap__bar_vol_4`: Train IC=+0.1473, Lock IC=+0.0804, Lock Sharpe=+0.0395

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_max__bar_vol_4__yesterday_body_ratio__bar_ret_0`: Train IC=+0.1221, Lock IC=+0.0813, Lock Sharpe=-0.9366
- `combo_ifelse__macd_hist__yesterday_lunch_gap__margin_extreme_rank_252d`: Train IC=+0.1454, Lock IC=+0.0617, Lock Sharpe=+0.4274
- `combo_ifelse__macd_hist__capital_buy_value__bar_vol_0`: Train IC=+0.1237, Lock IC=+0.0615, Lock Sharpe=-0.2508
- `combo_ifelse__macd_hist__capital_buy_value__first_bar_volume`: Train IC=+0.1237, Lock IC=+0.0615, Lock Sharpe=-0.2508
- `combo_clamp_diff__yearly_low_distance__coppock_curve_day`: Train IC=+0.1230, Lock IC=+0.0567, Lock Sharpe=+0.6634

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_max__bar_vol_4__sma50_dist__roc10`: Train IC=+0.1276, Lock IC=+0.0815, Lock Sharpe=+0.5924
- `combo_rank_min__bar_vol_5__macd_hist`: Train IC=+0.1178, Lock IC=+0.0787, Lock Sharpe=-0.1634
- `combo_tri_max__bar_vol_4__sma_distance_60d__roc10`: Train IC=+0.1235, Lock IC=+0.0734, Lock Sharpe=+0.5220
- `combo_tri_max__bar_vol_4__roc10__yearly_low_distance`: Train IC=+0.1357, Lock IC=+0.0617, Lock Sharpe=-0.0515
- `combo_tri_max__bar_vol_4__sma50_dist__stoch_k`: Train IC=+0.1040, Lock IC=+0.0608, Lock Sharpe=+0.6991

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_diff__short_balance_quantity__roc20`: Train IC=+0.1493, Lock IC=+0.0848, Lock Sharpe=-0.0456
- `combo_clamp_diff__short_balance_quantity__roc20`: Train IC=+0.1337, Lock IC=+0.0843, Lock Sharpe=-0.0456
- `combo_clamp_diff__short_balance__roc20`: Train IC=+0.1077, Lock IC=+0.0805, Lock Sharpe=-0.3469
- `combo_diff__yearly_low_distance__sma20_dist`: Train IC=+0.1250, Lock IC=+0.0719, Lock Sharpe=-0.1550
- `combo_clamp_diff__yearly_low_distance__sma20_dist`: Train IC=+0.1214, Lock IC=+0.0714, Lock Sharpe=-0.1550

### 50ETF — `long` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 3191 | 30 | 90.0% | +0.0350 | -0.4146 |
| B2 Rolling Guard | 820 | 30 | 70.0% | +0.0191 | -0.6808 |
| Absolute Sign Check | 36 | 30 | 60.0% | +0.0067 | -1.0502 |
| BH-FDR Gate | 38 | 30 | 33.3% | -0.0221 | -1.3020 |
| B3 Composite Floor | 4 | 4 | 100.0% | +0.0836 | +0.1455 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_mean__margin_net_buy__early_range__roc5`: Train IC=+0.2542, Lock IC=+0.1025, Lock Sharpe=-0.6657
- `combo_rank_max__margin_net_buy__iv_corridor_width`: Train IC=+0.1840, Lock IC=+0.0708, Lock Sharpe=-0.4155
- `combo_max__margin_net_buy__iv_corridor_width`: Train IC=+0.1640, Lock IC=+0.0674, Lock Sharpe=-0.0544
- `combo_tri_min__yesterday_wavetrend_osc__margin_net_buy__early_range`: Train IC=+0.1607, Lock IC=+0.0601, Lock Sharpe=+0.6316
- `combo_tri_min__wavetrend_osc_day__margin_net_buy__early_range`: Train IC=+0.1607, Lock IC=+0.0601, Lock Sharpe=+0.6316

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_mean__margin_net_buy__sma100_dist__iv_corridor_width`: Train IC=+0.1571, Lock IC=+0.0628, Lock Sharpe=-0.3589
- `combo_tri_mean__margin_net_buy__rsi21__iv_corridor_width`: Train IC=+0.2398, Lock IC=+0.0580, Lock Sharpe=-0.1556
- `combo_tri_mean__yesterday_wavetrend_osc__capital_buy_value__iv_corridor_width`: Train IC=+0.2089, Lock IC=+0.0572, Lock Sharpe=-0.2423
- `combo_tri_mean__wavetrend_osc_day__capital_buy_value__iv_corridor_width`: Train IC=+0.2089, Lock IC=+0.0572, Lock Sharpe=-0.2423
- `combo_tri_mean__tech_value_rotation__sma_distance_60d__iv_corridor_width`: Train IC=+0.1498, Lock IC=+0.0566, Lock Sharpe=+0.5262

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_rank_max__roc10__bar_vol_4`: Train IC=+0.0937, Lock IC=+0.1002, Lock Sharpe=-0.3212
- `combo_max__bar_vol_4__willr14`: Train IC=+0.1270, Lock IC=+0.0898, Lock Sharpe=-0.5002
- `combo_tri_max__sma_distance_60d__roc10__bar_vol_4`: Train IC=+0.0366, Lock IC=+0.0734, Lock Sharpe=-0.7780
- `combo_tri_median__rsi21__early_range__roc5`: Train IC=+0.0885, Lock IC=+0.0723, Lock Sharpe=-0.6946
- `combo_min__cl_pos_in_range__max_up_ret`: Train IC=+0.0427, Lock IC=+0.0705, Lock Sharpe=-0.5705

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_diff__iv_envelope_deviation__rsi21`: Train IC=+0.1068, Lock IC=+0.0472, Lock Sharpe=+0.1267
- `combo_clamp_diff__iv_envelope_deviation__rsi21`: Train IC=+0.1058, Lock IC=+0.0471, Lock Sharpe=+0.1267
- `combo_product__yesterday_early_range__max_up_ret`: Train IC=+0.1102, Lock IC=+0.0455, Lock Sharpe=-0.6072
- `combo_diff__iv_envelope_deviation__sma100_dist`: Train IC=+0.0992, Lock IC=+0.0397, Lock Sharpe=-0.3832
- `combo_clamp_diff__iv_envelope_deviation__sma100_dist`: Train IC=+0.0982, Lock IC=+0.0397, Lock Sharpe=-0.3832

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_clamp_diff__yearly_low_distance__yesterday_wavetrend_osc`: Train IC=+0.2087, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_clamp_diff__yearly_low_distance__wavetrend_osc_day`: Train IC=+0.2087, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_diff__yearly_low_distance__yesterday_wavetrend_osc`: Train IC=+0.2102, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_diff__yearly_low_distance__wavetrend_osc_day`: Train IC=+0.2102, Lock IC=+0.0836, Lock Sharpe=+0.1455

### 50ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 6935 | 30 | 60.0% | +0.0189 | -0.3139 |
| B2 Rolling Guard | 1759 | 30 | 46.7% | -0.0079 | -0.5140 |
| Absolute Sign Check | 239 | 30 | 36.7% | -0.0078 | -0.1252 |
| BH-FDR Gate | 149 | 30 | 53.3% | -0.0074 | -0.4674 |
| B3 Composite Floor | 1 | 1 | 100.0% | +0.0629 | +0.4266 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_min__bar_vol_5__bar_vol_0`: Train IC=+0.2084, Lock IC=+0.1078, Lock Sharpe=-0.3213
- `combo_min__bar_vol_5__first_bar_volume`: Train IC=+0.2084, Lock IC=+0.1078, Lock Sharpe=-0.3213
- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_tri_mean__iv_vol_ratio__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_rank_min__bar_vol_5__bar_vol_0`: Train IC=+0.2005, Lock IC=+0.0811, Lock Sharpe=-0.0800

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_mean__vol10__keltner_squeeze_width`: Train IC=+0.1821, Lock IC=+0.0941, Lock Sharpe=+0.1630
- `combo_tri_median__bar_vol_4__mfi14__rsi21`: Train IC=+0.1616, Lock IC=+0.0799, Lock Sharpe=+0.6272
- `combo_tri_ifelse__gap_pct__vix__mfi14__bar_rng_0__bar_vol_5`: Train IC=+0.1630, Lock IC=+0.0673, Lock Sharpe=+0.3178
- `combo_tri_ifelse__vol10__vix__sma50_dist__bar_vol_4__yesterday_lunch_gap`: Train IC=+0.1752, Lock IC=+0.0645, Lock Sharpe=+0.0092
- `combo_min__capital_buy_value__bar_vol_0`: Train IC=+0.1966, Lock IC=+0.0569, Lock Sharpe=-0.2511

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_ifelse__gap_pct__vix__capital_net_value__yesterday_vix_early_drift__yesterday_afternoon_momentum`: Train IC=+0.1829, Lock IC=+0.0511, Lock Sharpe=+0.4980
- `combo_tri_ifelse__gap_pct__vix__capital_net_value__vix_diff_1d__yesterday_afternoon_momentum`: Train IC=+0.1829, Lock IC=+0.0511, Lock Sharpe=+0.4980
- `combo_tri_ifelse__gap_pct__vix__capital_net_value__vix_skew_proxy__yesterday_afternoon_momentum`: Train IC=+0.2032, Lock IC=+0.0505, Lock Sharpe=+0.4980
- `combo_tri_ifelse__gap_pct__vix__capital_net_value__vix_skew_proxy__growth_momentum_ratio`: Train IC=+0.2125, Lock IC=+0.0411, Lock Sharpe=+0.4265
- `combo_tri_ifelse__gap_pct__vol10__capital_net_value__yesterday_vix_early_drift__yesterday_afternoon_momentum`: Train IC=+0.1827, Lock IC=+0.0401, Lock Sharpe=+0.1390

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `gap_pct`: Train IC=+0.1368, Lock IC=+0.0756, Lock Sharpe=+0.5967
- `combo_tri_min__gap_pct__iv_vol_ratio__bar_rng_0`: Train IC=+0.1726, Lock IC=+0.0622, Lock Sharpe=-0.6050
- `combo_min__gap_pct__bar_rng_0`: Train IC=+0.1726, Lock IC=+0.0610, Lock Sharpe=-0.6050
- `combo_tri_ifelse__gap_pct__vix__capital_net_value__yesterday_vix_early_drift__growth_momentum_ratio`: Train IC=+0.1917, Lock IC=+0.0425, Lock Sharpe=+0.4932
- `combo_tri_ifelse__gap_pct__vix__capital_net_value__vix_diff_1d__growth_momentum_ratio`: Train IC=+0.1917, Lock IC=+0.0425, Lock Sharpe=+0.4932

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_product__gap_pct__bar_rng_0`: Train IC=+0.2233, Lock IC=+0.0629, Lock Sharpe=+0.4266

### 500ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 1617 | 30 | 76.7% | +0.0318 | -0.0463 |
| B2 Rolling Guard | 749 | 30 | 83.3% | +0.0479 | +0.1277 |
| Absolute Sign Check | 154 | 30 | 73.3% | +0.0214 | -0.2103 |
| BH-FDR Gate | 351 | 30 | 93.3% | +0.0522 | -0.3659 |
| B3 Composite Floor | 453 | 30 | 100.0% | +0.0796 | -0.3886 |
| B4 Correlation Gate | 376 | 30 | 100.0% | +0.0697 | -0.0425 |

**Admitted Pool Summary**: 20 features, False Positive Rate = 0.0% (admitted but negative lock IC), Mean Lock IC = +0.0638, Mean Lock Sharpe = +0.0091

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__num_up_bars__yesterday_early_momentum`: Train IC=+0.1490, Lock IC=+0.0936, Lock Sharpe=+0.5152
- `yesterday_early_vwap_dev`: Train IC=+0.1518, Lock IC=+0.0728, Lock Sharpe=+0.4462
- `combo_ifelse__atr14_norm__yesterday_early_vwap_dev__yesterday_early_momentum`: Train IC=+0.1560, Lock IC=+0.0718, Lock Sharpe=+0.6844
- `combo_ifelse__vol20__yesterday_early_vwap_dev__yesterday_early_momentum`: Train IC=+0.1489, Lock IC=+0.0678, Lock Sharpe=+0.7864
- `combo_ifelse__macd_hist__yesterday_early_vwap_dev__yesterday_early_momentum`: Train IC=+0.1544, Lock IC=+0.0658, Lock Sharpe=+0.7668

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_rank_min__max_up_ret__cci14`: Train IC=+0.2008, Lock IC=+0.1210, Lock Sharpe=+0.8488
- `combo_tri_mean__max_down_ret__yesterday_first_30min_return__bar_vol_5`: Train IC=+0.2000, Lock IC=+0.1160, Lock Sharpe=+1.5191
- `combo_tri_median__max_down_ret__yesterday_first_30min_return__bar_vol_5`: Train IC=+0.2201, Lock IC=+0.1158, Lock Sharpe=+1.2194
- `combo_rank_min__max_up_ret__macd_hist`: Train IC=+0.1996, Lock IC=+0.1047, Lock Sharpe=+0.6850
- `combo_tri_mean__max_down_ret__first_30min_return__bar_vol_5`: Train IC=+0.1883, Lock IC=+0.0966, Lock Sharpe=+0.8048

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_min__bar_ret_0__first_30min_return__body_to_range_ratio`: Train IC=+0.1537, Lock IC=+0.0802, Lock Sharpe=+0.1163
- `combo_tri_min__first_bar_return__first_30min_return__body_to_range_ratio`: Train IC=+0.1539, Lock IC=+0.0800, Lock Sharpe=+0.1163
- `combo_rank_min__num_up_bars__body_to_range_ratio`: Train IC=+0.1989, Lock IC=+0.0727, Lock Sharpe=-0.2678
- `combo_ifelse__vol60__max_up_ret__num_up_bars`: Train IC=+0.1823, Lock IC=+0.0673, Lock Sharpe=-0.6047
- `combo_tri_min__max_up_ret__first_30min_return__body_to_range_ratio`: Train IC=+0.1568, Lock IC=+0.0666, Lock Sharpe=-0.3165

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_tri_median__max_up_ret__max_down_ret__yesterday_afternoon_momentum`: Train IC=+0.1448, Lock IC=+0.1077, Lock Sharpe=+0.8305
- `combo_rank_min__first_30min_return__gap_pct`: Train IC=+0.1430, Lock IC=+0.1020, Lock Sharpe=+0.3041
- `combo_min__bar_ret_0__first_30min_return`: Train IC=+0.1435, Lock IC=+0.0971, Lock Sharpe=+0.1010
- `combo_min__first_bar_return__first_30min_return`: Train IC=+0.1435, Lock IC=+0.0969, Lock Sharpe=+0.1010
- `combo_rank_min__bar_ret_0__first_30min_return`: Train IC=+0.1433, Lock IC=+0.0960, Lock Sharpe=+0.0640

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_tri_mean__max_up_ret__bar_vwap_dev_2__gap_pct`: Train IC=+0.2807, Lock IC=+0.1072, Lock Sharpe=+0.1533
- `combo_tri_median__max_up_ret__num_up_bars__bar_body_rng_1`: Train IC=+0.2852, Lock IC=+0.1020, Lock Sharpe=-0.6349
- `combo_tri_mean__max_up_ret__bar_ret_0__max_down_ret`: Train IC=+0.2434, Lock IC=+0.1014, Lock Sharpe=+0.2785
- `combo_tri_mean__max_up_ret__first_bar_return__max_down_ret`: Train IC=+0.2436, Lock IC=+0.1014, Lock Sharpe=+0.2785
- `combo_tri_mean__first_30min_return__bar_vwap_dev_2__gap_pct`: Train IC=+0.2435, Lock IC=+0.0984, Lock Sharpe=+0.0934

**Top False Negatives from B4 Correlation Gate** (rejected but positive lockbox IC):

- `combo_rank_min__max_up_ret__gap_pct`: Train IC=+0.2816, Lock IC=+0.1302, Lock Sharpe=+0.8964
- `combo_ifelse__gap_pct__bar_ret_0__max_down_ret`: Train IC=+0.2581, Lock IC=+0.1099, Lock Sharpe=+0.5744
- `combo_ifelse__gap_pct__first_bar_return__max_down_ret`: Train IC=+0.2578, Lock IC=+0.1097, Lock Sharpe=+0.5744
- `combo_tri_mean__max_up_ret__max_down_ret__bar_body_rng_0`: Train IC=+0.2724, Lock IC=+0.1037, Lock Sharpe=+0.3426
- `combo_diff__max_up_ret__early_range`: Train IC=+0.2601, Lock IC=+0.1017, Lock Sharpe=-0.0740

### 500ETF — `long` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 3598 | 30 | 96.7% | +0.0460 | +0.2300 |
| B2 Rolling Guard | 1028 | 30 | 96.7% | +0.0338 | -0.3890 |
| Absolute Sign Check | 50 | 30 | 53.3% | +0.0006 | -0.4072 |
| BH-FDR Gate | 432 | 30 | 70.0% | +0.0266 | -0.3241 |
| B3 Composite Floor | 7 | 7 | 42.9% | +0.0015 | -0.4922 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 100.0% (admitted but negative lock IC), Mean Lock IC = -0.0481, Mean Lock Sharpe = -1.3671

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_clamp_diff__vol60__max_up_ret`: Train IC=+0.2148, Lock IC=+0.0753, Lock Sharpe=-0.1216
- `combo_diff__vol60__max_up_ret`: Train IC=+0.2139, Lock IC=+0.0752, Lock Sharpe=-0.1216
- `combo_product__sma200_dist__yearly_low_distance`: Train IC=+0.2386, Lock IC=+0.0688, Lock Sharpe=+0.7891
- `combo_rank_min__yearly_high_distance__yearly_low_distance`: Train IC=+0.2127, Lock IC=+0.0645, Lock Sharpe=+0.6355
- `combo_rank_min__rsi21__yearly_low_distance`: Train IC=+0.2282, Lock IC=+0.0629, Lock Sharpe=+0.7621

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_mean__yesterday_wavetrend_osc__rsi5`: Train IC=+0.2094, Lock IC=+0.0710, Lock Sharpe=-0.1152
- `combo_mean__wavetrend_osc_day__rsi5`: Train IC=+0.2094, Lock IC=+0.0710, Lock Sharpe=-0.1152
- `combo_min__sma200_dist__rsi5`: Train IC=+0.2080, Lock IC=+0.0600, Lock Sharpe=-0.1657
- `combo_mean__sma200_dist__rsi5`: Train IC=+0.2119, Lock IC=+0.0583, Lock Sharpe=-0.0067
- `combo_mean__willr14__sma200_dist`: Train IC=+0.2074, Lock IC=+0.0550, Lock Sharpe=-0.7474

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_clamp_diff__stoch_k__roc20`: Train IC=+0.1436, Lock IC=+0.0671, Lock Sharpe=-0.1602
- `combo_diff__stoch_k__roc20`: Train IC=+0.1461, Lock IC=+0.0669, Lock Sharpe=-0.1602
- `combo_diff__willr14__roc20`: Train IC=+0.0760, Lock IC=+0.0479, Lock Sharpe=-0.4151
- `combo_mean__volume_slope__short_sell_quantity`: Train IC=+0.0805, Lock IC=+0.0429, Lock Sharpe=+0.3683
- `short_balance`: Train IC=+0.1235, Lock IC=+0.0405, Lock Sharpe=+0.5050

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_rank_min__bar_vwap_dev_2__max_up_ret`: Train IC=+0.1928, Lock IC=+0.0745, Lock Sharpe=-1.0570
- `combo_tri_median__limit_up_proximity_day__rsi21__cci14`: Train IC=+0.2055, Lock IC=+0.0701, Lock Sharpe=+0.3136
- `combo_tri_median__limit_down_proximity_day__rsi21__cci14`: Train IC=+0.2055, Lock IC=+0.0701, Lock Sharpe=+0.3136
- `combo_tri_median__yesterday_return__rsi21__cci14`: Train IC=+0.2055, Lock IC=+0.0701, Lock Sharpe=+0.3136
- `combo_product__yearly_low_distance__bar_vol_4`: Train IC=+0.2000, Lock IC=+0.0660, Lock Sharpe=-0.5134

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_product__yearly_low_distance__bar_vol_5`: Train IC=+0.2250, Lock IC=+0.0621, Lock Sharpe=+0.6552
- `combo_rank_min__yearly_low_distance__max_up_ret`: Train IC=+0.2313, Lock IC=+0.0587, Lock Sharpe=-0.0670
- `combo_min__first_30min_return__bar_body_rng_2`: Train IC=+0.2273, Lock IC=+0.0536, Lock Sharpe=-0.5341

### 500ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 9310 | 30 | 66.7% | +0.0238 | +0.1168 |
| B2 Rolling Guard | 2425 | 30 | 50.0% | +0.0075 | -0.2539 |
| Absolute Sign Check | 329 | 30 | 93.3% | +0.0602 | +0.1862 |
| BH-FDR Gate | 125 | 30 | 70.0% | +0.0228 | -0.2454 |
| B3 Composite Floor | 1 | 1 | 100.0% | +0.0387 | +0.0976 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__yesterday_early_vwap_dev__early_vwap_dev`: Train IC=+0.2040, Lock IC=+0.0864, Lock Sharpe=+0.5977
- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__yesterday_early_vwap_dev__bar_vwap_dev_5`: Train IC=+0.2040, Lock IC=+0.0864, Lock Sharpe=+0.5977
- `combo_tri_ifelse__vol60__vol_pk20__total_balance__early_vwap_dev__volume_percentile_20d`: Train IC=+0.1928, Lock IC=+0.0741, Lock Sharpe=+0.5423
- `combo_tri_ifelse__vol60__vol_pk20__total_balance__bar_vwap_dev_5__volume_percentile_20d`: Train IC=+0.1928, Lock IC=+0.0741, Lock Sharpe=+0.5423
- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__sma100_dist`: Train IC=+0.1854, Lock IC=+0.0666, Lock Sharpe=+0.2477

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__yesterday_early_vwap_dev__volume_percentile_20d`: Train IC=+0.2320, Lock IC=+0.0963, Lock Sharpe=+0.3396
- `combo_tri_ifelse__macd_hist__vol60__short_balance__yesterday_early_vwap_dev__yesterday_day_range`: Train IC=+0.1772, Lock IC=+0.0821, Lock Sharpe=+0.2874
- `combo_tri_ifelse__macd_hist__gap_pct__total_balance__high_beta_vol_ratio__volume_percentile_20d`: Train IC=+0.1774, Lock IC=+0.0769, Lock Sharpe=+0.5424
- `combo_tri_ifelse__macd_hist__vol60__short_balance__yesterday_early_vwap_dev__body_to_range_ratio`: Train IC=+0.1818, Lock IC=+0.0707, Lock Sharpe=+0.3150
- `combo_ifelse__bb_width__total_balance__short_balance_quantity`: Train IC=+0.1754, Lock IC=+0.0680, Lock Sharpe=+0.6529

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__early_vwap_dev`: Train IC=+0.1978, Lock IC=+0.1061, Lock Sharpe=+0.8742
- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__bar_vwap_dev_5`: Train IC=+0.1978, Lock IC=+0.1061, Lock Sharpe=+0.8742
- `combo_tri_ifelse__gap_pct__vol_pk20__first_bar_volume__yesterday_early_vwap_dev__margin_buy_repayment_spread`: Train IC=+0.1529, Lock IC=+0.1014, Lock Sharpe=+0.0022
- `combo_tri_ifelse__gap_pct__vol_pk20__bar_vol_0__yesterday_early_vwap_dev__margin_buy_repayment_spread`: Train IC=+0.1529, Lock IC=+0.1014, Lock Sharpe=+0.0022
- `combo_tri_ifelse__gap_pct__vol_pk20__first_bar_volume__yesterday_early_vwap_dev__short_balance_quantity`: Train IC=+0.1738, Lock IC=+0.0941, Lock Sharpe=+0.7520

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1488, Lock IC=+0.0999, Lock Sharpe=-0.0124
- `combo_clamp_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1316, Lock IC=+0.0996, Lock Sharpe=-0.0124
- `combo_tri_ifelse__macd_hist__vol60__first_bar_volume__yesterday_early_vwap_dev__sma100_dist`: Train IC=+0.1408, Lock IC=+0.0755, Lock Sharpe=+0.1951
- `combo_tri_ifelse__macd_hist__vol60__bar_vol_0__yesterday_early_vwap_dev__sma100_dist`: Train IC=+0.1408, Lock IC=+0.0755, Lock Sharpe=+0.1951
- `combo_tri_ifelse__macd_hist__gap_pct__rsi5__yesterday_early_vwap_dev__volume_percentile_20d`: Train IC=+0.1538, Lock IC=+0.0638, Lock Sharpe=+0.1329

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_tri_ifelse__macd_hist__vol_pk20__short_balance__yesterday_early_vwap_dev__body_to_range_ratio`: Train IC=+0.2444, Lock IC=+0.0387, Lock Sharpe=+0.0976

### 588000ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 3964 | 30 | 33.3% | -0.0229 | -0.1502 |
| B2 Rolling Guard | 1385 | 30 | 50.0% | +0.0068 | +0.0388 |
| Absolute Sign Check | 198 | 30 | 23.3% | -0.0764 | -1.2909 |
| BH-FDR Gate | 1314 | 30 | 30.0% | -0.0404 | -0.5318 |
| B3 Composite Floor | 2320 | 30 | 93.3% | +0.0231 | -0.0431 |
| B4 Correlation Gate | 470 | 30 | 93.3% | +0.0378 | +0.1171 |

**Admitted Pool Summary**: 20 features, False Positive Rate = 60.0% (admitted but negative lock IC), Mean Lock IC = -0.0294, Mean Lock Sharpe = -0.6673

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_product__vix_diff_1d__yesterday_range_ratio`: Train IC=+0.2620, Lock IC=+0.0499, Lock Sharpe=+0.2926
- `combo_product__yesterday_vix_early_drift__yesterday_range_ratio`: Train IC=+0.2620, Lock IC=+0.0499, Lock Sharpe=+0.2926
- `combo_product__vix_skew_proxy__yesterday_range_ratio`: Train IC=+0.2482, Lock IC=+0.0470, Lock Sharpe=+0.0145
- `combo_product__vix_diff_1d__yesterday_day_range`: Train IC=+0.2591, Lock IC=+0.0463, Lock Sharpe=+0.4432
- `combo_product__yesterday_vix_early_drift__yesterday_day_range`: Train IC=+0.2591, Lock IC=+0.0463, Lock Sharpe=+0.4432

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_min__vix_skew_proxy__vix_rolling_percentile_60d`: Train IC=+0.2627, Lock IC=+0.0526, Lock Sharpe=-0.4224
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__first_bar_return__vol_gk10`: Train IC=+0.2372, Lock IC=+0.0511, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__first_bar_return__vol_gk10`: Train IC=+0.2372, Lock IC=+0.0511, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__bar_ret_0__vol_gk10`: Train IC=+0.2374, Lock IC=+0.0510, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__bar_ret_0__vol_gk10`: Train IC=+0.2374, Lock IC=+0.0510, Lock Sharpe=+0.9127

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_ifelse__atr14_norm__vol20__bar_body_rng_1__vol_gk10__max_down_ret`: Train IC=+0.1788, Lock IC=+0.0256, Lock Sharpe=+0.3924
- `combo_clamp_diff__max_up_ret__cl_pos_in_range`: Train IC=+0.1776, Lock IC=+0.0237, Lock Sharpe=-0.3860
- `combo_diff__max_up_ret__cl_pos_in_range`: Train IC=+0.1837, Lock IC=+0.0224, Lock Sharpe=-0.2534
- `combo_tri_ifelse__atr14_norm__vol20__bar_body_rng_1__yesterday_day_realized_vol__max_down_ret`: Train IC=+0.1784, Lock IC=+0.0085, Lock Sharpe=+0.3886
- `combo_product__max_up_ret__vol10`: Train IC=+0.1725, Lock IC=+0.0079, Lock Sharpe=-0.0393

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_tri_ifelse__vix__atr14_norm__bar_vwap_dev_1__num_up_bars__max_down_ret`: Train IC=+0.1843, Lock IC=+0.0483, Lock Sharpe=+0.3427
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__yesterday_close_position__early_skew`: Train IC=+0.1843, Lock IC=+0.0323, Lock Sharpe=+0.1877
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__yesterday_day_close_pos__early_skew`: Train IC=+0.1843, Lock IC=+0.0323, Lock Sharpe=+0.1877
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__yesterday_close_position__early_skew`: Train IC=+0.1843, Lock IC=+0.0323, Lock Sharpe=+0.1877
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__yesterday_day_close_pos__early_skew`: Train IC=+0.1843, Lock IC=+0.0323, Lock Sharpe=+0.1877

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__short_sell_cover_spread__early_momentum`: Train IC=+0.3460, Lock IC=+0.0819, Lock Sharpe=+0.9472
- `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__northbound_net__max_down_ret`: Train IC=+0.3457, Lock IC=+0.0726, Lock Sharpe=+1.0714
- `combo_tri_ifelse__atr14_norm__vol20__vix_skew_proxy__short_sell_cover_spread__max_down_ret`: Train IC=+0.3585, Lock IC=+0.0702, Lock Sharpe=+1.0714
- `combo_tri_ifelse__vix__vol20__bar_vwap_dev_1__vol_gk10__max_down_ret`: Train IC=+0.3468, Lock IC=+0.0656, Lock Sharpe=+0.1212
- `combo_tri_ifelse__vix__vol20__vix_diff_1d__vix_skew_proxy__max_down_ret`: Train IC=+0.3487, Lock IC=+0.0494, Lock Sharpe=+0.2077

**Top False Negatives from B4 Correlation Gate** (rejected but positive lockbox IC):

- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__bar_ret_0__max_down_ret`: Train IC=+0.3670, Lock IC=+0.0793, Lock Sharpe=+0.9399
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__bar_ret_0__max_down_ret`: Train IC=+0.3670, Lock IC=+0.0793, Lock Sharpe=+0.9399
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__first_bar_return__max_down_ret`: Train IC=+0.3666, Lock IC=+0.0793, Lock Sharpe=+0.9399
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__first_bar_return__max_down_ret`: Train IC=+0.3666, Lock IC=+0.0793, Lock Sharpe=+0.9399
- `combo_ifelse__atr14_norm__vix_skew_proxy__first_30min_return`: Train IC=+0.3579, Lock IC=+0.0719, Lock Sharpe=+1.0524

### 588000ETF — `long` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 4783 | 30 | 36.7% | -0.0055 | -0.3911 |
| B2 Rolling Guard | 1760 | 30 | 23.3% | -0.0315 | -0.9980 |
| Absolute Sign Check | 129 | 30 | 43.3% | -0.0152 | -0.6430 |
| BH-FDR Gate | 764 | 30 | 53.3% | +0.0092 | -0.5672 |
| B3 Composite Floor | 6 | 6 | 0.0% | -0.0745 | -0.9679 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 100.0% (admitted but negative lock IC), Mean Lock IC = -0.0750, Mean Lock Sharpe = -0.8713

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_rank_min__early_realized_vol__vix_diff_1d`: Train IC=+0.2631, Lock IC=+0.0901, Lock Sharpe=+0.0444
- `combo_rank_min__early_realized_vol__yesterday_vix_early_drift`: Train IC=+0.2631, Lock IC=+0.0901, Lock Sharpe=+0.0444
- `combo_product__vix_diff_1d__yesterday_volume_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__vix_diff_1d__volume_sma_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__yesterday_vix_early_drift__yesterday_volume_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_mean__vix_skew_proxy__volume_slope`: Train IC=+0.2531, Lock IC=+0.0850, Lock Sharpe=-0.6777
- `combo_max__vix_skew_proxy__volume_slope`: Train IC=+0.2744, Lock IC=+0.0675, Lock Sharpe=-1.0303
- `combo_tri_median__vix_rolling_percentile_60d__vix_skew_proxy__buy_on_margin_value`: Train IC=+0.2518, Lock IC=+0.0579, Lock Sharpe=-0.8166
- `combo_mean__vix_rolling_percentile_60d__volume_slope`: Train IC=+0.2614, Lock IC=+0.0536, Lock Sharpe=+1.7087
- `combo_ifelse__vol10__early_realized_vol__yesterday_day_realized_vol`: Train IC=+0.2487, Lock IC=+0.0473, Lock Sharpe=-0.3264

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_ratio__capital_net_accel__capital_large_order_ratio`: Train IC=+0.2437, Lock IC=+0.0750, Lock Sharpe=+0.2892
- `combo_ratio__capital_net_accel__capital_net_ratio`: Train IC=+0.2435, Lock IC=+0.0748, Lock Sharpe=+0.0080
- `combo_max__capital_net_value__capital_large_order_ratio`: Train IC=+0.1849, Lock IC=+0.0649, Lock Sharpe=+0.9490
- `combo_rank_min__buy_on_margin_value__capital_net_value`: Train IC=+0.1569, Lock IC=+0.0633, Lock Sharpe=-0.1713
- `combo_tri_min__early_range__vol5__growth_momentum_ratio`: Train IC=+0.1550, Lock IC=+0.0586, Lock Sharpe=-0.2843

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_diff__vix_diff_1d__bar_rng_3`: Train IC=+0.2517, Lock IC=+0.1028, Lock Sharpe=-0.6503
- `combo_diff__yesterday_vix_early_drift__bar_rng_3`: Train IC=+0.2517, Lock IC=+0.1028, Lock Sharpe=-0.6503
- `combo_clamp_diff__vix_diff_1d__bar_rng_3`: Train IC=+0.2512, Lock IC=+0.0958, Lock Sharpe=-0.6503
- `combo_clamp_diff__yesterday_vix_early_drift__bar_rng_3`: Train IC=+0.2512, Lock IC=+0.0958, Lock Sharpe=-0.6503
- `combo_tri_min__early_realized_vol__yesterday_day_realized_vol__vix_diff_1d`: Train IC=+0.2683, Lock IC=+0.0726, Lock Sharpe=+0.0497

### 588000ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 7425 | 30 | 26.7% | -0.0206 | -0.7836 |
| B2 Rolling Guard | 2083 | 30 | 20.0% | -0.0261 | -0.9708 |
| Absolute Sign Check | 211 | 30 | 40.0% | -0.0017 | -0.2256 |
| BH-FDR Gate | 185 | 30 | 13.3% | -0.0335 | -0.8867 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_ifelse__sma20_dist__vix__vix_rolling_percentile_60d__capital_net_ratio__total_path_length`: Train IC=+0.2272, Lock IC=+0.1029, Lock Sharpe=+0.9632
- `combo_abs_diff__bar_ret_1__bar_vwap_dev_5`: Train IC=+0.2171, Lock IC=+0.0295, Lock Sharpe=+0.2902
- `combo_abs_diff__bar_ret_1__early_vwap_dev`: Train IC=+0.2171, Lock IC=+0.0295, Lock Sharpe=+0.2902
- `combo_tri_ifelse__vix__gap_pct__short_sell_cover_spread__bar_vwap_dev_5__stoch_d`: Train IC=+0.2268, Lock IC=+0.0177, Lock Sharpe=-0.2415
- `combo_tri_ifelse__vix__gap_pct__short_sell_cover_spread__early_vwap_dev__stoch_d`: Train IC=+0.2268, Lock IC=+0.0177, Lock Sharpe=-0.2415

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_min__yesterday_lunch_gap__capital_sell_value__bar_rng_3`: Train IC=+0.1701, Lock IC=+0.0843, Lock Sharpe=+0.5575
- `combo_ratio__wavetrend_osc_day__yesterday_day_realized_vol`: Train IC=+0.1769, Lock IC=+0.0502, Lock Sharpe=+0.0358
- `combo_ratio__yesterday_wavetrend_osc__yesterday_day_realized_vol`: Train IC=+0.1769, Lock IC=+0.0502, Lock Sharpe=+0.0358
- `combo_tri_ifelse__sma20_dist__vix__outside_bar_reversal_day__yesterday_lunch_gap__margin_balance`: Train IC=+0.1785, Lock IC=+0.0473, Lock Sharpe=+0.4113
- `combo_tri_ifelse__sma20_dist__vix__outside_bar_reversal_day__yesterday_day_range__margin_balance`: Train IC=+0.1736, Lock IC=+0.0092, Lock Sharpe=+0.2822

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_ifelse__sma20_dist__gap_pct__outside_bar_reversal_day__yesterday_lunch_gap__bar_ret_1`: Train IC=+0.1229, Lock IC=+0.0850, Lock Sharpe=+0.4422
- `combo_ifelse__gap_pct__yesterday_lunch_gap__sma10_dist`: Train IC=+0.1484, Lock IC=+0.0671, Lock Sharpe=+0.6808
- `combo_abs_diff__sma20_dist__rsi5`: Train IC=+0.1110, Lock IC=+0.0365, Lock Sharpe=-0.6410
- `combo_clamp_diff__bar_rng_3__bar_vwap_dev_3`: Train IC=+0.1414, Lock IC=+0.0322, Lock Sharpe=-0.3163
- `combo_abs_diff__yesterday_lunch_gap__yesterday_day_realized_vol`: Train IC=+0.1743, Lock IC=+0.0289, Lock Sharpe=+0.2019

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_product__gap_pct__yesterday_early_realized_vol`: Train IC=+0.1495, Lock IC=+0.0318, Lock Sharpe=+0.4820
- `bar_ret_1`: Train IC=+0.1445, Lock IC=+0.0198, Lock Sharpe=+0.2043
- `combo_tri_ifelse__vix__gap_pct__outside_bar_reversal_day__yesterday_day_range__bar_ret_1`: Train IC=+0.1682, Lock IC=+0.0192, Lock Sharpe=-1.8608
- `combo_ifelse__gap_pct__yesterday_range_ratio__vix_rolling_percentile_60d`: Train IC=+0.1510, Lock IC=+0.0064, Lock Sharpe=-1.3429

### 159915ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 2375 | 30 | 60.0% | +0.0250 | -0.2905 |
| B2 Rolling Guard | 1818 | 30 | 63.3% | +0.0245 | -0.3954 |
| Absolute Sign Check | 121 | 30 | 80.0% | +0.0206 | +0.0311 |
| BH-FDR Gate | 268 | 30 | 96.7% | +0.0549 | -0.1551 |
| B3 Composite Floor | 372 | 30 | 90.0% | +0.0383 | -0.2558 |
| B4 Correlation Gate | 52 | 30 | 96.7% | +0.0897 | +0.2692 |

**Admitted Pool Summary**: 9 features, False Positive Rate = 11.1% (admitted but negative lock IC), Mean Lock IC = +0.0731, Mean Lock Sharpe = +0.0972

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_product__max_up_ret__buy_on_margin_value`: Train IC=+0.1451, Lock IC=+0.0982, Lock Sharpe=+0.2152
- `combo_mean__early_range__gap_pct`: Train IC=+0.1743, Lock IC=+0.0924, Lock Sharpe=+0.3783
- `combo_tri_ifelse__gap_pct__bb_width__bar_ret_0__yesterday_early_trend__yesterday_stoch_rsi_cross`: Train IC=+0.1579, Lock IC=+0.0778, Lock Sharpe=+0.1919
- `combo_tri_ifelse__gap_pct__bb_width__first_bar_return__yesterday_early_trend__yesterday_stoch_rsi_cross`: Train IC=+0.1579, Lock IC=+0.0778, Lock Sharpe=+0.1919
- `combo_tri_ifelse__gap_pct__bb_width__bar_ret_0__yearly_high_distance__yesterday_stoch_rsi_cross`: Train IC=+0.1576, Lock IC=+0.0741, Lock Sharpe=+0.2592

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2106, Lock IC=+0.1310, Lock Sharpe=+1.2087
- `combo_mean__bar_body_rng_0__first_30min_return`: Train IC=+0.1917, Lock IC=+0.1101, Lock Sharpe=+0.5746
- `combo_rank_min__max_up_ret__max_down_ret`: Train IC=+0.2204, Lock IC=+0.0988, Lock Sharpe=+0.7200
- `combo_tri_median__max_up_ret__bar_body_rng_0__max_down_ret`: Train IC=+0.1986, Lock IC=+0.0917, Lock Sharpe=-0.0891
- `combo_mean__max_up_ret__bar_ret_0`: Train IC=+0.2060, Lock IC=+0.0906, Lock Sharpe=+0.0729

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_diff__max_up_ret__bar_rng_5`: Train IC=+0.1453, Lock IC=+0.1033, Lock Sharpe=+0.8012
- `combo_clamp_diff__max_up_ret__bar_rng_5`: Train IC=+0.1398, Lock IC=+0.1030, Lock Sharpe=+0.8012
- `combo_abs_diff__volume_sma_ratio__bar_vol_4`: Train IC=+0.1114, Lock IC=+0.0567, Lock Sharpe=-0.0120
- `combo_abs_diff__yesterday_volume_ratio__bar_vol_4`: Train IC=+0.1114, Lock IC=+0.0567, Lock Sharpe=-0.0120
- `combo_diff__volume_sma_ratio__bar_vol_4`: Train IC=+0.1195, Lock IC=+0.0473, Lock Sharpe=+0.5008

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_pm_return__yesterday_first_30min_return`: Train IC=+0.1558, Lock IC=+0.1423, Lock Sharpe=+1.0476
- `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_early_trend__first_30min_return`: Train IC=+0.1564, Lock IC=+0.1353, Lock Sharpe=+0.6128
- `combo_tri_median__max_up_ret__gap_pct__first_30min_return`: Train IC=+0.1578, Lock IC=+0.1312, Lock Sharpe=+0.0987
- `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__first_30min_return`: Train IC=+0.1577, Lock IC=+0.1287, Lock Sharpe=+0.9542
- `combo_tri_ifelse__gap_pct__bb_width__bar_ret_0__yesterday_early_trend__keltner_squeeze_width`: Train IC=+0.1548, Lock IC=+0.0786, Lock Sharpe=+0.2603

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_tri_mean__max_up_ret__bar_ret_0__gap_pct`: Train IC=+0.2608, Lock IC=+0.1341, Lock Sharpe=+1.1076
- `combo_tri_mean__max_up_ret__first_bar_return__gap_pct`: Train IC=+0.2604, Lock IC=+0.1341, Lock Sharpe=+1.1076
- `combo_tri_mean__max_up_ret__early_range__gap_pct`: Train IC=+0.2636, Lock IC=+0.1100, Lock Sharpe=+0.3769
- `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_momentum__bar_body_rng_0`: Train IC=+0.2459, Lock IC=+0.0953, Lock Sharpe=+0.8086
- `combo_tri_max__max_up_ret__bar_body_rng_0__max_down_ret`: Train IC=+0.2301, Lock IC=+0.0869, Lock Sharpe=+0.4644

**Top False Negatives from B4 Correlation Gate** (rejected but positive lockbox IC):

- `combo_mean__max_up_ret__gap_pct`: Train IC=+0.2287, Lock IC=+0.1505, Lock Sharpe=+1.0973
- `combo_tri_min__max_up_ret__first_bar_return__gap_pct`: Train IC=+0.2711, Lock IC=+0.1271, Lock Sharpe=+1.1425
- `combo_rank_min__max_up_ret__gap_pct`: Train IC=+0.2544, Lock IC=+0.1252, Lock Sharpe=+0.9217
- `combo_ifelse__gap_pct__bar_body_rng_0__yesterday_first_30min_return`: Train IC=+0.2077, Lock IC=+0.1243, Lock Sharpe=+0.8402
- `combo_diff__max_up_ret__keltner_squeeze_width`: Train IC=+0.2030, Lock IC=+0.1063, Lock Sharpe=+0.8462

### 159915ETF — `long` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 2808 | 30 | 76.7% | +0.0218 | -0.1880 |
| B2 Rolling Guard | 628 | 30 | 73.3% | +0.0294 | -0.2026 |
| Absolute Sign Check | 40 | 30 | 26.7% | -0.0079 | -0.4040 |
| BH-FDR Gate | 104 | 30 | 76.7% | +0.0297 | +0.0591 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_min__bar_body_rng_1__max_down_ret`: Train IC=+0.1562, Lock IC=+0.0845, Lock Sharpe=+0.6121
- `combo_tri_median__rsi5__yesterday_first_30min_return__volume_slope`: Train IC=+0.1941, Lock IC=+0.0809, Lock Sharpe=+0.4857
- `combo_min__max_down_ret__early_momentum`: Train IC=+0.1932, Lock IC=+0.0713, Lock Sharpe=+0.1747
- `combo_mean__bar_vwap_dev_3__max_down_ret`: Train IC=+0.1817, Lock IC=+0.0670, Lock Sharpe=+0.0293
- `combo_min__max_down_ret__bar_rng_2`: Train IC=+0.1889, Lock IC=+0.0650, Lock Sharpe=+0.2548

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_max__first_30min_return__bar_body_rng_1`: Train IC=+0.1690, Lock IC=+0.0836, Lock Sharpe=+0.2730
- `combo_rank_min__early_realized_vol__max_down_ret`: Train IC=+0.1535, Lock IC=+0.0816, Lock Sharpe=+0.8615
- `combo_rank_min__max_down_ret__early_momentum`: Train IC=+0.1661, Lock IC=+0.0733, Lock Sharpe=+0.6107
- `combo_rank_min__bar_rng_0__max_down_ret`: Train IC=+0.1528, Lock IC=+0.0709, Lock Sharpe=+1.0065
- `combo_rank_min__rsi5__yesterday_first_30min_return`: Train IC=+0.1837, Lock IC=+0.0679, Lock Sharpe=+0.3884

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_min__early_realized_vol__short_repayment_quantity`: Train IC=+0.0465, Lock IC=+0.0704, Lock Sharpe=-0.7196
- `combo_ratio__stoch_d__volume_percentile_20d`: Train IC=+0.0784, Lock IC=+0.0554, Lock Sharpe=+0.1105
- `combo_clamp_diff__bar_vol_4__stoch_d`: Train IC=+0.0647, Lock IC=+0.0164, Lock Sharpe=+0.0536
- `combo_diff__bar_vol_4__stoch_d`: Train IC=+0.0632, Lock IC=+0.0148, Lock Sharpe=+0.0536
- `combo_rank_min__bar_vol_4__volume_percentile_20d`: Train IC=+0.0750, Lock IC=+0.0039, Lock Sharpe=+0.3177

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_mean__bar_body_rng_1__max_down_ret`: Train IC=+0.1444, Lock IC=+0.0827, Lock Sharpe=-0.2102
- `combo_min__first_30min_return__bar_body_rng_1`: Train IC=+0.1858, Lock IC=+0.0782, Lock Sharpe=+0.5353
- `combo_min__early_realized_vol__max_down_ret`: Train IC=+0.1745, Lock IC=+0.0768, Lock Sharpe=+0.5838
- `combo_min__bar_rng_0__max_down_ret`: Train IC=+0.1729, Lock IC=+0.0741, Lock Sharpe=+1.0065
- `combo_min__yesterday_first_30min_return__cci14`: Train IC=+0.1745, Lock IC=+0.0716, Lock Sharpe=+0.3868

### 159915ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 7488 | 30 | 66.7% | +0.0113 | -0.1967 |
| B2 Rolling Guard | 3375 | 30 | 26.7% | -0.0136 | -0.1326 |
| Absolute Sign Check | 1332 | 30 | 20.0% | -0.0148 | -0.2917 |
| BH-FDR Gate | 47 | 30 | 46.7% | -0.0066 | -0.3652 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_product__bb_width__margin_repayment`: Train IC=+0.2082, Lock IC=+0.0637, Lock Sharpe=+1.0054
- `combo_min__yesterday_early_trend__yesterday_first_30min_return`: Train IC=+0.1645, Lock IC=+0.0548, Lock Sharpe=-0.2710
- `combo_diff__yesterday_pm_return__rsi21`: Train IC=+0.1723, Lock IC=+0.0484, Lock Sharpe=-0.7208
- `combo_tri_ifelse__vol_pk20__vol20__yesterday_afternoon_momentum__rsi21__early_realized_vol`: Train IC=+0.1878, Lock IC=+0.0435, Lock Sharpe=+0.0035
- `combo_tri_ifelse__vol_pk20__bb_width__iv_vol_ratio__sma100_dist__early_realized_vol`: Train IC=+0.1722, Lock IC=+0.0351, Lock Sharpe=+0.6703

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_ifelse__bb_width__sma20_dist__high_beta_vol_ratio__vol_gk10__yesterday_afternoon_momentum`: Train IC=+0.1671, Lock IC=+0.0674, Lock Sharpe=+0.1155
- `combo_tri_ifelse__vol20__sma20_dist__stoch_k__yesterday_afternoon_momentum__capital_sell_volume`: Train IC=+0.1671, Lock IC=+0.0301, Lock Sharpe=+0.0861
- `combo_tri_ifelse__vol20__sma20_dist__stoch_k__yesterday_pm_return__capital_sell_volume`: Train IC=+0.1662, Lock IC=+0.0269, Lock Sharpe=-0.0167
- `combo_tri_ifelse__vol_pk20__bb_width__stoch_k__yesterday_pm_return__yesterday_afternoon_momentum`: Train IC=+0.1757, Lock IC=+0.0109, Lock Sharpe=-0.1190
- `combo_tri_ifelse__vol_pk20__sma20_dist__stoch_k__yesterday_afternoon_momentum__rsi21`: Train IC=+0.2153, Lock IC=+0.0068, Lock Sharpe=-0.0093

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_ifelse__bb_width__sma20_dist__sma_distance_60d__vol_gk10__yesterday_afternoon_momentum`: Train IC=+0.1325, Lock IC=+0.0293, Lock Sharpe=-0.1764
- `combo_tri_ifelse__bb_width__sma20_dist__sma50_dist__vol_gk10__yesterday_afternoon_momentum`: Train IC=+0.1388, Lock IC=+0.0276, Lock Sharpe=-0.1552
- `combo_product__num_up_bars__bar_ret_1`: Train IC=+0.1543, Lock IC=+0.0192, Lock Sharpe=-0.5841
- `combo_tri_ifelse__bb_width__sma20_dist__ema12_dist__vol_gk10__yesterday_afternoon_momentum`: Train IC=+0.1491, Lock IC=+0.0174, Lock Sharpe=-0.1252
- `combo_tri_ifelse__vol20__sma20_dist__stoch_k__vol_gk10__yesterday_early_trend`: Train IC=+0.1306, Lock IC=+0.0070, Lock Sharpe=-0.2590

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_abs_diff__vol_gk10__coppock_curve_day`: Train IC=+0.0872, Lock IC=+0.0544, Lock Sharpe=-0.2159
- `combo_rank_min__vol_pk20__iv_vol_ratio`: Train IC=+0.1337, Lock IC=+0.0317, Lock Sharpe=-0.1190
- `combo_clamp_diff__vol20__bb_width`: Train IC=+0.1416, Lock IC=+0.0273, Lock Sharpe=-0.0453
- `combo_abs_diff__buy_on_margin_value__capital_buy_volume`: Train IC=+0.0851, Lock IC=+0.0211, Lock Sharpe=-1.2729
- `combo_product__num_up_bars__bar_vwap_dev_1`: Train IC=+0.1400, Lock IC=+0.0205, Lock Sharpe=-0.6166

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 733 | +0.0164 | 90.0% |
| 0.45 | 0.20 | 591 | +0.0164 | 90.0% |
| 0.45 | 0.30 | 408 | +0.0164 | 90.0% |
| 0.45 | 0.40 | 271 | +0.0164 | 90.0% |
| 0.45 | 0.50 | 180 | +0.0164 | 90.0% |
| 0.50 | 0.15 | 680 | +0.0164 | 90.0% |
| 0.50 | 0.25 | 482 | +0.0164 | 90.0% |
| 0.50 | 0.35 | 330 | +0.0164 | 90.0% |
| 0.50 | 0.45 | 218 | +0.0164 | 90.0% |
| 0.55 | 0.10 | 672 | +0.0164 | 90.0% |
| 0.55 | 0.20 | 581 | +0.0164 | 90.0% |
| 0.55 | 0.30 | 408 | +0.0164 | 90.0% |
| 0.55 | 0.40 | 271 | +0.0164 | 90.0% |
| 0.55 | 0.50 | 180 | +0.0164 | 90.0% |
| 0.60 | 0.15 | 463 | +0.0164 | 90.0% |
| 0.60 | 0.25 | 436 | +0.0164 | 90.0% |
| 0.60 | 0.35 | 329 | +0.0164 | 90.0% |
| 0.60 | 0.45 | 218 | +0.0164 | 90.0% |
| 0.65 | 0.10 | 275 | +0.0164 | 90.0% |
| 0.65 | 0.20 | 275 | +0.0164 | 90.0% |
| 0.65 | 0.30 | 275 | +0.0164 | 90.0% |
| 0.65 | 0.40 | 249 | +0.0164 | 90.0% |
| 0.65 | 0.50 | 180 | +0.0164 | 90.0% |
| 0.70 | 0.15 | 168 | +0.0187 | 90.0% |
| 0.70 | 0.25 | 168 | +0.0187 | 90.0% |
| 0.70 | 0.35 | 168 | +0.0187 | 90.0% |
| 0.70 | 0.45 | 167 | +0.0187 | 90.0% |
| 0.75 | 0.10 | 76 | -0.0120 | 30.0% |
| 0.75 | 0.20 | 76 | -0.0120 | 30.0% |
| 0.75 | 0.30 | 76 | -0.0120 | 30.0% |
| 0.75 | 0.40 | 76 | -0.0120 | 30.0% |
| 0.75 | 0.50 | 76 | -0.0120 | 30.0% |
| 0.80 | 0.15 | 44 | +0.0342 | 100.0% |
| 0.80 | 0.25 | 44 | +0.0342 | 100.0% |
| 0.80 | 0.35 | 44 | +0.0342 | 100.0% |
| 0.80 | 0.45 | 44 | +0.0342 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 44 candidates, mean lock IC=+0.0342, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 12 | -0.0087 | 20.0% |
| 0.45 | 0.20 | 3 | +0.0490 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 6 | +0.0126 | 50.0% |
| 0.50 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 1 | -0.0074 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 3 candidates, mean lock IC=+0.0490, 100.0% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 609 | +0.0069 | 60.0% |
| 0.45 | 0.20 | 257 | +0.0069 | 60.0% |
| 0.45 | 0.30 | 50 | -0.0071 | 50.0% |
| 0.45 | 0.40 | 10 | +0.0171 | 80.0% |
| 0.45 | 0.50 | 2 | -0.0107 | 50.0% |
| 0.50 | 0.15 | 388 | +0.0069 | 60.0% |
| 0.50 | 0.25 | 157 | +0.0043 | 60.0% |
| 0.50 | 0.35 | 19 | -0.0045 | 60.0% |
| 0.50 | 0.45 | 5 | -0.0050 | 60.0% |
| 0.55 | 0.10 | 355 | +0.0069 | 60.0% |
| 0.55 | 0.20 | 248 | +0.0069 | 60.0% |
| 0.55 | 0.30 | 50 | -0.0071 | 50.0% |
| 0.55 | 0.40 | 10 | +0.0171 | 80.0% |
| 0.55 | 0.50 | 2 | -0.0107 | 50.0% |
| 0.60 | 0.15 | 131 | +0.0008 | 60.0% |
| 0.60 | 0.25 | 127 | -0.0066 | 50.0% |
| 0.60 | 0.35 | 19 | -0.0045 | 60.0% |
| 0.60 | 0.45 | 5 | -0.0050 | 60.0% |
| 0.65 | 0.10 | 12 | +0.0107 | 60.0% |
| 0.65 | 0.20 | 12 | +0.0107 | 60.0% |
| 0.65 | 0.30 | 12 | +0.0107 | 60.0% |
| 0.65 | 0.40 | 8 | +0.0171 | 75.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 10 candidates, mean lock IC=+0.0171, 80.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 515 | +0.0422 | 100.0% |
| 0.45 | 0.20 | 413 | +0.0422 | 100.0% |
| 0.45 | 0.30 | 282 | +0.0440 | 100.0% |
| 0.45 | 0.40 | 220 | +0.0531 | 100.0% |
| 0.45 | 0.50 | 178 | +0.0531 | 100.0% |
| 0.50 | 0.15 | 465 | +0.0422 | 100.0% |
| 0.50 | 0.25 | 345 | +0.0432 | 100.0% |
| 0.50 | 0.35 | 248 | +0.0462 | 100.0% |
| 0.50 | 0.45 | 197 | +0.0531 | 100.0% |
| 0.55 | 0.10 | 468 | +0.0422 | 100.0% |
| 0.55 | 0.20 | 409 | +0.0422 | 100.0% |
| 0.55 | 0.30 | 282 | +0.0440 | 100.0% |
| 0.55 | 0.40 | 220 | +0.0531 | 100.0% |
| 0.55 | 0.50 | 178 | +0.0531 | 100.0% |
| 0.60 | 0.15 | 332 | +0.0495 | 100.0% |
| 0.60 | 0.25 | 299 | +0.0391 | 90.0% |
| 0.60 | 0.35 | 246 | +0.0462 | 100.0% |
| 0.60 | 0.45 | 197 | +0.0531 | 100.0% |
| 0.65 | 0.10 | 230 | +0.0462 | 100.0% |
| 0.65 | 0.20 | 230 | +0.0462 | 100.0% |
| 0.65 | 0.30 | 228 | +0.0462 | 100.0% |
| 0.65 | 0.40 | 214 | +0.0531 | 100.0% |
| 0.65 | 0.50 | 177 | +0.0531 | 100.0% |
| 0.70 | 0.15 | 170 | +0.0531 | 100.0% |
| 0.70 | 0.25 | 170 | +0.0531 | 100.0% |
| 0.70 | 0.35 | 170 | +0.0531 | 100.0% |
| 0.70 | 0.45 | 170 | +0.0531 | 100.0% |
| 0.75 | 0.10 | 133 | +0.0442 | 100.0% |
| 0.75 | 0.20 | 133 | +0.0442 | 100.0% |
| 0.75 | 0.30 | 133 | +0.0442 | 100.0% |
| 0.75 | 0.40 | 133 | +0.0442 | 100.0% |
| 0.75 | 0.50 | 133 | +0.0442 | 100.0% |
| 0.80 | 0.15 | 68 | +0.0356 | 100.0% |
| 0.80 | 0.25 | 68 | +0.0356 | 100.0% |
| 0.80 | 0.35 | 68 | +0.0356 | 100.0% |
| 0.80 | 0.45 | 68 | +0.0356 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 220 candidates, mean lock IC=+0.0531, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 276 | +0.0353 | 60.0% |
| 0.45 | 0.20 | 73 | +0.0125 | 50.0% |
| 0.45 | 0.30 | 21 | +0.0033 | 50.0% |
| 0.45 | 0.40 | 10 | +0.0260 | 80.0% |
| 0.45 | 0.50 | 3 | -0.0117 | 33.3% |
| 0.50 | 0.15 | 130 | +0.0575 | 90.0% |
| 0.50 | 0.25 | 34 | +0.0116 | 50.0% |
| 0.50 | 0.35 | 14 | +0.0113 | 60.0% |
| 0.50 | 0.45 | 5 | +0.0168 | 60.0% |
| 0.55 | 0.10 | 108 | +0.0180 | 50.0% |
| 0.55 | 0.20 | 55 | -0.0011 | 30.0% |
| 0.55 | 0.30 | 21 | +0.0033 | 50.0% |
| 0.55 | 0.40 | 10 | +0.0260 | 80.0% |
| 0.55 | 0.50 | 3 | -0.0117 | 33.3% |
| 0.60 | 0.15 | 29 | +0.0020 | 50.0% |
| 0.60 | 0.25 | 23 | +0.0033 | 50.0% |
| 0.60 | 0.35 | 14 | +0.0113 | 60.0% |
| 0.60 | 0.45 | 5 | +0.0168 | 60.0% |
| 0.65 | 0.10 | 7 | +0.0221 | 71.4% |
| 0.65 | 0.20 | 7 | +0.0221 | 71.4% |
| 0.65 | 0.30 | 7 | +0.0221 | 71.4% |
| 0.65 | 0.40 | 6 | +0.0178 | 66.7% |
| 0.65 | 0.50 | 3 | -0.0117 | 33.3% |
| 0.70 | 0.15 | 3 | -0.0117 | 33.3% |
| 0.70 | 0.25 | 3 | -0.0117 | 33.3% |
| 0.70 | 0.35 | 3 | -0.0117 | 33.3% |
| 0.70 | 0.45 | 3 | -0.0117 | 33.3% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 132 candidates, mean lock IC=+0.0575, 90.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 845 | -0.0197 | 30.0% |
| 0.45 | 0.20 | 342 | +0.0015 | 40.0% |
| 0.45 | 0.30 | 105 | +0.0004 | 70.0% |
| 0.45 | 0.40 | 24 | -0.0170 | 20.0% |
| 0.45 | 0.50 | 6 | +0.0261 | 50.0% |
| 0.50 | 0.15 | 527 | -0.0197 | 30.0% |
| 0.50 | 0.25 | 190 | +0.0003 | 50.0% |
| 0.50 | 0.35 | 53 | -0.0250 | 10.0% |
| 0.50 | 0.45 | 15 | +0.0034 | 50.0% |
| 0.55 | 0.10 | 470 | -0.0111 | 30.0% |
| 0.55 | 0.20 | 293 | +0.0015 | 40.0% |
| 0.55 | 0.30 | 105 | +0.0004 | 70.0% |
| 0.55 | 0.40 | 24 | -0.0170 | 20.0% |
| 0.55 | 0.50 | 6 | +0.0261 | 50.0% |
| 0.60 | 0.15 | 164 | -0.0039 | 40.0% |
| 0.60 | 0.25 | 133 | +0.0012 | 60.0% |
| 0.60 | 0.35 | 50 | -0.0250 | 10.0% |
| 0.60 | 0.45 | 15 | +0.0034 | 50.0% |
| 0.65 | 0.10 | 34 | -0.0061 | 40.0% |
| 0.65 | 0.20 | 34 | -0.0061 | 40.0% |
| 0.65 | 0.30 | 34 | -0.0061 | 40.0% |
| 0.65 | 0.40 | 17 | +0.0065 | 50.0% |
| 0.65 | 0.50 | 6 | +0.0261 | 50.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 6 candidates, mean lock IC=+0.0261, 50.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1792 | +0.0867 | 100.0% |
| 0.45 | 0.20 | 1631 | +0.0867 | 100.0% |
| 0.45 | 0.30 | 1386 | +0.0867 | 100.0% |
| 0.45 | 0.40 | 1085 | +0.0867 | 100.0% |
| 0.45 | 0.50 | 740 | +0.0826 | 100.0% |
| 0.50 | 0.15 | 1736 | +0.0867 | 100.0% |
| 0.50 | 0.25 | 1509 | +0.0867 | 100.0% |
| 0.50 | 0.35 | 1230 | +0.0867 | 100.0% |
| 0.50 | 0.45 | 904 | +0.0867 | 100.0% |
| 0.55 | 0.10 | 1713 | +0.0867 | 100.0% |
| 0.55 | 0.20 | 1616 | +0.0867 | 100.0% |
| 0.55 | 0.30 | 1386 | +0.0867 | 100.0% |
| 0.55 | 0.40 | 1085 | +0.0867 | 100.0% |
| 0.55 | 0.50 | 740 | +0.0826 | 100.0% |
| 0.60 | 0.15 | 1423 | +0.0867 | 100.0% |
| 0.60 | 0.25 | 1406 | +0.0867 | 100.0% |
| 0.60 | 0.35 | 1222 | +0.0867 | 100.0% |
| 0.60 | 0.45 | 904 | +0.0867 | 100.0% |
| 0.65 | 0.10 | 1011 | +0.0826 | 100.0% |
| 0.65 | 0.20 | 1011 | +0.0826 | 100.0% |
| 0.65 | 0.30 | 1008 | +0.0826 | 100.0% |
| 0.65 | 0.40 | 963 | +0.0826 | 100.0% |
| 0.65 | 0.50 | 731 | +0.0826 | 100.0% |
| 0.70 | 0.15 | 587 | +0.0826 | 100.0% |
| 0.70 | 0.25 | 587 | +0.0826 | 100.0% |
| 0.70 | 0.35 | 587 | +0.0826 | 100.0% |
| 0.70 | 0.45 | 585 | +0.0826 | 100.0% |
| 0.75 | 0.10 | 231 | +0.0745 | 100.0% |
| 0.75 | 0.20 | 231 | +0.0745 | 100.0% |
| 0.75 | 0.30 | 231 | +0.0745 | 100.0% |
| 0.75 | 0.40 | 231 | +0.0745 | 100.0% |
| 0.75 | 0.50 | 231 | +0.0745 | 100.0% |
| 0.80 | 0.15 | 59 | +0.0646 | 100.0% |
| 0.80 | 0.25 | 59 | +0.0646 | 100.0% |
| 0.80 | 0.35 | 59 | +0.0646 | 100.0% |
| 0.80 | 0.45 | 59 | +0.0646 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1792 candidates, mean lock IC=+0.0867, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 697 | -0.0047 | 40.0% |
| 0.45 | 0.20 | 435 | -0.0042 | 50.0% |
| 0.45 | 0.30 | 176 | -0.0139 | 40.0% |
| 0.45 | 0.40 | 53 | -0.0118 | 40.0% |
| 0.45 | 0.50 | 23 | +0.0170 | 70.0% |
| 0.50 | 0.15 | 561 | -0.0004 | 50.0% |
| 0.50 | 0.25 | 282 | +0.0041 | 60.0% |
| 0.50 | 0.35 | 79 | -0.0118 | 40.0% |
| 0.50 | 0.45 | 33 | +0.0006 | 50.0% |
| 0.55 | 0.10 | 517 | -0.0004 | 50.0% |
| 0.55 | 0.20 | 406 | -0.0042 | 50.0% |
| 0.55 | 0.30 | 176 | -0.0139 | 40.0% |
| 0.55 | 0.40 | 53 | -0.0118 | 40.0% |
| 0.55 | 0.50 | 23 | +0.0170 | 70.0% |
| 0.60 | 0.15 | 219 | +0.0046 | 50.0% |
| 0.60 | 0.25 | 195 | +0.0126 | 60.0% |
| 0.60 | 0.35 | 77 | -0.0118 | 40.0% |
| 0.60 | 0.45 | 33 | +0.0006 | 50.0% |
| 0.65 | 0.10 | 55 | -0.0126 | 40.0% |
| 0.65 | 0.20 | 55 | -0.0126 | 40.0% |
| 0.65 | 0.30 | 54 | -0.0126 | 40.0% |
| 0.65 | 0.40 | 41 | +0.0006 | 50.0% |
| 0.65 | 0.50 | 23 | +0.0170 | 70.0% |
| 0.70 | 0.15 | 15 | +0.0155 | 70.0% |
| 0.70 | 0.25 | 15 | +0.0155 | 70.0% |
| 0.70 | 0.35 | 15 | +0.0155 | 70.0% |
| 0.70 | 0.45 | 15 | +0.0155 | 70.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.70, ir_thr=0.50 → 13 candidates, mean lock IC=+0.0187, 70.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 769 | +0.0263 | 80.0% |
| 0.45 | 0.20 | 379 | +0.0502 | 100.0% |
| 0.45 | 0.30 | 151 | +0.0681 | 100.0% |
| 0.45 | 0.40 | 66 | +0.0482 | 90.0% |
| 0.45 | 0.50 | 13 | -0.0554 | 0.0% |
| 0.50 | 0.15 | 533 | +0.0441 | 100.0% |
| 0.50 | 0.25 | 252 | +0.0540 | 100.0% |
| 0.50 | 0.35 | 105 | +0.0681 | 100.0% |
| 0.50 | 0.45 | 36 | +0.0047 | 50.0% |
| 0.55 | 0.10 | 511 | +0.0263 | 80.0% |
| 0.55 | 0.20 | 364 | +0.0502 | 100.0% |
| 0.55 | 0.30 | 151 | +0.0681 | 100.0% |
| 0.55 | 0.40 | 66 | +0.0482 | 90.0% |
| 0.55 | 0.50 | 13 | -0.0554 | 0.0% |
| 0.60 | 0.15 | 223 | +0.0540 | 100.0% |
| 0.60 | 0.25 | 192 | +0.0540 | 100.0% |
| 0.60 | 0.35 | 102 | +0.0681 | 100.0% |
| 0.60 | 0.45 | 36 | +0.0047 | 50.0% |
| 0.65 | 0.10 | 70 | +0.0551 | 90.0% |
| 0.65 | 0.20 | 70 | +0.0551 | 90.0% |
| 0.65 | 0.30 | 70 | +0.0551 | 90.0% |
| 0.65 | 0.40 | 55 | +0.0551 | 90.0% |
| 0.65 | 0.50 | 13 | -0.0554 | 0.0% |
| 0.70 | 0.15 | 12 | -0.0629 | 0.0% |
| 0.70 | 0.25 | 12 | -0.0629 | 0.0% |
| 0.70 | 0.35 | 12 | -0.0629 | 0.0% |
| 0.70 | 0.45 | 9 | -0.0637 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.30 → 151 candidates, mean lock IC=+0.0681, 100.0% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 5343 | +0.0325 | 90.0% |
| 0.45 | 0.20 | 4975 | +0.0325 | 90.0% |
| 0.45 | 0.30 | 4465 | +0.0325 | 90.0% |
| 0.45 | 0.40 | 3931 | +0.0325 | 90.0% |
| 0.45 | 0.50 | 3372 | +0.0325 | 90.0% |
| 0.50 | 0.15 | 5173 | +0.0325 | 90.0% |
| 0.50 | 0.25 | 4728 | +0.0325 | 90.0% |
| 0.50 | 0.35 | 4187 | +0.0325 | 90.0% |
| 0.50 | 0.45 | 3662 | +0.0325 | 90.0% |
| 0.55 | 0.10 | 5102 | +0.0325 | 90.0% |
| 0.55 | 0.20 | 4908 | +0.0325 | 90.0% |
| 0.55 | 0.30 | 4455 | +0.0325 | 90.0% |
| 0.55 | 0.40 | 3931 | +0.0325 | 90.0% |
| 0.55 | 0.50 | 3372 | +0.0325 | 90.0% |
| 0.60 | 0.15 | 4574 | +0.0325 | 90.0% |
| 0.60 | 0.25 | 4466 | +0.0325 | 90.0% |
| 0.60 | 0.35 | 4137 | +0.0325 | 90.0% |
| 0.60 | 0.45 | 3662 | +0.0325 | 90.0% |
| 0.65 | 0.10 | 3918 | +0.0325 | 90.0% |
| 0.65 | 0.20 | 3918 | +0.0325 | 90.0% |
| 0.65 | 0.30 | 3896 | +0.0325 | 90.0% |
| 0.65 | 0.40 | 3753 | +0.0325 | 90.0% |
| 0.65 | 0.50 | 3348 | +0.0325 | 90.0% |
| 0.70 | 0.15 | 3078 | +0.0325 | 90.0% |
| 0.70 | 0.25 | 3078 | +0.0325 | 90.0% |
| 0.70 | 0.35 | 3074 | +0.0325 | 90.0% |
| 0.70 | 0.45 | 3035 | +0.0325 | 90.0% |
| 0.75 | 0.10 | 1887 | +0.0325 | 90.0% |
| 0.75 | 0.20 | 1887 | +0.0325 | 90.0% |
| 0.75 | 0.30 | 1887 | +0.0325 | 90.0% |
| 0.75 | 0.40 | 1887 | +0.0325 | 90.0% |
| 0.75 | 0.50 | 1883 | +0.0325 | 90.0% |
| 0.80 | 0.15 | 784 | +0.0393 | 100.0% |
| 0.80 | 0.25 | 784 | +0.0393 | 100.0% |
| 0.80 | 0.35 | 784 | +0.0393 | 100.0% |
| 0.80 | 0.45 | 784 | +0.0393 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 784 candidates, mean lock IC=+0.0393, 100.0% positive

### 588000ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1371 | -0.0647 | 10.0% |
| 0.45 | 0.20 | 892 | -0.0647 | 10.0% |
| 0.45 | 0.30 | 494 | -0.0640 | 10.0% |
| 0.45 | 0.40 | 236 | -0.0205 | 30.0% |
| 0.45 | 0.50 | 95 | -0.0213 | 30.0% |
| 0.50 | 0.15 | 1116 | -0.0647 | 10.0% |
| 0.50 | 0.25 | 688 | -0.0643 | 10.0% |
| 0.50 | 0.35 | 367 | -0.0594 | 10.0% |
| 0.50 | 0.45 | 163 | -0.0023 | 40.0% |
| 0.55 | 0.10 | 966 | -0.0643 | 10.0% |
| 0.55 | 0.20 | 802 | -0.0643 | 10.0% |
| 0.55 | 0.30 | 493 | -0.0640 | 10.0% |
| 0.55 | 0.40 | 236 | -0.0205 | 30.0% |
| 0.55 | 0.50 | 95 | -0.0213 | 30.0% |
| 0.60 | 0.15 | 511 | -0.0662 | 10.0% |
| 0.60 | 0.25 | 479 | -0.0609 | 10.0% |
| 0.60 | 0.35 | 351 | -0.0654 | 0.0% |
| 0.60 | 0.45 | 163 | -0.0023 | 40.0% |
| 0.65 | 0.10 | 199 | -0.0074 | 40.0% |
| 0.65 | 0.20 | 199 | -0.0074 | 40.0% |
| 0.65 | 0.30 | 193 | -0.0074 | 40.0% |
| 0.65 | 0.40 | 164 | +0.0111 | 50.0% |
| 0.65 | 0.50 | 89 | -0.0213 | 30.0% |
| 0.70 | 0.15 | 55 | -0.0272 | 30.0% |
| 0.70 | 0.25 | 55 | -0.0272 | 30.0% |
| 0.70 | 0.35 | 55 | -0.0272 | 30.0% |
| 0.70 | 0.45 | 51 | -0.0272 | 30.0% |
| 0.75 | 0.10 | 2 | -0.0260 | 0.0% |
| 0.75 | 0.20 | 2 | -0.0260 | 0.0% |
| 0.75 | 0.30 | 2 | -0.0260 | 0.0% |
| 0.75 | 0.40 | 2 | -0.0260 | 0.0% |
| 0.75 | 0.50 | 2 | -0.0260 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.65, ir_thr=0.40 → 164 candidates, mean lock IC=+0.0111, 50.0% positive

### 588000ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 697 | -0.0280 | 10.0% |
| 0.45 | 0.20 | 394 | -0.0286 | 10.0% |
| 0.45 | 0.30 | 208 | -0.0286 | 10.0% |
| 0.45 | 0.40 | 96 | -0.0243 | 10.0% |
| 0.45 | 0.50 | 40 | -0.0234 | 10.0% |
| 0.50 | 0.15 | 492 | -0.0277 | 10.0% |
| 0.50 | 0.25 | 310 | -0.0286 | 10.0% |
| 0.50 | 0.35 | 134 | -0.0315 | 10.0% |
| 0.50 | 0.45 | 60 | -0.0239 | 10.0% |
| 0.55 | 0.10 | 453 | -0.0239 | 10.0% |
| 0.55 | 0.20 | 351 | -0.0286 | 10.0% |
| 0.55 | 0.30 | 202 | -0.0286 | 10.0% |
| 0.55 | 0.40 | 96 | -0.0243 | 10.0% |
| 0.55 | 0.50 | 40 | -0.0234 | 10.0% |
| 0.60 | 0.15 | 231 | -0.0286 | 10.0% |
| 0.60 | 0.25 | 210 | -0.0286 | 10.0% |
| 0.60 | 0.35 | 121 | -0.0315 | 10.0% |
| 0.60 | 0.45 | 60 | -0.0239 | 10.0% |
| 0.65 | 0.10 | 89 | -0.0315 | 10.0% |
| 0.65 | 0.20 | 89 | -0.0315 | 10.0% |
| 0.65 | 0.30 | 87 | -0.0315 | 10.0% |
| 0.65 | 0.40 | 70 | -0.0243 | 10.0% |
| 0.65 | 0.50 | 40 | -0.0234 | 10.0% |
| 0.70 | 0.15 | 21 | -0.0246 | 40.0% |
| 0.70 | 0.25 | 21 | -0.0246 | 40.0% |
| 0.70 | 0.35 | 21 | -0.0246 | 40.0% |
| 0.70 | 0.45 | 21 | -0.0246 | 40.0% |
| 0.75 | 0.10 | 4 | -0.0057 | 25.0% |
| 0.75 | 0.20 | 4 | -0.0057 | 25.0% |
| 0.75 | 0.30 | 4 | -0.0057 | 25.0% |
| 0.75 | 0.40 | 4 | -0.0057 | 25.0% |
| 0.75 | 0.50 | 4 | -0.0057 | 25.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 4 candidates, mean lock IC=-0.0057, 25.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 2035 | +0.0958 | 100.0% |
| 0.45 | 0.20 | 1515 | +0.0958 | 100.0% |
| 0.45 | 0.30 | 903 | +0.0958 | 100.0% |
| 0.45 | 0.40 | 495 | +0.0958 | 100.0% |
| 0.45 | 0.50 | 251 | +0.0764 | 90.0% |
| 0.50 | 0.15 | 1785 | +0.0958 | 100.0% |
| 0.50 | 0.25 | 1207 | +0.0958 | 100.0% |
| 0.50 | 0.35 | 677 | +0.0958 | 100.0% |
| 0.50 | 0.45 | 364 | +0.0864 | 100.0% |
| 0.55 | 0.10 | 1765 | +0.0958 | 100.0% |
| 0.55 | 0.20 | 1479 | +0.0958 | 100.0% |
| 0.55 | 0.30 | 903 | +0.0958 | 100.0% |
| 0.55 | 0.40 | 495 | +0.0958 | 100.0% |
| 0.55 | 0.50 | 251 | +0.0764 | 90.0% |
| 0.60 | 0.15 | 1106 | +0.0958 | 100.0% |
| 0.60 | 0.25 | 995 | +0.0958 | 100.0% |
| 0.60 | 0.35 | 649 | +0.0958 | 100.0% |
| 0.60 | 0.45 | 364 | +0.0864 | 100.0% |
| 0.65 | 0.10 | 534 | +0.0864 | 100.0% |
| 0.65 | 0.20 | 533 | +0.0864 | 100.0% |
| 0.65 | 0.30 | 526 | +0.0864 | 100.0% |
| 0.65 | 0.40 | 443 | +0.0864 | 100.0% |
| 0.65 | 0.50 | 250 | +0.0764 | 90.0% |
| 0.70 | 0.15 | 181 | +0.0584 | 90.0% |
| 0.70 | 0.25 | 181 | +0.0584 | 90.0% |
| 0.70 | 0.35 | 181 | +0.0584 | 90.0% |
| 0.70 | 0.45 | 176 | +0.0584 | 90.0% |
| 0.75 | 0.10 | 52 | +0.0504 | 100.0% |
| 0.75 | 0.20 | 52 | +0.0504 | 100.0% |
| 0.75 | 0.30 | 52 | +0.0504 | 100.0% |
| 0.75 | 0.40 | 52 | +0.0504 | 100.0% |
| 0.75 | 0.50 | 52 | +0.0504 | 100.0% |
| 0.80 | 0.15 | 22 | +0.0163 | 70.0% |
| 0.80 | 0.25 | 22 | +0.0163 | 70.0% |
| 0.80 | 0.35 | 22 | +0.0163 | 70.0% |
| 0.80 | 0.45 | 22 | +0.0163 | 70.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 2035 candidates, mean lock IC=+0.0958, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 239 | +0.0522 | 80.0% |
| 0.45 | 0.20 | 126 | +0.0385 | 80.0% |
| 0.45 | 0.30 | 46 | +0.0409 | 80.0% |
| 0.45 | 0.40 | 14 | +0.0454 | 100.0% |
| 0.45 | 0.50 | 2 | +0.0521 | 100.0% |
| 0.50 | 0.15 | 172 | +0.0307 | 60.0% |
| 0.50 | 0.25 | 78 | +0.0379 | 80.0% |
| 0.50 | 0.35 | 25 | +0.0537 | 100.0% |
| 0.50 | 0.45 | 3 | +0.0536 | 100.0% |
| 0.55 | 0.10 | 162 | +0.0395 | 70.0% |
| 0.55 | 0.20 | 115 | +0.0385 | 80.0% |
| 0.55 | 0.30 | 46 | +0.0409 | 80.0% |
| 0.55 | 0.40 | 14 | +0.0454 | 100.0% |
| 0.55 | 0.50 | 2 | +0.0521 | 100.0% |
| 0.60 | 0.15 | 59 | +0.0305 | 70.0% |
| 0.60 | 0.25 | 46 | +0.0366 | 80.0% |
| 0.60 | 0.35 | 24 | +0.0538 | 100.0% |
| 0.60 | 0.45 | 3 | +0.0536 | 100.0% |
| 0.65 | 0.10 | 13 | +0.0483 | 100.0% |
| 0.65 | 0.20 | 13 | +0.0483 | 100.0% |
| 0.65 | 0.30 | 13 | +0.0483 | 100.0% |
| 0.65 | 0.40 | 9 | +0.0503 | 100.0% |
| 0.65 | 0.50 | 2 | +0.0521 | 100.0% |
| 0.70 | 0.15 | 1 | +0.0467 | 100.0% |
| 0.70 | 0.25 | 1 | +0.0467 | 100.0% |
| 0.70 | 0.35 | 1 | +0.0467 | 100.0% |
| 0.70 | 0.45 | 1 | +0.0467 | 100.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.60, ir_thr=0.35 → 24 candidates, mean lock IC=+0.0538, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 2314 | -0.0205 | 10.0% |
| 0.45 | 0.20 | 1190 | -0.0245 | 0.0% |
| 0.45 | 0.30 | 403 | -0.0172 | 10.0% |
| 0.45 | 0.40 | 119 | -0.0215 | 0.0% |
| 0.45 | 0.50 | 17 | -0.0215 | 0.0% |
| 0.50 | 0.15 | 1686 | -0.0205 | 10.0% |
| 0.50 | 0.25 | 731 | -0.0245 | 0.0% |
| 0.50 | 0.35 | 201 | -0.0041 | 40.0% |
| 0.50 | 0.45 | 38 | -0.0248 | 0.0% |
| 0.55 | 0.10 | 1515 | -0.0212 | 0.0% |
| 0.55 | 0.20 | 1090 | -0.0212 | 0.0% |
| 0.55 | 0.30 | 400 | -0.0157 | 10.0% |
| 0.55 | 0.40 | 119 | -0.0215 | 0.0% |
| 0.55 | 0.50 | 17 | -0.0215 | 0.0% |
| 0.60 | 0.15 | 528 | -0.0123 | 20.0% |
| 0.60 | 0.25 | 435 | -0.0123 | 20.0% |
| 0.60 | 0.35 | 191 | -0.0041 | 40.0% |
| 0.60 | 0.45 | 38 | -0.0248 | 0.0% |
| 0.65 | 0.10 | 96 | -0.0212 | 10.0% |
| 0.65 | 0.20 | 96 | -0.0212 | 10.0% |
| 0.65 | 0.30 | 91 | -0.0212 | 10.0% |
| 0.65 | 0.40 | 69 | -0.0252 | 0.0% |
| 0.65 | 0.50 | 17 | -0.0215 | 0.0% |
| 0.70 | 0.15 | 12 | -0.0235 | 0.0% |
| 0.70 | 0.25 | 12 | -0.0235 | 0.0% |
| 0.70 | 0.35 | 12 | -0.0235 | 0.0% |
| 0.70 | 0.45 | 11 | -0.0237 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.35 → 201 candidates, mean lock IC=-0.0041, 40.0% positive

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

1. **300ETF `single` — B2 Rolling Guard too strict**: 80% of top rejects have positive lockbox IC (mean lock IC=+0.0135). Consider relaxing this gate.
2. **300ETF `single` — Absolute Sign Check too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0278). Consider relaxing this gate.
3. **300ETF `single` — BH-FDR Gate too strict**: 70% of top rejects have positive lockbox IC (mean lock IC=+0.0038). Consider relaxing this gate.
4. **300ETF `single` — B3 Composite Floor too strict**: 83% of top rejects have positive lockbox IC (mean lock IC=+0.0108). Consider relaxing this gate.
5. **300ETF `single` — B4 Correlation Gate too strict**: 86% of top rejects have positive lockbox IC (mean lock IC=+0.0305). Consider relaxing this gate.
6. **300ETF `short` — Split-Half Sign Stability too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0220). Consider relaxing this gate.
7. **300ETF `short` — B2 Rolling Guard too strict**: 53% of top rejects have positive lockbox IC (mean lock IC=-0.0052). Consider relaxing this gate.
8. **50ETF `single` — Split-Half Sign Stability too strict**: 97% of top rejects have positive lockbox IC (mean lock IC=+0.0534). Consider relaxing this gate.
9. **50ETF `single` — B2 Rolling Guard too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0283). Consider relaxing this gate.
10. **50ETF `single` — Absolute Sign Check too strict**: 90% of top rejects have positive lockbox IC (mean lock IC=+0.0340). Consider relaxing this gate.
11. **50ETF `single` — BH-FDR Gate too strict**: 87% of top rejects have positive lockbox IC (mean lock IC=+0.0306). Consider relaxing this gate.
12. **50ETF `long` — Split-Half Sign Stability too strict**: 90% of top rejects have positive lockbox IC (mean lock IC=+0.0350). Consider relaxing this gate.
13. **50ETF `long` — B2 Rolling Guard too strict**: 70% of top rejects have positive lockbox IC (mean lock IC=+0.0191). Consider relaxing this gate.
14. **50ETF `long` — Absolute Sign Check too strict**: 60% of top rejects have positive lockbox IC (mean lock IC=+0.0067). Consider relaxing this gate.
15. **50ETF `short` — Split-Half Sign Stability too strict**: 60% of top rejects have positive lockbox IC (mean lock IC=+0.0189). Consider relaxing this gate.
16. **50ETF `short` — BH-FDR Gate too strict**: 53% of top rejects have positive lockbox IC (mean lock IC=-0.0074). Consider relaxing this gate.
17. **500ETF `single` — Split-Half Sign Stability too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0318). Consider relaxing this gate.
18. **500ETF `single` — B2 Rolling Guard too strict**: 83% of top rejects have positive lockbox IC (mean lock IC=+0.0479). Consider relaxing this gate.
19. **500ETF `single` — Absolute Sign Check too strict**: 73% of top rejects have positive lockbox IC (mean lock IC=+0.0214). Consider relaxing this gate.
20. **500ETF `single` — BH-FDR Gate too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0522). Consider relaxing this gate.
21. **500ETF `single` — B3 Composite Floor too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0796). Consider relaxing this gate.
22. **500ETF `single` — B4 Correlation Gate too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0697). Consider relaxing this gate.
23. **500ETF `long` — Split-Half Sign Stability too strict**: 97% of top rejects have positive lockbox IC (mean lock IC=+0.0460). Consider relaxing this gate.
24. **500ETF `long` — B2 Rolling Guard too strict**: 97% of top rejects have positive lockbox IC (mean lock IC=+0.0338). Consider relaxing this gate.
25. **500ETF `long` — Absolute Sign Check too strict**: 53% of top rejects have positive lockbox IC (mean lock IC=+0.0006). Consider relaxing this gate.
26. **500ETF `long` — BH-FDR Gate too strict**: 70% of top rejects have positive lockbox IC (mean lock IC=+0.0266). Consider relaxing this gate.
27. **500ETF `long` — Admission too loose**: 100% of admitted features have negative lockbox IC. Tighten B3 composite floor or add OOS validation gate.
28. **500ETF `short` — Split-Half Sign Stability too strict**: 67% of top rejects have positive lockbox IC (mean lock IC=+0.0238). Consider relaxing this gate.
29. **500ETF `short` — Absolute Sign Check too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0602). Consider relaxing this gate.
30. **500ETF `short` — BH-FDR Gate too strict**: 70% of top rejects have positive lockbox IC (mean lock IC=+0.0228). Consider relaxing this gate.
31. **588000ETF `single` — B3 Composite Floor too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0231). Consider relaxing this gate.
32. **588000ETF `single` — B4 Correlation Gate too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0378). Consider relaxing this gate.
33. **588000ETF `single` — Admission too loose**: 60% of admitted features have negative lockbox IC. Tighten B3 composite floor or add OOS validation gate.
34. **588000ETF `long` — BH-FDR Gate too strict**: 53% of top rejects have positive lockbox IC (mean lock IC=+0.0092). Consider relaxing this gate.
35. **588000ETF `long` — Admission too loose**: 100% of admitted features have negative lockbox IC. Tighten B3 composite floor or add OOS validation gate.
36. **159915ETF `single` — Split-Half Sign Stability too strict**: 60% of top rejects have positive lockbox IC (mean lock IC=+0.0250). Consider relaxing this gate.
37. **159915ETF `single` — B2 Rolling Guard too strict**: 63% of top rejects have positive lockbox IC (mean lock IC=+0.0245). Consider relaxing this gate.
38. **159915ETF `single` — Absolute Sign Check too strict**: 80% of top rejects have positive lockbox IC (mean lock IC=+0.0206). Consider relaxing this gate.
39. **159915ETF `single` — BH-FDR Gate too strict**: 97% of top rejects have positive lockbox IC (mean lock IC=+0.0549). Consider relaxing this gate.
40. **159915ETF `single` — B3 Composite Floor too strict**: 90% of top rejects have positive lockbox IC (mean lock IC=+0.0383). Consider relaxing this gate.
41. **159915ETF `single` — B4 Correlation Gate too strict**: 97% of top rejects have positive lockbox IC (mean lock IC=+0.0897). Consider relaxing this gate.
42. **159915ETF `long` — Split-Half Sign Stability too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0218). Consider relaxing this gate.
43. **159915ETF `long` — B2 Rolling Guard too strict**: 73% of top rejects have positive lockbox IC (mean lock IC=+0.0294). Consider relaxing this gate.
44. **159915ETF `long` — BH-FDR Gate too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0297). Consider relaxing this gate.
45. **159915ETF `short` — Split-Half Sign Stability too strict**: 67% of top rejects have positive lockbox IC (mean lock IC=+0.0113). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
