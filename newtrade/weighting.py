#!/usr/bin/env python3
"""
Factor Weighting Module for NewTrade framework.
Implements factor aggregation schemes to combine standardized features Z into a composite signal.

Implemented:
  - Equal Weight (EW)
  - IC Weight (ICW) with Empirical Bayes shrinkage
  - Score Weighted (B3-inspired, pool-metadata-only)
  - Rank Bounded Weight

Placeholder / Empty for future implementation:
  - Simple Linear GLM
"""

import numpy as np
from scipy.stats import rankdata


def compute_ew(Z: np.ndarray, signs: np.ndarray, **kwargs) -> np.ndarray:
    """
    Equal Weight Scheme (EW):
    Each factor gets equal weight w_i = sign_i / N.
    Z_composite = sum(w_i * z_i) = mean(sign_i * z_i).
    
    Args:
      - Z: Standardized feature matrix shape (T, N)
      - signs: Array of factor signs (+1 or -1) shape (N,)
      
    Returns:
      - Z_composite: Composite signal shape (T,)
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    # Apply sign alignment
    Z_signed = Z * signs
    
    # Equal weighted average
    Z_composite = np.mean(Z_signed, axis=1)
    
    return Z_composite


def compute_icw(Z: np.ndarray, signs: np.ndarray, pool: list, n_train: int = 1700, k: float = 1.0, **kwargs) -> np.ndarray:
    """
    IC Weighted Scheme (ICW) with Empirical Bayes Shrinkage:
    w_i ∝ max(0, deflated_ic_i - SE_IC)^k
    SE_IC = 1 / sqrt(n_train)
    
    Penalizes features with marginal IC estimates that are likely noise.
    Falls back to equal weight if all weights shrink to zero.
    
    Args:
      - Z: Standardized feature matrix shape (T, N)
      - signs: Array of factor signs (+1 or -1) shape (N,)
      - pool: List of pool item dicts with 'deflated_ic' field
      - n_train: Training sample size for SE_IC calculation (default ~7 years)
      - k: Exponent tilt toward higher-IC features (default 1.0)
      
    Returns:
      - Z_composite: Composite signal shape (T,)
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    # Empirical Bayes shrinkage: subtract SE(IC) ≈ 1/√n
    se_ic = 1.0 / np.sqrt(n_train)
    deflated_ics = np.array([item.get("deflated_ic", 0.0) for item in pool], dtype=np.float64)
    
    # Shrink and apply exponent
    weights = np.maximum(0.0, deflated_ics - se_ic) ** k
    
    # Normalize or fall back to equal weight
    w_sum = weights.sum()
    if w_sum < 1e-12:
        weights = np.ones(N, dtype=np.float64) / N
    else:
        weights = weights / w_sum
    
    # Apply sign alignment and weighted sum
    Z_signed = Z * signs
    Z_composite = Z_signed @ weights
    
    return Z_composite


def _compute_pool_scores(pool: list) -> np.ndarray:
    """
    Compute B3-inspired composite quality scores from pool metadata.
    score_i = 0.40 * rank_norm(deflated_ic) + 0.35 * rank_norm(ic_ir) + 0.25 * rank_norm(monotonicity)
    
    rank_norm(x_i) = rank(x_i) / N, maps to [1/N, 1.0].
    Uses only fields stored in admitted_pools.py.
    """
    N = len(pool)
    if N == 0:
        return np.empty(0, dtype=np.float64)
    
    deflated_ics = np.array([item.get("deflated_ic", 0.0) for item in pool], dtype=np.float64)
    ic_irs = np.array([item.get("ic_ir", 0.0) for item in pool], dtype=np.float64)
    monos = np.array([item.get("monotonicity", 0.0) for item in pool], dtype=np.float64)
    
    # Rank-normalize each metric to [1/N, 1.0]
    rank_norm_ic = rankdata(deflated_ics, method="average") / N
    rank_norm_ir = rankdata(ic_irs, method="average") / N
    rank_norm_mono = rankdata(monos, method="average") / N
    
    scores = 0.40 * rank_norm_ic + 0.35 * rank_norm_ir + 0.25 * rank_norm_mono
    return scores


def compute_score_w(Z: np.ndarray, signs: np.ndarray, pool: list, **kwargs) -> np.ndarray:
    """
    Score Weighted Scheme (B3-Inspired):
    w_i ∝ score_i = 0.40*rank_norm(deflated_ic) + 0.35*rank_norm(ic_ir) + 0.25*rank_norm(mono)
    
    Multi-dimensional quality weighting using only pool metadata.
    
    Args:
      - Z: Standardized feature matrix shape (T, N)
      - signs: Array of factor signs (+1 or -1) shape (N,)
      - pool: List of pool item dicts
      
    Returns:
      - Z_composite: Composite signal shape (T,)
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    scores = _compute_pool_scores(pool)
    
    # Normalize weights
    w_sum = scores.sum()
    if w_sum < 1e-12:
        weights = np.ones(N, dtype=np.float64) / N
    else:
        weights = scores / w_sum
    
    # Apply sign alignment and weighted sum
    Z_signed = Z * signs
    Z_composite = Z_signed @ weights
    
    return Z_composite


def compute_rank_w(Z: np.ndarray, signs: np.ndarray, pool: list, w_min_ratio: float = 0.5, w_max_ratio: float = 1.5, **kwargs) -> np.ndarray:
    """
    Rank Bounded Weight Scheme:
    Ranks factors by composite score, maps linearly to [w_min, w_max].
    w_min = w_min_ratio / N, w_max = w_max_ratio / N.
    
    Prevents single factor dominance while tilting toward higher-quality factors.
    Default: top factor gets 3× weight of bottom factor (1.5/0.5).
    
    Args:
      - Z: Standardized feature matrix shape (T, N)
      - signs: Array of factor signs (+1 or -1) shape (N,)
      - pool: List of pool item dicts
      - w_min_ratio: Minimum weight as ratio of 1/N (default 0.5)
      - w_max_ratio: Maximum weight as ratio of 1/N (default 1.5)
      
    Returns:
      - Z_composite: Composite signal shape (T,)
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    if N == 1:
        # Single factor: just use sign-aligned z-score
        return Z[:, 0] * signs[0]
    
    scores = _compute_pool_scores(pool)
    
    # Rank factors by score (1 = worst, N = best)
    ranks = rankdata(scores, method="average")  # [1, N]
    
    # Linear mapping: rank 1 -> w_min, rank N -> w_max
    w_min = w_min_ratio / N
    w_max = w_max_ratio / N
    weights = w_min + (w_max - w_min) * (ranks - 1.0) / (N - 1.0)
    
    # Normalize to sum to 1
    weights = weights / weights.sum()
    
    # Apply sign alignment and weighted sum
    Z_signed = Z * signs
    Z_composite = Z_signed @ weights
    
    return Z_composite


def compute_glm_w(Z: np.ndarray, y: np.ndarray, **kwargs) -> np.ndarray:
    """
    Simple Linear GLM Scheme:
    Fits expanding L2 Ridge regression model on Z to predict y.
    """
    raise NotImplementedError("GLM Ridge scheme is not implemented yet.")


WEIGHTING_SCHEMES = {
    "ew": compute_ew,
    "icw": compute_icw,
    "score": compute_score_w,
    "rank": compute_rank_w,
    "glm": compute_glm_w,
}


def get_weighting_scheme(scheme_name: str):
    """Factory getter for weighting functions."""
    scheme_lower = scheme_name.lower()
    if scheme_lower not in WEIGHTING_SCHEMES:
        raise ValueError(f"Unknown weighting scheme '{scheme_name}'. Available: {list(WEIGHTING_SCHEMES.keys())}")
    return WEIGHTING_SCHEMES[scheme_lower]
