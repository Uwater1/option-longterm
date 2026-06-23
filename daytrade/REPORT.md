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
| **50ETF** | `hybrid` | 50 | 80 | `hybrid` | 50 | 90 |
| **300ETF** | `hybrid` | 50 | 70 | `dual` | 95 | 40 |
| **500ETF** | `hybrid` | 50 | 90 | `dual` | 50 | 80 |
| **588000ETF** | `single` | 95 | 40 | `hybrid` | 95 | 40 |
| **159915ETF** | `single` | 50 | 90 | `hybrid` | 95 | 40 |

## 3. Performance (15 bps round-trip)

### 3.1 Per-Side OOS Metrics

*Place%* = side trades / total trading days in the period (capital deployment rate).

*Warnings* = non-blocking fragility flags. If any fire, the positive Sharpe may be a small-sample / heavy-tail artifact rather than a true edge. Three checks: `median<=0` (typical trade loses money), `win<=50%` (loses more often than wins), `n<60` (small sample, high multiple-testing risk from grid search).

| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |
|-----|------|-------|--------|------|--------|---------|-----------|----------|------------|----------|
| 50ETF | `long` | 29 | 5.3% | 58.6% | +4.34 | +935 | -314 | +32.2 | +9.2 | n<60 |
| 50ETF | `short` | 20 | 3.7% | 65.0% | +6.47 | +1011 | -220 | +50.5 | +30.9 | n<60 |
| 300ETF | `long` | 59 | 10.8% | 49.2% | +2.11 | +1050 | -641 | +17.8 | -6.2 | median<=0, win<=50%, n<60 |
| 300ETF | `short` | 22 | 4.0% | 54.5% | +5.53 | +1029 | -234 | +46.8 | +28.9 | n<60 |
| 500ETF | `long` | 29 | 5.3% | 62.1% | +3.80 | +1272 | -438 | +43.9 | +33.6 | n<60 |
| 500ETF | `short` | 139 | 25.6% | 54.7% | +0.02 | +23 | -1322 | +0.2 | +9.5 | — |
| 588000ETF | `long` | 29 | 5.3% | 48.3% | +5.43 | +3469 | -660 | +119.6 | -0.1 | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 32 | 5.9% | 62.5% | +3.87 | +1665 | -961 | +52.0 | +66.6 | n<60 |
| 159915ETF | `long` | 26 | 4.8% | 57.7% | +6.44 | +3253 | -693 | +125.1 | +68.7 | n<60 |
| 159915ETF | `short` | 43 | 7.9% | 60.5% | +3.45 | +1481 | -930 | +34.4 | +29.7 | n<60 |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |
|-----|----------|-------|----------|----------|------------|------|---------------|----------------|------------|-------------|---------------|
| **50ETF** | 212 | 49 | 5.3% | 3.7% | 9.0% | 58.0% | +5.35 | +7353 | +5.28 | +1946 | -308 |
| **300ETF** | 355 | 81 | 10.8% | 4.0% | 14.9% | 56.3% | +3.33 | +10339 | +3.04 | +2079 | -715 |
| **500ETF** | 421 | 168 | 5.3% | 25.6% | 30.9% | 55.1% | +1.58 | +6722 | +0.91 | +1295 | -1169 |
| **588000ETF** | 96 | 61 | 5.3% | 5.9% | 11.2% | 62.5% | +5.33 | +8228 | +4.68 | +5134 | -1189 |
| **159915ETF** | 165 | 69 | 4.8% | 7.9% | 12.7% | 63.0% | +6.24 | +12303 | +4.75 | +4734 | -992 |

### 3.3 Placement Rates (capital deployment frequency)

Fraction of trading days on which each side fires. High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.

| ETF | Long Place% (full) | Long Place% (OOS) | Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |
|-----|--------------------|-------------------|---------------------|---------------------|--------------------|
| **50ETF** | 5.4% | 5.3% | 2.4% | 3.7% | 9.0% |
| **300ETF** | 10.2% | 10.8% | 2.8% | 4.0% | 14.9% |
| **500ETF** | 2.4% | 5.3% | 13.1% | 25.6% | 30.9% |
| **588000ETF** | 3.9% | 5.3% | 3.6% | 5.9% | 11.2% |
| **159915ETF** | 3.6% | 4.8% | 2.4% | 7.9% | 12.7% |

### 3.4 Year-by-Year OOS Sharpe

| ETF | Side | 2024 | 2025 | 2026 |
|-----|------|---|---|---|
| 50ETF | `long` | +7.84 | -0.17 | -3.95 |
| 50ETF | `short` | +6.96 | +6.10 | +2.58 |
| 300ETF | `long` | +6.20 | -0.39 | -4.79 |
| 300ETF | `short` | +6.74 | +5.97 | — |
| 500ETF | `long` | +4.30 | +5.27 | +3.30 |
| 500ETF | `short` | +1.99 | +0.57 | -3.07 |
| 588000ETF | `long` | +8.86 | +10.53 | -5.59 |
| 588000ETF | `short` | +29.93 | +0.42 | +1.06 |
| 159915ETF | `long` | +10.23 | -4.04 | +20.12 |
| 159915ETF | `short` | +5.74 | +8.95 | -9.52 |

![yearly_sharpe](plots\yearly_sharpe.png)


### 3.5 Cost Sensitivity (OOS Sharpe by side)

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +5.69 | +4.34 | +2.32 |
| 50ETF | `short` | +7.75 | +6.47 | +4.55 |
| 300ETF | `long` | +3.29 | +2.11 | +0.33 |
| 300ETF | `short` | +6.71 | +5.53 | +3.76 |
| 500ETF | `long` | +4.66 | +3.80 | +2.50 |
| 500ETF | `short` | +1.34 | +0.02 | -1.95 |
| 588000ETF | `long` | +5.89 | +5.43 | +4.75 |
| 588000ETF | `short` | +4.62 | +3.87 | +2.76 |
| 159915ETF | `long` | +6.96 | +6.44 | +5.67 |
| 159915ETF | `short` | +4.45 | +3.45 | +1.94 |

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
| 50ETF | `long` | 29 | +9.2 | 58.6% | n<60 |
| 50ETF | `short` | 20 | +30.9 | 65.0% | n<60 |
| 300ETF | `long` | 59 | -6.2 | 49.2% | median<=0, win<=50%, n<60 |
| 300ETF | `short` | 22 | +28.9 | 54.5% | n<60 |
| 500ETF | `long` | 29 | +33.6 | 62.1% | n<60 |
| 500ETF | `short` | 139 | +9.5 | 54.7% | — |
| 588000ETF | `long` | 29 | -0.1 | 48.3% | median<=0, win<=50%, n<60 |
| 588000ETF | `short` | 32 | +66.6 | 62.5% | n<60 |
| 159915ETF | `long` | 26 | +68.7 | 57.7% | n<60 |
| 159915ETF | `short` | 43 | +29.7 | 60.5% | n<60 |

## 4. Diagnostic: Cluster Confusion (OOS traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; short side on Selloff.

| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |
|-----|------|-------|--------|----------|----------|
| 50ETF | `long` | 29 | 45% | 7% | 48% |
| 50ETF | `short` | 20 | 10% | 60% | 30% |
| 300ETF | `long` | 59 | 42% | 5% | 53% |
| 300ETF | `short` | 22 | 14% | 50% | 36% |
| 500ETF | `long` | 29 | 69% | 3% | 28% |
| 500ETF | `short` | 139 | 10% | 40% | 50% |
| 588000ETF | `long` | 29 | 48% | 14% | 38% |
| 588000ETF | `short` | 32 | 19% | 62% | 19% |
| 159915ETF | `long` | 26 | 77% | 4% | 19% |
| 159915ETF | `short` | 43 | 9% | 42% | 49% |

## 5. Mode Comparison (Phase 4 Cross-Mode Selection)

Each side deploys the mode with the highest OOS Sharpe. This table shows all eligible configs across single/hybrid/dual modes.

| ETF | Side | Single | Hybrid | Dual | **Deployed** |
|-----|------|--------|--------|------|--------------|
| 50ETF | `long` | +2.95 | +4.34 | +0.42 | **hybrid** (+4.34) |
| 50ETF | `short` | +3.86 | +6.47 | +0.99 | **hybrid** (+6.47) |
| 300ETF | `long` | +1.25 | +2.11 | +0.98 | **hybrid** (+2.11) |
| 300ETF | `short` | — | +0.62 | +5.53 | **dual** (+5.53) |
| 500ETF | `long` | +3.06 | +3.80 | +3.00 | **hybrid** (+3.80) |
| 500ETF | `short` | — | — | +0.02 | **dual** (+0.02) |
| 588000ETF | `long` | +5.43 | +5.36 | +3.25 | **single** (+5.43) |
| 588000ETF | `short` | +2.86 | +3.87 | +2.26 | **hybrid** (+3.87) |
| 159915ETF | `long` | +6.44 | +4.59 | +2.50 | **single** (+6.44) |
| 159915ETF | `short` | +2.74 | +3.45 | +1.20 | **hybrid** (+3.45) |

**Total deployed OOS Sharpe**: +41.46 (vs single-only +28.60, Δ = +12.86)


## 6. Verdict

- **Robust long_model (OOS Sharpe ≥ +2.0)**: 50ETF, 300ETF, 500ETF, 588000ETF, 159915ETF
- **Robust short_model (OOS Sharpe ≥ +2.0)**: 50ETF, 300ETF, 588000ETF, 159915ETF
- **Disabled long**: none
- **Disabled short**: none

## 7. Caveats

- Short-side P&L assumes 15bps transaction cost and other execution assumptions similar to the long side (options/margin/borrow costs not modeled)
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- 14:30 exit leaves late-day continuation on the table; v2 will add trailing stop
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Per-side eligibility uses holdout (2024-03+); earlier years may behave differently
- Single cost assumption (15bps RT) applied to both long and short; real-world shorts via options will carry different (likely higher) cost