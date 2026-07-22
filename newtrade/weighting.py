#!/usr/bin/env python3
"""
Factor Weighting Module for NewTrade framework.
Implements factor aggregation schemes to combine standardized features Z into a composite signal.

Currently Implemented:
  - Equal Weight (EW)

Placeholder / Empty for future implementation:
  - IC Weight (ICW)
  - Score Weighted
  - Rank Bounded Weight
  - Simple Linear GLM
"""

import numpy as np


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


def compute_icw(Z: np.ndarray, signs: np.ndarray, pool: list, **kwargs) -> np.ndarray:
    """
    IC Weighted Scheme (ICW):
    Weights factors proportional to max(0, Deflated_IC)^k.
    """
    raise NotImplementedError("IC Weighting scheme is not implemented yet.")


def compute_score_w(Z: np.ndarray, signs: np.ndarray, pool: list, **kwargs) -> np.ndarray:
    """
    Score Weighted Scheme:
    Weights factors by composite quality score (IC, IR, Monotonicity).
    """
    raise NotImplementedError("Score Weighted scheme is not implemented yet.")


def compute_rank_w(Z: np.ndarray, signs: np.ndarray, pool: list, **kwargs) -> np.ndarray:
    """
    Rank Bounded Weight Scheme:
    Ranks factors by quality and maps weights into [0.10, 0.20].
    """
    raise NotImplementedError("Rank Bounded Weight scheme is not implemented yet.")


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
