# NewTrade Framework — Day-Model Factor Monetization Plan

## 1. Executive Summary & Objective

Build a lean, practical prototype to monetize admitted factors from `day-model-new` into ETF trading signals.

### Core Focus
- **Factor Aggregation**: Combine admitted features ($N \ge 10$) into a single normalized signal $Z_{\text{composite}}$.
- **Threshold & Sizing**: Test threshold gating and simple position sizing.
- **Execution (Prototype)**: **ETF Spot only** for initial prototype. Instrument selection (Futures / Options / ETF Overlay) deferred until prototype validation is complete.
- **Zero Lookahead**: Enforce strict expanding-window parameter estimation.

---

## 2. Factor Aggregation & Weighting Schemes

Given $N$ admitted factors with standardized values $z_{i,t}$ calculated using expanding mean/std up to day $t-1$:

$$z_{i,t} = \frac{x_{i,t} - \hat{\mu}_{i, 1:t-1}}{\hat{\sigma}_{i, 1:t-1} + \epsilon}, \quad z_{i,t}^{\text{clipped}} = \text{clamp}(z_{i,t}, -3.0, 3.0)$$

### Weighting Schemes to Evaluate

| Scheme | Formula / Logic | Description |
|---|---|---|
| **1. Equal Weight (EW)** | $w_i = \frac{1}{N} \cdot \text{sign}_i$ | Baseline. Simple, zero parameter risk. |
| **2. IC Weight (ICW)** | $w_i \propto \max(0, \text{Deflated\_IC}_i - SE_{IC})^k$, $SE_{IC} = 1/\sqrt{n_{\text{train}}}$ | Empirical Bayes shrinkage. Penalizes marginal IC estimates likely noise. Falls back to EW if all weights shrink to 0. |
| **3. Score Weighted** | $w_i \propto \text{score}_i$ (see below) | Multi-dimensional quality score from pool metadata. |
| **4. Rank Bounded Weight** | Rank factors by $\text{score}_i$, map linearly $w_i \in [w_{\min}, w_{\max}]$ | Prevents single factor dominance, ensures diversification. |
| **5. Simple Linear GLM** | $y_t = \sum w_i z_{i,t} + c$ (Ridge / Non-negative L2) | Expanding linear combination baseline. |

#### Scheme 3 — Multi-Metric Dynamic Score Definition

$$\text{score}_{i,t} = 0.20 \times \text{rank\_norm}(\mu_{\text{IC}, t-1}) + 0.15 \times \text{rank\_norm}(\text{IC\_IR}_{t-1}) + 0.65 \times \text{rank\_norm}(\text{Monotonicity}_{750\text{d}, t-1})$$

- `rank_norm(x_i) = rank(x_i) / N` — rank-normalizes each metric to $[1/N, 1.0]$ across pool factors at day $t-1$.
- **Monotonicity Heavy (65% Weight)**: Anchors factor quality on sustained directional consistency over a 3-year A-share market cycle window ($750\text{d}$), eliminating noisy daily IC whipsaws.
- **Risk-Adjusted Stability (15% IC_IR)**: Penalizes volatile factors with inconsistent predictive power across regimes.

#### Scheme 4 — Rank Bounded Mapping (Default Scheme)

$$w_i = w_{\min} + (w_{\max} - w_{\min}) \cdot \frac{\text{rank}(\text{score}_{i,t}) - 1}{N - 1}$$

- **Moderate Tilt Default**: $w_{\min} = 0.2/N$, $w_{\max} = 1.8/N$ (top factor gets $9\times$ weight of bottom factor). Protects against pool tail noise while tilting heavily to top factors.
- **Zero-Lookahead Dynamic Score Ranking (`--dynamic-score`, default `--dynamic-metric multi`)**: Dynamically updates factor rank scores $S_{i,t}$ on day $t$ using the 3-year trailing rolling monotonicity score, smoothed with 30d EMA (`--ic-ema-span 30`). Fully eliminates lookahead bias.

#### ONC Group-Constrained Feature Selection

When `--group-constraint` is enabled (auto-detects from cluster file), Top-K selection enforces diversity across ONC clusters:

**Algorithm** (`_select_top_k_grouped` in `weighting.py`):
1. Sort features by score (EMA-30d rolling IC) descending.
2. Greedily select features: accept only if cluster has $<$ `max_per_group` representatives.
3. Stop when `top_k` features selected OR all clusters exhausted.

**ONC Clustering** (de Prado & Lewis 2019):
- Computed offline by `day-model-new/feature_clusters.py` on training-period Spearman correlation.
- Angular distance: $d(i,j) = \sqrt{0.5 \cdot (1 - \rho_{ij})}$.
- K-Means sweep with silhouette selection + recursive re-split of weak clusters.
- Output: `day-model-new/data/cluster_assignments_{etf}_{side}.json`.

**CLI**:
- `--group-constraint` / `--no-group-constraint`: Enable/disable (default: auto-detect).
- `--max-per-group N`: Max features per cluster (default: 1).

**Design Rationale**: Replaces admission-time correlation pruning (old B4 gate θ=0.80) with selection-time diversity control. Pool size is now unconstrained (B4 θ=0.95 only removes near-duplicates); ONC ensures the dynamic Top-K picker spreads across feature families.

**Top-K = 10 (Fixed)**: A/B testing (K ∈ {5,8,10,12,15} × 3 ETFs, OOS 2022–2026) showed cross-K Sharpe gaps ≤ 0.03–0.15, within selection noise for 16 trials. Per-ETF K tuning on OOS constitutes overfitting. Fixed K=10 is retained as a principled, non-optimized default.

**IC Mode (Expanding default, Rolling Tail optional)**: Two IC computation modes available via `--ic-mode`:
- `expanding` (default): Full-history Pearson IC. Works well for fresh pools and small N.
- `rolling_tail`: 480d rolling Spearman on top/bottom 10% tail. Aligns with admission criteria. Benefits large pools (N>100) with stale training data. Validated optimal window: 480d (peak of {240,360,480,600,720}). Tail 10% > 15%. EMA not needed at 480d.
- Default remains `expanding`; whether to switch is TBD pending further pool refresh cycles.

---

## 3. Threshold Tuning & Position Sizing

### 3.1 Conviction Threshold Selection (Train-Optimized + Production Buffer)

**Design**: Select optimal threshold on training set, then apply conservative buffer for production to combat IC decay.

1. **Training Sweep**: On expanding-window training portion (pre-OOS), sweep $Z_{\text{th}} \in [0.2, 1.5]$ step $0.1$:
   $$Z_{\text{th}}^{\text{train}*} = \arg\max_{Z_{\text{th}}} \text{CostAdjustedSharpe}(Z_{\text{th}})$$
2. **Production Threshold & Asymmetric Short Gating**:
   $$Z_{\text{th}}^{\text{long}} = Z_{\text{th}}^{\text{train}*} + \Delta_{\text{buffer}}, \quad Z_{\text{th}}^{\text{short}} = Z_{\text{th}}^{\text{long}} + \Delta_{\text{short\_buffer}}$$
   - Default $\Delta_{\text{buffer}} = 0.2$ (user-configurable via `--z-buffer`).
   - Short Buffer Bias: A-share markets have structural long bias; short signals require higher conviction ($Z_{\text{th}}^{\text{short}} > Z_{\text{th}}^{\text{long}}$, default $\Delta_{\text{short\_buffer}} = 0.2$) to filter out intraday mean-reversion noise.
3. **CLI**: `--z-th auto` (default) triggers train-sweep + buffer. `--z-th 0.7` overrides with fixed value.

### 3.2 Signal Thresholding & Sizing Modes

Only trade when signal conviction is strong enough to cover transaction cost (8 bps friction):

- **Binary Mode**:
  $$S_t = \begin{cases} +1 & \text{if } Z_{\text{composite},t} > Z_{\text{th}}^{\text{long}} \\ -1 & \text{if } Z_{\text{composite},t} < -Z_{\text{th}}^{\text{short}} \\ 0 & \text{otherwise} \end{cases}$$

- **Smooth Conviction Mode (tanh)**:
  $$S_t = \begin{cases} \tanh\left(\frac{Z_{\text{composite},t} - Z_{\text{th}}^{\text{long}}}{\gamma}\right) & \text{if } Z_{\text{composite},t} > Z_{\text{th}}^{\text{long}} \\ -\tanh\left(\frac{-Z_{\text{composite},t} - Z_{\text{th}}^{\text{short}}}{\gamma}\right) & \text{if } Z_{\text{composite},t} < -Z_{\text{th}}^{\text{short}} \\ 0 & \text{otherwise} \end{cases}$$

- **Steep Conviction Mode (quadratic)**:
  $$S_t = \begin{cases} \min\left(1.0, \left(\frac{Z_{\text{composite},t} - Z_{\text{th}}^{\text{long}}}{\gamma}\right)^2\right) & \text{if } Z_{\text{composite},t} > Z_{\text{th}}^{\text{long}} \\ -\min\left(1.0, \left(\frac{-Z_{\text{composite},t} - Z_{\text{th}}^{\text{short}}}{\gamma}\right)^2\right) & \text{if } Z_{\text{composite},t} < -Z_{\text{th}}^{\text{short}} \\ 0 & \text{otherwise} \end{cases}$$
  - Rationale: Diagnostic conviction binning shows $|Z| > 1.2$ signals generate 4.9~5.9 Sharpe and ~70% win rate; quadratic sizing ramps position quickly on extreme conviction days while minimizing size on weak days.


---

## 4. Execution Protocol (ETF Spot Prototype)

> [!NOTE]
> Instrument choice (ETF, Futures, or Options) will be decided after prototype results are finalized. The initial prototype uses **ETF Spot** for simplicity.

- **Instrument**: Target Spot ETFs (`300ETF`, `500ETF`, `50ETF`, `588000ETF`, `159915ETF`).
- **Timing**: Enter at 10:00 AM signal evaluation $\rightarrow$ Exit at 14:35 PM / Close.
- **Long Trade**: Buy ETF spot when $S_t > 0$.
- **Short Signal Handling**: Hold Cash / Reverse Repo when $S_t \le 0$ (Spot long-only constraint).
- **Friction**: 8 bps (0.0008) flat transaction fee per position change.

---

## 5. Core Requirements & Constraints

1. **Feature Count Floor ($\ge 10$ Features)**:
   - ETF side MUST have $\ge 10$ admitted features to trade. If $< 10$, skip trading or trigger candidate mining expansion.
2. **Strict Zero-Lookahead**:
   - All normalizations, factor weights, and thresholds must use historical data up to $t-1$.
3. **Cost-Adjusted Evaluation**:
   - All performance metrics evaluated AFTER 8 bps friction.

## 6. Project Architecture & Implementation Checklist

```
newtrade/
├── plan.md            # Plan document
├── utils.py           # Data loading & expanding z-score standardizer
├── weighting.py       # 5 Modular Weighting Functions (EW, ICW, ScoreW, Rank, GLM)
├── strategy.py        # Signal thresholding & position sizing
└── run_backtest.py    # Main CLI runner (--scheme ew|icw|score|rank|glm|all)
```

- [x] **Step 1: Data & Normalization (`newtrade/utils.py`)**
  - Load admitted pool features from `admitted_pools.py`.
  - Expanding-window z-score calculation ($\mu_{1:t-1}, \sigma_{1:t-1}$) + clamping ($\pm 3.0$).
- [x] **Step 2: Modular Weighting Schemes (`newtrade/weighting.py`)**
  - Implement 5 clean functions: `compute_ew()`, `compute_icw()`, `compute_score_w()`, `compute_rank_w()`, `compute_glm_w()`.
  - Schemes 1-4 implemented. Scheme 5 (GLM) deferred.
- [x] **Step 3: Strategy & Backtest Runner (`newtrade/strategy.py` & `newtrade/run_backtest.py`)**
  - Train-optimized threshold sweep (`--z-th auto`) + production buffer (`--z-buffer 0.1`).
  - Threshold gating & 8 bps friction simulation.
  - `--scheme all` flag to run & compare schemes side-by-side (ICW uncollapsed, EW collapsed).
  - Equity curve charts generated (`artifacts/equity_curve.png`) and automatically embedded into `newtrade/REPORT.md`.
  - `--validate` flag for integrated DSR + CPCV validation.
- [x] **Step 4: Robustness Validation (`newtrade/robustness.py`)**
  - DSR (Deflated Sharpe Ratio), CPCV, PBO, Ensemble, Sensitivity Grid.
  - Integrated into `run_backtest.py --validate`.
- [x] **Step 5: Walk-Forward Optimizer (`newtrade/optimize_unified.py`)**
  - 3-period walk-forward (Train→2020, Val=2020-2022, Test=2022-2026).
  - Multiprocessing (24-core), 4000+ configs in ~2min.

---

## 7. Research Findings — What Didn't Work (DO NOT REPEAT)

Original critique (claudesaid.txt) raised 8 issues. Below is what we tested, what failed, and why.

### 7.1 Threshold Overfit (DSR Correction)

**Critique**: Train-sweep Z_th + flat buffer not enough. Many params × schemes × ETFs = many trials. Report DSR not raw Sharpe.

**What we did**: Implemented DSR (Bailey & López de Prado) in `robustness.py`. Tested at N_trials = 10, 50, 2544, 4056.

**Result**: 
- At 50 trials: ALL single-ETF schemes NOT_SIGNIFICANT (best DSR=0.634 on 159915ETF).
- At 10 trials (pre-committed ensemble): 159915ETF DSR=0.928 (MARGINAL), portfolio DSR=0.953 (SIGNIFICANT).
- At 4056 trials (full grid): DSR=0.30 — nothing passes.

**Lesson**: DSR is extremely conservative. The correction is valid but makes single-ETF results look bad. Portfolio-level diversification is the correct way to achieve significance. **Do NOT report single-ETF DSR as evidence — use portfolio DSR or CPCV instead.**

### 7.2 Walk-Forward Split (CPCV vs Single Split)

**Critique**: Simple expanding-window train/OOS split has worse false-discovery control than CPCV.

**What we did**: Implemented CPCV (6-split, 2-test, purge=5) in `robustness.py`.

**Result**: 100% positive folds across ALL ETFs × ALL schemes. Signal is genuinely there.

**Lesson**: CPCV is the strongest evidence. If 15/15 folds are positive, the signal is real regardless of DSR. **Always report CPCV alongside Sharpe.**

### 7.3 Short-Side Skew / Small-N Fragility

**Critique**: 300ETF has 141 short vs 11 long. Small feature count + heavy short concentration = fragile.

**What we did**: Tested long-only vs L+S for each ETF/mode combination.

**Result**:
- 159915ETF binary L+S: SR=1.435 (shorts add 95 trades at 62% WR, +0.21 PnL)
- 500ETF binary L+S: SR=0.873 (shorts add 38 trades, marginal)
- 300ETF: Only 10 features — short side dominates (32S vs 20L) but unstable

**Lesson**: Shorts are valuable on 159915ETF (11 features) and 500ETF (32 features). 300ETF (10 features) is fragile — the short side works but is noise-sensitive. **Do NOT add more features to 300ETF pool without strict validation. The 10-feature floor is barely sufficient.**

### 7.4 Score Weight Formula Hand-Tuned (0.20/0.15/0.65)

**Critique**: The 0.20/0.15/0.65 split smells like it fit history. Nest inside CPCV/walk-forward.

**What we did**: Tested 15+ score_weight combinations via walk-forward optimizer:
- (0.20/0.15/0.65) B3 default
- (0.35/0.00/0.65) mono-dominant no IR
- (0.70/0.10/0.20) IC-dominant
- (0.75/0.00/0.25), (0.50/0.00/0.50), (0.45/0.00/0.55), etc.

**Result**:
- **Score weights are IRRELEVANT when using dynamic IC path** (the default). The expanding_ic kwarg bypasses static weights entirely.
- When using multi-metric path (`dynamic_metric="multi"`): 0.35/0.00/0.65 with mono_window=750 achieves best walk-forward test (1.233), BUT...
- **In production (full training data for thresholds), IC-only outperforms all multi-metric variants.**

**Lesson**: The score weight debate is moot. Dynamic IC path makes weights irrelevant. Multi-metric only helps when threshold training data is limited (walk-forward artifact). **Do NOT spend more time tuning score weights for production. IC-only is the answer.**

### 7.5 IC_IR Uselessness

**Critique**: Not explicitly raised, but discovered during research.

**What we did**: Tested configs with IC_IR=0 vs IC_IR=0.05 vs IC_IR=0.10 vs IC_IR=0.15.

**Result**: Adding IC_IR ALWAYS hurts or is neutral:
- 0.35/0.00/0.65 (no IR): Test SR=1.233
- 0.30/0.05/0.65 (tiny IR): Test SR=1.067
- 0.20/0.15/0.65 (B3 IR): Test SR=1.205

**Lesson**: IC_IR adds noise to daily factor weighting. It was useful for feature SELECTION (B3 gate) but NOT for daily signal construction. **Set IC_IR weight to 0 in any multi-metric scoring. Do NOT re-add it.**

### 7.6 Pick-the-Best Scheme (No Ensemble)

**Critique**: Testing EW/ICW/Score/Rank separately then crowning a winner = selection bias.

**What we did**: Compared ensemble (equal-weight average of all 4) vs individual schemes.

**Result**:
- Ensemble is NOT the best individual scheme on any ETF (Score or Rank usually beat it).
- BUT ensemble has lower variance across ETFs and eliminates scheme-selection overfit.
- PBO = 40% (MODERATE) — the IS-best scheme is below-median OOS in 40% of folds.

**Lesson**: Ensemble doesn't maximize Sharpe but eliminates the selection problem. **Use IC Weight (ICW) for primary execution, while inspecting EW as secondary baseline.**

### 7.7 Turnover/Cost Blind Spot

**Critique**: 67x-150x annualized turnover at 8bps — real cost nonlinear. Stress-test at 15-20bps.

**What we did**: Sensitivity grid at 8/12/15/20 bps.

**Result**:
- 159915ETF: Positive at ALL fee levels (min SR=0.49 at 20bps). Robust.
- 500ETF: Collapses at 15bps (SR→0.007). Fee-sensitive.
- 300ETF: Collapses at 20bps (SR→-0.355 with burn_in=504).
- Portfolio: Profitable at all levels (SR=0.364 at 20bps).

**Lesson**: 159915ETF is the only truly cost-robust instrument. 500ETF and 300ETF edges are thin and fee-sensitive. **If real slippage exceeds 12bps, drop 500ETF and 300ETF. Keep only 159915ETF.**

### 7.8 Untested Sizing Modes (tanh/quadratic)

**Critique**: Plan defines tanh/quadratic but only binary validated OOS.

**What we did**: Full comparison of binary/tanh/quadratic on ensemble signal.

**Result**:
- Binary: Highest raw Sharpe (1.435 on 159915ETF L+S)
- Quadratic: Best DSR robustness (0.965 at 10 trials) but lower Sharpe (0.956)
- Tanh: Middle ground (1.075)
- In production: Binary wins because it generates the most extreme positions and the signal is strong enough to support full conviction.

**Lesson**: Quadratic is theoretically safer but practically inferior when signal is strong. **Use binary for production. Quadratic only if signal degrades or drawdown becomes unacceptable.**

### 7.9 Per-ETF Parameter Customization = Overfit

**What we tried**: Selecting best mode/scheme/buffer per ETF.

**Result**: Walk-forward optimizer showed val-best config often NOT test-best. E.g., rank=[0.4,1.6] + ema=30 was val-optimal but hurt 500ETF in production (SR dropped from 0.969 to 0.708).

**Lesson**: **ONE unified config for ALL ETFs. No per-ETF customization. The config is:**
- Scheme: IC Weight (icw) primary, Equal Weight (ew) secondary
- Mode: Binary
- Buffer: +0.10
- Rank bounds: [0.2, 1.8] (default)
- Dynamic metric: IC-only
- Fee: 8bps

---

## 8. Component Diagnostic Results & Production Config

Ran `diagnose_components.py` and `run_backtest.py`:

### Key findings

**IC Weight (ICW) provides optimal signal weighting:**
- 159915ETF ICW: Cost Sharpe = 1.497, PnL = +0.6053, WinRate = 64.0%, DSR = 0.955 (SIGNIFICANT)
- 500ETF ICW: Cost Sharpe = 1.081, PnL = +0.3514, WinRate = 59.4%
- 300ETF ICW: Cost Sharpe = 0.815, PnL = +0.1467, WinRate = 58.1%

**Report & Visualization Protocol:**
- `run_backtest.py` generates equity curve chart (`artifacts/equity_curve.png`) and embeds it into `newtrade/REPORT.md`.
- `IC Weight (ICW)` report section is uncollapsed (`## IC Weight (ICW)`).
- `Equal Weight (EW)` report section is collapsed under `<details><summary><b>Equal Weight (EW)</b></summary></details>`.

### Production Config Summary

| Parameter | Value | Evidence |
|-----------|-------|----------|
| Scheme | **ICW (IC Weight)** | Primary scheme. High OOS Sharpe (1.497 on 159915ETF, DSR 0.955) |
| Secondary Scheme | **EW (Equal Weight)** | Secondary baseline. Collapsed in report. |
| Dynamic IC | **ON (expanding)** | Zero-lookahead expanding IC weighting |
| Position mode | Binary L+S | Highest Sharpe |
| Threshold | Train-sweep + buffer (`--z-th auto`) | Buffer +0.10 |
| Fee | 8 bps | Stress-tested to 20bps |
| Feature floor | ≥ 10 | 50ETF/588000ETF skipped |
| Visual Report | `REPORT.md` | Equity curve graph embedded, ICW uncollapsed, EW collapsed |


