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


def _ridge_fit(X: np.ndarray, y: np.ndarray, alpha: float, penalty_diag: np.ndarray = None) -> np.ndarray:
    """
    Closed-form Ridge regression (no intercept).
    beta = (X'X + alpha * D^{-1})^{-1} X'y
    
    Args:
      X: (n_samples, n_features)
      y: (n_samples,)
      alpha: L2 penalty strength
      penalty_diag: (n_features,) diagonal of penalty matrix D^{-1}.
                    If None, uses identity (isotropic Ridge).
                    Features with larger penalty_diag values are shrunk more.
      
    Returns:
      beta: (n_features,)
    """
    n_features = X.shape[1]
    XtX = X.T @ X
    Xty = X.T @ y
    if penalty_diag is not None:
        reg = alpha * np.diag(penalty_diag)
    else:
        reg = alpha * np.eye(n_features)
    beta = np.linalg.solve(XtX + reg, Xty)
    return beta


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
) -> tuple:
    """
    Select best Ridge alpha via expanding-window IC evaluation on training portion.
    
    For each candidate alpha, runs expanding fit from burn_in to train_end_idx,
    computes mean expanding IC (correlation of prediction with next-day return),
    and picks the alpha with highest mean IC.
    
    Args:
      Z_signed: (T, N) sign-aligned z-scores
      trade_returns: (T,) target returns
      alphas: list of candidate lambda values
      burn_in: first day to start predicting
      train_end_idx: end of training portion (exclusive). If None, uses full series.
      fee_bps: transaction cost (unused, kept for interface compat)
      clamp_nonneg: whether to clamp beta >= 0
      
    Returns:
      (best_alpha, best_ic, alpha_results)
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
                X_hist = Z_signed[:t]
                y_hist = trade_returns[:t]
                current_beta = _ridge_fit(X_hist, y_hist, alpha, penalty_diag=penalty_diag)
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
    ic_prior: bool = True,
    n_adaptive: bool = True,
    min_percentile: float = 0.0,
) -> tuple:
    """
    Produce expanding-window Ridge composite signal (V2).
    
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
      ic_prior: use IC-weighted penalty diagonal (V2)
      n_adaptive: scale alpha by N/10 (V2)
      min_percentile: expanding percentile gate for |Z| (0=disabled, V2)
      
    Returns:
      Z_composite: (T,) predicted signal
      info: dict with metadata (chosen alpha, coefficient snapshots, etc.)
    """
    T, N = Z_signed.shape
    
    if alphas is None:
        alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    
    # V2: Build IC-weighted penalty diagonal
    penalty_diag = None
    if ic_prior and pool is not None and len(pool) >= N:
        penalty_diag = _build_ic_penalty_diag(pool, N)
    
    # V2: N-adaptive alpha scaling
    n_scale = (N / 10.0) if n_adaptive else 1.0
    
    # Alpha selection
    alpha_results = []
    if alpha is None:
        # Scale candidate alphas by N-adaptive factor
        scaled_alphas = [a * n_scale for a in alphas]
        alpha, best_ic, alpha_results = select_best_alpha(
            Z_signed, trade_returns, scaled_alphas,
            burn_in=burn_in, train_end_idx=train_end_idx,
            fee_bps=fee_bps, clamp_nonneg=clamp_nonneg,
            penalty_diag=penalty_diag,
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
            X_hist = Z_signed[:t]
            y_hist = trade_returns[:t]
            current_beta = _ridge_fit(X_hist, y_hist, alpha, penalty_diag=penalty_diag)
            if clamp_nonneg:
                current_beta = np.maximum(0.0, current_beta)
            
            # Store snapshot every ~63 days (quarterly)
            if (t - effective_start) % 63 < refit_every:
                coef_history.append({"day": t, "beta": current_beta.copy()})
        
        Z_raw[t] = Z_signed[t] @ current_beta
    
    # Re-standardize to unit variance (expanding) so output is comparable to
    # Schemes 1-4 which produce signals with std ~ O(0.5-1.0).
    # Without this, Ridge predicts actual returns (~0.0003 scale) and the
    # threshold sweep in [0.2, 1.5] would never trigger.
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
    
    # V2: Optional percentile gate to control trade frequency
    if min_percentile > 0:
        # Expanding percentile gate: zero out weak signals
        abs_vals = np.abs(Z_composite)
        running_sorted = []
        for t in range(effective_start + 63, T):
            # Use expanding window percentile
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
        "ic_prior": ic_prior and penalty_diag is not None,
        "n_adaptive": n_adaptive,
        "n_scale": n_scale,
        "min_percentile": min_percentile,
    }
    
    return Z_composite, info
