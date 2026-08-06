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
from numba import njit


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


def compute_icir(Z: np.ndarray, signs: np.ndarray, pool: list = None, **kwargs) -> np.ndarray:
    """
    ICIR Weighted Scheme:
    w_i ∝ max(0, ICIR_i) where ICIR = rolling_mean(IC) / (rolling_std(IC) + 1e-4)
    Penalizes unstable factors directly.
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)
    
    top_k = kwargs.get("top_k", None)
    expanding_ic = kwargs.get("expanding_ic", None)
    cluster_ids = kwargs.get("cluster_ids", None)
    max_per_group = kwargs.get("max_per_group", 1)
    Z_signed = Z * signs

    if top_k is not None and 1 <= top_k < N and expanding_ic is not None and expanding_ic.shape == Z.shape:
        # Vectorized rolling ICIR calculation
        import pandas as pd
        ic_df = pd.DataFrame(expanding_ic)
        ic_mean = ic_df.rolling(window=480, min_periods=10).mean().shift(1).fillna(0.0).values
        ic_std = ic_df.rolling(window=480, min_periods=10).std().shift(1).fillna(1.0).values + 1e-4
        icir_mat = ic_mean / ic_std
        
        Z_composite = np.zeros(T, dtype=np.float64)
        for t in range(T):
            top_idx = _get_top_k_indices(icir_mat[t], top_k, cluster_ids, max_per_group)
            raw_w = np.maximum(0.0, icir_mat[t, top_idx])
            w_sum = raw_w.sum()
            w_t = np.zeros(N, dtype=np.float64)
            if w_sum < 1e-12:
                w_t[top_idx] = 1.0 / float(len(top_idx))
            else:
                w_t[top_idx] = raw_w / w_sum
            Z_composite[t] = Z_signed[t] @ w_t
        return Z_composite

    return compute_ew(Z, signs, pool=pool, **kwargs)


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

def adaptive_exit_rank(n_features: int, top_k: int = 10, hard_cap: int = 20) -> int:
    """
    Compute pool-adaptive exit_rank for hysteresis feature selection.
    Formula: min(top_k + (N - top_k) // 2, hard_cap)
    
    Ensures exit_rank is meaningful relative to pool size:
    - Small pools (N=22): exit_rank=16 (features exit at median of non-active ranks)
    - Large pools (N=377): exit_rank=20 (hard cap prevents over-stickiness past rank 20)
    
    Validated: Top-10 / ER=20 optimal across 300ETF, 500ETF, and 159915ETF.
    """
    formula = top_k + (n_features - top_k) // 2
    return min(formula, hard_cap)


def adaptive_exit_rank_clusters(n_clusters: int, top_k: int = 10, hard_cap: int = 25) -> int:
    """
    Cluster-count adaptive exit_rank: ER = min(top_k + max(5, n_clusters // 2), hard_cap).

    Rationale: with the max-1-per-cluster constraint the active set spans distinct
    ONC clusters, so the probation band should scale with the number of clusters
    (the effective selection depth), not the raw feature count.
    """
    band = max(5, n_clusters // 2)
    return min(top_k + band, hard_cap)


@njit(fastmath=True)
def _ema_smooth_matrix_numba(ic_mat: np.ndarray, span: int) -> np.ndarray:
    T, N = ic_mat.shape
    alpha = 2.0 / (span + 1.0)
    out = np.empty((T, N), dtype=np.float64)
    out[0] = ic_mat[0]
    for t in range(1, T):
        out[t] = alpha * ic_mat[t] + (1.0 - alpha) * out[t - 1]
    return out


@njit(fastmath=True)
def _compute_icw_hysteresis_numba(Z_signed: np.ndarray, ic_mat: np.ndarray, weight_mat: np.ndarray,
                                  cluster_ids: np.ndarray, top_k: int, exit_rank: int, se_ic: float) -> np.ndarray:
    T, N = Z_signed.shape
    Z_composite = np.zeros(T, dtype=np.float64)
    active_mask = np.zeros(N, dtype=np.bool_)
    use_weight_mat = (weight_mat.shape[0] == T and weight_mat.shape[1] == N)
    has_clusters = (cluster_ids.size == N)

    for t in range(T):
        scores = ic_mat[t]
        order = np.argsort(scores)[::-1]
        rank_of = np.empty(N, dtype=np.int64)
        for r_pos in range(N):
            rank_of[order[r_pos]] = r_pos + 1

        # 1. Exit: remove features that dropped below exit_rank
        for f in range(N):
            if active_mask[f] and rank_of[f] > exit_rank:
                active_mask[f] = False

        # 2. Enter: add features ranking <= top_k (cluster-constrained)
        n_active = 0
        for f in range(N):
            if active_mask[f]:
                n_active += 1

        for idx in order:
            if n_active >= top_k:
                break
            if active_mask[idx]:
                continue
            if rank_of[idx] > top_k:
                break
            if has_clusters:
                c = cluster_ids[idx]
                cluster_taken = False
                for f in range(N):
                    if active_mask[f] and cluster_ids[f] == c:
                        cluster_taken = True
                        break
                if cluster_taken:
                    continue
            active_mask[idx] = True
            n_active += 1

        # 3. ICW shrinkage weights for active set
        if n_active > 0:
            w_sum = 0.0
            sig_val = 0.0
            w_src = weight_mat[t] if use_weight_mat else scores

            for f in range(N):
                if active_mask[f]:
                    v = w_src[f] - se_ic
                    if v > 0.0:
                        w_sum += v

            if w_sum > 1e-12:
                for f in range(N):
                    if active_mask[f]:
                        v = w_src[f] - se_ic
                        if v > 0.0:
                            sig_val += Z_signed[t, f] * (v / w_sum)
            else:
                eq_w = 1.0 / float(n_active)
                for f in range(N):
                    if active_mask[f]:
                        sig_val += Z_signed[t, f] * eq_w
            Z_composite[t] = sig_val

    return Z_composite


def compute_icw_hysteresis(Z: np.ndarray, signs: np.ndarray, ic_mat: np.ndarray,
                           cluster_ids: np.ndarray = None, n_train: int = 1700,
                           top_k: int = 10, exit_rank: int = None,
                           max_per_group: int = 1, weight_mat: np.ndarray = None) -> np.ndarray:
    """
    Hysteresis-based Top-K selection with Empirical Bayes ICW shrinkage weights.
    Accelerated via Numba JIT kernel _compute_icw_hysteresis_numba.
    """
    T, N = Z.shape
    if N == 0:
        return np.zeros(T, dtype=np.float64)

    if exit_rank is None:
        exit_rank = adaptive_exit_rank(N, top_k)

    se_ic = 1.0 / np.sqrt(n_train)
    Z_signed = Z * signs
    c_arr = cluster_ids if cluster_ids is not None else np.empty(0, dtype=np.int64)
    w_mat = weight_mat if weight_mat is not None else np.empty((0, 0), dtype=np.float64)

    return _compute_icw_hysteresis_numba(Z_signed, ic_mat, w_mat, c_arr, top_k, exit_rank, se_ic)


WEIGHTING_SCHEMES = {
    "ew": compute_ew,
    "icw": compute_icw,
    "icir": compute_icir,
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
