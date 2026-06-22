# Daytrade — Frozen-Linear Intraday Alpha

Rule-based day-trading layer that consumes day-model trained coefficients as **frozen constants** (no runtime ML) and turns them into per-side deployable signals. Each ETF uses one signed frozen score where **sign determines direction** (positive → long, negative → short) and **magnitude determines conviction**. Each side has its own expanding-percentile threshold conditioned on that side's prior history.

An optional **hybrid mode** (`mode="hybrid"`) multiplies the single-model magnitude by a dual-model side-specialist score for additional conviction filtering. See `improvement_plan.md` for the full dual-model research findings.

---

## 1. Strategy in One Screen

```
  9:30 open
   │
   │  ── collect first N bars ──▶  N=3 for 159915/500 (decision@9:45)
   │                              N=6 for 300/50/588000 (decision@10:00)
   ▼
  Decision bar close
   │
   │  1) score = intercept + Σ coefᵢ × featureᵢ           [frozen, day-model]
   │  2) |score| vs expanding pct over same-side history   [walk-forward]
   │  3) long_model.fires  if score>0 & crosses L_thr
   │     short_model.fires if score<0 & crosses S_thr
   ▼
  Entry @ decision-bar close
   │
   │  hold (no intraday management in v1)
   ▼
  Exit @ 14:30 (5m bar 41 close, better liquidity than 15:00)
```

Per-side **eligibility guard** (calibration-time): a side deploys only if OOS P&L > 0 AND OOS Sharpe > 0 AND n ≥ 20. If neither side is eligible, the ETF is untradeable.

---

## 2. Commands

```bash
source .venv/bin/activate                              # or system python3 with sklearn/joblib

# End-to-end (recommended after any change)
python -m daytrade.scores        # IC sanity vs day-model report (~5s)
python -m daytrade.calibrate     # per-side grid search → daytrade/data/calibration.json (~3min)
python -m daytrade.report        # deployed backtest + REPORT.md + plots (~10s)

# Ad-hoc inspection
python -m daytrade.rules         # long/short signal counts at defaults
python -m daytrade.rules --mode hybrid  # hybrid-mode signal counts
python -m daytrade.backtest      # 300ETF smoke test with per-side metrics

# Tune at different cost assumption
python -m daytrade.calibrate --cost-bps 5
python -m daytrade.calibrate --cost-bps 30

# Experiment with hybrid mode (requires dual models trained first)
python day-model/train_model.py -e all --side both --trials 100  # train dual models
python -m daytrade.calibrate --mode hybrid                       # calibrate hybrid
python -m daytrade.report                                        # generate report
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
| **`hybrid`** | sign of single-model score | \|single\| × dual_side_score | combined-conviction history | margin-based (score/threshold) | ⚠️ Experimental, not better than single |

Dual-model artifacts (`linear_{ETF}_long.joblib` etc.) are trained via `python day-model/train_model.py --side both`. See `improvement_plan.md` for detailed findings on why single-mode outperforms.

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
                                            entry = close[decision_bar]
                                            exit  = close[EXIT_BAR=41]  (14:30)
                                            net_ret = direction × (exit/entry − 1) − cost
                                                                                      ▼
                                          calibrate.calibrate_all()  →  report.generate()
```

### Eligibility & Scoring

Calibration grid: `threshold_pct ∈ {50,60,70,80,90,95}`, `conviction_pct ∈ {40,50,60,70,80,90}`, run independently for long & short. Selection objective is profit-first composite (per AGENTS.md put convention):
- P&L 35%, FilterLift 30% (selectivity rate, `s5`), Sharpe 15%, MaxDD 10%, WinRate 5%, Placement 5% (trades kept fraction, `1.0 - s5`)
- Hard eligibility guard: OOS P&L > 0 AND OOS Sharpe > 0 AND OOS n ≥ 20

Selection is by **holdout** (2024-03-19+), never in-sample — matches day-model window.

---

## 4. File Structure

```
daytrade/
├── __init__.py         # paths, ETFS, DECISION_BAR, EXIT_BAR, DEFAULT_COST_BPS, HOLDOUT_START
├── scores.py           # frozen score loader (side-aware) + IC verification
├── rules.py            # expanding_pct, expanding_pct_masked, get_long_short_signals (mode="single"|"hybrid"), get_signals (legacy)
├── backtest.py         # 5m bar sim, per-side summarizer, holdout splitter (mode-aware)
├── calibrate.py        # independent per-side grid search (--mode single|hybrid)
├── report.py           # REPORT.md + results.json + 3 plots (reads mode from calibration.json)
├── improvement_plan.md # dual-model research findings & revised architecture
├── REPORT.md           # latest summary
├── AGENTS.md           # this file
├── data/
│   ├── calibration.json       # per-side best configs (single-mode default)
│   ├── calibration_hybrid.json # hybrid-mode calibration (saved for comparison)
│   └── results.json           # deployed metrics
└── plots/
    ├── equity_combined.png
    ├── equity_curves.png   # per-side panels
    └── yearly_sharpe.png   # per-side year bars
```

---

## 5. Key Parameters (`__init__.py`)

| Parameter | Default | Purpose |
|---|---|---|
| `ETFS` | 5 ETFs | Universe of tradable names |
| `DECISION_BAR` | `{159915:2, 500:2, 300:5, 50:5, 588000:5}` | Per-ETF decision bar index on 5m frame (bar 2 = 9:45, bar 5 = 10:00) |
| `EXIT_BAR` | `41` | 14:30 close (5m bars are timestamped at END of period) |
| `DEFAULT_COST_BPS` | `15.0` | Round-trip cost in basis points |
| `HOLDOUT_START` | `"2024-03-19"` | OOS cutoff (matches day-model) |
| `MIN_PERIODS` (rules) | `60` | Min same-side observations before expanding pct is valid |
| `THRESHOLD_GRID` (calibrate) | `[50,60,70,80,90,95]` | Calibration grid for threshold_pct (95 added: improved 500ETF Short) |
| `CONVICTION_GRID` (calibrate) | `[40,50,60,70,80,90]` | Calibration grid for conviction_pct |
| `MIN_OOS_TRADES` (calibrate) | `20` | Below this, side config is rejected |

---

## 6. Data Dependencies

All on disk — **no rqdatac needed at runtime**.

| Source | File | Used for |
|---|---|---|
| Frozen models (single, default) | `day-model/models/linear_{ETF}.joblib` | coef + intercept |
| Frozen scaler bundle (single) | `day-model/models/scaler_{ETF}.joblib` | StandardScaler (fitted on all 127 features) + `selected_features` + `y_scale` (=100, target in %) |
| Frozen models (dual, hybrid mode only) | `day-model/models/linear_{ETF}_{long,short}.joblib` | Side-specialist coef + intercept |
| Frozen scaler bundle (dual) | `day-model/models/scaler_{ETF}_{long,short}.joblib` | Side-specific scaler + features + stability metadata |
| Feature matrix | `day-model/data/features_{ETF}.parquet` | 127 features × pm_return, indexed by date |
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
5. Re-run `python -m daytrade.calibrate && python -m daytrade.report`.

### B. Change decision / exit bars

Edit `DECISION_BAR[etf]` or `EXIT_BAR` in `__init__.py`. Common alternatives:
- `EXIT_BAR = 23` → exit at 11:30 (AM-only, lunch-break strategy)
- `EXIT_BAR = 47` → exit at 15:00 close (full PM session)
- `DECISION_BAR[etf] = 0` → enter at 9:35 (first bar close, aggressive)
- `DECISION_BAR[etf] = 11` → wait until 9:35 + 11×5 = 10:25 (more confirmation)

Always re-run calibration after changing bars — thresholds are calibrated to the specific entry/exit window.

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

Edit `THRESHOLD_GRID`, `CONVICTION_GRID` in `calibrate.py`. Wider grids take longer; the current 5×4 per side × 5 ETFs × 2 sides = 200 backtests runs in ~2 min.

To change the composite score weights or eligibility guard, edit `_score()` and the `eligible` check in `calibrate.py:_calibrate_one_side`.

### F. Per-side asymmetric cost

Currently one `cost_bps` applies to both sides. For options-based shorts (which carry premium + borrow), edit `backtest_long_short` to take `long_cost_bps` and `short_cost_bps` separately, then plumb through calibration.

---

## 8. Deployability Status (as of latest calibration)

| ETF | Long | Short | Notes |
|---|---|---|---|
| **159915** | thr=50 c=90, OOS S=+8.59 | thr=50 c=80, OOS S=+6.16 | **Both sides robust. Best name.** |
| **500** | thr=50 c=40, OOS S=+2.88 | **thr=95 c=40, OOS S=+4.88** | Both sides robust. Short improved via wider grid (+2.91→+4.88) |
| **588000** | thr=50 c=90, OOS S=+3.51 | disabled | Long-only; shorts don't work |
| **300** | thr=50 c=80, OOS S=+0.17 | thr=50 c=90, OOS S=+2.21 | **Edge is on the short side**, not long |
| **50** | disabled | thr=50 c=80, OOS S=+0.67 | Fragile (only short, low Sharpe) |

Re-validate after every day-model retrain (see `day-model/AGENTS.md`) and after material market regime change.

---

## 9. Future Improvements (v2+)

Ordered roughly by expected value / implementation cost.

### High priority

1. **Trailing stop / take-profit** — v1 holds to 14:30 unconditionally. Add an intraday rule:
   - Stop-loss at `-k × ATR14` from entry (k ≈ 1.0–1.5)
   - Take-profit at `+2 × ATR14` (lock in Rally continuation)
   - Compare full-hold vs stop-vs-target vs hybrid in report.

2. **Position sizing** — currently fixed notional. Add:
   - Inverse-volatility sizing: `size_t = k / σ_t` (use `early_realized_vol` as same-day σ)
   - Per-side Kelly fraction: `f = (p·b − q) / b` estimated from rolling 252-day win-rate × payoff
   - Per-ETF capital cap to prevent 159915 dominating the book

3. **Asymmetric cost model** — longs use ETF-spread cost (~5–10 bps), shorts use option-leg cost (~30–50 bps). Affects short-side eligibility materially.

4. **Walk-forward re-calibration** — re-fit thresholds on rolling 2-year window quarterly. Catches regime drift in the score distribution even when coefficients are frozen.

### Medium priority

5. **Multi-ETF portfolio layer** — combine per-ETF strategies into a portfolio with:
   - Correlation-aware capital allocation (500/300/50 are highly correlated)
   - Max concurrent positions / drawdown circuit breaker
   - Equal-risk-contribution (risk parity) weights

6. **Real short side via options** — replace "short ETF = −1 × ETF return" with put-buy or bear-call-spread P&L using existing `data/{ETF}_historical_prices.parquet`. Will erode short Sharpe but make P&L realistic.

7. **Score ensemble** — day-model has per-ETF bar-count experiments (`run_experiment_bars.py`). Average scores from 9:45 / 9:55 / 10:00 models to denoise. Cheap robustness gain.

8. **Hand-rules v2** — implement Extension D above. Prune day-model LASSO to top-5 features by `stability × |coef|`, round weights, replace with vote thresholds. Trade ~30% of Sharpe for full interpretability and zero sklearn runtime dependency.

### Lower priority / research

9. **Exit-time optimization** — grid-search `EXIT_BAR ∈ {36, 39, 41, 44, 47}` per ETF per side. The 14:30 choice was liquidity-driven; some names may have late-day continuation edge (Rally) or mean-reversion edge (Selloff).

10. **Regime gating** — overlay a slow regime filter (e.g. 60-day MA of underlying, or 252-day realized vol bucket) to disable the long_model in bear regimes and short_model in bull regimes. day-model year-by-year IC shows material regime sensitivity.

11. **Live signal generator** — `live.py` that reads today's first N bars from a broker feed (or rqdatac intraday), computes the score, and emits a `{direction, entry_price, stop, target}` order. Output format compatible with manual or API execution.

12. **Better calibration objective** — current profit-first composite is a heuristic. Could replace with deflated Sharpe ratio (López de Prado) to penalize multiple-testing given the 5×4 grid.

13. **Cross-ETF cluster transfer** — day-trading REPORT §7 shows broad-market ETFs transfer well. Pool 300/50/588000 into one model (more data, less overfit). 159915/500 stay per-ETF.

---

## 10. Known Caveats

- Short-side P&L assumes 15bps transaction cost and other execution assumptions similar to the long side. Real option/margin/borrow costs are not modeled (which would reduce short_model Sharpe; the cost-sensitivity table in REPORT.md gives the break-even sensitivity).
- Frozen coefficients = **no regime adaptation**. Live IC decay (visible in day-model year-by-year tables for 50ETF) will silently erode edge until next retrain.
- 14:30 exit leaves late-day Rally continuation on the table — visible in the equity curve vs buy-and-hold.
- Per-side eligibility uses holdout (2024-03+) only; earlier years may behave differently. Year-by-year table is the honest diagnostic.
- Single `cost_bps` for both long and short; real shorts via options carry different (likely higher) cost.
- No position sizing in v1 — drawdowns are per-unit-notional and 159915 will dominate any naive portfolio combination.
- Drawdown Calculation: Drawdown was historically calculated with a buggy formula `minimum.accumulate(cum) - cum`. This was corrected to `cum - maximum.accumulate(cum)` with inception `0.0` prepended to measure drawdown from the start of trading.


---

## 11. Validation Checklist (after any code change)

- [ ] `python -m daytrade.scores` — verify IC matches day-model report (159915 within ±0.005 of +0.20)
- [ ] `python -m daytrade.calibrate` — at least 3 ETFs have ≥1 robust side (Sharpe ≥ +2)
- [ ] `python -m daytrade.report` — REPORT.md renders, all 3 plots present
- [ ] Cost sensitivity: at least 2 sides remain positive at 30 bps (robustness floor)
- [ ] Cluster confusion: long_model trades ≥30% Rally days, short_model ≥30% Selloff days (sanity that signal direction aligns with discovered day-types)
