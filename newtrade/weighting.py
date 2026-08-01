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

Group-Constrained Selection:
  When cluster_ids is provided (from ONC clustering), top-K selection enforces
  max_per_group features per cluster, ensuring diversity across feature groups.
"""

import numpy as np
from scipy.stats import rankdata


def _select_top_k_grouped(scores: np.ndarray, top_k: int, cluster_ids: np.ndarray,
                          max_per_group: int = 1) -> np.ndarray:
    """
    Greedy top-K selection with per-cluster cap.

    Args:
        scores: (N,) array of feature scores (higher = better)
        top_k: number of features to select
        cluster_ids: (N,) array of cluster assignments (int per feature)
        max_per_group: max features allowed per cluster (default 1)

    Returns:
        np.ndarray of selected feature indices
    """
    order = np.argsort(scores)[::-1]  # descending
    selected = []
    group_counts = {}
    for idx in order:
        g = int(cluster_ids[idx])
        if group_counts.get(g, 0) >= max_per_group:
            continue
        selected.append(idx)
        group_counts[g] = group_counts.get(g, 0) + 1
        if len(selected) >= top_k:
            break
    return np.array(selected, dtype=np.int64)


def _get_top_k_indices(scores: np.ndarray, top_k: int, cluster_ids: np.ndarray = None,
                       max_per_group: int = 1) -> np.ndarray:
    """
    Unified top-K selection: group-constrained if cluster_ids provided, else unconstrained.
    """
    if cluster_ids is not None and len(cluster_ids) == len(scores):
        return _select_top_k_grouped(scores, top_k, cluster_ids, max_per_group)
    else:
        return np.argsort(scores)[-top_k:]


def compute_ew(Z: np.ndarray, signs: np.ndarray, **kwargs) -> np.ndarray:
    """
    Equal Weight Scheme (EW):
    Each factor gets equal weight w_i = sign_i / N (or top_k features get equal weight 1/K).
    
    Args:
      - Z: Standardized feature matrix shape (T, N)
      - signs: Array of factor signs (+1 or -1) shape (N,)
      - top_k: Optional integer K to select top K factors by rolling IC or pool metadata.
      - cluster_ids: Optional (N,) array of ONC cluster assignments for group-constrained selection.
      - max_per_group: Max features per cluster (default 1).
      
    Returns:
      - Z_composite: Composite signal shape (T,)
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    top_k = kwargs.get("top_k", None)
    expanding_ic = kwargs.get("expanding_ic", None)
    pool = kwargs.get("pool", None)
    cluster_ids = kwargs.get("cluster_ids", None)
    max_per_group = kwargs.get("max_per_group", 1)
    
    if top_k is not None and 1 <= top_k < N:
        Z_signed = Z * signs
        if expanding_ic is not None and expanding_ic.shape == Z.shape:
            ic_ema_span = kwargs.get("ic_ema_span", 30)
            if ic_ema_span and ic_ema_span > 1:
                alpha = 2.0 / (ic_ema_span + 1.0)
                ic_mat = np.zeros_like(expanding_ic)
                ic_mat[0] = expanding_ic[0]
                for t_idx in range(1, T):
                    ic_mat[t_idx] = alpha * expanding_ic[t_idx] + (1.0 - alpha) * ic_mat[t_idx - 1]
            else:
                ic_mat = expanding_ic
            
            Z_composite = np.zeros(T, dtype=np.float64)
            for t in range(T):
                top_idx = _get_top_k_indices(ic_mat[t], top_k, cluster_ids, max_per_group)
                w_t = np.zeros(N, dtype=np.float64)
                w_t[top_idx] = 1.0 / float(len(top_idx))
                Z_composite[t] = Z_signed[t] @ w_t
            return Z_composite
        elif pool and len(pool) == N:
            deflated_ics = np.array([item.get("deflated_ic", 0.0) for item in pool], dtype=np.float64)
            top_idx = _get_top_k_indices(deflated_ics, top_k, cluster_ids, max_per_group)
            weights = np.zeros(N, dtype=np.float64)
            weights[top_idx] = 1.0 / float(len(top_idx))
            return Z_signed @ weights
    
    # Apply sign alignment
    Z_signed = Z * signs
    
    # Equal weighted average
    Z_composite = np.mean(Z_signed, axis=1)
    
    return Z_composite


def compute_icw(Z: np.ndarray, signs: np.ndarray, pool: list = None, n_train: int = 1700, k: float = 1.0, **kwargs) -> np.ndarray:
    """
    IC Weighted Scheme (ICW) with Empirical Bayes Shrinkage:
    w_i ∝ max(0, deflated_ic_i - SE_IC)^k
    SE_IC = 1 / sqrt(n_train)
    Supports optional top_k feature gating with group constraint.
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    top_k = kwargs.get("top_k", None)
    expanding_ic = kwargs.get("expanding_ic", None)
    cluster_ids = kwargs.get("cluster_ids", None)
    max_per_group = kwargs.get("max_per_group", 1)
    se_ic = 1.0 / np.sqrt(n_train)
    Z_signed = Z * signs

    if top_k is not None and 1 <= top_k < N and expanding_ic is not None and expanding_ic.shape == Z.shape:
        ic_ema_span = kwargs.get("ic_ema_span", 30)
        if ic_ema_span and ic_ema_span > 1:
            alpha = 2.0 / (ic_ema_span + 1.0)
            ic_mat = np.zeros_like(expanding_ic)
            ic_mat[0] = expanding_ic[0]
            for t_idx in range(1, T):
                ic_mat[t_idx] = alpha * expanding_ic[t_idx] + (1.0 - alpha) * ic_mat[t_idx - 1]
        else:
            ic_mat = expanding_ic
        
        Z_composite = np.zeros(T, dtype=np.float64)
        for t in range(T):
            top_idx = _get_top_k_indices(ic_mat[t], top_k, cluster_ids, max_per_group)
            w_t = np.zeros(N, dtype=np.float64)
            raw_w = np.maximum(0.0, ic_mat[t, top_idx] - se_ic) ** k
            w_sum = raw_w.sum()
            if w_sum < 1e-12:
                w_t[top_idx] = 1.0 / float(len(top_idx))
            else:
                w_t[top_idx] = raw_w / w_sum
            Z_composite[t] = Z_signed[t] @ w_t
        return Z_composite

    # Empirical Bayes shrinkage from pool
    if pool is not None and len(pool) == N:
        deflated_ics = np.array([item.get("deflated_ic", 0.0) for item in pool], dtype=np.float64)
    else:
        deflated_ics = np.ones(N, dtype=np.float64)
    
    weights = np.maximum(0.0, deflated_ics - se_ic) ** k
    
    if top_k is not None and 1 <= top_k < N:
        top_idx = _get_top_k_indices(deflated_ics, top_k, cluster_ids, max_per_group)
        mask = np.zeros(N, dtype=bool)
        mask[top_idx] = True
        weights[~mask] = 0.0

    # Normalize or fall back to equal weight
    w_sum = weights.sum()
    if w_sum < 1e-12:
        weights = np.ones(N, dtype=np.float64) / N
    else:
        weights = weights / w_sum
    
    Z_composite = Z_signed @ weights
    return Z_composite


def _compute_pool_scores(pool: list, score_weights: tuple = (0.20, 0.15, 0.65)) -> np.ndarray:
    """
    Compute B3-inspired composite quality scores from pool metadata.
    score_i = w_ic * rank_norm(deflated_ic) + w_ir * rank_norm(ic_ir) + w_mono * rank_norm(monotonicity)
    
    rank_norm(x_i) = rank(x_i) / N, maps to [1/N, 1.0].
    Uses only fields stored in admitted_pools.py.
    """
    N = len(pool)
    if N == 0:
        return np.empty(0, dtype=np.float64)
    
    w_ic, w_ir, w_mono = score_weights
    
    deflated_ics = np.array([item.get("deflated_ic", 0.0) for item in pool], dtype=np.float64)
    ic_irs = np.array([item.get("ic_ir", 0.0) for item in pool], dtype=np.float64)
    monos = np.array([item.get("monotonicity", 0.0) for item in pool], dtype=np.float64)
    
    # Rank-normalize each metric to [1/N, 1.0]
    rank_norm_ic = rankdata(deflated_ics, method="average") / N
    rank_norm_ir = rankdata(ic_irs, method="average") / N
    rank_norm_mono = rankdata(monos, method="average") / N
    
    scores = w_ic * rank_norm_ic + w_ir * rank_norm_ir + w_mono * rank_norm_mono
    return scores


def compute_score_w(Z: np.ndarray, signs: np.ndarray, pool: list = None, score_weights: tuple = (0.20, 0.15, 0.65), **kwargs) -> np.ndarray:
    """
    Score Weighted Scheme (B3-Inspired):
    w_i ∝ score_i = w_ic*rank_norm(deflated_ic) + w_ir*rank_norm(ic_ir) + w_mono*rank_norm(mono)
    Supports dynamic expanding score matrix and top_k feature filtering with group constraint.
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    if N == 1:
        return Z[:, 0] * signs[0]

    top_k = kwargs.get("top_k", None)
    expanding_ic = kwargs.get("expanding_ic", None)
    cluster_ids = kwargs.get("cluster_ids", None)
    max_per_group = kwargs.get("max_per_group", 1)
    if expanding_ic is not None and expanding_ic.shape == Z.shape:
        ic_ema_span = kwargs.get("ic_ema_span", 30)
        if ic_ema_span and ic_ema_span > 1:
            alpha = 2.0 / (ic_ema_span + 1.0)
            score_mat = np.zeros_like(expanding_ic)
            score_mat[0] = expanding_ic[0]
            for t_idx in range(1, T):
                score_mat[t_idx] = alpha * expanding_ic[t_idx] + (1.0 - alpha) * score_mat[t_idx - 1]
        else:
            score_mat = expanding_ic

        Z_signed = Z * signs
        Z_composite = np.zeros(T, dtype=np.float64)
        for t in range(T):
            s_t = score_mat[t]
            w_t = np.zeros(N, dtype=np.float64)
            if top_k is not None and 1 <= top_k < N:
                top_idx = _get_top_k_indices(s_t, top_k, cluster_ids, max_per_group)
                w_sub = s_t[top_idx]
                w_sum = w_sub.sum()
                if w_sum < 1e-12:
                    w_t[top_idx] = 1.0 / float(len(top_idx))
                else:
                    w_t[top_idx] = w_sub / w_sum
            else:
                w_sum = s_t.sum()
                if w_sum < 1e-12:
                    w_t = np.ones(N, dtype=np.float64) / N
                else:
                    w_t = s_t / w_sum
            Z_composite[t] = Z_signed[t] @ w_t
        return Z_composite
    
    scores = _compute_pool_scores(pool, score_weights=score_weights) if pool else np.ones(N, dtype=np.float64)
    weights = np.zeros(N, dtype=np.float64)
    if top_k is not None and 1 <= top_k < N:
        top_idx = _get_top_k_indices(scores, top_k, cluster_ids, max_per_group)
        sub_scores = scores[top_idx]
        w_sum = sub_scores.sum()
        if w_sum < 1e-12:
            weights[top_idx] = 1.0 / float(len(top_idx))
        else:
            weights[top_idx] = sub_scores / w_sum
    else:
        w_sum = scores.sum()
        if w_sum < 1e-12:
            weights = np.ones(N, dtype=np.float64) / N
        else:
            weights = scores / w_sum
    
    Z_signed = Z * signs
    Z_composite = Z_signed @ weights
    
    return Z_composite


def get_rank_weights(pool: list, w_min_ratio: float = 0.2, w_max_ratio: float = 1.8,
                     mapping_shape: str = "linear", power: float = 2.0, softmax_tau: float = 1.0,
                     top_k: int = None, score_weights: tuple = (0.20, 0.15, 0.65), **kwargs) -> np.ndarray:
    """
    Calculate Scheme 4 factor weights vector w_i for a pool.
    Supports group-constrained top-K selection via cluster_ids.
    """
    N = len(pool)
    if N == 0:
        return np.empty(0, dtype=np.float64)
    if N == 1:
        return np.ones(1, dtype=np.float64)

    cluster_ids = kwargs.get("cluster_ids", None)
    max_per_group = kwargs.get("max_per_group", 1)

    scores = _compute_pool_scores(pool, score_weights=score_weights)
    ranks = rankdata(scores, method="average")  # [1, N]
    
    w_min = w_min_ratio / N
    w_max = w_max_ratio / N

    shape_clean = mapping_shape.lower()

    if shape_clean == "top_k" or (top_k is not None and 1 <= top_k < N):
        k = top_k if top_k is not None and 1 <= top_k <= N else N
        top_k_indices = _get_top_k_indices(scores, k, cluster_ids, max_per_group)
        k_actual = len(top_k_indices)
        weights = np.zeros(N, dtype=np.float64)
        if k_actual == 1:
            weights[top_k_indices] = 1.0
        else:
            sub_ranks = rankdata(scores[top_k_indices], method="average")
            sub_w_min = w_min_ratio / k_actual
            sub_w_max = w_max_ratio / k_actual
            sub_w = sub_w_min + (sub_w_max - sub_w_min) * (sub_ranks - 1.0) / (k_actual - 1.0)
            weights[top_k_indices] = sub_w
    elif shape_clean == "power":
        norm_ranks = (ranks - 1.0) / (N - 1.0)  # [0, 1]
        p_ranks = norm_ranks ** power
        weights = w_min + (w_max - w_min) * p_ranks
    elif shape_clean == "softmax":
        norm_ranks = ranks / N
        exps = np.exp(softmax_tau * norm_ranks)
        weights = exps / exps.sum()
    else:
        # Default linear mapping
        weights = w_min + (w_max - w_min) * (ranks - 1.0) / (N - 1.0)

    # Normalize to sum to 1.0
    w_sum = weights.sum()
    if w_sum < 1e-12:
        weights = np.ones(N, dtype=np.float64) / N
    else:
        weights = weights / w_sum

    return weights


def compute_rank_w(Z: np.ndarray, signs: np.ndarray, pool: list = None,
                   w_min_ratio: float = 0.2, w_max_ratio: float = 1.8,
                   mapping_shape: str = "linear", power: float = 2.0, softmax_tau: float = 1.0,
                   top_k: int = None, score_weights: tuple = (0.20, 0.15, 0.65),
                   expanding_ic: np.ndarray = None, ic_ema_span: int = 10, weight_delta: float = None, **kwargs) -> np.ndarray:
    """
    Rank Bounded Weight Scheme (Scheme 4):
    Ranks factors by composite score, maps to weights using chosen mapping shape.
    Supports top_k feature selection both statically and dynamically with group constraint.
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    if N == 1:
        return Z[:, 0] * signs[0]
    
    cluster_ids = kwargs.get("cluster_ids", None)
    max_per_group = kwargs.get("max_per_group", 1)

    if expanding_ic is not None and expanding_ic.shape == Z.shape:
        if ic_ema_span and ic_ema_span > 1:
            alpha = 2.0 / (ic_ema_span + 1.0)
            ic_mat = np.zeros_like(expanding_ic)
            ic_mat[0] = expanding_ic[0]
            for t_idx in range(1, T):
                ic_mat[t_idx] = alpha * expanding_ic[t_idx] + (1.0 - alpha) * ic_mat[t_idx - 1]
        else:
            ic_mat = expanding_ic

        Z_signed = Z * signs
        Z_composite = np.zeros(T, dtype=np.float64)
        w_prev = np.ones(N, dtype=np.float64) / float(N)
        
        for t in range(T):
            ic_t = ic_mat[t]
            if top_k is not None and 1 <= top_k < N:
                top_idx = _get_top_k_indices(ic_t, top_k, cluster_ids, max_per_group)
                k_actual = len(top_idx)
                w_target = np.zeros(N, dtype=np.float64)
                if k_actual == 1:
                    w_target[top_idx] = 1.0
                else:
                    sub_ranks = rankdata(ic_t[top_idx], method="average")
                    sub_w_min = w_min_ratio / k_actual
                    sub_w_max = w_max_ratio / k_actual
                    w_target[top_idx] = sub_w_min + (sub_w_max - sub_w_min) * (sub_ranks - 1.0) / (k_actual - 1.0)
                    w_target = w_target / w_target.sum()
            else:
                w_min = w_min_ratio / N
                w_max = w_max_ratio / N
                ranks_t = rankdata(ic_t, method="average")
                w_target = w_min + (w_max - w_min) * (ranks_t - 1.0) / (N - 1.0)
                w_target = w_target / w_target.sum()
            
            if weight_delta is not None and 0.0 < weight_delta < 1.0:
                if t == 0:
                    weights_t = w_target
                else:
                    weights_t = w_prev + weight_delta * (w_target - w_prev)
                    weights_t = weights_t / weights_t.sum()
                w_prev = weights_t
            else:
                weights_t = w_target

            Z_composite[t] = Z_signed[t] @ weights_t
        return Z_composite

    weights = get_rank_weights(
        pool if pool else [],
        w_min_ratio=w_min_ratio,
        w_max_ratio=w_max_ratio,
        mapping_shape=mapping_shape,
        power=power,
        softmax_tau=softmax_tau,
        top_k=top_k,
        score_weights=score_weights,
        cluster_ids=cluster_ids,
        max_per_group=max_per_group,
    )
    
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


# =============================================================================
# Feature Selection Hysteresis (validated via A/B test 2026-08)
# =============================================================================

def adaptive_exit_rank(n_features: int, top_k: int = 10, hard_cap: int = 25) -> int:
    """
    Compute pool-adaptive exit_rank for hysteresis feature selection.
    Formula: min(top_k + (N - top_k) // 2, hard_cap)
    
    Ensures exit_rank is meaningful relative to pool size:
    - Small pools (N=22): exit_rank=16 (features exit at median of non-active ranks)
    - Large pools (N=193): exit_rank=25 (hard cap prevents over-stickiness)
    
    Validated: +26% Sharpe on 300ETF, +12% on 159915ETF, +4% on 500ETF.
    """
    formula = top_k + (n_features - top_k) // 2
    return min(formula, hard_cap)


def compute_icw_hysteresis(Z: np.ndarray, signs: np.ndarray, ic_mat: np.ndarray,
                           cluster_ids: np.ndarray = None, n_train: int = 1700,
                           top_k: int = 10, exit_rank: int = None,
                           max_per_group: int = 1) -> np.ndarray:
    """
    ICW with feature selection hysteresis (cluster-aware).
    
    Stabilizes Z_composite by reducing feature rotation:
    - Enter: feature ranks <= top_k AND cluster not occupied
    - Exit: feature ranks > exit_rank (wider threshold to leave)
    - Features in ranks (top_k, exit_rank] are 'on probation' - they stay
    
    Args:
      Z: Standardized feature matrix (T, N)
      signs: Factor signs (N,)
      ic_mat: EMA-smoothed IC matrix (T, N) for ranking
      cluster_ids: ONC cluster assignments (N,) or None
      n_train: Training sample count for SE_IC shrinkage
      top_k: Number of features to select (enter threshold)
      exit_rank: Rank below which features exit. If None, uses adaptive_exit_rank().
      max_per_group: Max features per cluster (default 1)
    
    Returns:
      Z_composite: (T,) composite signal
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    if exit_rank is None:
        exit_rank = adaptive_exit_rank(N, top_k)
    
    se_ic = 1.0 / np.sqrt(n_train)
    Z_signed = Z * signs
    Z_composite = np.zeros(T, dtype=np.float64)
    
    active_set = set()
    
    for t in range(T):
        scores = ic_mat[t]
        order = np.argsort(scores)[::-1]
        rank_of = np.zeros(N, dtype=np.int64)
        for rank_pos, idx in enumerate(order):
            rank_of[idx] = rank_pos + 1
        
        # 1. Exit: remove features that dropped below exit_rank
        to_remove = [f for f in active_set if rank_of[f] > exit_rank]
        for f in to_remove:
            active_set.discard(f)
        
        # 2. Enter: add features ranking <= top_k (cluster-constrained)
        occupied_clusters = {}
        if cluster_ids is not None:
            for f in active_set:
                occupied_clusters[int(cluster_ids[f])] = f
        
        for idx in order:
            if len(active_set) >= top_k:
                break
            idx_int = int(idx)
            if idx_int in active_set:
                continue
            if rank_of[idx_int] > top_k:
                break
            if cluster_ids is not None:
                c = int(cluster_ids[idx_int])
                if c in occupied_clusters:
                    continue
                occupied_clusters[c] = idx_int
            active_set.add(idx_int)
        
        # 3. ICW shrinkage weights for active set
        if not active_set:
            continue
        active_idx = np.array(sorted(active_set), dtype=np.int64)
        w_t = np.zeros(N, dtype=np.float64)
        raw_w = np.maximum(0.0, scores[active_idx] - se_ic)
        w_sum = raw_w.sum()
        if w_sum < 1e-12:
            w_t[active_idx] = 1.0 / float(len(active_idx))
        else:
            w_t[active_idx] = raw_w / w_sum
        Z_composite[t] = Z_signed[t] @ w_t
    
    return Z_composite


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
