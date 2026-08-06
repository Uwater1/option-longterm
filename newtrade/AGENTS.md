# NewTrade — Factor Monetization Commands & Architecture

Monetize admitted factors from `day-model-new` into ETF spot trading signals. See [plan.md](plan.md) for full design.

## Production System (Robustness-Validated)

```bash

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

# Trade Option Portfolios (100k RMB capital, 10k/trade, opt_time_decay_trailing=0.30 default)
uv run python newtrade/run_backtest.py -e 300ETF --option
uv run python newtrade/run_backtest.py -e all --option
uv run python newtrade/run_backtest.py -e all --pool-period all --option   # All vintages

# Option Strike Selection A/B test (5 modes × all ETFs)
uv run python newtrade/run_backtest.py -e all --pool-period _p2016_2024 --option --strike-ab --no-validate

# Force specific strike mode (override ETF-adaptive default)
uv run python newtrade/run_backtest.py -e 300ETF --option --strike-mode cascade
uv run python newtrade/run_backtest.py -e 159915ETF --option --strike-mode vol_t1

# Compare all weighting schemes side-by-side (score/icw/sortino/ew, auto exports trades CSVs)
uv run python newtrade/run_backtest.py -e 500ETF --scheme all

# Default production backtest (4 schemes: Score primary + ICW/Sortino/EW, Top-10, ER=25, validated)
uv run python newtrade/run_backtest.py -e all

# Single new schemes: Score Weight (primary), Sortino Weight (tailIC selection + Score-blend weights)
uv run python newtrade/run_backtest.py -e all --scheme score
uv run python newtrade/run_backtest.py -e all --scheme sortino

# Tune the Score blend (tail IC weight; default 0.75 = 75% tailIC + 25% Sortino)
uv run python newtrade/run_backtest.py -e all --scheme score --score-blend-w-ic 0.5

# Override hysteresis exit rank (default 25, A/B validated)
uv run python newtrade/run_backtest.py -e all --scheme icw --exit-rank 20

# Group-constrained backtest (ONC clusters, max 1 feature per cluster)
uv run python newtrade/run_backtest.py -e 300ETF --group-constraint
uv run python newtrade/run_backtest.py -e all --group-constraint --max-per-group 1
uv run python newtrade/run_backtest.py -e 300ETF --no-group-constraint  # disable

# Rolling Tail IC mode (480d window, top/bottom 10% Spearman)
uv run python newtrade/run_backtest.py -e all --ic-mode rolling_tail
uv run python newtrade/run_backtest.py -e 500ETF --ic-mode rolling_tail --tail-window 480

# Feature Correlation & Hierarchical Clustering Diagnosis Suite
uv run python newtrade/diagnose_correlation.py -e 300ETF --side single

# Position Sizing A/B Benchmark (6 Arms: binary, ungated, gated linear/prop, tanh, quadratic)
uv run python newtrade/research_position_sizing.py

# Research intraday stop-loss methods
uv run python newtrade/research_stoploss.py -e all --scheme all --report
uv run python newtrade/research_option_stoploss.py -e all --report
uv run python newtrade/tests/test_option_stoploss_ab.py
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
├── REPORT_option.md         # Option portfolio backtest report
├── REPORT_option_{year}.md  # Per-year option reports (generated via --pool-period/--year + --option)
├── run_backtest.py          # CLI runner (--year, --pool-period, --decay, --scheme, --validate, --option, --stoploss)
├── run_migration.py         # Pool migration protocol (--monitor, --candidate-period)
├── regenerate_admitted_pools.py  # Regenerate admitted_pools.py from pipeline output
├── portfolio_backtest.py    # Multi-ETF portfolio backtest + fee stress test
├── robustness.py            # DSR, CPCV, PBO, Ensemble, Sensitivity Grid
├── research_stoploss.py     # 1m intraday stop-loss simulator & Train/OOS benchmark
├── research_option_stoploss.py # Option intraday stop-loss simulator & Train/OOS benchmark
├── option_strategy.py       # Capital-constrained option portfolio execution, 5m stop-loss, ETF-adaptive strike selection
├── utils.py                 # Data loading, recipe computation, expanding z-score, futures trade return mapper
├── weighting.py             # Weighting schemes: ICW, EW, Score, Rank + hysteresis (weight_mat split, adaptive exit ranks)
├── strategy.py              # Threshold sweep, position sizing (binary/tanh/quadratic), ETF simulation
├── tests/                   # Research & experimental test suite
│   ├── test_option_stoploss_ab.py # Multi-arm option stoploss A/B testing suite
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
| **Production Signal** | 4 schemes: **ensemble** (primary, top of REPORT.md — averages icw + ew), **icw**, **sortino**, **ew** (TailIC-selected equal weight). All share top-10 hysteresis selection (ER=25). ETF-adaptive EMA IC span (**60d** for 300ETF/50ETF, 90d for 500ETF/159915ETF) + **Sortino≤0 selection gate** (post-EMA bounded mask, `--no-sortino-gate` to disable). |
| **Runtime Cache** | Heavy matrices (z-scores, rolling tail IC, Sortino) are computed once per ETF+pool+window and shared across `--scheme all` / `--year` / `--decay` calls (`_PRECOMP_CACHE` in run_backtest.py). |
| **Score Blend** | `DEFAULT_SCORE_BLEND_W_IC = 1.0` (100% TailIC for EW selection; Sortino≤0 selection gate handles downside risk). |
| **Scheme Roles** | ensemble (primary): averages icw + ew (0.849 Sharpe baseline). icw: tail IC selects + weights. sortino: tail IC selects, blend weights. ew: 100% tail IC selects top-K, equal weights. |
| **IC Mode** | `--ic-mode rolling_tail` (default): 480d rolling Spearman on top/bottom 10% tail. `--ic-mode expanding`: full-history Pearson. |
| **Exit Rank** | `--exit-rank` default **25** (fixed, A/B validated 2026-08: fairest across all 3 ETFs; per-ETF optima 23/25/15 conflict, adaptive formulas no better). |
| **Scheme Comparison** | `--scheme all` evaluates `icw`, `sortino`, `ew` side-by-side (ICW section uncollapsed, others in `<details>` blocks). |
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
| **Position Sizing** | Implemented `fast_ramp_linear` ($m=0.50, \Delta Z_{\text{full}}=0.30$) as default in `newtrade/run_backtest.py` (`strategy.py`). **Strictly beats Binary Baseline Sharpe across ALL 3 ETFs simultaneously (300ETF: 1.026 vs 1.021, 500ETF: 1.419 vs 1.390, 159915ETF: 1.573 vs 1.562; Avg 1.339 vs 1.324)** while **slashing MaxDD by 43.9% (3.97% vs 7.08%)** using only 0.55 avg position size! |
| **Feature Floor** | ETF/side must have ≥ 10 admitted features, else skipped. |
| **Zero Lookahead** | Expanding-window z-score (μ/σ from t-1). Expanding factor IC from t-1. Threshold from training sweep. |
| **Friction** | 8 bps per position state transition (Spot). 4 RMB per contract per side (Option). Stress-tested to 20bps. |
| **Option Strike Selection** | ETF-adaptive default (`--strike-mode auto`): 300ETF/50ETF=cascade, 500ETF=nearest, 159915ETF=vol_t1. A/B validated: +83% avg Sharpe vs OTM baseline. See [plan.md §5.3](plan.md). |
| **Instrument** | Long-Short enabled by default. Use `--long-only` for Spot ETF long-only. Use `--future` for Index Futures. |
| **Trade Window** | 10:00 entry → 14:35 exit (intraday). |
| **Intraday Stop-Loss** | Enabled by default: `time_decay_trailing=0.03` (spot), `opt_time_decay_trailing=0.30` (option). Disable with `--no-stoploss`. |
| **Yearly Diagnostics** | Per-year tests (2022–2025) exposed a 2025 regime break: all configs negative on 300ETF/500ETF. Use `--year` runs to check stability before adopting any weighting change. |

## Data Dependencies

- `day-model-new/admitted_pools.py` — Pool registry (feature_name, sign, deflated_ic, ic_ir, monotonicity, recipe).
- `day-model-new/data/cluster_assignments_{etf}_{side}.json` — ONC cluster assignments for group-constrained selection (generated by `day-model-new/feature_clusters.py`).
- `day-model/data/features_{ETF}.parquet` — Raw feature dataset with `trade_return` column.
- `data/{IF88,IC88,IH88}_5m.parquet` — 5m bars for CFFEX continuous index futures.
- `day-model-new/mining/recipe_utils.py` — `compute_recipe()` for combo features.

