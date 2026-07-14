"""
Build frozen feature lists for the frozen-vs-CSS experiment.

Arm B (Handpicked): Start from historical CSS outputs. Keep features selected
in >=6 of 8 quarters. Top up to each ETF's median historical CSS size using
the highest-frequency remaining features. Apply VIF+cond pruning at training
time (via train_etf's frozen_features path).

Arm C (Random Placebo): Random sample of the same count as Arm B per ETF.
Single fixed seed (42). Same VIF+cond pruning at training time.

Usage:
    python day-model/build_frozen_features.py            # Build and save
    python day-model/build_frozen_features.py --seed 42  # Custom seed for Arm C
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROLLING_DATA_DIR = HERE / "data" / "rolling"
OUT_DIR = HERE / "data" / "frozen"

ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
QUARTERS = ["202403", "202406", "202409", "202412",
            "202503", "202506", "202509", "202512"]
FREQ_THRESHOLD = 6  # >=6 of 8 quarters


def load_historical_css(etf: str):
    """Load per-quarter CSS selected_features for one ETF.

    CSS is side-independent (verified): single/long/short share the same
    selected_features for a given (ETF, quarter). We use the single-side
    champion (_sortino_blended) JSON.

    Returns (feature_sets, sizes) where feature_sets is a list of sets
    (one per quarter found) and sizes is a list of int sizes.
    """
    feature_sets = []
    sizes = []
    found_quarters = []
    for q in QUARTERS:
        for suffix in ["_sortino_blended", ""]:
            path = ROLLING_DATA_DIR / f"results_{etf}_r{q}{suffix}.json"
            if path.exists():
                with open(path) as f:
                    r = json.load(f)
                sf = list(r["selected_features"])
                feature_sets.append(set(sf))
                sizes.append(len(sf))
                found_quarters.append(q)
                break
    return feature_sets, sizes, found_quarters


def build_arm_b(etf: str, feature_sets, sizes):
    """Handpicked frozen list: features in >=6/8 quarters, topped up to median size."""
    freq = Counter()
    for s in feature_sets:
        for f in s:
            freq[f] += 1
    target_count = int(np.median(sizes)) if sizes else 15

    # Features passing the frequency threshold (preserving freq-desc order)
    passing = sorted(
        [f for f, c in freq.items() if c >= FREQ_THRESHOLD],
        key=lambda f: (-freq[f], f),
    )
    # Top-up candidates: features not passing, ordered by frequency desc then name
    remaining = sorted(
        [f for f, c in freq.items() if c < FREQ_THRESHOLD],
        key=lambda f: (-freq[f], f),
    )

    frozen = list(passing)
    for f in remaining:
        if len(frozen) >= target_count:
            break
        frozen.append(f)

    return frozen, freq, target_count, len(passing)


def build_arm_c(etf: str, all_features: list, target_count: int, seed: int):
    """Random placebo: sample target_count features uniformly without replacement.

    Per-ETF variation is achieved by combining the global seed with the ETF
    name hash. This keeps a single canonical seed (reproducibility) while
    ensuring different ETFs draw different placebo lists.
    """
    etf_offset = abs(hash(etf)) % (2**31)
    rng = np.random.default_rng(seed + etf_offset)
    pool = list(all_features)
    chosen_idx = rng.choice(len(pool), size=min(target_count, len(pool)),
                            replace=False)
    return [pool[i] for i in sorted(chosen_idx.tolist())]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42,
                    help="Random seed for Arm C (placebo). Default 42.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load master FEATURES list from build_features (needed for Arm C pool)
    import sys
    sys.path.insert(0, str(HERE))
    from build_features import FEATURES
    print(f"Master FEATURES pool: {len(FEATURES)} features")

    summary = {"etfs": {}, "config": {
        "freq_threshold": FREQ_THRESHOLD,
        "n_quarters": len(QUARTERS),
        "arm_c_seed": args.seed,
        "topup_policy": "median_historical_css_size",
    }}

    arm_b_all = {}
    arm_c_all = {}

    for etf in ETFS:
        feature_sets, sizes, found = load_historical_css(etf)
        if len(feature_sets) == 0:
            print(f"[{etf}] No historical CSS results found, skipping.")
            continue

        b_list, freq, target, n_passing = build_arm_b(etf, feature_sets, sizes)
        c_list = build_arm_c(etf, FEATURES, target, args.seed)

        # Report
        union_b = set(b_list)
        union_c = set(c_list)
        overlap = union_b & union_c
        print(f"\n[{etf}] quarters_found={len(found)}/8  "
              f"unique_in_history={len(freq)}  "
              f"passing_>={FREQ_THRESHOLD}/8={n_passing}  "
              f"target_count={target}")
        print(f"  Arm B (handpicked): {len(b_list)} features")
        print(f"    {sorted(b_list)}")
        print(f"  Arm C (random seed={args.seed}): {len(c_list)} features")
        print(f"    {sorted(c_list)}")
        print(f"  B vs C overlap: {len(overlap)} features "
              f"({100*len(overlap)/max(1,len(union_b)):.1f}% of B)")

        arm_b_all[etf] = b_list
        arm_c_all[etf] = c_list
        summary["etfs"][etf] = {
            "quarters_found": len(found),
            "unique_features_in_history": len(freq),
            "features_passing_freq_threshold": n_passing,
            "median_css_size": target,
            "size_arm_b": len(b_list),
            "size_arm_c": len(c_list),
            "arm_b_features": b_list,
            "arm_c_features": c_list,
            "b_c_overlap": len(overlap),
            "frequency_map": dict(freq),
            "historical_sizes": sizes,
        }

    # Save outputs
    out_b = OUT_DIR / "arm_b_handpicked.json"
    out_c = OUT_DIR / "arm_c_random.json"
    out_summary = OUT_DIR / "frozen_features_summary.json"
    with open(out_b, "w") as f:
        json.dump(arm_b_all, f, indent=2)
    with open(out_c, "w") as f:
        json.dump(arm_c_all, f, indent=2)
    with open(out_summary, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nSaved:")
    print(f"  Arm B: {out_b}")
    print(f"  Arm C: {out_c}")
    print(f"  Summary: {out_summary}")


if __name__ == "__main__":
    main()
