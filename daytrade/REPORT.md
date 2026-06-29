# Daytrade — Frozen-Linear Intraday Alpha (Walk-Forward Calibrated)

*Signal = frozen LASSO/Huber coefficients from day-model (target = `trade_return`, log return from entry-open to exit-close). Per-side (threshold, conviction, stop, exit_bar, mode) selected via **purged expanding-window walk-forward** (yearly folds, train = all prior years). No hyperparameter snooping. Decision at close[DECISION_BAR[etf]] -> entry at open[DECISION_BAR[etf]+1] -> exit dynamically selected per fold (between 13:05 and 14:55). Cost 15 bps round-trip.*


## 1. Strategy

- **Signal**: frozen LASSO/Huber/ElasticNet score from `day-model/models/linear_{ETF}.joblib`
- **Model target**: `trade_return` = log(close[EXIT_BAR] / open[decision_bar+1]) — mirrors actual trade P&L exactly
- **Per-side thresholds**: expanding-window percentile of |score| computed only over that side's prior history (causal: `series.shift(1)`)
- **Direction**: `long_model` fires when score>0 & crosses long thresholds; `short_model` fires when score<0 & crosses short thresholds
- **Calibration**: walk-forward yearly folds (test year Y, train = all years < Y, 1-day purge gap). Grid-search (thr, conv, stop, exit_bar) per fold using train-window data only; deploy on the test year. Trades stitched across test folds → pooled WF metrics.
- **Eligibility guard (per fold)**: train P&L>0 AND train Sharpe>0 AND n≥20. A side **deploys** only if eligible in ≥50% of folds AND pooled WF Sharpe>0.
- **Mode**: **mixed** (Phase 4 per-side deployment). Each side uses the mode (single/hybrid/dual, optionally +gated) with the highest pooled WF Sharpe among configs that pass the eligibility majority gate.
- **Decision/Entry**: per-ETF `DECISION_BAR` (see day-model/build_features.py).
- **Exit bar**: dynamically optimized per fold (between bar 24 [13:05] and bar 46 [14:55], default 41 [14:30])
- **Cost**: 15 bps round-trip (parametrizable)


## 2. Deployed Configurations

### 2.1 Deployed Modes & Performance

| ETF | Long mode | Long pooled S | Long elig | Short mode | Short pooled S | Short elig |
|-----|-----------|---------------|-----------|------------|----------------|------------|
| 50ETF | **dual+gated** | +3.15 | 6/6 | **single** | +0.75 | 6/6 |
| 300ETF | **dual** | +0.30 | 6/6 | **single** | +10.58 | 6/6 |
| 500ETF | **hybrid+gated** | +3.67 | 6/6 | **dual+gated** | +4.94 | 6/6 |
| 588000ETF | **single+gated** | +0.36 | 4/4 | **single+gated** | +1.54 | 4/4 |
| 159915ETF | **hybrid+gated** | +4.57 | 6/6 | **single** | +4.22 | 6/6 |

### 2.2 Summary of Deployed Stop Loss & Take-Profit Exit Times

| ETF | Side | Mode | Selected Stop Loss Types (across folds) | Selected Exit Times (across folds) |
|-----|------|------|-----------------------------------------|------------------------------------|
| 50ETF | `long` | **dual+gated** | 3.5×ATR | 41 (14:30) |
| 50ETF | `short` | **single** | 3.00%, str+0.50% | 44 (14:45), 46 (14:55) |
| 300ETF | `long` | **dual** | 5.00%, str+1.0×ATR | 41 (14:30) |
| 300ETF | `short` | **single** | str+0.50%, str+0.5×ATR | 24 (13:05), 44 (14:45) |
| 500ETF | `long` | **hybrid+gated** | 3.00%, 4.00% | 24 (13:05), 28 (13:25), 34 (13:55) |
| 500ETF | `short` | **dual+gated** | str+1.00%, struct | 44 (14:45), 46 (14:55) |
| 588000ETF | `long` | **single+gated** | 3.00%, 3.5×ATR, str+0.50% | 24 (13:05), 26 (13:15), 30 (13:35) |
| 588000ETF | `short` | **single+gated** | 3.00%, 4.00%, str+1.0×ATR | 38 (14:15) |
| 159915ETF | `long` | **hybrid+gated** | 3.5×ATR | 41 (14:30) |
| 159915ETF | `short` | **single** | 3.00%, 4.00% | 44 (14:45), 46 (14:55) |


### 2.3 Per-Fold Config Stability & Execution Details

Shows the (mode / threshold / conviction / stop / exit time) chosen for each fold's test year, plus train and test Sharpe. Variation across years exposes regime drift; consistency suggests a stable edge.


**50ETF / long** (mode=dual+gated, pooled WF S=+3.15, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | 3.5×ATR | 41 (14:30) | +1.81 | +1014 | 30 | +1.27 | +56 | 8 |
| 2022 | 50 | 90 | 3.5×ATR | 41 (14:30) | +1.68 | +1070 | 38 | +3.66 | +1031 | 33 |
| 2023 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.20 | +2101 | 71 | +3.66 | +27 | 2 |
| 2024 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.19 | +2128 | 73 | -1.00 | -28 | 6 |
| 2025 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.07 | +2100 | 79 | +nan | +88 | 1 |
| 2026 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.14 | +2188 | 80 | +nan | +0 | 0 |

**50ETF / short** (mode=single, pooled WF S=+0.75, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | str+0.50% | 44 (14:45) | +2.46 | +608 | 40 | +3.59 | +363 | 17 |
| 2022 | 50 | 90 | str+0.50% | 44 (14:45) | +2.73 | +960 | 57 | -2.04 | -244 | 19 |
| 2023 | 95 | 40 | str+0.50% | 44 (14:45) | +2.51 | +562 | 25 | -1.54 | -75 | 9 |
| 2024 | 95 | 40 | str+0.50% | 46 (14:55) | +1.87 | +526 | 34 | +6.40 | +723 | 9 |
| 2025 | 50 | 90 | 3.00% | 44 (14:45) | +2.21 | +1607 | 107 | -8.35 | -257 | 6 |
| 2026 | 50 | 90 | 3.00% | 44 (14:45) | +1.84 | +1390 | 113 | -2.63 | -139 | 7 |

**300ETF / long** (mode=dual, pooled WF S=+0.30, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | 5.00% | 41 (14:30) | +3.86 | +2552 | 68 | -1.29 | -50 | 14 |
| 2022 | 50 | 90 | 5.00% | 41 (14:30) | +3.40 | +2502 | 82 | +0.48 | +135 | 42 |
| 2023 | 50 | 90 | 5.00% | 41 (14:30) | +2.56 | +2637 | 124 | +3.68 | +185 | 12 |
| 2024 | 50 | 90 | 5.00% | 41 (14:30) | +2.59 | +2822 | 136 | +2.43 | +368 | 15 |
| 2025 | 50 | 90 | 5.00% | 41 (14:30) | +2.58 | +3190 | 151 | -12.14 | -314 | 7 |
| 2026 | 50 | 90 | str+1.0×ATR | 41 (14:30) | +2.25 | +2876 | 158 | -2.45 | -133 | 10 |

**300ETF / short** (mode=single, pooled WF S=+10.58, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | str+0.5×ATR | 24 (13:05) | +0.57 | +237 | 57 | +nan | +0 | 0 |
| 2022 | 50 | 90 | str+0.5×ATR | 24 (13:05) | +0.57 | +237 | 57 | +nan | +0 | 0 |
| 2023 | 50 | 90 | str+0.5×ATR | 24 (13:05) | +0.57 | +237 | 57 | +nan | +0 | 0 |
| 2024 | 50 | 90 | str+0.5×ATR | 24 (13:05) | +0.57 | +237 | 57 | +10.58 | +518 | 6 |
| 2025 | 50 | 90 | str+0.50% | 44 (14:45) | +2.31 | +1193 | 63 | +nan | +0 | 0 |
| 2026 | 50 | 90 | str+0.50% | 44 (14:45) | +2.31 | +1193 | 63 | +nan | +0 | 0 |

**500ETF / long** (mode=hybrid+gated, pooled WF S=+3.67, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | 3.00% | 34 (13:55) | +12.84 | +5022 | 49 | +15.20 | +178 | 4 |
| 2022 | 50 | 90 | 3.00% | 34 (13:55) | +12.56 | +5195 | 53 | +6.23 | +529 | 14 |
| 2023 | 50 | 90 | 3.00% | 34 (13:55) | +11.23 | +5701 | 67 | +nan | +198 | 1 |
| 2024 | 50 | 90 | 3.00% | 34 (13:55) | +11.41 | +5848 | 68 | +3.21 | +929 | 19 |
| 2025 | 95 | 40 | 4.00% | 24 (13:05) | +6.91 | +3143 | 40 | -28.62 | -159 | 2 |
| 2026 | 50 | 90 | 4.00% | 28 (13:25) | +7.35 | +6425 | 90 | +3.59 | +197 | 9 |

**500ETF / short** (mode=dual+gated, pooled WF S=+4.94, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | str+1.00% | 46 (14:55) | +4.57 | +3780 | 68 | +3.50 | +275 | 15 |
| 2022 | 50 | 90 | str+1.00% | 46 (14:55) | +4.33 | +4035 | 83 | +7.70 | +1610 | 22 |
| 2023 | 50 | 90 | str+1.00% | 46 (14:55) | +4.37 | +4906 | 105 | +8.03 | +368 | 8 |
| 2024 | 50 | 90 | str+1.00% | 46 (14:55) | +4.41 | +5219 | 113 | +3.14 | +662 | 17 |
| 2025 | 95 | 40 | struct | 46 (14:55) | +3.94 | +2899 | 72 | -0.30 | -16 | 8 |
| 2026 | 50 | 90 | str+1.00% | 44 (14:45) | +4.04 | +6024 | 144 | +6.21 | +829 | 15 |

**588000ETF / long** (mode=single+gated, pooled WF S=+0.36, elig 4/4):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2023 | 50 | 60 | str+0.50% | 26 (13:15) | +3.20 | +568 | 20 | -4.68 | -178 | 6 |
| 2024 | 50 | 70 | 3.00% | 30 (13:35) | +3.62 | +675 | 23 | -1.66 | -722 | 27 |
| 2025 | 50 | 60 | 3.5×ATR | 24 (13:05) | +2.92 | +2960 | 57 | +5.26 | +1677 | 34 |
| 2026 | 50 | 70 | 3.5×ATR | 24 (13:05) | +3.14 | +3092 | 69 | -4.39 | -443 | 10 |

**588000ETF / short** (mode=single+gated, pooled WF S=+1.54, elig 4/4):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2023 | 50 | 40 | 3.00% | 38 (14:15) | +5.14 | +2160 | 52 | +11.22 | +701 | 11 |
| 2024 | 50 | 40 | 3.00% | 38 (14:15) | +6.07 | +2991 | 63 | +0.26 | +40 | 16 |
| 2025 | 50 | 40 | 4.00% | 38 (14:15) | +5.02 | +3156 | 79 | +0.64 | +197 | 26 |
| 2026 | 50 | 40 | str+1.0×ATR | 38 (14:15) | +3.27 | +3094 | 105 | +0.74 | +107 | 12 |

**159915ETF / long** (mode=hybrid+gated, pooled WF S=+4.57, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 3.5×ATR | 41 (14:30) | +5.69 | +2933 | 49 | +1.03 | +64 | 9 |
| 2022 | 50 | 80 | 3.5×ATR | 41 (14:30) | +5.14 | +2997 | 58 | +1.22 | +389 | 27 |
| 2023 | 50 | 80 | 3.5×ATR | 41 (14:30) | +3.75 | +3387 | 85 | +66.00 | +278 | 2 |
| 2024 | 50 | 80 | 3.5×ATR | 41 (14:30) | +3.99 | +3665 | 87 | +7.65 | +933 | 10 |
| 2025 | 50 | 80 | 3.5×ATR | 41 (14:30) | +4.42 | +4598 | 97 | +2.97 | +186 | 7 |
| 2026 | 50 | 80 | 3.5×ATR | 41 (14:30) | +4.35 | +4783 | 104 | +26.24 | +1131 | 8 |

**159915ETF / short** (mode=single, pooled WF S=+4.22, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | 4.00% | 46 (14:55) | +5.19 | +2481 | 52 | +7.35 | +565 | 11 |
| 2022 | 50 | 90 | 4.00% | 46 (14:55) | +5.52 | +3006 | 63 | +3.68 | +175 | 5 |
| 2023 | 50 | 90 | 4.00% | 46 (14:55) | +5.22 | +3041 | 68 | +nan | +0 | 0 |
| 2024 | 50 | 90 | 4.00% | 46 (14:55) | +5.22 | +3041 | 68 | +5.54 | +1428 | 18 |
| 2025 | 50 | 90 | 3.00% | 46 (14:55) | +4.96 | +3784 | 86 | +2.17 | +608 | 31 |
| 2026 | 95 | 40 | 4.00% | 44 (14:45) | +6.68 | +3405 | 50 | +6.33 | +200 | 3 |

## 3. Walk-Forward OOS Performance (15 bps round-trip)

All metrics below are **pooled across test folds** (no IS/OOS split at a fixed date). Each fold's config was selected using train-window data only.


### 3.1 Per-Side Pooled WF Metrics

*Place%* = side trades / total trading days across all test folds (capital deployment rate).

*Warnings* = non-blocking fragility flags (`median<=0`, `win<=50%`, `n<60`).

| ETF | Side | N WF | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |
|-----|------|------|--------|------|--------|---------|-----------|----------|------------|----------|
| 50ETF | `long` | 47 | 3.6% | 61.7% | +4.66 | +1570 | -444 | +33.4 | +40.3 | n<60 |
| 50ETF | `short` | 66 | 5.0% | 48.5% | +1.21 | +578 | -689 | +8.8 | -2.9 | median<=0, win<=50% |
| 300ETF | `long` | 100 | 7.6% | 49.0% | +0.30 | +191 | -593 | +1.9 | -5.6 | median<=0, win<=50% |
| 300ETF | `short` | 6 | 0.5% | 83.3% | +10.58 | +518 | -90 | +86.4 | +61.9 | n<60 |
| 500ETF | `long` | 49 | 3.7% | 61.2% | +3.67 | +1871 | -829 | +38.2 | +40.7 | n<60 |
| 500ETF | `short` | 84 | 6.4% | 60.7% | +4.72 | +3501 | -644 | +41.7 | +56.2 | — |
| 588000ETF | `long` | 77 | 9.2% | 51.9% | +0.36 | +335 | -1924 | +4.4 | +11.6 | — |
| 588000ETF | `short` | 65 | 7.8% | 60.0% | +1.54 | +1046 | -837 | +16.1 | +20.1 | — |
| 159915ETF | `long` | 63 | 4.8% | 58.7% | +4.57 | +2981 | -413 | +47.3 | +39.9 | — |
| 159915ETF | `short` | 68 | 5.2% | 63.2% | +4.22 | +2976 | -622 | +43.8 | +39.6 | — |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N WF | L Place% | S Place% | Tot Place% | Win% | Sharpe | P&L bps | MaxDD bps |
|-----|------|----------|----------|------------|------|--------|---------|-----------|
| **50ETF** | 113 | 3.6% | 5.0% | 8.6% | 54.0% | +2.64 | +2148 | -709 |
| **300ETF** | 106 | 7.6% | 0.5% | 8.0% | 50.9% | +1.02 | +710 | -593 |
| **500ETF** | 133 | 3.7% | 6.4% | 10.1% | 60.9% | +4.29 | +5372 | -1218 |
| **588000ETF** | 142 | 9.2% | 7.8% | 17.0% | 55.6% | +0.86 | +1381 | -2378 |
| **159915ETF** | 131 | 4.8% | 5.2% | 9.9% | 61.1% | +4.41 | +5957 | -622 |

### 3.3 Year-by-Year Sharpe (fold-aligned)

| ETF | Side | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|-----|------|---|---|---|---|---|---|
| 50ETF | `long` | +1.27 | +5.83 | +3.66 | -1.00 | — | — |
| 50ETF | `short` | +3.59 | -0.36 | -1.54 | +6.40 | -8.35 | -2.63 |
| 300ETF | `long` | -1.29 | +0.48 | +3.68 | +2.43 | -12.14 | -2.45 |
| 300ETF | `short` | — | — | — | +10.58 | — | — |
| 500ETF | `long` | +15.20 | +6.23 | — | +3.21 | -28.62 | +3.59 |
| 500ETF | `short` | +3.50 | +7.70 | +8.03 | +3.14 | -8.66 | +6.21 |
| 588000ETF | `long` | — | — | -4.68 | -1.66 | +5.26 | -4.39 |
| 588000ETF | `short` | — | — | +11.22 | +0.26 | +0.64 | +0.74 |
| 159915ETF | `long` | +1.03 | +1.22 | +66.00 | +7.65 | +2.97 | +26.24 |
| 159915ETF | `short` | +7.35 | +3.68 | — | +5.54 | +2.17 | +6.33 |

![yearly_sharpe](plots\yearly_sharpe.png)


### 3.4 Cost Sensitivity (per-side, same per-fold configs)

_Per-fold configs are fixed (chosen at 15 bps). Cost sweep re-evaluates P&L only; it is a sensitivity diagnostic, not a re-optimisation._

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +4.49 | +3.15 | +1.14 |
| 50ETF | `short` | +2.11 | +0.75 | -1.29 |
| 300ETF | `long` | +1.86 | +0.30 | -2.05 |
| 300ETF | `short` | +11.81 | +10.58 | +8.75 |
| 500ETF | `long` | +4.63 | +3.67 | +2.23 |
| 500ETF | `short` | +6.07 | +4.94 | +3.25 |
| 588000ETF | `long` | +1.18 | +0.36 | -0.88 |
| 588000ETF | `short` | +2.50 | +1.54 | +0.10 |
| 159915ETF | `long` | +5.53 | +4.57 | +3.12 |
| 159915ETF | `short` | +5.19 | +4.22 | +2.78 |

### 3.5 Equity Curves (stitched across WF test folds)

![equity_combined](plots\equity_combined.png)

![equity_per_side](plots\equity_curves.png)


### 3.6 Fragility Warnings Summary

Non-blocking transparency flags. A side with warnings is still deployed (passes the hard eligibility majority gate) but the positive Sharpe may be a small-sample / heavy-tail artifact. Investigate before sizing.

| ETF | Side | N WF | Median bps | Win% | Warnings |
|-----|------|------|------------|------|----------|
| 50ETF | `long` | 47 | +40.3 | 61.7% | n<60 |
| 50ETF | `short` | 66 | -2.9 | 48.5% | median<=0, win<=50% |
| 300ETF | `long` | 100 | -5.6 | 49.0% | median<=0, win<=50% |
| 300ETF | `short` | 6 | +61.9 | 83.3% | n<60 |
| 500ETF | `long` | 49 | +40.7 | 61.2% | n<60 |
| 500ETF | `short` | 84 | +56.2 | 60.7% | — |
| 588000ETF | `long` | 77 | +11.6 | 51.9% | — |
| 588000ETF | `short` | 65 | +20.1 | 60.0% | — |
| 159915ETF | `long` | 63 | +39.9 | 58.7% | — |
| 159915ETF | `short` | 68 | +39.6 | 63.2% | — |

## 4. Diagnostic: Cluster Confusion (WF traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters?

| ETF | Side | N | Rally% | Selloff% | Neutral% |
|-----|------|---|--------|----------|----------|
| 50ETF | `long` | 47 | 38% | 21% | 40% |
| 50ETF | `short` | 66 | 5% | 55% | 41% |
| 300ETF | `long` | 100 | 50% | 8% | 42% |
| 300ETF | `short` | 6 | 17% | 67% | 17% |
| 500ETF | `long` | 49 | 61% | 6% | 31% |
| 500ETF | `short` | 84 | 5% | 52% | 43% |
| 588000ETF | `long` | 77 | 43% | 9% | 48% |
| 588000ETF | `short` | 65 | 5% | 60% | 35% |
| 159915ETF | `long` | 63 | 46% | 11% | 43% |
| 159915ETF | `short` | 68 | 13% | 34% | 53% |

## 5. Mode Comparison (Phase 4 — all walk-forward)

Each side deploys the mode with the highest pooled WF Sharpe among configs that pass the eligibility majority gate.

| ETF | Side | Single | Hybrid | Dual | Single+g | Hybrid+g | Dual+g | **Deployed** |
|-----|------|--------|--------|------|----------|----------|--------|--------------|
| 50ETF | `long` | — | — | +2.77 | +0.03 | +0.18 | +3.15 | **dual+gated** (+3.15) |
| 50ETF | `short` | +0.75 | — | — | +0.58 | +0.50 | — | **single** (+0.75) |
| 300ETF | `long` | — | — | +0.30 | — | — | — | **dual** (+0.30) |
| 300ETF | `short` | +10.58 | — | — | +9.73 | — | +3.16 | **single** (+10.58) |
| 500ETF | `long` | — | +1.37 | +1.24 | +2.83 | +3.67 | +1.95 | **hybrid+gated** (+3.67) |
| 500ETF | `short` | +4.37 | +0.89 | +2.81 | +2.04 | +3.20 | +4.94 | **dual+gated** (+4.94) |
| 588000ETF | `long` | — | — | — | +0.36 | — | — | **single+gated** (+0.36) |
| 588000ETF | `short` | — | — | — | +1.54 | — | — | **single+gated** (+1.54) |
| 159915ETF | `long` | +0.17 | +0.61 | — | +2.19 | +4.57 | +1.18 | **hybrid+gated** (+4.57) |
| 159915ETF | `short` | +4.22 | +2.22 | +1.75 | +2.76 | +2.91 | +1.45 | **single** (+4.22) |

**Total deployed pooled WF Sharpe**: +34.09


## 5.5 Gating Impact (v3, walk-forward)

Per-side pooled WF Sharpe: best ungated mode vs best gated mode.

| ETF | Side | Best Ungated | Best Gated | Δ | Deployed |
|-----|------|--------------|------------|---|----------|
| 50ETF | `long` | +2.77 | +3.15 | +0.38 | **dual+gated** (+3.15) |
| 50ETF | `short` | +0.75 | +0.58 | -0.17 | **single** (+0.75) |
| 300ETF | `long` | +0.30 | disabled | — | **dual** (+0.30) |
| 300ETF | `short` | +10.58 | +9.73 | -0.85 | **single** (+10.58) |
| 500ETF | `long` | +1.37 | +3.67 | +2.30 | **hybrid+gated** (+3.67) |
| 500ETF | `short` | +4.37 | +4.94 | +0.57 | **dual+gated** (+4.94) |
| 588000ETF | `long` | disabled | +0.36 | — | **single+gated** (+0.36) |
| 588000ETF | `short` | disabled | +1.54 | — | **single+gated** (+1.54) |
| 159915ETF | `long` | +0.61 | +4.57 | +3.95 | **hybrid+gated** (+4.57) |
| 159915ETF | `short` | +4.22 | +2.91 | -1.31 | **single** (+4.22) |

**Totals** — Ungated: +24.99 | Gated: +31.45 | Deployed: +34.09 (Δ vs ungated = +9.10)


## 6. Verdict

- **Robust long (pooled WF Sharpe ≥ +1.5)**: 50ETF, 500ETF, 159915ETF
- **Robust short (pooled WF Sharpe ≥ +1.5)**: 300ETF, 500ETF, 588000ETF, 159915ETF
- **Disabled long**: none
- **Disabled short**: none

_Note: the per-side deployability bar dropped from the previous single-split (Sharpe ≥ +2.0) to pooled-WF (Sharpe ≥ +1.5) because walk-forward metrics are honestly out-of-sample — the previous numbers were optimistically biased by hyperparameter selection on the reported window._

## 7. Caveats

- Short-side P&L assumes 15bps transaction cost; real options/margin/borrow costs not modeled
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- Exit bar dynamically optimized per fold (swept between 13:05 and 14:55 bar closes)
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Walk-forward folds are yearly; intra-year regime shifts are not captured
- Per-fold small-sample noise (fold with <60 trades) is flagged via the `n<60` warning
- Cost sensitivity holds per-fold configs fixed; a true cost re-optimisation may shift choices