# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ENSEMBLE`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Transaction Friction**: `8.0 bps`
- **Rank Mapping Options**: `mapping=linear, min_ratio=0.2, max_ratio=1.8, power=2.0`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/rank_bounded_equity.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 64 (23L/41S) | 0.773 | 1.308 | +0.1402 | 0.0621 | 57.8% (L:69.6%, S:51.2%) | 32.2x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.60/S:1.20) | 32 | 191 (187L/4S) | 0.670 | 1.478 | +0.2022 | 0.1271 | 59.2% (L:58.8%, S:75.0%) | 79.6x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 11 | 245 (127L/118S) | 1.411 | 2.197 | +0.6041 | 0.0885 | 60.8% (L:58.3%, S:63.6%) | 110.3x |

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.773 | 0.572 | NOT_SIGNIFICANT | 0.781 | 0.221 | 100% |
| 500ETF | ensemble | 0.670 | 0.434 | NOT_SIGNIFICANT | 1.206 | 0.487 | 100% |
| 159915ETF | ensemble | 1.411 | 0.930 | MARGINAL | 1.089 | 0.314 | 100% |

