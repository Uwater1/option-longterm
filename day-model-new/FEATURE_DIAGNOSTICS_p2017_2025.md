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

### 300ETF — `single` (Full Model Lockbox IC: +0.0330, Sharpe: -0.3457)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1012 | +0.0544 | +0.0544 | -0.0805 | 0.80 | 1/8 | 1.14 | 1.31 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0038 | +0.1539 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0957 | +0.0007 | +0.0007 | -1.2659 | 0.86 | 1/8 | 1.72 | 1.71 | `rbreaker_sell_setup_proximity_early` (1.21) | -0.0061 | -0.2559 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.0936 | -0.0022 | -0.0022 | -1.3090 | 0.89 | 1/8 | 1.36 | 0.75 | `volume_weighted_price_position` (1.24) | -0.0039 | +0.1008 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0976 | +0.0164 | +0.0164 | -0.7568 | 0.95 | 1/8 | 1.15 | 1.25 | `rbreaker_sell_setup_proximity_early` (1.21) | +0.0081 | -0.2022 |
| `combo_max__first_bar_return__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0790 | +0.0104 | +0.0104 | -0.1272 | 0.99 | 2/8 | 0.80 | 1.03 | `volume_surge_direction` (1.10) | -0.0010 | -0.3813 |
| `combo_tri_max__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.0904 | +0.0241 | +0.0241 | -0.9421 | 0.92 | 2/8 | 1.32 | 0.72 | `volume_weighted_price_position` (1.24) | +0.0019 | -0.0116 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Volatility & Oscillators | +1 | +0.0840 | +0.0303 | +0.0303 | -0.4943 | 0.99 | 1/8 | 1.07 | 0.93 | `volume_surge_direction` (1.10) | -0.0006 | +0.1025 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Other Technical | +1 | +0.0768 | +0.0753 | +0.0753 | -0.1501 | 0.98 | 2/8 | 1.48 | 0.96 | `star50_limit_proximity_early` (1.49) | +0.0116 | -0.1905 |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0364 | -0.0760 | -0.0760 | -2.1231 | 1.27 | 1/8 | 0.99 | 4.55 | `first_bar_sentiment` (1.06) | -0.0087 | -0.0234 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | Volatility & Oscillators | +1 | +0.0528 | -0.0133 | -0.0133 | -1.5530 | 0.65 | 0/8 | 0.75 | 0.49 | `double_bottom_bull_flag_early` (1.91) | -0.0008 | -0.0637 |
| `combo_min__bar_body_rng_0__demark_setup_reversal_early` | Other Technical | +1 | +0.0464 | -0.0600 | -0.0600 | -1.4098 | 1.27 | 2/8 | 0.44 | 0.50 | `demark_setup_reversal_early` (1.65) | -0.0048 | -0.0227 |
| `combo_abs_diff__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.0443 | +0.0103 | +0.0103 | -0.9746 | 1.33 | 3/8 | 0.77 | 0.43 | `first_bar_sentiment` (1.06) | +0.0012 | -0.0180 |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0534 | +0.0575 | +0.0575 | +0.6959 | 1.06 | 1/8 | 1.61 | 0.14 | `rbreaker_buy_setup_proximity_early` (2.51) | +0.0061 | +0.1592 |
| `combo_ratio__first_bar_return__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0796 | -0.0091 | -0.0091 | -0.5472 | 0.71 | 1/8 | 1.09 | 0.60 | `volume_surge_direction` (1.10) | +0.0000 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0923, Sharpe: +0.2324)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_mean__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1292 | +0.0469 | +0.0469 | -1.2311 | 0.36 | 0/8 | 0.79 | 0.56 | `bar_ret_0` (0.46) | -0.0032 | -0.3356 |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1475 | +0.0427 | +0.0427 | -0.2324 | 0.38 | 0/8 | 0.66 | 0.57 | `volume_weighted_momentum_acceleration` (0.47) | -0.0055 | +0.4011 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Intraday Range Momentum | +1 | +0.1453 | +0.0883 | +0.0883 | -0.5698 | 0.42 | 0/8 | 0.62 | 0.67 | `rbreaker_sell_setup_proximity_early` (0.41) | +0.0035 | +0.2411 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Intraday Range Momentum | +1 | +0.1364 | +0.0337 | +0.0337 | -1.4167 | 0.28 | 0/8 | 0.73 | 0.62 | `trend_bar_close_consistency` (0.54) | -0.0083 | -0.1568 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1050 | +0.0817 | +0.0817 | +0.3027 | 0.40 | 0/8 | 0.65 | 0.51 | `trend_bar_close_consistency` (0.54) | +0.0007 | -0.0055 |
| `combo_max__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1279 | +0.0247 | +0.0247 | -1.6524 | 0.46 | 0/8 | 0.90 | 0.54 | `first_bar_sentiment` (0.43) | -0.0024 | -0.1326 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1228 | +0.0958 | +0.0958 | +0.5075 | 0.45 | 0/8 | 0.41 | 0.41 | `bar_ret_0` (0.46) | +0.0023 | +0.3185 |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1186 | +0.1138 | +0.1138 | +0.2628 | 0.41 | 0/8 | 0.83 | 0.74 | `star50_limit_proximity_early` (0.50) | +0.0015 | +0.0690 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1090 | +0.0661 | +0.0661 | +1.4473 | 0.48 | 1/8 | 0.80 | 0.38 | `volume_weighted_momentum_acceleration` (0.47) | -0.0021 | +0.0765 |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | Other Technical | +1 | +0.1061 | +0.1335 | +0.1335 | +0.1748 | 0.61 | 1/8 | 1.41 | 1.86 | `star50_limit_proximity_early` (0.50) | +0.0041 | +0.1694 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1022 | +0.1034 | +0.1034 | +1.0177 | 0.50 | 0/8 | 0.50 | 0.34 | `max_down_ret` (0.55) | +0.0047 | +0.2333 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Other Technical | +1 | +0.0634 | +0.0335 | +0.0335 | +0.3145 | 0.77 | 1/8 | 0.59 | 0.61 | `trend_bar_close_consistency` (0.54) | +0.0004 | +0.2904 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1540, Sharpe: +1.7588)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0` | Other Technical | +1 | +0.1272 | +0.1191 | +0.1191 | +0.8724 | 0.44 | 0/8 | 1.47 | 2.32 | `impulse_bar_dominance` (0.77) | -0.0039 | +0.1636 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1320 | +0.1337 | +0.1337 | +0.9648 | 0.54 | 1/8 | 0.88 | 1.53 | `first_bar_sentiment` (0.86) | -0.0044 | +0.2756 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1332 | +0.1135 | +0.1135 | +0.7682 | 0.34 | 0/8 | 1.26 | 1.74 | `star50_limit_proximity_early` (0.52) | -0.0008 | +0.4581 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1304 | +0.1296 | +0.1296 | +0.3365 | 0.54 | 1/8 | 0.83 | 1.38 | `first_bar_return` (0.48) | -0.0034 | +0.2422 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1256 | +0.1258 | +0.1258 | +1.0333 | 0.60 | 0/8 | 1.25 | 2.06 | `volume_weighted_price_position` (0.77) | -0.0049 | +0.2461 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1429 | +0.1073 | +0.1073 | +0.1834 | 0.33 | 0/8 | 1.11 | 1.94 | `first_bar_return` (0.48) | +0.0019 | +0.1907 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1060 | +0.1511 | +0.1511 | +0.6805 | 0.55 | 1/8 | 1.85 | 5.93 | `volatility_expansion_trend_vector` (0.61) | +0.0023 | +0.1156 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1104 | +0.1100 | +0.1100 | +0.5568 | 0.67 | 1/8 | 0.87 | 1.54 | `yesterday_early_vwap_dev` (1.29) | +0.0041 | +0.4392 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0864 | +0.1079 | +0.1079 | -0.2788 | 0.88 | 1/8 | 2.54 | -8.81 | `yesterday_first_30min_return` (0.99) | +0.0018 | -0.2989 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1120 | +0.1308 | +0.1308 | +0.7043 | 0.52 | 1/8 | 1.38 | 3.68 | `volume_weighted_price_position` (0.77) | +0.0010 | +0.0459 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0983 | +0.1124 | +0.1124 | +0.3952 | 0.61 | 1/8 | 1.60 | 4.45 | `yesterday_first_30min_return` (0.99) | +0.0050 | +0.0974 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0883 | +0.0813 | +0.0813 | -0.1094 | 0.61 | 0/8 | 2.36 | 4.52 | `volume_weighted_price_position` (0.77) | -0.0018 | +0.1218 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0557 | -0.0153 | -0.0153 | -0.1443 | 0.97 | 1/8 | 0.26 | 0.12 | `volatility_expansion_trend_vector` (0.61) | -0.0007 | +0.1418 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 48.0% lock IC > 0, 19.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6442_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1114 | 30 | 86.7% | 36.7% | +0.0411 | -0.3449 |
| B2 Rolling Guard | 121 | 30 | 76.7% | 26.7% | +0.0265 | -0.3942 |
| BH-FDR Gate | 4 | 4 | 75.0% | 25.0% | +0.0237 | -0.4905 |
| B3 Composite Floor | 3 | 3 | 100.0% | 0.0% | +0.0184 | -1.0270 |
| B4 Correlation Gate | 339 | 30 | 66.7% | 30.0% | +0.0216 | -0.5161 |

**Admitted Pool Summary**: 25 features, False Positive Rate = 92.0% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0057, Mean Lock Sharpe = -0.7793

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ratio__limit_down_proximity_early__volume_concentration`: Train IC=+0.1720, Lock IC=+0.1235, Lock Sharpe=+0.9843
- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.1725, Lock IC=+0.1466, Lock Sharpe=+0.7732
- `combo_rel_diff__rbreaker_buy_setup_proximity_early__volume_concentration`: Train IC=+0.1725, Lock IC=+0.1466, Lock Sharpe=+0.7732
- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Lock Sharpe=+0.4449
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Lock Sharpe=+0.4449

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0963, Lock Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0963, Lock Sharpe=+0.8491
- `combo_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353
- `combo_z_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353
- `combo_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1325, Lock IC=+0.0920, Lock Sharpe=+0.5353

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Lock Sharpe=+0.1297

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Lock Sharpe=+0.3895
- `combo_z_sum__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2313, Lock IC=+0.0420, Lock Sharpe=+0.3895
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Lock Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Lock Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Lock Sharpe=+0.3783

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 6.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.8116_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 538 | 30 | 70.0% | 20.0% | +0.0193 | -0.5144 |
| B2 Rolling Guard | 41 | 30 | 23.3% | 10.0% | -0.0076 | -0.4749 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0266 | -1.2281 |

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

_Null Baseline (un-gated candidate pool): 57.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4381_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 518 | 30 | 73.3% | 36.7% | +0.0375 | -0.3299 |
| B2 Rolling Guard | 60 | 30 | 53.3% | 33.3% | -0.0027 | -0.2555 |
| BH-FDR Gate | 8 | 8 | 62.5% | 50.0% | +0.0200 | -0.1920 |
| B3 Composite Floor | 1 | 1 | 100.0% | 100.0% | +0.0684 | +0.3610 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.9794
- `combo_z_sum__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.1254, Lock IC=+0.0840, Lock Sharpe=+0.9794
- `combo_mean__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `combo_z_sum__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1252, Lock IC=+0.0965, Lock Sharpe=+0.8503
- `star50_limit_proximity_early`: Train IC=+0.1240, Lock IC=+0.0960, Lock Sharpe=+0.8503

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `pullback_depth_ratio`: Train IC=+0.0000, Lock IC=+0.0504, Lock Sharpe=+1.5711
- `double_bottom_bull_flag_early`: Train IC=+0.0000, Lock IC=+0.0395, Lock Sharpe=+0.9090
- `combo_sig_product__total_path_length__max_down_ret`: Train IC=+0.0376, Lock IC=+0.0550, Lock Sharpe=+0.8756
- `combo_sig_product__early_bid_ask_spread_proxy__limit_down_proximity_early`: Train IC=+0.0064, Lock IC=+0.0190, Lock Sharpe=+0.5424
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0389, Lock Sharpe=+0.4433

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.0708, Lock IC=+0.0119, Lock Sharpe=+0.7142
- `gap_pct`: Train IC=+0.1402, Lock IC=+0.1085, Lock Sharpe=+0.6926
- `combo_rank_max__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.1202, Lock IC=+0.0273, Lock Sharpe=+0.2891
- `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.1032, Lock IC=+0.0946, Lock Sharpe=+0.2733

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.2007, Lock IC=+0.0684, Lock Sharpe=+0.3610

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 68.0% lock IC > 0, 30.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4784_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 815 | 30 | 96.7% | 56.7% | +0.0378 | +0.1812 |
| B2 Rolling Guard | 76 | 30 | 83.3% | 46.7% | +0.0418 | +0.0118 |
| BH-FDR Gate | 3 | 3 | 0.0% | 0.0% | -0.0339 | -0.9002 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__volume_surge_max__roc10`: Train IC=+0.1513, Lock IC=+0.0272, Lock Sharpe=+1.0041
- `combo_rank_min__first_bar_volume__roc10`: Train IC=+0.1467, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_rank_min__bar_vol_0__roc10`: Train IC=+0.1467, Lock IC=+0.0283, Lock Sharpe=+1.0041
- `combo_min__roc60__roc10`: Train IC=+0.1297, Lock IC=+0.0274, Lock Sharpe=+0.7136
- `combo_sig_product__roc60__roc10`: Train IC=+0.1486, Lock IC=+0.0149, Lock Sharpe=+0.5659

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__sma50_dist`: Train IC=+0.1129, Lock IC=+0.0768, Lock Sharpe=+1.2013
- `combo_sig_product__iv_corridor_width__sma100_dist`: Train IC=+0.1155, Lock IC=+0.0663, Lock Sharpe=+1.0514
- `combo_sig_product__iv_corridor_width__roc60`: Train IC=+0.0946, Lock IC=+0.0603, Lock Sharpe=+0.9632
- `combo_rank_max__bar_vol_4__roc10`: Train IC=+0.1007, Lock IC=+0.0813, Lock Sharpe=+0.9300
- `combo_max__bar_vol_4__wavetrend_osc_day`: Train IC=+0.0830, Lock IC=+0.0958, Lock Sharpe=+0.8260

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 64.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.9364_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 321 | 30 | 63.3% | 0.0% | +0.0163 | -1.1550 |
| B2 Rolling Guard | 36 | 30 | 26.7% | 6.7% | -0.0014 | -0.7829 |
| BH-FDR Gate | 6 | 6 | 16.7% | 0.0% | -0.0367 | -1.6468 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__iv_envelope_deviation__yesterday_wavetrend_osc`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0844
- `combo_product__iv_envelope_deviation__wavetrend_osc_day`: Train IC=+0.0921, Lock IC=+0.0565, Lock Sharpe=+0.0844

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 28.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4128_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 278 | 30 | 76.7% | 60.0% | +0.0467 | +0.1306 |
| B2 Rolling Guard | 40 | 30 | 33.3% | 13.3% | +0.0115 | -0.1918 |
| BH-FDR Gate | 2 | 2 | 100.0% | 100.0% | +0.0198 | +0.3210 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1886, Lock IC=+0.0898, Lock Sharpe=+1.2870
- `limit_down_proximity_early`: Train IC=+0.1886, Lock IC=+0.0899, Lock Sharpe=+1.2870
- `combo_rank_max__bar_vol_4__mfi14`: Train IC=+0.1590, Lock IC=+0.0937, Lock Sharpe=+1.1906
- `sma20_dist`: Train IC=+0.1468, Lock IC=+0.1018, Lock Sharpe=+1.1639
- `star50_limit_proximity_early`: Train IC=+0.1271, Lock IC=+0.0603, Lock Sharpe=+0.8789

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `close_vs_open_range`: Train IC=+0.0193, Lock IC=+0.0427, Lock Sharpe=+1.1670
- `keltner_squeeze_width`: Train IC=+0.1163, Lock IC=+0.1636, Lock Sharpe=+1.1211
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0727, Lock Sharpe=+0.5902
- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0277, Lock Sharpe=+0.0353

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1148, Lock IC=+0.0302, Lock Sharpe=+0.5419
- `cvd_divergence_day`: Train IC=+0.1225, Lock IC=+0.0094, Lock Sharpe=+0.1001

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 69.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5482_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1802 | 30 | 100.0% | 60.0% | +0.0794 | -0.0896 |
| B2 Rolling Guard | 217 | 30 | 96.7% | 6.7% | +0.0382 | -0.8007 |
| BH-FDR Gate | 5 | 5 | 60.0% | 0.0% | -0.0027 | -1.3497 |
| B3 Composite Floor | 56 | 30 | 83.3% | 30.0% | +0.0264 | -0.6775 |
| B4 Correlation Gate | 521 | 30 | 100.0% | 10.0% | +0.0610 | -0.4942 |

**Admitted Pool Summary**: 29 features, False Positive Rate = 55.2% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0683, Mean Lock Sharpe = -0.1822

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`: Train IC=+0.2197, Lock IC=+0.0922, Lock Sharpe=+0.4695
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Lock Sharpe=+0.4340
- `combo_mean__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2188, Lock IC=+0.1124, Lock Sharpe=+0.3413
- `combo_z_sum__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2188, Lock IC=+0.1124, Lock Sharpe=+0.3413

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__first_bar_sentiment__early_late_momentum_divergence`: Train IC=+0.1855, Lock IC=+0.0659, Lock Sharpe=+0.3681
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2239, Lock IC=+0.0978, Lock Sharpe=+0.0194

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1847, Lock IC=+0.0017, Lock Sharpe=+0.3201
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.1599, Lock IC=+0.0747, Lock Sharpe=+0.2713
- `combo_tri_mean__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_z_mean__smooth_momentum_structure__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427
- `combo_tri_mean__smooth_momentum_structure__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.1694, Lock IC=+0.0740, Lock Sharpe=+0.2427

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2533, Lock IC=+0.0935, Lock Sharpe=+0.2501
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2533, Lock IC=+0.0935, Lock Sharpe=+0.2501
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__volatility_expansion_trend_vector`: Train IC=+0.2568, Lock IC=+0.0991, Lock Sharpe=+0.2078

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 59.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5074_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1228 | 30 | 83.3% | 66.7% | +0.0708 | +0.3640 |
| B2 Rolling Guard | 96 | 30 | 33.3% | 10.0% | -0.0230 | -0.7203 |
| BH-FDR Gate | 23 | 23 | 91.3% | 73.9% | +0.0383 | +0.4499 |

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
- `combo_sig_product__early_body_momentum__consecutive_higher_highs`: Train IC=+0.0742, Lock IC=+0.0383, Lock Sharpe=+0.9002
- `combo_sig_product__opening_momentum_score__consecutive_higher_highs`: Train IC=+0.0742, Lock IC=+0.0383, Lock Sharpe=+0.9002
- `combo_rank_min__shaved_bar_trend_conviction__trend_day_regime_conviction`: Train IC=+0.1061, Lock IC=+0.0275, Lock Sharpe=+0.8838

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 43.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.5074_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 369 | 30 | 56.7% | 33.3% | +0.0296 | -0.3004 |
| B2 Rolling Guard | 46 | 30 | 63.3% | 30.0% | +0.0057 | -0.3230 |
| BH-FDR Gate | 14 | 14 | 92.9% | 7.1% | +0.0489 | -0.8709 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.4723
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1458, Lock IC=+0.1141, Lock Sharpe=+0.4723
- `false_breakout_accumulation`: Train IC=+0.1489, Lock IC=+0.0315, Lock Sharpe=+0.4446
- `combo_mean__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.4139
- `combo_z_sum__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1584, Lock IC=+0.1016, Lock Sharpe=+0.4139

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `iv_diff_1d`: Train IC=+0.0334, Lock IC=+0.0868, Lock Sharpe=+0.9572
- `opening_direction_stability`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+0.5808
- `early_trend_hhi`: Train IC=+0.0000, Lock IC=+0.0338, Lock Sharpe=+0.5808
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0456, Lock Sharpe=+0.5463
- `impulse_bar_dominance`: Train IC=+0.0000, Lock IC=+0.0696, Lock Sharpe=+0.4248

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vwap_close_divergence_trend`: Train IC=+0.0805, Lock IC=+0.0323, Lock Sharpe=+0.2934

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 74.0% lock IC > 0, 51.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.0283_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 970 | 30 | 100.0% | 63.3% | +0.1014 | +0.1724 |
| B2 Rolling Guard | 145 | 30 | 93.3% | 60.0% | +0.0736 | +0.1597 |
| BH-FDR Gate | 3 | 3 | 100.0% | 33.3% | +0.0535 | +0.0233 |
| B3 Composite Floor | 121 | 30 | 100.0% | 96.7% | +0.1117 | +0.6261 |
| B4 Correlation Gate | 379 | 30 | 100.0% | 100.0% | +0.1261 | +1.0541 |

**Admitted Pool Summary**: 30 features, False Positive Rate = 26.7% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1108, Mean Lock Sharpe = +0.4436

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2018, Lock IC=+0.1126, Lock Sharpe=+1.5724
- `combo_clamp_diff__bar_body_rng_0__late_bar_momentum`: Train IC=+0.1793, Lock IC=+0.0890, Lock Sharpe=+1.4607
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.9095
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Lock Sharpe=+0.9095
- `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2346, Lock IC=+0.1159, Lock Sharpe=+0.7959

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Lock Sharpe=+1.0537
- `combo_clamp_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1528, Lock IC=+0.1099, Lock Sharpe=+0.9501
- `combo_rank_max__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1830, Lock IC=+0.0792, Lock Sharpe=+0.8691
- `combo_rank_max__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.1842, Lock IC=+0.1048, Lock Sharpe=+0.7777

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0396, Lock IC=+0.1184, Lock Sharpe=+0.1847

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__impulse_bar_dominance`: Train IC=+0.2725, Lock IC=+0.1182, Lock Sharpe=+1.4944
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__impulse_bar_dominance`: Train IC=+0.2628, Lock IC=+0.1068, Lock Sharpe=+1.3589
- `combo_min__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2227, Lock IC=+0.1193, Lock Sharpe=+1.3049
- `combo_tri_min__max_up_ret__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2417, Lock IC=+0.1107, Lock Sharpe=+1.2956
- `combo_tri_median__opening_drive_thrust_ratio__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2268, Lock IC=+0.1295, Lock Sharpe=+1.2146

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3122, Lock IC=+0.1361, Lock Sharpe=+1.6091
- `combo_tri_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.5184
- `combo_tri_z_mean__first_bar_sentiment__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Lock Sharpe=+1.5184
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Lock Sharpe=+1.4890
- `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3025, Lock IC=+0.1381, Lock Sharpe=+1.4675

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 66.0% lock IC > 0, 43.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2460_

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

_Null Baseline (un-gated candidate pool): 39.0% lock IC > 0, 24.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3723_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 256 | 30 | 76.7% | 46.7% | +0.0418 | -0.1211 |
| B2 Rolling Guard | 42 | 30 | 40.0% | 33.3% | +0.0131 | +0.0513 |
| BH-FDR Gate | 1 | 1 | 100.0% | 0.0% | +0.0926 | -0.0411 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `gap_pct`: Train IC=+0.0662, Lock IC=+0.1187, Lock Sharpe=+0.6266
- `combo_product__morning_volume_weighted_momentum__shaved_bar_trend_conviction`: Train IC=+0.1398, Lock IC=+0.0685, Lock Sharpe=+0.5945
- `vol_ratio_5_20`: Train IC=+0.0670, Lock IC=+0.0317, Lock Sharpe=+0.4589
- `combo_rel_diff__micro_gap_trend_continuation__shaved_bar_trend_conviction`: Train IC=+0.0946, Lock IC=+0.0112, Lock Sharpe=+0.4444
- `limit_down_proximity_early`: Train IC=+0.0645, Lock IC=+0.1323, Lock Sharpe=+0.4433

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.0168, Lock IC=+0.1035, Lock Sharpe=+1.0730
- `yesterday_close_position`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.8307
- `yesterday_day_close_pos`: Train IC=+0.0759, Lock IC=+0.1027, Lock Sharpe=+0.8307
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0397, Lock Sharpe=+0.7030
- `combo_rank_max__close_location_in_range_3d__yesterday_pm_return`: Train IC=+0.0241, Lock IC=+0.0817, Lock Sharpe=+0.5716

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 625 | +0.0246 | 80.0% |
| 0.45 | 0.20 | 616 | +0.0246 | 80.0% |
| 0.45 | 0.30 | 590 | +0.0246 | 80.0% |
| 0.45 | 0.40 | 518 | +0.0246 | 80.0% |
| 0.45 | 0.50 | 413 | +0.0246 | 80.0% |
| 0.50 | 0.15 | 622 | +0.0246 | 80.0% |
| 0.50 | 0.25 | 604 | +0.0246 | 80.0% |
| 0.50 | 0.35 | 556 | +0.0246 | 80.0% |
| 0.50 | 0.45 | 476 | +0.0246 | 80.0% |
| 0.55 | 0.10 | 619 | +0.0246 | 80.0% |
| 0.55 | 0.20 | 614 | +0.0246 | 80.0% |
| 0.55 | 0.30 | 590 | +0.0246 | 80.0% |
| 0.55 | 0.40 | 518 | +0.0246 | 80.0% |
| 0.55 | 0.50 | 413 | +0.0246 | 80.0% |
| 0.60 | 0.15 | 599 | +0.0246 | 80.0% |
| 0.60 | 0.25 | 592 | +0.0246 | 80.0% |
| 0.60 | 0.35 | 555 | +0.0246 | 80.0% |
| 0.60 | 0.45 | 476 | +0.0246 | 80.0% |
| 0.65 | 0.10 | 521 | +0.0246 | 80.0% |
| 0.65 | 0.20 | 521 | +0.0246 | 80.0% |
| 0.65 | 0.30 | 519 | +0.0246 | 80.0% |
| 0.65 | 0.40 | 499 | +0.0246 | 80.0% |
| 0.65 | 0.50 | 413 | +0.0246 | 80.0% |
| 0.70 | 0.15 | 383 | +0.0246 | 80.0% |
| 0.70 | 0.25 | 383 | +0.0246 | 80.0% |
| 0.70 | 0.35 | 383 | +0.0246 | 80.0% |
| 0.70 | 0.45 | 379 | +0.0246 | 80.0% |
| 0.75 | 0.10 | 154 | +0.0117 | 60.0% |
| 0.75 | 0.20 | 154 | +0.0117 | 60.0% |
| 0.75 | 0.30 | 154 | +0.0117 | 60.0% |
| 0.75 | 0.40 | 154 | +0.0117 | 60.0% |
| 0.75 | 0.50 | 154 | +0.0117 | 60.0% |
| 0.80 | 0.15 | 19 | -0.0192 | 20.0% |
| 0.80 | 0.25 | 19 | -0.0192 | 20.0% |
| 0.80 | 0.35 | 19 | -0.0192 | 20.0% |
| 0.80 | 0.45 | 19 | -0.0192 | 20.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 625 candidates, mean lock IC=+0.0246, 80.0% positive

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
| 0.45 | 0.10 | 396 | +0.0519 | 100.0% |
| 0.45 | 0.20 | 381 | +0.0519 | 100.0% |
| 0.45 | 0.30 | 355 | +0.0519 | 100.0% |
| 0.45 | 0.40 | 338 | +0.0519 | 100.0% |
| 0.45 | 0.50 | 319 | +0.0519 | 100.0% |
| 0.50 | 0.15 | 395 | +0.0519 | 100.0% |
| 0.50 | 0.25 | 371 | +0.0519 | 100.0% |
| 0.50 | 0.35 | 349 | +0.0519 | 100.0% |
| 0.50 | 0.45 | 331 | +0.0519 | 100.0% |
| 0.55 | 0.10 | 391 | +0.0519 | 100.0% |
| 0.55 | 0.20 | 379 | +0.0519 | 100.0% |
| 0.55 | 0.30 | 355 | +0.0519 | 100.0% |
| 0.55 | 0.40 | 338 | +0.0519 | 100.0% |
| 0.55 | 0.50 | 319 | +0.0519 | 100.0% |
| 0.60 | 0.15 | 362 | +0.0519 | 100.0% |
| 0.60 | 0.25 | 360 | +0.0519 | 100.0% |
| 0.60 | 0.35 | 348 | +0.0519 | 100.0% |
| 0.60 | 0.45 | 331 | +0.0519 | 100.0% |
| 0.65 | 0.10 | 342 | +0.0519 | 100.0% |
| 0.65 | 0.20 | 342 | +0.0519 | 100.0% |
| 0.65 | 0.30 | 340 | +0.0519 | 100.0% |
| 0.65 | 0.40 | 335 | +0.0519 | 100.0% |
| 0.65 | 0.50 | 319 | +0.0519 | 100.0% |
| 0.70 | 0.15 | 301 | +0.0519 | 100.0% |
| 0.70 | 0.25 | 301 | +0.0519 | 100.0% |
| 0.70 | 0.35 | 301 | +0.0519 | 100.0% |
| 0.70 | 0.45 | 301 | +0.0519 | 100.0% |
| 0.75 | 0.10 | 236 | +0.0508 | 100.0% |
| 0.75 | 0.20 | 236 | +0.0508 | 100.0% |
| 0.75 | 0.30 | 236 | +0.0508 | 100.0% |
| 0.75 | 0.40 | 236 | +0.0508 | 100.0% |
| 0.75 | 0.50 | 236 | +0.0508 | 100.0% |
| 0.80 | 0.15 | 189 | +0.0373 | 90.0% |
| 0.80 | 0.25 | 189 | +0.0373 | 90.0% |
| 0.80 | 0.35 | 189 | +0.0373 | 90.0% |
| 0.80 | 0.45 | 189 | +0.0373 | 90.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 396 candidates, mean lock IC=+0.0519, 100.0% positive

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
| 0.45 | 0.10 | 1404 | +0.0547 | 100.0% |
| 0.45 | 0.20 | 1385 | +0.0547 | 100.0% |
| 0.45 | 0.30 | 1313 | +0.0547 | 100.0% |
| 0.45 | 0.40 | 1220 | +0.0547 | 100.0% |
| 0.45 | 0.50 | 1008 | +0.0547 | 100.0% |
| 0.50 | 0.15 | 1395 | +0.0547 | 100.0% |
| 0.50 | 0.25 | 1350 | +0.0547 | 100.0% |
| 0.50 | 0.35 | 1265 | +0.0547 | 100.0% |
| 0.50 | 0.45 | 1095 | +0.0547 | 100.0% |
| 0.55 | 0.10 | 1399 | +0.0547 | 100.0% |
| 0.55 | 0.20 | 1384 | +0.0547 | 100.0% |
| 0.55 | 0.30 | 1313 | +0.0547 | 100.0% |
| 0.55 | 0.40 | 1220 | +0.0547 | 100.0% |
| 0.55 | 0.50 | 1008 | +0.0547 | 100.0% |
| 0.60 | 0.15 | 1348 | +0.0547 | 100.0% |
| 0.60 | 0.25 | 1332 | +0.0547 | 100.0% |
| 0.60 | 0.35 | 1261 | +0.0547 | 100.0% |
| 0.60 | 0.45 | 1095 | +0.0547 | 100.0% |
| 0.65 | 0.10 | 1210 | +0.0547 | 100.0% |
| 0.65 | 0.20 | 1210 | +0.0547 | 100.0% |
| 0.65 | 0.30 | 1210 | +0.0547 | 100.0% |
| 0.65 | 0.40 | 1182 | +0.0547 | 100.0% |
| 0.65 | 0.50 | 1008 | +0.0547 | 100.0% |
| 0.70 | 0.15 | 912 | +0.0547 | 100.0% |
| 0.70 | 0.25 | 912 | +0.0547 | 100.0% |
| 0.70 | 0.35 | 912 | +0.0547 | 100.0% |
| 0.70 | 0.45 | 911 | +0.0547 | 100.0% |
| 0.75 | 0.10 | 486 | +0.0547 | 100.0% |
| 0.75 | 0.20 | 486 | +0.0547 | 100.0% |
| 0.75 | 0.30 | 486 | +0.0547 | 100.0% |
| 0.75 | 0.40 | 486 | +0.0547 | 100.0% |
| 0.75 | 0.50 | 486 | +0.0547 | 100.0% |
| 0.80 | 0.15 | 193 | +0.0547 | 100.0% |
| 0.80 | 0.25 | 193 | +0.0547 | 100.0% |
| 0.80 | 0.35 | 193 | +0.0547 | 100.0% |
| 0.80 | 0.45 | 193 | +0.0547 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1404 candidates, mean lock IC=+0.0547, 100.0% positive

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
| 0.45 | 0.10 | 715 | +0.1241 | 100.0% |
| 0.45 | 0.20 | 702 | +0.1241 | 100.0% |
| 0.45 | 0.30 | 643 | +0.1241 | 100.0% |
| 0.45 | 0.40 | 579 | +0.1241 | 100.0% |
| 0.45 | 0.50 | 470 | +0.1241 | 100.0% |
| 0.50 | 0.15 | 710 | +0.1241 | 100.0% |
| 0.50 | 0.25 | 669 | +0.1241 | 100.0% |
| 0.50 | 0.35 | 621 | +0.1241 | 100.0% |
| 0.50 | 0.45 | 532 | +0.1241 | 100.0% |
| 0.55 | 0.10 | 709 | +0.1241 | 100.0% |
| 0.55 | 0.20 | 700 | +0.1241 | 100.0% |
| 0.55 | 0.30 | 643 | +0.1241 | 100.0% |
| 0.55 | 0.40 | 579 | +0.1241 | 100.0% |
| 0.55 | 0.50 | 470 | +0.1241 | 100.0% |
| 0.60 | 0.15 | 656 | +0.1241 | 100.0% |
| 0.60 | 0.25 | 648 | +0.1241 | 100.0% |
| 0.60 | 0.35 | 620 | +0.1241 | 100.0% |
| 0.60 | 0.45 | 532 | +0.1241 | 100.0% |
| 0.65 | 0.10 | 588 | +0.1241 | 100.0% |
| 0.65 | 0.20 | 588 | +0.1241 | 100.0% |
| 0.65 | 0.30 | 588 | +0.1241 | 100.0% |
| 0.65 | 0.40 | 569 | +0.1241 | 100.0% |
| 0.65 | 0.50 | 469 | +0.1241 | 100.0% |
| 0.70 | 0.15 | 418 | +0.1241 | 100.0% |
| 0.70 | 0.25 | 418 | +0.1241 | 100.0% |
| 0.70 | 0.35 | 418 | +0.1241 | 100.0% |
| 0.70 | 0.45 | 418 | +0.1241 | 100.0% |
| 0.75 | 0.10 | 222 | +0.1241 | 100.0% |
| 0.75 | 0.20 | 222 | +0.1241 | 100.0% |
| 0.75 | 0.30 | 222 | +0.1241 | 100.0% |
| 0.75 | 0.40 | 222 | +0.1241 | 100.0% |
| 0.75 | 0.50 | 222 | +0.1241 | 100.0% |
| 0.80 | 0.15 | 66 | +0.1241 | 100.0% |
| 0.80 | 0.25 | 66 | +0.1241 | 100.0% |
| 0.80 | 0.35 | 66 | +0.1241 | 100.0% |
| 0.80 | 0.45 | 66 | +0.1241 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 715 candidates, mean lock IC=+0.1241, 100.0% positive

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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | +0.1131 | +0.0000 | +0.0547 | 0.48x | 2016-08-24 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1067 | +0.0000 | +0.0007 | 0.01x | 2015-02-06 |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | +0.1108 | +0.0000 | -0.0022 | -0.02x | 2017-09-06 |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | +0.1253 | +0.0000 | +0.0164 | 0.13x | 2016-08-24 |
| `combo_max__first_bar_return__volume_surge_direction` | +0.0802 | +0.0000 | +0.0104 | 0.13x | 2013-08-21 |
| `combo_tri_max__first_bar_sentiment__volume_weighted_price_position__bar_body_rng_0` | +0.0882 | +0.0000 | +0.0241 | 0.27x | 2010-12-14 |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | +0.0994 | +0.0000 | +0.0303 | 0.30x | 2015-03-16 |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | +0.0909 | +0.0000 | +0.0753 | 0.83x | 2016-08-24 |
| `combo_tri_sig_max__volume_weighted_momentum_acceleration__max_up_ret__first_bar_sentiment` | +0.0339 | +0.0000 | -0.0760 | -2.24x | 2012-07-05 |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | +0.0366 | +0.0000 | -0.0133 | -0.36x | 2010-10-15 |
| `combo_min__bar_body_rng_0__demark_setup_reversal_early` | +0.0200 | +0.0000 | -0.0600 | -3.00x | 2010-10-15 |
| `combo_abs_diff__max_up_ret__first_bar_sentiment` | +0.0473 | +0.0000 | +0.0103 | 0.22x | 2011-12-23 |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | +0.0297 | +0.0000 | +0.0575 | 1.94x | 2012-08-03 |
| `combo_ratio__first_bar_return__volume_surge_direction` | +0.0811 | +0.0000 | -0.0091 | -0.11x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_mean__close_vs_open_range__bar_ret_0` | +0.1641 | +0.0000 | +0.0469 | 0.29x | No decay |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.1790 | +0.0000 | +0.0427 | 0.24x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | +0.1908 | +0.0000 | +0.0883 | 0.46x | No decay |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | +0.1841 | +0.0000 | +0.0337 | 0.18x | 2021-07-28 |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | +0.1545 | +0.0000 | +0.0817 | 0.53x | 2016-09-26 |
| `combo_max__max_up_ret__first_bar_sentiment` | +0.1639 | +0.0000 | +0.0247 | 0.15x | 2017-05-09 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1607 | +0.0000 | +0.0946 | 0.59x | No decay |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | +0.1377 | +0.0000 | +0.1138 | 0.83x | 2011-12-23 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1501 | +0.0000 | +0.0661 | 0.44x | No decay |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | +0.1085 | +0.0000 | +0.1335 | 1.23x | 2016-06-27 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +0.1392 | +0.0000 | +0.1034 | 0.74x | 2011-09-20 |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | +0.0594 | +0.0000 | +0.0335 | 0.56x | 2010-10-15 |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0` | +0.1344 | +0.0000 | +0.1191 | 0.89x | 2011-10-18 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1620 | +0.0000 | +0.1337 | 0.82x | 2017-02-27 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1644 | +0.0000 | +0.1135 | 0.69x | 2016-12-21 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1551 | +0.0000 | +0.1296 | 0.84x | 2011-10-18 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1513 | +0.0000 | +0.1258 | 0.83x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1454 | +0.0000 | +0.1073 | 0.74x | 2011-11-16 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1405 | +0.0000 | +0.1514 | 1.08x | 2016-09-14 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1105 | +0.0000 | +0.1100 | 1.00x | 2011-10-18 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0944 | +0.0000 | +0.1079 | 1.14x | 2011-10-18 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1317 | +0.0000 | +0.1308 | 0.99x | 2011-10-18 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1219 | +0.0000 | +0.1155 | 0.95x | 2017-01-20 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1172 | +0.0000 | +0.0813 | 0.69x | 2016-10-24 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0604 | +0.0000 | -0.0153 | -0.25x | 2012-01-17 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — 7-Year Jackknife Sign Stability too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 19.0%, mean lock Sharpe=-0.3449). Consider relaxing this gate.
2. **300ETF `single` — B4 Correlation Gate too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 19.0%, mean lock Sharpe=-0.5161). Consider relaxing this gate.
3. **300ETF `single` — Admission too loose**: 92% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
4. **300ETF `long` — 7-Year Jackknife Sign Stability too strict**: 20.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 6.0%, mean lock Sharpe=-0.5144). Consider relaxing this gate.
5. **300ETF `short` — BH-FDR Gate too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.1920). Consider relaxing this gate.
6. **50ETF `single` — 7-Year Jackknife Sign Stability too strict**: 56.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.1812). Consider relaxing this gate.
7. **50ETF `single` — B2 Rolling Guard too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 30.0%, mean lock Sharpe=+0.0118). Consider relaxing this gate.
8. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.1306). Consider relaxing this gate.
9. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.0896). Consider relaxing this gate.
10. **500ETF `single` — Admission too loose**: 55% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
11. **500ETF `long` — 7-Year Jackknife Sign Stability too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.3640). Consider relaxing this gate.
12. **500ETF `long` — BH-FDR Gate too strict**: 73.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=+0.4499). Consider relaxing this gate.
13. **500ETF `short` — 7-Year Jackknife Sign Stability too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3004). Consider relaxing this gate.
14. **500ETF `short` — B2 Rolling Guard too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3230). Consider relaxing this gate.
15. **159915ETF `single` — B3 Composite Floor too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+0.6261). Consider relaxing this gate.
16. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 51.0%, mean lock Sharpe=+1.0541). Consider relaxing this gate.
17. **159915ETF `long` — BH-FDR Gate too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 43.0%, mean lock Sharpe=+0.8546). Consider relaxing this gate.
18. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 46.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 24.0%, mean lock Sharpe=-0.1211). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
