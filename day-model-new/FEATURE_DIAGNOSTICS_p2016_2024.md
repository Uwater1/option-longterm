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

### 300ETF — `single` (Full Model Lockbox IC: +0.0306, Sharpe: +0.2489)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0999 | +0.0354 | +0.0354 | +0.0566 | 0.63 | 0/8 | 0.84 | 1.98 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0047 | +0.2185 |
| `combo_rank_min__volume_weighted_price_position__bar_body_rng_0` | Volatility & Oscillators | +1 | +0.0999 | +0.0141 | +0.0141 | -0.2026 | 0.89 | 1/8 | 0.89 | 2.80 | `volume_weighted_price_position` (1.11) | +0.0009 | +0.0520 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | Volatility & Oscillators | +1 | +0.0915 | -0.0131 | -0.0131 | -0.5701 | 0.90 | 2/8 | 1.54 | 6.91 | `volume_weighted_price_position` (1.11) | -0.0044 | +0.0087 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | Gap / Overnight Reversal | +1 | +0.0915 | -0.0023 | -0.0023 | -0.5759 | 0.82 | 0/8 | 1.74 | 3.10 | `volume_weighted_price_position` (1.11) | +0.0000 | -0.0139 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0882 | +0.0655 | +0.0655 | +0.9697 | 0.82 | 1/8 | 0.80 | 8.68 | `rbreaker_buy_setup_proximity_early` (2.08) | +0.0057 | +0.0088 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | Intraday Range Momentum | +1 | +0.0911 | -0.0067 | -0.0067 | -1.0941 | 0.86 | 1/8 | 1.09 | 3.24 | `max_up_ret` (0.89) | -0.0047 | -0.0543 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1022 | +0.0351 | +0.0351 | +0.1736 | 0.87 | 1/8 | 1.13 | -40.14 | `rbreaker_sell_setup_proximity_early` (1.07) | +0.0009 | -0.0050 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0405 | -0.0158 | -0.0158 | -1.0471 | 0.88 | 1/8 | 0.77 | 20.36 | `volume_weighted_price_position` (1.11) | -0.0011 | -0.0926 |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0324 | -0.0099 | -0.0099 | -0.2153 | 1.33 | 1/8 | 0.61 | 1.54 | `max_up_ret` (0.89) | -0.0027 | +0.2314 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0898 | +0.0050 | +0.0050 | +0.2005 | 0.58 | 1/8 | 0.60 | 0.82 | `volume_surge_direction` (0.95) | +0.0000 | +0.0000 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0719 | +0.0288 | +0.0288 | -0.2338 | 0.74 | 1/8 | 1.21 | 1.24 | `bar_vol_0` (2.19) | +0.0050 | +0.1578 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0523 | +0.0203 | +0.0203 | +0.1467 | 0.65 | 1/8 | 0.64 | 1.19 | `smooth_momentum_structure` (0.77) | +0.0024 | +0.3094 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1127, Sharpe: +0.7411)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1302 | +0.0955 | +0.0955 | +0.5066 | 0.36 | 0/8 | 0.80 | 0.67 | `trend_bar_close_consistency` (0.66) | +0.0005 | +0.0695 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Intraday Range Momentum | +1 | +0.1231 | +0.0586 | +0.0586 | -0.0789 | 0.35 | 0/8 | 0.74 | 0.67 | `bar_ret_0` (0.46) | -0.0045 | -0.1139 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1202 | +0.0742 | +0.0742 | +0.1097 | 0.42 | 0/8 | 0.52 | 0.42 | `bar_ret_0` (0.46) | -0.0002 | -0.0399 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1412 | +0.1193 | +0.1193 | +0.5966 | 0.44 | 0/8 | 0.66 | 0.32 | `opening_drive_thrust_ratio` (0.40) | +0.0084 | -0.1735 |
| `combo_rel_diff__max_up_ret__body_size_progression` | Intraday Range Momentum | +1 | +0.1350 | +0.0747 | +0.0747 | +0.2436 | 0.35 | 0/8 | 0.70 | 0.51 | `body_size_progression` (0.60) | -0.0010 | +0.1237 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1496 | +0.0874 | +0.0874 | +0.8706 | 0.42 | 0/8 | 0.70 | 0.61 | `volume_weighted_momentum_acceleration` (0.62) | -0.0003 | +0.1861 |
| `combo_max__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1239 | +0.0818 | +0.0818 | +0.0961 | 0.51 | 0/8 | 0.50 | 0.39 | `max_down_ret` (0.62) | +0.0009 | +0.0349 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1104 | +0.1566 | +0.1566 | +0.5389 | 0.44 | 0/8 | 0.51 | 0.67 | `max_down_ret` (0.62) | +0.0082 | +0.0551 |
| `vwap_trend_channel_slope` | Other Technical | +1 | +0.0836 | +0.0712 | +0.0712 | -0.3626 | 0.51 | 0/8 | 1.11 | 0.90 | — | +0.0038 | -0.0808 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Intraday Range Momentum | +1 | +0.0944 | +0.1148 | +0.1148 | -0.0882 | 0.57 | 0/8 | 0.84 | 0.54 | `star50_limit_proximity_early` (0.55) | +0.0056 | -0.0468 |
| `combo_diff__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.0701 | +0.0120 | +0.0120 | -0.8026 | 0.95 | 0/8 | 0.34 | 0.22 | `max_down_ret` (0.62) | -0.0030 | -0.1277 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1366, Sharpe: +1.4256)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1446 | +0.1235 | +0.1235 | +0.8704 | 0.52 | 1/8 | 1.10 | 2.98 | `bar_body_rng_0` (0.54) | +0.0045 | -0.1117 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1163 | +0.0911 | +0.0911 | +0.5434 | 0.62 | 1/8 | 1.30 | 4.55 | `yesterday_early_vwap_dev` (1.10) | +0.0090 | +0.2603 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1248 | +0.1283 | +0.1283 | +1.6959 | 0.57 | 1/8 | 1.04 | 1.71 | `volume_weighted_price_position` (0.77) | +0.0021 | +0.0890 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1262 | +0.0760 | +0.0760 | +0.1170 | 0.44 | 0/8 | 1.14 | 1.62 | `first_bar_sentiment` (0.76) | -0.0034 | -0.0181 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1284 | +0.1327 | +0.1327 | +0.9738 | 0.39 | 0/8 | 1.62 | 3.11 | `star50_limit_proximity_early` (0.68) | -0.0003 | -0.2155 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.1052 | +0.0904 | +0.0904 | +0.8135 | 0.42 | 0/8 | 1.62 | 2.75 | `impulse_bar_dominance` (1.04) | -0.0009 | -0.1888 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0943 | +0.1204 | +0.1204 | +1.1103 | 0.81 | 2/8 | 1.49 | -9.71 | `rbreaker_buy_setup_proximity_early` (1.12) | +0.0028 | -0.0629 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1024 | +0.1088 | +0.1088 | +0.4427 | 0.72 | 1/8 | 1.83 | 5.08 | `yesterday_early_vwap_dev` (1.10) | +0.0027 | -0.1016 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0859 | +0.0677 | +0.0677 | -0.1117 | 0.63 | 0/8 | 1.66 | 3.03 | `volume_weighted_price_position` (0.77) | +0.0002 | +0.0232 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0727 | +0.0259 | +0.0259 | +0.0683 | 0.28 | 0/8 | 1.63 | 1.21 | `rbreaker_buy_setup_proximity_early` (1.12) | +0.0005 | +0.0476 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0672 | -0.0273 | -0.0273 | +0.1690 | 0.52 | 0/8 | 0.75 | 0.64 | `volatility_expansion_trend_vector` (0.74) | -0.0043 | -0.0720 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 62.0% lock IC > 0, 30.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3373_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1196 | 30 | 86.7% | 26.7% | +0.0168 | -0.3578 |
| B2 Rolling Guard | 143 | 30 | 90.0% | 23.3% | +0.0126 | -0.1873 |
| BH-FDR Gate | 12 | 12 | 25.0% | 8.3% | -0.0108 | -0.6615 |
| B3 Composite Floor | 2 | 2 | 100.0% | 0.0% | +0.0102 | -0.3704 |
| B4 Correlation Gate | 255 | 30 | 73.3% | 43.3% | +0.0170 | +0.0656 |

**Admitted Pool Summary**: 19 features, False Positive Rate = 42.1% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0167, Mean Lock Sharpe = +0.0140

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Lock Sharpe=+0.5188
- `combo_z_sum__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1956, Lock IC=+0.0346, Lock Sharpe=+0.5188
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__first_bar_sentiment`: Train IC=+0.2062, Lock IC=+0.0300, Lock Sharpe=+0.3444
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__first_bar_sentiment`: Train IC=+0.2058, Lock IC=+0.0300, Lock Sharpe=+0.3444
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`: Train IC=+0.1994, Lock IC=+0.0197, Lock Sharpe=+0.3124

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1676, Lock IC=+0.0217, Lock Sharpe=+0.1912
- `combo_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1674, Lock IC=+0.0242, Lock Sharpe=+0.1912
- `combo_z_diff__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.1674, Lock IC=+0.0242, Lock Sharpe=+0.1912
- `combo_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1719, Lock IC=+0.0140, Lock Sharpe=+0.1415
- `combo_z_diff__volume_weighted_momentum_acceleration__first_bar_sentiment`: Train IC=+0.1719, Lock IC=+0.0140, Lock Sharpe=+0.1415

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1066, Lock IC=+0.0378, Lock Sharpe=+0.1611

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2291, Lock IC=+0.0645, Lock Sharpe=+0.9458
- `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2502, Lock IC=+0.0505, Lock Sharpe=+0.7439
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2350, Lock IC=+0.0270, Lock Sharpe=+0.5172
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2251, Lock IC=+0.0254, Lock Sharpe=+0.4883
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2341, Lock IC=+0.0362, Lock Sharpe=+0.3660

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

_Null Baseline (un-gated candidate pool): 78.0% lock IC > 0, 50.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0328_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1903 | 30 | 100.0% | 96.7% | +0.1026 | +0.6891 |
| B2 Rolling Guard | 357 | 30 | 100.0% | 90.0% | +0.0834 | +0.4624 |
| BH-FDR Gate | 8 | 8 | 87.5% | 12.5% | +0.0240 | -0.3213 |
| B3 Composite Floor | 15 | 15 | 100.0% | 86.7% | +0.0625 | +0.2102 |
| B4 Correlation Gate | 533 | 30 | 100.0% | 100.0% | +0.1003 | +0.6330 |

**Admitted Pool Summary**: 29 features, False Positive Rate = 13.8% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0903, Mean Lock Sharpe = +0.3550

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2273, Lock IC=+0.1225, Lock Sharpe=+1.2571
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2344, Lock IC=+0.1237, Lock Sharpe=+1.1553
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2329, Lock IC=+0.1040, Lock Sharpe=+1.1505
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2618, Lock IC=+0.1189, Lock Sharpe=+1.0221
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2294, Lock IC=+0.1098, Lock Sharpe=+0.9794

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.1971, Lock IC=+0.1117, Lock Sharpe=+1.2590
- `combo_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.1976, Lock IC=+0.1229, Lock Sharpe=+1.2071
- `combo_rank_min__star50_limit_proximity_early__close_vs_open_range`: Train IC=+0.2070, Lock IC=+0.1247, Lock Sharpe=+1.1213
- `combo_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.1870, Lock IC=+0.1042, Lock Sharpe=+1.0918
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Train IC=+0.1879, Lock IC=+0.0666, Lock Sharpe=+0.7913

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__max_up_ret__smooth_momentum_structure__first_bar_sentiment`: Train IC=+0.0830, Lock IC=+0.0744, Lock Sharpe=+0.6203

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1934, Lock IC=+0.0908, Lock Sharpe=+0.5788
- `combo_tri_median__opening_drive_thrust_ratio__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.1912, Lock IC=+0.0954, Lock Sharpe=+0.5787
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.1424, Lock IC=+0.0686, Lock Sharpe=+0.4355
- `combo_rank_max__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.1424, Lock IC=+0.0686, Lock Sharpe=+0.4355
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__trend_bar_close_consistency`: Train IC=+0.1801, Lock IC=+0.0873, Lock Sharpe=+0.3627

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__volatility_expansion_trend_vector`: Train IC=+0.2537, Lock IC=+0.1136, Lock Sharpe=+1.0585
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2665, Lock IC=+0.1105, Lock Sharpe=+0.9584
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__first_bar_sentiment`: Train IC=+0.2651, Lock IC=+0.1143, Lock Sharpe=+0.9484
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.2651, Lock IC=+0.1143, Lock Sharpe=+0.9484
- `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`: Train IC=+0.2566, Lock IC=+0.0857, Lock Sharpe=+0.8706

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

_Null Baseline (un-gated candidate pool): 79.0% lock IC > 0, 65.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.3339_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1022 | 30 | 90.0% | 76.7% | +0.0848 | +0.4544 |
| B2 Rolling Guard | 216 | 30 | 100.0% | 100.0% | +0.1085 | +0.6533 |
| BH-FDR Gate | 4 | 4 | 100.0% | 50.0% | +0.0684 | -0.0107 |
| B3 Composite Floor | 77 | 30 | 100.0% | 100.0% | +0.0896 | +0.5686 |
| B4 Correlation Gate | 317 | 30 | 100.0% | 100.0% | +0.1212 | +1.2987 |

**Admitted Pool Summary**: 17 features, False Positive Rate = 17.6% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0892, Mean Lock Sharpe = +0.5931

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Lock Sharpe=+1.4951
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1867, Lock IC=+0.1399, Lock Sharpe=+1.4951
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.1924, Lock IC=+0.1128, Lock Sharpe=+1.2866
- `combo_tri_min__max_up_ret__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.2045, Lock IC=+0.0681, Lock Sharpe=+1.1823
- `combo_rank_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2008, Lock IC=+0.1329, Lock Sharpe=+1.0349

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Lock Sharpe=+1.3322
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2011, Lock IC=+0.1394, Lock Sharpe=+1.3322
- `combo_mean__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.1752, Lock IC=+0.1020, Lock Sharpe=+1.3030
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.1826, Lock IC=+0.1317, Lock Sharpe=+1.2186
- `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`: Train IC=+0.1883, Lock IC=+0.1273, Lock Sharpe=+1.0683

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0763, Lock IC=+0.1143, Lock Sharpe=+0.2104
- `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector`: Train IC=+0.0869, Lock IC=+0.0809, Lock Sharpe=+0.1650

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__impulse_bar_dominance`: Train IC=+0.2037, Lock IC=+0.1093, Lock Sharpe=+1.1046
- `combo_mean__limit_down_proximity_early__volume_weighted_price_position`: Train IC=+0.1757, Lock IC=+0.1254, Lock Sharpe=+1.0792
- `combo_mean__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.1920, Lock IC=+0.0895, Lock Sharpe=+0.8978
- `combo_mean__opening_drive_thrust_ratio__bar_ret_0`: Train IC=+0.1920, Lock IC=+0.0905, Lock Sharpe=+0.8323
- `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.1927, Lock IC=+0.0859, Lock Sharpe=+0.7701

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2771, Lock IC=+0.1372, Lock Sharpe=+1.8229
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2736, Lock IC=+0.1362, Lock Sharpe=+1.8009
- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2717, Lock IC=+0.1211, Lock Sharpe=+1.8009
- `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2798, Lock IC=+0.1292, Lock Sharpe=+1.7062
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2883, Lock IC=+0.1316, Lock Sharpe=+1.5821

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
| 0.45 | 0.10 | 546 | +0.0249 | 80.0% |
| 0.45 | 0.20 | 539 | +0.0249 | 80.0% |
| 0.45 | 0.30 | 513 | +0.0249 | 80.0% |
| 0.45 | 0.40 | 423 | +0.0249 | 80.0% |
| 0.45 | 0.50 | 273 | +0.0249 | 80.0% |
| 0.50 | 0.15 | 540 | +0.0249 | 80.0% |
| 0.50 | 0.25 | 530 | +0.0249 | 80.0% |
| 0.50 | 0.35 | 482 | +0.0249 | 80.0% |
| 0.50 | 0.45 | 345 | +0.0249 | 80.0% |
| 0.55 | 0.10 | 540 | +0.0249 | 80.0% |
| 0.55 | 0.20 | 539 | +0.0249 | 80.0% |
| 0.55 | 0.30 | 513 | +0.0249 | 80.0% |
| 0.55 | 0.40 | 423 | +0.0249 | 80.0% |
| 0.55 | 0.50 | 273 | +0.0249 | 80.0% |
| 0.60 | 0.15 | 512 | +0.0249 | 80.0% |
| 0.60 | 0.25 | 511 | +0.0249 | 80.0% |
| 0.60 | 0.35 | 481 | +0.0249 | 80.0% |
| 0.60 | 0.45 | 345 | +0.0249 | 80.0% |
| 0.65 | 0.10 | 415 | +0.0249 | 80.0% |
| 0.65 | 0.20 | 415 | +0.0249 | 80.0% |
| 0.65 | 0.30 | 415 | +0.0249 | 80.0% |
| 0.65 | 0.40 | 397 | +0.0249 | 80.0% |
| 0.65 | 0.50 | 273 | +0.0249 | 80.0% |
| 0.70 | 0.15 | 211 | +0.0267 | 80.0% |
| 0.70 | 0.25 | 211 | +0.0267 | 80.0% |
| 0.70 | 0.35 | 211 | +0.0267 | 80.0% |
| 0.70 | 0.45 | 210 | +0.0267 | 80.0% |
| 0.75 | 0.10 | 54 | +0.0147 | 60.0% |
| 0.75 | 0.20 | 54 | +0.0147 | 60.0% |
| 0.75 | 0.30 | 54 | +0.0147 | 60.0% |
| 0.75 | 0.40 | 54 | +0.0147 | 60.0% |
| 0.75 | 0.50 | 54 | +0.0147 | 60.0% |
| 0.80 | 0.15 | 23 | +0.0083 | 50.0% |
| 0.80 | 0.25 | 23 | +0.0083 | 50.0% |
| 0.80 | 0.35 | 23 | +0.0083 | 50.0% |
| 0.80 | 0.45 | 23 | +0.0083 | 50.0% |

**Optimal**: mono_thr=0.70, ir_thr=0.10 → 211 candidates, mean lock IC=+0.0267, 80.0% positive

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
| 0.45 | 0.10 | 1305 | +0.1004 | 100.0% |
| 0.45 | 0.20 | 1282 | +0.1004 | 100.0% |
| 0.45 | 0.30 | 1185 | +0.1004 | 100.0% |
| 0.45 | 0.40 | 980 | +0.1004 | 100.0% |
| 0.45 | 0.50 | 738 | +0.1004 | 100.0% |
| 0.50 | 0.15 | 1298 | +0.1004 | 100.0% |
| 0.50 | 0.25 | 1235 | +0.1004 | 100.0% |
| 0.50 | 0.35 | 1096 | +0.1004 | 100.0% |
| 0.50 | 0.45 | 884 | +0.1004 | 100.0% |
| 0.55 | 0.10 | 1293 | +0.1004 | 100.0% |
| 0.55 | 0.20 | 1280 | +0.1004 | 100.0% |
| 0.55 | 0.30 | 1185 | +0.1004 | 100.0% |
| 0.55 | 0.40 | 980 | +0.1004 | 100.0% |
| 0.55 | 0.50 | 738 | +0.1004 | 100.0% |
| 0.60 | 0.15 | 1214 | +0.1004 | 100.0% |
| 0.60 | 0.25 | 1198 | +0.1004 | 100.0% |
| 0.60 | 0.35 | 1094 | +0.1004 | 100.0% |
| 0.60 | 0.45 | 884 | +0.1004 | 100.0% |
| 0.65 | 0.10 | 969 | +0.1004 | 100.0% |
| 0.65 | 0.20 | 969 | +0.1004 | 100.0% |
| 0.65 | 0.30 | 969 | +0.1004 | 100.0% |
| 0.65 | 0.40 | 927 | +0.1004 | 100.0% |
| 0.65 | 0.50 | 733 | +0.1004 | 100.0% |
| 0.70 | 0.15 | 615 | +0.1004 | 100.0% |
| 0.70 | 0.25 | 615 | +0.1004 | 100.0% |
| 0.70 | 0.35 | 615 | +0.1004 | 100.0% |
| 0.70 | 0.45 | 615 | +0.1004 | 100.0% |
| 0.75 | 0.10 | 277 | +0.0998 | 100.0% |
| 0.75 | 0.20 | 277 | +0.0998 | 100.0% |
| 0.75 | 0.30 | 277 | +0.0998 | 100.0% |
| 0.75 | 0.40 | 277 | +0.0998 | 100.0% |
| 0.75 | 0.50 | 277 | +0.0998 | 100.0% |
| 0.80 | 0.15 | 104 | +0.1004 | 100.0% |
| 0.80 | 0.25 | 104 | +0.1004 | 100.0% |
| 0.80 | 0.35 | 104 | +0.1004 | 100.0% |
| 0.80 | 0.45 | 104 | +0.1004 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 104 candidates, mean lock IC=+0.1004, 100.0% positive

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
| 0.45 | 0.10 | 657 | +0.1195 | 100.0% |
| 0.45 | 0.20 | 635 | +0.1195 | 100.0% |
| 0.45 | 0.30 | 579 | +0.1195 | 100.0% |
| 0.45 | 0.40 | 439 | +0.1195 | 100.0% |
| 0.45 | 0.50 | 296 | +0.1195 | 100.0% |
| 0.50 | 0.15 | 649 | +0.1195 | 100.0% |
| 0.50 | 0.25 | 608 | +0.1195 | 100.0% |
| 0.50 | 0.35 | 527 | +0.1195 | 100.0% |
| 0.50 | 0.45 | 371 | +0.1195 | 100.0% |
| 0.55 | 0.10 | 649 | +0.1195 | 100.0% |
| 0.55 | 0.20 | 634 | +0.1195 | 100.0% |
| 0.55 | 0.30 | 579 | +0.1195 | 100.0% |
| 0.55 | 0.40 | 439 | +0.1195 | 100.0% |
| 0.55 | 0.50 | 296 | +0.1195 | 100.0% |
| 0.60 | 0.15 | 601 | +0.1195 | 100.0% |
| 0.60 | 0.25 | 598 | +0.1195 | 100.0% |
| 0.60 | 0.35 | 527 | +0.1195 | 100.0% |
| 0.60 | 0.45 | 371 | +0.1195 | 100.0% |
| 0.65 | 0.10 | 465 | +0.1195 | 100.0% |
| 0.65 | 0.20 | 465 | +0.1195 | 100.0% |
| 0.65 | 0.30 | 465 | +0.1195 | 100.0% |
| 0.65 | 0.40 | 413 | +0.1195 | 100.0% |
| 0.65 | 0.50 | 295 | +0.1195 | 100.0% |
| 0.70 | 0.15 | 244 | +0.1195 | 100.0% |
| 0.70 | 0.25 | 244 | +0.1195 | 100.0% |
| 0.70 | 0.35 | 244 | +0.1195 | 100.0% |
| 0.70 | 0.45 | 239 | +0.1195 | 100.0% |
| 0.75 | 0.10 | 79 | +0.1195 | 100.0% |
| 0.75 | 0.20 | 79 | +0.1195 | 100.0% |
| 0.75 | 0.30 | 79 | +0.1195 | 100.0% |
| 0.75 | 0.40 | 79 | +0.1195 | 100.0% |
| 0.75 | 0.50 | 79 | +0.1195 | 100.0% |
| 0.80 | 0.15 | 13 | +0.0373 | 40.0% |
| 0.80 | 0.25 | 13 | +0.0373 | 40.0% |
| 0.80 | 0.35 | 13 | +0.0373 | 40.0% |
| 0.80 | 0.45 | 13 | +0.0373 | 40.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 657 candidates, mean lock IC=+0.1195, 100.0% positive

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
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1266 | +0.0000 | +0.0354 | 0.28x | 2016-08-24 |
| `combo_rank_min__volume_weighted_price_position__bar_body_rng_0` | +0.1129 | +0.0000 | +0.0153 | 0.14x | 2015-02-06 |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | +0.1149 | +0.0000 | -0.0134 | -0.12x | 2017-07-10 |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | +0.1037 | +0.0000 | -0.0023 | -0.02x | 2015-02-06 |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | +0.0971 | +0.0000 | +0.0638 | 0.66x | 2013-08-21 |
| `combo_min__max_up_ret__opening_drive_thrust_ratio` | +0.1146 | +0.0000 | -0.0067 | -0.06x | 2017-04-07 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1310 | +0.0000 | +0.0352 | 0.27x | 2016-08-24 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0348 | +0.0000 | -0.0158 | -0.45x | 2010-10-15 |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | +0.0312 | +0.0000 | -0.0099 | -0.32x | 2012-07-05 |
| `combo_ratio__first_bar_return__volume_surge_direction` | +0.0836 | +0.0000 | +0.0050 | 0.06x | 2010-10-15 |
| `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +0.0743 | +0.0000 | +0.0288 | 0.39x | 2017-10-12 |
| `combo_tri_mean__smooth_momentum_structure__first_bar_return__bar_body_rng_0` | +0.0358 | +0.0000 | +0.0203 | 0.57x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1881 | +0.0000 | +0.0955 | 0.51x | 2021-07-28 |
| `combo_rank_max__early_body_momentum__bar_ret_0` | +0.1669 | +0.0000 | +0.0590 | 0.35x | 2020-01-06 |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | +0.1382 | +0.0000 | +0.0742 | 0.54x | 2013-09-23 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1931 | +0.0000 | +0.1193 | 0.62x | No decay |
| `combo_rel_diff__max_up_ret__body_size_progression` | +0.1673 | +0.0000 | +0.0747 | 0.45x | 2019-12-05 |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1897 | +0.0000 | +0.0874 | 0.46x | 2025-07-24 |
| `combo_max__bar_ret_0__max_down_ret` | +0.1604 | +0.0000 | +0.0818 | 0.51x | 2016-11-30 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1420 | +0.0000 | +0.1566 | 1.10x | 2016-09-26 |
| `vwap_trend_channel_slope` | +0.1469 | +0.0000 | +0.0712 | 0.48x | 2016-11-01 |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | +0.1391 | +0.0000 | +0.1148 | 0.82x | 2016-08-24 |
| `combo_diff__bar_ret_0__max_down_ret` | +0.0372 | +0.0000 | +0.0120 | 0.32x | 2010-10-15 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1618 | +0.0000 | +0.1235 | 0.76x | 2017-01-20 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1165 | +0.0000 | +0.0911 | 0.78x | 2011-10-18 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1511 | +0.0000 | +0.1279 | 0.85x | 2017-01-20 |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | +0.1640 | +0.0000 | +0.0760 | 0.46x | 2017-02-27 |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | +0.1642 | +0.0000 | +0.1327 | 0.81x | 2017-01-20 |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__impulse_bar_dominance` | +0.1458 | +0.0000 | +0.0904 | 0.62x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | +0.1398 | +0.0000 | +0.1203 | 0.86x | 2016-09-14 |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1238 | +0.0000 | +0.1088 | 0.88x | 2017-02-27 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1192 | +0.0000 | +0.0677 | 0.57x | 2016-10-24 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | +0.0708 | +0.0000 | +0.0259 | 0.37x | 2011-04-13 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0645 | +0.0000 | -0.0273 | -0.42x | 2012-01-17 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2260). Consider relaxing this gate.
2. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 13.0%, mean lock Sharpe=-0.3172). Consider relaxing this gate.
3. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 29.0%, mean lock Sharpe=+0.2210). Consider relaxing this gate.
4. **50ETF `long` — 7-Year Jackknife Sign Stability too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 7.0%, mean lock Sharpe=-0.7170). Consider relaxing this gate.
5. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.1384). Consider relaxing this gate.
6. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.6891). Consider relaxing this gate.
7. **500ETF `single` — B2 Rolling Guard too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.4624). Consider relaxing this gate.
8. **500ETF `single` — B3 Composite Floor too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.2102). Consider relaxing this gate.
9. **500ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 50.0%, mean lock Sharpe=+0.6330). Consider relaxing this gate.
10. **500ETF `short` — BH-FDR Gate too strict**: 75.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.1756). Consider relaxing this gate.
11. **159915ETF `single` — B2 Rolling Guard too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 65.0%, mean lock Sharpe=+0.6533). Consider relaxing this gate.
12. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 65.0%, mean lock Sharpe=+0.5686). Consider relaxing this gate.
13. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 65.0%, mean lock Sharpe=+1.2987). Consider relaxing this gate.
14. **159915ETF `long` — B2 Rolling Guard too strict**: 86.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6794). Consider relaxing this gate.
15. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6624). Consider relaxing this gate.
16. **159915ETF `long` — B3 Composite Floor too strict**: 90.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 53.0%, mean lock Sharpe=+0.6774). Consider relaxing this gate.
17. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.1996). Consider relaxing this gate.
18. **159915ETF `short` — B2 Rolling Guard too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=+0.0101). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
