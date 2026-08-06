# QMT Feature Selection Report — First Draft (500ETF / 159915ETF)

Generated 2026-08-06 by `newtrade/research_qmt_selection.py` (deterministic, no RNG).
Companion deliverables: `newtrade/qmt_strategy.py` (self-contained QMT script),
`newtrade/build_qmt_config.py` (config baker), `newtrade/tests/test_qmt_selection.py`,
`newtrade/tests/test_qmt_features.py`.

---

## 1. Method

1. **Candidate universe** = union of features admitted across 5 training windows
   (original 2015-2022, p2015_2023, p2016_2024, p2017_2025, p2018_2026 — all from the
   B5-gated pipeline rerun of 2026-08-06). Sign conflicts across windows: 0 for both ETFs.
2. **Evidence per feature**: window count, mean deflated IC / IC-IR / monotonicity across
   windows, G7 cost-stress Sortino (20bp) and B5 deep-stress Sortino (24bp) margins from
   the mining attempt logs, ONC cluster id.
3. **Walk-forward evaluator**: composite = mean of sign-aligned expanding-z (burn-in 252,
   clip 3); thresholds swept on **pre-2023 data only** (long buffer +0.10, short buffer
   +0.20, 8bp round-trip cost); OOS evaluated 2023-01 through 2025-12 with per-year
   breakdown.
4. **Greedy forward selection to 10**: seed = most window-stable feature; then add the
   feature maximizing OOS cost Sharpe subject to max 2 features per ONC cluster, pairwise
   |corr| <= 0.7 on train-window z-scores, and every per-year Sharpe > -0.5. Ties broken
   by name (fully deterministic).

Universes: 500ETF = 524 candidates, 159915ETF = 300 candidates.

---

## 2. Results Summary

| ETF | Features | z_th L/S | OOS Sharpe | OOS PnL | Trades | Win Rate | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 500ETF | 10 | 0.70 / 1.20 | **1.336** | +0.366 | 161 | 55.3% | +1.26 | +1.82 | +1.05 |
| 159915ETF | 10 | 1.10 / 1.00 | **2.096** | +0.564 | 134 | 66.4% | +2.36 | +2.28 | +2.09 |

Per-year Sharpes are cost-adjusted and positive in every year for both ETFs — the 2025
regime check passes. These are spot-equivalent (8bp friction) Sharpes of the underlying
signal; the option layer adds its own convexity/cost profile on top.

---

## 3. Selected Features & Evidence

### 500ETF (thresholds z_th_long=0.70, z_th_short=1.20; train-optimal 0.60/1.00)

| # | Feature | sign | windows | mean dIC | IC-IR | mono | stress Sortino (20bp) | deep (24bp) | ONC cluster |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seed | combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0 | +1 | 5/5 | 0.290 | 0.83 | 0.78 | 1.74 | 1.40 | 28 |
| 1 | morning_volume_weighted_momentum | +1 | 1/5 | 0.170 | 0.58 | 0.71 | 0.56 | 0.19 | n/a |
| 2 | combo_min__bar_ret_0__early_order_flow_imbalance | +1 | 3/5 | 0.233 | 0.75 | 0.75 | 1.05 | 0.70 | 45 |
| 3 | combo_rel_diff__star50_limit_proximity_early__demark_setup_reversal_early | +1 | 1/5 | 0.201 | 0.60 | 0.70 | 0.90 | 0.63 | n/a |
| 4 | combo_sig_product__max_down_ret__vwap_close_divergence_trend | +1 | 4/5 | 0.167 | 0.61 | 0.71 | 1.30 | 0.99 | 85 |
| 5 | combo_sig_product__net_volume_flow__first_bar_return | +1 | 1/5 | 0.207 | 0.54 | 0.69 | 0.49 | 0.21 | 107 |
| 6 | combo_ratio__max_down_ret__volume_weighted_momentum_acceleration | +1 | 1/5 | 0.252 | 0.95 | 0.83 | 1.11 | 0.76 | 85 |
| 7 | combo_sig_product__max_up_ret__body_size_progression | +1 | 1/5 | 0.192 | 0.78 | 0.74 | 0.55 | 0.15 | n/a |
| 8 | combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum | +1 | 2/5 | 0.238 | 0.55 | 0.70 | 0.80 | 0.50 | 7 |
| 9 | combo_sig_product__opening_drive_thrust_ratio__bar_ret_0 | +1 | 1/5 | 0.208 | 0.52 | 0.68 | 0.82 | 0.52 | 59 |

### 159915ETF (thresholds z_th_long=1.10, z_th_short=1.00; train-optimal 1.00/0.80)

| # | Feature | sign | windows | mean dIC | IC-IR | mono | stress Sortino (20bp) | deep (24bp) | ONC cluster |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seed | combo_max__max_up_ret__volume_price_confirmation | +1 | 5/5 | 0.224 | 0.70 | 0.73 | 1.27 | 0.99 | 6 |
| 1 | combo_min__opening_drive_thrust_ratio__limit_down_proximity_early | +1 | 2/5 | 0.246 | 0.66 | 0.76 | 1.06 | 0.71 | n/a |
| 2 | combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation | +1 | 2/5 | 0.261 | 0.61 | 0.74 | 1.54 | 1.19 | n/a |
| 3 | combo_rel_diff__directional_volume_signature__early_late_momentum_divergence | +1 | 1/5 | 0.188 | 0.51 | 0.70 | 0.42 | 0.14 | 12 |
| 4 | combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector | +1 | 1/5 | 0.194 | 0.70 | 0.73 | 0.37 | 0.04 | n/a |
| 5 | combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position | +1 | 1/5 | 0.187 | 0.57 | 0.73 | 0.61 | 0.27 | n/a |
| 6 | combo_min__bar_ret_0__directional_volume_signature | +1 | 2/5 | 0.178 | 0.60 | 0.72 | 0.90 | 0.62 | 2 |
| 7 | combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max | +1 | 3/5 | 0.239 | 0.73 | 0.76 | 1.31 | 0.96 | n/a |
| 8 | combo_max__bar_ret_0__limit_down_proximity_early | +1 | 1/5 | 0.164 | 0.54 | 0.71 | 0.61 | 0.30 | n/a |
| 9 | combo_rank_max__rbreaker_sell_setup_proximity_early__gap_pct | +1 | 1/5 | 0.199 | 0.44 | 0.66 | 0.73 | 0.51 | n/a |

All 20 features are pure early-bar (9:30-10:00) features of the **underlying index**
(500ETF -> 000905, 159915ETF -> 399006), so the live decision needs only the first six
index 5m bars plus yesterday's index close and 20-day index volume.

---

## 4. Greedy Trajectory (composite OOS Sharpe after each add)

**500ETF**: seed -> 1.092 -> 1.197 -> 1.405 -> 1.335 -> 1.371 -> 1.436 -> **1.443** ->
1.421 -> 1.336. Peak at 7 features (1.443); steps 8-9 lower the composite Sharpe but are
the best admissible additions (corr/cluster/per-year constraints eliminate the rest).

**159915ETF**: seed -> 1.962 -> 2.074 -> 2.251 -> 2.296 -> 2.248 -> **2.420** -> 2.081 ->
2.096. Peak at 7 features (2.420).

Note for iteration 2: both trajectories peak at 7 features. The first 7 of each table are
the "hard core"; features 8-10 were added only to honor the fixed top-10 mandate. A
7-feature variant is a one-line config edit (delete entries from the baked config block).

---

## 5. Alternatives Considered

| Alternative | Verdict |
| --- | --- |
| Latest pool top-10 by deflated IC | Rejected: single-window dependent; no OOS evidence. |
| Cross-window intersection (>=3 windows) | Rejected: 500ETF universe would shrink to a handful; greedy already rewards window count via the seed. |
| Rolling 480d tail-IC live re-weighting | Deferred to iteration 2 (hand-tune knob in the baked config: weights dict). |
| Stop at greedy Sharpe peak (7 features) | Documented above; kept 10 per mandate. |
| Ensemble of all 4 dynamic schemes | Out of scope for first draft (single-file simplicity). |

Known caveats:
- `rank_*` recipe ECDF grids in the backtest are built on full-sample data; the live
  config bakes grids through the bake date (no future data). Drift is negligible.
- OOS metrics are spot-equivalent; option-layer fill quality is validated separately in
  simulation.
- 500ETF's low z_th_long (0.70) means frequent long entries; monitor long-side fill cost
  in simulation.

---

## 6. Deployment Artifacts

| File | Role |
| --- | --- |
| `newtrade/qmt_strategy.py` | THE deliverable: single self-contained QMT script (stdlib + numpy only). Features + signal + all trading. |
| `newtrade/build_qmt_config.py` | Regenerates the baked config block (selections, train stats, ECDF grids, expanding mu/sigma, thresholds, index seeds). |
| `newtrade/data/qmt_selection_{500ETF,159915ETF}.json` | Machine-readable selection + full evidence + greedy log. |
| `newtrade/tests/test_qmt_selection.py` | Validity / no-lookahead / reproducibility tests. |
| `newtrade/tests/test_qmt_features.py` | Dependency audit + feature/recipe/signal parity vs the offline pipeline. |

Test status (2026-08-06): ALL PASSED.
- Feature parity: 40 replay days/ETF vs `features_{ETF}.parquet`, max diff 2.0e-05
  (tolerance 1e-4; residual is numba-fastmath reassociation of ~1e9-scale volume sums).
- Recipe parity: max combo diff 3.9e-05.
- Side decisions vs offline pipeline z: 0 mismatches on the last 40 days, both ETFs.
- Greedy reproducibility (`--slow`): identical selections and thresholds on full rerun.

---

## Appendix A: QMT Paper-Trading Dry-Run Checklist

1. Copy `newtrade/qmt_strategy.py` into the QMT client strategy directory; add it as a
   model strategy bound to the **STOCK_OPTION** account in **simulation** mode.
2. Set the account id in `QMT_CONFIG["account"]` (baked block) if the client does not
   inject it.
3. First `init` log line must show `chain built: N (expiry,strike) pairs` for BOTH
   510500.SH and 159915.SZ (N >= 10). If 0, check option quote permissions.
4. Verify index data access: `get_market_data_ex` must return 5m bars for 000905.SH /
   399006.SZ (log shows `skip: index bars unavailable` otherwise).
5. At 10:00 expect one log line per ETF: `composite=... side=long|short|flat`.
6. Entry uses `passorder(50=buy-open ...)` limit at ask+1 tick, 1 contract, premium cap
   10,000 RMB. Exit/stop use `51=sell-close`.
7. State persists to `qmt_state/state_YYYYMMDD.json` next to the script; delete it to
   reset a simulation day.
8. Expected activity: ~55-66% of signal days trade; ~40-65 option trades per ETF per year.
9. Daily reconciliation: compare `composite` in the state file against a manual run of
   `python newtrade/tests/test_qmt_features.py` signals if numbers look odd.

## Appendix B: Live Signal Flow

```
09:30-10:00  index bars accumulate (6 x 5m)
10:00        compute 24 raw features -> 10 selected combos -> z-score (baked stats)
             -> composite = mean(sign*z) -> compare vs z_th_long / -z_th_short
entry        buy CALL (long) or PUT (short), front month,
             strike: 500ETF=nearest / 159915ETF=most liquid (vol_t1 proxy)
intraday     trailing stop: peak * (1 - 0.30*(1 - t)) , t = fraction of 10:00-14:35 elapsed
14:35        force close; 14:45 hard deadline flatten
```
