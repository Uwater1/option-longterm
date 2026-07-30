# NewTrade — Factor Monetization Commands & Architecture

Monetize admitted factors from `day-model-new` into ETF spot trading signals. See [plan.md](plan.md) for full design.

## Production System (Robustness-Validated)

```bash
# Production ensemble backtest (DSR-validated, CPCV-confirmed)
python newtrade/run_production.py -e all --mode binary --cpcv

# Multi-ETF portfolio backtest (equal-weight, DSR=0.953 SIGNIFICANT)
python newtrade/portfolio_backtest.py
python newtrade/portfolio_backtest.py --fee-bps 20   # Stress test

# Full robustness suite (DSR + CPCV + PBO + Ensemble + Sensitivity)
python newtrade/robustness.py -e all --all --trials 50
python newtrade/robustness.py -e 159915ETF --dsr --trials 10
python newtrade/robustness.py -e 500ETF --cpcv --n-splits 6 --n-test 2
```

## Research Commands

```bash
# Run single ETF with auto threshold (train-sweep + buffer)
uv run python newtrade/run_backtest.py -e 300ETF --scheme ew

# Trade underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF)
uv run python newtrade/run_backtest.py -e 300ETF --future --scheme rank
uv run python newtrade/run_backtest.py -e 500ETF --future --scheme rank

# Compare all weighting schemes side-by-side (auto exports trades CSVs)
uv run python newtrade/run_backtest.py -e 500ETF --scheme all

# Scheme 4 with dynamic zero-lookahead IC ranking & quadratic position sizing
uv run python newtrade/run_backtest.py -e 300ETF --scheme rank --dynamic-ic --position-mode quadratic

# Custom long/short threshold buffers (long buffer=0.1, short buffer=0.2 default)
uv run python newtrade/run_backtest.py -e all --scheme rank --z-buffer 0.1 --z-short-buffer 0.25

# All ETFs, all schemes, tanh sizing, custom buffer
uv run python newtrade/run_backtest.py -e all --scheme all --z-buffer 0.1
# --z-buffer 0.1 chosen because of a little sweep, little look ahead but logically correct

# Scheme 4 Dedicated Diagnostic Suite (sensitivity sweep, factor rank PnL, conviction bins)
uv run python newtrade/diagnose_rank_scheme.py -e 300ETF
uv run python newtrade/diagnose_rank_scheme.py -e 300ETF --future
uv run python newtrade/diagnose_rank_scheme.py -e all

# Scheme 5 Linear GLM with Britten-Jones Sharpe Optimization (--target-mode bj_sign / bj_return)
uv run python newtrade/glm_backtest.py -e 300ETF --target-mode bj_sign --compare
uv run python newtrade/glm_backtest.py -e all --target-mode bj_sign --prior-mode kns --kns-gamma 0.2 --compare
uv run python newtrade/glm_backtest.py -e all --target-mode bj_sign --compare
uv run python newtrade/glm_backtest.py -e all --target-mode bj_sign --compare --future

# Feature Correlation & Hierarchical Clustering Diagnosis Suite
uv run python newtrade/diagnose_correlation.py -e 300ETF --side single
uv run python newtrade/diagnose_correlation.py -e all --side single --threshold 0.70

# Default production backtest (ICW scheme, Top-10 truncation, EMA30 IC, validated)
uv run python newtrade/run_backtest.py -e all

# Compare ICW and EW side-by-side
uv run python newtrade/run_backtest.py -e all --scheme all

# Top-K & Weighting Research Suite in newtrade/tests/
uv run python newtrade/tests/test_top10_scoring.py
uv run python newtrade/tests/test_top10_weighting.py
uv run python newtrade/tests/test_score_w_ic_mono.py
uv run python newtrade/tests/test_reweight_cadence.py
uv run python newtrade/tests/test_750d_vs_30d_decay.py
# Research intraday stop-loss methods (Fixed, Today High/Low Anchor, Trailing, Vol ATR, Time Decay)
uv run python newtrade/research_stoploss.py -e all --scheme all --report
```

## Architecture

```
newtrade/
├── plan.md                  # Design document (weighting formulas, threshold logic, top-k selection)
├── plan_glm.md              # Scheme 5 GLM design document
├── REPORT.md                # OOS backtest report for ICW & EW (default research report)
├── REPORT_production.md     # Production ensemble report (DSR-validated)
├── REPORT_glm.md            # OOS backtest report for Scheme 5 GLM vs Rank
├── STOPLOSS_RESEARCH_REPORT.md # Intraday stop-loss evaluation report
├── run_production.py        # Production ensemble CLI (binary L+S, buffer=0.15, DSR)
├── portfolio_backtest.py    # Multi-ETF portfolio backtest + fee stress test
├── robustness.py            # DSR, CPCV, PBO, Ensemble, Sensitivity Grid
├── research_stoploss.py     # 1m intraday stop-loss simulator & Train/OOS benchmark
├── utils.py                 # Data loading, recipe computation, expanding z-score, futures trade return mapper
├── weighting.py             # Weighting schemes: ICW (default), EW, Score, Rank, with Top-K truncation
├── strategy.py              # Threshold sweep, position sizing (binary/tanh/quadratic), ETF simulation
├── run_backtest.py          # CLI runner (defaults: --scheme icw --top-k 10 --dynamic-metric ic --ic-ema-span 30 --validate)
├── tests/                   # Research & experimental test suite
│   ├── test_top10_scoring.py
│   ├── test_top10_weighting.py
│   ├── test_score_w_ic_mono.py
│   ├── test_reweight_cadence.py
│   └── test_750d_vs_30d_decay.py
├── artifacts/               # Equity charts, trade CSVs
└── data/                    # JSON result artifacts
```

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Production Signal** | IC Weighted (`--scheme icw`) on Top-10 features selected by 30d EMA IC (`--top-k 10 --dynamic-metric ic --ic-ema-span 30`). |
| **Scheme Comparison** | `--scheme all` evaluates `ICW` and `EW` side-by-side. |
| **Top-K Truncation** | Default `--top-k 10`. Solves 500ETF 32-feature dilution (+0.113 Sharpe lift) while acting as a non-destructive floor for lean pools (159915ETF SR=1.497). |
| **Production Sizing** | Binary L+S. Shorts add 30-40% of PnL. 61% WR on 159915ETF. |
| **Production Buffer** | +0.10 above train-optimal. Walk-forward validated. |
| **Validation** | Portfolio DSR=0.953 (SIGNIFICANT). CPCV 100% positive. PBO=40% (MODERATE). |
| **Scoring Research** | IC_IR useless for daily weighting. Mono helps at ≥0.65 in walk-forward but not in production. IC-only wins with full training data. |
| **Weighting Score** | B3-inspired pool-metadata-only score: `0.40×rank_norm(deflated_ic) + 0.35×rank_norm(ic_ir) + 0.25×rank_norm(mono)`. |
| **Scheme 4 Bounds** | Moderate Tilt default ($w_{\min}=0.2/N, w_{\max}=1.8/N$). Supports linear, power, softmax, top_k mapping. |
| **Dynamic Score Ranking** | Enabled by default (`--dynamic-score`, opt-out `--no-dynamic-score`). Uses `--dynamic-metric ic` smoothed with 30d EMA. |
| **Threshold Asymmetry** | Long buffer `--z-buffer` (default 0.1), Short buffer `--z-short-buffer` (default `z_buffer + 0.1`). |
| **Position Sizing** | `binary`, `tanh`, or `quadratic`. Production uses binary for max Sharpe. |
| **Feature Floor** | ETF/side must have ≥ 10 admitted features, else skipped. |
| **Zero Lookahead** | Expanding-window z-score (μ/σ from t-1). Expanding factor IC from t-1. Threshold from training sweep. |
| **Friction** | 8 bps per position state transition. Stress-tested to 20bps. |
| **Instrument** | Long-Short enabled by default. Use `--long-only` for Spot ETF long-only. Use `--future` for Index Futures. |
| **Trade Window** | 10:00 entry → 14:35 exit (intraday). |
| **Intraday Stop-Loss** | **Omitted**. Benchmarked 5 methods across 1m bars (2022-2026 OOS). Intraday stop-losses degrade Sharpe by -0.337 on avg due to premature exits on noisy local extremes & friction. |

## Data Dependencies

- `day-model-new/admitted_pools.py` — Pool registry (feature_name, sign, deflated_ic, ic_ir, monotonicity, recipe).
- `day-model/data/features_{ETF}.parquet` — Raw feature dataset with `trade_return` column.
- `data/{IF88,IC88,IH88}_5m.parquet` — 5m bars for CFFEX continuous index futures.
- `day-model-new/mining/recipe_utils.py` — `compute_recipe()` for combo features.

