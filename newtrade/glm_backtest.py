#!/usr/bin/env python3
"""
GLM Backtest Runner for NewTrade framework (Scheme 5 — Expanding Ridge).

Standalone CLI that runs the GLM composite and compares against Rank Bounded Weight.
Implements the acceptance gate defined in plan_glm.md.

Usage:
  uv run python newtrade/glm_backtest.py -e 300ETF --compare
  uv run python newtrade/glm_backtest.py -e all --compare --future
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "day-model-new"))
sys.path.insert(0, str(REPO_ROOT / "day-model-new" / "mining"))
sys.path.insert(0, str(REPO_ROOT / "day-model"))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, load_future_trade_returns,
)
from glm import expanding_ridge_composite
from weighting import compute_rank_w
from strategy import (
    generate_positions, simulate_etf_spot, calculate_metrics,
    sweep_optimal_threshold, compute_production_threshold,
)

AVAILABLE_ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]

# Acceptance gate thresholds (plan_glm.md §5)
GATE_PNL_RATIO = 0.8       # PnL_GLM >= 0.8 * PnL_Rank
GATE_MAXDD_RATIO = 1.5     # MaxDD_GLM <= 1.5 * MaxDD_Rank
GATE_WR_TOLERANCE = 3.0    # WinRate_GLM >= WinRate_Rank - 3%


def run_glm_single(
    etf: str,
    side: str = "single",
    z_th: str = "auto",
    position_mode: str = "binary",
    fee_bps: float = 0.0008,
    start_date: str = "2022-01-01",
    end_date: str = "2026-01-01",
    z_buffer: float = 0.1,
    z_short_buffer: float = None,
    alphas: list = None,
    clamp_nonneg: bool = True,
    long_only: bool = False,
    use_future: bool = False,
    min_features: int = 10,
    ic_prior: bool = True,
    n_adaptive: bool = True,
    min_percentile: float = 0.0,
) -> dict:
    """Run GLM backtest for one ETF."""
    
    # 1. Load pool
    pool = load_admitted_pool(etf, side=side, min_features=min_features)
    if not pool:
        return {"etf": etf, "status": "SKIPPED_FEAT_FLOOR", "n_features": len(pool)}

    # 2. Load dataset
    df = load_etf_dataset(etf)

    # 3. Trade returns
    asset_type = "Spot ETF"
    if use_future:
        fut_returns, fut_ok, fut_name = load_future_trade_returns(etf, df)
        if not fut_ok:
            return {"etf": etf, "status": "SKIPPED_NO_FUTURE", "n_features": len(pool)}
        full_trade_ret = fut_returns
        asset_type = f"Future ({fut_name})"
    else:
        full_trade_ret = (
            df["trade_return"].values.astype(np.float64)
            if "trade_return" in df.columns
            else df["close"].pct_change().fillna(0.0).values
        )

    # 4. Build feature matrix & signs
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)

    # 5. Expanding z-score
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    # 6. Sign-align
    Z_signed = Z_std * signs

    # 7. Determine training end index
    t_start_ts = pd.Timestamp(start_date)
    train_mask = df["date"] < t_start_ts
    train_end_idx = int(train_mask.sum())

    # 8. GLM composite
    if alphas is None:
        alphas = [0.01, 0.1, 1.0, 10.0, 100.0]

    Z_composite, glm_info = expanding_ridge_composite(
        Z_signed=Z_signed,
        trade_returns=full_trade_ret,
        alphas=alphas,
        burn_in=max(burn_in, 504),
        train_end_idx=train_end_idx,
        clamp_nonneg=clamp_nonneg,
        refit_every=1,
        fee_bps=fee_bps,
        pool=pool,
        ic_prior=ic_prior,
        n_adaptive=n_adaptive,
        min_percentile=min_percentile,
    )

    # 9. Threshold determination
    auto_threshold = (z_th == "auto")
    if auto_threshold:
        Z_train = Z_composite[train_mask.values]
        ret_train = full_trade_ret[train_mask.values]
        sweep_info = sweep_optimal_threshold(
            Z_train, ret_train, mode=position_mode, fee_bps=fee_bps, long_only=long_only
        )
        z_th_prod, z_th_short = compute_production_threshold(
            sweep_info, z_buffer=z_buffer, z_short_buffer=z_short_buffer
        )
    else:
        z_th_prod = float(z_th)
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        z_th_short = z_th_prod + eff_short_buf

    # 10. Position sizing
    positions_full = generate_positions(
        Z_composite, z_th=z_th_prod, z_th_short=z_th_short,
        mode=position_mode, long_only=long_only
    )

    # 11. OOS slice
    t_end = pd.Timestamp(end_date)
    mask = (df["date"] >= t_start_ts) & (df["date"] < t_end)
    if not mask.any():
        return {"etf": etf, "status": "NO_OOS_DATA", "n_features": len(pool)}

    positions_oos = positions_full[mask.values]
    trade_returns_oos = full_trade_ret[mask.values]

    # 12. Simulate
    net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)

    # 13. Metrics
    df_oos = df[mask].reset_index(drop=True)
    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=df_oos["date"])
    metrics.update({
        "etf": etf,
        "asset_type": asset_type,
        "scheme": "glm",
        "status": "SUCCESS",
        "n_features": len(pool),
        "z_th": z_th_prod,
        "z_th_short": z_th_short,
        "glm_alpha": glm_info["alpha"],
        "glm_alpha_results": glm_info["alpha_selection_results"],
        "clamp_nonneg": clamp_nonneg,
    })

    return metrics


def run_rank_single(
    etf: str,
    side: str = "single",
    z_th: str = "auto",
    position_mode: str = "binary",
    fee_bps: float = 0.0008,
    start_date: str = "2022-01-01",
    end_date: str = "2026-01-01",
    z_buffer: float = 0.1,
    z_short_buffer: float = None,
    long_only: bool = False,
    use_future: bool = False,
    min_features: int = 10,
) -> dict:
    """Run Rank Bounded Weight backtest for comparison baseline."""

    pool = load_admitted_pool(etf, side=side, min_features=min_features)
    if not pool:
        return {"etf": etf, "status": "SKIPPED_FEAT_FLOOR", "n_features": len(pool)}

    df = load_etf_dataset(etf)

    asset_type = "Spot ETF"
    if use_future:
        fut_returns, fut_ok, fut_name = load_future_trade_returns(etf, df)
        if not fut_ok:
            return {"etf": etf, "status": "SKIPPED_NO_FUTURE", "n_features": len(pool)}
        full_trade_ret = fut_returns
        asset_type = f"Future ({fut_name})"
    else:
        full_trade_ret = (
            df["trade_return"].values.astype(np.float64)
            if "trade_return" in df.columns
            else df["close"].pct_change().fillna(0.0).values
        )

    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    # Rank composite
    Z_composite = compute_rank_w(Z_std, signs, pool=pool)

    t_start_ts = pd.Timestamp(start_date)
    train_mask = df["date"] < t_start_ts

    auto_threshold = (z_th == "auto")
    if auto_threshold:
        Z_train = Z_composite[train_mask.values]
        ret_train = full_trade_ret[train_mask.values]
        sweep_info = sweep_optimal_threshold(
            Z_train, ret_train, mode=position_mode, fee_bps=fee_bps, long_only=long_only
        )
        z_th_prod, z_th_short = compute_production_threshold(
            sweep_info, z_buffer=z_buffer, z_short_buffer=z_short_buffer
        )
    else:
        z_th_prod = float(z_th)
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        z_th_short = z_th_prod + eff_short_buf

    positions_full = generate_positions(
        Z_composite, z_th=z_th_prod, z_th_short=z_th_short,
        mode=position_mode, long_only=long_only
    )

    t_end = pd.Timestamp(end_date)
    mask = (df["date"] >= t_start_ts) & (df["date"] < t_end)
    if not mask.any():
        return {"etf": etf, "status": "NO_OOS_DATA", "n_features": len(pool)}

    positions_oos = positions_full[mask.values]
    trade_returns_oos = full_trade_ret[mask.values]
    net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)

    df_oos = df[mask].reset_index(drop=True)
    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=df_oos["date"])
    metrics.update({
        "etf": etf,
        "asset_type": asset_type,
        "scheme": "rank",
        "status": "SUCCESS",
        "n_features": len(pool),
        "z_th": z_th_prod,
        "z_th_short": z_th_short,
    })

    return metrics


def check_acceptance(glm_m: dict, rank_m: dict) -> dict:
    """
    Check GLM acceptance gate vs Rank (plan_glm.md §5).
    Returns dict with per-metric pass/fail and overall verdict.
    """
    if glm_m.get("status") != "SUCCESS" or rank_m.get("status") != "SUCCESS":
        return {"verdict": "SKIP", "reasons": ["One or both schemes did not produce results"]}

    checks = {}
    reasons = []

    # Sharpe: GLM >= Rank
    s_glm = glm_m.get("cost_sharpe", 0.0)
    s_rank = rank_m.get("cost_sharpe", 0.0)
    checks["sharpe"] = s_glm >= s_rank
    if not checks["sharpe"]:
        reasons.append(f"Sharpe {s_glm:.3f} < {s_rank:.3f}")

    # PnL: GLM >= 0.8 * Rank
    p_glm = glm_m.get("total_pnl", 0.0)
    p_rank = rank_m.get("total_pnl", 0.0)
    pnl_floor = GATE_PNL_RATIO * p_rank
    checks["pnl"] = p_glm >= pnl_floor
    if not checks["pnl"]:
        reasons.append(f"PnL {p_glm:+.4f} < {GATE_PNL_RATIO}×{p_rank:+.4f} = {pnl_floor:+.4f}")

    # MaxDD: GLM <= 1.5 * Rank
    dd_glm = glm_m.get("max_drawdown", 0.0)
    dd_rank = rank_m.get("max_drawdown", 0.0)
    dd_ceiling = GATE_MAXDD_RATIO * dd_rank
    checks["maxdd"] = dd_glm <= dd_ceiling
    if not checks["maxdd"]:
        reasons.append(f"MaxDD {dd_glm:.4f} > {GATE_MAXDD_RATIO}×{dd_rank:.4f} = {dd_ceiling:.4f}")

    # Win Rate: GLM >= Rank - 3%
    wr_glm = glm_m.get("win_rate_pct", 0.0)
    wr_rank = rank_m.get("win_rate_pct", 0.0)
    wr_floor = wr_rank - GATE_WR_TOLERANCE
    checks["win_rate"] = wr_glm >= wr_floor
    if not checks["win_rate"]:
        reasons.append(f"WinRate {wr_glm:.1f}% < {wr_rank:.1f}% - {GATE_WR_TOLERANCE}% = {wr_floor:.1f}%")

    verdict = "PASS" if all(checks.values()) else "FAIL"
    return {"verdict": verdict, "checks": checks, "reasons": reasons}


def main():
    parser = argparse.ArgumentParser(description="NewTrade GLM (Scheme 5) Backtest Runner")
    parser.add_argument("-e", "--etf", type=str, default="all",
                        help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("-s", "--side", type=str, default="single", choices=["single", "long", "short"])
    parser.add_argument("--compare", action="store_true",
                        help="Run Rank Bounded Weight alongside GLM and print acceptance table")
    parser.add_argument("--no-clamp", action="store_true",
                        help="Disable non-negative coefficient clamp")
    parser.add_argument("--no-ic-prior", action="store_true",
                        help="Disable IC-weighted Ridge prior (V2, default: enabled)")
    parser.add_argument("--no-n-adaptive", action="store_true",
                        help="Disable N-adaptive alpha scaling (V2, default: enabled)")
    parser.add_argument("--min-percentile", type=float, default=0.0,
                        help="Expanding percentile gate for trade frequency control (0=disabled)")
    parser.add_argument("--alphas", type=str, default=None,
                        help="Comma-separated Ridge alpha grid (default: 0.001,0.01,0.1,1.0,10.0,100.0)")
    parser.add_argument("--z-th", type=str, default="auto",
                        help="Conviction threshold ('auto' or float)")
    parser.add_argument("--z-buffer", type=float, default=0.1)
    parser.add_argument("--z-short-buffer", type=float, default=None)
    parser.add_argument("--position-mode", type=str, default="binary",
                        choices=["binary", "tanh", "quadratic"])
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Transaction fee in bps")
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-01-01")
    parser.add_argument("--long-only", action="store_true")
    parser.add_argument("--future", action="store_true",
                        help="Trade Index Futures instead of Spot ETF")
    args = parser.parse_args()

    etfs = AVAILABLE_ETFS if args.etf.lower() == "all" else [args.etf]
    fee_bps = args.fee_bps / 10000.0
    alphas = [float(x) for x in args.alphas.split(",")] if args.alphas else None
    clamp = not args.no_clamp
    ic_prior = not args.no_ic_prior
    n_adaptive = not args.no_n_adaptive
    min_percentile = args.min_percentile

    mode_label = "Future" if args.future else "Spot ETF"
    print("=" * 80)
    print(f"NewTrade GLM Backtest (V2) | Mode={mode_label} | Clamp={clamp} | IC-Prior={ic_prior} | N-Adaptive={n_adaptive} | Pctl={min_percentile} | z_th={args.z_th} | OOS=[{args.start_date} ~ {args.end_date}]")
    print("=" * 80)

    glm_results = []
    rank_results = []

    for etf in etfs:
        print(f"\n--- {etf} ---")

        # Run GLM
        print(f"  [GLM] Running...")
        glm_m = run_glm_single(
            etf=etf, side=args.side, z_th=args.z_th,
            position_mode=args.position_mode, fee_bps=fee_bps,
            start_date=args.start_date, end_date=args.end_date,
            z_buffer=args.z_buffer, z_short_buffer=args.z_short_buffer,
            alphas=alphas, clamp_nonneg=clamp,
            long_only=args.long_only, use_future=args.future,
            ic_prior=ic_prior, n_adaptive=n_adaptive,
            min_percentile=min_percentile,
        )
        glm_results.append(glm_m)

        if glm_m.get("status") == "SUCCESS":
            print(f"  [GLM] Sharpe={glm_m['cost_sharpe']:.3f} | PnL={glm_m['total_pnl']:+.4f} | "
                  f"MaxDD={glm_m['max_drawdown']:.4f} | WR={glm_m['win_rate_pct']:.1f}% | "
                  f"Alpha={glm_m['glm_alpha']}")
        else:
            print(f"  [GLM] {glm_m.get('status', 'UNKNOWN')}")

        # Run Rank for comparison
        if args.compare:
            print(f"  [Rank] Running...")
            rank_m = run_rank_single(
                etf=etf, side=args.side, z_th=args.z_th,
                position_mode=args.position_mode, fee_bps=fee_bps,
                start_date=args.start_date, end_date=args.end_date,
                z_buffer=args.z_buffer, z_short_buffer=args.z_short_buffer,
                long_only=args.long_only, use_future=args.future,
            )
            rank_results.append(rank_m)

            if rank_m.get("status") == "SUCCESS":
                print(f"  [Rank] Sharpe={rank_m['cost_sharpe']:.3f} | PnL={rank_m['total_pnl']:+.4f} | "
                      f"MaxDD={rank_m['max_drawdown']:.4f} | WR={rank_m['win_rate_pct']:.1f}%")

                # Acceptance gate
                gate = check_acceptance(glm_m, rank_m)
                verdict = gate["verdict"]
                icon = "✓" if verdict == "PASS" else "✗"
                print(f"  [GATE] {icon} {verdict}")
                if gate["reasons"]:
                    for r in gate["reasons"]:
                        print(f"         - {r}")
            else:
                print(f"  [Rank] {rank_m.get('status', 'UNKNOWN')}")

    # Summary table
    print("\n" + "=" * 80)
    print(f"GLM vs RANK COMPARISON SUMMARY ({mode_label})")
    print("=" * 80)

    headers = ["ETF", "Scheme", "Sharpe", "PnL", "MaxDD", "WinRate", "Trades", "Alpha", "Gate"]
    rows = []

    for i, etf in enumerate(etfs):
        glm_m = glm_results[i]
        if glm_m.get("status") == "SUCCESS":
            rows.append([
                etf, "GLM",
                f"{glm_m['cost_sharpe']:.3f}",
                f"{glm_m['total_pnl']:+.4f}",
                f"{glm_m['max_drawdown']:.4f}",
                f"{glm_m['win_rate_pct']:.1f}%",
                str(glm_m.get("n_trades", 0)),
                f"{glm_m['glm_alpha']}",
                "",
            ])
        else:
            rows.append([etf, "GLM", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "SKIP"])

        if args.compare and i < len(rank_results):
            rank_m = rank_results[i]
            if rank_m.get("status") == "SUCCESS":
                gate = check_acceptance(glm_m, rank_m)
                rows.append([
                    etf, "Rank",
                    f"{rank_m['cost_sharpe']:.3f}",
                    f"{rank_m['total_pnl']:+.4f}",
                    f"{rank_m['max_drawdown']:.4f}",
                    f"{rank_m['win_rate_pct']:.1f}%",
                    str(rank_m.get("n_trades", 0)),
                    "-",
                    gate["verdict"],
                ])
            else:
                rows.append([etf, "Rank", "N/A", "N/A", "N/A", "N/A", "N/A", "-", "SKIP"])

    # Print table
    col_widths = [max(len(h), max(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print(" | ".join(c.ljust(w) for c, w in zip(row, col_widths)))

    # Save CSV artifact
    artifacts_dir = HERE / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if args.compare:
        csv_rows = []
        for i, etf in enumerate(etfs):
            glm_m = glm_results[i]
            rank_m = rank_results[i] if i < len(rank_results) else {}
            gate = check_acceptance(glm_m, rank_m) if args.compare else {"verdict": "N/A"}
            csv_rows.append({
                "etf": etf,
                "glm_sharpe": glm_m.get("cost_sharpe"),
                "glm_pnl": glm_m.get("total_pnl"),
                "glm_maxdd": glm_m.get("max_drawdown"),
                "glm_winrate": glm_m.get("win_rate_pct"),
                "glm_alpha": glm_m.get("glm_alpha"),
                "rank_sharpe": rank_m.get("cost_sharpe"),
                "rank_pnl": rank_m.get("total_pnl"),
                "rank_maxdd": rank_m.get("max_drawdown"),
                "rank_winrate": rank_m.get("win_rate_pct"),
                "gate_verdict": gate["verdict"],
            })
        csv_df = pd.DataFrame(csv_rows)
        csv_path = artifacts_dir / "glm_vs_rank.csv"
        csv_df.to_csv(csv_path, index=False)
        print(f"\nSaved comparison CSV to {csv_path}")

    # Final verdict
    if args.compare:
        n_pass = sum(1 for i in range(len(etfs))
                     if check_acceptance(glm_results[i], rank_results[i] if i < len(rank_results) else {})["verdict"] == "PASS")
        n_valid = sum(1 for i in range(len(etfs))
                      if glm_results[i].get("status") == "SUCCESS" and
                      (rank_results[i].get("status") == "SUCCESS" if i < len(rank_results) else False))
        print(f"\n{'=' * 80}")
        print(f"FINAL VERDICT: {n_pass}/{n_valid} ETFs PASS acceptance gate")
        if n_pass >= 3:
            print("→ GLM is production-viable. Consider integrating as --scheme glm.")
        else:
            print("→ GLM does NOT meet adoption threshold. Keep Rank Bounded Weight as primary.")
        print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
