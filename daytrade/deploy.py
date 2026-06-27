"""Phase 4: Per-side best-of-mode deployment (walk-forward aware).

Reads all walk-forward calibration files (single, hybrid, dual, each ±gated),
picks the best mode per (ETF, side) by **pooled walk-forward Sharpe**, and
saves the combined deployment.

A side is deployable for a given mode only if:
  - ``deployed == True`` in that mode's WF calibration (majority-fold
    eligibility AND pooled WF Sharpe > 0), AND
  - it has the highest pooled WF Sharpe among all candidate modes.

The deployed `calibration.json` carries the per-fold config table so the
report can show stability across folds (regime drift diagnostic).
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
    "single+gated": DATA_DIR / "calibration_single_gated.json",
    "hybrid+gated": DATA_DIR / "calibration_hybrid_gated.json",
    "dual+gated": DATA_DIR / "calibration_dual_gated.json",
}


def _deploy_better(candidate: dict, current: dict) -> bool:
    """Prefer higher pooled WF Sharpe, tiebreak by pooled WF P&L."""
    cs = candidate.get("pooled_wf_sharpe", 0) or 0
    cc = current.get("pooled_wf_sharpe", 0) or 0
    if abs(cs - cc) > 0.01:
        return cs > cc
    return (candidate.get("pooled_wf_pnl_bps", 0) or 0) > (current.get("pooled_wf_pnl_bps", 0) or 0)


def _load_mode_calibrations() -> dict[str, dict]:
    """Return {mode: calibration_dict} for all available WF calibration files."""
    out = {}
    for mode, path in MODE_FILES.items():
        if path.exists():
            out[mode] = json.loads(path.read_text())
    return out


def deploy(verbose: bool = True) -> dict:
    """Pick best mode per ETF per side by pooled WF Sharpe; save combined deployment."""
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

            # Deployment criterion: pooled walk-forward Sharpe (honest OOS).
            # The per-mode calibrator already enforces the per-fold eligibility
            # majority gate; we only pick among configs flagged deployed=True.
            if long_cfg and long_cfg.get("deployed"):
                if best_long is None or _deploy_better(long_cfg, best_long):
                    best_long = dict(long_cfg)
                    best_long_mode = mode

            if short_cfg and short_cfg.get("deployed"):
                if best_short is None or _deploy_better(short_cfg, best_short):
                    best_short = dict(short_cfg)
                    best_short_mode = mode

        # Annotate configs with their source mode + gated flag
        if best_long:
            best_long["_mode"] = best_long_mode
            best_long["gated"] = best_long_mode.endswith("+gated")
        if best_short:
            best_short["_mode"] = best_short_mode
            best_short["gated"] = best_short_mode.endswith("+gated")

        deployed[etf] = {
            "long": best_long,
            "short": best_short,
        }

        def _stop_label(cfg):
            if not cfg:
                return "—"
            st = cfg.get("stop_type")
            sv = cfg.get("stop_value")
            if st == "pct":
                return f"{sv:.3f}"
            elif st == "atr":
                return f"{sv:.1f}xATR"
            return "—"

        l_str = (f"{best_long_mode} pooled_S={best_long['pooled_wf_sharpe']:+.2f} "
                 f"(elig {best_long['n_folds_eligible']}/{best_long['n_folds']})"
                 if best_long else "disabled")
        s_str = (f"{best_short_mode} pooled_S={best_short['pooled_wf_sharpe']:+.2f} "
                 f"(elig {best_short['n_folds_eligible']}/{best_short['n_folds']})"
                 if best_short else "disabled")
        comparison_rows.append((etf, l_str, s_str))

    # Save combined deployment
    out = {
        "cost_bps": 15.0,
        "mode": "mixed",
        "walk_forward": True,
        "results": deployed,
    }
    out_path = DATA_DIR / "calibration.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    if verbose:
        print(f"Deployed calibration → {out_path}")
        print()
        print("=" * 110)
        print(f"{'ETF':<12} {'LONG (mode / pooled WF Sharpe / eligibility)':<49} "
              f"{'SHORT (mode / pooled WF Sharpe / eligibility)':<49}")
        print("-" * 110)
        for etf, l, s in comparison_rows:
            print(f"{etf:<12} {l:<49} {s:<49}")
        print("=" * 110)

        mode_counts = {}
        for etf_cfg in deployed.values():
            for side in ("long", "short"):
                cfg = etf_cfg[side]
                if cfg:
                    m = cfg["_mode"]
                    mode_counts[m] = mode_counts.get(m, 0) + 1
        print(f"\nMode usage: {mode_counts}")

        total_pooled = 0.0
        n_deployed = 0
        for etf_cfg in deployed.values():
            for side in ("long", "short"):
                cfg = etf_cfg[side]
                if cfg:
                    total_pooled += cfg.get("pooled_wf_sharpe", 0) or 0
                    n_deployed += 1
        print(f"Total deployed pooled WF Sharpe: {total_pooled:+.2f} across {n_deployed} sides")

    return deployed


if __name__ == "__main__":
    deploy()
