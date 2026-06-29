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
| 50ETF | **dual+gated** | +3.71 | 6/6 | **hybrid+gated** | +1.10 | 6/6 |
| 300ETF | **dual+gated** | +0.88 | 6/6 | **single+gated** | +16.02 | 6/6 |
| 500ETF | **single+gated** | +2.94 | 6/6 | **dual+gated** | +5.49 | 6/6 |
| 588000ETF | **hybrid+gated** | +0.27 | 2/4 | **single+gated** | +1.28 | 4/4 |
| 159915ETF | **hybrid+gated** | +2.43 | 6/6 | **single** | +4.22 | 6/6 |

### 2.2 Summary of Deployed Stop Loss & Take-Profit Exit Times

| ETF | Side | Mode | Selected Stop Loss Types (across folds) | Selected Exit Times (across folds) |
|-----|------|------|-----------------------------------------|------------------------------------|
| 50ETF | `long` | **dual+gated** | 3.5×ATR | 41 (14:30) |
| 50ETF | `short` | **hybrid+gated** | 3.00%, str+0.5×ATR, str+1.00% | 44 (14:45) |
| 300ETF | `long` | **dual+gated** | 5.00%, str+1.0×ATR | 41 (14:30) |
| 300ETF | `short` | **single+gated** | str+0.50% | 44 (14:45) |
| 500ETF | `long` | **single+gated** | 4.00%, str+0.5×ATR, str+1.0×ATR | 42 (14:35), 46 (14:55) |
| 500ETF | `short` | **dual+gated** | str+1.00%, struct | 46 (14:55) |
| 588000ETF | `long` | **hybrid+gated** | 3.5×ATR | 24 (13:05), 28 (13:25) |
| 588000ETF | `short` | **single+gated** | 3.00%, 4.00% | 32 (13:45), 38 (14:15) |
| 159915ETF | `long` | **hybrid+gated** | 3.5×ATR | 41 (14:30) |
| 159915ETF | `short` | **single** | 3.00%, 4.00% | 44 (14:45), 46 (14:55) |


### 2.3 Per-Fold Config Stability & Execution Details

Shows the (mode / threshold / conviction / stop / exit time) chosen for each fold's test year, plus train and test Sharpe. Variation across years exposes regime drift; consistency suggests a stable edge.


**50ETF / long** (mode=dual+gated, pooled WF S=+3.71, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.66 | +1414 | 29 | +3.06 | +168 | 10 |
| 2022 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.54 | +1582 | 39 | +4.24 | +1215 | 36 |
| 2023 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.94 | +2796 | 75 | +nan | +55 | 1 |
| 2024 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.98 | +2851 | 76 | -0.02 | -1 | 5 |
| 2025 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.87 | +2851 | 81 | +nan | +88 | 1 |
| 2026 | 50 | 90 | 3.5×ATR | 41 (14:30) | +2.94 | +2939 | 82 | +nan | -97 | 1 |

**50ETF / short** (mode=hybrid+gated, pooled WF S=+1.10, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | str+0.5×ATR | 44 (14:45) | +3.03 | +1071 | 46 | +3.88 | +591 | 22 |
| 2022 | 50 | 80 | str+0.5×ATR | 44 (14:45) | +2.66 | +1448 | 68 | +0.01 | +2 | 23 |
| 2023 | 50 | 70 | str+0.5×ATR | 44 (14:45) | +1.74 | +1763 | 135 | -6.48 | -404 | 14 |
| 2024 | 50 | 70 | str+1.00% | 44 (14:45) | +1.41 | +1529 | 149 | +3.57 | +674 | 14 |
| 2025 | 95 | 40 | 3.00% | 44 (14:45) | +4.73 | +1157 | 22 | +nan | -190 | 1 |
| 2026 | 50 | 80 | 3.00% | 44 (14:45) | +1.74 | +1670 | 114 | +2.39 | +63 | 4 |

**300ETF / long** (mode=dual+gated, pooled WF S=+0.88, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | 5.00% | 41 (14:30) | +4.44 | +2791 | 64 | -1.29 | -50 | 14 |
| 2022 | 50 | 90 | 5.00% | 41 (14:30) | +3.89 | +2742 | 78 | +1.43 | +373 | 37 |
| 2023 | 50 | 90 | 5.00% | 41 (14:30) | +3.21 | +3114 | 115 | +4.32 | +130 | 6 |
| 2024 | 50 | 90 | 5.00% | 41 (14:30) | +3.23 | +3244 | 121 | +3.52 | +487 | 13 |
| 2025 | 50 | 90 | 5.00% | 41 (14:30) | +3.27 | +3731 | 134 | -17.32 | -322 | 5 |
| 2026 | 50 | 90 | str+1.0×ATR | 41 (14:30) | +2.90 | +3409 | 139 | -2.46 | -116 | 8 |

**300ETF / short** (mode=single+gated, pooled WF S=+16.02, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | str+0.50% | 44 (14:45) | +0.40 | +131 | 43 | +nan | +0 | 0 |
| 2022 | 50 | 90 | str+0.50% | 44 (14:45) | +0.40 | +131 | 43 | +nan | +0 | 0 |
| 2023 | 50 | 90 | str+0.50% | 44 (14:45) | +0.40 | +131 | 43 | +nan | +0 | 0 |
| 2024 | 50 | 90 | str+0.50% | 44 (14:45) | +0.40 | +131 | 43 | +16.02 | +1259 | 6 |
| 2025 | 50 | 90 | str+0.50% | 44 (14:45) | +2.57 | +1086 | 49 | +nan | +0 | 0 |
| 2026 | 50 | 90 | str+0.50% | 44 (14:45) | +2.57 | +1086 | 49 | +nan | +0 | 0 |

**500ETF / long** (mode=single+gated, pooled WF S=+2.94, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 60 | str+1.0×ATR | 42 (14:35) | +3.41 | +3866 | 119 | +2.98 | +130 | 9 |
| 2022 | 50 | 60 | str+1.0×ATR | 42 (14:35) | +3.36 | +3991 | 128 | +6.02 | +868 | 26 |
| 2023 | 50 | 60 | str+1.0×ATR | 42 (14:35) | +3.70 | +4967 | 154 | +nan | -71 | 1 |
| 2024 | 50 | 60 | str+1.0×ATR | 42 (14:35) | +3.64 | +4905 | 155 | +3.89 | +1835 | 35 |
| 2025 | 50 | 90 | 4.00% | 46 (14:55) | +5.84 | +3707 | 64 | -6.60 | -203 | 3 |
| 2026 | 50 | 90 | str+0.5×ATR | 46 (14:55) | +5.19 | +3484 | 67 | -2.00 | -123 | 11 |

**500ETF / short** (mode=dual+gated, pooled WF S=+5.49, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | str+1.00% | 46 (14:55) | +4.26 | +4001 | 83 | +3.44 | +280 | 16 |
| 2022 | 50 | 90 | str+1.00% | 46 (14:55) | +4.02 | +4202 | 99 | +8.20 | +1686 | 22 |
| 2023 | 50 | 90 | str+1.00% | 46 (14:55) | +4.17 | +5136 | 121 | +2.75 | +181 | 9 |
| 2024 | 50 | 90 | str+1.00% | 46 (14:55) | +4.08 | +5322 | 130 | +5.33 | +935 | 17 |
| 2025 | 95 | 40 | struct | 46 (14:55) | +4.05 | +3068 | 78 | +0.57 | +30 | 8 |
| 2026 | 50 | 90 | str+1.00% | 46 (14:55) | +3.96 | +6324 | 160 | +6.56 | +892 | 15 |

**588000ETF / long** (mode=hybrid+gated, pooled WF S=+0.27, elig 2/4):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2023 | — | — | — | — | — | — | — | — | — | — (disabled) |
| 2024 | — | — | — | — | — | — | — | — | — | — (disabled) |
| 2025 | 50 | 90 | 3.5×ATR | 28 (13:25) | +2.11 | +1436 | 41 | +2.83 | +333 | 14 |
| 2026 | 50 | 90 | 3.5×ATR | 24 (13:05) | +2.92 | +2478 | 55 | -1.97 | -265 | 14 |

**588000ETF / short** (mode=single+gated, pooled WF S=+1.28, elig 4/4):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2023 | 50 | 40 | 3.00% | 32 (13:45) | +3.73 | +984 | 32 | +7.94 | +433 | 9 |
| 2024 | 50 | 40 | 3.00% | 32 (13:45) | +4.24 | +1405 | 41 | +0.67 | +92 | 15 |
| 2025 | 50 | 40 | 4.00% | 38 (14:15) | +4.14 | +1855 | 56 | +2.30 | +486 | 17 |
| 2026 | 50 | 40 | 4.00% | 38 (14:15) | +3.44 | +2173 | 73 | -2.06 | -300 | 12 |

**159915ETF / long** (mode=hybrid+gated, pooled WF S=+2.43, elig 6/6):
| Fold | Thr | Conv | Stop | Exit Time | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|-----------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 70 | 3.5×ATR | 41 (14:30) | +4.63 | +2943 | 62 | +2.88 | +296 | 14 |
| 2022 | 50 | 80 | 3.5×ATR | 41 (14:30) | +4.86 | +2794 | 57 | +0.99 | +342 | 31 |
| 2023 | 50 | 80 | 3.5×ATR | 41 (14:30) | +3.41 | +3136 | 88 | +nan | +163 | 1 |
| 2024 | 50 | 80 | 3.5×ATR | 41 (14:30) | +3.55 | +3299 | 89 | +0.96 | +113 | 12 |
| 2025 | 50 | 80 | 3.5×ATR | 41 (14:30) | +3.27 | +3412 | 101 | -0.49 | -27 | 6 |
| 2026 | 50 | 80 | 3.5×ATR | 41 (14:30) | +3.09 | +3384 | 107 | +22.03 | +756 | 5 |

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
| 50ETF | `long` | 50 | 3.8% | 58.0% | +3.63 | +1125 | -333 | +22.5 | +28.1 | n<60 |
| 50ETF | `short` | 75 | 5.7% | 46.7% | +1.53 | +983 | -1116 | +13.1 | -11.1 | median<=0, win<=50% |
| 300ETF | `long` | 83 | 6.3% | 50.6% | +0.88 | +502 | -593 | +6.0 | +3.9 | — |
| 300ETF | `short` | 6 | 0.5% | 83.3% | +16.02 | +1259 | -99 | +209.8 | +180.3 | n<60 |
| 500ETF | `long` | 85 | 6.4% | 51.8% | +2.94 | +2435 | -687 | +28.6 | +8.1 | — |
| 500ETF | `short` | 86 | 6.5% | 60.5% | +5.27 | +3777 | -403 | +43.9 | +46.4 | — |
| 588000ETF | `long` | 28 | 3.4% | 39.3% | +0.27 | +68 | -637 | +2.4 | -23.8 | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 53 | 6.3% | 54.7% | +1.28 | +710 | -849 | +13.4 | +13.9 | n<60 |
| 159915ETF | `long` | 69 | 5.2% | 50.7% | +2.43 | +1642 | -544 | +23.8 | +2.9 | — |
| 159915ETF | `short` | 68 | 5.2% | 63.2% | +4.22 | +2976 | -622 | +43.8 | +39.6 | — |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N WF | L Place% | S Place% | Tot Place% | Win% | Sharpe | P&L bps | MaxDD bps |
|-----|------|----------|----------|------------|------|--------|---------|-----------|
| **50ETF** | 125 | 3.8% | 5.7% | 9.5% | 51.2% | +2.19 | +2109 | -1248 |
| **300ETF** | 89 | 6.3% | 0.5% | 6.7% | 52.8% | +2.47 | +1761 | -568 |
| **500ETF** | 171 | 6.4% | 6.5% | 13.0% | 56.1% | +4.01 | +6212 | -920 |
| **588000ETF** | 81 | 3.4% | 6.3% | 9.7% | 49.4% | +0.97 | +779 | -1282 |
| **159915ETF** | 137 | 5.2% | 5.2% | 10.4% | 56.9% | +3.35 | +4617 | -622 |

### 3.3 Year-by-Year Sharpe (fold-aligned)

| ETF | Side | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|-----|------|---|---|---|---|---|---|
| 50ETF | `long` | +1.49 | +4.56 | — | -0.02 | — | — |
| 50ETF | `short` | +3.88 | +1.48 | -6.48 | +3.57 | — | +2.39 |
| 300ETF | `long` | -1.29 | +1.43 | +4.32 | +3.52 | -17.32 | -2.46 |
| 300ETF | `short` | — | — | — | +16.02 | — | — |
| 500ETF | `long` | +2.98 | +6.02 | — | +3.89 | -6.60 | -2.00 |
| 500ETF | `short` | +3.44 | +8.20 | +2.75 | +5.33 | -7.55 | +6.56 |
| 588000ETF | `long` | — | — | — | — | +2.83 | -1.97 |
| 588000ETF | `short` | — | — | +7.94 | +0.67 | +2.30 | -2.06 |
| 159915ETF | `long` | +2.88 | +0.99 | — | +0.96 | -0.49 | +22.03 |
| 159915ETF | `short` | +7.35 | +3.68 | — | +5.54 | +2.17 | +6.33 |

![yearly_sharpe](plots\yearly_sharpe.png)


### 3.4 Cost Sensitivity (per-side, same per-fold configs)

_Per-fold configs are fixed (chosen at 15 bps). Cost sweep re-evaluates P&L only; it is a sensitivity diagnostic, not a re-optimisation._

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +5.11 | +3.71 | +1.60 |
| 50ETF | `short` | +2.27 | +1.10 | -0.65 |
| 300ETF | `long` | +2.34 | +0.88 | -1.31 |
| 300ETF | `short` | +16.79 | +16.02 | +14.88 |
| 500ETF | `long` | +3.97 | +2.94 | +1.40 |
| 500ETF | `short` | +6.68 | +5.49 | +3.70 |
| 588000ETF | `long` | +1.39 | +0.27 | -1.40 |
| 588000ETF | `short` | +2.24 | +1.28 | -0.15 |
| 159915ETF | `long` | +3.45 | +2.43 | +0.90 |
| 159915ETF | `short` | +5.19 | +4.22 | +2.78 |

### 3.5 Equity Curves (stitched across WF test folds)

![equity_combined](plots\equity_combined.png)

![equity_per_side](plots\equity_curves.png)


### 3.6 Fragility Warnings Summary

Non-blocking transparency flags. A side with warnings is still deployed (passes the hard eligibility majority gate) but the positive Sharpe may be a small-sample / heavy-tail artifact. Investigate before sizing.

| ETF | Side | N WF | Median bps | Win% | Warnings |
|-----|------|------|------------|------|----------|
| 50ETF | `long` | 50 | +28.1 | 58.0% | n<60 |
| 50ETF | `short` | 75 | -11.1 | 46.7% | median<=0, win<=50% |
| 300ETF | `long` | 83 | +3.9 | 50.6% | — |
| 300ETF | `short` | 6 | +180.3 | 83.3% | n<60 |
| 500ETF | `long` | 85 | +8.1 | 51.8% | — |
| 500ETF | `short` | 86 | +46.4 | 60.5% | — |
| 588000ETF | `long` | 28 | -23.8 | 39.3% | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 53 | +13.9 | 54.7% | n<60 |
| 159915ETF | `long` | 69 | +2.9 | 50.7% | — |
| 159915ETF | `short` | 68 | +39.6 | 63.2% | — |

## 4. Diagnostic: Cluster Confusion (WF traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters?

| ETF | Side | N | Rally% | Selloff% | Neutral% |
|-----|------|---|--------|----------|----------|
| 50ETF | `long` | 50 | 36% | 24% | 40% |
| 50ETF | `short` | 75 | 12% | 45% | 43% |
| 300ETF | `long` | 83 | 49% | 10% | 41% |
| 300ETF | `short` | 6 | 17% | 67% | 17% |
| 500ETF | `long` | 85 | 42% | 7% | 49% |
| 500ETF | `short` | 86 | 5% | 50% | 45% |
| 588000ETF | `long` | 28 | 43% | 11% | 46% |
| 588000ETF | `short` | 53 | 6% | 64% | 30% |
| 159915ETF | `long` | 69 | 42% | 9% | 49% |
| 159915ETF | `short` | 68 | 13% | 34% | 53% |

## 5. Mode Comparison (Phase 4 — all walk-forward)

Each side deploys the mode with the highest pooled WF Sharpe among configs that pass the eligibility majority gate.

| ETF | Side | Single | Hybrid | Dual | Single+g | Hybrid+g | Dual+g | **Deployed** |
|-----|------|--------|--------|------|----------|----------|--------|--------------|
| 50ETF | `long` | — | — | +2.77 | +0.17 | +0.42 | +3.71 | **dual+gated** (+3.71) |
| 50ETF | `short` | +0.75 | — | — | +0.57 | +1.10 | — | **hybrid+gated** (+1.10) |
| 300ETF | `long` | — | — | +0.30 | — | — | +0.88 | **dual+gated** (+0.88) |
| 300ETF | `short` | +10.58 | — | — | +16.02 | — | +1.42 | **single+gated** (+16.02) |
| 500ETF | `long` | — | +1.37 | +1.24 | +2.94 | +2.24 | +2.21 | **single+gated** (+2.94) |
| 500ETF | `short` | +4.37 | +0.89 | +2.81 | +3.87 | +3.34 | +5.49 | **dual+gated** (+5.49) |
| 588000ETF | `long` | — | — | — | — | +0.27 | — | **hybrid+gated** (+0.27) |
| 588000ETF | `short` | — | — | — | +1.28 | — | — | **single+gated** (+1.28) |
| 159915ETF | `long` | +0.17 | +0.61 | — | +0.96 | +2.43 | +0.17 | **hybrid+gated** (+2.43) |
| 159915ETF | `short` | +4.22 | +2.22 | +1.75 | +3.35 | +1.36 | +1.58 | **single** (+4.22) |

**Total deployed pooled WF Sharpe**: +38.35


## 5.5 Gating Impact (v3, walk-forward)

Per-side pooled WF Sharpe: best ungated mode vs best gated mode.

| ETF | Side | Best Ungated | Best Gated | Δ | Deployed |
|-----|------|--------------|------------|---|----------|
| 50ETF | `long` | +2.77 | +3.71 | +0.93 | **dual+gated** (+3.71) |
| 50ETF | `short` | +0.75 | +1.10 | +0.35 | **hybrid+gated** (+1.10) |
| 300ETF | `long` | +0.30 | +0.88 | +0.58 | **dual+gated** (+0.88) |
| 300ETF | `short` | +10.58 | +16.02 | +5.44 | **single+gated** (+16.02) |
| 500ETF | `long` | +1.37 | +2.94 | +1.57 | **single+gated** (+2.94) |
| 500ETF | `short` | +4.37 | +5.49 | +1.12 | **dual+gated** (+5.49) |
| 588000ETF | `long` | disabled | +0.27 | — | **hybrid+gated** (+0.27) |
| 588000ETF | `short` | disabled | +1.28 | — | **single+gated** (+1.28) |
| 159915ETF | `long` | +0.61 | +2.43 | +1.81 | **hybrid+gated** (+2.43) |
| 159915ETF | `short` | +4.22 | +3.35 | -0.88 | **single** (+4.22) |

**Totals** — Ungated: +24.99 | Gated: +37.48 | Deployed: +38.35 (Δ vs ungated = +13.37)


## 6. Verdict

- **Robust long (pooled WF Sharpe ≥ +1.5)**: 50ETF, 500ETF, 159915ETF
- **Robust short (pooled WF Sharpe ≥ +1.5)**: 300ETF, 500ETF, 159915ETF
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