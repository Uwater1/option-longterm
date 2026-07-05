# Feature Pruning Plan — Day-Model

Goal: cut dead weight from `build_features.py` / `features_extra.py` before mining new features.
Rationale: 238 candidates vs ~2200 selection-train rows already thin. Every dead feature in
the pool costs BH-FDR power (more tests = worse threshold), costs CSS clustering compute,
and dilutes VIF pruning. Cutting first buys headroom for mining later.

Data source: active-feature lists across 4-5 independent train_model.py runs per ETF
(pre-nested-CV FDR=0.40 era + post-nested-CV FDR=0.15/MCP era). Frequency = how many
independent runs had the feature non-zero-weight (active), not just stability-selected.

---

## Tier 1 — Core signal, never touch, feature-engineer variants of these first

Appear active in ALL runs for their ETF. This is your actual alpha, everything else is noise
until proven otherwise.

| ETF | Feature | Hit rate |
|---|---|---|
| 50  | ... | ... | (to be added)
| 300 | `bar_ret_0`, `northbound_net`, `vix_iv_spread`, `iv_diff_1d`, `intraday_autocorr`, `inside_bar_failure_bull`, `consecutive_higher_highs`, `yesterday_early_vwap_dev`, `yesterday_am_return` | 4/4 |
| 500 | `yesterday_intraday_close_position` | 4/4 |
| 588000 | `max_up_ret`, `volume_weighted_price_position` | 4/4 |
| 159915 | `max_up_ret`, `gap_pct`, `yesterday_early_vwap_dev`, `inside_bar_failure_bull`, `yesterday_gap_pct`, `bar_ret_0`, `yesterday_day_vwap_dev` | 5/5 |

Cross-ETF overlap on latest run also flags `pullback_depth_max` (4/4 ETFs), `max_up_ret`/`max_down_ret`/`volume_weighted_price_position`/`yesterday_day_kurtosis` (3/4 ETFs) as
generically strong across assets — good candidates for interaction-term / multi-timeframe
variants when you do start mining.

**Action**: none. Do not prune. Prioritize these families when mining new features
(e.g. `bar_ret_0` at other lookback lengths, VWAP-deviation variants, kurtosis at other windows).

---

## Tier 2 — Marginal, appears 2-3/4 runs, watch not cut yet

Real signal some of the time, sensitive to screen/regularization config. Keep, but tag for
re-review after the MCP-sparsity bug (γ range) and plateau-selector bug are fixed — current
frequency counts are contaminated by those two known-broken runs (D/E), so don't trust this
tier's numbers until re-run clean.

Examples: `capital_net_ratio`, `volume_concentration`, `yesterday_day_vwap_dev` (300ETF),
`bar_vwap_dev_1/2`, `capital_buy_volume`, `sma100_dist` (500ETF), `volume_percentile_20d`
(588000ETF), `sma100_dist`, `bar_vol_5`, `volume_concentration` (159915ETF).

**Action**: hold. Re-audit after pipeline fixes, before any pruning decision.

---

## Tier 3 — Prune candidates: 1/4 or 1/5 hit rate, one-off appearances

Showed up active in exactly one run, never again despite screening surviving in later runs
too (i.e. it was available to be picked and wasn't). This is the "selected once by a
noisy trial, never again" pattern — the single most reliable dead-weight signal you have.

Long tail per ETF (full list from frequency dump), e.g.:
- 300ETF: `total_balance`, `range_expansion_ratio`, `capital_net_value`, `short_balance_quantity`, `northbound_sell`, `bar_body_rng_0`, `bar_vwap_dev_2`, `trend_strength_intraday`
- 500ETF: `early_skew`, `bar_rng_0`, `yesterday_early_trend`, `vol5`, `iv`, `bar_body_rng_2`, `vwap_slope_intraday`, `close_vs_open_range`, `yesterday_day_pm_am_vol_ratio`, `yesterday_first_30min_return`, `bb_width`, `total_path_length`, `iv_vol_ratio`
- 588000ETF: `late_bar_momentum`, `yesterday_early_range`, `upper_wick_dominance`, `roc60`, `volume_acceleration`, `num_up_bars`, `pullback_depth_ratio`, `vol_ratio_10_60`, `bar_ret_2`
- 159915ETF: `first_bar_sentiment`, `yesterday_day_close_pos`, `early_doji_count`, `vix_iv_ratio`, `rsi_opening`, `bar_vwap_dev_2`

**Do not delete yet based on this alone** — one-off appearance across 4-5 runs on a
100-200 trial search with known-buggy MCP/plateau selection is weak evidence by itself.
Treat as *candidates*, confirm below.

---

## Confirmation procedure before deleting anything

1. **Fix known bugs first** (MCP γ-range sparsity collapse, plateau-selector neighbor-count
   bug). Re-run all 4 ETFs clean, 2 more independent seeds. You need runs where the
   selector is actually working before frequency counts mean anything.
2. **Pull raw screening pass/fail per feature per run** from `cache_select_*.joblib`
   (`screen_mask`, `p_vals`). This plan only has visibility into *active* (non-zero weight)
   features from REPORT.md; it can't see which features never even survived BH-FDR
   screening across runs. Cross-reference: a feature that (a) never active in 5+ clean runs
   AND (b) fails BH-FDR screen in most of those runs is a much stronger deletion candidate
   than one that passes screening but never gets weight.
3. **Deprecate, don't delete.** Move candidate features to a `DEPRECATED` list in
   `features_extra.py`, keep the JIT code but exclude from `FEATURES` registry. Re-run
   full suite, confirm CV/PBO/deflated-Val metrics don't regress with smaller candidate pool
   (expect them to *improve slightly* — fewer tests, tighter BH-FDR effective threshold).
4. **Physically remove** only after 1 clean confirmation run shows no regression. Keep a
   changelog entry (feature name, last-active run, reason) in case you want it back later —
   Chinese market regimes shift, "useless in 2024-26 regime" isn't "useless forever."

## Secondary benefit of pruning

Fewer candidate features directly loosens the multiple-testing burden inside BH-FDR
(FDR=0.15 or 0.40 threshold interacts with total test count `m` — fewer `m` at fixed FDR
means a real signal has an easier bar to clear, and your fallback-top-50 trigger on
300ETF this run [WARNING flag, only 15 passed at FDR=0.15] happens less often). This is a
free power gain, not just housekeeping.