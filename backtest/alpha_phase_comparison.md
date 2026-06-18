# Alpha Model — Cross-Phase Comparison (OOS Put P&L)

Cadence = cycle (monthly cycle start, fair vs baselines). OOS years >= 2021.

`DEPLOY` = phase beats static filter on net P&L AND Sharpe>0 AND per-trigger>0.

Statistical column: Phase 1 walk-forward OOS (lift for crash / mean_ret for fall).

| ETF | Regime | Stat OOS | P1 netPnL (N) | P2 netPnL (N) | P3 netPnL (N) | Static netPnL (N) | **WINNER** |
|---|---|---|---|---|---|---|---|
| 50 | ST Fall | -0.56% [CI -0.01] | +1208 (9) | -3168 (39) | +836 (4) | +1331 (4) | static filter (no alpha edge) |
| 50 | MT Fall | -0.98% [CI -0.02] | -2002 (15) | -933 (27) | -600 (2) | +1331 (4) | static filter (no alpha edge) |
| 50 | ST Crash | 2.12x [CI 0.60] | -2154 (16) | -665 (9) | +424 (7) | +1613 (4) | static filter (no alpha edge) |
| 50 | MT Crash | 2.10x [CI 0.71] | +760 (14) | +1975 (15) ✅ | +2144 (6) ✅ | +1613 (4) | Phase 3 ✅ |
| 300 | ST Fall | -0.35% [CI -0.01] | +2689 (7) ✅ | -5488 (27) | +2017 (3) ✅ | +1385 (12) | Phase 1 ✅ |
| 300 | MT Fall | -0.96% [CI -0.01] | -1535 (12) | -1796 (34) | +2216 (8) ✅ | +1385 (12) | Phase 3 ✅ |
| 300 | ST Crash | 2.03x [CI 0.27] | -473 (14) | -3373 (12) | +0 (0) | +459 (12) | static filter (no alpha edge) |
| 300 | MT Crash | 1.45x [CI 0.48] | -943 (11) | -1036 (16) | -574 (3) | +459 (12) | static filter (no alpha edge) |
| 500 | ST Fall | -0.64% [CI -0.01] | -8235 (9) | -9001 (17) | -6583 (10) | -493 (1) | static filter (no alpha edge) |
| 500 | MT Fall | -0.71% [CI -0.02] | -3708 (10) | -7285 (18) | -1628 (1) | -493 (1) | static filter (no alpha edge) |
| 500 | ST Crash | 1.65x [CI 0.46] | -3806 (7) | +382 (6) ✅ | +0 (0) | -114 (1) | Phase 2 ✅ |
| 500 | MT Crash | 1.06x [CI 0.53] | -3386 (7) | +0 (0) | -564 (1) | -114 (1) | static filter (no alpha edge) |
