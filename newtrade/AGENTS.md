# NewTrade — Factor Monetization Commands & Architecture

Monetize admitted factors from `day-model-new` into ETF spot trading signals. See [plan.md](plan.md) for full design.

## Commands

```bash
# Run single ETF with auto threshold (train-sweep + buffer)
uv run python newtrade/run_backtest.py -e 300ETF --scheme ew

# Compare all weighting schemes side-by-side (auto exports trades CSVs)
uv run python newtrade/run_backtest.py -e 300ETF --scheme all

# Scheme 4 with dynamic zero-lookahead IC ranking & quadratic position sizing
uv run python newtrade/run_backtest.py -e 300ETF --scheme rank --dynamic-ic --position-mode quadratic

# Custom long/short threshold buffers (long buffer=0.1, short buffer=0.2 default)
uv run python newtrade/run_backtest.py -e 300ETF --scheme rank --z-buffer 0.1 --z-short-buffer 0.25

# All ETFs, all schemes, tanh sizing, custom buffer
uv run python newtrade/run_backtest.py -e all --scheme all --position-mode tanh --z-buffer 0.1
# --z-buffer 0.1 chosen because of a little sweep, little look ahead but logically correct

# Scheme 4 Dedicated Diagnostic Suite (sensitivity sweep, factor rank PnL, conviction bins)
uv run python newtrade/diagnose_rank_scheme.py -e 300ETF
uv run python newtrade/diagnose_rank_scheme.py -e all
```

## Architecture

```
newtrade/
├── plan.md                  # Design document (weighting formulas, threshold logic, short buffer)
├── utils.py                 # Data loading, recipe computation, expanding z-score, expanding factor IC (numba)
├── weighting.py             # 4 weighting schemes: EW, ICW, Score, Rank (Moderate Tilt 0.2~1.8 default, dynamic IC)
├── strategy.py              # Threshold sweep, position sizing (binary/tanh/quadratic), ETF simulation, trade log builder
├── run_backtest.py          # CLI runner (--scheme all, --z-th auto, --z-short-buffer, --dynamic-ic, CSV exporter)
├── diagnose_rank_scheme.py  # Dedicated Scheme 4 diagnosis suite
├── artifacts/               # Equity charts & trade log CSVs (rank_bounded_trades.csv, trades_*.csv)
└── data/                    # JSON result artifacts
```

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Weighting Score** | B3-inspired pool-metadata-only score: `0.40×rank_norm(deflated_ic) + 0.35×rank_norm(ic_ir) + 0.25×rank_norm(mono)`. |
| **Scheme 4 Bounds** | Moderate Tilt default ($w_{\min}=0.2/N, w_{\max}=1.8/N$). Supports linear, power, softmax, top_k mapping. |
| **Dynamic IC Ranking** | `--dynamic-ic` computes expanding zero-lookahead factor IC ($1:t-1$) for daily dynamic rank weights. |
| **Threshold Asymmetry** | Long buffer `--z-buffer` (default 0.2), Short buffer `--z-short-buffer` (default `z_buffer + 0.1`). Short requires higher conviction due to structural long bias. |
| **Position Sizing** | `binary`, `tanh`, or `quadratic` ($S_t = \text{sign}(Z) \cdot \min(1.0, ((|Z| - Z_{\text{th}})/\gamma)^2)$). |
| **Trade CSV Export** | Auto-exports date-level trade logs to `artifacts/trades_{scheme}_{etf}.csv` and `artifacts/rank_bounded_trades.csv`. |
| **ICW Shrinkage** | Empirical Bayes: `max(0, deflated_ic - 1/√n_train)^k`. Falls back to EW if all shrink to 0. |
| **Feature Floor** | ETF/side must have ≥ 10 admitted features, else skipped. |
| **Zero Lookahead** | Expanding-window z-score (μ/σ from t-1). Expanding factor IC from t-1. Threshold from training sweep. |
| **Friction** | 8 bps per position state transition. All metrics cost-adjusted. |
| **Instrument** | ETF Spot only (long-only). Futures/Options deferred. |
| **Trade Window** | 10:00 entry → 14:35 exit (intraday). |

## Data Dependencies

- `day-model-new/admitted_pools.py` — Pool registry (feature_name, sign, deflated_ic, ic_ir, monotonicity, recipe).
- `day-model/data/features_{ETF}.parquet` — Raw feature dataset with `trade_return` column.
- `day-model-new/mining/recipe_utils.py` — `compute_recipe()` for combo features.
