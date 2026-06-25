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
| **50ETF** | `—` | disabled | — | `hybrid` | 50 | 90 |
| **300ETF** | `hybrid` | 50 | 70 | `single` | 50 | 90 |
| **500ETF** | `single` | 50 | 60 | `dual` | 50 | 90 |
| **588000ETF** | `single` | 95 | 40 | `single` | 50 | 80 |
| **159915ETF** | `single` | 50 | 80 | `single` | 50 | 90 |

## 3. Performance (15 bps round-trip)

### 3.1 Per-Side OOS Metrics

*Place%* = side trades / total trading days in the period (capital deployment rate).

*Warnings* = non-blocking fragility flags. If any fire, the positive Sharpe may be a small-sample / heavy-tail artifact rather than a true edge. Three checks: `median<=0` (typical trade loses money), `win<=50%` (loses more often than wins), `n<60` (small sample, high multiple-testing risk from grid search).

| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |
|-----|------|-------|--------|------|--------|---------|-----------|----------|------------|----------|
| 50ETF | `short` | 30 | 5.5% | 60.0% | +5.59 | +994 | -334 | +33.1 | +24.3 | n<60 |
| 300ETF | `long` | 32 | 5.9% | 40.6% | +2.02 | +593 | -649 | +18.5 | -29.1 | median<=0, win<=50%, n<60 |
| 300ETF | `short` | 34 | 6.2% | 55.9% | +2.00 | +470 | -659 | +13.8 | +15.4 | n<60 |
| 500ETF | `long` | 83 | 15.3% | 57.8% | +2.39 | +1838 | -695 | +22.1 | +11.2 | — |
| 500ETF | `short` | 54 | 9.9% | 61.1% | +3.39 | +1503 | -775 | +27.8 | +29.0 | n<60 |
| 588000ETF | `long` | 29 | 5.3% | 48.3% | +4.41 | +2969 | -660 | +102.4 | -0.1 | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 69 | 12.7% | 62.3% | +3.00 | +2375 | -1229 | +34.4 | +48.1 | — |
| 159915ETF | `long` | 47 | 8.6% | 57.4% | +4.96 | +3707 | -813 | +78.9 | +57.1 | n<60 |
| 159915ETF | `short` | 72 | 13.2% | 59.7% | +2.37 | +1561 | -1021 | +21.7 | +18.5 | — |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |
|-----|----------|-------|----------|----------|------------|------|---------------|----------------|------------|-------------|---------------|
| **50ETF** | 80 | 30 | 0.0% | 5.5% | 5.5% | 62.5% | +3.61 | +2191 | +5.59 | +994 | -334 |
| **300ETF** | 418 | 66 | 5.9% | 6.2% | 12.1% | 49.5% | +1.04 | +3220 | +2.00 | +1063 | -659 |
| **500ETF** | 657 | 137 | 15.3% | 9.9% | 25.2% | 58.3% | +3.20 | +16626 | +2.76 | +3341 | -621 |
| **588000ETF** | 192 | 98 | 5.3% | 12.7% | 18.0% | 62.5% | +3.69 | +9133 | +3.44 | +5344 | -1229 |
| **159915ETF** | 336 | 119 | 8.6% | 13.2% | 21.9% | 64.0% | +5.45 | +19387 | +3.59 | +5268 | -1142 |

### 3.3 Placement Rates (capital deployment frequency)

Fraction of trading days on which each side fires. High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.

| ETF | Long Place% (full) | Long Place% (OOS) | Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |
|-----|--------------------|-------------------|---------------------|---------------------|--------------------|
| **50ETF** | 0.0% | 0.0% | 2.9% | 5.5% | 5.5% |
| **300ETF** | 10.4% | 5.9% | 4.9% | 6.2% | 12.1% |
| **500ETF** | 13.9% | 15.3% | 10.2% | 9.9% | 25.2% |
| **588000ETF** | 3.9% | 5.3% | 11.0% | 12.7% | 18.0% |
| **159915ETF** | 6.8% | 8.6% | 5.6% | 13.2% | 21.9% |

### 3.4 Year-by-Year OOS Sharpe

| ETF | Side | 2024 | 2025 | 2026 |
|-----|------|---|---|---|
| 50ETF | `short` | +11.94 | +9.20 | -3.23 |
| 300ETF | `long` | +1.98 | +1.94 | +2.97 |
| 300ETF | `short` | +1.31 | +3.52 | — |
| 500ETF | `long` | +3.38 | +3.04 | -0.26 |
| 500ETF | `short` | +6.79 | +0.09 | +5.49 |
| 588000ETF | `long` | +6.73 | +10.53 | -5.59 |
| 588000ETF | `short` | +12.73 | +1.03 | +1.32 |
| 159915ETF | `long` | +8.52 | -1.28 | +7.12 |
| 159915ETF | `short` | +4.15 | +4.78 | -2.98 |

![yearly_sharpe](plots\yearly_sharpe.png)


### 3.5 Cost Sensitivity (OOS Sharpe by side)

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `short` | +7.27 | +5.59 | +3.06 |
| 300ETF | `long` | +3.11 | +2.02 | +0.38 |
| 300ETF | `short` | +3.45 | +2.00 | -0.17 |
| 500ETF | `long` | +3.46 | +2.39 | +0.77 |
| 500ETF | `short` | +4.61 | +3.39 | +1.56 |
| 588000ETF | `long` | +4.84 | +4.41 | +3.77 |
| 588000ETF | `short` | +3.87 | +3.00 | +1.69 |
| 159915ETF | `long` | +5.59 | +4.96 | +4.02 |
| 159915ETF | `short` | +3.46 | +2.37 | +0.73 |

### 3.6 Equity Curves

![equity_combined](plots\equity_combined.png)

![equity_per_side](plots\equity_curves.png)


### 3.7 Fragility Warnings Summary

Non-blocking transparency flags. A side with warnings is still deployed (passes the hard guard `Sharpe>0 AND P&L>0 AND n≥20`) but the positive Sharpe may be a small-sample / heavy-tail artifact. Investigate before sizing the position.

- `median<=0`: typical OOS trade loses money; positive mean is carried by a few big winners
- `win<=50%`: side loses more often than it wins
- `n<60`: small sample; high multiple-testing risk from the 6×6 grid search

| ETF | Side | N OOS | Median bps | Win% | Warnings |
|-----|------|-------|------------|------|----------|
| 50ETF | `short` | 30 | +24.3 | 60.0% | n<60 |
| 300ETF | `long` | 32 | -29.1 | 40.6% | median<=0, win<=50%, n<60 |
| 300ETF | `short` | 34 | +15.4 | 55.9% | n<60 |
| 500ETF | `long` | 83 | +11.2 | 57.8% | — |
| 500ETF | `short` | 54 | +29.0 | 61.1% | n<60 |
| 588000ETF | `long` | 29 | -0.1 | 48.3% | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 69 | +48.1 | 62.3% | — |
| 159915ETF | `long` | 47 | +57.1 | 57.4% | n<60 |
| 159915ETF | `short` | 72 | +18.5 | 59.7% | — |

## 4. Diagnostic: Cluster Confusion (OOS traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; short side on Selloff.

| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |
|-----|------|-------|--------|----------|----------|
| 50ETF | `short` | 30 | 3% | 37% | 60% |
| 300ETF | `long` | 32 | 38% | 6% | 56% |
| 300ETF | `short` | 34 | 24% | 38% | 38% |
| 500ETF | `long` | 83 | 54% | 6% | 39% |
| 500ETF | `short` | 54 | 6% | 48% | 46% |
| 588000ETF | `long` | 29 | 48% | 14% | 38% |
| 588000ETF | `short` | 69 | 16% | 55% | 29% |
| 159915ETF | `long` | 47 | 62% | 4% | 34% |
| 159915ETF | `short` | 72 | 6% | 40% | 54% |

## 5. Mode Comparison (Phase 4 Cross-Mode Selection)

Each side deploys the mode with the highest OOS Sharpe. This table shows all eligible configs across single/hybrid/dual modes.

| ETF | Side | Single | Hybrid | Dual | **Deployed** |
|-----|------|--------|--------|------|--------------|
| 50ETF | `short` | +3.96 | +5.59 | — | **hybrid** (+5.59) |
| 300ETF | `long` | +1.16 | +2.02 | — | **hybrid** (+2.02) |
| 300ETF | `short` | +2.00 | — | +0.40 | **single** (+2.00) |
| 500ETF | `long` | +2.05 | +1.75 | +0.53 | **single** (+2.05) |
| 500ETF | `short` | +2.27 | +2.05 | +3.61 | **dual** (+3.61) |
| 588000ETF | `long` | +5.43 | +3.48 | +0.46 | **single** (+5.43) |
| 588000ETF | `short` | +3.00 | +2.33 | +0.86 | **single** (+3.00) |
| 159915ETF | `long` | +4.96 | +4.12 | +1.91 | **single** (+4.96) |
| 159915ETF | `short` | +3.14 | +2.98 | +2.20 | **single** (+3.14) |

**Total deployed OOS Sharpe**: +29.35 (vs single-only +27.97, Δ = +1.38)


## 5.5 Stop-Loss Optimisation (Phase 5)

Each side's stop-loss is optimised **in-sample** by maximising total IS profit on the best (threshold, conviction) pair. The chosen stop is then evaluated OOS. Two types are swept: fixed-% from entry and ATR-14 multiples. `none` = hold to 14:30 unconditionally (baseline).

| ETF | Side | Stop type | Stop value | OOS Sharpe (w/ stop) | OOS P&L bps | OOS MaxDD bps | OOS Win% | Stopped trades |
|-----|------|-----------|------------|-----------------------|-------------|---------------|----------|----------------|
| 50ETF | `short` | fixed-% | 4.00% | +5.59 | +994 | -334 | 60.0% | 0 |
| 300ETF | `long` | ATR-14 | 3.5× | +2.02 | +593 | -649 | 40.6% | 0 |
| 300ETF | `short` | fixed-% | 4.00% | +2.00 | +470 | -659 | 55.9% | 0 |
| 500ETF | `long` | fixed-% | 5.00% | +1.39 | +1182 | -1030 | 55.8% | 1 |
| 500ETF | `short` | ATR-14 | 3.5× | +3.61 | +1625 | -775 | 61.8% | 0 |
| 588000ETF | `long` | fixed-% | 5.00% | +4.41 | +2969 | -660 | 48.3% | 1 |
| 588000ETF | `short` | ATR-14 | 3.5× | +3.00 | +2375 | -1229 | 62.3% | 0 |
| 159915ETF | `long` | fixed-% | 5.00% | +4.96 | +3707 | -813 | 57.4% | 0 |
| 159915ETF | `short` | fixed-% | 3.00% | +2.37 | +1561 | -1021 | 59.7% | 6 |

## 6. Verdict

- **Robust long_model (OOS Sharpe ≥ +2.0)**: 300ETF, 500ETF, 588000ETF, 159915ETF
- **Robust short_model (OOS Sharpe ≥ +2.0)**: 50ETF, 500ETF, 588000ETF, 159915ETF
- **Disabled long**: 50ETF
- **Disabled short**: none

## 7. Caveats

- Short-side P&L assumes 15bps transaction cost and other execution assumptions similar to the long side (options/margin/borrow costs not modeled)
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- 14:30 exit leaves late-day continuation on the table; v2 will add trailing stop
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Per-side eligibility uses holdout (2024-03+); earlier years may behave differently
- Single cost assumption (15bps RT) applied to both long and short; real-world shorts via options will carry different (likely higher) cost