feature list are reselected every year, per day-model-new
I should probably update the feature list every year
Do a AB test

## Results (2026-07-30)

### Yearly reselection: REJECTED
- Yearly pool switching loses across all ETFs (300/500/159915) with both threshold methods
- Root cause: B4 correlation gate makes selection chaotically path-dependent (consecutive periods share 0-3 features)
- Per-year threshold sweeps produce inconsistent z_th, amplifying noise

### Pool update: ETF-dependent
- 159915ETF: New pipeline pool (p2017_2025) WINS (+0.44 Sharpe). admitted_pools.py updated.
- 300ETF: Old pool WINS (-0.87 Sharpe from new). Old features not in current candidates.
- 500ETF: Old pool WINS (-0.46 Sharpe from new). Same issue.
- Decision: Keep new pool for 159915ETF only. Revert 300ETF/500ETF to old pools.

### Threshold research: BIG OPPORTUNITY
- Percentile P75 (self-normalizing) produces 3-5x higher Sharpe than auto-sweep
- Auto-sweep couples to training-period signal distribution
- TODO: Research production-viable percentile threshold (P75 too aggressive, need proper calibration)

### Scripts
- `run_ab_test_yearly_reselection.py` — Initial A/B test
- `diagnose_yearly_reselection.py` — Root cause diagnostics (D1-D5)
- `diagnose_pool_divergence.py` — Pool overlap & signal distribution analysis
- `research_pool_comparison.py` — Final 3-way comparison (Old/New/Yearly × Auto/P75)
- `regenerate_admitted_pools.py` — Regenerate admitted_pools.py from pipeline output
- `research_switching_protocol.py` — Gated switching protocol backtest
- `investigate_gates.py` — Pipeline gate FN/FP analysis

### Migration Plan
See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for the full switching protocol.
Key: 2-year cadence, IC gate + Sharpe validation, percentile transition, rollback guard.