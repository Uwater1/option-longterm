# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2017_2025`

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
| 300ETF | single | 219 | 40 | 20 | 7 | 5 | 5 | 5 | 3 | 3 |
| 300ETF | long | 236 | 28 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 236 | 36 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 214 | 27 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 229 | 30 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 237 | 37 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 216 | 60 | 32 | 26 | 18 | 18 | 18 | 6 | 6 |
| 500ETF | long | 235 | 27 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 236 | 37 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 223 | 45 | 24 | 11 | 5 | 5 | 5 | 3 | 3 |
| 159915ETF | long | 235 | 35 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 232 | 35 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | +0.0942 | [+0.0501, +0.1346] | +0.2201 | [+0.1185, +0.3147] | +0.8667 | 5.45% | 1.3788 | 2.69% | 0.6926 | 1.4382 | 4.51% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.1264 | [+0.0844, +0.1660] | +0.2572 | [+0.1552, +0.3431] | +0.7818 | 6.83% | 1.5505 | 3.95% | 0.9090 | 1.7158 | 5.18% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 3 | +0.1208 | [+0.0777, +0.1628] | +0.2655 | [+0.1747, +0.3462] | +0.7333 | 7.15% | 1.5392 | 4.53% | 0.9811 | 2.1201 | 5.37% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | -0.0276* | [-0.1641, +0.0878] | -0.0717* | [-0.3437, +0.1711] | -0.2848 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.0352* | [-0.0972, +0.1386] | -0.0971* | [-0.3340, +0.1181] | +0.1879 | -0.38% | -0.1794 | -1.92% | -0.9004 | -1.1647 | 4.20% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 3 | +0.0854* | [-0.0357, +0.1884] | -0.0470* | [-0.3351, +0.1761] | +0.5636 | 1.31% | 0.4830 | -0.17% | -0.0614 | -0.0903 | 2.86% |
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
| `max_up_ret` | +1 | +0.0742 | +0.2051 | +0.2056 | 0.0002 | +0.6225 | +0.7216 | 0.000 |
| `first_bar_return` | +1 | +0.0874 | +0.1925 | +0.1926 | 0.0002 | +0.6512 | +0.7524 | 0.661 |
| `opening_drive_thrust_ratio` | +1 | +0.0880 | +0.1722 | +0.1727 | 0.0004 | +0.5638 | +0.7293 | 0.705 |

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
| `volatility_expansion_trend_vector` | +1 | +0.1070 | +0.2577 | +0.2575 | 0.0000 | +0.6551 | +0.7452 | 0.000 |
| `early_order_flow_imbalance` | +1 | +0.0995 | +0.2348 | +0.2351 | 0.0000 | +0.5819 | +0.7334 | 0.786 |
| `max_up_ret` | +1 | +0.1323 | +0.2006 | +0.1991 | 0.0000 | +0.6170 | +0.7216 | 0.638 |
| `first_bar_return` | +1 | +0.1160 | +0.1983 | +0.1986 | 0.0000 | +0.6758 | +0.7463 | 0.704 |
| `vwap_close_divergence_trend` | +1 | +0.0926 | +0.1534 | +0.1529 | 0.0022 | +0.5998 | +0.7046 | 0.815 |
| `num_up_bars` | +1 | +0.0907 | +0.1213 | +0.1198 | 0.0150 | +0.3576 | +0.6531 | 0.788 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | +1 | +0.1150 | +0.2357 | +0.2357 | 0.0000 | +0.7774 | +0.7545 | 0.000 |
| `max_up_ret` | +1 | +0.1114 | +0.2091 | +0.2080 | 0.0002 | +0.9114 | +0.8132 | 0.703 |
| `bar_body_rng_0` | +1 | +0.1039 | +0.1685 | +0.1695 | 0.0004 | +0.4113 | +0.6562 | 0.685 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.
