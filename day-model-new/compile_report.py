#!/usr/bin/env python3
"""
Compile BASELINE_REPORT.md from existing JSON outputs.

Reads from day-model-new/data/:
  - results_{ETF}_{side}{suffix}.json       (Stage B metrics)
  - selected_pool_{ETF}_{side}{suffix}.json (admitted features + recipes)
  - mining_attempts_{ETF}_{side}{suffix}.json (filter funnel counts + per-feature details)

Standalone: no pipeline execution, no numba imports. Runs in <1s.
"""

import argparse
import json
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

ETFS = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

ADAPTIVE_DATES = {
    "588000ETF": ("2020-11-01", "2025-01-01", "2025-01-01", "2025-07-01"),
    "_default":  ("2015-01-01", "2022-01-01", "2022-01-01", "2024-03-01"),
}


def _load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _verdict_counts(attempts):
    """Aggregate verdict counts. Returns dict keyed by short verdict family."""
    counts = Counter()
    for item in attempts:
        v = item.get("verdict", "UNKNOWN")
        if v.startswith("ADMITTED_REPLACED"):
            counts["ADMITTED_REPLACED"] += 1
        elif v.startswith("ADMITTED"):
            counts["ADMITTED"] += 1
        elif v.startswith("DROPPED_REPLACED"):
            counts["DROPPED_REPLACED"] += 1
        else:
            counts[v] += 1
    return counts


def _fmt_ci(low, high):
    return f"[{low:+.4f}, {high:+.4f}]"


def _fmt_metric_with_ci(value, ci, span_zero_flag=True):
    """Format metric + CI; append * if CI spans zero."""
    s = f"{value:+.4f}"
    if span_zero_flag and ci[0] * ci[1] <= 0:
        s += "*"
    return s, _fmt_ci(ci[0], ci[1])


def _metrics_row(etf, side, n_feats, metrics):
    """Build one row of a metrics table."""
    o_ic, o_ci = _fmt_metric_with_ci(metrics["overall_ic"], metrics["overall_ic_ci"])
    t_ic, t_ci = _fmt_metric_with_ci(metrics["tail_ic"], metrics["tail_ic_ci"])
    mono = metrics["monotonicity"]
    raw_ann = metrics.get("raw_ann_ret")
    raw_ann_str = f"{raw_ann * 100:.2f}%" if raw_ann is not None else "N/A"
    raw_sharpe = metrics.get("raw_sharpe")
    raw_sharpe_str = f"{raw_sharpe:.4f}" if raw_sharpe is not None else "N/A"
    cost_ann_str = f"{metrics['ann_ret'] * 100:.2f}%"
    cost_sharpe_str = f"{metrics['sharpe']:.4f}"
    return (
        f"| {etf} | {side} | {n_feats} | "
        f"{o_ic} | {o_ci} | "
        f"{t_ic} | {t_ci} | "
        f"{mono:+.4f} | "
        f"{raw_ann_str} | "
        f"{raw_sharpe_str} | "
        f"{cost_ann_str} | "
        f"{cost_sharpe_str} | "
        f"{metrics['sortino']:.4f} | "
        f"{metrics['max_dd']*100:.2f}% |"
    )


def build_report(etfs, sides, suffix):
    """Return list of markdown lines."""
    lines = []

    # ── Header ─────────────────────────────────────────────────────────
    lines.extend([
        "# Day-Model Rewrite v3 — Baseline Performance Report",
        "",
        f"Suffix: `{suffix or '(none)'}`",
        "",
        "Pipeline: select_features.py (Stage A: filter funnel) → evaluate_concept.py (Stage B: IC-weighted model)",
        "",
    ])
    for etf in etfs:
        train_start, train_end, oos_start, lock_start = ADAPTIVE_DATES.get(etf, ADAPTIVE_DATES["_default"])
        lines.append(f"- **{etf}**: Train `{train_start}` → `{train_end}` | Holdout OOS from `{oos_start}` | Lockbox from `{lock_start}`")
    lines.extend([
        "",
        "_\\* indicates the 95% circular block-bootstrap CI spans zero (statistically indistinguishable from noise)._",
        "_Note: Cost metrics incorporate 8 bps (0.0008) transaction cost per position state transition (realistic for liquid ETFs). Raw metrics represent pre-cost performance. Absolute-sign kill switches enforce mean return positivity on traded legs._",
    ])

    # ── Section 1: Filter Funnel ───────────────────────────────────────
    lines.extend([
        "",
        "## 1. Filter Funnel",
        "",
        "Candidate counts at each admission gate. Shows where features get pruned.",
        "",
        "| ETF | Side | Total Candidates | 7Y-Jackknife Pass | B2 Rolling Guard | Temporal Gate | BH-FDR Pass | B3 Composite Floor | Stability Gate | Quality Gate | B4 Correlation | Final Admitted |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for etf in etfs:
        for side in sides:
            att_path = DATA_DIR / f"mining_attempts_{etf}_{side}{suffix}.json"
            attempts = _load_json(att_path)
            if attempts is None:
                continue
            counts = _verdict_counts(attempts)
            total = len(attempts)
            sh_pass = total - counts.get("REJECTED_SPLIT_HALF", 0)
            # rolling-guard survivors = sh_pass - rg_rejects
            rg_survivors = sh_pass - counts.get("REJECTED_ROLLING_GUARD", 0)
            # Temporal gate rejects are subset of rolling-guard survivors
            temporal_survivors = rg_survivors - counts.get("REJECTED_TEMPORAL", 0)
            # FDR rejects are subset of temporal survivors
            fdr_survivors = temporal_survivors - counts.get("REJECTED_FDR_GATE", 0)
            # B3 Composite Floor rejects
            b3_survivors = fdr_survivors - counts.get("REJECTED_ADMISSION_FLOOR", 0)
            # Stability Gate rejects
            stab_survivors = b3_survivors - counts.get("REJECTED_STABILITY_GATE", 0)
            # Quality Gate rejects
            qual_survivors = stab_survivors - counts.get("REJECTED_QUALITY_GATE", 0)
            # B4 Correlation Gate rejects
            admitted = counts.get("ADMITTED", 0) + counts.get("ADMITTED_REPLACED", 0)
            final_pool = admitted - counts.get("DROPPED_REPLACED", 0)
            lines.append(
                f"| {etf} | {side} | {total:,} | {sh_pass:,} | {rg_survivors:,} | {temporal_survivors:,} | {fdr_survivors:,} "
                f"| {b3_survivors:,} | {stab_survivors:,} | {qual_survivors:,} | {admitted:,} | {final_pool} |"
            )

    # ── Section 2: Training-Period Metrics ─────────────────────────────
    lines.extend([
        "",
        "## 2. Training-Period Performance (in-sample)",
        "",
        "IC-weighted combination model on the training window. Useful for sanity-checking fit.",
        "",
        "| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |",
        "| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for etf in etfs:
        for side in sides:
            res = _load_json(DATA_DIR / f"results_{etf}_{side}{suffix}.json")
            if res is None:
                continue
            if not res.get("training_metrics"):
                continue
            n_feats = len(res["features_selected"])
            lines.append(_metrics_row(etf, side, n_feats, res["training_metrics"]))

    # ── Section 3: Holdout OOS Metrics ─────────────────────────────────
    lines.extend([
        "",
        "## 3. Holdout OOS Performance",
        "",
        "Out-of-sample from holdout start to present.",
        "",
        "| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |",
        "| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for etf in etfs:
        for side in sides:
            res = _load_json(DATA_DIR / f"results_{etf}_{side}{suffix}.json")
            if res is None:
                continue
            if not res.get("oos_metrics"):
                continue
            n_feats = len(res["features_selected"])
            lines.append(_metrics_row(etf, side, n_feats, res["oos_metrics"]))

    # ── Section 4: Lockbox Metrics ─────────────────────────────────────
    lines.extend([
        "",
        "## 4. OOS Lockbox Performance",
        "",
        "Most recent OOS window (lockbox start to present). Strictest generalization test.",
        "",
        "| ETF | Side | Features | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Raw Ann. Ret | Raw Sharpe | Cost Ann. Ret | Cost Sharpe | Sortino | Max DD |",
        "| :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for etf in etfs:
        for side in sides:
            res = _load_json(DATA_DIR / f"results_{etf}_{side}{suffix}.json")
            if res is None:
                continue
            if not res.get("lockbox_metrics"):
                continue
            n_feats = len(res["features_selected"])
            lines.append(_metrics_row(etf, side, n_feats, res["lockbox_metrics"]))

    # ── Section 5: Admitted Features (full details) ────────────────────
    lines.extend([
        "",
        "## 5. Admitted Features — Full Details",
        "",
        "Per ETF/side: every admitted feature with its quality metrics. `raw_ic` and `p_value` come from the",
        "BH-FDR pre-filter stage; `deflated_ic` is overall_ic adjusted for empirical null mean.",
        "",
    ])
    for etf in etfs:
        for side in sides:
            pool_path = DATA_DIR / f"selected_pool_{etf}_{side}{suffix}.json"
            pool = _load_json(pool_path)
            if pool is None:
                continue

            lines.append(f"### {etf} / {side}")
            if not pool:
                lines.extend(["No features admitted.", ""])
                continue

            # Cross-reference mining_attempts to pull raw_ic + p_value for admitted features
            att_path = DATA_DIR / f"mining_attempts_{etf}_{side}{suffix}.json"
            attempts = _load_json(att_path) or []
            admitted_lookup = {}
            for a in attempts:
                if a.get("verdict", "").startswith("ADMITTED") and "feature_name" in a:
                    admitted_lookup[a["feature_name"]] = a

            lines.extend([
                "",
                "| Feature | Sign | Raw IC | Overall IC | Deflated IC | p-value | IC IR | Monotonicity | Max Corr |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ])
            for item in sorted(pool, key=lambda x: -x.get("overall_ic", 0)):
                fname = item["feature_name"]
                extra = admitted_lookup.get(fname, {})
                raw_ic = extra.get("raw_ic", float("nan"))
                p_val = extra.get("p_value", float("nan"))
                max_corr = extra.get("max_corr", 0.0)
                lines.append(
                    f"| `{fname}` | {item['sign']:+d} | "
                    f"{raw_ic:+.4f} | {item['overall_ic']:+.4f} | {item['deflated_ic']:+.4f} | "
                    f"{p_val:.4f} | {item['ic_ir']:+.4f} | {item['monotonicity']:+.4f} | {max_corr:.3f} |"
                )
            lines.append("")

    # ── Section 6: Recipe Definitions ──────────────────────────────────
    lines.extend([
        "## 6. Recipe Definitions (combo_ features only)",
        "",
        "For each admitted combo feature, shows the operation and component base features.",
        "Recipes are resolved using training-set statistics (mean/std/median) to prevent lookahead leakage.",
        "",
    ])
    recipe_seen = set()
    for etf in etfs:
        for side in sides:
            pool_path = DATA_DIR / f"selected_pool_{etf}_{side}{suffix}.json"
            pool = _load_json(pool_path)
            if not pool:
                continue

            for item in pool:
                if "recipe" not in item:
                    continue
                fname = item["feature_name"]
                if fname in recipe_seen:
                    continue
                recipe_seen.add(fname)

            # No per-ETF separation in this section since names are unique;
            # we collect all combos across ETFs in one block.

    if recipe_seen:
        lines.extend([
            "| Feature | Op | Components |",
            "| :--- | :--- | :--- |",
        ])
        # Walk pools again to preserve order (sorted by etf, side, then overall_ic)
        for etf in etfs:
            for side in sides:
                pool_path = DATA_DIR / f"selected_pool_{etf}_{side}{suffix}.json"
                pool = _load_json(pool_path) or []
                for item in sorted(pool, key=lambda x: -x.get("overall_ic", 0)):
                    if "recipe" not in item:
                        continue
                    fname = item["feature_name"]
                    r = item["recipe"]
                    op = r.get("op", "?")
                    parts = []
                    for key in ["feature_a", "feature_b", "feature_c", "feature_cond", "feature_cond2"]:
                        if key in r:
                            parts.append(f"{key.replace('feature_', '')}=`{r[key]}`")
                    components = ", ".join(parts) if parts else "_(none)_"
                    lines.append(f"| `{fname}` | `{op}` | {components} |")
        lines.append("")

    return lines


def main():
    parser = argparse.ArgumentParser(description="Compile BASELINE_REPORT.md from existing JSON outputs.")
    parser.add_argument("-e", "--etf", default="all", help="ETF or 'all'")
    parser.add_argument("-s", "--side", default="all", help="Side or 'all'")
    parser.add_argument("--early", action="store_true", help="Use early window dataset suffix")
    parser.add_argument("--period-suffix", type=str, default=None, help="Period suffix for multi-period runs (e.g., _p2015_2023)")
    parser.add_argument("-o", "--output", default=None, help="Output path (default: day-model-new/BASELINE_REPORT{suffix}.md)")
    args = parser.parse_args()

    etfs = ETFS if args.etf == "all" else [args.etf]
    sides = SIDES if args.side == "all" else [args.side]
    suffix = args.period_suffix or ("_early" if args.early else "")

    lines = build_report(etfs, sides, suffix)
    out_path = Path(args.output) if args.output else (HERE / f"BASELINE_REPORT{suffix}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote report ({len(lines)} lines) to {out_path}")


if __name__ == "__main__":
    main()
