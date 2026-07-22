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
| **2. IC Weight (ICW)** | $w_i \propto \max(0, \text{Deflated\_IC}_i)^k$ ($k=1$ or $2$) | Weights by factor historical predictive power. |
| **3. Score Weighted** | $w_i \propto 0.4 \cdot \text{IC}_i + 0.3 \cdot \text{IR}_i + 0.3 \cdot \text{Mono}_i$ | Weights by composite factor quality score. |
| **4. Rank Bounded Weight** | Rank factors by quality, map $w_i \in [0.10, 0.20]$ | Prevents single factor dominance, ensures diversification. |
| **5. Simple Linear GLM** | $y_t = \sum w_i z_{i,t} + c$ (Ridge / Non-negative L2) | Expanding linear combination baseline. |

---

## 3. Threshold Tuning & Position Sizing

### 3.1 Signal Thresholding
Only trade when signal conviction is strong enough to cover transaction cost (8 bps friction):

- **Binary Mode**:
  $$S_t = \begin{cases} +1 & \text{if } Z_{\text{composite},t} > Z_{\text{th}} \\ -1 \text{ (or 0)} & \text{if } Z_{\text{composite},t} < -Z_{\text{th}} \\ 0 & \text{otherwise} \end{cases}$$

- **Smooth Conviction Mode (tanh)**:
  $$S_t = \tanh\left(\frac{Z_{\text{composite},t} \pm Z_{\text{th}}}{\gamma}\right) \quad \text{for } |Z_{\text{composite},t}| > Z_{\text{th}}$$

- **Threshold Sweep**: Evaluate $Z_{\text{th}} \in [0.2, 1.0]$ with step $0.1$.

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
- [ ] **Step 2: Modular Weighting Schemes (`newtrade/weighting.py`)**
  - Implement 5 clean functions: `compute_ew()`, `compute_icw()`, `compute_score_w()`, `compute_rank_w()`, `compute_glm_w()`.
- [ ] **Step 3: Strategy & Backtest Runner (`newtrade/strategy.py` & `newtrade/run_backtest.py`)**
  - Threshold gating ($Z_{\text{th}} \in [0.2, 1.0]$) & 8 bps friction simulation.
  - `--scheme all` flag to run & compare all 5 schemes side-by-side in one pass.

