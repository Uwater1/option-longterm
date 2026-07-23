# NewTrade — Factor Monetization Commands & Architecture

Monetize admitted factors from `day-model-new` into ETF spot trading signals. See [plan.md](plan.md) for full design.

## Commands

```bash
# Run single ETF with auto threshold (train-sweep + buffer)
uv run python newtrade/run_backtest.py -e 300ETF --scheme ew

# Compare all weighting schemes side-by-side
uv run python newtrade/run_backtest.py -e 300ETF --scheme all

# All ETFs, all schemes, tanh sizing, custom buffer
uv run python newtrade/run_backtest.py -e all --scheme all --position-mode tanh --z-buffer 0.1

# Fixed threshold override (skip train-sweep)
uv run python newtrade/run_backtest.py -e 500ETF --scheme icw --z-th 0.7
```

## Architecture

```
newtrade/
├── plan.md            # Design document (weighting formulas, threshold logic)
├── utils.py           # Data loading, recipe computation, expanding z-score (numba)
├── weighting.py       # 4 weighting schemes: EW, ICW, Score, Rank (+ GLM placeholder)
├── strategy.py        # Threshold sweep, position sizing (binary/tanh), ETF simulation
├── run_backtest.py    # CLI runner (--scheme all, --z-th auto)
└── data/              # JSON result artifacts
```

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Weighting Score** | B3-inspired but pool-metadata-only: `0.40×rank_norm(deflated_ic) + 0.35×rank_norm(ic_ir) + 0.25×rank_norm(mono)`. NOT the B3 admission formula (which needs per-candidate Sortino simulation). |
| **ICW Shrinkage** | Empirical Bayes: `max(0, deflated_ic - 1/√n_train)^k`. Falls back to EW if all shrink to 0. |
| **Threshold** | `--z-th auto` sweeps [0.2, 1.5] on training set (argmax cost-Sharpe), then adds `--z-buffer` (default +0.2) for IC decay protection. |
| **Feature Floor** | ETF/side must have ≥ 10 admitted features, else skipped. |
| **Zero Lookahead** | Expanding-window z-score (μ/σ from t-1). Weights from pool metadata (training-only). Threshold from training sweep. |
| **Friction** | 8 bps per position state transition. All metrics cost-adjusted. |
| **Instrument** | ETF Spot only (long-only). Futures/Options deferred. |
| **Trade Window** | 10:00 entry → 14:35 exit (intraday). |

## Data Dependencies

- `day-model-new/admitted_pools.py` — Pool registry (feature_name, sign, deflated_ic, ic_ir, monotonicity, recipe).
- `day-model/data/features_{ETF}.parquet` — Raw feature dataset with `trade_return` column.
- `day-model-new/mining/recipe_utils.py` — `compute_recipe()` for combo features.
