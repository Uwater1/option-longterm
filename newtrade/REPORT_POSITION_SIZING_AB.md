# NewTrade Position Sizing A/B Test Report (Min Position Floor Experiment)

**Evaluation Period**: `2022-01-01` to `2026-01-01`  
**Friction Level**: `8.0 bps` (proportional to position size $|S_t|$)  
**Intraday Stop-Loss**: `Enabled (time_decay_trailing=0.03)`  
**ETFs Evaluated**: `300ETF, 500ETF, 159915ETF`  

## Executive Summary

> [!IMPORTANT]
> **Binary Baseline Wins**: Arm A (`binary`) achieved the highest average OOS Cost Sharpe (**1.324**). All continuous position sizing arms underperformed binary sizing in zero-lookahead walk-forward evaluation.

## Ranked Summary Table Across Active ETFs

| Rank | Position Sizing Arm | Avg Cost Sharpe | Sharpe Delta | Avg Net PnL | Avg Max DD | Avg Win Rate | Avg Trades | Avg Pos Size |
|---|---|---|---|---|---|---|---|---|
| 1 | **Arm A: Binary Baseline** | **1.324** | `+0.000` | +0.5162 | 0.0708 | 56.3% | 251 | 1.00 |
| 2 | **Arm F: Quadratic (Min Pos Floor)** | **1.237** | `-0.087` | +0.5351 | 0.0805 | 53.5% | 334 | 0.37 |
| 3 | **Arm D: Gated Prop (Min Pos Floor)** | **1.209** | `-0.115` | +0.5311 | 0.0863 | 53.6% | 361 | 0.30 |
| 4 | **Arm C: Gated Linear (Min Pos Floor)** | **1.209** | `-0.115` | +0.5311 | 0.0863 | 53.6% | 361 | 0.10 |
| 5 | **Arm E: Tuned Tanh (Min Pos Floor)** | **1.209** | `-0.115` | +0.5311 | 0.0863 | 53.6% | 361 | 0.10 |
| 6 | **Arm B: Continuous Ungated** | **0.576** | `-0.749` | +0.3948 | 0.2504 | 51.1% | 969 | 0.24 |

## Per-ETF Detailed Results

### 300ETF

| Position Sizing Arm | Selected Parameters | Cost Sharpe | Net PnL | Max DD | Win Rate | Trades | Avg Pos Size |
|---|---|---|---|---|---|---|---|
| **Arm A: Binary Baseline** | `z_l=1.10, z_s=1.30` | **1.021** | +0.2337 | 0.0532 | 55.9% | 118 | 1.00 |
| **Arm C: Gated Linear (Min Pos Floor)** | `delta=-0.2, m=0.0, k=0.25` | **0.803** | +0.2227 | 0.0600 | 50.8% | 242 | 0.09 |
| **Arm E: Tuned Tanh (Min Pos Floor)** | `delta=-0.2, m=0.0, k=0.25` | **0.803** | +0.2227 | 0.0600 | 50.8% | 242 | 0.09 |
| **Arm D: Gated Prop (Min Pos Floor)** | `delta=-0.2, m=0.0, k=0.25` | **0.803** | +0.2227 | 0.0600 | 50.8% | 242 | 0.32 |
| **Arm F: Quadratic (Min Pos Floor)** | `delta=-0.2, m=0.0, gamma=1.0` | **0.803** | +0.2227 | 0.0600 | 50.8% | 242 | 0.20 |
| **Arm B: Continuous Ungated** | `k=0.25 (z_th=0)` | **0.131** | +0.0626 | 0.3195 | 49.0% | 969 | 0.17 |

### 500ETF

| Position Sizing Arm | Selected Parameters | Cost Sharpe | Net PnL | Max DD | Win Rate | Trades | Avg Pos Size |
|---|---|---|---|---|---|---|---|
| **Arm D: Gated Prop (Min Pos Floor)** | `delta=-0.1, m=0.0, k=0.25` | **1.535** | +0.6516 | 0.0765 | 54.2% | 476 | 0.29 |
| **Arm C: Gated Linear (Min Pos Floor)** | `delta=-0.1, m=0.0, k=0.25` | **1.535** | +0.6516 | 0.0765 | 54.2% | 476 | 0.12 |
| **Arm E: Tuned Tanh (Min Pos Floor)** | `delta=-0.1, m=0.0, k=0.25` | **1.535** | +0.6516 | 0.0765 | 54.2% | 476 | 0.12 |
| **Arm F: Quadratic (Min Pos Floor)** | `delta=-0.1, m=0.3, gamma=0.5` | **1.535** | +0.6516 | 0.0765 | 54.2% | 476 | 0.71 |
| **Arm A: Binary Baseline** | `z_l=0.70, z_s=1.10` | **1.390** | +0.5091 | 0.0814 | 54.8% | 383 | 1.00 |
| **Arm B: Continuous Ungated** | `k=0.50 (z_th=0)` | **0.450** | +0.2622 | 0.1564 | 50.5% | 969 | 0.38 |

### 159915ETF

| Position Sizing Arm | Selected Parameters | Cost Sharpe | Net PnL | Max DD | Win Rate | Trades | Avg Pos Size |
|---|---|---|---|---|---|---|---|
| **Arm A: Binary Baseline** | `z_l=0.90, z_s=1.10` | **1.562** | +0.8057 | 0.0777 | 58.1% | 253 | 1.00 |
| **Arm F: Quadratic (Min Pos Floor)** | `delta=+0.0, m=0.0, gamma=1.0` | **1.374** | +0.7311 | 0.1049 | 55.6% | 284 | 0.18 |
| **Arm D: Gated Prop (Min Pos Floor)** | `delta=-0.1, m=0.0, k=0.25` | **1.289** | +0.7190 | 0.1224 | 55.7% | 366 | 0.29 |
| **Arm C: Gated Linear (Min Pos Floor)** | `delta=-0.1, m=0.0, k=0.25` | **1.289** | +0.7190 | 0.1224 | 55.7% | 366 | 0.09 |
| **Arm E: Tuned Tanh (Min Pos Floor)** | `delta=-0.1, m=0.0, k=0.25` | **1.289** | +0.7190 | 0.1224 | 55.7% | 366 | 0.09 |
| **Arm B: Continuous Ungated** | `k=0.25 (z_th=0)` | **1.146** | +0.8596 | 0.2752 | 53.8% | 969 | 0.18 |
