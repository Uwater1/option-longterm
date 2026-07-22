# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme**: `EW`
- **Conviction Threshold ($Z_{th}$)**: `0.5`
- **Position Mode**: `binary`
- **Transaction Friction**: `8.0 bps`

| ETF | Side | OOS Period | Trade Window | Status | Features | Intraday Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 10:00-14:35 | SUCCESS | 10 | 133 | 0.281 | 1.146 | +0.0604 | 0.0766 | 47.4% | 60.3x |
| 500ETF | single | 2022-01 ~ 2025-12 | 10:00-14:35 | SUCCESS | 48 | 244 | 0.655 | 1.580 | +0.2054 | 0.1108 | 55.7% | 94.1x |
| 50ETF | single | 2022-01 ~ 2026-01 | 10:00-14:35 | SKIPPED_FEAT_FLOOR | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | 10:00-14:35 | SKIPPED_FEAT_FLOOR | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 10:00-14:35 | SUCCESS | 11 | 265 | 0.624 | 1.236 | +0.3105 | 0.1888 | 49.8% | 98.8x |
