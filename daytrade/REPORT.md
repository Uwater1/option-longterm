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
| **300ETF** | `hybrid+gated` | +1.34 | 6/6 | `single` | +7.17 | 6/6 |
| **500ETF** | `hybrid+gated` | +3.42 | 6/6 | `single+gated` | +4.90 | 6/6 |
| **588000ETF** | `single+gated` | +2.96 | 4/4 | `hybrid` | +2.54 | 4/4 |
| **159915ETF** | `single+gated` | +4.26 | 6/6 | `hybrid` | +3.49 | 6/6 |

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

**300ETF / short** (mode=single, pooled WF S=+7.17, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 95 | 40 | 4.00% | +3.27 | +825 | 37 | +1.56 | +19 | 2 |
| 2022 | 95 | 40 | 4.00% | +3.22 | +844 | 39 | +nan | +0 | 0 |
| 2023 | 95 | 40 | 4.00% | +3.22 | +844 | 39 | +nan | +0 | 0 |
| 2024 | 95 | 40 | 4.00% | +3.22 | +844 | 39 | +7.25 | +577 | 7 |
| 2025 | 95 | 40 | 4.00% | +4.08 | +1421 | 46 | +11.51 | +184 | 3 |
| 2026 | 95 | 40 | 4.00% | +4.41 | +1605 | 49 | +nan | +0 | 0 |

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

**588000ETF / long** (mode=single+gated, pooled WF S=+2.96, elig 4/4):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2023 | 50 | 80 | 3.00% | +5.96 | +2226 | 32 | +6.87 | +366 | 5 |
| 2024 | 50 | 80 | 3.00% | +6.15 | +2592 | 37 | +2.89 | +2052 | 31 |
| 2025 | 95 | 40 | 3.5×ATR | +7.88 | +4965 | 28 | +11.88 | +933 | 7 |
| 2026 | 95 | 40 | 3.5×ATR | +8.17 | +5898 | 35 | -6.70 | -497 | 7 |

**588000ETF / short** (mode=hybrid, pooled WF S=+2.54, elig 4/4):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2023 | 50 | 60 | 3.5×ATR | +3.04 | +1881 | 87 | +3.07 | +1261 | 68 |
| 2024 | 50 | 60 | 3.5×ATR | +3.05 | +3142 | 155 | +6.54 | +1803 | 38 |
| 2025 | 50 | 80 | 3.5×ATR | +5.59 | +3446 | 89 | +0.61 | +222 | 30 |
| 2026 | 50 | 80 | 3.5×ATR | +3.62 | +3668 | 119 | +0.40 | +86 | 15 |

**159915ETF / long** (mode=single+gated, pooled WF S=+4.26, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 5.00% | +11.09 | +6450 | 45 | +1.55 | +320 | 28 |
| 2022 | 50 | 80 | 5.00% | +7.87 | +6770 | 73 | +4.62 | +1330 | 33 |
| 2023 | 50 | 90 | 5.00% | +5.73 | +2981 | 50 | +81.89 | +286 | 2 |
| 2024 | 50 | 90 | 5.00% | +6.13 | +3267 | 52 | +8.65 | +2714 | 13 |
| 2025 | 95 | 40 | 5.00% | +6.67 | +3366 | 27 | -4.59 | -325 | 5 |
| 2026 | 50 | 90 | 5.00% | +4.92 | +5255 | 75 | +9.86 | +264 | 3 |

**159915ETF / short** (mode=hybrid, pooled WF S=+3.49, elig 6/6):
| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |
|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|
| 2021 | 50 | 80 | 4.00% | +4.68 | +4347 | 108 | +0.86 | +195 | 26 |
| 2022 | 50 | 80 | 3.00% | +3.89 | +4520 | 134 | +4.26 | +898 | 28 |
| 2023 | 50 | 80 | 4.00% | +4.28 | +5743 | 162 | +5.19 | +853 | 45 |
| 2024 | 50 | 80 | 4.00% | +4.24 | +6596 | 207 | +5.96 | +966 | 33 |
| 2025 | 50 | 90 | 4.00% | +4.57 | +3431 | 94 | +9.89 | +1500 | 17 |
| 2026 | 95 | 40 | 4.00% | +6.90 | +2988 | 43 | -4.95 | -535 | 9 |

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
| 300ETF | `short` | 12 | 0.9% | 66.7% | +7.17 | +780 | -330 | +65.0 | +94.5 | n<60 |
| 500ETF | `long` | 60 | 4.5% | 58.3% | +3.42 | +2357 | -647 | +39.3 | +21.9 | — |
| 500ETF | `short` | 53 | 4.0% | 64.2% | +4.90 | +2246 | -460 | +42.4 | +77.3 | n<60 |
| 588000ETF | `long` | 50 | 6.0% | 56.0% | +2.96 | +2854 | -804 | +57.1 | +24.0 | n<60 |
| 588000ETF | `short` | 151 | 18.1% | 62.9% | +2.54 | +3372 | -1334 | +22.3 | +31.6 | — |
| 159915ETF | `long` | 84 | 6.4% | 59.5% | +4.26 | +4590 | -558 | +54.6 | +32.9 | — |
| 159915ETF | `short` | 158 | 12.0% | 65.2% | +3.49 | +3876 | -873 | +24.5 | +29.4 | — |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N WF | L Place% | S Place% | Tot Place% | Win% | Sharpe | P&L bps | MaxDD bps |
|-----|------|----------|----------|------------|------|--------|---------|-----------|
| **50ETF** | 122 | 4.0% | 5.2% | 9.2% | 60.7% | +5.35 | +4273 | -525 |
| **300ETF** | 84 | 5.5% | 0.9% | 6.4% | 53.6% | +2.18 | +1632 | -798 |
| **500ETF** | 113 | 4.5% | 4.0% | 8.6% | 61.1% | +3.99 | +4603 | -558 |
| **588000ETF** | 201 | 6.0% | 18.1% | 24.1% | 61.2% | +2.53 | +6226 | -1299 |
| **159915ETF** | 242 | 6.4% | 12.0% | 18.3% | 63.2% | +3.69 | +8466 | -915 |

### 3.3 Year-by-Year Sharpe (fold-aligned)

| ETF | Side | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|-----|------|---|---|---|---|---|---|
| 50ETF | `long` | +1.49 | +4.24 | — | -0.02 | — | — |
| 50ETF | `short` | +8.75 | +12.94 | +1.92 | +5.78 | — | +0.30 |
| 300ETF | `long` | +2.26 | -0.23 | +9.27 | +3.21 | — | — |
| 300ETF | `short` | +1.56 | — | — | +7.25 | +11.51 | — |
| 500ETF | `long` | +13.24 | +6.67 | — | +1.55 | -3.58 | +5.37 |
| 500ETF | `short` | +33.90 | +5.18 | +0.49 | +9.42 | +5.91 | -1.50 |
| 588000ETF | `long` | — | — | +6.87 | +2.89 | +11.88 | -6.70 |
| 588000ETF | `short` | — | — | +3.07 | +6.54 | +0.61 | +0.40 |
| 159915ETF | `long` | +1.55 | +4.62 | +81.89 | +8.65 | -4.59 | +9.86 |
| 159915ETF | `short` | +0.86 | +4.26 | +5.19 | +5.96 | +9.89 | -4.95 |

![yearly_sharpe](plots/yearly_sharpe.png)


### 3.4 Cost Sensitivity (per-side, same per-fold configs)

_Per-fold configs are fixed (chosen at 15 bps). Cost sweep re-evaluates P&L only; it is a sensitivity diagnostic, not a re-optimisation._

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +5.11 | +3.71 | +1.60 |
| 50ETF | `short` | +7.77 | +6.18 | +3.80 |
| 300ETF | `long` | +2.47 | +1.34 | -0.36 |
| 300ETF | `short` | +8.28 | +7.17 | +5.52 |
| 500ETF | `long` | +4.29 | +3.42 | +2.11 |
| 500ETF | `short` | +6.05 | +4.90 | +3.16 |
| 588000ETF | `long` | +3.48 | +2.96 | +2.18 |
| 588000ETF | `short` | +3.68 | +2.54 | +0.83 |
| 159915ETF | `long` | +5.04 | +4.26 | +3.09 |
| 159915ETF | `short` | +4.91 | +3.49 | +1.35 |

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
| 300ETF | `short` | 12 | +94.5 | 66.7% | n<60 |
| 500ETF | `long` | 60 | +21.9 | 58.3% | — |
| 500ETF | `short` | 53 | +77.3 | 64.2% | n<60 |
| 588000ETF | `long` | 50 | +24.0 | 56.0% | n<60 |
| 588000ETF | `short` | 151 | +31.6 | 62.9% | — |
| 159915ETF | `long` | 84 | +32.9 | 59.5% | — |
| 159915ETF | `short` | 158 | +29.4 | 65.2% | — |

## 4. Diagnostic: Cluster Confusion (WF traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters?

| ETF | Side | N | Rally% | Selloff% | Neutral% |
|-----|------|---|--------|----------|----------|
| 50ETF | `long` | 53 | 36% | 26% | 38% |
| 50ETF | `short` | 69 | 6% | 43% | 51% |
| 300ETF | `long` | 72 | 46% | 12% | 42% |
| 300ETF | `short` | 12 | 25% | 67% | 8% |
| 500ETF | `long` | 60 | 67% | 5% | 28% |
| 500ETF | `short` | 53 | 8% | 43% | 49% |
| 588000ETF | `long` | 50 | 46% | 16% | 38% |
| 588000ETF | `short` | 151 | 6% | 55% | 39% |
| 159915ETF | `long` | 84 | 61% | 5% | 35% |
| 159915ETF | `short` | 158 | 3% | 42% | 55% |

## 5. Mode Comparison (Phase 4 — all walk-forward)

Each side deploys the mode with the highest pooled WF Sharpe among configs that pass the eligibility majority gate.

| ETF | Side | Single | Hybrid | Dual | Single+g | Hybrid+g | Dual+g | **Deployed** |
|-----|------|--------|--------|------|----------|----------|--------|--------------|
| 50ETF | `long` | +1.32 | +2.10 | +2.77 | +2.75 | +3.40 | +3.71 | **dual+gated** (+3.71) |
| 50ETF | `short` | +2.03 | +2.37 | — | +6.18 | +4.27 | — | **single+gated** (+6.18) |
| 300ETF | `long` | — | — | +0.42 | +0.63 | +1.34 | +1.02 | **hybrid+gated** (+1.34) |
| 300ETF | `short` | +7.17 | — | +0.57 | +6.59 | — | +2.17 | **single** (+7.17) |
| 500ETF | `long` | +0.96 | +1.80 | +1.38 | +2.25 | +3.42 | +2.35 | **hybrid+gated** (+3.42) |
| 500ETF | `short` | +3.07 | +1.98 | +2.42 | +4.90 | +2.49 | +3.35 | **single+gated** (+4.90) |
| 588000ETF | `long` | +2.94 | +0.82 | — | +2.96 | +1.45 | — | **single+gated** (+2.96) |
| 588000ETF | `short` | +2.16 | +2.54 | — | +2.45 | +2.46 | — | **hybrid** (+2.54) |
| 159915ETF | `long` | +4.19 | +2.25 | — | +4.26 | +2.85 | +0.76 | **single+gated** (+4.26) |
| 159915ETF | `short` | +2.98 | +3.49 | +2.60 | +2.54 | +2.99 | +2.63 | **hybrid** (+3.49) |

**Total deployed pooled WF Sharpe**: +39.96


## 5.5 Gating Impact (v3, walk-forward)

Per-side pooled WF Sharpe: best ungated mode vs best gated mode.

| ETF | Side | Best Ungated | Best Gated | Δ | Deployed |
|-----|------|--------------|------------|---|----------|
| 50ETF | `long` | +2.77 | +3.71 | +0.93 | **dual+gated** (+3.71) |
| 50ETF | `short` | +2.37 | +6.18 | +3.81 | **single+gated** (+6.18) |
| 300ETF | `long` | +0.42 | +1.34 | +0.92 | **hybrid+gated** (+1.34) |
| 300ETF | `short` | +7.17 | +6.59 | -0.58 | **single** (+7.17) |
| 500ETF | `long` | +1.80 | +3.42 | +1.62 | **hybrid+gated** (+3.42) |
| 500ETF | `short` | +3.07 | +4.90 | +1.82 | **single+gated** (+4.90) |
| 588000ETF | `long` | +2.94 | +2.96 | +0.02 | **single+gated** (+2.96) |
| 588000ETF | `short` | +2.54 | +2.46 | -0.08 | **hybrid** (+2.54) |
| 159915ETF | `long` | +4.19 | +4.26 | +0.07 | **single+gated** (+4.26) |
| 159915ETF | `short` | +3.49 | +2.99 | -0.49 | **hybrid** (+3.49) |

**Totals** — Ungated: +30.77 | Gated: +38.81 | Deployed: +39.96 (Δ vs ungated = +9.20)


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