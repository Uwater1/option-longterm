# Daytrade — Frozen-Linear Intraday Alpha

Rule-based day-trading layer consuming day-model trained coefficients as frozen constants (no runtime ML). Each ETF uses one signed frozen score: sign determines direction (positive -> long, negative -> short), magnitude determines conviction. Each side uses expanding-percentile threshold conditioned on side history.

Three signal modes: single (default), hybrid (single direction x dual conviction), dual (independent execution with rank normalisation). Deployed configuration uses mixed mode (Phase 4): each ETF x side picks mode maximizing pooled walk-forward Sharpe. Built by `python -m daytrade.deploy`.

Walk-forward calibration (v4): per-side parameters (threshold, conviction, stop, mode) re-selected per yearly fold using train data only. See §3 and `walkforward.py`.

---

## 1. Strategy Diagram

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
   │  hold (or exit early via intraday stop-loss)
   ▼
  Exit @ 14:30 (5m bar 41 close)
         or @ stop price if intraday stop-loss triggered
```

Target alignment: model trains on `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])` matching backtest trade P&L.

Per-side eligibility guard: side deploys only if OOS P&L > 0 AND OOS Sharpe > 0 AND n ≥ 20. If neither side eligible, ETF untradeable.

---

## 2. Commands

```bash
source .venv/bin/activate                              # Activate env

# End-to-end workflow
python -m daytrade.scores        # IC sanity check vs day-model report (~5s)
python -m daytrade.calibrate     # per-side grid search -> daytrade/data/calibration.json (~3min)
python -m daytrade.report        # deployed backtest + REPORT.md + plots (~10s)

# Full v2 pipeline (all modes -> deploy best per side)
python -m daytrade.calibrate --mode single                  # single-mode calibration
python -m daytrade.calibrate --mode hybrid                  # hybrid-mode calibration
python -m daytrade.calibrate --mode dual                    # dual-mode calibration
python -m daytrade.deploy                                    # pick best mode per side -> calibration.json
python -m daytrade.report                                    # generate report with mixed-mode deployment

# Gating-integrated pipeline (recommended)
python day-model/gating_model.py -e all -t 20 --jobs 5      # train gating models (~100s)
python -m daytrade.calibrate --all-modes --sweep-gated      # full sweep: 3 modes x 2 gated in one pool (~45s)
python -m daytrade.deploy                                    # mixed-mode picker evaluates +gated candidates
python -m daytrade.report

# Gating-only standalone backtest (diagnostic)
python -m daytrade.gating_only                              # all ETFs, 4% stop, conflict=flat
python -m daytrade.gating_only --no-stop                    # hold to 14:30
python -m daytrade.gating_only --conflict long              # take long on conflict

# Inspection & tuning
python -m daytrade.rules         # long/short signal counts at defaults
python -m daytrade.rules --mode hybrid  # hybrid-mode signal counts
python -m daytrade.rules --mode dual    # dual-mode signal counts
python -m daytrade.backtest      # 300ETF test with per-side metrics
python -m daytrade.calibrate --cost-bps 5
python -m daytrade.calibrate --cost-bps 30
python day-model/train_model.py -e all --trials 100  # retrain both long+short (--both default)
```

Outputs:
- `daytrade/data/calibration.json`: best per-side configs.
- `daytrade/data/results.json`: deployed metrics + cost sweep + cluster confusion.
- `daytrade/REPORT.md`: summary report.
- `daytrade/plots/{equity_combined,equity_curves,yearly_sharpe}.png`.

---

## 3. Architecture

### Per-Side Model Concept

Single frozen score computed per ETF per day (regression on PM return). Sign determines side; magnitude determines conviction. Independent parameters per side:
- `threshold_pct`: expanding percentile cutoff for tradable signal.
- `conviction_pct`: conviction floor (≤ threshold).

Expanding percentile computed conditionally over same-sign score history. Long and short mutually exclusive by construction (opposite score signs).

### Signal Modes

| Mode | Direction | Conviction | Threshold base | Conflict resolution | Status |
|:---|:---|:---|:---|:---|:---|
| `single` (default) | sign of single-model score | \|score\| | same-sign history | not needed | Deployed |
| `hybrid` | sign of single-model score | \|single\| x dual_side_score | combined-conviction history | margin-based | Deployed (159915 Short, 500 Long) |
| `dual` | independent side firing | rank-normalised dual score | expanding_pct_rank [0,1] | margin-based | Deployed (50 Short) |

`mixed` mode (Phase 4 deployment): ETF x side uses mode maximizing OOS Sharpe. Built by `python -m daytrade.deploy`.

### Gating Integration

Big-move gating model (`day-model/gating_model.py`) acts as post-hoc veto filter over directional signal. Long-gate fires on predicted big-up; short-gate fires on predicted big-down. Unpredicted days kept (no veto). Gate is veto filter, not standalone alpha.

Plumbing:
- `gating_loader.load_gating_mask(etf, side)` loads promoted artifact (`gating_{ETF}_{side}.joblib`).
- `backtest_long_short(..., gated=True)` ANDs mask into `signals["direction"]`.
- `calibrate.py --gated` / `--sweep-gated` runs grid with gating.
- `deploy.py` auto-adopts gated variant when OOS Sharpe improves.
- Deployed config carries `gated: bool` flag.

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
                                            entry = open[decision_bar + 1]
                                            exit  = close[EXIT_BAR=41]
                                            net_ret = direction × (exit/entry − 1) − cost
                                                                                       ▼
                                          calibrate.calibrate_all()  →  report.generate()
```

### Eligibility & Scoring

Grid: `threshold_pct ∈ {50,60,70,80,90,95}`, `conviction_pct ∈ {40,50,60,70,80,90}`.
Objective: P&L 35%, FilterLift 30%, Sharpe 15%, MaxDD 10%, WinRate 5%, Placement 5%.
Guards:
- Train eligibility: train P&L > 0 AND train Sharpe > 0 AND n ≥ 20.
- Deployment gate: eligible in ≥ 50% of folds AND pooled WF Sharpe > 0.
- Soft warnings recorded in calibrator (`median<=0`, `win<=50%`, `n<60`).

---

## 4. Walk-Forward Calibration

Replaced single split with purged expanding-window walk-forward (yearly folds).
Schedule: loop test year Y in {2021..2026}, train on dates before Y (purge gap = 1 day). Grid search configs on train window, select best mode by train score. Apply selected config to test year Y. Stitch trades across test folds into pooled WF equity curve.

Plumbing:
- `walkforward.py`: generates yearly folds.
- `calibrate.py`: grid searches on train window per fold, replays stitched trades.
- `deploy.py`: selects best mode per side by pooled WF Sharpe.
- `report.py`: reports pooled WF metrics and fold stability table.

Performance: memoised arrays and vectorised backtest allow full sweep in ~45s via `--all-modes --sweep-gated`.

---

## 5. File Structure

```
daytrade/
├── __init__.py         # parameters, ETFS, DECISION_BAR, EXIT_BAR, DEFAULT_COST_BPS
├── scores.py           # frozen score loader + IC verification
├── rules.py            # expanding_pct, signal rules (single/hybrid/dual modes)
├── backtest.py         # 5m bar simulation & trade summarizer
├── walkforward.py      # yearly expanding-window fold schedule
├── calibrate.py        # walk-forward per-side grid search
├── deploy.py           # per-side best-of-mode deployment by pooled WF Sharpe
├── report.py           # REPORT.md generator + plots
├── gating_loader.py    # loads gating artifacts -> boolean fire mask
├── gating_only.py      # standalone gate-only backtest
├── improvement_plan.md # research findings & architecture docs
├── GATING_ONLY_REPORT.md # gating comparison report
├── REPORT.md           # walk-forward performance report
├── AGENTS.md           # this file
├── data/               # calibration JSON files and results
└── plots/              # equity curves and yearly Sharpe charts
```

---

## 6. Key Parameters

| Parameter | Default | Purpose |
|---|---|---|
| `ETFS` | 5 ETFs | Universe of tradable names |
| `DECISION_BAR` | `{300:3, 50:2, 500:4, 588000:2, 159915:4}` | Per-ETF decision bar close |
| `EXIT_BAR` | `41` | 14:30 close |
| `DEFAULT_COST_BPS` | `15.0` | Round-trip cost in basis points |
| `MIN_PERIODS` | `60` | Min observations before expanding pct valid |
| `THRESHOLD_GRID` | `[50,60,70,80,90,95]` | Calibration grid for threshold_pct |
| `CONVICTION_GRID` | `[40,50,60,70,80,90]` | Calibration grid for conviction_pct |
| `MIN_TRAIN_TRADES` | `20` | Min train trades per fold |
| `MIN_FOLD_ELIGIBILITY_FRAC` | `0.50` | Min fold eligibility fraction for deployment |
| `STOP_PCT_GRID` | `[0.030, 0.040, 0.050]` | Fixed % stop-loss grid |
| `STOP_ATR_GRID` | `[3.5, 4.0, 5.0]` | ATR-14 multiple stop-loss grid |

---

## 7. Data Dependencies

All on disk — no runtime `rqdatac` needed.
- Models: `day-model/models/linear_{ETF}[_side].joblib`.
- Scalers: `day-model/models/scaler_{ETF}[_side].joblib`.
- Features: `day-model/data/features_{ETF}.parquet`.
- 5m Bars: `data/{ETF}_5m.parquet` (300ETF uses `510300_5m.parquet`).
- Clusters: `day-trading/data/clusters_{ETF}_macro.csv`.

---

## 8. How to Extend

### A. Add new ETF
1. Train model in `day-model/` (`linear_{ETF}.joblib`, `scaler_{ETF}.joblib`, `features_{ETF}.parquet`).
2. Ensure 5m data exists in `data/{ETF}_5m.parquet`.
3. Register in `daytrade/__init__.py` (`ETFS`, `DECISION_BAR`). Add 5m alias to `ETF_5M_FILE` in `backtest.py` if needed.
4. Run calibration and deploy pipeline.

### B. Change decision / exit bars
1. Edit `DECISION_BAR` or `EXIT_BAR` in `day-model/build_features.py` (single source of truth).
2. Retrain models, regenerate features, run calibrate, deploy, and report.

### C. Change cost assumption
Run `python -m daytrade.calibrate --cost-bps 5` or edit `DEFAULT_COST_BPS` in `__init__.py`.

---

## 9. Deployability Status

| ETF | Long | Short | Notes |
|---|---|---|---|
| **50** | dual+gated, pooled S=+3.71 | single+gated, pooled S=+6.18 | Robust via gating. |
| **300** | hybrid+gated, pooled S=+1.34 | single, pooled S=+7.17 (n=12) | Long marginal; short sparse. |
| **500** | hybrid+gated, pooled S=+3.42 | single+gated, pooled S=+4.90 | Both sides robust. |
| **588000** | single+gated, pooled S=+2.96 | hybrid, pooled S=+2.54 | 4 folds (data starts 2021). |
| **159915** | single+gated, pooled S=+4.26 | hybrid, pooled S=+3.49 | Both sides robust. |

Total deployed pooled WF Sharpe: **+39.96** across 10 sides.

---

## 10. Known Caveats

- Short P&L assumes 15bps transaction cost; real option borrow/friction not modeled.
- Frozen coefficients have no dynamic regime adaptation; requires periodic retrain.
- 14:30 exit leaves late-day rally continuation on table.
- Fixed capital allocation per trade; no dynamic position sizing.

---

## 11. Validation Checklist

- [ ] `python -m daytrade.scores`: verify positive IC across dual models.
- [ ] `python day-model/gating_model.py -e all -t 20 --jobs 5`: train gating models.
- [ ] `python day-model/evaluate_gating.py`: generate gating report.
- [ ] `python -m daytrade.calibrate --all-modes --sweep-gated`: run full sweep.
- [ ] `python -m daytrade.deploy`: rebuild deployment configuration.
- [ ] `python -m daytrade.report`: verify report and plots.
- [ ] Total deployed pooled WF Sharpe ≥ +30.

---

## 12. In-Memory Cache Invalidation

Module caches store hot-path computations in process memory. CLI runs start cold. In interactive sessions (REPL/Jupyter), clear caches when modifying code or regenerating files:

```python
from daytrade.backtest import (
    _5M_CACHE, _GROUPED_BARS_CACHE, _ATR_CACHE, _DAY_TABLE_CACHE, _BT_CACHE,
)
from daytrade.rules import _SIGNALS_CACHE, _MASKED_PCT_CACHE, _RANK_CACHE
from daytrade.scores import _SCORES_CACHE, _FEATURES_CACHE
from daytrade.report import _FOLDS_CACHE
for c in (_5M_CACHE, _GROUPED_BARS_CACHE, _ATR_CACHE, _DAY_TABLE_CACHE, _BT_CACHE,
          _SIGNALS_CACHE, _MASKED_PCT_CACHE, _RANK_CACHE,
          _SCORES_CACHE, _FEATURES_CACHE, _FOLDS_CACHE):
    c.clear()
```
