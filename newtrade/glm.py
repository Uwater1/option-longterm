#!/usr/bin/env python3
"""
Scheme 5 — Simple Linear GLM (Expanding Ridge) for NewTrade framework.

Implements expanding-window Ridge regression on sign-aligned z-scored factors.
Zero lookahead: at day t, coefficients are fitted on [0, t-1] only.

Design constraints (see plan_glm.md):
  - No feature selection (handled upstream by day-model-new admission gates)
  - No additional filters
  - Non-negative coefficient clamp (default ON)
  - Fixed alpha grid sweep on training portion
"""

import numpy as np


def _ridge_fit(
    X: np.ndarray,
    y: np.ndarray,
    alpha: float,
    penalty_diag: np.ndarray = None,
    sample_weights: np.ndarray = None,
) -> np.ndarray:
    """
    Closed-form Ridge regression (no intercept).
    beta = (X' W X + alpha * D^{-1})^{-1} X' W y
    """
    n_features = X.shape[1]
    if sample_weights is not None:
        sw_sqrt = np.sqrt(sample_weights)[:, None]
        X_w = X * sw_sqrt
        y_w = y * sample_weights
        XtX = X_w.T @ X_w
        Xty = X.T @ y_w
    else:
        XtX = X.T @ X
        Xty = X.T @ y
        
    if penalty_diag is not None:
        reg = alpha * np.diag(penalty_diag)
    else:
        reg = alpha * np.eye(n_features)
        
    try:
        beta = np.linalg.solve(XtX + reg, Xty)
    except np.linalg.LinAlgError:
        beta = np.linalg.lstsq(XtX + reg, Xty, rcond=None)[0]
    return beta


def _kns_ridge_fit(
    X: np.ndarray,
    y: np.ndarray,
    alpha: float,
    gamma: float = 1.0,
    sample_weights: np.ndarray = None,
) -> np.ndarray:
    """
    Kozak, Nagel, & Santosh (JFE 2020) PCA-space anisotropic Ridge fit.
    
    1. Eigen-decomposition of Gram matrix S = X' W X
    2. Construct PC penalty d_k = 1 / max(lambda_k, floor)^gamma
    3. Normalize d_k so mean(d_k) = 1.0 (preserves alpha scale)
    4. Solve in PC space: b_k = (Z_pc' W y)_k / (lambda_k + alpha * d_k)
    5. Transform back: beta = V @ b
    """
    n_samples, n_features = X.shape
    if sample_weights is not None:
        sw_sqrt = np.sqrt(sample_weights)[:, None]
        X_w = X * sw_sqrt
        y_w = y * sample_weights
    else:
        X_w = X
        y_w = y

    XtX = X_w.T @ X_w
    Xty = X.T @ y_w

    try:
        eigvals, V = np.linalg.eigh(XtX)
    except np.linalg.LinAlgError:
        return _ridge_fit(X, y, alpha, sample_weights=sample_weights)

    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    V = V[:, idx]

    max_ev = max(float(eigvals[0]), 1e-12)
    floored_eigvals = np.maximum(eigvals, max_ev * 1e-6)

    # KNS penalty diagonal: d_k = 1 / (lambda_k ^ gamma)
    penalty_pc = 1.0 / (floored_eigvals ** gamma)
    penalty_pc = penalty_pc / penalty_pc.mean()

    # Project into PC space
    Xty_pc = V.T @ Xty

    # Solve in PC space (diagonal system)
    denom = eigvals + alpha * penalty_pc
    b = Xty_pc / denom

    # Transform back: beta = V @ b
    beta = V @ b
    return beta


def _fit_model(
    X: np.ndarray,
    y: np.ndarray,
    alpha: float,
    prior_mode: str = "kns",
    kns_gamma: float = 1.0,
    penalty_diag: np.ndarray = None,
    sample_weights: np.ndarray = None,
) -> np.ndarray:
    """Fit model under requested prior_mode ('kns', 'ic', 'iso')."""
    if prior_mode == "kns":
        return _kns_ridge_fit(X, y, alpha, gamma=kns_gamma, sample_weights=sample_weights)
    elif prior_mode == "ic":
        return _ridge_fit(X, y, alpha, penalty_diag=penalty_diag, sample_weights=sample_weights)
    else:
        return _ridge_fit(X, y, alpha, penalty_diag=None, sample_weights=sample_weights)


def _prepare_regression_data(
    Z_hist: np.ndarray,
    ret_hist: np.ndarray,
    target_mode: str = "bj_sign",
) -> tuple:
    """
    Build X, y, sample_weights for expanding fit based on target_mode.
    
    Modes:
      'return': Standard MSE regression (y = trade_returns, X = Z_signed)
      'bj_return': Britten-Jones Sharpe regression (y = 1, X = Z_signed * trade_returns)
      'bj_sign': Britten-Jones directional regression (y = 1, X = Z_signed * sign(trade_returns))
      'bj_sortino': Britten-Jones downside-weighted Sortino regression (y = 1, X = Z_signed * trade_returns, sample_weights)
    """
    if target_mode == "return":
        return Z_hist, ret_hist, None
    elif target_mode == "bj_return":
        X = Z_hist * ret_hist[:, None]
        y = np.ones(len(Z_hist), dtype=np.float64)
        return X, y, None
    elif target_mode == "bj_sign":
        X = Z_hist * np.sign(ret_hist)[:, None]
        y = np.ones(len(Z_hist), dtype=np.float64)
        return X, y, None
    elif target_mode == "bj_sortino":
        X = Z_hist * ret_hist[:, None]
        y = np.ones(len(Z_hist), dtype=np.float64)
        weights = np.where(ret_hist < 0, 2.0, 1.0)
        return X, y, weights
    else:
        raise ValueError(f"Unknown target_mode: '{target_mode}'")


def _compute_ic(pred: np.ndarray, ret: np.ndarray) -> float:
    """Pearson correlation (IC) between predictions and returns."""
    if len(pred) < 10:
        return 0.0
    std_p = np.std(pred)
    std_r = np.std(ret)
    if std_p < 1e-12 or std_r < 1e-12:
        return 0.0
    return float(np.corrcoef(pred, ret)[0, 1])


def _build_ic_penalty_diag(pool: list, n_features: int) -> np.ndarray:
    """
    Build IC-weighted penalty diagonal D^{-1} from pool metadata.
    Features with weaker deflated_ic get penalized more (larger penalty).
    
    penalty_i = 1 / max(deflated_ic_i, floor)
    Normalized so mean(penalty) = 1.0 (preserves alpha scale).
    """
    ics = np.array([item.get("deflated_ic", 0.05) for item in pool[:n_features]], dtype=np.float64)
    ics = np.maximum(ics, 0.01)  # floor to avoid division by zero
    penalty = 1.0 / ics
    # Normalize so mean penalty = 1.0 (alpha retains its meaning)
    penalty = penalty / penalty.mean()
    return penalty


def select_best_alpha(
    Z_signed: np.ndarray,
    trade_returns: np.ndarray,
    alphas: list,
    burn_in: int = 504,
    train_end_idx: int = None,
    fee_bps: float = 0.0008,
    clamp_nonneg: bool = True,
    penalty_diag: np.ndarray = None,
    target_mode: str = "bj_sign",
    prior_mode: str = "ic",
    kns_gamma: float = 1.0,
) -> tuple:
    """
    Select best Ridge alpha via expanding-window IC evaluation on training portion.
    """
    T, N = Z_signed.shape
    if train_end_idx is None:
        train_end_idx = T
    
    effective_start = max(burn_in, 252)  # need at least 252 samples for first fit
    
    if effective_start >= train_end_idx:
        # Not enough data; return smallest alpha (least regularized)
        return alphas[0], 0.0, []
    
    alpha_results = []
    best_alpha = alphas[0]
    best_ic = -np.inf
    
    for alpha in alphas:
        # Expanding fit on training portion
        predictions = np.zeros(train_end_idx, dtype=np.float64)
        
        # Refit every 5 days during alpha selection (speed optimization)
        refit_cadence = 5
        current_beta = None
        
        for t in range(effective_start, train_end_idx):
            if current_beta is None or (t - effective_start) % refit_cadence == 0:
                X_fit, y_fit, weights = _prepare_regression_data(
                    Z_signed[:t], trade_returns[:t], target_mode=target_mode
                )
                current_beta = _fit_model(
                    X_fit, y_fit, alpha,
                    prior_mode=prior_mode, kns_gamma=kns_gamma,
                    penalty_diag=penalty_diag, sample_weights=weights,
                )
                if clamp_nonneg:
                    current_beta = np.maximum(0.0, current_beta)
            
            predictions[t] = Z_signed[t] @ current_beta
        
        # Evaluate using expanding IC (correlation with returns)
        pred_slice = predictions[effective_start:train_end_idx]
        ret_slice = trade_returns[effective_start:train_end_idx]
        
        ic = _compute_ic(pred_slice, ret_slice)
        
        # Also compute rolling IC stability (fraction of 63-day windows with IC > 0)
        window = 63
        n_windows = 0
        n_positive = 0
        for start in range(0, len(pred_slice) - window, window):
            win_ic = _compute_ic(pred_slice[start:start+window], ret_slice[start:start+window])
            n_windows += 1
            if win_ic > 0:
                n_positive += 1
        stability = n_positive / n_windows if n_windows > 0 else 0.0
        
        # Score: IC * stability (reward both strength and consistency)
        score = ic * (0.5 + 0.5 * stability)
        
        alpha_results.append({
            "alpha": alpha, "ic": round(ic, 4),
            "stability": round(stability, 3), "score": round(score, 4),
        })
        
        if score > best_ic:
            best_ic = score
            best_alpha = alpha
    
    return best_alpha, best_ic, alpha_results


def expanding_ridge_composite(
    Z_signed: np.ndarray,
    trade_returns: np.ndarray,
    alpha: float = None,
    alphas: list = None,
    burn_in: int = 504,
    train_end_idx: int = None,
    clamp_nonneg: bool = True,
    refit_every: int = 1,
    fee_bps: float = 0.0008,
    pool: list = None,
    ic_prior: bool = None,  # deprecated, use prior_mode instead
    n_adaptive: bool = True,
    min_percentile: float = 0.0,
    target_mode: str = "bj_sign",
    prior_mode: str = "ic",
    kns_gamma: float = 1.0,
) -> tuple:
    """
    Produce expanding-window Ridge composite signal.
    
    If alpha is None, runs alpha selection on training portion first.
    
    Args:
      Z_signed: (T, N) sign-aligned z-scores
      trade_returns: (T,) target returns
      alpha: fixed Ridge lambda (if None, auto-select)
      alphas: candidate grid for auto-selection
      burn_in: minimum history before first prediction
      train_end_idx: end of training portion for alpha selection
      clamp_nonneg: clamp beta_i >= 0
      refit_every: refit cadence in days (1 = daily)
      fee_bps: transaction cost
      pool: admitted pool metadata (for IC-weighted prior)
      n_adaptive: scale alpha by N/10 (default False with KNS prior)
      min_percentile: expanding percentile gate for |Z| (0=disabled)
      target_mode: 'return' (MSE), 'bj_return' (Sharpe), 'bj_sign' (Directional), 'bj_sortino' (Sortino)
      prior_mode: 'kns' (Kozak-Nagel-Santosh 2020 eigenstructure), 'ic' (per-feature IC), 'iso' (isotropic)
      kns_gamma: eigenvalue penalty exponent for KNS prior (default 1.0)
      
    Returns:
      Z_composite: (T,) predicted signal
      info: dict with metadata
    """
    T, N = Z_signed.shape
    
    # Handle backward-compat for ic_prior flag
    if ic_prior is True:
        prior_mode = "ic"
    elif ic_prior is False and prior_mode == "ic":
        prior_mode = "iso"
    
    if alphas is None:
        alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    
    # Build IC-weighted penalty diagonal if prior_mode == "ic"
    penalty_diag = None
    if prior_mode == "ic" and pool is not None and len(pool) >= N:
        penalty_diag = _build_ic_penalty_diag(pool, N)
    
    # N-adaptive alpha scaling (only if explicitly enabled)
    n_scale = (N / 10.0) if n_adaptive else 1.0
    
    # Alpha selection
    alpha_results = []
    if alpha is None:
        scaled_alphas = [a * n_scale for a in alphas]
        alpha, best_ic, alpha_results = select_best_alpha(
            Z_signed, trade_returns, scaled_alphas,
            burn_in=burn_in, train_end_idx=train_end_idx,
            fee_bps=fee_bps, clamp_nonneg=clamp_nonneg,
            penalty_diag=penalty_diag, target_mode=target_mode,
            prior_mode=prior_mode, kns_gamma=kns_gamma,
        )
    else:
        alpha = alpha * n_scale
    
    # Full expanding fit with chosen alpha
    Z_raw = np.zeros(T, dtype=np.float64)
    effective_start = max(burn_in, 252)
    
    current_beta = None
    coef_history = []  # sparse snapshots for diagnostics
    
    for t in range(effective_start, T):
        if current_beta is None or (t - effective_start) % refit_every == 0:
            X_fit, y_fit, weights = _prepare_regression_data(
                Z_signed[:t], trade_returns[:t], target_mode=target_mode
            )
            current_beta = _fit_model(
                X_fit, y_fit, alpha,
                prior_mode=prior_mode, kns_gamma=kns_gamma,
                penalty_diag=penalty_diag, sample_weights=weights,
            )
            if clamp_nonneg:
                current_beta = np.maximum(0.0, current_beta)
            
            # Store snapshot every ~63 days (quarterly)
            if (t - effective_start) % 63 < refit_every:
                coef_history.append({"day": t, "beta": current_beta.copy()})
        
        Z_raw[t] = Z_signed[t] @ current_beta
    
    # Re-standardize to unit variance (expanding)
    Z_composite = np.zeros(T, dtype=np.float64)
    sum_x = 0.0
    sum_sq = 0.0
    n_count = 0
    
    for t in range(effective_start, T):
        val = Z_raw[t]
        if n_count >= 63:  # need at least 63 samples for stable std
            mean = sum_x / n_count
            var = (sum_sq / n_count) - (mean * mean)
            std = np.sqrt(var) if var > 1e-12 else 1.0
            Z_composite[t] = (val - mean) / std
        # Update running stats
        sum_x += val
        sum_sq += val * val
        n_count += 1
    
    # Optional percentile gate to control trade frequency
    if min_percentile > 0:
        abs_vals = np.abs(Z_composite)
        for t in range(effective_start + 63, T):
            history = abs_vals[effective_start:t]
            threshold = np.percentile(history[history > 0], min_percentile) if (history > 0).any() else 0.0
            if abs_vals[t] < threshold:
                Z_composite[t] = 0.0
    
    info = {
        "alpha": alpha,
        "alpha_selection_results": alpha_results,
        "burn_in": effective_start,
        "clamp_nonneg": clamp_nonneg,
        "refit_every": refit_every,
        "n_features": N,
        "coef_history": coef_history,
        "raw_std": float(np.std(Z_raw[effective_start:T])) if T > effective_start else 0.0,
        "prior_mode": prior_mode,
        "kns_gamma": kns_gamma,
        "n_adaptive": n_adaptive,
        "n_scale": n_scale,
        "min_percentile": min_percentile,
        "target_mode": target_mode,
    }
    
    return Z_composite, info


