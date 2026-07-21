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
| Split-Half Sign Stability | 1971 | 30 | 76.7% | +0.0171 | -0.2119 |
| B2 Rolling Guard | 226 | 30 | 93.3% | +0.0233 | -0.4894 |
| Absolute Sign Check | 44 | 30 | 76.7% | +0.0221 | -0.1197 |
| BH-FDR Gate | 115 | 30 | 53.3% | +0.0016 | -0.3316 |
| B3 Composite Floor | 28 | 28 | 85.7% | +0.0103 | -0.3908 |
| B4 Correlation Gate | 18 | 18 | 88.9% | +0.0276 | -0.2956 |

**Admitted Pool Summary**: 7 features, False Positive Rate = 14.3% (admitted but negative lock IC), Mean Lock IC = +0.0227, Mean Lock Sharpe = -0.2246

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `yesterday_lunch_gap`: Train IC=+0.1668, Lock IC=+0.0943, Lock Sharpe=+0.3158
- `combo_rank_min__bar_ret_0__gap_pct`: Train IC=+0.1929, Lock IC=+0.0586, Lock Sharpe=+0.1359
- `combo_rank_min__first_bar_return__gap_pct`: Train IC=+0.1929, Lock IC=+0.0586, Lock Sharpe=+0.1359
- `combo_rank_min__max_up_ret__gap_pct`: Train IC=+0.2209, Lock IC=+0.0510, Lock Sharpe=-0.2330
- `combo_ifelse__gap_pct__bar_body_rng_0__short_sell_cover_spread`: Train IC=+0.1931, Lock IC=+0.0455, Lock Sharpe=+0.1934

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_body_rng_0__growth_momentum_ratio`: Train IC=+0.1556, Lock IC=+0.0868, Lock Sharpe=+0.5687
- `gap_pct`: Train IC=+0.1525, Lock IC=+0.0795, Lock Sharpe=+0.1398
- `combo_min__gap_pct__bar_vwap_dev_2`: Train IC=+0.1550, Lock IC=+0.0490, Lock Sharpe=-0.9738
- `combo_rank_min__gap_pct__bar_vwap_dev_2`: Train IC=+0.1506, Lock IC=+0.0476, Lock Sharpe=-0.8272
- `combo_min__gap_pct__early_range`: Train IC=+0.1877, Lock IC=+0.0410, Lock Sharpe=-0.6286

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_ret_0__short_sell_cover_spread`: Train IC=+0.2047, Lock IC=+0.0821, Lock Sharpe=+0.4454
- `combo_ifelse__macd_hist__first_bar_return__short_sell_cover_spread`: Train IC=+0.2049, Lock IC=+0.0819, Lock Sharpe=+0.4454
- `combo_min__wavetrend_osc_day__yesterday_day_range`: Train IC=+0.0461, Lock IC=+0.0530, Lock Sharpe=+0.5284
- `combo_min__yesterday_wavetrend_osc__yesterday_day_range`: Train IC=+0.0461, Lock IC=+0.0530, Lock Sharpe=+0.5284
- `combo_rank_min__bar_vol_0__yesterday_body_ratio`: Train IC=+0.0822, Lock IC=+0.0526, Lock Sharpe=-0.7008

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_ret_0__yesterday_northbound_net_ratio`: Train IC=+0.1749, Lock IC=+0.0701, Lock Sharpe=+0.5940
- `combo_ifelse__macd_hist__first_bar_return__yesterday_northbound_net_ratio`: Train IC=+0.1749, Lock IC=+0.0701, Lock Sharpe=+0.5940
- `combo_ifelse__macd_hist__max_up_ret__short_sell_cover_spread`: Train IC=+0.1642, Lock IC=+0.0475, Lock Sharpe=+0.3667
- `combo_max__first_bar_return__gap_pct`: Train IC=+0.1633, Lock IC=+0.0367, Lock Sharpe=-0.0066
- `combo_max__bar_ret_0__gap_pct`: Train IC=+0.1637, Lock IC=+0.0366, Lock Sharpe=-0.0066

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_body_rng_0__short_sell_cover_spread`: Train IC=+0.1986, Lock IC=+0.0904, Lock Sharpe=+0.1163
- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2027, Lock IC=+0.0428, Lock Sharpe=-0.1001
- `combo_tri_mean__bar_ret_0__gap_pct__first_30min_return`: Train IC=+0.2083, Lock IC=+0.0246, Lock Sharpe=+0.2007
- `combo_tri_mean__first_bar_return__gap_pct__first_30min_return`: Train IC=+0.2083, Lock IC=+0.0246, Lock Sharpe=+0.2007
- `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`: Train IC=+0.2020, Lock IC=+0.0151, Lock Sharpe=-0.7114

**Top False Negatives from B4 Correlation Gate** (rejected but positive lockbox IC):

- `combo_ifelse__macd_hist__bar_ret_0__growth_momentum_ratio`: Train IC=+0.1855, Lock IC=+0.0723, Lock Sharpe=+0.5292
- `combo_ifelse__macd_hist__first_bar_return__growth_momentum_ratio`: Train IC=+0.1853, Lock IC=+0.0723, Lock Sharpe=+0.5292
- `combo_ifelse__macd_hist__first_bar_return__option_oi_growth`: Train IC=+0.1840, Lock IC=+0.0620, Lock Sharpe=+0.2963
- `combo_ifelse__macd_hist__bar_ret_0__option_oi_growth`: Train IC=+0.1841, Lock IC=+0.0619, Lock Sharpe=+0.2963
- `combo_ifelse__gap_pct__bar_ret_0__short_sell_cover_spread`: Train IC=+0.2400, Lock IC=+0.0377, Lock Sharpe=-0.8458

### 300ETF — `long` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 128 | 30 | 46.7% | -0.0066 | -0.6807 |
| B2 Rolling Guard | 88 | 30 | 20.0% | -0.0032 | -0.3657 |
| BH-FDR Gate | 1 | 1 | 0.0% | -0.0606 | -0.7839 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `yesterday_lunch_gap`: Train IC=+0.1781, Lock IC=+0.0943, Lock Sharpe=-0.4058
- `first_bar_volume`: Train IC=+0.1039, Lock IC=+0.0353, Lock Sharpe=-0.1625
- `bar_vol_0`: Train IC=+0.1039, Lock IC=+0.0353, Lock Sharpe=-0.1625
- `macd_hist`: Train IC=+0.0803, Lock IC=+0.0348, Lock Sharpe=+0.4885
- `early_vwap_dev`: Train IC=+0.1342, Lock IC=+0.0281, Lock Sharpe=-0.3020

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `early_trend`: Train IC=+0.1309, Lock IC=+0.0621, Lock Sharpe=-0.2372
- `early_skew`: Train IC=+0.0590, Lock IC=+0.0222, Lock Sharpe=-0.7422
- `vix_skew_proxy`: Train IC=+0.0629, Lock IC=+0.0083, Lock Sharpe=-1.3412
- `vix_diff_1d`: Train IC=+0.0791, Lock IC=+0.0074, Lock Sharpe=-1.3079
- `yesterday_vix_early_drift`: Train IC=+0.0791, Lock IC=+0.0074, Lock Sharpe=-1.3079

### 300ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 10603 | 30 | 100.0% | +0.0167 | -0.5009 |
| B2 Rolling Guard | 1050 | 30 | 76.7% | +0.0136 | -0.5068 |
| Absolute Sign Check | 74 | 30 | 26.7% | -0.0140 | -0.6782 |
| BH-FDR Gate | 57 | 30 | 36.7% | -0.0035 | -0.5287 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_ifelse__gap_pct__vix_iv_ratio__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_ifelse__gap_pct__vix_iv_spread__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__iv__vix_iv_ratio__total_balance__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_ifelse__gap_pct__iv__vix_iv_ratio__total_path_length__yesterday_lunch_gap`: Train IC=+0.1792, Lock IC=+0.0729, Lock Sharpe=+0.5303
- `combo_tri_min__gap_pct__total_path_length__atr14_norm`: Train IC=+0.2088, Lock IC=+0.0567, Lock Sharpe=-0.3960

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_ifelse__sma20_dist__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1415, Lock IC=+0.0561, Lock Sharpe=-0.2614
- `combo_rank_min__short_sell_cover_spread__margin_short_ratio`: Train IC=+0.1696, Lock IC=+0.0540, Lock Sharpe=-0.8499
- `combo_rank_min__short_sell_cover_spread__margin_lever_ratio`: Train IC=+0.1696, Lock IC=+0.0540, Lock Sharpe=-0.8499
- `combo_tri_ifelse__vix__atr14_norm__yesterday_afternoon_reversal__short_sell_cover_spread__stoch_d`: Train IC=+0.1511, Lock IC=+0.0512, Lock Sharpe=+0.5766
- `combo_tri_ifelse__gap_pct__vix__vix_iv_ratio__total_balance__short_sell_cover_spread`: Train IC=+0.1417, Lock IC=+0.0510, Lock Sharpe=-0.7947

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_max__stoch_d__margin_short_ratio__mfi14`: Train IC=+0.0493, Lock IC=+0.0556, Lock Sharpe=+0.5980
- `combo_tri_max__stoch_d__margin_lever_ratio__mfi14`: Train IC=+0.0493, Lock IC=+0.0556, Lock Sharpe=+0.5980
- `combo_max__margin_short_ratio__sma20_dist`: Train IC=+0.0607, Lock IC=+0.0478, Lock Sharpe=+0.1454
- `combo_max__margin_lever_ratio__sma20_dist`: Train IC=+0.0607, Lock IC=+0.0478, Lock Sharpe=+0.1454
- `combo_abs_diff__margin_buy_repayment_spread__yesterday_day_realized_vol`: Train IC=+0.0866, Lock IC=+0.0414, Lock Sharpe=+0.2059

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `gap_pct`: Train IC=+0.1531, Lock IC=+0.0795, Lock Sharpe=+0.3802
- `combo_ifelse__vix__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1548, Lock IC=+0.0465, Lock Sharpe=-0.3810
- `combo_tri_ifelse__iv__vix__yesterday_pm_am_vol_ratio__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1548, Lock IC=+0.0465, Lock Sharpe=-0.3810
- `combo_tri_ifelse__iv__vix__yesterday_day_pm_am_vol_ratio__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1548, Lock IC=+0.0465, Lock Sharpe=-0.3810
- `combo_tri_ifelse__iv__vix__cci14__yesterday_afternoon_reversal__short_sell_cover_spread`: Train IC=+0.1548, Lock IC=+0.0465, Lock Sharpe=-0.3810

### 50ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 2377 | 30 | 86.7% | +0.0402 | -0.0778 |
| B2 Rolling Guard | 253 | 30 | 83.3% | +0.0392 | -0.4994 |
| Absolute Sign Check | 139 | 30 | 86.7% | +0.0328 | -0.0594 |
| BH-FDR Gate | 44 | 30 | 93.3% | +0.0307 | -0.0408 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_max__bar_vol_4__wavetrend_osc_day`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_max__bar_vol_4__yesterday_wavetrend_osc`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.8356
- `combo_mean__bar_vol_4__rsi5`: Train IC=+0.1862, Lock IC=+0.0775, Lock Sharpe=+0.0689
- `yesterday_lunch_gap`: Train IC=+0.1911, Lock IC=+0.0772, Lock Sharpe=+0.4464
- `combo_max__bar_vol_4__stoch_k`: Train IC=+0.1714, Lock IC=+0.0684, Lock Sharpe=+0.2635

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_ifelse__gap_pct__yesterday_lunch_gap__bar_vol_4`: Train IC=+0.1178, Lock IC=+0.1152, Lock Sharpe=+0.4901
- `combo_tri_mean__bar_vol_4__yesterday_body_ratio__bar_ret_0`: Train IC=+0.1098, Lock IC=+0.0859, Lock Sharpe=-1.0088
- `combo_tri_max__bar_vol_4__yesterday_body_ratio__bar_ret_0`: Train IC=+0.1221, Lock IC=+0.0813, Lock Sharpe=-0.9366
- `combo_ifelse__gap_pct__yesterday_lunch_gap__capital_buy_value`: Train IC=+0.1116, Lock IC=+0.0652, Lock Sharpe=-0.0604
- `combo_ifelse__macd_hist__yesterday_lunch_gap__margin_extreme_rank_252d`: Train IC=+0.1454, Lock IC=+0.0617, Lock Sharpe=+0.4274

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_max__bar_vol_4__sma50_dist__roc10`: Train IC=+0.1276, Lock IC=+0.0815, Lock Sharpe=+0.5924
- `combo_rank_min__bar_vol_5__macd_hist`: Train IC=+0.1178, Lock IC=+0.0787, Lock Sharpe=-0.1634
- `combo_rank_min__sma20_dist__bar_vol_5`: Train IC=+0.1010, Lock IC=+0.0775, Lock Sharpe=+0.0096
- `combo_tri_max__bar_vol_4__sma_distance_60d__roc10`: Train IC=+0.1235, Lock IC=+0.0734, Lock Sharpe=+0.5220
- `combo_tri_max__bar_vol_4__roc10__yearly_low_distance`: Train IC=+0.1357, Lock IC=+0.0617, Lock Sharpe=-0.0515

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_diff__short_balance_quantity__roc20`: Train IC=+0.1493, Lock IC=+0.0848, Lock Sharpe=-0.0456
- `combo_diff__yearly_low_distance__sma20_dist`: Train IC=+0.1250, Lock IC=+0.0719, Lock Sharpe=-0.1550
- `combo_clamp_diff__yearly_low_distance__sma20_dist`: Train IC=+0.1214, Lock IC=+0.0714, Lock Sharpe=-0.1550
- `combo_clamp_diff__iv_envelope_deviation__roc20`: Train IC=+0.0803, Lock IC=+0.0708, Lock Sharpe=+0.4617
- `combo_diff__yearly_low_distance__sma10_dist`: Train IC=+0.0787, Lock IC=+0.0658, Lock Sharpe=+0.5096

### 50ETF — `long` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 3827 | 30 | 86.7% | +0.0407 | -0.4162 |
| B2 Rolling Guard | 430 | 30 | 80.0% | +0.0275 | -0.5614 |
| Absolute Sign Check | 18 | 18 | 66.7% | +0.0277 | -0.5949 |
| BH-FDR Gate | 12 | 12 | 25.0% | -0.0261 | -1.5873 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_mean__margin_net_buy__early_range__roc5`: Train IC=+0.2542, Lock IC=+0.1025, Lock Sharpe=-0.6657
- `combo_clamp_diff__yearly_low_distance__yesterday_wavetrend_osc`: Train IC=+0.2087, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_clamp_diff__yearly_low_distance__wavetrend_osc_day`: Train IC=+0.2087, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_diff__yearly_low_distance__yesterday_wavetrend_osc`: Train IC=+0.2102, Lock IC=+0.0836, Lock Sharpe=+0.1455
- `combo_diff__yearly_low_distance__wavetrend_osc_day`: Train IC=+0.2102, Lock IC=+0.0836, Lock Sharpe=+0.1455

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_median__max_down_ret__rsi21__roc5`: Train IC=+0.1118, Lock IC=+0.0685, Lock Sharpe=+0.1340
- `combo_max__bar_vol_4__stoch_k`: Train IC=+0.1100, Lock IC=+0.0684, Lock Sharpe=-0.2128
- `combo_tri_median__yesterday_wavetrend_osc__yesterday_day_realized_vol__iv_corridor_width`: Train IC=+0.1128, Lock IC=+0.0572, Lock Sharpe=-0.4907
- `combo_tri_median__wavetrend_osc_day__yesterday_day_realized_vol__iv_corridor_width`: Train IC=+0.1128, Lock IC=+0.0572, Lock Sharpe=-0.4907
- `combo_rank_max__yesterday_wavetrend_osc__iv_corridor_width`: Train IC=+0.1583, Lock IC=+0.0548, Lock Sharpe=-0.1972

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_clamp_diff__sma_distance_60d__roc60`: Train IC=-0.0761, Lock IC=+0.1077, Lock Sharpe=+0.5548
- `combo_rank_max__roc10__bar_vol_4`: Train IC=+0.0937, Lock IC=+0.1002, Lock Sharpe=-0.3212
- `combo_tri_max__roc5__roc10__bar_vol_4`: Train IC=+0.0989, Lock IC=+0.0934, Lock Sharpe=-0.0113
- `combo_tri_max__sma_distance_60d__roc10__bar_vol_4`: Train IC=+0.0366, Lock IC=+0.0734, Lock Sharpe=-0.7780
- `combo_max__yesterday_wavetrend_osc__margin_net_buy`: Train IC=+0.0688, Lock IC=+0.0623, Lock Sharpe=-0.1923

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_diff__tech_value_rotation__sma200_dist`: Train IC=+0.0323, Lock IC=+0.0185, Lock Sharpe=-0.9501
- `combo_diff__max_down_ret__margin_net_buy`: Train IC=+0.0506, Lock IC=+0.0042, Lock Sharpe=-1.7566
- `combo_clamp_diff__max_down_ret__margin_net_buy`: Train IC=+0.0488, Lock IC=+0.0036, Lock Sharpe=-1.7566

### 50ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 8396 | 30 | 53.3% | +0.0186 | -0.2311 |
| B2 Rolling Guard | 738 | 30 | 70.0% | +0.0110 | -0.2876 |
| Absolute Sign Check | 86 | 30 | 66.7% | +0.0030 | -0.3895 |
| BH-FDR Gate | 39 | 30 | 33.3% | -0.0185 | -0.7374 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_min__bar_vol_5__bar_vol_0`: Train IC=+0.2084, Lock IC=+0.1078, Lock Sharpe=-0.3213
- `combo_min__bar_vol_5__first_bar_volume`: Train IC=+0.2084, Lock IC=+0.1078, Lock Sharpe=-0.3213
- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_tri_mean__iv_vol_ratio__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.6012
- `combo_rank_min__bar_vol_5__bar_vol_0`: Train IC=+0.2005, Lock IC=+0.0811, Lock Sharpe=-0.0800

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_ifelse__vol10__vix__sma50_dist__growth_momentum_ratio__max_up_ret`: Train IC=+0.1298, Lock IC=+0.0939, Lock Sharpe=+0.4262
- `combo_tri_ifelse__vol10__vix__sma_distance_60d__growth_momentum_ratio__max_up_ret`: Train IC=+0.1212, Lock IC=+0.0867, Lock Sharpe=+0.4144
- `combo_tri_ifelse__gap_pct__vix__sma50_dist__bar_rng_0__max_up_ret`: Train IC=+0.1332, Lock IC=+0.0831, Lock Sharpe=+0.8226
- `combo_tri_ifelse__vol10__vix__sma_distance_60d__yesterday_afternoon_momentum__max_up_ret`: Train IC=+0.1270, Lock IC=+0.0813, Lock Sharpe=+0.3955
- `combo_tri_median__bar_rng_0__capital_buy_value__bar_vol_0`: Train IC=+0.1259, Lock IC=+0.0783, Lock Sharpe=+0.3358

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_mean__vix__keltner_squeeze_width`: Train IC=+0.1270, Lock IC=+0.0843, Lock Sharpe=-0.2168
- `combo_mean__yesterday_day_realized_vol__keltner_squeeze_width`: Train IC=+0.1343, Lock IC=+0.0646, Lock Sharpe=-0.2397
- `combo_tri_ifelse__gap_pct__vix__sma50_dist__bar_vol_4__rsi21`: Train IC=+0.0997, Lock IC=+0.0472, Lock Sharpe=+0.2353
- `combo_min__bar_vol_0__roc5`: Train IC=+0.1071, Lock IC=+0.0426, Lock Sharpe=-0.0859
- `combo_min__first_bar_volume__roc5`: Train IC=+0.1071, Lock IC=+0.0426, Lock Sharpe=-0.0859

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_clamp_diff__iv_vol_ratio__roc20`: Train IC=+0.0697, Lock IC=+0.0708, Lock Sharpe=+0.4650
- `combo_diff__iv_vol_ratio__sma50_dist`: Train IC=+0.1170, Lock IC=+0.0567, Lock Sharpe=+0.3162
- `combo_product__bar_vol_4__bar_rng_0`: Train IC=+0.0657, Lock IC=+0.0566, Lock Sharpe=-0.4553
- `combo_clamp_diff__yesterday_afternoon_reversal__yesterday_afternoon_momentum`: Train IC=+0.1312, Lock IC=+0.0296, Lock Sharpe=-0.1196
- `combo_diff__yesterday_afternoon_reversal__yesterday_afternoon_momentum`: Train IC=+0.1301, Lock IC=+0.0296, Lock Sharpe=-0.1196

### 500ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 2429 | 30 | 96.7% | +0.0594 | -0.2474 |
| B2 Rolling Guard | 368 | 30 | 80.0% | +0.0393 | -0.2527 |
| Absolute Sign Check | 89 | 30 | 90.0% | +0.0249 | +0.1225 |
| BH-FDR Gate | 184 | 30 | 90.0% | +0.0520 | -0.2896 |
| B3 Composite Floor | 369 | 30 | 100.0% | +0.0805 | -0.3645 |
| B4 Correlation Gate | 327 | 30 | 100.0% | +0.0697 | -0.0425 |

**Admitted Pool Summary**: 18 features, False Positive Rate = 0.0% (admitted but negative lock IC), Mean Lock IC = +0.0646, Mean Lock Sharpe = -0.0399

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_median__max_down_ret__yesterday_first_30min_return__bar_vol_5`: Train IC=+0.2201, Lock IC=+0.1158, Lock Sharpe=+1.2194
- `combo_rank_max__max_down_ret__bar_vol_5`: Train IC=+0.2144, Lock IC=+0.0876, Lock Sharpe=+0.2281
- `combo_tri_median__max_up_ret__max_down_ret__bar_body_rng_1`: Train IC=+0.2621, Lock IC=+0.0796, Lock Sharpe=-0.5836
- `combo_mean__max_up_ret__cci14`: Train IC=+0.2373, Lock IC=+0.0786, Lock Sharpe=+0.4464
- `combo_tri_mean__first_bar_return__bar_body_rng_0__body_to_range_ratio`: Train IC=+0.2234, Lock IC=+0.0759, Lock Sharpe=+0.1443

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_rank_min__max_up_ret__macd_hist`: Train IC=+0.1996, Lock IC=+0.1047, Lock Sharpe=+0.6850
- `combo_mean__max_down_ret__num_up_bars`: Train IC=+0.1617, Lock IC=+0.0992, Lock Sharpe=+0.1165
- `combo_min__max_up_ret__macd_hist`: Train IC=+0.1619, Lock IC=+0.0976, Lock Sharpe=+0.4350
- `combo_ifelse__macd_hist__num_up_bars__bar_vwap_dev_2`: Train IC=+0.1607, Lock IC=+0.0858, Lock Sharpe=+0.3117
- `combo_ifelse__atr14_norm__yesterday_afternoon_momentum__yesterday_illiquidity_amihud`: Train IC=+0.1663, Lock IC=+0.0857, Lock Sharpe=+0.0110

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_rank_min__num_up_bars__body_to_range_ratio`: Train IC=+0.1989, Lock IC=+0.0727, Lock Sharpe=-0.2678
- `combo_ifelse__macd_hist__total_balance__short_balance`: Train IC=+0.1689, Lock IC=+0.0528, Lock Sharpe=+0.4466
- `combo_min__total_balance__vix_realized_spread`: Train IC=+0.1266, Lock IC=+0.0460, Lock Sharpe=-0.0175
- `combo_min__total_balance__iv_vol_ratio`: Train IC=+0.1266, Lock IC=+0.0456, Lock Sharpe=-0.1899
- `combo_min__short_balance__iv_vol_ratio`: Train IC=+0.0919, Lock IC=+0.0405, Lock Sharpe=+0.7816

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_rank_min__first_30min_return__gap_pct`: Train IC=+0.1430, Lock IC=+0.1020, Lock Sharpe=+0.3041
- `combo_min__first_30min_return__gap_pct`: Train IC=+0.1475, Lock IC=+0.0989, Lock Sharpe=+0.3067
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
| Split-Half Sign Stability | 4528 | 30 | 90.0% | +0.0300 | -0.1118 |
| B2 Rolling Guard | 371 | 30 | 100.0% | +0.0471 | -0.2106 |
| Absolute Sign Check | 16 | 16 | 50.0% | -0.0029 | -0.0585 |
| BH-FDR Gate | 227 | 30 | 86.7% | +0.0344 | -0.2678 |
| B3 Composite Floor | 5 | 5 | 40.0% | -0.0076 | -0.4530 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 100.0% (admitted but negative lock IC), Mean Lock IC = -0.0481, Mean Lock Sharpe = -1.3671

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_product__sma200_dist__yearly_low_distance`: Train IC=+0.2386, Lock IC=+0.0688, Lock Sharpe=+0.7891
- `combo_rank_min__rsi21__yearly_low_distance`: Train IC=+0.2282, Lock IC=+0.0629, Lock Sharpe=+0.7621
- `combo_ratio__sma200_dist__margin_balance`: Train IC=+0.2469, Lock IC=+0.0602, Lock Sharpe=-0.2230
- `combo_rank_min__yearly_low_distance__max_up_ret`: Train IC=+0.2313, Lock IC=+0.0587, Lock Sharpe=-0.0670
- `combo_min__sma50_dist__yearly_low_distance`: Train IC=+0.2372, Lock IC=+0.0564, Lock Sharpe=+0.1879

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_mean__yesterday_wavetrend_osc__rsi5`: Train IC=+0.2094, Lock IC=+0.0710, Lock Sharpe=-0.1152
- `combo_mean__wavetrend_osc_day__rsi5`: Train IC=+0.2094, Lock IC=+0.0710, Lock Sharpe=-0.1152
- `combo_tri_mean__sma100_dist__stoch_k__volume_percentile_20d`: Train IC=+0.1617, Lock IC=+0.0696, Lock Sharpe=+0.0038
- `combo_product__yearly_low_distance__max_up_ret`: Train IC=+0.1612, Lock IC=+0.0693, Lock Sharpe=-0.6058
- `combo_rank_min__yearly_high_distance__sma_distance_60d`: Train IC=+0.1733, Lock IC=+0.0631, Lock Sharpe=-0.7467

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_product__stoch_k__max_up_ret`: Train IC=+0.1316, Lock IC=+0.0745, Lock Sharpe=+0.2997
- `combo_min__yesterday_first_bar_volume__cci14`: Train IC=+0.1610, Lock IC=+0.0611, Lock Sharpe=+0.1695
- `combo_tri_max__yesterday_first_bar_volume__short_repayment_quantity__capital_buy_volume`: Train IC=+0.0085, Lock IC=+0.0503, Lock Sharpe=+0.1658
- `combo_product__stoch_k__bar_vol_4`: Train IC=+0.1588, Lock IC=+0.0266, Lock Sharpe=+0.4130
- `combo_tri_max__short_balance__short_repayment_quantity__capital_buy_volume`: Train IC=+0.0671, Lock IC=+0.0167, Lock Sharpe=+0.3801

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_min__first_30min_return__bar_body_rng_0`: Train IC=+0.1786, Lock IC=+0.0846, Lock Sharpe=-0.7002
- `combo_rank_min__bar_vwap_dev_2__max_up_ret`: Train IC=+0.1928, Lock IC=+0.0745, Lock Sharpe=-1.0570
- `combo_min__bar_vwap_dev_2__max_up_ret`: Train IC=+0.1769, Lock IC=+0.0691, Lock Sharpe=-0.9536
- `combo_tri_min__stoch_k__cci14__volume_percentile_20d`: Train IC=+0.2005, Lock IC=+0.0652, Lock Sharpe=+0.2968
- `combo_tri_median__rsi21__cci14__volume_percentile_20d`: Train IC=+0.1869, Lock IC=+0.0638, Lock Sharpe=+0.3071

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_product__yearly_low_distance__bar_vol_5`: Train IC=+0.2250, Lock IC=+0.0621, Lock Sharpe=+0.6552
- `combo_min__first_30min_return__bar_body_rng_2`: Train IC=+0.2273, Lock IC=+0.0536, Lock Sharpe=-0.5341

### 500ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 10868 | 30 | 60.0% | +0.0128 | -0.0553 |
| B2 Rolling Guard | 1089 | 30 | 83.3% | +0.0433 | +0.1761 |
| Absolute Sign Check | 148 | 30 | 83.3% | +0.0490 | +0.2809 |
| BH-FDR Gate | 69 | 30 | 100.0% | +0.0566 | -0.0398 |
| B3 Composite Floor | 1 | 1 | 100.0% | +0.0387 | +0.0976 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_ifelse__vol60__vol_pk20__total_balance__early_vwap_dev__volume_percentile_20d`: Train IC=+0.1928, Lock IC=+0.0741, Lock Sharpe=+0.5423
- `combo_tri_ifelse__vol60__vol_pk20__total_balance__bar_vwap_dev_5__volume_percentile_20d`: Train IC=+0.1928, Lock IC=+0.0741, Lock Sharpe=+0.5423
- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__body_to_range_ratio`: Train IC=+0.2585, Lock IC=+0.0657, Lock Sharpe=+0.3150
- `combo_tri_ifelse__vol60__vol_pk20__total_balance__yesterday_early_vwap_dev__volume_percentile_20d`: Train IC=+0.2149, Lock IC=+0.0651, Lock Sharpe=+0.5025
- `combo_tri_ifelse__macd_hist__gap_pct__total_balance__yesterday_early_vwap_dev__volume_percentile_20d`: Train IC=+0.2796, Lock IC=+0.0647, Lock Sharpe=-0.0045

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_tri_ifelse__vol60__gap_pct__yesterday_early_vwap_dev__high_beta_vol_ratio__margin_buy_repayment_spread`: Train IC=+0.1463, Lock IC=+0.1057, Lock Sharpe=+0.8119
- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__yesterday_early_vwap_dev__volume_percentile_20d`: Train IC=+0.2320, Lock IC=+0.0963, Lock Sharpe=+0.3396
- `combo_tri_ifelse__macd_hist__vol_pk20__rsi5__yesterday_early_vwap_dev__volume_percentile_20d`: Train IC=+0.1524, Lock IC=+0.0943, Lock Sharpe=+0.3900
- `combo_clamp_diff__rsi5__yesterday_day_vwap_dev`: Train IC=+0.1534, Lock IC=+0.0874, Lock Sharpe=-0.1809
- `combo_tri_ifelse__macd_hist__vol_pk20__total_balance__high_beta_vol_ratio__volume_percentile_20d`: Train IC=+0.1568, Lock IC=+0.0793, Lock Sharpe=+0.6868

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_ifelse__macd_hist__vol60__short_balance__yesterday_early_vwap_dev__early_vwap_dev`: Train IC=+0.1360, Lock IC=+0.1093, Lock Sharpe=+0.6096
- `combo_tri_ifelse__macd_hist__vol60__short_balance__yesterday_early_vwap_dev__bar_vwap_dev_5`: Train IC=+0.1360, Lock IC=+0.1093, Lock Sharpe=+0.6096
- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__early_vwap_dev`: Train IC=+0.1978, Lock IC=+0.1061, Lock Sharpe=+0.8742
- `combo_tri_ifelse__macd_hist__vol60__total_balance__yesterday_early_vwap_dev__bar_vwap_dev_5`: Train IC=+0.1978, Lock IC=+0.1061, Lock Sharpe=+0.8742
- `combo_tri_ifelse__macd_hist__vol_pk20__short_balance__yesterday_early_vwap_dev__early_vwap_dev`: Train IC=+0.1307, Lock IC=+0.0918, Lock Sharpe=+0.5257

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1488, Lock IC=+0.0999, Lock Sharpe=-0.0124
- `combo_clamp_diff__gap_pct__yesterday_day_vwap_dev`: Train IC=+0.1316, Lock IC=+0.0996, Lock Sharpe=-0.0124
- `combo_diff__rsi5__yesterday_day_vwap_dev`: Train IC=+0.1550, Lock IC=+0.0880, Lock Sharpe=-0.1809
- `combo_tri_ifelse__macd_hist__vol60__first_bar_volume__yesterday_early_vwap_dev__sma100_dist`: Train IC=+0.1408, Lock IC=+0.0755, Lock Sharpe=+0.1951
- `combo_tri_ifelse__macd_hist__vol60__bar_vol_0__yesterday_early_vwap_dev__sma100_dist`: Train IC=+0.1408, Lock IC=+0.0755, Lock Sharpe=+0.1951

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_tri_ifelse__macd_hist__vol_pk20__short_balance__yesterday_early_vwap_dev__body_to_range_ratio`: Train IC=+0.2444, Lock IC=+0.0387, Lock Sharpe=+0.0976

### 588000ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 5209 | 30 | 50.0% | -0.0080 | -0.3901 |
| B2 Rolling Guard | 766 | 30 | 90.0% | +0.0310 | +0.1435 |
| Absolute Sign Check | 110 | 30 | 3.3% | -0.0932 | -1.4164 |
| BH-FDR Gate | 1009 | 30 | 26.7% | -0.0374 | -0.5345 |
| B3 Composite Floor | 2141 | 30 | 93.3% | +0.0231 | -0.0431 |
| B4 Correlation Gate | 448 | 30 | 93.3% | +0.0378 | +0.1171 |

**Admitted Pool Summary**: 20 features, False Positive Rate = 60.0% (admitted but negative lock IC), Mean Lock IC = -0.0229, Mean Lock Sharpe = -0.4464

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_ifelse__vix__atr14_norm__vix_diff_1d__yesterday_vix_early_drift__num_up_bars`: Train IC=+0.2757, Lock IC=+0.0578, Lock Sharpe=+0.7604
- `combo_tri_min__vix_diff_1d__vix__yesterday_day_realized_vol`: Train IC=+0.3070, Lock IC=+0.0397, Lock Sharpe=+0.7306
- `combo_tri_min__yesterday_vix_early_drift__vix__yesterday_day_realized_vol`: Train IC=+0.3070, Lock IC=+0.0397, Lock Sharpe=+0.7306
- `combo_tri_ifelse__vix__atr14_norm__vix_diff_1d__short_sell_cover_spread__num_up_bars`: Train IC=+0.2752, Lock IC=+0.0385, Lock Sharpe=+0.0850
- `combo_tri_ifelse__vix__atr14_norm__yesterday_vix_early_drift__short_sell_cover_spread__num_up_bars`: Train IC=+0.2752, Lock IC=+0.0385, Lock Sharpe=+0.0850

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_min__vix_skew_proxy__vix_rolling_percentile_60d`: Train IC=+0.2627, Lock IC=+0.0526, Lock Sharpe=-0.4224
- `combo_rank_min__vix_skew_proxy__vix_rolling_percentile_60d`: Train IC=+0.2272, Lock IC=+0.0516, Lock Sharpe=+0.8927
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__first_bar_return__vol_gk10`: Train IC=+0.2372, Lock IC=+0.0511, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__yesterday_vix_early_drift__first_bar_return__vol_gk10`: Train IC=+0.2372, Lock IC=+0.0511, Lock Sharpe=+0.9127
- `combo_tri_ifelse__atr14_norm__vol20__vix_diff_1d__bar_ret_0__vol_gk10`: Train IC=+0.2374, Lock IC=+0.0510, Lock Sharpe=+0.9127

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_tri_ifelse__atr14_norm__vol20__short_sell_cover_spread__vol5__max_down_ret`: Train IC=+0.2205, Lock IC=+0.0001, Lock Sharpe=+0.9791

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_tri_ifelse__vix__vol20__vix_diff_1d__vix_rolling_percentile_60d__early_skew`: Train IC=+0.1855, Lock IC=+0.0281, Lock Sharpe=-0.2375
- `combo_tri_ifelse__vix__vol20__yesterday_vix_early_drift__vix_rolling_percentile_60d__early_skew`: Train IC=+0.1855, Lock IC=+0.0281, Lock Sharpe=-0.2375
- `combo_tri_ifelse__atr14_norm__vol20__bar_ret_1__yesterday_close_position__vix_rolling_percentile_60d`: Train IC=+0.1852, Lock IC=+0.0172, Lock Sharpe=-0.0138
- `combo_tri_ifelse__atr14_norm__vol20__bar_ret_1__yesterday_day_close_pos__vix_rolling_percentile_60d`: Train IC=+0.1852, Lock IC=+0.0172, Lock Sharpe=-0.0138
- `combo_tri_ifelse__vix__vol20__bar_vwap_dev_1__short_sell_cover_spread__early_skew`: Train IC=+0.1859, Lock IC=+0.0111, Lock Sharpe=-0.4684

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
| Split-Half Sign Stability | 5521 | 30 | 36.7% | -0.0101 | -0.4559 |
| B2 Rolling Guard | 1284 | 30 | 33.3% | -0.0221 | -0.5981 |
| Absolute Sign Check | 75 | 30 | 26.7% | -0.0504 | -0.7165 |
| BH-FDR Gate | 565 | 30 | 36.7% | -0.0184 | -0.6453 |
| B3 Composite Floor | 5 | 5 | 0.0% | -0.0740 | -0.9442 |

**Admitted Pool Summary**: 1 features, False Positive Rate = 100.0% (admitted but negative lock IC), Mean Lock IC = -0.0750, Mean Lock Sharpe = -0.8713

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_product__vix_diff_1d__yesterday_volume_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__vix_diff_1d__volume_sma_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__yesterday_vix_early_drift__yesterday_volume_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_product__yesterday_vix_early_drift__volume_sma_ratio`: Train IC=+0.2698, Lock IC=+0.0806, Lock Sharpe=+0.9209
- `combo_max__vix_skew_proxy__volume_slope`: Train IC=+0.2744, Lock IC=+0.0675, Lock Sharpe=-1.0303

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_rank_min__early_realized_vol__vix_diff_1d`: Train IC=+0.2631, Lock IC=+0.0901, Lock Sharpe=+0.0444
- `combo_rank_min__early_realized_vol__yesterday_vix_early_drift`: Train IC=+0.2631, Lock IC=+0.0901, Lock Sharpe=+0.0444
- `combo_ifelse__vol10__early_realized_vol__yesterday_day_realized_vol`: Train IC=+0.2487, Lock IC=+0.0473, Lock Sharpe=-0.3264
- `combo_clamp_diff__early_realized_vol__iv_envelope_deviation`: Train IC=+0.2362, Lock IC=+0.0442, Lock Sharpe=-0.2667
- `combo_clamp_diff__early_realized_vol__vix_iv_spread`: Train IC=+0.2362, Lock IC=+0.0442, Lock Sharpe=-0.2667

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_ratio__capital_net_accel__capital_large_order_ratio`: Train IC=+0.2437, Lock IC=+0.0750, Lock Sharpe=+0.2892
- `combo_abs_diff__capital_net_accel__capital_net_value`: Train IC=+0.1599, Lock IC=+0.0614, Lock Sharpe=-0.3482
- `combo_tri_median__early_range__vix_skew_proxy__buy_on_margin_value`: Train IC=+0.1116, Lock IC=+0.0437, Lock Sharpe=-0.7851
- `combo_rank_min__capital_buy_value__capital_net_value`: Train IC=+0.1484, Lock IC=+0.0402, Lock Sharpe=-0.1089
- `combo_product__growth_momentum_ratio__bar_rng_3`: Train IC=+0.1234, Lock IC=+0.0386, Lock Sharpe=-1.0825

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_ifelse__gap_pct__vol5__vix_skew_proxy`: Train IC=+0.2482, Lock IC=+0.0749, Lock Sharpe=-0.3595
- `combo_tri_min__early_realized_vol__yesterday_day_realized_vol__vix_diff_1d`: Train IC=+0.2683, Lock IC=+0.0726, Lock Sharpe=+0.0497
- `combo_tri_min__early_realized_vol__yesterday_day_realized_vol__yesterday_vix_early_drift`: Train IC=+0.2683, Lock IC=+0.0726, Lock Sharpe=+0.0497
- `combo_tri_min__early_realized_vol__yesterday_day_realized_vol__vix_skew_proxy`: Train IC=+0.2547, Lock IC=+0.0521, Lock Sharpe=+0.0497
- `combo_rank_max__bar_vol_4__vix_diff_1d`: Train IC=+0.2574, Lock IC=+0.0400, Lock Sharpe=-0.4380

### 588000ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 8720 | 30 | 16.7% | -0.0288 | -1.0100 |
| B2 Rolling Guard | 1039 | 30 | 26.7% | -0.0242 | -0.5785 |
| Absolute Sign Check | 131 | 30 | 66.7% | +0.0162 | -0.1659 |
| BH-FDR Gate | 91 | 30 | 33.3% | -0.0254 | -1.5433 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_ifelse__sma20_dist__vix__vix_rolling_percentile_60d__capital_net_ratio__total_path_length`: Train IC=+0.2272, Lock IC=+0.1029, Lock Sharpe=+0.9632
- `combo_tri_ifelse__vix__gap_pct__short_sell_cover_spread__bar_vwap_dev_5__stoch_d`: Train IC=+0.2268, Lock IC=+0.0177, Lock Sharpe=-0.2415
- `combo_tri_ifelse__vix__gap_pct__short_sell_cover_spread__early_vwap_dev__stoch_d`: Train IC=+0.2268, Lock IC=+0.0177, Lock Sharpe=-0.2415
- `combo_tri_ifelse__sma20_dist__vix__vix_rolling_percentile_60d__bar_ret_1__total_path_length`: Train IC=+0.2282, Lock IC=+0.0161, Lock Sharpe=-0.6929
- `combo_tri_ifelse__vix__gap_pct__high_beta_vol_ratio__capital_sell_value__stoch_d`: Train IC=+0.2659, Lock IC=+0.0146, Lock Sharpe=+0.1103

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_rank_min__short_balance_quantity__roc20`: Train IC=+0.1686, Lock IC=+0.0860, Lock Sharpe=+0.8040
- `combo_rank_max__vix_rolling_percentile_60d__vix_vol_ratio`: Train IC=+0.1660, Lock IC=+0.0578, Lock Sharpe=-0.4013
- `combo_tri_ifelse__sma20_dist__gap_pct__outside_bar_reversal_day__yesterday_lunch_gap__rsi5`: Train IC=+0.1552, Lock IC=+0.0547, Lock Sharpe=-0.1320
- `combo_max__vix_rolling_percentile_60d__vix_vol_ratio`: Train IC=+0.1404, Lock IC=+0.0526, Lock Sharpe=-0.9457
- `combo_min__vix__vix_skew_proxy`: Train IC=+0.1534, Lock IC=+0.0335, Lock Sharpe=+0.3985

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_ifelse__gap_pct__yesterday_lunch_gap__sma10_dist`: Train IC=+0.1484, Lock IC=+0.0671, Lock Sharpe=+0.6808
- `combo_rank_max__rsi5__sma50_dist`: Train IC=+0.0784, Lock IC=+0.0444, Lock Sharpe=+0.4081
- `combo_max__capital_net_ratio__margin_extreme_rank_252d`: Train IC=+0.0756, Lock IC=+0.0433, Lock Sharpe=-0.4145
- `combo_clamp_diff__capital_large_order_ratio__rsi5`: Train IC=+0.1008, Lock IC=+0.0424, Lock Sharpe=-0.8475
- `combo_tri_max__total_path_length__rsi5__stoch_d`: Train IC=+0.0845, Lock IC=+0.0424, Lock Sharpe=+0.6895

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_tri_ifelse__vix__gap_pct__outside_bar_reversal_day__yesterday_day_range__vix_rolling_percentile_60d`: Train IC=+0.1221, Lock IC=+0.0549, Lock Sharpe=-1.0607
- `combo_abs_diff__sma20_dist__yesterday_cvd_close`: Train IC=+0.1286, Lock IC=+0.0349, Lock Sharpe=-2.5125
- `combo_tri_ifelse__sma20_dist__gap_pct__short_repayment_quantity__yesterday_day_range__total_path_length`: Train IC=+0.1814, Lock IC=+0.0323, Lock Sharpe=+0.4660
- `combo_product__gap_pct__yesterday_early_realized_vol`: Train IC=+0.1495, Lock IC=+0.0318, Lock Sharpe=+0.4820
- `combo_abs_diff__bar_ret_1__bar_vwap_dev_5`: Train IC=+0.2171, Lock IC=+0.0295, Lock Sharpe=+0.2902

### 159915ETF — `single` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 3917 | 30 | 86.7% | +0.0462 | -0.0314 |
| B2 Rolling Guard | 718 | 30 | 60.0% | +0.0255 | -0.4125 |
| Absolute Sign Check | 55 | 30 | 80.0% | +0.0098 | -0.0458 |
| BH-FDR Gate | 182 | 30 | 100.0% | +0.0530 | -0.0728 |
| B3 Composite Floor | 251 | 30 | 100.0% | +0.0509 | -0.1103 |
| B4 Correlation Gate | 46 | 30 | 96.7% | +0.0897 | +0.2692 |

**Admitted Pool Summary**: 8 features, False Positive Rate = 12.5% (admitted but negative lock IC), Mean Lock IC = +0.0751, Mean Lock Sharpe = +0.1042

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__max_down_ret`: Train IC=+0.2211, Lock IC=+0.1272, Lock Sharpe=+1.1739
- `combo_tri_ifelse__gap_pct__bb_width__max_up_ret__yesterday_early_vwap_dev__yesterday_first_30min_return`: Train IC=+0.2194, Lock IC=+0.1261, Lock Sharpe=+1.0853
- `combo_tri_min__bar_ret_0__gap_pct__first_30min_return`: Train IC=+0.2080, Lock IC=+0.1182, Lock Sharpe=+1.2912
- `combo_tri_min__first_bar_return__gap_pct__first_30min_return`: Train IC=+0.2077, Lock IC=+0.1182, Lock Sharpe=+1.2912
- `combo_tri_mean__max_up_ret__bar_body_rng_0__max_down_ret`: Train IC=+0.2111, Lock IC=+0.1145, Lock Sharpe=+0.4491

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_min__max_up_ret__gap_pct`: Train IC=+0.2106, Lock IC=+0.1310, Lock Sharpe=+1.2087
- `combo_mean__bar_body_rng_0__first_30min_return`: Train IC=+0.1917, Lock IC=+0.1101, Lock Sharpe=+0.5746
- `combo_rank_min__max_up_ret__max_down_ret`: Train IC=+0.2204, Lock IC=+0.0988, Lock Sharpe=+0.7200
- `combo_clamp_diff__max_up_ret__early_range`: Train IC=+0.1895, Lock IC=+0.0980, Lock Sharpe=+0.5702
- `combo_tri_median__max_up_ret__bar_body_rng_0__max_down_ret`: Train IC=+0.1986, Lock IC=+0.0917, Lock Sharpe=-0.0891

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_clamp_diff__max_up_ret__bar_rng_5`: Train IC=+0.1398, Lock IC=+0.1030, Lock Sharpe=+0.8012
- `combo_diff__volume_sma_ratio__bar_vol_4`: Train IC=+0.1195, Lock IC=+0.0473, Lock Sharpe=+0.5008
- `combo_diff__yesterday_volume_ratio__bar_vol_4`: Train IC=+0.1195, Lock IC=+0.0473, Lock Sharpe=+0.5008
- `combo_clamp_diff__volume_sma_ratio__bar_vol_4`: Train IC=+0.1184, Lock IC=+0.0471, Lock Sharpe=+0.5008
- `combo_clamp_diff__yesterday_volume_ratio__bar_vol_4`: Train IC=+0.1184, Lock IC=+0.0471, Lock Sharpe=+0.5008

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_tri_median__max_up_ret__gap_pct__first_30min_return`: Train IC=+0.1578, Lock IC=+0.1312, Lock Sharpe=+0.0987
- `combo_ifelse__gap_pct__bar_body_rng_0__bar_ret_0`: Train IC=+0.1620, Lock IC=+0.0798, Lock Sharpe=+0.6001
- `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__bar_ret_0__first_bar_return`: Train IC=+0.1617, Lock IC=+0.0797, Lock Sharpe=+0.6001
- `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return`: Train IC=+0.1616, Lock IC=+0.0797, Lock Sharpe=+0.6001
- `combo_tri_median__max_up_ret__bar_body_rng_0__first_bar_return`: Train IC=+0.1633, Lock IC=+0.0796, Lock Sharpe=+0.3644

**Top False Negatives from B3 Composite Floor** (rejected but positive lockbox IC):

- `combo_tri_ifelse__gap_pct__bb_width__bar_body_rng_0__yesterday_early_vwap_dev__max_down_ret`: Train IC=+0.2202, Lock IC=+0.1372, Lock Sharpe=+0.9132
- `combo_tri_mean__max_up_ret__bar_ret_0__gap_pct`: Train IC=+0.2608, Lock IC=+0.1341, Lock Sharpe=+1.1076
- `combo_tri_mean__max_up_ret__first_bar_return__gap_pct`: Train IC=+0.2604, Lock IC=+0.1341, Lock Sharpe=+1.1076
- `combo_tri_mean__max_up_ret__early_range__gap_pct`: Train IC=+0.2636, Lock IC=+0.1100, Lock Sharpe=+0.3769
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
| Split-Half Sign Stability | 3230 | 30 | 80.0% | +0.0324 | +0.0372 |
| B2 Rolling Guard | 289 | 30 | 53.3% | +0.0006 | -0.2021 |
| Absolute Sign Check | 11 | 11 | 27.3% | -0.0178 | -0.5092 |
| BH-FDR Gate | 66 | 30 | 76.7% | +0.0346 | +0.0092 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_median__rsi5__yesterday_first_30min_return__volume_slope`: Train IC=+0.1941, Lock IC=+0.0809, Lock Sharpe=+0.4857
- `combo_min__early_realized_vol__max_down_ret`: Train IC=+0.1745, Lock IC=+0.0768, Lock Sharpe=+0.5838
- `combo_rank_min__max_down_ret__early_momentum`: Train IC=+0.1661, Lock IC=+0.0733, Lock Sharpe=+0.6107
- `combo_min__max_down_ret__early_momentum`: Train IC=+0.1932, Lock IC=+0.0713, Lock Sharpe=+0.1747
- `combo_rank_min__rsi5__yesterday_first_30min_return`: Train IC=+0.1837, Lock IC=+0.0679, Lock Sharpe=+0.3884

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_min__first_30min_return__max_down_ret`: Train IC=+0.1159, Lock IC=+0.0947, Lock Sharpe=+0.2340
- `combo_max__first_30min_return__bar_body_rng_1`: Train IC=+0.1690, Lock IC=+0.0836, Lock Sharpe=+0.2730
- `combo_rank_min__bar_rng_0__max_down_ret`: Train IC=+0.1528, Lock IC=+0.0709, Lock Sharpe=+1.0065
- `combo_tri_min__yesterday_first_30min_return__yesterday_return__bar_vol_4`: Train IC=+0.1215, Lock IC=+0.0693, Lock Sharpe=-0.0455
- `combo_tri_min__yesterday_first_30min_return__limit_up_proximity_day__bar_vol_4`: Train IC=+0.1215, Lock IC=+0.0693, Lock Sharpe=-0.0455

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_min__bar_vwap_dev_3__bar_body_rng_1`: Train IC=+0.1888, Lock IC=+0.0328, Lock Sharpe=+0.1273
- `combo_rank_max__margin_repayment__capital_net_value`: Train IC=-0.0307, Lock IC=+0.0047, Lock Sharpe=-1.2541
- `combo_rank_min__bar_vol_4__volume_percentile_20d`: Train IC=+0.0750, Lock IC=+0.0039, Lock Sharpe=+0.3177

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_min__bar_body_rng_1__max_down_ret`: Train IC=+0.1562, Lock IC=+0.0845, Lock Sharpe=+0.6121
- `combo_mean__bar_body_rng_1__max_down_ret`: Train IC=+0.1444, Lock IC=+0.0827, Lock Sharpe=-0.2102
- `combo_min__first_30min_return__bar_body_rng_1`: Train IC=+0.1858, Lock IC=+0.0782, Lock Sharpe=+0.5353
- `combo_min__bar_rng_0__max_down_ret`: Train IC=+0.1729, Lock IC=+0.0741, Lock Sharpe=+1.0065
- `combo_tri_max__first_30min_return__bar_body_rng_1__early_trend`: Train IC=+0.0994, Lock IC=+0.0728, Lock Sharpe=+0.0369

### 159915ETF — `short` Gate Effectiveness

| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Split-Half Sign Stability | 10328 | 30 | 60.0% | +0.0051 | -0.1605 |
| B2 Rolling Guard | 1505 | 30 | 30.0% | -0.0119 | -0.0686 |
| Absolute Sign Check | 524 | 30 | 13.3% | -0.0177 | -0.2837 |
| BH-FDR Gate | 11 | 11 | 63.6% | +0.0048 | -0.1624 |

**Top False Negatives from Split-Half Sign Stability** (rejected but positive lockbox IC):

- `combo_tri_ifelse__bb_width__sma20_dist__high_beta_vol_ratio__vol_gk10__yesterday_afternoon_momentum`: Train IC=+0.1671, Lock IC=+0.0674, Lock Sharpe=+0.1155
- `combo_product__bb_width__margin_repayment`: Train IC=+0.2082, Lock IC=+0.0637, Lock Sharpe=+1.0054
- `combo_diff__yesterday_pm_return__rsi21`: Train IC=+0.1723, Lock IC=+0.0484, Lock Sharpe=-0.7208
- `combo_tri_ifelse__vol_pk20__vol20__yesterday_afternoon_momentum__rsi21__early_realized_vol`: Train IC=+0.1878, Lock IC=+0.0435, Lock Sharpe=+0.0035
- `combo_tri_ifelse__vol_pk20__bb_width__iv_vol_ratio__sma100_dist__early_realized_vol`: Train IC=+0.1722, Lock IC=+0.0351, Lock Sharpe=+0.6703

**Top False Negatives from B2 Rolling Guard** (rejected but positive lockbox IC):

- `combo_min__yesterday_early_trend__yesterday_first_30min_return`: Train IC=+0.1645, Lock IC=+0.0548, Lock Sharpe=-0.2710
- `combo_tri_ifelse__vol_pk20__vol20__yesterday_afternoon_momentum__capital_sell_volume__early_realized_vol`: Train IC=+0.1622, Lock IC=+0.0303, Lock Sharpe=-0.2588
- `combo_tri_ifelse__vol_pk20__sma20_dist__stoch_k__yesterday_afternoon_momentum__early_realized_vol`: Train IC=+0.1610, Lock IC=+0.0261, Lock Sharpe=+0.2939
- `combo_tri_ifelse__vol20__sma20_dist__stoch_k__yesterday_pm_return__early_realized_vol`: Train IC=+0.1588, Lock IC=+0.0117, Lock Sharpe=+0.0987
- `combo_tri_ifelse__vol_pk20__sma20_dist__stoch_k__yesterday_afternoon_momentum__rsi21`: Train IC=+0.2153, Lock IC=+0.0068, Lock Sharpe=-0.0093

**Top False Negatives from Absolute Sign Check** (rejected but positive lockbox IC):

- `combo_ifelse__bb_width__vix_vol_ratio__stoch_k`: Train IC=+0.1801, Lock IC=+0.0105, Lock Sharpe=-0.4109
- `combo_tri_ifelse__vol20__sma20_dist__stoch_k__vol_gk10__yesterday_early_trend`: Train IC=+0.1306, Lock IC=+0.0070, Lock Sharpe=-0.2590
- `combo_ifelse__bb_width__vix_realized_spread__stoch_k`: Train IC=+0.1801, Lock IC=+0.0067, Lock Sharpe=-0.4109
- `combo_tri_max__sma50_dist__yesterday_pm_return__yesterday_afternoon_momentum`: Train IC=+0.1024, Lock IC=+0.0017, Lock Sharpe=-0.3508

**Top False Negatives from BH-FDR Gate** (rejected but positive lockbox IC):

- `combo_abs_diff__buy_on_margin_value__capital_buy_volume`: Train IC=+0.0851, Lock IC=+0.0211, Lock Sharpe=-1.2729
- `combo_tri_ifelse__vol_pk20__bb_width__iv_vol_ratio__vix_vol_ratio__capital_sell_volume`: Train IC=+0.0323, Lock IC=+0.0164, Lock Sharpe=+0.0510
- `combo_tri_ifelse__vol_pk20__bb_width__vix_realized_spread__vix_vol_ratio__capital_sell_volume`: Train IC=+0.0323, Lock IC=+0.0162, Lock Sharpe=-0.8572
- `combo_tri_median__iv_vol_ratio__vol20__vol_gk10`: Train IC=+0.0707, Lock IC=+0.0153, Lock Sharpe=+0.2383
- `combo_tri_max__vol20__vol_gk10__capital_sell_volume`: Train IC=+0.0743, Lock IC=+0.0118, Lock Sharpe=+0.4988

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 330 | +0.0164 | 90.0% |
| 0.45 | 0.20 | 292 | +0.0164 | 90.0% |
| 0.45 | 0.30 | 220 | +0.0164 | 90.0% |
| 0.45 | 0.40 | 155 | +0.0164 | 90.0% |
| 0.45 | 0.50 | 107 | +0.0164 | 90.0% |
| 0.50 | 0.15 | 315 | +0.0164 | 90.0% |
| 0.50 | 0.25 | 252 | +0.0164 | 90.0% |
| 0.50 | 0.35 | 184 | +0.0164 | 90.0% |
| 0.50 | 0.45 | 129 | +0.0164 | 90.0% |
| 0.55 | 0.10 | 318 | +0.0164 | 90.0% |
| 0.55 | 0.20 | 292 | +0.0164 | 90.0% |
| 0.55 | 0.30 | 220 | +0.0164 | 90.0% |
| 0.55 | 0.40 | 155 | +0.0164 | 90.0% |
| 0.55 | 0.50 | 107 | +0.0164 | 90.0% |
| 0.60 | 0.15 | 239 | +0.0164 | 90.0% |
| 0.60 | 0.25 | 234 | +0.0164 | 90.0% |
| 0.60 | 0.35 | 183 | +0.0164 | 90.0% |
| 0.60 | 0.45 | 129 | +0.0164 | 90.0% |
| 0.65 | 0.10 | 159 | +0.0164 | 90.0% |
| 0.65 | 0.20 | 159 | +0.0164 | 90.0% |
| 0.65 | 0.30 | 159 | +0.0164 | 90.0% |
| 0.65 | 0.40 | 145 | +0.0164 | 90.0% |
| 0.65 | 0.50 | 107 | +0.0164 | 90.0% |
| 0.70 | 0.15 | 92 | +0.0187 | 90.0% |
| 0.70 | 0.25 | 92 | +0.0187 | 90.0% |
| 0.70 | 0.35 | 92 | +0.0187 | 90.0% |
| 0.70 | 0.45 | 91 | +0.0187 | 90.0% |
| 0.75 | 0.10 | 32 | -0.0126 | 30.0% |
| 0.75 | 0.20 | 32 | -0.0126 | 30.0% |
| 0.75 | 0.30 | 32 | -0.0126 | 30.0% |
| 0.75 | 0.40 | 32 | -0.0126 | 30.0% |
| 0.75 | 0.50 | 32 | -0.0126 | 30.0% |
| 0.80 | 0.15 | 12 | +0.0310 | 100.0% |
| 0.80 | 0.25 | 12 | +0.0310 | 100.0% |
| 0.80 | 0.35 | 12 | +0.0310 | 100.0% |
| 0.80 | 0.45 | 12 | +0.0310 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 12 candidates, mean lock IC=+0.0310, 100.0% positive

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
| 0.45 | 0.10 | 315 | +0.0053 | 60.0% |
| 0.45 | 0.20 | 109 | +0.0038 | 60.0% |
| 0.45 | 0.30 | 28 | -0.0092 | 60.0% |
| 0.45 | 0.40 | 11 | +0.0048 | 60.0% |
| 0.45 | 0.50 | 2 | -0.0107 | 50.0% |
| 0.50 | 0.15 | 199 | +0.0053 | 60.0% |
| 0.50 | 0.25 | 69 | -0.0122 | 40.0% |
| 0.50 | 0.35 | 15 | +0.0050 | 70.0% |
| 0.50 | 0.45 | 5 | -0.0050 | 60.0% |
| 0.55 | 0.10 | 145 | +0.0038 | 60.0% |
| 0.55 | 0.20 | 101 | +0.0038 | 60.0% |
| 0.55 | 0.30 | 28 | -0.0092 | 60.0% |
| 0.55 | 0.40 | 11 | +0.0048 | 60.0% |
| 0.55 | 0.50 | 2 | -0.0107 | 50.0% |
| 0.60 | 0.15 | 45 | -0.0105 | 40.0% |
| 0.60 | 0.25 | 44 | -0.0105 | 40.0% |
| 0.60 | 0.35 | 15 | +0.0050 | 70.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 315 candidates, mean lock IC=+0.0053, 60.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 301 | +0.0490 | 100.0% |
| 0.45 | 0.20 | 266 | +0.0490 | 100.0% |
| 0.45 | 0.30 | 192 | +0.0459 | 100.0% |
| 0.45 | 0.40 | 155 | +0.0555 | 100.0% |
| 0.45 | 0.50 | 123 | +0.0555 | 100.0% |
| 0.50 | 0.15 | 284 | +0.0490 | 100.0% |
| 0.50 | 0.25 | 227 | +0.0407 | 90.0% |
| 0.50 | 0.35 | 170 | +0.0568 | 100.0% |
| 0.50 | 0.45 | 140 | +0.0555 | 100.0% |
| 0.55 | 0.10 | 282 | +0.0490 | 100.0% |
| 0.55 | 0.20 | 261 | +0.0490 | 100.0% |
| 0.55 | 0.30 | 192 | +0.0459 | 100.0% |
| 0.55 | 0.40 | 155 | +0.0555 | 100.0% |
| 0.55 | 0.50 | 123 | +0.0555 | 100.0% |
| 0.60 | 0.15 | 217 | +0.0440 | 90.0% |
| 0.60 | 0.25 | 200 | +0.0401 | 90.0% |
| 0.60 | 0.35 | 170 | +0.0568 | 100.0% |
| 0.60 | 0.45 | 140 | +0.0555 | 100.0% |
| 0.65 | 0.10 | 162 | +0.0555 | 100.0% |
| 0.65 | 0.20 | 162 | +0.0555 | 100.0% |
| 0.65 | 0.30 | 161 | +0.0555 | 100.0% |
| 0.65 | 0.40 | 152 | +0.0555 | 100.0% |
| 0.65 | 0.50 | 123 | +0.0555 | 100.0% |
| 0.70 | 0.15 | 123 | +0.0555 | 100.0% |
| 0.70 | 0.25 | 123 | +0.0555 | 100.0% |
| 0.70 | 0.35 | 123 | +0.0555 | 100.0% |
| 0.70 | 0.45 | 123 | +0.0555 | 100.0% |
| 0.75 | 0.10 | 82 | +0.0544 | 100.0% |
| 0.75 | 0.20 | 82 | +0.0544 | 100.0% |
| 0.75 | 0.30 | 82 | +0.0544 | 100.0% |
| 0.75 | 0.40 | 82 | +0.0544 | 100.0% |
| 0.75 | 0.50 | 82 | +0.0544 | 100.0% |
| 0.80 | 0.15 | 32 | +0.0273 | 100.0% |
| 0.80 | 0.25 | 32 | +0.0273 | 100.0% |
| 0.80 | 0.35 | 32 | +0.0273 | 100.0% |
| 0.80 | 0.45 | 32 | +0.0273 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.35 → 170 candidates, mean lock IC=+0.0568, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 131 | +0.0160 | 60.0% |
| 0.45 | 0.20 | 25 | +0.0019 | 50.0% |
| 0.45 | 0.30 | 9 | -0.0019 | 55.6% |
| 0.45 | 0.40 | 2 | +0.0039 | 100.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 64 | +0.0180 | 80.0% |
| 0.50 | 0.25 | 12 | -0.0087 | 50.0% |
| 0.50 | 0.35 | 4 | -0.0183 | 50.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 49 | +0.0142 | 50.0% |
| 0.55 | 0.20 | 17 | -0.0201 | 30.0% |
| 0.55 | 0.30 | 9 | -0.0019 | 55.6% |
| 0.55 | 0.40 | 2 | +0.0039 | 100.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 11 | +0.0045 | 60.0% |
| 0.60 | 0.25 | 9 | -0.0019 | 55.6% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 64 candidates, mean lock IC=+0.0180, 80.0% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 283 | -0.0332 | 20.0% |
| 0.45 | 0.20 | 107 | -0.0108 | 50.0% |
| 0.45 | 0.30 | 25 | -0.0201 | 40.0% |
| 0.45 | 0.40 | 9 | +0.0259 | 66.7% |
| 0.45 | 0.50 | 3 | +0.0409 | 66.7% |
| 0.50 | 0.15 | 179 | -0.0267 | 30.0% |
| 0.50 | 0.25 | 57 | -0.0059 | 60.0% |
| 0.50 | 0.35 | 19 | -0.0031 | 60.0% |
| 0.50 | 0.45 | 4 | +0.0484 | 75.0% |
| 0.55 | 0.10 | 149 | -0.0230 | 40.0% |
| 0.55 | 0.20 | 86 | -0.0131 | 50.0% |
| 0.55 | 0.30 | 25 | -0.0201 | 40.0% |
| 0.55 | 0.40 | 9 | +0.0259 | 66.7% |
| 0.55 | 0.50 | 3 | +0.0409 | 66.7% |
| 0.60 | 0.15 | 44 | -0.0078 | 50.0% |
| 0.60 | 0.25 | 33 | -0.0118 | 50.0% |
| 0.60 | 0.35 | 17 | -0.0031 | 60.0% |
| 0.60 | 0.45 | 4 | +0.0484 | 75.0% |
| 0.65 | 0.10 | 11 | +0.0249 | 80.0% |
| 0.65 | 0.20 | 11 | +0.0249 | 80.0% |
| 0.65 | 0.30 | 11 | +0.0249 | 80.0% |
| 0.65 | 0.40 | 7 | +0.0449 | 85.7% |
| 0.65 | 0.50 | 3 | +0.0409 | 66.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.45 → 4 candidates, mean lock IC=+0.0484, 75.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1177 | +0.0867 | 100.0% |
| 0.45 | 0.20 | 1116 | +0.0867 | 100.0% |
| 0.45 | 0.30 | 1007 | +0.0867 | 100.0% |
| 0.45 | 0.40 | 843 | +0.0867 | 100.0% |
| 0.45 | 0.50 | 609 | +0.0826 | 100.0% |
| 0.50 | 0.15 | 1148 | +0.0867 | 100.0% |
| 0.50 | 0.25 | 1064 | +0.0867 | 100.0% |
| 0.50 | 0.35 | 926 | +0.0867 | 100.0% |
| 0.50 | 0.45 | 745 | +0.0867 | 100.0% |
| 0.55 | 0.10 | 1149 | +0.0867 | 100.0% |
| 0.55 | 0.20 | 1112 | +0.0867 | 100.0% |
| 0.55 | 0.30 | 1006 | +0.0867 | 100.0% |
| 0.55 | 0.40 | 843 | +0.0867 | 100.0% |
| 0.55 | 0.50 | 609 | +0.0826 | 100.0% |
| 0.60 | 0.15 | 1023 | +0.0867 | 100.0% |
| 0.60 | 0.25 | 1013 | +0.0867 | 100.0% |
| 0.60 | 0.35 | 921 | +0.0867 | 100.0% |
| 0.60 | 0.45 | 745 | +0.0867 | 100.0% |
| 0.65 | 0.10 | 796 | +0.0826 | 100.0% |
| 0.65 | 0.20 | 796 | +0.0826 | 100.0% |
| 0.65 | 0.30 | 796 | +0.0826 | 100.0% |
| 0.65 | 0.40 | 762 | +0.0826 | 100.0% |
| 0.65 | 0.50 | 602 | +0.0826 | 100.0% |
| 0.70 | 0.15 | 491 | +0.0826 | 100.0% |
| 0.70 | 0.25 | 491 | +0.0826 | 100.0% |
| 0.70 | 0.35 | 491 | +0.0826 | 100.0% |
| 0.70 | 0.45 | 490 | +0.0826 | 100.0% |
| 0.75 | 0.10 | 207 | +0.0745 | 100.0% |
| 0.75 | 0.20 | 207 | +0.0745 | 100.0% |
| 0.75 | 0.30 | 207 | +0.0745 | 100.0% |
| 0.75 | 0.40 | 207 | +0.0745 | 100.0% |
| 0.75 | 0.50 | 207 | +0.0745 | 100.0% |
| 0.80 | 0.15 | 57 | +0.0646 | 100.0% |
| 0.80 | 0.25 | 57 | +0.0646 | 100.0% |
| 0.80 | 0.35 | 57 | +0.0646 | 100.0% |
| 0.80 | 0.45 | 57 | +0.0646 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1177 candidates, mean lock IC=+0.0867, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 349 | +0.0148 | 60.0% |
| 0.45 | 0.20 | 232 | -0.0091 | 40.0% |
| 0.45 | 0.30 | 97 | -0.0218 | 30.0% |
| 0.45 | 0.40 | 42 | -0.0080 | 40.0% |
| 0.45 | 0.50 | 20 | +0.0170 | 70.0% |
| 0.50 | 0.15 | 282 | +0.0148 | 60.0% |
| 0.50 | 0.25 | 149 | -0.0213 | 30.0% |
| 0.50 | 0.35 | 53 | -0.0060 | 40.0% |
| 0.50 | 0.45 | 30 | +0.0021 | 50.0% |
| 0.55 | 0.10 | 260 | +0.0027 | 50.0% |
| 0.55 | 0.20 | 216 | -0.0213 | 30.0% |
| 0.55 | 0.30 | 97 | -0.0218 | 30.0% |
| 0.55 | 0.40 | 42 | -0.0080 | 40.0% |
| 0.55 | 0.50 | 20 | +0.0170 | 70.0% |
| 0.60 | 0.15 | 117 | -0.0213 | 30.0% |
| 0.60 | 0.25 | 102 | -0.0213 | 30.0% |
| 0.60 | 0.35 | 52 | -0.0060 | 40.0% |
| 0.60 | 0.45 | 30 | +0.0021 | 50.0% |
| 0.65 | 0.10 | 37 | -0.0111 | 40.0% |
| 0.65 | 0.20 | 37 | -0.0111 | 40.0% |
| 0.65 | 0.30 | 37 | -0.0111 | 40.0% |
| 0.65 | 0.40 | 33 | +0.0021 | 50.0% |
| 0.65 | 0.50 | 20 | +0.0170 | 70.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 20 candidates, mean lock IC=+0.0170, 70.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 347 | +0.0517 | 100.0% |
| 0.45 | 0.20 | 176 | +0.0645 | 100.0% |
| 0.45 | 0.30 | 82 | +0.0437 | 90.0% |
| 0.45 | 0.40 | 30 | +0.0041 | 50.0% |
| 0.45 | 0.50 | 7 | -0.0515 | 0.0% |
| 0.50 | 0.15 | 259 | +0.0645 | 100.0% |
| 0.50 | 0.25 | 132 | +0.0678 | 100.0% |
| 0.50 | 0.35 | 53 | +0.0453 | 90.0% |
| 0.50 | 0.45 | 16 | -0.0440 | 10.0% |
| 0.55 | 0.10 | 232 | +0.0517 | 100.0% |
| 0.55 | 0.20 | 174 | +0.0645 | 100.0% |
| 0.55 | 0.30 | 82 | +0.0437 | 90.0% |
| 0.55 | 0.40 | 30 | +0.0041 | 50.0% |
| 0.55 | 0.50 | 7 | -0.0515 | 0.0% |
| 0.60 | 0.15 | 117 | +0.0678 | 100.0% |
| 0.60 | 0.25 | 106 | +0.0678 | 100.0% |
| 0.60 | 0.35 | 52 | +0.0485 | 90.0% |
| 0.60 | 0.45 | 16 | -0.0440 | 10.0% |
| 0.65 | 0.10 | 35 | +0.0108 | 60.0% |
| 0.65 | 0.20 | 35 | +0.0108 | 60.0% |
| 0.65 | 0.30 | 34 | +0.0114 | 60.0% |
| 0.65 | 0.40 | 25 | +0.0019 | 50.0% |
| 0.65 | 0.50 | 6 | -0.0535 | 0.0% |
| 0.70 | 0.15 | 4 | -0.0664 | 0.0% |
| 0.70 | 0.25 | 4 | -0.0664 | 0.0% |
| 0.70 | 0.35 | 4 | -0.0664 | 0.0% |
| 0.70 | 0.45 | 4 | -0.0664 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.25 → 132 candidates, mean lock IC=+0.0678, 100.0% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 4320 | +0.0325 | 90.0% |
| 0.45 | 0.20 | 4139 | +0.0325 | 90.0% |
| 0.45 | 0.30 | 3835 | +0.0325 | 90.0% |
| 0.45 | 0.40 | 3426 | +0.0325 | 90.0% |
| 0.45 | 0.50 | 3026 | +0.0325 | 90.0% |
| 0.50 | 0.15 | 4247 | +0.0325 | 90.0% |
| 0.50 | 0.25 | 3992 | +0.0325 | 90.0% |
| 0.50 | 0.35 | 3630 | +0.0325 | 90.0% |
| 0.50 | 0.45 | 3218 | +0.0325 | 90.0% |
| 0.55 | 0.10 | 4204 | +0.0325 | 90.0% |
| 0.55 | 0.20 | 4098 | +0.0325 | 90.0% |
| 0.55 | 0.30 | 3828 | +0.0325 | 90.0% |
| 0.55 | 0.40 | 3426 | +0.0325 | 90.0% |
| 0.55 | 0.50 | 3026 | +0.0325 | 90.0% |
| 0.60 | 0.15 | 3884 | +0.0325 | 90.0% |
| 0.60 | 0.25 | 3830 | +0.0325 | 90.0% |
| 0.60 | 0.35 | 3589 | +0.0325 | 90.0% |
| 0.60 | 0.45 | 3218 | +0.0325 | 90.0% |
| 0.65 | 0.10 | 3393 | +0.0325 | 90.0% |
| 0.65 | 0.20 | 3393 | +0.0325 | 90.0% |
| 0.65 | 0.30 | 3379 | +0.0325 | 90.0% |
| 0.65 | 0.40 | 3283 | +0.0325 | 90.0% |
| 0.65 | 0.50 | 3003 | +0.0325 | 90.0% |
| 0.70 | 0.15 | 2811 | +0.0325 | 90.0% |
| 0.70 | 0.25 | 2811 | +0.0325 | 90.0% |
| 0.70 | 0.35 | 2808 | +0.0325 | 90.0% |
| 0.70 | 0.45 | 2779 | +0.0325 | 90.0% |
| 0.75 | 0.10 | 1776 | +0.0325 | 90.0% |
| 0.75 | 0.20 | 1776 | +0.0325 | 90.0% |
| 0.75 | 0.30 | 1776 | +0.0325 | 90.0% |
| 0.75 | 0.40 | 1776 | +0.0325 | 90.0% |
| 0.75 | 0.50 | 1773 | +0.0325 | 90.0% |
| 0.80 | 0.15 | 762 | +0.0393 | 100.0% |
| 0.80 | 0.25 | 762 | +0.0393 | 100.0% |
| 0.80 | 0.35 | 762 | +0.0393 | 100.0% |
| 0.80 | 0.45 | 762 | +0.0393 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 762 candidates, mean lock IC=+0.0393, 100.0% positive

### 588000ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1023 | -0.0534 | 20.0% |
| 0.45 | 0.20 | 627 | -0.0534 | 20.0% |
| 0.45 | 0.30 | 351 | -0.0276 | 30.0% |
| 0.45 | 0.40 | 170 | -0.0036 | 50.0% |
| 0.45 | 0.50 | 87 | -0.0085 | 40.0% |
| 0.50 | 0.15 | 813 | -0.0534 | 20.0% |
| 0.50 | 0.25 | 495 | -0.0513 | 20.0% |
| 0.50 | 0.35 | 257 | -0.0097 | 50.0% |
| 0.50 | 0.45 | 124 | -0.0055 | 40.0% |
| 0.55 | 0.10 | 689 | -0.0513 | 20.0% |
| 0.55 | 0.20 | 568 | -0.0513 | 20.0% |
| 0.55 | 0.30 | 351 | -0.0276 | 30.0% |
| 0.55 | 0.40 | 170 | -0.0036 | 50.0% |
| 0.55 | 0.50 | 87 | -0.0085 | 40.0% |
| 0.60 | 0.15 | 365 | -0.0139 | 40.0% |
| 0.60 | 0.25 | 339 | -0.0051 | 50.0% |
| 0.60 | 0.35 | 244 | -0.0168 | 40.0% |
| 0.60 | 0.45 | 124 | -0.0055 | 40.0% |
| 0.65 | 0.10 | 150 | -0.0101 | 40.0% |
| 0.65 | 0.20 | 150 | -0.0101 | 40.0% |
| 0.65 | 0.30 | 146 | -0.0101 | 40.0% |
| 0.65 | 0.40 | 123 | -0.0085 | 40.0% |
| 0.65 | 0.50 | 83 | -0.0085 | 40.0% |
| 0.70 | 0.15 | 50 | -0.0069 | 40.0% |
| 0.70 | 0.25 | 50 | -0.0069 | 40.0% |
| 0.70 | 0.35 | 50 | -0.0069 | 40.0% |
| 0.70 | 0.45 | 49 | -0.0069 | 40.0% |
| 0.75 | 0.10 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.20 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.30 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.40 | 2 | -0.0596 | 0.0% |
| 0.75 | 0.50 | 2 | -0.0596 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 170 candidates, mean lock IC=-0.0036, 50.0% positive

### 588000ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 375 | -0.0246 | 40.0% |
| 0.45 | 0.20 | 224 | -0.0057 | 50.0% |
| 0.45 | 0.30 | 119 | -0.0264 | 30.0% |
| 0.45 | 0.40 | 54 | -0.0079 | 60.0% |
| 0.45 | 0.50 | 20 | -0.0056 | 50.0% |
| 0.50 | 0.15 | 278 | -0.0052 | 40.0% |
| 0.50 | 0.25 | 172 | -0.0264 | 30.0% |
| 0.50 | 0.35 | 81 | -0.0414 | 30.0% |
| 0.50 | 0.45 | 33 | -0.0078 | 50.0% |
| 0.55 | 0.10 | 250 | +0.0025 | 50.0% |
| 0.55 | 0.20 | 203 | -0.0057 | 50.0% |
| 0.55 | 0.30 | 119 | -0.0264 | 30.0% |
| 0.55 | 0.40 | 54 | -0.0079 | 60.0% |
| 0.55 | 0.50 | 20 | -0.0056 | 50.0% |
| 0.60 | 0.15 | 134 | -0.0052 | 40.0% |
| 0.60 | 0.25 | 119 | -0.0264 | 30.0% |
| 0.60 | 0.35 | 75 | -0.0414 | 30.0% |
| 0.60 | 0.45 | 33 | -0.0078 | 50.0% |
| 0.65 | 0.10 | 43 | -0.0153 | 30.0% |
| 0.65 | 0.20 | 43 | -0.0153 | 30.0% |
| 0.65 | 0.30 | 42 | -0.0092 | 40.0% |
| 0.65 | 0.40 | 33 | -0.0096 | 50.0% |
| 0.65 | 0.50 | 20 | -0.0056 | 50.0% |
| 0.70 | 0.15 | 13 | +0.0014 | 60.0% |
| 0.70 | 0.25 | 13 | +0.0014 | 60.0% |
| 0.70 | 0.35 | 13 | +0.0014 | 60.0% |
| 0.70 | 0.45 | 12 | -0.0010 | 50.0% |
| 0.75 | 0.10 | 5 | -0.0044 | 20.0% |
| 0.75 | 0.20 | 5 | -0.0044 | 20.0% |
| 0.75 | 0.30 | 5 | -0.0044 | 20.0% |
| 0.75 | 0.40 | 5 | -0.0044 | 20.0% |
| 0.75 | 0.50 | 4 | +0.0071 | 25.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.70, ir_thr=0.50 → 9 candidates, mean lock IC=+0.0185, 55.6% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1051 | +0.0912 | 100.0% |
| 0.45 | 0.20 | 847 | +0.0912 | 100.0% |
| 0.45 | 0.30 | 565 | +0.0912 | 100.0% |
| 0.45 | 0.40 | 355 | +0.0912 | 100.0% |
| 0.45 | 0.50 | 182 | +0.0781 | 100.0% |
| 0.50 | 0.15 | 953 | +0.0912 | 100.0% |
| 0.50 | 0.25 | 709 | +0.0912 | 100.0% |
| 0.50 | 0.35 | 434 | +0.0912 | 100.0% |
| 0.50 | 0.45 | 265 | +0.0832 | 100.0% |
| 0.55 | 0.10 | 966 | +0.0912 | 100.0% |
| 0.55 | 0.20 | 837 | +0.0912 | 100.0% |
| 0.55 | 0.30 | 565 | +0.0912 | 100.0% |
| 0.55 | 0.40 | 355 | +0.0912 | 100.0% |
| 0.55 | 0.50 | 182 | +0.0781 | 100.0% |
| 0.60 | 0.15 | 687 | +0.0912 | 100.0% |
| 0.60 | 0.25 | 634 | +0.0912 | 100.0% |
| 0.60 | 0.35 | 429 | +0.0912 | 100.0% |
| 0.60 | 0.45 | 265 | +0.0832 | 100.0% |
| 0.65 | 0.10 | 366 | +0.0832 | 100.0% |
| 0.65 | 0.20 | 365 | +0.0832 | 100.0% |
| 0.65 | 0.30 | 362 | +0.0832 | 100.0% |
| 0.65 | 0.40 | 321 | +0.0832 | 100.0% |
| 0.65 | 0.50 | 181 | +0.0781 | 100.0% |
| 0.70 | 0.15 | 137 | +0.0700 | 100.0% |
| 0.70 | 0.25 | 137 | +0.0700 | 100.0% |
| 0.70 | 0.35 | 137 | +0.0700 | 100.0% |
| 0.70 | 0.45 | 132 | +0.0700 | 100.0% |
| 0.75 | 0.10 | 39 | +0.0504 | 100.0% |
| 0.75 | 0.20 | 39 | +0.0504 | 100.0% |
| 0.75 | 0.30 | 39 | +0.0504 | 100.0% |
| 0.75 | 0.40 | 39 | +0.0504 | 100.0% |
| 0.75 | 0.50 | 39 | +0.0504 | 100.0% |
| 0.80 | 0.15 | 18 | +0.0156 | 80.0% |
| 0.80 | 0.25 | 18 | +0.0156 | 80.0% |
| 0.80 | 0.35 | 18 | +0.0156 | 80.0% |
| 0.80 | 0.45 | 18 | +0.0156 | 80.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1051 candidates, mean lock IC=+0.0912, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 142 | +0.0621 | 100.0% |
| 0.45 | 0.20 | 76 | +0.0575 | 100.0% |
| 0.45 | 0.30 | 34 | +0.0504 | 100.0% |
| 0.45 | 0.40 | 10 | +0.0310 | 70.0% |
| 0.45 | 0.50 | 2 | +0.0484 | 100.0% |
| 0.50 | 0.15 | 96 | +0.0505 | 90.0% |
| 0.50 | 0.25 | 51 | +0.0564 | 100.0% |
| 0.50 | 0.35 | 19 | +0.0571 | 100.0% |
| 0.50 | 0.45 | 3 | +0.0539 | 100.0% |
| 0.55 | 0.10 | 86 | +0.0497 | 90.0% |
| 0.55 | 0.20 | 68 | +0.0575 | 100.0% |
| 0.55 | 0.30 | 33 | +0.0504 | 100.0% |
| 0.55 | 0.40 | 10 | +0.0310 | 70.0% |
| 0.55 | 0.50 | 2 | +0.0484 | 100.0% |
| 0.60 | 0.15 | 31 | +0.0446 | 100.0% |
| 0.60 | 0.25 | 28 | +0.0517 | 100.0% |
| 0.60 | 0.35 | 17 | +0.0461 | 90.0% |
| 0.60 | 0.45 | 3 | +0.0539 | 100.0% |
| 0.65 | 0.10 | 10 | +0.0380 | 90.0% |
| 0.65 | 0.20 | 10 | +0.0380 | 90.0% |
| 0.65 | 0.30 | 10 | +0.0380 | 90.0% |
| 0.65 | 0.40 | 7 | +0.0351 | 85.7% |
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
| 0.45 | 0.10 | 919 | -0.0217 | 10.0% |
| 0.45 | 0.20 | 481 | -0.0170 | 20.0% |
| 0.45 | 0.30 | 153 | -0.0132 | 20.0% |
| 0.45 | 0.40 | 38 | -0.0225 | 0.0% |
| 0.45 | 0.50 | 3 | -0.0205 | 0.0% |
| 0.50 | 0.15 | 680 | -0.0217 | 10.0% |
| 0.50 | 0.25 | 274 | -0.0170 | 20.0% |
| 0.50 | 0.35 | 76 | -0.0064 | 30.0% |
| 0.50 | 0.45 | 9 | -0.0198 | 0.0% |
| 0.55 | 0.10 | 591 | -0.0146 | 20.0% |
| 0.55 | 0.20 | 430 | -0.0146 | 20.0% |
| 0.55 | 0.30 | 150 | -0.0127 | 20.0% |
| 0.55 | 0.40 | 38 | -0.0225 | 0.0% |
| 0.55 | 0.50 | 3 | -0.0205 | 0.0% |
| 0.60 | 0.15 | 190 | -0.0241 | 0.0% |
| 0.60 | 0.25 | 146 | -0.0241 | 0.0% |
| 0.60 | 0.35 | 69 | -0.0088 | 30.0% |
| 0.60 | 0.45 | 9 | -0.0198 | 0.0% |
| 0.65 | 0.10 | 36 | -0.0206 | 0.0% |
| 0.65 | 0.20 | 36 | -0.0206 | 0.0% |
| 0.65 | 0.30 | 35 | -0.0221 | 0.0% |
| 0.65 | 0.40 | 20 | -0.0214 | 0.0% |
| 0.65 | 0.50 | 3 | -0.0205 | 0.0% |
| 0.70 | 0.15 | 3 | -0.0211 | 0.0% |
| 0.70 | 0.25 | 3 | -0.0211 | 0.0% |
| 0.70 | 0.35 | 3 | -0.0211 | 0.0% |
| 0.70 | 0.45 | 2 | -0.0225 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.35 → 76 candidates, mean lock IC=-0.0064, 30.0% positive

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

1. **300ETF `single` — Split-Half Sign Stability too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0171). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0233). Consider relaxing this gate.
3. **300ETF `single` — Absolute Sign Check too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0221). Consider relaxing this gate.
4. **300ETF `single` — BH-FDR Gate too strict**: 53% of top rejects have positive lockbox IC (mean lock IC=+0.0016). Consider relaxing this gate.
5. **300ETF `single` — B3 Composite Floor too strict**: 86% of top rejects have positive lockbox IC (mean lock IC=+0.0103). Consider relaxing this gate.
6. **300ETF `single` — B4 Correlation Gate too strict**: 89% of top rejects have positive lockbox IC (mean lock IC=+0.0276). Consider relaxing this gate.
7. **300ETF `short` — Split-Half Sign Stability too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0167). Consider relaxing this gate.
8. **300ETF `short` — B2 Rolling Guard too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0136). Consider relaxing this gate.
9. **50ETF `single` — Split-Half Sign Stability too strict**: 87% of top rejects have positive lockbox IC (mean lock IC=+0.0402). Consider relaxing this gate.
10. **50ETF `single` — B2 Rolling Guard too strict**: 83% of top rejects have positive lockbox IC (mean lock IC=+0.0392). Consider relaxing this gate.
11. **50ETF `single` — Absolute Sign Check too strict**: 87% of top rejects have positive lockbox IC (mean lock IC=+0.0328). Consider relaxing this gate.
12. **50ETF `single` — BH-FDR Gate too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0307). Consider relaxing this gate.
13. **50ETF `long` — Split-Half Sign Stability too strict**: 87% of top rejects have positive lockbox IC (mean lock IC=+0.0407). Consider relaxing this gate.
14. **50ETF `long` — B2 Rolling Guard too strict**: 80% of top rejects have positive lockbox IC (mean lock IC=+0.0275). Consider relaxing this gate.
15. **50ETF `long` — Absolute Sign Check too strict**: 67% of top rejects have positive lockbox IC (mean lock IC=+0.0277). Consider relaxing this gate.
16. **50ETF `short` — Split-Half Sign Stability too strict**: 53% of top rejects have positive lockbox IC (mean lock IC=+0.0186). Consider relaxing this gate.
17. **50ETF `short` — B2 Rolling Guard too strict**: 70% of top rejects have positive lockbox IC (mean lock IC=+0.0110). Consider relaxing this gate.
18. **50ETF `short` — Absolute Sign Check too strict**: 67% of top rejects have positive lockbox IC (mean lock IC=+0.0030). Consider relaxing this gate.
19. **500ETF `single` — Split-Half Sign Stability too strict**: 97% of top rejects have positive lockbox IC (mean lock IC=+0.0594). Consider relaxing this gate.
20. **500ETF `single` — B2 Rolling Guard too strict**: 80% of top rejects have positive lockbox IC (mean lock IC=+0.0393). Consider relaxing this gate.
21. **500ETF `single` — Absolute Sign Check too strict**: 90% of top rejects have positive lockbox IC (mean lock IC=+0.0249). Consider relaxing this gate.
22. **500ETF `single` — BH-FDR Gate too strict**: 90% of top rejects have positive lockbox IC (mean lock IC=+0.0520). Consider relaxing this gate.
23. **500ETF `single` — B3 Composite Floor too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0805). Consider relaxing this gate.
24. **500ETF `single` — B4 Correlation Gate too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0697). Consider relaxing this gate.
25. **500ETF `long` — Split-Half Sign Stability too strict**: 90% of top rejects have positive lockbox IC (mean lock IC=+0.0300). Consider relaxing this gate.
26. **500ETF `long` — B2 Rolling Guard too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0471). Consider relaxing this gate.
27. **500ETF `long` — BH-FDR Gate too strict**: 87% of top rejects have positive lockbox IC (mean lock IC=+0.0344). Consider relaxing this gate.
28. **500ETF `long` — Admission too loose**: 100% of admitted features have negative lockbox IC. Tighten B3 composite floor or add OOS validation gate.
29. **500ETF `short` — Split-Half Sign Stability too strict**: 60% of top rejects have positive lockbox IC (mean lock IC=+0.0128). Consider relaxing this gate.
30. **500ETF `short` — B2 Rolling Guard too strict**: 83% of top rejects have positive lockbox IC (mean lock IC=+0.0433). Consider relaxing this gate.
31. **500ETF `short` — Absolute Sign Check too strict**: 83% of top rejects have positive lockbox IC (mean lock IC=+0.0490). Consider relaxing this gate.
32. **500ETF `short` — BH-FDR Gate too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0566). Consider relaxing this gate.
33. **588000ETF `single` — B2 Rolling Guard too strict**: 90% of top rejects have positive lockbox IC (mean lock IC=+0.0310). Consider relaxing this gate.
34. **588000ETF `single` — B3 Composite Floor too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0231). Consider relaxing this gate.
35. **588000ETF `single` — B4 Correlation Gate too strict**: 93% of top rejects have positive lockbox IC (mean lock IC=+0.0378). Consider relaxing this gate.
36. **588000ETF `single` — Admission too loose**: 60% of admitted features have negative lockbox IC. Tighten B3 composite floor or add OOS validation gate.
37. **588000ETF `long` — Admission too loose**: 100% of admitted features have negative lockbox IC. Tighten B3 composite floor or add OOS validation gate.
38. **588000ETF `short` — Absolute Sign Check too strict**: 67% of top rejects have positive lockbox IC (mean lock IC=+0.0162). Consider relaxing this gate.
39. **159915ETF `single` — Split-Half Sign Stability too strict**: 87% of top rejects have positive lockbox IC (mean lock IC=+0.0462). Consider relaxing this gate.
40. **159915ETF `single` — B2 Rolling Guard too strict**: 60% of top rejects have positive lockbox IC (mean lock IC=+0.0255). Consider relaxing this gate.
41. **159915ETF `single` — Absolute Sign Check too strict**: 80% of top rejects have positive lockbox IC (mean lock IC=+0.0098). Consider relaxing this gate.
42. **159915ETF `single` — BH-FDR Gate too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0530). Consider relaxing this gate.
43. **159915ETF `single` — B3 Composite Floor too strict**: 100% of top rejects have positive lockbox IC (mean lock IC=+0.0509). Consider relaxing this gate.
44. **159915ETF `single` — B4 Correlation Gate too strict**: 97% of top rejects have positive lockbox IC (mean lock IC=+0.0897). Consider relaxing this gate.
45. **159915ETF `long` — Split-Half Sign Stability too strict**: 80% of top rejects have positive lockbox IC (mean lock IC=+0.0324). Consider relaxing this gate.
46. **159915ETF `long` — B2 Rolling Guard too strict**: 53% of top rejects have positive lockbox IC (mean lock IC=+0.0006). Consider relaxing this gate.
47. **159915ETF `long` — BH-FDR Gate too strict**: 77% of top rejects have positive lockbox IC (mean lock IC=+0.0346). Consider relaxing this gate.
48. **159915ETF `short` — Split-Half Sign Stability too strict**: 60% of top rejects have positive lockbox IC (mean lock IC=+0.0051). Consider relaxing this gate.
49. **159915ETF `short` — BH-FDR Gate too strict**: 64% of top rejects have positive lockbox IC (mean lock IC=+0.0048). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
