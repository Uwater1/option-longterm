# Daytrade — Frozen-Linear Intraday Alpha

Rule-based day-trading layer that consumes day-model trained coefficients as **frozen constants** (no runtime ML) and turns them into per-side deployable signals. Each ETF uses one signed frozen score where **sign determines direction** (positive → long, negative → short) and **magnitude determines conviction**. Each side has its own expanding-percentile threshold conditioned on that side's prior history.

Three signal modes are available: **single** (default, proven), **hybrid** (single direction × dual conviction), and **dual** (v2 true independent execution with rank normalisation). The deployed configuration uses **mixed mode** (Phase 4): each ETF × side picks whichever of the three modes maximises **pooled walk-forward Sharpe**. Built by `python -m daytrade.deploy`.

**Calibration is walk-forward** (v4): per-side (threshold, conviction, stop, mode) is re-selected per yearly fold using train-window data only, eliminating the hyperparameter snooping bias of the previous single-split-at-`HOLDOUT_START` calibrator. See §3 "Walk-Forward Calibration" and `walkforward.py`.

---

## 1. Strategy in One Screen

```
  9:30 open
   │
   │  ── collect first (decision_bar+1) bars ──▶  per-ETF DECISION_BAR
   │     {300:3 (9:50), 50:2 (9:45), 500:4 (9:55),
   │      588000:2 (9:45), 159915:4 (9:55)}
   ▼
  Decision bar close  ->  compute score (causal: features use bars [0..decision_bar] only)
   │
   │  1) score = intercept + Σ coefᵢ × featureᵢ           [frozen, day-model trained on trade_return]
   │  2) |score| vs expanding pct over same-side history   [walk-forward]
   │  3) long_model.fires  if score>0 & crosses L_thr
   │     short_model.fires if score<0 & crosses S_thr
   ▼
  Entry @ open of bar (decision_bar + 1)   <- next-bar open after decision (realistic fill)
   │
   │  hold (or exit early via intraday stop-loss, Phase 5)
   ▼
  Exit @ 14:30 (5m bar 41 close, better liquidity than 15:00)
         or @ stop price if intraday stop-loss triggered
```

Target alignment: model trains on `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])` — exactly the trade P&L captured by the backtest. No window mismatch.

Per-side **eligibility guard** (calibration-time): a side deploys only if OOS P&L > 0 AND OOS Sharpe > 0 AND n ≥ 20. If neither side is eligible, the ETF is untradeable.

---

## 2. Commands

```bash
source .venv/bin/activate                              # or system python3 with sklearn/joblib

# End-to-end (recommended after any change)
python -m daytrade.scores        # IC sanity vs day-model report (~5s)
python -m daytrade.calibrate     # per-side grid search → daytrade/data/calibration.json (~3min)
python -m daytrade.report        # deployed backtest + REPORT.md + plots (~10s)

# Full v2 pipeline (all modes → deploy best per side)
python -m daytrade.calibrate --mode single                  # single-mode calibration
python -m daytrade.calibrate --mode hybrid                  # hybrid-mode calibration
python -m daytrade.calibrate --mode dual                    # dual-mode calibration (v2)
python -m daytrade.deploy                                    # pick best mode per side → calibration.json
python -m daytrade.report                                    # generate report with mixed-mode deployment

# Gating-integrated pipeline (recommended; +10.13 total OOS Sharpe over ungated)
python day-model/gating_model.py -e all -t 20 --jobs 5      # train gating models (all variants×selectors, ~100s)
python -m daytrade.calibrate --mode single --sweep-gated    # calibrate ungated + gated for all 3 modes
python -m daytrade.calibrate --mode hybrid --sweep-gated
python -m daytrade.calibrate --mode dual   --sweep-gated
python -m daytrade.deploy                                    # mixed-mode picker now treats {mode}+gated as candidates
python -m daytrade.report

# Gating-only standalone backtest (gate as sole signal — diagnostic, NOT for deployment)
python -m daytrade.gating_only                              # all ETFs, 4% stop, conflict=flat
python -m daytrade.gating_only --no-stop                    # hold to 14:30
python -m daytrade.gating_only --conflict long              # both gates fire → take long

# Ad-hoc inspection
python -m daytrade.rules         # long/short signal counts at defaults
python -m daytrade.rules --mode hybrid  # hybrid-mode signal counts
python -m daytrade.rules --mode dual    # dual-mode signal counts (v2)
python -m daytrade.backtest      # 300ETF smoke test with per-side metrics

# Tune at different cost assumption
python -m daytrade.calibrate --cost-bps 5
python -m daytrade.calibrate --cost-bps 30

# Retrain dual models (after feature changes)
python day-model/train_model.py -e all --side both --trials 100  # train dual models
```

Outputs:
- `daytrade/data/calibration.json` — best per-side configs
- `daytrade/data/results.json` — deployed metrics + cost sweep + cluster confusion
- `daytrade/REPORT.md` — human-readable summary
- `daytrade/plots/{equity_combined,equity_curves,yearly_sharpe}.png`

---

## 3. Architecture

### Per-Side Model Concept

A single frozen score is computed per ETF per day (regression on PM return). The **sign of the score determines side**; the **magnitude determines conviction**. Each side has independent:

- `threshold_pct` — expanding percentile cutoff for "tradable"
- `conviction_pct` — additional conviction floor (typically ≤ threshold)

The expanding percentile for the long side is computed **only over prior positive-score days** (conditional on the long regime). Same for shorts. This conditional thresholding is the key insight: long and short score magnitudes have different distributions, so a symmetric cutoff is sub-optimal.

Long & short are **mutually exclusive by construction** (different score signs), so no conflict resolution is needed.

### Signal Modes (`mode` parameter)

| Mode | Direction | Conviction | Threshold base | Conflict resolution | Status |
|:---|:---|:---|:---|:---|:---|
| **`single`** (default) | sign of single-model score | \|score\| | same-sign history only | not needed (mutually exclusive) | ✅ Proven, deployed |
| **`hybrid`** | sign of single-model score | \|single\| × dual_side_score | combined-conviction history | margin-based (score/threshold) | ✅ Deployed for 159915 Short, 500 Long |
| **`dual`** | each side fires independently | rank-normalised dual score | expanding_pct_rank [0,1] | margin-based (rank/threshold) | ✅ Deployed for 50 Short |

**`mixed` mode** (Phase 4 deployment): each ETF × side uses whichever of single/hybrid/dual maximises OOS Sharpe. Built by `python -m daytrade.deploy`. This is the default deployed configuration.

Dual-model artifacts (`linear_{ETF}_long.joblib` etc.) are trained via `python day-model/train_model.py --side both`. See `improvement_plan.md` for v2 results showing mixed-mode deployment (Phase 4) improves total OOS Sharpe by +3.01 over single-only.

### Gating Integration (v3 — production)

A **big-move gating model** (trained in `day-model/gating_model.py`, see
`day-model/AGENTS.md` §4) acts as a **post-hoc veto filter** over the daytrade
directional signal. On each day the long-gate fires only when a big-up move is
predicted; the short-gate fires only on predicted big-down. Signals are kept
only where the matching gate fires (days with no gate prediction are kept — no
veto). The gate is **not** a standalone alpha — see `GATING_ONLY_REPORT.md`
(gate-only total OOS Sharpe = +9.08 vs gated-daytrade +41.94). Its value is
selectivity: removing low-tradability days where the score fires but the move
won't follow through.

**Plumbing** (single integration chokepoint at `backtest.py` `direction` column):
- `gating_loader.load_gating_mask(etf, side) → pd.Series[date→bool]` loads the
  canonical promoted artifact (`gating_{ETF}_{side}.joblib`) and applies the
  persisted firing probability threshold (p70 of training predictions).
- `backtest_long_short(..., gated=True)` ANDs the mask into `signals["direction"]`
  after `get_long_short_signals` returns.
- `calibrate.py --gated` / `--sweep-gated` runs the grid with gating on (writes
  `calibration_{mode}_gated.json`).
- `deploy.py` `MODE_FILES` includes `{single,hybrid,dual}+gated`; the mixed-mode
  picker auto-adopts the gated variant per side when it wins on OOS Sharpe.
- Each deployed config carries a `gated: bool` flag; `report.py`'s
  `_run_mixed_backtest` splits the `+gated` suffix into `mode=base, gated=True`.

**Result**: gated mixed-mode total **pooled WF Sharpe +39.96** vs ungated
**+30.77** (Δ = **+9.20**); 7 of 10 cells pick a `+gated` config. Run
`python -m daytrade.calibrate --mode single --sweep-gated` (×3 modes) →
`python -m daytrade.deploy` → `python -m daytrade.report` to reproduce.
(Walk-forward v4 numbers; previous single-split headline was +41.94 gated / +31.81 ungated — the ~2 point drop is the hyperparameter selection bias removed.)

### Pipeline Flow

```
day-model/models/linear_{ETF}.joblib   ─┐
day-model/models/scaler_{ETF}.joblib    ├─▶ scores.compute_scores(etf) ─▶ pd.Series[date→score]
day-model/data/features_{ETF}.parquet   ─┘                                            │
                                                                                      ▼
                                          rules.get_long_short_signals(etf, L_thr, L_conv, S_thr, S_conv)
                                                                                      │
                                            per-day: long_fires / short_fires / direction
                                                                                      ▼
                                          backtest.backtest_long_short(etf, ...)
                                                                                      │
                                            entry = open[decision_bar + 1]   <- next-bar open after decision close
                                            exit  = close[EXIT_BAR=41]       (14:30)
                                            net_ret = direction × (exit/entry − 1) − cost
                                                                                      ▼
                                          calibrate.calibrate_all()  →  report.generate()
```

### Eligibility & Scoring

Calibration grid: `threshold_pct ∈ {50,60,70,80,90,95}`, `conviction_pct ∈ {40,50,60,70,80,90}`, run independently for long & short. Selection objective is profit-first composite (per AGENTS.md put convention):
- P&L 35%, FilterLift 30% (selectivity rate, `s5`), Sharpe 15%, MaxDD 10%, WinRate 5%, Placement 5% (trades kept fraction, `1.0 - s5`)
- **Hard per-fold eligibility guard**: train P&L > 0 AND train Sharpe > 0 AND n ≥ 20
- **Deployment gate (new, WF)**: a side deploys only if eligible in ≥ 50% of folds AND pooled WF Sharpe > 0
- **Soft fragility warnings** (non-blocking, transparency only): for each deployed side the calibrator records a `warnings` list flagging any of:
  - `median<=0` — typical pooled WF trade loses money (positive mean carried by heavy-tail winners)
  - `win<=50%` — side loses more often than it wins
  - `n<60` — small sample; high multiple-testing risk from the 6×6 grid search

  These surface in `REPORT.md` §3.6. They do NOT change deployment — investigate before sizing capital.

Selection is **walk-forward** (yearly expanding-window folds, see §3 below) — never on the window used for reporting.

---

## 3. Walk-Forward Calibration (v4 — no look-ahead in selection)

### Why

The runtime signal generation has always been causal (`expanding_pct_masked` /
`expanding_pct_rank` in `rules.py` use `series.shift(1)`, so the threshold at
time *t* depends only on data strictly before *t*). The frozen day-model
coefficients are themselves purged-walk-forward trained.

**The bias was in hyperparameter SELECTION.** The previous calibrator
grid-searched 36 (thr, conv) × 6 stop configs and 6 modes, picked the best by
metrics computed on the `HOLDOUT_START = 2024-03-19+` window, then **reported
metrics on the same window**. The headline "+41.94 OOS Sharpe" was therefore
the maximum of a ~200-cell grid search over the reported window — optimistically
biased (hyperparameter snooping). `deploy.py`'s mixed-mode picker compounded it
by selecting the best of 6 modes on the same window.

### Fix

Replaced the single IS/OOS split with **purged expanding-window walk-forward**
(yearly folds, matching `optimize_put_alpha.py --select-by-oos` and
`day-model/train_model.py:purged_tssplit` conventions):

```
For each test year Y in {2021, 2022, 2023, 2024, 2025, 2026}:
    train = all dates strictly before Y (purge gap = 1 day)
    For each mode in {single, hybrid, dual} × {ungated, +gated}:
        grid_search(thr, conv, stop) scoring on train window only
    pick best mode by train-window composite score
    if not eligible on train (P&L>0, S>0, n≥20) → side disabled for fold Y
    else apply selected config to test year Y
stitch trades across all test folds → pooled WF equity curve
```

A side is **deployed** iff:
1. Eligible (train P&L>0 AND train Sharpe>0 AND n≥20) in ≥ 50% of folds, AND
2. Pooled WF Sharpe > 0.

Purge gap = 1 day is sufficient because `trade_return` is a same-day target
(features at decision-bar close → exit at 14:30 same day) — no multi-day
forward leakage. The gap is a safety boundary only.

### Plumbing

- `walkforward.py` — `make_yearly_folds(dates)` → list of fold dicts
  `{test_year, train_end, test_start, test_end, n_train_days, n_test_days}`.
  Skips folds with `< 252` train days or `< 20` test days (so 588000ETF, which
  starts 2021, only contributes folds from 2023 onward).
- `calibrate.py:_grid_search_on_window(etf, side, train_end, mode, gated)` —
  replaces the old `_calibrate_one_side`. Scores on train window only; returns
  best eligible config + train-window metrics.
- `calibrate.py:calibrate_side_walkforward` — loops folds, replays each fold's
  selected config on its test window, concatenates stitched trades.
- `calibrate.py:replay_side_wf_trades` — rebuilds stitched WF trades from a
  persisted per-fold config (used by `report.py`; avoids re-running grid search).
- `deploy.py` — picks best mode per side by **pooled WF Sharpe** among configs
  that pass the eligibility majority gate.
- `report.py` — §2.1 "Per-Fold Config Stability" table exposes regime drift;
  §3 reports pooled WF metrics; §5 mode comparison all in WF terms.

### Result (bias gap)

| Metric | Old (single-split) | New (walk-forward) | Δ |
|---|---|---|---|
| Total deployed Sharpe | +41.94 (2024-03+ only) | **+39.96** (2021-2026 pooled) | -1.98 |
| 50ETF short Sharpe | +7.64 | +6.18 (single+gated) | -1.46 |
| 588000ETF long Sharpe | +5.86 | +2.96 (single+gated) | -2.90 |

The drop is modest overall because the day-model score was already honest; only
the threshold/stop/mode selection was biased. Some sides shrank materially
(e.g. 588000 long) — the previous number was inflated by selection on the
reported window. The pooled WF number is the honest estimate.

### Computational Cost

Per (ETF, side, mode, gated): 36 (thr, conv) × 7 stops × 6 folds ≈ 1,500
backtests. With existing NumPy-vectorised `backtest_long_short` and
multiprocessing, full sweep (5 ETFs × 2 sides × 6 mode/gated combos) runs in
~6 minutes. `calibration_*.json` files now contain per-fold config tables
(heavier but still <100 KB each).

---

## 4. File Structure

```
daytrade/
├── __init__.py         # paths, ETFS, DECISION_BAR, EXIT_BAR, DEFAULT_COST_BPS, HOLDOUT_START
├── scores.py           # frozen score loader (side-aware) + IC verification
├── rules.py            # expanding_pct, expanding_pct_masked, expanding_pct_rank, get_long_short_signals (mode="single"|"hybrid"|"dual"), get_signals (legacy)
├── backtest.py         # 5m bar sim, per-side summarizer, fold-agnostic (mode-aware, gated= veto)
├── walkforward.py      # [v4] yearly expanding-window fold schedule + purge helpers
├── calibrate.py        # [v4] walk-forward per-side grid search (--mode single|hybrid|dual, --gated/--sweep-gated)
├── deploy.py           # [v4] per-side best-of-mode deployment by pooled WF Sharpe (reads all calibration files incl. +gated)
├── report.py           # [v4] REPORT.md + results.json + 3 plots (WF pooled metrics, per-fold stability table)
├── gating_loader.py    # loads canonical gating artifacts → boolean fire mask per (etf, side)
├── gating_only.py      # standalone gate-only backtest (diagnostic; NOT deployment)
├── improvement_plan.md # dual-model research findings & revised architecture
├── GATING_ONLY_REPORT.md # gate-only vs gated-daytrade comparison (+9.08 vs +39.96)
├── REPORT.md           # latest summary (walk-forward)
├── AGENTS.md           # this file
├── data/
│   ├── calibration.json             # deployed per-side configs (mode="mixed", walk_forward=True)
│   ├── calibration_single.json      # single-mode WF calibration (ungated)
│   ├── calibration_hybrid.json      # hybrid-mode WF calibration (ungated)
│   ├── calibration_dual.json        # dual-mode WF calibration (ungated)
│   ├── calibration_single_gated.json  # single-mode + gating veto (WF)
│   ├── calibration_hybrid_gated.json  # hybrid-mode + gating veto (WF)
│   ├── calibration_dual_gated.json    # dual-mode + gating veto (WF)
│   └── results.json                 # deployed metrics (WF pooled)
└── plots/
    ├── equity_combined.png
    ├── equity_curves.png   # per-side panels (fold boundaries marked)
    └── yearly_sharpe.png   # per-side year bars (fold-aligned)
```

---

## 5. Key Parameters (`__init__.py` and `walkforward.py`)

| Parameter | Default | Purpose |
|---|---|---|
| `ETFS` | 5 ETFs | Universe of tradable names |
| `DECISION_BAR` | `{300:3, 50:2, 500:4, 588000:2, 159915:4}` | Per-ETF decision bar (close). Single source of truth in `day-model/build_features.py`; imported by `daytrade/__init__.py`. Picked by bar-count experiment with `trade_return` target. |
| `EXIT_BAR` | `41` | 14:30 close (5m bars are timestamped at END of period). Single source of truth in `day-model/build_features.py`. |
| `DEFAULT_COST_BPS` | `15.0` | Round-trip cost in basis points |
| `HOLDOUT_START` | `"2024-03-19"` | Legacy field; no longer used for calibration (v4 is walk-forward). Retained for `split_holdout` backwards-compat imports. |
| `MIN_PERIODS` (rules) | `60` | Min same-side observations before expanding pct is valid |
| `THRESHOLD_GRID` (calibrate) | `[50,60,70,80,90,95]` | Calibration grid for threshold_pct |
| `CONVICTION_GRID` (calibrate) | `[40,50,60,70,80,90]` | Calibration grid for conviction_pct |
| `MIN_TRAIN_TRADES` (calibrate) | `20` | Per-fold eligibility: min train trades |
| `MIN_FOLD_ELIGIBILITY_FRAC` (calibrate) | `0.50` | Side deploys only if eligible in ≥50% of folds |
| `STOP_PCT_GRID` (calibrate) | `[0.030, 0.040, 0.050]` | Fixed-% stop-loss grid (Phase 5); selected by train-window Sharpe |
| `STOP_ATR_GRID` (calibrate) | `[3.5, 4.0, 5.0]` | ATR-14 multiple stop-loss grid (Phase 5) |
| `FIRST_TEST_YEAR_DEFAULT` (walkforward) | `2021` | First walk-forward fold test year |
| `MIN_TRAIN_DAYS_DEFAULT` (walkforward) | `252` | Min train days for a fold (1 trading year) |
| `MIN_TEST_DAYS_DEFAULT` (walkforward) | `20` | Min test days for a fold |
| `PURGE_DAYS_DEFAULT` (walkforward) | `1` | Purge gap (safety only — `trade_return` is same-day) |

---

## 6. Data Dependencies

All on disk — **no rqdatac needed at runtime**.

| Source | File | Used for |
|---|---|---|
| Frozen models (single, default) | `day-model/models/linear_{ETF}.joblib` | coef + intercept |
| Frozen scaler bundle (single) | `day-model/models/scaler_{ETF}.joblib` | StandardScaler (fitted on all 130 features) + `selected_features` + `y_scale` (=100, target in %) |
| Frozen models (dual, hybrid mode only) | `day-model/models/linear_{ETF}_{long,short}.joblib` | Side-specialist coef + intercept |
| Frozen scaler bundle (dual) | `day-model/models/scaler_{ETF}_{long,short}.joblib` | Side-specific scaler + features + stability metadata |
| Feature matrix | `day-model/data/features_{ETF}.parquet` | 130 features × `trade_return` target (+ `pm_return` diagnostic), indexed by date |
| 5m bars | `data/{ETF}_5m.parquet` (note: 300ETF → `510300_5m.parquet`) | Entry/exit prices |
| Day-trading cluster labels | `day-trading/data/clusters_{ETF}_macro.csv` | Diagnostic: Rally/Selloff/Neutral confusion (read-only) |

---

## 7. How to Extend

### A. Add a new ETF

1. Train a model in `day-model/` first (need `linear_{ETF}.joblib`, `scaler_{ETF}.joblib`, `features_{ETF}.parquet`).
2. Ensure 5m data exists at `data/{ETF}_5m.parquet` (run `python3 download_5m_data.py`).
3. Register in `daytrade/__init__.py`:
   - Add to `ETFS`
   - Add to `DECISION_BAR` (use bar 5 by default; drop to bar 2 only if day-model §7 shows strong IC at 9:45)
4. If the 5m filename differs from the `{ETF}_5m.parquet` convention (e.g. 300ETF → 510300), add to `ETF_5M_FILE` in `backtest.py`.
5. Re-run `python -m daytrade.calibrate --mode single && python -m daytrade.calibrate --mode hybrid && python -m daytrade.calibrate --mode dual && python -m daytrade.deploy && python -m daytrade.report`.

### B. Change decision / exit bars

`DECISION_BAR` and `EXIT_BAR` are now defined in `day-model/build_features.py` (single source of truth) and imported by `daytrade/__init__.py`. To change them:

1. Edit `DECISION_BAR[etf]` or `EXIT_BAR` in `day-model/build_features.py`.
2. Re-run the full pipeline (feature build + retrain + calibrate + deploy + report) — both feature engineering and the backtest must be in sync.
3. To pick a new `DECISION_BAR` per-ETF from fresh evidence, run `python day-model/run_experiment_bars.py -e 300,50,500,588000,159915 --trials 40` (uses `trade_return` target; results saved to `experiment_bars_results_trade_return.json`).

Common alternatives:
- `EXIT_BAR = 23` → exit at 11:30 (AM-only, lunch-break strategy)
- `EXIT_BAR = 47` → exit at 15:00 close (full PM session)
- Lower `DECISION_BAR[etf]` → earlier decision, less information, less look-ahead risk
- Higher `DECISION_BAR[etf]` → later decision, more information, but shorter trade window

Always re-run the full pipeline after changing bars — features, model target, and thresholds are all coupled to the specific entry/exit window.

### C. Change cost assumption

```bash
python -m daytrade.calibrate --cost-bps 5      # tight (limit-order fills)
python -m daytrade.calibrate --cost-bps 30     # pessimistic (option-leg friction)
```

For permanent change, edit `DEFAULT_COST_BPS` in `__init__.py`.

### D. Replace the score (custom signal)

The only contract `rules.py` and `backtest.py` need is: `scores.compute_scores(etf)` returns a `pd.Series[date → float]`. To swap in a different signal source:

1. Implement a new function returning the same signature (e.g. `compute_scores_hand_rules()` that uses vote thresholds on raw features instead of frozen coefficients).
2. Update the import in `rules.py` (one line: `from .scores import compute_scores`).
3. Re-run calibration. Thresholds will adapt to the new score's scale.

This is the **v2 hand-rules path** outlined in the original plan: prune to top-5 features by `stability × |coef|`, round weights, build AND/OR vote rules. Keeps ~70% of ML Sharpe for full transparency.

### E. Change calibration grid

Edit `THRESHOLD_GRID`, `CONVICTION_GRID` in `calibrate.py`. Wider grids take longer; the current 6×6 per side × 5 ETFs × 2 sides = 360 backtests runs in ~3 min.

To change the composite score weights or eligibility guard, edit `_score()` and the `eligible` check in `calibrate.py:_calibrate_one_side`.

### F. Per-side asymmetric cost

Currently one `cost_bps` applies to both sides. For options-based shorts (which carry premium + borrow), edit `backtest_long_short` to take `long_cost_bps` and `short_cost_bps` separately, then plumb through calibration.

---

## 8. Deployability Status (walk-forward v4 — pooled across 2021-2026 folds)

Each side deploys the mode (single/hybrid/dual, optionally `+gated`) with the
highest **pooled walk-forward Sharpe** among configs passing the per-fold
eligibility majority gate (≥50% of folds eligible). Run `python -m daytrade.deploy`
to rebuild. The gating-integrated pipeline (`+gated` variants) remains the
**default production config** — 7 of 10 cells pick a `+gated` config.

| ETF | Long | Short | Notes |
|---|---|---|---|
| **50** | dual+gated, pooled S=+3.71 | single+gated, pooled S=+6.18 | Both sides robust via gating. |
| **300** | hybrid+gated, pooled S=+1.34 | single, pooled S=+7.17 (n=12) | Long marginal; short sparse but strong. Investigate `n<60`. |
| **500** | hybrid+gated, pooled S=+3.42 | single+gated, pooled S=+4.90 | Both sides robust. |
| **588000** | single+gated, pooled S=+2.96 | hybrid, pooled S=+2.54 | 4 folds only (data starts 2021). |
| **159915** | single+gated, pooled S=+4.26 | hybrid, pooled S=+3.49 | Both sides robust. |

**Total deployed pooled WF Sharpe**: **+39.96** across 10 sides (2021-2026
honest OOS). Previous single-split headline was +41.94 (2024-03+ only, biased
by selection on the reported window) — see §3 "Result (bias gap)" for the
side-by-side comparison.

Gating remains the single largest daytrade improvement since the
`pm_return`→`trade_return` target fix. Re-train gating models after every
day-model feature rebuild (`python day-model/gating_model.py -e all -t 20 --jobs 5`)
and re-run the calibrate→deploy→report pipeline.

Re-validate after every day-model retrain (see `day-model/AGENTS.md`) and after material market regime change.

---

## 9. Future Improvements (v2+)

Ordered roughly by expected value / implementation cost.

### High priority

1. **Trailing stop / take-profit** — v1 holds to 14:30 unconditionally. Stop-loss (Phase 5, IS-optimised) is now implemented: `backtest_long_short(... stop_pct=0.01)` for fixed-% or `stop_atr_k=1.5` for ATR-based. Calibrator sweeps `STOP_PCT_GRID=[0.3%, 0.5%, 0.8%, 1.0%, 1.5%]` and `STOP_ATR_GRID=[0.5, 1.0, 1.5, 2.0]`, selecting by IS max profit. Still TODO: take-profit at `+2 × ATR14` (lock in Rally continuation) and combined stop-vs-target-vs-hybrid comparison.

2. **Position sizing** — currently fixed notional. Add:
   - Inverse-volatility sizing: `size_t = k / σ_t` (use `early_realized_vol` as same-day σ)
   - Per-side Kelly fraction: `f = (p·b − q) / b` estimated from rolling 252-day win-rate × payoff
   - Per-ETF capital cap to prevent 159915 dominating the book

3. **Asymmetric cost model** — longs use ETF-spread cost (~5–10 bps), shorts use option-leg cost (~30–50 bps). Affects short-side eligibility materially.

4. **~~Walk-forward re-calibration~~** ✅ **Done (v4)** — replaced the single-split calibrator with purged expanding-window yearly folds (see §3). All threshold/stop/mode selection is now per-fold using train-window data only; reported metrics are pooled WF. Future enhancement: quarterly folds (finer-grained, more honest to intra-year regime shifts) — currently yearly to match `optimize_put_alpha.py` convention and keep per-fold sample size adequate.

5. **Phase 2 Option D: skglm L1-Huber** — install `skglm` and add L1-regularized Huber datafit to the model search space. Enables true robust sparse regression (Huber loss + L1 penalty simultaneously). Currently `sklearn.HuberRegressor` only supports L2.

### Medium priority

6. **Multi-ETF portfolio layer** — combine per-ETF strategies into a portfolio with:
   - Correlation-aware capital allocation (500/300/50 are highly correlated)
   - Max concurrent positions / drawdown circuit breaker
   - Equal-risk-contribution (risk parity) weights

7. **Real short side via options** — replace "short ETF = −1 × ETF return" with put-buy or bear-call-spread P&L using existing `data/{ETF}_historical_prices.parquet`. Will erode short Sharpe but make P&L realistic.

8. **Score ensemble** — day-model has per-ETF bar-count experiments (`run_experiment_bars.py`). Average scores from 9:45 / 9:55 / 10:00 models to denoise. Cheap robustness gain.

9. **Hand-rules v2** — implement Extension D above. Prune day-model LASSO to top-5 features by `stability × |coef|`, round weights, replace with vote thresholds. Trade ~30% of Sharpe for full interpretability and zero sklearn runtime dependency.

### Lower priority / research

10. **Exit-time optimization** — grid-search `EXIT_BAR ∈ {36, 39, 41, 44, 47}` per ETF per side. The 14:30 choice was liquidity-driven; some names may have late-day continuation edge (Rally) or mean-reversion edge (Selloff).

11. **Regime gating** — overlay a slow regime filter (e.g. 60-day MA of underlying, or 252-day realized vol bucket) to disable the long_model in bear regimes and short_model in bull regimes. day-model year-by-year IC shows material regime sensitivity.

12. **Live signal generator** — `live.py` that reads today's first N bars from a broker feed (or rqdatac intraday), computes the score, and emits a `{direction, entry_price, stop, target}` order. Output format compatible with manual or API execution.

13. **Better calibration objective** — current profit-first composite is a heuristic. Could replace with deflated Sharpe ratio (López de Prado) to penalize multiple-testing given the 5×4 grid.

14. **Cross-ETF cluster transfer** — day-trading REPORT §7 shows broad-market ETFs transfer well. Pool 300/50/588000 into one model (more data, less overfit). 159915/500 stay per-ETF.

15. **Restore 300ETF features** — `build_features.py` lost `rsi14`, `ema26_dist`, `vol_pk10`. Re-add or find replacements so 300ETF becomes tradeable again.

---

## 10. Known Caveats

- Short-side P&L assumes 15bps transaction cost and other execution assumptions similar to the long side. Real option/margin/borrow costs are not modeled (which would reduce short_model Sharpe; the cost-sensitivity table in REPORT.md gives the break-even sensitivity).
- Frozen coefficients = **no regime adaptation**. Live IC decay (visible in day-model year-by-year tables for 50ETF) will silently erode edge until next retrain.
- 14:30 exit leaves late-day Rally continuation on the table — visible in the equity curve vs buy-and-hold.
- Single `cost_bps` for both long and short; real shorts via options carry different (likely higher) cost.
- No position sizing in v1 — drawdowns are per-unit-notional and 159915 will dominate any naive portfolio combination.
- Drawdown Calculation: Drawdown was historically calculated with a buggy formula `minimum.accumulate(cum) - cum`. This was corrected to `cum - maximum.accumulate(cum)` with inception `0.0` prepended to measure drawdown from the start of trading.
- **300ETF long marginal**: pooled WF Sharpe +1.34 — above the deployment floor but thin. Several folds have <10 test trades. Treat as borderline; investigate before sizing.
- **300ETF short sparse (n=12 pooled)**: very selective (thr=95, conv=40) — high Sharpe but tiny sample. `n<60` fragility warning fires; high multiple-testing risk.
- **588000ETF fewer folds**: data starts 2021, so only 4 folds (2023-2026). First fold has just 32 train days — borderline `MIN_TRAIN_DAYS_DEFAULT=252` check.
- **Per-fold config instability**: stop type/value varies across folds for some sides (e.g. 500ETF long switches between 5.00% and 3.5×ATR). This is honest regime adaptation but means there is no single "deployed config" — the per-fold table in REPORT.md §2.1 is the source of truth.
- **Dual mode selectivity**: At thr=50, dual mode selects ~50% of days (rank ≥ median) since rank is computed over all days, not same-side days. Single mode's conditional thresholding is inherently more selective. Consider higher minimum thresholds for dual mode calibration.


---

## 11. Validation Checklist (after any code change)

- [ ] `python -m daytrade.scores` — verify IC positive for all ETF×side dual models
- [ ] `python day-model/gating_model.py -e all -t 20 --jobs 5` — gating models trained, all 10 cells deployable (WF AUC > 0.53, PR-AUC > base)
- [ ] `python day-model/evaluate_gating.py` — GATING_REPORT.md written, winner table sane
- [ ] `python -m daytrade.calibrate --mode single --sweep-gated` — WF ungated + gated configs saved (per-fold tables in JSON)
- [ ] `python -m daytrade.calibrate --mode hybrid --sweep-gated` — WF hybrid ungated + gated saved
- [ ] `python -m daytrade.calibrate --mode dual --sweep-gated` — WF dual ungated + gated saved
- [ ] `python -m daytrade.deploy` — mixed-mode calibration.json written, picks max pooled WF Sharpe per side
- [ ] `python -m daytrade.report` — REPORT.md renders, §2.1 per-fold stability table populated, §3 metrics are pooled WF (not single-split)
- [ ] `python -m daytrade.gating_only` — gate-only diagnostic runs (expect total ≪ gated-daytrade; sanity only)
- [ ] Cost sensitivity: at least 2 sides remain positive at 30 bps (robustness floor)
- [ ] Cluster confusion: long_model trades ≥30% Rally days, short_model ≥30% Selloff days (sanity that signal direction aligns with discovered day-types)
- [ ] Total deployed pooled WF Sharpe ≥ +30 (current: **+39.96**; was +41.94 single-split — the ~2 point drop is the selection bias removed, not a regression)
- [ ] No side flunks the majority-fold eligibility gate unexpectedly (if one does, investigate regime drift before re-enabling)
