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

### 300ETF — `single` (Full Model Lockbox IC: +0.0709, Sharpe: +0.3302)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.1188 | +0.0703 | +0.0703 | +0.3240 | 0.90 | 1/8 | 0.73 | 0.73 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0001 | +0.0148 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1132 | +0.0876 | +0.0876 | +0.7186 | 0.79 | 1/8 | 0.71 | 0.71 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0027 | -0.1277 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1156 | +0.0706 | +0.0706 | +0.8555 | 0.84 | 1/8 | 0.59 | 0.47 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0006 | -0.0158 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1216 | +0.0529 | +0.0529 | +0.3808 | 0.68 | 1/8 | 0.73 | 0.79 | `rbreaker_sell_setup_proximity_early` (1.02) | -0.0036 | +0.1054 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0999 | +0.0776 | +0.0776 | +0.8447 | 0.65 | 0/8 | 0.49 | 0.62 | `rbreaker_sell_setup_proximity_early` (1.02) | +0.0020 | -0.0733 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0872 | +0.0567 | +0.0567 | +0.4294 | 0.84 | 1/8 | 0.72 | 1.37 | `volume_weighted_price_position` (1.18) | +0.0027 | -0.3364 |
| `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.0931 | +0.0581 | +0.0581 | +0.1301 | 1.13 | 1/8 | 0.76 | 0.91 | `rbreaker_buy_setup_proximity_early` (1.45) | -0.0044 | -0.2466 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0354 | -0.0017 | -0.0017 | -0.6567 | 1.27 | 1/8 | 2.11 | -4.04 | `volume_weighted_price_position` (1.18) | -0.0000 | -0.1911 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0680 | +0.0048 | +0.0048 | -0.5873 | 0.81 | 1/8 | 0.58 | 0.79 | `volume_surge_direction` (0.97) | +0.0000 | +0.0000 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | Volatility & Oscillators | +1 | +0.0742 | +0.0529 | +0.0529 | +0.5709 | 0.72 | 1/8 | 0.59 | 0.89 | `bar_vol_0` (1.91) | -0.0006 | -0.0108 |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0665 | +0.0522 | +0.0522 | -0.1443 | 0.73 | 2/8 | 1.82 | 2.07 | `limit_down_proximity_early` (1.45) | -0.0005 | -0.0308 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1178, Sharpe: +0.7859)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | Other Technical | +1 | +0.1524 | +0.0889 | +0.0889 | +0.2828 | 0.47 | 0/8 | 0.59 | 0.54 | `trend_day_regime_conviction` (0.44) | -0.0008 | -0.1229 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1759 | +0.0883 | +0.0883 | +0.6113 | 0.43 | 0/8 | 0.53 | 0.40 | `first_bar_sentiment` (0.45) | +0.0009 | +0.0708 |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1641 | +0.0912 | +0.0912 | +0.1026 | 0.38 | 0/8 | 0.61 | 0.68 | `first_bar_sentiment` (0.45) | -0.0022 | -0.1139 |
| `combo_min__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1702 | +0.0726 | +0.0726 | -0.7944 | 0.35 | 0/8 | 0.55 | 0.48 | `first_bar_sentiment` (0.45) | -0.0032 | +0.1569 |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1624 | +0.0992 | +0.0992 | +0.5697 | 0.47 | 0/8 | 0.51 | 0.39 | `star50_limit_proximity_early` (0.61) | +0.0005 | -0.1437 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1709 | +0.0780 | +0.0780 | +0.1459 | 0.49 | 0/8 | 0.50 | 0.42 | `late_bar_momentum` (0.70) | -0.0022 | -0.0389 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1544 | +0.1215 | +0.1215 | +0.9205 | 0.53 | 0/8 | 0.69 | 0.52 | `star50_limit_proximity_early` (0.61) | +0.0033 | +0.2873 |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.1440 | +0.0862 | +0.0862 | -0.3387 | 0.48 | 0/8 | 0.82 | 0.59 | `double_bottom_bull_flag_early` (1.21) | -0.0003 | +0.0854 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1484 | +0.1175 | +0.1175 | +0.4851 | 0.42 | 0/8 | 0.58 | 0.52 | `close_vs_open_range` (0.47) | +0.0026 | +0.0343 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1489 | +0.1058 | +0.1058 | +1.1405 | 0.42 | 0/8 | 0.56 | 0.59 | `volume_weighted_momentum_acceleration` (0.57) | +0.0010 | -0.0727 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.0773 | +0.0475 | +0.0475 | -0.0575 | 1.25 | 2/8 | 0.12 | 0.06 | `volume_weighted_momentum_acceleration` (0.57) | -0.0002 | +0.1670 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1322 | +0.1300 | +0.1300 | +0.6068 | 0.44 | 0/8 | 0.66 | 0.67 | `star50_limit_proximity_early` (0.61) | +0.0028 | -0.0178 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | Other Technical | +1 | +0.0671 | +0.0716 | +0.0716 | +0.0053 | 0.84 | 1/8 | 1.18 | 0.87 | `double_bottom_bull_flag_early` (1.21) | -0.0001 | +0.0085 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1369 | +0.1223 | +0.1223 | +0.4818 | 0.39 | 0/8 | 0.73 | 0.83 | `star50_limit_proximity_early` (0.61) | +0.0014 | +0.2370 |
| `combo_sig_product__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1603 | +0.0792 | +0.0792 | +0.3953 | 0.43 | 0/8 | 0.52 | 0.66 | `bar_ret_0` (0.41) | -0.0004 | +0.0247 |
| `combo_ratio__bar_ret_0__net_volume_flow` | Volatility & Oscillators | +1 | +0.1119 | +0.0500 | +0.0500 | +0.3938 | 0.52 | 0/8 | 0.53 | 0.67 | `bar_ret_0` (0.41) | +0.0007 | +0.1102 |
| `combo_sig_product__first_bar_sentiment__close_vs_open_range` | Gap / Overnight Reversal | +1 | +0.1316 | +0.0673 | +0.0673 | -0.4527 | 0.42 | 0/8 | 0.64 | 0.46 | `close_vs_open_range` (0.47) | +0.0001 | -0.0497 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.0947 | -0.0211 | -0.0211 | -0.4893 | 0.85 | 1/8 | 0.50 | 0.17 | `close_vs_open_range` (0.47) | -0.0019 | +0.0139 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1481, Sharpe: +1.6308)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1650 | +0.1008 | +0.1008 | +1.0903 | 0.54 | 1/8 | 0.80 | 0.42 | `first_bar_sentiment` (0.75) | -0.0027 | -0.0641 |
| `combo_tri_median__max_up_ret__first_bar_sentiment__star50_limit_proximity_early` | Gap / Overnight Reversal | +1 | +0.1535 | +0.1236 | +0.1236 | +0.8616 | 0.53 | 0/8 | 1.08 | 0.76 | `first_bar_sentiment` (0.75) | -0.0008 | +0.2295 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1299 | +0.0937 | +0.0937 | +0.6050 | 0.61 | 1/8 | 1.14 | 0.91 | `yesterday_early_vwap_dev` (1.10) | +0.0038 | -0.2511 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | Other Technical | +1 | +0.1376 | +0.1458 | +0.1458 | +1.3138 | 0.56 | 0/8 | 1.26 | 1.00 | `star50_limit_proximity_early` (0.69) | +0.0050 | +0.1055 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1562 | +0.1219 | +0.1219 | +1.3598 | 0.48 | 0/8 | 0.95 | 0.87 | `star50_limit_proximity_early` (0.69) | -0.0013 | +0.0768 |
| `combo_max__max_up_ret__bar_ret_0` | Intraday Range Momentum | +1 | +0.1416 | +0.0960 | +0.0960 | +0.2321 | 0.35 | 0/8 | 1.04 | 0.89 | `bar_ret_0` (0.44) | -0.0003 | +0.0534 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1532 | +0.1260 | +0.1260 | +1.0555 | 0.36 | 0/8 | 1.19 | 1.11 | `rbreaker_sell_setup_proximity_early` (0.44) | -0.0005 | +0.2198 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1127 | +0.1302 | +0.1302 | +0.6763 | 0.66 | 1/8 | 0.77 | 0.68 | `yesterday_first_30min_return` (0.92) | +0.0089 | +0.3705 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1095 | +0.1090 | +0.1090 | +0.3724 | 0.66 | 0/8 | 1.03 | 1.15 | `star50_limit_proximity_early` (0.69) | +0.0002 | -0.0414 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0591 | -0.0132 | -0.0132 | -0.5256 | 0.84 | 2/8 | 0.53 | 0.98 | `volatility_expansion_trend_vector` (0.69) | -0.0005 | +0.2174 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 79.0% lock IC > 0, 34.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2303_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1205 | 30 | 100.0% | 63.3% | +0.0608 | +0.1497 |
| B2 Rolling Guard | 204 | 30 | 100.0% | 93.3% | +0.0554 | +0.3080 |
| BH-FDR Gate | 5 | 5 | 100.0% | 0.0% | +0.0298 | -0.4561 |
| B3 Composite Floor | 35 | 30 | 96.7% | 73.3% | +0.0500 | +0.2891 |
| B4 Correlation Gate | 196 | 30 | 100.0% | 96.7% | +0.0659 | +0.3913 |

**Admitted Pool Summary**: 20 features, False Positive Rate = 15.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0551, Mean Lock Sharpe = +0.2959

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

- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2265, Lock IC=+0.0937, Lock Sharpe=+1.0629
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Lock Sharpe=+0.5292
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2347, Lock IC=+0.0717, Lock Sharpe=+0.5292
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2346, Lock IC=+0.0716, Lock Sharpe=+0.5292
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2346, Lock IC=+0.0716, Lock Sharpe=+0.5292

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

_Null Baseline (un-gated candidate pool): 71.0% lock IC > 0, 51.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0377_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1823 | 30 | 100.0% | 96.7% | +0.0901 | +0.5392 |
| B2 Rolling Guard | 221 | 30 | 100.0% | 70.0% | +0.0755 | +0.2347 |
| BH-FDR Gate | 7 | 7 | 85.7% | 0.0% | +0.0145 | -0.6172 |
| B3 Composite Floor | 150 | 30 | 100.0% | 100.0% | +0.0922 | +0.4999 |
| B4 Correlation Gate | 660 | 30 | 100.0% | 100.0% | +0.1071 | +0.6977 |

**Admitted Pool Summary**: 43 features, False Positive Rate = 14.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0929, Mean Lock Sharpe = +0.4113

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2312, Lock IC=+0.1016, Lock Sharpe=+1.2136
- `combo_clamp_diff__star50_limit_proximity_early__body_size_progression`: Train IC=+0.2364, Lock IC=+0.0979, Lock Sharpe=+1.0894
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2937, Lock IC=+0.1129, Lock Sharpe=+0.9464
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.2819, Lock IC=+0.1134, Lock Sharpe=+0.8586
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2910, Lock IC=+0.1185, Lock Sharpe=+0.8115

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__body_size_progression__first_bar_return`: Train IC=+0.1879, Lock IC=+0.0787, Lock Sharpe=+0.7240
- `combo_z_diff__body_size_progression__first_bar_return`: Train IC=+0.1879, Lock IC=+0.0787, Lock Sharpe=+0.7240
- `combo_rel_diff__body_size_progression__first_bar_return`: Train IC=+0.1888, Lock IC=+0.0693, Lock Sharpe=+0.5882
- `combo_rel_diff__body_size_progression__bar_ret_0`: Train IC=+0.1881, Lock IC=+0.0693, Lock Sharpe=+0.5882
- `combo_max__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1971, Lock IC=+0.1086, Lock Sharpe=+0.5808

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2749, Lock IC=+0.1079, Lock Sharpe=+0.8023
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2890, Lock IC=+0.1056, Lock Sharpe=+0.7824

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2956, Lock IC=+0.1134, Lock Sharpe=+1.1317
- `combo_tri_min__net_volume_flow__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2971, Lock IC=+0.1120, Lock Sharpe=+1.1041
- `combo_tri_min__opening_auction_imbalance__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2971, Lock IC=+0.1120, Lock Sharpe=+1.1041
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2996, Lock IC=+0.1132, Lock Sharpe=+0.9985

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

_Null Baseline (un-gated candidate pool): 75.0% lock IC > 0, 58.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.2575_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1044 | 30 | 100.0% | 93.3% | +0.0918 | +0.6937 |
| B2 Rolling Guard | 258 | 30 | 100.0% | 96.7% | +0.1052 | +0.5922 |
| BH-FDR Gate | 2 | 2 | 0.0% | 0.0% | -0.0292 | -1.0342 |
| B3 Composite Floor | 161 | 30 | 100.0% | 100.0% | +0.1137 | +1.0091 |
| B4 Correlation Gate | 179 | 30 | 100.0% | 100.0% | +0.1284 | +1.3572 |

**Admitted Pool Summary**: 22 features, False Positive Rate = 4.5% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1105, Mean Lock Sharpe = +0.7971

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2597, Lock IC=+0.0980, Lock Sharpe=+1.7078
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Lock Sharpe=+1.3789
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2192, Lock IC=+0.1373, Lock Sharpe=+1.3789
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2935, Lock IC=+0.0960, Lock Sharpe=+1.3385
- `combo_rank_min__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.2615, Lock IC=+0.0906, Lock Sharpe=+1.3244

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2210, Lock IC=+0.1301, Lock Sharpe=+1.3582
- `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1946, Lock IC=+0.1281, Lock Sharpe=+1.3297
- `combo_tri_median__max_up_ret__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2326, Lock IC=+0.0999, Lock Sharpe=+1.0768
- `combo_tri_median__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2348, Lock IC=+0.1189, Lock Sharpe=+1.0159
- `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1987, Lock IC=+0.1327, Lock Sharpe=+0.7895

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0`: Train IC=+0.2828, Lock IC=+0.1401, Lock Sharpe=+1.7039
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.3073, Lock IC=+0.1158, Lock Sharpe=+1.5577
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2419, Lock IC=+0.1379, Lock Sharpe=+1.4133
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__impulse_bar_dominance`: Train IC=+0.2699, Lock IC=+0.1278, Lock Sharpe=+1.3924
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2419, Lock IC=+0.1373, Lock Sharpe=+1.3304

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2800, Lock IC=+0.1246, Lock Sharpe=+1.6742
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2774, Lock IC=+0.1366, Lock Sharpe=+1.6742
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Lock Sharpe=+1.6287
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2700, Lock IC=+0.1247, Lock Sharpe=+1.6287
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2904, Lock IC=+0.1209, Lock Sharpe=+1.5937

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
| 0.45 | 0.10 | 1380 | +0.1125 | 100.0% |
| 0.45 | 0.20 | 1363 | +0.1125 | 100.0% |
| 0.45 | 0.30 | 1316 | +0.1125 | 100.0% |
| 0.45 | 0.40 | 1193 | +0.1125 | 100.0% |
| 0.45 | 0.50 | 971 | +0.1125 | 100.0% |
| 0.50 | 0.15 | 1375 | +0.1125 | 100.0% |
| 0.50 | 0.25 | 1344 | +0.1125 | 100.0% |
| 0.50 | 0.35 | 1263 | +0.1125 | 100.0% |
| 0.50 | 0.45 | 1100 | +0.1125 | 100.0% |
| 0.55 | 0.10 | 1379 | +0.1125 | 100.0% |
| 0.55 | 0.20 | 1363 | +0.1125 | 100.0% |
| 0.55 | 0.30 | 1316 | +0.1125 | 100.0% |
| 0.55 | 0.40 | 1193 | +0.1125 | 100.0% |
| 0.55 | 0.50 | 971 | +0.1125 | 100.0% |
| 0.60 | 0.15 | 1335 | +0.1125 | 100.0% |
| 0.60 | 0.25 | 1329 | +0.1125 | 100.0% |
| 0.60 | 0.35 | 1262 | +0.1125 | 100.0% |
| 0.60 | 0.45 | 1100 | +0.1125 | 100.0% |
| 0.65 | 0.10 | 1185 | +0.1125 | 100.0% |
| 0.65 | 0.20 | 1185 | +0.1125 | 100.0% |
| 0.65 | 0.30 | 1185 | +0.1125 | 100.0% |
| 0.65 | 0.40 | 1145 | +0.1125 | 100.0% |
| 0.65 | 0.50 | 971 | +0.1125 | 100.0% |
| 0.70 | 0.15 | 876 | +0.1125 | 100.0% |
| 0.70 | 0.25 | 876 | +0.1125 | 100.0% |
| 0.70 | 0.35 | 876 | +0.1125 | 100.0% |
| 0.70 | 0.45 | 876 | +0.1125 | 100.0% |
| 0.75 | 0.10 | 456 | +0.1125 | 100.0% |
| 0.75 | 0.20 | 456 | +0.1125 | 100.0% |
| 0.75 | 0.30 | 456 | +0.1125 | 100.0% |
| 0.75 | 0.40 | 456 | +0.1125 | 100.0% |
| 0.75 | 0.50 | 456 | +0.1125 | 100.0% |
| 0.80 | 0.15 | 162 | +0.1085 | 100.0% |
| 0.80 | 0.25 | 162 | +0.1085 | 100.0% |
| 0.80 | 0.35 | 162 | +0.1085 | 100.0% |
| 0.80 | 0.45 | 162 | +0.1085 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1380 candidates, mean lock IC=+0.1125, 100.0% positive

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
| 0.45 | 0.10 | 629 | +0.1271 | 100.0% |
| 0.45 | 0.20 | 605 | +0.1271 | 100.0% |
| 0.45 | 0.30 | 522 | +0.1271 | 100.0% |
| 0.45 | 0.40 | 386 | +0.1271 | 100.0% |
| 0.45 | 0.50 | 237 | +0.1271 | 100.0% |
| 0.50 | 0.15 | 623 | +0.1271 | 100.0% |
| 0.50 | 0.25 | 577 | +0.1271 | 100.0% |
| 0.50 | 0.35 | 457 | +0.1271 | 100.0% |
| 0.50 | 0.45 | 317 | +0.1271 | 100.0% |
| 0.55 | 0.10 | 622 | +0.1271 | 100.0% |
| 0.55 | 0.20 | 604 | +0.1271 | 100.0% |
| 0.55 | 0.30 | 522 | +0.1271 | 100.0% |
| 0.55 | 0.40 | 386 | +0.1271 | 100.0% |
| 0.55 | 0.50 | 237 | +0.1271 | 100.0% |
| 0.60 | 0.15 | 570 | +0.1271 | 100.0% |
| 0.60 | 0.25 | 553 | +0.1271 | 100.0% |
| 0.60 | 0.35 | 457 | +0.1271 | 100.0% |
| 0.60 | 0.45 | 317 | +0.1271 | 100.0% |
| 0.65 | 0.10 | 401 | +0.1271 | 100.0% |
| 0.65 | 0.20 | 401 | +0.1271 | 100.0% |
| 0.65 | 0.30 | 401 | +0.1271 | 100.0% |
| 0.65 | 0.40 | 359 | +0.1271 | 100.0% |
| 0.65 | 0.50 | 237 | +0.1271 | 100.0% |
| 0.70 | 0.15 | 165 | +0.1271 | 100.0% |
| 0.70 | 0.25 | 165 | +0.1271 | 100.0% |
| 0.70 | 0.35 | 165 | +0.1271 | 100.0% |
| 0.70 | 0.45 | 163 | +0.1271 | 100.0% |
| 0.75 | 0.10 | 44 | +0.1229 | 100.0% |
| 0.75 | 0.20 | 44 | +0.1229 | 100.0% |
| 0.75 | 0.30 | 44 | +0.1229 | 100.0% |
| 0.75 | 0.40 | 44 | +0.1229 | 100.0% |
| 0.75 | 0.50 | 44 | +0.1229 | 100.0% |
| 0.80 | 0.15 | 6 | +0.0417 | 66.7% |
| 0.80 | 0.25 | 6 | +0.0417 | 66.7% |
| 0.80 | 0.35 | 6 | +0.0417 | 66.7% |
| 0.80 | 0.45 | 6 | +0.0417 | 66.7% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 629 candidates, mean lock IC=+0.1271, 100.0% positive

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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1127 | +0.0000 | +0.0885 | 0.79x | 2016-08-24 |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1193 | +0.0000 | +0.0706 | 0.59x | 2017-06-09 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1172 | +0.0000 | +0.0529 | 0.45x | 2015-02-06 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.0965 | +0.0000 | +0.0776 | 0.80x | 2013-09-23 |
| `combo_mean__max_up_ret__volume_weighted_price_position` | +0.1093 | +0.0000 | +0.0567 | 0.52x | 2015-02-06 |
| `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early` | +0.0930 | +0.0000 | +0.0581 | 0.63x | 2011-09-20 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0431 | +0.0000 | -0.0017 | -0.04x | 2010-10-15 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +0.0571 | +0.0000 | +0.0048 | 0.08x | 2010-10-15 |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0` | +0.0655 | +0.0000 | +0.0529 | 0.81x | 2017-10-12 |
| `combo_rel_diff__limit_down_proximity_early__volume_concentration` | +0.0575 | +0.0000 | +0.0522 | 0.91x | 2013-06-24 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_rank_max__opening_drive_thrust_ratio__trend_day_regime_conviction` | +0.1798 | +0.0000 | +0.0890 | 0.49x | 2016-11-30 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1729 | +0.0000 | +0.0883 | 0.51x | No decay |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | +0.1710 | +0.0000 | +0.0912 | 0.53x | 2020-01-06 |
| `combo_min__max_up_ret__first_bar_sentiment` | +0.1707 | +0.0000 | +0.0726 | 0.43x | 2020-01-06 |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | +0.1690 | +0.0000 | +0.0992 | 0.59x | 2019-12-05 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +0.1730 | +0.0000 | +0.0780 | 0.45x | 2014-06-05 |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1772 | +0.0000 | +0.1217 | 0.69x | 2016-08-24 |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.1513 | +0.0000 | +0.0862 | 0.57x | 2022-09-09 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1692 | +0.0000 | +0.1175 | 0.69x | 2020-01-06 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1531 | +0.0000 | +0.1058 | 0.69x | No decay |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volume_weighted_momentum_acceleration` | +0.0760 | +0.0000 | +0.0475 | 0.62x | 2012-05-07 |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | +0.1461 | +0.0000 | +0.1300 | 0.89x | 2016-08-24 |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | +0.0991 | +0.0000 | +0.0716 | 0.72x | 2016-08-24 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1397 | +0.0000 | +0.1223 | 0.88x | 2011-12-23 |
| `combo_sig_product__max_up_ret__bar_ret_0` | +0.1680 | +0.0000 | +0.0792 | 0.47x | 2017-04-07 |
| `combo_ratio__bar_ret_0__net_volume_flow` | +0.1031 | +0.0000 | +0.0500 | 0.49x | 2013-09-23 |
| `combo_sig_product__first_bar_sentiment__close_vs_open_range` | +0.1385 | +0.0000 | +0.0673 | 0.49x | 2020-01-06 |
| `combo_abs_diff__max_up_ret__close_vs_open_range` | +0.0641 | +0.0000 | -0.0211 | -0.33x | 2010-10-15 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1630 | +0.0000 | +0.1008 | 0.62x | 2017-04-28 |
| `combo_tri_median__max_up_ret__first_bar_sentiment__star50_limit_proximity_early` | +0.1591 | +0.0000 | +0.1236 | 0.78x | 2017-04-28 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1188 | +0.0000 | +0.0937 | 0.79x | 2011-10-18 |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | +0.1538 | +0.0000 | +0.1458 | 0.95x | 2016-10-24 |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | +0.1609 | +0.0000 | +0.1219 | 0.76x | 2017-01-20 |
| `combo_max__max_up_ret__bar_ret_0` | +0.1537 | +0.0000 | +0.0960 | 0.62x | 2017-04-28 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1649 | +0.0000 | +0.1260 | 0.76x | 2017-01-20 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1186 | +0.0000 | +0.1312 | 1.11x | 2017-01-20 |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1067 | +0.0000 | +0.1090 | 1.02x | 2011-10-18 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0622 | +0.0000 | -0.0132 | -0.21x | 2012-02-22 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 63.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.1497). Consider relaxing this gate.
2. **300ETF `single` — B2 Rolling Guard too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.3080). Consider relaxing this gate.
3. **300ETF `single` — B3 Composite Floor too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.2891). Consider relaxing this gate.
4. **300ETF `single` — B4 Correlation Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 34.0%, mean lock Sharpe=+0.3913). Consider relaxing this gate.
5. **300ETF `short` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.2417). Consider relaxing this gate.
6. **300ETF `short` — BH-FDR Gate too strict**: 85.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=+0.2273). Consider relaxing this gate.
7. **300ETF `short` — B3 Composite Floor too strict**: 40.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 14.0%, mean lock Sharpe=-0.1028). Consider relaxing this gate.
8. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 53.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 19.0%, mean lock Sharpe=-0.0069). Consider relaxing this gate.
9. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.2106). Consider relaxing this gate.
10. **50ETF `short` — BH-FDR Gate too strict**: 16.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 10.0%, mean lock Sharpe=-0.5453). Consider relaxing this gate.
11. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.5392). Consider relaxing this gate.
12. **500ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.4999). Consider relaxing this gate.
13. **500ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.6977). Consider relaxing this gate.
14. **500ETF `long` — BH-FDR Gate too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 18.0%, mean lock Sharpe=-0.1712). Consider relaxing this gate.
15. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.1404). Consider relaxing this gate.
16. **159915ETF `single` — 7-Year Jackknife Sign Stability too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 58.0%, mean lock Sharpe=+0.6937). Consider relaxing this gate.
17. **159915ETF `single` — B2 Rolling Guard too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 58.0%, mean lock Sharpe=+0.5922). Consider relaxing this gate.
18. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 58.0%, mean lock Sharpe=+1.0091). Consider relaxing this gate.
19. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 58.0%, mean lock Sharpe=+1.3572). Consider relaxing this gate.
20. **159915ETF `long` — BH-FDR Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 59.0%, mean lock Sharpe=+0.6527). Consider relaxing this gate.
21. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.1320). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
