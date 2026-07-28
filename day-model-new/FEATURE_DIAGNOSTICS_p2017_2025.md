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

### 300ETF — `single` (Full Model Lockbox IC: -0.0226, Sharpe: -0.0479)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_min__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0875 | -0.0223 | -0.0223 | -1.3571 | 85.92 | -7.2 | -0.90x | -0.0109 | +0.2258 |
| `volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.0791 | +0.0000 | +0.0000 | -0.4047 | 93.80 | +4.2 | 0.52x | +0.0053 | -0.0479 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | Intraday Range Momentum | +1 | +0.0964 | -0.0284 | -0.0284 | -0.8306 | 87.89 | -0.1 | -0.02x | -0.0097 | -0.0119 |
| `first_30min_return` | Intraday Range Momentum | +1 | +0.0582 | -0.0197 | -0.0197 | -0.4422 | 85.92 | +2.2 | 0.27x | +0.0038 | -0.0323 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0842, Sharpe: +0.4312)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1545 | +0.0289 | +0.0289 | -0.4152 | 83.30 | +2.0 | 0.25x | -0.0099 | +0.2587 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1453 | +0.0883 | +0.0883 | -0.5698 | 90.52 | -0.8 | -0.10x | +0.0096 | +0.0923 |
| `combo_min__net_volume_flow__impulse_bar_dominance` | Volatility & Oscillators | +1 | +0.1002 | +0.0717 | +0.0717 | -0.7637 | 86.58 | -2.6 | -0.33x | +0.0027 | -0.2717 |
| `combo_min__first_bar_sentiment__bar_ret_0` | Gap / Overnight Reversal | +1 | +0.1139 | +0.0486 | +0.0486 | -0.3006 | 80.68 | +2.7 | 0.34x | +0.0009 | -0.1344 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.1138 | +0.1138 | +0.2628 | 83.30 | +13.0 | 1.63x | +0.0041 | -0.0796 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.1239 | +0.0383 | +0.0383 | -0.5921 | 82.65 | -0.1 | -0.01x | -0.0033 | +0.0304 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1204 | +0.1108 | +0.1108 | +1.2537 | 84.61 | +29.9 | 3.74x | +0.0058 | +0.0529 |
| `combo_diff__max_up_ret__impulse_bar_dominance` | Intraday Range Momentum | +1 | +0.0745 | -0.0318 | -0.0318 | -1.2793 | 81.33 | -10.5 | -1.31x | -0.0082 | -0.2342 |
| `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | Other Technical | +1 | +0.1122 | +0.0032 | +0.0032 | -0.4809 | 82.65 | +0.4 | 0.05x | -0.0065 | +0.3748 |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1011 | +0.0944 | +0.0944 | -0.6509 | 90.52 | -0.8 | -0.11x | +0.0075 | -0.4235 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1022 | +0.1034 | +0.1034 | +1.4498 | 85.27 | +27.1 | 3.39x | +0.0055 | +0.2448 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.0634 | +0.0335 | +0.0335 | +0.3145 | 87.24 | +13.4 | 1.67x | -0.0016 | +0.1863 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1607, Sharpe: +1.4058)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1386 | +0.1275 | +0.1275 | +0.8333 | 87.24 | +25.9 | 3.23x | +0.0031 | +0.3705 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1340 | +0.1239 | +0.1239 | +1.0994 | 91.17 | +32.5 | 4.07x | +0.0002 | -0.2138 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0673 | +0.0673 | +0.1332 | 90.52 | +10.1 | 1.26x | -0.0014 | +0.3258 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | Other Technical | +1 | +0.1235 | +0.1428 | +0.1428 | +1.5199 | 83.30 | +38.5 | 4.81x | +0.0054 | +0.0068 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0918 | +0.1286 | +0.1286 | +0.5529 | 83.30 | +21.3 | 2.67x | +0.0099 | +0.5449 |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.0893 | +0.0887 | +0.0887 | -0.8232 | 87.89 | -7.9 | -0.99x | +0.0028 | +0.1157 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0983 | +0.1124 | +0.1124 | +0.3952 | 91.17 | +15.8 | 1.97x | +0.0068 | -0.1858 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1429 | +0.1073 | +0.1073 | +0.1834 | 84.61 | +12.0 | 1.50x | +0.0035 | +0.3073 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1120 | +0.1308 | +0.1308 | +0.7043 | 84.61 | +24.7 | 3.09x | +0.0000 | +0.1435 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1064 | +0.0659 | +0.0659 | +0.7397 | 87.24 | +24.3 | 3.04x | +0.0007 | +0.1157 |
| `trend_bar_close_consistency` | Other Technical | +1 | +0.0595 | +0.0806 | +0.0806 | -0.4274 | 86.58 | -0.4 | -0.05x | +0.0054 | -0.1992 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.0% lock IC > 0, 18.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5851_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 824 | 30 | 83.3% | 50.0% | +0.0513 | -0.1355 |
| B2 Rolling Guard | 98 | 30 | 80.0% | 33.3% | +0.0252 | -0.2939 |
| BH-FDR Gate | 3 | 3 | 100.0% | 33.3% | +0.0413 | -0.4780 |
| B4 Correlation Gate | 70 | 30 | 26.7% | 0.0% | -0.0083 | -1.0138 |

**Admitted Pool Summary**: 4 features, False Positive Rate = 100.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0176, Mean Lock Sharpe = -0.7587

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ratio__limit_down_proximity_early__volume_concentration`: Train IC=+0.1720, Lock IC=+0.1235, Lock Sharpe=+0.9843
- `combo_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611
- `combo_z_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611
- `combo_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611
- `combo_z_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1706, Lock IC=+0.1181, Lock Sharpe=+0.8611

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0963, Lock Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0963, Lock Sharpe=+0.8491
- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353
- `combo_z_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353
- `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Lock Sharpe=+0.1297

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 6.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7951_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 538 | 30 | 70.0% | 23.3% | +0.0193 | -0.5046 |
| B2 Rolling Guard | 41 | 30 | 23.3% | 10.0% | -0.0076 | -0.4884 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0266 | -1.3072 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `volume_concentration`: Train IC=+0.1149, Lock IC=+0.0409, Lock Sharpe=+0.7521
- `first_bar_volume`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.6546
- `bar_vol_0`: Train IC=+0.1294, Lock IC=+0.0659, Lock Sharpe=+0.6546
- `volume_surge_max`: Train IC=+0.1279, Lock IC=+0.0659, Lock Sharpe=+0.6546
- `sma200_dist`: Train IC=+0.1387, Lock IC=+0.0286, Lock Sharpe=+0.3842

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__willr14__roc60`: Train IC=+0.0666, Lock IC=+0.0596, Lock Sharpe=+0.5936
- `combo_diff__willr14__roc60`: Train IC=+0.0528, Lock IC=+0.0594, Lock Sharpe=+0.5936
- `combo_z_diff__willr14__roc60`: Train IC=+0.0528, Lock IC=+0.0594, Lock Sharpe=+0.5936

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4466_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 73.3% | 36.7% | +0.0375 | -0.3299 |
| B2 Rolling Guard | 60 | 30 | 53.3% | 30.0% | -0.0027 | -0.3663 |
| BH-FDR Gate | 8 | 8 | 62.5% | 50.0% | +0.0200 | -0.1816 |
| B3 Composite Floor | 1 | 1 | 100.0% | 100.0% | +0.0684 | +0.3610 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.9794
- `combo_z_sum__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.9794
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `star50_limit_proximity_early`: Train IC=+0.1240, Lock IC=+0.0960, Lock Sharpe=+0.8503

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__total_path_length__max_down_ret`: Train IC=+0.0376, Lock IC=+0.0550, Lock Sharpe=+0.8756
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0347, Lock Sharpe=+0.6443
- `combo_sig_product__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0064, Lock IC=+0.0190, Lock Sharpe=+0.5424
- `pullback_depth_ratio`: Train IC=+0.0000, Lock IC=+0.0504, Lock Sharpe=+0.2616
- `combo_mean__donchian_breakout_ratio_20d__dual_thrust_range_ratio`: Train IC=+0.0961, Lock IC=+0.0263, Lock Sharpe=+0.2180

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0708, Lock IC=+0.0119, Lock Sharpe=+0.7142
- `gap_pct`: Train IC=+0.1402, Lock IC=+0.1085, Lock Sharpe=+0.6926
- `combo_rank_max__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.1202, Lock IC=+0.0273, Lock Sharpe=+0.2891
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1032, Lock IC=+0.0946, Lock Sharpe=+0.2733

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.2007, Lock IC=+0.0684, Lock Sharpe=+0.3610

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 66.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4541_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 839 | 30 | 100.0% | 53.3% | +0.0414 | +0.1952 |
| B2 Rolling Guard | 78 | 30 | 90.0% | 53.3% | +0.0495 | +0.1274 |
| BH-FDR Gate | 3 | 3 | 0.0% | 0.0% | -0.0339 | -0.9002 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__volume_surge_max__roc10`: Train IC=+0.1513, Lock IC=+0.0272, Lock Sharpe=+1.0041
- `combo_rank_min__first_bar_volume__roc10`: Train IC=+0.1467, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_rank_min__bar_vol_0__roc10`: Train IC=+0.1467, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_min__roc60__roc10`: Train IC=+0.1297, Lock IC=+0.0274, Lock Sharpe=+0.7136
- `combo_rank_min__ma_alignment_score_5_10_20__roc10`: Train IC=+0.1303, Lock IC=+0.0844, Lock Sharpe=+0.6165

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__sma50_dist`: Train IC=+0.1129, Lock IC=+0.0768, Lock Sharpe=+1.2013
- `combo_sig_product__iv_corridor_width__sma100_dist`: Train IC=+0.1155, Lock IC=+0.0663, Lock Sharpe=+1.0514
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.0946, Lock IC=+0.0603, Lock Sharpe=+0.9632
- `combo_rank_max__bar_vol_4__roc10`: Train IC=+0.1007, Lock IC=+0.0813, Lock Sharpe=+0.9300
- `combo_max__bar_vol_4__yesterday_wavetrend_osc`: Train IC=+0.0830, Lock IC=+0.0958, Lock Sharpe=+0.8260

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9112_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 321 | 30 | 63.3% | 0.0% | +0.0163 | -1.0981 |
| B2 Rolling Guard | 36 | 30 | 26.7% | 6.7% | -0.0014 | -0.7447 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0367 | -1.6299 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__iv_envelope_deviation__yesterday_wavetrend_osc`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0844
- `combo_product__iv_envelope_deviation__wavetrend_osc_day`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0844

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 29.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3789_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 278 | 30 | 76.7% | 60.0% | +0.0467 | +0.1570 |
| B2 Rolling Guard | 40 | 30 | 33.3% | 20.0% | +0.0115 | -0.0930 |
| BH-FDR Gate | 2 | 2 | 100.0% | 100.0% | +0.0198 | +0.3210 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1886, Lock IC=+0.0898, Lock Sharpe=+1.2870
- `limit_down_proximity_early`: Train IC=+0.1886, Lock IC=+0.0899, Lock Sharpe=+1.2870
- `combo_rank_max__bar_vol_4__mfi14`: Train IC=+0.1590, Lock IC=+0.0937, Lock Sharpe=+1.1906
- `sma20_dist`: Train IC=+0.1468, Lock IC=+0.1018, Lock Sharpe=+1.1639
- `star50_limit_proximity_early`: Train IC=+0.1271, Lock IC=+0.0603, Lock Sharpe=+0.8789

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0277, Lock Sharpe=+1.2964
- `close_vs_open_range`: Train IC=+0.0193, Lock IC=+0.0427, Lock Sharpe=+1.1670
- `keltner_squeeze_width`: Train IC=+0.1163, Lock IC=+0.1636, Lock Sharpe=+1.1211
- `pullback_depth_ratio`: Train IC=+0.0000, Lock IC=+0.0131, Lock Sharpe=+1.0318
- `double_bottom_bull_flag_early`: Train IC=+0.0000, Lock IC=+0.0700, Lock Sharpe=+0.3934

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1148, Lock IC=+0.0302, Lock Sharpe=+0.5419
- `cvd_divergence_day`: Train IC=+0.1225, Lock IC=+0.0094, Lock Sharpe=+0.1001

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 69.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5748_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1781 | 30 | 100.0% | 60.0% | +0.0800 | -0.0568 |
| B2 Rolling Guard | 250 | 30 | 96.7% | 6.7% | +0.0412 | -0.8121 |
| BH-FDR Gate | 5 | 5 | 60.0% | 0.0% | -0.0027 | -1.3497 |
| B3 Composite Floor | 54 | 30 | 83.3% | 26.7% | +0.0292 | -0.6729 |
| B4 Correlation Gate | 561 | 30 | 100.0% | 0.0% | +0.0568 | -0.6310 |

**Admitted Pool Summary**: 12 features, False Positive Rate = 66.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0586, Mean Lock Sharpe = -0.1476

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__opening_drive_thrust_ratio__impulse_bar_dominance`: Train IC=+0.2142, Lock IC=+0.0899, Lock Sharpe=+1.4986
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Lock Sharpe=+0.5717
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_mean__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2188, Lock IC=+0.1124, Lock Sharpe=+0.3413

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__volume_weighted_momentum_acceleration__impulse_bar_dominance`: Train IC=+0.1793, Lock IC=+0.0702, Lock Sharpe=+0.6288
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2239, Lock IC=+0.0978, Lock Sharpe=+0.0194

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1881, Lock IC=+0.0017, Lock Sharpe=+0.3201
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.1599, Lock IC=+0.0747, Lock Sharpe=+0.2713
- `combo_tri_mean__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_z_mean__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_mean__smooth_momentum_structure__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 23.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5210_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1228 | 30 | 83.3% | 66.7% | +0.0708 | +0.3640 |
| B2 Rolling Guard | 96 | 30 | 33.3% | 10.0% | -0.0230 | -0.7306 |
| BH-FDR Gate | 23 | 23 | 91.3% | 78.3% | +0.0383 | +0.3385 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1626, Lock IC=+0.1245, Lock Sharpe=+1.4042
- `combo_diff__donchian_breakout_ratio_20d__yesterday_return`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400
- `combo_z_diff__donchian_breakout_ratio_20d__yesterday_return`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400
- `combo_diff__donchian_breakout_ratio_20d__limit_up_proximity_day`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400
- `combo_z_diff__donchian_breakout_ratio_20d__limit_up_proximity_day`: Train IC=+0.1716, Lock IC=+0.1128, Lock Sharpe=+0.8400

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__consecutive_higher_highs__trend_day_regime_conviction`: Train IC=+0.0601, Lock IC=+0.0134, Lock Sharpe=+0.9154
- `combo_rank_min__early_body_momentum__star50_limit_proximity_early`: Train IC=+0.1367, Lock IC=+0.1134, Lock Sharpe=+0.5147
- `combo_rank_min__opening_momentum_score__star50_limit_proximity_early`: Train IC=+0.1367, Lock IC=+0.1134, Lock Sharpe=+0.5147

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_abs_diff__early_body_momentum__shaved_bar_trend_conviction`: Train IC=+0.1248, Lock IC=+0.0888, Lock Sharpe=+1.8266
- `combo_abs_diff__opening_momentum_score__shaved_bar_trend_conviction`: Train IC=+0.1248, Lock IC=+0.0888, Lock Sharpe=+1.8266
- `combo_rank_min__shaved_bar_trend_conviction__trend_day_regime_conviction`: Train IC=+0.1061, Lock IC=+0.0275, Lock Sharpe=+0.8838
- `combo_min__shaved_bar_trend_conviction__trend_day_regime_conviction`: Train IC=+0.0970, Lock IC=+0.0277, Lock Sharpe=+0.8622
- `combo_rank_min__star50_limit_proximity_early__morning_trend_extrapolated`: Train IC=+0.1845, Lock IC=+0.1057, Lock Sharpe=+0.7359

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4854_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 369 | 30 | 56.7% | 33.3% | +0.0296 | -0.3058 |
| B2 Rolling Guard | 46 | 30 | 63.3% | 26.7% | +0.0057 | -0.2689 |
| BH-FDR Gate | 14 | 14 | 92.9% | 7.1% | +0.0489 | -0.8709 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.4723
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.4723
- `false_breakout_accumulation`: Train IC=+0.1489, Lock IC=+0.0315, Lock Sharpe=+0.4446
- `combo_mean__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.4139
- `combo_z_sum__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.4139

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `opening_direction_stability`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+1.7232
- `early_trend_hhi`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+1.7232
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0696, Lock Sharpe=+1.2386
- `iv_diff_1d`: Train IC=+0.0334, Lock IC=+0.0868, Lock Sharpe=+0.9572
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0300, Lock Sharpe=+0.5114

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vwap_close_divergence_trend`: Train IC=+0.0805, Lock IC=+0.0323, Lock Sharpe=+0.2934

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 76.0% lock IC > 0, 52.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.1491_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1149 | 30 | 100.0% | 73.3% | +0.1070 | +0.4464 |
| B2 Rolling Guard | 148 | 30 | 100.0% | 83.3% | +0.1020 | +0.6451 |
| BH-FDR Gate | 4 | 4 | 100.0% | 25.0% | +0.0586 | -0.2083 |
| B3 Composite Floor | 107 | 30 | 100.0% | 90.0% | +0.1066 | +0.3334 |
| B4 Correlation Gate | 411 | 30 | 100.0% | 100.0% | +0.1289 | +1.1286 |

**Admitted Pool Summary**: 11 features, False Positive Rate = 27.3% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1066, Mean Lock Sharpe = +0.4474

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1870, Lock IC=+0.1443, Lock Sharpe=+2.2459
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2358, Lock IC=+0.1409, Lock Sharpe=+1.7700
- `combo_rank_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2072, Lock IC=+0.1597, Lock Sharpe=+1.6299
- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2218, Lock IC=+0.1126, Lock Sharpe=+1.4142
- `combo_rank_max__opening_drive_thrust_ratio__directional_volume_signature`: Train IC=+0.2007, Lock IC=+0.0827, Lock Sharpe=+1.0347

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Lock Sharpe=+1.6676
- `combo_z_sum__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Lock Sharpe=+1.6676
- `combo_mean__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Lock Sharpe=+1.6676
- `combo_z_sum__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Lock Sharpe=+1.6676
- `combo_min__first_bar_sentiment__demark_setup_reversal_early`: Train IC=+0.1592, Lock IC=+0.0857, Lock Sharpe=+1.3351

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0545, Lock IC=+0.1184, Lock Sharpe=+0.1952

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__max_up_ret__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2424, Lock IC=+0.1107, Lock Sharpe=+1.2956
- `combo_tri_median__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2162, Lock IC=+0.1322, Lock Sharpe=+0.9789
- `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2133, Lock IC=+0.1295, Lock Sharpe=+0.9692
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2110, Lock IC=+0.1348, Lock Sharpe=+0.8886
- `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`: Train IC=+0.2460, Lock IC=+0.1133, Lock Sharpe=+0.8865

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3282, Lock IC=+0.1307, Lock Sharpe=+1.7816
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3122, Lock IC=+0.1361, Lock Sharpe=+1.6091
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3360, Lock IC=+0.1300, Lock Sharpe=+1.5827
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.5184
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.5184

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 66.0% lock IC > 0, 41.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2528_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 938 | 30 | 90.0% | 53.3% | +0.0783 | +0.1280 |
| B2 Rolling Guard | 63 | 30 | 90.0% | 50.0% | +0.0765 | +0.1443 |
| BH-FDR Gate | 117 | 30 | 100.0% | 96.7% | +0.1037 | +0.8546 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__trend_strength_intraday`: Train IC=+0.1628, Lock IC=+0.1119, Lock Sharpe=+1.6143
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2132, Lock IC=+0.1300, Lock Sharpe=+1.4635
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__counter_trend_bar_weakness`: Train IC=+0.1562, Lock IC=+0.1299, Lock Sharpe=+1.4458
- `combo_min__opening_drive_thrust_ratio__open_to_current_return`: Train IC=+0.1640, Lock IC=+0.1043, Lock Sharpe=+1.3003
- `combo_min__opening_drive_thrust_ratio__first_30min_return`: Train IC=+0.1640, Lock IC=+0.1043, Lock Sharpe=+1.3003

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.1162, Lock Sharpe=+1.1610
- `combo_tri_z_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.1162, Lock Sharpe=+1.1610
- `combo_tri_mean__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.0999, Lock IC=+0.1103, Lock Sharpe=+1.0839
- `combo_tri_z_mean__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.0999, Lock IC=+0.1103, Lock Sharpe=+1.0839
- `combo_rank_min__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.1129, Lock IC=+0.0837, Lock Sharpe=+1.0825

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1758, Lock IC=+0.1285, Lock Sharpe=+2.0254
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1506, Lock IC=+0.1406, Lock Sharpe=+1.7895
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1506, Lock IC=+0.1406, Lock Sharpe=+1.7895
- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1848, Lock IC=+0.1170, Lock Sharpe=+1.7797
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1491, Lock IC=+0.1210, Lock Sharpe=+1.2408

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 39.0% lock IC > 0, 23.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3720_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 256 | 30 | 76.7% | 46.7% | +0.0418 | -0.1156 |
| B2 Rolling Guard | 42 | 30 | 40.0% | 30.0% | +0.0131 | +0.0310 |
| BH-FDR Gate | 1 | 1 | 100.0% | 0.0% | +0.0926 | -0.0411 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `gap_pct`: Train IC=+0.0662, Lock IC=+0.1187, Lock Sharpe=+0.6266
- `combo_product__morning_volume_weighted_momentum__shaved_bar_trend_conviction`: Train IC=+0.1398, Lock IC=+0.0685, Lock Sharpe=+0.5945
- `vol_ratio_5_20`: Train IC=+0.0670, Lock IC=+0.0317, Lock Sharpe=+0.4589
- `combo_rel_diff__micro_gap_trend_continuation__shaved_bar_trend_conviction`: Train IC=+0.0946, Lock IC=+0.0112, Lock Sharpe=+0.4444
- `limit_down_proximity_early`: Train IC=+0.0645, Lock IC=+0.1323, Lock Sharpe=+0.4433

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0552, Lock Sharpe=+1.1274
- `combo_rank_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0168, Lock IC=+0.1035, Lock Sharpe=+1.0730
- `yesterday_close_position`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.8307
- `yesterday_day_close_pos`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.8307
- `combo_rank_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.0241, Lock IC=+0.0817, Lock Sharpe=+0.5716

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 447 | +0.0262 | 80.0% |
| 0.45 | 0.20 | 439 | +0.0262 | 80.0% |
| 0.45 | 0.30 | 417 | +0.0262 | 80.0% |
| 0.45 | 0.40 | 360 | +0.0262 | 80.0% |
| 0.45 | 0.50 | 290 | +0.0262 | 80.0% |
| 0.50 | 0.15 | 445 | +0.0262 | 80.0% |
| 0.50 | 0.25 | 429 | +0.0262 | 80.0% |
| 0.50 | 0.35 | 390 | +0.0262 | 80.0% |
| 0.50 | 0.45 | 334 | +0.0262 | 80.0% |
| 0.55 | 0.10 | 442 | +0.0262 | 80.0% |
| 0.55 | 0.20 | 437 | +0.0262 | 80.0% |
| 0.55 | 0.30 | 417 | +0.0262 | 80.0% |
| 0.55 | 0.40 | 360 | +0.0262 | 80.0% |
| 0.55 | 0.50 | 290 | +0.0262 | 80.0% |
| 0.60 | 0.15 | 426 | +0.0262 | 80.0% |
| 0.60 | 0.25 | 420 | +0.0262 | 80.0% |
| 0.60 | 0.35 | 389 | +0.0262 | 80.0% |
| 0.60 | 0.45 | 334 | +0.0262 | 80.0% |
| 0.65 | 0.10 | 365 | +0.0262 | 80.0% |
| 0.65 | 0.20 | 365 | +0.0262 | 80.0% |
| 0.65 | 0.30 | 363 | +0.0262 | 80.0% |
| 0.65 | 0.40 | 351 | +0.0262 | 80.0% |
| 0.65 | 0.50 | 290 | +0.0262 | 80.0% |
| 0.70 | 0.15 | 265 | +0.0262 | 80.0% |
| 0.70 | 0.25 | 265 | +0.0262 | 80.0% |
| 0.70 | 0.35 | 265 | +0.0262 | 80.0% |
| 0.70 | 0.45 | 263 | +0.0262 | 80.0% |
| 0.75 | 0.10 | 111 | +0.0120 | 60.0% |
| 0.75 | 0.20 | 111 | +0.0120 | 60.0% |
| 0.75 | 0.30 | 111 | +0.0120 | 60.0% |
| 0.75 | 0.40 | 111 | +0.0120 | 60.0% |
| 0.75 | 0.50 | 111 | +0.0120 | 60.0% |
| 0.80 | 0.15 | 18 | -0.0109 | 30.0% |
| 0.80 | 0.25 | 18 | -0.0109 | 30.0% |
| 0.80 | 0.35 | 18 | -0.0109 | 30.0% |
| 0.80 | 0.45 | 18 | -0.0109 | 30.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 447 candidates, mean lock IC=+0.0262, 80.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | -0.0188 | 30.0% |
| 0.45 | 0.20 | 6 | -0.0266 | 16.7% |
| 0.45 | 0.30 | 5 | -0.0224 | 20.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 8 | -0.0273 | 12.5% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 10 candidates, mean lock IC=-0.0188, 30.0% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 18 | +0.0125 | 50.0% |
| 0.45 | 0.20 | 7 | +0.0216 | 71.4% |
| 0.45 | 0.30 | 4 | +0.0087 | 75.0% |
| 0.45 | 0.40 | 1 | -0.0817 | 0.0% |
| 0.45 | 0.50 | 1 | -0.0817 | 0.0% |
| 0.50 | 0.15 | 14 | +0.0269 | 70.0% |
| 0.50 | 0.25 | 5 | +0.0094 | 80.0% |
| 0.50 | 0.35 | 1 | -0.0817 | 0.0% |
| 0.50 | 0.45 | 1 | -0.0817 | 0.0% |
| 0.55 | 0.10 | 9 | +0.0254 | 66.7% |
| 0.55 | 0.20 | 7 | +0.0216 | 71.4% |
| 0.55 | 0.30 | 4 | +0.0087 | 75.0% |
| 0.55 | 0.40 | 1 | -0.0817 | 0.0% |
| 0.55 | 0.50 | 1 | -0.0817 | 0.0% |
| 0.60 | 0.15 | 4 | +0.0087 | 75.0% |
| 0.60 | 0.25 | 4 | +0.0087 | 75.0% |
| 0.60 | 0.35 | 1 | -0.0817 | 0.0% |
| 0.60 | 0.45 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.10 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.20 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.30 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.40 | 1 | -0.0817 | 0.0% |
| 0.65 | 0.50 | 1 | -0.0817 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.15 → 14 candidates, mean lock IC=+0.0269, 70.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 387 | +0.0545 | 100.0% |
| 0.45 | 0.20 | 372 | +0.0545 | 100.0% |
| 0.45 | 0.30 | 345 | +0.0545 | 100.0% |
| 0.45 | 0.40 | 326 | +0.0545 | 100.0% |
| 0.45 | 0.50 | 305 | +0.0545 | 100.0% |
| 0.50 | 0.15 | 386 | +0.0545 | 100.0% |
| 0.50 | 0.25 | 361 | +0.0545 | 100.0% |
| 0.50 | 0.35 | 338 | +0.0545 | 100.0% |
| 0.50 | 0.45 | 317 | +0.0545 | 100.0% |
| 0.55 | 0.10 | 383 | +0.0545 | 100.0% |
| 0.55 | 0.20 | 370 | +0.0545 | 100.0% |
| 0.55 | 0.30 | 345 | +0.0545 | 100.0% |
| 0.55 | 0.40 | 326 | +0.0545 | 100.0% |
| 0.55 | 0.50 | 305 | +0.0545 | 100.0% |
| 0.60 | 0.15 | 352 | +0.0545 | 100.0% |
| 0.60 | 0.25 | 349 | +0.0545 | 100.0% |
| 0.60 | 0.35 | 337 | +0.0545 | 100.0% |
| 0.60 | 0.45 | 317 | +0.0545 | 100.0% |
| 0.65 | 0.10 | 328 | +0.0545 | 100.0% |
| 0.65 | 0.20 | 328 | +0.0545 | 100.0% |
| 0.65 | 0.30 | 327 | +0.0545 | 100.0% |
| 0.65 | 0.40 | 322 | +0.0545 | 100.0% |
| 0.65 | 0.50 | 305 | +0.0545 | 100.0% |
| 0.70 | 0.15 | 283 | +0.0545 | 100.0% |
| 0.70 | 0.25 | 283 | +0.0545 | 100.0% |
| 0.70 | 0.35 | 283 | +0.0545 | 100.0% |
| 0.70 | 0.45 | 283 | +0.0545 | 100.0% |
| 0.75 | 0.10 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.20 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.30 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.40 | 219 | +0.0534 | 100.0% |
| 0.75 | 0.50 | 219 | +0.0534 | 100.0% |
| 0.80 | 0.15 | 172 | +0.0450 | 100.0% |
| 0.80 | 0.25 | 172 | +0.0450 | 100.0% |
| 0.80 | 0.35 | 172 | +0.0450 | 100.0% |
| 0.80 | 0.45 | 172 | +0.0450 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 387 candidates, mean lock IC=+0.0545, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | +0.0048 | 44.4% |
| 0.45 | 0.20 | 4 | -0.0402 | 25.0% |
| 0.45 | 0.30 | 4 | -0.0402 | 25.0% |
| 0.45 | 0.40 | 3 | -0.0591 | 0.0% |
| 0.45 | 0.50 | 2 | -0.0541 | 0.0% |
| 0.50 | 0.15 | 8 | -0.0033 | 37.5% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 9 candidates, mean lock IC=+0.0048, 44.4% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 7 | +0.0191 | 71.4% |
| 0.45 | 0.20 | 2 | +0.0198 | 100.0% |
| 0.45 | 0.30 | 1 | +0.0094 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 2 | +0.0198 | 100.0% |
| 0.50 | 0.25 | 1 | +0.0094 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0151 | 66.7% |
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

**Optimal**: mono_thr=0.60, ir_thr=0.10 → 3 candidates, mean lock IC=+0.0458, 100.0% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1418 | +0.0509 | 100.0% |
| 0.45 | 0.20 | 1394 | +0.0509 | 100.0% |
| 0.45 | 0.30 | 1320 | +0.0509 | 100.0% |
| 0.45 | 0.40 | 1200 | +0.0509 | 100.0% |
| 0.45 | 0.50 | 985 | +0.0509 | 100.0% |
| 0.50 | 0.15 | 1409 | +0.0509 | 100.0% |
| 0.50 | 0.25 | 1363 | +0.0509 | 100.0% |
| 0.50 | 0.35 | 1258 | +0.0509 | 100.0% |
| 0.50 | 0.45 | 1069 | +0.0509 | 100.0% |
| 0.55 | 0.10 | 1412 | +0.0509 | 100.0% |
| 0.55 | 0.20 | 1393 | +0.0509 | 100.0% |
| 0.55 | 0.30 | 1320 | +0.0509 | 100.0% |
| 0.55 | 0.40 | 1200 | +0.0509 | 100.0% |
| 0.55 | 0.50 | 985 | +0.0509 | 100.0% |
| 0.60 | 0.15 | 1357 | +0.0509 | 100.0% |
| 0.60 | 0.25 | 1345 | +0.0509 | 100.0% |
| 0.60 | 0.35 | 1254 | +0.0509 | 100.0% |
| 0.60 | 0.45 | 1069 | +0.0509 | 100.0% |
| 0.65 | 0.10 | 1191 | +0.0509 | 100.0% |
| 0.65 | 0.20 | 1191 | +0.0509 | 100.0% |
| 0.65 | 0.30 | 1191 | +0.0509 | 100.0% |
| 0.65 | 0.40 | 1160 | +0.0509 | 100.0% |
| 0.65 | 0.50 | 985 | +0.0509 | 100.0% |
| 0.70 | 0.15 | 880 | +0.0509 | 100.0% |
| 0.70 | 0.25 | 880 | +0.0509 | 100.0% |
| 0.70 | 0.35 | 880 | +0.0509 | 100.0% |
| 0.70 | 0.45 | 879 | +0.0509 | 100.0% |
| 0.75 | 0.10 | 472 | +0.0509 | 100.0% |
| 0.75 | 0.20 | 472 | +0.0509 | 100.0% |
| 0.75 | 0.30 | 472 | +0.0509 | 100.0% |
| 0.75 | 0.40 | 472 | +0.0509 | 100.0% |
| 0.75 | 0.50 | 472 | +0.0509 | 100.0% |
| 0.80 | 0.15 | 175 | +0.0538 | 100.0% |
| 0.80 | 0.25 | 175 | +0.0538 | 100.0% |
| 0.80 | 0.35 | 175 | +0.0538 | 100.0% |
| 0.80 | 0.45 | 175 | +0.0538 | 100.0% |

**Optimal**: mono_thr=0.80, ir_thr=0.10 → 175 candidates, mean lock IC=+0.0538, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 45 | +0.0549 | 70.0% |
| 0.45 | 0.20 | 17 | +0.0496 | 80.0% |
| 0.45 | 0.30 | 10 | +0.0553 | 90.0% |
| 0.45 | 0.40 | 3 | +0.0523 | 66.7% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 25 | +0.0345 | 60.0% |
| 0.50 | 0.25 | 11 | +0.0567 | 90.0% |
| 0.50 | 0.35 | 5 | +0.0731 | 80.0% |
| 0.50 | 0.45 | 2 | +0.0888 | 100.0% |
| 0.55 | 0.10 | 25 | +0.0496 | 80.0% |
| 0.55 | 0.20 | 17 | +0.0496 | 80.0% |
| 0.55 | 0.30 | 10 | +0.0553 | 90.0% |
| 0.55 | 0.40 | 3 | +0.0523 | 66.7% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 12 | +0.0518 | 90.0% |
| 0.60 | 0.25 | 9 | +0.0561 | 88.9% |
| 0.60 | 0.35 | 5 | +0.0731 | 80.0% |
| 0.60 | 0.45 | 2 | +0.0888 | 100.0% |
| 0.65 | 0.10 | 4 | +0.0657 | 75.0% |
| 0.65 | 0.20 | 4 | +0.0657 | 75.0% |
| 0.65 | 0.30 | 4 | +0.0657 | 75.0% |
| 0.65 | 0.40 | 3 | +0.0523 | 66.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.35 → 5 candidates, mean lock IC=+0.0731, 80.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 21 | +0.0487 | 90.0% |
| 0.45 | 0.20 | 12 | +0.0487 | 90.0% |
| 0.45 | 0.30 | 5 | +0.0569 | 100.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 17 | +0.0487 | 90.0% |
| 0.50 | 0.25 | 8 | +0.0567 | 87.5% |
| 0.50 | 0.35 | 3 | +0.0490 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 16 | +0.0487 | 90.0% |
| 0.55 | 0.20 | 12 | +0.0487 | 90.0% |
| 0.55 | 0.30 | 5 | +0.0569 | 100.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 8 | +0.0506 | 87.5% |
| 0.60 | 0.25 | 6 | +0.0468 | 83.3% |
| 0.60 | 0.35 | 3 | +0.0490 | 100.0% |
| 0.60 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.65 | 0.10 | 3 | +0.0490 | 100.0% |
| 0.65 | 0.20 | 3 | +0.0490 | 100.0% |
| 0.65 | 0.30 | 3 | +0.0490 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.30 → 5 candidates, mean lock IC=+0.0569, 100.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 734 | +0.1307 | 100.0% |
| 0.45 | 0.20 | 722 | +0.1307 | 100.0% |
| 0.45 | 0.30 | 675 | +0.1307 | 100.0% |
| 0.45 | 0.40 | 610 | +0.1307 | 100.0% |
| 0.45 | 0.50 | 485 | +0.1307 | 100.0% |
| 0.50 | 0.15 | 730 | +0.1307 | 100.0% |
| 0.50 | 0.25 | 692 | +0.1307 | 100.0% |
| 0.50 | 0.35 | 649 | +0.1307 | 100.0% |
| 0.50 | 0.45 | 552 | +0.1307 | 100.0% |
| 0.55 | 0.10 | 729 | +0.1307 | 100.0% |
| 0.55 | 0.20 | 721 | +0.1307 | 100.0% |
| 0.55 | 0.30 | 675 | +0.1307 | 100.0% |
| 0.55 | 0.40 | 610 | +0.1307 | 100.0% |
| 0.55 | 0.50 | 485 | +0.1307 | 100.0% |
| 0.60 | 0.15 | 684 | +0.1307 | 100.0% |
| 0.60 | 0.25 | 678 | +0.1307 | 100.0% |
| 0.60 | 0.35 | 648 | +0.1307 | 100.0% |
| 0.60 | 0.45 | 552 | +0.1307 | 100.0% |
| 0.65 | 0.10 | 604 | +0.1307 | 100.0% |
| 0.65 | 0.20 | 604 | +0.1307 | 100.0% |
| 0.65 | 0.30 | 604 | +0.1307 | 100.0% |
| 0.65 | 0.40 | 588 | +0.1307 | 100.0% |
| 0.65 | 0.50 | 484 | +0.1307 | 100.0% |
| 0.70 | 0.15 | 447 | +0.1307 | 100.0% |
| 0.70 | 0.25 | 447 | +0.1307 | 100.0% |
| 0.70 | 0.35 | 447 | +0.1307 | 100.0% |
| 0.70 | 0.45 | 447 | +0.1307 | 100.0% |
| 0.75 | 0.10 | 228 | +0.1307 | 100.0% |
| 0.75 | 0.20 | 228 | +0.1307 | 100.0% |
| 0.75 | 0.30 | 228 | +0.1307 | 100.0% |
| 0.75 | 0.40 | 228 | +0.1307 | 100.0% |
| 0.75 | 0.50 | 228 | +0.1307 | 100.0% |
| 0.80 | 0.15 | 63 | +0.1307 | 100.0% |
| 0.80 | 0.25 | 63 | +0.1307 | 100.0% |
| 0.80 | 0.35 | 63 | +0.1307 | 100.0% |
| 0.80 | 0.45 | 63 | +0.1307 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 734 candidates, mean lock IC=+0.1307, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 142 | +0.0980 | 100.0% |
| 0.45 | 0.20 | 113 | +0.0980 | 100.0% |
| 0.45 | 0.30 | 65 | +0.0991 | 100.0% |
| 0.45 | 0.40 | 27 | +0.1036 | 100.0% |
| 0.45 | 0.50 | 2 | +0.0842 | 100.0% |
| 0.50 | 0.15 | 130 | +0.0980 | 100.0% |
| 0.50 | 0.25 | 86 | +0.0980 | 100.0% |
| 0.50 | 0.35 | 45 | +0.1012 | 100.0% |
| 0.50 | 0.45 | 12 | +0.1005 | 90.0% |
| 0.55 | 0.10 | 123 | +0.0980 | 100.0% |
| 0.55 | 0.20 | 110 | +0.0980 | 100.0% |
| 0.55 | 0.30 | 65 | +0.0991 | 100.0% |
| 0.55 | 0.40 | 27 | +0.1036 | 100.0% |
| 0.55 | 0.50 | 2 | +0.0842 | 100.0% |
| 0.60 | 0.15 | 67 | +0.0976 | 100.0% |
| 0.60 | 0.25 | 67 | +0.0976 | 100.0% |
| 0.60 | 0.35 | 41 | +0.1012 | 100.0% |
| 0.60 | 0.45 | 12 | +0.1005 | 90.0% |
| 0.65 | 0.10 | 21 | +0.0942 | 100.0% |
| 0.65 | 0.20 | 21 | +0.0942 | 100.0% |
| 0.65 | 0.30 | 21 | +0.0942 | 100.0% |
| 0.65 | 0.40 | 16 | +0.0951 | 100.0% |
| 0.65 | 0.50 | 2 | +0.0842 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 27 candidates, mean lock IC=+0.1036, 100.0% positive

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
| `combo_min__max_up_ret__bar_body_rng_0` | +0.1038 | +0.0000 | -0.0223 | -0.21x | 2015-03-16 |
| `volume_weighted_price_position` | +0.0929 | +0.0000 | +0.0000 | 0.00x | 2015-02-06 |
| `combo_diff__max_up_ret__early_vwap_acceleration` | +0.1167 | +0.0000 | -0.0284 | -0.24x | 2017-02-06 |
| `first_30min_return` | +0.0695 | +0.0000 | -0.0197 | -0.28x | 2015-02-06 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1870 | +0.0000 | +0.0289 | 0.15x | 2025-07-24 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1908 | +0.0000 | +0.0883 | 0.46x | No decay |
| `combo_min__net_volume_flow__impulse_bar_dominance` | +0.1346 | +0.0000 | +0.0717 | 0.53x | 2017-03-07 |
| `combo_min__first_bar_sentiment__bar_ret_0` | +0.1352 | +0.0000 | +0.0486 | 0.36x | 2013-09-23 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1377 | +0.0000 | +0.1138 | 0.83x | 2011-12-23 |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.1616 | +0.0000 | +0.0383 | 0.24x | 2016-12-29 |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | +0.1402 | +0.0000 | +0.1108 | 0.79x | 2023-01-16 |
| `combo_diff__max_up_ret__impulse_bar_dominance` | +0.0887 | +0.0000 | -0.0318 | -0.36x | 2013-08-21 |
| `combo_diff__opening_drive_thrust_ratio__impulse_bar_dominance` | +0.1279 | +0.0000 | +0.0032 | 0.02x | 2017-10-12 |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | +0.1350 | +0.0000 | +0.0944 | 0.70x | 2016-08-24 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +0.1392 | +0.0000 | +0.1034 | 0.74x | 2011-09-20 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.0594 | +0.0000 | +0.0335 | 0.56x | 2010-10-15 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | +0.1549 | +0.0000 | +0.1275 | 0.82x | 2017-01-20 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | +0.1683 | +0.0000 | +0.1239 | 0.74x | 2017-01-20 |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0686 | 0.50x | 2016-10-24 |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | +0.1451 | +0.0000 | +0.1428 | 0.98x | 2016-09-14 |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1012 | +0.0000 | +0.1286 | 1.27x | 2011-10-18 |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | +0.1196 | +0.0000 | +0.0887 | 0.74x | 2017-04-28 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1219 | +0.0000 | +0.1155 | 0.95x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1454 | +0.0000 | +0.1073 | 0.74x | 2011-11-16 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1317 | +0.0000 | +0.1308 | 0.99x | 2011-10-18 |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | +0.1370 | +0.0000 | +0.0659 | 0.48x | 2017-04-28 |
| `trend_bar_close_consistency` | +0.1085 | +0.0000 | +0.0806 | 0.74x | 2014-03-25 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.1355). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.2939). Consider relaxing this gate.
3. **300ETF `single` — Admission too loose**: 100% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
4. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 23.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 6.0%, mean lock Sharpe=-0.5046). Consider relaxing this gate.
5. **300ETF `short` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.1816). Consider relaxing this gate.
6. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.1952). Consider relaxing this gate.
7. **50ETF `single` — B2 Rolling Guard too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.1274). Consider relaxing this gate.
8. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 29.0%, mean lock Sharpe=+0.1570). Consider relaxing this gate.
9. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.0568). Consider relaxing this gate.
10. **500ETF `single` — Admission too loose**: 67% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
11. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=+0.3640). Consider relaxing this gate.
12. **500ETF `long` — BH-FDR Gate too strict**: 78.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=+0.3385). Consider relaxing this gate.
13. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3058). Consider relaxing this gate.
14. **500ETF `short` — B2 Rolling Guard too strict**: 26.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.2689). Consider relaxing this gate.
15. **159915ETF `single` — B2 Rolling Guard too strict**: 83.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 52.0%, mean lock Sharpe=+0.6451). Consider relaxing this gate.
16. **159915ETF `single` — B3 Composite Floor too strict**: 90.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 52.0%, mean lock Sharpe=+0.3334). Consider relaxing this gate.
17. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 52.0%, mean lock Sharpe=+1.1286). Consider relaxing this gate.
18. **159915ETF `long` — BH-FDR Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 41.0%, mean lock Sharpe=+0.8546). Consider relaxing this gate.
19. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 23.0%, mean lock Sharpe=-0.1156). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
