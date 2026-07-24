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

#### Scheme 3 — Score Definition (B3-Inspired, Pool-Metadata-Only)

$$\text{score}_i = 0.40 \times \text{rank\_norm}(\text{deflated\_ic}_i) + 0.35 \times \text{rank\_norm}(\text{ic\_ir}_i) + 0.25 \times \text{rank\_norm}(\text{monotonicity}_i)$$

- `rank_norm(x_i) = rank(x_i) / N` — maps each metric to $[1/N, 1.0]$ within the pool.
- Uses only fields already stored in `admitted_pools.py`: `deflated_ic`, `ic_ir`, `monotonicity`.
- **Why not B3 directly?** B3 (`0.4×Mono + 0.3×Sortino + 0.2×|TailIC| + 0.1×|OverallIC|`) is an *admission gate* that requires per-candidate `simulate_returns()` for Sortino — expensive and not stored per pool item. `ic_ir` (mean IC / std IC) is the information-ratio analog capturing the same "risk-adjusted predictive power" concept.
- **Design principle**: Admission (B3) decides IF a feature enters the pool; weighting decides HOW MUCH influence it gets. Different objectives → different formulas.

#### Scheme 4 — Rank Bounded Mapping (Enhanced)

$$w_i = w_{\min} + (w_{\max} - w_{\min}) \cdot \frac{\text{rank}(\text{score}_i) - 1}{N - 1}$$

- **Moderate Tilt Default**: $w_{\min} = 0.2/N$, $w_{\max} = 1.8/N$ (top factor gets $9\times$ weight of bottom factor). Protects against pool tail noise while tilting heavily to top factors.
- **Mapping Shapes**: Supports `linear`, `power` ($R^p$), `softmax` ($\exp(\tau R/N)$), and `top_k` truncation.
- **Zero-Lookahead Expanding Rolling IC Ranking (`--dynamic-ic`)**: Dynamically updates factor rank scores $S_{i,t}$ on day $t$ using historical expanding factor IC calculated strictly on data up to $t-1$. Automatically downweights decaying factors OOS.

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

- [ ] **Step 1: Data & Normalization (`newtrade/utils.py`)**
  - Load admitted pool features from `admitted_pools.py`.
  - Expanding-window z-score calculation ($\mu_{1:t-1}, \sigma_{1:t-1}$) + clamping ($\pm 3.0$).
- [x] **Step 2: Modular Weighting Schemes (`newtrade/weighting.py`)**
  - Implement 5 clean functions: `compute_ew()`, `compute_icw()`, `compute_score_w()`, `compute_rank_w()`, `compute_glm_w()`.
  - Schemes 1-4 implemented. Scheme 5 (GLM) deferred.
- [ ] **Step 3: Strategy & Backtest Runner (`newtrade/strategy.py` & `newtrade/run_backtest.py`)**
  - Train-optimized threshold sweep (`--z-th auto`) + production buffer (`--z-buffer 0.2`).
  - Threshold gating & 8 bps friction simulation.
  - `--scheme all` flag to run & compare all 5 schemes side-by-side in one pass.

