#!/usr/bin/env python3
"""
Generate candidate feature combinations — aggressive mining edition.

2-way ops (11): min, max, diff, ratio, ifelse, mean, product, abs_diff,
                rank_min, rank_max, clamp_diff
3-way ops (5):  tri_mean, tri_min, tri_max, tri_median, tri_ifelse

Core pruning rules:
1. Top K absolute train IC pre-filter.
2. Correlation sweet-spot (2-way: [0.15, 0.85], 3-way: [0.10, 0.90]).
3. Domain-specific combination rules.
4. Forbidden-directions memory checking.
5. Mining log dedup — never re-emit previously generated candidates.

Usage:
    python generate_combos.py                        # all ETFs x all sides (default)
    python generate_combos.py -e 300ETF -s long      # single ETF, single side
    python generate_combos.py -e all -s short        # all ETFs, short only
    python generate_combos.py -e 500ETF -s all       # one ETF, all 3 sides
    python generate_combos.py --top-k 40 --top-k-3 20
    python generate_combos.py --two-only             # skip 3-way
    python generate_combos.py --early                # early window dataset
    python generate_combos.py --no-dedup             # regenerate everything
"""

import os
import sys
import json
import hashlib
import argparse
import itertools
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata

# Paths
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.append(str(REPO_ROOT / "day-model"))

from build_features import FEATURES
sys.path.append(str(HERE.parent))
from admitted_pools import get_admitted_pool

ALL_ETFS = ["50ETF", "300ETF", "500ETF", "588000ETF", "159915ETF"]
ALL_SIDES = ["long", "short", "single"]

# ─── Constants ────────────────────────────────────────────────────────────────

REGIME_SET = frozenset([
    "vol20", "vol10", "vol60", "vol_pk20", "vol_gk20", "vix", "iv", "garch_state",
    "macd_hist", "sma20_dist", "gap_pct", "atr14_norm", "bb_width"
])
REGIME_FEATURES = list(REGIME_SET)

# 2-way ops applied to all qualifying pairs
TWO_WAY_OPS = ["min", "max", "diff", "mean", "product", "abs_diff",
               "rank_min", "rank_max", "clamp_diff", "z_sum", "z_diff", "sig_product", "rel_diff"]

# 3-way ops applied to qualifying triples
THREE_WAY_OPS = ["tri_mean", "tri_min", "tri_max", "tri_median", "tri_z_mean", "tri_sig_max"]

# Correlation boundaries
CORR_LOW_2WAY = 0.15
CORR_HIGH_2WAY = 0.85
CORR_LOW_3WAY = 0.10
CORR_HIGH_3WAY = 0.90

# Vol/volume keywords for ratio filter
_VOL_KEYWORDS = ("vol", "atr", "width", "vix", "volume", "balance", "capital", "northbound")

MINING_LOG_PATH = HERE / "mining_log.json"

# Component stability thresholds (universal, ETF-agnostic)
# A component is "unstable" if its yearly IC is too variable or has too many negative years.
# Combos containing unstable components are pruned at generation time.
COMPONENT_IC_CV_MAX = 3.0       # Max coefficient of variation of yearly ICs
COMPONENT_NEG_YEARS_MAX = 2     # Max number of negative-IC years allowed


# ─── Mining Log ───────────────────────────────────────────────────────────────

def load_mining_log() -> dict:
    """Load the persistent mining log, or return empty structure.
    Tolerates trailing garbage (e.g. extra braces from interrupted writes)
    by using raw_decode to extract the first valid JSON object."""
    if MINING_LOG_PATH.exists():
        try:
            with open(MINING_LOG_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            obj, _end = json.JSONDecoder().raw_decode(content)
            return obj
        except (json.JSONDecodeError, ValueError) as e:
            print(f"WARNING: mining_log.json corrupted ({e}); starting fresh.")
    return {"generated_space": {}, "batches": []}


def save_mining_log(log: dict):
    """Persist the mining log."""
    with open(MINING_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def get_already_generated(log: dict, etf: str, side: str) -> set:
    """Return set of candidate feature names already generated for this ETF/side."""
    key = f"{etf}_{side}"
    entry = log.get("generated_space", {}).get(key, {})
    return set(entry.get("candidate_names", []))


def update_generated_space(log: dict, etf: str, side: str, candidates: list,
                           two_way_ops: list, three_way_ops: list,
                           top_k_2way: int, top_k_3way: int):
    """Update the mining log's generated_space entry after generation."""
    key = f"{etf}_{side}"
    all_names = sorted([c["feature_name"] for c in candidates])
    name_hash = hashlib.sha256("|".join(all_names).encode()).hexdigest()[:16]

    if "generated_space" not in log:
        log["generated_space"] = {}

    existing = log["generated_space"].get(key, {})
    prev_names = set(existing.get("candidate_names", []))
    new_names = set(all_names)
    merged_names = sorted(prev_names | new_names)

    log["generated_space"][key] = {
        "2way_ops": two_way_ops,
        "3way_ops": three_way_ops,
        "top_k_2way": top_k_2way,
        "top_k_3way": top_k_3way,
        "total_generated": len(merged_names),
        "new_this_run": len(new_names - prev_names),
        "last_generated_at": datetime.now(timezone.utc).isoformat(),
        "hash": name_hash,
        "candidate_names": merged_names,
    }


# ─── Mining Memory (forbidden directions) ────────────────────────────────────

def load_mining_memory(etf, side, suffix):
    memory_path = HERE / f"mining_memory_{etf}_{side}{suffix}.json"
    if memory_path.exists():
        with open(memory_path, "r") as f:
            return json.load(f)
    return {"forbidden_features": [], "rejected_families": []}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_vol_or_volume(feature_name):
    """Check if a feature name indicates a positive scaling volatility/volume indicator."""
    fn = feature_name.lower()
    return any(kw in fn for kw in _VOL_KEYWORDS)


def _spearman_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape[0] < 5:
        return 0.0
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a).astype(np.float32)
    rb = rankdata(b).astype(np.float32)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom < 1e-12:
        return 0.0
    return float((ra * rb).sum() / denom)


def compute_side_tail_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str) -> float:
    n = len(y_pred)
    if side in ("long", "short"):
        pct = 0.15
    else:  # single (two-sided)
        pct = 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return 0.0

    order = np.argsort(y_pred)
    if side == "long":
        idx = order[-n_tail:]
    elif side == "short":
        idx = order[:n_tail]
    else:  # two-sided
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])

    return _spearman_from_arrays(y_true[idx], y_pred[idx])


def compute_component_stability(X_df: pd.DataFrame, y: np.ndarray, dates: np.ndarray,
                                features: list, side: str) -> dict:
    """Compute yearly IC stability for each feature.
    
    Returns dict mapping feature_name -> {"ic_cv": float, "n_negative_years": int, "stable": bool}.
    A feature is unstable if IC_CV > COMPONENT_IC_CV_MAX OR n_negative_years > COMPONENT_NEG_YEARS_MAX.
    
    This is a TRAINING-ONLY gate: uses only in-sample data to detect regime-dependent components.
    """
    years = pd.DatetimeIndex(dates).year
    unique_years = sorted(set(years))
    
    if len(unique_years) < 3:
        # Not enough years for stability assessment — mark all as stable
        return {f: {"ic_cv": 0.0, "n_negative_years": 0, "stable": True} for f in features}
    
    results = {}
    for feat in features:
        if feat not in X_df.columns:
            results[feat] = {"ic_cv": 0.0, "n_negative_years": 0, "stable": True}
            continue
        
        vals = X_df[feat].values.astype(np.float64)
        
        # Determine sign from full-sample IC
        full_ic = _spearman_from_arrays(vals, y)
        sign = 1.0 if full_ic >= 0 else -1.0
        pred = sign * vals
        
        # Compute yearly ICs
        yearly_ics = []
        for yr in unique_years:
            mask = years == yr
            if mask.sum() < 20:
                continue
            yr_ic = _spearman_from_arrays(y[mask], pred[mask])
            yearly_ics.append(yr_ic)
        
        if len(yearly_ics) < 3:
            results[feat] = {"ic_cv": 0.0, "n_negative_years": 0, "stable": True}
            continue
        
        ic_arr = np.array(yearly_ics)
        mean_ic = np.mean(ic_arr)
        std_ic = np.std(ic_arr)
        
        # IC coefficient of variation
        ic_cv = std_ic / abs(mean_ic) if abs(mean_ic) > 1e-6 else 99.0
        n_negative = int(np.sum(ic_arr < 0))
        
        is_stable = (ic_cv <= COMPONENT_IC_CV_MAX) and (n_negative <= COMPONENT_NEG_YEARS_MAX)
        
        results[feat] = {
            "ic_cv": float(ic_cv),
            "n_negative_years": n_negative,
            "stable": is_stable,
        }
    
    return results


def filter_unstable_combos(candidates: list, stability: dict) -> tuple:
    """Remove candidates containing unstable components.
    
    Returns (kept_candidates, n_removed).
    """
    unstable_set = {f for f, s in stability.items() if not s["stable"]}
    if not unstable_set:
        return candidates, 0
    
    kept = []
    removed = 0
    for cand in candidates:
        recipe = cand.get("recipe", {})
        components = []
        for key in ["feature_a", "feature_b", "feature_c", "feature_cond", "feature_cond2"]:
            if key in recipe:
                components.append(recipe[key])
        
        # Check if any component is unstable
        has_unstable = any(c in unstable_set for c in components)
        if has_unstable:
            removed += 1
        else:
            kept.append(cand)
    
    return kept, removed


def batch_feature_ic(X: np.ndarray, y: np.ndarray, side: str) -> np.ndarray:
    """Vectorized tail-IC computation for all features at once.

    Returns array of shape (n_features,) with abs(tail_ic) values.
    Uses fp32 throughout for speed.
    """
    n, n_feats = X.shape
    pct = 0.15 if side in ("long", "short") else 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return np.zeros(n_feats, dtype=np.float32)

    # Rank y once
    ry = rankdata(y).astype(np.float32)

    # Raw Spearman for sign detection: rank all features at once
    # X_ranks: (n, n_feats)
    X_ranks = np.empty_like(X, dtype=np.float32)
    for j in range(n_feats):
        X_ranks[:, j] = rankdata(X[:, j]).astype(np.float32)

    # Center ranks
    X_centered = X_ranks - X_ranks.mean(axis=0, keepdims=True)
    ry_centered = ry - ry.mean()

    # Full Spearman = dot product of centered ranks / (norms)
    x_norms = np.sqrt((X_centered ** 2).sum(axis=0))  # (n_feats,)
    y_norm = np.sqrt((ry_centered ** 2).sum())
    denom = x_norms * y_norm
    denom[denom < 1e-12] = 1.0
    raw_ics = (X_centered.T @ ry_centered) / denom  # (n_feats,)

    # Sign flip: make all features positively correlated
    signs = np.where(raw_ics < 0, -1.0, 1.0).astype(np.float32)
    X_flipped = X * signs[np.newaxis, :]  # (n, n_feats)

    # Tail IC per feature
    tail_ics = np.zeros(n_feats, dtype=np.float32)
    for j in range(n_feats):
        pred = X_flipped[:, j]
        order = np.argsort(pred)
        if side == "long":
            idx = order[-n_tail:]
        elif side == "short":
            idx = order[:n_tail]
        else:
            idx = np.concatenate([order[:n_tail], order[-n_tail:]])

        # Spearman on tail subset
        y_tail = y[idx]
        p_tail = pred[idx]
        if np.std(y_tail) < 1e-12 or np.std(p_tail) < 1e-12:
            continue
        ra = rankdata(y_tail).astype(np.float32)
        rb = rankdata(p_tail).astype(np.float32)
        ra -= ra.mean()
        rb -= rb.mean()
        d = np.sqrt((ra * ra).sum() * (rb * rb).sum())
        if d > 1e-12:
            tail_ics[j] = abs(float((ra * rb).sum() / d))

    return tail_ics


# ─── 2-Way Generation ────────────────────────────────────────────────────────

def generate_2way(top_k_features, corr_arr, feat_idx_map, regime_candidates,
                  non_regime_candidates, forbidden_set, forbidden_families) -> list:
    """Generate all 2-feature combination candidates using numpy corr array."""
    candidates = []
    n = len(top_k_features)

    for i in range(n):
        feat_a = top_k_features[i]
        idx_a = feat_idx_map[feat_a]
        a_is_vol = is_vol_or_volume(feat_a)
        for j in range(i + 1, n):
            feat_b = top_k_features[j]
            idx_b = feat_idx_map[feat_b]

            corr = corr_arr[idx_a, idx_b]
            if corr > CORR_HIGH_2WAY or corr < CORR_LOW_2WAY:
                continue

            # Standard ops
            for op in TWO_WAY_OPS:
                name = f"combo_{op}__{feat_a}__{feat_b}"
                if name not in forbidden_set and not any(fam in name for fam in forbidden_families):
                    candidates.append({"feature_name": name,
                                       "recipe": {"op": op, "feature_a": feat_a, "feature_b": feat_b}})

            # ratio: check vol/volume
            if is_vol_or_volume(feat_b):
                name = f"combo_ratio__{feat_a}__{feat_b}"
                if name not in forbidden_set and not any(fam in name for fam in forbidden_families):
                    candidates.append({"feature_name": name,
                                       "recipe": {"op": "ratio", "feature_a": feat_a, "feature_b": feat_b}})
            if a_is_vol:
                name = f"combo_ratio__{feat_b}__{feat_a}"
                if name not in forbidden_set and not any(fam in name for fam in forbidden_families):
                    candidates.append({"feature_name": name,
                                       "recipe": {"op": "ratio", "feature_a": feat_b, "feature_b": feat_a}})

    # ifelse combinations (regime-conditioned switching)
    for cond in regime_candidates:
        for a_idx in range(len(non_regime_candidates)):
            feat_a = non_regime_candidates[a_idx]
            for b_idx in range(a_idx + 1, len(non_regime_candidates)):
                feat_b = non_regime_candidates[b_idx]
                name = f"combo_ifelse__{cond}__{feat_a}__{feat_b}"
                if name not in forbidden_set and not any(fam in name for fam in forbidden_families):
                    candidates.append({"feature_name": name,
                                       "recipe": {"op": "ifelse", "feature_cond": cond,
                                                  "feature_a": feat_a, "feature_b": feat_b}})

    return candidates


# ─── 3-Way Generation ────────────────────────────────────────────────────────

def generate_3way(top_k_3_features, corr_arr, feat_idx_map, regime_candidates,
                  forbidden_set, forbidden_families) -> list:
    """Generate all 3-feature combination candidates using numpy corr array."""
    candidates = []

    # Standard tri ops (tri_mean, tri_min, tri_max, tri_median)
    for combo in itertools.combinations(top_k_3_features, 3):
        feat_a, feat_b, feat_c = combo
        ia, ib, ic = feat_idx_map[feat_a], feat_idx_map[feat_b], feat_idx_map[feat_c]

        corr_ab = corr_arr[ia, ib]
        corr_ac = corr_arr[ia, ic]
        corr_bc = corr_arr[ib, ic]

        if corr_ab > CORR_HIGH_3WAY or corr_ab < CORR_LOW_3WAY:
            continue
        if corr_ac > CORR_HIGH_3WAY or corr_ac < CORR_LOW_3WAY:
            continue
        if corr_bc > CORR_HIGH_3WAY or corr_bc < CORR_LOW_3WAY:
            continue

        for op in THREE_WAY_OPS:
            name = f"combo_{op}__{feat_a}__{feat_b}__{feat_c}"
            if name not in forbidden_set and not any(fam in name for fam in forbidden_families):
                candidates.append({"feature_name": name,
                                   "recipe": {"op": op, "feature_a": feat_a,
                                              "feature_b": feat_b, "feature_c": feat_c}})

    # tri_ifelse: nested regime branching
    non_regime_3 = [f for f in top_k_3_features if f not in REGIME_SET]
    regime_in_top3 = [f for f in top_k_3_features if f in REGIME_SET]

    for cond_pair in itertools.combinations(regime_in_top3, 2):
        cond1, cond2 = cond_pair
        for action_triple in itertools.combinations(non_regime_3, 3):
            feat_a, feat_b, feat_c = action_triple
            name = f"combo_tri_ifelse__{cond1}__{cond2}__{feat_a}__{feat_b}__{feat_c}"
            if name not in forbidden_set and not any(fam in name for fam in forbidden_families):
                candidates.append({"feature_name": name,
                                   "recipe": {"op": "tri_ifelse", "feature_cond": cond1,
                                              "feature_cond2": cond2, "feature_a": feat_a,
                                              "feature_b": feat_b, "feature_c": feat_c}})

    return candidates


# ─── Main ─────────────────────────────────────────────────────────────────────

def run_one(etf: str, side: str, args):
    """Run generation for a single ETF/side combination."""
    suffix = "_early" if args.early else ""
    do_3way = not args.two_only

    # 1. Pool size gate check (1c)
    if hasattr(args, "min_pool_floor") and args.min_pool_floor > 0 and not getattr(args, "ignore_pool_floor", False):
        pool = get_admitted_pool(etf, side)
        if len(pool) < args.min_pool_floor:
            print(f"\n{'='*60}")
            print(f"Generating combos for {etf} ({side})")
            print(f"  SKIP: Admitted pool size is {len(pool)} < floor ({args.min_pool_floor}). Mine single features first.")
            return

    # 1b. Train date range
    if etf == "588000ETF":
        train_start = pd.Timestamp("2020-11-01")
        train_end = pd.Timestamp("2025-01-01")
    else:
        train_start = pd.Timestamp("2015-01-01")
        train_end = pd.Timestamp("2022-01-01")

    print(f"\n{'='*60}")
    print(f"Generating combos for {etf} ({side})")
    print(f"  2-way: top-{args.top_k}, ops={TWO_WAY_OPS + ['ratio', 'ifelse']}")
    if do_3way:
        print(f"  3-way: top-{args.top_k_3}, ops={THREE_WAY_OPS + ['tri_ifelse']}")

    # 2. Load dataset
    features_dir = REPO_ROOT / "day-model" / "data"
    fname = f"features_{etf}_early.parquet" if args.early else f"features_{etf}.parquet"
    path = features_dir / fname
    if not path.exists():
        print(f"  SKIP: Dataset not found at {path}")
        return

    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
    if len(train_df) == 0:
        print("  SKIP: Empty train set.")
        return

    # fp32 for speed
    y_train = train_df["trade_return"].values.astype(np.float32)
    X_df = train_df[FEATURES].ffill()
    col_med = X_df.median().fillna(0.0)
    X_df = X_df.fillna(col_med)
    X_mat = X_df.values.astype(np.float32)  # (n_samples, n_features)

    # 3. Vectorized feature IC evaluation
    print(f"  Pre-evaluating {len(FEATURES)} features (vectorized fp32)...")
    tail_ics = batch_feature_ic(X_mat, y_train, side)

    # Sort features by IC
    sorted_idx = np.argsort(tail_ics)[::-1]
    feature_ics = [(FEATURES[i], float(tail_ics[i])) for i in sorted_idx]

    # Sample-size scaling relative to ~3400 trading days base
    n_days = len(train_df)
    sample_ratio = min(1.0, max(0.40, n_days / 3400.0))
    eff_top_k = max(15, int(args.top_k * sample_ratio))
    eff_top_k_3 = max(10, int(args.top_k_3 * sample_ratio))

    top_k_features = [FEATURES[i] for i in sorted_idx[:eff_top_k]]
    top_k_3_features = [FEATURES[i] for i in sorted_idx[:eff_top_k_3]]
    print(f"  Sample size: {n_days} days (ratio {sample_ratio:.2f}). Selected Top {eff_top_k} (2-way), Top {eff_top_k_3} (3-way).")
    print(f"  Best: {feature_ics[0][0]} (IC={feature_ics[0][1]:.4f})")

    # 3b. Component stability gate (training-only, ETF-agnostic)
    # Identifies features with unstable yearly IC — these produce regime-dependent combos.
    print(f"  Computing component stability (yearly IC decomposition)...")
    dates_train = train_df["date"].values
    stability = compute_component_stability(X_df, y_train, dates_train, FEATURES, side)
    unstable_features = [f for f, s in stability.items() if not s["stable"]]
    if unstable_features:
        print(f"  Unstable components (IC_CV>{COMPONENT_IC_CV_MAX} or neg_years>{COMPONENT_NEG_YEARS_MAX}): {unstable_features}")
    else:
        print(f"  All components stable.")

    # 4. Compute pairwise correlation matrix (numpy, fp32)
    all_needed = list(set(top_k_features + top_k_3_features))
    feat_idx_map = {f: i for i, f in enumerate(all_needed)}
    X_sub = X_df[all_needed].values.astype(np.float32)  # (n, k)
    # Center and compute corr via dot product
    X_sub -= X_sub.mean(axis=0, keepdims=True)
    norms = np.sqrt((X_sub ** 2).sum(axis=0))
    norms[norms < 1e-12] = 1.0
    X_normed = X_sub / norms[np.newaxis, :]
    corr_arr = np.abs(X_normed.T @ X_normed).astype(np.float32)  # (k, k)

    # Load mining memory (forbidden directions)
    memory = load_mining_memory(etf, side, suffix)
    forbidden_set = set(memory.get("forbidden_features", []))
    forbidden_families = memory.get("rejected_families", [])

    # Identify regime features in the top K
    regime_candidates = [f for f in top_k_features if f in REGIME_SET]
    non_regime_candidates = [f for f in top_k_features if f not in REGIME_SET][:15]

    # 5. Generate 2-way combinations
    candidates_2way = generate_2way(
        top_k_features, corr_arr, feat_idx_map,
        regime_candidates, non_regime_candidates,
        forbidden_set, forbidden_families
    )
    print(f"  2-way raw candidates: {len(candidates_2way)}")

    # 6. Generate 3-way combinations
    candidates_3way = []
    if do_3way:
        regime_3 = [f for f in top_k_3_features if f in REGIME_SET]
        candidates_3way = generate_3way(
            top_k_3_features, corr_arr, feat_idx_map,
            regime_3, forbidden_set, forbidden_families
        )
        print(f"  3-way raw candidates: {len(candidates_3way)}")

    all_candidates = candidates_2way + candidates_3way

    # 6b. Filter combos with unstable components
    all_candidates, n_unstable_removed = filter_unstable_combos(all_candidates, stability)
    if n_unstable_removed > 0:
        print(f"  Component stability filter: removed {n_unstable_removed} combos with unstable components.")

    # 7. Dedup against mining log
    log = load_mining_log()
    if not args.no_dedup:
        already_generated = get_already_generated(log, etf, side)
        before = len(all_candidates)
        all_candidates = [c for c in all_candidates
                          if c["feature_name"] not in already_generated]
        deduped = before - len(all_candidates)
        if deduped > 0:
            print(f"  Dedup: removed {deduped} previously generated candidates.")

    # 8. Update mining log
    two_way_ops_used = TWO_WAY_OPS + ["ratio", "ifelse"]
    three_way_ops_used = (THREE_WAY_OPS + ["tri_ifelse"]) if do_3way else []
    update_generated_space(
        log, etf, side, all_candidates,
        two_way_ops_used, three_way_ops_used,
        args.top_k, args.top_k_3 if do_3way else 0
    )
    save_mining_log(log)

    # 9. Save candidates JSON
    os.makedirs(HERE, exist_ok=True)
    out_path = HERE / f"candidates_{etf}_{side}{suffix}.json"
    with open(out_path, "w") as f:
        json.dump(all_candidates, f, indent=2)

    print(f"  => {len(all_candidates)} NEW candidates saved to {out_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Generate aggressive feature combination candidates.")
    parser.add_argument("-e", "--etf", default="all",
                        choices=["all"] + ALL_ETFS,
                        help="ETF to process (default: all)")
    parser.add_argument("-s", "--side", default="all",
                        choices=["all"] + ALL_SIDES,
                        help="Side to process (default: all)")
    parser.add_argument("-k", "--top-k", type=int, default=50,
                        help="Number of top base features for 2-way combinations (default: 50)")
    parser.add_argument("--top-k-3", type=int, default=25,
                        help="Number of top base features for 3-way combinations (default: 25)")
    parser.add_argument("--two-only", action="store_true",
                        help="Only generate 2-way combinations (skip 3-way)")
    parser.add_argument("--early", action="store_true",
                        help="Use early window return dataset")
    parser.add_argument("--min-pool-floor", type=int, default=0,
                        help="Minimum admitted pool size required before generating combos (default: 0)")
    parser.add_argument("--ignore-pool-floor", action="store_true",
                        help="Bypass the admitted pool size floor check")
    parser.add_argument("--no-dedup", action="store_true",
                        help="Disable dedup against mining log (regenerate everything)")
    args = parser.parse_args()

    etfs = ALL_ETFS if args.etf == "all" else [args.etf]
    sides = ALL_SIDES if args.side == "all" else [args.side]

    total = len(etfs) * len(sides)
    print(f"Feature combo generation: {len(etfs)} ETF(s) x {len(sides)} side(s) = {total} jobs")

    for etf in etfs:
        for side in sides:
            run_one(etf, side, args)

    print(f"\n{'='*60}")
    print(f"All done. {total} jobs completed.")


if __name__ == "__main__":
    main()
