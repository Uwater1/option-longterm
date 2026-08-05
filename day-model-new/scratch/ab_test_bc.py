"""A/B test of claude_said2.txt gates B and C (plus bonus E-discriminator check).

Population: current (gated) focus-window pools with OOS tier labels from
filter_diagnosis_p*.json. All new metrics are TRAIN-ONLY; ground truth is the
OOS tier (TP/Median/FP). We report how many FPs each candidate rule would kill
vs TP collateral, same methodology as research_gate_ab_test.py.

Gates tested:
  B  Sortino jackknife: 7 contiguous chunks of the train window; drop each
     chunk, recompute base-cost enforced-sign Sortino on the remaining 6.
     Metrics: jk_median, jk_cv = std/|mean|. Rules: jk_median <= 0, and
     (jk_median <= 0 OR jk_cv > cap) for cap in [0.5, 1.0, 1.5, 2.0, 3.0].
  C  Conviction-z plateau: Sortino under conviction_weighted sizing (exact
     simulate_returns logic) at z in {0.4, 0.5, 0.6} (+-20% around 0.5).
     Rules: min(sortinos) <= 0 ; also sign-flip count >= 1.
  E  (bonus) bootstrap Sortino CI at CURRENT stress cost (2.5x): 5th pct of
     199 block-bootstrap Sortinos computed on the STRESSED return series.
     Rule: ci_stress <= 0.  Tests whether the AND-ensemble adds discrimination
     beyond the current independent G4 (base-cost CI) + G7 (point stress).
"""
import sys
import json
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "mining"))
sys.path.insert(0, str(HERE.parent / "day-model"))

import research_gate_ab_test as H
from select_features import (_tail_positions_binary, _sortino_annual,
                             _bootstrap_sortino_ci, BOOT_B, BOOT_BLOCK)
import select_features as SF

COST = 0.0008
STRESS_MULT = 2.5
E_MULTS = [1.125, 1.25, 1.375, 1.5]  # in-bootstrap stress sweep (= 9/10/11/12bp base)
N_CHUNKS = 7
Z_SWEEP = [0.4, 0.5, 0.6]
FOCUS = {
    "_p2015_2023": ("2015-01-01", "2023-01-01"),
    "_p2016_2024": ("2016-01-01", "2024-01-01"),
    "_p2017_2025": ("2017-01-01", "2025-01-01"),
    "_p2018_2026": ("2018-01-01", "2026-01-01"),
}
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]


def conviction_positions(y_true, pred, side, conviction_z):
    """Mirror simulate_returns(position_mode='conviction_weighted',
    enforce_absolute_sign=True) for a given conviction_z."""
    n = len(pred)
    order = np.argsort(pred, kind="quicksort")
    pos = np.zeros(n, dtype=np.float64)
    std_pred = float(np.std(pred))
    mean_pred = float(np.mean(pred))

    def assign(idx, direction, y_check_mean):
        if std_pred <= 1e-12:
            return
        if y_check_mean <= 0.0:
            return
        z = direction * (pred[idx] - mean_pred) / std_pred
        mask = z > conviction_z
        if np.any(mask):
            sizes = np.tanh((z[mask] - conviction_z) / 1.5)
            pos[idx[mask]] = direction * sizes

    if side == "long":
        n_tail = max(5, int(n * 0.15))
        idx = order[-n_tail:]
        assign(idx, 1.0, float(np.mean(y_true[idx])))
    elif side == "short":
        n_tail = max(5, int(n * 0.15))
        idx = order[:n_tail]
        assign(idx, -1.0, float(np.mean(-y_true[idx])))
    else:
        n_tail = max(5, int(n * 0.10))
        li, si = order[-n_tail:], order[:n_tail]
        assign(li, 1.0, float(np.mean(y_true[li])))
        assign(si, -1.0, float(np.mean(-y_true[si])))
    return pos


def compute_metrics(train_df, item, side, tstats):
    feat_name = item["feature_name"]
    sign = item.get("sign", 1)
    recipe = item.get("recipe", None)
    vals_tr = H._feature_values(train_df, feat_name, recipe, *tstats)
    if vals_tr is None:
        return None
    pred_tr = sign * vals_tr
    y_tr = train_df["trade_return"].values.astype(np.float64)
    if np.std(pred_tr) < 1e-12:
        return None

    # --- E: bootstrap CI under stress cost, swept over in-bootstrap multipliers ---
    pos = _tail_positions_binary(y_tr, pred_tr, side)
    raw = pos * y_tr
    abs_pos = np.abs(pos)

    # Point-stress Sortino at 3.0x (increment on top of current 2.5x gate)
    point_30 = _sortino_annual(raw - abs_pos * COST * 3.0)

    rng = np.random.default_rng(42)
    T_len = len(raw)
    nblocks = int(np.ceil(T_len / BOOT_BLOCK))
    starts = rng.integers(0, max(T_len - BOOT_BLOCK, 1), size=(BOOT_B, nblocks))
    offs = np.arange(BOOT_BLOCK)
    idxm = (starts[:, :, None] + offs[None, None, :]) % T_len
    raw_boot = raw[idxm].reshape(BOOT_B, -1)[:, :T_len]
    abs_boot = abs_pos[idxm].reshape(BOOT_B, -1)[:, :T_len]

    out = {"feature_name": feat_name, "point_3.0": point_30}
    for m in E_MULTS:
        boot_ret = raw_boot - abs_boot * COST * m
        ann = boot_ret.mean(axis=1) * SF.ANNUAL_DAYS
        dvol = np.minimum(boot_ret, 0.0).std(axis=1) * np.sqrt(SF.ANNUAL_DAYS)
        out[f"ci_stress_{m}"] = float(np.percentile(ann / (dvol + 1e-10), 5.0))
    return out


def main():
    df_cache = {}
    all_rows = []
    for suffix, (t0, t1) in FOCUS.items():
        diag_path = HERE / "data" / f"filter_diagnosis{suffix}.json"
        if not diag_path.exists():
            continue
        diag = json.load(open(diag_path, encoding="utf-8"))
        for etf in ETFS:
            if etf not in diag:
                continue
            for side, s in diag[etf].items():
                tier_of = {}
                for tier in ("FP", "Median", "TP"):
                    for it in s.get(tier.lower() + "_features", []):
                        tier_of[(it["feature_name"], it.get("sign", 1))] = tier
                if not tier_of:
                    continue
                apath = HERE / "data" / f"mining_attempts_{etf}_{side}{suffix}.json"
                if not apath.exists():
                    continue
                attempts = json.load(open(apath, encoding="utf-8"))
                pool = [a for a in attempts if (a["feature_name"], a.get("sign", 1)) in tier_of]
                if not pool:
                    continue
                if etf not in df_cache:
                    path = HERE.parent / "day-model" / "data" / f"features_{etf}.parquet"
                    df = H.pd.read_parquet(path)
                    if "date" not in df.columns:
                        df = df.reset_index()
                    df["date"] = H.pd.to_datetime(df["date"])
                    df = df.sort_values("date").reset_index(drop=True)
                    for col in H.FEATURES:
                        df[col] = df[col].ffill()
                    df_cache[etf] = df
                df = df_cache[etf]
                train_df, lock_df, tstats = H.prep_split(df, t0, t1)
                if train_df is None:
                    continue
                tr_med = tstats[2]
                for col in H.FEATURES:
                    train_df[col] = train_df[col].fillna(tr_med[col])
                for item in pool:
                    try:
                        res = compute_metrics(train_df, item, side, tstats)
                    except Exception:
                        res = None
                    if res is None:
                        continue
                    res["suffix"] = suffix
                    res["etf"] = etf
                    res["tier"] = tier_of[(item["feature_name"], item.get("sign", 1))]
                    all_rows.append(res)
        print(f"done {suffix}, cumulative rows={len(all_rows)}", flush=True)

    out = HERE / "scratch" / "ab_bc_rows.json"
    json.dump(all_rows, open(out, "w", encoding="utf-8"))
    print("saved", out)

    def report(rows, label):
        tiers = {t: [r for r in rows if r["tier"] == t] for t in ["FP", "Median", "TP"]}
        n_fp, n_med, n_tp = len(tiers["FP"]), len(tiers["Median"]), len(tiers["TP"])
        if n_fp + n_med + n_tp == 0:
            return
        tot = n_fp + n_med + n_tp
        print(f"\n=== {label}  N={tot} FP={n_fp} Med={n_med} TP={n_tp} FPrate={n_fp/tot:.3f}")

        def line(name, rej):
            fk = sum(1 for r in tiers["FP"] if rej(r))
            mk = sum(1 for r in tiers["Median"] if rej(r))
            tk = sum(1 for r in tiers["TP"] if rej(r))
            rem = max(1, tot - fk - mk - tk)
            print(f"  {name:34s} FP {fk:3d}/{n_fp:<3d} Med {mk:3d}/{n_med:<3d} TP {tk:3d}/{n_tp:<3d} FPrate_after={(n_fp-fk)/rem:.3f}")

        # Point-stress increment: 2.5 -> 3.0
        line("POINT: stress@3.0x <=0", lambda r: r["point_3.0"] <= 0)
        # Boot-base tightening alone
        for m in E_MULTS:
            key = f"ci_stress_{m}"
            line(f"BOOT: boot-CI @{m}x <=0", lambda r, k=key: r[k] <= 0)
        # Combined: point 3.0 OR boot@m
        for m in E_MULTS:
            key = f"ci_stress_{m}"
            line(f"BOTH: point3.0 OR boot@{m}x",
                 lambda r, k=key: r["point_3.0"] <= 0 or r[k] <= 0)

    report(all_rows, "ALL FOCUS")
    for suffix in FOCUS:
        report([r for r in all_rows if r["suffix"] == suffix], suffix)


if __name__ == "__main__":
    main()
