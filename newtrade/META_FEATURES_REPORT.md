# Meta-Model Feature Feasibility Report

Pre-check for TODO #2: does ANY factor predict the 13:30→14:35 continuation (`hold_benefit_1330`) on in-sample production trades? Target is position-signed; all intraday features are direction-normalized. Discovery is IS-only; OOS is a stability mirror, never used for selection.

Feature categories: **s** snapshot (z_composite, running P&L, vols), **f** day-model-new admitted-pool factors (expanding z-score, sign-aligned, zero-lookahead), **u** 13:30-unique intraday (noon gap, reopen drift, drawdown, range position, trend consistency, realized vol, reopen volume ratio), **x** price-action interactions.

Caveat: pool membership was selected with data through 2024+, so `f_` values carry the same pool-selection lookahead as the labels themselves.

## 1. Data

| ETF | IS trades | OOS trades | #pool (f) | #unique (u) | #interact (x) | #snapshot (s) |
|---|---|---|---|---|---|---|
| 300ETF | 123 | 39 | 26 | 8 | 8 | 7 |
| 500ETF | 209 | 145 | 317 | 8 | 8 | 7 |
| 159915ETF | 440 | 249 | 37 | 8 | 8 | 7 |

Null benchmark: with n trades, Spearman SE ≈ 1/√n, so ~5% of features exceed |IC| > 1.96/√n by chance (n=123 → 0.18, n=209 → 0.14, n=440 → 0.09).

## 2. 300ETF

**Null test (IS).** Observed max |IC| = **0.280** vs permutation max-|IC| 95th percentile = 0.270 (500 shuffles); family-wise p = 0.024. SIGNAL PRESENT beyond chance.

**Exceedances.** 10/49 features with p<0.05 & |IC|>0.05 (chance expectation ≈ 2); 16 features with |IC| > 0.10.

**Top-15 features by |IS IC|** (target = hold_benefit_1330):

| Feature | Cat | IS IC | p | IS IC (binary cut) | OOS IC | IS→OOS stable |
|---|---|---|---|---|---|---|
| f_combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position | pool factor | +0.280 | 0.002 | -0.257 | -0.130 |  |
| u_trend_consistency | 13:30-unique | +0.261 | 0.004 | -0.212 | 0.284 | yes |
| u_range_position | 13:30-unique | +0.241 | 0.007 | -0.182 | 0.076 | yes |
| f_combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position | pool factor | +0.210 | 0.019 | -0.238 | -0.072 |  |
| f_combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration | pool factor | +0.209 | 0.020 | -0.213 | -0.058 |  |
| x_pnl_persist | interaction | +0.206 | 0.022 | -0.133 | -0.161 |  |
| u_vol_to_now | 13:30-unique | +0.191 | 0.034 | -0.131 | 0.037 | yes |
| x_abs_z | interaction | +0.191 | 0.035 | -0.180 | 0.134 | yes |
| first30_vol | snapshot | +0.185 | 0.041 | -0.087 | 0.038 | yes |
| morning_vol | snapshot | +0.178 | 0.049 | -0.117 | 0.030 |  |
| f_combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position | pool factor | +0.165 | 0.068 | -0.213 | -0.026 |  |
| u_vol_ratio_reopen | 13:30-unique | +0.147 | 0.105 | -0.124 | 0.047 | yes |
| z_composite | snapshot | +0.131 | 0.149 | -0.139 | -0.036 |  |
| f_combo_min__opening_drive_thrust_ratio__max_up_ret | pool factor | +0.116 | 0.202 | -0.141 | -0.176 |  |
| f_combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0 | pool factor | +0.116 | 0.203 | -0.157 | -0.025 |  |

**Category summary** (IS):

| Category | #features | Best feature | Best IC | #p<0.05 |
|---|---|---|---|---|
| snapshot | 7 | first30_vol | +0.185 | 2 |
| pool factor | 26 | f_combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position | +0.280 | 3 |
| 13:30-unique | 8 | u_trend_consistency | +0.261 | 3 |
| interaction | 8 | x_pnl_persist | +0.206 | 2 |

**Quintile buckets** (mean hold-benefit bps by IS quintile, Q1=lowest feature value; OOS uses IS edges):

| Feature | IS monotonic | IS Q1..Q5 bps | OOS Q1..Q5 bps |
|---|---|---|---|
| f_combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position | no | -9.1 / -14.6 / 27.0 / 43.4 / 43.7 | 11.7 / -19.7 / -15.5 / -10.4 / -3.2 |
| u_trend_consistency | no | -5.3 / -1.1 / -2.5 / 25.1 / 66.3 | -11.1 / -20.5 / -40.3 / -7.9 / 9.1 |
| u_range_position | no | 5.2 / -11.3 / 36.1 / 3.0 / 54.1 | -13.5 / -54.3 / 20.1 / -13.1 / 10.5 |

**Long/short consistency** (IS IC by side):

| Feature | n long | IC long | n short | IC short | Same sign |
|---|---|---|---|---|---|
| f_combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position | 93 | 0.236 | 30 | 0.536 | yes |
| u_trend_consistency | 93 | 0.159 | 30 | 0.506 | yes |
| u_range_position | 93 | 0.255 | 30 | 0.207 | yes |
| f_combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position | 93 | 0.187 | 30 | 0.535 | yes |
| f_combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration | 93 | 0.172 | 30 | 0.501 | yes |

## 2. 500ETF

**Null test (IS).** Observed max |IC| = **0.136** vs permutation max-|IC| 95th percentile = 0.230 (500 shuffles); family-wise p = 0.856. No family-wise signal beyond chance.

**Exceedances.** 1/340 features with p<0.05 & |IC|>0.05 (chance expectation ≈ 17); 3 features with |IC| > 0.10.

**Top-15 features by |IS IC|** (target = hold_benefit_1330):

| Feature | Cat | IS IC | p | IS IC (binary cut) | OOS IC | IS→OOS stable |
|---|---|---|---|---|---|---|
| u_vol_ratio_reopen | 13:30-unique | +0.136 | 0.049 | -0.101 | -0.029 |  |
| u_trend_consistency | 13:30-unique | +0.113 | 0.102 | -0.060 | 0.065 | yes |
| u_noon_gap | 13:30-unique | -0.104 | 0.133 | +0.095 | 0.057 |  |
| f_combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early | pool factor | -0.099 | 0.156 | +0.103 | -0.082 | yes |
| f_combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0 | pool factor | -0.098 | 0.159 | +0.099 | -0.078 | yes |
| f_combo_mean__star50_limit_proximity_early__shaved_bar_trend_conviction | pool factor | -0.094 | 0.177 | +0.094 | -0.078 | yes |
| f_combo_sig_product__rbreaker_sell_setup_proximity_early__early_body_momentum | pool factor | -0.092 | 0.184 | +0.058 | -0.168 | yes |
| x_abs_z | interaction | +0.092 | 0.185 | -0.036 | 0.017 |  |
| f_combo_rank_max__early_order_flow_imbalance__max_down_ret | pool factor | -0.092 | 0.185 | +0.047 | -0.084 | yes |
| f_combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow | pool factor | -0.092 | 0.187 | +0.103 | -0.101 | yes |
| f_combo_rank_min__volatility_expansion_trend_vector__star50_limit_proximity_early | pool factor | -0.091 | 0.189 | +0.103 | -0.110 | yes |
| f_combo_mean__net_volume_flow__star50_limit_proximity_early | pool factor | -0.090 | 0.194 | +0.087 | -0.120 | yes |
| f_combo_tri_mean__volatility_expansion_trend_vector__early_body_momentum__star50_limit_proximity_early | pool factor | -0.089 | 0.201 | +0.083 | -0.134 | yes |
| f_combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0 | pool factor | -0.088 | 0.206 | +0.115 | -0.086 | yes |
| f_combo_mean__rbreaker_sell_setup_proximity_early__close_vs_open_range | pool factor | -0.086 | 0.218 | +0.097 | -0.132 | yes |

**Category summary** (IS):

| Category | #features | Best feature | Best IC | #p<0.05 |
|---|---|---|---|---|
| snapshot | 7 | morning_vol | +0.070 | 0 |
| pool factor | 317 | f_combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early | -0.099 | 0 |
| 13:30-unique | 8 | u_vol_ratio_reopen | +0.136 | 1 |
| interaction | 8 | x_abs_z | +0.092 | 0 |

**Quintile buckets** (mean hold-benefit bps by IS quintile, Q1=lowest feature value; OOS uses IS edges):

| Feature | IS monotonic | IS Q1..Q5 bps | OOS Q1..Q5 bps |
|---|---|---|---|
| u_vol_ratio_reopen | no | 5.6 / 4.9 / -0.5 / 10.4 / 17.9 | 7.9 / 9.3 / -8.9 / -5.3 / 20.0 |
| u_trend_consistency | no | -2.8 / 13.2 / -1.1 / -7.7 / 33.4 | n/a / 23.6 / 0.3 / -6.2 / 8.4 |
| u_noon_gap | no | 37.6 / -30.9 / n/a / 1.4 / -1.1 | -0.4 / -48.8 / n/a / 3.2 / 17.7 |

**Long/short consistency** (IS IC by side):

| Feature | n long | IC long | n short | IC short | Same sign |
|---|---|---|---|---|---|
| u_vol_ratio_reopen | 175 | 0.141 | 34 | 0.123 | yes |
| u_trend_consistency | 175 | 0.093 | 34 | 0.220 | yes |
| u_noon_gap | 175 | -0.037 | 34 | -0.287 | yes |
| f_combo_rank_min__trend_bar_close_consistency__star50_limit_proximity_early | 175 | -0.046 | 34 | -0.301 | yes |
| f_combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0 | 175 | -0.053 | 34 | -0.183 | yes |

## 2. 159915ETF

**Null test (IS).** Observed max |IC| = **0.153** vs permutation max-|IC| 95th percentile = 0.150 (500 shuffles); family-wise p = 0.040. SIGNAL PRESENT beyond chance.

**Exceedances.** 7/60 features with p<0.05 & |IC|>0.05 (chance expectation ≈ 3); 5 features with |IC| > 0.10.

**Top-15 features by |IS IC|** (target = hold_benefit_1330):

| Feature | Cat | IS IC | p | IS IC (binary cut) | OOS IC | IS→OOS stable |
|---|---|---|---|---|---|---|
| x_dd_x_vol | interaction | -0.153 | 0.001 | +0.043 | 0.245 |  |
| u_drawdown_from_peak | 13:30-unique | -0.140 | 0.003 | +0.041 | 0.236 |  |
| u_vol_to_now | 13:30-unique | +0.133 | 0.005 | -0.020 | -0.130 |  |
| morning_vol | snapshot | +0.130 | 0.006 | -0.033 | -0.118 |  |
| x_z_x_pnl1330 | interaction | -0.105 | 0.028 | +0.096 | 0.024 |  |
| first30_vol | snapshot | +0.099 | 0.039 | -0.001 | -0.117 |  |
| u_range_position | 13:30-unique | -0.094 | 0.048 | +0.067 | 0.172 |  |
| pnl_at_1330 | snapshot | -0.069 | 0.149 | +0.072 | 0.151 |  |
| pnl_at_1305 | snapshot | -0.062 | 0.197 | +0.064 | 0.126 |  |
| f_combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0 | pool factor | -0.059 | 0.216 | +0.010 | 0.066 |  |
| u_trend_consistency | 13:30-unique | +0.059 | 0.220 | +0.029 | 0.043 |  |
| f_combo_min__bar_ret_0__directional_volume_signature | pool factor | +0.056 | 0.237 | -0.055 | -0.058 |  |
| f_combo_min__bar_ret_0__volume_price_confirmation | pool factor | +0.056 | 0.238 | -0.057 | -0.055 |  |
| f_combo_max__opening_drive_thrust_ratio__bar_body_rng_0 | pool factor | -0.055 | 0.249 | +0.023 | -0.026 |  |
| f_combo_rel_diff__directional_volume_signature__early_late_momentum_divergence | pool factor | +0.052 | 0.275 | -0.083 | 0.003 |  |

**Category summary** (IS):

| Category | #features | Best feature | Best IC | #p<0.05 |
|---|---|---|---|---|
| snapshot | 7 | morning_vol | +0.130 | 2 |
| pool factor | 37 | f_combo_ifelse__gap_pct__opening_drive_thrust_ratio__bar_body_rng_0 | -0.059 | 0 |
| 13:30-unique | 8 | u_drawdown_from_peak | -0.140 | 3 |
| interaction | 8 | x_dd_x_vol | -0.153 | 2 |

**Quintile buckets** (mean hold-benefit bps by IS quintile, Q1=lowest feature value; OOS uses IS edges):

| Feature | IS monotonic | IS Q1..Q5 bps | OOS Q1..Q5 bps |
|---|---|---|---|
| x_dd_x_vol | no | 51.3 / 12.5 / 13.4 / 14.4 / -9.2 | -33.4 / -4.7 / 3.4 / 13.0 / 17.6 |
| u_drawdown_from_peak | down | 48.5 / 19.4 / 13.4 / 3.5 / -2.4 | -29.3 / -0.3 / -3.7 / 21.3 / 19.4 |
| u_vol_to_now | no | 2.7 / 8.3 / 8.5 / 6.9 / 55.9 | 8.4 / -0.6 / -0.0 / 10.3 / -21.4 |

**Long/short consistency** (IS IC by side):

| Feature | n long | IC long | n short | IC short | Same sign |
|---|---|---|---|---|---|
| x_dd_x_vol | 312 | -0.197 | 128 | -0.046 | yes |
| u_drawdown_from_peak | 312 | -0.195 | 128 | -0.003 | yes |
| u_vol_to_now | 312 | 0.113 | 128 | 0.161 | yes |
| morning_vol | 312 | 0.111 | 128 | 0.169 | yes |
| x_z_x_pnl1330 | 312 | -0.110 | 128 | -0.069 | yes |

## 3. Pooled scan (3 ETFs, hand-crafted s/u/x features only)

| Feature | Cat | IS IC | p | OOS IC | IS→OOS stable |
|---|---|---|---|---|---|
| u_vol_to_now | 13:30-unique | +0.134 | 0.000 | -0.103 |  |
| morning_vol | snapshot | +0.130 | 0.000 | -0.098 |  |
| first30_vol | snapshot | +0.100 | 0.006 | -0.106 |  |
| x_dd_x_vol | interaction | -0.095 | 0.008 | 0.221 |  |
| u_trend_consistency | 13:30-unique | +0.079 | 0.029 | 0.068 | yes |
| x_z_x_pnl1330 | interaction | -0.072 | 0.045 | -0.031 | yes |
| u_drawdown_from_peak | 13:30-unique | -0.071 | 0.048 | 0.228 |  |
| x_pnl_persist | interaction | +0.065 | 0.070 | -0.129 |  |
| x_gap_confirm | interaction | +0.052 | 0.146 | -0.003 |  |
| u_vol_ratio_reopen | 13:30-unique | +0.051 | 0.155 | -0.023 |  |
| pnl_at_1305 | snapshot | -0.032 | 0.368 | 0.095 |  |
| x_abs_z | interaction | +0.032 | 0.372 | 0.016 |  |

7/23 features with p<0.05 & |IC|>0.05 (chance expectation ≈ 1).

## 4. Findings & verdict

- **300ETF**: family-wise p=0.024 (signal beyond chance), 10 nominally significant features vs 2 expected by chance, max |IC|=0.280 (null 95%: 0.270); of 23 features with |IS IC|>0.08, only 11 keep their sign OOS.
- **500ETF**: family-wise p=0.856 (no family-wise signal), 1 nominally significant features vs 17 expected by chance, max |IC|=0.136 (null 95%: 0.230); of 22 features with |IS IC|>0.08, only 17 keep their sign OOS.
- **159915ETF**: family-wise p=0.040 (signal beyond chance), 7 nominally significant features vs 3 expected by chance, max |IC|=0.153 (null 95%: 0.150); of 7 features with |IS IC|>0.08, only 0 keep their sign OOS.

**Verdict: patterns exist, but they are thin and regime-unstable.** 2/3 ETFs clear the family-wise null test on IS trades, yet only 28/52 (54%) of the |IS IC|>0.08 features keep their sign OOS — the same mean-reversion→momentum flip from META_LABEL_REPORT.md shows up feature-by-feature (e.g. drawdown-from-peak: IS IC -0.14 → OOS +0.24 on 159915ETF; pooled vol features: IS +0.10..+0.13 → OOS -0.10). The few sign-stable features (u_trend_consistency pooled IC ~+0.07-0.08, x_z_x_pnl1330 ~-0.07) are individually too weak to clear costs. A walk-forward meta-model would train on even thinner yearly slices (~60-110 trades/year), so success odds are low.

**Recommendation:** one attempt is defensible ONLY with (a) features restricted to sign-stable, regime-invariant intraday-state candidates (u_trend_consistency, u_range_position, x_z_x_pnl1330, u_noon_gap) — NOT the vol/drawdown features whose sign flips, and NOT raw pool factors (300ETF's top pool factors all flip sign OOS); (b) pooled cross-ETF training to get sample size; (c) the META_LABEL_REPORT.md kill criterion. Otherwise: deprioritize TODO #2 — the evidence says a model would mostly learn the current regime, which is exactly what breaks.

Note the structural difficulty flagged up front: the target is a ~65-minute continuation return conditional on the entry model already having taken a side, so most of the easy directional information is consumed. Any surviving signal must come from intraday state (gap/drift/drawdown/vol) or factor disagreement, and must overcome the IS (mean-reversion) vs OOS (momentum) regime split documented in META_LABEL_REPORT.md.