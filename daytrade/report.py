"""Report generation for long_model / short_model architecture.

Per-ETF sections show:
  - Combined metrics (long+short trades together)
  - Long-only metrics (long_model deployed)
  - Short-only metrics (short_model deployed)
  - Per-side year-by-year Sharpe
  - Cost sensitivity per side
  - Cluster confusion (Rally/Selloff/Neutral recovery)
  - Equity curves (combined + per-side)

Output: daytrade/REPORT.md + daytrade/plots/*.png + daytrade/data/results.json
"""
from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from . import ETFS, DECISION_BAR, EXIT_BAR, DEFAULT_COST_BPS, HOLDOUT_START, DAYTRADING_DATA
from .backtest import backtest_long_short, split_holdout, load_5m
from .scores import compute_scores, load_features

PKG_DIR = Path(__file__).resolve().parent
PLOTS_DIR = PKG_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = PKG_DIR / "data" / "results.json"
REPORT_PATH = PKG_DIR / "REPORT.md"
CALIB_PATH = PKG_DIR / "data" / "calibration.json"


def _sharpe(rets):
    if len(rets) < 2 or np.std(rets, ddof=1) == 0:
        return float("nan")
    return float(np.mean(rets) / np.std(rets, ddof=1) * np.sqrt(252))


def _max_dd_bps(rets):
    if len(rets) == 0:
        return float("nan")
    cum = np.insert(np.cumsum(rets), 0, 0.0)
    return float(np.min(cum - np.maximum.accumulate(cum)) * 1e4)


def _trading_day_counts(etf: str) -> tuple[int, int]:
    """Return (n_full_days, n_oos_days) from the feature parquet index.
    Used as the denominator for placement rate.
    """
    feats = load_features(etf)
    cutoff = pd.Timestamp(HOLDOUT_START)
    n_full = len(feats)
    n_oos = int((feats.index >= cutoff).sum())
    return n_full, n_oos


def _placement_rate(n_trades: int, n_days: int) -> float:
    """Fraction of trading days on which the side fired (capital deployment rate)."""
    if n_days <= 0:
        return float("nan")
    return 100.0 * n_trades / n_days


def load_best_configs() -> dict:
    """Return {etf: {"long": cfg_or_None, "short": cfg_or_None}}."""
    if not CALIB_PATH.exists():
        raise SystemExit("Run `python -m daytrade.calibrate` first.")
    data = json.load(open(CALIB_PATH))
    return {etf: v for etf, v in data["results"].items()}


def run_deployed_backtest(etf: str, cfg: dict, cost_bps: float) -> dict:
    """Run backtest with deployed long/short configs from calibration."""
    long_cfg = cfg.get("long")
    short_cfg = cfg.get("short")
    long_thr = long_cfg["threshold_pct"] if long_cfg else 0.0
    long_conv = long_cfg["conviction_pct"] if long_cfg else 0.0
    short_thr = short_cfg["threshold_pct"] if short_cfg else 0.0
    short_conv = short_cfg["conviction_pct"] if short_cfg else 0.0

    r = backtest_long_short(
        etf,
        long_threshold_pct=long_thr, long_conviction_pct=long_conv,
        short_threshold_pct=short_thr, short_conviction_pct=short_conv,
        cost_bps=cost_bps,
        long_enabled=bool(long_cfg), short_enabled=bool(short_cfg),
    )
    return r


def _label_clusters(etf: str) -> pd.DataFrame:
    csv = DAYTRADING_DATA / f"clusters_{etf}_macro.csv"
    if not csv.exists():
        return pd.DataFrame()
    cl = pd.read_csv(csv)
    cl["date"] = pd.to_datetime(cl["date"])
    feats = load_features(etf)
    joined = cl.merge(feats[["pm_return"]], left_on="date", right_index=True, how="inner")
    means = joined.groupby("cluster")["pm_return"].mean()
    order = means.sort_values()
    selloff_c = order.index[0]
    rally_c = order.index[-1]
    neutral_cs = [c for c in means.index if c not in (selloff_c, rally_c)]
    cmap = {rally_c: "Rally", selloff_c: "Selloff"}
    for c in neutral_cs:
        cmap[c] = "Neutral"
    cl["label"] = cl["cluster"].map(cmap)
    return cl[["date", "label"]]


def cost_sweep_per_side(configs: dict) -> pd.DataFrame:
    rows = []
    for cost in [5.0, 15.0, 30.0]:
        for etf, cfg in configs.items():
            r = run_deployed_backtest(etf, cfg, cost_bps=cost)
            t = r["trades"]
            if len(t) == 0:
                continue
            is_, oos = split_holdout(t)
            for side in ["long", "short"]:
                side_oos = oos[oos["direction"] == (1 if side == "long" else -1)]
                if len(side_oos) == 0:
                    continue
                rets = side_oos["net_ret"].values
                rows.append({
                    "cost_bps": cost, "etf": etf, "side": side,
                    "n_oos": len(side_oos),
                    "oos_sharpe": _sharpe(rets),
                    "oos_pnl_bps": float(rets.sum() * 1e4),
                })
    return pd.DataFrame(rows)


def plot_equity_curves(data: dict, cost_bps: float):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
    for ax, side, sign in [(axes[0], "Long", 1), (axes[1], "Short", -1)]:
        for etf, r in data.items():
            t = r["trades"]
            t = t[t["direction"] == sign]
            if len(t) == 0:
                continue
            cum = (1 + t["net_ret"]).cumprod()
            ax.plot(t.index, cum, label=etf, lw=1.3)
        ax.axvline(pd.Timestamp(HOLDOUT_START), color="k", ls="--", alpha=0.5)
        ax.set_title(f"{side} side (cost={cost_bps:.0f} bps RT)")
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(alpha=0.3)
        ax.set_ylabel("Cumulative return per trade")
    plt.tight_layout()
    p = PLOTS_DIR / "equity_curves.png"
    plt.savefig(p, dpi=110)
    plt.close()
    return p


def plot_combined_equity(data: dict, cost_bps: float):
    fig, ax = plt.subplots(figsize=(10, 5))
    for etf, r in data.items():
        t = r["trades"]
        if len(t) == 0:
            continue
        cum = (1 + t["net_ret"]).cumprod()
        label = etf
        cfg = data_configs.get(etf, {})
        sides = []
        if cfg.get("long"): sides.append("L")
        if cfg.get("short"): sides.append("S")
        if sides:
            label += f" ({'+'.join(sides)})"
        ax.plot(t.index, cum, label=label, lw=1.3)
    ax.axvline(pd.Timestamp(HOLDOUT_START), color="k", ls="--", alpha=0.5,
               label=f"Holdout ({HOLDOUT_START})")
    ax.set_title(f"Combined equity curves (cost={cost_bps:.0f} bps RT)")
    ax.set_ylabel("Cumulative return per trade")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    p = PLOTS_DIR / "equity_combined.png"
    plt.savefig(p, dpi=110)
    plt.close()
    return p


def plot_yearly_sharpe_per_side(data: dict, configs: dict):
    years = sorted({t.year for r in data.values() for t in r["trades"].index
                    if t >= pd.Timestamp(HOLDOUT_START)})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, side, sign in [(axes[0], "Long", 1), (axes[1], "Short", -1)]:
        deployed = [etf for etf in configs if configs[etf].get(side.lower())]
        if not deployed:
            ax.set_title(f"{side}: no deployments")
            continue
        width = 0.8 / max(len(deployed), 1)
        x = np.arange(len(years))
        for i, etf in enumerate(deployed):
            t = data[etf]["trades"]
            t = t[(t["direction"] == sign) & (t.index >= pd.Timestamp(HOLDOUT_START))]
            cells = []
            for y in years:
                yr = t[t.index.year == y]["net_ret"].values
                cells.append(_sharpe(yr) if len(yr) > 1 else float("nan"))
            ax.bar(x + i * width, cells, width, label=etf)
        ax.set_xticks(x + width * (len(deployed) - 1) / 2)
        ax.set_xticklabels(years)
        ax.axhline(0, color="k", lw=0.7)
        ax.set_title(f"{side} OOS Sharpe by year")
        ax.set_ylabel("Annualized Sharpe")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    p = PLOTS_DIR / "yearly_sharpe.png"
    plt.savefig(p, dpi=110)
    plt.close()
    return p


def cluster_confusion(data: dict) -> pd.DataFrame:
    rows = []
    for etf, r in data.items():
        cl = _label_clusters(etf)
        if cl.empty:
            continue
        t = r["trades"]
        oos = t[t.index >= pd.Timestamp(HOLDOUT_START)]
        for side, sign in [("long", 1), ("short", -1)]:
            sd = oos[oos["direction"] == sign]
            if len(sd) == 0:
                continue
            merged = sd.reset_index().merge(cl, on="date", how="left")
            total = len(merged)
            if total == 0:
                continue
            counts = merged["label"].value_counts().to_dict()
            rows.append({
                "etf": etf, "side": side, "n_oos": total,
                "Rally%": 100 * counts.get("Rally", 0) / total,
                "Selloff%": 100 * counts.get("Selloff", 0) / total,
                "Neutral%": 100 * counts.get("Neutral", 0) / total,
            })
    return pd.DataFrame(rows)


# Populated by generate() for use in plot_combined_equity
data_configs: dict = {}


def generate():
    global data_configs
    configs = load_best_configs()
    data_configs = configs
    print("Running deployed backtest at 15 bps...")
    data = {etf: run_deployed_backtest(etf, cfg, DEFAULT_COST_BPS)
            for etf, cfg in configs.items()}
    cost_df = cost_sweep_per_side(configs)
    cluster_df = cluster_confusion(data)
    eq_split = plot_equity_curves(data, DEFAULT_COST_BPS)
    eq_comb = plot_combined_equity(data, DEFAULT_COST_BPS)
    yr_path = plot_yearly_sharpe_per_side(data, configs)

    L = []
    L.append("# Daytrade — Frozen-Linear Intraday Alpha (Long/Short Model)\n")
    L.append("*Signal = frozen LASSO/Huber coefficients from day-model. "
             "Each ETF deploys independent `long_model` and `short_model`, "
             "each with its own expanding-percentile thresholds. "
             "Entry at decision bar (9:45 for 159915/500; 10:00 for 300/50/588000). "
             f"Exit at 14:30 (5m bar {EXIT_BAR}). "
             f"Cost {DEFAULT_COST_BPS:.0f} bps round-trip.*\n")

    L.append("\n## 1. Strategy\n")
    L.append("- **Signal**: frozen LASSO/Huber/ElasticNet score from `day-model/models/linear_{ETF}.joblib`")
    L.append("- **Per-side thresholds**: expanding-window percentile of |score| computed only over that side's prior history (no look-ahead)")
    L.append("- **Direction**: `long_model` fires when score>0 & crosses long thresholds; `short_model` fires when score<0 & crosses short thresholds")
    L.append("- **Eligibility guard**: each side deployed only if OOS P&L>0 AND OOS Sharpe>0 AND n≥20 (else disabled)")
    L.append("- **Entry bar**: 9:45 close for 159915/500; 10:00 close for 300/50/588000")
    L.append(f"- **Exit bar**: {EXIT_BAR} (5m close at 14:30, better liquidity than 15:00)")
    L.append(f"- **Cost**: {DEFAULT_COST_BPS:.0f} bps round-trip (parametrizable)")
    L.append(f"- **Holdout**: {HOLDOUT_START} onwards (matches day-model)\n")

    L.append("\n## 2. Deployed Configurations\n")
    L.append("| ETF | Long thr | Long conv | Short thr | Short conv |")
    L.append("|-----|----------|-----------|-----------|------------|")
    for etf in ETFS:
        cfg = configs.get(etf, {})
        lg = cfg.get("long"); sh = cfg.get("short")
        lstr = f"{lg['threshold_pct']:.0f} | {lg['conviction_pct']:.0f}" if lg else "disabled | —"
        sstr = f"{sh['threshold_pct']:.0f} | {sh['conviction_pct']:.0f}" if sh else "disabled | —"
        L.append(f"| **{etf}** | {lstr} | {sstr} |")

    L.append("\n## 3. Performance (15 bps round-trip)\n")
    L.append("### 3.1 Per-Side OOS Metrics\n")
    L.append("*Place%* = side trades / total trading days in the period (capital deployment rate).\n")
    L.append("| ETF | Side | N OOS | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps |")
    L.append("|-----|------|-------|--------|------|--------|---------|-----------|----------|")
    for etf, r in data.items():
        t = r["trades"]
        oos = t[t.index >= pd.Timestamp(HOLDOUT_START)]
        _, n_oos_days = _trading_day_counts(etf)
        for side, sign in [("long", 1), ("short", -1)]:
            sd = oos[oos["direction"] == sign]
            if len(sd) == 0:
                continue
            rets = sd["net_ret"].values
            L.append(f"| {etf} | `{side}` | {len(sd)} | "
                     f"{_placement_rate(len(sd), n_oos_days):.1f}% | "
                     f"{float((rets>0).mean()):.1%} | "
                     f"{_sharpe(rets):+.2f} | {rets.sum()*1e4:+.0f} | "
                     f"{_max_dd_bps(rets):+.0f} | {np.mean(rets)*1e4:+.1f} |")

    L.append("\n### 3.2 Combined (Long+Short) Per ETF\n")
    L.append("| ETF | N (full) | N OOS | L Place% | S Place% | Tot Place% | Win% | "
             "Sharpe (full) | P&L bps (full) | OOS Sharpe | OOS P&L bps | OOS MaxDD bps |")
    L.append("|-----|----------|-------|----------|----------|------------|------|"
             "---------------|----------------|------------|-------------|---------------|")
    for etf, r in data.items():
        t = r["trades"]
        if len(t) == 0:
            L.append(f"| {etf} | 0 | — | — | — | — | — | — | — | — | — | — |")
            continue
        n_full_days, n_oos_days = _trading_day_counts(etf)
        is_, oos = split_holdout(t)
        oos_rets = oos["net_ret"].values
        # Per-side placement rates (OOS)
        long_oos_n = int((oos["direction"] > 0).sum())
        short_oos_n = int((oos["direction"] < 0).sum())
        l_place = _placement_rate(long_oos_n, n_oos_days)
        s_place = _placement_rate(short_oos_n, n_oos_days)
        tot_place = _placement_rate(len(oos), n_oos_days)
        # Per-side placement rates (full) for the "L Place% / S Place% (full)" alt view
        L.append(f"| **{etf}** | {len(t)} | {len(oos)} | "
                 f"{l_place:.1f}% | {s_place:.1f}% | {tot_place:.1f}% | "
                 f"{float((t['net_ret']>0).mean()):.1%} | "
                 f"{_sharpe(t['net_ret'].values):+.2f} | "
                 f"{t['net_ret'].sum()*1e4:+.0f} | "
                 f"{_sharpe(oos_rets):+.2f} | {oos_rets.sum()*1e4:+.0f} | "
                 f"{_max_dd_bps(oos_rets):+.0f} |")

    L.append("\n### 3.3 Placement Rates (capital deployment frequency)\n")
    L.append("Fraction of trading days on which each side fires. "
             "High Place% × high Sharpe = dense edge; low Place% × high Sharpe = sparse but selective.\n")
    L.append("| ETF | Long Place% (full) | Long Place% (OOS) | "
             "Short Place% (full) | Short Place% (OOS) | Total Place% (OOS) |")
    L.append("|-----|--------------------|-------------------|"
             "---------------------|---------------------|--------------------|")
    for etf in ETFS:
        if etf not in data:
            continue
        t = data[etf]["trades"]
        n_full_days, n_oos_days = _trading_day_counts(etf)
        if len(t) == 0 or n_full_days == 0:
            L.append(f"| {etf} | — | — | — | — | — |")
            continue
        is_, oos = split_holdout(t)
        # Full
        l_full = _placement_rate(int((t["direction"] > 0).sum()), n_full_days)
        s_full = _placement_rate(int((t["direction"] < 0).sum()), n_full_days)
        # OOS
        l_oos = _placement_rate(int((oos["direction"] > 0).sum()), n_oos_days)
        s_oos = _placement_rate(int((oos["direction"] < 0).sum()), n_oos_days)
        tot_oos = _placement_rate(len(oos), n_oos_days)
        L.append(f"| **{etf}** | {l_full:.1f}% | {l_oos:.1f}% | "
                 f"{s_full:.1f}% | {s_oos:.1f}% | {tot_oos:.1f}% |")

    L.append("\n### 3.4 Year-by-Year OOS Sharpe\n")
    years = sorted({t.year for r in data.values() for t in r["trades"].index
                    if t >= pd.Timestamp(HOLDOUT_START)})
    L.append("| ETF | Side | " + " | ".join(str(y) for y in years) + " |")
    L.append("|-----|------|" + "---|" * len(years))
    for etf, r in data.items():
        t = r["trades"]
        oos = t[t.index >= pd.Timestamp(HOLDOUT_START)]
        for side, sign in [("long", 1), ("short", -1)]:
            sd = oos[oos["direction"] == sign]
            if len(sd) == 0:
                continue
            cells = []
            for y in years:
                yr = sd[sd.index.year == y]["net_ret"].values
                cells.append(f"{_sharpe(yr):+.2f}" if len(yr) > 1 else "—")
            L.append(f"| {etf} | `{side}` | " + " | ".join(cells) + " |")
    L.append(f"\n![yearly_sharpe]({yr_path.relative_to(PKG_DIR)})\n")

    L.append("\n### 3.5 Cost Sensitivity (OOS Sharpe by side)\n")
    if len(cost_df):
        L.append("| ETF | Side | 5 bps | 15 bps | 30 bps |")
        L.append("|-----|------|-------|--------|--------|")
        for etf in ETFS:
            for side in ["long", "short"]:
                row = cost_df[(cost_df["etf"] == etf) & (cost_df["side"] == side)]
                if len(row) == 0:
                    continue
                vals = {int(r["cost_bps"]): r["oos_sharpe"] for _, r in row.iterrows()}
                if not any(np.isnan(v) for v in vals.values()):
                    pass
                cells = " | ".join(
                    f"{vals.get(c, float('nan')):+.2f}" if not np.isnan(vals.get(c, float('nan'))) else "—"
                    for c in [5, 15, 30]
                )
                L.append(f"| {etf} | `{side}` | {cells} |")

    L.append("\n### 3.6 Equity Curves\n")
    L.append(f"![equity_combined]({eq_comb.relative_to(PKG_DIR)})\n")
    L.append(f"![equity_per_side]({eq_split.relative_to(PKG_DIR)})\n")

    L.append("\n## 4. Diagnostic: Cluster Confusion (OOS traded days)\n")
    L.append("Of days traded on each side, what fraction belonged to day-trading's "
             "discovered Rally/Selloff/Neutral clusters? Long side should concentrate on Rally; "
             "short side on Selloff.\n")
    if len(cluster_df):
        L.append("| ETF | Side | N OOS | Rally% | Selloff% | Neutral% |")
        L.append("|-----|------|-------|--------|----------|----------|")
        for _, row in cluster_df.iterrows():
            L.append(f"| {row['etf']} | `{row['side']}` | {row['n_oos']} | "
                     f"{row['Rally%']:.0f}% | {row['Selloff%']:.0f}% | {row['Neutral%']:.0f}% |")
    else:
        L.append("_cluster labels not available_")

    L.append("\n## 5. Verdict\n")
    # Auto-classify based on per-side robustness
    robust_long = []
    robust_short = []
    for etf, cfg in configs.items():
        l = cfg.get("long"); s = cfg.get("short")
        if l and l.get("oos_sharpe", 0) >= 2.0:
            robust_long.append(etf)
        if s and s.get("oos_sharpe", 0) >= 2.0:
            robust_short.append(etf)
    L.append(f"- **Robust long_model (OOS Sharpe ≥ +2.0)**: {', '.join(robust_long) or 'none'}")
    L.append(f"- **Robust short_model (OOS Sharpe ≥ +2.0)**: {', '.join(robust_short) or 'none'}")
    L.append(f"- **Disabled long**: {', '.join(e for e in ETFS if not configs.get(e,{}).get('long')) or 'none'}")
    L.append(f"- **Disabled short**: {', '.join(e for e in ETFS if not configs.get(e,{}).get('short')) or 'none'}")

    L.append("\n## 6. Caveats\n")
    L.append("- Short-side P&L assumes zero execution friction (options/margin costs not modeled)")
    L.append("- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability")
    L.append("- 14:30 exit leaves late-day continuation on the table; v2 will add trailing stop")
    L.append("- No position sizing (fixed notional); drawdowns are per-unit-notional")
    L.append("- Per-side eligibility uses holdout (2024-03+); earlier years may behave differently")
    L.append("- Single cost assumption (15bps RT) applied to both long and short; real-world shorts via options will carry different (likely higher) cost")

    REPORT_PATH.write_text("\n".join(L))
    print(f"Report → {REPORT_PATH}")

    out = {
        "cost_bps": DEFAULT_COST_BPS,
        "holdout_start": HOLDOUT_START,
        "configs": configs,
        "combined_metrics": {
            etf: {k: v for k, v in r.items() if k != "trades"}
            for etf, r in data.items()
        },
        "cost_sweep": cost_df.to_dict(orient="records"),
        "cluster_confusion": cluster_df.to_dict(orient="records"),
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"Results JSON → {RESULTS_PATH}")


if __name__ == "__main__":
    generate()
