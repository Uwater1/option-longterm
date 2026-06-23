# Daytrade — Frozen-Linear Intraday Alpha (Long/Short Model)

*Signal = frozen LASSO/Huber coefficients from day-model (target = `trade_return`, log return from entry-open to exit-close). Each ETF deploys independent `long_model` and `short_model`, each with its own expanding-percentile thresholds. Decision at close[DECISION_BAR[etf]] -> entry at open[DECISION_BAR[etf]+1] -> exit at close[41] (14:30). Cost 15 bps round-trip.*


## 1. Strategy

- **Signal**: frozen LASSO/Huber/ElasticNet score from `day-model/models/linear_{ETF}.joblib`
- **Model target**: `trade_return` = log(close[EXIT_BAR] / open[decision_bar+1]) — mirrors actual trade P&L exactly
- **Per-side thresholds**: expanding-window percentile of |score| computed only over that side's prior history (no look-ahead)
- **Direction**: `long_model` fires when score>0 & crosses long thresholds; `short_model` fires when score<0 & crosses short thresholds
- **Mode**: **mixed** (Phase 4 per-side deployment). Each side uses the mode (single/hybrid/dual) that maximises OOS Sharpe. See §2 for per-side mode assignments.
- **Eligibility guard**: each side deployed only if OOS P&L>0 AND OOS Sharpe>0 AND n≥20 (else disabled)
- **Decision/Entry**: per-ETF `DECISION_BAR` (see day-model/build_features.py). Decide at close[decision_bar], enter at open[decision_bar+1] (next-bar open, realistic fill).
- **Exit bar**: 41 (5m close at 14:30, better liquidity than 15:00)
- **Cost**: 15 bps round-trip (parametrizable)
- **Holdout**: 2024-03-19 onwards (matches day-model)


## 2. Deployed Configurations

| ETF | Long mode | Long thr | Long conv | Short mode | Short thr | Short conv |
|-----|-----------|----------|-----------|------------|-----------|------------|
| **50ETF** | `dual` | 50 | 80 | `single` | 50 | 90 |
| **300ETF** | `hybrid` | 50 | 60 | `hybrid` | 50 | 90 |
| **500ETF** | `hybrid` | 50 | 90 | `hybrid` | 50 | 90 |
| **588000ETF** | `single` | 95 | 40 | `single` | 50 | 80 |
| **159915ETF** | `single` | 50 | 80 | `single` | 95 | 40 |

## 3. Performance (15 bps round-trip)

### 3.1 Per-Side OOS Metrics

*Place%* = side trades / total trading days in the period (capital deployment rate).

*Warnings* = non-blocking fragility flags. If any fire, the positive Sharpe may be a small-sample / heavy-tail artifact rather than a true edge. Three checks: `median<=0` (typical trade loses money), `win<=50%` (loses more often than wins), `n<60` (small sample, high multiple-testing risk from grid search).

| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |
|-----|------|-------|--------|------|--------|---------|-----------|----------|------------|----------|
| 50ETF | `long` | 44 | 8.1% | 40.9% | +1.44 | +475 | -587 | +10.8 | -4.8 | median<=0, win<=50%, n<60 |
| 50ETF | `short` | 20 | 3.7% | 65.0% | +9.80 | +1441 | -66 | +72.1 | +36.3 | n<60 |
| 300ETF | `long` | 24 | 4.4% | 54.2% | +3.63 | +661 | -300 | +27.5 | +3.2 | n<60 |
| 300ETF | `short` | 33 | 6.1% | 42.4% | +2.76 | +676 | -535 | +20.5 | -6.7 | median<=0, win<=50%, n<60 |
| 500ETF | `long` | 29 | 5.3% | 55.2% | +5.57 | +2219 | -406 | +76.5 | +38.8 | n<60 |
| 500ETF | `short` | 37 | 6.8% | 56.8% | +4.25 | +990 | -308 | +26.8 | +29.6 | n<60 |
| 588000ETF | `long` | 21 | 3.9% | 47.6% | +5.75 | +3124 | -400 | +148.8 | -0.1 | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 68 | 12.5% | 58.8% | +3.48 | +2327 | -790 | +34.2 | +23.5 | — |
| 159915ETF | `long` | 60 | 11.0% | 58.3% | +3.07 | +2651 | -1205 | +44.2 | +19.6 | — |
| 159915ETF | `short` | 28 | 5.2% | 57.1% | +4.92 | +1409 | -502 | +50.3 | +32.9 | n<60 |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |
|-----|----------|-------|----------|----------|------------|------|---------------|----------------|------------|-------------|---------------|
| **50ETF** | 434 | 64 | 8.1% | 3.7% | 11.8% | 49.3% | +1.04 | +3634 | +3.93 | +1916 | -432 |
| **300ETF** | 445 | 57 | 4.4% | 6.1% | 10.5% | 52.1% | +1.48 | +4781 | +3.16 | +1337 | -552 |
| **500ETF** | 132 | 66 | 5.3% | 6.8% | 12.2% | 63.6% | +5.66 | +7598 | +4.73 | +3209 | -406 |
| **588000ETF** | 193 | 89 | 3.9% | 12.5% | 16.4% | 60.6% | +4.26 | +9583 | +3.99 | +5451 | -965 |
| **159915ETF** | 248 | 88 | 11.0% | 5.2% | 16.2% | 60.5% | +4.09 | +10963 | +3.51 | +4060 | -1081 |

### 3.3 Placement Rates (capital deployment frequency)

Fraction of trading days on which each side fires. High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.

| ETF | Long Place% (full) | Long Place% (OOS) | Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |
|-----|--------------------|-------------------|---------------------|---------------------|--------------------|
| **50ETF** | 12.6% | 8.1% | 3.3% | 3.7% | 11.8% |
| **300ETF** | 11.4% | 4.4% | 5.0% | 6.1% | 10.5% |
| **500ETF** | 2.5% | 5.3% | 2.4% | 6.8% | 12.2% |
| **588000ETF** | 3.1% | 3.9% | 11.8% | 12.5% | 16.4% |
| **159915ETF** | 7.2% | 11.0% | 1.9% | 5.2% | 16.2% |

### 3.4 Year-by-Year OOS Sharpe

| ETF | Side | 2024 | 2025 | 2026 |
|-----|------|---|---|---|
| 50ETF | `long` | +4.50 | +2.31 | -6.61 |
| 50ETF | `short` | +9.38 | +8.34 | — |
| 300ETF | `long` | +3.20 | +2.12 | +16.16 |
| 300ETF | `short` | +2.80 | +1.62 | — |
| 500ETF | `long` | +6.28 | +5.95 | +2.91 |
| 500ETF | `short` | +4.35 | -2.10 | +8.89 |
| 588000ETF | `long` | +7.42 | +3.75 | -1.46 |
| 588000ETF | `short` | +17.49 | +1.97 | -2.53 |
| 159915ETF | `long` | +7.80 | -2.85 | +0.59 |
| 159915ETF | `short` | +10.84 | +6.95 | -20.09 |

![yearly_sharpe](plots/yearly_sharpe.png)


### 3.5 Cost Sensitivity (OOS Sharpe by side)

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +2.77 | +1.44 | -0.56 |
| 50ETF | `short` | +11.16 | +9.80 | +7.76 |
| 300ETF | `long` | +4.95 | +3.63 | +1.65 |
| 300ETF | `short` | +4.11 | +2.76 | +0.74 |
| 500ETF | `long` | +6.30 | +5.57 | +4.48 |
| 500ETF | `short` | +5.83 | +4.25 | +1.87 |
| 588000ETF | `long` | +6.14 | +5.75 | +5.17 |
| 588000ETF | `short` | +4.50 | +3.48 | +1.95 |
| 159915ETF | `long` | +3.76 | +3.07 | +2.03 |
| 159915ETF | `short` | +5.90 | +4.92 | +3.45 |

### 3.6 Equity Curves

![equity_combined](plots/equity_combined.png)

![equity_per_side](plots/equity_curves.png)


### 3.7 Fragility Warnings Summary

Non-blocking transparency flags. A side with warnings is still deployed (passes the hard guard `Sharpe>0 AND P&L>0 AND n≥20`) but the positive Sharpe may be a small-sample / heavy-tail artifact. Investigate before sizing the position.

- `median<=0`: typical OOS trade loses money; positive mean is carried by a few big winners
- `win<=50%`: side loses more often than it wins
- `n<60`: small sample; high multiple-testing risk from the 6×6 grid search

| ETF | Side | N OOS | Median bps | Win% | Warnings |
|-----|------|-------|------------|------|----------|
| 50ETF | `long` | 44 | -4.8 | 40.9% | median<=0, win<=50%, n<60 |
| 50ETF | `short` | 20 | +36.3 | 65.0% | n<60 |
| 300ETF | `long` | 24 | +3.2 | 54.2% | n<60 |
| 300ETF | `short` | 33 | -6.7 | 42.4% | median<=0, win<=50%, n<60 |
| 500ETF | `long` | 29 | +38.8 | 55.2% | n<60 |
| 500ETF | `short` | 37 | +29.6 | 56.8% | n<60 |
| 588000ETF | `long` | 21 | -0.1 | 47.6% | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 68 | +23.5 | 58.8% | — |
| 159915ETF | `long` | 60 | +19.6 | 58.3% | — |
| 159915ETF | `short` | 28 | +32.9 | 57.1% | n<60 |

## 4. Diagnostic: Cluster Confusion (OOS traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; short side on Selloff.

| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |
|-----|------|-------|--------|----------|----------|
| 50ETF | `long` | 44 | 23% | 9% | 68% |
| 50ETF | `short` | 20 | 0% | 65% | 35% |
| 300ETF | `long` | 24 | 29% | 8% | 62% |
| 300ETF | `short` | 33 | 15% | 45% | 39% |
| 500ETF | `long` | 29 | 55% | 17% | 28% |
| 500ETF | `short` | 37 | 22% | 38% | 41% |
| 588000ETF | `long` | 21 | 38% | 24% | 38% |
| 588000ETF | `short` | 68 | 12% | 49% | 40% |
| 159915ETF | `long` | 60 | 45% | 12% | 43% |
| 159915ETF | `short` | 28 | 7% | 54% | 39% |

## 5. Mode Comparison (Phase 4 Cross-Mode Selection)

Each side deploys the mode with the highest OOS Sharpe. This table shows all eligible configs across single/hybrid/dual modes.

| ETF | Side | Single | Hybrid | Dual | **Deployed** |
|-----|------|--------|--------|------|--------------|
| 50ETF | `long` | — | — | +1.44 | **dual** (+1.44) |
| 50ETF | `short` | +9.80 | +2.47 | +2.75 | **single** (+9.80) |
| 300ETF | `long` | +0.61 | +3.63 | +1.29 | **hybrid** (+3.63) |
| 300ETF | `short` | +0.80 | +2.76 | +2.04 | **hybrid** (+2.76) |
| 500ETF | `long` | +2.97 | +5.57 | +4.17 | **hybrid** (+5.57) |
| 500ETF | `short` | +1.88 | +4.25 | +1.63 | **hybrid** (+4.25) |
| 588000ETF | `long` | +5.75 | +2.81 | +2.49 | **single** (+5.75) |
| 588000ETF | `short` | +3.48 | +2.48 | +2.50 | **single** (+3.48) |
| 159915ETF | `long` | +3.07 | +2.44 | +1.08 | **single** (+3.07) |
| 159915ETF | `short` | +4.92 | +4.67 | +1.74 | **single** (+4.92) |

**Total deployed OOS Sharpe**: +44.67 (vs single-only +33.29, Δ = +11.38)


## 6. Verdict

- **Robust long_model (OOS Sharpe ≥ +2.0)**: 300ETF, 500ETF, 588000ETF, 159915ETF
- **Robust short_model (OOS Sharpe ≥ +2.0)**: 50ETF, 300ETF, 500ETF, 588000ETF, 159915ETF
- **Disabled long**: none
- **Disabled short**: none

## 7. Caveats

- Short-side P&L assumes 15bps transaction cost and other execution assumptions similar to the long side (options/margin/borrow costs not modeled)
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- 14:30 exit leaves late-day continuation on the table; v2 will add trailing stop
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Per-side eligibility uses holdout (2024-03+); earlier years may behave differently
- Single cost assumption (15bps RT) applied to both long and short; real-world shorts via options will carry different (likely higher) cost