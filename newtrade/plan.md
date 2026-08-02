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

### 4.2 Dynamic Position Sizing (Fast Ramp Quadratic Default)

Production uses **Fast Ramp Quadratic** position sizing (`fast_ramp_quadratic`, $m=0.70, \Delta Z_{\text{full}}=0.40$):

$$S_t = \begin{cases} \text{sign}(Z_t) \cdot \left(m + (1-m) \cdot \min\left(1.0, \ \left(\frac{|Z_t| - Z_{\text{th}}}{\Delta Z_{\text{full}}}\right)^2\right)\right) & \text{if } |Z_t| > Z_{\text{th}} \\ 0 & \text{otherwise} \end{cases}$$

- **Min Position Floor ($m=0.70$)**: 70% size upon passing threshold. Easily absorbs 16 bps roundtrip transaction friction.
- **Full Ramp Margin ($\Delta Z_{\text{full}}=0.40$)**: Ramps quadratically to 100% position size as signal exceeds threshold by $+0.40\sigma$.
- **Performance Lift**: Boosts Portfolio Cost Sharpe (**0.817 vs 0.791 Binary Baseline, +0.026 lift**) and reduces Max Drawdown by **7.6% (8.09% vs 8.76%)** across all 3 ETFs simultaneously.

### 4.3 Summary of Position Sizing Research & Tried Options

| Model Mode | Formulation | Findings & Empirical Outcome |
|---|---|---|
| **Binary Baseline** | $S_t = \pm 1.0$ if $|Z_t| > Z_{\text{th}}$ | Hard gate step function. High drawdowns (8.76% MaxDD), rigid all-or-nothing allocation. |
| **Continuous Ungated** | $S_t = \text{clip}(k Z_t, -1, 1)$ | No threshold gate. High trade frequency on noise signals, severe transaction fee drag. |
| **Standard Tanh / Quad** | $S_t = \tanh((Z - Z_{\text{th}})/\gamma)$ | Ramp parameter $\gamma=1.5$ too slow; requires $+1.5\sigma$ excess signal to reach full size. Avg size collapsed to ~0.35–0.45. |
| **Fast Ramp Linear ($m=0.50, \Delta Z=0.30$)** | $S_t = m + (1-m)\frac{\Delta Z}{0.30}$ | Excellent drawdown reduction (-43.9%), but low $m=0.50$ floor diluted returns under 16 bps friction. |
| **Fast Ramp Linear ($m=0.70, \Delta Z=0.40$)** | $S_t = m + (1-m)\frac{\Delta Z}{0.40}$ | Strong performance (0.813 Avg Sharpe, -7.3% MaxDD). Linear ramp to 100%. |
| **Fast Ramp Quad ($m=0.70, \Delta Z=0.40$) [WINNER]** | $S_t = m + (1-m)\left(\frac{\Delta Z}{0.40}\right)^2$ | **Production Default**. Quadratic curve starting at 70% floor. Top Portfolio Sharpe (**0.817**), **-7.6% MaxDD reduction** (0.0809 vs 0.0876). |

---

## 5. Execution & Stop-Loss

### 5.1 Trade Protocol
- **Window**: Signal at 10:00 → enter → exit at 14:35.
- **Instruments**: ETF spot (default) or index futures (`--future`: IF88/IC88/IH88).
- **Friction**: 8 bps per side (16 bps round-trip) + 2 bps stop-loss slippage when triggered.

### 5.2 Intraday Stop-Loss: Time-Decay Trailing (3% Spot / 30% Option)

Production uses `time_decay_trailing`:
- **Spot ETF / Futures**: Param = 0.03 (3% spot trailing, tightening by 40% near close).
- **Option Portfolio (`--option`)**: Param = 0.30 (`opt_time_decay_trailing` default, 30% initial trailing gap, tightening by 40% to 18% near close).
- **Direct Option Stop Price**: Trails peak option premium $P_{\text{peak}}(t)$ directly on option contract RMB quotes ($P_{\text{stop}}(t) = P_{\text{peak}}(t) \times (1.0 - \theta(t))$).
- **Time Tightening**: $\theta(t) = \theta_{\text{start}} \times (1.0 - 0.40 \times f_t)$. Prevents holding dying option premiums into market close as late-day theta decay accelerates.

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
| Spot Stop-Loss | time_decay_trailing=0.03 | Cuts intraday spot losers |
| Option Stop-Loss | opt_time_decay_trailing=0.30 | +0.205 Sharpe lift on 300ETF, -49.4% MaxDD |
| Fee | 8 bps (Spot) / 4 RMB per side (Option) | Stress-tested |
| Feature Floor | ≥ 10 | 50ETF/588000ETF disabled |

**CLI**: `python newtrade/run_backtest.py --scheme icw` (all defaults are production-optimal)

---

## 7. Key Empirical Findings

1. **Rolling Tail IC > Expanding IC**: 480d tail Spearman dominates full-history Pearson, especially for large pools (500ETF: +64%). The "tail" component is key, not just "rolling."
2. **Hysteresis > Threshold Adaptation**: Feature churn is the real problem. Stabilizing selection beats all threshold adaptations (percentile, walk-forward, variance-scaled).
3. **ICW > Multi-Score**: Pure IC weighting with shrinkage beats composite scores (IC+IR+Monotonicity). Adding IR introduces noise.
4. **Fixed K=10**: Cross-K Sharpe differences ≤ 0.15 (noise). Per-ETF K tuning = overfitting.
5. **Direct Option Time-Decay Trailing**: Direct option price time-decay trailing stop (`opt_time_decay_trailing`, $\theta_{\text{start}}=0.30$, $c_{\text{tight}}=0.40$) achieves **1.251 Sharpe** (+0.205 lift) and slashes MaxDD from **22.87% to 11.57%** (-49.4% DD reduction) on 300ETF.
6. **CPCV 100% Positive**: All active ETFs show 100% positive folds in combinatorial purged cross-validation.
7. **DSR Significant**: 159915ETF achieves DSR = 0.965 (SIGNIFICANT at 10 trials). 500ETF marginal (0.934).

---

## 8. Architecture

```
newtrade/
├── plan.md                  # This document
├── REPORT.md                # Latest OOS backtest report (auto-generated)
├── REPORT_option.md         # Option portfolio OOS backtest report
├── run_backtest.py          # Main CLI (--scheme, --ic-mode, --hysteresis, --year, --decay, --option)
├── run_production.py        # Production ensemble CLI (DSR & CPCV validated)
├── weighting.py             # ICW, EW, hysteresis, adaptive_exit_rank, ONC selection
├── strategy.py              # Threshold sweep, position sizing, ETF simulation
├── option_strategy.py       # Capital-constrained option portfolio execution & 5m stoploss engine
├── utils.py                 # Data loaders, expanding z-score, rolling tail IC (Numba)
├── robustness.py            # DSR, CPCV, PBO, sensitivity analysis
├── research_stoploss.py     # 1m ETF intraday stop-loss simulator
├── research_option_stoploss.py # Option intraday stop-loss simulator & Train/OOS benchmark
├── glm.py / glm_backtest.py # Experimental Ridge GLM scheme
└── tests/                   # A/B test suite
    ├── test_option_stoploss_ab.py # Multi-arm option stoploss A/B testing suite
    ├── test_weighting_ab.py       # 11-arm weighting pipeline comparison
    ├── test_zthreshold_ab.py      # 7-arm threshold system comparison
    ├── test_hysteresis_sweep.py   # Exit-rank × threshold grid search
    └── run_ab_test_tail_ic.py     # Rolling tail IC window comparison
```

### Data Dependencies
- `day-model-new/data/selected_pool_{ETF}_{side}.json` — admitted feature pools
- `day-model-new/data/cluster_assignments_{ETF}_{side}.json` — ONC clusters
- `data/{ETF}_1d.parquet` — daily ETF prices
- `data/{ETF}_1m.parquet` — 1-minute bars (for ETF stoploss simulation)
- `data/{ETF}_historical_prices_5m.parquet` — 5-minute option contract prices

---

## 9. A/B Test History

### Weighting Pipeline (2026-08)
11 arms × 3 ETFs. TailIC_ICW confirmed optimal. Multi-score variants all underperform. See `tests/test_weighting_ab.py`.

### Z-Threshold System (2026-08)
7 arms × 3 ETFs (with stoploss). Baseline threshold is robust. Hysteresis beats all threshold adaptations. See `tests/test_zthreshold_ab.py`.

### Hysteresis Exit-Rank Sweep (2026-08)
Adaptive ER formula validated. Wider = better up to cap. RollPct480 adds no value on top of hysteresis. See `tests/test_hysteresis_sweep.py`.

### Option Intraday Stop-Loss Benchmark (2026-08)
5 arms × 3 ETFs. `opt_time_decay_trailing` (30% initial gap, 40% time decay) and `spot_time_decay_trailing` confirmed optimal. Direct option trailing stop cuts MaxDD on 300ETF from 22.87% to 11.57% while boosting Sharpe to 1.251 (+0.205 lift). See `tests/test_option_stoploss_ab.py`.
