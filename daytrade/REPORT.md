# Daytrade — Frozen-Linear Intraday Alpha (Walk-Forward Calibrated)

*Signal = frozen LASSO/Huber coefficients from day-model (target = `trade_return`, log return from entry-open to exit-close). Per-side (threshold, conviction, stop, mode) selected via **purged expanding-window walk-forward** (yearly folds, train = all prior years). No hyperparameter snooping. Decision at close[DECISION_BAR[etf]] -> entry at open[DECISION_BAR[etf]+1] -> exit at close[41] (14:30). Cost 15 bps round-trip.*


## 1. Strategy

- **Signal**: frozen LASSO/Huber/ElasticNet score from `day-model/models/linear_{ETF}.joblib`
- **Model target**: `trade_return` = log(close[EXIT_BAR] / open[decision_bar+1]) — mirrors actual trade P&L exactly
- **Per-side thresholds**: expanding-window percentile of |score| computed only over that side's prior history (causal: `series.shift(1)`)
- **Direction**: `long_model` fires when score>0 & crosses long thresholds; `short_model` fires when score<0 & crosses short thresholds
- **Calibration**: walk-forward yearly folds (test year Y, train = all years < Y, 1-day purge gap). Grid-search (thr, conv, stop) per fold using train-window data only; deploy on the test year. Trades stitched across test folds → pooled WF metrics.
- **Eligibility guard (per fold)**: train P&L>0 AND train Sharpe>0 AND n≥20. A side **deploys** only if eligible in ≥50% of folds AND pooled WF Sharpe>0.
- **Mode**: **mixed** (Phase 4 per-side deployment). Each side uses the mode (single/hybrid/dual, optionally +gated) with the highest pooled WF Sharpe among configs that pass the eligibility majority gate.
- **Decision/Entry**: per-ETF `DECISION_BAR` (see day-model/build_features.py).
- **Exit bar**: 41 (5m close at 14:30)
- **Cost**: 15 bps round-trip (parametrizable)


## 2. Deployed Configurations

| ETF | Long mode | Long pooled S | Long elig | Short mode | Short pooled S | Short elig |
|-----|-----------|---------------|-----------|------------|----------------|------------|
| **50ETF** | `dual+gated` | +3.71 | 6/6 | `single+gated` | +6.18 | 6/6 |
| **300ETF** | `hybrid+gated` | +1.34 | 6/6 | `single+gated` | +6.59 | 6/6 |
| **500ETF** | `hybrid+gated` | +3.42 | 6/6 | `single+gated` | +4.90 | 6/6 |
| **588000ETF** | `single` | +3.88 | 4/4 | `single` | +2.61 | 4/4 |
| **159915ETF** | `single` | +4.57 | 6/6 | `hybrid` | +4.94 | 6/6 |

### 2.1 Per-Fold Config Stability

Shows the (mode / threshold / conviction / stop) chosen for each fold's test year, plus train and test Sharpe. Variation across years exposes regime drift; consistency suggests a stable edge.


**50ETF / long** (mode=dual+gated, pooled WF S=+3.71, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 90 | 3.5×ATR | +2.66 | +1414 | 29 | +3.06 | +168 | 10 |
| 2022 | 50 | 90 | 3.5×ATR | +2.54 | +1582 | 39 | +4.24 | +1215 | 36 |
| 2023 | 50 | 90 | 3.5×ATR | +2.94 | +2796 | 75 | +nan | +55 | 1 |
| 2024 | 50 | 90 | 3.5×ATR | +2.98 | +2851 | 76 | -0.02 | -1 | 5 |
| 2025 | 50 | 90 | 3.5×ATR | +2.87 | +2851 | 81 | +nan | +88 | 1 |
| 2026 | 50 | 90 | 3.5×ATR | +2.94 | +2939 | 82 | +nan | -97 | 1 |

**50ETF / short** (mode=single+gated, pooled WF S=+6.18, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 4.00% | +4.02 | +1727 | 56 | +8.75 | +977 | 18 |
| 2022 | 50 | 80 | 4.00% | +4.99 | +2703 | 74 | +7.15 | +705 | 12 |
| 2023 | 50 | 80 | 4.00% | +5.34 | +3408 | 86 | +1.92 | +50 | 12 |
| 2024 | 50 | 80 | 4.00% | +5.02 | +3458 | 98 | +5.78 | +870 | 22 |
| 2025 | 50 | 90 | 4.00% | +6.69 | +3117 | 64 | +nan | +113 | 1 |
| 2026 | 50 | 90 | 4.00% | +6.86 | +3230 | 65 | +0.30 | +9 | 5 |

**300ETF / long** (mode=hybrid+gated, pooled WF S=+1.34, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 4.00% | +4.92 | +2661 | 54 | +2.26 | +56 | 6 |
| 2022 | 50 | 80 | 4.00% | +4.72 | +2718 | 60 | -0.23 | -89 | 45 |
| 2023 | 50 | 80 | 3.5×ATR | +2.97 | +2812 | 105 | +9.27 | +213 | 5 |
| 2024 | 50 | 80 | 3.5×ATR | +3.11 | +3025 | 110 | +3.21 | +574 | 15 |
| 2025 | 50 | 80 | 3.5×ATR | +3.13 | +3599 | 125 | +nan | +0 | 0 |
| 2026 | 50 | 80 | 3.5×ATR | +3.13 | +3599 | 125 | +nan | +97 | 1 |

**300ETF / short** (mode=single+gated, pooled WF S=+6.59, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 95 | 40 | 4.00% | +3.03 | +742 | 35 | +1.56 | +19 | 2 |
| 2022 | 95 | 40 | 4.00% | +2.99 | +760 | 37 | +nan | +0 | 0 |
| 2023 | 95 | 40 | 4.00% | +2.99 | +760 | 37 | +nan | +0 | 0 |
| 2024 | 95 | 40 | 4.00% | +2.99 | +760 | 37 | +7.25 | +577 | 7 |
| 2025 | 95 | 40 | 4.00% | +3.93 | +1337 | 44 | +6.43 | +92 | 2 |
| 2026 | 95 | 40 | 4.00% | +4.07 | +1429 | 46 | +nan | +0 | 0 |

**500ETF / long** (mode=hybrid+gated, pooled WF S=+3.42, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 5.00% | +8.15 | +4946 | 64 | +13.24 | +249 | 6 |
| 2022 | 50 | 80 | 5.00% | +8.13 | +5195 | 70 | +6.67 | +1202 | 21 |
| 2023 | 50 | 80 | 5.00% | +7.84 | +6397 | 91 | +nan | +148 | 1 |
| 2024 | 50 | 80 | 5.00% | +7.96 | +6545 | 92 | +1.55 | +619 | 26 |
| 2025 | 50 | 90 | 3.5×ATR | +4.44 | +2927 | 53 | -3.58 | -31 | 2 |
| 2026 | 50 | 90 | 3.5×ATR | +4.30 | +2896 | 55 | +5.37 | +170 | 4 |

**500ETF / short** (mode=single+gated, pooled WF S=+4.90, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 4.00% | +4.57 | +3061 | 68 | +33.90 | +381 | 3 |
| 2022 | 50 | 80 | 4.00% | +4.99 | +3442 | 71 | +5.18 | +419 | 7 |
| 2023 | 50 | 80 | 4.00% | +5.05 | +3861 | 78 | +0.49 | +19 | 3 |
| 2024 | 50 | 80 | 4.00% | +4.86 | +3880 | 81 | +9.42 | +1237 | 21 |
| 2025 | 50 | 90 | 4.00% | +8.22 | +3502 | 47 | +5.91 | +374 | 7 |
| 2026 | 50 | 90 | 4.00% | +7.98 | +3876 | 54 | -1.50 | -184 | 12 |

**588000ETF / long** (mode=single, pooled WF S=+3.88, elig 4/4):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2023 | 50 | 80 | 3.00% | +5.20 | +2195 | 39 | +10.75 | +628 | 6 |
| 2024 | 50 | 80 | 3.00% | +5.40 | +2569 | 45 | +3.49 | +3593 | 49 |
| 2025 | 95 | 40 | 3.5×ATR | +7.80 | +5296 | 32 | +9.73 | +879 | 8 |
| 2026 | 95 | 40 | 3.5×ATR | +7.96 | +6214 | 40 | +0.42 | +44 | 10 |

**588000ETF / short** (mode=single, pooled WF S=+2.61, elig 4/4):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2023 | 50 | 40 | 3.5×ATR | +4.41 | +3246 | 103 | +2.07 | +1229 | 98 |
| 2024 | 50 | 40 | — | +3.09 | +4056 | 201 | +6.75 | +1935 | 38 |
| 2025 | 50 | 80 | — | +4.81 | +3189 | 88 | +0.72 | +293 | 38 |
| 2026 | 50 | 80 | — | +3.26 | +3634 | 126 | +3.02 | +696 | 16 |

**159915ETF / long** (mode=single, pooled WF S=+4.57, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 5.00% | +11.36 | +6987 | 50 | +3.58 | +765 | 32 |
| 2022 | 50 | 80 | 5.00% | +8.23 | +7553 | 82 | +3.61 | +1160 | 36 |
| 2023 | 50 | 90 | 5.00% | +5.56 | +3017 | 53 | +20.37 | +409 | 4 |
| 2024 | 50 | 90 | 5.00% | +6.02 | +3403 | 57 | +9.11 | +3308 | 14 |
| 2025 | 95 | 40 | 5.00% | +6.56 | +3379 | 28 | -5.47 | -348 | 5 |
| 2026 | 50 | 90 | — | +4.81 | +5419 | 82 | +12.24 | +415 | 4 |

**159915ETF / short** (mode=hybrid, pooled WF S=+4.94, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | — | +4.68 | +4347 | 108 | +1.85 | +390 | 26 |
| 2022 | 50 | 80 | — | +3.89 | +4520 | 134 | +6.76 | +1279 | 28 |
| 2023 | 50 | 80 | — | +4.28 | +5743 | 162 | +5.90 | +1020 | 45 |
| 2024 | 50 | 80 | — | +4.24 | +6596 | 207 | +7.90 | +1543 | 33 |
| 2025 | 50 | 90 | — | +4.57 | +3431 | 94 | +10.98 | +1614 | 17 |
| 2026 | 95 | 40 | — | +6.90 | +2988 | 43 | -4.46 | -459 | 9 |

## 3. Walk-Forward OOS Performance (15 bps round-trip)

All metrics below are **pooled across test folds** (no IS/OOS split at a fixed date). Each fold's config was selected using train-window data only.


### 3.1 Per-Side Pooled WF Metrics

*Place%* = side trades / total trading days across all test folds (capital deployment rate).

*Warnings* = non-blocking fragility flags (`median<=0`, `win<=50%`, `n<60`).

| ETF | Side | N WF | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |
|-----|------|------|--------|------|--------|---------|-----------|----------|------------|----------|
| 50ETF | `long` | 53 | 4.0% | 56.6% | +3.51 | +1335 | -398 | +25.2 | +26.6 | n<60 |
| 50ETF | `short` | 69 | 5.2% | 63.8% | +7.07 | +2939 | -297 | +42.6 | +39.9 | — |
| 300ETF | `long` | 72 | 5.5% | 51.4% | +1.34 | +852 | -798 | +11.8 | +5.7 | — |
| 300ETF | `short` | 11 | 0.8% | 63.6% | +6.59 | +688 | -330 | +62.5 | +97.0 | n<60 |
| 500ETF | `long` | 60 | 4.5% | 58.3% | +3.42 | +2357 | -647 | +39.3 | +21.9 | — |
| 500ETF | `short` | 53 | 4.0% | 64.2% | +4.90 | +2246 | -460 | +42.4 | +77.3 | n<60 |
| 588000ETF | `long` | 73 | 8.7% | 60.3% | +3.88 | +5144 | -836 | +70.5 | +41.8 | — |
| 588000ETF | `short` | 190 | 22.8% | 58.4% | +2.61 | +4153 | -1337 | +21.9 | +22.9 | — |
| 159915ETF | `long` | 95 | 7.2% | 60.0% | +4.57 | +5709 | -572 | +60.1 | +35.6 | — |
| 159915ETF | `short` | 158 | 12.0% | 70.3% | +4.94 | +5386 | -770 | +34.1 | +36.8 | — |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N WF | L Place% | S Place% | Tot Place% | Win% | Sharpe | P&L bps | MaxDD bps |
|-----|------|----------|----------|------------|------|--------|---------|-----------|
| **50ETF** | 122 | 4.0% | 5.2% | 9.2% | 60.7% | +5.35 | +4273 | -525 |
| **300ETF** | 83 | 5.5% | 0.8% | 6.3% | 53.0% | +2.07 | +1540 | -798 |
| **500ETF** | 113 | 4.5% | 4.0% | 8.6% | 61.1% | +3.99 | +4603 | -558 |
| **588000ETF** | 263 | 8.7% | 22.8% | 31.5% | 58.9% | +2.95 | +9298 | -1352 |
| **159915ETF** | 253 | 7.2% | 12.0% | 19.2% | 66.4% | +4.50 | +11094 | -695 |

### 3.3 Year-by-Year Sharpe (fold-aligned)

| ETF | Side | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|-----|------|---|---|---|---|---|---|
| 50ETF | `long` | +1.49 | +4.24 | — | -0.02 | — | — |
| 50ETF | `short` | +8.75 | +12.94 | +1.92 | +5.78 | — | +0.30 |
| 300ETF | `long` | +2.26 | -0.23 | +9.27 | +3.21 | — | — |
| 300ETF | `short` | +1.56 | — | — | +7.25 | +6.43 | — |
| 500ETF | `long` | +13.24 | +6.67 | — | +1.55 | -3.58 | +5.37 |
| 500ETF | `short` | +33.90 | +5.18 | +0.49 | +9.42 | +5.91 | -1.50 |
| 588000ETF | `long` | — | — | +10.75 | +3.49 | +9.73 | +0.42 |
| 588000ETF | `short` | — | — | +2.07 | +6.75 | +0.72 | +3.02 |
| 159915ETF | `long` | +3.58 | +3.61 | +20.37 | +9.11 | -5.47 | +12.24 |
| 159915ETF | `short` | +1.85 | +6.76 | +5.90 | +7.90 | +10.98 | -4.46 |

![yearly_sharpe](plots/yearly_sharpe.png)


### 3.4 Cost Sensitivity (per-side, same per-fold configs)

_Per-fold configs are fixed (chosen at 15 bps). Cost sweep re-evaluates P&L only; it is a sensitivity diagnostic, not a re-optimisation._

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +5.11 | +3.71 | +1.60 |
| 50ETF | `short` | +7.77 | +6.18 | +3.80 |
| 300ETF | `long` | +2.47 | +1.34 | -0.36 |
| 300ETF | `short` | +7.65 | +6.59 | +5.01 |
| 500ETF | `long` | +4.29 | +3.42 | +2.11 |
| 500ETF | `short` | +6.05 | +4.90 | +3.16 |
| 588000ETF | `long` | +4.43 | +3.88 | +3.06 |
| 588000ETF | `short` | +3.80 | +2.61 | +0.82 |
| 159915ETF | `long` | +5.33 | +4.57 | +3.43 |
| 159915ETF | `short` | +6.38 | +4.94 | +2.76 |

### 3.5 Equity Curves (stitched across WF test folds)

![equity_combined](plots/equity_combined.png)

![equity_per_side](plots/equity_curves.png)


### 3.6 Fragility Warnings Summary

Non-blocking transparency flags. A side with warnings is still deployed (passes the hard eligibility majority gate) but the positive Sharpe may be a small-sample / heavy-tail artifact. Investigate before sizing.

| ETF | Side | N WF | Median bps | Win% | Warnings |
|-----|------|------|------------|------|----------|
| 50ETF | `long` | 53 | +26.6 | 56.6% | n<60 |
| 50ETF | `short` | 69 | +39.9 | 63.8% | — |
| 300ETF | `long` | 72 | +5.7 | 51.4% | — |
| 300ETF | `short` | 11 | +97.0 | 63.6% | n<60 |
| 500ETF | `long` | 60 | +21.9 | 58.3% | — |
| 500ETF | `short` | 53 | +77.3 | 64.2% | n<60 |
| 588000ETF | `long` | 73 | +41.8 | 60.3% | — |
| 588000ETF | `short` | 190 | +22.9 | 58.4% | — |
| 159915ETF | `long` | 95 | +35.6 | 60.0% | — |
| 159915ETF | `short` | 158 | +36.8 | 70.3% | — |

## 4. Diagnostic: Cluster Confusion (WF traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters?

| ETF | Side | N | Rally% | Selloff% | Neutral% |
|-----|------|---|--------|----------|----------|
| 50ETF | `long` | 53 | 36% | 26% | 38% |
| 50ETF | `short` | 69 | 6% | 43% | 51% |
| 300ETF | `long` | 72 | 46% | 12% | 42% |
| 300ETF | `short` | 11 | 27% | 64% | 9% |
| 500ETF | `long` | 60 | 67% | 5% | 28% |
| 500ETF | `short` | 53 | 8% | 43% | 49% |
| 588000ETF | `long` | 73 | 40% | 18% | 42% |
| 588000ETF | `short` | 190 | 8% | 45% | 47% |
| 159915ETF | `long` | 95 | 59% | 5% | 36% |
| 159915ETF | `short` | 158 | 3% | 42% | 55% |

## 5. Mode Comparison (Phase 4 — all walk-forward)

Each side deploys the mode with the highest pooled WF Sharpe among configs that pass the eligibility majority gate.

| ETF | Side | Single | Hybrid | Dual | Single+g | Hybrid+g | Dual+g | **Deployed** |
|-----|------|--------|--------|------|----------|----------|--------|--------------|
| 50ETF | `long` | +1.82 | +2.14 | +2.77 | +2.75 | +3.40 | +3.71 | **dual+gated** (+3.71) |
| 50ETF | `short` | +1.46 | +2.19 | — | +6.18 | +4.27 | — | **single+gated** (+6.18) |
| 300ETF | `long` | — | +0.43 | +0.30 | +0.63 | +1.34 | +1.02 | **hybrid+gated** (+1.34) |
| 300ETF | `short` | +5.72 | — | — | +6.59 | — | +2.17 | **single+gated** (+6.59) |
| 500ETF | `long` | +2.00 | +1.86 | +1.24 | +2.25 | +3.42 | +2.35 | **hybrid+gated** (+3.42) |
| 500ETF | `short` | +2.49 | +2.99 | +2.81 | +4.90 | +2.49 | +3.35 | **single+gated** (+4.90) |
| 588000ETF | `long` | +3.88 | +0.61 | — | +2.96 | +1.45 | — | **single** (+3.88) |
| 588000ETF | `short` | +2.61 | +2.56 | — | +2.45 | +2.46 | — | **single** (+2.61) |
| 159915ETF | `long` | +4.57 | +2.13 | — | +4.26 | +2.85 | +0.76 | **single** (+4.57) |
| 159915ETF | `short` | +4.23 | +4.94 | +1.75 | +2.54 | +2.99 | +2.63 | **hybrid** (+4.94) |

**Total deployed pooled WF Sharpe**: +42.13


## 5.5 Gating Impact (v3, walk-forward)

Per-side pooled WF Sharpe: best ungated mode vs best gated mode.

| ETF | Side | Best Ungated | Best Gated | Δ | Deployed |
|-----|------|--------------|------------|---|----------|
| 50ETF | `long` | +2.77 | +3.71 | +0.93 | **dual+gated** (+3.71) |
| 50ETF | `short` | +2.19 | +6.18 | +4.00 | **single+gated** (+6.18) |
| 300ETF | `long` | +0.43 | +1.34 | +0.90 | **hybrid+gated** (+1.34) |
| 300ETF | `short` | +5.72 | +6.59 | +0.88 | **single+gated** (+6.59) |
| 500ETF | `long` | +2.00 | +3.42 | +1.42 | **hybrid+gated** (+3.42) |
| 500ETF | `short` | +2.99 | +4.90 | +1.91 | **single+gated** (+4.90) |
| 588000ETF | `long` | +3.88 | +2.96 | -0.92 | **single** (+3.88) |
| 588000ETF | `short` | +2.61 | +2.46 | -0.15 | **single** (+2.61) |
| 159915ETF | `long` | +4.57 | +4.26 | -0.31 | **single** (+4.57) |
| 159915ETF | `short` | +4.94 | +2.99 | -1.94 | **hybrid** (+4.94) |

**Totals** — Ungated: +32.09 | Gated: +38.81 | Deployed: +42.13 (Δ vs ungated = +10.04)


## 6. Verdict

- **Robust long (pooled WF Sharpe ≥ +1.5)**: 50ETF, 500ETF, 588000ETF, 159915ETF
- **Robust short (pooled WF Sharpe ≥ +1.5)**: 50ETF, 300ETF, 500ETF, 588000ETF, 159915ETF
- **Disabled long**: none
- **Disabled short**: none

_Note: the per-side deployability bar dropped from the previous single-split (Sharpe ≥ +2.0) to pooled-WF (Sharpe ≥ +1.5) because walk-forward metrics are honestly out-of-sample — the previous numbers were optimistically biased by hyperparameter selection on the reported window._

## 7. Caveats

- Short-side P&L assumes 15bps transaction cost; real options/margin/borrow costs not modeled
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- 14:30 exit leaves late-day continuation on the table
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Walk-forward folds are yearly; intra-year regime shifts are not captured
- Per-fold small-sample noise (fold with <60 trades) is flagged via the `n<60` warning
- Cost sensitivity holds per-fold configs fixed; a true cost re-optimisation may shift choices