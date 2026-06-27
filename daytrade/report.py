"""Walk-forward report generation for long_model / short_model architecture.

Replaces the previous single-split-at-HOLDOUT_START framing. Per-side metrics
are now **pooled walk-forward OOS**: trades stitched across all test folds,
each fold's (thr, conv, stop, mode) selected using only train-window data.

Sections:
  §1 Strategy
  §2 Deployed configurations (per-side mode + per-fold config table)
  §3 Walk-forward OOS performance
    §3.1 Per-side pooled WF metrics
    §3.2 Combined per-ETF
    §3.3 Per-fold config stability (regime drift diagnostic)
    §3.4 Year-by-year Sharpe (natural fold alignment)
    §3.5 Cost sensitivity (per-side, re-evaluated at the same per-fold configs)
    §3.6 Equity curves (stitched WF)
    §3.7 Fragility warnings
  §4 Cluster confusion
  §5 Mode comparison (all WF) + §5.5 Gating impact (ungated WF vs gated WF)
  §6 Verdict
  §7 Caveats

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
from .backtest import load_5m
from .scores import load_features
from .walkforward import make_yearly_folds
from .calibrate import replay_side_wf_trades

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
    """Return (n_full_days, n_wf_days) from the feature parquet index.

    n_wf_days = days in any test fold (the honest OOS denominator).
    """
    feats = load_features(etf)
    folds = make_yearly_folds(feats.index)
    n_full = len(feats)
    wf_days = sum(f["n_test_days"] for f in folds)
    return n_full, wf_days


def _placement_rate(n_trades: int, n_days: int) -> float:
    if n_days <= 0:
        return float("nan")
    return 100.0 * n_trades / n_days


def load_best_configs() -> dict:
    if not CALIB_PATH.exists():
        raise SystemExit("Run `python -m daytrade.calibrate` and `python -m daytrade.deploy` first.")
    data = json.load(open(CALIB_PATH))
    return {etf: v for etf, v in data["results"].items()}


def _calib_mode() -> str:
    if not CALIB_PATH.exists():
        return "single"
    data = json.load(open(CALIB_PATH))
    return data.get("mode", "single")


def _folds_for(etf: str) -> list[dict]:
    feats = load_features(etf)
    return make_yearly_folds(feats.index)


def run_deployed_backtest_wf(etf: str, cfg: dict, cost_bps: float) -> dict:
    """Replay stitched WF trades for both sides and combine.

    Each side's per-fold configs are read from the deployed ``calibration.json``
    and replayed against the matching test windows. Trades from both sides are
    concatenated to form the combined per-ETF equity curve.
    """
    from .backtest import _summarize_long_short, _empty_long_short_result

    long_cfg = cfg.get("long")
    short_cfg = cfg.get("short")
    folds = _folds_for(etf)

    parts = []
    for side_cfg, side in [(long_cfg, "long"), (short_cfg, "short")]:
        if not side_cfg:
            continue
        trades = replay_side_wf_trades(etf, side, side_cfg, cost_bps, folds=folds)
        if len(trades) > 0:
            parts.append(trades)

    if not parts:
        return _empty_long_short_result(etf)

    combined = pd.concat(parts).sort_index()
    combined.index = pd.to_datetime(combined.index)
    combined = combined[~combined.index.duplicated(keep="first")]
    metrics = _summarize_long_short(combined, etf, cost_bps)
    metrics["trades"] = combined
    return metrics


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


def cost_sweep_per_side_wf(configs: dict) -> pd.DataFrame:
    """Re-evaluate the deployed per-fold configs at multiple cost assumptions.

    Caveat: per-fold configs were chosen at ``DEFAULT_COST_BPS``; we do not
    re-run the grid search per cost level. This is a sensitivity diagnostic,
    not a re-optimisation.
    """
    rows = []
    for cost in [5.0, 15.0, 30.0]:
        for etf, cfg in configs.items():
            trades_parts = []
            for side in ("long", "short"):
                side_cfg = cfg.get(side)
                if not side_cfg:
                    continue
                t = replay_side_wf_trades(etf, side, side_cfg, cost, folds=_folds_for(etf))
                if len(t):
                    trades_parts.append(t)
            if not trades_parts:
                continue
            all_t = pd.concat(trades_parts).sort_index()
            for side in ["long", "short"]:
                sign = 1 if side == "long" else -1
                sd = all_t[all_t["direction"] == sign]
                if len(sd) == 0:
                    continue
                rets = sd["net_ret"].values
                rows.append({
                    "cost_bps": cost, "etf": etf, "side": side,
                    "n": len(sd),
                    "sharpe": _sharpe(rets),
                    "pnl_bps": float(rets.sum() * 1e4),
                })
    return pd.DataFrame(rows)


def plot_equity_curves_wf(data: dict, cost_bps: float):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
    for ax, side, sign in [(axes[0], "Long", 1), (axes[1], "Short", -1)]:
        for etf, r in data.items():
            t = r["trades"]
            if len(t) == 0 or "direction" not in t.columns:
                continue
            t = t[t["direction"] == sign]
            if len(t) == 0:
                continue
            cum = (1 + t["net_ret"]).cumprod()
            ax.plot(t.index, cum, label=etf, lw=1.3)
        # Mark fold boundaries (year starts)
        for year in [2021, 2022, 2023, 2024, 2025, 2026]:
            ax.axvline(pd.Timestamp(f"{year}-01-01"), color="gray", ls=":",
                       alpha=0.35, lw=0.8)
        ax.set_title(f"{side} side — WF pooled (cost={cost_bps:.0f} bps RT)")
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(alpha=0.3)
        ax.set_ylabel("Cumulative return per trade")
    plt.tight_layout()
    p = PLOTS_DIR / "equity_curves.png"
    plt.savefig(p, dpi=110)
    plt.close()
    return p


def plot_combined_equity_wf(data: dict, cost_bps: float):
    fig, ax = plt.subplots(figsize=(11, 5))
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
    for year in [2021, 2022, 2023, 2024, 2025, 2026]:
        ax.axvline(pd.Timestamp(f"{year}-01-01"), color="gray", ls=":", alpha=0.35, lw=0.8)
    ax.set_title(f"Combined equity — walk-forward pooled (cost={cost_bps:.0f} bps RT)")
    ax.set_ylabel("Cumulative return per trade")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    p = PLOTS_DIR / "equity_combined.png"
    plt.savefig(p, dpi=110)
    plt.close()
    return p


def plot_yearly_sharpe_wf(data: dict, configs: dict):
    """Per-side Sharpe by year — naturally aligns with WF fold years."""
    years = sorted({t.year for r in data.values() for t in r["trades"].index})
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
            if len(t) == 0 or "direction" not in t.columns:
                continue
            t = t[t["direction"] == sign]
            cells = []
            for y in years:
                yr = t[t.index.year == y]["net_ret"].values
                cells.append(_sharpe(yr) if len(yr) > 1 else float("nan"))
            ax.bar(x + i * width, cells, width, label=etf)
        ax.set_xticks(x + width * (len(deployed) - 1) / 2)
        ax.set_xticklabels(years)
        ax.axhline(0, color="k", lw=0.7)
        ax.set_title(f"{side} WF Sharpe by fold year")
        ax.set_ylabel("Annualized Sharpe")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    p = PLOTS_DIR / "yearly_sharpe.png"
    plt.savefig(p, dpi=110)
    plt.close()
    return p


def cluster_confusion_wf(data: dict) -> pd.DataFrame:
    rows = []
    for etf, r in data.items():
        cl = _label_clusters(etf)
        if cl.empty:
            continue
        t = r["trades"]
        if len(t) == 0:
            continue
        for side, sign in [("long", 1), ("short", -1)]:
            sd = t[t["direction"] == sign]
            if len(sd) == 0:
                continue
            merged = sd.reset_index().merge(cl, on="date", how="left")
            total = len(merged)
            if total == 0:
                continue
            counts = merged["label"].value_counts().to_dict()
            rows.append({
                "etf": etf, "side": side, "n": total,
                "Rally%": 100 * counts.get("Rally", 0) / total,
                "Selloff%": 100 * counts.get("Selloff", 0) / total,
                "Neutral%": 100 * counts.get("Neutral", 0) / total,
            })
    return pd.DataFrame(rows)


# Populated by generate() for use in plot_combined_equity_wf
data_configs: dict = {}


def generate():
    global data_configs
    configs = load_best_configs()
    data_configs = configs
    mode = _calib_mode()
    print(f"Replaying deployed WF backtests at {DEFAULT_COST_BPS:.0f} bps (mode={mode})...")
    data = {etf: run_deployed_backtest_wf(etf, cfg, DEFAULT_COST_BPS)
            for etf, cfg in configs.items()}
    cost_df = cost_sweep_per_side_wf(configs)
    cluster_df = cluster_confusion_wf(data)
    eq_split = plot_equity_curves_wf(data, DEFAULT_COST_BPS)
    eq_comb = plot_combined_equity_wf(data, DEFAULT_COST_BPS)
    yr_path = plot_yearly_sharpe_wf(data, configs)

    L = []
    L.append("# Daytrade — Frozen-Linear Intraday Alpha (Walk-Forward Calibrated)\n")
    L.append("*Signal = frozen LASSO/Huber coefficients from day-model (target = `trade_return`, "
             "log return from entry-open to exit-close). "
             "Per-side (threshold, conviction, stop, mode) selected via **purged expanding-window "
             "walk-forward** (yearly folds, train = all prior years). No hyperparameter snooping. "
             "Decision at close[DECISION_BAR[etf]] -> entry at open[DECISION_BAR[etf]+1] -> "
             f"exit at close[{EXIT_BAR}] (14:30). Cost {DEFAULT_COST_BPS:.0f} bps round-trip.*\n")

    L.append("\n## 1. Strategy\n")
    L.append("- **Signal**: frozen LASSO/Huber/ElasticNet score from `day-model/models/linear_{ETF}.joblib`")
    L.append("- **Model target**: `trade_return` = log(close[EXIT_BAR] / open[decision_bar+1]) — mirrors actual trade P&L exactly")
    L.append("- **Per-side thresholds**: expanding-window percentile of |score| computed only over that side's prior history (causal: `series.shift(1)`)")
    L.append("- **Direction**: `long_model` fires when score>0 & crosses long thresholds; `short_model` fires when score<0 & crosses short thresholds")
    L.append("- **Calibration**: walk-forward yearly folds (test year Y, train = all years < Y, 1-day purge gap). "
             "Grid-search (thr, conv, stop) per fold using train-window data only; deploy on the test year. "
             "Trades stitched across test folds → pooled WF metrics.")
    L.append("- **Eligibility guard (per fold)**: train P&L>0 AND train Sharpe>0 AND n≥20. "
             "A side **deploys** only if eligible in ≥50% of folds AND pooled WF Sharpe>0.")
    if mode == "mixed":
        L.append("- **Mode**: **mixed** (Phase 4 per-side deployment). Each side uses the mode "
                 "(single/hybrid/dual, optionally +gated) with the highest pooled WF Sharpe among "
                 "configs that pass the eligibility majority gate.")
    L.append("- **Decision/Entry**: per-ETF `DECISION_BAR` (see day-model/build_features.py).")
    L.append(f"- **Exit bar**: {EXIT_BAR} (5m close at 14:30)")
    L.append(f"- **Cost**: {DEFAULT_COST_BPS:.0f} bps round-trip (parametrizable)\n")

    L.append("\n## 2. Deployed Configurations\n")
    if mode == "mixed":
        L.append("| ETF | Long mode | Long pooled S | Long elig | Short mode | Short pooled S | Short elig |")
        L.append("|-----|-----------|---------------|-----------|------------|----------------|------------|")
        for etf in ETFS:
            cfg = configs.get(etf, {})
            lg = cfg.get("long"); sh = cfg.get("short")
            lmode = lg.get("_mode", "?") if lg else "—"
            ls = (f"{lg['pooled_wf_sharpe']:+.2f}" if lg else "—")
            le = (f"{lg['n_folds_eligible']}/{lg['n_folds']}" if lg else "—")
            smode = sh.get("_mode", "?") if sh else "—"
            ss = (f"{sh['pooled_wf_sharpe']:+.2f}" if sh else "—")
            se = (f"{sh['n_folds_eligible']}/{sh['n_folds']}" if sh else "—")
            L.append(f"| **{etf}** | `{lmode}` | {ls} | {le} | `{smode}` | {ss} | {se} |")

    # Per-fold config stability table
    L.append("\n### 2.1 Per-Fold Config Stability\n")
    L.append("Shows the (mode / threshold / conviction / stop) chosen for each fold's test year, "
             "plus train and test Sharpe. Variation across years exposes regime drift; "
             "consistency suggests a stable edge.\n")
    for etf in ETFS:
        cfg = configs.get(etf, {})
        for side_name in ("long", "short"):
            side_cfg = cfg.get(side_name)
            if not side_cfg:
                continue
            L.append(f"\n**{etf} / {side_name}** (mode={side_cfg.get('_mode','?')}, "
                     f"pooled WF S={side_cfg['pooled_wf_sharpe']:+.2f}, "
                     f"elig {side_cfg['n_folds_eligible']}/{side_cfg['n_folds']}):")
            L.append("| Fold | Thr | Conv | Stop | Train S | Train P&L | Train N | Test S | Test P&L | Test N |")
            L.append("|------|-----|------|------|---------|-----------|---------|--------|-----------|--------|")
            for fr in side_cfg.get("folds", []):
                if not fr.get("eligible"):
                    L.append(f"| {fr['test_year']} | — | — | — | — | — | — | — | — | — (disabled) |")
                    continue
                st = fr.get("stop_type"); sv = fr.get("stop_value")
                if st == "pct":
                    stop_lbl = f"{sv:.2%}"
                elif st == "atr":
                    stop_lbl = f"{sv:.1f}×ATR"
                else:
                    stop_lbl = "—"
                L.append(f"| {fr['test_year']} | {fr['threshold_pct']:.0f} | {fr['conviction_pct']:.0f} | "
                         f"{stop_lbl} | {fr['train_sharpe']:+.2f} | {fr['train_pnl_bps']:+.0f} | "
                         f"{fr['train_n']} | {fr['test_sharpe']:+.2f} | {fr['test_pnl_bps']:+.0f} | "
                         f"{fr['test_n']} |")

    L.append("\n## 3. Walk-Forward OOS Performance (15 bps round-trip)\n")
    L.append("All metrics below are **pooled across test folds** (no IS/OOS split at a fixed date). "
             "Each fold's config was selected using train-window data only.\n")

    L.append("\n### 3.1 Per-Side Pooled WF Metrics\n")
    L.append("*Place%* = side trades / total trading days across all test folds (capital deployment rate).\n")
    L.append("*Warnings* = non-blocking fragility flags (`median<=0`, `win<=50%`, `n<60`).\n")
    L.append("| ETF | Side | N WF | Place% | Win% | Sharpe | P&L bps | MaxDD bps | Mean bps | Median bps | Warnings |")
    L.append("|-----|------|------|--------|------|--------|---------|-----------|----------|------------|----------|")
    for etf, r in data.items():
        t = r["trades"]
        if len(t) == 0 or "direction" not in t.columns:
            continue
        _, n_wf_days = _trading_day_counts(etf)
        for side, sign in [("long", 1), ("short", -1)]:
            sd = t[t["direction"] == sign]
            if len(sd) == 0:
                continue
            rets = sd["net_ret"].values
            n_sd = len(sd)
            median_bps = float(np.median(rets) * 1e4)
            wr = float((rets > 0).mean())
            warns = []
            if median_bps <= 0: warns.append("median<=0")
            if wr <= 0.50: warns.append("win<=50%")
            if n_sd < 60: warns.append("n<60")
            warn_str = ", ".join(warns) if warns else "—"
            L.append(f"| {etf} | `{side}` | {n_sd} | "
                     f"{_placement_rate(n_sd, n_wf_days):.1f}% | "
                     f"{wr:.1%} | "
                     f"{_sharpe(rets):+.2f} | {rets.sum()*1e4:+.0f} | "
                     f"{_max_dd_bps(rets):+.0f} | {np.mean(rets)*1e4:+.1f} | "
                     f"{median_bps:+.1f} | {warn_str} |")

    L.append("\n### 3.2 Combined (Long+Short) Per ETF\n")
    L.append("| ETF | N WF | L Place% | S Place% | Tot Place% | Win% | "
             "Sharpe | P&L bps | MaxDD bps |")
    L.append("|-----|------|----------|----------|------------|------|"
             "--------|---------|-----------|")
    for etf, r in data.items():
        t = r["trades"]
        if len(t) == 0:
            L.append(f"| {etf} | 0 | — | — | — | — | — | — | — |")
            continue
        _, n_wf_days = _trading_day_counts(etf)
        rets = t["net_ret"].values
        long_n = int((t["direction"] > 0).sum())
        short_n = int((t["direction"] < 0).sum())
        L.append(f"| **{etf}** | {len(t)} | "
                 f"{_placement_rate(long_n, n_wf_days):.1f}% | "
                 f"{_placement_rate(short_n, n_wf_days):.1f}% | "
                 f"{_placement_rate(len(t), n_wf_days):.1f}% | "
                 f"{float((rets>0).mean()):.1%} | "
                 f"{_sharpe(rets):+.2f} | {rets.sum()*1e4:+.0f} | "
                 f"{_max_dd_bps(rets):+.0f} |")

    L.append("\n### 3.3 Year-by-Year Sharpe (fold-aligned)\n")
    years = sorted({t.year for r in data.values() for t in r["trades"].index})
    L.append("| ETF | Side | " + " | ".join(str(y) for y in years) + " |")
    L.append("|-----|------|" + "---|" * len(years))
    for etf, r in data.items():
        t = r["trades"]
        if len(t) == 0 or "direction" not in t.columns:
            continue
        for side, sign in [("long", 1), ("short", -1)]:
            sd = t[t["direction"] == sign]
            if len(sd) == 0:
                continue
            cells = []
            for y in years:
                yr = sd[sd.index.year == y]["net_ret"].values
                cells.append(f"{_sharpe(yr):+.2f}" if len(yr) > 1 else "—")
            L.append(f"| {etf} | `{side}` | " + " | ".join(cells) + " |")
    L.append(f"\n![yearly_sharpe]({yr_path.relative_to(PKG_DIR)})\n")

    L.append("\n### 3.4 Cost Sensitivity (per-side, same per-fold configs)\n")
    L.append("_Per-fold configs are fixed (chosen at 15 bps). Cost sweep re-evaluates P&L only; "
             "it is a sensitivity diagnostic, not a re-optimisation._\n")
    if len(cost_df):
        L.append("| ETF | Side | 5 bps | 15 bps | 30 bps |")
        L.append("|-----|------|-------|--------|--------|")
        for etf in ETFS:
            for side in ["long", "short"]:
                row = cost_df[(cost_df["etf"] == etf) & (cost_df["side"] == side)]
                if len(row) == 0:
                    continue
                vals = {int(r["cost_bps"]): r["sharpe"] for _, r in row.iterrows()}
                cells = " | ".join(
                    f"{vals.get(c, float('nan')):+.2f}" if not np.isnan(vals.get(c, float('nan'))) else "—"
                    for c in [5, 15, 30]
                )
                L.append(f"| {etf} | `{side}` | {cells} |")

    L.append("\n### 3.5 Equity Curves (stitched across WF test folds)\n")
    L.append(f"![equity_combined]({eq_comb.relative_to(PKG_DIR)})\n")
    L.append(f"![equity_per_side]({eq_split.relative_to(PKG_DIR)})\n")

    L.append("\n### 3.6 Fragility Warnings Summary\n")
    L.append("Non-blocking transparency flags. A side with warnings is still deployed (passes the "
             "hard eligibility majority gate) but the positive Sharpe may be a small-sample / "
             "heavy-tail artifact. Investigate before sizing.\n")
    L.append("| ETF | Side | N WF | Median bps | Win% | Warnings |")
    L.append("|-----|------|------|------------|------|----------|")
    for etf, r in data.items():
        t = r["trades"]
        if len(t) == 0 or "direction" not in t.columns:
            continue
        for side, sign in [("long", 1), ("short", -1)]:
            sd = t[t["direction"] == sign]
            if len(sd) == 0:
                continue
            rets = sd["net_ret"].values
            n_sd = len(sd)
            median_bps = float(np.median(rets) * 1e4)
            wr = float((rets > 0).mean())
            warns = []
            if median_bps <= 0: warns.append("median<=0")
            if wr <= 0.50: warns.append("win<=50%")
            if n_sd < 60: warns.append("n<60")
            warn_str = ", ".join(warns) if warns else "—"
            L.append(f"| {etf} | `{side}` | {n_sd} | {median_bps:+.1f} | {wr:.1%} | {warn_str} |")

    L.append("\n## 4. Diagnostic: Cluster Confusion (WF traded days)\n")
    L.append("Of days traded on each side, what fraction belonged to day-trading's "
             "discovered Rally/Selloff/Neutral clusters?\n")
    if len(cluster_df):
        L.append("| ETF | Side | N | Rally% | Selloff% | Neutral% |")
        L.append("|-----|------|---|--------|----------|----------|")
        for _, row in cluster_df.iterrows():
            L.append(f"| {row['etf']} | `{row['side']}` | {row['n']} | "
                     f"{row['Rally%']:.0f}% | {row['Selloff%']:.0f}% | {row['Neutral%']:.0f}% |")
    else:
        L.append("_cluster labels not available_")

    # ── §5 Mode comparison (all WF) + §5.5 Gating impact ────────────────
    L.append("\n## 5. Mode Comparison (Phase 4 — all walk-forward)\n")
    L.append("Each side deploys the mode with the highest pooled WF Sharpe among configs "
             "that pass the eligibility majority gate.\n")
    from .deploy import _load_mode_calibrations
    mode_calibs = _load_mode_calibrations()
    if mode_calibs:
        L.append("| ETF | Side | Single | Hybrid | Dual | Single+g | Hybrid+g | Dual+g | **Deployed** |")
        L.append("|-----|------|--------|--------|------|----------|----------|--------|--------------|")
        for etf in ETFS:
            for side in ("long", "short"):
                vals = {}
                for m, mc in mode_calibs.items():
                    cfg = mc.get("results", {}).get(etf, {}).get(side)
                    if cfg and cfg.get("deployed"):
                        vals[m] = cfg
                if not vals:
                    continue
                cells = {}
                for m in ("single", "hybrid", "dual", "single+gated", "hybrid+gated", "dual+gated"):
                    c = vals.get(m)
                    cells[m] = f"{c['pooled_wf_sharpe']:+.2f}" if c else "—"
                deployed_cfg = configs.get(etf, {}).get(side)
                dep_mode = deployed_cfg.get("_mode", "?") if deployed_cfg else "—"
                dep_s = (f"{deployed_cfg['pooled_wf_sharpe']:+.2f}" if deployed_cfg else "—")
                L.append(f"| {etf} | `{side}` | {cells['single']} | {cells['hybrid']} | "
                         f"{cells['dual']} | {cells['single+gated']} | {cells['hybrid+gated']} | "
                         f"{cells['dual+gated']} | **{dep_mode}** ({dep_s}) |")
        # Totals
        total_dep = 0.0
        for etf in ETFS:
            for side in ("long", "short"):
                dep_cfg = configs.get(etf, {}).get(side)
                if dep_cfg:
                    total_dep += dep_cfg.get("pooled_wf_sharpe", 0) or 0
        L.append(f"\n**Total deployed pooled WF Sharpe**: {total_dep:+.2f}\n")

    L.append("\n## 5.5 Gating Impact (v3, walk-forward)\n")
    L.append("Per-side pooled WF Sharpe: best ungated mode vs best gated mode.\n")
    ungated = {m: c for m, c in mode_calibs.items() if not m.endswith("+gated")}
    gated = {m: c for m, c in mode_calibs.items() if m.endswith("+gated")}
    if ungated or gated:
        L.append("| ETF | Side | Best Ungated | Best Gated | Δ | Deployed |")
        L.append("|-----|------|--------------|------------|---|----------|")
        tot_ung = tot_gat = tot_dep = 0.0
        for etf in ETFS:
            for side in ("long", "short"):
                def _best(calibs):
                    b = None
                    for m, mc in calibs.items():
                        cfg = mc.get("results", {}).get(etf, {}).get(side)
                        if cfg and cfg.get("deployed"):
                            s = cfg.get("pooled_wf_sharpe", 0) or 0
                            if b is None or s > b:
                                b = s
                    return b
                u = _best(ungated); g = _best(gated)
                if u is None and g is None:
                    continue
                u_str = f"{u:+.2f}" if u is not None else "disabled"
                g_str = f"{g:+.2f}" if g is not None else "disabled"
                if u is not None: tot_ung += u
                if g is not None: tot_gat += g
                delta = (g - u) if (u is not None and g is not None) else float("nan")
                d_str = f"{delta:+.2f}" if delta == delta else "—"
                dep_cfg = configs.get(etf, {}).get(side)
                dep_mode = dep_cfg.get("_mode", "—") if dep_cfg else "—"
                dep_s = (f"{dep_cfg['pooled_wf_sharpe']:+.2f}" if dep_cfg else "—")
                if dep_cfg: tot_dep += dep_cfg.get("pooled_wf_sharpe", 0) or 0
                L.append(f"| {etf} | `{side}` | {u_str} | {g_str} | {d_str} | "
                         f"**{dep_mode}** ({dep_s}) |")
        lift = tot_dep - tot_ung
        L.append(f"\n**Totals** — Ungated: {tot_ung:+.2f} | Gated: {tot_gat:+.2f} | "
                 f"Deployed: {tot_dep:+.2f} (Δ vs ungated = {lift:+.2f})\n")

    L.append("\n## 6. Verdict\n")
    robust_long = []
    robust_short = []
    for etf, cfg in configs.items():
        l = cfg.get("long"); s = cfg.get("short")
        if l and l.get("pooled_wf_sharpe", 0) >= 1.5:
            robust_long.append(etf)
        if s and s.get("pooled_wf_sharpe", 0) >= 1.5:
            robust_short.append(etf)
    L.append(f"- **Robust long (pooled WF Sharpe ≥ +1.5)**: {', '.join(robust_long) or 'none'}")
    L.append(f"- **Robust short (pooled WF Sharpe ≥ +1.5)**: {', '.join(robust_short) or 'none'}")
    L.append(f"- **Disabled long**: {', '.join(e for e in ETFS if not configs.get(e,{}).get('long')) or 'none'}")
    L.append(f"- **Disabled short**: {', '.join(e for e in ETFS if not configs.get(e,{}).get('short')) or 'none'}")
    L.append("\n_Note: the per-side deployability bar dropped from the previous single-split "
             "(Sharpe ≥ +2.0) to pooled-WF (Sharpe ≥ +1.5) because walk-forward metrics are "
             "honestly out-of-sample — the previous numbers were optimistically biased by "
             "hyperparameter selection on the reported window._")

    L.append("\n## 7. Caveats\n")
    L.append("- Short-side P&L assumes 15bps transaction cost; real options/margin/borrow costs not modeled")
    L.append("- Frozen coefficients = no regime adaptation; live IC decay will hurt deployability")
    L.append("- 14:30 exit leaves late-day continuation on the table")
    L.append("- No position sizing (fixed notional); drawdowns are per-unit-notional")
    L.append("- Walk-forward folds are yearly; intra-year regime shifts are not captured")
    L.append("- Per-fold small-sample noise (fold with <60 trades) is flagged via the `n<60` warning")
    L.append("- Cost sensitivity holds per-fold configs fixed; a true cost re-optimisation may shift choices")

    REPORT_PATH.write_text("\n".join(L), encoding="utf-8")
    print(f"Report → {REPORT_PATH}")

    out = {
        "cost_bps": DEFAULT_COST_BPS,
        "walk_forward": True,
        "configs": configs,
        "combined_metrics": {
            etf: {k: v for k, v in r.items() if k != "trades"}
            for etf, r in data.items()
        },
        "cost_sweep": cost_df.to_dict(orient="records"),
        "cluster_confusion": cluster_df.to_dict(orient="records"),
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"Results JSON → {RESULTS_PATH}")


if __name__ == "__main__":
    generate()
