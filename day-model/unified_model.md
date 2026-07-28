# Unified Model Training Manifold (`unified_model.md`)

## 1. Overview & Motivation

In previous iterations of the `day-model` training pipeline, feature selection and regularization were treated as disjoint categorical choices (e.g., `skglm_huber_l1`, `skglm_mcp`, `ridge`). This categorical discretization led to two major systemic defects:

1. **Search Space Fragmentation**: Hyperparameter optimization algorithms (e.g., TPE in Optuna) evaluated each penalty model in isolated sub-spaces, preventing smooth transfer of gradient/surrogate knowledge across penalty regimes.
2. **"Hard Fall to Ridge" Cliff**: When feature collinearity caused $L_1$-based or standard MCP coordinate descent to fail or over-sparsify, the optimizer abruptly fell back to pure Ridge regression. This resulted in zero feature selection and coefficient bloat.

To solve both issues, the `day-model` introduces the **Unified Model Training Manifold**. This architecture embeds datafit robustness, $L_1$ sparsity, $L_2$ shrinkage, and non-convex Minimax Concave Penalty (MCP) variable selection into a single continuous estimator manifold parameterization.

---

## 2. Mathematical Formulation

The estimator is implemented as a `GeneralizedLinearEstimator` comprising a robust Huber loss datafit and a hybrid `MCP_plus_L2` penalty solved via Accelerated/Anderson Coordinate Descent (`AndersonCD`).

### 2.1 Optimization Objective

$$\min_{w \in \mathbb{R}^p} \sum_{i=1}^n L_\delta(y_i - x_i^T w) + P_{\alpha, \rho, \gamma}(w)$$

Where:
* $x_i \in \mathbb{R}^p$ represents the standardization-transformed feature vector at decision bar 10:00.
* $y_i = \ln\left(\frac{P_{\text{exit}}}{P_{\text{entry}}}\right)$ is the full-day log return from 10:00 to 14:35 across all 5 ETFs.
* $w \in \mathbb{R}^p$ is the model coefficient vector.

---

### 2.2 Datafit: Huber Loss ($L_\delta$)

To handle heavy-tailed financial returns and macro news outliers, the loss function $L_\delta(r)$ replaces standard OLS quadratic loss:

$$L_\delta(r) = \begin{cases} 
\frac{1}{2} r^2 & \text{if } |r| \le \delta \\ 
\delta |r| - \frac{1}{2}\delta^2 & \text{if } |r| > \delta 
\end{cases}$$

* **Parameter `huber_delta` ($\delta$)**: Controls the transition boundary from quadratic (Gaussian-like) loss to linear ($L_1$-like) loss.
* Bounds: $\delta \in [0.5, 5.0]$.

---

### 2.3 Penalty: $\text{MCP\_plus\_L2}(w)$

The unified penalty combines the non-convex selection properties of MCP with the quadratic stabilization of Ridge regularization:

$$P_{\alpha, \rho, \gamma}(w) = \sum_{j=1}^p p_{\text{MCP}}(w_j; \alpha_1, \gamma) + \frac{\mu}{2} \sum_{j=1}^p w_j^2$$

#### Parameterization Mapping:
The global regularization budget $\alpha_{\text{total}}$ (`unified_alpha`) and the sparse-vs-ridge mix parameter $\rho$ (`unified_rho`) continuously control penalty weights:

$$\alpha_1 = \alpha_{\text{total}} \times \rho \quad (L_1 / \text{MCP Sparsity Weight})$$
$$\mu = \alpha_{\text{total}} \times (1 - \rho) \quad (L_2 \text{ Ridge Weight})$$
$$\gamma = \text{unified\_gamma} \quad (\text{MCP Concavity Parameter})$$

#### MCP Component Formula $p_{\text{MCP}}(\theta; \alpha_1, \gamma)$:

$$p_{\text{MCP}}(\theta; \alpha_1, \gamma) = \begin{cases} 
\alpha_1 |\theta| - \frac{\theta^2}{2\gamma} & \text{if } |\theta| \le \gamma \alpha_1 \\ 
\frac{1}{2} \gamma \alpha_1^2 & \text{if } |\theta| > \gamma \alpha_1 
\end{cases}$$

---

## 3. Manifold Hyperparameters & Search Space

The manifold is completely parameterized by 4 continuous knobs:

| Hyperparameter | Symbol | Range | Scaling | Description |
| :--- | :--- | :--- | :--- | :--- |
| `unified_alpha` | $\alpha_{\text{total}}$ | $[10^{-5}, 10.0]$ | Log-uniform | Total regularization budget spanning unregularized to heavily penalized models. |
| `unified_rho` | $\rho$ | $[0.0, \rho_{\max}]$ | Uniform | Sparse vs. Ridge mix ratio. $\rho=0 \implies$ pure Ridge; $\rho \to 1 \implies$ pure MCP/ElasticNet. |
| `unified_gamma` | $\gamma$ | $[1.5, 10^4]$ | Log-uniform | Concavity parameter. Low $\gamma \implies$ unbiased selection; high $\gamma \implies L_1$ ElasticNet behavior. |
| `huber_delta` | $\delta$ | $[0.5, 5.0]$ | Uniform | Huber robust loss threshold for response outliers. |

### 3.1 Adaptive Collinearity Capping ($\rho_{\max}$)
High feature collinearity (large condition number $\kappa(X)$) can disrupt non-convex coordinate descent. The maximum allowable $\rho$ is dynamically constrained per trial:

$$\rho_{\max} = \text{clip}\left(1.0 - 0.005 \times (\kappa(X_{\text{raw}}) - 15.0), \, 0.5, \, 0.95\right)$$

This ensures that under high collinearity ($\kappa(X) > 15.0$), a minimal Ridge regularization component $\mu > 0$ is preserved to stabilize the solver.

---

## 4. Proximal Operator & Coordinate Descent Solver

`skglm` solves the continuous manifold using coordinate descent with custom proximal step mapping and subdifferential distance calculations.

### 4.1 Proximal Operator for `MCP_plus_L2`

For coordinate stepsize $\eta$, the proximal step decouples the quadratic $L_2$ term into scaling factors before applying `prox_MCP`:

$$\text{denom} = 1.0 + \eta \cdot \mu$$
$$v' = \frac{v}{\text{denom}}, \quad \eta' = \frac{\eta}{\text{denom}}$$
$$\text{prox}_{\text{MCP\_plus\_L2}}(v, \eta, \alpha_1, \gamma, \mu) = \text{prox}_{\text{MCP}}\left(v', \eta', \alpha_1, \gamma\right)$$

### 4.2 Subdifferential Distance (Optimality Metric)

The subdifferential distance $d_j$ for feature $j$ under active set working selection $ws$ is:

$$d_j = \begin{cases}
\max(0, |\nabla_j| - \alpha_1) & \text{if } w_j = 0 \\
\left| \nabla_j + \alpha_1 \text{sign}(w_j) - \frac{w_j}{\gamma} + \mu w_j \right| & \text{if } 0 < |w_j| < \gamma \alpha_1 \\
\left| \nabla_j + \mu w_j \right| & \text{if } |w_j| \ge \gamma \alpha_1
\end{cases}$$

where $\nabla_j$ is the gradient of the Huber loss with respect to $w_j$.

---

## 5. Continuous Regime Transitions

By sweeping $(\rho, \gamma)$, the manifold smoothly interpolates between classical estimator types:

```
                          unified_rho (ρ) -> 1.0
                 ┌──────────────────────────────────────┐
                 │                                      │
                 │   Unbiased MCP                       │   L1 / ElasticNet Proxy
                 │   (γ ≈ 1.5)                          │   (γ -> 10000.0)
                 │   - Aggressive selection             │   - Soft thresholding
                 │   - Nearly unbiased nonzero weights │   - Lasso-like shrinkage
                 │                                      │
                 └──────────────────┬───────────────────┘
                                    │
                                    │  unified_rho (ρ) -> 0.0
                                    ▼
                         Pure Huber-Ridge Regression
                         (α1 = 0, μ = unified_alpha)
                         - All features retained
                         - Smooth L2 shrinkage
```

1. **Pure Ridge Regression** ($\rho = 0.0$):
   * $\alpha_1 = 0$, $\mu = \alpha_{\text{total}}$.
   * Penalty reduces to $\frac{\mu}{2} \|w\|_2^2$.
2. **Nearly Unbiased Non-Convex MCP** ($\rho \to 1.0, \gamma \to 1.5$):
   * Aggressive non-convex penalization. Features above threshold $\gamma \alpha_1$ incur zero marginal penalty, avoiding $L_1$ shrinkage bias on strong alpha signals.
3. **L1 ElasticNet Proxy** ($\rho \to 1.0, \gamma \to \infty$):
   * MCP transition boundary $\gamma \alpha_1 \to \infty$, causing $p_{\text{MCP}}(\theta) \to \alpha_1 |\theta|$.
   * Penalty reduces to ElasticNet: $\alpha_1 \|w\|_1 + \frac{\mu}{2} \|w\|_2^2$.

---

## 6. Code Integration Reference

### Estimator Construction (`train_model.py`)

```python
from skglm import GeneralizedLinearEstimator
from skglm.datafits import SkglmHuber
from skglm.solvers import AndersonCD
from penalties import MCP_plus_L2

def _build_model(model_type: str, params: dict):
    solver = AndersonCD(max_epochs=2000, tol=1e-3)
    alpha = params["unified_alpha"]
    rho = params["unified_rho"]
    gamma = params["unified_gamma"]
    delta = params["huber_delta"]

    return GeneralizedLinearEstimator(
        datafit=SkglmHuber(delta=delta),
        penalty=MCP_plus_L2(
            alpha=alpha * rho,
            gamma=gamma,
            mu=alpha * (1.0 - rho)
        ),
        solver=solver,
    )
```

### Optuna Safety Pruning (Condition Number Safeguard)

```python
# Regularized Condition Number Check
SAFE_KAPPA = 40.0 * raw_X_cond
HARD_KAPPA = 10.0 * SAFE_KAPPA

if reg_kappa > HARD_KAPPA:
    raise optuna.TrialPruned(
        f"Regularized condition number {reg_kappa:.2f} > HARD_KAPPA ({HARD_KAPPA:.2f})"
    )
```
