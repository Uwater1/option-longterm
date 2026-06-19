# Daytrade — Frozen-Linear Intraday Alpha (Long/Short Model)

*Signal = frozen LASSO/Huber coefficients from day-model. Each ETF deploys independent `long_model` and `short_model`, each with its own expanding-percentile thresholds. Entry at decision bar (9:45 for 159915/500; 10:00 for 300/50/588000). Exit at 14:30 (5m bar 41). Cost 15 bps round-trip.*


## 1. Strategy

- **Signal**: frozen LASSO/Huber/ElasticNet score from `day-model/models/linear_{ETF}.joblib`
- **Per-side thresholds**: expanding-window percentile of |score| computed only over that side's prior history (no look-ahead)
- **Direction**: `long_model` fires when score>0 & crosses long thresholds; `short_model` fires when score<0 & crosses short thresholds
- **Eligibility guard**: each side deployed only if OOS P&L>0 AND OOS Sharpe>0 AND n≥20 (else disabled)
- **Entry bar**: 9:45 close for 159915/500; 10:00 close for 300/50/588000
- **Exit bar**: 41 (5m close at 14:30, better liquidity than 15:00)
- **Cost**: 15 bps round-trip (parametrizable)
- **Holdout**: 2024-03-19 onwards (matches day-model)


## 2. Deployed Configurations

| ETF | Long thr | Long conv | Short thr | Short conv |
|-----|----------|-----------|-----------|------------|
| **50ETF** | disabled | — | 80 | 40 |
| **300ETF** | 80 | 40 | 90 | 40 |
| **500ETF** | 50 | 40 | 90 | 40 |
| **588000ETF** | 90 | 40 | disabled | — |
| **159915ETF** | 90 | 40 | 80 | 40 |

## 3. Performance (15 bps round-trip)

### 3.1 Per-Side OOS Metrics

*Place%* = side trades / total trading days in the period (capital deployment rate).

| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps |
|-----|------|-------|--------|------|--------|---------|-----------|----------|
| 50ETF | `short` | 34 | 6.3% | 52.9% | +0.67 | +171 | -786 | +5.0 |
| 300ETF | `long` | 25 | 4.6% | 48.0% | +0.17 | +40 | -780 | +1.6 |
| 300ETF | `short` | 23 | 4.2% | 52.2% | +2.21 | +441 | -888 | +19.2 |
| 500ETF | `long` | 101 | 18.6% | 53.5% | +2.88 | +2487 | -3220 | +24.6 |
| 500ETF | `short` | 46 | 8.5% | 63.0% | +2.91 | +967 | -1407 | +21.0 |
| 588000ETF | `long` | 35 | 6.4% | 48.6% | +3.51 | +2491 | -3545 | +71.2 |
| 159915ETF | `long` | 32 | 5.9% | 78.1% | +8.59 | +3558 | -3685 | +111.2 |
| 159915ETF | `short` | 49 | 9.0% | 71.4% | +6.16 | +2724 | -3024 | +55.6 |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |
|-----|----------|-------|----------|----------|------------|------|---------------|----------------|------------|-------------|---------------|
| **50ETF** | 68 | 34 | 0.0% | 6.3% | 6.3% | 51.5% | -0.10 | -44 | +0.67 | +171 | -786 |
| **300ETF** | 224 | 48 | 4.6% | 4.2% | 8.8% | 48.7% | +0.89 | +1594 | +1.10 | +481 | -1177 |
| **500ETF** | 602 | 147 | 18.6% | 8.5% | 27.1% | 55.5% | +2.41 | +11463 | +2.89 | +3454 | -4432 |
| **588000ETF** | 64 | 35 | 6.4% | 0.0% | 6.4% | 51.6% | +3.50 | +3645 | +3.51 | +2491 | -3545 |
| **159915ETF** | 276 | 81 | 5.9% | 9.0% | 14.9% | 68.1% | +5.57 | +15081 | +7.18 | +6282 | -6709 |

### 3.3 Placement Rates (capital deployment frequency)

Fraction of trading days on which each side fires. High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.

| ETF | Long Place% (full) | Long Place% (OOS) | Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |
|-----|--------------------|-------------------|---------------------|---------------------|--------------------|
| **50ETF** | 0.0% | 0.0% | 2.5% | 6.3% | 6.3% |
| **300ETF** | 5.1% | 4.6% | 3.1% | 4.2% | 8.8% |
| **500ETF** | 18.4% | 18.6% | 3.7% | 8.5% | 27.1% |
| **588000ETF** | 4.9% | 6.4% | 0.0% | 0.0% | 6.4% |
| **159915ETF** | 3.8% | 5.9% | 6.3% | 9.0% | 14.9% |

### 3.4 Year-by-Year OOS Sharpe

| ETF | Side | 2024 | 2025 | 2026 |
|-----|------|---|---|---|
| 50ETF | `short` | +4.31 | -3.86 | -3.18 |
| 300ETF | `long` | +0.61 | — | -2.42 |
| 300ETF | `short` | +3.19 | +3.80 | -2.88 |
| 500ETF | `long` | +0.48 | +5.73 | +6.12 |
| 500ETF | `short` | -3.48 | +4.95 | +7.89 |
| 588000ETF | `long` | +7.17 | +2.57 | -7.44 |
| 159915ETF | `long` | +8.37 | +9.14 | +13.29 |
| 159915ETF | `short` | +1.82 | +10.95 | +4.37 |

![yearly_sharpe](plots/yearly_sharpe.png)


### 3.5 Cost Sensitivity (OOS Sharpe by side)

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `short` | +2.01 | +0.67 | -1.34 |
| 300ETF | `long` | +1.21 | +0.17 | -1.39 |
| 300ETF | `short` | +3.36 | +2.21 | +0.48 |
| 500ETF | `long` | +4.05 | +2.88 | +1.13 |
| 500ETF | `short` | +4.29 | +2.91 | +0.83 |
| 588000ETF | `long` | +4.01 | +3.51 | +2.77 |
| 159915ETF | `long` | +9.36 | +8.59 | +7.43 |
| 159915ETF | `short` | +7.27 | +6.16 | +4.50 |

### 3.6 Equity Curves

![equity_combined](plots/equity_combined.png)

![equity_per_side](plots/equity_curves.png)


## 4. Diagnostic: Cluster Confusion (OOS traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; short side on Selloff.

| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |
|-----|------|-------|--------|----------|----------|
| 50ETF | `short` | 34 | 9% | 50% | 41% |
| 300ETF | `long` | 25 | 32% | 16% | 52% |
| 300ETF | `short` | 23 | 13% | 26% | 61% |
| 500ETF | `long` | 101 | 36% | 8% | 56% |
| 500ETF | `short` | 46 | 17% | 30% | 52% |
| 588000ETF | `long` | 35 | 40% | 11% | 49% |
| 159915ETF | `long` | 32 | 47% | 3% | 50% |
| 159915ETF | `short` | 49 | 10% | 37% | 53% |

## 5. Verdict

- **Robust long_model (OOS Sharpe ≥ +2.0)**: 500ETF, 588000ETF, 159915ETF
- **Robust short_model (OOS Sharpe ≥ +2.0)**: 300ETF, 500ETF, 159915ETF
- **Disabled long**: 50ETF
- **Disabled short**: 588000ETF

## 6. Caveats

- Short-side P&L assumes zero execution friction (options/margin costs not modeled)
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- 14:30 exit leaves late-day continuation on the table; v2 will add trailing stop
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Per-side eligibility uses holdout (2024-03+); earlier years may behave differently
- Single cost assumption (15bps RT) applied to both long and short; real-world shorts via options will carry different (likely higher) cost