"""
Standalone evaluation report generator for Gating Models.

Reads the canonical promoted reports `report_{ETF}_{side}.json` (which carry the
auto-selected winner per cell) plus the full per-config reports
`report_{ETF}_{side}_{variant}_{selector}.json` and compiles:
  1. Winner summary (chosen variant × selector × honest OOS metrics).
  2. Full grid: forward_wf PR-AUC across all variants × selectors per cell.
  3. Per-cell selection reasoning + deployability.
  4. Diagnostic plot references.

Outputs:
  - day-model/gating_model/GATING_REPORT.md
  - tradability_model_report.md (project root mirror)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATING_DIR = HERE / "gating_model"
ROOT_REPORT = HERE.parent / "tradability_model_report.md"

ETFS = ["50ETF", "300ETF", "500ETF", "588000ETF", "159915ETF"]
SIDES = ["long", "short"]
VARIANTS = ["two_sided", "joint3", "gated"]
SELECTORS = ["none", "stability", "lgbm"]


def _load(path: Path):
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def _best_entry(rep):
    """Return (model_type, results_dict) for the chosen best model in a report."""
    best_mt = rep["best_model_type"]
    res = rep["results"].get(best_mt, {})
    return best_mt, res


def _wf(res):
    """Forward walk-forward estimate (preferred) or fall back to dev_only_oos."""
    wf = res.get("forward_wf_estimate")
    if wf:
        return wf
    # joint3 side-flattened report
    return res.get("dev_only_oos") or {}


def _dev_oos(res):
    return res.get("dev_only_oos") or res.get("dev_only_oos_long") or res.get("dev_only_oos_short") or {}


def _cv(res):
    return res.get("cv_metrics") or res.get("cv_long") or res.get("cv_short") or {}


def _deployable(wf, cv=None):
    """Apply the deployability rule using honest WF metrics."""
    if not wf:
        return "—"
    auc_ok = wf.get("auc", 0.5) > 0.53
    base = wf.get("base_rate", 0.0)
    prauc_ok = wf.get("pr_auc", 0.0) > base
    prec = wf.get("precision_at_thr", 0.0)
    lift_ok = prec > base * 1.1
    return "Yes" if (auc_ok and prauc_ok and lift_ok) else "No"


def generate_report():
    md = []
    md.append("# Gating Model Report\n")
    md.append(
        "Per-side big-move gating classifiers (long = big-up tail, short = "
        "big-down tail) used as a veto filter over the daytrade linear score. "
        "Three target variants (`two_sided`, `joint3`, `gated`) × three feature "
        "selectors (`none`/all features, `stability`, `lgbm`) are benchmarked; the "
        "best per ETF × side is auto-selected by honest walk-forward OOS PR-AUC.\n"
    )
    md.append(
        "Metrics: **WF** = pooled purged walk-forward over the full dataset "
        "(deployed-model proxy, `forward_wf_estimate`); **HO** = dev-trained "
        "model evaluated on the 20% chronological holdout (`dev_only_oos`).\n"
    )

    # ── Section 1: Winner summary ──────────────────────────────────────────
    md.append("## 1. Winner per ETF × side (auto-selected)\n")
    md.append(
        "| ETF | Side | Variant | Selector | Model | #Feat | FireThr | "
        "WF PR-AUC | WF AUC | WF Prec@70 | HO PR-AUC | Deployable |"
    )
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")

    for etf in ETFS:
        for side in SIDES:
            rep = _load(GATING_DIR / f"report_{etf}_{side}.json")
            if not rep:
                continue
            best_mt, res = _best_entry(rep)
            wf = _wf(res)
            dev = _dev_oos(res)
            variant = rep.get("chosen_variant", rep.get("variant", "?"))
            selector = rep.get("chosen_selector", rep.get("selector", "?"))
            n_feat = rep.get("n_features", "?")
            fire = rep.get("firing_threshold")
            fire_str = f"{fire:.3f}" if isinstance(fire, (int, float)) else "—"
            row = (
                f"| **{etf}** | `{side}` | `{variant}` | `{selector}` | {best_mt} | "
                f"{n_feat} | {fire_str} | "
                f"{wf.get('pr_auc', 0):.3f} | {wf.get('auc', 0.5):.3f} | "
                f"{wf.get('precision_at_thr', 0):.2%} | "
                f"{dev.get('pr_auc', 0):.3f} | {_deployable(wf)} |"
            )
            md.append(row)

    # ── Section 2: Full grid (forward_wf PR-AUC) ───────────────────────────
    md.append("\n## 2. Full grid — forward walk-forward PR-AUC\n")
    md.append(
        "Each cell shows the WF PR-AUC for every (variant, selector) "
        "combination. `**` marks the chosen winner; `()`: not deployable.\n"
    )
    for side in SIDES:
        md.append(f"\n### Side: `{side}`\n")
        header = "| ETF | " + " | ".join(
            f"{v}/{s}" for v in VARIANTS for s in SELECTORS
        ) + " |"
        md.append(header)
        md.append("|" + "---|" * (1 + len(VARIANTS) * len(SELECTORS)))
        for etf in ETFS:
            cells = []
            winner_tag = None
            canon = _load(GATING_DIR / f"report_{etf}_{side}.json")
            if canon:
                winner_tag = f"{canon.get('chosen_variant')}_{canon.get('chosen_selector')}"
            for v in VARIANTS:
                for s in SELECTORS:
                    rep = _load(GATING_DIR / f"report_{etf}_{side}_{v}_{s}.json")
                    if not rep:
                        cells.append("—")
                        continue
                    _, res = _best_entry(rep)
                    wf = _wf(res)
                    if not wf:
                        cells.append("—")
                        continue
                    val = wf.get("pr_auc", 0.0)
                    deployable = _deployable(wf) == "Yes"
                    tag = f"{val:.3f}"
                    if not deployable:
                        tag = f"({tag})"
                    tag_full = f"{v}_{s}"
                    if tag_full == winner_tag:
                        tag = f"**{tag}**"
                    cells.append(tag)
            md.append(f"| **{etf}** | " + " | ".join(cells) + " |")

    # ── Section 3: Per-cell reasoning ──────────────────────────────────────
    md.append("\n## 3. Selection summary & deployability\n")
    md.append(
        "- **Variant**: `two_sided` = per-side binary big-move; `joint3` = shared "
        "3-class softmax {big_up, neutral, big_down}; `gated` = big-move AND "
        "tradability/regime mask.\n"
        "- **Selector**: `none` = all candidate features; `stability` = regime-stratified "
        "block bootstrap + randomized ElasticNet + OOB IC; `lgbm` = walk-forward "
        "LightGBM gain + permutation importance.\n"
        "- **Deployable**: WF AUC > 0.53 AND WF PR-AUC > base rate AND "
        "WF Prec@70 > 1.1× base rate.\n"
    )
    n_dep = 0
    n_total = 0
    for etf in ETFS:
        for side in SIDES:
            canon = _load(GATING_DIR / f"report_{etf}_{side}.json")
            if not canon:
                continue
            n_total += 1
            best_mt, res = _best_entry(canon)
            wf = _wf(res)
            if _deployable(wf) == "Yes":
                n_dep += 1
    md.append(f"\n**Deployable cells: {n_dep}/{n_total}.**\n")

    # ── Section 4: Plots ───────────────────────────────────────────────────
    md.append("\n## 4. Diagnostic plots\n")
    md.append(
        "ROC + Precision-Recall curves per (ETF × side × variant × selector) "
        "are written to `gating_model/plots/curves_{ETF}_{side}_{variant}_{selector}.png`.\n"
    )

    content = "\n".join(md)
    GATING_DIR.mkdir(parents=True, exist_ok=True)
    out1 = GATING_DIR / "GATING_REPORT.md"
    out2 = ROOT_REPORT
    with open(out1, "w", encoding="utf-8") as f:
        f.write(content)
    with open(out2, "w", encoding="utf-8") as f:
        f.write(content)
    print(content)
    print(f"\nReport written to:\n  1. {out1}\n  2. {out2}")


if __name__ == "__main__":
    generate_report()
