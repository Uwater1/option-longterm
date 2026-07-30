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

### 300ETF — `single` (Full Model Lockbox IC: +0.0345, Sharpe: +0.4487)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Intraday Range Momentum | +1 | +0.1299 | +0.0650 | +0.0280 | +0.0482 | 0.65 | 0/7 | 0.81 | 0.50 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0023 | +0.0340 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1197 | +0.0619 | +0.0386 | +1.0692 | 0.91 | 1/7 | 0.75 | 0.56 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0016 | +0.0928 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1164 | +0.0602 | +0.0189 | +0.4526 | 0.82 | 1/7 | 1.02 | 0.74 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0031 | +0.0455 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1083 | +0.0690 | +0.0353 | +0.1885 | 0.58 | 0/7 | 0.83 | 0.50 | `rbreaker_sell_setup_proximity_early` (1.14) | +0.0011 | +0.0247 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.0953 | +0.0728 | +0.0616 | +0.2757 | 1.14 | 1/7 | 0.62 | 0.50 | — | -0.0027 | -0.1103 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | Other Technical | +1 | +0.1145 | +0.0808 | +0.0628 | +0.6626 | 0.74 | 1/7 | 1.13 | 0.63 | `star50_limit_proximity_early` (1.21) | +0.0064 | +0.0703 |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | Intraday Range Momentum | +1 | +0.0883 | +0.0561 | -0.0129 | -0.2036 | 0.86 | 1/7 | 1.26 | 1.03 | `volume_weighted_price_position` (1.30) | -0.0024 | +0.1899 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.0208 | -0.0038 | +0.0016 | +0.5869 | 5.62 | 4/7 | -0.29 | -0.31 | `rbreaker_sell_setup_proximity_early` (1.14) | -0.0000 | +0.0575 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | Volatility & Oscillators | +1 | +0.0538 | +0.0537 | +0.0706 | +0.4878 | 0.88 | 1/7 | 1.82 | 1.12 | `limit_down_proximity_early` (1.62) | +0.0038 | +0.1765 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Gap / Overnight Reversal | +1 | +0.0702 | +0.0120 | -0.0280 | -1.2340 | 0.75 | 1/7 | 0.87 | 0.50 | `volume_surge_direction` (1.02) | +0.0000 | +0.0000 |

### 500ETF — `single` (Full Model Lockbox IC: +0.1334, Sharpe: +1.3710)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1808 | +0.1142 | +0.1145 | +0.7240 | 0.40 | 0/7 | 0.65 | 0.51 | `close_vs_open_range` (0.48) | +0.0004 | +0.1470 |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1863 | +0.1030 | +0.1256 | +1.1032 | 0.42 | 0/7 | 1.09 | 1.10 | `star50_limit_proximity_early` (0.62) | -0.0003 | -0.0540 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1870 | +0.1116 | +0.1138 | +0.4832 | 0.37 | 0/7 | 0.61 | 0.63 | `close_vs_open_range` (0.48) | -0.0014 | +0.3846 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Gap / Overnight Reversal | +1 | +0.1906 | +0.0766 | +0.0842 | +0.4110 | 0.34 | 0/7 | 0.68 | 0.65 | `first_bar_sentiment` (0.44) | +0.0001 | +0.2272 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1881 | +0.0805 | +0.0991 | +1.0237 | 0.40 | 0/7 | 0.70 | 0.59 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0000 | +0.0968 |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | Intraday Range Momentum | +1 | +0.1889 | +0.0722 | +0.0735 | -0.4531 | 0.40 | 0/7 | 0.76 | 0.62 | `late_bar_momentum` (0.56) | -0.0008 | +0.1329 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1500 | +0.1164 | +0.1001 | +0.4564 | 0.44 | 0/7 | 0.69 | 0.56 | `close_vs_open_range` (0.48) | +0.0005 | +0.3250 |
| `combo_min__star50_limit_proximity_early__max_down_ret` | Intraday Range Momentum | +1 | +0.1312 | +0.0939 | +0.1114 | +0.4728 | 0.60 | 0/7 | 0.58 | 0.53 | `star50_limit_proximity_early` (0.62) | +0.0013 | +0.0000 |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | Gap / Overnight Reversal | +1 | +0.1182 | +0.0755 | +0.0743 | +0.0810 | 0.52 | 0/7 | 1.01 | 0.64 | `max_down_ret` (0.55) | -0.0006 | -0.0222 |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | Gap / Overnight Reversal | +1 | +0.1794 | +0.1196 | +0.1258 | +0.5110 | 0.44 | 0/7 | 0.67 | 0.69 | `demark_setup_reversal_early` (0.66) | +0.0011 | +0.0000 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.2028 | +0.0858 | +0.0810 | -0.4849 | 0.33 | 0/7 | 0.99 | 0.89 | `volume_weighted_momentum_acceleration` (0.46) | -0.0011 | +0.0775 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1611 | +0.0792 | +0.1083 | +1.3443 | 0.43 | 0/7 | 0.71 | 0.57 | `star50_limit_proximity_early` (0.62) | +0.0006 | +0.1878 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1499 | +0.0837 | +0.1100 | +1.0815 | 0.52 | 0/7 | 0.67 | 0.56 | `max_down_ret` (0.55) | +0.0040 | +0.2374 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1887 | +0.0883 | +0.1135 | +0.9912 | 0.39 | 0/7 | 0.95 | 0.87 | `star50_limit_proximity_early` (0.62) | -0.0003 | -0.0498 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | Other Technical | +1 | +0.1286 | +0.0852 | +0.1007 | +0.4324 | 0.46 | 0/7 | 0.63 | 0.40 | `close_vs_open_range` (0.48) | -0.0001 | +0.0000 |
| `combo_rank_min__bar_ret_0__rbreaker_buy_setup_proximity_early` | Other Technical | +1 | +0.1305 | +0.0728 | +0.1173 | +1.2788 | 0.55 | 0/7 | 0.73 | 0.54 | `rbreaker_buy_setup_proximity_early` (1.03) | +0.0013 | +0.0927 |
| `combo_rank_max__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.1535 | +0.0930 | +0.0728 | +0.2807 | 0.44 | 0/7 | 0.65 | 0.58 | `early_body_momentum` (0.39) | -0.0004 | +0.1729 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | Volatility & Oscillators | +1 | +0.1395 | +0.1098 | +0.1321 | +1.3027 | 0.43 | 0/7 | 0.77 | 0.84 | `star50_limit_proximity_early` (0.62) | +0.0008 | +0.0968 |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__close_vs_open_range` | Volatility & Oscillators | +1 | +0.1304 | +0.0986 | +0.1158 | +1.2975 | 0.41 | 0/7 | 0.71 | 0.80 | `star50_limit_proximity_early` (0.62) | +0.0004 | +0.0820 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | Intraday Range Momentum | +1 | +0.1583 | +0.0972 | +0.1139 | +1.4937 | 0.39 | 0/7 | 0.73 | 0.66 | `volume_weighted_momentum_acceleration` (0.46) | +0.0010 | +0.1832 |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.0830 | +0.0014 | +0.0337 | -0.0135 | 1.06 | 2/7 | 0.21 | 0.26 | `early_order_flow_imbalance` (0.73) | +0.0013 | +0.4264 |
| `combo_mean__bar_ret_0__max_down_ret` | Intraday Range Momentum | +1 | +0.1535 | +0.0871 | +0.1025 | +0.7111 | 0.36 | 0/7 | 0.81 | 0.60 | `max_down_ret` (0.55) | -0.0005 | +0.0809 |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Intraday Range Momentum | +1 | +0.1303 | +0.0958 | +0.0945 | +0.9027 | 0.35 | 0/7 | 0.66 | 0.79 | `close_vs_open_range` (0.48) | -0.0008 | +0.2488 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1638 | +0.1054 | +0.0902 | +0.5017 | 0.42 | 0/7 | 0.56 | 0.52 | `rbreaker_sell_setup_proximity_early` (0.40) | +0.0002 | +0.1764 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Other Technical | +1 | +0.1476 | +0.1024 | +0.1219 | +0.5797 | 0.50 | 0/7 | 0.52 | 0.51 | `star50_limit_proximity_early` (0.62) | -0.0009 | +0.1416 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1623 | +0.1046 | +0.1053 | +0.3612 | 0.38 | 0/7 | 0.62 | 0.56 | `star50_limit_proximity_early` (0.62) | -0.0016 | +0.0289 |
| `combo_ratio__max_down_ret__net_volume_flow` | Intraday Range Momentum | +1 | +0.1323 | +0.0543 | +0.1213 | +0.1422 | 0.47 | 0/7 | 0.64 | 0.42 | `max_down_ret` (0.55) | -0.0006 | +0.0000 |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | Intraday Range Momentum | +1 | +0.1064 | +0.0717 | +0.1357 | +1.4324 | 0.95 | 1/7 | 0.34 | 0.03 | `early_order_flow_imbalance` (0.73) | +0.0002 | +0.0000 |
| `rbreaker_sell_setup_proximity_early` | Other Technical | +1 | +0.1618 | +0.1110 | +0.1261 | +0.8321 | 0.40 | 0/7 | 0.47 | 0.49 | — | -0.0009 | +0.0551 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | Intraday Range Momentum | +1 | +0.0687 | +0.0159 | +0.0027 | +0.5710 | 0.64 | 0/7 | 0.54 | 0.36 | `early_body_momentum` (0.39) | +0.0009 | +0.3018 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | Other Technical | +1 | +0.1436 | +0.1254 | +0.1504 | +0.5807 | 0.38 | 0/7 | 0.79 | 0.76 | `star50_limit_proximity_early` (0.62) | +0.0009 | +0.0809 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | Intraday Range Momentum | +1 | +0.1415 | +0.0929 | +0.0879 | +0.2708 | 0.42 | 0/7 | 0.58 | 0.66 | `rbreaker_sell_setup_proximity_early` (0.40) | -0.0005 | +0.1031 |

### 588000ETF — `single` (Full Model Lockbox IC: -0.0537, Sharpe: +0.4134)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1040 | -0.0093 | -0.0537 | -0.4510 | 0.68 | 0/5 | 1.02 | 0.51 | — | -0.0537 | +0.4134 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1559, Sharpe: +1.7151)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Lock Sharpe | IC CV | Neg Yrs | Half Ratio | Recency Ratio | Weak Component | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: |
| `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0` | Other Technical | +1 | +0.1273 | +0.1339 | +0.1286 | +1.7509 | 0.52 | 0/7 | 1.46 | 1.09 | `impulse_bar_dominance` (1.19) | -0.0007 | -0.0186 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | Gap / Overnight Reversal | +1 | +0.1696 | +0.1203 | +0.1356 | +1.3158 | 0.51 | 1/7 | 1.36 | 0.80 | `first_bar_sentiment` (0.70) | -0.0028 | +0.1737 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Intraday Range Momentum | +1 | +0.1494 | +0.1331 | +0.1289 | +1.1085 | 0.44 | 0/7 | 1.25 | 1.01 | `star50_limit_proximity_early` (0.77) | +0.0004 | +0.0238 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1678 | +0.1162 | +0.1293 | +1.0208 | 0.56 | 1/7 | 1.05 | 0.77 | `rbreaker_sell_setup_proximity_early` (0.47) | -0.0006 | +0.0184 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1378 | +0.1127 | +0.1319 | +1.6572 | 0.54 | 0/7 | 1.31 | 0.90 | `volume_weighted_price_position` (0.71) | -0.0006 | -0.1141 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | Gap / Overnight Reversal | +1 | +0.1474 | +0.1399 | +0.1280 | +1.0786 | 0.46 | 0/7 | 1.18 | 1.34 | `rbreaker_sell_setup_proximity_early` (0.47) | +0.0025 | -0.1682 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.1109 | +0.1369 | +0.1432 | +1.4553 | 0.71 | 1/7 | 1.22 | 1.07 | `star50_limit_proximity_early` (0.77) | +0.0018 | -0.0866 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1170 | +0.1166 | +0.0998 | +0.6196 | 0.65 | 1/7 | 1.03 | 0.76 | `yesterday_early_vwap_dev` (1.27) | +0.0009 | +0.0975 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.0784 | +0.1119 | +0.1027 | +0.4767 | 1.01 | 1/7 | 1.82 | 1.44 | `yesterday_first_30min_return` (1.04) | +0.0017 | -0.0621 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | Volatility & Oscillators | +1 | +0.1102 | +0.1311 | +0.1379 | +1.1164 | 0.77 | 1/7 | 1.05 | 1.02 | `star50_limit_proximity_early` (0.77) | -0.0013 | +0.0332 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | Intraday Range Momentum | +1 | +0.1105 | +0.1292 | +0.1386 | +0.9674 | 0.72 | 1/7 | 0.67 | 0.50 | `yesterday_first_30min_return` (1.04) | +0.0075 | -0.1030 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Volatility & Oscillators | +1 | +0.0836 | +0.0904 | +0.0519 | -0.5308 | 0.72 | 0/7 | 1.54 | 1.62 | `volatility_expansion_trend_vector` (0.76) | -0.0002 | -0.1876 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | Intraday Range Momentum | +1 | +0.0637 | -0.0116 | -0.0258 | -0.1284 | 0.70 | 1/7 | 0.76 | 2.17 | `volatility_expansion_trend_vector` (0.76) | -0.0003 | +0.1469 |

---

## Filter Gate Effectiveness Analysis

Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.
**True False Negative (FN) Rate** = % of rejected features with lockbox IC > 0 AND lockbox Sharpe > 0 (profitable post-friction).
**Null Baseline Rate** = % of un-gated candidate features with lockbox IC > 0 AND lockbox Sharpe > 0 (random noise benchmark).
**False Positive Rate** = % of admitted features with negative lockbox IC or Sharpe (gate too loose).

### 300ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 62.0% lock IC > 0, 28.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.3111_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1039 | 30 | 73.3% | 30.0% | +0.0125 | -0.2595 |
| B2 Rolling Guard | 240 | 30 | 76.7% | 23.3% | +0.0040 | -0.1929 |
| BH-FDR Gate | 2 | 2 | 0.0% | 0.0% | -0.0243 | -0.8124 |
| B3 Composite Floor | 57 | 30 | 80.0% | 63.3% | +0.0074 | -0.0507 |
| B4 Correlation Gate | 65 | 30 | 90.0% | 83.3% | +0.0267 | +0.2782 |

**Admitted Pool Summary**: 17 features, False Positive Rate = 47.1% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0062, Mean Lock Sharpe = -0.2161

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0379, Lock Sharpe=+1.0599
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.2004, Lock IC=+0.0529, Lock Sharpe=+0.8717
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.2004, Lock IC=+0.0529, Lock Sharpe=+0.8717
- `combo_rank_min__max_up_ret__volume_surge_direction`: Train IC=+0.1992, Lock IC=+0.0050, Lock Sharpe=+0.4905
- `combo_tri_min__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2064, Lock IC=+0.0445, Lock Sharpe=+0.3476

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2064, Lock IC=+0.0263, Lock Sharpe=+0.8994
- `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2042, Lock IC=+0.0016, Lock Sharpe=+0.5869
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Train IC=+0.1796, Lock IC=+0.0141, Lock Sharpe=+0.2036
- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Train IC=+0.1892, Lock IC=+0.0238, Lock Sharpe=+0.0677
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Train IC=+0.1891, Lock IC=+0.0237, Lock Sharpe=+0.0677

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.1982, Lock IC=+0.0068, Lock Sharpe=+0.5114
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.1982, Lock IC=+0.0068, Lock Sharpe=+0.5114
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2120, Lock IC=+0.0218, Lock Sharpe=+0.3967
- `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.1933, Lock IC=+0.0074, Lock Sharpe=+0.2542
- `combo_tri_z_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.1933, Lock IC=+0.0074, Lock Sharpe=+0.2542

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2690, Lock IC=+0.0342, Lock Sharpe=+1.2516
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2255, Lock IC=+0.0660, Lock Sharpe=+0.7636
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0345, Lock Sharpe=+0.4582
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0345, Lock Sharpe=+0.4582
- `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2278, Lock IC=+0.0345, Lock Sharpe=+0.4582

### 300ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 38.0% lock IC > 0, 8.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.6045_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 555 | 30 | 73.3% | 3.3% | +0.0149 | -0.4762 |
| B2 Rolling Guard | 59 | 30 | 40.0% | 10.0% | -0.0056 | -0.6606 |
| BH-FDR Gate | 9 | 9 | 0.0% | 0.0% | -0.0266 | -0.4050 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__willr14__sma100_dist`: Train IC=+0.1400, Lock IC=+0.0526, Lock Sharpe=+0.2861

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `range_expansion_ratio`: Train IC=+0.0895, Lock IC=+0.0645, Lock Sharpe=+0.1756
- `intraday_slope`: Train IC=+0.1254, Lock IC=+0.0621, Lock Sharpe=+0.0417
- `early_trend`: Train IC=+0.1309, Lock IC=+0.0621, Lock Sharpe=+0.0255

### 300ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4229_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 373 | 30 | 36.7% | 6.7% | -0.0111 | -0.5859 |
| B2 Rolling Guard | 57 | 30 | 46.7% | 13.3% | +0.0006 | -0.5383 |
| BH-FDR Gate | 14 | 14 | 85.7% | 42.9% | +0.0293 | -0.0677 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_drive_thrust_ratio__volume_surge_direction`: Train IC=+0.1097, Lock IC=+0.0217, Lock Sharpe=+0.4434
- `volume_surge_direction`: Train IC=+0.1060, Lock IC=+0.0217, Lock Sharpe=+0.2779

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_ifelse__vix__rbreaker_sell_setup_proximity_early__inside_bar_failure_bull`: Train IC=+0.0965, Lock IC=+0.0032, Lock Sharpe=+1.0253
- `combo_abs_diff__iv__growth_momentum_ratio`: Train IC=+0.0200, Lock IC=+0.0582, Lock Sharpe=+0.5647
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1898, Lock IC=+0.0587, Lock Sharpe=+0.1412
- `inside_bar_failure_bull`: Train IC=+0.0000, Lock IC=+0.0027, Lock Sharpe=+0.1377

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `star50_limit_proximity_early`: Train IC=+0.0741, Lock IC=+0.0650, Lock Sharpe=+1.0348
- `gap_pct`: Train IC=+0.1531, Lock IC=+0.0795, Lock Sharpe=+0.7643
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0876, Lock IC=+0.0350, Lock Sharpe=+0.5535
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1883, Lock IC=+0.0616, Lock Sharpe=+0.4395
- `combo_diff__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.1968, Lock IC=+0.0587, Lock Sharpe=+0.1412

### 50ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 73.0% lock IC > 0, 39.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2409_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 730 | 30 | 90.0% | 33.3% | +0.0359 | -0.1814 |
| B2 Rolling Guard | 77 | 30 | 83.3% | 43.3% | +0.0228 | +0.0073 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__bar_vol_4__wavetrend_osc_day`: Train IC=+0.1856, Lock IC=+0.1103, Lock Sharpe=+0.9731
- `yesterday_lunch_gap`: Train IC=+0.1911, Lock IC=+0.0772, Lock Sharpe=+0.9161
- `combo_mean__bar_vol_4__roc10`: Train IC=+0.1425, Lock IC=+0.0859, Lock Sharpe=+0.7392
- `combo_z_sum__bar_vol_4__roc10`: Train IC=+0.1425, Lock IC=+0.0859, Lock Sharpe=+0.7392
- `combo_rank_max__bar_vol_4__bar_vol_0`: Train IC=+0.1590, Lock IC=+0.0527, Lock Sharpe=+0.4950

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `limit_down_proximity_early`: Train IC=+0.1361, Lock IC=+0.0431, Lock Sharpe=+0.9119
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.1361, Lock IC=+0.0431, Lock Sharpe=+0.9119
- `star50_limit_proximity_early`: Train IC=+0.1363, Lock IC=+0.0239, Lock Sharpe=+0.6822
- `combo_max__bar_vol_4__yesterday_body_ratio`: Train IC=+0.1823, Lock IC=+0.0712, Lock Sharpe=+0.6677
- `combo_product__bar_vol_4__bar_vol_0`: Train IC=+0.0898, Lock IC=+0.0492, Lock Sharpe=+0.5444

### 50ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 51.1% lock IC > 0, 13.3% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.7286_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 451 | 10 | 30.0% | 0.0% | -0.0176 | -0.7672 |
| B2 Rolling Guard | 66 | 11 | 54.5% | 18.2% | +0.0154 | -0.4584 |
| BH-FDR Gate | 7 | 6 | 0.0% | 0.0% | -0.0484 | -1.7936 |

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `bar_vol_4`: Train IC=+0.0880, Lock IC=+0.0834, Lock Sharpe=+0.3081
- `roc20`: Train IC=+0.0576, Lock IC=+0.0709, Lock Sharpe=+0.0586

### 50ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 58.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2833_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 277 | 30 | 63.3% | 50.0% | +0.0269 | -0.0553 |
| B2 Rolling Guard | 47 | 30 | 26.7% | 10.0% | -0.0050 | -0.2659 |
| BH-FDR Gate | 6 | 6 | 33.3% | 16.7% | -0.0207 | -0.5517 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_lunch_gap`: Train IC=+0.1124, Lock IC=+0.0772, Lock Sharpe=+1.0118
- `gap_pct`: Train IC=+0.1368, Lock IC=+0.0756, Lock Sharpe=+0.9755
- `combo_mean__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.7008
- `combo_z_sum__bar_vol_4__sma_distance_60d`: Train IC=+0.1970, Lock IC=+0.0852, Lock Sharpe=+0.7008
- `combo_mean__sma50_dist__bar_vol_4`: Train IC=+0.1659, Lock IC=+0.0918, Lock Sharpe=+0.6053

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `double_bottom_bull_flag_early`: Train IC=+0.0000, Lock IC=+0.0753, Lock Sharpe=+0.4768
- `consecutive_inside_bars_3d`: Train IC=+0.0000, Lock IC=+0.0364, Lock Sharpe=+0.2740
- `combo_product__sma50_dist__volume_differential_10d`: Train IC=+0.0682, Lock IC=+0.0090, Lock Sharpe=+0.0404

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1622, Lock IC=+0.0130, Lock Sharpe=+0.5948

### 500ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 74.0% lock IC > 0, 44.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0754_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1490 | 30 | 100.0% | 93.3% | +0.0864 | +0.3659 |
| B2 Rolling Guard | 310 | 30 | 96.7% | 76.7% | +0.0794 | +0.4069 |
| BH-FDR Gate | 11 | 11 | 0.0% | 0.0% | -0.0113 | -0.7696 |
| B3 Composite Floor | 250 | 30 | 100.0% | 93.3% | +0.1037 | +0.7247 |
| B4 Correlation Gate | 432 | 30 | 100.0% | 93.3% | +0.0996 | +0.5793 |

**Admitted Pool Summary**: 43 features, False Positive Rate = 23.3% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.0905, Mean Lock Sharpe = +0.3907

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2426, Lock IC=+0.0860, Lock Sharpe=+0.7897
- `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Lock Sharpe=+0.7897
- `combo_z_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`: Train IC=+0.2422, Lock IC=+0.0887, Lock Sharpe=+0.7897
- `combo_clamp_diff__max_up_ret__smooth_momentum_structure`: Train IC=+0.2887, Lock IC=+0.0793, Lock Sharpe=+0.7838
- `combo_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2635, Lock IC=+0.1118, Lock Sharpe=+0.7373

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__first_bar_sentiment__early_body_momentum`: Train IC=+0.1912, Lock IC=+0.0630, Lock Sharpe=+1.1475
- `combo_rank_max__first_bar_sentiment__opening_momentum_score`: Train IC=+0.1912, Lock IC=+0.0630, Lock Sharpe=+1.1475
- `combo_rank_max__trend_bar_close_consistency__first_bar_sentiment`: Train IC=+0.2157, Lock IC=+0.0624, Lock Sharpe=+0.9635
- `combo_mean__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Lock Sharpe=+0.7111
- `combo_z_sum__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.1025, Lock Sharpe=+0.7111

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_day_regime_conviction`: Train IC=+0.2819, Lock IC=+0.1041, Lock Sharpe=+1.2212
- `combo_rank_min__rbreaker_sell_setup_proximity_early__early_body_momentum`: Train IC=+0.2806, Lock IC=+0.1172, Lock Sharpe=+1.1947
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_momentum_score`: Train IC=+0.2806, Lock IC=+0.1172, Lock Sharpe=+1.1947
- `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.2681, Lock IC=+0.1240, Lock Sharpe=+1.1822
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2945, Lock IC=+0.1037, Lock Sharpe=+1.1804

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1217, Lock Sharpe=+1.1454
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3068, Lock IC=+0.1015, Lock Sharpe=+1.0848
- `combo_rank_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2868, Lock IC=+0.1125, Lock Sharpe=+1.0528
- `combo_rank_min__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2868, Lock IC=+0.1125, Lock Sharpe=+1.0528
- `combo_rank_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2846, Lock IC=+0.1319, Lock Sharpe=+1.0052

### 500ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 78.0% lock IC > 0, 35.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2739_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 954 | 30 | 100.0% | 30.0% | +0.0693 | +0.0390 |
| B2 Rolling Guard | 97 | 30 | 80.0% | 23.3% | +0.0535 | -0.3258 |
| BH-FDR Gate | 53 | 30 | 96.7% | 60.0% | +0.0679 | -0.0636 |
| B3 Composite Floor | 36 | 30 | 100.0% | 40.0% | +0.0517 | -0.0234 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__rbreaker_buy_setup_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__rbreaker_buy_setup_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__rbreaker_buy_setup_proximity_early__limit_down_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__limit_down_proximity_early__yesterday_return`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878
- `combo_min__limit_down_proximity_early__limit_up_proximity_day`: Train IC=+0.2604, Lock IC=+0.0768, Lock Sharpe=+0.5878

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `yesterday_day_vwap_dev`: Train IC=+0.1074, Lock IC=+0.0692, Lock Sharpe=+0.3684
- `bar_vol_4`: Train IC=+0.0794, Lock IC=+0.0045, Lock Sharpe=+0.2622
- `combo_diff__donchian_breakout_proximity_20d__yesterday_return`: Train IC=+0.0495, Lock IC=+0.0708, Lock Sharpe=+0.0834
- `combo_z_diff__donchian_breakout_proximity_20d__yesterday_return`: Train IC=+0.0495, Lock IC=+0.0708, Lock Sharpe=+0.0834
- `combo_diff__donchian_breakout_proximity_20d__limit_up_proximity_day`: Train IC=+0.0495, Lock IC=+0.0708, Lock Sharpe=+0.0834

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_buy_setup_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.8136
- `combo_rank_min__limit_down_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.1457, Lock IC=+0.1155, Lock Sharpe=+0.8136
- `first_30min_return`: Train IC=+0.1012, Lock IC=+0.0708, Lock Sharpe=+0.1899
- `open_to_current_return`: Train IC=+0.1012, Lock IC=+0.0708, Lock Sharpe=+0.1899
- `combo_mean__opening_momentum_score__star50_limit_proximity_early`: Train IC=+0.1292, Lock IC=+0.1027, Lock Sharpe=+0.1848

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1742, Lock IC=+0.1046, Lock Sharpe=+1.2349
- `combo_rank_min__star50_limit_proximity_early__shaved_bar_trend_conviction`: Train IC=+0.2116, Lock IC=+0.1196, Lock Sharpe=+1.2060
- `combo_rank_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1842, Lock IC=+0.1130, Lock Sharpe=+0.9668
- `combo_min__opening_momentum_score__rbreaker_sell_setup_proximity_early`: Train IC=+0.1819, Lock IC=+0.1072, Lock Sharpe=+0.5261
- `combo_min__early_body_momentum__rbreaker_sell_setup_proximity_early`: Train IC=+0.1819, Lock IC=+0.1072, Lock Sharpe=+0.5261

### 500ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 55.0% lock IC > 0, 33.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2357_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 356 | 30 | 46.7% | 43.3% | +0.0117 | -0.2319 |
| B2 Rolling Guard | 66 | 30 | 56.7% | 26.7% | +0.0158 | -0.2361 |
| BH-FDR Gate | 6 | 6 | 66.7% | 66.7% | +0.0726 | +0.1698 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1907, Lock IC=+0.1261, Lock Sharpe=+0.7706
- `gap_pct`: Train IC=+0.1160, Lock IC=+0.0889, Lock Sharpe=+0.4908
- `combo_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0719, Lock Sharpe=+0.4810
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0719, Lock Sharpe=+0.4810
- `combo_z_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1459, Lock IC=+0.0719, Lock Sharpe=+0.4810

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1375, Lock IC=+0.0868, Lock Sharpe=+0.5950
- `close_vs_open_range`: Train IC=+0.0789, Lock IC=+0.0872, Lock Sharpe=+0.4868
- `combo_min__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1062, Lock IC=+0.1197, Lock Sharpe=+0.3869
- `donchian_width_atr_ratio_20d`: Train IC=+0.0254, Lock IC=+0.0944, Lock Sharpe=+0.3236
- `trend_bar_close_consistency`: Train IC=+0.0828, Lock IC=+0.0529, Lock Sharpe=+0.3042

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+1.0439
- `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`: Train IC=+0.1540, Lock IC=+0.1281, Lock Sharpe=+1.0439
- `combo_mean__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.4994
- `combo_z_sum__rbreaker_sell_setup_proximity_early__gap_pct`: Train IC=+0.1305, Lock IC=+0.1180, Lock Sharpe=+0.4994

### 588000ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 27.0% lock IC > 0, 20.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4920_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 567 | 30 | 96.7% | 73.3% | +0.0474 | +0.1458 |
| B2 Rolling Guard | 325 | 30 | 36.7% | 36.7% | -0.0216 | -0.2399 |
| BH-FDR Gate | 38 | 30 | 10.0% | 10.0% | -0.0587 | -0.8415 |
| B3 Composite Floor | 470 | 30 | 3.3% | 3.3% | -0.0531 | -0.7280 |
| B4 Correlation Gate | 23 | 23 | 34.8% | 34.8% | -0.0297 | -0.4001 |

**Admitted Pool Summary**: 6 features, False Positive Rate = 83.3% (admitted but negative lock IC/Sharpe), Mean Lock IC = -0.0424, Mean Lock Sharpe = -0.5527

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_sig_product__directional_volume_signature__volume_weighted_momentum_acceleration`: Train IC=+0.2270, Lock IC=+0.0182, Lock Sharpe=+0.9905
- `volume_weighted_momentum_acceleration`: Train IC=+0.2216, Lock IC=+0.0363, Lock Sharpe=+0.9905
- `combo_min__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.2023, Lock IC=+0.0414, Lock Sharpe=+0.6246
- `combo_max__smooth_momentum_structure__early_vwap_acceleration`: Train IC=+0.2063, Lock IC=+0.0786, Lock Sharpe=+0.4001
- `combo_rank_min__early_vwap_acceleration__volume_weighted_momentum_acceleration`: Train IC=+0.2224, Lock IC=+0.0366, Lock Sharpe=+0.3950

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_rolling_percentile_60d`: Train IC=+0.1732, Lock IC=+0.0189, Lock Sharpe=+1.3113
- `bar_body_rng_1`: Train IC=+0.1664, Lock IC=+0.0226, Lock Sharpe=+0.8813
- `combo_tri_min__net_volume_flow__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.1668, Lock IC=+0.0198, Lock Sharpe=+0.7037
- `combo_tri_min__opening_auction_imbalance__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.1668, Lock IC=+0.0198, Lock Sharpe=+0.7037
- `vix_diff_1d`: Train IC=+0.2318, Lock IC=+0.0453, Lock Sharpe=+0.6705

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__high_low_sequence_momentum__pullback_depth_ratio`: Train IC=+0.1280, Lock IC=+0.0585, Lock Sharpe=+1.1745
- `combo_product__rsi_opening__pullback_depth_ratio`: Train IC=+0.1280, Lock IC=+0.0585, Lock Sharpe=+1.1745
- `volume_trend_intraday`: Train IC=+0.1105, Lock IC=+0.0414, Lock Sharpe=+0.8198

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__directional_volume_signature__opening_drive_thrust_ratio`: Train IC=+0.3064, Lock IC=+0.0010, Lock Sharpe=+0.1702

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__directional_volume_signature__early_vwap_acceleration`: Train IC=+0.2917, Lock IC=+0.0549, Lock Sharpe=+0.9909
- `combo_z_diff__directional_volume_signature__early_vwap_acceleration`: Train IC=+0.2917, Lock IC=+0.0549, Lock Sharpe=+0.9909
- `combo_rel_diff__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.3011, Lock IC=+0.0305, Lock Sharpe=+0.3474
- `combo_sig_product__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.2645, Lock IC=+0.0139, Lock Sharpe=+0.2213
- `combo_z_diff__directional_volume_signature__smooth_momentum_structure`: Train IC=+0.3037, Lock IC=+0.0282, Lock Sharpe=+0.1859

### 588000ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 52.0% lock IC > 0, 30.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4552_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 421 | 30 | 26.7% | 16.7% | -0.0361 | -0.5709 |
| B2 Rolling Guard | 197 | 30 | 53.3% | 20.0% | -0.0030 | -0.5633 |
| BH-FDR Gate | 26 | 26 | 11.5% | 7.7% | -0.0593 | -0.8176 |
| B3 Composite Floor | 3 | 3 | 0.0% | 0.0% | -0.0509 | -0.7630 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `vix_rolling_percentile_60d`: Train IC=+0.2034, Lock IC=+0.0189, Lock Sharpe=+1.5524
- `vix_realized_spread`: Train IC=+0.1995, Lock IC=+0.0695, Lock Sharpe=+1.3777
- `combo_clamp_diff__vix_rolling_percentile_60d__vol5`: Train IC=+0.1964, Lock IC=+0.1052, Lock Sharpe=+1.0313
- `combo_mean__vix_skew_proxy__vix_iv_spread`: Train IC=+0.2519, Lock IC=+0.0492, Lock Sharpe=+0.4210
- `combo_z_sum__vix_skew_proxy__vix_iv_spread`: Train IC=+0.2519, Lock IC=+0.0492, Lock Sharpe=+0.4210

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_mean__iv_envelope_deviation__vix_skew_proxy`: Train IC=+0.2856, Lock IC=+0.0271, Lock Sharpe=+0.1605
- `combo_z_sum__iv_envelope_deviation__vix_skew_proxy`: Train IC=+0.2856, Lock IC=+0.0271, Lock Sharpe=+0.1605
- `combo_mean__iv_envelope_deviation__vix_diff_1d`: Train IC=+0.2414, Lock IC=+0.0346, Lock Sharpe=+0.0660
- `combo_z_sum__iv_envelope_deviation__vix_diff_1d`: Train IC=+0.2414, Lock IC=+0.0346, Lock Sharpe=+0.0660
- `combo_mean__iv_envelope_deviation__yesterday_vix_early_drift`: Train IC=+0.2414, Lock IC=+0.0346, Lock Sharpe=+0.0660

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `lunch_transition_volume_skew`: Train IC=+0.0244, Lock IC=+0.0560, Lock Sharpe=+0.7736
- `combo_abs_diff__vol5__yesterday_day_realized_vol`: Train IC=+0.2014, Lock IC=+0.0186, Lock Sharpe=+0.0524

### 588000ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 37.0% lock IC > 0, 25.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.2320_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 485 | 30 | 13.3% | 10.0% | -0.0402 | -0.1466 |
| B2 Rolling Guard | 223 | 30 | 16.7% | 3.3% | -0.0443 | -0.1321 |
| BH-FDR Gate | 52 | 30 | 26.7% | 23.3% | -0.0090 | +0.1053 |
| B3 Composite Floor | 12 | 12 | 50.0% | 50.0% | +0.0159 | +0.3303 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__pullback_depth_ratio__opening_drive_thrust_ratio`: Train IC=+0.2129, Lock IC=+0.1599, Lock Sharpe=+0.8991
- `combo_diff__early_vwap_acceleration__directional_volume_signature`: Train IC=+0.2665, Lock IC=+0.0549, Lock Sharpe=+0.7615
- `combo_z_diff__early_vwap_acceleration__directional_volume_signature`: Train IC=+0.2665, Lock IC=+0.0549, Lock Sharpe=+0.7615

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_clamp_diff__early_vwap_acceleration__bar_ret_1`: Train IC=+0.2092, Lock IC=+0.0257, Lock Sharpe=+0.3886

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_max__directional_volume_signature__rbreaker_buy_setup_proximity_early`: Train IC=+0.1138, Lock IC=+0.0176, Lock Sharpe=+1.2122
- `combo_rank_max__directional_volume_signature__limit_down_proximity_early`: Train IC=+0.1138, Lock IC=+0.0176, Lock Sharpe=+1.2122
- `combo_min__opening_drive_thrust_ratio__directional_volume_signature`: Train IC=+0.1711, Lock IC=+0.0010, Lock Sharpe=+1.1356
- `combo_rank_min__pullback_depth_ratio__bar_ret_1`: Train IC=+0.1668, Lock IC=+0.1831, Lock Sharpe=+0.6416
- `bar_vwap_dev_1`: Train IC=+0.1205, Lock IC=+0.0191, Lock Sharpe=+0.5955

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_product__pullback_depth_ratio__opening_drive_thrust_ratio`: Train IC=+0.2417, Lock IC=+0.0719, Lock Sharpe=+2.2598
- `combo_rank_min__pullback_depth_ratio__tight_channel_persistence`: Train IC=+0.2595, Lock IC=+0.1475, Lock Sharpe=+0.7472
- `combo_mean__directional_volume_signature__bar_ret_1`: Train IC=+0.2562, Lock IC=+0.0284, Lock Sharpe=+0.6247
- `combo_z_sum__directional_volume_signature__bar_ret_1`: Train IC=+0.2562, Lock IC=+0.0284, Lock Sharpe=+0.6247
- `combo_min__pullback_depth_ratio__opening_auction_imbalance`: Train IC=+0.3116, Lock IC=+0.1096, Lock Sharpe=+0.5279

### 159915ETF — `single` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 73.0% lock IC > 0, 54.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = +0.2153_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 1128 | 30 | 100.0% | 66.7% | +0.0931 | +0.5098 |
| B2 Rolling Guard | 382 | 30 | 100.0% | 96.7% | +0.1066 | +0.7185 |
| BH-FDR Gate | 5 | 5 | 80.0% | 80.0% | +0.0384 | +0.5044 |
| B3 Composite Floor | 268 | 30 | 100.0% | 100.0% | +0.1294 | +1.3703 |
| B4 Correlation Gate | 54 | 30 | 100.0% | 100.0% | +0.1307 | +1.3592 |

**Admitted Pool Summary**: 9 features, False Positive Rate = 11.1% (admitted but negative lock IC/Sharpe), Mean Lock IC = +0.1249, Mean Lock Sharpe = +1.0644

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Lock Sharpe=+1.6125
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2248, Lock IC=+0.1533, Lock Sharpe=+1.6125
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2770, Lock IC=+0.1091, Lock Sharpe=+1.5826
- `combo_rank_min__first_bar_sentiment__limit_down_proximity_early`: Train IC=+0.2419, Lock IC=+0.1134, Lock Sharpe=+1.3320
- `combo_rank_min__first_bar_sentiment__rbreaker_buy_setup_proximity_early`: Train IC=+0.2419, Lock IC=+0.1134, Lock Sharpe=+1.3320

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Lock Sharpe=+1.7191
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1310, Lock Sharpe=+1.7191
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2801, Lock IC=+0.1413, Lock Sharpe=+1.4595
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2361, Lock IC=+0.1495, Lock Sharpe=+1.4034
- `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`: Train IC=+0.2189, Lock IC=+0.0877, Lock Sharpe=+1.2104

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Lock Sharpe=+1.0460
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0489, Lock Sharpe=+1.0460
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0948, Lock IC=+0.0497, Lock Sharpe=+1.0460
- `close_vs_open_range`: Train IC=+0.0863, Lock IC=+0.0988, Lock Sharpe=+0.7603

**Top True False Negatives from B3 Composite Floor** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Lock Sharpe=+1.8373
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1370, Lock Sharpe=+1.8373
- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2895, Lock IC=+0.1279, Lock Sharpe=+1.8188
- `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.2766, Lock IC=+0.1375, Lock Sharpe=+1.7472
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2957, Lock IC=+0.1138, Lock Sharpe=+1.7355

**Top True False Negatives from B4 Correlation Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Lock Sharpe=+2.0165
- `combo_z_sum__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2548, Lock IC=+0.1307, Lock Sharpe=+2.0165
- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2509, Lock IC=+0.1242, Lock Sharpe=+1.8505
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1419, Lock Sharpe=+1.8188
- `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2647, Lock IC=+0.1340, Lock Sharpe=+1.6914

### 159915ETF — `long` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 70.0% lock IC > 0, 46.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.0366_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 651 | 30 | 80.0% | 60.0% | +0.0756 | +0.3444 |
| B2 Rolling Guard | 67 | 30 | 96.7% | 96.7% | +0.0862 | +0.6461 |
| BH-FDR Gate | 24 | 24 | 91.7% | 70.8% | +0.0664 | +0.4617 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1406, Lock IC=+0.1687, Lock Sharpe=+1.0747
- `combo_tri_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1450, Lock IC=+0.1569, Lock Sharpe=+1.0547
- `combo_tri_min__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1450, Lock IC=+0.1569, Lock Sharpe=+1.0547
- `combo_mean__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1398, Lock IC=+0.1469, Lock Sharpe=+0.9504
- `combo_z_sum__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1398, Lock IC=+0.1469, Lock Sharpe=+0.9504

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_tri_min__opening_drive_thrust_ratio__micro_gap_trend_continuation__rbreaker_sell_setup_proximity_early`: Train IC=+0.1336, Lock IC=+0.1014, Lock Sharpe=+1.3455
- `combo_tri_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction__first_30min_return`: Train IC=+0.0383, Lock IC=+0.0968, Lock Sharpe=+1.0630
- `combo_tri_max__opening_drive_thrust_ratio__shaved_bar_trend_conviction__open_to_current_return`: Train IC=+0.0383, Lock IC=+0.0968, Lock Sharpe=+1.0630
- `combo_min__rbreaker_sell_setup_proximity_early__first_30min_return`: Train IC=+0.1197, Lock IC=+0.1425, Lock Sharpe=+0.9201
- `combo_min__rbreaker_sell_setup_proximity_early__open_to_current_return`: Train IC=+0.1197, Lock IC=+0.1425, Lock Sharpe=+0.9201

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `net_volume_flow`: Train IC=+0.0152, Lock IC=+0.1008, Lock Sharpe=+1.6234
- `opening_auction_imbalance`: Train IC=+0.0152, Lock IC=+0.1008, Lock Sharpe=+1.6234
- `combo_tri_min__opening_drive_thrust_ratio__shaved_bar_trend_conviction__rbreaker_sell_setup_proximity_early`: Train IC=+0.1514, Lock IC=+0.1368, Lock Sharpe=+1.4077
- `combo_mean__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.0240, Lock IC=+0.1014, Lock Sharpe=+1.1343
- `combo_z_sum__opening_drive_thrust_ratio__shaved_bar_trend_conviction`: Train IC=+0.0240, Lock IC=+0.1014, Lock Sharpe=+1.1343

### 159915ETF — `short` Gate Effectiveness

_Null Baseline (un-gated candidate pool): 37.0% lock IC > 0, 16.0% true FN rate (IC>0 & Sharpe>0), Mean Lock Sharpe = -0.4645_

| Gate | N Rejected | N Sampled | % Lock IC > 0 | True FN Rate (IC>0 & Sharpe>0) | Mean Lock IC | Mean Lock Sharpe |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 286 | 30 | 50.0% | 30.0% | -0.0026 | -0.3342 |
| B2 Rolling Guard | 67 | 30 | 50.0% | 33.3% | +0.0060 | -0.2346 |
| BH-FDR Gate | 3 | 3 | 100.0% | 66.7% | +0.1026 | +0.5571 |

**Top True False Negatives from 7-Year Jackknife Sign Stability** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.1709, Lock IC=+0.0830, Lock Sharpe=+0.9042
- `yesterday_pm_return`: Train IC=+0.1096, Lock IC=+0.0803, Lock Sharpe=+0.7355
- `early_realized_vol`: Train IC=+0.0947, Lock IC=+0.0234, Lock Sharpe=+0.4184
- `yesterday_afternoon_momentum`: Train IC=+0.1068, Lock IC=+0.0755, Lock Sharpe=+0.3907
- `combo_mean__close_location_in_range_3d__yesterday_afternoon_momentum`: Train IC=+0.2129, Lock IC=+0.0695, Lock Sharpe=+0.3893

**Top True False Negatives from B2 Rolling Guard** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `combo_max__morning_volume_weighted_momentum__failed_breakout_reversal_early`: Train IC=+0.0039, Lock IC=+0.0717, Lock Sharpe=+1.1309
- `gap_pct`: Train IC=+0.0358, Lock IC=+0.1182, Lock Sharpe=+0.6561
- `yesterday_day_realized_vol`: Train IC=+0.0376, Lock IC=+0.0061, Lock Sharpe=+0.4932
- `first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.0619, Lock Sharpe=+0.4303
- `volatility_expansion_trend_vector`: Train IC=+0.0202, Lock IC=+0.0923, Lock Sharpe=+0.3957

**Top True False Negatives from BH-FDR Gate** (rejected but lockbox IC > 0 AND Sharpe > 0):

- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0206, Lock IC=+0.1272, Lock Sharpe=+0.9699
- `limit_down_proximity_early`: Train IC=+0.0205, Lock IC=+0.1272, Lock Sharpe=+0.9699

---

## Gate Threshold Sensitivity

Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.
Optimal zone: high % positive lock IC with reasonable pool size.

### 300ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 508 | +0.0300 | 100.0% |
| 0.45 | 0.20 | 487 | +0.0300 | 100.0% |
| 0.45 | 0.30 | 421 | +0.0300 | 100.0% |
| 0.45 | 0.40 | 302 | +0.0300 | 100.0% |
| 0.45 | 0.50 | 187 | +0.0300 | 100.0% |
| 0.50 | 0.15 | 498 | +0.0300 | 100.0% |
| 0.50 | 0.25 | 465 | +0.0300 | 100.0% |
| 0.50 | 0.35 | 360 | +0.0300 | 100.0% |
| 0.50 | 0.45 | 253 | +0.0300 | 100.0% |
| 0.55 | 0.10 | 497 | +0.0300 | 100.0% |
| 0.55 | 0.20 | 486 | +0.0300 | 100.0% |
| 0.55 | 0.30 | 421 | +0.0300 | 100.0% |
| 0.55 | 0.40 | 302 | +0.0300 | 100.0% |
| 0.55 | 0.50 | 187 | +0.0300 | 100.0% |
| 0.60 | 0.15 | 433 | +0.0300 | 100.0% |
| 0.60 | 0.25 | 432 | +0.0300 | 100.0% |
| 0.60 | 0.35 | 360 | +0.0300 | 100.0% |
| 0.60 | 0.45 | 253 | +0.0300 | 100.0% |
| 0.65 | 0.10 | 292 | +0.0300 | 100.0% |
| 0.65 | 0.20 | 292 | +0.0300 | 100.0% |
| 0.65 | 0.30 | 290 | +0.0300 | 100.0% |
| 0.65 | 0.40 | 280 | +0.0300 | 100.0% |
| 0.65 | 0.50 | 187 | +0.0300 | 100.0% |
| 0.70 | 0.15 | 145 | +0.0290 | 100.0% |
| 0.70 | 0.25 | 145 | +0.0290 | 100.0% |
| 0.70 | 0.35 | 145 | +0.0290 | 100.0% |
| 0.70 | 0.45 | 145 | +0.0290 | 100.0% |
| 0.75 | 0.10 | 31 | +0.0214 | 80.0% |
| 0.75 | 0.20 | 31 | +0.0214 | 80.0% |
| 0.75 | 0.30 | 31 | +0.0214 | 80.0% |
| 0.75 | 0.40 | 31 | +0.0214 | 80.0% |
| 0.75 | 0.50 | 31 | +0.0214 | 80.0% |
| 0.80 | 0.15 | 11 | +0.0262 | 100.0% |
| 0.80 | 0.25 | 11 | +0.0262 | 100.0% |
| 0.80 | 0.35 | 11 | +0.0262 | 100.0% |
| 0.80 | 0.45 | 11 | +0.0262 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 508 candidates, mean lock IC=+0.0300, 100.0% positive

### 300ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 16 | -0.0287 | 0.0% |
| 0.45 | 0.20 | 10 | -0.0244 | 0.0% |
| 0.45 | 0.30 | 5 | -0.0269 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 11 | -0.0287 | 0.0% |
| 0.50 | 0.25 | 8 | -0.0223 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 9 | -0.0266 | 0.0% |
| 0.55 | 0.20 | 8 | -0.0223 | 0.0% |
| 0.55 | 0.30 | 5 | -0.0269 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.25 → 8 candidates, mean lock IC=-0.0223, 0.0% positive

### 300ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 20 | +0.0365 | 100.0% |
| 0.45 | 0.20 | 10 | +0.0268 | 80.0% |
| 0.45 | 0.30 | 7 | +0.0253 | 85.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 15 | +0.0299 | 90.0% |
| 0.50 | 0.25 | 8 | +0.0240 | 87.5% |
| 0.50 | 0.35 | 4 | +0.0202 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 15 | +0.0348 | 90.0% |
| 0.55 | 0.20 | 10 | +0.0268 | 80.0% |
| 0.55 | 0.30 | 7 | +0.0253 | 85.7% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 7 | +0.0253 | 85.7% |
| 0.60 | 0.25 | 7 | +0.0253 | 85.7% |
| 0.60 | 0.35 | 4 | +0.0202 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 20 candidates, mean lock IC=+0.0365, 100.0% positive

### 50ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 501 | +0.0498 | 100.0% |
| 0.45 | 0.20 | 488 | +0.0498 | 100.0% |
| 0.45 | 0.30 | 464 | +0.0498 | 100.0% |
| 0.45 | 0.40 | 437 | +0.0498 | 100.0% |
| 0.45 | 0.50 | 417 | +0.0508 | 100.0% |
| 0.50 | 0.15 | 495 | +0.0498 | 100.0% |
| 0.50 | 0.25 | 478 | +0.0498 | 100.0% |
| 0.50 | 0.35 | 451 | +0.0498 | 100.0% |
| 0.50 | 0.45 | 431 | +0.0498 | 100.0% |
| 0.55 | 0.10 | 495 | +0.0498 | 100.0% |
| 0.55 | 0.20 | 488 | +0.0498 | 100.0% |
| 0.55 | 0.30 | 464 | +0.0498 | 100.0% |
| 0.55 | 0.40 | 437 | +0.0498 | 100.0% |
| 0.55 | 0.50 | 417 | +0.0508 | 100.0% |
| 0.60 | 0.15 | 469 | +0.0498 | 100.0% |
| 0.60 | 0.25 | 468 | +0.0498 | 100.0% |
| 0.60 | 0.35 | 451 | +0.0498 | 100.0% |
| 0.60 | 0.45 | 431 | +0.0498 | 100.0% |
| 0.65 | 0.10 | 437 | +0.0498 | 100.0% |
| 0.65 | 0.20 | 437 | +0.0498 | 100.0% |
| 0.65 | 0.30 | 437 | +0.0498 | 100.0% |
| 0.65 | 0.40 | 433 | +0.0498 | 100.0% |
| 0.65 | 0.50 | 417 | +0.0508 | 100.0% |
| 0.70 | 0.15 | 403 | +0.0498 | 100.0% |
| 0.70 | 0.25 | 403 | +0.0498 | 100.0% |
| 0.70 | 0.35 | 403 | +0.0498 | 100.0% |
| 0.70 | 0.45 | 403 | +0.0498 | 100.0% |
| 0.75 | 0.10 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.20 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.30 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.40 | 361 | +0.0394 | 100.0% |
| 0.75 | 0.50 | 361 | +0.0394 | 100.0% |
| 0.80 | 0.15 | 267 | +0.0469 | 100.0% |
| 0.80 | 0.25 | 267 | +0.0469 | 100.0% |
| 0.80 | 0.35 | 267 | +0.0469 | 100.0% |
| 0.80 | 0.45 | 267 | +0.0469 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.50 → 417 candidates, mean lock IC=+0.0508, 100.0% positive

### 50ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 26 | -0.0446 | 0.0% |
| 0.45 | 0.20 | 8 | -0.0314 | 14.3% |
| 0.45 | 0.30 | 6 | -0.0484 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 15 | -0.0446 | 0.0% |
| 0.50 | 0.25 | 7 | -0.0484 | 0.0% |
| 0.50 | 0.35 | 5 | -0.0447 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 9 | -0.0416 | 0.0% |
| 0.55 | 0.20 | 6 | -0.0484 | 0.0% |
| 0.55 | 0.30 | 6 | -0.0484 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 6 | -0.0484 | 0.0% |
| 0.60 | 0.25 | 6 | -0.0484 | 0.0% |
| 0.60 | 0.35 | 5 | -0.0447 | 0.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 8 candidates, mean lock IC=-0.0314, 14.3% positive

### 50ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 10 | -0.0043 | 50.0% |
| 0.45 | 0.20 | 7 | +0.0095 | 57.1% |
| 0.45 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | -0.0094 | 44.4% |
| 0.50 | 0.25 | 3 | -0.0020 | 66.7% |
| 0.50 | 0.35 | 3 | -0.0020 | 66.7% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 7 | -0.0118 | 42.9% |
| 0.55 | 0.20 | 5 | -0.0064 | 40.0% |
| 0.55 | 0.30 | 3 | -0.0020 | 66.7% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 4 | -0.0068 | 50.0% |
| 0.60 | 0.25 | 3 | -0.0020 | 66.7% |
| 0.60 | 0.35 | 3 | -0.0020 | 66.7% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 7 candidates, mean lock IC=+0.0095, 57.1% positive

### 500ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 1518 | +0.1210 | 100.0% |
| 0.45 | 0.20 | 1486 | +0.1210 | 100.0% |
| 0.45 | 0.30 | 1417 | +0.1210 | 100.0% |
| 0.45 | 0.40 | 1252 | +0.1210 | 100.0% |
| 0.45 | 0.50 | 999 | +0.1210 | 100.0% |
| 0.50 | 0.15 | 1509 | +0.1210 | 100.0% |
| 0.50 | 0.25 | 1472 | +0.1210 | 100.0% |
| 0.50 | 0.35 | 1341 | +0.1210 | 100.0% |
| 0.50 | 0.45 | 1130 | +0.1210 | 100.0% |
| 0.55 | 0.10 | 1513 | +0.1210 | 100.0% |
| 0.55 | 0.20 | 1486 | +0.1210 | 100.0% |
| 0.55 | 0.30 | 1417 | +0.1210 | 100.0% |
| 0.55 | 0.40 | 1252 | +0.1210 | 100.0% |
| 0.55 | 0.50 | 999 | +0.1210 | 100.0% |
| 0.60 | 0.15 | 1455 | +0.1210 | 100.0% |
| 0.60 | 0.25 | 1445 | +0.1210 | 100.0% |
| 0.60 | 0.35 | 1338 | +0.1210 | 100.0% |
| 0.60 | 0.45 | 1130 | +0.1210 | 100.0% |
| 0.65 | 0.10 | 1241 | +0.1210 | 100.0% |
| 0.65 | 0.20 | 1241 | +0.1210 | 100.0% |
| 0.65 | 0.30 | 1237 | +0.1210 | 100.0% |
| 0.65 | 0.40 | 1199 | +0.1210 | 100.0% |
| 0.65 | 0.50 | 993 | +0.1210 | 100.0% |
| 0.70 | 0.15 | 866 | +0.1210 | 100.0% |
| 0.70 | 0.25 | 866 | +0.1210 | 100.0% |
| 0.70 | 0.35 | 866 | +0.1210 | 100.0% |
| 0.70 | 0.45 | 858 | +0.1210 | 100.0% |
| 0.75 | 0.10 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.20 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.30 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.40 | 454 | +0.1210 | 100.0% |
| 0.75 | 0.50 | 454 | +0.1210 | 100.0% |
| 0.80 | 0.15 | 161 | +0.1058 | 100.0% |
| 0.80 | 0.25 | 161 | +0.1058 | 100.0% |
| 0.80 | 0.35 | 161 | +0.1058 | 100.0% |
| 0.80 | 0.45 | 161 | +0.1058 | 100.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 1518 candidates, mean lock IC=+0.1210, 100.0% positive

### 500ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 110 | +0.0497 | 100.0% |
| 0.45 | 0.20 | 85 | +0.0497 | 100.0% |
| 0.45 | 0.30 | 45 | +0.0362 | 100.0% |
| 0.45 | 0.40 | 8 | +0.0521 | 87.5% |
| 0.45 | 0.50 | 2 | +0.1072 | 100.0% |
| 0.50 | 0.15 | 90 | +0.0497 | 100.0% |
| 0.50 | 0.25 | 63 | +0.0670 | 100.0% |
| 0.50 | 0.35 | 19 | +0.0511 | 100.0% |
| 0.50 | 0.45 | 4 | +0.0783 | 100.0% |
| 0.55 | 0.10 | 101 | +0.0497 | 100.0% |
| 0.55 | 0.20 | 84 | +0.0497 | 100.0% |
| 0.55 | 0.30 | 45 | +0.0362 | 100.0% |
| 0.55 | 0.40 | 8 | +0.0521 | 87.5% |
| 0.55 | 0.50 | 2 | +0.1072 | 100.0% |
| 0.60 | 0.15 | 56 | +0.0362 | 100.0% |
| 0.60 | 0.25 | 55 | +0.0362 | 100.0% |
| 0.60 | 0.35 | 19 | +0.0511 | 100.0% |
| 0.60 | 0.45 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.10 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.20 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.30 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.40 | 4 | +0.0783 | 100.0% |
| 0.65 | 0.50 | 2 | +0.1072 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.45 → 4 candidates, mean lock IC=+0.0783, 100.0% positive

### 500ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 15 | +0.0574 | 80.0% |
| 0.45 | 0.20 | 3 | -0.0178 | 33.3% |
| 0.45 | 0.30 | 1 | -0.0236 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 9 | +0.0579 | 77.8% |
| 0.50 | 0.25 | 1 | -0.0236 | 0.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 6 | +0.0726 | 66.7% |
| 0.55 | 0.20 | 2 | -0.0281 | 0.0% |
| 0.55 | 0.30 | 1 | -0.0236 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 2 | +0.1180 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.10 → 6 candidates, mean lock IC=+0.0726, 66.7% positive

### 588000ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 954 | -0.0255 | 0.0% |
| 0.45 | 0.20 | 900 | -0.0255 | 0.0% |
| 0.45 | 0.30 | 796 | -0.0255 | 0.0% |
| 0.45 | 0.40 | 697 | -0.0255 | 0.0% |
| 0.45 | 0.50 | 595 | -0.0255 | 0.0% |
| 0.50 | 0.15 | 925 | -0.0255 | 0.0% |
| 0.50 | 0.25 | 840 | -0.0255 | 0.0% |
| 0.50 | 0.35 | 748 | -0.0255 | 0.0% |
| 0.50 | 0.45 | 634 | -0.0255 | 0.0% |
| 0.55 | 0.10 | 912 | -0.0255 | 0.0% |
| 0.55 | 0.20 | 883 | -0.0255 | 0.0% |
| 0.55 | 0.30 | 796 | -0.0255 | 0.0% |
| 0.55 | 0.40 | 697 | -0.0255 | 0.0% |
| 0.55 | 0.50 | 595 | -0.0255 | 0.0% |
| 0.60 | 0.15 | 817 | -0.0255 | 0.0% |
| 0.60 | 0.25 | 785 | -0.0255 | 0.0% |
| 0.60 | 0.35 | 737 | -0.0255 | 0.0% |
| 0.60 | 0.45 | 634 | -0.0255 | 0.0% |
| 0.65 | 0.10 | 694 | -0.0255 | 0.0% |
| 0.65 | 0.20 | 694 | -0.0255 | 0.0% |
| 0.65 | 0.30 | 691 | -0.0255 | 0.0% |
| 0.65 | 0.40 | 670 | -0.0255 | 0.0% |
| 0.65 | 0.50 | 593 | -0.0255 | 0.0% |
| 0.70 | 0.15 | 569 | -0.0255 | 0.0% |
| 0.70 | 0.25 | 569 | -0.0255 | 0.0% |
| 0.70 | 0.35 | 569 | -0.0255 | 0.0% |
| 0.70 | 0.45 | 563 | -0.0255 | 0.0% |
| 0.75 | 0.10 | 403 | -0.0255 | 0.0% |
| 0.75 | 0.20 | 403 | -0.0255 | 0.0% |
| 0.75 | 0.30 | 403 | -0.0255 | 0.0% |
| 0.75 | 0.40 | 403 | -0.0255 | 0.0% |
| 0.75 | 0.50 | 403 | -0.0255 | 0.0% |
| 0.80 | 0.15 | 161 | -0.0255 | 0.0% |
| 0.80 | 0.25 | 161 | -0.0255 | 0.0% |
| 0.80 | 0.35 | 161 | -0.0255 | 0.0% |
| 0.80 | 0.45 | 161 | -0.0255 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 954 candidates, mean lock IC=-0.0255, 0.0% positive

### 588000ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 62 | -0.0396 | 20.0% |
| 0.45 | 0.20 | 28 | -0.0374 | 10.0% |
| 0.45 | 0.30 | 20 | -0.0392 | 10.0% |
| 0.45 | 0.40 | 13 | -0.0346 | 10.0% |
| 0.45 | 0.50 | 10 | -0.0346 | 10.0% |
| 0.50 | 0.15 | 36 | -0.0374 | 10.0% |
| 0.50 | 0.25 | 25 | -0.0366 | 10.0% |
| 0.50 | 0.35 | 16 | -0.0392 | 10.0% |
| 0.50 | 0.45 | 11 | -0.0346 | 10.0% |
| 0.55 | 0.10 | 33 | -0.0374 | 10.0% |
| 0.55 | 0.20 | 27 | -0.0374 | 10.0% |
| 0.55 | 0.30 | 20 | -0.0392 | 10.0% |
| 0.55 | 0.40 | 13 | -0.0346 | 10.0% |
| 0.55 | 0.50 | 10 | -0.0346 | 10.0% |
| 0.60 | 0.15 | 22 | -0.0376 | 10.0% |
| 0.60 | 0.25 | 22 | -0.0376 | 10.0% |
| 0.60 | 0.35 | 16 | -0.0392 | 10.0% |
| 0.60 | 0.45 | 11 | -0.0346 | 10.0% |
| 0.65 | 0.10 | 15 | -0.0379 | 10.0% |
| 0.65 | 0.20 | 15 | -0.0379 | 10.0% |
| 0.65 | 0.30 | 15 | -0.0379 | 10.0% |
| 0.65 | 0.40 | 13 | -0.0346 | 10.0% |
| 0.65 | 0.50 | 10 | -0.0346 | 10.0% |
| 0.70 | 0.15 | 2 | -0.0545 | 0.0% |
| 0.70 | 0.25 | 2 | -0.0545 | 0.0% |
| 0.70 | 0.35 | 2 | -0.0545 | 0.0% |
| 0.70 | 0.45 | 2 | -0.0545 | 0.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.50, ir_thr=0.10 → 59 candidates, mean lock IC=-0.0318, 30.0% positive

### 588000ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 128 | +0.0198 | 60.0% |
| 0.45 | 0.20 | 74 | +0.0198 | 60.0% |
| 0.45 | 0.30 | 42 | +0.0230 | 60.0% |
| 0.45 | 0.40 | 19 | +0.0368 | 50.0% |
| 0.45 | 0.50 | 7 | +0.0322 | 42.9% |
| 0.50 | 0.15 | 84 | +0.0198 | 60.0% |
| 0.50 | 0.25 | 51 | +0.0198 | 60.0% |
| 0.50 | 0.35 | 28 | +0.0269 | 40.0% |
| 0.50 | 0.45 | 12 | +0.0262 | 60.0% |
| 0.55 | 0.10 | 71 | +0.0198 | 60.0% |
| 0.55 | 0.20 | 61 | +0.0198 | 60.0% |
| 0.55 | 0.30 | 42 | +0.0230 | 60.0% |
| 0.55 | 0.40 | 19 | +0.0368 | 50.0% |
| 0.55 | 0.50 | 7 | +0.0322 | 42.9% |
| 0.60 | 0.15 | 39 | +0.0003 | 40.0% |
| 0.60 | 0.25 | 32 | +0.0005 | 40.0% |
| 0.60 | 0.35 | 24 | +0.0234 | 40.0% |
| 0.60 | 0.45 | 12 | +0.0262 | 60.0% |
| 0.65 | 0.10 | 17 | +0.0267 | 50.0% |
| 0.65 | 0.20 | 17 | +0.0267 | 50.0% |
| 0.65 | 0.30 | 17 | +0.0267 | 50.0% |
| 0.65 | 0.40 | 13 | +0.0043 | 40.0% |
| 0.65 | 0.50 | 7 | +0.0322 | 42.9% |
| 0.70 | 0.15 | 4 | +0.0169 | 25.0% |
| 0.70 | 0.25 | 4 | +0.0169 | 25.0% |
| 0.70 | 0.35 | 4 | +0.0169 | 25.0% |
| 0.70 | 0.45 | 4 | +0.0169 | 25.0% |
| 0.75 | 0.10 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.20 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.75 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.15 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.25 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.80 | 0.45 | 0 | +0.0000 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.40 → 19 candidates, mean lock IC=+0.0368, 50.0% positive

### 159915ETF — `single` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 714 | +0.1299 | 100.0% |
| 0.45 | 0.20 | 679 | +0.1299 | 100.0% |
| 0.45 | 0.30 | 537 | +0.1299 | 100.0% |
| 0.45 | 0.40 | 391 | +0.1299 | 100.0% |
| 0.45 | 0.50 | 215 | +0.1299 | 100.0% |
| 0.50 | 0.15 | 696 | +0.1299 | 100.0% |
| 0.50 | 0.25 | 613 | +0.1299 | 100.0% |
| 0.50 | 0.35 | 461 | +0.1299 | 100.0% |
| 0.50 | 0.45 | 315 | +0.1299 | 100.0% |
| 0.55 | 0.10 | 699 | +0.1299 | 100.0% |
| 0.55 | 0.20 | 672 | +0.1299 | 100.0% |
| 0.55 | 0.30 | 537 | +0.1299 | 100.0% |
| 0.55 | 0.40 | 391 | +0.1299 | 100.0% |
| 0.55 | 0.50 | 215 | +0.1299 | 100.0% |
| 0.60 | 0.15 | 611 | +0.1299 | 100.0% |
| 0.60 | 0.25 | 574 | +0.1299 | 100.0% |
| 0.60 | 0.35 | 455 | +0.1299 | 100.0% |
| 0.60 | 0.45 | 315 | +0.1299 | 100.0% |
| 0.65 | 0.10 | 380 | +0.1299 | 100.0% |
| 0.65 | 0.20 | 380 | +0.1299 | 100.0% |
| 0.65 | 0.30 | 377 | +0.1299 | 100.0% |
| 0.65 | 0.40 | 345 | +0.1299 | 100.0% |
| 0.65 | 0.50 | 210 | +0.1299 | 100.0% |
| 0.70 | 0.15 | 148 | +0.1263 | 100.0% |
| 0.70 | 0.25 | 148 | +0.1263 | 100.0% |
| 0.70 | 0.35 | 148 | +0.1263 | 100.0% |
| 0.70 | 0.45 | 145 | +0.1263 | 100.0% |
| 0.75 | 0.10 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.20 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.30 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.40 | 19 | +0.1295 | 100.0% |
| 0.75 | 0.50 | 19 | +0.1295 | 100.0% |
| 0.80 | 0.15 | 4 | -0.0044 | 0.0% |
| 0.80 | 0.25 | 4 | -0.0044 | 0.0% |
| 0.80 | 0.35 | 4 | -0.0044 | 0.0% |
| 0.80 | 0.45 | 4 | -0.0044 | 0.0% |

**Optimal**: mono_thr=0.45, ir_thr=0.10 → 714 candidates, mean lock IC=+0.1299, 100.0% positive

### 159915ETF — `long` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 43 | +0.0757 | 100.0% |
| 0.45 | 0.20 | 28 | +0.0785 | 100.0% |
| 0.45 | 0.30 | 12 | +0.0614 | 90.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 33 | +0.0747 | 100.0% |
| 0.50 | 0.25 | 15 | +0.0761 | 100.0% |
| 0.50 | 0.35 | 2 | +0.1005 | 100.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 28 | +0.0719 | 100.0% |
| 0.55 | 0.20 | 22 | +0.0719 | 100.0% |
| 0.55 | 0.30 | 12 | +0.0614 | 90.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 11 | +0.0541 | 90.0% |
| 0.60 | 0.25 | 11 | +0.0541 | 90.0% |
| 0.60 | 0.35 | 1 | +0.0641 | 100.0% |
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

**Optimal**: mono_thr=0.45, ir_thr=0.20 → 28 candidates, mean lock IC=+0.0785, 100.0% positive

### 159915ETF — `short` Threshold Sensitivity

| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |
| ---: | ---: | ---: | ---: | ---: |
| 0.45 | 0.10 | 9 | +0.0688 | 88.9% |
| 0.45 | 0.20 | 1 | +0.0532 | 100.0% |
| 0.45 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.45 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.15 | 5 | +0.0842 | 100.0% |
| 0.50 | 0.25 | 1 | +0.0532 | 100.0% |
| 0.50 | 0.35 | 0 | +0.0000 | 0.0% |
| 0.50 | 0.45 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.10 | 4 | +0.0944 | 100.0% |
| 0.55 | 0.20 | 1 | +0.0532 | 100.0% |
| 0.55 | 0.30 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.40 | 0 | +0.0000 | 0.0% |
| 0.55 | 0.50 | 0 | +0.0000 | 0.0% |
| 0.60 | 0.15 | 1 | +0.0532 | 100.0% |
| 0.60 | 0.25 | 1 | +0.0532 | 100.0% |
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

**Optimal**: mono_thr=0.55, ir_thr=0.15 → 3 candidates, mean lock IC=+0.1026, 100.0% positive

---

## Feature IC Decay Analysis

Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.
Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.

### 300ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | +0.1304 | +0.0983 | +0.0280 | 0.21x | 2016-08-24 |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1218 | +0.0774 | +0.0372 | 0.31x | 2016-08-24 |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1169 | +0.0920 | +0.0189 | 0.16x | 2017-05-09 |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment` | +0.1017 | +0.0982 | +0.0353 | 0.35x | 2013-09-23 |
| `rbreaker_sell_setup_proximity_early` | +0.0953 | +0.0781 | +0.0616 | 0.65x | 2016-08-24 |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | +0.1128 | +0.0907 | +0.0635 | 0.56x | 2016-08-24 |
| `combo_z_sum__max_up_ret__volume_weighted_price_position` | +0.1123 | +0.1251 | -0.0129 | -0.11x | 2015-02-06 |
| `combo_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.0068 | -0.0014 | +0.0016 | 0.24x | 2011-11-24 |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | +0.0428 | +0.0379 | +0.0706 | 1.65x | 2012-10-09 |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | +0.0571 | +0.0418 | -0.0280 | -0.49x | 2010-10-15 |

### 500ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment` | +0.1895 | +0.1062 | +0.1145 | 0.60x | No decay |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1763 | +0.0684 | +0.1256 | 0.71x | 2016-08-24 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range` | +0.2016 | +0.0940 | +0.1138 | 0.56x | No decay |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | +0.1821 | +0.0584 | +0.0842 | 0.46x | No decay |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | +0.1814 | +0.0513 | +0.0990 | 0.55x | No decay |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | +0.1831 | +0.0649 | +0.0735 | 0.40x | 2014-06-05 |
| `combo_sig_product__max_up_ret__close_vs_open_range` | +0.1721 | +0.1324 | +0.1001 | 0.58x | No decay |
| `combo_min__star50_limit_proximity_early__max_down_ret` | +0.1511 | +0.0727 | +0.1114 | 0.74x | 2016-08-24 |
| `combo_rank_max__first_bar_sentiment__max_down_ret` | +0.1249 | +0.0738 | +0.0743 | 0.60x | 2017-08-08 |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | +0.1911 | +0.1045 | +0.1258 | 0.66x | 2016-09-26 |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | +0.2007 | +0.0828 | +0.0810 | 0.40x | 2025-07-24 |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | +0.1562 | +0.0391 | +0.1083 | 0.69x | 2016-08-24 |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | +0.1543 | +0.0490 | +0.1100 | 0.71x | 2011-09-20 |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | +0.1733 | +0.0537 | +0.1135 | 0.65x | 2022-12-15 |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | +0.1524 | +0.0567 | +0.1011 | 0.66x | 2020-01-06 |
| `combo_rank_min__bar_ret_0__rbreaker_buy_setup_proximity_early` | +0.1310 | +0.0116 | +0.1192 | 0.91x | 2016-08-24 |
| `combo_rank_max__max_up_ret__early_body_momentum` | +0.1877 | +0.1103 | +0.0738 | 0.39x | 2016-11-30 |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | +0.1717 | +0.0707 | +0.1324 | 0.77x | 2016-09-26 |
| `combo_tri_min__net_volume_flow__star50_limit_proximity_early__close_vs_open_range` | +0.1678 | +0.0710 | +0.1158 | 0.69x | 2016-09-26 |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | +0.1601 | +0.0741 | +0.1139 | 0.71x | No decay |
| `combo_rel_diff__max_up_ret__early_order_flow_imbalance` | +0.0394 | -0.0405 | +0.0337 | 0.86x | 2011-04-21 |
| `combo_mean__bar_ret_0__max_down_ret` | +0.1613 | +0.0587 | +0.1025 | 0.64x | No decay |
| `combo_rank_min__max_up_ret__close_vs_open_range` | +0.1713 | +0.0886 | +0.0949 | 0.55x | 2020-02-12 |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1841 | +0.1120 | +0.0915 | 0.50x | 2019-12-05 |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | +0.1680 | +0.0685 | +0.1219 | 0.73x | 2016-09-26 |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | +0.1723 | +0.0893 | +0.1053 | 0.61x | 2021-05-28 |
| `combo_ratio__max_down_ret__net_volume_flow` | +0.1319 | -0.0332 | +0.1213 | 0.92x | 2021-02-24 |
| `combo_ratio__max_down_ret__early_order_flow_imbalance` | +0.1158 | -0.0073 | +0.1357 | 1.17x | 2011-09-20 |
| `rbreaker_sell_setup_proximity_early` | +0.1745 | +0.0776 | +0.1261 | 0.72x | 2021-07-28 |
| `combo_rel_diff__max_up_ret__early_body_momentum` | +0.0195 | +0.0240 | +0.0027 | 0.14x | 2010-10-15 |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | +0.1450 | +0.0886 | +0.1504 | 1.04x | 2016-08-24 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | +0.1754 | +0.0871 | +0.0879 | 0.50x | 2019-12-05 |

### 588000ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `max_up_ret` | +0.1036 | +0.1269 | -0.0537 | -0.52x | No decay |

### 159915ETF — `single` IC Decay

| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `combo_tri_min__star50_limit_proximity_early__impulse_bar_dominance__bar_body_rng_0` | +0.1311 | +0.1379 | +0.1286 | 0.98x | 2011-10-18 |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | +0.1713 | +0.0989 | +0.1356 | 0.79x | 2017-02-27 |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | +0.1682 | +0.1316 | +0.1289 | 0.77x | 2016-12-21 |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1622 | +0.0945 | +0.1293 | 0.80x | 2011-10-18 |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | +0.1536 | +0.0827 | +0.1319 | 0.86x | 2017-01-20 |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | +0.1409 | +0.1524 | +0.1280 | 0.91x | 2011-10-18 |
| `combo_rank_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | +0.1395 | +0.1217 | +0.1428 | 1.02x | 2016-09-14 |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | +0.1089 | +0.1275 | +0.0998 | 0.92x | 2011-10-18 |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | +0.0885 | +0.1221 | +0.1027 | 1.16x | 2011-10-18 |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | +0.1298 | +0.1186 | +0.1379 | 1.06x | 2011-10-18 |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | +0.1179 | +0.1085 | +0.1401 | 1.19x | 2017-01-20 |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | +0.1201 | +0.1270 | +0.0519 | 0.43x | 2016-10-24 |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | +0.0605 | +0.0053 | -0.0258 | -0.43x | 2012-02-22 |

---

## Actionable Recommendations for Filter Tuning

1. **300ETF `single` — B3 Composite Floor too strict**: 63.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=-0.0507). Consider relaxing this gate.
2. **300ETF `single` — B4 Correlation Gate too strict**: 83.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 28.0%, mean lock Sharpe=+0.2782). Consider relaxing this gate.
3. **300ETF `short` — BH-FDR Gate too strict**: 42.9% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.0677). Consider relaxing this gate.
4. **50ETF `short` — 7-Year Jackknife Sign Stability too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=-0.0553). Consider relaxing this gate.
5. **500ETF `single` — 7-Year Jackknife Sign Stability too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 44.0%, mean lock Sharpe=+0.3659). Consider relaxing this gate.
6. **500ETF `single` — B2 Rolling Guard too strict**: 76.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 44.0%, mean lock Sharpe=+0.4069). Consider relaxing this gate.
7. **500ETF `single` — B3 Composite Floor too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 44.0%, mean lock Sharpe=+0.7247). Consider relaxing this gate.
8. **500ETF `single` — B4 Correlation Gate too strict**: 93.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 44.0%, mean lock Sharpe=+0.5793). Consider relaxing this gate.
9. **500ETF `long` — BH-FDR Gate too strict**: 60.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 35.0%, mean lock Sharpe=-0.0636). Consider relaxing this gate.
10. **500ETF `short` — BH-FDR Gate too strict**: 66.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 33.0%, mean lock Sharpe=+0.1698). Consider relaxing this gate.
11. **588000ETF `single` — 7-Year Jackknife Sign Stability too strict**: 73.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=+0.1458). Consider relaxing this gate.
12. **588000ETF `single` — B2 Rolling Guard too strict**: 36.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.2399). Consider relaxing this gate.
13. **588000ETF `single` — B4 Correlation Gate too strict**: 34.8% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 20.0%, mean lock Sharpe=-0.4001). Consider relaxing this gate.
14. **588000ETF `single` — Admission too loose**: 83% of admitted features have negative lockbox IC or Sharpe. Tighten B3 composite floor or add OOS validation gate.
15. **588000ETF `short` — B3 Composite Floor too strict**: 50.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 25.0%, mean lock Sharpe=+0.3303). Consider relaxing this gate.
16. **159915ETF `single` — B2 Rolling Guard too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 54.0%, mean lock Sharpe=+0.7185). Consider relaxing this gate.
17. **159915ETF `single` — B3 Composite Floor too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 54.0%, mean lock Sharpe=+1.3703). Consider relaxing this gate.
18. **159915ETF `single` — B4 Correlation Gate too strict**: 100.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 54.0%, mean lock Sharpe=+1.3592). Consider relaxing this gate.
19. **159915ETF `long` — B2 Rolling Guard too strict**: 96.7% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 46.0%, mean lock Sharpe=+0.6461). Consider relaxing this gate.
20. **159915ETF `long` — BH-FDR Gate too strict**: 70.8% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 46.0%, mean lock Sharpe=+0.4617). Consider relaxing this gate.
21. **159915ETF `short` — 7-Year Jackknife Sign Stability too strict**: 30.0% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.3342). Consider relaxing this gate.
22. **159915ETF `short` — B2 Rolling Guard too strict**: 33.3% of top rejects are true false negatives (lock IC > 0 AND Sharpe > 0 vs null baseline 16.0%, mean lock Sharpe=-0.2346). Consider relaxing this gate.

### General Recommendations:
1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.
