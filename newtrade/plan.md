# NewTrade Framework — Day-Model Factor Monetization

## 1. Executive Summary

NewTrade converts admitted alpha factors from `day-model-new` into intraday ETF trading signals. Each day, a composite Z-score is built from the top-10 features (selected by rolling tail IC with hysteresis), and a binary trading decision is made: go long, go short, or stay flat.

### Core Design
- **Signal**: Weighted average of top-10 z-scored features, where weights come from Empirical Bayes-shrunk IC estimates.
- **Trade**: Enter at 10:00 AM, exit at 14:35 PM same day. Round-trip fee = 16 bps (8bp buy and 8 bp sell).
- **Gate**: Trade only when |Z_composite| exceeds a train-swept conviction threshold.
- **Scope**: 300ETF, 500ETF, 159915ETF (50ETF/588000ETF disabled — insufficient features).
- **Zero Lookahead**: All parameters estimated from data available at $t-1$.

### Production OOS Performance (2022-01 ~ 2025-12, 8 bps fee + stoploss) (check REPORT.md)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 22 | 118 (76L/42S) | 1.021 | 1.415 | +0.2337 | +0.1591 | 3.042 | +0.0746 | 2.837 | 0.0532 | 55.9% (L:56.6%, S:54.8%) | 59.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.10 (train L:0.60/S:1.00) | 193 | 383 (253L/130S) | 1.390 | 2.220 | +0.5091 | +0.1559 | 1.084 | +0.3532 | 4.235 | 0.0814 | 54.8% (L:53.4%, S:57.7%) | 161.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 27 | 253 (154L/99S) | 1.562 | 1.950 | +0.8057 | +0.5079 | 3.012 | +0.2978 | 3.295 | 0.0777 | 58.1% (L:53.9%, S:64.6%) | 115.7x |

---

## 2. Upstream: Feature Selection (day-model-new)

NewTrade consumes features from `day-model-new`'s admission pipeline. Features are intraday alpha factors predicting the 10:00→14:35 ETF return.

### Feature Generation
- **Base features**: ~200 intraday technical indicators computed from 1-minute bars (opening drive, VWAP acceleration, volume momentum, bar structure, etc.)
- **Combinators**: Pairwise and triple combinations via operations (diff, ratio, rank_min, clamp, z-score). Produces 1,500–3,000 candidates per ETF.

### 8-Gate Admission Pipeline (all training-only, zero OOS leakage)

| Gate | Purpose | Key Parameter |
|------|---------|---------------|
| 1. Jackknife Sign Stability | Reject sign-flipping features | 7 yearly chunks, max 1 flip |
| 2. Rolling Guard | Reject unstable rolling IC | mono ≥ 0.60, IR ≥ 0.30 |
| 3. Temporal Validation | Reject decayed signals | recent_ic > 0 |
| 4. BH-FDR | Multiple-testing correction | q = 0.30, 5000 block-shuffled sims |
| 5. Composite Floor (B3) | Beat empirical null | 93rd–97th percentile of null |
| 6. Temporal Stability | Kill artificial mirages | ic_cv × weak_link_cv ≥ 0.15 |
| 7. Quality Gate | Minimum signal strength | deflated_ic ≥ 0.03, sortino > 0 |
| 8. Correlation (B4) | Remove near-duplicates | θ = 0.95 |

### Output
- Per-ETF admitted pool (22–193 features for `single` side)
- ONC cluster assignments (de Prado 2019) for downstream diversity control
- Pool vintages re-trained every 2 years (`_p2015_2023`, `_p2016_2024`, `_p2017_2025`)

---

## 3. Signal Construction Pipeline

The daily signal construction follows this sequence:

```
Raw features → Expanding Z-score → IC Matrix (rolling tail 480d)
    → EMA smoothing → Hysteresis Top-10 Selection (cluster-constrained)
    → ICW Shrinkage Weighting → Z_composite
```

### 3.1 Expanding Z-Score Standardization

$$z_{i,t} = \text{clamp}\left(\frac{x_{i,t} - \hat{\mu}_{i, 1:t-1}}{\hat{\sigma}_{i, 1:t-1}}, -3.0, 3.0\right)$$

Burn-in: 252 days. Zero lookahead (uses only data up to $t-1$).

### 3.2 IC Estimation: Rolling Tail IC (480d)

For each feature $i$ at time $t$, compute Spearman rank correlation between $z_i$ and trade returns using only the top/bottom 10% tail observations within a trailing 480-day window:

$$\text{IC}_{i,t} = \text{SpearmanCorr}(z_i[\text{tail}], r[\text{tail}]) \quad \text{over } [t-480, t-1]$$

- **Why tail**: Focuses on extreme signal days where alpha is strongest.
- **Why rolling 480d**: 2 China trading years. Balances recency vs stability. Validated optimal vs expanding IC and longer windows (600d, 720d).
- **EMA smoothing**: Span = 30d (300ETF/50ETF) or 90d (500ETF/159915ETF) to reduce daily ranking noise.

### 3.3 Feature Selection: Hysteresis + ONC Cluster Constraint

**Problem**: Daily top-10 reselection causes feature churn → Z_composite distribution shifts → threshold instability.

**Solution**: Hysteresis (sticky selection) with adaptive exit rank:

- **Enter**: Feature enters active set when IC rank ≤ 10 AND its ONC cluster is unoccupied.
- **Exit**: Feature exits only when IC rank > `exit_rank` (wider gate than entry).
- **Adaptive exit_rank**: $\min\left(10 + \frac{N - 10}{2},\ 25\right)$ where $N$ = pool size.
  - 300ETF (N=22): exit_rank = 16
  - 159915ETF (N=27): exit_rank = 18
  - 500ETF (N=193): exit_rank = 25 (hard cap)
- **Cluster constraint**: Max 1 feature per ONC cluster in the active set. Ensures diversity across feature families.

**Validated impact**: +26% Sharpe on 300ETF, +12% on 159915ETF vs no-hysteresis baseline.

### 3.4 ICW Shrinkage Weighting

Given the active feature set $\mathcal{A}$ (up to 10 features):

$$w_i = \frac{\max(0, \text{IC}_{i,t} - SE_{\text{IC}})}{\sum_{j \in \mathcal{A}} \max(0, \text{IC}_{j,t} - SE_{\text{IC}})}, \quad SE_{\text{IC}} = \frac{1}{\sqrt{n_{\text{train}}}}$$

Features with IC below the standard error floor get zero weight (Empirical Bayes shrinkage).

### 3.5 Composite Signal

$$Z_{\text{composite},t} = \sum_{i \in \mathcal{A}} w_i \cdot z_{i,t} \cdot \text{sign}_i$$

---

## 4. Threshold & Position Sizing

### 4.1 Conviction Threshold (Train-Sweep + Buffer)

1. **Training sweep**: On pre-OOS data, sweep $Z_{\text{th}} \in [0.5, 1.5]$ step 0.1. Pick the threshold maximizing cost-adjusted Sharpe (with ≥ 8% active days constraint).
2. **Production buffer**: $Z_{\text{th}}^{\text{prod}} = Z_{\text{th}}^{\text{train}} + 0.10$
3. **Asymmetric short**: Short threshold gets additional +0.10 buffer (A-share structural long bias).

### 4.2 Position Sizing (Binary)

$$S_t = \begin{cases} +1 & \text{if } Z_t > Z_{\text{th}}^{\text{long}} \\ -1 & \text{if } Z_t < -Z_{\text{th}}^{\text{short}} \\ 0 & \text{otherwise} \end{cases}$$

Alternative modes (tanh, quadratic) exist but binary is production default.

---

## 5. Execution & Stop-Loss

### 5.1 Trade Protocol
- **Window**: Signal at 10:00 → enter → exit at 14:35.
- **Instruments**: ETF spot (default) or index futures (`--future`: IF88/IC88/IH88).
- **Friction**: 8 bps per side (16 bps round-trip) + 2 bps stop-loss slippage when triggered.

### 5.2 Intraday Stop-Loss: Time-Decay Trailing (3%)

Production uses `time_decay_trailing` with param=0.03:
- Trails the high-water mark of intraday P&L.
- Stop threshold decays over time (tighter near close, looser early).
- Triggered on ~30-40% of active trading days.
- Adds +2 bps execution slippage on stop days.

Enabled by default (`--stoploss`). Disable with `--no-stoploss`.

---

## 6. Production Configuration

| Parameter | Value | Evidence |
|-----------|-------|----------|
| Scheme | ICW (IC Weight) | Highest OOS Sharpe, DSR-validated |
| IC Mode | Rolling Tail (480d, 10%) | Wins A/B test vs expanding IC (+12% avg) |
| EMA Span | 30d (300/50), 90d (500/159915) | Pool-size adaptive smoothing |
| Top-K | 10 | Fixed; prevents dilution on large pools |
| Hysteresis | ON (adaptive exit rank) | +26% on small pools, +12% on medium |
| Exit Rank | min(10 + (N-10)//2, 25) | Pool-adaptive cap |
| ONC Cluster | Max 1 per cluster | Diversity across feature families |
| Position | Binary L+S | Highest Sharpe |
| Threshold | Train-sweep + 0.10 buffer | Robust across regimes |
| Stop-Loss | time_decay_trailing=0.03 | Cuts intraday losers |
| Fee | 8 bps | Stress-tested to 20 bps |
| Feature Floor | ≥ 10 | 50ETF/588000ETF disabled |

**CLI**: `python newtrade/run_backtest.py --scheme icw` (all defaults are production-optimal)

---

## 7. Key Empirical Findings

1. **Rolling Tail IC > Expanding IC**: 480d tail Spearman dominates full-history Pearson, especially for large pools (500ETF: +64%). The "tail" component is key, not just "rolling."
2. **Hysteresis > Threshold Adaptation**: Feature churn is the real problem. Stabilizing selection beats all threshold adaptations (percentile, walk-forward, variance-scaled).
3. **ICW > Multi-Score**: Pure IC weighting with shrinkage beats composite scores (IC+IR+Monotonicity). Adding IR introduces noise.
4. **Fixed K=10**: Cross-K Sharpe differences ≤ 0.15 (noise). Per-ETF K tuning = overfitting.
5. **Unified Config**: Single parameter set across ETFs prevents selection bias.
6. **CPCV 100% Positive**: All active ETFs show 100% positive folds in combinatorial purged cross-validation.
7. **DSR Significant**: 159915ETF achieves DSR = 0.965 (SIGNIFICANT at 10 trials). 500ETF marginal (0.934).

---

## 8. Architecture

```
newtrade/
├── plan.md                  # This document
├── REPORT.md                # Latest OOS backtest report (auto-generated)
├── run_backtest.py          # Main CLI (--scheme, --ic-mode, --hysteresis, --year, --decay)
├── run_production.py        # Production ensemble CLI (DSR & CPCV validated)
├── weighting.py             # ICW, EW, hysteresis, adaptive_exit_rank, ONC selection
├── strategy.py              # Threshold sweep, position sizing, ETF simulation
├── utils.py                 # Data loaders, expanding z-score, rolling tail IC (Numba)
├── robustness.py            # DSR, CPCV, PBO, sensitivity analysis
├── research_stoploss.py     # 1m intraday stop-loss simulator
├── glm.py / glm_backtest.py # Experimental Ridge GLM scheme
└── tests/                   # A/B test suite
    ├── test_weighting_ab.py       # 11-arm weighting pipeline comparison
    ├── test_zthreshold_ab.py      # 7-arm threshold system comparison
    ├── test_hysteresis_sweep.py   # Exit-rank × threshold grid search
    └── run_ab_test_tail_ic.py     # Rolling tail IC window comparison
```

### Data Dependencies
- `day-model-new/data/selected_pool_{ETF}_{side}.json` — admitted feature pools
- `day-model-new/data/cluster_assignments_{ETF}_{side}.json` — ONC clusters
- `data/{ETF}_1d.parquet` — daily ETF prices
- `data/{ETF}_1m.parquet` — 1-minute bars (for stoploss simulation)

---

## 9. A/B Test History

### Weighting Pipeline (2026-08)
11 arms × 3 ETFs. TailIC_ICW confirmed optimal. Multi-score variants all underperform. See `tests/test_weighting_ab.py`.

### Z-Threshold System (2026-08)
7 arms × 3 ETFs (with stoploss). Baseline threshold is robust. Hysteresis beats all threshold adaptations. See `tests/test_zthreshold_ab.py`.

### Hysteresis Exit-Rank Sweep (2026-08)
Adaptive ER formula validated. Wider = better up to cap. RollPct480 adds no value on top of hysteresis. See `tests/test_hysteresis_sweep.py`.
