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
from option_strategy import simulate_option_portfolio
from research_stoploss import load_intraday_bars_dict, simulate_full_series

AVAILABLE_ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
ALL_SCHEMES = ["icw", "ew"]  # leave only icw and ew for --scheme all
ENSEMBLE_SCHEMES = ["icw", "ew"]  # schemes averaged in ensemble


def run_single_backtest(etf: str, side: str = "single", scheme_name: str = "ew", z_th: float = 0.5, 
                        position_mode: str = "binary", fee_bps: float = 0.0008, min_features: int = 10,
                        start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                        z_buffer: float = 0.1, z_short_buffer: float = None, auto_threshold: bool = False,
                        rank_kwargs: dict = None, dynamic_ic: bool = False, long_only: bool = False,
                        use_future: bool = False, use_option: bool = False, use_stoploss: bool = True,
                        stoploss_mode: str = "time_decay_trailing", stoploss_param: float = 0.03,
                        pool_override: list = None) -> dict:
    """
    Run backtest for one ETF and side combination filtered to OOS date range.
    
    If auto_threshold=True, sweeps Z_th on training data and applies production buffer.
    If use_future=True, trades underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF).
    If pool_override is provided, uses that pool instead of admitted_pools.py.
    """
    # 1. Load admitted pool
    pool = pool_override if pool_override else load_admitted_pool(etf, side=side, min_features=min_features)
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
    option_result = None
    if use_option:
        # Option portfolio simulation mode
        iv_series = df_oos["iv"].values if "iv" in df_oos.columns else None
        option_result = simulate_option_portfolio(
            etf=etf,
            positions_oos=positions_oos,
            dates_oos=df_oos["date"],
            iv_series=iv_series,
            initial_capital=100_000.0,
            trade_budget=10_000.0,
            commission_per_side=4.0,
            min_days_to_maturity=7,
        )
        # Use option daily returns for metrics
        net_returns = option_result["daily_returns"]
        raw_returns = option_result["daily_gross_returns"]
        fees = (option_result["daily_gross_pnl"] - option_result["daily_pnl"]) / option_result["initial_capital"]
    elif use_stoploss:
        bars_dict = load_intraday_bars_dict(etf)
        if bars_dict:
            net_returns, raw_returns, stop_hits, trig_pct = simulate_full_series(
                df_oos["date"], positions_oos, bars_dict, method=stoploss_mode, param=stoploss_param, fee_bps=fee_bps
            )
            fees = np.where(stop_hits, fee_bps + 0.0002, np.where(np.abs(positions_oos) > 1e-5, fee_bps, 0.0))
        else:
            print(f"    [WARNING] Could not load 1m bars for {etf}. Falling back to baseline simulation.")
            net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)
    else:
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
    
    # Add option-specific metrics if in option mode
    if use_option and option_result is not None:
        metrics["option_final_capital"] = option_result["final_capital"]
        metrics["option_n_trades"] = option_result["n_trades"]
        metrics["option_bankrupt_day"] = option_result["bankrupt_day"]
        metrics["option_initial_capital"] = option_result["initial_capital"]
        metrics["option_trade_log_df"] = option_result["trade_log_df"]
        # Total P&L in RMB for option mode
        metrics["option_total_pnl_rmb"] = round(float(option_result["daily_pnl"].sum()), 2)
    
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
    parser.add_argument("--option", action="store_true", help="Simulate option portfolio (100k RMB, 10k per trade, nearest OTM, 7-day min DTM)")

    # Stop-Loss options
    parser.add_argument("--stoploss", dest="stoploss", action="store_true", default=True, help="Enable 3% time decay trailing stop-loss (default: True).")
    parser.add_argument("--no-stoploss", dest="stoploss", action="store_false", help="Disable stop-loss (hold position to 14:35 PM close).")
    parser.add_argument("--stoploss-mode", type=str, default="time_decay_trailing", help="Stop-loss mode (default: time_decay_trailing).")
    parser.add_argument("--stoploss-param", type=float, default=0.03, help="Stop-loss threshold parameter (default: 0.03 = 3.0%).")

    # Validation options
    parser.add_argument("--validate", dest="validate", action="store_true", default=True, help="Run DSR + CPCV validation on results (default: True)")
    parser.add_argument("--no-validate", dest="validate", action="store_false", help="Disable DSR + CPCV validation")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials for DSR correction (default: 10)")
    parser.add_argument("--cpcv-splits", type=int, default=6, help="CPCV number of splits (default: 6)")
    parser.add_argument("--cpcv-test", type=int, default=2, help="CPCV test chunks per fold (default: 2)")

    # Per-year pool evaluation
    parser.add_argument("--year", type=int, default=None, help="Run single-year backtest (e.g. --year 2024). Auto-sets start/end dates and output to REPORT_{year}.md")
    parser.add_argument("--pool-period", type=str, default=None, help="Use period-specific pool (e.g. '_p2016_2024', 'original' for baseline, 'old' for old vintage)")
    parser.add_argument("--decay", action="store_true", help="Decay analysis: run pool on each year from --year through 2025, generate multi-year chart")

    args = parser.parse_args()

    # Parse z_th: 'auto' or float
    auto_threshold = args.z_th.lower() == "auto"
    z_th_fixed = 0.5 if auto_threshold else float(args.z_th)

    etfs_to_run = AVAILABLE_ETFS if args.etf.lower() == "all" else [args.etf]
    schemes_to_run = ALL_SCHEMES if args.scheme.lower() == "all" else [args.scheme]
    # Default fee: 8 bps for ETF (conservative slippage), 4 bps for futures (tighter spreads)
    effective_fee_bps = args.fee_bps if args.fee_bps is not None else (4.0 if args.future else 8.0)
    fee_bps = effective_fee_bps / 10000.0

    # --year: override start/end dates and output path
    if args.year:
        args.start_date = f"{args.year}-01-01"
        args.end_date = f"{args.year + 1}-01-01"
        if not args.output:
            args.output = str(HERE / f"REPORT_{args.year}.md")
    elif args.pool_period and args.start_date == "2022-01-01":
        import re
        match = re.search(r'_p\d{4}_(\d{4})', args.pool_period)
        if match:
            pool_end_yr = match.group(1)
            args.start_date = f"{pool_end_yr}-01-01"
            if not args.output:
                args.output = str(HERE / f"REPORT_{args.pool_period.lstrip('_')}.md")
            print(f"  [AUTO OOS] Inferred OOS start_date={args.start_date} from pool_period '{args.pool_period}' (running till {args.end_date})")

    # --pool-period: load period-specific pool override
    pool_period_override = None
    if args.pool_period:
        import json as _json
        dm_data = REPO_ROOT / "day-model-new" / "data"
        if args.pool_period == "old":
            # Load old vintage from backup
            import importlib.util
            spec = importlib.util.spec_from_file_location("_old", HERE / "data" / "old_admitted_pools_backup.py")
            _mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_mod)
            pool_period_override = _mod.POOLS  # dict: etf -> {side -> [pool]}
        elif args.pool_period == "original":
            pool_period_override = "__original__"  # sentinel: load per-ETF from selected_pool_{etf}_single.json
        else:
            pool_period_override = args.pool_period  # suffix string like "_p2016_2024"

    print("================================================================================")
    mode_str = "Option Portfolio" if args.option else ("Future" if args.future else "Spot ETF")
    stoploss_info = f" | StopLoss={args.stoploss} ({args.stoploss_mode}={args.stoploss_param})" if not args.option else ""
    print(f"NewTrade Backtest Engine | Mode={mode_str} | Scheme={args.scheme.upper()} | z_th={args.z_th} | buffer={args.z_buffer}{stoploss_info} | LongOnly={args.long_only} | TopK={args.top_k} | OOS=[{args.start_date} ~ {args.end_date}]")
    if args.option:
        print(f"  Option Params: 100k RMB capital, 10k/trade, 4 RMB/side commission, >=7 DTM")
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

    # ─── Decay Mode: run pool across all future years ───
    if args.decay:
        if not args.pool_period:
            print("ERROR: --decay requires --pool-period")
            return
        start_year = args.year if args.year else 2022
        years = list(range(start_year, 2026))
        print(f"\n  DECAY ANALYSIS: pool='{args.pool_period}' across {years}")
        print(f"  {'Year':<6} | {'Sharpe':>8} {'PnL':>10} {'WR%':>6} {'Trades':>7}")
        print(f"  {'-'*6}-+-{'-'*34}")

        decay_results = []
        for yr in years:
            # Override dates for this year
            _start = f"{yr}-01-01"
            _end = f"{yr+1}-01-01"
            yr_results = []
            for etf in etfs_to_run:
                _pool_ov = None
                if isinstance(pool_period_override, dict):
                    _pool_ov = pool_period_override.get(etf, {}).get(args.side, [])
                elif pool_period_override == "__original__":
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)
                else:
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}{pool_period_override}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)

                res = run_single_backtest(
                    etf=etf, side=args.side, scheme_name="icw", z_th=0.5,
                    position_mode="binary", fee_bps=fee_bps,
                    start_date=_start, end_date=_end,
                    z_buffer=args.z_buffer, auto_threshold=True,
                    rank_kwargs=rank_kwargs, dynamic_ic=True,
                    long_only=args.long_only, use_stoploss=False,
                    pool_override=_pool_ov,
                )
                yr_results.append(res)
            decay_results.append((yr, yr_results))

        # Print decay table per ETF
        for etf in etfs_to_run:
            print(f"\n  {etf} decay (pool={args.pool_period}):")
            print(f"    {'Year':<6} | {'Sharpe':>8} {'PnL':>10} {'WR%':>6} {'Trades':>7}")
            print(f"    {'-'*6}-+-{'-'*34}")
            for yr, yr_results in decay_results:
                r = next((x for x in yr_results if x.get("etf") == etf), None)
                if r and r.get("status") == "SUCCESS":
                    print(f"    {yr:<6} | {r['cost_sharpe']:>8.3f} {r['total_pnl']:>+10.4f} {r['win_rate_pct']:>6.1f} {r['n_trades']:>7}")
                else:
                    print(f"    {yr:<6} | {'SKIP':>8}")

        # Generate decay chart
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            n_etfs = len([e for e in etfs_to_run if any(r.get('etf') == e and r.get('status') == 'SUCCESS' for _, yrs in decay_results for r in yrs)])
            if n_etfs > 0:
                fig, axes = plt.subplots(n_etfs, 1, figsize=(11, 3.5 * n_etfs), dpi=150, squeeze=False)
                plot_idx = 0
                for etf in etfs_to_run:
                    has_data = any(r.get('etf') == etf and r.get('status') == 'SUCCESS' for _, yrs in decay_results for r in yrs)
                    if not has_data:
                        continue
                    ax = axes[plot_idx, 0]
                    for yr, yr_results in decay_results:
                        r = next((x for x in yr_results if x.get('etf') == etf and x.get('status') == 'SUCCESS'), None)
                        if r and r.get('dates') and r.get('cum_pnl'):
                            ax.plot(r['dates'], r['cum_pnl'], label=f"{yr} (SR={r['cost_sharpe']:.2f})", linewidth=1.3)
                    ax.set_title(f"{etf} — Pool Decay ({args.pool_period})", fontsize=10, fontweight='bold')
                    ax.set_ylabel("Cum PnL")
                    ax.legend(fontsize=8, loc='upper left')
                    ax.grid(True, alpha=0.3)
                    plot_idx += 1
                fig.tight_layout()
                artifacts_dir = HERE / "artifacts"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                chart_path = artifacts_dir / f"decay{args.pool_period}.png"
                fig.savefig(chart_path)
                plt.close(fig)
                print(f"\n  Saved decay chart: {chart_path}")
        except Exception as e:
            print(f"  [WARNING] Decay chart failed: {e}")
        return

    results = []
    for scheme in schemes_to_run:
        for etf in etfs_to_run:
            # Resolve pool override for this ETF
            _pool_ov = None
            if pool_period_override is not None:
                if isinstance(pool_period_override, dict):
                    # 'old' mode: dict of pools
                    _pool_ov = pool_period_override.get(etf, {}).get(args.side, [])
                elif pool_period_override == "__original__":
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)
                else:
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}{pool_period_override}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)
                if _pool_ov is not None:
                    print(f"  [POOL] {etf}: using period pool '{args.pool_period}' ({len(_pool_ov)} features)")

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
                use_option=args.option,
                use_stoploss=args.stoploss,
                stoploss_mode=args.stoploss_mode,
                stoploss_param=args.stoploss_param,
                pool_override=_pool_ov,
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
            opt_suffix = "_option" if args.option else ""
            combined_csv = artifacts_dir / f"trade_log{fut_suffix}{opt_suffix}.csv"
            combined_df.to_csv(combined_csv, index=False)
            print(f"Saved primary trade log CSV to {combined_csv}")
        
        # Save option trade log CSV if in option mode
        if args.option:
            opt_dfs = [r["option_trade_log_df"] for r in plot_results if r.get("option_trade_log_df") is not None and not r["option_trade_log_df"].empty]
            if opt_dfs:
                combined_opt_df = pd.concat(opt_dfs, ignore_index=True)
                artifacts_dir = HERE / "artifacts"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                opt_csv = artifacts_dir / "option_trades.csv"
                combined_opt_df.to_csv(opt_csv, index=False)
                print(f"Saved option trade log CSV to {opt_csv}")

    # Resolve target markdown output path
    if args.output:
        out_path = Path(args.output)
    else:
        if args.option:
            out_path = HERE / "REPORT_option.md"
        elif args.future:
            out_path = HERE / "REPORT_future.md"
        else:
            out_path = HERE / "REPORT.md"

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
            
            mode_title = "Option Portfolio" if args.option else ("Index Future" if args.future else "Spot ETF")
            scheme_title = args.scheme.upper()
            ax.set_title(f"NewTrade {scheme_title} — {mode_title} OOS Net PnL (10:00 - 14:35 Intraday)", fontsize=11, fontweight='bold')
            ax.set_xlabel("Date", fontsize=9)
            ax.set_ylabel("Cumulative Net PnL", fontsize=9)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(loc="upper left", frameon=True, fontsize=9)
            fig.tight_layout()

            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            # Derive chart filename stem directly from out_path.stem
            stem = out_path.stem
            if stem.upper() == "REPORT":
                chart_stem = "equity_curve"
            elif stem.upper().startswith("REPORT_"):
                chart_stem = "equity_curve_" + stem[7:]
            elif "REPORT" in stem.upper():
                chart_stem = stem.replace("REPORT", "equity_curve").replace("report", "equity_curve")
            else:
                chart_stem = f"equity_curve_{stem}"

            chart_path = artifacts_dir / f"{chart_stem}.png"
            fig.savefig(chart_path)
            plt.close(fig)
            chart_rel_path = f"artifacts/{chart_stem}.png"
            print(f"Saved equity curve chart to {chart_path}")
        except Exception as e:
            print(f"[WARNING] Failed to generate plot: {e}")

    # Print summary table
    print("\n================================================================================")
    summary_mode = "OPTION PORTFOLIO" if args.option else ("INDEX FUTURE" if args.future else "SPOT ETF")
    print(f"NEWTRADE OOS BACKTEST PERFORMANCE SUMMARY ({summary_mode}) (10:00 - 14:35 Intraday Trades)")
    print("================================================================================")
    
    headers = ["ETF", "Asset", "Side", "OOS Period", "Z_th", "Features", "Trades", "Cost Sharpe", "Raw Sharpe", "Total PnL", "Long PnL", "Long Sharpe", "Short PnL", "Short Sharpe", "Max DD", "Win Rate", "Turnover"]
    
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
            
            # Option mode: show option-specific trade count
            if r.get("option_n_trades") is not None:
                trades_str = f"{r['option_n_trades']} opt"

            win_l = f"{r['win_rate_long_pct']:.1f}%" if r.get("win_rate_long_pct") is not None else "N/A"
            win_s = f"{r['win_rate_short_pct']:.1f}%" if r.get("win_rate_short_pct") is not None else "N/A"
            win_str = f"{r['win_rate_pct']:.1f}% (L:{win_l}, S:{win_s})"
            
            # Total PnL display: RMB for option mode, percentage for spot/future
            if r.get("option_total_pnl_rmb") is not None:
                total_pnl_str = f"{r['option_total_pnl_rmb']:+,.0f} RMB"
            else:
                total_pnl_str = f"{r['total_pnl']:+.4f}"

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
                total_pnl_str,
                f"{r.get('long_pnl', 0):+.4f}",
                f"{r.get('long_sharpe', 0):.3f}",
                f"{r.get('short_pnl', 0):+.4f}",
                f"{r.get('short_sharpe', 0):.3f}",
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
                "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
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
        r_copy.pop("option_trade_log_df", None)
        clean_results.append(r_copy)

    # Save markdown report
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# NewTrade OOS Backtest Report\n\n")
        f.write(f"- **OOS Evaluation Period**: `{args.start_date} ~ {args.end_date}`\n")
        f.write(f"- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`\n")
        f.write(f"- **Scheme(s)**: `{args.scheme.upper()}`\n")
        f.write(f"- **Conviction Threshold**: `{args.z_th}` (buffer=+{args.z_buffer})\n")
        f.write(f"- **Position Mode**: `{args.position_mode}`\n")
        if args.option:
            f.write(f"- **Mode**: `Option Portfolio`\n")
            f.write(f"- **Initial Capital**: `100,000 RMB per ETF`\n")
            f.write(f"- **Trade Budget**: `10% of portfolio capital per signal`\n")
            f.write(f"- **Commission**: `4 RMB per side (8 RMB round-trip)`\n")
            f.write(f"- **Option Selection**: `Nearest OTM, >=7 DTM`\n\n")
        else:
            if args.stoploss:
                f.write(f"- **Stop-Loss Execution**: `Enabled ({args.stoploss_mode}={args.stoploss_param})`\n")
                f.write(f"- **Transaction Friction**: `{effective_fee_bps} bps (+ 2.0 bps stop-loss execution slippage)`\n\n")
            else:
                f.write(f"- **Stop-Loss Execution**: `Disabled (Hold to 14:35 Close)`\n")
                f.write(f"- **Transaction Friction**: `{effective_fee_bps} bps`\n\n")
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

