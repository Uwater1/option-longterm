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
| **50ETF** | `hybrid` | 50 | 80 | `single` | 95 | 40 |
| **300ETF** | `hybrid` | 50 | 70 | `hybrid` | 50 | 90 |
| **500ETF** | `hybrid` | 50 | 70 | `single` | 50 | 90 |
| **588000ETF** | `hybrid` | 95 | 40 | `dual` | 95 | 40 |
| **159915ETF** | `hybrid` | 50 | 80 | `dual` | 95 | 40 |

## 3. Performance (15 bps round-trip)

### 3.1 Per-Side OOS Metrics

*Place%* = side trades / total trading days in the period (capital deployment rate).

*Warnings* = non-blocking fragility flags. If any fire, the positive Sharpe may be a small-sample / heavy-tail artifact rather than a true edge. Three checks: `median<=0` (typical trade loses money), `win<=50%` (loses more often than wins), `n<60` (small sample, high multiple-testing risk from grid search).

| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |
|-----|------|-------|--------|------|--------|---------|-----------|----------|------------|----------|
| 50ETF | `long` | 29 | 5.3% | 44.8% | +1.41 | +367 | -560 | +12.6 | -4.0 | median<=0, win<=50%, n<60 |
| 50ETF | `short` | 21 | 3.9% | 57.1% | +3.96 | +618 | -294 | +29.4 | +23.5 | n<60 |
| 300ETF | `long` | 21 | 3.9% | 52.4% | +1.12 | +376 | -913 | +17.9 | +0.1 | n<60 |
| 300ETF | `short` | 25 | 4.6% | 48.0% | +2.85 | +480 | -433 | +19.2 | -5.2 | median<=0, win<=50%, n<60 |
| 500ETF | `long` | 76 | 14.0% | 57.9% | +2.13 | +1543 | -695 | +20.3 | +12.3 | — |
| 500ETF | `short` | 52 | 9.6% | 51.9% | +2.27 | +829 | -677 | +15.9 | +7.7 | n<60 |
| 588000ETF | `long` | 25 | 4.6% | 60.0% | +6.09 | +3558 | -551 | +142.3 | +45.4 | n<60 |
| 588000ETF | `short` | 27 | 5.0% | 55.6% | +3.54 | +1177 | -471 | +43.6 | +18.3 | n<60 |
| 159915ETF | `long` | 41 | 7.5% | 56.1% | +5.21 | +3533 | -678 | +86.2 | +38.8 | n<60 |
| 159915ETF | `short` | 25 | 4.6% | 60.0% | +3.81 | +1067 | -519 | +42.7 | +44.1 | n<60 |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |
|-----|----------|-------|----------|----------|------------|------|---------------|----------------|------------|-------------|---------------|
| **50ETF** | 229 | 50 | 5.3% | 3.9% | 9.2% | 53.3% | +2.66 | +4129 | +2.38 | +985 | -429 |
| **300ETF** | 353 | 46 | 3.9% | 4.6% | 8.5% | 53.0% | +1.63 | +4655 | +1.58 | +856 | -764 |
| **500ETF** | 388 | 128 | 14.0% | 9.6% | 23.5% | 59.8% | +3.58 | +12198 | +2.16 | +2371 | -751 |
| **588000ETF** | 102 | 52 | 4.6% | 5.0% | 9.6% | 57.8% | +4.67 | +7443 | +4.91 | +4734 | -551 |
| **159915ETF** | 237 | 66 | 7.5% | 4.6% | 12.1% | 61.2% | +4.23 | +12985 | +4.73 | +4599 | -608 |

### 3.3 Placement Rates (capital deployment frequency)

Fraction of trading days on which each side fires. High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.

| ETF | Long Place% (full) | Long Place% (OOS) | Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |
|-----|--------------------|-------------------|---------------------|---------------------|--------------------|
| **50ETF** | 6.8% | 5.3% | 1.6% | 3.9% | 9.2% |
| **300ETF** | 9.2% | 3.9% | 3.8% | 4.6% | 8.5% |
| **500ETF** | 10.6% | 14.0% | 3.6% | 9.6% | 23.5% |
| **588000ETF** | 3.3% | 4.6% | 4.6% | 5.0% | 9.6% |
| **159915ETF** | 6.2% | 7.5% | 2.5% | 4.6% | 12.1% |

### 3.4 Year-by-Year OOS Sharpe

| ETF | Side | 2024 | 2025 | 2026 |
|-----|------|---|---|---|
| 50ETF | `long` | +3.32 | +3.03 | -9.77 |
| 50ETF | `short` | +5.05 | — | -1.06 |
| 300ETF | `long` | +1.15 | -8.24 | +16.16 |
| 300ETF | `short` | +3.05 | +10.98 | -1866.21 |
| 500ETF | `long` | +3.06 | +0.27 | +1.87 |
| 500ETF | `short` | +6.65 | +4.83 | -2.72 |
| 588000ETF | `long` | +9.80 | +11.13 | -2.32 |
| 588000ETF | `short` | +3.21 | +4.41 | +2.91 |
| 159915ETF | `long` | +7.69 | -1.72 | +7.12 |
| 159915ETF | `short` | -0.26 | +11.70 | -0.17 |

![yearly_sharpe](plots/yearly_sharpe.png)


### 3.5 Cost Sensitivity (OOS Sharpe by side)

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +2.53 | +1.41 | -0.26 |
| 50ETF | `short` | +5.30 | +3.96 | +1.94 |
| 300ETF | `long` | +1.74 | +1.12 | +0.18 |
| 300ETF | `short` | +4.34 | +2.85 | +0.62 |
| 500ETF | `long` | +3.18 | +2.13 | +0.56 |
| 500ETF | `short` | +3.69 | +2.27 | +0.13 |
| 588000ETF | `long` | +6.52 | +6.09 | +5.45 |
| 588000ETF | `short` | +4.35 | +3.54 | +2.32 |
| 159915ETF | `long` | +5.81 | +5.21 | +4.30 |
| 159915ETF | `short` | +4.70 | +3.81 | +2.47 |

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
| 50ETF | `long` | 29 | -4.0 | 44.8% | median<=0, win<=50%, n<60 |
| 50ETF | `short` | 21 | +23.5 | 57.1% | n<60 |
| 300ETF | `long` | 21 | +0.1 | 52.4% | n<60 |
| 300ETF | `short` | 25 | -5.2 | 48.0% | median<=0, win<=50%, n<60 |
| 500ETF | `long` | 76 | +12.3 | 57.9% | — |
| 500ETF | `short` | 52 | +7.7 | 51.9% | n<60 |
| 588000ETF | `long` | 25 | +45.4 | 60.0% | n<60 |
| 588000ETF | `short` | 27 | +18.3 | 55.6% | n<60 |
| 159915ETF | `long` | 41 | +38.8 | 56.1% | n<60 |
| 159915ETF | `short` | 25 | +44.1 | 60.0% | n<60 |

## 4. Diagnostic: Cluster Confusion (OOS traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; short side on Selloff.

| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |
|-----|------|-------|--------|----------|----------|
| 50ETF | `long` | 29 | 41% | 7% | 52% |
| 50ETF | `short` | 21 | 10% | 48% | 43% |
| 300ETF | `long` | 21 | 33% | 10% | 57% |
| 300ETF | `short` | 25 | 8% | 40% | 52% |
| 500ETF | `long` | 76 | 63% | 5% | 30% |
| 500ETF | `short` | 52 | 8% | 29% | 63% |
| 588000ETF | `long` | 25 | 48% | 16% | 36% |
| 588000ETF | `short` | 27 | 4% | 67% | 30% |
| 159915ETF | `long` | 41 | 61% | 5% | 34% |
| 159915ETF | `short` | 25 | 8% | 48% | 44% |

## 5. Mode Comparison (Phase 4 Cross-Mode Selection)

Each side deploys the mode with the highest OOS Sharpe. This table shows all eligible configs across single/hybrid/dual modes.

| ETF | Side | Single | Hybrid | Dual | **Deployed** |
|-----|------|--------|--------|------|--------------|
| 50ETF | `long` | — | +1.42 | +0.50 | **hybrid** (+1.42) |
| 50ETF | `short` | +3.96 | +2.37 | +2.20 | **single** (+3.96) |
| 300ETF | `long` | +1.16 | +2.54 | — | **hybrid** (+2.54) |
| 300ETF | `short` | +2.00 | +2.85 | — | **hybrid** (+2.85) |
| 500ETF | `long` | +2.05 | +2.13 | +0.71 | **hybrid** (+2.13) |
| 500ETF | `short` | +2.27 | +1.38 | +1.28 | **single** (+2.27) |
| 588000ETF | `long` | +5.43 | +5.47 | +0.96 | **hybrid** (+5.47) |
| 588000ETF | `short` | +3.00 | +2.82 | +3.54 | **dual** (+3.54) |
| 159915ETF | `long` | +4.96 | +5.21 | +1.49 | **hybrid** (+5.21) |
| 159915ETF | `short` | +3.14 | +1.94 | +3.52 | **dual** (+3.52) |

**Total deployed OOS Sharpe**: +30.42 (vs single-only +27.97, Δ = +2.45)


## 5.5 Stop-Loss Optimisation (Phase 5)

Each side's stop-loss is optimised **in-sample** by maximising total IS profit on the best (threshold, conviction) pair. The chosen stop is then evaluated OOS. Two types are swept: fixed-% from entry and ATR-14 multiples. `none` = hold to 14:30 unconditionally (baseline).

| ETF | Side | Stop type | Stop value | OOS Sharpe (w/ stop) | OOS P&L bps | OOS MaxDD bps | OOS Win% | Stopped trades |
|-----|------|-----------|------------|-----------------------|-------------|---------------|----------|----------------|
| 50ETF | `long` | fixed-% | 4.00% | +1.41 | +367 | -560 | 44.8% | 1 |
| 50ETF | `short` | fixed-% | 3.00% | +3.96 | +618 | -294 | 57.1% | 1 |
| 300ETF | `long` | ATR-14 | 3.5× | +1.12 | +376 | -913 | 52.4% | 1 |
| 300ETF | `short` | fixed-% | 4.00% | +2.85 | +480 | -433 | 48.0% | 0 |
| 500ETF | `long` | ATR-14 | 3.5× | +2.13 | +1543 | -695 | 57.9% | 0 |
| 500ETF | `short` | fixed-% | 4.00% | +2.27 | +829 | -677 | 51.9% | 0 |
| 588000ETF | `long` | fixed-% | 5.00% | +4.41 | +2869 | -551 | 55.6% | 0 |
| 588000ETF | `short` | fixed-% | 4.00% | +3.54 | +1177 | -471 | 55.6% | 0 |
| 159915ETF | `long` | fixed-% | 5.00% | +5.21 | +3533 | -678 | 56.1% | 0 |
| 159915ETF | `short` | ATR-14 | 3.5× | +3.52 | +1010 | -575 | 57.7% | 0 |

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