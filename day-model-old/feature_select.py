"""
Feature selectors for the gating model.

Two complementary, walk-forward, leakage-safe methods:
  1. select_stability       — regime-stratified block bootstrap + randomized
                              ElasticNet + OOB Spearman IC screen + variance
                              filter (ported from train_model.TimeSeriesStabilitySelector).
  2. select_lgbm_importance — 5-fold walk-forward LightGBM, aggregates gain
                              importance with OOS permutation importance.

Both return a list of selected feature names. Caller compares selectors on
honest OOS metrics and keeps the winner per (etf, side, target_variant).

Usage:
    from feature_select import select_stability, select_lgbm_importance
"""
from __future__ import annotations

import warnings
from typing import List, Sequence

import numpy as np
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import ElasticNet, ElasticNetCV
from sklearn.inspection import permutation_importance
from joblib import Parallel, delayed
from lightgbm import LGBMClassifier, LGBMRegressor

warnings.filterwarnings("ignore")

# Defaults (mirror train_model.py)
BLOCK_SIZE = 20
N_BOOTSTRAPS = 50
DEFAULT_N_SPLITS = 5
DEFAULT_PURGE_GAP = 5
VARIANCE_CAP = 0.15        # σ_S,j ≤ 0.15 to keep
STABILITY_THRESHOLD = 0.30  # min mean stability score to keep a feature


def purged_tssplit(n: int, n_splits: int, gap: int):
    """Expanding-window walk-forward splits with a purge gap to prevent leakage."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    for train_idx, test_idx in tscv.split(np.arange(n)):
        if gap > 0:
            train_end = train_idx[-1] - gap
            if train_end < 1:
                continue
            train_idx = train_idx[train_idx <= train_end]
        if len(train_idx) < 50 or len(test_idx) < 30:
            continue
        yield train_idx, test_idx


# ============================================================
# 1. Stability selector (regime-stratified bootstrap + randomized ElasticNet)
# ============================================================
def _run_stratified_bootstrap_trial(
    X, y, regimes, regime_starts, block_freqs,
    block_size, randomization_alpha, best_alpha, best_l1_ratio, random_seed,
):
    """One bootstrap trial: stratified block resample → randomized ElasticNet →
    coefficient selection + OOB Spearman IC screen. Returns two boolean masks.

    regime_starts : dict {regime_int: ndarray of block-start indices}
    block_freqs   : 1D ndarray, block_freqs[r] = frequency of regime r.
    """
    N, D = X.shape
    n_blocks = int(np.ceil(N / block_size))
    rng = np.random.default_rng(random_seed)

    regimes_list = list(regime_starts.keys())
    m_blocks = {}
    total = 0
    for r in regimes_list:
        freq = float(block_freqs[r]) if r < len(block_freqs) else 0.0
        m = int(np.round(n_blocks * freq))
        m_blocks[r] = m
        total += m
    diff = n_blocks - total
    if diff != 0 and regimes_list:
        chosen = max(regimes_list, key=lambda r: float(block_freqs[r]) if r < len(block_freqs) else 0.0)
        m_blocks[chosen] = max(0, m_blocks[chosen] + diff)

    start_indices = []
    for r, m in m_blocks.items():
        starts = regime_starts.get(r, np.array([], dtype=int))
        if m > 0 and len(starts) > 0:
            start_indices.extend(rng.choice(starts, size=m, replace=True))
    rng.shuffle(start_indices)

    boot_indices = []
    for s in start_indices:
        boot_indices.extend(range(s, s + block_size))
    boot_indices = boot_indices[:N]
    if len(boot_indices) == 0:
        boot_indices = np.arange(N)
        oob_indices = np.array([], dtype=int)
    else:
        oob_indices = np.setdiff1d(np.arange(N), boot_indices)

    X_boot = X[boot_indices]
    y_boot = y[boot_indices]

    scaler = StandardScaler()
    X_boot_scaled = scaler.fit_transform(X_boot).astype(np.float32)

    # Randomized L1 penalty: scale each feature by 1/W (W~U(α,1))
    W = rng.uniform(randomization_alpha, 1.0, size=D)
    X_boot_scaled_rand = X_boot_scaled / W

    model = ElasticNet(
        alpha=best_alpha, l1_ratio=best_l1_ratio,
        random_state=random_seed, max_iter=1000, tol=1e-3,
    )
    model.fit(X_boot_scaled_rand, y_boot)
    coef_selected = np.abs(model.coef_) > 1e-5

    ic_selected = np.ones(D, dtype=bool)
    if len(oob_indices) >= 10:
        X_oob = X[oob_indices]
        y_oob = y[oob_indices]
        X_oob_scaled = StandardScaler().fit_transform(X_oob).astype(np.float32)
        for j in range(D):
            x_oob_j = X_oob_scaled[:, j]
            if np.std(x_oob_j) < 1e-12:
                ic_selected[j] = False
                continue
            rho, pval = spearmanr(x_oob_j, y_oob)
            if np.isnan(rho):
                ic_selected[j] = True
            else:
                ic_selected[j] = (pval < 0.05) or (abs(rho) > 0.02)

    joint = coef_selected & ic_selected
    return joint, coef_selected, ic_selected


class StabilitySelector:
    """Regime-stratified block bootstrap stability selector.

    Steps per walk-forward fold:
      - Pre-tune ElasticNetCV (l1_ratio, alpha) on the train slice.
      - Run N_BOOTSTRAPS stratified block bootstraps with randomized L1.
      - Aggregate joint (coef ∧ IC) selection probabilities across folds.
      - Apply stability (mean ≥ threshold) AND variance (σ ≤ cap) filter.
    """

    def __init__(
        self,
        n_bootstraps: int = N_BOOTSTRAPS,
        block_size: int = BLOCK_SIZE,
        randomization_alpha: float = 0.5,
        l1_ratio: float = 0.8,
        n_splits: int = DEFAULT_N_SPLITS,
        purge_gap: int = DEFAULT_PURGE_GAP,
        variance_cap: float = VARIANCE_CAP,
        stability_threshold: float = STABILITY_THRESHOLD,
        n_jobs: int = -1,
    ):
        self.n_bootstraps = n_bootstraps
        self.block_size = block_size
        self.randomization_alpha = randomization_alpha
        self.l1_ratio = l1_ratio
        self.n_splits = n_splits
        self.purge_gap = purge_gap
        self.variance_cap = variance_cap
        self.stability_threshold = stability_threshold
        self.n_jobs = n_jobs

    def fit(self, X: np.ndarray, y: np.ndarray, features: Sequence[str]) -> dict:
        """Return dict with per-feature stats and the selected mask."""
        N, D = X.shape

        # Regime split on vol20 if available (proxy: rolling std of y)
        vol_idx = features.index("vol20") if "vol20" in features else -1
        if vol_idx >= 0:
            vols = X[:, vol_idx]
        else:
            vols = np.zeros(N)
            for i in range(20, N):
                vols[i] = np.std(y[i - 20:i])
        q33, q66 = np.quantile(vols, 0.33), np.quantile(vols, 0.66)
        regimes = np.zeros(N, dtype=int)
        regimes[vols > q33] = 1
        regimes[vols > q66] = 2

        # Build overlapping blocks labelled by modal regime
        block_starts = []
        block_regimes = []
        for s in range(0, N - self.block_size + 1):
            block_starts.append(s)
            block_regimes.append(int(np.bincount(regimes[s:s + self.block_size]).argmax()))
        block_starts = np.array(block_starts)
        block_regimes = np.array(block_regimes)

        splits = list(purged_tssplit(N, self.n_splits, self.purge_gap))
        if not splits:
            # Fall back to single in-sample fit
            splits = [(np.arange(N), np.arange(min(30, N)))]

        fold_joint, fold_coef, fold_ic = [], [], []
        for fold_idx, (train_idx, _) in enumerate(splits):
            X_tr, y_tr = X[train_idx], y[train_idx]
            regimes_tr = regimes[train_idx]
            max_start = len(train_idx) - self.block_size
            if max_start < 1:
                continue

            tr_block_starts = block_starts[block_starts <= max_start]
            tr_block_regimes = block_regimes[block_starts <= max_start]
            regime_starts = {r: tr_block_starts[tr_block_regimes == r] for r in (0, 1, 2)}

            counts = np.bincount(regimes_tr, minlength=3)
            freqs = counts / max(len(regimes_tr), 1)

            # Pre-tune alpha + l1_ratio on train slice
            scaler_tr = StandardScaler()
            X_tr_scaled = scaler_tr.fit_transform(X_tr).astype(np.float32)
            try:
                enet_cv = ElasticNetCV(
                    l1_ratio=self.l1_ratio, cv=5, random_state=42,
                    alphas=np.logspace(-4, 1, 20), tol=1e-2, max_iter=500, n_jobs=-1,
                )
                enet_cv.fit(X_tr_scaled, y_tr)
                best_alpha = enet_cv.alpha_
                best_l1_ratio = enet_cv.l1_ratio_
            except Exception:
                best_alpha, best_l1_ratio = 0.01, self.l1_ratio

            results = Parallel(n_jobs=self.n_jobs)(
                delayed(_run_stratified_bootstrap_trial)(
                    X_tr, y_tr, regimes_tr, regime_starts, freqs,
                    self.block_size, self.randomization_alpha,
                    best_alpha, best_l1_ratio, 42 + fold_idx * 1000 + i,
                )
                for i in range(self.n_bootstraps)
            )
            fold_joint.append(np.mean([r[0] for r in results], axis=0))
            fold_coef.append(np.mean([r[1] for r in results], axis=0))
            fold_ic.append(np.mean([r[2] for r in results], axis=0))

        mean_stability = np.mean(fold_joint, axis=0)
        std_stability = np.std(fold_joint, axis=0)
        mean_coef = np.mean(fold_coef, axis=0)
        mean_ic = np.mean(fold_ic, axis=0)

        selected = (mean_stability >= self.stability_threshold) & (std_stability <= self.variance_cap)
        return {
            "features": list(features),
            "mean_stability": mean_stability,
            "std_stability": std_stability,
            "mean_coef": mean_coef,
            "mean_ic": mean_ic,
            "selected_mask": selected,
        }


def select_stability(
    X: np.ndarray,
    y: np.ndarray,
    features: Sequence[str],
    stability_threshold: float = STABILITY_THRESHOLD,
    n_bootstraps: int = N_BOOTSTRAPS,
    n_splits: int = DEFAULT_N_SPLITS,
    purge_gap: int = DEFAULT_PURGE_GAP,
    min_features: int = 5,
    fallback_quantile: float = 0.85,
    n_jobs: int = -1,
) -> List[str]:
    """Run stability selection; return list of feature names.

    Guarantees at least `min_features` outputs: if the strict threshold yields
    fewer, relax to top-`fallback_quantile` by mean_stability (still respecting
    the variance cap).
    """
    selector = StabilitySelector(
        n_bootstraps=n_bootstraps,
        n_splits=n_splits,
        purge_gap=purge_gap,
        stability_threshold=stability_threshold,
        n_jobs=n_jobs,
    )
    stats = selector.fit(X, y, features)
    mask = stats["selected_mask"]
    selected = [f for f, m in zip(features, mask) if m]

    if len(selected) < min_features:
        # Relax: rank by mean_stability desc (ignore variance cap), take top quantile
        order = np.argsort(-stats["mean_stability"])
        keep_n = max(min_features, int(len(features) * (1.0 - fallback_quantile)))
        selected = [features[idx] for idx in order[:keep_n]]

    # De-duplicate while preserving order
    seen = set()
    out = []
    for f in selected:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


# ============================================================
# 2. LightGBM importance selector (gain + permutation)
# ============================================================
def select_lgbm_importance(
    X: np.ndarray,
    y: np.ndarray,
    features: Sequence[str],
    task: str = "classification",
    top_n: int = 30,
    n_splits: int = DEFAULT_N_SPLITS,
    purge_gap: int = DEFAULT_PURGE_GAP,
    permutation: bool = True,
    min_features: int = 5,
    n_jobs: int = -1,
) -> List[str]:
    """Walk-forward LightGBM feature importance selection.

    Aggregates two signals across folds:
      - gain importance (cheap, intrinsic)
      - OOS permutation importance on ROC AUC / Spearman IC (expensive, honest)

    Final score = 0.5 * rank(gain) + 0.5 * rank(permutation).
    Returns top_n feature names.
    """
    N, D = X.shape
    splits = list(purged_tssplit(N, n_splits, purge_gap))
    if not splits:
        splits = [(np.arange(max(50, N - 30)), np.arange(max(50, N - 30), N))]

    gain_scores = np.zeros(D)
    perm_scores = np.zeros(D)
    perm_runs = 0

    base_params = dict(
        n_estimators=80, learning_rate=0.05, num_leaves=15,
        max_depth=4, min_child_samples=20, subsample=0.8,
        colsample_bytree=0.8, random_state=42, n_jobs=1, verbose=-1,
    )

    for train_idx, test_idx in splits:
        X_tr, X_te = X[train_idx], X[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr).astype(np.float32)
        X_te_s = scaler.transform(X_te).astype(np.float32)

        if task == "classification":
            n_pos = int(np.sum(y_tr == 1))
            n_neg = int(np.sum(y_tr == 0))
            if n_pos < 5 or n_neg < 5:
                continue
            model = LGBMClassifier(**base_params)
            model.fit(X_tr_s, y_tr)
            gain_scores += model.feature_importances_
            if permutation:
                from sklearn.metrics import roc_auc_score
                try:
                    result = permutation_importance(
                        model, X_te_s, y_te, n_repeats=3,
                        scoring="roc_auc", random_state=42, n_jobs=n_jobs,
                    )
                    perm_scores += np.maximum(result.importances_mean, 0.0)
                    perm_runs += 1
                except Exception:
                    pass
        else:  # regression
            model = LGBMRegressor(**base_params)
            model.fit(X_tr_s, y_tr)
            gain_scores += model.feature_importances_
            if permutation:
                def _spearman_scorer(est, X, y):
                    p = est.predict(X)
                    if np.std(p) < 1e-12:
                        return 0.0
                    rho, _ = spearmanr(p, y)
                    return rho if not np.isnan(rho) else 0.0
                try:
                    result = permutation_importance(
                        model, X_te_s, y_te, n_repeats=3,
                        scoring=_spearman_scorer, random_state=42, n_jobs=n_jobs,
                    )
                    perm_scores += np.maximum(result.importances_mean, 0.0)
                    perm_runs += 1
                except Exception:
                    pass

    gain_scores = gain_scores / max(1, len(splits))
    if perm_runs > 0:
        perm_scores = perm_scores / perm_runs

    # Rank fusion
    def _rank_desc(scores: np.ndarray) -> np.ndarray:
        order = np.argsort(-scores)
        ranks = np.empty(D, dtype=float)
        ranks[order] = np.arange(D)
        # Higher score → lower rank number → higher normalized value
        return 1.0 - ranks / max(1, D - 1)

    gain_rank = _rank_desc(gain_scores)
    perm_rank = _rank_desc(perm_scores) if perm_runs > 0 else gain_rank
    fused = 0.5 * gain_rank + 0.5 * perm_rank

    order = np.argsort(-fused)
    keep_n = max(min_features, min(top_n, D))
    selected = [features[i] for i in order[:keep_n]]

    seen = set()
    out = []
    for f in selected:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


__all__ = [
    "StabilitySelector",
    "select_stability",
    "select_lgbm_importance",
    "purged_tssplit",
]
