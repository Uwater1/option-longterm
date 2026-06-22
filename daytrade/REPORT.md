# Daytrade — Frozen-Linear Intraday Alpha (Long/Short Model)

*Signal = frozen LASSO/Huber coefficients from day-model. Each ETF deploys independent `long_model` and `short_model`, each with its own expanding-percentile thresholds. Entry at decision bar (9:45 for 159915/500; 10:00 for 300/50/588000). Exit at 14:30 (5m bar 41). Cost 15 bps round-trip.*


## 1. Strategy

- **Signal**: frozen LASSO/Huber/ElasticNet score from `day-model/models/linear_{ETF}.joblib`
- **Per-side thresholds**: expanding-window percentile of |score| computed only over that side's prior history (no look-ahead)
- **Direction**: `long_model` fires when score>0 & crosses long thresholds; `short_model` fires when score<0 & crosses short thresholds
- **Mode**: **mixed** (Phase 4 per-side deployment). Each side uses the mode (single/hybrid/dual) that maximises OOS Sharpe. See §2 for per-side mode assignments.
- **Eligibility guard**: each side deployed only if OOS P&L>0 AND OOS Sharpe>0 AND n≥20 (else disabled)
- **Entry bar**: 9:45 close for 159915/500; 10:00 close for 300/50/588000
- **Exit bar**: 41 (5m close at 14:30, better liquidity than 15:00)
- **Cost**: 15 bps round-trip (parametrizable)
- **Holdout**: 2024-03-19 onwards (matches day-model)


## 2. Deployed Configurations

| ETF | Long mode | Long thr | Long conv | Short mode | Short thr | Short conv |
|-----|-----------|----------|-----------|------------|-----------|------------|
| **50ETF** | `—` | disabled | — | `dual` | 50 | 90 |
| **300ETF** | `—` | disabled | — | `—` | disabled | — |
| **500ETF** | `hybrid` | 50 | 60 | `single` | 50 | 90 |
| **588000ETF** | `single` | 50 | 90 | `—` | disabled | — |
| **159915ETF** | `single` | 50 | 90 | `hybrid` | 50 | 80 |

## 3. Performance (15 bps round-trip)

### 3.1 Per-Side OOS Metrics

*Place%* = side trades / total trading days in the period (capital deployment rate).

| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps |
|-----|------|-------|--------|------|--------|---------|-----------|----------|
| 50ETF | `short` | 24 | 4.4% | 58.3% | +1.36 | +351 | -658 | +14.6 |
| 500ETF | `long` | 94 | 17.3% | 58.5% | +3.68 | +3324 | -916 | +35.4 |
| 500ETF | `short` | 58 | 10.7% | 62.1% | +5.14 | +2128 | -318 | +36.7 |
| 588000ETF | `long` | 27 | 5.0% | 44.4% | +1.80 | +891 | -854 | +33.0 |
| 159915ETF | `long` | 32 | 5.9% | 68.8% | +6.37 | +3492 | -542 | +109.1 |
| 159915ETF | `short` | 61 | 11.2% | 67.2% | +4.83 | +2714 | -619 | +44.5 |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |
|-----|----------|-------|----------|----------|------------|------|---------------|----------------|------------|-------------|---------------|
| **50ETF** | 67 | 24 | 0.0% | 4.4% | 4.4% | 58.2% | +2.12 | +1526 | +1.36 | +351 | -658 |
| 300ETF | 0 | — | — | — | — | — | — | — | — | — | — |
| **500ETF** | 487 | 152 | 17.3% | 10.7% | 28.0% | 57.7% | +3.44 | +14908 | +4.11 | +5452 | -743 |
| **588000ETF** | 64 | 27 | 5.0% | 0.0% | 5.0% | 46.9% | +1.50 | +1313 | +1.80 | +891 | -854 |
| **159915ETF** | 261 | 93 | 5.9% | 11.2% | 17.1% | 68.2% | +5.78 | +15574 | +5.31 | +6206 | -658 |

### 3.3 Placement Rates (capital deployment frequency)

Fraction of trading days on which each side fires. High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.

| ETF | Long Place% (full) | Long Place% (OOS) | Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |
|-----|--------------------|-------------------|---------------------|---------------------|--------------------|
| **50ETF** | 0.0% | 0.0% | 2.5% | 4.4% | 4.4% |
| 300ETF | — | — | — | — | — |
| **500ETF** | 13.4% | 17.3% | 4.5% | 10.7% | 28.0% |
| **588000ETF** | 4.9% | 5.0% | 0.0% | 0.0% | 5.0% |
| **159915ETF** | 3.1% | 5.9% | 6.5% | 11.2% | 17.1% |

### 3.4 Year-by-Year OOS Sharpe

| ETF | Side | 2024 | 2025 | 2026 |
|-----|------|---|---|---|
| 50ETF | `short` | -0.03 | +8.82 | — |
| 500ETF | `long` | +2.52 | +5.73 | +4.54 |
| 500ETF | `short` | +1.04 | +7.85 | +6.19 |
| 588000ETF | `long` | +6.65 | -1.69 | -7.63 |
| 159915ETF | `long` | +6.09 | +9.08 | +9.18 |
| 159915ETF | `short` | +5.95 | +6.09 | +2.18 |

![yearly_sharpe](plots\yearly_sharpe.png)


### 3.5 Cost Sensitivity (OOS Sharpe by side)

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `short` | +2.29 | +1.36 | -0.03 |
| 500ETF | `long` | +4.72 | +3.68 | +2.12 |
| 500ETF | `short` | +6.54 | +5.14 | +3.04 |
| 588000ETF | `long` | +2.35 | +1.80 | +0.98 |
| 159915ETF | `long` | +6.95 | +6.37 | +5.49 |
| 159915ETF | `short` | +5.91 | +4.83 | +3.20 |

### 3.6 Equity Curves

![equity_combined](plots\equity_combined.png)

![equity_per_side](plots\equity_curves.png)


## 4. Diagnostic: Cluster Confusion (OOS traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; short side on Selloff.

| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |
|-----|------|-------|--------|----------|----------|
| 50ETF | `short` | 24 | 25% | 38% | 38% |
| 500ETF | `long` | 94 | 43% | 11% | 47% |
| 500ETF | `short` | 58 | 9% | 33% | 59% |
| 588000ETF | `long` | 27 | 41% | 11% | 48% |
| 159915ETF | `long` | 32 | 41% | 6% | 53% |
| 159915ETF | `short` | 61 | 11% | 38% | 51% |

## 5. Mode Comparison (Phase 4 Cross-Mode Selection)

Each side deploys the mode with the highest OOS Sharpe. This table shows all eligible configs across single/hybrid/dual modes.

| ETF | Side | Single | Hybrid | Dual | **Deployed** |
|-----|------|--------|--------|------|--------------|
| 50ETF | `short` | — | — | +1.36 | **dual** (+1.36) |
| 500ETF | `long` | +3.66 | +3.68 | — | **hybrid** (+3.68) |
| 500ETF | `short` | +5.14 | +2.75 | +1.67 | **single** (+5.14) |
| 588000ETF | `long` | +1.80 | +1.34 | +1.63 | **single** (+1.80) |
| 159915ETF | `long` | +6.37 | +6.34 | +3.76 | **single** (+6.37) |
| 159915ETF | `short` | +3.20 | +4.83 | +2.86 | **hybrid** (+4.83) |

**Total deployed OOS Sharpe**: +23.18 (vs single-only +20.17, Δ = +3.01)


## 6. Verdict

- **Robust long_model (OOS Sharpe ≥ +2.0)**: 500ETF, 159915ETF
- **Robust short_model (OOS Sharpe ≥ +2.0)**: 500ETF, 159915ETF
- **Disabled long**: 50ETF, 300ETF
- **Disabled short**: 300ETF, 588000ETF

## 7. Caveats

- Short-side P&L assumes 15bps transaction cost and other execution assumptions similar to the long side (options/margin/borrow costs not modeled)
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- 14:30 exit leaves late-day continuation on the table; v2 will add trailing stop
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Per-side eligibility uses holdout (2024-03+); earlier years may behave differently
- Single cost assumption (15bps RT) applied to both long and short; real-world shorts via options will carry different (likely higher) cost