# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2015_2023`

Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)

- **300ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **50ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **500ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`
- **588000ETF**: Train `2020-11-01` → `2025-01-01` | Holdout OOS from `2025-01-01` | Lockbox from `2025-07-01`
- **159915ETF**: Train `2015-01-01` → `2022-01-01` | Holdout OOS from `2022-01-01` | Lockbox from `2024-03-01`

_\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._
_Note: Cost metrics incorporate 8 bps (0.0008) transaction cost per position state transition (realistic for liquid ETFs). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._

## 1. Filter Funnel

Candidate counts at each admission gate. Shows where features get pruned.

| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 221 | 40 | 12 | 7 | 3 | 3 | 3 | 2 | 2 |
| 300ETF | long | 236 | 32 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 235 | 43 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 213 | 27 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 227 | 33 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 237 | 34 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 228 | 59 | 30 | 26 | 13 | 13 | 13 | 7 | 7 |
| 500ETF | long | 238 | 37 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 236 | 41 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 228 | 48 | 16 | 12 | 2 | 2 | 2 | 2 | 2 |
| 159915ETF | long | 238 | 32 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 236 | 43 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 2 | +0.1231 | [+0.0806, +0.1660] | +0.2245 | [+0.1177, +0.3090] | +0.9273 | 7.04% | 1.4120 | 4.34% | 0.8767 | 1.7452 | 6.17% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 7 | +0.1571 | [+0.1162, +0.1999] | +0.2522 | [+0.1495, +0.3450] | +0.8182 | 8.04% | 1.3221 | 5.31% | 0.8777 | 1.6103 | 5.37% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 2 | +0.1532 | [+0.1079, +0.1975] | +0.2444 | [+0.1538, +0.3261] | +0.8545 | 8.41% | 1.2315 | 6.00% | 0.8815 | 1.2608 | 16.09% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 2 | +0.0707* | [-0.0030, +0.1391] | +0.1366* | [-0.0801, +0.2802] | +0.6485 | 2.72% | 0.5797 | 0.69% | 0.1482 | 0.2320 | 5.15% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 7 | +0.1027 | [+0.0251, +0.1776] | +0.1082* | [-0.0556, +0.2580] | +0.8303 | 4.84% | 0.9450 | 2.08% | 0.4104 | 0.7560 | 8.54% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 2 | +0.1266 | [+0.0546, +0.1925] | +0.1566* | [-0.0130, +0.3133] | +0.8424 | 6.88% | 0.9739 | 5.12% | 0.7263 | 1.7397 | 5.69% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 4. OOS Lockbox Performance

Most recent OOS window (lockbox start to present). Strictest generalization test.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |

## 5. Admitted Features — Full Details

Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the
BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.

### 300ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.0965 | +0.2243 | +0.2248 | 0.0000 | +0.5652 | +0.7360 | 0.000 |
| `bar_body_rng_0` | +1 | +0.0910 | +0.1504 | +0.1517 | 0.0028 | +0.4998 | +0.6641 | 0.204 |

### 300ETF / long
No features admitted.

### 300ETF / short
No features admitted.

### 50ETF / single
No features admitted.

### 50ETF / long
No features admitted.

### 50ETF / short
No features admitted.

### 500ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | +1 | +0.1682 | +0.2632 | +0.2649 | 0.0000 | +0.7902 | +0.8084 | 0.000 |
| `max_up_ret` | +1 | +0.1619 | +0.2317 | +0.2328 | 0.0000 | +0.6107 | +0.7370 | 0.576 |
| `volatility_expansion_trend_vector` | +1 | +0.1151 | +0.2174 | +0.2189 | 0.0000 | +0.4977 | +0.7036 | 0.733 |
| `close_vs_open_range` | +1 | +0.1100 | +0.2057 | +0.2072 | 0.0000 | +0.5363 | +0.7042 | 0.795 |
| `first_bar_return` | +1 | +0.1457 | +0.1931 | +0.1945 | 0.0002 | +0.6014 | +0.7180 | 0.567 |
| `max_down_ret` | +1 | +0.1248 | +0.1750 | +0.1774 | 0.0006 | +0.5100 | +0.6590 | 0.534 |
| `first_30min_return` | +1 | +0.1142 | +0.1557 | +0.1567 | 0.0018 | +0.4824 | +0.6954 | 0.812 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | +1 | +0.1455 | +0.2279 | +0.2282 | 0.0000 | +0.6028 | +0.7011 | 0.000 |
| `max_up_ret` | +1 | +0.1282 | +0.2136 | +0.2148 | 0.0000 | +0.5942 | +0.7165 | 0.423 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.
