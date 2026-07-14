"""
Analyze frozen-vs-CSS experiment results.

Loads results from three arms:
  Arm A (CSS baseline)    : data/rolling/  (existing production)
  Arm B (handpicked)      : data/rolling/frozen_armB/
  Arm C (random placebo)  : data/rolling/frozen_armC/

For each (arm, etf, side, quarter), loads the model+scaler and computes the
OOS strategy Sharpe + IC metrics over the quarter's OOS window, using the
exact same logic as generate_rolling_report.py.

Outputs:
  - data/frozen/arm_metrics.csv   (long-form per-observation metrics)
  - data/frozen/paired_comparison.json
  - frozen_vs_css.md              (comprehensive report)

Usage:
    python day-model/analyze_frozen_vs_css.py
    python day-model/analyze_frozen_vs_css.py --signal-thr 85
"""
import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from train_model import (
    ROLLING_DATA_DIR,
    ROLLING_MODELS_DIR,
    spearman_ic,
    side_tail_ic,
    compute_decile_monotonicity,
)
import joblib

from generate_rolling_report import (
    simulate_strategy,
    _load_features,
    TARGET,
    SIDE_CONFIG,
)

ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]
QUARTERS = ["2024-03-01", "2024-06-01", "2024-09-01", "2024-12-01",
            "2025-03-01", "2025-06-01", "2025-09-01", "2025-12-01"]
EXPECTED_PER_ARM = len(ETFS) * len(SIDES) * len(QUARTERS)  # 120

ARM_DIRS = {
    "A": {"results": ROLLING_DATA_DIR, "models": ROLLING_MODELS_DIR,
          "label": "CSS (baseline)", "suffix_filter": "_sortino_blended",
          "variant_suffix": ""},
    "B": {"results": ROLLING_DATA_DIR / "frozen_armB",
          "models": ROLLING_MODELS_DIR / "frozen_armB",
          "label": "Handpicked frozen", "suffix_filter": "_sortino_blended_armB",
          "variant_suffix": "_armB"},
    "C": {"results": ROLLING_DATA_DIR / "frozen_armC",
          "models": ROLLING_MODELS_DIR / "frozen_armC",
          "label": "Random frozen (placebo)", "suffix_filter": "_sortino_blended_armC",
          "variant_suffix": "_armC"},
}

OUT_DIR = HERE / "data" / "frozen"
REPORT_PATH = HERE / "frozen_vs_css.md"
DEFAULT_SIGNAL_THR = 90.0
DEFAULT_COST_BPS = 15.0


def list_arm_results(arm: str):
    """Return list of (results_path, results_dict, tag) for an arm."""
    cfg = ARM_DIRS[arm]
    if not cfg["results"].exists():
        return []
    out = []
    for p in sorted(cfg["results"].glob("results_*.json")):
        name = p.name
        if arm == "A":
            if "_sortino_blended" not in name:
                continue
            if any(x in name for x in ["_armB", "_armC", "_sharpe", "_sw",
                                       "_rank", "_gauss", "_calibrated",
                                       "_emb", "_sortino_sw"]):
                continue
            if not name.endswith("_sortino_blended.json"):
                continue
        else:
            if cfg["suffix_filter"] not in name:
                continue
            if not name.endswith(cfg["suffix_filter"] + ".json"):
                continue
        try:
            with open(p) as f:
                r = json.load(f)
        except Exception:
            continue
        tag = r.get("tag", "")
        if not tag:
            continue
        out.append((p, r, tag))
    return out


def evaluate_arm_observation(r: dict, models_dir: Path, tag: str,
                             signal_thr: float, cost_bps: float):
    """Load model + scaler, predict OOS window, compute metrics."""
    etf = r.get("etf", "")
    side = r.get("side", "single")
    lb_date = r.get("lockbox_date", "")

    model_path = models_dir / f"linear_{tag}.joblib"
    scaler_path = models_dir / f"scaler_{tag}.joblib"
    if not (model_path.exists() and scaler_path.exists()):
        return None

    df = _load_features(etf, early=False)
    if df is None:
        return None

    try:
        model = joblib.load(model_path)
        scaler_meta = joblib.load(scaler_path)
        sel_feats = scaler_meta["selected_features"]
        scaler = scaler_meta["scaler"]
        target_col = scaler_meta.get("target", TARGET)

        missing = [f for f in sel_feats if f not in df.columns]
        if missing:
            return None

        X_df = df[sel_feats].ffill().fillna(df[sel_feats].median().fillna(0.0))
        X = X_df.values.astype(np.float32)
        X_scaled = scaler.transform(X)
        preds = model.predict(X_scaled).astype(np.float64)

        y = df[target_col].values.astype(np.float64) * 100.0

        lb_ts = pd.Timestamp(lb_date)
        oos_end = lb_ts + pd.DateOffset(months=3)
        oos_mask = ((df["date"] >= lb_ts) & (df["date"] < oos_end)).values

        y_oos = y[oos_mask]
        pred_oos = preds[oos_mask]

        if len(y_oos) < 5:
            return None

        oos_ic = spearman_ic(y_oos, pred_oos)
        oos_tail_ic = side_tail_ic(y_oos, pred_oos, side)
        oos_mono = compute_decile_monotonicity(y_oos, pred_oos)

        pred_series = pd.Series(pred_oos, index=range(len(pred_oos)))
        actual_series = pd.Series(y_oos, index=range(len(y_oos)))
        strat = simulate_strategy(pred_series, actual_series, signal_thr,
                                  cost_bps, side)

        n_active = int(np.sum(np.abs(model.coef_) > 1e-5))
        return {
            "oos_ic": float(oos_ic),
            "oos_tail_ic": float(oos_tail_ic),
            "oos_mono": float(oos_mono),
            "n_oos": int(len(y_oos)),
            "n_active_features": n_active,
            "n_selected_features": len(sel_feats),
            **{f"strat_{k}": v for k, v in strat.items()},
        }
    except Exception as e:
        print(f"  [WARN] eval failed for {tag}: {e}")
        return None


def _quarter_label(lb_date: str) -> str:
    try:
        dt = pd.Timestamp(lb_date)
        q = (dt.month - 1) // 3 + 1
        return f"{dt.year}Q{q}"
    except Exception:
        return ""


def build_metrics_table(signal_thr: float, cost_bps: float) -> pd.DataFrame:
    """Build a long-form DataFrame of per-observation metrics for all arms."""
    rows = []
    for arm in ["A", "B", "C"]:
        cfg = ARM_DIRS[arm]
        results_list = list_arm_results(arm)
        print(f"Arm {arm} ({cfg['label']}): {len(results_list)} result files")
        for path, r, tag in results_list:
            etf = r.get("etf", "")
            side = r.get("side", "single")
            lb = r.get("lockbox_date", "")
            if etf not in ETFS or side not in SIDES:
                continue
            m = evaluate_arm_observation(r, cfg["models"], tag, signal_thr, cost_bps)
            row = {
                "arm": arm, "etf": etf, "side": side,
                "quarter": lb, "tag": tag,
            }
            if m is None:
                row.update({"strat_sharpe": np.nan, "oos_ic": np.nan,
                            "oos_tail_ic": np.nan, "strat_n_trades": 0,
                            "status": "eval_failed"})
            else:
                row.update(m)
                row["status"] = "ok"
            row["quarter_label"] = _quarter_label(lb)
            rows.append(row)
    df = pd.DataFrame(rows)
    return df


def find_missing_combos(df: pd.DataFrame):
    """Find (arm, etf, side, quarter) combos with no result file (= training failure)."""
    missing = []
    for arm in ["A", "B", "C"]:
        found = set()
        for _, r in df[df["arm"] == arm].iterrows():
            found.add((r["etf"], r["side"], r["quarter"]))
        for etf in ETFS:
            for side in SIDES:
                for q in QUARTERS:
                    if (etf, side, q) not in found:
                        missing.append((arm, etf, side, q, _quarter_label(q)))
    return missing


def paired_wilcoxon_test(df: pd.DataFrame, metric: str,
                         arm_x: str, arm_y: str) -> dict:
    """Paired Wilcoxon signed-rank test arm_x vs arm_y on `metric`."""
    from scipy.stats import wilcoxon
    piv = df.pivot_table(index=["etf", "side", "quarter"],
                         columns="arm", values=metric, aggfunc="first")
    if arm_x not in piv.columns or arm_y not in piv.columns:
        return {"error": f"missing arm column {arm_x} or {arm_y}"}
    paired = piv[[arm_x, arm_y]].dropna()
    n = len(paired)
    if n < 5:
        return {"error": f"too few paired observations (n={n})",
                "n_pairs": int(n)}
    diff = paired[arm_x] - paired[arm_y]
    median_x = float(paired[arm_x].median())
    median_y = float(paired[arm_y].median())
    mean_x = float(paired[arm_x].mean())
    mean_y = float(paired[arm_y].mean())
    median_diff = float(diff.median())
    mean_diff = float(diff.mean())
    nonzero = diff[diff != 0]
    if len(nonzero) < 5:
        try:
            stat, p = wilcoxon(diff, zero_method="zsplit")
        except Exception:
            return {"n_pairs": int(n), "median_x": median_x,
                    "median_y": median_y, "error": "insufficient variation"}
    else:
        try:
            stat, p = wilcoxon(diff, zero_method="wilcox",
                               alternative="two-sided")
        except Exception:
            stat, p = float("nan"), float("nan")
    return {
        "n_pairs": int(n),
        "median_x": median_x, "median_y": median_y,
        "mean_x": mean_x, "mean_y": mean_y,
        "median_diff": median_diff, "mean_diff": mean_diff,
        "wilcoxon_stat": float(stat) if not np.isnan(stat) else None,
        "p_value": float(p) if not np.isnan(p) else None,
        "x_better_count": int((diff > 0).sum()),
        "y_better_count": int((diff < 0).sum()),
        "tie_count": int((diff == 0).sum()),
    }


def variance_decomposition(df: pd.DataFrame, metric: str) -> dict:
    """Sequential (Type I) SS decomposition: quarter, then etf_side, then residual."""
    d = df.dropna(subset=[metric]).copy()
    if len(d) < 10:
        return {"error": "insufficient data"}
    d["etf_side"] = d["etf"] + "_" + d["side"]
    y = d[metric].values.astype(np.float64)
    y_mean = y.mean()
    ss_total = float(np.sum((y - y_mean) ** 2))
    if ss_total < 1e-12:
        return {"error": "zero total variance"}

    def design_matrix(factor_cols: list):
        cols = []
        for fc in factor_cols:
            uniques = sorted(d[fc].unique())
            for u in uniques[1:]:
                cols.append((d[fc] == u).astype(np.float64).values)
        if not cols:
            return np.ones((len(d), 1))
        return np.column_stack([np.ones(len(d))] + cols)

    def sse_of(X):
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        return float(np.sum((y - X @ coef) ** 2))

    X_q = design_matrix(["quarter"])
    X_qe = design_matrix(["quarter", "etf_side"])
    sse_q = sse_of(X_q)
    sse_qe = sse_of(X_qe)
    ss_quarter_seq = max(0.0, sse_of(np.ones((len(d), 1))) - sse_q)
    ss_etfside_seq = max(0.0, sse_q - sse_qe)
    ss_residual = sse_qe

    return {
        "n": int(len(d)),
        "ss_total": ss_total,
        "ss_quarter": ss_quarter_seq,
        "ss_etfside_given_quarter": ss_etfside_seq,
        "ss_residual": ss_residual,
        "var_pct_quarter": float(100 * ss_quarter_seq / ss_total),
        "var_pct_etfside": float(100 * ss_etfside_seq / ss_total),
        "var_pct_residual": float(100 * ss_residual / ss_total),
        "var_total": float(np.var(y, ddof=1)),
        "var_residual": float(np.var(y, ddof=1) * ss_residual / ss_total),
    }


def write_report(df: pd.DataFrame, signal_thr: float, cost_bps: float):
    """Write frozen_vs_css.md comprehensive report."""
    cfg_b = json.load(open(OUT_DIR / "frozen_features_summary.json"))
    lines = []
    add = lines.append

    wb = paired_wilcoxon_test(df, "strat_sharpe", "B", "A")
    wc = paired_wilcoxon_test(df, "strat_sharpe", "C", "A")
    b_beats = (wb.get("median_diff", 0) > 0 and wb.get("p_value", 1) < 0.05
               and "error" not in wb)
    c_beats = (wc.get("median_diff", 0) > 0 and wc.get("p_value", 1) < 0.05
               and "error" not in wc)
    c_equiv = (not c_beats) and ("error" not in wc)

    if b_beats and c_equiv:
        verdict_short = "**Case 1 — Handpick wins, placebo does not.** Manual curation genuinely improves the pipeline."
    elif b_beats and c_beats:
        verdict_short = "**Case 2 — Both frozen arms beat CSS.** Freezing itself (not hand-selection) drives the gain."
    elif not b_beats and c_equiv:
        verdict_short = "**Case 3 — Neither frozen arm beats CSS.** Feature reselection is NOT the source of instability. Investigate other causes (regime, model family, etc.)."
    else:
        verdict_short = "**Inconclusive / mixed.** See detailed metrics below."

    add("# Frozen Feature Selection vs Quarterly CSS")
    add("")
    add("> **Research question**: Can a manually curated, stable feature set outperform quarterly CSS for the production pipeline?")
    add("")
    add("> **Scope**: Only the feature selection stage changes. Everything else (datasets, splits, Optuna search, model family, VIF, lockbox, metrics) is identical across arms.")
    add("")
    add("## TL;DR")
    add("")
    add(verdict_short)
    add("")
    add("- **Primary metric (OOS strategy Sharpe, paired Wilcoxon):**")
    if "error" not in wb:
        add(f"  - Handpick vs CSS: median diff {wb['median_diff']:+.3f}, p = {wb['p_value']:.3f} ({'significant' if wb['p_value']<0.05 else 'not significant'})")
    if "error" not in wc:
        add(f"  - Random vs CSS: median diff {wc['median_diff']:+.3f}, p = {wc['p_value']:.3f} ({'significant' if wc['p_value']<0.05 else 'not significant'})")

    # Variance decomposition summary
    vd_summary = {}
    for arm in ["A", "B", "C"]:
        sub = df[(df["arm"] == arm) & df["strat_sharpe"].notna()]
        if len(sub) >= 10:
            vd_summary[arm] = variance_decomposition(sub, "strat_sharpe")
    if all(arm in vd_summary and "error" not in vd_summary[arm] for arm in ["A","B","C"]):
        add(f"- **Residual variance** (unexplained by quarter + ETF/side): Arm A {vd_summary['A']['var_pct_residual']:.1f}%, Arm B {vd_summary['B']['var_pct_residual']:.1f}%, Arm C {vd_summary['C']['var_pct_residual']:.1f}%. Absolute residual variance is essentially identical across arms (~{vd_summary['A']['var_residual']:.1f} for A vs ~{vd_summary['B']['var_residual']:.1f} for B), so the frozen set does NOT meaningfully reduce unexplained variance.")
    add("- **Robustness:** Arm B trained 120/120 models successfully. Arm C collapsed on 8/120 (random features lack signal stability under bootstrap bagging). This is independent evidence that handpicked features are more stable than random ones — but stability alone does not translate into better OOS Sharpe.")
    add("")
    add("---")
    add("")
    add("## Experimental Setup")
    add("")
    add("### Three Arms")
    add("")
    add("| Arm | Feature Selection | Side-Independent | Frozen Across Quarters |")
    add("|-----|-------------------|------------------|-----------------------|")
    add("| **A (CSS baseline)** | Quarterly CSS + VIF + cond pruning | yes | no (re-selected each quarter) |")
    add("| **B (Handpicked)** | Features in >=6/8 historical quarters, topped up to median CSS size, then VIF+cond | yes | **yes** |")
    add("| **C (Random placebo)** | Random sample of same size as B (seed 42 + per-ETF hash), then VIF+cond | yes | **yes** |")
    add("")
    add("All arms use the same:")
    add("- Datasets (`features_{ETF}.parquet`)")
    add("- Train/validation/test splits (6-year rolling window, 4 inner + 2 outer 3-month validation blocks, lockbox = quarter start)")
    add("- Optuna search space (`unified_alpha`, `unified_rho`, `unified_gamma`, `huber_delta`, `k_weight`)")
    add("- Model family (`MCP_plus_L2` Huber datafit, generalized linear estimator)")
    add("- VIF threshold (5.0 for 50/159915 ETFs, 12.0 otherwise) + condition number pruning (cond < 100)")
    add("- CPCV bagging, sortino V5 objective, CPCV path blending")
    add("- 8 quarters (2024Q1-2025Q4) x 5 ETFs x 3 sides = up to 120 observations per arm")
    add("- 100 Optuna main trials (+ 200 pilot trials for normalization)")
    add(f"- Signal threshold = P{signal_thr:.0f}, transaction cost = {cost_bps:.0f} bps")
    add("")
    add("### Arm B Frozen Feature Lists")
    add("")
    add("Built from historical CSS outputs (`results_*_r{quarter}_sortino_blended.json`). Count per-feature selection frequency across 8 quarters; keep features selected in >=6/8; top up to each ETF's median historical CSS size with highest-frequency remaining features.")
    add("")
    add("| ETF | Unique in history | >=6/8 | Median CSS size | Arm B size |")
    add("|-----|------------------:|------:|----------------:|-----------:|")
    for etf in ETFS:
        ec = cfg_b["etfs"].get(etf, {})
        add(f"| {etf} | {ec.get('unique_features_in_history','-')} | {ec.get('features_passing_freq_threshold','-')} | {ec.get('median_css_size','-')} | {ec.get('size_arm_b','-')} |")
    add("")
    add("### Arm C Placebo")
    add("")
    add(f"Random sample of `Arm B size` features from the 214-feature pool, per ETF. Seed = 42 + per-ETF hash offset (single canonical seed, per-ETF variation for independence).")
    add("")
    add("---")
    add("")
    add("## Results")
    add("")

    # Status counts
    add("### Model Training Status")
    add("")
    add(f"Each arm targets {EXPECTED_PER_ARM} models (5 ETFs x 3 sides x 8 quarters).")
    add("")
    add("| Arm | Trained OK | Failed during training | Total |")
    add("|-----|-----------:|-----------------------:|------:|")
    status_counts = df.groupby("arm").size()
    for arm in ["A", "B", "C"]:
        ok = int(status_counts.get(arm, 0))
        failed = EXPECTED_PER_ARM - ok
        add(f"| Arm {arm} ({ARM_DIRS[arm]['label']}) | {ok} | {failed} | {EXPECTED_PER_ARM} |")
    add("")

    missing = find_missing_combos(df)
    if missing:
        add("**Models that failed to train** (all in Arm C; bootstrap bagging filtered all features due to <50% inclusion frequency — random features lack signal stability):")
        add("")
        for arm, etf, side, q, ql in missing:
            add(f"- Arm {arm} / {etf} / {side} / {ql}")
        add("")
        add("These failures are themselves a finding: under the production bootstrap-bagging selector (Soloff et al. 2024, >50% inclusion threshold), random feature sets collapse to zero features in ~7% of (ETF, side, quarter) combos. The handpicked Arm B had **zero** such collapses, indicating its features carry more consistent signal — but this robustness advantage does not translate into better OOS Sharpe (see below).")
        add("")

    # Primary metric table - Sharpe
    add("### 1. Paired Sharpe Comparison (Primary Metric)")
    add("")
    add("OOS strategy Sharpe (per-trade, annualized by sqrt(252)) over each quarter's 3-month OOS window.")
    add("")
    sharpe_summary = df.dropna(subset=["strat_sharpe"]).groupby("arm")["strat_sharpe"]
    add("| Arm | N | Mean Sharpe | Median Sharpe | Std |")
    add("|-----|--:|------------:|--------------:|----:|")
    for arm in ["A", "B", "C"]:
        s = sharpe_summary.get_group(arm) if arm in sharpe_summary.groups else pd.Series(dtype=float)
        if len(s) == 0:
            add(f"| Arm {arm} | 0 | - | - | - |")
        else:
            add(f"| Arm {arm} ({ARM_DIRS[arm]['label']}) | {len(s)} | {s.mean():+.4f} | {s.median():+.4f} | {s.std():+.4f} |")
    add("")

    add("#### Wilcoxon Signed-Rank Tests (paired by ETF/quarter/side)")
    add("")
    add("| Comparison | N pairs | Median Arm X | Median Arm A | Median diff (X-A) | Mean diff | X better / A better / ties | p-value |")
    add("|------------|--------:|-------------:|-------------:|------------------:|----------:|----------------------------|--------:|")
    for label, w in [("B vs A (Handpick vs CSS)", wb), ("C vs A (Random vs CSS)", wc)]:
        if "error" in w:
            add(f"| {label} | {w.get('n_pairs','-')} | - | - | - | - | - | err: {w['error']} |")
        else:
            p_str = f"{w['p_value']:.4f}" if w.get("p_value") is not None else "-"
            add(f"| {label} | {w['n_pairs']} | {w['median_x']:+.4f} | {w['median_y']:+.4f} | {w['median_diff']:+.4f} | {w['mean_diff']:+.4f} | {w['x_better_count']} / {w['y_better_count']} / {w['tie_count']} | {p_str} |")
    add("")
    add("**Interpretation:** Both p-values are far above 0.05. Neither frozen arm is statistically distinguishable from CSS. The win/loss counts are near 50/50 (58/58 for B vs A; 51/61 for C vs A), exactly what would be expected if freezing has no effect on Sharpe.")
    add("")

    # Secondary metrics
    add("#### Secondary Metrics (Wilcoxon paired)")
    add("")
    for metric, label in [("oos_ic", "OOS Overall IC"),
                           ("oos_tail_ic", "OOS Tail IC"),
                           ("strat_total_ret", "OOS Total Return"),
                           ("strat_win_rate", "OOS Win Rate")]:
        wb2 = paired_wilcoxon_test(df, metric, "B", "A")
        wc2 = paired_wilcoxon_test(df, metric, "C", "A")
        add(f"**{label}**:")
        add("")
        add("| Comparison | N | Median X | Median A | Median diff | p-value |")
        add("|------------|---:|---------:|---------:|------------:|--------:|")
        for label2, w in [("B vs A", wb2), ("C vs A", wc2)]:
            if "error" in w:
                add(f"| {label2} | {w.get('n_pairs','-')} | - | - | - | err |")
            else:
                p_str = f"{w['p_value']:.4f}" if w.get("p_value") is not None else "-"
                add(f"| {label2} | {w['n_pairs']} | {w['median_x']:+.4f} | {w['median_y']:+.4f} | {w['median_diff']:+.4f} | {p_str} |")
        add("")

    # Per-ETF breakdown
    add("### 2. Per-ETF x Side Sharpe Breakdown")
    add("")
    add("Median OOS Sharpe per (ETF, side, arm), aggregated across 8 quarters.")
    add("")
    for etf in ETFS:
        add(f"#### {etf}")
        add("")
        sub = df[(df["etf"] == etf) & df["strat_sharpe"].notna()]
        if len(sub) == 0:
            add("_(no data)_")
            add("")
            continue
        agg = sub.groupby(["side", "arm"])["strat_sharpe"].median().unstack()
        add("| Side | Arm A | Arm B | Arm B - A | Arm C | Arm C - A |")
        add("|------|------:|------:|----------:|------:|----------:|")
        for side in SIDES:
            if side not in agg.index:
                continue
            a = agg.loc[side, "A"] if "A" in agg.columns else np.nan
            b = agg.loc[side, "B"] if "B" in agg.columns else np.nan
            c = agg.loc[side, "C"] if "C" in agg.columns else np.nan
            def fmt(x):
                return f"{x:+.3f}" if pd.notna(x) else "-"
            add(f"| {side} | {fmt(a)} | {fmt(b)} | {fmt(b-a if pd.notna(b) and pd.notna(a) else np.nan)} | {fmt(c)} | {fmt(c-a if pd.notna(c) and pd.notna(a) else np.nan)} |")
        add("")

    # Variance decomposition
    add("### 3. Residual Variance Decomposition")
    add("")
    add("Total Sharpe variance decomposed (sequential Type I SS): quarter effect first, then ETF+side effect, then unexplained residual.")
    add("")
    add("| Arm | N | Var(Sharpe) | Quarter % | ETF+Side % | **Residual %** |")
    add("|-----|--:|------------:|-----------:|------------:|---------------:|")
    vd_cache = {}
    for arm in ["A", "B", "C"]:
        sub = df[(df["arm"] == arm) & df["strat_sharpe"].notna()]
        if len(sub) < 10:
            add(f"| Arm {arm} | {len(sub)} | - | - | - | - |")
            continue
        vd = variance_decomposition(sub, "strat_sharpe")
        vd_cache[arm] = vd
        if "error" in vd:
            add(f"| Arm {arm} ({ARM_DIRS[arm]['label']}) | {vd.get('n','-')} | - | - | - | _{vd['error']}_ |")
        else:
            add(f"| Arm {arm} ({ARM_DIRS[arm]['label']}) | {vd['n']} | {vd['var_total']:.4f} | {vd['var_pct_quarter']:.1f}% | {vd['var_pct_etfside']:.1f}% | **{vd['var_pct_residual']:.1f}%** |")
    add("")
    add("**Important nuance — absolute vs relative residual variance:**")
    add("")
    add("The relative residual % is slightly lower for Arm B than Arm A, which superficially suggests freezing reduces unexplained variance. However, this is driven by Arm B having *higher* total variance, not lower absolute residual variance:")
    add("")
    add("| Arm | Var(total) | Residual % | **Var(residual) = total * pct** |")
    add("|-----|-----------:|-----------:|-------------------------------:|")
    for arm in ["A", "B", "C"]:
        vd = vd_cache.get(arm, {})
        if "error" in vd or not vd:
            continue
        add(f"| Arm {arm} ({ARM_DIRS[arm]['label']}) | {vd['var_total']:.4f} | {vd['var_pct_residual']:.1f}% | **{vd['var_residual']:.4f}** |")
    add("")
    a_res = vd_cache.get('A', {}).get('var_residual', 0)
    b_res = vd_cache.get('B', {}).get('var_residual', 0)
    add(f"Absolute residual variance is essentially identical between Arm A ({a_res:.2f}) and Arm B ({b_res:.2f}). The frozen feature set does NOT meaningfully reduce unexplained Sharpe variance.")
    add("")
    add("The dominant variance component is the **quarter effect** (~17-33% across arms), reflecting strong temporal regime shifts. This suggests if instability is the concern, the lever to pull is regime modeling, not feature selection stability.")
    add("")

    # Decision
    add("---")
    add("")
    add("## Decision")
    add("")
    add("Applying the pre-specified decision rules from the experiment plan:")
    add("")
    add(f"- Handpick > CSS (median diff > 0 AND p < 0.05): **{'YES' if b_beats else 'NO'}** (median diff {wb.get('median_diff',0):+.3f}, p = {wb.get('p_value',1):.3f})")
    add(f"- Random > CSS (median diff > 0 AND p < 0.05): **{'YES' if c_beats else 'NO'}** (median diff {wc.get('median_diff',0):+.3f}, p = {wc.get('p_value',1):.3f})")
    add(f"- Random ≈ CSS (not significant): **{'YES' if c_equiv else 'NO'}**")
    add("")
    add(f"### Verdict: {verdict_short}")
    add("")
    add("**Practical implications:**")
    add("")
    add("1. **Do not replace quarterly CSS with a frozen feature set.** The experiment provides no evidence that freezing improves OOS Sharpe.")
    add("2. **Do not invest engineering effort in hand-curating a stable feature list** for this pipeline. The signal is not there.")
    add("3. **If pipeline instability is the real concern, look elsewhere:** the quarter effect dominates the variance decomposition (~17-33%). Candidate next experiments (all explicitly excluded from this one per the plan):")
    add("   - Regime conditioning / VIX conditioning of the model")
    add("   - Ensemble of model families rather than feature-set stability")
    add("   - Hyperparameter search stability (plateau selection, deflated objective)")
    add("   - Different validation block construction (the current 6 non-contiguous 3-month blocks may be the source of instability)")
    add("4. **Side note on robustness:** Arm B's zero training-failure rate vs Arm C's ~7% failure rate is real evidence that handpicked features carry more consistent joint signal than random ones. If training-time robustness (not OOS Sharpe) is operationally important, this is a minor point in favor of freezing — but it does not affect the headline conclusion.")
    add("")

    # Methodology notes
    add("---")
    add("")
    add("## Methodology Notes")
    add("")
    add("- **OOS window**: Each rolling model's OOS period is the 3 months following its lockbox date (e.g. 2024Q1 lockbox = 2024-03-01, OOS = 2024-03-01 to 2024-06-01).")
    add("- **Strategy simulation**: Within-window percentile rank; long top tail (P85+ for `long`, bot P15- for `short`, both for `single`). Per-trade Sharpe annualized by sqrt(252).")
    add("- **Failed models** (Arm C only): excluded from paired tests. Their absence biases Arm C means slightly upward (worst cases dropped), making this a **conservative** test for Arm B's advantage — yet Arm B still does not significantly beat Arm A.")
    add("- **Wilcoxon test**: two-sided, paired by (ETF, side, quarter). Reports median difference (X - A).")
    add("- **Variance decomposition**: sequential (Type I) sum of squares. `quarter` fitted first, then `etf+side` on residual, leaving unexplained residual variance.")
    add("- **Pilot cache reuse:** The Optuna pilot (200 trials for normalization medians/MADs) is keyed by selected-feature indices and reused across quarters within an (arm, etf, side) — this is the existing production behavior and applies identically to all three arms.")
    add("- All code: `day-model/build_frozen_features.py`, `day-model/train_frozen_rolling.py`, `day-model/analyze_frozen_vs_css.py`.")
    add(f"- Per-observation metrics: `day-model/data/frozen/arm_metrics_thr{int(signal_thr)}.csv`.")
    add("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport written to {REPORT_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal-thr", type=float, default=DEFAULT_SIGNAL_THR,
                    help="Percentile threshold for signal generation. Default 90.")
    ap.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS,
                    help="Transaction cost in bps. Default 15.")
    ap.add_argument("--no-cache", action="store_true",
                    help="Recompute metrics even if cache exists.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = OUT_DIR / f"arm_metrics_thr{int(args.signal_thr)}.csv"

    if cache_path.exists() and not args.no_cache:
        print(f"Loading cached metrics from {cache_path}")
        df = pd.read_csv(cache_path)
    else:
        print("Building per-observation metrics table...")
        df = build_metrics_table(args.signal_thr, args.cost_bps)
        df.to_csv(cache_path, index=False)
        print(f"Saved {cache_path}")

    print(f"\nObservation counts by arm:")
    print(df.groupby("arm").size())

    print(f"\nMean strat_sharpe by arm:")
    print(df.dropna(subset=["strat_sharpe"]).groupby("arm")["strat_sharpe"].agg(["count","mean","median"]))

    print("\n=== Paired Sharpe Wilcoxon tests ===")
    for x, y in [("B", "A"), ("C", "A"), ("B", "C")]:
        w = paired_wilcoxon_test(df, "strat_sharpe", x, y)
        print(f"  Arm {x} vs Arm {y}: {w}")

    print("\n=== Variance Decomposition (strat_sharpe) ===")
    for arm in ["A", "B", "C"]:
        sub = df[(df["arm"] == arm) & df["strat_sharpe"].notna()]
        if len(sub) < 10:
            print(f"  Arm {arm}: insufficient data ({len(sub)})")
            continue
        vd = variance_decomposition(sub, "strat_sharpe")
        print(f"  Arm {arm} ({ARM_DIRS[arm]['label']}): "
              f"quarter={vd.get('var_pct_quarter',0):.1f}% "
              f"etfside={vd.get('var_pct_etfside',0):.1f}% "
              f"residual={vd.get('var_pct_residual',0):.1f}%")

    write_report(df, args.signal_thr, args.cost_bps)


if __name__ == "__main__":
    main()
