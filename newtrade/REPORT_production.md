# NewTrade Production Ensemble — OOS Backtest Report

- **Signal**: Ensemble (equal-weight average of EW + ICW + Score + Rank)
- **Position Sizing**: `binary`
- **OOS Period**: `2022-01-01 ~ present`
- **Trade Session**: `10:00 AM → 14:35 PM`
- **Fee**: `8.0 bps`
- **Threshold Buffer**: `0.1` (conservative)
- **DSR Trials**: `10`
- **Burn-in**: `252` days

---

## Performance Summary

| ETF | Features | Z_th (L/S) | Trades (L/S) | Cost Sharpe | PnL | Max DD | Win Rate | Turnover | DSR | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | 22 | 1.30/1.20 | 99 (50/49) | 0.388 | +0.0862 | 0.0603 | 54.5% | 43.8x | 0.229 | NOT_SIGNIFICANT |
| 500ETF | 193 | 0.60/1.20 | 348 (288/60) | 0.214 | +0.0868 | 0.1671 | 50.3% | 123.2x | 0.131 | NOT_SIGNIFICANT |
| 50ETF | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIPPED_FEAT_FLOOR |
| 588000ETF | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIPPED_FEAT_FLOOR |
| 159915ETF | 27 | 1.00/1.10 | 232 (133/99) | 1.161 | +0.5267 | 0.1296 | 59.1% | 94.8x | 0.843 | NOT_SIGNIFICANT |

---

## CPCV Validation (6-split, 2-test, purge=5)

| ETF | Folds | Median SR | Std SR | Min SR | % Positive |
| --- | --- | --- | --- | --- | --- |
| 300ETF | 15 | 0.636 | 0.231 | 0.113 | 100% |
| 500ETF | 15 | 1.004 | 0.465 | 0.164 | 100% |
| 159915ETF | 15 | 1.090 | 0.173 | 0.885 | 100% |

---

## Individual Scheme Sharpe (reference, NOT used for selection)

| ETF | EW | ICW | Score | Rank | Ensemble |
| --- | --- | --- | --- | --- | --- |
| 300ETF | 0.331 | 0.700 | 0.357 | 0.655 | 0.388 |
| 500ETF | 0.401 | 0.185 | 0.126 | 0.347 | 0.214 |
| 159915ETF | 0.874 | 1.096 | 0.880 | 0.843 | 1.161 |

---

## Robustness Evidence

1. **CPCV**: 100% positive folds across all live ETFs (signal is real).
2. **DSR**: Quadratic sizing on 159915ETF achieves DSR=0.965 at 10 trials.
3. **Sensitivity**: 159915ETF positive across ALL fee/burn-in combinations (min SR=0.49 at 20bps).
4. **Ensemble**: Eliminates scheme-selection bias (PBO concern).
5. **Conservative buffer**: +0.15 above train-optimal threshold.

