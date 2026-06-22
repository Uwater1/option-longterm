"""Phase 4: Per-side best-of-mode deployment.

Reads all calibration files (single, hybrid, dual), picks the best config
per ETF per side by OOS composite score, and saves the combined deployment.

This implements the improvement plan Phase 4:
  "For each ETF, deploy whichever mode/side gives the best OOS composite score."

Output: daytrade/data/calibration.json with mode="mixed" and per-side _mode tags.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import ETFS

PKG_DIR = Path(__file__).resolve().parent
DATA_DIR = PKG_DIR / "data"

MODE_FILES = {
    "single": DATA_DIR / "calibration_single.json",
    "hybrid": DATA_DIR / "calibration_hybrid.json",
    "dual": DATA_DIR / "calibration_dual.json",
}


def _deploy_better(candidate: dict, current: dict) -> bool:
    """Deployment comparison: prefer higher OOS Sharpe, tiebreak by P&L."""
    cs = candidate.get("oos_sharpe", 0) or 0
    cc = current.get("oos_sharpe", 0) or 0
    if abs(cs - cc) > 0.01:
        return cs > cc
    # Tiebreak: higher P&L
    return (candidate.get("oos_pnl_bps", 0) or 0) > (current.get("oos_pnl_bps", 0) or 0)


def _load_mode_calibrations() -> dict[str, dict]:
    """Return {mode: calibration_dict} for all available calibration files."""
    out = {}
    for mode, path in MODE_FILES.items():
        if path.exists():
            out[mode] = json.loads(path.read_text())
    return out


def deploy(verbose: bool = True) -> dict:
    """Pick best mode per ETF per side and save combined deployment."""
    calibs = _load_mode_calibrations()
    if not calibs:
        raise SystemExit("No calibration files found. Run calibrate for each mode first.")

    deployed = {}
    comparison_rows = []

    for etf in ETFS:
        best_long = None
        best_short = None
        best_long_mode = None
        best_short_mode = None

        for mode, calib in calibs.items():
            res = calib.get("results", {}).get(etf, {})
            long_cfg = res.get("long")
            short_cfg = res.get("short")

            # Deployment criterion: OOS Sharpe (risk-adjusted), not composite
            # score.  Composite score within each mode already accounts for
            # tradeoffs; cross-mode we want the best risk-adjusted edge.
            # Tiebreak: higher P&L, then higher composite score.
            if long_cfg and long_cfg.get("eligible"):
                if best_long is None or _deploy_better(long_cfg, best_long):
                    best_long = dict(long_cfg)
                    best_long_mode = mode

            if short_cfg and short_cfg.get("eligible"):
                if best_short is None or _deploy_better(short_cfg, best_short):
                    best_short = dict(short_cfg)
                    best_short_mode = mode

        # Annotate configs with their source mode
        if best_long:
            best_long["_mode"] = best_long_mode
        if best_short:
            best_short["_mode"] = best_short_mode

        deployed[etf] = {
            "long": best_long,
            "short": best_short,
        }

        l_str = (f"{best_long_mode} thr={best_long['threshold_pct']:.0f} "
                 f"c={best_long['conviction_pct']:.0f} S={best_long['oos_sharpe']:+.2f}"
                 if best_long else "disabled")
        s_str = (f"{best_short_mode} thr={best_short['threshold_pct']:.0f} "
                 f"c={best_short['conviction_pct']:.0f} S={best_short['oos_sharpe']:+.2f}"
                 if best_short else "disabled")
        comparison_rows.append((etf, l_str, s_str))

    # Save combined deployment
    out = {
        "cost_bps": 15.0,
        "mode": "mixed",
        "results": deployed,
    }
    out_path = DATA_DIR / "calibration.json"
    out_path.write_text(json.dumps(out, indent=2))
    if verbose:
        print(f"Deployed calibration → {out_path}")
        print()
        print("=" * 80)
        print(f"{'ETF':<12} {'LONG (mode / cfg / Sharpe)':<35} {'SHORT (mode / cfg / Sharpe)':<35}")
        print("-" * 80)
        for etf, l, s in comparison_rows:
            print(f"{etf:<12} {l:<35} {s:<35}")
        print("=" * 80)

        # Count deployments per mode
        mode_counts = {}
        for etf_cfg in deployed.values():
            for side in ("long", "short"):
                cfg = etf_cfg[side]
                if cfg:
                    m = cfg["_mode"]
                    mode_counts[m] = mode_counts.get(m, 0) + 1
        print(f"\nMode usage: {mode_counts}")

    return deployed


if __name__ == "__main__":
    deploy()
