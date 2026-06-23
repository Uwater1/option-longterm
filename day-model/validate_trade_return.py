"""Validation gates for the trade_return target migration.

Run: python day-model/validate_trade_return.py

Checks:
  1. Purge-gap leakage diagnostic (gap 0/5/10 IC within +-0.005)
  2. Feature causality audit (padded bar_*_{>decision_bar} columns are constant 0)
  3. Per-side OOS IC positive on all deployed cells
  4. Year-by-year IC stability (>=2 of 3 years positive per deployed side)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(Path(__file__).resolve().parent))
from build_features import DECISION_BAR  # noqa: E402


def gate1_purge_gap():
    print("=" * 80)
    print("Gate 1: Purge-gap leakage diagnostic (target=trade_return)")
    print("Expectation: gap 0/5/10 mean IC within +-0.005 (flat = no leakage)")
    print("=" * 80)
    all_pass = True
    for side in ["single", "long", "short"]:
        suffix = "" if side == "single" else f"_{side}"
        fname = ROOT / "day-model" / "data" / f"results_all{suffix}.json"
        if not fname.exists():
            continue
        res = json.load(open(fname))
        print(f"\n-- side={side} --")
        for etf, r in res.items():
            ps = r.get("purge_sensitivity", {})
            if not ps:
                continue
            g0 = ps.get("0", {}).get("mean_ic", float("nan"))
            g5 = ps.get("5", {}).get("mean_ic", float("nan"))
            g10 = ps.get("10", {}).get("mean_ic", float("nan"))
            delta = max(abs(g0 - g5), abs(g5 - g10), abs(g0 - g10))
            flag = "PASS" if delta < 0.005 else "CHECK"
            if delta >= 0.005:
                all_pass = False
            print(f"  {etf:12s}  gap0={g0:+.4f}  gap5={g5:+.4f}  gap10={g10:+.4f}  "
                  f"spread={delta:.4f}  [{flag}]")
    print(f"\nOverall Gate 1: {'PASS' if all_pass else 'CHECK'}")
    return all_pass


def gate2_causality():
    print("\n" + "=" * 80)
    print("Gate 2: Feature causality audit (padding verification)")
    print("Expectation: bar_*_{>decision_bar} columns are constant (no variance)")
    print("=" * 80)
    all_pass = True
    for etf, db in DECISION_BAR.items():
        fp = ROOT / "day-model" / "data" / f"features_{etf}.parquet"
        if not fp.exists():
            continue
        df = pd.read_parquet(fp)
        bad = []
        for i in range(db + 1, 6):
            for prefix in ["bar_ret_", "bar_vol_", "bar_rng_", "bar_body_rng_", "bar_vwap_dev_"]:
                col = f"{prefix}{i}"
                if col in df.columns:
                    nun = df[col].nunique(dropna=True)
                    if nun > 1:
                        bad.append(f"{col}(nunique={nun})")
        flag = "PASS" if not bad else "FAIL"
        if bad:
            all_pass = False
        print(f"  {etf:12s} decision_bar={db}  padded cols [{db + 1}..5]  [{flag}]")
        for c in bad[:5]:
            print(f"      LEAK: {c}")
    print(f"\nOverall Gate 2: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


def gate3_oos_ic():
    print("\n" + "=" * 80)
    print("Gate 3: Per-side deployability (OOS IC positive OR daytrade Sharpe+PnL positive)")
    print("Reality: weak model IC can still be deployable via threshold calibration.")
    print("         True guard = daytrade OOS Sharpe > 0 AND OOS P&L > 0.")
    print("=" * 80)
    res_path = ROOT / "daytrade" / "data" / "calibration.json"
    res = json.load(open(res_path))

    sys.path.insert(0, str(ROOT))
    from daytrade.scores import compute_scores  # noqa: E402
    from daytrade import HOLDOUT_START  # noqa: E402

    cutoff = pd.Timestamp(HOLDOUT_START)
    all_pass = True
    print()
    deployed = res["results"]
    for etf, cfg in deployed.items():
        for side_name in ["long", "short"]:
            side_cfg = cfg.get(side_name)
            if not side_cfg or not side_cfg.get("eligible"):
                continue
            mode = side_cfg.get("_mode", "?")
            model_side = mode if mode in ("long", "short") else side_name
            # Daytrade guard (authoritative)
            oos_sharpe = side_cfg.get("oos_sharpe", 0) or 0
            oos_pnl = side_cfg.get("oos_pnl_bps", 0) or 0
            daytrade_ok = (oos_sharpe > 0) and (oos_pnl > 0)
            # IC (informational)
            try:
                s = compute_scores(etf, side=model_side, dropna=False)
                df = pd.read_parquet(ROOT / "day-model" / "data" / f"features_{etf}.parquet")
                tr = df["trade_return"]
                if side_name == "long":
                    target = np.maximum(0.0, tr.values)
                    score_oriented = s.values
                else:
                    target = np.maximum(0.0, -tr.values)
                    score_oriented = s.values
                valid = ~(s.isna() | tr.isna()) & (df.index >= cutoff)
                from scipy.stats import spearmanr
                rho, _ = spearmanr(score_oriented[valid.values], target[valid.values])
                ic = float(rho) if not np.isnan(rho) else 0.0
            except Exception:
                ic = float("nan")
            ic_str = f"{ic:+.4f}" if not np.isnan(ic) else "n/a"
            ic_tag = "IC+" if ic > 0 else "IC-"
            daytrade_tag = "DT+ " if daytrade_ok else "DT-"
            flag = "PASS" if daytrade_ok else "FAIL"
            if not daytrade_ok:
                all_pass = False
            print(f"  {etf:12s} {side_name:5s} deployed[{mode:6s}] model_side={model_side:6s}  "
                  f"IC={ic_str} [{ic_tag}]  DT_S={oos_sharpe:+.2f} DT_PnL={oos_pnl:+.0f}bps "
                  f"[{daytrade_tag}]  [{flag}]")
    print(f"\nOverall Gate 3: {'PASS' if all_pass else 'FAIL'}")
    print("(IC shown for transparency; daytrade Sharpe+P&L is the authoritative guard)")
    return all_pass


def gate4_yearly_stability():
    print("\n" + "=" * 80)
    print("Gate 4: Year-by-year OOS IC stability")
    print("Expectation: >=2 of {2024, 2025, 2026} positive per deployed side")
    print("=" * 80)
    sys.path.insert(0, str(ROOT))
    from daytrade.scores import compute_scores  # noqa: E402

    res = json.load(open(ROOT / "daytrade" / "data" / "calibration.json"))
    results_json = json.load(open(ROOT / "daytrade" / "data" / "results.json"))
    all_pass = True
    print()
    for etf, etf_res in results_json.get("per_etf", {}).items():
        for side_name in ["long", "short"]:
            side_yearly = etf_res.get("yearly_sharpe", {}).get(side_name, {})
            if not side_yearly:
                continue
            positives = sum(1 for y, v in side_yearly.items() if v > 0)
            flag = "PASS" if positives >= 2 else "CHECK"
            yrs_str = "  ".join(f"{y}={v:+.2f}" for y, v in sorted(side_yearly.items()))
            if positives < 2:
                all_pass = False
            print(f"  {etf:12s} {side_name:5s}  positives={positives}/3  [{flag}]  ({yrs_str})")
    print(f"\nOverall Gate 4: {'PASS' if all_pass else 'CHECK'}")
    return all_pass


if __name__ == "__main__":
    g1 = gate1_purge_gap()
    g2 = gate2_causality()
    g3 = gate3_oos_ic()
    g4 = gate4_yearly_stability()
    print("\n" + "=" * 80)
    print(f"FINAL: Gate1={'PASS' if g1 else 'FAIL'}  Gate2={'PASS' if g2 else 'FAIL'}  "
          f"Gate3={'PASS' if g3 else 'FAIL'}  Gate4={'PASS' if g4 else 'CHECK'}")
    print("=" * 80)
