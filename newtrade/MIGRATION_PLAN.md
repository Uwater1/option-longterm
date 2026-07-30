# Pool Migration Plan

## Current State (2026-07-30)

| ETF | Active Pool | Source | Features | OOS Sharpe |
|-----|-------------|--------|----------|------------|
| 300ETF | Old vintage | Pre-pipeline curation | 10 | 0.816 |
| 500ETF | Old vintage | Pre-pipeline curation | 32 | 0.879 |
| 159915ETF | p2017_2025 | Pipeline output | 13 | 1.428 |

## Reselection Cadence

- **Frequency**: Every 2 years, aligned with day-model-new period runs
- **Next run**: `run_periods.py --periods p5` (train 2018-2026, OOS 2026+)
- **Trigger**: Automatic at cadence. No ad-hoc reselection between cycles.

## Switch Decision Protocol

At each reselection cycle, for each ETF:

### Step 1: Gate Check (must pass ALL)
1. New pool has ≥ 10 features
2. Trailing 6-month rolling IC of new pool > old pool (computed at switch date)
3. New pool trained on ≥ 7 years of data

### Step 2: Validation (informational)
- Run `research_pool_comparison.py` with new pool vs current pool
- Compare both Auto-Sweep and Percentile P75 Sharpe
- If new pool loses on BOTH metrics → do NOT switch (override gate)

### Step 3: Transition (if switch approved)
- **Months 1-6**: Use percentile P75 threshold (removes coupling to new signal distribution)
- **Month 7+**: Recalibrate auto-sweep on accumulated new-pool history (≥ 126 trading days)
- During transition, log daily: active pool, threshold method, realized IC

### Step 4: Rollback Guard
- If post-switch 3-month realized Sharpe < 0 → revert to old pool immediately
- Old pool must be preserved (backed up in `newtrade/data/old_admitted_pools_backup.py`)

## Evidence from Switching Protocol Research

### 159915ETF (successful migration already done)
- Gate passed at 2024-01-01: old IC=0.109, new IC=0.136
- Gated+Percentile: 2022-23 sr=2.93, 2024-25 sr=3.06 → **BOTH positive**
- Verdict: Clean switch. New pool adopted.

### 500ETF (hold — do not switch yet)
- Gate passed at 2024-01-01: old IC=0.078, new IC=0.098
- But: old pool Sharpe=1.86 vs new=0.71 (auto-sweep full period)
- New pool (12 features) is too lean vs old (32 features)
- Verdict: **HOLD old pool**. Wait for next cycle with expanded candidates.

### 300ETF (hold — do not switch yet)
- Gate passed at 2024-01-01: old IC=0.043, new IC=0.075
- But: old pool Sharpe=3.29 vs new=0.67 (auto-sweep full period)
- New pool admitted features have 92% FP rate (pipeline signal too weak for 300ETF)
- Verdict: **HOLD old pool**. 300ETF may need pipeline gate recalibration before next switch.

## Monitoring

Quarterly check (manual or scripted):
1. Rolling 6-month IC of active pool
2. Alert if IC < 0.05 for 2 consecutive quarters → trigger early reselection
3. Track feature-level IC decay: if >50% of pool features have trailing IC < 0.03 → flag for review

## Files

| File | Purpose |
|------|---------|
| `day-model-new/admitted_pools.py` | Production pool registry (single source of truth) |
| `newtrade/regenerate_admitted_pools.py` | Regenerate from pipeline output (selective per-ETF) |
| `newtrade/research_pool_comparison.py` | 3-way comparison (Old/New/Yearly × Auto/P75) |
| `newtrade/research_switching_protocol.py` | Switching protocol backtest |
| `newtrade/data/old_admitted_pools_backup.py` | Preserved old pools for rollback |
| `day-model-new/run_periods.py` | Multi-period reselection orchestrator |

## Next Actions

- [ ] Add `--periods p5` config to `run_periods.py` (train 2018-2026)
- [ ] Automate quarterly IC monitoring script
- [ ] Before next switch: run `research_pool_comparison.py` + `research_switching_protocol.py`
- [ ] Consider: expand 300ETF/500ETF candidate pool to recover missing old-pool features
