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

### 300ETF — `single` (Full Model Lockbox IC: +0.0727, Sharpe: +0.5090)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1188 | +0.0703 | +0.0703 | +0.3240 | 0.90 | 1/8 | 0.73 | 0.73 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0001 | -0.0391 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1119 | +0.0543 | +0.0543 | +0.3473 | 0.77 | 1/8 | 0.75 | 0.80 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0026 | +0.2889 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1186 | +0.0755 | +0.0755 | +0.5654 | 0.70 | 0/8 | 0.53 | 0.48 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0013 | -0.0137 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0999 | +0.0776 | +0.0776 | +0.8447 | 0.65 | 0/8 | 0.49 | 0.62 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0026 | -0.0528 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0965 | +0.0662 | +0.0662 | +0.0044 | 1.02 | 1/8 | 0.66 | 0.75 | — | -0.0034 | +0.0148 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0941 | +0.0566 | +0.0566 | +0.3084 | 0.79 | 1/8 | 0.51 | 1.11 | `volume_weighted_price_position` (1.18) | +0.0011 | +0.1199 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0811 | +0.0539 | +0.0539 | +0.0387 | 0.80 | 0/8 | 0.87 | 1.95 | `volume_weighted_price_position` (1.18) | +0.0017 | -0.0176 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0354 | -0.0017 | -0.0017 | -0.6567 | 1.27 | 1/8 | 2.11 | -4.04 | `volume_weighted_price_position` (1.18) | +0.0011 | +0.0439 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0660 | +0.0417 | +0.0417 | -0.0329 | 0.79 | 1/8 | 1.45 | 1.93 | `limit_down_proximity_early` (1.45) | +0.0006 | +0.0045 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0742 | +0.0529 | +0.0529 | +0.5709 | 0.72 | 1/8 | 0.59 | 0.89 | `bar_vol_0` (1.91) | -0.0012 | +0.0730 |
| `combo_ratio__bar_ret_0__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0928 | +0.0383 | +0.0383 | +0.0933 | 0.58 | 1/8 | 0.54 | 0.79 | `volume_surge_direction` (0.97) | +0.0000 | +0.0000 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0894 | +0.0701 | +0.0701 | +0.3915 | 0.73 | 0/8 | 0.63 | 1.10 | `early_vwap_acceleration` (1.17) | +0.0012 | +0.1314 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1271, Sharpe: +0.5795)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1763 | +0.1217 | +0.1217 | +0.8196 | 0.44 | 0/8 | 0.60 | 0.39 | `opening_drive_thrust_ratio` (0.42) | +0.0048 | -0.2169 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1484 | +0.1175 | +0.1175 | +0.4851 | 0.42 | 0/8 | 0.58 | 0.52 | `close_vs_open_range` (0.47) | +0.0032 | -0.1471 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1650 | +0.1003 | +0.1003 | +0.4546 | 0.41 | 0/8 | 0.57 | 0.65 | `opening_drive_thrust_ratio` (0.42) | -0.0007 | -0.2075 |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Intraday Range Momentum | +1 | +0.1725 | +0.0851 | +0.0851 | +0.4503 | 0.45 | 0/8 | 0.54 | 0.50 | `early_late_momentum_divergence` (0.70) | -0.0016 | -0.4048 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1447 | +0.0976 | +0.0976 | +0.9250 | 0.54 | 0/8 | 0.56 | 0.35 | `star50_limit_proximity_early` (0.61) | +0.0008 | -0.1665 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1269 | +0.0958 | +0.0958 | +0.2125 | 0.61 | 0/8 | 0.58 | 0.47 | `star50_limit_proximity_early` (0.61) | +0.0055 | +0.1625 |
| `combo_min__first_bar_sentiment__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1456 | +0.0787 | +0.0787 | +0.4560 | 0.40 | 0/8 | 0.50 | 0.47 | `first_bar_sentiment` (0.45) | -0.0005 | -0.1213 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1489 | +0.1058 | +0.1058 | +1.1405 | 0.42 | 0/8 | 0.56 | 0.59 | `volume_weighted_momentum_acceleration` (0.57) | +0.0005 | -0.1504 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1562 | +0.0990 | +0.0990 | +0.1521 | 0.37 | 0/8 | 0.51 | 0.53 | `star50_limit_proximity_early` (0.61) | -0.0005 | -0.3238 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1603 | +0.0792 | +0.0792 | +0.3953 | 0.43 | 0/8 | 0.52 | 0.66 | `bar_ret_0` (0.41) | -0.0006 | -0.3109 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1369 | +0.1223 | +0.1223 | +0.4818 | 0.39 | 0/8 | 0.72 | 0.83 | `star50_limit_proximity_early` (0.61) | +0.0038 | -0.1485 |
| `combo_ratio__bar_ret_0__net_volume_flow` | Volatility & Oscillators | +1 | +0.1119 | +0.0500 | +0.0500 | +0.3938 | 0.52 | 0/8 | 0.53 | 0.67 | `bar_ret_0` (0.41) | +0.0011 | -0.0757 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.0947 | -0.0211 | -0.0211 | -0.4893 | 0.85 | 1/8 | 0.50 | 0.17 | `close_vs_open_range` (0.47) | -0.0023 | -0.2380 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1608, Sharpe: +1.7948)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1376 | +0.1458 | +0.1458 | +1.3138 | 0.56 | 0/8 | 1.26 | 1.00 | `star50_limit_proximity_early` (0.69) | +0.0003 | +0.1975 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1603 | +0.1260 | +0.1260 | +1.3254 | 0.45 | 0/8 | 1.04 | 0.74 | `first_bar_sentiment` (0.75) | -0.0027 | +0.2054 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1072 | +0.1075 | +0.1075 | +0.3554 | 0.82 | 1/8 | 1.22 | 0.96 | `yesterday_first_30min_return` (0.92) | +0.0021 | -0.0627 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1127 | +0.1302 | +0.1302 | +0.6763 | 0.66 | 1/8 | 0.77 | 0.68 | `yesterday_first_30min_return` (0.92) | +0.0082 | +0.1216 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1243 | +0.1277 | +0.1277 | +1.0889 | 0.38 | 0/8 | 1.18 | 1.34 | `rbreaker_sell_setup_proximity_early` (0.44) | +0.0021 | +0.1939 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1211 | +0.1169 | +0.1169 | +0.6278 | 0.49 | 0/8 | 1.04 | 0.68 | `late_bar_momentum` (0.82) | +0.0041 | +0.2901 |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1374 | +0.0958 | +0.0958 | +0.8819 | 0.53 | 1/8 | 0.83 | 0.52 | `first_bar_sentiment` (0.75) | -0.0010 | +0.1812 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1095 | +0.1090 | +0.1090 | +0.3724 | 0.66 | 0/8 | 1.03 | 1.15 | `star50_limit_proximity_early` (0.69) | +0.0001 | -0.0698 |
| `volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0795 | +0.1157 | +0.1157 | +1.0095 | 0.69 | 0/8 | 1.44 | 1.58 | — | -0.0001 | +0.0683 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0591 | -0.0132 | -0.0132 | -0.5256 | 0.84 | 2/8 | 0.53 | 0.98 | `volatility_expansion_trend_vector` (0.69) | +0.0006 | +0.4340 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 69.0% lock IC > 0, 30.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3010_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1205 | 30 | 100.0% | 63.3% | +0.0608 | +0.1497 |
| B2 Rolling Guard | 204 | 30 | 100.0% | 93.3% | +0.0554 | +0.3080 |
| BH-FDR Gate | 5 | 5 | 100.0% | 0.0% | +0.0298 | -0.4561 |
| B3 Composite Floor | 35 | 30 | 96.7% | 73.3% | +0.0500 | +0.2891 |
| B4 Correlation Gate | 205 | 30 | 100.0% | 96.7% | +0.0670 | +0.4224 |

**Admitted Pool Summary**: 12 features, False Positive Rate = 16.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0548, Mean Lock Sharpe = +0.2163

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2016, Lock IC=+0.0681, Lock Sharpe=+0.9639
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2164, Lock IC=+0.0791, Lock Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2161, Lock IC=+0.0791, Lock Sharpe=+0.5289
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__first_bar_sentiment`: Train IC=+0.2089, Lock IC=+0.0581, Lock Sharpe=+0.3785
- `combo_tri_min__star50_limit_proximity_early__bar_ret_0__first_bar_sentiment`: Train IC=+0.2086, Lock IC=+0.0581, Lock Sharpe=+0.3785

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1759, Lock IC=+0.0546, Lock Sharpe=+0.7446
- `combo_tri_median__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.1758, Lock IC=+0.0545, Lock Sharpe=+0.7446
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__first_bar_sentiment`: Train IC=+0.1704, Lock IC=+0.0562, Lock Sharpe=+0.6715
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__first_bar_sentiment`: Train IC=+0.1704, Lock IC=+0.0562, Lock Sharpe=+0.6715
- `combo_clamp_diff__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.1843, Lock IC=+0.0574, Lock Sharpe=+0.5286

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2104, Lock IC=+0.0769, Lock Sharpe=+0.8833
- `combo_tri_min__first_bar_return__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1633, Lock IC=+0.0550, Lock Sharpe=+0.6654
- `combo_tri_min__bar_ret_0__first_bar_sentiment__volume_weighted_price_position`: Train IC=+0.1629, Lock IC=+0.0550, Lock Sharpe=+0.6654
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.1982, Lock IC=+0.0610, Lock Sharpe=+0.5317
- `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1979, Lock IC=+0.0611, Lock Sharpe=+0.5317

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2593, Lock IC=+0.0877, Lock Sharpe=+1.0876
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2265, Lock IC=+0.0937, Lock Sharpe=+1.0629
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2691, Lock IC=+0.0706, Lock Sharpe=+0.8555
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Lock Sharpe=+0.5292
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Lock Sharpe=+0.5292

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

_Null Baseline (un-gated candidate pool): 74.0% lock IC > 0, 19.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3818_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 837 | 30 | 86.7% | 53.3% | +0.0205 | -0.0069 |
| B2 Rolling Guard | 46 | 30 | 56.7% | 6.7% | +0.0078 | -0.4555 |
| BH-FDR Gate | 1 | 1 | 100.0% | 100.0% | +0.0071 | +0.0067 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1396, Lock IC=+0.0321, Lock Sharpe=+0.5189
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.1615, Lock IC=+0.0418, Lock Sharpe=+0.4378
- `combo_mean__bar_vol_4__first_bar_volume`: Train IC=+0.1418, Lock IC=+0.0144, Lock Sharpe=+0.3220
- `combo_z_sum__bar_vol_4__first_bar_volume`: Train IC=+0.1418, Lock IC=+0.0144, Lock Sharpe=+0.3220
- `combo_mean__bar_vol_4__bar_vol_0`: Train IC=+0.1418, Lock IC=+0.0144, Lock Sharpe=+0.3220

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.1441, Lock IC=+0.0059, Lock Sharpe=+0.1981
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1441, Lock IC=+0.0059, Lock Sharpe=+0.1981

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `star50_limit_proximity_early`: Train IC=+0.1457, Lock IC=+0.0071, Lock Sharpe=+0.0067

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

_Null Baseline (un-gated candidate pool): 75.0% lock IC > 0, 40.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0571_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1823 | 30 | 100.0% | 86.7% | +0.0932 | +0.4943 |
| B2 Rolling Guard | 242 | 30 | 100.0% | 70.0% | +0.0753 | +0.2370 |
| BH-FDR Gate | 7 | 7 | 85.7% | 0.0% | +0.0145 | -0.6172 |
| B3 Composite Floor | 156 | 30 | 100.0% | 100.0% | +0.0955 | +0.5158 |
| B4 Correlation Gate | 629 | 30 | 100.0% | 100.0% | +0.1086 | +0.7037 |

**Admitted Pool Summary**: 13 features, False Positive Rate = 7.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0872, Mean Lock Sharpe = +0.4356

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2305, Lock IC=+0.1016, Lock Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Lock Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Lock Sharpe=+0.9464
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.2819, Lock IC=+0.1134, Lock Sharpe=+0.8586
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2977, Lock IC=+0.1185, Lock Sharpe=+0.8115

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__body_size_progression__first_bar_return`: Train IC=+0.1879, Lock IC=+0.0787, Lock Sharpe=+0.7240
- `combo_z_diff__body_size_progression__first_bar_return`: Train IC=+0.1879, Lock IC=+0.0787, Lock Sharpe=+0.7240
- `combo_rel_diff__body_size_progression__first_bar_return`: Train IC=+0.1891, Lock IC=+0.0693, Lock Sharpe=+0.5882
- `combo_rel_diff__body_size_progression__bar_ret_0`: Train IC=+0.1880, Lock IC=+0.0693, Lock Sharpe=+0.5882
- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Lock Sharpe=+0.5808

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Lock Sharpe=+1.1317
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Lock Sharpe=+1.1317
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.3150, Lock IC=+0.1141, Lock Sharpe=+0.9327

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

_Null Baseline (un-gated candidate pool): 86.0% lock IC > 0, 66.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.3418_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1181 | 30 | 100.0% | 93.3% | +0.0987 | +0.8258 |
| B2 Rolling Guard | 312 | 30 | 100.0% | 96.7% | +0.1050 | +0.7043 |
| BH-FDR Gate | 2 | 2 | 0.0% | 0.0% | -0.0292 | -1.0342 |
| B3 Composite Floor | 148 | 30 | 100.0% | 100.0% | +0.1138 | +1.0690 |
| B4 Correlation Gate | 172 | 30 | 100.0% | 100.0% | +0.1273 | +1.3422 |

**Admitted Pool Summary**: 10 features, False Positive Rate = 10.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1059, Mean Lock Sharpe = +0.6937

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2086, Lock IC=+0.1325, Lock Sharpe=+1.9186
- `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`: Train IC=+0.2246, Lock IC=+0.1331, Lock Sharpe=+1.8587
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2421, Lock IC=+0.0980, Lock Sharpe=+1.7078
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Lock Sharpe=+1.3789
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Lock Sharpe=+1.3789

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Lock Sharpe=+1.3582
- `combo_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2299, Lock IC=+0.1187, Lock Sharpe=+1.1602
- `combo_z_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2299, Lock IC=+0.1187, Lock Sharpe=+1.1602
- `combo_rel_diff__first_bar_return__demark_setup_reversal_early`: Train IC=+0.2261, Lock IC=+0.1187, Lock Sharpe=+1.1071
- `combo_rel_diff__bar_ret_0__demark_setup_reversal_early`: Train IC=+0.2236, Lock IC=+0.1199, Lock Sharpe=+1.1071

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2321, Lock IC=+0.1334, Lock Sharpe=+1.9776
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2321, Lock IC=+0.1334, Lock Sharpe=+1.9776
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3073, Lock IC=+0.1158, Lock Sharpe=+1.5577
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2324, Lock IC=+0.1197, Lock Sharpe=+1.5206
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2324, Lock IC=+0.1197, Lock Sharpe=+1.5206

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Lock Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Lock Sharpe=+1.6742
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2819, Lock IC=+0.1269, Lock Sharpe=+1.6324
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Lock Sharpe=+1.6287
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Lock Sharpe=+1.6287

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
| 0.45 | 0.10 | 529 | +0.0704 | 100.0% |
| 0.45 | 0.20 | 515 | +0.0704 | 100.0% |
| 0.45 | 0.30 | 462 | +0.0704 | 100.0% |
| 0.45 | 0.40 | 329 | +0.0704 | 100.0% |
| 0.45 | 0.50 | 198 | +0.0704 | 100.0% |
| 0.50 | 0.15 | 523 | +0.0704 | 100.0% |
| 0.50 | 0.25 | 500 | +0.0704 | 100.0% |
| 0.50 | 0.35 | 406 | +0.0704 | 100.0% |
| 0.50 | 0.45 | 271 | +0.0704 | 100.0% |
| 0.55 | 0.10 | 522 | +0.0704 | 100.0% |
| 0.55 | 0.20 | 515 | +0.0704 | 100.0% |
| 0.55 | 0.30 | 462 | +0.0704 | 100.0% |
| 0.55 | 0.40 | 329 | +0.0704 | 100.0% |
| 0.55 | 0.50 | 198 | +0.0704 | 100.0% |
| 0.60 | 0.15 | 484 | +0.0704 | 100.0% |
| 0.60 | 0.25 | 481 | +0.0704 | 100.0% |
| 0.60 | 0.35 | 406 | +0.0704 | 100.0% |
| 0.60 | 0.45 | 271 | +0.0704 | 100.0% |
| 0.65 | 0.10 | 345 | +0.0704 | 100.0% |
| 0.65 | 0.20 | 345 | +0.0704 | 100.0% |
| 0.65 | 0.30 | 345 | +0.0704 | 100.0% |
| 0.65 | 0.40 | 314 | +0.0704 | 100.0% |
| 0.65 | 0.50 | 198 | +0.0704 | 100.0% |
| 0.70 | 0.15 | 166 | +0.0704 | 100.0% |
| 0.70 | 0.25 | 166 | +0.0704 | 100.0% |
| 0.70 | 0.35 | 166 | +0.0704 | 100.0% |
| 0.70 | 0.45 | 166 | +0.0704 | 100.0% |
| 0.75 | 0.10 | 53 | +0.0634 | 100.0% |
| 0.75 | 0.20 | 53 | +0.0634 | 100.0% |
| 0.75 | 0.30 | 53 | +0.0634 | 100.0% |
| 0.75 | 0.40 | 53 | +0.0634 | 100.0% |
| 0.75 | 0.50 | 53 | +0.0634 | 100.0% |
| 0.80 | 0.15 | 17 | +0.0380 | 100.0% |
| 0.80 | 0.25 | 17 | +0.0380 | 100.0% |
| 0.80 | 0.35 | 17 | +0.0380 | 100.0% |
| 0.80 | 0.45 | 17 | +0.0380 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 529 candidates, mean lock IC=+0.0704, 100.0% positive

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
| 0.45 | 0.10 | 380 | +0.0616 | 100.0% |
| 0.45 | 0.20 | 374 | +0.0616 | 100.0% |
| 0.45 | 0.30 | 361 | +0.0616 | 100.0% |
| 0.45 | 0.40 | 350 | +0.0616 | 100.0% |
| 0.45 | 0.50 | 345 | +0.0616 | 100.0% |
| 0.50 | 0.15 | 377 | +0.0616 | 100.0% |
| 0.50 | 0.25 | 371 | +0.0616 | 100.0% |
| 0.50 | 0.35 | 354 | +0.0616 | 100.0% |
| 0.50 | 0.45 | 347 | +0.0616 | 100.0% |
| 0.55 | 0.10 | 378 | +0.0616 | 100.0% |
| 0.55 | 0.20 | 374 | +0.0616 | 100.0% |
| 0.55 | 0.30 | 361 | +0.0616 | 100.0% |
| 0.55 | 0.40 | 350 | +0.0616 | 100.0% |
| 0.55 | 0.50 | 345 | +0.0616 | 100.0% |
| 0.60 | 0.15 | 366 | +0.0616 | 100.0% |
| 0.60 | 0.25 | 364 | +0.0616 | 100.0% |
| 0.60 | 0.35 | 354 | +0.0616 | 100.0% |
| 0.60 | 0.45 | 347 | +0.0616 | 100.0% |
| 0.65 | 0.10 | 349 | +0.0616 | 100.0% |
| 0.65 | 0.20 | 349 | +0.0616 | 100.0% |
| 0.65 | 0.30 | 348 | +0.0616 | 100.0% |
| 0.65 | 0.40 | 347 | +0.0616 | 100.0% |
| 0.65 | 0.50 | 345 | +0.0616 | 100.0% |
| 0.70 | 0.15 | 344 | +0.0616 | 100.0% |
| 0.70 | 0.25 | 344 | +0.0616 | 100.0% |
| 0.70 | 0.35 | 344 | +0.0616 | 100.0% |
| 0.70 | 0.45 | 344 | +0.0616 | 100.0% |
| 0.75 | 0.10 | 319 | +0.0661 | 100.0% |
| 0.75 | 0.20 | 319 | +0.0661 | 100.0% |
| 0.75 | 0.30 | 319 | +0.0661 | 100.0% |
| 0.75 | 0.40 | 319 | +0.0661 | 100.0% |
| 0.75 | 0.50 | 319 | +0.0661 | 100.0% |
| 0.80 | 0.15 | 271 | +0.0343 | 80.0% |
| 0.80 | 0.25 | 271 | +0.0343 | 80.0% |
| 0.80 | 0.35 | 271 | +0.0343 | 80.0% |
| 0.80 | 0.45 | 271 | +0.0343 | 80.0% |

**Optimal**: mono_thr=0.75, ir_thr=0.10 → 319 candidates, mean lock IC=+0.0661, 100.0% positive

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
| 0.45 | 0.10 | 1370 | +0.1119 | 100.0% |
| 0.45 | 0.20 | 1350 | +0.1119 | 100.0% |
| 0.45 | 0.30 | 1301 | +0.1119 | 100.0% |
| 0.45 | 0.40 | 1170 | +0.1119 | 100.0% |
| 0.45 | 0.50 | 920 | +0.1119 | 100.0% |
| 0.50 | 0.15 | 1364 | +0.1119 | 100.0% |
| 0.50 | 0.25 | 1332 | +0.1119 | 100.0% |
| 0.50 | 0.35 | 1239 | +0.1119 | 100.0% |
| 0.50 | 0.45 | 1063 | +0.1119 | 100.0% |
| 0.55 | 0.10 | 1369 | +0.1119 | 100.0% |
| 0.55 | 0.20 | 1350 | +0.1119 | 100.0% |
| 0.55 | 0.30 | 1301 | +0.1119 | 100.0% |
| 0.55 | 0.40 | 1170 | +0.1119 | 100.0% |
| 0.55 | 0.50 | 920 | +0.1119 | 100.0% |
| 0.60 | 0.15 | 1321 | +0.1119 | 100.0% |
| 0.60 | 0.25 | 1317 | +0.1119 | 100.0% |
| 0.60 | 0.35 | 1238 | +0.1119 | 100.0% |
| 0.60 | 0.45 | 1063 | +0.1119 | 100.0% |
| 0.65 | 0.10 | 1157 | +0.1119 | 100.0% |
| 0.65 | 0.20 | 1157 | +0.1119 | 100.0% |
| 0.65 | 0.30 | 1157 | +0.1119 | 100.0% |
| 0.65 | 0.40 | 1117 | +0.1119 | 100.0% |
| 0.65 | 0.50 | 920 | +0.1119 | 100.0% |
| 0.70 | 0.15 | 824 | +0.1119 | 100.0% |
| 0.70 | 0.25 | 824 | +0.1119 | 100.0% |
| 0.70 | 0.35 | 824 | +0.1119 | 100.0% |
| 0.70 | 0.45 | 824 | +0.1119 | 100.0% |
| 0.75 | 0.10 | 410 | +0.1119 | 100.0% |
| 0.75 | 0.20 | 410 | +0.1119 | 100.0% |
| 0.75 | 0.30 | 410 | +0.1119 | 100.0% |
| 0.75 | 0.40 | 410 | +0.1119 | 100.0% |
| 0.75 | 0.50 | 410 | +0.1119 | 100.0% |
| 0.80 | 0.15 | 141 | +0.1106 | 100.0% |
| 0.80 | 0.25 | 141 | +0.1106 | 100.0% |
| 0.80 | 0.35 | 141 | +0.1106 | 100.0% |
| 0.80 | 0.45 | 141 | +0.1106 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1370 candidates, mean lock IC=+0.1119, 100.0% positive

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
| 0.45 | 0.10 | 690 | +0.1325 | 100.0% |
| 0.45 | 0.20 | 660 | +0.1325 | 100.0% |
| 0.45 | 0.30 | 573 | +0.1325 | 100.0% |
| 0.45 | 0.40 | 404 | +0.1325 | 100.0% |
| 0.45 | 0.50 | 236 | +0.1325 | 100.0% |
| 0.50 | 0.15 | 685 | +0.1325 | 100.0% |
| 0.50 | 0.25 | 630 | +0.1325 | 100.0% |
| 0.50 | 0.35 | 492 | +0.1325 | 100.0% |
| 0.50 | 0.45 | 325 | +0.1325 | 100.0% |
| 0.55 | 0.10 | 681 | +0.1325 | 100.0% |
| 0.55 | 0.20 | 659 | +0.1325 | 100.0% |
| 0.55 | 0.30 | 573 | +0.1325 | 100.0% |
| 0.55 | 0.40 | 404 | +0.1325 | 100.0% |
| 0.55 | 0.50 | 236 | +0.1325 | 100.0% |
| 0.60 | 0.15 | 621 | +0.1325 | 100.0% |
| 0.60 | 0.25 | 604 | +0.1325 | 100.0% |
| 0.60 | 0.35 | 489 | +0.1325 | 100.0% |
| 0.60 | 0.45 | 325 | +0.1325 | 100.0% |
| 0.65 | 0.10 | 408 | +0.1325 | 100.0% |
| 0.65 | 0.20 | 408 | +0.1325 | 100.0% |
| 0.65 | 0.30 | 408 | +0.1325 | 100.0% |
| 0.65 | 0.40 | 366 | +0.1325 | 100.0% |
| 0.65 | 0.50 | 236 | +0.1325 | 100.0% |
| 0.70 | 0.15 | 159 | +0.1325 | 100.0% |
| 0.70 | 0.25 | 159 | +0.1325 | 100.0% |
| 0.70 | 0.35 | 159 | +0.1325 | 100.0% |
| 0.70 | 0.45 | 157 | +0.1325 | 100.0% |
| 0.75 | 0.10 | 37 | +0.1179 | 100.0% |
| 0.75 | 0.20 | 37 | +0.1179 | 100.0% |
| 0.75 | 0.30 | 37 | +0.1179 | 100.0% |
| 0.75 | 0.40 | 37 | +0.1179 | 100.0% |
| 0.75 | 0.50 | 37 | +0.1179 | 100.0% |
| 0.80 | 0.15 | 6 | +0.0417 | 66.7% |
| 0.80 | 0.25 | 6 | +0.0417 | 66.7% |
| 0.80 | 0.35 | 6 | +0.0417 | 66.7% |
| 0.80 | 0.45 | 6 | +0.0417 | 66.7% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 690 candidates, mean lock IC=+0.1325, 100.0% positive

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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1294 | +0.0000 | +0.0711 | 0.55x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1143 | +0.0000 | +0.0543 | 0.47x | 2017-05-09 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1235 | +0.0000 | +0.0755 | 0.61x | 2017-07-10 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.0965 | +0.0000 | +0.0776 | 0.80x | 2013-09-23 |
| `rbreaker_sell_setup_proximity_early` | +0.0962 | +0.0000 | +0.0662 | 0.69x | 2016-08-24 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +0.1103 | +0.0000 | +0.0566 | 0.51x | 2015-03-16 |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | +0.0955 | +0.0000 | +0.0539 | 0.56x | 2015-02-06 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0431 | +0.0000 | -0.0017 | -0.04x | 2010-10-15 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +0.0511 | +0.0000 | +0.0417 | 0.81x | 2012-10-09 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +0.0655 | +0.0000 | +0.0529 | 0.81x | 2017-10-12 |
| `combo_ratio__bar_ret_0__volume_surge_direction` | +0.0812 | +0.0000 | +0.0383 | 0.47x | 2010-10-15 |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | +0.1120 | +0.0000 | +0.0701 | 0.63x | 2017-02-06 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1976 | +0.0000 | +0.1217 | 0.62x | No decay |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1692 | +0.0000 | +0.1175 | 0.69x | 2020-01-06 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | +0.1995 | +0.0000 | +0.1003 | 0.50x | 2016-11-30 |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | +0.1749 | +0.0000 | +0.0851 | 0.49x | 2019-12-05 |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | +0.1475 | +0.0000 | +0.0972 | 0.66x | 2016-08-24 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1473 | +0.0000 | +0.0958 | 0.65x | 2016-08-24 |
| `combo_min__first_bar_sentiment__first_bar_return` | +0.1400 | +0.0000 | +0.0787 | 0.56x | 2013-09-23 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1531 | +0.0000 | +0.1058 | 0.69x | No decay |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +0.1677 | +0.0000 | +0.0990 | 0.59x | 2021-05-28 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1680 | +0.0000 | +0.0792 | 0.47x | 2017-04-07 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1398 | +0.0000 | +0.1223 | 0.88x | 2011-12-23 |
| `combo_ratio__bar_ret_0__net_volume_flow` | +0.1031 | +0.0000 | +0.0500 | 0.49x | 2013-09-23 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | +0.0641 | +0.0000 | -0.0211 | -0.33x | 2010-10-15 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1538 | +0.0000 | +0.1458 | 0.95x | 2016-10-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1666 | +0.0000 | +0.1260 | 0.76x | 2017-01-20 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1021 | +0.0000 | +0.1075 | 1.05x | 2011-10-18 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1186 | +0.0000 | +0.1312 | 1.11x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1417 | +0.0000 | +0.1277 | 0.90x | 2017-01-20 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +0.1252 | +0.0000 | +0.1169 | 0.93x | 2011-03-11 |
| `combo_tri_min__first_bar_sentiment__bar_body_rng_0__first_bar_return` | +0.1456 | +0.0000 | +0.0958 | 0.66x | 2017-02-27 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1067 | +0.0000 | +0.1090 | 1.02x | 2011-10-18 |
| `volatility_expansion_trend_vector` | +0.1263 | +0.0000 | +0.1157 | 0.92x | 2016-10-24 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0622 | +0.0000 | -0.0132 | -0.21x | 2012-02-22 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 63.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.1497). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.3080). Consider relaxing this gate.
3. **300ETF `single` — B3 Composite Floor too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.2891). Consider relaxing this gate.
4. **300ETF `single` — B4 Correlation Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.4224). Consider relaxing this gate.
5. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2417). Consider relaxing this gate.
6. **300ETF `short` — BH-FDR Gate too strict**: 85.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=+0.2273). Consider relaxing this gate.
7. **300ETF `short` — B3 Composite Floor too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.1028). Consider relaxing this gate.
8. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 19.0%, mean lock Sharpe=-0.0069). Consider relaxing this gate.
9. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.2106). Consider relaxing this gate.
10. **50ETF `short` — BH-FDR Gate too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.5453). Consider relaxing this gate.
11. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 40.0%, mean lock Sharpe=+0.4943). Consider relaxing this gate.
12. **500ETF `single` — B2 Rolling Guard too strict**: 70.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 40.0%, mean lock Sharpe=+0.2370). Consider relaxing this gate.
13. **500ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 40.0%, mean lock Sharpe=+0.5158). Consider relaxing this gate.
14. **500ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 40.0%, mean lock Sharpe=+0.7037). Consider relaxing this gate.
15. **500ETF `long` — BH-FDR Gate too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.1712). Consider relaxing this gate.
16. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.1404). Consider relaxing this gate.
17. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 66.0%, mean lock Sharpe=+1.0690). Consider relaxing this gate.
18. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 66.0%, mean lock Sharpe=+1.3422). Consider relaxing this gate.
19. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+0.6527). Consider relaxing this gate.
20. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.1320). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
