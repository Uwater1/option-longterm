# NewTrade — Factor Monetization Commands & Architecture

Monetize admitted factors from `day-model-new` into ETF spot trading signals. See [plan.md](plan.md) for full design.

## Commands

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

# Multi-Metric Score Weight Tuning & Zero-Lookahead Calibration (Numba Accelerated <8s)
uv run python newtrade/tune_score_weights.py
```

## Architecture

```
newtrade/
├── plan.md                  # Design document (weighting formulas, threshold logic, short buffer)
├── plan_glm.md              # Scheme 5 GLM design document
├── REPORT.md                # OOS backtest report for Schemes 1-4
├── REPORT_glm.md            # OOS backtest report for Scheme 5 GLM vs Rank
├── tune_score_weights.py    # Zero-lookahead Numba grid search & adaptive metric score weight optimizer
├── utils.py                 # Data loading, recipe computation, expanding z-score, futures trade return mapper
├── weighting.py             # 4 weighting schemes: EW, ICW, Score, Rank (Moderate Tilt 0.2~1.8 default, dynamic IC)
├── glm.py                   # Scheme 5 Expanding Ridge with Britten-Jones (1999) Sharpe/directional target modes
├── glm_backtest.py          # Standalone Scheme 5 CLI runner & acceptance gate vs Rank Bounded Weight
├── strategy.py              # Threshold sweep, position sizing (binary/tanh/quadratic), ETF simulation, trade log builder
├── run_backtest.py          # CLI runner (--future, --scheme all, --z-th auto, --z-short-buffer, --dynamic-ic, CSV exporter)
├── diagnose_rank_scheme.py  # Dedicated Scheme 4 diagnosis suite
├── diagnose_correlation.py  # Feature correlation & Ward linkage clustering diagnosis
├── artifacts/               # Equity charts & correlation PNG maps (correlation_300ETF_single.png, high_corr_pairs_*.csv)
└── data/                    # JSON result artifacts
```

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Weighting Score** | B3-inspired pool-metadata-only score: `0.40×rank_norm(deflated_ic) + 0.35×rank_norm(ic_ir) + 0.25×rank_norm(mono)`. |
| **Scheme 4 Bounds** | Moderate Tilt default ($w_{\min}=0.2/N, w_{\max}=1.8/N$). Supports linear, power, softmax, top_k mapping. |
| **Dynamic Score Ranking** | Enabled by default (`--dynamic-score`, opt-out `--no-dynamic-score`). Uses `--dynamic-metric ic` (expanding Pearson correlation IC default) smoothed with 30d EMA (`--ic-ema-span 30`). Boosts 300ETF Sharpe to **1.234** (+0.2025 PnL, 2.65% MaxDD). Supports `--dynamic-metric multi` fallback. |
| **Threshold Asymmetry** | Long buffer `--z-buffer` (default 0.1), Short buffer `--z-short-buffer` (default `z_buffer + 0.1`). Short requires higher conviction due to structural long bias. |
| **Position Sizing** | `binary`, `tanh`, or `quadratic` ($S_t = \text{sign}(Z) \cdot \min(1.0, ((|Z| - Z_{\text{th}})/\gamma)^2)$). |
| **Trade CSV Export** | Auto-exports date-level trade logs to `artifacts/trades_{scheme}_{etf}.csv` and `artifacts/rank_bounded_trades.csv`. |
| **ICW Shrinkage** | Empirical Bayes: `max(0, deflated_ic - 1/√n_train)^k`. Falls back to EW if all shrink to 0. |
| **Feature Floor** | ETF/side must have ≥ 10 admitted features, else skipped. |
| **Zero Lookahead** | Expanding-window z-score (μ/σ from t-1). Expanding factor IC from t-1. Threshold from training sweep. |
| **Friction** | 8 bps per position state transition. All metrics cost-adjusted. |
| **Instrument** | Long-Short enabled by default (`long_only=False`). Use `--long-only` for Spot ETF long-only trades. Use `--future` to trade underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF). |
| **Trade Window** | 10:00 entry → 14:35 exit (intraday). |

## Data Dependencies

- `day-model-new/admitted_pools.py` — Pool registry (feature_name, sign, deflated_ic, ic_ir, monotonicity, recipe).
- `day-model/data/features_{ETF}.parquet` — Raw feature dataset with `trade_return` column.
- `data/{IF88,IC88,IH88}_5m.parquet` — 5m bars for CFFEX continuous index futures.
- `day-model-new/mining/recipe_utils.py` — `compute_recipe()` for combo features.

