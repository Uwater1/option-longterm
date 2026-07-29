#!/usr/bin/env python3
"""
Main CLI Backtest Runner for NewTrade framework.
Runs full pipeline:
  1. Load admitted pools & raw ETF datasets.
  2. Compute zero-lookahead expanding z-score standardization over history.
  3. Aggregate composite signal Z_composite using chosen weighting scheme.
  4. Filter to target OOS period (default: 2022-01-01 to 2026-01-01).
  5. Apply conviction threshold & position sizing.
  6. Simulate ETF spot backtest with 8 bps friction.
  7. Output markdown performance report & JSON results.
"""

import sys
import json
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba, expanding_factor_score_numba, load_future_trade_returns
from weighting import get_weighting_scheme
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold, build_trade_log_df
from robustness import deflated_sharpe_ratio, run_cpcv_backtest

AVAILABLE_ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
ALL_SCHEMES = ["icw", "ew"]  # leave only icw and ew for --scheme all
ENSEMBLE_SCHEMES = ["icw", "ew"]  # schemes averaged in ensemble


def run_single_backtest(etf: str, side: str = "single", scheme_name: str = "ew", z_th: float = 0.5, 
                        position_mode: str = "binary", fee_bps: float = 0.0008, min_features: int = 10,
                        start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                        z_buffer: float = 0.1, z_short_buffer: float = None, auto_threshold: bool = False,
                        rank_kwargs: dict = None, dynamic_ic: bool = False, long_only: bool = False,
                        use_future: bool = False) -> dict:
    """
    Run backtest for one ETF and side combination filtered to OOS date range.
    
    If auto_threshold=True, sweeps Z_th on training data and applies production buffer.
    If use_future=True, trades underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF).
    """
    # 1. Load admitted pool
    pool = load_admitted_pool(etf, side=side, min_features=min_features)
    if not pool:
        print(f"    [SKIP] Pool size {len(pool)} < {min_features} threshold.")
        return {
            "etf": etf,
            "side": side,
            "scheme": scheme_name,
            "asset_type": "Future" if use_future else "Spot ETF",
            "status": "SKIPPED_FEAT_FLOOR",
            "n_features": len(pool),
            "period": f"{start_date[:7]} ~ {end_date[:7]}",
            "n_trades": 0,
            "cost_sharpe": 0.0,
            "raw_sharpe": 0.0,
            "total_pnl": 0.0,
            "max_drawdown": 0.0,
            "win_rate_pct": 0.0,
            "ann_turnover": 0.0,
            "trade_log_df": None,
        }

    # 2. Load ETF dataset
    df = load_etf_dataset(etf)

    # Handle --future underlying traded return loading
    asset_type = "Spot ETF"
    if use_future:
        fut_returns, fut_ok, fut_name = load_future_trade_returns(etf, df)
        if not fut_ok:
            print(f"--> [SKIP] {etf} has no Index Future mapping for --future mode.")
            return {
                "etf": etf,
                "side": side,
                "scheme": scheme_name,
                "asset_type": "Future (N/A)",
                "status": "SKIPPED_NO_FUTURE",
                "n_features": len(pool),
                "period": f"{start_date[:7]} ~ {end_date[:7]}",
                "n_trades": 0,
                "cost_sharpe": 0.0,
                "raw_sharpe": 0.0,
                "total_pnl": 0.0,
                "max_drawdown": 0.0,
                "win_rate_pct": 0.0,
                "ann_turnover": 0.0,
                "trade_log_df": None,
            }
        full_trade_ret = fut_returns
        asset_type = f"Future ({fut_name})"
    else:
        full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values

    print(f"--> Running Backtest: ETF={etf}, Asset={asset_type}, Side={side}, Scheme={scheme_name.upper()}, z_th={'auto' if auto_threshold else z_th}, Mode={position_mode}, LongOnly={long_only}, OOS=[{start_date} to {end_date}]")
    
    # 3. Build raw feature matrix & signs
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    
    # 4. Zero-lookahead expanding z-score standardizer on full history
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    
    # 5. Calculate Composite Signal using weighting scheme
    # Determine n_train for ICW shrinkage (days before start_date)
    t_start_ts = pd.Timestamp(start_date)
    n_train = int((df["date"] < t_start_ts).sum())
    if n_train < 252:
        n_train = 1700  # fallback ~7 years
    
    if scheme_name == "ensemble":
        # Ensemble: equal-weight average of all 4 schemes
        IC_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)
        rk = rank_kwargs if rank_kwargs else {}
        Z_composites = []
        for s_name in ENSEMBLE_SCHEMES:
            s_func = get_weighting_scheme(s_name)
            s_kwargs = dict(rk)
            s_kwargs["expanding_ic"] = IC_mat
            Z_composites.append(s_func(Z_std, signs, pool=pool, n_train=n_train, **s_kwargs))
        Z_composite = np.mean(Z_composites, axis=0)
    else:
        scheme_func = get_weighting_scheme(scheme_name)
        extra_kwargs = dict(rank_kwargs) if rank_kwargs else {}
        if dynamic_ic:
            metric_choice = extra_kwargs.get("dynamic_metric", "multi")
            if metric_choice == "multi" and scheme_name == "score":
                sw = extra_kwargs.get("score_weights", (0.20, 0.15, 0.65))
                mw = extra_kwargs.get("mono_window", 750)
                exp_mat = expanding_factor_score_numba(Z_std, signs, full_trade_ret, burn_in=burn_in, score_weights=sw, mono_window=mw)
            else:
                exp_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)
            extra_kwargs["expanding_ic"] = exp_mat
        Z_composite = scheme_func(Z_std, signs, pool=pool, n_train=n_train, **extra_kwargs)

    # 6. Threshold Determination (auto-sweep or fixed)
    sweep_info = None
    if auto_threshold:
        # Get training-period composite signal and returns for sweep
        train_mask = df["date"] < t_start_ts
        Z_composite_train = Z_composite[train_mask.values]
        trade_returns_train = full_trade_ret[train_mask.values]
        
        # Sweep on training data
        sweep_info = sweep_optimal_threshold(
            Z_composite_train, trade_returns_train,
            mode=position_mode, fee_bps=fee_bps, long_only=long_only
        )
        z_th_prod, z_th_short = compute_production_threshold(sweep_info, z_buffer=z_buffer, z_short_buffer=z_short_buffer)
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        opt_l = sweep_info.get("optimal_z_th_long", sweep_info.get("optimal_z_th", 0.5))
        opt_s = sweep_info.get("optimal_z_th_short", opt_l)
        print(f"    [THRESHOLD] Train-optimal Long Z_th={opt_l:.2f}, Short Z_th={opt_s:.2f} (Long Sharpe={sweep_info['best_sharpe']:.3f}) -> Prod Long Z_th={z_th_prod:.2f} (buf=+{z_buffer:.2f}), Short Z_th={z_th_short:.2f} (buf=+{eff_short_buf:.2f})")
    else:
        z_th_prod = z_th
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        z_th_short = z_th + (eff_short_buf - z_buffer if z_short_buffer is not None else 0.0)

    # 7. Position Sizing with production thresholds
    positions_full = generate_positions(Z_composite, z_th=z_th_prod, z_th_short=z_th_short, mode=position_mode, long_only=long_only)

    # 8. Date Filtering to OOS Evaluation Period
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    if not mask.any():
        print(f"    [WARNING] No data available for date range {start_date} to {end_date}. Falling back to recent history.")
        mask = df["date"] >= df["date"].iloc[-1000]

    df_oos = df[mask].reset_index(drop=True)
    positions_oos = positions_full[mask]
    Z_composite_oos = Z_composite[mask.values if isinstance(mask, pd.Series) else mask]

    # 9. Backtest Simulation on OOS slice
    trade_returns_oos = full_trade_ret[mask.values if isinstance(mask, pd.Series) else mask]
    net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)

    # 10. Trade log DataFrame creation & CSV export
    trade_log_df = build_trade_log_df(
        df_oos=df_oos,
        Z_composite_oos=Z_composite_oos,
        positions_oos=positions_oos,
        net_returns=net_returns,
        raw_returns=raw_returns,
        fees=fees,
        etf=etf,
        scheme=scheme_name,
        z_th=z_th_prod,
        asset_type=asset_type,
        trade_returns_arr=trade_returns_oos,
    )
    
    artifacts_dir = HERE / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    fut_suffix = "_future" if use_future else ""
    trade_csv_path = artifacts_dir / f"trades_{scheme_name}_{etf}{fut_suffix}.csv"
    trade_log_df.to_csv(trade_csv_path, index=False)

    # 11. Calculate Metrics
    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=df_oos["date"])
    metrics.update({
        "etf": etf,
        "asset_type": asset_type,
        "side": side,
        "scheme": scheme_name,
        "status": "SUCCESS",
        "n_features": len(pool),
        "z_th": z_th_prod,
        "z_th_long": z_th_prod,
        "z_th_short": z_th_short,
        "z_th_train_long": sweep_info.get("optimal_z_th_long", sweep_info.get("optimal_z_th")) if sweep_info else None,
        "z_th_train_short": sweep_info.get("optimal_z_th_short") if sweep_info else None,
        "z_buffer": z_buffer if auto_threshold else 0.0,
        "long_only": long_only,
        "use_future": use_future,
        "position_mode": position_mode,
        "dates": df_oos["date"].dt.strftime("%Y-%m-%d").tolist() if "date" in df_oos.columns else [],
        "cum_pnl": np.cumsum(net_returns).tolist(),
        "trade_log_df": trade_log_df,
        # Arrays for validation (stripped before JSON save)
        "_net_returns": net_returns,
        "_Z_composite": Z_composite,
        "_trade_returns": full_trade_ret,
        "_dates_series": df["date"],
    })

    print(f"    [RESULT] OOS ({metrics['period']}) | Cost Sharpe: {metrics['cost_sharpe']} | PnL: {metrics['total_pnl']} | WinRate: {metrics['win_rate_pct']}% | Intraday Trades: {metrics['n_trades']}/{metrics['n_days']}")

    return metrics



def main():
    parser = argparse.ArgumentParser(description="NewTrade Day-Model Factor Monetization Backtest Runner")
    parser.add_argument("-e", "--etf", type=str, default="all", help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("-s", "--side", type=str, default="single", choices=["single", "long", "short"], help="Trading side")
    parser.add_argument("--scheme", type=str, default="all", choices=["ew", "icw", "score", "rank", "ensemble", "all"], help="Factor weighting scheme (default: all)")
    parser.add_argument("--z-th", type=str, default="auto", help="Conviction threshold Z score. 'auto' = train-sweep + buffer, or float value for fixed.")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Production buffer added to train-optimal threshold (default 0.1, walk-forward validated)")
    parser.add_argument("--z-short-buffer", type=float, default=None, help="Production buffer for short threshold (default: z_buffer + 0.1)")
    parser.add_argument("--position-mode", type=str, default="binary", choices=["binary", "tanh", "quadratic"], help="Position sizing mode")
    parser.add_argument("--fee-bps", type=float, default=None, help="Transaction fee in basis points (default: 8.0 for ETF, 4.0 for futures)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS Start Date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS End Date (YYYY-MM-DD)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output markdown report path (default: newtrade/REPORT.md)")

    
    # Scheme 4 (Rank Bounded Mapping) Options
    parser.add_argument("--rank-min-ratio", type=float, default=0.2, help="Scheme 4 w_min ratio relative to 1/N (default 0.2)")
    parser.add_argument("--rank-max-ratio", type=float, default=1.8, help="Scheme 4 w_max ratio relative to 1/N (default 1.8)")
    parser.add_argument("--rank-mapping", type=str, default="linear", choices=["linear", "power", "softmax", "top_k"], help="Scheme 4 rank mapping shape")
    parser.add_argument("--rank-power", type=float, default=2.0, help="Power exponent for 'power' rank mapping shape")
    parser.add_argument("--top-k", type=int, default=10, help="Top K factors feature truncation selection threshold (default: 10)")
    parser.add_argument("--rank-top-k", type=int, default=None, help="Top K factors truncation threshold for 'top_k' rank mapping shape")
    parser.add_argument("--dynamic-ic", "--dynamic-score", dest="dynamic_ic", action="store_true", default=True, help="Enable zero-lookahead expanding factor ranking (default: True)")
    parser.add_argument("--no-dynamic-ic", "--no-dynamic-score", dest="dynamic_ic", action="store_false", help="Disable dynamic ranking (use static pool metadata score)")
    parser.add_argument("--dynamic-metric", type=str, default="ic", choices=["ic", "multi"], help="Dynamic factor ranking metric: 'ic' (default: single expanding IC) or 'multi'")
    parser.add_argument("--mono-window", type=int, default=750, help="Rolling window for monotonicity calculation (default 750 trading days ~ 3 years, 0 for full expanding)")
    parser.add_argument("--score-w-ic", type=float, default=0.20, help="Score weight for IC component (default 0.20)")
    parser.add_argument("--score-w-ir", type=float, default=0.15, help="Score weight for IC_IR component (default 0.15)")
    parser.add_argument("--score-w-mono", type=float, default=0.65, help="Score weight for Monotonicity component (default 0.65)")
    parser.add_argument("--ic-ema-span", type=int, default=30, help="EMA span parameter for smoothing dynamic expanding metrics (default 30)")
    parser.add_argument("--weight-delta", type=float, default=None, help="Optional partial-adjustment delta parameter for smoothing daily target weight jumps (default: None)")
    parser.add_argument("--long-only", dest="long_only", action="store_true", default=False, help="Restrict to long-only trades (Spot ETF mode). Default: False (allows shorting).")
    parser.add_argument("--allow-short", dest="long_only", action="store_false", help="Allow short trades (default)")
    parser.add_argument("--future", action="store_true", help="Trade underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF) instead of Spot ETF.")

    # Validation options
    parser.add_argument("--validate", dest="validate", action="store_true", default=True, help="Run DSR + CPCV validation on results (default: True)")
    parser.add_argument("--no-validate", dest="validate", action="store_false", help="Disable DSR + CPCV validation")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials for DSR correction (default: 10)")
    parser.add_argument("--cpcv-splits", type=int, default=6, help="CPCV number of splits (default: 6)")
    parser.add_argument("--cpcv-test", type=int, default=2, help="CPCV test chunks per fold (default: 2)")

    args = parser.parse_args()

    # Parse z_th: 'auto' or float
    auto_threshold = args.z_th.lower() == "auto"
    z_th_fixed = 0.5 if auto_threshold else float(args.z_th)

    etfs_to_run = AVAILABLE_ETFS if args.etf.lower() == "all" else [args.etf]
    schemes_to_run = ALL_SCHEMES if args.scheme.lower() == "all" else [args.scheme]
    # Default fee: 8 bps for ETF (conservative slippage), 4 bps for futures (tighter spreads)
    effective_fee_bps = args.fee_bps if args.fee_bps is not None else (4.0 if args.future else 8.0)
    fee_bps = effective_fee_bps / 10000.0

    print("================================================================================")
    print(f"NewTrade Backtest Engine | Mode={'Future' if args.future else 'Spot ETF'} | Scheme={args.scheme.upper()} | z_th={args.z_th} | buffer={args.z_buffer} | LongOnly={args.long_only} | TopK={args.top_k} | OOS=[{args.start_date} ~ {args.end_date}]")
    print("================================================================================")

    rank_kwargs = {
        "w_min_ratio": args.rank_min_ratio,
        "w_max_ratio": args.rank_max_ratio,
        "mapping_shape": args.rank_mapping,
        "power": args.rank_power,
        "top_k": args.top_k if args.top_k is not None else args.rank_top_k,
        "ic_ema_span": args.ic_ema_span,
        "dynamic_metric": args.dynamic_metric,
        "weight_delta": args.weight_delta,
        "score_weights": (args.score_w_ic, args.score_w_ir, args.score_w_mono),
        "mono_window": args.mono_window,
    }

    results = []
    for scheme in schemes_to_run:
        for etf in etfs_to_run:
            res = run_single_backtest(
                etf=etf,
                side=args.side,
                scheme_name=scheme,
                z_th=z_th_fixed,
                position_mode=args.position_mode,
                fee_bps=fee_bps,
                start_date=args.start_date,
                end_date=args.end_date,
                z_buffer=args.z_buffer,
                z_short_buffer=args.z_short_buffer,
                auto_threshold=auto_threshold,
                rank_kwargs=rank_kwargs,
                dynamic_ic=args.dynamic_ic,
                long_only=args.long_only,
                use_future=args.future,
            )
            results.append(res)

    # ─── Validation: DSR + CPCV ───
    if args.validate:
        from scipy.stats import skew, kurtosis
        from math import sqrt
        print("\n" + "=" * 70)
        print(f"VALIDATION (DSR trials={args.trials}, CPCV splits={args.cpcv_splits}/test={args.cpcv_test})")
        print("=" * 70)
        for r in results:
            if r.get("status") != "SUCCESS":
                continue
            net_ret = r.get("_net_returns")
            Z_comp = r.get("_Z_composite")
            trade_ret = r.get("_trade_returns")
            dates_s = r.get("_dates_series")
            if net_ret is None or Z_comp is None:
                continue
            
            # DSR
            std_n = np.std(net_ret)
            obs_sr = float((np.mean(net_ret) / std_n) * sqrt(252)) if std_n > 1e-12 else 0.0
            sk = float(skew(net_ret))
            kt = float(kurtosis(net_ret))
            dsr = deflated_sharpe_ratio(obs_sr, n_trials=args.trials, n_obs=len(net_ret),
                                         skewness=sk, kurtosis_excess=kt)
            r["dsr"] = dsr
            
            # CPCV
            cpcv = run_cpcv_backtest(Z_comp, trade_ret, dates_s,
                                      n_splits=args.cpcv_splits, n_test=args.cpcv_test,
                                      purge_gap=5, mode=r.get("position_mode", "binary"),
                                      fee_bps=effective_fee_bps / 10000.0,
                                      z_buffer=r.get("z_buffer", 0.1),
                                      long_only=r.get("long_only", False))
            r["cpcv"] = cpcv
            
            print(f"  {r['etf']} ({r['scheme']}): SR={obs_sr:.3f}, "
                  f"DSR={dsr['dsr']:.3f} ({dsr['verdict']}), "
                  f"CPCV median={cpcv['sharpe_median']:.3f}\u00b1{cpcv['sharpe_std']:.3f} "
                  f"({cpcv['pct_positive']:.0f}% pos)")
        print()

    # Save aggregated trades CSV artifact
    plot_results = [r for r in results if r.get("status") == "SUCCESS"]
    if plot_results:
        all_dfs = [r["trade_log_df"] for r in plot_results if r.get("trade_log_df") is not None]
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            fut_suffix = "_future" if args.future else ""
            combined_csv = artifacts_dir / f"trade_log{fut_suffix}.csv"
            combined_df.to_csv(combined_csv, index=False)
            print(f"Saved primary trade log CSV to {combined_csv}")

    # Generate equity curve plot artifact
    chart_rel_path = None
    if plot_results:
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
            for r in plot_results:
                if r.get("dates") and r.get("cum_pnl"):
                    dates = pd.to_datetime(r["dates"])
                    cum_pnl = r["cum_pnl"]
                    scheme_lbl = r.get('scheme', '').upper()
                    is_ew = (r.get('scheme') == 'ew')
                    ax.plot(dates, cum_pnl, label=f"{r['etf']} [{scheme_lbl}] ({r.get('asset_type', 'Spot ETF')}) (Sharpe: {r['cost_sharpe']:.3f}, PnL: {r['total_pnl']:+.4f})", linewidth=1.0 if is_ew else 1.8, alpha=0.35 if is_ew else 1.0, linestyle='--' if is_ew else '-')
            
            mode_title = "Index Future" if args.future else "Spot ETF"
            scheme_title = args.scheme.upper()
            ax.set_title(f"NewTrade {scheme_title} — {mode_title} OOS Net PnL (10:00 - 14:35 Intraday)", fontsize=11, fontweight='bold')
            ax.set_xlabel("Date", fontsize=9)
            ax.set_ylabel("Cumulative Net PnL", fontsize=9)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(loc="upper left", frameon=True, fontsize=9)
            fig.tight_layout()

            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            fut_suffix = "_future" if args.future else ""
            chart_path = artifacts_dir / f"equity_curve{fut_suffix}.png"
            fig.savefig(chart_path)
            plt.close(fig)
            chart_rel_path = f"artifacts/equity_curve{fut_suffix}.png"
            print(f"Saved equity curve chart to {chart_path}")
        except Exception as e:
            print(f"[WARNING] Failed to generate plot: {e}")

    # Print summary table
    print("\n================================================================================")
    print(f"NEWTRADE OOS BACKTEST PERFORMANCE SUMMARY ({'INDEX FUTURE' if args.future else 'SPOT ETF'}) (10:00 - 14:35 Intraday Trades)")
    print("================================================================================")
    
    headers = ["ETF", "Asset", "Side", "OOS Period", "Z_th", "Features", "Trades", "Cost Sharpe", "Raw Sharpe", "Total PnL", "Max DD", "Win Rate", "Turnover"]
    
    SCHEME_TITLES = {
        "ensemble": "Ensemble (Equal-Weight Average)",
        "rank": f"Rank Bounded Weight ({args.rank_mapping.capitalize()})",
        "ew": "Equal Weight (EW)",
        "icw": "IC Weight (ICW)",
        "score": "Score Weighted",
        "glm": "Linear GLM",
    }
    
    def _format_row(r):
        if r["status"] == "SUCCESS":
            z_l = r.get("z_th_long", r["z_th"])
            z_s = r.get("z_th_short", r["z_th"])
            tr_l = r.get("z_th_train_long")
            tr_s = r.get("z_th_train_short")
            
            if r.get("long_only", False):
                z_th_str = f"L:{z_l:.2f}"
                if tr_l is not None:
                    z_th_str += f" (train:{tr_l:.2f})"
            else:
                z_th_str = f"L:{z_l:.2f}/S:{z_s:.2f}"
                if tr_l is not None and tr_s is not None:
                    z_th_str += f" (train L:{tr_l:.2f}/S:{tr_s:.2f})"
                elif tr_l is not None:
                    z_th_str += f" (train L:{tr_l:.2f})"
            
            n_l = r.get("n_long_trades", 0)
            n_s = r.get("n_short_trades", 0)
            trades_str = f"{r.get('n_trades', 0)} ({n_l}L/{n_s}S)"

            win_l = f"{r['win_rate_long_pct']:.1f}%" if r.get("win_rate_long_pct") is not None else "N/A"
            win_s = f"{r['win_rate_short_pct']:.1f}%" if r.get("win_rate_short_pct") is not None else "N/A"
            win_str = f"{r['win_rate_pct']:.1f}% (L:{win_l}, S:{win_s})"

            return [
                r["etf"],
                r.get("asset_type", "Spot ETF"),
                r["side"],
                r["period"],
                z_th_str,
                str(r["n_features"]),
                trades_str,
                f"{r['cost_sharpe']:.3f}",
                f"{r['raw_sharpe']:.3f}",
                f"{r['total_pnl']:+.4f}",
                f"{r['max_drawdown']:.4f}",
                win_str,
                f"{r['ann_turnover']:.1f}x",
            ]
        else:
            return [
                r["etf"],
                r.get("asset_type", "N/A"),
                r["side"],
                r.get("period", "N/A"),
                "N/A",
                str(r["n_features"]),
                "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
            ]

    
    def _render_table(rows):
        lines = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)
    
    # Group results by scheme (icw first, other schemes next, ew last)
    from collections import OrderedDict
    scheme_groups = OrderedDict()
    if "icw" in [r.get("scheme") for r in results]:
        scheme_groups["icw"] = [r for r in results if r.get("scheme") == "icw"]
    for r in results:
        s = r.get("scheme", "?")
        if s not in ("icw", "ew"):
            scheme_groups.setdefault(s, []).append(r)
    if "ew" in [r.get("scheme") for r in results]:
        scheme_groups["ew"] = [r for r in results if r.get("scheme") == "ew"]
    
    # Build report sections
    report_sections = []
    chart_img_included = False
    for scheme_key, scheme_results in scheme_groups.items():
        rows = [_format_row(r) for r in scheme_results]
        title = SCHEME_TITLES.get(scheme_key, scheme_key.upper())
        table_md = _render_table(rows)
        
        if scheme_key == "ew":
            # Collapsed details block ONLY for Equal Weight (EW)
            prefix = ""
            if chart_rel_path and not chart_img_included:
                prefix = f"![Cumulative Equity]({chart_rel_path})\n\n"
                chart_img_included = True
            section = f"{prefix}<details>\n<summary><b>{title}</b> (click to expand)</summary>\n\n{table_md}\n\n</details>"
        else:
            # Uncollapsed main section for IC Weight (ICW) and other schemes
            img_md = ""
            if chart_rel_path and not chart_img_included:
                img_md = f"![Cumulative Equity]({chart_rel_path})\n\n"
                chart_img_included = True
            section = f"## {title}\n\n{img_md}{table_md}"
        report_sections.append(section)
    
    report_content = "\n\n".join(report_sections)
    print("\n" + report_content + "\n")

    # Clean results before saving JSON (drop large arrays & DataFrames to keep JSON clean)
    clean_results = []
    for r in results:
        r_copy = dict(r)
        r_copy.pop("dates", None)
        r_copy.pop("cum_pnl", None)
        r_copy.pop("trade_log_df", None)
        r_copy.pop("_net_returns", None)
        r_copy.pop("_Z_composite", None)
        r_copy.pop("_trade_returns", None)
        r_copy.pop("_dates_series", None)
        clean_results.append(r_copy)

    # Save markdown report (default: REPORT.md or REPORT_future.md in newtrade/)
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = HERE / ("REPORT_future.md" if args.future else "REPORT.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# NewTrade OOS Backtest Report\n\n")
        f.write(f"- **OOS Evaluation Period**: `{args.start_date} ~ {args.end_date}`\n")
        f.write(f"- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`\n")
        f.write(f"- **Scheme(s)**: `{args.scheme.upper()}`\n")
        f.write(f"- **Conviction Threshold**: `{args.z_th}` (buffer=+{args.z_buffer})\n")
        f.write(f"- **Position Mode**: `{args.position_mode}`\n")
        f.write(f"- **Transaction Friction**: `{effective_fee_bps} bps`\n")
        f.write(f"- **Rank Mapping Options**: `mapping={args.rank_mapping}, min_ratio={args.rank_min_ratio}, max_ratio={args.rank_max_ratio}, power={args.rank_power}`\n\n")
        f.write(report_content + "\n")
        
        # Append validation section if available
        if args.validate:
            val_rows = [r for r in results if r.get("status") == "SUCCESS" and "dsr" in r]
            if val_rows:
                f.write("\n---\n\n## Validation (DSR + CPCV)\n\n")
                f.write(f"- **DSR Trials**: `{args.trials}`\n")
                f.write(f"- **CPCV**: `{args.cpcv_splits}` splits, `{args.cpcv_test}` test chunks, purge=5\n\n")
                f.write("| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |\n")
                f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
                for r in val_rows:
                    d = r["dsr"]
                    c = r["cpcv"]
                    f.write(f"| {r['etf']} | {r['scheme']} | {r['cost_sharpe']:.3f} | "
                            f"{d['dsr']:.3f} | {d['verdict']} | {c['sharpe_median']:.3f} | "
                            f"{c['sharpe_std']:.3f} | {c['pct_positive']:.0f}% |\n")
                f.write("\n")
    print(f"Saved backtest report to {out_path}")

    # Save JSON result artifact in newtrade/data/
    data_dir = HERE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    scheme_label = args.scheme if args.scheme != "all" else "all_schemes"
    json_path = data_dir / f"backtest_results_{scheme_label}_{args.side}.json"
    with open(json_path, "w") as f:
        json.dump(clean_results, f, indent=2)
    print(f"Saved JSON results to {json_path}")


if __name__ == "__main__":
    main()

