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

# Period-pool backtest (auto OOS start from pool cutoff 2024-01 through 2026-01)
uv run python newtrade/run_backtest.py -e all --pool-period _p2016_2024 --no-stoploss

# Run all pool vintages sequentially (old, _p2016_2024, _p2018_2026) for full benchmark comparison
uv run python newtrade/run_backtest.py -e all --pool-period all

# Start-year backtest (runs from 2022-01-01 through 2026-01-01)
uv run python newtrade/run_backtest.py -e all --year 2022 --pool-period old --no-stoploss -o newtrade/REPORT_2022_old.md

# Pool decay analysis: test one pool across all future years
uv run python newtrade/run_backtest.py -e 159915ETF --decay --pool-period _p2015_2023 --year 2023
uv run python newtrade/run_backtest.py -e all --decay --pool-period old --year 2022

# Trade underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF)
uv run python newtrade/run_backtest.py -e 300ETF --future --scheme rank
uv run python newtrade/run_backtest.py -e 500ETF --future --scheme rank

# Compare all weighting schemes side-by-side (auto exports trades CSVs)
uv run python newtrade/run_backtest.py -e 500ETF --scheme all

# Default production backtest (ICW scheme, Top-10 truncation, EMA30 IC, validated)
uv run python newtrade/run_backtest.py -e all

# Group-constrained backtest (ONC clusters, max 1 feature per cluster)
uv run python newtrade/run_backtest.py -e 300ETF --group-constraint
uv run python newtrade/run_backtest.py -e all --group-constraint --max-per-group 1
uv run python newtrade/run_backtest.py -e 300ETF --no-group-constraint  # disable

# Feature Correlation & Hierarchical Clustering Diagnosis Suite
uv run python newtrade/diagnose_correlation.py -e 300ETF --side single

# Research intraday stop-loss methods
uv run python newtrade/research_stoploss.py -e all --scheme all --report
```

## Pool Migration Commands

```bash
# Quarterly IC monitoring (alerts on degradation)
python newtrade/run_migration.py --monitor

# Evaluate migration candidate (dry run)
python newtrade/run_migration.py --candidate-period _p2018_2026

# Regenerate admitted_pools.py from pipeline output
python newtrade/regenerate_admitted_pools.py

# Run p5 reselection (train 2018-2026)
python day-model-new/run_periods.py --periods p5
```

## Architecture

```
newtrade/
├── plan.md                  # Design document (weighting formulas, threshold logic, top-k selection)
├── plan_glm.md              # Scheme 5 GLM design document
├── MIGRATION_PLAN.md        # Pool switching protocol (2-year cadence, IC gate, rollback)
├── TODO.md                  # Research notes and experiment results
├── REPORT.md                # OOS backtest report (default full-period)
├── REPORT_{year}.md         # Per-year reports (generated via --year flag)
├── REPORT_production.md     # Production ensemble report (DSR-validated)
├── run_production.py        # Production ensemble CLI (binary L+S, buffer=0.15, DSR)
├── run_backtest.py          # CLI runner (--year, --pool-period, --decay, --scheme, --validate)
├── run_migration.py         # Pool migration protocol (--monitor, --candidate-period)
├── regenerate_admitted_pools.py  # Regenerate admitted_pools.py from pipeline output
├── portfolio_backtest.py    # Multi-ETF portfolio backtest + fee stress test
├── robustness.py            # DSR, CPCV, PBO, Ensemble, Sensitivity Grid
├── research_stoploss.py     # 1m intraday stop-loss simulator & Train/OOS benchmark
├── utils.py                 # Data loading, recipe computation, expanding z-score, futures trade return mapper
├── weighting.py             # Weighting schemes: ICW (default), EW, Score, Rank, with Top-K truncation
├── strategy.py              # Threshold sweep, position sizing (binary/tanh/quadratic), ETF simulation
├── tests/                   # Research & experimental test suite
│   ├── walkforward_migration.py   # Walk-forward protocol validation (4 switch attempts)
│   ├── research_pool_comparison.py # 3-way comparison (Old/New/Yearly × Auto/P75)
│   ├── research_switching_protocol.py # Gated switching backtest
│   ├── run_ab_test_yearly_reselection.py # Initial A/B test
│   ├── investigate_gates.py       # Pipeline gate FN/FP analysis
│   └── ...                        # Top-K, scoring, cadence tests
├── artifacts/               # Equity charts, decay charts, trade CSVs
└── data/                    # JSON result artifacts, old pool backup
```

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Pool Migration** | 2-year cadence via `run_periods.py`. IC gate (candidate > current + min delta) → Sharpe validation → percentile P75 transition → rollback guard. See [MIGRATION_PLAN.md](MIGRATION_PLAN.md). |
| **Per-Year Diagnosis** | `--year 2022` sets start date to `2022-01-01` and runs through `2026-01-01` with unique chart. `--pool-period _p2016_2024` auto-infers OOS start date `2024-01-01`. `--decay` tests pool across future years. |
| **Full Pool Benchmark** | `--pool-period all` sequentially executes backtests for all pool vintages (`old`, `_p2016_2024`, `_p2018_2026`) and generates dedicated reports/charts. |
| **Active ETF Scope** | `300ETF`, `500ETF`, `50ETF`, `159915ETF`. `588000ETF` is **disabled** (trained on 2021-2025 during market regime change). |
| **Production Signal** | IC Weighted (`--scheme icw`) on Top-10 features selected by ETF-adaptive EMA IC (`--ic-ema-span`: 30d for 300ETF/50ETF, 90d for 500ETF/159915ETF). |
| **Scheme Comparison** | `--scheme all` evaluates `ICW` and `EW` side-by-side. |
| **Top-K Truncation** | Default `--top-k 10`. Solves 500ETF 32-feature dilution (+0.113 Sharpe lift) while acting as a non-destructive floor for lean pools (159915ETF SR=1.497). |
| **ONC Group Constraint** | `--group-constraint` enables ONC cluster-based diversity (max 1 feature per cluster per day). Auto-detects period cluster file `day-model-new/data/cluster_assignments_{etf}_{side}{suffix}.json` matching `--pool-period`. Use `--max-per-group N` to allow N features per cluster. |
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
- `day-model-new/data/cluster_assignments_{etf}_{side}.json` — ONC cluster assignments for group-constrained selection (generated by `day-model-new/feature_clusters.py`).
- `day-model/data/features_{ETF}.parquet` — Raw feature dataset with `trade_return` column.
- `data/{IF88,IC88,IH88}_5m.parquet` — 5m bars for CFFEX continuous index futures.
- `day-model-new/mining/recipe_utils.py` — `compute_recipe()` for combo features.

