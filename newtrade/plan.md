# NewTrade Framework — Day-Model Factor Monetization Plan

## 1. Executive Summary & Objective

Monetize admitted factors from `day-model-new` into intraday ETF spot and index futures trading signals.

### Core Focus & Scope
- **Factor Aggregation**: Combine admitted features ($N \ge 10$) into normalized composite signal $Z_{\text{composite}}$.
- **Active ETF Scope**: `300ETF`, `500ETF`, `50ETF`, `159915ETF` (`588000ETF` disabled due to 2021–2025 regime shift).
- **Mandatory Feature Floor**: $\ge 10$ admitted features per ETF/side. Skip trading if count floor unfulfilled.
- **Zero Lookahead**: Enforce strict expanding-window parameter estimation ($\mu_{1:t-1}, \sigma_{1:t-1}$ standardizer, expanding/rolling IC at $t-1$, train-swept thresholds).
- **Intraday Trade Window**: Enter 10:00 AM signal evaluation $\rightarrow$ Exit 14:35 PM / Close.
- **Friction-Adjusted**: 8 bps (0.0008) flat transaction fee per position state transition. Stress-tested up to 20 bps.

---

## 2. Preprocessing, Selection & Weighting Schemes

### 2.1 Dynamic Expanding Standardization

Standardize raw factor $x_{i,t}$ using historical expanding statistics up to day $t-1$:

$$z_{i,t} = \text{clamp}\left(\frac{x_{i,t} - \hat{\mu}_{i, 1:t-1}}{\hat{\sigma}_{i, 1:t-1} + \epsilon}, -3.0, 3.0\right)$$

### 2.2 Top-K Selection & ONC Diversity Control

- **Top-K Truncation ($K=10$ Default)**: Select top $K=10$ features dynamically by rolling IC or score. Prevents feature dilution on large pools (e.g. 500ETF with 32 features) while preserving non-destructive performance on lean pools (159915ETF with 11 features).
- **ONC Group Constraint (`--group-constraint`)**: Greedy top-$K$ selection enforcing maximum `max_per_group` features per cluster, using Optimal Number of Clusters (ONC, de Prado 2019).
  - Angular distance: $d(i,j) = \sqrt{0.5 \cdot (1 - \rho_{ij})}$.
  - Cluster files auto-detected per pool vintage (`day-model-new/data/cluster_assignments_{etf}_{side}{suffix}.json`).

### 2.3 Weighting Schemes

Given $N$ factors standardized to $z_{i,t}$:

| Scheme | Formula / Logic | Status / Description |
|---|---|---|
| **1. IC Weight (ICW)** | $w_i = \max(0, \text{IC}_{i,t-1} - SE_{\text{IC}})^k \cdot \text{sign}_i$ | **Production Default**. Empirical Bayes shrinkage. High OOS Sharpe. |
| **2. Equal Weight (EW)** | $w_i = \frac{1}{K} \cdot \text{sign}_i$ across top $K$ features | **Secondary Baseline**. Zero parameter risk. |
| **3. Score Weighted (ScoreW)** | $w_i \propto \text{score}_i$ | *Deprecated / Research Only*. Underperformed ICW/EW in OOS testing; excluded from `ALL_SCHEMES` and `REPORT.md`. |
| **4. Rank Bounded Weight (RankW)** | Rank factors by $\text{score}_i$, map linearly to $[w_{\min}, w_{\max}]$ | *Deprecated / Research Only*. Underperformed in dynamic tail IC mode; excluded from `ALL_SCHEMES` and `REPORT.md`. |

> Note: `run_backtest.py` limits active benchmark schemes to `ALL_SCHEMES = ["icw", "ew"]`. `score` and `rank` schemes remain in `weighting.py` for legacy research comparison only.

### 2.4 IC Estimation Modes

- `expanding` (default baseline): Full-history Pearson IC from day 1 to $t-1$.
- `rolling_tail` (`TailIC_ICW`, production optimal): 480d rolling Spearman IC calculated on top/bottom 10% tail. Dominates A/B testing across multi-year OOS evaluation.

---

## 3. Threshold Tuning & Position Sizing

### 3.1 Conviction Threshold Selection (Train-Sweep + Buffer)

1. **Training Sweep**: On expanding pre-OOS dataset, sweep $Z_{\text{th}} \in [0.2, 1.5]$ step 0.1:
   $$Z_{\text{th}}^{\text{train}*} = \arg\max_{Z_{\text{th}}} \text{CostAdjustedSharpe}(Z_{\text{th}})$$
2. **Production Threshold & Asymmetric Short Gating**:
   $$Z_{\text{th}}^{\text{long}} = Z_{\text{th}}^{\text{train}*} + \Delta_{\text{buffer}}, \quad Z_{\text{th}}^{\text{short}} = Z_{\text{th}}^{\text{long}} + \Delta_{\text{short\_buffer}}$$
   - Default long buffer: $\Delta_{\text{buffer}} = +0.10$ (`--z-buffer 0.10`).
   - Default short buffer: $\Delta_{\text{short\_buffer}} = +0.10$ (filters A-share intraday noise given structural long bias).

### 3.2 Position Sizing Modes

- **Binary Mode (Production Default)**:
  $$S_t = \begin{cases} +1 & \text{if } Z_{\text{composite},t} > Z_{\text{th}}^{\text{long}} \\ -1 & \text{if } Z_{\text{composite},t} < -Z_{\text{th}}^{\text{short}} \\ 0 & \text{otherwise} \end{cases}$$
- **Tanh Mode (Smooth Conviction)**: $S_t = \tanh((|Z| - Z_{\text{th}})/\gamma) \cdot \text{sign}(Z)$.
- **Quadratic Mode (Steep Conviction)**: $S_t = \min(1.0, ((|Z| - Z_{\text{th}})/\gamma)^2) \cdot \text{sign}(Z)$.

---

## 4. Execution Protocol & Intraday Stop-Loss Findings

### 4.1 Execution Protocol
- **Trade Window**: Signal calculated at 10:00 AM $\rightarrow$ position entered $\rightarrow$ exited at 14:35 PM / Close.
- **Instruments**:
  - ETF Spot: Binary Long-Short simulation or `--long-only` spot constraint.
  - Index Futures: Continuous CFFEX futures (`--future`, IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF).
- **Friction**: 8 bps (0.0008) flat transaction fee per position state transition.

### 4.2 Intraday Stop-Loss Research Finding: REJECTED
- Benchmarked 5 intraday 1m stop-loss methods (Fixed %, Trailing %, Volatility ATR, Time-Decay, Intraday Reversal) in `research_stoploss.py`.
- **Result**: Intraday stop-losses degrade net Sharpe by $-0.337$ on average across all ETFs.
- **Reason**: Intraday noise triggers premature exits on temporary pullbacks before 14:35 edge materializes, while doubling transaction friction.
- **Decision**: Intraday stop-loss **omitted**. Trade full 10:00 $\rightarrow$ 14:35 holding window.

---

## 5. Multi-Period Pool Management & Migration Protocol

### 5.1 Pool Vintages & Auto-Cutoff
- Supported pool vintages: `old` (2010–2023 train), `_p2016_2024` (2016–2024 train), `_p2018_2026` (2018–2026 train).
- CLI flags: `--pool-period` (`old`, `_p2016_2024`, `_p2018_2026`, `all`), `--year` (OOS start year), `--decay` (evaluates pool decay over future years).
- Dynamic OOS start auto-inferred from pool cutoff date.

### 5.2 Automated Pool Migration Protocol (`run_migration.py`)
- **Cadence**: 2-year scheduled pool re-selection via `day-model-new/run_periods.py`.
- **Quarterly Monitor**: `--monitor` tracks rolling 60d IC of pool factors; alerts on signal decay.
- **Switching Gate**: Candidate pool accepted ONLY if Candidate OOS Sharpe $>$ Current OOS Sharpe + min threshold.
- **Transition**: Percentile P75 threshold smoothing during pool transition + automatic rollback guard. See [MIGRATION_PLAN.md](MIGRATION_PLAN.md).

---

## 6. Architecture & File Inventory

```
newtrade/
├── plan.md                  # Master strategy design document
├── plan_glm.md              # Scheme 5 GLM experimental design document
├── MIGRATION_PLAN.md        # Pool switching protocol & migration gates
├── TODO.md                  # Experiment logs & A/B test results
├── REPORT.md                # Default OOS backtest report (ICW & EW)
├── REPORT_production.md     # Production ensemble robustness report
├── run_production.py        # Production ensemble CLI (DSR & CPCV validated)
├── run_backtest.py          # Main CLI runner (--year, --pool-period, --decay, --scheme, --ic-mode)
├── run_migration.py         # Pool migration monitor & switching CLI
├── regenerate_admitted_pools.py  # Pool registry code generator
├── portfolio_backtest.py    # Multi-ETF portfolio backtest & fee stress test
├── robustness.py            # DSR, CPCV, PBO, Ensemble, Sensitivity module
├── research_stoploss.py     # 1m intraday stop-loss simulator
├── utils.py                 # Data loader, recipe calculator, expanding standardizer, futures mapper
├── weighting.py             # ICW, EW, ScoreW, RankW weighting & Top-K/ONC selection
├── strategy.py              # Threshold optimizer, position sizer, ETF spot simulator
└── tests/                   # Verification & research A/B test suite
```

---

## 7. Key Empirical Lessons

1. **TailIC_ICW Optimal**: 480d rolling tail IC + ICW shrinkage dominates multi-metric scoring across multi-year OOS A/B tests (Avg Sharpe 1.238 vs 0.97–1.18).
2. **Portfolio DSR vs Single-ETF Conservatism**: Single-ETF DSR is highly conservative at 50+ trials, but multi-ETF equal-weight portfolio achieves DSR = 0.953 (SIGNIFICANT).
3. **CPCV Validation**: 100% positive folds across 6-split 2-test CPCV for all active ETFs.
4. **Cost Sensitivity**: 159915ETF is robust up to 20 bps fee (SR 0.49). 500ETF and 300ETF require fee $\le 12$ bps.
5. **Score Weights & IC_IR**: Adding IC_IR or static score weights introduces noise in daily weighting; IC-only / TailIC is cleaner and superior.
6. **Top-K Truncation**: Fixed $K=10$ provides robust dilution protection without per-ETF overfitting.
7. **Unified Configuration**: Single parameter set across ETFs prevents selection bias overfit.

---

## 8. Production System Configuration

| Parameter | Default Value | Rationale / Evidence |
|---|---|---|
| **Primary Scheme** | `icw` (IC Weight) | Highest OOS Sharpe, DSR-validated |
| **Secondary Scheme** | `ew` (Equal Weight) | Non-parameterized secondary baseline |
| **IC Mode** | `rolling_tail` (480d window, 10% tail) | TailIC_ICW rank #1 in A/B testing |
| **Top-K Truncation** | $K=10$ | Solves feature dilution on large pools |
| **ONC Group Constraint** | `--group-constraint` | Enforces 1 feature per cluster for diversity |
| **Position Sizing** | `binary` (Long-Short) | Highest Sharpe (+1 / 0 / -1) |
| **Threshold Buffer** | $\Delta_{\text{buffer}} = +0.10$ | Prevents IC decay overfitting |
| **Friction** | 8 bps (0.0008) | Real ETF friction simulation |
| **Feature Floor** | $\ge 10$ features | 588000ETF disabled |
| **Trade Window** | 10:00 entry $\rightarrow$ 14:35 exit | Intraday spot / index futures |
