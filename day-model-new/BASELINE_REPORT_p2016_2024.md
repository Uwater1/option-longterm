# Day-Model Rewrite v3 — Baseline Performance Report

Suffix: `_p2016_2024`

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
| 300ETF | single | 220 | 37 | 17 | 8 | 3 | 3 | 3 | 3 | 3 |
| 300ETF | long | 235 | 36 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| 300ETF | short | 237 | 41 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | single | 214 | 24 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | long | 234 | 35 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50ETF | short | 239 | 42 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | single | 218 | 67 | 38 | 26 | 13 | 13 | 13 | 6 | 6 |
| 500ETF | long | 239 | 29 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 500ETF | short | 236 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | single | 222 | 45 | 23 | 15 | 1 | 1 | 1 | 1 | 1 |
| 159915ETF | long | 237 | 42 | 14 | 1 | 0 | 0 | 0 | 0 | 0 |
| 159915ETF | short | 232 | 43 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## 2. Training-Period Performance (in-sample)

IC-weighted combination model on the training window. Useful for sanity-checking fit.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | +0.1010 | [+0.0574, +0.1441] | +0.2298 | [+0.1272, +0.3194] | +0.7212 | 4.11% | 1.3907 | 1.40% | 0.4812 | 0.8883 | 4.79% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.1280 | [+0.0864, +0.1721] | +0.2394 | [+0.1499, +0.3388] | +0.6727 | 6.67% | 1.4969 | 3.76% | 0.8503 | 1.5187 | 5.28% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 1 | +0.1123 | [+0.0692, +0.1578] | +0.2061 | [+0.1136, +0.3015] | +0.8424 | 5.69% | 1.1476 | 3.73% | 0.7582 | 1.3614 | 7.63% |
| 159915ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |

## 3. Holdout OOS Performance

Out-of-sample from holdout start to present.

| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | +0.0155* | [-0.0719, +0.1093] | +0.0560* | [-0.1537, +0.2391] | +0.6364 | 2.61% | 0.6807 | -0.19% | -0.0505 | -0.1167 | 7.14% |
| 300ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 300ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | single | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 50ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | single | 6 | +0.0933 | [+0.0098, +0.1779] | +0.0345* | [-0.1515, +0.1893] | +0.6485 | 3.48% | 0.6379 | 0.57% | 0.1061 | 0.1882 | 9.27% |
| 500ETF | long | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 500ETF | short | 0 | +0.0000* | [+0.0000, +0.0000] | +0.0000* | [+0.0000, +0.0000] | +0.0000 | 0.00% | 0.0000 | 0.00% | 0.0000 | 0.0000 | 0.00% |
| 159915ETF | single | 1 | +0.0765* | [-0.0111, +0.1566] | +0.0774* | [-0.0884, +0.2349] | +0.7333 | 5.86% | 0.7777 | 3.92% | 0.5222 | 1.2381 | 7.42% |
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
| `bar_body_rng_0` | +1 | +0.0989 | +0.1976 | +0.1979 | 0.0000 | +0.6275 | +0.7054 | 0.000 |
| `max_up_ret` | +1 | +0.0773 | +0.1850 | +0.1850 | 0.0002 | +0.4645 | +0.6740 | 0.555 |
| `opening_drive_thrust_ratio` | +1 | +0.0933 | +0.1783 | +0.1775 | 0.0002 | +0.5398 | +0.7234 | 0.690 |

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
| `net_volume_flow` | +1 | +0.1020 | +0.2221 | +0.2220 | 0.0000 | +0.6976 | +0.7728 | 0.000 |
| `max_up_ret` | +1 | +0.1293 | +0.2055 | +0.2058 | 0.0000 | +0.5418 | +0.6967 | 0.654 |
| `first_bar_return` | +1 | +0.1165 | +0.1959 | +0.1970 | 0.0000 | +0.4899 | +0.6684 | 0.673 |
| `opening_drive_thrust_ratio` | +1 | +0.1384 | +0.1931 | +0.1922 | 0.0000 | +0.6281 | +0.7650 | 0.752 |
| `close_vs_open_range` | +1 | +0.0902 | +0.1705 | +0.1705 | 0.0006 | +0.3944 | +0.6329 | 0.839 |
| `vwap_close_divergence_trend` | +1 | +0.0837 | +0.1606 | +0.1592 | 0.0014 | +0.4241 | +0.6411 | 0.772 |

### 500ETF / long
No features admitted.

### 500ETF / short
No features admitted.

### 159915ETF / single

| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `max_up_ret` | +1 | +0.1123 | +0.2061 | +0.2058 | 0.0002 | +0.7080 | +0.7604 | 0.000 |

### 159915ETF / long
No features admitted.

### 159915ETF / short
No features admitted.

## 6. Recipe Definitions (combo_ features only)

For each admitted combo feature, shows the operation and component base features.
Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.
