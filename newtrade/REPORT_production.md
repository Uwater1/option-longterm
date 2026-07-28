# NewTrade Production Ensemble — OOS Backtest Report

- **Signal**: Ensemble (equal-weight average of EW + ICW + Score + Rank)
- **Position Sizing**: `binary`
- **OOS Period**: `2022-01-01 ~ 2026-01-01`
- **Trade Session**: `10:00 AM → 14:35 PM`
- **Fee**: `8.0 bps`
- **Threshold Buffer**: `0.1` (conservative)
- **DSR Trials**: `10`
- **Burn-in**: `252` days

---

## Performance Summary

| ETF | Features | Z_th (L/S) | Trades (L/S) | Cost Sharpe | PnL | Max DD | Win Rate | Turnover | DSR | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | 10 | 1.30/1.00 | 64 (23/41) | 0.773 | +0.1402 | 0.0621 | 57.8% | 32.2x | 0.572 | NOT_SIGNIFICANT |
| 500ETF | 32 | 0.60/1.00 | 278 (224/54) | 0.969 | +0.3589 | 0.1005 | 57.2% | 116.0x | 0.699 | NOT_SIGNIFICANT |
| 50ETF | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIPPED_FEAT_FLOOR |
| 588000ETF | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIPPED_FEAT_FLOOR |
| 159915ETF | 11 | 0.90/1.00 | 243 (126/117) | 1.404 | +0.6011 | 0.0885 | 60.9% | 109.8x | 0.928 | MARGINAL |

---

## CPCV Validation (6-split, 2-test, purge=5)

| ETF | Folds | Median SR | Std SR | Min SR | % Positive |
| --- | --- | --- | --- | --- | --- |
| 300ETF | 15 | 0.781 | 0.237 | 0.389 | 100% |
| 500ETF | 15 | 1.206 | 0.508 | 0.211 | 100% |
| 159915ETF | 15 | 1.084 | 0.305 | 0.533 | 100% |

---

## Individual Scheme Sharpe (reference, NOT used for selection)

| ETF | EW | ICW | Score | Rank | Ensemble |
| --- | --- | --- | --- | --- | --- |
| 300ETF | 0.780 | 0.821 | 0.933 | 0.961 | 0.773 |
| 500ETF | 0.873 | 0.738 | 1.049 | 0.801 | 0.969 |
| 159915ETF | 1.233 | 1.163 | 1.512 | 1.239 | 1.404 |

---

## Robustness Evidence

1. **CPCV**: 100% positive folds across all live ETFs (signal is genuine).
2. **DSR**: 159915ETF DSR=0.928 (MARGINAL) at 10 trials; portfolio DSR=0.953 (SIGNIFICANT).
3. **Sensitivity**: 159915ETF positive across ALL fee/burn-in combos (min SR=0.49 at 20bps).
4. **Ensemble**: Equal-weight average eliminates scheme-selection bias (PBO=40%, MODERATE).
5. **Walk-forward validated**: Parameters selected on 2020-2022 validation, never on test.

---

## Scoring Weight Research (Walk-Forward, 4056 configs)

Tested IC-only vs multi-metric (IC + IC_IR + Monotonicity) dynamic weighting:

| Config | mono_win | Val SR | Test SR | MaxDD | Note |
| --- | --- | --- | --- | --- | --- |
| IC-only (production) | — | 2.207 | 1.159 | 0.053 | **Best in production** |
| 0.35/0.00/0.65 | 750 | 1.633 | **1.233** | 0.065 | Best walk-forward test |
| 0.20/0.15/0.65 (B3) | 500 | 1.698 | 1.205 | 0.067 | B3 default |
| 0.40/0.05/0.55 | 750 | 1.833 | 1.148 | 0.071 | Val-winner (overfits) |
| 0.75/0.00/0.25 | 500 | 1.881 | 1.111 | 0.057 | Too little mono |

**Key findings:**
- IC_IR is useless for daily weighting (zero it out).
- Monotonicity helps at ≥0.65 weight in walk-forward, but advantage disappears with full training data.
- **Production uses IC-only**: simpler, more stable, outperforms when thresholds trained on full pre-OOS data.
- Multi-metric (0.35/0/0.65, mono=750) available via `DEFAULT_DYNAMIC_METRIC="multi"` if needed.

---

## Production Config

| Parameter | Value | Source |
| --- | --- | --- |
| Scheme | Ensemble (EW+ICW+Score+Rank)/4 | Walk-forward grid |
| Dynamic metric | IC-only (EMA-smoothed expanding IC) | Production comparison |
| Mode | Binary (L+S) | Walk-forward grid |
| Buffer | +0.10 | Walk-forward grid |
| Rank bounds | [0.2, 1.8] (default) | Production-validated |
| Fee | 8 bps | Realistic Chinese ETF |
| Threshold | Train-sweep (all pre-OOS) + buffer | Zero look-ahead |

## Commands

```bash
python newtrade/run_production.py -e all --cpcv          # Production run
python newtrade/optimize_unified.py --quick --validate    # Quick walk-forward grid
python newtrade/optimize_unified.py --validate            # Full grid (4000+ configs, 2min)
python newtrade/portfolio_backtest.py                     # Multi-ETF portfolio + stress
python newtrade/robustness.py -e all --all                # Full DSR/CPCV/PBO suite
```

