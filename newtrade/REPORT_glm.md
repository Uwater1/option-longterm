# NewTrade Scheme 5 — Linear GLM OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme**: `Scheme 5 — Linear GLM (Expanding Ridge)`
- **Target Formulation Mode**: `bj_sign`
- **Prior Mode**: `ic`
- **Conviction Threshold**: `auto` (z_buffer = 0.1)
- **Position Mode**: `binary`
- **Transaction Friction**: `8.0 bps`
- **Instrument Mode**: `Spot ETF`

---

## Executive Summary & Acceptance Gate Results

| ETF | Asset | Side | Z_th | Features | Trades | GLM Sharpe | Rank Sharpe | GLM PnL | Rank PnL | GLM MaxDD | Rank MaxDD | GLM WR | Rank WR | Gate Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | L:1.60/S:1.20 | 10 | 13 | 0.680 | 0.707 | +0.0797 | +0.1447 | 0.0243 | 0.0474 | 69.2% | 55.9% | **FAIL** |
| 500ETF | Spot ETF | single | L:0.90/S:1.30 | 32 | 290 | 0.836 | 0.768 | +0.3192 | +0.2799 | 0.1232 | 0.1182 | 58.3% | 55.9% | **PASS** |
| 50ETF | Spot ETF | single | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIP |
| 588000ETF | Spot ETF | single | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIP |
| 159915ETF | Spot ETF | single | L:0.80/S:1.30 | 11 | 346 | 1.502 | 1.460 | +0.7879 | +0.6359 | 0.1058 | 0.0910 | 58.1% | 61.1% | **PASS** |
