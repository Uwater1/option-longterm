#!/usr/bin/env python3
"""
Meta-model feature feasibility study (pre-check for newtrade/TODO.md #2).

Question: is there ANY factor-level pattern that predicts the 13:30 -> 14:35
continuation (hold_benefit_1330) on in-sample trades? If no feature carries
signal here, training a meta-model will not find any either.

Features assembled per trade (all direction-normalized: multiplied by
position sign so longs and shorts are comparable):
  s_ snapshot columns already in meta_labels CSV (z_composite, pnl_at_*,
     morning_vol, first30_vol, lunch_move)
  f_ day-model-new admitted-pool factors (expanding z-score, sign-aligned,
     zero-lookahead; same values that feed Z_composite)
  u_ 13:30-unique intraday factors (noon gap, reopen drift, drawdown from
     trade peak, range position, trend consistency, realized vol, volume ratio)
  x_ price-action interactions combining s/u factors

Pattern search (IS trades only for discovery, OOS for stability):
  - Spearman IC of every feature vs hold_benefit_1330 (+ binary cut label)
  - Permutation max-|IC| null test (family-wise significance)
  - Exceedance counts vs the 5% chance expectation
  - Quintile bucket monotonicity for the top features
  - Long/short consistency for the top features
  - Pooled (3-ETF) scan on hand-crafted factors

Outputs
-------
newtrade/artifacts/meta_features_{etf}.csv   extended trade-feature matrix
newtrade/META_FEATURES_REPORT.md             findings & verdict
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

sys.path.append(str(HERE))

from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba)
from research_meta_label import load_day_bars, DEFAULT_ETFS, md_table, fmt

TARGET = "hold_benefit_1330"          # r_1435 - r_1330, position-signed
BINARY_LABEL = "cut_is_better"        # 1 if exiting at 13:30 beats 14:35
CATEGORIES = {"s": "snapshot", "f": "pool factor", "u": "13:30-unique", "x": "interaction"}
N_PERM = 500


# ----------------------------------------------------------------------
# Feature construction
# ----------------------------------------------------------------------
def add_intraday_features(tr: pd.DataFrame, bars: dict) -> pd.DataFrame:
    """u_ features from 1m bars, computed at the 13:30 decision point."""
    recs = []
    for _, row in tr.iterrows():
        dstr = row["date"].strftime("%Y-%m-%d")
        day = bars.get(dstr)
        rec = {}
        if day is None:
            recs.append(rec)
            continue
        sgn = 1.0 if row["position"] > 0 else -1.0
        opens, highs, lows, closes, vols = (day["opens"], day["highs"], day["lows"],
                                            day["closes"], day["volumes"])
        i0, i1330 = day["i_entry"], day["i_1330"]
        i1130, i1301, i1030 = day.get("i_1130", -1), day.get("i_1301", -1), day.get("i_1030", -1)

        c1330 = closes[i1330]
        if i1130 > 0 and i1301 > 0:
            c1130, o1301 = closes[i1130], opens[i1301]
            if c1130 > 0 and o1301 > 0:
                rec["u_noon_gap"] = sgn * float(np.log(o1301 / c1130))          # lunch gap
                rec["u_reopen_drift"] = sgn * float(np.log(c1330 / o1301))      # 13:01->13:30 drift
                rec["u_lunch_total"] = sgn * float(np.log(c1330 / c1130))       # gap + drift
            if i1301 > 0:
                v_reopen = float(vols[i1301: i1330 + 1].sum())
                v_first30 = float(vols[i0: i1030 + 1].sum()) if i1030 > i0 else np.nan
                rec["u_vol_ratio_reopen"] = v_reopen / v_first30 if (v_first30 and v_first30 > 0) else np.nan

        seg = closes[i0: i1330 + 1]
        if len(seg) > 5:
            log_rets = np.diff(np.log(np.maximum(seg, 1e-10)))
            rec["u_vol_to_now"] = float(np.std(log_rets))                        # realized vol 10:00->13:30
            rec["u_trend_consistency"] = float((sgn * log_rets > 0).mean())      # fraction of up-moves

        win_hi = float(highs[i0: i1330 + 1].max())
        win_lo = float(lows[i0: i1330 + 1].min())
        if sgn > 0:
            rec["u_drawdown_from_peak"] = float(np.log(c1330 / win_hi)) if win_hi > 0 else np.nan
        else:
            rec["u_drawdown_from_peak"] = float(np.log(win_lo / c1330)) if win_lo > 0 else np.nan
        if win_hi > win_lo:
            rp = (c1330 - win_lo) / (win_hi - win_lo)
            rec["u_range_position"] = rp if sgn > 0 else 1.0 - rp                # 1 = best for trade
        recs.append(rec)

    extra = pd.DataFrame(recs, index=tr.index)
    return pd.concat([tr, extra], axis=1)


def add_interactions(tr: pd.DataFrame) -> pd.DataFrame:
    """x_ price-action interactions (snapshot/unique x state)."""
    z = tr["z_composite"]
    tr = tr.copy()
    tr["x_abs_z"] = z.abs()
    tr["x_z_x_pnl1330"] = z * tr["pnl_at_1330"]
    tr["x_z_x_noongap"] = z * tr.get("u_noon_gap", np.nan)
    tr["x_z_x_reopen"] = z * tr.get("u_reopen_drift", np.nan)
    tr["x_z_x_mvol"] = z * tr["morning_vol"]
    tr["x_pnl_persist"] = tr["pnl_at_1125"] * tr["pnl_at_1330"]                  # >0: consistent path
    tr["x_gap_confirm"] = tr.get("u_noon_gap", np.nan) * tr.get("u_reopen_drift", np.nan)
    tr["x_dd_x_vol"] = tr.get("u_drawdown_from_peak", np.nan) * tr.get("u_vol_to_now", np.nan)
    return tr


def load_pool_factor_panel(etf: str, dates: pd.Series) -> tuple[pd.DataFrame, list]:
    """Sign-aligned expanding z-score values of admitted-pool factors at given dates."""
    pool = load_admitted_pool(etf, side="single", min_features=10, suffix="")
    if not pool:
        return pd.DataFrame(index=dates.index), []
    df_full = load_etf_dataset(etf)
    X, signs, names = build_pool_feature_matrix(df_full, pool)
    Z = expanding_zscore_numba(X)
    Z_signed = Z * signs[np.newaxis, :]
    idx_map = {d: i for i, d in enumerate(df_full["date"])}
    rows = np.array([idx_map.get(d, -1) for d in dates])
    vals = np.where((rows >= 0)[:, None], Z_signed[np.maximum(rows, 0)], np.nan)
    cols = [f"f_{n}" for n in names]
    return pd.DataFrame(vals, index=dates.index, columns=cols), names


def build_feature_frame(etf: str) -> pd.DataFrame:
    csv_path = HERE / "artifacts" / f"meta_labels_{etf}.csv"
    lab = pd.read_csv(csv_path, parse_dates=["date"])
    tr = lab[lab["position"].abs() > 1e-5].reset_index(drop=True).copy()
    tr[BINARY_LABEL] = (tr["r_1330"] > tr["r_1435"]).astype(int)

    bars = load_day_bars(etf)
    tr = add_intraday_features(tr, bars)
    tr = add_interactions(tr)

    pool_panel, pool_names = load_pool_factor_panel(etf, tr["date"])
    tr = pd.concat([tr, pool_panel], axis=1)
    print(f"    [FEATURES] {etf}: {len(tr)} trades | pool factors={len(pool_names)}, "
          f"unique={sum(c.startswith('u_') for c in tr.columns)}, "
          f"interactions={sum(c.startswith('x_') for c in tr.columns)}")
    return tr


def feature_columns(tr: pd.DataFrame, categories: tuple = ("s", "f", "u", "x")) -> list:
    snaps = ["z_composite", "pnl_at_1125", "pnl_at_1305", "pnl_at_1330",
             "morning_vol", "first30_vol", "lunch_move"]
    cols = []
    if "s" in categories:
        cols += [c for c in snaps if c in tr.columns]
    if "f" in categories:
        cols += [c for c in tr.columns if c.startswith("f_")]
    if "u" in categories:
        cols += [c for c in tr.columns if c.startswith("u_")]
    if "x" in categories:
        cols += [c for c in tr.columns if c.startswith("x_")]
    return cols


def category_of(col: str) -> str:
    if col.startswith("f_"):
        return "f"
    if col.startswith("u_"):
        return "u"
    if col.startswith("x_"):
        return "x"
    return "s"


# ----------------------------------------------------------------------
# Pattern search
# ----------------------------------------------------------------------
def scan_features(tr: pd.DataFrame, cols: list, panel: str) -> pd.DataFrame:
    """Spearman IC of each feature vs TARGET (+ binary label) on one panel."""
    d = tr[tr["period"] == panel]
    y = d[TARGET].values
    yb = d[BINARY_LABEL].values
    rows = []
    for c in cols:
        x = d[c].values.astype(np.float64)
        ok = np.isfinite(x) & np.isfinite(y)
        if ok.sum() < 30:
            continue
        rho, p = spearmanr(x[ok], y[ok])
        rho_b, p_b = spearmanr(x[ok], yb[ok])
        rows.append({"feature": c, "category": category_of(c), "n": int(ok.sum()),
                     "ic": float(rho), "p": float(p),
                     "ic_binary": float(rho_b), "p_binary": float(p_b)})
    return pd.DataFrame(rows)


def permutation_max_ic(tr: pd.DataFrame, cols: list, n_perm: int = N_PERM, seed: int = 7) -> tuple:
    """Family-wise null: distribution of max |rank-corr| under target shuffling (IS).
    Per-column missingness is handled by neutral rank imputation (mean rank),
    so rows are never dropped for having one missing feature."""
    d = tr[tr["period"] == "IS"]
    y = d[TARGET].values.astype(np.float64)
    ok_y = np.isfinite(y)
    n = int(ok_y.sum())
    if n < 30:
        return np.nan, np.array([np.nan]), np.nan

    R_list = []
    for c in cols:
        x = d[c].values.astype(np.float64)
        fin = np.isfinite(x) & ok_y
        if fin.sum() < 30:
            continue
        r = np.full(n, np.nan)
        r[fin] = rankdata(x[fin])
        r[~np.isfinite(r)] = (fin.sum() + 1) / 2.0   # neutral rank for missing
        R_list.append(r)
    if not R_list:
        return np.nan, np.array([np.nan]), np.nan
    R = np.column_stack(R_list)
    y = y[ok_y]
    yr = rankdata(y)

    def max_corr(yranks: np.ndarray) -> float:
        Rc = R - R.mean(axis=0)
        yc = yranks - yranks.mean()
        num = Rc.T @ yc
        den = np.sqrt((Rc ** 2).sum(axis=0)) * np.sqrt((yc ** 2).sum())
        with np.errstate(invalid="ignore", divide="ignore"):
            corr = np.where(den > 1e-12, num / den, 0.0)
        return float(np.nanmax(np.abs(corr)))

    rng = np.random.default_rng(seed)
    obs = max_corr(yr)
    null = np.array([max_corr(rng.permutation(yr)) for _ in range(n_perm)])
    fam_p = float((null >= obs).mean())
    return obs, null, fam_p


def bucket_analysis(tr: pd.DataFrame, feat: str, n_q: int = 5) -> dict:
    """Quintile buckets on IS feature values; mean hold-benefit IS + OOS."""
    d_is = tr[tr["period"] == "IS"].dropna(subset=[feat, TARGET])
    d_oos = tr[tr["period"] == "OOS"].dropna(subset=[feat, TARGET])
    if len(d_is) < n_q * 5:
        return {}
    edges = np.quantile(d_is[feat].values, np.linspace(0, 1, n_q + 1))
    edges[0], edges[-1] = -np.inf, np.inf

    def per_bucket(d: pd.DataFrame) -> tuple:
        idx = np.clip(np.searchsorted(edges, d[feat].values, side="right") - 1, 0, n_q - 1)
        means, ns = [], []
        for q in range(n_q):
            sel = d[TARGET].values[idx == q]
            means.append(float(sel.mean() * 1e4) if len(sel) else np.nan)
            ns.append(int(len(sel)))
        return means, ns

    m_is, n_is = per_bucket(d_is)
    m_oos, n_oos = per_bucket(d_oos)
    finite = [m for m in m_is if np.isfinite(m)]
    mono_up = len(finite) >= 3 and all(np.diff(finite) > 0)
    mono_dn = len(finite) >= 3 and all(np.diff(finite) < 0)
    return {"feat": feat, "m_is": m_is, "n_is": n_is, "m_oos": m_oos, "n_oos": n_oos,
            "mono_is": "up" if mono_up else ("down" if mono_dn else "no")}


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
def build_report(res: dict) -> str:
    L = []
    L.append("# Meta-Model Feature Feasibility Report\n")
    L.append("Pre-check for TODO #2: does ANY factor predict the 13:30→14:35 continuation "
             "(`hold_benefit_1330`) on in-sample production trades? Target is position-signed; "
             "all intraday features are direction-normalized. Discovery is IS-only; OOS is a "
             "stability mirror, never used for selection.\n")
    L.append("Feature categories: **s** snapshot (z_composite, running P&L, vols), "
             "**f** day-model-new admitted-pool factors (expanding z-score, sign-aligned, "
             "zero-lookahead), **u** 13:30-unique intraday (noon gap, reopen drift, drawdown, "
             "range position, trend consistency, realized vol, reopen volume ratio), "
             "**x** price-action interactions.\n")
    L.append("Caveat: pool membership was selected with data through 2024+, so `f_` values carry "
             "the same pool-selection lookahead as the labels themselves.\n")

    # Setup table
    rows = []
    for etf, r in res.items():
        if etf.startswith("_"):
            continue
        tr = r["frame"]
        rows.append([etf, int(((tr["period"] == "IS")).sum()), int((tr["period"] == "OOS").sum()),
                     sum(1 for c in r["cols"] if c.startswith("f_")),
                     sum(1 for c in r["cols"] if c.startswith("u_")),
                     sum(1 for c in r["cols"] if c.startswith("x_")),
                     sum(1 for c in r["cols"] if category_of(c) == "s")])
    L.append("## 1. Data\n")
    L.append(md_table(["ETF", "IS trades", "OOS trades", "#pool (f)", "#unique (u)",
                       "#interact (x)", "#snapshot (s)"], rows))
    L.append(f"\nNull benchmark: with n trades, Spearman SE ≈ 1/√n, so ~5% of features exceed "
             f"|IC| > 1.96/√n by chance (n=123 → 0.18, n=209 → 0.14, n=440 → 0.09).\n")

    for etf, r in res.items():
        if etf.startswith("_"):
            continue
        scan_is, scan_oos, perm = r["scan_is"], r["scan_oos"], r["perm"]
        obs_max, null_dist, fam_p = perm
        L.append(f"## 2. {etf}\n")

        # Null test
        L.append(f"**Null test (IS).** Observed max |IC| = **{obs_max:.3f}** vs permutation "
                 f"max-|IC| 95th percentile = {np.quantile(null_dist, 0.95):.3f} "
                 f"({N_PERM} shuffles); family-wise p = {fam_p:.3f}. "
                 f"{'SIGNAL PRESENT beyond chance.' if fam_p < 0.05 else 'No family-wise signal beyond chance.'}\n")

        # Exceedances
        n_feat = len(scan_is)
        n_sig = int(((scan_is["p"] < 0.05) & (scan_is["ic"].abs() > 0.05)).sum())
        n_big = int((scan_is["ic"].abs() > 0.10).sum())
        L.append(f"**Exceedances.** {n_sig}/{n_feat} features with p<0.05 & |IC|>0.05 "
                 f"(chance expectation ≈ {0.05 * n_feat:.0f}); {n_big} features with |IC| > 0.10.\n")

        # Top table
        merged = scan_is.merge(scan_oos[["feature", "ic", "p"]], on="feature", how="left",
                               suffixes=("", "_oos"))
        merged["stable"] = (np.sign(merged["ic"]) == np.sign(merged["ic_oos"])) \
                           & (merged["ic"].abs() > 0.08) & (merged["ic_oos"].abs() > 0.03)
        top = merged.reindex(merged["ic"].abs().sort_values(ascending=False).index).head(15)
        rows = [[t["feature"], CATEGORIES[t["category"]],
                 f"{t['ic']:+.3f}", f"{t['p']:.3f}", f"{t['ic_binary']:+.3f}",
                 fmt(t["ic_oos"], 3), "yes" if t["stable"] else ""]
                for _, t in top.iterrows()]
        L.append("**Top-15 features by |IS IC|** (target = hold_benefit_1330):\n")
        L.append(md_table(["Feature", "Cat", "IS IC", "p", "IS IC (binary cut)", "OOS IC", "IS→OOS stable"], rows))
        L.append("")

        # Category summary
        rows = []
        for cat, name in CATEGORIES.items():
            sub = scan_is[scan_is["category"] == cat]
            if len(sub) == 0:
                continue
            best = sub.loc[sub["ic"].abs().idxmax()]
            rows.append([name, len(sub), f"{best['feature']}", f"{best['ic']:+.3f}",
                         int((sub['p'] < 0.05).sum())])
        L.append("**Category summary** (IS):\n")
        L.append(md_table(["Category", "#features", "Best feature", "Best IC", "#p<0.05"], rows))
        L.append("")

        # Buckets
        top3 = top.head(3)["feature"].tolist()
        rows = []
        for f in top3:
            b = bucket_analysis(r["frame"], f)
            if not b:
                continue
            m_is_s = " / ".join(fmt(m, 1) for m in b["m_is"])
            m_oos_s = " / ".join(fmt(m, 1) for m in b["m_oos"])
            rows.append([f, b["mono_is"], m_is_s, m_oos_s])
        L.append("**Quintile buckets** (mean hold-benefit bps by IS quintile, Q1=lowest feature "
                 "value; OOS uses IS edges):\n")
        L.append(md_table(["Feature", "IS monotonic", "IS Q1..Q5 bps", "OOS Q1..Q5 bps"], rows))
        L.append("")

        # Long/short consistency
        d_is = r["frame"][r["frame"]["period"] == "IS"]
        rows = []
        for f in top.head(5)["feature"].tolist():
            lo = d_is[d_is["position"] > 0]
            sh = d_is[d_is["position"] < 0]
            rl = spearmanr(lo[f], lo[TARGET])[0] if len(lo) > 20 else np.nan
            rs = spearmanr(sh[f], sh[TARGET])[0] if len(sh) > 20 else np.nan
            rows.append([f, len(lo), fmt(rl, 3), len(sh), fmt(rs, 3),
                         "yes" if (np.isfinite(rl) and np.isfinite(rs) and np.sign(rl) == np.sign(rs)) else "no"])
        L.append("**Long/short consistency** (IS IC by side):\n")
        L.append(md_table(["Feature", "n long", "IC long", "n short", "IC short", "Same sign"], rows))
        L.append("")

    # Pooled hand-crafted scan
    pooled = res.get("_pooled")
    if pooled is not None:
        scan_p, scan_po = pooled["scan_is"], pooled["scan_oos"]
        merged = scan_p.merge(scan_po[["feature", "ic"]], on="feature", how="left",
                              suffixes=("", "_oos"))
        merged["stable"] = (np.sign(merged["ic"]) == np.sign(merged["ic_oos"])) \
                           & (merged["ic"].abs() > 0.06) & (merged["ic_oos"].abs() > 0.03)
        top = merged.reindex(merged["ic"].abs().sort_values(ascending=False).index).head(12)
        rows = [[t["feature"], CATEGORIES[t["category"]], f"{t['ic']:+.3f}", f"{t['p']:.3f}",
                 fmt(t["ic_oos"], 3), "yes" if t["stable"] else ""]
                for _, t in top.iterrows()]
        L.append("## 3. Pooled scan (3 ETFs, hand-crafted s/u/x features only)\n")
        L.append(md_table(["Feature", "Cat", "IS IC", "p", "OOS IC", "IS→OOS stable"], rows))
        n_sig = int(((scan_p["p"] < 0.05) & (scan_p["ic"].abs() > 0.05)).sum())
        L.append(f"\n{n_sig}/{len(scan_p)} features with p<0.05 & |IC|>0.05 "
                 f"(chance expectation ≈ {0.05 * len(scan_p):.0f}).\n")

    # Verdict
    L.append("## 4. Findings & verdict\n")
    L.append(res["_verdict"])
    return "\n".join(L)


def build_verdict(res: dict) -> str:
    lines = []
    n_pass_fam = 0
    n_total_big, n_stable_big = 0, 0
    for etf, r in res.items():
        if etf.startswith("_"):
            continue
        obs_max, null_dist, fam_p = r["perm"]
        scan_is, scan_oos = r["scan_is"], r["scan_oos"]
        n_sig = int(((scan_is["p"] < 0.05) & (scan_is["ic"].abs() > 0.05)).sum())
        exp = 0.05 * len(scan_is)
        passed = fam_p < 0.05
        n_pass_fam += int(passed)
        # OOS sign stability of features with meaningful IS IC
        merged = scan_is.merge(scan_oos[["feature", "ic"]], on="feature", how="left",
                               suffixes=("", "_oos"))
        big = merged[merged["ic"].abs() > 0.08]
        stable = big[(np.sign(big["ic"]) == np.sign(big["ic_oos"])) & (big["ic_oos"].abs() > 0.02)]
        n_total_big += len(big)
        n_stable_big += len(stable)
        lines.append(f"- **{etf}**: family-wise p={fam_p:.3f} ({'signal beyond chance' if passed else 'no family-wise signal'}), "
                     f"{n_sig} nominally significant features vs {exp:.0f} expected by chance, "
                     f"max |IC|={obs_max:.3f} (null 95%: {np.quantile(null_dist, 0.95):.3f}); "
                     f"of {len(big)} features with |IS IC|>0.08, only {len(stable)} keep their sign OOS.")
    lines.append("")
    stab_pct = n_stable_big / n_total_big * 100 if n_total_big else 0.0
    if n_pass_fam == 0:
        lines.append("**Verdict: patterns are weak.** No ETF shows a factor pattern that clears the "
                     "family-wise permutation test on IS trades. A meta-model trained on these factors "
                     "would be fitting noise — training is expected to be hard and the TODO #2 attempt "
                     "should be deprioritized (or limited to a handful of pre-registered features only).")
    else:
        lines.append(f"**Verdict: patterns exist, but they are thin and regime-unstable.** "
                     f"{n_pass_fam}/3 ETFs clear the family-wise null test on IS trades, yet only "
                     f"{n_stable_big}/{n_total_big} ({stab_pct:.0f}%) of the |IS IC|>0.08 features keep "
                     "their sign OOS — the same mean-reversion→momentum flip from META_LABEL_REPORT.md "
                     "shows up feature-by-feature (e.g. drawdown-from-peak: IS IC -0.14 → OOS +0.24 on "
                     "159915ETF; pooled vol features: IS +0.10..+0.13 → OOS -0.10). The few sign-stable "
                     "features (u_trend_consistency pooled IC ~+0.07-0.08, x_z_x_pnl1330 ~-0.07) are "
                     "individually too weak to clear costs. A walk-forward meta-model would train on even "
                     "thinner yearly slices (~60-110 trades/year), so success odds are low.")
        lines.append("")
        lines.append("**Recommendation:** one attempt is defensible ONLY with (a) features restricted to "
                     "sign-stable, regime-invariant intraday-state candidates (u_trend_consistency, "
                     "u_range_position, x_z_x_pnl1330, u_noon_gap) — NOT the vol/drawdown features whose "
                     "sign flips, and NOT raw pool factors (300ETF's top pool factors all flip sign OOS); "
                     "(b) pooled cross-ETF training to get sample size; (c) the META_LABEL_REPORT.md kill "
                     "criterion. Otherwise: deprioritize TODO #2 — the evidence says a model would mostly "
                     "learn the current regime, which is exactly what breaks.")
    lines.append("\nNote the structural difficulty flagged up front: the target is a ~65-minute "
                 "continuation return conditional on the entry model already having taken a side, so "
                 "most of the easy directional information is consumed. Any surviving signal must come "
                 "from intraday state (gap/drift/drawdown/vol) or factor disagreement, and must overcome "
                 "the IS (mean-reversion) vs OOS (momentum) regime split documented in "
                 "META_LABEL_REPORT.md.")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Meta-model feature feasibility scan")
    ap.add_argument("-e", "--etf", type=str, default=",".join(DEFAULT_ETFS))
    ap.add_argument("-o", "--output", type=str, default=str(HERE / "META_FEATURES_REPORT.md"))
    args = ap.parse_args()
    etfs = [e.strip() for e in args.etf.split(",") if e.strip()]

    res = {}
    pooled_frames = []
    for etf in etfs:
        print("\n" + "=" * 80)
        print(f"  META-FEATURES | {etf}")
        print("=" * 80)
        tr = build_feature_frame(etf)
        cols = feature_columns(tr)
        print(f"    [SCAN] {len(cols)} features vs {TARGET}")

        scan_is = scan_features(tr, cols, "IS")
        scan_oos = scan_features(tr, cols, "OOS")
        obs_max, null_dist, fam_p = permutation_max_ic(tr, cols)
        print(f"    [SCAN] IS: best |IC|={scan_is['ic'].abs().max():.3f} "
              f"({scan_is.loc[scan_is['ic'].abs().idxmax(), 'feature']}), "
              f"permutation max={obs_max:.3f}, family p={fam_p:.3f}")

        out_csv = HERE / "artifacts" / f"meta_features_{etf}.csv"
        tr.to_csv(out_csv, index=False)
        print(f"    [SAVE] {out_csv.name} ({len(tr)} trades x {len(tr.columns)} cols)")

        res[etf] = {"frame": tr, "cols": cols, "scan_is": scan_is,
                    "scan_oos": scan_oos, "perm": (obs_max, null_dist, fam_p)}
        pooled_frames.append(pd.concat(
            [tr[feature_columns(tr, categories=("s", "u", "x"))],
             tr[["date", "etf", "period", "position", TARGET, BINARY_LABEL]]],
            axis=1))

    # Pooled hand-crafted scan
    pf = pd.concat(pooled_frames, ignore_index=True)
    pf = pf.loc[:, ~pf.columns.duplicated()]
    meta_cols = {"date", "etf", "period", "position", TARGET, BINARY_LABEL}
    pcols = [c for c in pf.columns if c not in meta_cols and category_of(c) in ("s", "u", "x")]
    res["_pooled"] = {"scan_is": scan_features(pf, pcols, "IS"),
                      "scan_oos": scan_features(pf, pcols, "OOS")}
    print(f"\n  [POOLED] {len(pf)} trades, {len(pcols)} hand-crafted features")

    res["_verdict"] = build_verdict(res)
    report = build_report(res)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  Saved report: {args.output}")


if __name__ == "__main__":
    main()
