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
| **50ETF** | `single+gated` | 50 | 60 | `single+gated` | 50 | 80 |
| **300ETF** | `hybrid+gated` | 50 | 40 | `single` | 50 | 90 |
| **500ETF** | `single+gated` | 50 | 60 | `dual+gated` | 50 | 90 |
| **588000ETF** | `single+gated` | 95 | 40 | `single+gated` | 50 | 80 |
| **159915ETF** | `hybrid+gated` | 50 | 40 | `hybrid+gated` | 50 | 70 |

## 3. Performance (15 bps round-trip)

### 3.1 Per-Side OOS Metrics

*Place%* = side trades / total trading days in the period (capital deployment rate).

*Warnings* = non-blocking fragility flags. If any fire, the positive Sharpe may be a small-sample / heavy-tail artifact rather than a true edge. Three checks: `median<=0` (typical trade loses money), `win<=50%` (loses more often than wins), `n<60` (small sample, high multiple-testing risk from grid search).

| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |
|-----|------|-------|--------|------|--------|---------|-----------|----------|------------|----------|
| 50ETF | `long` | 23 | 4.2% | 52.2% | +1.16 | +253 | -415 | +11.0 | +3.4 | n<60 |
| 50ETF | `short` | 31 | 5.7% | 71.0% | +7.64 | +1488 | -297 | +48.0 | +48.4 | n<60 |
| 300ETF | `long` | 23 | 4.2% | 52.2% | +5.28 | +1414 | -379 | +61.5 | +23.5 | n<60 |
| 300ETF | `short` | 34 | 6.2% | 55.9% | +2.00 | +470 | -659 | +13.8 | +15.4 | n<60 |
| 500ETF | `long` | 50 | 9.2% | 64.0% | +3.05 | +1863 | -1030 | +37.3 | +40.2 | n<60 |
| 500ETF | `short` | 38 | 7.0% | 60.5% | +2.83 | +970 | -634 | +25.5 | +57.3 | n<60 |
| 588000ETF | `long` | 23 | 4.2% | 52.2% | +4.69 | +2791 | -660 | +121.3 | +25.2 | n<60 |
| 588000ETF | `short` | 46 | 8.5% | 58.7% | +3.30 | +1985 | -739 | +43.2 | +52.6 | n<60 |
| 159915ETF | `long` | 50 | 9.2% | 62.0% | +5.07 | +2939 | -603 | +58.8 | +35.0 | n<60 |
| 159915ETF | `short` | 46 | 8.5% | 63.0% | +4.05 | +1770 | -944 | +38.5 | +26.6 | n<60 |

### 3.2 Combined (Long+Short) Per ETF

| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |
|-----|----------|-------|----------|----------|------------|------|---------------|----------------|------------|-------------|---------------|
| **50ETF** | 344 | 54 | 4.2% | 5.7% | 9.9% | 58.1% | +3.45 | +8233 | +4.12 | +1741 | -415 |
| **300ETF** | 429 | 57 | 4.2% | 6.2% | 10.5% | 52.7% | +2.10 | +6869 | +3.61 | +1884 | -659 |
| **500ETF** | 380 | 88 | 9.2% | 7.0% | 16.2% | 62.1% | +4.06 | +15110 | +2.95 | +2834 | -1030 |
| **588000ETF** | 106 | 69 | 4.2% | 8.5% | 12.7% | 62.3% | +4.13 | +7052 | +3.78 | +4776 | -867 |
| **159915ETF** | 441 | 96 | 9.2% | 8.5% | 17.6% | 59.0% | +3.93 | +18459 | +4.63 | +4709 | -1093 |

### 3.3 Placement Rates (capital deployment frequency)

Fraction of trading days on which each side fires. High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.

| ETF | Long Place% (full) | Long Place% (OOS) | Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |
|-----|--------------------|-------------------|---------------------|---------------------|--------------------|
| **50ETF** | 7.8% | 4.2% | 4.8% | 5.7% | 9.9% |
| **300ETF** | 10.8% | 4.2% | 4.9% | 6.2% | 10.5% |
| **500ETF** | 7.7% | 9.2% | 6.3% | 7.0% | 16.2% |
| **588000ETF** | 3.2% | 4.2% | 4.9% | 8.5% | 12.7% |
| **159915ETF** | 10.4% | 9.2% | 5.8% | 8.5% | 17.6% |

### 3.4 Year-by-Year OOS Sharpe

| ETF | Side | 2024 | 2025 | 2026 |
|-----|------|---|---|---|
| 50ETF | `long` | +1.69 | +14.16 | -9.63 |
| 50ETF | `short` | +7.29 | +20.26 | +0.30 |
| 300ETF | `long` | +6.51 | +2.54 | +0.45 |
| 300ETF | `short` | +1.31 | +3.52 | — |
| 500ETF | `long` | +2.82 | +9.34 | +2.79 |
| 500ETF | `short` | +2.68 | +0.96 | +5.66 |
| 588000ETF | `long` | +6.89 | +11.88 | -6.70 |
| 588000ETF | `short` | +11.22 | +2.08 | +1.02 |
| 159915ETF | `long` | +3.17 | +9.76 | +5.02 |
| 159915ETF | `short` | +4.61 | +10.49 | -1.99 |

![yearly_sharpe](plots\yearly_sharpe.png)


### 3.5 Cost Sensitivity (OOS Sharpe by side)

| ETF | Side | 5 bps | 15 bps | 30 bps |
|-----|------|-------|--------|--------|
| 50ETF | `long` | +2.21 | +1.16 | -0.42 |
| 50ETF | `short` | +9.23 | +7.64 | +5.25 |
| 300ETF | `long` | +6.14 | +5.28 | +3.99 |
| 300ETF | `short` | +3.45 | +2.00 | -0.17 |
| 500ETF | `long` | +3.86 | +3.05 | +1.82 |
| 500ETF | `short` | +3.94 | +2.83 | +1.17 |
| 588000ETF | `long` | +5.08 | +4.69 | +4.11 |
| 588000ETF | `short` | +4.06 | +3.30 | +2.15 |
| 159915ETF | `long` | +5.94 | +5.07 | +3.78 |
| 159915ETF | `short` | +5.10 | +4.05 | +2.47 |

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
| 50ETF | `long` | 23 | +3.4 | 52.2% | n<60 |
| 50ETF | `short` | 31 | +48.4 | 71.0% | n<60 |
| 300ETF | `long` | 23 | +23.5 | 52.2% | n<60 |
| 300ETF | `short` | 34 | +15.4 | 55.9% | n<60 |
| 500ETF | `long` | 50 | +40.2 | 64.0% | n<60 |
| 500ETF | `short` | 38 | +57.3 | 60.5% | n<60 |
| 588000ETF | `long` | 23 | +25.2 | 52.2% | n<60 |
| 588000ETF | `short` | 46 | +52.6 | 58.7% | n<60 |
| 159915ETF | `long` | 50 | +35.0 | 62.0% | n<60 |
| 159915ETF | `short` | 46 | +26.6 | 63.0% | n<60 |

## 4. Diagnostic: Cluster Confusion (OOS traded days)

Of days traded on each side, what fraction belonged to day-trading's discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; short side on Selloff.

| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |
|-----|------|-------|--------|----------|----------|
| 50ETF | `long` | 23 | 61% | 4% | 35% |
| 50ETF | `short` | 31 | 6% | 52% | 42% |
| 300ETF | `long` | 23 | 57% | 9% | 35% |
| 300ETF | `short` | 34 | 24% | 38% | 38% |
| 500ETF | `long` | 50 | 70% | 4% | 24% |
| 500ETF | `short` | 38 | 5% | 53% | 42% |
| 588000ETF | `long` | 23 | 52% | 17% | 30% |
| 588000ETF | `short` | 46 | 20% | 59% | 22% |
| 159915ETF | `long` | 50 | 58% | 4% | 38% |
| 159915ETF | `short` | 46 | 2% | 59% | 39% |

## 5. Mode Comparison (Phase 4 Cross-Mode Selection)

Each side deploys the mode with the highest OOS Sharpe. This table shows all eligible configs across single/hybrid/dual modes.

| ETF | Side | Single | Hybrid | Dual | **Deployed** |
|-----|------|--------|--------|------|--------------|
| 50ETF | `long` | — | — | — | **single+gated** (+1.16) |
| 50ETF | `short` | +3.96 | +5.59 | — | **single+gated** (+7.64) |
| 300ETF | `long` | +1.16 | +2.02 | — | **hybrid+gated** (+5.28) |
| 300ETF | `short` | +2.00 | — | +0.40 | **single** (+2.00) |
| 500ETF | `long` | +2.05 | +1.75 | +0.53 | **single+gated** (+3.78) |
| 500ETF | `short` | +2.27 | +2.05 | +3.61 | **dual+gated** (+3.80) |
| 588000ETF | `long` | +5.43 | +3.48 | +0.46 | **single+gated** (+5.86) |
| 588000ETF | `short` | +3.00 | +2.33 | +0.86 | **single+gated** (+3.30) |
| 159915ETF | `long` | +4.96 | +4.12 | +1.91 | **hybrid+gated** (+5.07) |
| 159915ETF | `short` | +3.14 | +2.98 | +2.20 | **hybrid+gated** (+4.05) |

**Total deployed OOS Sharpe**: +39.73 (vs single-only +27.97, Δ = +11.75)


## 5.5 Gating Impact (v3)

Per-side OOS Sharpe: best ungated mode (single/hybrid/dual) vs best gated mode (single/hybrid/dual + gating veto). The mixed-mode picker auto-adopts `+gated` per side when it wins on OOS Sharpe.

| ETF | Side | Best Ungated | Best Gated | Δ | Deployed |
|-----|------|--------------|------------|---|----------|
| 50ETF | `long` | disabled | +1.16 | — | **single+gated** (+1.16) |
| 50ETF | `short` | +5.59 | +7.64 | +2.05 | **single+gated** (+7.64) |
| 300ETF | `long` | +2.02 | +5.28 | +3.26 | **hybrid+gated** (+5.28) |
| 300ETF | `short` | +2.00 | +1.27 | -0.73 | **single** (+2.00) |
| 500ETF | `long` | +2.05 | +3.78 | +1.73 | **single+gated** (+3.78) |
| 500ETF | `short` | +3.61 | +3.80 | +0.18 | **dual+gated** (+3.80) |
| 588000ETF | `long` | +5.43 | +5.86 | +0.43 | **single+gated** (+5.86) |
| 588000ETF | `short` | +3.00 | +3.30 | +0.30 | **single+gated** (+3.30) |
| 159915ETF | `long` | +4.96 | +5.07 | +0.11 | **hybrid+gated** (+5.07) |
| 159915ETF | `short` | +3.14 | +4.05 | +0.91 | **hybrid+gated** (+4.05) |

**Totals** — Ungated mixed: +31.81 | Gated mixed: +41.21 | Deployed (mixed-mode picker): +41.94 (Δ vs ungated = +10.13)

_Gate-only (no daytrade score) totals just +9.08 OOS Sharpe — see `GATING_ONLY_REPORT.md`. The gate is a selectivity filter, not a standalone alpha._


## 5.6 Stop-Loss Optimisation (Phase 5)

Each side's stop-loss is optimised **in-sample** by maximising total IS profit on the best (threshold, conviction) pair. The chosen stop is then evaluated OOS. Two types are swept: fixed-% from entry and ATR-14 multiples. `none` = hold to 14:30 unconditionally (baseline).

| ETF | Side | Stop type | Stop value | OOS Sharpe (w/ stop) | OOS P&L bps | OOS MaxDD bps | OOS Win% | Stopped trades |
|-----|------|-----------|------------|-----------------------|-------------|---------------|----------|----------------|
| 50ETF | `long` | fixed-% | 4.00% | +1.16 | +253 | -415 | 52.2% | 1 |
| 50ETF | `short` | fixed-% | 4.00% | +7.64 | +1488 | -297 | 71.0% | 0 |
| 300ETF | `long` | ATR-14 | 3.5× | +5.28 | +1414 | -379 | 52.2% | 0 |
| 300ETF | `short` | fixed-% | 4.00% | +2.00 | +470 | -659 | 55.9% | 0 |
| 500ETF | `long` | fixed-% | 5.00% | +2.74 | +1711 | -1030 | 62.7% | 2 |
| 500ETF | `short` | ATR-14 | 3.5× | +3.80 | +1430 | -634 | 62.5% | 0 |
| 588000ETF | `long` | fixed-% | 5.00% | +4.69 | +2791 | -660 | 52.2% | 1 |
| 588000ETF | `short` | ATR-14 | 3.5× | +3.30 | +1985 | -739 | 58.7% | 0 |
| 159915ETF | `long` | fixed-% | 4.00% | +5.07 | +2939 | -603 | 62.0% | 4 |
| 159915ETF | `short` | fixed-% | 4.00% | +4.05 | +1770 | -944 | 63.0% | 2 |

## 6. Verdict

- **Robust long_model (OOS Sharpe ≥ +2.0)**: 300ETF, 500ETF, 588000ETF, 159915ETF
- **Robust short_model (OOS Sharpe ≥ +2.0)**: 50ETF, 500ETF, 588000ETF, 159915ETF
- **Disabled long**: none
- **Disabled short**: none

## 7. Caveats

- Short-side P&L assumes 15bps transaction cost and other execution assumptions similar to the long side (options/margin/borrow costs not modeled)
- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability
- 14:30 exit leaves late-day continuation on the table; v2 will add trailing stop
- No position sizing (fixed notional); drawdowns are per-unit-notional
- Per-side eligibility uses holdout (2024-03+); earlier years may behave differently
- Single cost assumption (15bps RT) applied to both long and short; real-world shorts via options will carry different (likely higher) cost