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
| 500ETF | Spot ETF | single | L:0.90/S:1.30 | 32 | 290 | 0.836 | 0.806 | +0.3192 | +0.2780 | 0.1232 | 0.1547 | 58.3% | 57.6% | **PASS** |
